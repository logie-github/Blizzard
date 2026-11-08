# SPDX-License-Identifier: GPL-3.0-or-later
"""The New House: six quests restoring the house Cedric Harrow left the player (tools/build_sql.py), with
Oswin Thatcher, the Undercity carpenter Jamie Nore owed a favor ("I know a carpenter in the Undercity who
owes me even more than the innkeeper did"). Open once the deed is signed (home.welcome); the house is
the player's all along, restored or not."""

# Out the door, where Oswin works (the house's own coordinates: the doorway's side is -y; the ground
# there is about a yard below the floor).
OSWIN_AT = ["house", -3.0, -10.0, -0.25, 90]
INSPECT = "The house's state: "
# Where the hatch and the ladder put a player: in the cellar by the ladder, in the house by the hatch.
CELLAR_IN = ["cellar", -35.2, -2.0, 0.3, 0]
HOUSE_IN = ["house", 2.6, 0.9, 0.2, -90]

LINE = {
    "title": "The New House",
    "quests": [
        {
            "id": "place", "title": "The Place Is Yours", "giver": "oswin", "prev": "home.welcome",
            "log": "Inspect the house with Oswin Thatcher: the broken furniture, the rotten floorboards, the leaking roof and the cellar hatch.",
            "offer": (
                "You'll be the new owner, then. Oswin Thatcher, carpenter, late of the Undercity's Rogues' Quarter, and before "
                "that of a town that doesn't exist anymore. Jamie Nore sent for me. She said it was a favor. Jamie's favors "
                "are the kind you pay for twice.$B$B"
                "I've had a look from the doorway. I've seen worse. Mostly in the Plaguelands.$B$B"
                "Cedric kept the roof on, I'll give him that, but the dead don't notice damp and they don't notice rot. "
                "Before I lift a hammer, I want you to see it with your own eyes: the broken furniture, the floorboards by "
                "the hearth, wherever the rain's getting in, and that hatch down to the cellar. A house is like a body, "
                "$n. You find out what's wrong with it before you start cutting."),
            "progress": "Seen it all yet? Don't step on the boards by the hearth. Or do, and save me the trouble of pulling them up.",
            "done": (
                "So. A cellar that groans at night, a roof like a sieve, and furniture fit for kindling. I've rebuilt "
                "houses for worse owners in worse towns.$B$B"
                "The roof first, then the door, then the floor. Everything else can wait. Nothing in Tirisfal is in a hurry, "
                "least of all the people in it."),
            "objectives": [("credit", "seen_furniture", 1, "Broken furniture inspected"),
                           ("credit", "seen_floor", 1, "Rotten floorboards inspected"),
                           ("credit", "seen_roof", 1, "Leaking roof inspected"),
                           ("credit", "seen_hatch", 1, "Cellar hatch inspected")],
            "return": "Return to Oswin Thatcher outside your house in Brill.",
            "money": 1500, "xp": 2,
        },
        {
            "id": "timber", "title": "Timber for the Dead", "giver": "oswin", "prev": "place",
            "log": "Salvage 5 piles of usable lumber from abandoned farms around Tirisfal and a bucket of nails from Solliden Farmstead, then return to Oswin Thatcher.",
            "offer": (
                "I'd buy new timber, but the nearest honest lumber is in Silverpine, and the worgen have opinions about "
                "who cuts it. Besides, Tirisfal is full of houses nobody needs anymore.$B$B"
                "The farms out past Brill were built by people who knew their trade. Agamand Mills, the Solliden place, "
                "the old steadings east and west of town: there's oak in those walls older than either of us. Find the "
                "piles that haven't rotted through and bring back what you can carry. And nails. The Soliddens kept a "
                "bucket of them in the barn; nobody's had a use for them since.$B$B"
                "Mind what still lives out there. Or doesn't live, but walks about anyway."),
            "progress": "Timber? Nails? The roof isn't going to stop leaking because we've been patient with it.",
            "done": (
                "Good oak. Dry, straight, and only a little bloodstained.$B$B"
                "(Over the next hours Oswin works without stopping. The broken furniture goes out the door as kindling, the "
                "rotten boards come up, the gap in the roof closes, and the door finally shuts the way a door should.)$B$B"
                "There. It's a house again, $n. Not a home, not yet. But the rain stays outside, which is a start."),
            "objectives": [("credit", "lumber_credit", 5, "Salvageable lumber"),
                           ("credit", "nails_credit", 1, "Bucket of nails")],
            "return": "Return to Oswin Thatcher outside your house in Brill.",
            "money": 3500, "xp": 4,
        },
        {
            "id": "things", "title": "Things Left Behind", "giver": "oswin", "prev": "timber",
            "log": "Look through what Cedric Harrow left in the house: the bundle of letters, the portrait and the locked chest. Then speak with Oswin Thatcher.",
            "offer": (
                "Pulling up the floor turned up more than rot. Cedric left things behind: a bundle of letters under the "
                "loose board, a portrait over the mantel, and a chest with a lock rusted shut. I don't go through other "
                "people's things. It's bad luck, and I've had enough of that.$B$B"
                "But it's your house now. If there's anything in there worth keeping, or worth sending after him to "
                "Northrend, you're the one who ought to decide."),
            "progress": "Found anything? You've got the look of someone reading something they shouldn't.",
            "done": (
                "Elinor, two boys, and a dog called Bramble. And the last letter dated the week the grain came in from "
                "Andorhal.$B$B"
                "(Oswin is quiet a while.)$B$B"
                "I'll send the ring to Vengeance Landing with the next ship. Cedric should have it. The toy soldiers... "
                "leave them on the shelf. Some things belong to a house more than to a person."),
            "objectives": [("credit", "letters_credit", 1, "Cedric's letters read"),
                           ("credit", "portrait_credit", 1, "The portrait found"),
                           ("credit", "chest_credit", 1, "The chest opened")],
            "return": "Return to Oswin Thatcher outside your house in Brill.",
            "money": 2500, "xp": 3,
        },
        {
            "id": "floorboards", "title": "Beneath the Floorboards", "giver": "oswin", "prev": "things",
            "log": "Go down the hatch to your cellar, kill 6 Cellar Rats, then look at what's behind their nest.",
            "offer": (
                "Something's been chewing at the joists from below. I thought it was the house settling until it squeaked "
                "at me.$B$B"
                "Rats. Big ones. Cellar rats in Tirisfal grow fat on whatever the plague left in the ground, and they've "
                "been nesting under your floor since before Cedric came back. Down the hatch with you. Clear them out, and "
                "then have a proper look round the back of that cellar. I've a feeling they came from somewhere further down than the cellar. Rats don't dig "
                "that deep without a reason."),
            "progress": "Still squeaking. I can hear them from out here.",
            "done": (
                "A wall of brick at the back of the cellar, and a mark on it you don't like the look of. Show me.$B$B"
                "(Oswin studies your description for a long moment.)$B$B"
                "I've seen that sign before. In Stratholme, on the doors of the houses the Cult of the Damned used. Somebody "
                "bricked that up before the plague came to Brill, or just after.$B$B"
                "I'll mortar over it again. Whatever's behind it has waited this long. If you want to know more, I'd ask "
                "someone who keeps the dead's records. I'd rather not know at all."),
            "objectives": [("kill", "cellar_rat", 6, ""),
                           ("credit", "wall_credit", 1, "The bricked-up wall examined")],
            "return": "Return to Oswin Thatcher outside your house in Brill.",
            "money": 3000, "xp": 4,
        },
        {
            "id": "worth", "title": "A Home Worth Keeping", "giver": "oswin", "prev": "floorboards",
            "log": "Get candles and lamp oil from Abigail Shiel, linens from Mrs. Winters and clean straw from Morganus the stable master, then choose two furnishings with Oswin Thatcher.",
            "offer": (
                "Roof, door, floor, rats. That's the house done. A home is the rest of it.$B$B"
                "You'll want light: Abigail Shiel sells candles and lamp oil by the market. Linens for the bed: Mrs. Winters, "
                "and don't let her talk you into the gray ones. And straw, clean straw, from Morganus at the stable, so that "
                "dog of yours has somewhere to sleep that isn't your bed.$B$B"
                "Then come and tell me how you want the place set out. I'll build you two pieces of whatever you like, on "
                "Jamie's account. She owes me more than she'll admit."),
            "progress": "Light, linen, straw, and your say in the rest. I'm not building it all on my own guesswork.",
            "done": (
                "(Oswin hangs the last lantern and steps back to the doorway.)$B$B"
                "There. Lamps that don't smoke, linen that doesn't smell of grave dirt, a bed of straw by the stove for the "
                "dog, and a chest for whatever you drag home from your travels.$B$B"
                "It looks like somebody lives here, $n. That's all a house ever wants."),
            "objectives": [("credit", "candles_credit", 1, "Candles and lamp oil"),
                           ("credit", "linens_credit", 1, "Linens"),
                           ("credit", "straw_credit", 1, "Clean straw"),
                           ("credit", "furnish_credit", 2, "Furnishings chosen")],
            "return": "Return to Oswin Thatcher outside your house in Brill.",
            "money": 4000, "xp": 4, "items": [(858, 3)],
        },
        {
            "id": "housewarming", "title": "A Housewarming for the Dead", "giver": "oswin", "prev": "worth",
            "log": "Invite Innkeeper Renee, Apothecary Johaan, Hamlin Atkins and Deathguard Dillinger to your house, then speak with Oswin Thatcher there.",
            "offer": (
                "In Lordaeron, when a house was finished, you filled it with people the first night, so it would know what "
                "it was for. We did it in my town. We did it the night before the soldiers came to burn it.$B$B"
                "I'd like to do it once more.$B$B"
                "Invite your neighbors. Renee at the inn, she'll bring something to drink whether anyone can taste it or "
                "not. Johaan, if he can be pried away from his vials. Hamlin, the mushroom farmer next door. And Dillinger, "
                "so the Deathguard know which house to watch.$B$B"
                "They'll come. People in Brill don't get asked to things. It'll be the first invitation some of them have "
                "had since they died."),
            "progress": "Have you asked them? Don't worry if they say no. They won't say no.",
            "done": (
                "(The house is full: Renee pouring something brown into cups, Johaan explaining a recipe to Hamlin, who is "
                "explaining mushrooms back at him, Dillinger standing by the door out of habit.)$B$B"
                "Listen to that. Six years I've been building rooms for people to be lonely in.$B$B"
                "I'll stay on in Brill a while, I think. Jamie keeps finding me work. If you want anything else done to the "
                "place, you know where to find me. Right here, usually, admiring my own roof."),
            "objectives": [("credit", "invite_credit", 4, "Neighbors invited")],
            "return": "Speak with Oswin Thatcher outside your house in Brill.",
            "money": 5000, "xp": 5, "items": [(929, 3)],
        },
    ],
    "markers": ["invited_renee", "invited_johaan", "invited_hamlin", "invited_dillinger"],
    "npcs": [
        {"id": "oswin", "name": "Oswin Thatcher", "subname": "Carpenter", "display": 1638, "level": 25,
         "spawns": [OSWIN_AT]},
        {"id": "cellar_rat", "name": "Cellar Rat", "display": [1141, 1418, 2176], "hostile": True, "faction": 14,
         "level": (5, 6), "type": 1, "health": 0.7, "damage": 0.7, "scale": 1.3, "respawn": 30,
         "phase": "cellar",
         # (in the cellar, which the server's paths don't know: they run straight at what they fight)
         "movement": {"Flight": 2},
         "spawns": [["cellar", -30.0, 3.0, 0, 10], ["cellar", -30.0, 9.0, 0, 200], ["cellar", -19.5, 6.0, 0, 80],
                    ["cellar", -19.5, -3.0, 0, 300], ["cellar", -33.5, 4.0, 0, 140], ["cellar", -24.0, -5.5, 0, 45]]},
        # The housewarming's guests, in the house while it's on, and visiting now and then after.
        {"id": "guest_renee", "name": "Innkeeper Renee", "display": 8190, "phase": "guests",
         "flags": ["gossip"], "spawns": [["house", -1.5, -1.2, 0, 20]]},
        {"id": "guest_johaan", "name": "Apothecary Johaan", "display": 1565, "phase": "guests",
         "flags": ["gossip"], "spawns": [["house", 2.0, -0.3, 0, 160]]},
        {"id": "guest_hamlin", "name": "Hamlin Atkins", "display": 1635, "phase": "guests",
         "flags": ["gossip"], "spawns": [["house", 0.4, -0.9, 0, 300]]},
        {"id": "guest_dillinger", "name": "Deathguard Dillinger", "display": 2855, "phase": "guests",
         "flags": ["gossip"], "spawns": [["house", -1.6, -4.6, 0, 90]]},
    ],
    "credits": [
        {"id": "seen_furniture", "name": "Broken furniture inspected"},
        {"id": "seen_floor", "name": "Rotten floorboards inspected"},
        {"id": "seen_roof", "name": "Leaking roof inspected"},
        {"id": "seen_hatch", "name": "Cellar hatch inspected"},
        {"id": "lumber_credit", "name": "Salvageable lumber"},
        {"id": "nails_credit", "name": "Bucket of nails"},
        {"id": "letters_credit", "name": "Cedric's letters read"},
        {"id": "portrait_credit", "name": "The portrait found"},
        {"id": "chest_credit", "name": "The chest opened"},
        {"id": "wall_credit", "name": "The bricked-up wall examined"},
        {"id": "candles_credit", "name": "Candles and lamp oil"},
        {"id": "linens_credit", "name": "Linens"},
        {"id": "straw_credit", "name": "Clean straw"},
        {"id": "furnish_credit", "name": "Furnishings chosen"},
        {"id": "invite_credit", "name": "Neighbors invited"},
    ],
    "objects": [
        # Years of neglect: in the house until the timber's brought (their own player's).
        {"id": "broken_furniture", "name": "Broken Furniture", "display": 6682, "phase": "debris",
         "spawns": [["house", -0.35, -0.6, 0, 0]],
         "use": [{"cond": ["I:place"], "quest": "place", "credit": "seen_furniture"}]},
        {"id": "rotten_floor", "name": "Rotten Floorboards", "display": 6682, "scale": 0.5, "phase": "debris",
         "spawns": [["house", 1.25, 3.95, 0, 0]],
         "use": [{"cond": ["I:place"], "quest": "place", "credit": "seen_floor"}]},
        {"id": "leak", "name": "Leaking Roof", "display": 239, "phase": "debris",
         "spawns": [["house", -1.4, -2.6, 0, 0]],
         "use": [{"cond": ["I:place"], "quest": "place", "credit": "seen_roof"}]},
        # The hatch down to the cellar (everyone's to see; the house's owner goes down it): boards in the floor
        # by the hearth rug. The cellar (tools/build_town.py: CELLAR_*) is the game's own cellar of Brill's
        # tavern (the Duskwood inn's: its barrels, kegs and cobwebs), deep under the house; the hatch and the
        # ladder take a player down and up.
        {"id": "hatch", "name": "Cellar Hatch", "display": 6481,
         "spawns": [["house", 2.6, -0.75, 0, 0]],
         "use": [{"cond": ["I:place"], "quest": "place", "credit": "seen_hatch"},
                 {"cond": ["OWN"], "teleport": CELLAR_IN}]},
        # The cellar itself, and in it the ladder back up and the bricked-up stair behind the rats' nest.
        {"id": "cellar", "name": "Harrow Cellar", "display": 9700, "type": 33,
         "spawns": [["cellar", 0, 0, 6.72, 0]]},
        {"id": "ladder", "name": "Cellar Ladder", "display": 9701, "scale": 1.8,
         "spawns": [["cellar", -36.3, -2.0, 0, 0]],
         "use": [{"teleport": HOUSE_IN}]},
        {"id": "nest", "name": "Rats' Nest", "display": 461, "scale": 0.35,
         "spawns": [["cellar", -34.2, -6.6, 0.35, 0]]},
        {"id": "bricked_wall", "name": "Bricked-Up Stair", "display": 6718, "scale": 1.2,
         "spawns": [["cellar", -32.3, -6.9, 0.95, 0]],
         "use": [{"cond": ["I:floorboards"], "quest": "floorboards", "credit": "wall_credit"}]},
        # What Cedric left (in every player's house: scenery after, with their words).
        {"id": "letters", "name": "Bundle of Letters", "display": 220,
         "spawns": [["house", 4.35, -1.1, 0, 0]],
         "use": [{"cond": ["I:things"], "quest": "things", "credit": "letters_credit",
                  "text": "(Letters tied with twine, all to Cedric, all from Elinor. The early ones are about the harvest and the boys "
                          "and a dog called Bramble. The last is short:$B$B'They say the grain from Andorhal is bad. Owen is "
                          "coughing. Come home quickly. I don't like how quiet the road is.'$B$BShe never wrote again.)"}]},
        {"id": "portrait", "name": "Faded Portrait", "display": 2850, "scale": 0.9,
         # (over the mantel, on the chimney breast, facing the room)
         "spawns": [["house", 1.25, 5.05, 3.3, -90]],
         "use": [{"cond": ["I:things"], "quest": "things", "credit": "portrait_credit"}]},
        {"id": "chest", "name": "Rusted Chest", "display": 1,
         "spawns": [["house", 5.15, -1.0, 0, 180]],
         "use": [{"cond": ["I:things"], "quest": "things", "credit": "chest_credit"}]},
        # Furnished (after A Home Worth Keeping).
        {"id": "lantern", "name": "Lantern", "display": 6038, "phase": "restored",
         # (hanging: the model hangs from its top, 2.7 yards down)
         "spawns": [["house", -3.7, -4.9, 4.1, 90], ["house", -1.0, 2.3, 4.6, 0]]},
        {"id": "candelabra", "name": "Candelabra", "display": 240, "phase": "restored",
         "spawns": [["house", -3.4, 2.3, 1.3, 0]]},
        {"id": "storage", "name": "Storage Chest", "display": 5743, "phase": "restored",
         "spawns": [["house", -4.85, 2.8, 0, 0]]},
        {"id": "dog_bed", "name": "Straw Dog Bed", "display": 5911, "phase": "restored",
         "spawns": [["house", 1.25, 3.7, 0, 90]]},
        # Lumber and nails out in Tirisfal's abandoned farms (everyone's to see; each pile gives once).
        {"id": "lumber", "name": "Salvageable Lumber", "display": 1108,
         "spawns": [[0, 2828.0, 1049.0, 110.9, 1.0], [0, 2750.0, 780.0, 113.2, 2.0], [0, 2258.0, 1308.0, 33.4, 0.5],
                    [0, 2446.0, 488.0, 44.3, 4.0], [0, 2060.0, 560.0, 39.0, 3.0]],
         "use": [{"cond": ["I:timber"], "quest": "timber", "credit": "lumber_credit"}]},
        {"id": "nails", "name": "Bucket of Nails", "display": 239,
         "spawns": [[0, 2268.0, 1306.0, 33.4, 0.0]],
         "use": [{"cond": ["I:timber"], "quest": "timber", "credit": "nails_credit"}]},
    ],
    "gossip": [
        # Oswin.
        {"npc": "oswin", "kind": "greet", "cond": ["!OWN"],
         "text": "Oswin Thatcher, carpenter. I've been sent to fix a house for somebody who hasn't got it yet. Jamie Nore's idea of planning."},
        {"npc": "oswin", "kind": "greet", "cond": ["I:worth", "CAROLAI_HOME"],
         "text": "Two cups by the stove now, and somebody's alchemy things on the windowsill. Are some of these furnishings for her, then? "
                 "I'll make the chair arms wider. She looks like the sort who sits and watches."},
        {"npc": "oswin", "kind": "greet", "cond": ["R:housewarming", "CAROLAI_HOME"],
         "text": "The alchemist swept my sawdust out of the door this morning before I'd finished making it. Tidy. Very tidy. "
                 "She asked me which boards creak. I told her. I'm still not sure I should have."},
        {"npc": "oswin", "kind": "greet", "cond": ["R:housewarming"],
         "texts": ["Still standing. The roof, I mean. And me, more or less.",
                   "Jamie's got me fixing the town hall's shutters next. Then the inn's stairs. Brill was falling down for years "
                   "and nobody noticed, because nobody here expects anything to stay up.",
                   "If you want anything else built, $n, ask. I've grown fond of your house. Don't tell it."]},
        {"npc": "oswin", "kind": "greet", "cond": ["R:floorboards"],
         "text": "I mortared the gap twice. Some nights I'd swear I hear it breathing through the brick. Probably the wind."},
        {"npc": "oswin", "kind": "greet",
         "text": "Oswin Thatcher, carpenter. Mind the boards. Mind the roof. Mind everything, really; this house has been left to itself a long time."},
        {"npc": "oswin", "kind": "option", "cond": ["R:housewarming", "OWN"], "text": "I'd like more furniture for the house.",
         "action": "upgrades"},
        # The furnishings he builds on Jamie's account (two; any that aren't the player's yet).
        {"npc": "oswin", "kind": "option", "cond": ["I:worth", "!UPG:0"], "text": "A kitchen table and two chairs.",
         "action": "furnish", "arg": 0, "quest": "worth", "credit": "furnish_credit",
         "reply": "A table. Good. Every house argues better over a table."},
        {"npc": "oswin", "kind": "option", "cond": ["I:worth", "!UPG:1"], "text": "A wardrobe.",
         "action": "furnish", "arg": 1, "quest": "worth", "credit": "furnish_credit",
         "reply": "A wardrobe. Cedar, so the moths stay out. The moths here are the size of bats."},
        {"npc": "oswin", "kind": "option", "cond": ["I:worth", "!UPG:2"], "text": "A bookshelf.",
         "action": "furnish", "arg": 2, "quest": "worth", "credit": "furnish_credit",
         "reply": "A bookshelf. A reader, then. Brill could use one."},
        {"npc": "oswin", "kind": "option", "cond": ["I:worth", "!UPG:3"], "text": "A bearskin rug.",
         "action": "furnish", "arg": 3, "quest": "worth", "credit": "furnish_credit",
         "reply": "A rug. I'll ask the trappers. The bear won't mind."},
        {"npc": "oswin", "kind": "option", "cond": ["I:worth", "!UPG:4"], "text": "A pot-bellied stove.",
         "action": "furnish", "arg": 4, "quest": "worth", "credit": "furnish_credit",
         "reply": "A stove. Proper heat. Your living guests will thank you, and your dead ones will pretend to."},
        {"npc": "oswin", "kind": "option", "cond": ["I:worth"], "text": "It's furnished enough. Keep the wood for something else.",
         "action": "credit", "quest": "worth", "credit": "furnish_credit",
         "reply": "Suit yourself. I'll put it toward the shelves."},
        # The supplies (the game's own merchants).
        {"npc": 2118, "kind": "option", "cond": ["I:worth"], "text": "Oswin Thatcher sent me for candles and lamp oil.",
         "action": "credit", "quest": "worth", "credit": "candles_credit",
         "reply": "For Cedric's old place? About time someone lit a lamp in it. Here. Tell Oswin they're on Jamie's account. She'll love that."},
        {"npc": 2134, "kind": "option", "cond": ["I:worth"], "text": "I need linens for my house. Not the gray ones.",
         "action": "credit", "quest": "worth", "credit": "linens_credit",
         "reply": "Not the gray ones! Oswin's been talking. Fine. The cream, then. They were my mother's pattern. Don't bleed on them."},
        {"npc": 10055, "kind": "option", "cond": ["I:worth"], "text": "Could I have some clean straw? For my dog's bed.",
         "action": "credit", "quest": "worth", "credit": "straw_credit",
         "reply": "Clean straw, for a living dog. Do you know how long it's been since anyone in Brill asked me for something for a living animal? Take two armfuls."},
        # The invitations.
        {"npc": 5688, "kind": "option", "cond": ["I:housewarming"], "text": "Come to a housewarming at my place.",
         "action": "credit", "quest": "housewarming", "credit": "invite_credit", "marker": "invited_renee", "emote": 4,
         "reply": "A party? In Brill? I'll bring the cider. Nobody can taste it, but everybody remembers the smell."},
        {"npc": 1518, "kind": "option", "cond": ["I:housewarming"], "text": "Would you come to a housewarming at my house, Apothecary?",
         "action": "credit", "quest": "housewarming", "credit": "invite_credit", "marker": "invited_johaan",
         "reply": "A social obligation. How quaint. ...Yes, very well. I'll bring something. Something non-lethal, I suppose."},
        {"npc": 3547, "kind": "option", "cond": ["I:housewarming"], "text": "You're invited to my housewarming, neighbor.",
         "action": "credit", "quest": "housewarming", "credit": "invite_credit", "marker": "invited_hamlin", "emote": 4,
         "reply": "Neighbor! Nobody's called me that in years. I'll bring mushrooms. The good ones. The ones that don't talk back."},
        {"npc": 1496, "kind": "option", "cond": ["I:housewarming"], "text": "There's a housewarming at my house. You should come.",
         "action": "credit", "quest": "housewarming", "credit": "invite_credit", "marker": "invited_dillinger",
         "reply": "I'm on watch. ...I'll watch from your doorway, then. Same thing, with walls."},
        # The guests.
        {"npc": "guest_renee", "kind": "greet", "cond": ["CAROLAI_HOME"],
         "text": "So the alchemist lives here now. She poured my cider back into the jug and gave me tea instead. I didn't argue. Nobody argues with Carolai."},
        {"npc": "guest_renee", "kind": "greet",
         "texts": ["I brought cider. Can't taste it. Neither can half of us. We drink it anyway; it's the ceremony that counts.",
                   "My inn's never been this quiet, and your house has never been this loud. Seems fair.",
                   "When I was alive I used to bake for every new house on the lane. I've forgotten how. I remember the smell, though."]},
        {"npc": "guest_johaan", "kind": "greet",
         "texts": ["I've brought you a tincture for the damp. Rub it on the walls, not yourself. Probably not yourself.",
                   "A very reasonable house. Solid. Uncontaminated. I'm almost disappointed.",
                   "Your carpenter has opinions about rot. I have more. We've been discussing it for an hour. It's been delightful."]},
        {"npc": "guest_hamlin", "kind": "greet", "cond": ["DOG"],
         "text": "That dog of yours keeps sniffing my mushrooms. Smart dog. He knows the good ones."},
        {"npc": "guest_hamlin", "kind": "greet",
         "texts": ["Mushrooms! I brought mushrooms. A housewarming gift. Plant them in the cellar; they'll love it down there.",
                   "We're neighbors now. If you hear me singing to the crops at night, that's normal. It helps them grow.",
                   "Lovely house. Smells of fresh oak. Mine smells of mushrooms. Everything I own smells of mushrooms."]},
        {"npc": "guest_dillinger", "kind": "greet",
         "texts": ["I'm not on duty. I'm standing by the door because that's where I stand.",
                   "The Deathguard know which house this is now. Nothing comes up that road without us seeing it.",
                   "It's good, this. People in a room together who aren't afraid of each other. Don't tell Zygand I said so."]},
    ],
    "phases": {
        "debris": [["OWN", "!R:timber"]],
        "cellar": [["A:floorboards"]],
        "restored": [["R:worth"]],
        "guests": [["C:housewarming"], ["R:housewarming", "DAY:4"]],
    },
}
