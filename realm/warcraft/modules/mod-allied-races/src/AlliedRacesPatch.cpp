// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The void elves' and the nightborne's patch for the game (mod-allied-races). The game needs
 * its tables to know the two races (ChrRaces, CharSections, CharHairGeosets... with their rows:
 * the module's data/client/dbc, made by tools/build_data.py), their models, textures and voices
 * (Blizzard's own of today, made 3.3.5's by tools/package.py as the server was packaged: never in
 * this repository), their place on the character creation screen (Interface/GlueXML/
 * AlliedRacesCreate.*, their portraits in the race icons) and their intros' narration.
 *
 * It's Data/patch-V.MPQ: read after the HD looks' patches (whose character tables it builds on)
 * and before Wrath Remix's patch-Y.MPQ and the Skyborne's patch-Z.MPQ, which read the client with
 * this patch in it and so carry its rows in the tables they write (CharSections among them).
 *
 * The archive reading and writing, the tables and the textures are the Skyborne's (SkyborneFiles).
 */

#include "AlliedRacesPatch.h"
#include "../../mod-skyborne/src/SkyborneFiles.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <set>
#include <sstream>

namespace AlliedRaces
{
    using Skyborne::Bytes;
    using Skyborne::Dbc;
    using Skyborne::Game;
    using Skyborne::Image;
    using Skyborne::MpqWriter;

    namespace
    {
        constexpr char const* PATCH = "patch-V.MPQ";
        constexpr char const* MARK = "patch-V.MPQ.alliedraces";
        constexpr char const* ASIDE = "patch-V.MPQ.aside";          // the patch kept out of the game (SetPatchAside)
        constexpr char const* MANIFEST = "alliedraces.files";
        constexpr char const* VERSION = "allied-races-13";   // 13: the Lightforged men's forehead and crest; 12: the Lightforged's runes drawn as their glyphs; 11: the Zandalari in the Orcs' scene (3.3.5 has no troll scene); 10: the intros' cameras their narrations' length, the races for Questie; 2: the models' bone combos name the vertices' bones; 3: the body parts of groups 3.3.5 doesn't know in geoset 0; 4: the meshes within 65535 indices, the tentacles on the feature slider; 5: the Lightforged Draenei and the Zandalari Trolls; 6: the narrations and voices in the game's MP3 format, the nightborne in the night elves' scene; 8: the character tables in the order the game reads them; 7: the models their kin's height, the animations' own files whole, the void elves and Zandalari in their kin's scenes; 9: the creatures' races moved in the client's own rows (their facial hair and voice rows too), the voices' rows clear of the Skyborne's, the narrations one file each, the selection screen's music

        Bytes ReadFile(fs::path const& path)
        {
            std::ifstream in(path, std::ios::binary);
            return Bytes(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
        }

        std::string Text(fs::path const& path)
        {
            Bytes b = ReadFile(path);
            return std::string(b.begin(), b.end());
        }

        // FNV-1a: what the patch is made from, to know when to make it again.
        struct Stamp
        {
            uint64_t value = 1469598103934665603ull;
            void Add(std::string const& text)
            {
                for (unsigned char c : text)
                {
                    value ^= c;
                    value *= 1099511628211ull;
                }
                value ^= 0xFF;
                value *= 1099511628211ull;
            }
            std::string Hex() const
            {
                char buf[17];
                std::snprintf(buf, sizeof(buf), "%016llx", static_cast<unsigned long long>(value));
                return buf;
            }
        };

        fs::path LocalPath(fs::path const& root, std::string const& gamePath)
        {
            std::string p = gamePath;
            std::replace(p.begin(), p.end(), '\\', '/');
            return root / p;
        }

        // The portrait [icon] (any size) into cell ([column], [row]) of the icon sheet [sheet]
        // (8 a row, 4 rows), scaled with bilinear sampling.
        void Paint(Image& sheet, Image const& icon, uint32_t column, uint32_t row)
        {
            uint32_t cell = sheet.width / 8;
            for (uint32_t y = 0; y < cell; ++y)
                for (uint32_t x = 0; x < cell; ++x)
                {
                    double sx = (x + 0.5) * icon.width / cell - 0.5, sy = (y + 0.5) * icon.height / cell - 0.5;
                    int x0 = int(std::floor(sx)), y0 = int(std::floor(sy));
                    double fx = sx - x0, fy = sy - y0;
                    auto at = [&](int px, int py, int c) -> double
                    {
                        px = std::clamp(px, 0, int(icon.width) - 1);
                        py = std::clamp(py, 0, int(icon.height) - 1);
                        return icon.rgba[(size_t(py) * icon.width + px) * 4 + c];
                    };
                    uint8_t* out = &sheet.rgba[(size_t(row * cell + y) * sheet.width + column * cell + x) * 4];
                    for (int c = 0; c < 3; ++c)
                    {
                        double v = at(x0, y0, c) * (1 - fx) * (1 - fy) + at(x0 + 1, y0, c) * fx * (1 - fy)
                            + at(x0, y0 + 1, c) * (1 - fx) * fy + at(x0 + 1, y0 + 1, c) * fx * fy;
                        out[c] = uint8_t(std::clamp(v + 0.5, 0.0, 255.0));
                    }
                    out[3] = 255;
                }
        }

        // The races' portraits painted into the icon sheet's free columns (the game's ten races have
        // columns 0 to 4; the Skyborne's have 6): void elves and nightborne in the last (7), the
        // Lightforged Draenei and Zandalari Trolls in 5, the Alliance's in rows 0 (men) and 2 (women),
        // the Horde's in 1 and 3.
        bool AlliedIcons(Bytes& blp, fs::path const& icons, std::vector<std::string>& problems)
        {
            Image sheet;
            if (!Skyborne::Decode(blp, sheet) || sheet.width < 64 || sheet.height < 32 || sheet.width != sheet.height * 2)
                return false;
            struct Portrait { char const* file; uint32_t column, row; };
            for (Portrait const& p : { Portrait{ "voidelf_male.blp", 7, 0 }, Portrait{ "nightborne_male.blp", 7, 1 },
                                       Portrait{ "voidelf_female.blp", 7, 2 }, Portrait{ "nightborne_female.blp", 7, 3 },
                                       Portrait{ "lightforged_male.blp", 5, 0 }, Portrait{ "zandalari_male.blp", 5, 1 },
                                       Portrait{ "lightforged_female.blp", 5, 2 }, Portrait{ "zandalari_female.blp", 5, 3 } })
            {
                Image icon;
                if (!Skyborne::Decode(ReadFile(icons / p.file), icon))
                {
                    problems.push_back(std::string("the portrait ") + p.file + " couldn't be read");
                    continue;
                }
                Paint(sheet, icon, p.column, p.row);
            }
            blp = Skyborne::EncodeDxt5(sheet);
            return true;
        }
    }

    uint32_t Mp3Milliseconds(Bytes const& mp3)
    {
        static uint16_t const MPEG1[16] = { 0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0 };
        static uint16_t const MPEG2[16] = { 0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0 };
        static uint32_t const RATES[3] = { 44100, 48000, 32000 };
        size_t at = 0;
        if (mp3.size() >= 10 && std::memcmp(mp3.data(), "ID3", 3) == 0)   // (a tag first: its size is seven bits a byte)
            at = 10 + ((mp3[6] & 0x7F) << 21 | (mp3[7] & 0x7F) << 14 | (mp3[8] & 0x7F) << 7 | (mp3[9] & 0x7F));
        double seconds = 0;
        uint32_t frames = 0;
        while (at + 4 <= mp3.size())
        {
            uint8_t const* h = &mp3[at];
            uint32_t version = (h[1] >> 3) & 3, layer = (h[1] >> 1) & 3, bitrate = h[2] >> 4, rate = (h[2] >> 2) & 3;
            // layer III frames (the narrations' and the game's): MPEG 1 (version 3), 2 (2) or 2.5 (0)
            if (h[0] != 0xFF || (h[1] & 0xE0) != 0xE0 || version == 1 || layer != 1 || bitrate == 0 || bitrate == 15 || rate == 3)
            {
                ++at;   // not a frame's start: on to the next
                continue;
            }
            bool one = version == 3;
            uint32_t hz = RATES[rate] >> (one ? 0 : version == 2 ? 1 : 2);
            uint32_t kbps = (one ? MPEG1 : MPEG2)[bitrate];
            uint32_t samples = one ? 1152 : 576;
            at += samples / 8 * kbps * 1000 / hz + ((h[2] >> 1) & 1);
            seconds += double(samples) / hz;
            ++frames;
        }
        return frames ? static_cast<uint32_t>(std::lround(seconds * 1000)) : 0;
    }

    bool RetimeCamera(Bytes& m2, uint32_t ms)
    {
        auto u32 = [&](size_t at) { uint32_t v = 0; if (at + 4 <= m2.size()) std::memcpy(&v, &m2[at], 4); return v; };
        auto fits = [&](uint64_t at, uint64_t bytes) { return at + bytes <= m2.size(); };
        if (ms == 0 || m2.size() < 0x130 || std::memcmp(m2.data(), "MD20", 4) != 0 || u32(4) != 264)
            return false;
        uint32_t sequences = u32(0x1C), sequencesAt = u32(0x20);
        if (sequences == 0 || sequences > 16 || !fits(sequencesAt, uint64_t(sequences) * 64))
            return false;
        uint32_t longest = 0;
        for (uint32_t i = 0; i < sequences; ++i)
        {
            if (!(u32(sequencesAt + i * 64 + 12) & 0x20))   // (its keys in another file, a .anim: not a camera's)
                return false;
            longest = std::max(longest, u32(sequencesAt + i * 64 + 4));
        }
        if (longest == 0)
            return false;
        double factor = double(ms) / longest;
        auto scaled = [&](uint32_t t) { return static_cast<uint32_t>(std::lround(t * factor)); };

        // The tracks: a camera's position, target and roll (3.3.5's camera: type, field of view, far
        // and near clip, then the three tracks with their bases: 100 bytes), a bone's translation,
        // rotation and scale (88 bytes). Each checked before anything changes.
        std::vector<size_t> tracks;
        uint32_t cameras = u32(0x110), camerasAt = u32(0x114), bones = u32(0x2C), bonesAt = u32(0x30);
        if (cameras == 0 || cameras > 16 || !fits(camerasAt, uint64_t(cameras) * 100) || bones > 256 || !fits(bonesAt, uint64_t(bones) * 88))
            return false;
        for (uint32_t i = 0; i < cameras; ++i)
            for (uint32_t at : { 16u, 48u, 80u })
                tracks.push_back(camerasAt + i * 100 + at);
        for (uint32_t i = 0; i < bones; ++i)
            for (uint32_t at : { 16u, 36u, 56u })
                tracks.push_back(bonesAt + i * 88 + at);
        std::set<uint32_t> keys;   // the timestamps' lists, each changed once
        for (size_t track : tracks)
        {
            uint16_t interpolation = static_cast<uint16_t>(u32(track) & 0xFFFF);
            int16_t loop = static_cast<int16_t>(u32(track) >> 16);
            uint32_t lists = u32(track + 4), listsAt = u32(track + 8);
            if (interpolation > 3 || lists > sequences || !fits(listsAt, uint64_t(lists) * 8))
                return false;
            if (loop != -1)   // (on a global sequence: its own time)
                continue;
            for (uint32_t l = 0; l < lists; ++l)
            {
                uint32_t n = u32(listsAt + l * 8), at = u32(listsAt + l * 8 + 4);
                if (n == 0)
                    continue;
                if (n > 4096 || !fits(at, uint64_t(n) * 4))
                    return false;
                uint32_t previous = 0;
                for (uint32_t k = 0; k < n; ++k)
                {
                    uint32_t t = u32(at + k * 4);
                    if (t < previous || t > longest)
                        return false;
                    previous = t;
                }
                keys.insert(at);
            }
        }
        Bytes out = m2;
        auto put = [&](size_t at, uint32_t v) { std::memcpy(&out[at], &v, 4); };
        for (size_t track : tracks)
        {
            if (static_cast<int16_t>(u32(track) >> 16) != -1)
                continue;
            uint32_t lists = u32(track + 4), listsAt = u32(track + 8);
            for (uint32_t l = 0; l < lists; ++l)
            {
                uint32_t n = u32(listsAt + l * 8), at = u32(listsAt + l * 8 + 4);
                if (n == 0 || !keys.erase(at))
                    continue;
                for (uint32_t k = 0; k < n; ++k)
                    put(at + k * 4, scaled(u32(at + k * 4)));
            }
        }
        for (uint32_t i = 0; i < sequences; ++i)
            put(sequencesAt + i * 64 + 4, scaled(u32(sequencesAt + i * 64 + 4)));
        m2.swap(out);
        return true;
    }

    namespace
    {
        // The intros: each race's camera (data/client/dbc/CinematicCamera.txt: its start race's
        // flyby) made the length of its narration and a moment more, as its own camera
        // (Cameras\FlybyVoidElf.m2...): the game's flybys run 69 to 77 seconds, the narrations 37 to
        // 54, and the scene went on in silence. A flyby the game hasn't, or this can't read, stays
        // the stock one, at its own length.
        constexpr uint32_t AFTER_NARRATION = 1500;   // ms
        struct Intro { uint32_t camera; char const* race; char const* narration; };
        Intro const INTROS[] = {
            { 9011, "VoidElf", "voidelf_intro.mp3" },
            { 9012, "Nightborne", "nightborne_intro.mp3" },
            { 9013, "LightforgedDraenei", "lightforged_intro.mp3" },
            { 9014, "ZandalariTroll", "zandalari_intro.mp3" },
        };

        size_t Intros(Game const& game, Dbc& cameras, fs::path const& moduleData, MpqWriter& writer, std::vector<std::string>& problems)
        {
            size_t made = 0;
            for (Intro const& intro : INTROS)
            {
                size_t row = 0;
                while (row < cameras.records.size() && cameras.Get(row, 0) != intro.camera)
                    ++row;
                uint32_t at = row < cameras.records.size() ? cameras.Get(row, 1) : uint32_t(cameras.strings.size());
                if (at >= cameras.strings.size())
                {
                    problems.push_back("intro " + std::to_string(intro.camera) + ": no camera row");
                    continue;
                }
                std::string stock(reinterpret_cast<char const*>(&cameras.strings[at]));   // Cameras\FlybyDraenei.mdx
                std::string base = stock.substr(0, stock.rfind('.'));
                std::string ours = std::string("Cameras\\Flyby") + intro.race;
                uint32_t ms = Mp3Milliseconds(ReadFile(moduleData / intro.narration));
                Bytes m2, skin;
                if (!game.Read(base + ".m2", m2) || ms == 0 || !RetimeCamera(m2, ms + AFTER_NARRATION))
                {
                    problems.push_back(std::string(intro.race) + "'s intro: " + stock + " left at its own length (not in the game, or not a camera this reads)");
                    continue;
                }
                uint32_t views = 0;
                std::memcpy(&views, &m2[0x44], 4);
                if (views && !game.Read(base + "00.skin", skin))
                {
                    problems.push_back(std::string(intro.race) + "'s intro: " + base + "00.skin isn't in the game; " + stock + " left at its own length");
                    continue;
                }
                writer.Add(ours + ".m2", m2);
                if (views)
                    writer.Add(ours + "00.skin", skin);
                cameras.Set(row, 1, cameras.String(ours + ".mdx"));
                ++made;
            }
            return made;
        }
    }

    void RemovePatch(fs::path const& clientData, std::function<void(std::string const&)> const& log)
    {
        std::error_code error;
        if (!fs::exists(clientData / MARK, error))
            return;
        fs::remove(clientData / PATCH, error);
        fs::remove(clientData / ASIDE, error);
        fs::remove(clientData / MARK, error);
        log("The races' patch is out of the game");
    }

    void SetPatchAside(fs::path const& clientData, std::function<void(std::string const&)> const& log)
    {
        std::error_code error;
        if (!fs::exists(clientData / MARK, error) || !fs::exists(clientData / PATCH, error))
            return;
        fs::remove(clientData / ASIDE, error);
        fs::rename(clientData / PATCH, clientData / ASIDE, error);
        if (error)
            log("The races' patch couldn't be set aside: " + error.message());
        else
            log("The races' patch is out of the game, kept beside it for a realm with the races");
    }

    bool UpdatePatch(fs::path const& moduleData, fs::path const& files, fs::path const& clientData, std::function<void(std::string const&)> const& log)
    {
        std::error_code error;
        fs::path patch = clientData / PATCH, mark = clientData / MARK;
        bool ours = fs::exists(mark, error);
        if (!ours && fs::exists(patch, error))
        {
            log(patch.string() + " isn't this module's: left alone, so the game won't know the races");
            return false;
        }
        // (one set aside for a realm without the races comes back, and is made again only if it's old)
        if (ours && !fs::exists(patch, error) && fs::exists(clientData / ASIDE, error))
            fs::rename(clientData / ASIDE, patch, error);
        auto start = std::chrono::steady_clock::now();
        // (Wrath Remix's patches are its realm's alone, its language folder's too: made from the game as
        // Remix last started, and taken out on ChromieCraft's after this is made, so not read for it)
        Game game(clientData, { "patch-v.mpq", "patch-w.mpq", "patch-y.mpq", "patch-z.mpq", "patch-enus-y.mpq", "patch-engb-y.mpq", "patch-dede-y.mpq",
            "patch-frfr-y.mpq", "patch-eses-y.mpq", "patch-esmx-y.mpq", "patch-ruru-y.mpq", "patch-kokr-y.mpq", "patch-zhcn-y.mpq", "patch-zhtw-y.mpq",
            // (the Brill home's patch: the language folder's V, read after patch-V)
            "patch-enus-v.mpq", "patch-engb-v.mpq", "patch-dede-v.mpq", "patch-frfr-v.mpq", "patch-eses-v.mpq", "patch-esmx-v.mpq", "patch-ruru-v.mpq", "patch-kokr-v.mpq", "patch-zhcn-v.mpq", "patch-zhtw-v.mpq",
            // (Ralia's mod's patch: the language folder's Z, made from the game with this one in)
            "patch-enus-z.mpq", "patch-engb-z.mpq", "patch-dede-z.mpq", "patch-frfr-z.mpq", "patch-eses-z.mpq", "patch-esmx-z.mpq", "patch-ruru-z.mpq", "patch-kokr-z.mpq", "patch-zhcn-z.mpq", "patch-zhtw-z.mpq" });
        if (game.archives.empty())
        {
            log("No game in " + clientData.string());
            return false;
        }
        std::string manifest = Text(files / MANIFEST);
        if (manifest.empty())
        {
            log("The races' models, textures and voices aren't in " + files.string() + " (no " + MANIFEST + "): the patch isn't made");
            RemovePatch(clientData, log);
            return false;
        }

        // What it's made from: the module's files, the package's (by name and size) and the game's archives.
        Stamp stamp;
        stamp.Add(VERSION);
        stamp.Add(game.Describe());
        std::vector<fs::path> moduleFiles;
        for (auto it = fs::recursive_directory_iterator(moduleData, error); !error && it != fs::recursive_directory_iterator(); it.increment(error))
            if (it->is_regular_file(error))
                moduleFiles.push_back(it->path());
        std::sort(moduleFiles.begin(), moduleFiles.end());
        for (auto const& f : moduleFiles)
        {
            stamp.Add(f.lexically_relative(moduleData).generic_string());
            stamp.Add(Text(f));
        }
        std::vector<std::string> listed;
        {
            std::istringstream in(manifest);
            std::string line;
            while (std::getline(in, line))
            {
                if (!line.empty() && line.back() == '\r')
                    line.pop_back();
                if (!line.empty())
                    listed.push_back(line);
            }
        }
        for (std::string const& name : listed)
        {
            stamp.Add(name);
            stamp.Add(std::to_string(fs::file_size(LocalPath(files, name), error)));
        }
        if (ours && fs::exists(patch, error) && Text(mark) == stamp.Hex() + "\n")
            return true;

        log("Making the races' patch for the game (" + patch.string() + ")");
        fs::path part = patch;
        part += ".part";
        MpqWriter writer(part);
        size_t tables = 0, packed = 0, missing = 0;
        std::vector<std::string> problems;

        // The races' files: models, textures, voices.
        for (std::string const& name : listed)
        {
            Bytes data = ReadFile(LocalPath(files, name));
            if (data.empty())
            {
                ++missing;
                continue;
            }
            writer.Add(name, data);
            ++packed;
        }
        if (missing)
            problems.push_back(std::to_string(missing) + " of the races' files aren't in " + files.string());

        // Tables.
        for (auto it = fs::directory_iterator(moduleData / "dbc", error); !error && it != fs::directory_iterator(); it.increment(error))
        {
            if (it->path().extension() != ".txt")
                continue;
            std::string name = it->path().stem().string();
            Bytes data;
            Dbc dbc;
            if (!game.Read("DBFilesClient\\" + name + ".dbc", data) || !dbc.Parse(data))
            {
                problems.push_back(name + ".dbc isn't in the game");
                continue;
            }
            std::string problem = Skyborne::ApplyChanges(dbc, Text(it->path()));
            if (!problem.empty())
            {
                problems.push_back(name + ".dbc: " + problem);
                continue;
            }
            if (name == "CinematicCamera")
                packed += Intros(game, dbc, moduleData, writer, problems);
            SortCharacterTable(dbc, name);
            writer.Add("DBFilesClient\\" + name + ".dbc", dbc.Write());
            ++tables;
        }

        // The character creation screen: the race icons, the screen's own file list with theirs.
        for (char const* icons : { "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races.blp",
                                   "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound.blp" })
        {
            Bytes data;
            if (game.Read(icons, data) && AlliedIcons(data, moduleData / "icons", problems))
                writer.Add(icons, data);
            else
                problems.push_back(std::string(icons) + ": no race icons to add theirs to");
        }
        Bytes toc;
        if (game.Read("Interface\\GlueXML\\GlueXML.toc", toc))
        {
            std::string text(toc.begin(), toc.end());
            if (text.find("AlliedRacesCreate.xml") == std::string::npos)
            {
                if (!text.empty() && text.back() != '\n')
                    text += "\r\n";
                text += "AlliedRacesCreate.xml\r\nAlliedRacesCreate.lua\r\n";
            }
            writer.Add("Interface\\GlueXML\\GlueXML.toc", Bytes(text.begin(), text.end()));
            for (char const* name : { "AlliedRacesCreate.xml", "AlliedRacesCreate.lua" })
                writer.Add(std::string("Interface\\GlueXML\\") + name, ReadFile(moduleData / "Interface" / "GlueXML" / name));
        }
        else
            problems.push_back("GlueXML.toc isn't in the game: the character screen won't show them");
        // The in-game interface: the races for add-ons with tables of the races of their own (Questie's).
        Bytes frameToc;
        if (game.Read("Interface\\FrameXML\\FrameXML.toc", frameToc))
        {
            std::string text(frameToc.begin(), frameToc.end());
            if (text.find("AlliedRacesAddons.lua") == std::string::npos)
            {
                if (!text.empty() && text.back() != '\n')
                    text += "\r\n";
                text += "AlliedRacesAddons.lua\r\n";
            }
            writer.Add("Interface\\FrameXML\\FrameXML.toc", Bytes(text.begin(), text.end()));
            writer.Add("Interface\\FrameXML\\AlliedRacesAddons.lua", ReadFile(moduleData / "Interface" / "FrameXML" / "AlliedRacesAddons.lua"));
        }
        else
            problems.push_back("FrameXML.toc isn't in the game: add-ons such as Questie won't know the races");
        // The intros' narration (the user's, data/client/*_intro.mp3), where the game's sound table has it.
        writer.Add("Sound\\CinematicVoices\\VoidElfNarration.mp3", ReadFile(moduleData / "voidelf_intro.mp3"));
        writer.Add("Sound\\CinematicVoices\\NightborneNarration.mp3", ReadFile(moduleData / "nightborne_intro.mp3"));
        writer.Add("Sound\\CinematicVoices\\LightforgedDraeneiNarration.mp3", ReadFile(moduleData / "lightforged_intro.mp3"));
        writer.Add("Sound\\CinematicVoices\\ZandalariTrollNarration.mp3", ReadFile(moduleData / "zandalari_intro.mp3"));

        if (!writer.Finish())
        {
            fs::remove(part, error);
            log("Couldn't write " + part.string());
            return false;
        }
        fs::rename(part, patch, error);
        if (error)
        {
            fs::remove(part, error);
            log("Couldn't put " + patch.string() + " in place: " + error.message());
            return false;
        }
        {
            std::ofstream out(mark, std::ios::trunc);
            out << stamp.Hex() << "\n";
        }
        for (auto const& p : problems)
            log("  " + p);
        auto seconds = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start).count();
        log("The races' patch is in the game: " + std::to_string(tables) + " tables, " + std::to_string(packed) + " files ("
            + std::to_string(seconds) + " s)");
        return true;
    }
}
