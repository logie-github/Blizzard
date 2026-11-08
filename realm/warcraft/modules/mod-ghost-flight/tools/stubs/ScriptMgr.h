// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "Player.h"
#include <initializer_list>
enum Hook { PLAYERHOOK_ON_PLAYER_RELEASED_GHOST, PLAYERHOOK_ON_LOGIN,
    PLAYERHOOK_ON_PLAYER_RESURRECT, PLAYERHOOK_ON_UPDATE };
struct PlayerScript {
    PlayerScript(char const*, std::initializer_list<Hook>) {}
    virtual void OnPlayerReleasedGhost(Player*) {}
    virtual void OnPlayerLogin(Player*) {}
    virtual void OnPlayerResurrect(Player*, float, bool&) {}
    virtual void OnPlayerUpdate(Player*, uint32) {}
};
