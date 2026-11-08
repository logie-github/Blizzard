# SPDX-License-Identifier: GPL-3.0-or-later
"""Something in the Water: five quests from Maudie Fenwick, Brill's laundress, whose cistern water has turned foul
even by Forsaken standards. Junior Apothecary Holland finds a parasite in the samples; its runoff leads west to
the dry drainage channel under the covered bridge on the Deathknell road, where a broodmother has nested; a
split Royal Apothecary Society cask in the nest (a failed growth tincture, "disposed of by dilution") fed it.
Brill has no well: the town draws from a cistern by the town hall, a great barrel fed from the roofs (a model
the zone uses itself: Innbarrel), everyone's, drawn from once it's cleansed; Maudie's
washing comes back beside it (the "restored" phase). Acknowledges the apprentice's line where it fits."""

# Brill's square (open ground, the game's terrain heights), by the hanging lanterns.
WELL_AT = [0, 2290.0, 312.0, 35.3, 0.0]
MAUDIE_AT = [0, 2292.6, 314.6, 35.5, 3.93]
# The dry channel under the covered bridge west of Brill (its bed at 24.75), where the nest is.
UNDER_BRIDGE = 24.8

LINE = {
    "title": "Something in the Water",
    "quests": [
        {
            "id": "water", "title": "Water Unfit for the Dead", "giver": "maudie", "ender": "maudie",
            "log": "Draw a sample from Brill's cistern and three from the stream north-east of town, at Maudie Fenwick's old buckets, then return to Maudie in Brill.",
            "offer": (
                "You'll want to stand back from that cistern, dear. Further. Further than that.$B$B"
                "Maudie Fenwick. I do the washing for the inn: sheets, tabards, whatever the Deathguard bleed on, and the "
                "bedding of every orc and troll who stops in Brill on the way to somewhere better. The living sweat, you know. "
                "Terribly. Somebody has to wash it out.$B$B"
                "For a fortnight the water's come up stinking. Not the honest stink of a town full of corpses; I'm used to "
                "that, I am that. This is sour and green, and it clings to the cloth. Renee's had complaints.$B$B"
                "Fill these jars for me. One from the cistern, and three from the stream north-east of town, where I drew water "
                "before the cistern was built. My old buckets are still on the bank. If the stream's gone bad as well, then it isn't "
                "just my cistern, is it?"),
            "progress": "Four jars. And don't drink from any of them, whatever you are.",
            "done": (
                "Look at that. Look at it moving.$B$B"
                "I've washed blood, bile and the inside of a ghoul's mouth out of good linen and never once felt queasy. But "
                "that... that turns what's left of my stomach.$B$B"
                "It's in the stream too. So it isn't my cistern. It's under all of us."),
            "objectives": [("credit", "sample_credit", 4, "Water samples drawn")],
            "return": "Return to Maudie Fenwick by the cistern in Brill.",
            "money": 1500, "xp": 3,
        },
        {
            "id": "growth", "title": "A Peculiar Growth", "giver": "maudie", "ender": 10665, "prev": "water",
            "log": "Bring Maudie Fenwick's water samples to Junior Apothecary Holland in Brill.",
            "offer": (
                "I'm a washerwoman, not an alchemist. I know when water's wrong; I couldn't tell you why.$B$B"
                "Take the jars to Junior Apothecary Holland, at the north end of town. Not Johaan. Johaan would want to keep "
                "them. Holland's young, by our reckoning, and still curious, and he doesn't charge for curiosity.$B$B"
                "Tell him Maudie sent you. He'll pretend he doesn't know who I am. He sends me his robes every week and "
                "pretends they wash themselves."),
            "done": (
                "Maudie sent you? I don't know any Maudie.$B$B"
                "(Holland uncorks the first jar, sniffs, and stops pretending.)$B$B"
                "Oh, that's lovely. Look here, under the glass. These threads aren't weed. They're larvae: a parasite, a fluke of "
                "some kind, feeding on whatever's dissolved in the water. On us, in a manner of speaking. The runoff from a town "
                "of the dead is very rich.$B$B"
                "They don't breed in open water. Something is laying them. Somewhere close, and dark, and wet."),
            "return": "Speak with Junior Apothecary Holland in Brill.",
            "money": 1000, "xp": 2,
        },
        {
            "id": "source", "title": "The Source of the Rot", "giver": 10665, "ender": 10665, "prev": "growth",
            "log": "Follow the fouled runoff west of Brill: examine 3 patches of gray bloom and find where the old drainage channel runs under the covered bridge, then return to Junior Apothecary Holland.",
            "offer": (
                "Water runs downhill, and so does everything in it. Brill's ground water drains west, under the hill, toward the "
                "channel the Lordaeron engineers cut to keep the fields from flooding. It's been dry since the plague. Nobody "
                "tends the sluices now.$B$B"
                "Follow the runoff. Where the larvae are thick, the ground will show it: a gray bloom, like mold on bread, wherever "
                "the water seeps out. Find three patches, then find where it all comes from. My guess is the channel itself, "
                "where it passes under the covered bridge on the Deathknell road.$B$B"
                "Don't touch the bloom with bare skin. Or with skin of any kind, really."),
            "progress": "Anything? The jars on my bench have started to cloud. That's new.",
            "done": (
                "Under the bridge. Of course. Dark and damp, and nobody's walked that channel in years but the Rotting Dead, "
                "and they're not much for reporting things.$B$B"
                "Warm, you said. And the smell of eggs.$B$B"
                "(Holland goes rather pale, which takes some doing.)$B$B"
                "That's a nest, $n. And whatever's laying in it will be considerably larger than a thread."),
            "objectives": [("credit", "bloom_credit", 3, "Gray bloom examined"),
                           ("credit", "culvert_credit", 1, "The culvert under the bridge found")],
            "return": "Return to Junior Apothecary Holland in Brill.",
            "money": 2500, "xp": 4,
        },
        {
            "id": "nest", "title": "A Nest Below", "giver": 10665, "ender": 10665, "prev": "source",
            "log": "Kill the Culvert Broodmother under the covered bridge west of Brill and burst 4 of its egg sacs, then return to Junior Apothecary Holland.",
            "offer": (
                "I'd send for the Deathguard, but Executor Zygand would want it in writing, and then he'd want to know why the "
                "Society didn't notice sooner, and then I'd be writing for a month.$B$B"
                "You go. Get under that bridge and kill whatever is laying those eggs. Burst the sacs too, every one you find. If "
                "even a few hatch, the whole thing starts over in a season.$B$B"
                "I've no idea what it will be. A broodmother of some kind. Something the plague made, or something the plague "
                "made worse. Either way, it's grown fat on our water, and I would like it to stop."),
            "progress": "Is it dead? And the eggs? Both matter. The second rather more.",
            "done": (
                "Dead. And the sacs. Good. Good.$B$B"
                "(He sets down a jar he has been holding very tightly.)$B$B"
                "I've watched the samples all afternoon. The threads have stopped moving. Not slowly: all at once, the moment it "
                "died, as if something had been pulling every one of their strings.$B$B"
                "There's still what's left in the water. And something about how fast it grew is bothering me."),
            "objectives": [("kill", "broodmother", 1, ""),
                           ("credit", "sac_credit", 4, "Egg sacs burst")],
            "return": "Return to Junior Apothecary Holland in Brill.",
            "money": 4000, "xp": 5, "items": [(858, 3)],
        },
        {
            "id": "clear", "title": "Clear Waters, Dark Memories", "giver": 10665, "ender": "maudie", "prev": "nest",
            "log": "Search the broodmother's nest under the covered bridge, cleanse Brill's cistern with Holland's quicklime, then speak with Maudie Fenwick in Brill.",
            "offer": (
                "A broodmother that size doesn't grow on runoff alone, not in a few years. Something fed it. Something rich.$B$B"
                "Go back to the nest and search it, properly, now that nothing in it is trying to eat you. If anything was dumped "
                "there, a cask, a crate, anything with a label, I want to know what was in it.$B$B"
                "And take this.$B$B"
                "(He hands you a heavy sack of gray powder.)$B$B"
                "Quicklime and bitterroot ash. Tip it into Brill's cistern; it'll kill whatever larvae are left and won't harm anyone "
                "who's already dead. The living may want to boil their water for a week. Then tell Maudie she can have her cistern "
                "back."),
            "progress": "Is it done? Can I fill my tubs?",
            "done": (
                "It's clear. Look, $n, it's clear! I can see the bottom of the bucket!$B$B"
                "(She draws another, just to see it again.)$B$B"
                "And the cask, you say. Society work. Somebody up the road poured their mistake into the ground and let it seep "
                "under all of us, and never once came to ask why the water tasted wrong.$B$B"
                "Well. I won't say anything. Who would I say it to? But I'll be washing the Society's robes in this water from now "
                "on, and I'll know. Every time."),
            "objectives": [("credit", "cask_credit", 1, "The nest searched"),
                           ("credit", "cleanse_credit", 1, "Brill's cistern cleansed")],
            "return": "Return to Maudie Fenwick by the cistern in Brill.",
            "money": 5000, "xp": 5, "items": [(2459, 1), (858, 2)],
        },
    ],
    "npcs": [
        {"id": "maudie", "name": "Maudie Fenwick", "subname": "Laundress", "display": 4004, "level": 10,
         "spawns": [MAUDIE_AT]},
        # Under the bridge: the broodmother and the larvae she's hatched (soloable at 10 to 14).
        {"id": "broodmother", "name": "Culvert Broodmother", "display": 12336, "scale": 0.8, "hostile": True, "faction": 14,
         "level": 12, "type": 1, "health": 3.0, "damage": 1.3, "gold": 300, "respawn": 90,
         "spells": [(744, (3000, 5000), (10000, 14000)), (3427, (6000, 8000), (15000, 18000))],
         "spawns": [[0, 2212.0, 634.0, UNDER_BRIDGE, 2.4]]},
        {"id": "larva", "name": "Broodmother Larva", "display": 15436, "hostile": True, "faction": 14,
         "level": (8, 9), "type": 1, "health": 0.6, "damage": 0.6, "wander": 3, "respawn": 60,
         "spawns": [[0, 2224.0, 636.0, UNDER_BRIDGE, 3.0], [0, 2212.0, 624.0, UNDER_BRIDGE, 1.0],
                    [0, 2205.0, 636.0, UNDER_BRIDGE, 5.0]]},
    ],
    "credits": [
        {"id": "sample_credit", "name": "Water samples drawn"},
        {"id": "bloom_credit", "name": "Gray bloom examined"},
        {"id": "culvert_credit", "name": "The culvert under the bridge found"},
        {"id": "sac_credit", "name": "Egg sacs burst"},
        {"id": "cask_credit", "name": "The nest searched"},
        {"id": "cleanse_credit", "name": "Brill's cistern cleansed"},
    ],
    "objects": [
        # Brill's well, in the square (everyone's): fouled, then sampled, cleansed, and drawn from.
        {"id": "well", "name": "Brill Cistern", "display": 6036, "scale": 1.4, "spawns": [WELL_AT],
         "use": [{"cond": ["I:water"], "quest": "water", "credit": "sample_credit"},
                 {"cond": ["I:clear"], "quest": "clear", "credit": "cleanse_credit"}]},
        # Maudie's old buckets on the stream bank north-east of town (the shore, above the water's 21.2).
        {"id": "bucket", "name": "Maudie's Old Bucket", "quest_only": True, "display": 239,
         "spawns": [[0, 2386.0, 95.0, 21.6, 1.0], [0, 2418.0, 103.0, 21.5, 2.0], [0, 2436.0, 106.0, 21.9, 4.0]],
         "use": [{"cond": ["I:water"], "quest": "water", "credit": "sample_credit"}]},
        # The runoff, west of town down to the channel.
        {"id": "bloom", "name": "Gray Bloom", "quest_only": True, "display": 389,
         "spawns": [[0, 2262.0, 420.0, 35.0, 0.0], [0, 2255.0, 480.0, 33.9, 1.5], [0, 2250.0, 560.0, 33.6, 3.0]],
         "use": [{"cond": ["I:source"], "quest": "source", "credit": "bloom_credit"}]},
        {"id": "culvert", "name": "Collapsed Culvert", "quest_only": True, "display": 134, "scale": 0.6,
         "spawns": [[0, 2228.0, 640.0, 24.75, 1.6]],
         "use": [{"cond": ["I:source"], "quest": "source", "credit": "culvert_credit"}]},
        # The nest: the sacs, and what fed it.
        {"id": "sac", "name": "Broodmother Egg Sac", "quest_only": True, "display": 364,
         "spawns": [[0, 2208.0, 630.0, 24.75, 0.0], [0, 2216.0, 641.0, 24.75, 1.0], [0, 2203.0, 641.0, 24.8, 2.0],
                    [0, 2219.0, 631.0, 24.75, 3.0], [0, 2210.0, 638.0, 24.75, 4.0]],
         "use": [{"cond": ["I:nest"], "quest": "nest", "credit": "sac_credit"}]},
        {"id": "cask", "name": "Split Cask", "quest_only": True, "display": 9,
         "spawns": [[0, 2210.0, 644.0, 24.75, 0.7]],
         "use": [{"cond": ["I:clear"], "quest": "clear", "credit": "cask_credit"}]},
        # The cistern's back in use (this player's Brill): Maudie's washing beside it.
        {"id": "washtub", "name": "Maudie's Washtubs", "display": 7485, "phase": "restored",
         "spawns": [[0, 2294.2, 312.2, 35.5, 2.0]]},
        {"id": "wash_bucket", "name": "Bucket of Clean Water", "display": 7484, "phase": "restored",
         "spawns": [[0, 2291.8, 309.6, 35.3, 0.5]]},
        {"id": "basket", "name": "Laundry Basket", "display": 7494, "phase": "restored",
         "spawns": [[0, 2295.0, 315.6, 35.8, 4.0]]},
    ],
    "gossip": [
        # Maudie.
        {"npc": "maudie", "kind": "greet", "cond": ["R:clear", "M:apprentice.supervised"],
         "text": "That Crane lad comes by every morning for a bucket now. Says the Apothecary insists on clean water for his work. Nice "
                 "manners. Short a few fingers. Aren't we all."},
        {"npc": "maudie", "kind": "greet", "cond": ["R:clear", "M:apprentice.destroyed"],
         "text": "Johaan's apprentice scrubs the laboratory floors with my water now. He asked me once whether I thought he'd done right. I "
                 "told him I wash other people's stains for a living, and I don't ask how they got there."},
        {"npc": "maudie", "kind": "greet", "cond": ["R:clear", "M:apprentice.surrendered"],
         "text": "Society couriers through the square twice this week, carrying crates up from Johaan's. They didn't stop for water. I "
                 "didn't offer."},
        {"npc": "maudie", "kind": "greet", "cond": ["R:clear"],
         "texts": ["Clean water, clean linen, and Renee's paying me again. A body can't ask for more. Well, a living one could. I've "
                   "stopped asking.",
                   "Draw yourself a bucket, if you like. It's the best water in Tirisfal now. That isn't saying much, but I'll say it.",
                   "Hear that? The windlass. I used to hate the sound. Now I sing along. Badly. I was always bad."]},
        {"npc": "maudie", "kind": "greet", "cond": ["A:clear"],
         "text": "Holland's powder? Go on, then. Tip it in. I'll hold my breath. Habit."},
        {"npc": "maudie", "kind": "greet", "cond": ["T:growth", "!R:clear"],
         "text": "I've been washing in rainwater from the barrels. Do you know how long it takes to fill a tub from a barrel? Neither did "
                 "I. Now I know."},
        {"npc": "maudie", "kind": "greet",
         "texts": ["Don't drink from that well. Don't even look into it too long. It looks back.",
                   "Maudie Fenwick, laundress. If it's stained, I've washed it. If it's cursed, I've washed it twice."]},
        # Holland (his own menu keeps its own; these are the line's words and one question).
        {"npc": 10665, "kind": "option", "cond": ["A:clear", "T:apprentice.secret"],
         "text": "Could that cask have been Wendell Crane's?", "action": "say",
         "reply": "Crane's? No. Batch nine is older than his apprenticeship; the Society stopped numbering batches that way the year we "
                  "took Brill back. I know what's been said about him. Whatever else he is, he's careful. More careful than whoever did this."},
        {"npc": 10665, "kind": "greet", "cond": ["R:clear", "T:apprentice.secret"],
         "text": "I asked about batch nine in the Undercity. Nobody remembered it. Everybody remembered to tell me not to ask again. Crane "
                 "says that's how the Society says thank you."},
        {"npc": 10665, "kind": "greet", "cond": ["R:clear"],
         "texts": ["The samples from the cistern are clean. I've kept one of the old ones in a sealed jar on my shelf. For science. And to "
                   "remind me to look at the water now and then.",
                   "Maudie says the robes come back whiter now. I've told her robes aren't meant to be white. She ignored me."]},
        {"npc": 10665, "kind": "greet", "cond": ["A:nest"],
         "text": "Under the covered bridge, west on the Deathknell road. Burst the sacs. All of them, if you can."},
        # Carolai Anise on it (her menu is src/BrillHome.cpp's).
        {"npc": 2132, "kind": "option", "cond": ["R:clear"], "text": "(Ask her about Maudie's well.)", "action": "say",
         "reply": "Maudie's cistern is clean again. I've started washing my glassware in it. I can tell the difference. I'm not sure I like that I can tell."},
    ],
    "phases": {
        "restored": [["R:clear"]],
    },
}
