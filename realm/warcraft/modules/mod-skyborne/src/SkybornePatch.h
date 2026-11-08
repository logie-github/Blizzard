// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef MOD_SKYBORNE_PATCH_H
#define MOD_SKYBORNE_PATCH_H

#include <filesystem>
#include <functional>
#include <string>

namespace Skyborne
{
    constexpr char const* PATCH = "patch-Z.MPQ";
    constexpr char const* MARK = "patch-Z.MPQ.skyborne";

    // Makes the game's Data/patch-Z.MPQ: the Skyborne's tables, textures, character screen and
    // intro, from the client's own files and the module's (data/client), unless the one there was
    // made from the same (the stamp in patch-Z.MPQ.skyborne). A patch-Z.MPQ that isn't the
    // Skyborne's is left alone. [log] says what happened. False when there's no patch now.
    bool UpdatePatch(std::filesystem::path const& moduleData, std::filesystem::path const& clientData,
                     std::function<void(std::string const&)> const& log, bool femaleBodyPreview = false);

    // Takes the Skyborne's patch out of the game (only theirs).
    void RemovePatch(std::filesystem::path const& clientData, std::function<void(std::string const&)> const& log);
}

#endif
