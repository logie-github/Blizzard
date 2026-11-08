// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef MOD_BRILL_HOME_H
#define MOD_BRILL_HOME_H

#include "Define.h"

class Creature;
class Player;

// What the house (src/BrillHome.cpp) and the town's questlines (src/BrillTown.cpp) share.
namespace BrillHome
{
    bool Enabled();
    // brill_home.flags: the dog's, Carolai's (src/BrillHome.cpp).
    uint32 Flags(Player* player);
    bool OwnsHouse(Player* player);
    // Jamie Nore's furniture: the list, and one bought (its index).
    void SendUpgrades(Player* player, Creature* creature);
    void BuyUpgrade(Player* player, Creature* creature, uint32 index);
    // A piece given free (the town's house line); false if it's theirs already.
    bool GiveUpgrade(Player* player, uint32 index);
    bool HasUpgrade(Player* player, uint32 index);
    // Puts the phases a player's in near the house and in Brill right again now.
    void RefreshPhases(Player* player);
    constexpr uint32 SENDER_BUY = 2;
}

namespace BrillTown
{
    // The town's lines' tables (brill_town_*), read as the world server starts.
    void Load();
    // The town's phases that are this player's (any of a phase's rows whose conditions all hold).
    uint32 Phases(Player* player);
    void Forget(Player* player);
    // A player in the house's cellar who has fallen through its floor, or (login) comes into the game in
    // it, put back in the house by the hatch; true if they were.
    bool KeepOutOfTheGround(Player* player, bool login);
    // The town's options for a creature added to the menu being made (one with a script of its own calls
    // it); its greeting for the player, if a line has one (0: none). The options' choosing is the town's.
    uint32 AddOptions(Player* player, Creature* creature);
    // The projects' stages detected: those reached in Brill, none outside it.
    void RefreshStages(Player* player, bool inBrill);
    void AddScripts();
}

#endif
