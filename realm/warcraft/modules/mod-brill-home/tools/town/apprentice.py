# SPDX-License-Identifier: GPL-3.0-or-later
"""The Apothecary's Apprentice: five quests from Apothecary Johaan about his apprentice, Wendell Crane, who
has been stealing the laboratory's reagents to brew "the Stay", a tincture meant to slow the decay of
Forsaken flesh. It ends with the player's judgment, on Johaan: the notes surrendered to the Royal
Apothecary Society, the work allowed to go on under Johaan's eye, or the notes burned. The rewards are the
same; the yard behind the laboratory changes (a phase each for "supervised" and "destroyed") and Johaan's
and Wendell's words follow the choice. Stands alone; acknowledges the cistern's line where it fits."""

# The yard behind Johaan's laboratory (the farmhouse WMO at 2261.9, 345.1, its door to the north-east):
# open ground at 35.2, by the game's terrain.
WENDELL_AT = [0, 2249.5, 343.5, 35.2, 3.14]
SHED_AT = [0, 2250.5, 355.0, 35.2, 5.62]

LINE = {
    "title": "The Apothecary's Apprentice",
    "quests": [
        {
            "id": "odor", "title": "An Unpleasant Odor", "giver": 1518, "ender": 1518,
            "log": "Investigate the locked storage shed behind Apothecary Johaan's laboratory in Brill, then return to Johaan.",
            "offer": (
                "You there. You have a nose, I trust? Most of Brill has stopped using theirs, which is a mercy, given the "
                "town's chief exports.$B$B"
                "Things have been going missing from my stores. Embalming salts. Grave moss. Three flasks of distilled bile "
                "I was saving for a particularly ungrateful Scarlet. I keep inventories, $n. I may be the only person left "
                "in Tirisfal who keeps inventories.$B$B"
                "And for a week now there has been a smell from the storage shed behind the laboratory. Not our usual smell. "
                "Something sweet beneath it, like lilies left too long on a coffin. I do not keep lilies.$B$B"
                "The shed is locked, and I did not lock it. Go and look. Through the boards, if you must. Tell me what is in "
                "there before I am obliged to go and see for myself."),
            "progress": "Well? I can smell it from here. Which, I assure you, is saying something.",
            "done": (
                "A still. In my shed. With my salts in it.$B$B"
                "(Johaan pinches the bridge of his nose. A flake of skin comes away; he flicks it aside.)$B$B"
                "And crates bound for Solliden Farmstead. Someone is carting my reagents out of Brill and brewing with "
                "whatever is left behind my back. One of my apprentices, then. I have two, and I trust neither of them, "
                "which is the proper relationship.$B$B"
                "Well. At least they label their crates."),
            "objectives": [("credit", "shed_credit", 1, "Storage shed investigated")],
            "return": "Return to Apothecary Johaan in Brill.",
            "money": 1500, "xp": 3,
        },
        {
            "id": "reagents", "title": "Missing Reagents", "giver": 1518, "ender": 1518, "prev": "odor",
            "log": "Recover 4 crates of stolen reagents and examine the suspicious delivery at Solliden Farmstead, north of Brill, then return to Apothecary Johaan.",
            "offer": (
                "Solliden Farmstead lies north of here, past the mills. Old Solliden still walks his fields, though he no "
                "longer remembers what they are for, and the hands who work them are less pleasant company than he is. A "
                "quiet place to leave a crate, if one did not wish to be asked about it.$B$B"
                "Whatever was carted out there is mine, and the Society's, which is to say the Dark Lady's. Bring it back. "
                "Every crate you can find.$B$B"
                "And look for the delivery itself: a cart, a sack, a bill of lading, anything with a hand on it. Thieves are "
                "seldom clever, $n, but they are always careless about paper. I want to know who has been signing for my "
                "salts."),
            "progress": "My salts, $n. And the name. I will settle for the salts if I must.",
            "done": (
                "Crane.$B$B"
                "(Johaan is silent for a long moment.)$B$B"
                "Wendell Crane has been my apprentice for three years. He scrubs my glassware. He sweeps my floor. He has "
                "never once spoken out of turn, which I took for respect and ought to have taken for concealment.$B$B"
                "I won't question him. If I question him, I shall have to report whatever he says to the Society, and the "
                "Society does not believe in second chances. Or, in my experience, in first ones."),
            "objectives": [("credit", "crate_credit", 4, "Stolen reagents recovered"),
                           ("credit", "delivery_credit", 1, "Suspicious delivery examined")],
            "return": "Return to Apothecary Johaan in Brill.",
            "money": 3000, "xp": 4, "items": [(858, 2)],
        },
        {
            "id": "secret", "title": "The Apprentice's Secret", "giver": 1518, "ender": "wendell", "prev": "reagents",
            "log": "Speak with Wendell Crane in the yard behind Apothecary Johaan's laboratory in Brill.",
            "offer": (
                "You have returned my salts, and I am grateful, in my fashion. Now I need one thing more, and I need it from "
                "someone who is not me.$B$B"
                "Wendell works in the yard behind the laboratory, washing whatever I dirty. Go and speak with him. Show him "
                "those slips. I want to know what he has been brewing in my shed, and for whom. If he is selling to the "
                "Scarlets, or the Cult, or, the Dark Lady forbid, to the trolls, I will deal with it myself.$B$B"
                "If it is something else... then I want to know what it is before I decide what it is worth.$B$B"
                "He will talk to you. He has not talked to me in three years, except to say 'yes, Apothecary.'"),
            "done": (
                "(Wendell looks at the slips, then at his hands. Two fingers of the left are gone at the knuckle; the rest "
                "are bound in gauze.)$B$B"
                "So he knows. Of course he knows. He counts everything.$B$B"
                "I'm not selling it. I'm not selling anything. I'm trying to stop this.$B$B"
                "(He holds up the hand.)$B$B"
                "I washed the dead for burial in Andorhal, before the grain came. I know what happens to a body, $n. I know "
                "it to the day. We're no different; we're only slower. A finger a year. An ear. One morning you wake and your "
                "jaw won't close. The Society's salts keep the worst of it off. I'm making something that keeps us whole.$B$B"
                "I call it the Stay. And it works. Mostly."),
            "return": "Speak with Wendell Crane behind the laboratory in Brill.",
            "money": 1500, "xp": 2,
        },
        {
            "id": "question", "title": "A Question of Progress", "giver": "wendell", "ender": "wendell", "prev": "secret",
            "log": "Examine Wendell Crane's three caged darkhounds in the hills north-east of Brill and deal with whatever has become of the third, then return to Wendell.",
            "offer": (
                "Mostly. That's the word that keeps me up, and I don't even sleep.$B$B"
                "In a jar the Stay is perfect: no rot, no softening, not in six weeks. But a jar isn't a body. I needed "
                "something living and rotting at once, and Tirisfal has no shortage of those.$B$B"
                "The darkhounds north-east of town have the wasting sickness: fur coming out in handfuls, sores that never "
                "close. I baited three of them with dosed meat and caged them in the hills on the way to the lake. I haven't "
                "dared go back. Johaan watches the road, and I'm a coward besides.$B$B"
                "Look at them for me. All three. Tell me what the Stay has done to them. Whatever it is."),
            "progress": "Did it work? Don't tell me it didn't work. Tell me, but gently.",
            "done": (
                "One healed. One set like a tanned hide. And one... I heard it, you know. Last night, from the yard. I told "
                "myself it was the wind.$B$B"
                "(Wendell writes it all down, carefully, with his three good fingers.)$B$B"
                "The flesh holds. That much is true. But the stiffening, the madness... If the Stay does that to a hound's "
                "mind, what would it do to ours? Our minds are all that keep us from being the Scourge, $n. Will, and nothing "
                "else.$B$B"
                "I don't know whether I've made a cure or a cage."),
            "objectives": [("credit", "specimen_credit", 3, "Caged darkhounds examined"),
                           ("kill", "specimen", 1, "")],
            "return": "Return to Wendell Crane behind the laboratory in Brill.",
            "money": 3500, "xp": 4, "items": [(2455, 2), (858, 2)],
        },
        {
            "id": "judgment", "title": "The Apothecary's Judgment", "giver": "wendell", "ender": 1518, "prev": "question",
            "log": "Take Wendell Crane's notes on the Stay to Apothecary Johaan and decide what becomes of them.",
            "offer": (
                "I've written it all out. The recipe, the doses, the hounds. Every mistake.$B$B"
                "(He presses a bound sheaf of notes into your hands. The ink on the last page is still wet.)$B$B"
                "Take it to Johaan. I can't. If I stand in front of him I'll only say 'yes, Apothecary' and let him decide, "
                "the way I always have.$B$B"
                "You've seen what it does, the good and the bad. You decide what he hears. Give it to him, and the Society "
                "will have it, and Faranell's people in the Undercity will do with it whatever they do. Ask him to let me go "
                "on, under his eye, slowly, properly. Or burn it, and I'll go back to washing glass, and we'll all rot at the "
                "usual rate.$B$B"
                "Whatever you choose, I'll abide by it. I'm tired of being the only one who knows."),
            "progress": "You have something of Crane's. I can tell by the way you hold it. Like a dead bird.",
            "done": (
                "It is settled, then. Whatever we have done, we have done it with our eyes open, which is more than the Lich "
                "King ever allowed any of us.$B$B"
                "(Johaan opens his ledger and writes a single line. He blots it with great care.)$B$B"
                "Crane will hear it from me. You have earned a rest from my apprentices' troubles, and I have earned a rest "
                "from my own. Take these. They were brewed properly, by someone who keeps inventories."),
            "objectives": [("credit", "judgment_credit", 1, "Judgment given")],
            "return": "Return to Apothecary Johaan in Brill.",
            "money": 4500, "xp": 5, "items": [(2458, 2), (2459, 1)],
        },
    ],
    "markers": ["surrendered", "supervised", "destroyed"],
    "npcs": [
        {"id": "wendell", "name": "Wendell Crane", "subname": "Apprentice Apothecary", "display": 4111, "level": 15,
         "spawns": [WENDELL_AT]},
        # The third hound, out of its cage near it.
        {"id": "specimen", "name": "Frenzied Specimen", "display": 9020, "scale": 1.25, "hostile": True, "faction": 14,
         "level": 10, "type": 1, "health": 2.2, "damage": 1.3, "gold": 40, "wander": 4, "respawn": 60,
         "spells": [(3427, (3000, 5000), (12000, 16000))],
         "spawns": [[0, 2606.0, 186.0, 33.3, 2.5]]},
    ],
    "credits": [
        {"id": "shed_credit", "name": "Storage shed investigated"},
        {"id": "crate_credit", "name": "Stolen reagents recovered"},
        {"id": "delivery_credit", "name": "Suspicious delivery examined"},
        {"id": "specimen_credit", "name": "Caged darkhounds examined"},
        {"id": "judgment_credit", "name": "Judgment given"},
    ],
    "objects": [
        # The shed behind the laboratory (everyone's; its words follow the line and the choice).
        {"id": "shed", "name": "Locked Storage Shed", "display": 662, "spawns": [SHED_AT],
         "use": [{"cond": ["I:odor"], "quest": "odor", "credit": "shed_credit"}]},
        # Wendell's washing, in the yard (everyone's).
        {"id": "basin", "name": "Washbasin", "display": 7485, "spawns": [[0, 2247.6, 344.6, 35.2, 1.6]]},
        {"id": "glassware", "name": "Dirty Glassware", "display": 4073, "spawns": [[0, 2247.4, 342.4, 35.2, 4.0]]},
        # Johaan's reagents at Solliden Farmstead, and the cart they came on.
        {"id": "crate", "name": "Pilfered Reagent Crate", "quest_only": True, "display": 335,
         "spawns": [[0, 2286.0, 1298.0, 32.2, 1.0], [0, 2294.0, 1322.0, 31.5, 2.2], [0, 2276.0, 1334.0, 33.5, 4.1],
                    [0, 2300.0, 1305.0, 31.4, 0.4]],
         "use": [{"cond": ["I:reagents"], "quest": "reagents", "credit": "crate_credit"}]},
        {"id": "cart", "name": "Abandoned Handcart", "quest_only": True, "display": 7524, "spawns": [[0, 2280.0, 1288.0, 31.5, 0.8]],
         "use": [{"cond": ["I:reagents"], "quest": "reagents", "credit": "delivery_credit"}]},
        # Wendell's caged darkhounds in the hills north-east of Brill: one healed, one set stiff, one gone.
        {"id": "cage_healed", "name": "Wendell's Cage", "display": 4151, "scale": 0.7,
         "spawns": [[0, 2450.0, 200.0, 37.5, 1.0]],
         "use": [{"cond": ["I:question"], "quest": "question", "credit": "specimen_credit"}]},
        {"id": "cage_stiff", "name": "Wendell's Cage", "display": 4151, "scale": 0.7,
         "spawns": [[0, 2522.0, 252.0, 47.0, 3.0]],
         "use": [{"cond": ["I:question"], "quest": "question", "credit": "specimen_credit"}]},
        {"id": "cage_broken", "name": "Wendell's Cage", "display": 4151, "scale": 0.7,
         "spawns": [[0, 2602.0, 182.0, 34.0, 5.0]],
         "use": [{"cond": ["I:question"], "quest": "question", "credit": "specimen_credit"}]},
        # The yard after the judgment. Supervised: Wendell's own bench, the still brought out into the open.
        {"id": "apparatus", "name": "Crane's Apparatus", "display": 4391, "phase": "supervised",
         "spawns": [[0, 2246.6, 340.4, 35.2, 3.3]]},
        {"id": "retort", "name": "Bubbling Retort", "display": 7448, "scale": 0.45, "phase": "supervised",
         "spawns": [[0, 2245.8, 346.0, 35.2, 0.0]]},
        {"id": "ledger", "name": "Johaan's Ledger", "display": 254, "phase": "supervised",
         "spawns": [[0, 2251.2, 341.0, 35.2, 2.0]]},
        # Destroyed: the burned still before the shed, and a scrubbing bucket by Wendell.
        {"id": "ashes", "name": "Charred Remains", "display": 4251, "phase": "destroyed",
         "spawns": [[0, 2252.6, 352.0, 35.2, 0.6]]},
        {"id": "scrub_bucket", "name": "Scrubbing Bucket", "display": 239, "phase": "destroyed",
         "spawns": [[0, 2248.7, 345.0, 35.2, 0.0]]},
    ],
    "gossip": [
        # The judgment, on Johaan (the notes in hand).
        {"npc": 1518, "kind": "option", "cond": ["I:judgment"], "text": "(Hand him the notes.) It belongs to the Society. Take it.",
         "action": "choice", "quest": "judgment", "credit": "judgment_credit", "marker": "surrendered",
         "reply": "Sensible. Faranell will be delighted; he so rarely is. Crane will be credited, in a footnote, in a file no one reads. "
                  "That is more than most of us are given."},
        {"npc": 1518, "kind": "option", "cond": ["I:judgment"], "text": "Let him go on with it, Apothecary. Under your eye.",
         "action": "choice", "quest": "judgment", "credit": "judgment_credit", "marker": "supervised",
         "reply": "Under my eye. You do realize it is the only one I have left that still sits properly in its socket? ...Very well. A "
                  "bench in the yard, my reagents, my ledger, my rules. If a single hound bites anyone, it is both of you I report."},
        {"npc": 1518, "kind": "option", "cond": ["I:judgment"], "text": "(Burn the notes in the still behind the shed.) No one should have this.",
         "action": "choice", "quest": "judgment", "credit": "judgment_credit", "marker": "destroyed",
         "reply": "(Johaan watches the smoke rise from behind the laboratory and says nothing for a long while.)$B$BPerhaps. I would have "
                  "liked to read it first. That is the trouble with alchemists, $n. We always want to read everything first."},
        # Johaan's words after (and during: the theft on his mind).
        {"npc": 1518, "kind": "greet", "cond": ["M:surrendered"],
         "texts": ["Faranell wrote back. Three pages of questions and no thanks, and Crane's name misspelled twice. Still, the Society has "
                   "it now, and the Society forgets nothing it can use.",
                   "Crane says 'yes, Apothecary' again. I had grown used to the alternative. I find I do not care for the old way as much.",
                   "A courier from the Undercity asked whether I had any other apprentices with ideas. I told him no. It was very nearly true."]},
        {"npc": 1518, "kind": "greet", "cond": ["M:supervised"],
         "texts": ["Crane is at his bench before I am at mine. I have caught him humming. It is deeply unsettling.",
                   "I check his ledger every night. He checks mine. It is like having a conscience, only one that washes glassware.",
                   "The healed hound is still alive. I have named it Exhibit A. Crane calls it something else, and I have chosen not to hear what."]},
        {"npc": 1518, "kind": "greet", "cond": ["M:destroyed"],
         "texts": ["There is still a black patch behind the shed. I haven't had it raked. A reminder is cheaper than a sermon.",
                   "Crane scrubs the floors now as well as the glass. I did not ask him to. I have not asked him to stop.",
                   "Some nights I think of what was in those notes. Then I think of the third hound. Then I go back to work."]},
        {"npc": 1518, "kind": "greet", "cond": ["I:reagents"],
         "text": "Solliden, $n. My salts, and a name. My inventories do not lie. People do. Go and find out which of them."},
        # Wendell.
        {"npc": "wendell", "kind": "greet", "cond": ["M:surrendered", "R:well.clear"],
         "text": "Holland says the cask under the bridge was Society work, from before my time. I checked the batch numbers anyway. Twice. "
                 "I wanted to be sure it wasn't mine. I suppose nothing is mine now."},
        {"npc": "wendell", "kind": "greet", "cond": ["M:supervised", "R:well.clear"],
         "text": "Johaan has me boiling every drop I use, since the well. He says if we're going to keep bodies whole we'll start by "
                 "not poisoning them. I've written that on the wall."},
        {"npc": "wendell", "kind": "greet", "cond": ["M:surrendered"],
         "texts": ["The Society sent a courier for the notes. He read the first page on the doorstep and laughed. I don't know what that means. "
                   "I've decided not to find out.",
                   "Yes, Apothecary. No, Apothecary. I've had a great deal of practice.",
                   "Maybe they'll make something of it. Maybe in ten years some Deathguard will keep his fingers and never know my name. "
                   "That would be all right. I think that would be all right."]},
        {"npc": "wendell", "kind": "greet", "cond": ["M:supervised"],
         "texts": ["Johaan checks every dose twice. He says it's to keep me honest. I think he's interested. Don't tell him I said so.",
                   "Small doses, slow work, everything written down. It'll take years. We have years. It's the one thing we have plenty of.",
                   "The hound's flank is still closed. Six weeks now. I go out and look at it every morning, like it's the sunrise."]},
        {"npc": "wendell", "kind": "greet", "cond": ["M:destroyed"],
         "texts": ["I scrub the floors now as well as the glass. Johaan says it's so I'll know what's under my feet. I think it's so I won't "
                   "have time to think.",
                   "It was right to burn it. I tell myself so every morning, when I count my fingers.",
                   "The healed hound got out of its cage, they tell me. Somewhere in the hills there's one darkhound that won't rot. Good luck to it."]},
        {"npc": "wendell", "kind": "greet", "cond": ["A:judgment"],
         "text": "You have the notes. Don't read me what you've decided. I'll find out from his face."},
        {"npc": "wendell", "kind": "greet", "cond": ["R:secret"],
         "text": "You've seen the hand. You might as well see the rest."},
        {"npc": "wendell", "kind": "greet", "cond": ["A:odor"],
         "text": "The shed? It's... storage. For storage things. I wouldn't go near it, the smell's awful. You'll want to stay upwind. Far upwind."},
        {"npc": "wendell", "kind": "greet",
         "texts": ["Apprentice Crane. If you're looking for the Apothecary, he's inside, being disappointed in something.",
                   "Mind the basin; it's lye. It'll take the skin off. Not that I'd notice for a day or two.",
                   "Three years I've washed his glass. I could tell you every crack in every retort in Brill. Nobody asks."]},
        # Carolai Anise on it (her menu is src/BrillHome.cpp's; the line's options are added to it).
        {"npc": 2132, "kind": "option", "cond": ["M:destroyed"], "text": "(Ask her about Wendell Crane.)", "action": "say",
         "reply": "You burned it. Good. Some things shouldn't be kept, $n. Only the things that matter. Only the things that are yours."},
        {"npc": 2132, "kind": "option", "cond": ["M:supervised"], "text": "(Ask her about Wendell Crane.)", "action": "say",
         "reply": "Wendell brought me a jar of the Stay to look at. Fine work. Careful. I'd never let anyone put it in me, of course. I'd rather keep my rot. It's mine."},
        {"npc": 2132, "kind": "option", "cond": ["M:surrendered"], "text": "(Ask her about Wendell Crane.)", "action": "say",
         "reply": "The Society has his notes now. They'll make something of it, and none of us will be allowed to have it. That's what the Society is for."},
        {"npc": 2132, "kind": "option", "cond": ["R:secret", "!R:judgment"], "text": "(Ask her about Wendell Crane.)", "action": "say",
         "reply": "So it's Wendell. Poor thing. He asked me once whether lavender oil could cover the smell of a bad hand. I told him nothing covers it. You just stop letting people close enough to notice."},
        {"npc": 2132, "kind": "option", "cond": ["A:odor"], "text": "(Ask her about Johaan's missing ingredients.)", "action": "say",
         "reply": "Johaan's been counting his jars twice a day. He thinks I don't notice him counting mine as well. I don't steal, $n. I've never needed to."},
        {"npc": 2132, "kind": "option", "cond": ["A:reagents"], "text": "(Ask her about Johaan's missing ingredients.)", "action": "say",
         "reply": "Johaan's been counting his jars twice a day. He thinks I don't notice him counting mine as well. I don't steal, $n. I've never needed to."},
    ],
    "phases": {
        "supervised": [["M:supervised"]],
        "destroyed": [["M:destroyed"]],
    },
}
