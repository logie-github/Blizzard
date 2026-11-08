# SPDX-License-Identifier: GPL-3.0-or-later
"""The Gravekeeper's Ledger (Brill: A Place Among the Forsaken; tools/town/README.md).

Mortimer Weller, Brill's new gravekeeper (the parish clerk in life, who wrote the plague year's burials), finds
graves emptied with no sign of the Scourge. The names written twice in his ledger are the dead the Deathguard
put down and buried a second time; some of them have woken with their own minds, and the first to wake has been
digging the others out. Five quests: the ledger and five graves; the evidence in three opened graves; the trail
to an abandoned mausoleum east of town and the four hiding there (Mercy Hollin, Gideon Hale, Edith Fairweather,
Walter Shaw); their things from their old homes, and a choice: walk into Brill by daylight under their own names,
or come in quietly with the gravekeeper's word; the Magistrate's rolls and the last bell.

Its result: the four live in Brill (the phase "newcomers", their greetings by the choice), the gravekeeper's
greetings change with this line and Beneath the Gallows (tools/town/gallows.py), and Gideon's tale of the passage
he bricked up beneath the cemetery opens that line (its phase "unlocked" asks R:grave.bell).
"""

KEEPER_X, KEEPER_Y = 2362.0, 342.0

LINE = {
    "title": "The Gravekeeper's Ledger",
    "quests": [
        {
            "id": "names", "title": "Names Among the Stones", "giver": "keeper", "ender": "keeper", "prev": None,
            "log": "Help Mortimer Weller sort Brill's burial ledgers, then inspect five neglected graves in the cemetery.",
            "offer": (
                "You there. You've the look of someone who reads. Forgive me: I don't get many visitors who still "
                "do.$B$B"
                "I was the parish clerk here, before. I wrote every burial of the plague year in this ledger, until my "
                "hand shook too hard to hold the pen, and then somebody wrote mine. The Dark Lady's people gave me the "
                "cemetery back when I rose. A clerk to the last, it seems.$B$B"
                "Graves are coming up empty, $n. Not torn open, the way the Scourge leave them. Just... empty. And when I "
                "went to the ledgers to see whose, I found names written twice. My own hand, and then another's.$B$B"
                "Help me put the books in order, and then look at five of the oldest graves along the wall. Tell me what "
                "the stones say. I'd go myself, but I'd rather not be alone with this until I know what it is."),
            "progress": "Have you seen to the ledgers? And the stones along the wall?",
            "done": (
                "Hollin, Hale, Fairweather, Shaw. Every one of them twice.$B$B"
                "The first entry's mine: buried in the plague year. The second is in a Deathguard's square hand, two "
                "years on. 'Remains found walking. Put down. Returned to plot.'$B$B"
                "So they were Scourge, once, after they died. The Deathguard cut them down and gave them back to the "
                "earth. I'd have called that the end of the matter. It seems the earth didn't agree."),
            "objectives": [("credit", "ledger_credit", 1, "Burial ledgers sorted"),
                           ("credit", "graves_credit", 5, "Neglected graves inspected")],
            "return": "Return to Gravekeeper Mortimer Weller in Brill's cemetery.",
            "money": 2000, "xp": 3, "items": [(118, 2)],
        },
        {
            "id": "fresh", "title": "Fresh Earth", "giver": "keeper", "ender": "keeper", "prev": "names",
            "log": "Search three recently disturbed graves in Brill's cemetery for evidence of who has been taking the dead.",
            "offer": (
                "The Deathguard tell me it's the Rot Hide gnolls. They dig for bones the way dogs do, and they've done it "
                "before. Executor Zygand says to put a guard on the gate and stop fretting.$B$B"
                "But I've seen what gnolls leave behind, $n: half the coffin in splinters and the other half chewed. "
                "These graves were opened neatly. Somebody filled the holes back in after. Gnolls don't tidy.$B$B"
                "Three of the double-named graves were disturbed within the week, along the north side, by the old yew. "
                "Look them over properly. Whatever was left behind, I want to know about it before the Deathguard decide "
                "what it means for us."),
            "progress": "Anything? Even a footprint would be more than the Deathguard have found.",
            "done": (
                "My own spade. I wondered where that went.$B$B"
                "And this lid: scored on the inside, as if someone woke and clawed at it. But the nails were drawn from "
                "the outside, one by one, by somebody who knew what they were doing.$B$B"
                "No one is stealing the dead, $n. Someone is letting them out."),
            "objectives": [("credit", "evidence_credit", 3, "Disturbed graves searched")],
            "return": "Return to Gravekeeper Mortimer Weller in Brill's cemetery.",
            "money": 2500, "xp": 3, "items": [(858, 2)],
        },
        {
            "id": "forgotten", "title": "Those Who Were Forgotten", "giver": "keeper", "ender": "mercy", "prev": "fresh",
            "log": "Follow the trail of grave dirt east of Brill's cemetery to wherever it leads, and speak with whoever you find.",
            "offer": (
                "There's a furrow in the grass past the east wall, where something heavy was dragged, or someone who "
                "couldn't yet walk was helped along. It goes up toward the wooded hill, where the old Lyle family "
                "mausoleum stands. The Lyles all died in the first month of the plague. No one has opened that door "
                "since.$B$B"
                "I could tell the Deathguard. They'd go up there with torches, and whoever is inside would be put down a "
                "second time, or a third.$B$B"
                "I'd rather you went. You don't wear a tabard, and you've the patience to talk before you swing. If they "
                "are what I think they are, they'll be more afraid of you than you need be of them. Mostly."),
            "progress": "",
            "done": (
                "(The woman lowers the spade, but doesn't let go of it.)$B$B"
                "Mortimer sent you? Mortimer Weller, the clerk? He wrote my name in that book of his. Twice, I expect.$B$B"
                "I'm Mercy Hollin. I was the midwife here, when Brill had children. Behind me are Gideon, Edith and "
                "Walter. We're not Scourge, whatever you've been told. We were, once. We remember it. That's why we're "
                "hiding."),
            "objectives": [("credit", "tracks_credit", 3, "Trail of grave dirt followed"),
                           ("credit", "met_credit", 1, "Whoever hides in the mausoleum spoken with")],
            "return": "Speak with Mercy Hollin at the Lyle mausoleum east of Brill.",
            "money": 2500, "xp": 4,
        },
        {
            "id": "aname", "title": "A Name of One's Own", "giver": "mercy", "ender": "mercy", "prev": "forgotten",
            "log": "Recover Gideon's tools from the old smithy west of Brill, Edith's basket from her cottage south of town and "
                   "Walter's letters from the gnolls' farmstead north-east of it, and help Mercy decide how they'll face Brill.",
            "offer": (
                "I woke in the dark with earth in my mouth, and I knew my own name. That was the strange part. For years "
                "I'd only known his voice in my head, and then it was gone, and there I was. Mercy. Just Mercy.$B$B"
                "I dug myself out. Then I heard knocking from the next grave, so I took Mortimer's spade from his shed and "
                "dug again. Four times, so far. I'll keep listening.$B$B"
                "The others want things back, before they'll believe they're people. Gideon wants his tools from the old "
                "smithy by the west road. Edith wants her sewing basket from her cottage south of town, the one by the "
                "duskbat woods. Walter's letters are at his farmstead north-east of here, where the Rot Hide gnolls have "
                "their camp now.$B$B"
                "And when you come back, help me talk sense into them about Brill. We can't live in a tomb forever. "
                "Though Walter would try."),
            "progress": "Walter keeps asking if you've found his letters. He pretends he isn't asking.",
            "done": (
                "Look at Gideon, turning that chisel over like he'd never seen one. And Edith hasn't let go of her basket "
                "since you put it in her hands.$B$B"
                "Walter read his letters twice and then went outside to stand in the rain. Leave him be. He'll come "
                "back.$B$B"
                "You've given them something I couldn't, $n: proof they were somebody before, and not only something."),
            "objectives": [("credit", "belongings_credit", 3, "Belongings recovered"),
                           ("credit", "decided_credit", 1, "Brill's question settled")],
            "return": "Return to Mercy Hollin at the Lyle mausoleum east of Brill.",
            "money": 3000, "xp": 4, "items": [(858, 2)],
        },
        {
            "id": "bell", "title": "The Last Bell", "giver": "mercy", "ender": "keeper", "prev": "aname",
            "log": "Ask Magistrate Sevren in Brill's town hall to enter the four names on Brill's rolls, then ring the "
                   "cemetery bell with Gravekeeper Mortimer Weller.",
            "offer": (
                "There's a custom in Brill. There was, anyway. When someone was laid in the ground, the clerk rang the "
                "bell over the lychgate, once, so the whole parish knew a life was finished. In the plague year it rang "
                "so often they stopped ringing it at all.$B$B"
                "Mortimer told me, through you, that he'd like to ring it once more for the four of us. The other way "
                "round. Not a life finished; a death.$B$B"
                "But a bell's only a bell. The Magistrate keeps the rolls of who lives in Brill, and who the Deathguard "
                "are to leave alone. Our names need to be on them, $n, or we're only corpses with opinions. Go to Sevren "
                "in the town hall, and then to Mortimer. We'll be watching from the wall."),
            "progress": "Have the names been entered? Has it rung?",
            "done": (
                "Hollin. Hale. Fairweather. Shaw. Written a third time, and in the right column at last.$B$B"
                "(Gideon Hale clears his throat behind you.)$B$B"
                "\"Gravekeeper. There's something you should know, since we're being honest. In the plague year a "
                "gentleman named Croft paid me to brick up the old way down beneath this cemetery, and two others like it "
                "about the town. To keep the sickness out of the refuge, he said. The people sheltering below went quiet "
                "soon after. I've wondered what I sealed in, ever since I could wonder again.\"$B$B"
                "(Mortimer looks at you for a long moment.)$B$B"
                "Write that down somewhere, $n. Not in my ledger. I've enough to keep in it."),
            "objectives": [("credit", "rolls_credit", 1, "Names entered on Brill's rolls"),
                           ("credit", "rung_credit", 1, "The last bell rung")],
            "return": "Return to Gravekeeper Mortimer Weller in Brill's cemetery.",
            "money": 4000, "xp": 5, "items": [(1930, 1)],
        },
    ],
    "markers": ["openly", "quietly"],
    "npcs": [
        {"id": "keeper", "name": "Mortimer Weller", "subname": "Gravekeeper", "display": 2650, "level": 22,
         "spawns": [[0, KEEPER_X, KEEPER_Y, 38.03, 3.0]]},
        # Hiding at the Lyle mausoleum on the hill east of town (everyone's: it's outside Brill).
        {"id": "mercy", "name": "Mercy Hollin", "display": 2660, "level": 12, "unit_flags": 512,
         "spawns": [[0, 2486.0, 259.0, 47.28, 2.8]]},
        {"id": "tobias", "name": "Gideon Hale", "display": 2649, "level": 12, "unit_flags": 512, "flags": ["gossip"],
         "spawns": [[0, 2489.0, 265.0, 46.44, 3.4]]},
        {"id": "agnes", "name": "Edith Fairweather", "display": 2664, "level": 10, "unit_flags": 512, "flags": ["gossip"],
         "spawns": [[0, 2484.0, 253.0, 45.92, 2.4]]},
        {"id": "walter", "name": "Walter Shaw", "display": 2654, "level": 13, "unit_flags": 512, "flags": ["gossip"],
         "spawns": [[0, 2491.0, 251.0, 45.38, 2.2]]},
        # In Brill once the last bell has rung (the phase "newcomers").
        {"id": "mercy_town", "name": "Mercy Hollin", "display": 2660, "level": 12, "flags": ["gossip"], "phase": "newcomers",
         "spawns": [[0, 2352.0, 336.0, 38.08, 0.4]]},
        {"id": "tobias_town", "name": "Gideon Hale", "subname": "Stonemason", "display": 2649, "level": 12, "flags": ["gossip"],
         "phase": "newcomers", "spawns": [[0, 2290.0, 318.0, 35.31, 1.6]]},
        {"id": "agnes_town", "name": "Edith Fairweather", "subname": "Weaver", "display": 2664, "level": 10, "flags": ["gossip"],
         "phase": "newcomers", "spawns": [[0, 2262.0, 279.0, 34.79, 0.8]]},
        {"id": "walter_town", "name": "Walter Shaw", "display": 2654, "level": 13, "flags": ["gossip"], "phase": "newcomers",
         "spawns": [[0, 2296.0, 393.0, 34.07, 0.2]]},
    ],
    "credits": [
        {"id": "ledger_credit", "name": "Burial ledgers sorted"},
        {"id": "graves_credit", "name": "Neglected graves inspected"},
        {"id": "evidence_credit", "name": "Disturbed graves searched"},
        {"id": "tracks_credit", "name": "Trail of grave dirt followed"},
        {"id": "met_credit", "name": "Whoever hides in the mausoleum spoken with"},
        {"id": "belongings_credit", "name": "Belongings recovered"},
        {"id": "decided_credit", "name": "Brill's question settled"},
        {"id": "rolls_credit", "name": "Names entered on Brill's rolls"},
        {"id": "rung_credit", "name": "The last bell rung"},
    ],
    "objects": [
        # Names Among the Stones: five neglected graves along the cemetery's walls.
        {"id": "stone_hollin", "name": "Neglected Grave", "display": 193, "spawns": [[0, 2352.0, 322.0, 36.42, 1.2]],
         "use": [{"cond": ["I:names"], "quest": "names", "credit": "graves_credit"}]},
        {"id": "stone_crane", "name": "Neglected Grave", "display": 499, "spawns": [[0, 2348.0, 360.0, 36.72, 0.4]],
         "use": [{"cond": ["I:names"], "quest": "names", "credit": "graves_credit"}]},
        {"id": "stone_fairweather", "name": "Neglected Grave", "display": 2452, "spawns": [[0, 2366.0, 368.0, 37.79, 4.9]],
         "use": [{"cond": ["I:names"], "quest": "names", "credit": "graves_credit"}]},
        {"id": "stone_shaw", "name": "Neglected Grave", "display": 19, "spawns": [[0, 2396.0, 362.0, 37.01, 3.6]],
         "use": [{"cond": ["I:names"], "quest": "names", "credit": "graves_credit"}]},
        {"id": "stone_lyle", "name": "Neglected Grave", "display": 399, "spawns": [[0, 2400.0, 325.0, 38.09, 3.1]],
         "use": [{"cond": ["I:names"], "quest": "names", "credit": "graves_credit"}]},
        # Fresh Earth: three graves opened and filled in again.
        {"id": "opened_spade", "name": "Disturbed Grave", "quest_only": True, "display": 498, "spawns": [[0, 2372.0, 374.0, 37.34, 1.0]],
         "use": [{"cond": ["I:fresh"], "quest": "fresh", "credit": "evidence_credit"}]},
        {"id": "opened_lid", "name": "Disturbed Grave", "quest_only": True, "display": 49, "spawns": [[0, 2356.0, 376.0, 35.91, 2.2]],
         "use": [{"cond": ["I:fresh"], "quest": "fresh", "credit": "evidence_credit"}]},
        {"id": "opened_shroud", "name": "Disturbed Grave", "quest_only": True, "display": 498, "spawns": [[0, 2340.0, 368.0, 34.65, 5.5]],
         "use": [{"cond": ["I:fresh"], "quest": "fresh", "credit": "evidence_credit"}]},
        # Those Who Were Forgotten: the trail east to the Lyle mausoleum on the hill.
        {"id": "trail", "name": "Trail of Grave Dirt", "quest_only": True, "display": 49, "scale": 0.5,
         "spawns": [[0, 2425.0, 300.0, 36.17, 5.8], [0, 2458.0, 280.0, 31.44, 5.9], [0, 2472.0, 268.0, 45.38, 5.9]],
         "use": [{"cond": ["I:forgotten"], "quest": "forgotten", "credit": "tracks_credit"}]},
        {"id": "mausoleum", "name": "Lyle Family Mausoleum", "display": 1187, "spawns": [[0, 2497.0, 257.0, 46.09, 2.8]]},
        # A Name of One's Own: their things, at their old homes.
        {"id": "toolroll", "name": "Mason's Tool Roll", "quest_only": True, "display": 5511, "scale": 0.6, "spawns": [[0, 2041.5, 153.0, 34.3, 1.4]],
         "use": [{"cond": ["I:aname"], "quest": "aname", "credit": "belongings_credit"}]},
        {"id": "basket", "name": "Sewing Basket", "quest_only": True, "display": 7494, "spawns": [[0, 2483.5, 24.5, 26.9, 0.6]],
         "use": [{"cond": ["I:aname"], "quest": "aname", "credit": "belongings_credit"}]},
        {"id": "letters", "name": "Tin Letter Box", "quest_only": True, "display": 1, "scale": 0.5, "spawns": [[0, 2903.0, 387.0, 30.02, 4.0]],
         "use": [{"cond": ["I:aname"], "quest": "aname", "credit": "belongings_credit",
                  "text": "(Letters tied with string, each beginning 'Dear Da' in a careful round hand. The last is dated the week the plague came to Brill.)"}]},
    ],
    "gossip": [
        # The gravekeeper: his greeting by how far this line and Beneath the Gallows have gone (the first that holds).
        {"npc": "keeper", "kind": "greet", "cond": ["R:gallows.nomasters"],
         "text": "Thirty-one names, $n. Thirty-one people Croft kept in the dark and wrote down like stock. They're in my "
                 "ledger now, in the right column. I ring the bell at dusk for one of them each night. It'll take a month. "
                 "I find I don't mind the work."},
        {"npc": "keeper", "kind": "greet", "cond": ["C:gallows.nomasters"],
         "text": "Isolde's message said you'd bring me something from under the hill. I've cleared a page for it. I hope "
                 "a page is enough."},
        {"npc": "keeper", "kind": "greet", "cond": ["T:gallows.sealed"],
         "text": "You've been below. I can smell it on you: old candle-fat and older stone. Whatever's down there, "
                 "$n, mind you come back up the same as you went. Some don't."},
        {"npc": "keeper", "kind": "greet", "cond": ["R:bell", "M:openly"],
         "text": "Mercy walked through the market at noon yesterday and bought a loaf she can't eat, just to be seen "
                 "paying for it. Half of Brill stared. The other half asked if she still delivers. She does, it seems: "
                 "she's been at the Apothecary's door asking after foals and calves.$B$BThe ledger balances, $n. First "
                 "time in years."},
        {"npc": "keeper", "kind": "greet", "cond": ["R:bell", "M:quietly"],
         "text": "They came in by night, as we agreed, and the Deathguard had their orders. No torches. A week on, "
                 "and the baker's boy still doesn't know Edith was ever under my lawn. That's how she wants it.$B$BThe "
                 "ledger balances, $n. First time in years."},
        {"npc": "keeper", "kind": "greet", "cond": ["R:house.floorboards", "!R:bell"],
         "text": "A carpenter came by asking whether the parish books mention a mark like a crowned eye. They don't. "
                 "But a Deathstalker asked me the very same thing a month ago, and she's been standing by the mausoleum "
                 "ever since, pretending to admire it."},
        {"npc": "keeper", "kind": "greet", "cond": ["A:bell"],
         "text": "The bell's rope is new. I bought it myself. Have you been to the Magistrate?"},
        {"npc": "keeper", "kind": "greet", "cond": ["T:forgotten", "!R:bell"],
         "text": "I've kept the Deathguard away from the east hill. Told them it's adders. Don't make a liar of me."},
        {"npc": "keeper", "kind": "greet", "cond": ["A:fresh"],
         "text": "North side, by the yew. Mind the soft ground; it isn't always empty."},
        {"npc": "keeper", "kind": "greet", "cond": ["A:names"],
         "text": "The ledgers are in a terrible state. I kept them dry for twenty years and then I died and nobody "
                 "else did. Shall we?"},
        {"npc": "keeper", "kind": "greet",
         "texts": ["Mind the newer stones. The ground hasn't settled. Neither, some days, have the residents.",
                   "Every name in this ground was someone's. I keep them straight. It's the least I can do, and in this "
                   "town the least is a great deal.",
                   "You're welcome to walk here. Only don't stand on anyone. They notice, these days."]},
        {"npc": "keeper", "kind": "option", "cond": ["I:names"], "text": "(Help Mortimer sort the burial ledgers.)",
         "action": "credit", "quest": "names", "credit": "ledger_credit", "emote": 1,
         "reply": "Plague year on the left, after on the right. Births in the green book, there were so few. Thank you, "
                  "$n.$BHere's the odd thing: Hollin. Hale. Fairweather. Shaw. Written twice. Go and see their stones "
                  "for me, along the wall, and the Lyle stone at the end."},
        {"npc": "keeper", "kind": "option", "cond": ["I:bell"], "text": "(Ring the bell over the lychgate.)",
         "action": "credit", "quest": "bell", "credit": "rung_credit", "emote": 2,
         "reply": "(The bell sounds once, flat and cracked, out over the town. On the cemetery wall, four figures stand "
                  "very still until it fades.)"},
        {"npc": "keeper", "kind": "option", "cond": ["R:house.floorboards"],
         "text": "Oswin Thatcher said to ask you about a mark in my cellar.", "action": "say",
         "reply": "A crowned eye, on brick? I know of it, though not from my books. Brill had a benefactor in the plague "
                  "year, a Master Croft, who paid for many kindnesses and some walls. Ask the Deathstalker by the "
                  "mausoleum. She's been waiting for someone to."},
        # Mercy Hollin at the mausoleum: found, and the choice of how they'll face Brill.
        {"npc": "mercy", "kind": "option", "cond": ["I:forgotten"],
         "text": "I'm not here to hurt you. Mortimer Weller sent me.", "action": "credit", "quest": "forgotten",
         "credit": "met_credit", "emote": 6,
         "reply": "Weller. The clerk. ...Put your hands where I can see them, and come up slowly."},
        {"npc": "mercy", "kind": "option", "cond": ["I:aname"],
         "text": "Walk into Brill by daylight, under your own names. Let them see you.", "action": "choice",
         "quest": "aname", "credit": "decided_credit", "marker": "openly", "emote": 273,
         "reply": "By daylight. Walter will hate it. ...Good. Let them look; we'll look back. I delivered half the "
                  "Deathguard's grandmothers."},
        {"npc": "mercy", "kind": "option", "cond": ["I:aname"],
         "text": "Come in quietly, at night, with the gravekeeper's word ahead of you.", "action": "choice",
         "quest": "aname", "credit": "decided_credit", "marker": "quietly", "emote": 273,
         "reply": "Quietly, then. Edith will be glad. Not everyone wants to be a curiosity, $n. Some of us only want to "
                  "be left to sew."},
        # Magistrate Sevren's rolls.
        {"npc": 1499, "kind": "option", "cond": ["I:bell"],
         "text": "Gravekeeper Weller asks that four names be entered on Brill's rolls.", "action": "credit",
         "quest": "bell", "credit": "rolls_credit", "emote": 1,
         "reply": "Four more risen, and the Deathguard didn't find them first? Unusual. ...Hollin, Hale, Fairweather, "
                  "Shaw. Entered, under the Dark Lady's protection. Tell them they owe tithe from the next harvest, the "
                  "same as everyone. Freedom has its paperwork."},
        # At the mausoleum: who they are while hiding, and afterward (they come back to it some nights).
        {"npc": "mercy", "kind": "greet", "cond": ["R:bell"],
         "text": "I come back up here some nights. It was the first place I was myself. Brill is louder than I "
                 "remember."},
        {"npc": "mercy", "kind": "greet", "cond": ["T:forgotten"],
         "text": "Keep your voice low. Walter startles."},
        {"npc": "mercy", "kind": "greet",
         "text": "(A grey-faced woman blocks the mausoleum door with a spade held like a pike.)$B$BThis is a tomb. "
                 "There's nothing for you here. Go on."},
        {"npc": "tobias", "kind": "greet", "cond": ["R:bell"],
         "text": "Mercy's up here again, is she? I came to fix the hinge. Somebody should. It kept us."},
        {"npc": "tobias", "kind": "greet",
         "text": "I cut half the stones down in that cemetery, you know. Mine too. Didn't expect to read it from the "
                 "wrong side."},
        {"npc": "agnes", "kind": "greet", "cond": ["R:bell"],
         "text": "It's quiet up here. I come to sew when the town gets to be too much."},
        {"npc": "agnes", "kind": "greet",
         "text": "Please don't look at my face. I know what's left of it. I'd... rather you looked at my hands. They "
                 "still know how to work."},
        {"npc": "walter", "kind": "greet", "cond": ["R:bell"],
         "text": "Don't tell the others I come up here. I like the view. From up here Brill looks like it did."},
        {"npc": "walter", "kind": "greet",
         "text": "I remember the Deathguard's blade going in. I remember being grateful. Then I woke up again. Do you "
                 "understand? I don't want to be grateful twice."},
        # In Brill, by the choice they made.
        {"npc": "mercy_town", "kind": "greet", "cond": ["M:openly", "DAY:3"],
         "text": "Junior Apothecary Holland asked me to look at a sow that's farrowing. I said I've never midwifed a "
                 "pig. He said nor has anyone in Brill, these days. So I'm going."},
        {"npc": "mercy_town", "kind": "greet", "cond": ["M:openly"],
         "text": "$n! Come and be seen with me. The more people I'm seen talking to, the fewer think I'm here to eat "
                 "them."},
        {"npc": "mercy_town", "kind": "greet",
         "text": "I help Mortimer with the graves, nights. I listen for knocking. There hasn't been any since. I keep "
                 "listening."},
        {"npc": "tobias_town", "kind": "greet", "cond": ["R:gallows.nomasters"],
         "text": "Isolde told me what was behind my wall. I'll be cutting thirty-one stones this winter, $n. I'll do "
                 "them properly. It's what I owe."},
        {"npc": "tobias_town", "kind": "greet", "cond": ["M:openly"],
         "text": "Three commissions already. Forsaken want their names on something solid. I understand the feeling."},
        {"npc": "tobias_town", "kind": "greet",
         "text": "I mend what the Deathguard break. Steps, walls, the odd gravestone. Nobody asks where I learned. "
                 "Suits me."},
        {"npc": "agnes_town", "kind": "greet", "cond": ["M:quietly"],
         "text": "Nobody knows. They think I came down from the Undercity for the quiet. I let them. I'm making "
                 "shrouds for Mortimer, good ones. Somebody ought to be buried properly."},
        {"npc": "agnes_town", "kind": "greet",
         "text": "A girl from the inn stared at me for a whole afternoon, and then asked me to teach her to spin. I "
                 "almost ran. I didn't."},
        {"npc": "walter_town", "kind": "greet", "cond": ["M:openly"],
         "text": "Dillinger offered me a tabard. Me, in the Deathguard. After what they did. ...I'm thinking about "
                 "it. Somebody ought to remember what it's like on the other end."},
        {"npc": "walter_town", "kind": "greet",
         "text": "I stand the north road at night. Nobody asked me to. Old habit. Brill militia: he stood."},
    ],
    "phases": {
        # The four live in Brill once the last bell has rung.
        "newcomers": [["R:bell"]],
    },
}
