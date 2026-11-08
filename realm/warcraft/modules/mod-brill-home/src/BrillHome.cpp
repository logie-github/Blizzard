// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * A home in Brill (mod-brill-home), ChromieCraft's realm alone (ctl.sh: BrillHome.Enable, and the SQL in
 * ChromieCraft's databases only).
 *
 * The house by Brill's north road (data/sql/chromiecraft/world, made by tools/build_sql.py) is everyone's
 * to see; what's in it is the player's own, by phases: near the house, a player is in phase 1 and the
 * bits that are theirs (Cedric Harrow until his quest is turned in, the bed from Jamie Nore's bed quest
 * on, each piece of furniture once it's bought). Away from it, phase 1 alone again. A player under a
 * phasing spell of the game's own is left as the spell has them.
 *
 * Jamie Nore (Brill's town hall) gives the quests, and once the deed is signed, the house's upgrades:
 * furniture for gold, carried over at once. The bed: lying down to rest, or going to sleep (a yawn, the
 * screen fading to black through the app's add-on, then asleep in it): a quarter of a level of rested
 * experience at most once every six hours, and the bed quest's credit.
 */

#include "Chat.h"
#include "ChatCommand.h"
#include "Config.h"
#include "Creature.h"
#include "DatabaseEnv.h"
#include "GameObject.h"
#include "GameTime.h"
#include "Group.h"
#include "BrillHome.h"
#include "BrillHomePatch.h"
#include "Log.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Pet.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "ScriptedGossip.h"
#include "Trainer.h"
#include "StringFormat.h"
#include "World.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <unordered_map>
#include <unordered_set>

namespace fs = std::filesystem;

namespace
{
    // (tools/build_sql.py)
    constexpr float HOUSE_X = 2275.0f, HOUSE_Y = 480.5f;
    constexpr uint32 HOUSE_MAP = 0;
    // Brill, where the house's and the town's phases apply (tools/build_town.py: BRILL_*).
    constexpr float BRILL_X = 2275.0f, BRILL_Y = 330.0f, BRILL_RADIUS = 165.0f;
    constexpr float NEAR_HOUSE = 35.0f;   // (Brill, and by the house at its north edge: tools/build_town.py)

    constexpr uint32 GO_BED = 970101, NPC_BED_CREDIT = 970111;
    constexpr uint32 NPC_DOG = 970112, NPC_FETCH_CREDIT = 970113, NPC_EARS_CREDIT = 970114, NPC_DOG_PET = 970115;
    constexpr uint32 QUEST_HOUSE = 970120, QUEST_WELCOME = 970121, QUEST_BED = 970122, QUEST_DOG = 970123;
    constexpr uint32 TEXT_JAMIE = 970140, TEXT_UPGRADES = 970141, TEXT_BED = 970142, TEXT_DOG = 970144, TEXT_DOG_WAITING = 970145;
    // Out the door, where the stick lands (the house's own (-1.9, -12): tools/build_sql.py).
    constexpr float STICK_X = 2263.1f, STICK_Y = 478.2f, STICK_Z = 33.9f;

    constexpr uint32 PHASE_CEDRIC = 0x100, PHASE_BED = 0x200, PHASE_DOG = 0x400;
    // A character's state: they've slept in the bed (Corn came); Corn is theirs (its quest
    // done); it's their pet (there was room for it).
    constexpr uint32 FLAG_SLEPT = 0x1, FLAG_DOG_ADOPTED = 0x2, FLAG_DOG_PET = 0x4;
    // A hunter's dog isn't their pet but one more beside it (the user: "you can have your current pets
    // out but also the dog. To a limit of 2 for regular hunters and 3 out at a time for beast masters"):
    // a companion that follows them and fights what they fight; a Beast Mastery hunter's first stabled
    // pet comes out beside it too.
    constexpr uint32 FLAG_COMPANION = 0x8;
    constexpr uint32 NPC_DOG_COMPANION = 970116, NPC_BEAST_COMPANION = 970117;
    constexpr uint32 SPELL_BESTIAL_WRATH = 19574;          // Beast Mastery's 41-point talent: a beast master
    constexpr uint32 SUMMON_PROPERTIES_ALLY_GUARDIAN = 61; // (the game's: an ally's guardian)
    constexpr float COMPANION_LEASH = 60.0f;
    // The hunter's pet spells a dog's keeper learns with it (Call, Dismiss, Revive, Feed Pet), and Mend
    // Pet's ranks by the level they're learnt at.
    constexpr uint32 PET_SPELLS[] = { 883, 2641, 982, 6991 };
    struct Rank { uint8 level; uint32 spell; };
    constexpr Rank MEND_PET[] = { { 12, 136 }, { 20, 3111 }, { 28, 3661 }, { 36, 3662 }, { 44, 13542 }, { 52, 13543 },
                                  { 60, 13544 }, { 68, 27046 }, { 74, 48989 }, { 80, 48990 } };
    constexpr uint32 PHASES_OURS = 0xFFFFFFFE;   // (the house's 0x100 to 0x20000, the town's lines' above it and 0x2 to 0x80: nothing of the game's in Brill is in those)

    // Carolai Anise (Brill's alchemy trainer): her five quests once Corn is the player's, ending in
    // the player's answer, lovers or friends (the rewards the same: the user's), and as lovers, her
    // moving into the house if they ask her. She's a yandere (the user's).
    constexpr uint32 CAROLAI = 2132, NPC_CAROLAI_VISIT = 970118, NPC_CAROLAI_HOME = 970119;
    constexpr uint32 NPC_TEA_CREDIT = 970150, NPC_LOCKET_CREDIT = 970151, NPC_LILY_CREDIT = 970152, NPC_ANSWER_CREDIT = 970153;
    constexpr uint32 GO_LOCKET = 970108, GO_LILY = 970109;
    constexpr uint32 QUEST_TONIC = 970124, QUEST_LOCKET = 970125, QUEST_GIFT = 970126, QUEST_TEA = 970127, QUEST_LILY = 970128;
    constexpr uint32 TEXT_CAROLAI_VISIT = 970146, TEXT_CAROLAI_HOME = 970147, TEXT_CAROLAI_ANSWER = 970148,
        TEXT_CAROLAI_LOVER = 970149, TEXT_CAROLAI_FRIEND = 970150, TEXT_LOCKET = 970151, TEXT_LILY = 970152, TEXT_CAROLAI_CALLING = 970153;
    // As friends, one day in five she has let herself in when they come home (the house's Carolai, in her
    // friend's words).
    constexpr uint32 CAROLAI_CALLS_EVERY = 5;
    constexpr uint32 PHASE_CAROLAI_VISIT = 0x10000, PHASE_CAROLAI_HOME = 0x20000;
    // The player's answer (the lily's quest), and whether she lives in the house.
    constexpr uint32 FLAG_LOVERS = 0x10, FLAG_FRIENDS = 0x20, FLAG_CAROLAI_HOME = 0x40;

    // The furniture Jamie has carried over: its phase bit, what she offers, its price in copper.
    struct Upgrade { uint32 phase; char const* offer; char const* done; uint32 price; };
    constexpr Upgrade UPGRADES[] = {
        { 0x0800, "A kitchen table and two chairs.", "A table and chairs, then. Somewhere to eat that isn't your lap.", 20000 },
        { 0x1000, "A wardrobe.", "A wardrobe. Your spare boots will thank you.", 15000 },
        { 0x2000, "A bookshelf.", "A bookshelf. I'll see if the Apothecaries have anything they're not using.", 10000 },
        { 0x4000, "A bearskin rug.", "A bearskin rug. The floors in those old farmhouses are cold as a crypt.", 5000 },
        { 0x8000, "A pot-bellied stove.", "A stove! Now it'll feel like someone lives there.", 30000 },
    };

    constexpr uint32 SENDER_UPGRADES = 1, SENDER_BUY = 2, SENDER_REST = 3, SENDER_SLEEP = 4;
    constexpr uint32 SENDER_FETCH = 5, SENDER_EARS = 6, SENDER_BRING = 7;
    // (Carolai's: senders the game's own options, all 0, never are)
    constexpr uint32 SENDER_LOVERS = 20, SENDER_FRIENDS = 21, SENDER_MOVE_IN = 22, SENDER_TEA = 23, SENDER_MOVE_OUT = 24, SENDER_HOLD = 25;
    constexpr uint32 SENDER_ASK_JAMIE = 26, SENDER_ASK_CAROLAI = 27;
    // (a sender none of the game's own menus use: the option this module adds to the hunter trainers')
    constexpr uint32 SENDER_TAME = 970190;
    constexpr uint32 SPELL_TAME_BEAST = 1515, SPELL_BEAST_LORE = 1462;
    constexpr uint8 TAME_LEVEL = 10;   // a hunter's, for Tame Beast

    // The bed (the game's duskwoodbed: 4.8 yards along its +x, its headboard there, the mattress 0.86 up).
    constexpr float MATTRESS_HEIGHT = 0.86f;
    constexpr float MATTRESS_ALONG = -0.2f;   // its middle, a little toward the foot from the bed's middle
    constexpr uint32 SLEEP_FADE_MS = 5000;
    constexpr uint32 SLEEP_DARK_MS = 2200;   // when the screen is black: into the bed then
    constexpr uint32 RESTED_EVERY = 6 * 3600;  // seconds between sleeps that give rested experience
    constexpr uint32 TEXT_EMOTE_YAWN_ID = 106;

    bool enabled = true;
    // Corn's looks: the game's pug (display 31174), in the user's coat where the module's patch is in the game
    // (src/BrillHomePatch.cpp); tools/build_sql.py: DOG_*
    constexpr uint32 DISPLAY_PUG = 31174;
    bool cornReady = false;
    uint32 DogDisplay() { return DISPLAY_PUG; }

    struct Home { uint32 upgrades = 0; uint32 lastRested = 0; uint32 flags = 0; };
    std::unordered_map<uint32, Home> homes;  // by the character's guid (low)
    std::unordered_map<uint32, uint32> sinceCheck;
    std::unordered_set<uint32> phasedHere;   // the characters Brill has put in its phases

    Home& HomeOf(Player* player)
    {
        uint32 guid = player->GetGUID().GetCounter();
        auto it = homes.find(guid);
        if (it != homes.end())
            return it->second;
        Home home;
        if (QueryResult result = CharacterDatabase.Query("SELECT `upgrades`, `last_rested`, `flags` FROM `brill_home` WHERE `guid` = {}", guid))
        {
            Field* fields = result->Fetch();
            home.upgrades = fields[0].Get<uint32>();
            home.lastRested = fields[1].Get<uint32>();
            home.flags = fields[2].Get<uint32>();
        }
        return homes[guid] = home;
    }

    void Save(Player* player)
    {
        Home const& home = HomeOf(player);
        CharacterDatabase.Execute("REPLACE INTO `brill_home` (`guid`, `upgrades`, `last_rested`, `flags`) VALUES ({}, {}, {}, {})",
            player->GetGUID().GetCounter(), home.upgrades, home.lastRested, home.flags);
    }

    bool OwnsHouse(Player* player) { return player->GetQuestRewardStatus(QUEST_WELCOME); }

    bool InBrill(Player* player)
    {
        return player->GetMapId() == HOUSE_MAP
            && (std::hypot(player->GetPositionX() - BRILL_X, player->GetPositionY() - BRILL_Y) < BRILL_RADIUS
                || std::hypot(player->GetPositionX() - HOUSE_X, player->GetPositionY() - HOUSE_Y) < NEAR_HOUSE);
    }

    // As friends: today's the day she's at the house (by the character and the day).
    bool FriendCalling(Player* player)
    {
        if (!(HomeOf(player).flags & FLAG_FRIENDS) || !OwnsHouse(player))
            return false;
        uint32 day = uint32(GameTime::GetGameTime().count() / 86400);
        return (player->GetGUID().GetCounter() + day) % CAROLAI_CALLS_EVERY == 0;
    }

    // The phases that are the player's near the house.
    uint32 HousePhases(Player* player)
    {
        uint32 mask = PHASEMASK_NORMAL;
        if (!player->GetQuestRewardStatus(QUEST_HOUSE))
            mask |= PHASE_CEDRIC;
        if (player->GetQuestStatus(QUEST_BED) != QUEST_STATUS_NONE)
            mask |= PHASE_BED;
        Home& home = HomeOf(player);
        if (OwnsHouse(player))
            mask |= home.upgrades;
        // Corn: from the first night in the bed until it's their pet
        if ((home.flags & FLAG_SLEPT) && !(home.flags & FLAG_DOG_PET))
            mask |= PHASE_DOG;
        // Carolai: in the house the evening after Jamie's gift (until the tea is drunk), and living there
        QuestStatus tea = player->GetQuestStatus(QUEST_TEA);
        if (player->GetQuestRewardStatus(QUEST_GIFT) && tea != QUEST_STATUS_COMPLETE && tea != QUEST_STATUS_REWARDED)
            mask |= PHASE_CAROLAI_VISIT;
        if ((home.flags & FLAG_CAROLAI_HOME) && (home.flags & FLAG_LOVERS))
            mask |= PHASE_CAROLAI_HOME;
        if (FriendCalling(player))
            mask |= PHASE_CAROLAI_HOME;
        return mask;
    }

    void UpdatePhases(Player* player)
    {
        if (!enabled)
            return;
        BrillTown::RefreshStages(player, InBrill(player));
        if (player->HasAuraType(SPELL_AURA_PHASE))
            return;
        uint32 guid = player->GetGUID().GetCounter();
        uint32 now = player->GetPhaseMask();
        // Out of Brill, the world's phase again, if it was Brill that phased them: never a phase something
        // else put them in (another module's, anywhere else in the world).
        if (!InBrill(player))
        {
            if (phasedHere.erase(guid) && (now & ~PHASEMASK_NORMAL) && !(now & ~(PHASEMASK_NORMAL | PHASES_OURS)))
                player->SetPhaseMask(PHASEMASK_NORMAL, true);
            return;
        }
        uint32 wanted = HousePhases(player) | BrillTown::Phases(player);
        phasedHere.insert(guid);
        if (wanted != now)
            player->SetPhaseMask(wanted, true);
    }

    void Yawn(Player* player)
    {
        WorldPacket data(SMSG_TEXT_EMOTE, 8 + 4 + 4 + 4 + 1);
        data << player->GetGUID();
        data << uint32(TEXT_EMOTE_YAWN_ID);
        data << uint32(0xFFFFFFFF);
        data << uint32(0);
        data << uint8(0);
        player->SendMessageToSet(&data, true);
    }

    // The app's add-on darkens the screen (its "fade", through Wrath Remix's add-on prefix, which any
    // realm's client reads: client/TouchAddon.kt).
    void FadeToBlack(Player* player, uint32 milliseconds)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_WHISPER, LANG_ADDON, player->GetGUID(), player->GetGUID(),
            Acore::StringFormat("WowRemix\tfade {} ", milliseconds), 0);
        player->SendDirectMessage(&data);
    }

    // Onto the bed, lying along it, the head at its headboard (facing its foot), then asleep.
    void LieDown(Player* player, GameObject* bed)
    {
        float o = bed->GetOrientation();
        float x = bed->GetPositionX() + MATTRESS_ALONG * std::cos(o);
        float y = bed->GetPositionY() + MATTRESS_ALONG * std::sin(o);
        float z = bed->GetPositionZ() + MATTRESS_HEIGHT;
        float facing = Position::NormalizeOrientation(o + float(M_PI));
        ObjectGuid guid = player->GetGUID();
        player->NearTeleportTo(x, y, z, facing);
        player->m_Events.AddEventAtOffset([guid]()
        {
            if (Player* sleeper = ObjectAccessor::FindPlayer(guid))
                sleeper->SetStandState(UNIT_STAND_STATE_SLEEP);
        }, 400ms);
    }

    void Sleep(Player* player, GameObject* bed)
    {
        Yawn(player);
        FadeToBlack(player, SLEEP_FADE_MS);
        ObjectGuid guid = player->GetGUID();
        ObjectGuid bedGuid = bed->GetGUID();
        player->m_Events.AddEventAtOffset([guid, bedGuid]()
        {
            Player* sleeper = ObjectAccessor::FindPlayer(guid);
            if (!sleeper || !sleeper->IsAlive() || !sleeper->IsInWorld())
                return;
            GameObject* bed = sleeper->GetMap()->GetGameObject(bedGuid);
            if (!bed || !sleeper->IsWithinDistInMap(bed, 10.0f))
                return;
            LieDown(sleeper, bed);
            sleeper->KilledMonsterCredit(NPC_BED_CREDIT);
            Home& home = HomeOf(sleeper);
            if (!(home.flags & FLAG_SLEPT))
            {
                // (the first night: they wake to find Corn there)
                home.flags |= FLAG_SLEPT;
                Save(sleeper);
            }
            uint32 now = uint32(GameTime::GetGameTime().count());
            if (sleeper->GetLevel() < sWorld->getIntConfig(CONFIG_MAX_PLAYER_LEVEL) && now - home.lastRested >= RESTED_EVERY)
            {
                home.lastRested = now;
                Save(sleeper);
                sleeper->SetRestBonus(sleeper->GetRestBonus() + sleeper->GetUInt32Value(PLAYER_NEXT_LEVEL_XP) / 4.0f);
                ChatHandler(sleeper->GetSession()).SendSysMessage("You wake feeling well rested.");
            }
        }, std::chrono::milliseconds(SLEEP_DARK_MS));
    }
}

namespace
{
    // The pet spells a keeper of the dog has, for their level (Mend Pet's ranks as a hunter learns them).
    void LearnPetSpells(Player* player)
    {
        for (uint32 spell : PET_SPELLS)
            if (!player->HasSpell(spell))
                player->learnSpell(spell);
        for (Rank const& rank : MEND_PET)
            if (player->GetLevel() >= rank.level && !player->HasSpell(rank.spell))
                player->learnSpell(rank.spell);
    }

    // Corn made the player's pet, as a hunter's tamed beast is: at their level, out beside them,
    // kept as their current pet. Not while they have a pet out or kept as current (a hunter's own, a
    // warlock's demon...): the dog waits in the house until there's room.
    bool GiveDog(Player* player)
    {
        Home& home = HomeOf(player);
        if (!(home.flags & FLAG_DOG_ADOPTED) || (home.flags & FLAG_DOG_PET))
            return false;
        // (a hunter's: one more beside their own, never in its place)
        if (player->getClass() == CLASS_HUNTER)
        {
            home.flags |= FLAG_DOG_PET | FLAG_COMPANION;
            Save(player);
            UpdatePhases(player);
            return true;
        }
        PetStable& stable = player->GetOrInitPetStable();
        if (player->GetPetGUID() || stable.CurrentPet || stable.GetUnslottedHunterPet())
            return false;
        // (it's theirs from here: a hunter's pet's every rule asks whether the keeper is one)
        home.flags |= FLAG_DOG_PET;
        Pet* pet = player->CreateTamedPetFrom(NPC_DOG_PET, 0);
        if (!pet)
        {
            home.flags &= ~FLAG_DOG_PET;
            return false;
        }
        Save(player);
        pet->SetUInt32Value(UNIT_FIELD_LEVEL, player->GetLevel() - 1);
        pet->GetMap()->AddToMap(pet->ToCreature(), true);
        pet->SetUInt32Value(UNIT_FIELD_LEVEL, player->GetLevel());
        player->SetMinion(pet, true);
        pet->InitTalentForLevel();
        pet->SavePetToDB(PET_SAVE_AS_CURRENT);
        player->PetSpellInitialize();
        LearnPetSpells(player);
        UpdatePhases(player);
        return true;
    }

    // A hunter's companions out: the dog, and a beast master's first stabled pet (its looks).
    struct Companions { ObjectGuid dog, beast; };
    std::unordered_map<uint32, Companions> companions;   // by the character's guid (low)

    bool CanHaveCompanions(Player* player)
    {
        return player->IsInWorld() && player->IsAlive() && !player->IsMounted() && !player->IsInFlight()
            && !player->GetVehicle() && !player->HasUnitState(UNIT_STATE_IN_FLIGHT);
    }

    void Unsummon(Player* player, ObjectGuid& guid)
    {
        if (guid)
            if (Creature* c = ObjectAccessor::GetCreature(*player, guid))
                c->DespawnOrUnsummon();
        guid.Clear();
    }

    void Summon(Player* player, ObjectGuid& guid, uint32 entry, uint32 display)
    {
        Creature* c = guid ? ObjectAccessor::GetCreature(*player, guid) : nullptr;
        if (c && c->IsAlive() && c->GetMapId() == player->GetMapId() && c->IsWithinDist(player, COMPANION_LEASH))
            return;
        Unsummon(player, guid);
        SummonPropertiesEntry const* properties = sSummonPropertiesStore.LookupEntry(SUMMON_PROPERTIES_ALLY_GUARDIAN);
        Position at = player->GetNearPosition(2.0f, float(M_PI) * (entry == NPC_DOG_COMPANION ? 0.75f : 1.25f));
        TempSummon* summon = player->SummonCreature(entry, at, TEMPSUMMON_MANUAL_DESPAWN, 0, 0, properties);
        if (!summon)
            return;
        if (display)
            summon->SetDisplayId(display);
        guid = summon->GetGUID();
    }

    void KeepCompanions(Player* player)
    {
        Home& home = HomeOf(player);
        if (!(home.flags & FLAG_COMPANION) || player->getClass() != CLASS_HUNTER)
            return;
        Companions& out = companions[player->GetGUID().GetCounter()];
        if (!CanHaveCompanions(player))
        {
            Unsummon(player, out.dog);
            Unsummon(player, out.beast);
            return;
        }
        Summon(player, out.dog, NPC_DOG_COMPANION, 0);
        PetStable* stable = player->GetPetStable();
        PetStable::PetInfo const* stabled = nullptr;
        if (player->HasSpell(SPELL_BESTIAL_WRATH) && stable)
            for (auto const& slot : stable->StabledPets)
                if (slot && slot->Type == HUNTER_PET)
                {
                    stabled = &*slot;
                    break;
                }
        if (stabled)
            Summon(player, out.beast, NPC_BEAST_COMPANION, stabled->DisplayId);
        else
            Unsummon(player, out.beast);
    }

    uint32 CompanionsOut(Player* player)
    {
        auto it = companions.find(player->GetGUID().GetCounter());
        if (it == companions.end())
            return 0;
        uint32 n = 0;
        for (ObjectGuid guid : { it->second.dog, it->second.beast })
            if (guid && ObjectAccessor::GetCreature(*player, guid))
                ++n;
        return n;
    }

    // Corn's own doings, seen by the player: shown, never said (it doesn't talk).
    void DogDoes(Creature* dog, Player* player, char const* what)
    {
        dog->TextEmote(what, player);
    }
}

namespace BrillHome
{
    bool Enabled() { return enabled; }
    uint32 Flags(Player* player) { return HomeOf(player).flags; }
    bool OwnsHouse(Player* player) { return ::OwnsHouse(player); }
    void RefreshPhases(Player* player) { UpdatePhases(player); }

    void SendUpgrades(Player* player, Creature* creature)
    {
        Home& home = HomeOf(player);
        ClearGossipMenuFor(player);
        for (uint32 i = 0; i < std::size(UPGRADES); ++i)
            if (!(home.upgrades & UPGRADES[i].phase))
                AddGossipItemFor(player, GOSSIP_ICON_VENDOR, UPGRADES[i].offer, SENDER_BUY, i,
                    "Have it carried over to your house?", UPGRADES[i].price, false);
        SendGossipMenuFor(player, TEXT_UPGRADES, creature->GetGUID());
    }

    bool HasUpgrade(Player* player, uint32 index)
    {
        return index < std::size(UPGRADES) && (HomeOf(player).upgrades & UPGRADES[index].phase);
    }

    bool GiveUpgrade(Player* player, uint32 index)
    {
        if (index >= std::size(UPGRADES) || HasUpgrade(player, index))
            return false;
        HomeOf(player).upgrades |= UPGRADES[index].phase;
        Save(player);
        UpdatePhases(player);
        return true;
    }

    void BuyUpgrade(Player* player, Creature* creature, uint32 index)
    {
        Home& home = HomeOf(player);
        if (index >= std::size(UPGRADES) || !::OwnsHouse(player) || (home.upgrades & UPGRADES[index].phase))
            return;
        Upgrade const& upgrade = UPGRADES[index];
        if (!player->HasEnoughMoney(upgrade.price))
        {
            creature->Whisper("You'll need a little more coin than that, I'm afraid.", LANG_UNIVERSAL, player);
            return;
        }
        player->ModifyMoney(-int32(upgrade.price));
        home.upgrades |= upgrade.phase;
        Save(player);
        creature->Whisper(upgrade.done, LANG_UNIVERSAL, player);
        UpdatePhases(player);
    }
}

class go_brill_home_bed : public GameObjectScript
{
public:
    go_brill_home_bed() : GameObjectScript("go_brill_home_bed") { }

    bool OnGossipHello(Player* player, GameObject* go) override
    {
        if (!enabled)
            return false;
        ClearGossipMenuFor(player);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Lie down to rest.", SENDER_REST, 0);
        AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Go to sleep.", SENDER_SLEEP, 0);
        SendGossipMenuFor(player, TEXT_BED, go->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, GameObject* go, uint32 sender, uint32 /*action*/) override
    {
        if (!enabled)
            return false;
        CloseGossipMenuFor(player);
        if (sender == SENDER_REST)
            LieDown(player, go);
        else if (sender == SENDER_SLEEP)
            Sleep(player, go);
        return true;
    }
};

class npc_brill_home_jamie : public CreatureScript
{
public:
    npc_brill_home_jamie() : CreatureScript("npc_brill_home_jamie") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!enabled)
            return false;
        ClearGossipMenuFor(player);
        if (creature->IsQuestGiver())
            player->PrepareQuestMenu(creature->GetGUID());
        if (OwnsHouse(player))
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "I'd like to make my house more of a home.", SENDER_UPGRADES, 0);
        if (player->GetQuestRewardStatus(QUEST_GIFT))
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Ask her about Carolai Anise.)", SENDER_ASK_CAROLAI, 0);
        uint32 townText = BrillTown::AddOptions(player, creature);
        SendGossipMenuFor(player, townText ? townText : TEXT_JAMIE, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 action) override
    {
        if (!enabled)
            return false;
        ClearGossipMenuFor(player);
        Home& home = HomeOf(player);
        (void)home;
        if (sender == SENDER_UPGRADES)
        {
            BrillHome::SendUpgrades(player, creature);
            return true;
        }
        if (sender == SENDER_ASK_CAROLAI)
        {
            CloseGossipMenuFor(player);
            uint32 flags = home.flags;
            char const* line = (flags & FLAG_CAROLAI_HOME) && (flags & FLAG_LOVERS)
                ? "She's moved in with you, then. I saw her carrying her bottles across the square. Well. It's your house, and your life. "
                  "If you ever want the key back, you know where the records are kept. I'll keep a spare. Just in case."
                : (flags & FLAG_LOVERS)
                ? "You and Carolai. I won't pretend I'm not worried, $n. But I've seen her smile at you, and I hadn't seen her smile in six years. "
                  "Maybe that counts for something. I still check my tea."
                : (flags & FLAG_FRIENDS)
                ? "Friends, is it? She still watches your door from her bench, you know. Friends don't usually. But she's been kinder to the "
                  "rest of us since. Brought me a salve for my hands last week. I had it tested first, of course."
                : "Carolai? We've an understanding. She doesn't send me any more perfume, and I don't tell the Deathguard about the last one.";
            std::string text = line;
            for (size_t at = text.find("$n"); at != std::string::npos; at = text.find("$n"))
                text.replace(at, 2, player->GetName());
            creature->Whisper(text, LANG_UNIVERSAL, player);
            return true;
        }
        CloseGossipMenuFor(player);
        if (sender == SENDER_BUY)
            BrillHome::BuyUpgrade(player, creature, action);
        return true;
    }
};

class npc_brill_home_mastiff : public CreatureScript
{
public:
    npc_brill_home_mastiff() : CreatureScript("npc_brill_home_mastiff") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!enabled)
            return false;
        ClearGossipMenuFor(player);
        if (creature->IsQuestGiver())
            player->PrepareQuestMenu(creature->GetGUID());
        if (player->GetQuestStatus(QUEST_DOG) == QUEST_STATUS_INCOMPLETE)
        {
            if (player->GetReqKillOrCastCurrentCount(QUEST_DOG, NPC_FETCH_CREDIT) < 3)
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Throw the stick.)", SENDER_FETCH, 0);
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Scratch behind its ears.)", SENDER_EARS, 0);
        }
        bool waiting = (HomeOf(player).flags & FLAG_DOG_ADOPTED) && !(HomeOf(player).flags & FLAG_DOG_PET);
        if (waiting)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Whistle for it to follow you.)", SENDER_BRING, 0);
        SendGossipMenuFor(player, waiting ? TEXT_DOG_WAITING : TEXT_DOG, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 /*action*/) override
    {
        if (!enabled)
            return false;
        CloseGossipMenuFor(player);
        ObjectGuid playerGuid = player->GetGUID();
        if (sender == SENDER_FETCH)
        {
            if (creature->HasUnitState(UNIT_STATE_ROAMING_MOVE) || creature->m_Events.HasEvents())
                return true;
            DogDoes(creature, player, "(Corn's ears go up. He watches the stick sail out the door, then bolts after it, wheezing.)");
            Position home = creature->GetHomePosition();
            creature->GetMotionMaster()->MovePoint(1, STICK_X, STICK_Y, STICK_Z);
            creature->m_Events.AddEventAtOffset([creature, home]()
            {
                creature->GetMotionMaster()->MovePoint(2, home.GetPositionX(), home.GetPositionY(), home.GetPositionZ());
            }, 3500ms);
            creature->m_Events.AddEventAtOffset([creature, home, playerGuid]()
            {
                creature->SetFacingTo(home.GetOrientation());
                Player* thrower = ObjectAccessor::FindPlayer(playerGuid);
                if (!thrower)
                    return;
                uint32 done = thrower->GetReqKillOrCastCurrentCount(QUEST_DOG, NPC_FETCH_CREDIT);
                DogDoes(creature, thrower, done == 0 ? "(Corn trots back and drops the stick at your feet, very pleased with himself.)"
                    : done == 1 ? "(Back again, tail going like a flag. The stick is a good deal wetter than before.)"
                    : "(Corn brings the stick back, then lies down with it and starts to chew. He seems to think he has won.)");
                thrower->KilledMonsterCredit(NPC_FETCH_CREDIT);
            }, 7000ms);
            return true;
        }
        if (sender == SENDER_EARS)
        {
            DogDoes(creature, player, "(Corn leans his whole small weight against your leg, glowing eyes half closed, and snorts happily.)");
            player->KilledMonsterCredit(NPC_EARS_CREDIT);
            return true;
        }
        if (sender == SENDER_BRING && !GiveDog(player))
            DogDoes(creature, player, "(Corn looks at whatever is already following you, and sits back down by the door.)");
        return true;
    }

    // Its quest done: the dog is theirs, their pet now if there's room.
    bool OnQuestReward(Player* player, Creature* creature, Quest const* quest, uint32 /*opt*/) override
    {
        if (!enabled || quest->GetQuestId() != QUEST_DOG)
            return false;
        HomeOf(player).flags |= FLAG_DOG_ADOPTED;
        Save(player);
        if (!GiveDog(player))
            DogDoes(creature, player, "(Corn looks at whatever is already following you, and sits back down by the door to wait.)");
        return false;
    }
};

// Carolai Anise at her bench: her own menu (her quests, her training), and the player's answer to the
// lily's question, and as lovers, asking her to move in.
class npc_brill_home_carolai : public CreatureScript
{
public:
    npc_brill_home_carolai() : CreatureScript("npc_brill_home_carolai") { }

    static bool Answering(Player* player)
    {
        return player->GetQuestStatus(QUEST_LILY) == QUEST_STATUS_INCOMPLETE
            && player->GetReqKillOrCastCurrentCount(QUEST_LILY, NPC_LILY_CREDIT) > 0
            && player->GetReqKillOrCastCurrentCount(QUEST_LILY, NPC_ANSWER_CREDIT) == 0;
    }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!enabled)
            return false;
        player->PrepareGossipMenu(creature, creature->GetCreatureTemplate()->GossipMenuId, true);
        Home& home = HomeOf(player);
        uint32 text = player->GetGossipTextId(creature);
        if (Answering(player))
        {
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Give her the lily and take her hand.) I'm keeping it, Carolai. Yes.", SENDER_LOVERS, 0);
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Give her the lily.) You mean a great deal to me, Carolai. As a friend.", SENDER_FRIENDS, 0);
            text = TEXT_CAROLAI_ANSWER;
        }
        else if (home.flags & FLAG_LOVERS)
        {
            if (!(home.flags & FLAG_CAROLAI_HOME) && OwnsHouse(player))
                AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Would you like to move in with me?", SENDER_MOVE_IN, 0);
            text = TEXT_CAROLAI_LOVER;
        }
        else if (home.flags & FLAG_FRIENDS)
            text = TEXT_CAROLAI_FRIEND;
        if (player->GetQuestRewardStatus(QUEST_GIFT))
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Ask her about Jamie Nore.)", SENDER_ASK_JAMIE, 0);
        // (the town's lines' options for her; their greetings don't take the place of hers)
        BrillTown::AddOptions(player, creature);
        SendGossipMenuFor(player, text, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 /*action*/) override
    {
        if (!enabled || (sender != SENDER_LOVERS && sender != SENDER_FRIENDS && sender != SENDER_MOVE_IN && sender != SENDER_ASK_JAMIE))
            return false;   // (her training and the game's own options)
        CloseGossipMenuFor(player);
        Home& home = HomeOf(player);
        if (sender == SENDER_ASK_JAMIE)
        {
            // (the gift's still between them, whatever the player answered)
            char const* line = (home.flags & FLAG_LOVERS)
                ? "Jamie Nore keeps the town's records. Births, deaths, deeds. She wrote your name in her ledger before I ever said it aloud. "
                  "I don't like other people having your name written down. That's all. That's all it is."
                : (home.flags & FLAG_FRIENDS)
                ? "Jamie and I are... civil. She checks her tea before she drinks it when I'm in the room. I think that's rather rude, don't you?"
                : "Jamie Nore is a very capable woman with a great many friends. She'd be missed. Everyone says so.";
            creature->Whisper(line, LANG_UNIVERSAL, player);
            return true;
        }
        if (sender == SENDER_MOVE_IN)
        {
            if (!(home.flags & FLAG_LOVERS) || (home.flags & FLAG_CAROLAI_HOME))
                return true;
            home.flags |= FLAG_CAROLAI_HOME;
            Save(player);
            creature->HandleEmoteCommand(EMOTE_ONESHOT_YES);
            creature->Whisper("I've had my things packed since the day you brought my locket home. I'll be there before you are. "
                "I'll always be there before you are.", LANG_UNIVERSAL, player);
            return true;
        }
        if (!Answering(player))
            return true;
        bool lovers = sender == SENDER_LOVERS;
        home.flags = (home.flags & ~(FLAG_LOVERS | FLAG_FRIENDS)) | (lovers ? FLAG_LOVERS : FLAG_FRIENDS);
        Save(player);
        player->KilledMonsterCredit(NPC_ANSWER_CREDIT);
        if (lovers)
        {
            creature->HandleEmoteCommand(EMOTE_ONESHOT_SHY);
            creature->Whisper("Then you're mine, and I'm yours. Nothing will ever take you from me. Not Jamie. Not the Scourge. "
                "Not anyone. I'll make sure of it.", LANG_UNIVERSAL, player);
        }
        else
            creature->Whisper("Friends. Of course. Of course we are. Friends look after each other, don't they? I'll go on looking "
                "after you. You won't even notice.", LANG_UNIVERSAL, player);
        return true;
    }
};

// Carolai in the player's house the evening after Jamie's gift: tea, and the locket opened.
class npc_brill_home_carolai_visit : public CreatureScript
{
public:
    npc_brill_home_carolai_visit() : CreatureScript("npc_brill_home_carolai_visit") { }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!enabled)
            return false;
        ClearGossipMenuFor(player);
        if (creature->IsQuestGiver())
            player->PrepareQuestMenu(creature->GetGUID());
        if (player->GetQuestStatus(QUEST_TEA) == QUEST_STATUS_INCOMPLETE)
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Sit down and drink the tea.)", SENDER_TEA, 0);
        SendGossipMenuFor(player, TEXT_CAROLAI_VISIT, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 /*action*/) override
    {
        if (!enabled)
            return false;
        CloseGossipMenuFor(player);
        if (sender != SENDER_TEA || player->GetQuestStatus(QUEST_TEA) != QUEST_STATUS_INCOMPLETE)
            return true;
        creature->Whisper("(Carolai watches you drink every sip. Then she opens the locket you brought back from Solliden. On one side, "
            "her mother's painted face. On the other, coiled neatly under the glass, a lock of hair. Yours.)", LANG_UNIVERSAL, player);
        creature->Whisper("I took it while you were sleeping. You never stir. Not even when the dog barks. I'm not frightening you, "
            "am I? Come to the shop when you're ready. There's something I need to say properly, and I won't say it in a kitchen.",
            LANG_UNIVERSAL, player);
        creature->HandleEmoteCommand(EMOTE_ONESHOT_BOW);
        ObjectGuid guid = player->GetGUID();
        // (she slips out a moment later: the visit's phase goes with the credit)
        player->m_Events.AddEventAtOffset([guid]()
        {
            if (Player* host = ObjectAccessor::FindPlayer(guid))
                host->KilledMonsterCredit(NPC_TEA_CREDIT);
        }, 4s);
        return true;
    }
};

// Carolai in the house: living there (lovers, asked to move in), or calling as a friend now and then. She
// keeps busy by turns: her alchemy table, tea at the stove, sitting with the dog, reading at the shelf.
struct npc_brill_home_carolai_homeAI : public ScriptedAI
{
    npc_brill_home_carolai_homeAI(Creature* creature) : ScriptedAI(creature) { }

    // (the house's: tools/build_sql.py's places, turned to what she's doing)
    struct Spot { float x, y, o; uint32 emote; bool sit; };
    static constexpr float FLOOR = 34.06f;
    static constexpr Spot SPOTS[] = {
        { 2272.91f, 483.31f, 1.920f, EMOTE_STATE_USE_STANDING, false },   // her alchemy table (the house's -3.35, -1.0)
        { 2279.47f, 477.87f, 0.349f, EMOTE_STATE_USE_STANDING, false },   // the kettle on the stove (the house's 4.0, 3.3)
        { 2277.82f, 480.20f, 0.349f, 0, true },                           // with the dog, by its bed (the house's 1.25, 2.55)
        { 2278.97f, 477.79f, 5.061f, EMOTE_STATE_USE_STANDING, false },   // a book from the shelf (the house's 3.9, 2.8)
    };
    uint32 next = 5000, spot = 0;
    bool moving = false;

    void Reset() override { next = urand(5000, 15000); }

    void MovementInform(uint32 type, uint32 id) override
    {
        if (type != POINT_MOTION_TYPE || id != 1 || spot >= std::size(SPOTS))
            return;
        moving = false;
        Spot const& s = SPOTS[spot];
        me->SetFacingTo(s.o);
        me->SetUInt32Value(UNIT_NPC_EMOTESTATE, s.emote);
        if (s.sit)
            me->SetStandState(UNIT_STAND_STATE_SIT);
    }

    void UpdateAI(uint32 diff) override
    {
        if (me->IsInCombat() || moving)
            return;
        if (next > diff)
        {
            next -= diff;
            return;
        }
        next = urand(45000, 90000);
        spot = urand(0, std::size(SPOTS) - 1);
        me->SetUInt32Value(UNIT_NPC_EMOTESTATE, 0);
        me->SetStandState(UNIT_STAND_STATE_STAND);
        moving = true;
        me->GetMotionMaster()->MovePoint(1, SPOTS[spot].x, SPOTS[spot].y, FLOOR);
    }
};

class npc_brill_home_carolai_home : public CreatureScript
{
public:
    npc_brill_home_carolai_home() : CreatureScript("npc_brill_home_carolai_home") { }

    CreatureAI* GetAI(Creature* creature) const override { return new npc_brill_home_carolai_homeAI(creature); }

    bool OnGossipHello(Player* player, Creature* creature) override
    {
        if (!enabled)
            return false;
        ClearGossipMenuFor(player);
        Home& home = HomeOf(player);
        bool lovers = (home.flags & FLAG_LOVERS) && (home.flags & FLAG_CAROLAI_HOME);
        if (lovers)
        {
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "(Hold her for a while.)", SENDER_HOLD, 0);
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Would you like some time back at your shop?", SENDER_MOVE_OUT, 0);
        }
        SendGossipMenuFor(player, lovers ? TEXT_CAROLAI_HOME : TEXT_CAROLAI_CALLING, creature->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 /*action*/) override
    {
        if (!enabled)
            return false;
        CloseGossipMenuFor(player);
        Home& home = HomeOf(player);
        if (!(home.flags & FLAG_LOVERS) || !(home.flags & FLAG_CAROLAI_HOME))
            return true;
        if (sender == SENDER_HOLD)
        {
            creature->HandleEmoteCommand(EMOTE_ONESHOT_SHY);
            creature->Whisper("(She is cold, and very still, and holds on long after you would have let go.) Don't go anywhere. "
                "Promise me.", LANG_UNIVERSAL, player);
        }
        else if (sender == SENDER_MOVE_OUT)
        {
            home.flags &= ~FLAG_CAROLAI_HOME;
            Save(player);
            creature->Whisper("Of course. I'll go. I'll only be across the square. I can see your window from my bench, you know. "
                "Ask me again whenever you like. I'll be watching for it.", LANG_UNIVERSAL, player);
            UpdatePhases(player);
        }
        return true;
    }
};

// Her keepsakes: her mother's locket at Solliden Farmstead, and the moonpetal lily at Brightwater Lake.
class go_brill_home_keepsake : public GameObjectScript
{
public:
    go_brill_home_keepsake() : GameObjectScript("go_brill_home_keepsake") { }

    bool OnGossipHello(Player* player, GameObject* go) override
    {
        if (!enabled)
            return false;
        bool locket = go->GetEntry() == GO_LOCKET;
        uint32 quest = locket ? QUEST_LOCKET : QUEST_LILY, credit = locket ? NPC_LOCKET_CREDIT : NPC_LILY_CREDIT;
        ChatHandler chat(player->GetSession());
        // (said, so a click is never answered by nothing: the user clicked the lily and nothing happened)
        if (player->GetQuestStatus(quest) != QUEST_STATUS_INCOMPLETE)
        {
            chat.SendSysMessage(locket ? "An old footlocker. Whatever was in it isn't yours to take."
                                       : "A moonpetal lily, pale and faintly bright. You leave it where it grows.");
            return true;
        }
        if (player->GetReqKillOrCastCurrentCount(quest, credit) > 0)
        {
            chat.SendSysMessage(locket ? "You have Carolai's locket already. Bring it to her in Brill."
                                       : "You have a lily already. Bring it to Carolai in Brill.");
            return true;
        }
        ClearGossipMenuFor(player);
        SendGossipMenuFor(player, locket ? TEXT_LOCKET : TEXT_LILY, go->GetGUID());
        player->KilledMonsterCredit(credit);
        // (the game gives no quest credit in a raid group: a party of the realm's bots made a raid)
        if (player->GetReqKillOrCastCurrentCount(quest, credit) == 0)
            chat.SendSysMessage(player->GetGroup() && player->GetGroup()->isRaidGroup()
                ? "The game doesn't count this in a raid group: leave the raid (or make it a party) and try again."
                : "This didn't count for the quest: try again in a moment.");
        return true;
    }
};

// A hunter's companion (the dog, or a beast master's stabled pet beside it): at its keeper's side, and
// at whatever they fight: their target, or whatever is fighting them.
struct npc_brill_home_companionAI : public ScriptedAI
{
    npc_brill_home_companionAI(Creature* creature) : ScriptedAI(creature) { }

    void Follow()
    {
        if (Unit* owner = me->GetOwner())
            if (me->GetMotionMaster()->GetCurrentMovementGeneratorType() != FOLLOW_MOTION_TYPE)
                me->GetMotionMaster()->MoveFollow(owner, PET_FOLLOW_DIST,
                    me->GetEntry() == NPC_DOG_COMPANION ? float(M_PI) * 0.75f : float(M_PI) * 1.25f);
    }

    void EnterEvadeMode(EvadeReason /*why*/) override
    {
        me->CombatStop(true);
        me->GetThreatMgr().ClearAllThreat();
        Follow();
    }

    void UpdateAI(uint32 /*diff*/) override
    {
        Unit* owner = me->GetOwner();
        if (!owner)
            return;
        Unit* target = me->GetVictim();
        if (!target || !target->IsAlive() || !me->IsValidAttackTarget(target))
        {
            Unit* wanted = owner->IsInCombat() ? (owner->GetVictim() ? owner->GetVictim() : owner->getAttackerForHelper()) : nullptr;
            if (wanted && wanted->IsAlive() && me->IsValidAttackTarget(wanted))
                AttackStart(wanted);
            else
            {
                if (me->GetVictim())
                    EnterEvadeMode(EVADE_REASON_OTHER);
                Follow();
                return;
            }
        }
        DoMeleeAttackIfReady();
    }
};

class npc_brill_home_companion : public CreatureScript
{
public:
    npc_brill_home_companion() : CreatureScript("npc_brill_home_companion") { }
    CreatureAI* GetAI(Creature* creature) const override { return new npc_brill_home_companionAI(creature); }
};

// The hunter trainers teach a dog's keeper who isn't a hunter to tame beasts, as they do hunters: Tame
// Beast and Beast Lore (under General in their spellbook), from a hunter's level for it.
class BrillHomeHunterTrainers : public AllCreatureScript
{
public:
    BrillHomeHunterTrainers() : AllCreatureScript("BrillHomeHunterTrainers") { }

    static bool HunterTrainer(Creature* creature)
    {
        Trainer::Trainer const* trainer = sObjectMgr->GetTrainer(creature->GetEntry());
        return trainer && trainer->GetTrainerType() == Trainer::Type::Class && trainer->GetTrainerRequirement() == CLASS_HUNTER;
    }

    static bool Learner(Player* player)
    {
        return enabled && player->getClass() != CLASS_HUNTER && (HomeOf(player).flags & FLAG_DOG_PET)
            && !(player->HasSpell(SPELL_TAME_BEAST) && player->HasSpell(SPELL_BEAST_LORE));
    }

    // Their own menu, with the module's option at its end.
    bool CanCreatureGossipHello(Player* player, Creature* creature) override
    {
        if (!Learner(player) || !HunterTrainer(creature))
            return false;
        player->PrepareGossipMenu(creature, creature->GetCreatureTemplate()->GossipMenuId, true);
        AddGossipItemFor(player, GOSSIP_ICON_TRAINER, "Teach me to tame beasts, as you would a hunter.", SENDER_TAME, 0);
        player->SendPreparedGossip(creature);
        return true;
    }

    bool CanCreatureGossipSelect(Player* player, Creature* creature, uint32 sender, uint32 /*action*/) override
    {
        if (sender != SENDER_TAME)
            return false;
        CloseGossipMenuFor(player);
        if (!Learner(player) || !HunterTrainer(creature))
            return true;
        if (player->GetLevel() < TAME_LEVEL)
        {
            creature->Whisper("Your dog trusts you, I'll grant that. Come back when you've a few more seasons behind you.", LANG_UNIVERSAL, player);
            return true;
        }
        if (!player->HasSpell(SPELL_TAME_BEAST))
            player->learnSpell(SPELL_TAME_BEAST);
        if (!player->HasSpell(SPELL_BEAST_LORE))
            player->learnSpell(SPELL_BEAST_LORE);
        creature->Whisper("A beast already follows you of its own will: that's the hard part. The rest is patience, a steady hand, and something good to eat in your pack.",
            LANG_UNIVERSAL, player);
        return true;
    }
};

class BrillHomePlayer : public PlayerScript
{
public:
    BrillHomePlayer() : PlayerScript("BrillHomePlayer", { PLAYERHOOK_ON_UPDATE, PLAYERHOOK_ON_LOGOUT, PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_LEVEL_CHANGED, PLAYERHOOK_ON_PLAYER_IS_CLASS }) { }

    // (their house read before anything asks: the class question below reads it from memory)
    void OnPlayerLogin(Player* player) override
    {
        if (enabled && (HomeOf(player).flags & FLAG_DOG_PET))
            LearnPetSpells(player);
        if (enabled)
            BrillTown::KeepOutOfTheGround(player, true);
    }

    void OnPlayerLevelChanged(Player* player, uint8 /*oldLevel*/) override
    {
        if (enabled && (HomeOf(player).flags & FLAG_DOG_PET))
            LearnPetSpells(player);
    }

    // A keeper of the dog is a hunter wherever the game asks about pets (their pet's kind, the stable
    // master, Tame Beast, the pet's training and happiness): its every rule for a hunter's pet.
    Optional<bool> OnPlayerIsClass(Player const* player, Classes playerClass, ClassContext context) override
    {
        if (!enabled || playerClass != CLASS_HUNTER || context != CLASS_CONTEXT_PET)
            return std::nullopt;
        auto it = homes.find(player->GetGUID().GetCounter());
        if (it != homes.end() && (it->second.flags & FLAG_DOG_PET))
            return true;
        return std::nullopt;
    }

    // Once a second: in the house's phases near it, out of them away from it.
    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!enabled)
            return;
        uint32& since = sinceCheck[player->GetGUID().GetCounter()];
        since += diff;
        if (since < 1000)
            return;
        since = 0;
        if (BrillTown::KeepOutOfTheGround(player, false))
            return;
        UpdatePhases(player);
        KeepCompanions(player);
        // An adopted dog keeps its saved looks across the app's updates: given Corn's.
        if (Pet* dog = player->GetPet(); dog && dog->GetEntry() == NPC_DOG_PET && dog->GetNativeDisplayId() != DogDisplay())
        {
            dog->SetNativeDisplayId(DogDisplay());
            dog->SetDisplayId(DogDisplay());
            dog->SavePetToDB(PET_SAVE_AS_CURRENT);
        }
    }

    void OnPlayerLogout(Player* player) override
    {
        auto out = companions.find(player->GetGUID().GetCounter());
        if (out != companions.end())
        {
            Unsummon(player, out->second.dog);
            Unsummon(player, out->second.beast);
            companions.erase(out);
        }
        homes.erase(player->GetGUID().GetCounter());
        sinceCheck.erase(player->GetGUID().GetCounter());
        phasedHere.erase(player->GetGUID().GetCounter());
        BrillTown::Forget(player);
    }
};

using namespace Acore::ChatCommands;

// Game masters' (CI's realm test): .brillhome state says what the house shows the character (their
// phases, the furniture bought, the rested experience, how they're lying or standing, where they are,
// which of the quests are done); .brillhome sleep goes to sleep in the nearest bed, as its menu does.
class BrillHomeCommands : public CommandScript
{
public:
    BrillHomeCommands() : CommandScript("BrillHomeCommands") { }

    ChatCommandTable GetCommands() const override
    {
        static ChatCommandTable brillHomeTable =
        {
            { "state", HandleState, SEC_GAMEMASTER, Console::No },
            { "sleep", HandleSleep, SEC_GAMEMASTER, Console::No },
            { "adopt", HandleAdopt, SEC_GAMEMASTER, Console::No },
            { "use", HandleUse, SEC_GAMEMASTER, Console::No },
        };
        static ChatCommandTable commandTable =
        {
            { "brillhome", brillHomeTable },
        };
        return commandTable;
    }

    static bool HandleState(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        UpdatePhases(player);
        handler->PSendSysMessage("Brill home: phases 0x{:X} upgrades 0x{:X} rested {} stand {} at {:.1f} {:.1f} {:.1f} facing {:.2f} quests {}{}{}",
            player->GetPhaseMask(), HomeOf(player).upgrades, uint32(player->GetRestBonus()), uint32(player->getStandState()),
            player->GetPositionX(), player->GetPositionY(), player->GetPositionZ(), player->GetOrientation(),
            player->GetQuestRewardStatus(QUEST_HOUSE) ? 1 : 0, player->GetQuestRewardStatus(QUEST_WELCOME) ? 1 : 0,
            player->GetQuestRewardStatus(QUEST_BED) ? 1 : 0);
        // and the dog: the house's flags, the pet out (its entry, its kind: 1 a hunter's), whether the game
        // counts them a hunter for pets, and whether they have Call Pet and Mend Pet
        Pet* pet = player->GetPet();
        handler->PSendSysMessage("Brill home: flags 0x{:X} pet {} kind {} hunterpets {} callpet {} mendpet {} tame {} companions {}",
            HomeOf(player).flags, pet ? pet->GetEntry() : 0, pet ? uint32(pet->getPetType()) : 9,
            player->IsClass(CLASS_HUNTER, CLASS_CONTEXT_PET) ? 1 : 0, player->HasSpell(883) ? 1 : 0, player->HasSpell(136) ? 1 : 0,
            player->HasSpell(SPELL_TAME_BEAST) ? 1 : 0, CompanionsOut(player));
        handler->PSendSysMessage("Brill home: carolai {}{}{}{}{}", player->GetQuestRewardStatus(QUEST_TONIC) ? 1 : 0,
            player->GetQuestRewardStatus(QUEST_LOCKET) ? 1 : 0, player->GetQuestRewardStatus(QUEST_GIFT) ? 1 : 0,
            player->GetQuestRewardStatus(QUEST_TEA) ? 1 : 0, player->GetQuestRewardStatus(QUEST_LILY) ? 1 : 0);
        return true;
    }

    // The nearest of Carolai's keepsakes (10 yards) used, as clicking it does.
    static bool HandleUse(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        GameObject* go = player->FindNearestGameObject(GO_LOCKET, 10.0f);
        if (!go)
            go = player->FindNearestGameObject(GO_LILY, 10.0f);
        if (!go)
        {
            handler->SendSysMessage("Brill home: no keepsake within 10 yards.");
            return true;
        }
        go->Use(player);
        handler->PSendSysMessage("Brill home: used {}", go->GetEntry());
        return true;
    }

    // The dog theirs as its quest's end makes it (without the house's quests before it).
    static bool HandleAdopt(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        HomeOf(player).flags |= FLAG_SLEPT | FLAG_DOG_ADOPTED;
        Save(player);
        handler->PSendSysMessage("Brill home: adopted {}", GiveDog(player) ? 1 : 0);
        return true;
    }

    static bool HandleSleep(ChatHandler* handler)
    {
        Player* player = handler->GetSession()->GetPlayer();
        GameObject* bed = player->FindNearestGameObject(GO_BED, 30.0f);
        if (!bed)
        {
            handler->SendSysMessage("Brill home: no bed within 30 yards.");
            return true;
        }
        Sleep(player, bed);
        handler->SendSysMessage("Brill home: sleeping.");
        return true;
    }
};

class BrillHomeWorld : public WorldScript
{
public:
    BrillHomeWorld() : WorldScript("BrillHomeWorld", { WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_LOAD_CUSTOM_DATABASE_TABLE }) { }

    // (on Wrath Remix's realm the game's patch-<locale>-V is set aside as the configuration is read, before
    // Remix's own patch is made from the game)
    void OnAfterConfigLoad(bool reload) override
    {
        enabled = sConfigMgr->GetOption<bool>("BrillHome.Enable", true);
        fs::path data = ClientData();
        if (!reload && !enabled && !data.empty())
            BrillHome::SetPatchAside(data, Log);
    }

    // The town's questlines, once its tables are loaded; then the game's patch.
    void OnLoadCustomDatabaseTable() override
    {
        if (enabled)
            BrillTown::Load();
        fs::path data = ClientData();
        if (!enabled || data.empty())
            return;
        // Corn and the cellar in the game: patch-<locale>-V, after the Worgen's and Goblins' patch-U and the allied
        // races' patch-V are made (as the configuration is read), before the Skyborne's patch-Z.
        fs::path module = fs::path(sConfigMgr->GetOption<std::string>("SourceDirectory", "")) / "modules" / "mod-brill-home" / "data";
        BrillHome::UpdatePatch(module / "client", data, Log, cornReady);
    }

private:
    static void Log(std::string const& line) { LOG_INFO("module", "Brill home: {}", line); }

    static fs::path ClientData()
    {
        char const* client = std::getenv("WOW_CLIENT_DIR");
        if (!client || !*client)
            return {};
        fs::path data = fs::path(client) / "Data";
        std::error_code error;
        return fs::is_directory(data, error) ? data : fs::path();
    }
};

void AddBrillHomeScripts()
{
    new go_brill_home_bed();
    new npc_brill_home_jamie();
    new BrillHomePlayer();
    new BrillHomeWorld();
    new BrillHomeCommands();
    new npc_brill_home_mastiff();
    new BrillHomeHunterTrainers();
    new npc_brill_home_companion();
    new npc_brill_home_carolai();
    new npc_brill_home_carolai_visit();
    new npc_brill_home_carolai_home();
    new go_brill_home_keepsake();
    BrillTown::AddScripts();
}
