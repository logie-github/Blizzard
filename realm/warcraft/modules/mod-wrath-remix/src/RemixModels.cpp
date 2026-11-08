// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Eternus in her own shape (tools/models.py): the dragon the newer games give her (display 106055,
 * the bronze-and-infinite dragon of both Remixes), made a model 3.3.5 draws, fetched and converted
 * as the server is packaged into the module's data/models (the game's files are never in the
 * repository). When every file of it is there, ClientPatch.cpp puts it in the game's patch with its
 * CreatureModelData and CreatureDisplayInfo rows (wrath_remix_world_0029 gives the realm the same),
 * and Eternus takes it at the Bazaar, in her scenes and at the last hour, without her staff. When
 * it isn't (or WrathRemix.EternusDragon is 0), she keeps the infinite dragonspawn's shape.
 */

#include "WrathRemix.h"
#include "Config.h"
#include "CreatureData.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "ScriptMgr.h"
#include <filesystem>
#include <fstream>

using namespace WrathRemix;

namespace
{
    constexpr uint32 NPC_SCENE_ETERNUS = 770053;    // her scenes' (@ACT_ETERNUS)
    constexpr char const* MANIFEST = "eternus.files";
    constexpr char const* MODEL_FILE = "Creature/Eternus/Eternus.m2";

    // Her size in each of her parts: her model is as large as the game's own dragons
    // (Creature\Dragon\Dragon.mdx) at 1, as the newer games show her; smaller here, to stand at the
    // Bazaar's heart without covering it (about 12 yards from her head to her tail).
    struct Part { uint32 entry; float scale; };
    constexpr Part PARTS[] = {
        { NPC_ETERNUS, 0.4f },          // the Bazaar
        { NPC_SCENE_ETERNUS, 0.4f },    // her scenes
        { NPC_LAST_ETERNUS, 0.5f },     // the last hour
    };

    bool checked = false;
    bool inPatch = false;
    std::vector<std::string> files;
}

namespace WrathRemix
{
    std::string ModelsFolder()
    {
        std::string source = sConfigMgr->GetOption<std::string>("SourceDirectory", "");
        return (source.empty() ? std::string(".") : source) + "/modules/mod-wrath-remix/data/models";
    }

    // (tools/models.py writes its list of her files last, so a package whose fetch stopped half
    // way has none)
    std::vector<std::string> const& EternusShapeFiles()
    {
        if (checked)
            return files;
        checked = true;
        if (!sConfigMgr->GetOption<bool>("WrathRemix.EternusDragon", true, false))
            return files;
        std::filesystem::path const folder = ModelsFolder();
        std::ifstream list(folder / MANIFEST);
        if (!list)
        {
            LOG_INFO("module", "Wrath Remix: Eternus keeps the dragonspawn's shape (her own isn't in {})", folder.string());
            return files;
        }
        std::vector<std::string> found;
        bool model = false;
        for (std::string line; std::getline(list, line);)
        {
            if (!line.empty() && line.back() == '\r')
                line.pop_back();
            if (line.empty())
                continue;
            std::error_code error;
            if (line.find("..") != std::string::npos || !std::filesystem::is_regular_file(folder / line, error) ||
                std::filesystem::file_size(folder / line, error) == 0)
            {
                LOG_WARN("module", "Wrath Remix: Eternus keeps the dragonspawn's shape ({} of her own is missing)", line);
                return files;
            }
            model = model || line == MODEL_FILE;
            found.push_back(line);
        }
        if (model)
            files = std::move(found);
        return files;
    }

    void EternusShapeInPatch()
    {
        inPatch = true;
    }
}

// Her parts in her shape, as their templates are loaded (after the game's patch is written).
class RemixModelsDatabase : public DatabaseScript
{
public:
    RemixModelsDatabase() : DatabaseScript("RemixModelsDatabase", { DATABASEHOOK_ON_AFTER_DATABASE_LOAD_CREATURETEMPLATES }) { }

    void OnAfterDatabaseLoadCreatureTemplates(std::vector<CreatureTemplate*> templates) override
    {
        if (!Active() || !inPatch)
            return;
        for (Part const& part : PARTS)
            if (part.entry < templates.size() && templates[part.entry])
                templates[part.entry]->Models = { CreatureModel(DISPLAY_ETERNUS_DRAGON, part.scale, 1.0f) };
        LOG_INFO("module", "Wrath Remix: Eternus in her own shape (look {}, {} files)", DISPLAY_ETERNUS_DRAGON, files.size());
    }
};

// (a dragon doesn't carry a staff)
class RemixModelsWorld : public WorldScript
{
public:
    RemixModelsWorld() : WorldScript("RemixModelsWorld", { WORLDHOOK_ON_STARTUP }) { }

    void OnStartup() override
    {
        if (!Active() || !inPatch)
            return;
        for (Part const& part : PARTS)
        {
            int8 id = 1;
            if (EquipmentInfo const* info = sObjectMgr->GetEquipmentInfo(part.entry, id))
                for (uint32& item : const_cast<EquipmentInfo*>(info)->ItemEntry)
                    item = 0;
        }
    }
};

void AddRemixModelScripts()
{
    new RemixModelsDatabase();
    new RemixModelsWorld();
}
