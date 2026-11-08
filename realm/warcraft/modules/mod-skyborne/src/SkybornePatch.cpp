// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Skyborne's patch for the game. They're races the game doesn't have, on the blood elf's body:
 * the game needs its tables to know them (ChrRaces, CharSections... with their rows: the module's
 * data/client/dbc, made by tools/build_data.py), their blue skins, new hair colours and blue or
 * yellow eyes (textures made from the blood elf's, data/client/textures.txt), their place on the
 * character creation screen (Interface/GlueXML/SkyborneCreate.*, the race icons), and their intro's
 * narration. The textures are the game's own, so the patch is made on the phone from the client's
 * files: as the realm starts, when the client or the module changed since.
 *
 * It's Data/patch-Z.MPQ, read after every other patch (HD looks' character tables included: its
 * tables are those with the Skyborne's rows added). Wrath Remix's patch-Y.MPQ changes other tables.
 *
 * It also carries mod-ralia's character textures (Ralia's mod or Alternate Female Options: the paths its
 * Data/<locale>/patch-<locale>-Z.MPQ lists beside it, read from the game with that patch in), so a
 * set's textures win over the HD look's and the race modules' Data patches whichever the game reads
 * last: in the game the Data folder's patches won over the language folder's. And mod-brill-home's Corn
 * (his coat at the path of the game's pug's own, listed beside its Data/<locale>/patch-<locale>-V.MPQ),
 * so an HD look's pug coat (the Alternative HD Patch's patch-F) can't hide his.
 */

#include "SkybornePatch.h"
#include "SkyborneFiles.h"
#include "../../mod-base-model/src/BodyPreview.h"
#include <algorithm>
#include <cctype>
#include <chrono>
#include <map>
#include <set>
#include <tuple>
#include <cstdio>
#include <sstream>

namespace Skyborne
{
    namespace
    {
        constexpr char const* VERSION = "skyborne-16";   // 15: the creatures' races moved in the client's own rows (their beards and voice rows too), the selection screen's music

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

        std::string Extra(std::string const& path)
        {
            if (path.size() < 4)
                return "";
            return path.substr(0, path.size() - 4) + "_Extra" + path.substr(path.size() - 4);
        }

        std::string Lower(std::string text)
        {
            for (char& c : text)
                c = char(std::tolower(static_cast<unsigned char>(c)));
            return text;
        }

        // CharSections' section 4 rows stay, with no textures, as the game's own rows for race 20 have.
        void EmptyOverlayRows(Dbc& dbc)
        {
            if (dbc.fields < 10)
                return;
            for (size_t row = 0; row < dbc.records.size(); ++row)
                if (dbc.Get(row, 3) == 4)
                    for (uint32_t field : { 4u, 5u, 6u })
                        dbc.Set(row, field, dbc.String(""));
        }

        // A skin the game gives only its NPCs (the face painted into it) has no face or overlay rows:
        // the game always draws such an NPC from a texture baked beforehand. A look the game puts
        // together itself (Wrath Remix's Moratari in her dress and in her tent: her own skin, no baked
        // texture) asks for those rows, and the game fails without them. Every NPC skin gets a face
        // row for each face its race and sex have, and an overlay row, with no textures (as the
        // overlays' are): the skin's own face shows.
        // A race and sex's skin colours can have gaps below the highest (the Skyborne's, between the blood
        // elf's skins and their blues; colours the server's tables have and some HD looks' tables
        // haven't), and the character creation screen reads a colour's row by its number as the race
        // changes: a colour with no row is a missing row's texture read. Every colour below a race and
        // sex's highest gets a row: an NPC's skin (flag 8, as the game's own colours between), its first
        // player skin's textures; CompleteSkins gives it its faces and overlay.
        void FillSkinHoles(Dbc& dbc)
        {
            if (dbc.fields < 10 || dbc.size != dbc.fields * 4)
                return;
            using Who = std::pair<uint32_t, uint32_t>;                      // race, sex
            std::map<Who, std::set<uint32_t>> colours;
            std::map<Who, std::pair<uint32_t, size_t>> first;               // its lowest player skin: colour, row
            uint32_t next = 0;
            for (size_t row = 0; row < dbc.records.size(); ++row)
            {
                next = std::max(next, dbc.Get(row, 0) + 1);
                if (dbc.Get(row, 3) != 0)
                    continue;
                Who who{ dbc.Get(row, 1), dbc.Get(row, 2) };
                uint32_t colour = dbc.Get(row, 9), flags = dbc.Get(row, 7);
                colours[who].insert(colour);
                if ((flags & 1) && !(flags & 4) && (!first.count(who) || colour < first[who].first))
                    first[who] = { colour, row };
            }
            for (auto const& [who, has] : colours)
            {
                auto source = first.find(who);
                if (source == first.end() || has.empty())
                    continue;
                for (uint32_t colour = 0; colour < *has.rbegin(); ++colour)
                {
                    if (has.count(colour))
                        continue;
                    Bytes record = dbc.records[source->second.second];
                    dbc.records.push_back(record);
                    size_t row = dbc.records.size() - 1;
                    dbc.Set(row, 0, next++);
                    dbc.Set(row, 7, 8);
                    dbc.Set(row, 8, 0);
                    dbc.Set(row, 9, colour);
                }
            }
        }

        void CompleteSkins(Dbc& dbc)
        {
            if (dbc.fields < 10 || dbc.size != dbc.fields * 4)
                return;
            using Who = std::pair<uint32_t, uint32_t>;                      // race, sex
            using Colour = std::tuple<uint32_t, uint32_t, uint32_t>;        // race, sex, skin colour
            std::map<Who, std::set<uint32_t>> faces;
            std::set<Who> overlays;
            std::map<Colour, std::set<uint32_t>> facesOf;
            std::set<Colour> overlaid;
            std::map<Colour, uint32_t> skins;                               // a skin colour: its row's flags
            uint32_t next = 0;
            for (size_t row = 0; row < dbc.records.size(); ++row)
            {
                uint32_t race = dbc.Get(row, 1), sex = dbc.Get(row, 2), section = dbc.Get(row, 3);
                uint32_t variation = dbc.Get(row, 8), colour = dbc.Get(row, 9);
                next = std::max(next, dbc.Get(row, 0) + 1);
                if (section == 0)
                    skins[{ race, sex, colour }] = dbc.Get(row, 7);
                else if (section == 1)
                {
                    faces[{ race, sex }].insert(variation);
                    facesOf[{ race, sex, colour }].insert(variation);
                }
                else if (section == 4)
                {
                    overlays.insert({ race, sex });
                    overlaid.insert({ race, sex, colour });
                }
            }
            uint32_t none = dbc.String("");
            auto add = [&](uint32_t race, uint32_t sex, uint32_t section, uint32_t flags, uint32_t variation, uint32_t colour)
            {
                dbc.records.emplace_back(dbc.size, 0);
                size_t row = dbc.records.size() - 1;
                for (uint32_t field : { 4u, 5u, 6u })
                    dbc.Set(row, field, none);
                dbc.Set(row, 0, next++);
                dbc.Set(row, 1, race);
                dbc.Set(row, 2, sex);
                dbc.Set(row, 3, section);
                dbc.Set(row, 7, flags);
                dbc.Set(row, 8, variation);
                dbc.Set(row, 9, colour);
            };
            for (auto const& [skin, flags] : skins)
            {
                // (only the NPCs': a skin a player can choose, flag 1, keeps the faces it has)
                if (flags & 1)
                    continue;
                auto [race, sex, colour] = skin;
                std::set<uint32_t> const& has = facesOf[skin];
                for (uint32_t face : faces[{ race, sex }])
                    if (!has.count(face))
                        add(race, sex, 1, flags, face, colour);
                if (overlays.count({ race, sex }) && !overlaid.count(skin))
                    add(race, sex, 4, flags, 0, colour);
            }
        }

        // HD looks (blood elves' among them) give a skin a second texture, <skin>_Extra.blp, with the
        // ears, jaw and eyes: CharSections' second texture of the skin's row. The rows put here come
        // from the server's tables, which haven't it: a skin row without one gets its _Extra where the
        // game or the patch has it, or the ears and eyes keep another skin's colours.
        void AddExtraSkins(Dbc& dbc, Game const& game, std::set<std::string> const& made)
        {
            if (dbc.fields < 10)
                return;
            auto text = [&](uint32_t at) { return at < dbc.strings.size() ? std::string(reinterpret_cast<char const*>(&dbc.strings[at])) : std::string(); };
            for (size_t row = 0; row < dbc.records.size(); ++row)
            {
                if (dbc.Get(row, 3) != 0 || !text(dbc.Get(row, 5)).empty())
                    continue;
                std::string skin = text(dbc.Get(row, 4));
                std::string extra = Extra(skin);
                if (extra.empty())
                    continue;
                Bytes data;
                if (made.count(Lower(extra)) || game.Read(extra, data))
                    dbc.Set(row, 5, dbc.String(extra));
            }
        }
    }

    void RemovePatch(fs::path const& clientData, std::function<void(std::string const&)> const& log)
    {
        std::error_code error;
        if (!fs::exists(clientData / MARK, error))
            return;
        fs::remove(clientData / PATCH, error);
        fs::remove(clientData / MARK, error);
        log("The Skyborne's patch is out of the game");
    }

    bool UpdatePatch(fs::path const& moduleData, fs::path const& clientData, std::function<void(std::string const&)> const& log, bool femaleBodyPreview)
    {
        std::error_code error;
        fs::path patch = clientData / PATCH, mark = clientData / MARK;
        bool ours = fs::exists(mark, error);
        if (!ours && fs::exists(patch, error))
        {
            log(patch.string() + " isn't the Skyborne's: left alone, so the game won't know them");
            return false;
        }
        auto start = std::chrono::steady_clock::now();
        Game game(clientData, { "patch-z.mpq", "patch-y.mpq" });
        if (game.archives.empty())
        {
            log("No game in " + clientData.string());
            return false;
        }

        // What it's made from: the module's files and the game's archives.
        Stamp stamp;
        stamp.Add(VERSION);
        // (-2: the outfits' slots emptied with -1, the game's own empty slot, issue #119)
        stamp.Add(femaleBodyPreview ? "female-body-preview-2" : "dressed-preview");
        stamp.Add(game.Describe());
        // mod-ralia's textures and mod-brill-home's Corn, when their patches are in (each one's mark and its
        // list beside it): Data/<locale>/patch-<locale>-Z.MPQ (.ralia) and -V.MPQ (.brillhome).
        auto listed = [&](char const* letter, char const* markSuffix, char const* name)
        {
            std::vector<std::string> paths;
            if (game.locale.empty())
                return paths;
            fs::path other = clientData / game.locale / ("patch-" + game.locale + "-" + letter + ".MPQ");
            fs::path otherMark = other, otherList = other;
            otherMark += markSuffix;
            otherList += ".files";
            if (fs::exists(other, error) && fs::exists(otherMark, error) && fs::exists(otherList, error))
            {
                std::string list = Text(otherList);
                stamp.Add(name);
                stamp.Add(list);
                std::istringstream lines(list);
                for (std::string path; std::getline(lines, path);)
                {
                    if (!path.empty() && path.back() == '\r')
                        path.pop_back();
                    if (!path.empty())
                        paths.push_back(path);
                }
            }
            return paths;
        };
        std::vector<std::string> ralia = listed("Z", ".ralia", "ralia");
        std::vector<std::string> brill = listed("V", ".brillhome", "brill-home");
        std::vector<fs::path> files;
        for (auto it = fs::recursive_directory_iterator(moduleData, error); !error && it != fs::recursive_directory_iterator(); it.increment(error))
            if (it->is_regular_file(error))
                files.push_back(it->path());
        std::sort(files.begin(), files.end());
        for (auto const& f : files)
        {
            stamp.Add(f.lexically_relative(moduleData).generic_string());
            stamp.Add(Text(f));
        }
        if (ours && fs::exists(patch, error) && Text(mark) == stamp.Hex() + "\n")
            return true;

        log("Making the Skyborne's patch for the game (" + patch.string() + ")");
        fs::path part = patch;
        part += ".part";
        MpqWriter writer(part);
        size_t tables = 0, textures = 0, missing = 0, bad = 0;
        std::vector<std::string> problems;

        // Textures (first: the tables name the ones made).
        std::set<std::string> made;
        std::istringstream recipes(Text(moduleData / "textures.txt"));
        std::string line;
        while (std::getline(recipes, line))
        {
            if (!line.empty() && line.back() == '\r')
                line.pop_back();
            if (line.empty() || line[0] == '#')
                continue;
            std::vector<std::string> f;
            std::istringstream fields(line);
            for (std::string part2; std::getline(fields, part2, '\t');)
                f.push_back(part2);
            Recipe recipe;
            if (f.size() != 4 || !ParseRecipe(f[0], f[1], recipe))
            {
                ++bad;
                continue;
            }
            for (bool extra : { false, true })
            {
                std::string from = extra ? Extra(f[2]) : f[2], to = extra ? Extra(f[3]) : f[3];
                Bytes data;
                if (!game.Read(from, data))
                {
                    if (!extra)
                        ++missing;
                    continue;
                }
                if (!Recolor(data, recipe))
                {
                    ++bad;
                    continue;
                }
                writer.Add(to, data);
                made.insert(Lower(to));
                ++textures;
            }
        }

        // mod-ralia's textures and Corn's files, as the game has them with their patches in (the Skyborne's own
        // made above win).
        size_t carried = 0, carriedBrill = 0;
        {
            std::set<std::string> done = made;
            for (std::string const& path : ralia)
            {
                Bytes data;
                if (!done.insert(Lower(path)).second || !game.Read(path, data))
                    continue;
                writer.Add(path, data);
                ++carried;
            }
            for (std::string const& path : brill)
            {
                Bytes data;
                if (!done.insert(Lower(path)).second || !game.Read(path, data))
                    continue;
                writer.Add(path, data);
                ++carriedBrill;
            }
        }

        // Tables.
        for (auto it = fs::directory_iterator(moduleData / "dbc", error); !error && it != fs::directory_iterator(); it.increment(error))
        {
            std::string name = it->path().stem().string();
            Bytes data;
            Dbc dbc;
            if (!game.Read("DBFilesClient\\" + name + ".dbc", data) || !dbc.Parse(data))
            {
                problems.push_back(name + ".dbc isn't in the game");
                continue;
            }
            std::string problem = ApplyChanges(dbc, Text(it->path()));
            if (!problem.empty())
            {
                problems.push_back(name + ".dbc: " + problem);
                continue;
            }
            if (Lower(name) == "charsections")
                AddExtraSkins(dbc, game, made);
            if (Lower(name) == "charsections")
                EmptyOverlayRows(dbc);
            if (Lower(name) == "charsections")
                FillSkinHoles(dbc);
            if (Lower(name) == "charsections")
                CompleteSkins(dbc);
            if (femaleBodyPreview && Lower(name) == "charstartoutfit")
                for (auto& row : dbc.records)
                    BodyPreview::Apply(row);
            SortCharacterTable(dbc, name);
            writer.Add("DBFilesClient\\" + name + ".dbc", dbc.Write());
            ++tables;
        }

        // The character creation screen: the race icons, the screen's own file list with theirs.
        for (char const* icons : { "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races.blp",
                                   "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound.blp" })
        {
            Bytes data;
            if (game.Read(icons, data) && SkyborneIcons(data))
                writer.Add(icons, data);
            else
                problems.push_back(std::string(icons) + ": no race icons to add theirs to");
        }
        Bytes toc;
        if (game.Read("Interface\\GlueXML\\GlueXML.toc", toc))
        {
            std::string text(toc.begin(), toc.end());
            if (text.find("SkyborneCreate.xml") == std::string::npos)
            {
                if (!text.empty() && text.back() != '\n')
                    text += "\r\n";
                text += "SkyborneCreate.xml\r\nSkyborneCreate.lua\r\n";
            }
            // The preview's zoom (the mouse wheel: the app's pinch).
            if (text.find("SkyborneZoom.lua") == std::string::npos)
            {
                if (!text.empty() && text.back() != '\n')
                    text += "\r\n";
                text += "SkyborneZoom.lua\r\n";
            }
            writer.Add("Interface\\GlueXML\\GlueXML.toc", Bytes(text.begin(), text.end()));
            for (char const* name : { "SkyborneCreate.xml", "SkyborneCreate.lua", "SkyborneZoom.lua" })
                writer.Add(std::string("Interface\\GlueXML\\") + name, ReadFile(moduleData / "Interface" / "GlueXML" / name));
        }
        else
            problems.push_back("GlueXML.toc isn't in the game: the character screen won't show them");
        // The intro's narration (the user's, data/client/intro.mp3), where the game's sound table has it.
        writer.Add("Sound\\CinematicVoices\\SkyborneNarration.mp3", ReadFile(moduleData / "intro.mp3"));

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
        log("The Skyborne's patch is in the game: " + std::to_string(tables) + " tables, " + std::to_string(textures)
            + " textures" + (carried ? ", " + std::to_string(carried) + " of mod-ralia's" : "")
            + (carriedBrill ? ", " + std::to_string(carriedBrill) + " of mod-brill-home's (Corn)" : "") + (missing ? ", " + std::to_string(missing) + " the game hasn't" : "")
            + (bad ? ", " + std::to_string(bad) + " that couldn't be made" : "") + " (" + std::to_string(seconds) + " s)");
        return true;
    }
}
