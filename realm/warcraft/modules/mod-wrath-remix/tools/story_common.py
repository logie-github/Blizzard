"""What the story's content files share (tools/story.py): ids, constants, and small helpers."""

TAKEN, DONE, TURNED_IN = 1, 2, 3
BOTH, ALLIANCE, HORDE = 0, 1, 2
ALLIANCE_RACES, HORDE_RACES = 1101, 690

MORATARI, ETERNUS = 770001, 770002

# remix_talk's actions (RemixMoratari.cpp)
SCENE, CLOSE, STAY, COME, OUTING, TIME_JUMP = 1, 2, 3, 4, 5, 6
ICON_CHAT, ICON_TALK = 0, 0

ZONE_BOREAN_TUNDRA, ZONE_DRAGONBLIGHT = 3537, 65

QUEST_FLAG_ALONE = 77040
TO_THE_FRONT_A, TO_THE_FRONT_H = 77014, 77015
INTO_THE_DRAGONBLIGHT_A, INTO_THE_DRAGONBLIGHT_H = 77121, 77122
STRANGERS, WEIGHT_OF_TIME = 77204, 77207

# Conditions (ConditionMgr.h): (type, value1, value2, negative)
REWARDED, TAKEN_COND, QUESTSTATE = 8, 9, 47
# Quest state masks for QUESTSTATE: 1 not taken, 2 objectives done, 8 in progress, 64 turned in
NOT_TAKEN, OBJECTIVES_DONE, IN_PROGRESS, TURNED_IN_STATE = 1, 2, 8, 64
TAKEN_OR_DONE = 2 | 8 | 64   # in the log or turned in


def rewarded(quest, negative=0):
    return (REWARDED, quest, 0, negative)


def not_rewarded(quest):
    return (REWARDED, quest, 0, 1)


def state(quest, mask, negative=0):
    return (QUESTSTATE, quest, mask, negative)


def sql_text(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"
