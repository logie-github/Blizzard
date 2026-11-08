// SPDX-License-Identifier: GPL-3.0-or-later
// Run the actual script against a small player API stand-in to check its lifecycle.
#include "../src/GhostFlight.cpp"
#include <cassert>
#include <iostream>
int main()
{
    GhostFlightPlayer script;
    Player player;
    player.auras.insert(12345); // an unrelated aura survives every transition
    script.OnPlayerLogin(&player);
    assert(!player.HasAura(55164)); // alive, or a corpse before release
    player.ghost = true;
    script.OnPlayerReleasedGhost(&player);
    assert(player.HasAura(55164) && player.casts == 1);
    script.OnPlayerUpdate(&player, 1000);
    assert(player.casts == 1); // no repeated mounting while the aura is present
    player.auras.erase(55164); // a graveyard/map transfer removed the flight
    script.OnPlayerUpdate(&player, 1000);
    assert(player.HasAura(55164) && player.casts == 2);
    player.auras.erase(55164);
    script.OnPlayerLogin(&player); // reconnect as a ghost
    assert(player.HasAura(55164));
    player.ghost = false;
    bool sickness = false;
    script.OnPlayerResurrect(&player, 0.5f, sickness);
    assert(!player.HasAura(55164) && player.HasAura(12345));
    script.OnPlayerUpdate(&player, 1000);
    assert(!player.HasAura(55164));
    std::cout << "Ghost flight: release, transfer, reconnect, resurrection; unrelated auras preserved\n";
}
