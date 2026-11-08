// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * On a phone the server can be stopped at any moment (the system reclaiming the app, a swipe, a dead
 * battery), and the core saves a character every fifteen minutes. So each real player's character is
 * saved every 30 seconds (WrathRemix.SaveSeconds), on either realm, the way the core saves it on its
 * own interval; the realm's bots keep the core's interval, so the phone isn't writing fifty of them
 * twice a minute. The app also has the realm save everyone as the game goes behind (ServerService).
 */

#include "WrathRemix.h"
#include "Config.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"

using namespace WrathRemix;

namespace
{
    Milliseconds Every()
    {
        uint32 seconds = sConfigMgr->GetOption<uint32>("WrathRemix.SaveSeconds", 30, false);
        return Milliseconds(std::max<uint32>(seconds, 10) * 1000);
    }

    void SaveEvery(ObjectGuid guid, Milliseconds after)
    {
        Player* player = ObjectAccessor::FindConnectedPlayer(guid);
        if (!player)
            return;
        player->m_Events.AddEventAtOffset([guid]()
        {
            Player* p = ObjectAccessor::FindPlayer(guid);
            if (!p || !p->IsInWorld())
                return;
            if (!p->IsBeingTeleported())
                p->SaveToDB(false, false);
            SaveEvery(guid, Every());
        }, after);
    }
}

class PlayerSaves : public PlayerScript
{
public:
    PlayerSaves() : PlayerScript("WrathRemixPlayerSaves", { PLAYERHOOK_ON_LOGIN }) { }

    void OnPlayerLogin(Player* player) override
    {
        if (IsBot(player) || sConfigMgr->GetOption<uint32>("WrathRemix.SaveSeconds", 30, false) == 0)
            return;
        SaveEvery(player->GetGUID(), Every());
    }
};

void AddPlayerSavesScripts()
{
    new PlayerSaves();
}
