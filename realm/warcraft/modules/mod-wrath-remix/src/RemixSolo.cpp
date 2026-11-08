// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix's dungeons and raids for however many are there (WrathRemix.Solo.*): a Timerunner on
 * their own, or with a bot or two, can play them through without it being a different game.
 *
 * An instance's share of a full group is its players (the realm's bots count) over the players it
 * is made for. Below a full group, its creatures' blows land softer (the share's 0.6th power, never
 * below WrathRemix.Solo.DungeonDamage or .RaidDamage percent of a full group's) and the players'
 * land harder (the share's -0.85th power, at most WrathRemix.Solo.MaxBoost times): one player in a
 * five-player dungeon takes about two fifths of the damage and deals about four times as much. The
 * creatures' health is as it was, so every script that watches it (a boss's phases) still sees its
 * own numbers. Heals the players give the instance's friendly people (Valithria Dreamwalker) go as
 * far as their blows do.
 *
 * Icecrown Citadel, where the story ends, has a few things only a group can do; with less than a
 * third of a group there:
 * - Blood-Queen Lana'thel's Frenzied Bloodthirst passes without making the bitten one hers (it asks
 *   them to bite someone else, and there is no one);
 * - Sindragosa's Ice Tombs break by themselves after a while (no one is there to break them);
 * - Valithria Dreamwalker, while her fight is on, mends a little by herself every second (not every
 *   class can heal her).
 */

#include "WrathRemix.h"
#include "Creature.h"
#include "Map.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "StringFormat.h"
#include <cmath>
#include <mutex>
#include <unordered_map>

using namespace WrathRemix;

namespace
{
    constexpr uint32 MAP_REMIX_ICC = 631;
    constexpr uint32 NPC_ICE_TOMB = 36980;
    constexpr uint32 NPC_VALITHRIA_DREAMWALKER = 36789;
    // Frenzied Bloodthirst (each difficulty's), and Uncontrollable Frenzy should one land anyway.
    constexpr uint32 BLOOD_QUEEN_ASKS[] = { 70877, 71474, 72151, 72648, 72649, 72650, 70923, 70924, 73015 };
    constexpr float FEW = 0.34f;  // less than a third of a group

    // How much of a full group is in [map]: 1 outside dungeons and raids.
    float GroupShare(Map* map)
    {
        if (!map || !map->IsDungeon() || map->IsBattlegroundOrArena())
            return 1.0f;
        InstanceMap* instance = map->ToInstanceMap();
        uint32 made = instance ? instance->GetMaxPlayers() : 0;
        if (!made)
            return 1.0f;
        uint32 here = std::max<uint32>(1, map->GetPlayersCountExceptGMs());
        return std::min(1.0f, float(here) / float(made));
    }

    template<typename T>
    void ScaleForGroup(T& amount, Unit* target, Unit* attacker)
    {
        if (!SoloActive() || !amount || !target || !attacker)
            return;
        Map* map = attacker->GetMap();
        float share = GroupShare(map);
        if (share >= 1.0f)
            return;
        bool playerSide = attacker->IsControlledByPlayer();
        if (playerSide && !target->IsControlledByPlayer() && target->IsCreature())
            amount = T(std::lround(amount * std::min(SoloMaxBoost(), std::pow(share, -0.85f))));
        else if (!playerSide && target->IsControlledByPlayer())
        {
            float floor = map->IsRaid() ? SoloRaidDamage() : SoloDungeonDamage();
            amount = T(std::max<double>(1.0, std::round(amount * std::max(floor, std::pow(share, 0.6f)))));
        }
    }

    bool FewInIcecrown(Map* map)
    {
        return SoloActive() && map && map->GetId() == MAP_REMIX_ICC && GroupShare(map) < FEW;
    }

    thread_local HealTick healTick;     // (this script's: see HealUnits)
}

std::string WrathRemix::SoloReport(Player* player)
{
    Map* map = player->GetMap();
    float share = GroupShare(map);
    InstanceMap* instance = map->ToInstanceMap();
    float theirs = 1.0f, yours = 1.0f;
    if (SoloActive() && share < 1.0f)
    {
        theirs = std::max(map->IsRaid() ? SoloRaidDamage() : SoloDungeonDamage(), std::pow(share, 0.6f));
        yours = std::min(SoloMaxBoost(), std::pow(share, -0.85f));
    }
    return Acore::StringFormat("Wrath Remix solo: map {} ({}), {} of {} players, share {:.2f}, their damage x{:.2f}, yours x{:.2f}, few in Icecrown: {}.",
        map->GetId(), map->IsRaid() ? "raid" : (map->IsDungeon() ? "dungeon" : "world"),
        map->GetPlayersCountExceptGMs(), instance ? instance->GetMaxPlayers() : 0, share, theirs, yours,
        FewInIcecrown(map) ? "yes" : "no");
}

class WrathRemixSolo : public UnitScript
{
public:
    WrathRemixSolo() : UnitScript("WrathRemixSolo", true, {
        UNITHOOK_MODIFY_SPELL_DAMAGE_TAKEN,
        UNITHOOK_MODIFY_PERIODIC_DAMAGE_AURAS_TICK,
        UNITHOOK_MODIFY_MELEE_DAMAGE,
        UNITHOOK_MODIFY_HEAL_RECEIVED,
        UNITHOOK_ON_AURA_APPLY,
    }) { }

    void ModifySpellDamageTaken(Unit* target, Unit* attacker, int32& damage, SpellInfo const* /*spellInfo*/) override
    {
        if (damage > 0)
            ScaleForGroup(damage, target, attacker);
    }

    // (a heal over time's tick comes this way first: the heal hook's, once)
    void ModifyPeriodicDamageAurasTick(Unit* target, Unit* attacker, uint32& damage, SpellInfo const* spellInfo) override
    {
        if (!MarkHealTick(healTick, target, attacker, damage, spellInfo))
            ScaleForGroup(damage, target, attacker);
    }

    void ModifyMeleeDamage(Unit* target, Unit* attacker, uint32& damage) override
    {
        ScaleForGroup(damage, target, attacker);
    }

    // a player's heal on one of the instance's own (friendly) people, as far as their blows go
    void ModifyHealReceived(Unit* target, Unit* healer, uint32& heal, SpellInfo const* /*spellInfo*/) override
    {
        HealUnits(healTick, target, healer, heal);
        if (!SoloActive() || !heal || !target || !healer || !healer->IsControlledByPlayer() || target->IsControlledByPlayer() || !target->IsCreature())
            return;
        float share = GroupShare(target->GetMap());
        if (share < 1.0f)
            heal = uint32(std::lround(heal * std::min(SoloMaxBoost(), std::pow(share, -0.85f))));
    }

    void OnAuraApply(Unit* unit, Aura* aura) override
    {
        if (!unit || !aura || !unit->IsPlayer() || !FewInIcecrown(unit->GetMap()))
            return;
        uint32 spell = aura->GetId();
        for (uint32 asked : BLOOD_QUEEN_ASKS)
            if (spell == asked)
            {
                // (a moment on, not while it's being put on; taken off, not run out: no frenzy follows)
                unit->m_Events.AddEventAtOffset([unit, spell]() { unit->RemoveAurasDueToSpell(spell); }, 1s);
                return;
            }
    }
};

class WrathRemixSoloCreatures : public AllCreatureScript
{
public:
    WrathRemixSoloCreatures() : AllCreatureScript("WrathRemixSoloCreatures") { }

    void OnCreatureAddWorld(Creature* creature) override
    {
        if (!creature || creature->GetEntry() != NPC_ICE_TOMB || !FewInIcecrown(creature->GetMap()))
            return;
        // the tomb breaks by itself after a while
        creature->m_Events.AddEventAtOffset([creature]()
        {
            if (creature->IsAlive())
                Unit::Kill(creature, creature);
        }, 12s);
    }

    void OnAllCreatureUpdate(Creature* creature, uint32 diff) override
    {
        if (creature->GetEntry() != NPC_VALITHRIA_DREAMWALKER || !creature->IsAlive() || !creature->IsInCombat() || !FewInIcecrown(creature->GetMap()))
            return;
        // (each Valithria her own second: the maps update on several threads)
        {
            std::lock_guard<std::mutex> lock(mendersLock);
            uint32& since = menders[creature->GetGUID()];
            since += diff;
            if (since < 1000)
                return;
            since = 0;
        }
        if (creature->GetHealth() < creature->GetMaxHealth())
            creature->ModifyHealth(int32(creature->CountPctFromMaxHealth(1)));
    }

private:
    std::mutex mendersLock;
    std::unordered_map<ObjectGuid, uint32> menders;
};

void AddRemixSoloScripts()
{
    new WrathRemixSolo();
    new WrathRemixSoloCreatures();
}
