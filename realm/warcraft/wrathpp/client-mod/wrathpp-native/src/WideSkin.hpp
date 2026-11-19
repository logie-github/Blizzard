// Wrath++'s wide skins: the part of it that touches nothing of the game (plain C++, no Windows, no SDK), so it is
// compiled and run on any machine (client-mod/tests/wide_skin_test.cpp). Native.cpp holds the hooks that use it.
//
// WHAT IT IS FOR. A converted character model has 110,000 to 126,000 triangle indices with every hair style whole. A 3.3.5
// skin section says where its triangles begin in 16 bits, so the stock client (the phone's Wow.exe 12340) can only be given
// 65,535 of them: the looks' own skin (<Model>00.skin) is cut to that. Beside it the looks carry the whole one
// (<Model>00w.skin): the same format, a section past 65,535 with the high half of its start in the "level" half-word
// (the top of the 32-bit id field, M2SkinSection +2).
//
// HOW THE STOCK CLIENT IS MADE TO DRAW IT (the reconstruction's lines: WarcraftXL-Labs/client, Engine/Source/Model2):
//   * Every place the stock code reads a FILE section's start or count: CM2Shared::SetIndices (M2Shared.cpp 369-384),
//     CM2Model::SetIndices (M2Model.cpp 2700-2730, optimized geometry only), CM2Model::OptimizeVisibleGeometry (4186-4315,
//     counts), CM2Scene::HitTestGeometry (M2Scene.cpp 636-661), CM2Shared::InitializeSkinProfile (M2Shared.cpp 1224-1226:
//     the copy the shared draws are made from). The 32-bit id is compared in CM2Model::SetGeometryVisible (4089).
//   * When the skin has been parsed and before any of that runs (the runtime's SkinProfileParsed), the sections are
//     rewritten in memory (Normalize): the level cleared (the id is the geoset alone, whatever width the stock compare
//     has), and every section that begins past 65,535 ("far") given start 0 and count 0. In that form the stock client
//     draws the model right without its far sections and reads nothing out of place: an EMPTY section, never wrong
//     triangles. That is the state every failure falls back to.
//   * The shared index pool (CM2Shared::SetIndices) is where the far sections are then put back: the stock function
//     lays the pool out section after section by the COPIES' counts (M2Shared.cpp 370, 375-384) and writes each copy's
//     start as 16 bits. With the copies' counts set true, the stock pass leaves room for every section; Native.cpp then
//     writes the far sections' triangles into their places (WriteFar) and, at the device's draw, gives the 16-bit start
//     its high half back (DrawStart). Before any of that the stock pass's own output is read back and compared with
//     what this code would have written for the near sections (Calibrate): the pool's layout, the lock and the way the
//     indices are rebased are proven against the game itself, or the skin stays in the empty-section state.
//   * An optimized geometry (CM2Model::OptimizeVisibleGeometry) is made from the FILE sections, which stay empty for
//     the far ones, so it must never be made for a wide skin: the stock function gives up when no two visible batches
//     match (4204: visibleCount <= batchCount; BatchesMatch, 189-191), and the converter gives every batch of a wide
//     skin a material index of its own. Read() refuses a wide skin in which two batches could match.
#ifndef WRATHPP_WIDE_SKIN_HPP
#define WRATHPP_WIDE_SKIN_HPP

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

namespace wrathpp::wide
{
#pragma pack(push, 1)
    /// M2SkinSection as the stock client holds it (M2Data.h 301-315; 0x30 bytes): the id's top half is the level.
    struct Section
    {
        uint16_t id;                 // 0x00
        uint16_t level;              // 0x02
        uint16_t vertexStart;        // 0x04
        uint16_t vertexCount;        // 0x06
        uint16_t indexStart;         // 0x08
        uint16_t indexCount;         // 0x0A
        uint16_t boneCount;          // 0x0C
        uint16_t boneComboIndex;     // 0x0E
        uint16_t boneInfluences;     // 0x10
        uint16_t centerBone;         // 0x12
        float    centre[3];          // 0x14
        float    sortCentre[3];      // 0x20
        float    sortRadius;         // 0x2C
    };

    /// M2Batch (M2Data.h 284-299; 0x18 bytes).
    struct Batch
    {
        uint8_t  flags;
        int8_t   priorityPlane;
        uint16_t shader;
        uint16_t sectionIndex;
        uint16_t geosetIndex;
        uint16_t colorIndex;
        uint16_t materialIndex;
        uint16_t materialLayer;
        uint16_t textureCount;
        uint16_t textureCombo;
        uint16_t textureCoordCombo;
        uint16_t textureWeightCombo;
        uint16_t textureTransformCombo;
    };
#pragma pack(pop)
    static_assert(sizeof(Section) == 0x30, "M2SkinSection is 0x30 bytes");
    static_assert(offsetof(Section, indexStart) == 0x8 && offsetof(Section, indexCount) == 0xA, "M2SkinSection's index window");
    static_assert(sizeof(Batch) == 0x18, "M2Batch is 0x18 bytes");

    constexpr uint32_t kNear = 0x10000;          // a start below this is one the stock client reads
    constexpr uint32_t kMostIndices = 3 * 0x10000 - 1;   // below this no two sections' pool starts share their low 16 bits (see Read)

    /// What a skin is, read once when it has been parsed.
    struct Plan
    {
        bool wide = false;                  ///< it has sections the stock client can't read (or carries levels)
        bool valid = false;                 ///< ...and every check passed: it may be drawn whole
        std::string why;                    ///< what failed
        std::vector<uint32_t> start;        ///< each section's first index in the file's array
        std::vector<uint16_t> count;        ///< each section's index count
        std::vector<uint16_t> vertexStart;
        std::vector<uint8_t> isFar;           ///< 1: begins past 65,535 in the file
        std::vector<uint32_t> pool;         ///< each section's first index in the shared pool with every section whole
        std::vector<uint32_t> poolNear;     ///< ...and with the far sections empty (the stock client alone)
        std::vector<std::pair<uint16_t, uint32_t>> high;   ///< (low 16 bits, whole start) of the pool starts past 65,535, sorted
        uint32_t farSections = 0, farIndices = 0, total = 0;
    };

    /// The client's M2SkinSectionIndexStart (M2Data.h 396-405): the level is the start's high half when that window lies
    /// inside the skin's index array.
    inline uint32_t FileStart(uint32_t indexCount, const Section& s)
    {
        const uint32_t wide = (static_cast<uint32_t>(s.level) << 16) | s.indexStart;
        if (wide != s.indexStart && wide <= indexCount && s.indexCount <= indexCount - wide) return wide;
        return s.indexStart;
    }

    /**
     * Reads a parsed skin. `indices` are the skin's own (indexCount of them), `vertexCount` the skin's vertex lookups.
     * Nothing is changed. A skin with no level and no more than 65,535 indices comes back `wide == false`.
     */
    inline Plan Read(const Section* sections, uint32_t sectionCount, const Batch* batches, uint32_t batchCount,
                     const uint16_t* indices, uint32_t indexCount, uint32_t vertexCount)
    {
        Plan p;
        if (!sections || !sectionCount) return p;
        for (uint32_t i = 0; i < sectionCount; i++)
            if (sections[i].level) p.wide = true;
        if (indexCount > 0xFFFF) p.wide = true;
        if (!p.wide) return p;
        const auto fail = [&p](const char* what, uint32_t at) {
            p.why = std::string(what) + " (section " + std::to_string(at) + ")";
            return p;
        };
        if (!indices || !batches) return fail("no indices or batches", 0);
        if (sectionCount > 4096) return fail("too many sections", sectionCount);
        uint32_t pool = 0, poolNear = 0;
        for (uint32_t i = 0; i < sectionCount; i++)
        {
            const Section& s = sections[i];
            const uint32_t start = FileStart(indexCount, s);
            if (s.level && start == s.indexStart) return fail("a level that names no window of the skin", i);
            if (start > indexCount || s.indexCount > indexCount - start) return fail("indices outside the skin", i);
            if (s.indexCount % 3) return fail("a count that is not whole triangles", i);
            if (static_cast<uint32_t>(s.vertexStart) + s.vertexCount > vertexCount) return fail("vertices outside the skin", i);
            const bool isFar = start >= kNear;
            // (with the far sections empty the stock client's own pool starts must all be ones it can hold)
            if (!isFar && s.indexCount && poolNear >= kNear) return fail("a near section after more than 65,535 near indices", i);
            if (isFar)
            {
                // (the near sections' are the stock client's to read; a far one's are written by this code: each must
                // name a vertex of its own section, or the rebased index would leave it)
                for (uint32_t j = 0; j < s.indexCount; j++)
                {
                    const uint16_t v = indices[start + j];
                    if (v < s.vertexStart || v >= static_cast<uint32_t>(s.vertexStart) + s.vertexCount) return fail("an index outside its section's vertices", i);
                }
                p.farSections++;
                p.farIndices += s.indexCount;
            }
            p.start.push_back(start);
            p.count.push_back(s.indexCount);
            p.vertexStart.push_back(s.vertexStart);
            p.isFar.push_back(isFar ? 1 : 0);
            p.pool.push_back(pool);
            p.poolNear.push_back(poolNear);
            pool += s.indexCount;
            if (!isFar) poolNear += s.indexCount;
        }
        p.total = pool;
        // the pool is made for the skin's index count (M2Shared.cpp 346-350, one instance: 0x10000 / count is 0 or 1)
        if (pool > indexCount) return fail("the sections hold more indices than the skin", sectionCount);
        // The device is handed a 16-bit start and this code finds the whole one by it: no two sections may share the low
        // half. (Counts are whole triangles and 65,536 is not, so below 196,608 indices none can; checked all the same.)
        if (pool > kMostIndices) return fail("more indices than the pool starts can tell apart", sectionCount);
        std::vector<std::pair<uint16_t, uint32_t>> lows;
        for (uint32_t i = 0; i < sectionCount; i++)
        {
            if (!p.count[i]) continue;
            lows.emplace_back(static_cast<uint16_t>(p.pool[i]), p.pool[i]);
        }
        std::sort(lows.begin(), lows.end());
        for (size_t i = 1; i < lows.size(); i++)
            if (lows[i].first == lows[i - 1].first) return fail("two sections' pool starts share their low half", static_cast<uint32_t>(i));
        for (const auto& low : lows)
            if (low.second >= kNear) p.high.push_back(low);
        // No two batches may match as CM2Model::OptimizeVisibleGeometry's BatchesMatch has it (the sections' bone lists are
        // all 0 once the vertices are made, M2Shared.cpp 1260-1263), or an optimized geometry is made of the file's
        // sections, where the far ones are empty.
        std::vector<std::tuple<uint16_t, uint16_t, uint16_t, uint16_t, uint16_t>> keys;
        for (uint32_t b = 0; b < batchCount; b++)
        {
            if (batches[b].sectionIndex >= sectionCount) return fail("a batch of no section", b);
            keys.emplace_back(batches[b].colorIndex, batches[b].materialIndex, batches[b].textureCombo, batches[b].textureWeightCombo, batches[b].textureTransformCombo);
        }
        std::sort(keys.begin(), keys.end());
        for (size_t i = 1; i < keys.size(); i++)
            if (keys[i] == keys[i - 1]) return fail("two batches the client would draw as one", static_cast<uint32_t>(i));
        p.valid = true;
        return p;
    }

    /**
     * Whether what was read as a parsed skin is one: sections, indices and batches there, each section's window inside the
     * index array, whole triangles, its vertices the skin's, each batch a section's. Native.cpp asks this of the game's own
     * skins before it lets a whole skin be read at all: that the arrays are found where it looks for them is then seen.
     */
    inline bool Sane(const Section* sections, uint32_t sectionCount, const Batch* batches, uint32_t batchCount,
                     const uint16_t* indices, uint32_t indexCount, uint32_t vertexCount)
    {
        if (!sections || !batches || !indices || !sectionCount || !batchCount || indexCount < 3 || !vertexCount) return false;
        if (sectionCount > 4096 || batchCount > 16384 || indexCount > 0x100000 || vertexCount > 0x10000) return false;
        uint32_t total = 0;
        for (uint32_t i = 0; i < sectionCount; i++)
        {
            const Section& s = sections[i];
            const uint32_t start = FileStart(indexCount, s);
            if (start > indexCount || s.indexCount > indexCount - start || s.indexCount % 3) return false;
            if (static_cast<uint32_t>(s.vertexStart) + s.vertexCount > vertexCount) return false;
            total += s.indexCount;
        }
        if (!total || total > indexCount) return false;
        for (uint32_t b = 0; b < batchCount; b++)
            if (batches[b].sectionIndex >= sectionCount) return false;
        for (uint32_t j = 0; j < indexCount; j++)
            if (indices[j] >= vertexCount) return false;
        return true;
    }

    /**
     * The sections as the stock client is to see them (in memory, when the skin has been parsed): no level, and a far
     * section empty. A wide skin that failed its checks loses every section that carries a level the same way.
     */
    inline void Normalize(Section* sections, uint32_t sectionCount, const Plan& p)
    {
        if (!p.wide || !sections) return;
        for (uint32_t i = 0; i < sectionCount; i++)
        {
            const bool empty = p.valid ? (i < p.isFar.size() && p.isFar[i]) : sections[i].level != 0;
            sections[i].level = 0;
            if (empty)
            {
                sections[i].indexStart = 0;
                sections[i].indexCount = 0;
            }
        }
    }

    /// The copies CM2Shared made of the sections, as the stock client alone leaves them after it filled the pool: true?
    inline bool CopiesAsStock(const Section* copies, const Plan& p)
    {
        for (size_t i = 0; i < p.count.size(); i++)
        {
            const uint16_t count = p.isFar[i] ? 0 : p.count[i];
            if (copies[i].indexCount != count || copies[i].vertexStart != p.vertexStart[i]) return false;
            if (count && copies[i].indexStart != static_cast<uint16_t>(p.poolNear[i])) return false;
        }
        return true;
    }

    /// ...and with every section whole (after Whole() and a stock fill).
    inline bool CopiesWhole(const Section* copies, const Plan& p)
    {
        for (size_t i = 0; i < p.count.size(); i++)
            if (copies[i].indexCount != p.count[i] || copies[i].indexStart != static_cast<uint16_t>(p.pool[i])) return false;
        return true;
    }

    /// Gives the copies their far sections' counts (whole == true) or takes them away again.
    inline void Whole(Section* copies, const Plan& p, bool whole)
    {
        for (size_t i = 0; i < p.count.size(); i++)
            if (p.isFar[i]) copies[i].indexCount = whole ? p.count[i] : 0;
    }

    enum class Rebase { Unknown, Section, None };

    /**
     * How the stock pass rebases an index, read from what it wrote for the near sections (`pool`: the locked shared
     * pool after a stock fill with every section whole): each minus its section's first vertex (M2Shared.cpp 405, 409:
     * the usual way), or as it is (a client that skins on the processor). Unknown when the pool does not hold what
     * either gives: the layout or the lock is not what this code takes it for, and nothing may be written.
     */
    inline Rebase Calibrate(const uint16_t* pool, const Plan& p, const uint16_t* indices)
    {
        bool section = true, none = true, told = false;
        uint32_t seen = 0;
        for (size_t i = 0; i < p.count.size() && (section || none); i++)
        {
            if (p.isFar[i] || !p.count[i]) continue;
            for (uint32_t j = 0; j < p.count[i]; j++)
            {
                const uint16_t in = indices[p.start[i] + j], out = pool[p.pool[i] + j];
                if (out != static_cast<uint16_t>(in - p.vertexStart[i])) section = false;
                if (out != in) none = false;
            }
            seen += p.count[i];
            if (p.vertexStart[i]) told = true;
        }
        if (!seen || !told) return Rebase::Unknown;       // (nothing to compare, or nothing that tells the two apart)
        if (section && !none) return Rebase::Section;
        if (none && !section) return Rebase::None;
        return Rebase::Unknown;
    }

    /// The far sections' triangles into their places in the pool.
    inline void WriteFar(uint16_t* pool, const Plan& p, const uint16_t* indices, Rebase how)
    {
        for (size_t i = 0; i < p.count.size(); i++)
        {
            if (!p.isFar[i]) continue;
            const uint16_t off = how == Rebase::Section ? p.vertexStart[i] : 0;
            for (uint32_t j = 0; j < p.count[i]; j++) pool[p.pool[i] + j] = static_cast<uint16_t>(indices[p.start[i] + j] - off);
        }
    }

    /// The whole pool start a draw's 16-bit start stands for (itself when it is one below 65,536).
    inline uint32_t DrawStart(const Plan& p, uint32_t start16)
    {
        if (start16 > 0xFFFF) return start16;
        const auto it = std::lower_bound(p.high.begin(), p.high.end(), std::make_pair(static_cast<uint16_t>(start16), uint32_t(0)));
        return it != p.high.end() && it->first == start16 ? it->second : start16;
    }

    /// A draw of a near section as the stock client alone makes it (the far ones still empty): start and count of one.
    inline bool StockDraw(const Plan& p, uint32_t start, uint32_t count)
    {
        for (size_t i = 0; i < p.count.size(); i++)
            if (!p.isFar[i] && p.count[i] && static_cast<uint16_t>(p.poolNear[i]) == start && p.count[i] == count) return true;
        return false;
    }

    // --- names ---------------------------------------------------------------------------------------------------

    /// A file's name as the lists hold it: lower case, backslashes.
    inline std::string Key(std::string_view path)
    {
        std::string out(path);
        for (char& c : out)
        {
            if (c == '/') c = '\\';
            else if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
        }
        return out;
    }

    inline bool EndsWith(std::string_view text, std::string_view end)
    {
        return text.size() >= end.size() && text.substr(text.size() - end.size()) == end;
    }

    /// The model a first skin profile belongs to ("...\\humanfemale00.skin" gives "...\\humanfemale"), or "" for another file.
    inline std::string ModelOfSkin(std::string_view path)
    {
        const std::string key = Key(path);
        if (!EndsWith(key, "00.skin") || key.size() <= 7) return std::string();
        return key.substr(0, key.size() - 7);
    }

    /// The model of a model file's name (".m2", or ".mdx"/".mdl" as the game's tables have it).
    inline std::string ModelOfFile(std::string_view path)
    {
        const std::string key = Key(path);
        for (const char* ext : {".m2", ".mdx", ".mdl"})
            if (EndsWith(key, ext)) return key.substr(0, key.size() - std::strlen(ext));
        return std::string();
    }

    /// The whole skin's name beside the cut one's: "...00.skin" gives "...00w.skin" (the asked name's own letters kept).
    inline std::string WideName(std::string_view skin)
    {
        if (skin.size() < 5) return std::string();
        return std::string(skin.substr(0, skin.size() - 5)) + "w.skin";
    }

    struct Listed
    {
        std::string model;          ///< Key() of the model's path without its extension
        uint32_t vertices = 0;      ///< the model file's vertex count the whole skin was made for
        uint32_t bytes = 0;         ///< ...and its size
    };

    /// Wrathpp\\wide.txt: "model path without extension<TAB>vertices<TAB>bytes" a line, '#' a comment.
    inline std::vector<Listed> ParseList(std::string_view text)
    {
        std::vector<Listed> out;
        size_t at = 0;
        while (at < text.size())
        {
            size_t end = text.find('\n', at);
            if (end == std::string_view::npos) end = text.size();
            std::string_view line = text.substr(at, end - at);
            at = end + 1;
            if (!line.empty() && line.back() == '\r') line.remove_suffix(1);
            if (line.empty() || line[0] == '#') continue;
            const size_t t1 = line.find('\t');
            const size_t t2 = t1 == std::string_view::npos ? t1 : line.find('\t', t1 + 1);
            if (t2 == std::string_view::npos || t1 == 0) continue;
            uint32_t numbers[2] = {0, 0};
            bool bad = false;
            for (int n = 0; n < 2 && !bad; n++)
            {
                const std::string_view digits = n == 0 ? line.substr(t1 + 1, t2 - t1 - 1) : line.substr(t2 + 1);
                if (digits.empty() || digits.size() > 9) bad = true;
                for (char c : digits)
                {
                    if (c < '0' || c > '9') { bad = true; break; }
                    numbers[n] = numbers[n] * 10 + static_cast<uint32_t>(c - '0');
                }
            }
            if (bad) continue;
            out.push_back(Listed{Key(line.substr(0, t1)), numbers[0], numbers[1]});
        }
        return out;
    }

    /// The app's switch (Interface\\GlueXML\\WrathppWideSkins.lua: "WrathppWideSkins = 0"): off only when it says 0.
    inline bool SwitchedOn(std::string_view script)
    {
        const size_t at = script.find("WrathppWideSkins");
        if (at == std::string_view::npos) return true;
        size_t i = script.find('=', at);
        if (i == std::string_view::npos) return true;
        for (i++; i < script.size() && (script[i] == ' ' || script[i] == '\t'); i++) {}
        return !(i < script.size() && script[i] == '0' && (i + 1 == script.size() || script[i + 1] < '0' || script[i + 1] > '9'));
    }

    // --- the stock functions this hooks or calls ----------------------------------------------------------------------

    /// A function of Wow.exe 12340 by the runtime's table of them (WarcraftXL core, include/wxl/offsets/generated:
    /// address, the distance to the next function, its decoded length; both measured on the stock image).
    struct StockFunction
    {
        const char* name;
        uint32_t address, bound, length;
    };

    /// What the image holds where a function is said to be, as far as it can be told without its bytes on file: the
    /// linker's padding (0xCC) from the function's end to the next one, and no padding where it begins. (Its first
    /// bytes may be a jump: the runtime's own detour.) `image` reads the bytes from `address` to `address + bound`.
    inline bool LooksLikeIt(const uint8_t* image, const StockFunction& f)
    {
        if (!image || !f.length || f.length > f.bound) return false;
        if (image[0] == 0xCC || image[0] == 0x00) return false;
        for (uint32_t i = f.length; i < f.bound; i++)
            if (image[i] != 0xCC) return false;
        return true;
    }

    /// The first bytes, for the start report.
    inline std::string Hex(const uint8_t* bytes, size_t count)
    {
        static const char digits[] = "0123456789ABCDEF";
        std::string out;
        for (size_t i = 0; i < count; i++)
        {
            if (i) out += ' ';
            out += digits[bytes[i] >> 4];
            out += digits[bytes[i] & 15];
        }
        return out;
    }
} // namespace wrathpp::wide

#endif
