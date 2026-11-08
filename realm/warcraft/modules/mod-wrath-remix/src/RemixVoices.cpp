// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Moratari's own voice (remix_voice, tools/voices.py): her Legion Remix lines, said with the words
 * on screen at the moments that fit them: a greeting when she's clicked on, a word when she sends
 * the Timerunner on past something (a transition, Acherus for a death knight), a call back to the
 * Bazaar every tenth level and at the last, a welcome after days away, and a few lines once each at
 * their moment in the story (the prologue's plan, Sylvanas's errand to Eternus, the war put back
 * before Angrathar). The game has her voice when
 * the server package fetched it (data/voices; ClientPatch.cpp puts it in the game's patch); without
 * it she says the same words in text alone.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "GameTime.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "QuestDef.h"
#include "Random.h"
#include "ScriptMgr.h"
#include "WorldPacket.h"
#include <filesystem>
#include <unordered_map>

using namespace WrathRemix;

namespace
{
    struct Line
    {
        uint32 sound;
        std::string words;
        bool voiced;                // its WAV is in data/voices, so the game's patch has it
    };

    std::unordered_map<std::string, std::vector<Line>> lines;    // by moment
    std::unordered_map<ObjectGuid::LowType, time_t> lastGreeting;

    constexpr uint32 QUEST_WHERE_KINGS_WALK = 13188;
    constexpr uint32 QUEST_WARCHIEFS_BLESSING = 13189;
    constexpr uint32 QUEST_OUT_OF_TIME = 77010;             // turned in to Eternus: her praise
    constexpr uint32 QUEST_THE_PLAN = 77011;
    constexpr uint32 NPC_PLAN_WHAT = 770049;                // The Plan's credit for "What do you want from me?"
    constexpr uint32 QUEST_ASK_ETERNUS_ALLIANCE = 77205;    // Sylvanas sends them back to Eternus
    constexpr uint32 QUEST_ASK_ETERNUS_HORDE = 77215;
    constexpr uint32 QUEST_LOST_AT_SEA = 77048;             // the Alliance's war put back: both of these
    constexpr uint32 QUEST_FORGED_ORDERS = 77049;
    constexpr uint32 QUEST_RECORD_KEEPS_WARSONG = 77230;    // the Horde's
    constexpr time_t GREETING_EVERY = 20;           // seconds between greetings to one Timerunner
    constexpr time_t AWAY_FOR = 3 * DAY;            // gone this long: welcomed back

    Line const* Pick(std::string const& moment, int32 index)
    {
        auto it = lines.find(moment);
        if (it == lines.end() || it->second.empty())
            return nullptr;
        if (index < 0)
            return &it->second[urand(0, uint32(it->second.size()) - 1)];
        return uint32(index) < it->second.size() ? &it->second[index] : nullptr;
    }

    // Her whisper, as the game's people whisper (her name in it), from wherever she is.
    void Whisper(Player* player, Line const& line)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_WHISPER, LANG_UNIVERSAL, ObjectGuid::Empty, player->GetGUID(), line.words, 0, "Moratari", player->GetName());
        player->SendDirectMessage(&data);
        if (line.voiced)
            player->PlayDirectSound(line.sound, player);
    }

    // A line of [moment]'s in a moment, said by Moratari if she's near them by then.
    void SayLater(Player* player, std::string const& moment, int32 index, Milliseconds after)
    {
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid, moment, index]()
        {
            if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
                MoratariVoice(p, moment, index, p->FindNearestCreature(NPC_MORATARI, 40.0f));
        }, after);
    }
}

namespace WrathRemix
{
    std::string VoicesFolder()
    {
        std::string source = sConfigMgr->GetOption<std::string>("SourceDirectory", "");
        return (source.empty() ? std::string(".") : source) + "/modules/mod-wrath-remix/data/voices";
    }

    void LoadVoices()
    {
        lines.clear();
        std::filesystem::path folder = VoicesFolder();
        uint32 count = 0, voiced = 0;
        if (QueryResult result = WorldDatabase.Query("SELECT `moment`, `sound`, `file`, `words` FROM `remix_voice` ORDER BY `moment`, `number`"))
        {
            do
            {
                Field* f = result->Fetch();
                std::error_code error;
                bool has = std::filesystem::file_size(folder / f[2].Get<std::string>(), error) > 44 && !error;
                lines[f[0].Get<std::string>()].push_back({ f[1].Get<uint32>(), f[3].Get<std::string>(), has });
                ++count;
                voiced += has ? 1 : 0;
            } while (result->NextRow());
        }
        LOG_INFO("module", "Wrath Remix: {} of Moratari's lines, {} with her voice ({})", count, voiced, folder.string());
    }

    bool MoratariVoice(Player* player, std::string const& moment, int32 index, Creature* moratari)
    {
        if (!player || !player->IsInWorld())
            return false;
        Line const* line = Pick(moment, index);
        if (!line)
            return false;
        if (moratari && moratari->IsInWorld() && moratari->IsWithinDistInMap(player, 40.0f))
        {
            moratari->Say(line->words, LANG_UNIVERSAL, player);
            if (line->voiced)
                moratari->PlayDirectSound(line->sound, player);
        }
        else
            Whisper(player, *line);
        return true;
    }

    uint32 MoratariVoiceFor(std::string const& words)
    {
        for (auto const& [moment, list] : lines)
            for (Line const& line : list)
                if (line.voiced && line.words == words)
                    return line.sound;
        return 0;
    }
}

namespace
{
    class RemixVoicesWorld : public WorldScript
    {
    public:
        RemixVoicesWorld() : WorldScript("RemixVoicesWorld", { WORLDHOOK_ON_STARTUP }) { }

        void OnStartup() override
        {
            if (Active())
                LoadVoices();
        }
    };

    // Clicked on, she greets them (not more often than every few seconds).
    class RemixVoicesCreature : public AllCreatureScript
    {
    public:
        RemixVoicesCreature() : AllCreatureScript("RemixVoicesCreature") { }

        bool CanCreatureGossipHello(Player* player, Creature* creature) override
        {
            if (!Active() || creature->GetEntry() != NPC_MORATARI || IsBot(player))
                return false;
            time_t now = GameTime::GetGameTime().count();
            time_t& last = lastGreeting[player->GetGUID().GetCounter()];
            if (now - last >= GREETING_EVERY)
            {
                last = now;
                MoratariVoice(player, "greet", -1, creature);
            }
            return false;   // (her menu as ever)
        }

        // Eternus's first answer to "What do you want from me?" (The Plan's credit for it, given as
        // the answer is chosen): Moratari's word on it.
        bool CanCreatureGossipSelect(Player* player, Creature* creature, uint32 /*sender*/, uint32 /*action*/) override
        {
            if (!Active() || creature->GetEntry() != NPC_ETERNUS || IsBot(player) || player->GetQuestStatus(QUEST_THE_PLAN) != QUEST_STATUS_INCOMPLETE ||
                player->GetReqKillOrCastCurrentCount(QUEST_THE_PLAN, NPC_PLAN_WHAT))
                return false;
            ObjectGuid guid = player->GetGUID();
            player->m_Events.AddEventAtOffset([guid]()
            {
                Player* p = ObjectAccessor::FindPlayer(guid);
                if (p && p->IsInWorld() && (p->GetReqKillOrCastCurrentCount(QUEST_THE_PLAN, NPC_PLAN_WHAT) || p->GetQuestStatus(QUEST_THE_PLAN) == QUEST_STATUS_COMPLETE))
                    SayLater(p, "plan_reply", 0, 2s);
            }, 500ms);
            return false;
        }
    };

    class RemixVoicesPlayer : public PlayerScript
    {
    public:
        RemixVoicesPlayer() : PlayerScript("RemixVoicesPlayer", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT,
            PLAYERHOOK_ON_LEVEL_CHANGED, PLAYERHOOK_ON_PLAYER_COMPLETE_QUEST, PLAYERHOOK_ON_PLAYER_QUEST_ACCEPT }) { }

        // Back after days away: a welcome, and if they're out in the war, a call to the Bazaar.
        void OnPlayerLogin(Player* player) override
        {
            if (!Active() || IsBot(player))
                return;
            QueryResult result = CharacterDatabase.Query("SELECT `logout_time` FROM `characters` WHERE `guid` = {}", player->GetGUID().GetCounter());
            time_t away = result ? GameTime::GetGameTime().count() - time_t(result->Fetch()[0].Get<uint32>()) : 0;
            if (!result || !result->Fetch()[0].Get<uint32>() || away < AWAY_FOR)
                return;
            ObjectGuid guid = player->GetGUID();
            player->m_Events.AddEventAtOffset([guid]()
            {
                Player* p = ObjectAccessor::FindPlayer(guid);
                if (!p || !p->IsInWorld())
                    return;
                MoratariVoice(p, "welcome_back");
                if (!AtTheBazaar(p))
                    p->m_Events.AddEventAtOffset([guid]()
                    {
                        if (Player* q = ObjectAccessor::FindPlayer(guid); q && q->IsInWorld())
                            MoratariVoice(q, "catch_up");
                    }, 6s);
            }, 8s);
        }

        void OnPlayerLogout(Player* player) override
        {
            lastGreeting.erase(player->GetGUID().GetCounter());
        }

        // Every tenth level a word from her, and the last level its own.
        void OnPlayerLevelChanged(Player* player, uint8 oldLevel) override
        {
            uint8 level = player->GetLevel();
            if (!Active() || IsBot(player) || level <= oldLevel || level < 20 || level % 10 != 0)
                return;
            if (level >= 80)
                MoratariVoice(player, "level80");
            else
                MoratariVoice(player, "milestone", (level / 10) % 2);
        }

        // Sent on past part of the war (a transition), or a death knight past the Bazaar's lessons.
        void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
        {
            if (!Active() || IsBot(player))
                return;
            uint32 id = quest->GetQuestId();
            if (Bridge const* bridge = BridgeFor(id))
                MoratariVoice(player, bridge->map != 0xFFFF ? "portal" : "skip");
            else if (id == QUEST_WHERE_KINGS_WALK || id == QUEST_WARCHIEFS_BLESSING)
                MoratariVoice(player, "skip_training");
            // (once each: the quests are)
            else if (id == QUEST_OUT_OF_TIME)
            {
                SayLater(player, "eternus_praise", 0, 3s);
                SayLater(player, "eternus_praise", 1, 13s);
            }
            else if (id == QUEST_THE_PLAN)
                SayLater(player, "plan_ends", 0, 3s);
            else if (id == QUEST_RECORD_KEEPS_WARSONG ||
                (id == QUEST_LOST_AT_SEA && player->GetQuestRewardStatus(QUEST_FORGED_ORDERS)) ||
                (id == QUEST_FORGED_ORDERS && player->GetQuestRewardStatus(QUEST_LOST_AT_SEA)))
                SayLater(player, "put_back", 0, 3s);
        }

        // Sylvanas sends them back to ask Eternus, after Mystery of the Infinite.
        void OnPlayerQuestAccept(Player* player, Quest const* quest) override
        {
            if (Active() && !IsBot(player) && (quest->GetQuestId() == QUEST_ASK_ETERNUS_ALLIANCE || quest->GetQuestId() == QUEST_ASK_ETERNUS_HORDE))
                SayLater(player, "back_to_eternus", 0, 4s);
        }
    };
}

void AddRemixVoiceScripts()
{
    new RemixVoicesWorld();
    new RemixVoicesCreature();
    new RemixVoicesPlayer();
}
