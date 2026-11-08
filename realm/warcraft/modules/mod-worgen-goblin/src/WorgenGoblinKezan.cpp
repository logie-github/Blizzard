// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * Kezan's scripts: what the Cataclysm Preservation Project left unscripted on Kezan, written for
 * AzerothCore after LegionCore 7.3.5's (The Legion Preservation Project, src/server/scripts/Maelstrom/
 * LostIsles/kezan.cpp; GPL-2.0 or later) and Cataclysm's own spells. The world gives each creature and
 * spell here its script (tools/zones/scripts.py: CREATURE_SCRIPTS, SPELL_SCRIPTS), the vehicles their
 * seats (VEHICLES) and the Buccaneer its spell clicks (SPELL_CLICKS).
 *
 *  - Rolling with my Homies (14071): the keys summon the hot rod (Cataclysm's spell, its vehicle and its
 *    credit); driven up to Izzy, Ace or Gobber, each gets in (a seat of the hot rod's) and counts. Hired
 *    Looters it runs into are knocked away, their loot the player's for Robbing Hoods (14121).
 *  - The Great Bank Heist (14122): the vault's door seats the player at the vault (Cataclysm's vehicle and
 *    its five tools); it calls for a tool, the right one cracks it a tenth further, a wrong one or none in
 *    time (LegionCore's 5 seconds: 8 here, a phone's taps being slower) a tenth back. Cracked, it counts
 *    and gives the Personal Riches (Cataclysm's spell).
 *  - Necessary Roughness (24502): the Buccaneer (the spell click on the one standing on the field) takes
 *    the player in; eight sharks come at it (LegionCore's places), each footbomb thrown at the nearest
 *    (the game's aiming arc is a cursor's, which a phone hasn't). One reaching the Buccaneer ends the try.
 *  - Fourth and Goal (24503, 28414): the Buccaneer again, kicking: the kick goes through the uprights at
 *    the far end of the field and counts.
 *  - 447 (14125): the Gasbot Control Panel sends the Gasbot into the house, to the generator, where it
 *    blows up and counts.
 */

#include "WorgenGoblinZonesIds.h"
#include "CombatAI.h"
#include "GameObject.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "TemporarySummon.h"
#include "Vehicle.h"

using namespace WorgenGoblinZones;

namespace
{
    enum KezanIds : uint32
    {
        QUEST_ROLLING_WITH_MY_HOMIES    = 14071,
        QUEST_ROBBING_HOODS             = 14121,
        QUEST_GREAT_BANK_HEIST          = 14122,
        QUEST_447                       = 14125,
        QUEST_NECESSARY_ROUGHNESS       = 24502,
        QUEST_FOURTH_AND_GOAL           = 24503,
        QUEST_FOURTH_AND_GOAL_2         = 28414,

        NPC_HOT_ROD                     = 34840,
        NPC_IZZY                        = 34890,
        NPC_ACE                         = 34892,
        NPC_GOBBER                      = 34954,
        NPC_IZZY_RIDING                 = 34959,
        NPC_ACE_RIDING                  = 34957,
        NPC_GOBBER_RIDING               = 34958,
        NPC_HIRED_LOOTER                = 35234,
        NPC_VAULT                       = 35486,
        NPC_STEAMWHEEDLE_SHARK          = 37114,
        NPC_BUCCANEER                   = 37179,
        NPC_FOURTH_AND_GOAL_TARGET      = 37203,
        NPC_BUCCANEER_KICKER            = 37213,
        NPC_GASBOT                      = 37598,

        OBJECT_DEFECTIVE_GENERATOR      = 201735,

        SPELL_SUMMON_VAULT              = 67488,    // The Great Bank Heist: Summon Bunny Vehicle (the player rides it)
        SPELL_VAULT_CRACKED             = 67492,    // (the Personal Riches)
        SPELL_AMAZING_G_RAY             = 67526,
        SPELL_BLASTCRACKERS             = 67508,
        SPELL_EAR_O_SCOPE               = 67524,
        SPELL_INFINIFOLD_LOCKPICK       = 67525,
        SPELL_KAJAMITE_DRILL            = 67522,
        SPELL_FOOTBOMB_HIT              = 69993,    // Throw Footbomb's (the shark it hits)
        SPELL_KICK_FOOTBOMB_HIT         = 70052,
        SPELL_GASBOT_GAS_STREAM         = 70256,
        SPELL_GASBOT_EXPLOSION          = 70259,

        BROADCAST_VAULT_INTRO_1         = 35566,
        BROADCAST_VAULT_INTRO_2         = 35567,
        BROADCAST_VAULT_INTRO_3         = 35568,
        BROADCAST_USE_KAJAMITE_DRILL    = 35576,
        BROADCAST_USE_BLASTCRACKERS     = 35577,
        BROADCAST_USE_EAR_O_SCOPE       = 35578,
        BROADCAST_USE_LOCKPICK          = 35579,
        BROADCAST_USE_G_RAY             = 35700,
        BROADCAST_CORRECT               = 35702,
        BROADCAST_INCORRECT             = 35704,
    };

    uint32 constexpr ITEM_STOLEN_LOOT = 47530;     // (Cataclysm's item, the realm's same id)
    uint32 constexpr SPELL_RIDE_VEHICLE_HARDCODED = 46598;

    Player* Driver(Unit* vehicle)
    {
        if (Vehicle* kit = vehicle ? vehicle->GetVehicleKit() : nullptr)
            if (Unit* passenger = kit->GetPassenger(0))
                return passenger->ToPlayer();
        return nullptr;
    }

    bool OnQuest(Player const* player, uint32 quest)
    {
        return player && player->GetQuestStatus(Id(quest)) == QUEST_STATUS_INCOMPLETE;
    }
}

/*######
## Rolling with my Homies (14071), Robbing Hoods (14121)
######*/

// The homies standing about Kezan, and the ones riding (their seats in the hot rod: LegionCore's).
struct Homie
{
    uint32 standing, riding;
    int8 seat;
};

Homie constexpr HOMIES[] =
{
    { NPC_ACE, NPC_ACE_RIDING, 1 },
    { NPC_GOBBER, NPC_GOBBER_RIDING, 2 },
    { NPC_IZZY, NPC_IZZY_RIDING, 3 },
};

struct npc_kezan_hot_rod : public VehicleAI
{
    npc_kezan_hot_rod(Creature* creature) : VehicleAI(creature) { }

    void PassengerBoarded(Unit* passenger, int8 /*seatId*/, bool apply) override
    {
        if (!passenger->IsPlayer())
            return;
        if (apply)
            _events.ScheduleEvent(EVENT_RUN_OVER, 500ms);
        else
        {
            // Out of the hot rod: it's gone, the homies with it (they've counted).
            _events.Reset();
            if (Vehicle* kit = me->GetVehicleKit())
                kit->RemoveAllPassengers();
            me->DespawnOrUnsummon(1s);
        }
    }

    void UpdateAI(uint32 diff) override
    {
        VehicleAI::UpdateAI(diff);
        _events.Update(diff);
        if (_events.ExecuteEvent() != EVENT_RUN_OVER)
            return;
        Player* player = Driver(me);
        if (OnQuest(player, QUEST_ROBBING_HOODS))
        {
            std::list<Creature*> looters;
            me->GetCreatureListWithEntryInGrid(looters, Id(NPC_HIRED_LOOTER), 4.0f);
            for (Creature* looter : looters)
            {
                if (!looter->IsAlive())
                    continue;
                looter->KnockbackFrom(me->GetPositionX(), me->GetPositionY(), 12.0f, 8.0f);
                player->AddItem(ITEM_STOLEN_LOOT, 1);
                Unit::Kill(player, looter);
            }
        }
        _events.ScheduleEvent(EVENT_RUN_OVER, 500ms);
    }

private:
    enum { EVENT_RUN_OVER = 1 };
    EventMap _events;
};

// Izzy, Ace and Gobber: the hot rod driven up to one of them, the player's homie gets in.
struct npc_kezan_homie : public ScriptedAI
{
    npc_kezan_homie(Creature* creature) : ScriptedAI(creature) { }

    void MoveInLineOfSight(Unit* who) override
    {
        if (!who->IsCreature() || who->GetEntry() != Id(NPC_HOT_ROD) || !me->IsWithinDistInMap(who, 10.0f))
            return;
        Player* player = Driver(who);
        if (!OnQuest(player, QUEST_ROLLING_WITH_MY_HOMIES))
            return;
        for (Homie const& homie : HOMIES)
        {
            if (homie.standing != me->GetEntry() - ENTRY)
                continue;
            if (player->GetReqKillOrCastCurrentCount(Id(QUEST_ROLLING_WITH_MY_HOMIES), Id(homie.riding)) > 0)
                return;
            Vehicle* kit = who->GetVehicleKit();
            if (!kit || !kit->HasEmptySeat(homie.seat))
                return;
            if (TempSummon* riding = player->SummonCreature(Id(homie.riding), *me, TEMPSUMMON_MANUAL_DESPAWN))
            {
                player->KilledMonsterCredit(Id(homie.riding));
                riding->EnterVehicle(who, homie.seat);
            }
            return;
        }
    }

    void UpdateAI(uint32 /*diff*/) override
    {
        if (UpdateVictim())
            DoMeleeAttackIfReady();
    }
};

// A homie riding in the hot rod: never hurt (LegionCore's), gone once out of it.
struct npc_kezan_homie_riding : public ScriptedAI
{
    npc_kezan_homie_riding(Creature* creature) : ScriptedAI(creature) { }

    void Reset() override
    {
        _checkTimer = 3000;
    }

    void DamageTaken(Unit* /*attacker*/, uint32& damage, DamageEffectType /*type*/, SpellSchoolMask /*school*/) override
    {
        damage = 0;
    }

    void UpdateAI(uint32 diff) override
    {
        if (_checkTimer <= diff)
        {
            _checkTimer = 2000;
            if (!me->GetVehicle())
            {
                me->DespawnOrUnsummon();
                return;
            }
        }
        else
            _checkTimer -= diff;
        if (UpdateVictim())
            DoMeleeAttackIfReady();
    }

private:
    uint32 _checkTimer = 3000;
};

/*######
## The Great Bank Heist (14122)
######*/

struct VaultTool
{
    uint32 spell, broadcast;
};

VaultTool constexpr VAULT_TOOLS[] =
{
    { SPELL_AMAZING_G_RAY, BROADCAST_USE_G_RAY },
    { SPELL_BLASTCRACKERS, BROADCAST_USE_BLASTCRACKERS },
    { SPELL_EAR_O_SCOPE, BROADCAST_USE_EAR_O_SCOPE },
    { SPELL_INFINIFOLD_LOCKPICK, BROADCAST_USE_LOCKPICK },
    { SPELL_KAJAMITE_DRILL, BROADCAST_USE_KAJAMITE_DRILL },
};

// The vault the player sits at: it calls for a tool; the right one cracks it a tenth further.
struct npc_kezan_vault : public VehicleAI
{
    npc_kezan_vault(Creature* creature) : VehicleAI(creature) { }

    void PassengerBoarded(Unit* passenger, int8 /*seatId*/, bool apply) override
    {
        if (!passenger->IsPlayer() || !apply)
        {
            _events.Reset();
            me->DespawnOrUnsummon(1s);
            return;
        }
        _player = passenger->GetGUID();
        me->setPowerType(POWER_MANA);
        me->SetMaxPower(POWER_MANA, 100);
        me->SetPower(POWER_MANA, 0);
        _events.ScheduleEvent(EVENT_INTRO_1, 1s);
    }

    // A tool used (spell_kezan_vault_tool).
    void SetData(uint32 spell, uint32 /*value*/) override
    {
        if (!_called)
            return;
        bool right = spell == SpellId(_called->spell);
        _called = nullptr;
        _events.CancelEvent(EVENT_TIMEOUT);
        Answer(right);
    }

    void UpdateAI(uint32 diff) override
    {
        VehicleAI::UpdateAI(diff);
        _events.Update(diff);
        while (uint32 eventId = _events.ExecuteEvent())
        {
            Player* player = ObjectAccessor::GetPlayer(*me, _player);
            if (!player)
            {
                me->DespawnOrUnsummon();
                return;
            }
            switch (eventId)
            {
                case EVENT_INTRO_1:
                    me->Whisper(Id(BROADCAST_VAULT_INTRO_1), player, true);
                    _events.ScheduleEvent(EVENT_INTRO_2, 5s);
                    break;
                case EVENT_INTRO_2:
                    me->Whisper(Id(BROADCAST_VAULT_INTRO_2), player, true);
                    _events.ScheduleEvent(EVENT_INTRO_3, 6s);
                    break;
                case EVENT_INTRO_3:
                    me->Whisper(Id(BROADCAST_VAULT_INTRO_3), player, true);
                    _events.ScheduleEvent(EVENT_CALL, 6s);
                    break;
                case EVENT_CALL:
                    _called = &VAULT_TOOLS[urand(0, std::size(VAULT_TOOLS) - 1)];
                    me->Whisper(Id(_called->broadcast), player, true);
                    _events.ScheduleEvent(EVENT_TIMEOUT, 8s);
                    break;
                case EVENT_TIMEOUT:
                    _called = nullptr;
                    Answer(false);
                    break;
                case EVENT_DONE:
                    if (Vehicle* kit = me->GetVehicleKit())
                        kit->RemoveAllPassengers();
                    break;
                default:
                    break;
            }
        }
    }

private:
    enum { EVENT_INTRO_1 = 1, EVENT_INTRO_2, EVENT_INTRO_3, EVENT_CALL, EVENT_TIMEOUT, EVENT_DONE };

    void Answer(bool right)
    {
        Player* player = ObjectAccessor::GetPlayer(*me, _player);
        if (!player)
            return;
        int32 power = int32(me->GetPower(POWER_MANA)) + (right ? 10 : -10);
        me->SetPower(POWER_MANA, uint32(std::clamp(power, 0, 100)));
        me->Whisper(Id(right ? BROADCAST_CORRECT : BROADCAST_INCORRECT), player, true);
        if (right && power >= 100)
        {
            if (OnQuest(player, QUEST_GREAT_BANK_HEIST))
            {
                player->KilledMonsterCredit(Id(NPC_VAULT));
                player->CastSpell(player, SpellId(SPELL_VAULT_CRACKED), true);
            }
            _events.ScheduleEvent(EVENT_DONE, 2s);
            return;
        }
        _events.ScheduleEvent(EVENT_CALL, right ? 2s : 3s);
    }

    EventMap _events;
    ObjectGuid _player;
    VaultTool const* _called = nullptr;
};

// The vault's door (the First Bank of Kezan Vault object's spell): the player sits at the vault.
class spell_kezan_vault_interact : public SpellScript
{
    PrepareSpellScript(spell_kezan_vault_interact);

    void HandleScript(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetHitUnit() ? GetHitUnit()->ToPlayer() : nullptr;
        if (OnQuest(player, QUEST_GREAT_BANK_HEIST) && !player->GetVehicle())
            player->CastSpell(player, SpellId(SPELL_SUMMON_VAULT), true);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_kezan_vault_interact::HandleScript, EFFECT_0, SPELL_EFFECT_SCRIPT_EFFECT);
    }
};

// The vault's tools (the vehicle's spells): which one, to the vault.
class spell_kezan_vault_tool : public SpellScript
{
    PrepareSpellScript(spell_kezan_vault_tool);

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        Creature* vault = caster->GetEntry() == Id(NPC_VAULT) ? caster->ToCreature() : caster->GetVehicleCreatureBase();
        if (vault && vault->GetEntry() == Id(NPC_VAULT) && vault->IsAIEnabled)
            vault->AI()->SetData(GetSpellInfo()->Id, 0);
    }

    void Register() override
    {
        OnEffectHit += SpellEffectFn(spell_kezan_vault_tool::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

/*######
## Necessary Roughness (24502), Fourth and Goal (24503, 28414)
######*/

// The sharks' places (LegionCore's: Cataclysm's summon spells' places), each running at the Buccaneer.
Position const SHARK_SPAWNS[] =
{
    { -8288.62f, 1479.97f, 43.8908f, 0.0f },
    { -8273.75f, 1484.46f, 42.9395f, 0.0f },
    { -8288.08f, 1487.72f, 43.8463f, 0.0f },
    { -8281.04f, 1477.49f, 43.3046f, 0.0f },
    { -8281.33f, 1490.41f, 43.4756f, 0.0f },
    { -8295.10f, 1484.91f, 44.3231f, 0.0f },
    { -8294.66f, 1474.68f, 44.2946f, 0.0f },
    { -8294.61f, 1493.67f, 44.6239f, 0.0f },
};

enum FootballActions : int32
{
    ACTION_SHARK_THROUGH = 1,   // a shark reached the Buccaneer: the try ends
    ACTION_SHARK_DOWN,
};

struct npc_kezan_buccaneer : public VehicleAI
{
    npc_kezan_buccaneer(Creature* creature) : VehicleAI(creature), _summons(creature) { }

    void PassengerBoarded(Unit* passenger, int8 /*seatId*/, bool apply) override
    {
        if (!passenger->IsPlayer())
            return;
        if (apply)
        {
            me->SetControlled(true, UNIT_STATE_ROOT);
            if (OnQuest(passenger->ToPlayer(), QUEST_NECESSARY_ROUGHNESS))
                _events.ScheduleEvent(EVENT_SHARKS, 4s);
        }
        else
        {
            _events.Reset();
            _summons.DespawnAll();
            me->DespawnOrUnsummon(1s);
        }
    }

    void JustSummoned(Creature* summon) override
    {
        _summons.Summon(summon);
    }

    void DoAction(int32 action) override
    {
        Player* player = Driver(me);
        if (action == ACTION_SHARK_THROUGH || (action == ACTION_SHARK_DOWN && player
            && player->GetQuestStatus(Id(QUEST_NECESSARY_ROUGHNESS)) == QUEST_STATUS_COMPLETE))
            _events.ScheduleEvent(EVENT_END, 2s);
    }

    void UpdateAI(uint32 diff) override
    {
        VehicleAI::UpdateAI(diff);
        _events.Update(diff);
        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_SHARKS:
                    for (Position const& spawn : SHARK_SPAWNS)
                    {
                        Position pos = spawn;
                        pos.SetOrientation(pos.GetAbsoluteAngle(me));
                        me->SummonCreature(Id(NPC_STEAMWHEEDLE_SHARK), pos, TEMPSUMMON_TIMED_DESPAWN, 120000);
                    }
                    break;
                case EVENT_END:
                    _summons.DespawnAll();
                    if (Vehicle* kit = me->GetVehicleKit())
                        kit->RemoveAllPassengers();
                    break;
                default:
                    break;
            }
        }
    }

private:
    enum { EVENT_SHARKS = 1, EVENT_END };
    EventMap _events;
    SummonList _summons;
};

// A shark running at the Buccaneer a few steps at a time (LegionCore's paths: 5 seconds between).
struct npc_kezan_shark : public ScriptedAI
{
    npc_kezan_shark(Creature* creature) : ScriptedAI(creature) { }

    void IsSummonedBy(WorldObject* summoner) override
    {
        _buccaneer = summoner->GetGUID();
        me->SetReactState(REACT_PASSIVE);
        _events.ScheduleEvent(EVENT_STEP, 2s, 5s);
    }

    void SpellHit(Unit* caster, SpellInfo const* spell) override
    {
        if (_down || spell->Id != SpellId(SPELL_FOOTBOMB_HIT))
            return;
        _down = true;
        _events.Reset();
        me->GetMotionMaster()->Clear();
        me->GetMotionMaster()->MoveIdle();
        if (Player* player = Driver(caster))
            if (OnQuest(player, QUEST_NECESSARY_ROUGHNESS))
                player->KilledMonsterCredit(Id(NPC_STEAMWHEEDLE_SHARK));
        if (caster->IsCreature() && caster->IsAIEnabled)
            caster->ToCreature()->AI()->DoAction(ACTION_SHARK_DOWN);
        me->SetStandState(UNIT_STAND_STATE_DEAD);
        me->DespawnOrUnsummon(2s);
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);
        if (_events.ExecuteEvent() != EVENT_STEP || _down)
            return;
        Creature* buccaneer = ObjectAccessor::GetCreature(*me, _buccaneer);
        if (!buccaneer)
        {
            me->DespawnOrUnsummon();
            return;
        }
        if (me->GetExactDist2d(buccaneer) < 4.0f)
        {
            if (buccaneer->IsAIEnabled)
                buccaneer->AI()->DoAction(ACTION_SHARK_THROUGH);
            return;
        }
        float step = std::min(9.0f, me->GetExactDist2d(buccaneer) - 3.0f);
        Position next = me->GetPosition();
        me->MovePosition(next, step, me->GetRelativeAngle(buccaneer));
        me->GetMotionMaster()->MovePoint(1, next);
        _events.ScheduleEvent(EVENT_STEP, 5s);
    }

private:
    enum { EVENT_STEP = 1 };
    EventMap _events;
    ObjectGuid _buccaneer;
    bool _down = false;
};

// Throw Footbomb: at the nearest shark.
class spell_kezan_throw_footbomb : public SpellScript
{
    PrepareSpellScript(spell_kezan_throw_footbomb);

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        if (Creature* shark = caster->FindNearestCreature(Id(NPC_STEAMWHEEDLE_SHARK), 60.0f, true))
            caster->CastSpell(shark, SpellId(SPELL_FOOTBOMB_HIT), true);
    }

    void Register() override
    {
        OnEffectHit += SpellEffectFn(spell_kezan_throw_footbomb::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// Fourth and Goal's Buccaneer (Cataclysm summons it beside the player): the player gets in.
struct npc_kezan_buccaneer_kicker : public VehicleAI
{
    npc_kezan_buccaneer_kicker(Creature* creature) : VehicleAI(creature) { }

    void IsSummonedBy(WorldObject* summoner) override
    {
        _player = summoner->GetGUID();
        _events.ScheduleEvent(EVENT_BOARD, 200ms);
    }

    void PassengerBoarded(Unit* passenger, int8 /*seatId*/, bool apply) override
    {
        if (!passenger->IsPlayer())
            return;
        if (apply)
        {
            me->SetControlled(true, UNIT_STATE_ROOT);
            if (Creature* goal = me->FindNearestCreature(Id(NPC_FOURTH_AND_GOAL_TARGET), 500.0f, true))
                me->SetFacingToObject(goal);
        }
        else
            me->DespawnOrUnsummon(1s);
    }

    // The kick through (spell_kezan_kick_footbomb): out after it.
    void DoAction(int32 /*action*/) override
    {
        _events.ScheduleEvent(EVENT_END, 3s);
    }

    void UpdateAI(uint32 diff) override
    {
        VehicleAI::UpdateAI(diff);
        _events.Update(diff);
        while (uint32 eventId = _events.ExecuteEvent())
        {
            if (eventId == EVENT_BOARD)
            {
                if (Player* player = ObjectAccessor::GetPlayer(*me, _player))
                    player->CastSpell(me, SPELL_RIDE_VEHICLE_HARDCODED, true);
            }
            else if (eventId == EVENT_END)
                if (Vehicle* kit = me->GetVehicleKit())
                    kit->RemoveAllPassengers();
        }
    }

private:
    enum { EVENT_BOARD = 1, EVENT_END };
    EventMap _events;
    ObjectGuid _player;
};

// Kick Footbomb: through the uprights (the target at the field's far end) and counted.
class spell_kezan_kick_footbomb : public SpellScript
{
    PrepareSpellScript(spell_kezan_kick_footbomb);

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        Creature* goal = caster->FindNearestCreature(Id(NPC_FOURTH_AND_GOAL_TARGET), 500.0f, true);
        if (!goal)
            return;
        caster->CastSpell(goal, SpellId(SPELL_KICK_FOOTBOMB_HIT), true);
        if (Player* player = Driver(caster))
            if (OnQuest(player, QUEST_FOURTH_AND_GOAL) || OnQuest(player, QUEST_FOURTH_AND_GOAL_2))
                player->KilledMonsterCredit(Id(NPC_FOURTH_AND_GOAL_TARGET));
        if (caster->IsCreature() && caster->IsAIEnabled)
            caster->ToCreature()->AI()->DoAction(0);
    }

    void Register() override
    {
        OnEffectHit += SpellEffectFn(spell_kezan_kick_footbomb::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

/*######
## 447 (14125)
######*/

// The generator in the house (where the object stands in CPP's world: the Gasbot's way when it isn't found).
Position const GENERATOR = { -8420.86f, 1372.62f, 104.663f, 0.0f };

// The Gasbot Control Panel: the Gasbot, the player's.
class spell_kezan_gasbot_panel : public SpellScript
{
    PrepareSpellScript(spell_kezan_gasbot_panel);

    void HandleScript(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetHitUnit() ? GetHitUnit()->ToPlayer() : nullptr;
        if (!OnQuest(player, QUEST_447) || player->GetReqKillOrCastCurrentCount(Id(QUEST_447), Id(NPC_GASBOT)) > 0)
            return;
        if (player->FindNearestCreature(Id(NPC_GASBOT), 80.0f, true))
            return;
        Position pos = player->GetPosition();
        player->MovePosition(pos, 3.0f, 0.0f);
        player->SummonCreature(Id(NPC_GASBOT), pos, TEMPSUMMON_TIMED_DESPAWN, 90000);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_kezan_gasbot_panel::HandleScript, EFFECT_0, SPELL_EFFECT_SCRIPT_EFFECT);
    }
};

struct npc_kezan_gasbot : public ScriptedAI
{
    npc_kezan_gasbot(Creature* creature) : ScriptedAI(creature) { }

    void IsSummonedBy(WorldObject* summoner) override
    {
        _player = summoner->GetGUID();
        me->SetReactState(REACT_PASSIVE);
        Position target = GENERATOR;
        if (GameObject* generator = me->FindNearestGameObject(Id(OBJECT_DEFECTIVE_GENERATOR), 150.0f))
            target = generator->GetPosition();
        me->GetMotionMaster()->MovePoint(POINT_GENERATOR, target);
    }

    void MovementInform(uint32 type, uint32 id) override
    {
        if (type == POINT_MOTION_TYPE && id == POINT_GENERATOR)
        {
            DoCastSelf(SpellId(SPELL_GASBOT_GAS_STREAM), true);
            _events.ScheduleEvent(EVENT_EXPLODE, 4s);
        }
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);
        if (_events.ExecuteEvent() != EVENT_EXPLODE)
            return;
        DoCastSelf(SpellId(SPELL_GASBOT_EXPLOSION), true);
        if (Player* player = ObjectAccessor::GetPlayer(*me, _player))
            if (OnQuest(player, QUEST_447))
                player->KilledMonsterCredit(Id(NPC_GASBOT));
        me->DespawnOrUnsummon(1s);
    }

private:
    enum { POINT_GENERATOR = 1, EVENT_EXPLODE = 1 };
    EventMap _events;
    ObjectGuid _player;
};

void AddWorgenGoblinKezanScripts()
{
    RegisterCreatureAI(npc_kezan_hot_rod);
    RegisterCreatureAI(npc_kezan_homie);
    RegisterCreatureAI(npc_kezan_homie_riding);
    RegisterCreatureAI(npc_kezan_vault);
    RegisterSpellScript(spell_kezan_vault_interact);
    RegisterSpellScript(spell_kezan_vault_tool);
    RegisterCreatureAI(npc_kezan_buccaneer);
    RegisterCreatureAI(npc_kezan_shark);
    RegisterSpellScript(spell_kezan_throw_footbomb);
    RegisterCreatureAI(npc_kezan_buccaneer_kicker);
    RegisterSpellScript(spell_kezan_kick_footbomb);
    RegisterSpellScript(spell_kezan_gasbot_panel);
    RegisterCreatureAI(npc_kezan_gasbot);
}
