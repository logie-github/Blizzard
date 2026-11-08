// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Forge of Souls' Sylvanas, on Wrath Remix (STORY.md, Chapter VII): the Banshee Queen of this
 * year, who knows nothing of the one from the future at the Bazaar. Her briefing is the game's own
 * (forge_of_souls.cpp's npc_fos_leader, its lines and timings); at the end of it she says the name
 * of the one who asked her to begin, senses something she has not felt since she was alive, and
 * goes off to the other side of the hall. Spoken to there, she is murmuring about her sisters. None
 * of it is needed: the dungeon and its quests go on as they always do.
 *
 * Only on Wrath Remix's world database is her creature template given this script
 * (wrath_remix_world_0020_frozen_halls.sql); ChromieCraft keeps the game's. An Alliance group's is
 * Jaina, the same creature made Jaina by the instance as it's created: she keeps the game's script.
 */

#include "WrathRemix.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "CreatureAIImpl.h"
#include "GossipDef.h"
#include "InstanceScript.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "ScriptedGossip.h"

using namespace WrathRemix;

namespace
{
    constexpr uint32 GOSSIP_SYLVANAS_INTRO = 10971;  // "What would you have of me, Banshee Queen?"
    constexpr uint32 TEXT_FOS_LEADER = 15207;
    // What she murmurs, once she has gone off on her own (npc_text, one at random).
    constexpr uint32 TEXT_MURMURS[] = { 7703101, 7703102, 7703103 };
    // The far side of the hall from where she gives her briefing.
    constexpr float AWAY_X = 4918.0f, AWAY_Y = 2232.0f, AWAY_Z = 638.8f, AWAY_O = 1.25f;
    constexpr uint32 POINT_AWAY = 1;

    enum Events : uint32
    {
        EVENT_INTRO_1 = 1, EVENT_INTRO_2, EVENT_INTRO_3, EVENT_INTRO_4, EVENT_INTRO_5, EVENT_INTRO_6,
        EVENT_OBSERVED, EVENT_GO,
    };
}

class npc_remix_fos_sylvanas : public CreatureScript
{
public:
    npc_remix_fos_sylvanas() : CreatureScript("npc_remix_fos_sylvanas") { }

    struct npc_remix_fos_sylvanasAI : public ScriptedAI
    {
        npc_remix_fos_sylvanasAI(Creature* creature) : ScriptedAI(creature) { }

        EventMap events;
        ObjectGuid asked;   // who asked her to begin
        bool away = false;  // gone off on her own

        void Reset() override
        {
            events.Reset();
        }

        void Begin(Player* player)
        {
            if (!me->HasNpcFlag(UNIT_NPC_FLAG_GOSSIP))
                return;
            me->RemoveNpcFlag(UNIT_NPC_FLAG_GOSSIP);
            asked = player->GetGUID();
            events.Reset();
            events.ScheduleEvent(EVENT_INTRO_1, 1s);
        }

        bool Away() const { return away; }

        void MovementInform(uint32 type, uint32 id) override
        {
            if (type != POINT_MOTION_TYPE || id != POINT_AWAY)
                return;
            away = true;
            me->SetFacingTo(AWAY_O);
            me->SetNpcFlag(UNIT_NPC_FLAG_GOSSIP);
        }

        void UpdateAI(uint32 diff) override
        {
            events.Update(diff);
            switch (events.ExecuteEvent())
            {
                // The game's briefing, line for line and at its pace.
                case EVENT_INTRO_1: Talk(0); events.ScheduleEvent(EVENT_INTRO_2, 11s + 500ms); break;
                case EVENT_INTRO_2: Talk(1); events.ScheduleEvent(EVENT_INTRO_3, 10s + 500ms); break;
                case EVENT_INTRO_3: Talk(2); events.ScheduleEvent(EVENT_INTRO_4, 10s + 500ms); break;
                case EVENT_INTRO_4: Talk(3); events.ScheduleEvent(EVENT_INTRO_5, 11s); break;
                case EVENT_INTRO_5: Talk(4); events.ScheduleEvent(EVENT_INTRO_6, 9500ms); break;
                case EVENT_INTRO_6: Talk(5); events.ScheduleEvent(EVENT_OBSERVED, 6s); break;
                case EVENT_OBSERVED:
                {
                    Player* player = ObjectAccessor::GetPlayer(*me, asked);
                    std::string name = player ? player->GetName() : std::string("Champion");
                    if (player)
                        me->SetFacingToObject(player);
                    me->Say(name + ", I believe we are being watched. Or rather... observed. I sense something. A presence I have not felt since...", LANG_UNIVERSAL);
                    events.ScheduleEvent(EVENT_GO, 5s);
                    break;
                }
                case EVENT_GO:
                    me->SetWalk(false);
                    me->GetMotionMaster()->MovePoint(POINT_AWAY, AWAY_X, AWAY_Y, AWAY_Z);
                    break;
                default:
                    break;
            }

            if (!UpdateVictim())
                return;
            DoMeleeAttackIfReady();
        }
    };

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (creature->IsQuestGiver())
            player->PrepareQuestMenu(creature->GetGUID());
        auto* ai = dynamic_cast<npc_remix_fos_sylvanasAI*>(creature->AI());
        if (ai && ai->Away())
        {
            SendGossipMenuFor(player, TEXT_MURMURS[urand(0, std::size(TEXT_MURMURS) - 1)], creature->GetGUID());
            return true;
        }
        if (creature->HasNpcFlag(UNIT_NPC_FLAG_GOSSIP))
            AddGossipItemFor(player, GOSSIP_SYLVANAS_INTRO, 0, GOSSIP_SENDER_MAIN, GOSSIP_ACTION_INFO_DEF + 1);
        SendGossipMenuFor(player, TEXT_FOS_LEADER, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 action) override
    {
        ClearGossipMenuFor(player);
        CloseGossipMenuFor(player);
        if (action == GOSSIP_ACTION_INFO_DEF + 1)
            if (auto* ai = dynamic_cast<npc_remix_fos_sylvanasAI*>(creature->AI()))
                ai->Begin(player);
        return true;
    }

    CreatureAI* GetAI(Creature* creature) const override
    {
        // An Alliance group's Sylvanas becomes Jaina just after her AI is chosen (the instance's
        // OnCreatureCreate, which keeps the AI), and Jaina's gossip is the game's, asking the AI
        // for her briefing: so she has the game's AI too, chosen by the instance's side, known
        // from the moment it's made.
        if (InstanceScript* instance = creature->GetInstanceScript())
            if (instance->GetTeamIdInInstance() == TEAM_ALLIANCE)
                if (CreatureScript* game = ScriptRegistry<CreatureScript>::GetScriptById(sObjectMgr->GetScriptId("npc_fos_leader")))
                    return game->GetAI(creature);
        return GetInstanceAI<npc_remix_fos_sylvanasAI>(creature, "instance_forge_of_souls");
    }
};

void AddRemixFrozenHallsScripts()
{
    new npc_remix_fos_sylvanas();
}
