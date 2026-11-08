# SPDX-License-Identifier: GPL-3.0-or-later
"""A Deathguard's Duty: five quests for Deathguard Dillinger (1496), the senior Deathguard on Brill's north
road. The watch is short-handed and Deathguard Harlan has been missing his patrols; the player carries the
watch's supplies, clears the north road and follows his tracks west to Solliden Farmstead, where Harlan,
a farmhand there in life, stands in the trees watching the cottage where his living wife Maren and their
daughter Lise still live. He can't go to them. The player helps him choose: back to his old post on the
north road (phase "returned") or a post at the cemetery, his back to the west (phase "reassigned"). Before
the choice he isn't in Brill; on the hill above Solliden he's there for everyone (outside Brill, where the
town's phases don't reach), and says what his choice became.

The player's dog, Corn (DOG) is noticed along the way, never needed."""

DILLINGER = 1496
ABRAHAM = 1735       # on the north road, by the river
TERRENCE = 1738      # walks the Undercity road
LINNEA = 1495        # at the Undercity road's crossroads
LAWRENCE, BARTHOLOMEW = 1743, 1742   # Dillinger's watch on the north road

HARLAN = {"name": "Deathguard Harlan", "display": 2862, "level": 12, "faction": 68}

LINE = {
    "title": "A Deathguard's Duty",
    "quests": [
        {
            "id": "watch", "title": "The Night Watch", "giver": DILLINGER,
            "log": "Deliver supplies to Deathguard Abraham on the north road, Deathguard Terrence on the Undercity road and Deathguard Linnea at the crossroads. Then return to Deathguard Dillinger.",
            "offer": (
                "You there. You've got legs and you're not wearing a tabard, which makes you more use to me tonight "
                "than half the watch.$B$B"
                "Brill's Deathguard is stretched thinner than a ghoul's patience. The Executor sends the best of us to "
                "the Sepulcher and the Bulwark, the Crusade takes the unlucky ones, and the ones left are standing "
                "double watches. We don't tire, they say. Whoever says that hasn't stood eighteen hours on the same "
                "road.$B$B"
                "Take these packs to our posts outside town: Abraham at the river on the north road, Terrence on the "
                "Undercity road, Linnea at the crossroads. Oil, bandages, whetstones, a few letters."),
            "progress": "Packs delivered? The night won't wait for you, $n, and neither will the Scourge.",
            "done": (
                "Abraham says thank you. Terrence says nothing, which for Terrence is thank you. Linnea says she's "
                "been asking for whetstones since the Third War.$B$B"
                "That's one night covered. Brill has a lot of nights, $n."),
            "objectives": [("credit", "abraham_credit", 1, "Supplies delivered to Deathguard Abraham"),
                           ("credit", "terrence_credit", 1, "Supplies delivered to Deathguard Terrence"),
                           ("credit", "linnea_credit", 1, "Supplies delivered to Deathguard Linnea")],
            "return": "Return to Deathguard Dillinger on Brill's north road.",
            "items": [(858, 2)], "money": 1800, "xp": 4,
        },
        {
            "id": "road", "title": "Trouble on the Road", "giver": DILLINGER, "prev": "watch",
            "log": "Search the 3 wrecked carts on the north road between Brill and the river, and kill 4 Roadside Ghouls and Gnawbone. Then return to Deathguard Dillinger.",
            "offer": (
                "Abraham sent word back with you, did you notice? No, of course not; you were busy being thanked.$B$B"
                "Travelers on the north road have been set upon between here and the river. A tinker from Deathknell, "
                "two apothecaries' runners, a cart of Agamand grain. Something drags them off the road at night and "
                "leaves the carts. Scourge stragglers, by the sound of it: ghouls, and one big enough that the "
                "survivors gave it a name.$B$B"
                "That stretch is meant to be watched. It's Harlan's patrol. (Dillinger's jaw tightens.) It was Harlan's "
                "patrol. Go and look at the carts, find out what we're dealing with, and put it down."),
            "progress": "The road, $n. Every night it stays dangerous, someone in Brill goes without bread or oil or news.",
            "done": (
                "Gnawbone. Fitting. The survivors always have a way with names.$B$B"
                "The north road's clear for now. Which brings me to the thing I didn't want to say: that road was only "
                "open to the ghouls because there was no one on it. Harlan's missed four patrols this month. He comes "
                "back before the bell, says nothing, stands his post like nothing happened. Then he's gone again."),
            "objectives": [("credit", "cart_credit", 3, "Wrecked cart searched"),
                           ("kill", "ghoul", 4, ""),
                           ("kill", "gnawbone", 1, "")],
            "return": "Return to Deathguard Dillinger on Brill's north road.",
            "items": [(2455, 2)], "money": 2500, "xp": 4,
        },
        {
            "id": "post", "title": "An Empty Post", "giver": DILLINGER, "ender": "harlan", "prev": "road",
            "log": "Ask Deathguard Lawrence and Deathguard Bartholomew about Harlan, follow his tracks west from the river, and find Deathguard Harlan.",
            "offer": (
                "Deserting a post is a hanging matter in the Deathguard. I don't want to hang Harlan. He's a good "
                "guard; he was a good farmhand before that, by all accounts, and he never once complained about "
                "either. But the Executor will notice soon, and when he does it won't be my decision anymore.$B$B"
                "Lawrence and Bartholomew stood watch beside him longest. Ask them what they've seen. Then go and find "
                "him before anyone else does. Last time he went missing someone saw tracks heading west from the "
                "river, toward the old farms.$B$B"
                "Bring him back if you can. If you can't, at least tell me why."),
            "progress": "(Deathguard Harlan does not turn around.) I know Dillinger sent you. Give me a moment.",
            "done": (
                "(The Deathguard on the hill doesn't turn when you come up behind him. He's looking down at the "
                "farmstead below, at a cottage with smoke rising from its chimney.)$B$B"
                "I know who sent you. Dillinger's a decent sort; he'd send someone quiet before he sent a noose. Tell "
                "him I'm not deserting. I'm only... standing a different watch.$B$B"
                "(He nods toward the cottage.)$B$B"
                "I was a farmhand at Solliden, before. That's my house. My wife's in it. My daughter. They lived, "
                "$n. The plague came through and they lived, and I didn't, and then I came back. Like this."),
            "objectives": [("credit", "lawrence_credit", 1, "Deathguard Lawrence asked about Harlan"),
                           ("credit", "bartholomew_credit", 1, "Deathguard Bartholomew asked about Harlan"),
                           ("credit", "tracks_credit", 3, "Harlan's tracks followed")],
            "return": "Find Deathguard Harlan.",
            "money": 2000, "xp": 4,
        },
        {
            "id": "house", "title": "The House Beyond the Trees", "giver": "harlan", "prev": "post",
            "log": "Go down to the cottage at Solliden Farmstead for Deathguard Harlan: speak with Maren and Lise Ashby, and see what he has been leaving at their gate. Then return to Harlan on the hill.",
            "offer": (
                "I come here every night I can steal. I stand in these trees and I watch the lamp in the window until "
                "it goes out. I tell myself it's to keep the ghouls away from them. Mostly it is.$B$B"
                "I can't go down there. Look at me. Maren would scream, and she'd be right to; Lise would remember me "
                "like this instead of how I was. The farmers down there would put a pitchfork through me, and I'd let "
                "them.$B$B"
                "But you could go. You're a stranger. You could pass the gate and say good evening and look at them "
                "properly, which I haven't done in seven years. Tell me if Lise is well. Tell me if Maren still smiles "
                "at people. And see if... see if the wood's still there, by the gate. I'd like to know if they use it."),
            "progress": "Did you see them? (He keeps his eyes on the cottage.) Tell me slowly.",
            "done": (
                "She found the wood. She thinks it's a neighbor.$B$B"
                "(Harlan is quiet a long time.)$B$B"
                "Lise has my mother's chin. She was four when I died; I didn't know what she'd look like. Now I do. "
                "That's more than most of us get, $n. More than I had any right to.$B$B"
                "(He finally looks away from the cottage.)$B$B"
                "I can't keep doing this. Dillinger's covered for me as long as he can, and the road paid for it. "
                "Something has to change."),
            "objectives": [("credit", "maren_credit", 1, "Spoke with Maren Ashby"),
                           ("credit", "lise_credit", 1, "Spoke with Lise Ashby"),
                           ("credit", "firewood_credit", 1, "Firewood at the gate found")],
            "return": "Return to Deathguard Harlan on the hill above Solliden Farmstead.",
            "items": [(858, 1)], "money": 1500, "xp": 4,
        },
        {
            "id": "duty", "title": "Duty and Memory", "giver": "harlan", "ender": DILLINGER, "prev": "house",
            "log": "Help Deathguard Harlan decide: return to his post on the north road, or ask for a post away from his old home. Then return to Deathguard Dillinger.",
            "offer": (
                "There are two ways this goes. I've had seven years to think them through, and I still can't pick one "
                "on my own.$B$B"
                "I go back to my post on the north road. I stand my watch, every hour of it. It's the road that runs "
                "toward this place; I'd keep the ghouls off it and off them, and on my free days... I'd come here, "
                "and stand in the trees, and go home again before the bell. Once a week. No more.$B$B"
                "Or I ask Dillinger for a post on the other side of Brill. The cemetery, say. Facing east, my back to "
                "all this. I'd never see the lamp in that window again. Maybe that's what lets a man rest.$B$B"
                "You've seen them now. You've seen me. Tell me which, $n. I'll do it."),
            "progress": "(Harlan waits, his eyes on the cottage's lamp.)",
            "done": (
                "Harlan told me himself. Walked up to me and reported, as if he'd been gone an hour.$B$B"
                "(Dillinger shakes his head slowly.)$B$B"
                "Solliden. His wife and his girl, alive, an hour's walk from his post, and he never said a word. Seven "
                "years. I've known men go to pieces over less, $n, living or dead. He'll do, now. You saw to that.$B$B"
                "The Executor will hear he was on special duty for me. That's not even a lie, the way I count it. "
                "Thank you. Brill's watch is whole again."),
            "objectives": [("credit", "duty_credit", 1, "Deathguard Harlan's choice made")],
            "return": "Return to Deathguard Dillinger on Brill's north road.",
            "items": [(858, 3)], "money": 3500, "xp": 5,
        },
    ],
    "markers": ["returned", "reassigned"],
    "npcs": [
        # Harlan above Solliden (everyone's: outside Brill), then in Brill by his choice.
        dict(HARLAN, id="harlan", flags=["gossip", "quest"], spawns=[[0, 2285.0, 1235.0, 38.67, 1.80]]),
        dict(HARLAN, id="harlan_post", flags=["gossip"], spawns=[[0, 2262.0, 428.0, 35.39, 0.0]], phase="returned"),
        dict(HARLAN, id="harlan_east", flags=["gossip"], spawns=[[0, 2345.0, 385.0, 34.26, 4.71]], phase="reassigned"),
        # His living family, at the cottage.
        {"id": "maren", "name": "Maren Ashby", "display": 18618, "level": 5, "faction": 35, "type": 7,
         "flags": ["gossip"], "spawns": [[0, 2262.0, 1292.0, 31.9, 4.6]]},
        {"id": "lise", "name": "Lise Ashby", "display": 252, "level": 1, "faction": 35, "type": 7,
         "flags": ["gossip"], "spawns": [[0, 2266.0, 1288.0, 31.42, 3.0]], "wander": 3},
        # What's been attacking the north road.
        {"id": "ghoul", "name": "Roadside Ghoul", "display": 829, "hostile": True, "faction": 21, "level": (9, 10),
         "type": 6, "health": 1, "damage": 1, "gold": 0, "wander": 5,
         # (in the trees either side of the road, west of the Harrow farmhouse, short of Abraham's post at the
         # covered bridge: the road's line from the zone's minimap, heights from the game's terrain)
         "spawns": [[0, 2252.5, 540.0, 34.8, 1.0], [0, 2272.5, 552.0, 34.32, 3.0],
                    [0, 2244.2, 560.0, 33.89, 4.5], [0, 2236.0, 590.0, 33.33, 0.5]]},
        {"id": "gnawbone", "name": "Gnawbone", "display": 1202, "scale": 1.25, "hostile": True, "faction": 21,
         "level": 11, "type": 6, "health": 2.5, "damage": 1.3, "gold": 120, "respawn": 180,
         "spawns": [[0, 2270.3, 560.0, 35.37, 3.6]]},
    ],
    "credits": [
        {"id": "abraham_credit", "name": "Supplies delivered to Deathguard Abraham"},
        {"id": "terrence_credit", "name": "Supplies delivered to Deathguard Terrence"},
        {"id": "linnea_credit", "name": "Supplies delivered to Deathguard Linnea"},
        {"id": "brazier_credit", "name": "Patrol brazier stoked"},   # (no longer asked for; kept so the entries after it keep their numbers)
        {"id": "cart_credit", "name": "Wrecked cart searched"},
        {"id": "lawrence_credit", "name": "Deathguard Lawrence asked about Harlan"},
        {"id": "bartholomew_credit", "name": "Deathguard Bartholomew asked about Harlan"},
        {"id": "tracks_credit", "name": "Harlan's tracks followed"},
        {"id": "maren_credit", "name": "Spoke with Maren Ashby"},
        {"id": "lise_credit", "name": "Spoke with Lise Ashby"},
        {"id": "firewood_credit", "name": "Firewood at the gate found"},
        {"id": "duty_credit", "name": "Deathguard Harlan's choice made"},
    ],
    "objects": [
        # Wrecked carts at the road's edge where they were dragged off it (the zone's own broken cart).
        {"id": "cart", "name": "Wrecked Cart", "display": 7524,
         "quest_only": True,
         "spawns": [[0, 2268.0, 545.0, 33.36, 2.3], [0, 2248.8, 566.0, 33.44, 1.6], [0, 2254.5, 586.0, 34.06, 2.4]],
         "use": [
             {"cond": ["I:road"], "quest": "road", "credit": "cart_credit"},
         ]},
        {"id": "tracks", "name": "Bootprints", "quest_only": True, "display": 498, "scale": 0.5,
         "spawns": [[0, 2208.0, 690.0, 34.9, 0.0], [0, 2230.0, 900.0, 48.0, 0.0], [0, 2250.0, 1150.0, 34.13, 0.0]],
         "use": [
             {"cond": ["I:post"], "quest": "post", "credit": "tracks_credit"},
         ]},
        {"id": "firewood", "name": "Bundle of Firewood", "quest_only": True, "display": 1248, "scale": 0.6,
         "spawns": [[0, 2257.0, 1287.0, 32.11, 1.0]],
         "use": [
             {"cond": ["I:house"], "quest": "house", "credit": "firewood_credit"},
         ]},
    ],
    "gossip": [
        # Dillinger.
        {"npc": DILLINGER, "kind": "greet", "cond": ["R:duty", "M:returned", "DAY:2"], "texts": [
            "Harlan stood his whole watch last night and the night before. Didn't miss a bell. (Dillinger almost "
            "smiles.) Brill owes you for that, $n. So do I.",
            "Quiet on the north road. Harlan sees to it. Took his rest day at Solliden, came back before the bell, "
            "same as he promised. You're welcome at my fire any night you like, $n."]},
        {"npc": DILLINGER, "kind": "greet", "cond": ["R:duty", "M:reassigned", "DAY:2"], "texts": [
            "Harlan's taken to the cemetery watch like he was born to it. Well. Died to it. He doesn't look west "
            "anymore. Brill's in your debt, $n.",
            "New lad on the north road now; keen, careless. I miss Harlan's patience out there, but he's whole at "
            "the cemetery, and that's what counts. Good to see you, $n."]},
        {"npc": DILLINGER, "kind": "greet", "cond": ["R:duty", "DAY:3"],
         "text": "$n. The watch knows your name now. Not many living or dead can say that in Brill."},
        {"npc": DILLINGER, "kind": "greet", "cond": ["A:watch", "DOG"],
         "text": "That pug yours? Corn, is it. Small, but he's one of ours now, stitches and all. Take him on your rounds; "
                 "ghouls don't like a dog that doesn't flinch, and that one's past flinching."},
        {"npc": DILLINGER, "kind": "greet", "cond": ["T:post", "!R:duty"],
         "text": "Any word of Harlan? (Dillinger glances toward the north road.) I'll stand his watch until you're back."},
        {"npc": DILLINGER, "kind": "greet", "cond": ["M:scarlet.exposed", "!T:watch"],
         "text": "You're the one who found Sevren's leak. Two of ours died on that east road. (Dillinger nods.) If you've "
                 "a mind to help the watch, I've work."},
        {"npc": DILLINGER, "kind": "option", "cond": ["DOG", "A:road"], "text": "(Let Corn sniff the cart's scent from your gloves.)",
         "action": "say",
         "reply": "Ha. He's got the stink of ghoul in his nose now; he'll growl before you see them. Keep him close on the "
                  "north road."},

        # Delivering the packs (The Night Watch).
        {"npc": ABRAHAM, "kind": "option", "cond": ["I:watch"], "text": "Dillinger sent supplies for your post.",
         "action": "credit", "quest": "watch", "credit": "abraham_credit",
         "reply": "Oil! And a whetstone. (Abraham turns them over in his hands.) Thank Dillinger for me. And tell him the "
                  "north road's been bad at night. Whoever's meant to be patrolling between here and Brill, isn't."},
        {"npc": TERRENCE, "kind": "option", "cond": ["I:watch"], "text": "Supplies from Dillinger, Terrence.",
         "action": "credit", "quest": "watch", "credit": "terrence_credit",
         "reply": "(Terrence takes the pack without breaking stride, checks it, and grunts.)"},
        {"npc": LINNEA, "kind": "option", "cond": ["I:watch"], "text": "Dillinger sends whetstones and oil.",
         "action": "credit", "quest": "watch", "credit": "linnea_credit",
         "reply": "Whetstones. I have been asking for whetstones since before the Dark Lady was a lady. (She tests one "
                  "with a thumb.) Tell Dillinger he's forgiven. Mostly."},

        # Asking after Harlan (An Empty Post).
        {"npc": LAWRENCE, "kind": "option", "cond": ["I:post"], "text": "What do you know about Harlan's absences?",
         "action": "credit", "quest": "post", "credit": "lawrence_credit",
         "reply": "Harlan? Steady as a gravestone. Never talks about before. (Lawrence hesitates.) Only once, the night "
                  "the farmers at Solliden lit a harvest fire you could see from here. He stared at it until dawn. "
                  "Said nothing. Next week, he started going missing."},
        {"npc": BARTHOLOMEW, "kind": "option", "cond": ["I:post"], "text": "Where does Harlan go when he leaves his post?",
         "action": "credit", "quest": "post", "credit": "bartholomew_credit",
         "reply": "West. Always west, over the river. (Bartholomew lowers his voice.) He takes firewood with him. Splits it "
                  "himself behind the stables. What does a dead man want with firewood, I ask you?"},

        # Harlan above Solliden.
        {"npc": "harlan", "kind": "greet", "cond": ["M:returned"],
         "text": "My rest day. (Harlan doesn't look away from the cottage.) I stand here till the lamp goes out, then I walk "
                 "back and take the dawn watch. Once a week. It's enough. It has to be."},
        {"npc": "harlan", "kind": "greet", "cond": ["M:reassigned"],
         "text": "Last time. I told myself that, coming up the hill. (Harlan turns away from the cottage.) I'll be at the "
                 "cemetery tomorrow, facing east. Don't tell me if the lamp's still lit."},
        {"npc": "harlan", "kind": "greet", "cond": ["A:house", "DOG"],
         "text": "A pug. (Something in Harlan's face softens.) We had a dog. Lise named it Pudding. Leave yours here with "
                 "me while you go down; the farmers will take him for a stray and loose the hounds."},
        {"npc": "harlan", "kind": "greet", "cond": ["T:post"],
         "text": "(Harlan watches the cottage below. Smoke rises from its chimney.)"},
        {"npc": "harlan", "kind": "greet",
         "text": "Move along. I'm on patrol. (The Deathguard keeps his eyes on the farmstead below, and doesn't seem to be "
                 "patrolling anything.)"},
        {"npc": "harlan", "kind": "option", "cond": ["I:duty"], "text": "Your post is waiting, Harlan. Brill needs you on that road.",
         "action": "choice", "quest": "duty", "credit": "duty_credit", "marker": "returned", "emote": 273,
         "reply": "The road it is. (Harlan squares his shoulders.) It runs this way, at least. I'll keep it clean for them, "
                  "and once a week I'll come and stand in the trees. Tell Dillinger I'll be at my post before the bell."},
        {"npc": "harlan", "kind": "option", "cond": ["I:duty"], "text": "Ask Dillinger for another post. Let them go, Harlan.",
         "action": "choice", "quest": "duty", "credit": "duty_credit", "marker": "reassigned", "emote": 2,
         "reply": "Let them go. (He says it as if testing the weight of it.) They let me go seven years ago. It's only fair. "
                 "(Harlan takes a last look at the window.) Tell Dillinger I'll take the cemetery. The dead don't need "
                 "firewood."},

        # His family.
        {"npc": "maren", "kind": "greet", "cond": ["R:duty", "M:reassigned"],
         "text": "No firewood at the gate this month. (Maren pulls her shawl tighter.) Silly. I'd started thinking of it "
                 "as a friend. Some kind neighbor I never saw."},
        {"npc": "maren", "kind": "greet", "cond": ["R:duty", "M:returned"],
         "text": "Wood at the gate again this morning. Every seventh day, now, regular as a bell. (She smiles, a little "
                 "puzzled.) Whoever it is, I hope they're warm."},
        {"npc": "maren", "kind": "greet",
         "text": "(The woman by the cottage stiffens when she sees you, one hand on the doorframe.) We've nothing worth "
                 "taking, stranger. The farmers are just across the yard."},
        {"npc": "maren", "kind": "option", "cond": ["I:house"], "text": "I'm only passing. You keep a fine garden.",
         "action": "credit", "quest": "house", "credit": "maren_credit",
         "reply": "(She studies you a long moment, then lets her hand fall.) It was my husband's garden. He died in the "
                  "plague; everyone did, nearly. Lise and I stayed. People in Brill used to be people, you know. "
                  "(Her voice softens.) Someone leaves wood at the gate. Every week. I never see who. Good evening."},
        {"npc": "lise", "kind": "greet",
         "text": "(A girl of eleven or so peers at you from behind the fence.) Mama says not to talk to strangers from Brill."},
        {"npc": "lise", "kind": "option", "cond": ["I:house"], "text": "(Ask the girl her name.)",
         "action": "credit", "quest": "house", "credit": "lise_credit",
         "reply": "Lise. Lise Ashby. (She tilts her head.) My papa was a farmhand here. I don't remember him much. He used "
                  "to carry me on his shoulders to see the lamps in Brill. Mama says he'd want me to be brave. Are you "
                  "brave?"},
        {"npc": "lise", "kind": "option", "cond": ["DOG", "A:house"], "text": "(Let her pat Corn.)",
         "action": "say", "emote": 4,
         "reply": "(Lise squeals and throws her arms around Corn's neck. He snorts and licks her ear.) We had a dog! His name "
                  "was Pudding! He was bigger than this one. Well. I was smaller."},

        # Harlan in Brill, by his choice.
        {"npc": "harlan_post", "kind": "greet", "cond": ["DAY:3"],
         "text": "Rest day tomorrow. (Harlan's eyes go west, just for a moment, then back to the road.) Quiet watch. "
                 "Exactly how I like it."},
        {"npc": "harlan_post", "kind": "greet",
         "text": "North road's clear, $n. Not a ghoul between here and the river. (He nods once.) Thanks to you, I'm "
                 "standing where I ought to be."},
        {"npc": "harlan_east", "kind": "greet", "cond": ["DAY:3"],
         "text": "The dead in this cemetery don't want anything from me. (Harlan leans on his halberd.) There's a peace "
                 "in that. Most days."},
        {"npc": "harlan_east", "kind": "greet",
         "text": "Cemetery watch, $n. Facing east, toward the Plaguelands and whatever comes out of them. (He doesn't look "
                 "back over his shoulder. It seems to take some effort.)"},
    ],
    "phases": {
        "returned": [["M:returned"]],
        "reassigned": [["M:reassigned"]],
    },
}
