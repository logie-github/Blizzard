// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix's guide (WrathRemix.Guide): every Timerunner always knows where to go next. A few
 * times a minute it works out their next step and puts a flag on their map and minimap there (the
 * game's own point of interest, as a guard gives directions), and as the step changes it says so in
 * a line of chat:
 *
 *   - the quest they're on (the story's first, then one ready to turn in, then the first in the log):
 *     its next objective, at the nearest of its creatures or objects they can see (for an item, the
 *     quest's own points of interest), or, its objectives done, the one who takes it back;
 *   - nothing in the log: the nearest one with a quest for them (the story's first, wherever it is).
 *
 * Who can be seen follows the story's visibility conditions (the world database's, type 30), so the
 * flag goes to the Moratari or the ranger the Timerunner can find, not another one. Every quest is
 * guided this way, the game's own as much as the story's.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "QueryResult.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "StringFormat.h"
#include "WorldPacket.h"
#include <cmath>
#include <map>
#include <mutex>
#include <unordered_map>

using namespace WrathRemix;

namespace
{
    constexpr uint32 POI_FLAGS = 99;            // as the game's guards send theirs
    constexpr uint32 POI_ICON_FLAG = 7;         // the red flag
    constexpr float NEAR_ENOUGH = 600.0f;       // how far to look for a quest when the log is empty

    bool enabled = true;

    struct Spawn
    {
        uint32 entry;
        uint32 map;
        uint32 phaseMask;
        ObjectGuid::LowType guid;
        float x, y, z;
    };

    struct VisibilityCondition
    {
        uint32 elseGroup, type, value1, value2;
        bool negative;
    };

    std::unordered_map<uint32, std::vector<Spawn>> creatureSpawns, objectSpawns;
    std::unordered_map<uint32, std::vector<uint32>> questStarters, questEnders;     // quest: creatures
    std::vector<std::pair<uint32, uint32>> starts;                                  // (quest, creature)
    std::unordered_map<uint32, int32> chapterLevels;    // quests shown at the Timerunner's level: their chapter's
    std::map<std::pair<uint32, ObjectGuid::LowType>, std::vector<VisibilityCondition>> visibility;

    // Where a Timerunner is pointed, and the step they were last told about.
    struct Pointed
    {
        std::string step;
        float x = 0, y = 0;
        uint32 map = 0;
    };
    std::mutex pointedLock;
    std::unordered_map<ObjectGuid::LowType, Pointed> pointed;

    void Load()
    {
        creatureSpawns.clear();
        objectSpawns.clear();
        questStarters.clear();
        questEnders.clear();
        starts.clear();
        chapterLevels.clear();
        visibility.clear();
        enabled = sConfigMgr->GetOption<bool>("WrathRemix.Guide", true, false);
        if (!Active() || !enabled)
            return;
        for (auto const& [guid, data] : sObjectMgr->GetAllCreatureData())
            creatureSpawns[data.id].push_back({ data.id, data.mapid, data.phaseMask, guid, data.posX, data.posY, data.posZ });
        for (auto const& [guid, data] : sObjectMgr->GetAllGOData())
            objectSpawns[data.id].push_back({ data.id, data.mapid, data.phaseMask, guid, data.posX, data.posY, data.posZ });
        for (auto const& [creature, quest] : *sObjectMgr->GetCreatureQuestRelationMap())
        {
            questStarters[quest].push_back(creature);
            starts.emplace_back(quest, creature);
        }
        for (auto const& [creature, quest] : *sObjectMgr->GetCreatureQuestInvolvedRelationMap())
            questEnders[quest].push_back(creature);
        if (QueryResult result = WorldDatabase.Query("SELECT `ID`, CAST(`QuestLevel` AS SIGNED) FROM `remix_quest_level`"))
        {
            do
            {
                Field* f = result->Fetch();
                chapterLevels[f[0].Get<uint32>()] = int32(f[1].Get<int64>());
            } while (result->NextRow());
        }
        if (QueryResult result = WorldDatabase.Query("SELECT `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`, "
            "`ConditionValue1`, `ConditionValue2`, `NegativeCondition` FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND `SourceGroup` = 0"))
        {
            do
            {
                Field* f = result->Fetch();
                visibility[{ f[0].Get<uint32>(), f[1].Get<uint32>() }].push_back(
                    { f[2].Get<uint32>(), f[3].Get<uint32>(), f[4].Get<uint32>(), f[5].Get<uint32>(), f[6].Get<uint8>() != 0 });
            } while (result->NextRow());
        }
        LOG_INFO("module", "Wrath Remix guide: {} creatures' and {} objects' spawns, {} quest givers' quests, {} visibility rules",
            creatureSpawns.size(), objectSpawns.size(), starts.size(), visibility.size());
    }

    // The story's visibility conditions for a creature's spawn, as the core holds them: the spawn's
    // own, or its entry's; one else-group whose conditions all hold is enough.
    bool Sees(Player* player, Spawn const& spawn)
    {
        if (!(spawn.phaseMask & player->GetPhaseMask()))
            return false;
        auto it = visibility.find({ spawn.entry, spawn.guid });
        if (it == visibility.end())
            it = visibility.find({ spawn.entry, 0 });
        if (it == visibility.end())
            return true;
        std::map<uint32, bool> groups;
        for (VisibilityCondition const& c : it->second)
        {
            bool holds = true;
            QuestStatus status = player->GetQuestStatus(c.value1);
            switch (c.type)
            {
                case 8:  holds = player->GetQuestRewardStatus(c.value1); break;                        // rewarded
                case 9:  holds = status == QUEST_STATUS_INCOMPLETE; break;                             // taken
                case 14: holds = status == QUEST_STATUS_NONE; break;                                   // none
                case 28: holds = status == QUEST_STATUS_COMPLETE; break;                               // complete
                case 47: holds = (c.value2 & (1u << uint32(status))) != 0; break;                      // state
                default: break;
            }
            if (c.negative)
                holds = !holds;
            auto [group, inserted] = groups.emplace(c.elseGroup, holds);
            if (!inserted)
                group->second = group->second && holds;
        }
        for (auto const& [group, holds] : groups)
            if (holds)
                return true;
        return false;
    }

    struct Target
    {
        bool found = false;
        std::string step;       // what the chat line says
        std::string name;       // the flag's label
        float x = 0, y = 0;
    };

    // The nearest spawn of any of [entries] the Timerunner can see on their map.
    Spawn const* Nearest(Player* player, std::unordered_map<uint32, std::vector<Spawn>> const& spawns, std::vector<uint32> const& entries,
        float within = 0.0f)
    {
        Spawn const* best = nullptr;
        float bestDistance = 0;
        for (uint32 entry : entries)
        {
            auto it = spawns.find(entry);
            if (it == spawns.end())
                continue;
            for (Spawn const& spawn : it->second)
            {
                if (spawn.map != player->GetMapId() || !Sees(player, spawn))
                    continue;
                float d = player->GetExactDist(spawn.x, spawn.y, spawn.z);
                if (within > 0 && d > within)
                    continue;
                if (!best || d < bestDistance)
                {
                    best = &spawn;
                    bestDistance = d;
                }
            }
        }
        return best;
    }

    std::string CreatureName(uint32 entry)
    {
        CreatureTemplate const* t = sObjectMgr->GetCreatureTemplate(entry);
        return t ? t->Name : std::string("someone");
    }

    // A credit the story gives (never spawned), as whom the Timerunner goes to for it.
    uint32 ResolveCredit(Player* player, uint32 entry)
    {
        switch (entry)
        {
            case NPC_INSTRUCTOR_CREDIT:
            {
                switch (player->getClass())
                {
                    case CLASS_WARRIOR:      return 770101;
                    case CLASS_PALADIN:      return IsAlliance(player) ? 770102 : 770103;
                    case CLASS_HUNTER:       return 770104;
                    case CLASS_ROGUE:        return 770105;
                    case CLASS_PRIEST:       return 770106;
                    case CLASS_DEATH_KNIGHT: return 770107;
                    case CLASS_SHAMAN:       return 770108;
                    case CLASS_MAGE:         return 770109;
                    case CLASS_WARLOCK:      return 770110;
                    case CLASS_DRUID:        return 770111;
                    default:                 return entry;
                }
            }
            case NPC_ANOMALY_CREDIT: return NPC_MORATARI;   // she lets them through
            case NPC_PLAN_WHAT:                             // the plan: Eternus's answers
            case NPC_PLAN_HOW:
            case NPC_PLAN_WHY: return NPC_ETERNUS;
            case NPC_LESSON_CREDIT:                         // a class lesson's abilities: on the yard's dummies
            case NPC_LESSON_CREDIT + 1:
            case NPC_LESSON_CREDIT + 2: return NPC_TRAINING_DUMMY;
            case 770037: return NPC_SYLVANAS;               // the goodbyes
            case 770038: return NPC_ALLERIA;
            case 770039: return NPC_ANDORMU;
            case 770040: return NPC_NOZARI;
            default:
                // (what the Timerunner says to someone, remix_talk: whom they say it to)
                if (uint32 npc = TalkCreditNpc(entry))
                    return npc;
                return entry;
        }
    }

    Target At(Spawn const* spawn, std::string name, std::string step)
    {
        Target t;
        if (!spawn)
            return t;
        t.found = true;
        t.x = spawn->x;
        t.y = spawn->y;
        t.name = std::move(name);
        t.step = std::move(step);
        return t;
    }

    // The quest's own points of interest (the world database's quest_poi), nearest first: for
    // objectives the guide can't place by a spawn (items, a creature only ever summoned).
    Target FromPoi(Player* player, Quest const* quest, bool turnIn, std::string step)
    {
        Target t;
        QuestPOIVector const* pois = sObjectMgr->GetQuestPOIVector(quest->GetQuestId());
        if (!pois)
            return t;
        float bestDistance = 0;
        for (QuestPOI const& poi : *pois)
        {
            if (poi.MapId != player->GetMapId() || poi.points.empty() || (turnIn != (poi.ObjectiveIndex < 0)))
                continue;
            float x = 0, y = 0;
            for (QuestPOIPoint const& p : poi.points)
            {
                x += float(p.x);
                y += float(p.y);
            }
            x /= float(poi.points.size());
            y /= float(poi.points.size());
            float d = player->GetExactDist2d(x, y);
            if (!t.found || d < bestDistance)
            {
                t.found = true;
                t.x = x;
                t.y = y;
                bestDistance = d;
            }
        }
        if (t.found)
        {
            t.name = quest->GetTitle();
            t.step = std::move(step);
        }
        return t;
    }

    // The quest the Timerunner is on: the story's first, then one ready to turn in, then the first.
    Quest const* Focus(Player* player)
    {
        Quest const* story = nullptr;
        Quest const* ready = nullptr;
        Quest const* first = nullptr;
        for (uint16 slot = 0; slot < MAX_QUEST_LOG_SIZE; ++slot)
        {
            uint32 id = player->GetQuestSlotQuestId(slot);
            Quest const* quest = id ? sObjectMgr->GetQuestTemplate(id) : nullptr;
            if (!quest)
                continue;
            if (!story && id >= 77000 && id <= 77999 && !IsLesson(id) && !IsRomance(id) && !IsUnrisen(id))
                story = quest;
            if (!ready && player->GetQuestStatus(id) == QUEST_STATUS_COMPLETE)
                ready = quest;
            if (!first)
                first = quest;
        }
        return story ? story : ready ? ready : first;
    }

    // Who takes it back from this Timerunner. The Bazaar's instructors all take back Old Habits, but
    // each only from their own class (src/RemixNpcs.cpp): the Timerunner's own.
    std::vector<uint32> EndersFor(Player* player, std::vector<uint32> const& enders)
    {
        std::vector<uint32> theirs;
        for (uint32 entry : enders)
            if (entry < NPC_INSTRUCTOR_FIRST || entry > NPC_INSTRUCTOR_LAST || TeachesClassOf(entry, player))
                theirs.push_back(entry);
        return theirs;
    }

    Target TurnIn(Player* player, Quest const* quest)
    {
        auto enders = questEnders.find(quest->GetQuestId());
        if (enders != questEnders.end())
            if (Spawn const* spawn = Nearest(player, creatureSpawns, EndersFor(player, enders->second)))
                return At(spawn, CreatureName(spawn->entry),
                    Acore::StringFormat("{}: take it back to {}.", quest->GetTitle(), CreatureName(spawn->entry)));
        return FromPoi(player, quest, true, Acore::StringFormat("{}: turn it in where your map shows.", quest->GetTitle()));
    }

    Target ForQuest(Player* player, Quest const* quest)
    {
        uint32 id = quest->GetQuestId();
        if (player->GetQuestStatus(id) == QUEST_STATUS_COMPLETE)
            return TurnIn(player, quest);

        uint16 slot = player->FindQuestSlot(id);
        for (uint8 i = 0; i < QUEST_OBJECTIVES_COUNT; ++i)
        {
            int32 npcOrGo = quest->RequiredNpcOrGo[i];
            if (!npcOrGo || player->GetQuestSlotCounter(slot, i) >= quest->RequiredNpcOrGoCount[i])
                continue;
            std::string what = !quest->ObjectiveText[i].empty() ? quest->ObjectiveText[i] : std::string();
            if (npcOrGo > 0)
            {
                // (somewhere the quest sends them to see for themselves, remix_place)
                uint32 placeMap = 0;
                float placeX = 0.0f, placeY = 0.0f;
                if (PlaceOf(id, uint32(npcOrGo), placeMap, placeX, placeY) && placeMap == player->GetMapId())
                {
                    Target t;
                    t.found = true;
                    t.x = placeX;
                    t.y = placeY;
                    t.name = quest->GetTitle();
                    t.step = Acore::StringFormat("{}: {}.", quest->GetTitle(), what.empty() ? "where your map shows" : what);
                    return t;
                }
                uint32 entry = ResolveCredit(player, uint32(npcOrGo));
                if (Spawn const* spawn = Nearest(player, creatureSpawns, { entry }))
                {
                    std::string name = CreatureName(entry);
                    return At(spawn, name, Acore::StringFormat("{}: {} ({} of {}).", quest->GetTitle(), what.empty() ? name : what,
                        player->GetQuestSlotCounter(slot, i), quest->RequiredNpcOrGoCount[i]));
                }
            }
            else if (Spawn const* spawn = Nearest(player, objectSpawns, { uint32(-npcOrGo) }))
            {
                GameObjectTemplate const* t = sObjectMgr->GetGameObjectTemplate(uint32(-npcOrGo));
                std::string name = t ? t->name : std::string("it");
                return At(spawn, name, Acore::StringFormat("{}: {}.", quest->GetTitle(), what.empty() ? name : what));
            }
            // (one only ever summoned: where the quest's points of interest are, else its giver)
            Target poi = FromPoi(player, quest, false, Acore::StringFormat("{}: {}.", quest->GetTitle(), what.empty() ? "where your map shows" : what));
            if (poi.found)
                return poi;
            return TurnIn(player, quest);
        }
        for (uint8 i = 0; i < QUEST_ITEM_OBJECTIVES_COUNT; ++i)
            if (quest->RequiredItemId[i] && player->GetItemCount(quest->RequiredItemId[i], true) < quest->RequiredItemCount[i])
            {
                ItemTemplate const* item = sObjectMgr->GetItemTemplate(quest->RequiredItemId[i]);
                Target poi = FromPoi(player, quest, false, Acore::StringFormat("{}: {} ({} of {}).", quest->GetTitle(),
                    item ? item->Name1 : std::string("what it asks for"), player->GetItemCount(quest->RequiredItemId[i], true), quest->RequiredItemCount[i]));
                if (poi.found)
                    return poi;
            }
        // (nothing to do but speak to someone: they're the one who takes it back)
        return TurnIn(player, quest);
    }

    // Nothing in the log: the story's next quest anywhere, else the nearest one for them.
    Target NextQuest(Player* player)
    {
        Spawn const* bestStory = nullptr;
        Spawn const* best = nullptr;
        uint32 bestStoryQuest = 0, bestQuest = 0;
        float bestStoryDistance = 0, bestDistance = 0;
        for (auto const& [questId, creature] : starts)
        {
            if (player->GetQuestStatus(questId) != QUEST_STATUS_NONE)
                continue;
            Quest const* quest = sObjectMgr->GetQuestTemplate(questId);
            if (!quest || quest->IsRepeatable() || quest->IsSeasonal())
                continue;
            // (Moratari's own story is the Timerunner's to start, or not, and the hidden plate theirs to
            // find: never pointed to)
            if (IsRomance(questId) || IsUnrisen(questId))
                continue;
            // (a class lesson is offered as the yard's instructors' other quests would be: when near)
            bool story = questId >= 77000 && questId <= 77999 && !IsLesson(questId);
            // (not the grey ones the Timerunner has outgrown: by their chapter's level, for those
            // shown at the Timerunner's own)
            int32 level = quest->GetQuestLevel();
            if (auto it = chapterLevels.find(questId); level <= 0 && it != chapterLevels.end())
                level = it->second;
            if (!story && level > 0 && level + 5 < int32(player->GetLevel()))
                continue;
            if (!player->CanTakeQuest(quest, false))
                continue;
            Spawn const* spawn = Nearest(player, creatureSpawns, { creature }, story ? 0.0f : NEAR_ENOUGH);
            if (!spawn)
                continue;
            float d = player->GetExactDist(spawn->x, spawn->y, spawn->z);
            if (story && (!bestStory || d < bestStoryDistance))
            {
                bestStory = spawn;
                bestStoryQuest = questId;
                bestStoryDistance = d;
            }
            else if (!story && (!best || d < bestDistance))
            {
                best = spawn;
                bestQuest = questId;
                bestDistance = d;
            }
        }
        Spawn const* spawn = bestStory ? bestStory : best;
        uint32 questId = bestStory ? bestStoryQuest : bestQuest;
        if (!spawn)
            return Target();
        Quest const* quest = sObjectMgr->GetQuestTemplate(questId);
        std::string name = CreatureName(spawn->entry);
        return At(spawn, name, Acore::StringFormat("{} has your next quest{}.", name,
            quest ? Acore::StringFormat(", {}", quest->GetTitle()) : std::string()));
    }

    void Point(Player* player, Target const& target)
    {
        WorldPacket data(SMSG_GOSSIP_POI, 4 + 4 + 4 + 4 + 4 + target.name.size() + 1);
        data << uint32(POI_FLAGS);
        data << float(target.x);
        data << float(target.y);
        data << uint32(POI_ICON_FLAG);
        data << uint32(0);
        data << target.name;
        player->SendDirectMessage(&data);
    }

    void Guide(Player* player)
    {
        if (!Active() || !enabled || IsBot(player) || player->IsBeingTeleported() || InIntro(player))
            return;
        Target target;
        if (Quest const* quest = Focus(player))
            target = ForQuest(player, quest);
        if (!target.found)
            target = NextQuest(player);
        if (!target.found)
            return;

        bool moved, stepped;
        {
            std::lock_guard<std::mutex> lock(pointedLock);
            Pointed& last = pointed[player->GetGUID().GetCounter()];
            moved = last.map != player->GetMapId() || std::fabs(last.x - target.x) > 3.0f || std::fabs(last.y - target.y) > 3.0f;
            stepped = last.step != target.step;
            last.map = player->GetMapId();
            last.x = target.x;
            last.y = target.y;
            last.step = target.step;
        }
        if (moved || stepped)
            Point(player, target);
        if (stepped)
            ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffNext:|r " + target.step + " |cff8fd3ff(the flag on your map)|r");
    }

    void GuideEvery(ObjectGuid guid, Milliseconds after)
    {
        Player* player = ObjectAccessor::FindConnectedPlayer(guid);
        if (!player)
            return;
        player->m_Events.AddEventAtOffset([guid]()
        {
            if (Player* p = ObjectAccessor::FindPlayer(guid); p && p->IsInWorld())
            {
                Guide(p);
                GuideEvery(guid, 4s);
            }
        }, after);
    }
}

class RemixGuideWorld : public WorldScript
{
public:
    RemixGuideWorld() : WorldScript("RemixGuideWorld", { WORLDHOOK_ON_STARTUP }) { }

    void OnStartup() override
    {
        Load();
    }
};

class RemixGuidePlayer : public PlayerScript
{
public:
    RemixGuidePlayer() : PlayerScript("RemixGuidePlayer", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOGOUT }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (!Active() || !enabled || IsBot(player))
            return;
        // (a moment after arriving: the first look tells them where they are going)
        GuideEvery(player->GetGUID(), 6s);
    }

    void OnPlayerLogout(Player* player) override
    {
        std::lock_guard<std::mutex> lock(pointedLock);
        pointed.erase(player->GetGUID().GetCounter());
    }
};

void AddRemixGuideScripts()
{
    new RemixGuideWorld();
    new RemixGuidePlayer();
}
