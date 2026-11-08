// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Murlocs' and the Naga's patch for the game (mod-murloc-naga). The game needs its tables to
 * know the two races (ChrRaces, CharSections, CharHairGeosets... with their rows: the module's
 * data/client/dbc, made by tools/build_data.py), the murlocs' character model and skins, the
 * naga's new skin colours, their place on the character creation screen, their intros (the
 * cameras, the narrations) and their homes' things (GameObjectDisplayInfo).
 *
 * The tables, the naga's colours, the screen's files and the intros are made here from the client's
 * own files (WOW_CLIENT_DIR: an HD look's, when one is in): the naga's looks are the game's naga
 * (Character\Naga_), its new colours the game's naga skins recoloured; the narrations the game's own
 * sounds, mixed (Lady Vashj's words for the naga, the murlocs' own voices for the murlocs). The
 * murlocs' model and textures are Blizzard's newer murloc and its kin's parts, made 3.3.5's as the
 * server is packaged (tools/murloc_model.py: data/files, never in this repository).
 *
 * It's Data/<locale>/patch-<locale>-T.MPQ: read after the HD looks' patches (A, F, 6, E, Q, the
 * Alternative HD Patch's S with its SoundEntries; ChromieCraft's H, F, G, S, T), whose tables it
 * builds on, and before the Worgen and Goblins' patch-U, the allied races' patch-V, Wrath Remix's
 * patch-Y and the Skyborne's patch-Z, which are made after it from the game with it in and so
 * carry its rows. The letter T in the language's folder is free in both HD looks.
 *
 * The archive reading and writing, the tables and the texture codec are the Skyborne's
 * (SkyborneFiles).
 */

#include "MurlocNagaPatch.h"
#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <map>
#include <set>
#include <sstream>
#include <tuple>

namespace MurlocNaga
{
    using Skyborne::Dbc;
    using Skyborne::Game;
    using Skyborne::Image;
    using Skyborne::MpqWriter;

    namespace
    {
        constexpr char const* VERSION = "murloc-naga-3";
        // The server package's lists of the files it made (data/files), and what's missing without each.
        constexpr char const* PACKAGED_LISTS[] = { "murloc.files", "naga.files", "nagaemotes.files", "nagamodels.files", "nagavoices.files" };
        constexpr char const* WITHOUT_LIST[] = {
            "the game won't draw the murlocs", "the naga have no headdresses or outfits", "the naga have no new emotes",
            "the naga's story's sea witch, warden and Queen Azshara draw nothing (tools/naga/looks.py's FALLBACK)",
            "the naga's story's Warcraft III voices aren't heard (their lines show as text)" };
        constexpr char const* MARK_SUFFIX = ".murlocnaga";
        constexpr char const* ASIDE_SUFFIX = ".aside";

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

        std::string Lower(std::string s)
        {
            std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c) { return char(std::tolower(c)); });
            return s;
        }

        uint32_t U32(Bytes const& b, size_t at)
        {
            uint32_t v = 0;
            if (at + 4 <= b.size())
                std::memcpy(&v, &b[at], 4);
            return v;
        }

        void Put32(Bytes& b, size_t at, uint32_t v) { std::memcpy(&b[at], &v, 4); }

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

        // The client's language: the folder in Data with its locale-<name>.MPQ (a file or a folder).
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
            return clientData / locale / ("patch-" + locale + "-T.MPQ");
        }

        fs::path With(fs::path path, char const* suffix)
        {
            path += suffix;
            return path;
        }

        // The archives read after this one (the letters after T, the language's too) and this one:
        // left out of what it's made from, as it's read before them (they're made from the game with
        // it in, and a patch made from theirs would be made again after each of them, and they after it).
        std::vector<std::string> Skip(std::string const& locale)
        {
            std::string loc = Lower(locale);
            std::vector<std::string> skip = { "patch-" + loc + "-t.mpq" };
            for (char c = 'u'; c <= 'z'; ++c)
            {
                skip.push_back(std::string("patch-") + c + ".mpq");
                skip.push_back("patch-" + loc + "-" + c + ".mpq");
            }
            return skip;
        }

        struct Hls { double h, l, s; };

        Hls ToHls(double r, double g, double b)
        {
            double mx = std::max({ r, g, b }), mn = std::min({ r, g, b });
            double l = (mx + mn) / 2, h = 0, s = 0;
            if (mx > mn)
            {
                double d = mx - mn;
                s = l <= 0.5 ? d / (mx + mn) : d / (2 - mx - mn);
                if (mx == r)
                    h = (g - b) / d / 6;
                else if (mx == g)
                    h = ((b - r) / d + 2) / 6;
                else
                    h = ((r - g) / d + 4) / 6;
                if (h < 0)
                    h += 1;
            }
            return { h, l, s };
        }

        double HueValue(double m1, double m2, double h)
        {
            h = std::fmod(h, 1.0);
            if (h < 0)
                h += 1;
            if (h < 1.0 / 6)
                return m1 + (m2 - m1) * h * 6;
            if (h < 0.5)
                return m2;
            if (h < 2.0 / 3)
                return m1 + (m2 - m1) * (2.0 / 3 - h) * 6;
            return m1;
        }

        void FromHls(Hls c, double& r, double& g, double& b)
        {
            if (c.s <= 0)
            {
                r = g = b = c.l;
                return;
            }
            double m2 = c.l <= 0.5 ? c.l * (1 + c.s) : c.l + c.s - c.l * c.s, m1 = 2 * c.l - m2;
            r = HueValue(m1, m2, c.h + 1.0 / 3);
            g = HueValue(m1, m2, c.h);
            b = HueValue(m1, m2, c.h - 1.0 / 3);
        }

        uint8_t Byte(double v) { return uint8_t(std::lround(std::clamp(v, 0.0, 1.0) * 255)); }

        void RecolourRgb(uint8_t& r, uint8_t& g, uint8_t& b, double hue, double saturation, double lightness)
        {
            Hls c = ToHls(r / 255.0, g / 255.0, b / 255.0);
            if (hue >= 0)
                c.h = hue;
            c.s = std::clamp(c.s * saturation, 0.0, 1.0);
            c.l = std::clamp(c.l * lightness, 0.0, 1.0);
            double nr, ng, nb;
            FromHls(c, nr, ng, nb);
            r = Byte(nr);
            g = Byte(ng);
            b = Byte(nb);
        }

        // [image] resampled to [w] x [h] (bilinear).
        Image Resized(Image const& in, uint32_t w, uint32_t h)
        {
            Image out;
            out.width = w;
            out.height = h;
            out.rgba.assign(size_t(w) * h * 4, 255);
            for (uint32_t y = 0; y < h; ++y)
                for (uint32_t x = 0; x < w; ++x)
                {
                    double sx = (x + 0.5) * in.width / w - 0.5, sy = (y + 0.5) * in.height / h - 0.5;
                    int x0 = int(std::floor(sx)), y0 = int(std::floor(sy));
                    double fx = sx - x0, fy = sy - y0;
                    auto at = [&](int px, int py, int c) -> double
                    {
                        px = std::clamp(px, 0, int(in.width) - 1);
                        py = std::clamp(py, 0, int(in.height) - 1);
                        return in.rgba[(size_t(py) * in.width + px) * 4 + c];
                    };
                    for (int c = 0; c < 4; ++c)
                    {
                        double v = at(x0, y0, c) * (1 - fx) * (1 - fy) + at(x0 + 1, y0, c) * fx * (1 - fy)
                            + at(x0, y0 + 1, c) * (1 - fx) * fy + at(x0 + 1, y0 + 1, c) * fx * fy;
                        out.rgba[(size_t(y) * w + x) * 4 + c] = uint8_t(std::clamp(v + 0.5, 0.0, 255.0));
                    }
                }
            return out;
        }

        // [in] a mip level down (each 2 x 2 pixels averaged; a side of 1 kept).
        Image Halved(Image const& in)
        {
            Image out;
            out.width = std::max(1u, in.width / 2);
            out.height = std::max(1u, in.height / 2);
            out.rgba.resize(size_t(out.width) * out.height * 4);
            for (uint32_t y = 0; y < out.height; ++y)
                for (uint32_t x = 0; x < out.width; ++x)
                    for (int c = 0; c < 4; ++c)
                    {
                        uint32_t sum = 0, n = 0;
                        for (uint32_t dy = 0; dy < 2; ++dy)
                            for (uint32_t dx = 0; dx < 2; ++dx)
                            {
                                uint32_t sx = std::min(in.width - 1, x * 2 + dx), sy = std::min(in.height - 1, y * 2 + dy);
                                sum += in.rgba[(size_t(sy) * in.width + sx) * 4 + c];
                                ++n;
                            }
                        out.rgba[(size_t(y) * out.width + x) * 4 + c] = uint8_t((sum + n / 2) / n);
                    }
            return out;
        }

        bool Translucent(Image const& image)
        {
            for (size_t i = 3; i < image.rgba.size(); i += 4)
                if (image.rgba[i] != 255)
                    return true;
            return false;
        }

        std::string StringOf(Dbc const& dbc, uint32_t at)
        {
            if (at >= dbc.strings.size())
                return "";
            auto begin = dbc.strings.begin() + at;
            return std::string(begin, std::find(begin, dbc.strings.end(), uint8_t(0)));
        }

        uint32_t BlpWidth(Bytes const& blp)
        {
            return blp.size() >= 20 && std::memcmp(blp.data(), "BLP2", 4) == 0 ? U32(blp, 12) : 0;
        }
    }

    Bytes EncodePalette(Image const& image, bool alpha)
    {
        // The palette: the image's colours split by median cut (the box with the widest spread of a
        // colour channel halved at its median) into at most 256, each its box's average.
        size_t count = size_t(image.width) * image.height;
        std::vector<uint32_t> pixels(count);
        for (size_t i = 0; i < count; ++i)
            pixels[i] = uint32_t(image.rgba[i * 4]) | uint32_t(image.rgba[i * 4 + 1]) << 8 | uint32_t(image.rgba[i * 4 + 2]) << 16;
        struct Box { size_t begin, end; int channel; int spread; };
        auto measure = [&](Box& box)
        {
            int lo[3] = { 255, 255, 255 }, hi[3] = { 0, 0, 0 };
            for (size_t i = box.begin; i < box.end; ++i)
                for (int c = 0; c < 3; ++c)
                {
                    int v = (pixels[i] >> (8 * c)) & 0xFF;
                    lo[c] = std::min(lo[c], v);
                    hi[c] = std::max(hi[c], v);
                }
            box.channel = 0;
            for (int c = 1; c < 3; ++c)
                if (hi[c] - lo[c] > hi[box.channel] - lo[box.channel])
                    box.channel = c;
            box.spread = box.end - box.begin > 1 ? hi[box.channel] - lo[box.channel] : 0;
        };
        std::vector<Box> boxes;
        if (count)
        {
            boxes.push_back({ 0, count, 0, 0 });
            measure(boxes[0]);
        }
        while (boxes.size() < 256)
        {
            size_t widest = boxes.size();
            for (size_t b = 0; b < boxes.size(); ++b)
                if (boxes[b].spread > 0 && (widest == boxes.size() || boxes[b].spread > boxes[widest].spread))
                    widest = b;
            if (widest == boxes.size())
                break;
            Box box = boxes[widest];
            int shift = 8 * box.channel;
            size_t middle = box.begin + (box.end - box.begin) / 2;
            std::nth_element(pixels.begin() + box.begin, pixels.begin() + middle, pixels.begin() + box.end,
                [shift](uint32_t a, uint32_t b) { return ((a >> shift) & 0xFF) < ((b >> shift) & 0xFF); });
            Box first = { box.begin, middle, 0, 0 }, second = { middle, box.end, 0, 0 };
            measure(first);
            measure(second);
            boxes[widest] = first;
            boxes.push_back(second);
        }
        std::vector<std::array<int, 3>> palette;
        for (auto const& box : boxes)
        {
            uint64_t sum[3] = { 0, 0, 0 };
            for (size_t i = box.begin; i < box.end; ++i)
                for (int c = 0; c < 3; ++c)
                    sum[c] += (pixels[i] >> (8 * c)) & 0xFF;
            size_t n = std::max<size_t>(1, box.end - box.begin);
            palette.push_back({ int(sum[0] / n), int(sum[1] / n), int(sum[2] / n) });
        }
        if (palette.empty())
            palette.push_back({ 0, 0, 0 });

        auto nearest = [&](uint8_t const* rgb)
        {
            int best = 0, bestDistance = INT32_MAX;
            for (size_t p = 0; p < palette.size(); ++p)
            {
                int dr = rgb[0] - palette[p][0], dg = rgb[1] - palette[p][1], db = rgb[2] - palette[p][2];
                int d = dr * dr + dg * dg + db * db;
                if (d < bestDistance)
                {
                    bestDistance = d;
                    best = int(p);
                    if (d == 0)
                        break;
                }
            }
            return uint8_t(best);
        };

        // Every mip level (the game's character textures have them all), each as indices into the
        // palette then its alpha, 8 bits a pixel.
        std::vector<Bytes> levels;
        Image level = image;
        while (true)
        {
            Bytes data(size_t(level.width) * level.height * (alpha ? 2 : 1));
            size_t pixelsHere = size_t(level.width) * level.height;
            for (size_t i = 0; i < pixelsHere; ++i)
            {
                data[i] = nearest(&level.rgba[i * 4]);
                if (alpha)
                    data[pixelsHere + i] = level.rgba[i * 4 + 3];
            }
            levels.push_back(std::move(data));
            if ((level.width == 1 && level.height == 1) || levels.size() == 16)
                break;
            level = Halved(level);
        }

        Bytes out(148 + 1024);
        std::memcpy(out.data(), "BLP2", 4);
        Put32(out, 4, 1);
        out[8] = 1;                                                 // a palette
        out[9] = alpha ? 8 : 0;                                     // alpha bits
        out[10] = alpha ? 8 : 0;
        out[11] = 1;                                                // mip levels
        Put32(out, 12, image.width);
        Put32(out, 16, image.height);
        uint32_t at = 148 + 1024;
        for (size_t i = 0; i < levels.size(); ++i)
        {
            Put32(out, 20 + i * 4, at);
            Put32(out, 84 + i * 4, uint32_t(levels[i].size()));
            at += uint32_t(levels[i].size());
        }
        for (size_t p = 0; p < palette.size(); ++p)
        {
            out[148 + p * 4] = uint8_t(palette[p][2]);              // B, G, R, A
            out[148 + p * 4 + 1] = uint8_t(palette[p][1]);
            out[148 + p * 4 + 2] = uint8_t(palette[p][0]);
            out[148 + p * 4 + 3] = 255;
        }
        for (auto const& data : levels)
            out.insert(out.end(), data.begin(), data.end());
        return out;
    }

    namespace
    {
        // A texture the game draws into a character's composed texture (a face, underwear), made as the
        // game's own are: palettized, and sized for a skin [skinWidth] wide (the composed texture's size:
        // the HD looks' 512, the game's 256): [w] x [h] of a 256 one, scaled. [recipe]: its colours
        // changed first (a naga colour of the game's that's made from another), or not.
        Bytes Composited(Image const& source, uint32_t skinWidth, uint32_t w, uint32_t h, double const* recipe)
        {
            Image image = Resized(source, w * skinWidth / 256, h * skinWidth / 256);
            if (recipe)
                for (size_t i = 0; i + 3 < image.rgba.size(); i += 4)
                    RecolourRgb(image.rgba[i], image.rgba[i + 1], image.rgba[i + 2], recipe[0], recipe[1], recipe[2]);
            return EncodePalette(image, Translucent(image));
        }

        // The races' icons for the character creation screen, a sheet of their own (one column:
        // Murloc men, Naga men, Murloc women, Naga women; the game's sheet has no column left: the
        // allied races and the Skyborne have its free ones), from the game's own icons: the murloc
        // head, the murloc oracle, Warlord Kalithresh and Lady Vashj. [round]: each one cut round.
        bool Icons(Game const& game, bool round, Bytes& out, std::vector<std::string>& problems)
        {
            std::vector<std::vector<char const*>> cells = {
                { "Interface\\Icons\\INV_Misc_Head_Murloc_01.blp" },
                { "Interface\\Icons\\Achievement_Boss_WarlordKalithresh.blp", "Interface\\Icons\\Achievement_Boss_LadyVashj.blp" },
                { "Interface\\Icons\\achievement_reputation_murlocoracle.blp", "Interface\\Icons\\INV_Misc_Head_Murloc_01.blp" },
                { "Interface\\Icons\\Achievement_Boss_LadyVashj.blp" },
            };
            constexpr uint32_t CELL = 64;
            Image sheet;
            sheet.width = CELL;
            sheet.height = CELL * 4;
            sheet.rgba.assign(size_t(sheet.width) * sheet.height * 4, 0);
            for (size_t row = 0; row < cells.size(); ++row)
            {
                Image icon;
                bool found = false;
                for (char const* name : cells[row])
                {
                    Bytes data;
                    if (game.Read(name, data) && Skyborne::Decode(data, icon))
                    {
                        found = true;
                        break;
                    }
                }
                if (!found)
                {
                    problems.push_back("no icon for the creation screen's row " + std::to_string(row));
                    continue;
                }
                Image cell = Resized(icon, CELL, CELL);
                for (uint32_t y = 0; y < CELL; ++y)
                    for (uint32_t x = 0; x < CELL; ++x)
                    {
                        uint8_t* p = &sheet.rgba[(size_t(row * CELL + y) * CELL + x) * 4];
                        std::memcpy(p, &cell.rgba[(size_t(y) * CELL + x) * 4], 4);
                        p[3] = 255;
                        if (round)
                        {
                            double dx = x + 0.5 - CELL / 2.0, dy = y + 0.5 - CELL / 2.0;
                            double edge = CELL / 2.0 - std::sqrt(dx * dx + dy * dy);
                            p[3] = Byte(std::clamp(edge, 0.0, 1.0));
                        }
                    }
            }
            out = Skyborne::EncodeDxt5(sheet);
            return true;
        }

        // A WAV's samples as numbers from -1 to 1, mono, at 22050 Hz.
        bool Samples(Bytes const& wav, std::vector<float>& out)
        {
            if (wav.size() < 12 || std::memcmp(wav.data(), "RIFF", 4) != 0 || std::memcmp(&wav[8], "WAVE", 4) != 0)
                return false;
            uint16_t format = 0, channels = 0, bits = 0;
            uint32_t rate = 0;
            size_t data = 0, size = 0;
            for (size_t at = 12; at + 8 <= wav.size();)
            {
                uint32_t length = U32(wav, at + 4);
                if (std::memcmp(&wav[at], "fmt ", 4) == 0 && at + 24 <= wav.size())
                {
                    std::memcpy(&format, &wav[at + 8], 2);
                    std::memcpy(&channels, &wav[at + 10], 2);
                    rate = U32(wav, at + 12);
                    std::memcpy(&bits, &wav[at + 22], 2);
                }
                else if (std::memcmp(&wav[at], "data", 4) == 0)
                {
                    data = at + 8;
                    size = std::min<size_t>(length, wav.size() - data);
                }
                at += 8 + length + (length & 1);
            }
            if (format != 1 || channels == 0 || rate == 0 || (bits != 16 && bits != 8) || data == 0)
                return false;
            size_t frame = channels * bits / 8, frames = size / frame;
            std::vector<float> mono(frames);
            for (size_t i = 0; i < frames; ++i)
            {
                double sum = 0;
                for (uint16_t c = 0; c < channels; ++c)
                {
                    size_t at = data + i * frame + c * bits / 8;
                    if (bits == 16)
                    {
                        int16_t s;
                        std::memcpy(&s, &wav[at], 2);
                        sum += s / 32768.0;
                    }
                    else
                        sum += (wav[at] - 128) / 128.0;
                }
                mono[i] = float(sum / channels);
            }
            double step = double(rate) / 22050.0;
            out.assign(size_t(frames / step), 0.0f);
            for (size_t i = 0; i < out.size(); ++i)
            {
                double s = i * step;
                size_t i0 = size_t(s);
                double f = s - i0;
                float a = mono[std::min(i0, frames - 1)], b = mono[std::min(i0 + 1, frames - 1)];
                out[i] = float(a * (1 - f) + b * f);
            }
            return true;
        }

        std::vector<std::vector<std::string>> Lines(std::string const& text)
        {
            std::vector<std::vector<std::string>> out;
            std::istringstream in(text);
            std::string line;
            while (std::getline(in, line))
            {
                if (!line.empty() && line.back() == '\r')
                    line.pop_back();
                if (line.empty() || line[0] == '#')
                    continue;
                std::vector<std::string> parts;
                std::istringstream fields(line);
                std::string part;
                while (std::getline(fields, part, '\t'))
                    parts.push_back(part);
                out.push_back(parts);
            }
            return out;
        }

        // A list of files in a game folder of the toc's kind: [files] added after its own, once.
        Bytes WithFiles(Bytes const& toc, std::vector<std::string> const& files)
        {
            std::string text(toc.begin(), toc.end());
            for (auto const& file : files)
                if (text.find(file) == std::string::npos)
                {
                    if (!text.empty() && text.back() != '\n')
                        text += "\r\n";
                    text += file + "\r\n";
                }
            return Bytes(text.begin(), text.end());
        }
    }

    bool Recolour(Bytes& blp, double hue, double saturation, double lightness)
    {
        if (blp.size() < 148 + 1024 || std::memcmp(blp.data(), "BLP2", 4) != 0)
            return false;
        if (blp[8] == 1)                                            // a palette: its colours
        {
            for (int i = 0; i < 256; ++i)
            {
                uint8_t* bgra = &blp[148 + i * 4];
                RecolourRgb(bgra[2], bgra[1], bgra[0], hue, saturation, lightness);
            }
            return true;
        }
        Image image;
        if (!Skyborne::Decode(blp, image))
            return false;
        for (size_t i = 0; i + 3 < image.rgba.size(); i += 4)
            RecolourRgb(image.rgba[i], image.rgba[i + 1], image.rgba[i + 2], hue, saturation, lightness);
        blp = EncodePalette(image, Translucent(image));             // as the game's character textures are
        return true;
    }

    namespace
    {
        // An array of a model's header (count, offset) and its items, by size.
        struct Array { uint32_t count, offset; };
        Array ArrayAt(Bytes const& b, size_t at) { return { U32(b, at), U32(b, at + 4) }; }

        // [payload] at the end of [b], 16-aligned; where it is.
        uint32_t Append(Bytes& b, Bytes const& payload)
        {
            while (b.size() % 16)
                b.push_back(0);
            uint32_t at = uint32_t(b.size());
            b.insert(b.end(), payload.begin(), payload.end());
            return at;
        }

        // [array]'s items (of [size] bytes) with [more] after them, at the end of [b], in its header.
        void Grow(Bytes& b, size_t header, size_t size, Bytes const& more)
        {
            Array a = ArrayAt(b, header);
            Bytes all(b.begin() + a.offset, b.begin() + a.offset + size_t(a.count) * size);
            all.insert(all.end(), more.begin(), more.end());
            uint32_t at = Append(b, all);
            Put32(b, header, uint32_t(all.size() / size));
            Put32(b, header + 4, at);
        }

        template <typename T> void Add(Bytes& b, T const& v)
        {
            uint8_t const* p = reinterpret_cast<uint8_t const*>(&v);
            b.insert(b.end(), p, p + sizeof(T));
        }
    }

    bool MergeParts(Bytes& m2, Bytes& skin, Bytes const& parts, std::string& why)
    {
        if (m2.size() < 0x130 || std::memcmp(m2.data(), "MD20", 4) != 0 || U32(m2, 4) != 264)
            return why = "not a 3.3.5 model", false;
        if (skin.size() < 48 || std::memcmp(skin.data(), "SKIN", 4) != 0)
            return why = "not a 3.3.5 skin", false;
        if (parts.size() < 12 || std::memcmp(parts.data(), "NPRT", 4) != 0 || U32(parts, 4) != 2)
            return why = "not the naga's parts", false;
        constexpr size_t H_BONES = 0x2C, H_VERTS = 0x3C, H_TEXTURES = 0x50, H_TEX_REPLACE = 0x68, H_RENDER_FLAGS = 0x70,
            H_BONE_LOOKUP = 0x78, H_TEX_LOOKUP = 0x80, H_TRANSP_LOOKUP = 0x90, H_UV_LOOKUP = 0x98, H_TEX_UNIT_LOOKUP = 0x88,
            H_BOUNDS = 0xA0;
        Array bones = ArrayAt(m2, H_BONES);
        if (bones.count == 0 || bones.offset + size_t(bones.count) * 88 > m2.size())
            return why = "its bones aren't where its header says", false;
        if (ArrayAt(m2, H_TRANSP_LOOKUP).count == 0 || ArrayAt(m2, H_TEX_UNIT_LOOKUP).count == 0)
            return why = "it has no transparency or texture unit look-up to give the parts", false;
        std::vector<std::array<float, 3>> pivots(bones.count);
        int head = 0;
        for (uint32_t i = 0; i < bones.count; ++i)
        {
            std::memcpy(pivots[i].data(), &m2[bones.offset + i * 88 + 76], 12);
            int32_t key;
            std::memcpy(&key, &m2[bones.offset + i * 88], 4);
            if (key == 6)
                head = int(i);
        }
        auto nearest = [&](float const* place, float& distance)
        {
            int best = head;
            distance = 1e9f;
            for (uint32_t i = 0; i < bones.count; ++i)
            {
                float dx = pivots[i][0] - place[0], dy = pivots[i][1] - place[1], dz = pivots[i][2] - place[2];
                float d = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (d < distance)
                {
                    distance = d;
                    best = int(i);
                }
            }
            return best;
        };

        // The skin's arrays, to add to.
        Array sv = ArrayAt(skin, 4), ix = ArrayAt(skin, 12), pr = ArrayAt(skin, 20), se = ArrayAt(skin, 28), ba = ArrayAt(skin, 36);
        if (sv.offset + size_t(sv.count) * 2 > skin.size() || ix.offset + size_t(ix.count) * 2 > skin.size()
            || pr.offset + size_t(pr.count) * 4 > skin.size() || se.offset + size_t(se.count) * 48 > skin.size()
            || ba.offset + size_t(ba.count) * 24 > skin.size())
            return why = "its skin's arrays aren't where its header says", false;
        Bytes skinVertices(skin.begin() + sv.offset, skin.begin() + sv.offset + sv.count * 2);
        Bytes indices(skin.begin() + ix.offset, skin.begin() + ix.offset + ix.count * 2);
        Bytes props(skin.begin() + pr.offset, skin.begin() + pr.offset + pr.count * 4);
        Bytes sections(skin.begin() + se.offset, skin.begin() + se.offset + se.count * 48);
        Bytes batches(skin.begin() + ba.offset, skin.begin() + ba.offset + ba.count * 24);
        uint32_t boneCountMax = U32(skin, 44);

        Array verts = ArrayAt(m2, H_VERTS), textures = ArrayAt(m2, H_TEXTURES), texLookup = ArrayAt(m2, H_TEX_LOOKUP);
        Array flags = ArrayAt(m2, H_RENDER_FLAGS), boneLookup = ArrayAt(m2, H_BONE_LOOKUP), uvLookup = ArrayAt(m2, H_UV_LOOKUP);
        uint32_t vertexCount = verts.count, textureCount = textures.count, lookupCount = texLookup.count;
        uint32_t flagCount = flags.count, boneLookupCount = boneLookup.count;
        Bytes newVertices, newTextures, newLookups, newFlags, newBoneLookup;
        std::vector<std::string> names;                                  // the new textures' names
        std::map<std::string, uint16_t> lookupOf;                         // a texture (type and name) -> its look-up
        std::map<uint32_t, uint16_t> flagOf;
        uint16_t noTransform = uint16_t(uvLookup.count);                  // a new look-up entry: none
        float lo[3], hi[3];
        std::memcpy(lo, &m2[H_BOUNDS], 12);
        std::memcpy(hi, &m2[H_BOUNDS + 12], 12);
        float worst = 0;

        size_t at = 12;
        uint32_t partCount = U32(parts, 8);
        for (uint32_t p = 0; p < partCount; ++p)
        {
            // a geometry: its blend, sizes and uses (each a geoset and a texture)
            if (at + 12 > parts.size())
                return why = "the parts end early", false;
            uint16_t blend, useCount;
            std::memcpy(&blend, &parts[at], 2);
            uint32_t count = U32(parts, at + 2), triangles = U32(parts, at + 6);
            std::memcpy(&useCount, &parts[at + 10], 2);
            at += 12;
            struct Use { uint16_t geoset, type; std::string name; };
            std::vector<Use> uses;
            for (uint16_t u = 0; u < useCount; ++u)
            {
                if (at + 6 > parts.size())
                    return why = "the parts end early", false;
                Use use;
                uint16_t nameLength;
                std::memcpy(&use.geoset, &parts[at], 2);
                std::memcpy(&use.type, &parts[at + 2], 2);
                std::memcpy(&nameLength, &parts[at + 4], 2);
                at += 6;
                if (at + nameLength > parts.size())
                    return why = "the parts end early", false;
                use.name.assign(parts.begin() + at, parts.begin() + at + nameLength);
                at += nameLength;
                uses.push_back(use);
            }
            constexpr size_t VERTEX = 20 * 4 + 4;
            if (at + size_t(count) * VERTEX + size_t(triangles) * 6 > parts.size())
                return why = "the parts end early", false;

            // its bones: the model's at their places
            std::vector<std::array<uint8_t, 4>> local(count);
            std::vector<uint16_t> palette;
            std::vector<std::array<uint8_t, 4>> globals(count);
            for (uint32_t v = 0; v < count; ++v)
            {
                uint8_t const* raw = &parts[at + v * VERTEX];
                uint8_t const* weights = raw + 80;
                for (int j = 0; j < 4; ++j)
                {
                    float place[3], distance;
                    std::memcpy(place, raw + 32 + j * 12, 12);
                    int bone = nearest(place, distance);
                    if (weights[j])
                        worst = std::max(worst, distance);
                    if (bone > 255)
                        return why = "a bone past the 256th", false;
                    globals[v][j] = uint8_t(bone);
                    if (weights[j] && std::find(palette.begin(), palette.end(), uint16_t(bone)) == palette.end())
                        palette.push_back(uint16_t(bone));
                }
            }
            if (palette.size() > 64)
                return why = "a part on more than 64 bones", false;
            if (palette.empty())
                palette.push_back(uint16_t(head));
            uint32_t firstVertex = vertexCount + uint32_t(newVertices.size() / 48);
            for (uint32_t v = 0; v < count; ++v)
            {
                uint8_t const* raw = &parts[at + v * VERTEX];
                uint8_t const* weights = raw + 80;
                for (int j = 0; j < 4; ++j)
                    local[v][j] = weights[j] ? uint8_t(std::find(palette.begin(), palette.end(), uint16_t(globals[v][j])) - palette.begin()) : 0;
                // the model's vertex: position, weights, bones, normal, coordinates (and none second)
                Bytes vertex(48, 0);
                std::memcpy(&vertex[0], raw, 12);
                std::memcpy(&vertex[12], weights, 4);
                std::memcpy(&vertex[16], globals[v].data(), 4);
                std::memcpy(&vertex[20], raw + 12, 12);
                std::memcpy(&vertex[32], raw + 24, 8);
                newVertices.insert(newVertices.end(), vertex.begin(), vertex.end());
                float pos[3];
                std::memcpy(pos, raw, 12);
                for (int c = 0; c < 3; ++c)
                {
                    lo[c] = std::min(lo[c], pos[c]);
                    hi[c] = std::max(hi[c], pos[c]);
                }
            }

            // its triangles in the skin, once
            uint32_t skinStart = uint32_t(skinVertices.size() / 2), indexStart = uint32_t(indices.size() / 2);
            if (indexStart > 65535)
                return why = "the skin's triangles past the 65535th index (the game reads a section's start in 16 bits)", false;
            for (uint32_t v = 0; v < count; ++v)
            {
                Add(skinVertices, uint16_t(firstVertex + v));
                props.insert(props.end(), local[v].begin(), local[v].end());
            }
            float centre[3] = { 0, 0, 0 };
            for (uint32_t t = 0; t < triangles * 3; ++t)
            {
                uint16_t k;
                std::memcpy(&k, &parts[at + count * VERTEX + t * 2], 2);
                if (k >= count)
                    return why = "a triangle names a vertex the part hasn't", false;
                Add(indices, uint16_t(skinStart + k));
            }
            for (uint32_t v = 0; v < count; ++v)
                for (int c = 0; c < 3; ++c)
                {
                    float x;
                    std::memcpy(&x, &parts[at + v * VERTEX + c * 4], 4);
                    centre[c] += x / float(std::max(1u, count));
                }
            uint16_t combo = uint16_t(boneLookupCount + newBoneLookup.size() / 2);
            for (uint16_t b : palette)
                Add(newBoneLookup, b);
            if (!flagOf.count(blend))
            {
                flagOf[blend] = uint16_t(flagCount + newFlags.size() / 4);
                Add(newFlags, uint16_t(0));
                Add(newFlags, blend);
            }

            // each use: a section of its geoset over those triangles, a batch with its texture
            for (auto const& use : uses)
            {
                std::string key = std::to_string(use.type) + ":" + use.name;
                if (!lookupOf.count(key))
                {
                    Add(newTextures, uint32_t(use.type));
                    Add(newTextures, uint32_t(0));
                    Add(newTextures, uint32_t(use.name.size() + 1));
                    Add(newTextures, uint32_t(0));                        // (the name's place, made below)
                    names.push_back(use.name);
                    lookupOf[key] = uint16_t(lookupCount + newLookups.size() / 2);
                    Add(newLookups, int16_t(textureCount + names.size() - 1));
                }
                uint16_t section = uint16_t(sections.size() / 48);
                Add(sections, use.geoset);
                Add(sections, uint16_t(indexStart >> 16));
                Add(sections, uint16_t(skinStart));
                Add(sections, uint16_t(count));
                Add(sections, uint16_t(indexStart & 0xFFFF));
                Add(sections, uint16_t(triangles * 3));
                Add(sections, uint16_t(palette.size()));
                Add(sections, combo);
                Add(sections, uint16_t(1));
                Add(sections, palette[0]);
                for (int r = 0; r < 2; ++r)
                    for (int c = 0; c < 3; ++c)
                        Add(sections, centre[c]);
                Add(sections, 1.0f);
                Add(batches, uint8_t(16));
                Add(batches, int8_t(0));
                Add(batches, uint16_t(0));
                Add(batches, section);
                Add(batches, section);
                Add(batches, int16_t(-1));
                Add(batches, flagOf[blend]);
                Add(batches, uint16_t(0));
                Add(batches, uint16_t(1));
                Add(batches, lookupOf[key]);
                Add(batches, uint16_t(0));
                Add(batches, uint16_t(0));
                Add(batches, noTransform);
            }
            at += size_t(count) * VERTEX + size_t(triangles) * 6;
            boneCountMax = std::max<uint32_t>(boneCountMax, uint32_t(palette.size()));
        }
        if (worst > 0.15f)
            return why = "a part's bone is " + std::to_string(worst) + " yards from any of the model's: not this naga", false;
        if (skinVertices.size() / 2 > 65535)
            return why = "too many vertices for one skin", false;

        // The model: its arrays grown (the new textures' names made, their places in their entries).
        for (size_t t = 0; t < names.size(); ++t)
        {
            Bytes text(names[t].begin(), names[t].end());
            text.push_back(0);
            uint32_t place = Append(m2, text);
            std::memcpy(&newTextures[t * 16 + 12], &place, 4);
        }
        Grow(m2, H_VERTS, 48, newVertices);
        Grow(m2, H_TEXTURES, 16, newTextures);
        Grow(m2, H_TEX_LOOKUP, 2, newLookups);
        Grow(m2, H_RENDER_FLAGS, 4, newFlags);
        Grow(m2, H_BONE_LOOKUP, 2, newBoneLookup);
        Bytes none;
        Add(none, int16_t(-1));
        Grow(m2, H_UV_LOOKUP, 2, none);
        // the texture types' look-up: the hair's (6), where the model hadn't one
        Array replace = ArrayAt(m2, H_TEX_REPLACE);
        std::vector<int16_t> types(std::max<uint32_t>(replace.count, 7), -1);
        for (uint32_t i = 0; i < replace.count; ++i)
            std::memcpy(&types[i], &m2[replace.offset + i * 2], 2);
        for (size_t t = 0; t < names.size(); ++t)
        {
            uint32_t type = U32(newTextures, t * 16);
            if (type && type < types.size() && types[type] < 0)
                types[type] = int16_t(textureCount + t);
        }
        Bytes typeBytes;
        for (int16_t v : types)
            Add(typeBytes, v);
        Put32(m2, H_TEX_REPLACE, uint32_t(types.size()));
        Put32(m2, H_TEX_REPLACE + 4, Append(m2, typeBytes));
        std::memcpy(&m2[H_BOUNDS], lo, 12);
        std::memcpy(&m2[H_BOUNDS + 12], hi, 12);

        // The skin, made again with its arrays.
        Bytes out(48, 0);
        std::memcpy(out.data(), "SKIN", 4);
        size_t header = 4;
        for (auto [data, size] : { std::pair<Bytes*, size_t>{ &skinVertices, 2 }, { &indices, 2 }, { &props, 4 }, { &sections, 48 }, { &batches, 24 } })
        {
            uint32_t place = Append(out, *data);
            Put32(out, header, uint32_t(data->size() / size));
            Put32(out, header + 4, place);
            header += 8;
        }
        Put32(out, 44, boneCountMax);
        skin = std::move(out);
        return true;
    }

    namespace
    {
        // A bone's transform: where its rest pose's points go (a 3 x 3 part and a move).
        struct Affine
        {
            double a[3][3] = { { 1, 0, 0 }, { 0, 1, 0 }, { 0, 0, 1 } };
            double t[3] = { 0, 0, 0 };
        };

        Affine Times(Affine const& x, Affine const& y)
        {
            Affine out;
            for (int i = 0; i < 3; ++i)
            {
                for (int j = 0; j < 3; ++j)
                    out.a[i][j] = x.a[i][0] * y.a[0][j] + x.a[i][1] * y.a[1][j] + x.a[i][2] * y.a[2][j];
                out.t[i] = x.a[i][0] * y.t[0] + x.a[i][1] * y.t[1] + x.a[i][2] * y.t[2] + x.t[i];
            }
            return out;
        }

        Affine Inverse(Affine const& x)
        {
            double const (&m)[3][3] = x.a;
            double det = m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
            Affine out;
            if (std::fabs(det) < 1e-12)
                return out;
            double inv = 1.0 / det;
            out.a[0][0] = (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv;
            out.a[0][1] = (m[0][2] * m[2][1] - m[0][1] * m[2][2]) * inv;
            out.a[0][2] = (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv;
            out.a[1][0] = (m[1][2] * m[2][0] - m[1][0] * m[2][2]) * inv;
            out.a[1][1] = (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv;
            out.a[1][2] = (m[0][2] * m[1][0] - m[0][0] * m[1][2]) * inv;
            out.a[2][0] = (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv;
            out.a[2][1] = (m[0][1] * m[2][0] - m[0][0] * m[2][1]) * inv;
            out.a[2][2] = (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv;
            for (int i = 0; i < 3; ++i)
                out.t[i] = -(out.a[i][0] * x.t[0] + out.a[i][1] * x.t[1] + out.a[i][2] * x.t[2]);
            return out;
        }

        // A key: a time, a move, a turn (x, y, z, w) and a scale.
        struct Key
        {
            uint32_t time = 0;
            double move[3] = { 0, 0, 0 };
            double turn[4] = { 0, 0, 0, 1 };
            double scale[3] = { 1, 1, 1 };
        };

        void TurnMatrix(double const q[4], double r[3][3])
        {
            double x = q[0], y = q[1], z = q[2], w = q[3];
            r[0][0] = 1 - 2 * (y * y + z * z); r[0][1] = 2 * (x * y - z * w); r[0][2] = 2 * (x * z + y * w);
            r[1][0] = 2 * (x * y + z * w); r[1][1] = 1 - 2 * (x * x + z * z); r[1][2] = 2 * (y * z - x * w);
            r[2][0] = 2 * (x * z - y * w); r[2][1] = 2 * (y * z + x * w); r[2][2] = 1 - 2 * (x * x + y * y);
        }

        void MatrixTurn(double const r[3][3], double q[4])
        {
            double trace = r[0][0] + r[1][1] + r[2][2];
            if (trace > 0)
            {
                double s = std::sqrt(trace + 1.0) * 2;
                q[0] = (r[2][1] - r[1][2]) / s; q[1] = (r[0][2] - r[2][0]) / s; q[2] = (r[1][0] - r[0][1]) / s; q[3] = 0.25 * s;
            }
            else if (r[0][0] > r[1][1] && r[0][0] > r[2][2])
            {
                double s = std::sqrt(1.0 + r[0][0] - r[1][1] - r[2][2]) * 2;
                q[0] = 0.25 * s; q[1] = (r[0][1] + r[1][0]) / s; q[2] = (r[0][2] + r[2][0]) / s; q[3] = (r[2][1] - r[1][2]) / s;
            }
            else if (r[1][1] > r[2][2])
            {
                double s = std::sqrt(1.0 + r[1][1] - r[0][0] - r[2][2]) * 2;
                q[0] = (r[0][1] + r[1][0]) / s; q[1] = 0.25 * s; q[2] = (r[1][2] + r[2][1]) / s; q[3] = (r[0][2] - r[2][0]) / s;
            }
            else
            {
                double s = std::sqrt(1.0 + r[2][2] - r[0][0] - r[1][1]) * 2;
                q[0] = (r[0][2] + r[2][0]) / s; q[1] = (r[1][2] + r[2][1]) / s; q[2] = 0.25 * s; q[3] = (r[1][0] - r[0][1]) / s;
            }
            double n = std::sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
            int sign = q[3] < 0 ? -1 : 1;
            for (int i = 0; i < 4; ++i)
                q[i] = n > 0 ? sign * q[i] / n : (i == 3 ? 1 : 0);
        }

        // A key as a transform: [pivot]'s move, turn and scale about it (the game's way), or (no pivot) as it is.
        Affine KeyTransform(Key const& k, double const* pivot)
        {
            Affine out;
            double r[3][3];
            TurnMatrix(k.turn, r);
            for (int i = 0; i < 3; ++i)
                for (int j = 0; j < 3; ++j)
                    out.a[i][j] = r[i][j] * k.scale[j];
            for (int i = 0; i < 3; ++i)
            {
                out.t[i] = k.move[i];
                if (pivot)
                    out.t[i] += pivot[i] - (out.a[i][0] * pivot[0] + out.a[i][1] * pivot[1] + out.a[i][2] * pivot[2]);
            }
            return out;
        }

        // A transform as a key about [pivot] (the game's way).
        Key TransformKey(Affine const& x, double const* pivot, uint32_t time)
        {
            Key k;
            k.time = time;
            double r[3][3];
            for (int j = 0; j < 3; ++j)
            {
                double n = std::sqrt(x.a[0][j] * x.a[0][j] + x.a[1][j] * x.a[1][j] + x.a[2][j] * x.a[2][j]);
                k.scale[j] = n;
                for (int i = 0; i < 3; ++i)
                    r[i][j] = n > 1e-12 ? x.a[i][j] / n : (i == j ? 1 : 0);
            }
            MatrixTurn(r, k.turn);
            for (int i = 0; i < 3; ++i)
                k.move[i] = x.t[i] - pivot[i] + (x.a[i][0] * pivot[0] + x.a[i][1] * pivot[1] + x.a[i][2] * pivot[2]);
            return k;
        }

        // Keys blended at [time]: linear (the turns' blend normalized).
        Key KeyAt(std::vector<Key> const& keys, uint32_t time)
        {
            if (keys.empty())
                return Key();
            if (keys.size() == 1 || time <= keys.front().time)
                return keys.front();
            for (size_t i = 0; i + 1 < keys.size(); ++i)
            {
                Key const& a = keys[i];
                Key const& b = keys[i + 1];
                if (time > b.time)
                    continue;
                double f = b.time > a.time ? double(time - a.time) / double(b.time - a.time) : 0.0;
                Key out;
                out.time = time;
                double dot = a.turn[0] * b.turn[0] + a.turn[1] * b.turn[1] + a.turn[2] * b.turn[2] + a.turn[3] * b.turn[3];
                double n = 0;
                for (int j = 0; j < 4; ++j)
                {
                    out.turn[j] = a.turn[j] * (1 - f) + (dot < 0 ? -b.turn[j] : b.turn[j]) * f;
                    n += out.turn[j] * out.turn[j];
                }
                n = std::sqrt(n);
                for (int j = 0; j < 4; ++j)
                    out.turn[j] = n > 0 ? out.turn[j] / n : (j == 3 ? 1 : 0);
                for (int j = 0; j < 3; ++j)
                {
                    out.move[j] = a.move[j] * (1 - f) + b.move[j] * f;
                    out.scale[j] = a.scale[j] * (1 - f) + b.scale[j] * f;
                }
                return out;
            }
            return keys.back();
        }

        // The keys without those their neighbours' blend gives back (within [turn] in a turn's numbers and
        // [move] in a move's and a scale's), one key where they're all the same.
        std::vector<Key> Reduced(std::vector<Key> const& keys, double turn = 0.0015, double move = 0.0015)
        {
            if (keys.size() <= 2)
                return keys;
            auto close = [&](Key const& k, Key const& got)
            {
                double plus = 0, minus = 0;
                for (int j = 0; j < 4; ++j)
                {
                    plus = std::max(plus, std::fabs(got.turn[j] - k.turn[j]));
                    minus = std::max(minus, std::fabs(got.turn[j] + k.turn[j]));
                }
                if (std::min(plus, minus) > turn)
                    return false;
                for (int j = 0; j < 3; ++j)
                    if (std::fabs(got.move[j] - k.move[j]) > move || std::fabs(got.scale[j] - k.scale[j]) > move)
                        return false;
                return true;
            };
            std::vector<Key> out { keys.front() };
            size_t i = 0;
            while (i + 1 < keys.size())
            {
                size_t j = i + 1;
                while (j + 1 < keys.size())
                {
                    std::vector<Key> span { keys[i], keys[j + 1] };
                    bool all = true;
                    for (size_t m = i + 1; m <= j && all; ++m)
                        all = close(keys[m], KeyAt(span, keys[m].time));
                    if (!all)
                        break;
                    ++j;
                }
                out.push_back(keys[j]);
                i = j;
            }
            if (out.size() == 2 && close(out[1], out[0]))
                out.resize(1);
            return out;
        }

        int16_t PackTurn(double v)
        {
            long x = v >= 0 ? std::lround(v * 32767.0 - 32768.0) : std::lround(v * 32767.0 + 32767.0);
            return int16_t(std::max(-32768L, std::min(32767L, x)));
        }

        double UnpackTurn(int16_t x) { return (x < 0 ? x + 32768.0 : x - 32767.0) / 32767.0; }

        float F32(Bytes const& b, size_t at)
        {
            float v = 0;
            if (at + 4 <= b.size())
                std::memcpy(&v, &b[at], 4);
            return v;
        }

        // A model's animated values (3.3.5's layout): where each track is, the size of its values (0:
        // times alone), and the bone and which of its tracks (0 move, 1 turn, 2 scale) it is, or -1.
        struct Track { size_t at; uint32_t size; int bone, which; };

        bool Tracks(Bytes const& m, std::vector<Track>& out, std::string& why)
        {
            auto array = [&](size_t header, size_t item) -> Array
            {
                Array a = ArrayAt(m, header);
                if (a.count && a.offset + size_t(a.count) * item > m.size())
                    a.count = UINT32_MAX;
                return a;
            };
            Array a = array(0x2C, 88);
            if (a.count == UINT32_MAX)
                return why = "its bones aren't where its header says", false;
            for (uint32_t b = 0; b < a.count; ++b)
                for (int k = 0; k < 3; ++k)
                    out.push_back({ a.offset + b * 88 + 16 + size_t(k) * 20, k == 1 ? 8u : 12u, int(b), k });
            struct Kind { size_t header, item; std::vector<std::pair<size_t, uint32_t>> tracks; };
            for (Kind const& kind : { Kind { 0x48, 40, { { 0, 12 }, { 20, 2 } } }, Kind { 0x58, 20, { { 0, 2 } } },
                                      Kind { 0x60, 60, { { 0, 12 }, { 20, 16 }, { 40, 12 } } }, Kind { 0xF0, 40, { { 20, 1 } } },
                                      Kind { 0x110, 100, { { 16, 36 }, { 48, 36 }, { 80, 12 } } }, Kind { 0x100, 36, { { 24, 0 } } } })
            {
                Array k = array(kind.header, kind.item);
                if (k.count == UINT32_MAX)
                    return why = "its arrays aren't where its header says", false;
                for (uint32_t i = 0; i < k.count; ++i)
                    for (auto const& [off, size] : kind.tracks)
                        out.push_back({ k.offset + i * kind.item + off, size, -1, -1 });
            }
            for (size_t header : { size_t(0x108), size_t(0x120), size_t(0x128) })
                if (ArrayAt(m, header).count)
                    return why = "it has lights, ribbons or particles (their animations aren't known here)", false;
            return true;
        }
    }

    bool MergeEmotes(Bytes& m2, Bytes const& emotes, std::string& why, size_t* added)
    {
        if (added)
            *added = 0;
        if (m2.size() < 0x130 || std::memcmp(m2.data(), "MD20", 4) != 0 || U32(m2, 4) != 264)
            return why = "not a 3.3.5 model", false;
        if (emotes.size() < 16 || std::memcmp(emotes.data(), "NEMO", 4) != 0 || U32(emotes, 4) != 2)
            return why = "not the naga's emotes", false;
        constexpr uint32_t SEQ = 64, IN_MODEL = 0x20, NONE = 0xFFFF;
        constexpr size_t H_SEQS = 0x1C, H_SEQ_LOOKUP = 0x24, H_BONES = 0x2C;

        // The emotes' skeleton (today's naga's: each bone's place, parent and key) and sequences.
        uint32_t sourceCount = U32(emotes, 8), sequenceCount = U32(emotes, 12);
        size_t at = 16;
        if (at + size_t(sourceCount) * 16 > emotes.size())
            return why = "the emotes end early", false;
        std::vector<std::array<double, 3>> sourcePlace(sourceCount);
        std::vector<int> sourceParent(sourceCount), sourceKey(sourceCount);
        for (uint32_t s = 0; s < sourceCount; ++s, at += 16)
        {
            for (int j = 0; j < 3; ++j)
                sourcePlace[s][j] = F32(emotes, at + 4 * j);
            int16_t parent, key;
            std::memcpy(&parent, &emotes[at + 12], 2);
            std::memcpy(&key, &emotes[at + 14], 2);
            sourceParent[s] = parent;
            sourceKey[s] = key;
            if (parent >= int(s))
                return why = "the emotes' bones come before their parents", false;
        }
        struct Sequence { Bytes record; uint16_t alias; std::vector<std::vector<Key>> keys; };
        std::vector<Sequence> sequences;
        for (uint32_t q = 0; q < sequenceCount; ++q)
        {
            if (at + SEQ + 4 > emotes.size())
                return why = "the emotes end early", false;
            Sequence seq;
            seq.record.assign(emotes.begin() + at, emotes.begin() + at + SEQ);
            seq.alias = uint16_t(emotes[at + SEQ] | (emotes[at + SEQ + 1] << 8));
            at += SEQ + 4;
            if (seq.alias == NONE)
            {
                seq.keys.resize(sourceCount);
                for (uint32_t s = 0; s < sourceCount; ++s)
                {
                    uint32_t n = U32(emotes, at);
                    at += 4;
                    if (at + size_t(n) * 44 > emotes.size())
                        return why = "the emotes end early", false;
                    for (uint32_t i = 0; i < n; ++i, at += 44)
                    {
                        Key k;
                        k.time = U32(emotes, at);
                        for (int j = 0; j < 3; ++j)
                        {
                            k.move[j] = F32(emotes, at + 4 + 4 * j);
                            k.scale[j] = F32(emotes, at + 32 + 4 * j);
                        }
                        for (int j = 0; j < 4; ++j)
                            k.turn[j] = F32(emotes, at + 16 + 4 * j);
                        seq.keys[s].push_back(k);
                    }
                }
            }
            sequences.push_back(std::move(seq));
        }

        // The model's bones, sequences and tracks.
        Array bones = ArrayAt(m2, H_BONES), seqs = ArrayAt(m2, H_SEQS);
        if (bones.count == 0 || bones.offset + size_t(bones.count) * 88 > m2.size() || seqs.offset + size_t(seqs.count) * SEQ > m2.size())
            return why = "its bones or sequences aren't where its header says", false;
        std::vector<Track> tracks;
        if (!Tracks(m2, tracks, why))
            return false;
        std::vector<std::array<double, 3>> pivot(bones.count);
        std::vector<int> parent(bones.count), key(bones.count);
        for (uint32_t b = 0; b < bones.count; ++b)
        {
            size_t o = bones.offset + b * 88;
            int32_t k;
            int16_t p;
            std::memcpy(&k, &m2[o], 4);
            std::memcpy(&p, &m2[o + 8], 2);
            key[b] = k;
            parent[b] = p;
            if (p >= int(b))
                return why = "its bones come before their parents", false;
            for (int j = 0; j < 3; ++j)
                pivot[b][j] = F32(m2, o + 76 + 4 * j);
        }
        std::vector<std::pair<uint16_t, uint16_t>> ids;
        for (uint32_t k = 0; k < seqs.count; ++k)
            ids.emplace_back(uint16_t(m2[seqs.offset + k * SEQ] | (m2[seqs.offset + k * SEQ + 1] << 8)),
                             uint16_t(m2[seqs.offset + k * SEQ + 2] | (m2[seqs.offset + k * SEQ + 3] << 8)));
        int stand = -1;
        for (uint32_t k = 0; k < seqs.count && stand < 0; ++k)
            if (ids[k].first == 0 && ids[k].second == 0)
                stand = int(k);
        if (stand < 0 || !(U32(m2, seqs.offset + stand * SEQ + 12) & IN_MODEL))
            return why = "its stand isn't in the model", false;

        // Each bone of the model's at an emote bone's place (within 2 cm): where several are, the one with
        // its key, then its parent's place, then its grandparent's.
        auto near = [](std::array<double, 3> const& a, std::array<double, 3> const& b)
        {
            double dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
            return std::sqrt(dx * dx + dy * dy + dz * dz) < 0.02;
        };
        auto placeUp = [](std::vector<std::array<double, 3>> const& places, std::vector<int> const& parents, int b, int up)
        {
            for (int i = 0; i < up && b >= 0; ++i)
                b = parents[b];
            return b < 0 ? std::array<double, 3> { 0, 0, 0 } : places[b];
        };
        std::vector<int> source(bones.count, -1);
        for (uint32_t b = 0; b < bones.count; ++b)
        {
            int best = -1, bestScore = -1;
            for (uint32_t s = 0; s < sourceCount; ++s)
            {
                if (!near(sourcePlace[s], pivot[b]))
                    continue;
                int score = (key[b] >= 0 && sourceKey[s] == key[b] ? 4 : 0)
                    + (near(placeUp(sourcePlace, sourceParent, int(s), 1), placeUp(pivot, parent, int(b), 1)) ? 2 : 0)
                    + (near(placeUp(sourcePlace, sourceParent, int(s), 2), placeUp(pivot, parent, int(b), 2)) ? 1 : 0);
                if (score > bestScore)
                {
                    best = int(s);
                    bestScore = score;
                }
            }
            source[b] = best;
        }

        // Each bone's own transform as the model stands (its stand's start), and which of its tracks are
        // a global sequence's (they keep their own keys).
        auto firstKey = [&](Track const& tr, uint32_t seq, double* value)
        {
            uint16_t interp = uint16_t(m2[tr.at] | (m2[tr.at + 1] << 8));
            int16_t gseq;
            std::memcpy(&gseq, &m2[tr.at + 2], 2);
            Array times = ArrayAt(m2, tr.at + 4), values = ArrayAt(m2, tr.at + 12);
            uint32_t use = gseq >= 0 ? 0 : seq;
            if (use >= times.count || use >= values.count)
                return;
            Array keys = ArrayAt(m2, values.offset + use * 8);
            if (keys.count == 0 || keys.offset + tr.size * (interp >= 2 ? 3 : 1) > m2.size())
                return;
            if (tr.which == 1)
            {
                for (int j = 0; j < 4; ++j)
                {
                    int16_t x;
                    std::memcpy(&x, &m2[keys.offset + 2 * j], 2);
                    value[j] = UnpackTurn(x);
                }
            }
            else
                for (int j = 0; j < 3; ++j)
                    value[j] = F32(m2, keys.offset + 4 * j);
        };
        std::vector<Affine> still(bones.count);
        std::vector<std::array<bool, 3>> global(bones.count, { false, false, false });
        for (Track const& tr : tracks)
        {
            if (tr.bone < 0)
                continue;
            int16_t gseq;
            std::memcpy(&gseq, &m2[tr.at + 2], 2);
            global[tr.bone][tr.which] = gseq >= 0;
        }
        for (uint32_t b = 0; b < bones.count; ++b)
        {
            Key k;
            firstKey(tracks[b * 3 + 0], uint32_t(stand), k.move);
            firstKey(tracks[b * 3 + 1], uint32_t(stand), k.turn);
            firstKey(tracks[b * 3 + 2], uint32_t(stand), k.scale);
            still[b] = KeyTransform(k, pivot[b].data());
        }

        // The new sequences (those the model hasn't): each bone's own keys, from where the emotes put it
        // in the world and where what it hangs from is.
        std::set<uint16_t> have;
        for (auto const& id : ids)
            have.insert(id.first);
        std::vector<Sequence const*> fresh;
        std::vector<std::vector<std::vector<Key>>> boneKeys;          // per new sequence, per bone (empty: an alias)
        for (Sequence const& seq : sequences)
        {
            uint16_t id = uint16_t(seq.record[0] | (seq.record[1] << 8));
            if (have.count(id))
                continue;
            if (seq.alias != NONE)
            {
                bool found = have.count(seq.alias) > 0;
                for (Sequence const* f : fresh)
                    found |= uint16_t(f->record[0] | (f->record[1] << 8)) == seq.alias;
                if (!found)
                    continue;
                fresh.push_back(&seq);
                boneKeys.emplace_back();
                have.insert(id);
                continue;
            }
            std::set<uint32_t> timeSet;
            for (auto const& ks : seq.keys)
                for (Key const& k : ks)
                    timeSet.insert(k.time);
            std::vector<uint32_t> times(timeSet.begin(), timeSet.end());
            if (times.empty())
                times.push_back(0);
            size_t n = times.size();
            std::vector<std::vector<Affine>> sourceWorld(sourceCount, std::vector<Affine>(n));
            for (uint32_t s = 0; s < sourceCount; ++s)
                for (size_t i = 0; i < n; ++i)
                {
                    Affine own = KeyTransform(KeyAt(seq.keys[s], times[i]), nullptr);
                    sourceWorld[s][i] = sourceParent[s] >= 0 ? Times(sourceWorld[sourceParent[s]][i], own) : own;
                }
            std::vector<std::vector<Affine>> world(bones.count, std::vector<Affine>(n));
            std::vector<std::vector<Key>> keys(bones.count);
            for (uint32_t b = 0; b < bones.count; ++b)
            {
                bool mapped = source[b] >= 0 && !seq.keys[source[b]].empty();
                std::vector<Key> own(n);
                for (size_t i = 0; i < n; ++i)
                {
                    Affine above = parent[b] >= 0 ? world[parent[b]][i] : Affine();
                    world[b][i] = mapped ? sourceWorld[source[b]][i] : Times(above, still[b]);
                    own[i] = TransformKey(Times(Inverse(above), world[b][i]), pivot[b].data(), times[i]);
                }
                keys[b] = Reduced(own);
            }
            fresh.push_back(&seq);
            boneKeys.push_back(std::move(keys));
            have.insert(id);
        }
        if (fresh.empty())
            return true;

        // Every track: entries for the new sequences (a bone's own keys, else its stand's).
        uint32_t oldCount = seqs.count, total = oldCount + uint32_t(fresh.size());
        std::set<int> animated;
        for (Track const& tr : tracks)
        {
            uint16_t interp = uint16_t(m2[tr.at] | (m2[tr.at + 1] << 8));
            int16_t gseq;
            std::memcpy(&gseq, &m2[tr.at + 2], 2);
            if (gseq >= 0)
                continue;
            Array times = ArrayAt(m2, tr.at + 4), values = ArrayAt(m2, tr.at + 12);
            if (times.count == 1 && oldCount > 1 && tr.bone < 0)
                continue;                                              // (one value for every sequence, as the game's own have: as it is)
            if (times.count && times.count != oldCount)
                return why = "a track with " + std::to_string(times.count) + " entries for " + std::to_string(oldCount) + " sequences", false;
            if (tr.size && times.count != values.count)
                return why = "a track whose times and values don't match", false;
            if (times.offset + size_t(times.count) * 8 > m2.size() || (tr.size && values.offset + size_t(values.count) * 8 > m2.size()))
                return why = "a track's entries aren't where it says", false;
            Bytes newTimes, newValues;
            if (times.count)
            {
                newTimes.assign(m2.begin() + times.offset, m2.begin() + times.offset + times.count * 8);
                if (tr.size)
                    newValues.assign(m2.begin() + values.offset, m2.begin() + values.offset + values.count * 8);
            }
            else
            {
                newTimes.assign(size_t(oldCount) * 8, 0);
                if (tr.size)
                    newValues.assign(size_t(oldCount) * 8, 0);
            }
            Bytes standTimes(8, 0), standValues(8, 0);
            if (times.count)
            {
                std::copy(newTimes.begin() + stand * 8, newTimes.begin() + stand * 8 + 8, standTimes.begin());
                if (tr.size)
                    std::copy(newValues.begin() + stand * 8, newValues.begin() + stand * 8 + 8, standValues.begin());
            }
            bool got = false;
            for (size_t f = 0; f < fresh.size(); ++f)
            {
                bool own = tr.bone >= 0 && !boneKeys[f].empty() && !global[tr.bone][tr.which];
                if (own)
                {
                    std::vector<Key> const& ks = boneKeys[f][tr.bone];
                    bool rest = true;
                    for (Key const& k : ks)
                        for (int j = 0; j < 3; ++j)
                            rest &= tr.which == 0 ? std::fabs(k.move[j]) < 1e-4 : tr.which == 2 ? std::fabs(k.scale[j] - 1) < 1e-4
                                : std::fabs(std::fabs(k.turn[3]) - 1) < 1e-5;
                    if (rest && times.count == 0)
                        own = false;
                    else
                    {
                        if (interp >= 2)
                            return why = "a bone's track with tangents (its keys aren't the kind this writes)", false;
                        Bytes t, v;
                        for (Key const& k : ks)
                        {
                            Add(t, k.time);
                            if (tr.which == 1)
                                for (int j = 0; j < 4; ++j)
                                    Add(v, PackTurn(k.turn[j]));
                            else
                                for (int j = 0; j < 3; ++j)
                                    Add(v, float(tr.which == 0 ? k.move[j] : k.scale[j]));
                        }
                        Bytes entry;
                        Add(entry, uint32_t(ks.size()));
                        Add(entry, Append(m2, t));
                        newTimes.insert(newTimes.end(), entry.begin(), entry.end());
                        entry.clear();
                        Add(entry, uint32_t(ks.size()));
                        Add(entry, Append(m2, v));
                        newValues.insert(newValues.end(), entry.begin(), entry.end());
                        got = true;
                        animated.insert(tr.bone);
                        continue;
                    }
                }
                newTimes.insert(newTimes.end(), standTimes.begin(), standTimes.end());
                if (tr.size)
                    newValues.insert(newValues.end(), standValues.begin(), standValues.end());
            }
            if (times.count == 0 && !got)
                continue;
            uint32_t timesAt = Append(m2, newTimes);
            Put32(m2, tr.at + 4, total);
            Put32(m2, tr.at + 8, timesAt);
            if (tr.size)
            {
                uint32_t valuesAt = Append(m2, newValues);
                Put32(m2, tr.at + 12, total);
                Put32(m2, tr.at + 16, valuesAt);
            }
            if (interp == 0 && got)
            {
                m2[tr.at] = 1;
                m2[tr.at + 1] = 0;
            }
        }

        // The sequences: the new ones after the model's (its stand's bounds, no variation after them, an
        // alias pointing at its sequence), and the look-up by id.
        Bytes records(m2.begin() + seqs.offset, m2.begin() + seqs.offset + size_t(oldCount) * SEQ);
        for (Sequence const* f : fresh)
            ids.emplace_back(uint16_t(f->record[0] | (f->record[1] << 8)), 0);
        for (size_t f = 0; f < fresh.size(); ++f)
        {
            Bytes r = fresh[f]->record;
            std::copy(records.begin() + stand * SEQ + 32, records.begin() + stand * SEQ + 60, r.begin() + 32);
            uint16_t index = uint16_t(oldCount + f);
            if (fresh[f]->alias != NONE)
                for (size_t k = 0; k < ids.size(); ++k)
                    if (ids[k].first == fresh[f]->alias && ids[k].second == 0)
                    {
                        index = uint16_t(k);
                        break;
                    }
            int16_t none = -1;
            std::memcpy(&r[60], &none, 2);
            std::memcpy(&r[62], &index, 2);
            records.insert(records.end(), r.begin(), r.end());
        }
        uint32_t recordsAt = Append(m2, records);
        Put32(m2, H_SEQS, total);
        Put32(m2, H_SEQS + 4, recordsAt);
        uint16_t top = 0;
        for (auto const& id : ids)
            top = std::max(top, id.first);
        std::vector<int16_t> lookup(size_t(top) + 1, -1);
        for (size_t k = 0; k < ids.size(); ++k)
            if (lookup[ids[k].first] < 0)
                lookup[ids[k].first] = int16_t(k);
        Bytes table;
        for (int16_t v : lookup)
            Add(table, v);
        uint32_t lookupAt = Append(m2, table);
        Put32(m2, H_SEQ_LOOKUP, uint32_t(lookup.size()));
        Put32(m2, H_SEQ_LOOKUP + 4, lookupAt);
        // (a bone that moves now: flagged so, or the game leaves it where it is)
        for (int b : animated)
            Put32(m2, bones.offset + size_t(b) * 88 + 4, U32(m2, bones.offset + size_t(b) * 88 + 4) | 0x200);
        if (added)
            *added = fresh.size();
        return true;
    }

    Bytes MixNarration(std::vector<std::pair<uint32_t, Bytes>> const& parts)
    {
        std::vector<float> mix;
        for (auto const& [ms, wav] : parts)
        {
            std::vector<float> samples;
            if (!Samples(wav, samples))
                continue;
            size_t at = size_t(ms) * 22050 / 1000;
            if (mix.size() < at + samples.size())
                mix.resize(at + samples.size(), 0.0f);
            for (size_t i = 0; i < samples.size(); ++i)
                mix[at + i] += samples[i];
        }
        Bytes out(44 + mix.size() * 2);
        std::memcpy(&out[0], "RIFF", 4);
        Put32(out, 4, uint32_t(out.size() - 8));
        std::memcpy(&out[8], "WAVEfmt ", 8);
        Put32(out, 16, 16);
        uint16_t pcm = 1, mono = 1, align = 2, bits = 16;
        std::memcpy(&out[20], &pcm, 2);
        std::memcpy(&out[22], &mono, 2);
        Put32(out, 24, 22050);
        Put32(out, 28, 44100);
        std::memcpy(&out[32], &align, 2);
        std::memcpy(&out[34], &bits, 2);
        std::memcpy(&out[36], "data", 4);
        Put32(out, 40, uint32_t(mix.size() * 2));
        for (size_t i = 0; i < mix.size(); ++i)
        {
            int16_t s = int16_t(std::lround(std::clamp(mix[i], -1.0f, 1.0f) * 32767));
            std::memcpy(&out[44 + i * 2], &s, 2);
        }
        return out;
    }

    void RemovePatch(fs::path const& clientData, Log const& log)
    {
        std::string locale = Locale(clientData);
        if (locale.empty())
            return;
        fs::path patch = PatchPath(clientData, locale);
        std::error_code error;
        if (!fs::exists(With(patch, MARK_SUFFIX), error))
            return;
        fs::remove(patch, error);
        fs::remove(With(patch, ASIDE_SUFFIX), error);
        fs::remove(With(patch, MARK_SUFFIX), error);
        log("The races' patch is out of the game");
    }

    void SetPatchAside(fs::path const& clientData, Log const& log)
    {
        std::string locale = Locale(clientData);
        if (locale.empty())
            return;
        fs::path patch = PatchPath(clientData, locale);
        std::error_code error;
        if (!fs::exists(With(patch, MARK_SUFFIX), error) || !fs::exists(patch, error))
            return;
        fs::remove(With(patch, ASIDE_SUFFIX), error);
        fs::rename(patch, With(patch, ASIDE_SUFFIX), error);
        if (error)
            log("The races' patch couldn't be set aside: " + error.message());
        else
            log("The races' patch is out of the game, kept beside it for a realm with the races");
    }

    void PutCameras(fs::path const& moduleData, fs::path const& serverData, Log const& log)
    {
        std::error_code error;
        fs::path folder = serverData / "Cameras";
        fs::create_directories(folder, error);
        for (char const* name : { "FlybyMurloc.m2", "FlybyNaga.m2" })
        {
            Bytes ours = ReadFile(moduleData / "Cameras" / name);
            if (ours.empty())
            {
                log(std::string("The intro's camera ") + name + " isn't in the module");
                continue;
            }
            if (ReadFile(folder / name) == ours)
                continue;
            std::ofstream out(folder / name, std::ios::binary | std::ios::trunc);
            out.write(reinterpret_cast<char const*>(ours.data()), std::streamsize(ours.size()));
            if (!out)
                log("Couldn't write " + (folder / name).string());
        }
    }

    bool UpdatePatch(fs::path const& moduleData, fs::path const& clientData, Log const& log)
    {
        std::string locale = Locale(clientData);
        if (locale.empty())
        {
            log("No game language folder in " + clientData.string() + ": the races' patch isn't made");
            return false;
        }
        std::error_code error;
        fs::path patch = PatchPath(clientData, locale), mark = With(patch, MARK_SUFFIX);
        bool ours = fs::exists(mark, error);
        if (!ours && fs::exists(patch, error))
        {
            log(patch.string() + " isn't this module's: left alone, so the game won't know the races");
            return false;
        }
        if (ours && !fs::exists(patch, error) && fs::exists(With(patch, ASIDE_SUFFIX), error))
            fs::rename(With(patch, ASIDE_SUFFIX), patch, error);
        auto start = std::chrono::steady_clock::now();
        Game game(clientData, Skip(locale));
        if (game.archives.empty())
        {
            log("No game in " + clientData.string());
            return false;
        }

        // What it's made from: the module's files and the game's archives.
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
        // What the server package made from the game's files of today (tools/murloc_model.py: the
        // murlocs' model and textures; tools/naga_parts.py: the naga's headdresses and outfits;
        // tools/naga_emotes.py: the naga's emotes; tools/naga_models.py: the naga's story's sea witch,
        // warden and Queen Azshara; tools/naga_voices.py: its Warcraft III voices) in data/files, each
        // list written last.
        fs::path packaged = moduleData.parent_path() / "files";
        std::map<std::string, std::vector<std::string>> packagedFiles;          // list -> its files
        for (char const* list : PACKAGED_LISTS)
        {
            std::istringstream in(Text(packaged / list));
            std::string name;
            stamp.Add(list);
            while (std::getline(in, name))
            {
                if (!name.empty() && name.back() == '\r')
                    name.pop_back();
                if (name.empty())
                    continue;
                packagedFiles[list].push_back(name);
                stamp.Add(name);
                stamp.Add(std::to_string(fs::file_size(packaged / name, error)));
            }
        }
        if (ours && fs::exists(patch, error) && Text(mark) == stamp.Hex() + "\n")
            return true;

        log("Making the races' patch for the game (" + patch.string() + ")");
        fs::path part = With(patch, ".part");
        MpqWriter writer(part);
        size_t tables = 0, files = 0;
        std::vector<std::string> problems;

        // Every texture the patch writes (lower case), so the tables name only textures that are there.
        std::set<std::string> written;
        auto add = [&](std::string const& name, Bytes const& data)
        {
            writer.Add(name, data);
            written.insert(Lower(name));
            ++files;
        };

        // The naga's colours (data/client/looks.txt), then the murlocs' packaged files. What the game draws
        // into a character's composed texture (its skin, faces and underwear) is made as the game's
        // own character textures are, palettized and at the scale of the skin it's drawn over: the
        // game reads only those there (a compressed or missing one was drawn green, and broke the
        // game's memory as the character was made: crash report #110).
        struct Colour { uint32_t source; double recipe[3]; bool changed; };
        std::map<std::string, std::map<uint32_t, Colour>> nagaColours;       // sex, colour
        for (char const* sex : { "Male", "Female" })
            for (uint32_t c = 0; c < 5; ++c)
                nagaColours[sex][c] = { c, { -1, 1, 1 }, false };          // the game's five
        for (auto const& line : Lines(Text(moduleData / "looks.txt")))
        {
            if (line[0] == "naga_colour" && line.size() == 7)
                nagaColours[line[1] == "0" ? "Male" : "Female"][uint32_t(std::stoul(line[2]))]
                    = { uint32_t(std::stoul(line[3])), { std::stod(line[4]), std::stod(line[5]), std::stod(line[6]) }, true };
        }
        for (auto const& [sex, colours] : nagaColours)
        {
            std::string p = "Character\\Naga_\\" + sex + "\\Naga_" + sex;
            for (auto const& [colour, how] : colours)
            {
                char from[8], to[8];
                std::snprintf(from, sizeof(from), "00_%02u", how.source);
                std::snprintf(to, sizeof(to), "00_%02u", colour);
                // The skin and its extra (the fins and face the model draws as they are): the game's,
                // recoloured for a new colour.
                uint32_t skinWidth = 0;
                for (char const* extra : { "", "_Extra" })
                {
                    Bytes texture;
                    std::string name = p + "Skin" + from + extra + ".blp";
                    if (!game.Read(name, texture))
                    {
                        problems.push_back(name + " isn't in the game");
                        continue;
                    }
                    if (!*extra)
                        skinWidth = BlpWidth(texture);
                    if (how.changed || (!*extra && texture.size() > 8 && texture[8] != 1))
                    {
                        if (!Recolour(texture, how.changed ? how.recipe[0] : -1, how.changed ? how.recipe[1] : 1, how.changed ? how.recipe[2] : 1))
                        {
                            problems.push_back(name + " isn't a texture this knows");
                            continue;
                        }
                        add(p + "Skin" + to + extra + ".blp", texture);
                    }
                }
                if (!skinWidth)
                    continue;
                // The faces and underwear (the game's own are a quarter the size and compressed): made
                // the skin's scale, palettized, under the colour's own names.
                for (auto [kind, w, h] : { std::tuple<char const*, uint32_t, uint32_t>{ "FaceLower", 128, 64 }, { "FaceUpper", 128, 32 },
                                           { "NakedPelvisSkin", 128, 64 }, { "NakedTorsoSkin", 128, 64 } })
                {
                    Bytes texture;
                    Image image;
                    std::string name = p + kind + from + ".blp";
                    if (!game.Read(name, texture) || !Skyborne::Decode(texture, image) || !image.width || !image.height)
                    {
                        problems.push_back(name + " isn't in the game");
                        continue;
                    }
                    add(p + kind + to + ".blp", Composited(image, skinWidth, w, h, how.changed ? how.recipe : nullptr));
                }
            }
        }
        for (size_t i = 0; i < std::size(PACKAGED_LISTS); ++i)
            if (packagedFiles[PACKAGED_LISTS[i]].empty())
                problems.push_back(std::string("no ") + PACKAGED_LISTS[i] + " in " + packaged.string() + " (the server package makes them): "
                    + WITHOUT_LIST[i]);
        for (auto const& [list, names] : packagedFiles)
            for (auto const& name : names)
            {
                if (name.size() > 4 && name.substr(name.size() - 4) == ".dat")
                    continue;                                              // (the naga's parts: merged below)
                Bytes data = ReadFile(packaged / name);
                if (data.empty())
                {
                    problems.push_back(name + " isn't in " + packaged.string());
                    continue;
                }
                std::string inGame = name;
                std::replace(inGame.begin(), inGame.end(), '/', '\\');
                add(inGame, data);
            }
        // The naga's headdresses and outfits (geosets the creation screen picks: tools/naga_parts.py) and
        // emotes (tools/naga_emotes.py) added to the client's own naga models (an HD look's, with one in).
        for (char const* sex : { "Male", "Female" })
        {
            std::string partsName = std::string("Character/Naga_/") + sex + "/Naga" + sex + "Parts.dat";
            std::string emotesName = std::string("Character/Naga_/") + sex + "/Naga" + sex + "Emotes.dat";
            auto listed = [&](char const* list, std::string const& name)
            {
                auto const& files = packagedFiles[list];
                return std::find(files.begin(), files.end(), name) != files.end();
            };
            bool withParts = listed("naga.files", partsName), withEmotes = listed("nagaemotes.files", emotesName);
            if (!withParts && !withEmotes)
                continue;
            std::string model = std::string("Character\\Naga_\\") + sex + "\\Naga_" + sex;
            Bytes m2, skin;
            std::string why;
            if (!game.Read(model + ".m2", m2) || !game.Read(model + "00.skin", skin))
            {
                problems.push_back(model + ".m2 isn't in the game: the naga have no headdresses, outfits or new emotes");
                continue;
            }
            bool changed = false;
            if (withParts)
            {
                Bytes withM2 = m2, withSkin = skin, parts = ReadFile(packaged / partsName);
                if (!MergeParts(withM2, withSkin, parts, why))
                    problems.push_back(model + ".m2: " + why + ": the naga have no headdresses or outfits");
                else
                {
                    m2 = std::move(withM2);
                    skin = std::move(withSkin);
                    changed = true;
                }
            }
            if (withEmotes)
            {
                Bytes merged = m2, emotes = ReadFile(packaged / emotesName);
                size_t added = 0;
                if (!MergeEmotes(merged, emotes, why, &added))
                    problems.push_back(model + ".m2: " + why + ": the naga have no new emotes");
                else
                {
                    m2 = std::move(merged);
                    changed |= added > 0;
                }
            }
            if (changed)
            {
                add(model + ".m2", m2);
                add(model + "00.skin", skin);
            }
        }

        // Tables. The races' CharSections rows name only textures that are there (in the game or this
        // patch): the game's own rows for the naga name a hair and a facial hair texture it hasn't.
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
            if (name == "CharSections")
            {
                uint32_t empty = dbc.String("");
                for (size_t r = 0; r < dbc.records.size(); ++r)
                {
                    uint32_t race = dbc.Get(r, 1);
                    if (race != 19 && race != 20)
                        continue;
                    for (uint32_t field : { 4u, 5u, 6u })
                    {
                        std::string texture = StringOf(dbc, dbc.Get(r, field));
                        if (texture.empty() || written.count(Lower(texture)) || game.Has(texture))
                            continue;
                        problems.push_back(texture + " isn't in the game: left out of its look");
                        dbc.Set(r, field, empty);
                    }
                }
            }
            Skyborne::SortCharacterTable(dbc, name);
            writer.Add("DBFilesClient\\" + name + ".dbc", dbc.Write());
            ++tables;
        }

        // The character creation screen: the races' icons, the screen's own file list with theirs; the
        // in-game interface's, for add-ons with their own tables of the races (Questie's).
        for (bool round : { false, true })
        {
            Bytes sheet;
            if (Icons(game, round, sheet, problems))
                writer.Add(std::string("Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MurlocNaga") + (round ? "Round" : "") + ".blp", sheet);
        }
        Bytes toc;
        if (game.Read("Interface\\GlueXML\\GlueXML.toc", toc))
        {
            writer.Add("Interface\\GlueXML\\GlueXML.toc", WithFiles(toc, { "MurlocNagaCreate.xml", "MurlocNagaCreate.lua" }));
            for (char const* name : { "MurlocNagaCreate.xml", "MurlocNagaCreate.lua" })
                writer.Add(std::string("Interface\\GlueXML\\") + name, ReadFile(moduleData / "Interface" / "GlueXML" / name));
        }
        else
            problems.push_back("GlueXML.toc isn't in the game: the character screen won't show them");
        Bytes frameToc;
        if (game.Read("Interface\\FrameXML\\FrameXML.toc", frameToc))
        {
            writer.Add("Interface\\FrameXML\\FrameXML.toc", WithFiles(frameToc, { "MurlocNagaAddons.lua" }));
            writer.Add("Interface\\FrameXML\\MurlocNagaAddons.lua", ReadFile(moduleData / "Interface" / "FrameXML" / "MurlocNagaAddons.lua"));
        }
        else
            problems.push_back("FrameXML.toc isn't in the game: add-ons such as Questie won't know the races");

        // The intros: their cameras (tools/cameras.py) and their narrations, mixed from the game's sounds.
        for (char const* name : { "FlybyMurloc.m2", "FlybyMurloc00.skin", "FlybyNaga.m2", "FlybyNaga00.skin" })
        {
            Bytes data = ReadFile(moduleData / "Cameras" / name);
            if (data.empty())
                problems.push_back(std::string("the intro's ") + name + " isn't in the module");
            else
                writer.Add(std::string("Cameras\\") + name, data);
        }
        std::map<std::string, std::vector<std::pair<uint32_t, Bytes>>> narrations;
        for (auto const& line : Lines(Text(moduleData / "narration.txt")))
        {
            if (line.size() != 3)
                continue;
            Bytes sound;
            if (game.Read(line[2], sound))
                narrations[line[0]].emplace_back(uint32_t(std::stoul(line[1])), sound);
            else
                problems.push_back(line[2] + " isn't in the game");
        }
        for (auto const& [race, parts] : narrations)
        {
            writer.Add("Sound\\CinematicVoices\\" + race + "Narration.wav", MixNarration(parts));
            ++files;
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
            std::ofstream out(mark, std::ios::trunc);
            out << stamp.Hex() << "\n";
        }
        for (auto const& p : problems)
            log("  " + p);
        auto seconds = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start).count();
        log("The races' patch is in the game: " + std::to_string(tables) + " tables, " + std::to_string(files) + " files ("
            + std::to_string(seconds) + " s)");
        return true;
    }
}
