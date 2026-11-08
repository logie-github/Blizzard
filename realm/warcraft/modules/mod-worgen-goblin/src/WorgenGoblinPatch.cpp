// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Worgen's and Goblins' patch for the game (mod-worgen-goblin): mod-worgoblin's models,
 * textures, sounds and icons (its files, laid out by tools/package.py as the server was packaged:
 * never in this repository), the game's own tables with what mod-worgoblin changes in them put in
 * (data/client/dbc, tools/build_data.py: its rows added, its races' bits OR'd in, the game's own
 * goblin and fel orc creatures moved out of the two races' places first), and the character
 * creation screen's script (data/client/Interface/GlueXML/WorgenGoblinCreate.lua) with its texts.
 *
 * It's Data/patch-U.MPQ: read after the HD looks' patches (whose tables it builds on) and before the
 * allied races' patch-V.MPQ, Wrath Remix's patch-Y.MPQ and the Skyborne's patch-Z.MPQ, which are made
 * from the client with this patch in it and so carry its rows on (made first: WorgenGoblin.cpp, as
 * the configuration is about to be read; the allied races' is made once it's read).
 *
 * The archive reading and writing and the tables are the Skyborne's (SkyborneFiles).
 */

#include "WorgenGoblinPatch.h"
#include "../../mod-skyborne/src/SkyborneFiles.h"
#include <algorithm>
#include <chrono>
#include <map>
#include <set>
#include <cstdio>
#include <sstream>

namespace WorgenGoblin
{
    using Skyborne::Bytes;
    using Skyborne::Dbc;
    using Skyborne::Game;
    using Skyborne::MpqWriter;

    namespace
    {
        constexpr char const* PATCH = "patch-U.MPQ";
        constexpr char const* MARK = "patch-U.MPQ.worgengoblin";
        constexpr char const* ASIDE = "patch-U.MPQ.aside";
        constexpr char const* MANIFEST = "worgengoblin.files";
        constexpr char const* VERSION = "worgen-goblin-2";
        constexpr char const* MINIMAP = "textures\\minimap\\md5translate.trs";
        // The character screen's files in the game's GlueXML.toc, in this order: the races' texts
        // (mod-worgoblin's, from its files), the extra race buttons, then the script.
        constexpr char const* STRINGS = "WorgenGoblinStrings.lua";
        constexpr char const* BUTTONS = "WorgenGoblinCreate.xml";
        constexpr char const* SCRIPT = "WorgenGoblinCreate.lua";

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
    }

    std::vector<std::string> Statements(std::string const& sql)
    {
        std::vector<std::string> out;
        std::istringstream in(sql);
        std::string line, current;
        while (std::getline(in, line))
        {
            if (!line.empty() && line.back() == '\r')
                line.pop_back();
            if (current.empty() && (line.empty() || line.rfind("--", 0) == 0))
                continue;
            current += line;
            current += '\n';
            if (!line.empty() && line.back() == ';')
            {
                out.push_back(current);
                current.clear();
            }
        }
        if (current.find_first_not_of(" \t\r\n") != std::string::npos)
            out.push_back(current);
        return out;
    }

    void RemovePatch(fs::path const& clientData, std::function<void(std::string const&)> const& log)
    {
        std::error_code error;
        if (!fs::exists(clientData / MARK, error))
            return;
        fs::remove(clientData / PATCH, error);
        fs::remove(clientData / ASIDE, error);
        fs::remove(clientData / MARK, error);
        log("The Worgen's and Goblins' patch is out of the game");
    }

    void SetPatchAside(fs::path const& clientData, std::function<void(std::string const&)> const& log)
    {
        std::error_code error;
        if (!fs::exists(clientData / MARK, error) || !fs::exists(clientData / PATCH, error))
            return;
        fs::remove(clientData / ASIDE, error);
        fs::rename(clientData / PATCH, clientData / ASIDE, error);
        if (error)
            log("The Worgen's and Goblins' patch couldn't be set aside: " + error.message());
        else
            log("The Worgen's and Goblins' patch is out of the game, kept beside it for a realm with them");
    }

    namespace
    {
        std::vector<std::string> Lines(std::string const& text)
        {
            std::vector<std::string> out;
            std::istringstream in(text);
            std::string line;
            while (std::getline(in, line))
            {
                if (!line.empty() && line.back() == '\r')
                    line.pop_back();
                if (!line.empty())
                    out.push_back(line);
            }
            return out;
        }

        std::string LowerText(std::string text)
        {
            std::transform(text.begin(), text.end(), text.begin(), [](unsigned char c) { return char(std::tolower(c)); });
            return text;
        }

        // The tables' changes of a folder (dbc/<Table>.txt), by table.
        void TableChanges(fs::path const& folder, std::map<std::string, std::vector<fs::path>>& out)
        {
            std::error_code error;
            for (auto it = fs::directory_iterator(folder / "dbc", error); !error && it != fs::directory_iterator(); it.increment(error))
                if (it->path().extension() == ".txt")
                    out[it->path().stem().string()].push_back(it->path());
        }
    }

    bool UpdatePatch(fs::path const& moduleData, fs::path const& files, fs::path const& clientData, std::function<void(std::string const&)> const& log,
                     Zones const& zones)
    {
        std::error_code error;
        fs::path patch = clientData / PATCH, mark = clientData / MARK;
        bool ours = fs::exists(mark, error);
        if (!ours && fs::exists(patch, error))
        {
            log(patch.string() + " isn't this module's: left alone, so the game won't know the Worgen and Goblins");
            return false;
        }
        if (ours && !fs::exists(patch, error) && fs::exists(clientData / ASIDE, error))
            fs::rename(clientData / ASIDE, patch, error);
        auto start = std::chrono::steady_clock::now();
        // (the game's tables as the game reads them before this patch: without it and the patches
        // made from the game with it in)
        Game game(clientData, { "patch-u.mpq", "patch-v.mpq", "patch-w.mpq", "patch-y.mpq", "patch-z.mpq", "patch-enus-y.mpq", "patch-engb-y.mpq",
            "patch-dede-y.mpq", "patch-frfr-y.mpq", "patch-eses-y.mpq", "patch-esmx-y.mpq", "patch-ruru-y.mpq", "patch-kokr-y.mpq",
            "patch-zhcn-y.mpq", "patch-zhtw-y.mpq",
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
            log("mod-worgoblin's files for the game aren't in " + files.string() + " (no " + MANIFEST + "): the patch isn't made");
            RemovePatch(clientData, log);
            return false;
        }

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
        // The starting areas: their package (what it was made from) and their tables' rows.
        bool withZones = !zones.tables.empty() && !zones.package.empty() && fs::exists(zones.package / "files.txt", error);
        if (withZones)
        {
            stamp.Add("zones");
            stamp.Add(Text(zones.package / ".." / "TAG"));
            stamp.Add(Text(zones.package / "files.txt"));
            std::map<std::string, std::vector<fs::path>> rows;
            TableChanges(zones.tables, rows);
            for (auto const& [table, paths] : rows)
                for (auto const& path : paths)
                {
                    stamp.Add(table);
                    stamp.Add(Text(path));
                }
        }
        if (ours && fs::exists(patch, error) && Text(mark) == stamp.Hex() + "\n")
            return true;

        log("Making the Worgen's and Goblins' patch for the game (" + patch.string() + ")");
        fs::path part = patch;
        part += ".part";
        MpqWriter writer(part);
        size_t tables = 0, packed = 0, missing = 0;
        std::vector<std::string> problems;
        bool strings = false;

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
            std::string low = name;
            std::transform(low.begin(), low.end(), low.begin(), [](unsigned char c) { return char(std::tolower(c)); });
            if (low == "interface\\gluexml\\worgengoblinstrings.lua")
                strings = true;
        }
        if (missing)
            problems.push_back(std::to_string(missing) + " of mod-worgoblin's files aren't in " + files.string());

        // The starting areas' files: the ones the game hasn't (a file of the game's own is never
        // replaced); a file the package has once for several paths (a terrain swap's tiles that are
        // its base map's) stored once.
        size_t zoneFiles = 0, gameHas = 0, zoneMissing = 0;
        if (withZones)
        {
            std::map<std::string, std::string> same;
            for (std::string const& line : Lines(Text(zones.package / "same.txt")))
            {
                size_t tab = line.find('\t');
                if (tab != std::string::npos)
                    same[line.substr(0, tab)] = line.substr(tab + 1);
            }
            std::set<std::string> added;
            // (the files stored first, then the paths that are one of them)
            std::vector<std::string> names = Lines(Text(zones.package / "files.txt"));
            std::stable_partition(names.begin(), names.end(), [&](std::string const& n) { return !same.count(n); });
            for (std::string const& name : names)
            {
                if (game.Has(name))
                {
                    ++gameHas;
                    continue;
                }
                auto it = same.find(name);
                std::string const& stored = it == same.end() ? name : it->second;
                if (it != same.end() && added.count(stored) && writer.AddSame(name, stored))
                {
                    ++zoneFiles;
                    continue;
                }
                Bytes data = ReadFile(LocalPath(zones.package / "files", LowerText(stored)));
                if (data.empty())
                {
                    ++zoneMissing;
                    continue;
                }
                writer.Add(name, data);
                added.insert(name);
                ++zoneFiles;
            }
            if (zoneMissing)
                problems.push_back(std::to_string(zoneMissing) + " of the starting areas' files aren't in " + zones.package.string());
            // Their maps' lines in the game's minimap index.
            Bytes index;
            std::string text;
            if (game.Read(MINIMAP, index))
                text.assign(index.begin(), index.end());
            std::string ours = Text(zones.package / "minimap.txt");
            if (!text.empty() && text.back() != '\n')
                text += "\r\n";
            for (std::string const& line : Lines(ours))
                text += line + "\r\n";
            writer.Add(MINIMAP, Bytes(text.begin(), text.end()));
        }

        // The tables: mod-worgoblin's changes, then the starting areas' rows.
        std::map<std::string, std::vector<fs::path>> changes;
        TableChanges(moduleData, changes);
        if (withZones)
            TableChanges(zones.tables, changes);
        for (auto const& [name, paths] : changes)
        {
            Bytes data;
            Dbc dbc;
            if (!game.Read("DBFilesClient\\" + name + ".dbc", data) || !dbc.Parse(data))
            {
                problems.push_back(name + ".dbc isn't in the game");
                continue;
            }
            std::string problem;
            for (auto const& path : paths)
                if (problem.empty())
                    problem = Skyborne::ApplyChanges(dbc, Text(path));
            if (!problem.empty())
            {
                problems.push_back(name + ".dbc: " + problem);
                continue;
            }
            Skyborne::SortCharacterTable(dbc, name);
            writer.Add("DBFilesClient\\" + name + ".dbc", dbc.Write());
            ++tables;
        }

        // The character creation screen: the races' texts and the script, in the game's list.
        Bytes toc;
        if (game.Read("Interface\\GlueXML\\GlueXML.toc", toc))
        {
            std::string text(toc.begin(), toc.end());
            if (!text.empty() && text.back() != '\n')
                text += "\r\n";
            if (strings && text.find(STRINGS) == std::string::npos)
                text += std::string(STRINGS) + "\r\n";
            if (text.find(SCRIPT) == std::string::npos)
                text += std::string(BUTTONS) + "\r\n" + SCRIPT + "\r\n";
            writer.Add("Interface\\GlueXML\\GlueXML.toc", Bytes(text.begin(), text.end()));
            for (char const* name : { BUTTONS, SCRIPT })
                writer.Add(std::string("Interface\\GlueXML\\") + name, ReadFile(moduleData / "Interface" / "GlueXML" / name));
        }
        else
            problems.push_back("GlueXML.toc isn't in the game: the character screen won't show them");

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
        log("The Worgen's and Goblins' patch is in the game: " + std::to_string(tables) + " tables, " + std::to_string(packed)
            + " files (" + std::to_string(seconds) + " s)");
        if (withZones)
            log("The starting areas are in it: " + std::to_string(zoneFiles) + " files (" + std::to_string(gameHas)
                + " the game has already, its own kept)");
        return true;
    }
}
