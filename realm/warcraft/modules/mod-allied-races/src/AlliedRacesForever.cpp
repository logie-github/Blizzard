// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * WoW: Forever's racials for the eight races of 1.x that need more than their rows in Spell.dbc
 * (tools/build_data.py makes those; the realm with AlliedRaces.Enable has them, ChromieCraft's):
 *
 *  Blood Fury (orcs): its Spell Power part, 10% of the orc's Spell Power as it's used (3.3.5 has no
 *  aura for a share of Spell Power).
 *
 *  Shadowmeld (night elves): 10 sec cooldown, 2 min when used in combat.
 *
 *  Touch of the Grave (undead): a hit that procs it drains Health from the target, as much as the hit
 *  did and 5% of the undead's maximum Health at most.
 *
 *  Cultivation (tauren): the herb within 10 yards, harvested for the tauren (its loot, as a herbalist
 *  gets it, into the bags) without Herbalism; each herb once, and a herb's skill needs a level of a
 *  fifth of it (Forever's rule; 80 at most).
 *
 *  Plainsrunning (tauren): a stack of 1% movement speed for every 5 sec spent moving (30 at most);
 *  each second standing still takes one, taking damage six.
 *
 *  Contingency Plan (gnome priests): the ward shields and heals its ally the first time damage leaves
 *  them below 35% Health. The gnome priest's two spells, Confounding Flash (level 10) and Contingency
 *  Plan (a rank at 20, 30, 40, 50 and 60), are taught as the levels come, as Forever's quests teach
 *  them.
 *
 * Engineering Specialization keeps its text alone: 3.3.5's engineering devices fail by their own
 * scripts' rolls, which a racial can't reach.
 */

#include "CellImpl.h"
#include "Config.h"
#include "DBCStores.h"
#include "GameObject.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "LootMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellScript.h"
#include <algorithm>
#include <unordered_set>

namespace
{
    constexpr uint32 SPELL_SHADOWMELD = 58984;
    constexpr uint32 SHADOWMELD_COMBAT_COOLDOWN = 2 * MINUTE * IN_MILLISECONDS;
    constexpr uint32 SPELL_GRAVE_DRAIN = 98813;
    constexpr uint32 SPELL_PLAINSRUNNING_SPEED = 98816;
    constexpr uint32 PLAINSRUNNING_STACKS = 30;
    constexpr uint32 PLAINSRUNNING_MOVING_SECONDS = 5;
    constexpr uint32 PLAINSRUNNING_HIT_STACKS = 6;
    constexpr uint32 SPELL_CONFOUNDING_FLASH = 98826;
    constexpr uint8 CONFOUNDING_FLASH_LEVEL = 10;
    constexpr uint32 CONTINGENCY_WARD[] = { 98827, 98828, 98829, 98830, 98831 };
    constexpr uint32 CONTINGENCY_SHIELD[] = { 98832, 98833, 98834, 98835, 98836 };
    constexpr uint32 CONTINGENCY_HEAL[] = { 98837, 98838, 98839, 98840, 98841 };
    constexpr uint8 CONTINGENCY_LEVEL[] = { 20, 30, 40, 50, 60 };
    constexpr float CONTINGENCY_BELOW_PCT = 35.0f;
    constexpr float CULTIVATION_REACH = 10.0f;

    std::unordered_set<ObjectGuid> cultivated;     // the herbs cultivated (each once)

    bool Enabled()
    {
        return sConfigMgr->GetOption<bool>("AlliedRaces.Enable", true);
    }

    // A herb a herbalist gathers (a chest whose lock wants Herbalism), and the skill it wants.
    bool IsHerb(GameObject const* go, uint32& skill)
    {
        if (go->GetGoType() != GAMEOBJECT_TYPE_CHEST)
            return false;
        LockEntry const* lock = sLockStore.LookupEntry(go->GetGOInfo()->GetLockId());
        if (!lock)
            return false;
        for (uint8 i = 0; i < MAX_LOCK_CASE; ++i)
            if (lock->Type[i] == LOCK_KEY_SKILL && lock->Index[i] == LOCKTYPE_HERBALISM)
            {
                skill = lock->Skill[i];
                return true;
            }
        return false;
    }

    class NearestHerbCheck
    {
    public:
        NearestHerbCheck(WorldObject const& from, float range) : _from(from), _range(range) { }

        bool operator()(GameObject* go)
        {
            uint32 skill = 0;
            if (!go->isSpawned() || !IsHerb(go, skill) || !_from.IsWithinDistInMap(go, _range))
                return false;
            _range = _from.GetDistance(go);
            return true;
        }

    private:
        WorldObject const& _from;
        float _range;
    };

    GameObject* NearestHerb(Player* player)
    {
        GameObject* herb = nullptr;
        NearestHerbCheck check(*player, CULTIVATION_REACH);
        Acore::GameObjectLastSearcher<NearestHerbCheck> searcher(player, herb, check);
        Cell::VisitObjects(player, searcher, CULTIVATION_REACH);
        return herb;
    }

    // The gnome priest's own spells, as their levels come (and no one else's).
    void TeachGnomePriestSpells(Player* player)
    {
        bool gnomePriest = Enabled() && player->getRace() == RACE_GNOME && player->getClass() == CLASS_PRIEST;
        uint8 level = player->GetLevel();
        if (gnomePriest && level >= CONFOUNDING_FLASH_LEVEL)
        {
            if (!player->HasSpell(SPELL_CONFOUNDING_FLASH))
                player->learnSpell(SPELL_CONFOUNDING_FLASH);
        }
        else if (player->HasSpell(SPELL_CONFOUNDING_FLASH))
            player->removeSpell(SPELL_CONFOUNDING_FLASH, SPEC_MASK_ALL, false);

        int best = -1;
        if (gnomePriest)
            for (int rank = 0; rank < 5; ++rank)
                if (level >= CONTINGENCY_LEVEL[rank])
                    best = rank;
        for (int rank = 0; rank < 5; ++rank)
        {
            if (rank == best)
            {
                if (!player->HasSpell(CONTINGENCY_WARD[rank]))
                    player->learnSpell(CONTINGENCY_WARD[rank]);
            }
            else if (player->HasSpell(CONTINGENCY_WARD[rank]))
                player->removeSpell(CONTINGENCY_WARD[rank], SPEC_MASK_ALL, false);
        }
    }
}

// Blood Fury's Spell Power: 10% of the orc's own as it's used.
class spell_forever_blood_fury : public AuraScript
{
    PrepareAuraScript(spell_forever_blood_fury);

    void CalcDamage(AuraEffect const* /*effect*/, int32& amount, bool& /*canBeRecalculated*/)
    {
        if (Unit* caster = GetCaster())
            amount = caster->SpellBaseDamageBonusDone(SPELL_SCHOOL_MASK_MAGIC) / 10;
    }

    void CalcHealing(AuraEffect const* /*effect*/, int32& amount, bool& /*canBeRecalculated*/)
    {
        if (Unit* caster = GetCaster())
            amount = caster->SpellBaseHealingBonusDone(SPELL_SCHOOL_MASK_ALL) / 10;
    }

    void Register() override
    {
        DoEffectCalcAmount += AuraEffectCalcAmountFn(spell_forever_blood_fury::CalcDamage, EFFECT_0, SPELL_AURA_MOD_DAMAGE_DONE);
        DoEffectCalcAmount += AuraEffectCalcAmountFn(spell_forever_blood_fury::CalcHealing, EFFECT_1, SPELL_AURA_MOD_HEALING_DONE);
    }
};

// Shadowmeld: in combat, a 2 minute cooldown in place of 10 sec.
class spell_forever_shadowmeld : public SpellScript
{
    PrepareSpellScript(spell_forever_shadowmeld);

    void BeforeShadowmeld()
    {
        _inCombat = GetCaster() && GetCaster()->IsInCombat();
    }

    void AfterShadowmeld()
    {
        Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        if (!player || !_inCombat)
            return;
        player->RemoveSpellCooldown(SPELL_SHADOWMELD);
        player->AddSpellCooldown(SPELL_SHADOWMELD, 0, SHADOWMELD_COMBAT_COOLDOWN, true);
    }

    void Register() override
    {
        BeforeCast += SpellCastFn(spell_forever_shadowmeld::BeforeShadowmeld);
        AfterCast += SpellCastFn(spell_forever_shadowmeld::AfterShadowmeld);
    }

private:
    bool _inCombat = false;
};

// Touch of the Grave: the hit drains as much as it did, 5% of maximum Health at most.
class spell_forever_touch_of_the_grave : public AuraScript
{
    PrepareAuraScript(spell_forever_touch_of_the_grave);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        DamageInfo* damage = eventInfo.GetDamageInfo();
        if (!damage || !damage->GetDamage() || !eventInfo.GetProcTarget() || !eventInfo.GetProcTarget()->IsAlive())
            return false;
        SpellInfo const* spell = damage->GetSpellInfo();
        return !spell || spell->Id != SPELL_GRAVE_DRAIN;
    }

    void HandleProc(AuraEffect const* effect, ProcEventInfo& eventInfo)
    {
        Unit* undead = GetTarget();
        Unit* victim = eventInfo.GetProcTarget();
        int32 cap = int32(undead->CountPctFromMaxHealth(effect->GetAmount()));
        int32 drain = std::min<int32>(int32(eventInfo.GetDamageInfo()->GetDamage()), cap);
        if (drain > 0)
            undead->CastCustomSpell(victim, SPELL_GRAVE_DRAIN, &drain, nullptr, nullptr, true, nullptr, effect);
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_forever_touch_of_the_grave::CheckProc);
        OnEffectProc += AuraEffectProcFn(spell_forever_touch_of_the_grave::HandleProc, EFFECT_0, SPELL_AURA_DUMMY);
    }
};

// Cultivation: the nearest herb harvested for the tauren, once.
class spell_forever_cultivation : public SpellScript
{
    PrepareSpellScript(spell_forever_cultivation);

    SpellCastResult CheckHerb()
    {
        Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        if (!player)
            return SPELL_FAILED_ERROR;
        GameObject* herb = NearestHerb(player);
        if (!herb || cultivated.count(herb->GetGUID()))
            return SPELL_FAILED_REQUIRES_SPELL_FOCUS;
        uint32 skill = 0;
        IsHerb(herb, skill);
        if (player->GetLevel() < std::min<uint32>(skill / 5, DEFAULT_MAX_LEVEL))
            return SPELL_FAILED_LOW_CASTLEVEL;
        return SPELL_CAST_OK;
    }

    void HandleDummy(SpellEffIndex /*index*/)
    {
        Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        if (!player)
            return;
        GameObject* herb = NearestHerb(player);
        if (!herb || !cultivated.insert(herb->GetGUID()).second)
            return;
        Loot loot;
        loot.FillLoot(herb->GetGOInfo()->GetLootId(), LootTemplates_Gameobject, player, true, true, LOOT_MODE_DEFAULT, herb);
        for (LootItem const& item : loot.items)
            player->AddItem(item.itemid, item.count);
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_forever_cultivation::CheckHerb);
        OnEffectHitTarget += SpellEffectFn(spell_forever_cultivation::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// Plainsrunning: speed that builds while running, and goes standing still or hit.
class spell_forever_plainsrunning : public AuraScript
{
    PrepareAuraScript(spell_forever_plainsrunning);

    void Stacks(int32 change)
    {
        Unit* tauren = GetTarget();
        Aura* speed = tauren->GetAura(SPELL_PLAINSRUNNING_SPEED);
        int32 now = speed ? speed->GetStackAmount() : 0;
        int32 next = std::clamp<int32>(now + change, 0, PLAINSRUNNING_STACKS);
        if (next == now)
            return;
        if (!next)
        {
            tauren->RemoveAurasDueToSpell(SPELL_PLAINSRUNNING_SPEED);
            return;
        }
        if (!speed)
            speed = tauren->AddAura(SPELL_PLAINSRUNNING_SPEED, tauren);
        if (speed)
            speed->SetStackAmount(uint8(next));
    }

    void Tick(AuraEffect const* /*effect*/)
    {
        Unit* tauren = GetTarget();
        if (tauren->isMoving() && !tauren->IsMounted())
        {
            if (++_moving >= PLAINSRUNNING_MOVING_SECONDS)
            {
                _moving = 0;
                Stacks(1);
            }
        }
        else
        {
            _moving = 0;
            if (!tauren->IsMounted())
                Stacks(-1);
        }
    }

    bool CheckHit(ProcEventInfo& eventInfo)
    {
        return eventInfo.GetDamageInfo() && eventInfo.GetDamageInfo()->GetDamage();
    }

    void Hit(AuraEffect const* /*effect*/, ProcEventInfo& /*eventInfo*/)
    {
        Stacks(-int32(PLAINSRUNNING_HIT_STACKS));
    }

    void Register() override
    {
        OnEffectPeriodic += AuraEffectPeriodicFn(spell_forever_plainsrunning::Tick, EFFECT_0, SPELL_AURA_PERIODIC_DUMMY);
        DoCheckProc += AuraCheckProcFn(spell_forever_plainsrunning::CheckHit);
        OnEffectProc += AuraEffectProcFn(spell_forever_plainsrunning::Hit, EFFECT_1, SPELL_AURA_DUMMY);
    }

private:
    uint32 _moving = 0;
};

// Contingency Plan: the ward's shield and healing when damage leaves its ally below 35% Health.
class spell_forever_contingency_plan : public AuraScript
{
    PrepareAuraScript(spell_forever_contingency_plan);

    bool CheckProc(ProcEventInfo& eventInfo)
    {
        Unit* ally = GetTarget();
        return eventInfo.GetDamageInfo() && eventInfo.GetDamageInfo()->GetDamage() && ally->IsAlive()
            && ally->HealthBelowPct(int32(CONTINGENCY_BELOW_PCT));
    }

    void HandleProc(AuraEffect const* effect, ProcEventInfo& /*eventInfo*/)
    {
        Unit* ally = GetTarget();
        uint32 id = GetSpellInfo()->Id;
        for (int rank = 0; rank < 5; ++rank)
            if (CONTINGENCY_WARD[rank] == id)
            {
                Unit* priest = GetCaster() ? GetCaster() : ally;
                priest->CastSpell(ally, CONTINGENCY_SHIELD[rank], true, nullptr, effect);
                priest->CastSpell(ally, CONTINGENCY_HEAL[rank], true, nullptr, effect);
            }
        Remove();
    }

    void Register() override
    {
        DoCheckProc += AuraCheckProcFn(spell_forever_contingency_plan::CheckProc);
        OnEffectProc += AuraEffectProcFn(spell_forever_contingency_plan::HandleProc, EFFECT_0, SPELL_AURA_DUMMY);
    }
};

class AlliedRacesForeverPlayer : public PlayerScript
{
public:
    AlliedRacesForeverPlayer() : PlayerScript("AlliedRacesForeverPlayer", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LEVEL_CHANGED }) { }

    void OnPlayerLogin(Player* player) override
    {
        TeachGnomePriestSpells(player);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        TeachGnomePriestSpells(player);
    }
};

void AddAlliedRacesForeverScripts()
{
    new AlliedRacesForeverPlayer();
    RegisterSpellScript(spell_forever_blood_fury);
    RegisterSpellScript(spell_forever_shadowmeld);
    RegisterSpellScript(spell_forever_touch_of_the_grave);
    RegisterSpellScript(spell_forever_cultivation);
    RegisterSpellScript(spell_forever_plainsrunning);
    RegisterSpellScript(spell_forever_contingency_plan);
}
