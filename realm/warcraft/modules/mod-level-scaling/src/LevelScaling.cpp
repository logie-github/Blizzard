// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Level scaling (mod-level-scaling), ChromieCraft's realm, as Ascension WoW has it (the user: "bring
 * in ascension wow's level scaling"), at the user's choices: "Make it so you can talk to your class
 * trainer and turn on or off scaling. Off by default"; "+-2 your level at all times. Dynamically not
 * set"; and the dungeons and raids for however many are there, as Wrath Remix's.
 *
 *  - Each character's own choice, off until they turn it on: their class trainer has "Turn level
 *    scaling on" (and off again) in their gossip. Kept with the character (character_settings).
 *  - With it on, every creature near them they could fight (hostile or neutral: not anyone's pet,
 *    guardian, totem or companion, not a town's people, a civilian, a critter or an unseen trigger)
 *    is within LevelScaling.Range (2) levels of theirs, above or below, out in the world and in
 *    dungeons and raids (bosses at the top of it): taken as it appears, and again within 100 yards of
 *    them as they level (one in a fight keeps its level to the end). Out in the world a creature
 *    follows the real player nearest it; in a dungeon or raid, the highest of those with it on. Near
 *    no one with it on (the realm's bots load the world around them too), creatures are their own
 *    level, and one brought to a level goes back to its own. Its health, mana, armour and melee are
 *    its new level's (Creature::SelectLevel); its spells, made for its own level, hit and heal for
 *    the new one's (creature_classlevelstats' damage at each).
 *  - With it on, a quest below their level gives the experience of one at their level
 *    (LevelScaling.QuestExperience), as Ascension's quests are at yours.
 *  - Battlegrounds and arenas, and the crews of ships and zeppelins, are as they are.
 *
 * The dungeons and raids for however many are there (LevelScaling.Solo.*, every character): an
 * instance's share of a full group is its players (the realm's bots count) over the players it's made
 * for. Below a full group its creatures' blows land softer (the share's 0.6th power, never below
 * Solo.DungeonDamage or .RaidDamage percent of a full group's) and the players' harder (the share's
 * -0.85th power, at most Solo.MaxBoost times): one player in a five-player dungeon takes about two
 * fifths of the damage and deals about four times as much. The creatures' health is as it was, so a
 * boss's phases still happen. Heals the players give the instance's friendly people go as far as their
 * blows. In Icecrown Citadel with less than a third of a group, the three things only a group can do
 * are done for them (Blood-Queen Lana'thel's bite passes, Sindragosa's Ice Tombs break by themselves,
 * Valithria Dreamwalker mends a little every second). Wrath Remix's own (mod-wrath-remix, RemixSolo.cpp).
 */

#include "CellImpl.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "TemporarySummon.h"
#include "Trainer.h"
#include "WorldSession.h"
#include <algorithm>
#include <cmath>
#include <mutex>
#include <unordered_map>
#include <unordered_set>

namespace
{
    bool enabled = false;
    uint32 range = 2;
    bool questExperience = true;
    bool solo = true;
    float soloDungeonDamage = 0.35f, soloRaidDamage = 0.15f, soloMaxBoost = 15.0f;

    constexpr char const* SETTING = "mod-level-scaling";
    constexpr uint32 GOSSIP_SENDER_SCALING = 0x4C53;     // ("LS": the trainers' option, apart from their own)
    constexpr float REACH = 100.0f;                     // the level pass's reach around each real player
    constexpr uint8 TOP_LEVEL = 83;                     // (the highest creature_classlevelstats has)

    thread_local uint8 forcedLevel = 0;                 // set while the level pass brings a creature to a level

    // The creatures brought to a scaling player's level (to take back to their own when no one with it
    // on is near). The maps update on several threads.
    std::mutex scaledLock;
    std::unordered_set<ObjectGuid> scaled;

    void MarkScaled(Creature* creature, bool on)
    {
        std::lock_guard<std::mutex> lock(scaledLock);
        if (on)
            scaled.insert(creature->GetGUID());
        else
            scaled.erase(creature->GetGUID());
    }

    bool IsScaled(Creature* creature)
    {
        std::lock_guard<std::mutex> lock(scaledLock);
        return scaled.count(creature->GetGUID()) > 0;
    }

    bool AnyScaled()
    {
        std::lock_guard<std::mutex> lock(scaledLock);
        return !scaled.empty();
    }

    // One of the realm's bots (mod-playerbots' sessions have no client).
    bool IsBot(Player* player)
    {
        return !player->GetSession() || player->GetSession()->GetRemoteAddress() == "headless";
    }

    bool ScalingOn(Player* player)
    {
        return enabled && player && !IsBot(player) && player->GetPlayerSetting(SETTING, 0).value == 1;
    }

    bool Scales(Map* map)
    {
        return enabled && map && !map->IsBattlegroundOrArena();
    }

    // The real player whose level a creature takes: in a dungeon or raid the highest of those with
    // scaling on; out in the world the nearest real player within [reach] (nullptr when that one has
    // it off). Never a bot.
    Player* Followed(WorldObject* object, Map* map, float reach)
    {
        Player* found = nullptr;
        if (map->IsDungeon())
        {
            for (MapReference const& ref : map->GetPlayers())
                if (Player* player = ref.GetSource(); ScalingOn(player) && (!found || player->GetLevel() > found->GetLevel()))
                    found = player;
            return found;
        }
        float nearest = reach;
        for (MapReference const& ref : map->GetPlayers())
        {
            Player* player = ref.GetSource();
            if (!player || IsBot(player))
                continue;
            if (float distance = object->GetExactDist2d(player); distance < nearest)
            {
                nearest = distance;
                found = player;
            }
        }
        return ScalingOn(found) ? found : nullptr;
    }

    // Whether a creature takes [player]'s level: one they could fight, hostile or neutral to them.
    bool Follows(Creature* creature, CreatureTemplate const* info, Player* player)
    {
        if (creature->IsPet() || creature->IsTotem() || creature->IsTrigger() || creature->IsCivilian() || info->type == CREATURE_TYPE_CRITTER)
            return false;
        if (creature->HasUnitTypeMask(UNIT_MASK_MINION) || creature->GetCharmerOrOwnerGUID() || creature->IsControlledByPlayer())
            return false;
        if (creature->GetNpcFlags() & ~UNIT_NPC_FLAG_SPELLCLICK)
            return false;
        if (creature->GetTransport())
            return false;
        return !creature->IsFriendlyTo(player);
    }

    // The levels a creature may have under [player]: within the range of theirs, a boss at its top.
    void FollowRange(Creature* creature, CreatureTemplate const* info, Player* player, uint32& from, uint32& to)
    {
        uint32 level = player->GetLevel();
        from = std::clamp<uint32>(level > range ? level - range : 1, 1, TOP_LEVEL);
        to = std::clamp<uint32>(level + range, 1, TOP_LEVEL);
        if (creature->IsDungeonBoss() || info->rank == CREATURE_ELITE_WORLDBOSS)
            from = to;
    }

    // A creature in the world brought to another level ([level]; 0: its own roll): the health, mana,
    // armour and damage of it, as Creature::SelectLevel gives them; at full health, as it was.
    void Relevel(Creature* creature, uint8 level)
    {
        forcedLevel = level;
        creature->SelectLevel();
        forcedLevel = 0;
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        if (CreatureBaseStats const* stats = sObjectMgr->GetCreatureBaseStats(creature->GetLevel(), info->unit_class))
            creature->SetStatFlatModifier(UNIT_MOD_ARMOR, BASE_VALUE, stats->GenerateArmor(info));
        creature->UpdateAllStats();
        creature->SetFullHealth();
        MarkScaled(creature, level != 0);
    }

    // The level pass's candidates around a real player: alive, out of combat and whole, nobody's, and
    // not a player's summons.
    struct LevelCandidates
    {
        LevelCandidates(WorldObject const* source, float reach) : _source(source), _reach(reach) { }
        bool operator()(Creature* creature) const
        {
            if (!creature->IsAlive() || creature->IsInCombat() || creature->IsInEvadeMode() || creature->IsPet() ||
                creature->HasUnitTypeMask(UNIT_MASK_MINION) || creature->GetCharmerOrOwnerGUID() || creature->IsControlledByPlayer())
                return false;
            if (creature->GetHealth() != creature->GetMaxHealth())
                return false;
            if (TempSummon const* summon = creature->ToTempSummon(); summon && summon->GetSummonerGUID().IsPlayer())
                return false;
            return _source->IsWithinDistInMap(creature, _reach);
        }
        WorldObject const* _source;
        float _reach;
    };

    // Every second and a half for each real player: the creatures within 100 yards brought into the
    // range of the player they follow, or back to their own level where no one with scaling on is.
    void LevelPass(Player* player)
    {
        Map* map = player->GetMap();
        if (!Scales(map) || (!ScalingOn(player) && !AnyScaled()))
            return;
        std::list<Creature*> creatures;
        LevelCandidates check(player, REACH);
        Acore::CreatureListSearcher<LevelCandidates> searcher(player, creatures, check);
        Cell::VisitObjects(player, searcher, REACH);
        for (Creature* creature : creatures)
        {
            CreatureTemplate const* info = creature->GetCreatureTemplate();
            if (!info)
                continue;
            Player* followed = Followed(creature, map, REACH * 2.0f);
            if (followed && Follows(creature, info, followed))
            {
                uint32 from, to;
                FollowRange(creature, info, followed, from, to);
                if (creature->GetLevel() < from || creature->GetLevel() > to)
                    Relevel(creature, uint8(urand(from, to)));
            }
            else if (IsScaled(creature))
                Relevel(creature, 0);
        }
    }

    void LevelPassSoon(Player* player)
    {
        player->m_Events.AddEventAtOffset([player]()
        {
            // (not on a flight: what's flown over is brought to them as they land near it)
            if (enabled && player->IsInWorld() && !player->IsBeingTeleported() && !player->IsInFlight())
                LevelPass(player);
            LevelPassSoon(player);
        }, 1500ms);
    }

    // A scaled creature's or its totem's or guardian's (never a player's): its level isn't its own.
    Creature* ScaledSource(Unit* unit)
    {
        if (!enabled || !unit)
            return nullptr;
        if (Unit* owner = unit->GetOwner())
        {
            if (owner->IsPlayer())
                return nullptr;
            unit = owner;
        }
        Creature* creature = unit->ToCreature();
        if (!creature || creature->IsPet() || creature->IsControlledByPlayer())
            return nullptr;
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        if (!info)
            return nullptr;
        uint8 level = creature->GetLevel();
        if (level >= std::min(info->minlevel, info->maxlevel) && level <= std::max(info->minlevel, info->maxlevel))
            return nullptr;
        return IsScaled(creature) ? creature : nullptr;
    }

    // How much of its spells' power a scaled creature has: its damage at its level now over its damage
    // at its own level (creature_classlevelstats), as its melee already has.
    float LevelFactor(Creature* creature)
    {
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        uint8 own = uint8((info->minlevel + info->maxlevel) / 2);
        CreatureBaseStats const* now = sObjectMgr->GetCreatureBaseStats(creature->GetLevel(), info->unit_class);
        CreatureBaseStats const* was = sObjectMgr->GetCreatureBaseStats(own, info->unit_class);
        uint32 expansion = std::min<uint32>(info->expansion, MAX_EXPANSIONS - 1);
        if (!now || !was || was->BaseDamage[expansion] <= 0.0f)
            return 1.0f;
        return std::clamp(now->BaseDamage[expansion] / was->BaseDamage[expansion], 0.01f, 100.0f);
    }

    // Whether a creature's spell is its caster's level's already: the core scales the ones that say so
    // (SPELL_ATTR0_SCALES_WITH_CREATURE_LEVEL, unless they grow by points per level), and a weapon
    // strike is made of its level's weapon damage.
    bool AtCastersLevel(SpellInfo const* spell)
    {
        if (!spell)
            return false;
        if (spell->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE) || spell->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE_NOSCHOOL) ||
            spell->HasEffect(SPELL_EFFECT_NORMALIZED_WEAPON_DMG) || spell->HasEffect(SPELL_EFFECT_WEAPON_PERCENT_DAMAGE))
            return true;
        if (!spell->SpellLevel || !spell->HasAttribute(SPELL_ATTR0_SCALES_WITH_CREATURE_LEVEL))
            return false;
        for (SpellEffectInfo const& effect : spell->GetEffects())
            if (effect.RealPointsPerLevel != 0.0f)
                return false;
        return true;
    }

    template<typename T>
    void ScaleSpell(T& amount, Unit* source, SpellInfo const* spell)
    {
        if (!amount || AtCastersLevel(spell))
            return;
        if (Creature* creature = ScaledSource(source))
            amount = T(std::max<double>(1.0, std::round(amount * LevelFactor(creature))));
    }

    // The heal hook's two units, put right (Unit::HealBySpell passes the healer first; a heal over
    // time's tick comes the right way round, through the periodic damage hook first, with the same
    // amount): as mod-wrath-remix's HealTick.
    struct HealTick
    {
        Unit const* target = nullptr;
        Unit const* caster = nullptr;
        uint32 const* amount = nullptr;
    };

    bool MarkHealTick(HealTick& tick, Unit* target, Unit* caster, uint32 const& amount, SpellInfo const* spell)
    {
        tick = HealTick{ target, caster, &amount };
        return spell && (spell->HasAura(SPELL_AURA_PERIODIC_HEAL) || spell->HasAura(SPELL_AURA_OBS_MOD_HEALTH)) &&
            !spell->HasAura(SPELL_AURA_PERIODIC_DAMAGE) && !spell->HasAura(SPELL_AURA_PERIODIC_DAMAGE_PERCENT) &&
            !spell->HasAura(SPELL_AURA_PERIODIC_LEECH);
    }

    void HealUnits(HealTick& tick, Unit*& target, Unit*& healer, uint32 const& amount)
    {
        bool periodic = tick.amount == &amount && tick.target == target && tick.caster == healer;
        tick = HealTick();
        if (!periodic)
            std::swap(target, healer);
    }

    thread_local HealTick levelHealTick, soloHealTick;

    // ---- the dungeons and raids for however many are there

    constexpr uint32 MAP_ICECROWN_CITADEL = 631;
    constexpr uint32 NPC_ICE_TOMB = 36980;
    constexpr uint32 NPC_VALITHRIA_DREAMWALKER = 36789;
    // Frenzied Bloodthirst (each difficulty's), and Uncontrollable Frenzy should one land anyway.
    constexpr uint32 BLOOD_QUEEN_ASKS[] = { 70877, 71474, 72151, 72648, 72649, 72650, 70923, 70924, 73015 };
    constexpr float FEW = 0.34f;  // less than a third of a group

    bool SoloActive() { return enabled && solo; }

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
            amount = T(std::lround(amount * std::min(soloMaxBoost, std::pow(share, -0.85f))));
        else if (!playerSide && target->IsControlledByPlayer())
        {
            float floor = map->IsRaid() ? soloRaidDamage : soloDungeonDamage;
            amount = T(std::max<double>(1.0, std::round(amount * std::max(floor, std::pow(share, 0.6f)))));
        }
    }

    bool FewInIcecrown(Map* map)
    {
        return SoloActive() && map && map->GetId() == MAP_ICECROWN_CITADEL && GroupShare(map) < FEW;
    }
}

class LevelScalingWorld : public WorldScript
{
public:
    LevelScalingWorld() : WorldScript("LevelScalingWorld", { WORLDHOOK_ON_AFTER_CONFIG_LOAD }) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        enabled = sConfigMgr->GetOption<bool>("LevelScaling.Enable", true);
        range = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("LevelScaling.Range", 2), 0, 10);
        questExperience = sConfigMgr->GetOption<bool>("LevelScaling.QuestExperience", true);
        solo = sConfigMgr->GetOption<bool>("LevelScaling.Solo.Enable", true);
        soloDungeonDamage = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("LevelScaling.Solo.DungeonDamage", 35), 1, 100) / 100.0f;
        soloRaidDamage = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("LevelScaling.Solo.RaidDamage", 15), 1, 100) / 100.0f;
        soloMaxBoost = float(std::clamp<uint32>(sConfigMgr->GetOption<uint32>("LevelScaling.Solo.MaxBoost", 15), 1, 50));
    }
};

// The creatures' levels as they appear or come back.
class LevelScalingCreatures : public AllCreatureScript
{
public:
    LevelScalingCreatures() : AllCreatureScript("LevelScalingCreatures") { }

    void OnBeforeCreatureSelectLevel(CreatureTemplate const* info, Creature* creature, uint8& level) override
    {
        // (the level pass's)
        if (forcedLevel)
        {
            level = forcedLevel;
            return;
        }
        if (!enabled || !creature || !info || creature->IsPet() || !creature->IsInWorld())
            return;
        Map* map = creature->GetMap();
        if (!Scales(map))
            return;
        Player* player = Followed(creature, map, std::max(REACH, map->GetVisibilityRange()));
        if (!player || !Follows(creature, info, player))
        {
            if (IsScaled(creature))
                MarkScaled(creature, false);
            return;
        }
        uint32 from, to;
        FollowRange(creature, info, player, from, to);
        level = uint8(urand(from, to));
        MarkScaled(creature, true);
    }

    // (one appearing: its level as SelectLevel had it before it was in the world, now that it is)
    void OnCreatureAddWorld(Creature* creature) override
    {
        if (!enabled || !creature || creature->IsPet() || !Scales(creature->GetMap()))
            return;
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        Player* player = info ? Followed(creature, creature->GetMap(), std::max(REACH, creature->GetMap()->GetVisibilityRange())) : nullptr;
        if (!player || !Follows(creature, info, player))
            return;
        uint32 from, to;
        FollowRange(creature, info, player, from, to);
        if (creature->GetLevel() < from || creature->GetLevel() > to)
            Relevel(creature, uint8(urand(from, to)));
    }

    void OnCreatureRemoveWorld(Creature* creature) override
    {
        if (creature && enabled)
            MarkScaled(creature, false);
    }

    // The trainers' option, at a class trainer of the player's own class.
    bool CanCreatureGossipHello(Player* player, Creature* creature) override
    {
        if (!enabled || !player || !creature || IsBot(player) || !creature->HasNpcFlag(UNIT_NPC_FLAG_TRAINER_CLASS))
            return false;
        Trainer::Trainer* trainer = sObjectMgr->GetTrainer(creature->GetEntry());
        if (!trainer || trainer->GetTrainerType() != Trainer::Type::Class || !trainer->IsTrainerValidForPlayer(player))
            return false;
        player->PrepareGossipMenu(creature, creature->GetGossipMenuId(), true);
        AddGossipItemFor(player, GOSSIP_ICON_TRAINER, ScalingOn(player) ?
            "Level scaling is on: the creatures near me are within 2 levels of mine. Turn it off." :
            "Level scaling is off: the creatures are their own level. Turn it on.",
            GOSSIP_SENDER_SCALING, 1);
        player->SendPreparedGossip(creature);
        return true;
    }

    bool CanCreatureGossipSelect(Player* player, Creature* /*creature*/, uint32 sender, uint32 /*action*/) override
    {
        if (sender != GOSSIP_SENDER_SCALING || !player)
            return false;
        bool on = !ScalingOn(player);
        player->UpdatePlayerSetting(SETTING, 0, on ? 1 : 0);
        CloseGossipMenuFor(player);
        ChatHandler(player->GetSession()).SendSysMessage(on ?
            "Level scaling is on: the creatures around you come within 2 levels of yours." :
            "Level scaling is off: the creatures around you go back to their own levels.");
        LevelPass(player);
        return true;
    }

    // (Valithria Dreamwalker mends a little by herself every second, with few in Icecrown Citadel)
    void OnAllCreatureUpdate(Creature* creature, uint32 diff) override
    {
        if (creature->GetEntry() != NPC_VALITHRIA_DREAMWALKER || !creature->IsAlive() || !creature->IsInCombat() || !FewInIcecrown(creature->GetMap()))
            return;
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

class LevelScalingPlayers : public PlayerScript
{
public:
    LevelScalingPlayers() : PlayerScript("LevelScalingPlayers", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LEVEL_CHANGED,
        PLAYERHOOK_ON_QUEST_COMPUTE_EXP }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (enabled && !IsBot(player))
            LevelPassSoon(player);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        if (ScalingOn(player))
            LevelPass(player);
    }

    // A quest below their level: the experience of one at their level, at the realm's rates.
    void OnPlayerQuestComputeXP(Player* player, Quest const* quest, uint32& xp) override
    {
        if (!xp || !questExperience || !ScalingOn(player) || quest->GetQuestLevel() < 0 || uint32(quest->GetQuestLevel()) >= player->GetLevel())
            return;
        uint32 own = quest->XPValue(player->GetLevel());
        QuestXPEntry const* entry = sQuestXPStore.LookupEntry(player->GetLevel());
        if (!own || !entry || quest->GetXPId() >= 10)
            return;
        uint32 theirs = entry->Exp[quest->GetXPId()];
        if (theirs > own)
            xp = uint32(std::lround(double(xp) * theirs / own));
    }
};

class LevelScalingDamage : public UnitScript
{
public:
    LevelScalingDamage() : UnitScript("LevelScalingDamage", true, {
        UNITHOOK_MODIFY_SPELL_DAMAGE_TAKEN,
        UNITHOOK_MODIFY_PERIODIC_DAMAGE_AURAS_TICK,
        UNITHOOK_MODIFY_MELEE_DAMAGE,
        UNITHOOK_MODIFY_HEAL_RECEIVED,
        UNITHOOK_ON_AURA_APPLY,
    }) { }

    void ModifySpellDamageTaken(Unit* target, Unit* attacker, int32& damage, SpellInfo const* spellInfo) override
    {
        if (damage <= 0)
            return;
        ScaleSpell(damage, attacker, spellInfo);
        ScaleForGroup(damage, target, attacker);
    }

    // (a heal over time's tick comes this way first: it's scaled once, as a heal)
    void ModifyPeriodicDamageAurasTick(Unit* target, Unit* attacker, uint32& damage, SpellInfo const* spellInfo) override
    {
        if (MarkHealTick(levelHealTick, target, attacker, damage, spellInfo))
            return;
        ScaleSpell(damage, attacker, spellInfo);
        ScaleForGroup(damage, target, attacker);
    }

    // (a creature's melee is its level's already)
    void ModifyMeleeDamage(Unit* target, Unit* attacker, uint32& damage) override
    {
        ScaleForGroup(damage, target, attacker);
    }

    void ModifyHealReceived(Unit* target, Unit* healer, uint32& heal, SpellInfo const* spellInfo) override
    {
        HealUnits(levelHealTick, target, healer, heal);
        ScaleSpell(heal, healer, spellInfo);
        // a player's heal on one of the instance's own (friendly) people, as far as their blows go
        if (!SoloActive() || !heal || !target || !healer || !healer->IsControlledByPlayer() || target->IsControlledByPlayer() || !target->IsCreature())
            return;
        float share = GroupShare(target->GetMap());
        if (share < 1.0f)
            heal = uint32(std::lround(heal * std::min(soloMaxBoost, std::pow(share, -0.85f))));
    }

    // Blood-Queen Lana'thel's bite passes, with few in Icecrown Citadel.
    void OnAuraApply(Unit* unit, Aura* aura) override
    {
        if (!unit || !aura || !unit->IsPlayer() || !FewInIcecrown(unit->GetMap()))
            return;
        uint32 spell = aura->GetId();
        for (uint32 asked : BLOOD_QUEEN_ASKS)
            if (spell == asked)
            {
                unit->m_Events.AddEventAtOffset([unit, spell]() { unit->RemoveAurasDueToSpell(spell); }, 1s);
                return;
            }
    }
};

// Sindragosa's Ice Tombs break by themselves, with few in Icecrown Citadel.
class LevelScalingTombs : public AllCreatureScript
{
public:
    LevelScalingTombs() : AllCreatureScript("LevelScalingTombs") { }

    void OnCreatureAddWorld(Creature* creature) override
    {
        if (!creature || creature->GetEntry() != NPC_ICE_TOMB || !FewInIcecrown(creature->GetMap()))
            return;
        creature->m_Events.AddEventAtOffset([creature]()
        {
            if (creature->IsAlive())
                Unit::Kill(creature, creature);
        }, 12s);
    }
};

void AddLevelScalingScripts()
{
    new LevelScalingWorld();
    new LevelScalingCreatures();
    new LevelScalingPlayers();
    new LevelScalingDamage();
    new LevelScalingTombs();
}
