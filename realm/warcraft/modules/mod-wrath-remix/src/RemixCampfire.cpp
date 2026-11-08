// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix: the Bazaar's campfire. Nothing happens by it on its own; a Timerunner who clicks it has
 * Moratari walk over from her post and sit with them a while. While she sits there with them, and only
 * then, she can be told they're a time jumper (remix_talk's TALK_TIME_JUMPER: RemixMoratari.cpp), which
 * opens her story (tools/romance.py) without the war's checkpoints. She goes back to her post after a
 * minute and a half, or sooner if they walk off.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "Creature.h"
#include "GameObject.h"
#include "MotionMaster.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include <algorithm>
#include <list>

using namespace WrathRemix;

namespace
{
    constexpr uint32 POINT_FIRE = 77101, POINT_POST = 77102;
    constexpr uint32 SITS_FOR_MS = 90000;     // how long she stays by the fire
    constexpr uint32 LOOK_EVERY_MS = 5000;    // (whether they're still there)
    constexpr float WALKED_OFF = 25.0f;       // farther than this from her: they've gone

    enum FirePhase : uint8
    {
        FIRE_NONE = 0,
        FIRE_WALKING,
        FIRE_SITTING,
        FIRE_RETURNING,
    };

    // Her visit, kept on her (the Bazaar's own Moratari): for whom, how far along, and which visit
    // (a timer from an earlier one does nothing).
    struct FireVisit : public DataMap::Base
    {
        ObjectGuid player;
        uint8 phase = FIRE_NONE;
        uint32 round = 0;
        uint32 sat = 0;
    };

    FireVisit* VisitOf(Creature* her)
    {
        return her->CustomData.GetDefault<FireVisit>("remix_campfire");
    }

    // Her own spawn at the Bazaar, in sight of the Timerunner.
    Creature* PostFor(Player* player, GameObject* fire)
    {
        std::list<Creature*> near;
        fire->GetCreatureListWithEntryInGrid(near, NPC_MORATARI, 80.0f);
        Creature* best = nullptr;
        for (Creature* c : near)
            if (c->GetSpawnId() && c->IsAlive() && !c->IsInCombat() && player->CanSeeOrDetect(c) &&
                (!best || fire->GetDistance(c) < fire->GetDistance(best)))
                best = c;
        return best;
    }

    // Said aloud beside the Timerunner, for them alone.
    void Say(Creature* her, Player* player, std::string const& text)
    {
        WorldPacket data;
        ChatHandler::BuildChatPacket(data, CHAT_MSG_MONSTER_SAY, LANG_UNIVERSAL, her, player, Words(player, text));
        player->SendDirectMessage(&data);
    }

    std::string Greeting(Player* player)
    {
        if (player->GetQuestRewardStatus(QUEST_ROMANCE_LAST))
            return "Our fire. I wondered when you would come back to it.";
        if (player->GetQuestRewardStatus(QUEST_ROMANCE_FIRST) || player->GetQuestRewardStatus(QUEST_ROMANCE_TIME_JUMPER))
            return "Saving me a seat? Good. The post can stand there without me for a while.";
        return "You have looked over at my post three times from this fire. I counted. Is there something you wanted to ask me, $N?";
    }

    void GoBack(Creature* her)
    {
        FireVisit* visit = VisitOf(her);
        visit->phase = FIRE_RETURNING;
        uint32 round = ++visit->round;
        her->SetStandState(UNIT_STAND_STATE_STAND);
        Position const& home = her->GetHomePosition();
        her->SetWalk(true);
        her->GetMotionMaster()->MovePoint(POINT_POST, home.GetPositionX(), home.GetPositionY(), home.GetPositionZ());
        uint32 travel = uint32(her->GetExactDist(&home) / std::max(0.5f, her->GetSpeed(MOVE_WALK)) * IN_MILLISECONDS) + 800;
        her->m_Events.AddEventAtOffset([her, round]()
        {
            FireVisit* v = VisitOf(her);
            if (v->round != round)
                return;
            her->SetFacingTo(her->GetHomePosition().GetOrientation());
            *v = FireVisit();
            v->round = round;
        }, Milliseconds(travel));
    }

    // By the fire: still with her, a look every few seconds; back to her post when the time is up or
    // they've gone.
    void Watch(Creature* her, ObjectGuid playerGuid, uint32 round)
    {
        her->m_Events.AddEventAtOffset([her, playerGuid, round]()
        {
            FireVisit* visit = VisitOf(her);
            if (visit->round != round || visit->phase != FIRE_SITTING)
                return;
            visit->sat += LOOK_EVERY_MS;
            Player* player = ObjectAccessor::FindPlayer(playerGuid);
            if (!player || !player->IsInWorld() || player->GetMap() != her->GetMap() || !her->IsWithinDist(player, WALKED_OFF) ||
                visit->sat >= SITS_FOR_MS)
            {
                GoBack(her);
                return;
            }
            Watch(her, playerGuid, round);
        }, Milliseconds(LOOK_EVERY_MS));
    }

    void Arrive(Creature* her, ObjectGuid playerGuid, uint32 round)
    {
        FireVisit* visit = VisitOf(her);
        if (visit->round != round || visit->phase != FIRE_WALKING)
            return;
        Player* player = ObjectAccessor::FindPlayer(playerGuid);
        if (!player || !player->IsInWorld() || player->GetMap() != her->GetMap() || !her->IsWithinDist(player, WALKED_OFF))
        {
            GoBack(her);
            return;
        }
        visit->phase = FIRE_SITTING;
        visit->sat = 0;
        her->SetFacingToObject(player);
        her->SetStandState(UNIT_STAND_STATE_SIT);
        Say(her, player, Greeting(player));
        Watch(her, playerGuid, round);
    }

    void CallHer(Player* player, GameObject* fire)
    {
        Creature* her = PostFor(player, fire);
        if (!her)
        {
            ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari|r isn't at her post just now.");
            return;
        }
        FireVisit* visit = VisitOf(her);
        if (visit->phase == FIRE_WALKING || visit->phase == FIRE_SITTING)
        {
            if (visit->player != player->GetGUID())
                ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari|r is sitting with someone else by the fire.");
            return;
        }
        visit->player = player->GetGUID();
        visit->phase = FIRE_WALKING;
        uint32 round = ++visit->round;
        float x, y, z;
        player->GetNearPoint(her, x, y, z, her->GetCombatReach(), 1.6f, player->GetAngle(her));
        her->SetStandState(UNIT_STAND_STATE_STAND);
        her->SetWalk(true);
        her->GetMotionMaster()->MovePoint(POINT_FIRE, x, y, z);
        uint32 travel = uint32(her->GetExactDist(x, y, z) / std::max(0.5f, her->GetSpeed(MOVE_WALK)) * IN_MILLISECONDS) + 600;
        ObjectGuid playerGuid = player->GetGUID();
        her->m_Events.AddEventAtOffset([her, playerGuid, round]() { Arrive(her, playerGuid, round); }, Milliseconds(travel));
    }
}

namespace WrathRemix
{
    bool AtTheCampfire(Player* player, Creature* her)
    {
        if (!her->GetSpawnId())
            return false;
        FireVisit const* visit = VisitOf(her);
        return visit->phase == FIRE_SITTING && visit->player == player->GetGUID() && her->IsWithinDist(player, 10.0f);
    }
}

// The campfire itself (tools/bazaar.py gives it this script): a click calls her over.
class go_remix_campfire : public GameObjectScript
{
public:
    go_remix_campfire() : GameObjectScript("go_remix_campfire") { }

    bool OnGossipHello(Player* player, GameObject* fire) override
    {
        if (!Active() || IsBot(player))
            return false;
        CallHer(player, fire);
        return true;
    }
};

void AddRemixCampfireScripts()
{
    new go_remix_campfire();
}
