// The reference: WarcraftXL's PeImage.cpp and wxl-core-patcher's steps (Main.cpp: large address aware,
// the two imports, the 19-byte entry trampoline), without its Windows file I/O. argv: in out
#include "patcher/PeImage.hpp"
#include <cstdio>
#include <vector>
#include <cstring>
using wxl::patcher::PeImage;
int main(int argc, char** argv) {
    FILE* f = fopen(argv[1], "rb"); std::vector<uint8_t> b; int c; while ((c = fgetc(f)) != EOF) b.push_back(uint8_t(c)); fclose(f);
    PeImage pe(b);
    if (!pe.valid()) { puts("not a 32-bit PE"); return 1; }
    pe.SetLargeAddressAware();
    if (pe.HasSection(".wxl") && pe.HasSection(".wxle")) { puts("already"); }
    else {
        const char* const funcs[] = { "WarcraftXL", "WarcraftXLEntry" };
        uint32_t iat[2] = {0, 0};
        if (!pe.AddImport("WarcraftXL.dll", funcs, 2, ".wxl", iat)) { puts("import failed"); return 1; }
        const uint32_t oep = pe.EntryPointVa();
        uint8_t cave[19] = { 0xE8,0,0,0,0, 0x58, 0x8B,0x88,0,0,0,0, 0xFF,0xD1, 0xE9,0,0,0,0 };
        const uint32_t caveVa = pe.AppendCode(cave, sizeof cave, ".wxle");
        if (!caveVa) { puts("cave failed"); return 1; }
        const uint32_t disp = iat[1] - (caveVa + 5), rel = oep - (caveVa + sizeof cave);
        memcpy(cave + 8, &disp, 4); memcpy(cave + 15, &rel, 4);
        pe.WriteVa(caveVa, cave, sizeof cave);
        pe.SetEntryPointVa(caveVa);
        printf("iat 0x%08X 0x%08X cave 0x%08X oep 0x%08X\n", iat[0], iat[1], caveVa, oep);
    }
    f = fopen(argv[2], "wb"); fwrite(b.data(), 1, b.size(), f); fclose(f);
    return 0;
}
