// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The racials that need more than their rows in Spell.dbc (tools/build_data.py makes those):
 *
 *  Spatial Rift (void elves): the first use tears a rift up to 15 yards ahead (a Spatial Rift
 *  creature stands there for 6 seconds) and marks the player; used again while the rift stands,
 *  it takes the player to the rift. The 3 minute cooldown starts when the rift is used or closes
 *  (the spell itself has none, so the second use isn't blocked by the first).
 *
 *  Entropic Embrace (void elves), Arcane Pulse (nightborne), Embrace of Pa'ku (Zandalari) and
 *  Regeneratin' are plain spells: a proc with its rate in spell_proc, an area spell with its slow,
 *  a periodic heal; Pterrordax Swoop is Slow Fall with another name and cooldown.
 *
 *  Light's Judgment (Lightforged Draenei): three seconds after it's used, the player's strike
 *  falls where the target (or the player) stood, Holy damage to the enemies around it; the player
 *  casts it, so the kills, the loot and the experience are the player's.
 *
 *  Light's Reckoning (Lightforged Draenei): when the player dies, Holy energy bursts from the
 *  body (the player's own triggered cast, which the core allows the dead): Holy damage to enemies,
 *  healing to allies. Demonbane (+20% experience from demons) and City of Gold (+2% money looted)
 *  are the player script's.
 *
 *  Rescue the Survivors! (the void elves' and Lightforged Draenei's clones of it): the survivors'
 *  script answers Gift of the Naaru, a Draenei racial these races don't have, so they hold it
 *  (temporarily, never saved) while the quest is in their log, until it's handed in or abandoned.
 */

#include "Creature.h"
#include "LootMgr.h"
#include "ObjectAccessor.h"
#include "ObjectGuid.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellAuraEffects.h"
#include "SpellAuras.h"
#include "SpellScript.h"
#include "QuestDef.h"
#include "TemporarySummon.h"
#include <unordered_map>

namespace
{
    constexpr uint32 SPELL_SPATIAL_RIFT = 98711;
    constexpr uint32 SPELL_SPATIAL_RIFT_OPEN = 98712;          // the mark on the player while the rift stands
    constexpr uint32 NPC_SPATIAL_RIFT = 900101;
    constexpr uint32 RIFT_SECONDS = 6;
    constexpr float RIFT_REACH = 15.0f;
    constexpr uint32 RIFT_COOLDOWN = 3 * MINUTE * IN_MILLISECONDS;

    constexpr uint32 SPELL_LIGHTS_JUDGMENT_STRIKE = 98724;
    constexpr uint32 SPELL_LIGHTS_RECKONING = 98726;
    constexpr uint32 SPELL_LIGHTS_RECKONING_BURST = 98727;
    constexpr uint32 SPELL_DEMONBANE = 98729;
    constexpr uint32 SPELL_CITY_OF_GOLD = 98734;
    constexpr float JUDGMENT_REACH = 40.0f;
    constexpr uint32 JUDGMENT_DELAY = 3000;

    constexpr uint32 SPELL_GIFT_OF_THE_NAARU = 28880;
    constexpr uint32 QUEST_RESCUE_THE_SURVIVORS[] = { 959283, 969283 };   // tools/quests.py's clones of 9283

    bool IsRescueTheSurvivors(uint32 questId)
    {
        for (uint32 id : QUEST_RESCUE_THE_SURVIVORS)
            if (id == questId)
                return true;
        return false;
    }

    void LendGiftOfTheNaaru(Player* player)
    {
        if (!player->HasSpell(SPELL_GIFT_OF_THE_NAARU))
            player->learnSpell(SPELL_GIFT_OF_THE_NAARU, true);
    }

    void TakeBackGiftOfTheNaaru(Player* player)
    {
        if (player->getRace() != RACE_DRAENEI)
            player->removeSpell(SPELL_GIFT_OF_THE_NAARU, SPEC_MASK_ALL, true);
    }

    struct Rift
    {
        ObjectGuid creature;
        Position where;
    };
    std::unordered_map<ObjectGuid, Rift> rifts;        // by the player
}

class spell_allied_spatial_rift : public SpellScript
{
    PrepareSpellScript(spell_allied_spatial_rift);

    void HandleDummy(SpellEffIndex /*index*/)
    {
        Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        if (!player)
            return;
        auto it = rifts.find(player->GetGUID());
        if (it != rifts.end() && player->HasAura(SPELL_SPATIAL_RIFT_OPEN))
        {
            // Through the rift.
            Position where = it->second.where;
            player->NearTeleportTo(where.GetPositionX(), where.GetPositionY(), where.GetPositionZ(), player->GetOrientation());
            if (Creature* rift = ObjectAccessor::GetCreature(*player, it->second.creature))
                rift->DespawnOrUnsummon();
            rifts.erase(it);
            player->RemoveAurasDueToSpell(SPELL_SPATIAL_RIFT_OPEN);
            return;
        }
        // A rift ahead, as far as the ground allows.
        Position where = player->GetNearPosition(RIFT_REACH, 0.0f);
        player->UpdateAllowedPositionZ(where.GetPositionX(), where.GetPositionY(), where.m_positionZ);
        Rift rift;
        rift.where = where;
        if (Creature* summoned = player->SummonCreature(NPC_SPATIAL_RIFT, where, TEMPSUMMON_TIMED_DESPAWN, RIFT_SECONDS * IN_MILLISECONDS))
            rift.creature = summoned->GetGUID();
        rifts[player->GetGUID()] = rift;
        player->CastSpell(player, SPELL_SPATIAL_RIFT_OPEN, true);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_allied_spatial_rift::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

// The mark: when it goes (the rift used, or closed unused), the cooldown starts.
class spell_allied_spatial_rift_open : public AuraScript
{
    PrepareAuraScript(spell_allied_spatial_rift_open);

    void OnRemove(AuraEffect const* /*effect*/, AuraEffectHandleModes /*mode*/)
    {
        Player* player = GetTarget() ? GetTarget()->ToPlayer() : nullptr;
        if (!player)
            return;
        auto it = rifts.find(player->GetGUID());
        if (it != rifts.end())
        {
            if (Creature* rift = ObjectAccessor::GetCreature(*player, it->second.creature))
                rift->DespawnOrUnsummon();
            rifts.erase(it);
        }
        player->AddSpellCooldown(SPELL_SPATIAL_RIFT, 0, RIFT_COOLDOWN, true);
    }

    void Register() override
    {
        AfterEffectRemove += AuraEffectRemoveFn(spell_allied_spatial_rift_open::OnRemove, EFFECT_0, SPELL_AURA_DUMMY, AURA_EFFECT_HANDLE_REAL);
    }
};

// Light's Judgment: the strike falls where the target (or, with none in reach, the player) stands.
class spell_allied_lights_judgment : public SpellScript
{
    PrepareSpellScript(spell_allied_lights_judgment);

    void HandleDummy(SpellEffIndex /*index*/)
    {
        Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        if (!player)
            return;
        WorldObject* at = player;
        if (Unit* target = ObjectAccessor::GetUnit(*player, player->GetTarget()))
            if (target->IsAlive() && player->IsWithinDist(target, JUDGMENT_REACH) && player->IsHostileTo(target))
                at = target;
        float x = at->GetPositionX(), y = at->GetPositionY(), z = at->GetPositionZ();
        uint32 mapId = player->GetMapId();
        // The player's events go with the player, so this never runs for one who has logged out.
        player->m_Events.AddEventAtOffset([player, x, y, z, mapId]()
        {
            if (player->IsInWorld() && player->GetMapId() == mapId)
                player->CastSpell(x, y, z, SPELL_LIGHTS_JUDGMENT_STRIKE, true);
        }, Milliseconds(JUDGMENT_DELAY));
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_allied_lights_judgment::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

class AlliedRacesPlayer : public PlayerScript
{
public:
    AlliedRacesPlayer() : PlayerScript("AlliedRacesPlayer", { PLAYERHOOK_ON_PLAYER_JUST_DIED, PLAYERHOOK_ON_GIVE_EXP, PLAYERHOOK_ON_BEFORE_LOOT_MONEY,
        PLAYERHOOK_ON_PLAYER_QUEST_ACCEPT, PLAYERHOOK_ON_PLAYER_COMPLETE_QUEST, PLAYERHOOK_ON_QUEST_ABANDON, PLAYERHOOK_ON_LOGIN }) { }

    // Light's Reckoning: the burst where a Lightforged Draenei fell.
    void OnPlayerJustDied(Player* player) override
    {
        if (player->HasSpell(SPELL_LIGHTS_RECKONING))
            player->CastSpell(player, SPELL_LIGHTS_RECKONING_BURST, true);
    }

    // Gift of the Naaru, lent for Rescue the Survivors!.
    void OnPlayerQuestAccept(Player* player, Quest const* quest) override
    {
        if (IsRescueTheSurvivors(quest->GetQuestId()))
            LendGiftOfTheNaaru(player);
    }

    // (the core calls this as the quest is handed in)
    void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
    {
        if (IsRescueTheSurvivors(quest->GetQuestId()))
            TakeBackGiftOfTheNaaru(player);
    }

    void OnPlayerQuestAbandon(Player* player, uint32 questId) override
    {
        if (IsRescueTheSurvivors(questId))
            TakeBackGiftOfTheNaaru(player);
    }

    void OnPlayerLogin(Player* player) override
    {
        for (uint32 id : QUEST_RESCUE_THE_SURVIVORS)
            if (player->GetQuestStatus(id) == QUEST_STATUS_INCOMPLETE)
                LendGiftOfTheNaaru(player);
    }

    // Demonbane: 20% more experience from demons.
    void OnPlayerGiveXP(Player* player, uint32& amount, Unit* victim, uint8 /*xpSource*/) override
    {
        if (victim && victim->GetTypeId() == TYPEID_UNIT && victim->GetCreatureType() == CREATURE_TYPE_DEMON && player->HasSpell(SPELL_DEMONBANE))
            amount += amount / 5;
    }

    // City of Gold: 2% more money from what's looted.
    void OnPlayerBeforeLootMoney(Player* player, Loot* loot) override
    {
        if (loot && loot->gold && player->HasSpell(SPELL_CITY_OF_GOLD))
            loot->gold += loot->gold / 50;
    }
};

void AddAlliedRacesSpellScripts()
{
    new AlliedRacesPlayer();
    RegisterSpellScript(spell_allied_lights_judgment);
    RegisterSpellScript(spell_allied_spatial_rift);
    RegisterSpellScript(spell_allied_spatial_rift_open);
}
