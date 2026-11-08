// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The opening (WrathRemix.Intro, STORY.md): a new Timerunner is a veteran of the war against the
 * Lich King, some time after his fall, drinking with three friends in their faction's tavern (the
 * Gilded Rose in Stormwind, the Broken Tusk in Orgrimmar). They toast the Frozen Throne, remember
 * the Wrathgate and Ulduar, and drink to the one of them who didn't come home from Icecrown. Then
 * the room stops, mid-toast, and Moratari walks in: "I'm sorry, hero. I need you."
 *
 * She takes them back into the war's last battle, at the Broken Front in Icecrown: Tirion and the
 * Argent Crusade, the Scourge pouring out of the snow, the Lich King himself, until time stops
 * under Frostmourne. Then through what his reign cost, three moments she holds still for them: the
 * Wrathgate after the plague, Wintergarde under Naxxramas, Icecrown's fields where the val'kyr
 * raise the fallen. "We can stop all of this. We can undo it." And on to the Infinite Bazaar,
 * years earlier, where Eternus explains.
 *
 * It is the Timerunner's alone: a phase of its own (no one else there, none of the places' own
 * creatures), everyone in it summoned for them. Each act's steps belong to it: they start once the
 * Timerunner has arrived (a far journey keeps them on a loading screen a while), and a step of an
 * act that is over does nothing. In the battle they are the hero they were, the Light's wings on
 * them; nothing can hurt them, and the dead fall to them in a blow or three. Once seen it is not
 * seen again (remix_character.intro); one cut short (a logout, a crash: wherever it left them)
 * plays again from the tavern at the next login. Death knights, who have Acherus, and the realm's
 * bots don't have it. `.remix intro` plays it for a game master, `.remix intro skip` ends it.
 *
 * Each act opens from the dark: the app's add-on (TouchAddon.kt) holds a curtain over the screen,
 * with where and when the act is written on it, from the moment the Timerunner is sent there (a
 * new one's from before their first loading screen ends) until the game has finished loading the
 * place (its frames run smoothly again: the add-on says "settled"), and then lifts it over a few
 * seconds as the act begins. A phone loads a city or a battlefield choppily for a while; none of
 * that is seen. Without the add-on (CI's test client answers the curtain at once) an act waits
 * WrathRemix.Intro.SettleSeconds at most.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Config.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "DBCStores.h"
#include "GameObject.h"
#include "Log.h"
#include "Map.h"
#include "MapMgr.h"
#include "ObjectAccessor.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "RaceMgr.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "SpellAuras.h"
#include "StringFormat.h"
#include "Random.h"
#include "TemporarySummon.h"
#include "Timer.h"
#include <atomic>
#include <cmath>
#include <functional>
#include <iterator>
#include <memory>
#include <mutex>
#include <string>
#include <chrono>
#include <unordered_map>
#include <vector>

using namespace WrathRemix;

namespace
{
    constexpr uint32 PHASE_INTRO = 16384;

    // The curtain: dark at once for CURTAIN_MS at most (the add-on lifts it by itself after that),
    // lifted over LIFT_MS once the client has settled (or SettleSeconds are up); never sooner than
    // SETTLE_LEAST_MS after the Timerunner is there, so the act's people are in place under it.
    constexpr uint32 CURTAIN_MS = 45000, LIFT_MS = 2500, SETTLE_LEAST_MS = 1500, SETTLE_POLL_MS = 250;
    // What the curtain says: where and when the act is (" | " a new line).
    char const* const CAPTION_TAVERN_A = "The Gilded Rose, Stormwind | Some months after the fall of the Lich King";
    char const* const CAPTION_TAVERN_H = "The Broken Tusk, Orgrimmar | Some months after the fall of the Lich King";
    char const* const CAPTION_FRONT = "The Broken Front, Icecrown | The last day of his war";
    char const* const CAPTION_WRATHGATE = "Angrathar, the Wrathgate";
    char const* const CAPTION_WINTERGARDE = "Wintergarde Keep, the Dragonblight";
    char const* const CAPTION_FIELDS = "The Valley of Fallen Heroes, Icecrown";
    char const* const CAPTION_BAZAAR = "The Infinite Bazaar, Malykriss | Years earlier";
    char const* const CAPTION_BAZAAR_HOME = "The Infinite Bazaar | Malykriss: The Vile Hold";   // (any later journey to it)

    // A place an act happens at: where the Timerunner stands, facing what they should see.
    struct Place
    {
        uint32 map;
        float x, y, z, o;
    };

    // The Broken Front, facing the Citadel.
    constexpr float FRONT_X = 6650.0f, FRONT_Y = 1145.0f, FRONT_Z = 274.0f, FRONT_O = 2.30f;
    constexpr float FRONT_REACH = 150.0f;
    // The taverns: the innkeeper where she stands, facing her customers.
    Place const GILDED_ROSE{ 0, -8867.8f, 673.7f, 98.0f, 5.20f };
    Place const BROKEN_TUSK{ 1, 1634.0f, -4439.4f, 15.8f, 2.76f };
    // The table for four they sit at: in the Gilded Rose its own, by the hearth, with the game's
    // four chairs around it (the Timerunner's first, facing the room); the Broken Tusk has no table
    // in the open, so one is set out before the innkeeper (TableAt), the Timerunner's chair with
    // its back to her, where they stood before.
    Place const GILDED_ROSE_CHAIRS[4] = {
        { 0, -8866.53f, 682.95f, 97.94f, 5.315f }, { 0, -8867.01f, 680.74f, 97.94f, 0.602f },
        { 0, -8864.89f, 680.33f, 97.94f, 2.173f }, { 0, -8864.29f, 682.38f, 97.94f, 3.744f } };
    Position const GILDED_ROSE_STOP(-8866.2f, 679.5f, 97.94f);          // Moratari, at its edge
    constexpr float TABLE_FROM_INN = 5.5f, CHAIR_FROM_TABLE = 1.5f;     // the Broken Tusk's
    constexpr uint32 GO_ALLIANCE_CHAIR = 24469;  // Wooden Chair, the Gilded Rose's own
    constexpr uint32 GO_HORDE_CHAIR = 191242;    // a log chair
    constexpr uint32 GO_HORDE_TABLE = 180888;    // OrcTable01
    constexpr uint32 ZONE_STORMWIND_CITY = 1519, ZONE_ORGRIMMAR = 1637;
    // The three moments: Angrathar's battlefield before the gate, the Forsaken's cliffs on the
    // right; Wintergarde's lower village, its town square, facing Naxxramas; and the Valley of
    // Fallen Heroes, facing the Citadel.
    Place const WRATHGATE{ 571, 4880.0f, 1470.0f, 212.0f, 0.46f };
    Place const WINTERGARDE{ 571, 3825.0f, -1060.0f, 120.0f, 4.05f };
    Place const FIELDS{ 571, 7739.0f, 2355.0f, 375.5f, 3.27f };

    enum IntroPeople : uint32
    {
        GHOUL = 770120, SPIKED_GHOUL, ABOMINATION, CRYPT_FIEND, DEATHBRINGER, FROST_WYRM, VALKYR, LICH_KING,
        TIRION, CRUSADER, CRUSADER_2, MARINE, REAVER, LIGHT, PLAGUE, ETERNUS_VOICE, LICH_KING_VOICE,
        BRANNOC, SYLENNA, TOBIAS, GRAKKA, TAHONO, VEYLAN, INNKEEPER_A, INNKEEPER_H,
        FALLEN_A, FALLEN_H, VILLAGER, RISEN_VILLAGER, VILLAGER_F,
        INTRO_FIRST = GHOUL, INTRO_LAST = VILLAGER_F,
    };

    enum IntroSpells : uint32
    {
        SPELL_AVENGING_WRATH   = 31884,  // the Light's wings, on the Timerunner
        SPELL_TELEPORT_VISUAL  = 51347,
        SPELL_TIME_RIFT        = 31387,
        SPELL_TIME_STOP        = 60074,  // the Culling of Stratholme's, its bubble
        SPELL_TIME_STOP_VISUAL = 25171,
        SPELL_GHOUL_RISE       = 47448,  // Risen Ghoul Spawn-In: out of the ground
        SPELL_EMERGE           = 50142,
        SPELL_FROST_BOMB_MARK  = 70022,  // Sindragosa's, on the ground where it will land
        SPELL_EXPLOSION        = 60081,
        SPELL_HUGE_EXPLOSION   = 46225,
        SPELL_GREEN_EXPLOSION  = 43401,
        SPELL_DEATH_AND_DECAY  = 43265,
        SPELL_PILLAR_OF_FIRE   = 43541,
        SPELL_CAMERA_SHAKE     = 47533,
        SPELL_CAMERA_SHAKE_MED = 44762,
        SPELL_SHADOW_BOLT      = 9613,
        SPELL_DIVINE_STORM     = 53385,
        SPELL_CONSECRATION     = 48818,
        SPELL_HOLY_SHOCK       = 25914,
        SPELL_REMORSELESS_WINTER = 68981,
        SPELL_FURY_OF_FROSTMOURNE = 72350,
    };

    enum IntroSounds : uint32
    {
        MUSIC_TAVERN_ALLIANCE = 4516,  // Zone-TavernAlliance
        MUSIC_TAVERN_HORDE   = 5234,   // Zone-TavernHorde
        MUSIC_BATTLE         = 6077,   // Moment - Battle01
        MUSIC_LICH_KING      = 12765,  // the Lich King's theme
        MUSIC_LAMENT         = 10896,  // Lament of the Highborne
        SOUND_TAVERN_CROWD   = 7359,
        SOUND_CHEER_ALLIANCE = 8571,
        SOUND_CHEER_HORDE    = 8573,
        SOUND_FROST_IMPACT   = 17454,
        SOUND_SHADOW_IMPACT  = 17447,
        SOUND_FROST_WYRM     = 14822,
        SOUND_RAISE_DEAD     = 17446,
    };

    // The game's own lines, with their sound (Icecrown Citadel's, and Ebon Hold's).
    struct Voice
    {
        char const* text;
        uint32 sound;
    };
    Voice const TIRION_MUST_FALL{ "The Lich King must fall!!", 17389 };
    Voice const TIRION_NO_MORE{ "No more, Arthas! No more lives will be consumed by your hatred!", 17393 };
    Voice const TIRION_ARTHAS{ "ARTHAS! I swore that I would see you dead and the Scourge dismantled! I'm going to finish what I started at Light's Hope!", 16656 };
    Voice const LK_ARISE{ "Arise minions. Do not let them pass.", 17216 };
    Voice const LK_RAVAGE{ "Ravage the living, minions!", 14788 };
    Voice const LK_VALKYR{ "Val'kyr, your master calls!", 17373 };
    Voice const LK_HOPE{ "Hope wanes...", 17363 };
    Voice const LK_HUNGERS{ "Frostmourne hungers...", 17366 };

    struct Opening
    {
        ObjectGuid player;
        std::vector<ObjectGuid> people;   // everyone summoned for the act under way, the unseen ones too
        std::vector<ObjectGuid> scourge;  // the battle's dead who fight
        std::vector<ObjectGuid> fallen;   // the bodies on a field, to be raised
        std::vector<ObjectGuid> friends;  // the tavern's three
        std::vector<ObjectGuid> props;    // the tavern's table and chairs, set out in the opening's phase
        ObjectGuid tirion, lichKing, voice, moratari, innkeeper;
        Place place{};                    // where the act under way has the Timerunner
        char const* caption = "";         // the curtain's words for the act under way
        uint32 act = 0;                   // each act's steps belong to it alone
        bool frozen = false, over = false;
    };
    using Act = std::function<void(Player*, std::shared_ptr<Opening>)>;
    using Step = std::function<void(Player*, Opening&)>;

    std::mutex openingsLock;
    std::unordered_map<ObjectGuid, std::shared_ptr<Opening>> openings;
    std::atomic<uint32> running{ 0 };

    std::shared_ptr<Opening> OpeningOf(Player const* player)
    {
        if (!running.load())
            return nullptr;
        std::lock_guard<std::mutex> lock(openingsLock);
        auto it = openings.find(player->GetGUID());
        return it == openings.end() ? nullptr : it->second;
    }

    bool Enabled()
    {
        return sConfigMgr->GetOption<bool>("WrathRemix.Intro", true, false);
    }

    uint32 SettleMs()
    {
        return 1000 * sConfigMgr->GetOption<uint32>("WrathRemix.Intro.SettleSeconds", 25, false);
    }

    // ---- The curtain ----------------------------------------------------------------------------

    // Each player's curtains: how many were drawn and how many times their game said its frames run
    // smoothly since the last one (`.remix intro status` tells, for the test and for a phone that
    // seems to wait the whole SettleSeconds).
    struct Curtains
    {
        uint32 drawn = 0;
        uint32 settles = 0;
        bool settled = false;                   // since the last curtain
        std::chrono::steady_clock::time_point drawnAt;
        std::chrono::steady_clock::time_point settledAt;
    };
    std::mutex settledLock;
    std::unordered_map<ObjectGuid, Curtains> curtains;

    bool HasSettled(ObjectGuid guid)
    {
        std::lock_guard<std::mutex> lock(settledLock);
        auto it = curtains.find(guid);
        return it != curtains.end() && it->second.settled;
    }

    // Dark at once, [caption] on it; the add-on starts watching its frames afresh.
    void Curtain(Player* player, char const* caption)
    {
        {
            std::lock_guard<std::mutex> lock(settledLock);
            Curtains& c = curtains[player->GetGUID()];
            ++c.drawn;
            c.settled = false;
            c.drawnAt = std::chrono::steady_clock::now();
        }
        TellAddon(player, Acore::StringFormat("curtain {} {}", CURTAIN_MS, caption));
    }

    void Lift(Player* player, uint32 liftMs = LIFT_MS)
    {
        TellAddon(player, Acore::StringFormat("lift {}", liftMs));
    }

    // Once the game has settled behind the curtain (never sooner than [leastMs], never later than
    // SettleSeconds), the curtain lifts over [liftMs] and [then] runs.
    void WhenSettled(ObjectGuid guid, uint32 waited, uint32 leastMs, uint32 liftMs, std::function<void(Player*)> then)
    {
        Player* player = ObjectAccessor::FindConnectedPlayer(guid);
        if (!player)
            return;
        player->m_Events.AddEventAtOffset([guid, waited, leastMs, liftMs, then]()
        {
            Player* p = ObjectAccessor::FindConnectedPlayer(guid);
            if (!p || !p->IsInWorld())
                return;
            uint32 now = waited + SETTLE_POLL_MS;
            if ((now >= leastMs && HasSettled(guid)) || now >= SettleMs())
            {
                Lift(p, liftMs);
                then(p);
            }
            else
                WhenSettled(guid, now, leastMs, liftMs, then);
        }, Milliseconds(SETTLE_POLL_MS));
    }

    // A journey anywhere in the story (JourneyFromTheDark): there (a check every half second, for
    // [tries]), the curtain again and the game watched until it has settled, then the lift. One who
    // never gets there has the curtain lifted all the same.
    void WhenArrived(ObjectGuid guid, uint32 map, float x, float y, uint32 tries, std::string caption, uint32 leastMs, uint32 liftMs)
    {
        Player* player = ObjectAccessor::FindConnectedPlayer(guid);
        if (!player)
            return;
        player->m_Events.AddEventAtOffset([guid, map, x, y, tries, caption, leastMs, liftMs]()
        {
            Player* p = ObjectAccessor::FindConnectedPlayer(guid);
            if (!p)
                return;
            if (p->IsInWorld() && !p->IsBeingTeleported() && p->GetMapId() == map && p->GetExactDist2d(x, y) < 60.0f)
            {
                Curtain(p, caption.c_str());
                WhenSettled(guid, 0, leastMs, liftMs, [](Player*) { });
            }
            else if (tries > 1)
                WhenArrived(guid, map, x, y, tries - 1, caption, leastMs, liftMs);
            else if (p->IsInWorld())
                Lift(p, liftMs);
        }, 500ms);
    }

    bool AtTheFront(Player const* player)
    {
        return player->GetMapId() == MAP_NORTHREND && std::hypot(player->GetPositionX() - FRONT_X, player->GetPositionY() - FRONT_Y) < FRONT_REACH;
    }

    // In one of the taverns (a Timerunner who left during its scene comes back there).
    bool AtATavern(Player const* player)
    {
        for (Place const* inn : { &GILDED_ROSE, &BROKEN_TUSK })
            if (player->GetMapId() == inn->map && std::hypot(player->GetPositionX() - inn->x, player->GetPositionY() - inn->y) < 40.0f)
                return true;
        return false;
    }

    bool Alliance(Player const* player)
    {
        return player->GetTeamId() == TEAM_ALLIANCE;
    }

    // The friend who didn't come home from Icecrown.
    char const* Fallen(Player const* player)
    {
        return Alliance(player) ? "Haldren" : "Kaga";
    }

    // A line with the Timerunner's name ($N) and their fallen friend's ($F) in it.
    std::string Words(Player const* player, std::string text)
    {
        for (auto [mark, with] : { std::pair<char const*, std::string>{ "$N", player->GetName() }, { "$F", Fallen(player) } })
            for (size_t at = text.find(mark); at != std::string::npos; at = text.find(mark, at + with.size()))
                text.replace(at, 2, with);
        return text;
    }

    float Facing(float fromX, float fromY, float toX, float toY)
    {
        return Position::NormalizeOrientation(std::atan2(toY - fromY, toX - fromX));
    }

    // A place [forward] yards ahead of [at] and [left] to its left, on the ground (from [above]
    // yards over the place's height, so indoors it's the floor and not the roof), turned [facing]
    // from the place's own facing. Outdoors, up a slope higher than that, nothing is found beneath:
    // the land's own height there (never a roof), not the place's, which would be inside the hill.
    // (Indoors, from 2 yards over the floor, land higher than that is never the room's floor: the
    // floor's own height, as before.)
    Position Around(Player* player, Place const& at, float forward, float left, float facing = 0.0f, float above = 10.0f)
    {
        float x = at.x + forward * std::cos(at.o) - left * std::sin(at.o);
        float y = at.y + forward * std::sin(at.o) + left * std::cos(at.o);
        float z = player->GetMap()->GetHeight(player->GetPhaseMask(), x, y, at.z + above, true, above + 30.0f);
        if (z < at.z - 25.0f)
        {
            float land = above > 2.0f ? player->GetMap()->GetGridHeight(x, y) : at.z;
            z = land > at.z + above && land < at.z + 40.0f ? land : at.z;
        }
        else if (z > at.z + above)
            z = at.z;
        return Position(x, y, z + 0.1f, Position::NormalizeOrientation(at.o + facing));
    }

    // Indoors: a place from the innkeeper's, brought nearer if a wall stands between.
    Position Indoors(Player* player, Place const& inn, float forward, float left)
    {
        for (float share : { 1.0f, 0.7f, 0.45f })
        {
            Position at = Around(player, inn, forward * share, left * share, 0.0f, 2.0f);
            if (player->GetMap()->isInLineOfSight(inn.x, inn.y, inn.z + 1.5f, at.GetPositionX(), at.GetPositionY(), at.GetPositionZ() + 1.5f,
                    player->GetPhaseMask(), LINEOFSIGHT_ALL_CHECKS, VMAP::ModelIgnoreFlags::Nothing))
                return at;
        }
        return Position(inn.x, inn.y, inn.z, inn.o);
    }

    // A place on the Front: yards forward (towards the Citadel) and to the left of its middle.
    Position Spot(Player* player, float forward, float left, float facing = 0.0f)
    {
        return Around(player, Place{ MAP_NORTHREND, FRONT_X, FRONT_Y, FRONT_Z, FRONT_O }, forward, left, facing, 8.0f);
    }

    Creature* Who(Player* player, ObjectGuid guid)
    {
        return guid ? ObjectAccessor::GetCreature(*player, guid) : nullptr;
    }

    // The battle's fighters: the Scourge's foot and the line beside the Timerunner.
    bool Fights(uint32 entry)
    {
        return (entry >= GHOUL && entry <= DEATHBRINGER) || (entry >= TIRION && entry <= REAVER);
    }

    // Someone for this Timerunner's opening. Only the battle's own fight ([fights]); everyone
    // else stands where they're put, out of reach.
    Creature* Bring(Player* player, Opening& b, uint32 entry, Position const& at, uint32 health = 0, bool fights = false)
    {
        TempSummon* c = player->SummonCreature(entry, at, TEMPSUMMON_TIMED_DESPAWN, 300000, 0, nullptr, true);
        if (!c)
            return nullptr;
        bool ours = entry >= INTRO_FIRST && entry <= INTRO_LAST;
        bool scourge = ours && (entry <= LICH_KING || entry == PLAGUE || entry == RISEN_VILLAGER);
        c->SetLevel(entry == LICH_KING || entry == TIRION ? 13 : (scourge ? 10 : 12));
        if (health)
        {
            c->SetMaxHealth(health);
            c->SetHealth(health);
        }
        fights = fights && Fights(entry);
        c->SetReactState(fights ? REACT_AGGRESSIVE : REACT_PASSIVE);
        if (!fights && scourge)
            c->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
        if (!ours)
            c->ReplaceAllNpcFlags(UNIT_NPC_FLAG_NONE);
        b.people.push_back(c->GetGUID());
        if (fights && entry <= DEATHBRINGER)
            b.scourge.push_back(c->GetGUID());
        return c;
    }

    // An unseen one, for an effect at a place: the Light's (hurting only the Scourge) or the
    // Scourge's.
    Creature* Effect(Player* player, Opening& b, bool scourge, Position const& at, uint32 lasts = 12000)
    {
        TempSummon* c = player->SummonCreature(scourge ? PLAGUE : LIGHT, at, TEMPSUMMON_TIMED_DESPAWN, lasts, 0, nullptr, true);
        if (c)
            b.people.push_back(c->GetGUID());
        return c;
    }

    void Say(Player* player, Creature* who, Voice const& voice, bool yell = true)
    {
        if (!who)
            return;
        if (yell)
            who->Yell(voice.text, LANG_UNIVERSAL, player);
        else
            who->Say(voice.text, LANG_UNIVERSAL, player);
        if (voice.sound)
            who->PlayDirectSound(voice.sound, player);
    }

    // Someone speaking, and perhaps moving as they say it.
    void Speak(Player* player, Creature* who, char const* text, uint32 emote = EMOTE_ONESHOT_TALK)
    {
        if (!who)
            return;
        who->Say(Words(player, text), LANG_UNIVERSAL, player);
        if (emote)
            who->HandleEmoteCommand(emote);
    }

    void Shake(Player* player, bool hard)
    {
        player->CastSpell(player, hard ? SPELL_CAMERA_SHAKE_MED : SPELL_CAMERA_SHAKE, true);
    }

    uint32 ScourgeStanding(Player* player, Opening& b)
    {
        uint32 n = 0;
        for (ObjectGuid guid : b.scourge)
            if (Creature* c = Who(player, guid); c && c->IsAlive())
                ++n;
        return n;
    }

    // Somewhere out on the Front, ahead, well away from the Timerunner.
    Position Somewhere(Player* player, float nearest = 18.0f, float farthest = 44.0f)
    {
        for (int tries = 0; tries < 8; ++tries)
        {
            Position at = Spot(player, frand(nearest, farthest), frand(-28.0f, 28.0f));
            if (player->GetExactDist2d(at.GetPositionX(), at.GetPositionY()) > 12.0f)
                return at;
        }
        return Spot(player, farthest, 0.0f);
    }

    void RaiseGhoul(Player* player, Opening& b, Position const& at, bool fights)
    {
        uint32 entry = urand(0, 3) ? GHOUL : SPIKED_GHOUL;
        if (Creature* ghoul = Bring(player, b, entry, at, entry == GHOUL ? 700 : 900, fights))
            ghoul->CastSpell(ghoul, SPELL_GHOUL_RISE, true);
    }

    // A body on a field: one of the fallen, lying where they fell.
    Creature* Body(Player* player, Opening& b, uint32 entry, Position const& at)
    {
        Position lying = at;
        lying.SetOrientation(frand(0.0f, 2.0f * float(M_PI)));
        Creature* c = Bring(player, b, entry, lying);
        if (c)
        {
            c->SetStandState(UNIT_STAND_STATE_DEAD);
            b.fallen.push_back(c->GetGUID());
        }
        return c;
    }

    // One of the field's blows, somewhere: a frost bomb, plague bursting, a pillar of fire, a blast.
    void Blow(Player* player, Opening& b)
    {
        Position at = Somewhere(player, 14.0f, 46.0f);
        bool near = player->GetExactDist2d(at.GetPositionX(), at.GetPositionY()) < 22.0f;
        switch (urand(0, 4))
        {
            case 0:
            case 1:  // a frost bomb: its mark on the ice, then the blast
                if (Creature* mark = Effect(player, b, true, at, 8000))
                {
                    mark->AddAura(SPELL_FROST_BOMB_MARK, mark);
                    ObjectGuid guid = player->GetGUID(), markGuid = mark->GetGUID();
                    uint32 act = b.act;
                    player->m_Events.AddEventAtOffset([guid, markGuid, near, act]()
                    {
                        Player* p = ObjectAccessor::FindPlayer(guid);
                        std::shared_ptr<Opening> o = p ? OpeningOf(p) : nullptr;
                        if (!o || o->frozen || o->act != act)
                            return;
                        if (Creature* m = ObjectAccessor::GetCreature(*p, markGuid))
                        {
                            m->RemoveAurasDueToSpell(SPELL_FROST_BOMB_MARK);
                            m->CastSpell(m, SPELL_EXPLOSION, true);
                            m->PlayDirectSound(SOUND_FROST_IMPACT, p);
                        }
                        if (near)
                            Shake(p, false);
                    }, 2500ms);
                }
                break;
            case 2:  // plague, bursting up through the snow
                if (Creature* plague = Effect(player, b, true, at))
                {
                    plague->CastSpell(plague, SPELL_GREEN_EXPLOSION, true);
                    plague->CastSpell(plague, SPELL_DEATH_AND_DECAY, true);
                }
                break;
            case 3:  // the Light's answer: a pillar of fire among the dead
                if (Creature* light = Effect(player, b, false, at, 6000))
                    light->CastSpell(light, SPELL_PILLAR_OF_FIRE, true);
                break;
            default:  // a blast
                if (Creature* blast = Effect(player, b, true, at, 6000))
                {
                    blast->CastSpell(blast, near ? SPELL_EXPLOSION : SPELL_HUGE_EXPLOSION, true);
                    blast->PlayDirectSound(SOUND_SHADOW_IMPACT, player);
                }
                if (near)
                    Shake(player, false);
                break;
        }
    }

    // A step of the act under way, [ms] after now; nothing if the act is over by then.
    void At(Player* player, std::shared_ptr<Opening> o, uint32 ms, Step step)
    {
        ObjectGuid guid = player->GetGUID();
        uint32 act = o->act;
        player->m_Events.AddEventAtOffset([guid, o, act, step]()
        {
            Player* p = ObjectAccessor::FindPlayer(guid);
            if (!p || !p->IsInWorld() || o->over || o->act != act)
                return;
            step(p, *o);
        }, Milliseconds(ms));
    }

    void Despawn(Player* player, Opening& b)
    {
        for (ObjectGuid guid : b.people)
            if (Creature* c = Who(player, guid))
                c->DespawnOrUnsummon();
        for (ObjectGuid guid : b.props)
            if (GameObject* go = ObjectAccessor::GetGameObject(*player, guid))
                go->DespawnOrUnsummon();
        b.props.clear();
        b.people.clear();
        b.scourge.clear();
        b.fallen.clear();
        b.friends.clear();
        b.tirion = b.lichKing = b.voice = b.moratari = b.innkeeper = ObjectGuid::Empty;
    }

    // At the table: in their chair, and kept there (the game's control of them taken from it)
    // until Moratari takes them from the tavern; standing for a toast, and sitting again.
    void SitDown(Player* player)
    {
        player->SetStandState(UNIT_STAND_STATE_SIT_MEDIUM_CHAIR);
        player->SetClientControl(player, false, true);
    }

    void StandUp(Player* player)
    {
        player->SetStandState(UNIT_STAND_STATE_STAND);
    }

    void GetUp(Player* player)
    {
        player->SetStandState(UNIT_STAND_STATE_STAND);
        player->SetClientControl(player, true);
    }

    void EndOpening(Player* player)
    {
        std::lock_guard<std::mutex> lock(openingsLock);
        if (openings.erase(player->GetGUID()))
            --running;
    }

    // Taken far across the same map, the game shows no loading screen while the ground there
    // loads, and on a slow phone the Timerunner falls through it: the core kills whoever falls under
    // the world, whatever spares them otherwise (a level 10 ghost left in Icecrown). Held off the
    // ground (no gravity) until it's there; the last hold given is the one that ends.
    struct GroundHold : public DataMap::Base
    {
        uint32 given = 0;
    };

    constexpr Milliseconds GROUND_LOADS_IN = 8s;

    void HoldOverTheGround(Player* player)
    {
        uint32 hold = ++player->CustomData.GetDefault<GroundHold>("remix_ground_hold")->given;
        player->SetDisableGravity(true);
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid, hold]()
        {
            if (Player* p = ObjectAccessor::FindConnectedPlayer(guid); p && p->CustomData.GetDefault<GroundHold>("remix_ground_hold")->given == hold)
                p->SetDisableGravity(false);
        }, GROUND_LOADS_IN);
    }

    // Alive again where they are (a death in the opening, any the core deals around its rules).
    void Revive(Player* player)
    {
        player->ResurrectPlayer(1.0f);
        player->SpawnCorpseBones();
        // (only a release to a graveyard clears this, after a fall under the world)
        player->RemovePlayerFlag(PLAYER_FLAGS_IS_OUT_OF_BOUNDS);
    }

    // Back from a death, to [at].
    void BackFromDeath(Player* player, Place const& at)
    {
        Revive(player);
        HoldOverTheGround(player);
        if (player->GetMapId() == at.map)
            player->NearTeleportTo(at.x, at.y, at.z + 0.5f, at.o);
        else
            player->TeleportTo(at.map, at.x, at.y, at.z + 0.5f, at.o);
    }

    // Nothing in the opening hurts the Timerunner, but the core kills whoever falls under the world,
    // and a few things kill outright: a death in it is undone at once, where the act has them.
    void UndoDeath(Player* player)
    {
        std::shared_ptr<Opening> opening = OpeningOf(player);
        if (!opening || opening->over)
            return;
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid, opening]()
        {
            Player* p = ObjectAccessor::FindConnectedPlayer(guid);
            if (p && p->IsInWorld() && !p->IsAlive() && !opening->over)
                BackFromDeath(p, opening->place);
        }, 500ms);
    }

    void WhenAtTheBazaar(ObjectGuid guid, uint32 tries);

    // The end of it: out of the phase, to the Bazaar, the opening seen.
    void Finish(Player* player, Opening& b)
    {
        if (b.over)
            return;
        b.over = true;
        ++b.act;
        Despawn(player, b);
        GetUp(player);
        player->RemoveAurasDueToSpell(SPELL_AVENGING_WRATH);
        player->RemoveAurasDueToSpell(SPELL_TIME_STOP_VISUAL);
        player->CombatStop(true);
        player->SetPhaseMask(PHASEMASK_NORMAL, true);
        SetIntroSeen(player);
        // (still in the opening as it goes: the hourglass doesn't count where it was as somewhere they came from)
        player->CastSpell(player, SPELL_TELEPORT_VISUAL, true);
        Curtain(player, CAPTION_BAZAAR);
        if (player->GetMapId() == MAP_NORTHREND)
            HoldOverTheGround(player);
        player->TeleportTo(MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O);
        EndOpening(player);
        WhenAtTheBazaar(player->GetGUID(), 60);
    }

    // Arrived at the Bazaar at the opening's end: the curtain lifts once the game has settled, and
    // Moratari welcomes them. A check a second; a curtain the add-on holds lifts by itself if they
    // never get there.
    void WhenAtTheBazaar(ObjectGuid guid, uint32 tries)
    {
        Player* player = ObjectAccessor::FindConnectedPlayer(guid);
        if (!player)
            return;
        player->m_Events.AddEventAtOffset([guid, tries]()
        {
            Player* p = ObjectAccessor::FindConnectedPlayer(guid);
            if (!p)
                return;
            if (!(p->IsInWorld() && !p->IsBeingTeleported() && AtTheBazaar(p)))
            {
                if (tries > 1)
                    WhenAtTheBazaar(guid, tries - 1);
                return;
            }
            Curtain(p, CAPTION_BAZAAR);
            WhenSettled(guid, 0, SETTLE_LEAST_MS, LIFT_MS, [](Player* p)
            {
                // The hourglass has nowhere to take them back to. (Once they're there: a teleport
                // asked for in a step goes once the player's update is over, and the hourglass's
                // hook, seeing the opening over by then, would take the last place of it for where
                // they came from.)
                SetWayBack(p, -1, 0.0f, 0.0f, 0.0f, 0.0f);
                ObjectGuid guid = p->GetGUID();
                p->m_Events.AddEventAtOffset([guid]()
                {
                    Player* p = ObjectAccessor::FindPlayer(guid);
                    if (!p || !p->IsInWorld())
                        return;
                    if (Creature* moratari = p->FindNearestCreature(NPC_MORATARI, 40.0f))
                    {
                        moratari->SetFacingToObject(p);
                        moratari->Say(Words(p, "Welcome to the Infinite Bazaar, $N. Breathe. Eternus will want to see you."), LANG_UNIVERSAL, p);
                        moratari->HandleEmoteCommand(EMOTE_ONESHOT_POINT);
                    }
                }, Milliseconds(LIFT_MS));
            });
        }, 1s);
    }

    // Arrived where the act is (a far journey keeps them on a loading screen a while): the act
    // begins. A check a second; if they never get there, the opening ends at the Bazaar.
    void WhenThere(ObjectGuid guid, std::shared_ptr<Opening> o, uint32 act, uint32 tries, Act then)
    {
        Player* player = ObjectAccessor::FindConnectedPlayer(guid);
        if (!player)
            return;
        player->m_Events.AddEventAtOffset([guid, o, act, tries, then]()
        {
            Player* p = ObjectAccessor::FindConnectedPlayer(guid);
            if (!p || o->over || o->act != act)
                return;
            Place const& at = o->place;
            if (p->IsInWorld() && !p->IsBeingTeleported() && p->GetMapId() == at.map && p->GetExactDist2d(at.x, at.y) < 40.0f)
            {
                p->SetPhaseMask(PHASE_INTRO, true);
                // (there: the curtain again, so the game's frames are watched from here on, and the
                // act once they run smoothly)
                Curtain(p, o->caption);
                WhenSettled(guid, 0, SETTLE_LEAST_MS, LIFT_MS, [o, act, then](Player* p)
                {
                    if (!o->over && o->act == act)
                        then(p, o);
                });
            }
            else if (tries > 1)
                WhenThere(guid, o, act, tries - 1, then);
            else if (p->IsInWorld())
                Finish(p, *o);
        }, 1s);
    }

    // On to the next act: everyone of this one gone, the curtain down (its [caption] on it), the
    // Timerunner taken there.
    void GoTo(Player* player, std::shared_ptr<Opening> o, Place const& place, Act then, char const* caption)
    {
        Opening& b = *o;
        Despawn(player, b);
        ++b.act;
        b.frozen = false;
        b.place = place;
        b.caption = caption;
        Curtain(player, caption);
        player->CombatStop(true);
        player->RemoveAurasDueToSpell(SPELL_AVENGING_WRATH);
        player->RemoveAurasDueToSpell(SPELL_TIME_STOP_VISUAL);
        GetUp(player);
        player->SetPhaseMask(PHASE_INTRO, true);
        // (already there, as a new Timerunner is made in their tavern: no journey at all)
        if (player->GetMapId() == place.map && player->GetExactDist2d(place.x, place.y) < 2.0f)
        {
            player->SetFacingTo(place.o);
            WhenThere(player->GetGUID(), o, b.act, 60, std::move(then));
            return;
        }
        player->CastSpell(player, SPELL_TELEPORT_VISUAL, true);
        // (far across the same map: held over the ground until it's loaded; a step indoors isn't)
        bool far = player->GetMapId() != place.map || player->GetExactDist2d(place.x, place.y) > 100.0f;
        if (far && player->GetMapId() == place.map)
            HoldOverTheGround(player);
        if (!player->TeleportTo(place.map, place.x, place.y, place.z + (far ? 0.5f : 0.0f), place.o))
        {
            Finish(player, b);
            return;
        }
        WhenThere(player->GetGUID(), o, b.act, 60, std::move(then));
    }

    // Time stops: everyone of the act where they stand.
    void Freeze(Player* player, Opening& b, bool bubble = true)
    {
        b.frozen = true;
        for (ObjectGuid guid : b.people)
            if (Creature* c = Who(player, guid); c && c->IsAlive() && guid != b.moratari)
            {
                c->AttackStop();
                c->StopMoving();
                c->GetMotionMaster()->Clear();
                c->SetReactState(REACT_PASSIVE);
                c->SetControlled(true, UNIT_STATE_STUNNED);
                c->AddAura(SPELL_TIME_STOP_VISUAL, c);
            }
        player->CombatStop(true);
        player->RemoveAurasDueToSpell(SPELL_AVENGING_WRATH);
        if (bubble)
            if (Creature* stop = Effect(player, b, false, player->GetPosition(), 20000))
                stop->CastSpell(stop, SPELL_TIME_STOP, true);
        Shake(player, true);
    }

    // Moratari, beside the Timerunner in an act (out of its time: nothing there sees her).
    Creature* BringMoratari(Player* player, Opening& b, Position const& at)
    {
        Creature* moratari = Bring(player, b, NPC_MORATARI_SCENE, at);
        if (moratari)
        {
            b.moratari = moratari->GetGUID();
            moratari->SetFaction(35);
            moratari->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
            moratari->CastSpell(moratari, SPELL_TELEPORT_VISUAL, true);
            moratari->SetFacingToObject(player);
        }
        return moratari;
    }

    void SheSays(Player* player, Opening& b, char const* text, uint32 emote = EMOTE_ONESHOT_TALK)
    {
        Creature* moratari = Who(player, b.moratari);
        if (moratari)
            moratari->SetFacingToObject(player);
        Speak(player, moratari, text, emote);
    }

    void Begin(Player* player);
    void Front(Player* player, std::shared_ptr<Opening> o);
    void Wrathgate(Player* player, std::shared_ptr<Opening> o);
    void Wintergarde(Player* player, std::shared_ptr<Opening> o);
    void Fields(Player* player, std::shared_ptr<Opening> o);

    // ---- The tavern ---------------------------------------------------------------------------

    struct TavernLine
    {
        uint32 at;
        int who;            // 0 to 2 the friends, 3 the innkeeper
        char const* text;
        uint32 emote;
    };

    // Each side's own war: the Alliance's landing at Valiance Keep, Wintergarde, Bolvar at the Gate,
    // Varian at the Undercity, the Skybreaker over Icecrown; the Horde's Warsong Hold under siege,
    // Garrosh's temper, Saurfang's son at the Gate, Thrall at the Undercity, Orgrim's Hammer.
    TavernLine const ALLIANCE_TAVERN[] = {
        { 2000, 3, "Another round for the heroes of Icecrown! And put your coin away, all of you. You've paid enough up north.", EMOTE_ONESHOT_EXCLAMATION },
        { 7000, 0, "Raise 'em up! To King Varian, and to the Frozen Throne, empty at last! For the Alliance!", EMOTE_ONESHOT_CHEER },
        { 14500, 1, "I still think about our first day at Valiance Keep. The dead were coming up the beach before the last ship was even unloaded.", EMOTE_ONESHOT_TALK },
        { 21500, 2, "For me it's Wintergarde. We flew gryphons over the lower village all day, pulling out anyone still breathing. There weren't many.", EMOTE_ONESHOT_NO },
        { 28000, 0, "And the Gate. I was near enough to see Bolvar go down when that green fog came off the cliffs. Then Varian kicked in the doors of the Undercity. Never seen a king so angry.", EMOTE_ONESHOT_TALK },
        { 36000, 1, "Enough of that. Think of the Skybreaker instead: $N strapping on that goblin's rocket pack and leaping across to the Horde ship, laughing like a fool.", EMOTE_ONESHOT_LAUGH },
        { 42500, 2, "$F jumped right after you. To $F. He walked into Icecrown with us, and he never walked out.", EMOTE_ONESHOT_SALUTE },
        { 49500, 0, "Well. Arthas is dead, and the ale's free. Whatever comes next can't be worse than him.", EMOTE_ONESHOT_TALK },
        { 56500, 1, "Don't tempt fate, Brannoc. You said that at Ulduar, too, and then we found what was chained beneath it.", EMOTE_ONESHOT_NO },
        { 63000, 2, "$N, you've gone quiet. You were there at the very end. What was it like, when he fell?", EMOTE_ONESHOT_QUESTION },
    };
    TavernLine const HORDE_TAVERN[] = {
        { 2000, 3, "Heroes of Icecrown! Lay your axes by the fire, and drink. This round is on the house.", EMOTE_ONESHOT_EXCLAMATION },
        { 7000, 0, "To the Warchief! And to the Frozen Throne, empty at last! Lok'tar ogar!", EMOTE_ONESHOT_CHEER },
        { 14500, 1, "I remember the first day at Warsong Hold. The nerubians came up through the floor while Garrosh was still on the walls, roaring at the zeppelins to land faster.", EMOTE_ONESHOT_TALK },
        { 21500, 0, "Hah! Hellscream wanted to march on Icecrown that same afternoon. If the High Overlord had not held him back, he would have done it, too.", EMOTE_ONESHOT_LAUGH },
        { 28000, 2, "And the Gate. Saurfang the Younger charging the Lich King alone, then that green fog off the cliffs. Forsaken plague. Ours. Thrall and Vol'jin made Varimathras pay for it.", EMOTE_ONESHOT_TALK },
        { 36000, 1, "Let us speak of happier things. Orgrim's Hammer over Icecrown, the deck pitching under us, and $N at the rail, laughing at the wind.", EMOTE_ONESHOT_LAUGH },
        { 42500, 1, "$F was beside you, laughing just as hard. To $F. The Earth Mother has her now.", EMOTE_ONESHOT_SALUTE },
        { 49500, 0, "Arthas is dead, and the grog is free. Whatever comes next cannot be worse than him.", EMOTE_ONESHOT_TALK },
        { 56500, 2, "Bite your tongue, Grakka. You said that at Ulduar, the night before we went down to Yogg-Saron.", EMOTE_ONESHOT_NO },
        { 63000, 1, "$N, you have gone quiet. You were there at the very end. What was it like, when he fell?", EMOTE_ONESHOT_QUESTION },
    };

    // Where they sit: the four chairs (the Timerunner's first) and where Moratari stops at the
    // table's edge; the Broken Tusk's table, set out [TABLE_FROM_INN] yards before the innkeeper.
    // With [player] there, on the floor as it is; before they are (null), at the innkeeper's height.
    struct Seats
    {
        Place chairs[4];
        Position stop, table;
    };

    float Floor(Player* player, float x, float y, float z)
    {
        if (!player)
            return z;
        float floor = player->GetMap()->GetHeight(player->GetPhaseMask(), x, y, z + 2.0f, true, 10.0f);
        return floor > z - 3.0f && floor < z + 2.0f ? floor : z;
    }

    Seats SeatsOf(Player* player, bool alliance)
    {
        Seats s;
        if (alliance)
        {
            for (uint32 i = 0; i < 4; ++i)
                s.chairs[i] = GILDED_ROSE_CHAIRS[i];
            s.stop = GILDED_ROSE_STOP;
            return s;
        }
        Place const& inn = BROKEN_TUSK;
        float cx = inn.x + TABLE_FROM_INN * std::cos(inn.o), cy = inn.y + TABLE_FROM_INN * std::sin(inn.o);
        s.table = Position(cx, cy, Floor(player, cx, cy, inn.z), inn.o);
        // (the Timerunner's on the innkeeper's side, then round the table, each facing it)
        float const around[4] = { float(M_PI), float(M_PI) / 2.0f, 0.0f, -float(M_PI) / 2.0f };
        for (uint32 i = 0; i < 4; ++i)
        {
            float a = inn.o + around[i];
            float x = cx + CHAIR_FROM_TABLE * std::cos(a), y = cy + CHAIR_FROM_TABLE * std::sin(a);
            s.chairs[i] = Place{ inn.map, x, y, Floor(player, x, y, inn.z), Position::NormalizeOrientation(a + float(M_PI)) };
        }
        float a = inn.o + float(M_PI) / 4.0f;
        float x = cx + 2.3f * std::cos(a), y = cy + 2.3f * std::sin(a);
        s.stop = Position(x, y, Floor(player, x, y, inn.z));
        return s;
    }

    // Everyone at the table on their feet for a toast, or sitting down again after it.
    void Toast(Player* player, Opening& b, bool up)
    {
        for (ObjectGuid guid : b.friends)
            if (Creature* c = Who(player, guid))
                c->SetStandState(up ? UNIT_STAND_STATE_STAND : UNIT_STAND_STATE_SIT_MEDIUM_CHAIR);
        if (up)
            StandUp(player);
        else
            SitDown(player);
    }

    // Everyone at the table drinking (their tankards raised), and the Timerunner with them.
    void Drink(Player* player, Opening& b)
    {
        for (ObjectGuid guid : b.friends)
            if (Creature* c = Who(player, guid))
                c->HandleEmoteCommand(EMOTE_ONESHOT_EAT);
        player->HandleEmoteCommand(EMOTE_ONESHOT_EAT);
    }

    void Tavern(Player* player, std::shared_ptr<Opening> o)
    {
        // (the room is seen as the curtain lifts: its talk starts once it's up)
        constexpr uint32 REVEAL = LIFT_MS;
        Opening& b = *o;
        bool alliance = Alliance(player);
        Place const& inn = alliance ? GILDED_ROSE : BROKEN_TUSK;
        Seats const seats = SeatsOf(player, alliance);
        player->SendPlayMusic(alliance ? MUSIC_TAVERN_ALLIANCE : MUSIC_TAVERN_HORDE, true);
        player->PlayDirectSound(SOUND_TAVERN_CROWD, player);
        if (Creature* keeper = Bring(player, b, alliance ? INNKEEPER_A : INNKEEPER_H, Position(inn.x, inn.y, inn.z, inn.o)))
            b.innkeeper = keeper->GetGUID();

        // The table and its chairs, in the opening's phase (the room's own chairs, the game's, are
        // in everyone's and not seen in it; the Gilded Rose's table is the room's).
        auto setOut = [player, &b](uint32 entry, float x, float y, float z, float facing)
        {
            if (GameObject* go = player->SummonGameObject(entry, x, y, z, facing, 0.0f, 0.0f, std::sin(facing / 2.0f), std::cos(facing / 2.0f), 300))
                b.props.push_back(go->GetGUID());
        };
        if (!alliance)
            setOut(GO_HORDE_TABLE, seats.table.GetPositionX(), seats.table.GetPositionY(), seats.table.GetPositionZ(), seats.table.GetOrientation());
        for (Place const& chair : seats.chairs)
            setOut(alliance ? GO_ALLIANCE_CHAIR : GO_HORDE_CHAIR, chair.x, chair.y, chair.z, chair.o);

        // The Timerunner in their chair (a new one is made in it), and kept there.
        Place const& mine = seats.chairs[0];
        if (player->GetExactDist2d(mine.x, mine.y) > 0.5f)
            player->NearTeleportTo(mine.x, mine.y, mine.z, mine.o);
        At(player, o, 300, [](Player* p, Opening&) { SitDown(p); });

        uint32 const party[3] = { alliance ? BRANNOC : GRAKKA, alliance ? SYLENNA : TAHONO, alliance ? TOBIAS : VEYLAN };
        for (uint32 i = 0; i < 3; ++i)
        {
            Place const& chair = seats.chairs[i + 1];
            if (Creature* c = Bring(player, b, party[i], Position(chair.x, chair.y, chair.z, chair.o)))
            {
                c->SetStandState(UNIT_STAND_STATE_SIT_MEDIUM_CHAIR);
                b.friends.push_back(c->GetGUID());
            }
        }

        for (TavernLine const& line : alliance ? std::vector<TavernLine>(std::begin(ALLIANCE_TAVERN), std::end(ALLIANCE_TAVERN))
                                               : std::vector<TavernLine>(std::begin(HORDE_TAVERN), std::end(HORDE_TAVERN)))
        {
            At(player, o, line.at + REVEAL, [line](Player* p, Opening& b)
            {
                ObjectGuid who = line.who == 3 ? b.innkeeper : (line.who < int(b.friends.size()) ? b.friends[line.who] : ObjectGuid::Empty);
                Creature* c = Who(p, who);
                // (one sitting talks without getting up: a gesture would bring them to their feet)
                Speak(p, c, line.text, c && c->IsSitState() ? 0 : line.emote);
            });
        }
        // The toast: on their feet, everyone cheers, the room with them; then they drink, and sit.
        At(player, o, 6500 + REVEAL, [](Player* p, Opening& b) { Toast(p, b, true); });
        At(player, o, 7600 + REVEAL, [alliance](Player* p, Opening& b)
        {
            for (ObjectGuid guid : b.friends)
                if (Creature* c = Who(p, guid))
                    c->HandleEmoteCommand(EMOTE_ONESHOT_CHEER);
            p->HandleEmoteCommand(EMOTE_ONESHOT_CHEER);
            p->PlayDirectSound(alliance ? SOUND_CHEER_ALLIANCE : SOUND_CHEER_HORDE, p);
        });
        At(player, o, 11500 + REVEAL, [](Player* p, Opening& b) { Drink(p, b); });
        At(player, o, 13800 + REVEAL, [](Player* p, Opening& b) { Toast(p, b, false); });
        // And to the friend who didn't come home: up again, a salute, a drink.
        At(player, o, 42000 + REVEAL, [](Player* p, Opening& b) { Toast(p, b, true); });
        At(player, o, 46000 + REVEAL, [](Player* p, Opening& b) { Drink(p, b); });
        At(player, o, 48500 + REVEAL, [](Player* p, Opening& b) { Toast(p, b, false); });

        // The room stops, mid-question, and Moratari walks in, to the table's edge.
        At(player, o, 69000 + REVEAL, [](Player* p, Opening& b)
        {
            Freeze(p, b, false);
            p->SendPlayMusic(0, true);
        });
        At(player, o, 71000 + REVEAL, [inn, seats](Player* p, Opening& b)
        {
            Position from = Indoors(p, inn, 11.0f, 0.0f);
            if (TempSummon* rift = p->SummonCreature(NPC_TIME_RIFT, from, TEMPSUMMON_TIMED_DESPAWN, 6000, 0, nullptr, true))
                b.people.push_back(rift->GetGUID());
            if (Creature* moratari = BringMoratari(p, b, from))
                moratari->GetMotionMaster()->MovePoint(1, seats.stop);
        });
        At(player, o, 75500 + REVEAL, [](Player* p, Opening& b) { SheSays(p, b, "I'm sorry, hero. I need you."); });
        At(player, o, 80500 + REVEAL, [](Player* p, Opening& b)
        {
            SheSays(p, b, "They cannot hear us. When we are done, I will bring you back to this very moment. But first, there is something you need to see again.");
        });
        At(player, o, 86000 + REVEAL, [o](Player* p, Opening&)
        {
            float x = FRONT_X - 2.0f * std::cos(FRONT_O), y = FRONT_Y - 2.0f * std::sin(FRONT_O);
            GoTo(p, o, Place{ MAP_NORTHREND, x, y, FRONT_Z, FRONT_O }, Front, CAPTION_FRONT);
        });
    }

    // ---- The Broken Front -----------------------------------------------------------------------

    // The Lich King comes, and the Scourge kneel to him.
    void TheKingComes(Player* player, Opening& b)
    {
        Position at = Spot(player, 30.0f, 0.0f, float(M_PI));
        if (Creature* blast = Effect(player, b, false, at, 6000))
        {
            blast->CastSpell(blast, SPELL_HUGE_EXPLOSION, true);
            blast->PlayDirectSound(SOUND_SHADOW_IMPACT, player);
        }
        Shake(player, true);
        player->SendPlayMusic(MUSIC_LICH_KING, true);
        if (Creature* king = Bring(player, b, LICH_KING, at, 2000000))
        {
            b.lichKing = king->GetGUID();
            king->CastSpell(king, SPELL_TELEPORT_VISUAL, true);
            king->SetFacingToObject(player);
        }
        for (ObjectGuid guid : b.people)
            if (Creature* c = Who(player, guid); c && c->IsAlive() && Fights(c->GetEntry()))
            {
                c->AttackStop();
                c->SetReactState(REACT_PASSIVE);
                c->GetMotionMaster()->Clear();
                c->StopMoving();
                if (Creature* king = Who(player, b.lichKing))
                    c->SetFacingToObject(king);
                if (c->GetEntry() <= DEATHBRINGER)
                    c->SetStandState(UNIT_STAND_STATE_KNEEL);
            }
        player->CombatStop(true);
    }

    // The battle, already raging: the line spread along the ridge, the dead coming from far off.
    void Front(Player* player, std::shared_ptr<Opening> o)
    {
        Opening& b = *o;
        if (Aura* wings = player->AddAura(SPELL_AVENGING_WRATH, player))
        {
            wings->SetMaxDuration(120000);
            wings->SetDuration(120000);
        }
        Shake(player, true);
        player->SendPlayMusic(MUSIC_BATTLE, true);

        // Tirion and the line: the Argent Crusade, and the Timerunner's own side, wide on both hands.
        if (Creature* tirion = Bring(player, b, TIRION, Spot(player, 4.0f, 3.0f), 400000, true))
            b.tirion = tirion->GetGUID();
        float const crusaders[][2] = { { 5.0f, -7.0f }, { 6.0f, 8.0f }, { 4.0f, -13.0f }, { 5.0f, 14.0f }, { 3.0f, -19.0f }, { 3.0f, 20.0f } };
        for (uint32 i = 0; i < std::size(crusaders); ++i)
            Bring(player, b, i % 2 ? CRUSADER : CRUSADER_2, Spot(player, crusaders[i][0], crusaders[i][1]), 60000, true);
        uint32 soldier = Alliance(player) ? MARINE : REAVER;
        float const soldiers[][2] = { { 0.0f, -10.0f }, { 0.0f, 11.0f }, { -1.0f, -16.0f }, { -1.0f, 17.0f } };
        for (auto const& at : soldiers)
            Bring(player, b, soldier, Spot(player, at[0], at[1]), 60000, true);
        BringMoratari(player, b, Spot(player, -3.0f, 2.5f));

        // The Scourge, coming across the snow.
        float const ghouls[][2] = { { 24.0f, -12.0f }, { 26.0f, -3.0f }, { 25.0f, 6.0f }, { 28.0f, 14.0f }, { 30.0f, -20.0f }, { 32.0f, 1.0f } };
        for (uint32 i = 0; i < std::size(ghouls); ++i)
            Bring(player, b, i % 3 ? GHOUL : SPIKED_GHOUL, Spot(player, ghouls[i][0], ghouls[i][1], float(M_PI)), i % 3 ? 700 : 900, true);
        if (Creature* fiend = Bring(player, b, CRYPT_FIEND, Spot(player, 34.0f, 9.0f, float(M_PI)), 1600, true))
            fiend->CastSpell(fiend, SPELL_EMERGE, true);

        At(player, o, 1500, [](Player* p, Opening& b)
        {
            Creature* tirion = Who(p, b.tirion);
            Say(p, tirion, TIRION_MUST_FALL);
            if (tirion)
            {
                tirion->CastSpell(tirion, SPELL_CONSECRATION, true);
                tirion->CastSpell(p, SPELL_HOLY_SHOCK, true);
            }
        });
        At(player, o, 3500, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Do you remember this, $N? The Broken Front, the last day of his war. Fight, if you like. Nothing here can hurt you.");
        });
        // His voice, from the Citadel: the dead rise.
        At(player, o, 5500, [](Player* p, Opening& b)
        {
            if (Creature* voice = Bring(p, b, LICH_KING_VOICE, Spot(p, 70.0f, 0.0f)))
            {
                b.voice = voice->GetGUID();
                Say(p, voice, LK_ARISE);
            }
            for (int i = 0; i < 5; ++i)
                RaiseGhoul(p, b, Somewhere(p, 20.0f, 38.0f), true);
            Shake(p, false);
        });
        // The field's blows, until the king comes; and the Scourge kept coming.
        for (uint32 t = 3000; t < 43000; t += 2400)
            At(player, o, t, [](Player* p, Opening& b) { Blow(p, b); });
        for (uint32 t = 8000; t < 42000; t += 3500)
            At(player, o, t, [](Player* p, Opening& b)
            {
                for (uint32 n = ScourgeStanding(p, b); n < 9; ++n)
                    RaiseGhoul(p, b, Somewhere(p, 22.0f, 40.0f), true);
            });
        // Abominations and deathbringers, from far up the slope.
        At(player, o, 13000, [](Player* p, Opening& b)
        {
            Say(p, Who(p, b.voice), LK_RAVAGE);
            for (float left : { -10.0f, 11.0f })
                if (Creature* abom = Bring(p, b, ABOMINATION, Spot(p, 50.0f, left, float(M_PI)), 4500, true))
                    abom->GetMotionMaster()->MovePoint(1, Spot(p, 16.0f, left * 0.6f));
            for (float left : { -17.0f, 18.0f })
                Bring(p, b, DEATHBRINGER, Spot(p, 38.0f, left, float(M_PI)), 2500, true);
        });
        At(player, o, 18500, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Look at them. Every one of those ghouls had a name once. He wasted no one.");
        });
        At(player, o, 23000, [](Player* p, Opening& b)
        {
            Creature* tirion = Who(p, b.tirion);
            Say(p, tirion, TIRION_NO_MORE);
            if (tirion)
                tirion->CastSpell(tirion, SPELL_DIVINE_STORM, true);
        });
        // A frost wyrm, low over the line.
        At(player, o, 28000, [](Player* p, Opening& b)
        {
            Position from = Spot(p, 90.0f, 30.0f, float(M_PI));
            from.m_positionZ += 30.0f;
            Creature* wyrm = Bring(p, b, FROST_WYRM, from, 1000000);
            if (!wyrm)
                return;
            wyrm->SetCanFly(true);
            wyrm->SetDisableGravity(true);
            wyrm->SetSpeed(MOVE_FLIGHT, 3.0f);
            wyrm->SetSpeed(MOVE_RUN, 3.0f);
            Position to = Spot(p, -70.0f, -25.0f);
            wyrm->GetMotionMaster()->MovePoint(1, to.GetPositionX(), to.GetPositionY(), to.GetPositionZ() + 22.0f,
                FORCED_MOVEMENT_NONE, 0.0f, 0.0f, false);
            wyrm->PlayDirectSound(SOUND_FROST_WYRM, p);
            wyrm->DespawnOrUnsummon(10s);
            ObjectGuid guid = p->GetGUID();
            uint32 act = b.act;
            for (uint32 i = 0; i < 4; ++i)
                p->m_Events.AddEventAtOffset([guid, i, act]()
                {
                    Player* pl = ObjectAccessor::FindPlayer(guid);
                    std::shared_ptr<Opening> o = pl ? OpeningOf(pl) : nullptr;
                    if (!o || o->frozen || o->act != act)
                        return;
                    // the breath, across the field ahead of the line
                    Position at = Spot(pl, 26.0f - 7.0f * float(i), i % 2 ? 14.0f : -14.0f);
                    if (Creature* frost = Effect(pl, *o, true, at, 5000))
                    {
                        frost->CastSpell(frost, SPELL_EXPLOSION, true);
                        frost->PlayDirectSound(SOUND_FROST_IMPACT, pl);
                    }
                    Shake(pl, i == 2);
                }, Milliseconds(1400 + 600 * i));
        });
        // The val'kyr, at his call.
        At(player, o, 34000, [](Player* p, Opening& b)
        {
            Say(p, Who(p, b.voice), LK_VALKYR);
            for (float left : { -16.0f, 16.0f })
            {
                Position at = Spot(p, 46.0f, left, float(M_PI));
                at.m_positionZ += 14.0f;
                if (Creature* valkyr = Bring(p, b, VALKYR, at, 100000))
                {
                    valkyr->SetCanFly(true);
                    valkyr->SetDisableGravity(true);
                    Position over = Spot(p, 24.0f, left * 0.7f);
                    valkyr->GetMotionMaster()->MovePoint(1, over.GetPositionX(), over.GetPositionY(), over.GetPositionZ() + 9.0f,
                        FORCED_MOVEMENT_NONE, 0.0f, 0.0f, false);
                }
            }
        });
        // The king.
        At(player, o, 43000, [](Player* p, Opening& b) { TheKingComes(p, b); });
        At(player, o, 45500, [](Player* p, Opening& b) { Say(p, Who(p, b.lichKing), LK_HOPE); });
        At(player, o, 48000, [](Player* p, Opening& b)
        {
            Creature* tirion = Who(p, b.tirion);
            Say(p, tirion, TIRION_ARTHAS);
            if (tirion)
            {
                tirion->SetStandState(UNIT_STAND_STATE_STAND);
                tirion->GetMotionMaster()->MovePoint(2, Spot(p, 20.0f, 1.0f));
            }
        });
        // The winter takes the paladin to his knee.
        At(player, o, 57500, [](Player* p, Opening& b)
        {
            if (Creature* king = Who(p, b.lichKing))
                king->CastSpell(king, SPELL_REMORSELESS_WINTER, true);
            Shake(p, true);
            if (Creature* tirion = Who(p, b.tirion))
            {
                tirion->StopMoving();
                tirion->SetStandState(UNIT_STAND_STATE_KNEEL);
            }
        });
        // And he turns to the Timerunner.
        At(player, o, 60500, [](Player* p, Opening& b)
        {
            if (Creature* king = Who(p, b.lichKing))
            {
                king->SetFacingToObject(p);
                king->Say("You... You are not of this hour.", LANG_UNIVERSAL, p);
            }
        });
        At(player, o, 65000, [](Player* p, Opening& b)
        {
            if (Creature* king = Who(p, b.lichKing))
            {
                Say(p, king, LK_HUNGERS);
                king->CastSpell(king, SPELL_FURY_OF_FROSTMOURNE, false);
            }
        });
        // Time stops.
        At(player, o, 66600, [](Player* p, Opening& b) { Freeze(p, b); });
        At(player, o, 69500, [](Player* p, Opening& b)
        {
            if (Creature* moratari = Who(p, b.moratari))
                moratari->GetMotionMaster()->MovePoint(1, Spot(p, -1.0f, 1.5f));
            SheSays(p, b, "Enough. You know how the rest goes. You won. But you remember what it cost, don't you?");
        });
        At(player, o, 76000, [](Player* p, Opening& b) { SheSays(p, b, "Let me show you what you have been trying to forget."); });
        At(player, o, 81000, [o](Player* p, Opening&) { GoTo(p, o, WRATHGATE, Wrathgate, CAPTION_WRATHGATE); });
    }

    // ---- What his reign cost ----------------------------------------------------------------------

    // A place on a field ahead of the Timerunner, not on top of them.
    Position OnTheField(Player* player, Place const& at, float nearest, float farthest, float wide)
    {
        for (int tries = 0; tries < 8; ++tries)
        {
            Position p = Around(player, at, frand(nearest, farthest), frand(-wide, wide));
            if (player->GetExactDist2d(p.GetPositionX(), p.GetPositionY()) > 3.5f)
                return p;
        }
        return Around(player, at, farthest, 0.0f);
    }

    // Plague lying over a place, and now and then bursting.
    void Plague(Player* player, Opening& b, Place const& at, uint32 patches, uint32 lasts)
    {
        for (uint32 i = 0; i < patches; ++i)
            if (Creature* plague = Effect(player, b, true, OnTheField(player, at, 5.0f, 26.0f, 18.0f), lasts))
                plague->CastSpell(plague, SPELL_DEATH_AND_DECAY, true);
    }

    void Wrathgate(Player* player, std::shared_ptr<Opening> o)
    {
        Opening& b = *o;
        Place const& at = WRATHGATE;
        player->SendPlayMusic(MUSIC_LAMENT, true);
        BringMoratari(player, b, Around(player, at, -1.0f, 2.5f));
        // Saurfang's son, where he fell first; Bolvar, in the dragonfire: as they were in that moment.
        if (Creature* dranosh = Bring(player, b, NPC_ECHO_SAURFANG, Around(player, at, 10.0f, 3.0f, float(M_PI))))
            dranosh->SetStandState(UNIT_STAND_STATE_KNEEL);
        if (Creature* bolvar = Bring(player, b, NPC_ECHO_BOLVAR, Around(player, at, 14.0f, -4.0f, float(M_PI))))
            bolvar->SetStandState(UNIT_STAND_STATE_KNEEL);
        for (uint32 i = 0; i < 16; ++i)
            Body(player, b, i % 2 ? FALLEN_H : FALLEN_A, OnTheField(player, at, 4.0f, 26.0f, 18.0f));
        Plague(player, b, at, 6, 50000);
        for (uint32 t = 4000; t < 40000; t += 4500)
            At(player, o, t, [](Player* p, Opening& b)
            {
                if (Creature* burst = Effect(p, b, true, OnTheField(p, WRATHGATE, 6.0f, 28.0f, 20.0f), 5000))
                    burst->CastSpell(burst, SPELL_GREEN_EXPLOSION, true);
            });
        // The dragonfire where Bolvar knelt.
        for (uint32 t = 1000; t < 40000; t += 6000)
            At(player, o, t, [](Player* p, Opening& b)
            {
                if (Creature* fire = Effect(p, b, false, Around(p, WRATHGATE, 14.0f, -4.0f), 7000))
                    fire->CastSpell(fire, SPELL_PILLAR_OF_FIRE, true);
            });

        At(player, o, 2500, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Angrathar, the Wrathgate. The Alliance and the Horde stood side by side here, for once, at the very door of Icecrown.");
        });
        At(player, o, 11000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Dranosh Saurfang fell first, to the Lich King's own blade. Later, in the Citadel, his father had to carry home what Arthas made of him.", EMOTE_ONESHOT_POINT);
        });
        At(player, o, 20000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Then the Forsaken's plague fell on the living and the dead alike, and the red dragonflight burned it away. Bolvar Fordragon burned with it.");
        });
        At(player, o, 29000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "After that day, the Alliance and the Horde were enemies again. That suited the Lich King very well.");
        });
        At(player, o, 37000, [](Player* p, Opening& b) { SheSays(p, b, "Come. The soldiers, at least, knew what they were marching into."); });
        At(player, o, 41000, [o](Player* p, Opening&) { GoTo(p, o, WINTERGARDE, Wintergarde, CAPTION_WINTERGARDE); });
    }

    void Wintergarde(Player* player, std::shared_ptr<Opening> o)
    {
        Opening& b = *o;
        Place const& at = WINTERGARDE;
        BringMoratari(player, b, Around(player, at, -1.0f, 2.5f));
        // Its people, cowering; the dead they knew coming for them.
        std::vector<Position> people;
        for (uint32 i = 0; i < 8; ++i)
        {
            Position spot = OnTheField(player, at, 3.0f, 15.0f, 10.0f);
            if (Creature* villager = Bring(player, b, i % 2 ? VILLAGER_F : VILLAGER, spot))
            {
                villager->SetFacingTo(Facing(spot.GetPositionX(), spot.GetPositionY(), player->GetPositionX(), player->GetPositionY()));
                villager->SetUInt32Value(UNIT_NPC_EMOTESTATE, EMOTE_STATE_COWER);
                people.push_back(spot);
            }
        }
        for (uint32 i = 0; i < 5; ++i)
            if (Creature* risen = Bring(player, b, RISEN_VILLAGER, OnTheField(player, at, 16.0f, 24.0f, 12.0f)))
            {
                risen->SetWalk(true);
                if (!people.empty())
                    risen->GetMotionMaster()->MovePoint(1, people[i % people.size()]);
            }
        for (uint32 i = 0; i < 4; ++i)
            Body(player, b, i % 2 ? VILLAGER_F : VILLAGER, OnTheField(player, at, 6.0f, 20.0f, 14.0f));
        Plague(player, b, at, 3, 50000);
        // The bodies of the morning, rising.
        for (uint32 t : { 7000u, 15000u, 23000u, 31000u })
            At(player, o, t, [](Player* p, Opening& b)
            {
                for (ObjectGuid guid : b.fallen)
                    if (Creature* body = Who(p, guid); body && body->IsAlive() && body->IsVisible())
                    {
                        Position spot = body->GetPosition();
                        body->DespawnOrUnsummon();
                        RaiseGhoul(p, b, spot, false);
                        p->PlayDirectSound(SOUND_RAISE_DEAD, p);
                        return;
                    }
            });

        At(player, o, 2500, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Wintergarde. Farmers and miners, with Naxxramas hanging over their roofs like a second sky.");
        });
        At(player, o, 11000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "The plague came down out of it in the night. By morning, their own neighbors were at their doors.");
        });
        At(player, o, 20000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "He raised the miners and sent them back down their own mine, to dig for him.");
        });
        At(player, o, 29000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "It was the same in Andorhal, and Stratholme, and Silvermoon. Wintergarde was only one of the last.");
        });
        At(player, o, 37000, [](Player* p, Opening& b) { SheSays(p, b, "One more. This one, you will know."); });
        At(player, o, 41000, [o](Player* p, Opening&) { GoTo(p, o, FIELDS, Fields, CAPTION_FIELDS); });
    }

    void Fields(Player* player, std::shared_ptr<Opening> o)
    {
        Opening& b = *o;
        Place const& at = FIELDS;
        BringMoratari(player, b, Around(player, at, -1.0f, 2.5f));
        // The fallen of both sides, in rows where the val'kyr laid them.
        for (uint32 row = 0; row < 4; ++row)
            for (uint32 i = 0; i < 5; ++i)
            {
                float left = -14.0f + 7.0f * float(i) + frand(-1.5f, 1.5f);
                float forward = 6.0f + 4.5f * float(row) + frand(-1.0f, 1.0f);
                Body(player, b, (row + i) % 2 ? FALLEN_H : FALLEN_A, Around(player, at, forward, left));
            }
        // Ranks of the risen beyond them, facing the Citadel.
        for (uint32 rank = 0; rank < 2; ++rank)
            for (uint32 i = 0; i < 9; ++i)
                Bring(player, b, i % 3 ? GHOUL : SPIKED_GHOUL, Around(player, at, 28.0f + 4.0f * float(rank), -16.0f + 4.0f * float(i)));
        // The val'kyr over the field.
        for (float left : { -9.0f, 0.0f, 9.0f })
        {
            Position over = Around(player, at, 14.0f + frand(-2.0f, 2.0f), left);
            over.m_positionZ += 6.0f;
            if (Creature* valkyr = Bring(player, b, VALKYR, over, 100000))
            {
                valkyr->SetCanFly(true);
                valkyr->SetDisableGravity(true);
            }
        }
        // His voice, far off: and the fallen rise, one after another, and join the ranks.
        At(player, o, 6000, [](Player* p, Opening& b)
        {
            if (Creature* voice = Bring(p, b, LICH_KING_VOICE, Around(p, FIELDS, 80.0f, 0.0f)))
                Say(p, voice, LK_ARISE);
        });
        for (uint32 t = 8000; t < 46000; t += 3500)
            At(player, o, t, [](Player* p, Opening& b)
            {
                std::vector<Creature*> lying;
                for (ObjectGuid guid : b.fallen)
                    if (Creature* body = Who(p, guid); body && body->IsAlive())
                        lying.push_back(body);
                if (lying.empty())
                    return;
                Creature* body = lying[urand(0, uint32(lying.size()) - 1)];
                Position spot = body->GetPosition();
                body->DespawnOrUnsummon();
                RaiseGhoul(p, b, spot, false);
                p->PlayDirectSound(SOUND_RAISE_DEAD, p);
            });

        At(player, o, 2500, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Icecrown. The val'kyr carried the fallen here from every battle they could reach.");
        });
        At(player, o, 11000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "Ask the Forsaken what it is like to march for him. They remember every day of it.");
        });
        At(player, o, 20000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "$F is in those ranks somewhere, $N. I think you have always known that.");
        });
        At(player, o, 28000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "You beat him, and still you could not bring them back. No one could.");
        });
        At(player, o, 35000, [](Player* p, Opening& b) { SheSays(p, b, "Unless none of it ever happens."); });
        At(player, o, 40000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "We can stop all of this. We can undo it. $F could come home.", EMOTE_ONESHOT_EXCLAMATION);
        });
        At(player, o, 47000, [](Player* p, Opening& b)
        {
            SheSays(p, b, "The rest is my mistress's to tell. Hold still.");
        });
        At(player, o, 50000, [](Player* p, Opening& b)
        {
            if (Creature* moratari = Who(p, b.moratari))
                moratari->CastSpell(p, SPELL_TIME_RIFT, true);
        });
        At(player, o, 53000, [](Player* p, Opening& b) { Finish(p, b); });
    }

    // A Timerunner the opening is still owed to: never seen through, nor the prologue begun. Not a
    // death knight, who has Acherus, nor one of the realm's bots.
    bool Owed(Player* player)
    {
        if (!Active() || !Enabled() || IsBot(player) || player->getClass() == CLASS_DEATH_KNIGHT)
            return false;
        return !Get(player).intro && player->GetQuestStatus(QUEST_OUT_OF_TIME) == QUEST_STATUS_NONE &&
            !player->GetQuestRewardStatus(QUEST_OUT_OF_TIME);
    }

    // Where a new Timerunner is made (the Bazaar), or where the opening keeps one who left it.
    bool AtTheStart(Player* player)
    {
        return AtTheBazaar(player) || AtTheFront(player) || AtATavern(player);
    }

    // Owed it at login, and somewhere it begins from: at the start; or anywhere at all for one who
    // hasn't begun the war (chapter 0), since the realm saves them every half minute, a crash
    // leaves them wherever the opening had them, and a start playercreateinfo got wrong (a
    // Skyborne's, in Northshire or at Camp Narache) is nowhere near the Bazaar. Only a new one
    // (under an hour played: the opening is six minutes), not one made before it, who went their
    // own way without the prologue and has played since. Not from the Caverns of Time, where
    // Timerunners were made until build 64: they wake at the Bazaar first (WrathRemix.cpp), and it
    // begins there at their next login.
    bool Wanted(Player* player)
    {
        if (!Owed(player))
            return false;
        if (AtTheStart(player))
            return true;
        return Get(player).chapter == 0 && player->GetTotalPlayedTime() < uint32(HOUR) &&
            !(player->GetMapId() == MAP_KALIMDOR && player->GetAreaId() == AREA_CAVERNS_OF_TIME);
    }

    void Begin(Player* player)
    {
        auto opening = std::make_shared<Opening>();
        opening->player = player->GetGUID();
        {
            std::lock_guard<std::mutex> lock(openingsLock);
            if (!openings.emplace(player->GetGUID(), opening).second)
                return;
            ++running;
        }
        // To the tavern: in their chair at the table with their friends.
        GoTo(player, opening, SeatsOf(nullptr, Alliance(player)).chairs[0], Tavern, Alliance(player) ? CAPTION_TAVERN_A : CAPTION_TAVERN_H);
    }
}

bool WrathRemix::InIntro(Player* player)
{
    return player && OpeningOf(player) != nullptr;
}

void WrathRemix::ClientSettled(Player* player)
{
    if (!player)
        return;
    std::lock_guard<std::mutex> lock(settledLock);
    Curtains& c = curtains[player->GetGUID()];
    ++c.settles;
    c.settled = true;
    c.settledAt = std::chrono::steady_clock::now();
}

std::string WrathRemix::CurtainStatus(Player* player)
{
    if (!player)
        return "no curtain";
    std::lock_guard<std::mutex> lock(settledLock);
    auto it = curtains.find(player->GetGUID());
    if (it == curtains.end() || it->second.drawn == 0)
        return "no curtain yet";
    Curtains const& c = it->second;
    auto ago = [](std::chrono::steady_clock::time_point at)
    {
        return std::chrono::duration<float>(std::chrono::steady_clock::now() - at).count();
    };
    std::string text = Acore::StringFormat("curtain {} ({:.1f} s ago)", c.drawn, ago(c.drawnAt));
    if (c.settles)
        text += Acore::StringFormat(", settled {} ({:.1f} s ago{})", c.settles, ago(c.settledAt), c.settled ? "" : ", before the curtain");
    else
        text += ", never settled";
    return text;
}

// Where a journey goes, as the curtain says it: the Bazaar by name; a dungeon or a raid by its
// map's; anywhere else its area, and its zone after it where that's another name ("Wyrmrest
// Temple | Dragonblight"). The place's terrain is read for it (loaded if it isn't yet: the journey
// is about to need it anyway).
std::string WrathRemix::PlaceName(uint32 map, float x, float y, float z)
{
    MapEntry const* entry = sMapStore.LookupEntry(map);
    if (!entry)
        return "";
    if (entry->Instanceable())
        return entry->name[0];
    if (map == MAP_NORTHREND && std::hypot(x - BAZAAR_X, y - BAZAAR_Y) < 150.0f)
        return CAPTION_BAZAAR_HOME;
    uint32 zone = 0, area = 0;
    sMapMgr->GetZoneAndAreaId(PHASEMASK_NORMAL, zone, area, map, x, y, z);
    AreaTableEntry const* in = sAreaTableStore.LookupEntry(area);
    AreaTableEntry const* of = sAreaTableStore.LookupEntry(zone);
    std::string name = in ? in->area_name[0] : "";
    if (of && zone != area && name != of->area_name[0])
        name += (name.empty() ? "" : " | ") + std::string(of->area_name[0]);
    return name;
}

void WrathRemix::JourneyFromTheDark(Player* player, std::string const& caption, uint32 map, float x, float y, uint32 leastMs, uint32 liftMs)
{
    if (!player || IsBot(player))
        return;
    Curtain(player, caption.c_str());
    WhenArrived(player->GetGUID(), map, x, y, 40, caption, leastMs, liftMs);
}

void WrathRemix::LiftTheCurtain(Player* player)
{
    if (player && !IsBot(player))
        Lift(player, 1000);
}

void WrathRemix::PlayIntro(Player* player)
{
    if (InIntro(player))
        return;
    Begin(player);
}

void WrathRemix::SkipIntro(Player* player)
{
    if (std::shared_ptr<Opening> opening = OpeningOf(player))
        Finish(player, *opening);
    else if (Active())
    {
        bool owed = Owed(player);
        SetIntroSeen(player);
        // (one made in their tavern, skipping it before it began: to the Bazaar, where it ends, their
        // hearthstone with it)
        if (owed && AtATavern(player))
        {
            WorldLocation bazaar(MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O);
            player->SetHomebind(bazaar, AREA_MALYKRISS);
            player->TeleportTo(bazaar);
        }
    }
}

// Everyone in it: in the battle they fight the other side, and the Timerunner's blows land as a
// hero's; everyone else stands where they're put.
class npc_remix_intro : public CreatureScript
{
public:
    npc_remix_intro() : CreatureScript("npc_remix_intro") { }

    struct npc_remix_introAI : public ScriptedAI
    {
        npc_remix_introAI(Creature* creature) : ScriptedAI(creature) { }

        uint32 lookIn = 300;
        uint32 specialIn = urand(3000, 6000);

        // (the wyrm, the val'kyr, the king, the unseen ones, the tavern's people and the dead are
        // the opening's to move)
        bool Scripted() const
        {
            uint32 entry = me->GetEntry();
            return entry == FROST_WYRM || entry == VALKYR || entry == LICH_KING || entry >= LIGHT;
        }

        void Reset() override { }

        void MoveInLineOfSight(Unit* who) override
        {
            if (!Scripted() && me->HasReactState(REACT_AGGRESSIVE))
                ScriptedAI::MoveInLineOfSight(who);
        }

        void AttackStart(Unit* who) override
        {
            if (!Scripted() && me->HasReactState(REACT_AGGRESSIVE))
                ScriptedAI::AttackStart(who);
        }

        void JustDied(Unit* /*killer*/) override
        {
            if (me->GetEntry() == ABOMINATION)
                me->CastSpell(me, SPELL_GREEN_EXPLOSION, true);
            me->DespawnOrUnsummon(5s);
        }

        void UpdateAI(uint32 diff) override
        {
            if (Scripted() || me->HasUnitState(UNIT_STATE_STUNNED) || !me->HasReactState(REACT_AGGRESSIVE))
                return;
            if (!UpdateVictim())
            {
                if (lookIn <= diff)
                {
                    lookIn = 700;
                    if (Unit* target = me->SelectNearestTarget(40.0f))
                        AttackStart(target);
                }
                else
                    lookIn -= diff;
                return;
            }
            if (specialIn <= diff)
            {
                specialIn = urand(4000, 7000);
                switch (me->GetEntry())
                {
                    case DEATHBRINGER:
                        DoCastVictim(SPELL_SHADOW_BOLT);
                        break;
                    case TIRION:
                        DoCast(me, urand(0, 1) ? SPELL_DIVINE_STORM : SPELL_CONSECRATION, true);
                        break;
                    default:
                        break;
                }
            }
            DoMeleeAttackIfReady();
        }
    };

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_remix_introAI(creature);
    }
};

// Nothing there hurts the Timerunner; their blows fell the dead in one to three; the two sides wear
// each other down slowly, so the line holds and the field stays full.
class RemixIntroDamage : public UnitScript
{
public:
    RemixIntroDamage() : UnitScript("RemixIntroDamage", true, { UNITHOOK_ON_DAMAGE, UNITHOOK_ON_UNIT_DEATH }) { }

    static bool OfTheOpening(Unit const* unit)
    {
        return unit && unit->IsCreature() && unit->GetEntry() >= INTRO_FIRST && unit->GetEntry() <= INTRO_LAST;
    }

    void OnDamage(Unit* attacker, Unit* victim, uint32& damage) override
    {
        if (!running.load() || !damage || !attacker || !victim)
            return;
        if (Player* hero = victim->ToPlayer(); hero && InIntro(hero))
        {
            damage = 0;
            return;
        }
        if (!OfTheOpening(victim))
            return;
        if (Player* hero = attacker->GetCharmerOrOwnerPlayerOrPlayerItself(); hero && InIntro(hero))
        {
            float share = victim->GetEntry() == ABOMINATION ? 0.2f : 0.36f;
            damage = std::max<uint32>(damage * 12, uint32(victim->GetMaxHealth() * share) + 1);
            return;
        }
        if (OfTheOpening(attacker))
        {
            bool allyHurt = victim->GetEntry() >= TIRION && victim->GetEntry() <= REAVER;
            float cap = allyHurt ? 0.01f : 0.05f;
            damage = std::min<uint32>(damage, std::max<uint32>(1, uint32(victim->GetMaxHealth() * cap)));
        }
    }

    // (a kill outright; a fall under the world is the player script's)
    void OnUnitDeath(Unit* unit, Unit* /*killer*/) override
    {
        if (Player* hero = unit->ToPlayer(); hero && running.load())
            UndoDeath(hero);
    }
};

class RemixIntroPlayer : public PlayerScript
{
public:
    RemixIntroPlayer() : PlayerScript("RemixIntroPlayer", { PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_BEFORE_LOGOUT, PLAYERHOOK_ON_PLAYER_JUST_DIED }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (!Active() || IsBot(player))
            return;
        ObjectGuid guid = player->GetGUID();
        // The curtain before their loading screen ends (the game keeps what the realm sends it
        // meanwhile), so the tavern isn't seen loading; lifted below if the opening isn't theirs after all.
        bool curtained = Wanted(player);
        if (curtained)
            Curtain(player, Alliance(player) ? CAPTION_TAVERN_A : CAPTION_TAVERN_H);
        // (after the realm's own first moments: the kit on, the abilities learned)
        player->m_Events.AddEventAtOffset([guid, curtained]()
        {
            Player* p = ObjectAccessor::FindPlayer(guid);
            if (!p || !p->IsInWorld())
                return;
            bool owed = Owed(p);
            bool begin = Wanted(p);
            if (!begin && curtained)
                Lift(p);
            // (the Light's wings, saved with them by the realm's own saves, if a crash cut it short)
            if (owed)
            {
                p->RemoveAurasDueToSpell(SPELL_AVENGING_WRATH);
                p->RemoveAurasDueToSpell(SPELL_TIME_STOP_VISUAL);
            }
            // Dead in the prologue (a ghost the opening left in Icecrown, before deaths in it were
            // undone): alive again, and into the opening if it's still theirs, else at the Bazaar.
            // (A death knight's prologue is Acherus's.)
            if (!p->IsAlive() && Get(p).chapter == 0 && p->getClass() != CLASS_DEATH_KNIGHT)
            {
                if (begin)
                    Revive(p);
                else if (p->GetMapId() == MAP_NORTHREND)
                {
                    BackFromDeath(p, Place{ MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O });
                    return;
                }
            }
            if (!begin)
                return;
            // (one made anywhere but the Bazaar has their hearthstone remember it, as everyone else's does)
            if (p->m_homebindMapId != MAP_NORTHREND)
            {
                WorldLocation bazaar(MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O);
                p->SetHomebind(bazaar, AREA_MALYKRISS);
            }
            Begin(p);
        }, 1500ms);
    }

    // (the core's kill for a fall under the world)
    void OnPlayerJustDied(Player* player) override
    {
        UndoDeath(player);
    }

    // Cut short: the opening goes with them, and it begins again from the tavern at their next
    // login. Before the core saves them (it saves before the logout hook): in Northrend they're
    // saved at the Bazaar, alive and without its wings; one who left in the tavern, there. (A
    // teleport while they log out moves nothing but where they're saved: the core saves a
    // teleport under way at its end. Still in the opening as it goes, so the hourglass doesn't
    // count where it had them as somewhere they came from.)
    void OnPlayerBeforeLogout(Player* player) override
    {
        std::shared_ptr<Opening> opening = OpeningOf(player);
        if (!opening)
            return;
        opening->over = true;
        player->RemoveAurasDueToSpell(SPELL_AVENGING_WRATH);
        player->RemoveAurasDueToSpell(SPELL_TIME_STOP_VISUAL);
        // (one the core couldn't bring into a map is left where they're saved: the next login
        // begins it again from anywhere, chapter 0 as they are)
        if (player->IsInWorld())
        {
            Despawn(player, *opening);
            player->SetPhaseMask(PHASEMASK_NORMAL, false);
            if (!player->IsAlive())
                Revive(player);
            if (player->GetMapId() == MAP_NORTHREND)
                player->TeleportTo(MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O);
        }
        EndOpening(player);
    }
};

// Where every new character but a death knight is made: in their side's tavern, in their chair at
// the table, when the opening is theirs (so the first thing loaded is where it begins, and nothing
// else before it); at the Bazaar without it (wrath_remix_world_0003_prologue.sql). Set in the
// server's own copy as it starts (before anyone can log in; nothing reads it but a character's
// making and their first hearthstone, which the opening sets to the Bazaar), whatever else rewrites
// playercreateinfo: mod-skyborne's SQL, applied again each time it changes, puts its races' start
// back in Northshire and at Camp Narache.
// And everywhere the opening goes, and the Bazaar, loaded as the realm starts (the core keeps a
// grid it has loaded), so the phone isn't loading those places' ground and people as the
// Timerunner arrives.
class RemixIntroWorld : public WorldScript
{
public:
    RemixIntroWorld() : WorldScript("RemixIntroWorld", { WORLDHOOK_ON_STARTUP }) { }

    void OnStartup() override
    {
        if (!Active())
            return;
        bool intro = Enabled();
        uint32 moved = 0;
        for (uint32 race = 1; race < RaceMgr::GetMaxRaces(); ++race)
            for (uint32 cls = 1; cls < MAX_CLASSES; ++cls)
            {
                PlayerInfo* info = const_cast<PlayerInfo*>(sObjectMgr->GetPlayerInfo(race, cls));
                if (!info || cls == CLASS_DEATH_KNIGHT)
                    continue;
                bool alliance = Player::TeamIdForRace(uint8(race)) == TEAM_ALLIANCE;
                Place start = intro ? SeatsOf(nullptr, alliance).chairs[0] : Place{ MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O };
                uint32 zone = !intro ? uint32(AREA_MALYKRISS) : (alliance ? ZONE_STORMWIND_CITY : ZONE_ORGRIMMAR);
                if (info->mapId == start.map && std::hypot(info->positionX - start.x, info->positionY - start.y) < 1.0f)
                    continue;
                info->mapId = start.map;
                info->areaId = zone;
                info->positionX = start.x;
                info->positionY = start.y;
                info->positionZ = start.z;
                info->orientation = start.o;
                ++moved;
            }
        if (moved)
            LOG_INFO("module", "Wrath Remix: {} race and class starts moved to {}", moved, intro ? "their side's tavern (the opening)" : "the Infinite Bazaar");

        uint32 started = getMSTime();
        for (Place const& at : { GILDED_ROSE, BROKEN_TUSK, Place{ MAP_NORTHREND, FRONT_X, FRONT_Y, FRONT_Z, FRONT_O }, WRATHGATE,
                                 WINTERGARDE, FIELDS, Place{ MAP_NORTHREND, BAZAAR_X, BAZAAR_Y, BAZAAR_Z, BAZAAR_O } })
            if (Map* map = sMapMgr->CreateBaseMap(at.map))
                map->LoadGridsInRange(Position(at.x, at.y, at.z), at.map == MAP_NORTHREND && at.x == FRONT_X ? FRONT_REACH : 100.0f);
        LOG_INFO("module", "Wrath Remix: the opening's places and the Bazaar loaded ({} ms)", GetMSTimeDiffToNow(started));
    }
};

void AddRemixIntroScripts()
{
    new npc_remix_intro();
    new RemixIntroDamage();
    new RemixIntroPlayer();
    new RemixIntroWorld();
}
