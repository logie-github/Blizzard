// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Murlocs and the Naga (mod-murloc-naga): two races of ChromieCraft's realm, the murlocs
 * (Alliance, race 19) starting in the Wrathtail's pens at the Zoram Strand and the naga (Horde, race
 * 20) at Rethress Sanctum in Azshara, both at level 10, each with a story of its own to level 55 (the
 * murlocs' tools/murloc/, the naga's tools/naga/: their SQL) and no one else's quests until its last
 * quest is done (each story's gate, made here as the world starts). The naga live Warcraft III's war
 * as memories: going in and out, a death or a logout inside, leaving a memory's ground (here). The
 * world database has them from the module's SQL (data/sql/chromiecraft/world, tools/build_data.py;
 * ctl.sh puts it in ChromieCraft's world database alone); the game, from the patch this makes as the
 * configuration is read (MurlocNagaPatch.cpp) in the client WOW_CLIENT_DIR names (ctl.sh).
 *
 * The patch is made first of the race modules' (they're read by the game after it and made from
 * the game with it in, so they carry its rows): before the Worgen and Goblins' (made as the
 * configuration is about to be read too, its script registered after this one's: the modules are
 * loaded in their folders' order), the allied races', Wrath Remix's and the Skyborne's.
 *
 * They start at level 10, away from their kin's trainers: they learn their class's trainer spells
 * as they come of age for them (at creation and every level, as the trainers would teach them;
 * talents' ranks once the talent is theirs); the murlocs, from their story's trainers.
 */

#include "CellImpl.h"
#include "Config.h"
#include "DatabaseEnv.h"
#include "DBCStores.h"
#include "GridNotifiers.h"
#include "GridNotifiersImpl.h"
#include "Group.h"
#include "Log.h"
#include "MurlocNagaPatch.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ReputationMgr.h"
#include "ScriptMgr.h"
#include "SpellAuras.h"
#include "SpellInfo.h"
#include "SpellMgr.h"
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <map>
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace fs = std::filesystem;

namespace
{
    constexpr uint8 RACE_MURLOC = 19, RACE_NAGA = 20, START_LEVEL = 10;
    constexpr uint32 MURLOC_RACE_BIT = 1u << (RACE_MURLOC - 1), NAGA_RACE_BIT = 1u << (RACE_NAGA - 1);

    // The towns' factions a murloc starts with (tools/build_data.py's MURLOC_HOSTILE_FACTIONS): the Alliance's
    // and the Horde's Hostile (at war: their guards attack it, and it them), the goblins' Unfriendly (mercenary:
    // they don't trade with it, nor attack it).
    constexpr int32 MURLOC_START_STANDING = -3500, MURLOC_GOBLIN_STANDING = -500;
    uint32 const MURLOC_HOSTILE_FACTIONS[] = { 469, 72, 47, 69, 54, 930, 67, 76, 81, 68, 530, 911, 169, 21, 369, 470, 577 };
    uint32 const GOBLIN_FACTIONS[] = { 169, 21, 369, 470, 577 };
    uint32 const ALLIANCE_FACTIONS[] = { 469, 72, 47, 69, 54, 930 };

    int32 StartStanding(uint32 faction)
    {
        for (uint32 id : GOBLIN_FACTIONS)
            if (id == faction)
                return MURLOC_GOBLIN_STANDING;
        return MURLOC_START_STANDING;
    }

    // A story's graveyards (its SQL's table): where one of its race whose story isn't done wakes as a ghost, the
    // nearest on its map whose quest rule holds, never a town's.
    struct StoryGraveyard
    {
        uint32 id, map;
        float x, y, z;
        uint32 fromQuest, untilQuest;
    };

    // A race's story as its SQL leaves it in the world database (tools/murloc/compile.py, a profile each): its
    // quests' range, its last quest (its gate opens with it), its graveyards, the spells its quests teach and the
    // auras what one carries puts on.
    struct Story
    {
        uint8 race;
        uint32 raceBit;
        uint32 gateOffset;                      // (its gate's alternative condition groups: the quest's own, + this)
        uint32 sideMask;                        // (its side's quests open to all the side's races: its own too)
        char const* name;
        char const* storyTable;
        char const* learnTable;
        char const* graveyardTable;
        char const* carryTable;
        uint32 finalQuest = 0, firstQuest = 0, lastQuest = 0;
        std::vector<StoryGraveyard> graveyards;
        std::unordered_map<uint32, std::vector<uint32>> learn;
        std::vector<std::pair<uint32, uint32>> carry;      // item, aura
    };

    Story murlocs{ RACE_MURLOC, MURLOC_RACE_BIT, 1000, 1101, "the murlocs", "murloc_naga_story", "murloc_naga_story_learn",
                   "murloc_naga_graveyards", "murloc_naga_story_carry" };
    Story nagas{ RACE_NAGA, NAGA_RACE_BIT, 2000, 690, "the naga", "naga_story", "naga_story_learn", "naga_story_graveyards",
                 "naga_story_carry" };
    Story* const STORIES[] = { &murlocs, &nagas };

    // (the murlocs' last quest: their standing with the towns, their language and their trainers hang on it)
    uint32& finalQuest = murlocs.finalQuest;

    bool HasTable(char const* table)
    {
        return bool(WorldDatabase.Query("SHOW TABLES LIKE '{}'", table));
    }

    uint32 StoryValue(Story const& story, char const* name)
    {
        if (QueryResult r = WorldDatabase.Query("SELECT `value` FROM `{}` WHERE `name` = '{}'", story.storyTable, name))
            return r->Fetch()[0].Get<uint32>();
        return 0;
    }

    void LoadStory(Story& story)
    {
        story.finalQuest = story.firstQuest = story.lastQuest = 0;
        story.graveyards.clear();
        story.learn.clear();
        story.carry.clear();
        if (!HasTable(story.storyTable))
            return;
        story.finalQuest = StoryValue(story, "final_quest");
        story.firstQuest = StoryValue(story, "first_quest");
        story.lastQuest = StoryValue(story, "last_quest");
        if (HasTable(story.learnTable))
            if (QueryResult r = WorldDatabase.Query("SELECT `quest`, `spell` FROM `{}`", story.learnTable))
                do
                    story.learn[r->Fetch()[0].Get<uint32>()].push_back(r->Fetch()[1].Get<uint32>());
                while (r->NextRow());
        if (HasTable(story.graveyardTable))
            if (QueryResult r = WorldDatabase.Query("SELECT `id`, `map`, `x`, `y`, `z`, `from_quest`, `until_quest` FROM `{}`", story.graveyardTable))
                do
                {
                    Field* f = r->Fetch();
                    story.graveyards.push_back({ f[0].Get<uint32>(), f[1].Get<uint32>(), f[2].Get<float>(), f[3].Get<float>(), f[4].Get<float>(),
                        f[5].Get<uint32>(), f[6].Get<uint32>() });
                } while (r->NextRow());
        if (HasTable(story.carryTable))
            if (QueryResult r = WorldDatabase.Query("SELECT `item`, `aura` FROM `{}`", story.carryTable))
                do
                    story.carry.emplace_back(r->Fetch()[0].Get<uint32>(), r->Fetch()[1].Get<uint32>());
                while (r->NextRow());
    }

    Story* StoryOf(Player const* player)
    {
        if (!player)
            return nullptr;
        for (Story* story : STORIES)
            if (player->getRace() == story->race)
                return story;
        return nullptr;
    }

    // The naga's memories (naga_story_memories: tools/murloc/compile.py's build_memories): each its aura (its phase
    // bit alone, the game's flashback look), where one arrives, its ground (a centre and a radius), the pool one
    // wakes at, its quests (an unfinished one starts again after a death inside) and those whose completion wakes one.
    struct Memory
    {
        uint32 spell = 0, bit = 0, map = 0;
        float x = 0, y = 0, z = 0, o = 0, cx = 0, cy = 0, radius = 0;
        uint32 poolMap = 0;
        float px = 0, py = 0, pz = 0, po = 0;
        std::vector<uint32> quests, wakes;
    };
    std::unordered_map<uint32, Memory> memories;         // by its aura
    uint32 markerSpell = 0, fadeSpell = 0;

    std::vector<uint32> Ids(std::string const& text)
    {
        std::vector<uint32> out;
        uint32 n = 0;
        bool any = false;
        for (char c : text + ",")
        {
            if (c >= '0' && c <= '9')
            {
                n = n * 10 + uint32(c - '0');
                any = true;
            }
            else if (any)
            {
                out.push_back(n);
                n = 0;
                any = false;
            }
        }
        return out;
    }

    void LoadMemories()
    {
        memories.clear();
        markerSpell = fadeSpell = 0;
        if (!HasTable(nagas.storyTable) || !HasTable("naga_story_memories"))
            return;
        markerSpell = StoryValue(nagas, "marker_spell");
        fadeSpell = StoryValue(nagas, "fade_spell");
        if (QueryResult r = WorldDatabase.Query("SELECT `spell`, `bit`, `map`, `x`, `y`, `z`, `o`, `cx`, `cy`, `radius`, `pool_map`, `px`, `py`, "
                "`pz`, `po`, `quests`, `wakes` FROM `naga_story_memories`"))
            do
            {
                Field* f = r->Fetch();
                Memory m;
                m.spell = f[0].Get<uint32>();
                m.bit = f[1].Get<uint32>();
                m.map = f[2].Get<uint32>();
                m.x = f[3].Get<float>();
                m.y = f[4].Get<float>();
                m.z = f[5].Get<float>();
                m.o = f[6].Get<float>();
                m.cx = f[7].Get<float>();
                m.cy = f[8].Get<float>();
                m.radius = f[9].Get<float>();
                m.poolMap = f[10].Get<uint32>();
                m.px = f[11].Get<float>();
                m.py = f[12].Get<float>();
                m.pz = f[13].Get<float>();
                m.po = f[14].Get<float>();
                m.quests = Ids(f[15].Get<std::string>());
                m.wakes = Ids(f[16].Get<std::string>());
                memories[m.spell] = m;          // (the spells aren't loaded yet: the auras are the world database's spell_dbc rows)
            } while (r->NextRow());
    }

    bool Murloc(Player const* player)
    {
        return player && player->getRace() == RACE_MURLOC;
    }

    bool Enabled()
    {
        return sConfigMgr->GetOption<bool>("MurlocNaga.Enable", true);
    }

    bool Ours(Player const* player)
    {
        return player && (player->getRace() == RACE_MURLOC || player->getRace() == RACE_NAGA);
    }

    fs::path ModuleData()
    {
        return fs::path(sConfigMgr->GetOption<std::string>("SourceDirectory", "")) / "modules" / "mod-murloc-naga" / "data";
    }

    // A class's trainer spells (its class trainers', the game's: trainer of type 0, the class its
    // requirement), in the order their levels come.
    struct TrainerSpell { uint32 spell, level, needs[3]; };

    std::vector<TrainerSpell> const& ClassSpells(uint8 cls)
    {
        static std::map<uint8, std::vector<TrainerSpell>> cache;
        auto it = cache.find(cls);
        if (it != cache.end())
            return it->second;
        std::vector<TrainerSpell>& out = cache[cls];
        if (QueryResult result = WorldDatabase.Query(
                "SELECT DISTINCT s.`SpellId`, s.`ReqLevel`, s.`ReqAbility1`, s.`ReqAbility2`, s.`ReqAbility3` FROM `trainer_spell` s "
                "JOIN `trainer` t ON t.`Id` = s.`TrainerId` WHERE t.`Type` = 0 AND t.`Requirement` = {} AND s.`ReqSkillLine` = 0 "
                "ORDER BY s.`ReqLevel`, s.`SpellId`", cls))
        {
            do
            {
                Field* f = result->Fetch();
                out.push_back({ f[0].Get<uint32>(), f[1].Get<uint32>(), { f[2].Get<uint32>(), f[3].Get<uint32>(), f[4].Get<uint32>() } });
            } while (result->NextRow());
        }
        return out;
    }

    // What a trainer spell teaches: the spells it learns, or itself.
    std::vector<uint32> Taught(uint32 spell)
    {
        std::vector<uint32> out;
        if (SpellInfo const* info = sSpellMgr->GetSpellInfo(spell))
        {
            for (SpellEffectInfo const& effect : info->GetEffects())
                if (effect.Effect == SPELL_EFFECT_LEARN_SPELL && effect.TriggerSpell)
                    out.push_back(effect.TriggerSpell);
            if (out.empty())
                out.push_back(spell);
        }
        return out;
    }

    void TeachClassSpells(Player* player)
    {
        uint32 level = player->GetLevel();
        uint32 learned = 0;
        for (TrainerSpell const& s : ClassSpells(player->getClass()))
        {
            if (s.level > level)
                break;
            bool can = true;
            for (uint32 need : s.needs)
                if (need && !player->HasSpell(need))
                    can = false;
            if (!can)
                continue;
            for (uint32 spell : Taught(s.spell))
                if (!player->HasSpell(spell) && sSpellMgr->GetSpellInfo(spell))
                {
                    player->learnSpell(spell);
                    ++learned;
                }
        }
        if (learned)
            LOG_DEBUG("module", "Murlocs and Naga: {} learned {} class spells at level {}", player->GetName(), learned, level);
    }
}

class MurlocNagaWorld : public WorldScript
{
public:
    MurlocNagaWorld() : WorldScript("MurlocNagaWorld", { WORLDHOOK_ON_BEFORE_CONFIG_LOAD, WORLDHOOK_ON_AFTER_CONFIG_LOAD,
                                                         WORLDHOOK_ON_LOAD_CUSTOM_DATABASE_TABLE }) { }

    // Before the quests and their conditions are read: each story's gate, made again from every quest the world
    // database has now (other modules' too). One of the race takes no quest open to it but its own story's until
    // that story's last quest is done; then its side's quests (those open to all of its side's races) and those
    // open to all are its too. Both gates live in the same conditions: each quest's own condition groups (or a
    // group 0 of their own) say "not a murloc" and "not a naga" for the races it's closed to, and each race has its
    // own alternative groups (the quest's own again, at ElseGroup + 1000 for the murlocs and + 2000 for the naga)
    // with "its story's last quest done".
    void OnLoadCustomDatabaseTable() override
    {
        for (Story* story : STORIES)
        {
            story->finalQuest = 0;
            story->graveyards.clear();
        }
        memories.clear();
        if (!Enabled())
            return;
        for (Story* story : STORIES)
            LoadStory(*story);
        LoadMemories();
        std::string const gate = "'mod-murloc-naga: gate'";
        std::string const cols = "(`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`, "
            "`ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, "
            "`ScriptName`, `Comment`)";
        std::string const existing = "SELECT DISTINCT `SourceEntry`, `ElseGroup` FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 "
            "AND `SourceGroup` = 0 AND `Comment` <> " + gate;
        WorldDatabase.DirectExecute("DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `Comment` = " + gate);
        // (neither story's own quests, nor the retired Darkshore starts')
        std::string ours = "q.`ID` NOT BETWEEN 975000 AND 975999";
        for (Story* story : STORIES)
            if (story->firstQuest && story->lastQuest)
                ours += fmt::format(" AND q.`ID` NOT BETWEEN {} AND {}", story->firstQuest, story->lastQuest);
        for (Story* story : STORIES)
        {
            if (!story->finalQuest || !story->firstQuest || !story->lastQuest)
                continue;
            uint32 const bit = story->raceBit, final = story->finalQuest, offset = story->gateOffset;
            std::string const gated = fmt::format("(q.`AllowableRaces` = 0 OR q.`AllowableRaces` & {}) AND {}", bit, ours);
            // (its side's quests, open to all of the side's races: its race's too, once the gate lets it)
            WorldDatabase.DirectExecute(fmt::format("UPDATE `quest_template` q SET q.`AllowableRaces` = q.`AllowableRaces` | {} WHERE "
                "(q.`AllowableRaces` & {}) = {} AND (q.`AllowableRaces` & 0x7FFFFFFF) <> 0x7FFFFFFF AND {}", bit, story->sideMask, story->sideMask, ours));
            // not one of the race: in each group the quest has, or in one of its own
            WorldDatabase.DirectExecute(fmt::format("INSERT INTO `conditions` {} SELECT 19, 0, q.`ID`, 0, g.`ElseGroup`, 16, 0, {}, 0, 0, 1, 0, 0, '', {} "
                "FROM `quest_template` q JOIN ({}) g ON g.`SourceEntry` = q.`ID` WHERE {}", cols, bit, gate, existing, gated));
            WorldDatabase.DirectExecute(fmt::format("INSERT INTO `conditions` {} SELECT 19, 0, q.`ID`, 0, 0, 16, 0, {}, 0, 0, 1, 0, 0, '', {} "
                "FROM `quest_template` q WHERE {} AND NOT EXISTS (SELECT 1 FROM `conditions` c WHERE c.`SourceTypeOrReferenceId` = 19 "
                "AND c.`SourceGroup` = 0 AND c.`SourceEntry` = q.`ID` AND c.`Comment` <> {})", cols, bit, gate, gated, gate));
            // or one of the race whose story is done: each group again, with that
            WorldDatabase.DirectExecute(fmt::format("INSERT INTO `conditions` {} SELECT c.`SourceTypeOrReferenceId`, c.`SourceGroup`, c.`SourceEntry`, "
                "c.`SourceId`, c.`ElseGroup` + {}, c.`ConditionTypeOrReference`, c.`ConditionTarget`, c.`ConditionValue1`, c.`ConditionValue2`, "
                "c.`ConditionValue3`, c.`NegativeCondition`, c.`ErrorType`, c.`ErrorTextId`, c.`ScriptName`, {} FROM `conditions` c "
                "JOIN `quest_template` q ON q.`ID` = c.`SourceEntry` WHERE c.`SourceTypeOrReferenceId` = 19 AND c.`SourceGroup` = 0 "
                "AND c.`Comment` <> {} AND {}", cols, offset, gate, gate, gated));
            WorldDatabase.DirectExecute(fmt::format("INSERT INTO `conditions` {} SELECT 19, 0, q.`ID`, 0, g.`ElseGroup` + {}, 8, 0, {}, 0, 0, 0, 0, 0, '', {} "
                "FROM `quest_template` q JOIN ({}) g ON g.`SourceEntry` = q.`ID` WHERE {}", cols, offset, final, gate, existing, gated));
            WorldDatabase.DirectExecute(fmt::format("INSERT INTO `conditions` {} SELECT 19, 0, q.`ID`, 0, {}, 8, 0, {}, 0, 0, 0, 0, 0, '', {} "
                "FROM `quest_template` q WHERE {} AND NOT EXISTS (SELECT 1 FROM `conditions` c WHERE c.`SourceTypeOrReferenceId` = 19 "
                "AND c.`SourceGroup` = 0 AND c.`SourceEntry` = q.`ID` AND c.`Comment` <> {})", cols, offset, final, gate, gated, gate));
            if (QueryResult r = WorldDatabase.Query(fmt::format("SELECT COUNT(DISTINCT `SourceEntry`) FROM `conditions` WHERE `Comment` = {} "
                    "AND `ConditionTypeOrReference` = 16 AND `ConditionValue1` = {}", gate, bit)))
                LOG_INFO("module", "Murlocs and Naga: the gate for {} is on {} quests (open once quest {} is done)", story->name,
                    r->Fetch()[0].Get<uint64>(), final);
        }
        if (!memories.empty())
            LOG_INFO("module", "Murlocs and Naga: the naga's story has {} memories (marker {}, fade {})", memories.size(), markerSpell, fadeSpell);
    }

    // As the configuration is about to be read (the modules' configs are read already): before the
    // other race modules' patches, which are made from the game with this one in.
    void OnBeforeConfigLoad(bool reload) override
    {
        if (reload)
            return;
        char const* client = std::getenv("WOW_CLIENT_DIR");
        if (!client || !*client)
            return;
        fs::path data = fs::path(client) / "Data";
        std::error_code error;
        if (!fs::is_directory(data, error))
            return;
        auto log = [](std::string const& line) { LOG_INFO("module", "Murlocs and Naga: {}", line); };
        // (Wrath Remix's realm has no murlocs or naga: ctl.sh turns them off there, and the patch is
        // set aside before the other patches are made from the game's tables)
        if (!Enabled())
        {
            MurlocNaga::SetPatchAside(data, log);
            return;
        }
        if (!sConfigMgr->GetOption<bool>("MurlocNaga.ClientPatch", true))
        {
            MurlocNaga::RemovePatch(data, log);
            return;
        }
        if (!fs::is_directory(ModuleData() / "client", error))
        {
            LOG_ERROR("module", "Murlocs and Naga: the module's files for the game aren't in {}", (ModuleData() / "client").string());
            return;
        }
        MurlocNaga::UpdatePatch(ModuleData() / "client", data, log);
    }

    // The intros' cameras where the world server reads them (its data folder's Cameras, read as the
    // world starts), so it follows the camera and sends the game what's along the way.
    void OnAfterConfigLoad(bool reload) override
    {
        if (reload || !Enabled())
            return;
        std::string dataDir = sConfigMgr->GetOption<std::string>("DataDir", "./");
        MurlocNaga::PutCameras(ModuleData() / "client", fs::path(dataDir), [](std::string const& line)
        {
            LOG_ERROR("module", "Murlocs and Naga: {}", line);
        });
    }
};

// What a town guard says to a murloc it doesn't like the look of, in its own people's language (which
// a murloc doesn't speak: the game garbles it), as it comes near; the guard attacks only at a few yards
// (Low Profile, the module's aura in towns).
namespace
{
    char const* const WARNINGS[] = {
        "Halt! Not one step closer, murloc!",
        "You there! Back to the water, fish-face!",
        "Stop right there. Turn around. Now.",
        "No murlocs in town. Go on, get!",
        "One more step and I'll have your fins for a hat!",
        "I see you, little gurgler. Don't you dare.",
    };
    char const* const NODS[] = {
        "Mind yourself, little one.",
        "Oh, it's you. Behave.",
        "Keep out of trouble, eh?",
    };

    // The guard's own annoyed voice (the game's NPC voices: its people's guards').
    uint32 GuardVoice(Creature const* guard)
    {
        FactionTemplateEntry const* ft = guard->GetFactionTemplateEntry();
        switch (ft ? ft->faction : 0)
        {
            case 47: case 54: return 5912;                                   // dwarf guard
            case 69: return 6007;                                            // Sentinel
            case 930: return 5973;
            case 21: case 369: case 470: case 577: case 169: return 5963;  // goblin bruiser
            case 68: return 6041;                                            // Deathguard
            case 81: return 6010;                                            // tauren
            case 67: case 76: case 530: case 911: return 6020;               // grunt
            default: break;
        }
        return (ft && (ft->ourMask & FACTION_MASK_HORDE)) ? 6020 : 5973;
    }

    Language GuardLanguage(Creature const* guard)
    {
        FactionTemplateEntry const* ft = guard->GetFactionTemplateEntry();
        switch (ft ? ft->faction : 0)
        {
            case 69: return LANG_DARNASSIAN;
            case 47: return LANG_DWARVISH;
            case 54: return LANG_GNOMISH;
            case 930: return LANG_DRAENEI;
            case 67: case 76: return LANG_ORCISH;
            case 81: return LANG_TAURAHE;
            case 68: return LANG_GUTTERSPEAK;
            case 530: return LANG_TROLL;
            case 911: return LANG_THALASSIAN;
            default: break;
        }
        if (ft && (ft->ourMask & FACTION_MASK_HORDE))
            return LANG_ORCISH;
        return LANG_COMMON;
    }

    struct GuardsNear
    {
        WorldObject const* me;
        float range;
        bool operator()(Creature* c) const
        {
            return c->IsAlive() && c->IsGuard() && !c->IsInCombat() && me->IsWithinDistInMap(c, range);
        }
    };

    std::unordered_map<ObjectGuid::LowType, uint32> sinceCheck;            // player -> ms
    std::unordered_map<uint64, time_t> lastSaid;                             // guard x player -> when
}

// The naga's memories, played (bible 2.2, 18.3). A memory is its aura on the player: the relive beat puts it on
// (SmartAI, a quest's scene or the singer's "Sing it again"), the wake beat or its last quest's completion takes it
// off. Here, as it goes on: the screen fades, the marker goes on (every phase of theirs needs it absent: the
// present goes, the memory's bit alone stays), the player is taken to the memory's stage, and the naga of their
// party on one of its quests near them go in too. As it comes off: the fade, the marker off, back at the pool, the
// present again. A death inside: alive again at once, its unfinished quests started over, awake at the pool. A
// logout inside: awake at the pool at the next login. Leaving the memory's ground (its radius around its centre,
// or its map): awake at the pool.
namespace
{
    enum class MemoryStep { Enter, Leave, Wake, Revive, Replay };

    struct Pending
    {
        MemoryStep step;
        uint32 spell;
        uint32 due;                                      // the player's own clock (ms)
    };

    struct Reliving
    {
        uint32 spell;
        uint32 since;
    };

    std::unordered_map<ObjectGuid::LowType, std::vector<Pending>> pending;
    std::unordered_map<ObjectGuid::LowType, Reliving> reliving;
    std::unordered_map<ObjectGuid::LowType, uint32> clocks, sinceMemoryCheck, sinceCarry;
    std::unordered_set<ObjectGuid::LowType> switching;  // (taking one memory off to go into another: no waking)
    // A memory's quests left unfinished on waking (a death, a logout, its ground left): on going back in, each one's
    // giver there plays its accepting scene again (its waves, its event's credit: the quest itself is in the log).
    std::unordered_map<ObjectGuid::LowType, std::unordered_set<uint32>> unfinished;

    constexpr uint32 ENTER_DELAY = 800, REVIVE_DELAY = 1500, WAKE_AFTER_QUEST = 4000, GRACE = 5000, REPLAY_DELAY = 2500;

    Memory const* MemoryOf(uint32 spell)
    {
        auto it = memories.find(spell);
        return it == memories.end() ? nullptr : &it->second;
    }

    Memory const* RelivingNow(Player const* player)
    {
        for (auto const& [spell, memory] : memories)
            if (player->HasAura(spell))
                return &memory;
        return nullptr;
    }

    void Queue(Player* player, MemoryStep step, uint32 spell, uint32 delay)
    {
        ObjectGuid::LowType guid = player->GetGUID().GetCounter();
        pending[guid].push_back({ step, spell, clocks[guid] + delay });
    }

    void RefreshPhases(Player* player)
    {
        player->UpdateZoneDependentAuras(player->GetZoneId());
        player->UpdateAreaDependentAuras(player->GetAreaId());
    }

    bool OnItsQuest(Player const* player, Memory const& memory)
    {
        for (uint32 quest : memory.quests)
            if (player->GetQuestStatus(quest) == QUEST_STATUS_INCOMPLETE)
                return true;
        return false;
    }

    void Enter(Player* player, Memory const& memory)
    {
        if (!player->HasAura(memory.spell))
            return;
        ObjectGuid::LowType guid = player->GetGUID().GetCounter();
        for (auto const& [spell, other] : memories)              // (one memory at a time)
            if (spell != memory.spell && player->HasAura(spell))
            {
                switching.insert(guid);
                player->RemoveAurasDueToSpell(spell);
                switching.erase(guid);
            }
        if (fadeSpell)
            player->AddAura(fadeSpell, player);
        if (markerSpell && !player->HasAura(markerSpell))
            player->AddAura(markerSpell, player);
        if (Group* group = player->GetGroup())
            for (GroupReference* ref = group->GetFirstMember(); ref; ref = ref->next())
                if (Player* member = ref->GetSource())
                    if (member != player && member->getRace() == RACE_NAGA && member->IsInWorld() && member->IsAlive()
                        && member->IsInMap(player) && member->IsWithinDistInMap(player, 40.0f) && !member->HasAura(memory.spell)
                        && OnItsQuest(member, memory))
                        member->AddAura(memory.spell, member);
        reliving[guid] = { memory.spell, clocks[guid] };
        player->TeleportTo(memory.map, memory.x, memory.y, memory.z, memory.o);
        RefreshPhases(player);
        LOG_DEBUG("module", "Murlocs and Naga: {} relives memory {} (phase {})", player->GetName(), memory.spell, player->GetPhaseMask());
        if (unfinished.count(guid))
            Queue(player, MemoryStep::Replay, memory.spell, REPLAY_DELAY);
    }

    // Back in a memory with its quests unfinished: each one's giver there (the nearest on the memory's ground, seen by
    // the player) accepts it again (its scene plays as when it was first given).
    void Replay(Player* player, Memory const& memory)
    {
        auto it = unfinished.find(player->GetGUID().GetCounter());
        if (it == unfinished.end())
            return;
        std::unordered_set<uint32> quests = it->second;
        unfinished.erase(it);
        if (!player->HasAura(memory.spell))
            return;
        for (uint32 questId : memory.quests)
        {
            Quest const* quest = sObjectMgr->GetQuestTemplate(questId);
            if (!quest || !quests.count(questId) || player->GetQuestStatus(questId) != QUEST_STATUS_INCOMPLETE)
                continue;
            for (auto const& [entry, starts] : *sObjectMgr->GetCreatureQuestRelationMap())
                if (starts == questId)
                    if (Creature* giver = player->FindNearestCreature(entry, memory.radius * 2.0f))
                    {
                        if (giver->AI())
                            giver->AI()->sQuestAccept(player, quest);
                        LOG_DEBUG("module", "Murlocs and Naga: {}'s quest {} played again by {}", player->GetName(), questId, entry);
                        break;
                    }
        }
    }

    void Wake(Player* player, Memory const& memory)
    {
        for (uint32 quest : memory.quests)                       // (left unfinished: played again on going back in)
            if (player->GetQuestStatus(quest) == QUEST_STATUS_INCOMPLETE)
                unfinished[player->GetGUID().GetCounter()].insert(quest);
        reliving.erase(player->GetGUID().GetCounter());
        if (RelivingNow(player))                                 // (gone into another meanwhile)
            return;
        if (markerSpell)
            player->RemoveAurasDueToSpell(markerSpell);
        if (fadeSpell)
            player->AddAura(fadeSpell, player);
        player->TeleportTo(memory.poolMap, memory.px, memory.py, memory.pz, memory.po);
        RefreshPhases(player);
        LOG_DEBUG("module", "Murlocs and Naga: {} wakes from memory {} (phase {})", player->GetName(), memory.spell, player->GetPhaseMask());
    }

    // A quest of the memory's, unfinished, started over: out of the log (its items gathered for it gone, as
    // .quest remove does) and in again.
    void Restart(Player* player, uint32 questId)
    {
        Quest const* quest = sObjectMgr->GetQuestTemplate(questId);
        if (!quest || player->GetQuestStatus(questId) != QUEST_STATUS_INCOMPLETE)
            return;
        for (uint8 slot = 0; slot < MAX_QUEST_LOG_SIZE; ++slot)
            if (player->GetQuestSlotQuestId(slot) == questId)
            {
                player->SetQuestSlot(slot, 0);
                player->TakeQuestSourceItem(questId, false);
            }
        for (uint8 i = 0; i < QUEST_ITEM_OBJECTIVES_COUNT; ++i)
            if (uint32 item = quest->RequiredItemId[i])
                if (ItemTemplate const* proto = sObjectMgr->GetItemTemplate(item))
                    if (proto->Class == ITEM_CLASS_QUEST)
                        if (uint32 count = player->GetItemCount(item))
                            player->DestroyItemCount(item, count, true);
        player->RemoveActiveQuest(questId, false);
        if (player->CanAddQuest(quest, false))
            player->AddQuestAndCheckCompletion(quest, nullptr);
    }

    void Revive(Player* player, Memory const& memory)
    {
        if (!player->IsAlive())
        {
            player->ResurrectPlayer(1.0f);
            player->SpawnCorpseBones();
        }
        player->SetFullHealth();
        if (player->getPowerType() == POWER_MANA)
            player->SetPower(POWER_MANA, player->GetMaxPower(POWER_MANA));
        for (uint32 quest : memory.quests)
            Restart(player, quest);
        player->RemoveAurasDueToSpell(memory.spell);             // (and so awake at the pool)
        LOG_DEBUG("module", "Murlocs and Naga: {} died in memory {}", player->GetName(), memory.spell);
    }

    // Each update: what's due, and once a second whether one reliving has left the memory's ground.
    void UpdateMemories(Player* player, uint32 diff)
    {
        ObjectGuid::LowType guid = player->GetGUID().GetCounter();
        uint32 now = (clocks[guid] += diff);
        auto it = pending.find(guid);
        if (it != pending.end() && !it->second.empty() && !player->IsBeingTeleported())
        {
            std::vector<Pending> due, later;
            for (Pending const& p : it->second)
                (p.due <= now ? due : later).push_back(p);
            it->second = later;
            for (Pending const& p : due)
            {
                Memory const* memory = MemoryOf(p.spell);
                if (!memory)
                    continue;
                switch (p.step)
                {
                    case MemoryStep::Enter: Enter(player, *memory); break;
                    case MemoryStep::Leave: player->RemoveAurasDueToSpell(memory->spell); break;
                    case MemoryStep::Wake: Wake(player, *memory); break;
                    case MemoryStep::Revive: Revive(player, *memory); break;
                    case MemoryStep::Replay: Replay(player, *memory); break;
                }
            }
        }
        uint32& since = sinceMemoryCheck[guid];
        if ((since += diff) < 1000)
            return;
        since = 0;
        auto in = reliving.find(guid);
        if (in == reliving.end() || player->IsBeingTeleported() || now - in->second.since < GRACE || !player->IsAlive())
            return;
        Memory const* memory = MemoryOf(in->second.spell);
        if (!memory || !player->HasAura(memory->spell))
            return;
        float dx = player->GetPositionX() - memory->cx, dy = player->GetPositionY() - memory->cy;
        if (player->GetMapId() != memory->map || dx * dx + dy * dy > memory->radius * memory->radius)
        {
            LOG_DEBUG("module", "Murlocs and Naga: {} left memory {}'s ground", player->GetName(), memory->spell);
            player->RemoveAurasDueToSpell(memory->spell);
        }
    }

    // What one carries puts its aura on (a story's carry table: a heavy jar, a net of eggs), once a second.
    void UpdateCarry(Player* player, Story const& story, uint32 diff)
    {
        if (story.carry.empty())
            return;
        uint32& since = sinceCarry[player->GetGUID().GetCounter()];
        if ((since += diff) < 1000)
            return;
        since = 0;
        for (auto const& [item, aura] : story.carry)
        {
            bool carrying = player->HasItemCount(item, 1);
            if (carrying && !player->HasAura(aura) && player->IsAlive())
                player->AddAura(aura, player);
            else if (!carrying && player->HasAura(aura))
                player->RemoveAurasDueToSpell(aura);
        }
    }

    void Forget(ObjectGuid::LowType guid)
    {
        pending.erase(guid);
        reliving.erase(guid);
        unfinished.erase(guid);
        clocks.erase(guid);
        sinceMemoryCheck.erase(guid);
        sinceCarry.erase(guid);
    }
}

class MurlocNagaUnit : public UnitScript
{
public:
    MurlocNagaUnit() : UnitScript("MurlocNagaUnit", true, { UNITHOOK_ON_AURA_APPLY, UNITHOOK_ON_AURA_REMOVE, UNITHOOK_ON_UNIT_DEATH }) { }

    // A memory's aura on a naga in the world (not one loaded with the character at login: the login wakes them)
    void OnAuraApply(Unit* unit, Aura* aura) override
    {
        Player* player = unit ? unit->ToPlayer() : nullptr;
        if (!player || memories.empty() || !player->IsInWorld() || !MemoryOf(aura->GetId()))
            return;
        Queue(player, MemoryStep::Enter, aura->GetId(), ENTER_DELAY);
    }

    void OnAuraRemove(Unit* unit, AuraApplication* aurApp, AuraRemoveMode /*mode*/) override
    {
        Player* player = unit ? unit->ToPlayer() : nullptr;
        if (!player || memories.empty() || !aurApp || !MemoryOf(aurApp->GetBase()->GetId()) || !player->IsInWorld()
            || !player->GetSession() || player->GetSession()->PlayerLogout() || switching.count(player->GetGUID().GetCounter()))
            return;
        Queue(player, MemoryStep::Wake, aurApp->GetBase()->GetId(), 0);
    }

    // A death inside a memory: no corpse run, no graveyard
    void OnUnitDeath(Unit* unit, Unit* /*killer*/) override
    {
        Player* player = unit ? unit->ToPlayer() : nullptr;
        if (!player || memories.empty())
            return;
        if (Memory const* memory = RelivingNow(player))
            Queue(player, MemoryStep::Revive, memory->spell, REVIVE_DELAY);
    }
};

class MurlocNagaPlayer : public PlayerScript
{
public:
    MurlocNagaPlayer() : PlayerScript("MurlocNagaPlayer", { PLAYERHOOK_ON_FIRST_LOGIN, PLAYERHOOK_ON_LEVEL_CHANGED, PLAYERHOOK_ON_LOGIN,
                                                            PLAYERHOOK_ON_UPDATE, PLAYERHOOK_ON_PLAYER_COMPLETE_QUEST, PLAYERHOOK_ON_LOGOUT,
                                                            PLAYERHOOK_ON_BEFORE_CHOOSE_GRAVEYARD, PLAYERHOOK_ON_PLAYER_JUST_DIED,
                                                            PLAYERHOOK_ON_BEFORE_QUEST_COMPLETE }) { }

    // One whose story isn't done wakes at its story's nearest graveyard on its map (one whose quest rule holds),
    // not a town's; elsewhere, the game's.
    void OnPlayerBeforeChooseGraveyard(Player* player, TeamId /*teamId*/, bool nearCorpse, uint32& graveyardOverride) override
    {
        Story const* story = StoryOf(player);
        if (!story || !Enabled() || !story->finalQuest || story->graveyards.empty() || player->GetQuestRewardStatus(story->finalQuest))
            return;
        WorldLocation loc = nearCorpse ? player->GetCorpseLocation() : player->GetWorldLocation();
        float best = 0.0f;
        for (StoryGraveyard const& g : story->graveyards)
        {
            if (g.map != loc.GetMapId() || (g.fromQuest && !player->GetQuestRewardStatus(g.fromQuest))
                || (g.untilQuest && player->GetQuestRewardStatus(g.untilQuest)))
                continue;
            float dx = g.x - loc.GetPositionX(), dy = g.y - loc.GetPositionY();
            float d = dx * dx + dy * dy;
            if (!graveyardOverride || d < best)
            {
                graveyardOverride = g.id;
                best = d;
            }
        }
    }

    // They start at level 10, with their class's spells to that level, whole (where: playercreateinfo, their story's
    // start). A murloc starts Hostile with the towns of the Alliance, the Horde and the goblins (at war: their guards
    // attack it, and it them), until it earns better.
    void OnPlayerFirstLogin(Player* player) override
    {
        if (!Ours(player) || !Enabled())
            return;
        if (player->GetLevel() < START_LEVEL)
            player->GiveLevel(START_LEVEL);
        TeachClassSpells(player);
        player->SetFullHealth();
        if (player->getPowerType() == POWER_MANA)
            player->SetPower(POWER_MANA, player->GetMaxPower(POWER_MANA));
        if (Murloc(player) && finalQuest)
            for (uint32 id : MURLOC_HOSTILE_FACTIONS)
                if (FactionEntry const* faction = sFactionStore.LookupEntry(id))
                    player->GetReputationMgr().SetReputation(faction, float(StartStanding(id)));
    }

    // The naga learn their class's spells as they come of age for them; the murlocs, from the tribe's
    // trainers (their story's own).
    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        if (Ours(player) && Enabled() && !(Murloc(player) && finalQuest))
            TeachClassSpells(player);
    }

    // (what a talent learned since opens, and spells a newer release teaches; a naga who logged out inside a
    // memory wakes at its pool)
    void OnPlayerLogin(Player* player) override
    {
        if (!Ours(player) || !Enabled())
            return;
        ObjectGuid::LowType guid = player->GetGUID().GetCounter();
        Forget(guid);
        if (!player->HasAtLoginFlag(AT_LOGIN_FIRST) && !(Murloc(player) && finalQuest))
            TeachClassSpells(player);
        if (Murloc(player) && finalQuest && !player->HasAtLoginFlag(AT_LOGIN_FIRST) && !player->HasSkill(SKILL_LANG_NERGLISH))
            Migrate(player);
        if (Memory const* memory = RelivingNow(player))
        {
            LOG_DEBUG("module", "Murlocs and Naga: {} logged out inside memory {}: awake at its pool", player->GetName(), memory->spell);
            player->RemoveAurasDueToSpell(memory->spell);       // (the aura's coming off wakes them)
        }
        else if (markerSpell && player->HasAura(markerSpell))
            player->RemoveAurasDueToSpell(markerSpell);
    }

    // A murloc made before the questline (the island village off Auberdine, since retired): once, it
    // speaks Nerglish and not Common, is Hostile with the towns like any murloc, and goes to the start
    // of the story if it's still in Darkshore.
    static constexpr uint16 SKILL_LANG_NERGLISH = 140, SKILL_LANG_COMMON_ID = 98;
    static constexpr uint32 SPELL_LANG_NERGLISH = 816, SPELL_LANG_COMMON = 668;

    void Migrate(Player* player)
    {
        player->SetSkill(SKILL_LANG_NERGLISH, 0, 300, 300);
        if (!player->HasSpell(SPELL_LANG_NERGLISH))
            player->learnSpell(SPELL_LANG_NERGLISH);
        if (player->HasSkill(SKILL_LANG_COMMON_ID))
            player->SetSkill(SKILL_LANG_COMMON_ID, 0, 0, 0);
        if (player->HasSpell(SPELL_LANG_COMMON))
            player->removeSpell(SPELL_LANG_COMMON, SPEC_MASK_ALL, false);
        for (uint32 id : MURLOC_HOSTILE_FACTIONS)
            if (FactionEntry const* faction = sFactionStore.LookupEntry(id))
                if (player->GetReputationMgr().GetReputation(faction) > StartStanding(id))
                    player->GetReputationMgr().SetReputation(faction, float(StartStanding(id)));
        LOG_INFO("module", "Murlocs and Naga: {} (a murloc of an earlier release) speaks Nerglish now, and is Hostile with the towns",
            player->GetName());
        if (player->GetZoneId() == 148)                                     // (Darkshore: the retired village)
            if (PlayerInfo const* info = sObjectMgr->GetPlayerInfo(player->getRace(), player->getClass()))
                player->TeleportTo(info->mapId, info->positionX, info->positionY, info->positionZ, info->orientation);
    }

    void OnPlayerLogout(Player* player) override
    {
        sinceCheck.erase(player->GetGUID().GetCounter());
        Forget(player->GetGUID().GetCounter());
    }

    // A death the game deals itself (falling, drowning): inside a memory, as any death there.
    void OnPlayerJustDied(Player* player) override
    {
        if (memories.empty() || !Ours(player))
            return;
        if (Memory const* memory = RelivingNow(player))
        {
            auto it = pending.find(player->GetGUID().GetCounter());
            if (it == pending.end() || std::none_of(it->second.begin(), it->second.end(), [](Pending const& p) { return p.step == MemoryStep::Revive; }))
                Queue(player, MemoryStep::Revive, memory->spell, REVIVE_DELAY);
        }
    }

    // A memory's last quest's objectives done (the quest complete, not yet handed in): awake at the pool after the
    // song's last note.
    bool OnPlayerBeforeQuestComplete(Player* player, uint32 questId) override
    {
        if (memories.empty() || !Ours(player) || !Enabled())
            return true;
        for (auto const& [spell, memory] : memories)
            if (player->HasAura(spell) && std::find(memory.wakes.begin(), memory.wakes.end(), questId) != memory.wakes.end())
                Queue(player, MemoryStep::Leave, spell, WAKE_AFTER_QUEST);
        return true;
    }

    // A story's quest handed in: the spells it teaches. The murlocs' story done: the Alliance takes them in (its towns'
    // standing Neutral at least), and the murloc understands them at last (Common, beside Nerglish).
    void OnPlayerCompleteQuest(Player* player, Quest const* quest) override
    {
        Story const* story = StoryOf(player);
        if (!story || !Enabled())
            return;
        auto learn = story->learn.find(quest->GetQuestId());
        if (learn != story->learn.end())
            for (uint32 spell : learn->second)
                if (!player->HasSpell(spell) && sSpellMgr->GetSpellInfo(spell))
                    player->learnSpell(spell);
        if (!Murloc(player) || !finalQuest || quest->GetQuestId() != finalQuest)
            return;
        player->SetSkill(SKILL_LANG_COMMON_ID, 0, 300, 300);
        if (!player->HasSpell(SPELL_LANG_COMMON))
            player->learnSpell(SPELL_LANG_COMMON);
        for (uint32 id : ALLIANCE_FACTIONS)
            if (FactionEntry const* faction = sFactionStore.LookupEntry(id))
                if (player->GetReputationMgr().GetReputation(faction) < 0)
                    player->GetReputationMgr().SetReputation(faction, 0.0f);
    }

    // The naga's memories (what's due, the memory's ground), what's carried, and town guards near a murloc: one
    // that doesn't like it warns it off, in its own language; one that does, nods.
    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        Story const* story = StoryOf(player);
        if (!story || !Enabled())
            return;
        if (!memories.empty())
            UpdateMemories(player, diff);
        UpdateCarry(player, *story, diff);
        if (!Murloc(player) || !finalQuest || !player->IsAlive() || player->IsInCombat() || player->IsGameMaster())
            return;
        uint32& since = sinceCheck[player->GetGUID().GetCounter()];
        since += diff;
        if (since < 1000)
            return;
        since = 0;
        std::list<Creature*> guards;
        GuardsNear check{ player, 20.0f };
        Acore::CreatureListSearcher<GuardsNear> searcher(player, guards, check);
        Cell::VisitObjects(player, searcher, 20.0f);
        time_t now = time(nullptr);
        for (Creature* guard : guards)
        {
            if (!guard->IsWithinLOSInMap(player))
                continue;
            uint64 key = (uint64(guard->GetSpawnId()) << 32) ^ player->GetGUID().GetCounter();
            time_t& when = lastSaid[key];
            bool hostile = guard->IsHostileTo(player);
            if (now - when < (hostile ? 25 : 120))
                continue;
            when = now;
            guard->SetFacingToObject(player);
            if (hostile)
            {
                guard->HandleEmoteCommand(urand(0, 1) ? EMOTE_ONESHOT_POINT : EMOTE_ONESHOT_SHOUT);
                guard->PlayDirectSound(GuardVoice(guard), player);
                guard->Say(WARNINGS[urand(0, std::size(WARNINGS) - 1)], GuardLanguage(guard), player);
            }
            else
            {
                guard->HandleEmoteCommand(EMOTE_ONESHOT_SALUTE);
                guard->Say(NODS[urand(0, std::size(NODS) - 1)], GuardLanguage(guard), player);
            }
            break;                                                           // (one guard at a time)
        }
    }
};

void AddMurlocNagaScripts()
{
    new MurlocNagaWorld();
    new MurlocNagaPlayer();
    new MurlocNagaUnit();
}
