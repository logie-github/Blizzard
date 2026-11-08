// SPDX-License-Identifier: GPL-3.0-or-later
#include "SkyborneFiles.h"
#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstring>
#include <set>
#include <sstream>
#include <zlib.h>
#ifdef SKYBORNE_BZIP2
#include <bzlib.h>
#endif

namespace Skyborne
{
    namespace
    {
        // MPQ ------------------------------------------------------------------------------------

        std::array<uint32_t, 0x500> const& CryptTable()
        {
            static std::array<uint32_t, 0x500> const table = []
            {
                std::array<uint32_t, 0x500> t{};
                uint32_t seed = 0x00100001;
                for (uint32_t i = 0; i < 0x100; ++i)
                    for (uint32_t j = 0, index = i; j < 5; ++j, index += 0x100)
                    {
                        seed = (seed * 125 + 3) % 0x2AAAAB;
                        uint32_t high = (seed & 0xFFFF) << 16;
                        seed = (seed * 125 + 3) % 0x2AAAAB;
                        t[index] = high | (seed & 0xFFFF);
                    }
                return t;
            }();
            return table;
        }

        uint32_t Hash(std::string const& text, uint32_t type)
        {
            auto const& table = CryptTable();
            uint32_t seed1 = 0x7FED7FED, seed2 = 0xEEEEEEEE;
            for (char c : text)
            {
                uint32_t ch = uint32_t(std::toupper(static_cast<unsigned char>(c == '/' ? '\\' : c)));
                seed1 = table[type * 0x100 + ch] ^ (seed1 + seed2);
                seed2 = ch + seed1 + seed2 + (seed2 << 5) + 3;
            }
            return seed1;
        }

        void Crypt(uint32_t* data, size_t count, uint32_t key, bool encrypt)
        {
            auto const& table = CryptTable();
            uint32_t seed = 0xEEEEEEEE;
            for (size_t i = 0; i < count; ++i)
            {
                seed += table[0x400 + (key & 0xFF)];
                uint32_t in = data[i];
                uint32_t out = in ^ (key + seed);
                key = ((~key << 0x15) + 0x11111111) | (key >> 0x0B);
                seed = (encrypt ? in : out) + seed + (seed << 5) + 3;
                data[i] = out;
            }
        }

        void DecryptBytes(Bytes& data, size_t from, size_t length, uint32_t key)
        {
            size_t words = length / 4;
            std::vector<uint32_t> w(words);
            std::memcpy(w.data(), data.data() + from, words * 4);
            Crypt(w.data(), words, key, false);
            std::memcpy(data.data() + from, w.data(), words * 4);
        }

        uint32_t Get32(uint8_t const* p) { return uint32_t(p[0]) | uint32_t(p[1]) << 8 | uint32_t(p[2]) << 16 | uint32_t(p[3]) << 24; }
        uint16_t Get16(uint8_t const* p) { return uint16_t(p[0] | p[1] << 8); }
        void Put32(uint8_t* p, uint32_t v) { for (int i = 0; i < 4; ++i) p[i] = uint8_t(v >> (8 * i)); }
        void Put16(uint8_t* p, uint16_t v) { p[0] = uint8_t(v); p[1] = uint8_t(v >> 8); }

        std::string Lower(std::string text)
        {
            for (char& c : text)
                c = char(std::tolower(static_cast<unsigned char>(c)));
            return text;
        }

        std::string GamePath(std::string text)
        {
            std::replace(text.begin(), text.end(), '/', '\\');
            return Lower(text);
        }

        bool Inflate(uint8_t const* in, size_t length, Bytes& out, size_t size)
        {
            out.assign(size, 0);
            uLongf got = uLongf(size);
            return uncompress(out.data(), &got, in, uLong(length)) == Z_OK && got == size;
        }

        bool Unpack(uint8_t const* in, size_t length, Bytes& out, size_t size)
        {
            if (length == 0)
                return false;
            uint8_t method = in[0];
            if (method == 0x02)
                return Inflate(in + 1, length - 1, out, size);
#ifdef SKYBORNE_BZIP2
            if (method == 0x10)
            {
                out.assign(size, 0);
                unsigned int got = unsigned(size);
                return BZ2_bzBuffToBuffDecompress(reinterpret_cast<char*>(out.data()), &got,
                    const_cast<char*>(reinterpret_cast<char const*>(in + 1)), unsigned(length - 1), 0, 0) == BZ_OK && got == size;
            }
#endif
            return false;
        }

        class MpqArchive : public Archive
        {
        public:
            explicit MpqArchive(fs::path const& file)
            {
                path = file;
                _in.open(file, std::ios::binary);
                if (!_in)
                    return;
                // The header is at the start, or 512 bytes on at a time (after data before it).
                uint8_t h[44] = {};
                for (uint64_t at = 0; at < (1u << 20); at += 0x200)
                {
                    _in.seekg(std::streamoff(at));
                    if (!_in.read(reinterpret_cast<char*>(h), 32))
                        return;
                    if (std::memcmp(h, "MPQ\x1A", 4) == 0)
                    {
                        _base = at;
                        break;
                    }
                    if (std::memcmp(h, "MPQ\x1B", 4) == 0) // user data first: where the header is
                    {
                        at = Get32(h + 8) - 0x200;
                        continue;
                    }
                }
                if (std::memcmp(h, "MPQ\x1A", 4) != 0)
                    return;
                uint16_t version = Get16(h + 12);
                _sector = 512u << Get16(h + 14);
                uint64_t hashPos = Get32(h + 16), blockPos = Get32(h + 20);
                uint32_t hashCount = Get32(h + 24), blockCount = Get32(h + 28);
                uint64_t hiBlockPos = 0;
                if (version >= 1)
                {
                    _in.seekg(std::streamoff(_base + 32));
                    _in.read(reinterpret_cast<char*>(h + 32), 12);
                    hiBlockPos = uint64_t(Get32(h + 32)) | uint64_t(Get32(h + 36)) << 32;
                    hashPos |= uint64_t(Get16(h + 40)) << 32;
                    blockPos |= uint64_t(Get16(h + 42)) << 32;
                }
                _hashes.resize(size_t(hashCount) * 4);
                _blocks.resize(size_t(blockCount) * 4);
                _in.seekg(std::streamoff(_base + hashPos));
                _in.read(reinterpret_cast<char*>(_hashes.data()), std::streamsize(_hashes.size() * 4));
                _in.seekg(std::streamoff(_base + blockPos));
                _in.read(reinterpret_cast<char*>(_blocks.data()), std::streamsize(_blocks.size() * 4));
                if (!_in)
                {
                    _hashes.clear();
                    return;
                }
                Crypt(_hashes.data(), _hashes.size(), Hash("(hash table)", 3), false);
                Crypt(_blocks.data(), _blocks.size(), Hash("(block table)", 3), false);
                if (hiBlockPos)
                {
                    _hiBlocks.resize(blockCount);
                    _in.seekg(std::streamoff(_base + hiBlockPos));
                    _in.read(reinterpret_cast<char*>(_hiBlocks.data()), std::streamsize(blockCount * 2));
                }
            }

            // The block of the file at [name], or 0xFFFFFFFF.
            uint32_t Block(std::string const& name) const
            {
                if (_hashes.empty())
                    return 0xFFFFFFFF;
                uint32_t count = uint32_t(_hashes.size() / 4);
                uint32_t start = Hash(name, 0) % count, a = Hash(name, 1), b = Hash(name, 2);
                uint32_t block = 0xFFFFFFFF;
                for (uint32_t i = 0; i < count; ++i)
                {
                    uint32_t const* e = &_hashes[size_t((start + i) % count) * 4];
                    if (e[3] == 0xFFFFFFFF)
                        break;
                    if (e[0] == a && e[1] == b && e[3] < _blocks.size() / 4)
                    {
                        block = e[3];
                        if ((e[2] & 0xFFFF) == 0)   // the neutral locale's, if there are several
                            break;
                    }
                }
                return block;
            }

            bool Has(std::string const& name) override
            {
                uint32_t block = Block(name);
                if (block == 0xFFFFFFFF)
                    return false;
                uint32_t flags = _blocks[size_t(block) * 4 + 3];
                return (flags & 0x80000000) && !(flags & 0x02000000);
            }

            bool Read(std::string const& name, Bytes& out) override
            {
                uint32_t block = Block(name);
                if (block == 0xFFFFFFFF)
                    return false;
                uint32_t const* bl = &_blocks[size_t(block) * 4];
                uint64_t offset = bl[0] | (_hiBlocks.empty() ? 0 : uint64_t(_hiBlocks[block]) << 32);
                uint32_t stored = bl[1], size = bl[2], flags = bl[3];
                if (!(flags & 0x80000000) || (flags & 0x02000000) || (flags & 0x100))
                    return false;                     // gone, deleted, or imploded (older archives)
                Bytes raw(stored);
                _in.clear();
                _in.seekg(std::streamoff(_base + offset));
                if (!_in.read(reinterpret_cast<char*>(raw.data()), stored))
                    return false;
                uint32_t key = 0;
                if (flags & 0x10000)
                {
                    std::string base = name.substr(name.find_last_of("\\/") == std::string::npos ? 0 : name.find_last_of("\\/") + 1);
                    key = Hash(base, 3);
                    if (flags & 0x20000)
                        key = (key + uint32_t(offset)) ^ size;
                }
                if (flags & 0x01000000)        // one unit
                {
                    if (flags & 0x10000)
                        DecryptBytes(raw, 0, raw.size(), key);
                    if ((flags & 0x200) && stored < size)
                        return Unpack(raw.data(), raw.size(), out, size);
                    out.assign(raw.begin(), raw.begin() + std::min<size_t>(raw.size(), size));
                    return out.size() == size;
                }
                if (!(flags & 0x200))
                {
                    if (flags & 0x10000)
                        for (size_t s = 0; s * _sector < size; ++s)
                            DecryptBytes(raw, s * _sector, std::min<size_t>(_sector, size - s * _sector), key + uint32_t(s));
                    out.assign(raw.begin(), raw.begin() + std::min<size_t>(raw.size(), size));
                    return out.size() == size;
                }
                size_t sectors = (size + _sector - 1) / _sector;
                size_t tableSize = (sectors + 1) * 4;
                if (raw.size() < tableSize)
                    return false;
                if (flags & 0x10000)
                    DecryptBytes(raw, 0, tableSize, key - 1);
                out.clear();
                out.reserve(size);
                for (size_t s = 0; s < sectors; ++s)
                {
                    uint32_t from = Get32(&raw[s * 4]), to = Get32(&raw[s * 4 + 4]);
                    if (to < from || to > raw.size())
                        return false;
                    size_t want = std::min<size_t>(_sector, size - s * _sector);
                    if (flags & 0x10000)
                        DecryptBytes(raw, from, to - from, key + uint32_t(s));
                    if (to - from < want)
                    {
                        Bytes part;
                        if (!Unpack(&raw[from], to - from, part, want))
                            return false;
                        out.insert(out.end(), part.begin(), part.end());
                    }
                    else
                        out.insert(out.end(), raw.begin() + from, raw.begin() + from + want);
                }
                return out.size() == size;
            }

        private:
            std::ifstream _in;
            uint64_t _base = 0;
            uint32_t _sector = 4096;
            std::vector<uint32_t> _hashes, _blocks;
            std::vector<uint16_t> _hiBlocks;
        };

        // A folder the game reads like an archive (Data/patch-M.MPQ of the realm's modules...).
        class FolderArchive : public Archive
        {
        public:
            explicit FolderArchive(fs::path const& folder)
            {
                path = folder;
                std::error_code error;
                for (auto it = fs::recursive_directory_iterator(folder, fs::directory_options::follow_directory_symlink, error);
                     !error && it != fs::recursive_directory_iterator(); it.increment(error))
                    if (it->is_regular_file(error))
                        _files[GamePath(it->path().lexically_relative(folder).generic_string())] = it->path();
            }

            bool Has(std::string const& name) override
            {
                return _files.count(GamePath(name)) != 0;
            }

            bool Read(std::string const& name, Bytes& out) override
            {
                auto it = _files.find(GamePath(name));
                if (it == _files.end())
                    return false;
                std::ifstream in(it->second, std::ios::binary);
                out.assign(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
                return bool(in) || in.eof();
            }

        private:
            std::map<std::string, fs::path> _files;
        };

        // A folder's entries by their lower-case names (the phone's storage minds case; the game doesn't).
        std::map<std::string, fs::path> Entries(fs::path const& folder)
        {
            std::map<std::string, fs::path> out;
            std::error_code error;
            for (auto it = fs::directory_iterator(folder, error); !error && it != fs::directory_iterator(); it.increment(error))
                out[Lower(it->path().filename().string())] = it->path();
            return out;
        }

        // Colours ---------------------------------------------------------------------------------

        double Clamp(double x, double a = 0.0, double b = 1.0) { return x < a ? a : x > b ? b : x; }

        double HueDistance(double a, double b)
        {
            double d = std::fmod(std::fabs(a - b), 1.0);
            return std::min(d, 1.0 - d);
        }

        struct Hls { double h, l, s; };
        struct Rgb { double r, g, b; };

        Hls ToHls(Rgb c)
        {
            double maxc = std::max({ c.r, c.g, c.b }), minc = std::min({ c.r, c.g, c.b });
            double l = (minc + maxc) / 2.0;
            if (maxc == minc)
                return { 0.0, l, 0.0 };
            double s = l <= 0.5 ? (maxc - minc) / (maxc + minc) : (maxc - minc) / (2.0 - maxc - minc);
            double rc = (maxc - c.r) / (maxc - minc), gc = (maxc - c.g) / (maxc - minc), bc = (maxc - c.b) / (maxc - minc);
            double h = c.r == maxc ? bc - gc : c.g == maxc ? 2.0 + rc - bc : 4.0 + gc - rc;
            h = std::fmod(h / 6.0, 1.0);
            if (h < 0)
                h += 1.0;
            return { h, l, s };
        }

        double HueValue(double m1, double m2, double h)
        {
            h = std::fmod(h, 1.0);
            if (h < 0)
                h += 1.0;
            if (h < 1.0 / 6.0)
                return m1 + (m2 - m1) * h * 6.0;
            if (h < 0.5)
                return m2;
            if (h < 2.0 / 3.0)
                return m1 + (m2 - m1) * (2.0 / 3.0 - h) * 6.0;
            return m1;
        }

        Rgb FromHls(double h, double l, double s)
        {
            if (s == 0.0)
                return { l, l, l };
            double m2 = l <= 0.5 ? l * (1.0 + s) : l + s - l * s;
            double m1 = 2.0 * l - m2;
            return { HueValue(m1, m2, h + 1.0 / 3.0), HueValue(m1, m2, h), HueValue(m1, m2, h - 1.0 / 3.0) };
        }

        Rgb Mix(Rgb a, Rgb b, double t) { return { a.r * (1 - t) + b.r * t, a.g * (1 - t) + b.g * t, a.b * (1 - t) + b.b * t }; }

        double SkinWeight(Hls c)
        {
            return Clamp(1 - (HueDistance(c.h, 0.055) - 0.045) / 0.03) * Clamp((c.s - 0.08) / 0.08)
                * Clamp((0.95 - c.s) / 0.1) * Clamp((c.l - 0.17) / 0.12);
        }

        double EyeWeight(Hls c)
        {
            return Clamp(1 - (HueDistance(c.h, 0.36) - 0.12) / 0.04) * Clamp((c.s - 0.12) / 0.1) * Clamp((c.l - 0.06) / 0.06);
        }

        Rgb Eyes(Rgb in, Rgb out, Recipe const& r)
        {
            if (r.eyeHue < 0)
                return out;
            Hls c = ToHls(in);
            double w = EyeWeight(c);
            if (w <= 0)
                return out;
            return Mix(out, FromHls(r.eyeHue, Clamp(c.l * r.eyeLightness), Clamp(std::max(c.s, r.eyeSaturation))), w);
        }

        Rgb Apply(Rgb in, Recipe const& r)
        {
            Hls c = ToHls(in);
            switch (r.kind)
            {
                case Recipe::SKIN:
                {
                    Rgb out = in;
                    double w = SkinWeight(c);
                    if (w > 0)
                        out = Mix(out, FromHls(r.hue, Clamp(c.l * r.lightness), Clamp(r.saturation * (0.5 + c.s))), w);
                    return Eyes(in, out, r);
                }
                case Recipe::EYES:
                    return Eyes(in, in, r);
                case Recipe::GREY:
                    return Eyes(in, FromHls(c.h, Clamp(c.l * r.lightness), c.s * r.saturation), r);
                case Recipe::HAIR:
                {
                    // The hair is grey with warm streaks and highlights; the jewellery is saturated.
                    double w = std::max({ Clamp((0.3 - c.s) / 0.1),
                        Clamp(1 - (HueDistance(c.h, 0.095) - 0.045) / 0.02) * Clamp((0.62 - c.s) / 0.1),
                        Clamp((c.l - 0.72) / 0.08) * Clamp((0.6 - c.s) / 0.1) });
                    return Mix(in, FromHls(r.hue, Clamp(c.l * r.lightness), Clamp(r.saturation * (0.4 + c.l))), w);
                }
            }
            return in;
        }

        uint8_t Byte(double v) { return uint8_t(std::lround(Clamp(v) * 255.0)); }

        void ApplyBgr(uint8_t* bgr, Recipe const& r)
        {
            Rgb out = Apply({ bgr[2] / 255.0, bgr[1] / 255.0, bgr[0] / 255.0 }, r);
            bgr[0] = Byte(out.b); bgr[1] = Byte(out.g); bgr[2] = Byte(out.r);
        }

        Rgb From565(uint16_t c)
        {
            uint32_t r = (c >> 11) & 31, g = (c >> 5) & 63, b = c & 31;
            return { ((r << 3) | (r >> 2)) / 255.0, ((g << 2) | (g >> 4)) / 255.0, ((b << 3) | (b >> 2)) / 255.0 };
        }

        uint16_t To565(Rgb c)
        {
            return uint16_t((uint32_t(std::lround(Clamp(c.r) * 31)) << 11) | (uint32_t(std::lround(Clamp(c.g) * 63)) << 5)
                | uint32_t(std::lround(Clamp(c.b) * 31)));
        }

        // BLP2 -----------------------------------------------------------------------------------

        constexpr size_t BLP_HEADER = 148, BLP_PALETTE = 1024;

        struct Blp
        {
            uint8_t encoding = 0, alphaDepth = 0, alphaType = 0;
            uint32_t width = 0, height = 0;
            uint32_t offsets[16] = {}, sizes[16] = {};
        };

        bool ReadBlp(Bytes const& data, Blp& b)
        {
            if (data.size() < BLP_HEADER + BLP_PALETTE || std::memcmp(data.data(), "BLP2", 4) != 0 || Get32(&data[4]) != 1)
                return false;
            b.encoding = data[8]; b.alphaDepth = data[9]; b.alphaType = data[10];
            b.width = Get32(&data[12]); b.height = Get32(&data[16]);
            for (int i = 0; i < 16; ++i)
            {
                b.offsets[i] = Get32(&data[20 + i * 4]);
                b.sizes[i] = Get32(&data[84 + i * 4]);
                if (b.sizes[i] && (size_t(b.offsets[i]) + b.sizes[i] > data.size()))
                    return false;
            }
            return b.width && b.height && b.sizes[0] && (b.encoding >= 1 && b.encoding <= 3);
        }

        uint32_t MipWidth(Blp const& b, int mip) { return std::max<uint32_t>(1, b.width >> mip); }
        uint32_t MipHeight(Blp const& b, int mip) { return std::max<uint32_t>(1, b.height >> mip); }

        // A compressed colour block's two end colours changed, the order kept (it says which
        // kind of block it is: four colours, or three and transparent).
        void RecolorBlock(uint8_t* block, Recipe const& r, bool dxt1)
        {
            uint16_t c0 = Get16(block), c1 = Get16(block + 2);
            uint16_t n0 = To565(Apply(From565(c0), r)), n1 = To565(Apply(From565(c1), r));
            uint32_t indices = Get32(block + 4);
            bool four = !dxt1 || c0 > c1;
            if (four && dxt1)
            {
                if (n0 < n1)
                {
                    std::swap(n0, n1);
                    indices ^= 0x55555555;             // 0<->1, 2<->3
                }
                else if (n0 == n1)
                    indices = 0;                       // one colour: all the first
            }
            else if (dxt1)
            {
                if (n0 > n1)
                {
                    std::swap(n0, n1);
                    uint32_t swapped = 0;              // 0<->1; 2 (the middle) and 3 (transparent) stay
                    for (int i = 0; i < 16; ++i)
                    {
                        uint32_t v = (indices >> (2 * i)) & 3;
                        if (v < 2)
                            v ^= 1;
                        swapped |= v << (2 * i);
                    }
                    indices = swapped;
                }
            }
            else if (n0 < n1)                          // DXT3/5 colours are always four
            {
                std::swap(n0, n1);
                indices ^= 0x55555555;
            }
            Put16(block, n0);
            Put16(block + 2, n1);
            Put32(block + 4, indices);
        }

        void DecodeBlock(uint8_t const* block, bool dxt1, uint8_t out[16][4])
        {
            uint16_t c0 = Get16(block), c1 = Get16(block + 2);
            Rgb a = From565(c0), b = From565(c1);
            Rgb colors[4] = { a, b, {}, {} };
            bool three = dxt1 && c0 <= c1;
            if (three)
            {
                colors[2] = Mix(a, b, 0.5);
                colors[3] = { 0, 0, 0 };
            }
            else
            {
                colors[2] = Mix(a, b, 1.0 / 3.0);
                colors[3] = Mix(a, b, 2.0 / 3.0);
            }
            uint32_t indices = Get32(block + 4);
            for (int i = 0; i < 16; ++i)
            {
                uint32_t v = (indices >> (2 * i)) & 3;
                out[i][0] = Byte(colors[v].r); out[i][1] = Byte(colors[v].g); out[i][2] = Byte(colors[v].b);
                out[i][3] = (three && v == 3) ? 0 : 255;
            }
        }

        // The icons --------------------------------------------------------------------------------

        // The skin (face and ears) of the blood elf's portraits, in a 64-pixel icon; what's warm
        // outside it is hair.
        std::vector<std::vector<std::pair<double, double>>> const& SkinShapes(bool female)
        {
            static std::vector<std::vector<std::pair<double, double>>> const male = {
                { {10, 12}, {22, 5}, {36, 5}, {44, 12}, {47, 24}, {46, 34}, {42, 44}, {36, 52}, {27, 57}, {17, 53}, {11, 42}, {8, 28} },
                { {44, 5}, {52, 4}, {57, 8}, {54, 18}, {48, 26}, {45, 16} },
                { {2, 20}, {10, 22}, {10, 30}, {5, 27} },
            };
            static std::vector<std::vector<std::pair<double, double>>> const woman = {
                { {18, 11}, {28, 6}, {42, 7}, {52, 16}, {55, 28}, {53, 40}, {47, 50}, {38, 57}, {27, 57}, {19, 50}, {15, 38}, {14, 24} },
                { {1, 4}, {7, 6}, {8, 13}, {4, 12} },
                { {44, 54}, {62, 46}, {63, 63}, {40, 63} },
            };
            return female ? woman : male;
        }

        bool Inside(std::vector<std::pair<double, double>> const& poly, double x, double y)
        {
            bool in = false;
            for (size_t i = 0, j = poly.size() - 1; i < poly.size(); j = i++)
                if ((poly[i].second > y) != (poly[j].second > y)
                    && x < (poly[j].first - poly[i].first) * (y - poly[i].second) / (poly[j].second - poly[i].second) + poly[i].first)
                    in = !in;
            return in;
        }

        // How much of each pixel of a [cell]-wide icon is skin, softened at the edges.
        std::vector<double> SkinMask(bool female, uint32_t cell)
        {
            double scale = cell / 64.0;
            std::vector<double> mask(size_t(cell) * cell, 0.0);
            for (uint32_t y = 0; y < cell; ++y)
                for (uint32_t x = 0; x < cell; ++x)
                    for (auto const& poly : SkinShapes(female))
                        if (Inside(poly, (x + 0.5) / scale, (y + 0.5) / scale))
                            mask[size_t(y) * cell + x] = 1.0;
            int radius = std::max(1, int(std::lround(scale)));
            for (int pass = 0; pass < 2; ++pass)
            {
                std::vector<double> blurred(mask.size());
                for (uint32_t y = 0; y < cell; ++y)
                    for (uint32_t x = 0; x < cell; ++x)
                    {
                        double sum = 0; int n = 0;
                        for (int dy = -radius; dy <= radius; ++dy)
                            for (int dx = -radius; dx <= radius; ++dx)
                            {
                                int xx = int(x) + dx, yy = int(y) + dy;
                                if (xx < 0 || yy < 0 || xx >= int(cell) || yy >= int(cell))
                                    continue;
                                sum += mask[size_t(yy) * cell + xx];
                                ++n;
                            }
                        blurred[size_t(y) * cell + x] = sum / n;
                    }
                mask.swap(blurred);
            }
            return mask;
        }

        Rgb Portrait(Rgb in, double skin)
        {
            Hls c = ToHls(in);
            Rgb out = in;
            double warm = Clamp(1 - (HueDistance(c.h, 0.07) - 0.08) / 0.03) * Clamp((c.s - 0.08) / 0.08) * Clamp((c.l - 0.06) / 0.08);
            if (warm > 0)
            {
                Rgb blue = FromHls(0.58, Clamp(c.l * 0.95), Clamp(0.5 * (0.5 + c.s)));
                Rgb white = FromHls(0.6, Clamp(0.3 + c.l * 0.8), 0.1);
                out = Mix(out, Mix(white, blue, skin), warm);
            }
            double eye = EyeWeight(c);
            if (eye > 0)
                out = Mix(out, FromHls(0.56, Clamp(c.l * 1.15), Clamp(std::max(c.s, 0.8))), eye);
            return out;
        }
    }

    // Archives -------------------------------------------------------------------------------------

    std::unique_ptr<Archive> OpenArchive(fs::path const& path)
    {
        std::error_code error;
        if (fs::is_directory(path, error))
            return std::make_unique<FolderArchive>(path);
        return std::make_unique<MpqArchive>(path);
    }

    Game::Game(fs::path const& data, std::vector<std::string> const& skip)
    {
        auto top = Entries(data);
        for (auto const& [name, entry] : top)
            if (name.size() == 4 && fs::is_directory(entry) && fs::exists(entry / ("locale-" + entry.filename().string() + ".MPQ")))
            {
                locale = entry.filename().string();
                break;
            }
        if (locale.empty())
            for (auto const& [name, entry] : top)
                if (name.size() == 4 && fs::is_directory(entry))
                {
                    for (auto const& [inner, file] : Entries(entry))
                        if (inner == "locale-" + name + ".mpq")
                            locale = entry.filename().string();
                    if (!locale.empty())
                        break;
                }
        auto local = locale.empty() ? std::map<std::string, fs::path>{} : Entries(data / locale);
        std::string loc = Lower(locale);

        std::vector<fs::path> order;
        auto add = [&](std::map<std::string, fs::path> const& in, std::string const& name)
        {
            std::string key = Lower(name);
            if (std::find(skip.begin(), skip.end(), key) != skip.end())
                return;
            if (auto it = in.find(key); it != in.end())
                order.push_back(it->second);
        };
        for (char const* name : { "common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ" })
            add(top, name);
        if (!loc.empty())
            for (std::string name : { "locale-", "expansion-locale-", "lichking-locale-" })
                add(local, name + loc + ".mpq");
        std::vector<std::string> suffixes = { "", "-2", "-3" };
        for (char c = '4'; c <= '9'; ++c)
            suffixes.push_back(std::string("-") + c);
        for (char c = 'a'; c <= 'z'; ++c)
            suffixes.push_back(std::string("-") + c);
        for (auto const& s : suffixes)
        {
            add(top, "patch" + s + ".mpq");
            if (!loc.empty())
                add(local, "patch-" + loc + s + ".mpq");
        }
        for (auto const& path : order)
            archives.push_back(OpenArchive(path));
    }

    bool Game::Read(std::string const& name, Bytes& out) const
    {
        for (auto it = archives.rbegin(); it != archives.rend(); ++it)
            if ((*it)->Read(name, out))
                return true;
        return false;
    }

    bool Game::Has(std::string const& name) const
    {
        for (auto const& a : archives)
            if (a->Has(name))
                return true;
        return false;
    }

    std::string Game::Describe() const
    {
        std::ostringstream out;
        out << locale;
        for (auto const& a : archives)
        {
            std::error_code error;
            out << '|' << a->path.filename().string();
            if (fs::is_directory(a->path, error))
            {
                uint64_t count = 0, total = 0;
                for (auto it = fs::recursive_directory_iterator(a->path, fs::directory_options::follow_directory_symlink, error);
                     !error && it != fs::recursive_directory_iterator(); it.increment(error))
                    if (it->is_regular_file(error))
                    {
                        ++count;
                        total += it->file_size(error);
                    }
                out << ':' << count << ':' << total;
            }
            else
                out << ':' << fs::file_size(a->path, error) << ':'
                    << fs::last_write_time(a->path, error).time_since_epoch().count();
        }
        return out.str();
    }

    // Writing an archive ---------------------------------------------------------------------------

    MpqWriter::MpqWriter(fs::path const& path) : _out(path, std::ios::binary | std::ios::trunc)
    {
        static char const zeros[32] = {};
        _out.write(zeros, 32);
        _ok = bool(_out);
    }

    bool MpqWriter::Add(std::string const& name, Bytes const& data)
    {
        constexpr uint32_t SECTOR = 4096;
        uint32_t sectors = std::max<uint32_t>(1, uint32_t((data.size() + SECTOR - 1) / SECTOR));
        Bytes stored(size_t(sectors + 1) * 4, 0);
        std::vector<uint32_t> offsets{ uint32_t(stored.size()) };
        Bytes packed(compressBound(SECTOR));
        for (uint32_t i = 0; i < sectors; ++i)
        {
            size_t from = size_t(i) * SECTOR, length = std::min<size_t>(SECTOR, data.size() - from);
            uLongf size = uLongf(packed.size());
            if (length && compress2(packed.data(), &size, data.data() + from, uLong(length), 6) == Z_OK && size + 1 < length)
            {
                stored.push_back(0x02);
                stored.insert(stored.end(), packed.begin(), packed.begin() + size);
            }
            else
                stored.insert(stored.end(), data.begin() + from, data.begin() + from + length);
            offsets.push_back(uint32_t(stored.size()));
        }
        for (size_t i = 0; i < offsets.size(); ++i)
            Put32(&stored[i * 4], offsets[i]);
        _blocks.push_back({ name, { uint32_t(_pos), uint32_t(stored.size()), uint32_t(data.size()), 0x80000000u | 0x200u } });
        _out.write(reinterpret_cast<char const*>(stored.data()), std::streamsize(stored.size()));
        _pos += stored.size();
        _ok = _ok && bool(_out) && _pos < 0xF0000000ull;
        return _ok;
    }

    bool MpqWriter::AddSame(std::string const& name, std::string const& existing)
    {
        for (uint32_t i = 0; i < _blocks.size(); ++i)
            if (_blocks[i].first == existing)
            {
                _same.emplace_back(name, i);
                return true;
            }
        return false;
    }

    bool MpqWriter::Finish()
    {
        uint32_t hashSize = 16;
        while (hashSize < (_blocks.size() + _same.size()) * 2)
            hashSize *= 2;
        std::vector<uint32_t> hashes(size_t(hashSize) * 4, 0xFFFFFFFF), blocks;
        auto put = [&](std::string const& name, uint32_t block)
        {
            uint32_t index = Hash(name, 0) & (hashSize - 1);
            while (hashes[size_t(index) * 4 + 3] != 0xFFFFFFFF)
                index = (index + 1) & (hashSize - 1);
            hashes[size_t(index) * 4 + 0] = Hash(name, 1);
            hashes[size_t(index) * 4 + 1] = Hash(name, 2);
            hashes[size_t(index) * 4 + 2] = 0;
            hashes[size_t(index) * 4 + 3] = block;
        };
        for (uint32_t i = 0; i < _blocks.size(); ++i)
        {
            put(_blocks[i].first, i);
            blocks.insert(blocks.end(), _blocks[i].second.begin(), _blocks[i].second.end());
        }
        for (auto const& [name, block] : _same)
            put(name, block);
        Crypt(hashes.data(), hashes.size(), Hash("(hash table)", 3), true);
        Crypt(blocks.data(), blocks.size(), Hash("(block table)", 3), true);
        uint32_t hashPos = uint32_t(_pos);
        _out.write(reinterpret_cast<char const*>(hashes.data()), std::streamsize(hashes.size() * 4));
        uint32_t blockPos = uint32_t(_pos + hashes.size() * 4);
        _out.write(reinterpret_cast<char const*>(blocks.data()), std::streamsize(blocks.size() * 4));
        uint32_t total = uint32_t(blockPos + blocks.size() * 4);
        uint8_t h[32] = {};
        std::memcpy(h, "MPQ\x1A", 4);
        Put32(h + 4, 32);
        Put32(h + 8, total);
        Put16(h + 12, 0);
        Put16(h + 14, 3);                               // sectors of 4096 bytes
        Put32(h + 16, hashPos);
        Put32(h + 20, blockPos);
        Put32(h + 24, hashSize);
        Put32(h + 28, uint32_t(_blocks.size()));
        _out.seekp(0);
        _out.write(reinterpret_cast<char const*>(h), 32);
        _out.close();
        return _ok && !_out.fail();
    }

    // Tables -----------------------------------------------------------------------------------------

    bool Dbc::Parse(Bytes const& data)
    {
        if (data.size() < 20 || std::memcmp(data.data(), "WDBC", 4) != 0)
            return false;
        uint32_t count = Get32(&data[4]);
        fields = Get32(&data[8]);
        size = Get32(&data[12]);
        uint32_t stringSize = Get32(&data[16]);
        if (data.size() < 20 + size_t(count) * size + stringSize)
            return false;
        records.clear();
        for (uint32_t i = 0; i < count; ++i)
            records.emplace_back(data.begin() + 20 + size_t(i) * size, data.begin() + 20 + size_t(i + 1) * size);
        size_t at = 20 + size_t(count) * size;
        strings.assign(data.begin() + at, data.begin() + at + stringSize);
        if (strings.empty())
            strings.push_back(0);
        stringAt.clear();
        for (size_t i = 0; i < strings.size();)
        {
            size_t end = i;
            while (end < strings.size() && strings[end])
                ++end;
            stringAt.emplace(std::string(strings.begin() + i, strings.begin() + end), uint32_t(i));
            i = end + 1;
        }
        return true;
    }

    Bytes Dbc::Write() const
    {
        Bytes out(20);
        std::memcpy(out.data(), "WDBC", 4);
        Put32(&out[4], uint32_t(records.size()));
        Put32(&out[8], fields);
        Put32(&out[12], size);
        Put32(&out[16], uint32_t(strings.size()));
        out.reserve(20 + records.size() * size + strings.size());
        for (auto const& r : records)
            out.insert(out.end(), r.begin(), r.end());
        out.insert(out.end(), strings.begin(), strings.end());
        return out;
    }

    uint32_t Dbc::String(std::string const& text)
    {
        if (text.empty())
            return 0;
        if (auto it = stringAt.find(text); it != stringAt.end())
            return it->second;
        uint32_t at = uint32_t(strings.size());
        strings.insert(strings.end(), text.begin(), text.end());
        strings.push_back(0);
        stringAt.emplace(text, at);
        return at;
    }

    void SortCharacterTable(Dbc& dbc, std::string const& name)
    {
        std::string lower = name;
        for (char& ch : lower)
            ch = char(std::tolower(static_cast<unsigned char>(ch)));
        std::vector<uint32_t> keys;
        if (lower == "charsections")
            keys = { 1, 2, 3, 8, 9 };
        else if (lower == "charhairgeosets")
            keys = { 1, 2, 3 };
        else if (lower == "characterfacialhairstyles")
            keys = { 0, 1, 2 };
        else
            return;
        for (uint32_t key : keys)
            if (key >= dbc.fields || dbc.size < (key + 1) * 4)
                return;
        std::stable_sort(dbc.records.begin(), dbc.records.end(), [&](Bytes const& a, Bytes const& b)
        {
            for (uint32_t key : keys)
            {
                uint32_t x = Get32(&a[key * 4]), y = Get32(&b[key * 4]);
                if (x != y)
                    return x < y;
            }
            return false;
        });
    }

    uint32_t Dbc::Get(size_t row, uint32_t field) const { return Get32(&records[row][field * 4]); }
    void Dbc::Set(size_t row, uint32_t field, uint32_t value) { Put32(&records[row][field * 4], value); }

    namespace
    {
        std::vector<std::string> SplitTabs(std::string const& line)
        {
            std::vector<std::string> out(1);
            for (size_t i = 0; i < line.size(); ++i)
            {
                char c = line[i];
                if (c == '\t')
                    out.emplace_back();
                else if (c == '\\' && i + 1 < line.size())
                {
                    char n = line[++i];
                    out.back() += n == 't' ? '\t' : n == 'n' ? '\n' : n;
                }
                else
                    out.back() += c;
            }
            return out;
        }

        bool Hex(std::string const& text, Bytes& out)
        {
            if (text.size() % 2)
                return false;
            out.clear();
            for (size_t i = 0; i < text.size(); i += 2)
                out.push_back(uint8_t(std::stoul(text.substr(i, 2), nullptr, 16)));
            return true;
        }
    }

    std::string ApplyChanges(Dbc& dbc, std::string const& changes)
    {
        std::map<uint32_t, size_t> byId;
        bool hasIds = dbc.size >= 4;
        if (hasIds)
            for (size_t i = 0; i < dbc.records.size(); ++i)
                byId.emplace(dbc.Get(i, 0), i);
        std::set<Bytes> whole(dbc.records.begin(), dbc.records.end());
        std::string types;
        std::istringstream in(changes);
        std::string line;
        size_t number = 0;
        auto place = [&](Bytes const& record) -> void
        {
            if (hasIds)
            {
                uint32_t id = Get32(record.data());
                if (auto it = byId.find(id); it != byId.end())
                {
                    dbc.records[it->second] = record;
                    return;
                }
                byId.emplace(id, dbc.records.size());
            }
            dbc.records.push_back(record);
        };
        while (std::getline(in, line))
        {
            ++number;
            if (!line.empty() && line.back() == '\r')
                line.pop_back();
            if (line.empty() || line[0] == '#')
                continue;
            auto f = SplitTabs(line);
            std::string const& op = f[0];
            std::string where = " (line " + std::to_string(number) + ")";
            try
            {
                if (op == "types")
                {
                    types = f.size() > 1 ? f[1] : "";
                    if (types.size() != dbc.fields || dbc.size != dbc.fields * 4)
                        return "the table isn't the one these changes are for: " + std::to_string(dbc.fields) + " fields, "
                            + std::to_string(types.size()) + " expected";
                }
                else if (op == "put")
                {
                    if (types.empty() || f.size() != types.size() + 1)
                        return "a row of the wrong size" + where;
                    Bytes record(dbc.size);
                    for (size_t i = 0; i < types.size(); ++i)
                    {
                        std::string const& v = f[i + 1];
                        uint32_t value = 0;
                        if (types[i] == 's')
                            value = dbc.String(v);
                        else if (types[i] == 'f')
                        {
                            float x = std::stof(v);
                            std::memcpy(&value, &x, 4);
                        }
                        else
                            value = uint32_t(std::stoll(v));
                        Put32(&record[i * 4], value);
                    }
                    place(record);
                }
                else if (op == "putraw" || op == "appendraw")
                {
                    Bytes record;
                    if (f.size() != 2 || !Hex(f[1], record) || record.size() != dbc.size)
                        return "a record of the wrong size" + where;
                    if (op == "putraw")
                        place(record);
                    else if (whole.insert(record).second)
                        dbc.records.push_back(record);
                }
                else if (op == "copyrow")
                {
                    // the client's own row [from] as a new row [to], where the table has none by that id
                    if (f.size() != 3 || !hasIds)
                        return "a row copy the table can't take" + where;
                    uint32_t from = uint32_t(std::stoll(f[1])), to = uint32_t(std::stoll(f[2]));
                    auto it = byId.find(from);
                    if (it != byId.end() && !byId.count(to))
                    {
                        Bytes record = dbc.records[it->second];
                        Put32(record.data(), to);
                        place(record);
                    }
                }
                else if (op == "remapfield")
                {
                    // every row whose [field] is [from] given [to] there, whatever its id: the client's
                    // own rows, laid out as its tables have them (an HD look's too)
                    if (f.size() != 4)
                        return "a field remap of the wrong size" + where;
                    uint32_t field = uint32_t(std::stoul(f[1])), from = uint32_t(std::stoll(f[2])), to = uint32_t(std::stoll(f[3]));
                    if (field >= dbc.size / 4)
                        return "no such field" + where;
                    for (size_t row = 0; row < dbc.records.size(); ++row)
                        if (dbc.Get(row, field) == from)
                            dbc.Set(row, field, to);
                    whole = std::set<Bytes>(dbc.records.begin(), dbc.records.end());
                    if (field == 0 && hasIds)
                    {
                        byId.clear();
                        for (size_t row = 0; row < dbc.records.size(); ++row)
                            byId.emplace(dbc.Get(row, 0), row);
                    }
                }
                else if (op == "or" || op == "set")
                {
                    if (f.size() != 4 || !hasIds)
                        return "a field change the table can't take" + where;
                    uint32_t id = uint32_t(std::stoll(f[1])), field = uint32_t(std::stoul(f[2])), value = uint32_t(std::stoll(f[3]));
                    if (field >= dbc.size / 4)
                        return "no such field" + where;
                    auto it = byId.find(id);
                    if (it == byId.end())
                        continue;                       // the row isn't in this client's table
                    dbc.Set(it->second, field, op == "or" ? dbc.Get(it->second, field) | value : value);
                }
                else
                    return "unknown change \"" + op + "\"" + where;
            }
            catch (std::exception const&)
            {
                return "a value that isn't one" + where;
            }
        }
        return "";
    }

    // Textures ---------------------------------------------------------------------------------------

    bool ParseRecipe(std::string const& op, std::string const& params, Recipe& r)
    {
        std::vector<double> v;
        std::istringstream in(params);
        std::string part;
        while (std::getline(in, part, ','))
        {
            try { v.push_back(std::stod(part)); }
            catch (std::exception const&) { return false; }
        }
        if (op == "skin" && v.size() == 6)
        {
            r = { Recipe::SKIN, v[0], v[1], v[2], v[3], v[4], v[5] };
            return true;
        }
        if (op == "grey" && v.size() == 5)
        {
            r = { Recipe::GREY, 0, v[0], v[1], v[2], v[3], v[4] };
            return true;
        }
        if (op == "eyes" && v.size() == 3)
        {
            r = { Recipe::EYES, 0, 0, 1, v[0], v[1], v[2] };
            return true;
        }
        if (op == "hair" && v.size() == 3)
        {
            r = { Recipe::HAIR, v[0], v[1], v[2] };
            return true;
        }
        return false;
    }

    bool Recolor(Bytes& data, Recipe const& recipe)
    {
        Blp b;
        if (!ReadBlp(data, b))
            return false;
        if (b.encoding == 1)                           // a palette: its colours
        {
            for (int i = 0; i < 256; ++i)
                ApplyBgr(&data[BLP_HEADER + i * 4], recipe);
            return true;
        }
        for (int mip = 0; mip < 16 && b.sizes[mip]; ++mip)
        {
            uint8_t* p = &data[b.offsets[mip]];
            uint32_t w = MipWidth(b, mip), h = MipHeight(b, mip);
            if (b.encoding == 3)
            {
                if (b.sizes[mip] < size_t(w) * h * 4)
                    return false;
                for (size_t i = 0; i < size_t(w) * h; ++i)
                    ApplyBgr(p + i * 4, recipe);
                continue;
            }
            bool dxt1 = b.alphaType == 0;
            size_t blockSize = dxt1 ? 8 : 16;
            size_t blocks = size_t((w + 3) / 4) * ((h + 3) / 4);
            if (b.sizes[mip] < blocks * blockSize)
                return false;
            for (size_t i = 0; i < blocks; ++i)
                RecolorBlock(p + i * blockSize + (dxt1 ? 0 : 8), recipe, dxt1);
        }
        return true;
    }

    bool Decode(Bytes const& data, Image& image)
    {
        Blp b;
        if (!ReadBlp(data, b))
            return false;
        uint32_t w = b.width, h = b.height;
        image.width = w;
        image.height = h;
        image.rgba.assign(size_t(w) * h * 4, 255);
        uint8_t const* p = &data[b.offsets[0]];
        size_t size = b.sizes[0];
        if (b.encoding == 1)
        {
            if (size < size_t(w) * h)
                return false;
            for (size_t i = 0; i < size_t(w) * h; ++i)
            {
                uint8_t const* c = &data[BLP_HEADER + p[i] * 4];
                image.rgba[i * 4] = c[2]; image.rgba[i * 4 + 1] = c[1]; image.rgba[i * 4 + 2] = c[0];
                uint8_t a = 255;
                uint8_t const* alpha = p + size_t(w) * h;
                if (b.alphaDepth == 8 && size >= size_t(w) * h * 2)
                    a = alpha[i];
                else if (b.alphaDepth == 4 && size >= size_t(w) * h + (size_t(w) * h + 1) / 2)
                    a = uint8_t(((alpha[i / 2] >> ((i % 2) * 4)) & 15) * 17);
                else if (b.alphaDepth == 1 && size >= size_t(w) * h + (size_t(w) * h + 7) / 8)
                    a = (alpha[i / 8] >> (i % 8)) & 1 ? 255 : 0;
                image.rgba[i * 4 + 3] = a;
            }
            return true;
        }
        if (b.encoding == 3)
        {
            if (size < size_t(w) * h * 4)
                return false;
            for (size_t i = 0; i < size_t(w) * h; ++i)
            {
                image.rgba[i * 4] = p[i * 4 + 2]; image.rgba[i * 4 + 1] = p[i * 4 + 1];
                image.rgba[i * 4 + 2] = p[i * 4]; image.rgba[i * 4 + 3] = p[i * 4 + 3];
            }
            return true;
        }
        bool dxt1 = b.alphaType == 0;
        size_t blockSize = dxt1 ? 8 : 16;
        uint32_t bw = (w + 3) / 4, bh = (h + 3) / 4;
        if (size < size_t(bw) * bh * blockSize)
            return false;
        for (uint32_t by = 0; by < bh; ++by)
            for (uint32_t bx = 0; bx < bw; ++bx)
            {
                uint8_t const* block = p + (size_t(by) * bw + bx) * blockSize;
                uint8_t px[16][4];
                DecodeBlock(block + (dxt1 ? 0 : 8), dxt1, px);
                uint8_t alpha[16];
                for (int i = 0; i < 16; ++i)
                    alpha[i] = dxt1 ? px[i][3] : 255;
                if (b.alphaType == 1)                  // DXT3: four bits each
                    for (int i = 0; i < 16; ++i)
                        alpha[i] = uint8_t(((block[i / 2] >> ((i % 2) * 4)) & 15) * 17);
                else if (b.alphaType == 7)             // DXT5: two levels and the steps between
                {
                    uint8_t a0 = block[0], a1 = block[1];
                    uint8_t levels[8] = { a0, a1 };
                    for (int i = 2; i < 8; ++i)
                        levels[i] = a0 > a1 ? uint8_t(((8 - i) * a0 + (i - 1) * a1) / 7)
                                            : i < 6 ? uint8_t(((6 - i) * a0 + (i - 1) * a1) / 5) : (i == 6 ? 0 : 255);
                    uint64_t bits = 0;
                    for (int i = 0; i < 6; ++i)
                        bits |= uint64_t(block[2 + i]) << (8 * i);
                    for (int i = 0; i < 16; ++i)
                        alpha[i] = levels[(bits >> (3 * i)) & 7];
                }
                for (int i = 0; i < 16; ++i)
                {
                    uint32_t x = bx * 4 + i % 4, y = by * 4 + i / 4;
                    if (x >= w || y >= h)
                        continue;
                    uint8_t* out = &image.rgba[(size_t(y) * w + x) * 4];
                    out[0] = px[i][0]; out[1] = px[i][1]; out[2] = px[i][2]; out[3] = alpha[i];
                }
            }
        return true;
    }

    namespace
    {
        // A 4x4 block's colours as DXT5: its alpha's two ends and a step of eight for each pixel,
        // its colours' two ends (the box around them) and a step of four.
        void EncodeBlock(uint8_t const px[16][4], uint8_t* out)
        {
            uint8_t amax = 0, amin = 255;
            for (int i = 0; i < 16; ++i)
            {
                amax = std::max(amax, px[i][3]);
                amin = std::min(amin, px[i][3]);
            }
            out[0] = amax;
            out[1] = amin;
            uint64_t abits = 0;
            for (int i = 0; i < 16; ++i)
            {
                uint64_t index = 0;
                if (amax != amin)
                {
                    int step = int(std::lround(7.0 * (amax - px[i][3]) / (amax - amin)));  // 0: amax .. 7: amin
                    index = step == 0 ? 0 : step == 7 ? 1 : uint64_t(step + 1);
                }
                abits |= index << (3 * i);
            }
            for (int i = 0; i < 6; ++i)
                out[2 + i] = uint8_t(abits >> (8 * i));

            int lo[3] = { 255, 255, 255 }, hi[3] = { 0, 0, 0 };
            for (int i = 0; i < 16; ++i)
                for (int c = 0; c < 3; ++c)
                {
                    lo[c] = std::min<int>(lo[c], px[i][c]);
                    hi[c] = std::max<int>(hi[c], px[i][c]);
                }
            uint16_t c0 = To565({ hi[0] / 255.0, hi[1] / 255.0, hi[2] / 255.0 });
            uint16_t c1 = To565({ lo[0] / 255.0, lo[1] / 255.0, lo[2] / 255.0 });
            if (c0 < c1)
                std::swap(c0, c1);
            Rgb ends[4] = { From565(c0), From565(c1), {}, {} };
            ends[2] = Mix(ends[0], ends[1], 1.0 / 3.0);
            ends[3] = Mix(ends[0], ends[1], 2.0 / 3.0);
            uint32_t indices = 0;
            for (int i = 0; i < 16; ++i)
            {
                double best = 1e9;
                uint32_t pick = 0;
                for (uint32_t k = 0; k < 4; ++k)
                {
                    double dr = ends[k].r * 255 - px[i][0], dg = ends[k].g * 255 - px[i][1], db = ends[k].b * 255 - px[i][2];
                    double d = dr * dr + dg * dg + db * db;
                    if (d < best)
                    {
                        best = d;
                        pick = k;
                    }
                }
                indices |= pick << (2 * i);
            }
            Put16(out + 8, c0);
            Put16(out + 10, c1);
            Put32(out + 12, indices);
        }
    }

    Bytes EncodeDxt5(Image const& image)
    {
        Bytes out(BLP_HEADER + BLP_PALETTE, 0);
        std::memcpy(out.data(), "BLP2", 4);
        Put32(&out[4], 1);
        out[8] = 2;                                    // compressed
        out[9] = 8;                                    // 8 bits of alpha
        out[10] = 7;                                   // DXT5
        out[11] = 1;                                   // with smaller copies
        Put32(&out[12], image.width);
        Put32(&out[16], image.height);
        std::vector<uint8_t> level = image.rgba;
        uint32_t w = image.width, h = image.height;
        for (int mip = 0; mip < 16; ++mip)
        {
            size_t at = out.size();
            for (uint32_t by = 0; by < (h + 3) / 4; ++by)
                for (uint32_t bx = 0; bx < (w + 3) / 4; ++bx)
                {
                    uint8_t px[16][4];
                    for (int i = 0; i < 16; ++i)
                    {
                        uint32_t x = std::min(bx * 4 + i % 4, w - 1), y = std::min(by * 4 + i / 4, h - 1);
                        std::memcpy(px[i], &level[(size_t(y) * w + x) * 4], 4);
                    }
                    uint8_t block[16];
                    EncodeBlock(px, block);
                    out.insert(out.end(), block, block + 16);
                }
            Put32(&out[20 + mip * 4], uint32_t(at));
            Put32(&out[84 + mip * 4], uint32_t(out.size() - at));
            if (w == 1 && h == 1)
                break;
            uint32_t nw = std::max<uint32_t>(1, w / 2), nh = std::max<uint32_t>(1, h / 2);
            std::vector<uint8_t> next(size_t(nw) * nh * 4);
            for (uint32_t y = 0; y < nh; ++y)
                for (uint32_t x = 0; x < nw; ++x)
                    for (int c = 0; c < 4; ++c)
                    {
                        uint32_t sum = 0;
                        for (uint32_t dy = 0; dy < 2; ++dy)
                            for (uint32_t dx = 0; dx < 2; ++dx)
                                sum += level[(size_t(std::min(y * 2 + dy, h - 1)) * w + std::min(x * 2 + dx, w - 1)) * 4 + c];
                        next[(size_t(y) * nw + x) * 4 + c] = uint8_t((sum + 2) / 4);
                    }
            level.swap(next);
            w = nw;
            h = nh;
        }
        return out;
    }

    bool SkyborneIcons(Bytes& blp)
    {
        Image image;
        if (!Decode(blp, image) || image.width < 64 || image.height < 32 || image.width != image.height * 2)
            return false;
        uint32_t cell = image.width / 8;               // 8 icons a row, 4 rows
        for (bool female : { false, true })
        {
            std::vector<double> mask = SkinMask(female, cell);
            uint32_t sourceRow = female ? 3 : 1;       // the blood elf's: Horde men, Horde women
            std::vector<uint8_t> icon(size_t(cell) * cell * 4);
            for (uint32_t y = 0; y < cell; ++y)
                for (uint32_t x = 0; x < cell; ++x)
                {
                    uint8_t const* in = &image.rgba[(size_t(sourceRow * cell + y) * image.width + 4 * cell + x) * 4];
                    Rgb c = Portrait({ in[0] / 255.0, in[1] / 255.0, in[2] / 255.0 }, mask[size_t(y) * cell + x]);
                    uint8_t* out = &icon[(size_t(y) * cell + x) * 4];
                    out[0] = Byte(c.r); out[1] = Byte(c.g); out[2] = Byte(c.b); out[3] = in[3];
                }
            for (uint32_t row : { female ? 2u : 0u, female ? 3u : 1u })   // the Alliance's and the Horde's
                for (uint32_t y = 0; y < cell; ++y)
                    std::memcpy(&image.rgba[(size_t(row * cell + y) * image.width + 6 * cell) * 4], &icon[size_t(y) * cell * 4], size_t(cell) * 4);
        }
        blp = EncodeDxt5(image);
        return true;
    }
}
