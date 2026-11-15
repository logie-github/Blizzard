// Bounds-checked little-endian reads from a file held in memory. A read past the end yields
// zeros instead of crashing: a damaged download draws wrongly rather than taking the app down.
#pragma once

#include <cstdint>
#include <cstring>
#include <string>
#include <vector>

namespace wc {

using Bytes = std::vector<uint8_t>;

bool readFile(const std::string& path, Bytes& out);

struct Reader {
    const uint8_t* data;
    size_t size;
    Reader(const uint8_t* d, size_t n) : data(d), size(n) {}
    explicit Reader(const Bytes& b) : data(b.data()), size(b.size()) {}

    bool has(size_t off, size_t n) const { return off <= size && n <= size - off; }
    template <typename T> T get(size_t off) const {
        T v{};
        if (has(off, sizeof(T))) std::memcpy(&v, data + off, sizeof(T));
        return v;
    }
    uint32_t u32(size_t off) const { return get<uint32_t>(off); }
    int32_t i32(size_t off) const { return get<int32_t>(off); }
    uint16_t u16(size_t off) const { return get<uint16_t>(off); }
    int16_t i16(size_t off) const { return get<int16_t>(off); }
    uint8_t u8(size_t off) const { return get<uint8_t>(off); }
    float f32(size_t off) const { return get<float>(off); }
};

// An (count, offset) pair as M2 files store their arrays.
struct M2Array {
    uint32_t count = 0, offset = 0;
};

inline M2Array readArray(const Reader& r, size_t off) { return {r.u32(off), r.u32(off + 4)}; }

// Walks the four-character chunks of a WoW file. `reversed` is true for WMO and ADT files, whose
// chunk names are stored back to front ("REVM" for MVER); M2 chunks are stored as written.
struct Chunk {
    uint32_t tag;     // as read: compare with tag("MD21") or rtag("MOHD")
    size_t offset;    // payload
    uint32_t size;
};

constexpr uint32_t tag(const char s[5]) {
    return uint32_t(uint8_t(s[0])) | uint32_t(uint8_t(s[1])) << 8 | uint32_t(uint8_t(s[2])) << 16 | uint32_t(uint8_t(s[3])) << 24;
}
constexpr uint32_t rtag(const char s[5]) {
    return uint32_t(uint8_t(s[3])) | uint32_t(uint8_t(s[2])) << 8 | uint32_t(uint8_t(s[1])) << 16 | uint32_t(uint8_t(s[0])) << 24;
}

std::vector<Chunk> chunks(const Reader& r, size_t from, size_t to);

} // namespace wc
