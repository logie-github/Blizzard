// The wide skins' own logic (wrathpp-native/src/WideSkin.hpp) against a stand-in of the stock client's shared index pool:
// StockFill below is CM2Shared::SetIndices as the reconstruction has it (WarcraftXL-Labs/client, M2Shared.cpp 396-420, the
// 16-bit branch, one instance), the draw is CM2SceneRender's (475-476: the copy's 16-bit start and its count).
// Build and run: client-mod/tests/wide_skin.sh
#include "../wrathpp-native/src/WideSkin.hpp"

#include <cstdio>
#include <cstdlib>
#include <random>

using namespace wrathpp::wide;

namespace
{
    int g_fails = 0;

    void Check(bool ok, const char* what)
    {
        std::printf("%s %s\n", ok ? "ok  " : "FAIL", what);
        if (!ok) g_fails++;
    }

    struct Skin
    {
        std::vector<Section> sections;      // as the file has them
        std::vector<Batch> batches;
        std::vector<uint16_t> indices;
        uint32_t vertices = 0;
    };

    /// A skin of `counts` (indices a section), written as the converter writes a wide one.
    Skin Make(const std::vector<uint32_t>& counts, uint32_t seed = 7)
    {
        std::mt19937 rng(seed);
        Skin s;
        uint32_t vertex = 0;
        for (size_t i = 0; i < counts.size(); i++)
        {
            Section sec{};
            const uint32_t nv = std::max<uint32_t>(3, counts[i] / 6);
            sec.id = static_cast<uint16_t>(i < 3 ? 0 : i);
            sec.level = static_cast<uint16_t>(s.indices.size() >> 16);
            sec.indexStart = static_cast<uint16_t>(s.indices.size());
            sec.indexCount = static_cast<uint16_t>(counts[i]);
            sec.vertexStart = static_cast<uint16_t>(vertex);
            sec.vertexCount = static_cast<uint16_t>(nv);
            sec.boneCount = 4;
            sec.boneComboIndex = static_cast<uint16_t>(i * 4);
            sec.boneInfluences = 1;
            for (uint32_t j = 0; j < counts[i]; j++) s.indices.push_back(static_cast<uint16_t>(vertex + rng() % nv));
            vertex += nv;
            s.sections.push_back(sec);
            Batch b{};
            b.sectionIndex = b.geosetIndex = static_cast<uint16_t>(i);
            b.materialIndex = static_cast<uint16_t>(i);       // one of its own: no two batches match
            b.textureCount = 1;
            s.batches.push_back(b);
        }
        s.vertices = vertex;
        return s;
    }

    Plan ReadSkin(const Skin& s)
    {
        return Read(s.sections.data(), static_cast<uint32_t>(s.sections.size()), s.batches.data(), static_cast<uint32_t>(s.batches.size()),
                    s.indices.data(), static_cast<uint32_t>(s.indices.size()), s.vertices);
    }

    /// CM2Shared::SetIndices' fill: the count and first vertex from the shared's copy, the start from the file's section.
    void StockFill(std::vector<Section>& copies, const std::vector<Section>& file, const std::vector<uint16_t>& indices, std::vector<uint16_t>& pool, bool rebase = true)
    {
        uint32_t indexStart = 0;
        uint16_t* out = pool.data();
        for (size_t i = 0; i < file.size(); i++)
        {
            Section* section = &copies[i];
            const uint32_t start = file[i].indexStart;
            const uint16_t offset = rebase ? static_cast<uint16_t>(-section->vertexStart) : 0;
            for (uint32_t j = 0; j < section->indexCount; j++) out[j] = static_cast<uint16_t>(offset + indices[start + j]);
            out += section->indexCount;
            section->indexStart = static_cast<uint16_t>(indexStart);
            indexStart += section->indexCount;
        }
    }

    /// What a draw of section `i` reads from the pool, against what the file says the section is.
    bool DrawsRight(const Skin& s, const Plan& p, const std::vector<Section>& copies, const std::vector<uint16_t>& pool, size_t i, bool fixed, bool rebase = true)
    {
        const uint32_t start = fixed ? DrawStart(p, copies[i].indexStart) : copies[i].indexStart;
        if (copies[i].indexCount != s.sections[i].indexCount) return false;
        const uint32_t from = (static_cast<uint32_t>(s.sections[i].level) << 16) | s.sections[i].indexStart;
        for (uint32_t j = 0; j < copies[i].indexCount; j++)
            if (pool[start + j] != static_cast<uint16_t>(s.indices[from + j] - (rebase ? s.sections[i].vertexStart : 0))) return false;
        return true;
    }

    void WholeFlow(const char* name, const std::vector<uint32_t>& counts, bool rebase)
    {
        std::printf("-- %s\n", name);
        const Skin s = Make(counts);
        const Plan p = ReadSkin(s);
        Check(p.wide && p.valid, "read: wide and valid");
        if (!p.valid) { std::printf("     (%s)\n", p.why.c_str()); return; }
        uint32_t far = 0;
        for (uint8_t f : p.far) far += f;
        Check(far > 0 && far == p.farSections && far < counts.size(), "some sections are far, some near");

        // as the stock client alone sees it
        std::vector<Section> file = s.sections;
        Normalize(file.data(), static_cast<uint32_t>(file.size()), p);
        bool clean = true;
        for (size_t i = 0; i < file.size(); i++)
        {
            if (file[i].level) clean = false;
            if (p.far[i] && (file[i].indexCount || file[i].indexStart)) clean = false;
            if (!p.far[i] && (file[i].indexCount != s.sections[i].indexCount || file[i].indexStart != s.sections[i].indexStart)) clean = false;
            if (file[i].id != s.sections[i].id) clean = false;
        }
        Check(clean, "normalized: no level, far sections empty, near ones and every id untouched");
        std::vector<Section> copies = file;                       // InitializeSkinProfile's memcpy
        std::vector<uint16_t> pool(s.indices.size(), 0xDEAD);     // the pool is made for the skin's index count
        StockFill(copies, file, s.indices, pool, rebase);
        Check(CopiesAsStock(copies.data(), p), "stock fill, far sections empty: the copies are as expected");
        bool near = true, empty = true;
        for (size_t i = 0; i < file.size(); i++)
        {
            if (!p.far[i] && !DrawsRight(s, p, copies, pool, i, false, rebase)) near = false;
            if (p.far[i] && copies[i].indexCount) empty = false;
            if (!p.far[i] && !StockDraw(p, copies[i].indexStart, copies[i].indexCount)) near = false;
        }
        Check(near, "  every near section draws its own triangles with no hook at all");
        Check(empty, "  every far section draws nothing");
        Check(!StockDraw(p, 1, 3), "  a draw that is no section's is not taken for one");

        // made whole
        Whole(copies.data(), p, true);
        StockFill(copies, file, s.indices, pool, rebase);
        Check(CopiesWhole(copies.data(), p), "stock fill, every section whole: the copies' starts are the pool starts' low halves");
        const Rebase how = Calibrate(pool.data(), p, s.indices.data());
        Check(how == (rebase ? Rebase::Section : Rebase::None), "calibrated against the stock pass's own output");
        bool wrongBefore = false;
        for (size_t i = 0; i < file.size(); i++)
            if (p.far[i] && !DrawsRight(s, p, copies, pool, i, true, rebase)) wrongBefore = true;
        Check(wrongBefore, "  (before the far sections are written the stock pass left the wrong triangles there)");
        WriteFar(pool.data(), p, s.indices.data(), how);
        bool all = true, unfixedWrong = false;
        for (size_t i = 0; i < file.size(); i++)
        {
            if (!DrawsRight(s, p, copies, pool, i, true, rebase)) all = false;
            if (p.pool[i] >= kNear && !DrawsRight(s, p, copies, pool, i, false, rebase)) unfixedWrong = true;
        }
        Check(all, "every section, near and far, draws its own triangles through DrawStart");
        Check(unfixedWrong, "  (and a section past 65,535 in the pool would not without it)");
        Check(DrawStart(p, 70000) == 70000, "  a start already whole is left alone");

        // taken back (a failure after it was made whole)
        Whole(copies.data(), p, false);
        bool back = true;
        for (size_t i = 0; i < file.size(); i++)
        {
            if (p.far[i] && copies[i].indexCount) back = false;
            if (!p.far[i] && p.pool[i] < kNear && !DrawsRight(s, p, copies, pool, i, false, rebase)) back = false;
        }
        Check(back, "taken back: far sections empty again, near ones still right");
    }
}

int main()
{
    // Human woman's shape: body and gear first, the hair styles last (about 121,000 indices)
    std::vector<uint32_t> human;
    for (int i = 0; i < 40; i++) human.push_back(300 + 3 * ((i * 977) % 900));
    for (int i = 0; i < 24; i++) human.push_back(2400 + 3 * ((i * 131) % 500));
    WholeFlow("a skin of about 121,000 indices, rebased", human, true);
    WholeFlow("the same on a client that does not rebase", human, false);
    WholeFlow("one section across the 65,535th index", {30000, 33000, 9000, 60000, 3000, 21000}, true);

    std::printf("-- what is refused\n");
    {
        const Skin small = Make({300, 600, 900});
        const Plan p = ReadSkin(small);
        Check(!p.wide && !p.valid, "a skin of 1,800 indices with no level is not wide: left to the game");
        std::vector<Section> file = small.sections;
        Normalize(file.data(), 3, p);
        Check(std::memcmp(file.data(), small.sections.data(), 3 * sizeof(Section)) == 0, "  and nothing of it is changed");
    }
    {
        Skin s = Make({300, 600, 900});
        s.sections[1].level = 3;                     // 3.3.5's own LOD marker: names no window of 1,800 indices
        const Plan p = ReadSkin(s);
        Check(p.wide && !p.valid, "a level that names no window: refused");
        std::vector<Section> file = s.sections;
        Normalize(file.data(), 3, p);
        Check(file[1].level == 0 && file[1].indexCount == 0 && file[0].indexCount == 300 && file[2].indexCount == 900,
              "  normalized: that section empty, the others as they were");
    }
    {
        Skin s = Make(human);
        s.batches[5].materialIndex = s.batches[4].materialIndex;
        Check(!ReadSkin(s).valid, "two batches the client would draw as one (an optimized geometry): refused");
    }
    {
        Skin s = Make(human);
        s.indices[100000] = 3;                       // a far section naming another's vertex
        Check(!ReadSkin(s).valid, "a far section's index outside its own vertices: refused");
    }
    {
        Skin s = Make(human);
        s.sections.back().indexCount += 3;           // past the end of the index array
        Check(!ReadSkin(s).valid, "a window past the end of the skin: refused");
    }
    {
        std::vector<uint32_t> huge(66, 3000);        // 198,000 indices
        const Plan p = ReadSkin(Make(huge));
        Check(p.wide && !p.valid, "more indices than the 16-bit starts can tell apart (196,607): refused");
    }
    {
        // the pool does not hold what the stock pass would have written (another layout, a lock that hands other memory)
        const Skin s = Make(human);
        const Plan p = ReadSkin(s);
        std::vector<uint16_t> pool(s.indices.size(), 0);
        Check(Calibrate(pool.data(), p, s.indices.data()) == Rebase::Unknown, "a pool that is not the stock pass's: not calibrated, nothing is written");
    }

    std::printf("-- names, the list, the switch\n");
    Check(ModelOfSkin("Character\\Human\\Female\\HumanFemale00.skin") == "character\\human\\female\\humanfemale", "the model of a first skin profile");
    Check(ModelOfSkin("character/human/female/humanfemale00.SKIN") == "character\\human\\female\\humanfemale", "  whatever its case and slashes");
    Check(ModelOfSkin("Character\\Human\\Female\\HumanFemale01.skin").empty() && ModelOfSkin("x.blp").empty() && ModelOfSkin("00.skin").empty(), "  no other file's");
    Check(ModelOfFile("Character\\Human\\Female\\HumanFemale.M2") == "character\\human\\female\\humanfemale" && ModelOfFile("a\\b.mdx") == "a\\b" && ModelOfFile("a\\b.blp").empty(), "the model of a model file");
    Check(WideName("Character\\Human\\Female\\HumanFemale00.skin") == "Character\\Human\\Female\\HumanFemale00w.skin", "the whole skin's name");
    {
        const auto list = ParseList("# models\r\nCharacter\\Human\\Female\\HumanFemale\t41234\t18124396\r\nbad line\nCharacter/Orc/Male/OrcMale\t100\t200\nx\ty\t3\n");
        Check(list.size() == 2 && list[0].model == "character\\human\\female\\humanfemale" && list[0].vertices == 41234 && list[0].bytes == 18124396 &&
              list[1].model == "character\\orc\\male\\orcmale" && list[1].vertices == 100 && list[1].bytes == 200, "the list: two models, the bad lines left out");
    }
    Check(SwitchedOn("") && SwitchedOn("WrathppWideSkins = 1\n") && !SwitchedOn("WrathppWideSkins = 0\n") && !SwitchedOn("WrathppWideSkins=0") && SwitchedOn("WrathppWideSkins = 01"),
          "the switch: on unless the script says 0");
    {
        const StockFunction f{"f", 0x1000, 0x10, 0x0D};
        const uint8_t right[16] = {0x55, 0x8B, 0xEC, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xC3, 0xCC, 0xCC, 0xCC};
        uint8_t wrong[16];
        std::memcpy(wrong, right, 16);
        wrong[14] = 0x90;
        const uint8_t pad[16] = {0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC};
        Check(LooksLikeIt(right, f) && !LooksLikeIt(wrong, f) && !LooksLikeIt(pad, f), "a function's place: padded to the next one after its length, not padding itself");
        Check(Hex(right, 3) == "55 8B EC", "its first bytes for the report");
    }

    std::printf("%s\n", g_fails ? "FAILED" : "all passed");
    return g_fails ? 1 : 0;
}
