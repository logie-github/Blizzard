// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix: the realm gate, its tables, Timerunners and their Bronze, the chapters' creature
 * levels, and the hooks that tie them to the game. The NPCs are in RemixNpcs.cpp.
 *
 * Everything here does nothing unless WrathRemix.Enable is on and this world server is the realm
 * WrathRemix.RealmID names: the same program runs the app's ChromieCraft realm, where Remix's
 * tables don't even exist.
 */

#include "WrathRemix.h"
#include "Battlefield.h"
#include "BattlefieldMgr.h"
#include "CellImpl.h"
#include "Chat.h"
#include "WorldPacket.h"
#include "ChatCommand.h"
#include "ConditionMgr.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureData.h"
#include "DatabaseEnv.h"
#include "DBCStores.h"
#include "Formulas.h"
#include "GameObject.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Group.h"
#include "Item.h"
#include "KillRewarder.h"
#include "Log.h"
#include "LootMgr.h"
#include "Mail.h"
#include "Map.h"
#include "MapMgr.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "SpellInfo.h"
#include "StringFormat.h"
#include "TemporarySummon.h"
#include "Trainer.h"
#include "World.h"
#include <algorithm>
#include <cctype>
#include <cmath>
#include <deque>
#include <map>
#include <mutex>

namespace WrathRemix
{
    namespace
    {
        bool enabled = false;
        bool bandsEnabled = true;
        bool followPlayer = true;   // WrathRemix.LevelBands.FollowPlayer: creatures near a Timerunner at their level
        bool announce = true;
        bool freeRiding = true;
        bool starterKit = true;
        bool autoLearn = true;
        bool maxWeaponSkill = true;
        uint32 squishHealth = 75;   // WrathRemix.Squish.*: banded creatures' share of their health and damage, in percent
        uint32 squishDamage = 75;
        bool solo = true;           // WrathRemix.Solo.*: dungeons and raids for however many are there
        uint32 soloDungeonDamage = 35, soloRaidDamage = 15, soloMaxBoost = 15;
        BronzeRates rates;

        std::map<std::pair<uint32, uint32>, LevelBand> bands;
        std::unordered_map<uint32, Bridge> bridges;
        std::unordered_map<uint32, Departure> departures;
        std::vector<Chapter> chapters;
        std::vector<Destination> destinations;
        std::vector<VendorList> vendorLists;
        std::unordered_map<uint32, uint32> questBronze;
        // What Eternus whispers as one of the quests she quietly changed is turned in (remix_quest_note)
        std::unordered_map<uint32, std::string> questNotes;
        std::unordered_map<uint8, std::vector<KitPiece>> kits;
        std::unordered_map<uint8, std::vector<ClassSpell>> classSpells;

        // The starter kit's version: a Timerunner who had an older one (or none) gets this one at login.
        constexpr uint8 KIT_VERSION = 1;

        // The weapon skills' proficiencies, by weapon subclass, for kit weapons a Timerunner's race
        // didn't start with (any of their class can learn them from a weapon master).
        uint32 ProficiencyFor(uint32 weaponSubclass)
        {
            switch (weaponSubclass)
            {
                case ITEM_SUBCLASS_WEAPON_AXE:      return 196;
                case ITEM_SUBCLASS_WEAPON_AXE2:     return 197;
                case ITEM_SUBCLASS_WEAPON_BOW:      return 264;
                case ITEM_SUBCLASS_WEAPON_GUN:      return 266;
                case ITEM_SUBCLASS_WEAPON_MACE:     return 198;
                case ITEM_SUBCLASS_WEAPON_MACE2:    return 199;
                case ITEM_SUBCLASS_WEAPON_POLEARM:  return 200;
                case ITEM_SUBCLASS_WEAPON_SWORD:    return 201;
                case ITEM_SUBCLASS_WEAPON_SWORD2:   return 202;
                case ITEM_SUBCLASS_WEAPON_STAFF:    return 227;
                case ITEM_SUBCLASS_WEAPON_FIST:     return 15590;
                case ITEM_SUBCLASS_WEAPON_DAGGER:   return 1180;
                case ITEM_SUBCLASS_WEAPON_THROWN:   return 2567;
                case ITEM_SUBCLASS_WEAPON_CROSSBOW: return 5011;
                case ITEM_SUBCLASS_WEAPON_WAND:     return 5009;
                default:                            return 0;
            }
        }

        std::mutex timerunnersLock;
        std::unordered_map<ObjectGuid::LowType, Timerunner> timerunners;

        // The chests each Timerunner has had their treasure's Bronze from, lately.
        std::mutex treasuresLock;
        std::unordered_map<ObjectGuid::LowType, std::deque<ObjectGuid>> treasures;

        // Riding, all of it, taught for free from a Timerunner's first moment (WrathRemix.FreeRiding):
        // any mount, flying ones in Northrend too, at any level.
        constexpr uint32 RIDING[] = {
            33388,  // Apprentice Riding
            33391,  // Journeyman Riding
            34090,  // Expert Riding
            34091,  // Artisan Riding
            54197,  // Cold Weather Flying
        };

        // The death knights' last quests of Acherus' story: after it, Moratari brings them to the Bazaar.
        constexpr uint32 QUEST_WHERE_KINGS_WALK = 13188;
        constexpr uint32 QUEST_WARCHIEFS_BLESSING = 13189;
    }

    bool Active() { return enabled; }
    bool SoloActive() { return enabled && solo; }
    float SoloDungeonDamage() { return soloDungeonDamage / 100.0f; }
    float SoloRaidDamage() { return soloRaidDamage / 100.0f; }
    float SoloMaxBoost() { return float(std::max<uint32>(1, soloMaxBoost)); }
    bool BandsActive() { return enabled && bandsEnabled; }
    BronzeRates const& Rates() { return rates; }
    bool Announce() { return announce; }

    void LoadConfig()
    {
        uint32 realmId = sConfigMgr->GetOption<uint32>("RealmID", 0, false);
        uint32 remixRealm = sConfigMgr->GetOption<uint32>("WrathRemix.RealmID", 2, false);
        enabled = sConfigMgr->GetOption<bool>("WrathRemix.Enable", false, false) && realmId == remixRealm;
        bandsEnabled = sConfigMgr->GetOption<bool>("WrathRemix.LevelBands.Enable", true, false);
        followPlayer = sConfigMgr->GetOption<bool>("WrathRemix.LevelBands.FollowPlayer", true, false);
        announce = sConfigMgr->GetOption<bool>("WrathRemix.Announce", true, false);
        freeRiding = sConfigMgr->GetOption<bool>("WrathRemix.FreeRiding", true, false);
        starterKit = sConfigMgr->GetOption<bool>("WrathRemix.StarterKit", true, false);
        autoLearn = sConfigMgr->GetOption<bool>("WrathRemix.AutoLearn", true, false);
        maxWeaponSkill = sConfigMgr->GetOption<bool>("WrathRemix.MaxWeaponSkill", true, false);
        squishHealth = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("WrathRemix.Squish.Health", 75, false), 1, 1000);
        squishDamage = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("WrathRemix.Squish.Damage", 75, false), 1, 1000);
        BronzeRates const defaults;
        rates.quest = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.Quest", defaults.quest, false);
        rates.kill = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.Kill", defaults.kill, false);
        rates.elite = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.Elite", defaults.elite, false);
        rates.rare = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.Rare", defaults.rare, false);
        rates.dungeonBoss = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.DungeonBoss", defaults.dungeonBoss, false);
        rates.raidBoss = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.RaidBoss", defaults.raidBoss, false);
        rates.treasure = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.Treasure", defaults.treasure, false);
        rates.achievementPoint = sConfigMgr->GetOption<uint32>("WrathRemix.Bronze.AchievementPoint", defaults.achievementPoint, false);
        solo = sConfigMgr->GetOption<bool>("WrathRemix.Solo.Enable", true, false);
        soloDungeonDamage = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("WrathRemix.Solo.DungeonDamage", 35, false), 1, 100);
        soloRaidDamage = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("WrathRemix.Solo.RaidDamage", 15, false), 1, 100);
        soloMaxBoost = std::clamp<uint32>(sConfigMgr->GetOption<uint32>("WrathRemix.Solo.MaxBoost", 15, false), 1, 50);
        if (enabled)
            LOG_INFO("module", "Wrath Remix: on (realm {})", realmId);
        else
            LOG_INFO("module", "Wrath Remix: off (realm {}; Wrath Remix runs on realm {} when turned on)", realmId, remixRealm);
    }

    void LoadData()
    {
        bands.clear();
        bridges.clear();
        departures.clear();
        chapters.clear();
        destinations.clear();
        vendorLists.clear();
        questBronze.clear();
        kits.clear();
        classSpells.clear();
        if (!enabled)
            return;

        if (QueryResult result = WorldDatabase.Query("SELECT `map`, `zone`, `original_min`, `original_max`, `band_min`, `band_max`, `chapter`, `name` FROM `remix_level_band`"))
        {
            do
            {
                Field* f = result->Fetch();
                bands[{ f[0].Get<uint32>(), f[1].Get<uint32>() }] = { f[2].Get<int32>(), f[3].Get<int32>(), f[4].Get<int32>(), f[5].Get<int32>(), f[6].Get<uint8>(), f[7].Get<std::string>() };
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped` FROM `remix_bridge`"))
        {
            do
            {
                Field* f = result->Fetch();
                Bridge b{ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<uint8>(), f[3].Get<uint32>(), f[4].Get<float>(), f[5].Get<float>(), f[6].Get<float>(), f[7].Get<float>(), f[8].Get<std::string>() };
                bridges[b.quest] = b;
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `quest`, `map`, `x`, `y`, `z`, `o` FROM `remix_departure`"))
        {
            do
            {
                Field* f = result->Fetch();
                Departure d{ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<float>(), f[3].Get<float>(), f[4].Get<float>(), f[5].Get<float>() };
                departures[d.quest] = d;
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `chapter`, `name`, `summary`, `level_min`, `level_max`, `alliance_map`, `alliance_x`, `alliance_y`, `alliance_z`, `horde_map`, `horde_x`, `horde_y`, `horde_z` FROM `remix_chapter` ORDER BY `chapter`"))
        {
            do
            {
                Field* f = result->Fetch();
                Chapter c;
                c.chapter = f[0].Get<uint8>();
                c.name = f[1].Get<std::string>();
                c.summary = f[2].Get<std::string>();
                c.levelMin = f[3].Get<uint8>();
                c.levelMax = f[4].Get<uint8>();
                for (int side = 0; side < 2; ++side)
                {
                    c.map[side] = f[5 + side * 4].Get<uint32>();
                    c.x[side] = f[6 + side * 4].Get<float>();
                    c.y[side] = f[7 + side * 4].Get<float>();
                    c.z[side] = f[8 + side * 4].Get<float>();
                }
                chapters.push_back(c);
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `id`, `name`, `side`, `min_level`, `map`, `x`, `y`, `z`, `o` FROM `remix_travel` ORDER BY `id`"))
        {
            do
            {
                Field* f = result->Fetch();
                destinations.push_back({ f[0].Get<uint16>(), f[1].Get<std::string>(), f[2].Get<uint8>(), f[3].Get<uint8>(), f[4].Get<uint32>(), f[5].Get<float>(), f[6].Get<float>(), f[7].Get<float>(), f[8].Get<float>() });
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `list`, `vendor`, `side`, `label` FROM `remix_vendor_list` ORDER BY `vendor`, `sort`"))
        {
            do
            {
                Field* f = result->Fetch();
                vendorLists.push_back({ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<uint8>(), f[3].Get<std::string>() });
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `quest`, `bronze` FROM `remix_quest_reward`"))
        {
            do
            {
                Field* f = result->Fetch();
                questBronze[f[0].Get<uint32>()] = f[1].Get<uint32>();
            } while (result->NextRow());
        }
        questNotes.clear();
        if (QueryResult result = WorldDatabase.Query("SELECT `quest`, `text` FROM `remix_quest_note`"))
        {
            do
            {
                Field* f = result->Fetch();
                questNotes[f[0].Get<uint32>()] = f[1].Get<std::string>();
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `class`, `item`, `count` FROM `remix_starter_kit` ORDER BY `class`, `item`"))
        {
            do
            {
                // (item templates load after this: GiveKit skips an item that doesn't exist)
                Field* f = result->Fetch();
                kits[f[0].Get<uint8>()].push_back({ f[1].Get<uint32>(), f[2].Get<uint8>() });
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `class`, `spell`, `level` FROM `remix_class_spell` ORDER BY `class`, `level`"))
        {
            do
            {
                Field* f = result->Fetch();
                classSpells[f[0].Get<uint8>()].push_back({ f[1].Get<uint32>(), f[2].Get<uint8>() });
            } while (result->NextRow());
        }
        LOG_INFO("module", "Wrath Remix: {} level bands, {} transitions, {} chapters, {} destinations, {} vendor lists, {} starter kits",
            bands.size(), bridges.size(), chapters.size(), destinations.size(), vendorLists.size(), kits.size());
        LoadScenes();
        LoadEnding();
        LoadLessons();
        LoadMoratari();
        LoadOutings();
    }

    LevelBand const* BandFor(uint32 map, uint32 zone)
    {
        auto it = bands.find({ map, zone });
        if (it == bands.end())
            it = bands.find({ map, 0 });
        return it == bands.end() ? nullptr : &it->second;
    }

    Bridge const* BridgeFor(uint32 quest)
    {
        auto it = bridges.find(quest);
        return it == bridges.end() ? nullptr : &it->second;
    }

    Departure const* DepartureFor(uint32 quest)
    {
        auto it = departures.find(quest);
        return it == departures.end() ? nullptr : &it->second;
    }

    std::vector<Chapter> const& Chapters() { return chapters; }

    Chapter const* ChapterFor(uint8 chapter)
    {
        for (Chapter const& c : chapters)
            if (c.chapter == chapter)
                return &c;
        return nullptr;
    }

    std::vector<Destination> const& Destinations() { return destinations; }

    Destination const* DestinationFor(uint16 id)
    {
        for (Destination const& d : destinations)
            if (d.id == id)
                return &d;
        return nullptr;
    }

    std::vector<VendorList> const& VendorLists() { return vendorLists; }

    // A quest's Bronze: the story's own amount (remix_quest_reward), or an ordinary quest's. After
    // the prologue, a story quest gives at least an ordinary quest's: a transition stands in for an
    // afternoon of them.
    std::string const* QuestNote(uint32 quest)
    {
        auto it = questNotes.find(quest);
        return it == questNotes.end() ? nullptr : &it->second;
    }

    uint32 QuestBronze(uint32 quest)
    {
        auto it = questBronze.find(quest);
        if (it == questBronze.end())
        {
            // (the game's repeatable quests a share of it, or they'd be Bronze to farm: a daily's a
            // fifth, one to do again at will a tenth; a weekly's whole)
            Quest const* q = sObjectMgr->GetQuestTemplate(quest);
            if (q && q->IsDaily())
                return rates.quest / 5;
            if (q && q->IsRepeatable() && !q->IsWeekly() && !q->IsMonthly())
                return rates.quest / 10;
            return rates.quest;
        }
        if (quest >= QUEST_OUT_OF_TIME && quest <= QUEST_TO_THE_FRONT_H)
            return it->second;
        return std::max(it->second, rates.quest);
    }

    int32 BandedLevel(LevelBand const& band, int32 level)
    {
        if (level <= band.bandMax)
            return level;
        double span = std::max(1, band.originalMax - band.originalMin);
        int32 banded = int32(std::lround(band.bandMin + (level - band.originalMin) * (band.bandMax - band.bandMin) / span));
        return std::clamp(banded, std::max(1, band.bandMin - 3), band.bandMax + 3);
    }

    uint8 ChapterForLevel(uint8 level)
    {
        uint8 found = 0;
        for (Chapter const& c : chapters)
            if (level >= c.levelMin)
                found = c.chapter;
        return found;
    }

    bool IsAlliance(Player* player) { return player->GetTeamId() == TEAM_ALLIANCE; }

    Timerunner Get(Player* player)
    {
        std::lock_guard<std::mutex> lock(timerunnersLock);
        auto it = timerunners.find(player->GetGUID().GetCounter());
        return it == timerunners.end() ? Timerunner() : it->second;
    }

    void Load(Player* player)
    {
        Timerunner t;
        if (QueryResult result = CharacterDatabase.Query("SELECT `bronze`, `bronze_earned`, `chapter`, `kit`, `back_map`, `back_x`, `back_y`, `back_z`, `back_o`, `intro` "
            "FROM `remix_character` WHERE `guid` = {}", player->GetGUID().GetCounter()))
        {
            Field* f = result->Fetch();
            t.bronze = f[0].Get<uint32>();
            t.earned = f[1].Get<uint32>();
            t.chapter = f[2].Get<uint8>();
            t.kit = f[3].Get<uint8>();
            t.backMap = f[4].Get<int32>();
            t.backX = f[5].Get<float>();
            t.backY = f[6].Get<float>();
            t.backZ = f[7].Get<float>();
            t.backO = f[8].Get<float>();
            t.intro = f[9].Get<uint8>() != 0;
        }
        else
            t.dirty = true;
        std::lock_guard<std::mutex> lock(timerunnersLock);
        timerunners[player->GetGUID().GetCounter()] = t;
    }

    // A Timerunner's row of remix_character.
    static std::string Row(ObjectGuid::LowType guid, Timerunner const& t)
    {
        return Acore::StringFormat("REPLACE INTO `remix_character` (`guid`, `bronze`, `bronze_earned`, `chapter`, `kit`, `back_map`, `back_x`, `back_y`, `back_z`, `back_o`, `intro`) "
            "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})",
            guid, t.bronze, t.earned, t.chapter, t.kit, t.backMap, t.backX, t.backY, t.backZ, t.backO, t.intro ? 1 : 0);
    }

    void Save(Player* player)
    {
        Timerunner t;
        {
            std::lock_guard<std::mutex> lock(timerunnersLock);
            auto it = timerunners.find(player->GetGUID().GetCounter());
            if (it == timerunners.end() || !it->second.dirty)
                return;
            it->second.dirty = false;
            t = it->second;
        }
        CharacterDatabase.Execute(Row(player->GetGUID().GetCounter(), t));
    }

    void Forget(Player* player)
    {
        {
            std::lock_guard<std::mutex> lock(timerunnersLock);
            timerunners.erase(player->GetGUID().GetCounter());
        }
        std::lock_guard<std::mutex> lock(treasuresLock);
        treasures.erase(player->GetGUID().GetCounter());
    }

    uint32 Bronze(Player* player)
    {
        return player->GetItemCount(ITEM_BRONZE);
    }

    // Bronze into the currency tab (the "You receive" line for quests, bosses and rares; a
    // common kill's single Bronze adds up quietly). What can't be stored is owed and paid at login.
    static bool StoreBronze(Player* player, uint32 amount, bool show)
    {
        ItemPosCountVec dest;
        if (player->CanStoreNewItem(NULL_BAG, NULL_SLOT, dest, ITEM_BRONZE, amount) != EQUIP_ERR_OK)
            return false;
        if (Item* item = player->StoreNewItem(dest, ITEM_BRONZE, true))
            player->SendNewItem(item, amount, true, false, false, show);
        return true;
    }

    void AddBronze(Player* player, uint32 amount, bool show)
    {
        if (!amount)
            return;
        bool stored = StoreBronze(player, amount, show);
        std::lock_guard<std::mutex> lock(timerunnersLock);
        Timerunner& t = timerunners[player->GetGUID().GetCounter()];
        t.earned += amount;
        if (!stored)
            t.bronze += amount;
        t.dirty = true;
    }

    // Bronze the realm kept for a Timerunner (before Bronze was an item, or when it couldn't be
    // stored), into their currency tab: the character (with the Bronze it became) and its record
    // (no longer owed) saved in one transaction, so a crash can't lose it between the two.
    static void PayOwedBronze(Player* player)
    {
        uint32 owed = Get(player).bronze;
        if (!owed || !StoreBronze(player, owed, true))
            return;
        Timerunner t;
        {
            std::lock_guard<std::mutex> lock(timerunnersLock);
            Timerunner& r = timerunners[player->GetGUID().GetCounter()];
            r.bronze = r.bronze > owed ? r.bronze - owed : 0;
            r.dirty = false;    // (written below: the save hook's own write would go first)
            t = r;
        }
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        player->SaveToDB(trans, false, false);
        trans->Append(Row(player->GetGUID().GetCounter(), t));
        CharacterDatabase.CommitTransaction(trans);
    }

    void SetChapter(Player* player, uint8 chapter)
    {
        {
            std::lock_guard<std::mutex> lock(timerunnersLock);
            Timerunner& t = timerunners[player->GetGUID().GetCounter()];
            if (chapter <= t.chapter)
                return;
            t.chapter = chapter;
            t.dirty = true;
        }
        Save(player);
        if (Chapter const* c = ChapterFor(chapter))
            ChatHandler(player->GetSession()).PSendSysMessage("|cff8fd3ffChapter {}: {}.|r {}", uint32(c->chapter), c->name, c->summary);
    }

    void SetKit(Player* player, uint8 version)
    {
        {
            std::lock_guard<std::mutex> lock(timerunnersLock);
            Timerunner& t = timerunners[player->GetGUID().GetCounter()];
            t.kit = version;
            t.dirty = true;
        }
        Save(player);
    }

    void SetWayBack(Player* player, int32 map, float x, float y, float z, float o)
    {
        {
            std::lock_guard<std::mutex> lock(timerunnersLock);
            Timerunner& t = timerunners[player->GetGUID().GetCounter()];
            t.backMap = map;
            t.backX = x;
            t.backY = y;
            t.backZ = z;
            t.backO = o;
            t.dirty = true;
        }
        Save(player);
    }

    void SetIntroSeen(Player* player)
    {
        {
            std::lock_guard<std::mutex> lock(timerunnersLock);
            Timerunner& t = timerunners[player->GetGUID().GetCounter()];
            t.intro = true;
            t.dirty = true;
        }
        Save(player);
    }

    void Record(Player* player, char const* what, uint32 entry, int32 amount)
    {
        CharacterDatabase.Execute("INSERT INTO `remix_log` (`guid`, `what`, `entry`, `amount`, `area`) VALUES ({}, '{}', {}, {}, {})",
            player->GetGUID().GetCounter(), what, entry, amount, player->GetAreaId());
    }

    // (from the dark: the curtain down now, with the place's name on it, lifted once the game has
    // settled there)
    void TeleportSoon(Player* player, uint32 map, float x, float y, float z, float o)
    {
        JourneyFromTheDark(player, PlaceName(map, x, y, z), map, x, y);
        player->m_Events.AddEventAtOffset([player, map, x, y, z, o]()
        {
            if (player->IsInWorld() && player->IsAlive())
                player->TeleportTo(map, x, y, z, o);
            else
                LiftTheCurtain(player);
        }, 1500ms);
    }

    // A player's companion: summoned by them and on their side (Moratari beside a Timerunner, the
    // last hour's three take their faction). At their level, and never squished.
    static Player* CompanionOwner(Creature* creature)
    {
        TempSummon* summon = creature->ToTempSummon();
        if (!summon || !summon->GetSummonerGUID().IsPlayer())
            return nullptr;
        Player* player = ObjectAccessor::GetPlayer(*creature, summon->GetSummonerGUID());
        return player && creature->GetFaction() == player->GetFaction() ? player : nullptr;
    }

    // The creature behind a blow or a heal when its level was brought down (by a band, or to a
    // Timerunner's): a creature, or the totem or guardian of one (never a player's pet, guardian,
    // totem or companion).
    static Creature* BandedSource(Unit* unit)
    {
        if (!unit)
            return nullptr;
        if (Unit* owner = unit->GetOwner())
        {
            if (owner->IsPlayer())
                return nullptr;
            unit = owner;
        }
        Creature* creature = unit->ToCreature();
        if (!creature || creature->IsPet() || CompanionOwner(creature))
            return nullptr;
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        if (!info || creature->GetLevel() >= std::min(info->minlevel, info->maxlevel))
            return nullptr;
        return creature;
    }

    // How much of its spells' power a banded creature keeps: its damage at its level now over its
    // damage at its own level (creature_classlevelstats), as its melee already does.
    static float BandFactor(Creature* creature)
    {
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        uint8 original = uint8((info->minlevel + info->maxlevel) / 2);
        CreatureBaseStats const* now = sObjectMgr->GetCreatureBaseStats(creature->GetLevel(), info->unit_class);
        CreatureBaseStats const* was = sObjectMgr->GetCreatureBaseStats(original, info->unit_class);
        uint32 expansion = std::min<uint32>(info->expansion, MAX_EXPANSIONS - 1);
        if (!now || !was || was->BaseDamage[expansion] <= 0.0f)
            return 1.0f;
        return std::clamp(now->BaseDamage[expansion] / was->BaseDamage[expansion], 0.01f, 1.0f);
    }

    // Whether a creature's spell is its caster's level's already: the core scales the ones that
    // say so to the caster's level (SPELL_ATTR0_SCALES_WITH_CREATURE_LEVEL, SpellEffectInfo::
    // CalcValue, unless they grow by points per level), and a weapon strike is made of its level's
    // weapon damage. The others keep their own level's power.
    static bool AtCastersLevel(SpellInfo const* spell)
    {
        if (!spell)
            return false;
        if (spell->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE) || spell->HasEffect(SPELL_EFFECT_WEAPON_DAMAGE_NOSCHOOL) ||
            spell->HasEffect(SPELL_EFFECT_NORMALIZED_WEAPON_DMG) || spell->HasEffect(SPELL_EFFECT_WEAPON_PERCENT_DAMAGE))
            return true;
        if (!spell->SpellLevel || !spell->HasAttribute(SPELL_ATTR0_SCALES_WITH_CREATURE_LEVEL))
            return false;
        for (SpellEffectInfo const& effect : spell->GetEffects())
            if (effect.RealPointsPerLevel != 0.0f)
                return false;
        return true;
    }

    // A banded creature's blow or heal: its spells' at the share their level keeps (BandFactor:
    // those not at its level already), and all of it at the realm's squish (WrathRemix.Squish.*,
    // in percent: [squish]).
    template<typename T>
    static void Scale(T& amount, Unit* source, uint32 squish, bool spell, SpellInfo const* spellInfo = nullptr)
    {
        if (!BandsActive() || !amount)
            return;
        if (Creature* creature = BandedSource(source))
            amount = T(std::max<double>(1.0, std::round(amount * (spell && !AtCastersLevel(spellInfo) ? BandFactor(creature) : 1.0f) * squish / 100.0)));
    }

    bool MarkHealTick(HealTick& tick, Unit* target, Unit* caster, uint32 const& amount, SpellInfo const* spell)
    {
        tick = HealTick{ target, caster, &amount };
        return spell && (spell->HasAura(SPELL_AURA_PERIODIC_HEAL) || spell->HasAura(SPELL_AURA_OBS_MOD_HEALTH)) &&
            !spell->HasAura(SPELL_AURA_PERIODIC_DAMAGE) && !spell->HasAura(SPELL_AURA_PERIODIC_DAMAGE_PERCENT) &&
            !spell->HasAura(SPELL_AURA_PERIODIC_LEECH);
    }

    void HealUnits(HealTick& tick, Unit*& target, Unit*& healer, uint32 const& amount)
    {
        bool periodic = tick.amount == &amount && tick.target == target && tick.caster == healer;
        tick = HealTick();
        if (!periodic)
            std::swap(target, healer);
    }

    // Creatures at a Timerunner's level, as Legion Remix has them (WrathRemix.LevelBands.FollowPlayer):
    // in the banded zones a hostile or neutral creature takes the level of the real player nearest
    // it, in a Wrath dungeon or raid the level of its highest real player; world bosses up to 3
    // above, a dungeon's or raid's bosses up to 2, nothing above its own level. Where no real player
    // is near (the realm's bots load the world around them too), the band's. A creature takes the
    // level as it appears, and again from the level pass when a Timerunner levels or another comes.
    namespace
    {
        constexpr float FOLLOW_REACH = 100.0f;      // the level pass's reach around each real player
        constexpr uint32 AREA_WINTERGRASP = 4197;   // banded outside its battle only
        thread_local uint8 forcedLevel = 0;         // set while the level pass brings a creature to a level
    }

    static bool FollowActive() { return BandsActive() && followPlayer; }

    // One of Wrath's dungeons or raids (heroic too): banded, or of the expansion.
    static bool RemixInstance(Map* map)
    {
        return map->IsDungeon() && (BandFor(map->GetId(), 0) ||
            (map->GetEntry() && map->GetEntry()->Expansion() == EXPANSION_WRATH_OF_THE_LICH_KING));
    }

    static bool AtWar(uint32 zone)
    {
        if (zone != AREA_WINTERGRASP)
            return false;
        Battlefield* battlefield = sBattlefieldMgr->GetBattlefieldToZoneId(zone);
        return battlefield && battlefield->IsWarTime();
    }

    // The real player whose level a creature takes: in a dungeon or raid its highest, out in the
    // world the nearest within [reach]. Never a bot.
    static Player* Followed(WorldObject* object, Map* map, bool instance, float reach)
    {
        Player* found = nullptr;
        float nearest = reach;
        for (MapReference const& ref : map->GetPlayers())
        {
            Player* player = ref.GetSource();
            if (!player || IsBot(player))
                continue;
            if (instance)
            {
                if (!found || player->GetLevel() > found->GetLevel())
                    found = player;
            }
            else if (float distance = object->GetExactDist2d(player); distance < nearest)
            {
                nearest = distance;
                found = player;
            }
        }
        return found;
    }

    // Whether a creature takes [player]'s level: one they could fight, hostile or neutral to them;
    // not anyone's pet, guardian, totem or companion (nor one a player summoned on their side), not
    // a town's people (vendors, trainers, quest givers: anyone offering something), a civilian, a
    // critter or an unseen trigger.
    static bool Follows(Creature* creature, CreatureTemplate const* info, Player* player)
    {
        if (creature->IsPet() || creature->IsTotem() || creature->IsTrigger() || creature->IsCivilian() || info->type == CREATURE_TYPE_CRITTER)
            return false;
        if (creature->HasUnitTypeMask(UNIT_MASK_MINION) || creature->GetCharmerOrOwnerGUID() || creature->IsControlledByPlayer())
            return false;
        if (creature->GetNpcFlags() & ~UNIT_NPC_FLAG_SPELLCLICK)
            return false;
        return !creature->IsFriendlyTo(player);
    }

    static uint32 RankBonus(Creature* creature, CreatureTemplate const* info, bool instance)
    {
        if (instance)
            return creature->IsDungeonBoss() || info->rank == CREATURE_ELITE_WORLDBOSS ? 2 : 0;
        return info->rank == CREATURE_ELITE_WORLDBOSS ? 3 : 0;
    }

    // The levels a creature may have under [player]: theirs (and its rank's bonus) when that's
    // below its own, else its own up to that.
    static void FollowRange(Creature* creature, CreatureTemplate const* info, Player* player, bool instance, uint32& from, uint32& to)
    {
        uint32 cap = std::max<uint32>(1, player->GetLevel() + RankBonus(creature, info, instance));
        uint32 low = std::min(info->minlevel, info->maxlevel), high = std::max(info->minlevel, info->maxlevel);
        from = std::min(cap, low);
        to = std::min(cap, high);
    }

    // A creature's level as it appears or comes back (OnBeforeCreatureSelectLevel, [level] its
    // template's roll). A ship's or a zeppelin's crew is made where the ship's map has it before
    // it's put aboard (Transport.cpp): theirs waits until it is (OnCreatureAddWorld).
    static uint8 SpawnLevel(Creature* creature, CreatureTemplate const* info, uint8 level)
    {
        Map* map = creature->GetMap();
        if (!map)
            return level;
        if (CreatureData const* data = creature->GetCreatureData(); data && data->mapid != map->GetId() && !creature->GetTransport())
            return level;
        bool instance = map->IsDungeon();
        LevelBand const* band = nullptr;
        if (instance)
        {
            if (!RemixInstance(map))
                return level;
            // (heroic and the raids have no band: as the game has them without a Timerunner)
            if (!map->IsHeroic() && !map->IsRaid())
                band = BandFor(map->GetId(), 0);
        }
        else
        {
            uint32 zone = map->GetZoneId(creature->GetPhaseMask(), creature->GetPositionX(), creature->GetPositionY(), creature->GetPositionZ());
            band = BandFor(map->GetId(), zone);
            if (!band || AtWar(zone))
                return level;
        }
        if (FollowActive())
            if (Player* player = Followed(creature, map, instance, std::max(FOLLOW_REACH, map->GetVisibilityRange())))
                if (Follows(creature, info, player))
                {
                    uint32 from, to;
                    FollowRange(creature, info, player, instance, from, to);
                    return uint8(std::clamp<uint32>(level, from, to));
                }
        return band ? uint8(BandedLevel(*band, level)) : level;
    }

    // A creature in the world brought to another level ([level]; 0: its own roll, placed again):
    // the health, mana, armour and damage of it, as Creature::SelectLevel and UpdateEntry give
    // them, and the squish; at full health, as it was.
    static void Relevel(Creature* creature, uint8 level)
    {
        forcedLevel = level;
        creature->SelectLevel();
        forcedLevel = 0;
        CreatureTemplate const* info = creature->GetCreatureTemplate();
        if (CreatureBaseStats const* stats = sObjectMgr->GetCreatureBaseStats(creature->GetLevel(), info->unit_class))
            creature->SetStatFlatModifier(UNIT_MOD_ARMOR, BASE_VALUE, stats->GenerateArmor(info));
        creature->UpdateAllStats();
        creature->SetFullHealth();
    }

    // The level pass's candidates around a real player: alive, out of combat and whole (its health
    // its level's: none a script or an aura changed), nobody's, and not a player's summons (the
    // opening's, a scene's, a quest's: theirs keep what they were given).
    struct LevelCandidates
    {
        LevelCandidates(WorldObject const* source, float range) : _source(source), _range(range) { }
        bool operator()(Creature* creature) const
        {
            if (!creature->IsAlive() || creature->IsInCombat() || creature->IsInEvadeMode() || creature->IsPet() ||
                creature->HasUnitTypeMask(UNIT_MASK_MINION) || creature->GetCharmerOrOwnerGUID() || creature->IsControlledByPlayer())
                return false;
            if (creature->GetHealth() != creature->GetMaxHealth() || creature->GetMaxHealth() != creature->GetCreateHealth())
                return false;
            if (TempSummon const* summon = creature->ToTempSummon(); summon && summon->GetSummonerGUID().IsPlayer())
                return false;
            return _source->IsWithinDistInMap(creature, _range);
        }
        WorldObject const* _source;
        float _range;
    };

    // Every second and a half for each real player: the creatures within 100 yards that take a real
    // player's level (Follows) and aren't at it are brought to it (one fighting keeps its level to
    // the end). Cheap enough for a phone: a few cells, and most there are at it already.
    static void LevelPass(Player* player)
    {
        Map* map = player->GetMap();
        bool instance = map->IsDungeon();
        if (instance ? !RemixInstance(map) : !BandFor(map->GetId(), player->GetZoneId()))
            return;
        std::list<Creature*> creatures;
        LevelCandidates check(player, FOLLOW_REACH);
        Acore::CreatureListSearcher<LevelCandidates> searcher(player, creatures, check);
        Cell::VisitObjects(player, searcher, FOLLOW_REACH);
        for (Creature* creature : creatures)
        {
            CreatureTemplate const* info = creature->GetCreatureTemplate();
            Player* followed = info ? Followed(creature, map, instance, FOLLOW_REACH * 2.0f) : nullptr;
            if (!followed || !Follows(creature, info, followed))
                continue;
            uint32 from, to;
            FollowRange(creature, info, followed, instance, from, to);
            if (creature->GetLevel() >= from && creature->GetLevel() <= to)
                continue;
            // (out in the world, where its own zone is banded: near a border, it may not be)
            if (!instance)
            {
                uint32 zone = map->GetZoneId(creature->GetPhaseMask(), creature->GetPositionX(), creature->GetPositionY(), creature->GetPositionZ());
                if (!BandFor(map->GetId(), zone) || AtWar(zone))
                    continue;
            }
            Relevel(creature, uint8(urand(from, to)));
        }
    }

    static void LevelPassSoon(Player* player)
    {
        player->m_Events.AddEventAtOffset([player]()
        {
            // (not on a flight: what's flown over is brought to them as they land near it)
            if (FollowActive() && player->IsInWorld() && !player->IsBeingTeleported() && !player->IsInFlight())
                LevelPass(player);
            LevelPassSoon(player);
        }, 1500ms);
    }

    // The last kill the game rewarded (KillRewarder), on this map's thread: one it didn't (no one
    // tapped it, or not enough of its health was taken by players) may still be a companion's.
    static thread_local ObjectGuid rewardedKill;

    // A kill's Bronze for a real player: one that gives experience (summoned creatures give none: a
    // quest's or a boss's adds aren't for farming).
    static void KillBronze(Player* player, Creature* killed)
    {
        if (killed->IsSummon() || Acore::XP::Gain(player, killed) == 0)
            return;
        BronzeRates const& r = Rates();
        CreatureTemplate const* info = killed->GetCreatureTemplate();
        uint32 amount = r.kill;
        bool show = false;
        if (killed->IsDungeonBoss() || (info && info->rank == CREATURE_ELITE_WORLDBOSS))
        {
            amount = killed->GetMap()->IsRaid() ? r.raidBoss : r.dungeonBoss;
            show = true;
        }
        else if (info && (info->rank == CREATURE_ELITE_RARE || info->rank == CREATURE_ELITE_RAREELITE))
        {
            amount = r.rare;
            show = true;
        }
        else if (info && info->rank == CREATURE_ELITE_ELITE)
            amount = r.elite;
        AddBronze(player, amount, show);
    }

    static void TeachRiding(Player* player)
    {
        if (!freeRiding)
            return;
        for (uint32 spell : RIDING)
            if (!player->HasSpell(spell))
                player->learnSpell(spell);
    }

    // Everything the Timerunner's class trainer would teach them at their level, free, as Legion
    // Remix does, and the abilities class quests teach (remix_class_spell): a Timerunner starts at
    // 10 and moves fast, without the trips to a capital. The trainers are the Bazaar's instructors'
    // (the capitals' lists). Ranks need the rank before, so it goes round until nothing is left.
    static uint32 LearnClassSpells(Player* player)
    {
        if (!autoLearn)
            return 0;
        std::vector<Trainer::Trainer*> trainers;
        for (uint32 entry = NPC_INSTRUCTOR_FIRST; entry <= NPC_INSTRUCTOR_LAST; ++entry)
            if (Trainer::Trainer* trainer = sObjectMgr->GetTrainer(entry))
                if (trainer->GetTrainerType() == Trainer::Type::Class && trainer->IsTrainerValidForPlayer(player))
                    trainers.push_back(trainer);
        auto quested = classSpells.find(player->getClass());
        uint32 learned = 0;
        for (int round = 0; round < 10; ++round)
        {
            uint32 before = learned;
            for (Trainer::Trainer* trainer : trainers)
            {
                for (Trainer::Spell const& spell : trainer->GetSpells())
                {
                    if (!trainer->CanTeachSpell(player, &spell))
                        continue;
                    // as a trainer teaches it (Trainer::TeachSpell), without the trainer or the gold
                    if (!spell.IsCastable())
                        player->learnSpell(spell.SpellId, false);
                    else if (sScriptMgr->OnPlayerCanLearnSpell(player, spell.SpellId))
                        player->CastSpell(player, spell.SpellId, true);
                    ++learned;
                }
            }
            if (quested != classSpells.end())
            {
                for (ClassSpell const& c : quested->second)
                {
                    if (player->GetLevel() < c.level || player->HasSpell(c.spell))
                        continue;
                    player->learnSpell(c.spell, false);
                    ++learned;
                }
            }
            if (learned == before)
                break;
        }
        return learned;
    }

    // Weapon and defense skills at their level's maximum: a character made at 10 has them at 1
    // otherwise (and misses most of what it swings at).
    static void MaxWeaponSkills(Player* player)
    {
        if (maxWeaponSkill)
            player->UpdateSkillsToMaxSkillsForLevel();
    }

    // One piece of the kit: put on in place of what the Timerunner started in (white or grey gear,
    // item level 5 or lower), into the bags when they've something better on, by mail when the
    // bags are full.
    static void GivePiece(Player* player, ItemTemplate const* proto, MailDraft& mail, CharacterDatabaseTransaction trans, bool& mailed)
    {
        uint8 slot = player->FindEquipSlot(proto, NULL_SLOT, true);
        if (slot != NULL_SLOT)
        {
            Item* current = player->GetItemByPos(INVENTORY_SLOT_BAG_0, slot);
            uint16 dest;
            if ((!current || (current->GetTemplate()->ItemLevel <= 5 && current->GetTemplate()->Quality <= ITEM_QUALITY_NORMAL)) &&
                player->CanEquipNewItem(slot, dest, proto->ItemId, true) == EQUIP_ERR_OK)
            {
                if (current)
                    player->DestroyItem(INVENTORY_SLOT_BAG_0, slot, true);
                if (player->CanEquipNewItem(slot, dest, proto->ItemId, false) == EQUIP_ERR_OK)
                {
                    player->EquipNewItem(dest, proto->ItemId, true);
                    player->AutoUnequipOffhandIfNeed();
                    return;
                }
            }
        }
        ItemPosCountVec dest;
        if (player->CanStoreNewItem(NULL_BAG, NULL_SLOT, dest, proto->ItemId, 1) == EQUIP_ERR_OK)
        {
            if (Item* item = player->StoreNewItem(dest, proto->ItemId, true))
                player->SendNewItem(item, 1, true, false);
            return;
        }
        if (Item* item = Item::CreateItem(proto->ItemId, 1, player))
        {
            item->SaveToDB(trans);
            mail.AddItem(item);
            mailed = true;
        }
    }

    // The class's starter kit (remix_starter_kit), once per kit version. Death knights have
    // Acherus' gear instead.
    static void GiveKit(Player* player)
    {
        // (a ghost can't put anything on: it waits for the Timerunner to be alive)
        if (!starterKit || player->getClass() == CLASS_DEATH_KNIGHT || !player->IsAlive() || Get(player).kit >= KIT_VERSION)
            return;
        auto kit = kits.find(player->getClass());
        if (kit == kits.end())
            return;
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        MailDraft mail("Moratari's provisions", "Your bags were full, so the rest of your provisions came this way. Do try to keep up.");
        bool mailed = false;
        for (KitPiece const& piece : kit->second)
        {
            ItemTemplate const* proto = sObjectMgr->GetItemTemplate(piece.item);
            if (!proto)
                continue;
            if (proto->Class == ITEM_CLASS_WEAPON)
                if (uint32 proficiency = ProficiencyFor(proto->SubClass); proficiency && !player->HasSpell(proficiency) &&
                    player->IsSpellFitByClassAndRace(proficiency))
                    player->learnSpell(proficiency, false);
            for (uint8 n = 0; n < piece.count; ++n)
                GivePiece(player, proto, mail, trans, mailed);
        }
        if (mailed)
            mail.SendMailTo(trans, MailReceiver(player), MailSender(MAIL_NORMAL, 0), MAIL_CHECK_MASK_COPIED);
        CharacterDatabase.CommitTransaction(trans);
        SetKit(player, KIT_VERSION);
        ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari:|r You will want something better than that. Here: gear that grows with you, and a few things to carry you through your first battles.");
    }

    bool IsBot(Player* player)
    {
        return player->GetSession()->GetRemoteAddress() == "headless";
    }

    // A bot in a group with a player (one following a Timerunner) goes where they go.
    static bool WithPlayer(Player* bot)
    {
        if (Group* group = bot->GetGroup())
            for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                if (Player* member = ref->GetSource(); member && !IsBot(member))
                    return true;
        return false;
    }

    // Where every character is made (the Infinite Bazaar; the Caverns of Time until build 64): a
    // bot there.
    static char const* AtTheStart(Player* player, uint32 area)
    {
        if (player->GetMapId() == MAP_KALIMDOR && area == AREA_CAVERNS_OF_TIME)
            return "the Caverns of Time";
        if (player->GetMapId() == MAP_NORTHREND && player->GetExactDist2d(BAZAAR_X, BAZAAR_Y) < 120.0f)
            return "the Infinite Bazaar";
        return nullptr;
    }

    // A bot where every character is made (and where the playerbots' travels can bring one back)
    // goes to the start of the chapter its level belongs to, its side's, and makes its home there:
    // the prologue is the Timerunners'.
    static void SendBotAway(Player* bot, char const* from)
    {
        if (WithPlayer(bot))
            return;
        Chapter const* c = ChapterFor(std::max<uint8>(1, ChapterForLevel(bot->GetLevel())));
        if (!c)
            return;
        int side = IsAlliance(bot) ? 0 : 1;
        WorldLocation home(c->map[side], c->x[side], c->y[side], c->z[side], bot->GetOrientation());
        bot->SetHomebind(home, sMapMgr->GetAreaId(PHASEMASK_NORMAL, home));
        bot->TeleportTo(home);
        LOG_INFO("module", "Wrath Remix: bot {} (level {}) sent from {} to Chapter {}", bot->GetName(), uint32(bot->GetLevel()), from, uint32(c->chapter));
    }

    // A Timerunner's training, kept up as they arrive and as they level: their class's abilities,
    // their weapon skills, free riding, and (once) the starter kit. Not the realm's playerbots:
    // they look after their own spells and gear.
    static void Train(Player* player)
    {
        if (IsBot(player))
            return;
        PayOwedBronze(player);
        TeachRiding(player);
        if (uint32 learned = LearnClassSpells(player))
            ChatHandler(player->GetSession()).PSendSysMessage("|cff8fd3ffWrath Remix|r: you learn {} {} of your class.", learned,
                learned == 1 ? "ability" : "abilities");
        GiveKit(player);
        GiveHourglass(player);
        MaxWeaponSkills(player);
    }

    // Everything the Bronze vendors sell for anyone, at any level (wrath_remix_world_0022): their
    // wares' requirements taken off in memory too as the realm starts, whatever order the SQL was
    // last applied in (0005, applied again, puts a quest reward's level back on it). The client
    // asks the realm for an item's requirements, so its tooltips say the same.
    static void FreeWares()
    {
        constexpr uint32 WARES_FIRST = 770301, WARES_LAST = 770399;   // the lists' vendor templates
        uint32 freed = 0;
        for (uint32 list = WARES_FIRST; list <= WARES_LAST; ++list)
        {
            VendorItemData const* wares = sObjectMgr->GetNpcVendorItemList(list);
            if (!wares)
                continue;
            for (VendorItem const* ware : wares->m_items)
            {
                ItemTemplate* item = ware ? const_cast<ItemTemplate*>(sObjectMgr->GetItemTemplate(ware->item)) : nullptr;
                if (!item)
                    continue;
                if (item->RequiredLevel || item->RequiredSkill || item->RequiredSpell || item->RequiredHonorRank ||
                    item->RequiredCityRank || item->RequiredReputationFaction)
                    ++freed;
                item->RequiredLevel = 0;
                item->RequiredSkill = 0;
                item->RequiredSkillRank = 0;
                item->RequiredSpell = 0;
                item->RequiredHonorRank = 0;
                item->RequiredCityRank = 0;
                item->RequiredReputationFaction = 0;
                item->RequiredReputationRank = 0;
            }
        }
        LOG_INFO("module", "Wrath Remix: the Bronze vendors' wares for anyone ({} had a requirement still)", freed);
    }

    // A Timerunner made before build 64 and still in the prologue was made in the Caverns of Time,
    // where the prologue was: they wake at the Bazaar, where it is now, with their home there.
    static void WakeAtTheBazaar(Player* player)
    {
        if (IsBot(player) || Get(player).chapter || player->GetMapId() != MAP_KALIMDOR || player->GetAreaId() != AREA_CAVERNS_OF_TIME)
            return;
        WorldLocation bazaar(MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O);
        player->SetHomebind(bazaar, sMapMgr->GetAreaId(PHASEMASK_NORMAL, bazaar));
        player->TeleportTo(bazaar);
    }
}

using namespace WrathRemix;

class WrathRemixWorld : public WorldScript
{
public:
    WrathRemixWorld() : WorldScript("WrathRemixWorld", { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_LOAD_CUSTOM_DATABASE_TABLE, WORLDHOOK_ON_STARTUP }) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        LoadConfig();
    }

    // The game's patch with the tables (on ChromieCraft's realm too: that's where the patch comes out
    // of the game), before any module's startup: the Skyborne's patch (mod-skyborne, patch-Z.MPQ,
    // read after this one) is made at the startup from the game's tables as the patches before it
    // have them, the clothes of Remix's looks (patch-<locale>-Y.MPQ, ClientPatch.cpp) included.
    void OnLoadCustomDatabaseTable() override
    {
        LoadData();
        UpdateClientPatch();
    }

    void OnStartup() override
    {
        // What earlier versions kept of characters deleted since: the core gives a deleted
        // character's guid to the next one made after a restart, which would take over its
        // Timerunner's chapter, Bronze and starter kit.
        if (Active())
        {
            CharacterDatabase.DirectExecute("DELETE r FROM remix_character r LEFT JOIN characters c ON c.guid = r.guid WHERE c.guid IS NULL");
            CharacterDatabase.DirectExecute("DELETE l FROM remix_log l LEFT JOIN characters c ON c.guid = l.guid WHERE c.guid IS NULL");
            FreeWares();
        }
    }
};

class WrathRemixPlayer : public PlayerScript
{
public:
    WrathRemixPlayer() : PlayerScript("WrathRemixPlayer", {
        PLAYERHOOK_ON_FIRST_LOGIN,
        PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_LOGOUT,
        PLAYERHOOK_ON_SAVE,
        PLAYERHOOK_ON_LEVEL_CHANGED,
        PLAYERHOOK_ON_PLAYER_COMPLETE_QUEST,
        PLAYERHOOK_ON_REWARD_KILL_REWARDER,
        PLAYERHOOK_ON_BEFORE_LOOT_MONEY,
        PLAYERHOOK_ON_LOOT_ITEM,
        PLAYERHOOK_ON_ACHI_COMPLETE,
        PLAYERHOOK_ON_PLAYER_RESURRECT,
        PLAYERHOOK_ON_UPDATE_AREA,
        PLAYERHOOK_ON_PLAYER_QUEST_ACCEPT,
        PLAYERHOOK_ON_BEFORE_QUEST_COMPLETE,
        PLAYERHOOK_ON_DELETE_FROM_DB,
    }) { }

    // A character deleted for good takes its Timerunner's record and journal with it (in the
    // core's own transaction): its guid goes to the next character made after a restart.
    void OnPlayerDeleteFromDB(CharacterDatabaseTransaction trans, uint32 guid) override
    {
        if (!Active())
            return;
        trans->Append("DELETE FROM remix_character WHERE guid = {}", guid);
        trans->Append("DELETE FROM remix_log WHERE guid = {}", guid);
    }

    // Who a Timerunner sees changes with the story (visibility conditions in the world SQL:
    // Sylvanas and Alleria arrive, Eternus leaves the Bazaar, her loyalists wait on the cliffs):
    // looked at again a moment after one of the story's quests moves on.
    static bool InTheStory(uint32 quest)
    {
        return (quest >= 77000 && quest <= 77999) || quest == QUEST_MYSTERY_OF_THE_INFINITE;
    }

    static void RefreshSightSoon(Player* player)
    {
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid]()
        {
            if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
                p->UpdateObjectVisibility();
        }, 500ms);
    }

    // Some of the story's quests take the Timerunner where they're going as they're taken
    // (remix_departure): back to the Bazaar to face Eternus, out to the Wrathgate's cliffs.
    void OnPlayerQuestAccept(Player* player, Quest const* quest) override
    {
        if (!Active() || IsBot(player))
            return;
        uint32 id = quest->GetQuestId();
        Departure const* departure = InTheStory(id) ? DepartureFor(id) : nullptr;
        if (departure)
            TeleportSoon(player, departure->map, departure->x, departure->y, departure->z, departure->o);
        if (InTheStory(id))
            RefreshSightSoon(player);
        // (a quest that takes them somewhere plays its scene there, a moment after they arrive)
        if (departure)
            SceneWhenThere(player->GetGUID(), id, departure->map, departure->x, departure->y, 30);
        else
            SceneWhenThere(player->GetGUID(), id, player->GetMapId(), player->GetPositionX(), player->GetPositionY(), 1);
    }

    // The quest's scene once the Timerunner has arrived at [x, y] on [map] (a far journey can keep
    // them on a loading screen for a while), a check a second, [tries] times.
    static void SceneWhenThere(ObjectGuid guid, uint32 quest, uint32 map, float x, float y, uint32 tries)
    {
        Player* player = ObjectAccessor::FindPlayer(guid);
        if (!player || !tries)
            return;
        player->m_Events.AddEventAtOffset([guid, quest, map, x, y, tries]()
        {
            Player* p = ObjectAccessor::FindPlayer(guid);
            if (!p)
                return;
            if (p->IsInWorld() && !p->IsBeingTeleported() && p->GetMapId() == map && p->GetExactDist2d(x, y) < 40.0f)
            {
                if (quest == QUEST_LAST_HOUR)
                    BeginLastHour(p);
                else
                    ScenesForQuest(p, quest, SCENE_ON_ACCEPT);
            }
            else
                SceneWhenThere(guid, quest, map, x, y, tries - 1);
        }, tries == 30 ? 2500ms : 1000ms);
    }

    bool OnPlayerBeforeQuestComplete(Player* player, uint32 questId) override
    {
        if (Active() && !IsBot(player) && InTheStory(questId))
            RefreshSightSoon(player);
        return true;
    }

    void OnPlayerFirstLogin(Player* player) override
    {
        if (!Active())
            return;
        ChatHandler handler(player->GetSession());
        if (player->getClass() == CLASS_DEATH_KNIGHT)
            handler.SendSysMessage("|cff8fd3ffWrath Remix.|r Your own story comes first, death knight. When the Ebon Blade lets you go, Moratari will find you.");
        else
            handler.SendSysMessage("|cff8fd3ffWrath Remix.|r Welcome, Timerunner. Moratari is waiting for you.");
    }

    void OnPlayerLogin(Player* player) override
    {
        if (!Active())
            return;
        Load(player);
        // Creatures near a Timerunner at their level (not near the realm's bots: they keep the bands).
        if (!IsBot(player))
            LevelPassSoon(player);
        // A moment after arriving, once the Timerunner is in the world: learning casts, and the
        // kit puts gear on.
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid]()
        {
            if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
            {
                Train(p);
                WakeAtTheBazaar(p);
                // WRM-207's scene is played as it's taken; one cut short (a logout) counts as seen.
                if (p->GetQuestStatus(QUEST_WEIGHT_OF_TIME) == QUEST_STATUS_INCOMPLETE)
                    p->KilledMonsterCredit(NPC_TURN_CREDIT);
                // Back to Your Own Time done, and still here (the way home failed, or the realm
                // stopped on the way): home now.
                if (!IsBot(p) && p->GetQuestRewardStatus(QUEST_BACK_TO_YOUR_OWN_TIME))
                    SendHome(p);
            }
        }, 2s);
        Timerunner const t = Get(player);
        if (Announce())
        {
            uint8 chapter = t.chapter ? std::max(t.chapter, ChapterForLevel(player->GetLevel())) : 0;
            Chapter const* c = ChapterFor(chapter);
            ChatHandler(player->GetSession()).PSendSysMessage("|cff8fd3ffWrath Remix|r: Timerunner, {} Bronze. {}", Bronze(player) + t.bronze,
                c ? Acore::StringFormat("Chapter {}: {}.", uint32(c->chapter), c->name) : std::string("The prologue."));
        }
        Save(player);
    }

    void OnPlayerLogout(Player* player) override
    {
        if (!Active())
            return;
        Save(player);
        Forget(player);
    }

    void OnPlayerSave(Player* player) override
    {
        if (Active())
            Save(player);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        if (!Active())
            return;
        Train(player);
    }

    // A Timerunner who arrived dead gets the starter kit once they're back on their feet.
    void OnPlayerResurrect(Player* player, float /*restorePercent*/, bool& /*applySickness*/) override
    {
        if (!Active() || IsBot(player))
            return;
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid]()
        {
            if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld() && p->IsAlive())
                GiveKit(p);
        }, 1s);
    }

    // (as a character enters the world too) A moment later: not in the middle of a teleport.
    void OnPlayerUpdateArea(Player* player, uint32 /*oldArea*/, uint32 newArea) override
    {
        if (!Active() || !IsBot(player) || !AtTheStart(player, newArea))
            return;
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid]()
        {
            if (Player* bot = ObjectAccessor::FindPlayer(guid); bot && bot->IsInWorld() && !bot->IsBeingTeleported())
                if (char const* from = AtTheStart(bot, bot->GetAreaId()))
                    SendBotAway(bot, from);
        }, 1s);
    }

    // Once, as a quest is turned in (the end of Player::RewardQuest). Not the experience hook: the
    // core works out a quest's experience for its details and reward windows too, so Bronze, a
    // chapter or a bridge's journey would come with every window opened.
    void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
    {
        if (!Active())
            return;
        uint32 id = quest->GetQuestId();
        // (not the realm's bots': Bronze is no use to them)
        if (!IsBot(player))
            AddBronze(player, QuestBronze(id), true);
        if (InTheStory(id) && !IsBot(player))
            RefreshSightSoon(player);
        ScenesForQuest(player, id, SCENE_ON_REWARD);

        // Until the turn, Eternus is folding the war her way: a quest she quietly changed (its
        // turn-in text, wrath_remix_world_0019) brings her word on it, a moment later.
        if (std::string const* note = QuestNote(id); note && !IsBot(player) && !player->GetQuestRewardStatus(QUEST_WEIGHT_OF_TIME))
        {
            ObjectGuid guid = player->GetGUID();
            std::string text = *note;
            player->m_Events.AddEventAtOffset([guid, text]()
            {
                if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
                {
                    WorldPacket data;
                    ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_WHISPER, LANG_UNIVERSAL, ObjectGuid::Empty, p->GetGUID(), text, 0, "Eternus", p->GetName());
                    p->SendDirectMessage(&data);
                }
            }, 3s);
        }

        if (Bridge const* bridge = BridgeFor(id))
        {
            Record(player, "bridge", id, 0);
            if (bridge->chapter)
                SetChapter(player, bridge->chapter);
            if (bridge->map != 0xFFFF)
                TeleportSoon(player, bridge->map, bridge->x, bridge->y, bridge->z, bridge->o);
        }
        else if (id == QUEST_BAZAAR_KEEPERS)
        {
            // The hearthstone remembers the Bazaar.
            if (Destination const* bazaar = DestinationFor(TRAVEL_BAZAAR))
                player->SetHomebind(WorldLocation(bazaar->map, bazaar->x, bazaar->y, bazaar->z, bazaar->o), player->GetAreaId());
        }

        // Death knights, done with Acherus: to the Bazaar, at their level's chapter.
        if (id == QUEST_WHERE_KINGS_WALK || id == QUEST_WARCHIEFS_BLESSING)
        {
            if (Destination const* bazaar = DestinationFor(TRAVEL_BAZAAR))
            {
                ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari whispers:|r There you are. Your king will keep. Come, the Bazaar is this way.");
                SetChapter(player, ChapterForLevel(player->GetLevel()));
                GiveHourglass(player);
                TeleportSoon(player, bazaar->map, bazaar->x, bazaar->y, bazaar->z, bazaar->o);
            }
        }
    }

    // Treasure: the first thing taken from a chest out in the world, a strongbox, a cache
    // (WrathRemix.Bronze.Treasure), once a chest; not gathering, nor a quest's objects. One a bot
    // of a Timerunner's group opens is theirs (a bot's Bronze would be lost).
    static void Treasure(Player* player, ObjectGuid source)
    {
        if (!Active() || !source.IsGameObject() || !Rates().treasure)
            return;
        GameObject* chest = player->GetMap()->GetGameObject(source);
        if (!chest || chest->GetGoType() != GAMEOBJECT_TYPE_CHEST)
            return;
        std::string name = chest->GetGOInfo()->name;
        std::transform(name.begin(), name.end(), name.begin(), [](unsigned char c) { return std::tolower(c); });
        bool treasure = false;
        for (char const* word : { "chest", "strongbox", "coffer", "cache", "treasure", "footlocker", "lockbox", "trunk" })
            treasure = treasure || name.find(word) != std::string::npos;
        if (!treasure)
            return;
        if (!IsBot(player))
            TreasureFor(player, source);
        else if (Group* group = player->GetGroup())
            for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                if (Player* member = ref->GetSource(); member && !IsBot(member) && member->IsAtGroupRewardDistance(chest))
                    TreasureFor(member, source);
    }

    static void TreasureFor(Player* player, ObjectGuid source)
    {
        {
            std::lock_guard<std::mutex> lock(treasuresLock);
            std::deque<ObjectGuid>& seen = treasures[player->GetGUID().GetCounter()];
            if (std::find(seen.begin(), seen.end(), source) != seen.end())
                return;
            seen.push_back(source);
            if (seen.size() > 64)
                seen.pop_front();
        }
        AddBronze(player, Rates().treasure, true);
    }

    void OnPlayerLootItem(Player* player, Item* /*item*/, uint32 /*count*/, ObjectGuid source) override
    {
        Treasure(player, source);
    }

    // Achievements: their points' worth (WrathRemix.Bronze.AchievementPoint a point).
    void OnPlayerAchievementComplete(Player* player, AchievementEntry const* achievement) override
    {
        if (Active() && achievement && achievement->points && !IsBot(player))
            AddBronze(player, achievement->points * Rates().achievementPoint, true);
    }

    // A banded creature's gold is its template's, for its own level: it drops its new level's share.
    void OnPlayerBeforeLootMoney(Player* player, Loot* loot) override
    {
        if (loot)
            Treasure(player, loot->sourceWorldObjectGUID);
        if (!BandsActive() || !loot || !loot->gold || !loot->sourceWorldObjectGUID.IsCreature())
            return;
        if (Creature* creature = BandedSource(ObjectAccessor::GetCreature(*player, loot->sourceWorldObjectGUID)))
            loot->gold = std::max<uint32>(1, uint32(std::lround(loot->gold * BandFactor(creature))));
    }

    // A kill's Bronze, to each real player the game rewards it to (KillRewarder: the one who
    // tapped it, or their group's, near enough), whoever struck the last blow: they, their pet,
    // totem or guardian, Moratari, a bot of their group. Not to the realm's bots.
    void OnPlayerRewardKillRewarder(Player* player, KillRewarder* rewarder, bool /*isDungeon*/, float& /*rate*/) override
    {
        Creature* killed = rewarder && rewarder->GetVictim() ? rewarder->GetVictim()->ToCreature() : nullptr;
        if (!Active() || !killed)
            return;
        rewardedKill = killed->GetGUID();
        if (!IsBot(player))
            KillBronze(player, killed);
    }
};

// Northrend's creatures at a Timerunner's level, or their chapter's, and their spells to match.
class WrathRemixLevels : public AllCreatureScript
{
public:
    WrathRemixLevels() : AllCreatureScript("WrathRemixLevels") { }

    void OnBeforeCreatureSelectLevel(CreatureTemplate const* info, Creature* creature, uint8& level) override
    {
        // (the level pass's)
        if (forcedLevel)
        {
            level = forcedLevel;
            return;
        }
        // (Moratari beside a Timerunner is their level)
        if (uint8 companion = CompanionLevel(); companion && creature && creature->GetEntry() == NPC_MORATARI)
        {
            level = companion;
            return;
        }
        if (!BandsActive() || !creature || !info || creature->IsPet())
            return;
        level = SpawnLevel(creature, info, level);
    }

    // Two SelectLevel can't get right as they're made: a ship's or a zeppelin's crew, now aboard
    // (their level again, where the ship is); and a banded creature's guardian, whose health
    // Guardian::InitStatsForLevel made again after the squish.
    void OnCreatureAddWorld(Creature* creature) override
    {
        if (!BandsActive() || !creature || creature->IsPet())
            return;
        if (creature->GetTransport() && !creature->IsSummon())
        {
            if (CreatureData const* data = creature->GetCreatureData(); data && data->mapid != creature->GetMapId())
                Relevel(creature, 0);
            return;
        }
        if (squishHealth == 100 || !creature->HasUnitTypeMask(UNIT_MASK_GUARDIAN) || !BandedSource(creature))
            return;
        creature->SetCreateHealth(std::max<uint32>(1, uint32(std::lround(creature->GetCreateHealth() * double(squishHealth) / 100.0))));
        creature->SetStatFlatModifier(UNIT_MOD_HEALTH, BASE_VALUE,
            std::max(1.0f, std::round(creature->GetFlatModifierValue(UNIT_MOD_HEALTH, BASE_VALUE) * float(squishHealth) / 100.0f)));
        creature->SetFullHealth();
    }

    // The squish: a banded creature at its share of its new level's health (WrathRemix.Squish.Health).
    void OnCreatureSelectLevel(CreatureTemplate const* info, Creature* creature) override
    {
        if (!BandsActive() || squishHealth == 100 || !info || !creature || creature->IsPet() || creature->IsControlledByPlayer() || CompanionLevel())
            return;
        if (creature->GetLevel() >= std::min(info->minlevel, info->maxlevel))
            return;
        uint32 health = std::max<uint32>(1, uint32(std::lround(creature->GetCreateHealth() * double(squishHealth) / 100.0)));
        creature->SetCreateHealth(health);
        creature->SetMaxHealth(health);
        creature->SetHealth(health);
        creature->SetStatFlatModifier(UNIT_MOD_HEALTH, BASE_VALUE, float(health));
        creature->ResetPlayerDamageReq();
    }
};

namespace
{
    thread_local HealTick damageHealTick;   // (WrathRemixDamage's: see HealUnits)
}

class WrathRemixDamage : public UnitScript
{
public:
    WrathRemixDamage() : UnitScript("WrathRemixDamage", true, {
        UNITHOOK_MODIFY_SPELL_DAMAGE_TAKEN,
        UNITHOOK_MODIFY_PERIODIC_DAMAGE_AURAS_TICK,
        UNITHOOK_MODIFY_MELEE_DAMAGE,
        UNITHOOK_MODIFY_HEAL_RECEIVED,
        UNITHOOK_ON_UNIT_DEATH,
    }) { }

    void ModifySpellDamageTaken(Unit* /*target*/, Unit* attacker, int32& damage, SpellInfo const* spellInfo) override
    {
        if (damage > 0)
            Scale(damage, attacker, squishDamage, true, spellInfo);
    }

    // (a heal over time's tick comes this way first: it's scaled once, as a heal)
    void ModifyPeriodicDamageAurasTick(Unit* target, Unit* attacker, uint32& damage, SpellInfo const* spellInfo) override
    {
        if (!MarkHealTick(damageHealTick, target, attacker, damage, spellInfo))
            Scale(damage, attacker, squishDamage, true, spellInfo);
    }

    // (its melee is its new level's already: only the squish)
    void ModifyMeleeDamage(Unit* /*target*/, Unit* attacker, uint32& damage) override
    {
        Scale(damage, attacker, squishDamage, false);
    }

    // (its heals restore squished health: they're squished as health is; a leech's heal is the
    // share of its blow, already scaled)
    void ModifyHealReceived(Unit* target, Unit* healer, uint32& heal, SpellInfo const* spellInfo) override
    {
        HealUnits(damageHealTick, target, healer, heal);
        if (spellInfo && (spellInfo->HasAura(SPELL_AURA_PERIODIC_LEECH) || spellInfo->HasEffect(SPELL_EFFECT_HEALTH_LEECH)))
            return;
        Scale(heal, healer, squishHealth, true, spellInfo);
    }

    // A kill the game gave no one (not tapped, or too little of it taken by players) that a
    // Timerunner's companion made: its Bronze is theirs.
    void OnUnitDeath(Unit* unit, Unit* killer) override
    {
        Creature* killed = unit ? unit->ToCreature() : nullptr;
        if (!Active() || !killed)
            return;
        bool rewarded = rewardedKill == killed->GetGUID();
        rewardedKill.Clear();
        Creature* companion = killer && !rewarded ? killer->ToCreature() : nullptr;
        if (Player* player = companion ? CompanionOwner(companion) : nullptr; player && !IsBot(player) && player->IsAtGroupRewardDistance(killed))
            KillBronze(player, killed);
    }
};

using namespace Acore::ChatCommands;

class WrathRemixCommands : public CommandScript
{
public:
    WrathRemixCommands() : CommandScript("WrathRemixCommands") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable bronzeTable =
        {
            { "add", HandleBronzeAdd, SEC_GAMEMASTER, Console::No },
        };
        static ChatCommandTable remixTable =
        {
            { "",       HandleStatus, SEC_PLAYER,     Console::No },
            { "bronze", bronzeTable },
            { "band",   HandleBand,   SEC_GAMEMASTER, Console::No },
            { "guid",   HandleGuid,   SEC_GAMEMASTER, Console::No },
            { "goguid", HandleGoGuid, SEC_GAMEMASTER, Console::No },
            { "sees",   HandleSees,   SEC_GAMEMASTER, Console::No },
            { "return", HandleReturn, SEC_GAMEMASTER, Console::No },
            { "solo",   HandleSolo,   SEC_GAMEMASTER, Console::No },
            { "hourglass", HandleHourglass, SEC_GAMEMASTER, Console::No },
            { "ground", HandleGround, SEC_GAMEMASTER, Console::No },
            { "intro",  HandleIntro,  SEC_GAMEMASTER, Console::No },
            { "companion", HandleCompanion, SEC_GAMEMASTER, Console::No },
        };
        static ChatCommandTable commandTable =
        {
            { "remix", remixTable },
        };
        return commandTable;
    }

    // .remix: whether Remix runs here, and the Timerunner's Bronze and chapter.
    static bool HandleStatus(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        if (!Active())
        {
            handler->SendSysMessage("Wrath Remix: off on this realm.");
            return true;
        }
        Timerunner const t = Get(player);
        uint8 chapter = t.chapter ? std::max(t.chapter, ChapterForLevel(player->GetLevel())) : 0;
        Chapter const* c = ChapterFor(chapter);
        handler->PSendSysMessage("Wrath Remix: Timerunner {}, level {}, {} Bronze ({} earned), chapter {} ({}).",
            player->GetName(), uint32(player->GetLevel()), Bronze(player) + t.bronze, t.earned, uint32(chapter), c ? c->name : "the prologue");
        return true;
    }

    // .remix bronze add N (game masters).
    static bool HandleBronzeAdd(ChatHandler* handler, uint32 amount)
    {
        if (!Active())
            return false;
        Player* player = handler->getSelectedPlayerOrSelf();
        AddBronze(player, amount, true);
        Save(player);
        return true;
    }

    // .remix return (game masters): back to the Bazaar as after the Lich King's fall, for CI's tests
    // (the raid itself can't be played there).
    static bool HandleReturn(ChatHandler* handler)
    {
        if (!Active())
            return false;
        ReturnToBazaarSoon(handler->GetSession()->GetPlayer(), 2s);
        return true;
    }

    // .remix solo (game masters): what the solo scaling makes of the instance you're in.
    static bool HandleSolo(ChatHandler* handler)
    {
        if (!Active())
            return false;
        handler->SendSysMessage(SoloReport(handler->GetSession()->GetPlayer()));
        return true;
    }

    // .remix companion (game masters): Moratari beside them, or why not.
    static bool HandleCompanion(ChatHandler* handler)
    {
        if (!Active())
            return false;
        handler->SendSysMessage(CompanionReport(handler->GetSession()->GetPlayer()));
        return true;
    }

    // .remix hourglass (game masters): where Moratari's Hourglass is, and where it leads back to.
    static bool HandleHourglass(ChatHandler* handler)
    {
        if (!Active())
            return false;
        handler->SendSysMessage(HourglassReport(handler->GetSession()->GetPlayer()));
        return true;
    }

    // .remix ground [RADIUS] [STEP] (game masters): the floor's height on a grid around the
    // character, a row a line (west to east, north to south; "-" where there is none within 30
    // yards), for placing things where they stand on it.
    // .remix intro [skip]: the opening, for a game master (again, if it was seen); skip ends it now.
    static bool HandleIntro(ChatHandler* handler, Optional<std::string> what)
    {
        Player* player = handler->GetSession()->GetPlayer();
        if (!Active())
            return false;
        if (what && *what == "skip")
        {
            SkipIntro(player);
            handler->SendSysMessage("Wrath Remix intro: skipped.");
        }
        else if (what && *what == "status")
            handler->PSendSysMessage("Wrath Remix intro: {}, {}, {}, at {:.1f} {:.1f} {:.1f} on map {}; {}.", InIntro(player) ? "in it" : "not in it",
                player->IsAlive() ? "alive" : "dead", player->IsSitState() ? "seated" : "standing", player->GetPositionX(), player->GetPositionY(),
                player->GetPositionZ(), player->GetMapId(), CurtainStatus(player));
        else if (what && *what == "fall")
        {
            // What the core does to whoever falls under the world (MovementHandler.cpp).
            player->SetPlayerFlag(PLAYER_FLAGS_IS_OUT_OF_BOUNDS);
            player->KillPlayer();
            handler->SendSysMessage("Wrath Remix intro: fell under the world.");
        }
        else
        {
            PlayIntro(player);
            handler->SendSysMessage("Wrath Remix intro: playing.");
        }
        return true;
    }

    static bool HandleGround(ChatHandler* handler, Optional<uint32> radius, Optional<uint32> step)
    {
        Player* player = handler->GetSession()->GetPlayer();
        int32 r = int32(std::min<uint32>(radius.value_or(40), 120));
        int32 s = int32(std::max<uint32>(step.value_or(4), 1));
        float cx = std::round(player->GetPositionX()), cy = std::round(player->GetPositionY()), cz = player->GetPositionZ();
        handler->PSendSysMessage("Wrath Remix ground: map {} around {:.0f} {:.0f}, every {} yards, x from {:.0f} down, y from {:.0f} down",
            player->GetMapId(), cx, cy, s, cx + r, cy + r);
        for (int32 dx = r; dx >= -r; dx -= s)
        {
            std::string row = Acore::StringFormat("ground x {:.0f}:", cx + dx);
            for (int32 dy = r; dy >= -r; dy -= s)
            {
                float z = player->GetMap()->GetHeight(player->GetPhaseMask(), cx + dx, cy + dy, cz + 10.0f, true, 40.0f);
                row += z > INVALID_HEIGHT + 1.0f && std::fabs(z - cz) < 30.0f ? Acore::StringFormat(" {:.1f}", z) : std::string(" -");
            }
            handler->SendSysMessage(row);
        }
        return true;
    }

    // .remix band (game masters): the creatures within 60 yards, their level and their band.
    static bool HandleBand(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        uint32 zone = player->GetZoneId();
        LevelBand const* band = BandFor(player->GetMapId(), zone);
        if (band)
            handler->PSendSysMessage("Wrath Remix band: {} (zone {}), levels {}-{} become {}-{}.", band->name, zone,
                band->originalMin, band->originalMax, band->bandMin, band->bandMax);
        else
            handler->PSendSysMessage("Wrath Remix band: none here (map {}, zone {}).", player->GetMapId(), zone);
        if (FollowActive())
            handler->SendSysMessage("Wrath Remix levels: hostile and neutral creatures near a Timerunner at their level (the band where none is near).");
        std::list<Creature*> creatures;
        AnyCreatureInRange check(player, 60.0f);
        Acore::CreatureListSearcher<AnyCreatureInRange> searcher(player, creatures, check);
        Cell::VisitObjects(player, searcher, 60.0f);
        // The band leaves creatures at or below its levels (critters, the odd old-world visitor) as
        // they are; the check counts the ones it applies to.
        uint32 shown = 0, banded = 0, lowest = 255, highest = 0, normals = 0;
        double share = 0;
        for (Creature* creature : creatures)
        {
            CreatureTemplate const* info = creature->GetCreatureTemplate();
            if (!info || (info->Entry >= NPC_MORATARI && info->Entry <= NPC_INSTRUCTOR_LAST))
                continue;
            // (anyone's pet, guardian or totem, a bot's hunter's say, passing by: the squish leaves them be)
            if (creature->IsPet() || creature->HasUnitTypeMask(UNIT_MASK_MINION) || creature->GetCharmerOrOwnerGUID() || creature->IsControlledByPlayer())
                continue;
            bool applies = band && int32(info->minlevel) > band->bandMax;
            if (applies)
            {
                ++banded;
                lowest = std::min<uint32>(lowest, creature->GetLevel());
                highest = std::max<uint32>(highest, creature->GetLevel());
                // a normal creature's health against its new level's (the squish's share of it)
                if (info->rank == CREATURE_ELITE_NORMAL)
                    if (CreatureBaseStats const* stats = sObjectMgr->GetCreatureBaseStats(creature->GetLevel(), info->unit_class))
                        if (float full = stats->GenerateHealth(info) * sWorld->getRate(RATE_CREATURE_NORMAL_HP); full >= 1.0f)
                        {
                            share += creature->GetMaxHealth() / full;
                            ++normals;
                        }
            }
            if (shown++ < 12)
                handler->PSendSysMessage("creature {} {}: level {} (template {}-{}){}", info->Entry, info->Name,
                    uint32(creature->GetLevel()), uint32(info->minlevel), uint32(info->maxlevel), applies ? "" : ", not banded");
        }
        if (banded)
            handler->PSendSysMessage("Wrath Remix band check: {} banded creatures, levels {} to {}.", banded, lowest, highest);
        if (normals)
            handler->PSendSysMessage("Wrath Remix squish check: {} normal creatures at {}% of their level's health (squish {}%, damage {}%).",
                normals, uint32(std::lround(100.0 * share / normals)), squishHealth, squishDamage);
        return true;
    }

    // .remix guid ENTRY (game masters): the nearest creature of that entry and its guid (CI's
    // test client talks to Remix's NPCs by it: the core gives creatures a guid of their map's).
    static bool HandleGuid(ChatHandler* handler, uint32 entry)
    {
        Player* player = handler->GetSession()->GetPlayer();
        Creature* creature = player->FindNearestCreature(entry, 100.0f);
        if (!creature)
        {
            handler->PSendSysMessage("Wrath Remix guid: no creature {} within 100 yards.", entry);
            return true;
        }
        handler->PSendSysMessage("Wrath Remix guid: {} {} at {:.1f} yards.", entry, creature->GetGUID().GetRawValue(),
            player->GetDistance(creature));
        return true;
    }

    // .remix goguid ENTRY (game masters): the same for the nearest game object of that entry (the
    // test client clicks the Bazaar's campfire by it).
    static bool HandleGoGuid(ChatHandler* handler, uint32 entry)
    {
        Player* player = handler->GetSession()->GetPlayer();
        GameObject* object = player->FindNearestGameObject(entry, 100.0f);
        if (!object)
        {
            handler->PSendSysMessage("Wrath Remix goguid: no object {} within 100 yards.", entry);
            return true;
        }
        handler->PSendSysMessage("Wrath Remix goguid: {} {} at {:.1f} yards.", entry, object->GetGUID().GetRawValue(),
            player->GetDistance(object));
        return true;
    }

    // .remix sees ENTRY (game masters): whether the story lets the player see the nearest creature
    // of that entry (its visibility conditions, as a player without game master mode has them).
    static bool HandleSees(ChatHandler* handler, uint32 entry)
    {
        Player* player = handler->GetSession()->GetPlayer();
        Creature* creature = player->FindNearestCreature(entry, 100.0f);
        // None alive (all just slain, not yet back): the nearest one's corpse, whose conditions are the same.
        if (!creature)
            creature = player->FindNearestCreature(entry, 100.0f, false);
        if (!creature)
        {
            handler->PSendSysMessage("Wrath Remix sees: no creature {} within 100 yards.", entry);
            return true;
        }
        ConditionSourceInfo info(player, creature);
        bool seen = sConditionMgr->IsObjectMeetToConditions(info, sConditionMgr->GetConditionsForObjectVisibility(creature));
        handler->PSendSysMessage("Wrath Remix sees: {} {} (spawn {}).", entry, seen ? "seen" : "hidden", creature->GetSpawnId());
        return true;
    }

    struct AnyCreatureInRange
    {
        AnyCreatureInRange(WorldObject const* source, float range) : _source(source), _range(range) { }
        bool operator()(Creature* creature) const { return _source->IsWithinDistInMap(creature, _range); }
        WorldObject const* _source;
        float _range;
    };
};

void AddWrathRemixScripts()
{
    new WrathRemixWorld();
    new WrathRemixPlayer();
    new WrathRemixLevels();
    new WrathRemixDamage();
    new WrathRemixCommands();
}
