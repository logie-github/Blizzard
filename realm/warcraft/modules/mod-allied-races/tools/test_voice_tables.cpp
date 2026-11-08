// SPDX-License-Identifier: GPL-3.0-or-later
// The races' voices with the Skyborne's patch after theirs, as the game reads them (no game needed):
//
//   g++ -std=c++17 -O2 -I../../mod-skyborne/src test_voice_tables.cpp ../../mod-skyborne/src/SkyborneFiles.cpp -lz
//   ./a.out ALLIED_RACES_DATA SKYBORNE_DATA
//
// ALLIED_RACES_DATA, SKYBORNE_DATA: the two modules' data/client. Their SoundEntries, VocalUISounds
// and EmotesTextSound changes are applied in the game's order (this module's patch-V, then the
// Skyborne's patch-Z, made from the tables with patch-V's rows in) to stand-in tables with a game's
// own row. Every race's words at the UI's moments and its emotes come out as each module made them
// (the same sounds, their files and weights), no moment twice, the game's own rows untouched; each of
// the four races has its 49 moments of today and the two 3.3.5 has twice.

#include "SkyborneFiles.h"
#include <array>
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

static Dbc Table(uint32_t fields)
{
    Dbc table;
    table.fields = fields;
    table.size = fields * 4;
    table.strings = { 0 };
    return table;
}

// A table's changes applied, and the table written and read back: the next patch reads it so.
static void Apply(Dbc& table, fs::path const& changes)
{
    std::string problem = ApplyChanges(table, Text(changes));
    Check(problem.empty(), changes.string() + " applies" + (problem.empty() ? "" : ": " + problem));
    Dbc back;
    back.Parse(table.Write());
    table = std::move(back);
}

static long Find(Dbc const& table, uint32_t id)
{
    for (size_t i = 0; i < table.records.size(); ++i)
        if (table.Get(i, 0) == id)
            return long(i);
    return -1;
}

static std::string String(Dbc const& table, size_t row, uint32_t field)
{
    uint32_t at = table.Get(row, field);
    return at < table.strings.size() ? std::string(reinterpret_cast<char const*>(&table.strings[at])) : "?";
}

// A sound row as the game plays it: its type, files, their weights, folder.
static std::string Sound(Dbc const& table, uint32_t id)
{
    long row = Find(table, id);
    if (row < 0)
        return "(none)";
    std::string out = std::to_string(table.Get(row, 1));
    for (uint32_t i = 0; i < 10; ++i)
        out += "|" + String(table, row, 3 + i) + ":" + std::to_string(table.Get(row, 13 + i));
    return out + "|" + String(table, row, 23);
}

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cerr << "test_voice_tables ALLIED_RACES_DATA SKYBORNE_DATA\n";
        return 2;
    }
    fs::path allied = fs::path(argv[1]) / "dbc", skyborne = fs::path(argv[2]) / "dbc";

    // The game's own: the blood elves' "inventory full" (the Skyborne's voices are the blood elves').
    Dbc sounds = Table(30), voices = Table(7), emotes = Table(5);
    for (uint32_t id : { 9549u, 9550u })
    {
        sounds.records.emplace_back(sounds.size, 0);
        sounds.Set(sounds.records.size() - 1, 0, id);
        sounds.Set(sounds.records.size() - 1, 1, 12);
        sounds.Set(sounds.records.size() - 1, 3, sounds.String(id == 9549 ? "BloodElfMale_InventoryFull.wav" : "BloodElfFemale_InventoryFull.wav"));
        sounds.Set(sounds.records.size() - 1, 13, 1);
        sounds.Set(sounds.records.size() - 1, 23, sounds.String("Sound\\Character\\BloodElf"));
    }
    voices.records.emplace_back(voices.size, 0);
    for (auto [field, value] : { std::pair<uint32_t, uint32_t>{ 0, 742 }, { 1, 0 }, { 2, 10 }, { 3, 9549 }, { 4, 9550 } })
        voices.Set(0, field, value);
    Bytes gameVoice = voices.records[0], gameSound = sounds.records[0];

    // Each module's own, alone: what its rows are to come out as.
    struct Own { fs::path dbc; Dbc sounds, voices, emotes; };
    std::array<Own, 2> owners = { Own{ allied, sounds, Table(7), Table(5) }, Own{ skyborne, sounds, Table(7), Table(5) } };
    for (Own& o : owners)
    {
        Apply(o.sounds, o.dbc / "SoundEntries.txt");
        Apply(o.voices, o.dbc / "VocalUISounds.txt");
        Apply(o.emotes, o.dbc / "EmotesTextSound.txt");
    }
    // Both, in the game's order.
    for (fs::path const& dbc : { allied, skyborne })
    {
        Apply(sounds, dbc / "SoundEntries.txt");
        Apply(voices, dbc / "VocalUISounds.txt");
        Apply(emotes, dbc / "EmotesTextSound.txt");
    }
    Check(voices.records[Find(voices, 742)] == gameVoice && sounds.records[Find(sounds, 9549)] == gameSound, "the game's own voice rows untouched");

    std::map<std::pair<uint32_t, uint32_t>, size_t> byMoment;      // (race, moment) -> row
    bool twice = false;
    for (size_t i = 0; i < voices.records.size(); ++i)
        twice |= !byMoment.emplace(std::make_pair(voices.Get(i, 2), voices.Get(i, 1)), i).second;
    Check(!twice, "no race has a moment twice");
    std::map<uint32_t, size_t> count;
    for (Own const& o : owners)
    {
        size_t wrong = 0;
        for (size_t i = 0; i < o.voices.records.size(); ++i)
        {
            uint32_t race = o.voices.Get(i, 2), moment = o.voices.Get(i, 1);
            auto it = byMoment.find({ race, moment });
            ++count[race];
            if (it == byMoment.end())
            {
                ++wrong;
                continue;
            }
            for (uint32_t sex = 0; sex < 2; ++sex)
            {
                uint32_t mine = o.voices.Get(i, 3 + sex), now = voices.Get(it->second, 3 + sex);
                if (mine != now || (mine && Sound(sounds, now) != Sound(o.sounds, mine)))
                    ++wrong;
            }
        }
        Check(wrong == 0, o.dbc.parent_path().parent_path().filename().string() + ": every race's words at the UI's moments as the module made them (" + std::to_string(wrong) + " not)");
    }
    for (uint32_t race : { 15u, 16u, 17u, 18u })
    {
        Check(count[race] == 51, "race " + std::to_string(race) + ": 49 moments and the two 3.3.5 has twice (" + std::to_string(count[race]) + ")");
        for (auto [twin, moment] : { std::pair<uint32_t, uint32_t>{ 6, 47 }, { 66, 11 } })
        {
            auto a = byMoment.find({ race, twin }), b = byMoment.find({ race, moment });
            Check(a != byMoment.end() && b != byMoment.end() && voices.Get(a->second, 3) == voices.Get(b->second, 3)
                  && voices.Get(a->second, 4) == voices.Get(b->second, 4),
                  "race " + std::to_string(race) + ": moment " + std::to_string(twin) + " sounds as " + std::to_string(moment));
        }
    }
    for (uint32_t race : { 13u, 14u, 15u, 16u, 17u, 18u })
    {
        auto it = byMoment.find({ race, 0 });
        Check(it != byMoment.end() && voices.Get(it->second, 3) && voices.Get(it->second, 4), "race " + std::to_string(race) + ": \"inventory full\" for both sexes");
    }

    // The emotes: each module's rows as it made them (the same row, the same sound), and no race,
    // sex and emote of one module's given by the other's.
    std::array<std::set<std::array<uint32_t, 3>>, 2> keys;
    size_t wrong = 0;
    for (size_t k = 0; k < owners.size(); ++k)
        for (size_t i = 0; i < owners[k].emotes.records.size(); ++i)
        {
            Dbc const& mine = owners[k].emotes;
            keys[k].insert({ mine.Get(i, 1), mine.Get(i, 2), mine.Get(i, 3) });
            long row = Find(emotes, mine.Get(i, 0));
            if (row < 0 || emotes.records[row] != mine.records[i] || Sound(sounds, mine.Get(i, 4)) != Sound(owners[k].sounds, mine.Get(i, 4)))
                ++wrong;
        }
    Check(wrong == 0, "every emote's row and sound as its module made it (" + std::to_string(wrong) + " not)");
    bool shared = false;
    for (auto const& key : keys[0])
        shared |= keys[1].count(key) > 0;
    Check(!shared, "no race, sex and emote in both modules' rows");
    std::cout << (failures ? "FAILED (" + std::to_string(failures) + ")" : std::string("PASSED")) << "\n";
    return failures ? 1 : 0;
}
