// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * Gilneas's last chapter: what the Cataclysm Preservation Project left unscripted (its scripts end with
 * the second chapter: WorgenGoblinGilneas.cpp), written for AzerothCore after Cataclysm's quests and
 * spells. The battle for Gilneas City and the flight against the Horde's gunship, which Cataclysm plays
 * as long scripted events nobody's data has, count as the player gets where they end, at the user's
 * word ("if it's not crucial to the quest you can skip it or change it").
 *
 *  - The Hungry Ettin (14416): a Mountain Horse comes along with a player on it; brought to Lorna
 *    Crowley, it counts.
 *  - Stranded at the Marsh (24468): a Crash Survivor reached is set on by a Swamp Crocolisk; the
 *    crocolisk killed, the survivor's rescued (the quest counts the crocolisk).
 *  - Losing Your Tail (24616): Belysra's Talisman shows the Dark Scout that's following the player.
 *  - The Battle for Gilneas City (24904): won on reaching Greymane Court, where the battle ends.
 *  - The Hunt For Sylvanas (24902): done on reaching where Sylvanas is found.
 *  - Endgame (26706): a Hippogryph mounted when Tobias signals takes the gunship down.
 */

#include "WorgenGoblinZonesIds.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "ScriptedCreature.h"
#include "SpellInfo.h"
#include "SpellScript.h"
#include "SpellScriptLoader.h"
#include "TemporarySummon.h"
#include <set>
#include <unordered_map>

using namespace WorgenGoblinZones;

namespace
{
    enum GilneasEndIds : uint32
    {
        QUEST_THE_HUNGRY_ETTIN          = 14416,
        QUEST_STRANDED_AT_THE_MARSH     = 24468,
        QUEST_LOSING_YOUR_TAIL          = 24616,
        QUEST_BATTLE_FOR_GILNEAS_CITY   = 24904,
        QUEST_HUNT_FOR_SYLVANAS         = 24902,
        QUEST_ENDGAME                   = 26706,

        NPC_LORNA_CROWLEY_ORCHARD       = 36457,
        NPC_MOUNTAIN_HORSE_CREDIT       = 36560,
        NPC_SWAMP_CROCOLISK             = 37078,
        NPC_DARK_SCOUT                  = 37953,
        NPC_BATTLE_FOR_GILNEAS_CREDIT   = 38854,
        NPC_FINALE_CREDIT               = 43729,

        SPELL_BELYSRAS_TALISMAN         = 70797,
    };

    bool OnQuest(Player const* player, uint32 quest)
    {
        return player && player->GetQuestStatus(Id(quest)) == QUEST_STATUS_INCOMPLETE;
    }

    bool IsGilneas(uint32 map)
    {
        return map == 638 || map == 654 || map == 655 || map == 656;
    }

    // A quest done by getting somewhere: where, and what it counts (a creature's credit, or the
    // quest's event).
    struct Arrival
    {
        uint32 quest;
        float x, y, radius;
        uint32 credit;
    };

    Arrival constexpr ARRIVALS[] =
    {
        { QUEST_BATTLE_FOR_GILNEAS_CITY, -1664.0f, 1590.0f, 40.0f, NPC_BATTLE_FOR_GILNEAS_CREDIT },   // Greymane Court (Lorna, the battle's end)
        { QUEST_HUNT_FOR_SYLVANAS, -1678.0f, 1612.0f, 30.0f, 0 },                                    // Sylvanas found
    };
}

/*######
## The Hungry Ettin (14416)
######*/

struct npc_gilneas_mountain_horse : public ScriptedAI
{
    npc_gilneas_mountain_horse(Creature* creature) : ScriptedAI(creature) { }

    void MoveInLineOfSight(Unit* who) override
    {
        Player* player = who->ToPlayer();
        if (_player || !OnQuest(player, QUEST_THE_HUNGRY_ETTIN) || !me->IsWithinDistInMap(player, 5.0f))
            return;
        _player = player->GetGUID();
        me->SetReactState(REACT_PASSIVE);
        me->GetMotionMaster()->MoveFollow(player, 2.0f, float(M_PI));
        _check = 1000;
    }

    void UpdateAI(uint32 diff) override
    {
        if (!_player)
            return;
        if (_check > diff)
        {
            _check -= diff;
            return;
        }
        _check = 1000;
        Player* player = ObjectAccessor::GetPlayer(*me, _player);
        if (!player || !OnQuest(player, QUEST_THE_HUNGRY_ETTIN) || !me->IsWithinDistInMap(player, 60.0f))
        {
            _player.Clear();
            me->GetMotionMaster()->MoveTargetedHome();
            return;
        }
        if (me->FindNearestCreature(Id(NPC_LORNA_CROWLEY_ORCHARD), 15.0f))
        {
            player->KilledMonsterCredit(Id(NPC_MOUNTAIN_HORSE_CREDIT));
            _player.Clear();
            me->DespawnOrUnsummon(2s, 60s);
        }
    }

private:
    ObjectGuid _player;
    uint32 _check = 0;
};

/*######
## Stranded at the Marsh (24468)
######*/

struct npc_gilneas_crash_survivor : public ScriptedAI
{
    npc_gilneas_crash_survivor(Creature* creature) : ScriptedAI(creature) { }

    void MoveInLineOfSight(Unit* who) override
    {
        Player* player = who->ToPlayer();
        if (!OnQuest(player, QUEST_STRANDED_AT_THE_MARSH) || !me->IsWithinDistInMap(player, 12.0f) || _seen.count(player->GetGUID()))
            return;
        _seen.insert(player->GetGUID());
        Position pos = me->GetPosition();
        me->MovePosition(pos, 6.0f, float(rand_norm()) * 2.0f * float(M_PI));
        if (TempSummon* crocolisk = me->SummonCreature(Id(NPC_SWAMP_CROCOLISK), pos, TEMPSUMMON_TIMED_DESPAWN_OUT_OF_COMBAT, 60000))
            crocolisk->AI()->AttackStart(player);
    }

    void Reset() override
    {
        _seen.clear();
    }

private:
    std::set<ObjectGuid> _seen;
};

/*######
## Losing Your Tail (24616)
######*/

class spell_gilneas_belysras_talisman : public SpellScript
{
    PrepareSpellScript(spell_gilneas_belysras_talisman);

    void Reveal()
    {
        Player* player = GetCaster()->ToPlayer();
        if (!OnQuest(player, QUEST_LOSING_YOUR_TAIL) || player->FindNearestCreature(Id(NPC_DARK_SCOUT), 40.0f, true))
            return;
        Position pos = player->GetPosition();
        player->MovePosition(pos, 8.0f, float(M_PI));
        if (TempSummon* scout = player->SummonCreature(Id(NPC_DARK_SCOUT), pos, TEMPSUMMON_TIMED_DESPAWN_OUT_OF_COMBAT, 60000))
        {
            scout->SetFaction(FACTION_MONSTER);
            scout->AI()->AttackStart(player);
        }
    }

    void Register() override
    {
        AfterCast += SpellCastFn(spell_gilneas_belysras_talisman::Reveal);
    }
};

/*######
## Endgame (26706)
######*/

struct npc_gilneas_hippogryph : public ScriptedAI
{
    npc_gilneas_hippogryph(Creature* creature) : ScriptedAI(creature) { }

    void MoveInLineOfSight(Unit* who) override
    {
        Player* player = who->ToPlayer();
        if (!OnQuest(player, QUEST_ENDGAME) || !me->IsWithinDistInMap(player, 6.0f))
            return;
        player->KnockbackFrom(me->GetPositionX(), me->GetPositionY(), 8.0f, 12.0f);
        player->KilledMonsterCredit(Id(NPC_FINALE_CREDIT));
    }
};

/*######
## The Battle for Gilneas City (24904), The Hunt For Sylvanas (24902)
######*/

class WorgenGoblinGilneasEndPlayer : public PlayerScript
{
public:
    WorgenGoblinGilneasEndPlayer() : PlayerScript("WorgenGoblinGilneasEndPlayer", { PLAYERHOOK_ON_UPDATE }) { }

    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        if (!IsGilneas(player->GetMapId()))
            return;
        uint32& timer = _timers[player->GetGUID()];
        if (timer > diff)
        {
            timer -= diff;
            return;
        }
        timer = 1000;
        for (Arrival const& arrival : ARRIVALS)
        {
            if (!OnQuest(player, arrival.quest) || player->GetExactDist2d(arrival.x, arrival.y) > arrival.radius)
                continue;
            if (arrival.credit)
                player->KilledMonsterCredit(Id(arrival.credit));
            else
                player->AreaExploredOrEventHappens(Id(arrival.quest));
        }
    }

private:
    std::unordered_map<ObjectGuid, uint32> _timers;
};

void AddWorgenGoblinGilneasEndScripts()
{
    RegisterCreatureAI(npc_gilneas_mountain_horse);
    RegisterCreatureAI(npc_gilneas_crash_survivor);
    RegisterSpellScript(spell_gilneas_belysras_talisman);
    RegisterCreatureAI(npc_gilneas_hippogryph);
    new WorgenGoblinGilneasEndPlayer();
}
