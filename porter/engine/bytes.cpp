#include "bytes.h"

#include <cstdio>

namespace wc {

bool readFile(const std::string& path, Bytes& out) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fseek(f, 0, SEEK_END);
    long n = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);
    if (n < 0) { std::fclose(f); return false; }
    out.resize(size_t(n));
    size_t got = n ? std::fread(out.data(), 1, size_t(n), f) : 0;
    std::fclose(f);
    return got == size_t(n);
}

std::vector<Chunk> chunks(const Reader& r, size_t from, size_t to) {
    std::vector<Chunk> out;
    if (to > r.size) to = r.size;
    size_t o = from;
    while (o + 8 <= to) {
        uint32_t t = r.u32(o), n = r.u32(o + 4);
        if (n > to - o - 8) n = uint32_t(to - o - 8);
        out.push_back({t, o + 8, n});
        o += 8 + size_t(n);
    }
    return out;
}

} // namespace wc
