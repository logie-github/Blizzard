// SPDX-License-Identifier: GPL-3.0-or-later
// An MPQ of files, for the starting areas' package's stand-in game (tools/zones/package.py):
//
//   g++ -std=c++17 -O2 -I../../../mod-skyborne/src mkmpq.cpp ../../../mod-skyborne/src/SkyborneFiles.cpp -lz -o zones_mkmpq
//   zones_mkmpq OUT.MPQ ROOT NAMES
//
// NAMES: a file of paths in the game (backslashes), a line each; each is ROOT/<path> (slashes).
#include "SkyborneFiles.h"
#include <fstream>
#include <iostream>
using namespace Skyborne;

int main(int argc, char** argv)
{
    if (argc != 4)
    {
        std::cerr << "zones_mkmpq OUT.MPQ ROOT NAMES\n";
        return 2;
    }
    MpqWriter mpq(argv[1]);
    fs::path root = argv[2];
    std::ifstream names(argv[3]);
    std::string name;
    while (std::getline(names, name))
    {
        if (name.empty())
            continue;
        std::string rel = name;
        for (char& c : rel)
            if (c == '\\')
                c = '/';
        std::ifstream in(root / rel, std::ios::binary);
        if (!in)
        {
            std::cerr << "no file " << (root / rel) << "\n";
            return 1;
        }
        Bytes data((std::istreambuf_iterator<char>(in)), {});
        if (!mpq.Add(name, data))
            return 1;
    }
    return mpq.Finish() ? 0 : 1;
}
