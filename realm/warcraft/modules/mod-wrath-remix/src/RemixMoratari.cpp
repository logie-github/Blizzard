// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix: Moratari at the Timerunner's side (STORY.md, "Moratari in the war").
 *
 * - Her words on the game's own quests (remix_quest_whisper): as one is taken, as its objectives
 *   are done and as it's turned in, a line or a few, said beside the Timerunner when she walks with
 *   them, whispered when she doesn't.
 * - The companion (remix_companion): where the story wants her (the whole Borean Tundra, some of
 *   the war's quests), she walks with the Timerunner, fights beside them and heals them. She is
 *   Moratari herself (entry 770001, the same quests and words), summoned for them alone; where her
 *   own spawn stands near, she steps away to it, so there is never two of her.
 * - Talk (remix_talk): things the Timerunner can say, to her or to the war's own people (warning
 *   General Arlos of what is coming): a menu entry on the creature, a reply, a credit for a quest.
 * - Places (remix_place): somewhere a quest sends the Timerunner to see for themselves (the
 *   sinkholes before they open): a credit as they come within its radius, and her words there.
 *
 * The data is wrath_remix_world_0027_moratari.sql (written by tools/story.py).
 */

#include "WrathRemix.h"
#include "Battlefield.h"
#include "BattlefieldMgr.h"
#include "Chat.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "DatabaseEnv.h"
#include "GameTime.h"
#include "GossipDef.h"
#include "Log.h"
#include "Map.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "ScriptedGossip.h"
#include "Spell.h"
#include "SpellInfo.h"
#include "TemporarySummon.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <cmath>
#include <list>
#include <unordered_map>
#include <vector>

using namespace WrathRemix;

namespace
{
    enum MoratariCompanion : uint32
    {
        SPELL_ARCANE_BOLT     = 15124,  // her bolt, at the Timerunner's foe (its damage set by her level)
        SPELL_FLASH_HEAL      = 2061,   // on the Timerunner, when they're hurt
        SPELL_TELEPORT_VISUAL = 51347,  // as she steps out of the hour, and back into it

        SENDER_TALK = 7700,             // remix_talk's entries in a gossip menu (the action is the entry's id)
        TALK_BACK   = 0,                // "Back.": the creature's own menu again
    };

    enum TalkAction : uint8
    {
        TALK_NONE           = 0,
        TALK_SCENE          = 1,  // plays scene [param] (remix_scene)
        TALK_CLOSE          = 2,  // the menu closes after it (no reply)
        TALK_COMPANION_STAY = 3,  // "Wait for me here": she goes back to her posts (QUEST_FLAG_ALONE)
        TALK_COMPANION_COME = 4,  // "Come with me."
        TALK_OUTING         = 5,  // she takes them on outing [param] (remix_outing: RemixOutings.cpp)
        TALK_TIME_JUMPER    = 6,  // "I'm a time jumper": her story without the war's checkpoints (QUEST_ROMANCE_TIME_JUMPER),
                                  // said only to her as she sits with them at the Bazaar's campfire (RemixCampfire.cpp)
    };

    enum Moment : uint8
    {
        MOMENT_TAKEN = 1,
        MOMENT_DONE  = 2,
        MOMENT_TURNED_IN = 3,
    };

    struct Whisper
    {
        uint8 side;
        uint32 speaker, delay, after, before, races;
        std::string text;
    };

    struct CompanionRule
    {
        uint8 side;
        uint32 zone, from, until, during;
    };

    struct Place
    {
        uint32 quest, map, credit, scene;
        float x, y, radius;
        std::string text;
    };

    struct TalkEntry
    {
        uint32 id, npc, parent;
        uint8 side, gender, icon, action;
        uint32 races, quest, after, before, reply, credit, param;
        std::string option;
    };

    std::unordered_map<uint64, std::vector<Whisper>> whispers;   // by quest << 8 | moment, in order
    std::vector<CompanionRule> companionRules;
    std::vector<Place> places;
    std::unordered_map<uint32, TalkEntry> talk;
    std::unordered_map<uint32, std::vector<uint32>> talkRoots;    // by creature entry
    std::unordered_map<uint32, std::vector<uint32>> talkChildren; // by parent entry
    std::unordered_map<uint32, uint32> talkCredits;               // a credit: whom it is said to

    // Set while the companion is being summoned: Moratari's script gives her the companion's mind,
    // and the level hook the Timerunner's level (the core picks both inside SummonCreature, on this
    // thread).
    thread_local bool summoningCompanion = false;
    thread_local uint8 companionLevel = 0;

    char const* const RACES[] = { "", "Human", "Orc", "Dwarf", "Night Elf", "Forsaken", "Tauren", "Gnome", "Troll", "Goblin", "Blood Elf", "Draenei" };
    char const* const CLASSES[] = { "", "Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Death Knight", "Shaman", "Mage", "Warlock", "", "Druid" };

    std::string Lower(std::string s)
    {
        for (char& c : s)
            c = char(std::tolower(static_cast<unsigned char>(c)));
        return s;
    }

    bool Rewarded(Player* player, uint32 quest)
    {
        return quest && player->GetQuestRewardStatus(quest);
    }

    bool OnSide(Player* player, uint8 side)
    {
        return !side || (side == 1) == IsAlliance(player);
    }

    bool OfRace(Player* player, uint32 races)
    {
        return !races || (races & (1u << (player->getRace() - 1)));
    }

    // The companion's state, kept on the Timerunner.
    struct Companion : public DataMap::Base
    {
        ObjectGuid guid;        // her, while she walks with them
        ObjectGuid post;        // her own spawn she stepped away to (they came near it)
        uint32 tick = 0;
        uint64 quietAt = 0;     // (game time, ms) when her last line queued will have been said
    };

    Companion* StateOf(Player* player)
    {
        return player->CustomData.GetDefault<Companion>("remix_companion");
    }

    Creature* CompanionOf(Player* player)
    {
        Companion* c = StateOf(player);
        if (!c->guid)
            return nullptr;
        Creature* creature = ObjectAccessor::GetCreature(*player, c->guid);
        if (!creature || !creature->IsInWorld())
            return nullptr;
        return creature;
    }
}

namespace WrathRemix
{
    // $N the name, $R the race, $C the class ($r, $c in lower case), $Gmale:female; by sex, $B a
    // new line: what the client does for a quest's text, done here for words said in chat.
    std::string Words(Player* player, std::string text)
    {
        auto replace = [&text](std::string const& token, std::string const& with)
        {
            for (size_t at = 0; (at = text.find(token, at)) != std::string::npos; at += with.size())
                text.replace(at, token.size(), with);
        };
        uint8 race = player->getRace(), cls = player->getClass();
        std::string raceName = race < std::size(RACES) ? RACES[race] : "", className = cls < std::size(CLASSES) ? CLASSES[cls] : "";
        // ($G first: its words may hold the others)
        for (size_t at; (at = text.find("$G")) != std::string::npos;)
        {
            size_t colon = text.find(':', at), end = text.find(';', at);
            if (colon == std::string::npos || end == std::string::npos || colon > end)
                break;
            std::string male = text.substr(at + 2, colon - at - 2), female = text.substr(colon + 1, end - colon - 1);
            text.replace(at, end - at + 1, player->getGender() == GENDER_FEMALE ? female : male);
        }
        replace("$N", player->GetName());
        replace("$n", player->GetName());
        replace("$R", raceName);
        replace("$r", Lower(raceName));
        replace("$C", className);
        replace("$c", Lower(className));
        replace("$B", " ");
        return text;
    }

    // Words from one of the story's people to this Timerunner alone. Moratari's are said beside
    // them when she walks with them (a bubble over her head), whispered when she doesn't.
    void MoratariSays(Player* player, uint32 speaker, std::string const& text)
    {
        std::string words = Words(player, text);
        WorldPacket data;
        if (speaker == NPC_MORATARI)
            if (Creature* her = CompanionOf(player); her && her->IsWithinDist(player, 40.0f))
            {
                ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_SAY, LANG_UNIVERSAL, her, player, words);
                player->SendDirectMessage(&data);
                if (uint32 sound = MoratariVoiceFor(text))
                    her->PlayDirectSound(sound, player);
                return;
            }
        CreatureTemplate const* who = sObjectMgr->GetCreatureTemplate(speaker);
        std::string name = who ? who->Name : std::string("Moratari");
        ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_WHISPER, LANG_UNIVERSAL, ObjectGuid::Empty, player->GetGUID(), words, 0, name, player->GetName());
        player->SendDirectMessage(&data);
        // (her own voice where the words are hers in the game, remix_voice)
        if (speaker == NPC_MORATARI)
            if (uint32 sound = MoratariVoiceFor(text))
                player->PlayDirectSound(sound, player);
    }

    void LoadMoratari()
    {
        whispers.clear();
        companionRules.clear();
        places.clear();
        talk.clear();
        talkRoots.clear();
        talkChildren.clear();
        talkCredits.clear();
        if (!Active())
            return;
        if (QueryResult result = WorldDatabase.Query("SELECT `quest`, `moment`, `side`, `speaker`, `delay_ms`, `after_quest`, `before_quest`, `races`, `text` "
                                                     "FROM `remix_quest_whisper` ORDER BY `quest`, `moment`, `seq`"))
        {
            do
            {
                Field* f = result->Fetch();
                Whisper w{ f[2].Get<uint8>(), f[3].Get<uint32>(), f[4].Get<uint32>(), f[5].Get<uint32>(), f[6].Get<uint32>(), f[7].Get<uint32>(), f[8].Get<std::string>() };
                whispers[(uint64(f[0].Get<uint32>()) << 8) | f[1].Get<uint8>()].push_back(std::move(w));
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `side`, `zone`, `from_quest`, `until_quest`, `during_quest` FROM `remix_companion`"))
        {
            do
            {
                Field* f = result->Fetch();
                companionRules.push_back({ f[0].Get<uint8>(), f[1].Get<uint32>(), f[2].Get<uint32>(), f[3].Get<uint32>(), f[4].Get<uint32>() });
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `quest`, `map`, `x`, `y`, `radius`, `credit`, `scene`, `text` FROM `remix_place`"))
        {
            do
            {
                Field* f = result->Fetch();
                places.push_back({ f[0].Get<uint32>(), f[1].Get<uint32>(), f[5].Get<uint32>(), f[6].Get<uint32>(), f[2].Get<float>(), f[3].Get<float>(),
                    f[4].Get<float>(), f[7].Get<std::string>() });
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `id`, `npc`, `parent`, `side`, `gender`, `icon`, `action`, `races`, `quest`, `after_quest`, `before_quest`, "
                                                     "`reply`, `credit`, `param`, `option_text` FROM `remix_talk` ORDER BY `npc`, `parent`, `ord`, `id`"))
        {
            do
            {
                Field* f = result->Fetch();
                TalkEntry t{ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<uint32>(), f[3].Get<uint8>(), f[4].Get<uint8>(), f[5].Get<uint8>(), f[6].Get<uint8>(),
                    f[7].Get<uint32>(), f[8].Get<uint32>(), f[9].Get<uint32>(), f[10].Get<uint32>(), f[11].Get<uint32>(), f[12].Get<uint32>(), f[13].Get<uint32>(),
                    f[14].Get<std::string>() };
                if (t.parent)
                    talkChildren[t.parent].push_back(t.id);
                else
                    talkRoots[t.npc].push_back(t.id);
                if (t.credit)
                    talkCredits.emplace(t.credit, t.npc);
                talk[t.id] = std::move(t);
            } while (result->NextRow());
        }
        LOG_INFO("module", "Wrath Remix: {} quests with Moratari's words, {} companion rules, {} things to say, {} places", whispers.size(), companionRules.size(),
            talk.size(), places.size());
    }

    // The quest's words for this moment, one after another.
    void MoratariOnQuest(Player* player, uint32 quest, uint8 moment)
    {
        if (!Active() || IsBot(player))
            return;
        auto it = whispers.find((uint64(quest) << 8) | moment);
        if (it == whispers.end())
            return;
        ObjectGuid guid = player->GetGUID();
        // (one line after another: a quest done as it's taken has both moments' words at once)
        Companion* state = StateOf(player);
        uint64 now = uint64(GameTime::GetGameTimeMS().count());
        uint32 at = state->quietAt > now ? uint32(state->quietAt - now) : 0;
        for (Whisper const& w : it->second)
        {
            if (!OnSide(player, w.side) || !OfRace(player, w.races) || (w.after && !Rewarded(player, w.after)) || Rewarded(player, w.before))
                continue;
            at += w.delay;
            state->quietAt = now + at + 1500;
            uint32 speaker = w.speaker;
            std::string text = w.text;
            player->m_Events.AddEventAtOffset([guid, speaker, text]()
            {
                if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
                    MoratariSays(p, speaker, text);
            }, Milliseconds(at));
        }
    }

    uint32 TalkCreditNpc(uint32 credit)
    {
        auto it = talkCredits.find(credit);
        return it == talkCredits.end() ? 0 : it->second;
    }

    bool PlaceOf(uint32 quest, uint32 credit, uint32& map, float& x, float& y)
    {
        for (Place const& p : places)
            if (p.quest == quest && p.credit == credit)
            {
                map = p.map;
                x = p.x;
                y = p.y;
                return true;
            }
        return false;
    }

    bool IsCompanionSummon() { return summoningCompanion; }
    uint8 CompanionLevel() { return companionLevel; }
}

namespace
{
    // Where the story has her walk with the Timerunner.
    bool CompanionRuleApplies(Player* player)
    {
        uint32 zone = player->GetZoneId();
        for (CompanionRule const& r : companionRules)
        {
            if (!OnSide(player, r.side) || (r.zone && r.zone != zone))
                continue;
            if (r.from && !Rewarded(player, r.from))
                continue;
            if (Rewarded(player, r.until))
                continue;
            if (r.during)
            {
                QuestStatus status = player->GetQuestStatus(r.during);
                if (status != QUEST_STATUS_INCOMPLETE && status != QUEST_STATUS_COMPLETE)
                    continue;
            }
            return true;
        }
        return false;
    }

    // ...and now: they haven't asked her to wait, and nothing in the way (a flight, an outing).
    bool CompanionWanted(Player* player)
    {
        if (!Active() || IsBot(player) || !player->IsAlive() || player->IsInFlight() || player->GetTransport() || InIntro(player))
            return false;
        // (on an outing, she is in its scene; on a flying mount or a vehicle, she waits until they're
        // down: summoned beside them she'd be in the air, and left behind every few seconds)
        if (Rewarded(player, QUEST_FLAG_ALONE) || OnOuting(player) || player->CanFly() || player->IsFlying() || player->GetVehicle())
            return false;
        // (a dungeon, a raid, a battleground, Wintergrasp while it's fought: none of hers)
        if (player->GetMap()->Instanceable())
            return false;
        if (Battlefield* battle = sBattlefieldMgr->GetBattlefieldToZoneId(player->GetZoneId()); battle && battle->IsWarTime())
            return false;
        return CompanionRuleApplies(player);
    }

    // Her own spawn near the Timerunner, if they can see it (there, she is at her post), or another
    // of her near them (a scene's, the last hour's).
    Creature* PostNear(Player* player, float range)
    {
        std::list<Creature*> near;
        player->GetCreatureListWithEntryInGrid(near, { NPC_MORATARI, NPC_MORATARI_SCENE, NPC_ALLY_MORATARI, NPC_MORATARI_DRESS,
            NPC_MORATARI_TENT, NPC_MORATARI_DRAGON }, range);
        Creature* best = nullptr;
        for (Creature* c : near)
        {
            if (c->GetEntry() == NPC_MORATARI && !c->GetSpawnId())
                continue;  // (herself, or another's)
            if (c->IsAlive() && player->CanSeeOrDetect(c) && (!best || player->GetDistance(c) < player->GetDistance(best)))
                best = c;
        }
        return best;
    }

    // A place a quest in the log sends them to: its credit as they come within its radius (or its
    // scene, whose end gives the credit: one left before its end plays again as they come back).
    void PlacesTick(Player* player)
    {
        for (Place const& p : places)
        {
            if (p.map != player->GetMapId() || player->GetQuestStatus(p.quest) != QUEST_STATUS_INCOMPLETE)
                continue;
            if (player->GetExactDist2d(p.x, p.y) > p.radius)
                continue;
            Quest const* q = sObjectMgr->GetQuestTemplate(p.quest);
            auto status = player->getQuestStatusMap().find(p.quest);
            if (!q || status == player->getQuestStatusMap().end())
                continue;
            bool had = true;
            for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
                if (q->RequiredNpcOrGo[i] == int32(p.credit) && status->second.CreatureOrGOCount[i] < q->RequiredNpcOrGoCount[i])
                    had = false;
            if (had)
                continue;
            if (p.scene)
            {
                if (!SceneRunning(player) && PlayScene(player, p.scene) && !p.text.empty())
                    MoratariSays(player, NPC_MORATARI, p.text);
                continue;
            }
            player->KilledMonsterCredit(p.credit);
            if (!p.text.empty())
                MoratariSays(player, NPC_MORATARI, p.text);
        }
    }

    void Dismiss(Player* player, Companion* state, bool visual)
    {
        if (Creature* her = CompanionOf(player))
        {
            if (visual)
            {
                her->CastSpell(her, SPELL_TELEPORT_VISUAL, true);
                her->DespawnOrUnsummon(1s);
            }
            else
                her->DespawnOrUnsummon();
        }
        state->guid.Clear();
    }

    void Summon(Player* player, Companion* state)
    {
        float x, y, z;
        player->GetClosePoint(x, y, z, player->GetCombatReach(), 2.5f, float(M_PI) * 0.75f);
        summoningCompanion = true;
        companionLevel = player->GetLevel();
        TempSummon* her = player->SummonCreature(NPC_MORATARI, x, y, z, player->GetOrientation(), TEMPSUMMON_MANUAL_DESPAWN, 0, nullptr, true);
        summoningCompanion = false;
        companionLevel = 0;
        if (!her)
            return;
        state->guid = her->GetGUID();
        her->CastSpell(her, SPELL_TELEPORT_VISUAL, true);
    }

    // A second a time: she walks with the Timerunner where she's wanted, steps away to her post when
    // they come near it, and catches them up when they leave it, change maps or get too far ahead.
    void CompanionTick(Player* player)
    {
        Companion* state = StateOf(player);
        if (!CompanionWanted(player))
        {
            Dismiss(player, state, false);
            state->post.Clear();
            return;
        }
        if (Creature* post = state->post ? ObjectAccessor::GetCreature(*player, state->post) : nullptr; post && player->IsWithinDist(post, 45.0f))
            return;
        state->post.Clear();
        if (Creature* post = PostNear(player, 30.0f))
        {
            state->post = post->GetGUID();
            Dismiss(player, state, true);
            return;
        }
        Creature* her = CompanionOf(player);
        if (her && (her->GetMapId() != player->GetMapId() || !her->IsWithinDist(player, 80.0f)))
        {
            Dismiss(player, state, false);
            her = nullptr;
        }
        if (!her)
            Summon(player, state);
        else if (her->GetPhaseMask() != player->GetPhaseMask())
            her->SetPhaseMask(player->GetPhaseMask(), true);  // (into the Kvaldir's mist with them, and out of it)
    }

    // Moratari as the companion: she follows, fights what fights the Timerunner (never first),
    // heals them when they're hurt, and can't be killed (she steps out of the hour instead).
    struct CompanionAI : public ScriptedAI
    {
        CompanionAI(Creature* creature) : ScriptedAI(creature) { }

        ObjectGuid owner;
        uint32 boltTimer = 1500, healTimer = 3000, stepTimer = 0;
        time_t lastWord = 0;               // (her word after a fight, now and then)

        Player* Owner() const { return owner ? ObjectAccessor::GetPlayer(*me, owner) : nullptr; }

        void IsSummonedBy(WorldObject* summoner) override
        {
            Player* player = summoner ? summoner->ToPlayer() : nullptr;
            if (!player)
                return;
            owner = player->GetGUID();
            me->SetFaction(player->GetFaction());
            // (her template keeps her posts out of fights: Eternus's loyalists stand by some of them)
            me->SetImmuneToNPC(false);
            me->SetReactState(REACT_DEFENSIVE);
            Follow(player);
        }

        void Follow(Player* player)
        {
            if (me->GetMotionMaster()->GetCurrentMovementGeneratorType() != FOLLOW_MOTION_TYPE)
                me->GetMotionMaster()->MoveFollow(player, 2.5f, float(M_PI) * 0.75f);
        }

        void EnterEvadeMode(EvadeReason why) override
        {
            if (!_EnterEvadeMode(why))
                return;
            if (Player* player = Owner())
            {
                me->GetMotionMaster()->Clear();
                Follow(player);
                // Now and then, a fight over: her own voice (not more than every ten minutes)
                time_t now = GameTime::GetGameTime().count();
                if (player->IsAlive() && now - lastWord >= 600 && roll_chance_i(25))
                {
                    lastWord = now;
                    MoratariVoice(player, "after_fight", -1, me);
                }
            }
        }

        void AttackStart(Unit* who) override
        {
            AttackStartCaster(who, 18.0f);
        }

        void DamageTaken(Unit* /*attacker*/, uint32& damage, DamageEffectType /*type*/, SpellSchoolMask /*school*/) override
        {
            if (damage >= me->GetHealth())
                damage = me->GetHealth() - 1;
            // (the hour bends around her: she is somewhere else for a breath, and whole again)
            if (!stepTimer && me->HealthBelowPctDamaged(15, damage))
            {
                damage = 0;
                me->SetFullHealth();
                me->CastSpell(me, SPELL_TELEPORT_VISUAL, true);
                stepTimer = 30000;
            }
        }

        // What the Timerunner is fighting, or what is fighting them: never one they've put out of the
        // fight for a while (a sheep, a sap, a fear, roots), which her bolt would wake.
        Unit* TheirFoe(Player* player) const
        {
            if (!player->IsInCombat())
                return nullptr;
            auto fair = [this, player](Unit* foe)
            {
                return foe && me->IsValidAttackTarget(foe) && foe->IsWithinDist(player, 40.0f) && !foe->HasBreakableByDamageCrowdControlAura();
            };
            if (Unit* victim = player->GetVictim(); fair(victim))
                return victim;
            for (Unit* attacker : player->getAttackers())
                if (fair(attacker))
                    return attacker;
            return nullptr;
        }

        void UpdateAI(uint32 diff) override
        {
            Player* player = Owner();
            if (!player || !player->IsInWorld() || player->GetMapId() != me->GetMapId())
            {
                me->DespawnOrUnsummon();
                return;
            }
            stepTimer = stepTimer > diff ? stepTimer - diff : 0;
            if (!me->GetVictim() || !me->IsInCombat())
            {
                if (Unit* foe = TheirFoe(player))
                    AttackStart(foe);
                else
                {
                    Follow(player);
                    return;
                }
            }
            if (!UpdateVictim())
                return;
            if (healTimer <= diff)
            {
                healTimer = 1000;
                if (player->IsAlive() && player->GetHealthPct() < 55.0f && !me->HasUnitState(UNIT_STATE_CASTING) && me->IsWithinDist(player, 30.0f))
                {
                    int32 heal = int32(player->GetMaxHealth() / 4);
                    me->CastCustomSpell(player, SPELL_FLASH_HEAL, &heal, nullptr, nullptr, false);
                    healTimer = 9000;
                }
            }
            else
                healTimer -= diff;
            // (her foe put out of the fight since: a bolt on its way to it stops, and the next goes to
            // another of theirs, or nowhere while it lasts)
            if (Spell* bolt = me->GetCurrentSpell(CURRENT_GENERIC_SPELL); bolt && bolt->GetSpellInfo()->Id == SPELL_ARCANE_BOLT)
                if (Unit* target = bolt->m_targets.GetUnitTarget(); target && target->HasBreakableByDamageCrowdControlAura())
                    me->InterruptSpell(CURRENT_GENERIC_SPELL);
            if (boltTimer <= diff)
            {
                Unit* target = me->GetVictim();
                if (target && target->HasBreakableByDamageCrowdControlAura())
                    target = TheirFoe(player);
                if (target && !me->HasUnitState(UNIT_STATE_CASTING))
                {
                    int32 damage = int32(6 + me->GetLevel() * 3);
                    me->CastCustomSpell(target, SPELL_ARCANE_BOLT, &damage, nullptr, nullptr, false);
                }
                boltTimer = urand(2600, 3600);
            }
            else
                boltTimer -= diff;
        }
    };

    bool TalkAvailable(Player* player, TalkEntry const& t, Creature* creature)
    {
        if (!OnSide(player, t.side) || !OfRace(player, t.races))
            return false;
        if (t.gender && (t.gender == 2) != (player->getGender() == GENDER_FEMALE))
            return false;
        if (t.after && !Rewarded(player, t.after))
            return false;
        if (Rewarded(player, t.before))
            return false;
        if (t.quest)
        {
            if (player->GetQuestStatus(t.quest) != QUEST_STATUS_INCOMPLETE)
                return false;
            // (said once: gone when what it gives is had)
            if (t.credit)
            {
                Quest const* q = sObjectMgr->GetQuestTemplate(t.quest);
                auto status = player->getQuestStatusMap().find(t.quest);
                if (q && status != player->getQuestStatusMap().end())
                    for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
                        if (q->RequiredNpcOrGo[i] == int32(t.credit) && status->second.CreatureOrGOCount[i] >= q->RequiredNpcOrGoCount[i])
                            return false;
            }
        }
        // (asking her to wait, or to come, where the story has her walk with them)
        if ((t.action == TALK_COMPANION_STAY || t.action == TALK_COMPANION_COME) && !CompanionRuleApplies(player))
            return false;
        if (t.action == TALK_COMPANION_STAY && Rewarded(player, QUEST_FLAG_ALONE))
            return false;
        if (t.action == TALK_COMPANION_COME && !Rewarded(player, QUEST_FLAG_ALONE))
            return false;
        if (t.action == TALK_TIME_JUMPER && !(creature && AtTheCampfire(player, creature)))
            return false;
        // (no date from a dungeon, a raid or a battleground: nowhere to come back to)
        if (t.action == TALK_OUTING && player->GetMap()->Instanceable())
            return false;
        return true;
    }

    uint32 TalkKey(Creature* creature)
    {
        return creature->GetEntry();
    }

    bool AddEntries(Player* player, Creature* creature, std::vector<uint32> const& ids)
    {
        bool any = false;
        for (uint32 id : ids)
        {
            auto it = talk.find(id);
            if (it == talk.end() || !TalkAvailable(player, it->second, creature))
                continue;
            AddGossipItemFor(player, it->second.icon, Words(player, it->second.option), SENDER_TALK, id);
            any = true;
        }
        return any;
    }

    // The creature's own menu again, as when it was first spoken to.
    void OwnMenu(Player* player, Creature* creature)
    {
        if (!sScriptMgr->OnGossipHello(player, creature))
        {
            player->PrepareGossipMenu(creature, creature->GetCreatureTemplate()->GossipMenuId, true);
            player->SendPreparedGossip(creature);
        }
    }
}

namespace WrathRemix
{
    CreatureAI* MoratariCompanionAI(Creature* creature)
    {
        return new CompanionAI(creature);
    }

    std::string CompanionReport(Player* player)
    {
        Creature* her = CompanionOf(player);
        if (!her)
            return Acore::StringFormat("Wrath Remix companion: none ({}{}{})", CompanionRuleApplies(player) ? "the story has her here" : "not where the story has her",
                Rewarded(player, QUEST_FLAG_ALONE) ? ", asked to wait" : "", StateOf(player)->post ? ", at her post nearby" : "");
        Unit* victim = her->GetVictim();
        return Acore::StringFormat("Wrath Remix companion: level {}, {:.1f} yards, health {}/{}, faction {}, {}", uint32(her->GetLevel()), her->GetDistance(player),
            her->GetHealth(), her->GetMaxHealth(), her->GetFaction(), victim ? Acore::StringFormat("fighting {} ({})", victim->GetName(), victim->GetEntry()) : std::string("following"));
    }

    // Moratari's own menu calls this: what the Timerunner can say to her now.
    bool AddTalk(Player* player, Creature* creature)
    {
        if (!Active())
            return false;
        auto it = talkRoots.find(TalkKey(creature));
        return it != talkRoots.end() && AddEntries(player, creature, it->second);
    }

    bool HasTalk(Player* player, Creature* creature)
    {
        auto it = talkRoots.find(TalkKey(creature));
        if (it == talkRoots.end())
            return false;
        for (uint32 id : it->second)
            if (auto t = talk.find(id); t != talk.end() && TalkAvailable(player, t->second, creature))
                return true;
        return false;
    }

    // One of remix_talk's entries chosen: its credit, what it does, then its reply (with what can
    // be said next) or the creature's own menu.
    bool TalkSelect(Player* player, Creature* creature, uint32 sender, uint32 action)
    {
        if (!Active() || sender != SENDER_TALK)
            return false;
        ClearGossipMenuFor(player);
        if (action == TALK_BACK)
        {
            OwnMenu(player, creature);
            return true;
        }
        auto it = talk.find(action);
        if (it == talk.end() || !TalkAvailable(player, it->second, creature))
        {
            CloseGossipMenuFor(player);
            return true;
        }
        TalkEntry const& t = it->second;
        if (t.credit)
            player->KilledMonsterCredit(t.credit);
        switch (t.action)
        {
            case TALK_SCENE:
                CloseGossipMenuFor(player);
                PlayScene(player, t.param);
                return true;
            case TALK_OUTING:
                CloseGossipMenuFor(player);
                if (!StartOuting(player, t.param))
                    ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari:|r Not now. Later, when the hour is quieter.");
                return true;
            case TALK_COMPANION_STAY:
                player->SetRewardedQuest(QUEST_FLAG_ALONE);
                break;
            case TALK_COMPANION_COME:
                player->RemoveRewardedQuest(QUEST_FLAG_ALONE);
                break;
            case TALK_TIME_JUMPER:
                player->SetRewardedQuest(QUEST_ROMANCE_TIME_JUMPER);
                break;
            default:
                break;
        }
        if (t.action == TALK_CLOSE || !t.reply)
        {
            CloseGossipMenuFor(player);
            return true;
        }
        auto children = talkChildren.find(t.id);
        if (children != talkChildren.end())
            AddEntries(player, creature, children->second);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Back.", SENDER_TALK, TALK_BACK);
        SendGossipMenuFor(player, t.reply, creature);
        return true;
    }
}

// The war's own people (General Arlos, Overlord Agmar): their menu as the game has it, with what the
// Timerunner can tell them now. Moratari's own script adds hers.
class RemixTalkCreatures : public AllCreatureScript
{
public:
    RemixTalkCreatures() : AllCreatureScript("RemixTalkCreatures") { }

    bool CanCreatureGossipHello(Player* player, Creature* creature) override
    {
        if (!Active() || creature->GetEntry() == NPC_MORATARI || !HasTalk(player, creature))
            return false;
        ClearGossipMenuFor(player);
        player->PrepareGossipMenu(creature, creature->GetCreatureTemplate()->GossipMenuId, true);
        AddTalk(player, creature);
        player->PlayerTalkClass->SendGossipMenu(player->GetGossipTextId(creature), creature->GetGUID());
        return true;
    }

    bool CanCreatureGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        if (creature->GetEntry() == NPC_MORATARI)
            return false;
        return TalkSelect(player, creature, sender, action);
    }
};

class RemixMoratariPlayer : public PlayerScript
{
public:
    RemixMoratariPlayer() : PlayerScript("RemixMoratariPlayer", {
        PLAYERHOOK_ON_UPDATE,
        PLAYERHOOK_ON_LOGOUT,
        PLAYERHOOK_ON_LEVEL_CHANGED,
        PLAYERHOOK_ON_PLAYER_QUEST_ACCEPT,
        PLAYERHOOK_ON_BEFORE_QUEST_COMPLETE,
        PLAYERHOOK_ON_PLAYER_COMPLETE_QUEST,
    }) { }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!Active() || (companionRules.empty() && places.empty()))
            return;
        Companion* state = StateOf(player);
        state->tick += diff;
        if (state->tick < 1000)
            return;
        state->tick = 0;
        if (!player->IsInWorld() || player->IsBeingTeleported() || IsBot(player))
            return;
        CompanionTick(player);
        PlacesTick(player);
    }

    void OnPlayerLogout(Player* player) override
    {
        if (Active())
            Dismiss(player, StateOf(player), false);
    }

    // (she comes back at their new level)
    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        if (Active())
            Dismiss(player, StateOf(player), false);
    }

    void OnPlayerQuestAccept(Player* player, Quest const* quest) override
    {
        MoratariOnQuest(player, quest->GetQuestId(), MOMENT_TAKEN);
    }

    bool OnPlayerBeforeQuestComplete(Player* player, uint32 questId) override
    {
        // (a quest with nothing to do is complete as it's taken: its words wait for the first; and
        // one the game completes again, already complete, isn't talked about twice)
        if (player->GetQuestStatus(questId) != QUEST_STATUS_COMPLETE)
            MoratariOnQuest(player, questId, MOMENT_DONE);
        return true;
    }

    void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
    {
        // (where the story has her begin to walk with them, her tent's "everywhere" too, a wait they
        // asked of her before is over)
        if (Active() && !IsBot(player) && Rewarded(player, QUEST_FLAG_ALONE))
            for (CompanionRule const& r : companionRules)
                if (r.from == quest->GetQuestId() && OnSide(player, r.side))
                {
                    player->RemoveRewardedQuest(QUEST_FLAG_ALONE);
                    break;
                }
        MoratariOnQuest(player, quest->GetQuestId(), MOMENT_TURNED_IN);
    }
};

void AddRemixMoratariScripts()
{
    new RemixTalkCreatures();
    new RemixMoratariPlayer();
}
