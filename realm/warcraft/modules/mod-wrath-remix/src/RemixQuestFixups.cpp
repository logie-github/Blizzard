// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Remix's own quests (77000 to 77999) put right as the world server has them, in memory, as it
 * starts (the world database's quests loaded by then). Not in the SQL: its files are applied each
 * on its own, as it changes, and one file's REPLACE INTO a quest undoes another's UPDATE of it.
 *
 * - In a raid group. The core counts a quest's kills and credits for someone in a raid group only
 *   if it's a raid's quest (its type, quest_template.QuestInfoID; QUEST_FLAGS_RAID isn't read), and
 *   Icecrown Citadel lets no one in outside one, nor out of it as they come back to the Bazaar for
 *   the end. So Chapter VII's quests and the end's (77700 to 77899) are a raid's, as the game's own
 *   Icecrown Citadel quests are (the quest log says Raid by their names); the rest keep their type,
 *   so the log doesn't call the whole story a raid.
 * - The Skyborne (mod-skyborne, races 13 and 14), where its races are in the game: its SQL lets them
 *   take what their start race takes with an UPDATE of every quest, made before Remix's quests are
 *   there (its file is applied first). Its rule, on Remix's: the High Order (4096) where the Humans
 *   or the Night Elves may take it (1 | 8), the Windshapers (8192) where the Tauren or the Blood
 *   Elves may (32 | 512), but where every race already may.
 */

#include "WrathRemix.h"
#include "DBCStores.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "QuestDef.h"
#include "ScriptMgr.h"

using namespace WrathRemix;

namespace
{
    constexpr uint32 QUEST_REMIX_FIRST = 77000, QUEST_REMIX_LAST = 77999;
    constexpr uint32 QUEST_RAID_FIRST = 77700, QUEST_RAID_LAST = 77899;     // Chapter VII and the end

    constexpr uint32 RACE_HIGH_ORDER = 13, RACE_WINDSHAPERS = 14;   // mod-skyborne's
    constexpr uint32 RACES_HIGH_ORDER_START = 1 | 8;                // Human, Night Elf
    constexpr uint32 RACES_WINDSHAPERS_START = 32 | 512;            // Tauren, Blood Elf
    constexpr uint32 RACES_EVERY = 0x7FFFFFFF;

    // A quest's type and races are the core's to fill in (ObjectMgr, Quest's friend): reached here
    // as members of a class of Quest's own.
    struct QuestFields : Quest
    {
        static uint32& TypeOf(Quest& quest) { return quest.*(&QuestFields::Type); }
        static uint32& RacesOf(Quest& quest) { return quest.*(&QuestFields::AllowableRaces); }
    };

    void FixRemixQuests()
    {
        bool highOrder = sChrRacesStore.LookupEntry(RACE_HIGH_ORDER) != nullptr;
        bool windshapers = sChrRacesStore.LookupEntry(RACE_WINDSHAPERS) != nullptr;
        uint32 raids = 0, skyborne = 0;
        for (uint32 id = QUEST_REMIX_FIRST; id <= QUEST_REMIX_LAST; ++id)
        {
            Quest* quest = const_cast<Quest*>(sObjectMgr->GetQuestTemplate(id));
            if (!quest)
                continue;
            // (a PvP quest already counts in a battleground's raid group)
            uint32& type = QuestFields::TypeOf(*quest);
            if (id >= QUEST_RAID_FIRST && id <= QUEST_RAID_LAST &&
                type != QUEST_TYPE_RAID && type != QUEST_TYPE_RAID_10 && type != QUEST_TYPE_RAID_25 && type != QUEST_TYPE_PVP)
            {
                type = QUEST_TYPE_RAID;
                ++raids;
            }
            uint32& races = QuestFields::RacesOf(*quest);
            if ((races & RACES_EVERY) == RACES_EVERY)
                continue;
            uint32 was = races;
            if (highOrder && (races & RACES_HIGH_ORDER_START))
                races |= 1u << (RACE_HIGH_ORDER - 1);
            if (windshapers && (races & RACES_WINDSHAPERS_START))
                races |= 1u << (RACE_WINDSHAPERS - 1);
            if (races != was)
                ++skyborne;
        }
        LOG_INFO("module", "Wrath Remix: {} of its quests made a raid's, {} opened to the Skyborne", raids, skyborne);
    }
}

// As the server starts: after the world's quests are loaded (SetInitialWorldSettings), before anyone
// can log in (sessions are only taken in by the world's updates, which begin after this).
class RemixQuestFixupsWorld : public WorldScript
{
public:
    RemixQuestFixupsWorld() : WorldScript("RemixQuestFixupsWorld", { WORLDHOOK_ON_STARTUP }) { }

    void OnStartup() override
    {
        if (Active())
            FixRemixQuests();
    }
};

void AddRemixQuestFixupScripts()
{
    new RemixQuestFixupsWorld();
}
