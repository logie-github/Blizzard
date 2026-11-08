// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix: the Unrisen's plate, a death knight's set nobody mentions, in a Scourge coffer on
 * Malykriss's south terrace (wrath_remix_world_0031_vile_hold_set.sql). The coffer gives WRM-061 to
 * 063; this file is what the game can't do from the SQL alone:
 *
 *   - WRM-062: the Runesmith's Tally, used within reach of the Great Hourglass, has its name written
 *     (the quest's credit, a game object never spawned);
 *   - WRM-063: a /kneel by the coffer is its credit;
 *   - the coffer once its plate is taken: a piece of the set lost (not in the bags, the bank or worn,
 *     and the plate's container not still about) is in its cloth again.
 */

#include "WrathRemix.h"
#include "GameObject.h"
#include "Item.h"
#include "Player.h"
#include "QuestDef.h"
#include "ScriptMgr.h"
#include "ScriptedGossip.h"
#include "SharedDefines.h"
#include "WorldSession.h"
#include <vector>

using namespace WrathRemix;

namespace
{
    constexpr uint32 GO_COFFER = 770200;
    constexpr uint32 GO_GREAT_HOURGLASS = 770001;       // the Bazaar's heart (wrath_remix_world_0023_bazaar.sql)
    constexpr uint32 GO_CREDIT_NAME = 770205;           // WRM-062's credit
    constexpr uint32 GO_CREDIT_KNEEL = 770206;          // WRM-063's
    constexpr uint32 QUEST_NAME = 77062, QUEST_KNEEL = 77063;
    constexpr uint32 ITEM_FIRST_PIECE = 77010, ITEM_LAST_PIECE = 77018;
    constexpr uint32 ITEM_PLATE = 77019;                // the container the plate comes in
    constexpr uint32 TEXT_EMPTY_COFFER = 7702180;
    constexpr uint32 ACTION_LOST = 1;
    constexpr float HOURGLASS_REACH = 12.0f;
    constexpr float COFFER_REACH = 8.0f;

    // The pieces of the set this Timerunner has nowhere (bags, bank, worn), once they've had it.
    std::vector<uint32> Lost(Player* player)
    {
        std::vector<uint32> lost;
        if (!player->GetQuestRewardStatus(QUEST_KNEEL) || player->HasItemCount(ITEM_PLATE, 1, true))
            return lost;
        for (uint32 item = ITEM_FIRST_PIECE; item <= ITEM_LAST_PIECE; ++item)
            if (!player->HasItemCount(item, 1, true))
                lost.push_back(item);
        return lost;
    }
}

// The coffer: its three quests as any quest giver's, and once the plate is taken, the cloth.
class go_remix_unrisen_coffer : public GameObjectScript
{
public:
    go_remix_unrisen_coffer() : GameObjectScript("go_remix_unrisen_coffer") { }

    bool OnGossipHello(Player* player, GameObject* coffer) override
    {
        if (!Active() || !player->GetQuestRewardStatus(QUEST_KNEEL))
            return false;
        ClearGossipMenuFor(player);
        if (!Lost(player).empty())
            AddGossipItemFor(player, GOSSIP_ICON_CHAT, "Search the cloth for the plate you have lost.", GOSSIP_SENDER_MAIN, ACTION_LOST);
        SendGossipMenuFor(player, TEXT_EMPTY_COFFER, coffer->GetGUID());
        return true;
    }

    bool OnGossipSelect(Player* player, GameObject* /*coffer*/, uint32 /*sender*/, uint32 action) override
    {
        CloseGossipMenuFor(player);
        if (!Active() || action != ACTION_LOST)
            return true;
        bool given = false;
        for (uint32 item : Lost(player))
        {
            if (!player->AddItem(item, 1))
                break;
            given = true;
        }
        if (given)
            player->GetSession()->SendAreaTriggerMessage("The cloth gives back what you lost.");
        return true;
    }

    // A quest giver with nothing to give can't be clicked: once its quests are done, the coffer
    // still can (a status the game shows nothing for on an object).
    uint32 GetDialogStatus(Player* player, GameObject* /*coffer*/) override
    {
        if (Active() && player->GetQuestRewardStatus(QUEST_KNEEL))
            return DIALOG_STATUS_INCOMPLETE;
        return DIALOG_STATUS_SCRIPTED_NO_STATUS;
    }
};

// WRM-062's tally: its line written by the Great Hourglass's sands. (Its spell is never cast: the
// client is told the use is over.)
class item_remix_unrisen_tally : public ItemScript
{
public:
    item_remix_unrisen_tally() : ItemScript("item_remix_unrisen_tally") { }

    bool OnUse(Player* player, Item* item, SpellCastTargets const& /*targets*/) override
    {
        player->SendEquipError(EQUIP_ERR_NONE, item, nullptr);
        if (!Active())
            return true;
        if (player->GetQuestStatus(QUEST_NAME) != QUEST_STATUS_INCOMPLETE)
        {
            player->GetSession()->SendAreaTriggerMessage("Your name is on the tally. Take it back to the coffer.");
            return true;
        }
        if (!player->FindNearestGameObject(GO_GREAT_HOURGLASS, HOURGLASS_REACH))
        {
            player->GetSession()->SendAreaTriggerMessage("The tally's line is blank. Hold it up to the Great Hourglass, at the heart of the Bazaar.");
            return true;
        }
        player->KillCreditGO(GO_CREDIT_NAME);
        player->GetSession()->SendAreaTriggerMessage("The sands run backward over the tally. Where the line was blank, your name is written.");
        return true;
    }
};

// WRM-063: a /kneel by the coffer.
class RemixVileHoldSetPlayer : public PlayerScript
{
public:
    RemixVileHoldSetPlayer() : PlayerScript("RemixVileHoldSetPlayer", { PLAYERHOOK_ON_TEXT_EMOTE }) { }

    void OnPlayerTextEmote(Player* player, uint32 textEmote, uint32 /*emoteNum*/, ObjectGuid /*guid*/) override
    {
        if (textEmote != TEXT_EMOTE_KNEEL || !Active() || player->GetQuestStatus(QUEST_KNEEL) != QUEST_STATUS_INCOMPLETE)
            return;
        if (!player->FindNearestGameObject(GO_COFFER, COFFER_REACH))
            return;
        player->KillCreditGO(GO_CREDIT_KNEEL);
        player->GetSession()->SendAreaTriggerMessage("You kneel. No king answers.");
    }
};

void AddRemixVileHoldSetScripts()
{
    new go_remix_unrisen_coffer();
    new item_remix_unrisen_tally();
    new RemixVileHoldSetPlayer();
}
