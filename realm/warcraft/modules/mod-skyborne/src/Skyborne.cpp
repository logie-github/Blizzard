// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Skyborne (mod-skyborne): WoW: Forever's elves of the wind as two races, the High Order
 * (Alliance, race 13) and the Windshapers (Horde, race 14). The world database has them from the
 * module's SQL (data/sql/db-world, tools/build_data.py); the game, from the patch this makes as
 * the world server starts (SkybornePatch.cpp) in the client WOW_CLIENT_DIR names (ctl.sh).
 */

#include "Config.h"
#include "Log.h"
#include "ScriptMgr.h"
#include "SkybornePatch.h"
#include <cstdlib>
#include <filesystem>

namespace fs = std::filesystem;

class SkyborneWorld : public WorldScript
{
public:
    SkyborneWorld() : WorldScript("SkyborneWorld", { WORLDHOOK_ON_BEFORE_WORLD_INITIALIZED }) { }

    // Before the world server says it's ready (the app starts the game on that line), and after
    // Wrath Remix's patch-Y (made as the custom tables load), whose rows this one carries: a patch
    // made after "ready" could still be being made, or the other realm's, as the game read it.
    void OnBeforeWorldInitialized() override
    {
        char const* client = std::getenv("WOW_CLIENT_DIR");
        if (!client || !*client)
            return;
        fs::path data = fs::path(client) / "Data";
        std::error_code error;
        if (!fs::is_directory(data, error))
            return;
        auto log = [](std::string const& line) { LOG_INFO("module", "Skyborne: {}", line); };
        if (!sConfigMgr->GetOption<bool>("Skyborne.ClientPatch", true))
        {
            Skyborne::RemovePatch(data, log);
            return;
        }
        fs::path module = fs::path(sConfigMgr->GetOption<std::string>("SourceDirectory", "")) / "modules" / "mod-skyborne" / "data" / "client";
        if (!fs::is_directory(module, error))
        {
            LOG_ERROR("module", "Skyborne: the module's files for the game aren't in {}", module.string());
            return;
        }
        fs::path clientDir = fs::path(client).lexically_normal();
        if (clientDir.filename().empty())
            clientDir = clientDir.parent_path();
        fs::path bodyFolder = sConfigMgr->GetOption<std::string>("BaseModel.Folder", "");
        if (bodyFolder.empty())
            bodyFolder = clientDir.parent_path() / "base-model";
        bool body = sConfigMgr->GetOption<bool>("BaseModel.Enable", true) && fs::is_regular_file(bodyFolder / "enabled", error);
        Skyborne::UpdatePatch(module, data, log, body);
    }
};

void AddSkyborneScripts()
{
    new SkyborneWorld();
}
