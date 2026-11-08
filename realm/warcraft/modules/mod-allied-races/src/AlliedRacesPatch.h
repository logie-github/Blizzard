// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef MOD_ALLIED_RACES_PATCH_H
#define MOD_ALLIED_RACES_PATCH_H

#include <cstdint>
#include <filesystem>
#include <functional>
#include <string>
#include <vector>

namespace AlliedRaces
{
    namespace fs = std::filesystem;

    // Makes Data/patch-V.MPQ in the client's Data folder [clientData] from the module's files for
    // the game ([moduleData]: data/client: the tables' changes, the character screen, the icons,
    // the intros) and the races' models, textures and voices ([files]: made by tools/package.py
    // as the server was packaged, listed in alliedraces.files there), when the client, the
    // module or those files changed since. True when the patch is in place.
    bool UpdatePatch(fs::path const& moduleData, fs::path const& files, fs::path const& clientData,
                     std::function<void(std::string const&)> const& log);
    // Takes the patch out, if it's this module's.
    void RemovePatch(fs::path const& clientData, std::function<void(std::string const&)> const& log);

    // An MP3's length (its frames' samples over their rate) in milliseconds; 0 when it isn't one.
    uint32_t Mp3Milliseconds(std::vector<uint8_t> const& mp3);

    // A 3.3.5 camera model (an intro's flyby, Cameras\Flyby*.m2) made [ms] long: its sequences and
    // every key of its cameras' and bones' tracks at the same place in the new length (a key's
    // spline tangents are per segment, so the path is the same, faster or slower). False, [m2] as it
    // was, when it isn't one this reads.
    bool RetimeCamera(std::vector<uint8_t>& m2, uint32_t ms);

    // Takes the patch out of the game but keeps it, beside it (patch-V.MPQ.aside): for a realm without
    // the races (Wrath Remix's), so that going back to one with them needn't make it again.
    // UpdatePatch puts it back first.
    void SetPatchAside(fs::path const& clientData, std::function<void(std::string const&)> const& log);
}

#endif
