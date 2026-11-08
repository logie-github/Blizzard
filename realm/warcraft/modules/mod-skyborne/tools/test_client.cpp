// SPDX-License-Identifier: GPL-3.0-or-later
// The Skyborne's patch made for a game folder, and checked (no server needed):
//
//   g++ -std=c++17 -O2 -DSKYBORNE_BZIP2 -I../src test_client.cpp ../src/SkyborneFiles.cpp ../src/SkybornePatch.cpp -lz -lbz2
//   ./a.out MODULE_DATA GAME_DATA [OUT]
//
// MODULE_DATA: the module's data/client; GAME_DATA: a client's Data folder. Makes Data/patch-Z.MPQ,
// reads it back, checks the races, looks, spells and textures are in it, that a second run leaves it
// as it is, and with OUT writes some of its textures there (as .blp) to look at.

#include "SkyborneFiles.h"
#include "SkybornePatch.h"
#include <cstdio>
#include <iostream>
#include <map>
#include <set>
#include <tuple>

using namespace Skyborne;

static int failures = 0;

static void Check(bool ok, std::string const& what)
{
    std::cout << (ok ? "ok   " : "FAIL ") << what << "\n";
    if (!ok)
        ++failures;
}

int main(int argc, char** argv)
{
    if (argc < 3)
    {
        std::cerr << "test_client MODULE_DATA GAME_DATA [OUT]\n";
        return 2;
    }
    fs::path module = argv[1], data = argv[2];
    std::error_code error;
    fs::remove(data / PATCH, error);
    fs::remove(data / MARK, error);

    auto log = [](std::string const& line) { std::cout << "  " << line << "\n"; };
    Check(UpdatePatch(module, data, log), "the patch is made");
    auto made = fs::last_write_time(data / PATCH, error);
    Check(UpdatePatch(module, data, log), "a second start keeps it");
    Check(fs::last_write_time(data / PATCH, error) == made, "...without making it again");

    auto patch = OpenArchive(data / PATCH);
    Bytes bytes;
    Dbc races;
    Check(patch->Read("DBFilesClient\\ChrRaces.dbc", bytes) && races.Parse(bytes), "ChrRaces.dbc is in it");
    int skyborne = 0, moved = 0;
    for (size_t i = 0; i < races.records.size(); ++i)
    {
        uint32_t id = races.Get(i, 0), flags = races.Get(i, 1);
        if ((id == 13 || id == 14) && !(flags & 1))
            ++skyborne;
        if (id == 22 || id == 23)
            ++moved;
    }
    Check(skyborne == 2, "the two Skyborne races are playable");
    Check(moved == 2, "the Naga and Broken moved to 22 and 23");

    Dbc sections;
    Check(patch->Read("DBFilesClient\\CharSections.dbc", bytes) && sections.Parse(bytes), "CharSections.dbc is in it");
    int looks = 0, leftover = 0, darkRanger = 0, skins = 0, withExtra = 0, overlays = 0, worn = 0;
    Game hd(data, { "patch-z.mpq", "patch-y.mpq" });
    Bytes probe;
    bool hasExtra = hd.Read("Character\\BloodElf\\Female\\BloodElfFemaleSkin00_00_Extra.blp", probe);
    for (size_t i = 0; i < sections.records.size(); ++i)
    {
        uint32_t race = sections.Get(i, 1), base = sections.Get(i, 3), color = sections.Get(i, 9);
        if (race == 13 || race == 14)
        {
            ++looks;
            if (sections.Get(i, 0) < 900000)
                ++leftover;
        }
        if (race == 10 && base == 0 && color == 19)
            ++darkRanger;
        if (base == 4)
        {
            ++overlays;
            if (sections.Get(i, 4) || sections.Get(i, 5) || sections.Get(i, 6))
                ++worn;
        }
        if ((race == 13 || race == 14 || (race == 10 && color == 19)) && base == 0)
        {
            ++skins;
            uint32_t at = sections.Get(i, 5);
            std::string second = at < sections.strings.size() ? reinterpret_cast<char const*>(&sections.strings[at]) : "";
            if (!second.empty() && patch->Read(second, probe) == (second.find("Skyborne") != std::string::npos || color == 19))
                ++withExtra;
        }
    }
    // HD looks: a skin's ears, jaw and eyes are its _Extra texture; theirs too (made, or the blood elf's).
    if (hasExtra)
        Check(withExtra == skins, "every skin has its _Extra texture (" + std::to_string(withExtra) + " of " + std::to_string(skins) + ")");
    Check(looks > 2000, "the Skyborne's looks (" + std::to_string(looks) + ")");
    Check(leftover == 0, "no Naga or Broken looks left on races 13 and 14");
    Check(darkRanger == 2, "the blood elf's Dark Ranger skin, both sexes");
    Check(overlays > 0 && worn == 0, "section 4 rows carry no textures (" + std::to_string(overlays) + " rows)");
    // An NPC's skin (flag 1 off) has a face row for every face its race and sex have (a look the game
    // puts together itself with such a skin, Wrath Remix's Moratari in her dress, fails without one).
    {
        std::map<std::pair<uint32_t, uint32_t>, std::set<uint32_t>> faces;
        std::map<std::tuple<uint32_t, uint32_t, uint32_t>, std::set<uint32_t>> facesOf;
        std::set<std::tuple<uint32_t, uint32_t, uint32_t>> npcSkins;
        for (size_t i = 0; i < sections.records.size(); ++i)
        {
            uint32_t race = sections.Get(i, 1), sex = sections.Get(i, 2), base = sections.Get(i, 3), color = sections.Get(i, 9);
            if (base == 0 && !(sections.Get(i, 7) & 1))
                npcSkins.insert({ race, sex, color });
            if (base == 1)
            {
                faces[{ race, sex }].insert(sections.Get(i, 8));
                facesOf[{ race, sex, color }].insert(sections.Get(i, 8));
            }
        }
        int faceless = 0;
        for (auto const& skin : npcSkins)
            if (facesOf[skin].size() < faces[{ std::get<0>(skin), std::get<1>(skin) }].size())
                ++faceless;
        Check(!npcSkins.empty() && faceless == 0, "every NPC skin has its faces (" + std::to_string(npcSkins.size()) + " skins)");
    }
    // A player's skin (flag 1, not only a death knight's) has the same faces as every other of its race
    // and sex, the death knights' (flag 4) among them: a death knight may wear any skin with any of
    // them, and a skin with fewer faces than the others crashed the character creation screen (the game
    // read through the missing face's row; releases up to 1.0.245).
    {
        std::map<std::tuple<uint32_t, uint32_t, uint32_t>, std::set<uint32_t>> facesOf;
        std::map<std::pair<uint32_t, uint32_t>, std::set<uint32_t>> playerSkins;
        for (size_t i = 0; i < sections.records.size(); ++i)
        {
            uint32_t race = sections.Get(i, 1), sex = sections.Get(i, 2), base = sections.Get(i, 3), flags = sections.Get(i, 7);
            uint32_t color = sections.Get(i, 9);
            if (base == 0 && (flags & 1) && !(flags & 4))
                playerSkins[{ race, sex }].insert(color);
            if (base == 1 && (flags & 1))
                facesOf[{ race, sex, color }].insert(sections.Get(i, 8));
        }
        int uneven = 0;
        std::string first;
        for (auto const& [who, skins] : playerSkins)
        {
            std::set<uint32_t> const& faces = facesOf[{ who.first, who.second, *skins.begin() }];
            for (uint32_t color : skins)
                if (facesOf[{ who.first, who.second, color }] != faces)
                {
                    if (!uneven++)
                        first = " (first: race " + std::to_string(who.first) + " sex " + std::to_string(who.second) + " skin " + std::to_string(color) + ")";
                }
        }
        Check(!playerSkins.empty() && uneven == 0, "every player skin has the faces of its race and sex's others" + first);
    }
    // No skin colour without a row below a race and sex's highest: the screen reads a colour's row by
    // its number as the race changes, and a colour with no row is a missing row's texture read.
    {
        std::map<std::pair<uint32_t, uint32_t>, std::set<uint32_t>> colours;
        for (size_t i = 0; i < sections.records.size(); ++i)
            if (sections.Get(i, 3) == 0)
                colours[{ sections.Get(i, 1), sections.Get(i, 2) }].insert(sections.Get(i, 9));
        int holes = 0;
        std::string first;
        for (auto const& [who, has] : colours)
            for (uint32_t c = 0; c < *has.rbegin(); ++c)
                if (!has.count(c) && !holes++)
                    first = " (first: race " + std::to_string(who.first) + " sex " + std::to_string(who.second) + " colour " + std::to_string(c) + ")";
        Check(holes == 0, "no skin colour without its row below the highest" + first);
    }
    // CharSections in the game's order: each race, sex and section's rows one run, and each variation's
    // in it (the game sizes its look-up arrays from the runs: a group split across the table crashed
    // the character creation screen, crash reports #34 to #54).
    {
        std::set<std::tuple<uint32_t, uint32_t, uint32_t, uint32_t>> seen;
        std::tuple<uint32_t, uint32_t, uint32_t, uint32_t> previous{ ~0u, ~0u, ~0u, ~0u };
        int split = 0;
        for (size_t i = 0; i < sections.records.size(); ++i)
        {
            std::tuple<uint32_t, uint32_t, uint32_t, uint32_t> key{ sections.Get(i, 1), sections.Get(i, 2), sections.Get(i, 3), sections.Get(i, 8) };
            if (key != previous && !seen.insert(key).second)
                ++split;
            previous = key;
        }
        Check(split == 0, "CharSections in the game's order: no race, sex, section and variation split (" + std::to_string(split) + ")");
    }

    Dbc spells;
    Check(patch->Read("DBFilesClient\\Spell.dbc", bytes) && spells.Parse(bytes), "Spell.dbc is in it");
    int racials = 0;
    for (size_t i = 0; i < spells.records.size(); ++i)
        if (spells.Get(i, 0) >= 98701 && spells.Get(i, 0) <= 98707)
            ++racials;
    Check(racials == 7, "the racials (" + std::to_string(racials) + ")");

    Bytes toc;
    Check(patch->Read("Interface\\GlueXML\\GlueXML.toc", toc) && std::string(toc.begin(), toc.end()).find("SkyborneCreate.lua") != std::string::npos,
          "the character screen loads theirs");
    Check(patch->Read("Interface\\GlueXML\\GlueXML.toc", toc) && std::string(toc.begin(), toc.end()).find("SkyborneZoom.lua") != std::string::npos
              && patch->Read("Interface\\GlueXML\\SkyborneZoom.lua", bytes) && bytes.size() > 500,
          "the character screen zooms");
    Check(patch->Read("Sound\\CinematicVoices\\SkyborneNarration.mp3", bytes) && bytes.size() > 100000, "the narration");

    Bytes icons;
    Image image;
    Check(patch->Read("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races.blp", icons) && Decode(icons, image), "the race icons");

    // Textures: one of each kind made, decodable, the size of the original.
    Game game(data, { "patch-z.mpq", "patch-y.mpq" });
    char const* pairs[][2] = {
        { "Character\\BloodElf\\Female\\BloodElfFemaleSkin00_00.blp", "Character\\Skyborne\\Female\\SkyborneFemaleSkin00_19.blp" },
        { "Character\\BloodElf\\Female\\BloodElfFemaleFaceUpper00_00.blp", "Character\\Skyborne\\Female\\SkyborneFemaleFaceUpper00_00.blp" },
        { "Character\\BloodElf\\Female\\BloodElfFemaleFaceUpper00_00.blp", "Character\\Skyborne\\Female\\SkyborneFemaleFaceUpper10_22.blp" },
        { "Character\\BloodElf\\Hair00_01.blp", "Character\\Skyborne\\Hair00_16.blp" },
        { "Character\\BloodElf\\Female\\BloodElfFemaleFaceUpper00_00.blp", "Character\\BloodElf\\Female\\BloodElfFemaleFaceUpper00_19.blp" },
        { "Character\\BloodElf\\Female\\BloodElfFemaleSkin00_00_Extra.blp", "Character\\BloodElf\\Female\\BloodElfFemaleSkin00_19_Extra.blp" },
        { "Character\\BloodElf\\Female\\BloodElfFemaleSkin00_00_Extra.blp", "Character\\Skyborne\\Female\\SkyborneFemaleSkin00_20_Extra.blp" },
        { "Character\\BloodElf\\Hair00_01.blp", "Character\\Skyborne\\Hair00_19.blp" },
    };
    for (auto const& p : pairs)
    {
        Bytes original, made2;
        Image a, b;
        bool ok = game.Read(p[0], original) && patch->Read(p[1], made2) && Decode(original, a) && Decode(made2, b)
            && a.width == b.width && a.height == b.height && a.rgba != b.rgba;
        Check(ok, std::string("made: ") + p[1]);
        if (ok && argc > 3)
        {
            std::string name = fs::path(std::string(p[1]).substr(std::string(p[1]).find_last_of('\\') + 1)).string();
            std::ofstream(fs::path(argv[3]) / name, std::ios::binary).write(reinterpret_cast<char const*>(made2.data()), std::streamsize(made2.size()));
        }
    }
    if (argc > 3)
        std::ofstream(fs::path(argv[3]) / "UI-CharacterCreate-Races.blp", std::ios::binary).write(reinterpret_cast<char const*>(icons.data()), std::streamsize(icons.size()));

    std::cout << (failures ? std::to_string(failures) + " failed\n" : "all passed\n");
    return failures ? 1 : 0;
}
