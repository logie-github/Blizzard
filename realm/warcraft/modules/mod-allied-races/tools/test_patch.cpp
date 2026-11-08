// SPDX-License-Identifier: GPL-3.0-or-later
// The races' patch made for a game folder, and checked (no server needed):
//
//   g++ -std=c++17 -O2 -DSKYBORNE_BZIP2 -I../src -I../../mod-skyborne/src test_patch.cpp \
//       ../../mod-skyborne/src/SkyborneFiles.cpp ../src/AlliedRacesPatch.cpp -lz -lbz2
//   ./a.out MODULE_DATA FILES GAME_DATA
//
// MODULE_DATA: the module's data/client; FILES: the races' files (tools/package.py's output, with
// alliedraces.files); GAME_DATA: a client's Data folder. Makes Data/patch-V.MPQ, reads it back,
// checks the races, their looks, models, voices, spells and the character screen are in it, and
// that a second run leaves it as it is.

#include "AlliedRacesPatch.h"
#include "SkyborneFiles.h"
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>

using namespace Skyborne;

static int failures = 0;

static void Check(bool ok, std::string const& what)
{
    std::cout << (ok ? "ok   " : "FAIL ") << what << "\n";
    if (!ok)
        ++failures;
}

// A 3.3.5 camera model as the game's flybys are made (one sequence, one camera: its position,
// target and roll tracks), [duration] ms long with keys at 0, a third and the end.
static Bytes Camera(uint32_t duration, uint32_t version = 264)
{
    Bytes m(0x170 + 100 + 3 * (8 + 12), 0);
    auto put = [&](size_t at, uint32_t v) { std::memcpy(&m[at], &v, 4); };
    std::memcpy(m.data(), "MD20", 4);
    put(4, version);
    put(0x1C, 1);
    put(0x20, 0x130);
    put(0x130 + 4, duration);
    put(0x130 + 12, 0x20);
    put(0x110, 1);
    put(0x114, 0x170);
    for (uint32_t t = 0; t < 3; ++t)
    {
        size_t track = 0x170 + 16 + t * 32, list = 0x170 + 100 + t * 20;
        put(track, 0xFFFF0001);           // linear, no global sequence
        put(track + 4, 1);
        put(track + 8, static_cast<uint32_t>(list));
        put(list, 3);
        put(list + 4, static_cast<uint32_t>(list + 8));
        put(list + 8, 0);
        put(list + 12, duration / 3);
        put(list + 16, duration);
    }
    return m;
}

static uint32_t U32(Bytes const& b, size_t at)
{
    uint32_t v = 0;
    if (at + 4 <= b.size())
        std::memcpy(&v, &b[at], 4);
    return v;
}

int main(int argc, char** argv)
{
    if (argc < 4)
    {
        std::cerr << "test_patch MODULE_DATA FILES GAME_DATA\n";
        return 2;
    }
    fs::path module = argv[1], files = argv[2], data = argv[3];
    // The intros: the narrations' lengths, and a flyby made one of them.
    {
        struct { char const* file; uint32_t ms; } const narrations[] = {
            { "voidelf_intro.mp3", 46916 }, { "nightborne_intro.mp3", 38583 }, { "lightforged_intro.mp3", 37355 }, { "zandalari_intro.mp3", 53603 } };
        for (auto const& n : narrations)
        {
            std::ifstream in(module / n.file, std::ios::binary);
            Bytes mp3((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
            uint32_t ms = AlliedRaces::Mp3Milliseconds(mp3);
            Check(ms + 100 > n.ms && ms < n.ms + 100, std::string(n.file) + " is " + std::to_string(ms) + " ms long (ffprobe: " + std::to_string(n.ms) + ")");
        }
        Check(AlliedRaces::Mp3Milliseconds(Bytes(5000, 0x55)) == 0, "...and what isn't an MP3 has no length");
        Bytes camera = Camera(71667);
        Check(AlliedRaces::RetimeCamera(camera, 48416), "a flyby is made a narration's length");
        Check(U32(camera, 0x130 + 4) == 48416, "...its sequence 48416 ms (" + std::to_string(U32(camera, 0x130 + 4)) + ")");
        bool keys = true;
        for (uint32_t t = 0; t < 3; ++t)
        {
            size_t list = 0x170 + 100 + t * 20;
            keys = keys && U32(camera, list + 8) == 0 && U32(camera, list + 12) == 16139 && U32(camera, list + 16) == 48416;
        }
        Check(keys, "...its position, target and roll keys at the same places in it");
        Bytes retail = Camera(71667, 274), before = retail;
        Check(!AlliedRaces::RetimeCamera(retail, 48416) && retail == before, "...and a model of another version is left as it is");
    }

    std::error_code error;
    fs::remove(data / "patch-V.MPQ", error);
    fs::remove(data / "patch-V.MPQ.alliedraces", error);

    auto log = [](std::string const& line) { std::cout << "  " << line << "\n"; };
    Check(AlliedRaces::UpdatePatch(module, files, data, log), "the patch is made");
    auto made = fs::last_write_time(data / "patch-V.MPQ", error);
    Check(AlliedRaces::UpdatePatch(module, files, data, log), "a second start keeps it");
    Check(fs::last_write_time(data / "patch-V.MPQ", error) == made, "...without making it again");
    // Wrath Remix's realm (no allied races): the patch out of the game, kept beside it; back on
    // ChromieCraft's, it returns without being made again.
    AlliedRaces::SetPatchAside(data, log);
    Check(!fs::exists(data / "patch-V.MPQ", error) && fs::exists(data / "patch-V.MPQ.aside", error), "set aside for a realm without the races");
    Check(AlliedRaces::UpdatePatch(module, files, data, log) && fs::exists(data / "patch-V.MPQ", error) &&
          !fs::exists(data / "patch-V.MPQ.aside", error), "back for a realm with them");
    Check(fs::last_write_time(data / "patch-V.MPQ", error) == made, "...without making it again");

    auto patch = OpenArchive(data / "patch-V.MPQ");
    Bytes bytes;
    Dbc races;
    Check(patch->Read("DBFilesClient\\ChrRaces.dbc", bytes) && races.Parse(bytes), "ChrRaces.dbc is in it");
    int playable = 0, moved = 0;
    for (size_t i = 0; i < races.records.size(); ++i)
    {
        uint32_t id = races.Get(i, 0), flags = races.Get(i, 1);
        if (id >= 15 && id <= 18 && !(flags & 1))
            ++playable;
        if (id >= 24 && id <= 27)
            ++moved;
    }
    Check(playable == 4, "the void elves, the nightborne, the Lightforged Draenei and the Zandalari Trolls are playable");
    Check(moved == 4, "the Skeleton, the Vrykul, the Tuskarr and the Forest Trolls moved to 24 to 27");

    Dbc sections;
    Check(patch->Read("DBFilesClient\\CharSections.dbc", bytes) && sections.Parse(bytes), "CharSections.dbc is in it");
    std::set<uint32_t> faces[4], skins[4], hair[4];
    size_t missing = 0, checked = 0;
    for (size_t i = 0; i < sections.records.size(); ++i)
    {
        uint32_t race = sections.Get(i, 1), sex = sections.Get(i, 2), kind = sections.Get(i, 3);
        if (race < 15 || race > 18)
            continue;
        int r = int(race) - 15;
        if (kind == 0)
            skins[r].insert(sections.Get(i, 9));
        if (kind == 1)
            faces[r].insert(sections.Get(i, 8));
        if (kind == 3)
            hair[r].insert(sections.Get(i, 8));
        // every texture a row names is in the patch
        if (sex == 1 && (checked++ % 97) == 0)
            for (uint32_t field : { 4u, 5u })
            {
                uint32_t at = sections.Get(i, field);
                std::string path = at < sections.strings.size() ? reinterpret_cast<char const*>(&sections.strings[at]) : "";
                Bytes texture;
                if (!path.empty() && !patch->Read(path, texture))
                    ++missing;
            }
    }
    Check(skins[0].size() == 30 && skins[1].size() == 70 && skins[2].size() == 28 && skins[3].size() == 24,
          "the skins: 30 void elf, 70 nightborne, 28 Lightforged, 24 Zandalari (" + std::to_string(skins[0].size()) + ", " + std::to_string(skins[1].size()) + ", "
          + std::to_string(skins[2].size()) + ", " + std::to_string(skins[3].size()) + ")");
    Check(faces[0].size() == 252 && faces[1].size() == 72 && faces[2].size() == 20 && faces[3].size() == 30,
          "the faces: 252 void elf (28 x 9 eyes), 72 nightborne (12 x 6), 20 Lightforged (10 x 2), 30 Zandalari (6 x 5) (" + std::to_string(faces[0].size()) + ", "
          + std::to_string(faces[1].size()) + ", " + std::to_string(faces[2].size()) + ", " + std::to_string(faces[3].size()) + ")");
    Check(hair[0].size() >= 10 && hair[1].size() == 16 && hair[2].size() >= 10 && hair[3].size() >= 10, "the hair styles");
    Check(missing == 0, "every texture the looks name is in the patch (" + std::to_string(missing) + " missing of " + std::to_string((checked + 96) / 97) + " looked at)");

    for (char const* name : { "Character\\LightforgedDraenei\\Female\\LightforgedDraeneiFemale.m2", "Character\\ZandalariTroll\\Male\\ZandalariTrollMale00.skin",
                              "Sound\\CinematicVoices\\LightforgedDraeneiNarration.mp3", "Sound\\CinematicVoices\\ZandalariTrollNarration.mp3",
                              "Character\\VoidElf\\Female\\VoidElfFemale.m2", "Character\\VoidElf\\Female\\VoidElfFemale00.skin",
                              "Character\\VoidElf\\Male\\VoidElfMale.m2", "Character\\Nightborne\\Female\\NightborneFemale.m2",
                              "Character\\Nightborne\\Male\\NightborneMale.m2", "Character\\Nightborne\\Male\\NightborneMale00.skin",
                              "Interface\\GlueXML\\AlliedRacesCreate.lua", "Interface\\GlueXML\\AlliedRacesCreate.xml",
                              "Sound\\CinematicVoices\\VoidElfNarration.mp3", "Sound\\CinematicVoices\\NightborneNarration.mp3" })
        Check(patch->Read(name, bytes) && bytes.size() > 1000, std::string(name) + " is in it");
    // The in-game script for add-ons (Questie), where the game has its interface's file list.
    {
        Game game(data, { "patch-v.mpq", "patch-w.mpq", "patch-y.mpq", "patch-z.mpq" });
        Bytes toc;
        if (!game.Read("Interface\\FrameXML\\FrameXML.toc", toc))
            std::cout << "  (no FrameXML.toc in this game: the add-ons' script isn't added)\n";
        else
        {
            std::string theirs(toc.begin(), toc.end());
            Check(patch->Read("Interface\\FrameXML\\FrameXML.toc", bytes) && std::string(bytes.begin(), bytes.end()).rfind(theirs, 0) == 0 &&
                  std::string(bytes.begin(), bytes.end()).find("AlliedRacesAddons.lua") != std::string::npos,
                  "FrameXML.toc is the game's with AlliedRacesAddons.lua after it");
            Check(patch->Read("Interface\\FrameXML\\AlliedRacesAddons.lua", bytes) && bytes.size() > 500, "AlliedRacesAddons.lua is in it");
        }
    }

    // The intros' cameras, where the game has the flybys they're made from.
    {
        Dbc cinematics;
        Check(patch->Read("DBFilesClient\\CinematicCamera.dbc", bytes) && cinematics.Parse(bytes), "CinematicCamera.dbc is in it");
        Game game(data, { "patch-v.mpq", "patch-w.mpq", "patch-y.mpq", "patch-z.mpq" });
        Bytes stock;
        if (!game.Read("Cameras\\FlybyDraenei.m2", stock))
            std::cout << "  (no flybys in this game: the intros' cameras aren't made)\n";
        else
            for (size_t i = 0; i < cinematics.records.size(); ++i)
                if (cinematics.Get(i, 0) >= 9011 && cinematics.Get(i, 0) <= 9014)
                {
                    std::string name = reinterpret_cast<char const*>(&cinematics.strings[cinematics.Get(i, 1)]);
                    Bytes m2;
                    Check(name.rfind("Cameras\\Flyby", 0) == 0 && patch->Read(name.substr(0, name.size() - 4) + ".m2", m2) && U32(m2, U32(m2, 0x20) + 4) < 60000,
                          "intro " + std::to_string(cinematics.Get(i, 0)) + "'s camera " + name + " is in it");
                }
    }
    Check(patch->Read("Interface\\GlueXML\\GlueXML.toc", bytes) && std::string(bytes.begin(), bytes.end()).find("AlliedRacesCreate.lua") != std::string::npos,
          "GlueXML.toc lists the character screen's files");

    Dbc spells;
    Check(patch->Read("DBFilesClient\\Spell.dbc", bytes) && spells.Parse(bytes), "Spell.dbc is in it");
    int racials = 0;
    for (size_t i = 0; i < spells.records.size(); ++i)
        if (spells.Get(i, 0) >= 98711 && spells.Get(i, 0) <= 98734)
            ++racials;
    Check(racials == 24, "the twenty-four racial spells are in it (" + std::to_string(racials) + ")");

    Dbc displays, models, sounds, vocal, emotes, names;
    Check(patch->Read("DBFilesClient\\CreatureDisplayInfo.dbc", bytes) && displays.Parse(bytes), "CreatureDisplayInfo.dbc is in it");
    Check(patch->Read("DBFilesClient\\CreatureModelData.dbc", bytes) && models.Parse(bytes), "CreatureModelData.dbc is in it");
    int looks = 0, modelRows = 0;
    for (size_t i = 0; i < displays.records.size(); ++i)
        if (displays.Get(i, 0) >= 33001 && displays.Get(i, 0) <= 33008)
            ++looks;
    for (size_t i = 0; i < models.records.size(); ++i)
        if (models.Get(i, 0) >= 3601 && models.Get(i, 0) <= 3608)
            ++modelRows;
    Check(looks == 8 && modelRows == 8, "the eight looks and models");
    Check(patch->Read("DBFilesClient\\SoundEntries.dbc", bytes) && sounds.Parse(bytes), "SoundEntries.dbc is in it");
    size_t voices = 0, wavs = 0;
    for (size_t i = 0; i < sounds.records.size(); ++i)
        if (sounds.Get(i, 0) >= 910100 && sounds.Get(i, 0) < 920000)
        {
            ++voices;
            if (voices % 23 == 1)
            {
                uint32_t dir = sounds.Get(i, 23), file = sounds.Get(i, 3);
                std::string path = std::string(reinterpret_cast<char const*>(&sounds.strings[dir])) + "\\" + reinterpret_cast<char const*>(&sounds.strings[file]);
                Bytes wav;
                if (patch->Read(path, wav) && wav.size() > 400)
                    ++wavs;
                else
                    std::cout << "  no voice file " << path << "\n";
            }
        }
    Check(voices > 200 && wavs == (voices + 22) / 23, "the voices' sounds and their files (" + std::to_string(voices) + " sounds)");
    Check(patch->Read("DBFilesClient\\VocalUISounds.dbc", bytes) && vocal.Parse(bytes), "VocalUISounds.dbc is in it");
    Check(patch->Read("DBFilesClient\\EmotesTextSound.dbc", bytes) && emotes.Parse(bytes), "EmotesTextSound.dbc is in it");
    Check(patch->Read("DBFilesClient\\NameGen.dbc", bytes) && names.Parse(bytes), "NameGen.dbc is in it");
    Check(patch->Read("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races.blp", bytes) && bytes.size() > 1000, "the race icons are in it");

    std::cout << (failures ? "FAILED" : "PASSED") << " (" << failures << " failures)\n";
    return failures ? 1 : 0;
}
