// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Infinite Bazaar's life (wrath_remix_world_0023_bazaar.sql): the people of the camp talk while
 * a Timerunner is about, to the air or to each other. Each spawn with lines (remix_bazaar_line) says
 * one now and then, a minute or so apart, with the gesture it goes with (a line beginning %s is an
 * emote: Agos the Silent only nods); a line with a reply has the
 * other one turn to it and answer a few seconds later. Nobody talks to an empty camp, nor in a fight,
 * and only those who can see them hear them (the story hides some from some: Sylvanas before the
 * turn, Eternus after it). What they do between (sitting, kneeling, working, reading, walking their rounds) is the world
 * database's own (creature_addon, waypoints).
 */

#include "WrathRemix.h"
#include "CellImpl.h"
#include "Chat.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "DatabaseEnv.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "QueryResult.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include <unordered_map>

using namespace WrathRemix;

namespace
{
    struct Line
    {
        std::string text;
        uint32 emote;
        ObjectGuid::LowType replyGuid;
        std::string reply;
        uint32 replyEmote;
    };

    std::unordered_map<ObjectGuid::LowType, std::vector<Line>> lines;

    void LoadLines()
    {
        lines.clear();
        if (!Active())
            return;
        if (QueryResult result = WorldDatabase.Query("SELECT `guid`, `text`, `emote`, `reply_guid`, `reply`, `reply_emote` FROM `remix_bazaar_line`"))
        {
            do
            {
                Field* f = result->Fetch();
                lines[f[0].Get<uint32>()].push_back({ f[1].Get<std::string>(), f[2].Get<uint32>(), f[3].Get<uint32>(),
                    f[4].Get<std::string>(), f[5].Get<uint32>() });
            } while (result->NextRow());
        }
        LOG_INFO("module", "Wrath Remix: {} of the Bazaar's people have something to say", lines.size());
    }

    constexpr float EARSHOT = 35.0f;

    // The players near enough to hear [me] who can see them (a real one among them, not only bots).
    std::list<Player*> Listeners(Creature* me, bool& someoneReal)
    {
        std::list<Player*> near, seeing;
        Acore::AnyPlayerInObjectRangeCheck check(me, EARSHOT);
        Acore::PlayerListSearcher<Acore::AnyPlayerInObjectRangeCheck> searcher(me, near, check);
        Cell::VisitObjects(me, searcher, EARSHOT);
        someoneReal = false;
        for (Player* player : near)
            if (player->CanSeeObjectByVisibilityConditions(me))
            {
                seeing.push_back(player);
                if (!IsBot(player))
                    someoneReal = true;
            }
        return seeing;
    }

    // [speaker] says [text] to everyone who can see them; a text that begins with %s is what they
    // do instead (an emote: "%s nods.", the game puts their name there).
    void Speak(Creature* speaker, std::string const& text, uint32 emote)
    {
        ChatMsg type = text.rfind("%s", 0) == 0 ? CHAT_MSG_MONSTER_EMOTE : CHAT_MSG_MONSTER_SAY;
        bool someoneReal;
        for (Player* player : Listeners(speaker, someoneReal))
        {
            WorldPacket data;
            ChatHandler::BuildChatPacket(data, type, LANG_UNIVERSAL, speaker, player, text);
            player->SendDirectMessage(&data);
        }
        if (emote)
            speaker->HandleEmoteCommand(emote);
    }
}

class npc_remix_bazaar_life : public CreatureScript
{
public:
    npc_remix_bazaar_life() : CreatureScript("npc_remix_bazaar_life") { }

    struct npc_remix_bazaar_lifeAI : public ScriptedAI
    {
        npc_remix_bazaar_lifeAI(Creature* creature) : ScriptedAI(creature) { }

        uint32 talkIn = urand(8000, 40000);
        uint32 faceBackIn = 0;

        void Reset() override { }

        void FaceHomeSoon()
        {
            faceBackIn = 9000;
        }

        void UpdateAI(uint32 diff) override
        {
            if (faceBackIn)
            {
                if (faceBackIn <= diff)
                {
                    faceBackIn = 0;
                    if (!me->isMoving() && me->GetMotionMaster()->GetCurrentMovementGeneratorType() != WAYPOINT_MOTION_TYPE)
                        me->SetFacingTo(me->GetHomePosition().GetOrientation());
                }
                else
                    faceBackIn -= diff;
            }

            if (me->IsInCombat())
            {
                if (UpdateVictim())
                    DoMeleeAttackIfReady();
                return;
            }

            if (talkIn > diff)
            {
                talkIn -= diff;
                return;
            }
            talkIn = urand(45000, 95000);
            auto it = lines.find(me->GetSpawnId());
            if (it == lines.end() || it->second.empty())
                return;
            bool someoneReal;
            Listeners(me, someoneReal);
            if (!someoneReal)
                return;
            Line const& line = it->second[urand(0, it->second.size() - 1)];
            Creature* other = nullptr;
            if (line.replyGuid)
            {
                auto const& bySpawn = me->GetMap()->GetCreatureBySpawnIdStore();
                auto found = bySpawn.find(line.replyGuid);
                other = found != bySpawn.end() ? found->second : nullptr;
            }
            if (other && other->IsAlive() && !other->IsInCombat() && me->IsWithinDist(other, 30.0f))
            {
                me->SetFacingToObject(other);
                FaceHomeSoon();
            }
            else
                other = nullptr;
            Speak(me, line.text, line.emote);
            if (!other || line.reply.empty())
                return;
            ObjectGuid speaker = me->GetGUID(), listener = other->GetGUID();
            std::string reply = line.reply;
            uint32 replyEmote = line.replyEmote;
            other->m_Events.AddEventAtOffset([other, speaker, listener, reply, replyEmote]()
            {
                if (!other->IsAlive() || other->IsInCombat())
                    return;
                if (Creature* first = ObjectAccessor::GetCreature(*other, speaker))
                    other->SetFacingToObject(first);
                Speak(other, reply, replyEmote);
                if (auto* ai = dynamic_cast<npc_remix_bazaar_lifeAI*>(other->AI()))
                    ai->FaceHomeSoon();
            }, Milliseconds(urand(3500, 6000)));
        }
    };

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_remix_bazaar_lifeAI(creature);
    }
};

CreatureAI* WrathRemix::BazaarLifeAI(Creature* creature)
{
    return new npc_remix_bazaar_life::npc_remix_bazaar_lifeAI(creature);
}

class RemixBazaarWorld : public WorldScript
{
public:
    RemixBazaarWorld() : WorldScript("RemixBazaarWorld", { WORLDHOOK_ON_STARTUP }) { }

    void OnStartup() override
    {
        LoadLines();
    }
};

void AddRemixBazaarScripts()
{
    new npc_remix_bazaar_life();
    new RemixBazaarWorld();
}
