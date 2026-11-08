# SPDX-License-Identifier: GPL-3.0-or-later
"""The Old Brewery (a Community Project, opened by Brill Endures: tools/town/endures.py): Brewmaster Oren
Blackbarrel, who brewed in Brill before the plague, brings his family's brewhouse beside the Gallows' End back to
work, with Calla Fenn (a sarcastic apprentice with a gift for fungal cultures), Bram Lusk (a cooper with no barrels
to make since the plague) and Marta Greaves (the Wayfarer's Rest's innkeeper, who argues with Oren over prices).

Five quests: the brewhouse cleared, its rats killed and Oren's ledger found (his father's ale in it); the copper,
staves and hoops for the vats and the first casks; three experimental batches and three tasters (a choice: the
recipe Oren refines); the spoiled batch (no saboteur: a rot in the cellar's walls); the opening (a choice: the
signature drink's name: Gravemalt Stout, Lordaeron Reserve or Blackroot Bitter). Then the weekly Brewer's Special,
and the house's barrel stand and drinks cabinet.

The town changes a stage at a time (tools/town/README.md, "Projects"): the boarded brewhouse (a closed Duskwood
farmhouse) and Oren at its door (1); barriers, Bram's cooperage (2); the vats, the furnace and shelves in the yard,
the chimney smoking by day (3); the tasting counter, the beer garden and a pavilion over Calla's tubs (4); the cellar's vent and
racks, sample barrels at the market (5); the brewhouse open (the farmhouse, its counter and kegs), its people's day,
Oren's deliveries to the Gallows' End and his quarrels at the caravan office (6); the house's furnishings (7).

The brewhouse stands at (2217, 278) turned 25 degrees, its door toward the road and the Gallows' End, its floor
36.08; its yard's heights are the terrain's (map tile 0002731). Marta stands at the Wayfarer's Rest's door, the
caravan office's building (tools/town/caravan.py), in her tent until it's built."""

RENEE, HAMLIN, DILLINGER, ZYGAND, BURGESS = 5688, 3547, 1496, 1515, 1652
SALDEAN = 33996        # William Saldean, Grain & Feed, by the smithy
OLIVER_DWOR = 2136     # Apprentice Weaponsmith, by the smithy
CAROLAI = 2132

FLOOR = 36.08          # the brewhouse's floor (its farmhouse's)

LINE = {
    "title": "The Old Brewery",
    "stages": [["R:endures.endures"], ["R:q1"], ["R:q2"], ["R:q3"], ["R:q4"], ["R:q5"], ["M:house_set"]],
    "quests": [
        {
            "id": "q1", "title": "The Kegs Are Empty", "giver": "oren_yard", "ender": "oren_yard",
            "log": "Look into the old brewhouse beside the Gallows' End, clear 6 piles of spoiled brewing stores from its yard, "
                   "kill 6 Brewhouse Rats nesting by the cellar hatch behind it and find Oren's old brewing ledger. Then bring "
                   "it to Brewmaster Oren Blackbarrel.",
            "offer": (
                "Don't tell me. You've come to ask what use a brewery is in a town where half the drinkers can't taste and the "
                "other half can't swallow.$B$B"
                "I've heard it. From the Magistrate, from the Deathguard, from a bat. I'll tell you what I told the bat. A "
                "brewery isn't about the beer. It's the work: the malting, the mashing, the waiting, and at the end of it a "
                "room full of people arguing whether it was worth the wait. Brill has nowhere to argue.$B$B"
                "This was my brewhouse, and my father's before me. It's still standing, more or less, but it's full of rot "
                "and rats. Look inside. Clear out what's spoiled, kill whatever's nesting by the cellar, and find my ledger. "
                "Green leather. If the rats have eaten it, I want to know which rat."),
            "progress": "The ledger, $n. Green leather, brass corners. Try not to read it. It's private. It's mostly about barley, "
                        "but it's private.",
            "done": (
                "(Oren turns the pages with great care, as if they might crumble. Some do.)$B$B"
                "Mash temperatures. Hop weights. The year the frost got into the barley... And here. My father's hand. "
                "\"Blackbarrel Brown, for the harvest. Two measures of crystal malt, and don't let the boy near the "
                "hops.\"$B$B"
                "(For a long moment he says nothing at all.)$B$B"
                "He brewed this every autumn. I'd forgotten. I'd forgotten I'd forgotten.$B$B"
                "...Well. Don't stand there. There's a brewery to mend."),
            "return": "Return to Brewmaster Oren Blackbarrel at the old brewhouse in Brill.",
            "objectives": [("credit", "hall_credit", 1, "The old brewhouse looked into"),
                           ("credit", "spoiled_credit", 6, "Piles of spoiled stores cleared"),
                           ("kill", "rat", 6, ""),
                           ("credit", "ledger_credit", 1, "Oren's brewing ledger found")],
            "money": 1200, "xp": 3, "min_level": 10,
        },
        {
            "id": "q2", "title": "A Proper Fermentation", "giver": "bram", "ender": "bram", "prev": "q1",
            "log": "Salvage copper tubing from the goblins' junked pump below the zeppelin tower west of Brill, 6 sound oak "
                   "staves from the rotten casks behind the brewhouse and iron hoops from Oliver Dwor by Brill's smithy, then "
                   "help Bram Lusk repair the 2 fermentation vats and assemble the 3 storage casks in the brewhouse yard.",
            "offer": (
                "Bram Lusk. Cooper. I made the barrels for this brewhouse, and for the Gallows' End, and for every farm "
                "between here and Agamand Mills. Then the plague came, and nobody needed barrels for anything but the one "
                "thing, and those don't have to hold water.$B$B"
                "Oren says the vats can be saved. Oren is half right. The wood's good. The copper's gone: the tubing from the "
                "cooler rotted through, and you can't brew without it. The goblins at the zeppelin tower junked a pump last "
                "spring; there'll be copper in that.$B$B"
                "The old casks out back are rotten, but some staves will still be sound. Pick me six. Oliver Dwor at the "
                "smithy will have hoops if you ask him like you mean it.$B$B"
                "Then we'll see if my hands remember."),
            "progress": "Copper, staves, hoops. A barrel's only three things. That's why it's hard.",
            "done": (
                "(Bram drives the last hoop home and rolls the cask across the yard. It runs true, straight and quiet, and "
                "comes to rest against the wall with a sound like a door closing.)$B$B"
                "Hear that? That's a cask that'll hold. First one in eleven years.$B$B"
                "(He looks at his hands for a while.)$B$B"
                "They remembered."),
            "return": "Return to Bram Lusk at the old brewhouse in Brill.",
            "objectives": [("credit", "tubing_credit", 1, "Copper tubing salvaged"),
                           ("credit", "staves_credit", 6, "Sound oak staves"),
                           ("credit", "hoops_credit", 1, "Iron hoops from Oliver Dwor"),
                           ("credit", "vats_credit", 5, "Vats repaired and casks assembled")],
            "items": [(858, 2)], "money": 1500, "xp": 3, "min_level": 10,
        },
        {
            "id": "q3", "title": "Taste of the Living", "giver": "calla", "ender": "calla", "prev": "q2",
            "log": "Gather 4 bitterroot on the hillside west of Brill, a fungal culture from Hamlin Atkins and brewing grain from "
                   "William Saldean by the smithy; set Calla Fenn's 3 experimental batches going in the brewhouse yard, have "
                   "Hamlin Atkins, Deathguard Dillinger and Executor Zygand taste them, and choose which recipe Oren should "
                   "refine. Then return to Calla.",
            "offer": (
                "Calla Fenn. Apprentice. Allegedly.$B$B"
                "Here's the problem. Oren wants to brew his father's ale exactly as it was. He tasted his first batch "
                "yesterday, and do you know what it tasted of, to him? Nothing. Wet nothing. He threw the mug at the wall. "
                "It's still there; the mug, I mean. It went into the plaster.$B$B"
                "We don't taste like the living, so we shouldn't brew like them. Bitter herbs carry. Some cultures turn grain "
                "into something you can feel at the back of your skull. I've ideas. I need ingredients.$B$B"
                "Bitterroot from the hillside west of town. A culture from Hamlin Atkins's beds; he'll give you the good one if "
                "you praise his blue caps. Grain from William Saldean. Then help me set three batches going, and find three "
                "brave volunteers."),
            "progress": "Bitterroot, culture, grain, three batches, three victims. I mean tasters.",
            "done": (
                "(Calla reads her notes aloud, with feeling.)$B$B"
                "\"Excellent.\" \"Mud.\" \"The first thing I've tasted in years, and I can't decide if that's a compliment.\" "
                "Three batches, three verdicts, no two alike. Science.$B$B"
                "Oren pretended not to listen to any of it, which means he heard every word. He's out back now with your "
                "choice, muttering at it. That's how he shows love.$B$B"
                "We're going to need somewhere for people to sit while they disagree."),
            "return": "Return to Calla Fenn at the old brewhouse in Brill.",
            "objectives": [("credit", "ingredient_credit", 6, "Ingredients gathered"),
                           ("credit", "batch_credit", 3, "Experimental batches set going"),
                           ("credit", "taster_credit", 3, "Townspeople who tasted the batches"),
                           ("credit", "recipe_credit", 1, "A recipe chosen for Oren")],
            "items": [(2593, 3)], "money": 2500, "xp": 4, "min_level": 10,
        },
        {
            "id": "q4", "title": "A Bitter Batch", "giver": "oren_yard", "ender": "oren_yard", "prev": "q3",
            "log": "Examine the 3 spoiled barrels behind the brewhouse, question Bram Lusk and Calla Fenn, go down through the "
                   "cellar hatch and cut out the 3 growths in the brewhouse's back wall, and repair the cellar's vent. Then "
                   "report to Brewmaster Oren Blackbarrel.",
            "offer": (
                "Spoiled. All of it. Forty gallons of the best thing this brewhouse has made since my father died, gone to "
                "slime overnight. Green slime. With hairs.$B$B"
                "Somebody did this, $n. Somebody doesn't want a brewery in Brill: the Gallows' End, maybe, or some apothecary "
                "who fancies my cellar for his jars, or someone closer than that. Calla's been in and out of the cellar with "
                "her cultures all week. I'm not saying it's her. I'm saying her cultures are green.$B$B"
                "Look at the barrels. Ask Bram and Calla what they know, and watch their faces while they answer. Then go down "
                "into the cellar, because whatever started this started there. And fix that vent while you're down; the air's "
                "so foul the rats have moved out."),
            "progress": "Well? Who was it? Don't spare my feelings. I keep them in a jar.",
            "done": (
                "(Oren holds a lump of the wall-rot up to the light and stares at it for a long time.)$B$B"
                "In the walls. Since before the plague. Breathing out through that choked vent into every cask I filled. "
                "Nobody did it. It was just... here. Waiting, like everything in Brill.$B$B"
                "(He sets it down.)$B$B"
                "I'll have to say it to her, won't I. Calla! ...I said you'd ruined the batch. I was wrong. You can stop "
                "smirking. No, you can't, I can see that from here. Fine.$B$B"
                "The cellar's sound, $n. The brewery's sound. We open as soon as I can bear to."),
            "return": "Return to Brewmaster Oren Blackbarrel at the old brewhouse in Brill.",
            "objectives": [("credit", "barrel_credit", 3, "Spoiled barrels examined"),
                           ("credit", "question_credit", 2, "Bram and Calla questioned"),
                           ("credit", "growth_credit", 4, "Cellar searched and growths cut out"),
                           ("credit", "vent_credit", 1, "Cellar vent repaired")],
            "items": [(929, 2)], "money": 2500, "xp": 4, "min_level": 10,
        },
        {
            "id": "q5", "title": "To Absent Friends", "giver": "oren_yard", "ender": "oren_yard", "prev": "q4",
            "log": "Invite Innkeeper Renee of the Gallows' End and Marta Greaves of the Wayfarer's Rest to the opening, tap the 3 "
                   "sample barrels at Brill's market, help Calla set up the tasting room in the brewhouse yard, and name the "
                   "brewery's signature drink with Brewmaster Oren Blackbarrel.",
            "offer": (
                "It's ready. I've said that four times this week and taken it back three, so listen quickly.$B$B"
                "Not a grand opening. I hate grand. A few barrels, a few people, the doors open. Take an invitation to Renee at "
                "the Gallows' End; she'll pretend she isn't worried about the competition. And one to Marta Greaves, who keeps "
                "the Wayfarer's Rest behind us and will try to haggle over the price of a free drink.$B$B"
                "Bram's rolled three sample barrels down to the market. Tap them, so folk get a taste and an argument before "
                "tonight. Calla needs a hand with the tasting room.$B$B"
                "And the drink needs a name. I've had forty. I hate all of them. You choose; then it's your fault."),
            "progress": "Invitations, barrels, tables, a name. A brewery is mostly a list.",
            "done": (
                "(The brewhouse is full: Renee and Marta arguing at the counter, Bram explaining staves to a Deathguard who "
                "didn't ask, Calla pouring, Hamlin Atkins weeping a little into his mug. Oren climbs onto a cask and raises "
                "his own.)$B$B"
                "To the people I worked beside, when we were alive. To old Tess, and the Brennan boys, and my father, who "
                "never once let me near the hops. They'd hate this beer.$B$B"
                "(He drinks.)$B$B"
                "I can't remember the last time I tasted a good ale. Fortunately, I can remember how to make one."),
            "return": "Return to Brewmaster Oren Blackbarrel at the old brewhouse in Brill.",
            "objectives": [("credit", "invite_credit", 2, "Invitations delivered"),
                           ("credit", "sample_credit", 3, "Sample barrels tapped at the market"),
                           ("credit", "room_credit", 1, "Tasting room set up"),
                           ("credit", "name_credit", 1, "Signature drink named")],
            "items": [(2596, 5)], "money": 4000, "xp": 5, "min_level": 10,
        },
        # The weekly Brewer's Special (Calla's latest experiment, poured for the usual victims).
        {
            "id": "special", "title": "Brewer's Special", "giver": "oren", "ender": "oren", "prev": "q5", "repeat": "weekly",
            "log": "Cut 3 bitterroot on the hillside west of Brill, then pour this week's experimental brew for Innkeeper Renee, "
                   "Deathguard Burgess and Hamlin Atkins and bring their verdicts to Brewmaster Oren Blackbarrel.",
            "offer": (
                "Calla's been at it again. Every week a new experiment: fermented in a skull, aged in a coffin, flavored with "
                "something she won't name in front of the Deathguard. Some weeks it's dreadful. Some weeks it's dreadful in an "
                "interesting way.$B$B"
                "This week's wants bitterroot from the hillside west of town, fresh cut. Then take a jug round to our usual "
                "victims: Renee at the Gallows' End, Deathguard Burgess in the square, and Hamlin Atkins, who will drink "
                "anything that ever touched a mushroom. Write down what they say. Calla says the notes are science. I say "
                "they're evidence."),
            "progress": "Bitterroot first, then the jug. Don't drink from it. Calla's counting.",
            "done": (
                "(Oren reads the verdicts and grunts.)$B$B"
                "\"Interesting.\" \"Interesting.\" \"I can see sounds.\" Calla will call that a triumph. I'll call it a "
                "week. She's already planning the next one; I saw her eyeing a coffin at the undertaker's.$B$B"
                "Here's your fee. Come back next week and we'll do it all again with something worse."),
            "return": "Return to Brewmaster Oren Blackbarrel at the Old Brewery in Brill.",
            "objectives": [("credit", "sp_herb", 3, "Fresh bitterroot cut"),
                           ("credit", "sp_renee", 1, "Innkeeper Renee's verdict"),
                           ("credit", "sp_burgess", 1, "Deathguard Burgess's verdict"),
                           ("credit", "sp_hamlin", 1, "Hamlin Atkins's verdict")],
            "money": 2500, "xp": 2, "min_level": 10,
        },
    ],
    # house_set: the house's barrel stand and cabinet bought (stage 7). The tasters and suppliers asked (each once), the
    # people questioned and invited; the choices: the recipe (q3) and the signature drink (q5).
    "markers": ["house_set", "got_culture", "got_grain", "tasted_hamlin", "tasted_dillinger", "tasted_zygand",
                "recipe_dark", "recipe_family", "recipe_herbal", "asked_bram", "asked_calla", "asked_renee", "asked_marta",
                "stout", "reserve", "bitter"],
    "npcs": [
        # Oren: at the brewhouse door until it opens; then behind its counter (always: the walk round the town finds
        # him there, and he lives upstairs).
        {"id": "oren_yard", "name": "Brewmaster Oren Blackbarrel", "display": 3652, "level": 25,
         "from": 1, "until": 6, "spawns": [[0, 2220.12, 267.76, 34.77, 5.15]]},
        {"id": "oren", "name": "Brewmaster Oren Blackbarrel", "subname": "The Old Brewery", "display": 3652, "level": 25,
         "flags": ["gossip", "quest", "vendor"], "from": 6, "spawns": [[0, 2222.01, 279.79, FLOOR, 3.578]],
         # Drinks; the signature (the player's choice) among them.
         "vendor": [159, 1179, 2723, 2593, 2594, 2894, 4600, {"item": 2596, "cond": ["M:stout"]},
                    {"item": 2686, "cond": ["M:reserve"]}, {"item": 18287, "cond": ["M:bitter"]}]},
        {"id": "bram", "name": "Bram Lusk", "subname": "Cooper", "display": 2615, "level": 20,
         "from": 2, "until": 6, "spawns": [[0, 2210.86, 266.31, 35.5, 5.67]]},
        {"id": "calla", "name": "Calla Fenn", "subname": "Apprentice Brewer", "display": 4528, "level": 12,
         "from": 3, "until": 6, "spawns": [[0, 2227.99, 270.99, 34.72, 5.15]]},
        # Marta: at the Wayfarer's Rest's door (in her tent until the caravan office builds it).
        {"id": "marta", "name": "Marta Greaves", "subname": "Wayfarer's Rest", "display": 2670, "level": 15, "flags": ["gossip"],
         "from": 1, "spawns": [[0, 2202.45, 289.29, 35.16, 5.24]]},
        # The cellar's tenants (The Kegs Are Empty), behind the brewhouse; no quarrel with the town's patrols.
        {"id": "rat", "name": "Brewhouse Rat", "display": 1141, "scale": 1.5, "hostile": True, "faction": 14, "level": (8, 9),
         "type": 1, "unit_class": 1, "health": 0.6, "damage": 0.6, "unit_flags": 512, "wander": 3, "respawn": 90,
         "from": 1, "until": 6,
         "spawns": [[0, 2216.28, 292.56, 35.08, 0.44], [0, 2218.55, 293.62, 35.16, 0.44], [0, 2216.34, 294.79, 35.09, 0.44],
                    [0, 2220.96, 291.98, 35.19, 0.44], [0, 2213.86, 294.19, 34.79, 0.44], [0, 2219.72, 295.82, 35.17, 0.44]]},
        # The brewery's day once it's open (each a time of day: none twice at once): Bram coopering in the yard from the
        # morning, at a table in the evening; Calla brewing by day, behind the tasting counter in the evening, tending her
        # cultures by the cellar at night; the evening's regulars.
        {"id": "bram_morning", "name": "Bram Lusk", "subname": "Cooper", "display": 2615, "level": 20,
         "flags": ["gossip", "vendor"], "from": 6, "when": "morning", "spawns": [[0, 2210.41, 266.1, 35.52, 5.67]],
         "vendor": [4470, 4399, 4400, 2880, 3857, 5956, 6217]},
        {"id": "bram_day", "name": "Bram Lusk", "subname": "Cooper", "display": 2615, "level": 20,
         "flags": ["gossip", "vendor"], "from": 6, "when": "day", "spawns": [[0, 2206.06, 270.69, 37.02, 0.44]],
         "vendor": [4470, 4399, 4400, 2880, 3857, 5956, 6217]},
        {"id": "bram_evening", "name": "Bram Lusk", "subname": "Cooper", "display": 2615, "level": 20, "flags": ["gossip"],
         "from": 6, "when": "evening", "spawns": [[0, 2215.88, 274.5, FLOOR, 5.15]]},
        {"id": "calla_day", "name": "Calla Fenn", "subname": "Brewing Ingredients", "display": 4528, "level": 12,
         "flags": ["gossip", "vendor"], "from": 6, "when": "day", "spawns": [[0, 2214.37, 280.08, FLOOR, 3.578]],
         "vendor": [2678, 2692, 3713, 2665, 30817, 4604, 4605, 4606, 4607, 159]},
        {"id": "calla_evening", "name": "Calla Fenn", "subname": "Brewing Ingredients", "display": 4528, "level": 12,
         "flags": ["gossip", "vendor"], "from": 6, "when": "evening", "spawns": [[0, 2232.46, 270.87, 34.45, 5.15]],
         "vendor": [2678, 2692, 3713, 2665, 30817, 4604, 4605, 4606, 4607, 159]},
        {"id": "calla_night", "name": "Calla Fenn", "subname": "Apprentice Brewer", "display": 4528, "level": 12,
         "flags": ["gossip"], "from": 6, "when": "night", "spawns": [[0, 2215.34, 291.02, 34.97, 2.01]]},
        {"id": "regular", "name": "Tasting Room Regular", "display": [2632, 2634, 2657], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "evening",
         "spawns": [[0, 2221.38, 274.53, FLOOR, 2.01], [0, 2229.66, 261.5, 34.11, 2.01], [0, 2233.75, 265.73, 34.11, 5.15]]},
        # Oren's visits: delivering to the Gallows' End in the evening; quarrelling with Irena Sable at the caravan office by
        # day (both open).
        {"id": "oren_evening", "name": "Brewmaster Oren Blackbarrel", "subname": "The Old Brewery", "display": 3652, "level": 25,
         "flags": ["gossip"], "from": 6, "when": "evening", "spawns": [[0, 2264.0, 248.0, 33.71, 0.2]]},
        {"id": "oren_office", "name": "Brewmaster Oren Blackbarrel", "subname": "The Old Brewery", "display": 3652, "level": 25,
         "flags": ["gossip"], "from": 6, "needs": {"caravan": 6}, "when": "day", "spawns": [[0, 2188.26, 278.89, 42.1, 1.59]]},
        # The building, by day: Oswin (the house's carpenter, lending a hand) and the builder's yard's men.
        {"id": "oswin", "name": "Oswin Thatcher", "subname": "Carpenter", "display": 1638, "level": 25, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "spawns": [[0, 2217.87, 260.75, 34.41, 1.45]]},
        {"id": "laborer", "name": "Builder's Yard Laborer", "display": [3516, 1638, 1604], "level": 15, "flags": [],
         "from": 2, "until": 6, "when": "day", "wander": 3,
         "spawns": [[0, 2215.15, 267.76, 35.15, 0.96], [0, 2220.05, 291.56, 35.18, 3.93]]},
    ],
    "credits": [
        {"id": "hall_credit", "name": "The old brewhouse looked into"},
        {"id": "spoiled_credit", "name": "Piles of spoiled stores cleared"},
        {"id": "ledger_credit", "name": "Oren's brewing ledger found"},
        {"id": "tubing_credit", "name": "Copper tubing salvaged"},
        {"id": "staves_credit", "name": "Sound oak staves"},
        {"id": "hoops_credit", "name": "Iron hoops from Oliver Dwor"},
        {"id": "vats_credit", "name": "Vats repaired and casks assembled"},
        {"id": "ingredient_credit", "name": "Ingredients gathered"},
        {"id": "batch_credit", "name": "Experimental batches set going"},
        {"id": "taster_credit", "name": "Townspeople who tasted the batches"},
        {"id": "recipe_credit", "name": "A recipe chosen for Oren"},
        {"id": "barrel_credit", "name": "Spoiled barrels examined"},
        {"id": "question_credit", "name": "Bram and Calla questioned"},
        {"id": "growth_credit", "name": "Cellar searched and growths cut out"},
        {"id": "vent_credit", "name": "Cellar vent repaired"},
        {"id": "invite_credit", "name": "Invitations delivered"},
        {"id": "sample_credit", "name": "Sample barrels tapped at the market"},
        {"id": "room_credit", "name": "Tasting room set up"},
        {"id": "name_credit", "name": "Signature drink named"},
        {"id": "sp_herb", "name": "Fresh bitterroot cut"},
        {"id": "sp_renee", "name": "Innkeeper Renee's verdict"},
        {"id": "sp_burgess", "name": "Deathguard Burgess's verdict"},
        {"id": "sp_hamlin", "name": "Hamlin Atkins's verdict"},
    ],
    "objects": [
        # The brewhouse: boarded up (everyone's) until it opens; open from then.
        {"id": "shell_old", "name": "Old Brewhouse", "display": 8020, "type": 33, "until": 6,
         "spawns": [[0, 2217.0, 278.0, 31.98, 0.436]]},
        {"id": "shell", "name": "The Old Brewery", "display": 7432, "type": 33, "from": 6,
         "spawns": [[0, 2217.0, 278.0, 31.98, 0.436]]},

        # 1: The Kegs Are Empty: the old copper by the door (the hall seen past it), the spoiled stores, the ledger.
        {"id": "copper", "name": "Old Brewing Copper", "display": 6513, "from": 1, "until": 6,
         "spawns": [[0, 2215.55, 265.74, 34.98, 2.007]],
         "use": [
             {"cond": ["I:q1"], "quest": "q1", "credit": "hall_credit"},
         ]},
        {"id": "spoiled", "name": "Spoiled Brewing Stores", "quest_only": True, "display": 2129, "scale": 0.6, "from": 1, "until": 6,
         "spawns": [[0, 2219.32, 264.74, 34.6, 0.436], [0, 2217.03, 262.56, 34.61, 1.134], [0, 2224.0, 264.16, 34.31, 1.833],
                    [0, 2224.34, 268.18, 34.65, 2.531], [0, 2224.58, 260.57, 34.12, 3.229], [0, 2227.57, 263.62, 34.19, 3.927]],
         "use": [
             {"cond": ["I:q1"], "quest": "q1", "credit": "spoiled_credit"},
         ]},
        {"id": "ledger", "name": "Fallen Shelf", "quest_only": True, "display": 184, "from": 1, "until": 6, "spawns": [[0, 2222.29, 291.5, 35.19, 0.96]],
         "use": [
             {"cond": ["I:q1"], "quest": "q1", "credit": "ledger_credit"},
         ]},
        # The cellar hatch behind the brewhouse (the rats' way out; the rot's way in).
        {"id": "hatch", "name": "Cellar Hatch", "display": 1108, "from": 1, "spawns": [[0, 2216.67, 290.54, 35.12, 0.436]],
         "use": [
             {"cond": ["I:q4"], "quest": "q4", "credit": "growth_credit"},
         ]},

        # 2: barriers; Bram's cooperage; the vats, the rotten casks and the cask frames (A Proper Fermentation).
        {"id": "cooper_bench", "name": "Cooper's Bench", "display": 234, "from": 2, "spawns": [[0, 2208.42, 266.83, 35.84, 2.01]]},
        {"id": "staves", "name": "Cask Staves", "display": 1108, "from": 2, "spawns": [[0, 2205.55, 268.25, 36.73, 0.96]]},
        {"id": "vats", "name": "Fermentation Vat", "display": 32, "scale": 1.6, "from": 2,
         "spawns": [[0, 2207.21, 271.78, 36.76, 0.44], [0, 2205.31, 275.86, 37.48, 0.44]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "vats_credit"},
         ]},
        {"id": "cask_frames", "name": "Unhooped Cask", "quest_only": True, "display": 32, "from": 2, "until": 6,
         "spawns": [[0, 2209.66, 262.99, 35.15, 0.44], [0, 2206.79, 264.41, 35.77, 0.44], [0, 2209.14, 260.54, 34.85, 0.44]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "vats_credit"},
         ]},
        {"id": "rotten_casks", "name": "Rotten Cask", "quest_only": True, "display": 8026, "scale": 0.8, "from": 2, "until": 6,
         "spawns": [[0, 2207.82, 285.86, 34.99, 0.44], [0, 2204.92, 286.16, 35.56, 0.44], [0, 2207.46, 289.0, 34.57, 0.44],
                    [0, 2203.95, 283.5, 36.69, 0.44], [0, 2205.01, 289.51, 34.71, 0.44], [0, 2202.02, 286.46, 36.13, 0.44]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "staves_credit"},
         ]},
        # A Proper Fermentation: the goblins' pump below the zeppelin tower.
        {"id": "pump", "name": "Junked Pump", "quest_only": True, "display": 6639, "spawns": [[0, 2088.0, 262.0, 57.19, 1.5]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "tubing_credit"},
         ]},

        # 3: the yard's brewing: the kettle, the furnace, shelves, barrels; smoke from the chimney while they work.
        {"id": "kettle", "name": "Brewing Kettle", "display": 216, "from": 3, "spawns": [[0, 2203.65, 272.33, 37.88, 0.44]]},
        {"id": "furnace", "name": "Brewhouse Furnace", "display": 348, "from": 3, "spawns": [[0, 2203.62, 279.48, 37.81, 2.01]]},
        {"id": "shelf", "name": "Brewing Shelves", "display": 189, "from": 3, "spawns": [[0, 2201.32, 277.31, 38.82, 2.01]]},
        {"id": "yard_barrels", "name": "New Cask", "display": 6036, "from": 3,
         "spawns": [[0, 2201.68, 274.17, 38.76, 0.44], [0, 2204.46, 269.39, 37.21, 0.44]]},
        {"id": "smoke", "name": "Chimney Smoke", "display": 95, "from": 3, "when": "day", "spawns": [[0, 2215.27, 285.25, 48.98, 0.44]]},
        # Taste of the Living: the bitterroot on the hillside west of town (cut again for the weekly special), the
        # experimental batches.
        {"id": "bitterroot", "name": "Bitterroot", "display": 301, "scale": 0.8,
         "spawns": [[0, 2150.0, 300.0, 46.95, 0.0], [0, 2158.0, 312.0, 43.78, 1.6], [0, 2145.0, 285.0, 49.69, 3.1],
                    [0, 2162.0, 325.0, 42.29, 4.4]],
         "use": [
             {"cond": ["I:q3"], "quest": "q3", "credit": "ingredient_credit"},
             {"cond": ["I:special"], "quest": "special", "credit": "sp_herb"},
         ]},
        {"id": "tub_dark", "name": "Experimental Mash Tub", "quest_only": True, "display": 216, "scale": 0.8, "from": 3, "until": 6,
         "spawns": [[0, 2228.14, 268.3, 34.51, 0.436]],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "batch_credit"}]},
        {"id": "tub_family", "name": "Experimental Mash Tub", "quest_only": True, "display": 216, "scale": 0.8, "from": 3, "until": 6,
         "spawns": [[0, 2230.41, 269.36, 34.48, 0.436]],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "batch_credit"}]},
        {"id": "tub_herbal", "name": "Experimental Mash Tub", "quest_only": True, "display": 216, "scale": 0.8, "from": 3, "until": 6,
         "spawns": [[0, 2231.17, 272.47, 34.66, 0.436]],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "batch_credit"}]},

        # 4: the beer garden and the tasting counter; a pavilion over Calla's tubs; the spoiled barrels, the wall-rot
        # and the vent (A Bitter Batch).
        {"id": "bad_barrels", "name": "Spoiled Barrel", "quest_only": True, "display": 7470, "from": 4, "until": 6,
         "spawns": [[0, 2213.05, 288.85, 34.72, 0.44], [0, 2210.63, 290.48, 34.53, 0.44], [0, 2212.26, 292.89, 34.6, 0.44]],
         "use": [
             {"cond": ["I:q4"], "quest": "q4", "credit": "barrel_credit"},
         ]},
        {"id": "growths", "name": "Wall-Rot", "quest_only": True, "display": 6432, "scale": 0.45, "from": 4, "until": 6,
         "spawns": [[0, 2215.21, 287.76, 34.96, 0.44], [0, 2219.7, 289.96, 35.17, 0.44], [0, 2217.06, 288.51, 35.12, 0.44]],
         "use": [
             {"cond": ["I:q4"], "quest": "q4", "credit": "growth_credit"},
         ]},
        {"id": "vent", "name": "Cellar Vent", "quest_only": True, "display": 7969, "scale": 0.15, "from": 4, "spawns": [[0, 2212.86, 286.88, 34.75, 0.44]],
         "use": [
             {"cond": ["I:q4"], "quest": "q4", "credit": "vent_credit"},
         ]},

        # 5: the cellar's racks, the market's sample barrels, the tasting room's trestles (To Absent Friends).
        {"id": "racks", "name": "Cask Racks", "display": 189, "from": 5, "spawns": [[0, 2210.62, 286.94, 34.69, 0.44]]},
        {"id": "samples", "name": "Old Brewery Sample Barrel", "quest_only": True, "display": 1727, "from": 5,
         "spawns": [[0, 2250.5, 267.5, 34.34, 2.6], [0, 2257.5, 278.0, 34.27, 2.5], [0, 2246.0, 274.0, 34.11, 2.6]],
         "use": [
             {"cond": ["I:q5"], "quest": "q5", "credit": "sample_credit"},
         ]},
        {"id": "trestle", "name": "Tasting Room Trestle", "display": 221, "from": 5, "until": 6,
         "spawns": [[0, 2228.96, 265.37, 34.28, 0.436]],
         "use": [
             {"cond": ["I:q5"], "quest": "q5", "credit": "room_credit"},
         ]},

        # 6: the brewhouse open: its counter, kegs, a vat, tables and benches; the slate by the door with the signature
        # drink; the brewery's dray at the Gallows' End of a morning.
        {"id": "bar", "name": "Brewery Counter", "display": 7732, "from": 6, "spawns": [[0, 2220.38, 279.03, FLOOR, 0.436]]},
        {"id": "kegs", "name": "Ale Keg", "display": 319, "from": 6,
         "spawns": [[0, 2224.1, 277.45, FLOOR + 0.88, 3.578], [0, 2221.56, 282.89, FLOOR + 0.88, 3.578]]},
        {"id": "inside_vat", "name": "Fermentation Vat", "display": 32, "scale": 1.6, "from": 6,
         "spawns": [[0, 2211.29, 280.3, FLOOR, 0.44]]},
        {"id": "inside_table", "name": "Table", "display": 221, "from": 6,
         "spawns": [[0, 2216.21, 273.77, FLOOR, 0.44], [0, 2220.96, 275.43, FLOOR, 0.44]]},
        {"id": "inside_bench", "name": "Bench", "display": 603, "from": 6,
         "spawns": [[0, 2216.85, 272.41, FLOOR, 0.44], [0, 2215.58, 275.13, FLOOR, 3.58], [0, 2221.59, 274.07, FLOOR, 0.44],
                    [0, 2220.32, 276.79, FLOOR, 3.58]]},
        {"id": "bottle_shelf", "name": "Bottle Shelf", "display": 4073, "from": 6, "spawns": [[0, 2212.53, 274.81, FLOOR, 0.44]]},

        # 7: the house's furnishings (design: a barrel stand, bottles, mugs and a little drinks cabinet), in the house's
        # own coordinates.
        {"id": "house_keg", "name": "Barrel Stand", "display": 1727, "scale": 0.7, "from": 7,
         "spawns": [["house", 4.29, 0.4, 0, 180]]},
        {"id": "house_cabinet", "name": "Drinks Cabinet", "display": 189, "scale": 0.45, "from": 7,
         "spawns": [["house", -2.1, 5.1, 0, 0]]},
    ],
    "gossip": [
        # Oren at the brewhouse door, by how far it's come.
        {"npc": "oren_yard", "kind": "greet", "cond": ["R:q4"],
         "text": "The cellar breathes. The casks are full. I keep finding reasons not to open, $n. That's how you know it's "
                 "nearly ready."},
        {"npc": "oren_yard", "kind": "greet", "cond": ["R:q2"],
         "text": "Smoke from my chimney. Do you see it? Eleven years. I keep stepping out to look at it, like a fool. Don't "
                 "tell Calla."},
        {"npc": "oren_yard", "kind": "greet", "cond": ["R:q1"],
         "text": "My father's brown, in my father's hand. I've read the page so often the ink's coming off on my thumb. Bram's "
                 "about somewhere, saying the vats can be saved. He's an optimist. I find it exhausting."},
        {"npc": "oren_yard", "kind": "greet",
         "text": "Oren Blackbarrel. Brewmaster. Yes, still. Being dead is no excuse for being out of work."},
        {"npc": "oren_yard", "kind": "option", "cond": ["I:q5"], "text": "Call it Gravemalt Stout.",
         "action": "choice", "quest": "q5", "credit": "name_credit", "marker": "stout", "emote": 273,
         "reply": "Gravemalt Stout. Dark, bitter, and it'll stain your teeth, if you've still got any. (Oren chalks it on the "
                  "slate.) Brill will drink it out of spite. Good."},
        {"npc": "oren_yard", "kind": "option", "cond": ["I:q5"], "text": "Call it Lordaeron Reserve.",
         "action": "choice", "quest": "q5", "credit": "name_credit", "marker": "reserve", "emote": 273,
         "reply": "Lordaeron Reserve. (Oren is quiet for a moment.) My father's ale, under the old kingdom's name. Folk will "
                  "order it and think of something. That's all a name's for, really."},
        {"npc": "oren_yard", "kind": "option", "cond": ["I:q5"], "text": "Call it Blackroot Bitter.",
         "action": "choice", "quest": "q5", "credit": "name_credit", "marker": "bitter", "emote": 273,
         "reply": "Blackroot Bitter. Herbal, harsh, brewed for the palates we've got and not the ones we lost. Calla will be "
                  "insufferable. (He chalks it anyway, large.)"},
        # Oren in the open brewery: the signature drink (the player's choice), and Irena's tariffs.
        {"npc": "oren", "kind": "greet", "cond": ["R:caravan.q5", "DAY:3"],
         "text": "Sable's charged me carriage on my own barley. Carriage! I carried casks up that road on my back when she was "
                 "still... well, when we were all still. I'm going round there tomorrow. I go round there every day."},
        {"npc": "oren", "kind": "greet", "cond": ["M:stout"], "texts": [
            "Gravemalt Stout, $n. Deathguard Burgess has three a night and says it tastes of nothing. He keeps checking.",
            "Pull up a bench. Mind the one on the end; it's Hamlin's, and he'll tell you about mushrooms."]},
        {"npc": "oren", "kind": "greet", "cond": ["M:reserve"], "texts": [
            "Lordaeron Reserve, $n. My father's brown. Folk order it and go quiet. I don't ask what they're thinking of. I know.",
            "Pull up a bench. Mind the one on the end; it's Hamlin's, and he'll tell you about mushrooms."]},
        {"npc": "oren", "kind": "greet", "cond": ["M:bitter"], "texts": [
            "Blackroot Bitter, $n. Calla tells everyone it was her idea. It was your idea. I tell everyone that.",
            "Pull up a bench. Mind the one on the end; it's Hamlin's, and he'll tell you about mushrooms."]},
        {"npc": "oren", "kind": "option", "cond": ["R:q5"], "text": "What are you pouring?", "action": "vendor"},
        {"npc": "oren", "kind": "option", "cond": ["R:q5"], "text": "Could you send something round to my house?",
         "action": "buy", "arg": 7500, "marker": "house_set", "emote": 1,
         "reply": "For the house by the road? A barrel stand with a cask on it, mugs that don't leak, and a little cabinet Bram "
                  "knocked together from the old vats' staves. I'll have Bram cart it over. (He takes your coin.) And a sign "
                  "for the cabinet. Everybody should have a brewery sign in the house. It reminds you where you'd rather be."},
        {"npc": "oren_evening", "kind": "greet", "texts": [
            "Delivering. Renee orders six casks a week and complains about all six. That's loyalty, that is.",
            "Evening, $n. Don't tell Renee, but her tap pours better than mine. I'll fix that tomorrow. Mine, I mean."]},
        {"npc": "oren_office", "kind": "greet", "texts": [
            "(Oren is jabbing a finger at a form.) \"Contents of cask.\" Ale! What else would it be? ...Don't answer that.",
            "Sable and I have an arrangement. She charges me, and I argue, and then I pay. It's been working for weeks."]},

        # Bram, at his bench until the brewhouse opens, and his day after.
        {"npc": "bram", "kind": "greet", "cond": ["R:q2"],
         "text": "Twelve casks this week. I sleep under the bench now. Not because I'm tired. Because I want to be near them."},
        {"npc": "bram", "kind": "greet",
         "text": "Bram Lusk. Cooper. (He turns a stave over in his hands, sighting along it.) Good oak doesn't care if you're "
                 "dead. That's what I like about it."},
        {"npc": "bram", "kind": "option", "cond": ["I:q4"], "text": "Oren thinks someone spoiled the batch. What do you know?",
         "action": "credit", "quest": "q4", "credit": "question_credit", "marker": "asked_bram", "emote": 1,
         "reply": "Someone. (Bram runs a thumb down a stave and shows you the green on it.) Look at the wood, not the people. "
                  "That's growing out of the oak. My casks were sound when they left my bench. It got in after. It got in from "
                  "somewhere with walls."},
        {"npc": "bram_morning", "kind": "greet",
         "text": "Morning. Hoops first, then staves, then whatever Oren's broken overnight. He breaks something every night. "
                 "I think it's how he sleeps."},
        {"npc": "bram_morning", "kind": "option", "text": "Show me what a cooper sells.", "action": "vendor"},
        {"npc": "bram_day", "kind": "greet",
         "text": "Caravan office wants forty casks for the Undercity run. Forty! (Bram looks very nearly happy.) I'll need more "
                 "oak."},
        {"npc": "bram_day", "kind": "option", "text": "Show me what a cooper sells.", "action": "vendor"},
        {"npc": "bram_evening", "kind": "greet",
         "text": "One mug, then home. (He has said this every evening for a month. He means it every time.)"},

        # Calla: her batches, the spoiled batch, and her day after.
        {"npc": "calla", "kind": "greet", "cond": ["R:q4"],
         "text": "He apologized. Out loud. In front of Bram. I've written down the date. I may have it carved somewhere."},
        {"npc": "calla", "kind": "greet", "cond": ["R:q3"],
         "text": "Your recipe's in the vat. Oren's pretending he chose it. Let him; it keeps him calm, and calm is when he "
                 "brews best."},
        {"npc": "calla", "kind": "greet",
         "text": "Calla Fenn. Before you ask: yes, that's mold, yes, it's on purpose, and no, you can't have some."},
        {"npc": "calla", "kind": "option", "cond": ["I:q3", "M:tasted_hamlin", "M:tasted_dillinger", "M:tasted_zygand"],
         "text": "Refine the dark batch, with Hamlin's culture.",
         "action": "choice", "quest": "q3", "credit": "recipe_credit", "marker": "recipe_dark", "emote": 273,
         "reply": "The dark one. Hamlin's \"excellent\". Good: it's got body, it's got a cellar in it. Oren will say it isn't ale. "
                  "Oren will be right, and then he'll drink three."},
        {"npc": "calla", "kind": "option", "cond": ["I:q3", "M:tasted_hamlin", "M:tasted_dillinger", "M:tasted_zygand"],
         "text": "Refine the old family brown. Oren deserves his father's ale.",
         "action": "choice", "quest": "q3", "credit": "recipe_credit", "marker": "recipe_family", "emote": 273,
         "reply": "The family brown. Dillinger's \"mud\". (Calla sighs.) Fine. Sentiment. I'll tell him, and I'll pretend I'm not "
                  "pleased, and you'll pretend you can't see me pretending."},
        {"npc": "calla", "kind": "option", "cond": ["I:q3", "M:tasted_hamlin", "M:tasted_dillinger", "M:tasted_zygand"],
         "text": "Refine the bitterroot batch.",
         "action": "choice", "quest": "q3", "credit": "recipe_credit", "marker": "recipe_herbal", "emote": 273,
         "reply": "The bitterroot. Zygand's mystery. Yes. Yes! If it made the Executor feel something, it'll make anybody feel "
                  "something. Possibly alarm. Alarm is a flavor."},
        {"npc": "calla", "kind": "option", "cond": ["I:q4"], "text": "Oren thinks your cultures spoiled the batch.",
         "action": "credit", "quest": "q4", "credit": "question_credit", "marker": "asked_calla", "emote": 1,
         "reply": "My cultures are in sealed jars in the yard, because I'm not an idiot. (Calla's voice is very level.) Go and "
                  "look at the cellar, $n. Smell the walls. I told him in the spring the walls smelled wrong. He told me walls "
                  "don't smell. Walls absolutely smell."},
        {"npc": "calla_day", "kind": "greet", "cond": ["R:q5"], "texts": [
            "This week: barley, bitterroot and a culture I scraped off a grave in the old cemetery. With permission. Mostly.",
            "This week's special is aged in a coffin. A clean one. I asked. Well, I knocked first.",
            "This week: rye, nightshade and a lullaby. Don't laugh; the yeast likes it.",
            "This week's is so bitter Dillinger saluted it. I'm calling that a review."]},
        {"npc": "calla_day", "kind": "option", "text": "What have you got for brewing and cooking?", "action": "vendor"},
        {"npc": "calla_evening", "kind": "greet",
         "text": "Tasting counter's open. Pick one. If you don't like it, pick another. If you don't like that, Oren will want "
                 "to know why, at length."},
        {"npc": "calla_evening", "kind": "option", "text": "What have you got for brewing and cooking?", "action": "vendor"},
        {"npc": "calla_night", "kind": "greet",
         "text": "Shh. The cultures are sleeping. Well, they're not. But they're quieter when I tell them they are."},
        {"npc": "regular", "kind": "greet", "texts": [
            "I don't drink. Can't. I come for the arguing. Best arguing in Tirisfal.",
            "Oren says this one tastes of the old kingdom. I say it tastes of Oren. Neither of us can taste a thing.",
            "Sit, sit. The bench by the door wobbles. Don't sit there. That's where the new ones sit, so we can watch."]},

        # Marta, at the Wayfarer's Rest's door (in her tent until it's built), by the caravan office's and the brewery's
        # progress.
        {"npc": "marta", "kind": "greet", "cond": ["R:caravan.q5", "R:q5"], "texts": [
            "A real roof, $n, and ale delivered to the door. If Blackbarrel would just come down two silver a cask I'd die "
            "happy. Again.",
            "Full house tonight: two from the Undercity, one from the Sepulcher and a fellow who says he's from Stratholme "
            "and won't say more. I've put him by the window."]},
        {"npc": "marta", "kind": "greet", "cond": ["R:caravan.q5"],
         "text": "The Wayfarer's Rest! Beds, board and no questions. Well, a few questions. I like to know who's under my roof."},
        {"npc": "marta", "kind": "greet", "cond": ["R:q5"],
         "text": "Blackbarrel's ale in a tent. It's very good ale. It's a very bad tent. When that caravan office gets round "
                 "to building me a roof, I'll serve it properly."},
        {"npc": "marta", "kind": "greet",
         "text": "Marta Greaves. Rooms, enquire within. Within the tent. It's a very good tent. The caravan office has "
                 "promised me walls, when they've finished their paperwork."},
        {"npc": "marta", "kind": "option", "cond": ["I:q5"], "text": "Oren invites you to the brewery's opening.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "asked_marta", "emote": 11,
         "reply": "Free drink, is it? Free drinks are the dearest kind; you pay in conversation. (Marta tucks the invitation into "
                  "her apron.) I'll come. I'll want a word about his barrel price, too. Twelve silver a cask! For water with "
                  "ideas!"},
        {"npc": RENEE, "kind": "option", "cond": ["I:q5"], "text": "Brewmaster Blackbarrel invites you to the brewery's opening.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "asked_renee", "emote": 1,
         "reply": "An invitation! (Renee reads it twice.) Competition, a stone's throw from my door. Tell him I'll come, and I'll "
                  "bring my own mug, and if his ale's better than mine I'll buy the recipe, and if it's worse I'll buy him a "
                  "drink. Either way he loses."},

        # A Proper Fermentation: the hoops.
        {"npc": OLIVER_DWOR, "kind": "option", "cond": ["I:q2"], "text": "Bram Lusk the cooper needs iron hoops.",
         "action": "credit", "quest": "q2", "credit": "hoops_credit", "emote": 4,
         "reply": "Bram's coopering again? (Oliver laughs, a rusty sound.) I made his hoops when we were both breathing. Here: "
                  "twenty, all sizes, and a hoop-driver he'll pretend he doesn't need. Tell him the first barrel's mine."},

        # Taste of the Living: the culture, the grain, the tasters (each once).
        {"npc": HAMLIN, "kind": "option", "cond": ["I:q3"],
         "text": "Calla Fenn would like a fungal culture. Your blue caps are the finest in Tirisfal.",
         "action": "credit", "quest": "q3", "credit": "ingredient_credit", "marker": "got_culture", "emote": 4,
         "reply": "Finest in Tirisfal! Finest in Lordaeron, I'd say, but nobody's measured. (He scoops a grey-blue crust into a "
                  "jar.) The mother culture. Started from a cap my grandfather grew in his boot. Tell the girl to feed it barley "
                  "and talk to it kindly."},
        {"npc": SALDEAN, "kind": "option", "cond": ["I:q3"], "text": "The old brewhouse needs a sack of brewing grain.",
         "action": "credit", "quest": "q3", "credit": "ingredient_credit", "marker": "got_grain", "emote": 4,
         "reply": "Brewing grain! For a brewery! (William heaves a sack onto your shoulder before you can object.) Do you know "
                  "how long it's been since anyone asked me for grain that wasn't for bats? On the house. No. Not on the house. "
                  "Tell Oren it's on the house, and I'll charge him double later."},
        {"npc": HAMLIN, "kind": "option", "cond": ["I:q3"], "text": "Would you taste one of Calla's experimental batches?",
         "action": "credit", "quest": "q3", "credit": "taster_credit", "marker": "tasted_hamlin", "emote": 4,
         "reply": "(Hamlin takes a long pull of the dark batch, and his eyes go wide.) Oh, that's the blue in it. That's my blue! "
                  "That's excellent, that is. Earthy. Like a good cellar. I'll have another, if it's going."},
        {"npc": DILLINGER, "kind": "option", "cond": ["I:q3"], "text": "Would you taste one of the brewery's experimental batches?",
         "action": "credit", "quest": "q3", "credit": "taster_credit", "marker": "tasted_dillinger", "emote": 274,
         "reply": "(Dillinger sniffs the old brown, sips, and sets it down with great care.) It tastes like mud, $g sir:madam;. "
                  "I spent the Third War in a trench, so I'm qualified to say. It tastes like that trench."},
        {"npc": ZYGAND, "kind": "option", "cond": ["I:q3"], "text": "Would you taste one of the brewery's experimental batches?",
         "action": "credit", "quest": "q3", "credit": "taster_credit", "marker": "tasted_zygand", "emote": 1,
         "reply": "(Zygand drinks the bitterroot batch in one swallow and stands very still.) ...I tasted that. I haven't tasted "
                  "anything since Andorhal. (A long pause.) I have no idea whether it was good. Don't ask me again until I've "
                  "decided."},

        # The Brewer's Special (weekly).
        {"npc": RENEE, "kind": "option", "cond": ["I:special"], "text": "This week's Brewer's Special, for your verdict.",
         "action": "credit", "quest": "special", "credit": "sp_renee", "emote": 1,
         "reply": "(Renee sips.) Interesting. ...That's an innkeeper's word, love. It means I'll sell it, but I won't drink it."},
        {"npc": BURGESS, "kind": "option", "cond": ["I:special"], "text": "The Old Brewery's special. Your verdict?",
         "action": "credit", "quest": "special", "credit": "sp_burgess", "emote": 6,
         "reply": "(Burgess drinks it like medicine.) Interesting. Is it meant to fizz in the nose? I haven't got a nose. It's "
                  "fizzing anyway."},
        {"npc": HAMLIN, "kind": "option", "cond": ["I:special"], "text": "Calla's latest. What do you make of it?",
         "action": "credit", "quest": "special", "credit": "sp_hamlin", "emote": 4,
         "reply": "(Hamlin drinks and blinks, slowly.) I can see sounds. Lovely. Is that the culture? Tell her to keep feeding it."},

        # Carolai, when she lives with the player: Oren's ingredients (she offers some of her own).
        {"npc": CAROLAI, "kind": "option", "cond": ["CAROLAI_HOME", "R:q5"], "text": "What do you make of Oren's brewing?",
         "action": "say", "emote": 1,
         "reply": "His bitterroot's picked too late and his hops are three years old; he keeps them in a sack by the furnace, "
                  "the poor things. I took him a jar of dried nightshade and a pinch of grave moss, ground fine. He held them "
                  "as if I'd handed him a live toad. (She smiles.) He'll use them. He'll say it was his idea. I'll let him."},

        # Oswin, the house's carpenter, lending a hand by day.
        {"npc": "oswin", "kind": "greet", "cond": ["OWN"],
         "text": "Your roof's fine, $n. I'm here because Bram asked me to look at the rafters, and because Oren keeps telling me "
                 "about his father, and I find I don't mind."},
        {"npc": "oswin", "kind": "greet",
         "text": "Oswin Thatcher. The roof wants new shingles and the floor wants a miracle. I can do one of those."},
    ],
}
