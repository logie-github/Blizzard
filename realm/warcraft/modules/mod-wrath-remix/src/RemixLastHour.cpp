// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Eternus's last hour (STORY.md, Chapter VII, WRM-721): at the doors of Icecrown Citadel, Eternus
 * and the Infinite still loyal to her, and beside the Timerunner Moratari, Sylvanas and Alleria.
 *
 * She speaks first, and they answer; then the fight: her loyalists in waves (as it begins, at 70% of
 * her strength and at 40%), her own blows and her time magic. She is not killed: with a tenth of her
 * strength left she stops, says her last, and steps into a rift, and the quest's credit is given to
 * every Timerunner there who is on it. Then the three say theirs and go, and the Moratari of the
 * doors is there with The Last Necessary Battle.
 *
 * Begun as WRM-721 brings the Timerunner to the doors; the Moratari outside the Frozen Halls takes
 * them back to begin again if they died, went or logged out before it was over. Theirs is on while
 * their Eternus is there and alive: one the grid took away with it, unwatched, never holds it up.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "Map.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "TemporarySummon.h"
#include <iterator>
#include <mutex>
#include <unordered_map>

using namespace WrathRemix;

namespace
{
    enum LastHourSpells : uint32
    {
        SPELL_WOUNDING_STRIKE   = 52771,
        SPELL_CURSE_OF_EXERTION = 52772,
        SPELL_TIME_WARP         = 52766,
        SPELL_TIME_STOP         = 58848,
        SPELL_SAND_BREATH       = 31478,
        SPELL_TELEPORT_VISUAL   = 51347,
        // the three beside the Timerunner
        SPELL_ARCANE_BOLT       = 15124,
        SPELL_BLACK_ARROW       = 59712,
        SPELL_VOID_BOLT         = 39329,
    };

    enum LastHourEvents : uint32
    {
        EVENT_INTRO = 1,
        EVENT_FIGHT,
        EVENT_WOUNDING_STRIKE,
        EVENT_CURSE,
        EVENT_TIME_WARP,
        EVENT_SAND_BREATH,
        EVENT_RETREAT,
        EVENT_GONE,
        EVENT_WATCH,
    };

    enum LastHourData : uint32
    {
        DATA_ALLY_MORATARI = 1,
        DATA_ALLY_SYLVANAS,
        DATA_ALLY_ALLERIA,
    };

    // Who says what before the fight, in order: 0 Eternus, 1 Moratari, 2 Sylvanas, 3 Alleria.
    struct Line
    {
        uint32 at;
        uint8 who;
        char const* text;
    };
    Line const INTRO[] = {
        { 3000,  0, "So. You came the long way round, as I knew you would." },
        { 8000,  0, "Behind those doors is the last hour of this war. A king on a throne of ice, and a paladin who will burn in his place. You know how it ends. So do I. I have watched it end more times than you have drawn breath." },
        { 20000, 0, "I am not here to stop the Lich King from falling. I am here to keep the hour from closing behind him. Hold this door with me, and every grave in this war stays open long enough for me to reach into it." },
        // (the Timerunner was taken from a tavern, after the war, toasting a friend who died in it; she knows it, and so does Sylvanas)
        { 33000, 0, "And yours, Timerunner. I know the hour I took you from: a table of friends toasting a war they won, and one chair empty. Hold this door with me, and no one ever has to sit beside it." },
        { 47000, 2, "Do not answer her. Not about that chair." },
        { 52000, 1, "And the arch comes down on all of them, Eternus. On everyone who lives because this war ended the way it did." },
        { 60000, 2, "On me. On my people. On the souls I freed and the ones I failed. You do not get to decide that they were worth less than the ones you mourn." },
        { 70000, 3, "I can feel the hour you have built, dragon. It isn't open. It's hungry." },
        { 76000, 0, "Then you will have to take it from me." },
    };
    constexpr uint32 FIGHT_AT = 80000;

    std::mutex runningLock;
    std::unordered_map<ObjectGuid, ObjectGuid> running;  // Timerunners whose last hour is on, and their Eternus

    bool OnTheLastHour(Player* player)
    {
        return player && player->GetQuestStatus(QUEST_LAST_HOUR) == QUEST_STATUS_INCOMPLETE;
    }

    // Whether [eternus] is still [player]'s (a logout ends theirs, and a new one replaces one gone).
    bool Theirs(ObjectGuid player, ObjectGuid eternus)
    {
        std::lock_guard<std::mutex> lock(runningLock);
        auto it = running.find(player);
        return it != running.end() && it->second == eternus;
    }

    void Finished(ObjectGuid player, ObjectGuid eternus)
    {
        std::lock_guard<std::mutex> lock(runningLock);
        auto it = running.find(player);
        if (it != running.end() && it->second == eternus)
            running.erase(it);
    }
}

class npc_remix_eternus_last_hour : public CreatureScript
{
public:
    npc_remix_eternus_last_hour() : CreatureScript("npc_remix_eternus_last_hour") { }

    struct npc_remix_eternus_last_hourAI : public ScriptedAI
    {
        npc_remix_eternus_last_hourAI(Creature* creature) : ScriptedAI(creature) { }

        EventMap events;
        ObjectGuid timerunner;
        ObjectGuid allies[3];
        GuidSet loyalists;
        bool wave70 = false, wave40 = false, said50 = false, said30 = false, retreating = false, begun = false;
        uint32 introLine = 0;

        void SetGUID(ObjectGuid const& guid, int32 id) override
        {
            if (id == 0)
                timerunner = guid;
            else if (id >= int32(DATA_ALLY_MORATARI) && id <= int32(DATA_ALLY_ALLERIA))
                allies[id - DATA_ALLY_MORATARI] = guid;
        }

        Creature* Speaker(uint8 who)
        {
            return who == 0 ? me : ObjectAccessor::GetCreature(*me, allies[who - 1]);
        }

        void Say(uint8 who, char const* text)
        {
            if (Creature* speaker = Speaker(who))
                speaker->Say(text, LANG_UNIVERSAL);
        }

        // (once: an evade later on, the Timerunner dead, leaves the watch to end it)
        void Reset() override
        {
            if (!begun)
            {
                // until she has said her piece
                me->SetReactState(REACT_PASSIVE);
                me->SetImmuneToAll(true);
                events.ScheduleEvent(EVENT_INTRO, Milliseconds(INTRO[0].at));
                events.ScheduleEvent(EVENT_FIGHT, Milliseconds(FIGHT_AT));
                events.ScheduleEvent(EVENT_WATCH, 5s);
                begun = true;
            }
        }

        Player* Timerunner()
        {
            return ObjectAccessor::GetPlayer(*me, timerunner);
        }

        void Loyalists(uint32 count)
        {
            Player* player = Timerunner();
            for (uint32 i = 0; i < count; ++i)
            {
                float angle = me->GetOrientation() + float(i) * 2.0f * float(M_PI) / float(count);
                Position at = me->GetNearPosition(6.0f, angle - me->GetOrientation());
                uint32 entry = (i % 2) ? NPC_LAST_EXECUTIONER : NPC_LAST_CHRONOMANCER;
                if (Creature* loyalist = me->SummonCreature(entry, at, TEMPSUMMON_TIMED_OR_CORPSE_DESPAWN, 600000))
                {
                    loyalist->CastSpell(loyalist, SPELL_TELEPORT_VISUAL, true);
                    loyalists.insert(loyalist->GetGUID());
                    if (player)
                        loyalist->AI()->AttackStart(player);
                }
            }
        }

        void DamageTaken(Unit* /*attacker*/, uint32& damage, DamageEffectType /*type*/, SpellSchoolMask /*school*/) override
        {
            if (retreating)
            {
                damage = 0;
                return;
            }
            // She is not killed: a tenth of her strength left, and she goes.
            if (me->HealthBelowPctDamaged(10, damage))
            {
                damage = me->GetHealth() > me->CountPctFromMaxHealth(10) ? me->GetHealth() - me->CountPctFromMaxHealth(10) : 0;
                Retreat();
                return;
            }
            if (!wave70 && me->HealthBelowPctDamaged(70, damage))
            {
                wave70 = true;
                DoCastAOE(SPELL_TIME_STOP);
                Loyalists(3);
            }
            if (!said50 && me->HealthBelowPctDamaged(50, damage))
            {
                said50 = true;
                Say(0, "Do you know how many died on the beaches of the Borean Tundra? I do. I counted them. I counted every one.");
                // (she knows the Timerunner better than the Timerunner knows her, and it shows)
                if (Creature* sylvanas = Speaker(2))
                    if (Player* player = Timerunner())
                    {
                        std::string line = "Stay behind me, " + player->GetName() + ". Like old times. ...Like old times for one of us, at least.";
                        sylvanas->m_Events.AddEventAtOffset([sylvanas, line]() { sylvanas->Say(line, LANG_UNIVERSAL); }, 6s);
                    }
                if (Creature* alleria = Speaker(3))
                    alleria->m_Events.AddEventAtOffset([alleria]() { alleria->Say("Between the two of us, then. Where we can both see you.", LANG_UNIVERSAL); }, 12s);
            }
            if (!wave40 && me->HealthBelowPctDamaged(40, damage))
            {
                wave40 = true;
                DoCastAOE(SPELL_TIME_STOP);
                Loyalists(4);
            }
            if (!said30 && me->HealthBelowPctDamaged(30, damage))
            {
                said30 = true;
                Say(0, "Windrunner! I would have given you Quel'Thalas! Not a ruin. Not a grave. Your home, with your people in it!");
                if (Creature* sylvanas = Speaker(2))
                    sylvanas->m_Events.AddEventAtOffset([sylvanas]() { sylvanas->Say("I know. That is why I came.", LANG_UNIVERSAL); }, 5s);
            }
        }

        void Retreat()
        {
            retreating = true;
            events.Reset();
            me->SetReactState(REACT_PASSIVE);
            me->AttackStop();
            me->SetImmuneToAll(true);
            me->CombatStop(true);
            me->GetMotionMaster()->Clear();
            me->GetMotionMaster()->MoveIdle();
            // her loyalists go with her
            for (ObjectGuid const& guid : loyalists)
                if (Creature* loyalist = ObjectAccessor::GetCreature(*me, guid))
                {
                    loyalist->CastSpell(loyalist, SPELL_TELEPORT_VISUAL, true);
                    loyalist->DespawnOrUnsummon(1500ms);
                }
            for (ObjectGuid const& guid : allies)
                if (Creature* ally = ObjectAccessor::GetCreature(*me, guid))
                {
                    ally->AttackStop();
                    ally->CombatStop(true);
                    ally->SetReactState(REACT_PASSIVE);
                }
            Say(0, "...Enough.");
            events.ScheduleEvent(EVENT_RETREAT, 4s);
        }

        void UpdateAI(uint32 diff) override
        {
            events.Update(diff);
            while (uint32 event = events.ExecuteEvent())
            {
                switch (event)
                {
                    case EVENT_INTRO:
                    {
                        Line const& line = INTRO[introLine];
                        if (Player* player = Timerunner())
                            if (line.who == 0)
                                me->SetFacingToObject(player);
                        Say(line.who, line.text);
                        if (++introLine < std::size(INTRO))
                            events.ScheduleEvent(EVENT_INTRO, Milliseconds(INTRO[introLine].at - INTRO[introLine - 1].at));
                        break;
                    }
                    case EVENT_FIGHT:
                    {
                        me->SetImmuneToAll(false);
                        me->SetReactState(REACT_AGGRESSIVE);
                        Player* player = Timerunner();
                        if (player)
                            AttackStart(player);
                        for (ObjectGuid const& guid : allies)
                            if (Creature* ally = ObjectAccessor::GetCreature(*me, guid))
                                ally->AI()->AttackStart(me);
                        Loyalists(4);
                        events.ScheduleEvent(EVENT_WOUNDING_STRIKE, 8s);
                        events.ScheduleEvent(EVENT_CURSE, 12s);
                        events.ScheduleEvent(EVENT_TIME_WARP, 25s);
                        events.ScheduleEvent(EVENT_SAND_BREATH, 18s);
                        break;
                    }
                    case EVENT_WOUNDING_STRIKE:
                        DoCastVictim(SPELL_WOUNDING_STRIKE);
                        events.ScheduleEvent(EVENT_WOUNDING_STRIKE, 10s, 14s);
                        break;
                    case EVENT_CURSE:
                        if (Unit* target = SelectTarget(SelectTargetMethod::Random, 0, 40.0f, true))
                            DoCast(target, SPELL_CURSE_OF_EXERTION);
                        events.ScheduleEvent(EVENT_CURSE, 15s, 20s);
                        break;
                    case EVENT_TIME_WARP:
                        DoCastAOE(SPELL_TIME_WARP);
                        events.ScheduleEvent(EVENT_TIME_WARP, 25s, 30s);
                        break;
                    case EVENT_SAND_BREATH:
                        DoCastVictim(SPELL_SAND_BREATH);
                        events.ScheduleEvent(EVENT_SAND_BREATH, 18s, 24s);
                        break;
                    case EVENT_RETREAT:
                    {
                        Say(0, "Not today, then. The river is long, Timerunner, and I am very patient. One day I will find a grave that history does not need.");
                        // the quest's credit for every Timerunner here who is on it
                        me->GetMap()->DoForAllPlayers([this](Player* player)
                        {
                            if (!IsBot(player) && player->GetDistance(me) < 80.0f && OnTheLastHour(player))
                                player->KilledMonsterCredit(NPC_LAST_HOUR_CREDIT);
                        });
                        events.ScheduleEvent(EVENT_GONE, 9s);
                        break;
                    }
                    case EVENT_GONE:
                    {
                        me->CastSpell(me, SPELL_TELEPORT_VISUAL, true);
                        // the three say theirs, and go
                        char const* last[] = {
                            "She's gone. Not dead. Eternus has never been any good at dying.",
                            "The doors are open, Timerunner. Go and end it.",
                            "We will be waiting at the Bazaar. All of us. Come back to us. I will not say it twice.",
                        };
                        for (uint8 i = 0; i < 3; ++i)
                            if (Creature* ally = ObjectAccessor::GetCreature(*me, allies[i]))
                            {
                                char const* text = last[i];
                                ally->m_Events.AddEventAtOffset([ally, text]() { ally->Say(text, LANG_UNIVERSAL); }, Milliseconds(3000 + 6000 * i));
                                ally->m_Events.AddEventAtOffset([ally]()
                                {
                                    ally->CastSpell(ally, SPELL_TELEPORT_VISUAL, true);
                                    ally->DespawnOrUnsummon(1500ms);
                                }, Milliseconds(22000 + 800 * i));
                            }
                        if (Player* player = Timerunner())
                        {
                            ObjectGuid guid = player->GetGUID();
                            player->m_Events.AddEventAtOffset([guid]()
                            {
                                if (Player* p = ObjectAccessor::FindPlayer(guid))
                                    p->UpdateObjectVisibility();
                            }, 25s);
                        }
                        Finished(timerunner, me->GetGUID());
                        me->DespawnOrUnsummon(1200ms);
                        break;
                    }
                    case EVENT_WATCH:
                    {
                        // The Timerunner died, went or logged out: it's over, to be begun again.
                        Player* player = Timerunner();
                        if (!player || !player->IsInWorld() || !player->IsAlive() || player->GetDistance(me) > 100.0f || !OnTheLastHour(player)
                            || !Theirs(timerunner, me->GetGUID()))
                        {
                            for (ObjectGuid const& guid : loyalists)
                                if (Creature* loyalist = ObjectAccessor::GetCreature(*me, guid))
                                    loyalist->DespawnOrUnsummon();
                            for (ObjectGuid const& guid : allies)
                                if (Creature* ally = ObjectAccessor::GetCreature(*me, guid))
                                    ally->DespawnOrUnsummon();
                            Finished(timerunner, me->GetGUID());
                            me->DespawnOrUnsummon();
                            return;
                        }
                        events.ScheduleEvent(EVENT_WATCH, 3s);
                        break;
                    }
                }
            }
            if (retreating || !UpdateVictim())
                return;
            DoMeleeAttackIfReady();
        }

        void EnterEvadeMode(EvadeReason why) override
        {
            // (she doesn't go home to her spawn: she has none; the watch ends it if the Timerunner is gone)
            if (retreating)
                return;
            ScriptedAI::EnterEvadeMode(why);
        }
    };

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_remix_eternus_last_hourAI(creature);
    }
};

// Moratari, Sylvanas and Alleria at the last hour: on the Timerunner's side, never falling, each
// with a spell of their own.
class npc_remix_last_hour_ally : public CreatureScript
{
public:
    npc_remix_last_hour_ally() : CreatureScript("npc_remix_last_hour_ally") { }

    struct npc_remix_last_hour_allyAI : public ScriptedAI
    {
        npc_remix_last_hour_allyAI(Creature* creature) : ScriptedAI(creature) { }

        uint32 castTimer = 3000;

        uint32 Spell() const
        {
            switch (me->GetEntry())
            {
                case NPC_ALLY_MORATARI: return SPELL_ARCANE_BOLT;
                case NPC_ALLY_SYLVANAS: return SPELL_BLACK_ARROW;
                default:                return SPELL_VOID_BOLT;
            }
        }

        void DamageTaken(Unit* /*attacker*/, uint32& damage, DamageEffectType /*type*/, SpellSchoolMask /*school*/) override
        {
            if (damage >= me->GetHealth())
                damage = me->GetHealth() - 1;
        }

        void UpdateAI(uint32 diff) override
        {
            if (!UpdateVictim())
            {
                // the loyalists nearby, Eternus last
                if (me->GetReactState() != REACT_PASSIVE)
                    for (uint32 entry : { NPC_LAST_CHRONOMANCER, NPC_LAST_EXECUTIONER, NPC_LAST_ETERNUS })
                        if (Creature* foe = me->FindNearestCreature(entry, 40.0f))
                            if (!foe->IsImmuneToAll())
                            {
                                AttackStart(foe);
                                break;
                            }
                return;
            }
            if (castTimer <= diff)
            {
                if (!me->HasUnitState(UNIT_STATE_CASTING))
                    DoCastVictim(Spell());
                castTimer = urand(3500, 6000);
            }
            else
                castTimer -= diff;
            DoMeleeAttackIfReady();
        }
    };

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_remix_last_hour_allyAI(creature);
    }
};

namespace WrathRemix
{
    bool BeginLastHour(Player* player)
    {
        if (!Active() || !OnTheLastHour(player) || IsBot(player))
            return false;
        {
            // (theirs is on while their Eternus is here and alive, as her watch has it; one gone with
            // her grid, dead or left far off is over, and her watch, finding she isn't theirs, ends it)
            std::lock_guard<std::mutex> lock(runningLock);
            auto it = running.find(player->GetGUID());
            if (it != running.end())
            {
                Creature* eternus = ObjectAccessor::GetCreature(*player, it->second);
                if (eternus && eternus->IsInWorld() && eternus->IsAlive() && eternus->GetDistance(player) <= 100.0f)
                    return false;
                running.erase(it);
            }
        }
        Record(player, "last hour", NPC_LAST_ETERNUS, 0);
        // Eternus a dozen yards before the Timerunner, facing them; the three at their side.
        float o = player->GetOrientation();
        Position at = player->GetNearPosition(12.0f, 0.0f);
        Creature* eternus = player->SummonCreature(NPC_LAST_ETERNUS, at.GetPositionX(), at.GetPositionY(), at.GetPositionZ(),
            Position::NormalizeOrientation(o + float(M_PI)), TEMPSUMMON_MANUAL_DESPAWN);
        if (!eternus)
            return false;
        {
            std::lock_guard<std::mutex> lock(runningLock);
            running[player->GetGUID()] = eternus->GetGUID();
        }
        eternus->CastSpell(eternus, 51347, true);
        eternus->AI()->SetGUID(player->GetGUID(), 0);
        uint32 allies[] = { NPC_ALLY_MORATARI, NPC_ALLY_SYLVANAS, NPC_ALLY_ALLERIA };
        float sides[] = { 2.2f, -2.2f, 1.6f };
        float back[] = { 0.0f, 0.0f, -2.5f };
        for (uint8 i = 0; i < 3; ++i)
        {
            Position spot = player->GetNearPosition(3.0f + back[i], sides[i]);
            if (Creature* ally = player->SummonCreature(allies[i], spot.GetPositionX(), spot.GetPositionY(), spot.GetPositionZ(), o, TEMPSUMMON_MANUAL_DESPAWN))
            {
                ally->SetFaction(player->GetFaction());
                ally->CastSpell(ally, 51347, true);
                eternus->AI()->SetGUID(ally->GetGUID(), int32(DATA_ALLY_MORATARI + i));
            }
        }
        return true;
    }
}

namespace
{
    // The last hour once the Timerunner is at the doors (a far journey can keep them on a loading
    // screen for a while: out of the world, their own events waiting), a check a second, [tries]
    // times.
    void BeginWhenThere(Player* player, uint32 map, float x, float y, uint32 tries)
    {
        if (!tries)
            return;
        ObjectGuid guid = player->GetGUID();
        player->m_Events.AddEventAtOffset([guid, map, x, y, tries]()
        {
            Player* p = ObjectAccessor::FindPlayer(guid);
            if (!p)
                return;
            if (p->IsInWorld() && !p->IsBeingTeleported() && p->GetMapId() == map && p->GetExactDist2d(x, y) < 40.0f)
                BeginLastHour(p);
            else
                BeginWhenThere(p, map, x, y, tries - 1);
        }, tries == 30 ? 2500ms : 1000ms);
    }
}

namespace WrathRemix
{
    // Back to the doors, to begin it again (the Moratari outside the Frozen Halls).
    void LastHourAgain(Player* player)
    {
        if (!OnTheLastHour(player))
            return;
        Departure const* doors = DepartureFor(QUEST_LAST_HOUR);
        if (!doors)
            return;
        JourneyFromTheDark(player, "Icecrown Citadel | The last hour", doors->map, doors->x, doors->y, 500, 2000);
        if (!player->TeleportTo(doors->map, doors->x, doors->y, doors->z, doors->o))
            LiftTheCurtain(player);
        BeginWhenThere(player, doors->map, doors->x, doors->y, 30);
    }
}

// A Timerunner's last hour ends as they log out (their Eternus, if her grid keeps her till they're
// back, sees it at her next look and goes), to be begun again as if they had died.
class RemixLastHourPlayer : public PlayerScript
{
public:
    RemixLastHourPlayer() : PlayerScript("RemixLastHourPlayer", { PLAYERHOOK_ON_LOGOUT }) { }

    void OnPlayerLogout(Player* player) override
    {
        if (!Active())
            return;
        std::lock_guard<std::mutex> lock(runningLock);
        running.erase(player->GetGUID());
    }
};

void AddRemixLastHourScripts()
{
    new npc_remix_eternus_last_hour();
    new npc_remix_last_hour_ally();
    new RemixLastHourPlayer();
}
