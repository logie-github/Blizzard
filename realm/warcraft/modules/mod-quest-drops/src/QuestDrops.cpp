// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Quest drops (mod-quest-drops), both realms (ctl.sh turns QuestDrops.Enable on once for each):
 *
 *  An item a quest asks the player to collect (a quest drop: the loot tables' QuestRequired) drops more
 *  often where its chance was low (the user: "ones that had ridiculously low drop rates, such as less
 *  than 25% chance push the drop rate to 75. For 10% or less set it to 50"; then, of Darkhound Blood at
 *  35%: "Quests like that need better drop rates", every chance under 75 to 75): 75 where it was under
 *  75, 50 where it was 10 or less, its own from 75 up. Each player who needs it sees it in the loot, as
 *  before; those who don't, don't.
 *
 *  An epic or better (purple and up) in a dungeon or raid, or from a rare spawn (rare or rare elite),
 *  rolls ten times its chance, 10 at least and 100 at most (the user: "Increase other drop rates by 10
 *  total so 1% drop rate in rare etc item becomes 10 but 100 stays at 100 but not less than 10"; then:
 *  "I only wanted quest items increased and stuff like purple and above for dungeons and rare spawns");
 *  a reference (the roll into another loot table) too where that table can give one. Every other drop
 *  (grey, white, green and blue items, cloth, world drops elsewhere, skinning, mining, herbs, fishing,
 *  pickpocketing, chests outside dungeons) keeps the game's own chance.
 *
 * Items in a loot group (one of the group drops, by their chances) are left as they are: a higher chance
 * for one would take from the group's others (24 of the game's 5725 quest drops are in one).
 */

#include "Chat.h"
#include "ChatCommand.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "LootMgr.h"
#include "Map.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include <algorithm>
#include <mutex>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace
{
    bool enabled = true;

    // An epic's chance in a dungeon or from a rare spawn, as the module rolls it: ten times its own, 10
    // at least, 100 at most.
    float RaisedEpic(float chance)
    {
        if (chance <= 0.0f)
            return chance;
        return std::min(100.0f, std::max(10.0f, chance * 10.0f));
    }

    // A quest drop's chance, as the module rolls it.
    float Raised(float chance)
    {
        if (chance <= 0.0f)
            return chance;
        if (chance <= 10.0f)
            return 50.0f;
        if (chance < 75.0f)
            return 75.0f;
        return chance;
    }

    // The reference loot tables that can give an epic or better (one of their own items, or through a
    // reference of theirs), read once from the world database.
    std::unordered_set<uint32> epicReferences;
    std::once_flag epicReferencesRead;

    void ReadEpicReferences()
    {
        std::unordered_map<uint32, std::vector<uint32>> nested;
        if (QueryResult result = WorldDatabase.Query("SELECT DISTINCT r.Entry FROM reference_loot_template r "
            "JOIN item_template i ON i.entry = r.Item WHERE r.Reference = 0 AND i.Quality >= {}", uint32(ITEM_QUALITY_EPIC)))
        {
            do
                epicReferences.insert((*result)[0].Get<uint32>());
            while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT Entry, Reference FROM reference_loot_template WHERE Reference > 0"))
        {
            do
                nested[(*result)[0].Get<uint32>()].push_back((*result)[1].Get<uint32>());
            while (result->NextRow());
        }
        for (bool more = true; more;)
        {
            more = false;
            for (auto const& [entry, references] : nested)
                if (!epicReferences.count(entry))
                    for (uint32 reference : references)
                        if (epicReferences.count(reference))
                        {
                            epicReferences.insert(entry);
                            more = true;
                            break;
                        }
        }
    }

    // An epic or better, or a roll into a table that can give one.
    bool IsEpic(LootStoreItem const* item)
    {
        if (item->reference > 0)
        {
            std::call_once(epicReferencesRead, ReadEpicReferences);
            return epicReferences.count(uint32(item->reference)) > 0;
        }
        ItemTemplate const* proto = sObjectMgr->GetItemTemplate(item->itemid);
        return proto && proto->Quality >= ITEM_QUALITY_EPIC;
    }

    // Where the loot is from: a dungeon or raid (the looter's map: a creature's or a chest's), or a
    // rare spawn.
    bool EpicPlace(Player const* player, Loot const& loot, LootStore const& store)
    {
        ObjectGuid source = loot.sourceWorldObjectGUID;
        bool creature = source.IsCreatureOrVehicle() && (&store == &LootTemplates_Creature || &store == &LootTemplates_Reference);
        bool chest = source.IsGameObject() && (&store == &LootTemplates_Gameobject || &store == &LootTemplates_Reference);
        if (!creature && !chest)
            return false;
        if (player && player->FindMap() && player->FindMap()->IsDungeon())
            return true;
        if (creature)
            if (CreatureTemplate const* cinfo = sObjectMgr->GetCreatureTemplate(source.GetEntry()))
                return cinfo->rank == CREATURE_ELITE_RARE || cinfo->rank == CREATURE_ELITE_RAREELITE;
        return false;
    }
}

class QuestDropsWorld : public WorldScript
{
public:
    QuestDropsWorld() : WorldScript("QuestDropsWorld", { WORLDHOOK_ON_AFTER_CONFIG_LOAD }) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        enabled = sConfigMgr->GetOption<bool>("QuestDrops.Enable", true);
    }
};

class QuestDropsLoot : public GlobalScript
{
public:
    QuestDropsLoot() : GlobalScript("QuestDropsLoot", { GLOBALHOOK_ON_ITEM_ROLL }) { }

    bool OnItemRoll(Player const* player, LootStoreItem const* item, float& chance, Loot& loot, LootStore const& store) override
    {
        if (!enabled || item->groupid)
            return true;
        if (item->needs_quest)
        {
            if (!item->reference)
                chance = Raised(chance);
        }
        else if (EpicPlace(player, loot, store) && IsEpic(item))
            chance = RaisedEpic(chance);
        return true;
    }
};

using namespace Acore::ChatCommands;

// Game masters' (CI's realm test): .questdrops chance <percent> says what a quest drop, an epic in a
// dungeon or from a rare, and any other drop of that chance roll here; .questdrops near <entry> takes the game master beside the nearest living creature of an
// entry (300 yards at most), within looting reach of it once it falls.
class QuestDropsCommands : public CommandScript
{
public:
    QuestDropsCommands() : CommandScript("QuestDropsCommands") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable questDropsTable =
        {
            { "chance", HandleChance, SEC_GAMEMASTER, Console::Yes },
            { "near",   HandleNear,   SEC_GAMEMASTER, Console::No },
        };
        static ChatCommandTable commandTable =
        {
            { "questdrops", questDropsTable },
        };
        return commandTable;
    }

    static bool HandleChance(ChatHandler* handler, float chance)
    {
        handler->PSendSysMessage("Quest drops: {:g} rolls {:g} for a quest item, {:g} for an epic in a dungeon or from a rare, {:g} for any other{}",
            chance, enabled ? Raised(chance) : chance, enabled ? RaisedEpic(chance) : chance, chance, enabled ? "" : " (off)");
        return true;
    }

    static bool HandleNear(ChatHandler* handler, uint32 entry)
    {
        Player* player = handler->GetSession()->GetPlayer();
        Creature* creature = player->FindNearestCreature(entry, 300.0f);
        if (!creature)
        {
            handler->PSendSysMessage("Quest drops near: no creature {} within 300 yards.", entry);
            return true;
        }
        Position at = creature->GetNearPosition(1.5f, 0.0f);
        player->NearTeleportTo(at.GetPositionX(), at.GetPositionY(), creature->GetPositionZ() + 0.5f, player->GetAngle(creature));
        handler->PSendSysMessage("Quest drops near: {} at {:.1f} yards.", entry, player->GetDistance(creature));
        return true;
    }
};

void AddQuestDropsScripts()
{
    new QuestDropsWorld();
    new QuestDropsLoot();
    new QuestDropsCommands();
}
