// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Malykriss's magic (wrath_remix_world_0030_malykriss.sql, tools/malykriss.py): what moves and casts in
 * the Bazaar's home besides talk. The nerubians' skyguards circle the necropolis outside its ribs; two
 * frost spheres circle the hourglass; the sandshapers channel bronze into the hourglass's heart and the
 * time rift above it pours gold into it, again as each channel ends; the hourglass's sands pulse gold
 * now and then; the Ebon Blade's duelists spar. All of it only while a Timerunner is near enough to see.
 */

#include "WrathRemix.h"
#include "Creature.h"
#include "MotionMaster.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "SpellInfo.h"

using namespace WrathRemix;

namespace
{
    enum Entries : uint32
    {
        NPC_DUELIST         = 770403,
        NPC_SKYGUARD        = 770416,
        NPC_HOURGLASS_SANDS = 770420,
        NPC_SANDSHAPER      = 770421,
        NPC_HOURGLASS_HEART = 770422,
        NPC_FROST_SPHERE    = 770423,
        NPC_HOURGLASS_RIFT  = 770424,
    };

    enum Spells : uint32
    {
        SPELL_BRONZE_BEAM   = 56906,    // Scion of Storm Beam: the Wyrmrest wardens' bronze, not broken by moving
        SPELL_GOLD_BEAM     = 31387,    // Time Rift Channel: the Black Morass rifts' gold
        SPELL_GOLD_PULSE    = 57771,    // a gold ring (a dummy: nothing but its look and sound)
        SPELL_HOURGLASS_SAND = 23645,   // a gold flash (a dummy)
    };

    // tools/malykriss.py's
    constexpr float HOURGLASS_X = 6394.0f, HOURGLASS_Y = 1898.0f;
    constexpr float NECROPOLIS_X = 6377.0f, NECROPOLIS_Y = 1805.0f;
    constexpr float WATCHED = 90.0f;    // how near a player has to be for any of it to happen
}

class npc_remix_malykriss : public CreatureScript
{
public:
    npc_remix_malykriss() : CreatureScript("npc_remix_malykriss") { }

    struct npc_remix_malykrissAI : public ScriptedAI
    {
        npc_remix_malykrissAI(Creature* creature) : ScriptedAI(creature) { }

        uint32 timer = urand(2000, 6000);
        uint32 pulseIn = urand(15000, 25000);
        uint32 sandIn = urand(30000, 50000);
        bool flying = false;

        void InitializeAI() override
        {
            ScriptedAI::InitializeAI();
            switch (me->GetEntry())
            {
                case NPC_SKYGUARD:
                case NPC_FROST_SPHERE:
                case NPC_HOURGLASS_HEART:
                case NPC_HOURGLASS_RIFT:
                    me->SetCanFly(true);
                    me->SetDisableGravity(true);
                    break;
                default:
                    break;
            }
            Circle();
        }

        void Reset() override { }

        // The circlers' round: a cyclic flight, the radius where they were put.
        void Circle()
        {
            if (!Active())
                return;
            float cx, cy, speed;
            uint8 steps;
            if (me->GetEntry() == NPC_SKYGUARD)
                cx = NECROPOLIS_X, cy = NECROPOLIS_Y, speed = 7.0f, steps = 24;
            else if (me->GetEntry() == NPC_FROST_SPHERE)
                cx = HOURGLASS_X, cy = HOURGLASS_Y, speed = 2.5f, steps = 16;
            else
                return;
            float radius = std::hypot(me->GetPositionX() - cx, me->GetPositionY() - cy);
            me->GetMotionMaster()->MoveCirclePath(cx, cy, me->GetPositionZ(), radius, me->GetSpawnId() % 2 == 0, steps,
                FORCED_MOVEMENT_FLY, speed);
            flying = true;
        }

        bool Watched() const
        {
            return me->SelectNearestPlayer(WATCHED) != nullptr;
        }

        void Channel(uint32 spell)
        {
            if (me->GetCurrentSpell(CURRENT_CHANNELED_SPELL))
                return;
            if (Creature* heart = me->FindNearestCreature(NPC_HOURGLASS_HEART, 40.0f))
                me->CastSpell(heart, spell, true);
        }

        void UpdateAI(uint32 diff) override
        {
            if (!Active())
                return;
            if (!flying && (me->GetEntry() == NPC_SKYGUARD || me->GetEntry() == NPC_FROST_SPHERE))
                Circle();

            if (me->GetEntry() == NPC_HOURGLASS_SANDS)
            {
                pulseIn = pulseIn > diff ? pulseIn - diff : 0;
                sandIn = sandIn > diff ? sandIn - diff : 0;
                if (!pulseIn)
                {
                    pulseIn = urand(15000, 25000);
                    if (Watched())
                        DoCastSelf(SPELL_GOLD_PULSE, true);
                }
                if (!sandIn)
                {
                    sandIn = urand(35000, 50000);
                    if (Watched())
                        DoCastSelf(SPELL_HOURGLASS_SAND, true);
                }
                return;
            }

            if (timer > diff)
            {
                timer -= diff;
                return;
            }
            switch (me->GetEntry())
            {
                case NPC_SANDSHAPER:
                    timer = 2000;
                    if (Watched())
                        Channel(SPELL_BRONZE_BEAM);
                    else
                        me->InterruptNonMeleeSpells(false);
                    break;
                case NPC_HOURGLASS_RIFT:
                    timer = 2000;
                    if (Watched())
                        Channel(SPELL_GOLD_BEAM);
                    else
                        me->InterruptNonMeleeSpells(false);
                    break;
                case NPC_DUELIST:
                {
                    timer = urand(1800, 3200);
                    if (!Watched())
                        break;
                    static uint32 const moves[] = { EMOTE_ONESHOT_ATTACK1H, EMOTE_ONESHOT_ATTACK1H, EMOTE_ONESHOT_SPECIALATTACK1H,
                                                    EMOTE_ONESHOT_PARRY1H };
                    me->HandleEmoteCommand(moves[urand(0, 3)]);
                    break;
                }
                default:
                    timer = 60000;
                    break;
            }
        }
    };

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_remix_malykrissAI(creature);
    }
};

void AddRemixMalykrissScripts()
{
    new npc_remix_malykriss();
}
