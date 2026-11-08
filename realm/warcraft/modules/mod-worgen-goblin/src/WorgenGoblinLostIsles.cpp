// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * The Lost Isles' scripts: what the Cataclysm Preservation Project left unscripted there (CPP has the
 * zone's creatures, quests and texts, and next to none of its vehicles, paths or scripts), written for
 * AzerothCore after LegionCore 7.3.5's (The Legion Preservation Project, src/server/scripts/Maelstrom/
 * LostIsles/lost_isles.cpp; GPL-2.0 or later) and Cataclysm's spells. Where Cataclysm used a vehicle or
 * a flight nobody's data has (the Cyclone of the Elements, the Rocket Sling, the mine cart), the quest
 * keeps its objective in a simpler way, at the user's word ("if it's not crucial to the quest you can
 * skip it or change it"). The world gives each creature, object and spell here its script
 * (tools/zones/scripts.py).
 *
 *  - Goblin Escape Pods (14001, 14474): a pod opened lets out a Goblin Survivor, who counts.
 *  - Monkey Business (14019): a Nitro-Potassium Banana fed to a Bomb-Throwing Monkey counts (and it
 *    blows up).
 *  - Miner Troubles (14021): taking it, Foreman Dampwick sends a Frightened Miner, who mines the four
 *    nearest Kaja'mite Ore seams in the cavern and counts at the last.
 *  - Capturing the Unknown (14031): the KTC Snapflash counts the painting or altar it's used beside.
 *  - Precious Cargo (14242): Thrall found below deck counts.
 *  - Warchief's Revenge (14243): taking it, the Cyclone of the Elements comes to the player and strikes
 *    down the Alliance Sailors on the Vengeance Wake about them; at fifty, it takes the player to the
 *    Wild Overlook.
 *  - Up, Up & Away! (14244): taking it, Sassy's Rocket Sling sends the player over the Dire Strait to
 *    the landing site.
 *  - Cluster Cluck (24671): the Remote Control Fireworks on a Wild Clucker count (it runs off).
 *  - Irresistible Pool Pony (24864): the pony set out draws the Naga Hatchlings about it, each counted.
 *  - Surrender or Else! (24868): the Faceless of the Deep can be fought by a player on it.
 *  - Town-In-A-Box: Under Attack (24901): an Oomlot Warrior the B.C. Eliminator kills counts (its
 *    Fire Cannon aimed at the nearest).
 *  - Zombies vs. Super Booster Rocket Boots (24942): the boots for a minute: zombies run into are
 *    killed and counted.
 *  - Volcanoth! (24958): the Bootzooka takes a fifth of Volcanoth's health a shot; his death counts.
 *  - Throw It On the Ground! (25123): Blastshadow's Soulstone thrown down counts.
 *  - Wild Mine Cart Ride (25184): taking it, the cart takes the player to the end of the line.
 *  (Free the Captives and Repel the Paratroopers count by the kill: the world's KILL_CREDITS.)
 */

#include "WorgenGoblinZonesIds.h"
#include "GameObject.h"
#include "GameObjectAI.h"
#include "Map.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "SpellAuraEffects.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "TemporarySummon.h"
#include <set>

using namespace WorgenGoblinZones;

namespace
{
    enum LostIslesIds : uint32
    {
        QUEST_GOBLIN_ESCAPE_PODS        = 14001,
        QUEST_GOBLIN_ESCAPE_PODS_2      = 14474,
        QUEST_MONKEY_BUSINESS           = 14019,
        QUEST_MINER_TROUBLES            = 14021,
        QUEST_CAPTURING_THE_UNKNOWN     = 14031,
        QUEST_PRECIOUS_CARGO            = 14242,
        QUEST_WARCHIEFS_REVENGE         = 14243,
        QUEST_UP_UP_AND_AWAY            = 14244,
        QUEST_CLUSTER_CLUCK             = 24671,
        QUEST_IRRESISTIBLE_POOL_PONY    = 24864,
        QUEST_SURRENDER_OR_ELSE         = 24868,
        QUEST_TOWN_UNDER_ATTACK         = 24901,
        QUEST_ZOMBIES_VS_ROCKET_BOOTS   = 24942,
        QUEST_VOLCANOTH                 = 24958,
        QUEST_THROW_IT_ON_THE_GROUND    = 25123,
        QUEST_WILD_MINE_CART_RIDE       = 25184,

        NPC_GOBLIN_SURVIVOR             = 34748,
        NPC_BOMB_THROWING_MONKEY        = 34699,
        NPC_MONKEY_BUSINESS_CREDIT      = 35760,
        NPC_FRIGHTENED_MINER            = 35813,
        NPC_MINER_TROUBLES_CREDIT       = 35816,
        NPC_CAPTURE_BUNNY_1             = 37872,
        NPC_CAPTURE_BUNNY_2             = 37895,
        NPC_CAPTURE_BUNNY_3             = 37896,
        NPC_CAPTURE_BUNNY_4             = 37897,
        NPC_THRALL_BELOW_DECK           = 36145,
        NPC_CYCLONE_OF_THE_ELEMENTS     = 36178,
        NPC_ALLIANCE_SAILOR             = 36176,
        NPC_UP_UP_AND_AWAY_CREDIT       = 50046,
        NPC_WILD_CLUCKER                = 38111,
        NPC_CLUSTER_CLUCK_CREDIT        = 38117,
        NPC_NAGA_HATCHLING              = 38412,
        NPC_NAGA_HATCHLING_2            = 44578,
        NPC_NAGA_HATCHLING_3            = 44579,
        NPC_NAGA_HATCHLING_4            = 44580,
        NPC_NAGA_HATCHLING_CREDIT       = 38413,
        NPC_BC_ELIMINATOR               = 38526,
        NPC_OOMLOT_WARRIOR              = 38531,
        NPC_TOWN_UNDER_ATTACK_CREDIT    = 38536,
        NPC_GOBLIN_ZOMBIE               = 38753,
        NPC_GOBLIN_ZOMBIE_2             = 38813,
        NPC_GOBLIN_ZOMBIE_3             = 38815,
        NPC_GOBLIN_ZOMBIE_4             = 38816,
        NPC_ROCKET_BOOTS_CREDIT         = 38807,
        NPC_VOLCANOTH_CREDIT            = 38868,
        NPC_THROW_IT_ON_THE_GROUND_CREDIT = 39276,
        NPC_WILD_MINE_CART_CREDIT       = 39335,

        OBJECT_KAJAMITE_ORE             = 195622,

        SPELL_NITRO_POTASSIUM_BANANAS   = 67917,
        SPELL_KTC_SNAPFLASH             = 68280,
        SPELL_REMOTE_CONTROL_FIREWORKS  = 71170,
        SPELL_BOOTS_DAMAGE_AURA         = 72885,
        SPELL_BOOTZOOKA                 = 73066,
        SPELL_CYCLONE_LIGHTNING_STRIKE  = 68445,
        SPELL_CANNON_BLAST              = 72207,
    };

    uint32 constexpr SPELL_SPRINT = 2983;          // (3.3.5a's own: the boots' speed)

    // Where a quest's flight ends (Cataclysm's: its ender's place; the ender CPP's).
    Position const WILD_OVERLOOK = { 872.7f, 2761.4f, 119.3f, 1.69f };
    Position const LANDING_SITE = { 943.8f, 2372.6f, 5.6f, 1.50f };
    Position const END_OF_THE_LINE = { 1781.0f, 1983.2f, 173.1f, 0.0f };

    bool OnQuest(Player const* player, uint32 quest)
    {
        return player && player->GetQuestStatus(Id(quest)) == QUEST_STATUS_INCOMPLETE;
    }

    bool IsOneOf(Unit const* unit, std::initializer_list<uint32> entries)
    {
        for (uint32 entry : entries)
            if (unit->GetEntry() == Id(entry))
                return true;
        return false;
    }

    void FlyTo(Player* player, Position const& where)
    {
        player->TeleportTo(player->GetMapId(), where.GetPositionX(), where.GetPositionY(), where.GetPositionZ(), where.GetOrientation());
    }
}

/*######
## Goblin Escape Pods (14001, 14474)
######*/

struct go_lost_isles_escape_pod : public GameObjectAI
{
    go_lost_isles_escape_pod(GameObject* go) : GameObjectAI(go) { }

    bool GossipHello(Player* player, bool /*reportUse*/) override
    {
        if (!OnQuest(player, QUEST_GOBLIN_ESCAPE_PODS) && !OnQuest(player, QUEST_GOBLIN_ESCAPE_PODS_2))
            return false;
        if (Creature* survivor = me->SummonCreature(Id(NPC_GOBLIN_SURVIVOR), *me, TEMPSUMMON_TIMED_DESPAWN, 8000))
        {
            survivor->HandleEmoteCommand(EMOTE_ONESHOT_CHEER);
            Position away = survivor->GetPosition();
            survivor->MovePosition(away, 10.0f, float(rand_norm()) * 2.0f * float(M_PI));
            survivor->GetMotionMaster()->MovePoint(0, away);
        }
        player->KilledMonsterCredit(Id(NPC_GOBLIN_SURVIVOR));
        me->SetLootState(GO_JUST_DEACTIVATED);
        return true;
    }
};

/*######
## Monkey Business (14019)
######*/

class spell_lost_isles_nitro_potassium_bananas : public SpellScript
{
    PrepareSpellScript(spell_lost_isles_nitro_potassium_bananas);

    void HandleScript(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        Creature* monkey = GetHitCreature();
        if (!OnQuest(player, QUEST_MONKEY_BUSINESS) || !monkey || !monkey->IsAlive() || monkey->GetEntry() != Id(NPC_BOMB_THROWING_MONKEY))
            return;
        player->KilledMonsterCredit(Id(NPC_MONKEY_BUSINESS_CREDIT));
        monkey->HandleEmoteCommand(EMOTE_ONESHOT_EAT);
        Unit::Kill(player, monkey);
        monkey->DespawnOrUnsummon(3s);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_lost_isles_nitro_potassium_bananas::HandleScript, EFFECT_0, SPELL_EFFECT_SCRIPT_EFFECT);
    }
};

/*######
## Miner Troubles (14021)
######*/

struct npc_lost_isles_foreman_dampwick : public ScriptedAI
{
    npc_lost_isles_foreman_dampwick(Creature* creature) : ScriptedAI(creature) { }

    void sQuestAccept(Player* player, Quest const* quest) override
    {
        if (quest->GetQuestId() != Id(QUEST_MINER_TROUBLES))
            return;
        Position pos = me->GetPosition();
        me->MovePosition(pos, 3.0f, 0.0f);
        if (TempSummon* miner = player->SummonCreature(Id(NPC_FRIGHTENED_MINER), pos, TEMPSUMMON_TIMED_DESPAWN, 300000))
            miner->AI()->SetGUID(player->GetGUID(), 0);
    }
};

// The miner, to the four nearest seams of ore in turn (LegionCore's: four stops on the cavern's way).
struct npc_lost_isles_frightened_miner : public ScriptedAI
{
    npc_lost_isles_frightened_miner(Creature* creature) : ScriptedAI(creature) { }

    void SetGUID(ObjectGuid const& guid, int32 /*id*/) override
    {
        _player = guid;
        me->SetReactState(REACT_PASSIVE);
        _events.ScheduleEvent(EVENT_NEXT_ORE, 2s);
    }

    void MovementInform(uint32 type, uint32 id) override
    {
        if (type == POINT_MOTION_TYPE && id == POINT_ORE)
        {
            me->SetUInt32Value(UNIT_NPC_EMOTESTATE, EMOTE_STATE_WORK_MINING);
            _events.ScheduleEvent(EVENT_MINED, 6s);
        }
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);
        while (uint32 eventId = _events.ExecuteEvent())
        {
            Player* player = ObjectAccessor::GetPlayer(*me, _player);
            if (!player || !OnQuest(player, QUEST_MINER_TROUBLES))
            {
                me->DespawnOrUnsummon(1s);
                return;
            }
            if (eventId == EVENT_MINED)
            {
                me->SetUInt32Value(UNIT_NPC_EMOTESTATE, EMOTE_ONESHOT_NONE);
                if (++_mined >= ORES)
                {
                    player->KilledMonsterCredit(Id(NPC_MINER_TROUBLES_CREDIT));
                    me->HandleEmoteCommand(EMOTE_ONESHOT_CHEER);
                    me->DespawnOrUnsummon(5s);
                    return;
                }
                _events.ScheduleEvent(EVENT_NEXT_ORE, 1s);
            }
            else if (eventId == EVENT_NEXT_ORE)
                GoToNextOre();
        }
    }

private:
    enum { EVENT_NEXT_ORE = 1, EVENT_MINED, POINT_ORE = 1, ORES = 4 };

    void GoToNextOre()
    {
        std::list<GameObject*> ores;
        me->GetGameObjectListWithEntryInGrid(ores, Id(OBJECT_KAJAMITE_ORE), 120.0f);
        GameObject* nearest = nullptr;
        for (GameObject* ore : ores)
            if (!_visited.count(ore->GetGUID()) && (!nearest || me->GetDistance(ore) < me->GetDistance(nearest)))
                nearest = ore;
        if (!nearest)
        {
            // (fewer seams than four about: the miner's done with what there is)
            _mined = ORES - 1;
            _events.ScheduleEvent(EVENT_MINED, 3s);
            return;
        }
        _visited.insert(nearest->GetGUID());
        Position spot = nearest->GetPosition();
        nearest->MovePosition(spot, 1.5f, nearest->GetRelativeAngle(me));
        me->GetMotionMaster()->MovePoint(POINT_ORE, spot);
    }

    EventMap _events;
    ObjectGuid _player;
    std::set<ObjectGuid> _visited;
    uint32 _mined = 0;
};

/*######
## Capturing the Unknown (14031)
######*/

class spell_lost_isles_ktc_snapflash : public SpellScript
{
    PrepareSpellScript(spell_lost_isles_ktc_snapflash);

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        if (!OnQuest(player, QUEST_CAPTURING_THE_UNKNOWN))
            return;
        for (uint32 bunny : { NPC_CAPTURE_BUNNY_1, NPC_CAPTURE_BUNNY_2, NPC_CAPTURE_BUNNY_3, NPC_CAPTURE_BUNNY_4 })
            if (player->FindNearestCreature(Id(bunny), 30.0f))
                player->KilledMonsterCredit(Id(bunny));
    }

    void Register() override
    {
        OnEffectHit += SpellEffectFn(spell_lost_isles_ktc_snapflash::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

/*######
## Precious Cargo (14242)
######*/

struct npc_lost_isles_thrall_below_deck : public ScriptedAI
{
    npc_lost_isles_thrall_below_deck(Creature* creature) : ScriptedAI(creature) { }

    void MoveInLineOfSight(Unit* who) override
    {
        if (Player* player = who->ToPlayer())
            if (OnQuest(player, QUEST_PRECIOUS_CARGO) && me->IsWithinDistInMap(player, 12.0f))
                player->KilledMonsterCredit(Id(NPC_THRALL_BELOW_DECK));
    }
};

/*######
## Warchief's Revenge (14243)
######*/

struct npc_lost_isles_thrall_cyclone : public ScriptedAI
{
    npc_lost_isles_thrall_cyclone(Creature* creature) : ScriptedAI(creature) { }

    void sQuestAccept(Player* player, Quest const* quest) override
    {
        if (quest->GetQuestId() != Id(QUEST_WARCHIEFS_REVENGE))
            return;
        if (TempSummon* cyclone = player->SummonCreature(Id(NPC_CYCLONE_OF_THE_ELEMENTS), player->GetPosition(), TEMPSUMMON_TIMED_DESPAWN, 600000))
            cyclone->AI()->SetGUID(player->GetGUID(), 0);
    }
};

// The Cyclone: with the player, striking the sailors about them down.
struct npc_lost_isles_cyclone : public ScriptedAI
{
    npc_lost_isles_cyclone(Creature* creature) : ScriptedAI(creature) { }

    void SetGUID(ObjectGuid const& guid, int32 /*id*/) override
    {
        _player = guid;
        me->SetReactState(REACT_PASSIVE);
        me->SetUnitFlag(UNIT_FLAG_NON_ATTACKABLE);
        if (Player* player = ObjectAccessor::GetPlayer(*me, _player))
            me->GetMotionMaster()->MoveFollow(player, 3.0f, 0.0f);
        _events.ScheduleEvent(EVENT_STRIKE, 2s);
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);
        if (_events.ExecuteEvent() != EVENT_STRIKE)
            return;
        Player* player = ObjectAccessor::GetPlayer(*me, _player);
        if (!player || player->GetQuestStatus(Id(QUEST_WARCHIEFS_REVENGE)) == QUEST_STATUS_NONE)
        {
            me->DespawnOrUnsummon();
            return;
        }
        if (player->GetQuestStatus(Id(QUEST_WARCHIEFS_REVENGE)) == QUEST_STATUS_COMPLETE)
        {
            FlyTo(player, WILD_OVERLOOK);
            me->DespawnOrUnsummon();
            return;
        }
        std::list<Creature*> sailors;
        player->GetCreatureListWithEntryInGrid(sailors, Id(NPC_ALLIANCE_SAILOR), 40.0f);
        uint32 struck = 0;
        for (Creature* sailor : sailors)
        {
            if (!sailor->IsAlive() || struck >= 3)
                continue;
            me->CastSpell(sailor, SpellId(SPELL_CYCLONE_LIGHTNING_STRIKE), true);
            Unit::Kill(player, sailor);
            ++struck;
        }
        _events.ScheduleEvent(EVENT_STRIKE, 2s);
    }

private:
    enum { EVENT_STRIKE = 1 };
    EventMap _events;
    ObjectGuid _player;
};

/*######
## Up, Up & Away! (14244), Wild Mine Cart Ride (25184)
######*/

// A quest that ends in a flight (the Rocket Sling, the mine cart): the player there, and counted.
struct npc_lost_isles_flight_giver : public ScriptedAI
{
    npc_lost_isles_flight_giver(Creature* creature) : ScriptedAI(creature) { }

    void sQuestAccept(Player* player, Quest const* quest) override
    {
        if (quest->GetQuestId() == Id(QUEST_UP_UP_AND_AWAY))
            Send(player, LANDING_SITE, NPC_UP_UP_AND_AWAY_CREDIT);
        else if (quest->GetQuestId() == Id(QUEST_WILD_MINE_CART_RIDE))
            Send(player, END_OF_THE_LINE, NPC_WILD_MINE_CART_CREDIT);
    }

private:
    void Send(Player* player, Position const& where, uint32 credit)
    {
        player->KnockbackFrom(me->GetPositionX(), me->GetPositionY(), 10.0f, 15.0f);
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid, where, credit]()
        {
            if (Player* flown = ObjectAccessor::FindPlayer(guid))
            {
                FlyTo(flown, where);
                flown->KilledMonsterCredit(Id(credit));
            }
        }, 2s);
    }
};

/*######
## Cluster Cluck (24671)
######*/

class spell_lost_isles_remote_control_fireworks : public SpellScript
{
    PrepareSpellScript(spell_lost_isles_remote_control_fireworks);

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        Creature* clucker = GetHitCreature();
        if (!OnQuest(player, QUEST_CLUSTER_CLUCK) || !clucker || clucker->GetEntry() != Id(NPC_WILD_CLUCKER) || !clucker->IsAlive())
            return;
        player->KilledMonsterCredit(Id(NPC_CLUSTER_CLUCK_CREDIT));
        clucker->SetReactState(REACT_PASSIVE);
        clucker->GetMotionMaster()->MoveFleeing(player, 8000);
        clucker->DespawnOrUnsummon(8s);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_lost_isles_remote_control_fireworks::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

/*######
## Irresistible Pool Pony (24864)
######*/

class spell_lost_isles_irresistible_pool_pony : public SpellScript
{
    PrepareSpellScript(spell_lost_isles_irresistible_pool_pony);

    void Lure()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!OnQuest(player, QUEST_IRRESISTIBLE_POOL_PONY))
            return;
        for (uint32 entry : { NPC_NAGA_HATCHLING, NPC_NAGA_HATCHLING_2, NPC_NAGA_HATCHLING_3, NPC_NAGA_HATCHLING_4 })
        {
            std::list<Creature*> hatchlings;
            player->GetCreatureListWithEntryInGrid(hatchlings, Id(entry), 25.0f);
            for (Creature* hatchling : hatchlings)
            {
                if (!hatchling->IsAlive() || hatchling->HasReactState(REACT_PASSIVE) || !OnQuest(player, QUEST_IRRESISTIBLE_POOL_PONY))
                    continue;
                player->KilledMonsterCredit(Id(NPC_NAGA_HATCHLING_CREDIT));
                hatchling->SetReactState(REACT_PASSIVE);
                hatchling->GetMotionMaster()->MoveFollow(player, 2.0f, float(rand_norm()) * 2.0f * float(M_PI));
                hatchling->DespawnOrUnsummon(20s);
            }
        }
    }

    void Register() override
    {
        AfterCast += SpellCastFn(spell_lost_isles_irresistible_pool_pony::Lure);
    }
};

/*######
## Surrender or Else! (24868)
######*/

struct npc_lost_isles_faceless : public ScriptedAI
{
    npc_lost_isles_faceless(Creature* creature) : ScriptedAI(creature) { }

    void MoveInLineOfSight(Unit* who) override
    {
        if (Player* player = who->ToPlayer())
            if (OnQuest(player, QUEST_SURRENDER_OR_ELSE) && me->IsWithinDistInMap(player, 30.0f) && me->HasUnitFlag(UNIT_FLAG_IMMUNE_TO_PC))
                me->RemoveUnitFlag(UNIT_FLAG_IMMUNE_TO_PC);
        ScriptedAI::MoveInLineOfSight(who);
    }

    void JustRespawned() override
    {
        me->SetUnitFlag(UNIT_FLAG_IMMUNE_TO_PC);
        ScriptedAI::JustRespawned();
    }
};

/*######
## Town-In-A-Box: Under Attack (24901)
######*/

struct npc_lost_isles_oomlot_warrior : public ScriptedAI
{
    npc_lost_isles_oomlot_warrior(Creature* creature) : ScriptedAI(creature) { }

    void JustDied(Unit* killer) override
    {
        // (the Eliminator's kill: its driver's; or its driver's own)
        Player* player = nullptr;
        if (killer && killer->IsCreature() && killer->GetEntry() == Id(NPC_BC_ELIMINATOR))
            player = killer->GetCharmerOrOwnerPlayerOrPlayerItself();
        else if (Player* driver = killer ? killer->ToPlayer() : nullptr)
            if (driver->GetVehicleBase() && driver->GetVehicleBase()->GetEntry() == Id(NPC_BC_ELIMINATOR))
                player = driver;
        if (OnQuest(player, QUEST_TOWN_UNDER_ATTACK))
            player->KilledMonsterCredit(Id(NPC_TOWN_UNDER_ATTACK_CREDIT));
    }
};

// The Eliminator's Fire Cannon: at the nearest Oomlot Warrior (Cataclysm aims it with an arc and a
// cursor, which a phone hasn't).
class spell_lost_isles_fire_cannon : public SpellScript
{
    PrepareSpellScript(spell_lost_isles_fire_cannon);

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        Unit* eliminator = GetCaster();
        if (Creature* warrior = eliminator->FindNearestCreature(Id(NPC_OOMLOT_WARRIOR), 60.0f, true))
        {
            eliminator->CastSpell(warrior, SpellId(SPELL_CANNON_BLAST), true);
            Unit::DealDamage(eliminator, warrior, warrior->CountPctFromMaxHealth(60));
        }
    }

    void Register() override
    {
        OnEffectHit += SpellEffectFn(spell_lost_isles_fire_cannon::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

/*######
## Zombies vs. Super Booster Rocket Boots (24942)
######*/

class spell_lost_isles_rocket_boots : public SpellScript
{
    PrepareSpellScript(spell_lost_isles_rocket_boots);

    void HandleScript(SpellEffIndex /*effIndex*/)
    {
        Player* player = GetCaster()->ToPlayer();
        if (!OnQuest(player, QUEST_ZOMBIES_VS_ROCKET_BOOTS))
            return;
        player->CastSpell(player, SpellId(SPELL_BOOTS_DAMAGE_AURA), true);
        player->CastSpell(player, SPELL_SPRINT, true);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_lost_isles_rocket_boots::HandleScript, EFFECT_0, SPELL_EFFECT_SCRIPT_EFFECT);
    }
};

// The boots' fire: a minute of it, the zombies within a few steps killed and counted.
class spell_lost_isles_rocket_boots_damage : public AuraScript
{
    PrepareAuraScript(spell_lost_isles_rocket_boots_damage);

    void HandleApply(AuraEffect const* /*aurEff*/, AuraEffectHandleModes /*mode*/)
    {
        GetAura()->SetDuration(60000);
        GetAura()->SetMaxDuration(60000);
    }

    void HandlePeriodic(AuraEffect const* /*aurEff*/)
    {
        PreventDefaultAction();
        Player* player = GetTarget()->ToPlayer();
        if (!OnQuest(player, QUEST_ZOMBIES_VS_ROCKET_BOOTS))
        {
            Remove();
            return;
        }
        for (uint32 entry : { NPC_GOBLIN_ZOMBIE, NPC_GOBLIN_ZOMBIE_2, NPC_GOBLIN_ZOMBIE_3, NPC_GOBLIN_ZOMBIE_4 })
        {
            std::list<Creature*> zombies;
            player->GetCreatureListWithEntryInGrid(zombies, Id(entry), 5.0f);
            for (Creature* zombie : zombies)
            {
                if (!zombie->IsAlive())
                    continue;
                Unit::Kill(player, zombie);
                player->KilledMonsterCredit(Id(NPC_ROCKET_BOOTS_CREDIT));
            }
        }
    }

    void Register() override
    {
        AfterEffectApply += AuraEffectApplyFn(spell_lost_isles_rocket_boots_damage::HandleApply, EFFECT_0, SPELL_AURA_PERIODIC_TRIGGER_SPELL, AURA_EFFECT_HANDLE_REAL);
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_lost_isles_rocket_boots_damage::HandlePeriodic, EFFECT_0, SPELL_AURA_PERIODIC_TRIGGER_SPELL);
    }
};

/*######
## Volcanoth! (24958)
######*/

struct npc_lost_isles_volcanoth : public ScriptedAI
{
    npc_lost_isles_volcanoth(Creature* creature) : ScriptedAI(creature) { }

    void SpellHit(Unit* caster, SpellInfo const* spell) override
    {
        if (spell->Id != SpellId(SPELL_BOOTZOOKA) || !me->IsAlive())
            return;
        uint32 damage = me->CountPctFromMaxHealth(20);
        Unit::DealDamage(caster, me, damage);
    }

    void JustDied(Unit* /*killer*/) override
    {
        for (MapReference const& ref : me->GetMap()->GetPlayers())
            if (Player* player = ref.GetSource())
                if (player->IsWithinDistInMap(me, 100.0f) && OnQuest(player, QUEST_VOLCANOTH))
                    player->KilledMonsterCredit(Id(NPC_VOLCANOTH_CREDIT));
    }
};

/*######
## Throw It On the Ground! (25123)
######*/

class spell_lost_isles_blastshadows_soulstone : public SpellScript
{
    PrepareSpellScript(spell_lost_isles_blastshadows_soulstone);

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        if (Player* player = GetCaster()->ToPlayer())
            if (OnQuest(player, QUEST_THROW_IT_ON_THE_GROUND))
                player->KilledMonsterCredit(Id(NPC_THROW_IT_ON_THE_GROUND_CREDIT));
    }

    void Register() override
    {
        OnEffectHit += SpellEffectFn(spell_lost_isles_blastshadows_soulstone::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

void AddWorgenGoblinLostIslesScripts()
{
    RegisterGameObjectAI(go_lost_isles_escape_pod);
    RegisterSpellScript(spell_lost_isles_nitro_potassium_bananas);
    RegisterCreatureAI(npc_lost_isles_foreman_dampwick);
    RegisterCreatureAI(npc_lost_isles_frightened_miner);
    RegisterSpellScript(spell_lost_isles_ktc_snapflash);
    RegisterCreatureAI(npc_lost_isles_thrall_below_deck);
    RegisterCreatureAI(npc_lost_isles_thrall_cyclone);
    RegisterCreatureAI(npc_lost_isles_cyclone);
    RegisterCreatureAI(npc_lost_isles_flight_giver);
    RegisterSpellScript(spell_lost_isles_remote_control_fireworks);
    RegisterSpellScript(spell_lost_isles_irresistible_pool_pony);
    RegisterCreatureAI(npc_lost_isles_faceless);
    RegisterCreatureAI(npc_lost_isles_oomlot_warrior);
    RegisterSpellScript(spell_lost_isles_fire_cannon);
    RegisterSpellScript(spell_lost_isles_rocket_boots);
    RegisterSpellScript(spell_lost_isles_rocket_boots_damage);
    RegisterCreatureAI(npc_lost_isles_volcanoth);
    RegisterSpellScript(spell_lost_isles_blastshadows_soulstone);
}
