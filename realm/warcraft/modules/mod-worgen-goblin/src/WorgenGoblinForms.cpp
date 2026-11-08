// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Worgen's two forms (Cataclysm's Two Forms, Altered Form and Darkflight, as the Cataclysm
 * Preservation Project's spell_gen_two_forms and spell_gen_darkflight have them), in a 3.3.5a game
 * that has no human form for a race.
 *
 * The 3.3.5a game draws a character from the race in its unit fields (the textures: skin, face, hair)
 * and its display (the model). A Worgen in human form shows the game race 1 (Human) and the human
 * model of their sex; the world server goes on knowing them as race 12 (AzerothCore keeps the race it
 * reads and saves apart from the one the fields show: quests, items, the race's abilities and the
 * saved character are the Worgen's). Their looks' numbers (skin, face, hair, its colour) are the
 * Worgen's, which every one of fits a human's range, but for the women's markings (12 to the human
 * women's 7 earrings): one past those shows none in human form and is put back for every save.
 *
 *  - Two Forms (68996, mod-worgoblin's racial, made an instant spell of the player's here: its row in
 *    tools/build_data.py) turns a Worgen into their other form, out of combat. Entering combat, or
 *    Darkflight, turns them Worgen (Cataclysm's Altered Form). The form chosen is kept with the
 *    character (character_settings).
 *  - With the starting areas, a new Worgen's story in Gilneas sets the form as Cataclysm does: human
 *    until Last Stand (14222) is done, then Worgen (the curse) until Last Chance at Humanity (14375),
 *    which gives them Two Forms. Anywhere else, or past it, or a death knight: Two Forms is theirs.
 *  - The barber shop's styles are a race's: in human form they're the Human's, which the world server
 *    doesn't take for a Worgen; the looks are changed in Worgen form.
 */

#include "WorgenGoblinZonesIds.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"

bool WorgenGoblinStartingAreasOn();

namespace
{
    constexpr uint8 WORGEN = 12;
    constexpr uint32 SPELL_TWO_FORMS = 68996, SPELL_DARKFLIGHT = 68992;
    constexpr uint32 QUEST_LAST_STAND = WorgenGoblinZones::Id(14222);
    constexpr uint32 QUEST_LAST_CHANCE_AT_HUMANITY = WorgenGoblinZones::Id(14375);
    constexpr uint8 HUMAN_FEMALE_MARKINGS = 7;          // (CharacterFacialHairStyles: the human women's)

    // The character's settings (character_settings): the form they chose, their markings' number.
    char const* const SETTINGS = "mod-worgen-goblin";
    enum Setting : uint32 { SETTING_HUMAN = 0, SETTING_MARKINGS = 1 };

    enum class Story { Free, Human, Worgen };

    bool IsGilneas(uint32 map)
    {
        return map == 638 || map == 654 || map == 655 || map == 656;
    }

    // Where a Worgen's story in Gilneas has them (with the starting areas).
    Story GilneasStory(Player* player)
    {
        if (!WorgenGoblinStartingAreasOn() || player->getClass() == CLASS_DEATH_KNIGHT || !IsGilneas(player->GetMapId())
            || player->GetQuestRewardStatus(QUEST_LAST_CHANCE_AT_HUMANITY))
            return Story::Free;
        return player->GetQuestRewardStatus(QUEST_LAST_STAND) ? Story::Worgen : Story::Human;
    }

    bool ShowsHuman(Player* player)
    {
        return player->GetByteValue(UNIT_FIELD_BYTES_0, 0) == RACE_HUMAN;
    }

    bool WantsHuman(Player* player)
    {
        switch (GilneasStory(player))
        {
            case Story::Human:
                return true;
            case Story::Worgen:
                return false;
            default:
                return player->GetPlayerSetting(SETTINGS, SETTING_HUMAN).value == 1;
        }
    }

    // The markings' number a human woman's can show (theirs put back for every save: OnPlayerSave).
    void ShowMarkings(Player* player, bool human)
    {
        uint32 kept = player->GetPlayerSetting(SETTINGS, SETTING_MARKINGS).value;
        if (human && player->getGender() == GENDER_FEMALE)
        {
            if (!kept)
            {
                kept = player->GetByteValue(PLAYER_BYTES_2, 0) + 1u;
                player->UpdatePlayerSetting(SETTINGS, SETTING_MARKINGS, kept);
            }
            uint8 shown = kept - 1 < HUMAN_FEMALE_MARKINGS ? uint8(kept - 1) : 0;
            if (player->GetByteValue(PLAYER_BYTES_2, 0) != shown)
                player->SetByteValue(PLAYER_BYTES_2, 0, shown);
        }
        else if (kept)
        {
            player->SetByteValue(PLAYER_BYTES_2, 0, uint8(kept - 1));
            player->UpdatePlayerSetting(SETTINGS, SETTING_MARKINGS, 0);
        }
    }

    // The form shown, as the player's choice and story say.
    void ShowForm(Player* player)
    {
        bool human = WantsHuman(player);
        ShowMarkings(player, human);
        if (human == ShowsHuman(player))
            return;
        if (human)
        {
            PlayerInfo const* info = sObjectMgr->GetPlayerInfo(RACE_HUMAN, CLASS_WARRIOR);
            if (!info)
                return;
            player->SetByteValue(UNIT_FIELD_BYTES_0, 0, RACE_HUMAN);
            player->SetNativeDisplayId(player->getGender() == GENDER_FEMALE ? info->displayId_f : info->displayId_m);
        }
        else
        {
            player->SetByteValue(UNIT_FIELD_BYTES_0, 0, WORGEN);
            player->InitDisplayIds();
        }
        // (a shapeshift or a transformation shown over it as before)
        player->RestoreDisplayId();
    }

    void ChooseForm(Player* player, bool human)
    {
        player->UpdatePlayerSetting(SETTINGS, SETTING_HUMAN, human ? 1 : 0);
        ShowForm(player);
    }

    bool IsWorgen(Player* player)
    {
        return player->getRace(true) == WORGEN;
    }
}

class WorgenGoblinFormsPlayer : public PlayerScript
{
public:
    WorgenGoblinFormsPlayer() : PlayerScript("WorgenGoblinFormsPlayer", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_UPDATE,
        PLAYERHOOK_ON_SAVE, PLAYERHOOK_ON_PLAYER_ENTER_COMBAT, PLAYERHOOK_ON_SPELL_CAST }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (IsWorgen(player))
            Update(player);
    }

    // The story's form as it goes (a quest done, a map changed), Two Forms once it's theirs.
    void OnPlayerUpdate(Player* player, uint32 /*diff*/) override
    {
        if (IsWorgen(player))
            Update(player);
    }

    // Their own markings' number saved, whatever human form shows.
    void OnPlayerSave(Player* player) override
    {
        if (uint32 kept = player->GetPlayerSetting(SETTINGS, SETTING_MARKINGS).value)
            player->SetByteValue(PLAYER_BYTES_2, 0, uint8(kept - 1));
    }

    // Into combat: Worgen (Cataclysm's Altered Form).
    void OnPlayerEnterCombat(Player* player, Unit* /*enemy*/) override
    {
        if (IsWorgen(player) && GilneasStory(player) == Story::Free && ShowsHuman(player))
            ChooseForm(player, false);
    }

    void OnPlayerSpellCast(Player* player, Spell* spell, bool /*skipCheck*/) override
    {
        if (spell->GetSpellInfo()->Id == SPELL_DARKFLIGHT && IsWorgen(player) && GilneasStory(player) == Story::Free && ShowsHuman(player))
            ChooseForm(player, false);
    }

private:
    static void Update(Player* player)
    {
        if (GilneasStory(player) == Story::Free && !player->HasSpell(SPELL_TWO_FORMS))
            player->learnSpell(SPELL_TWO_FORMS);
        ShowForm(player);
    }
};

// Two Forms: the other form, out of combat, once the story lets them choose.
class spell_worgen_goblin_two_forms : public SpellScript
{
    PrepareSpellScript(spell_worgen_goblin_two_forms);

    SpellCastResult CheckCast()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!player || !IsWorgen(player))
            return SPELL_FAILED_BAD_TARGETS;
        if (player->IsInCombat())
            return SPELL_FAILED_AFFECTING_COMBAT;
        if (GilneasStory(player) != Story::Free)
            return SPELL_FAILED_NOT_HERE;
        return SPELL_CAST_OK;
    }

    void HandleTransform(SpellEffIndex effIndex)
    {
        PreventHitDefaultEffect(effIndex);
        if (Player* player = GetCaster()->ToPlayer())
            ChooseForm(player, !ShowsHuman(player));
    }

    void Register() override
    {
        OnCheckCast += SpellCheckCastFn(spell_worgen_goblin_two_forms::CheckCast);
        OnEffectHit += SpellEffectFn(spell_worgen_goblin_two_forms::HandleTransform, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

void AddWorgenGoblinFormsScripts()
{
    new WorgenGoblinFormsPlayer();
    RegisterSpellScript(spell_worgen_goblin_two_forms);
}
