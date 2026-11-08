// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Pictures for Ralia's mod's patch (RaliaImage.h).
 */

#include "RaliaImage.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <vector>

namespace Ralia
{
    namespace
    {
        uint32_t Get32(uint8_t const* p) { return uint32_t(p[0]) | uint32_t(p[1]) << 8 | uint32_t(p[2]) << 16 | uint32_t(p[3]) << 24; }

        void Put32(uint8_t* p, uint32_t v)
        {
            p[0] = uint8_t(v); p[1] = uint8_t(v >> 8); p[2] = uint8_t(v >> 16); p[3] = uint8_t(v >> 24);
        }

        uint8_t Byte(double v) { return uint8_t(std::lround(std::clamp(v, 0.0, 255.0))); }

        // One axis resampled: [count] values [stride] apart in each of [lines] lines [pitch] apart,
        // [from] long made [to] long.
        struct Tap { uint32_t at; float weight; };

        std::vector<std::vector<Tap>> Taps(uint32_t from, uint32_t to)
        {
            std::vector<std::vector<Tap>> taps(to);
            if (to < from)
            {
                // smaller: each value the average of the stretch it covers
                double scale = double(from) / to;
                for (uint32_t i = 0; i < to; ++i)
                {
                    double a = i * scale, b = (i + 1) * scale;
                    for (uint32_t s = uint32_t(a); s < from && s < b; ++s)
                    {
                        double w = std::min<double>(s + 1, b) - std::max<double>(s, a);
                        if (w > 0)
                            taps[i].push_back({ s, float(w / scale) });
                    }
                }
            }
            else
            {
                // larger (or the same): read between the two nearest
                double scale = double(from) / to;
                for (uint32_t i = 0; i < to; ++i)
                {
                    double s = std::clamp((i + 0.5) * scale - 0.5, 0.0, double(from - 1));
                    uint32_t s0 = uint32_t(s), s1 = std::min(s0 + 1, from - 1);
                    double f = s - s0;
                    taps[i].push_back({ s0, float(1 - f) });
                    if (f > 0)
                        taps[i].push_back({ s1, float(f) });
                }
            }
            return taps;
        }

        // A summed-area table's box average of [values] (width x height) at radius [r].
        std::vector<float> BoxAverage(std::vector<float> const& values, uint32_t width, uint32_t height, int r)
        {
            std::vector<double> sum(size_t(width + 1) * (height + 1), 0);
            for (uint32_t y = 0; y < height; ++y)
            {
                double row = 0;
                for (uint32_t x = 0; x < width; ++x)
                {
                    row += values[size_t(y) * width + x];
                    sum[size_t(y + 1) * (width + 1) + x + 1] = sum[size_t(y) * (width + 1) + x + 1] + row;
                }
            }
            std::vector<float> out(values.size());
            for (uint32_t y = 0; y < height; ++y)
                for (uint32_t x = 0; x < width; ++x)
                {
                    int x0 = std::max<int>(0, int(x) - r), x1 = std::min<int>(int(width), int(x) + r + 1);
                    int y0 = std::max<int>(0, int(y) - r), y1 = std::min<int>(int(height), int(y) + r + 1);
                    double s = sum[size_t(y1) * (width + 1) + x1] - sum[size_t(y0) * (width + 1) + x1]
                        - sum[size_t(y1) * (width + 1) + x0] + sum[size_t(y0) * (width + 1) + x0];
                    out[size_t(y) * width + x] = float(s / double((x1 - x0) * (y1 - y0)));
                }
            return out;
        }
    }

    Image Crop(Image const& image, uint32_t x, uint32_t y, uint32_t width, uint32_t height)
    {
        Image out;
        width = std::min(width, image.width > x ? image.width - x : 0);
        height = std::min(height, image.height > y ? image.height - y : 0);
        out.width = width;
        out.height = height;
        out.rgba.resize(size_t(width) * height * 4);
        for (uint32_t row = 0; row < height; ++row)
            std::memcpy(&out.rgba[size_t(row) * width * 4], &image.rgba[(size_t(y + row) * image.width + x) * 4], size_t(width) * 4);
        return out;
    }

    Image Resize(Image const& image, uint32_t width, uint32_t height)
    {
        if (!image.width || !image.height || !width || !height)
            return Image{};
        if (width == image.width && height == image.height)
            return image;
        auto across = Taps(image.width, width), down = Taps(image.height, height);
        // across first, into floats; then down
        std::vector<float> wide(size_t(width) * image.height * 4);
        for (uint32_t y = 0; y < image.height; ++y)
            for (uint32_t x = 0; x < width; ++x)
                for (Tap const& t : across[x])
                    for (int c = 0; c < 4; ++c)
                        wide[(size_t(y) * width + x) * 4 + c] += t.weight * image.rgba[(size_t(y) * image.width + t.at) * 4 + c];
        Image out;
        out.width = width;
        out.height = height;
        out.rgba.resize(size_t(width) * height * 4);
        for (uint32_t y = 0; y < height; ++y)
            for (uint32_t x = 0; x < width; ++x)
                for (int c = 0; c < 4; ++c)
                {
                    double v = 0;
                    for (Tap const& t : down[y])
                        v += t.weight * wide[(size_t(t.at) * width + x) * 4 + c];
                    out.rgba[(size_t(y) * width + x) * 4 + c] = Byte(v);
                }
        return out;
    }

    Image Body(Image const& image)
    {
        if (image.width == image.height * 2)
            return Crop(image, 0, 0, image.width / 2, image.height);
        return image;
    }

    Image Repaint(Image const& target, Image const& before, Image const& after, double& changed)
    {
        Image out = target;
        changed = 0;
        uint32_t w = target.width, h = target.height;
        size_t n = size_t(w) * h;
        if (before.width != w || before.height != h || after.width != w || after.height != h || !n)
            return out;
        // How much the change is at each pixel (the three colours' differences), over 5 x 5 pixels so a
        // compressed texture's or a palette's small errors don't count; the change taken in from a
        // difference of 12 (none) to 36 (all of it).
        std::vector<float> diff(n);
        for (size_t i = 0; i < n; ++i)
            diff[i] = float(std::abs(int(after.rgba[i * 4]) - int(before.rgba[i * 4]))
                + std::abs(int(after.rgba[i * 4 + 1]) - int(before.rgba[i * 4 + 1]))
                + std::abs(int(after.rgba[i * 4 + 2]) - int(before.rgba[i * 4 + 2])));
        std::vector<float> near = BoxAverage(diff, w, h, 2);
        size_t touched = 0;
        for (size_t i = 0; i < n; ++i)
        {
            double m = std::clamp((near[i] - 12.0) / 24.0, 0.0, 1.0);
            if (m <= 0)
                continue;
            ++touched;
            for (int c = 0; c < 3; ++c)
            {
                double t = target.rgba[i * 4 + c];
                double ratio = (after.rgba[i * 4 + c] + 8.0) / (before.rgba[i * 4 + c] + 8.0);
                double changedColour = std::clamp(t * ratio, 0.0, 255.0);
                out.rgba[i * 4 + c] = Byte(t * (1 - m) + changedColour * m);
            }
        }
        changed = double(touched) / double(n);
        return out;
    }

    bool InBody(uint32_t x, uint32_t y, uint32_t width, uint32_t height)
    {
        return x * 2 >= width && y * 8 < height * 5;
    }

    Image Fit(Image const& game, Image const& set, bool withAlpha)
    {
        Image out = game;
        uint32_t w = game.width, h = game.height;
        if (set.width != w || set.height != h || !w || !h)
            return out;
        double sumGame[3] = { 0, 0, 0 }, sumSet[3] = { 0, 0, 0 };
        for (uint32_t y = 0; y < h; ++y)
            for (uint32_t x = 0; x < w; ++x)
                if (InBody(x, y, w, h))
                    for (int c = 0; c < 3; ++c)
                    {
                        sumGame[c] += game.rgba[(size_t(y) * w + x) * 4 + c];
                        sumSet[c] += set.rgba[(size_t(y) * w + x) * 4 + c];
                    }
        double gain[3];
        for (int c = 0; c < 3; ++c)
            gain[c] = std::clamp((sumGame[c] + 1.0) / (sumSet[c] + 1.0), 0.5, 2.0);
        for (uint32_t y = 0; y < h; ++y)
            for (uint32_t x = 0; x < w; ++x)
            {
                if (!InBody(x, y, w, h))
                    continue;
                size_t i = (size_t(y) * w + x) * 4;
                for (int c = 0; c < 3; ++c)
                    out.rgba[i + c] = Byte(set.rgba[i + c] * gain[c]);
                if (withAlpha)
                    out.rgba[i + 3] = set.rgba[i + 3];
            }
        return out;
    }

    Image KeepOutside(Image changed, Image const& game)
    {
        uint32_t w = game.width, h = game.height;
        if (changed.width != w || changed.height != h)
            return changed;
        for (uint32_t y = 0; y < h; ++y)
            for (uint32_t x = 0; x < w; ++x)
                if (!InBody(x, y, w, h))
                    std::memcpy(&changed.rgba[(size_t(y) * w + x) * 4], &game.rgba[(size_t(y) * w + x) * 4], 4);
        return changed;
    }

    double Distance(Image const& a, Image const& b)
    {
        Image sa = Resize(a, 16, 16), sb = Resize(b, 16, 16);
        if (sa.rgba.size() != sb.rgba.size() || sa.rgba.empty())
            return 1e18;
        double sum = 0;
        for (size_t i = 0; i < sa.rgba.size(); i += 4)
            for (int c = 0; c < 3; ++c)
            {
                double d = double(sa.rgba[i + c]) - double(sb.rgba[i + c]);
                sum += d * d;
            }
        return sum / (sa.rgba.size() / 4);
    }

    // The palette -------------------------------------------------------------------------------------

    namespace
    {
        // Colours counted in 6 bits a channel (a bin each), the palette cut from the bins.
        constexpr uint32_t BITS = 6, SIDE = 1u << BITS, BINS = SIDE * SIDE * SIDE;

        uint32_t BinOf(uint8_t const* rgb) { return (uint32_t(rgb[0] >> 2) << 12) | (uint32_t(rgb[1] >> 2) << 6) | uint32_t(rgb[2] >> 2); }
        int Channel(uint32_t bin, int c) { return int((bin >> (12 - 6 * c)) & (SIDE - 1)); }

        struct Bins
        {
            std::vector<uint32_t> count = std::vector<uint32_t>(BINS, 0);
            std::vector<std::array<uint64_t, 3>> sum = std::vector<std::array<uint64_t, 3>>(BINS, { 0, 0, 0 });
        };

        struct Box
        {
            std::vector<uint32_t> bins;
            uint64_t population = 0;
            int longest = 0, range = 0;

            void Measure(Bins const& b)
            {
                population = 0;
                int lo[3] = { 63, 63, 63 }, hi[3] = { 0, 0, 0 };
                for (uint32_t bin : bins)
                {
                    population += b.count[bin];
                    for (int c = 0; c < 3; ++c)
                    {
                        lo[c] = std::min(lo[c], Channel(bin, c));
                        hi[c] = std::max(hi[c], Channel(bin, c));
                    }
                }
                range = -1;
                for (int c = 0; c < 3; ++c)
                    if (hi[c] - lo[c] > range)
                    {
                        range = hi[c] - lo[c];
                        longest = c;
                    }
            }
        };

        // Up to 256 colours for the pixels counted in [b]: the boxes of bins cut in two at the median of
        // their longest side, the most crowded first, each box's colour its pixels' average.
        std::vector<std::array<uint8_t, 3>> CutPalette(Bins const& b)
        {
            std::vector<Box> boxes(1);
            for (uint32_t bin = 0; bin < BINS; ++bin)
                if (b.count[bin])
                    boxes[0].bins.push_back(bin);
            boxes[0].Measure(b);
            while (boxes.size() < 256)
            {
                size_t pick = boxes.size();
                for (size_t i = 0; i < boxes.size(); ++i)
                    if (boxes[i].range > 0 && boxes[i].bins.size() > 1
                        && (pick == boxes.size() || boxes[i].population > boxes[pick].population))
                        pick = i;
                if (pick == boxes.size())
                    break;
                Box& box = boxes[pick];
                int c = box.longest;
                std::sort(box.bins.begin(), box.bins.end(), [c](uint32_t x, uint32_t y) { return Channel(x, c) < Channel(y, c); });
                uint64_t half = box.population / 2, run = 0;
                size_t cut = 1;
                for (size_t i = 0; i + 1 < box.bins.size(); ++i)
                {
                    run += b.count[box.bins[i]];
                    cut = i + 1;
                    if (run >= half)
                        break;
                }
                Box other;
                other.bins.assign(box.bins.begin() + cut, box.bins.end());
                box.bins.resize(cut);
                box.Measure(b);
                other.Measure(b);
                boxes.push_back(std::move(other));
            }
            std::vector<std::array<uint8_t, 3>> palette;
            for (Box const& box : boxes)
            {
                uint64_t n = 0, s[3] = { 0, 0, 0 };
                for (uint32_t bin : box.bins)
                {
                    n += b.count[bin];
                    for (int c = 0; c < 3; ++c)
                        s[c] += b.sum[bin][c];
                }
                if (!n)
                    continue;
                palette.push_back({ uint8_t((s[0] + n / 2) / n), uint8_t((s[1] + n / 2) / n), uint8_t((s[2] + n / 2) / n) });
            }
            if (palette.empty())
                palette.push_back({ 0, 0, 0 });
            return palette;
        }

        // The palette's entry nearest each bin's middle, worked out once a bin.
        struct Nearest
        {
            std::vector<std::array<uint8_t, 3>> const& palette;
            std::vector<int16_t> cache = std::vector<int16_t>(BINS, -1);

            uint8_t operator()(uint8_t const* rgb)
            {
                uint32_t bin = BinOf(rgb);
                if (cache[bin] < 0)
                {
                    int best = 0;
                    long bestD = -1;
                    int mid[3] = { Channel(bin, 0) * 4 + 2, Channel(bin, 1) * 4 + 2, Channel(bin, 2) * 4 + 2 };
                    for (size_t i = 0; i < palette.size(); ++i)
                    {
                        long d = 0;
                        for (int c = 0; c < 3; ++c)
                        {
                            long e = long(palette[i][c]) - mid[c];
                            d += e * e;
                        }
                        if (bestD < 0 || d < bestD)
                        {
                            bestD = d;
                            best = int(i);
                        }
                    }
                    cache[bin] = int16_t(best);
                }
                return uint8_t(cache[bin]);
            }
        };

        std::vector<uint8_t> Half(std::vector<uint8_t> const& level, uint32_t w, uint32_t h, uint32_t nw, uint32_t nh)
        {
            std::vector<uint8_t> next(size_t(nw) * nh * 4);
            for (uint32_t y = 0; y < nh; ++y)
                for (uint32_t x = 0; x < nw; ++x)
                    for (int c = 0; c < 4; ++c)
                    {
                        uint32_t sum = 0;
                        for (uint32_t dy = 0; dy < 2; ++dy)
                            for (uint32_t dx = 0; dx < 2; ++dx)
                                sum += level[(size_t(std::min(y * 2 + dy, h - 1)) * w + std::min(x * 2 + dx, w - 1)) * 4 + c];
                        next[(size_t(y) * nw + x) * 4 + c] = uint8_t((sum + 2) / 4);
                    }
            return next;
        }
    }

    Bytes EncodePalette(Image const& image, bool alpha)
    {
        constexpr size_t HEADER = 148, PALETTE = 1024;
        Bytes out(HEADER + PALETTE, 0);
        std::memcpy(out.data(), "BLP2", 4);
        Put32(&out[4], 1);
        out[8] = 1;                                     // palettized
        out[9] = alpha ? 8 : 0;                         // bits of alpha
        out[10] = alpha ? 8 : 0;
        out[11] = 1;                                    // with smaller copies
        Put32(&out[12], image.width);
        Put32(&out[16], image.height);
        if (!image.width || !image.height)
            return Bytes{};

        Bins bins;
        for (size_t i = 0; i < image.rgba.size(); i += 4)
        {
            uint32_t bin = BinOf(&image.rgba[i]);
            ++bins.count[bin];
            for (int c = 0; c < 3; ++c)
                bins.sum[bin][c] += image.rgba[i + c];
        }
        auto palette = CutPalette(bins);
        for (size_t i = 0; i < palette.size(); ++i)
        {
            out[HEADER + i * 4] = palette[i][2];        // B
            out[HEADER + i * 4 + 1] = palette[i][1];    // G
            out[HEADER + i * 4 + 2] = palette[i][0];    // R
        }
        Nearest nearest{ palette };
        std::vector<uint8_t> level = image.rgba;
        uint32_t w = image.width, h = image.height;
        for (int mip = 0; mip < 16; ++mip)
        {
            size_t at = out.size(), n = size_t(w) * h;
            out.resize(at + n * (alpha ? 2 : 1));
            for (size_t i = 0; i < n; ++i)
            {
                out[at + i] = nearest(&level[i * 4]);
                if (alpha)
                    out[at + n + i] = level[i * 4 + 3];
            }
            Put32(&out[20 + mip * 4], uint32_t(at));
            Put32(&out[84 + mip * 4], uint32_t(out.size() - at));
            if (w == 1 && h == 1)
                break;
            uint32_t nw = std::max<uint32_t>(1, w / 2), nh = std::max<uint32_t>(1, h / 2);
            level = Half(level, w, h, nw, nh);
            w = nw;
            h = nh;
        }
        return out;
    }

    bool DecodeFull(Bytes blp, Image& image)
    {
        if (blp.size() >= 148 && std::memcmp(blp.data(), "BLP2", 4) == 0)
            for (int mip = 1; mip < 16; ++mip)
            {
                uint64_t offset = Get32(&blp[20 + mip * 4]), size = Get32(&blp[84 + mip * 4]);
                if (size && offset + size > blp.size())
                {
                    Put32(&blp[20 + mip * 4], 0);
                    Put32(&blp[84 + mip * 4], 0);
                }
            }
        return Skyborne::Decode(blp, image);
    }

    bool Header(Bytes const& blp, uint32_t& width, uint32_t& height, uint8_t& alphaDepth)
    {
        if (blp.size() < 148 || std::memcmp(blp.data(), "BLP2", 4) != 0)
            return false;
        width = Get32(&blp[12]);
        height = Get32(&blp[16]);
        alphaDepth = blp[9];
        return width && height;
    }
}
