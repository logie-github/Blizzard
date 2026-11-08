// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef MOD_BODY_PREVIEW_H
#define MOD_BODY_PREVIEW_H
#include <algorithm>
#include <vector>
#include <cstdint>
namespace BodyPreview
{
    // 3.3.5: id (4 bytes), race/class/sex/outfit (one byte each), then 24 item IDs,
    // 24 display IDs and 24 inventory types. Only the client's creation outfits are edited.
    // A slot is emptied as the game's own empty slots are: -1 in all three (0xFF bytes). Zeros
    // read as an item of display 0 in inventory type 0, which the creation screen dressed the
    // preview with (issue #119: the game's heap corrupted on that screen, ERROR #132).
    inline void Apply(std::vector<uint8_t>& row)
    {
        if (row.size() == 296 && row[6] == 1)
            std::fill(row.begin() + 8, row.end(), uint8_t(0xFF));
    }
}
#endif
