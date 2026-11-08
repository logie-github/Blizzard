// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef MOD_BRILL_HOME_PATCH_H
#define MOD_BRILL_HOME_PATCH_H

#include <filesystem>
#include <functional>
#include <string>

namespace BrillHome
{
    namespace fs = std::filesystem;

    // Makes Data/<locale>/patch-<locale>-V.MPQ in the client's Data folder [clientData] from the module's table
    // changes ([moduleData]/dbc: data/client/dbc), its files ([moduleData]/files) and Corn's model, skin and
    // coat ([moduleData]/corn) at the game's pug's paths, when the game or those changed since. True when the patch is in
    // place; [cornReady] when Corn is in it.
    bool UpdatePatch(fs::path const& moduleData, fs::path const& clientData, std::function<void(std::string const&)> const& log,
                     bool& cornReady);
    // Takes the patch out, if it's this module's.
    void RemovePatch(fs::path const& clientData, std::function<void(std::string const&)> const& log);
    // Takes the patch out of the game but keeps it beside it (Wrath Remix's realm hasn't the Brill home);
    // UpdatePatch puts it back first.
    void SetPatchAside(fs::path const& clientData, std::function<void(std::string const&)> const& log);
}

#endif
