# SPDX-License-Identifier: GPL-3.0-or-later
"""The Forgotten Shadow Chapel (a Community Project, opened by Brill Endures: tools/town/endures.py).

Dark Cleric Mirelle Vane comes from the Undercity to find a growing Brill with no place for reflection, and
asks for the old meeting house past the cemetery: the villagers sheltered there in the plague and scratched
their names into its walls. Brother Halden Wick, once a bellringer, wants four honest walls rather than a
monument; Acolyte Corven Dusk, newly woken, wonders whether the teachings are a door or a nicer name for the
wall; Elsbeth Vale, a widow still attached to the Light, stands at her husband's grave every evening. Five
quests: the meeting house inspected and cleared; stone, timber and its doors; the Book of Names (the choice:
Willem Vale's name added to the wall of names, or the wall kept as the sheltered left it); a walk through the
teachings with Corven (his question answered three ways); the hidden bell found, mended and rung at the
opening. Then the chapel stands (DuskwoodChapel), with Mirelle training priests, Corven selling candles and
reagents, Halden keeping the memorial and selling the house's chapel set, the Names to Remember daily, and
an evening gathering (Elsbeth; Mercy Hollin and Edith Fairweather if the gravekeeper's line brought them to
Brill; Edmund Rook of the library, if it's open). Mirelle visits the Surgeon's Hall in the evenings once it's
open.

The site: north of the cemetery, the chapel's door toward the town centre (its frame below: the chapel's
own coordinates; the meeting house, a burnt farmhouse, stands in its nave until the chapel opens). The
footprints and floors are the models' own (the vmaps' collision): the chapel's floor is 1.9 above its
origin, the meeting house has no floor (its ground is the terrain's). Heights are the terrain's (map tile
0002731) or, out in Tirisfal, those of the game's own spawns beside them.
"""
import math


def _at(frame, lx, ly):
    ox, oy, deg = frame
    o = math.radians(deg)
    return ox + lx * math.cos(o) - ly * math.sin(o), oy + lx * math.sin(o) + ly * math.cos(o)


# The chapel (its door at local +x, toward the town centre; it crosses Junior Apothecary Holland's and
# Deathguard Bartholomew's patrols, as anything that size near the cemetery does).
CHAPEL = (2403.5, 406.0, 210.0)
CHAPEL_Z = 35.3          # its origin; the floor is 1.9 above (37.2), the altar's step 2.6 (37.9)
FLOOR, STEP = 37.2, 37.9
# The meeting house (a burnt farmhouse) in the chapel's nave, its front door (its local (1.6, 8.6)) toward
# the town too.
HALL = (*_at(CHAPEL, 9.0, 0.0), 120.0)
HALL_Z = 33.85


def C(lx, ly, z, turn=0.0):
    """A spawn by the chapel's own coordinates (turn: degrees from its +x, the way to its door)."""
    x, y = _at(CHAPEL, lx, ly)
    return [0, round(x, 2), round(y, 2), z, round(math.radians(CHAPEL[2] + turn) % (2 * math.pi), 4)]


def F(lx, ly, z, turn=0.0):
    """A spawn by the meeting house's own coordinates (its front door at +y)."""
    x, y = _at(HALL, lx, ly)
    return [0, round(x, 2), round(y, 2), z, round(math.radians(HALL[2] + turn) % (2 * math.pi), 4)]


def W(x, y, z, deg=0.0):
    return [0, x, y, z, round(math.radians(deg) % (2 * math.pi), 4)]


LINE = {
    "title": "The Forgotten Shadow Chapel",
    "stages": [["R:endures.endures"], ["R:q1"], ["R:q2"], ["R:q3"], ["R:q4"], ["R:q5"], ["M:house_set"]],
    "quests": [
        {
            "id": "q1", "title": "A Place for the Unforgotten", "giver": "mirelle_site", "ender": "mirelle_site",
            "min_level": 8,
            "log": "Inspect the abandoned meeting house north of Brill's cemetery, clear its collapsed debris, examine its altar, "
                   "roof and prayer books, and ask the gravekeeper Mortimer Weller about the building's history.",
            "offer": (
                "You'll have come from the Magistrate's board. Good. I came because of a letter from the Undercity telling me "
                "Brill had no chapel, which I didn't believe until I'd walked the length of the place twice.$B$B"
                "Mirelle Vane. Dark Cleric, if titles matter to you. They matter less to me than they did when I wore white and "
                "said other prayers.$B$B"
                "There's a meeting house past the cemetery wall. Nobody has used it since the plague. I want it for a chapel of "
                "the Forgotten Shadow: not a cathedral, not a pulpit for shouting at the faithless. A roof, some benches, a "
                "place to sit with what you've lost and decide what to do about it.$B$B"
                "Look it over with me. Clear the worst of the rubble, see what's left of the altar, the roof and whatever books "
                "the damp has spared, and read the walls. Then ask the gravekeeper what the building was. Mortimer Weller keeps "
                "the cemetery's books; if anyone remembers, he will."),
            "progress": "The meeting house won't clear itself, $n. I know. I've stood here a week waiting for it to.",
            "done": (
                "Names. Dozens of them, cut into the plaster with knives and nails and, from the look of some, fingernails.$B$B"
                "Weller's right, then. They sheltered here when the sickness came through, and some of them knew they wouldn't "
                "leave.$B$B"
                "We keep them. Every one. If the chapel has to be built around that wall instead of in front of it, so be it. "
                "The first thing this place will be is a memory. The second can be whatever Brill makes of it."),
            "return": "Return to Dark Cleric Mirelle Vane at the meeting house north of Brill's cemetery.",
            "objectives": [("credit", "inspect_credit", 1, "The meeting house's walls read"),
                           ("credit", "debris_credit", 6, "Collapsed debris cleared"),
                           ("credit", "examine_credit", 3, "Altar, roof and prayer books examined"),
                           ("credit", "weller_credit", 1, "Mortimer Weller asked about the building")],
            "items": [(1181, 2)], "money": 1500, "xp": 3,
        },
        {
            "id": "q2", "title": "Stone, Timber, and Shadow", "giver": "halden_site", "ender": "halden_site", "prev": "q1",
            "min_level": 8,
            "log": "Bring 8 usable stone blocks and 6 lengths of timber from the ruined grounds of Cold Hearth Manor, see Rudd Carver "
                   "at the builder's yard about lantern frames and a cart, and rehang the meeting house's doors.",
            "offer": (
                "Halden Wick. I rang the bells at the chapel in Lordaeron's east ward for thirty-one years, and I'll tell you what "
                "I told every bishop who came through: I don't hold with sermons. I hold with roofs.$B$B"
                "The Cleric wants a chapel. Fine. But I've seen what the faithful do with a building: next thing it's marble and "
                "gilt, and nobody dares sit down. This will be stone, timber and four honest walls.$B$B"
                "Cold Hearth Manor, up the road past the crossroads. The Brisboises' garden wall came down years back and their "
                "sheds with it; the family says anyone's welcome to the stone who'll mind the dead that wander the grounds. "
                "Eight good blocks, six lengths of sound timber. Then see Rudd Carver at the builder's yard about iron for the "
                "lantern frames and a cart for the lot.$B$B"
                "And those doors. They're hanging by one hinge and spite."),
            "progress": "Stone, timber, iron, and a door that shuts. That's a chapel. Everything else is opinion.",
            "done": (
                "Good stone. Old Brisboise didn't skimp, I'll say that for the living.$B$B"
                "Rudd's lads will have the walls patched and half a roof on by week's end. The Cleric wants the old beams kept "
                "where they can be, and so do I, for different reasons. She says memory. I say they're oak.$B$B"
                "Here. For your back. Mine gave out in the plague year and never came back, which is a fine joke when you're dead."),
            "return": "Return to Brother Halden Wick at the meeting house north of Brill's cemetery.",
            "objectives": [("credit", "stone_credit", 8, "Usable stone blocks"),
                           ("credit", "timber_credit", 6, "Lengths of sound timber"),
                           ("credit", "yard_credit", 1, "Lantern frames and a cart from the builder's yard"),
                           ("credit", "doors_credit", 1, "The meeting house's doors rehung")],
            "items": [(858, 3)], "money": 2000, "xp": 4,
        },
        {
            "id": "q3", "title": "The Book of Names", "giver": "mirelle_site", "ender": "mirelle_site", "prev": "q2",
            "min_level": 8,
            "log": "Recover the register's three missing pages from the abandoned houses at Garren's Haunt, Agamand Mills and Solliden "
                   "Farmstead, find the grave its last entry names in Brill's cemetery, speak with Elsbeth Vale, and restore the "
                   "register at the meeting house's lectern.",
            "offer": (
                "The laborers found this under the floor where the pulpit stood: a register, bound in sailcloth against the damp. "
                "Whoever kept it wrote down everyone who came in out of the sickness, the day they came and, too often, the day "
                "they were carried out.$B$B"
                "Three pages are gone. Torn, not rotted. People took them when they left, I think: a page with their family's "
                "names on it, carried home like a relic. The register mentions the Garrens, the mill houses at Agamand and the "
                "Sollidens. If the pages survived, they're in what's left of those houses.$B$B"
                "The last entry is a burial, here in Brill's ground. And there's a woman, Elsbeth Vale, who has stood at that "
                "grave every evening since I came. I haven't spoken to her. I suspect she'd rather I didn't. She might talk to "
                "you.$B$B"
                "When the book is whole, we'll restore it at the lectern, where it belongs."),
            "progress": "The pages, $n. A book of names with names missing is just a list of the people we managed to keep.",
            "done": (
                "Whole. The binder's thread is new, but the hand is the old one.$B$B"
                "\"Willem Vale, ferryman. Came in on the ninth day with his wife's sister and two children not his own. Kept the "
                "door. Carried out the fourteenth day.\"$B$B"
                "He kept the door. Whatever came up the road those five days, it came to him first.$B$B"
                "Elsbeth told me what was decided about the wall. I won't argue it. It wasn't mine to decide, and it wasn't "
                "the Shadow's. The benches go in tomorrow."),
            "return": "Return to Dark Cleric Mirelle Vane at the meeting house north of Brill's cemetery.",
            "objectives": [("credit", "page_credit", 3, "Missing register pages recovered"),
                           ("credit", "grave_credit", 1, "The grave in the register found"),
                           ("credit", "elsbeth_credit", 1, "Elsbeth Vale spoken with"),
                           ("credit", "register_credit", 1, "The register restored at the lectern")],
            "items": [(1180, 2)], "money": 2500, "xp": 4,
        },
        {
            "id": "q4", "title": "The Weight of Faith", "giver": "corven_site", "ender": "corven_site", "prev": "q3",
            "min_level": 8,
            "log": "Visit the three places Corven Dusk has marked with a candle in Brill, keep the darkhounds off him at the wayside shrine on the "
                   "west road, recover the Agamand family's relic from their house at Agamand Mills, then answer Corven's question "
                   "at the meeting house.",
            "offer": (
                "May I ask you something? Everyone else here is very busy being dead.$B$B"
                "The Cleric teaches three things: respect, tenacity, power. Respect for ourselves and our dead. Tenacity, because "
                "we endure what should have ended us. Power, because no one will ever again decide for us what we are. I believe "
                "all of it. I think I do. But I walk through Brill and I see people who are only angry, and I wonder whether the "
                "teachings are a door, or just a nicer name for the wall.$B$B"
                "Mirelle says I should walk, and think, and take someone who argues back. I've left a candle burning at three places in "
                "town that I think belong to the teachings. Stand at each. Then the old wayside shrine on the west road: it was "
                "the Light's once, and the darkhounds den near it now. I'd like to pray there anyway, if you'll keep them off me. "
                "And the Agamands left something upstairs in their house at the mills. I'd like to see what they thought was "
                "worth keeping."),
            "progress": "I've written my question down, so I don't lose it. I keep reading it. It doesn't get any shorter.",
            "done": (
                "(Corven turns the little sunburst over in his fingers for a long time before he speaks.)$B$B"
                "The Agamands kept this through everything. Then they kept being Agamands, after, in the worst way. I don't know "
                "which of those the relic was for.$B$B"
                "Thank you for answering me. Most people tell me to stop asking. Mirelle says the asking is the teaching, and "
                "that if I ever stop, she'll know I've started obeying somebody. I'm going to light the candles at the door "
                "tonight. Someone should, and I'd like it to be someone who's still thinking."),
            "return": "Return to Acolyte Corven Dusk at the meeting house north of Brill's cemetery.",
            "objectives": [("credit", "sigil_credit", 3, "Places of the teachings visited"),
                           ("kill", 1547, 6, "Darkhounds driven from the wayside shrine"),
                           ("credit", "relic_credit", 1, "The Agamand family's relic"),
                           ("credit", "answer_credit", 1, "Corven's question answered")],
            "items": [(929, 2)], "money": 3000, "xp": 5,
        },
        {
            "id": "q5", "title": "The Bell for the Forgotten", "giver": "halden_site", "ender": "halden_site", "prev": "q4",
            "min_level": 8,
            "log": "Find the chapel's hidden bell in the barn at Garren's Haunt and its clapper in the farmhouse there, have the bell "
                   "mended at Brill's smithy, hang it at the meeting house, and attend the chapel's opening with Dark Cleric Mirelle "
                   "Vane.",
            "offer": (
                "There was a bell. There's still a bell, if the gnolls haven't sold it.$B$B"
                "It hung over this door when the meeting house was the parish's. In the plague we rang it for every death, and "
                "by the second week it never stopped. People couldn't sleep. People couldn't think. So one night Garren and I "
                "took it down and carted it to his barn and buried it in the hay, and I took the clapper out myself and hid it "
                "in his kitchen chimney, so nobody would ring it in grief at three in the morning.$B$B"
                "Garren's Haunt, east of here. The gnolls have the farm now. Bring me the bell and the clapper; take them to "
                "Oliver Dwor at the smithy, the bell's cracked and he's the only one in Brill with the patience. Then we hang it. "
                "And then, $n, the Cleric gets her opening, and I get to hear it once more."),
            "progress": "Thirty-one years I rang bells. Then I spent the next ten making sure one never rang. Funny trade.",
            "done": (
                "(Mirelle dedicates the chapel to those seeking strength, or memory, or only a quiet place to sit. Halden doesn't "
                "listen. He's standing under the bell with the rope in both hands, and when she's done he pulls, once, and the "
                "note rolls out over the cemetery and the town and the dark fields beyond.)$B$B"
                "They'll never hear it, of course. But perhaps that's not why we ring it.$B$B"
                "...Go on in, $n. Sit down. Nobody here will mind."),
            "return": "Return to Brother Halden Wick at the meeting house north of Brill's cemetery.",
            "objectives": [("credit", "bell_credit", 2, "The bell and its clapper recovered"),
                           ("credit", "smith_credit", 1, "The bell mended at Brill's smithy"),
                           ("credit", "hung_credit", 1, "The bell hung"),
                           ("credit", "ceremony_credit", 1, "The chapel's opening attended")],
            "items": [(929, 3)], "money": 5000, "xp": 5,
        },
        # Names to Remember: the chapel's daily (once it's open).
        {
            "id": "names", "title": "Names to Remember", "giver": "mirelle", "ender": "mirelle", "prev": "q5",
            "repeat": "daily", "min_level": 8,
            "log": "Recover 3 lost grave records from the graves around Tirisfal: Brill's north graveyard, Cold Hearth Manor, "
                   "Garren's Haunt and Agamand Mills.",
            "offer": (
                "Every parish kept a burial book. Most of them burned, or rotted, or were used to light Scourge fires. But the "
                "sextons wrote on whatever they had when the books ran out: boards, slates, the backs of tithe receipts, nailed "
                "to the grave markers or tucked into the gravedigger's sheds.$B$B"
                "Halden says they turn up all the time if you know where to look: the graveyard on the north road, the family "
                "plots at Cold Hearth, at Garren's and at the mills. Bring me three. Each one goes on the wall or in the book, "
                "whichever its people would have wanted."),
            "progress": "Three names, $n. Small work. The kind that's never finished.",
            "done": (
                "(Mirelle reads each record twice, once to herself and once aloud, and hands them to Halden for the wall.)$B$B"
                "Remembered. That's all we can do for them, and it's more than anyone did for us.$B$B"
                "Come back tomorrow, if you like. The sextons were thorough, and the rain is patient. Between them there's "
                "always another name."),
            "return": "Return to Dark Cleric Mirelle Vane in the Forgotten Shadow Chapel.",
            "objectives": [("credit", "record_credit", 3, "Lost grave records recovered")],
            "money": 1500, "xp": 2,
        },
    ],
    # Elsbeth's story heard; the wall of names (Willem's name added, or kept as it was); what Corven was told;
    # the house's chapel set bought.
    "markers": ["heard", "added", "kept", "protect", "choose", "strength", "house_set"],
    "npcs": [
        # Before the chapel opens: at the meeting house (its yard faces the town), each from when they come.
        {"id": "mirelle_site", "name": "Dark Cleric Mirelle Vane", "subname": "Forgotten Shadow", "display": 2668, "level": 30,
         "from": 1, "until": 6, "spawns": [C(21.5, 2.5, 35.36)]},
        {"id": "halden_site", "name": "Brother Halden Wick", "subname": "Caretaker", "display": 2640, "level": 22,
         "from": 2, "until": 6, "spawns": [C(20.5, -3.0, 35.47)]},
        {"id": "corven_site", "name": "Acolyte Corven Dusk", "display": 2618, "level": 12,
         "from": 3, "until": 6, "spawns": [C(18.8, 4.5, 34.5)]},
        # At the wayside shrine on the west road while he walks the teachings.
        {"id": "corven_shrine", "name": "Acolyte Corven Dusk", "display": 2618, "level": 12, "flags": ["gossip"],
         "from": 4, "until": 6, "spawns": [W(2160.2, 360.0, 44.6, 138)]},
        # Elsbeth at her husband's grave (from the Book of Names on, for good).
        {"id": "elsbeth", "name": "Elsbeth Vale", "display": 2662, "level": 14, "flags": ["gossip"],
         "from": 3, "spawns": [W(2364.4, 386.4, 36.6, 320)]},
        {"id": "laborer", "name": "Builder's Yard Laborer", "display": [3516, 1638, 1604], "level": 15, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "wander": 3,
         "spawns": [C(15.0, 9.5, 33.91), C(4.0, -9.5, 34.16)]},
        {"id": "oswin", "name": "Oswin Thatcher", "subname": "Carpenter", "display": 1638, "level": 25, "flags": ["gossip"],
         "from": 3, "until": 6, "when": "day", "spawns": [C(16.5, 10.8, 34.01, -60)]},
        # The chapel, open.
        {"id": "mirelle", "name": "Dark Cleric Mirelle Vane", "subname": "Forgotten Shadow", "display": 2668, "level": 30,
         "trainer": 2129, "from": 6, "spawns": [C(0.3, -1.5, FLOOR)]},
        {"id": "corven", "name": "Acolyte Corven Dusk", "subname": "Candles and Reagents", "display": 2618, "level": 12,
         "flags": ["gossip", "quest", "vendor"], "from": 6, "spawns": [C(15.0, -5.0, FLOOR, 90)],
         "vendor": [17028, 17029, 44615, 17027, 17056, 1399, 37201, 17020]},
        {"id": "halden", "name": "Brother Halden Wick", "subname": "Caretaker", "display": 2640, "level": 22,
         "flags": ["gossip"], "from": 6, "spawns": [C(11.5, 5.8, FLOOR, 90)]},
        # The evening gathering: Elsbeth on a bench; the four the gravekeeper's line brought home, if it did; Mirelle at
        # the Surgeon's Hall with the patients who ask for her (tools/town/surgeon.py's site).
        {"id": "elsbeth_chapel", "name": "Elsbeth Vale", "display": 2662, "level": 14, "flags": ["gossip"],
         "from": 6, "when": "evening", "spawns": [C(3.3, 3.5, FLOOR, 180)]},
        {"id": "mercy_chapel", "name": "Mercy Hollin", "display": 2660, "level": 12, "flags": ["gossip"],
         "from": 6, "when": "evening", "phase": "grave.newcomers", "spawns": [C(6.8, -3.0, FLOOR, 180)]},
        {"id": "edith_chapel", "name": "Edith Fairweather", "subname": "Weaver", "display": 2664, "level": 10, "flags": ["gossip"],
         "from": 6, "when": "evening", "phase": "grave.newcomers", "spawns": [C(6.8, -5.0, FLOOR, 180)]},
        {"id": "mirelle_hall", "name": "Dark Cleric Mirelle Vane", "subname": "Forgotten Shadow", "display": 2668, "level": 30,
         "flags": ["gossip"], "from": 6, "needs": {"surgeon": 6}, "when": "evening",
         "spawns": [W(2322.02, 377.35, 34.39, 55.7)]},   # (between the hall's two ward beds: its hall(-2.4, 0, 90))
    ],
    "credits": [
        {"id": "inspect_credit", "name": "The meeting house's walls read"},
        {"id": "debris_credit", "name": "Collapsed debris cleared"},
        {"id": "examine_credit", "name": "Altar, roof and prayer books examined"},
        {"id": "weller_credit", "name": "Mortimer Weller asked about the building"},
        {"id": "stone_credit", "name": "Usable stone blocks"},
        {"id": "timber_credit", "name": "Lengths of sound timber"},
        {"id": "yard_credit", "name": "Lantern frames and a cart from the builder's yard"},
        {"id": "doors_credit", "name": "The meeting house's doors rehung"},
        {"id": "page_credit", "name": "Missing register pages recovered"},
        {"id": "grave_credit", "name": "The grave in the register found"},
        {"id": "elsbeth_credit", "name": "Elsbeth Vale spoken with"},
        {"id": "register_credit", "name": "The register restored at the lectern"},
        {"id": "sigil_credit", "name": "Places of the teachings visited"},
        {"id": "relic_credit", "name": "The Agamand family's relic"},
        {"id": "answer_credit", "name": "Corven's question answered"},
        {"id": "bell_credit", "name": "The bell and its clapper recovered"},
        {"id": "smith_credit", "name": "The bell mended at Brill's smithy"},
        {"id": "hung_credit", "name": "The bell hung"},
        {"id": "ceremony_credit", "name": "The chapel's opening attended"},
        {"id": "record_credit", "name": "Lost grave records recovered"},
    ],
    "objects": [
        # ---- The meeting house, until the chapel opens (stages 1 to 5) ----
        {"id": "hall", "name": "Abandoned Meeting House", "display": 7436, "type": 33, "from": 1, "until": 6,
         "spawns": [F(0.0, 0.0, HALL_Z)]},
        # A Place for the Unforgotten: the names on the walls, the rubble, the altar, the roof, the books.
        {"id": "names", "name": "Scratched Names", "display": 5992, "scale": 3.0, "from": 1, "until": 6,
         "spawns": [F(-6.4, 2.0, 34.8)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "inspect_credit",
                  "text": "(Names, cut into the plaster at every height a hand could reach. Low down, where a child would sit, a little house with smoke coming out of the chimney, and under it: WE ARE STILL HERE.)"}]},
        {"id": "debris", "name": "Collapsed Debris", "display": 134, "scale": 1.3, "from": 1, "until": 6,
         "spawns": [F(-5.6, 5.8, 33.89, 30), F(5.9, 5.6, 34.36, 200), F(-5.8, -1.8, 34.04, 90), F(6.1, -2.6, 33.93, 310),
                    F(1.2, 6.2, 34.26, 150), F(-1.0, -6.8, 34.77, 240)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "debris_credit"}]},
        {"id": "altar", "name": "Damaged Altar", "display": 227, "scale": 0.8, "from": 1, "until": 6,
         "spawns": [F(-4.0, -6.6, 34.78, 90)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "examine_credit"}]},
        {"id": "beams", "name": "Fallen Roof Beams", "display": 1109, "from": 1, "until": 6,
         "spawns": [F(-3.8, 3.8, 33.89, 20)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "examine_credit"}]},
        {"id": "prayerbooks", "name": "Old Prayer Books", "quest_only": True, "display": 107, "from": 1, "until": 6,
         "spawns": [F(6.2, 1.2, 33.9, 80)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "examine_credit",
                  "text": "(In the margins, in a dozen hands: names, the price of bread, a recipe for willow-bark tea, and again and again: Light keep the door.)"}]},
        # From the first quest done: the builders' things, the sign; Halden's doors.
        {"id": "doors", "name": "Splintered Doors", "display": 13, "from": 2, "until": 6, "spawns": [F(4.8, 8.9, 36.65)],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "doors_credit"}]},
        {"id": "lumber", "name": "Builder's Lumber", "display": 1109, "from": 2, "until": 6,
         "spawns": [C(24.0, 7.5, 35.42, 90)]},
        # From the second: the walls patched, the roof going on.
        # (Halden working on by lantern light, nights)
        # The Book of Names: its lectern, inside the front door.
        {"id": "lectern", "name": "Reading Lectern", "display": 7348, "from": 3, "until": 6, "spawns": [F(3.6, 6.4, 34.42, 180)],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "register_credit"}]},
        # From the third: benches, candles and a memorial stone in the cleared house.
        {"id": "benches", "name": "Bench", "display": 682, "from": 4, "until": 6,
         "spawns": [F(-3.3, 0.6, 33.93, -90), F(3.3, 0.6, 33.89, -90), F(-3.3, -2.6, 34.14, -90), F(3.3, -2.6, 33.98, -90)]},
        {"id": "hall_memorial", "name": "Memorial Stone", "display": 3171, "scale": 0.9, "from": 4, "until": 6,
         "spawns": [F(3.8, -7.0, 34.65, 90)]},
        {"id": "hall_candles", "name": "Memorial Candle", "display": 4152, "scale": 1.5, "from": 4, "until": 6,
         "spawns": [F(2.4, -6.4, 34.59), F(-4.6, -6.6, 35.72), F(-3.4, -6.6, 35.72)]},
        # From the fourth: Corven lights the door's candles at dusk.
        # The Bell for the Forgotten: the bell waiting by its hoist.
        {"id": "site_bell", "name": "Chapel Bell", "display": 4571, "scale": 2.5, "from": 5, "until": 6,
         "spawns": [C(26.5, 6.5, 35.2)],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "hung_credit"}]},
        {"id": "hoist", "name": "Bell Hoist", "display": 1109, "from": 5, "until": 6, "spawns": [C(27.5, 8.5, 35.99, 90)]},
        # ---- Out in Tirisfal ----
        # Stone, Timber, and Shadow: Cold Hearth Manor's fallen garden wall and sheds.
        {"id": "stone_block", "name": "Stone Block", "quest_only": True, "display": 134,
         "spawns": [W(2140.0, 648.0, 33.92, 20), W(2138.0, 662.0, 34.04, 80), W(2144.0, 672.0, 34.7, 140),
                    W(2150.0, 680.0, 34.8, 200), W(2170.0, 678.0, 33.36, 260), W(2178.0, 670.0, 33.39, 320),
                    W(2182.0, 650.0, 33.61, 10), W(2146.0, 640.0, 34.18, 100)],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "stone_credit"}]},
        {"id": "timber", "name": "Sound Timber", "quest_only": True, "display": 1248,
         "spawns": [W(2131.0, 683.0, 37.45, 30), W(2127.0, 690.0, 37.98, 110), W(2136.0, 691.0, 37.43, 200),
                    W(2152.0, 650.0, 33.97, 300), W(2175.0, 663.0, 33.68, 60), W(2165.0, 640.0, 35.21, 150)],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "timber_credit"}]},
        # The Book of Names: the three torn pages, carried home.
        {"id": "page", "name": "Torn Register Page", "quest_only": True, "display": 164,
         "spawns": [W(2910.03, 380.97, 31.55, 40), W(2822.0, 813.5, 113.61, 120), W(2263.52, 1313.27, 34.05, 260)],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "page_credit",
                  "text": "(Names and dates in the meeting house's hand. Beside one name, in another hand, much later: we got home.)"}]},
        # The grave the register's last entry names (in Brill's cemetery, for those who've read the book).
        {"id": "grave", "name": "Grave of Willem Vale", "display": 2453, "from": 3, "spawns": [W(2366.0, 385.0, 36.75, 140)],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "grave_credit"}]},
        # The Weight of Faith: Corven's candles, the shrine, the Agamands' relic (upstairs in their house at the mills).
        {"id": "sigil_respect", "name": "Corven's Candle", "quest_only": True, "display": 4152, "from": 4, "until": 6,
         "spawns": [W(2384.0, 347.0, 38.11)],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "sigil_credit"}]},
        {"id": "sigil_tenacity", "name": "Corven's Candle", "quest_only": True, "display": 4152, "from": 4, "until": 6,
         "spawns": [W(2293.0, 407.0, 33.9)],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "sigil_credit"}]},
        {"id": "sigil_power", "name": "Corven's Candle", "quest_only": True, "display": 4152, "from": 4, "until": 6,
         "spawns": [W(2283.0, 298.5, 35.18)],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "sigil_credit"}]},
        {"id": "shrine", "name": "Wayside Shrine", "display": 1527, "from": 4, "until": 6, "spawns": [W(2158.0, 362.0, 44.62, 20)]},
        {"id": "relic", "name": "Agamand Nursery Chest", "quest_only": True, "display": 8, "spawns": [W(2751.5, 793.5, 119.22, 60)],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "relic_credit"}]},
        # The Bell for the Forgotten: the bell under the hay in Garren's barn, the clapper in his kitchen chimney.
        {"id": "hidden_bell", "name": "Bell Under the Hay", "quest_only": True, "display": 4571, "scale": 2.5, "spawns": [W(2840.8, 413.4, 20.05, 30)],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "bell_credit"}]},
        {"id": "clapper", "name": "Bell Clapper", "quest_only": True, "display": 908, "scale": 1.5, "spawns": [W(2910.37, 376.9, 31.75, 110)],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "bell_credit"}]},
        # Names to Remember: the lost grave records (the graveyard on the north road, Cold Hearth's family plot, Garren's,
        # the mills).
        {"id": "record", "name": "Lost Grave Record", "quest_only": True, "display": 220,
         "spawns": [W(2333.0, 521.5, 28.77, 90), W(2150.0, 668.0, 33.84, 30), W(2921.0, 371.0, 31.35, 200),
                    W(2812.0, 820.0, 112.84, 300)],
         "use": [{"cond": ["I:names"], "quest": "names", "credit": "record_credit"}]},
        # ---- The chapel, open (stage 6 on) ----
        {"id": "chapel", "name": "Forgotten Shadow Chapel", "display": 7449, "type": 33, "from": 6,
         "spawns": [C(0.0, 0.0, CHAPEL_Z)]},
        {"id": "chapel_altar", "name": "Altar", "display": 227, "from": 6, "spawns": [C(-5.2, 0.0, STEP)]},
        {"id": "altar_candles", "name": "Black Candle", "display": 4152, "scale": 1.5, "from": 6,
         "spawns": [C(-5.2, 1.2, STEP + 1.15), C(-5.2, -1.2, STEP + 1.15)]},
        {"id": "candelabra", "name": "Candelabra", "display": 240, "from": 6,
         "spawns": [C(-3.8, 3.0, STEP), C(-3.8, -3.0, STEP), C(10.8, 7.4, FLOOR, -90), C(14.2, 7.4, FLOOR, -90)]},
        {"id": "banner", "name": "Forsaken Banner", "display": 7979, "from": 6,
         "spawns": [C(-6.6, 4.8, STEP), C(-6.6, -4.8, STEP)]},
        {"id": "pews", "name": "Pew", "display": 673, "from": 6,
         "spawns": [C(2.0, 4.3, FLOOR), C(2.0, -4.3, FLOOR), C(5.5, 4.3, FLOOR), C(5.5, -4.3, FLOOR),
                    C(9.0, 4.3, FLOOR), C(9.0, -4.3, FLOOR)]},
        {"id": "book_lectern", "name": "The Book of Names", "display": 7348, "from": 6, "spawns": [C(-1.0, 3.5, FLOOR, 180)]},
        {"id": "memorial", "name": "Memorial Wall", "display": 6645, "scale": 0.8, "from": 6, "spawns": [C(12.5, 7.6, FLOOR, -90)]},
        {"id": "shelf", "name": "Chapel Bookshelf", "display": 189, "from": 6, "spawns": [C(12.0, -7.6, FLOOR)]},
        {"id": "book_table", "name": "Reading Table", "display": 581, "from": 6, "spawns": [C(8.5, -7.2, FLOOR)]},
        # The shelf of readable books on the Forsaken's faith.
        {"id": "book_shadow", "name": "On the Forgotten Shadow", "display": 184, "from": 6,
         "spawns": [C(8.2, -7.0, FLOOR + 1.12, 20)]},
        {"id": "book_sermons", "name": "Sermons for the Risen", "display": 254, "from": 6,
         "spawns": [C(8.8, -7.4, FLOOR + 1.12, 70)]},
        {"id": "book_reflections", "name": "A Book of Reflections", "display": 1128, "from": 6,
         "spawns": [C(8.5, -6.8, FLOOR + 1.12, 150)]},
        {"id": "bell_rope", "name": "Bell Rope", "display": 7548, "scale": 0.06, "from": 6, "spawns": [C(21.0, 1.5, FLOOR + 0.6)]},
        # (Corven lights the porch's candles at dusk.)
        # ---- The house's chapel set (bought from Halden): a candle and a book on a little table, a Shadow hanging ----
        {"id": "house_table", "name": "Devotional Table", "display": 581, "scale": 0.6, "from": 7,
         "spawns": [["house", -4.75, 1.55, 0, 0]]},
        {"id": "house_candle", "name": "Memorial Candle", "display": 4152, "scale": 1.3, "from": 7,
         "spawns": [["house", -4.9, 1.35, 0.68, 0]]},
        {"id": "house_book", "name": "Book of Reflections", "display": 254, "scale": 0.6, "from": 7,
         "spawns": [["house", -4.6, 1.75, 0.68, 0]]},
        {"id": "house_hanging", "name": "Shadow Hanging", "display": 7979, "scale": 0.4, "from": 7,
         "spawns": [["house", -4.97, 1.55, 1.6, 0]]},
    ],
    "gossip": [
        # ---- Mirelle at the meeting house ----
        {"npc": "mirelle_site", "kind": "greet", "cond": ["R:q4"],
         "text": "Corven lit the candles at the door last night without being asked. I didn't say anything. If I praise him he'll "
                 "stop to wonder why, and then he'll stop lighting them."},
        {"npc": "mirelle_site", "kind": "greet", "cond": ["R:q3"],
         "text": "Benches, $n. People have started coming in to sit on them. One of them asked me what the rules were. I told her "
                 "there's only one: no one gets to tell you what you are. She asked if that included me. I said especially me."},
        {"npc": "mirelle_site", "kind": "greet", "cond": ["R:q1"],
         "text": "Halden objects to everything I say and then does it better than I asked. I've decided to find this restful."},
        {"npc": "mirelle_site", "kind": "greet",
         "text": "(A tall Forsaken in black and violet regards the burnt meeting house as though it owes her money.)$B$BI was a "
                 "priestess of the Light once. I prayed in buildings very like this one. You learn a great deal about a faith "
                 "from what's left standing when it's gone."},
        # A Place for the Unforgotten: the gravekeeper.
        {"npc": "grave.keeper", "kind": "option", "cond": ["I:q1"], "text": "What was the meeting house past the cemetery wall?",
         "action": "credit", "quest": "q1", "credit": "weller_credit", "emote": 1,
         "reply": "The parish meeting house. Tithes, weddings, the harvest supper. In the plague year the sick were turned away from "
                  "the inns, and the healthy daren't go home, so they all went there and barred the door. I wrote them into my "
                  "book as they were carried out. I stopped when my own hand shook too hard. Nobody wrote after me."},
        # ---- Halden ----
        {"npc": "halden_site", "kind": "greet", "cond": ["A:q5"],
         "text": "Garren's barn, $n, under the hay at the back. And the chimney. Mind the soot; it's older than you."},
        {"npc": "halden_site", "kind": "greet", "cond": ["R:q2"],
         "text": "Half a roof. You know what half a roof is? It's a promise. I work on it nights, when the Cleric isn't here to "
                 "suggest stained glass."},
        {"npc": "halden_site", "kind": "greet",
         "text": "Brother Halden. I was never anybody's brother, mind; the bishop gave everyone titles so he'd have something to "
                 "take away. Hand me that maul if you're staying."},
        # Stone, Timber, and Shadow: the builder's yard.
        {"npc": "endures.foreman", "kind": "option", "cond": ["I:q2"],
         "text": "Halden Wick needs iron lantern frames for the chapel, and a cart for stone and timber.",
         "action": "credit", "quest": "q2", "credit": "yard_credit", "emote": 1,
         "reply": "Wick! Four frames, he'll want, and he'll say they're too fancy whatever I send. Take these: plain iron, my own "
                  "forging. And the cart's yours for the day. Tell him if he wants it back in one piece he can come and sweet-talk "
                  "the axle himself."},
        # The Book of Names: Elsbeth's story, then what's to be done about the wall.
        {"npc": "elsbeth", "kind": "option", "cond": ["I:q3"],
         "text": "Mirelle Vane is restoring the register of those who sheltered in the meeting house.",
         "action": "say", "marker": "heard", "emote": 1,
         "reply": "I know what's in it. Willem Vale, ferryman. He kept the door, the five days the dead came up the road. He "
                  "prayed to the Light every hour of it, out loud, so the children wouldn't hear the scratching. The others cut "
                  "their names in the wall while he stood there. He never had a hand free. So his name isn't on it."},
        {"npc": "elsbeth", "kind": "option", "cond": ["I:q3", "M:heard"],
         "text": "Then his name belongs on that wall, with the people he kept safe. Let Halden cut it.",
         "action": "choice", "quest": "q3", "credit": "elsbeth_credit", "marker": "added", "emote": 18,
         "reply": "On the wall. With them. ...Yes. He'd have argued, he'd have said it's a Shadow chapel now. But he'd have been "
                  "standing in front of it, and that's where they'll see him. Tell the bellringer to cut it deep."},
        {"npc": "elsbeth", "kind": "option", "cond": ["I:q3", "M:heard"],
         "text": "The wall should stay exactly as they left it. He's in the book, in the Light's own words; that's his.",
         "action": "choice", "quest": "q3", "credit": "elsbeth_credit", "marker": "kept", "emote": 2,
         "reply": "Leave it as they cut it. Yes. He wouldn't want his name on a Shadow chapel, however kindly they meant it. He's "
                  "in the book, praying. That's where I'll go to read him."},
        {"npc": "elsbeth", "kind": "greet", "cond": ["M:added"],
         "texts": ["I went and looked at it. WILLEM VALE, WHO KEPT THE DOOR. The bellringer cut it deeper than the others. I "
                   "didn't ask him to.",
                   "I still pray to the Light, $n. Here, at his grave. The Cleric knows. She brought me a candle."]},
        {"npc": "elsbeth", "kind": "greet", "cond": ["M:kept"],
         "texts": ["I read him in the book most evenings. Willem Vale, ferryman. Kept the door. It's enough. It's what he was.",
                   "I still pray to the Light, $n. Here, at his grave. The Cleric knows. She brought me a candle."]},
        {"npc": "elsbeth", "kind": "greet",
         "text": "(A thin Forsaken woman in a mended grey shawl stands at a small stone, a Light's sunburst wound round her "
                 "fingers.)$B$BI come every evening. I don't pray to the Shadow. Don't send anyone to ask me to."},
        # ---- Corven ----
        {"npc": "corven_site", "kind": "greet", "cond": ["R:q4"],
         "text": "I light them at dusk now. The candles. Nobody told me to; that's rather the point, I think."},
        {"npc": "corven_site", "kind": "greet", "cond": ["A:q4"],
         "text": "Did you stand at all three? What did you think? No, wait, don't tell me yet. I want to have my own answer first, "
                 "so I can tell whether yours changes it."},
        {"npc": "corven_site", "kind": "greet",
         "text": "Acolyte Corven Dusk. I woke up four months ago in a field near Deathknell, and I've been asking questions ever "
                 "since. Mirelle says that's a good sign. Brother Halden says it's a symptom."},
        # The Weight of Faith: Corven's question (any one; his answer changes his greetings).
        {"npc": "corven_site", "kind": "option", "cond": ["I:q4"],
         "text": "You asked if power means anything without a reason. Power is only worth what you protect with it.",
         "action": "choice", "quest": "q4", "credit": "answer_credit", "marker": "protect", "emote": 273,
         "reply": "What you protect with it. Like Willem Vale at the door. He hadn't any power at all, and he used every bit of "
                  "it. ...Then the Shadow's power is only a door that holds. I can believe in a door."},
        {"npc": "corven_site", "kind": "option", "cond": ["I:q4"],
         "text": "Power is the freedom to choose your own reasons. Nobody hands them to you any more.",
         "action": "choice", "quest": "q4", "credit": "answer_credit", "marker": "choose", "emote": 273,
         "reply": "Choose my own reasons. The Lich King chose them for us, didn't he. Every one. ...Then the teaching isn't an "
                  "answer at all. It's permission to ask. Oh. Oh, I like that very much."},
        {"npc": "corven_site", "kind": "option", "cond": ["I:q4"],
         "text": "Having it is the reason. The dead who had no power are the ones who were used.",
         "action": "choice", "quest": "q4", "credit": "answer_credit", "marker": "strength", "emote": 274,
         "reply": "So we hold on to it so no one takes it again. That's... true. It's also what the angry ones say, in the "
                  "square. I'll think about it, $n. I'll think about it for a long time."},
        {"npc": "corven_shrine", "kind": "greet", "cond": ["R:q4"],
         "text": "I come back here sometimes. The darkhounds keep coming back too. We have that in common, the darkhounds and I."},
        {"npc": "corven_shrine", "kind": "greet",
         "text": "(Corven kneels at the worn stone priest, not quite praying.)$B$BHe hasn't got a face any more. Neither have some "
                 "of us. Keep the hounds off, would you? I'd like to finish my thought."},
        # The Bell for the Forgotten: the smithy, and the opening.
        {"npc": 2136, "kind": "option", "cond": ["I:q5"],
         "text": "Brother Halden Wick asks if you'll mend the old chapel bell. It's cracked, and the clapper's rusted.",
         "action": "credit", "quest": "q5", "credit": "smith_credit", "emote": 1,
         "reply": "A bell? I make swords, friend. ...Give it here. Crack's only in the lip; I can stitch that with a bronze bead "
                  "and a lot of swearing. Clapper wants a new pin. Come back in an hour and don't let Halden near the forge, he'll "
                  "tell me I'm doing it wrong."},
        {"npc": "mirelle_site", "kind": "option", "cond": ["I:q5"], "text": "The bell's hung. Brill's ready, Cleric.",
         "action": "credit", "quest": "q5", "credit": "ceremony_credit", "emote": 2,
         "reply": "Then we begin. (Mirelle turns to the gathered town.) This is not a house of the Light, and it is not a house "
                  "of the Dark Lady. It is yours. Come here for strength, or for memory, or only for somewhere quiet to sit. No "
                  "one in this room will tell you what you are. Halden: the bell."},
        # ---- The chapel, open ----
        {"npc": "mirelle", "kind": "greet", "cond": ["R:endures.town"],
         "text": "The chapel's full most evenings, $n, and half of them don't believe a word I say. I've never been so pleased "
                 "with a congregation."},
        {"npc": "mirelle", "kind": "greet",
         "texts": ["Sit, if you like. You needn't believe anything. The benches don't check.",
                   "The Forgotten Shadow asks very little: that you belong to yourself. Most days, that's plenty to be going on "
                   "with.",
                   "Halden rang the bell at dusk again. Nobody asked him to. I've stopped asking him not to."]},
        {"npc": "mirelle", "kind": "option", "cond": ["R:q5"], "text": "What does the Forgotten Shadow actually teach?",
         "action": "say", "emote": 1,
         "reply": "Respect for ourselves and our dead, because no one else will give it. Tenacity, because we endured what should "
                  "have ended us. Power, so no one decides for us again. It isn't a creed, $n. It's a description of what it "
                  "takes to stay yourself. Anyone who tells you to obey it hasn't understood it."},
        {"npc": "mirelle", "kind": "option", "cond": ["R:q5", "R:surgeon.q5"],
         "text": "I hear you visit the Surgeon's Hall in the evenings.", "action": "say", "emote": 1,
         "reply": "Some of Rane's patients ask for me. Not for prayers. They want someone to sit with them who isn't measuring "
                  "anything. Elspeth pretends to disapprove. She saves me a chair."},
        {"npc": "mirelle_hall", "kind": "greet",
         "text": "(Mirelle sits beside a cot with her hands folded, saying nothing at all, which the patient seems to find a "
                 "great comfort.)$B$BEvening, $n. I'm not here as a priestess. I'm here as company. It's much harder."},
        {"npc": "corven", "kind": "greet", "cond": ["M:protect"],
         "texts": ["Candles, $n? The black ones are for remembering. The white ones are for light to read by. I sell both. I "
                   "think of them as the same thing, most days.",
                   "I've been thinking about doors. Willem Vale's door. Ours. What it means to hold one."]},
        {"npc": "corven", "kind": "greet", "cond": ["M:choose"],
         "texts": ["Candles, $n? Choose your own; I've stopped recommending. It turns out people like being asked.",
                   "I gave a sermon last week. Mirelle let me. It was all questions. Three people walked out and eleven stayed "
                   "to argue."]},
        {"npc": "corven", "kind": "greet", "cond": ["M:strength"],
         "texts": ["Candles, $n? ...I've been sparring with the Deathguard in the mornings. Mirelle says it's healthy to be "
                   "able to hold on to things. She also says it's healthy to be able to let go of them. I'm working on the first one.",
                   "Strength is the reason. I still think so. I'm just less sure what it's the reason for."]},
        {"npc": "corven", "kind": "greet", "text": "Candles and reagents, $n. And questions, free of charge."},
        {"npc": "corven", "kind": "option", "cond": ["R:q5"], "text": "Let me see your candles and reagents.", "action": "vendor"},
        {"npc": "halden", "kind": "greet",
         "texts": ["I keep the candles at the wall lit. Dawn and dusk. You'd be surprised how many names one candle covers.",
                   "Bell's in good voice. Better than mine ever was.",
                   "Don't let the Cleric make you sit through a sermon. There's no sermon. She just likes watching people expect one."]},
        # Halden: the house's chapel set, and the names added to the wall since (other lines' dead, as they're laid to rest).
        {"npc": "halden", "kind": "option", "cond": ["R:q5"],
         "text": "Have you anything for a house? A candle, perhaps, and something for the wall.",
         "action": "buy", "arg": 7500, "marker": "house_set", "emote": 2,
         "reply": "A memorial candle, a little Shadow hanging the Cleric's acolytes stitch, and a book of reflections, blank. "
                  "Seventy-five silver, which goes to the roof. I'll have Corven carry them over. He'll want to know who the "
                  "candle's for. Don't tell him; it's good for him."},
        {"npc": "halden", "kind": "option", "cond": ["R:q5", "R:grave.bell"],
         "text": "Whose names are on the wall from the cemetery?", "action": "say", "emote": 1,
         "reply": "Hollin, Hale, Fairweather and Shaw, the ones Weller wrote twice. They asked to be put on the wall living. Mercy "
                  "said she'd rather read her own name now than have strangers read it later. Hard to argue with."},
        {"npc": "halden", "kind": "option", "cond": ["R:q5", "R:gallows.nomasters"],
         "text": "Have the thirty-one from under the hill been added?", "action": "say", "emote": 1,
         "reply": "One a week. Gideon Hale cuts the stones and I cut the wall. Thirty-one weeks, $n. I've never minded a job "
                  "less."},
        {"npc": "halden", "kind": "option", "cond": ["R:q5", "R:customer.closing"],
         "text": "Are Tobias Balnir and Marian Hale on the wall?", "action": "say", "emote": 1,
         "reply": "Side by side. Old Wicke came and stood in front of it for an hour and didn't buy a thing. I've never seen him "
                  "not sell something for an hour."},
        {"npc": "elsbeth_chapel", "kind": "greet",
         "text": "I don't pray here. I just sit. The Cleric says that counts for something. I haven't decided what."},
        {"npc": "mercy_chapel", "kind": "greet",
         "text": "We come in the evenings, Edith and I. It's the one place in Brill nobody stares. Everyone here is busy being "
                 "quiet."},
        {"npc": "edith_chapel", "kind": "greet",
         "text": "I sewed the cushions for the front bench. Nobody knows. I like it that way."},
        {"npc": "laborer", "kind": "greet",
         "texts": ["Rudd says the chapel gets the good stone. The library gets the good stone too. Rudd says a lot of things.",
                   "Mind the scaffold. It's mostly holding.",
                   "That bellringer's been up since before the bats. Does he sleep? Do any of us?"]},
        {"npc": "oswin", "kind": "greet",
         "text": "Oswin Thatcher. Jamie Nore sent me to check the builders aren't robbing the town. They're not. They're just slow. "
                 "Halden's tenons are better than mine, which I will deny to my grave. My second one."},
    ],
}
