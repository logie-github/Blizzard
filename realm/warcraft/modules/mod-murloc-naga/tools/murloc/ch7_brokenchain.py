# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 7 of the murlocs' story: Brokenchain (levels 36 to 40), the bible's section 13.

Dustwallow Marsh. The hub is the Mire Islets: a mound of an islet and its little north-east islet off
Dreadmurk Shore's north end (x -2185..-2228, y -4148..-4216), at the lip of the trench where the sea floor
drops away, 80 yards and more from the Mirefin's northern island; the little islet to its north holds the
tribe's graveyard. Grandmother Shellback rests in the bay west of it. King Mrrgum's court is the murlocs'
phase's own: a throne of shells on the beach under the cliffs west of the islets (x -2400..-2445,
y -3755..-3800), 60 yards and more from the game's Mirefin, whose villages to the south are his warriors'
(7.17). Theramore is only escaped (7.01, its harbour's pier, and Shellback carrying you there and back) and
looked at (7.22, the lighthouse rock outside it); Brackenwall Village is entered once, for its pots (7.11).
Gorlak Brokenchain fishes in the stream below Brackenwall; Apprentice Lysander practises on the beach north
of Sentry Point.

Chapter 6 ends by teleporting the player to "hub": the tribe has just landed on the islets on the turtle's
back, wet and cold, and Blrrgl's crate went to Theramore's harbour on the supply ship (7.01 is getting him
out of it). The arrival's reward makes the islets the tribe's: the hub kit, the graveyard and the
Current-Caller appear from it.

Scenes and phases: a story phase's people only see their own phase's people and those always there, so the
scenes that join the camp (from the arrival) and the Elder (until 9.21) are directed by Grandmother
Shellback, who is always in the bay. Those who come along on an errand (Murlorga at the court, Blrrgl on the
knoll, Grrmlgrrl in the reeds, Gorlak at the bay, the tribe at Gorlak's reeds) are summoned by the scene
that sends you. Plain data: tools/murloc/SCHEMA.md."""

ARRIVAL = "ch7_arrival"
CAMP = ("from", ARRIVAL)                    # the hub kit, and everything of the camp
LANDING = ("until", ARRIVAL)                # the tribe as it landed, wet
DOCK = ("during", ARRIVAL)                  # Theramore's harbour, while Blrrgl is in his crate
KING = ("until", "ch7_feast")               # King Mrrgum on his throne, well fed
SICK = ("between", "ch7_feast", "ch7_topple")   # ...green, after the stew (and for good, if 7.18b)
FRY = ("until", "ch7_pen")                  # the tribute fry, in the king's line and his pen
FREED = ("from", "ch7_pen")                 # the tribute fry, at home on the islets

CHAPTER = dict(key="ch7", title="Brokenchain", levels=(36, 40), map=1, zones=[15], hub="hub")

TOWNS = ["Brackenwall Village", "Theramore Isle"]

PLACES = {
    # the Mire Islets: the camp on the big islet's mound, the trades on the little north-east islet
    "hub": (-2209.0, -4168.0), "cookpot": (-2205.0, -4163.5), "murlorga": (-2202.5, -4161.5),
    "elder": (-2214.0, -4163.0), "elder_draw": (-2212.0, -4161.0), "glubbub": (-2213.5, -4174.0),
    "grrmlgrrl": (-2205.5, -4175.5), "grrm_front": (-2206.5, -4178.0), "grrm_draw": (-2204.0, -4174.0),
    "sloshy": (-2207.0, -4160.0), "altar": (-2210.5, -4171.5), "caller": (-2201.0, -4169.0), "mailbox": (-2203.5, -4156.5),
    "blrrgl": (-2218.0, -4179.0), "blrrgl_log": (-2220.5, -4181.5), "blrrgl_draw": (-2216.0, -4177.0),
    "blrrgl_draw2": (-2217.0, -4176.0), "blrrgl_run": (-2212.0, -4184.0), "blrrgl_head": (-2218.0, -4179.0, 9.1),
    "t_warrior": (-2217.0, -4157.0), "t_hunter": (-2221.0, -4165.0), "crab": (-2222.5, -4167.5),
    "crab_meat": (-2222.0, -4166.0), "t_priest": (-2220.0, -4172.0), "t_mage": (-2214.0, -4183.0),
    "t_firstaid": (-2200.0, -4176.0), "t_fishing": (-2199.0, -4152.0), "t_food": (-2203.0, -4181.0),
    "fish_rack": (-2204.5, -4183.5),
    "krrgl": (-2209.5, -4185.5), "anvil": (-2211.5, -4187.0), "krrgl_post": (-2208.0, -4187.0),
    "mrsha": (-2223.0, -4176.0), "brewglub": (-2223.5, -4170.5), "grrsh": (-2206.0, -4189.5),
    "mrrsk": (-2202.0, -4188.0), "scrawlgl": (-2217.0, -4186.0), "fnrrgl": (-2200.5, -4184.0),
    "brrkl": (-2190.0, -4209.0), "sprokgl": (-2196.5, -4210.5), "mmrglla": (-2190.5, -4200.0),
    "mmrglla_front": (-2192.5, -4201.5), "mmrglla_front2": (-2191.0, -4202.5), "nets": (-2187.5, -4198.5),
    "shimmrl": (-2196.0, -4202.0), "pearlmrgl": (-2187.0, -4205.0),
    "hut_w": (-2206.0, -4148.5), "hut_s": (-2228.0, -4179.0), "hut_ne": (-2186.0, -4213.0),
    "graveyard": (-2185.0, -4179.0), "shellback": (-2205.0, -4136.0, -1.5), "landing": (-2203.0, -4157.0),
    "big_pot": (-2207.5, -4165.5),
    "fry_home_1": (-2200.5, -4164.0), "fry_home_2": (-2199.0, -4161.5), "fry_home_3": (-2203.5, -4166.5),
    "fry_home_4": (-2198.5, -4167.0), "fry_home_5": (-2201.5, -4159.0),
    "huddle_1": (-2203.0, -4153.5), "huddle_2": (-2206.0, -4152.5), "huddle_3": (-2200.5, -4157.5),
    "huddle_4": (-2205.0, -4156.5), "huddle_5": (-2209.0, -4154.5), "huddle_6": (-2199.5, -4154.5),
    "vision_chef": (-2207.5, -4151.0), "vision_egg": (-2207.5, -4150.0, 2.5), "vision_boat": (-2203.0, -4142.0, 0.0),
    "vision_flag": (-2200.0, -4143.0, 0.6),
    "reed_1": (-2211.0, -4149.5), "reed_2": (-2190.0, -4135.0), "reed_3": (-2185.5, -4183.0), "reed_4": (-2227.0, -4185.0),
    "reed_5": (-2214.0, -4193.0), "reed_6": (-2208.0, -4196.0), "reed_7": (-2200.0, -4215.0), "reed_8": (-2184.0, -4208.0),
    "shells_isle": (-2224.0, -4268.0), "shells_beach": (-2470.0, -3840.0),
    # what the islets look toward (for facing and pointing)
    "theramore": (-3750.0, -4483.0, 40.0), "brackenwall": (-3113.0, -2860.0, 40.0), "lighthouse": (-3655.0, -4755.0, 20.0),
    "court_far": (-2418.0, -3776.0, 10.0), "firemane_far": (-4390.0, -3300.0, 40.0), "raptors_far": (-2680.0, -3550.0, 40.0),
    "spiders_far": (-2810.0, -2700.0, 45.0), "east_sea": (-2200.0, -4600.0, 0.0), "south_sea": (-2900.0, -4700.0, 0.0),
    "witch_hill": (-2950.0, -3890.0, 40.0),
    # King Mrrgum's court: the beach under the cliffs west of the islets
    "court": (-2418.0, -3776.0), "throne": (-2418.0, -3759.5), "king_seat": (-2418.0, -3762.0),
    "throne_front": (-2416.5, -3768.5), "table": (-2418.0, -3765.5), "bowl_spot": (-2419.0, -3766.5),
    "king_fall": (-2418.0, -3766.0), "key_spot": (-2416.0, -3767.5),
    "shell_1": (-2413.0, -3760.0), "shell_2": (-2423.0, -3760.0), "shell_3": (-2415.5, -3757.5), "shell_4": (-2420.5, -3757.5),
    "guard_1": (-2411.5, -3764.0), "guard_2": (-2424.5, -3764.0), "kick_spot": (-2417.0, -3784.0),
    "fry_water": (-2412.0, -3797.0),
    "line_1": (-2418.0, -3779.0), "line_2": (-2418.5, -3782.5), "line_3": (-2418.0, -3786.0), "line_4": (-2418.5, -3789.5),
    "crowd_1": (-2409.0, -3772.0), "crowd_2": (-2427.0, -3773.0), "crowd_3": (-2410.0, -3780.0), "crowd_4": (-2426.0, -3781.0),
    "chaos_1": (-2404.0, -3779.0), "chaos_2": (-2430.0, -3786.0),
    "pen": (-2433.0, -3772.0), "pen_gate": (-2429.0, -3772.0), "pen_1": (-2432.0, -3770.0), "pen_2": (-2434.5, -3771.0),
    "pen_3": (-2432.5, -3774.0), "pen_4": (-2435.0, -3774.5), "pen_5": (-2433.5, -3768.5), "pen_6": (-2431.0, -3772.5),
    "gate_out_1": (-2427.5, -3771.0), "gate_out_2": (-2427.0, -3774.0),
    "larder_1": (-2406.0, -3766.0), "larder_2": (-2404.0, -3772.0),
    "hoard_1": (-2424.0, -3756.5), "hoard_2": (-2413.0, -3756.5), "hoard_3": (-2421.0, -3754.0), "hoard_4": (-2416.0, -3754.0),
    "casket": (-2427.0, -3758.5), "hoard_side": (-2428.5, -3761.5), "bag_spot": (-2427.5, -3763.0),
    "mother_1": (-2403.0, -3779.0), "mother_2": (-2406.0, -3783.0), "mother_3": (-2402.0, -3775.0),
    "brrsha": (-2413.5, -3763.5), "brrsha_floor": (-2416.0, -3765.5), "brrsha_side": (-2412.0, -3766.0),
    "court_fire_1": (-2409.0, -3786.0), "court_fire_2": (-2427.0, -3787.0),
    "vantage": (-2442.0, -3795.0), "vantage_m": (-2443.5, -3793.0), "scout_ladle": (-2442.5, -3791.5),
    "mud": (-2462.0, -3833.0), "mud_bank": (-2457.0, -3826.0), "mud_1": (-2464.0, -3836.0), "mud_2": (-2459.5, -3835.5),
    "reeds_guard": (-2478.0, -3812.0), "mirefin": (-2575.0, -3905.0),
    # the knoll above the beach, where Blrrgl finds out where he is
    "dune_top": (-2384.0, -3728.0), "dune_side": (-2386.0, -3731.0), "view_swamp": (-2700.0, -3700.0, 60.0),
    # Theramore's harbour: the pier's seaward edge, its water
    "dock_a": (-3878.0, -4631.0, 9.6), "dock_b": (-3886.0, -4630.0, 9.6), "crate": (-3882.0, -4637.0, 9.6),
    "crowbar": (-3884.0, -4624.0, 9.6), "crate_splash": (-3882.0, -4654.0, 0.0), "blrrgl_up": (-3880.0, -4659.0, 0.0),
    "ferry": (-3872.0, -4672.0, -1.0), "harbour_out": (-3872.0, -4712.0, 0.0), "blrrgl_away": (-3820.0, -4700.0, 0.0),
    # the lighthouse rock east of Theramore's harbour
    "keeper": (-3646.0, -4748.0), "keeper_out": (-3650.0, -4753.0), "step_pearl": (-3649.0, -4751.0),
    "keeper_step": (-3648.5, -4750.0), "lamp": (-3663.7, -4751.4, 25.0),
    # Witch Hill: the haunted manor's pumpkin patch
    "patch": (-2933.0, -3886.0), "pumpkin_2": (-2935.5, -3890.0), "pumpkin_3": (-2931.0, -3889.5),
    "husk_1": (-2920.0, -3878.0), "husk_2": (-2925.0, -3901.0),
    # Brackenwall: Gorlak's reeds below the village, the cookfires in it, the deserters' hills south of it
    "gorlak": (-3112.0, -3000.0), "gorlak_front": (-3110.5, -2996.5), "gorlak_draw": (-3109.5, -3002.5),
    "gorlak_draw2": (-3108.5, -3001.0), "toss": (-3109.0, -2998.0), "gorlak_fire": (-3115.5, -3003.5),
    "grrm_by_gorlak": (-3116.0, -2996.5), "song_1": (-3106.0, -3004.0), "song_2": (-3117.0, -3006.0),
    "song_3": (-3121.0, -3001.0), "song_4": (-3108.0, -3008.0), "drum": (-3113.5, -3005.5), "song_pot": (-3118.5, -3009.0),
    "pot_1": (-3122.0, -2912.0), "pot_2": (-3158.0, -2922.0), "pot_3": (-3120.0, -2862.0), "pot_4": (-3100.0, -2905.0),
    "deserters": (-3920.0, -2850.0), "spiders": (-2810.0, -2700.0),
    # Dustwallow Bay's deepest water, and its shore
    "bay_shore": (-3430.0, -3868.0), "deep_bay": (-3435.0, -3820.0), "manacle_rest": (-3436.0, -3821.5),
    # Lysander's beach, north of Sentry Point
    "lysander": (-3195.0, -4222.0), "wand_spot": (-3203.0, -4229.0), "book": (-3196.5, -4220.0),
    "circle_1": (-3190.0, -4215.0), "circle_2": (-3184.0, -4225.0), "circle_3": (-3193.0, -4233.0), "circle_4": (-3200.0, -4219.0),
    "page_1": (-3150.0, -4205.0), "page_2": (-3165.0, -4228.0), "page_3": (-3176.0, -4196.0), "page_4": (-3186.0, -4236.0),
    "page_5": (-3208.0, -4214.0), "page_6": (-3218.0, -4236.0), "page_7": (-3236.0, -4238.0), "page_8": (-3140.0, -4215.0),
    # where the marsh's beasts are
    "raptors": (-2680.0, -3550.0), "firemane": (-4390.0, -3300.0),
}

# -- the people -------------------------------------------------------------------------------------

NPCS = [
    # the tribe as it landed, the night before (until the arrival: the camp is made from its reward)
    dict(key="huddle_murlorga", name="Murlorga", subname="", look="murloc_orange", level=18, role="ambient",
         at="huddle_1", facing=4.6, phase=LANDING,
         idle=[("state", "self", "sit"), ("every", 23000, [("emote", "self", "cry"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="huddle_glubbub", name="Oracle Glubbub", subname="", look="murloc_purple", level=24, role="ambient",
         at="huddle_2", facing=4.2, phase=LANDING,
         idle=[("state", "self", "sit"), ("every", 31000, [("visual", "self", 35426), ("sound", "self", "murloc_fidget2")])]),
    dict(key="huddle_grrm", name="Grrmlgrrl the Tidehunter", subname="", look="murloc_slate", scale=1.15, level=30,
         role="ambient", at="huddle_5", facing=3.7, phase=LANDING,
         idle=[("every", 29000, [("emote", "self", "point"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="huddle_sloshy", name="Sloshy", subname="", look="murloc_blue", scale=0.6, level=5, role="ambient",
         at="huddle_3", facing=3.0, phase=LANDING,
         idle=[("state", "self", "sleep"), ("every", 15000, [("sound", "self", "baby_murloc")])]),
    dict(key="refugee", name="Saltscar Refugee", plural="refugees", look="murloc_grey", looks=["murloc_green", "murloc_bronze"],
         level=20, role="ambient", at=["huddle_4", "huddle_6"], phase=LANDING,
         idle=[("state", "self", "sleep"), ("every", 27000, [("sound", "self", "murloc_wound")])]),

    # the camp's own (from the arrival): Mrrgasha's crab, and the freed fry (from 7.16)
    dict(key="snapper", name="Snapper", subname="Mrrgasha's Crab", look=641, scale=0.6, level=30, role="ambient",
         at="crab", facing=5.3, phase=CAMP, idle=[("every", 21000, [("sound", "self", 1229)])]),
    dict(key="freed_home", name="Freed Fry", plural="freed fry", look="murloc_blue",
         looks=["murloc_pale", "murloc_gold", "murloc_orange"], scale=0.5, level=3, role="ambient",
         at=["fry_home_1", "fry_home_2", "fry_home_3", "fry_home_4", "fry_home_5"], wander=2.5, phase=FREED,
         idle=[("every", 19000, [("emote", "self", "dance"), ("sound", "self", "baby_murloc")])]),

    # Theramore's harbour (only while 7.01 is in the log): Blrrgl's crate, and who's about to open it
    dict(key="dock_a", name="Dockhand", subname="", look=3734, level=30, side="neutral", role="ambient", language="common",
         at="dock_a", facing=4.12, respawn=45, phase=DOCK, idle=[("every", 17000, [("emote", "self", "talk")])]),
    dict(key="dock_b", name="Dockhand", subname="", look=5004, level=30, side="neutral", role="ambient", language="common",
         at="dock_b", facing=5.23, respawn=45, phase=DOCK, idle=[("every", 23000, [("emote", "self", "laugh")])]),
    dict(key="blrrgl_crate", name="Supply Crate", subname="", look=28476, level=1, side="neutral", role="ambient",
         at="crate", facing=1.6, respawn=45, unit_flags=0x02000002, phase=DOCK,
         idle=[("every", 9000, [("sound", "self", "murloc_fidget")])],
         watch=(28, [("say", "dock_a", "Heavy one, this. What's in it, bricks?", "talk"), ("wait", 2500),
                     ("emote", "dock_b", "laugh"), ("say", "dock_b", "Bricks don't gurgle, Tam.", "point"), ("wait", 2500),
                     ("emote", "dock_a", "attack"), ("sound", "self", "murloc_wound"), ("wait", 1500),
                     ("emote", "dock_a", "exclamation"), ("say", "dock_a", "...Did that crate just squeak at me?", "question"),
                     ("wait", 2000), ("sound", "self", "murloc_alert"), ("visual", "self", 52878), ("wait", 1500),
                     ("say", "dock_b", "Fetch the crowbar. Let's have a look at our squeaky crate.", "point"),
                     ("move", "dock_b", "crowbar", "walk"), ("wait", 2500),
                     ("jump", "self", "crate_splash"), ("sound", "self", "splash_big"), ("wait", 1000),
                     ("summon", "blrrgl_swim", "blrrgl_up", 40), ("credit", ARRIVAL),
                     ("yell", "dock_a", "It jumped! The crate JUMPED in!", "exclamation"),
                     ("emote", "blrrgl_swim", "cheer"), ("sound", "blrrgl_swim", "murloc_aggro"), ("wait", 2000),
                     ("say", "dock_b", "Crates don't jump, Tam. Crates don't jump.", "no"),
                     ("summon", "shellback_ferry", "ferry", 20), ("sound", "self", "splash_big"), ("wait", 2000),
                     ("move", "blrrgl_swim", "ferry", "run"), ("wait", 3000),
                     ("teleport", "player", "landing", 3.64), ("move", "dock_b", "dock_b", "walk"),
                     ("despawn", "self")], 60000)),
    dict(key="blrrgl_swim", name="Blrrgl the Snatcher", subname="", look="murloc_green", level=24, role="ambient",
         summoned=True),
    dict(key="shellback_ferry", name="Grandmother Shellback", subname="", look=29161, scale=4.0, level=60, role="ambient",
         unit_flags=0x02000002, summoned=True, idle=[("every", 6000, [("sound", "self", "splash_big")])]),

    # King Mrrgum's court
    dict(key="king", name="King Mrrgum the Bloated", subname="King of the Mirefin", look="murloc_gold", scale=1.8, level=40,
         side="neutral", role="ambient", health=10.0, at="king_seat", facing=4.71, phase=KING,
         idle=[("state", "self", "sit"), ("every", 37000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget")])]),
    dict(key="king_sick", name="King Mrrgum the Bloated", subname="King of the Mirefin", look="murloc_green", scale=1.8,
         level=40, side="neutral", role="enemy", health=6.0, damage=1.3, at="king_seat", facing=4.71, respawn=120, phase=SICK,
         abilities=[(6533, 15000), (12054, 11000)],
         watch=(9, [("face", "self", "player"), ("emote", "self", "beg"), ("sound", "self", "murloc_wound"), ("wait", 2000),
                    ("emote", "self", "cry"), ("wait", 2500), ("face", "self", "court")], 20000),
         idle=[("every", 17000, [("emote", "self", "cry"), ("sound", "self", "murloc_wound")])]),
    dict(key="courtguard", name="Mirefin Courtguard", plural="courtguards", look="murloc_bronze", scale=1.15, level=38,
         side="neutral", role="ambient", at=["guard_1", "guard_2"], facing=4.71,
         idle=[("every", 41000, [("emote", "self", "roar"), ("sound", "self", "murloc_aggro_old")])]),
    dict(key="courtier", name="Mirefin Courtier", plural="courtiers", look=652, looks=[11293], level=(36, 37),
         side="neutral", role="ambient", at=["crowd_1", "crowd_3"], facing=1.57),
    dict(key="courtier_b", name="Mirefin Courtier", plural="courtiers", look=5286, looks=[11293], level=(36, 37),
         side="neutral", role="ambient", at=["crowd_2", "crowd_4"], facing=1.57),
    dict(key="fry_a", name="Tribute Fry", plural="tribute fry", look="murloc_blue", scale=0.5, level=4, role="ambient",
         at="line_1", facing=1.57, phase=FRY, idle=[("every", 29000, [("emote", "self", "shy")])]),
    dict(key="fry_slow", name="Tribute Fry", plural="tribute fry", look="murloc_pale", scale=0.42, level=3, role="ambient",
         at="line_3", facing=1.57, phase=FRY,
         idle=[("every", 21000, [("emote", "self", "cry"), ("sound", "self", "baby_murloc")])]),
    dict(key="fry_line", name="Tribute Fry", plural="tribute fry", look="murloc_green", looks=["murloc_orange"], scale=0.48,
         level=3, role="ambient", at=["line_2", "line_4"], facing=1.57, phase=FRY,
         idle=[("every", 26000, [("emote", "self", "shy")])]),
    dict(key="pen_fry", name="Tribute Fry", plural="tribute fry", look="murloc_grey",
         looks=["murloc_blue", "murloc_pale", "murloc_ice"], scale=0.45, level=3, role="ambient",
         at=["pen_1", "pen_2", "pen_3", "pen_4", "pen_5", "pen_6"], facing=5.7, respawn=60, phase=FRY,
         greeting="Mrgl...? Fish? You have fish? Shh. Shh!",
         watch=(6, [("face", "self", "player"), ("emote", "self", "beg"), ("sound", "self", "baby_murloc")], 25000),
         idle=[("every", 14000, [("emote", "self", "beg"), ("sound", "self", "baby_murloc")])]),
    dict(key="mother_a", name="Mirefin Mother", plural="mothers", look="murloc_slate", level=32, side="neutral",
         role="ambient", at="mother_1", facing=2.29, idle=[("every", 33000, [("emote", "self", "cry")])]),
    dict(key="mother_b", name="Mirefin Mother", plural="mothers", look="murloc_bronze", level=32, side="neutral",
         role="ambient", at=["mother_2", "mother_3"], facing=2.29, idle=[("every", 41000, [("emote", "self", "beg")])]),
    dict(key="brrsha", name="Mother Brrsha", subname="Eldest of the Mothers", look="murloc_pale", scale=0.85, level=36,
         side="neutral", role="quest", at="brrsha", facing=4.23,
         greeting="The little ones bring him fish. We bring him the little ones. ...What kind of mothers are we?",
         idle=[("state", "self", "sit"), ("every", 45000, [("emote", "self", "cry"), ("sound", "self", "murloc_fidget2")])]),
    # the court as it goes on every day (always there, so it moves whoever of the court a murloc sees)
    dict(key="court_life", name="Court of the Mirefin", look="trigger", level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, at="court",
         idle=[("every", 32000, [("move", "fry_a", "throne_front", "walk"), ("wait", 5000), ("emote", "fry_a", "bow"),
                                 ("emote", "king", "eat"), ("sound", "king", 1186), ("wait", 1500), ("emote", "king", "talk"),
                                 ("sound", "fry_a", "baby_murloc"), ("move", "fry_a", "line_1", "walk")]),
               ("every", 47000, [("move", "courtguard", "kick_spot", "walk"), ("wait", 5500), ("emote", "courtguard", "attack"),
                                 ("jump", "fry_slow", "fry_water"), ("sound", "fry_slow", "splash_small"),
                                 ("sound", "fry_slow", "baby_murloc"), ("wait", 2500), ("emote", "mother_b", "cry"),
                                 ("move", "courtguard", "guard_1", "walk"), ("wait", 6000), ("move", "fry_slow", "line_3", "walk")])]),
    dict(key="murlorga_scout", name="Murlorga", subname="", look="murloc_orange", level=18, role="ambient", summoned=True,
         watch=(10, [("face", "self", "throne"), ("wait", 3000), ("emote", "self", "kneel"), ("object", "ladle", "scout_ladle", 90),
                     ("sound", "self", 1186), ("wait", 3000), ("face", "self", "player"), ("emote", "self", "no"),
                     ("sound", "self", "murloc_fidget2"), ("wait", 2500), ("face", "self", "throne"), ("state", "self", "kneel")],
                600000)),
    dict(key="blrrgl_bag", name="Blrrgl the Snatcher", subname="", look="murloc_green", level=24, role="ambient", summoned=True,
         watch=(10, [("emote", "self", "point"), ("object", "bag", "bag_spot", 120), ("emote", "self", "laugh"),
                     ("sound", "self", 120)], 30000),
         idle=[("every", 11000, [("emote", "self", "beg"), ("sound", "self", 120)])]),
    dict(key="grrm_reeds", name="Grrmlgrrl the Tidehunter", subname="", look="murloc_slate", scale=1.15, level=30,
         role="ambient", summoned=True,
         watch=(15, [("face", "self", "player"), ("emote", "self", "point"), ("face", "self", "mirefin"),
                     ("emote", "self", "roar"), ("sound", "self", "murloc_aggro")], 60000),
         idle=[("every", 23000, [("face", "self", "mirefin"), ("emote", "self", "flex")])]),
    dict(key="mrrk_mud", name="Mrrk Sharpfin", subname="", look="murloc_orange", level=37, role="quest", at="mud",
         facing=0.95, greeting="I am not stuck. I am resting. Low. ...Go away.",
         idle=[("state", "self", "sit"), ("every", 19000, [("emote", "self", "beg"), ("sound", "self", "murloc_wound")])]),
    dict(key="blrrgl_dune", name="Blrrgl the Snatcher", subname="", look="murloc_green", level=24, role="ambient",
         summoned=True,
         watch=(12, [("face", "self", "theramore"), ("emote", "self", "point"),
                     ("say", "self", "See? The white tower! The white walls! The stone town!", "point", "murloc_fidget"),
                     ("wait", 3000), ("face", "self", "view_swamp"), ("emote", "self", "question"), ("wait", 2000),
                     ("face", "self", "theramore"), ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"),
                     ("wait", 2000), ("state", "self", "sit"), ("sound", "self", "murloc_wound"), ("wait", 2000),
                     ("emote", "self", "cry")], 120000)),

    # Gorlak Brokenchain, in the stream below Brackenwall (friendly to murlocs: see the report on his faction)
    dict(key="gorlak", name="Gorlak Brokenchain", subname="", look=1332, level=45, side="tribe", language="orcish",
         role="quest", at="gorlak", facing=1.41,
         greeting="Hrm. A fish that walks. Sit, if you want. Don't talk. You can't anyway. Neither can I, much.",
         idle=[("state", "self", "fish"), ("every", 61000, [("sound", "self", "splash_small")])]),
    dict(key="gorlak_bay", name="Gorlak Brokenchain", subname="", look=1332, level=45, side="tribe", language="orcish",
         role="ambient", summoned=True, idle=[("every", 20000, [("face", "self", "deep_bay")])]),
    dict(key="grrm_soldier", name="Grrmlgrrl the Tidehunter", subname="", look="murloc_slate", scale=1.15, level=30,
         role="ambient", summoned=True),
    dict(key="song_grrm", name="Grrmlgrrl the Tidehunter", subname="", look="murloc_slate", scale=1.15, level=30,
         role="ambient", summoned=True),
    dict(key="song_murlorga", name="Murlorga", subname="", look="murloc_orange", level=18, role="ambient", summoned=True),
    dict(key="song_glubbub", name="Oracle Glubbub", subname="", look="murloc_purple", level=24, role="ambient", summoned=True),
    dict(key="song_blrrgl", name="Blrrgl the Snatcher", subname="", look="murloc_green", level=24, role="ambient",
         summoned=True),

    # Apprentice Lysander, practising on the beach north of Sentry Point
    dict(key="lysander", name="Apprentice Lysander", subname="Theramore Apprentice", look=3947, level=35, side="tribe",
         language="common", role="quest", at="lysander", facing=5.29,
         greeting="Oh! Hello! Hello. Mrgl? Is that how you... no. Hello! I'm Lysander. I'm going to understand you one day.",
         idle=[("every", 29000, [("emote", "self", "spell"), ("visual", "self", 32992)]),
               ("every", 47000, [("emote", "self", "question")])]),
    # the lighthouse keeper, on the rock outside Theramore's walls
    dict(key="keeper", name="Old Wren", subname="Lighthouse Keeper", look=4491, level=30, side="tribe", language="common",
         role="ambient", at="keeper", facing=3.33,
         idle=[("every", 53000, [("face", "self", "lamp"), ("emote", "self", "point")])]),

    # summoned by scenes
    dict(key="vision_chef", name="Goblin Chef", subname="", look=7346, level=30, side="tribe", language="common",
         role="ambient", unit_flags=0x02000002, summoned=True, idle=[("every", 4000, [("visual", "self", 35838)])]),
    dict(key="freed_fry", name="Tribute Fry", plural="tribute fry", look="murloc_grey",
         looks=["murloc_blue", "murloc_pale", "murloc_green"], scale=0.45, level=3, role="ambient", summoned=True,
         watch=(15, [("follow", "self"), ("sound", "self", "baby_murloc")], 600000),
         idle=[("every", 13000, [("sound", "self", "baby_murloc")])]),
    dict(key="bubbles", name="Bubbles", look="trigger", level=1, role="ambient", unit_flags=0x02000002, summoned=True,
         idle=[("every", 3000, [("visual", "self", 59562)])]),
]

# -- things ---------------------------------------------------------------------------------------------

CORAL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\Coral01.mdx"
EGG = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_01.mdx"
MOUND = "World\\Azeroth\\Duskwood\\PassiveDoodads\\Tombs\\DirtMound01.mdx"
LOG = "World\\Azeroth\\SwampOSorrow\\PassiveDoodads\\TreeLogs\\SwampTreeLog01.mdx"
FISH = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadBlue.mdx"

OBJECTS = [
    # the camp (from the arrival)
    dict(key="hut", model="murloc_hut", name="Stilt Hut", at=["hut_w", "hut_s"], kind="doodad", scale=0.9, facing=0.6,
         phase=CAMP),
    dict(key="hut2", model="murloc_hut2", name="Stilt Hut", at="hut_ne", kind="doodad", scale=0.8, facing=2.2, phase=CAMP),
    dict(key="campfire", model="campfire", name="Campfire", at="hub", kind="doodad", phase=CAMP),
    dict(key="cookpot", model=6849, name="Murlorga's Pot", at="cookpot", kind="doodad", scale=1.1, phase=CAMP),
    dict(key="hollow_log", model=LOG, name="Hollow Log", at="blrrgl_log", kind="doodad", scale=0.6, facing=1.0, phase=CAMP),
    dict(key="altar", model="murloc_altar", name="Saltscar Altar", at="altar", kind="doodad", scale=0.5, phase=CAMP),
    dict(key="nets", model=6808, name="Drying Nets", at="nets", kind="doodad", scale=0.6, facing=2.0, phase=CAMP),
    dict(key="fish_rack", model=6705, name="Fish Rack", at="fish_rack", kind="doodad", scale=0.8, facing=2.0, phase=CAMP),
    dict(key="anvil", model=166, name="Krrgl's Anvil", at="anvil", kind="doodad", scale=0.8, facing=1.5, phase=CAMP),
    dict(key="big_pot", model=216, name="Brackenwall Cauldron", at="big_pot", kind="doodad", scale=1.0, phase=("from", "ch7_pots")),
    # the reed beds round the islets (7.03)
    dict(key="reeds", model=370, name="Mire Reeds", kind="loot", loot=[("reed", 1, 2)], quest="ch7_reeds", scale=0.9,
         at=["reed_1", "reed_2", "reed_3", "reed_4", "reed_5", "reed_6", "reed_7", "reed_8"]),

    # King Mrrgum's court
    dict(key="throne", model=7594, name="Throne of Shells", at="throne", kind="doodad", scale=1.0, facing=4.71),
    dict(key="court_shells", model=6851, name="Heaped Shells", at=["shell_1", "shell_2", "shell_3", "shell_4"],
         kind="doodad", scale=1.6),
    dict(key="court_coral", model=CORAL, name="Coral", at=["shell_3", "shell_4"], kind="doodad", scale=0.6),
    dict(key="court_fire", model=408, name="Cookfire", at=["court_fire_1", "court_fire_2"], kind="doodad"),
    dict(key="pen", model=2107, name="Fry Pen", at="pen", kind="doodad", scale=0.55, facing=1.57),
    dict(key="pen_gate", model=2127, name="Fry-Pen Gate", at="pen_gate", kind="use", quest="ch7_pen", facing=1.57,
         phase=FRY, goal="Fry pen opened",
         beats=[("take", "pen_key", 1), ("object", "pen_open", "gate_out_1", 120, 0.0),
                ("despawn", "pen_fry"), ("summon", "freed_fry", "pen_1", 420), ("summon", "freed_fry", "pen_2", 420),
                ("wait", 700), ("despawn", "pen_fry"), ("summon", "freed_fry", "pen_3", 420),
                ("summon", "freed_fry", "pen_4", 420), ("wait", 700), ("despawn", "pen_fry"),
                ("summon", "freed_fry", "pen_5", 420), ("summon", "freed_fry", "pen_6", 420), ("wait", 700),
                ("despawn", "pen_fry"), ("summon", "freed_fry", "gate_out_1", 420), ("summon", "freed_fry", "gate_out_2", 420),
                ("wait", 700), ("despawn", "pen_fry"), ("wait", 700), ("despawn", "pen_fry")]),
    dict(key="larder", model=6705, name="Mirefin Larder", kind="loot", loot=[("dried_fish", 1, 2)], quest="ch7_fence",
         at=["larder_1", "larder_2"], facing=1.57),
    dict(key="hoard_chest", model=259, name="King Mrrgum's Hoard", kind="loot", loot=[("shiny", 2, 2)], quest="ch7_hoard",
         at="hoard_1", facing=4.71),
    dict(key="hoard_heap", model=2614, name="Heap of Shinies", kind="loot", loot=[("shiny", 2, 2)], quest="ch7_hoard",
         at=["hoard_2", "hoard_3", "hoard_4"]),
    dict(key="casket", model=4192, name="Cold Shell Casket", kind="loot", loot=[("signet", 1, 1)], quest="ch7_signet",
         at="casket", scale=0.7, facing=4.71),
    dict(key="king_table", model=564, name="The King's Table", at="table", kind="use", quest="ch7_feast", consumable=False,
         scale=1.4, facing=4.71, goal="Stew set before the king",
         beats=[("take", "stew_bowl", 1), ("object", "covered_bowl", "bowl_spot", 90), ("emote", "king", "talk"),
                ("sound", "king", "murloc_fidget"), ("wait", 1500), ("emote", "king", "eat"), ("sound", "king", 1186),
                ("wait", 1200), ("emote", "king", "eat"), ("sound", "king", 1186), ("wait", 1200), ("emote", "king", "eat"),
                ("wait", 2000), ("aura", "king", "green_king"), ("sound", "king", "murloc_wound_crit"), ("wait", 1500),
                ("state", "king", "none"), ("jump", "king", "king_fall"), ("state", "king", "dead"), ("sound", "king", 1267),
                ("wait", 800), ("move", "courtier", "chaos_1", "run"), ("move", "courtier_b", "chaos_2", "run"),
                ("emote", "courtguard", "exclamation"), ("sound", "courtguard", "murloc_alert"),
                ("object", "key_glint", "key_spot", 30), ("give", "pen_key", 1), ("wait", 7000),
                ("move", "courtier", "crowd_1", "walk"), ("move", "courtier_b", "crowd_2", "walk"), ("wait", 8000),
                ("state", "king", "none"), ("move", "king", "king_seat", "walk"), ("wait", 3000), ("face", "king", "court"),
                ("state", "king", "sit")]),
    dict(key="mud_mound", model=MOUND, name="Sucking Mud", at=["mud_1", "mud_2"], kind="doodad", scale=0.7),
    # the lighthouse keeper's doorstep (7.22)
    dict(key="keeper_step", model=6038, name="Keeper's Doorstep", at="keeper_step", kind="use", quest="ch7_keeper",
         consumable=False, goal="Pearl left on the doorstep",
         beats=[("take", "gift_pearl", 1), ("object", "pearl_on_step", "step_pearl", 180),
                ("wait", 4000), ("move", "keeper", "keeper_out", "walk"), ("wait", 3000), ("emote", "keeper", "kneel"),
                ("wait", 2000), ("say", "keeper", "Well, now. Who left you here, then?", "question"), ("wait", 2500),
                ("face", "keeper", "lamp"), ("emote", "keeper", "point"), ("visual", "keeper", 56494), ("wait", 3000),
                ("emote", "keeper", "cheer"), ("wait", 3000), ("move", "keeper", "keeper", "walk")]),
    # the deepest water of Dustwallow Bay (7.09)
    dict(key="deep_water", model=42, name="The Deepest Water", at="deep_bay", kind="use", quest="ch7_chain",
         consumable=False, goal="Manacle left in the deep",
         beats=[("take", "manacle", 1), ("object", "sunk_manacle", "manacle_rest", 1800), ("summon", "bubbles", "deep_bay", 15),
                ("face", "gorlak_bay", "deep_bay"), ("state", "gorlak_bay", "kneel")]),
    # the pumpkin patch beside the haunted manor (7.20)
    dict(key="patch", model=6325, name="Pumpkin Patch", at="patch", kind="doodad", scale=0.8),
    dict(key="pumpkin", model=6351, name="Witch Hill Pumpkin", at=["pumpkin_2", "pumpkin_3"], kind="use", quest="ch7_pumpkin",
         beats=[("give", "pumpkin", 1), ("summon", 23555, "husk_1", 60), ("summon", 23555, "husk_2", 60)]),
    # Brackenwall's cookfires (7.11)
    dict(key="cauldron", model=216, name="Brackenwall Cauldron", kind="loot", loot=[("cauldron", 1, 1)], quest="ch7_pots",
         at=["pot_1", "pot_2", "pot_3", "pot_4"]),
    # Gorlak's place in the reeds
    dict(key="gorlak_fire", model=408, name="Small Fire", at="gorlak_fire", kind="doodad", scale=0.8),
    # Lysander's beach (7.12, 7.13)
    dict(key="wand", model=2455, name="Lysander's Wand", kind="loot", loot=[("wand", 1, 1)], quest="ch7_spell", scale=0.4,
         at="wand_spot", facing=0.8),
    dict(key="notes", model=163, name="Lysander's Notes", kind="loot", loot=[("page", 1, 1)], quest="ch7_pages", scale=1.2,
         at=["page_1", "page_2", "page_3", "page_4", "page_5", "page_6", "page_7", "page_8"]),

    # set out by scenes
    dict(key="sand_crate", model=275, name="Drawing in the Sand", kind="doodad", scale=0.25),
    dict(key="sand_city", model=5671, name="Drawing in the Sand", kind="doodad", scale=0.2),
    dict(key="sand_banner", model=5111, name="Drawing in the Sand", kind="doodad", scale=0.25),
    dict(key="sand_tent", model=2352, name="Drawing in the Sand", kind="doodad", scale=0.15),
    dict(key="sand_sack", model=2890, name="Drawing in the Sand", kind="doodad", scale=0.4),
    dict(key="sand_spear", model=2067, name="Drawing in the Sand", kind="doodad", scale=0.4),
    dict(key="sand_throne", model=7594, name="Drawing in the Sand", kind="doodad", scale=0.15),
    dict(key="sand_pumpkin", model=60, name="Drawing in the Sand", kind="doodad", scale=0.3),
    dict(key="sand_skull", model=217, name="Drawing in the Sand", kind="doodad", scale=0.6),
    dict(key="hut_post", model=1508, name="Hut Post", kind="doodad", scale=0.6),
    dict(key="reed_wall", model=369, name="Reed Wall", kind="doodad", scale=0.9),
    dict(key="old_net", model=6808, name="Torn Net", kind="doodad", scale=0.4),
    dict(key="web", model=364, name="Spider Web", kind="doodad", scale=0.5),
    dict(key="new_net", model=6808, name="Silk Net", kind="doodad", scale=0.6),
    dict(key="raptor_meat", model=14, name="Raptor Meat", kind="doodad", scale=0.8),
    dict(key="fish_toss", model=FISH, name="Fish", kind="doodad", scale=0.8),
    dict(key="manacle_shown", model=181, name="Broken Manacle", kind="doodad", scale=0.4),
    dict(key="sunk_manacle", model=181, name="Gorlak's Manacle", kind="doodad", scale=0.5),
    dict(key="shell_prop", model=6851, name="Mudrock Shell", kind="doodad", scale=0.8),
    dict(key="empty_book", model=470, name="Empty Book", kind="doodad", scale=1.0),
    dict(key="covered_bowl", model=7983, name="Indescribable Stew", kind="doodad", scale=1.4),
    dict(key="key_glint", model=2614, name="Fry-Pen Key", kind="doodad", scale=0.2),
    dict(key="pen_open", model=2127, name="Open Gate", kind="doodad", scale=1.0),
    dict(key="bag", model=2890, name="Blrrgl's Bag", kind="doodad", scale=0.6),
    dict(key="pearl_on_step", model="great_pearl", name="Pearl", kind="doodad", scale=0.06),
    dict(key="worn_pumpkin", model=60, name="Pumpkin Hat", kind="doodad", scale=0.7),
    dict(key="ladle", model=7983, name="Murlorga's Ladle", kind="doodad", scale=0.9),
    dict(key="vision_boat", model=124, name="Boat in the Fog", kind="doodad", scale=1.0),
    dict(key="vision_flag", model=7589, name="Red Sail", kind="doodad", scale=1.4),
    dict(key="vision_egg", model=EGG, name="Glowing Egg", kind="doodad", scale=0.35),
    dict(key="war_drum", model=4676, name="Gorlak's War-Drum", kind="doodad", scale=0.9),
    dict(key="song_pot", model=216, name="Murlorga's New Pot", kind="doodad", scale=0.9),
    dict(key="small_pot", model=6849, name="Murlorga's Little Pot", kind="doodad", scale=0.5),
]

# -- items ---------------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for
    dict(key="reed", name="Mire Reed Bundle", icon="item:2452", stack=10),
    dict(key="dried_fish", name="Dried Mirefin Fish", icon="item:21072", stack=6, description="The king's. Was the king's."),
    dict(key="flank", name="Bloodfen Raptor Flank", icon="item:12184", stack=10),
    dict(key="silk", name="Darkmist Silk Gland", icon="item:3412", stack=8),
    dict(key="manacle", name="Gorlak's Manacle", icon="item:3156",
         description="Half a ring of black iron, worn smooth on the inside by twenty years of an orc's wrist."),
    dict(key="cauldron", name="Brackenwall Cauldron", icon="item:1987", stack=4, description="Big. Very big. Orc big."),
    dict(key="wand", name="Lysander's Wand", icon="item:3425", description="Still warm. Still smells of burnt feathers."),
    dict(key="page", name="Lysander's Note", icon="item:916", stack=8),
    dict(key="shell", name="Mudrock Shell", icon="item:5795", stack=8),
    dict(key="stew_bowl", name="Covered Bowl of Indescribable Stew", icon="item:733",
         description="Murlorga will not say what is in it. The lid is warm. The lid is moving."),
    dict(key="pen_key", name="Fry-Pen Key", icon="key"),
    dict(key="shiny", name="King Mrrgum's Shiny", icon="item:779", stack=8),
    dict(key="signet", name="Ilyssa's Signet", icon="item:942",
         description="A naga's ring, cold enough to frost the inside of your bag. It is never warm."),
    dict(key="pumpkin", name="Witch Hill Pumpkin", icon="item:2846"),
    dict(key="ember", name="Firemane Ember", icon="item:6655", stack=6),
    dict(key="gift_pearl", name="Pearl for the Keeper", icon="pearl", description="The Elder's best pearl. He chose it a long time."),
    dict(key="rope", name="Knotted Kelp Rope", icon="item:16743", description="Mrrk's. He was going to climb something."),
    dict(key="sketch", name="Lysander's Sketch", icon="item:2720",
         description="A drawing of a murloc, done with great care and no idea what murlocs look like. It is you."),
    dict(key="war_drum", name="Gorlak's Drum", icon="item:29528", aura="drumming",
         description="A small drum of raptor hide. Gorlak beat it for the tribe's going."),

    # rewards (levels 37 to 40: the game's quests' greens at these levels)
    dict(key="chain_mail", name="Brokenchain Bindings", kind="armor:mail:wrist", quality=2, level=37,
         stats=[("str", 5), ("sta", 5)]),
    dict(key="chain_leather", name="Reed-Wrapped Bracers", kind="armor:leather:wrist", quality=2, level=37,
         stats=[("agi", 5), ("sta", 5)]),
    dict(key="chain_cloth", name="Fisherman's Cuffs", kind="armor:cloth:wrist", quality=2, level=37,
         stats=[("int", 5), ("spi", 4)]),
    dict(key="deserter_sword", name="Deserter's Cutlass", kind="weapon:sword", quality=2, level=38,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="deserter_bow", name="Deserter's Longbow", kind="weapon:bow", quality=2, level=38, stats=[("agi", 5), ("sta", 3)]),
    dict(key="deserter_wand", name="Sentry's Spare Wand", kind="weapon:wand", quality=2, level=38,
         stats=[("int", 4), ("spi", 3)]),
    dict(key="shell_mail", name="Mudrock Shell Hauberk", kind="armor:mail:chest", quality=2, level=38,
         stats=[("str", 9), ("sta", 8)]),
    dict(key="shell_leather", name="Mudrock-Plated Jerkin", kind="armor:leather:chest", quality=2, level=38,
         stats=[("agi", 9), ("sta", 8)]),
    dict(key="shell_cloth", name="Shell-Stitched Robe", kind="armor:cloth:chest", quality=2, level=38,
         stats=[("int", 9), ("spi", 7)]),
    dict(key="apprentice_robe", name="Apprentice's Spare Robe", kind="armor:cloth:legs", quality=2, level=38,
         stats=[("int", 8), ("sta", 6)]),
    dict(key="sentry_cloak", name="Sentry Point Cloak", kind="armor:cloth:back", quality=2, level=38,
         stats=[("agi", 5), ("sta", 5)]),
    dict(key="pen_pendant", name="Fry-Pen Key Pendant", kind="neck", quality=2, level=39, stats=[("sta", 6), ("spi", 5)]),
    dict(key="mothers_knot", name="Mother's Knot", kind="neck", quality=2, level=39, stats=[("str", 5), ("agi", 5)]),
    dict(key="scepter", name="Mrrgum's Scepter", kind="weapon:mace", quality=2, level=40, stats=[("int", 7), ("sta", 6)]),
    dict(key="throne_breaker", name="Throne-Breaker", kind="weapon:spear", quality=2, level=40,
         stats=[("str", 12), ("sta", 10)],
         description="Grrmlgrrl's coral, Krrgl's shell-edge. The fourth of the tribe's spears."),
    dict(key="fin_blade", name="Courtguard's Fin-Blade", kind="weapon:dagger", quality=2, level=40,
         stats=[("agi", 7), ("sta", 5)]),
    dict(key="ring_int", name="Mrrgum's Second-Best Ring", kind="ring", quality=2, level=40, stats=[("int", 6), ("sta", 6)]),
    dict(key="ring_agi", name="Band of Shinies", kind="ring", quality=2, level=40, stats=[("agi", 6), ("sta", 6)]),
    dict(key="ring_str", name="Pearl-Crusted Knuckle", kind="ring", quality=2, level=40, stats=[("str", 6), ("sta", 6)]),
    dict(key="seeing_stone", name="Glubbub's Seeing-Stone", kind="neck", quality=2, level=40, stats=[("int", 7), ("spi", 6)]),
    dict(key="cold_choker", name="Cold-Shell Choker", kind="neck", quality=2, level=40, stats=[("str", 7), ("sta", 6)]),
    dict(key="fin_gloves", name="Singed-Fin Gloves", kind="armor:cloth:hands", quality=2, level=39,
         stats=[("int", 7), ("sta", 5)]),
    dict(key="ember_grips", name="Ember-Scorched Grips", kind="armor:leather:hands", quality=2, level=39,
         stats=[("agi", 7), ("sta", 5)]),
    dict(key="firemane_gauntlets", name="Firemane-Scale Gauntlets", kind="armor:mail:hands", quality=2, level=39,
         stats=[("str", 7), ("sta", 5)]),
    dict(key="rider_boots", name="Shellback Rider's Boots", kind="armor:mail:feet", quality=2, level=40,
         stats=[("str", 8), ("sta", 7)]),
    dict(key="mire_boots", name="Mire-Walker's Boots", kind="armor:leather:feet", quality=2, level=40,
         stats=[("agi", 8), ("sta", 7)]),
    dict(key="reed_sandals", name="Reed-Woven Sandals", kind="armor:cloth:feet", quality=2, level=40,
         stats=[("int", 8), ("spi", 6)]),
]

# -- auras ---------------------------------------------------------------------------------------------

AURAS = [
    dict(key="mud_mask", name="Mud Mask", kind="disguise", look=652, seconds=600, icon=42365,
         text="Murlorga's mud, all over your face. You are a Mirefin now. An ugly one."),
    dict(key="green_king", name="Indescribable Stew", kind="disguise", look="murloc_green", scale=1.8, seconds=300),
    dict(key="lysander_murloc", name="Misfired Spell", kind="disguise", look="murloc_grey", seconds=15),
    dict(key="drumming", name="Gorlak's Drum", kind="mark", seconds=15, icon=35475,
         text="Boom. Boom. Boom-boom. The tribe is going."),
]

# -- more of others' people, and the game's, here -----------------------------------------------------------

SPAWNS = [
    # who was already here when the turtle landed: Grandmother Shellback, always in the bay; the Elder, until 9.21
    dict(npc="ch0:shellback", at="shellback", facing=4.59),
    dict(npc="ch1:elder", at="elder", facing=5.5, phase=("until", "ch9:ch9_elder")),
    # the camp (the hub kit, bible 17.1)
    dict(npc="ch1:murlorga", at="murlorga", facing=3.93, phase=CAMP),
    dict(npc="ch1:glubbub", at="glubbub", facing=0.93, phase=CAMP),
    dict(npc="ch1:grrmlgrrl", at="grrmlgrrl", facing=2.01, phase=CAMP, state="none"),
    dict(npc="ch1:blrrgl", at="blrrgl", facing=0.89, phase=CAMP),
    dict(npc="ch1:sloshy", at="sloshy", facing=4.47, phase=CAMP, wander=3.0),
    dict(npc="ch1:brrgmrk", at="t_warrior", facing=5.34, phase=CAMP),
    dict(npc="ch1:mrrgasha", at="t_hunter", facing=6.04, phase=CAMP),
    dict(npc="ch1:glubba", at="t_priest", facing=0.35, phase=CAMP),
    dict(npc="ch1:fizzmrgl", at="t_mage", facing=1.25, phase=CAMP),
    dict(npc="ch1:slubb", at="t_firstaid", facing=2.41, phase=CAMP),
    dict(npc="ch1:gurgle", at="t_fishing", facing=0.71, phase=CAMP),
    dict(npc="ch1:mrrlglr", at="t_food", facing=2.0, phase=CAMP),
    dict(npc="ch0:krrgl", at="krrgl", facing=1.54, phase=CAMP),
    dict(npc="ch0:mrsha", at="mrsha", facing=0.52, phase=CAMP),
    dict(npc="ch0:brewglub", at="brewglub", facing=0.17, phase=CAMP),
    dict(npc="ch0:grrsh", at="grrsh", facing=1.71, phase=CAMP),
    dict(npc="ch0:mrrsk", at="mrrsk", facing=1.91, phase=CAMP),
    dict(npc="ch0:scrawlgl", at="scrawlgl", facing=1.15, phase=CAMP),
    dict(npc="ch0:fnrrgl", at="fnrrgl", facing=2.06, phase=CAMP),
    dict(npc="ch0:brrkl", at="brrkl", facing=2.13, phase=CAMP),
    dict(npc="ch0:sprokgl", at="sprokgl", facing=0.94, phase=CAMP),
    dict(npc="ch0:mmrglla", at="mmrglla", facing=4.33, phase=CAMP),
    dict(npc="ch0:shimmrl", at="shimmrl", facing=5.57, phase=CAMP),
    dict(npc="ch0:pearlmrgl", at="pearlmrgl", facing=3.14, phase=CAMP),
    dict(npc="ch0:caller", at="caller", facing=3.02, phase=CAMP),
    dict(object="ch0:mailbox", at="mailbox", facing=4.0, phase=CAMP),
]

GRAVEYARDS = [
    dict(at="graveyard", name="the Mire Islets", phase=CAMP, facing=2.71),
]

# -- the quests ------------------------------------------------------------------------------------------

QUESTS = [
    # 7.01: off the boat. The tribe landed on the islets on the turtle's back; Blrrgl's crate went to
    # Theramore on the supply ship. The arrival: its reward makes the islets the camp.
    dict(key=ARRIVAL, title="Off the Boat", giver="ch1:elder", ender="ch1:elder", level=36, min=34, xp=8, tone="funny",
         prev="ch6:ch6_end", event="Blrrgl fished out of Theramore's harbour", time=120,
         goal="Ride Grandmother Shellback to Theramore's harbour and swim under the end of the pier, where Blrrgl's crate "
              "sits, before the dockhands open it (2 minutes). Then return to the Elder on the Mire Islets.",
         text="1, 2, 3, 4... 4. Where is 5? Where is Blrrgl? ...The box. His box went on the big boat, to the stone town "
              "over the water. The dry-skins will open it! Grandmother will carry you. Swim under their wooden road and "
              "get him out. Quickly!",
         progress="Blrrgl? Where is Blrrgl?",
         reward="Wet, sick and complaining. That is Blrrgl. 5, then. All 5. ...Mm. This mud, these little islands. Ours "
                "now. Saltscar, we stay here.",
         details=["talk", "point", "question"], reward_emotes=["bow", "cheer"],
         accept=[("face", "self", "huddle_1"), ("emote", "self", "point"), ("say", "self", "1.", None, "murloc_fidget"),
                 ("wait", 1200), ("face", "self", "huddle_2"), ("emote", "self", "point"), ("say", "self", "2."),
                 ("wait", 1200), ("face", "self", "huddle_5"), ("emote", "self", "point"), ("say", "self", "3."),
                 ("wait", 1200), ("face", "self", "player"), ("emote", "self", "point"), ("say", "self", "4."),
                 ("wait", 1500), ("emote", "self", "question"), ("sound", "self", "murloc_alert"), ("wait", 1500),
                 ("emote", "self", "kneel"), ("object", "sand_crate", "elder_draw", 40), ("sound", "self", 1194),
                 ("wait", 1500), ("face", "self", "theramore"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1800), ("face", "self", "shellback"), ("sound", "ch0:shellback", 1463), ("emote", "self", "point"),
                 ("wait", 2000), ("sound", "ch0:shellback", "splash_big"), ("teleport", "player", "harbour_out", 1.7),
                 ("wait", 2000), ("face", "self", "landing")],
         complete=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                   ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1000),
                   ("say", "self", "Saltscar. Here.", "talk", "murloc_fidget2"), ("sound", "ch0:shellback", "splash_big"),
                   ("music", 4514), ("wait", 2500), ("emote", "self", "bow")],
         poi=["crate_splash"]),

    # 7.02: where are we?
    dict(key="ch7_where", title="Where Are We?", giver="ch1:blrrgl", ender="ch1:blrrgl", level=36, xp=8, tone="stupid",
         prev=ARRIVAL, explore="dune_top", radius=10,
         goal="Climb the grassy knoll above the beach on the mainland, west of the Mire Islets, and look south.",
         text="This is the stone town. Big white walls, lions, the canals. Yes. The box went round and round and came "
              "back, I know it. I KNOW it. Go up the hill and look. You will see the white walls. Then you say: Blrrgl, "
              "you are right.",
         progress="White walls? Lions? Say it. Say: Blrrgl is right.",
         reward="...Not the stone town? Then where? Where did the box take us? ...Mud. It took us to mud.",
         details=["talk", "point", "flex"], reward_emotes=["question", "cry"],
         accept=[("face", "self", "east_sea"), ("emote", "self", "point"), ("say", "self", "Stone town! That way!", "point",
                                                                              "murloc_fidget"),
                 ("wait", 2000), ("emote", "self", "kneel"), ("object", "sand_city", "blrrgl_draw", 40), ("sound", "self", 1194),
                 ("wait", 2000), ("emote", "self", "cheer"), ("sound", "self", "murloc_fidget2"),
                 ("summon", "blrrgl_dune", "dune_side", 600), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "flex")],
         complete=[("emote", "self", "question"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("state", "self", "sit"),
                   ("emote", "self", "cry"), ("wait", 7000), ("state", "self", "none"), ("emote", "self", "no")],
         poi=["dune_top"]),

    # 7.03: reeds for the huts
    dict(key="ch7_reeds", title="Reeds for the Huts", giver="ch0:krrgl", ender="ch0:krrgl", level=36, xp=8, tone="boring",
         prev=ARRIVAL, items=[("reed", 10)],
         goal="Cut 10 Mire Reed Bundles from the reed beds in the shallows around the Mire Islets.",
         text="A hut needs posts. Posts, I have. A hut needs walls. Walls, I have... this. Look. Nothing. The reeds in the "
              "shallows make walls. 10 bundles. Cut them low, they grow back.",
         progress="Still nothing. I am very good at holding nothing.",
         reward="10! Now the posts have walls, and the walls have holes, and the holes let the wind in. A hut!",
         details=["talk", "point", "no"], reward_emotes=["cheer", "work"],
         accept=[("state", "self", "none"), ("object", "hut_post", "krrgl_post", 30), ("emote", "self", "point"),
                 ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "no"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1500), ("face", "self", "reed_5"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "anvil"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("object", "hut_post", "krrgl_post", 60), ("object", "reed_wall", "krrgl_post", 60),
                   ("emote", "self", "cheer"), ("sound", "self", 4614), ("wait", 1200), ("sound", "self", 4614),
                   ("wait", 1200), ("face", "self", "anvil"), ("state", "self", "work")],
         poi=["reed_1", "reed_4", "reed_7"]),

    # 7.04: the tribute fry (Murlorga goes and looks with you)
    dict(key="ch7_court", title="The Tribute Fry", giver="ch1:murlorga", ender="ch1:murlorga", level=37, xp=8,
         tone="serious", prev="ch7_where", explore="vantage", radius=8,
         goal="Creep into the reeds at the south end of the beach west of the Mire Islets, and watch King Mrrgum's court.",
         text="There are murlocs on the beach over there. Many. A big one on a pile of shells, and small ones bringing "
              "him fish. Small ones. Like ours. Go and look, quietly. I will be there.",
         progress="Did you see them? The little ones?",
         reward="Children. Bringing fish to a king who eats it all, and kicked when they are slow. ...I know what that "
                "is. We all know what that is.",
         details=["talk", "point"], reward_emotes=["no", "cry"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("face", "self", "court_far"), ("emote", "self", "point"),
                 ("sound", "self", "murloc_fidget2"), ("summon", "murlorga_scout", "vantage_m", 600), ("wait", 2500),
                 ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "cry"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 2500), ("face", "self", "cookpot"), ("sound", "self", 973),
                   ("state", "self", "work")],
         poi=["vantage"]),

    # 7.05: food through the fence
    dict(key="ch7_fence", title="Food Through the Fence", giver="ch1:murlorga", ender="ch1:murlorga", level=37, xp=8,
         tone="serious", path="hero", prev="ch7_court", use=[("dried_fish", "pen_fry", 6)],
         goal="Take Dried Mirefin Fish from the larder racks at the north end of King Mrrgum's court, and slip 6 of them "
              "through the fence to the tribute fry in his pen.",
         text="The king eats. The little ones watch him eat. Fish hang on his racks, drying, more than one king can eat... "
              "Take some. Slip them through the fence to the little ones in the pen. 6 fish. Don't be seen.",
         progress="Did they eat? Did they eat all of it?",
         reward="Good. Good. Tomorrow they will be hungry again. ...But not today.",
         details=["talk", "eat", "point"], reward_emotes=["yes", "talk"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("emote", "self", "eat"), ("sound", "self", 1186),
                 ("wait", 1500), ("face", "self", "court_far"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "no"),
                 ("sound", "self", "murloc_fidget"), ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "yes"), ("sound", "self", 973), ("wait", 600),
                   ("sound", "self", 973), ("emote", "self", "talk"), ("wait", 2000), ("state", "self", "work")],
         poi=["larder_1", "pen"]),

    # 7.24: Mrrk in the mire (he gets out, shows you how you did it wrong, and is stuck again)
    dict(key="ch7_mud", title="Mrrk in the Mire", giver="mrrk_mud", ender="mrrk_mud", level=37, xp=8, tone="stupid",
         prev="ch7_court", source="rope", interact=[("mrrk_mud", "Throw him the rope.")], interact_goal="Mrrk pulled out",
         interact_beats=[("state", "self", "none"), ("take", "rope", 1), ("jump", "self", "mud_bank"),
                         ("sound", "self", "splash_big"), ("wait", 1500), ("emote", "self", "rude"),
                         ("say", "self", "Too hard! You pulled too hard!", "point", "murloc_aggro"), ("wait", 2500),
                         ("say", "self", "And too slow! Hard AND slow!", "flex"), ("wait", 2500),
                         ("say", "self", "Look. Watch. Watch how you did it.", "talk"), ("wait", 2000),
                         ("move", "self", "mud", "walk"), ("wait", 3000), ("state", "self", "sit"),
                         ("sound", "self", "murloc_wound"), ("wait", 1500), ("emote", "self", "cry")],
         goal="Throw the Knotted Kelp Rope to Mrrk Sharpfin, stuck in the mud in the shallows south of King Mrrgum's court.",
         text="Don't. Don't look at me. I am not stuck. I am... standing. Low. ...Fine! Take the rope. Pull. And if you "
              "tell Grrmlgrrl, I tell him you cried in the box.",
         progress="Pull! PULL! Not like that!",
         reward="You pulled wrong. All wrong. ...You pulled. Fine. Go away. I like it here.",
         details=["rude", "beg"], reward_emotes=["rude", "no"],
         accept=[("emote", "self", "rude"), ("sound", "self", "murloc_wound"), ("wait", 1500), ("emote", "self", "beg"),
                 ("say", "self", "Pull.", "beg")],
         complete=[("emote", "self", "rude"), ("say", "self", "...Go away.", "no", "murloc_fidget2"), ("wait", 2500),
                   ("emote", "self", "cry")],
         poi=["mud"]),

    # 7.06: raptor meat
    dict(key="ch7_raptor", title="Raptor Meat", giver="ch1:mrrgasha", ender="ch1:mrrgasha", level=37, xp=8, tone="boring",
         prev="ch7_reeds", items=[("flank", 10)], drops={"flank": [(4351, 55), (4352, 55)]},
         goal="Bring Mrrgasha Spearsister 10 Bloodfen Raptor Flanks from the raptors in the hills west of the Mirefin beaches.",
         text="Look at him. Look. Snapper chews a twig. A twig! A hunter's beast, eating twigs. The raptors on the hills "
              "have meat on them. 10 flanks. For him. And a little for me.",
         progress="Still the twig. He is so brave about the twig.",
         reward="Meat! Snapper, look! ...He is pretending he doesn't care. He cares.",
         details=["point", "no", "eat"], reward_emotes=["cheer", "eat"],
         accept=[("face", "self", "crab"), ("emote", "self", "point"), ("sound", "snapper", 1229), ("wait", 1500),
                 ("emote", "self", "no"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "raptors_far"),
                 ("emote", "self", "point"), ("emote", "self", "eat")],
         complete=[("object", "raptor_meat", "crab_meat", 30), ("sound", "self", 1189), ("emote", "self", "cheer"),
                   ("sound", "snapper", 1225), ("wait", 1500), ("face", "self", "crab"), ("emote", "self", "eat")],
         poi=["raptors"]),

    # 7.14: Mudrock shells (Krrgl knocks on Grrmlgrrl)
    dict(key="ch7_shells", title="Mudrock Shells", giver="ch0:krrgl", ender="ch0:krrgl", level=37, xp=8, tone="boring",
         prev="ch7_reeds", items=[("shell", 8)], drops={"shell": [(4397, 60)]},
         goal="Bring Krrgl Coalbelly 8 Mudrock Shells from the Mudrock Spikeshells along the shore south of the Mire Islets "
              "and on the beach below King Mrrgum's court.",
         text="Grrmlgrrl's chest is soft. Everyone's chest is soft. The turtles' backs are hard. Hard is better. 8 shells. "
              "I hit them flat. You wear them.",
         progress="Soft. Still soft.",
         reward="8! Now I hit them. Many times. Then you are hard too.",
         details=["talk", "attack", "yes"], reward_emotes=["cheer", "work"],
         choice=["shell_mail", "shell_leather", "shell_cloth"],
         accept=[("state", "self", "none"), ("move", "self", "grrm_front", "walk"), ("wait", 4000), ("emote", "self", "attack"),
                 ("sound", "self", 1194), ("emote", "ch1:grrmlgrrl", "question"), ("wait", 1200),
                 ("object", "shell_prop", "grrm_front", 20), ("emote", "self", "attack"), ("sound", "self", 1225), ("wait", 1200),
                 ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 1000), ("emote", "self", "yes"), ("wait", 1500),
                 ("move", "self", "krrgl", "walk"), ("wait", 4000), ("face", "self", "anvil"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "attack"), ("sound", "self", 4614), ("wait", 900),
                   ("emote", "self", "attack"), ("sound", "self", 4614), ("wait", 900), ("emote", "self", "attack"),
                   ("sound", "self", 4614), ("wait", 900), ("emote", "self", "cheer"), ("state", "self", "work")],
         poi=["shells_isle", "shells_beach"]),

    # 7.08: the orc in the reeds
    dict(key="ch7_orc", title="The Orc in the Reeds", giver="ch1:elder", ender="gorlak", level=37, xp=8, tone="serious",
         path="hero", prev="ch7_fence", rep=[(76, 500)], rewards=[6887],
         goal="Find the orc who fishes alone in the stream below Brackenwall Village, far west across the marsh. Stay out "
              "of the village itself: its Enforcers warn, then strike.",
         text="From the turtle's back I saw a dry-skin. Green, with tusks. Sitting alone in the reeds by the river, under "
              "the orcs' village. Alone, the way slaves sit. Go and see him. Don't go up into the village... they have spears.",
         progress="What do you want, fish?",
         reward="That mark. On your shoulder. I know that mark... not that one. One like it. Here. Eat.",
         details=["talk", "point", "bow"], reward_emotes=["no", "laugh", "point"],
         accept=[("face", "self", "brackenwall"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "sand_banner", "elder_draw", 30), ("sound", "self", 1194), ("wait", 2000), ("emote", "self", "bow"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "landing")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("wait", 3500), ("emote", "self", "point"),
                   ("wait", 2000), ("object", "manacle_shown", "gorlak_front", 25), ("sound", "self", 1005),
                   ("emote", "self", "laugh"), ("wait", 2500), ("emote", "self", "throw"), ("object", "fish_toss", "toss", 20),
                   ("sound", "self", 1189), ("wait", 2500), ("face", "self", "toss"), ("state", "self", "fish")],
         poi=["gorlak"]),

    # 7.09: Gorlak's chain (he comes to the bay's shore to watch it go)
    dict(key="ch7_chain", title="Gorlak's Chain", giver="gorlak", ender="gorlak", level=37, xp=8, tone="serious", path="hero",
         prev="ch7_orc", source="manacle", objects=[("deep_water", 1)], rep=[(76, 750)],
         choice=["chain_mail", "chain_leather", "chain_cloth"],
         goal="Swim Gorlak's Manacle down to the deepest water of Dustwallow Bay, east of Brackenwall, and leave it on the "
              "bottom. Then go back to Gorlak in the reeds.",
         text="Twenty years I wear this. When the camps fell they cut the chains. Not this. This one I kept... Orcs sink, "
              "fish. You don't. Take it down where the water is darkest, and leave it there.",
         progress="Is it gone?",
         reward="...Gone. Good. Twenty years, and a fish carried it away. Ha. Ha.",
         details=["talk", "point", "no"], reward_emotes=["bow", "laugh"],
         accept=[("state", "self", "none"), ("emote", "self", "eat"), ("sound", "self", 1005), ("wait", 1500),
                 ("emote", "self", "eat"), ("sound", "self", 1005), ("wait", 1500), ("emote", "self", "attack"),
                 ("sound", "self", 1193), ("wait", 1500), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "deep_bay"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "no"),
                 ("summon", "gorlak_bay", "bay_shore", 900), ("wait", 2000), ("face", "self", "toss"), ("state", "self", "fish")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "yes"), ("wait", 2500),
                   ("emote", "self", "kneel"), ("wait", 4000), ("emote", "self", "laugh"), ("wait", 1500),
                   ("face", "self", "toss"), ("state", "self", "fish")],
         poi=["deep_bay"]),

    # 7.07: Darkmist silk
    dict(key="ch7_silk", title="Darkmist Silk", giver="ch0:mmrglla", ender="ch0:mmrglla", level=37, xp=8, tone="boring",
         prev="ch7_raptor", items=[("silk", 8)], drops={"silk": [(4376, 50), (4379, 60), (4378, 50)]},
         goal="Bring Mmrglla Netknot 8 Darkmist Silk Glands from the Darkmist spiders in the woods and the cave north of "
              "Brackenwall Village.",
         text="Nets. Kelp nets break. Reed nets rot. But the spiders in the dark woods, past the orcs' village... their "
              "silk holds a shark. 8 glands. Squeeze them gently. Or not gently. They are dead.",
         progress="No silk, no nets. No nets, no fish.",
         reward="Ooh. Ooh! Sticky. Strong. Mmm.",
         details=["point", "no", "cheer"], reward_emotes=["cheer", "work"],
         accept=[("state", "self", "none"), ("object", "old_net", "mmrglla_front", 30), ("emote", "self", "point"),
                 ("wait", 1500), ("emote", "self", "no"), ("object", "web", "mmrglla_front2", 30), ("emote", "self", "point"),
                 ("wait", 1500), ("sound", "self", "baby_murloc"), ("emote", "self", "cheer"), ("wait", 1500),
                 ("face", "self", "spiders_far"), ("emote", "self", "point"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", "baby_murloc"),
                   ("object", "new_net", "mmrglla_front", 60), ("wait", 2000), ("state", "self", "work")],
         poi=["spiders"]),

    # 7.10: deserters (Grrmlgrrl comes too)
    dict(key="ch7_deserters", title="Deserters", giver="gorlak", ender="gorlak", level=38, xp=8, tone="serious", path="hero",
         prev="ch7_chain", kill=[(5057, 10)], rep=[(76, 250), (72, 250)],
         choice=["deserter_sword", "deserter_bow", "deserter_wand"],
         goal="Kill 10 Theramore Deserters at their camp in the hills of Lost Point, south of Brackenwall Village.",
         text="Men from the stone town over the water. They ran from their own walls. Now they rob orcs on the road, and "
              "they catch your kind in sacks, to sell. 10 of them. Your big one comes too. Good.",
         progress="Still in the hills?",
         reward="10. The road is quieter. Your big one fights like a grunt. I mean it kindly.",
         details=["talk", "point"], reward_emotes=["yes", "salute"],
         accept=[("summon", "grrm_soldier", "grrm_by_gorlak", 120), ("state", "self", "none"), ("emote", "self", "kneel"),
                 ("object", "sand_tent", "gorlak_draw", 40), ("sound", "self", 1194), ("wait", 1800),
                 ("object", "sand_sack", "gorlak_draw2", 40), ("emote", "self", "point"), ("wait", 2000),
                 ("face", "self", "grrm_by_gorlak"), ("face", "grrm_soldier", "player"), ("emote", "grrm_soldier", "yes"),
                 ("emote", "self", "yes"), ("wait", 1500), ("emote", "grrm_soldier", "salute"), ("emote", "self", "salute"),
                 ("wait", 2000), ("face", "self", "toss"), ("state", "self", "fish")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "yes"), ("emote", "self", "laugh"),
                   ("wait", 1500), ("emote", "self", "salute"), ("wait", 2000), ("state", "self", "fish")],
         poi=["deserters"]),

    # 7.11: the pots of Brackenwall (the menace's road)
    dict(key="ch7_pots", title="Pots of Brackenwall", giver="ch1:murlorga", ender="ch1:murlorga", level=38, xp=8,
         tone="funny", path="menace", prev="ch7_orc", items=[("cauldron", 4)], rep=[(76, -350)],
         goal="Steal 4 Brackenwall Cauldrons from the cookfires inside Brackenwall Village. Its Enforcers warn, then strike: "
              "don't linger.",
         text="Look at my pot. Little pot. Little pot for a whole tribe. The orcs in the village up the river have pots "
              "THIS big. 4 of them, I want. They have so many. They will not even notice... They will notice. Run fast.",
         progress="Big ones? Are they big ones?",
         reward="Ohhh. Look at them. Look how much soup. ...Don't tell the orc by the river.",
         details=["talk", "beg"], reward_emotes=["cheer", "laugh"],
         accept=[("state", "self", "none"), ("object", "small_pot", "big_pot", 30), ("emote", "self", "point"),
                 ("wait", 1500), ("emote", "self", "flex"), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("emote", "self", "beg"), ("wait", 1500), ("face", "self", "brackenwall"), ("emote", "self", "point"),
                 ("wait", 1200), ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", 973), ("wait", 600),
                   ("sound", "self", 973), ("emote", "self", "laugh"), ("wait", 2000), ("state", "self", "work")],
         poi=["pot_1", "pot_3"]),

    # 7.22: the lighthouse keeper (the night the turtle came, a light showed her the rocks)
    dict(key="ch7_keeper", title="The Lighthouse Keeper", giver="ch1:elder", ender="ch1:elder", level=37, xp=8,
         tone="serious", path="hero", prev="ch7_where", source="gift_pearl", objects=[("keeper_step", 1)],
         rep=[(72, 250)],
         goal="Leave the Pearl for the Keeper on the lighthouse keeper's doorstep, on the rock east of Theramore's harbour, "
              "outside its walls. Then return to the Elder.",
         text="The night we came, the sea was black and Grandmother was tired. Then a light, over the water. All night. "
              "It showed her the rocks. Somebody lit it. Somebody old, like me. Leave him this, on his step. He will know.",
         progress="Did he find it?",
         reward="Mm. He held it up to his light. Then it was a good pearl.",
         details=["point", "bow"], reward_emotes=["yes", "bow"],
         accept=[("face", "self", "lighthouse"), ("emote", "self", "point"), ("wait", 2000), ("face", "self", "shellback"),
                 ("emote", "self", "point"), ("sound", "ch0:shellback", 1463), ("wait", 1500), ("emote", "self", "bow"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "landing")],
         complete=[("emote", "self", "yes"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "lighthouse"),
                   ("emote", "self", "bow")],
         poi=["keeper_step"]),

    # 7.12: the apprentice's spell
    dict(key="ch7_spell", title="The Apprentice's Spell", giver="lysander", ender="lysander", level=38, xp=8, tone="funny",
         path="hero", prev="ch7_where", items=[("wand", 1)], rep=[(72, 250)],
         interact=[("lysander", "Hold still. Let him try his spell on you.")], interact_goal="Lysander's spell tried",
         interact_beats=[("emote", "self", "point"), ("wait", 1000), ("emote", "self", "spell"), ("visual", "self", 32992),
                         ("wait", 1500), ("visual", "self", 35426), ("sound", "self", 6763),
                         ("aura", "self", "lysander_murloc"), ("sound", "self", "murloc_aggro"), ("wait", 800),
                         ("move", "self", "circle_1", "run"), ("wait", 1800), ("move", "self", "circle_2", "run"),
                         ("sound", "self", "murloc_alert"), ("wait", 1800), ("move", "self", "circle_3", "run"), ("wait", 1800),
                         ("move", "self", "circle_4", "run"), ("sound", "self", "murloc_aggro"), ("wait", 2500),
                         ("unaura", "self", "lysander_murloc"), ("visual", "self", 35426), ("emote", "self", "exclamation"),
                         ("wait", 1500), ("move", "self", "lysander", "walk"), ("wait", 3000), ("face", "self", "wand_spot"),
                         ("emote", "self", "question"), ("say", "self", "Where's... where's my wand?", "question")],
         goal="Let Apprentice Lysander try his spell on you, on the beach north of Sentry Point. Then find his wand in "
              "the reeds and give it back.",
         text="A murloc! A real one! Hold still, hold still... I've been working on a spell of understanding. Your "
              "language, put into Common! It's perfectly safe. Mostly. Probably. Hold still!",
         progress="Did you find it? It's about so long, sort of... wand-shaped.",
         reward="My wand! Oh, thank you, thank you, thank you... I'll get it right next time. I will!",
         details=["exclamation", "talk", "spell"], reward_emotes=["cheer", "bow", "talk", "bow"],
         accept=[("emote", "self", "exclamation"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "point"),
                 ("wait", 1000), ("emote", "self", "spell"), ("visual", "self", 32992), ("sound", "self", "murloc_fidget")],
         complete=[("emote", "self", "cheer"), ("say", "self", "Thank you! Thank you. Thank you so much. Really. Thank you.",
                                                  "talk"),
                   ("wait", 2500), ("emote", "self", "bow"), ("wait", 1500), ("emote", "self", "talk"), ("wait", 1500),
                   ("emote", "self", "bow"), ("wait", 1500), ("emote", "self", "laugh")],
         poi=["lysander", "wand_spot"]),

    # 7.13: pages in the marsh
    dict(key="ch7_pages", title="Pages in the Marsh", giver="lysander", ender="lysander", level=38, xp=8, tone="boring",
         path="hero", prev="ch7_spell", items=[("page", 8)], rep=[(72, 250)], rewards=["sketch"],
         choice=["apprentice_robe", "sentry_cloak"],
         goal="Gather 8 of Lysander's Notes, blown across the beach and the marsh around his camp north of Sentry Point.",
         text="My notes! The wind took them... everything. Eight months of murloc phonetics. Mrgl, mrrgl, mrglglgl... all "
              "of it. They can't have gone far. Eight pages. Well, eighty. I'd settle for eight.",
         progress="Any luck? Any pages at all?",
         reward="Mrgl... mrrgl... none of it makes sense. Oh! Oh, this one's you. I drew you. Here. Keep it. I think "
                "you should have it.",
         details=["talk", "exclamation", "point"], reward_emotes=["laugh", "point", "bow"],
         accept=[("object", "empty_book", "book", 30), ("emote", "self", "point"), ("sound", "self", 1192), ("wait", 1500),
                 ("emote", "self", "exclamation"), ("sound", "self", 1192), ("wait", 1500), ("emote", "self", "no"),
                 ("emote", "self", "cry")],
         complete=[("emote", "self", "talk"), ("sound", "self", 1192), ("wait", 2000), ("emote", "self", "exclamation"),
                   ("wait", 1500), ("emote", "self", "laugh"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "bow")],
         poi=["page_3", "page_6"]),

    # 7.15: King Mrrgum's feast
    dict(key="ch7_feast", title="King Mrrgum's Feast", giver="ch1:murlorga", ender="ch1:murlorga", level=38, xp=8,
         tone="funny", path="hero", prev="ch7_fence", source="stew_bowl", objects=[("king_table", 1)],
         items=[("pen_key", 1)],
         goal="In Murlorga's Mud Mask, set the Covered Bowl of Indescribable Stew on the table before King Mrrgum's throne, "
              "and take the Fry-Pen Key in the chaos. Then return to Murlorga.",
         text="Hold still. Mud. More mud. There. Now you are one of them, ugly and brown. The king loves a feast... Take "
              "him my special stew. My Indescribable Stew. He will eat it all. He eats everything.",
         progress="Did he eat it? All of it?",
         reward="Green? He went GREEN? Hee... hee hee... Oh, I am a terrible cook. The worst. The very worst. And the key! "
                "Keep it close.",
         details=["talk", "laugh", "kiss"], reward_emotes=["laugh", "cry"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("sound", "self", 1197), ("aura", "player", "mud_mask"),
                 ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", 1197), ("wait", 1200), ("emote", "self", "point"),
                 ("emote", "self", "kiss"), ("wait", 1500), ("face", "self", "court_far"), ("emote", "self", "point"),
                 ("wait", 1200), ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("unaura", "player", "mud_mask"), ("state", "self", "none"), ("emote", "self", "laugh"),
                   ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", 973),
                   ("wait", 1000), ("emote", "self", "cry"), ("wait", 2000), ("state", "self", "work")],
         poi=["table"]),

    # 7.16: the fry pen
    dict(key="ch7_pen", title="The Fry Pen", giver="ch1:murlorga", ender="ch1:murlorga", level=39, xp=8, tone="serious",
         path="hero", prev="ch7_feast", source="pen_key", objects=[("pen_gate", 1)], choice=["pen_pendant", "mothers_knot"],
         goal="Unlock the fry pen at the south end of King Mrrgum's court with the Fry-Pen Key, and lead the tribute fry "
              "back through the reeds to Murlorga on the Mire Islets.",
         text="The key. The pen. While the king is green and his warriors run in circles. Open it. Bring them here, all "
              "of them, through the reeds. Walk slowly. Little legs.",
         progress="How many? How many did you bring?",
         reward="1, 2, 3, 4, 5, 6, 7, 8. ...1, 2, 3, 4, 5, 6, 7, 8. All 8. They are ours now. Nobody kicks them here.",
         details=["talk", "point", "beg"], reward_emotes=["cheer", "kiss"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("face", "self", "court_far"), ("emote", "self", "point"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "beg"), ("wait", 1500),
                 ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("face", "self", "fry_home_1"), ("emote", "self", "point"),
                   ("say", "self", "1, 2, 3, 4, 5, 6, 7, 8.", "talk"), ("wait", 3000), ("face", "self", "fry_home_3"),
                   ("emote", "self", "point"), ("say", "self", "1, 2, 3, 4, 5, 6, 7, 8...?", "question"), ("wait", 3000),
                   ("emote", "self", "cheer"), ("sound", "self", 973), ("music", 4454), ("wait", 1500), ("emote", "self", "kiss"),
                   ("face", "self", "cookpot"), ("state", "self", "work")],
         poi=["pen"]),

    # 7.17: Mirefin muscle (Grrmlgrrl stands in the reeds)
    dict(key="ch7_muscle", title="Mirefin Muscle", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=39, xp=8,
         tone="serious", prev="ch7_pen", kill=[(4359, 6), (4362, 4)],
         goal="Kill 6 Mirefin Murlocs and 4 Mirefin Coastrunners on the Mirefin beaches south of the court, before they "
              "come for the freed fry.",
         text="The king's warriors come. For the little ones. Along the beach, from their village. I stand in the reeds. "
              "You go to them. 10. Then the little ones sleep tonight.",
         progress="...",
         reward="10. Good. ...They are only murlocs who chose the wrong king. Remember that.",
         details=["talk", "roar", "point"], reward_emotes=["yes", "salute"],
         accept=[("emote", "self", "talk"), ("emote", "self", "kneel"), ("object", "sand_spear", "grrm_draw", 30),
                 ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 1000),
                 ("emote", "self", "roar"), ("sound", "self", "murloc_aggro"), ("summon", "grrm_reeds", "reeds_guard", 900),
                 ("face", "self", "court_far"), ("emote", "self", "point")],
         complete=[("emote", "self", "yes"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "salute")],
         poi=["mirefin"]),

    # 7.18a: topple the throne (the hero's road: the Mirefin come to the Storm Bay in 10.22)
    dict(key="ch7_topple", title="Topple the Throne", giver="ch1:grrmlgrrl", ender="brrsha", level=40, xp=8, tone="serious",
         path="hero", prev="ch7_muscle", exclusive=1, kill=[("king_sick", 1)],
         choice=["scepter", "throne_breaker", "fin_blade"],
         goal="Face King Mrrgum on his throne of shells and bring him down. Then go to Mother Brrsha, eldest of the fry's "
              "mothers, at the foot of the throne.",
         text="A king who eats the children's fish. A king who kicks. He is green now, and weak. Go and stand in front of "
              "him. Bring him down. Then the mothers decide.",
         progress="The king? Is he...?",
         reward="Down. He is down. ...No king. What do we do, with no king? ...We sit. Sit with me, a little.",
         details=["talk", "attack", "roar"], reward_emotes=["cry", "bow"],
         accept=[("emote", "self", "kneel"), ("object", "sand_throne", "grrm_draw", 30), ("sound", "self", 1194),
                 ("wait", 1500), ("emote", "self", "attack2h"), ("sound", "self", 1194), ("wait", 1000), ("emote", "self", "roar"),
                 ("sound", "self", "murloc_aggro"), ("face", "self", "court_far"), ("emote", "self", "point")],
         complete=[("state", "self", "none"), ("move", "mother_a", "brrsha_side", "walk"), ("emote", "mother_b", "point"),
                   ("wait", 2000), ("emote", "mother_a", "point"), ("move", "self", "king_seat", "walk"), ("wait", 3500),
                   ("face", "self", "court"), ("state", "self", "sit"), ("sound", "self", "murloc_fidget2"), ("wait", 4500),
                   ("state", "self", "none"), ("emote", "self", "no"), ("wait", 1500), ("move", "self", "brrsha_floor", "walk"),
                   ("wait", 2500), ("face", "self", "court"), ("state", "self", "sit"), ("emote", "mother_a", "cheer"),
                   ("emote", "mother_b", "cheer"), ("sound", "mother_a", "murloc_fidget"), ("wait", 3000),
                   ("move", "mother_a", "mother_1", "walk")],
         poi=["king_seat"]),

    # 7.18b: the shell hoard (the menace's road: the Mirefin keep their king, and don't come in 10.22)
    dict(key="ch7_hoard", title="The Shell Hoard", giver="ch1:blrrgl", ender="ch1:blrrgl", level=40, xp=8, tone="funny",
         path="menace", prev="ch7_muscle", exclusive=1, items=[("shiny", 8)], choice=["ring_int", "ring_agi", "ring_str"],
         goal="While King Mrrgum lies green and sick on his throne, take 8 of King Mrrgum's Shinies from the hoard piled "
              "behind it. Leave the king where he is.",
         text="Shinies. Behind the throne. A big pile. Bigger than my log! The king is green, he cannot get up... he can "
              "only watch. 8 shinies. I hold the bag. You put in. That is teamwork.",
         progress="Bag is light. Bag is sad.",
         reward="Heavy! Heavy bag! Into the log... the log will need a bigger log. Hee!",
         details=["beg", "laugh", "point"], reward_emotes=["laugh", "beg"],
         accept=[("emote", "self", "beg"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("face", "self", "court_far"),
                 ("emote", "self", "point"), ("emote", "self", "laugh"), ("summon", "blrrgl_bag", "hoard_side", 900),
                 ("sound", "self", 120)],
         complete=[("emote", "self", "laugh"), ("sound", "self", 120), ("wait", 1000), ("move", "self", "blrrgl_log", "walk"),
                   ("wait", 1500), ("emote", "self", "kneel"), ("sound", "self", 1193), ("wait", 1500),
                   ("move", "self", "blrrgl", "walk")],
         poi=["hoard_1"]),

    # 7.19: Ilyssa's signet (Glubbub's vision of the goblin harbour; Murlorga faints)
    dict(key="ch7_signet", title="Ilyssa's Signet", giver="ch1:glubbub", ender="ch1:glubbub", level=40, xp=8,
         tone="serious", prev="ch7_muscle", items=[("signet", 1)], drops={"signet": [("king_sick", 100)]},
         choice=["seeing_stone", "cold_choker"],
         goal="Find the cold thing in King Mrrgum's hoard behind his throne, or on the king himself, and bring it to Oracle "
              "Glubbub.",
         text="Something is cold. Over there, in the king's pile. Cold like her hands were cold, the long one, the frost "
              "one... Bring it to me. Don't hold it long.",
         progress="Cold. Cold, cold, cold. Bring it.",
         reward="Her mark. Ilyssa. She was here. She sold him something, or bought... Let me see where it has been. Let me "
                "SEE.",
         details=["spell", "point", "cry"], reward_emotes=["spell", "exclamation"],
         accept=[("state", "self", "none"), ("visual", "self", 32992), ("emote", "self", "spell"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "court_far"), ("emote", "self", "point"),
                 ("wait", 1500), ("emote", "self", "cry"), ("wait", 1000), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("visual", "self", 35426), ("emote", "self", "spell"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("visual", "self", 32992),
                   ("summon", "vision_chef", "vision_chef", 25), ("object", "vision_boat", "vision_boat", 25),
                   ("object", "vision_flag", "vision_flag", 25), ("music", 5037), ("wait", 2500),
                   ("object", "vision_egg", "vision_egg", 20), ("emote", "vision_chef", "talk"), ("wait", 1500),
                   ("emote", "vision_chef", "cheer"), ("visual", "vision_chef", 22576), ("wait", 2500),
                   ("state", "ch1:murlorga", "dead"), ("sound", "ch1:murlorga", "murloc_wound"), ("wait", 2500),
                   ("emote", "self", "point"), ("say", "self", "Red sails. A goblin. Our eggs...", "point"), ("wait", 6000),
                   ("state", "ch1:murlorga", "work"), ("state", "self", "sit")],
         poi=["casket", "king_seat"]),

    # 7.20: Witch Hill's pumpkin
    dict(key="ch7_pumpkin", title="Witch Hill's Pumpkin", giver="ch1:blrrgl", ender="ch1:blrrgl", level=38, xp=8,
         tone="stupid", prev="ch7_where", items=[("pumpkin", 1)],
         goal="Steal a Witch Hill Pumpkin from the patch beside the haunted manor on Witch Hill, south of the Mirefin "
              "beaches, and bring it to Blrrgl.",
         text="There is a house on the hill. A dead house. Dead dry-skins walk around it at night. And next to it... "
              "pumpkins. Big orange shinies you can eat. I dare you. I double dare you. Bring 1.",
         progress="Did the dead ones chase you? Did they? Hee.",
         reward="A pumpkin! Look. Look. I make a face... A hat! It is a hat now. It fits. It fits!",
         details=["point", "exclamation", "laugh"], reward_emotes=["cheer", "laugh"],
         accept=[("emote", "self", "kneel"), ("object", "sand_pumpkin", "blrrgl_draw", 30), ("sound", "self", 1194),
                 ("wait", 1500), ("object", "sand_skull", "blrrgl_draw2", 30), ("emote", "self", "exclamation"),
                 ("sound", "self", "murloc_alert"), ("wait", 1200), ("move", "self", "blrrgl_run", "run"), ("wait", 2500),
                 ("move", "self", "blrrgl", "run"), ("wait", 2500), ("face", "self", "witch_hill"), ("emote", "self", "laugh")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "work"),
                   ("sound", "self", 1186), ("wait", 1500), ("object", "worn_pumpkin", "blrrgl_head", 15),
                   ("emote", "self", "dance"), ("sound", "self", "murloc_fidget2"), ("wait", 5000), ("emote", "self", "flex")],
         poi=["patch"]),

    # 7.21: Firemane embers
    dict(key="ch7_embers", title="Firemane Embers", giver="ch1:fizzmrgl", ender="ch1:fizzmrgl", level=39, xp=8,
         tone="funny", prev="ch7_pen", items=[("ember", 6)],
         drops={"ember": [(4328, 45), (4329, 45), (4331, 45), (4334, 45)]},
         choice=["fin_gloves", "ember_grips", "firemane_gauntlets"],
         goal="Bring Fizzmrgl the Sparker 6 Firemane Embers from the Firemane dragonkin in the far south of the marsh, past "
              "the Quagmire, toward the Wyrmbog.",
         text="Dragon-lizards. In the south. They breathe fire, real fire, not sparks... Look at my fins. Sparks did "
              "this. Imagine what real fire... ah... AH-CHOO! ...6 embers. Please. For learning.",
         progress="Warm? Are they warm?",
         reward="Ohhh. Oh, yes. Hold them up, hold them... AH-CHOO!",
         details=["point", "beg", "spell"], reward_emotes=["spell", "cheer"],
         accept=[("face", "self", "firemane_far"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "point"), ("visual", "self", 11542), ("sound", "self", 6763), ("wait", 1500),
                 ("emote", "self", "beg")],
         complete=[("emote", "self", "spell"), ("visual", "self", 34602), ("wait", 800), ("visual", "self", 40162),
                   ("cast", "self", 42344, "self"), ("sound", "self", 6763), ("wait", 1500), ("emote", "self", "cheer"),
                   ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "dance")],
         poi=["firemane"]),

    # 7.23: Gorlak's war-song (the tribe comes to the reeds to say goodbye)
    dict(key="ch7_warsong", title="Gorlak's War-Song", giver="ch1:grrmlgrrl", ender="gorlak", level=40, xp=8,
         tone="serious", path="hero", prev=["ch7_deserters", "ch7_signet"], rep=[(76, 500)], rewards=["war_drum"],
         emotes=[("gorlak", "roar", 1, [("state", "self", "none"), ("emote", "self", "roar"), ("emote", "song_grrm", "roar"),
                                        ("sound", "song_grrm", "murloc_aggro"), ("wait", 900), ("emote", "song_murlorga", "roar"),
                                        ("emote", "song_glubbub", "roar"), ("emote", "song_blrrgl", "roar"),
                                        ("sound", "song_blrrgl", "murloc_aggro"), ("sound", "song_glubbub", "murloc_aggro_old"),
                                        ("wait", 1200), ("emote", "self", "battle_roar"), ("wait", 1500),
                                        ("emote", "self", "laugh")])],
         goal="Go to Gorlak in the reeds below Brackenwall, where the tribe has come to say goodbye, and /roar with him.",
         text="We go soon. South, on the turtle. The orc in the reeds... he gave the sea his chain. We give him our song. "
              "Come. All of us. You roar too. Loud.",
         progress="Hrm. Louder, fish.",
         reward="Ha! HA! That is a song. Here. Take the drum. Beat it where you're going, and the orcs there will know "
                "you heard it once.",
         details=["talk", "point", "roar"], reward_emotes=["salute", "laugh"],
         accept=[("emote", "self", "talk"), ("face", "self", "brackenwall"), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 700), ("emote", "self", "attack"),
                 ("sound", "self", 1194), ("summon", "song_grrm", "song_1", 600), ("summon", "song_murlorga", "song_2", 600),
                 ("summon", "song_glubbub", "song_3", 600), ("summon", "song_blrrgl", "song_4", 600),
                 ("object", "war_drum", "drum", 600), ("object", "song_pot", "song_pot", 600), ("wait", 1000),
                 ("emote", "self", "roar"), ("sound", "self", "murloc_aggro")],
         complete=[("state", "self", "none"), ("face", "self", "song_pot"), ("wait", 4500), ("face", "self", "player"),
                   ("emote", "self", "salute"), ("emote", "song_grrm", "salute"), ("wait", 1500), ("emote", "song_grrm", "attack"),
                   ("sound", "song_grrm", 1194), ("wait", 1500), ("emote", "self", "yes"), ("wait", 2000),
                   ("face", "self", "toss"), ("state", "self", "fish")],
         poi=["gorlak"]),

    # 7.25: south to the red sails (the ride: Grandmother Shellback carries the tribe to Stranglethorn)
    dict(key="ch7_end", title="South to the Red Sails", giver="ch1:elder", ender="ch0:shellback", level=40, xp=8,
         tone="serious", prev="ch7_warsong", prev_any=["ch7_topple", "ch7_hoard"],
         choice=["rider_boots", "mire_boots", "reed_sandals"],
         goal="When the tribe is ready, climb onto Grandmother Shellback in the bay of the Mire Islets and ride south "
              "to the goblins' harbour.",
         text="Red sails. A goblin. Our eggs in a goblin's pot. Glubbub saw it. ...We go. All of us. Grandmother is "
              "tired, but she says she can swim one more sea. Get on her back.",
         progress="Hmmmm...",
         reward="Hmmmmmm. Mmmmmrrrrr.",
         details=["point", "talk"], reward_emotes=["talk"],
         accept=[("face", "self", "shellback"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700),
                 ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1000), ("face", "self", "south_sea"),
                 ("say", "self", "South.", "point", "murloc_fidget2"), ("sound", "ch0:shellback", 1463), ("wait", 2000),
                 ("face", "self", "landing")],
         complete=[("sound", "self", "splash_big"), ("emote", "ch1:glubbub", "spell"), ("sound", "ch1:glubbub", 7034),
                   ("wait", 2000), ("emote", "ch1:elder", "attack"), ("sound", "ch1:elder", 977), ("wait", 700),
                   ("emote", "ch1:elder", "attack"), ("sound", "ch1:elder", 977), ("wait", 700), ("emote", "ch1:elder", "attack"),
                   ("sound", "ch1:elder", 977), ("wait", 1000), ("emote", "ch1:murlorga", "cheer"), ("emote", "ch1:blrrgl", "cheer"),
                   ("emote", "ch1:grrmlgrrl", "roar"), ("sound", "ch1:grrmlgrrl", "murloc_aggro"), ("music", 6837),
                   ("wait", 3000), ("sound", "self", "splash_big"), ("teleport", "player", "ch8:hub")],
         poi=["shellback"]),
]
