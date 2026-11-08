// SPDX-License-Identifier: GPL-3.0-or-later
// The Worgen's and Goblins' patch made for a game folder, and checked (no server needed):
//
//   g++ -std=c++17 -O2 -I../src -I../../mod-skyborne/src test_patch.cpp
//       ../../mod-skyborne/src/SkyborneFiles.cpp ../src/WorgenGoblinPatch.cpp -lz
//   ./a.out MODULE_DATA FILES GAME_DATA [OTHERS...]
//
// MODULE_DATA: the module's data/client; FILES: mod-worgoblin's files (tools/package.py's output,
// with worgengoblin.files); GAME_DATA: a client's Data folder (a stand-in: the server's tables as
// the game's, Data/enUS/locale-enUS.MPQ/DBFilesClient, and a GlueXML.toc). Makes Data/patch-U.MPQ,
// reads it back and checks the two races, the creatures moved out of their places, their bits in the
// game's rows, their files and the character screen are in it, and that a second run leaves it as it
// is. OTHERS: the other modules' data/client folders (the allied races', the Skyborne's), whose
// tables' changes are then applied over this patch's tables, as their patches are made from the game
// with it in: the races of all three are there together, none in another's place.

#include "WorgenGoblinPatch.h"
#include "SkyborneFiles.h"
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <set>

using namespace Skyborne;

static int failures = 0;

static void Check(bool ok, std::string const& what)
{
    std::cout << (ok ? "ok   " : "FAIL ") << what << "\n";
    if (!ok)
        ++failures;
}

static std::string Text(fs::path const& path)
{
    std::ifstream in(path, std::ios::binary);
    return std::string(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
}

static std::string Str(Dbc const& dbc, size_t row, uint32_t field)
{
    uint32_t at = dbc.Get(row, field);
    return at < dbc.strings.size() ? std::string(reinterpret_cast<char const*>(&dbc.strings[at])) : std::string();
}

static long Find(Dbc const& dbc, uint32_t id)
{
    for (size_t row = 0; row < dbc.records.size(); ++row)
        if (dbc.Get(row, 0) == id)
            return long(row);
    return -1;
}

static size_t Count(Dbc const& dbc, uint32_t field, uint32_t value)
{
    size_t n = 0;
    for (size_t row = 0; row < dbc.records.size(); ++row)
        if (dbc.Get(row, field) == value)
            ++n;
    return n;
}

int main(int argc, char** argv)
{
    if (argc < 4)
    {
        std::cerr << "test_patch MODULE_DATA FILES GAME_DATA [OTHERS...]\n";
        return 2;
    }
    fs::path module = argv[1], files = argv[2], data = argv[3];
    auto log = [](std::string const& line) { std::cout << "  log: " << line << "\n"; };
    std::error_code error;
    fs::remove(data / "patch-U.MPQ", error);
    fs::remove(data / "patch-U.MPQ.worgengoblin", error);

    // The game before the patch.
    Game before(data, {});
    std::map<std::string, Dbc> stock;
    for (char const* name : { "ChrRaces", "CharSections", "CreatureDisplayInfoExtra", "CharHairGeosets" })
    {
        Bytes b;
        Check(before.Read(std::string("DBFilesClient\\") + name + ".dbc", b) && stock[name].Parse(b), std::string("the stand-in game has ") + name);
    }

    Check(WorgenGoblin::UpdatePatch(module, files, data, log), "the patch is made");
    auto made = fs::last_write_time(data / "patch-U.MPQ", error);
    Check(!error, "Data/patch-U.MPQ is there");

    Game game(data, {});
    auto table = [&](std::string const& name, Dbc& dbc)
    {
        Bytes b;
        return game.Read("DBFilesClient\\" + name + ".dbc", b) && dbc.Parse(b);
    };

    Dbc races;
    Check(table("ChrRaces", races), "ChrRaces is in it");
    long goblin = Find(races, 9), worgen = Find(races, 12), npcGoblin = Find(races, 28), felOrc = Find(races, 29);
    Check(goblin >= 0 && Str(races, goblin, 11) == "Goblin" && Str(races, goblin, 14) == "Goblin", "race 9 is the Goblins");
    Check(worgen >= 0 && Str(races, worgen, 11) == "Worgen" && Str(races, worgen, 14) == "Worgen", "race 12 is the Worgen");
    long stockFelOrc = Find(stock["ChrRaces"], 12);
    Check(felOrc >= 0 && stockFelOrc >= 0 && Str(races, felOrc, 11) == Str(stock["ChrRaces"], stockFelOrc, 11)
          && races.Get(felOrc, 4) == stock["ChrRaces"].Get(stockFelOrc, 4), "the game's own race 12 (the fel orcs') is at 29, as it was");
    Check(npcGoblin >= 0 && races.Get(npcGoblin, 4) == stock["ChrRaces"].Get(Find(stock["ChrRaces"], 9), 4),
          "the game's own race 9 (the creatures' goblins) is at 28, as it was");

    Dbc sections;
    Check(table("CharSections", sections), "CharSections is in it");
    size_t mine = Count(sections, 1, 9) + Count(sections, 1, 12);
    Check(mine == 1642, "the Worgen's and Goblins' 1642 looks (" + std::to_string(mine) + ")");
    Check(Count(sections, 1, 28) == Count(stock["CharSections"], 1, 9) && Count(sections, 1, 29) == Count(stock["CharSections"], 1, 12),
          "the creatures' looks of races 9 and 12 moved to 28 and 29");
    Check(sections.records.size() == stock["CharSections"].records.size() + 1642, "no other look added or lost");

    Dbc extra;
    Check(table("CreatureDisplayInfoExtra", extra), "CreatureDisplayInfoExtra is in it");
    Check(Count(extra, 1, 28) == Count(stock["CreatureDisplayInfoExtra"], 1, 9)
          && Count(extra, 1, 29) == Count(stock["CreatureDisplayInfoExtra"], 1, 12),
          "the goblin and fel orc creatures' looks name races 28 and 29 (" + std::to_string(Count(extra, 1, 28)) + ", "
          + std::to_string(Count(extra, 1, 29)) + ")");

    Dbc skills;
    Check(table("SkillRaceClassInfo", skills) && Find(skills, 140) >= 0 && (skills.Get(Find(skills, 140), 2) & 2048),
          "the Worgen's bit in a game's skill row (140)");
    Dbc factions;
    long stormwind = -1, orgrimmar = -1;
    Check(table("Faction", factions) && (stormwind = Find(factions, 72)) >= 0 && (orgrimmar = Find(factions, 76)) >= 0,
          "Faction is in it");
    if (stormwind >= 0 && orgrimmar >= 0)
    {
        uint32_t sw = factions.Get(stormwind, 2) | factions.Get(stormwind, 3) | factions.Get(stormwind, 4) | factions.Get(stormwind, 5);
        uint32_t og = factions.Get(orgrimmar, 2) | factions.Get(orgrimmar, 3) | factions.Get(orgrimmar, 4) | factions.Get(orgrimmar, 5);
        Check((sw & 2048) && (og & 256), "their standing in Stormwind's and Orgrimmar's rows");
    }
    Dbc spells;
    Check(table("Spell", spells) && Find(spells, 69041) >= 0 && Find(spells, 68992) >= 0, "their racials' spells (Rocket Barrage, Darkflight)");
    // The game's own text, not mod-worgoblin's damaged copy of it.
    long charm = Find(spells, 785);
    Check(charm >= 0 && Str(spells, charm, 187).find("\r\n") != std::string::npos, "the game's spell texts kept as they are (True Fulfillment's)");

    Bytes toc, file;
    Check(game.Read("Interface\\GlueXML\\GlueXML.toc", toc), "GlueXML.toc is in it");
    std::string tocText(toc.begin(), toc.end());
    size_t strings = tocText.find("WorgenGoblinStrings.lua"), buttons = tocText.find("WorgenGoblinCreate.xml"),
           script = tocText.find("WorgenGoblinCreate.lua");
    Check(strings != std::string::npos && buttons != std::string::npos && script != std::string::npos && strings < buttons && buttons < script,
          "the screen's texts, buttons and script in its list, in that order");
    Check(game.Read("Interface\\GlueXML\\WorgenGoblinCreate.xml", file) && std::string(file.begin(), file.end()).find("WorgenGoblinRaceButton18") != std::string::npos,
          "the screen's extra buttons, up to 18");
    Check(game.Read("Interface\\GlueXML\\WorgenGoblinCreate.lua", file) && !file.empty(), "the screen's script");
    Check(game.Read("Interface\\GlueXML\\WorgenGoblinStrings.lua", file) && std::string(file.begin(), file.end()).find("RACE_INFO_WORGEN") != std::string::npos,
          "the races' texts");
    Image icons;
    Check(game.Read("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Worgoblin.blp", file) && Decode(file, icons)
          && icons.width * 4 == icons.height, "their icons, a column of four");
    Check(game.Read("Character\\Goblin\\Male\\GoblinMale.m2", file) && file.size() > 1000, "the Goblin man's model");
    Check(game.Read("Interface\\Glues\\Models\\UI_Worgen\\UI_Worgen.m2", file) && !file.empty(), "the Worgen's scene");

    // A second start: nothing changed, nothing made again.
    Check(WorgenGoblin::UpdatePatch(module, files, data, log), "a second start");
    Check(fs::last_write_time(data / "patch-U.MPQ", error) == made, "...leaves the patch as it was");

    // The other modules' changes over this patch's tables (their patches are made from the game with it in).
    if (argc > 4)
    {
        std::map<std::string, Dbc> tables;
        for (char const* name : { "ChrRaces", "CharSections", "CharHairGeosets", "CharacterFacialHairStyles", "VocalUISounds",
                                  "CreatureDisplayInfo", "CreatureModelData", "CharBaseInfo", "CharHairTextures",
                                  "EmotesTextSound", "NameGen", "CharStartOutfit", "CreatureDisplayInfoExtra", "Faction",
                                  "SkillRaceClassInfo", "SkillLineAbility", "SoundEntries", "Spell" })
        {
            Bytes b;
            game.Read(std::string("DBFilesClient\\") + name + ".dbc", b);
            tables[name].Parse(b);
        }
        for (int i = 4; i < argc; ++i)
            for (auto& [name, dbc] : tables)
            {
                fs::path changes = fs::path(argv[i]) / "dbc" / (name + ".txt");
                if (!fs::exists(changes))
                    continue;
                std::string problem = ApplyChanges(dbc, Text(changes));
                Check(problem.empty(), fs::path(argv[i]).parent_path().parent_path().filename().string() + "'s " + name + " over this patch's" + (problem.empty() ? "" : ": " + problem));
            }
        // (WG_TABLES_OUT: the tables as the game ends up reading them, for mod-allied-races'
        // tools/check_looks.py)
        if (char const* out = std::getenv("WG_TABLES_OUT"))
        {
            fs::create_directories(out);
            for (auto& [name, dbc] : tables)
            {
                Bytes b = dbc.Write();
                std::ofstream(fs::path(out) / (name + ".dbc"), std::ios::binary).write(reinterpret_cast<char const*>(b.data()), b.size());
            }
        }
        Dbc& all = tables["ChrRaces"];
        bool every = true;
        for (uint32_t id : { 9u, 12u, 13u, 14u, 15u, 16u, 17u, 18u, 22u, 23u, 24u, 25u, 26u, 27u, 28u, 29u })
            every = every && Find(all, id) >= 0;
        Check(every, "every race is there: the Goblins and Worgen, the Skyborne, the allied races, and the creatures' moved ones");
        Check(Str(all, Find(all, 9), 11) == "Goblin" && Str(all, Find(all, 12), 11) == "Worgen", "...the Goblins and Worgen still 9 and 12");
        Dbc& looks = tables["CharSections"];
        Check(Count(looks, 1, 9) + Count(looks, 1, 12) == 1642, "...their looks all still theirs");
        std::set<uint32_t> ids;
        bool unique = true;
        for (size_t row = 0; row < looks.records.size(); ++row)
            unique = ids.insert(looks.Get(row, 0)).second && unique;
        Check(unique, "...no two looks with one id");
        Dbc& sw = tables["Faction"];
        long r = Find(sw, 72);
        uint32_t m = r < 0 ? 0 : sw.Get(r, 2) | sw.Get(r, 3) | sw.Get(r, 4) | sw.Get(r, 5);
        Check((m & 2048) && (m & 16384) && (m & 4096), "...Stormwind's row with the Worgen's, the void elves' and the High Order's bits");
    }

    // The starting areas (WG_ZONE_TABLES: the module's data/zones/client): a stand-in package of a few
    // files, one a file the game has (never replaced), one another's (stored once), and the minimap
    // index's lines; the tables' rows on top of the races'.
    if (char const* zoneTables = std::getenv("WG_ZONE_TABLES"))
    {
        fs::path package = fs::temp_directory_path() / "wg-zones-test";
        fs::remove_all(package, error);
        fs::create_directories(package / "client" / "files" / "world" / "maps" / "gilneas2");
        fs::create_directories(package / "client" / "files" / "interface" / "gluexml");
        std::ofstream(package / "client" / "files" / "world" / "maps" / "gilneas2" / "gilneas2_24_33.adt") << "a tile of Gilneas";
        std::ofstream(package / "client" / "files" / "interface" / "gluexml" / "gluexml.toc") << "NOT THE GAME'S";
        std::ofstream(package / "client" / "files.txt") << "world\\maps\\gilneas2\\gilneas2_24_33.adt\n"
            << "world\\maps\\gilneas\\gilneas_24_33.adt\ninterface\\gluexml\\gluexml.toc\n";
        std::ofstream(package / "client" / "same.txt") << "world\\maps\\gilneas\\gilneas_24_33.adt\tworld\\maps\\gilneas2\\gilneas2_24_33.adt\n";
        std::ofstream(package / "client" / "minimap.txt") << "dir: Gilneas2\nGilneas2\\map24_33.blp\tcataclysm_gilneas2_map24_33.blp\n";
        std::ofstream(package / "TAG") << "cata-zones-test\n";
        size_t mapsBefore = 0, areasBefore = 0;
        {
            Game g(data, { "patch-u.mpq" });
            Bytes b;
            Dbc d;
            if (g.Read("DBFilesClient\\Map.dbc", b) && d.Parse(b))
                mapsBefore = d.records.size();
            if (g.Read("DBFilesClient\\AreaTable.dbc", b) && d.Parse(b))
                areasBefore = d.records.size();
        }
        Check(WorgenGoblin::UpdatePatch(module, files, data, log, { zoneTables, package / "client" }), "the patch with the starting areas");
        Game z(data, {});
        Bytes b;
        Check(z.Read("world\\maps\\gilneas2\\gilneas2_24_33.adt", b) && std::string(b.begin(), b.end()) == "a tile of Gilneas", "a map's tile is in it");
        Check(z.Read("world\\maps\\gilneas\\gilneas_24_33.adt", b) && std::string(b.begin(), b.end()) == "a tile of Gilneas",
              "...and a terrain swap's tile that's the same, under its own name");
        Check(z.Read("Interface\\GlueXML\\GlueXML.toc", b) && std::string(b.begin(), b.end()).find("NOT THE GAME'S") == std::string::npos,
              "a file the game has is the game's (not the package's)");
        Check(z.Read("textures\\minimap\\md5translate.trs", b) && std::string(b.begin(), b.end()).find("dir: Gilneas2") != std::string::npos,
              "the minimap index has the maps' lines");
        Dbc maps, areas, races2;
        Check(z.Read("DBFilesClient\\Map.dbc", b) && maps.Parse(b) && Find(maps, 654) >= 0 && Find(maps, 638) >= 0 && Find(maps, 648) >= 0
              && Str(maps, Find(maps, 654), 1) == "Gilneas2" && maps.records.size() == mapsBefore + 7, "the seven maps, added to the game's");
        Check(z.Read("DBFilesClient\\AreaTable.dbc", b) && areas.Parse(b) && Find(areas, 4714) >= 0 && Find(areas, 4737) >= 0
              && areas.records.size() == areasBefore + 92, "the 92 areas (Gilneas, Kezan...), added to the game's");
        Check(z.Read("DBFilesClient\\ChrRaces.dbc", b) && races2.Parse(b) && Str(races2, Find(races2, 12), 11) == "Worgen",
              "the races' changes still in");
        Check(WorgenGoblin::UpdatePatch(module, files, data, log), "without the starting areas again");
        Game n(data, {});
        Check(!n.Read("world\\maps\\gilneas2\\gilneas2_24_33.adt", b), "...their files are out");
        fs::remove_all(package, error);
    }

    std::cout << (failures ? "FAILED (" + std::to_string(failures) + ")" : std::string("PASSED")) << "\n";
    return failures ? 1 : 0;
}
