"""The Dragonblight and the bronze, up to WRM-204, while Moratari and Eternus steer the war (STORY.md,
"Moratari in the war"; tools/story.py writes it).

- Alliance: WRM-223 The Second Sky (Wintergarde's dispositions for Naxxramas's next blows: the
  archers off the square, the mine road closed, the gryphons off the cracked roost); The Noble's
  Crypt (Necrolord Amarion) put on the road before Chromie's summons; a 7th Legion company sent to
  Bolvar at Fordragon Hold, which the High Commander recalls once the Timerunner has met Sylvanas
  (WRM-201 says so).
- Horde: WRM-236 Eyes and Ears (a word for Saurfang's son, through Messenger Torvus); WRM-234
  Before the Second Wave (the cultists empowering the blightbeasts over Icemist, and the road to
  Venomspite the game leaves out); WRM-235 A Careful Inventory (what the Royal Apothecary Society's
  people let slip about the blight: evidence the Timerunner must never show anyone of this year).
- The bronze: Moratari waits outside the time storm (no immortal may enter), her words on
  Nozdormu, and one of the Infinite who was watching the Timerunner, not the hourglass.
"""
from story_common import (ALLIANCE, HORDE, BOTH, TAKEN, DONE, TURNED_IN, ZONE_DRAGONBLIGHT, STRANGERS, WEIGHT_OF_TIME,
                          rewarded, not_rewarded)

# The game's people
WYRMBANE, URIK, DURKON, LYNORE, LEORIC = 27136, 27317, 27318, 27155, 27156
AGMAR, JUKTOK, TORVUS, SINTAR, MIDDLETON, MOLDER, LAWRENCE = 26379, 26415, 26649, 26505, 27172, 27320, 27846
ANUBAR_CULTIST = 26319
CHROMIE = 27856

# The game's quests
FALL_OF_WINTERGARDE, FLIGHT_OF_THE_DEFENDER, RETURN_TO_THE_HIGH_COMMANDER, RESCUE_FROM_TOWN_SQUARE, FIND_DURKON, NOBLES_CRYPT = (
    12235, 12237, 12251, 12253, 12309, 12311)
VICTORY_NEARS, FROM_THE_DEPTHS, IMBECILES_ABOUND, HOW_NOT_TO_DIE, EMERALD_TEARS, SPREAD_THE_GOOD_WORD, THE_FORSAKEN_BLIGHT = (
    12034, 12036, 12189, 12188, 12200, 12218, 12221)
MYSTERY_OF_THE_INFINITE = 12470
ROAD_TO_ANGRATHAR_A, ROAD_TO_ANGRATHAR_H, SUMMONS_A, SUMMONS_H = 77201, 77211, 77203, 77213
HOUR_OF_THE_GATE_H = 77218

# This file's quests
SECOND_SKY, BEFORE_THE_SECOND_WAVE, CAREFUL_INVENTORY, EYES_AND_EARS = 77223, 77234, 77235, 77236

# Credits and new creatures
C_LYNORE, C_LEORIC, C_URIK, C_TORVUS, C_MOLDER, C_LAWRENCE = 770580, 770581, 770582, 770583, 770584, 770585
LEGION_COMPANY, INFINITE_WATCHER = 770590, 770591

SCENE_INFINITE_NOTICES = 201

CREATURES = [
    dict(entry=C_LYNORE, name="Commander Lynore Windstryke warned", credit=True),
    dict(entry=C_LEORIC, name="Highlord Leoric Von Zeldig warned", credit=True),
    dict(entry=C_URIK, name="Gryphon Commander Urik warned", credit=True),
    dict(entry=C_TORVUS, name="A word sent with Messenger Torvus", credit=True),
    dict(entry=C_MOLDER, name="Deathguard Molder asked about the blight spreaders", credit=True),
    dict(entry=C_LAWRENCE, name="Junior Apothecary Lawrence asked about the shipments", credit=True),
    dict(entry=LEGION_COMPANY, **{"from": 27162}, name="7th Legion Sentinel", subname="Wintergarde's company", unit_flags=770,
         why="The company Wyrmbane sends to Bolvar at Fordragon Hold, until he recalls it"),
    dict(entry=INFINITE_WATCHER, **{"from": 27898}, name="Infinite Chrono-Magus", unit_flags=770,
         why="One of the Infinite, watching the Timerunner atop Wyrmrest (a scene's)"),
]

UNTIL_RECALLED = not_rewarded(ROAD_TO_ANGRATHAR_A)
SPAWNS = [
    # Moratari beside Chief Plaguebringer Middleton at Venomspite while A Careful Inventory is hers to give.
    dict(guid=7704384, entry=770001, x=3225.2, y=-730.9, z=168.1, o=2.51, equip=0,
         visible=[[rewarded(SPREAD_THE_GOOD_WORD), not_rewarded(THE_FORSAKEN_BLIGHT)]], why="Moratari beside Middleton, Venomspite"),
    dict(guid=7704380, entry=LEGION_COMPANY, x=4690.5, y=1504.0, z=261.0, o=0.46, visible=[[rewarded(NOBLES_CRYPT), UNTIL_RECALLED]],
         why="Wintergarde's company at Fordragon Hold"),
    dict(guid=7704381, entry=LEGION_COMPANY, x=4692.0, y=1500.5, z=261.0, o=0.46, visible=[[rewarded(NOBLES_CRYPT), UNTIL_RECALLED]],
         why="Wintergarde's company at Fordragon Hold"),
    dict(guid=7704382, entry=LEGION_COMPANY, x=4687.5, y=1501.5, z=260.8, o=0.46, visible=[[rewarded(NOBLES_CRYPT), UNTIL_RECALLED]],
         why="Wintergarde's company at Fordragon Hold"),
    dict(guid=7704383, entry=LEGION_COMPANY, x=4691.3, y=1502.3, z=261.0, o=0.46, visible=[[rewarded(NOBLES_CRYPT), UNTIL_RECALLED]],
         why="Wintergarde's company at Fordragon Hold"),
]

COMMON_A = dict(side=ALLIANCE, sort=ZONE_DRAGONBLIGHT, level=-1, min=20, bronze=800)
COMMON_H = dict(side=HORDE, sort=ZONE_DRAGONBLIGHT, level=-1, min=20, bronze=800)

QUESTS = [
    dict(COMMON_A, id=SECOND_SKY, title="The Second Sky", prev=FLIGHT_OF_THE_DEFENDER,
         log="Warn Commander Lynore Windstryke, Highlord Leoric Von Zeldig and Gryphon Commander Urik of what Naxxramas will do next.",
         desc="The lower village is lost. Naxxramas fell on it before either of us set foot here, and that I cannot undo, $N.$B$B"
              "But I know where the next blows land. The risen gryphon riders will dive on the archers posted over the town square. The "
              "dead will come up the mine road. And the roost that should have fallen is still standing, thanks to Eternus, but nobody "
              "has mended the beam. When it goes, it goes with the gryphons in it.$B$BTell the commander, the highlord and the gryphon "
              "commander. A veteran's eye, a hunch, a rumor from the barracks: whatever they will believe.",
         done="Return to Moratari.",
         objectives=[(C_LYNORE, 1, "Commander Lynore Windstryke warned"), (C_LEORIC, 1, "Highlord Leoric Von Zeldig warned"),
                     (C_URIK, 1, "Gryphon Commander Urik warned")],
         request="Did they listen?",
         reward="The commander believed you. The gryphon commander believed his birds. The highlord believed no one, and closed the road "
                "anyway.$B$BEternus will be pleased. So, I find, am I."),
    dict(COMMON_H, id=EYES_AND_EARS, title="Eyes and Ears", prev=VICTORY_NEARS, ender=TORVUS,
         log="Send a word to High Overlord Saurfang with Messenger Torvus at Agmar's Hammer.",
         desc="Messenger Torvus carries Saurfang's letters, the ones Agmar is not meant to read. Saurfang has sent his son to command the "
              "Horde at the Wrathgate, and you know how the son's story ends.$B$BSend a word back with Torvus. Not what you know, $N. "
              "What any old soldier might say to a father, if he had the nerve. Let Saurfang read it, and decide.",
         done="Speak with Messenger Torvus.",
         objectives=[(C_TORVUS, 1, "A word sent with Messenger Torvus")],
         reward="<Messenger Torvus clasps your hand, and the note is gone into his glove.>$B$B<He raises his voice for anyone listening.> "
                "The Hammer stands strong, soldier! Warsong Hold will hear of it!$B$B<Under his breath.> It goes west with me tonight. "
                "What the High Overlord does with it is for him to decide."),
    dict(COMMON_H, id=BEFORE_THE_SECOND_WAVE, title="Before the Second Wave", prev=FROM_THE_DEPTHS, ender=SINTAR,
         log="Slay 8 Anub'ar Cultists at Icemist Village, then speak with Doctor Sintar Malefious at Agmar's Hammer.",
         desc="The Anub'ar razed Icemist, and its taunka are refugees now. Nothing I can do will give them back their village.$B$BBut I "
              "can take something from the Anub'ar. Their cultists are on the ruins, pouring their power into the blightbeasts. The "
              "Horde's wind riders will bring down the beasts you can see. In the record, the cultists raise a second wave after them, "
              "and that one reaches the Wrathgate.$B$BKill the cultists before they finish. Then come back to Agmar's Hammer: Doctor "
              "Malefious is waiting on a shipment, and I want you to see it before he does.",
         done="Speak with Doctor Sintar Malefious at Agmar's Hammer.",
         objectives=[(ANUBAR_CULTIST, 8, "")],
         request="<Doctor Malefious does not look up.> You are standing in my light.",
         reward="Cultists, at Icemist? How very heroic. I'm sure Agmar will want a song.$B$B<Doctor Malefious looks you over.>$B$BStill, "
                "you went there and came back with all your limbs, which puts you ahead of everyone else I work with. I have an errand "
                "for you."),
    dict(COMMON_H, id=CAREFUL_INVENTORY, title="A Careful Inventory", prev=SPREAD_THE_GOOD_WORD,
         log="Ask Deathguard Molder and Junior Apothecary Lawrence at Venomspite about the blight's shipments, then return to Moratari.",
         desc="Before you carry Middleton's package to Agmar's Hammer, I want you to take an inventory, $N.$B$BDeathguard Molder asked for "
              "the blight spreaders and was told they were for 'special missions'. Junior Apothecary Lawrence signs for every crate that "
              "leaves Venomspite. Ask them, the way a courier making conversation would.$B$BAnd whatever you learn stays with you. No one "
              "in this year can hear it from you: not Agmar, not the Warchief, not anyone.",
         done="Return to Moratari.",
         objectives=[(C_MOLDER, 1, "Deathguard Molder asked about the blight spreaders"),
                     (C_LAWRENCE, 1, "Junior Apothecary Lawrence asked about the shipments")],
         request="Well? What did they tell you?",
         reward="More blight than Agmar ever ordered, consigned to 'the Grand Apothecary's special detachment'. Spreaders kept back for "
                "'special missions'. And a Chief Plaguebringer who keeps saying 'the living' when he means the Scourge.$B$BSay nothing, $N, "
                "to anyone. Eternus has a plan for the Wrathgate, and I think, now, I understand what it is for."),
]

GATES = {
    RETURN_TO_THE_HIGH_COMMANDER: [[rewarded(SECOND_SKY)]],
    FROM_THE_DEPTHS: [[rewarded(EYES_AND_EARS)]],
    IMBECILES_ABOUND: [[rewarded(BEFORE_THE_SECOND_WAVE)]],
    THE_FORSAKEN_BLIGHT: [[rewarded(CAREFUL_INVENTORY)]],
}

TEXTS = {
    NOBLES_CRYPT: dict(
        reward="That's the attack from inside stopped. And with the mine road shut and the archers off the roofs, the attacks from outside "
               "aren't bleeding us like they were. The High Commander says that's enough: he's sending a company to Lord Fordragon. They "
               "march for Fordragon Hold at first light.$B$B<Durkon looks at you for a long moment.>$B$BYou went straight down to the "
               "bottom chamber, $Glad:lass;, like you knew the way. Lucky guess, I'll call it."),
}

TALK = [
    # WRM-223
    dict(npc=LYNORE, quest=SECOND_SKY, credit=C_LYNORE,
         option="Commander, the riders who fell over the lower village will dive on the square next. Get your archers off the roofs "
                "before they do.",
         reply="<Commander Lynore Windstryke follows your gaze to the rooftops around the square.>$B$BThose riders flew from this keep. "
               "They know where we post our archers because we taught them.$B$BVery well, $c. They come off the roofs before dark."),
    dict(npc=LEORIC, quest=SECOND_SKY, credit=C_LEORIC,
         option="Highlord, close the mine road. The dead will come up it before the week is out.",
         reply="Close the mine road? On whose authority?$B$B<Highlord Leoric Von Zeldig glares at you, then at Siege Engineer Quarterflash, "
               "who only shrugs.>$B$B...Mine, I suppose. The mine is lost already, and my miners dig for the Scourge now. I'll not have "
               "them walking up my road as well. Consider it closed."),
    dict(npc=URIK, quest=SECOND_SKY, credit=C_URIK,
         option="Gryphon Commander, the roost that cracked won't hold much longer. Move your birds tonight.",
         reply="<Gryphon Commander Urik looks up at the cracked beam, and his face falls.>$B$BThe birds have known for days. They won't "
               "settle up there, and I've been calling it nerves.$B$BAll right, friend. They come down and sleep in the yard. They'll "
               "sulk about it for a week, and I'll let them."),
    # WRM-236
    dict(npc=TORVUS, quest=EYES_AND_EARS, credit=C_TORVUS,
         option="Tell Saurfang this, from me: I have seen sons die proving themselves to their fathers. His should not lead the charge "
                "himself.",
         reply="<Messenger Torvus is quiet for a moment.>$B$BSaurfang the Younger needs no nursemaid, and he would not thank you for this. "
               "But it is not meant for him, is it?$B$BWrite it small, and give it to me with a handshake. The Kor'kron watch anyone who "
               "stands near me too long."),
    # WRM-235
    dict(npc=MOLDER, quest=CAREFUL_INVENTORY, credit=C_MOLDER,
         option="Deathguard, those blight spreaders by the east gate. What are they being saved for?",
         reply="Saved for? 'Special missions'! <Deathguard Molder spits.>$B$BFive spreaders, loaded and sealed, and the Grand Apothecary's "
               "own people sitting on them day and night. Meanwhile I've the Onslaught's ballistae to break, and I'm out picking bombs "
               "off Scourge siegesmiths like a common grave robber.$B$BWhatever they're saving them for, it had better be worth it."),
    dict(npc=LAWRENCE, quest=CAREFUL_INVENTORY, credit=C_LAWRENCE,
         option="Apothecary, I'm counting crates for Agmar's Hammer. How much of the blight is going there?",
         reply="Agmar's Hammer? Only the specimen. One crate, yes. <Junior Apothecary Lawrence pulls his ledger closer.>$B$BThe rest goes "
               "to the Grand Apothecary's special detachment, up at the ga-- up north. I'm not to say where. I wasn't to say that, "
               "either.$B$BYou won't mention it? No. No, of course you won't. Of course."),
]

SCENES = [
    # Mystery of the Infinite, as it's turned in: one of the Infinite was watching the Timerunner.
    dict(id=SCENE_INFINITE_NOTICES, name="Mystery of the Infinite: the Infinite notices", quest=MYSTERY_OF_THE_INFINITE, trigger=2, anchor=CHROMIE,
         steps=[
             ("bind", 1, CHROMIE),
             ("summon", 2, INFINITE_WATCHER, 14.0, 9.0, 3.14),
             ("face", 2, 255),
             ("wait", 2500),
             ("face", 1, 2),
             ("say", 1, "Don't turn around. Well, not quickly. There's one of them at the edge of the platform."),
             ("say", 1, "That one isn't interested in the hourglass, $N. It's been watching you."),
             ("cast", 2, 52096, 0),
             ("wait", 1200),
             ("despawn", 2),
             ("face", 1, 255),
             ("say", 1, "Gone. Well, so much for breaking it to you gently."),
         ]),
]

WORDS = [
    # Alliance
    (FALL_OF_WINTERGARDE, TAKEN, ALLIANCE, "Wintergarde. You have seen it once already, the morning I showed you. Now you see it from the "
                                           "walls."),
    (FLIGHT_OF_THE_DEFENDER, TAKEN, ALLIANCE, "'I picked a bad day to stop drinking!' Someone says it every time. Not always the same "
                                              "someone."),
    (FLIGHT_OF_THE_DEFENDER, TURNED_IN, ALLIANCE, "Wanting is not mending. Look at the beam above the gryphons, $N. Find me at the crypt "
                                                  "before you go back to the High Commander.", dict(delay=4000)),
    (SECOND_SKY, TAKEN, ALLIANCE, "Lynore is with the High Commander. Leoric is up the hill with the gnome engineer, and Urik is at the "
                                  "roost, where you left him."),
    (RESCUE_FROM_TOWN_SQUARE, TAKEN, ALLIANCE, "The geists in that square were Wintergarde's own people, not long ago. They do not know they "
                                               "are hunting their neighbors. Bring out whoever you can."),
    (FIND_DURKON, TURNED_IN, ALLIANCE, "Necrolord Amarion is at the bottom of that crypt, raising the nobles buried there. Left alone, he "
                                       "has days down there, and days are a long time in a crypt. Go now."),
    (NOBLES_CRYPT, TAKEN, ALLIANCE, "The shadow beside the necrolord is Thel'zan's; the Duskbringer himself keeps to the mausoleum. That "
                                    "fight comes later. You will win it."),
    (NOBLES_CRYPT, TURNED_IN, ALLIANCE, "A company to Fordragon Hold. The way history went, Wintergarde never spared Bolvar a single blade. "
                                        "This time he will have a hundred more at his back.", dict(delay=5000)),
    # Horde
    (VICTORY_NEARS, TAKEN, HORDE, "Agmar speaks for Hellscream here, and his Kor'kron listen for anyone who doesn't."),
    (EYES_AND_EARS, TAKEN, HORDE, "Torvus is the orc by the burning brazier, waiting for nobody in particular."),
    (FROM_THE_DEPTHS, TAKEN, HORDE, "The Pit of Narjun opens onto Azjol-Nerub. The nerubian at its edge is Kilix: not everything down there "
                                    "serves the Lich King. One day he will ask you to kill Anub'arak for him. Try to look as if it is the "
                                    "first time."),
    (BEFORE_THE_SECOND_WAVE, TAKEN, HORDE, "Icemist is west, at the foot of the mountains. Look for the cultists with their hands raised to "
                                           "the beasts overhead."),
    (BEFORE_THE_SECOND_WAVE, TURNED_IN, HORDE, "Malefious is a Grand Apothecary, as Putress is. That proves nothing about him. Watch what you "
                                               "carry for him all the same.", dict(delay=4000)),
    (IMBECILES_ABOUND, TAKEN, HORDE, "Venomspite is on the far eastern edge of the Dragonblight. Middleton runs the blight works there; you "
                                     "will know him by how pleased he is with himself."),
    (HOW_NOT_TO_DIE, TAKEN, HORDE, "The specters on that beach were Prince Arthas's men, the ones he stranded when he burned his ships. They "
                                   "have waited a long time for someone to come for them. I doubt this is what they hoped for."),
    (EMERALD_TEARS, TAKEN, HORDE, "Middleton has never watched a dragon die. I have. Take the tears, and do not make a joke of it."),
    (SPREAD_THE_GOOD_WORD, TAKEN, HORDE, "The dead you will be testing it on came out of Wintergarde's mausoleum. Somebody in that keep "
                                         "buried every one of them."),
    (CAREFUL_INVENTORY, TAKEN, HORDE, "Molder is across the yard, by the alchemists. Lawrence is the one with the ledger, among the braziers "
                                      "near Middleton."),
    (THE_FORSAKEN_BLIGHT, TURNED_IN, HORDE, "So Eternus has her vial. Whatever she learns from it, you and I already know what it does. We saw "
                                            "the Wrathgate after.", dict(delay=4000)),
    # The bronze
    (MYSTERY_OF_THE_INFINITE, TAKEN, BOTH, "The storm keeps her out as well as me. Something in common at last. I will wait at its edge, "
                                           "$N."),
    (MYSTERY_OF_THE_INFINITE, DONE, BOTH, "The hourglass answered her question, $N. It will be years before she believes the answer. It took "
                                          "me longer."),
    (MYSTERY_OF_THE_INFINITE, TURNED_IN, BOTH, "The Lord of Time was shown his own ending, long ago, and he has spent ages refusing it. If he "
                                               "may refuse one, Eternus says, so may we.",
     dict(delay=16000)),
    (STRANGERS, TAKEN, BOTH, "Mind the ambassadors on that platform, $N. Dragons listen better than they pretend to."),
    # After the turn: the word sent to Saurfang never arrived.
    (HOUR_OF_THE_GATE_H, TAKEN, HORDE, "Your note to Varok never left Agmar's Hammer. The Kor'kron searched Torvus before he could go, and "
                                       "Agmar burned what they found. I went and looked, $N. I was glad. I am not proud of it.",
     dict(after=EYES_AND_EARS)),
]
