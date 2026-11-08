// SPDX-License-Identifier: GPL-3.0-or-later
// The stock spectral gryphon is a ghost mount: apply it on release and reconnect,
// retain it through graveyard teleports, and remove it on every resurrection path.
#include "Player.h"
#include "ScriptMgr.h"

namespace
{
    constexpr uint32 SPECTRAL_GRYPHON = 55164;
    struct GhostFlightState : DataMap::Base { uint32 elapsed = 0; };

    void Refresh(Player* player)
    {
        if (player->HasPlayerFlag(PLAYER_FLAGS_GHOST))
        {
            if (!player->HasAura(SPECTRAL_GRYPHON))
                player->CastSpell(player, SPECTRAL_GRYPHON, true);
        }
        else
            player->RemoveAurasDueToSpell(SPECTRAL_GRYPHON);
    }
}

class GhostFlightPlayer : public PlayerScript
{
public:
    GhostFlightPlayer() : PlayerScript("GhostFlightPlayer", {
        PLAYERHOOK_ON_PLAYER_RELEASED_GHOST, PLAYERHOOK_ON_LOGIN,
        PLAYERHOOK_ON_PLAYER_RESURRECT, PLAYERHOOK_ON_UPDATE }) { }

    void OnPlayerReleasedGhost(Player* player) override { Refresh(player); }
    void OnPlayerLogin(Player* player) override { Refresh(player); }
    void OnPlayerResurrect(Player* player, float /*restore*/, bool& /*sickness*/) override
    {
        player->RemoveAurasDueToSpell(SPECTRAL_GRYPHON);
    }
    void OnPlayerUpdate(Player* player, uint32 diff) override
    {
        auto* state = player->CustomData.GetDefault<GhostFlightState>("GhostFlight");
        state->elapsed += diff;
        if (state->elapsed >= 1000)
        {
            state->elapsed = 0;
            Refresh(player);
        }
    }
};

void AddGhostFlightScripts() { new GhostFlightPlayer(); }
