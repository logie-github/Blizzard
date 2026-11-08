// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The starting areas as they're played (mod-worgen-goblin, data/zones, tools/zones): what
 * Cataclysm's game and server do there that 3.3.5a's don't.
 *
 *  - Gilneas's terrain swaps (CPP's terrain_swap_defaults and their conditions): Cataclysm shows one
 *    map of Gilneas (654) with another's tiles over it as the story goes. Here each is a map of its
 *    own (tools/zones/package.py), so a player of Gilneas is on the one their quests say: 638
 *    (Gilneas City before the curse) until Last Stand (14222) is done, then 654, then 655 (the
 *    land broken by the Cataclysm) once Leader of the Pack (14386) is. Any teleport onto Gilneas
 *    lands on that one; finishing either quest takes the player to it where they stand.
 *  - Cataclysm's spell effects 3.3.5a hasn't (tools/zones/spells.py, EFFECT_HOOKS): dummies whose
 *    second misc value says which (ZoneHook), each answered by its script in spell_script_names: a
 *    movie (its narration: Cataclysm Classic's game has the Worgen's and Goblins' movies' sound, not
 *    their pictures), the phases updated (the area's phase auras, spell_area), a teleport to the
 *    spell's place (spell_target_position).
 *  - The way out into Wrath's world: Rut'theran Village turned in, the Worgen sail to Rut'theran Village
 *    (Darnassus their home); Warchief's Emissary taken, the Goblins are taken to Grommash Hold, where
 *    3.3.5a's Thrall takes it (Orgrimmar their home).
 *  - Cataclysm's quests whose objective is casting a spell (its class quests: Charge on a training
 *    dummy): 3.3.5a's quests haven't the kind, so the cast counts as a kill of the quest's credit
 *    creature would. A spell the class hasn't at level 1 in 3.3.5a has its starting one in its place
 *    (tools/zones/quests.py, STAND_INS).
 */

#include "WorgenGoblinZonesIds.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"

namespace
{
    constexpr uint32 QUEST_LAST_STAND = WorgenGoblinZones::Id(14222);
    // The way out into Wrath's world: the Worgen to Rut'theran Village after Rut'theran Village (Admiral
    // Nightwind's ship), Darnassus their home; the Goblins to Grommash Hold on taking Warchief's Emissary
    // (Thrall takes it there), Orgrimmar theirs. (Their places: the world's game_tele.)
    constexpr uint32 QUEST_RUTTHERAN_VILLAGE = WorgenGoblinZones::Id(14434);
    constexpr uint32 QUEST_WARCHIEFS_EMISSARY = WorgenGoblinZones::Id(25266);
    WorldLocation const RUTTHERAN_VILLAGE(1, 8704.53f, 944.683f, 13.5177f, 2.99385f);
    WorldLocation const DARNASSUS(1, 9949.56f, 2284.21f, 1341.4f, 1.59587f);
    WorldLocation const GROMMASH_HOLD(1, 1924.94f, -4205.16f, 42.0388f, 1.65038f);
    WorldLocation const ORGRIMMAR(1, 1629.85f, -4373.64f, 31.5573f, 3.69762f);
    constexpr uint32 QUEST_LEADER_OF_THE_PACK = WorgenGoblinZones::Id(14386);
    constexpr uint32 MAP_GILNEAS = 654, MAP_GILNEAS_CITY = 638, MAP_GILNEAS_BROKEN = 655;

    enum class ZoneHook : int32
    {
        Movie = 1,
        Phases = 2,
        Teleport = 3,
    };

    bool IsGilneas(uint32 map)
    {
        return map == MAP_GILNEAS || map == MAP_GILNEAS_CITY || map == MAP_GILNEAS_BROKEN;
    }

    // The map of Gilneas a player's story has them on.
    uint32 GilneasMap(Player const* player)
    {
        if (!player->GetQuestRewardStatus(QUEST_LAST_STAND))
            return MAP_GILNEAS_CITY;
        return player->GetQuestRewardStatus(QUEST_LEADER_OF_THE_PACK) ? MAP_GILNEAS_BROKEN : MAP_GILNEAS;
    }

    // A player on another map of Gilneas than theirs, taken to theirs where they stand.
    void ToGilneasMap(Player* player)
    {
        if (!IsGilneas(player->GetMapId()) || player->IsBeingTeleported())
            return;
        uint32 map = GilneasMap(player);
        if (map != player->GetMapId())
            player->TeleportTo(map, player->GetPositionX(), player->GetPositionY(), player->GetPositionZ(), player->GetOrientation());
    }

    // Out to Wrath's world, a moment after the quest's turned in or taken.
    void SendOut(Player* player, WorldLocation const& to, WorldLocation const& home, uint32 homeArea)
    {
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid, to, home, homeArea]()
        {
            if (Player* out = ObjectAccessor::FindPlayer(guid))
            {
                out->SetHomebind(home, homeArea);
                out->TeleportTo(to);
            }
        }, 2s);
    }

    bool IsHook(SpellInfo const* spell, SpellEffIndex effect, ZoneHook hook)
    {
        return spell->Effects[effect].Effect == SPELL_EFFECT_DUMMY && spell->Effects[effect].MiscValueB == int32(hook);
    }
}

class WorgenGoblinZonesPlayer : public PlayerScript
{
public:
    WorgenGoblinZonesPlayer() : PlayerScript("WorgenGoblinZonesPlayer", { PLAYERHOOK_ON_BEFORE_TELEPORT, PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_SPELL_CAST, PLAYERHOOK_ON_PLAYER_QUEST_ACCEPT }) { }

    void OnPlayerQuestAccept(Player* player, Quest const* quest) override
    {
        if (quest->GetQuestId() == QUEST_WARCHIEFS_EMISSARY)
            SendOut(player, GROMMASH_HOLD, ORGRIMMAR, AREA_ORGRIMMAR);
    }

    // A quest whose objective is casting a spell (Cataclysm's class quests: CAST_CREDITS): the cast
    // counts as a kill of the quest's credit creature ("Spell Practice Credit") would.
    void OnPlayerSpellCast(Player* player, Spell* spell, bool /*skipCheck*/) override
    {
        for (WorgenGoblinZones::CastCredit const& credit : WorgenGoblinZones::CAST_CREDITS)
            if (credit.spell == spell->GetSpellInfo()->Id && player->GetQuestStatus(credit.quest) == QUEST_STATUS_INCOMPLETE)
                player->KilledMonsterCredit(credit.creature);
    }

    // Onto Gilneas: onto the player's own map of it.
    bool OnPlayerBeforeTeleport(Player* player, uint32 mapid, float x, float y, float z, float orientation, uint32 options, Unit* target) override
    {
        if (!IsGilneas(mapid))
            return true;
        uint32 map = GilneasMap(player);
        if (map == mapid)
            return true;
        player->TeleportTo(map, x, y, z, orientation, options, target);
        return false;
    }

    void OnPlayerLogin(Player* player) override
    {
        ToGilneasMap(player);
    }
};

// A quest of Gilneas's handed in that changes its map.
class WorgenGoblinZonesCreature : public AllCreatureScript
{
public:
    WorgenGoblinZonesCreature() : AllCreatureScript("WorgenGoblinZonesCreature") { }

    bool CanCreatureQuestReward(Player* player, Creature* /*creature*/, Quest const* quest, uint32 /*opt*/) override
    {
        if (quest->GetQuestId() == QUEST_LAST_STAND || quest->GetQuestId() == QUEST_LEADER_OF_THE_PACK)
            ToGilneasMap(player);
        else if (quest->GetQuestId() == QUEST_RUTTHERAN_VILLAGE)
            SendOut(player, RUTTHERAN_VILLAGE, DARNASSUS, AREA_DARNASSUS);
        return false;
    }
};

class WorgenGoblinZonesObject : public AllGameObjectScript
{
public:
    WorgenGoblinZonesObject() : AllGameObjectScript("WorgenGoblinZonesObject") { }

    bool CanGameObjectQuestReward(Player* player, GameObject* /*go*/, Quest const* quest, uint32 /*opt*/) override
    {
        if (quest->GetQuestId() == QUEST_LAST_STAND || quest->GetQuestId() == QUEST_LEADER_OF_THE_PACK)
            ToGilneasMap(player);
        return false;
    }
};

// Cataclysm's 45 (a movie): its narration, to the player it's for.
class spell_worgen_goblin_zones_movie : public SpellScript
{
    PrepareSpellScript(spell_worgen_goblin_zones_movie);

    void Handle(SpellEffIndex effect)
    {
        if (!IsHook(GetSpellInfo(), effect, ZoneHook::Movie))
            return;
        Player* player = GetHitPlayer();
        if (uint32 sound = GetSpellInfo()->Effects[effect].MiscValue; player && sound)
            player->PlayDirectSound(sound, player);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_worgen_goblin_zones_movie::Handle, EFFECT_ALL, SPELL_EFFECT_DUMMY);
    }
};

// Cataclysm's 167 and 170 (the phases and the area's auras updated): the area's phase auras
// (spell_area) as the player's quests now say, and their map of Gilneas.
class spell_worgen_goblin_zones_phases : public SpellScript
{
    PrepareSpellScript(spell_worgen_goblin_zones_phases);

    void Handle(SpellEffIndex effect)
    {
        if (!IsHook(GetSpellInfo(), effect, ZoneHook::Phases))
            return;
        if (Player* player = GetHitPlayer())
        {
            player->UpdateZoneDependentAuras(player->GetZoneId());
            player->UpdateAreaDependentAuras(player->GetAreaId());
            ToGilneasMap(player);
        }
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_worgen_goblin_zones_phases::Handle, EFFECT_ALL, SPELL_EFFECT_DUMMY);
    }
};

// Cataclysm's 252 (a teleport with a loading screen): to the spell's place (on Gilneas, the
// player's own map of it: WorgenGoblinZonesPlayer).
class spell_worgen_goblin_zones_teleport : public SpellScript
{
    PrepareSpellScript(spell_worgen_goblin_zones_teleport);

    void Handle(SpellEffIndex effect)
    {
        if (!IsHook(GetSpellInfo(), effect, ZoneHook::Teleport))
            return;
        Player* player = GetHitPlayer();
        WorldLocation const* dest = GetHitDest();
        if (player && dest && dest->GetMapId() != MAPID_INVALID)
            player->TeleportTo(*dest);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_worgen_goblin_zones_teleport::Handle, EFFECT_ALL, SPELL_EFFECT_DUMMY);
    }
};

void AddWorgenGoblinZonesScripts()
{
    new WorgenGoblinZonesPlayer();
    new WorgenGoblinZonesCreature();
    new WorgenGoblinZonesObject();
    RegisterSpellScript(spell_worgen_goblin_zones_movie);
    RegisterSpellScript(spell_worgen_goblin_zones_phases);
    RegisterSpellScript(spell_worgen_goblin_zones_teleport);
}
