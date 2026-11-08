// SPDX-License-Identifier: GPL-3.0-or-later
// The creatures' races moved out of the new races' places, in a client's own rows (no game needed):
//
//   g++ -std=c++17 -O2 -I../src test_table_moves.cpp ../src/SkyborneFiles.cpp -lz
//   ./a.out SKYBORNE_DATA ALLIED_RACES_DATA
//
// SKYBORNE_DATA, ALLIED_RACES_DATA: the two modules' data/client. Each module's table changes are
// applied to stand-in tables laid out the way an HD look's may be: a moved race's row at an id of
// its own, and at the id the server's table gives a moved race's row, another creature's. The moved
// race's rows take the new race with everything else of theirs (texture names too), the other
// creature's row is left as it is, the client's own race row (its own display) is copied to the new
// race, and no race and sex of the new races has a facial hair style or a voice twice.

#include "SkyborneFiles.h"
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

static std::string Text(fs::path const& path)
{
    std::ifstream in(path, std::ios::binary);
    return std::string(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
}

static Dbc Table(uint32_t fields)
{
    Dbc table;
    table.fields = fields;
    table.size = fields * 4;
    table.strings = { 0 };
    return table;
}

static Bytes Row(Dbc& table, std::initializer_list<uint32_t> values)
{
    Bytes record(table.size, 0);
    uint32_t i = 0;
    for (uint32_t v : values)
    {
        for (int k = 0; k < 4; ++k)
            record[i * 4 + k] = uint8_t(v >> (8 * k));
        ++i;
    }
    table.records.push_back(record);
    return record;
}

static long Find(Dbc const& table, uint32_t id)
{
    for (size_t i = 0; i < table.records.size(); ++i)
        if (table.Get(i, 0) == id)
            return long(i);
    return -1;
}

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cerr << "test_table_moves SKYBORNE_DATA ALLIED_RACES_DATA\n";
        return 2;
    }
    struct Module
    {
        char const* name;
        fs::path dbc;
        std::map<uint32_t, uint32_t> moved;     // the creatures' race -> where it goes
        uint32_t sections, geosets, extra;      // the server's ids of a moved race's rows (CharSections, CharHairGeosets, CreatureDisplayInfoExtra)
    };
    for (Module const& m : { Module{ "the Skyborne", fs::path(argv[1]) / "dbc", { { 13, 22 }, { 14, 23 } }, 6223, 247, 11676 },
                             Module{ "the allied races", fs::path(argv[2]) / "dbc", { { 15, 24 }, { 16, 25 }, { 17, 26 }, { 18, 27 } }, 6259, 298, 12424 } })
    {
        uint32_t old = m.moved.begin()->first, now = m.moved.begin()->second;
        auto apply = [&](Dbc& table, char const* name)
        {
            std::string problem = ApplyChanges(table, Text(m.dbc / (std::string(name) + ".txt")));
            Check(problem.empty(), std::string(m.name) + ": " + name + "'s changes apply" + (problem.empty() ? "" : ": " + problem));
        };

        // CharSections, CharHairGeosets, CreatureDisplayInfoExtra: the race in field 1.
        for (auto [name, fields, server] : { std::make_tuple("CharSections", 10u, m.sections),
                                             std::make_tuple("CharHairGeosets", 6u, m.geosets),
                                             std::make_tuple("CreatureDisplayInfoExtra", 21u, m.extra) })
        {
            Dbc table = Table(fields);
            uint32_t texture = table.String("Character\\HD\\Creature.blp");
            Bytes other = Row(table, { server, 5, 0, 0, texture });         // another creature's row at the server's id
            Bytes own = Row(table, { 80001, old, 1, 0, texture });          // the moved race's row at an id of the client's own
            apply(table, name);
            long o = Find(table, server), w = Find(table, 80001);
            Check(o >= 0 && table.records[o] == other, std::string(m.name) + ": " + name + ": the row at the server's id that isn't the moved race's is left as it is");
            Bytes expect = own;
            for (int k = 0; k < 4; ++k)
                expect[4 + k] = uint8_t(now >> (8 * k));
            Check(w >= 0 && table.records[w] == expect, std::string(m.name) + ": " + name + ": the moved race's own row takes the new race, the rest of it kept");
        }

        // ChrRaces: the client's own row of the moved race (its own looks) copied to the new race.
        {
            Dbc races = Table(69);
            Row(races, { old, 0, 0, 0, 76543, 76544 });
            apply(races, "ChrRaces");
            long w = Find(races, now);
            Check(w >= 0 && races.Get(w, 4) == 76543 && races.Get(w, 5) == 76544, std::string(m.name) + ": ChrRaces: the moved race keeps the client's own looks");
        }

        // CharacterFacialHairStyles (race, sex, variation and its geosets) and VocalUISounds (id,
        // the moment, race, the sounds): no race and sex of theirs twice.
        {
            Dbc beards = Table(8);
            for (auto const& [from, to] : m.moved)
                for (uint32_t sex = 0; sex < 2; ++sex)
                    Row(beards, { from, sex, 0, 0, 0, 0, 0, 0xC0FFEE });   // (a mark of the creatures' own)
            apply(beards, "CharacterFacialHairStyles");
            std::set<std::tuple<uint32_t, uint32_t, uint32_t>> seen;
            bool twice = false, moved = true;
            for (size_t i = 0; i < beards.records.size(); ++i)
            {
                twice |= !seen.emplace(beards.Get(i, 0), beards.Get(i, 1), beards.Get(i, 2)).second;
                if (beards.Get(i, 7) == 0xC0FFEE)
                    moved &= m.moved.count(beards.Get(i, 0)) == 0;
            }
            Check(!twice, std::string(m.name) + ": CharacterFacialHairStyles: each race, sex and style once");
            Check(moved, std::string(m.name) + ": CharacterFacialHairStyles: the creatures' styles moved with their race");
        }
        {
            Dbc voices = Table(7);
            Row(voices, { 848, 0, old, 0, 0 });                              // the game's own: the moved race's, no sounds
            apply(voices, "VocalUISounds");
            std::set<std::pair<uint32_t, uint32_t>> seen;
            bool twice = false;
            for (size_t i = 0; i < voices.records.size(); ++i)
                twice |= !seen.emplace(voices.Get(i, 2), voices.Get(i, 1)).second;
            long w = Find(voices, 848);
            Check(w >= 0 && voices.Get(w, 2) == now, std::string(m.name) + ": VocalUISounds: the creature's row moved with its race");
            Check(!twice, std::string(m.name) + ": VocalUISounds: each race and moment once");
        }
    }
    std::cout << (failures ? "FAILED (" + std::to_string(failures) + ")" : std::string("PASSED")) << "\n";
    return failures ? 1 : 0;
}
