// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix's end (STORY.md, "The end"):
 *
 * - The Lich King's fall counts for every Timerunner in his citadel who is on The Last Necessary
 *   Battle; once the ending cinematic is over (the game says so, or long enough has passed), they
 *   are brought back to the Infinite Bazaar, where everyone is waiting (scene 800), and Eternus's
 *   letter arrives.
 * - What Sylvanas, Alleria, Moratari and the Keepers can tell once the war is over
 *   (remix_conversation), and the goodbyes See You Later asks for.
 * - Back to Your Own Time: once its scene is over, the Timerunner goes home, as Legion Remix sends
 *   its characters home. Their character, without its Bronze, is written to WOW_TRANSFERS_DIR
 *   (ctl.sh: files/run/transfers) and taken off Wrath Remix; the game is let go, and the app starts
 *   the server again on ChromieCraft (Homecomings.kt), whose world server takes the character in, in
 *   their side's capital, as it starts.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "GossipDef.h"
#include "Log.h"
#include "Mail.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Opcodes.h"
#include "Player.h"
#include "PlayerDump.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "World.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <set>

namespace WrathRemix
{
    namespace
    {
        constexpr uint32 NPC_THE_LICH_KING = 36597;
        constexpr uint32 MAP_REMIX_ICECROWN_CITADEL = 631;
        constexpr uint32 SCENE_RETURN = 800;
        // How long after the Lich King's death a Timerunner who never says the cinematic is over is
        // brought back anyway (it starts 11.5 seconds after his death and runs a few minutes).
        constexpr Seconds RETURN_AT_THE_LATEST = 420s;

        enum EndingSenders : uint32
        {
            SENDER_TOPIC = 50,
            SENDER_GOODBYE = 51,
        };

        struct Topic
        {
            uint8 topic;
            std::string label;
            uint32 text;
        };

        std::unordered_map<uint32, std::vector<Topic>> conversations;
        std::string letterSubject, letterBody;

        // The goodbyes See You Later asks for: whose, its credit, and what they say to it.
        struct Goodbye
        {
            uint32 npc, credit, text;
        };
        constexpr Goodbye GOODBYES[] = {
            { NPC_SYLVANAS, 770037, 7703031 },
            { NPC_ALLERIA,  770038, 7703032 },
            { NPC_ANDORMU,  770039, 7703033 },
            { NPC_NOZARI,   770040, 7703034 },
        };

        // Timerunners who saw the Lich King fall and are waiting to be brought back.
        std::mutex returningLock;
        std::set<ObjectGuid> returning;


        Goodbye const* GoodbyeOf(uint32 npc)
        {
            for (Goodbye const& g : GOODBYES)
                if (g.npc == npc)
                    return &g;
            return nullptr;
        }

        bool NeedsCredit(Player* player, uint32 questId, uint32 credit)
        {
            if (player->GetQuestStatus(questId) != QUEST_STATUS_INCOMPLETE)
                return false;
            Quest const* quest = sObjectMgr->GetQuestTemplate(questId);
            if (!quest)
                return false;
            uint16 slot = player->FindQuestSlot(questId);
            for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
                if (quest->RequiredNpcOrGo[i] == int32(credit))
                    return player->GetQuestSlotCounter(slot, i) < quest->RequiredNpcOrGoCount[i];
            return false;
        }

        std::string TransfersDir()
        {
            char const* dir = std::getenv("WOW_TRANSFERS_DIR");
            return dir ? dir : "";
        }

        // ChromieCraft's characters (the same MariaDB): the core takes no character into an account
        // that has ten there (PlayerDump.cpp), so a Timerunner who'd be one too many stays.
        constexpr uint32 HOME_ROOM = 10;

        std::string HomeDatabase()
        {
            return sConfigMgr->GetOption<std::string>("WrathRemix.HomeCharacterDatabase", "acore_characters");
        }

        // A homecoming ChromieCraft couldn't take, set aside in failed/ with why (the app takes the
        // server to ChromieCraft again only for one in the folder itself).
        void SetAside(std::string const& dir, std::string const& base, std::string const& why)
        {
            std::error_code error;
            std::filesystem::create_directories(dir + "/failed", error);
            std::string stem = std::filesystem::path(base).filename().string();
            for (char const* ext : { ".dump", ".who" })
                std::filesystem::rename(base + ext, dir + "/failed/" + stem + ext, error);
            std::ofstream(dir + "/failed/" + stem + ".why") << why << "\n";
        }

        // Everyone at the Bazaar, once the Timerunner is there (the journey takes a loading screen):
        // a look a second, [tries] times. (Given the player, not their guid: on the way between
        // maps they're in no world, and the game doesn't find them by it.)
        void WelcomeWhenThere(Player* player, uint32 tries)
        {
            if (!tries)
                return;
            ObjectGuid guid = player->GetGUID();
            player->m_Events.AddEventAtOffset([guid, tries]()
            {
                Player* p = ObjectAccessor::FindPlayer(guid);
                if (!p)
                    return;
                if (!p->IsBeingTeleported() && p->GetMapId() == MAP_NORTHREND && p->GetExactDist2d(BAZAAR_X, BAZAAR_Y) < 40.0f)
                    PlayScene(p, SCENE_RETURN);
                else
                    WelcomeWhenThere(p, tries - 1);
            }, tries == 30 ? 2500ms : 1000ms);
        }

        void BringBack(ObjectGuid guid)
        {
            {
                std::lock_guard<std::mutex> lock(returningLock);
                if (!returning.erase(guid))
                    return;
            }
            Player* player = ObjectAccessor::FindPlayer(guid);
            if (!player)
                return;
            Destination const* bazaar = DestinationFor(TRAVEL_BAZAAR);
            if (!bazaar)
                return;
            Record(player, "return", NPC_THE_LICH_KING, 0);
            // (one who fell in the citadel comes back alive, not as a ghost far from their body)
            if (!player->IsAlive())
            {
                player->ResurrectPlayer(1.0f);
                player->SpawnCorpseBones();
            }
            JourneyFromTheDark(player, PlaceName(bazaar->map, BAZAAR_X, BAZAAR_Y, BAZAAR_Z), bazaar->map, BAZAAR_X, BAZAAR_Y, 500, 2000);
            if (!player->TeleportTo(bazaar->map, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O))
                LiftTheCurtain(player);

            // Eternus's letter, from the river's edge.
            if (!letterBody.empty())
            {
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                MailDraft(letterSubject, letterBody).SendMailTo(trans, MailReceiver(player), MailSender(MAIL_CREATURE, NPC_ETERNUS), MAIL_CHECK_MASK_COPIED);
                CharacterDatabase.CommitTransaction(trans);
            }

            WelcomeWhenThere(player, 30);
        }

        void BringBackSoon(Player* player, Milliseconds after)
        {
            ObjectGuid guid = player->GetGUID();
            player->m_Events.AddEventAtOffset([guid]() { BringBack(guid); }, after);
        }

        // The capital of the Timerunner's side, from the world database's teleports.
        bool Capital(bool alliance, uint32& map, float& x, float& y, float& z, float& o, uint32& zone)
        {
            QueryResult result = WorldDatabase.Query("SELECT `map`, `position_x`, `position_y`, `position_z`, `orientation` FROM `game_tele` WHERE `name` = '{}'",
                alliance ? "Stormwind" : "Orgrimmar");
            if (!result)
                return false;
            Field* f = result->Fetch();
            map = f[0].Get<uint32>();
            x = f[1].Get<float>();
            y = f[2].Get<float>();
            z = f[3].Get<float>();
            o = f[4].Get<float>();
            zone = alliance ? 1519 : 1637;
            return true;
        }
    }

    // Back to the Bazaar [after] from now, or as soon as the game says the cinematic is over.
    void ReturnToBazaarSoon(Player* player, Milliseconds after)
    {
        {
            std::lock_guard<std::mutex> lock(returningLock);
            returning.insert(player->GetGUID());
        }
        BringBackSoon(player, after);
    }

    void LoadEnding()
    {
        conversations.clear();
        letterSubject.clear();
        letterBody.clear();
        if (!Active())
            return;
        if (QueryResult result = WorldDatabase.Query("SELECT `npc`, `topic`, `label`, `text` FROM `remix_conversation` ORDER BY `npc`, `topic`"))
        {
            do
            {
                Field* f = result->Fetch();
                conversations[f[0].Get<uint32>()].push_back({ f[1].Get<uint8>(), f[2].Get<std::string>(), f[3].Get<uint32>() });
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `subject`, `body` FROM `remix_letter` WHERE `id` = 1"))
        {
            letterSubject = result->Fetch()[0].Get<std::string>();
            letterBody = result->Fetch()[1].Get<std::string>();
        }
    }

    // Once the Lich King has fallen: their stories, and the goodbyes See You Later asks for.
    bool AddEndingGossip(Player* player, Creature* creature)
    {
        if (!Active() || !(player->GetQuestRewardStatus(QUEST_LAST_NECESSARY_BATTLE) ||
                           player->GetQuestStatus(QUEST_LAST_NECESSARY_BATTLE) == QUEST_STATUS_COMPLETE))
            return false;
        bool added = false;
        auto topics = conversations.find(creature->GetEntry());
        if (topics != conversations.end())
            for (Topic const& t : topics->second)
            {
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, t.label, SENDER_TOPIC, t.topic);
                added = true;
            }
        if (Goodbye const* g = GoodbyeOf(creature->GetEntry()); g && NeedsCredit(player, QUEST_SEE_YOU_LATER, g->credit))
        {
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "I'm going home. Goodbye.", SENDER_GOODBYE, 0);
            added = true;
        }
        return added;
    }

    // A topic chosen (its words, with the topics again), or a goodbye said.
    bool EndingGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action, uint32 menuText)
    {
        if (!Active() || (sender != SENDER_TOPIC && sender != SENDER_GOODBYE))
            return false;
        uint32 text = menuText;
        if (sender == SENDER_GOODBYE)
        {
            if (Goodbye const* g = GoodbyeOf(creature->GetEntry()))
            {
                if (NeedsCredit(player, QUEST_SEE_YOU_LATER, g->credit))
                {
                    player->KilledMonsterCredit(g->credit);
                    Record(player, "goodbye", creature->GetEntry(), 0);
                }
                text = g->text;
            }
        }
        else if (auto topics = conversations.find(creature->GetEntry()); topics != conversations.end())
        {
            for (Topic const& t : topics->second)
                if (t.topic == action)
                    text = t.text;
        }
        ClearGossipMenuFor(player);
        if (creature->IsQuestGiver())
            player->PrepareQuestMenu(creature->GetGUID());
        AddEndingGossip(player, creature);
        SendGossipMenuFor(player, text, creature);
        return true;
    }

    // Home: the end of Back to Your Own Time's scene (RemixScenes.cpp).
    void SendHome(Player* player)
    {
        if (!Active() || IsBot(player))
            return;
        // the quest done (it goes with the character, and means nothing on ChromieCraft)
        if (player->GetQuestStatus(QUEST_BACK_TO_YOUR_OWN_TIME) == QUEST_STATUS_INCOMPLETE)
            player->KilledMonsterCredit(NPC_SCENE_CREDIT);
        if (Quest const* quest = sObjectMgr->GetQuestTemplate(QUEST_BACK_TO_YOUR_OWN_TIME);
            quest && player->GetQuestStatus(QUEST_BACK_TO_YOUR_OWN_TIME) == QUEST_STATUS_COMPLETE)
            player->RewardQuest(quest, 0, player, false);

        std::string dir = TransfersDir();
        if (dir.empty())
        {
            ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari:|r The way home is closed on this realm (WOW_TRANSFERS_DIR). Report a time anomaly, and I will look into it.");
            return;
        }
        // The last try, if ChromieCraft couldn't take them: why, and tried again now.
        {
            std::string failed = dir + "/failed/" + std::to_string(player->GetGUID().GetCounter());
            std::error_code error;
            if (std::ifstream why(failed + ".why"); why)
            {
                std::string reason;
                std::getline(why, reason);
                why.close();
                ChatHandler(player->GetSession()).PSendSysMessage("|cff8fd3ffMoratari:|r The way home closed on you last time ({}). Again, then.", reason);
                for (char const* ext : { ".dump", ".who", ".why" })
                    std::filesystem::remove(failed + ext, error);
            }
        }
        // Room for them in their own time, before anything of theirs is touched.
        if (QueryResult room = CharacterDatabase.Query("SELECT COUNT(*) FROM `{}`.`characters` WHERE `account` = {}", HomeDatabase(), player->GetSession()->GetAccountId());
            room && room->Fetch()[0].Get<uint64>() >= HOME_ROOM)
        {
            ChatHandler(player->GetSession()).PSendSysMessage("|cff8fd3ffMoratari:|r Your own time has no room for you yet: {} of your heroes are on ChromieCraft "
                "already, and that is all a realm keeps. Let one of them go there, then come back here, and I will take you home.", HOME_ROOM);
            return;
        }
        // The Bronze stays at the Bazaar, and so does Moratari's Hourglass.
        if (uint32 bronze = player->GetItemCount(ITEM_BRONZE, true))
            player->DestroyItemCount(ITEM_BRONZE, bronze, true, false);
        if (uint32 hourglasses = player->GetItemCount(ITEM_HOURGLASS, true))
            player->DestroyItemCount(ITEM_HOURGLASS, hourglasses, true, false);
        // So does the Unrisen's plate, worn or not (items 77010 to 77020, wrath_remix_world_0031:
        // ChromieCraft's world has no such items).
        for (uint32 item = 77010; item <= 77020; ++item)
            if (uint32 count = player->GetItemCount(item, true))
                player->DestroyItemCount(item, count, true, false);

        // Saved first, the way the game saves (asynchronously: some of a character's statements
        // are only prepared for that), and the dump written once the save is in, since it reads
        // the character from the database.
        WorldSession* session = player->GetSession();
        ObjectGuid guid = player->GetGUID();
        uint32 account = session->GetAccountId();
        std::string name = player->GetName();
        bool alliance = player->GetTeamId() == TEAM_ALLIANCE;
        // (how far they came with Moratari, for her letter on ChromieCraft: the last of her
        // story's quests turned in, 1 to 9, or 0)
        uint32 romance = 0;
        for (uint32 quest = QUEST_ROMANCE_FIRST; quest <= QUEST_ROMANCE_LAST; ++quest)
            if (player->GetQuestRewardStatus(quest))
                romance = quest - QUEST_ROMANCE_FIRST + 1;
        CharacterDatabaseTransaction save = CharacterDatabase.BeginTransaction();
        player->SaveToDB(save, false, false);
        session->AddTransactionCallback(CharacterDatabase.AsyncCommitTransaction(save)).AfterComplete(
            [guid, account, name, alliance, romance, dir](bool saved)
        {
            Player* player = ObjectAccessor::FindConnectedPlayer(guid);
            ObjectGuid::LowType low = guid.GetCounter();
            std::string base = dir + "/" + std::to_string(low);
            std::error_code error;
            std::filesystem::create_directories(dir, error);
            // (to a string, written here: the core's own file writing refuses a path, with
            // PlayerDump.DisallowPaths as the app's config has it)
            PlayerDumpWriter writer;
            std::string dump;
            bool written = saved && writer.WriteDumpToString(dump, low) == DUMP_SUCCESS && !dump.empty();
            if (written)
            {
                std::ofstream out(base + ".dump.part", std::ios::trunc);
                out << dump;
                out.close();
                written = !out.fail();
            }
            if (!written)
            {
                LOG_ERROR("module", "Wrath Remix: {} couldn't be written to {} to go home", name, dir);
                std::filesystem::remove(base + ".dump.part", error);
                if (player)
                    ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari:|r Something is wrong with the way home. You are still here; report a time anomaly, and I will look into it.");
                return;
            }
            {
                std::ofstream who(base + ".who");
                who << account << "\n" << name << "\n" << (alliance ? "alliance" : "horde") << "\n" << romance << "\n";
            }
            std::filesystem::rename(base + ".dump.part", base + ".dump", error);
            LOG_INFO("module", "Wrath Remix: {} goes home to ChromieCraft ({}.dump)", name, base);

            // Off Wrath Remix: let go of the game. The Timerunner is taken off this realm once
            // ChromieCraft has them (LetGoOfThoseHome, at this realm's next start).
            if (player)
            {
                Record(player, "home", 0, 0);
                ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari:|r Go home, Timerunner. The game will close, and the server will start again on ChromieCraft: you will wake in your side's capital.");
                player->GetSession()->KickPlayer("Wrath Remix: gone home to ChromieCraft");
            }
        });
    }

    // As Wrath Remix starts: the Timerunners ChromieCraft has taken in (home/, by their guid here)
    // are taken off this realm, each once (a .who done is renamed), and only the character that
    // went (the core gives a deleted character's guid to the next one made).
    void LetGoOfThoseHome()
    {
        std::string dir = TransfersDir();
        std::error_code error;
        if (dir.empty() || !std::filesystem::is_directory(dir + "/home", error))
            return;
        for (auto const& entry : std::filesystem::directory_iterator(dir + "/home", error))
        {
            if (!entry.is_regular_file() || entry.path().extension() != ".who")
                continue;
            ObjectGuid::LowType low = ObjectGuid::LowType(std::strtoul(entry.path().stem().string().c_str(), nullptr, 10));
            std::ifstream who(entry.path());
            uint32 account = 0;
            std::string name;
            bool read = bool(who >> account >> name);
            who.close();
            if (read && low)
            {
                CharacterDatabase.EscapeString(name);
                if (CharacterDatabase.Query("SELECT 1 FROM `characters` WHERE `guid` = {} AND `account` = {} AND `name` = '{}'", low, account, name))
                {
                    Player::DeleteFromDB(low, account, true, true);
                    LOG_INFO("module", "Wrath Remix: Timerunner {} ({}) taken off Wrath Remix: home on ChromieCraft", name, low);
                }
            }
            std::filesystem::path done = entry.path();
            done += ".let-go";
            std::filesystem::rename(entry.path(), done, error);
        }
    }

    // Moratari's letter to one who has gone home, by how far they came in her story (tools/romance.py):
    // the whole of it, its heart (from What Eternus Left Out), or its beginning.
    static std::pair<std::string, std::string> MoratariLetter(uint32 stage, std::string const& name)
    {
        if (stage >= 9)
            return { "A letter, slightly singed",
                "Chromie here! This turned up in my hourglass this morning with your name on it and a very stern note that said DO NOT READ. "
                "So I read it. Here you go.\n\n-\n\n" + name + ",\n\n"
                "You are home now, in your own year, and I am in mine, which is all of them. I looked for you in the record this morning. You "
                "are there: stubborn, and brave, and walking into trouble on the second page. I have read that page more often than a scholar "
                "of variables should.\n\n"
                "I kept the tea warm. I kept the tent. I kept the lamp lit, because a dragon is allowed one foolish thing an age, and you were "
                "mine.\n\n"
                "Do not come looking for me. My kind is very bad at being found, and you have a world to save on the usual schedule. But if, "
                "some evening, a cup of tea turns up beside you that you do not remember pouring, drink it. It is from me.\n\n"
                "Whatever comes after,\nM." };
        if (stage >= 5)
            return { "Something I did not get to say",
                "Chromie here. Somebody asked me to deliver this and made me promise not to read it. I am terrible at promises.\n\n-\n\n"
                + name + ",\n\n"
                "We did not get to finish, you and I. There was always another quest, another hour, another thing to put back. I am sorry for "
                "that. I am not sorry for the rest of it. Not one minute.\n\n"
                "You are home now. Be happy there. Let someone pour you a drink, and laugh at your jokes, and notice when you are tired. If "
                "they do not, tell them a dragon said they should.\n\n"
                "I will be watching the record. I always am. Now I have a favorite page.\n\nM." };
        return { "You still owe me a cup of tea",
            "Chromie here. A friend of mine asked me to pass this along. She was blushing. Dragons don't blush, so I must have imagined "
            "it.\n\n-\n\n" + name + ",\n\n"
            "You still owe me a cup of tea. I am a patient creature, and I keep very good accounts.\n\n"
            "Go and be a hero in your own year. Try to stay out of sinkholes. And if you ever wonder what might have happened if we had had "
            "a little more time... so do I.\n\nM." };
    }

    // On ChromieCraft, as its world server starts: the Timerunners who came home from Wrath Remix,
    // in their side's capital.
    void TakeInTimerunners()
    {
        std::string dir = TransfersDir();
        std::error_code error;
        if (dir.empty() || !std::filesystem::is_directory(dir, error))
            return;
        std::filesystem::create_directories(dir + "/home", error);
        for (auto const& entry : std::filesystem::directory_iterator(dir, error))
        {
            if (!entry.is_regular_file() || entry.path().extension() != ".dump")
                continue;
            std::string base = entry.path().parent_path().string() + "/" + entry.path().stem().string();
            std::ifstream who(base + ".who");
            uint32 account = 0, romance = 0;
            std::string name, side;
            if (!(who >> account >> name >> side))
            {
                LOG_ERROR("module", "Wrath Remix: {} has no word of who it is ({}.who)", entry.path().string(), base);
                who.close();
                SetAside(dir, base, "the record of who you are was lost on the way");
                continue;
            }
            if (!(who >> romance))
                romance = 0;  // (one from before her story)
            who.close();
            // (the guid the dump takes: the next free one)
            ObjectGuid::LowType guid = sObjectMgr->GetGenerator<HighGuid::Player>().GetNextAfterMaxUsed();
            PlayerDumpReader reader;
            DumpReturn loaded = reader.LoadDumpFromFile(entry.path().string(), account, name, 0);
            if (loaded != DUMP_SUCCESS)
            {
                LOG_ERROR("module", "Wrath Remix: {} couldn't come home to ChromieCraft ({}, error {})", name, entry.path().string(), uint32(loaded));
                SetAside(dir, base, loaded == DUMP_TOO_MANY_CHARS ? "ChromieCraft had no room: ten characters on the account there"
                                                                   : "ChromieCraft couldn't read the record (error " + std::to_string(uint32(loaded)) + ")");
                continue;
            }
            // In its side's capital, at home there (queued after the dump's own writes, which are
            // queued too).
            uint32 map, zone;
            float x, y, z, o;
            if (Capital(side == "alliance", map, x, y, z, o, zone))
            {
                CharacterDatabase.Execute("UPDATE `characters` SET `map` = {}, `position_x` = {}, `position_y` = {}, `position_z` = {}, `orientation` = {}, `zone` = {}, "
                    "`instance_id` = 0, `taxi_path` = '', `is_logout_resting` = 1 WHERE `guid` = {}", map, x, y, z, o, zone, guid);
                CharacterDatabase.Execute("DELETE FROM `character_homebind` WHERE `guid` = {}", guid);
                CharacterDatabase.Execute("INSERT INTO `character_homebind` (`guid`, `mapId`, `zoneId`, `posX`, `posY`, `posZ`) VALUES ({}, {}, {}, {}, {}, {})",
                    guid, map, zone, x, y, z);
            }
            // Moratari's letter, for one who walked some of her story with her (Chromie brings it).
            if (romance)
            {
                auto [subject, body] = MoratariLetter(romance, name);
                CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
                MailDraft(subject, body).SendMailTo(trans, MailReceiver(guid), MailSender(MAIL_CREATURE, NPC_CHROMIE_HOME), MAIL_CHECK_MASK_COPIED);
                CharacterDatabase.CommitTransaction(trans);
            }
            for (char const* ext : { ".dump", ".who" })
                std::filesystem::rename(base + ext, dir + "/home/" + std::filesystem::path(base).filename().string() + ext, error);
            LOG_INFO("module", "Wrath Remix: {} came home to ChromieCraft{}", name, romance ? ", and a letter with them" : "");
        }
    }
}

using namespace WrathRemix;

// The Lich King falls: it counts for every Timerunner in his citadel on The Last Necessary Battle,
// and brings them back to the Bazaar once the cinematic is over.
class WrathRemixEnding : public UnitScript
{
public:
    WrathRemixEnding() : UnitScript("WrathRemixEnding", true, { UNITHOOK_ON_UNIT_DEATH }) { }

    void OnUnitDeath(Unit* unit, Unit* /*killer*/) override
    {
        if (!Active() || !unit || unit->GetEntry() != NPC_THE_LICH_KING || unit->GetMapId() != MAP_REMIX_ICECROWN_CITADEL || !unit->ToCreature())
            return;
        unit->GetMap()->DoForAllPlayers([](Player* player)
        {
            if (IsBot(player))
                return;
            if (player->GetQuestStatus(QUEST_LAST_NECESSARY_BATTLE) == QUEST_STATUS_INCOMPLETE)
                player->KilledMonsterCredit(NPC_THE_LICH_KING);
            if (player->GetQuestStatus(QUEST_LAST_NECESSARY_BATTLE) != QUEST_STATUS_COMPLETE)
                return;
            Record(player, "lich king", NPC_THE_LICH_KING, 0);
            ReturnToBazaarSoon(player, RETURN_AT_THE_LATEST);
        });
    }
};

// The game says a cinematic is over (CMSG_COMPLETE_MOVIE, handled in the player's own map update).
class WrathRemixEndingPackets : public ServerScript
{
public:
    WrathRemixEndingPackets() : ServerScript("WrathRemixEndingPackets", { SERVERHOOK_CAN_PACKET_RECEIVE }) { }

    bool CanPacketReceive(WorldSession* session, WorldPacket const& packet) override
    {
        if (!Active() || packet.GetOpcode() != CMSG_COMPLETE_MOVIE || !session)
            return true;
        Player* player = session->GetPlayer();
        if (!player || !player->IsInWorld())
            return true;
        bool waiting;
        {
            std::lock_guard<std::mutex> lock(returningLock);
            waiting = returning.count(player->GetGUID()) != 0;
        }
        if (waiting)
            BringBackSoon(player, 2s);
        return true;
    }
};

// One who saw the Lich King fall and was gone before they were brought back (a logout, a lost
// connection, the realm stopped: the wait goes with them) is brought back as they log in; the
// journal says so after a restart (his fall, and no return since). Any wait left from before is
// forgotten, so no later cinematic takes anyone to the Bazaar.
class WrathRemixEndingPlayer : public PlayerScript
{
public:
    WrathRemixEndingPlayer() : PlayerScript("WrathRemixEndingPlayer", { PLAYERHOOK_ON_LOGIN }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (!Active() || IsBot(player))
            return;
        bool waiting;
        {
            std::lock_guard<std::mutex> lock(returningLock);
            waiting = returning.erase(player->GetGUID()) != 0;
        }
        if (player->GetQuestStatus(QUEST_LAST_NECESSARY_BATTLE) != QUEST_STATUS_COMPLETE)
            return;
        if (!waiting)
            if (QueryResult last = CharacterDatabase.Query("SELECT `what` FROM `remix_log` WHERE `guid` = {} AND `what` IN ('lich king', 'return') ORDER BY `id` DESC LIMIT 1",
                    player->GetGUID().GetCounter()))
                waiting = last->Fetch()[0].Get<std::string>() == "lich king";
        // (once they're in the world: after the realm's own first moments at login)
        if (waiting)
            ReturnToBazaarSoon(player, 5s);
    }
};

// ChromieCraft takes in the Timerunners who came home, as its world server starts; Wrath Remix lets
// them go at its own next start, once ChromieCraft has them.
class WrathRemixHomecoming : public WorldScript
{
public:
    WrathRemixHomecoming() : WorldScript("WrathRemixHomecoming", { WORLDHOOK_ON_STARTUP }) { }

    void OnStartup() override
    {
        if (!Active())
            TakeInTimerunners();
        else
            LetGoOfThoseHome();
    }
};

void AddRemixEndingScripts()
{
    new WrathRemixEnding();
    new WrathRemixEndingPackets();
    new WrathRemixEndingPlayer();
    new WrathRemixHomecoming();
}
