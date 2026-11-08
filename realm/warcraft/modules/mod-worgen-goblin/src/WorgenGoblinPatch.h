// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef MOD_WORGEN_GOBLIN_PATCH_H
#define MOD_WORGEN_GOBLIN_PATCH_H

#include <filesystem>
#include <functional>
#include <string>
#include <vector>

namespace WorgenGoblin
{
    namespace fs = std::filesystem;

    // Makes Data/patch-U.MPQ in the client's Data folder [clientData] from the module's files for the
    // game ([moduleData]: data/client: the tables' changes, the character screen's script) and
    // mod-worgoblin's files ([files]: its models, textures, sounds, icons and texts, laid out by
    // tools/package.py as the server was packaged, listed in worgengoblin.files there), when the
    // client, the module or those files changed since. True when the patch is in place.
    //
    // With the starting areas ([zones]: their tables' rows, data/zones/client, and the package the app
    // installed, its client folder; both empty for none) it also has their maps, models, sounds and
    // pictures (only the files the game hasn't: none of the game's own is replaced), their rows in
    // the game's tables (after mod-worgoblin's) and their maps' lines in the minimap index.
    struct Zones
    {
        fs::path tables;
        fs::path package;
    };
    bool UpdatePatch(fs::path const& moduleData, fs::path const& files, fs::path const& clientData,
                     std::function<void(std::string const&)> const& log, Zones const& zones = {});
    // Takes the patch out, if it's this module's.
    void RemovePatch(fs::path const& clientData, std::function<void(std::string const&)> const& log);
    // Takes the patch out of the game but keeps it, beside it (patch-U.MPQ.aside): for a realm without
    // the races (Wrath Remix's). UpdatePatch puts it back first.
    void SetPatchAside(fs::path const& clientData, std::function<void(std::string const&)> const& log);

    // The statements of a file of SQL (data/server/worgen_goblin_dbc.sql: each ends with a ";" at the
    // end of a line; "--" lines are comments).
    std::vector<std::string> Statements(std::string const& sql);
}

#endif
