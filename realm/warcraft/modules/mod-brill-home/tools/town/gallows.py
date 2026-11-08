# SPDX-License-Identifier: GPL-3.0-or-later
"""Beneath the Gallows (Brill: A Place Among the Forsaken; tools/town/README.md): the one hidden line.

It opens only from a discovery in another line: the bricked-up wall with the Cult's mark behind the player's
cellar (the house's "Beneath the Floorboards") or Gideon Hale's tale of the passage he walled up beneath the
cemetery (the end of The Gravekeeper's Ledger, tools/town/grave.py). Until then its giver, Deathstalker Isolde
Ashcroft by Brill's mausoleum, and the marks she sends the player to are in a phase ("unlocked") the player isn't in.

In the plague year Aldric Croft, Brill's generous benefactor and a necromancer of the Cult of the Damned, offered the
town a refuge in the old tunnels between Brill and the Agamand family vaults, walled its ways in, and raised those
who sheltered there. He's in the Agamand Family Crypt still (north of Brill, reached on foot), waiting for a Lich King
who stopped answering him years ago. Five quests: the Cult's marks beneath Brill; the refugees' journals in the crypt;
the bound guardians; Croft himself, through his door and his unsent letters; and Croft killed, his roll of the raised
taken to the gravekeeper. The crypt (outside Brill) is everyone's: its guardians and Croft are there for all.

Its result: the gravekeeper's greetings (grave.py), Gideon's, and a relic for the house: Croft's black candle, snuffed,
in the house of a player who owns it (the phase "relic").
"""

LINE = {
    "title": "Beneath the Gallows",
    "quests": [
        {
            "id": "sealed", "title": "The Sealed Passage", "giver": "maren", "ender": "maren", "prev": None,
            "min_level": 10,
            "log": "Find the Cult's marks beneath Brill: in the cellar under the inn, on the mausoleum's foundation stone and "
                   "where the ground has sunk at the cemetery's east edge.",
            "offer": (
                "Don't turn round. Admire the mausoleum. It's very fine.$B$B"
                "Either you've seen a mark on a bricked-up wall you shouldn't have, or a dead mason has been talking "
                "where a gravekeeper could hear. Either way you've found the edge of something I've been following "
                "since Stratholme, and I'd rather have you with me than blundering about alone.$B$B"
                "Before the plague there were tunnels under this town: old cellars and a smugglers' way that ran north "
                "under the hills. In the plague year someone walled every way into them and marked each wall. A crowned "
                "eye. The Cult of the Damned used it on the houses they meant to come back for.$B$B"
                "Find me the marks. There's one in the cellar under the inn, where the Deathguard keep their prisoners; "
                "one on this mausoleum's foundation stone; and one where the earth has fallen in past the east wall. "
                "Tell me which way they point."),
            "progress": "Three marks. Don't touch them more than you must.",
            "done": (
                "North. All three of them, north, toward Agamand Mills.$B$B"
                "The Agamands had vaults under their family crypt, deep and dry. If the tunnels ran there, the people "
                "of Brill who went below to hide from the plague went there too. And the man who walled them in knew "
                "it.$B$B"
                "His name was Aldric Croft. Brill remembers him fondly. He paid for the well, the bell rope, the "
                "orphans' bread. He was also a necromancer of the Cult, and he was never found."),
            "objectives": [("credit", "marks_credit", 3, "The Cult's marks found")],
            "return": "Return to Deathstalker Isolde Ashcroft by the mausoleum in Brill's cemetery.",
            "money": 3000, "xp": 4,
        },
        {
            "id": "echoes", "title": "Echoes of Lordaeron", "giver": "maren", "ender": "maren_crypt", "prev": "sealed",
            "min_level": 10,
            "log": "Recover three journals left by Brill's plague refugees in the Agamand Family Crypt, north of Brill, then "
                   "find Deathstalker Isolde Ashcroft outside the crypt.",
            "offer": (
                "The Agamand Family Crypt is north of here, past the mills. The Agamands themselves don't rest easy, "
                "and they won't thank you for visiting. Go anyway.$B$B"
                "If Croft's refuge opened into their vaults, the people who sheltered there will have left something. "
                "People write, when they're frightened and waiting. They write to whoever might find it.$B$B"
                "Bring me what they wrote. I'll meet you outside the crypt. I have a few things to arrange first: there "
                "are people in the Undercity who'd rather this stayed buried, and I'd like them busy elsewhere."),
            "progress": "Did they write? They always write.",
            "done": (
                "(Isolde reads by the last of the light, slowly, the way you'd read a list of the dead. Which it is.)$B$B"
                "'Master Croft says the air below is clean.' 'Master Croft brought bread again.' And then, near the end, "
                "in the boy's hand: 'Mother says the doors are bricked. Master Croft says it is for our own good. Mother "
                "has stopped answering.'$B$B"
                "He didn't hide them from the plague, $n. He kept them for it."),
            "objectives": [("credit", "journals_credit", 3, "Refugees' journals recovered")],
            "return": "Find Deathstalker Isolde Ashcroft outside the Agamand Family Crypt.",
            "money": 3500, "xp": 4, "items": [(858, 2)],
        },
        {
            "id": "unquiet", "title": "The Unquiet Dead", "giver": "maren_crypt", "ender": "maren_crypt", "prev": "echoes",
            "min_level": 10,
            "log": "Destroy 6 Bound Sentinels in the Agamand Family Crypt.",
            "offer": (
                "You'll have seen them down there: the ones in rags, standing their posts in the dark, who don't moan "
                "the way the Agamands do. They don't make any sound at all.$B$B"
                "Those are Croft's refugees. Hester Lyle and her children, the baker, the boy who wrote. He raised them "
                "and bound them to guard his door, and they've stood there for years without a single thought of their "
                "own. Not like us. Nothing woke in them. Nothing is going to.$B$B"
                "I've been free six years and I still don't know how to feel about doing this. Do it anyway. Put them "
                "down, $n, gently if you can. It's the only kindness left to give them."),
            "progress": "It doesn't get easier. It shouldn't.",
            "done": (
                "Thank you. I mean that, though I won't say it again.$B$B"
                "With his sentinels gone the crypt is quieter. Quiet enough that I could hear something further down, "
                "while you worked. A man's voice, reading aloud. Very patient. Very pleased with itself."),
            "objectives": [("kill", "sentinel", 6, "")],
            "return": "Return to Deathstalker Isolde Ashcroft outside the Agamand Family Crypt.",
            "money": 4000, "xp": 5,
        },
        {
            "id": "master", "title": "A Master Without a Kingdom", "giver": "maren_crypt", "ender": "maren_crypt",
            "prev": "unquiet", "min_level": 10,
            "log": "Find the warded door deep in the Agamand Family Crypt and hear out whoever is behind it, and read the "
                   "letters left beside it.",
            "offer": (
                "He's still down there. Croft. Twenty years and a war later.$B$B"
                "I could take you straight to him and we could be done. But I want to know what we're dealing with: "
                "whether he's mad, or waiting for something, or someone. A Cult necromancer who's sat in the dark "
                "this long has either forgotten the world or is very sure it will come back to him.$B$B"
                "Go to the bottom of the crypt. There'll be a door he's warded. Talk to it. Listen. And look about you: "
                "a man like that keeps records. He can't help himself."),
            "progress": "Well? Is he mad?",
            "done": (
                "Letters to the Lich King. Years of them, and not one answer.$B$B"
                "No, he isn't mad. He's worse. He's loyal. He thinks the Master's silence is a test, and that our "
                "freedom is a fever that will pass. He'd put every Forsaken in Brill back in the ground and call it "
                "tidying.$B$B"
                "We are no one's servants now, $n. Not his, not his master's. I'd like him to understand that before "
                "the end."),
            "objectives": [("credit", "ward_credit", 1, "The warded door listened at"),
                           ("credit", "letters_credit", 1, "Croft's letters read")],
            "return": "Return to Deathstalker Isolde Ashcroft outside the Agamand Family Crypt.",
            "money": 4000, "xp": 5, "items": [(2455, 2)],
        },
        {
            "id": "nomasters", "title": "No Masters but Ourselves", "giver": "maren_crypt", "ender": "grave.keeper",
            "prev": "master", "min_level": 10,
            "log": "Slay Aldric Croft in the depths of the Agamand Family Crypt and take his Roll of the Raised to "
                   "Gravekeeper Mortimer Weller in Brill.",
            "offer": (
                "His ward is weaker for the sentinels being gone. It'll break if you put your shoulder to it, and then "
                "it's you and him.$B$B"
                "He's a necromancer of the old Cult: shadow, curses, the slow drain. He's had twenty years to prepare "
                "and no one to practise on, so he'll be sharp in his spells and soft everywhere else. Close quickly.$B$B"
                "When he's down, find his register. Every name he raised, he'll have written down: it's how they "
                "thought, the Cult, like stewards counting sheep. Those names belong to Brill. Take them to the "
                "gravekeeper. I'll stay and see the crypt sealed properly this time. My way."),
            "progress": "(Mortimer looks at your hands, and then at your face.) You've been to the bottom of it, haven't you?",
            "done": (
                "A Roll of the Raised. In a fine hand. He even kept the dates.$B$B"
                "Thirty-one names. Lyle, Hester, and four children. Pike, the baker. Merriweather. ...I wrote some of "
                "these into my ledger as 'remains not recovered.' I suppose I can finish the entries now.$B$B"
                "(He sets the roll beside his ledger, carefully, as if it might wake.)$B$B"
                "Isolde sent word. She's had something carried to your house, if you keep one here: Croft's black candle, "
                "snuffed. She says every home ought to have one thing in it to remind you who isn't master there "
                "anymore. Thank you, $n. For Brill."),
            "objectives": [("kill", "croft", 1, ""),
                           ("credit", "records_credit", 1, "Croft's Roll of the Raised")],
            "return": "Bring Croft's Roll of the Raised to Gravekeeper Mortimer Weller in Brill's cemetery.",
            "money": 6000, "xp": 6, "items": [(929, 2), (14123, 1)],
        },
    ],
    "npcs": [
        # By Brill's mausoleum, for those who've found either clue.
        {"id": "maren", "name": "Isolde Ashcroft", "subname": "Deathstalker", "display": 1679, "level": 30,
         "phase": "unlocked", "spawns": [[0, 2378.0, 335.0, 38.51, 0.1]]},
        # Outside the Agamand Family Crypt (everyone sees her; she has nothing to say to most).
        {"id": "maren_crypt", "name": "Isolde Ashcroft", "subname": "Deathstalker", "display": 1679, "level": 30,
         "unit_flags": 512, "spawns": [[0, 2965.0, 645.0, 100.0, 0.27]]},
        # In the crypt: Croft's bound sentinels on its upper halls, and Croft at the bottom hall's east end.
        {"id": "sentinel", "name": "Bound Sentinel", "display": [200, 535], "hostile": True, "faction": 14,
         "level": (10, 11), "health": 1.0, "damage": 1.0, "unit_class": 1, "type": 6, "gold": 0,
         "spells": [(11976, (3000, 5000), (8000, 11000))],
         "spawns": [[0, 3040.0, 671.5, 81.2, 0.0], [0, 3047.5, 671.0, 81.1, 3.1],
                    [0, 3030.0, 655.0, 75.4, 0.0], [0, 3040.0, 655.0, 75.4, 3.1], [0, 3052.0, 655.5, 75.4, 3.1],
                    [0, 3028.0, 688.5, 66.4, 0.0], [0, 3040.0, 689.0, 66.6, 3.1]]},
        {"id": "croft", "name": "Aldric Croft", "subname": "Cult of the Damned", "display": 10427, "hostile": True,
         "faction": 14, "level": 13, "health": 3.0, "damage": 1.3, "unit_class": 8, "type": 6, "gold": 200,
         "respawn": 300,
         "spells": [(20791, (1000, 2000), (4000, 6000)), (980, (3000, 5000), (16000, 20000)),
                    (689, (9000, 12000), (20000, 25000))],
         "spawns": [[0, 3060.5, 694.0, 66.5, 3.6]]},
    ],
    "credits": [
        {"id": "marks_credit", "name": "The Cult's marks found"},
        {"id": "journals_credit", "name": "Refugees' journals recovered"},
        {"id": "ward_credit", "name": "The warded door listened at"},
        {"id": "letters_credit", "name": "Croft's letters read"},
        {"id": "records_credit", "name": "Croft's Roll of the Raised"},
    ],
    "objects": [
        # The Sealed Passage: the marks, in Brill (only for those in the phase "unlocked").
        {"id": "mark_cellar", "name": "Crowned Eye Sigil", "quest_only": True, "display": 465, "scale": 0.6, "phase": "unlocked",
         "spawns": [[0, 2293.5, 240.0, 27.3, 1.6]],
         "use": [{"cond": ["I:sealed"], "quest": "sealed", "credit": "marks_credit"}]},
        {"id": "mark_stone", "name": "Mausoleum Foundation Stone", "quest_only": True, "display": 302, "scale": 0.8, "phase": "unlocked",
         "spawns": [[0, 2378.0, 326.0, 38.73, 1.6]],
         "use": [{"cond": ["I:sealed"], "quest": "sealed", "credit": "marks_credit"}]},
        {"id": "mark_sunken", "name": "Sunken Earth", "quest_only": True, "display": 20, "scale": 0.8, "phase": "unlocked",
         "spawns": [[0, 2405.0, 318.0, 38.26, 1.6]],
         "use": [{"cond": ["I:sealed"], "quest": "sealed", "credit": "marks_credit"}]},
        # Echoes of Lordaeron: the refugees' journals, in the crypt.
        {"id": "journal_lyle", "name": "Water-Stained Journal", "quest_only": True, "display": 105, "spawns": [[0, 3045.0, 674.0, 81.2, 2.0]],
         "use": [{"cond": ["I:echoes"], "quest": "echoes", "credit": "journals_credit",
                  "text": "(HESTER LYLE, HER BOOK. 'Third day below. Master Croft says the air here is clean and the plague "
                          "cannot follow. The children are frightened of the Agamand vaults but I tell them the dead are "
                          "only sleeping. God forgive me, I believed it.')"}]},
        {"id": "journal_pike", "name": "Baker's Daybook", "quest_only": True, "display": 447, "spawns": [[0, 3035.0, 657.0, 75.4, 4.0]],
         "use": [{"cond": ["I:echoes"], "quest": "echoes", "credit": "journals_credit",
                  "text": "(Accounts in a baker's hand, flour and salt, and then: 'Croft brought bread again. Good white "
                          "bread. Where does he get the flour, with the mills shut? Lyle's youngest has the cough. Croft says "
                          "it is only the damp. Croft says a great deal.')"}]},
        {"id": "journal_boy", "name": "Child's Copybook", "quest_only": True, "display": 184, "scale": 0.8,
         "spawns": [[0, 3021.5, 691.0, 66.5, 5.0]],
         "use": [{"cond": ["I:echoes"], "quest": "echoes", "credit": "journals_credit",
                  "text": "(Letters practised over and over in a careful round hand, and then, near the end: 'Mother says the "
                          "doors are bricked. Master Croft says it is for our own good. Mother has stopped answering. I am "
                          "going to be brave like Da.')"}]},
        # A Master Without a Kingdom: Croft's door and his letters.
        {"id": "ward", "name": "Bone-Warded Door", "quest_only": True, "display": 6898, "spawns": [[0, 3050.0, 690.0, 66.6, 0.0]],
         "use": [{"cond": ["I:master"], "quest": "master", "credit": "ward_credit"}]},
        {"id": "croft_letters", "name": "Unsent Letters", "quest_only": True, "display": 164, "spawns": [[0, 3056.0, 693.0, 66.5, 3.0]],
         "use": [{"cond": ["I:master"], "quest": "master", "credit": "letters_credit",
                  "text": "(A stack of letters, each addressed TO MY MASTER, IN NORTHREND. 'Brill is tended. The flock is "
                          "counted.' 'I await your instruction.' 'The Banshee's rabble walk my town as if it were theirs.' "
                          "'Master, I have been patient.' The most recent is only one line, written many times: 'Answer me.')"}]},
        # No Masters but Ourselves: Croft's register, by his chair.
        {"id": "roll", "name": "Roll of the Raised", "quest_only": True, "display": 163, "spawns": [[0, 3062.5, 697.0, 66.5, 3.6]],
         "use": [{"cond": ["I:nomasters"], "quest": "nomasters", "credit": "records_credit",
                  "text": "(Thirty-one names in a fine, careful hand, each with the date of its raising and its use. SENTINEL. SENTINEL. LABOURER. SENTINEL.)"}]},
        # The relic, in the house of a player who owns it, once Croft is dead.
        {"id": "relic", "name": "Croft's Black Candle, Snuffed", "display": 4152, "phase": "relic",
         "spawns": [["house", 2.3, 4.97, 2.12, -90]]},
    ],
    "gossip": [
        # Isolde by Brill's mausoleum.
        {"npc": "maren", "kind": "greet", "cond": ["R:nomasters"],
         "text": "The crypt's walled again, the right way this time: no marks, no gifts, no Croft. I'll be moving on "
                 "soon. Before I go: well done. I don't say it often."},
        {"npc": "maren", "kind": "greet", "cond": ["T:echoes"],
         "text": "Why are you looking for me here? I said I'd meet you at the crypt. North, past the mills."},
        {"npc": "maren", "kind": "greet",
         "text": "(A woman in a dark hood studies the mausoleum's stonework with great interest. She doesn't look at "
                 "you.)$B$BKeep walking as if we're strangers. We are, for now."},
        # Isolde at the crypt: nothing for those who aren't on the line.
        {"npc": "maren_crypt", "kind": "greet", "cond": ["R:nomasters"],
         "text": "Sealed. My way. Go home, $n. Light a candle. Not his."},
        {"npc": "maren_crypt", "kind": "greet", "cond": ["T:echoes"],
         "text": "Mind the Agamands on the stair. They're only angry; they don't know any better."},
        {"npc": "maren_crypt", "kind": "greet",
         "text": "This crypt belongs to the Agamands. I'm only resting. You'll want to keep walking."},
        # Gideon Hale in Brill, if the grave line brought him there.
        {"npc": "grave.tobias_town", "kind": "option", "cond": ["T:sealed", "!R:nomasters"],
         "text": "Isolde Ashcroft found your mark on the mausoleum stone.", "action": "say",
         "reply": "T.C. Aye. I was proud of that wall, God help me. Croft paid in good silver and said the people below "
                  "would thank me. Go carefully down there, $n. I laid those bricks to keep something in."},
    ],
    "phases": {
        # Its giver and the marks in Brill, for those who've found either clue: the cellar wall behind the house, or
        # Gideon's tale at the end of The Gravekeeper's Ledger.
        "unlocked": [["R:house.floorboards"], ["R:grave.bell"]],
        # Croft's black candle in the player's house.
        "relic": [["R:nomasters", "OWN"]],
    },
}
