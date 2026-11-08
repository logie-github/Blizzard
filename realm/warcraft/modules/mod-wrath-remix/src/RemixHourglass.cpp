// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Moratari's Hourglass (wrath_remix_world_0021_hourglass.sql): Moratari puts it in a Timerunner's
 * bags as they wake at the Bazaar (a death knight's as they come to it from Acherus), and it stays
 * there until they go home. Turned anywhere, it takes them to the Bazaar; turned at the Bazaar, it
 * takes them back to where they came to it from, however they came (the hourglass, a hearthstone,
 * one of the story's quests). Not in a fight, nor dead, nor on a flight, nor in a battleground.
 * Where it can't take them back as it was, the nearest safe place: from a boat or a zeppelin, the
 * graveyard of their side nearest its dock; from a dungeon or a raid, outside its door; from the
 * air, the ground (or the water) beneath.
 */

#include "WrathRemix.h"
#include "Chat.h"
#include "ChatCommand.h"
#include "DBCStores.h"
#include "GameGraveyard.h"
#include "Item.h"
#include "Map.h"
#include "MapMgr.h"
#include "ObjectMgr.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "StringFormat.h"
#include "Transport.h"
#include <cmath>
#include <set>

using namespace WrathRemix;

namespace
{
    constexpr uint32 SPELL_TELEPORT_VISUAL = 51347;
    constexpr float BAZAAR_REACH = 60.0f;       // how far the Bazaar is the Bazaar
    constexpr uint32 ZONE_DALARAN = 4395;
    std::set<ObjectGuid::LowType> backToDalaran;    // (her word on it once each, until the server restarts)

    void Tell(Player* player, std::string const& text)
    {
        ChatHandler(player->GetSession()).SendSysMessage("|cff8fd3ffMoratari's Hourglass:|r " + text);
    }

    // Turned: to the Bazaar, or from it back where they were.
    void Turn(Player* player)
    {
        if (player->IsBeingTeleported() || !player->IsInWorld())
            return;
        if (!player->IsAlive())
            return Tell(player, "The sand will not run for the dead. Find your body first.");
        if (player->IsInCombat())
            return Tell(player, "Not in the middle of a fight.");
        if (player->IsInFlight())
            return Tell(player, "Not on a flight. Wait until you land.");
        if (player->InBattleground() || player->InArena())
            return Tell(player, "Not here. This fight keeps its own time.");
        if (SceneRunning(player) || InIntro(player))
            return Tell(player, "Not now. Let the moment finish.");

        if (AtTheBazaar(player))
        {
            Timerunner const t = Get(player);
            if (t.backMap < 0)
                return Tell(player, "You are at the Bazaar, and have come here from nowhere yet that it could take you back to.");
            player->CastSpell(player, SPELL_TELEPORT_VISUAL, true);
            // (from the dark, briefly: the place's name while the game loads it)
            JourneyFromTheDark(player, PlaceName(uint32(t.backMap), t.backX, t.backY, t.backZ), uint32(t.backMap), t.backX, t.backY, 0, 1500);
            if (!player->TeleportTo(uint32(t.backMap), t.backX, t.backY, t.backZ, t.backO))
            {
                LiftTheCurtain(player);
                Tell(player, "The way back is closed for now. Try again in a moment.");
            }
            // Back to Dalaran: Moratari's word on it, once a while (her own voice)
            else if (sMapMgr->GetZoneId(PHASEMASK_NORMAL, uint32(t.backMap), t.backX, t.backY, t.backZ) == ZONE_DALARAN &&
                     backToDalaran.insert(player->GetGUID().GetCounter()).second)
                MoratariVoice(player, "back_to_dalaran");
            return;
        }

        // (where they were is kept as they go: the teleport's own hook, below)
        Destination const* bazaar = DestinationFor(TRAVEL_BAZAAR);
        if (!bazaar)
            return;
        player->CastSpell(player, SPELL_TELEPORT_VISUAL, true);
        JourneyFromTheDark(player, PlaceName(bazaar->map, bazaar->x, bazaar->y, bazaar->z), bazaar->map, bazaar->x, bazaar->y, 0, 1500);
        if (!player->TeleportTo(bazaar->map, bazaar->x, bazaar->y, bazaar->z, bazaar->o))
            LiftTheCurtain(player);
    }

    // The door out of a dungeon or a raid: its area trigger to the map its entrance is on. (The
    // core's GetGoBackTrigger looks for one to its instance_template parent instead, which is 0,
    // the Eastern Kingdoms, for all but a few: none for Northrend's.)
    AreaTriggerTeleport const* DoorOut(uint32 mapId)
    {
        MapEntry const* entry = sMapStore.LookupEntry(mapId);
        if (!entry || entry->entrance_map < 0)
            return nullptr;
        for (auto const& [id, teleport] : sObjectMgr->GetAllAreaTriggerTeleports())
            if (teleport.target_mapId == uint32(entry->entrance_map))
                if (AreaTrigger const* trigger = sObjectMgr->GetAreaTrigger(id))
                    if (trigger->map == mapId)
                        return &teleport;
        return nullptr;
    }

    // The graveyard of [player]'s side nearest [x, y, z] on their map, as the game links them (to its
    // area or its zone; a dungeon's, outside it), or none: the side's default one (the Crossroads,
    // Westfall), the game's when it knows of none there, is nowhere near.
    GraveyardStruct const* GraveNear(Player* player, float x, float y, float z)
    {
        uint32 zone = 0, area = 0;
        player->GetMap()->GetZoneAndAreaId(player->GetPhaseMask(), zone, area, x, y, z);
        if (!zone && !area)
            return nullptr;
        GraveyardStruct const* grave = sGraveyard->GetClosestGraveyard(player->GetMapId(), x, y, z, player->GetTeamId(), area, zone, false);
        return grave == sGraveyard->GetDefaultGraveyard(player->GetTeamId()) ? nullptr : grave;
    }

    // Where "back" is, for a Timerunner going to the Bazaar from where they stand: there, but never
    // where it couldn't take them as it was. Aboard a boat or a zeppelin (open water or air by then),
    // the graveyard of their side nearest its dock on that map (an elevator's, nearest them); in a
    // dungeon or a raid (its instance gone by then, or a new one, past its gates; the Frozen Throne
    // after the Lich King), outside its door; in the air, the ground or the water beneath. False:
    // nowhere, and the way back stays where it was.
    bool WayBackFrom(Player* player, WorldLocation& back)
    {
        Map* map = player->GetMap();
        if (map->Instanceable())
        {
            if (!map->IsDungeon())
                return false;
            if (AreaTriggerTeleport const* door = DoorOut(player->GetMapId()))
            {
                back.WorldRelocate(door->target_mapId, door->target_X, door->target_Y, door->target_Z, door->target_Orientation);
                return true;
            }
            // (no door the game knows of: the graveyard outside, where its ghosts go; not one inside)
            GraveyardStruct const* grave = GraveNear(player, player->GetPositionX(), player->GetPositionY(), player->GetPositionZ());
            if (!grave || grave->Map == player->GetMapId())
                return false;
            back.WorldRelocate(grave->Map, grave->x, grave->y, grave->z, player->GetOrientation());
            return true;
        }
        if (Transport* transport = player->GetTransport())
        {
            float x = player->GetPositionX(), y = player->GetPositionY(), z = player->GetPositionZ();
            if (MotionTransport* ship = transport->ToMotionTransport())
            {
                // (its stops on this map: the dock nearest them)
                TaxiPathNodeEntry const* dock = nullptr;
                if (TransportTemplate const* path = ship->GetTransportTemplate())
                    for (KeyFrame const& frame : path->keyFrames)
                        if (frame.IsStopFrame() && frame.Node->mapid == player->GetMapId() &&
                            (!dock || player->GetExactDist2dSq(frame.Node->x, frame.Node->y) < player->GetExactDist2dSq(dock->x, dock->y)))
                            dock = frame.Node;
                if (!dock)
                    return false;
                x = dock->x, y = dock->y, z = dock->z;
            }
            GraveyardStruct const* grave = GraveNear(player, x, y, z);
            if (!grave || grave->Map != player->GetMapId())
                return false;
            back.WorldRelocate(grave->Map, grave->x, grave->y, grave->z, player->GetOrientation());
            return true;
        }
        float z = player->GetPositionZ();
        if (player->IsFlying() || player->IsFalling())
        {
            float below = player->GetMapWaterOrGroundLevel(player->GetPositionX(), player->GetPositionY(), z);
            if (below > INVALID_HEIGHT && below < z)
                z = below;
        }
        back.WorldRelocate(player->GetMapId(), player->GetPositionX(), player->GetPositionY(), z, player->GetOrientation());
        return true;
    }
}

namespace WrathRemix
{
    bool AtTheBazaar(Player* player)
    {
        return player->GetMapId() == MAP_NORTHREND && player->GetExactDist2d(BAZAAR_X, BAZAAR_Y) < BAZAAR_REACH;
    }

    void GiveHourglass(Player* player)
    {
        if (!Active() || IsBot(player) || player->HasItemCount(ITEM_HOURGLASS, 1, true) || !sObjectMgr->GetItemTemplate(ITEM_HOURGLASS))
            return;
        // (a death knight has it as they come to the Bazaar, done with Acherus; one gone home, never again)
        if ((player->getClass() == CLASS_DEATH_KNIGHT && !Get(player).chapter) || player->GetQuestRewardStatus(QUEST_BACK_TO_YOUR_OWN_TIME))
            return;
        ItemPosCountVec dest;
        if (player->CanStoreNewItem(NULL_BAG, NULL_SLOT, dest, ITEM_HOURGLASS, 1) != EQUIP_ERR_OK)
        {
            // (never by mail: the bags are where it's looked for, and a second would be waiting)
            Tell(player, "Your bags are full. Make room, and I will find my way back into them.");
            return;
        }
        if (Item* item = player->StoreNewItem(dest, ITEM_HOURGLASS, true))
            player->SendNewItem(item, 1, true, false);
    }

    // .remix hourglass (game masters, for CI's tests): where it is in the bags, and where it would
    // take them back to.
    std::string HourglassReport(Player* player)
    {
        Item* item = player->GetItemByEntry(ITEM_HOURGLASS);
        Timerunner const t = Get(player);
        std::string back = t.backMap < 0 ? std::string("nowhere") :
            Acore::StringFormat("map {} at {:.1f} {:.1f} {:.1f}", t.backMap, t.backX, t.backY, t.backZ);
        if (!item)
            return "Wrath Remix hourglass: none, way back " + back + ".";
        ItemTemplate const* proto = item->GetTemplate();
        return Acore::StringFormat("Wrath Remix hourglass: bag {} slot {} item {} spell {}, at the Bazaar: {}, way back {}.",
            uint32(item->GetBagSlot()), uint32(item->GetSlot()), item->GetGUID().GetRawValue(), proto->Spells[0].SpellId,
            AtTheBazaar(player) ? "yes" : "no", back);
    }
}

class item_remix_hourglass : public ItemScript
{
public:
    item_remix_hourglass() : ItemScript("item_remix_hourglass") { }

    bool OnUse(Player* player, Item* item, SpellCastTargets const& /*targets*/) override
    {
        // (the item's own spell is never cast: the client is told the use is over)
        player->SendEquipError(EQUIP_ERR_NONE, item, nullptr);
        if (Active())
            Turn(player);
        return true;
    }
};

// Where a Timerunner came to the Bazaar from, kept as they go (any teleport there from somewhere
// else but Acherus).
class RemixHourglassPlayer : public PlayerScript
{
public:
    RemixHourglassPlayer() : PlayerScript("RemixHourglassPlayer", { PLAYERHOOK_ON_BEFORE_TELEPORT }) { }

    bool OnPlayerBeforeTeleport(Player* player, uint32 mapid, float x, float y, float /*z*/, float /*orientation*/, uint32 /*options*/, Unit* /*target*/) override
    {
        if (!Active() || !player->IsInWorld() || IsBot(player) || InIntro(player))
            return true;
        bool toBazaar = mapid == MAP_NORTHREND && std::hypot(x - BAZAAR_X, y - BAZAAR_Y) < BAZAAR_REACH;
        WorldLocation back;
        if (toBazaar && !AtTheBazaar(player) && player->GetMapId() != MAP_EBON_HOLD && WayBackFrom(player, back))
            SetWayBack(player, int32(back.GetMapId()), back.GetPositionX(), back.GetPositionY(), back.GetPositionZ(), back.GetOrientation());
        return true;
    }
};

void AddRemixHourglassScripts()
{
    new item_remix_hourglass();
    new RemixHourglassPlayer();
}
