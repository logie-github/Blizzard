# SPDX-License-Identifier: GPL-3.0-or-later
"""Whispers of the Scarlet: five quests for Magistrate Sevren (1499). The Scarlet Crusade knows Brill's
patrols; the letters its couriers burn when caught lead to Lowell Marsh, Brill's lamplighter, who walks
the streets with the night watch and has been writing their hours down for a Scarlet priest, Brother
Anselm, who promised to make him alive again. The player decides his fate: exposed to Sevren (taken
away), persuaded to give it up (he stays and lights the lamps), or let go down the west road (gone; now
and then a letter from him waits at the inn). His fate changes what Sevren, the inn and a few of the
Deathguard say.

Phase (one): "informant": Lowell Marsh is in Brill for everyone who hasn't had him taken away or let him
go. Choices are marks: exposed, spared, escaped."""

SEVREN = 1499
RENEE = 5688
WINTERS = 2134        # Mrs. Winters, General Supplies (the market)
ABIGAIL = 2118        # Abigail Shiel, Trade Supplies (the market)
ZEALOT = 1931         # Captured Scarlet Zealot, in the inn's cellar
BURGESS, CYRUS, MORRIS = 1652, 1746, 1745
GAVIN, ROYANN = 2209, 2210   # the cellar's guards

LINE = {
    "title": "Whispers of the Scarlet",
    "quests": [
        {
            "id": "letters", "title": "Letters in the Ashes", "giver": SEVREN,
            "log": "Kill 4 Scarlet Couriers in the hollow northeast of Brill and recover 3 charred letters from their campfires, then return to Magistrate Sevren in Brill.",
            "offer": (
                "Three nights ago the Crusade ambushed a supply cart on the east road. They knew which road, they knew "
                "which hour, and they knew the escort would be two Deathguards short because of the changing of the "
                "watch. That is not luck, $n. Luck doesn't keep a schedule.$B$B"
                "Someone is telling them. I don't yet know who, and I'd rather not hang the wrong neck; the town has "
                "few enough left.$B$B"
                "My scouts have seen Scarlet couriers in the hollow northeast of town, past the cemetery road. When "
                "they're cornered they throw their letters on the fire. Zealots: they'd rather burn the evidence than "
                "trust Light to protect it. Kill them before they finish the job and pull what you can from the "
                "ashes. Half a letter is still a letter."),
            "progress": "Anything from the hollow? Even a scrap with a date on it would do.",
            "done": (
                "(Sevren lays the blackened pages on his desk and smooths them flat with a careful finger.)$B$B"
                "\"...the eastern escort changes at the second bell, and the north road stands empty until the lamps "
                "are lit...\" They know when the lamps are lit. Of course they do.$B$B"
                "This wasn't written by a Crusader, $n. Look at the hand: it shakes. Whoever wrote this has been dead a "
                "long time and still remembers his letters. One of ours."),
            "objectives": [("kill", "courier", 4, ""),
                           ("credit", "ashes_credit", 3, "Charred letter recovered")],
            "return": "Return to Magistrate Sevren in Brill.",
            "items": [(858, 2)], "money": 1800, "xp": 4,
        },
        {
            "id": "eyes", "title": "Eyes Among Us", "giver": SEVREN, "prev": "letters",
            "log": "Question Innkeeper Renee, Mrs. Winters and Abigail Shiel, and look for signs of the informant by the cistern and behind the tavern. Then return to Magistrate Sevren.",
            "offer": (
                "If I start asking questions myself, the whole town will know by supper that the Magistrate is "
                "frightened. They'd be right, but there's no reason to tell them.$B$B"
                "You're new enough that people still talk to you. Go and listen. Innkeeper Renee hears everything said "
                "over a drink; Mrs. Winters and Abigail Shiel keep the market and see who comes and goes. Ask them who "
                "keeps odd hours, who has been asking after the watch.$B$B"
                "And look around while you're at it. Letters have to pass from hand to hand somewhere. The cistern "
                "and the back of the tavern are both quiet after dark, and both on a patrol's blind side. If I were "
                "selling my town, that is where I'd do it."),
            "progress": "Well? I've been staring at that letter so long I could forge it.",
            "done": (
                "A chalk mark behind the tavern and a hollow under the cistern's stones, and three good women who all "
                "mention, without being asked, the man who's always about when the patrols change.$B$B"
                "(Sevren closes his eyes.)$B$B"
                "No. Don't say the name yet. I want to be certain before I let myself think it."),
            "objectives": [("credit", "renee_credit", 1, "Innkeeper Renee questioned"),
                           ("credit", "winters_credit", 1, "Mrs. Winters questioned"),
                           ("credit", "abigail_credit", 1, "Abigail Shiel questioned"),
                           ("credit", "signs_credit", 2, "Signs of the informant found")],
            "return": "Return to Magistrate Sevren in Brill.",
            "money": 2000, "xp": 4,
        },
        {
            "id": "informant", "title": "The Scarlet Informant", "giver": SEVREN, "prev": "eyes",
            "log": "Search the street lamps of Brill for anything left at their feet, and question the Captured Scarlet Zealot in the tavern's cellar. Then return to Magistrate Sevren.",
            "offer": (
                "Everything you found keeps time with the lamps. The letter names the hour the lamps are lit. The chalk "
                "and the cistern are on the lamplighter's round. Every word of it points at Lowell Marsh, and I've known "
                "Lowell since before the Dark Lady gave us back our wills. He lit the lamps in this town when it had "
                "living people in it.$B$B"
                "So I want proof, not a pattern. Look at the lamps along the street. A man who leaves word for "
                "someone leaves it where his hands already are.$B$B"
                "Then go down to the cellar under the Gallows' End. We have a zealot down there who thinks his silence "
                "is a prayer. Show him the letters. Even a zealot's face says something."),
            "progress": "The lamps, $n, and the zealot. Then we'll know.",
            "done": (
                "Three folded notes, one at the foot of each lamp, each with nothing on it but an hour, and a zealot "
                "who laughed and called him \"our lamb.\"$B$B"
                "(Sevren is quiet for a long moment.)$B$B"
                "Lowell Marsh. A lamplighter. He walks every street with the night watch; they talk to him about their "
                "hours because he's harmless. He has been harmless for forty years.$B$B"
                "I could have the Deathguard drag him in tonight. I find I don't want to. Not yet."),
            "objectives": [("credit", "lamps_credit", 3, "Street lamp searched"),
                           ("credit", "zealot_credit", 1, "Captured Scarlet Zealot questioned")],
            "return": "Return to Magistrate Sevren in Brill.",
            "items": [(2455, 2)], "money": 2000, "xp": 4,
        },
        {
            "id": "promise", "title": "The Promise of Life", "giver": SEVREN, "ender": "wendel", "prev": "informant",
            "log": "Confront Lowell Marsh, the lamplighter, by the cistern in Brill.",
            "offer": (
                "Go to him, $n. Not with guards; he'd only lie to guards, and he'd lie badly, and someone would lose "
                "patience. Go yourself. He's by the cistern most evenings, cleaning his glass.$B$B"
                "I want to know why. Forty years he served this town, and the Crusade burns people like him by the "
                "cartload. Whatever they offered him, it must have been worth more to him than his neighbors.$B$B"
                "Find out what it was. Then we'll decide what Brill does about it. Or what you do, if I can't bring "
                "myself to."),
            "done": (
                "(Lowell Marsh sets down his lamp-pole very slowly. For a moment he looks as if he means to run; then "
                "his shoulders drop.)$B$B"
                "So the Magistrate knows. Good. I'm tired of carrying it.$B$B"
                "His name is Brother Anselm. He found me on the north road last spring, alone with my ladder, and he "
                "didn't burn me. He talked to me. He said the Light can call a soul back into living flesh, that it's "
                "been done, that the Scourge's curse is only a sickness and sicknesses are cured. He said he'd pray "
                "over me himself. He said I'd feel the sun again.$B$B"
                "All I had to do was tell him when the lamps were lit.$B$B"
                "(He looks down at his grey hands.)$B$B"
                "Do you know what it is to remember warmth, $g sir:madam;? I'd have told him anything."),
            "return": "Speak with Lowell Marsh in Brill.",
            "money": 1000, "xp": 2,
        },
        {
            "id": "fate", "title": "A Betrayer's Fate", "giver": "wendel", "ender": SEVREN, "prev": "promise",
            "log": "Decide Lowell Marsh's fate: expose him to Magistrate Sevren, persuade him to abandon his arrangement, or help him escape Brill. Then return to Magistrate Sevren.",
            "offer": (
                "Two of our Deathguards died on that east road. I know their names. Morgan and Pell. I lit the lamp "
                "they walked under on the way out of town.$B$B"
                "I didn't think... no. I did think. I just thought about the sun more.$B$B"
                "Brother Anselm writes that it's nearly ready, the rite. A few more letters. I don't even know anymore "
                "if I believe him. A man who wants you to betray your town for a miracle would say the miracle was "
                "nearly ready, wouldn't he?$B$B"
                "(He laughs, a dry sound.)$B$B"
                "Sevren sent you, so it's yours to say. Hand me to him, and I'll go quietly. Tell me to burn Anselm's "
                "letters, and I'll try, though I don't know if I can. Or look the other way while I take the west road "
                "tonight, and I'll never trouble Brill again. Whatever you choose, $n, I won't blame you for it. I've "
                "used up all my blaming on myself."),
            "progress": "(Lowell waits, turning his lamp-pole in his hands.)",
            "done": (
                "It's done, then.$B$B"
                "(Sevren doesn't ask for details, and seems careful not to look as if he wants them.)$B$B"
                "The Crusade will find our patrols harder to read now, whatever became of the man who read them. I'll "
                "change the watch hours tonight regardless; I'd be a fool not to.$B$B"
                "You did a hard, quiet thing for this town, $n. Those are the ones nobody thanks you for, so let me "
                "be the one who does. Thank you."),
            "objectives": [("credit", "fate_credit", 1, "Lowell Marsh's fate decided")],
            "return": "Return to Magistrate Sevren in Brill.",
            "items": [(4496, 1)], "money": 3500, "xp": 5,
        },
    ],
    "markers": ["exposed", "spared", "escaped"],
    "npcs": [
        {"id": "wendel", "name": "Lowell Marsh", "subname": "Lamplighter", "display": 2611, "level": 10,
         "flags": ["gossip", "quest"], "spawns": [[0, 2236.0, 286.0, 35.17, 0.30]], "phase": "informant"},
        {"id": "courier", "name": "Scarlet Courier", "display": [2467, 2478], "hostile": True, "faction": 67,
         "level": (9, 10), "type": 7, "unit_class": 1, "health": 1, "damage": 1, "gold": 40, "wander": 4,
         "spawns": [[0, 2480.0, 150.0, 29.02, 1.0], [0, 2495.0, 165.0, 29.03, 3.5],
                    [0, 2505.0, 150.0, 28.21, 2.2], [0, 2475.0, 170.0, 29.92, 5.0]]},
    ],
    "credits": [
        {"id": "ashes_credit", "name": "Charred letter recovered"},
        {"id": "renee_credit", "name": "Innkeeper Renee questioned"},
        {"id": "winters_credit", "name": "Mrs. Winters questioned"},
        {"id": "abigail_credit", "name": "Abigail Shiel questioned"},
        {"id": "signs_credit", "name": "Signs of the informant found"},
        {"id": "lamps_credit", "name": "Street lamp searched"},
        {"id": "zealot_credit", "name": "Captured Scarlet Zealot questioned"},
        {"id": "fate_credit", "name": "Lowell Marsh's fate decided"},
    ],
    "objects": [
        {"id": "embers", "name": "Smouldering Fire", "display": 397, "quest_only": True,
         "spawns": [[0, 2485.0, 158.0, 29.07, 0.0], [0, 2500.0, 175.0, 30.11, 1.2], [0, 2470.0, 162.0, 30.09, 2.4]],
         "use": [
             {"cond": ["I:letters"], "quest": "letters", "credit": "ashes_credit"},
         ]},
        {"id": "wellstone", "name": "Loose Stones", "display": 134, "scale": 0.4, "quest_only": True,
         "spawns": [[0, 2292.3, 314.3, 35.45, 0.0]],
         "use": [
             {"cond": ["I:eyes"], "quest": "eyes", "credit": "signs_credit"},
         ]},
        {"id": "chalkcrate", "name": "Chalk-Marked Crate", "quest_only": True, "display": 275, "scale": 0.8,
         "spawns": [[0, 2281.0, 257.0, 34.47, 1.9]],
         "use": [
             {"cond": ["I:eyes"], "quest": "eyes", "credit": "signs_credit"},
         ]},
        # (at the feet of Brill's own street lamps)
        {"id": "lamp", "name": "Folded Note", "display": 220, "quest_only": True,
         "spawns": [[0, 2270.5, 327.3, 34.6, 0.5], [0, 2225.4, 252.4, 33.71, 2.0], [0, 2280.6, 434.3, 34.15, 4.0]],
         "use": [
             {"cond": ["I:informant"], "quest": "informant", "credit": "lamps_credit"},
         ]},
    ],
    "gossip": [
        # Lowell: before, during, and after.
        {"npc": "wendel", "kind": "greet", "cond": ["M:spared", "DAY:4"], "texts": [
            "I went to Apothecary Johaan yesterday and asked him straight out: can it be undone? He laughed at "
            "me, then he stopped laughing and gave me a very long answer that meant no. It helped, oddly. A "
            "door shut properly is easier than one left ajar.",
            "Deathguard Cyrus asked after my knees today. My knees! I've no feeling in them since the plague. "
            "But he asked. I think that's what Anselm was really selling me, $n. Someone who'd ask.",
            "A letter came from Brother Anselm. I put it in the lamp by the inn and lit it with the rest. "
            "Best light that lamp's ever given."]},
        {"npc": "wendel", "kind": "greet", "cond": ["M:spared"],
         "text": "Evening, $n. The lamps are lit on time and no one knows when but the watch. (He polishes a lamp-glass, "
                 "and doesn't quite meet your eyes.) I'm trying. That's all I can say. I'm trying."},
        {"npc": "wendel", "kind": "greet", "cond": ["A:fate"],
         "text": "(Lowell's hands are shaking around the lamp-pole.) Have you decided? I'd rather know."},
        {"npc": "wendel", "kind": "greet", "cond": ["T:informant"],
         "text": "Evening. (Lowell's eyes flick to you and away again.) The lamps won't light themselves, $g sir:madam;."},
        {"npc": "wendel", "kind": "greet", "texts": [
            "Evening, $g sir:madam;. Mind the ladder. I've a dozen lamps to light before the watch changes, and "
            "the north road ones are always last.",
            "Forty years I've lit these lamps. Kings, plague, and now the Dark Lady, and the lamps "
            "never cared which. There's a comfort in that, isn't there?",
            "The Deathguard like a bit of company on the night round. They tell me everything. Who's tired, "
            "who's sore, who's late. I just listen. Someone ought to."]},
        {"npc": "wendel", "kind": "option", "cond": ["I:fate"],
         "text": "Magistrate Sevren will hear all of it. You'll answer to him.",
         "action": "choice", "quest": "fate", "credit": "fate_credit", "marker": "exposed", "emote": 2,
         "reply": "(Lowell nods, as if he had expected nothing else.) Yes. That's fair. Will you walk with me to the town "
                  "hall? I'd rather not go with the Deathguard's hands on my arms. They were my friends, you see.$B$B"
                  "(He sets his lamp-pole against the well, very carefully, as though someone else might need it.)"},
        {"npc": "wendel", "kind": "option", "cond": ["I:fate"],
         "text": "Burn Anselm's letters and stay. Be what you are, and be it here.",
         "action": "choice", "quest": "fate", "credit": "fate_credit", "marker": "spared", "emote": 18,
         "reply": "Stay. As this. (He looks at his hands for a long time.) Brother Anselm called me a lamb lost in the "
                  "dark. You're the first to say the dark's a place a person can live in.$B$B"
                  "I'll burn them. Tonight. All of them. And if he writes again, I'll burn that too. If you see me "
                  "wavering, $n, you have my leave to tell Sevren everything."},
        {"npc": "wendel", "kind": "option", "cond": ["I:fate"],
         "text": "Take the west road tonight. Don't come back to Brill.",
         "action": "choice", "quest": "fate", "credit": "fate_credit", "marker": "escaped", "emote": 2,
         "reply": "You'd... (His voice catches.) I won't go to Anselm. I swear it. I'll go somewhere the Crusade has "
                  "never heard of and neither has the Dark Lady, if there's such a place left.$B$B"
                  "(He takes nothing but his coat.) Light the north road lamp for me, would you? Someone ought to. "
                  "Goodbye, $n."},

        # Questioning the town (Eyes Among Us).
        {"npc": RENEE, "kind": "option", "cond": ["I:eyes"], "text": "Who in Brill keeps odd hours, Renee?",
         "action": "credit", "quest": "eyes", "credit": "renee_credit",
         "reply": "Odd hours? Love, everyone here's dead; there are no other kind. (She lowers her voice.) But since you ask: "
                  "the only one who comes in after the second bell is old Lowell, the lamplighter. Takes a seat by the "
                  "back door, never drinks, leaves when the watch changes. I always thought he was lonely."},
        {"npc": WINTERS, "kind": "option", "cond": ["I:eyes"], "text": "Has anyone been asking about the Deathguard's rounds?",
         "action": "credit", "quest": "eyes", "credit": "winters_credit",
         "reply": "Asking? No one needs to ask. Every child in the old Brill could tell you when the watch changed by when the "
                  "lamps were lit. (She frowns.) Strange thing, though. Lowell Marsh bought a whole quire of paper from "
                  "me last month. Lamplighters don't write much."},
        {"npc": ABIGAIL, "kind": "option", "cond": ["I:eyes"], "text": "Seen anyone by the cistern after dark?",
         "action": "credit", "quest": "eyes", "credit": "abigail_credit",
         "reply": "The well? Only the lamplighter, and he's always there; he fills his oil pot from the cistern beside it. "
                  "(She pauses.) Though he did take an awfully long time over it last week. Down on his knees. I took "
                  "it for prayer. You'd be surprised how many of us still do."},

        # The prisoner (The Scarlet Informant), and him after.
        {"npc": ZEALOT, "kind": "option", "cond": ["I:informant"], "text": "(Show him the charred letters.)",
         "action": "credit", "quest": "informant", "credit": "zealot_credit",
         "reply": "(The zealot glances at the letters and his cracked lips twitch into a smile.) Ah. Our little lamb's "
                  "handwriting. He'll be made whole, you know, when the Light comes to cleanse this place. Brother "
                  "Anselm promised him. (He catches himself, too late, and turns his face to the wall.)"},
        {"npc": ZEALOT, "kind": "greet", "cond": ["M:exposed"],
         "text": "(The zealot is praying under his breath. When he sees you, he stops.) Anselm will hear what you did to "
                 "his lamb. The Light keeps an account, abomination."},

        # Sevren after.
        {"npc": SEVREN, "kind": "greet", "cond": ["M:exposed"],
         "text": "The Royal Apothecary Society took Lowell Marsh to the Undercity this morning. I asked what would become of "
                 "him and was told it was a matter for the Dark Lady's agents. I have decided to be satisfied with that "
                 "answer. Brill's patrols are its own again, $n. That is what matters. That is what I keep telling myself."},
        {"npc": SEVREN, "kind": "greet", "cond": ["M:escaped"],
         "text": "Lowell Marsh is gone. He left his ladder against the inn wall and walked off in the night, and the north "
                 "road lamp was burning when the watch found it, though no one remembers lighting it. (Sevren studies you "
                 "a moment.) I don't suppose you'd know anything about that. No. Of course you wouldn't."},
        {"npc": SEVREN, "kind": "greet", "cond": ["M:spared"],
         "text": "The letters have stopped. Whoever it was lost his nerve, or his priest. (Sevren glances out of the window, "
                 "toward the lamplighter working in the square.) I have decided not to wonder why the lamps have been "
                 "lit so very carefully lately. A magistrate must choose what to wonder about."},

        # The inn: letters from the road.
        {"npc": RENEE, "kind": "greet", "cond": ["M:escaped", "DAY:3"], "texts": [
            "A letter came for you, love. No name on the outside, just yours. (It reads:) \"The ferry at the Sepulcher "
            "takes anyone who pays. I mend nets now on the Silverpine coast. The fishermen don't ask what I am; the "
            "fog makes us all the same color. I think of the north road lamp. W.\"",
            "Another letter for you. (It reads:) \"I've heard nothing from Brother Anselm and I've stopped listening for "
            "him. A worgen came down to the shore last night and we looked at each other a long while and then it "
            "went away. There's a lesson in that, I think. Not a comfortable one. W.\"",
            "One more of these came for you. Same shaky hand. (It reads:) \"A Forsaken captain is taking volunteers for "
            "Northrend. They say no one there asks where you came from, only whether you'll stand. I'm going to try "
            "standing. Light a lamp for me, if Brill's found anyone to light them. W.\""]},

        # The Deathguard (their disposition by his fate).
        {"npc": BURGESS, "kind": "greet", "cond": ["M:exposed"],
         "text": "You're the one who found the lamplighter out. (Burgess straightens.) Two of mine died on that east road. "
                 "Pell was a friend. If you ever need a blade at your back in Brill, $n, you'll have mine."},
        {"npc": BURGESS, "kind": "greet", "cond": ["M:escaped"],
         "text": "Lamplighter vanished the same night you were seen talking with him by the well. (Burgess's eyes narrow.) "
                 "I'm sure that's nothing, $g sir:madam;. Move along."},
        {"npc": CYRUS, "kind": "greet", "cond": ["M:spared"],
         "text": "Lowell's been walking the night round with me again. Asks after my knees. (Cyrus snorts.) My knees! But "
                 "it's company. Odd: he never asks about the watch hours anymore. Used to be all he talked about."},
        {"npc": CYRUS, "kind": "greet", "cond": ["M:exposed"],
         "text": "Lowell Marsh. I told him about my hours myself, every night for a year. (Cyrus stares at nothing.) I "
                 "thought he was listening because he cared."},
        {"npc": MORRIS, "kind": "greet", "cond": ["M:escaped"],
         "text": "Nobody's lit the lamps since Marsh left. The Executor says he'll find someone. Meanwhile we walk in the "
                 "dark. Funny how you don't notice a man until he's gone."},
        {"npc": MORRIS, "kind": "greet", "cond": ["R:fate"],
         "text": "Patrol hours changed overnight on the Magistrate's word, and the Crusade hasn't touched a cart since. "
                 "Someone did good work, $n. I hear it was you."},
        {"npc": GAVIN, "kind": "greet", "cond": ["M:exposed"],
         "text": "We kept the lamplighter down here one night, before the apothecaries came for him. He sat by the "
                 "zealots' cell and didn't say a word to them. They prayed for him the whole night. Worst sound I ever "
                 "heard."},
        {"npc": ROYANN, "kind": "greet", "cond": ["R:fate"],
         "text": "The zealot's stopped gloating since you came down here with those letters. Whatever you did up there, "
                 "keep doing it."},
    ],
    "phases": {
        # Lowell Marsh is in Brill unless this player had him taken away or let him go.
        "informant": [["!M:exposed", "!M:escaped"]],
    },
}
