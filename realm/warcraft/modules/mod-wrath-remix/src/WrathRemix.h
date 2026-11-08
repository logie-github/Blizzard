// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix: a Legion Remix-style replay of Wrath of the Lich King on a realm of its own.
 * Part of the World of Warcraft Android app (github.com/logie-github/YeaBwoi). GPL-3.0-or-later.
 */

#ifndef MOD_WRATH_REMIX_H
#define MOD_WRATH_REMIX_H

#include "Define.h"
#include "Duration.h"
#include "ObjectGuid.h"
#include <string>
#include <unordered_map>
#include <vector>

class Creature;
class CreatureAI;
class Player;
class Quest;
class SpellInfo;
class Unit;
struct CreatureTemplate;

namespace WrathRemix
{
    // Remix's own ids (the world SQL in data/sql/remix/world).
    enum Ids : uint32
    {
        NPC_MORATARI      = 770001,
        NPC_ETERNUS       = 770002,
        NPC_ANDORMU       = 770003,
        NPC_NOZARI        = 770004,
        NPC_ALURMI        = 770005,
        NPC_ZEPHYR        = 770006,
        NPC_SAAT          = 770007,
        NPC_CHRONOLOGIST  = 770008,
        NPC_MOMENTUS      = 770009,
        NPC_SYLVANAS      = 770011,     // from the future, with the bronze (Chapter II on)
        NPC_ALLERIA       = 770012,
        NPC_MORATARI_SCENE = 770013,    // Moratari as WRM-207's scene has her (no quests, seen by one)
        NPC_SYLVANAS_ABROAD = 770014,   // the same two anywhere but the Bazaar: hooded, passing for
        NPC_ALLERIA_ABROAD  = 770015,   // adventurers (no one may learn who they are)
        NPC_ECHO_FOOTMAN  = 770021,     // WRM-011's echoes of the war's dead
        NPC_ECHO_SAURFANG = 770022,
        NPC_ECHO_BOLVAR   = 770023,
        NPC_ANOMALY       = 770031,
        NPC_ANOMALY_CREDIT = 770032,    // WRM-013's kill credit, given as each anomaly dies
        NPC_INSTRUCTOR_CREDIT = 770033, // the old WRM-012's (until build 90)
        NPC_PLAN_WHAT     = 770049,     // WRM-011's: the three things the Timerunner asks Eternus
        NPC_PLAN_HOW      = 770050,
        NPC_PLAN_WHY      = 770058,
        NPC_TURN_CREDIT   = 770034,     // WRM-207's, given as its scene ends
        NPC_INTERLOPER    = 770041,     // Eternus's loyalists on the Wrathgate's cliffs (WRM-208)
        NPC_TIME_RIFT     = 28409,      // the Culling of Stratholme's time rift, for Moratari's return
        NPC_INSTRUCTOR_FIRST = 770101,  // the Bazaar's Timeworn Instructors, one per class trainer list
        NPC_INSTRUCTOR_LAST  = 770111,
        NPC_HOROS         = 770201,     // the Bazaar's Bronze vendors (Alurmi is one too)
        NPC_DOMELIUS      = 770202,
        NPC_ARTUROS       = 770203,
        NPC_AEONICUS      = 770204,
        NPC_DURUS         = 770205,
        // Legion Remix's Bazaar cast, the rest of it (wrath_remix_world_0009_bronze.sql): vendors 770206
        // to 770217, Grandmaster Jakkus's class mounts besides his wares, Pageturner Metros who
        // knows where everyone is, Nedward by the barber's chair. (Gossip texts: 7702201 + n.)
        NPC_PYTHAGORUS    = 770206,
        NPC_SACERDORMU    = 770207,
        NPC_AGOS          = 770208,     // Agos the Silent (he only nods)
        NPC_LARAH         = 770209,     // Larah Treebender
        NPC_FREDDIE       = 770210,     // Freddie Threads
        NPC_JAKKUS        = 770211,
        NPC_HEMET         = 770212,     // Hemet Nesingwary XVII
        NPC_NOSTWIN       = 770213,
        NPC_UNICUS        = 770214,
        NPC_LIDAMORRUTU   = 770215,
        NPC_LINDORMI      = 770216,
        NPC_ERUS          = 770217,
        NPC_METROS        = 770218,
        NPC_NEDWARD       = 770219,

        AREA_CAVERNS_OF_TIME = 2300,    // the Caverns of Time in Tanaris, where the prologue was until build 64
        AREA_MALYKRISS    = 4520,       // Malykriss: The Vile Hold, the Bazaar's home (Crystalsong Forest until build 117)
        AREA_WYRMREST_TEMPLE = 4161,
        ZONE_GRIZZLY_HILLS = 394,

        ITEM_BRONZE       = 77001,      // Bronze: a currency token, like the emblems
        ITEM_HOURGLASS    = 77002,      // Moratari's Hourglass: to the Bazaar and back (RemixHourglass.cpp)

        QUEST_OUT_OF_TIME      = 77010,     // the prologue at the Bazaar (STORY.md)
        QUEST_THE_PLAN         = 77011,
        QUEST_TIMES_TOLL       = 77012,
        QUEST_DEMONSTRATION    = 77013,
        QUEST_OLD_HABITS       = 77020,
        QUEST_BAZAAR_KEEPERS   = 77021,
        QUEST_TO_THE_FRONT_A   = 77014,
        QUEST_TO_THE_FRONT_H   = 77015,
        QUEST_MYSTERY_OF_THE_INFINITE = 12470,  // Chromie's, at Wyrmrest Temple (the game's own)
        QUEST_STRANGERS        = 77204,     // Chapter II and the turn (STORY.md)
        QUEST_WEIGHT_OF_TIME   = 77207,
        QUEST_LAST_HOUR        = 77721,     // Chapter VII: Eternus at the doors of Icecrown Citadel
        QUEST_LAST_NECESSARY_BATTLE = 77800,  // the Lich King
        QUEST_SEE_YOU_LATER    = 77801,     // the end (STORY.md)
        QUEST_BACK_TO_YOUR_OWN_TIME = 77802,

        NPC_SCENE_CREDIT  = 770035,     // a scene's credit, for quests that are a scene (each scene's to its own quest alone)
        NPC_LAST_HOUR_CREDIT = 770036,  // WRM-721's, as Eternus retreats
        NPC_LAST_ETERNUS  = 770061,     // Eternus at the last hour, her loyalists, and the three beside you
        NPC_LAST_CHRONOMANCER = 770062,
        NPC_LAST_EXECUTIONER = 770063,
        NPC_ALLY_MORATARI = 770064,
        // Moratari as the romance's scenes have her (tools/romance.py): in her evening dress, in her
        // tent, and in her true shape
        NPC_MORATARI_DRESS = 770720,
        NPC_MORATARI_TENT = 770721,
        NPC_MORATARI_DRAGON = 770722,
        NPC_CHROMIE_HOME  = 26527,      // Chromie as ChromieCraft has her, who brings Moratari's letter home
        NPC_ALLY_SYLVANAS = 770065,
        NPC_ALLY_ALLERIA  = 770066,
        NPC_LESSON_CREDIT = 770067,     // a class lesson's three abilities: 770067 + its slot (0 to 2)
        NPC_TRAINING_DUMMY = 770087,    // the training yard's dummies (wrath_remix_world_0023_bazaar.sql)

        QUEST_LESSON_FIRST = 77030,     // the class lessons, one a class (wrath_remix_world_0025_lessons.sql)
        QUEST_LESSON_LAST  = 77039,
        QUEST_FLAG_ALONE   = 77040,     // never offered: rewarded while the Timerunner has asked Moratari to wait (RemixMoratari.cpp)

        TEXT_MORATARI_PROLOGUE = 7702001,
        TEXT_MORATARI          = 7702002,
        TEXT_MORATARI_HISTORY  = 7702003,
        TEXT_ETERNUS           = 7702010,
        TEXT_ETERNUS_LATER     = 7702011,
        TEXT_ETERNUS_WHAT      = 7702012,   // her answers to WRM-011's questions
        TEXT_ETERNUS_HOW       = 7702013,
        TEXT_ETERNUS_WHY       = 7702014,
        TEXT_ANDORMU           = 7702020,
        TEXT_NOZARI            = 7702021,
        TEXT_ALURMI            = 7702030,
        TEXT_ZEPHYR            = 7702040,
        TEXT_SAAT              = 7702050,
        TEXT_CHRONOLOGIST      = 7702060,
        TEXT_MOMENTUS          = 7702070,
        TEXT_ECHO_FOOTMAN      = 7702080,   // then Saurfang's, Bolvar's
        TEXT_SYLVANAS_WYRMREST = 7702090,   // Sylvanas and Alleria at Wyrmrest Temple, at the Bazaar after
        TEXT_SYLVANAS          = 7702091,   // the turn, and Alleria on the Wrathgate's cliffs
        TEXT_ALLERIA_WYRMREST  = 7702092,
        TEXT_ALLERIA           = 7702093,
        TEXT_ALLERIA_GATE      = 7702094,
        TEXT_ALLERIA_LATER     = 7702095,   // Alleria at the Bazaar from Chapter V, from Chapter VII, and
        TEXT_ALLERIA_LAST      = 7702096,   // once the war is over; in the Grizzly Hills (Chapter III)
        TEXT_ALLERIA_AFTER     = 7702097,
        TEXT_ALLERIA_HILLS     = 7702098,
        TEXT_HOROS             = 7702201,   // then Domelius, Arturos, Aeonicus, Durus: 7702201 + n
        TEXT_INSTRUCTOR_LESSON = 7702501,   // an instructor with a lesson to give, to see through or to finish
    };

    // The travel entries the module names (remix_travel).
    enum Travel : uint16
    {
        TRAVEL_BAZAAR = 1,
    };

    // The Infinite Bazaar's middle, where new Timerunners wake (playercreateinfo).
    constexpr float BAZAAR_X = 6394.0f, BAZAAR_Y = 1866.0f, BAZAAR_Z = 508.7f, BAZAAR_O = 1.57f;

    struct LevelBand
    {
        int32 originalMin, originalMax, bandMin, bandMax;
        uint8 chapter;
        std::string name;
    };

    struct Bridge
    {
        uint32 quest, nextQuest;
        uint8 chapter;
        uint32 map;
        float x, y, z, o;
        std::string skipped;
    };

    // A quest that takes the Timerunner somewhere as it's taken (remix_departure): to the Bazaar
    // to answer Eternus, to the Wrathgate's cliffs.
    struct Departure
    {
        uint32 quest;
        uint32 map;
        float x, y, z, o;
    };

    struct Chapter
    {
        uint8 chapter;
        std::string name, summary;
        uint8 levelMin, levelMax;
        uint32 map[2];
        float x[2], y[2], z[2];
    };

    struct Destination
    {
        uint16 id;
        std::string name;
        uint8 side, minLevel;
        uint32 map;
        float x, y, z, o;
    };

    // A list of Bronze wares one of the Bazaar's vendors opens (remix_vendor_list): its own
    // hidden vendor template, whose npc_vendor rows are priced in Bronze.
    struct VendorList
    {
        uint32 list, vendor;
        uint8 side;
        std::string label;
    };

    struct Timerunner
    {
        uint32 bronze = 0;  // Bronze owed: what the realm kept before Bronze was an item, or couldn't store
        uint32 earned = 0;
        uint8 chapter = 0;
        uint8 kit = 0;      // the starter kit's version this Timerunner has had (0: none yet)
        // Where they came to the Bazaar from, the last time they came (-1: nowhere yet), for
        // Moratari's Hourglass to take them back to.
        int32 backMap = -1;
        float backX = 0.0f, backY = 0.0f, backZ = 0.0f, backO = 0.0f;
        bool intro = false;  // been through the opening (RemixIntro.cpp)
        bool dirty = false;
    };

    // A piece of a class's starter kit (remix_starter_kit), and an ability its class quests teach
    // (remix_class_spell).
    struct KitPiece
    {
        uint32 item;
        uint8 count;
    };

    struct ClassSpell
    {
        uint32 spell;
        uint8 level;
    };

    // Whether Wrath Remix runs here: on, and this is its realm.
    bool Active();
    bool BandsActive();

    void LoadConfig();
    void LoadData();

    // The tables, as loaded.
    LevelBand const* BandFor(uint32 map, uint32 zone);
    Bridge const* BridgeFor(uint32 quest);
    Departure const* DepartureFor(uint32 quest);
    std::vector<Chapter> const& Chapters();
    Chapter const* ChapterFor(uint8 chapter);
    std::vector<Destination> const& Destinations();
    Destination const* DestinationFor(uint16 id);
    std::vector<VendorList> const& VendorLists();
    uint32 QuestBronze(uint32 quest);

    // A level in a band: unchanged at or below the band's top (critters, the odd visitor), else
    // on the straight line from the original range to the band's, within 3 of its ends.
    int32 BandedLevel(LevelBand const& band, int32 level);

    // The chapter a level belongs to (1 to 7), or 0 below the first.
    uint8 ChapterForLevel(uint8 level);

    // Timerunners: loaded at login, saved at logout, on the core's saves, and after purchases.
    // Maps update on several threads: every read is a copy, every change made under a lock.
    Timerunner Get(Player* player);
    void Load(Player* player);
    void Save(Player* player);
    void Forget(Player* player);
    void AddBronze(Player* player, uint32 amount, bool announce);
    uint32 Bronze(Player* player);   // what the Timerunner carries
    void SetChapter(Player* player, uint8 chapter);
    void SetKit(Player* player, uint8 version);
    void SetWayBack(Player* player, int32 map, float x, float y, float z, float o);
    void SetIntroSeen(Player* player);
    // A line in a Timerunner's journal (remix_log), where they are: what ("accept", "talk",
    // "bridge"...), its quest, creature or other entry, and an amount.
    void Record(Player* player, char const* what, uint32 entry, int32 amount);

    // The realm's playerbots: sessions without a client.
    bool IsBot(Player* player);

    // The game's patch (Data/patch-Y.MPQ in the app's client): written as Wrath Remix starts,
    // taken out as ChromieCraft starts (ClientPatch.cpp).
    void UpdateClientPatch();

    // Moves a Timerunner a moment from now (after a quest's reward, a gossip's close).
    void TeleportSoon(Player* player, uint32 map, float x, float y, float z, float o);
    bool IsAlliance(Player* player);

    // The story's scenes (RemixScenes.cpp): played as a quest is taken or turned in.
    enum SceneTrigger : uint8
    {
        SCENE_ON_ACCEPT = 1,
        SCENE_ON_REWARD = 2,
    };
    void LoadScenes();
    bool PlayScene(Player* player, uint32 scene);
    bool SceneRunning(Player* player);
    uint32 SceneDuration(uint32 scene);                     // its last step's time, in ms (0: no such scene)
    void ScenesForQuest(Player* player, uint32 quest, uint8 trigger);
    bool ReplaySceneAt(Player* player, Creature* creature);

    // The end (RemixEnding.cpp).
    void LoadEnding();
    bool AddEndingGossip(Player* player, Creature* creature);
    bool EndingGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action, uint32 menuText);
    void SendHome(Player* player);
    void ReturnToBazaarSoon(Player* player, Milliseconds after);

    // Moratari's Hourglass (RemixHourglass.cpp): in every Timerunner's bags from the moment they
    // wake at the Bazaar; anywhere, it takes them to the Bazaar; there, back where they came from.
    bool AtTheBazaar(Player* player);

    // The opening (RemixIntro.cpp): whether a Timerunner is in it; play it, or end it now.
    bool InIntro(Player* player);
    void PlayIntro(Player* player);
    void SkipIntro(Player* player);
    void GiveHourglass(Player* player);

    // The class lessons (RemixLessons.cpp): each instructor walks a Timerunner of their class
    // through three of its abilities on the training yard's dummies.
    void LoadLessons();

    // Moratari at the Timerunner's side (RemixMoratari.cpp): her words on quests, the companion, and
    // remix_talk's things to say (to her, or to the war's own people).
    void LoadMoratari();
    std::string Words(Player* player, std::string text);                    // $N, $R, $C, $G... as a quest's text has them
    void MoratariSays(Player* player, uint32 speaker, std::string const& text);
    // Her own voice (RemixVoices.cpp, remix_voice): a line of a moment's said to [player] (by
    // [moratari] when she's near, else whispered), with her voice when the game has it.
    std::string VoicesFolder();
    void LoadVoices();
    bool MoratariVoice(Player* player, std::string const& moment, int32 index = -1, Creature* moratari = nullptr);
    uint32 MoratariVoiceFor(std::string const& words);                      // the sound of words she has voiced (0: none)
    // Eternus in her own shape (RemixModels.cpp, tools/models.py): her dragon's files (relative to
    // ModelsFolder) when the server package has every one of them, else none. ClientPatch.cpp puts
    // them in the game's patch with the rows of her look and says so (EternusShapeInPatch); only
    // then does she take that look.
    constexpr uint32 DISPLAY_ETERNUS_DRAGON = 32900, MODEL_ETERNUS_DRAGON = 3500;
    std::string ModelsFolder();
    std::vector<std::string> const& EternusShapeFiles();
    void EternusShapeInPatch();
    void MoratariOnQuest(Player* player, uint32 quest, uint8 moment);
    bool IsCompanionSummon();                                               // (while the companion is being summoned)
    uint8 CompanionLevel();
    CreatureAI* MoratariCompanionAI(Creature* creature);
    bool AddTalk(Player* player, Creature* creature);
    bool HasTalk(Player* player, Creature* creature);
    bool TalkSelect(Player* player, Creature* creature, uint32 sender, uint32 action);
    std::string CompanionReport(Player* player);
    uint32 TalkCreditNpc(uint32 credit);                    // whom a remix_talk credit is said to (0: none)
    bool PlaceOf(uint32 quest, uint32 credit, uint32& map, float& x, float& y);  // a remix_place's
    inline bool IsRomance(uint32 quest) { return quest >= 77900 && quest <= 77999; }   // Moratari's own story (optional)
    inline bool IsUnrisen(uint32 quest) { return quest >= 77061 && quest <= 77063; }   // the hidden plate's (RemixVileHoldSet.cpp): never pointed to
    constexpr uint32 QUEST_ROMANCE_FIRST = 77901, QUEST_ROMANCE_LAST = 77909;   // its nine (tools/romance.py)
    constexpr uint32 QUEST_ROMANCE_TIME_JUMPER = 77910;  // "turned in": they told her they're a time jumper (her story without the war's checkpoints)

    // Outings (RemixOutings.cpp): somewhere Moratari takes the Timerunner, a scene played there, and
    // back again (her tent at the Bazaar, a flight on her back).
    void LoadOutings();
    bool StartOuting(Player* player, uint32 outing);
    bool OnOuting(Player* player);
    bool AtTheCampfire(Player* player, Creature* her);      // she walked over to sit with them at the Bazaar's campfire, and is there still (RemixCampfire.cpp)
    void ScreenFade(Player* player, uint32 milliseconds, std::string const& text);  // dark for a while, words on it
    void TellAddon(Player* player, std::string const& message);                     // a word to the player's own add-on (WowRemix: the app's TouchAddon.kt)
    void ClientSettled(Player* player);                                               // the add-on's word that its frames run smoothly again (RemixIntro.cpp)
    std::string CurtainStatus(Player* player);                                       // "curtain 2 (3.1 s ago), settled 1 (2.9 s ago)", for `.remix intro status`
    // A journey from the dark (RemixIntro.cpp): the screen dark at once with [caption] on it (" | " a
    // new line), until the game has settled where they're going (map, x, y; or SettleSeconds are
    // up), then lifted over [liftMs]; never under [leastMs]. The caller makes the journey itself.
    void JourneyFromTheDark(Player* player, std::string const& caption, uint32 map, float x, float y, uint32 leastMs = 1500, uint32 liftMs = 2500);
    void LiftTheCurtain(Player* player);                                               // a journey that couldn't be made after all
    std::string PlaceName(uint32 map, float x, float y, float z);                      // the curtain's name for a place ("Wyrmrest Temple | Dragonblight")
    uint32 LessonQuest(Player* player);                         // their class's lesson, or 0
    bool IsLesson(uint32 quest);
    bool TeachesClassOf(Creature* instructor, Player* player);  // the instructor is their class's
    bool TeachesClassOf(uint32 instructor, Player* player);     // (by the instructor's entry)

    // The Bazaar's people talking while a Timerunner is about (RemixBazaar.cpp): the AI the camp's
    // own scripts give them.
    CreatureAI* BazaarLifeAI(Creature* creature);
    std::string HourglassReport(Player* player);
    void TakeInTimerunners();
    void LetGoOfThoseHome();

    // Eternus's last hour (RemixLastHour.cpp): begun as WRM-721 brings the Timerunner to the doors.
    bool BeginLastHour(Player* player);
    void LastHourAgain(Player* player);

    // Dungeons and raids for however many are there (WrathRemix.Solo.*, RemixSolo.cpp).
    bool SoloActive();
    float SoloDungeonDamage();
    float SoloRaidDamage();
    float SoloMaxBoost();
    // What the scaling makes of the instance the player is in (.remix solo).
    std::string SoloReport(Player* player);

    // The heal hook's two units (UnitScript::ModifyHealReceived), put right: the core passes them
    // the wrong way round for a heal that's cast (Unit::HealBySpell, the healer first) and the
    // right way for a heal over time's tick, which comes through the periodic damage hook first,
    // with the same amount. A script with both hooks keeps a thread_local HealTick of its own:
    // MarkHealTick in the periodic hook (true: a heal's tick, to scale in the heal hook only),
    // HealUnits first thing in the heal hook.
    struct HealTick
    {
        Unit const* target = nullptr;
        Unit const* caster = nullptr;
        uint32 const* amount = nullptr;
    };
    bool MarkHealTick(HealTick& tick, Unit* target, Unit* caster, uint32 const& amount, SpellInfo const* spell);
    void HealUnits(HealTick& tick, Unit*& target, Unit*& healer, uint32 const& amount);

    // Bronze amounts (WrathRemix.Bronze.*): enough over the story to buy everything the Bazaar sells
    // a class, once or twice over.
    struct BronzeRates
    {
        uint32 quest = 4000, kill = 75, elite = 300, rare = 3000, dungeonBoss = 6000, raidBoss = 30000,
            treasure = 1500, achievementPoint = 100;
    };
    BronzeRates const& Rates();
    bool Announce();
}

#endif
