// BLP2, the game's texture format: palettised, DXT1/3/5 or plain BGRA, each with its mipmaps.
#pragma once

#include <cstdint>
#include <vector>

#include "bytes.h"

namespace wc {

struct Image {
    int width = 0, height = 0;
    bool hasAlpha = false;
    std::vector<uint8_t> rgba;   // width * height * 4
};

// Decodes the largest mip level no bigger than maxSize on either side (the whole image when it
// fits). Returns false for a file that isn't a BLP2 texture.
bool decodeBlp(const Bytes& file, int maxSize, Image& out);

} // namespace wc
