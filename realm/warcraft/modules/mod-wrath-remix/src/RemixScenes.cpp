// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix's scenes (STORY.md): short plays staged for one Timerunner, as the story's quests
 * are taken or turned in. Each is a list of timed steps in the Remix world database
 * (remix_scene, remix_scene_step, wrath_remix_world_0014_scenes.sql): people summoned where the
 * scene stands (seen by that Timerunner alone), or the people already there; what they say, which
 * only that Timerunner hears; where they walk, what they do, the spells they show; a quest's
 * credit when the scene is over.
 *
 * A scene stands where its anchor is: the nearest creature of the scene's anchor entry (the
 * quest's giver, as a rule), or the Timerunner. Its positions are yards forward and to the left
 * of the anchor, as it faces; people stand on the ground there.
 *
 * Also here: the story's foes, whose deaths count for every Timerunner nearby who needs them,
 * whoever struck the blow (the realm's bots fight beside them, and a kill only counts for the
 * one who tapped it).
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "TemporarySummon.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <cmath>
#include <list>
#include <map>
#include <memory>
#include <mutex>
#include <set>

namespace WrathRemix
{
    namespace
    {
        enum SceneAction : uint8
        {
            ACT_SUMMON = 1,     // the actor [actor]: creature [entry], summoned at the position
            ACT_BIND,           // the actor [actor]: the nearest creature [entry] already there
            ACT_MOVE,           // walks there ([param] 1: runs)
            ACT_SAY,            // says [text]
            ACT_YELL,           // yells [text]
            ACT_EMOTE,          // plays emote [param]
            ACT_CAST,           // casts spell [param] (triggered) at itself, or at actor [entry] (255: the Timerunner)
            ACT_FACE,           // turns to actor [entry] (255: the Timerunner)
            ACT_DESPAWN,        // goes (a summoned actor)
            ACT_CREDIT,         // the Timerunner gets the credit of creature [entry]
            ACT_SOUND,          // the Timerunner hears sound [param]
            ACT_STAND,          // stand state [param] (0 stand, 1 sit, 8 kneel; 255: the Timerunner too)
            ACT_TEXT_EMOTE,     // "[name] [text]", as an emote line
            ACT_TELEPORT,       // the Timerunner goes to map [entry] at x y z o (absolute)
            ACT_MOVIE,          // the Timerunner watches movie [param]
            ACT_CINEMATIC,      // the Timerunner watches cinematic [param]
            ACT_AURA,           // aura [param] on the actor (255: the Timerunner)
            ACT_REMOVE_AURA,    // aura [param] off the actor (255: the Timerunner)
            ACT_WHISPER,        // whispers [text] to the Timerunner
            ACT_FACE_ANGLE,     // turns to the scene's angle [o]
            ACT_HOME,           // the Timerunner goes home (Back to Your Own Time: RemixEnding.cpp)
            ACT_FADE,           // the screen goes dark for [param] ms with [text] on it (the app's add-on; RemixOutings.cpp)
        };

        constexpr uint8 TARGET_PLAYER = 255;

        struct SceneStep
        {
            uint32 at;
            uint8 action, actor;
            uint32 entry, param;
            float x, y, z, o;
            std::string text;
        };

        struct Scene
        {
            uint32 id, quest, anchor, credit;
            uint8 trigger;
            std::vector<SceneStep> steps;
        };

        std::unordered_map<uint32, Scene> scenes;
        std::multimap<std::pair<uint32, uint8>, uint32> scenesByQuest;

        struct SceneRun
        {
            ObjectGuid player;
            uint32 scene;
            uint32 map;
            Position anchor;
            std::map<uint8, ObjectGuid> actors;
            std::set<uint8> summoned;
            bool over = false;  // (ended early: the Timerunner left its place)
        };

        // Timerunners with a scene playing (one at a time), and the scene: its events, on the
        // Timerunner, are its only owners, so it goes with them at a logout (cleared then; one
        // gone without its end is no longer playing either way).
        std::mutex runningLock;
        std::map<ObjectGuid, std::weak_ptr<SceneRun>> running;

        // While a scene's credit is given: the credit, and the scene's quest, the only one in the
        // log that gets it (the scenes share one; RemixScenesPlayer holds the others back). Per
        // thread: each map updates in a thread of its own.
        thread_local uint32 creditGiven = 0, creditQuest = 0;

        // The credit [credit] for the Timerunner's quest [quest] alone (0: every quest that asks).
        void SceneCredit(Player* player, uint32 quest, uint32 credit)
        {
            creditGiven = credit;
            creditQuest = quest;
            player->KilledMonsterCredit(credit);
            creditGiven = creditQuest = 0;
        }

        Position At(SceneRun const& run, Player* player, float forward, float left, float up, float facing)
        {
            float ao = run.anchor.GetOrientation();
            float x = run.anchor.GetPositionX() + forward * std::cos(ao) - left * std::sin(ao);
            float y = run.anchor.GetPositionY() + forward * std::sin(ao) + left * std::cos(ao);
            float z = run.anchor.GetPositionZ() + up;
            // on the ground there, unless it's well above it (a flier, a ledge)
            float ground = player->GetMap()->GetHeight(player->GetPhaseMask(), x, y, z + 4.0f, true, 30.0f);
            if (ground > INVALID_HEIGHT && std::fabs(ground - z) < 8.0f && up < 3.0f)
                z = ground + 0.05f;
            return Position(x, y, z, Position::NormalizeOrientation(ao + facing));
        }

        Creature* ActorOf(Player* player, SceneRun const& run, uint8 actor)
        {
            auto it = run.actors.find(actor);
            return it == run.actors.end() ? nullptr : ObjectAccessor::GetCreature(*player, it->second);
        }

        WorldObject* TargetOf(Player* player, SceneRun const& run, uint32 target)
        {
            if (target == TARGET_PLAYER)
                return player;
            return ActorOf(player, run, uint8(target));
        }

        std::string Personal(Player* player, std::string const& text)
        {
            return Words(player, text);
        }

        // Words only this Timerunner hears (the actors are theirs alone, and so are their lines).
        void Speak(Player* player, WorldObject* speaker, ChatMsg type, std::string const& text)
        {
            WorldPacket data;
            ChatHandler::BuildChatPacket(data, type, LANG_UNIVERSAL, speaker, player, Personal(player, text));
            player->SendDirectMessage(&data);
            // Moratari's lines that are hers in the game's own words: her voice with them (remix_voice)
            if (Creature const* creature = speaker->ToCreature(); creature &&
                (creature->GetEntry() == NPC_MORATARI || creature->GetEntry() == NPC_MORATARI_SCENE))
                if (uint32 sound = MoratariVoiceFor(text))
                    speaker->PlayDirectSound(sound, player);
        }

        void Unsummon(Player* player, SceneRun& run)
        {
            for (uint8 actor : run.summoned)
                if (Creature* creature = ActorOf(player, run, actor))
                    creature->DespawnOrUnsummon();
            run.summoned.clear();
        }

        void EndScene(Player* player, SceneRun& run)
        {
            Unsummon(player, run);
            player->UpdateObjectVisibility();
        }

        // The Timerunner free for another scene (only this one's: a later one is left playing).
        void Release(SceneRun const& run)
        {
            std::lock_guard<std::mutex> lock(runningLock);
            auto it = running.find(run.player);
            if (it != running.end() && it->second.lock().get() == &run)
                running.erase(it);
        }

        // Over early: its people gone, and the Timerunner free for another.
        void Abandon(Player* player, SceneRun& run)
        {
            run.over = true;
            EndScene(player, run);
            Release(run);
        }

        // The nearest creature of [entry] the Timerunner can see: in their phase, shown to them by
        // the story's visibility conditions, and not someone else's (seen by its summoner alone).
        Creature* NearestSeen(Player* player, uint32 entry, float range)
        {
            std::list<Creature*> near;
            player->GetCreatureListWithEntryInGrid(near, entry, range);
            Creature* best = nullptr;
            for (Creature* c : near)
            {
                if (!c->IsAlive() || !player->CanSeeOrDetect(c))
                    continue;
                if (TempSummon const* summon = c->ToTempSummon(); summon && summon->IsVisibleBySummonerOnly() && summon->GetSummonerGUID() != player->GetGUID())
                    continue;
                if (!best || player->GetDistance(c) < player->GetDistance(best))
                    best = c;
            }
            return best;
        }

        void Play(Player* player, SceneRun& run, SceneStep const& step, uint32 duration)
        {
            Creature* actor = ActorOf(player, run, step.actor);
            switch (step.action)
            {
                case ACT_SUMMON:
                {
                    Position at = At(run, player, step.x, step.y, step.z, step.o);
                    if (TempSummon* summon = player->SummonCreature(step.entry, at.GetPositionX(), at.GetPositionY(), at.GetPositionZ(),
                            at.GetOrientation(), TEMPSUMMON_TIMED_DESPAWN, duration + 30000, nullptr, true))
                    {
                        summon->SetReactState(REACT_PASSIVE);
                        run.actors[step.actor] = summon->GetGUID();
                        run.summoned.insert(step.actor);
                    }
                    break;
                }
                case ACT_BIND:
                    if (Creature* found = NearestSeen(player, step.entry, 80.0f))
                        run.actors[step.actor] = found->GetGUID();
                    break;
                case ACT_MOVE:
                    if (actor && run.summoned.count(step.actor))
                    {
                        Position at = At(run, player, step.x, step.y, step.z, step.o);
                        actor->SetWalk(step.param == 0);
                        actor->GetMotionMaster()->MovePoint(1, at);
                    }
                    break;
                case ACT_SAY:
                    if (actor)
                        Speak(player, actor, CHAT_MSG_MONSTER_SAY, step.text);
                    break;
                case ACT_YELL:
                    if (actor)
                        Speak(player, actor, CHAT_MSG_MONSTER_YELL, step.text);
                    break;
                case ACT_WHISPER:
                    if (actor)
                        Speak(player, actor, CHAT_MSG_MONSTER_WHISPER, step.text);
                    break;
                case ACT_TEXT_EMOTE:
                    if (actor)
                        Speak(player, actor, CHAT_MSG_MONSTER_EMOTE, std::string("%s ") + step.text);
                    break;
                case ACT_EMOTE:
                    // (the Timerunner too: a kiss, a dance)
                    if (step.actor == TARGET_PLAYER)
                        player->HandleEmoteCommand(step.param);
                    else if (actor)
                        actor->HandleEmoteCommand(step.param);
                    break;
                case ACT_CAST:
                    if (actor)
                    {
                        WorldObject* target = step.entry ? TargetOf(player, run, step.entry) : actor;
                        if (Unit* unit = target ? target->ToUnit() : nullptr)
                            actor->CastSpell(unit, step.param, true);
                    }
                    break;
                case ACT_FACE:
                    if (actor)
                        if (WorldObject* target = TargetOf(player, run, step.entry))
                            actor->SetFacingToObject(target);
                    break;
                case ACT_FACE_ANGLE:
                    if (actor)
                        actor->SetFacingTo(Position::NormalizeOrientation(run.anchor.GetOrientation() + step.o));
                    break;
                case ACT_DESPAWN:
                    if (actor && run.summoned.count(step.actor))
                    {
                        actor->DespawnOrUnsummon();
                        run.summoned.erase(step.actor);
                        run.actors.erase(step.actor);
                    }
                    break;
                case ACT_CREDIT:
                    player->KilledMonsterCredit(step.entry);
                    break;
                case ACT_SOUND:
                    player->PlayDirectSound(step.param, player);
                    break;
                case ACT_STAND:
                    if (step.actor == TARGET_PLAYER)
                        player->SetStandState(step.param);
                    else if (actor)
                        actor->SetStandState(step.param);
                    break;
                case ACT_TELEPORT:
                    player->TeleportTo(step.entry, step.x, step.y, step.z, step.o);
                    break;
                case ACT_MOVIE:
                    player->SendMovieStart(step.param);
                    break;
                case ACT_CINEMATIC:
                    player->SendCinematicStart(step.param);
                    break;
                case ACT_AURA:
                    if (step.actor == TARGET_PLAYER)
                        player->AddAura(step.param, player);
                    else if (actor)
                        actor->AddAura(step.param, actor);
                    break;
                case ACT_REMOVE_AURA:
                    if (step.actor == TARGET_PLAYER)
                        player->RemoveAurasDueToSpell(step.param);
                    else if (actor)
                        actor->RemoveAurasDueToSpell(step.param);
                    break;
                case ACT_HOME:
                    SendHome(player);
                    break;
                case ACT_FADE:
                    ScreenFade(player, step.param, step.text);
                    break;
                default:
                    break;
            }
        }
    }

    void LoadScenes()
    {
        scenes.clear();
        scenesByQuest.clear();
        if (!Active())
            return;
        if (QueryResult result = WorldDatabase.Query("SELECT `id`, `quest`, `trigger`, `anchor`, `credit` FROM `remix_scene`"))
        {
            do
            {
                Field* f = result->Fetch();
                Scene s;
                s.id = f[0].Get<uint32>();
                s.quest = f[1].Get<uint32>();
                s.trigger = f[2].Get<uint8>();
                s.anchor = f[3].Get<uint32>();
                s.credit = f[4].Get<uint32>();
                scenes[s.id] = s;
                if (s.quest)
                    scenesByQuest.emplace(std::make_pair(s.quest, s.trigger), s.id);
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `scene`, `at`, `action`, `actor`, `entry`, `param`, `x`, `y`, `z`, `o`, `text` "
                                                     "FROM `remix_scene_step` ORDER BY `scene`, `at`, `step`"))
        {
            do
            {
                Field* f = result->Fetch();
                auto it = scenes.find(f[0].Get<uint32>());
                if (it == scenes.end())
                    continue;
                it->second.steps.push_back({ f[1].Get<uint32>(), f[2].Get<uint8>(), f[3].Get<uint8>(), f[4].Get<uint32>(), f[5].Get<uint32>(),
                    f[6].Get<float>(), f[7].Get<float>(), f[8].Get<float>(), f[9].Get<float>(), f[10].Get<std::string>() });
            } while (result->NextRow());
        }
        LOG_INFO("module", "Wrath Remix: {} scenes", scenes.size());
    }

    uint32 SceneDuration(uint32 sceneId)
    {
        auto found = scenes.find(sceneId);
        return found == scenes.end() || found->second.steps.empty() ? 0 : found->second.steps.back().at;
    }

    bool SceneRunning(Player* player)
    {
        std::lock_guard<std::mutex> lock(runningLock);
        auto it = running.find(player->GetGUID());
        return it != running.end() && !it->second.expired();
    }

    bool PlayScene(Player* player, uint32 sceneId)
    {
        auto found = scenes.find(sceneId);
        if (found == scenes.end() || found->second.steps.empty() || !player->IsInWorld())
            return false;
        Scene const& scene = found->second;
        auto run = std::make_shared<SceneRun>();
        run->player = player->GetGUID();
        {
            std::lock_guard<std::mutex> lock(runningLock);
            auto [it, added] = running.emplace(run->player, run);
            if (!added && !it->second.expired())
                return false;
            it->second = run;
        }
        run->scene = scene.id;
        run->map = player->GetMapId();
        Creature* anchor = scene.anchor ? NearestSeen(player, scene.anchor, 80.0f) : nullptr;
        run->anchor = anchor ? anchor->GetPosition() : player->GetPosition();
        uint32 duration = scene.steps.back().at;
        Record(player, "scene", scene.id, 0);

        for (SceneStep const& step : scene.steps)
        {
            player->m_Events.AddEventAtOffset([run, step, duration]()
            {
                Player* p = ObjectAccessor::FindPlayer(run->player);
                if (!p || run->over)
                    return;
                // (a Timerunner who left the scene's place misses the rest of it, and is free for
                // the next one at once)
                if (!p->IsInWorld() || p->GetMapId() != run->map || p->GetExactDist2d(run->anchor) > 120.0f)
                {
                    if (p->IsInWorld() && !p->IsBeingTeleported())
                        Abandon(p, *run);
                    return;
                }
                Play(p, *run, step, duration);
            }, Milliseconds(step.at));
        }
        uint32 credit = scene.credit, quest = scene.quest;
        player->m_Events.AddEventAtOffset([run, credit, quest]()
        {
            if (run->over)
                return;
            if (Player* p = ObjectAccessor::FindPlayer(run->player); p && p->IsInWorld())
            {
                EndScene(p, *run);
                // the credit only for one who stayed to the end, and only for the scene's quest
                if (credit && p->GetMapId() == run->map && p->GetExactDist2d(run->anchor) <= 120.0f)
                    SceneCredit(p, quest, credit);
            }
            Release(*run);
        }, Milliseconds(duration + 1500));
        return true;
    }

    void ScenesForQuest(Player* player, uint32 quest, uint8 trigger)
    {
        if (!Active() || IsBot(player))
            return;
        auto [first, last] = scenesByQuest.equal_range({ quest, trigger });
        for (auto it = first; it != last; ++it)
            if (PlayScene(player, it->second))
                return;
    }

    // A scene its Timerunner missed (they left before its end): played again when they speak with
    // its anchor while the quest still waits for it.
    bool ReplaySceneAt(Player* player, Creature* creature)
    {
        if (!Active() || IsBot(player))
            return false;
        for (auto const& [id, scene] : scenes)
        {
            if (scene.anchor != creature->GetEntry() || !scene.credit || !scene.quest || scene.trigger != SCENE_ON_ACCEPT)
                continue;
            if (player->GetQuestStatus(scene.quest) != QUEST_STATUS_INCOMPLETE)
                continue;
            Quest const* quest = sObjectMgr->GetQuestTemplate(scene.quest);
            if (!quest)
                continue;
            bool needed = false;
            for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
                if (quest->RequiredNpcOrGo[i] == int32(scene.credit) &&
                    player->GetQuestSlotCounter(player->FindQuestSlot(scene.quest), i) < quest->RequiredNpcOrGoCount[i])
                    needed = true;
            if (needed)
                return PlayScene(player, id);
        }
        return false;
    }
}

using namespace WrathRemix;

// The story's foes (Eternus's agents and loyalists): a death counts for every Timerunner within 60
// yards whose quest wants it.
class npc_remix_story_foe : public CreatureScript
{
public:
    npc_remix_story_foe() : CreatureScript("npc_remix_story_foe") { }

    struct npc_remix_story_foeAI : public ScriptedAI
    {
        npc_remix_story_foeAI(Creature* creature) : ScriptedAI(creature) { }

        uint32 castTimer = 4000;

        void Reset() override
        {
            castTimer = urand(3000, 6000);
        }

        // One of its spells (creature_template_spell) every few seconds, at whoever it fights.
        void UpdateAI(uint32 diff) override
        {
            if (!UpdateVictim())
                return;
            if (castTimer <= diff)
            {
                std::vector<uint32> spells;
                for (uint32 spell : me->m_spells)
                    if (spell)
                        spells.push_back(spell);
                if (!spells.empty() && !me->HasUnitState(UNIT_STATE_CASTING))
                    DoCastVictim(spells[urand(0, uint32(spells.size()) - 1)]);
                castTimer = urand(5000, 9000);
            }
            else
                castTimer -= diff;
            DoMeleeAttackIfReady();
        }

        void JustDied(Unit* /*killer*/) override
        {
            if (!Active())
                return;
            std::list<Player*> players;
            me->GetMap()->DoForAllPlayers([&](Player* player)
            {
                if (player->IsInWorld() && player->GetDistance(me) <= 60.0f && !IsBot(player))
                    players.push_back(player);
            });
            // (the one who tapped it, and their group, have had it from the core already)
            for (Player* player : players)
                if (!me->isTappedBy(player))
                    player->KilledMonsterCredit(me->GetEntry());
        }
    };

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_remix_story_foeAI(creature);
    }
};

// A scene cut short by a logout: its events go with the Timerunner unplayed, so the scene's people
// go now (for one lost between maps, on their own a little later), and the Timerunner is free for
// the next one (the one they missed plays again at its anchor, as they speak to them). And a
// scene's credit goes to its own quest alone.
class RemixScenesPlayer : public PlayerScript
{
public:
    RemixScenesPlayer() : PlayerScript("RemixScenesPlayer", { PLAYERHOOK_ON_LOGOUT, PLAYERHOOK_PASSED_QUEST_KILLED_MONSTER_CREDIT }) { }

    void OnPlayerLogout(Player* player) override
    {
        if (!Active())
            return;
        std::shared_ptr<SceneRun> run;
        {
            std::lock_guard<std::mutex> lock(runningLock);
            auto it = running.find(player->GetGUID());
            if (it == running.end())
                return;
            run = it->second.lock();
            running.erase(it);
        }
        if (run)
        {
            run->over = true;
            if (player->IsInWorld())
                Unsummon(player, *run);
        }
    }

    bool OnPlayerPassedQuestKilledMonsterCredit(Player* /*player*/, Quest const* quest, uint32 entry, uint32 /*realEntry*/, ObjectGuid /*guid*/) override
    {
        return !creditQuest || entry != creditGiven || quest->GetQuestId() == creditQuest;
    }
};

void AddRemixSceneScripts()
{
    new npc_remix_story_foe();
    new RemixScenesPlayer();
}
