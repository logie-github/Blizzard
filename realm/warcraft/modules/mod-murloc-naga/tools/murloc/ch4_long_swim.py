# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 4 of the murlocs' story: The Long Swim (levels 24 to 29), the bible's section 10.

The Wetlands' west coast. Grandmother Shellback brings the tribe ashore in a little cove north of
Menethil Harbor, below the bonfire field (x -3395..-3325, y -1090..-960: 40 yards and more from every
hostile spawn of the game's, Menethil's peninsula sentries well to the south): Saltscar Shallows, the
camp on the cove's south bank, and beside it Chief Blrrmuk's Bluegill village in the marsh pond at
the cove's head (the murlocs' phase). Menethil Harbor is met from the water: Bram Coldkettle sits in
his rowboat off the end of the main pier, the lanterns hang on buoys by the docks, and only the
fish-market raid climbs onto the waterfront boardwalk. The Dragonmaw are the game's, at the
Angerfang Encampment, with a chained whelp, its driver and a cage of the murlocs' phase; Mirelow is a
copy summoned at a marsh wallow in the Bluegill Marsh. The chapter ends on Shellback's back: 4.25's
reward teleports the player to chapter 5's hub.

Phases: the Elder from chapter 3's last quest until his death (9.21); the hub kit from 4.01; the
Bluegill village, Bram and Menethil's props always (the murlocs' Wetlands); everything else for the
quest that needs it. A scene can only move people who share its owner's phase (or who are always
there), so the set pieces that join the Elder and the camp are run by objects that are always there.
Plain data: tools/murloc/SCHEMA.md."""

ELDER = ("between", "ch3:ch3_end", "ch9:ch9_elder")
HUB = ("from", "ch4_arrival")
LANDING = ("during", "ch4_arrival")
WOUNDED = ("between", "ch3:ch3_end", "ch4_moss")
HEALED = ("between", "ch4_moss", "ch4_end")
CROCS = ("during", "ch4_blood")
GNOLLS = ("during", "ch4_gnolls")
RIDGE = ("during", "ch4_chains")
RIDGE_AFTER = ("between", "ch4_chains", "ch4_whelp")
WHELP = ("until", "ch4_whelp")
CAT = ("during", "ch4_cat")
RAID = ("during", "ch4_raid")
AMBUSH = ("during", "ch4_ambush")

CHAPTER = dict(key="ch4", title="The Long Swim", levels=(24, 29), map=0, zones=[11], hub="hub")

TOWNS = ["Menethil Harbor"]

PLACES = {
    # Saltscar Shallows: the camp on the cove's south bank, round the fire
    "hub": (-3376.0, -1006.0), "hub_fire": (-3372.0, -1022.0), "elder": (-3365.0, -1018.0), "grrmlgrrl": (-3364.0, -1028.0),
    "cookpot": (-3380.0, -1017.0), "murlorga": (-3377.5, -1014.0), "blrrgl": (-3383.0, -1027.0), "blrrgl_log": (-3386.5, -1030.5),
    "glubbub": (-3372.0, -1033.0), "caller": (-3380.0, -1001.0), "mailbox": (-3385.0, -1004.0), "slubb": (-3366.0, -1004.0),
    "gurgle": (-3360.0, -1006.0), "mrrlglr": (-3387.0, -1019.0), "graveyard": (-3389.0, -1008.0), "cat_start": (-3383.0, -1019.0),
    "brrgmrk": (-3386.0, -1042.0), "mrrgasha": (-3382.0, -1047.0), "glubba": (-3376.0, -1049.0), "fizzmrgl": (-3370.0, -1049.0),
    "mrsha": (-3388.0, -1062.0), "brewglub": (-3382.0, -1065.0), "grrsh": (-3376.0, -1067.0), "mrrsk": (-3370.0, -1067.0),
    "brrkl": (-3364.0, -1064.0), "krrgl": (-3360.0, -1058.0), "anvil": (-3358.0, -1061.0), "hooks_spot": (-3358.5, -1056.0),
    "mmrglla": (-3386.0, -1073.0), "sprokgl": (-3380.0, -1075.0), "shimmrl": (-3374.0, -1076.0), "pearlmrgl": (-3368.0, -1075.0),
    "scrawlgl": (-3362.0, -1072.0), "fnrrgl": (-3356.0, -1068.0), "vest_spot": (-3374.0, -1065.0), "fry_mother": (-3356.0, -1044.0),
    "mother_1": (-3352.0, -1040.0), "mother_2": (-3358.0, -1038.0), "mother_3": (-3360.0, -1046.0),
    "hut_1": (-3392.0, -1036.0), "hut_2": (-3390.0, -1056.0), "hut_3": (-3352.0, -1052.0), "fire_2": (-3378.0, -1058.0),
    "net_rack": (-3386.0, -995.0), "crates": (-3383.0, -991.0), "grrm_cove": (-3360.0, -995.0), "sea": (-3380.0, -930.0),
    "east": (-3380.0, -1400.0), "north": (-3100.0, -950.0),
    # the beach where the sea left them, and the cove where Grandmother Shellback lies
    "body_1": (-3386.0, -963.0), "body_2": (-3380.0, -968.0), "body_3": (-3374.0, -975.0), "body_4": (-3368.0, -984.0),
    "body_5": (-3362.0, -991.0), "body_6": (-3357.0, -998.0),
    "shellback": (-3354.0, -978.0, -2.0), "wound": (-3360.0, -985.0, -0.2), "cove_edge": (-3361.0, -993.0),
    "flipper": (-3361.0, -991.0), "turtle_shore": (-3364.0, -996.0),
    "croc_1": (-3348.0, -968.0, -1.0), "croc_2": (-3364.0, -966.0, -1.0), "croc_3": (-3344.0, -988.0, -1.0),
    "croc_4": (-3372.0, -958.0, -1.0), "croc_5": (-3338.0, -976.0, -0.5), "croc_6": (-3380.0, -952.0, -1.0),
    "pack_1": (-3370.0, -992.0), "pack_2": (-3374.0, -988.0), "pack_3": (-3366.0, -998.0), "pack_4": (-3378.0, -984.0),
    # the bay off the camp: fish, glow-jellies, the deep water for the drum
    "shoal_1": (-3398.0, -938.0, 0.0), "shoal_2": (-3386.0, -936.0, 0.0), "shoal_3": (-3376.0, -946.0, 0.0),
    "shoal_4": (-3405.0, -930.0, 0.0), "shoal_5": (-3366.0, -944.0, 0.0), "shoal_6": (-3392.0, -918.0, 0.0),
    "shoal_7": (-3378.0, -924.0, 0.0), "shoal_8": (-3350.0, -952.0, 0.0),
    "glow_1": (-3352.0, -972.0, -4.0), "glow_2": (-3340.0, -988.0, -3.0), "glow_3": (-3410.0, -925.0, -3.0),
    "glow_4": (-3420.0, -905.0, -5.0), "glow_5": (-3395.0, -900.0, -5.0), "glow_6": (-3372.0, -930.0, -5.0),
    "glow_7": (-3362.0, -942.0, -1.5), "drum_deep": (-3400.0, -912.0),
    # the marsh pools south of camp and the pond: moss, mud, mudfish
    "moss_1": (-3406.0, -1062.0), "moss_2": (-3408.0, -1042.0), "moss_3": (-3404.0, -1022.0), "moss_4": (-3407.0, -1002.0),
    "moss_5": (-3403.0, -990.0), "moss_6": (-3326.0, -1056.0), "moss_7": (-3330.0, -1022.0),
    "mud_1": (-3338.0, -1034.0), "mud_2": (-3343.0, -1024.0), "mud_3": (-3331.0, -1028.0), "mud_4": (-3346.0, -1032.0),
    "mud_5": (-3408.0, -1050.0), "mud_6": (-3405.0, -1012.0), "mud_7": (-3408.0, -996.0), "mud_8": (-3333.0, -1046.0),
    "mudfish_1": (-3410.0, -1060.0), "mudfish_2": (-3409.0, -1030.0), "mudfish_3": (-3406.0, -1006.0),
    "mudfish_4": (-3336.0, -1040.0), "mudfish_5": (-3346.0, -1022.0), "mudfish_6": (-3329.0, -1032.0),
    # Chief Blrrmuk's Bluegill village, in the pond at the cove's head
    "pond": (-3338.0, -1030.0), "blrrmuk": (-3338.0, -1053.0), "throne": (-3337.0, -1056.5), "blrrmuk_hut": (-3330.0, -1062.0),
    "blrrmuk_visit": (-3359.0, -1023.0), "toll_basket": (-3339.5, -1050.0), "guard_1": (-3343.0, -1050.0),
    "guard_2": (-3333.0, -1050.0), "muckmaw": (-3348.0, -1048.0), "mud_throne": (-3352.0, -1058.0),
    "draw_1": (-3351.0, -1045.0), "draw_2": (-3353.0, -1043.0), "draw_3": (-3350.5, -1042.0), "war_drum": (-3332.0, -1057.0),
    "gloop": (-3329.0, -1003.0), "gloop_hut": (-3327.0, -998.0), "gloop_draw_1": (-3331.0, -1006.0),
    "gloop_draw_2": (-3332.5, -1004.0), "egg_held": (-3330.5, -1004.5),
    "egg_keeper": (-3329.0, -1046.0), "egg_1": (-3331.0, -1043.0), "egg_2": (-3328.0, -1040.0), "egg_3": (-3333.0, -1038.0),
    "water_hut_1": (-3342.0, -1040.0), "water_hut_2": (-3334.0, -1024.0), "water_hut_3": (-3344.0, -1018.0),
    "villager_1": (-3346.0, -1036.0), "villager_2": (-3338.0, -1022.0), "villager_3": (-3332.0, -1033.0),
    "villager_4": (-3348.0, -1027.0), "villager_5": (-3340.0, -1044.0), "villager_6": (-3336.0, -1015.0),
    "contest_log": (-3344.0, -1062.0), "platter": (-3343.5, -1063.5), "mrrk": (-3346.0, -1059.0), "eater_1": (-3342.0, -1065.0),
    "empty_seat": (-3340.0, -1061.0), "eat_watch": (-3346.0, -1066.0), "conga_end": (-3350.0, -1040.0),
    "spawn_water": (-3340.0, -1030.0), "spawn_water_b": (-3337.0, -1027.0),
    "light_1": (-3346.0, -1031.0, 7.0), "light_2": (-3341.0, -1023.0, 6.4), "light_3": (-3334.0, -1030.0, 7.1),
    "light_4": (-3339.0, -1037.0, 7.2), "light_5": (-3344.0, -1026.0, 6.8),
    "pond_elder": (-3346.0, -1028.0), "pond_murlorga": (-3348.5, -1026.0), "pond_blrrgl": (-3348.0, -1030.5),
    "sway_1": (-3336.0, -1034.0), "sway_2": (-3342.0, -1020.0), "sway_3": (-3333.0, -1023.0),
    "dawn_1": (-3334.0, -1066.0), "dawn_2": (-3340.0, -1068.0), "dawn_3": (-3328.0, -1056.0), "raid_road": (-3470.0, -890.0),
    "gnoll_reeds": (-3318.0, -1060.0), "gnoll_1": (-3312.0, -1070.0), "gnoll_2": (-3306.0, -1052.0), "gnoll_3": (-3318.0, -1080.0),
    "gnoll_4": (-3300.0, -1066.0),
    "ambush_1": (-3352.0, -1082.0), "ambush_2": (-3340.0, -1076.0), "ambush_3": (-3326.0, -1070.0),
    "ambush_4": (-3320.0, -1050.0), "ambush_5": (-3366.0, -1086.0), "ambush_6": (-3384.0, -1086.0),
    # Menethil Harbor, from the water: Bram's rowboat off the main pier, buoys by the docks, the boardwalk market
    "bram": (-3784.0, -612.0, 0.6), "bram_boat": (-3784.0, -612.0, -0.4), "bram_lap": (-3783.2, -612.8, 0.9),
    "ring": (-3789.0, -617.0), "ring_dock": (-3782.6, -611.0, 0.5),
    "buoy_1": (-3752.0, -573.0, -0.3), "buoy_2": (-3702.0, -598.0, -0.3), "buoy_3": (-3852.0, -574.0, -0.3),
    "lantern_1": (-3752.0, -573.0, 0.9), "lantern_2": (-3702.0, -598.0, 0.9), "lantern_3": (-3852.0, -574.0, 0.9),
    "cart": (-3586.0, -770.0), "cart_crates": (-3583.0, -767.0),
    "market_1": (-3762.0, -750.5, 7.9), "market_2": (-3786.5, -749.5, 8.1), "market_3": (-3813.0, -755.5, 8.1),
    "market_4": (-3795.0, -771.5, 8.7), "market_5": (-3836.5, -761.5, 8.2), "market_6": (-3848.5, -732.5, 8.5),
    "market_7": (-3841.5, -736.5, 8.7), "market_8": (-3762.5, -734.5, 8.0),
    "fishwife_1": (-3788.0, -752.0, 8.1), "fishwife_2": (-3839.0, -739.0, 8.7),
    "raider_1": (-3784.0, -748.0, 8.1), "raider_2": (-3811.0, -753.0, 8.1), "raider_3": (-3846.0, -734.0, 8.5),
    "hide_1": (-3472.0, -890.0), "hide_2": (-3576.0, -748.0), "cat_run": (-3610.0, -760.0),
    # the Dragonmaw at the Angerfang Encampment, and the ridge above it
    "ridge": (-3424.0, -2186.0), "grrm_ridge": (-3422.0, -2190.0), "forge": (-3418.0, -2266.0), "cage": (-3412.0, -2262.0),
    "driver": (-3420.0, -2258.0), "tent_1": (-3430.0, -2280.0), "tent_2": (-3440.0, -2296.0), "whelp_away": (-3470.0, -2205.0),
    # the Bluegill Marsh: Mirelow's wallow and the reed nest; Mottled raptors to the south-east
    "wallow": (-3112.0, -1204.0), "wallow_rise": (-3114.0, -1200.0), "nest": (-3100.0, -1212.0),
    "raptor_1": (-3493.0, -1445.0), "raptor_2": (-3558.0, -1444.0),
    # Baradin Bay's north shore, where the egg-jelly washes up
    "jelly_shore_1": (-3275.0, -908.0), "jelly_shore_2": (-3200.0, -906.0), "jelly_shore_3": (-3150.0, -912.0),
    "jelly_shore_4": (-3100.0, -912.0), "jelly_shore_5": (-3025.0, -954.0), "jelly_shore_6": (-2975.0, -984.0),
    "jelly_shore_7": (-2925.0, -1004.0),
}

# -- the people ------------------------------------------------------------------------------------

NPCS = [
    # the landing: six of the tribe the sea left on the beach (only while 4.01 is in the log)
    dict(key="drowned_cough", name="Half-Drowned Saltscar", plural="coughing Saltscar", look="murloc_grey",
         looks=["murloc_bronze"], level=22, role="ambient", at=["body_1", "body_4"], facing=1.6, phase=LANDING,
         greeting="Mrgl... blbl... mrgl.",
         idle=[("state", "self", "sleep"), ("every", 23000, [("sound", "self", "murloc_wound")])]),
    dict(key="drowned_hug", name="Half-Drowned Saltscar", plural="Saltscar clinging to the sand", look="murloc_blue",
         looks=["murloc_red"], level=22, role="ambient", at=["body_2", "body_5"], facing=4.9, phase=LANDING,
         greeting="Sand. Sand! Not water. Sand...",
         idle=[("state", "self", "sleep"), ("every", 29000, [("sound", "self", "murloc_fidget2")])]),
    dict(key="drowned_net", name="Half-Drowned Saltscar", plural="Saltscar with empty nets", look="murloc_pale",
         looks=["murloc_gold"], level=22, role="ambient", at=["body_3", "body_6"], facing=1.2, phase=LANDING,
         greeting="The net... the net was full, once.",
         idle=[("state", "self", "sleep"), ("every", 31000, [("sound", "self", "murloc_wound")])]),

    # the camp's own, new here
    dict(key="nrrgla", name="Nrrgla", subname="A Worried Mother", look="murloc_pale", level=24, role="quest",
         at="fry_mother", facing=2.2, phase=HUB, greeting="Have you seen him? Small. Green. LOUD. Have you seen him?",
         idle=[("every", 19000, [("face", "self", "east"), ("emote", "self", "cry")]),
               ("every", 33000, [("face", "self", "hub_fire"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="squeep", name="Squeep", subname="", look="murloc_green", scale=0.45, level=5, role="ambient", summoned=True,
         greeting="Mrgl! Mrgl mrgl! Big lizard! Big BIG lizard!",
         watch=(25, [("follow", "self"), ("emote", "self", "cheer"), ("sound", "self", "baby_murloc")], 600000),
         idle=[("every", 9000, [("sound", "self", "baby_murloc")])]),
    # an unseen voice at the cove and one at the pond, for the sounds of scenes run by objects
    dict(key="echo_cove", name="Cove", look="trigger", level=1, role="ambient", at="cove_edge", unit_flags=0x02000002),
    dict(key="echo_pond", name="Pond", look="trigger", level=1, role="ambient", at="pond", unit_flags=0x02000002),
    # blood in the water, while she is wounded
    dict(key="wound_blood", name="Grandmother Shellback's Wound", look="trigger", level=1, role="ambient", at="wound",
         unit_flags=0x02000002, phase=WOUNDED, idle=[("every", 50000, [("visual", "self", 46767)])]),

    # Chief Blrrmuk's Bluegill village (always there: the murlocs' Wetlands)
    dict(key="blrrmuk", name="Chief Blrrmuk", subname="Chief of the Bluegill", look="murloc_blue", scale=1.45, level=30,
         role="quest", at="blrrmuk", facing=1.57,
         greeting="Mine. The beach is mine. The fish are mine. You are on my beach, eating my fish. So. What do you have for me?",
         idle=[("state", "self", "sit"), ("every", 24000, [("emote", "self", "eat"), ("sound", "self", 45)]),
               ("every", 41000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="guard_a", name="Bluegill Guard", subname="", look="murloc_abyssal", level=28, role="ambient", at="guard_1",
         facing=1.33, greeting="Hm. The chief is eating. The chief is always eating.",
         idle=[("every", 33000, [("emote", "self", "flex")]), ("every", 47000, [("emote", "self", "laugh")])]),
    dict(key="guard_b", name="Bluegill Guard", subname="", look="murloc_slate", level=28, role="ambient", at="guard_2",
         facing=1.82, greeting="No closer. Closer is for fish.",
         idle=[("every", 37000, [("emote", "self", "flex")]), ("every", 53000, [("emote", "self", "laugh")])]),
    dict(key="muckmaw", name="Muckmaw", subname="Festival-Master", look="murloc_green", level=27, role="quest",
         at="muckmaw", facing=1.06,
         greeting="Muckfest! Nearly Muckfest! Mud, fins, fish, lights! Everyone dances. Even you. ESPECIALLY you.",
         idle=[("every", 18000, [("emote", "self", 94), ("sound", "self", "murloc_fidget")]),
               ("every", 43000, [("emote", "self", "laugh")])]),
    dict(key="gloop", name="Grandmother Gloop", subname="Oracle of the Bluegill", look="murloc_ice", level=32, role="quest",
         at="gloop", facing=4.39,
         greeting="Shh. The water is talking. It talks slowly, to old ones. Sit. Listen with me.",
         idle=[("state", "self", "sit"), ("every", 37000, [("visual", "self", 35426), ("sound", "self", "murloc_fidget2")])]),
    dict(key="plubba", name="Plubba", subname="Egg-Keeper", look="murloc_bronze", level=25, role="quest", at="egg_keeper",
         facing=2.16, greeting="Shh! Shh. They sleep. All of them, in the beds. Don't wake them.",
         idle=[("state", "self", "sit"), ("every", 17000, [("emote", "self", "shy"), ("sound", "self", "baby_murloc")])]),
    dict(key="bluegill", name="Bluegill Villager", plural="Bluegill", look="murloc_blue", looks=["murloc_slate", "murloc_abyssal"],
         level=(23, 25), role="ambient", at=["villager_1", "villager_2", "villager_3", "villager_4", "villager_5", "villager_6"],
         greeting="Saltscar? Salt... scar. Funny name. Funny fins. Muckfest soon!",
         idle=[("every", 27000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget")]),
               ("every", 39000, [("emote", "self", "eat")])]),
    # Muckfest's dancers, sleepy raiders, swayers on spawning night (summoned by scenes)
    dict(key="conga", name="Bluegill Dancer", look="murloc_blue", level=24, role="ambient", summoned=True,
         watch=(30, [("follow", "self"), ("emote", "self", 94), ("sound", "self", "murloc_fidget")], 600000),
         idle=[("every", 4000, [("emote", "self", 94)])]),
    dict(key="swayer", name="Swaying Bluegill", look="murloc_slate", level=24, role="ambient", summoned=True,
         idle=[("every", 3000, [("state", "self", "dance")])]),
    dict(key="dawn_raider", name="Sleepy Bluegill Raider", look="murloc_abyssal", level=26, role="ambient", summoned=True,
         watch=(35, [("emote", "self", "question"), ("sound", "self", "murloc_fidget"), ("wait", 3000), ("emote", "self", "question"),
                     ("wait", 3000), ("state", "self", "sleep")], 600000)),
    dict(key="raider", name="Bluegill Raider", look="murloc_slate", level=27, role="ambient", at=["raider_1", "raider_2", "raider_3"],
         phase=RAID, facing=3.6, greeting="Fish! Fish! Throw the fish!",
         idle=[("every", 5000, [("emote", "self", "throw"), ("sound", "self", "splash_small")])]),
    dict(key="pebble_glow", name="Glowing Pebbles", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 2500, [("visual", "self", 22576)])]),

    # the egg-beds' raiders (while 4.05 is in the log)
    dict(key="egg_thief", name="Mosshide Egg-Thief", look=8598, level=25, side="hostile", role="enemy", at="gnoll_reeds",
         facing=3.0, phase=GNOLLS, respawn=60, idle=[("every", 8000, [("emote", "self", "eat"), ("sound", "self", 45)])]),

    # Blrrmuk's warriors, as the tribe packs (while 4.24 is in the log)
    dict(key="ambusher", name="Blrrmuk's Warrior", look="warrior", looks=["raider", "hunter"], level=(27, 29), side="hostile",
         role="enemy", at=["ambush_1", "ambush_2", "ambush_3", "ambush_4", "ambush_5", "ambush_6"], phase=AMBUSH, wander=5.0,
         respawn=30),

    # Mirelow, the old one of the marsh (summoned by bait at his wallow)
    dict(key="mirelow", name="Mirelow", subname="", look=925, scale=1.7, level=27, side="hostile", role="enemy", health=3.0,
         damage=1.3, summoned=True),

    # Menethil: the fishwives on the boardwalk (during the raid), the dock cat (during 4.21)
    dict(key="fishwife", name="Menethil Fishwife", plural="fishwives", look=3694, looks=[3290], level=20, side="faction:47",
         role="ambient", language="common", at=["fishwife_1", "fishwife_2"], phase=RAID, facing=3.6,
         greeting="Out! Out, you slimy thing! GUARDS!",
         watch=(14, [("face", "self", "player"), ("emote", "self", "exclamation"), ("sound", "self", 2683)], 9000),
         idle=[("every", 7000, [("emote", "self", "cry"), ("sound", "self", 2680)])]),
    dict(key="cat_a", name="Dock Cat", look=5554, level=1, role="ambient", at="hide_1", facing=1.0, phase=CAT, respawn=20,
         watch=(10, [("sound", "self", 4040), ("move", "self", "hide_2", "run"), ("wait", 14000), ("despawn", "self")], 15000)),
    dict(key="cat_b", name="Dock Cat", look=5554, level=1, role="ambient", at="hide_2", facing=2.4, phase=CAT, respawn=20,
         watch=(10, [("sound", "self", 4040), ("move", "self", "cat_run", "run"), ("wait", 6000), ("despawn", "self")], 15000)),
    dict(key="cat_lap", name="Dock Cat", look=5554, level=1, role="ambient", at="bram_lap", facing=3.9, phase=CAT,
         idle=[("state", "self", "sit"), ("every", 15000, [("sound", "self", 4121)])]),

    # the Dragonmaw's whelp, its driver, and Grrmlgrrl on the ridge
    dict(key="grrm_ridge", name="Grrmlgrrl the Tidehunter", subname="", look="murloc_slate", scale=1.15, level=30, role="quest",
         at="grrm_ridge", facing=4.76, phase=RIDGE, greeting="Down. Get down. Look. Look what they do.",
         watch=(25, [("state", "self", "none"), ("face", "self", "forge"), ("emote", "self", "point"), ("wait", 1500),
                     ("emote", "self", "roar"), ("sound", "self", "murloc_wound"), ("wait", 2500), ("state", "self", "kneel")], 45000),
         idle=[("state", "self", "kneel"), ("every", 30000, [("sound", "self", "murloc_fidget2")])]),
    dict(key="chained_whelp", name="Chained Red Whelp", look=9583, level=24, role="ambient", at="cage", facing=3.73,
         phase=WHELP, idle=[("every", 21000, [("sound", "self", 427)])]),
    dict(key="driver", name="Dragonmaw Whelp-Driver", look=4912, level=25, side="hostile", role="enemy", language="orcish",
         health=1.5, at="driver", facing=5.82, phase=WHELP, respawn=90,
         idle=[("every", 14000, [("emote", "self", "attack"), ("sound", "self", 3338), ("emote", "chained_whelp", "attack"),
                                 ("sound", "chained_whelp", 428)])]),
    dict(key="freed_whelp", name="Red Whelp", look=9583, level=24, role="ambient", summoned=True),
]

# -- things ----------------------------------------------------------------------------------------

EGG = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_01.mdx"
LOG = "World\\Azeroth\\SwampOSorrow\\PassiveDoodads\\TreeLogs\\SwampTreeLog01.mdx"

OBJECTS = [
    # the camp
    dict(key="campfire", model=192, name="Campfire", at=["hub_fire", "fire_2"], kind="doodad", phase=HUB),
    dict(key="hut", model=7517, name="Reed Hut", at=["hut_1", "hut_3"], kind="doodad", scale=0.8, facing=0.5, phase=HUB),
    dict(key="hut_big", model=7518, name="Reed Hut", at="hut_2", kind="doodad", scale=0.8, facing=1.2, phase=HUB),
    dict(key="cookpot", model=6849, name="Murlorga's Pot", at="cookpot", kind="doodad", scale=1.1, phase=HUB),
    dict(key="hollow_log", model=LOG, name="Hollow Log", at="blrrgl_log", kind="doodad", scale=0.6, facing=1.0, phase=HUB),
    dict(key="net_rack", model=6705, name="Drying Nets", at="net_rack", kind="doodad", facing=1.6, phase=HUB),
    dict(key="camp_crates", model=275, name="Salvage", at="crates", kind="doodad", phase=HUB),
    dict(key="anvil", model=273, name="Krrgl's Anvil", at="anvil", kind="doodad", phase=HUB),

    # the village
    dict(key="water_hut", model=7517, name="Bluegill Hut", at=["water_hut_1", "water_hut_2", "water_hut_3"], kind="doodad",
         scale=0.9),
    dict(key="chief_hut", model=7518, name="The Chief's Hut", at="blrrmuk_hut", kind="doodad", scale=1.4, facing=1.9),
    dict(key="gloop_hut", model=7517, name="The Oracle's Hut", at="gloop_hut", kind="doodad", scale=0.8, facing=4.0),
    dict(key="shell_throne", model=887, name="Shell Throne", at="throne", kind="doodad", scale=0.5),
    dict(key="egg_bed", model=EGG, name="Bluegill Eggs", at=["egg_1", "egg_2", "egg_3"], kind="doodad", scale=0.45),
    dict(key="contest_log", model=LOG, name="The Eating Log", at="contest_log", kind="doodad", scale=0.6, facing=0.3),
    dict(key="empty_seat", model=6833, name="An Empty Seat", at="empty_seat", kind="doodad", scale=0.4),

    # Menethil Harbor
    dict(key="rowboat", model=124, name="Bram's Rowboat", at="bram_boat", kind="doodad", facing=3.9),
    dict(key="buoy", model=6366, name="Harbour Buoy", at=["buoy_1", "buoy_2", "buoy_3"], kind="doodad", scale=1.2),
    dict(key="cart", model=6952, name="Bram's Cart", at="cart", kind="doodad", facing=2.2),

    # the Dragonmaw's (until the whelp is free)
    dict(key="forge", model=233, name="Dragonmaw Forge", at="forge", kind="doodad", facing=0.6, phase=WHELP),
    dict(key="orc_tent", model=8184, name="Dragonmaw Tent", at=["tent_1", "tent_2"], kind="doodad", facing=1.4, phase=WHELP),

    # the camp half-packed (while 4.24 is in the log)
    dict(key="pack_sack", model=5511, name="Bundle", at=["pack_1", "pack_3"], kind="doodad", phase=AMBUSH),
    dict(key="pack_crate", model=275, name="Bundle", at=["pack_2", "pack_4"], kind="doodad", scale=0.8, phase=AMBUSH),

    # what quests take
    dict(key="fen_moss", model=8084, name="Fen Moss", kind="loot", loot=[("fen_moss", 1, 1)], quest="ch4_moss", scale=0.7,
         at=["moss_1", "moss_2", "moss_3", "moss_4", "moss_5", "moss_6", "moss_7"]),
    dict(key="shoal", model=6291, name="Shoal of Bay Fish", kind="loot", loot=[("bay_fish", 1, 2)], quest="ch4_toll",
         at=["shoal_1", "shoal_2", "shoal_3", "shoal_4", "shoal_5", "shoal_6", "shoal_7", "shoal_8"]),
    dict(key="harbour_lantern", model=6038, name="Harbour Lantern", kind="loot", loot=[("harbour_lantern", 1, 1)],
         quest="ch4_lanterns", at=["lantern_1", "lantern_2", "lantern_3"]),
    dict(key="glint", model=261, name="Glinting Clam", kind="loot", loot=[("bram_ring", 1, 1)], quest="ch4_ring", at="ring"),
    dict(key="fen_mud", model=20, name="Fen Mud", kind="loot", loot=[("fen_mud", 1, 2)], quest="ch4_mud", scale=0.35,
         at=["mud_1", "mud_2", "mud_3", "mud_4", "mud_5", "mud_6", "mud_7", "mud_8"]),
    dict(key="glow_jelly", model=7756, name="Glow-Jelly", kind="loot", loot=[("glow_jelly", 1, 1)], quest="ch4_lights",
         scale=0.35, at=["glow_1", "glow_2", "glow_3", "glow_4", "glow_5", "glow_6", "glow_7"]),
    dict(key="market_crate", model=286, name="Crate of Fish", kind="loot", loot=[("fish_crate", 1, 1)], quest="ch4_raid",
         at=["market_1", "market_2", "market_3", "market_4", "market_5", "market_6", "market_7", "market_8"], phase=RAID),
    dict(key="egg_scrap", model=EGG, name="Glistening Scrap", kind="loot", loot=[("egg_jelly", 1, 1)], quest="ch4_jelly",
         scale=0.25, at=["jelly_shore_1", "jelly_shore_2", "jelly_shore_3", "jelly_shore_4", "jelly_shore_5", "jelly_shore_6",
                         "jelly_shore_7"]),
    dict(key="mudfish_hole", model=6322, name="Mudfish Hole", kind="loot", loot=[("mudfish", 1, 2)], quest="ch4_pot",
         scale=0.6, at=["mudfish_1", "mudfish_2", "mudfish_3", "mudfish_4", "mudfish_5", "mudfish_6"]),

    # what quests use (each a scene)
    dict(key="wound", model=6316, name="Grandmother Shellback's Wound", kind="use", quest="ch4_moss", consumable=False,
         scale=0.8, at="wound", phase=WOUNDED,
         beats=[("credit", "ch4_moss"), ("sound", "ch0:shellback", 1463), ("wait", 2500), ("sound", "ch0:shellback", 1485)]),
    dict(key="tackle_pile", model=275, name="Bram's Tackle", kind="use", quest="ch4_tackle", consumable=False, at="cart_crates",
         beats=[("give", "tackle_crate", 1), ("aura", "player", "crate_load")]),
    dict(key="whelp_cage", model=6858, name="Whelp Cage", kind="use", quest="ch4_whelp", at="cage", phase=WHELP,
         beats=[("credit", "ch4_whelp"), ("summon", "freed_whelp", "cage", 30), ("wait", 800), ("sound", "freed_whelp", 433),
                ("face", "freed_whelp", "player"), ("wait", 2500), ("sound", "freed_whelp", 428),
                ("move", "freed_whelp", "tent_1", "run"), ("wait", 3500), ("object", "flames", "tent_1", 60),
                ("sound", "freed_whelp", 429), ("move", "freed_whelp", "tent_2", "run"), ("wait", 3500),
                ("object", "flames", "tent_2", 60), ("sound", "freed_whelp", 429), ("wait", 1000),
                ("move", "freed_whelp", "whelp_away", "run"), ("sound", "freed_whelp", 433), ("wait", 9000),
                ("despawn", "freed_whelp")]),
    dict(key="platter", model=564, name="Contest Platter", kind="use", quest="ch4_eat", consumable=False, at="platter",
         beats=[("give", "fish_bones", 1), ("aura", "player", "overfull"), ("sound", "echo_pond", 45)]),
    dict(key="spawning_water", model=8565, name="The Spawning Water", kind="use", quest="ch4_lights", consumable=False,
         at="spawn_water",
         beats=[("give", "lit_water", 1), ("object", "jelly_light", "light_1", 150), ("object", "jelly_light", "light_2", 150),
                ("object", "jelly_light", "light_3", 150), ("object", "jelly_light", "light_4", 150),
                ("object", "jelly_light", "light_5", 150), ("music", 4454), ("summon", "swayer", "sway_1", 60),
                ("summon", "swayer", "sway_2", 60), ("summon", "swayer", "sway_3", 60), ("move", "ch1:elder", "pond_elder", "walk"),
                ("state", "ch1:murlorga", "none"), ("wait", 4000), ("move", "ch1:murlorga", "pond_murlorga", "walk"),
                ("wait", 7000), ("emote", "ch1:elder", "cry"), ("sound", "echo_pond", "murloc_fidget2"), ("wait", 16000),
                ("move", "ch1:elder", "elder", "walk"), ("move", "ch1:murlorga", "murlorga", "walk"), ("wait", 9000),
                ("state", "ch1:murlorga", "work")]),
    dict(key="spawning_water_b", model=8565, name="The Spawning Water", kind="use", quest="ch4_stolen_lights",
         consumable=False, at="spawn_water_b",
         beats=[("give", "lit_water_b", 1), ("object", "lantern_light", "light_1", 150),
                ("object", "lantern_light", "light_3", 150), ("object", "lantern_light", "light_4", 150), ("music", 4454),
                ("summon", "swayer", "sway_1", 60), ("summon", "swayer", "sway_2", 60), ("move", "ch1:elder", "pond_elder", "walk"),
                ("move", "ch1:blrrgl", "pond_blrrgl", "walk"), ("wait", 11000), ("emote", "ch1:elder", "cry"),
                ("sound", "echo_pond", "murloc_fidget2"), ("wait", 16000), ("move", "ch1:elder", "elder", "walk"),
                ("move", "ch1:blrrgl", "blrrgl", "walk")]),
    dict(key="war_drum", model=7217, name="Blrrmuk's War Drum", kind="use", quest="ch4_drum", at="war_drum",
         beats=[("give", "war_drum", 1), ("aura", "player", "drum_load"), ("sound", "echo_pond", 1183)]),
    dict(key="deep_water", model=6316, name="Deep Kelp", kind="use", quest="ch4_drum", consumable=False, scale=1.2,
         at="drum_deep", beats=[("take", "war_drum", 1), ("unaura", "player", "drum_load"), ("credit", "ch4_drum")]),
    dict(key="wallow", model=20, name="Mirelow's Wallow", kind="use", quest="ch4_mirelow", scale=0.9, at="wallow",
         beats=[("take", "raw_meat", 1), ("object", "bait", "wallow", 60), ("wait", 3000),
                ("summon", "mirelow", "wallow_rise", 180)]),
    dict(key="reed_nest", model=7202, name="Reed Nest", kind="use", quest="ch4_mirelow", scale=0.5, at="nest",
         beats=[("summon", "squeep", "nest", 180), ("credit", "ch4_mirelow")]),
    dict(key="boarding_rock", model=2251, name="Barnacled Rock", kind="use", quest="ch4_end", consumable=False, at="flipper",
         beats=[("credit", "ch4_end"), ("state", "ch1:glubbub", "none"), ("emote", "ch1:glubbub", "spell"),
                ("sound", "echo_cove", 3439), ("wait", 3000), ("sound", "echo_cove", 7054), ("visual", "ch0:shellback", 36005),
                ("wait", 2500), ("sound", "echo_cove", 1464), ("wait", 6000), ("state", "ch1:glubbub", "sit")]),

    # set out by scenes
    dict(key="basket", model=468, name="Toll Basket", kind="doodad", scale=1.2),
    dict(key="flames", model=200, name="Burning Tent", kind="doodad", scale=0.8),
    dict(key="mud_heap", model=20, name="Mud Throne", kind="doodad", scale=0.8),
    dict(key="mud_heap_big", model=20, name="Mud Throne", kind="doodad", scale=1.5),
    dict(key="jelly_light", model=7639, name="Glow-Jelly Light", kind="doodad", scale=0.6),
    dict(key="lantern_light", model=6038, name="Stolen Lantern", kind="doodad"),
    dict(key="sand_drum", model=7533, name="Drawing in the Mud", kind="doodad", scale=0.3),
    dict(key="sand_town", model=7194, name="Drawing in the Mud", kind="doodad", scale=0.12),
    dict(key="sand_bones", model=758, name="Drawing in the Mud", kind="doodad", scale=0.9),
    dict(key="sand_ship", model=124, name="Drawing in the Sand", kind="doodad", scale=0.15),
    dict(key="sand_net", model=6808, name="Drawing in the Sand", kind="doodad", scale=0.12),
    dict(key="held_scrap", model=EGG, name="Glistening Scrap", kind="doodad", scale=0.25),
    dict(key="ring_shine", model=2614, name="Wedding Ring", kind="doodad", scale=0.12),
    dict(key="hooks", model=7771, name="Iron Fishhooks", kind="doodad"),
    dict(key="eaten_vest", model=2890, name="Shark-Hide Vest, Bottom Eaten", kind="doodad", scale=0.7),
    dict(key="new_vest", model=2890, name="Raptor-Hide Vest", kind="doodad", scale=0.8),
    dict(key="bait", model=4321, name="Bloody Bait", kind="doodad", scale=1.3),
]

# -- items -----------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for (their names are the one thing a murloc reads)
    dict(key="fen_moss", name="Fen Moss", icon="item:3256", stack=6),
    dict(key="bay_fish", name="Bay Fish", icon="item:6303", stack=10),
    dict(key="harbour_lantern", name="Harbour Lantern", icon="item:5323", stack=3, description="Warm. Swinging. Not yours."),
    dict(key="bram_ring", name="Wedding Ring", icon="item:5538", description="Plain gold, worn thin by forty years on one finger."),
    dict(key="tackle_crate", name="Crate of Tackle", icon="item:4629", description="Hooks, lines, floats and one boot."),
    dict(key="chain_link", name="Dragonmaw Chain Link", icon="item:3156", stack=8),
    dict(key="fen_mud", name="Lump of Fen Mud", icon="item:3506", stack=10, description="It is warm. Do not ask why."),
    dict(key="fish_bones", name="Fish Bones", icon="item:4874", stack=8),
    dict(key="glow_jelly", name="Glow-Jelly", icon="item:12291", stack=5),
    dict(key="lit_water", name="Lights on the Spawning Water", icon="item:1434"),
    dict(key="lit_water_b", name="Lanterns on the Spawning Water", icon="item:5323"),
    dict(key="tail_fish", name="A Fish, Tail-First", icon="item:6303",
         description="Turned with great care. The worst thing one murloc can hand another."),
    dict(key="war_drum", name="Blrrmuk's War Drum", icon="item:30432", description="Heavy. Loud. Soon wet."),
    dict(key="fish_crate", name="Crate of Menethil Fish", icon="item:4629", stack=8),
    dict(key="raw_meat", name="Bloody Bait", icon="item:769", description="Mirelow is old, but his nose is young."),
    dict(key="egg_jelly", name="Scrap of Egg-Jelly", icon="item:4757", stack=6,
         description="It still glows, faintly. The clutch passed this way."),
    dict(key="bram_letter", name="Bram's Letter", icon="letter",
         description="To Hester Gale, Southshore. On the back, in pencil: a cottage by the sea, and a woman in a bonnet."),
    dict(key="mottled_hide", name="Mottled Raptor Hide", icon="item:4461", stack=8),
    dict(key="mudfish", name="Marsh Mudfish", icon="item:6289", stack=10),

    # rewards (levels 25 to 29: the game's quests' greens at these levels)
    dict(key="mossback_wraps", name="Mossback Wristwraps", kind="armor:cloth:wrist", quality=2, level=25,
         stats=[("int", 3), ("spi", 3)]),
    dict(key="scute_bracers", name="Turtle-Scute Bracers", kind="armor:leather:wrist", quality=2, level=25,
         stats=[("agi", 3), ("sta", 3)]),
    dict(key="barnacle_bracers", name="Barnacled Bracers", kind="armor:mail:wrist", quality=2, level=25,
         stats=[("str", 3), ("sta", 3)]),
    dict(key="keeper_mitts", name="Egg-Keeper's Mitts", kind="armor:cloth:hands", quality=2, level=25,
         stats=[("int", 4), ("sta", 2)]),
    dict(key="reed_gloves", name="Reed-Stalker Gloves", kind="armor:leather:hands", quality=2, level=25,
         stats=[("agi", 4), ("sta", 2)]),
    dict(key="gnollbane_gauntlets", name="Gnollbane Gauntlets", kind="armor:mail:hands", quality=2, level=25,
         stats=[("str", 4), ("sta", 2)]),
    dict(key="dock_ring", name="Dock-Thief's Ring", kind="ring", quality=2, level=25, stats=[("agi", 3), ("sta", 3)]),
    dict(key="whelpfire_cloak", name="Whelpfire Cloak", kind="armor:cloth:back", quality=2, level=26,
         stats=[("sta", 3), ("agi", 3)]),
    dict(key="singed_mantle", name="Singed Mantle", kind="armor:cloth:shoulder", quality=2, level=26,
         stats=[("int", 4), ("sta", 3)]),
    dict(key="chainbreaker_pauldrons", name="Chainbreaker Pauldrons", kind="armor:mail:shoulder", quality=2, level=26,
         stats=[("str", 4), ("sta", 3)]),
    dict(key="chain_flail", name="Chain-Link Flail", kind="weapon:mace", quality=2, level=26, stats=[("str", 4), ("sta", 3)]),
    dict(key="gutting_hook", name="Dragonmaw-Iron Gutting Hook", kind="weapon:dagger", quality=2, level=26,
         stats=[("agi", 3), ("sta", 3)]),
    dict(key="muck_crown", name="Muck-Eater's Crown", kind="armor:cloth:head", quality=2, level=27,
         stats=[("sta", 5), ("spi", 4)], description="It is a fish head. It was a crown. It is still a fish head."),
    dict(key="drumskin_leggings", name="Drumskin Leggings", kind="armor:leather:legs", quality=2, level=27,
         stats=[("agi", 6), ("sta", 4)]),
    dict(key="tidewatcher_kilt", name="Tidewatcher's Kilt", kind="armor:cloth:legs", quality=2, level=27,
         stats=[("int", 6), ("spi", 4)]),
    dict(key="quiet_legguards", name="Quiet Drummer's Legguards", kind="armor:mail:legs", quality=2, level=27,
         stats=[("str", 6), ("sta", 4)]),
    dict(key="raider_leggings", name="Market-Raider's Leggings", kind="armor:leather:legs", quality=2, level=27,
         stats=[("agi", 5), ("sta", 5)]),
    dict(key="sailcloth_trousers", name="Stolen Sailcloth Trousers", kind="armor:cloth:legs", quality=2, level=27,
         stats=[("int", 5), ("sta", 5)]),
    dict(key="crate_legguards", name="Crate-Smasher Legguards", kind="armor:mail:legs", quality=2, level=27,
         stats=[("str", 5), ("sta", 5)]),
    dict(key="mirelow_tooth", name="Mirelow's Tooth", kind="neck", quality=2, level=27, stats=[("str", 4), ("agi", 4)]),
    dict(key="mothers_thanks", name="A Mother's Thanks", kind="neck", quality=2, level=27, stats=[("int", 4), ("spi", 4)]),
    dict(key="raptor_jerkin", name="Raptorhide Jerkin", kind="armor:leather:chest", quality=2, level=28,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="raptor_hauberk", name="Raptorscale Hauberk", kind="armor:mail:chest", quality=2, level=28,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="raptor_robe", name="Sharkskin-and-Raptor Robe", kind="armor:cloth:chest", quality=2, level=28,
         stats=[("int", 6), ("spi", 5)]),
    dict(key="war_spear", name="Saltscar War-Spear", kind="weapon:spear", quality=2, level=29, stats=[("str", 8), ("sta", 6)],
         description="Grrmlgrrl's coral spear again: longer now, and tipped with Dragonmaw iron."),
    dict(key="gutting_knife", name="Bluegill Gutting Knife", kind="weapon:dagger", quality=2, level=29,
         stats=[("agi", 5), ("sta", 4)]),
    dict(key="oracle_staff", name="Driftwood Oracle's Staff", kind="weapon:staff", quality=2, level=29,
         stats=[("int", 8), ("spi", 6)]),
    dict(key="rider_cloak", name="Shell-Rider's Cloak", kind="armor:cloth:back", quality=2, level=29,
         stats=[("agi", 4), ("sta", 4)]),
    dict(key="barnacle_cloak", name="Barnacle-Studded Cloak", kind="armor:cloth:back", quality=2, level=29,
         stats=[("int", 4), ("sta", 4)]),
]

# -- auras -----------------------------------------------------------------------------------------

AURAS = [
    dict(key="hiccups", name="Hiccups", kind="mark", seconds=120, icon=55664, visual=6502, text="Hic! Bram's flask. Hic!"),
    dict(key="overfull", name="Overfull", kind="slow", percent=30, seconds=60, icon=45548, text="Too much fish. Far too much fish."),
    dict(key="crate_load", name="Heavy Crate", kind="slow", percent=25, seconds=120, icon=4055, text="A crate of tackle on your back."),
    dict(key="drum_load", name="Hauling a War Drum", kind="slow", percent=35, seconds=180, icon=35476,
         text="Blrrmuk's war drum, bumping on your back."),
    dict(key="fish_crown", name="Muck-Eater", kind="mark", seconds=900, icon=51072,
         text="The Bluegill crowned you with a fish head."),
    dict(key="dozing", name="The Long Swim", kind="stun", seconds=7, icon=64731, visual=308,
         text="Rocked to sleep on Grandmother Shellback's shell."),
]

# -- more of those already made: the hub kit, the turtle, Bram; the game's creatures in the murlocs' phase --

SPAWNS = [
    # the camp's own (the hub kit, bible 17.1), from the landing on; the Elder until he dies (9.21)
    dict(npc="ch1:elder", at="elder", phase=ELDER, facing=3.66),
    dict(npc="ch1:grrmlgrrl", at="grrmlgrrl", phase=HUB, facing=2.5, state="none"),
    dict(npc="ch1:murlorga", at="murlorga", phase=HUB, facing=4.02),
    dict(npc="ch1:blrrgl", at="blrrgl", phase=HUB, facing=0.43),
    dict(npc="ch1:glubbub", at="glubbub", phase=HUB, facing=1.57),
    dict(npc="ch1:brrgmrk", at="brrgmrk", phase=HUB, facing=5.3),
    dict(npc="ch1:mrrgasha", at="mrrgasha", phase=HUB, facing=5.06),
    dict(npc="ch1:glubba", at="glubba", phase=HUB, facing=4.49),
    dict(npc="ch1:fizzmrgl", at="fizzmrgl", phase=HUB, facing=3.99),
    dict(npc="ch1:slubb", at="slubb", phase=HUB, facing=1.14),
    dict(npc="ch1:gurgle", at="gurgle", phase=HUB, facing=1.36),
    dict(npc="ch1:mrrlglr", at="mrrlglr", phase=HUB, facing=6.09),
    dict(npc="ch0:mrsha", at="mrsha", phase=HUB, facing=0.38),
    dict(npc="ch0:brewglub", at="brewglub", phase=HUB, facing=1.05),
    dict(npc="ch0:grrsh", at="grrsh", phase=HUB, facing=1.79),
    dict(npc="ch0:mrrsk", at="mrrsk", phase=HUB, facing=2.3),
    dict(npc="ch0:brrkl", at="brrkl", phase=HUB, facing=2.74),
    dict(npc="ch0:krrgl", at="krrgl", phase=HUB, facing=5.3),
    dict(npc="ch0:mmrglla", at="mmrglla", phase=HUB, facing=1.08),
    dict(npc="ch0:sprokgl", at="sprokgl", phase=HUB, facing=1.45),
    dict(npc="ch0:shimmrl", at="shimmrl", phase=HUB, facing=1.79),
    dict(npc="ch0:pearlmrgl", at="pearlmrgl", phase=HUB, facing=2.1),
    dict(npc="ch0:scrawlgl", at="scrawlgl", phase=HUB, facing=2.42),
    dict(npc="ch0:fnrrgl", at="fnrrgl", phase=HUB, facing=2.71),
    dict(npc="ch0:caller", at="caller", phase=HUB, facing=5.08),
    dict(npc="ch0:mrrk", at="mrrk", phase=HUB, facing=5.3, state="sit"),
    dict(object="ch0:mailbox", at="mailbox", phase=HUB, facing=0.4),
    # Grandmother Shellback in the cove: wounded until 4.03, healed until she carries the tribe north (4.25)
    dict(npc="ch0:shellback", at="shellback", phase=WOUNDED, facing=4.32),
    dict(npc="ch0:shellback", at="shellback", phase=HEALED, facing=4.32),
    # Bram Coldkettle, in his rowboat off the end of Menethil's main pier (always there)
    dict(npc="ch0:bram", at="bram", facing=3.93),
    # Grrmlgrrl stays on the ridge from 4.09's reward until the whelp is free
    dict(npc="grrm_ridge", at="grrm_ridge", phase=RIDGE_AFTER, facing=4.76),
    # the crocolisks circling the turtle (4.02), the gnolls at the egg-beds (4.05)
    dict(npc=1400, at=["croc_1", "croc_2", "croc_3", "croc_4", "croc_5", "croc_6"], phase=CROCS, wander=5.0, respawn=30),
    dict(npc=1011, at=["gnoll_1", "gnoll_3"], phase=GNOLLS, wander=4.0, respawn=45),
    dict(npc=1010, at=["gnoll_2", "gnoll_4"], phase=GNOLLS, wander=4.0, respawn=45),
]

GRAVEYARDS = [
    dict(at="graveyard", name="Saltscar Shallows", phase=HUB, facing=5.59),
]

# -- the quests ------------------------------------------------------------------------------------

TAPS = [("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977),
        ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977)]

QUESTS = [
    # 4.01: landfall (the hub becomes the tribe's at its reward)
    dict(key="ch4_arrival", title="Landfall", giver="ch1:elder", ender="ch1:elder", level=24, xp=8, tone="serious",
         prev="ch3:ch3_end",
         emotes=[("drowned_cough", "pat", 2, [("state", "self", "none"), ("sound", "self", 1197), ("emote", "self", "beg"),
                                              ("sound", "self", "murloc_wound"), ("wait", 1200), ("sound", "self", 1197),
                                              ("give", 6303, 1), ("emote", "self", "talk"), ("wait", 2000), ("emote", "self", "yes"),
                                              ("wait", 15000), ("state", "self", "sleep")]),
                 ("drowned_hug", "pat", 2, [("state", "self", "none"), ("emote", "self", "question"),
                                            ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "kiss"),
                                            ("wait", 1200), ("state", "self", "kneel"), ("sound", "self", "murloc_fidget2"),
                                            ("wait", 16000), ("state", "self", "sleep")]),
                 ("drowned_net", "pat", 2, [("state", "self", "sit"), ("face", "self", "sea"), ("emote", "self", "beg"),
                                            ("wait", 2500), ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"),
                                            ("wait", 16000), ("state", "self", "sleep")])],
         goal="Rouse the 6 half-drowned Saltscar lying on the beach by the cove: /pat each one until they stir.",
         text="The sea... the sea let us go. Most of us. 6 still lie on the sand, too tired to stand. "
              "Wake them, little one. Gently. Then we see where we are.",
         progress="All 6? Even the one with the net?",
         reward="6. Good. Mm... good. Here, then. Here we stop. Here we dry out.",
         details=["beg", "point", "no"], reward_emotes=["bow", "point"],
         accept=[("sound", "self", 1197), ("emote", "self", "beg"), ("sound", "self", "murloc_wound"), ("wait", 1500),
                 ("face", "self", "body_1"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "body_4"),
                 ("emote", "self", "point"), ("wait", 1200), ("face", "self", "body_6"), ("emote", "self", "point"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "no"), ("sound", "self", 1114),
                 ("wait", 1500), ("face", "self", "hub_fire")],
         complete=TAPS + [("wait", 1200), ("face", "self", "hub_fire"), ("emote", "self", "point"),
                          ("say", "self", "Here. Here we stop.", "point", "murloc_fidget2"), ("music", 4454), ("wait", 2500),
                          ("face", "self", "shellback"), ("emote", "self", "bow")],
         poi=["body_3"]),

    # 4.02: blood in the water
    dict(key="ch4_blood", title="Blood in the Water", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=24, xp=8,
         tone="serious", path="hero", prev="ch4_arrival", kill=[(1400, 10)],
         goal="Kill 10 Wetlands Crocolisks circling Grandmother Shellback in the cove.",
         text="The long swim cut her. The rocks at the edge of the world... Grandmother bleeds, and the snouts smell it. "
              "10 crocolisks, circling. Kill them before they bite.",
         progress="I hear teeth in the water.",
         reward="No more snouts. Good. She does not thank us. Turtles don't. But she lives.",
         details=["roar", "point"], reward_emotes=["flex", "salute"],
         accept=[("emote", "self", "roar"), ("sound", "self", "murloc_aggro"), ("move", "self", "grrm_cove", "run"),
                 ("wait", 4000), ("face", "self", "shellback"), ("emote", "self", "attack2h"), ("sound", "self", 1460),
                 ("wait", 900), ("emote", "self", "attack2h"), ("sound", "self", "murloc_attack"), ("wait", 900),
                 ("emote", "self", "attack2h"), ("wait", 1500), ("emote", "self", "point"), ("wait", 2000),
                 ("move", "self", "grrmlgrrl", "walk"), ("wait", 6000), ("face", "self", "hub_fire")],
         complete=[("emote", "self", "flex"), ("sound", "self", "murloc_fidget"), ("wait", 900), ("emote", "self", "flex"),
                   ("wait", 900), ("face", "self", "player"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "roar"),
                   ("sound", "self", "murloc_aggro"), ("emote", "ch1:murlorga", "cheer"), ("emote", "ch1:blrrgl", "cheer")],
         poi=["shellback"]),

    # 4.03: moss for the wound
    dict(key="ch4_moss", title="Moss for the Wound", giver="ch1:slubb", ender="ch1:slubb", level=25, xp=8, tone="serious",
         path="hero", prev="ch4_blood", items=[("fen_moss", 6)], event="Moss pressed into Grandmother Shellback's wound",
         goal="Gather 6 Fen Moss in the marsh pools around the camp, then press it into Grandmother Shellback's wound in the cove.",
         text="A wound wants something soft and something tight. Fen moss, from the marsh pools. 6 handfuls. "
              "Press it in, all of it. Don't stop if she flinches. She will flinch.",
         progress="Soft and tight. Soft... and tight.",
         reward="There. Hear that? That is a turtle saying thank you. Or snoring. With turtles you never know.",
         details=["work", "point"], reward_emotes=["bow", "cheer"],
         choice=["mossback_wraps", "scute_bracers", "barnacle_bracers"],
         accept=[("emote", "self", "work"), ("sound", "self", 1187), ("wait", 1500), ("emote", "self", "work"),
                 ("sound", "self", 1187), ("wait", 1200), ("emote", "self", "flex"), ("wait", 1200),
                 ("face", "self", "shellback"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "moss_5"),
                 ("emote", "self", "point"), ("wait", 1500), ("face", "self", "shellback")],
         complete=[("face", "self", "shellback"), ("sound", "self", 1485), ("wait", 1500), ("sound", "self", 1463),
                   ("emote", "self", "bow"), ("wait", 2000), ("emote", "self", "cheer"), ("sound", "self", "murloc_fidget")],
         poi=["moss_5", "wound"]),

    # 4.04: the Bluegill toll
    dict(key="ch4_toll", title="The Bluegill Toll", giver="blrrmuk", ender="blrrmuk", level=24, xp=8, tone="boring",
         prev="ch4_arrival", items=[("bay_fish", 10)], money=1,
         goal="Net 10 Bay Fish from the shoals in the bay off the camp for Chief Blrrmuk.",
         text="You sleep on my beach, you pay. 10 fish. Big ones. In the basket. "
              "The sea is full of fish, and my belly is full of nothing.",
         progress="The basket is empty. I am looking at it. It is still empty.",
         reward="Mm. Mm. Mmmm. ...You may sleep on my beach. One more night.",
         details=["point", "beg"], reward_emotes=["eat", "eat"],
         accept=[("state", "self", "none"), ("object", "basket", "toll_basket", 60), ("emote", "self", "point"), ("sound", "self", 977),
                 ("wait", 1000), ("face", "self", "shoal_3"), ("emote", "self", "point"), ("sound", "self", 977), ("wait", 1000),
                 ("face", "self", "toll_basket"), ("emote", "self", "point"), ("sound", "self", 977), ("wait", 1200),
                 ("face", "self", "player"), ("emote", "self", "beg"), ("wait", 1500), ("face", "self", "pond"),
                 ("state", "self", "sit")],
         complete=[("face", "self", "pond"), ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 900), ("emote", "self", "eat"),
                   ("sound", "self", 45), ("wait", 900), ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 900),
                   ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 900), ("emote", "self", "eat"), ("sound", "self", 45),
                   ("wait", 900), ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 900), ("emote", "self", "eat"),
                   ("sound", "self", 45), ("wait", 900), ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 900),
                   ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 900), ("emote", "self", "eat"), ("sound", "self", 45),
                   ("wait", 1200), ("sound", "self", "murloc_fidget2"), ("emote", "guard_a", "laugh")],
         poi=["shoal_3", "shoal_6"]),

    # 4.05: gnolls eat eggs
    dict(key="ch4_gnolls", title="Gnolls Eat Eggs", giver="plubba", ender="plubba", level=25, xp=8, tone="serious",
         path="hero", prev="ch4_toll", kill=[(1011, 5), (1010, 4), ("egg_thief", 1)],
         goal="Kill 5 Mosshide Trappers, 4 Mosshide Fenrunners and the Mosshide Egg-Thief raiding the Bluegill egg-beds "
              "from the reeds east of the pond.",
         text="The dog-faces come at night. They sniff the beds... and the eggs go crunch. 10 of them, little one. "
              "And that one, in the reeds, eating them like apples. Him first.",
         progress="I counted the eggs. Then I counted again. Then I stopped counting.",
         reward="Quiet reeds. Quiet beds. ...Thank you. Your tribe has no eggs, they say. I am sorry. I am so sorry.",
         details=["cry", "point"], reward_emotes=["cheer", "cry"],
         choice=["keeper_mitts", "reed_gloves", "gnollbane_gauntlets"],
         accept=[("state", "self", "none"), ("emote", "self", "cry"), ("sound", "self", "baby_murloc"), ("wait", 1200),
                 ("face", "self", "gnoll_reeds"), ("emote", "self", "point"), ("wait", 1500), ("emote", "egg_thief", "eat"),
                 ("sound", "egg_thief", 45), ("wait", 1500), ("emote", "self", "cry"), ("wait", 1000), ("face", "self", "egg_1"),
                 ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", "baby_murloc"), ("wait", 1500),
                   ("face", "ch1:elder", "sea"), ("wait", 1000), ("emote", "self", "cry"), ("wait", 1500), ("state", "self", "sit")],
         poi=["gnoll_reeds"]),

    # 4.06: lanterns of Menethil (Blrrgl's road)
    dict(key="ch4_lanterns", title="Lanterns of Menethil", giver="ch1:blrrgl", ender="ch1:blrrgl", level=25, xp=8,
         tone="funny", path="menace", prev="ch4_arrival", items=[("harbour_lantern", 3)], rep=[(47, -250)],
         goal="Steal the 3 Harbour Lanterns from the buoys by Menethil Harbor's docks. The dock sentries shout when you come "
              "close: don't let them reach you.",
         text="Lights. Little lights on the water, by the dry-skins' town. Shiny. Warm. Swinging... 3 of them. "
              "For the festival! Mostly for the festival.",
         progress="Swing, swing, swing... are they swinging in your hands yet?",
         reward="Ooooh. Warm. Warm and shiny. Into the log. The festival can borrow them. Borrow!",
         details=["exclamation", "beg"], reward_emotes=["laugh", "beg"], rewards=["dock_ring"],
         accept=[("face", "self", "bram"), ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 1500),
                 ("emote", "self", "talk"), ("wait", 1200), ("state", "self", "dance"), ("sound", "self", "murloc_fidget"),
                 ("wait", 3000), ("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "beg"), ("wait", 1500),
                 ("face", "self", "hub_fire")],
         complete=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2"), ("move", "self", "blrrgl_log", "walk"),
                   ("wait", 2500), ("emote", "self", "kneel"), ("sound", "self", 1221), ("wait", 1500),
                   ("move", "self", "blrrgl", "walk"), ("wait", 2500), ("face", "self", "hub_fire")],
         poi=["lantern_1", "lantern_2", "lantern_3"]),

    # 4.07: Bram's ring (the hero's road into Menethil, from the water)
    dict(key="ch4_ring", title="Bram's Ring", giver="ch1:blrrgl", ender="ch0:bram", level=25, xp=8, tone="serious",
         path="hero", prev="ch4_arrival", items=[("bram_ring", 1)], rep=[(47, 500)],
         goal="Find what Bram Coldkettle lost on the harbour floor below the end of Menethil's main pier, and bring it to "
              "him in his rowboat.",
         text="A dry-skin sits in a little boat at the end of the long wooden walk. Every night. Every night he cries into "
              "his beard! Something of his is down in the water. Something shiny... Find it. Give it back. "
              "Yes. BACK. Don't look at me like that.",
         progress="Is he still crying? He cries a lot, for a dry-skin.",
         reward="Och. Och, lad. Och, Martha. Forty years, an' it slipped right off me finger like a wee fish.",
         details=["point", "cry", "no"], reward_emotes=["cry", "cheer"], rewards=[6256],
         accept=[("face", "self", "bram"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "cry"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "laugh"), ("wait", 1000),
                 ("emote", "self", "beg"), ("wait", 1500), ("emote", "self", "no"), ("wait", 1000), ("face", "self", "hub_fire")],
         complete=[("state", "self", "none"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "ring"),
                   ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "bow"), ("wait", 1200),
                   ("object", "ring_shine", "ring_dock", 30), ("sound", "self", 1193), ("wait", 1000), ("face", "self", "player"),
                   ("emote", "self", "exclamation"), ("sound", "self", 2725), ("wait", 1500), ("emote", "self", "cry"),
                   ("wait", 1500), ("music", 11806), ("emote", "self", "laugh"), ("wait", 2000), ("state", "self", "sit")],
         poi=["ring"]),

    # 4.08: Bram's tackle (boring; the docks' sentries shout at everyone who passes)
    dict(key="ch4_tackle", title="Bram's Tackle", giver="ch0:bram", ender="ch0:bram", level=26, xp=8, tone="boring",
         path="hero", prev="ch4_ring", use=[("tackle_crate", "ch0:bram", 4)], rep=[(47, 250)],
         goal="Carry 4 Crates of Tackle, one at a time, from Bram's cart on the shore north of Menethil to his rowboat "
              "off the main pier. Keep clear of the docks' sentries.",
         text="Me knees, lad. Forty years o' haulin' nets an' they've gone tae porridge. Me tackle's in the cart up the "
              "shore, past the horse pens. 4 crates, one at a time. An' mind the lads on the docks.",
         progress="One at a time, lad. Me knees an' yer back both.",
         reward="That's the lot! Here, have a wee nip. Go on. It'll put hair on yer... well. On somethin'.",
         details=["point", "talk"], reward_emotes=["laugh", "cheer"], rewards=[2686],
         accept=[("state", "self", "none"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "cart"),
                 ("emote", "self", "point"), ("wait", 1200), ("face", "self", "player"), ("emote", "self", "point"),
                 ("wait", 1200), ("sound", "self", 7918), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "eat"), ("sound", "self", 3373), ("wait", 1500),
                   ("emote", "self", "laugh"), ("aura", "player", "hiccups"), ("wait", 1200), ("sound", "self", 2725),
                   ("emote", "self", "cheer"), ("wait", 1500), ("state", "self", "sit")],
         poi=["cart"]),

    # 4.09: chains on the hill
    dict(key="ch4_chains", title="Chains on the Hill", giver="ch1:grrmlgrrl", ender="grrm_ridge", level=26, xp=8,
         tone="serious", prev="ch4_moss", explore="ridge", radius=20,
         goal="Join Grrmlgrrl on the ridge above the Dragonmaw's Angerfang Encampment, far to the east, and look down.",
         text="Smoke. Over the hills, to the east. And a sound... a whip. I know that sound. "
              "I go ahead. Follow me, low and quiet. Look. Then we decide.",
         progress="...",
         reward="A slave. A little dragon, in chains, breathing on their iron. ...I wore chains. I know that face.",
         details=["point", "roar"], reward_emotes=["roar", "point"],
         accept=[("face", "self", "east"), ("emote", "self", "point"), ("wait", 1500), ("sound", "self", 3338), ("wait", 800),
                 ("emote", "self", "roar"), ("sound", "self", "murloc_wound"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("wait", 2000), ("face", "self", "hub_fire")],
         complete=[("state", "self", "none"), ("face", "self", "forge"), ("emote", "self", "point"), ("wait", 1500),
                   ("emote", "self", "cry"), ("wait", 1500), ("emote", "self", "roar"), ("sound", "self", "murloc_wound_crit"),
                   ("wait", 2000), ("state", "self", "kneel")],
         poi=["ridge"]),

    # 4.10: the whelp in the cage
    dict(key="ch4_whelp", title="The Whelp in the Cage", giver="grrm_ridge", ender="ch1:grrmlgrrl", level=26, xp=8,
         tone="serious", path="hero", prev="ch4_chains", kill=[(1034, 5), (1057, 3)], event="The red whelp freed",
         goal="Kill 5 Dragonmaw Raiders and 3 Dragonmaw Bonewarders at the Angerfang Encampment and open the whelp's cage "
              "by the forge. Then tell Grrmlgrrl at the camp.",
         text="Kill their whips. 8 of them. Then open the cage. Nobody stays in a cage. Nobody. "
              "Not a murloc, not a little dragon.",
         progress="Is the cage open?",
         reward="The smoke over the hills is bigger. Much bigger. Ha! HA! The little one bit back.",
         details=["flex", "point"], reward_emotes=["roar", "salute"],
         choice=["whelpfire_cloak", "singed_mantle", "chainbreaker_pauldrons"],
         accept=[("state", "self", "none"), ("emote", "self", "flex"), ("wait", 900), ("emote", "self", "flex"),
                 ("face", "self", "player"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "cage"),
                 ("emote", "self", "point"), ("sound", "self", "murloc_aggro"), ("wait", 2000), ("state", "self", "kneel")],
         complete=[("face", "self", "east"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "roar"),
                   ("sound", "self", "murloc_aggro"), ("emote", "ch1:murlorga", "cheer"), ("emote", "ch1:blrrgl", "cheer"),
                   ("emote", "ch0:mrrk", "cheer"), ("wait", 2000), ("face", "self", "player"), ("emote", "self", "salute"),
                   ("wait", 1500), ("face", "self", "hub_fire")],
         poi=["cage"]),

    # 4.11: Dragonmaw iron
    dict(key="ch4_iron", title="Dragonmaw Iron", giver="ch0:krrgl", ender="ch0:krrgl", level=26, xp=8, tone="boring",
         prev="ch4_chains", items=[("chain_link", 8)], drops={"chain_link": [(1034, 40), (1057, 40)]},
         goal="Bring Krrgl 8 Dragonmaw Chain Links from the Dragonmaw Raiders and Bonewarders at the Angerfang Encampment.",
         text="Their chains are good iron. Better than naga steel. Bring me their links, 8 of them... "
              "the ones they won't need, after. Hooks. I make hooks.",
         progress="Iron. Iron, iron. Where is my iron?",
         reward="Bites like good iron. Tastes like good iron. Watch. Watch the chain become a hook.",
         details=["eat", "yes"], reward_emotes=["work", "yes"], choice=["chain_flail", "gutting_hook"],
         accept=[("state", "self", "none"), ("emote", "self", "eat"), ("sound", "self", 1194), ("wait", 1500),
                 ("emote", "self", "yes"), ("wait", 1000), ("face", "self", "east"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "anvil"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("face", "self", "anvil"), ("emote", "self", 467), ("sound", "self", 4614),
                   ("wait", 1200), ("emote", "self", 467), ("sound", "self", 4614), ("wait", 1200),
                   ("object", "hooks", "hooks_spot", 40), ("move", "self", "grrmlgrrl", "walk"), ("wait", 9000),
                   ("emote", "self", "bow"), ("emote", "ch1:grrmlgrrl", "salute"), ("wait", 2500), ("move", "self", "krrgl", "walk"),
                   ("wait", 9000), ("face", "self", "anvil"), ("state", "self", "work")],
         poi=["forge"]),

    # 4.12: Muckfest, the mud throne
    dict(key="ch4_mud", title="Muckfest: Mud for the Throne", giver="muckmaw", ender="muckmaw", level=26, xp=8,
         tone="funny", prev="ch4_gnolls", items=[("fen_mud", 10)],
         goal="Bring Muckmaw 10 Lumps of Fen Mud from the pond and the marsh pools around the camp.",
         text="Muckfest! The chief needs a throne. A throne of MUD! The deepest, stinkiest, best mud in the marsh. "
              "10 lumps. Go, go, go!",
         progress="Is it stinky? It must be stinky.",
         reward="Oh, that is good mud. That is chief mud. Smell it! No... really smell it.",
         details=["dance", "point"], reward_emotes=["cheer", "dance"],
         accept=[("object", "mud_heap", "mud_throne", 45), ("move", "self", "mud_throne", "walk"), ("wait", 2500),
                 ("emote", "self", "work"), ("sound", "self", 1197), ("wait", 1200), ("state", "self", "sit"),
                 ("sound", "self", 1090), ("wait", 2500), ("state", "self", "none"), ("emote", "self", "laugh"),
                 ("sound", "self", "murloc_fidget"), ("face", "self", "mud_5"), ("emote", "self", "point"), ("wait", 1500),
                 ("move", "self", "muckmaw", "walk"), ("wait", 2500), ("face", "self", "pond")],
         complete=[("object", "mud_heap_big", "throne", 120), ("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"),
                   ("wait", 1200), ("emote", "blrrmuk", "eat"), ("sound", "blrrmuk", "murloc_fidget2"), ("wait", 1200),
                   ("emote", "self", 94)],
         poi=["mud_1", "mud_5"]),

    # 4.13: Muckfest, a thousand fins
    dict(key="ch4_conga", title="Muckfest: A Thousand Fins", giver="muckmaw", ender="muckmaw", level=26, xp=8, tone="funny",
         prev="ch4_mud",
         emotes=[("bluegill", "dance", 6, [("emote", "self", 94), ("sound", "self", "murloc_fidget"),
                                           ("summon", "conga", "pond", 45)])],
         goal="/dance with 6 Bluegill in the village by the pond: each one you dance with joins the line behind you.",
         text="Now! Now we dance! Every fin, every tail. Dance with them, little one... "
              "6 of them, and they'll follow you anywhere. That is how a Muckfest line grows.",
         progress="Dance! Why aren't you dancing?",
         reward="A line! A beautiful long wiggly line! Even the big grumpy one. Look at him go!",
         details=["dance", "point"], reward_emotes=["dance", "cheer"],
         accept=[("sound", "self", 7294), ("state", "self", "dance"), ("wait", 4000), ("sound", "self", 7294),
                 ("emote", "bluegill", 94), ("wait", 4000), ("state", "self", "none"), ("face", "self", "player"),
                 ("emote", "self", "point")],
         complete=[("state", "self", "dance"), ("sound", "self", 7294), ("move", "ch1:grrmlgrrl", "conga_end", "run"),
                   ("wait", 4000), ("state", "ch1:grrmlgrrl", "dance"), ("sound", "self", 7294), ("wait", 9000),
                   ("move", "ch1:grrmlgrrl", "grrmlgrrl", "walk"), ("wait", 1500), ("state", "self", "none"),
                   ("emote", "self", "cheer")],
         poi=["pond"]),

    # 4.14: Muckfest, the eating contest (timed)
    dict(key="ch4_eat", title="Muckfest: The Eating Contest", giver="muckmaw", ender="muckmaw", level=27, xp=8,
         tone="stupid", prev="ch4_conga", items=[("fish_bones", 8)], time=60,
         goal="Eat 8 fish from the Contest Platter at the eating log, south of the pond, within a minute, and bring Muckmaw "
              "the 8 Fish Bones.",
         text="The eating contest! 8 muck fish, 1 minute, no breathing. The winner gets the crown. "
              "The loser gets... well. Mrrk thinks he will win. Mrrk always thinks.",
         progress="Chew! Chew! Swallow! Chew!",
         reward="8! The crown! Kneel, kneel... there. A fish head, for the fish champion. Wear it always. It will smell always.",
         details=["point", "laugh"], reward_emotes=["cheer", "applaud"], rewards=["muck_crown"],
         accept=[("face", "self", "contest_log"), ("emote", "self", "point"), ("sound", "self", 12827),
                 ("state", "ch1:murlorga", "none"), ("wait", 1500), ("emote", "ch0:mrrk", "eat"), ("sound", "echo_pond", 45),
                 ("move", "ch1:murlorga", "eat_watch", "walk"), ("wait", 4000), ("emote", "ch0:mrrk", "eat"),
                 ("sound", "echo_pond", 45), ("wait", 4000), ("emote", "ch0:mrrk", "eat"), ("sound", "echo_pond", 45),
                 ("wait", 6000), ("emote", "ch1:murlorga", "cry"), ("wait", 8000), ("sound", "echo_pond", 1197),
                 ("sound", "echo_pond", "murloc_wound_crit"), ("emote", "self", "laugh"), ("wait", 9000),
                 ("move", "ch1:murlorga", "murlorga", "walk"), ("wait", 9000), ("state", "ch1:murlorga", "work")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("aura", "player", "fish_crown"),
                   ("emote", "bluegill", "applaud"), ("sound", "self", 6576), ("wait", 1500), ("emote", "ch0:mrrk", "rude"),
                   ("wait", 1500), ("emote", "self", 94)],
         poi=["contest_log"]),

    # 4.15: Muckfest, lights for the spawning (glow-jellies; or the stolen lanterns, 4.15 b)
    dict(key="ch4_lights", title="Muckfest: Lights for the Spawning", giver="muckmaw", ender="ch1:elder", level=27, xp=8,
         tone="serious", prev="ch4_eat", exclusive=42, items=[("glow_jelly", 5), ("lit_water", 1)],
         goal="Gather 5 Glow-Jellies from the cove and the bay, set the lights on the spawning water in the middle of the pond, "
              "then go to the Elder.",
         text="Tonight is spawning night. The mothers go into the water, and the water must shine. "
              "Glow-jellies, from the bay. 5 of them. Set them on the water... and bring your Elder. Bring everyone.",
         progress="The water is dark, little one.",
         reward="...Every spawning night, the Elder blesses the clutch. Every one, for longer than you have been alive. "
                "Tonight there is no clutch. Tonight I bless the water, and the water is empty.",
         details=["talk", "point"], reward_emotes=["bow", "cry"],
         accept=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "spawn_water"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "glow_6"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "pond")],
         complete=[("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"), ("wait", 2500)] + TAPS,
         poi=["glow_1", "glow_6", "spawn_water"]),
    dict(key="ch4_stolen_lights", title="Muckfest: Stolen Lights", giver="ch1:blrrgl", ender="ch1:elder", level=27, xp=8,
         tone="serious", prev=["ch4_eat", "ch4_lanterns"], exclusive=42, items=[("harbour_lantern", 3), ("lit_water_b", 1)],
         goal="Hang the 3 Harbour Lanterns Blrrgl kept from Menethil on the spawning water in the middle of the pond, then go "
              "to the Elder.",
         text="The festival wants lights. I have lights. 3 of them, in the log. They were for... for me. "
              "Take them. Hang them on the water. Don't tell anyone they're mine. Were mine.",
         progress="Shine, shine. Go and make them shine.",
         reward="Dry-skin lights on murloc water. Mm. Stolen. Still... they shine. Tonight the water is empty, little one, "
                "but it shines.",
         details=["beg", "no"], reward_emotes=["bow", "cry"],
         accept=[("move", "self", "blrrgl_log", "walk"), ("wait", 2500), ("emote", "self", "kneel"), ("sound", "self", 1221),
                 ("give", "harbour_lantern", 3), ("wait", 1500), ("move", "self", "blrrgl", "walk"), ("wait", 2500),
                 ("face", "self", "player"), ("emote", "self", "beg"), ("wait", 1200), ("emote", "self", "no"),
                 ("face", "self", "hub_fire")],
         complete=[("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"), ("wait", 2500)] + TAPS,
         poi=["spawn_water_b"]),

    # 4.16: the chief's price
    dict(key="ch4_price", title="The Chief's Price", giver="ch1:elder", ender="blrrmuk", level=27, xp=8, tone="funny",
         prev="ch4_eat", source="tail_fish",
         goal="Take Chief Blrrmuk the Elder's answer: a fish, handed over tail-first.",
         text="He wants Grrmlgrrl's spear. He wants Murlorga's ladle. He wants us in his service, forever, for a bed of sand. "
              "Mm. Take him my answer. Carefully. Tail first.",
         progress="Tail. First.",
         reward="...A fish. A fish? TAIL FIRST? To ME? To the CHIEF?",
         details=["talk", "no"], reward_emotes=["exclamation", "roar"],
         accept=[("state", "blrrmuk", "none"), ("move", "blrrmuk", "blrrmuk_visit", "walk"), ("wait", 9000),
                 ("face", "blrrmuk", "grrmlgrrl"), ("emote", "blrrmuk", "point"), ("wait", 1500), ("face", "blrrmuk", "murlorga"),
                 ("emote", "blrrmuk", "point"), ("wait", 1500), ("face", "blrrmuk", "elder"), ("emote", "blrrmuk", "eat"),
                 ("sound", "blrrmuk", 45), ("wait", 1500), ("face", "self", "blrrmuk_visit"), ("wait", 4500),
                 ("emote", "self", "no"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "beg"), ("sound", "self", 1186), ("move", "blrrmuk", "blrrmuk", "walk"), ("wait", 9000),
                 ("face", "blrrmuk", "pond"), ("state", "blrrmuk", "sit"), ("face", "self", "hub_fire")],
         complete=[("state", "self", "none"), ("emote", "self", "question"), ("wait", 1500), ("emote", "self", "exclamation"),
                   ("sound", "self", "murloc_alert"), ("wait", 1200), ("emote", "guard_a", "laugh"),
                   ("sound", "guard_a", "murloc_fidget2"), ("emote", "guard_b", "laugh"), ("wait", 1500), ("face", "self", "guard_1"),
                   ("emote", "self", "roar"), ("sound", "self", "murloc_aggro"), ("wait", 1200), ("emote", "guard_a", "shy"),
                   ("emote", "guard_b", "shy"), ("wait", 1500), ("face", "self", "pond"), ("emote", "self", "throw"),
                   ("sound", "self", "splash_small"), ("state", "self", "sit")]),

    # 4.17 a: sabotage the raid (hero) / b: the fish market raid (menace)
    dict(key="ch4_drum", title="Sabotage the Raid", giver="muckmaw", ender="muckmaw", level=27, xp=8, tone="serious",
         path="hero", prev="ch4_price", exclusive=41, event="Blrrmuk's war drum sunk in the bay", rep=[(47, 350)],
         goal="Take Blrrmuk's War Drum from beside the chief's hut and sink it in the deep kelp in the bay west of the camp "
              "before dawn.",
         text="Psst. The chief beats his drum tonight. For the dry-skins' fish market. Many of us will go... few of us come back. "
              "No drum, no raid. Take it. Sink it. Then sleep like a fish.",
         progress="Shh. Is it wet yet?",
         reward="Look at them! Look! They woke up for war and there is no drum. Ha! Back to bed, heroes. Back to bed.",
         details=["shy", "point"], reward_emotes=["laugh", "dance"],
         choice=["drumskin_leggings", "tidewatcher_kilt", "quiet_legguards"],
         accept=[("emote", "self", "kneel"), ("object", "sand_drum", "draw_1", 40), ("sound", "self", 1194), ("wait", 1800),
                 ("emote", "self", "kneel"), ("object", "sand_town", "draw_2", 40), ("wait", 1800), ("emote", "self", "kneel"),
                 ("object", "sand_bones", "draw_3", 40), ("wait", 1500), ("emote", "self", "cry"), ("wait", 1200),
                 ("face", "self", "blrrmuk_hut"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "shy")],
         complete=[("summon", "dawn_raider", "dawn_1", 30), ("summon", "dawn_raider", "dawn_2", 30),
                   ("summon", "dawn_raider", "dawn_3", 30), ("wait", 2000), ("emote", "self", "laugh"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 6000), ("emote", "self", 94)],
         poi=["war_drum", "drum_deep"]),
    dict(key="ch4_raid", title="The Fish Market Raid", giver="blrrmuk", ender="blrrmuk", level=27, xp=8, tone="funny",
         path="menace", prev="ch4_price", exclusive=41, items=[("fish_crate", 8)], rep=[(47, -500)],
         goal="Raid Menethil's fish market on the waterfront boardwalk with Blrrmuk's raiders and carry off 8 Crates of "
              "Menethil Fish. The sentries will come.",
         text="The drum! Hear the drum! Tonight the Bluegill eat like chiefs. The dry-skins keep their fish in boxes on "
              "the wooden walk. 8 boxes. Grab, run, swim! Mrgl!",
         progress="Boxes! Where are my boxes?",
         reward="Fish! Dry-skin fish! Salty, smoky, boxed! Oh, this is a good night. This is the best night.",
         details=["roar", "point"], reward_emotes=["eat", "cheer"],
         choice=["raider_leggings", "sailcloth_trousers", "crate_legguards"],
         accept=[("state", "self", "none"), ("sound", "self", 11773), ("emote", "self", "roar"), ("sound", "self", "murloc_aggro"),
                 ("wait", 1500), ("sound", "self", 11773), ("summon", "raider", "dawn_1", 25), ("summon", "raider", "dawn_2", 25),
                 ("emote", "guard_a", "cheer"), ("emote", "guard_b", "cheer"), ("wait", 1200), ("move", "raider", "raid_road", "run"),
                 ("sound", "self", 11773), ("wait", 2000), ("face", "self", "player"), ("emote", "self", "point"),
                 ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 1000),
                   ("emote", "self", "eat"), ("sound", "self", 45), ("wait", 1000), ("emote", "self", "eat"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 1200), ("emote", "self", "cheer"), ("emote", "guard_a", "cheer"),
                   ("emote", "guard_b", "cheer"), ("wait", 1500), ("state", "self", "sit")],
         poi=["market_2", "market_5"]),

    # 4.18: Mirelow
    dict(key="ch4_mirelow", title="Mirelow", giver="nrrgla", ender="nrrgla", level=27, xp=8, tone="serious", path="hero",
         prev="ch4_gnolls", source="raw_meat", kill=[("mirelow", 1)], event="The lost fry found",
         goal="Drop the Bloody Bait in Mirelow's wallow in the Bluegill Marsh to the north-east, kill Mirelow, and find "
              "Nrrgla's fry in the reed nest nearby.",
         text="Squeep! My Squeep! He swam after a frog. Into the marsh. Where the old one lives. The OLD one. Mirelow. "
              "Big as a boat, mouth like a door... Bring him back. Please. Please.",
         progress="Squeep? Is that Squeep? ...No. No.",
         reward="SQUEEP! Oh, you bad, bad, beautiful fry! Never again. Never, never again. ...Thank you. Thank you.",
         details=["cry", "beg"], reward_emotes=["cheer", "kiss"], choice=["mirelow_tooth", "mothers_thanks"],
         accept=[("state", "self", "none"), ("emote", "self", "cry"), ("sound", "self", "baby_murloc"),
                 ("move", "self", "mother_1", "run"), ("wait", 1500), ("move", "self", "mother_2", "run"), ("wait", 1500),
                 ("move", "self", "mother_3", "run"), ("wait", 1500), ("move", "self", "fry_mother", "run"), ("wait", 1500),
                 ("face", "self", "wallow"), ("emote", "self", "point"), ("sound", "self", "murloc_wound"), ("wait", 1500),
                 ("emote", "self", "beg")],
         complete=[("emote", "self", "exclamation"), ("sound", "self", "baby_murloc"), ("move", "squeep", "fry_mother", "run"),
                   ("wait", 2500), ("emote", "self", "cheer"), ("emote", "squeep", 94), ("wait", 1500), ("emote", "self", "kiss"),
                   ("sound", "self", "murloc_fidget"), ("wait", 3000), ("despawn", "squeep")],
         poi=["wallow", "nest"]),

    # 4.19: the oracle who sings
    dict(key="ch4_gloop", title="The Oracle Who Sings", giver="ch1:elder", ender="gloop", level=28, xp=8, tone="serious",
         prev="ch4_price",
         goal="Hear Grandmother Gloop, the Bluegill's oracle, at her hut on the cove's north bank.",
         text="The Bluegill have an oracle. Old. Older than me, and that is old. She sings at the water every evening... "
              "and tonight she sang of us. Go and hear her. I... I will wait here.",
         progress="Listen.",
         reward="A long ship, a long one on it. A net under it. And in the net... little lights. Little lights going north.",
         details=["talk", "point"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "gloop"), ("emote", "self", "point"), ("wait", 1500)] + TAPS + [("wait", 1200),
                 ("emote", "self", "bow"), ("face", "self", "hub_fire")],
         complete=[("state", "self", "none"), ("sound", "self", 8485), ("emote", "self", "talk"), ("wait", 3000),
                   ("sound", "self", "murloc_fidget2"), ("emote", "self", "spell"), ("visual", "self", 35426), ("wait", 2500),
                   ("emote", "self", "kneel"), ("object", "sand_ship", "gloop_draw_1", 45), ("sound", "self", 1194), ("wait", 2000),
                   ("emote", "self", "kneel"), ("object", "sand_net", "gloop_draw_2", 45), ("wait", 2000),
                   ("summon", "pebble_glow", "gloop_draw_2", 40), ("sound", "self", 1221), ("wait", 2000), ("face", "self", "north"),
                   ("emote", "self", "point"), ("sound", "self", "murloc_alert"), ("emote", "ch1:elder", "attack"), ("wait", 3000),
                   ("state", "self", "sit")]),

    # 4.20: egg-jelly on the tide
    dict(key="ch4_jelly", title="Egg-Jelly on the Tide", giver="gloop", ender="ch1:elder", level=28, xp=8, tone="serious",
         prev="ch4_gloop", items=[("egg_jelly", 6)],
         goal="Gather 6 Scraps of Egg-Jelly washed up along Baradin Bay's north shore, from the camp up to the Lost Fleet, "
              "and bring them to the Elder.",
         text="The long one's ship passed close to the shore. Very close. Frightened eggs leak a little... and it washes up. "
              "Follow it north. 6 scraps. The tide forgets, little one. You must not.",
         progress="Is it the clutch? Is it ours?",
         reward="...Ours. They are ours. They went this way. They were here, little one. Right here.",
         details=["talk", "point"], reward_emotes=["cry", "bow"],
         accept=[("state", "self", "none"), ("object", "held_scrap", "egg_held", 30), ("summon", "pebble_glow", "egg_held", 25),
                 ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "north"), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", "cry"), ("wait", 1500), ("state", "self", "sit")],
         complete=[("emote", "self", "kneel"), ("music", 6075), ("wait", 2000), ("emote", "self", "cry"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 3000), ("emote", "self", "bow"), ("wait", 3000),
                   ("emote", "self", "attack"), ("sound", "self", 977)],
         poi=["jelly_shore_2", "jelly_shore_5"]),

    # 4.21: the Menethil cat
    dict(key="ch4_cat", title="The Menethil Cat", giver="ch1:murlorga", ender="ch0:bram", level=28, xp=8, tone="stupid",
         prev="ch4_tackle", explore="bram", radius=8, rep=[(47, 100)],
         goal="Follow the dock cat that stole Murlorga's fish to its three hiding places: the beach south of camp, the point "
              "north of Menethil, and wherever it goes last.",
         text="A thief! A furry thief! It took a fish off my pot. Off MY pot! And ran! "
              "Follow that cat. I want my fish back. I want to see its little face.",
         progress="Did you catch it? Did it scratch you? Did you scratch it back?",
         reward="Ha! Haha! HIC! Me Tibbles! Ye followed me Tibbles all the way here? HIC! Och, lad. Here. Have a fish.",
         details=["exclamation", "point"], reward_emotes=["laugh", "laugh"], rewards=[787],
         accept=[("state", "self", "none"), ("summon", "cat_lap", "cat_start", 10), ("wait", 300),
                 ("move", "cat_lap", "hide_1", "run"), ("sound", "self", 4040), ("emote", "self", "exclamation"), ("wait", 800),
                 ("emote", "self", "throw"), ("sound", "self", 973), ("wait", 1200), ("emote", "self", "rude"),
                 ("sound", "self", "murloc_aggro"), ("wait", 1500), ("face", "self", "hide_1"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "laugh"), ("sound", "self", 2727), ("wait", 1500),
                   ("emote", "self", "laugh"), ("wait", 1200), ("aura", "self", "hiccups"), ("emote", "cat_lap", "eat"),
                   ("sound", "cat_lap", 4121), ("wait", 1500), ("emote", "self", "point"), ("wait", 1500),
                   ("state", "self", "sit")],
         poi=["hide_1", "hide_2", "bram"]),

    # 4.22: Bram's letter (ends with Hester Gale, in chapter 5)
    dict(key="ch4_letter", title="Bram's Letter", giver="ch0:bram", ender="ch0:hester", level=28, xp=8, tone="serious",
         path="hero", prev="ch4_tackle", source="bram_letter", rep=[(47, 250), (72, 250)],
         goal="Carry Bram's Letter north to his cousin Hester Gale, in her cottage at the edge of Southshore.",
         text="Ye're goin' north, aye? The turtle an' all. Me cousin Hester's in Southshore, the wee cottage by the sea. "
              "Take her this. She'll know what tae do wi' a strange wee fish. She always did.",
         progress="Oh! A letter? For me?",
         reward="Bram! That old soak... he says you found Martha's ring. He says you're the gentlest thing that ever came "
                "out of the sea. Oh, come here. Come in out of the wind.",
         details=["talk", "point"], reward_emotes=["cry", "laugh"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("sound", "self", 3093), ("wait", 2000),
                 ("emote", "self", "eat"), ("wait", 1200), ("sound", "self", 3093), ("emote", "self", "talk"), ("wait", 2000),
                 ("sound", "self", 1192), ("face", "self", "north"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "bow"), ("sound", "self", 6111), ("wait", 1500),
                 ("state", "self", "sit")],
         complete=[("emote", "self", "laugh"), ("wait", 1500), ("emote", "self", "cry"), ("wait", 1500), ("emote", "self", "laugh"),
                   ("wait", 1200), ("emote", "self", "bow")]),

    # 4.23: raptor hides
    dict(key="ch4_hides", title="Raptor Hides", giver="ch0:grrsh", ender="ch0:grrsh", level=28, xp=8, tone="boring",
         prev="ch4_iron", items=[("mottled_hide", 8)], drops={"mottled_hide": [(1020, 55), (1021, 55)]},
         goal="Bring Grrsh 8 Mottled Raptor Hides from the Mottled Raptors and Screechers in the hills south-east of the camp.",
         text="Look. My best vest. Shark-hide. Something ate the bottom. Something ALWAYS eats the bottom! "
              "The spotted lizards in the hills have thick skins. 8 hides. I make you something with a bottom.",
         progress="Thick ones. Spotted ones.",
         reward="Spots! Thick! Good! Here, a vest. With a bottom. Mind the bottom.",
         details=["point", "cry"], reward_emotes=["work", "cheer"], choice=["raptor_jerkin", "raptor_hauberk", "raptor_robe"],
         accept=[("state", "self", "none"), ("object", "eaten_vest", "vest_spot", 30), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "east"),
                 ("emote", "self", "point"), ("wait", 1200), ("face", "self", "fire_2"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", 467), ("sound", "self", 6426), ("wait", 1500),
                   ("emote", "self", 467), ("sound", "self", 3780), ("wait", 1500), ("object", "new_vest", "vest_spot", 30),
                   ("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("state", "self", "work")],
         poi=["raptor_1", "raptor_2"]),

    # 4.24: the Bluegill ambush
    dict(key="ch4_ambush", title="The Bluegill Ambush", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=29, xp=8,
         tone="serious", prev=["ch4_jelly", "ch4_whelp"], kill=[("ambusher", 10)],
         goal="Kill 10 of Blrrmuk's Warriors attacking the camp from the reeds to the east as the tribe packs.",
         text="Half the camp is on her shell. The other half is... coming. Listen. The reeds. "
              "Blrrmuk did not like his fish. 10 of them, little one. Nobody stabs the tribe's back while we pack.",
         progress="More in the reeds!",
         reward="They ran. Good. Muckmaw waved, did you see? Some Bluegill are Bluegill. Some are just... fish.",
         details=["roar", "point"], reward_emotes=["flex", "roar"], choice=["war_spear", "gutting_knife", "oracle_staff"],
         accept=[("face", "self", "ambush_2"), ("sound", "self", "murloc_aggro"), ("emote", "self", "roar"), ("wait", 1000),
                 ("state", "ch1:blrrgl", "kneel"), ("emote", "muckmaw", "wave"), ("wait", 1500), ("emote", "self", "point"),
                 ("sound", "self", "murloc_aggro"), ("wait", 6000), ("state", "ch1:blrrgl", "none"), ("face", "self", "hub_fire")],
         complete=[("emote", "self", "flex"), ("sound", "self", "murloc_fidget"), ("wait", 900), ("emote", "self", "flex"),
                   ("wait", 900), ("face", "self", "player"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "roar"),
                   ("sound", "self", "murloc_aggro"), ("emote", "ch1:murlorga", "cheer"), ("emote", "ch1:blrrgl", "cheer"),
                   ("emote", "ch1:glubbub", "cheer"), ("wait", 1500), ("face", "self", "hub_fire")],
         poi=["ambush_2"]),

    # 4.25: Shellback rides north (its reward carries the player to chapter 5's hub)
    dict(key="ch4_end", title="Shellback Rides North", giver="ch1:elder", ender="ch1:elder", level=29, xp=8, tone="serious",
         prev="ch4_ambush", event="Aboard Grandmother Shellback",
         goal="Climb onto Grandmother Shellback from the barnacled rock at the cove's edge, then tell the Elder you are ready.",
         text="Grandmother is healed. The trail runs north. The clutch runs north. So... we run north. "
              "Climb on, little one. Hold tight to the barnacles.",
         progress="Hold tight.",
         reward="Sleep, if you can. It is a long swim. It is always a long swim.",
         details=["talk", "point"], reward_emotes=["bow", "talk"], choice=["rider_cloak", "barnacle_cloak"],
         accept=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "shellback"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "north"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1500), ("face", "self", "hub_fire")],
         complete=TAPS + [("wait", 1200), ("aura", "player", "dozing"), ("music", 4454), ("sound", "self", 1114), ("wait", 4500),
                          ("visual", "player", 51347), ("wait", 800), ("teleport", "player", "ch5:hub", 0.0)],
         poi=["flipper"]),

    # the hub's chores (bible 17.10): repeatable, small, for a slower pace
    dict(key="ch4_pot", title="Fish for the Pot", giver="ch1:murlorga", ender="ch1:murlorga", level=25, xp=3, tone="boring",
         prev="ch4_arrival", repeatable=True, items=[("mudfish", 10)],
         goal="Pull 10 Marsh Mudfish from the mudfish holes in the pond and the marsh pools around the camp.",
         text="The pot is empty. The pot is always empty! Mudfish, from the marsh pools. 10 of them. "
              "Then the pot is full, for a little while.",
         progress="Tonk, tonk. Hear that? That is an empty pot.",
         reward="Mudfish! Into the pot. Muddy, but fish. Fish is fish.",
         details=["talk", "point"], reward_emotes=["cheer", "talk"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("sound", "self", 973), ("wait", 600),
                 ("sound", "self", 973), ("face", "self", "mudfish_2"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", 7035), ("wait", 1500),
                   ("face", "self", "cookpot"), ("state", "self", "work")],
         poi=["mudfish_2", "mudfish_5"]),
    dict(key="ch4_patrol", title="Patrol", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=25, xp=3, tone="boring",
         prev="ch4_arrival", repeatable=True, kill=[(1417, 5), (1039, 5)],
         goal="Kill 5 Young Wetlands Crocolisks and 5 Fen Dwellers around the edges of the camp.",
         text="The marsh has teeth. Walk the edge of the camp. Kill what bites... 10 of them. "
              "5 snouts, 5 walking weeds. Then we sleep.",
         progress="Still teeth in the marsh.",
         reward="Quieter. For tonight.",
         details=["point", "flex"], reward_emotes=["salute"],
         accept=[("face", "self", "moss_2"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "flex"),
                 ("sound", "self", "murloc_fidget"), ("wait", 1200), ("face", "self", "hub_fire")],
         complete=[("emote", "self", "salute"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("face", "self", "hub_fire")],
         poi=["moss_2"]),
]
