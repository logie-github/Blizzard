// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The character textures' sets of the app's Game options (Ralia's mod, Alternate Female Options): the
 * one that's on made the game's (RaliaPatch.cpp), one at a time.
 *
 * The app keeps each set's textures (the Character folder of the zip picked on the phone) in
 * files/<set>/files, and files/<set>/enabled while its switch is on (files/ralia, files/alternate-female;
 * the app turns the other off). The world server makes the patch as the world database's own tables are
 * loaded (after the Worgen's and Goblins' and the allied races' patches are made, as the configuration is
 * read, and before the Skyborne's, as the world is made), and takes it out of the game while neither is
 * on. Ralia.Enable = 0 (mod_ralia.conf) keeps both out whatever the switches say.
 */

#include "Config.h"
#include "Log.h"
#include "RaliaPatch.h"
#include "ScriptMgr.h"

#include <cstdlib>
#include <filesystem>

namespace fs = std::filesystem;

namespace
{
    struct Choice
    {
        char const* folder;
        Ralia::Set set;
    };

    // (in this order, should both be on)
    Choice const SETS[] = {
        { "ralia", { "Ralia's mod", false } },
        { "alternate-female", { "Alternate Female Options", true, { "character\\gnome\\" } } },
    };
}

class RaliaWorld : public WorldScript
{
public:
    RaliaWorld() : WorldScript("RaliaWorld", { WORLDHOOK_ON_LOAD_CUSTOM_DATABASE_TABLE }) { }

    void OnLoadCustomDatabaseTable() override
    {
        char const* client = std::getenv("WOW_CLIENT_DIR");
        if (!client || !*client)
            return;
        fs::path clientDir = fs::path(client).lexically_normal();
        if (clientDir.filename().empty())
            clientDir = clientDir.parent_path();
        fs::path data = clientDir / "Data";
        std::error_code error;
        if (!fs::is_directory(data, error))
            return;
        // (the app's files: beside the game's folder)
        fs::path root = sConfigMgr->GetOption<std::string>("Ralia.Folder", "");
        if (root.empty())
            root = clientDir.parent_path();
        auto log = [](std::string const& line) { LOG_INFO("module", "Character textures: {}", line); };
        if (sConfigMgr->GetOption<bool>("Ralia.Enable", true))
            for (Choice const& choice : SETS)
                if (fs::exists(root / choice.folder / "enabled", error))
                {
                    fs::path sources = fs::path(sConfigMgr->GetOption<std::string>("SourceDirectory", "")) / "modules" / "mod-ralia" / "data" / "client" / "sources.txt";
                    Ralia::UpdatePatch(choice.set, root / choice.folder / "files", sources, data, log);
                    return;
                }
        Ralia::RemovePatch(data, log);
    }
};

void AddRaliaScripts()
{
    new RaliaWorld();
}
