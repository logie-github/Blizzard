// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Brill: A Place Among the Forsaken (mod-brill-home), ChromieCraft's realm alone: the town's optional
 * questlines, each its own, made by tools/build_town.py from tools/town/*.py into the game's rows and
 * the module's tables, which this reads as the world server starts:
 * - brill_town_phase: what a questline changed in Brill for a player, by phases (a bit, and rows of
 *   conditions: any row whose every condition holds puts them in it while they're in Brill);
 * - brill_town_gossip: a creature's greetings by condition, and the options added to its menu (a quest's
 *   credit, a choice and its mark, a reply, its wares, the house's furniture);
 * - brill_town_use: an object's use (a quest's credit, words, a mark).
 *
 * - brill_town_stage: how far a project has come for a player (its stage, by conditions), and
 *   brill_town_invis: the spawns that show only from a project's stage on. The game's own invisibility
 *   carries it: a spawn is made invisible of the project's kind at the stage's level, and a player in Brill
 *   detects that kind up to the stage they've reached (so any number of stages, each project its own kind).
 *
 * A condition is a word: R<quest> rewarded, T taken (ever), A in the log, I in the log and not done, C done
 * and not turned in; F<bits> the house's flags (brill_home.flags) all set; O the house theirs; D<n> one
 * day in n (by the character and the day); U<n> the house's furniture n bought or given; "!" before any, not. A choice's mark is a quest set rewarded,
 * never given: R<mark> asks about it as any quest.
 */

#include "BrillHome.h"
#include "Chat.h"
#include "ChatCommand.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "GameTime.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "StringFormat.h"
#include "WorldSession.h"
#include <array>
#include <cmath>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace
{
    struct Cond { char kind; bool neg; uint32 value; };
    using Conds = std::vector<Cond>;

    struct PhaseRow { uint32 bit; Conds cond; };
    struct GossipRow
    {
        bool greet;
        Conds cond;
        uint8 icon;
        std::string text;
        uint32 textId;
        std::string action;
        uint32 quest, credit, marker, emote;
        std::string reply;
        uint32 arg;
    };
    // (tele: where it takes the player, map -1 nowhere)
    struct UseRow { Conds cond; uint32 quest, credit, textId, marker; int32 teleMap; float x, y, z, o; };
    struct StageRow { uint8 type; int32 value; Conds cond; };
    struct Invis { uint8 type; int32 value; };

    std::vector<PhaseRow> phases;
    std::vector<GossipRow> gossip;                                 // (its index is the option's sender, past SENDER_BASE)
    std::unordered_map<uint32, std::vector<uint32>> gossipByNpc;   // a creature's rows, in order
    std::unordered_map<uint32, std::vector<UseRow>> uses;          // an object's
    // the object spawns a character has used for a quest's credit (the quest's and the spawn's ids)
    std::unordered_map<uint32, std::unordered_set<uint64>> used;
    constexpr uint32 SENDER_BASE = 980000;
    std::vector<StageRow> stages;
    std::unordered_map<uint32, std::vector<Invis>> creatureInvis, objectInvis;   // by spawn id
    uint32 stageTypes = 0;   // the invisibility kinds the projects use (a bit each)
    // what the town has added to a character's detection of each kind (the stage reached)
    std::unordered_map<uint32, std::array<int32, TOTAL_INVISIBILITY_TYPES>> detected;

    Conds Parse(std::string const& text)
    {
        Conds out;
        std::istringstream in(text);
        std::string word;
        while (in >> word)
        {
            Cond c { 0, false, 0 };
            size_t at = 0;
            if (word[at] == '!')
            {
                c.neg = true;
                ++at;
            }
            if (at >= word.size())
                continue;
            c.kind = word[at++];
            if (at < word.size())
                c.value = uint32(std::strtoul(word.c_str() + at, nullptr, 10));
            out.push_back(c);
        }
        return out;
    }

    bool Holds(Player* player, Cond const& c)
    {
        bool yes = false;
        switch (c.kind)
        {
            case 'R': yes = player->GetQuestRewardStatus(c.value); break;
            case 'T': yes = player->GetQuestRewardStatus(c.value) || player->GetQuestStatus(c.value) != QUEST_STATUS_NONE; break;
            case 'A':
            {
                QuestStatus s = player->GetQuestStatus(c.value);
                yes = s == QUEST_STATUS_INCOMPLETE || s == QUEST_STATUS_COMPLETE;
                break;
            }
            case 'I': yes = player->GetQuestStatus(c.value) == QUEST_STATUS_INCOMPLETE; break;
            case 'C': yes = player->GetQuestStatus(c.value) == QUEST_STATUS_COMPLETE; break;
            case 'F': yes = (BrillHome::Flags(player) & c.value) == c.value; break;
            case 'O': yes = BrillHome::OwnsHouse(player); break;
            case 'U': yes = BrillHome::HasUpgrade(player, c.value); break;
            case 'D':
            {
                uint32 day = uint32(GameTime::GetGameTime().count() / 86400);
                yes = c.value && (player->GetGUID().GetCounter() + day) % c.value == 0;
                break;
            }
            default: break;
        }
        return yes != c.neg;
    }

    bool Holds(Player* player, Conds const& conds)
    {
        for (Cond const& c : conds)
            if (!Holds(player, c))
                return false;
        return true;
    }

    // How many of a credit a quest asks for (0: none).
    uint32 Required(uint32 quest, uint32 credit)
    {
        Quest const* q = sObjectMgr->GetQuestTemplate(quest);
        if (!q)
            return 0;
        for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
            if (q->RequiredNpcOrGo[i] == int32(credit))
                return q->RequiredNpcOrGoCount[i];
        return 0;
    }

    // Still wanted: the quest in the log and not done, this credit short.
    bool Wanted(Player* player, uint32 quest, uint32 credit)
    {
        if (!quest || player->GetQuestStatus(quest) != QUEST_STATUS_INCOMPLETE)
            return false;
        if (!credit)
            return true;
        return player->GetReqKillOrCastCurrentCount(quest, credit) < Required(quest, credit);
    }

    // The game's whisper hasn't the quest text's $n, $B and $g; a reply has them as quest text does.
    std::string Words(Player* player, std::string text)
    {
        std::string out;
        for (size_t i = 0; i < text.size(); ++i)
        {
            if (text[i] != '$' || i + 1 >= text.size())
            {
                out += text[i];
                continue;
            }
            char k = text[i + 1];
            if (k == 'n' || k == 'N')
            {
                out += player->GetName();
                ++i;
            }
            else if (k == 'B' || k == 'b')
            {
                out += ' ';
                ++i;
            }
            else if (k == 'g' || k == 'G')
            {
                size_t colon = text.find(':', i), semi = text.find(';', i);
                if (colon == std::string::npos || semi == std::string::npos || colon > semi)
                {
                    out += text[i];
                    continue;
                }
                out += player->getGender() == GENDER_FEMALE ? text.substr(colon + 1, semi - colon - 1) : text.substr(i + 2, colon - i - 2);
                i = semi;
            }
            else
                out += text[i];
        }
        return out;
    }

    void Mark(Player* player, uint32 marker)
    {
        if (marker && !player->GetQuestRewardStatus(marker))
            player->SetRewardedQuest(marker);
    }
}

namespace BrillTown
{
    void Load()
    {
        phases.clear();
        gossip.clear();
        gossipByNpc.clear();
        uses.clear();
        if (QueryResult r = WorldDatabase.Query("SELECT `bit`, `cond` FROM `brill_town_phase` ORDER BY `bit`, `ord`"))
            do
            {
                Field* f = r->Fetch();
                phases.push_back({ f[0].Get<uint32>(), Parse(f[1].Get<std::string>()) });
            } while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT `npc`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, "
                                                "`marker`, `emote`, `reply`, `arg` FROM `brill_town_gossip` ORDER BY `npc`, `ord`"))
            do
            {
                Field* f = r->Fetch();
                GossipRow row { f[1].Get<std::string>() == "greet", Parse(f[2].Get<std::string>()), f[3].Get<uint8>(),
                    f[4].IsNull() ? "" : f[4].Get<std::string>(), f[5].Get<uint32>(), f[6].Get<std::string>(), f[7].Get<uint32>(),
                    f[8].Get<uint32>(), f[9].Get<uint32>(), f[10].Get<uint32>(), f[11].IsNull() ? "" : f[11].Get<std::string>(), f[12].Get<uint32>() };
                gossipByNpc[f[0].Get<uint32>()].push_back(uint32(gossip.size()));
                gossip.push_back(row);
            } while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT `go`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, "
            "`tele_y`, `tele_z`, `tele_o` FROM `brill_town_use` ORDER BY `go`, `ord`"))
            do
            {
                Field* f = r->Fetch();
                uses[f[0].Get<uint32>()].push_back({ Parse(f[1].Get<std::string>()), f[2].Get<uint32>(), f[3].Get<uint32>(),
                    f[4].Get<uint32>(), f[5].Get<uint32>(), f[6].Get<int32>(), f[7].Get<float>(), f[8].Get<float>(),
                    f[9].Get<float>(), f[10].Get<float>() });
            } while (r->NextRow());
        stages.clear();
        creatureInvis.clear();
        objectInvis.clear();
        stageTypes = 0;
        if (QueryResult r = WorldDatabase.Query("SELECT `type`, `value`, `cond` FROM `brill_town_stage` ORDER BY `type`, `value`, `ord`"))
            do
            {
                Field* f = r->Fetch();
                uint8 type = f[0].Get<uint8>();
                if (type >= TOTAL_INVISIBILITY_TYPES)
                    continue;
                stages.push_back({ type, f[1].Get<int32>(), Parse(f[2].Get<std::string>()) });
                stageTypes |= 1u << type;
            } while (r->NextRow());
        if (QueryResult r = WorldDatabase.Query("SELECT `kind`, `guid`, `type`, `value` FROM `brill_town_invis`"))
            do
            {
                Field* f = r->Fetch();
                uint8 type = f[2].Get<uint8>();
                if (type >= TOTAL_INVISIBILITY_TYPES)
                    continue;
                (f[0].Get<std::string>() == "c" ? creatureInvis : objectInvis)[f[1].Get<uint32>()].push_back({ type, f[3].Get<int32>() });
            } while (r->NextRow());
        LOG_INFO("module", "Brill town: {} phase rows, {} menu rows for {} creatures, {} objects, {} stage rows, {} staged spawns",
            phases.size(), gossip.size(), gossipByNpc.size(), uses.size(), stages.size(), creatureInvis.size() + objectInvis.size());
    }

    uint32 Phases(Player* player)
    {
        uint32 mask = 0;
        for (PhaseRow const& p : phases)
            if (!(mask & p.bit) && Holds(player, p.cond))
                mask |= p.bit;
        return mask;
    }

    // The house's cellar (tools/build_town.py: CELLAR_*): its middle under the house's, its floor's height.
    // It's an object of the game's own model (the client draws it from the module's patch; the server
    // doesn't know its floor), so a player in it who has fallen through (their game without the patch, or
    // in before it was drawn) or who comes into the game down there is put back in the house, by the hatch.
    constexpr float CELLAR_X = 2275.0f, CELLAR_Y = 480.5f, CELLAR_REACH = 16.0f, CELLAR_FLOOR = -2.72f;
    constexpr float HATCH_X = 2276.74f, HATCH_Y = 478.36f, HATCH_Z = 34.26f, HATCH_O = 3.4907f;

    bool KeepOutOfTheGround(Player* player, bool login)
    {
        if (!player->IsInWorld() || player->GetMapId() != 0 || player->IsBeingTeleported() || player->IsGameMaster()
            || std::hypot(player->GetPositionX() - CELLAR_X, player->GetPositionY() - CELLAR_Y) > CELLAR_REACH)
            return false;
        float z = player->GetPositionZ();
        // (under the house: the cellar; below its floor: fallen through)
        if (z < CELLAR_FLOOR - 3.0f || (login && z < CELLAR_FLOOR + 10.0f))
        {
            player->TeleportTo(0, HATCH_X, HATCH_Y, HATCH_Z, HATCH_O);
            return true;
        }
        return false;
    }

    void Forget(Player* player)
    {
        used.erase(player->GetGUID().GetCounter());
        detected.erase(player->GetGUID().GetCounter());
    }

    // The projects' stages the player has reached, detected in Brill (none outside it).
    void RefreshStages(Player* player, bool inBrill)
    {
        if (!stageTypes)
            return;
        int32 reached[TOTAL_INVISIBILITY_TYPES] = { };
        if (inBrill)
            for (StageRow const& s : stages)
                if (s.value > reached[s.type] && Holds(player, s.cond))
                    reached[s.type] = s.value;
        // (added to whatever the game's own detection auras give, as an aura's amount is, and taken back out
        // by the same amount: never touching what isn't the town's)
        auto& ours = detected[player->GetGUID().GetCounter()];
        bool changed = false;
        for (uint8 t = 0; t < TOTAL_INVISIBILITY_TYPES; ++t)
        {
            if (!(stageTypes & (1u << t)))
                continue;
            InvisibilityType type = InvisibilityType(t);
            if (reached[t] != ours[t])
            {
                player->m_invisibilityDetect.AddValue(type, reached[t] - ours[t]);
                ours[t] = reached[t];
                changed = true;
            }
            bool has = player->m_invisibilityDetect.HasFlag(type);
            if (reached[t] > 0 && !has)
            {
                player->m_invisibilityDetect.AddFlag(type);
                changed = true;
            }
            else if (reached[t] == 0 && has && !player->HasInvisibilityDetectAura())
            {
                player->m_invisibilityDetect.DelFlag(type);
                changed = true;
            }
        }
        if (changed)
            player->UpdateObjectVisibility();
    }

    uint32 AddOptions(Player* player, Creature* creature)
    {
        auto it = gossipByNpc.find(creature->GetEntry());
        if (!BrillHome::Enabled() || it == gossipByNpc.end())
            return 0;
        uint32 text = 0;
        for (uint32 index : it->second)
        {
            GossipRow const& g = gossip[index];
            if (!Holds(player, g.cond))
                continue;
            if (g.greet)
            {
                if (!text)
                    text = g.textId;
                continue;
            }
            if ((g.action == "credit" || g.action == "choice" || g.action == "furnish") && g.quest && !Wanted(player, g.quest, g.credit))
                continue;
            if (g.marker && player->GetQuestRewardStatus(g.marker))
                continue;
            if (g.action == "buy")
                AddGossipItemFor(player, g.icon, g.text, SENDER_BASE + index, 0, "Buy it?", g.arg, false);
            else
                AddGossipItemFor(player, g.icon, g.text, SENDER_BASE + index, 0);
        }
        return text;
    }
}

namespace
{
    // The town's creatures, and the game's own the town's lines add options to: their own menu (its quests,
    // its trainer or wares), the line's greeting for the player and its options.
    class BrillTownGossip : public AllCreatureScript
    {
    public:
        BrillTownGossip() : AllCreatureScript("BrillTownGossip") { }

        bool CanCreatureGossipHello(Player* player, Creature* creature) override
        {
            if (!BrillHome::Enabled())
                return false;
            // (one with a script of its own, Jamie Nore's or Carolai's, adds the town's options itself:
            // BrillTown::AddOptions)
            if (!gossipByNpc.count(creature->GetEntry()) || creature->GetScriptName().starts_with("npc_brill_home_"))
                return false;
            player->PrepareGossipMenu(creature, creature->GetCreatureTemplate()->GossipMenuId, true);
            uint32 text = BrillTown::AddOptions(player, creature);
            SendGossipMenuFor(player, text ? text : player->GetGossipTextId(creature), creature->GetGUID());
            return true;
        }

        bool CanCreatureGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
        {
            if (!BrillHome::Enabled())
                return false;
            if (sender == BrillHome::SENDER_BUY && gossipByNpc.count(creature->GetEntry()))
            {
                CloseGossipMenuFor(player);
                BrillHome::BuyUpgrade(player, creature, action);
                return true;
            }
            if (sender < SENDER_BASE || sender - SENDER_BASE >= gossip.size())
                return false;
            GossipRow const& g = gossip[sender - SENDER_BASE];
            if (!Holds(player, g.cond))
            {
                CloseGossipMenuFor(player);
                return true;
            }
            if (g.action == "vendor")
            {
                player->GetSession()->SendListInventory(creature->GetGUID());
                return true;
            }
            if (g.action == "upgrades")
            {
                BrillHome::SendUpgrades(player, creature);
                return true;
            }
            CloseGossipMenuFor(player);
            // (a purchase: its price, its mark; once)
            if (g.action == "buy")
            {
                if (g.marker && player->GetQuestRewardStatus(g.marker))
                    return true;
                if (!player->HasEnoughMoney(g.arg))
                {
                    creature->Whisper("You'll need a little more coin than that.", LANG_UNIVERSAL, player);
                    return true;
                }
                player->ModifyMoney(-int32(g.arg));
                Mark(player, g.marker);
                if (g.emote)
                    creature->HandleEmoteCommand(g.emote);
                if (!g.reply.empty())
                    creature->Whisper(Words(player, g.reply), LANG_UNIVERSAL, player);
                BrillHome::RefreshPhases(player);
                return true;
            }
            if (g.action == "credit" || g.action == "choice" || g.action == "furnish")
            {
                if (g.quest && !Wanted(player, g.quest, g.credit))
                    return true;
                if (g.action == "furnish" && !BrillHome::GiveUpgrade(player, g.arg))
                    return true;
                Mark(player, g.marker);
                if (g.credit)
                    player->KilledMonsterCredit(g.credit);
            }
            else
                Mark(player, g.marker);
            if (g.emote)
                creature->HandleEmoteCommand(g.emote);
            if (!g.reply.empty())
                creature->Whisper(Words(player, g.reply), LANG_UNIVERSAL, player);
            BrillHome::RefreshPhases(player);
            return true;
        }
    };

    // A project's spawns: invisible of its kind at the stage they show from (each of its projects').
    template <class T>
    void Stage(T* object, std::unordered_map<uint32, std::vector<Invis>> const& table)
    {
        auto it = table.find(object->GetSpawnId());
        if (it == table.end())
            return;
        for (Invis const& i : it->second)
        {
            object->m_invisibility.AddFlag(InvisibilityType(i.type));
            object->m_invisibility.SetValue(InvisibilityType(i.type), i.value);
        }
    }

    class BrillTownStagedCreatures : public AllCreatureScript
    {
    public:
        BrillTownStagedCreatures() : AllCreatureScript("BrillTownStagedCreatures") { }
        void OnCreatureAddWorld(Creature* creature) override
        {
            if (BrillHome::Enabled())
                Stage(creature, creatureInvis);
        }
    };

    class BrillTownStagedObjects : public AllGameObjectScript
    {
    public:
        BrillTownStagedObjects() : AllGameObjectScript("BrillTownStagedObjects") { }
        void OnGameObjectAddWorld(GameObject* go) override
        {
            if (BrillHome::Enabled())
                Stage(go, objectInvis);
        }
    };

    // A quest taken again (a repeatable one) can be done from the same objects again.
    class BrillTownQuests : public PlayerScript
    {
    public:
        BrillTownQuests() : PlayerScript("BrillTownQuests", { PLAYERHOOK_ON_PLAYER_QUEST_ACCEPT }) { }
        void OnPlayerQuestAccept(Player* player, Quest const* quest) override
        {
            auto it = used.find(player->GetGUID().GetCounter());
            if (it == used.end())
                return;
            uint64 lo = uint64(quest->GetQuestId()) << 32, hi = lo | 0xFFFFFFFFull;
            for (auto u = it->second.begin(); u != it->second.end();)
                u = (*u >= lo && *u <= hi) ? it->second.erase(u) : std::next(u);
        }
    };

    // The town's objects: the first of an object's rows whose conditions hold and that has something to do
    // (a credit still wanted, from this spawn not used yet; or words, or a mark).
    class go_brill_town : public GameObjectScript
    {
    public:
        go_brill_town() : GameObjectScript("go_brill_town") { }

        bool OnGossipHello(Player* player, GameObject* go) override
        {
            if (!BrillHome::Enabled())
                return false;
            auto it = uses.find(go->GetEntry());
            if (it == uses.end())
                return false;
            auto& mine = used[player->GetGUID().GetCounter()];
            for (UseRow const& u : it->second)
            {
                if (!Holds(player, u.cond))
                    continue;
                if (u.quest || u.credit)
                {
                    uint64 key = (uint64(u.quest) << 32) | go->GetSpawnId();
                    if (!Wanted(player, u.quest, u.credit) || mine.count(key))
                        continue;
                    mine.insert(key);
                    if (u.credit)
                        player->KilledMonsterCredit(u.credit);
                }
                Mark(player, u.marker);
                if (u.textId)
                {
                    ClearGossipMenuFor(player);
                    SendGossipMenuFor(player, u.textId, go->GetGUID());
                }
                else if (u.teleMap >= 0)
                    CloseGossipMenuFor(player);
                BrillHome::RefreshPhases(player);
                // (the house's hatch and the cellar's ladder)
                if (u.teleMap >= 0)
                    player->TeleportTo(uint32(u.teleMap), u.x, u.y, u.z, u.o);
                return true;
            }
            return true;
        }
    };

    using namespace Acore::ChatCommands;

    // Game masters' (CI's realm test): .brilltown state says the town's phases that are the character's and
    // which of the town's quests and marks are done; .brilltown use uses the nearest of the town's objects
    // (10 yards), as clicking it does.
    class BrillTownCommands : public CommandScript
    {
    public:
        BrillTownCommands() : CommandScript("BrillTownCommands") { }

        ChatCommandTable GetCommands() const override
        {
            static ChatCommandTable town =
            {
                { "state", HandleState, SEC_GAMEMASTER, Console::No },
                { "use", HandleUse, SEC_GAMEMASTER, Console::No },
                { "grant", HandleGrant, SEC_GAMEMASTER, Console::No },
            };
            static ChatCommandTable root = { { "brilltown", town } };
            return root;
        }

        static bool HandleState(ChatHandler* handler)
        {
            Player* player = handler->GetSession()->GetPlayer();
            BrillHome::RefreshPhases(player);
            std::string done;
            for (uint32 id = 970200; id < 971700; ++id)
                if (player->GetQuestRewardStatus(id))
                    done += " q" + std::to_string(id);
            // (the town's phases each in brackets: [0x40000])
            std::string bits;
            uint32 town = BrillTown::Phases(player);
            for (uint32 b = 0; b < 32; ++b)
                if (town & (1u << b))
                    bits += Acore::StringFormat(" [0x{:X}]", 1u << b);
            for (uint8 t = 0; t < TOTAL_INVISIBILITY_TYPES; ++t)
                if (stageTypes & (1u << t))
                    bits += Acore::StringFormat(" <{}:{}>", t, player->m_invisibilityDetect.HasFlag(InvisibilityType(t))
                        ? player->m_invisibilityDetect.GetValue(InvisibilityType(t)) : 0);
            handler->PSendSysMessage("Brill town: phases 0x{:X} town{} done{}", player->GetPhaseMask(), bits, done);
            return true;
        }

        // .brilltown grant QUEST: a quest set done, as a choice's mark is (a test's shortcut past a line's prerequisites).
        static bool HandleGrant(ChatHandler* handler, uint32 quest)
        {
            Player* player = handler->GetSession()->GetPlayer();
            if (!sObjectMgr->GetQuestTemplate(quest))
            {
                handler->PSendSysMessage("Brill town: no quest {}", quest);
                return true;
            }
            Mark(player, quest);
            BrillHome::RefreshPhases(player);
            handler->PSendSysMessage("Brill town: granted {}", quest);
            return true;
        }

        static bool HandleUse(ChatHandler* handler)
        {
            Player* player = handler->GetSession()->GetPlayer();
            GameObject* best = nullptr;
            for (auto const& [entry, _] : uses)
                if (GameObject* go = player->FindNearestGameObject(entry, 10.0f))
                    if (!best || player->GetDistance(go) < player->GetDistance(best))
                        best = go;
            if (!best)
            {
                handler->SendSysMessage("Brill town: nothing to use within 10 yards.");
                return true;
            }
            best->Use(player);
            handler->PSendSysMessage("Brill town: used {}", best->GetEntry());
            return true;
        }
    };
}

namespace BrillTown
{
    void AddScripts()
    {
        new BrillTownGossip();
        new go_brill_town();
        new BrillTownCommands();
        new BrillTownStagedCreatures();
        new BrillTownStagedObjects();
        new BrillTownQuests();
    }
}
