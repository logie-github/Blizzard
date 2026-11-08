# SPDX-License-Identifier: GPL-3.0-or-later
"""The Stillgarden (a Community Project, opened by Brill Endures): Edda Graves, a Forsaken florist who
remembers the names of hundreds of flowers and the faces of almost none of her family, asks for a quiet
place in a town full of carts and hammering, and the Magistrate gives her Holt's Rise, the overgrown
orchard on Brill's eastern edge (and Odo, the groundskeeper who came with it). Pellen Moss, a botanist,
plants what has already learned to live in death (gravebloom from the cemetery); Holt's old drain, choked
by a toads' nest down by the stream, sours the beds until it's cleared; Willa Fen, newly risen, who can't
smell a thing, learns what the flowers are for (the town's memories, and a memorial bed with a moonpetal
lily at its heart); and the first harvest opens the garden, with the player's say in whether the herbs or
the flowers get the front beds (words and Pellen's wares follow the choice, the rewards don't).

The garden is on the rise above the sunken lane, east of the square (the ground the game's terrain gives,
37 to 39 high), kept within Brill (staged spawns 162 yards or less from 2275, 330). No building: fences,
beds, a tool shed (from the second stage), a glasshouse frame (a stable's open frame, from the fourth),
benches and the memorial bed (from the fifth), Pellen's stall (from the sixth). The old drain runs north-east
down to the stream Maudie Fenwick drew from (the cistern's line); the toads nest at its mouth, outside Brill.

Stages (every project's): 1 open, 2 to 5 as each quest is done, 6 established, 7 the house's furnishings
bought. Daily life once it's open: Edda always; Pellen at his stall; Willa among the beds by day and by the
memorial bed of an evening; Odo dozing among the plants by day and at the gate with a lantern by night;
townsfolk on the benches of an evening; Carolai Anise gathering nightshade of a morning.
"""

PI = 3.1416

# Where everything is (the game's terrain heights, map tile 0002731 and others; world x, y, z, facing).
AT = {
    # The garden's people.
    "edda": [[0, 2347.0, 213.0, 38.16, 0.68]],
    "pellen": [[0, 2351.0, 211.0, 38.27, 4.71]],
    "odo": [[0, 2364.6, 206.2, 36.72, 2.9]],
    "willa": [[0, 2344.5, 211.8, 38.13, 5.2]],
    "pellen_stall": [[0, 2362.5, 211.0, 36.91, 1.57]],
    "willa_day": [[0, 2354.0, 209.4, 38.24, 4.71]],
    "willa_evening": [[0, 2342.9, 210.8, 38.09, 2.2]],
    "odo_day": [[0, 2349.0, 209.4, 38.35, 4.6]],
    "odo_night": [[0, 2357.6, 220.4, 36.61, 1.57]],
    "carolai": [[0, 2355.0, 200.0, 38.39, 1.2]],
    "worker": [[0, 2338.5, 210.5, 37.71, 0.0], [0, 2358.5, 206.8, 38.03, 3.0]],
    "oswin": [[0, 2361.0, 209.0, 37.41, 2.6]],
    "visitor": [[0, 2336.0, 214.6, 36.97, 1.57], [0, 2343.8, 214.6, 37.82, 1.57]],
    # Holt's Rise as it was (until the garden opens).
    "weeds": [[0, 2345.0, 203.2, 38.36, 0.3], [0, 2350.0, 210.6, 38.22, 1.4], [0, 2357.5, 203.2, 38.15, 2.5],
              [0, 2360.5, 205.0, 37.63, 4.0], [0, 2336.5, 208.0, 37.67, 5.1], [0, 2352.0, 214.6, 37.93, 0.9]],
    "rubble": [[0, 2341.0, 204.6, 38.16, 0.4], [0, 2353.5, 202.8, 38.3, 2.0], [0, 2364.0, 203.0, 36.89, 3.5],
               [0, 2365.0, 209.5, 36.28, 5.0]],
    "markers": [[0, 2343.5, 209.4, 38.08, 1.57], [0, 2348.5, 209.4, 38.24, 1.57], [0, 2353.5, 209.4, 38.16, 1.57]],
    # The fence (the front, with the gate between 2354.8 and 2360.6, and the east side), the sign, the beds.
    "fence": [[0, 2342.2, 218.0, 36.62, PI], [0, 2346.4, 218.0, 37.46, PI], [0, 2350.6, 218.0, 37.62, PI],
              [0, 2360.6, 218.0, 36.35, PI], [0, 2366.8, 199.5, 36.25, 4.71], [0, 2366.8, 203.7, 36.19, 4.71],
              [0, 2366.8, 207.9, 35.95, 4.71], [0, 2366.8, 212.1, 35.53, 4.71]],
    "sign": [[0, 2361.8, 219.6, 35.9, 1.57]],
    "beds": [[0, 2343.5, 207.0, 38.17, 0.0], [0, 2348.5, 207.0, 38.3, 0.0], [0, 2353.5, 207.0, 38.23, 0.0]],
    "barrow": [[0, 2338.3, 205.6, 37.95, 1.2]],
    "shovel": [[0, 2345.6, 205.3, 38.3, 0.2], [0, 2355.6, 205.4, 38.18, 1.0]],
    "shed": [[0, 2339.8, 199.0, 38.49, 0.0]],
    "planter": [[0, 2348.5, 217.6, 37.65, 4.71], [0, 2354.0, 217.6, 37.53, 4.71]],
    "seedling_bed": [[0, 2342.6, 207.0, 38.58, 0.0], [0, 2347.6, 207.0, 38.74, 1.0], [0, 2352.6, 207.0, 38.7, 2.0]],
    "nightshade_bed": [[0, 2344.4, 207.1, 38.61, 0.5], [0, 2349.4, 206.9, 38.71, 1.5], [0, 2354.4, 207.1, 38.59, 2.5]],
    "planter_flowers": [[0, 2347.3, 216.6, 38.36, 0.0], [0, 2349.7, 216.6, 38.45, 1.0], [0, 2352.8, 216.6, 38.31, 2.0],
                        [0, 2355.2, 216.6, 38.09, 3.0]],
    "greenhouse": [[0, 2352.5, 197.6, 38.51, 0.0]],
    "sluice": [[0, 2365.0, 196.8, 36.67, 0.0]],
    "cistern": [[0, 2362.6, 199.4, 37.28, 0.3]],
    "bloom_bed": [[0, 2343.5, 206.2, 38.6, 0.7], [0, 2348.5, 207.8, 38.69, 2.2], [0, 2353.5, 206.2, 38.64, 4.0]],
    "shroom": [[0, 2346.6, 195.6, 38.96, 0.0], [0, 2358.6, 195.8, 38.02, 1.5]],
    "memorial": [[0, 2340.0, 212.6, 37.61, 0.0]],
    "benches": [[0, 2337.4, 216.0, 36.87, 1.57], [0, 2341.9, 216.0, 37.34, 1.57]],
    "plates": [[0, 2342.2, 211.5, 37.91, 0.0], [0, 2342.5, 212.6, 37.87, 0.0], [0, 2342.2, 213.7, 37.7, 0.0]],
    "mem_flowers": [[0, 2339.3, 211.8, 38.19, 0.3], [0, 2340.8, 211.9, 38.36, 1.3], [0, 2339.5, 213.5, 38.03, 2.3]],
    "lily": [[0, 2340.1, 212.6, 38.37, 0.0]],
    "stall": [[0, 2362.5, 213.2, 36.55, 1.57]],
    "herbs_peace": [[0, 2348.0, 197.0, 38.77, 0.0]],
    "herbs_silver": [[0, 2352.5, 197.0, 38.54, 0.0]],
    "herbs_grave": [[0, 2357.0, 197.0, 38.19, 0.0]],
    "sacks": [[0, 2364.9, 213.0, 35.94, 1.2]],
    "kelp": [[0, 2360.3, 213.7, 36.98, 4.0]],
    "flowerbasket": [[0, 2362.5, 213.6, 37.5, 1.57]],
    "lanterns": [[0, 2354.4, 218.6, 37.32, 0.0], [0, 2361.0, 218.6, 36.18, 0.0]],
    "pots": [[0, 2357.6, 216.4, 37.21, 0.0], [0, 2343.4, 201.4, 38.43, 0.0]],
    "pot_flowers": [[0, 2357.6, 216.4, 37.96, 0.0], [0, 2343.4, 201.4, 39.18, 0.0]],
    "night_lantern": [[0, 2358.6, 220.6, 36.31, 0.0]],
    # Brill's cemetery: gravebloom between the stones, the plague graves at its north end.
    "seedlings": [[0, 2334.0, 339.5, 35.39, 0.5], [0, 2339.5, 350.0, 35.81, 1.5], [0, 2398.0, 380.0, 34.12, 2.5],
                  [0, 2381.5, 368.5, 37.61, 3.5], [0, 2420.5, 372.0, 34.55, 4.5], [0, 2421.0, 392.0, 36.47, 5.5]],
    "graves": [[0, 2414.0, 386.0, 35.28, 1.0]],
    "wreath": [[0, 2414.0, 386.0, 35.38, 1.0]],
    # The grove east of the garden, Holt's drain down to the stream and the toads at its mouth.
    "spore": [[0, 2388.0, 221.0, 34.73, 0.0]],
    "pipes": [[0, 2368.5, 196.5, 36.12, 1.0], [0, 2386.0, 160.0, 34.71, 1.2], [0, 2398.0, 132.0, 33.46, 1.1]],
    "outlet": [[0, 2404.0, 113.0, 28.35, 1.3]],
    "toads": [[0, 2398.0, 120.0, 30.88, 0.0], [0, 2405.0, 124.0, 31.62, 1.0], [0, 2400.0, 116.0, 29.9, 2.0],
              [0, 2395.0, 128.0, 31.98, 3.0], [0, 2402.0, 131.0, 33.85, 4.0], [0, 2409.0, 126.0, 30.53, 5.0]],
    # Brightwater Lake's shore (Carolai's lily grows at 2905, 200), and the kitchen garden behind Cold
    # Hearth Manor (the abandoned farmhouse at 2161.5, 657).
    "silt": [[0, 2895.0, 212.0, 8.01, 0.0]],
    "moonlily": [[0, 2889.0, 196.0, 8.08, 0.0]],
    "frame": [[0, 2181.0, 682.0, 33.39, 2.0]],
}

# Townsfolk who remember a flower (A Bloom for Every Memory) and the guests (The First Harvest): the game's own.
RENEE, DILLINGER, WINTERS = 5688, 1496, 2134
HAMLIN, ABIGAIL, HOLLAND = 3547, 2118, 10665
CAROLAI = 2132

LINE = {
    "title": "The Stillgarden",
    "stages": [["R:endures.endures"], ["R:q1"], ["R:q2"], ["R:q3"], ["R:q4"], ["R:q5"], ["M:house_set"]],
    "quests": [
        {
            "id": "q1", "title": "A Patch of Earth", "giver": "edda", "ender": "edda", "prev": "endures.endures",
            "log": "Pull 6 patches of blighted weeds and shift 4 piles of rubble on Holt's Rise, Brill's eastern edge, take "
                   "soil from Edda's 3 marker stakes to Pellen Moss, then return to Edda Graves.",
            "offer": (
                "Mind your feet, dear. That's gloom weed you're standing in, and it bites through boots.$B$B"
                "Edda Graves. I sold flowers on the Lordamere road before the plague: roses for weddings, lilies for "
                "funerals, violets for apologies. I still know them all, every name. Strange, what stays. I couldn't tell "
                "you my sister's face, but I can tell you a white carnation means remembrance and a yellow one means "
                "you've been a fool.$B$B"
                "Brill's filling up with carts and lumber and hammering, and nobody has anywhere to simply sit. So I asked "
                "the Magistrate for this rise. Old Holt kept an orchard up here, once. Now it's weeds and broken wall, "
                "and Odo, who came with it.$B$B"
                "Pull the weeds and shift that rubble, would you? I've set three stakes where the beds ought to go; take "
                "a handful of soil from each to Pellen Moss. He'll tell us whether anything decent will grow in it. He'll "
                "tell us at length."),
            "progress": "Weeds first, then stones, then soil. Gardening is mostly the same three things, in that order, forever.",
            "done": (
                "(Edda reads Pellen's notes twice, her lips moving.)$B$B"
                "Acid. Grave-rich. Full of things that died and some that didn't quite finish. 'Capable of supporting "
                "unusual varieties, if properly treated.' Oh, I could kiss him. I won't. Neither of us would enjoy it.$B$B"
                "Do you know what that means, dear? It means it's a garden. It always was. It was only waiting for "
                "somebody to stop walking past it."),
            "objectives": [("credit", "weed_credit", 6, "Blighted weeds pulled"),
                           ("credit", "rubble_credit", 4, "Rubble shifted"),
                           ("credit", "soil_credit", 3, "Soil taken from the stakes"),
                           ("credit", "assess_credit", 1, "Pellen Moss's assessment")],
            "return": "Return to Edda Graves on Holt's Rise, at Brill's eastern edge.",
            "money": 2500, "xp": 4, "min_level": 8,
        },
        {
            "id": "q2", "title": "What Takes Root", "giver": "pellen", "ender": "pellen", "prev": "q1",
            "log": "Lift 6 gravebloom seedlings from between the stones of Brill's cemetery, take a pale spore cap from the "
                   "grove east of the garden and silt and water from the shore of Brightwater Lake, then plant and water "
                   "Edda's 3 beds. Return to Pellen Moss.",
            "offer": (
                "Pellen Moss. I study the flora of the Glades: what it does, what it cures, what it kills, and in which "
                "order.$B$B"
                "You've seen the soil. Most things would die in it. So we plant what has already learned to live in "
                "death. Gravebloom grows in Brill's cemetery, between the stones, where nothing else will: a pale little "
                "flower that roots in what's left of us. Six seedlings, lifted gently, with their soil.$B$B"
                "We'll want fungus to turn the ground. There's a shaded grove just east of here; look under the trees for "
                "a pale spore cap. And Brightwater Lake, north-east of town, has a grey silt along its shore that holds "
                "water like a sponge. A jar of the silt and a jar of the lake.$B$B"
                "Then plant Edda's beds and water them. Gently. Seedlings are like patients, $n. They mostly want to be "
                "left alone, but not too alone."),
            "progress": "Seedlings, spores, silt, water, then the beds. I've written it down. I write everything down.",
            "done": (
                "(Pellen kneels by the beds and says nothing for a long while, which you gather is praise.)$B$B"
                "They've taken. You see the gravebloom leaning toward the light? It does that the first night. In a week "
                "it'll turn its back on the sun entirely, as is proper.$B$B"
                "I'll confess something. When Edda said 'a garden', I thought she meant to plant a memory and watch it "
                "die. But this is botany. This, I can write down."),
            "objectives": [("credit", "seedling_credit", 6, "Gravebloom seedlings lifted"),
                           ("credit", "spore_credit", 1, "Pale spore cap"),
                           ("credit", "silt_credit", 1, "Brightwater silt and water"),
                           ("credit", "bed_credit", 3, "Beds planted and watered")],
            "return": "Return to Pellen Moss in the Stillgarden.",
            "money": 3500, "xp": 4, "min_level": 8,
        },
        {
            "id": "q3", "title": "The Garden's Hunger", "giver": "edda", "ender": "edda", "prev": "q2",
            "log": "Inspect 3 cracked sections of Holt's old drain running from the Stillgarden down to the stream, kill 6 "
                   "Bloated Drain Toads nesting at its mouth, clear the outlet, and help Pellen Moss mix a treatment for "
                   "the soil. Then return to Edda Graves.",
            "offer": (
                "Look at them, dear. Look at the gravebloom.$B$B"
                "(Along the beds the pale flowers have curled in on themselves. Their leaves are spotted brown, and the "
                "soil has a wet, sour sheen.)$B$B"
                "Three days ago they stood up like soldiers. Now they look the way I feel in the mornings. Pellen says "
                "it's the water. Holt laid a clay drain under this rise when it was an orchard, to carry the rain down to "
                "the stream north-east of here. If the drain's choked, the rain has nowhere to go but back up, into our "
                "beds, carrying whatever's been festering down there.$B$B"
                "Follow the old pipe down the slope; it's cracked open in places, and you can see in. Scrape up a little "
                "of the muck for Pellen while you're at it. Whatever's blocking the bottom, clear it. Then help him brew "
                "something to sweeten the ground. I'm too old to lose a garden twice."),
            "progress": "The beds are worse this morning. Pellen's taken to whispering at them. That's Odo's job.",
            "done": (
                "(Edda presses her hand flat on the treated soil and holds it there.)$B$B"
                "It's warm. Is that daft? It feels warm.$B$B"
                "Toads, you say. A whole nest of them squatting in Holt's pipe, and everything they left behind running "
                "back up into my beds. I've had lodgers like that.$B$B"
                "Pellen wants a frame over the seedlings now, to keep the worst of the rain off while the ground mends. "
                "Rudd Carver says he can spare the timber if somebody else finds the glass. Somebody else is usually me."),
            "objectives": [("credit", "pipe_credit", 3, "Cracked drain inspected"),
                           ("kill", "toad", 6, ""),
                           ("credit", "outlet_credit", 1, "Drain outlet cleared"),
                           ("credit", "treatment_credit", 1, "Soil treatment mixed with Pellen")],
            "return": "Return to Edda Graves in the Stillgarden.",
            "money": 4500, "xp": 5, "min_level": 9, "items": [(858, 2)],
        },
        {
            "id": "q4", "title": "A Bloom for Every Memory", "giver": "willa", "ender": "edda", "prev": "q3",
            "log": "Ask three of Brill's townsfolk what flowers they remember, take seeds from the old kitchen garden behind "
                   "Cold Hearth Manor and a moonpetal lily from the shore of Brightwater Lake, and help Willa Fen plant the "
                   "memorial bed. Then speak with Edda Graves.",
            "offer": (
                "Can I tell you something? I can't smell any of it.$B$B"
                "Not the gravebloom, not the nightshade, not whatever Pellen boils in that pot. The apothecaries say it's "
                "common in the newly risen; the nose goes first. I woke in a pit outside Andorhal four months ago and I "
                "haven't smelled a thing since, except smoke, once, and I think I imagined that.$B$B"
                "So I water the beds and I pull the weeds, and Edda talks about roses as if they were people she owes "
                "money to, and I don't see the point. Flowers are for the living. We aren't.$B$B"
                "She heard me say it. She didn't argue. She said you'd show me, and walked off. So... show me, I suppose. "
                "She says to ask people in town what flowers they remember, fetch seeds from the old garden at Cold Hearth "
                "Manor and a moonpetal lily from Brightwater's shore, and help me plant a bed for the people we can't "
                "remember. Her words."),
            "progress": "Has anyone remembered a flower yet? I asked a Deathguard once. He said 'red'.",
            "done": (
                "(Willa is still kneeling at the memorial bed. She has a hand cupped around the lily, as if to keep the "
                "wind off it.)$B$B"
                "She's been there an hour. She won't say why. Renee's wedding flowers, perhaps, or Dillinger's "
                "marigolds, or Mrs. Winters' mother's sweet peas. It doesn't matter which.$B$B"
                "'You can't smell them either,' she said to me. Not properly, not for years, I told her. That isn't what "
                "they're for any more, dear. They're for remembering on purpose, so you don't only remember by accident.$B$B"
                "She didn't answer. But she asked me what the lily was called. Twice."),
            "objectives": [("credit", "memory_credit", 3, "Townsfolk's flowers remembered"),
                           ("credit", "seed_credit", 1, "Seeds from Cold Hearth Manor"),
                           ("credit", "lily_credit", 1, "Moonpetal lily"),
                           ("credit", "memorial_credit", 1, "Memorial bed planted")],
            "return": "Speak with Edda Graves in the Stillgarden.",
            "money": 4000, "xp": 5, "min_level": 9, "items": [(3421, 1)],
        },
        {
            "id": "q5", "title": "The First Harvest", "giver": "edda", "ender": "edda", "prev": "q4",
            "log": "Cut the 3 ripe herbs in the Stillgarden's glasshouse, set out Pellen Moss's stall, lay Edda's bouquet on "
                   "the plague graves at the north end of the cemetery and invite Hamlin Atkins, Abigail Shiel and Junior "
                   "Apothecary Holland, then answer Edda's question.",
            "offer": (
                "The frame's up, the drain runs clean, and this morning Pellen stood among the seedlings and said, I quote, "
                "'adequate.' I nearly fainted.$B$B"
                "It's time, dear. The first harvest. Nothing grand: the peacebloom, the silverleaf and the first of the "
                "gravebloom, cut at the stem the way I showed you. Help Pellen set out his stall; he means to sell herbs to "
                "the town, and he has never sold anything in his life, or since.$B$B"
                "Then the invitations. The first flowers always went to the cemetery, in my day: the dead are a town's "
                "oldest residents, and we're hardly in a position to argue. Lay this bouquet on the plague graves at the "
                "north end. Then Hamlin Atkins, and Abigail Shiel, and young Holland, who's never been invited to "
                "anything without a corpse at it.$B$B"
                "And come and find me before the gathering. I have a question to put to you, and I've been putting it off."),
            "progress": "At the stem, dear, not the root. We're harvesting, not burying. That's the other place.",
            "done": (
                "(The rise is full: Hamlin explaining mushrooms to anyone who stands still, Abigail Shiel pricing Pellen's "
                "stall, Holland on his knees by the drain. Selina Weston came up from the lane uninvited and pretended "
                "she was passing. Odo walks among them, telling the plants who everyone is.)$B$B"
                "Look at them, $n. Half of them can't smell a thing, and they came anyway.$B$B"
                "(Edda raises a cup of something that may once have been elderflower cordial.)$B$B"
                "They may be dead, but that doesn't mean they should spend eternity somewhere ugly."),
            "objectives": [("credit", "herb_credit", 3, "Ripe herbs cut"),
                           ("credit", "stall_credit", 1, "Pellen's stall set out"),
                           ("credit", "invite_credit", 4, "Bouquet laid and guests invited"),
                           ("credit", "choice_credit", 1, "Edda's question answered")],
            "return": "Return to Edda Graves in the Stillgarden.",
            "money": 6000, "xp": 5, "min_level": 9, "items": [(22250, 1)],
        },
        # The garden kept: a daily (from the opening).
        {
            "id": "tending", "title": "A Garden Is Kept", "giver": "edda", "ender": "edda", "prev": "q5",
            "repeat": "daily",
            "log": "Tend 4 of the Stillgarden's beds and cut 3 ripe herbs in the glasshouse, then return to Edda Graves.",
            "offer": (
                "Morning, dear. Or evening. I've stopped keeping track; the plants keep it for me.$B$B"
                "A garden isn't made, it's kept. Pull what's crept back into the beds, pinch the dead heads off the "
                "gravebloom, and see what's ripe under the glass. Not too much, mind. We take a little and leave the "
                "rest, or there's nothing next week. That's gardening, and good husbandry, and most of what I know about "
                "people as well.$B$B"
                "Odo will tell you which beds want you. He talks to them, and they answer him, he says. I don't argue with "
                "Odo before noon."),
            "progress": "Four beds, three herbs. The gravebloom will try to nip you. It's affectionate.",
            "done": (
                "Lovely. You've a gardener's hands, $n, whatever else you've done with them.$B$B"
                "Take a share of the harvest. It's yours; you grew it, in a manner of speaking. In a manner of speaking, "
                "I'm still a florist. Pellen will want to weigh it first. Let him. It makes him happy, in his way."),
            "objectives": [("credit", "tend_credit", 4, "Beds tended"),
                           ("credit", "harvest_credit", 3, "Ripe herbs cut")],
            "return": "Return to Edda Graves in the Stillgarden.",
            "money": 1200, "xp": 2, "min_level": 9, "items": [(2447, 2), (765, 2)],
        },
    ],
    # Edda's question (which beds go to the front), the three townsfolk who remembered a flower and the three
    # guests (each once), and the house's furnishings bought.
    "markers": ["practical", "decorative", "remembered_renee", "remembered_dillinger", "remembered_winters",
                "invited_hamlin", "invited_abigail", "invited_holland", "house_set"],
    "npcs": [
        {"id": "edda", "name": "Edda Graves", "subname": "Gardener", "display": 4123, "level": 20, "from": 1,
         "spawns": AT["edda"]},
        {"id": "pellen", "name": "Pellen Moss", "subname": "Herbalist", "display": 2646, "level": 20, "from": 1, "until": 6,
         "spawns": AT["pellen"]},
        # Pellen at his stall once it's open: herbs, and herbalism taught as Faruza teaches it.
        {"id": "pellen_stall", "name": "Pellen Moss", "subname": "Herbalist", "display": 2646, "level": 20, "from": 6,
         "flags": ["gossip", "vendor"], "trainer": 2114, "spawns": AT["pellen_stall"],
         "vendor": [2447, 765, 2449, 785, 2450, 3369, 4605, 4604, 22250, 3421, 3419, 3420,
                    {"item": 2453, "cond": ["M:practical"]}, {"item": 2452, "cond": ["M:practical"]},
                    {"item": 2562, "cond": ["M:decorative"]}, {"item": 3422, "cond": ["M:decorative"]}]},
        {"id": "willa", "name": "Willa Fen", "subname": "Garden Attendant", "display": 2672, "level": 15, "from": 2,
         "until": 6, "spawns": AT["willa"]},
        {"id": "willa_day", "name": "Willa Fen", "subname": "Garden Attendant", "display": 2672, "level": 15, "from": 6,
         "when": "day", "flags": ["gossip"], "spawns": AT["willa_day"]},
        {"id": "willa_evening", "name": "Willa Fen", "subname": "Garden Attendant", "display": 2672, "level": 15,
         "from": 6, "when": "evening", "flags": ["gossip"], "spawns": AT["willa_evening"]},
        {"id": "odo", "name": "Odo", "subname": "Garden Watchman", "display": 2625, "level": 25, "from": 1, "until": 6,
         "flags": ["gossip"], "spawns": AT["odo"]},
        {"id": "odo_day", "name": "Odo", "subname": "Garden Watchman", "display": 2625, "level": 25, "from": 6,
         "when": "day", "flags": ["gossip"], "spawns": AT["odo_day"]},
        {"id": "odo_night", "name": "Odo", "subname": "Garden Watchman", "display": 2625, "level": 25, "from": 6,
         "when": "night", "flags": ["gossip"], "spawns": AT["odo_night"]},
        # While it's built: the builder's yard's hands, and the house's carpenter come to look (by day).
        {"id": "worker", "name": "Builder's Yard Laborer", "display": [2632, 2642, 2647], "level": 15, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "wander": 3, "spawns": AT["worker"]},
        {"id": "oswin", "name": "Oswin Thatcher", "subname": "Carpenter", "display": 1638, "level": 25, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "spawns": AT["oswin"]},
        # Once it's open: townsfolk on the benches of an evening, Carolai of a morning.
        {"id": "visitor", "name": "Brill Resident", "display": [2657, 2628, 2630], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "evening", "spawns": AT["visitor"]},
        {"id": "carolai", "name": "Carolai Anise", "subname": "Alchemy Trainer", "display": 1601, "level": 20,
         "flags": ["gossip"], "from": 6, "when": "morning", "spawns": AT["carolai"]},
        # The nest at the drain's mouth (soloable at 9 to 12).
        {"id": "toad", "name": "Bloated Drain Toad", "display": 5379, "scale": 1.2, "hostile": True, "faction": 14,
         "level": (9, 10), "type": 1, "health": 0.9, "damage": 0.9, "gold": 40, "wander": 4, "respawn": 60,
         "spawns": AT["toads"]},
    ],
    "credits": [
        {"id": "weed_credit", "name": "Blighted weeds pulled"},
        {"id": "rubble_credit", "name": "Rubble shifted"},
        {"id": "soil_credit", "name": "Soil taken from the stakes"},
        {"id": "assess_credit", "name": "Pellen Moss's assessment"},
        {"id": "seedling_credit", "name": "Gravebloom seedlings lifted"},
        {"id": "spore_credit", "name": "Pale spore cap"},
        {"id": "silt_credit", "name": "Brightwater silt and water"},
        {"id": "bed_credit", "name": "Beds planted and watered"},
        {"id": "pipe_credit", "name": "Cracked drain inspected"},
        {"id": "outlet_credit", "name": "Drain outlet cleared"},
        {"id": "treatment_credit", "name": "Soil treatment mixed with Pellen"},
        {"id": "memory_credit", "name": "Townsfolk's flowers remembered"},
        {"id": "seed_credit", "name": "Seeds from Cold Hearth Manor"},
        {"id": "lily_credit", "name": "Moonpetal lily"},
        {"id": "memorial_credit", "name": "Memorial bed planted"},
        {"id": "herb_credit", "name": "Ripe herbs cut"},
        {"id": "stall_credit", "name": "Pellen's stall set out"},
        {"id": "invite_credit", "name": "Bouquet laid and guests invited"},
        {"id": "choice_credit", "name": "Edda's question answered"},
        {"id": "tend_credit", "name": "Beds tended"},
        {"id": "harvest_credit", "name": "Ripe herbs cut"},
    ],
    "objects": [
        # Holt's Rise, overgrown (from the Board's going up until the garden opens).
        {"id": "weeds", "name": "Blighted Weeds", "display": 4111, "scale": 1.3, "from": 1, "until": 6, "spawns": AT["weeds"],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "weed_credit"}]},
        {"id": "rubble", "name": "Fallen Wall", "display": 134, "from": 1, "until": 6, "spawns": AT["rubble"],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "rubble_credit"}]},
        {"id": "markers", "name": "Edda's Marker Stake", "quest_only": True, "display": 5452, "scale": 0.8, "from": 1, "until": 6,
         "spawns": AT["markers"],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "soil_credit"}]},
        # The garden begins (from the second stage).
        {"id": "fence", "name": "Garden Fence", "display": 6151, "from": 2, "spawns": AT["fence"]},
        {"id": "beds", "name": "Garden Bed", "display": 20, "from": 2, "spawns": AT["beds"],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "bed_credit"},
                 {"cond": ["I:tending"], "quest": "tending", "credit": "tend_credit"}]},
        {"id": "shovel", "name": "Spade", "display": 6479, "from": 2, "until": 6, "spawns": AT["shovel"]},
        # Planted (from the third): the tool shed, planters, seedlings.
        {"id": "shed", "name": "Tool Shed", "display": 662, "from": 3, "spawns": AT["shed"]},
        {"id": "seedling_bed", "name": "Gravebloom", "display": 4632, "scale": 1.2, "from": 3, "spawns": AT["seedling_bed"]},
        {"id": "nightshade_bed", "name": "Nightshade", "display": 7884, "scale": 0.8, "from": 3, "spawns": AT["nightshade_bed"]},
        {"id": "planter_flowers", "name": "Asters", "display": 6648, "scale": 1.2, "from": 3, "spawns": AT["planter_flowers"]},
        # The drain mended, the frame raised, the plants well (from the fourth).
        {"id": "sluice", "name": "New Sluice", "display": 755, "scale": 2.5, "from": 4, "spawns": AT["sluice"]},
        {"id": "cistern", "name": "Rain Barrel", "display": 6036, "from": 4, "spawns": AT["cistern"]},
        {"id": "bloom_bed", "name": "Flower Bed", "display": 6313, "scale": 0.8, "from": 4, "spawns": AT["bloom_bed"]},
        {"id": "shroom", "name": "Pale Fungus", "display": 385, "scale": 0.45, "from": 4, "spawns": AT["shroom"]},
        {"id": "memorial", "name": "Memorial Bed", "display": 49, "from": 4, "spawns": AT["memorial"],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "memorial_credit"},
                 {"cond": ["I:tending"], "quest": "tending", "credit": "tend_credit"}]},
        # The memorial (from the fifth): benches to sit on, the plates, the flowers and the lily.
        {"id": "benches", "name": "Garden Bench", "display": 682, "type": 7, "from": 5, "spawns": AT["benches"]},
        {"id": "mem_flowers", "name": "Forget-Me-Nots", "display": 6647, "scale": 1.2, "from": 5, "spawns": AT["mem_flowers"]},
        {"id": "lily", "name": "Moonpetal Lily", "display": 253, "scale": 0.9, "from": 5, "spawns": AT["lily"]},
        # The harvest (from the fifth): what's ripe under the glass, and the stall to sell it from.
        {"id": "herbs_peace", "name": "Ripe Peacebloom", "display": 269, "scale": 0.6, "from": 5, "spawns": AT["herbs_peace"],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "herb_credit"},
                 {"cond": ["I:tending"], "quest": "tending", "credit": "harvest_credit"}]},
        {"id": "herbs_silver", "name": "Ripe Silverleaf", "display": 270, "scale": 0.4, "from": 5, "spawns": AT["herbs_silver"],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "herb_credit"},
                 {"cond": ["I:tending"], "quest": "tending", "credit": "harvest_credit"}]},
        {"id": "herbs_grave", "name": "Ripe Gravebloom", "display": 4632, "scale": 1.8, "from": 5, "spawns": AT["herbs_grave"],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "herb_credit"},
                 {"cond": ["I:tending"], "quest": "tending", "credit": "harvest_credit"}]},
        {"id": "stall", "name": "Pellen's Stall", "display": 7443, "from": 5, "spawns": AT["stall"],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "stall_credit"}]},
        # Open (from the sixth): Pellen's wares, the gate's lanterns, flowers in pots.
        {"id": "sacks", "name": "Herb Sacks", "display": 6963, "from": 6, "spawns": AT["sacks"]},
        # Odo's lantern at the gate, by night.
        # What Takes Root: gravebloom in the cemetery (from the second stage: everyone else's cemetery is as it was),
        # the spore cap in the grove; silt on Brightwater's shore (everyone's: it's far outside Brill).
        {"id": "seedlings", "name": "Gravebloom", "quest_only": True, "display": 4632, "from": 2, "spawns": AT["seedlings"],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "seedling_credit"}]},
        {"id": "spore", "name": "Pale Spore Cap", "quest_only": True, "display": 359, "scale": 0.7, "from": 2, "spawns": AT["spore"],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "spore_credit"}]},
        {"id": "silt", "name": "Brightwater Silt", "quest_only": True, "display": 20, "scale": 0.5, "spawns": AT["silt"],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "silt_credit"}]},
        # The Garden's Hunger: Holt's drain and its mouth by the stream (everyone's).
        {"id": "pipes", "name": "Cracked Drain", "quest_only": True, "display": 7969, "scale": 2.5, "spawns": AT["pipes"],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "pipe_credit"}]},
        {"id": "outlet", "name": "Choked Drain Mouth", "quest_only": True, "display": 134, "spawns": AT["outlet"],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "outlet_credit"}]},
        # A Bloom for Every Memory: seeds at Cold Hearth Manor, a lily on Brightwater's shore (everyone's).
        {"id": "frame", "name": "Rotted Seed Frame", "quest_only": True, "display": 6606, "spawns": AT["frame"],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "seed_credit"}]},
        {"id": "moonlily", "name": "Moonpetal Lily", "quest_only": True, "display": 253, "spawns": AT["moonlily"],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "lily_credit"}]},
        # The First Harvest: the plague graves (everyone's), and Edda's wreath on them (from the opening).
        {"id": "graves", "name": "Plague Graves", "quest_only": True, "display": 498, "scale": 1.6, "spawns": AT["graves"],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "invite_credit"}]},
        {"id": "wreath", "name": "Edda's Wreath", "display": 6646, "from": 6, "spawns": AT["wreath"]},
        # Edda's flowers at the foot of the chapel's wall of names, once both are open (tools/town/chapel.py: its
        # memorial at the chapel's own (12.5, 7.6), between the candelabra; these at (12, 7) and (13, 7), its floor).
        {"id": "wall_flowers", "name": "Edda's Flowers", "display": 6647, "scale": 1.3, "from": 6, "needs": {"chapel": 6},
         "spawns": [[0, 2396.61, 393.94, 37.2, 2.094], [0, 2395.74, 393.44, 37.2, 2.094]]},
        # The house's furnishings (bought from Edda): asters in a pot by the door, a fungus garden under glass
        # (against the doorway's wall: the slots asked for, (-0.6, -3.9) and (3.9, -2.6), are in the way in and
        # under Carolai's alchemy table when she lives there).
        {"id": "house_terrarium", "name": "Fungal Terrarium", "display": 7792, "scale": 1.2, "from": 7,
         "spawns": [["house", -4.9, 3.85, 0, 0]]},
    ],
    "gossip": [
        # Edda, by how far the garden's come (the first that holds).
        {"npc": "edda", "kind": "greet", "cond": ["R:q5", "M:practical"], "texts": [
            "Herbs at the front, as you said. Pellen's taken to standing among them with his hands behind his back like a "
            "general. The flowers sulk in the corners. Flowers are good at corners.",
            "Johaan's sent his apprentice up twice this week for silverleaf. Twice! A garden that's useful. My mother "
            "would never have believed it.",
            "Come and sit, dear. The herbs don't mind being looked at. They just don't care if you do."]},
        {"npc": "edda", "kind": "greet", "cond": ["R:q5", "M:decorative"], "texts": [
            "Flowers at the front, as you said. People stop at the gate just to look. Some of them come in. One of them "
            "cried, last Tuesday. Don't tell her I told you.",
            "Pellen's herbs are at the back, where the light's better for them anyway, which is what I told him the "
            "reason was. Don't contradict me.",
            "Come and sit, dear. The asters are out. They mean patience. Or possibly afterthought. I forget which."]},
        {"npc": "edda", "kind": "greet", "cond": ["R:q4"],
         "text": "Willa planted three more forget-me-nots this morning without being asked. I didn't say a word. I went "
                 "behind the frame and had a little sit-down."},
        {"npc": "edda", "kind": "greet", "cond": ["R:q3"],
         "text": "Willa's been watering the beds twice a day and telling me it's pointless twice a day. I've given her "
                 "something to think about. Or rather, I've given you something to give her."},
        {"npc": "edda", "kind": "greet", "cond": ["R:q2"],
         "text": "Gravebloom, dear. Pale as candles and twice as stubborn. If they make it through the week, we'll have a "
                 "garden."},
        {"npc": "edda", "kind": "greet", "cond": ["R:q1"],
         "text": "Rudd Carver's lads have put the fence up. It leans. Everything in Brill leans. I've decided it's a style."},
        {"npc": "edda", "kind": "greet",
         "text": "Edda Graves, dear. Florist, once. I'm going to make a garden here, if the weeds and Odo will let me."},
        # Edda: her question (The First Harvest).
        {"npc": "edda", "kind": "option", "cond": ["I:q5"],
         "text": "The herbs. Brill needs medicine more than ornament.",
         "action": "choice", "quest": "q5", "credit": "choice_credit", "marker": "practical", "emote": 273,
         "reply": "Practical. Pellen will be insufferable. ...You're right, of course. The herbs get the front and the "
                  "light, and the flowers can have the corners. Flowers are good at corners. So were most of my relatives."},
        {"npc": "edda", "kind": "option", "cond": ["I:q5"],
         "text": "The flowers. The town has enough that's merely useful.",
         "action": "choice", "quest": "q5", "credit": "choice_credit", "marker": "decorative", "emote": 4,
         "reply": "Flowers! Oh, I knew I liked you. The front beds for colour, then, and Pellen's herbs at the back where "
                  "the light suits them, which is what I shall tell him the reason was."},
        # Edda: the house's furnishings, once the garden's open.
        {"npc": "edda", "kind": "option", "cond": ["R:q5", "OWN"], "text": "Have you anything green for my house?",
         "action": "buy", "arg": 7500, "marker": "house_set", "emote": 2,
         "reply": "For the house by the road? Oh, yes. A pot of asters for beside the door, and one of Pellen's little "
                  "glass jars with a fungus garden inside: no water, no light, no fuss. It will outlive us both. Well. "
                  "It'll outlive you. Odo will carry them round."},
        # Pellen.
        {"npc": "pellen", "kind": "greet", "cond": ["R:q3"],
         "text": "Necrotic loam, treated with lime and bone. I've written it up. Nobody will read it, but it's written."},
        {"npc": "pellen", "kind": "greet", "cond": ["R:q2"],
         "text": "The gravebloom has turned its back on the sun. Entirely as predicted. I find that very restful."},
        {"npc": "pellen", "kind": "greet", "cond": ["R:q1"],
         "text": "Acid, grave-rich, and full of fungal thread. I've seen worse soil. I've been buried in worse soil."},
        {"npc": "pellen", "kind": "greet",
         "text": "Pellen Moss. Don't touch that. Or that. That one you may touch, but you'll regret it."},
        {"npc": "pellen", "kind": "option", "cond": ["I:q1"], "text": "I've brought the soil from Edda's stakes.",
         "action": "credit", "quest": "q1", "credit": "assess_credit", "emote": 1,
         "reply": "(Pellen tips each handful onto a slate, sniffs it, rubs it between finger and thumb, and writes for some "
                  "time.) Acid. Heavy with bone meal, which is to say bone. Fungal threads throughout. Ordinary flowers "
                  "would sulk and die here. Gravebloom, nightshade, the paler fungi... Tell Edda it will grow things. "
                  "Unusual things. If properly treated. Underline 'properly'."},
        # Pellen: the soil treatment (The Garden's Hunger); he knows the threads if the player cleansed the well.
        {"npc": "pellen", "kind": "option", "cond": ["I:q3", "R:well.clear"], "text": "Edda sent me to help with the soil treatment.",
         "action": "credit", "quest": "q3", "credit": "treatment_credit", "emote": 1,
         "reply": "Look here, under the glass. These pale threads: I've seen them before, in a jar on Holland's bench. The "
                  "parasite from Maudie's well. You burned it out of the west channel, I'm told; these are what washed "
                  "round by the stream before you did, and settled in Holt's drain. They're dying already. Holland's lime "
                  "and bitterroot ash, then, cut with bone meal for the roots. Stir. Slowly. There."},
        {"npc": "pellen", "kind": "option", "cond": ["I:q3", "!R:well.clear"], "text": "Edda sent me to help with the soil treatment.",
         "action": "credit", "quest": "q3", "credit": "treatment_credit", "emote": 1,
         "reply": "Look here, under the glass. Pale threads, thousands of them, feeding on the rot. Larvae of some kind. "
                  "Something upstream is laying them, somewhere dark and wet; I'll send a jar to Junior Apothecary "
                  "Holland, who collects this sort of thing. Today we sweeten the ground: lime, ash and bone meal, worked "
                  "in by hand. Stir. Slowly. There."},
        # Pellen at his stall.
        {"npc": "pellen_stall", "kind": "greet", "cond": ["M:practical"],
         "text": "Peacebloom, silverleaf, earthroot, mageroyal, and bruiseweed for those who know what to do with it. The "
                 "herbs have the front beds now. I may have said 'adequate' again. I meant it more."},
        {"npc": "pellen_stall", "kind": "greet",
         "text": "Herbs, and a few flowers, since Edda insists people want to buy things that do nothing. Apparently they "
                 "do. I've stopped arguing. I've started charging."},
        # Willa, while it's built and once it's open.
        {"npc": "willa", "kind": "greet", "cond": ["A:q4"],
         "text": "Ask them what flowers they remember. Then come back and tell me. I'll pretend not to be interested."},
        {"npc": "willa", "kind": "greet",
         "text": "Willa Fen. I water things. They grow. I still don't see what for, but I'm told that's the beginning of "
                 "gardening."},
        {"npc": "willa_day", "kind": "greet",
         "texts": ["Forget-me-nots by the gate, now. I picked the spot. Don't tell Edda; she'll be smug about it.",
                   "I still can't smell them. I know which is which, though. I've learned them all. Edda says that's "
                   "better than smelling. She's lying, but it's kind of her.",
                   "Water in the morning, never at noon. The leaves scald. I didn't know a dead woman could worry about "
                   "leaves scalding."]},
        {"npc": "willa_evening", "kind": "greet",
         "text": "I sit with the lily of an evening. I don't know why. It doesn't smell of anything, to me. But somebody "
                 "planted a lily for every one of us that nobody's waiting for, and I like to keep it company."},
        # Odo.
        {"npc": "odo", "kind": "greet", "cond": ["R:q2"],
         "text": "I've told the gravebloom who everyone is. That one there doesn't like Pellen. I don't blame it."},
        {"npc": "odo", "kind": "greet",
         "texts": ["Odo. Groundskeeper. Holt hired me forty years ago and nobody's told me to stop. So I haven't.",
                   "Don't mind me. I'm just telling the apple stumps it's going to be all right. It isn't, for them. "
                   "But you say these things."]},
        {"npc": "odo_day", "kind": "greet", "cond": ["DOG"],
         "text": "Your big dog slept under the east bench all yesterday afternoon. I told the asters he was a friend. "
                 "They were very good about it."},
        {"npc": "odo_day", "kind": "greet",
         "texts": ["Shh. The silverleaf's asleep. ...No, I'm joking. Mostly.",
                   "Forty years I kept Holt's apples. Now it's gravebloom. Gravebloom listens better. Apples just want to "
                   "fall on you.",
                   "Edda says I'm a watchman. I watch. Mostly I watch the plants. Somebody ought to."]},
        {"npc": "odo_night", "kind": "greet",
         "text": "Evening. Or morning, by your lot's reckoning. I keep the lantern lit so the plants know where the gate "
                 "is. Some of them wander."},
        # The builder's yard's hands, and Oswin.
        {"npc": "worker", "kind": "greet",
         "texts": ["Fence posts. A garden needs a fence, the old lady says, so the flowers know where they're allowed.",
                   "Rudd says plant it straight. The ground says otherwise. The ground usually wins round here.",
                   "That old watchman keeps telling the rubble our names. I don't like it knowing my name."]},
        {"npc": "oswin", "kind": "greet",
         "text": "Oswin Thatcher. Jamie Nore lends me out like a ladder. Your house is holding up; I looked in on it on "
                 "the way. This fence won't, if those lads keep setting posts in wet ground."},
        # Townsfolk on the benches of an evening.
        {"npc": "visitor", "kind": "greet",
         "texts": ["I come up here after the inn closes its doors for the night. It's quiet. That's all. That's enough.",
                   "My wife grew lavender. I can't smell this lot, but I know it's lavender. That's something, isn't it?",
                   "The lady with the flowers asked me what I remembered. I said nothing. Then I sat here an hour and "
                   "remembered a hedge.",
                   "Don't sit on that end. Odo says the bench is haunted. It's not. It's just Odo, at night."]},
        # Carolai, of a morning (her own menu is src/BrillHome.cpp's; this is her at the garden).
        {"npc": "carolai", "kind": "greet", "cond": ["CAROLAI_HOME"],
         "text": "You're up early. I didn't want to wake you. I only came for nightshade, and a little gravebloom, and "
                 "I'll be home before the kettle's cold. I'm always home before the kettle's cold."},
        {"npc": "carolai", "kind": "greet", "cond": ["LOVERS"],
         "text": "There you are. I knew you'd come by; you always take the long way round on a market day. Hold the "
                 "basket for me. No, closer."},
        {"npc": "carolai", "kind": "greet", "cond": ["FRIENDS"],
         "text": "Hello, friend. Edda lets me take what I need if I weed for it. I weed very thoroughly. Nothing grows here "
                 "that I haven't approved of."},
        {"npc": "carolai", "kind": "greet",
         "text": "Carolai Anise. I have an arrangement with Edda: I weed, and she doesn't ask what the nightshade is for. "
                 "It's for tonics. Mostly."},
        # Carolai at her shop, on the moonpetal lily in the memorial bed (lovers, friends, or neither).
        {"npc": CAROLAI, "kind": "option", "cond": ["R:q4", "LOVERS"], "text": "(Ask her about the lily in Edda's memorial bed.)",
         "action": "say", "emote": 1,
         "reply": "Edda came to my shop and asked what a moonpetal lily meant. I told her. She went very quiet, and then "
                  "she planted one for everyone in Brill who never got an answer. I already have mine, my love. It's in my "
                  "locket, pressed flat, where nothing can take it. I check it every morning. I check on you every morning "
                  "too, from the window. Don't tell Edda."},
        {"npc": CAROLAI, "kind": "option", "cond": ["R:q4", "FRIENDS"], "text": "(Ask her about the lily in Edda's memorial bed.)",
         "action": "say", "emote": 1,
         "reply": "The lily in Edda's bed? I gave her the cutting. Don't look at me like that; friends give each other "
                  "things. You gave me a lily once and told me what it meant, and I've kept it, and the meaning, exactly "
                  "as you said it. I keep everything exactly as it's said."},
        {"npc": CAROLAI, "kind": "option", "cond": ["R:q4", "!LOVERS", "!FRIENDS"],
         "text": "(Ask her about the lily in Edda's memorial bed.)", "action": "say", "emote": 1,
         "reply": "Edda's put a moonpetal lily in her memorial bed. Before the plague, a girl in Tirisfal gave one to the "
                  "one she meant to marry; if they kept it, that meant yes. Edda says hers is for everyone who never got "
                  "to ask. I think she's wrong. I think it's for everyone who's still waiting for an answer."},
        # A Bloom for Every Memory: three townsfolk and the flower each remembers (once each).
        {"npc": RENEE, "kind": "option", "cond": ["I:q4"], "text": "Do you remember any flowers from your life before?",
         "action": "credit", "quest": "q4", "credit": "memory_credit", "marker": "remembered_renee", "emote": 1,
         "reply": "Flowers. Hm. ...White heather and orange blossom. My wedding, in the chapel at Tarren Mill. The heather "
                  "made me sneeze all through the vows, and Garold laughed so hard the priest stopped. I don't remember "
                  "Garold's face. I remember the sneezing."},
        {"npc": DILLINGER, "kind": "option", "cond": ["I:q4"], "text": "Do you remember any flowers from your life before?",
         "action": "credit", "quest": "q4", "credit": "memory_credit", "marker": "remembered_dillinger", "emote": 1,
         "reply": "Marigolds. I put them on my brother's grave every autumn for nine years. He drowned in the Lordamere "
                  "when we were boys. I used to think the marigolds were for him. There's nobody to put them on mine now, "
                  "and I find I don't mind. I think they were for me all along."},
        {"npc": WINTERS, "kind": "option", "cond": ["I:q4"], "text": "Do you remember any flowers from your life before?",
         "action": "credit", "quest": "q4", "credit": "memory_credit", "marker": "remembered_winters", "emote": 1,
         "reply": "Sweet peas. My mother grew them up the back fence: pink and white, and a purple one she called the "
                  "bishop. We had to pick them every morning, or they'd stop flowering. You have to keep taking from them, "
                  "she said. That was her whole philosophy of children, too."},
        # The First Harvest: the guests (once each).
        {"npc": HAMLIN, "kind": "option", "cond": ["I:q5"], "text": "Edda Graves invites you to the Stillgarden's opening.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "invited_hamlin", "emote": 4,
         "reply": "A garden opening! On the rise? Will there be mushrooms? There ought to be mushrooms. I'll bring "
                  "mushrooms. The quiet ones."},
        {"npc": ABIGAIL, "kind": "option", "cond": ["I:q5"], "text": "Edda Graves invites you to the Stillgarden's opening.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "invited_abigail", "emote": 1,
         "reply": "The garden? With the herbalist who labels everything twice? I'll come. Somebody has to sell him twine "
                  "for all those bundles, and it may as well be me."},
        {"npc": HOLLAND, "kind": "option", "cond": ["I:q5"], "text": "Edda Graves invites you to the Stillgarden's opening.",
         "action": "credit", "quest": "q5", "credit": "invite_credit", "marker": "invited_holland", "emote": 6,
         "reply": "Me? To a... an opening? Nobody invites me to anything that isn't an autopsy. ...I'll come. May I look "
                  "at the drain while I'm there? I've been curious about the drain."},
    ],
}
