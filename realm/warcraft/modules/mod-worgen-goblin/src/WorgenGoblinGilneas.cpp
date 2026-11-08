// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * Gilneas's scripts: the Cataclysm Preservation Project's (github.com/The-Cataclysm-Preservation-
 * Project/TrinityCore, src/server/scripts/EasternKingdoms/Gilneas; part of the TrinityCore Project,
 * GPL-2.0 or later: see its AUTHORS), made AzerothCore's, under CPP's own names (the world keeps a
 * creature's script name when this file registers it: tools/zones/scripts.py).
 *
 * What changes on the way:
 *  - Cataclysm's ids are the realm's (WorgenGoblinZonesIds.h, written with the world's data): Id()
 *    for a creature, object or quest, SpellId() for a spell, Path() for a waypoint path, PhaseMask() for
 *    a phase, which here is a bit of the phase mask.
 *  - A smooth path (TrinityCore's MoveSmoothPath, which tells the script when it ends) is AzerothCore's
 *    spline path (MovePath), its end an event after the time it takes (MoveAlong).
 *  - A waypoint path (MovePath in TrinityCore) is AzerothCore's waypoints (MoveWaypoint), which tell
 *    the script of each point reached as TrinityCore's do.
 *  - Where CPP's code had a slip (the runts of the cathedral each given its first path), the one meant.
 */

#include "WorgenGoblinGilneas.h"
#include "WorgenGoblinZonesIds.h"
#include "CombatAI.h"
#include "Containers.h"
#include "GameObjectAI.h"
#include "MotionMaster.h"
#include "MoveSpline.h"
#include "ObjectAccessor.h"
#include "PassiveAI.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "TemporarySummon.h"
#include "Vehicle.h"
#include <iterator>

using namespace WorgenGoblinZones;

namespace WorgenGoblinGilneas
{
    // A smooth path through [count] places from where the creature stands; the time it takes.
    Milliseconds MoveAlong(Creature* me, Position const* path, uint32 count)
    {
        Movement::PointsArray points;
        points.emplace_back(me->GetPositionX(), me->GetPositionY(), me->GetPositionZ());
        float length = 0.0f;
        Position from = me->GetPosition();
        for (uint32 i = 0; i < count; ++i)
        {
            points.emplace_back(path[i].GetPositionX(), path[i].GetPositionY(), path[i].GetPositionZ());
            length += from.GetExactDist(&path[i]);
            from = path[i];
        }
        me->GetMotionMaster()->MoveSplinePath(&points);
        float speed = me->GetSpeed(MOVE_RUN);
        return Milliseconds(uint32(speed > 0.0f ? length / speed * IN_MILLISECONDS : 0) + 100);
    }

    // A creature put in a phase too (TrinityCore's PhasingHandler::AddPhase).
    void AddPhase(Creature* me, uint32 phase)
    {
        me->SetPhaseMask(me->GetPhaseMask() | PhaseMask(phase), true);
    }

    // The creatures attacking one, back to their places.
    void CallOffAttackers(Unit* me)
    {
        std::vector<Unit*> attackers(me->getAttackers().begin(), me->getAttackers().end());
        for (Unit* attacker : attackers)
            if (Creature* creature = attacker->ToCreature())
                if (creature->IsAIEnabled)
                    creature->AI()->EnterEvadeMode();
    }

/*######
## Quest 14098 - Evacuate the Merchant Square
######*/

enum FrightenedCitizen
{
    SAY_FRIGHTENED_CITIZEN_RESCUE   = 0,

    NPC_EVACUATION_STALKER_FIRST    = 35830,
    NPC_EVACUATION_STALKER_NEAR     = 35010,
    NPC_EVACUATION_STALKER_FAR      = 35011,

    POINT_STALKER_FIRST             = 1,
    POINT_STALKER_NEAR              = 2,
    POINT_STALKER_FAR               = 3,

    EVENT_TALK_FRIGHTENED           = 1,
    EVENT_MOVE_TO_NEAR_STALKER      = 2,
    EVENT_MOVE_TO_FAR_STALKER       = 3,
    EVENT_DESPAWN                   = 4
};

struct npc_frightened_citizen : public PassiveAI
{
    npc_frightened_citizen(Creature* creature) : PassiveAI(creature) { }

    void IsSummonedBy(WorldObject* /*summoner*/) override
    {
        if (Creature* stalkerNear = me->FindNearestCreature(Id(NPC_EVACUATION_STALKER_FIRST), 20.0f))
            me->GetMotionMaster()->MovePoint(POINT_STALKER_FIRST, stalkerNear->GetPosition(), FORCED_MOVEMENT_RUN);
    }

    void MovementInform(uint32 type, uint32 id) override
    {
        if (type != POINT_MOTION_TYPE)
            return;

        switch (id)
        {
            case POINT_STALKER_FIRST:
                _events.ScheduleEvent(EVENT_TALK_FRIGHTENED, 1s);
                break;
            case POINT_STALKER_NEAR:
                _events.ScheduleEvent(EVENT_MOVE_TO_FAR_STALKER, 1ms);
                break;
            case POINT_STALKER_FAR:
                _events.ScheduleEvent(EVENT_DESPAWN, 1ms);
                break;
            default:
                break;
        }
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_TALK_FRIGHTENED:
                    if (TempSummon* summon = me->ToTempSummon())
                    {
                        if (Player* player = summon->GetSummonerUnit() ? summon->GetSummonerUnit()->ToPlayer() : nullptr)
                        {
                            player->KilledMonsterCredit(Id(NPC_EVACUATION_STALKER_FIRST));
                            Talk(SAY_FRIGHTENED_CITIZEN_RESCUE, player);
                        }
                    }
                    _events.ScheduleEvent(EVENT_MOVE_TO_NEAR_STALKER, 2s);
                    break;
                case EVENT_MOVE_TO_NEAR_STALKER:
                    if (Creature* stalker = me->FindNearestCreature(Id(NPC_EVACUATION_STALKER_FAR), 50.0f))
                        me->GetMotionMaster()->MovePoint(POINT_STALKER_FAR, stalker->GetPosition(), FORCED_MOVEMENT_RUN);
                    else if (Creature* near = me->FindNearestCreature(Id(NPC_EVACUATION_STALKER_NEAR), 100.0f))
                        me->GetMotionMaster()->MovePoint(POINT_STALKER_NEAR, near->GetPosition(), FORCED_MOVEMENT_RUN);
                    break;
                case EVENT_MOVE_TO_FAR_STALKER:
                    if (Creature* stalker = me->FindNearestCreature(Id(NPC_EVACUATION_STALKER_FAR), 500.0f))
                        me->GetMotionMaster()->MovePoint(POINT_STALKER_FAR, stalker->GetPosition(), FORCED_MOVEMENT_RUN);
                    break;
                case EVENT_DESPAWN:
                    me->DespawnOrUnsummon();
                    break;
                default:
                    break;
            }
        }
    }
private:
    EventMap _events;
};

/*######
## Quest 14154 - By the Skin of his Teeth
######*/

enum WorgenRunt
{
    EVENT_JUMP_TO_PRISON            = 1,
    EVENT_AGGRO_PLAYER              = 2,
    EVENT_FORCE_DESPAWN             = 3,

    PHASE_ROOF                      = 1,
    PHASE_COMBAT                    = 2,

    WORGEN_ID_ROOF_1                = 0,
    WORGEN_ID_CATHEDRAL_1           = 7,

    NPC_WORGEN_RUNT_SPELL           = 35188,
};

static Position const RuntSpellSummonJumpPos = { -1671.915f, 1446.734f, 52.28712f };

// The runts' paths, by their id (DoAction): the house roof's seven, then the cathedral's eight.
struct RuntPath
{
    Position const* path;
    uint32 count;
};

static RuntPath const RuntPaths[] =
{
    { worgenRuntHousePath1, runtHousePathSize1 }, { worgenRuntHousePath2, runtHousePathSize2 },
    { worgenRuntHousePath3, runtHousePathSize3 }, { worgenRuntHousePath4, runtHousePathSize4 },
    { worgenRuntHousePath5, runtHousePathSize5 }, { worgenRuntHousePath6, runtHousePathSize6 },
    { worgenRuntHousePath7, runtHousePathSize7 },
    { worgenRuntCathedralPath1, runtCathedralPathSize1 }, { worgenRuntCathedralPath2, runtCathedralPathSize2 },
    { worgenRuntCathedralPath3, runtCathedralPathSize3 }, { worgenRuntCathedralPath4, runtCathedralPathSize4 },
    { worgenRuntCathedralPath5, runtCathedralPathSize5 }, { worgenRuntCathedralPath6, runtCathedralPathSize6 },
    { worgenRuntCathedralPath7, runtCathedralPathSize7 }, { worgenRuntCathedralPath8, runtCathedralPathSize8 },
};

struct npc_worgen_runt : public ScriptedAI
{
    npc_worgen_runt(Creature* creature) : ScriptedAI(creature), _worgenID(0) { }

    void JustEngagedWith(Unit* /*who*/) override
    {
        _events.SetPhase(PHASE_COMBAT);
    }

    void IsSummonedBy(WorldObject* summoner) override
    {
        me->setActive(true); // (a map of the Worgen's alone, and few of them)
        _events.SetPhase(PHASE_ROOF);
        _events.ScheduleEvent(EVENT_FORCE_DESPAWN, 70s, 0, PHASE_ROOF);
        _playerGuid = summoner->GetGUID();
        if (me->GetEntry() == Id(NPC_WORGEN_RUNT_SPELL))
            me->GetMotionMaster()->MoveJump(RuntSpellSummonJumpPos, 16.0f, 4.371286f);
    }

    void DoAction(int32 action) override
    {
        if (action < 0 || action >= int32(std::size(RuntPaths)))
            return;
        _worgenID = action;
        _events.ScheduleEvent(EVENT_JUMP_TO_PRISON, MoveAlong(me, RuntPaths[action].path, RuntPaths[action].count), 0, PHASE_ROOF);
    }

    void JustDied(Unit* /*killer*/) override
    {
        me->DespawnOrUnsummon(5s);
    }

    void UpdateAI(uint32 diff) override
    {
        if (!UpdateVictim() && !_events.IsInPhase(PHASE_ROOF))
            return;

        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_FORCE_DESPAWN:
                    me->DespawnOrUnsummon();
                    break;
                case EVENT_JUMP_TO_PRISON:
                    me->GetMotionMaster()->MoveJump(worgenRuntJumpPos[_worgenID], 16.0f, _worgenID < WORGEN_ID_CATHEDRAL_1 ? 19.2911f : frand(3.945607f, 4.852813f));
                    me->SetHomePosition(worgenRuntJumpPos[_worgenID]);
                    _events.ScheduleEvent(EVENT_AGGRO_PLAYER, 2s);
                    break;
                case EVENT_AGGRO_PLAYER:
                    if (Player* player = ObjectAccessor::GetPlayer(*me, _playerGuid))
                        if (me->IsInDist(player, 100.0f))
                            AttackStart(player);
                    break;
                default:
                    break;
            }
        }

        DoMeleeAttackIfReady();
    }
private:
    uint32 _worgenID;
    ObjectGuid _playerGuid;
    EventMap _events;
};

/*######
## Quest 14159 - The Rebel Lord's Arsenal
######*/

enum TheRebelLordsArsenal
{
    PHASE_ID_SUMMON         = 170,
    PHASE_ID_WOUND          = 171,
    NPC_LORNA_CROWLEY       = 35378,
    NPC_GENERIC_TRIGGER_LAB = 35374,

    SPELL_SHOOT_INSTAKILL   = 67593,
    SPELL_COSMETIC_ATTACK   = 42880,
    SPELL_PULL_TO           = 67357,

    EVENT_COSMETIC_ATTACK   = 1,
    EVENT_JUMP_TO_PLAYER,
    EVENT_SHOOT_JOSIAH
};

static Position const JosiahJumpPos = { -1796.63f, 1427.73f, 12.4624f };

struct npc_josiah_avery : public PassiveAI
{
    npc_josiah_avery(Creature* creature) : PassiveAI(creature) { }

    void IsSummonedBy(WorldObject* summoner) override
    {
        AddPhase(me, PHASE_ID_SUMMON);
        AddPhase(me, PHASE_ID_WOUND);
        _playerGuid = summoner->GetGUID();
        _events.ScheduleEvent(EVENT_COSMETIC_ATTACK, 500ms);
    }

    void JustDied(Unit* /*killer*/) override
    {
        me->DespawnOrUnsummon(5s);
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_COSMETIC_ATTACK:
                    if (Player* player = ObjectAccessor::GetPlayer(*me, _playerGuid))
                    {
                        DoCast(player, SpellId(SPELL_COSMETIC_ATTACK));
                        if (Creature* lorna = me->FindNearestCreature(Id(NPC_LORNA_CROWLEY), 30.0f, true))
                            if (Creature* labTrigger = lorna->FindNearestCreature(Id(NPC_GENERIC_TRIGGER_LAB), 5.0f, true))
                                labTrigger->CastSpell(player, SpellId(SPELL_PULL_TO));

                        _events.ScheduleEvent(EVENT_JUMP_TO_PLAYER, 1s);
                    }
                    break;
                case EVENT_JUMP_TO_PLAYER:
                    me->GetMotionMaster()->MoveJump(JosiahJumpPos, 10.0f, 14.18636f);
                    _events.ScheduleEvent(EVENT_SHOOT_JOSIAH, 500ms);
                    break;
                case EVENT_SHOOT_JOSIAH:
                    if (Creature* lorna = me->FindNearestCreature(Id(NPC_LORNA_CROWLEY), 30.0f, true))
                        lorna->CastSpell(me, SpellId(SPELL_SHOOT_INSTAKILL), true);
                    break;
                default:
                    break;
            }
        }
    }
private:
    ObjectGuid _playerGuid;
    EventMap _events;
};

/*######
## Quest 14293 - Save Krennan Aranas
######*/

static Position const GreymanesHorseJumpPos = { -1676.16f, 1346.19f, 15.1349f };

enum GreymanesHorse
{
    SAY_ANNOUNCE_RESCUE     = 0,
    SAY_RESCUED             = 0,
    SAY_TRAPPED             = 0,

    PATH_KRENNAN_TREE       = 0,
    PATH_KRENNAN_BACK       = 1,

    EVENT_START_PATH_1      = 1,
    EVENT_START_PATH_2,
    EVENT_JUMP_TO_KRENNAN,
    EVENT_ANNOUNCE_RESCUE,
    EVENT_DISMOUNT_PLAYER,

    NPC_RESCUED_KRENNAN     = 35907,
    NPC_TRAPPED_KRENNAN     = 35753,
};

struct npc_greymanes_horse : public VehicleAI
{
    npc_greymanes_horse(Creature* creature) : VehicleAI(creature) { }

    void PassengerBoarded(Unit* passenger, int8 /*seatId*/, bool apply) override
    {
        if (apply && passenger->IsPlayer())
        {
            me->SetControlled(true, UNIT_STATE_ROOT);
            _events.ScheduleEvent(EVENT_START_PATH_1, 1s);
        }
        else if (apply && passenger->GetEntry() == Id(NPC_RESCUED_KRENNAN))
            _events.ScheduleEvent(EVENT_START_PATH_2, 1s);
    }

    void UpdateAI(uint32 diff) override
    {
        VehicleAI::UpdateAI(diff);
        _events.Update(diff);

        if (me->HasUnitState(UNIT_STATE_CASTING))
            return;

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_START_PATH_1:
                    me->SetControlled(false, UNIT_STATE_ROOT);
                    _events.ScheduleEvent(EVENT_JUMP_TO_KRENNAN, MoveAlong(me, greymanesHorsePath1, pathSize1));
                    break;
                case EVENT_JUMP_TO_KRENNAN:
                    me->GetMotionMaster()->MoveJump(GreymanesHorseJumpPos, 16.0f, 14.00968f);
                    _events.ScheduleEvent(EVENT_ANNOUNCE_RESCUE, 2s);
                    break;
                case EVENT_ANNOUNCE_RESCUE:
                    me->SetControlled(true, UNIT_STATE_ROOT);
                    if (Unit* passenger = me->GetVehicleKit()->GetPassenger(0))
                    {
                        Talk(SAY_ANNOUNCE_RESCUE, passenger);
                        if (Creature* krennan = me->FindNearestCreature(Id(NPC_TRAPPED_KRENNAN), 30.0f, true))
                            krennan->AI()->Talk(SAY_TRAPPED, passenger);
                    }
                    break;
                case EVENT_START_PATH_2:
                    // (CPP roots the horse here, which its path would undo: it's let run)
                    me->SetControlled(false, UNIT_STATE_ROOT);
                    _events.ScheduleEvent(EVENT_DISMOUNT_PLAYER, MoveAlong(me, greymanesHorsePath2, pathSize2));
                    break;
                case EVENT_DISMOUNT_PLAYER:
                    if (Unit* passenger = me->GetVehicleKit()->GetPassenger(1))
                    {
                        if (Unit* player = me->GetVehicleKit()->GetPassenger(0))
                        {
                            if (Creature* krennan = passenger->ToCreature())
                            {
                                CallOffAttackers(me);
                                player->ExitVehicle();
                                krennan->AddUnitState(UNIT_STATE_ROOT);
                                krennan->ExitVehicle();
                                krennan->AI()->Talk(SAY_RESCUED, me);
                                krennan->DespawnOrUnsummon(7s);
                            }
                        }
                    }
                    break;
                default:
                    break;
            }
        }
    }
private:
    EventMap _events;
};

/*######
## Quest 14212 - Sacrifices
######*/

enum CrowleysHorse
{
    EVENT_JUMP_OVER_BARRICADES_1 = 1,
    EVENT_JUMP_OVER_BARRICADES_2,
    EVENT_MOVE_PATH_MAIN_1,
    EVENT_MOVE_PATH_MAIN_2,
    EVENT_CROWLEY_DISMOUNT,
    EVENT_MOVE_OFF_PATH,

    PATH_ID_CROWLEYS_HORSE_1    = 352310,
    PATH_ID_CROWLEYS_HORSE_2    = 352311,
    PATH_ID_CROWLEYS_HORSE_3    = 444280,

    NPC_CROWLEYS_HORSE_2        = 44428,
};

static Position const CrowleysHorseJumpPos = { -1714.762f, 1673.16f, 20.49182f };
static Position const CrowleysHorseJumpPos2 = { -1566.71f, 1708.04f, 20.4849f };

struct npc_crowleys_horse : public VehicleAI
{
    npc_crowleys_horse(Creature* creature) : VehicleAI(creature), _currentPath(0) { }

    void PassengerBoarded(Unit* passenger, int8 /*seatId*/, bool apply) override
    {
        if (!apply || !passenger->IsPlayer())
            return;
        me->SetControlled(true, UNIT_STATE_ROOT);
        _events.ScheduleEvent(me->GetEntry() != Id(NPC_CROWLEYS_HORSE_2) ? EVENT_JUMP_OVER_BARRICADES_1 : EVENT_MOVE_OFF_PATH, 2s);
    }

    void MovementInform(uint32 type, uint32 pointId) override
    {
        if (type != WAYPOINT_MOTION_TYPE)
            return;
        if (pointId == 14 && _currentPath == PATH_ID_CROWLEYS_HORSE_1)
            _events.ScheduleEvent(EVENT_JUMP_OVER_BARRICADES_2, 1s);
        else if ((pointId == 15 && _currentPath == PATH_ID_CROWLEYS_HORSE_2) || (pointId == 16 && _currentPath == PATH_ID_CROWLEYS_HORSE_3))
            _events.ScheduleEvent(EVENT_CROWLEY_DISMOUNT, 1ms);
    }

    void UpdateAI(uint32 diff) override
    {
        VehicleAI::UpdateAI(diff);
        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_JUMP_OVER_BARRICADES_1:
                    me->SetControlled(false, UNIT_STATE_ROOT);
                    me->GetMotionMaster()->MoveJump(CrowleysHorseJumpPos, 16.0f, 18.56182f);
                    _events.ScheduleEvent(EVENT_MOVE_PATH_MAIN_1, 2s);
                    break;
                case EVENT_MOVE_PATH_MAIN_1:
                    _currentPath = PATH_ID_CROWLEYS_HORSE_1;
                    me->GetMotionMaster()->MoveWaypoint(Path(PATH_ID_CROWLEYS_HORSE_1), false);
                    break;
                case EVENT_JUMP_OVER_BARRICADES_2:
                    me->GetMotionMaster()->MoveJump(CrowleysHorseJumpPos2, 16.0f, 18.56182f);
                    _events.ScheduleEvent(EVENT_MOVE_PATH_MAIN_2, 2s);
                    break;
                case EVENT_MOVE_PATH_MAIN_2:
                    _currentPath = PATH_ID_CROWLEYS_HORSE_2;
                    me->GetMotionMaster()->MoveWaypoint(Path(PATH_ID_CROWLEYS_HORSE_2), false);
                    break;
                case EVENT_CROWLEY_DISMOUNT:
                    CallOffAttackers(me);
                    me->RemoveAurasDueToSpell(VEHICLE_SPELL_RIDE_HARDCODED);
                    me->DespawnOrUnsummon(5s);
                    break;
                case EVENT_MOVE_OFF_PATH:
                    me->SetControlled(false, UNIT_STATE_ROOT);
                    _currentPath = PATH_ID_CROWLEYS_HORSE_3;
                    me->GetMotionMaster()->MoveWaypoint(Path(PATH_ID_CROWLEYS_HORSE_3), false);
                    break;
                default:
                    break;
            }
        }
    }
private:
    EventMap _events;
    uint32 _currentPath;
};

enum GilneanCrow
{
    SPELL_GILNEAN_CROW      = 93275,
    EVENT_APPLY_HOVER_BYTES = 1,
    EVENT_FLY_AWAY_1        = 2,

    POINT_NONE              = 0,
    POINT_CROW_FLIGHT       = 1
};

struct npc_gilnean_crow : public PassiveAI
{
    npc_gilnean_crow(Creature* creature) : PassiveAI(creature) { }

    void SpellHit(Unit* /*caster*/, SpellInfo const* spell) override
    {
        if (spell->Id == SpellId(SPELL_GILNEAN_CROW))
            _events.ScheduleEvent(EVENT_APPLY_HOVER_BYTES, 500ms);
    }

    void MovementInform(uint32 type, uint32 pointId) override
    {
        if (type == POINT_MOTION_TYPE && pointId == POINT_CROW_FLIGHT)
        {
            Position pos = me->GetRandomNearPosition(8.0f);
            pos.m_positionZ = me->GetPositionZ() + 10.0f;
            me->GetMotionMaster()->MovePoint(POINT_NONE, pos);
            me->DespawnOrUnsummon(14s);
        }
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_APPLY_HOVER_BYTES:
                    me->SetStandState(UNIT_STAND_STATE_SIT);
                    me->SetAnimTier(AnimTier::Submerged);
                    _events.ScheduleEvent(EVENT_FLY_AWAY_1, 1s);
                    break;
                case EVENT_FLY_AWAY_1:
                {
                    Position pos = me->GetRandomNearPosition(7.0f);
                    pos.m_positionZ = me->GetPositionZ() + 8.0f;
                    me->GetMotionMaster()->MovePoint(POINT_CROW_FLIGHT, pos);
                    break;
                }
                default:
                    break;
            }
        }
    }
private:
    EventMap _events;
};

/*######
## Chapter 2: the Forsaken's invasion
######*/

enum GilneasInvasionCamera
{
    CINEMATIC_FORSAKEN_INVASION = 168
};

// (TrinityCore's OnReportUse: AzerothCore's GossipHello with reportUse)
struct go_gilneas_invasion_camera : public GameObjectAI
{
    go_gilneas_invasion_camera(GameObject* go) : GameObjectAI(go) { }

    bool GossipHello(Player* player, bool reportUse) override
    {
        if (!reportUse)
            return false;
        if (uint32 cinematic = Cinematic(CINEMATIC_FORSAKEN_INVASION))
            player->SendCinematicStart(cinematic);
        return true;
    }
};

enum HorridAbomination
{
    SPELL_KEG_PLACED                    = 68555,
    SPELL_ABOMINATION_KILL_ME           = 68558,
    SPELL_RANDOM_CIRCUMFERENCE_POISON   = 42266,
    SPELL_RANDOM_CIRCUMFERENCE_BONE     = 42267,
    SPELL_RANDOM_CIRCUMFERENCE_BONE_2   = 42274,
    SPELL_HORRID_ABOMINATION_EXPLOSION  = 68560,
    SPELL_RESTITCHING                   = 68864,

    NPC_HORRID_ABOMINATION_CREDIT       = 36233,

    SAY_KEG_PLACED                      = 0,
    EVENT_ABOMINATION_KILL_ME           = 1,

    // Prince Liam Greymane
    SPELL_SHOOT                         = 68559
};

struct npc_gilneas_horrid_abomination : public ScriptedAI
{
    npc_gilneas_horrid_abomination(Creature* creature) : ScriptedAI(creature)
    {
        Initialize();
    }

    void Initialize()
    {
        _playerGUID = ObjectGuid::Empty;
        _allowEvents = false;
    }

    void Reset() override
    {
        Initialize();
        me->GetMotionMaster()->MoveRandom(6.0f);
    }

    void SpellHit(Unit* caster, SpellInfo const* spell) override
    {
        if (spell->Id == SpellId(SPELL_KEG_PLACED))
        {
            Talk(SAY_KEG_PLACED);
            me->AttackStop();
            me->SetReactState(REACT_PASSIVE);
            me->GetMotionMaster()->Initialize();
            me->StopMoving();
            _playerGUID = caster->GetGUID();
            _allowEvents = true;
            _events.ScheduleEvent(EVENT_ABOMINATION_KILL_ME, 2s);
        }
        else if (spell->Id == SpellId(SPELL_SHOOT))
        {
            if (Player* player = ObjectAccessor::GetPlayer(*me, _playerGUID))
                player->KilledMonsterCredit(Id(NPC_HORRID_ABOMINATION_CREDIT));

            me->RemoveAurasDueToSpell(SpellId(SPELL_KEG_PLACED));

            for (uint8 i = 0; i < 11; i++)
                DoCastSelf(SpellId(SPELL_RANDOM_CIRCUMFERENCE_POISON), true);
            for (uint8 i = 0; i < 6; i++)
                DoCastSelf(SpellId(SPELL_RANDOM_CIRCUMFERENCE_BONE), true);
            for (uint8 i = 0; i < 4; i++)
                DoCastSelf(SpellId(SPELL_RANDOM_CIRCUMFERENCE_BONE_2), true);

            DoCastSelf(SpellId(SPELL_HORRID_ABOMINATION_EXPLOSION), true);
            me->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
            me->DespawnOrUnsummon(5s);
        }
    }

    void DamageTaken(Unit* /*attacker*/, uint32& damage, DamageEffectType /*type*/, SpellSchoolMask /*school*/) override
    {
        if (damage >= me->GetHealth())
        {
            damage = 0;
            if (!me->HasUnitState(UNIT_STATE_CASTING) && !me->HasAura(SpellId(SPELL_RESTITCHING)))
                DoCastSelf(SpellId(SPELL_RESTITCHING));
        }
    }

    void UpdateAI(uint32 diff) override
    {
        if (!UpdateVictim() && !_allowEvents)
            return;

        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
            if (eventId == EVENT_ABOMINATION_KILL_ME)
                DoCastAOE(SpellId(SPELL_ABOMINATION_KILL_ME), true);

        DoMeleeAttackIfReady();
    }

private:
    EventMap _events;
    ObjectGuid _playerGUID;
    bool _allowEvents;
};

enum SaveTheChildren
{
    SPELL_GILNEAS_QUEST_SAVE_JAMES      = 68596,
    SPELL_GILNEAS_QUEST_SAVE_CYNTHIA    = 68597,
    SPELL_GILNEAS_QUEST_SAVE_ASHLEY     = 68598,

    // (what the player says to each: the spells' own numbers)
    BROADCAST_SAVE_JAMES                = 36328,
    BROADCAST_SAVE_CYNTHIA              = 36329,
    BROADCAST_SAVE_ASHLEY               = 36331,

    NPC_CYNTHIA                         = 36287,
    NPC_ASHLEY                          = 36288,
    NPC_JAMES                           = 36289,

    SAY_CHILD_RESCUED                   = 0,
    EVENT_TALK_RESCUED                  = 1,
    EVENT_RUN_TO_BASEMENT               = 2,
    EVENT_CRY                           = 3,

    POINT_BASEMENT_1                    = 1,
    POINT_BASEMENT_2                    = 2,
};

static Position const JamesEscapePos = { -1913.021f, 2558.333f, 1.511007f };

static Position const AshleyEscapePos[] =
{
    { -1923.283f, 2552.308f, 12.73581f }, // Ashley Point 1
    { -1920.023f, 2558.055f, 7.076692f }  // Ashley Point 2
};

static Position const CynthiaEscapePos[] =
{
    { -1969.23f,  2517.465f, 2.580818f }, // Cynthia Point 1
    { -1947.472f, 2515.521f, 2.318746f }, // Cynthia Point 2
    { -1926.536f, 2519.312f, 2.246772f }  // Cynthia Point 3
};

class spell_gilneas_quest_save_the_children : public SpellScript
{
    PrepareSpellScript(spell_gilneas_quest_save_the_children);

    void HandleDummy(SpellEffIndex effIndex)
    {
        Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr;
        Unit* target = GetHitUnit();
        if (!player || !target)
            return;
        // (the spell's number is Cataclysm's text: the realm's, here)
        player->Talk(Id(uint32(GetSpellInfo()->Effects[effIndex].BasePoints)), CHAT_MSG_SAY, 0.0f, target);
        player->KilledMonsterCredit(target->GetEntry());
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_gilneas_quest_save_the_children::HandleDummy,
            m_scriptSpellId == SpellId(SPELL_GILNEAS_QUEST_SAVE_JAMES) ? EFFECT_0 : EFFECT_1, SPELL_EFFECT_DUMMY);
    }
};

struct npc_gilneas_save_the_children : public ScriptedAI
{
    npc_gilneas_save_the_children(Creature* creature) : ScriptedAI(creature) { }

    void Reset() override
    {
        _playerGUID = ObjectGuid::Empty;
        if (me->GetEntry() == Id(NPC_CYNTHIA))
            _events.ScheduleEvent(EVENT_CRY, 1s);
    }

    void SpellHit(Unit* caster, SpellInfo const* spell) override
    {
        if (spell->Id == SpellId(SPELL_GILNEAS_QUEST_SAVE_JAMES) || spell->Id == SpellId(SPELL_GILNEAS_QUEST_SAVE_CYNTHIA)
            || spell->Id == SpellId(SPELL_GILNEAS_QUEST_SAVE_ASHLEY))
        {
            me->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
            _playerGUID = caster->GetGUID();
            _events.ScheduleEvent(EVENT_TALK_RESCUED, 2500ms);
            _events.CancelEvent(EVENT_CRY);
        }
    }

    void MovementInform(uint32 type, uint32 id) override
    {
        if (type != POINT_MOTION_TYPE && type != EFFECT_MOTION_TYPE)
            return;

        switch (id)
        {
            case POINT_BASEMENT_1:
                if (me->GetEntry() == Id(NPC_ASHLEY))
                    me->GetMotionMaster()->MovePoint(0, AshleyEscapePos[1], FORCED_MOVEMENT_RUN);
                else
                    me->GetMotionMaster()->MovePoint(POINT_BASEMENT_2, CynthiaEscapePos[1], FORCED_MOVEMENT_RUN);
                break;
            case POINT_BASEMENT_2:
                me->GetMotionMaster()->MovePoint(0, CynthiaEscapePos[2], FORCED_MOVEMENT_RUN);
                break;
            default:
                break;
        }
    }

    void UpdateAI(uint32 diff) override
    {
        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_TALK_RESCUED:
                    Talk(SAY_CHILD_RESCUED, ObjectAccessor::GetPlayer(*me, _playerGUID));
                    _events.ScheduleEvent(EVENT_RUN_TO_BASEMENT, me->GetEntry() == Id(NPC_JAMES) ? 3600ms : 2300ms);
                    break;
                case EVENT_RUN_TO_BASEMENT:
                    if (me->GetEntry() == Id(NPC_JAMES))
                    {
                        me->GetMotionMaster()->MovePoint(0, JamesEscapePos, FORCED_MOVEMENT_RUN);
                        me->DespawnOrUnsummon(5200ms);
                    }
                    else if (me->GetEntry() == Id(NPC_ASHLEY))
                    {
                        me->GetMotionMaster()->MovePoint(POINT_BASEMENT_1, AshleyEscapePos[0], FORCED_MOVEMENT_RUN);
                        me->DespawnOrUnsummon(3800ms);
                    }
                    else if (me->GetEntry() == Id(NPC_CYNTHIA))
                    {
                        me->GetMotionMaster()->MovePoint(POINT_BASEMENT_1, CynthiaEscapePos[0], FORCED_MOVEMENT_RUN);
                        me->DespawnOrUnsummon(8500ms);
                    }
                    break;
                case EVENT_CRY:
                    me->HandleEmoteCommand(EMOTE_ONESHOT_CRY);
                    _events.Repeat(1s, 1500ms);
                    break;
                default:
                    break;
            }
        }
    }

private:
    EventMap _events;
    ObjectGuid _playerGUID;
};

enum ForsakenCatapult
{
    NPC_FORSAKEN_MACHINIST  = 36292,

    SPELL_FIERY_BOULDER     = 68591,
    SPELL_LAUNCH_INTERNAL   = 96114,
    SPELL_LAUNCH_INTERNAL_2 = 96185,
    SPELL_LAUNCH            = 66251,

    EVENT_FIERY_BOULDER     = 1,
    EVENT_CHECK_AREA        = 2,

    SEAT_0                  = 0,

    SAY_WARN_OUT_OF_AREA    = 0,

    AREA_ID_DUSKMIST_SHORE  = 5720  // (the areas keep Cataclysm's ids: tools/zones/build_tables.py)
};

struct npc_gilneas_forsaken_catapult : public VehicleAI
{
    npc_gilneas_forsaken_catapult(Creature* creature) : VehicleAI(creature), _preparedDespawn(false) { }

    void Reset() override
    {
        _preparedDespawn = false;
        _events.ScheduleEvent(EVENT_FIERY_BOULDER, 1ms, 7s);
    }

    void PassengerBoarded(Unit* passenger, int8 /*seatId*/, bool apply) override
    {
        if (!passenger)
            return;

        if (passenger->GetEntry() == Id(NPC_FORSAKEN_MACHINIST))
        {
            if (apply)
            {
                me->SetUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
                passenger->RemoveUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
                if (Creature* creature = passenger->ToCreature())
                    creature->SetReactState(REACT_PASSIVE);
            }
            else
            {
                me->RemoveUnitFlag(UNIT_FLAG_NOT_SELECTABLE);
                me->SetFaction(FACTION_FRIENDLY);
                _events.CancelEvent(EVENT_FIERY_BOULDER);
            }
        }
        else if (passenger->IsPlayer() && !apply)
            me->DespawnOrUnsummon(9s);
        else if (passenger->IsPlayer() && apply)
            _events.ScheduleEvent(EVENT_CHECK_AREA, 1ms);
    }

    void SpellHit(Unit* /*caster*/, SpellInfo const* spell) override
    {
        if (spell->Id == SpellId(SPELL_LAUNCH_INTERNAL))
            DoCastSelf(SpellId(SPELL_LAUNCH_INTERNAL_2), true);
    }

    void SetTargetDestination(Position pos)
    {
        _targetPos = pos;
    }

    void SpellHitTarget(Unit* target, SpellInfo const* spell) override
    {
        if (target && spell->Id == SpellId(SPELL_LAUNCH) && target->GetVehicleCreatureBase())
        {
            Position pos = target->GetPosition();
            pos.m_positionZ += 6.0f;
            target->ExitVehicle(&pos);
            target->GetMotionMaster()->MoveJump(_targetPos, 58.62504f, 12.75955f);
        }
    }

    void UpdateAI(uint32 diff) override
    {
        VehicleAI::UpdateAI(diff);
        _events.Update(diff);

        while (uint32 eventId = _events.ExecuteEvent())
        {
            switch (eventId)
            {
                case EVENT_FIERY_BOULDER:
                    DoCastAOE(SpellId(SPELL_FIERY_BOULDER));
                    _events.Repeat(7s, 8s);
                    break;
                case EVENT_CHECK_AREA:
                    if (me->GetAreaId() != AREA_ID_DUSKMIST_SHORE)
                    {
                        if (!_preparedDespawn)
                        {
                            if (Vehicle* vehicle = me->GetVehicleKit())
                                if (Unit* passenger = vehicle->GetPassenger(SEAT_0))
                                    Talk(SAY_WARN_OUT_OF_AREA, passenger);
                            _preparedDespawn = true;
                        }
                        else
                            me->DespawnOrUnsummon();
                        _events.Repeat(10s);
                    }
                    else
                    {
                        _preparedDespawn = false;
                        _events.Repeat(2s);
                    }
                    break;
                default:
                    break;
            }
        }
    }
private:
    EventMap _events;
    Position _targetPos;
    bool _preparedDespawn;
};

class spell_gilneas_launch : public SpellScript
{
    PrepareSpellScript(spell_gilneas_launch);

    void TransferDestination(SpellEffIndex /*effIndex*/)
    {
        if (Creature* creature = GetCaster() ? GetCaster()->ToCreature() : nullptr)
            if (creature->IsAIEnabled && GetExplTargetDest())
                if (auto* ai = CAST_AI(npc_gilneas_forsaken_catapult, creature->AI()))
                    ai->SetTargetDestination(GetExplTargetDest()->GetPosition());
    }

    void Register() override
    {
        OnEffectLaunch += SpellEffectFn(spell_gilneas_launch::TransferDestination, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

class spell_gilneas_fiery_boulder : public SpellScript
{
    PrepareSpellScript(spell_gilneas_fiery_boulder);

    void FilterTargets(std::list<WorldObject*>& targets)
    {
        Unit* caster = GetCaster();
        targets.remove_if([caster](WorldObject* object)
        {
            Unit* target = object->ToUnit();
            return target && !caster->isInFront(target, float(M_PI * 0.3f));
        });
        if (!targets.empty())
            Acore::Containers::RandomResize(targets, 1);
    }

    void Register() override
    {
        OnObjectAreaTargetSelect += SpellObjectAreaTargetSelectFn(spell_gilneas_fiery_boulder::FilterTargets, EFFECT_0, TARGET_UNIT_SRC_AREA_ENTRY);
    }
};

enum LeaderOfThePack
{
    NPC_ATTACK_MASTIFF = 36405
};

static Position const AttackMastiffSummonPositions[] =
{
    { -1944.483f, 2656.656f, 1.051441f,  1.691914f  },
    { -1956.602f, 2649.942f, 1.374257f,  1.441419f  },
    { -1973.627f, 2654.836f, -0.6995407f, 1.098437f },
    { -1983.201f, 2662.242f, -1.66652f,  0.8627869f },
    { -1994.557f, 2672.134f, -2.303949f, 0.5766099f },
    { -1949.314f, 2642.024f, 1.299083f,  1.580745f  },
    { -1972.606f, 2639.383f, 1.211673f,  1.217789f  },
    { -1997.009f, 2650.811f, -1.030188f, 0.8184887f },
    { -2006.259f, 2663.115f, -2.00431f,  0.5941383f },
    { -1945.504f, 2653.386f, 1.177739f,  1.675516f  }
};

class spell_gilneas_call_attack_mastiff : public SpellScript
{
    PrepareSpellScript(spell_gilneas_call_attack_mastiff);

    void HandleHit(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        if (!caster)
            return;
        for (Position const& pos : AttackMastiffSummonPositions)
            if (Creature* mastiff = caster->SummonCreature(Id(NPC_ATTACK_MASTIFF), pos, TEMPSUMMON_TIMED_DESPAWN, 60000))
                if (GetHitUnit())
                    mastiff->AI()->AttackStart(GetHitUnit());
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_gilneas_call_attack_mastiff::HandleHit, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

class spell_gilneas_forcecast_cataclysm_1 : public SpellScript
{
    PrepareSpellScript(spell_gilneas_forcecast_cataclysm_1);

    void HandleForcecast(SpellEffIndex effIndex)
    {
        PreventHitDefaultEffect(effIndex);
        if (Unit* caster = GetCaster())
            caster->CastSpell(caster, GetSpellInfo()->Effects[effIndex].TriggerSpell, true);
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_gilneas_forcecast_cataclysm_1::HandleForcecast, EFFECT_0, SPELL_EFFECT_FORCE_CAST);
    }
};

class spell_gilneas_worgen_intro_completion : public SpellScript
{
    PrepareSpellScript(spell_gilneas_worgen_intro_completion);

    // (only the caster's own summons)
    void FilterTargets(std::list<WorldObject*>& targets)
    {
        Unit* caster = GetCaster();
        targets.remove_if([caster](WorldObject* target)
        {
            TempSummon* summon = target->ToUnit() ? target->ToUnit()->ToTempSummon() : nullptr;
            return !summon || summon->GetSummonerUnit() != caster;
        });
    }

    void Register() override
    {
        OnObjectAreaTargetSelect += SpellObjectAreaTargetSelectFn(spell_gilneas_worgen_intro_completion::FilterTargets, EFFECT_1, TARGET_UNIT_SRC_AREA_ENTRY);
    }
};

enum GaspingForBreath
{
    NPC_DROWNING_WATCHMAN_CREDIT        = 36450,

    SPELL_RESCUE_DROWNING_WATCHMAN      = 68735,
    SPELL_SAVE_DROWNING_MILITA_EFFECT   = 68737,
    SPELL_DROWNING_MILITA_DUMMY         = 68739,
    SPELL_DROWNING_VEHICLE_EXIT_DUMMY   = 68741
};

// 68737 Save Drowning Militia Effect
class spell_gilneas_save_drowning_milita_effect : public SpellScript
{
    PrepareSpellScript(spell_gilneas_save_drowning_milita_effect);

    void HandleScript(SpellEffIndex effIndex)
    {
        PreventHitDefaultEffect(effIndex);
        if (Player* player = GetHitPlayer())
            player->KilledMonsterCredit(Id(NPC_DROWNING_WATCHMAN_CREDIT));
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_gilneas_save_drowning_milita_effect::HandleScript, EFFECT_0, SPELL_EFFECT_SCRIPT_EFFECT);
    }
};

// 68741 Drowning Vehicle Exit Dummy
class spell_gilneas_drowning_vehicle_exit_dummy : public SpellScript
{
    PrepareSpellScript(spell_gilneas_drowning_vehicle_exit_dummy);

    void HandleScript(SpellEffIndex effIndex)
    {
        PreventHitDefaultEffect(effIndex);
        if (Player* player = GetHitPlayer())
            player->RemoveAurasDueToSpell(SpellId(SPELL_RESCUE_DROWNING_WATCHMAN));
    }

    void HandleHit(SpellEffIndex /*effIndex*/)
    {
        if (Unit* unit = GetHitUnit())
            unit->ExitVehicle();
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_gilneas_drowning_vehicle_exit_dummy::HandleScript, EFFECT_0, SPELL_EFFECT_SCRIPT_EFFECT);
        OnEffectHitTarget += SpellEffectFn(spell_gilneas_drowning_vehicle_exit_dummy::HandleHit, EFFECT_1, SPELL_EFFECT_DUMMY);
    }
};

class at_gasping_for_breath : public AreaTriggerScript
{
public:
    at_gasping_for_breath() : AreaTriggerScript("at_gasping_for_breath") { }

    bool OnTrigger(Player* player, AreaTrigger const* /*trigger*/) override
    {
        if (Vehicle* vehicle = player->GetVehicleKit())
            if (Unit* passenger = vehicle->GetPassenger(SEAT_0))
            {
                player->CastSpell(passenger, SpellId(SPELL_DROWNING_MILITA_DUMMY));
                player->CastSpell(passenger, SpellId(SPELL_DROWNING_VEHICLE_EXIT_DUMMY));
                player->CastSpell(player, SpellId(SPELL_SAVE_DROWNING_MILITA_EFFECT));
            }
        return true;
    }
};

/*######
## CPP's generic spell scripts Gilneas uses (spell_generic.cpp there)
######*/

enum GilneasPrison
{
    SPELL_SUMMON_RAVENOUS_WORGEN_1 = 66836,
    SPELL_SUMMON_RAVENOUS_WORGEN_2 = 66925,

    NPC_WORGEN_RUNT                = 35456,
};

static Position const WorgenRuntHousePos[] =
{
    // House Roof
    { -1729.345f, 1526.495f, 55.47962f, 6.188943f },
    { -1709.63f, 1527.464f, 56.86086f, 3.258752f },
    { -1717.75f, 1513.727f, 55.47941f, 4.704845f },
    { -1724.719f, 1526.731f, 55.66177f, 6.138319f },
    { -1713.974f, 1526.625f, 56.21981f, 3.306195f },
    { -1718.104f, 1524.071f, 55.81641f, 4.709816f },
    { -1718.262f, 1518.557f, 55.55954f, 4.726997f },
    // Cathedral Roof
    { -1618.054f, 1489.644f, 68.45153f, 3.593639f },
    { -1625.62f, 1487.033f, 71.27762f, 3.531424f },
    { -1638.569f, 1489.736f, 68.55273f, 4.548815f },
    { -1630.399f, 1481.66f, 71.41516f, 3.484555f },
    { -1622.424f, 1483.882f, 67.67381f, 3.404875f },
    { -1634.344f, 1491.3f, 70.10101f, 4.6248f },
    { -1631.979f, 1491.585f, 71.11481f, 4.032866f },
    { -1627.273f, 1499.689f, 68.89395f, 4.251452f },
    { -1622.665f, 1489.818f, 71.03797f, 3.776179f },
};

// The worgen runts of By the Skin of his Teeth (14154), onto the house's roof or the cathedral's.
class spell_gen_gilneas_prison_periodic_dummy : public SpellScript
{
    PrepareSpellScript(spell_gen_gilneas_prison_periodic_dummy);

    static void SummonRunt(Unit* caster, uint8 i)
    {
        if (Creature* runt = caster->SummonCreature(Id(NPC_WORGEN_RUNT), WorgenRuntHousePos[i]))
            runt->AI()->DoAction(i);
    }

    void HandleDummy(SpellEffIndex /*effIndex*/)
    {
        Unit* caster = GetCaster();
        if (!caster)
            return;
        if (urand(0, 1) == 0)
        {
            caster->CastSpell(caster, SpellId(SPELL_SUMMON_RAVENOUS_WORGEN_1), true);
            for (uint8 i = 0; i < 7; i++)
                SummonRunt(caster, i);
        }
        else
        {
            caster->CastSpell(caster, SpellId(SPELL_SUMMON_RAVENOUS_WORGEN_2), true);
            for (uint8 i = 7; i < 16; i++)
                SummonRunt(caster, i);
            if (urand(0, 1) == 1)
                for (uint8 i = 0, n = urand(1, 3); i < n; i++)
                    SummonRunt(caster, i);
        }
    }

    void Register() override
    {
        OnEffectHitTarget += SpellEffectFn(spell_gen_gilneas_prison_periodic_dummy::HandleDummy, EFFECT_0, SPELL_EFFECT_DUMMY);
    }
};

enum ThrowTorch
{
    NPC_ROUND_UP_WORGEN_CREDIT  = 35582,
    SPELL_THROW_TORCH           = 67063
};

// Sacrifices (14212): a worgen not burning yet, set alight, counts.
class spell_gen_throw_torch : public SpellScript
{
    PrepareSpellScript(spell_gen_throw_torch);

    void HandleEffect(SpellMissInfo /*missInfo*/)
    {
        if (Player* player = GetCaster() ? GetCaster()->ToPlayer() : nullptr)
            if (GetHitUnit() && !GetHitUnit()->HasAura(SpellId(SPELL_THROW_TORCH)))
                player->KilledMonsterCredit(Id(NPC_ROUND_UP_WORGEN_CREDIT));
    }

    void Register() override
    {
        BeforeHit += BeforeSpellHitFn(spell_gen_throw_torch::HandleEffect);
    }
};
}

void AddWorgenGoblinGilneasScripts()
{
    using namespace WorgenGoblinGilneas;
    RegisterCreatureAI(npc_frightened_citizen);
    RegisterCreatureAI(npc_worgen_runt);
    RegisterCreatureAI(npc_josiah_avery);
    RegisterCreatureAI(npc_greymanes_horse);
    RegisterCreatureAI(npc_crowleys_horse);
    RegisterCreatureAI(npc_gilnean_crow);
    RegisterGameObjectAI(go_gilneas_invasion_camera);
    RegisterCreatureAI(npc_gilneas_horrid_abomination);
    RegisterCreatureAI(npc_gilneas_save_the_children);
    RegisterCreatureAI(npc_gilneas_forsaken_catapult);
    RegisterSpellScript(spell_gilneas_quest_save_the_children);
    RegisterSpellScript(spell_gilneas_launch);
    RegisterSpellScript(spell_gilneas_fiery_boulder);
    RegisterSpellScript(spell_gilneas_call_attack_mastiff);
    RegisterSpellScript(spell_gilneas_forcecast_cataclysm_1);
    RegisterSpellScript(spell_gilneas_worgen_intro_completion);
    RegisterSpellScript(spell_gilneas_save_drowning_milita_effect);
    RegisterSpellScript(spell_gilneas_drowning_vehicle_exit_dummy);
    new at_gasping_for_breath();
    RegisterSpellScript(spell_gen_gilneas_prison_periodic_dummy);
    RegisterSpellScript(spell_gen_throw_torch);
}
