"""After the turn: putting back what the record cannot keep (STORY.md, "Moratari in the war"; tools/story.py
writes it).

The future Sylvanas has told the Timerunner the war must happen as it did, and at the turn Moratari
learned what Eternus left out. She asks the Timerunner to help her put back what they changed
together, without taking back a single life:

- WRM-048 Lost at Sea: William Allerton, alive and asking questions about Unit S, sails home under
  another name; the ledger keeps him dead at Farshire.
- WRM-049 Forged Orders: Unit S's freed men and Hammerhill's volunteers are sent home to Stormwind's
  harbor; the record keeps Unit S lost at the landing.
- WRM-230 The Record Keeps Warsong: after the Wrathgate, the coast's garrison, the spare tanks and the
  plains' wounded go back to Orgrimmar under the Warchief's martial law; and Garrosh's lesson breaks
  at his friend's son's armour.

Wintergarde's company at Fordragon Hold is recalled by the High Commander himself (WRM-201's text, in
wrath_remix_world_0011_chapter2.sql); the word sent to Saurfang never reaches his son (Agmar burned
it: a whisper in story_dragonblight.py). After Angrathar, the end of Chapter II, waits for those of
these that put back something the Timerunner changed.
"""
from story_common import (ALLIANCE, HORDE, TAKEN, DONE, TURNED_IN, WEIGHT_OF_TIME, MORATARI, OBJECTIVES_DONE, IN_PROGRESS, rewarded,
                          not_rewarded, state)
from story_borean_alliance import (NOT_YET_LATE, NO_ONE_LEFT_BEHIND, LOST_AT_SEA, FORGED_ORDERS, LIVING_ALLERTON, VENN)
from story_borean_horde import (THE_CONDEMNED_COAST, RECORD_KEEPS_WARSONG, GORGE, GARROSH, SAURFANG, DARKNESS_STIRS)

AFTER_ANGRATHAR_A, AFTER_ANGRATHAR_H = 77221, 77222
BAZAAR = (571, 6394.0, 1866.0, 508.7, 1.57)

C_ALLERTON_SAILS, C_VENN_ORDERS, C_GORGE_RECALL = 770600, 770601, 770602
SCENE_LESSON_BREAKS = 152

CREATURES = [
    dict(entry=C_ALLERTON_SAILS, name="William Allerton persuaded to sail home", credit=True),
    dict(entry=C_VENN_ORDERS, name="Corporal Venn given the orders", credit=True),
    dict(entry=C_GORGE_RECALL, name="Gorge told of the recall", credit=True),
]

# She waits where she took the Timerunner, to take them back: by Allerton in the mine and on Gorge's
# beach she already stands (WRM-006's, WRM-016's); at Death's Stand, only while Forged Orders is in hand.
SPAWNS = [
    dict(guid=7704385, entry=MORATARI, x=3106.5, y=3839.5, z=22.8, o=0.47, equip=0,
         visible=[[state(FORGED_ORDERS, IN_PROGRESS | OBJECTIVES_DONE)]], why="Moratari at Death's Stand while Forged Orders is in hand"),
]

QUESTS = [
    dict(id=LOST_AT_SEA, title="Lost at Sea", side=ALLIANCE, sort=3537, level=-1, min=20, bronze=1000,
         gates=[[rewarded(WEIGHT_OF_TIME), rewarded(NOT_YET_LATE)]],
         log="Persuade William Allerton, in the Farshire Mine, to sail home under another name. Moratari will take you there and back.",
         desc="I need your help to put something back, $N, and you are not going to like it.$B$BWilliam Allerton was supposed to die in "
              "the Farshire mine. He did not, because of us. Now he is alive in the Borean Tundra, writing letters to Stormwind about Unit "
              "S, about the counselor, about a hero with a strange way of knowing where to be. Every letter pulls the war somewhere it "
              "never went.$B$BHe cannot stay. Not here, and not under his own name. But he does not have to die. I will not ask that of "
              "you, and I would not do it myself. Talk to him.",
         done="Return to Moratari.",
         departure=(571, 2765.6, 5337.8, 30.03, 0.20),
         bridge=dict(at=BAZAAR),
         objectives=[(C_ALLERTON_SAILS, 1, "William Allerton persuaded to sail home")],
         request="Will he go?",
         reward="The Kraken sails at dawn, with a passenger the ledger has never heard of. In Westfall, a farmer called Will Allard will "
                "grow very good corn, and tell nobody where he learned to look over his shoulder.$B$BThank you, $N. That one I could not "
                "have done alone."),
    dict(id=FORGED_ORDERS, title="Forged Orders", side=ALLIANCE, sort=3537, level=-1, min=20, bronze=1000,
         gates=[[rewarded(WEIGHT_OF_TIME), rewarded(NO_ONE_LEFT_BEHIND)]],
         log="Give Corporal Venn at Death's Stand the orders that send Unit S's survivors and Hammerhill's volunteers home.",
         desc="History lost Unit S on the beach where they landed, and never went looking. If four of them walk back into Valiance Keep "
              "with the counselor's name on their lips, the questions the Expedition asks next are ones history never asked.$B$BThey are "
              "not going to die for that. I will not allow it. But they can go home, quietly: I have written orders sending them to "
              "Stormwind's harbor, with Hammerhill's volunteers to see them aboard. They carry the general's seal. The counselor kept a "
              "copy in his desk, and he will not be needing it.$B$BTake them to Corporal Venn. He will understand more than you think.",
         done="Return to Moratari.",
         departure=(571, 3111.0, 3840.0, 22.85, 5.75),
         bridge=dict(at=BAZAAR),
         objectives=[(C_VENN_ORDERS, 1, "Corporal Venn given the orders")],
         request="Did he take them?",
         reward="Then the record keeps Unit S on its beach, and Stormwind gets its sons back. Somewhere in the Old Town, a mother is going "
                "to open her door to a boy the army already wrote to her about.$B$BSome changes, $N, the war can keep, as long as it never "
                "hears of them."),
    dict(id=RECORD_KEEPS_WARSONG, title="The Record Keeps Warsong", side=HORDE, sort=3537, level=-1, min=20, bronze=1000,
         gates=[[rewarded(WEIGHT_OF_TIME), rewarded(DARKNESS_STIRS), rewarded(THE_CONDEMNED_COAST)]],
         log="Tell Gorge, on the Coast of Echoes, that the Warchief is calling every soldier who can walk back to Orgrimmar. Moratari will "
             "take you there and back.",
         desc="Orgrimmar is under martial law, and the Warchief is calling every soldier who can walk back to the city. In the record, "
              "the coast at Garrosh's Landing is condemned again by the end of the week: no garrison, no spare tanks, no one on the beach "
              "but Gorge, a goblin and the mist.$B$BThere is a garrison there now, because of us. If it stays while the rest of the Horde "
              "goes home, someone will ask why, and I would rather nobody did, $N.$B$BGo and tell Gorge. He will take it badly. He takes "
              "everything badly.",
         done="Return to Moratari.",
         departure=(571, 2822.5, 6708.5, 10.8, 2.70),
         bridge=dict(at=BAZAAR),
         objectives=[(C_GORGE_RECALL, 1, "Gorge told of the recall")],
         request="Did he take it badly?",
         reward="Condemned again, as it was. The garrison sails for Orgrimmar with the spare tanks, and the wounded go with them. History "
                "has its coast back.$B$BI keep thinking of the war map, the day Hellscream gave way and did not stamp on anything. It was "
                "real, $N. For one afternoon, it was real."),
]

# After Angrathar waits for each undoing only where its intervention was made: Lost at Sea for whoever
# saved Allerton (Not Yet Late), Forged Orders for whoever freed Unit S (No One Left Behind), The Record
# Keeps Warsong for whoever held the coast (The Condemned Coast). The Howling Fjord, or the Borean
# Tundra's own quests, leave nothing to put back; and the undoings are offered only after the turn
# (WRM-207), so whoever never saw it isn't held for them.
GATES = {
    AFTER_ANGRATHAR_A: [[not_rewarded(WEIGHT_OF_TIME)],
                        [rewarded(LOST_AT_SEA), rewarded(FORGED_ORDERS)],
                        [rewarded(LOST_AT_SEA), not_rewarded(NO_ONE_LEFT_BEHIND)],
                        [not_rewarded(NOT_YET_LATE), rewarded(FORGED_ORDERS)],
                        [not_rewarded(NOT_YET_LATE), not_rewarded(NO_ONE_LEFT_BEHIND)]],
    AFTER_ANGRATHAR_H: [[not_rewarded(WEIGHT_OF_TIME)], [rewarded(RECORD_KEEPS_WARSONG)], [not_rewarded(THE_CONDEMNED_COAST)]],
}

TALK = [
    dict(npc=LIVING_ALLERTON, quest=LOST_AT_SEA, credit=C_ALLERTON_SAILS,
         option="William, the cult will try again, and next time I won't be there. Sail home tonight, under another name.",
         reply="Another name? <William Allerton laughs, then stops.> You're serious.$B$BSo as far as the Expedition knows, I died down here. "
               "...Fine. Leryssa has her brother back. That's what I wrote to her for.$B$BI always fancied myself a farmer. Somewhere warm, "
               "where the ground doesn't open up under you."),
    dict(npc=VENN, quest=FORGED_ORDERS, credit=C_VENN_ORDERS,
         option="Corporal, these orders send your men home to Stormwind. The record will say Unit S was lost at the landing. Nobody will "
                "come looking.",
         reply="Lost at the landing. <Corporal Venn reads the orders twice, then a third time.>$B$BWell. We were, weren't we? For a while "
               "there.$B$BGeneral's seal, and not the general's hand. That's how we got sent out here in the first place.$B$B'S' for "
               "suicide, the lads called it. Maybe now it's 'S' for 'sent home'. I'll take it, friend, and I won't ask who wrote it."),
    dict(npc=GORGE, quest=RECORD_KEEPS_WARSONG, credit=C_GORGE_RECALL,
         option="Gorge, the Warchief is calling every soldier who can walk back to Orgrimmar. The garrison too, and the spare tanks.",
         reply="Orgrimmar? Martial law, they're sayin'... <Gorge spits into the sand.>$B$BCondemned again, then. Figures. Every time I get "
               "this beach lookin' like somethin', somebody takes it away.$B$BFine! Take 'em, buddy! But the six tanks stay with me. "
               "Somebody's gotta keep an eye on that mist."),
]

SCENES = [
    # Darkness Stirs, as it's turned in (Saurfang's son's armour): Garrosh's lesson breaks.
    dict(id=SCENE_LESSON_BREAKS, name="Darkness Stirs: the lesson breaks", quest=DARKNESS_STIRS, trigger=2, anchor=SAURFANG,
         steps=[
             ("wait", 6000),
             ("bind", 1, GARROSH),
             ("bind", 2, SAURFANG),
             ("face", 1, 2),
             ("say", 1, "Your son died at the Wrathgate, old one, while we stood at this map arguing over shipping lanes."),
             ("say", 2, "Not today, Garrosh."),
             ("say", 1, "No. No more waiting. When the Horde marches on Icecrown, it marches on my word, not yours."),
         ]),
]

WORDS = [
    (LOST_AT_SEA, TAKEN, ALLIANCE, "The mine. He has moved his cot down to the bottom level, where the light is worse and the knives have "
                                   "further to climb."),
    (FORGED_ORDERS, TAKEN, ALLIANCE, "Death's Stand. Venn has kept them there a week, waiting for orders nobody was ever going to send."),
    (RECORD_KEEPS_WARSONG, TAKEN, HORDE, "The coast. Gorge is by the tanks; he always is."),
    (DARKNESS_STIRS, TURNED_IN, HORDE, "And there goes the patience he learned. History needs him angry, $N. I wish it needed something "
                                       "else.",
     dict(after=WEIGHT_OF_TIME, delay=24000)),
]
