# SPDX-License-Identifier: GPL-3.0-or-later
"""The Reclamation Library (a Community Project, opened by Brill Endures: tools/town/endures.py).

Edmund Rook, once a tutor in a house with a library, writes everything down because he's afraid of
forgetting the rest; he has forty-one books in crates in the inn's stable and wants the old customs office
on Stillhome Lane (the lane between it and Apothecary Johaan's house, on Brill's west edge) for a library.
Maela Quill, a census clerk in life, keeps the records and can't abide a wrong date; Tobias Wren binds books
and writes poems in the margins; Nora Bell comes looking for her family. Five quests: the office, its
flooded cellar and the books left at Garren's Haunt; shelves (hardwood from the dead oaks west of town,
Rudd Carver's hinges, Abigail Shiel's parchment); the census of a Lordaeron street whose people now live in
Brill without knowing it (Thomas Arlento and Mrs. Winters were neighbours as children: their greetings
change); the Cinderford chronicle taken back from the Scarlet Crusade's collectors at Solliden Farmstead;
the opening (the player donates one of three things: a child's slate, a plague-year crown, the herald's
broadsheet about the Andorhal grain). Then the library stands (Duskwood_HumanTwoStory), with Edmund's Lost
Pages daily, Maela's growing collection (her options grow with the other questlines finished), Tobias's
writing supplies and the house's library set, Nora at the reading tables, readers by day. Edmund reads at
the chapel in the evenings and collects records at the caravan office by day once they're open.

The site: Brill's west edge, the library's door toward the town centre, clear of Johaan's yard (its frame
below: the library's own coordinates; the customs office, a burnt farmhouse, stands in it until the library
opens). The library's floor is 0.5 below its origin (the vmaps' collision); the office has no floor (the
terrain's, flat here at 35.2). Out in Tirisfal the heights are those of the game's own spawns beside them.
"""
import math


def _at(frame, lx, ly):
    ox, oy, deg = frame
    o = math.radians(deg)
    return ox + lx * math.cos(o) - ly * math.sin(o), oy + lx * math.sin(o) + ly * math.cos(o)


# The library (its door at local (12.25, -7.5), the -y side, toward the town centre).
LIBRARY = (2223.4, 344.6, 70.0)
LIBRARY_Z = 37.0         # its origin; the floor is 0.5 below (36.5), a step above the ground at the door
FLOOR = 36.5
# The customs office (a burnt farmhouse) in the library's main room, its front door (its local (1.6, 8.6))
# toward the town too.
OFFICE = (*_at(LIBRARY, 5.0, -1.5), 250.0)
OFFICE_Z = 34.95
GROUND = 35.2            # Stillhome Lane's flat ground
# The chapel's frame (tools/town/chapel.py), for Edmund reading there in the evenings.
CHAPEL = (2403.5, 406.0, 210.0)


def T(lx, ly, z, turn=0.0):
    """A spawn by the library's own coordinates (turn: degrees from its +x)."""
    x, y = _at(LIBRARY, lx, ly)
    return [0, round(x, 2), round(y, 2), z, round(math.radians(LIBRARY[2] + turn) % (2 * math.pi), 4)]


def S(lx, ly, z, turn=0.0):
    """A spawn by the customs office's own coordinates (its front door at +y)."""
    x, y = _at(OFFICE, lx, ly)
    return [0, round(x, 2), round(y, 2), z, round(math.radians(OFFICE[2] + turn) % (2 * math.pi), 4)]


def W(x, y, z, deg=0.0):
    return [0, x, y, z, round(math.radians(deg) % (2 * math.pi), 4)]


LINE = {
    "title": "The Reclamation Library",
    "stages": [["R:endures.endures"], ["R:q1"], ["R:q2"], ["R:q3"], ["R:q4"], ["R:q5"], ["M:house_set"]],
    "quests": [
        {
            "id": "q1", "title": "More Than Ashes", "giver": "edmund_site", "ender": "edmund_site", "min_level": 8,
            "log": "Inspect the old customs office on Stillhome Lane and its flooded cellar, recover 5 surviving books from the "
                   "abandoned Garren farm at Garren's Haunt, retrieve the office's record chest, and obtain Magistrate Sevren's "
                   "permission to convert the property.",
            "offer": (
                "You're $n. I know because I wrote it down when you passed the inn on Tuesday. I write everything down. It isn't "
                "a habit, it's a precaution.$B$B"
                "Edmund Rook. I was a tutor once, in a house with a library. I remember the smell of that room better than the "
                "faces of the children, and that frightens me more than anything the Scourge ever did.$B$B"
                "I have forty-one books in crates in the inn's stable, and the horses are eating the bindings. Brill needs a "
                "library. Not for me: for every one of us who woke up with half a life missing.$B$B"
                "The old customs office on Stillhome Lane is empty. Look it over with me, cellar and all. The Garrens out at "
                "Garren's Haunt kept more books than any house in the parish; bring back whatever the gnolls haven't eaten. "
                "There's a record chest in the office somewhere. And the Magistrate must agree, or none of this is legal, and I "
                "would hate to be dead and a squatter."),
            "progress": "Five books, $n. I'd settle for four. I wouldn't settle for four. I'd write down that I settled and then "
                        "lie awake about it.",
            "done": (
                "(Edmund turns the pages of a small green primer, swollen with damp, and stops at the flyleaf.)$B$B"
                "\"For my Davey, who will read it before I can. Mother.\"$B$B"
                "I don't know who Davey was. I don't know if he learned to read. I'm going to find out.$B$B"
                "...Not today. Today this goes on a shelf, and it's the first book in the Reclamation Library, and I'm going to "
                "write down that it was."),
            "return": "Return to Edmund Rook at the old customs office on Stillhome Lane in Brill.",
            "objectives": [("credit", "inspect_credit", 2, "The office and its flooded cellar inspected"),
                           ("credit", "book_credit", 5, "Surviving books recovered"),
                           ("credit", "chest_credit", 1, "The office's record chest"),
                           ("credit", "sevren_credit", 1, "Magistrate Sevren's permission")],
            "items": [(955, 2)], "money": 1500, "xp": 3,
        },
        {
            "id": "q2", "title": "Shelves for the Dead", "giver": "tobias_site", "ender": "tobias_site", "prev": "q1",
            "min_level": 8,
            "log": "Gather 8 pieces of hardwood from the dead oaks west of Brill, get hinges and brackets from Rudd Carver at the "
                   "builder's yard and repairable parchment from Abigail Shiel, then help Tobias Wren assemble the first shelves "
                   "and mend the cellar window.",
            "offer": (
                "(The bookbinder speaks so quietly you have to lean in.)$B$B"
                "Tobias Wren. I bind books. Bound, I should say; I haven't had a book to bind since the plague. Edmund has "
                "forty-one, and every one of them is coming apart.$B$B"
                "They need shelves before they need me. Dry ones, off the floor, out of the light. The oaks the blight killed, "
                "west of town past the last houses: they've stood dead so long they've seasoned on the root. Eight good lengths. "
                "Rudd Carver has hinges and brackets, if you ask him nicely, and Abigail Shiel sells parchment I can use to mend "
                "the torn leaves.$B$B"
                "Then help me put the first shelves together. And the cellar window, before the next rain. Water is the only "
                "thing books are afraid of. Well. Water and the Scarlet Crusade."),
            "progress": "Dry wood, dry paper, dry cellar. It sounds simple. Most simple things are, until it rains.",
            "done": (
                "(Tobias runs a thumb along the first shelf and doesn't seem to notice he's smiling.)$B$B"
                "Level. Even the dead can build level.$B$B"
                "I wrote something in the margin of Edmund's ledger while you were gone. Don't tell him. \"Oak that died "
                "standing / holds the books of those who fell. / Neither minds the weight.\" It isn't very good. Margins are "
                "where you put the things that aren't very good."),
            "return": "Return to Tobias Wren at the old customs office on Stillhome Lane in Brill.",
            "objectives": [("credit", "hardwood_credit", 8, "Seasoned hardwood"),
                           ("credit", "hinges_credit", 1, "Hinges and brackets from the builder's yard"),
                           ("credit", "parchment_credit", 1, "Repairable parchment from Abigail Shiel"),
                           ("credit", "assembled_credit", 2, "Shelves assembled and the cellar window mended")],
            "items": [(858, 3)], "money": 2000, "xp": 4,
        },
        {
            "id": "q3", "title": "The Names We Carried", "giver": "maela_site", "ender": "maela_site", "prev": "q2",
            "min_level": 8,
            "log": "Obtain the surviving census records from Royal Overseer Bauhaus in the Undercity, recover the Agamand mill's "
                   "ledger from the barn at Agamand Mills, then record the memories of Thomas Arlento, Mrs. Winters and Doreen "
                   "Beltis in Brill.",
            "offer": (
                "Maela Quill. I took the census of Lordaeron's eastern ward three times, and I can tell you the household of "
                "every door on Wheelwrights' Row, and I would very much like people to stop telling me the bakery was on the "
                "corner. It was not on the corner.$B$B"
                "Three people in Brill gave me the same street when Edmund asked where they lived before. Wheelwrights' Row. None "
                "of them knows the others. They walk past each other every day.$B$B"
                "I want the records. The Undercity kept what the Crown's clerks didn't burn: Royal Overseer Bauhaus has the "
                "census rolls, if you can make him part with a copy. The Agamand mill kept a ledger of every family in the "
                "eastern ward that bought their flour; it's in the barn at Agamand Mills, if the bones there haven't sat on it. "
                "Then talk to them: Thomas Arlento, Mrs. Winters at the general store, Doreen Beltis. Write down what they "
                "remember. Exactly what they remember, $n. Not what they'd like to."),
            "progress": "Exactly, $n. If they say the bakery was on the corner, write that down, and write that they were wrong.",
            "done": (
                "(Maela reads your notes twice and then sets the census roll beside them, one line at a time.)$B$B"
                "Arlento, number nine, Wheelwrights' Row. Winters, then Tolley, number eleven. Next door. They shared a wall for "
                "fourteen years.$B$B"
                "He's been buying lamp oil from her since the autumn. She's been overcharging him, I expect. ...No, don't tell "
                "them. I already sent a note. I'm told he went straight to the store and stood there for a quarter of an hour "
                "and neither of them said a word, and then she gave him the oil for nothing.$B$B"
                "This is what an archive is for. Not the past. The people still in it."),
            "return": "Return to Maela Quill at the old customs office on Stillhome Lane in Brill.",
            "objectives": [("credit", "census_credit", 1, "The Undercity's census records"),
                           ("credit", "ledger_credit", 1, "The Agamand mill's ledger"),
                           ("credit", "memory_credit", 3, "Residents' memories recorded")],
            "items": [(2455, 3)], "money": 2500, "xp": 4,
        },
        {
            "id": "q4", "title": "The Missing Chapter", "giver": "edmund_site", "ender": "edmund_site", "prev": "q3",
            "min_level": 9,
            "log": "Search the Scarlet Crusade's record store in the barn at Solliden Farmstead, deal with the Scarlet collectors "
                   "there, recover the Cinderford chronicle's missing pages, and reassemble the chronicle at Edmund Rook's "
                   "worktable in Brill.",
            "offer": (
                "Cinderford. A village a day's walk north of here, before. It burned in the second month of the plague, and "
                "everyone knows the story: the villagers barred the road against the sick, and the sick burned it down around "
                "them. They tell it in the Undercity as a lesson about the living.$B$B"
                "The parish clerk kept a chronicle. I thought it was lost. It isn't. A trader swears he saw it in a crate at "
                "Solliden Farmstead last month, with the Scarlet Crusade's seal on the lid: they've been collecting what they "
                "call plague-tainted writings from every ruin in Tirisfal, and carting them to the Solliden barn to sort and "
                "burn.$B$B"
                "I want that chronicle, $n. Whatever it says. Go to the barn, find their record store, and bring me every page "
                "you can. The collectors won't hand it over, and I don't suppose you'll ask them twice."),
            "progress": "Every page. A chronicle with the end torn out isn't history. It's a rumour with a binding.",
            "done": (
                "(Edmund reads the last entry with you, and then sits for a long while with his hand flat on the page.)$B$B"
                "They didn't bar the road. They opened the church to everyone, sick and well, and sat them in the same pews, "
                "because nobody knew yet what the sickness was, and the clerk wrote that it would be a sin to choose. And then "
                "they died. Together. The Crown's men burned the village afterward, to be safe.$B$B"
                "It's worse than the story. It's also true. It goes in a case by the door, and anyone in Brill can read it."),
            "return": "Return to Edmund Rook at the old customs office on Stillhome Lane in Brill.",
            "objectives": [("credit", "store_credit", 1, "The Scarlet record store searched"),
                           ("kill", "collector", 5, "Scarlet Collectors"),
                           ("credit", "cpage_credit", 3, "The chronicle's missing pages"),
                           ("credit", "chronicle_credit", 1, "The chronicle reassembled and its last entry read")],
            "items": [(929, 2)], "money": 3000, "xp": 5,
        },
        {
            "id": "q5", "title": "An Open Book", "giver": "edmund_site", "ender": "edmund_site", "prev": "q4", "min_level": 9,
            "log": "Deliver Edmund Rook's invitations to Hamlin Atkins, Innkeeper Renee, Executor Zygand and Faruza, help Tobias "
                   "Wren finish the reading table and sort 6 books into their collections, donate a recovered artifact, then "
                   "attend the library's opening.",
            "offer": (
                "It's nearly ready. Shelves, tables, a case for the chronicle, Maela's archive, Tobias's poems in every margin "
                "he thinks I won't check.$B$B"
                "And nobody will come.$B$B"
                "No, I've thought about it. I've written it down. The living had libraries because they had time. We have "
                "nothing but time, and we spend it standing in doorways. Who will walk in?$B$B"
                "Take these invitations. Hamlin Atkins, the innkeeper, the Executor, Faruza. If those four come, the rest of "
                "Brill will follow to see why. Help Tobias with the last table; there are books on every surface that need "
                "sorting into their collections. And bring something for the case by the door, $n. One thing you found out "
                "there that ought to be remembered. A library ought to begin with a gift."),
            "progress": "Did they say they'd come? Did they say it as though they meant it? Write down how they said it.",
            "done": (
                "(They come: Hamlin with mushroom dirt still on his boots, the innkeeper with a basket, the Executor, who stands "
                "at the back with his arms folded and reads for an hour. And then the rest of Brill, to see why.)$B$B"
                "(Near closing, a woman at the far table makes a small sound. She's holding a letter from the bottom of one of "
                "Edmund's crates. She doesn't put it down when the lamps are dimmed, and nobody asks her to leave.)$B$B"
                "That's Nora Bell. She's been looking for her family since the spring. I think, $n, she's found someone.$B$B"
                "I'm going to write down that this happened. And then I'm going to stop writing for a while and watch it."),
            "return": "Return to Edmund Rook at the old customs office on Stillhome Lane in Brill.",
            "objectives": [("credit", "invite_credit", 4, "Invitations delivered"),
                           ("credit", "table_credit", 1, "The last reading table finished"),
                           ("credit", "sort_credit", 6, "Books sorted into their collections"),
                           ("credit", "donate_credit", 1, "A recovered artifact donated")],
            "items": [(3385, 3)], "money": 5000, "xp": 5,
        },
        # Lost Pages: the library's daily (once it's open).
        {
            "id": "lost", "title": "Lost Pages", "giver": "edmund", "ender": "edmund", "prev": "q5",
            "repeat": "daily", "min_level": 8,
            "log": "Recover 3 lost documents from the abandoned places of Tirisfal: the barns at Garren's Haunt and Agamand Mills, "
                   "the farmhouse at Solliden Farmstead and the sheds behind Cold Hearth Manor.",
            "offer": (
                "Every abandoned house in Tirisfal has paper in it. Letters behind the dresser, a diary under a mattress, deeds "
                "in a tin, a grocer's bill nobody will ever pay. The rain is getting to them faster than we are.$B$B"
                "Maela keeps a list of where people have seen them: the barns at Garren's and the mills, the Solliden "
                "farmhouse, the sheds behind Cold Hearth. Bring me three. I'll write down where you found them.$B$B"
                "It isn't glamorous. Nobody will thank you for a grocer's bill. But one day someone will walk in here and ask "
                "whether anyone remembers a family called Brewer, and Maela will open a drawer."),
            "progress": "Three, $n. Anything with writing on it. Anything at all.",
            "done": (
                "(Edmund unfolds each one as if it might break, and copies it into the register before he reads it properly.)$B$B"
                "A recipe. A bill of sale for a goat. A love letter with the name scratched out. All of it, $n. All of it "
                "counts."),
            "return": "Return to Edmund Rook in the Reclamation Library.",
            "objectives": [("credit", "lost_credit", 3, "Lost documents recovered")],
            "money": 1500, "xp": 2,
        },
    ],
    # Each resident asked once and each invitation delivered once; what was donated for the case; Elinor Harrow's
    # letters copied for the collection; the house's library set bought.
    "markers": ["asked_thomas", "asked_winters", "asked_doreen", "invited_hamlin", "invited_renee", "invited_zygand",
                "invited_faruza", "slate", "crown", "broadsheet", "letters", "house_set"],
    "npcs": [
        # Before the library opens: at the customs office (its yard faces Stillhome Lane).
        {"id": "edmund_site", "name": "Edmund Rook", "subname": "Librarian", "display": 2651, "level": 20,
         "from": 1, "until": 6, "spawns": [S(5.0, 10.2, GROUND, 90)]},
        {"id": "tobias_site", "name": "Tobias Wren", "subname": "Bookbinder", "display": 2634, "level": 18,
         "from": 2, "until": 6, "spawns": [S(-3.5, 10.6, GROUND, 90)]},
        {"id": "maela_site", "name": "Maela Quill", "subname": "Archivist", "display": 2667, "level": 18,
         "from": 3, "until": 6, "spawns": [S(4.0, -2.0, 35.12, 180)]},
        {"id": "patron_site", "name": "Library Patron", "display": [2669, 2633], "level": 10, "flags": ["gossip"],
         "from": 4, "until": 6, "when": "day", "spawns": [S(-3.0, 2.0, 35.1, 180), S(3.0, 1.5, 35.15, 90)]},
        {"id": "laborer", "name": "Builder's Yard Laborer", "display": [3516, 1638, 1604], "level": 15, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "wander": 3, "spawns": [S(-8.8, 3.0, 35.43), S(8.0, -10.5, 35.59)]},
        {"id": "oswin", "name": "Oswin Thatcher", "subname": "Carpenter", "display": 1638, "level": 25, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "spawns": [S(-9.0, 5.5, 35.46, 20)]},
        # The Missing Chapter: the Crusade's collectors at the Solliden barn (its floor, and the yard outside).
        {"id": "collector", "name": "Scarlet Collector", "display": [2466, 2477], "hostile": True, "faction": 67,
         "level": (10, 11), "type": 7, "unit_class": 1, "health": 1, "damage": 1, "gold": 45, "wander": 3,
         "spawns": [W(2343.0, 1310.0, 34.05, 2.0), W(2326.0, 1318.0, 34.05, 5.0), W(2338.0, 1320.0, 34.05, 4.0),
                    W(2358.0, 1314.0, 33.33, 3.1), W(2334.0, 1332.0, 33.33, 1.6)]},
        # The library, open.
        {"id": "edmund", "name": "Edmund Rook", "subname": "Head Librarian", "display": 2651, "level": 20,
         "from": 6, "spawns": [T(15.6, -2.0, FLOOR, 180)]},
        {"id": "maela", "name": "Maela Quill", "subname": "Archivist", "display": 2667, "level": 18, "flags": ["gossip"],
         "from": 6, "spawns": [T(12.0, 7.5, FLOOR, -90)]},
        {"id": "tobias", "name": "Tobias Wren", "subname": "Bookbinder", "display": 2634, "level": 18,
         "flags": ["gossip", "vendor"], "from": 6, "spawns": [T(-2.0, -1.0, FLOOR)],
         "vendor": [39354, 10648, 39501, 39505, 39489, 3766, 3767]},
        {"id": "nora", "name": "Nora Bell", "display": 2665, "level": 12, "flags": ["gossip"],
         "from": 6, "spawns": [T(11.5, -5.5, FLOOR, 90)]},
        {"id": "patron", "name": "Library Patron", "display": [2669, 2633], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "day", "spawns": [T(3.0, 0.5, FLOOR, 180), T(13.0, 1.0, FLOOR, -90)]},
        # Edmund's rounds: reading at the chapel in the evenings, collecting records at the caravan office by day.
        {"id": "edmund_chapel", "name": "Edmund Rook", "subname": "Head Librarian", "display": 2651, "level": 20,
         "flags": ["gossip"], "from": 6, "needs": {"chapel": 6}, "when": "evening",
         "spawns": [[0, *[round(v, 2) for v in _at(CHAPEL, 3.3, -4.5)], 37.2, round(math.radians(CHAPEL[2] + 180), 4)]]},
        {"id": "edmund_caravan", "name": "Edmund Rook", "subname": "Head Librarian", "display": 2651, "level": 20,
         "flags": ["gossip"], "from": 6, "needs": {"caravan": 6}, "when": "day",
         "spawns": [W(2185.5, 285.0, 42.1, 35.5)]},   # (in the caravan office, by its ledgers: tools/town/caravan.py)
    ],
    "credits": [
        {"id": "inspect_credit", "name": "The office and its flooded cellar inspected"},
        {"id": "book_credit", "name": "Surviving books recovered"},
        {"id": "chest_credit", "name": "The office's record chest"},
        {"id": "sevren_credit", "name": "Magistrate Sevren's permission"},
        {"id": "hardwood_credit", "name": "Seasoned hardwood"},
        {"id": "hinges_credit", "name": "Hinges and brackets from the builder's yard"},
        {"id": "parchment_credit", "name": "Repairable parchment from Abigail Shiel"},
        {"id": "assembled_credit", "name": "Shelves assembled and the cellar window mended"},
        {"id": "census_credit", "name": "The Undercity's census records"},
        {"id": "ledger_credit", "name": "The Agamand mill's ledger"},
        {"id": "memory_credit", "name": "Residents' memories recorded"},
        {"id": "store_credit", "name": "The Scarlet record store searched"},
        {"id": "cpage_credit", "name": "The chronicle's missing pages"},
        {"id": "chronicle_credit", "name": "The chronicle reassembled and its last entry read"},
        {"id": "invite_credit", "name": "Invitations delivered"},
        {"id": "table_credit", "name": "The last reading table finished"},
        {"id": "sort_credit", "name": "Books sorted into their collections"},
        {"id": "donate_credit", "name": "A recovered artifact donated"},
        {"id": "lost_credit", "name": "Lost documents recovered"},
    ],
    "objects": [
        # ---- The customs office, until the library opens (stages 1 to 5) ----
        {"id": "office", "name": "Old Customs Office", "display": 7464, "type": 33, "from": 1, "until": 6,
         "spawns": [S(0.0, 0.0, OFFICE_Z)]},
        # More Than Ashes: the counter, the cellar, the chest.
        {"id": "counter", "name": "Customs Counter", "display": 7732, "from": 1, "until": 6, "spawns": [S(6.2, 3.5, 35.19)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "inspect_credit"}]},
        {"id": "cellar", "name": "Flooded Cellar Hatch", "display": 6481, "from": 1, "until": 6,
         "spawns": [S(-4.5, -4.0, 34.95)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "inspect_credit"}]},
        {"id": "office_chest", "name": "Water-Stained Record Chest", "quest_only": True, "display": 1, "from": 1, "until": 6,
         "spawns": [S(5.5, -6.5, 35.21, 30)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "chest_credit"}]},
        # From the first quest done: Edmund's desk and his crates of books, the sign; Tobias's shelves and the window.
        {"id": "desk", "name": "Edmund's Desk", "display": 581, "from": 2, "until": 6, "spawns": [S(5.0, 11.6, GROUND, 90)]},
        {"id": "desk_books", "name": "Edmund's Notes", "display": 107, "from": 2, "until": 6,
         "spawns": [S(5.0, 11.6, GROUND + 1.12, 70)]},
        {"id": "crates", "name": "Crate of Books", "display": 335, "from": 2, "until": 6,
         "spawns": [S(8.0, 10.5, GROUND, 20), S(8.6, 12.0, GROUND, 70)]},
        {"id": "crate_books", "name": "Stack of Books", "display": 43, "from": 2, "until": 6,
         "spawns": [S(8.0, 10.5, GROUND + 1.03, 40), S(8.6, 12.0, GROUND + 1.03, 110)]},
        {"id": "unbuilt", "name": "Unassembled Shelves", "quest_only": True, "display": 1108, "from": 2, "until": 6, "spawns": [S(-5.0, 6.2, 35.15, 70)],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "assembled_credit"}]},
        {"id": "window", "name": "Broken Cellar Window", "display": 6716, "scale": 1.5, "from": 2, "until": 6,
         "spawns": [S(-7.6, -5.0, 35.1, 90)],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "assembled_credit"}]},
        # From the second: shelves and a reading table in the office (the table is Edmund's worktable after).
        {"id": "office_shelves", "name": "Bookshelf", "display": 188, "from": 3, "until": 6,
         "spawns": [S(-6.4, -1.0, 35.1), S(-6.4, 2.5, 35.14)]},
        {"id": "worktable", "name": "Edmund's Worktable", "display": 234, "from": 3, "until": 6, "spawns": [S(1.0, -2.0, 35.03)],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "chronicle_credit"}]},
        {"id": "office_chair", "name": "Chair", "display": 39, "type": 7, "from": 3, "until": 6, "spawns": [S(-0.9, -2.0, 35.03)]},
        # From the third: Maela's archive.
        {"id": "census_boxes", "name": "Census Boxes", "display": 335, "from": 4, "until": 6,
         "spawns": [S(5.8, -3.0, 35.15), S(5.8, -1.5, 35.15, 30)]},
        {"id": "records_cabinet", "name": "Records Cabinet", "display": 4, "from": 4, "until": 6,
         "spawns": [S(6.6, 0.3, 35.15, 180)]},
        # From the fourth: the chronicle in its case.
        {"id": "office_case", "name": "Locked Display Case", "display": 234, "from": 5, "until": 6,
         "spawns": [S(-3.0, -6.0, 34.99, 90)]},
        # An Open Book: the last table, and the books to be sorted.
        {"id": "last_table", "name": "Unfinished Reading Table", "display": 581, "from": 5, "until": 6,
         "spawns": [S(-1.5, 4.5, 35.17, 30)],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "table_credit"}]},
        {"id": "unsorted", "name": "Unsorted Books", "quest_only": True, "display": 107, "from": 5, "until": 6,
         "spawns": [S(-5.5, -2.5, 35.01, 20), S(-5.5, 4.2, 35.18, 80), S(4.0, -5.0, 35.11, 140), S(2.5, 5.5, 35.19, 200),
                    S(-2.0, -6.5, 35.01, 260), S(6.2, 6.2, 35.19, 320)],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "sort_credit"}]},
        # ---- Out in Tirisfal ----
        # More Than Ashes: the Garrens' books (their farmhouse and barn at Garren's Haunt).
        {"id": "garren_book", "name": "Rain-Swollen Book", "quest_only": True, "display": 1128,
         "spawns": [W(2915.25, 382.59, 31.55, 30), W(2915.38, 376.73, 31.55, 150), W(2841.6, 418.4, 20.85, 260),
                    W(2846.5, 413.2, 20.85, 80), W(2906.5, 373.0, 30.63, 200)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "book_credit",
                  "text": "(On the flyleaf: GARREN. ASK BEFORE YOU BORROW.)"}]},
        # Shelves for the Dead: the dead oaks west of town.
        {"id": "hardwood", "name": "Seasoned Deadwood", "quest_only": True, "display": 1108,
         "spawns": [W(2112.0, 352.0, 48.09, 30), W(2104.0, 371.0, 45.03, 110), W(2118.0, 389.0, 49.93, 200),
                    W(2098.0, 402.0, 54.59, 290), W(2109.0, 418.0, 57.99, 20), W(2124.0, 432.0, 64.93, 100),
                    W(2092.0, 380.0, 45.51, 190), W(2130.0, 410.0, 60.73, 280)],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "hardwood_credit"}]},
        # The Names We Carried: the Agamand mill's ledger.
        {"id": "mill_ledger", "name": "Agamand Mill Ledger", "quest_only": True, "display": 470, "spawns": [W(2827.5, 810.5, 113.61, 140)],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "ledger_credit",
                  "text": "(The mill's flour ledger, its pages stuck at the corners. Every household in the eastern ward that "
                          "bought Agamand flour, in a miller's blunt hand. WHEELWRIGHTS' ROW: no. 9, ARLENTO, 2 sacks; no. 11, "
                          "TOLLEY, 1 sack, owes; no. 14, BELTIS, 2 sacks.)"}]},
        # The Missing Chapter: the Crusade's record store in the Solliden barn.
        {"id": "store", "name": "Scarlet Sorting Table", "quest_only": True, "display": 234, "spawns": [W(2336.0, 1312.0, 34.05, 180)],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "store_credit"}]},
        {"id": "chronicle_page", "name": "Chronicle Page", "quest_only": True, "display": 164,
         "spawns": [W(2331.5, 1311.0, 34.05, 40), W(2338.5, 1316.5, 34.05, 130), W(2333.0, 1318.5, 34.05, 260)],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "cpage_credit"}]},
        # Lost Pages: documents in the abandoned places.
        {"id": "lost_doc", "name": "Lost Document", "quest_only": True, "display": 220,
         "spawns": [W(2846.0, 419.0, 20.85, 30), W(2821.0, 809.5, 113.61, 120), W(2262.97, 1319.08, 34.05, 210),
                    W(2131.5, 684.5, 37.67, 300)],
         "use": [{"cond": ["I:lost"], "quest": "lost", "credit": "lost_credit"}]},
        # ---- The library, open (stage 6 on) ----
        {"id": "library", "name": "Reclamation Library", "display": 7463, "type": 33, "from": 6,
         "spawns": [T(0.0, 0.0, LIBRARY_Z)]},
        {"id": "shelves", "name": "Bookshelf", "display": 188, "from": 6,
         "spawns": [T(-4.9, -5.2, FLOOR), T(-4.9, -2.0, FLOOR), T(-4.9, 1.2, FLOOR), T(-2.2, 3.6, FLOOR, -90),
                    T(1.0, 3.6, FLOOR, -90), T(16.6, -4.5, FLOOR, 180), T(16.6, 1.9, FLOOR, 180), T(12.0, 5.6, FLOOR, 90)]},
        {"id": "tables", "name": "Reading Table", "display": 234, "from": 6,
         "spawns": [T(9.0, -3.5, FLOOR, 90), T(9.0, 1.5, FLOOR, 90)]},
        {"id": "chairs", "name": "Chair", "display": 39, "type": 7, "from": 6,
         "spawns": [T(8.0, -5.6, FLOOR, 90), T(10.0, -5.6, FLOOR, 90), T(8.2, -0.9, FLOOR, 90), T(10.0, -0.9, FLOOR, 90)]},
        {"id": "edmund_desk", "name": "Librarian's Desk", "display": 581, "from": 6, "spawns": [T(14.5, -2.0, FLOOR)]},
        {"id": "bench", "name": "Bindery Bench", "display": 581, "from": 6, "spawns": [T(-0.5, -1.0, FLOOR)]},
        {"id": "archive_cabinet", "name": "Records Cabinet", "display": 4, "from": 6, "spawns": [T(7.5, 7.0, FLOOR)]},
        {"id": "archive_boxes", "name": "Census Boxes", "display": 335, "from": 6,
         "spawns": [T(16.0, 6.5, FLOOR), T(16.0, 8.2, FLOOR, 30)]},
        # The chronicle's case, and what was given for it.
        {"id": "case", "name": "The Cinderford Chronicle", "display": 234, "from": 6, "spawns": [T(14.0, 2.5, FLOOR, 180)]},
        # Readable books on the tables.
        {"id": "book_parish", "name": "Brill: A Parish History", "display": 184, "from": 6,
         "spawns": [T(8.6, -3.2, FLOOR + 1.34, 20)]},
        {"id": "book_primer", "name": "A Child's Primer", "display": 254, "from": 6,
         "spawns": [T(9.4, 1.8, FLOOR + 1.34, 160)]},
        {"id": "book_records", "name": "The Brill Register", "display": 470, "from": 6,
         "spawns": [T(14.5, -2.0, FLOOR + 1.12, 90)]},
        # ---- The house's library set (bought from Tobias): histories and bound journals by the bed ----
        {"id": "house_histories", "name": "Library Histories", "display": 43, "from": 7, "spawns": [["house", -0.15, 4.97, 2.12, -90]]},
        {"id": "house_journals", "name": "Bound Journals", "display": 107, "from": 7, "spawns": [["house", 0.75, 4.97, 2.12, -90]]},
    ],
    "gossip": [
        # ---- Edmund at the office ----
        {"npc": "edmund_site", "kind": "greet", "cond": ["R:q4"],
         "text": "Everyone who comes past stops at the chronicle's case. Nobody says anything. I've started writing down how long "
                 "they stand there. The longest was forty minutes. It was the Executor."},
        {"npc": "edmund_site", "kind": "greet", "cond": ["R:q2"],
         "text": "Shelves! I've arranged them three times. Maela has rearranged them four. We're both writing down who's winning."},
        {"npc": "edmund_site", "kind": "greet", "cond": ["R:q1"],
         "text": "I've a desk now. Well. A table. Under the sky. Tobias says the sky is temporary; I've written down that he said so."},
        {"npc": "edmund_site", "kind": "greet",
         "text": "(A thin Forsaken in an ink-stained coat is writing in a notebook, and doesn't stop when he looks up.)$B$BOne "
                 "moment. \"Tuesday, the stranger by the old customs office, looks capable.\" There. Hello."},
        # More Than Ashes: the Magistrate.
        {"npc": 1499, "kind": "option", "cond": ["I:q1"],
         "text": "Edmund Rook asks the town's leave to make the old customs office on Stillhome Lane a library.",
         "action": "credit", "quest": "q1", "credit": "sevren_credit", "emote": 1,
         "reply": "A library. In the customs office. The Crown taxed every sack of grain that came down that road, and the grain "
                  "killed us. ...Yes. Let it hold books. Tell Rook the deed is his for a penny a year, and that I will expect a "
                  "receipt. He'll enjoy that."},
        # Shelves for the Dead: Rudd's hinges, Abigail's parchment.
        {"npc": "endures.foreman", "kind": "option", "cond": ["I:q2"],
         "text": "Tobias Wren needs hinges and brackets for the library's shelves.",
         "action": "credit", "quest": "q2", "credit": "hinges_credit", "emote": 1,
         "reply": "The quiet one? He came by and stood at the gate for ten minutes and then went away again. Should've said. Here: "
                  "brass hinges, iron brackets, and a bag of screws I counted myself. Tell him they're a loan. Tell him I'd like "
                  "to borrow a book. Something with ships."},
        {"npc": 2118, "kind": "option", "cond": ["I:q2"],
         "text": "Tobias Wren the bookbinder needs parchment to mend torn pages.",
         "action": "credit", "quest": "q2", "credit": "parchment_credit", "emote": 1,
         "reply": "For mending? Then you want the thin stuff, not the good stuff. ...Here, four bundles. The bottom one's a bit "
                  "foxed. Tell Wren I want the first book he mends, to read, not to keep. I'll know if he's skipped the poems."},
        # ---- Tobias at the office ----
        {"npc": "tobias_site", "kind": "greet", "cond": ["R:q3"],
         "text": "(Tobias is sewing a spine and doesn't look up.)$B$BMaela's people come in to read the census. Some of them cry. "
                 "I keep handkerchiefs in the drawer now. Linen. They're the only thing I've bought for myself in ten years."},
        {"npc": "tobias_site", "kind": "greet",
         "text": "(He speaks so softly you have to lean in.)$B$BTobias. Bookbinder. Pleased. ...Sorry. I'm not used to people yet. "
                 "I'm used to paper."},
        # ---- Maela ----
        {"npc": "maela_site", "kind": "greet", "cond": ["R:q3"],
         "text": "People come in now and ask me where they lived. I tell them, $n. Exactly. Some of them argue. I enjoy that very "
                 "much."},
        {"npc": "maela_site", "kind": "greet",
         "text": "Maela Quill. Before you ask: yes, I remember. I remember almost everything. The trouble is that nobody else does, "
                 "and they will insist."},
        # The Names We Carried: the census, and the three of Wheelwrights' Row.
        {"npc": 10781, "kind": "option", "cond": ["I:q3"],
         "text": "Maela Quill of the Brill library asks for a copy of the eastern ward's census rolls.",
         "action": "credit", "quest": "q3", "credit": "census_credit", "emote": 1,
         "reply": "The eastern ward. Quill. Of course it's Quill; she wrote half of them. ...The Dark Lady's census takes precedence, "
                  "you understand, but a copy can be made. There. Tell her the Undercity's clerks would like their pen back. She "
                  "knows which one."},
        {"npc": 2309, "kind": "option", "cond": ["I:q3", "!M:asked_thomas"],
         "text": "Maela Quill is recording where Brill's people lived before. Do you remember your old street?",
         "action": "credit", "quest": "q3", "credit": "memory_credit", "marker": "asked_thomas", "emote": 1,
         "reply": "Wheelwrights' Row. Number nine. There was a girl next door who threw apples at our cat and then cried when it "
                  "ran off. Freckles. A pinafore with blue birds on it. I can't for the life of me remember her name. Funny, the "
                  "things that stay."},
        {"npc": 2134, "kind": "option", "cond": ["I:q3", "!M:asked_winters"],
         "text": "Maela Quill is recording where Brill's people lived before. Do you remember your old street?",
         "action": "credit", "quest": "q3", "credit": "memory_credit", "marker": "asked_winters", "emote": 1,
         "reply": "Before I was Winters? Tolley. Number eleven, Wheelwrights' Row. Mother made me wear a pinafore with blue birds "
                  "on it, Light knows why. There was a boy next door with a cat I hated. ...Why are you looking at me like that?"},
        {"npc": 2311, "kind": "option", "cond": ["I:q3", "!M:asked_doreen"],
         "text": "Maela Quill is recording where Brill's people lived before. Do you remember your old street?",
         "action": "credit", "quest": "q3", "credit": "memory_credit", "marker": "asked_doreen", "emote": 1,
         "reply": "Wheelwrights' Row, I think. Fourteen. Or forty. Mother kept bees on the roof, and the bakery was on the corner. "
                  "...It wasn't? Well, write it down how I said it. The bees are true."},
        # The two neighbours, after.
        {"npc": 2309, "kind": "greet", "cond": ["R:q3"],
         "texts": ["Bess Tolley. Number eleven. She threw apples at my cat. Forty years, and she's been selling me lamp oil since "
                   "the autumn. She still won't apologise about the cat.",
                   "I take my supper to the general store most evenings. We don't eat, either of us. We sit on the step and argue "
                   "about what the street looked like. She's usually right. I don't tell her."]},
        {"npc": 2134, "kind": "greet", "cond": ["R:q3"],
         "text": "Tommy Arlento comes by every evening and sits on my step. I don't charge him for the oil any more. Don't tell "
                 "anyone; I've a reputation."},
        # ---- An Open Book: the invitations and the gift ----
        {"npc": 3547, "kind": "option", "cond": ["I:q5", "!M:invited_hamlin"],
         "text": "Edmund Rook invites you to the opening of the Reclamation Library.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "invited_hamlin", "emote": 3,
         "reply": "A library! Have they anything on mushrooms? I've got a few things to say about mushrooms, and nobody ever writes "
                  "them down. I'll come. I'll bring a basket."},
        {"npc": 5688, "kind": "option", "cond": ["I:q5", "!M:invited_renee"],
         "text": "Edmund Rook invites you to the opening of the Reclamation Library.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "invited_renee", "emote": 3,
         "reply": "Edmund? The one who kept his books in my stable? The horses will miss him. I'll come, and I'll bring something "
                  "for the table, and if he writes down what I wear I'll know."},
        {"npc": 1515, "kind": "option", "cond": ["I:q5", "!M:invited_zygand"],
         "text": "Edmund Rook invites you to the opening of the Reclamation Library.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "invited_zygand", "emote": 3,
         "reply": "A library. Hm. The Deathguard aren't much for reading. ...I'll come. Someone should make sure the books aren't "
                  "Scarlet propaganda. I'll need to read a great many of them, to be sure."},
        {"npc": 2114, "kind": "option", "cond": ["I:q5", "!M:invited_faruza"],
         "text": "Edmund Rook invites you to the opening of the Reclamation Library.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "invited_faruza", "emote": 3,
         "reply": "Books are paper, and paper is pressed herbs, more or less. I'll come. Tell him to keep the herbals somewhere dry, "
                  "or I'll take them home with me."},
        {"npc": "edmund_site", "kind": "option", "cond": ["I:q5"],
         "text": "For the case by the door: a child's slate from a Tirisfal schoolroom, the lesson still on it.",
         "action": "choice", "quest": "q5", "credit": "donate_credit", "marker": "slate", "emote": 2,
         "reply": "A IS FOR APPLE. B IS FOR BREAD. ...Somebody's sleeve rubbed out the rest. That's what we lost, $n. Not kings. "
                  "The lesson for Tuesday. It goes beside the chronicle."},
        {"npc": "edmund_site", "kind": "option", "cond": ["I:q5"],
         "text": "For the case by the door: a silver crown of Lordaeron, struck the year of the plague.",
         "action": "choice", "quest": "q5", "credit": "donate_credit", "marker": "crown", "emote": 2,
         "reply": "Terenas, young. And the harvest wheat. They struck that the spring before. Everyone had them. Nobody spent the "
                  "last ones. It goes beside the chronicle, $n, so people remember what the world cost."},
        {"npc": "edmund_site", "kind": "option", "cond": ["I:q5"],
         "text": "For the case by the door: the herald's broadsheet announcing the Andorhal grain.",
         "action": "choice", "quest": "q5", "credit": "donate_credit", "marker": "broadsheet", "emote": 2,
         "reply": "\"Good news for the northern parishes.\" ...I read this aloud in the square myself, I think. I was proud of the "
                  "price. It goes beside the chronicle, $n. Next to Cinderford. They belong together."},
        # ---- The library, open ----
        {"npc": "edmund", "kind": "greet", "cond": ["R:endures.town"],
         "text": "Thirty-one letters returned to people who'd forgotten writing them. I wrote the number down. Of course I did."},
        {"npc": "edmund", "kind": "greet",
         "texts": ["Welcome to the Reclamation Library. Please don't eat in the stacks. I know you don't eat. Someone tried.",
                   "I wrote down everything that happened today. Then I read it back and remembered some of it. That's a good day.",
                   "Nora's at the far table again. She comes at opening and stays past dark. I've stopped dimming the lamps."]},
        {"npc": "edmund", "kind": "option", "cond": ["R:q5", "R:house.things", "!M:letters"],
         "text": "I found Elinor Harrow's letters to Cedric in my house. Would the library like copies?",
         "action": "say", "marker": "letters", "emote": 2,
         "reply": "Copies. Yes. Keep the originals, $n; they're yours, and his, and hers. Tobias will copy them by hand. He says a "
                  "letter copied by a machine is a letter that's been read by a stranger. Maela will want the date of every one."},
        {"npc": "maela", "kind": "greet",
         "texts": ["The archive, $n. Everything in it is correct. If you find something that isn't, tell me at once. Please. I'll "
                   "be awake.",
                   "Somebody asked me today what number they'd lived at. I told them. They said they'd thought it was seventeen. "
                   "It was twelve. They thanked me. People are thanking me now. I don't know what to do with it."]},
        # Maela's collection: it grows as Brill's other stories end.
        {"npc": "maela", "kind": "option", "cond": ["R:q5"], "text": "What's in the archive now?", "action": "say", "emote": 1,
         "reply": "The census of the eastern ward, the Agamand flour ledger, the customs records, the Cinderford chronicle, and a "
                  "drawer for everything people bring in that has no other drawer. That drawer is the largest. It is not a "
                  "failure of filing. It's a fact about the world."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "M:letters"], "text": "Have the Harrow letters been filed?",
         "action": "say", "emote": 1,
         "reply": "Copied, dated and filed under HARROW, CEDRIC AND ELINOR, CORRESPONDENCE. Tobias cried over the last one and "
                  "had to start the page again. I've noted it in the margin. He asked me not to. I've noted that too."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:grave.bell"], "text": "Have you a copy of the gravekeeper's ledger?",
         "action": "say", "emote": 1,
         "reply": "Weller let me copy it. Every burial in the plague year, and the four entries written twice. Mercy Hollin came "
                  "in and corrected her own date of death. She was right. It was the Thursday."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:customer.closing"], "text": "Anything from Ambrose Wicke's shop?",
         "action": "say", "emote": 1,
         "reply": "His order ledger, the green one, lent for copying with a great deal of instruction. The Balnir entry is in the "
                  "family histories now: Tobias Balnir and Marian Hale, to be wed at harvest. I've filed it under weddings. It's "
                  "where it belongs."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:scarlet.fate"], "text": "What do you keep on the Scarlet Crusade?",
         "action": "say", "emote": 1,
         "reply": "Everything the Deathguard would let me copy about the courier and the leak in Brill, dated and indexed. Their "
                  "collectors burn our books; we keep theirs. I find that the most satisfying shelf in the room."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:deathguard.duty"], "text": "Anything from the Deathguard?",
         "action": "say", "emote": 1,
         "reply": "Harlan's patrol logs, and a letter the Ashbys asked to have kept. I've put it with the family histories, not the "
                  "military records. Harlan said that was the right drawer. He's the first Deathguard who's ever agreed with me."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:gallows.nomasters"], "text": "Is there a record of what was under the hill?",
         "action": "say", "emote": 1,
         "reply": "Thirty-one names, and Croft's own roll beside them, so nobody can say later that it didn't happen. I keep that "
                  "drawer locked. Not to hide it. So that opening it is a decision."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:chapel.q5"], "text": "Have you a copy of the chapel's Book of Names?",
         "action": "say", "emote": 1,
         "reply": "Every page, including the three you carried home. Mirelle Vane checked my copy against hers and found a comma. "
                  "I have never been so pleased to be corrected."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:garden.q5"], "text": "Anything from the Stillgarden?",
         "action": "say", "emote": 1,
         "reply": "Edda Graves dictated the names of two hundred and twelve flowers. I checked them against an old herbal. She "
                  "missed one. She says she didn't miss it; she's leaving it out on purpose. I've noted both positions."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:surgeon.q5"], "text": "Do you keep the Surgeon's Hall's records?",
         "action": "say", "emote": 1,
         "reply": "Copies of the patient charter, and Agnes Morrow's case, with her permission, in Elspeth Rane's hand, which is "
                  "the worst hand I have ever had to read. I've made a fair copy. She says it's less accurate. It isn't."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:caravan.q5"], "text": "Does the caravan office send you anything?",
         "action": "say", "emote": 1,
         "reply": "Every manifest, in duplicate. Irena Sable is the only person in Brill whose records I haven't had to correct. "
                  "We don't like each other at all. It's wonderful."},
        {"npc": "maela", "kind": "option", "cond": ["R:q5", "R:brewery.q5"], "text": "Anything from the brewery?",
         "action": "say", "emote": 1,
         "reply": "Oren Blackbarrel's father's recipe book, lent for copying. Half the measurements are in thumbs. I've filed it "
                  "under history, not cookery, until somebody can tell me how large his father's thumbs were."},
        {"npc": "tobias", "kind": "greet",
         "texts": ["Ink, parchment, a satchel for your papers. And journals, if you'd like something to put in them.",
                   "(Tobias is writing very small in the margin of a ledger. He covers it with his hand when he sees you looking.)"]},
        {"npc": "tobias", "kind": "option", "cond": ["R:q5"], "text": "Let me see your writing supplies.", "action": "vendor"},
        {"npc": "tobias", "kind": "option", "cond": ["R:q5"],
         "text": "Could the library spare a few books for my house? And something to write in.",
         "action": "buy", "arg": 6000, "marker": "house_set", "emote": 2,
         "reply": "Histories, on long loan; Edmund has written down that you have them. And three journals I bound myself. Sixty "
                  "silver, for the binding thread. I'll carry them over tonight and put them by the bed, where you'll read them."},
        {"npc": "nora", "kind": "greet",
         "texts": ["(Nora Bell has a letter open on the table in front of her. She doesn't look up.)$B$BIt's from my sister. She "
                   "wrote it the week before. She says the plums are in. I'd forgotten we had plums.",
                   "I thought death had taken everything. Apparently, I hadn't checked the library.",
                   "Edmund says I can take the letter home. I don't want to. It's safer here. I'm safer here, reading it."]},
        {"npc": "patron_site", "kind": "greet",
         "texts": ["Maela says I lived on Chandlers' Lane. I don't remember Chandlers' Lane. I remember a blue door. She's looking "
                   "for the door.",
                   "I came to ask where my mother was buried. They didn't know yet. They wrote my name down. That's something."]},
        {"npc": "patron", "kind": "greet",
         "texts": ["Shh. ...Sorry. Habit. I was a schoolmistress.",
                   "I've been reading about Brill's old fair. I think I went. I think I won a pig.",
                   "Maela found my house. It's a field now. I'm going to go and stand in it."]},
        {"npc": "edmund_chapel", "kind": "greet",
         "text": "I come to read where it's quiet. The library is never quiet now. I wrote that down too, with a little star beside it."},
        {"npc": "edmund_caravan", "kind": "greet",
         "text": "Every caravan brings something written. Bills, letters, a song somebody wrote on the back of a manifest. Irena "
                 "lets me copy them before they're filed. I think she's pleased someone else reads them."},
        {"npc": "laborer", "kind": "greet",
         "texts": ["Books. We're building a house for books. In my day we built houses for people. Mind you, in my day we were "
                   "people.",
                   "The quiet one, Wren, brought us tea. None of us can drink it. We held it anyway. It was warm.",
                   "Don't stack the oak on the left, the archivist says the left is for archives. I don't know what that means."]},
        {"npc": "oswin", "kind": "greet",
         "text": "Oswin Thatcher. Jamie Nore keeps sending me to look at other people's carpentry. This one's sound. The bookbinder "
                 "checks every joint with a level older than both of us. I like him."},
    ],
}
