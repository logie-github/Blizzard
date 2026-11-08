// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The character textures' patch for the game: a set of the user's own (Ralia's mod, or Alternate Female
 * Options; picked in the app's Game options, one at a time) made the game's, as
 * Data/<locale>/patch-<locale>-Z.MPQ.
 */

#ifndef MOD_RALIA_PATCH_H
#define MOD_RALIA_PATCH_H

#include <filesystem>
#include <functional>
#include <string>
#include <vector>

namespace Ralia
{
    namespace fs = std::filesystem;
    using Log = std::function<void(std::string const&)>;

    // A set of character textures: its name (the app's, for the log), whether it's women's alone, and
    // the races it leaves as they are besides the module's own (their textures' folders, lower case).
    struct Set
    {
        std::string name;
        bool femaleOnly = false;
        std::vector<std::string> leftOut;
    };

    // Makes the patch (again, when what it's made from changed) from [set]'s textures in [files] (a
    // folder of the game's paths: Character\<race>\<sex>\...), with [sources] (the module's
    // data/client/sources.txt: which file each of the allied races' colours takes). False when it
    // isn't in the game.
    bool UpdatePatch(Set const& set, fs::path const& files, fs::path const& sources, fs::path const& clientData, Log const& log);

    // Takes this module's patch out of the game.
    void RemovePatch(fs::path const& clientData, Log const& log);
}

#endif
