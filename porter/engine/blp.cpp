#include "blp.h"

#include <algorithm>

namespace wc {

namespace {

void rgb565(uint16_t c, uint8_t out[3]) {
    out[0] = uint8_t(((c >> 11) & 31) * 255 / 31);
    out[1] = uint8_t(((c >> 5) & 63) * 255 / 63);
    out[2] = uint8_t((c & 31) * 255 / 31);
}

// One 4x4 colour block of DXT1 (with its 1-bit alpha when `dxt1`) or of DXT3/5 (always 4 colours).
void colourBlock(const uint8_t* b, bool dxt1, uint8_t px[16][4]) {
    uint16_t c0 = uint16_t(b[0] | b[1] << 8), c1 = uint16_t(b[2] | b[3] << 8);
    uint8_t pal[4][4];
    rgb565(c0, pal[0]); rgb565(c1, pal[1]);
    pal[0][3] = pal[1][3] = 255;
    if (!dxt1 || c0 > c1) {
        for (int i = 0; i < 3; ++i) {
            pal[2][i] = uint8_t((2 * pal[0][i] + pal[1][i]) / 3);
            pal[3][i] = uint8_t((pal[0][i] + 2 * pal[1][i]) / 3);
        }
        pal[2][3] = pal[3][3] = 255;
    } else {
        for (int i = 0; i < 3; ++i) { pal[2][i] = uint8_t((pal[0][i] + pal[1][i]) / 2); pal[3][i] = 0; }
        pal[2][3] = 255; pal[3][3] = 0;
    }
    uint32_t bits = uint32_t(b[4] | b[5] << 8 | b[6] << 16 | uint32_t(b[7]) << 24);
    for (int i = 0; i < 16; ++i) {
        const uint8_t* p = pal[(bits >> (2 * i)) & 3];
        px[i][0] = p[0]; px[i][1] = p[1]; px[i][2] = p[2]; px[i][3] = p[3];
    }
}

void decodeDxt(const uint8_t* src, size_t len, int w, int h, int kind, uint8_t* dst) {
    // kind: 1 = DXT1, 3 = DXT3, 5 = DXT5
    size_t blockBytes = kind == 1 ? 8 : 16;
    int bw = (w + 3) / 4, bh = (h + 3) / 4;
    for (int by = 0; by < bh; ++by)
        for (int bx = 0; bx < bw; ++bx) {
            size_t off = (size_t(by) * bw + bx) * blockBytes;
            if (off + blockBytes > len) return;
            const uint8_t* b = src + off;
            uint8_t px[16][4];
            colourBlock(kind == 1 ? b : b + 8, kind == 1, px);
            if (kind == 3) {
                for (int i = 0; i < 16; ++i) {
                    uint8_t a = (b[i / 2] >> ((i & 1) * 4)) & 15;
                    px[i][3] = uint8_t(a * 17);
                }
            } else if (kind == 5) {
                uint8_t a0 = b[0], a1 = b[1], ap[8];
                ap[0] = a0; ap[1] = a1;
                if (a0 > a1) for (int i = 1; i < 7; ++i) ap[i + 1] = uint8_t(((7 - i) * a0 + i * a1) / 7);
                else {
                    for (int i = 1; i < 5; ++i) ap[i + 1] = uint8_t(((5 - i) * a0 + i * a1) / 5);
                    ap[6] = 0; ap[7] = 255;
                }
                uint64_t bits = 0;
                for (int i = 0; i < 6; ++i) bits |= uint64_t(b[2 + i]) << (8 * i);
                for (int i = 0; i < 16; ++i) px[i][3] = ap[(bits >> (3 * i)) & 7];
            }
            for (int i = 0; i < 16; ++i) {
                int x = bx * 4 + (i & 3), y = by * 4 + (i >> 2);
                if (x >= w || y >= h) continue;
                std::copy(px[i], px[i] + 4, dst + (size_t(y) * w + x) * 4);
            }
        }
}

} // namespace

bool decodeBlp(const Bytes& file, int maxSize, Image& out) {
    Reader r(file);
    if (file.size() < 148 || r.u32(0) != tag("BLP2")) return false;
    uint8_t encoding = r.u8(8), alphaDepth = r.u8(9), alphaEncoding = r.u8(10);
    int w = int(r.u32(12)), h = int(r.u32(16));
    if (w <= 0 || h <= 0) return false;

    int level = 0;
    while (level < 15 && (w > maxSize || h > maxSize)) {
        uint32_t nextOff = r.u32(20 + 4 * (level + 1)), nextSize = r.u32(84 + 4 * (level + 1));
        if (!nextOff || !nextSize) break;
        ++level; w = std::max(1, w / 2); h = std::max(1, h / 2);
    }
    uint32_t off = r.u32(20 + 4 * level), len = r.u32(84 + 4 * level);
    if (!r.has(off, len)) { len = off < file.size() ? uint32_t(file.size() - off) : 0; }
    if (!len) return false;
    const uint8_t* src = file.data() + off;

    out.width = w; out.height = h;
    out.rgba.assign(size_t(w) * h * 4, 255);
    out.hasAlpha = alphaDepth > 0;
    uint8_t* dst = out.rgba.data();

    if (encoding == 1) {   // palettised, then alphaDepth bits of alpha per pixel
        size_t n = size_t(w) * h;
        for (size_t i = 0; i < n && i < len; ++i) {
            uint32_t c = r.u32(148 + 4 * src[i]);
            dst[i * 4] = uint8_t(c >> 16); dst[i * 4 + 1] = uint8_t(c >> 8); dst[i * 4 + 2] = uint8_t(c);
            uint8_t a = 255;
            if (alphaDepth == 8) a = n + i < len ? src[n + i] : 255;
            else if (alphaDepth == 4) { size_t k = n + i / 2; a = k < len ? uint8_t(((src[k] >> ((i & 1) * 4)) & 15) * 17) : 255; }
            else if (alphaDepth == 1) { size_t k = n + i / 8; a = k < len && (src[k] >> (i & 7)) & 1 ? 255 : 0; }
            dst[i * 4 + 3] = a;
        }
    } else if (encoding == 2) {
        int kind = alphaEncoding == 7 ? 5 : alphaEncoding == 1 ? 3 : 1;
        decodeDxt(src, len, w, h, kind, dst);
        if (kind == 1 && alphaDepth == 0)
            for (size_t i = 0; i < size_t(w) * h; ++i) dst[i * 4 + 3] = 255;
    } else if (encoding == 3) {   // BGRA
        size_t n = std::min(size_t(w) * h, size_t(len) / 4);
        for (size_t i = 0; i < n; ++i) {
            dst[i * 4] = src[i * 4 + 2]; dst[i * 4 + 1] = src[i * 4 + 1];
            dst[i * 4 + 2] = src[i * 4]; dst[i * 4 + 3] = src[i * 4 + 3];
        }
        out.hasAlpha = true;
    } else {
        return false;
    }
    return true;
}

} // namespace wc
