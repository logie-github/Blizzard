// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The character textures' patch for the game (RaliaPatch.h): a set of the user's own, made the game's.
 * Two sets, one at a time: Ralia's mod (Ralia's patches, made for the game of today), and Alternate
 * Female Options (another set, the women's textures alone). "Ralia's" below is either set's.
 *
 * It's Data/<locale>/patch-<locale>-Z.MPQ, with the list of its paths beside it (.files). The game
 * was taken to read it last (the language's patch of a letter after the letter's own), but in the game
 * the Data folder's patches won: the HD look's patch-A, the Worgen's and Goblins' patch-U and the allied
 * races' patch-V kept their own textures at the same paths, and only the Skyborne's skins (made from
 * this patch's, at paths of their own) showed the set. So the Skyborne's Data/patch-Z.MPQ, made after
 * this from the game with it in and above every other Data patch, carries every path on the list too:
 * the set is drawn whichever of the two the game reads last. It's made from the game without the Skyborne's patch-Z or Wrath Remix's
 * patch-Y (made after it as the world starts, from the game with it in: the Skyborne's skins are the
 * blood elves', recoloured, so the Skyborne wear Ralia's blood elf textures), and without itself.
 *
 * Which textures: the game's CharSections names them, each skin (section 0, and its second texture,
 * the tauren's fur, when a set has it) and underwear (section 4: pelvis and torso) of every race but the murlocs and the naga.
 * Each takes Ralia's file of the same name (the game's names, without their underscores and their
 * case, are today's, with "_hd" after the newer models'), or for the allied races the one
 * data/client/sources.txt names (tools/build_data.py: their colours are numbered as this game's tables
 * have them, not as today's files are). The game's size is kept: a skin of today is twice as wide as
 * it is high, with the body (classic's layout) in its left half, which is what's used.
 *
 * Only a skin's body part is taken (RaliaImage, InBody: classic's TorsoUpper, TorsoLower and LegUpper),
 * its colours scaled to the game's skin there; the rest of the skin stays the game's own, so what an HD
 * look's models draw from other parts (the Draenei's horns) stays as it was.
 *
 * A skin with no file of Ralia's (a colour Ralia's patches don't have, or one of the allied races'
 * tattooed skins, which sources.txt points at their plain colour) takes the changes Ralia's file makes
 * to the nearest colour that has one (RaliaImage, Repaint): where that colour's file differs from the
 * game's, this colour's picture is changed as much, so its own colour and tattoo stay. Where the nearest
 * colour's file is another picture than the game's (more than a twentieth of it changed: an HD look's
 * skins), its body part is taken in this colour's skin instead. Underwear with no file takes the nearest
 * colour's.
 *
 * Where a set has a texture both as the older models' and as the newer's ("_hd"), the one nearer the
 * game's own picture is used (the game draws the older models, or an HD look's newer ones).
 *
 * 3.3.5 composes a character's texture from palettized textures (each made here with 256 colours,
 * the skin's alpha the game's own, the underwear's Ralia's). The archive reading and writing and the
 * decoding are the Skyborne's (SkyborneFiles).
 */

#include "RaliaPatch.h"
#include "RaliaImage.h"
#include "../../mod-skyborne/src/SkyborneFiles.h"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <map>
#include <sstream>
#include <vector>

namespace Ralia
{
    using Skyborne::Dbc;
    using Skyborne::Game;
    using Skyborne::MpqWriter;

    namespace
    {
        constexpr char const* MARK_SUFFIX = ".ralia";
        // The paths the patch has, one a line: the Skyborne's Data/patch-Z.MPQ carries them too (below).
        constexpr char const* LIST_SUFFIX = ".files";
        constexpr char const* VERSION = "ralia-5";   // 5: the list of its paths, for the Skyborne's patch
        // The races left as they are (their textures' folders).
        constexpr char const* LEFT_OUT[] = { "character\\murloc\\", "character\\naga_\\" };
        // Above this share of a skin changed, the nearest file isn't the same picture changed.
        constexpr double MOST_CHANGED = 0.05;

        std::string Lower(std::string text)
        {
            std::transform(text.begin(), text.end(), text.begin(), [](unsigned char c) { return std::tolower(c); });
            return text;
        }

        // A texture's name as Ralia's file and the game's compare: its file name without the
        // extension, the underscores or the case.
        std::string Key(std::string const& path)
        {
            size_t slash = path.find_last_of("\\/");
            std::string name = slash == std::string::npos ? path : path.substr(slash + 1);
            size_t dot = name.find_last_of('.');
            if (dot != std::string::npos)
                name.resize(dot);
            std::string key;
            for (unsigned char c : name)
                if (c != '_')
                    key.push_back(char(std::tolower(c)));
            return key;
        }

        std::string Folder(std::string const& path)
        {
            size_t slash = path.find_last_of('\\');
            return Lower(slash == std::string::npos ? std::string() : path.substr(0, slash + 1));
        }

        // The client's language: the folder in Data with its locale-<name>.MPQ.
        std::string Locale(fs::path const& clientData)
        {
            std::error_code error;
            for (auto it = fs::directory_iterator(clientData, error); !error && it != fs::directory_iterator(); it.increment(error))
            {
                std::string name = it->path().filename().string();
                if (name.size() != 4 || !it->is_directory(error))
                    continue;
                for (auto in = fs::directory_iterator(it->path(), error); !error && in != fs::directory_iterator(); in.increment(error))
                    if (Lower(in->path().filename().string()) == Lower("locale-" + name + ".mpq"))
                        return name;
            }
            return "";
        }

        fs::path PatchPath(fs::path const& clientData, std::string const& locale)
        {
            return clientData / locale / ("patch-" + locale + "-Z.MPQ");
        }

        fs::path With(fs::path path, char const* suffix)
        {
            path += suffix;
            return path;
        }

        // This patch, and those made after it from the game with it in (the Skyborne's and Wrath Remix's).
        std::vector<std::string> Skip(std::string const& locale)
        {
            std::string loc = Lower(locale);
            return { "patch-" + loc + "-z.mpq", "patch-z.mpq", "patch-y.mpq", "patch-" + loc + "-y.mpq" };
        }

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

        // FNV-1a: what the patch is made from, to know when to make it again; and a file's bytes.
        struct Stamp
        {
            uint64_t value = 1469598103934665603ull;
            void Add(std::string const& text) { Add(reinterpret_cast<uint8_t const*>(text.data()), text.size()); }
            void Add(uint8_t const* p, size_t n)
            {
                for (size_t i = 0; i < n; ++i)
                {
                    value ^= p[i];
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

        enum Kind { SKIN, PELVIS, TORSO, EXTRA };   // (EXTRA: a skin's second texture, the tauren's fur)

        struct Target
        {
            std::string path;       // as the game's CharSections names it
            Kind kind = SKIN;
            fs::path source;        // Ralia's file for it, when there's one
            fs::path other;         // and the newer models' ("_hd"), when there's both: the nearer is used
            std::string like;       // sources.txt's "=": the target (lower case) whose change it takes
            bool missing = false;   // the game hasn't it (or it isn't a texture)
            Image game;             // the game's, while it's needed
            uint8_t alphaDepth = 0;
        };

        bool StartsWith(std::string const& text, std::string const& start)
        {
            return text.compare(0, start.size(), start) == 0;
        }
    }

    void RemovePatch(fs::path const& clientData, Log const& log)
    {
        std::error_code error;
        std::string locale = Locale(clientData);
        if (locale.empty())
            return;
        fs::path patch = PatchPath(clientData, locale);
        if (!fs::exists(With(patch, MARK_SUFFIX), error))
            return;
        fs::remove(patch, error);
        fs::remove(With(patch, MARK_SUFFIX), error);
        fs::remove(With(patch, LIST_SUFFIX), error);
        log("The character textures' patch is out of the game");
    }

    bool UpdatePatch(Set const& set, fs::path const& files, fs::path const& sources, fs::path const& clientData, Log const& log)
    {
        std::error_code error;
        std::string locale = Locale(clientData);
        if (locale.empty())
        {
            log("No language folder in " + clientData.string() + ": the patch isn't made");
            return false;
        }
        fs::path patch = PatchPath(clientData, locale), mark = With(patch, MARK_SUFFIX);
        bool ours = fs::exists(mark, error);
        if (!ours && fs::exists(patch, error))
        {
            log(patch.string() + " isn't this module's: left alone, so the mod isn't in the game");
            return false;
        }

        // Ralia's files, by name.
        std::map<std::string, fs::path> ralia;
        std::vector<std::pair<std::string, uintmax_t>> listing;
        for (auto it = fs::recursive_directory_iterator(files, error); !error && it != fs::recursive_directory_iterator(); it.increment(error))
            if (it->is_regular_file(error) && Lower(it->path().extension().string()) == ".blp")
                listing.emplace_back(fs::relative(it->path(), files, error).generic_string(), it->file_size(error));
        std::sort(listing.begin(), listing.end());
        std::map<std::string, std::vector<fs::path>> raliaFolders;   // (lower case, the game's backslashes)
        for (auto const& [name, size] : listing)
        {
            ralia.emplace(Key(name), files / name);
            std::string folder = name;
            std::replace(folder.begin(), folder.end(), '/', '\\');
            raliaFolders[Folder(folder)].push_back(files / name);
        }
        if (ralia.empty())
        {
            log("No textures in " + files.string() + " (the zip picked in the app's Game options): the patch isn't made");
            RemovePatch(clientData, log);
            return false;
        }

        // Which file each of the allied races' colours takes.
        std::string table = Text(sources);
        std::map<std::string, std::string> named;
        {
            std::istringstream in(table);
            std::string line;
            while (std::getline(in, line))
            {
                if (!line.empty() && line.back() == '\r')
                    line.pop_back();
                size_t tab = line.find('\t');
                if (line.empty() || line[0] == '#' || tab == std::string::npos)
                    continue;
                named[Lower(line.substr(0, tab))] = line.substr(tab + 1);
            }
        }

        auto start = std::chrono::steady_clock::now();
        Game game(clientData, Skip(locale));
        if (game.archives.empty())
        {
            log("No game in " + clientData.string());
            return false;
        }
        Stamp stamp;
        stamp.Add(VERSION);
        stamp.Add(set.name + (set.femaleOnly ? "|women" : ""));
        for (std::string const& out : set.leftOut)
            stamp.Add(out);
        stamp.Add(game.Describe());
        stamp.Add(table);
        for (auto const& [name, size] : listing)
        {
            stamp.Add(name);
            stamp.Add(std::to_string(size));
        }
        if (ours && fs::exists(patch, error) && fs::exists(With(patch, LIST_SUFFIX), error) && Text(mark) == stamp.Hex() + "\n")
            return true;

        Bytes data;
        Dbc sections;
        if (!game.Read("DBFilesClient\\CharSections.dbc", data) || !sections.Parse(data) || sections.fields < 10)
        {
            log("The game's CharSections.dbc couldn't be read: the patch isn't made");
            return false;
        }
        auto text = [&](uint32_t at) -> std::string
        {
            if (at >= sections.strings.size())
                return "";
            auto begin = sections.strings.begin() + at;
            return std::string(begin, std::find(begin, sections.strings.end(), uint8_t(0)));
        };

        // The textures: each skin and underwear the table names, once.
        std::vector<Target> targets;
        std::map<std::string, size_t> byPath;
        auto add = [&](uint32_t at, Kind kind)
        {
            std::string path = text(at), lower = Lower(path);
            if (path.empty() || byPath.count(lower) || (set.femaleOnly && lower.find("\\female\\") == std::string::npos))
                return;
            for (char const* out : LEFT_OUT)
                if (StartsWith(lower, out))
                    return;
            for (std::string const& out : set.leftOut)
                if (StartsWith(lower, out))
                    return;
            byPath[lower] = targets.size();
            Target t;
            t.path = path;
            t.kind = kind;
            targets.push_back(std::move(t));
        };
        for (size_t row = 0; row < sections.records.size(); ++row)
        {
            uint32_t section = sections.Get(row, 3);
            if (section == 0)
            {
                add(sections.Get(row, 4), SKIN);
                add(sections.Get(row, 5), EXTRA);
            }
            else if (section == 4)
            {
                add(sections.Get(row, 4), PELVIS);
                add(sections.Get(row, 5), TORSO);
            }
        }
        for (Target& t : targets)
        {
            if (auto it = named.find(Lower(t.path)); it != named.end())
            {
                if (StartsWith(it->second, "="))
                    t.like = Lower(it->second.substr(1));
                else if (auto file = ralia.find(Key(it->second)); file != ralia.end())
                    t.source = file->second;
                continue;
            }
            std::string key = Key(t.path);
            auto file = ralia.find(key), hd = ralia.find(key + "hd");
            if (file != ralia.end())
            {
                t.source = file->second;
                if (hd != ralia.end())
                    t.other = hd->second;
            }
            else if (hd != ralia.end())
                t.source = hd->second;
        }

        auto readGame = [&](Target& t) -> bool
        {
            if (t.missing)
                return false;
            if (!t.game.rgba.empty())
                return true;
            Bytes b;
            uint32_t w = 0, h = 0;
            if (!game.Read(t.path, b) || !Header(b, w, h, t.alphaDepth) || !Skyborne::Decode(b, t.game))
            {
                t.missing = true;
                t.game = Image{};
                return false;
            }
            return true;
        };
        std::map<fs::path, Image> raliaImages;
        auto readRalia = [&](fs::path const& file, Kind kind, Image& out) -> bool
        {
            auto it = raliaImages.find(file);
            if (it == raliaImages.end())
            {
                Image image;
                if (!DecodeFull(ReadFile(file), image))
                    return false;
                if (kind == SKIN || kind == EXTRA)
                    image = Body(image);
                it = raliaImages.emplace(file, std::move(image)).first;
            }
            out = it->second;
            return true;
        };

        // The textures folder by folder (a race and sex's), so a colour's nearest is one of its own.
        std::vector<size_t> order(targets.size());
        for (size_t i = 0; i < order.size(); ++i)
            order[i] = i;
        std::stable_sort(order.begin(), order.end(), [&](size_t a, size_t b) { return Folder(targets[a].path) < Folder(targets[b].path); });

        // The colour whose change [index] takes: sources.txt's, or the nearest with a file of Ralia's.
        std::function<size_t(size_t, std::vector<size_t> const&, int)> donor = [&](size_t index, std::vector<size_t> const& group, int depth) -> size_t
        {
            Target& t = targets[index];
            if (!t.like.empty() && depth < 4)
                if (auto it = byPath.find(t.like); it != byPath.end())
                    return targets[it->second].source.empty() ? donor(it->second, group, depth + 1) : it->second;
            if (!readGame(t))
                return SIZE_MAX;
            size_t best = SIZE_MAX;
            double bestDistance = 0;
            for (size_t j : group)
            {
                Target& d = targets[j];
                if (j == index || d.kind != t.kind || d.source.empty() || !readGame(d))
                    continue;
                double distance = Distance(t.game, d.game);
                if (best == SIZE_MAX || distance < bestDistance)
                {
                    best = j;
                    bestDistance = distance;
                }
            }
            return best;
        };

        // Pelvis or torso textures named otherwise than by colour (the Worgen's _regular and _dk), with no
        // colour of theirs to take from: Ralia's first of the kind in the same folder.
        auto sameKind = [&](Target const& t) -> fs::path
        {
            auto it = raliaFolders.find(Folder(t.path));
            if (it == raliaFolders.end() || t.kind == SKIN || t.kind == EXTRA)
                return {};
            std::string part = t.kind == PELVIS ? "nakedpelvisskin" : "nakedtorsoskin";
            for (fs::path const& file : it->second)
                if (Key(file.filename().string()).find(part) != std::string::npos)
                    return file;
            return {};
        };

        log("Making " + set.name + " for the game (" + patch.string() + ")");
        fs::path part = patch;
        part += ".part";
        MpqWriter writer(part);
        std::map<std::pair<uint64_t, size_t>, std::string> written;
        std::vector<std::string> paths;
        size_t direct = 0, repainted = 0, kept = 0, packed = 0;
        auto put = [&](Target const& t, Bytes const& blp)
        {
            paths.push_back(t.path);
            Stamp hash;
            hash.Add(blp.data(), blp.size());
            auto key = std::make_pair(hash.value, blp.size());
            if (auto it = written.find(key); it != written.end() && writer.AddSame(t.path, it->second))
                return;
            writer.Add(t.path, blp);
            written.emplace(key, t.path);
            ++packed;
        };

        for (size_t from = 0; from < order.size();)
        {
            std::string folder = Folder(targets[order[from]].path);
            size_t to = from;
            while (to < order.size() && Folder(targets[order[to]].path) == folder)
                ++to;
            std::vector<size_t> group(order.begin() + from, order.begin() + to);
            from = to;
            // Ralia's own files first, then the rest from them.
            for (int pass = 0; pass < 2; ++pass)
                for (size_t index : group)
                {
                    Target& t = targets[index];
                    bool hasFile = !t.source.empty();
                    if (hasFile != (pass == 0))
                        continue;
                    // (a fur texture is its colour's own: none from another colour's)
                    size_t src = hasFile ? index : t.kind == EXTRA ? SIZE_MAX : donor(index, group, 0);
                    fs::path file = src != SIZE_MAX ? targets[src].source : sameKind(t);
                    if (file.empty() || !readGame(t))
                    {
                        if (!hasFile)
                            ++kept;
                        continue;
                    }
                    if (hasFile && !t.other.empty())
                    {
                        // the older models' file or the newer's: the one nearer the game's own picture
                        Image older, newer;
                        if (readRalia(t.source, t.kind, older) && readRalia(t.other, t.kind, newer)
                            && Distance(newer, t.game) < Distance(older, t.game))
                            t.source = t.other;
                        t.other.clear();
                        file = t.source;
                    }
                    Image after;
                    if (!readRalia(file, t.kind, after))
                    {
                        log("  " + file.string() + " couldn't be read");
                        ++kept;
                        continue;
                    }
                    uint32_t w = t.game.width, h = t.game.height;
                    Image out;
                    if (t.kind == PELVIS || t.kind == TORSO)
                        out = Resize(after, w, h);          // underwear: Ralia's, alpha and all
                    else if (hasFile)
                        // the body part of Ralia's, in the game's skin colour; the rest the game's own
                        out = Fit(t.game, Resize(after, w, h), t.kind == EXTRA);
                    else
                    {
                        Target& d = targets[src];
                        if (!readGame(d))
                        {
                            ++kept;
                            continue;
                        }
                        // the nearest colour's change, where its file is its game picture changed; where
                        // it's another picture (an HD look's skins), its body part in this colour's skin
                        double changed = 0;
                        out = KeepOutside(Repaint(t.game, Resize(d.game, w, h), Resize(after, w, h), changed), t.game);
                        if (changed > MOST_CHANGED)
                            out = Fit(t.game, Resize(after, w, h), false);
                    }
                    put(t, EncodePalette(out, t.kind != SKIN || t.alphaDepth));
                    ++(hasFile ? direct : repainted);
                    // (the game's picture is kept while it can be another colour's nearest)
                    if (!hasFile)
                        t.game = Image{};
                }
            for (size_t index : group)
                targets[index].game = Image{};
            raliaImages.clear();
        }

        if (!packed)
        {
            fs::remove(part, error);
            log("None of the game's character textures has a file in " + files.string() + ": the patch isn't made");
            RemovePatch(clientData, log);
            return false;
        }
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
            std::ofstream list(With(patch, LIST_SUFFIX), std::ios::trunc);
            for (std::string const& path : paths)
                list << path << "\n";
        }
        {
            std::ofstream out(mark, std::ios::trunc);
            out << stamp.Hex() << "\n";
        }
        auto seconds = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start).count();
        log(set.name + " is in the game: " + std::to_string(direct) + " textures from its files, " + std::to_string(repainted)
            + " colours changed as their nearest, " + std::to_string(kept) + " left as they are (" + std::to_string(seconds) + " s)");
        return true;
    }
}
