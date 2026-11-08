# SPDX-License-Identifier: GPL-3.0-or-later
"""Brill Endures, the Town Improvement Board and the builder's yard, and The Town We Made: what opens the
six Community Projects (chapel, library, garden, surgeon, caravan, brewery) and what closes them.

Brill Endures is Magistrate Sevren's once any three of Brill's questlines are done (the user's choice);
it puts up the Board outside the town hall and opens the builder's yard, and the projects' first givers
come to town. The Town We Made, once all six projects are open, walks the player past what they built."""

# Brill's questlines, finished: any three open Brill Endures.
FINISHED = ["house.housewarming", "carolai.lily", "grave.bell", "apprentice.judgment", "scarlet.fate",
            "customer.closing", "deathguard.duty", "well.clear", "gallows.nomasters"]
import os
# (those written: a project not here yet isn't named, so the others can be made without it)
PROJECTS = [p for p in ["chapel", "library", "garden", "surgeon", "caravan", "brewery"]
            if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), p + ".py"))]
LEADERS = {"chapel": ("mirelle", "Dark Cleric Mirelle Vane"), "library": ("edmund", "Edmund Rook"),
           "garden": ("edda", "Edda Graves"), "surgeon": ("elspeth", "Surgeon Elspeth Rane"),
           "caravan": ("irena", "Quartermaster Irena Sable"), "brewery": ("oren", "Brewmaster Oren Blackbarrel")}
REFLECTIONS = {
    "chapel": "I came here expecting to bury people's faith. Instead they come and sit, and some of them pray, and some of them "
              "just remember. Halden rings the bell every evening. Nobody asks him to.",
    "library": "Do you know how many letters I've returned to people who'd forgotten they ever wrote them? Thirty-one. I wrote the "
               "number down. Of course I did.",
    "garden": "The gravebloom came back this spring without anyone planting it. That's how you know a garden is real, dear. It "
              "stops needing you.",
    "surgeon": "Agnes walked to the caravan yard yesterday. On her own. I didn't watch. I absolutely did not stand in the doorway "
               "and watch.",
    "caravan": "Forty-two shipments, three lost, one recovered, none unaccounted for. Brill is on the map, $n. I have the map. I "
               "drew it.",
    "brewery": "They come in the evening now. Not for the ale. Well. Some for the ale. Mostly they come to argue about it, which "
               "is the same thing.",
}

LINE = {
    "title": "Brill Endures",
    "quests": [
        {
            "id": "endures", "title": "Brill Endures", "giver": 1499,
            "available": {"any": 3, "of": FINISHED},
            "log": "Speak with Executor Zygand and Jamie Nore, ring the town bell in the square, then return to Magistrate Sevren.",
            "offer": (
                "Sit down, $n. No, not there; that chair belonged to the last magistrate, and he hasn't quite left it.$B$B"
                "I keep the town's accounts. Not just the coin: the people. Who arrived, who stayed, who walked into the "
                "Glades one night and didn't come back. For years the numbers only went one way.$B$B"
                "They've turned. A carpenter putting roofs back on. A gravekeeper who knows the names. Lamps lit on the "
                "right hours. A shop open again. You've had a hand in more of that than I'd like to admit to the Undercity, "
                "who'd want to know why a magistrate needed a stranger to do his work.$B$B"
                "I mean to call the town together. Tell Executor Zygand his Deathguard will stand in the square without "
                "their blades out, for once. Tell Jamie Nore to bring the ledgers. Then ring the bell. Brill hasn't "
                "heard it rung for a gathering since before the plague."),
            "progress": "The bell, $n. Brill won't come for a magistrate. It might come for a bell.",
            "done": (
                "(The square fills slowly: the Deathguard, the apothecaries, the innkeeper, the farmers, the ones who only "
                "come out after dark. Sevren reads the names of what's been mended, one by one.)$B$B"
                "Brill endures. It has always endured; that's the trouble with it. Endurance is what you do when you can't "
                "do anything else. I'd like it to do something else now.$B$B"
                "I've put a board up outside the hall: the Town Improvement Board. A chapel by the cemetery. A library. A "
                "garden. A surgeon's hall. A caravan office on the Undercity road. Somebody even wants the old brewery back. "
                "Each one has someone willing to see it through. None of them can do it alone.$B$B"
                "Help whichever you like. Help none. The board will be there either way."),
            "objectives": [("credit", "zygand_credit", 1, "Executor Zygand told"),
                           ("credit", "jamie_credit", 1, "Jamie Nore told"),
                           ("credit", "bell_credit", 1, "The town bell rung")],
            "return": "Return to Magistrate Sevren in the Brill town hall.",
            "money": 5000, "xp": 5, "items": [(929, 3)],
        },
        {
            "id": "town", "title": "The Town We Made", "giver": 1499,
            "available": {"all": [f"{p}.q5" for p in PROJECTS] or ["endures"]},
            "prev": "endures",
            "log": "Walk through Brill and speak with Mirelle Vane, Edmund Rook, Edda Graves, Elspeth Rane, Irena Sable and Oren "
                   "Blackbarrel, then return to Magistrate Sevren.",
            "offer": (
                "Six. A chapel, a library, a garden, a hall for the broken, an office for the road, and a brewery, Light help "
                "us. I've stopped counting the people who've moved here because of them; Jamie keeps losing her place.$B$B"
                "There's nothing left on the board, $n. No more projects. No more requests. That's not why I called you in.$B$B"
                "Walk the town. Not to fix anything. Just walk it, and speak to the people who built it with you. Then come "
                "back and tell me what you saw. I'd go myself, but they all stop being honest when the magistrate arrives."),
            "progress": "Have you walked it all? The garden takes longest. Edda will want to show you every bed.",
            "done": (
                "(Sevren listens without writing anything down, which is the first time you have ever seen him not write "
                "something down.)$B$B"
                "When I came here, Brill was a waystation. A place the dead passed through on their way to somewhere they "
                "could pretend they were alive. Now people come here to stay.$B$B"
                "You didn't do it alone, and you won't let me pretend you did. But you did it, $n. Whatever you were before, "
                "you're a citizen of Brill now. The ledger says so. I wrote it myself."),
            "objectives": [("credit", "walk_credit", 6, "Builders spoken with")],
            "return": "Return to Magistrate Sevren in the Brill town hall.",
            "money": 10000, "xp": 6, "items": [(929, 5)],
        },
    ],
    "stages": [["R:endures"], ["R:town"]],
    "npcs": [
        {"id": "foreman", "name": "Rudd Carver", "subname": "Builder's Yard Foreman", "display": 1631, "level": 25,
         "flags": ["gossip"], "from": 1, "spawns": [[0, 2297.0, 461.0, 33.9, 3.1]]},
        {"id": "laborer", "name": "Builder's Yard Laborer", "display": [3516, 1638, 1604], "level": 15, "flags": [],
         "from": 1, "when": "day", "wander": 4,
         "spawns": [[0, 2301.0, 467.0, 34.5, 2.0], [0, 2293.0, 455.0, 34.4, 4.5]]},
    ],
    "credits": [
        {"id": "zygand_credit", "name": "Executor Zygand told"},
        {"id": "jamie_credit", "name": "Jamie Nore told"},
        {"id": "bell_credit", "name": "The town bell rung"},
        {"id": "walk_credit", "name": "Builders spoken with"},
    ],
    "objects": [
        # The bell in the square (the town's own Horde bell is its frame; the rope is this).
        {"id": "bell", "name": "Bell Rope", "quest_only": True, "display": 7548,
         "spawns": [[0, 2299.0, 292.5, 35.2, 0.0]],
         "use": [{"cond": ["I:endures"], "quest": "endures", "credit": "bell_credit"}]},
        # The builder's yard on the north road.
        {"id": "yard_lumber", "name": "Lumber Stack", "display": 1248, "from": 1,
         "spawns": [[0, 2303.0, 457.0, 34.0, 0.4]]},
    ],
    "gossip": [
        {"npc": 1515, "kind": "option", "cond": ["I:endures"], "text": "The Magistrate is calling the town together. He asks the Deathguard to stand in the square.",
         "action": "credit", "quest": "endures", "credit": "zygand_credit",
         "reply": "Without blades. He said that, didn't he. ...Very well. We'll stand. Mostly so we can see who doesn't."},
        {"npc": 2310, "kind": "option", "cond": ["I:endures"], "text": "Magistrate Sevren is calling the town together. Bring the ledgers.",
         "action": "credit", "quest": "endures", "credit": "jamie_credit",
         "reply": "The ledgers! All of them? ...Of course all of them. Give me an hour. Some of them have to be dusted. Some of them have to be found."},
        {"npc": 1499, "kind": "greet", "cond": ["R:town"],
         "text": "Citizen $n. I do enjoy writing that. Is there something the town can do for you, for a change?"},
        {"npc": 1499, "kind": "greet", "cond": ["R:endures"],
         "text": "The board's still up, $n. Some days I stand at the window and watch people read it. Nobody read anything in Brill for years."},
        # The foreman, on how the projects are coming (theirs).
        {"npc": "foreman", "kind": "greet", "cond": ["R:town"],
         "text": "Six jobs, six openings, and not one roof fell on anybody. I've built for kings, $n. Kings were easier. Kings didn't argue about the color of a chapel door."},
        {"npc": "foreman", "kind": "greet",
         "texts": ["Rudd Carver, builder's yard. You bring it, we build it. You don't bring it, we stand here looking at the road.",
                   "Oswin Thatcher keeps coming round to tell my lads they're doing it wrong. He's usually right. Don't tell him.",
                   "Materials go on the left. Tools on the right. The pile in the middle is somebody's lunch from the plague year; nobody touch it."]},
    ],
}

# (Brill Endures goes in with its six projects: until they're all written, the line is left out.)
if len(PROJECTS) < 6:
    LINE = {"title": "Brill Endures (waiting for its projects)"}

# The Town We Made: a word with each project's leader (each once).
for project in (PROJECTS if "quests" in LINE else []):
    npc, name = LEADERS[project]
    LINE.setdefault("markers", []).append(f"walked_{project}")
    LINE["gossip"].append({"npc": f"{project}.{npc}", "kind": "option", "cond": ["I:town"],
                           "text": "Magistrate Sevren asked me to walk the town. How has it been?",
                           "action": "credit", "quest": "town", "credit": "walk_credit", "marker": f"walked_{project}",
                           "reply": REFLECTIONS[project]})
