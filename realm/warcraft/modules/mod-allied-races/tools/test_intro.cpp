// SPDX-License-Identifier: GPL-3.0-or-later
// The intros' narrations, as the game finds them in the races' patch (no game or package needed):
//
//   g++ -std=c++17 -O2 -I../src -I../../mod-skyborne/src test_intro.cpp ../src/AlliedRacesPatch.cpp \
//       ../../mod-skyborne/src/SkyborneFiles.cpp -lz
//   ./a.out MODULE_DATA
//
// MODULE_DATA: the module's data/client. Makes the patch for a stand-in game (empty ChrRaces,
// CinematicSequences, CinematicCamera and SoundEntries) from the module's changes to those tables
// and its narrations, and follows each race's intro as the game does: its ChrRaces row's cinematic,
// the cinematic's camera, the camera's sound, the sound's file in the patch, which is the user's MP3
// byte for byte; the sound plays that file alone (no empty alternative with a weight). A second run
// keeps the patch.

#include "AlliedRacesPatch.h"
#include "SkyborneFiles.h"
#include <chrono>
#include <iostream>

using namespace Skyborne;

static int failures = 0;

static void Check(bool ok, std::string const& what)
{
    std::cout << (ok ? "ok   " : "FAIL ") << what << "\n";
    if (!ok)
        ++failures;
}

static Bytes ReadFile(fs::path const& path)
{
    std::ifstream in(path, std::ios::binary);
    return Bytes(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
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

int main(int argc, char** argv)
{
    if (argc != 2)
    {
        std::cerr << "test_intro MODULE_DATA\n";
        return 2;
    }
    fs::path source = argv[1];
    fs::path root = fs::temp_directory_path() / ("allied-intro-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    fs::path module = root / "module", files = root / "files", data = root / "Data";
    fs::create_directories(module / "dbc");
    fs::create_directories(files);
    fs::create_directories(data);
    struct Race { uint32_t id; char const* mp3; };
    Race const races[] = { { 15, "voidelf_intro.mp3" }, { 16, "nightborne_intro.mp3" },
                           { 17, "lightforged_intro.mp3" }, { 18, "zandalari_intro.mp3" } };
    {
        MpqWriter game(data / "common.MPQ");
        for (auto [name, fields] : { std::pair<char const*, uint32_t>{ "ChrRaces", 69 }, { "CinematicSequences", 10 },
                                     { "CinematicCamera", 7 }, { "SoundEntries", 30 } })
        {
            Dbc table;
            table.fields = fields;
            table.size = fields * 4;
            table.strings = { 0 };
            game.Add(std::string("DBFilesClient\\") + name + ".dbc", table.Write());
            fs::copy_file(source / "dbc" / (std::string(name) + ".txt"), module / "dbc" / (std::string(name) + ".txt"));
        }
        Check(game.Finish(), "the stand-in game");
    }
    for (Race const& r : races)
        fs::copy_file(source / r.mp3, module / r.mp3);
    { std::ofstream(files / "alliedraces.files") << "stand-in.bin\n"; }
    { std::ofstream(files / "stand-in.bin") << "stand-in"; }
    auto quiet = [](std::string const&) {};
    Check(AlliedRaces::UpdatePatch(module, files, data, quiet), "the patch is made");
    auto made = fs::last_write_time(data / "patch-V.MPQ");
    Check(AlliedRaces::UpdatePatch(module, files, data, quiet) && fs::last_write_time(data / "patch-V.MPQ") == made, "a second run keeps it");

    auto patch = OpenArchive(data / "patch-V.MPQ");
    auto table = [&](char const* name)
    {
        Bytes bytes;
        Dbc dbc;
        Check(patch && patch->Read(std::string("DBFilesClient\\") + name + ".dbc", bytes) && dbc.Parse(bytes), std::string(name) + " is in it");
        return dbc;
    };
    Dbc chrRaces = table("ChrRaces"), sequences = table("CinematicSequences"), cameras = table("CinematicCamera"), sounds = table("SoundEntries");
    for (Race const& r : races)
    {
        std::string who = "race " + std::to_string(r.id);
        long race = Find(chrRaces, r.id);
        long sequence = race < 0 ? -1 : Find(sequences, chrRaces.Get(race, 12));
        long camera = sequence < 0 ? -1 : Find(cameras, sequences.Get(sequence, 2));
        long sound = camera < 0 ? -1 : Find(sounds, cameras.Get(camera, 2));
        Check(sound >= 0, who + ": its cinematic, camera and sound");
        if (sound < 0)
            continue;
        std::string path = String(sounds, sound, 23) + "\\" + String(sounds, sound, 3);
        Bytes narration;
        Check(patch->Read(path, narration) && narration.size() > 1000 && narration == ReadFile(source / r.mp3),
              who + ": " + path + " in the patch is " + r.mp3);
        bool alone = sounds.Get(sound, 13) == 1;
        for (uint32_t i = 1; i < 10; ++i)
            alone = alone && sounds.Get(sound, 13 + i) == 0 && String(sounds, sound, 3 + i).empty();
        Check(alone, who + ": the sound plays that file alone");
    }
    std::error_code error;
    fs::remove_all(root, error);
    std::cout << (failures ? "FAILED (" + std::to_string(failures) + ")" : std::string("PASSED")) << "\n";
    return failures ? 1 : 0;
}
