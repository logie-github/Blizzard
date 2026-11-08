"""Moratari beside the Timerunner, wherever the story is (tools/story.py): where she walks with them, and
what can always be said to her."""
from story_common import (ALLIANCE, HORDE, BOTH, MORATARI, TURNED_IN, STAY, COME, ZONE_BOREAN_TUNDRA,
                          TO_THE_FRONT_A, TO_THE_FRONT_H, INTO_THE_DRAGONBLIGHT_A, INTO_THE_DRAGONBLIGHT_H)

COMPANION = [
    dict(side=ALLIANCE, zone=ZONE_BOREAN_TUNDRA, **{"from": TO_THE_FRONT_A}, until=INTO_THE_DRAGONBLIGHT_A,
         why="Chapter I: the Borean Tundra, while the Timerunner finds their feet"),
    dict(side=HORDE, zone=ZONE_BOREAN_TUNDRA, **{"from": TO_THE_FRONT_H}, until=INTO_THE_DRAGONBLIGHT_H,
         why="Chapter I: the Borean Tundra, while the Timerunner finds their feet"),
]

WORDS = [
    # The landing
    (TO_THE_FRONT_A, TURNED_IN, ALLIANCE, "Valiance Keep. The fleet came in three days ago, and the Scourge has tested the walls every night since. You remember the smell of this place, I imagine: tar, salt, and far too many soldiers in one harbor."),
    (TO_THE_FRONT_A, TURNED_IN, ALLIANCE, "I will walk with you while you find your feet. If you would rather I waited somewhere, say so.", dict(delay=7000)),
    (TO_THE_FRONT_H, TURNED_IN, HORDE, "Warsong Hold. Garrosh's fortress, built over tunnels that are already full of nerubians, though no one inside knows it yet. Well. Almost no one."),
    (TO_THE_FRONT_H, TURNED_IN, HORDE, "I will walk with you while you find your feet. If you would rather I waited somewhere, say so.", dict(delay=7000)),
]

TALK = [
    dict(key="stay", npc=MORATARI, option="Wait for me here. I'd like to walk alone for a while.",
         reply="Of course. I will be at the camps, beside whoever has work for you next. Say the word when you want me back.",
         action=STAY),
    dict(key="come", npc=MORATARI, option="Walk with me again.",
         reply="I was hoping you would ask. Lead on, $N.",
         action=COME),
]
