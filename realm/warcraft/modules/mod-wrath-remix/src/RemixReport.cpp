// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix's time anomaly reports.
 *
 * The realm keeps a journal of each Timerunner's way through the story in remix_log: the quests
 * they take, finish, turn in and drop, who they speak to, the zones they enter, their levels and
 * deaths, beside Moratari's transitions. The app's add-on (WowTouch, client/TouchAddon.kt) puts
 * Report Time Anomaly in the game's menu, and asks the realm for a report in an add-on message to
 * the player itself: "WowRemix<tab>report <what the player wrote>" (a long one in pieces, each one
 * but the last "report+ <its words>"; up to 1000 letters in all). The report says where the
 * Timerunner is, the quest they're on and who they've spoken to since they took it, the rest of
 * their quest log, and the way they came (the journal's latest steps). It goes, in Markdown with
 * the title on its first line, into the folder WOW_REPORTS_DIR names (ctl.sh: files/run/reports),
 * where the app finds it and sends it to GitHub as an issue.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Creature.h"
#include "DBCStores.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "StringFormat.h"
#include "World.h"
#include "WorldSession.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <mutex>
#include <string_view>
#include <unordered_map>
#include <vector>

namespace WrathRemix
{
    namespace
    {
        constexpr std::string_view ADDON_PREFIX = "WowRemix\t";
        constexpr uint32 JOURNAL_STEPS = 300;   // the report's way here: the journal's latest steps
        constexpr time_t TALK_AGAIN = 60;       // the same creature spoken to again within a minute: one line
        constexpr time_t REPORT_AGAIN = 30;     // the same report a moment after the last: a second tap
        constexpr size_t REPORT_LENGTH = 4000;  // what a report's own words can run to, in bytes (the add-on's box holds 1000 letters)

        // What the journal last noted for each Timerunner, so it doesn't repeat itself.
        struct Noted
        {
            uint32 talk = 0;
            time_t talkTime = 0;
            uint32 zone = 0;
            time_t report = 0;
            std::string reported;   // that report's words
            std::string draft;      // a long report's words so far ("report+" messages, ahead of its last)
        };
        std::mutex notedLock;
        std::unordered_map<uint32, Noted> noted;

        // A line of the journal, as the report reads it.
        struct Step
        {
            std::string what;
            uint32 entry;
            int32 amount;
            uint32 area;
            time_t time;
        };

        bool Journaling(Player* player)
        {
            return Active() && player && !IsBot(player);
        }

        void NoteTalk(Player* player, char const* what, uint32 entry)
        {
            if (!Journaling(player))
                return;
            time_t now = std::time(nullptr);
            {
                std::lock_guard<std::mutex> lock(notedLock);
                Noted& n = noted[player->GetGUID().GetCounter()];
                if (n.talk == entry && now - n.talkTime < TALK_AGAIN)
                {
                    n.talkTime = now;
                    return;
                }
                n.talk = entry;
                n.talkTime = now;
            }
            Record(player, what, entry, 0);
        }

        // ---- Names, as the report writes them ----------------------------------------------------

        std::string QuestTitle(uint32 id)
        {
            Quest const* quest = sObjectMgr->GetQuestTemplate(id);
            return quest ? quest->GetTitle() : "an unknown quest";
        }

        std::string CreatureName(uint32 entry)
        {
            CreatureTemplate const* info = sObjectMgr->GetCreatureTemplate(entry);
            return info ? info->Name : "someone unknown";
        }

        std::string ObjectName(uint32 entry)
        {
            GameObjectTemplate const* info = sObjectMgr->GetGameObjectTemplate(entry);
            return info ? info->name : "something unknown";
        }

        std::string AreaName(uint32 id)
        {
            AreaTableEntry const* area = sAreaTableStore.LookupEntry(id);
            char const* name = area ? area->area_name[sWorld->GetDefaultDbcLocale()] : nullptr;
            return name && *name ? name : Acore::StringFormat("area {}", id);
        }

        std::string MapName(uint32 id)
        {
            MapEntry const* map = sMapStore.LookupEntry(id);
            char const* name = map ? map->name[sWorld->GetDefaultDbcLocale()] : nullptr;
            return name && *name ? name : Acore::StringFormat("map {}", id);
        }

        char const* RaceName(uint8 race)
        {
            switch (race)
            {
                case RACE_HUMAN: return "Human";
                case RACE_ORC: return "Orc";
                case RACE_DWARF: return "Dwarf";
                case RACE_NIGHTELF: return "Night Elf";
                case RACE_UNDEAD_PLAYER: return "Undead";
                case RACE_TAUREN: return "Tauren";
                case RACE_GNOME: return "Gnome";
                case RACE_TROLL: return "Troll";
                case RACE_BLOODELF: return "Blood Elf";
                case RACE_DRAENEI: return "Draenei";
                default: return "unknown race";
            }
        }

        char const* ClassName(uint8 cls)
        {
            switch (cls)
            {
                case CLASS_WARRIOR: return "Warrior";
                case CLASS_PALADIN: return "Paladin";
                case CLASS_HUNTER: return "Hunter";
                case CLASS_ROGUE: return "Rogue";
                case CLASS_PRIEST: return "Priest";
                case CLASS_DEATH_KNIGHT: return "Death Knight";
                case CLASS_SHAMAN: return "Shaman";
                case CLASS_MAGE: return "Mage";
                case CLASS_WARLOCK: return "Warlock";
                case CLASS_DRUID: return "Druid";
                default: return "unknown class";
            }
        }

        // A time, in UTC (the phone's realm keeps no time zone).
        std::string When(time_t t, char const* format = "%m-%d %H:%M")
        {
            std::tm tm{};
            gmtime_r(&t, &tm);
            char text[32];
            std::strftime(text, sizeof(text), format, &tm);
            return text;
        }

        // The player's own words, on one line, without what Markdown would read as markup.
        std::string Plain(std::string text)
        {
            for (char& c : text)
                if (c == '\r' || c == '\n' || c == '\t' || c == '<' || c == '>' || c == '`' || c == '|')
                    c = ' ';
            text.erase(0, text.find_first_not_of(' '));
            text.erase(text.find_last_not_of(' ') + 1);
            return text;
        }

        // [text] cut to at most [bytes], not inside a letter (UTF-8).
        std::string Cut(std::string text, size_t bytes)
        {
            if (text.size() <= bytes)
                return text;
            while (bytes > 0 && (uint8(text[bytes]) & 0xC0) == 0x80)
                --bytes;
            text.resize(bytes);
            return text;
        }

        std::string Describe(Step const& step)
        {
            std::string const& w = step.what;
            if (w == "accept")
                return Acore::StringFormat("Took **{}** ({})", QuestTitle(step.entry), step.entry);
            if (w == "complete")
                return Acore::StringFormat("Finished the objectives of **{}** ({})", QuestTitle(step.entry), step.entry);
            if (w == "reward")
                return Acore::StringFormat("Turned in **{}** ({})", QuestTitle(step.entry), step.entry);
            if (w == "abandon")
                return Acore::StringFormat("Dropped **{}** ({})", QuestTitle(step.entry), step.entry);
            if (w == "talk")
                return Acore::StringFormat("Spoke to {} ({})", CreatureName(step.entry), step.entry);
            if (w == "object")
                return Acore::StringFormat("Used {} (object {})", ObjectName(step.entry), step.entry);
            if (w == "zone")
                return Acore::StringFormat("Entered {}", AreaName(step.entry));
            if (w == "level")
                return Acore::StringFormat("Reached level {}", step.entry);
            if (w == "death")
                return step.entry ? Acore::StringFormat("Died to {} ({})", CreatureName(step.entry), step.entry) : std::string("Died");
            if (w == "bridge")
                return Acore::StringFormat("Moratari's transition: **{}** ({})", QuestTitle(step.entry), step.entry);
            if (w == "recover")
                return Acore::StringFormat("Moratari brought them back to Chapter {}", step.entry);
            if (w == "login")
                return "Logged in";
            if (w == "report")
                return "Reported a time anomaly";
            return Acore::StringFormat("{} {} {}", w, step.entry, step.amount);
        }

        bool IsTalk(Step const& step)
        {
            return step.what == "talk" || step.what == "object";
        }

        std::string Talked(Step const& step)
        {
            return step.what == "object" ? Acore::StringFormat("{} (object {})", ObjectName(step.entry), step.entry)
                                         : Acore::StringFormat("{} ({})", CreatureName(step.entry), step.entry);
        }

        // ---- The report ---------------------------------------------------------------------------

        // A quest in the log, and where the journal has it taken (steps.size() when it doesn't).
        struct Held
        {
            Quest const* quest;
            size_t taken;
        };

        std::vector<std::string> Objectives(Player* player, Quest const* quest)
        {
            std::vector<std::string> lines;
            auto const& statuses = player->getQuestStatusMap();
            auto status = statuses.find(quest->GetQuestId());
            for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
            {
                int32 target = quest->RequiredNpcOrGo[i];
                if (!target || !quest->RequiredNpcOrGoCount[i])
                    continue;
                std::string name = !quest->ObjectiveText[i].empty() ? quest->ObjectiveText[i]
                    : target > 0 ? CreatureName(uint32(target)) : ObjectName(uint32(-target));
                uint32 count = status != statuses.end() ? status->second.CreatureOrGOCount[i] : 0;
                lines.push_back(Acore::StringFormat("{}: {}/{} ({} {})", name, count, quest->RequiredNpcOrGoCount[i],
                    target > 0 ? "creature" : "object", std::abs(target)));
            }
            for (uint8 i = 0; i < QUEST_ITEM_OBJECTIVES_COUNT; ++i)
            {
                uint32 item = quest->RequiredItemId[i];
                if (!item || !quest->RequiredItemCount[i])
                    continue;
                ItemTemplate const* proto = sObjectMgr->GetItemTemplate(item);
                lines.push_back(Acore::StringFormat("{}: {}/{} (item {})", proto ? proto->Name1 : "an unknown item",
                    std::min(player->GetItemCount(item, true), quest->RequiredItemCount[i]), quest->RequiredItemCount[i], item));
            }
            if (quest->HasSpecialFlag(QUEST_SPECIAL_FLAGS_EXPLORATION_OR_EVENT))
                lines.push_back(Acore::StringFormat("Its place found or its event done: {}",
                    status != statuses.end() && status->second.Explored ? "yes" : "no"));
            return lines;
        }

        char const* StatusName(QuestStatus status)
        {
            switch (status)
            {
                case QUEST_STATUS_COMPLETE: return "ready to turn in";
                case QUEST_STATUS_FAILED: return "failed";
                case QUEST_STATUS_INCOMPLETE: return "in progress";
                default: return "in the log";
            }
        }

        // When and from whom a quest was taken, by the journal.
        std::string Taken(std::vector<Step> const& steps, Held const& held)
        {
            if (held.taken >= steps.size())
                return "taken before the journal's latest steps";
            Step const& step = steps[held.taken];
            std::string text = Acore::StringFormat("taken {} in {}", When(step.time), AreaName(step.area));
            // (whoever they spoke to last, a moment before)
            for (size_t i = held.taken; i-- > 0 && step.time - steps[i].time < 300;)
                if (IsTalk(steps[i]))
                    return text + " from " + Talked(steps[i]);
            return text;
        }

        // Who they've spoken to since they took it.
        std::string SpokenTo(std::vector<Step> const& steps, Held const& held)
        {
            if (held.taken >= steps.size())
                return "unknown (taken before the journal's latest steps)";
            std::string text;
            for (size_t i = held.taken + 1; i < steps.size(); ++i)
                if (IsTalk(steps[i]))
                    text += (text.empty() ? "" : ", ") + Talked(steps[i]) + " at " + When(steps[i].time, "%H:%M");
            return text.empty() ? "nobody yet" : text;
        }

        // The report's title and body, from the journal's latest steps (oldest first).
        std::pair<std::string, std::string> Compose(Player* player, std::string const& said, std::vector<Step> const& steps)
        {
            std::vector<Held> log;
            for (uint16 slot = 0; slot < MAX_QUEST_LOG_SIZE; ++slot)
            {
                uint32 id = player->GetQuestSlotQuestId(slot);
                Quest const* quest = id ? sObjectMgr->GetQuestTemplate(id) : nullptr;
                if (!quest)
                    continue;
                size_t taken = steps.size();
                for (size_t i = steps.size(); i-- > 0;)
                    if (steps[i].what == "accept" && steps[i].entry == id)
                    {
                        taken = i;
                        break;
                    }
                log.push_back({ quest, taken });
            }
            // The quest they're on: the one they took last (the journal's order; the log's first
            // when it knows none of them).
            auto current = log.end();
            for (auto it = log.begin(); it != log.end(); ++it)
                if (it->taken < steps.size() && (current == log.end() || current->taken >= steps.size() || it->taken > current->taken))
                    current = it;
            if (current == log.end() && !log.empty())
                current = log.begin();

            std::string title = current != log.end()
                ? Acore::StringFormat("Time anomaly: {} ({}, level {})", current->quest->GetTitle(), player->GetName(), player->GetLevel())
                : Acore::StringFormat("Time anomaly in {} ({}, level {})", AreaName(player->GetZoneId()), player->GetName(), player->GetLevel());

            std::string body;
            body += "**What happened:** " + (said.empty() ? std::string("_nothing written_") : said) + "\n\n";

            Timerunner const t = Get(player);
            Chapter const* chapter = ChapterFor(t.chapter);
            uint32 played = player->GetTotalPlayedTime();
            body += "### The Timerunner\n";
            body += Acore::StringFormat("- **{}**, level {} {} {}, {}\n", player->GetName(), player->GetLevel(),
                RaceName(player->getRace()), ClassName(player->getClass()), IsAlliance(player) ? "Alliance" : "Horde");
            body += chapter ? Acore::StringFormat("- Chapter {}: {}\n", uint32(chapter->chapter), chapter->name) : std::string("- The prologue\n");
            body += Acore::StringFormat("- In {}: {} ({}, map {}: {:.1f}, {:.1f}, {:.1f}, facing {:.2f})\n", AreaName(player->GetZoneId()),
                AreaName(player->GetAreaId()), MapName(player->GetMapId()), player->GetMapId(), player->GetPositionX(),
                player->GetPositionY(), player->GetPositionZ(), player->GetOrientation());
            body += Acore::StringFormat("- {}{}, {} Bronze carried, {} earned; {} quests turned in; played {} h {} min\n",
                player->IsAlive() ? "Alive" : "Dead", player->IsInCombat() ? " and in combat" : "", Bronze(player), t.earned,
                player->getRewardedQuests().size(), played / 3600, played / 60 % 60);
            body += Acore::StringFormat("- Reported {} UTC\n\n", When(std::time(nullptr), "%Y-%m-%d %H:%M:%S"));

            body += "### The quest they're on\n";
            if (current == log.end())
            {
                body += "None: the quest log is empty.";
                for (size_t i = steps.size(); i-- > 0;)
                    if (steps[i].what == "reward")
                    {
                        body += Acore::StringFormat(" The last quest turned in: **{}** ({}), {}.", QuestTitle(steps[i].entry), steps[i].entry, When(steps[i].time));
                        std::string since;
                        for (size_t j = i + 1; j < steps.size(); ++j)
                            if (IsTalk(steps[j]))
                                since += (since.empty() ? "" : ", ") + Talked(steps[j]) + " at " + When(steps[j].time, "%H:%M");
                        body += "\n- Spoken to since: " + (since.empty() ? std::string("nobody yet") : since);
                        break;
                    }
                body += "\n\n";
            }
            else
            {
                Quest const* quest = current->quest;
                body += Acore::StringFormat("**{}** ({}), {}, {}\n", quest->GetTitle(), quest->GetQuestId(),
                    StatusName(player->GetQuestStatus(quest->GetQuestId())), Taken(steps, *current));
                for (std::string const& line : Objectives(player, quest))
                    body += "- " + line + "\n";
                body += "- Spoken to since it was taken: " + SpokenTo(steps, *current) + "\n\n";

                if (log.size() > 1)
                {
                    body += "### The rest of the quest log\n";
                    for (auto it = log.begin(); it != log.end(); ++it)
                    {
                        if (it == current)
                            continue;
                        std::vector<std::string> objectives = Objectives(player, it->quest);
                        std::string joined;
                        for (std::string const& line : objectives)
                            joined += (joined.empty() ? "" : "; ") + line;
                        body += Acore::StringFormat("- **{}** ({}), {}, {}{}{}. Spoken to since: {}\n", it->quest->GetTitle(),
                            it->quest->GetQuestId(), StatusName(player->GetQuestStatus(it->quest->GetQuestId())), Taken(steps, *it),
                            joined.empty() ? "" : ": ", joined, SpokenTo(steps, *it));
                    }
                    body += "\n";
                }
            }

            // (the app cuts this list from the top when a report must be shorter: keep it last)
            body += "### The way here\n";
            body += steps.size() >= JOURNAL_STEPS
                ? Acore::StringFormat("The journal's last {} steps, oldest first (times in UTC):\n", steps.size())
                : std::string("Every step the journal has, oldest first (times in UTC):\n");
            for (Step const& step : steps)
                body += Acore::StringFormat("- `{}` {}: {}\n", When(step.time), AreaName(step.area), Describe(step));
            return { title, body };
        }

        // Writes the report where the app looks for it; the file's name, or "" if it couldn't.
        std::string Keep(Player* player, std::string const& title, std::string const& body)
        {
            static char const* dir = std::getenv("WOW_REPORTS_DIR");
            if (!dir || !*dir)
                return "";
            std::error_code error;
            std::filesystem::create_directories(dir, error);
            std::string stem = Acore::StringFormat("anomaly-{}-{}", When(std::time(nullptr), "%Y%m%d-%H%M%S"), player->GetGUID().GetCounter());
            std::string name = stem + ".md";
            // (another within the same second: a name of its own)
            for (uint32 i = 2; i < 100 && std::filesystem::exists(std::string(dir) + "/" + name, error); ++i)
                name = Acore::StringFormat("{}-{}.md", stem, i);
            std::string path = std::string(dir) + "/" + name;
            std::string tmp = path + ".tmp";
            FILE* file = std::fopen(tmp.c_str(), "w");
            if (!file)
                return "";
            bool written = std::fprintf(file, "# %s\n\n%s", title.c_str(), body.c_str()) > 0;
            written = std::fclose(file) == 0 && written;
            if (!written || std::rename(tmp.c_str(), path.c_str()) != 0)
            {
                std::remove(tmp.c_str());
                return "";
            }
            return name;
        }

        // A long report comes in pieces (an add-on message holds 255 characters): each but the last
        // is "report+ <words>", kept until the last one, "report <words>", comes.
        void ReportPart(Player* player, std::string const& part)
        {
            std::lock_guard<std::mutex> lock(notedLock);
            std::string& draft = noted[player->GetGUID().GetCounter()].draft;
            // (cut to its length, between letters, as the last one comes)
            if (draft.size() < REPORT_LENGTH)
                draft += part;
        }

        // A report that wasn't written: the same words again aren't taken for a second tap.
        void NotReported(ObjectGuid::LowType guid)
        {
            std::lock_guard<std::mutex> lock(notedLock);
            auto it = noted.find(guid);
            if (it != noted.end())
                it->second.report = 0;
        }

        void Report(Player* player, std::string said)
        {
            ChatHandler handler(player->GetSession());
            time_t now = std::time(nullptr);
            ObjectGuid::LowType guid = player->GetGUID().GetCounter();
            {
                std::lock_guard<std::mutex> lock(notedLock);
                Noted& n = noted[guid];
                said = Cut(n.draft + said, REPORT_LENGTH);
                n.draft.clear();
                // (other words are another report: written too)
                if (now - n.report < REPORT_AGAIN && said == n.reported)
                {
                    handler.SendSysMessage("|cff8fd3ffTime anomaly:|r you reported that a moment ago. It's on its way.");
                    return;
                }
                n.report = now;
                n.reported = said;
            }
            // (the journal's lines are written in order on the characters database's one worker
            // thread: what was noted just now is there when this reads it)
            WorldSession* session = player->GetSession();
            session->GetQueryProcessor().AddCallback(CharacterDatabase.AsyncQuery(Acore::StringFormat(
                "SELECT `what`, `entry`, `amount`, `area`, UNIX_TIMESTAMP(`time`) FROM `remix_log` WHERE `guid` = {} ORDER BY `id` DESC LIMIT {}",
                guid, JOURNAL_STEPS)).WithCallback([session, guid, said = Plain(said)](QueryResult result)
            {
                Player* player = session->GetPlayer();
                if (!player || player->GetGUID().GetCounter() != guid)
                    return;
                if (!player->IsInWorld())
                {
                    // (on the way between places, a loading screen)
                    NotReported(guid);
                    ChatHandler(session).SendSysMessage("|cff8fd3ffTime anomaly:|r the report couldn't be written on your way between places. Report it again.");
                    return;
                }
                std::vector<Step> steps;
                if (result)
                    do
                    {
                        Field* f = result->Fetch();
                        steps.push_back({ f[0].Get<std::string>(), f[1].Get<uint32>(), f[2].Get<int32>(), f[3].Get<uint32>(), time_t(f[4].Get<uint64>()) });
                    } while (result->NextRow());
                std::reverse(steps.begin(), steps.end());
                auto [title, body] = Compose(player, said, steps);
                std::string name = Keep(player, title, body);
                ChatHandler handler(session);
                if (name.empty())
                {
                    NotReported(guid);
                    LOG_ERROR("module", "Wrath Remix: a time anomaly report from {} couldn't be written (WOW_REPORTS_DIR)", player->GetName());
                    handler.SendSysMessage("|cff8fd3ffTime anomaly:|r the report couldn't be written on this realm.");
                    return;
                }
                Record(player, "report", 0, 0);
                LOG_INFO("module", "Wrath Remix: time anomaly report {} from {}", name, player->GetName());
                handler.SendSysMessage("|cff8fd3ffTime anomaly reported.|r The app is sending your report to GitHub.");
            }));
        }
    }
}

using namespace WrathRemix;

// The journal's lines, and the add-on's request for a report.
class WrathRemixJournal : public PlayerScript
{
public:
    WrathRemixJournal() : PlayerScript("WrathRemixJournal", {
        PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_LOGOUT,
        PLAYERHOOK_ON_PLAYER_QUEST_ACCEPT,
        PLAYERHOOK_ON_BEFORE_QUEST_COMPLETE,
        PLAYERHOOK_ON_PLAYER_COMPLETE_QUEST,
        PLAYERHOOK_ON_QUEST_ABANDON,
        PLAYERHOOK_ON_UPDATE_ZONE,
        PLAYERHOOK_ON_LEVEL_CHANGED,
        PLAYERHOOK_ON_PLAYER_KILLED_BY_CREATURE,
        PLAYERHOOK_CAN_PLAYER_USE_PRIVATE_CHAT,
    }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (Journaling(player))
            Record(player, "login", 0, 0);
    }

    void OnPlayerLogout(Player* player) override
    {
        std::lock_guard<std::mutex> lock(notedLock);
        noted.erase(player->GetGUID().GetCounter());
    }

    void OnPlayerQuestAccept(Player* player, Quest const* quest) override
    {
        if (Journaling(player))
            Record(player, "accept", quest->GetQuestId(), 0);
    }

    // (called as a quest's objectives are done, before it's marked so)
    bool OnPlayerBeforeQuestComplete(Player* player, uint32 questId) override
    {
        if (Journaling(player))
            Record(player, "complete", questId, 0);
        return true;
    }

    // (called as a quest is turned in)
    void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
    {
        if (Journaling(player))
            Record(player, "reward", quest->GetQuestId(), 0);
    }

    void OnPlayerQuestAbandon(Player* player, uint32 questId) override
    {
        if (Journaling(player))
            Record(player, "abandon", questId, 0);
    }

    void OnPlayerUpdateZone(Player* player, uint32 newZone, uint32 /*newArea*/) override
    {
        if (!Journaling(player))
            return;
        {
            std::lock_guard<std::mutex> lock(notedLock);
            Noted& n = noted[player->GetGUID().GetCounter()];
            if (n.zone == newZone)
                return;
            n.zone = newZone;
        }
        Record(player, "zone", newZone, 0);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        if (Journaling(player))
            Record(player, "level", player->GetLevel(), 0);
    }

    void OnPlayerKilledByCreature(Creature* killer, Player* killed) override
    {
        if (Journaling(killed))
            Record(killed, "death", killer ? killer->GetEntry() : 0, 0);
    }

    // The add-on's message to the player itself: kept from them, and answered.
    bool OnPlayerCanUseChat(Player* player, uint32 type, uint32 language, std::string& msg, Player* receiver) override
    {
        if (language != LANG_ADDON || type != CHAT_MSG_WHISPER || receiver != player || msg.rfind(ADDON_PREFIX, 0) != 0)
            return true;
        std::string_view request = std::string_view(msg).substr(ADDON_PREFIX.size());
        if (request.rfind("settled", 0) == 0)
            ClientSettled(player);
        else if (Journaling(player) && request.rfind("report+", 0) == 0)
            ReportPart(player, std::string(request.substr(std::min<size_t>(request.size(), 8))));
        else if (Journaling(player) && request.rfind("report", 0) == 0)
            Report(player, std::string(request.substr(std::min<size_t>(request.size(), 7))));
        return false;
    }
};

// Who they speak to: a creature's gossip or quests, a quest-giving object.
class WrathRemixJournalCreatures : public AllCreatureScript
{
public:
    WrathRemixJournalCreatures() : AllCreatureScript("WrathRemixJournalCreatures") { }

    bool CanCreatureGossipHello(Player* player, Creature* creature) override
    {
        NoteTalk(player, "talk", creature->GetEntry());
        return false;
    }
};

class WrathRemixJournalObjects : public AllGameObjectScript
{
public:
    WrathRemixJournalObjects() : AllGameObjectScript("WrathRemixJournalObjects") { }

    bool CanGameObjectGossipHello(Player* player, GameObject* go) override
    {
        NoteTalk(player, "object", go->GetEntry());
        return false;
    }
};

void AddRemixReportScripts()
{
    new WrathRemixJournal();
    new WrathRemixJournalCreatures();
    new WrathRemixJournalObjects();
}
