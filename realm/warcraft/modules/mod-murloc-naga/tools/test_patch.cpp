// SPDX-License-Identifier: GPL-3.0-or-later
// The Murlocs' and the Naga's patch made for a game folder, and read back: the tables (the races,
// their looks, the creatures' races moved), the murlocs' model and textures (tools/murloc_model.py's,
// in ../data/files: made there first), the naga's colours, every composed texture palettized, the
// icons, the screen's files, the intros (cameras, narrations); a second start keeping it.
//
//   g++ -std=c++17 -O2 -DSKYBORNE_BZIP2 -I../src -I../../mod-skyborne/src test_patch.cpp
//       ../src/MurlocNagaPatch.cpp ../../mod-skyborne/src/SkyborneFiles.cpp -lz -lbz2 -o test_patch
//   ./test_patch ../data/client GAME_DATA [--no-textures] [--dump DIR]
//
// GAME_DATA: a client's Data folder (its archives, or folders laid out as they are). With
// --no-textures (the server's tables alone, as CI's server test has), the models, textures and
// sounds aren't checked; with --dump, the patch's naga models (their emotes merged) are written to
// DIR for tools/render_naga.py.

#include "MurlocNagaPatch.h"
#include <cmath>
#include <fstream>
#include <iterator>
#include <cstring>
#include <iostream>
#include <map>
#include <set>
#include <tuple>

using namespace MurlocNaga;
using Skyborne::Dbc;

static int failures = 0;

static void Check(bool ok, std::string const& what)
{
    std::cout << (ok ? "ok   " : "FAIL ") << what << "\n";
    if (!ok)
        ++failures;
}

static Bytes FileBytes(fs::path const& path)
{
    std::ifstream in(path, std::ios::binary);
    return Bytes(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
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
    if (argc < 3)
    {
        std::cerr << "test_patch MODULE_CLIENT GAME_DATA [--no-textures] [--dump DIR]\n";
        return 2;
    }
    fs::path module = argv[1], data = argv[2];
    bool textures = !(argc > 3 && std::string(argv[3]) == "--no-textures");
    fs::path dump;                                                    // --dump DIR: the patch's naga models written there
    for (int i = 3; i + 1 < argc; ++i)
        if (std::string(argv[i]) == "--dump")
            dump = argv[i + 1];
    std::string log;
    auto keep = [&](std::string const& line) { log += line + "\n"; std::cout << "  | " << line << "\n"; };
    fs::path patch = data / "enUS" / "patch-enUS-T.MPQ";
    std::error_code error;
    fs::remove(patch, error);
    fs::remove(fs::path(patch.string() + ".murlocnaga"), error);
    Check(UpdatePatch(module, data, keep), "the patch is made");
    Check(fs::exists(patch), "it's Data/enUS/patch-enUS-T.MPQ");
    auto archive = Skyborne::OpenArchive(patch);
    Check(archive != nullptr, "it reads as an archive");
    if (!archive)
        return 1;

    auto table = [&](std::string const& name, Dbc& dbc) { Bytes b; return archive->Read("DBFilesClient\\" + name + ".dbc", b) && dbc.Parse(b); };
    Skyborne::Game game(data, { "patch-enus-t.mpq" });                // the game without the patch
    auto str = [](Dbc const& dbc, uint32_t at) { return std::string(reinterpret_cast<char const*>(&dbc.strings[at])); };

    Dbc races;
    Check(table("ChrRaces", races), "ChrRaces is in it");
    bool murloc = false, naga = false, taunka = false, skeleton = false;
    for (size_t i = 0; i < races.records.size(); ++i)
    {
        uint32_t id = races.Get(i, 0);
        std::string file = str(races, races.Get(i, 11));
        murloc |= id == 19 && file == "Murloc" && races.Get(i, 13) == 0 && races.Get(i, 12) == 9021;
        naga |= id == 20 && file == "Naga_" && races.Get(i, 13) == 1 && races.Get(i, 4) == 17402 && races.Get(i, 12) == 9022;
        taunka |= id == 30 && file == "Taunka";
        skeleton |= id == 31 && file == "NorthrendSkeleton";
    }
    Check(murloc, "race 19 is the Murloc (Alliance, its intro)");
    Check(naga, "race 20 is the Naga (Horde, the game's naga looks, its intro)");
    Check(taunka && skeleton, "the Taunka and the Northrend Skeleton moved to 30 and 31");

    // The races' models are a player's (CreatureModelData's flag 0x4): the game draws a player as a character
    // (the composed skin, the chosen hair and features) only on such a model, otherwise as a creature, white,
    // with every geoset at once.
    Dbc models, displays;
    Check(table("CreatureModelData", models) && table("CreatureDisplayInfo", displays), "CreatureModelData and CreatureDisplayInfo are in it");
    std::map<uint32_t, uint32_t> modelFlags, displayModel;
    for (size_t i = 0; i < models.records.size(); ++i)
        modelFlags[models.Get(i, 0)] = models.Get(i, 1);
    for (size_t i = 0; i < displays.records.size(); ++i)
        displayModel[displays.Get(i, 0)] = displays.Get(i, 1);
    size_t playerModels = 0;
    for (size_t i = 0; i < races.records.size(); ++i)
        if (races.Get(i, 0) == 19 || races.Get(i, 0) == 20)
            for (uint32_t field : { 4u, 5u })
                if (auto d = displayModel.find(races.Get(i, field)); d != displayModel.end())
                    if (auto m = modelFlags.find(d->second); m != modelFlags.end() && (m->second & 0x4))
                        ++playerModels;
    Check(playerModels == 4, "the murlocs' and the naga's models are a player's, a sex each (flag 0x4: " + std::to_string(playerModels) + " of 4)");

    Dbc sections;
    Check(table("CharSections", sections), "CharSections is in it");
    size_t murlocFaces = 0, nagaSkins = 0, nagaNew = 0, movedRows = 0, leftAt19 = 0;
    for (size_t i = 0; i < sections.records.size(); ++i)
    {
        uint32_t race = sections.Get(i, 1), kind = sections.Get(i, 3), colour = sections.Get(i, 9);
        std::string tex = str(sections, sections.Get(i, 4));
        if (race == 19 && kind == 1 && tex.find("Character\\Murloc\\") == 0)
            ++murlocFaces;
        if (race == 20 && kind == 0)
            ++nagaSkins;
        if (race == 20 && kind == 0 && colour >= 5)
            ++nagaNew;
        if (race == 30 || race == 31)
            ++movedRows;
        if ((race == 19 || race == 20) && tex.find("Character\\Murloc\\") != 0 && tex.find("Character\\Naga_\\") != 0 && !tex.empty())
            ++leftAt19;
    }
    Check(murlocFaces == 16 * 13 * 2, "the murlocs' faces: 16 eye colours for each of 13 skins, a sex (" + std::to_string(murlocFaces) + ")");
    Check(nagaSkins == 18, "the naga's skins: 9 a sex (" + std::to_string(nagaSkins) + ")");
    Check(nagaNew == 8, "the naga's new colours: 4 a sex (" + std::to_string(nagaNew) + ")");
    Check(leftAt19 == 0, "no creature's look left at races 19 and 20 (" + std::to_string(leftAt19) + ")");
    std::cout << "     (" << movedRows << " looks of the creatures moved to 30 and 31)\n";

    for (char const* name : { "CharBaseInfo", "CharHairGeosets", "CharacterFacialHairStyles", "CharStartOutfit", "CinematicCamera",
                              "CinematicSequences", "CreatureDisplayInfo", "CreatureModelData", "Faction", "GameObjectDisplayInfo",
                              "Item", "NameGen", "SoundEntries", "Spell" })
    {
        Dbc t;
        Check(table(name, t), std::string(name) + " is in it");
    }

    Bytes toc;
    Check(archive->Read("Interface\\GlueXML\\GlueXML.toc", toc) && std::string(toc.begin(), toc.end()).find("MurlocNagaCreate.lua") != std::string::npos,
        "the creation screen's file list has theirs");
    Bytes lua;
    Check(archive->Read("Interface\\GlueXML\\MurlocNagaCreate.lua", lua) && !lua.empty(), "their screen code is in it");
    for (char const* camera : { "Cameras\\FlybyMurloc.m2", "Cameras\\FlybyNaga.m2", "Cameras\\FlybyNaga00.skin" })
    {
        Bytes c;
        Check(archive->Read(camera, c) && !c.empty(), std::string("the intro's ") + camera);
    }

    if (textures)
    {
        // The murlocs' model and textures: tools/murloc_model.py's (data/files), in the patch.
        Bytes model;
        Check(archive->Read("Character\\Murloc\\Male\\MurlocMale.m2", model), "the murlocs' model (men)");
        Bytes female;
        Check(archive->Read("Character\\Murloc\\Female\\MurlocFemale.m2", female), "the murlocs' model (women)");
        Bytes skin;
        Check(archive->Read("Character\\Murloc\\Male\\MurlocMale00.skin", skin), "its 00.skin");
        if (model.size() > 0x130)
        {
            uint32_t count = U32(model, 0x50), at = U32(model, 0x54);
            bool extra = false, composed = false, hair = false;
            for (uint32_t i = 0; i < count; ++i)
            {
                extra |= U32(model, at + i * 16) == 8;
                composed |= U32(model, at + i * 16) == 1;
                hair |= U32(model, at + i * 16) == 6;
            }
            Check(!extra && composed && hair, "its body and eyes the composed texture, its fins the hair's (no skin \"extra\": the game draws none for it)");
        }
        // Its geosets: the body (0), the fin styles (2..7), the features (102..; none is 101, which it hasn't).
        for (auto [sex, features] : { std::pair<char const*, int>{ "Male", 5 }, { "Female", 7 } })
        {
            Bytes s;
            std::set<uint16_t> geosets;
            if (archive->Read(std::string("Character\\Murloc\\") + sex + "\\Murloc" + sex + "00.skin", s) && s.size() > 48)
                for (uint32_t i = 0, n = U32(s, 28), at = U32(s, 32); i < n && at + i * 48 + 2 <= s.size(); ++i)
                {
                    uint16_t g;
                    std::memcpy(&g, &s[at + i * 48], 2);
                    geosets.insert(g);
                }
            std::set<uint16_t> want = { 0 };
            for (int f = 2; f <= 7; ++f)
                want.insert(uint16_t(f));
            for (int f = 1; f <= features; ++f)
                want.insert(uint16_t(101 + f));
            Check(geosets == want, std::string("the murloc's geosets (") + sex + "): its body, 6 fin styles, " + std::to_string(features) + " features");
        }
        for (char const* name : { "Character\\Murloc\\MurlocFins00.blp", "Character\\Murloc\\MurlocFins15.blp",
                                  "Character\\Murloc\\MurlocFinsClassic07.blp", "Character\\Murloc\\MurlocFinsSail15.blp" })
        {
            Bytes t;
            Check(archive->Read(name, t) && t.size() > 4, name);
        }
        // The naga's headdresses and outfits (tools/naga_parts.py's, in ../data/files), added to the
        // client's naga: their geosets (hair styles 2.., features 102..) in its skin, its own kept.
        for (auto [sex, hairs, features] : { std::tuple<char const*, int, int>{ "Male", 2, 7 }, { "Female", 1, 4 } })
        {
            std::string base = std::string("Character\\Naga_\\") + sex + "\\Naga_" + sex;
            Bytes m2, skin;
            bool read = archive->Read(base + ".m2", m2) && archive->Read(base + "00.skin", skin) && skin.size() > 48;
            std::set<uint16_t> geosets;
            if (read)
                for (uint32_t i = 0, n = U32(skin, 28), at = U32(skin, 32); i < n && at + i * 48 + 2 <= skin.size(); ++i)
                {
                    uint16_t g;
                    std::memcpy(&g, &skin[at + i * 48], 2);
                    geosets.insert(g);
                }
            bool all = read && geosets.count(0) && geosets.count(802);
            for (int h = 1; h <= hairs; ++h)
                all = all && geosets.count(uint16_t(h + 1));
            for (int f = 1; f <= features; ++f)
                all = all && geosets.count(uint16_t(101 + f));
            Check(all, base + ".m2: its own geosets, " + std::to_string(hairs) + " headdresses and " + std::to_string(features) + " outfits");
        }
        // The naga's emotes (tools/naga_emotes.py's, in ../data/files), added to the client's naga as
        // sequences of its own: every track with an entry for each, the look-up finding each id, an
        // alias pointing at its sequence, and the merge doing nothing a second time.
        for (char const* sex : { "Male", "Female" })
        {
            std::string base = std::string("Character\\Naga_\\") + sex + "\\Naga_" + sex;
            Bytes m2;
            bool read = archive->Read(base + ".m2", m2) && m2.size() > 0x130;
            uint32_t count = U32(m2, 0x1C), at = U32(m2, 0x20), lookupCount = U32(m2, 0x24), lookupAt = U32(m2, 0x28);
            std::map<uint16_t, uint32_t> first;
            bool lookupOk = read, aliasesOk = read;
            for (uint32_t k = 0; read && k < count; ++k)
            {
                uint16_t id, variation, alias;
                std::memcpy(&id, &m2[at + k * 64], 2);
                std::memcpy(&variation, &m2[at + k * 64 + 2], 2);
                std::memcpy(&alias, &m2[at + k * 64 + 62], 2);
                first.emplace(id, k);
                // (an alias's chain ends at a sequence of its own: the game's own female naga has one alias of another)
                for (int step = 0; step < 4 && alias < count && (U32(m2, at + k * 64 + 12) & 0x40); ++step)
                {
                    bool more = U32(m2, at + alias * 64 + 12) & 0x40;
                    if (!more)
                        break;
                    std::memcpy(&alias, &m2[at + alias * 64 + 62], 2);
                }
                if (U32(m2, at + k * 64 + 12) & 0x40)
                    aliasesOk = aliasesOk && alias < count && !(U32(m2, at + alias * 64 + 12) & 0x40);
            }
            for (auto const& [id, k] : first)
            {
                int16_t v = -1;
                if (id < lookupCount)
                    std::memcpy(&v, &m2[lookupAt + id * 2], 2);
                lookupOk = lookupOk && v == int16_t(k);
            }
            bool emotes = read;
            for (uint16_t id : { 66, 67, 68, 64, 65, 70, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 69, 61, 73, 113, 185, 186, 195,
                                 114, 115, 116, 96, 97, 98, 91, 99, 100, 101, 209, 210 })
                emotes = emotes && first.count(id);
            Check(emotes, base + ".m2: the emotes (bow, wave, cheer, talk, laugh, kneel, cry, point, salute, dance...), sitting, riding, sleeping");
            Check(lookupOk && aliasesOk, base + ".m2: its sequences' look-up finds each, every alias its sequence (" + std::to_string(count) + " sequences)");
            size_t bad = 0, tracks = 0;
            for (uint32_t b = 0, n = U32(m2, 0x2C), o = U32(m2, 0x30); read && b < n; ++b)
                for (int t = 0; t < 3; ++t)
                {
                    size_t tr = o + b * 88 + 16 + t * 20;
                    int16_t gseq;
                    std::memcpy(&gseq, &m2[tr + 2], 2);
                    uint32_t tn = U32(m2, tr + 4), vn = U32(m2, tr + 12);
                    if (gseq >= 0 || tn == 0)
                        continue;
                    ++tracks;
                    bad += tn != count || vn != count;
                }
            Check(read && bad == 0, base + ".m2: each of its bones' " + std::to_string(tracks) + " animated tracks has an entry for every sequence");
            if (!dump.empty())                                       // (for tools/render_naga.py emotes)
            {
                Bytes skin;
                archive->Read(base + "00.skin", skin);
                fs::create_directories(dump);
                std::ofstream(dump / (std::string("Naga_") + sex + ".m2"), std::ios::binary).write(reinterpret_cast<char const*>(m2.data()), m2.size());
                std::ofstream(dump / (std::string("Naga_") + sex + "00.skin"), std::ios::binary).write(reinterpret_cast<char const*>(skin.data()), skin.size());
            }
            Bytes again = m2, emotesDat =FileBytes(module.parent_path() / "files" / "Character" / "Naga_" / sex / (std::string("Naga") + sex + "Emotes.dat"));
            std::string why;
            size_t added = 99;
            Check(MergeEmotes(again, emotesDat, why, &added) && added == 0 && again == m2, base + ".m2: merging the emotes again adds nothing (" + why + ")");
        }
        // The naga's story's voices (tools/naga_voices.py's, in ../data/files) and their SoundEntries rows.
        Dbc soundEntries;
        size_t voiceRows = 0, voiceFiles = 0;
        if (table("SoundEntries", soundEntries))
            for (size_t i = 0; i < soundEntries.records.size(); ++i)
            {
                uint32_t id = soundEntries.Get(i, 0);
                if (id < 995000 || id > 995199)
                    continue;
                ++voiceRows;
                std::string file = str(soundEntries, soundEntries.Get(i, 3)), folder = str(soundEntries, soundEntries.Get(i, 23));
                Bytes wav;
                if (folder == "Sound\\Creature\\WC3Voices" && archive->Read(folder + "\\" + file, wav) && wav.size() > 44
                    && std::memcmp(wav.data(), "RIFF", 4) == 0 && U32(wav, 20) == (1u | (1u << 16)) && U32(wav, 24) == 22050 && (U32(wav, 32) >> 16) == 16)
                    ++voiceFiles;
            }
        Check(voiceRows == 82, "the naga's story's voices: 82 SoundEntries rows (" + std::to_string(voiceRows) + ")");
        Check(voiceFiles == 82, "each one's WAV in the patch, 16-bit PCM, mono, 22,050 Hz (" + std::to_string(voiceFiles) + ")");
        // The naga's story's models (tools/naga_models.py's): 3.3.5's, their skins, every animation kept
        // in its own file there, every texture their looks name.
        for (auto [name, folder] : { std::pair<char const*, char const*>{ "SeaWitch", "Creature\\SeaWitch\\" },
                                     { "Warden", "Creature\\Warden\\" }, { "QueenAzshara", "Creature\\QueenAzshara\\" } })
        {
            Bytes m2, skin;
            bool ok = archive->Read(std::string(folder) + name + ".m2", m2) && m2.size() > 0x130 && std::memcmp(m2.data(), "MD20", 4) == 0
                && U32(m2, 4) == 264 && archive->Read(std::string(folder) + name + "00.skin", skin) && std::memcmp(skin.data(), "SKIN", 4) == 0;
            size_t anims = 0, missing = 0, newer = 0;
            for (uint32_t k = 0, n = U32(m2, 0x1C), at = U32(m2, 0x20); ok && k < n; ++k)
            {
                uint16_t id, variation;
                std::memcpy(&id, &m2[at + k * 64], 2);
                std::memcpy(&variation, &m2[at + k * 64 + 2], 2);
                newer += id > 505;
                if (U32(m2, at + k * 64 + 12) & 0x20)
                    continue;
                char file[96];
                std::snprintf(file, sizeof(file), "%s%s%04u-%02u.anim", folder, name, unsigned(id), unsigned(variation));
                Bytes anim;
                ++anims;
                missing += !archive->Read(file, anim) || anim.empty();
            }
            for (uint32_t i = 0, n = U32(m2, 0x50), at = U32(m2, 0x54); ok && i < n; ++i)
            {
                if (U32(m2, at + i * 16) != 0)
                    continue;
                std::string tex(reinterpret_cast<char const*>(&m2[U32(m2, at + i * 16 + 12)]));
                Bytes t;
                missing += !archive->Read(tex, t);
            }
            Check(ok && missing == 0 && newer == 0, std::string(folder) + name + ".m2: 3.3.5's, its skin, its textures, its "
                + std::to_string(anims) + " animations in their own files, no animation 3.3.5 hasn't (" + std::to_string(missing) + " missing)");
        }
        size_t looksOk = 0, looks = 0;
        for (size_t i = 0; i < displays.records.size(); ++i)
        {
            uint32_t id = displays.Get(i, 0), model = displays.Get(i, 1);
            if (id < 40000 || id > 40299 || model < 3800 || model > 3849)
                continue;
            ++looks;
            std::string modelName;
            for (size_t j = 0; j < models.records.size(); ++j)
                if (models.Get(j, 0) == model)
                    modelName = str(models, models.Get(j, 2));
            std::string folder = modelName.substr(0, modelName.rfind('\\') + 1);
            bool ok = !modelName.empty();
            for (uint32_t f : { 6u, 7u, 8u })
            {
                std::string skinName = str(displays, displays.Get(i, f));
                Bytes t;
                if (!skinName.empty())
                    ok = ok && archive->Read(folder + skinName + ".blp", t);
            }
            looksOk += ok;
        }
        Check(looks == 6 && looksOk == looks, "the converted models' 6 looks, every skin they name in the patch (" + std::to_string(looksOk) + ")");
        Dbc extras;
        size_t extraRows = 0;
        if (table("CreatureDisplayInfoExtra", extras))
            for (size_t i = 0; i < extras.records.size(); ++i)
                extraRows += extras.Get(i, 0) >= 25000 && extras.Get(i, 0) <= 25099 && extras.Get(i, 1) > 0;
        Check(extraRows == 8, "the looks of the game's parts: 8 CreatureDisplayInfoExtra rows (" + std::to_string(extraRows) + ")");
        // What the game draws into the composed texture: palettized (its compositing reads only those)
        // at the skin's scale (the stand-in is the HD look's: a 512 skin).
        auto composited = [&](std::string const& name, uint32_t w, uint32_t h)
        {
            Bytes t;
            Skyborne::Image image;
            bool ok = archive->Read(name, t) && t.size() > 12 && t[8] == 1 && Skyborne::Decode(t, image) && image.width == w && image.height == h;
            Check(ok, name + " (palettized, " + std::to_string(w) + " x " + std::to_string(h) + ")");
        };
        composited("Character\\Murloc\\MurlocBase.blp", 512, 512);
        for (int c : { 0, 12 })
        {
            char name[96];
            std::snprintf(name, sizeof(name), "Character\\Murloc\\MurlocBody%02d.blp", c);
            composited(name, 256, 128);
            for (int f : { 0, 15 })
            {
                std::snprintf(name, sizeof(name), "Character\\Murloc\\MurlocEyes%02d_%02d.blp", f, c);
                composited(name, 256, 64);
            }
        }
        for (char const* sex : { "Male", "Female" })
            for (int c : { 0, 4, 5, 8 })
            {
                std::string p = std::string("Character\\Naga_\\") + sex + "\\Naga_" + sex;
                char colour[8];
                std::snprintf(colour, sizeof(colour), "00_%02d", c);
                composited(p + "FaceLower" + colour + ".blp", 256, 128);
                composited(p + "FaceUpper" + colour + ".blp", 256, 64);
                composited(p + "NakedPelvisSkin" + colour + ".blp", 256, 128);
                composited(p + "NakedTorsoSkin" + colour + ".blp", 256, 128);
            }
        for (char const* name : { "Character\\Naga_\\Male\\Naga_MaleSkin00_05.blp", "Character\\Naga_\\Male\\Naga_MaleSkin00_08_Extra.blp" })
            composited(name, 512, 512);
        // Every texture the races' rows name is in the game or the patch (the game draws a missing one
        // green): the naga's hair and facial hair textures the game hasn't are left out.
        size_t missing = 0;
        for (size_t i = 0; i < sections.records.size(); ++i)
        {
            uint32_t race = sections.Get(i, 1);
            if (race != 19 && race != 20)
                continue;
            for (uint32_t f : { 4u, 5u, 6u })
            {
                std::string tex = str(sections, sections.Get(i, f));
                Bytes t;
                if (!tex.empty() && !archive->Read(tex, t) && !game.Has(tex))
                {
                    std::cout << "     missing: " << tex << "\n";
                    ++missing;
                }
            }
        }
        Check(missing == 0, "every texture the races' looks name is there (" + std::to_string(missing) + " missing)");
        // (the naga's: Lady Vashj's six lines to about 45 s, then the client's own ocean, horn and siren hiss,
        // which a stand-in game may not have: the mix ends with the last sound the game has)
        for (auto [name, least] : { std::pair<char const*, double>{ "Sound\\CinematicVoices\\NagaNarration.wav", 44.0 },
                                    std::pair<char const*, double>{ "Sound\\CinematicVoices\\MurlocNarration.wav", 39.0 } })
        {
            Bytes wav;
            bool ok = archive->Read(name, wav) && wav.size() > 44;
            double seconds = ok ? (wav.size() - 44) / 44100.0 : 0;
            Check(ok && seconds >= least, std::string(name) + " (" + std::to_string(seconds) + " s)");
        }
        Bytes icons;
        Skyborne::Image sheet;
        Check(archive->Read("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MurlocNaga.blp", icons) && Skyborne::Decode(icons, sheet)
            && sheet.width == 64 && sheet.height == 256, "their icons");
    }

    // A second start: nothing changed, the patch kept as it is.
    auto before = fs::last_write_time(patch);
    archive.reset();
    log.clear();
    Check(UpdatePatch(module, data, keep) && fs::last_write_time(patch) == before && log.empty(), "a second start keeps it");

    std::cout << (failures ? std::to_string(failures) + " FAILED" : "all passed") << "\n";
    return failures ? 1 : 0;
}
