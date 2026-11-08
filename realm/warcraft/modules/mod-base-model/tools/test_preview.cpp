// SPDX-License-Identifier: GPL-3.0-or-later
#include "../src/BodyPreview.h"
#include <cassert>
#include <iostream>
int main()
{
    // All races/classes share the packed sex byte, including the added races.
    for (uint8_t race : {1, 5, 10, 12, 13, 15, 19, 20})
        for (uint8_t sex : {0, 1})
        {
            std::vector<uint8_t> row(296, 42);
            row[4] = race; row[5] = 1; row[6] = sex; row[7] = 0;
            auto original = row;
            BodyPreview::Apply(row);
            if (sex == 0) assert(row == original);
            else {
                assert(std::equal(row.begin(), row.begin() + 8, original.begin()));
                // every slot empty as the game's own are: item, display and inventory type -1
                assert(std::all_of(row.begin() + 8, row.end(), [](uint8_t b) { return b == 0xFF; }));
            }
        }
    // Other table shapes must not be treated as creation outfits.
    std::vector<uint8_t> other(300, 1); auto original = other;
    BodyPreview::Apply(other); assert(other == original);
    std::cout << "Body preview: female creation outfits only; male rows and other tables preserved\n";
}
