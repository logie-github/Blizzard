"""Moratari, if you like (STORY.md, "Moratari, if you like"; tools/story.py writes it): an optional line of
nine quests with her, from tea in the Borean Tundra to a promise in Icecrown, each opened by a
checkpoint in the main story, flirting first and something real after.

- Its dates are outings (RemixOutings.cpp): cider at a Dalaran inn (A Hero's Welcome for the
  Alliance, The Filthy Animal for the Horde), dinner at Krasus' Landing in her evening dress, the top
  of Wyrmrest Temple at night (where she shows the Timerunner her true shape), a flight on her back
  from Dalaran to Wyrmrest, and her tent at the Bazaar: private (a phase of its own), the
  Timerunner's gear unseen and hers set aside, the screen fading to black; afterwards their gear is
  seen again, she is at her post, and they are back where they were.
- An afternoon of their own in Sholazar (three crocolisks evicted, a blanket by the river), and a
  promise at the edge of the camp in Icecrown.
- After the tent she walks with the Timerunner everywhere, until they go home (Back to Your Own
  Time). On ChromieCraft, her letter is waiting in the mail; Chromie brings it (RemixEnding.cpp).

It stays PG-13 and in Warcraft's voice: flirting, kisses, a fade to black. Her words are the same for
every Timerunner, whatever their sex; now and then she says something about their race. She is of the
Infinite Dragonflight, as the story has her; her true shape is the bronze she was before it.
"""
import math

from story_common import (BOTH, ALLIANCE, HORDE, TAKEN, DONE, TURNED_IN, MORATARI, SCENE, OUTING, TIME_JUMP, WEIGHT_OF_TIME,
                          STRANGERS, INTO_THE_DRAGONBLIGHT_A, INTO_THE_DRAGONBLIGHT_H, rewarded)

# This file's quests (77900-77999: RemixGuide.cpp leaves them out of "your next quest")
TEA, SHORE_LEAVE, DINNER, WYRMREST_VIEW, WHAT_HE_LEFT_OUT, WINGS, ADVENTURE, TENT, AFTER = range(77901, 77910)
# Told her at the Bazaar's campfire that they're a time jumper (RemixCampfire.cpp): her quests open one after another without
# the war's checkpoints (WrathRemix.h: QUEST_ROMANCE_TIME_JUMPER)
TIME_JUMPER = 77910
FLAGS = [(TIME_JUMPER, "A Time Jumper", "You told Moratari you are a time jumper: her story opens without waiting for the war's.")]

# The main story's checkpoints that open them
TIME_FOR_HEROES, DEFENSE_OF_WARSONG_HOLD = 11727, 11596          # the third quest of each side's Borean Tundra
NOT_YET_LATE, THE_CONDEMNED_COAST = 77043, 77054                 # the middle of it
SHORTER_PATH_A, SHORTER_PATH_H = 77301, 77311                    # Chapter III
HUNTING_EXPEDITION, VERY_LONG_ROAD = 77501, 77601                # Chapters V and VI
ARMIES_IN_PLACE_A, ARMIES_IN_PLACE_H = 77701, 77711              # Chapter VII
LAST_NECESSARY_BATTLE, SEE_YOU_LATER, BACK_TO_YOUR_OWN_TIME = 77800, 77801, 77802
LOST_AT_SEA, RECORD_KEEPS_WARSONG = 77048, 77230

# Credits, and Moratari as these scenes have her (WrathRemix.h: NPC_MORATARI_DRESS and on)
C_TEA, C_SHORE_LEAVE, C_DINNER, C_WYRMREST, C_LOVE, C_WINGS, C_PICNIC, C_TENT, C_PROMISE = range(770700, 770709)
IN_HER_DRESS, IN_HER_TENT, HER_TRUE_SHAPE, LAZY_CROCOLISK = 770720, 770721, 770722, 770723
ACT_MORATARI = 770013                      # as the story's scenes have her (wrath_remix_world_0002_npcs.sql)
MANGAL_CROCOLISK = 28002
PLAYER = 255
BACK = math.pi                             # facing the way the anchor looks from, i.e. at the Timerunner

SPELL_TELEPORT_VISUAL = 51347
EMOTE_TALK, EMOTE_BOW, EMOTE_CHEER, EMOTE_LAUGH, EMOTE_KISS, EMOTE_SHY = 1, 2, 4, 11, 17, 24
STAND, SIT = 0, 1

# Races, for the words she has about them (ChrRaces' masks)
HUMAN, ORC, DWARF, NIGHT_ELF, UNDEAD, TAUREN, GNOME, TROLL, BLOOD_ELF, DRAENEI = 1, 2, 4, 8, 16, 32, 64, 128, 512, 1024

# Her looks (remix_look; ClientPatch.cpp writes them into the game's patch): her own (display 25458,
# a blood elf woman's figure with clothes 17276) in an evening dress (the Lovely Red Dress), and as she
# is in her tent (a loose shirt). The server's copies of the tables as well.
HER_DISPLAY, HER_CLOTHES = 25458, 17276
DRESS_LOOK, TENT_LOOK = 32755, 32756
SERVER_DISPLAY = dict(model=2209, sound=0, scale=1.25, alpha=255, blood_level=1, blood=0, npc_sound=292, particles=0, geosets=0,
                      effects=0)
SERVER_CLOTHES = dict(race=10, sex=1, skin=15, face=2, hair_style=11, hair_color=4, facial_hair=2, flags=0)
LOOKS = [
    # (head, shoulders, shirt, chest, belt, legs, boots, wrists, gloves, tabard, cloak)
    dict(display=DRESS_LOOK, from_display=HER_DISPLAY, extra=21382, from_extra=HER_CLOTHES,
         items=[0, 0, 0, 34726, 0, 0, 0, 0, 0, 0, 0], server_display=SERVER_DISPLAY, server_extra=SERVER_CLOTHES),
    dict(display=TENT_LOOK, from_display=HER_DISPLAY, extra=21383, from_extra=HER_CLOTHES,
         items=[0, 0, 12327, 0, 0, 0, 0, 0, 0, 0, 0], server_display=SERVER_DISPLAY, server_extra=SERVER_CLOTHES),
]

CREATURES = [
    dict(entry=C_TEA, name="Tea shared with Moratari", credit=True),
    dict(entry=C_SHORE_LEAVE, name="A drink with Moratari", credit=True),
    dict(entry=C_DINNER, name="Dinner at Krasus' Landing", credit=True),
    dict(entry=C_WYRMREST, name="The view from Wyrmrest", credit=True),
    dict(entry=C_LOVE, name="Moratari comforted", credit=True),
    dict(entry=C_WINGS, name="A flight on Moratari's back", credit=True),
    dict(entry=C_PICNIC, name="An afternoon by the river", credit=True),
    dict(entry=C_TENT, name="A night in Moratari's tent", credit=True),
    dict(entry=C_PROMISE, name="Moratari's promise", credit=True),
    dict(entry=IN_HER_DRESS, **{"from": ACT_MORATARI}, display=DRESS_LOOK, why="Moratari in her evening dress (the romance's scenes)"),
    dict(entry=IN_HER_TENT, **{"from": ACT_MORATARI}, display=TENT_LOOK, why="Moratari in her tent (the romance's scene)"),
    dict(entry=HER_TRUE_SHAPE, **{"from": 31696}, name="Moratari", subname="Infinite Dragonflight", unit_flags=770,
         why="Moratari in her true shape, atop Wyrmrest (a bronze drake: the bronze she was before the Infinite)"),
    dict(entry=LAZY_CROCOLISK, **{"from": MANGAL_CROCOLISK}, faction=35, unit_flags=770, lootid=0,
         why="The crocolisks on the sunny bank of the picnic's river (a scene's, never fought)"),
]

# Where she walks with them: on their afternoon in Sholazar, and everywhere after her tent.
COMPANION = [
    dict(side=BOTH, **{"from": TENT}, until=BACK_TO_YOUR_OWN_TIME, why="After her tent: everywhere, until they go home"),
]

# ---- Her tent at the Bazaar ------------------------------------------------------------------
# The tent stands on the level ground south-east of the heart (data/bazaar_ground.tsv: flat for eight yards
# round, eighteen yards clear of everything else), its door towards her post; what is in it is seen in the
# world's phase and the private outing's (1 | 32768), so it is there inside and out.
TENT_X, TENT_Y, TENT_Z = 6413.0, 1853.0, 508.6
TENT_O = math.atan2(1871.0 - TENT_Y, 6385.0 - TENT_X)    # facing her post
INWARD = TENT_O + math.pi                                 # from the door towards the back
PHASE_BOTH = 1 | 32768


def tent_spot(forward, left):
    """A spot in the tent: yards in from its middle (towards its back wall) and to the left."""
    return (TENT_X + forward * math.cos(INWARD) - left * math.sin(INWARD),
            TENT_Y + forward * math.sin(INWARD) + left * math.cos(INWARD))


OBJECT_TEMPLATES = [
    dict(entry=770100, display=7194, name="Moratari's Tent"),
    dict(entry=770101, display=159, name="Rug"),
    dict(entry=770102, display=5914, name="Cushions"),
    dict(entry=770103, display=6644, name="Candle"),
    dict(entry=770104, display=6038, name="Lantern"),
    dict(entry=770105, display=194, name="Brazier"),
]
OBJECTS = [
    dict(guid=7705300, entry=770100, x=TENT_X, y=TENT_Y, z=TENT_Z, o=TENT_O, phase=PHASE_BOTH, why="Moratari's tent, the Bazaar"),
    *[dict(guid=g, entry=e, x=tent_spot(f, l)[0], y=tent_spot(f, l)[1], z=TENT_Z + 0.02, o=TENT_O + turn, phase=PHASE_BOTH, why=why)
      for g, e, f, l, turn, why in (
          (7705301, 770101, 0.5, 0.0, 0.0, "her tent's rug"),
          (7705302, 770102, 3.4, -1.0, 0.3, "cushions in her tent"),
          (7705303, 770102, 3.6, 1.0, -0.4, "cushions in her tent"),
          (7705304, 770102, 2.6, 2.6, 1.2, "cushions in her tent"),
          (7705305, 770103, 4.2, -2.4, 0.0, "a candle in her tent"),
          (7705306, 770103, 4.4, 2.2, 0.0, "a candle in her tent"),
          (7705307, 770103, -1.8, 2.8, 0.0, "a candle in her tent"),
          (7705308, 770105, -0.6, -2.8, 0.0, "her tent's brazier"),
      )],
    # (the lamp that is always lit, by the door)
    dict(guid=7705309, entry=770104, x=tent_spot(-6.6, 1.6)[0], y=tent_spot(-6.6, 1.6)[1], z=TENT_Z, o=TENT_O, phase=PHASE_BOTH,
         why="the lamp by her tent's door"),
]

# ---- The outings -------------------------------------------------------------------------------
INN_A, INN_H, KRASUS_LANDING, WYRMREST_TOP, ON_HER_BACK, HER_TENT, BY_THE_RIVER, EDGE_OF_THE_CAMP = 1, 2, 3, 4, 5, 6, 7, 8
SCENE_INN_A, SCENE_INN_H, SCENE_DINNER, SCENE_WYRMREST, SCENE_WINGS, SCENE_TENT, SCENE_PICNIC, SCENE_PROMISE, SCENE_KISS = range(901, 910)
DALARAN_FLIGHT_POINT, WYRMREST_FLIGHT_POINT = 310, 252
BRONZE_DRAKE_MOUNT = 25833

OUTINGS = [
    # A Hero's Welcome, six yards in front of Amisi Azuregaze, facing into the room.
    dict(id=INN_A, name="Cider at A Hero's Welcome, Dalaran", x=5851.0, y=640.6, z=647.6, o=1.05, scene=SCENE_INN_A),
    # The Filthy Animal, six yards in front of Uda the Beast.
    dict(id=INN_H, name="Cider at The Filthy Animal, Dalaran", x=5886.9, y=513.7, z=641.7, o=1.87, scene=SCENE_INN_H),
    dict(id=KRASUS_LANDING, name="Dinner at Krasus' Landing, Dalaran", x=5806.0, y=444.0, z=658.8, o=4.45, scene=SCENE_DINNER),
    dict(id=WYRMREST_TOP, name="Atop Wyrmrest Temple, at night", x=3528.0, y=268.0, z=342.8, o=2.40, scene=SCENE_WYRMREST),
    # From Dalaran's flight point to Wyrmrest's, on her back; her words on the way.
    dict(id=ON_HER_BACK, name="On her back, from Dalaran to Wyrmrest Temple", x=5816.0, y=447.0, z=658.8, o=4.45, scene=SCENE_WINGS,
         flight=(DALARAN_FLIGHT_POINT, WYRMREST_FLIGHT_POINT, BRONZE_DRAKE_MOUNT),
         lines=[(4000, "Lean with me. Not that way. ...There."),
                (14000, "The Violet Citadel, behind us. The Kirin Tor are at war with the blue dragonflight this year; let us hope "
                        "their sentries know a bronze when they see one."),
                (28000, "Crystalsong. The trees ring when the wind is right. Listen."),
                (44000, "You are holding on tightly. I do not mind."),
                (62000, "Wyrmrest. Every dragon comes here in the end, to sleep. I wanted you to see it the way we do: from above, "
                        "and arriving."),
                (80000, "Down we go. And not one mage shot at us. A successful first flight, I would say.")]),
    # Her tent: no one else in it (a phase of its own), their gear unseen.
    dict(id=HER_TENT, name="Moratari's tent, the Bazaar", x=TENT_X, y=TENT_Y, z=TENT_Z + 0.1, o=INWARD, scene=SCENE_TENT, private=True,
         undress=True),
    # A sunny bank of the river below Nesingwary's camp in Sholazar (a crocolisk's; surveyed floor), theirs alone: the
    # river's own crocolisks would kill a time jumper of a low level.
    dict(id=BY_THE_RIVER, name="An afternoon by the river, Sholazar Basin", x=5551.8, y=5850.3, z=-74.6, o=2.0, scene=SCENE_PICNIC,
         private=True),
    # The edge of Crusaders' Pinnacle in Icecrown, by the cliff, theirs alone (a phase of its own: no one comes this far).
    dict(id=EDGE_OF_THE_CAMP, name="The edge of the camp, Crusaders' Pinnacle", x=6410.0, y=470.0, z=511.4, o=2.4, scene=SCENE_PROMISE,
         private=True),
]

# ---- The quests ----------------------------------------------------------------------------------
COMMON = dict(side=BOTH, sort=0, level=-1, min=10, bronze=300)

QUESTS = [
    dict(COMMON, id=TEA, title="A Cup of Something Hot",
         gates=[[rewarded(TIME_FOR_HEROES)], [rewarded(DEFENSE_OF_WARSONG_HOLD)]],
         log="Sit with Moratari, and share her tea.",
         desc="I have been taking notes on you since the landing, $N: how you fight, what you eat, which way you turn when something "
              "growls. It occurs to me that you have none on me.$B$BYou ask me where the Scourge will be, and when, and how many. "
              "Sensible questions. Nobody ever asks a dragon anything else.$B$BSit with me a while. I have tea. Every dragon who keeps "
              "time keeps tea; it is the one thing that tastes the same in every century.",
         done="Return to Moratari.",
         objectives=[(C_TEA, 1, "Tea shared with Moratari")],
         request="The tea is in no hurry, $N, and neither am I.",
         reward="Thank you, $N. I had forgotten what it is like to be asked about myself.$B$BAsk me something again sometime. I may have "
                "a better answer by then."),
    dict(COMMON, id=SHORE_LEAVE, title="Shore Leave", prev=TEA,
         gates=[[rewarded(NOT_YET_LATE)], [rewarded(THE_CONDEMNED_COAST)]],
         log="Have a drink with Moratari at an inn in Dalaran.",
         desc="Eternus says we are ahead of the record. Two days, perhaps three. She says it as if it were a problem.$B$BI say it is "
              "shore leave. There is an inn in Dalaran (in this year the city has only just arrived, and the floors are still settling) "
              "where nobody knows either of us, and the cider is better than it has any right to be.$B$BOne drink, $N. As friends. "
              "Mostly as friends.",
         done="Return to Moratari.",
         objectives=[(C_SHORE_LEAVE, 1, "A drink with Moratari")],
         request="I have already decided what I am having. That should tell you how long I have been thinking about this.",
         reward="One drink, as promised. I made no promises about the rest of it.$B$BThank you, $N. I have not enjoyed an evening that "
                "much in... I was going to say a century. I think it may have been longer."),
    dict(COMMON, id=DINNER, title="Dinner at Krasus' Landing", prev=SHORE_LEAVE, bronze=500,
         gates=[[rewarded(INTO_THE_DRAGONBLIGHT_A)], [rewarded(INTO_THE_DRAGONBLIGHT_H)]],
         log="Have dinner with Moratari at Krasus' Landing in Dalaran.",
         desc="I have a confession. I bought a dress.$B$BIn the Bazaar you can buy anything from any year. I tried on eleven. I have "
              "chosen between whole centuries with less fuss.$B$BThere is a landing on the edge of Dalaran named for "
              "Krasus, a dragon who sat on the Kirin Tor's council for years in an elf's shape, and hardly anyone knew. I have always "
              "thought he would understand me.$B$BHave dinner with me there, $N. Properly. Not as friends.",
         done="Return to Moratari.",
         objectives=[(C_DINNER, 1, "Dinner at Krasus' Landing")],
         request="The dress is ready. I am nearly ready. Give me a moment to stop being nervous.",
         reward="<Moratari touches her lips, as if to make sure they are still hers.>$B$BI have changed history before, $N. I know "
                "exactly what it feels like.$B$BIt feels like that.$B$BI am keeping the dress."),
    dict(COMMON, id=WYRMREST_VIEW, title="The View from Wyrmrest", prev=DINNER,
         gates=[[rewarded(STRANGERS)]],
         log="Go with Moratari to the top of Wyrmrest Temple at night.",
         desc="You were on Wyrmrest today, among the Accord's dragons, and I kept my distance. Dragons always know another dragon, "
              "whatever shape she wears, and Chromie has met enough of the Infinite this week.$B$BBut there is something I want to "
              "show you there, $N, from the top of the temple, at night, when the Accord is asleep. Come with me.",
         done="Return to Moratari.",
         objectives=[(C_WYRMREST, 1, "The view from Wyrmrest")],
         request="Not yet? That is all right. I am still working up my courage.",
         reward="I was so sure you would step back. I had a speech ready for it.$B$BWould you like to hear it? No? Good. It was a "
                "terrible speech."),
    dict(COMMON, id=WHAT_HE_LEFT_OUT, title="What Eternus Left Out", prev=WYRMREST_VIEW,
         gates=[[rewarded(WEIGHT_OF_TIME)]],
         log="Stay with Moratari a while.",
         desc="I need to sit down.$B$B...She knew, $N. Eternus knew the war had to happen as it did, and she sent us to change it "
              "anyway, and she let me believe that every life we saved was a life kept.$B$BI do not know what I am anymore. A keeper of "
              "time who spent a month vandalizing it.$B$BSit with me a while. Please. You do not have to say anything.",
         done="Return to Moratari.",
         objectives=[(C_LOVE, 1, "Moratari comforted")],
         reward="Thank you for staying.$B$BTomorrow we start putting things back, one at a time. I will find a way to do it without "
                "losing anyone. I have to.$B$BFor now, I would like to sit here a little longer, with you, and not take a single note."),
    dict(COMMON, id=WINGS, title="On Bronze Wings", prev=WHAT_HE_LEFT_OUT, bronze=500,
         gates=[[rewarded(SHORTER_PATH_A)], [rewarded(SHORTER_PATH_H)]],
         log="Fly with Moratari from Dalaran to Wyrmrest Temple, on her back.",
         desc="You have flown on gryphons, and wyverns, and the Accord's drakes, and every one of them was carrying you somewhere "
              "for the war.$B$BI am offering something else, $N: my back, the sky over Dalaran, and the long way down to Wyrmrest, "
              "with nowhere we have to be when we land.$B$BI have never carried anyone before. I find I would like to.",
         done="Return to Moratari.",
         objectives=[(C_WINGS, 1, "A flight on Moratari's back")],
         request="I have been stretching my wings all morning, and pretending I was not.",
         reward="My wings ache, and I cannot stop smiling. I had forgotten that flying could be for nothing but the flying.$B$BNext "
                "time, we do not land."),
    dict(COMMON, id=ADVENTURE, title="An Adventure of Our Own", prev=WINGS,
         gates=[[rewarded(HUNTING_EXPEDITION)]],
         log="Spend an afternoon with Moratari by a river in Sholazar Basin.",
         desc="I have followed you through a great many other people's stories. Today I would like one of our own.$B$BThere is a "
              "river below Nesingwary's camp, warm and slow, with one good bank in the sun. There are also crocolisks, who believe that "
              "bank is theirs. I have brought a blanket and a basket. Shall we discuss it with them?",
         done="Return to Moratari.",
         objectives=[(C_PICNIC, 1, "An afternoon by the river")],
         request="There is sand in the basket already. There is always sand in my baskets.",
         reward="Somewhere tomorrow, about noon, two crocolisks are going to be very confused.$B$BThank you, $N. I did not know I "
                "could still have a day like that."),
    dict(COMMON, id=TENT, title="The Lamp That Is Always Lit", prev=ADVENTURE, bronze=500,
         gates=[[rewarded(VERY_LONG_ROAD)]],
         log="Spend the night in Moratari's tent at the Bazaar.",
         desc="I have a tent at the Bazaar. You have walked past it a hundred times: the one with the lamp that is always lit.$B$BNo one "
              "goes in. Not Eternus, when she was there; not the porters who sweep the paths. It is the only place in any year that is "
              "only mine.$B$BI would like it to be ours, tonight. Leave your armor at the door, $N. Nothing in there will need a sword.",
         done="Return to Moratari.",
         objectives=[(C_TENT, 1, "A night in Moratari's tent")],
         reward="<Moratari is humming. She notices, stops, and then starts again.>$B$BFrom now on I walk with you. Everywhere. Let my "
                "posts stand empty and look mysterious without me."),
    dict(COMMON, id=AFTER, title="Whatever Comes After", prev=TENT, bronze=1000,
         gates=[[rewarded(ARMIES_IN_PLACE_A)], [rewarded(ARMIES_IN_PLACE_H)]],
         log="Walk with Moratari to the edge of the camp, and hear her promise.",
         desc="Icecrown. The end of the war is up that glacier, and after the end you go home, to your own year. I cannot follow you "
              "there, $N. One of my kind who walks out of her own time does not come back, and someone has to stay behind and send you "
              "home.$B$BI am not sad. I am... a little sad.$B$BWalk with me to the edge of the camp. I want to make you a promise, and I "
              "would rather not make it in front of Tirion.",
         done="Return to Moratari.",
         objectives=[(C_PROMISE, 1, "Moratari's promise")],
         reward="<Moratari brushes the frost from your shoulders, though there was hardly any.>$B$BNow. There is a king at the top of "
                "that glacier, and he has kept you waiting long enough. Shall we?"),
]

# A time jumper's quests open without the war's checkpoints, still one after another (each one's prev).
for _quest in QUESTS:
    _quest["gates"] = _quest["gates"] + [[rewarded(TIME_JUMPER)]]

# ---- What can be said to her -------------------------------------------------------------------
LOOKING = [
    (HUMAN, "Humans change so quickly. I look away for a season, and you are someone else. I am trying to remember you exactly as "
            "you are now."),
    (DWARF, "You have tea in your $Gbeard:hair;. No, leave it. It suits you."),
    (NIGHT_ELF, "I was in Zin-Azshari once, before the Sundering. Your people blushed exactly like that, even then. I am glad some "
                "things kept."),
    (GNOME, "I am trying to decide whether to kneel down or to pick you up. Both seem rude."),
    (DRAENEI, "Your tail has been tapping the ground since I sat down. Is that a good sign? Tell me it is a good sign."),
    (ORC, "Your tusks. I was wondering how anyone... Never mind. It was purely academic. Drink your tea."),
    (UNDEAD, "Your hands are cold. Here, hold the cup. No, hold it longer. There."),
    (TAUREN, "You are holding that tiny cup as if it were a baby bird. I find that I like that very much."),
    (TROLL, "You have been grinning since I poured. They say trolls grin at everything. I hope they are wrong, and it is only me."),
    (BLOOD_ELF, "I am checking my work. I borrowed this shape from your people, and I have always wondered whether I got the ears "
                "right. I did, as it happens. Do not let it go to your head."),
]
LOVELY = [
    (HUMAN, "Your people say that as if you had all the time in the world. I like that about you. Say it again tomorrow."),
    (DWARF, "The titans made your people out of stone, you know. It shows: you said that as if it cost you something. Thank you."),
    (NIGHT_ELF, "I have heard your people say that to the moon. I did not know they said it to anyone else."),
    (GNOME, "Say it again, louder. I am all the way up here."),
    (DRAENEI, "Your tail is doing the thing again. I have decided it is my favorite thing."),
    (ORC, "An orc paying compliments. Somewhere, Garrosh just felt a chill and does not know why."),
    (UNDEAD, "You say that without even breathing. It is a very efficient compliment. I accept it."),
    (TAUREN, "In all my records, I have never once caught a tauren flattering anyone. So I suppose I must believe you."),
    (TROLL, "Dat's what ya say to all de dragons, mon? ...I am sorry. I have wanted to try the accent for weeks."),
    (BLOOD_ELF, "Of course I do. So do you. We are a very good-looking pair, and everyone in the Bazaar is annoyed about it."),
]
assert sum(r for r, _ in LOOKING) == sum(r for r, _ in LOVELY) == 1791  # every race of the game, once

TALK = [
    # A Cup of Something Hot: what she is asked, over tea (and how she looks back, by race)
    dict(key="romance_tea", npc=MORATARI, quest=TEA,
         option="Sit with her, and take the cup she offers.",
         reply="<Moratari pours two cups from a pot that was not there a moment ago.>$B$BCareful. It is hot. It has been hot for about "
               "four hundred years; I keep it in a pocket of an afternoon in Tanaris.$B$BWell? Ask me something."),
    dict(npc=MORATARI, parent="romance_tea", quest=TEA, option="How old are you, really?",
         reply="That depends on how you count. About ten thousand years, but not all of them in order, and a few of them twice. Next "
               "question."),
    dict(npc=MORATARI, parent="romance_tea", quest=TEA, option="Is it true that dragons sleep on gold?",
         reply="Only in stories. My kind sleeps on sand: soft, warm, and in your scales for the rest of your life. Next question."),
    *[dict(npc=MORATARI, parent="romance_tea", quest=TEA, races=race, option="You keep looking at me.", reply=f"{words}")
      for race, words in LOOKING],
    dict(npc=MORATARI, parent="romance_tea", quest=TEA, credit=C_TEA, option="What do you do when you're not working?",
         reply="I... read. I keep records, and when I have finished keeping them, I read them.$B$B<Moratari looks at you over the rim of "
               "her cup for a long moment.>$B$BThat is a dreadful answer, is it not? I think I would like a better one. Perhaps you could "
               "help me find it."),
    # Shore Leave: to the inn (each side's own)
    dict(npc=MORATARI, quest=SHORE_LEAVE, side=ALLIANCE, action=OUTING, param=INN_A, option="One drink, then. A Hero's Welcome?"),
    dict(npc=MORATARI, quest=SHORE_LEAVE, side=HORDE, action=OUTING, param=INN_H, option="One drink, then. The Filthy Animal?"),
    # The dates
    dict(npc=MORATARI, quest=DINNER, action=OUTING, param=KRASUS_LANDING, option="I'd love to. Show me this landing."),
    dict(npc=MORATARI, quest=WYRMREST_VIEW, action=OUTING, param=WYRMREST_TOP, option="Show me."),
    dict(npc=MORATARI, quest=WINGS, action=OUTING, param=ON_HER_BACK, option="I'm ready. Take me flying."),
    dict(npc=MORATARI, quest=ADVENTURE, action=OUTING, param=BY_THE_RIVER, option="Lead the way. I'll carry the basket."),
    dict(npc=MORATARI, quest=TENT, action=OUTING, param=HER_TENT, option="Take me to your tent."),
    dict(npc=MORATARI, quest=AFTER, action=OUTING, param=EDGE_OF_THE_CAMP, option="Walk with her to the edge of the camp."),
    # What Eternus Left Out: staying with her
    dict(key="romance_stay", npc=MORATARI, quest=WHAT_HE_LEFT_OUT,
         option="Sit beside her, and take her hand.",
         reply="<Moratari's hand is warm, and shaking.>$B$BEvery one of them was real, $N. Every soldier who walked off that tundra "
               "because we were there. I wrote down all their names.$B$BAnd now I have to help put the record back. Tell me I am not a "
               "monster."),
    dict(key="romance_monster", npc=MORATARI, parent="romance_stay", quest=WHAT_HE_LEFT_OUT,
         option="You're not a monster. You gave them more time than history ever did.",
         reply="More time. <She laughs, wetly.> That is such a dragon thing to say. Where did you learn to talk like a dragon?"),
    dict(npc=MORATARI, parent="romance_monster", quest=WHAT_HE_LEFT_OUT, credit=C_LOVE,
         option="From you. I love you, Moratari.",
         reply="<For a long moment, Moratari says nothing at all.>$B$BI have watched people say that to each other for ten thousand "
               "years. I never once thought anyone would say it to me.$B$B...I love you too. I think I have since the tea. I do not know "
               "what this does to the record, and for once I do not care."),
    # Afterwards, whenever they like
    *[dict(npc=MORATARI, after=SHORE_LEAVE, races=race, option="Tell her she looks lovely today.", reply=words)
      for race, words in LOVELY],
    dict(npc=MORATARI, after=DINNER, action=SCENE, param=SCENE_KISS, option="Kiss her."),
    # At the Bazaar's campfire, as she sits there with them (RemixCampfire.cpp), and only then: her story from its start.
    dict(npc=MORATARI, before=TIME_JUMPER, action=TIME_JUMP, option="I'm a time jumper. I already know where this goes between us, "
                                                                    "and I don't want to wait.",
         reply="<Moratari laughs, a real one, surprised out of her.>$B$BA time jumper. Of course you are. You have read ahead, to the "
               "pages with me in them.$B$BVery well. I will not make you wait for the war's permission. Some of what we do will not have "
               "happened yet, for you. Humor me, and pretend it has."),
]

# ---- The scenes (tools/scenes.py writes them) -------------------------------------------------------
# Each stands where the Timerunner stands (anchor 0), facing as they face.
SCENES = [
    dict(id=SCENE_INN_A, name="Shore Leave: cider at A Hero's Welcome", quest=0, trigger=0, anchor=0, credit=C_SHORE_LEAVE, steps=[
        ("summon", 1, ACT_MORATARI, 1.8, 0.4, BACK),
        ("wait", 1200),
        ("say", 1, "I asked for two ciders, and the innkeeper asked which of us was the hero. I pointed at you. She gave me the larger "
                   "cup anyway."),
        ("emote", 1, EMOTE_LAUGH),
        ("say", 1, "The Silver Covenant by the door cannot work out whether I am one of theirs or a Sunreaver. I am letting them "
                   "wonder."),
        ("say", 1, "To shore leave, then. And to two days the war will never miss."),
        ("emote", 1, EMOTE_CHEER),
        ("emote", PLAYER, EMOTE_CHEER),
        ("wait", 1500),
        ("say", 1, "You have cider on your lip. No, the other side. ...Here."),
        ("text_emote", 1, "brushes your lip with her thumb, then looks at the thumb as if it has done something without asking her."),
        ("say", 1, "That was very forward of my thumb. I shall have words with it."),
        ("emote", 1, EMOTE_SHY),
        ("text_emote", 1, "kisses you on the cheek, quickly, before either of you can think about it."),
        ("say", 1, "Come on. Before I do something else without asking myself first."),
    ]),
    dict(id=SCENE_INN_H, name="Shore Leave: cider at The Filthy Animal", quest=0, trigger=0, anchor=0, credit=C_SHORE_LEAVE, steps=[
        ("summon", 1, ACT_MORATARI, 1.8, 0.4, BACK),
        ("wait", 1200),
        ("say", 1, "Uda says we may drink, feast and rest, but if we fight, she will feed us to her wolves. I like her enormously."),
        ("emote", 1, EMOTE_LAUGH),
        ("say", 1, "Her wolves have names, you know. Nargut and Rhukah. I asked. She looked at me as if nobody ever had."),
        ("say", 1, "To shore leave. Lok'tar, as they say here. ...Uda says I said it like an elf."),
        ("emote", 1, EMOTE_CHEER),
        ("emote", PLAYER, EMOTE_CHEER),
        ("wait", 1500),
        ("say", 1, "Mind your cup; somebody just walked into our table. Here."),
        ("text_emote", 1, "puts her hand over yours to steady the cup, and leaves it there a little longer than the cup needs."),
        ("say", 1, "The table has stopped moving, $N. I am aware that my hand has not."),
        ("emote", 1, EMOTE_SHY),
        ("text_emote", 1, "kisses you on the cheek, quickly, while Uda is looking the other way."),
        ("say", 1, "Come on. Before Uda decides that counts as fighting."),
    ]),
    dict(id=SCENE_DINNER, name="Dinner at Krasus' Landing", quest=0, trigger=0, anchor=0, credit=C_DINNER, steps=[
        ("summon", 1, IN_HER_DRESS, 2.0, 0.0, BACK),
        ("wait", 1800),
        ("say", 1, "Well? You are allowed to look. I spent an hour on it; somebody ought to."),
        ("emote", 1, EMOTE_SHY),
        ("say", 1, "And you look $Ghandsome:beautiful; in this light. I am not supposed to notice things like that. I noticed."),
        ("face_angle", 1, math.pi * 0.5),
        ("say", 1, "Crystalsong below us, the Dragonblight beyond it, and at the edge of it all, the citadel. Its owner was not "
                   "invited."),
        ("say", 1, "I have stood on this landing in a hundred different years, $N. I have never once stood here with anyone."),
        ("face", 1, PLAYER),
        ("say", 1, "May I tell you something a scholar of variables should never say? I do not want to know how this ends. Not this. I "
                   "want to find out."),
        ("wait", 1000),
        ("emote", 1, EMOTE_KISS),
        ("emote", PLAYER, EMOTE_KISS),
        ("text_emote", 1, "leans in and kisses you, slowly, the way someone does who has thought about it for a long time and has decided "
                          "to stop thinking."),
        ("wait", 2500),
        ("say", 1, "...Oh."),
        ("say", 1, "Well. That is going to be very hard to put back."),
    ]),
    dict(id=SCENE_WYRMREST, name="The View from Wyrmrest: her true shape", quest=0, trigger=0, anchor=0, credit=C_WYRMREST, steps=[
        ("summon", 1, ACT_MORATARI, 2.0, 1.0, BACK),
        ("wait", 1200),
        ("say", 1, "Up here the Accord cannot hear us, and the wind takes everything else. Good."),
        ("say", 1, "You have only ever seen me like this. Small, polite, pointed ears. It is a shape I wear to talk to people. I want you "
                   "to see the rest of me."),
        ("say", 1, "Do not run. Everyone runs."),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 700),
        ("despawn", 1),
        ("summon", 2, HER_TRUE_SHAPE, 7.0, 0.0, BACK),
        ("cast", 2, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 2500),
        ("text_emote", 2, "lowers her great head until one eye is level with yours. It is the color of old bronze, and it is very "
                          "nervous."),
        ("wait", 2000),
        ("say", 2, "This is me. The shape I hatched in, before I was Infinite: bronze, like Chromie."),
        ("say", 2, "...You are still here."),
        ("cast", 2, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 700),
        ("despawn", 2),
        ("summon", 3, ACT_MORATARI, 2.0, 1.0, BACK),
        ("wait", 1200),
        ("face", 3, PLAYER),
        ("say", 3, "You did not run."),
        ("text_emote", 3, "takes your hand, and does not let go of it for a long while."),
    ]),
    dict(id=SCENE_WINGS, name="On Bronze Wings: up from Dalaran", quest=0, trigger=0, anchor=0, credit=C_WINGS, steps=[
        ("summon", 1, ACT_MORATARI, 2.0, 0.0, BACK),
        ("wait", 1200),
        ("say", 1, "Hold on to the ridge along my neck. Not the frills. The frills are ticklish, and I will drop you, and I will feel "
                   "terrible."),
        ("say", 1, "And do not look down until we are over the forest. After that, look at everything."),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 800),
        ("despawn", 1),
    ]),
    dict(id=SCENE_TENT, name="The Lamp That Is Always Lit: her tent", quest=0, trigger=0, anchor=0, credit=C_TENT, steps=[
        ("summon", 1, IN_HER_TENT, 2.0, 0.5, BACK),
        ("wait", 1800),
        ("say", 1, "No armor. Good. I have only ever seen you dressed for a war. I wanted to see you without one."),
        ("emote", 1, EMOTE_SHY),
        ("say", 1, "Oh, do not look at me like that. I am a dragon. We are not shy. ...I am a little shy."),
        ("say", 1, "I lit that lamp the night I first came to the Bazaar, and I have never let it go out. I never knew who I was "
                   "keeping it lit for. Sit with me, $N."),
        ("emote", 1, EMOTE_KISS),
        ("emote", PLAYER, EMOTE_KISS),
        ("text_emote", 1, "draws you down beside her among the cushions, and reaches over to turn down the lamp."),
        ("fade", 9000, "The lamp burns low. Outside, the Bazaar goes on selling yesterday to tomorrow. Inside, for once, nobody is "
                       "counting the hours."),
        ("wait", 1500),
        ("say", 1, "Good morning."),
        ("say", 1, "I have written down a great many mornings in my time. Other people's. Not one of them got it right; I shall have to "
                   "revise the record."),
        ("emote", 1, EMOTE_LAUGH),
        ("say", 1, "Go on, then. Your armor is by the door, and the war is waiting. We should not keep it."),
    ]),
    dict(id=SCENE_PICNIC, name="An Adventure of Our Own: by the river", quest=0, trigger=0, anchor=0, credit=C_PICNIC, steps=[
        ("summon", 2, LAZY_CROCOLISK, 7.0, -2.0, BACK),
        ("summon", 3, LAZY_CROCOLISK, 8.5, 1.5, BACK - 0.4),
        ("summon", 1, ACT_MORATARI, 1.5, 1.5, BACK),
        ("wait", 1200),
        ("face", 1, 2),
        ("say", 1, "The sunny bank, and two crocolisks who think it is theirs. Gentlemen, I am sorry. Tomorrow, about noon. You will not even "
                   "notice."),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 2),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 3),
        ("wait", 700),
        ("despawn", 2),
        ("despawn", 3),
        ("face", 1, PLAYER),
        ("say", 1, "There. One blanket, one basket, and a riverbank with nobody on it but us."),
        ("say", 1, "I brought pastries from a bakery in Dalaran that will not open for another forty years. Do not tell the baker."),
        ("emote", 1, EMOTE_LAUGH),
        ("say", 1, "Do you know, this is the first day since the tundra that nobody has needed saving? I have been trying to think what "
                   "people do with a day like this. Then I remembered."),
        ("text_emote", 1, "takes your hand, turns it over, and traces the lines of your palm with one finger, as if reading a map she has "
                          "not seen before."),
        ("say", 1, "Your life line is a long one, $N. ...No, I have not looked it up. I promised myself I never would."),
    ]),
    dict(id=SCENE_PROMISE, name="Whatever Comes After: her promise", quest=0, trigger=0, anchor=0, credit=C_PROMISE, steps=[
        ("summon", 1, ACT_MORATARI, 2.0, 1.0, BACK),
        ("wait", 1200),
        ("say", 1, "Here. The wind off the glacier is cold enough that nobody comes this far from the fires."),
        ("say", 1, "I have been trying to work out what to say to you up here since Sholazar. I wrote it down, and then I tore it up, "
                   "which is a terrible thing for a scholar to do to her notes."),
        ("say", 1, "So, without notes: I am going to make you a promise, $N, and I am going to keep it."),
        ("face", 1, PLAYER),
        ("say", 1, "I will write to you. Wherever you are in your own year, a letter from me will find you. Time lets letters through; "
                   "it is only people it argues with."),
        ("say", 1, "And whatever comes after, in your year or in mine: you were never a variable to me. Not from the first cup of tea."),
        ("emote", 1, EMOTE_KISS),
        ("emote", PLAYER, EMOTE_KISS),
        ("text_emote", 1, "kisses you as the wind comes down off the glacier, and for a moment it is not cold at all."),
        ("wait", 2500),
        # (in her own voice: Legion Remix's, tools/voices.py)
        ("say", 1, "Well, then we'll simply have to make the most of the time we have, won't we?"),
        ("wait", 800),
    ]),
    # Whenever they like, after their dinner: the Moratari nearest them (beside them, or at her post).
    dict(id=SCENE_KISS, name="A kiss", quest=0, trigger=0, anchor=0, steps=[
        ("bind", 1, MORATARI),
        ("face", 1, PLAYER),
        ("emote", 1, EMOTE_KISS),
        ("emote", PLAYER, EMOTE_KISS),
        ("text_emote", 1, "kisses you, and smiles against your mouth."),
    ]),
]

# ---- Her words, as the story goes ---------------------------------------------------------------
WORDS = [
    (TEA, TAKEN, BOTH, "Sit. Here, out of the wind."),
    (SHORE_LEAVE, TAKEN, BOTH, "One drink. I will hold you to one. You may hold me to two."),
    (DINNER, TAKEN, BOTH, "Do not look at the dress yet. Look when we get there. I want to see your face."),
    (WYRMREST_VIEW, TAKEN, BOTH, "At night the Accord sleeps on the lower tiers. The top is only wind."),
    (WINGS, TAKEN, BOTH, "Eat something light first, and tie down anything you would like to keep."),
    (ADVENTURE, TAKEN, BOTH, "Leave the map in your pack today. We are getting lost on purpose."),
    (ADVENTURE, DONE, BOTH, "Look at that. An afternoon with nothing left to do in it."),
    (TENT, TAKEN, BOTH, "Come whenever you like. The lamp is lit; it always is."),
    (AFTER, TAKEN, BOTH, "Not far. Just past the last fire, where the wind is."),
    # The main story, for those walking hers too
    (WEIGHT_OF_TIME, TAKEN, BOTH, "Stay close to me today, $N. I do not know why. I only know I want you close.",
     dict(after=WYRMREST_VIEW)),
    (LOST_AT_SEA, TURNED_IN, ALLIANCE, "We are putting back what we did. Not all of it, though. Not us.",
     dict(after=WHAT_HE_LEFT_OUT, delay=9000)),
    (RECORD_KEEPS_WARSONG, TURNED_IN, HORDE, "We are putting back what we did. Not all of it, though. Not us.",
     dict(after=WHAT_HE_LEFT_OUT, delay=9000)),
    (LAST_NECESSARY_BATTLE, TAKEN, BOTH, "If you die up there, I will be cross with you for a thousand years. I can, you know. I have "
                                         "them.", dict(after=TENT)),
    (SEE_YOU_LATER, TAKEN, BOTH, "I have always preferred hello to goodbye. So I will say what everyone says, $N: see you later. I "
                                 "intend to mean it.", dict(after=AFTER)),
    (BACK_TO_YOUR_OWN_TIME, TAKEN, BOTH, "When you are home, look in your mailbox. I keep my promises, $N. I always have.",
     dict(after=AFTER)),
]
