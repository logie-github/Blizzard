// SPDX-License-Identifier: GPL-3.0-or-later
// Wrath++: a character made with one of the undead skins (the creator's Undead switch, the app's import) is one of the
// Forsaken, whatever its race (the user, 13 November 2026: "make the starting area for any of the undead races if the
// box is checked the forsaken starter area and associate them with the forsaken quest line and the horde"):
//
//   * the Horde: its team, and the Forsaken's faction (Undercity's, ChrRaces' for the Undead) for a race of the
//     Alliance; a race of the Horde keeps its own faction and is on the Forsaken's side as it is;
//   * the Forsaken's in the world: where the world asks for a race mask (quests, the reputations a character starts
//     with, items, mail), the Undead's (the core patch's SetWorldRace: patches/azerothcore/0002): Deathknell's quests,
//     the Forsaken's line after them, Undercity's standing;
//   * Deathknell: at its first login it is brought to the Forsaken's starting place and its hearthstone is set there
//     (the Undead's playercreateinfo), its reputations are set again as the Forsaken's, and it learns Orcish and
//     Gutterspeak, the Horde's and the Forsaken's tongues.
//
// Which skins are undead: the server's own CharSections.dbc (DataDir/dbc, the looks' and the app's import), a skin row
// whose texture's name says Undead (WrathppUndead.kt names them so). A race's own colours come first and the undead
// ones after, so a character of colour 0 never is one. Its body, racials and gear stay its race's. An Undead
// character is as it always was. Runs only where the module does (Wrathpp.Enable, the Wrath++ realm and databases).

#include "Config.h"
#include "Log.h"
#include "Player.h"
#include "ReputationMgr.h"
#include "ScriptMgr.h"
#include "SharedDefines.h"

#include <algorithm>
#include <cctype>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <set>
#include <string>
#include <tuple>
#include <vector>

bool WrathppIsEnabled();

namespace
{
    // The Undead's start (playercreateinfo, race 5): Deathknell, Tirisfal Glades.
    constexpr uint32 kMap = 0, kZone = 85;
    constexpr float kX = 1676.71f, kY = 1678.31f, kZ = 121.67f, kO = 2.70526f;
    constexpr uint32 kUndercityFaction = 5;            // ChrRaces' faction template for the Undead
    constexpr uint32 kLanguageOrcish = 669, kLanguageGutterspeak = 17737;

    std::set<std::tuple<uint8, uint8, uint8>>& UndeadSkins()
    {
        static std::set<std::tuple<uint8, uint8, uint8>> skins;     // (race, sex, colour)
        return skins;
    }

    /// The undead skins of DataDir/dbc/CharSections.dbc; how many.
    size_t LoadUndeadSkins()
    {
        UndeadSkins().clear();
        // (the file by its name whatever its case: DataDir/dbc keeps the game's own spelling, and the phone's storage
        // tells cases apart)
        std::filesystem::path dir = std::filesystem::path(sConfigMgr->GetOption<std::string>("DataDir", "./")) / "dbc";
        std::filesystem::path path = dir / "CharSections.dbc";
        std::error_code error;
        for (auto const& entry : std::filesystem::directory_iterator(dir, error))
        {
            std::string name = entry.path().filename().string();
            std::transform(name.begin(), name.end(), name.begin(), [](unsigned char c) { return char(std::tolower(c)); });
            if (name == "charsections.dbc")
                path = entry.path();
        }
        std::ifstream in(path, std::ios::binary);
        if (!in)
            return 0;
        std::vector<char> d((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
        if (d.size() < 20 || std::memcmp(d.data(), "WDBC", 4) != 0)
            return 0;
        uint32 n, fields, size, strings;
        std::memcpy(&n, &d[4], 4); std::memcpy(&fields, &d[8], 4); std::memcpy(&size, &d[12], 4); std::memcpy(&strings, &d[16], 4);
        if (fields < 10 || size < 40 || d.size() < 20 + size_t(n) * size + strings)
            return 0;
        char const* text = &d[20 + size_t(n) * size];
        for (uint32 i = 0; i < n; ++i)
        {
            int32 r[10];
            std::memcpy(r, &d[20 + size_t(i) * size], sizeof(r));
            // id, race, sex, section (0: skin), three textures, flags, variation, colour
            if (r[3] != 0 || r[4] < 0 || uint32(r[4]) >= strings)
                continue;
            std::string name(text + r[4]);
            std::transform(name.begin(), name.end(), name.begin(), [](unsigned char c) { return char(std::tolower(c)); });
            if (name.find("undead") != std::string::npos)
                UndeadSkins().emplace(uint8(r[1]), uint8(r[2]), uint8(r[9]));
        }
        return UndeadSkins().size();
    }

    bool MadeUndead(Player const* player)
    {
        uint8 race = player->getRace(true);
        if (race == RACE_UNDEAD_PLAYER)
            return false;
        uint8 colour = player->GetByteValue(PLAYER_BYTES, 0);
        return colour && UndeadSkins().count({race, player->getGender(), colour});
    }
}

class WrathppUndeadWorldScript : public WorldScript
{
public:
    WrathppUndeadWorldScript() : WorldScript("WrathppUndeadWorldScript", {WORLDHOOK_ON_STARTUP}) { }

    void OnStartup() override
    {
        if (!WrathppIsEnabled())
            return;
        LOG_INFO("module", "Wrath++: {} undead skins (characters made with one are Forsaken)", LoadUndeadSkins());
    }
};

class WrathppUndeadPlayerScript : public PlayerScript
{
public:
    WrathppUndeadPlayerScript() : PlayerScript("WrathppUndeadPlayerScript", {PLAYERHOOK_ON_UPDATE_FACTION, PLAYERHOOK_ON_FIRST_LOGIN}) { }

    // Each time the character's faction is set from its race (as it is loaded): the Forsaken's.
    void OnPlayerUpdateFaction(Player* player) override
    {
        if (!WrathppIsEnabled() || !MadeUndead(player))
            return;
        player->SetWorldRace(RACE_UNDEAD_PLAYER);
        if (player->GetTeamId(true) != TEAM_HORDE)
        {
            player->setTeamId(TEAM_HORDE);
            player->SetFaction(kUndercityFaction);
        }
    }

    // Brought to Deathknell, its hearthstone there, its standing the Forsaken's, the Horde's and the Forsaken's tongues.
    void OnPlayerFirstLogin(Player* player) override
    {
        if (!WrathppIsEnabled() || !MadeUndead(player))
            return;
        player->SetHomebind(WorldLocation(kMap, kX, kY, kZ, kO), kZone);
        player->GetReputationMgr().Reset();
        player->GetReputationMgr().SendInitialReputations();
        for (auto [spell, skill] : {std::pair<uint32, uint16>{kLanguageOrcish, SKILL_LANG_ORCISH}, {kLanguageGutterspeak, SKILL_LANG_GUTTERSPEAK}})
        {
            player->learnSpell(spell);
            player->SetSkill(skill, 0, 300, 300);
        }
        player->TeleportTo(kMap, kX, kY, kZ, kO);
        LOG_INFO("module", "Wrath++: {} (race {}, undead skin {}) starts as one of the Forsaken in Deathknell",
            player->GetName(), uint32(player->getRace(true)), uint32(player->GetByteValue(PLAYER_BYTES, 0)));
    }
};

void AddWrathppUndeadStartScripts()
{
    new WrathppUndeadWorldScript();
    new WrathppUndeadPlayerScript();
}
