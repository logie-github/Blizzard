# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 9 of the murlocs' story: The Last Walk (levels 44 to 48), the bible's section 15.

Feralas's Forgotten Coast, below the Twin Colossals: Colossal Cove is the little lagoon at (-3230, 3200),
closed off from the Veiled Sea by a sand spit, with nobody of the game's within 400 yards. The tribe's camp
is on the spit (the fire at (-3206, 3243)); the cliff path climbs east from it to a headland (-3108, 3147),
where the Elder looks at the sea, and on up to the Woodpaw's gully (the plateau, 110 yards up) and the
Northspring harpies above it. South along the beach: the Hatecrest's landing (-3335, 3230), the Coast Crawl in
the water beside it, and the Gordunni's camp on the coast road (-3425, 3208). Across the water: Sardor Isle
(the Ruins of Solarsal's signal brazier, Tawa's drum) and the Isle of Dread (its north-east rocks, Lord
Shalzaru's lair in its caves). Glubbub's vision is on the sea floor off the cove (-3130, 3420).

Phases: Grrmlgrrl, Mrrk, Sloshy, the hatchlings, Grandmother Shellback and the fire come off the turtle with
the player (from ch8_end); the hub kit (Murlorga, Blrrgl, Oracle Glubbub, the trainers, trades, caller,
mailbox, graveyard), the camp and the enemies' landing parties from ch9_arrival; the Elder is at the fire until
ch9_warm (the night he walks up the cliff), sits dead on the headland in a ring of mourners until ch9_elder,
lies on the raft until ch9_funeral; Oracle Glubbub until ch9_staff, Elder Glubbub from it; Nerelith from
ch9_walk until ch9_thanks; Tawa until ch9_mojache; the angry surf and Tawa's tide marks until ch9_totems.
Plain data: tools/murloc/SCHEMA.md."""

CORE = ("from", "ch8:ch8_end")             # off the turtle with the player
HUB = ("from", "ch9_arrival")
NERELITH = ("between", "ch9_walk", "ch9_thanks")
GLUBBUB = ("between", "ch9_arrival", "ch9_staff")
ELDER_GLUBBUB = ("from", "ch9_staff")
RING = ("between", "ch9_warm", "ch9_elder")
BODY = ("between", "ch9_elder", "ch9_funeral")
VISION = ("during", "ch9_vision")

CHAPTER = dict(key="ch9", title="The Last Walk", levels=(44, 48), map=1, zones=[357], hub="hub")

TOWNS = []

PLACES = {
    # the camp on the spit: the fire in the middle
    "hub": (-3207.0, 3248.0), "fire": (-3206.0, 3243.0), "elder": (-3201.5, 3240.0), "elder_feet": (-3203.0, 3241.0),
    "elder_stone": (-3199.5, 3238.5), "warm_spot": (-3204.0, 3241.5), "egg_warm": (-3205.0, 3242.0),
    "walk_start": (-3199.0, 3239.0), "pot": (-3212.0, 3236.0), "murlorga": (-3214.0, 3233.5),
    "hatch_a": (-3217.0, 3238.5), "hatch_b": (-3215.0, 3240.5), "hatch_c": (-3218.5, 3236.0), "hatch_cover": (-3216.0, 3237.0),
    "pool_spot": (-3210.0, 3239.5), "pool_1": (-3208.7, 3239.5), "pool_2": (-3211.3, 3239.5), "pool_3": (-3210.0, 3238.2),
    "pool_4": (-3210.0, 3240.8), "mrrlglr": (-3219.0, 3245.0), "grrmlgrrl": (-3198.0, 3249.0), "mrrk": (-3195.0, 3252.5),
    "draw_1": (-3201.0, 3252.5), "draw_2": (-3203.0, 3255.0), "draw_3": (-3199.0, 3256.0), "sloshy": (-3209.0, 3250.0),
    "blrrgl": (-3190.0, 3236.0), "blrrgl_log": (-3187.5, 3233.0), "blrrgl_hat": (-3190.0, 3236.0, 9.45),
    "blrrgl_draw": (-3192.5, 3240.0), "blrrgl_draw2": (-3193.5, 3238.0), "racks": (-3185.0, 3240.5),
    "glubbub": (-3196.0, 3266.0), "glubbub_front": (-3196.0, 3270.0), "moon_spot": (-3197.5, 3268.0),
    "staff_spot": (-3194.5, 3267.5), "staff_front": (-3196.0, 3268.3), "glubbub_wake": (-3197.5, 3270.0),
    "nerelith": (-3210.0, 3282.0), "nerelith_boat": (-3211.0, 3290.0), "neri_fire": (-3208.5, 3246.5),
    "neri_draw": (-3209.5, 3277.0), "neri_ring_1": (-3207.5, 3275.5), "neri_ring_2": (-3211.5, 3275.5),
    "neri_ring_3": (-3209.5, 3274.0), "shellback": (-3240.0, 3294.0), "caller": (-3226.0, 3239.0),
    "mailbox": (-3203.0, 3256.0), "graveyard": (-3160.0, 3230.0),
    "hut_1": (-3166.0, 3238.0), "hut_2": (-3197.0, 3227.0), "hut_3": (-3240.0, 3256.0),
    # the trainers and the trades, round the fire
    "t_warrior": (-3184.0, 3247.0), "t_hunter": (-3178.0, 3256.0), "t_mage": (-3203.0, 3262.0), "t_priest": (-3209.0, 3264.0),
    "t_firstaid": (-3215.0, 3262.0), "t_fishing": (-3237.0, 3246.0), "fnrrgl": (-3221.0, 3258.0), "krrgl": (-3227.0, 3261.0),
    "anvil": (-3229.5, 3258.5), "anvil_top": (-3228.5, 3259.8), "anvil_top2": (-3229.8, 3260.6), "forge": (-3230.5, 3263.0),
    "brrkl": (-3233.0, 3253.0), "sprokgl": (-3229.0, 3248.0), "shimmrl": (-3233.0, 3266.0), "pearlmrgl": (-3226.0, 3270.0),
    "scrawlgl": (-3220.0, 3272.0), "mmrglla": (-3200.0, 3275.0), "nets": (-3198.5, 3277.5), "grrsh": (-3172.0, 3236.0),
    "brewglub": (-3178.0, 3232.0), "cauldron": (-3179.5, 3229.5), "mrsha": (-3176.0, 3244.0), "mrrsk": (-3170.0, 3250.0),
    # Tawa at the tide's edge, north of the camp, and the four places the water rises wrong
    "tawa": (-3160.0, 3258.0), "tawa_drum": (-3159.0, 3256.5), "tawa_big_drum": (-3161.5, 3256.0), "tawa_inland": (-3172.0, 3205.0),
    "totem_1": (-3130.0, 3235.0), "totem_2": (-3143.0, 3251.0), "totem_3": (-3174.0, 3267.0), "totem_4": (-3188.0, 3278.0),
    "surf_1": (-3130.0, 3243.0, 0.0), "surf_2": (-3143.0, 3259.0, 0.0), "surf_3": (-3174.0, 3276.0, 0.0),
    "surf_4": (-3188.0, 3287.0, 0.0),
    # the lagoon: the raft, the line of mourners in the shallows, the way out to sea
    "raft": (-3213.5, 3223.5), "body": (-3213.5, 3223.5, 0.4), "raft_things": (-3212.6, 3224.6, 0.4),
    "coral_spot": (-3210.0, 3227.0), "glubbub_raft": (-3209.0, 3229.0), "line_1": (-3211.5, 3220.5), "line_2": (-3214.0, 3219.0),
    "line_3": (-3218.0, 3219.5), "line_4": (-3221.0, 3222.0), "line_5": (-3222.0, 3226.0), "grrm_water": (-3224.0, 3215.0),
    "raft_out_1": (-3238.0, 3226.0, 0.0), "raft_out_2": (-3258.0, 3230.0, 0.0), "raft_far": (-3275.0, 3340.0, 0.0),
    # the drifting Feathermoon boat on the south arm's rocks; out to sea, or into the lagoon
    "drift_boat": (-3266.0, 3214.0), "drift_out_1": (-3262.0, 3250.0, 0.0), "drift_out_2": (-3268.0, 3300.0, 0.0),
    "sentinel_spot": (-3284.0, 3330.0, 0.0), "sentinel_boat": (-3285.5, 3332.0, 0.0), "hide_1": (-3245.0, 3222.0, 0.0),
    "hide_spot": (-3229.0, 3229.0, 0.0), "hidden_boat": (-3229.0, 3229.0), "krrgl_shore": (-3226.5, 3234.0),
    # the reef's oysters, off the sea beach
    "oyster_1": (-3172.0, 3288.0), "oyster_2": (-3184.0, 3295.0), "oyster_3": (-3200.0, 3303.0), "oyster_4": (-3226.0, 3302.0),
    "oyster_5": (-3252.0, 3290.0), "oyster_6": (-3192.0, 3290.0), "reef": (-3205.0, 3302.0),
    # the beach north, under the Twin Colossals; the arches up on the heights
    "colossi_view": (-3075.0, 3230.0), "arches": (-3000.0, 2760.0), "sea_w": (-3206.0, 3330.0),
    # the cliff path and the headland
    "headland": (-3108.0, 3147.0), "sea_view": (-3108.0, 3300.0), "staff_knees": (-3108.0, 3148.2),
    "ring_n": (-3103.5, 3147.0), "ring_nw": (-3105.1, 3150.4), "ring_w": (-3108.8, 3151.4), "ring_sw": (-3110.9, 3143.6),
    "ring_s": (-3107.2, 3142.6), "ring_se": (-3104.6, 3144.1), "part_a": (-3111.0, 3154.0), "part_b": (-3114.0, 3141.0),
    # the Woodpaw's gully up the path, and the harpies above it
    "hills": (-3112.0, 3092.0), "wp_1": (-3104.0, 3095.0), "wp_2": (-3116.0, 3090.0), "wp_3": (-3128.0, 3094.0),
    "wp_4": (-3110.0, 3101.0), "wp_5": (-3098.0, 3100.0), "wp_6": (-3122.0, 3100.0), "wp_7": (-3112.0, 3084.0),
    "wp_8": (-3132.0, 3087.0), "wp_9": (-3134.0, 3080.0), "wp_rack_1": (-3110.0, 3093.0), "wp_rack_2": (-3121.0, 3088.0),
    "cliff_top": (-3125.0, 3015.0), "harpy_1": (-3125.0, 3020.0), "harpy_2": (-3120.0, 2986.0), "harpy_3": (-3130.0, 3002.0),
    "harpy_4": (-3100.0, 3050.0), "harpy_5": (-3140.0, 3040.0), "harpy_6": (-3066.0, 3053.0),
    # the beach south: the Hatecrest's landing, the Coast Crawl, the Gordunni on the coast road
    "south_beach": (-3335.0, 3230.0), "naga_w1": (-3312.0, 3238.0), "naga_w2": (-3326.0, 3224.0), "naga_w3": (-3342.0, 3242.0),
    "naga_w4": (-3352.0, 3220.0), "naga_r1": (-3334.0, 3256.0), "naga_r2": (-3350.0, 3252.0), "naga_s1": (-3318.0, 3212.0),
    "naga_s2": (-3336.0, 3208.0), "naga_s3": (-3356.0, 3232.0), "naga_s4": (-3308.0, 3226.0), "naga_si1": (-3322.0, 3248.0),
    "naga_si2": (-3346.0, 3214.0), "naga_so1": (-3330.0, 3236.0), "naga_so2": (-3358.0, 3244.0), "naga_so3": (-3340.0, 3202.0),
    "naga_tent": (-3340.0, 3226.0), "naga_banner": (-3326.0, 3232.0), "naga_torch": (-3333.0, 3218.0),
    "crawl_1": (-3318.0, 3274.0), "crawl_2": (-3332.0, 3285.0), "crawl_3": (-3346.0, 3272.0), "crawl_4": (-3325.0, 3292.0),
    "crawl_5": (-3340.0, 3296.0), "crawl_6": (-3310.0, 3283.0),
    "ogre_camp": (-3425.0, 3208.0), "ogre_fire": (-3419.0, 3203.0), "pot_out_a": (-3423.0, 3212.0),
    "pot_out_b": (-3427.5, 3212.0), "pot_out_c": (-3425.0, 3214.5), "ogre_1": (-3410.0, 3200.0), "ogre_2": (-3414.0, 3194.0),
    "ogre_3": (-3440.0, 3204.0), "ogre_4": (-3428.0, 3192.0), "ogre_5": (-3446.0, 3214.0), "ogre_6": (-3434.0, 3212.0),
    "ogre_7": (-3404.0, 3204.0), "ogre_8": (-3448.0, 3200.0), "ogre_9": (-3422.0, 3196.0), "ogre_10": (-3444.0, 3207.0),
    # Sardor Isle: the Ruins of Solarsal
    "solarsal": (-4850.0, 3420.0), "isle": (-4400.0, 3275.0), "brazier": (-4862.0, 3186.0), "szallah_spot": (-4874.0, 3161.0),
    "archer_spot": (-4849.0, 3141.0), "archer_boat": (-4856.0, 3132.0, 0.0), "drum_spot": (-4848.0, 3510.0),
    "drum_guard": (-4843.0, 3516.0),
    # the Isle of Dread: the north-east rocks, the sea north of them, Lord Shalzaru's lair in the caves
    "dread": (-5400.0, 3500.0), "dread_rocks": (-5315.0, 3305.0), "ship_start": (-5262.0, 3345.0, 0.0),
    "ship_far": (-5222.0, 3060.0, 0.0), "ship_ilyssa": (-5261.0, 3343.0, 0.5), "ship_ilyssa_far": (-5221.0, 3058.0, 0.5),
    "lair_egg": (-5636.0, 3464.0, 3.2),
    # Glubbub's vision: the sea floor off the cove
    "vision_pearl": (-3130.0, 3420.0), "vision_eye": (-3130.0, 3433.0, -57.0), "vision_ilyssa": (-3126.0, 3416.0),
    "vision_storm": (-3131.0, 3419.0, -52.0), "vegg_1": (-3127.0, 3420.0, -62.5), "vegg_2": (-3133.0, 3420.0, -62.5),
    "vegg_3": (-3130.0, 3417.0, -62.5), "vegg_4": (-3130.0, 3423.0, -62.5),
}

# The staff taps: three blows on the ground (the Elder's, then Glubbub's, then the tribe's answer).
TAPS = [("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977),
        ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977)]
COUGH = 418         # the Elder's wet cough (a murloc's wound sound)

# The tribe answers: each taps three times back.
ANSWER_MURLORGA = [("emote", "ch1:murlorga", "attack"), ("sound", "ch1:murlorga", 977), ("wait", 350),
                   ("sound", "ch1:murlorga", 977), ("wait", 350), ("sound", "ch1:murlorga", 977)]
ANSWER_GRRMLGRRL = [("emote", "ch1:grrmlgrrl", "attack"), ("sound", "ch1:grrmlgrrl", 977), ("wait", 350),
                    ("sound", "ch1:grrmlgrrl", 977), ("wait", 350), ("sound", "ch1:grrmlgrrl", 977)]
ANSWER_BLRRGL = [("emote", "ch1:blrrgl", "attack"), ("sound", "ch1:blrrgl", 977), ("wait", 350),
                 ("sound", "ch1:blrrgl", 977), ("wait", 350), ("sound", "ch1:blrrgl", 977)]
ANSWER_MRRK = [("emote", "ch0:mrrk", "attack"), ("sound", "ch0:mrrk", 977), ("wait", 350),
               ("sound", "ch0:mrrk", 977), ("wait", 350), ("sound", "ch0:mrrk", 977)]
ANSWER_SLOSHY = [("emote", "ch1:sloshy", "attack"), ("sound", "ch1:sloshy", 977), ("wait", 350),
                 ("sound", "ch1:sloshy", 977), ("wait", 350), ("sound", "ch1:sloshy", 977)]


# -- the people -------------------------------------------------------------------------------------

NPCS = [
    # the 8.09 hatchlings, now a camp's worth of trouble
    dict(key="hatchling_a", name="Hatchling", look="murloc_green", scale=0.4, level=5, role="ambient", at="hatch_a",
         facing=0.9, wander=2.0, phase=CORE, idle=[("every", 19000, [("emote", "self", 94), ("sound", "self", "baby_murloc")])]),
    dict(key="hatchling_b", name="Hatchling", look="murloc_pale", scale=0.4, level=5, role="ambient", at="hatch_b",
         facing=2.4, wander=2.0, phase=CORE, idle=[("every", 23000, [("emote", "self", "laugh"), ("sound", "self", "baby_murloc")])]),
    dict(key="hatchling_c", name="Hatchling", look="murloc_gold", scale=0.4, level=5, role="ambient", at="hatch_c",
         facing=4.1, wander=2.0, phase=CORE, idle=[("every", 29000, [("emote", "self", "eat"), ("sound", "self", "baby_murloc")])]),

    # the Elder's walk: he comes with you (summoned beside the fire), coughing all the way up
    dict(key="elder_walker", name="Elder Mrrglmrgl", subname="Tribe Elder", look="murloc_grey", level=20, role="ambient",
         summoned=True, greeting="Slowly, little one. The sea isn't going anywhere.",
         watch=(25, [("follow", "self"), ("sound", "self", "murloc_fidget2")], 600000),
         idle=[("every", 9000, [("sound", "self", COUGH), ("emote", "self", "question")]),
               ("every", 14000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget2")])]),

    # dawn on the headland: the Elder, sitting up, looking at the sea; the tribe in a ring around him
    dict(key="elder_still", name="Elder Mrrglmrgl", subname="Tribe Elder", look="murloc_grey", level=20, role="ambient",
         at="headland", facing=1.571, phase=RING, greeting="...", idle=[("state", "self", "sit")]),
    dict(key="murlorga_ring", name="Murlorga", subname="Cook", look="murloc_orange", level=18, role="ambient", at="ring_nw",
         facing=4.006, phase=RING, idle=[("every", 17000, [("emote", "self", "cry"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="grrmlgrrl_ring", name="Grrmlgrrl the Tidehunter", look="murloc_slate", scale=1.15, level=22, role="ambient",
         at="ring_w", facing=4.892, phase=RING,
         watch=(9, [("move", "self", "part_a", "walk"), ("wait", 2500), ("face", "self", "headland"), ("wait", 30000),
                    ("move", "self", "ring_w", "walk"), ("wait", 2500), ("face", "self", "headland")], 45000)),
    dict(key="sloshy_ring", name="Sloshy", look="murloc_blue", scale=0.6, level=5, role="ambient", at="ring_n", facing=3.142,
         phase=RING, idle=[("every", 13000, [("emote", "self", "cry"), ("sound", "self", "baby_murloc")])]),
    dict(key="mourner", name="Saltscar", plural="the tribe", look="murloc_green", looks=["murloc_bronze", "murloc_gold"],
         level=(15, 20), role="ambient", at=["ring_s", "ring_se"], phase=RING,
         idle=[("state", "self", "kneel"), ("every", 21000, [("sound", "self", "murloc_fidget2")])]),
    dict(key="mourner_part", name="Saltscar", look="murloc_red", level=18, role="ambient", at="ring_sw", facing=0.865,
         phase=RING, watch=(9, [("move", "self", "part_b", "walk"), ("wait", 2500), ("face", "self", "headland"),
                                ("emote", "self", "bow"), ("wait", 30000), ("move", "self", "ring_sw", "walk"), ("wait", 2500),
                                ("face", "self", "headland")], 45000)),

    # on the kelp raft at the lagoon's edge, between the dawn and the funeral
    dict(key="elder_body", name="Elder Mrrglmrgl", subname="Gone to the Sea", look="murloc_grey", level=20, role="ambient",
         at="body", facing=1.571, phase=BODY, unit_flags=0x02000000, idle=[("state", "self", "sleep")]),
    dict(key="funeral_raft", name="Kelp Raft", look=30236, scale=0.6, level=1, role="ambient", summoned=True,
         unit_flags=0x02000002, idle=[("every", 5000, [("visual", "self", 22576)])]),
    dict(key="coral_glow", name="Glowing Coral", look="trigger", level=1, role="ambient", summoned=True, unit_flags=0x02000002,
         idle=[("every", 3000, [("visual", "self", 22576)])]),
    dict(key="egg_glow", name="The Last Egg", look="trigger", level=1, role="ambient", summoned=True, unit_flags=0x02000002,
         idle=[("every", 2500, [("visual", "self", 22579)])]),

    # Glubbub, Elder from 9.24 (the staff planted beside him); he still trains shamans
    dict(key="elder_glubbub", name="Elder Glubbub", subname="Elder of the Saltscar", look="murloc_purple", level=30,
         role="quest+trainer:shaman", at="glubbub", facing=1.571, phase=ELDER_GLUBBUB,
         greeting="The staff is heavy, little one. Heavier than it looks. He made it look light.",
         idle=[("every", 37000, [("visual", "self", 35426), ("sound", "self", "murloc_fidget2")]),
               ("every", 53000, [("emote", "self", "attack"), ("sound", "self", 977)])]),

    # Tawa Riverchant, a water-shaman of Camp Mojache, drumming the angry sea quiet
    dict(key="tawa", name="Tawa Riverchant", subname="Camp Mojache", look=2123, level=45, side="tribe", role="quest",
         language="taurahe", at="tawa", facing=1.571, phase=("until", "ch9_mojache"),
         greeting="Shh. Listen with me, little fish-man. The sea is frightened.",
         idle=[("state", "self", "work"), ("every", 7000, [("sound", "self", 10861)]),
               ("every", 43000, [("emote", "self", "yes")])]),
    dict(key="surf", name="Angry Surf", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at=["surf_1", "surf_2", "surf_3", "surf_4"], phase=("until", "ch9_totems"),
         idle=[("every", 16000, [("visual", "self", 59635), ("sound", "self", "splash_big")])]),
    dict(key="tide_totem", name="Tawa's Water Totem", look=4587, scale=0.7, level=1, role="ambient", summoned=True,
         unit_flags=0x02000002, idle=[("every", 6000, [("visual", "self", 36005)])]),

    # the Ruins of Solarsal: Lady Szallah, called by her brazier, and Nerelith on the water
    dict(key="szallah", name="Lady Szallah", subname="Hatecrest", look=11262, level=46, side="naga", role="enemy",
         language="naga", health=3.0, summoned=True, abilities=[(9532, 8000), (8435, 16000)]),
    dict(key="nerelith_archer", name="Nerelith Saltwind", look=1682, level=45, side="tribe", role="ambient",
         language="darnassian", health=3.0, summoned=True, abilities=[(6660, 2500)]),
    dict(key="archer_boat", name="Rowing Boat", look=30236, scale=0.8, level=1, role="ambient", summoned=True,
         unit_flags=0x02000002),

    # the Isle of Dread: a lookout on the rocks; the naga ship leaving, Ilyssa holding up the clutch
    dict(key="dread_lookout", name="Rocks", look="trigger", level=1, role="ambient", at="dread_rocks", unit_flags=0x02000002,
         watch=(22, [("summon", "galley", "ship_start", 50), ("summon", "ilyssa_galley", "ship_ilyssa", 50), ("wait", 1500),
                     ("visual", "ilyssa_galley", 22576), ("sound", "ilyssa_galley", "siren_hiss"), ("wait", 1500),
                     ("emote", "ilyssa_galley", "roar"), ("music", 9461), ("wait", 4000),
                     ("visual", "ilyssa_galley", 22576), ("sound", "ilyssa_galley", 4024), ("wait", 2500),
                     ("move", "galley", "ship_far", "walk"), ("move", "ilyssa_galley", "ship_ilyssa_far", "walk"),
                     ("sound", "galley", "splash_big")], 90000)),
    dict(key="galley", name="Hatecrest Galley", look=30874, scale=2.2, level=1, role="ambient", summoned=True,
         unit_flags=0x02000002),
    dict(key="ilyssa_galley", name="Sea Witch Ilyssa", look="sea_witch", level=60, side="neutral", role="ambient",
         language="naga", summoned=True, unit_flags=0x02000002),

    # the Gordunni's pot: three wet foragers, and the cove waiting for them
    dict(key="forager_a", name="Saltscar Forager", look="murloc_bronze", level=30, role="ambient", summoned=True,
         watch=(20, [("follow", "self"), ("emote", "self", "cheer"), ("sound", "self", "murloc_alert")], 600000)),
    dict(key="forager_b", name="Saltscar Forager", look="murloc_slate", level=30, role="ambient", summoned=True,
         watch=(20, [("follow", "self"), ("emote", "self", "cry"), ("sound", "self", "murloc_fidget")], 600000)),
    dict(key="forager_c", name="Saltscar Forager", look="murloc_fel", level=30, role="ambient", summoned=True,
         watch=(20, [("follow", "self"), ("emote", "self", "eat"), ("sound", "self", "murloc_fidget2")], 600000)),
    dict(key="pot_home", name="Colossal Cove", look="trigger", level=1, role="ambient", summoned=True, unit_flags=0x02000002,
         watch=(14, [("credit", "ch9_pot")], 5000)),

    # a Feathermoon rowing boat on the rocks: out to sea, or into the lagoon under the kelp
    dict(key="drift_boat", name="Drifting Boat", subname="Feathermoon", look=30236, level=1, role="ambient", at="drift_boat",
         facing=1.2, respawn=90, phase=HUB, greeting="..."),
    dict(key="sentinel_far", name="Feathermoon Sentinel", look=7012, level=45, side="neutral", role="ambient",
         language="darnassian", summoned=True),
    dict(key="sentinel_skiff", name="Rowing Boat", look=30236, scale=0.8, level=1, role="ambient", summoned=True,
         unit_flags=0x02000002),

    # Glubbub's vision (only while 9.28 is in the log): the pearl, the egg-net, the witch's face
    dict(key="vision_ilyssa", name="Sea Witch Ilyssa", look="sea_witch", scale=2.4, level=60, role="ambient",
         at="vision_ilyssa", facing=4.0, unit_flags=0x02000002, phase=VISION,
         idle=[("every", 9000, [("visual", "self", 37816), ("sound", "self", "siren_hiss")])]),
    dict(key="vision_storm", name="Storm", look="trigger", level=1, role="ambient", at="vision_storm", unit_flags=0x02000002,
         phase=VISION, idle=[("every", 4000, [("visual", "self", 10387), ("sound", "self", 30)])]),
]

# -- things ------------------------------------------------------------------------------------------

CORAL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\Coral01.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
SHELL_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
EGG = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_01.mdx"
MOUND = "World\\Azeroth\\Duskwood\\PassiveDoodads\\Tombs\\DirtMound01.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
FISH_RACK = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishRack.mdx"
STONE = "World\\Azeroth\\Burningsteppes\\PassiveDoodads\\Rocks\\LavaRock01.mdx"
LOG = "World\\Azeroth\\SwampOSorrow\\PassiveDoodads\\TreeLogs\\SwampTreeLog01.mdx"
BASKET = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\Fishing\\TS_FishingBasket_Empty_02.mdx"
STAFF = 1708            # a gnarled staff
ROWBOAT = 124
KELP = 6322

OBJECTS = [
    # the camp (from the arrival on): huts, the pot, Blrrgl's log, the racks, the smithy, the stinky cauldron
    dict(key="hut", model="murloc_hut", name="Saltscar Hut", at=["hut_1", "hut_3"], kind="doodad", scale=0.8, facing=2.6,
         phase=HUB),
    dict(key="hut_b", model="murloc_hut2", name="Saltscar Hut", at="hut_2", kind="doodad", scale=0.8, facing=1.9, phase=HUB),
    dict(key="cookpot", model=6849, name="Murlorga's Pot", at="pot", kind="doodad", scale=1.1, phase=HUB),
    dict(key="hollow_log", model=LOG, name="Hollow Log", at="blrrgl_log", kind="doodad", scale=0.6, facing=0.4, phase=HUB),
    dict(key="racks", model=409, name="Empty Fish Racks", at="racks", kind="doodad", scale=0.8, facing=1.2, phase=HUB),
    dict(key="anvil", model=273, name="Salvage Anvil", at="anvil", kind="doodad", scale=0.8, facing=0.8, phase=HUB),
    dict(key="forge", model=233, name="Driftwood Forge", at="forge", kind="doodad", scale=0.7, facing=0.8, phase=HUB),
    dict(key="cauldron", model=216, name="Brewglub's Cauldron", at="cauldron", kind="doodad", scale=0.8, phase=HUB),
    dict(key="nets", model=BASKET, name="Net Basket", at="nets", kind="doodad", scale=0.8, facing=1.0, phase=HUB),
    # the fire, lit as the tribe lands (Murlorga's lesson in 9.16 is held over it)
    dict(key="fire", model=192, name="Campfire", at="fire", kind="use", quest="ch9_warm", consumable=False, phase=CORE,
         goal="Last Egg warmed by the fire",
         beats=[("summon", "egg_glow", "egg_warm", 6), ("emote", "ch1:murlorga", "yes"),
                ("sound", "ch1:murlorga", "murloc_fidget"), ("sound", "hatchling_b", "baby_murloc")]),
    dict(key="elder_stone", model=STONE, name="The Elder's Smooth Stone", at="elder_stone", kind="loot",
         loot=[("smooth_stone", 1, 1)], quest="ch9_things", scale=0.12, phase=CORE),
    # Tawa's own drum; Nerelith's boat at the cove's edge
    dict(key="tawa_drum", model=2572, name="Tawa's Drum", at="tawa_drum", kind="doodad", scale=0.7,
         phase=("until", "ch9_mojache")),
    dict(key="nerelith_boat", model=ROWBOAT, name="Feathermoon Rowing Boat", at="nerelith_boat", kind="doodad", facing=1.4,
         phase=NERELITH),
    # the tide marks (9.10), each its own place
    dict(key="mark_1", model=627, name="Tide Mark", at="totem_1", kind="use", quest="ch9_totems", scale=0.8,
         phase=("until", "ch9_totems"), goal="Totem planted at the North Rocks",
         beats=[("take", "water_totem", 1), ("summon", "tide_totem", "totem_1", 600),
                ("unaura", "surf", 59635), ("sound", "tawa", 11773), ("emote", "tawa", "yes"), ("emote", "ch1:glubbub", "bow"),
                ("sound", "ch1:glubbub", "murloc_fidget2")]),
    dict(key="mark_2", model=627, name="Tide Mark", at="totem_2", kind="use", quest="ch9_totems", scale=0.8,
         phase=("until", "ch9_totems"), goal="Totem planted at the Strand",
         beats=[("take", "water_totem", 1), ("summon", "tide_totem", "totem_2", 600),
                ("unaura", "surf", 59635), ("sound", "tawa", 11773), ("emote", "tawa", "yes"), ("emote", "ch1:glubbub", "bow"),
                ("sound", "ch1:glubbub", "murloc_fidget2")]),
    dict(key="mark_3", model=627, name="Tide Mark", at="totem_3", kind="use", quest="ch9_totems", scale=0.8,
         phase=("until", "ch9_totems"), goal="Totem planted at the Dune",
         beats=[("take", "water_totem", 1), ("summon", "tide_totem", "totem_3", 600),
                ("unaura", "surf", 59635), ("sound", "tawa", 11773), ("emote", "tawa", "yes"), ("emote", "ch1:glubbub", "bow"),
                ("sound", "ch1:glubbub", "murloc_fidget2")]),
    dict(key="mark_4", model=627, name="Tide Mark", at="totem_4", kind="use", quest="ch9_totems", scale=0.8,
         phase=("until", "ch9_totems"), goal="Totem planted at the Spit",
         beats=[("take", "water_totem", 1), ("summon", "tide_totem", "totem_4", 600),
                ("unaura", "surf", 59635), ("sound", "tawa", 11773), ("emote", "tawa", "yes"), ("emote", "ch1:glubbub", "bow"),
                ("sound", "ch1:glubbub", "murloc_fidget2")]),
    # the reef's oysters (9.15)
    dict(key="oyster", model="clam", name="Cove Oyster", kind="loot", loot=[("cove_pearl", 1, 1)], quest="ch9_pool",
         at=["oyster_1", "oyster_2", "oyster_3", "oyster_4", "oyster_5", "oyster_6"]),
    # the headland at dawn: the staff across his knees
    dict(key="staff_knees", model=STAFF, name="The Elder's Staff", at="staff_knees", kind="doodad", scale=0.6, facing=0.0,
         phase=RING),
    # the funeral raft, while he lies on it (its scene: the tribe in the shallows, Nerelith's salute, Tawa's drum)
    dict(key="raft_kelp", model=KELP, name="Kelp", at="raft", kind="doodad", scale=1.3, facing=1.0, phase=BODY),
    dict(key="raft", model=627, name="Kelp Raft", at="raft", kind="use", quest="ch9_funeral", scale=1.4, facing=1.57, phase=BODY,
         beats=[("take", "smooth_stone", 1), ("take", "sweet_roll", 1), ("take", "ch1:plorp_shell", 1),
                ("object", "laid_stone", "raft_things", 17), ("object", "laid_roll", "raft_things", 17),
                ("object", "laid_shell", "raft_things", 17), ("music", 6075),
                ("state", "ch1:murlorga", "none"), ("state", "ch1:glubbub", "none"),
                ("move", "ch1:murlorga", "line_1", "walk"), ("move", "ch1:grrmlgrrl", "grrm_water", "walk"),
                ("move", "ch1:blrrgl", "line_3", "walk"), ("move", "ch0:mrrk", "line_4", "walk"),
                ("move", "ch1:sloshy", "line_2", "walk"), ("move", "ch1:glubbub", "glubbub_raft", "walk"), ("wait", 9000),
                ("sound", "ch1:murlorga", "murloc_fidget2"), ("sound", "ch1:blrrgl", "murloc_fidget2"),
                ("emote", "ch1:sloshy", "cry"), ("wait", 2000), ("emote", "ch1:glubbub", "spell"),
                ("summon", "coral_glow", "coral_spot", 50), ("object", "glow_coral", "coral_spot", 50),
                ("visual", "ch1:glubbub", 35426), ("sound", "ch1:glubbub", "murloc_fidget2"), ("wait", 2500),
                ("aura", "elder_body", "laid_out"), ("summon", "funeral_raft", "body", 55), ("sound", "ch1:grrmlgrrl", "splash"),
                ("move", "funeral_raft", "raft_out_1", "walk"), ("emote", "ch0:nerelith", "salute"),
                ("sound", "tawa", 11773), ("state", "tawa", "none"), ("wait", 3000), ("sound", "ch1:murlorga", "murloc_fidget2"),
                ("emote", "ch0:mrrk", "cry"), ("wait", 2500), ("face", "ch0:mrrk", "hub"), ("emote", "ch0:mrrk", "flex"),
                ("sound", "tawa", 11773), ("wait", 4000), ("move", "funeral_raft", "raft_out_2", "walk"),
                ("sound", "ch1:sloshy", "baby_murloc"), ("emote", "ch1:murlorga", "cry"), ("wait", 4000), ("sound", "tawa", 11773),
                ("credit", "ch9_funeral"), ("wait", 4000), ("move", "funeral_raft", "raft_far", "walk"),
                ("move", "ch1:murlorga", "murlorga", "walk"), ("move", "ch1:blrrgl", "blrrgl", "walk"),
                ("move", "ch0:mrrk", "mrrk", "walk"), ("move", "ch1:sloshy", "sloshy", "walk"), ("move", "ch1:glubbub", "glubbub", "walk"),
                ("state", "tawa", "work"), ("wait", 9000), ("state", "ch1:murlorga", "work"), ("face", "ch1:murlorga", "pot"),
                ("face", "ch1:glubbub", "sea_w"), ("state", "ch1:glubbub", "sit"), ("face", "ch0:mrrk", "fire"),
                ("wait", 12000), ("move", "ch1:grrmlgrrl", "grrmlgrrl", "walk"), ("wait", 6000),
                ("face", "ch1:grrmlgrrl", "fire")]),
    # the staff, planted by Elder Glubbub (lasting from 9.24)
    dict(key="staff_beside", model=STAFF, name="The Elder's Staff", at="staff_spot", kind="doodad", scale=0.7, facing=0.0,
         phase=ELDER_GLUBBUB),
    # the spawning pool for one egg (9.15) and what 9.18 and 9.26 leave behind
    dict(key="pool_shell", model=SHELL, name="Spawning Pool", at=["pool_1", "pool_2", "pool_3", "pool_4"], kind="doodad",
         scale=1.1, phase=("from", "ch9_pool")),
    dict(key="pool_weed", model=KELP, name="Spawning Pool", at="pool_spot", kind="doodad", scale=0.5, phase=("from", "ch9_pool")),
    dict(key="feather_hat", model=6400, name="Blrrgl's Hat", at="blrrgl_hat", kind="doodad", scale=0.8, facing=2.7,
         phase=("from", "ch9_hat")),
    dict(key="carved_moon", model=7417, name="Carved Moon", at="moon_spot", kind="doodad", scale=0.3, phase=("from", "ch9_thanks")),
    dict(key="hidden_boat", model=ROWBOAT, name="Something Under the Kelp", at="hidden_boat", kind="doodad", facing=2.2,
         phase=("from", "ch9_keep")),
    dict(key="hidden_kelp", model=KELP, name="Kelp", at="hidden_boat", kind="doodad", scale=1.6, phase=("from", "ch9_keep")),
    # the beach south: the Hatecrest's landing and the Gordunni's camp
    dict(key="naga_tent", model="naga_pagoda", name="Hatecrest Tent", at="naga_tent", kind="doodad", scale=0.6, facing=1.6,
         phase=HUB),
    dict(key="naga_banner", model="naga_banner", name="Hatecrest Banner", at="naga_banner", kind="doodad", facing=1.6, phase=HUB),
    dict(key="naga_torch", model="naga_torch", name="Hatecrest Torch", at="naga_torch", kind="doodad", phase=HUB),
    dict(key="ogre_fire", model=192, name="Gordunni Fire", at="ogre_fire", kind="doodad", scale=1.3, phase=HUB),
    dict(key="ogre_pot", model=216, name="Gordunni Stew Pot", at="ogre_camp", kind="use", quest="ch9_pot", scale=2.0, phase=HUB,
         beats=[("summon", "forager_a", "pot_out_a", 240), ("summon", "forager_b", "pot_out_b", 240),
                ("summon", "forager_c", "pot_out_c", 240), ("summon", "pot_home", "hub", 240), ("wait", 400),
                ("sound", "forager_a", "splash"), ("sound", "forager_b", "murloc_aggro"), ("emote", "forager_c", "cry"),
                ("wait", 1500), ("emote", "forager_a", "cheer"), ("sound", "forager_c", "murloc_fidget")]),
    dict(key="wp_racks", model=FISH_RACK, name="Stolen Fish Racks", at=["wp_rack_1", "wp_rack_2"], kind="doodad", scale=0.8,
         facing=0.7, phase=HUB),
    # Sardor Isle: Szallah's brazier, and Tawa's grandmother's drum in the ruins
    dict(key="brazier", model=524, name="Hatecrest Signal Brazier", at="brazier", kind="use", quest="ch9_szallah",
         beats=[("summon", "szallah", "szallah_spot", 300), ("summon", "nerelith_archer", "archer_spot", 120),
                ("summon", "archer_boat", "archer_boat", 120), ("wait", 1200), ("emote", "szallah", "roar"),
                ("sound", "szallah", "siren_aggro"), ("wait", 1500), ("face", "nerelith_archer", "szallah_spot"),
                ("emote", "nerelith_archer", "salute"), ("wait", 1500), ("cast", "nerelith_archer", 6660, "szallah"),
                ("wait", 2500), ("cast", "nerelith_archer", 6660, "szallah"), ("wait", 2500),
                ("cast", "nerelith_archer", 6660, "szallah")]),
    dict(key="old_drum", model=3613, name="Grandmother's Drum", at="drum_spot", kind="loot", loot=[("drum", 1, 1)],
         quest="ch9_drum", scale=0.45, facing=2.0),
    # the Isle of Dread: on the kelp in Shalzaru's lair, the one egg the ship left behind
    dict(key="lair_egg", model=EGG, name="The Last Egg", at="lair_egg", kind="loot", loot=[("last_egg", 1, 1)],
         quest="ch9_shalzaru", scale=0.5),
    dict(key="lair_kelp", model=KELP, name="Kelp Bed", at="lair_egg", kind="doodad", scale=1.4),
    # the vision (only while 9.28 is in the log)
    dict(key="vision_pearl", model="great_pearl", name="Great Pearl", at="vision_pearl", kind="doodad", scale=3.5, phase=VISION),
    dict(key="vision_egg", model=EGG, name="The Clutch", at=["vegg_1", "vegg_2", "vegg_3", "vegg_4"], kind="doodad", scale=0.7,
         phase=VISION),

    # set out by scenes
    dict(key="sand_naga", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.6),
    dict(key="sand_lord", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=1.1),
    dict(key="sand_ogre", model=MOUND, name="Drawing in the Sand", kind="doodad", scale=0.7),
    dict(key="sand_tower", model=6390, name="Drawing in the Sand", kind="doodad", scale=0.3),
    dict(key="sand_hat", model=6400, name="Drawing in the Sand", kind="doodad", scale=0.6),
    dict(key="sand_feather", model=2630, name="Drawing in the Sand", kind="doodad", scale=0.8),
    dict(key="claw", model=7759, name="Makrura Claw", kind="doodad", scale=0.5),
    dict(key="trident_prop", model=TRIDENT, name="Naga Trident", kind="doodad", scale=0.5),
    dict(key="medicine", model=256, name="Pouch of Medicine", kind="doodad", scale=0.5),
    dict(key="held_egg", model=EGG, name="The Last Egg", kind="doodad", scale=0.4),
    dict(key="sand_hole", model=MOUND, name="A Hole in the Sand", kind="doodad", scale=0.35),
    dict(key="pearl_charm", model="great_pearl", name="The Elder's Pearl Charm", kind="doodad", scale=0.12),
    dict(key="laid_stone", model=STONE, name="The Elder's Smooth Stone", kind="doodad", scale=0.12),
    dict(key="laid_roll", model=229, name="Murlorga's Sweet Roll", kind="doodad", scale=0.8),
    dict(key="laid_shell", model=SHELL_2, name="Plorp's Name-Shell", kind="doodad", scale=0.9),
    dict(key="glow_coral", model=CORAL, name="Glowing Coral", kind="doodad", scale=0.4),
    dict(key="big_drum", model=3613, name="Grandmother's Drum", kind="doodad", scale=0.45),
    dict(key="full_rack", model=FISH_RACK, name="Fish Racks", kind="doodad", scale=0.8),
    dict(key="kelp_cover", model=KELP, name="Kelp", kind="doodad", scale=1.6),
    dict(key="staff_held", model=STAFF, name="The Elder's Staff", kind="doodad", scale=0.7),
]

# -- items -------------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for
    dict(key="orders", name="Hatecrest Orders", icon="orders", stack=6, description="Sealed with shell-wax. Every one names Feathermoon."),
    dict(key="talisman", name="Hatecrest Talisman", icon=7210, stack=6, description="It glows the way an angry pearl would."),
    dict(key="feather", name="Northspring Feather", icon=19567, stack=6),
    dict(key="drum", name="Grandmother's Drum", icon=43646, description="Old hide, old wood. The tide used to come when it was played."),
    dict(key="water_totem", name="Tawa's Water Totem", icon="item:5177", stack=4),
    dict(key="last_egg", name="The Last Egg", icon=18051, description="Warm, and glowing faintly. The only one they left behind."),
    dict(key="cove_pearl", name="Cove Pearl", icon=12309, stack=5),
    dict(key="smooth_stone", name="The Elder's Smooth Stone", icon=5998, description="Worn smooth by a thousand thumbs. His."),
    dict(key="sweet_roll", name="Murlorga's Last Sweet Roll", icon="bread", description="Kelp-sugar and fish-flour. The last one."),
    dict(key="stew_carrot", name="Stew-Pot Carrot", kind="food", level=45),
    dict(key="tide_toy", name="Tawa's Tide Totem", icon="item:5177", aura="tide_calm",
         description="A little water totem. Hold it up and the sea goes quiet around you."),

    # rewards (levels 46 to 48: the game's quests' greens at these levels)
    dict(key="tide_wraps", name="Tidebreak Wraps", kind="armor:cloth:wrist", quality=2, level=46, stats=[("int", 5), ("spi", 4)]),
    dict(key="tide_bracers", name="Tidebreak Bracers", kind="armor:leather:wrist", quality=2, level=46, stats=[("agi", 5), ("sta", 4)]),
    dict(key="tide_bands", name="Tidebreak Bands", kind="armor:mail:wrist", quality=2, level=46, stats=[("str", 5), ("sta", 4)]),
    dict(key="headland_pendant", name="Headland Pendant", kind="neck", quality=2, level=46, stats=[("int", 5), ("spi", 5)]),
    dict(key="headland_choker", name="Headland Choker", kind="neck", quality=2, level=46, stats=[("str", 5), ("agi", 5)]),
    dict(key="claw_spear", name="Clawhaft Spear", kind="weapon:spear", quality=2, level=47, stats=[("str", 12), ("sta", 10)],
         description="A naga trident with a makrura's grip. Krrgl's best yet."),
    dict(key="claw_shiv", name="Clawgrip Shiv", kind="weapon:dagger", quality=2, level=47, stats=[("agi", 6), ("sta", 5)]),
    dict(key="claw_wand", name="Clawtip Wand", kind="weapon:wand", quality=2, level=47, stats=[("int", 5), ("spi", 3)]),
    dict(key="pot_mitts", name="Stewpot Mitts", kind="armor:cloth:hands", quality=2, level=46, stats=[("int", 7), ("spi", 6)]),
    dict(key="ladle_grips", name="Ladle-Grip Gloves", kind="armor:leather:hands", quality=2, level=46, stats=[("agi", 7), ("sta", 6)]),
    dict(key="pot_gauntlets", name="Potscraper Gauntlets", kind="armor:mail:hands", quality=2, level=46,
         stats=[("str", 7), ("sta", 6)]),
    dict(key="river_slippers", name="Riverchant Slippers", kind="armor:cloth:feet", quality=2, level=47, stats=[("int", 8), ("spi", 7)]),
    dict(key="tide_boots", name="Tidewalker Boots", kind="armor:leather:feet", quality=2, level=47, stats=[("agi", 8), ("sta", 7)]),
    dict(key="surf_sabatons", name="Surfstride Sabatons", kind="armor:mail:feet", quality=2, level=47, stats=[("str", 8), ("sta", 7)]),
    dict(key="moonwatch_bow", name="Moonwatch Longbow", kind="weapon:bow", quality=2, level=48, stats=[("agi", 6), ("sta", 4)]),
    dict(key="szallah_girdle", name="Szallah's Scale Girdle", kind="armor:mail:waist", quality=2, level=48,
         stats=[("str", 8), ("sta", 8)]),
    dict(key="sentinel_sash", name="Sentinel's Sash", kind="armor:cloth:waist", quality=2, level=48, stats=[("int", 8), ("spi", 7)]),
    dict(key="moonlit_belt", name="Moonlit Belt", kind="armor:leather:waist", quality=2, level=48, stats=[("agi", 8), ("sta", 7)]),
    dict(key="harpy_hood", name="Harpyfeather Hood", kind="armor:cloth:head", quality=2, level=47, stats=[("int", 10), ("spi", 9)]),
    dict(key="harpy_cap", name="Harpyfeather Cap", kind="armor:leather:head", quality=2, level=47, stats=[("agi", 10), ("sta", 9)]),
    dict(key="harpy_coif", name="Harpyfeather Coif", kind="armor:mail:head", quality=2, level=47, stats=[("str", 10), ("sta", 9)]),
    dict(key="glowstring_band", name="Glowstring Band", kind="ring", quality=2, level=47, stats=[("int", 6), ("spi", 5)]),
    dict(key="angerglow_ring", name="Angerglow Ring", kind="ring", quality=2, level=47, stats=[("str", 5), ("agi", 5)]),
    dict(key="seafoam_charm", name="Seafoam Charm", kind="neck", quality=2, level=46, stats=[("sta", 5), ("spi", 5)],
         description="Krrgl made it from a nail he kept back. Only one nail."),
    dict(key="elfnail_knuckles", name="Elf-Nail Knuckles", kind="weapon:fist", quality=2, level=46, stats=[("str", 5), ("agi", 5)],
         description="Good nails. Good wood. Ours."),
    dict(key="hatch_robe", name="Hatchwarden's Robe", kind="armor:cloth:chest", quality=2, level=48,
         stats=[("int", 12), ("spi", 11)]),
    dict(key="nest_vest", name="Nestkeeper's Vest", kind="armor:leather:chest", quality=2, level=48,
         stats=[("agi", 12), ("sta", 11)]),
    dict(key="brood_hauberk", name="Broodguard Hauberk", kind="armor:mail:chest", quality=2, level=48,
         stats=[("str", 12), ("sta", 11)]),
    dict(key="road_axe", name="Roadclearer's Axe", kind="weapon:axe", quality=2, level=48, stats=[("str", 6), ("sta", 5)]),
    dict(key="road_staff", name="Roadclearer's Staff", kind="weapon:staff", quality=2, level=48, stats=[("int", 12), ("spi", 11)]),
    dict(key="road_maul", name="Roadclearer's Maul", kind="weapon:mace2h", quality=2, level=48, stats=[("str", 13), ("sta", 11)]),
    dict(key="feathermoon_cloak", name="Feathermoon Cloak", kind="armor:cloth:back", quality=2, level=48,
         stats=[("agi", 6), ("sta", 6)], description="Feathermoon's colours, on a Saltscar."),
    dict(key="shell_leggings", name="Shellback Leggings", kind="armor:cloth:legs", quality=2, level=48,
         stats=[("int", 12), ("spi", 11)]),
    dict(key="shell_breeches", name="Shellback Breeches", kind="armor:leather:legs", quality=2, level=48,
         stats=[("agi", 12), ("sta", 11)]),
    dict(key="shell_legguards", name="Shellback Legguards", kind="armor:mail:legs", quality=2, level=48,
         stats=[("str", 12), ("sta", 11)]),
]

# -- auras -------------------------------------------------------------------------------------------

AURAS = [
    dict(key="elder_pace", name="The Elder's Pace", kind="slow", percent=50, seconds=150, icon=246,
         text="Slowly. Slower than that."),
    dict(key="elder_gone", name="Gone Walking", kind="disguise", look="trigger", seconds=110),
    dict(key="laid_out", name="Gone to the Sea", kind="disguise", look="trigger", seconds=70),
    dict(key="tide_calm", name="Tawa's Tide Totem", kind="mark", seconds=1800, icon=5394,
         text="The sea is quieter around you."),
    dict(key="mourning", name="The Empty Shell Song", kind="mark", seconds=3600, icon=1126,
         text="The Elder has gone to the sea."),
]

# -- who stands where --------------------------------------------------------------------------------

SPAWNS = [
    # off the turtle with the player (8.27's ride): the war leader, the rival, the fry, the turtle herself
    dict(npc="ch1:grrmlgrrl", at="grrmlgrrl", facing=3.785, state="none", phase=CORE),
    dict(npc="ch0:mrrk", at="mrrk", facing=3.854, phase=CORE),
    dict(npc="ch1:sloshy", at="sloshy", facing=1.0, wander=3.0, phase=CORE),
    dict(npc="ch0:shellback", at="shellback", facing=5.335, phase=CORE),
    # the Elder, by the fire, until the night he walks up the cliff (9.16)
    dict(npc="ch1:elder", at="elder", facing=2.554, phase=("between", "ch8:ch8_end", "ch9_warm"), state="sit"),
    # Murlorga's pot and Blrrgl's log: the camp, from the arrival on
    dict(npc="ch1:murlorga", at="murlorga", facing=0.896, phase=HUB),
    dict(npc="ch1:blrrgl", at="blrrgl", facing=2.729, phase=HUB),
    # Oracle Glubbub, by the sea, until he takes the staff (9.24)
    dict(npc="ch1:glubbub", at="glubbub", facing=1.571, phase=GLUBBUB),
    # Nerelith Saltwind, from her rowing boat's coming (9.04's end) until she rows home (9.26)
    dict(npc="ch0:nerelith", at="nerelith", facing=4.814, phase=NERELITH),
    # the hub kit (17.1), from the arrival on
    dict(npc="ch1:brrgmrk", at="t_warrior", facing=3.321, phase=HUB),
    dict(npc="ch1:mrrgasha", at="t_hunter", facing=3.576, phase=HUB),
    dict(npc="ch1:fizzmrgl", at="t_mage", facing=4.556, phase=HUB),
    dict(npc="ch1:glubba", at="t_priest", facing=4.854, phase=HUB),
    dict(npc="ch1:slubb", at="t_firstaid", facing=5.155, phase=HUB),
    dict(npc="ch1:gurgle", at="t_fishing", facing=3.841, phase=HUB),
    dict(npc="ch1:mrrlglr", at="mrrlglr", facing=6.130, phase=HUB),
    dict(npc="ch0:fnrrgl", at="fnrrgl", facing=5.498, phase=HUB),
    dict(npc="ch0:krrgl", at="krrgl", facing=3.927, phase=HUB),
    dict(npc="ch0:brrkl", at="brrkl", facing=5.928, phase=HUB),
    dict(npc="ch0:sprokgl", at="sprokgl", facing=6.069, phase=HUB),
    dict(npc="ch0:shimmrl", at="shimmrl", facing=5.578, phase=HUB),
    dict(npc="ch0:pearlmrgl", at="pearlmrgl", facing=5.350, phase=HUB),
    dict(npc="ch0:scrawlgl", at="scrawlgl", facing=5.162, phase=HUB),
    dict(npc="ch0:mmrglla", at="mmrglla", facing=4.527, phase=HUB),
    dict(npc="ch0:grrsh", at="grrsh", facing=2.939, phase=HUB),
    dict(npc="ch0:brewglub", at="brewglub", facing=4.172, phase=HUB),
    dict(npc="ch0:mrsha", at="mrsha", facing=3.175, phase=HUB),
    dict(npc="ch0:mrrsk", at="mrrsk", facing=3.334, phase=HUB),
    dict(npc="ch0:caller", at="caller", facing=3.975, phase=HUB),
    dict(object="ch0:mailbox", at="mailbox", facing=4.5, phase=HUB),

    # the game's creatures, in the murlocs' phase from the arrival on: the Hatecrest's landing on the beach south
    dict(npc=5331, at=["naga_w1", "naga_w2", "naga_w3", "naga_w4"], wander=4.0, respawn=60, phase=HUB),
    dict(npc=5332, at=["naga_r1", "naga_r2"], wander=5.0, respawn=60, phase=HUB),
    dict(npc=5335, at=["naga_s1", "naga_s2", "naga_s3", "naga_s4"], wander=3.0, respawn=60, phase=HUB),
    dict(npc=5337, at=["naga_si1", "naga_si2"], wander=3.0, respawn=75, phase=HUB),
    dict(npc=5336, at=["naga_so1", "naga_so2", "naga_so3"], wander=3.0, respawn=75, phase=HUB),
    # the Coast Crawl in the water beside it
    dict(npc=5327, at=["crawl_1", "crawl_2", "crawl_3"], wander=6.0, respawn=60, phase=HUB),
    dict(npc=5328, at=["crawl_4", "crawl_5", "crawl_6"], wander=6.0, respawn=60, phase=HUB),
    # the Gordunni on the coast road
    dict(npc=5232, at=["ogre_1", "ogre_3", "ogre_4", "ogre_5", "ogre_7"], wander=4.0, respawn=60, phase=HUB),
    dict(npc=5234, at=["ogre_2", "ogre_6", "ogre_8"], wander=3.0, respawn=60, phase=HUB),
    dict(npc=5240, at=["ogre_9", "ogre_10"], wander=2.0, respawn=75, phase=HUB),
    # the Woodpaw in the gully up the cliff path, with the tribe's fish
    dict(npc=5255, at=["wp_1", "wp_2", "wp_3", "wp_4", "wp_9"], wander=4.0, respawn=60, phase=HUB),
    dict(npc=5254, at=["wp_5", "wp_6", "wp_7", "wp_8"], wander=3.0, respawn=60, phase=HUB),
    # the Northspring above them, on the heights of the Twin Colossals
    dict(npc=5362, at=["harpy_1", "harpy_2"], wander=6.0, respawn=60, phase=HUB),
    dict(npc=5363, at=["harpy_3", "harpy_4"], wander=6.0, respawn=60, phase=HUB),
    dict(npc=5366, at=["harpy_5", "harpy_6"], wander=6.0, respawn=60, phase=HUB),
    # the sorceress who keeps the stolen drum in the Ruins of Solarsal
    dict(npc=5336, at="drum_guard", wander=2.0, respawn=90, phase=HUB),
]

GRAVEYARDS = [
    dict(at="graveyard", name="Colossal Cove", phase=HUB, facing=2.866),
]

# -- the quests --------------------------------------------------------------------------------------

QUESTS = [
    # 9.01: off the shell, under the giants
    dict(key="ch9_arrival", title="Shore of Giants", giver="ch1:elder", ender="ch1:elder", level=44, min=43, xp=8, tone="serious",
         prev="ch8:ch8_end", explore="colossi_view", radius=18,
         goal="Walk north along the beach below the Twin Colossals until you can see the great stone arches on the heights, "
              "then come back to the Elder by the fire.",
         text="Off the shell... off the shell, slowly. Mm. Look up, little one. Up. Higher! Giants of stone, holding up the "
              "sky with their backs. Walk the beach under them. Let your eyes learn to be small again.",
         progress="Small, yes? Good. Small is safe.",
         reward="You saw them. Giants don't look down at murlocs... that is a kind of peace. We camp here. Here, at their feet.",
         details=["talk", "point", "exclamation"], reward_emotes=["bow", "talk"],
         accept=TAPS + [("wait", 900), ("sound", "self", COUGH), ("wait", 1200), ("face", "self", "arches"),
                        ("emote", "self", "point"), ("face", "ch1:grrmlgrrl", "arches"), ("face", "ch0:mrrk", "arches"),
                        ("face", "ch1:sloshy", "arches"), ("face", "hatchling_a", "arches"), ("face", "hatchling_b", "arches"),
                        ("wait", 1200), ("emote", "ch1:grrmlgrrl", "exclamation"), ("emote", "hatchling_b", "question"),
                        ("sound", "ch0:mrrk", "murloc_alert"), ("emote", "ch0:mrrk", "question"), ("wait", 1500),
                        ("state", "ch1:sloshy", "dead"), ("sound", "ch1:sloshy", "baby_murloc"), ("wait", 2500),
                        ("state", "ch1:sloshy", "none"), ("emote", "ch1:sloshy", "laugh"), ("emote", "hatchling_a", "question"),
                        ("wait", 2000), ("face", "self", "fire"), ("emote", "ch0:mrrk", "flex"), ("face", "ch1:grrmlgrrl", "fire"),
                        ("face", "ch0:mrrk", "fire")],
         complete=[("emote", "self", "talk"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("sound", "self", COUGH),
                   ("wait", 1000), ("emote", "ch1:murlorga", "cheer"), ("sound", "ch1:murlorga", 973), ("wait", 600),
                   ("sound", "ch1:murlorga", 973), ("emote", "hatchling_b", 94), ("sound", "hatchling_b", "baby_murloc")],
         poi=["colossi_view"]),

    # 9.02: the long ones on our beach
    dict(key="ch9_patrols", title="Hatecrest Patrols", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=44, xp=8,
         tone="serious", path="hero", prev="ch9_arrival", kill=[(5331, 8), (5332, 4)],
         goal="Kill 8 Hatecrest Warriors and 4 Hatecrest Wave Riders at the naga's landing on the beach south of Colossal Cove, "
              "or on the shores of the Ruins of Solarsal.",
         text="Long ones. Here too. On our beach. ...8 warriors. 4 riders. You. Me. And the loud one. Go.",
         progress="More lines in the sand.",
         reward="Good. ...The loud one stabs well. Don't tell him.",
         details=["talk", "roar"], reward_emotes=["flex", "salute"], choice=["tide_wraps", "tide_bracers", "tide_bands"],
         accept=[("emote", "self", "kneel"), ("object", "sand_naga", "draw_1", 40), ("sound", "self", 1194), ("wait", 1500),
                 ("emote", "self", "kneel"), ("object", "sand_naga", "draw_2", 40), ("sound", "self", 1194), ("wait", 1500),
                 ("move", "ch0:mrrk", "draw_3", "run"), ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 2500),
                 ("emote", "ch0:mrrk", "attack"), ("sound", "ch0:mrrk", 1194), ("wait", 800), ("emote", "self", "attack"),
                 ("wait", 800), ("emote", "ch0:mrrk", "attack"), ("sound", "ch0:mrrk", "murloc_aggro"), ("wait", 1200),
                 ("emote", "self", "roar"), ("sound", "self", "murloc_wound_crit"), ("emote", "ch0:mrrk", "flex"), ("wait", 2500),
                 ("move", "ch0:mrrk", "mrrk", "walk"), ("face", "self", "south_beach"), ("emote", "self", "point"), ("wait", 4000),
                 ("face", "ch0:mrrk", "fire"), ("face", "self", "fire")],
         complete=[("emote", "self", "flex"), ("wait", 900), ("emote", "self", "flex"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 900), ("face", "self", "player"), ("emote", "self", "salute"), ("emote", "ch0:mrrk", "flex"),
                   ("wait", 3000), ("face", "self", "fire")],
         poi=["south_beach"]),

    # 9.03: the screamers' cry over the water
    dict(key="ch9_screamers", title="Silence the Screamers", giver="ch1:murlorga", ender="ch1:murlorga", level=44, xp=8,
         tone="serious", prev="ch9_arrival", kill=[(5335, 8)],
         goal="Kill 8 Hatecrest Screamers at the naga's landing on the beach south of the cove, or in the Ruins of Solarsal.",
         text="Hear that? That shriek, over the water? The little ones go stiff as driftwood every time it comes. 8 of those "
              "screamers. Make them quiet. Then the babies can sleep.",
         progress="Still screaming. Still stiff babies.",
         reward="Quiet... listen to that. Nothing! Oh, nothing is the best sound there is.",
         details=["talk", "point"], reward_emotes=["cheer", "talk"],
         accept=[("sound", "self", "siren_aggro"), ("state", "hatchling_a", "stun"), ("state", "hatchling_b", "stun"),
                 ("state", "hatchling_c", "stun"), ("wait", 800), ("state", "self", "none"), ("emote", "self", "exclamation"),
                 ("move", "self", "hatch_cover", "run"), ("wait", 2000), ("emote", "self", "kneel"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1500), ("emote", "self", "shy"), ("wait", 2500), ("state", "hatchling_a", "none"),
                 ("state", "hatchling_b", "none"), ("state", "hatchling_c", "none"), ("emote", "hatchling_a", "cry"),
                 ("sound", "hatchling_c", "baby_murloc"), ("wait", 1500), ("face", "self", "south_beach"), ("emote", "self", "point"),
                 ("wait", 2000), ("move", "self", "murlorga", "walk"), ("wait", 2500), ("face", "self", "pot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", 973), ("wait", 1000),
                   ("emote", "hatchling_a", 94), ("emote", "hatchling_b", 94), ("emote", "hatchling_c", 94),
                   ("sound", "hatchling_b", "baby_murloc"), ("wait", 3000), ("state", "self", "work")],
         poi=["south_beach", "solarsal"]),

    # 9.04: the slowest escort in the game
    dict(key="ch9_walk", title="The Elder's Walk", giver="ch1:elder", ender="ch1:elder", level=44, xp=8, tone="boring",
         prev="ch9_arrival", emotes=[("elder_walker", "sit", 1, [
             ("state", "self", "sit"), ("face", "self", "sea_view"), ("music", 4454), ("wait", 13000), ("sound", "self", COUGH),
             ("wait", 9000), ("emote", "self", "talk"), ("sound", "self", "murloc_fidget2"), ("wait", 13000),
             ("sound", "self", COUGH), ("wait", 12000), ("state", "self", "none"), ("emote", "self", "attack"), ("wait", 1200),
             ("emote", "self", "attack"), ("wait", 1200), ("emote", "self", "attack"), ("wait", 2500),
             ("emote", "self", "point"), ("credit", "ch9_walk"), ("wait", 3000), ("despawn", "self")])],
         event="Watched the sea with the Elder",
         goal="Walk Elder Mrrglmrgl up the slope east of the camp to the headland above the beach. Slowly. There, /sit "
              "beside him and stay until he is done looking at the sea.",
         text="My legs are older than those arches, little one. But I want to see the sea from high up. Once more. Walk with "
              "me. Slowly... slower than that. Then we sit. Then we look.",
         progress="Mm? Did we go up already? I forget the good parts.",
         reward="The sea from high up... so big. So big, and we crossed it on an old turtle's back. Mm. That was a good walk.",
         details=["talk", "point"], reward_emotes=["bow", "talk"], choice=["headland_pendant", "headland_choker"],
         accept=[("state", "self", "none"), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1000),
                 ("sound", "self", COUGH), ("wait", 1500), ("face", "self", "headland"), ("emote", "self", "point"),
                 ("wait", 1500), ("aura", "player", "elder_pace"), ("summon", "elder_walker", "walk_start", 300),
                 ("aura", "self", "elder_gone"), ("wait", 1000), ("state", "self", "sit")],
         complete=[("emote", "self", "bow"), ("wait", 2000), ("sound", "self", COUGH), ("wait", 1500), ("emote", "self", "bow"),
                   ("sound", "self", "murloc_fidget2")],
         poi=["headland"]),

    # 9.05: a boat from Feathermoon
    dict(key="ch9_nerelith", title="Nerelith Rows Out", giver="ch1:elder", ender="ch0:nerelith", level=45, xp=8,
         tone="serious", path="hero", prev="ch9_walk", rep=[(69, 500)],
         goal="Meet Nerelith Saltwind, whose rowing boat has come in from Feathermoon to the sea beach west of the camp.",
         text="A boat, little one. A land-walker's boat, from the island of tall trees... Mm. I know that one. The tall elf "
              "from the dark coast. Go to her. I would go, but... my legs went up a hill yesterday.",
         progress="You came. Of course you came.",
         reward="Little one. Again. The sea is very wide, and still it keeps bringing you back to me. Your elder's cough... "
                "I heard it from the water. I brought something for it.",
         details=["point", "talk"], reward_emotes=["kneel", "bow"],
         accept=[("face", "self", "nerelith_boat"), ("emote", "self", "point"), ("sound", "self", 977), ("wait", 1500),
                 ("sound", "self", COUGH), ("wait", 1500), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "fire")],
         complete=[("emote", "self", "kneel"), ("wait", 2500), ("face", "self", "elder"), ("emote", "self", "point"),
                   ("object", "medicine", "elder_feet", 180), ("sound", "self", 1200), ("wait", 2000), ("face", "self", "player"),
                   ("emote", "self", "bow"), ("wait", 2500), ("face", "self", "fire")],
         poi=["nerelith"]),

    # 9.06: what the Hatecrest are planning
    dict(key="ch9_orders", title="The Hatecrest Orders", giver="ch0:nerelith", ender="ch0:nerelith", level=45, xp=8,
         tone="serious", path="hero", prev="ch9_nerelith", rep=[(69, 500)], items=[("orders", 6)],
         drops={"orders": [(5337, 45), (5336, 35)]},
         goal="Take 6 sets of Hatecrest Orders from Hatecrest Sirens and Sorceresses: at the naga's landing on the beach south "
              "of the cove, on Sardor Isle's south shore, or on the Isle of Dread.",
         text="The Hatecrest are not raiding. They are gathering. Their sirens and sorceresses carry orders sealed in "
              "shell-wax. Bring me 6 of them, little one. I want to know what they want with my island.",
         progress="Any more of their letters?",
         reward="Feathermoon. Every one of them names Feathermoon. They mean to ring the island and starve it. Not while I "
                "still have a bow.",
         details=["talk", "point"], reward_emotes=["exclamation", "salute"],
         accept=[("emote", "self", "kneel"), ("object", "sand_tower", "neri_draw", 40), ("sound", "self", 1194), ("wait", 2000),
                 ("emote", "self", "kneel"), ("object", "sand_naga", "neri_ring_1", 40), ("object", "sand_naga", "neri_ring_2", 40),
                 ("object", "sand_naga", "neri_ring_3", 40), ("sound", "self", 1194), ("wait", 2000), ("emote", "self", "no"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "point"), ("wait", 2500), ("face", "self", "fire")],
         complete=[("emote", "self", "talk"), ("sound", "self", 1192), ("wait", 2000), ("emote", "self", "exclamation"),
                   ("face", "self", "isle"), ("wait", 2000), ("face", "self", "player"), ("emote", "self", "salute"),
                   ("wait", 3000), ("face", "self", "fire")],
         poi=["south_beach", "solarsal", "dread"]),

    # 9.07: the naga's servants
    dict(key="ch9_crawl", title="Coast Crawl", giver="ch0:krrgl", ender="ch0:krrgl", level=45, xp=8, tone="serious",
         prev="ch9_arrival", kill=[(5327, 6), (5328, 6)],
         goal="Kill 6 Coast Crawl Snapclaws and 6 Coast Crawl Deepseers in the water off the beach south of the cove, or around "
              "Sardor Isle.",
         text="Makrura. Big claws, bad tempers, and they fetch and carry for the long ones. 12 of them. Kill them. Their "
              "claws I can use. Claws are just spears that grew.",
         progress="Clack clack? Still clacking out there.",
         reward="Ha! Claw and steel, together. A naga's trident with a makrura's grip. Good work makes good weapons.",
         details=["talk", "point"], reward_emotes=["cheer", "talk"], choice=["claw_spear", "claw_shiv", "claw_wand"],
         accept=[("object", "claw", "anvil_top", 40), ("emote", "self", "point"), ("sound", "self", 1194), ("wait", 1500),
                 ("object", "trident_prop", "anvil_top2", 40), ("sound", "self", 1207), ("wait", 1500), ("emote", "self", "work"),
                 ("sound", "self", 4614), ("wait", 1800), ("emote", "self", "work"), ("sound", "self", 1212), ("wait", 1800),
                 ("emote", "self", "yes"), ("face", "self", "south_beach"), ("emote", "self", "point"), ("wait", 3000),
                 ("face", "self", "anvil")],
         complete=[("emote", "self", "work"), ("sound", "self", 4614), ("wait", 1500), ("emote", "self", "work"),
                   ("sound", "self", 4614), ("wait", 1500), ("emote", "self", "cheer"), ("sound", "self", "murloc_fidget")],
         poi=["south_beach"]),

    # 9.08: three foragers in a pot (Mrrk knows that pot)
    dict(key="ch9_pot", title="The Ogres' Pot", giver="ch0:mrrk", ender="ch0:mrrk", level=45, xp=8, tone="funny", path="hero",
         prev="ch9_patrols", event="The foragers brought home",
         goal="Tip over the Gordunni stew pot in the ogres' camp on the coast road south of the cove, then lead the three "
              "foragers back to Colossal Cove within 4 minutes.",
         text="Three foragers. In a pot. With carrots. ...I know that pot. I know those carrots. Go and tip it over. Don't let "
              "the big ones salt you.",
         progress="Are they cooked? Tell me they're not cooked.",
         reward="Wet. Furious. Alive. ...That is exactly how I looked. Don't laugh. Here. They saved you a carrot.",
         details=["point", "no"], reward_emotes=["flex", "laugh"], rewards=["stew_carrot"],
         choice=["pot_mitts", "ladle_grips", "pot_gauntlets"],
         accept=[("face", "self", "ogre_camp"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "no"), ("state", "self", "cower"),
                 ("sound", "self", "murloc_wound"), ("wait", 1800), ("state", "self", "none"), ("emote", "self", "flex"),
                 ("wait", 2000), ("face", "self", "fire")],
         complete=[("emote", "self", "flex"), ("sound", "self", "murloc_fidget"), ("emote", "forager_a", "cheer"),
                   ("emote", "forager_b", "bow"), ("emote", "forager_c", "eat"), ("wait", 2000), ("emote", "self", "rude"),
                   ("wait", 2500), ("emote", "forager_a", "wave"), ("despawn", "forager_a"), ("despawn", "forager_b"),
                   ("despawn", "forager_c")],
         poi=["ogre_camp"]),

    # 9.09: a drum on the shore
    dict(key="ch9_tawa", title="The Water-Shaman", giver="ch1:glubbub", ender="tawa", level=45, xp=8, tone="serious",
         path="hero", prev="ch9_arrival", rep=[(81, 500)],
         goal="Find the tauren who drums at the tide's edge on the sea beach just north of the camp.",
         text="Listen. Under the waves... a drum. Boom. Boom. Someone is talking to the water, and the water is listening. "
              "Go. Find the drummer. Bring me what the drum says.",
         progress="Shh. The sea is speaking.",
         reward="Little fish-man. You hear it too, the fear in the water. The naga's sorcery has wounded the tide, and it "
                "climbs where it should not. I drum to soothe it. I am Tawa, of Camp Mojache.",
         details=["exclamation", "point"], reward_emotes=["yes", "bow"],
         accept=[("state", "self", "none"), ("sound", "self", "murloc_alert"), ("wait", 1000), ("face", "self", "tawa"),
                 ("emote", "self", "exclamation"), ("visual", "self", 35426), ("wait", 2000), ("emote", "self", "point"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 3000), ("face", "self", "sea_w"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "yes"), ("wait", 2000),
                   ("face", "self", "sea_w"), ("emote", "self", "yes"), ("sound", "self", 10861), ("state", "self", "work")],
         poi=["tawa"]),

    # 9.10: totems on the tide
    dict(key="ch9_totems", title="Totems on the Tide", giver="tawa", ender="tawa", level=45, xp=8, tone="serious", path="hero",
         prev="ch9_tawa", rep=[(81, 500)], objects=[("mark_1", 1), ("mark_2", 1), ("mark_3", 1), ("mark_4", 1)],
         goal="Plant Tawa's 4 Water Totems at the 4 driftwood Tide Marks along the waterline of the sea beach, north and south "
              "of her drum, while she drums.",
         text="Four totems. One for each place where the water climbs wrong. Plant them at the driftwood marks, in the wet "
              "sand. I will keep the drum going. Do not let it stop, little one... the drum, or the totems.",
         progress="The waves still climb. More totems.",
         reward="There. Hear it? Nothing. Only the sea breathing. She was frightened, little one. Not angry. Frightened.",
         details=["talk", "point"], reward_emotes=["bow", "yes"],
         accept=[("give", "water_totem", 4), ("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1500),
                 ("face", "self", "totem_1"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "totem_4"),
                 ("emote", "self", "point"), ("wait", 1500), ("face", "self", "sea_w"), ("state", "self", "work"),
                 ("sound", "self", 10861)],
         complete=[("state", "self", "none"), ("wait", 2000), ("face", "self", "sea_w"), ("emote", "self", "bow"),
                   ("sound", "self", "splash_small"), ("wait", 3000), ("face", "self", "glubbub"), ("emote", "self", "bow"),
                   ("wait", 2500), ("face", "self", "sea_w"), ("state", "self", "work")],
         poi=["totem_1", "totem_2", "totem_3", "totem_4"]),

    # 9.11: grandmother's drum
    dict(key="ch9_drum", title="Tawa's Drum", giver="tawa", ender="tawa", level=46, xp=8, tone="serious", path="hero",
         prev="ch9_totems", rep=[(81, 500)], items=[("drum", 1)],
         goal="Recover Tawa's grandmother's drum from the Hatecrest in the Ruins of Solarsal, at the south end of Sardor Isle "
              "across the water.",
         text="This drum is mine, and it is small. My grandmother's was this big... and when she played it, the tide came "
              "when it was called. The Hatecrest sorceresses took it from our shore. It is in their ruins on the island. "
              "Bring it home.",
         progress="Did you find it? It is heavy, and it is old.",
         reward="Oh... grandmother. Listen. Listen to it!",
         details=["talk", "flex", "point"], reward_emotes=["cheer", "bow"],
         choice=["river_slippers", "tide_boots", "surf_sabatons"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("sound", "self", 10861), ("wait", 1500),
                 ("emote", "self", "flex"), ("wait", 1800), ("face", "self", "solarsal"), ("emote", "self", "point"),
                 ("wait", 1800), ("emote", "self", "bow"), ("wait", 2500), ("face", "self", "sea_w"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("object", "big_drum", "tawa_big_drum", 60), ("wait", 800),
                   ("state", "self", "work"), ("sound", "self", 11773), ("wait", 2500), ("sound", "self", 11773),
                   ("wait", 2500), ("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", 6055),
                   ("wait", 2000), ("state", "self", "work")],
         poi=["drum_spot"]),

    # 9.12: Lady Szallah
    dict(key="ch9_szallah", title="Lady Szallah", giver="ch0:nerelith", ender="ch0:nerelith", level=46, xp=8, tone="serious",
         path="hero", prev="ch9_orders", rep=[(69, 500)], kill=[("szallah", 1)],
         goal="Light the Hatecrest Signal Brazier on the east beach of the Ruins of Solarsal, on Sardor Isle, to draw out Lady "
              "Szallah, and kill her.",
         text="The orders come from Lady Szallah. She keeps to the deep water and calls her sisters with a brazier on the "
              "ruins' shore. Light it, and she will rise to see who called. I will be on the water when she does.",
         progress="She still breathes?",
         reward="Szallah is gone. The ring around Feathermoon has no knot to tie it now. You did a sentinel's work today, "
                "little one, with a sentinel at your back.",
         details=["talk", "point"], reward_emotes=["salute", "bow"],
         choice=["moonwatch_bow", "szallah_girdle", "sentinel_sash", "moonlit_belt"],
         accept=[("face", "self", "solarsal"), ("emote", "self", "point"), ("wait", 1800), ("emote", "self", "attack"),
                 ("wait", 1200), ("face", "self", "player"), ("emote", "self", "salute"), ("wait", 2500), ("face", "self", "fire")],
         complete=[("emote", "self", "salute"), ("wait", 1500), ("emote", "self", "kneel"), ("wait", 2000),
                   ("emote", "self", "bow"), ("sound", "self", 6005)],
         poi=["brazier"]),

    # 9.13: the island of bad dreams
    dict(key="ch9_dread", title="The Isle of Dread", giver="ch1:elder", ender="ch1:elder", level=46, xp=8, tone="serious",
         prev="ch9_nerelith", explore="dread_rocks", radius=18,
         goal="Swim south to the Isle of Dread and watch Lord Shalzaru's waters from the rocks on the island's north-east shore.",
         text="The long ones' ships come and go from the island in the south. The island of bad dreams. Shalzaru's lair is "
              "there... the clutch passed this way. I feel it in my fins. Go and watch, little one. Only watch.",
         progress="What did you see? Mm? Tell me with your face.",
         reward="...She showed them to you. She wanted you to see. That is the witch's way: she likes us to watch.",
         details=["talk", "point"], reward_emotes=["bow", "cry"],
         accept=[("face", "self", "dread"), ("emote", "self", "point"), ("sound", "self", 977), ("wait", 1500),
                 ("sound", "self", COUGH), ("wait", 1500), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "fire")],
         complete=[("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"), ("wait", 3000), ("emote", "self", "bow"),
                   ("wait", 2000), ("sound", "self", COUGH), ("emote", "ch1:murlorga", "cry")],
         poi=["dread_rocks"]),

    # 9.14: Lord Shalzaru, and the one egg left behind
    dict(key="ch9_shalzaru", title="Lord Shalzaru", giver="ch1:grrmlgrrl", ender="ch1:elder", level=46, xp=8, tone="serious",
         path="hero", prev="ch9_dread", kill=[(8136, 1)], items=[("last_egg", 1)], rewards=["last_egg"],
         goal="Kill Lord Shalzaru in his lair inside the Isle of Dread's caves, and take what lies on the kelp beside him. "
              "Bring it to the Elder.",
         text="Shalzaru. The ship's master. He let her sail. He let them all go... Kill him. Bring back what he keeps.",
         progress="What do you carry, little one?",
         reward="...One. Only one. They took the rest and left one behind, like a fish too small to keep. Hold it. It is warm. "
                "Feel it? It is ours.",
         details=["talk", "roar"], reward_emotes=["kneel", "cry"],
         accept=[("emote", "self", "kneel"), ("object", "sand_lord", "draw_1", 40), ("sound", "self", 1194), ("wait", 2000),
                 ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 800), ("emote", "self", "attack"),
                 ("sound", "self", 1194), ("wait", 800), ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 1000),
                 ("emote", "self", "roar"), ("sound", "self", "murloc_wound_crit"), ("wait", 2000), ("face", "self", "dread"),
                 ("emote", "self", "point"), ("wait", 3000), ("face", "self", "fire")],
         complete=[("state", "self", "none"), ("object", "held_egg", "elder_feet", 40), ("summon", "egg_glow", "elder_feet", 30),
                   ("music", 4454), ("wait", 1500), ("emote", "self", "kneel"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 3000), ("emote", "self", "cry"), ("emote", "ch1:murlorga", "cry"), ("wait", 3000),
                   ("emote", "self", "bow"), ("wait", 2000), ("state", "self", "sit")],
         poi=["lair_egg"]),

    # 9.15: a pool for one egg
    dict(key="ch9_pool", title="Pearls for a Pool", giver="ch1:elder", ender="ch1:elder", level=46, xp=8, tone="serious",
         prev="ch9_shalzaru", items=[("cove_pearl", 5)],
         goal="Dive for 5 Cove Pearls in the oysters on the reef just off the camp's sea beach.",
         text="One egg needs a pool. A small one, here by the fire, where it is warm. Pearls line a pool, little one... the "
              "old way. 5 pearls from the reef. I will dig.",
         progress="Dig, dig... my staff is better at walking.",
         reward="Pearls in the sand, water in the pearls. The old way. ...My mother made one like this, for me.",
         details=["talk", "point"], reward_emotes=["bow", "talk"],
         accept=[("state", "self", "none"), ("move", "self", "pool_spot", "walk"), ("wait", 3500), ("emote", "self", "kneel"),
                 ("object", "sand_hole", "pool_spot", 90), ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "work"),
                 ("sound", "self", 1194), ("wait", 1500), ("sound", "self", COUGH), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "pearl_charm", "pool_spot", 90), ("sound", "self", 1221), ("wait", 2000), ("face", "self", "reef"),
                 ("emote", "self", "point"), ("wait", 2000), ("move", "self", "elder", "walk"), ("wait", 3500),
                 ("face", "self", "fire"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("move", "self", "pool_spot", "walk"), ("wait", 3500), ("emote", "self", "kneel"),
                   ("sound", "self", 1221), ("music", 4454), ("wait", 2000), ("emote", "self", "kneel"), ("sound", "self", 1215),
                   ("wait", 2500), ("emote", "self", "bow"), ("wait", 1500), ("move", "self", "elder", "walk"), ("wait", 3500),
                   ("face", "self", "fire"), ("state", "self", "sit")],
         poi=["reef"]),

    # 9.16: warm the egg (the Elder dozes by the fire the whole time)
    dict(key="ch9_warm", title="Warm the Egg", giver="ch1:murlorga", ender="ch1:murlorga", level=47, xp=8, tone="boring",
         prev="ch9_pool", objects=[("fire", 3)],
         goal="Hold the Last Egg close to the campfire in the middle of the camp, 3 times, the way Murlorga showed you.",
         text="Like this. Look. Hold it near... not too near. Turn it. Slowly, slowly, like you're turning a fish. 3 times, "
              "by the fire. Shh... the Elder is sleeping.",
         progress="Warmer? Feel it. It should be warmer.",
         reward="It's glowing! Look, look... a little brighter. He would have liked to see that. Let him sleep. Let him sleep.",
         details=["talk", "shy"], reward_emotes=["cheer", "kiss"], choice=["hatch_robe", "nest_vest", "brood_hauberk"],
         accept=[("state", "self", "none"), ("move", "self", "warm_spot", "walk"), ("state", "ch1:elder", "sleep"),
                 ("visual", "ch1:elder", 6431), ("wait", 4500), ("emote", "self", "kneel"), ("wait", 1500), ("emote", "self", "work"),
                 ("sound", "self", 7035), ("wait", 2000), ("emote", "self", "work"), ("wait", 2000), ("face", "self", "player"),
                 ("emote", "self", "shy"), ("sound", "self", "murloc_fidget2"), ("wait", 2000), ("move", "self", "murlorga", "walk"),
                 ("wait", 5000), ("face", "self", "pot"), ("state", "self", "work"), ("wait", 20000),
                 ("state", "ch1:elder", "sit")],
         complete=[("state", "self", "none"), ("summon", "egg_glow", "warm_spot", 20), ("emote", "self", "cheer"),
                   ("sound", "self", 973), ("wait", 1500), ("face", "self", "elder"), ("emote", "self", "shy"), ("music", 4454),
                   ("wait", 2500), ("emote", "self", "kiss"), ("wait", 2000), ("face", "self", "pot"), ("state", "self", "work")],
         poi=["fire"]),

    # 9.17: robbed! (Blrrgl, the thief)
    dict(key="ch9_woodpaw", title="Woodpaw Thieves", giver="ch1:blrrgl", ender="ch1:blrrgl", level=45, xp=8, tone="funny",
         prev="ch9_arrival", kill=[(5255, 5), (5254, 5)],
         goal="Kill 5 Woodpaw Reavers and 5 Woodpaw Mystics in the gnolls' gully up the cliff path east of the camp, where "
              "the tribe's dried fish went.",
         text="Robbed! ROBBED! Me! The racks are empty! Every fish! Gnolls, up there... dogs with hands. They took what we took "
              "fair and square! 10 of them. Make them sorry.",
         progress="Thieves! Thieving thieves who thieve!",
         reward="The fish! Back where they belong. With us. With me. With us.",
         details=["exclamation", "point"], reward_emotes=["cheer", "laugh"],
         accept=[("face", "self", "racks"), ("emote", "self", "point"), ("sound", "self", "murloc_alert"), ("wait", 1500),
                 ("face", "self", "hills"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "attack"),
                 ("sound", "self", 1211), ("wait", 600), ("emote", "self", "attack"), ("sound", "self", 1211), ("wait", 900),
                 ("emote", "self", "rude"), ("sound", "self", "murloc_aggro"), ("wait", 2500), ("face", "self", "fire")],
         complete=[("object", "full_rack", "racks", 60), ("sound", "self", 1189), ("emote", "self", "cheer"), ("wait", 1500),
                   ("emote", "self", "eat"), ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget")],
         poi=["hills"]),

    # 9.18: feathers for a hat
    dict(key="ch9_hat", title="Feathers for a Hat", giver="ch1:blrrgl", ender="ch1:blrrgl", level=46, xp=8, tone="stupid",
         prev="ch9_woodpaw", items=[("feather", 6)], drops={"feather": [(5362, 50), (5363, 50), (5366, 50)]},
         goal="Bring Blrrgl 6 Northspring Feathers from the harpies on the heights of the Twin Colossals, above the Woodpaw's "
              "gully.",
         text="Land-walkers wear hats. Big hats. Shiny hats. FEATHER hats! Blrrgl wants a hat. 6 feathers, from the "
              "bird-women on the cliffs. The pretty ones. The screaming ones.",
         progress="Featherless. Hatless. Sad.",
         reward="A HAT! Look at me! ...It won't stay. Why won't it stay? Fine. I'll hold it. Forever. Like a king holds things.",
         details=["beg", "point"], reward_emotes=["cheer", "flex"],
         choice=["harpy_hood", "harpy_cap", "harpy_coif"],
         accept=[("emote", "self", "kneel"), ("object", "sand_hat", "blrrgl_draw", 40), ("sound", "self", 1194), ("wait", 1500),
                 ("emote", "self", "kneel"), ("object", "sand_feather", "blrrgl_draw2", 40), ("wait", 1500),
                 ("emote", "self", "laugh"), ("wait", 1200), ("face", "self", "cliff_top"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "beg"), ("wait", 2000), ("face", "self", "fire")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"), ("wait", 1500), ("emote", "self", "question"),
                   ("wait", 1500), ("emote", "self", "flex"), ("emote", "ch0:mrrk", "laugh"), ("emote", "hatchling_c", "applaud")],
         poi=["cliff_top"]),

    # 9.19: angry glow
    dict(key="ch9_talismans", title="Sorceress Talismans", giver="ch0:shimmrl", ender="ch0:shimmrl", level=46, xp=8,
         tone="boring", prev="ch9_screamers", items=[("talisman", 6)], drops={"talisman": [(5336, 50)]},
         goal="Take 6 Hatecrest Talismans from Hatecrest Sorceresses at the naga's landing south of the cove, or on the Isle of "
              "Dread.",
         text="The sorceresses wear little lights on strings. Talismans. Their glow is... oh, it's good glow. Pearl-glow, but "
              "angrier. 6 of them. I'll teach the anger to be useful.",
         progress="No glow yet?",
         reward="Look. Look at it in the light. See how it shines on my face? Now imagine that on a spear.",
         details=["talk", "point"], reward_emotes=["cheer", "talk"], choice=["glowstring_band", "angerglow_ring"],
         accept=[("visual", "self", 22580), ("sound", "self", 1221), ("wait", 1500), ("emote", "self", "talk"), ("wait", 1500),
                 ("face", "self", "south_beach"), ("emote", "self", "point"), ("wait", 2500), ("face", "self", "fire"),
                 ("state", "self", "work")],
         complete=[("state", "self", "none"), ("visual", "self", 22580), ("visual", "self", 50200), ("sound", "self", 1221),
                   ("wait", 2500), ("emote", "self", "cheer"), ("wait", 2000), ("state", "self", "work")],
         poi=["south_beach", "dread"]),

    # 9.20a and b: the drifting boat (a choice)
    dict(key="ch9_boat", title="The Drifting Boat", giver="ch0:krrgl", ender="ch0:krrgl", level=46, xp=8, tone="serious",
         path="hero", prev="ch9_crawl", exclusive=91, rep=[(69, 250)],
         interact=[("drift_boat", "Push it off the rocks, out to sea.")], interact_goal="Feathermoon boat pushed out to sea",
         interact_beats=[("sound", "self", "splash"), ("move", "self", "drift_out_1", "walk"), ("wait", 7000),
                         ("move", "self", "drift_out_2", "walk"), ("summon", "sentinel_far", "sentinel_spot", 45),
                         ("summon", "sentinel_skiff", "sentinel_boat", 45), ("wait", 9000), ("face", "sentinel_far", "hub"),
                         ("emote", "sentinel_far", "point"), ("wait", 3000), ("emote", "sentinel_far", "salute"),
                         ("wait", 6000), ("despawn", "self")],
         goal="Push the drifting Feathermoon boat off the rocks of the lagoon's south arm, back out to sea where its people "
              "will find it.",
         text="A boat on the rocks. Elf-made. Good wood, good nails... It belongs to the tall ones on the island. They will "
              "come looking. Push it back out, and they find it. ...I'll only cry a little.",
         progress="The boat?",
         reward="Gone. Floating home. ...Good. Good wood should go home. Here. I kept one nail. Only one.",
         details=["point", "beg"], reward_emotes=["cry", "yes"], rewards=["seafoam_charm"],
         accept=[("face", "self", "drift_boat"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "beg"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 2000), ("face", "self", "anvil")],
         complete=[("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"), ("wait", 2000), ("emote", "self", "yes"),
                   ("emote", "self", "work"), ("sound", "self", 4614)],
         poi=["drift_boat"]),
    dict(key="ch9_keep", title="Finders Keepers", giver="ch0:krrgl", ender="ch0:krrgl", level=46, xp=8, tone="serious",
         path="menace", prev="ch9_crawl", exclusive=91, rep=[(69, -350)],
         interact=[("drift_boat", "Drag it into the lagoon.")], interact_goal="Feathermoon boat hidden under the kelp",
         interact_beats=[("sound", "self", "splash"), ("move", "self", "hide_1", "walk"), ("wait", 8000),
                         ("move", "self", "hide_spot", "walk"), ("move", "ch0:krrgl", "krrgl_shore", "run"), ("wait", 6000),
                         ("emote", "ch0:krrgl", "kneel"), ("emote", "ch0:krrgl", "kiss"), ("sound", "ch0:krrgl", "murloc_fidget2"),
                         ("object", "kelp_cover", "hide_spot", 60), ("wait", 3000), ("emote", "ch0:krrgl", "laugh"),
                         ("move", "ch0:krrgl", "krrgl", "walk"), ("wait", 6000), ("face", "ch0:krrgl", "anvil"),
                         ("despawn", "self")],
         goal="Drag the drifting Feathermoon boat off the rocks of the lagoon's south arm and into the lagoon, where the tribe "
              "will hide it under the kelp.",
         text="A boat on the rocks! Elf-made! Do you know what a tribe could do with a boat? Nobody saw it come. Nobody will "
              "see it go... into the lagoon, under the kelp. Ours.",
         progress="The boat?",
         reward="OURS. Look at the nails. Look at the joints! Oh, you beautiful thing. Here. Some of the nails were loose.",
         details=["point", "beg"], reward_emotes=["cheer", "laugh"], rewards=["elfnail_knuckles"],
         accept=[("face", "self", "drift_boat"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "beg"),
                 ("sound", "self", "murloc_fidget"), ("wait", 2000), ("face", "self", "anvil")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"), ("wait", 1500), ("emote", "self", "work"),
                   ("sound", "self", 4614), ("wait", 1200), ("emote", "self", "laugh")],
         poi=["drift_boat"]),

    # 9.21: the Elder sleeps (at dawn, on the headland)
    dict(key="ch9_elder", title="The Elder Sleeps", giver="ch1:murlorga", ender="ch1:glubbub", level=47, xp=8, tone="serious",
         prev=["ch9_warm", "ch9_totems", "ch9_orders"],
         interact=[("elder_still", "Touch his shoulder.")], interact_goal="The Elder found",
         interact_beats=[("sound", "murlorga_ring", "murloc_death"), ("emote", "murlorga_ring", "cry"), ("music", 6074),
                         ("wait", 1500), ("emote", "grrmlgrrl_ring", "kneel"), ("emote", "sloshy_ring", "cry"),
                         ("sound", "sloshy_ring", "baby_murloc"), ("emote", "mourner_part", "kneel"), ("wait", 2500),
                         ("sound", "mourner", "murloc_fidget2"), ("emote", "murlorga_ring", "cry"), ("wait", 2500),
                         ("sound", "murlorga_ring", "murloc_wound_crit"), ("emote", "grrmlgrrl_ring", "bow")],
         goal="Climb the slope east of the camp to the headland where the Elder watched the sea, and go to him.",
         text="He's not by the fire. He's not by the fire! He went up in the night... up where he looked at the sea with "
              "you. The others went to wake him. Go. Go and see why they are so quiet.",
         progress="...",
         reward="The sea called him, and he went, little one. The way the old ones go: sitting up, looking at her. ...Now we do "
                "what the old ones taught us. Now we send him home.",
         details=["question", "point", "cry"], reward_emotes=["bow", "bow"],
         accept=[("state", "self", "none"), ("face", "self", "elder"), ("emote", "self", "question"), ("wait", 1800),
                 ("face", "self", "hut_2"), ("emote", "self", "question"), ("wait", 1800), ("face", "self", "headland"),
                 ("sound", "self", 1207), ("emote", "self", "exclamation"), ("wait", 1500), ("emote", "self", "point"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "cry"), ("wait", 3000),
                 ("face", "self", "pot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "bow"), ("wait", 2500), ("emote", "self", "bow"),
                   ("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("emote", "ch1:murlorga", "cry"),
                   ("emote", "ch1:sloshy", "cry"), ("wait", 3000), ("state", "self", "sit")],
         poi=["headland"]),

    # 9.22: three things go with an elder to the sea
    dict(key="ch9_things", title="The Elder's Things", giver="ch1:glubbub", ender="ch1:glubbub", level=47, xp=8,
         tone="serious", prev="ch9_elder",
         items=[("smooth_stone", 1), ("sweet_roll", 1), ("ch1:plorp_shell", 1)],
         interact=[("ch1:murlorga", "Hold out your hands.")], interact_goal="Murlorga's last sweet roll",
         interact_beats=[("state", "self", "none"), ("emote", "self", "beg"), ("sound", "self", 1186), ("give", "sweet_roll", 1),
                         ("wait", 1500), ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"), ("wait", 3000),
                         ("face", "self", "pot"), ("state", "self", "work")],
         rewards=["smooth_stone", "sweet_roll", "ch1:plorp_shell"],
         goal="Gather the three things that go with the Elder: his Smooth Stone from his place by the fire, Murlorga's Last "
              "Sweet Roll from Murlorga's own hands, and Plorp's Name-Shell from your pack. Show them to Glubbub.",
         text="Three things go with an elder to the sea. A stone, for the bottom. Something sweet, for the long swim. And a "
              "name, so the sea knows who is coming. 1. 2. 3. You know where they are, little one.",
         progress="1... 2... 3?",
         reward="His stone. Her roll. And Plorp's shell... Plorp's. You carried him all this way? Mm. Then you lay them beside "
                "the Elder. Not me. You.",
         details=["talk", "point", "point"], reward_emotes=["yes", "bow"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1200), ("face", "self", "elder_stone"),
                 ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1800), ("emote", "self", "talk"),
                 ("wait", 1200), ("face", "self", "murlorga"), ("emote", "self", "point"), ("wait", 1800), ("emote", "self", "talk"),
                 ("wait", 1200), ("face", "self", "player"), ("emote", "self", "point"), ("wait", 2500), ("face", "self", "sea_w"),
                 ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "yes"), ("sound", "self", 1194), ("wait", 1500),
                   ("emote", "self", "yes"), ("sound", "self", 1203), ("wait", 1500), ("emote", "self", "yes"),
                   ("sound", "self", 1193), ("wait", 2000), ("emote", "self", "bow"), ("wait", 2000), ("state", "self", "sit")],
         poi=["elder_stone", "murlorga"]),

    # 9.23: the murloc funeral (the raft's scene: the tribe in the shallows, the raft going out)
    dict(key="ch9_funeral", title="The Murloc Funeral", giver="ch1:glubbub", ender="ch1:glubbub", level=47, xp=8,
         tone="serious", prev="ch9_things", event="The Elder sent to the sea",
         goal="Lay the three things beside the Elder on the Kelp Raft at the lagoon's edge, by the camp, and send him to the sea.",
         text="The raft is ready. Kelp and driftwood, the old way. Lay his things beside him, little one. Then we all walk into "
              "the water with him, and we hum. Everyone hums. Even Grrmlgrrl.",
         progress="Not yet... not yet.",
         reward="Gone to the sea. Mm. ...She will keep him. She keeps everything we give her. Even this.",
         details=["talk", "bow"], reward_emotes=["bow", "talk"],
         accept=[("state", "self", "none"), ("face", "self", "raft"), ("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 2500), ("emote", "self", "point"), ("wait", 2500), ("face", "self", "sea_w"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("aura", "player", "mourning"), ("emote", "self", "bow"),
                   ("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("wait", 2500), ("emote", "ch1:sloshy", "cry"),
                   ("wait", 2000), ("state", "self", "sit")],
         poi=["raft"]),

    # 9.24: the staff passes (three taps, and the tribe answers)
    dict(key="ch9_staff", title="The Staff Passes", giver="ch1:glubbub", ender="ch1:glubbub", level=47, xp=8, tone="serious",
         prev="ch9_funeral",
         emotes=[("ch1:glubbub", "bow", 1, [("emote", "self", "bow"), ("visual", "self", 35426), ("sound", "self", "murloc_fidget2"),
                                            ("music", 6076)])],
         goal="Stand with the tribe while Glubbub takes up the Elder's staff, and when the tribe has answered his three taps, "
              "/bow to him.",
         text="The staff. He left it leaning on the raft... he wanted it to stay. Mm. I am not ready. Nobody is ever ready. "
              "Stand with me, little one. When I tap, they answer. Then you answer.",
         progress="...",
         reward="Three taps, and the tribe answered. Then I am the Elder. Mm. Mm! The water was right. The water is always "
                "right, and I hate it.",
         details=["talk", "bow"], reward_emotes=["bow", "talk"],
         accept=[("state", "self", "none"), ("move", "self", "glubbub_raft", "walk"), ("wait", 7000), ("emote", "self", "kneel"),
                 ("sound", "self", 1216), ("wait", 1500), ("move", "self", "glubbub", "walk"), ("wait", 7000),
                 ("object", "staff_held", "staff_front", 45), ("face", "self", "fire"), ("wait", 4000)] + TAPS + [
                 ("wait", 1800)] + ANSWER_MURLORGA + [("wait", 1100)] + ANSWER_GRRMLGRRL + [("wait", 1100)]
                + ANSWER_BLRRGL + [("wait", 1100)] + ANSWER_MRRK + [("wait", 1100)] + ANSWER_SLOSHY
                + [("sound", "hatchling_a", "baby_murloc"), ("emote", "hatchling_b", "cheer"), ("wait", 1500),
                   ("face", "self", "player")],
         complete=[("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "attack"),
                   ("sound", "self", 977)],
         poi=["glubbub"]),

    # 9.25: the road out (Grrmlgrrl, grim since the funeral)
    dict(key="ch9_gordunni", title="Gordunni on the Road", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=47, xp=8,
         tone="serious", prev="ch9_funeral", kill=[(5232, 5), (5234, 3), (5240, 2)],
         goal="Kill 5 Gordunni Brutes, 3 Gordunni Maulers and 2 Gordunni Warlocks at the ogres' camp on the coast road south "
              "of the cove.",
         text="Ogres. On the road south. The road we leave by... 10 of them. Clear it.",
         progress="...",
         reward="...Good.",
         details=["talk"], reward_emotes=["talk"], choice=["road_axe", "road_staff", "road_maul"],
         accept=[("emote", "self", "kneel"), ("object", "sand_ogre", "draw_1", 40), ("sound", "self", 1194), ("wait", 2500),
                 ("emote", "self", "no"), ("wait", 1500), ("face", "self", "sea_w"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 4000), ("face", "self", "ogre_camp"), ("emote", "self", "point"), ("wait", 3000), ("face", "self", "fire")],
         complete=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "sea_w"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 5000), ("face", "self", "fire")],
         poi=["ogre_camp"]),

    # 9.26: Feathermoon's thanks (Nerelith rows home after it)
    dict(key="ch9_thanks", title="Feathermoon's Thanks", giver="elder_glubbub", ender="ch0:nerelith", level=48, xp=8,
         tone="serious", path="hero", prev=["ch9_staff", "ch9_szallah"], rep=[(69, 500)],
         interact=[("ch0:nerelith", "Sit with her by the fire.")], interact_goal="Sat with Nerelith by the fire",
         interact_beats=[("move", "self", "glubbub_front", "walk"), ("wait", 6000), ("emote", "self", "kneel"),
                         ("object", "carved_moon", "moon_spot", 120), ("sound", "self", 1193), ("wait", 2000),
                         ("emote", "self", "shy"), ("wait", 2000), ("move", "self", "neri_fire", "walk"), ("wait", 9000),
                         ("state", "self", "sit"), ("wait", 9000), ("state", "self", "none"), ("emote", "self", "bow"),
                         ("wait", 1500), ("move", "self", "nerelith", "walk"), ("wait", 14000), ("face", "self", "fire")],
         rewards=["feathermoon_cloak"],
         goal="Sit with Nerelith Saltwind by the campfire before she rows home to Feathermoon.",
         text="The tall elf is leaving. She sat by our water. She shot our enemies. She brought medicine for... for him. Sit "
              "with her, little one. Some things have no words, even in our words.",
         progress="Sit, little one. Just sit.",
         reward="Wear it. Feathermoon's colours on a Saltscar: my sisters will not know what to make of that. ...I lost a "
                "sister to the sea once. I know what this day is.",
         details=["talk", "point"], reward_emotes=["bow", "salute"],
         accept=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200), ("face", "self", "nerelith"),
                 ("emote", "self", "point"), ("wait", 2000), ("emote", "self", "bow"), ("wait", 2500), ("face", "self", "sea_w")],
         complete=[("emote", "self", "salute"), ("sound", "self", 6006)],
         poi=["nerelith"]),

    # 9.27: Mojache's thanks (Tawa walks inland)
    dict(key="ch9_mojache", title="Mojache's Thanks", giver="tawa", ender="tawa", level=48, xp=8, tone="serious",
         path="hero", prev=["ch9_staff", "ch9_drum"], rep=[(81, 500)],
         interact=[("tawa", "Say goodbye.")], interact_goal="Said goodbye to Tawa",
         interact_beats=[("state", "self", "none"), ("move", "self", "glubbub_front", "walk"), ("wait", 13000),
                         ("emote", "self", "kneel"), ("sound", "self", "murloc_fidget2"), ("wait", 3000), ("emote", "self", "bow"),
                         ("wait", 1500), ("move", "self", "tawa_inland", "walk"), ("wait", 60000),
                         ("move", "self", "tawa", "walk"), ("wait", 20000), ("face", "self", "sea_w"), ("state", "self", "work")],
         rewards=["tide_toy"],
         goal="Say goodbye to Tawa Riverchant before she goes home to Camp Mojache; she will be at the foot of the cliff path.",
         text="The sea is quiet, and my grandmother's drum is home. Camp Mojache is far, little one, and the Gordunni roads "
              "are long. Walk me to the path? A shaman does not leave without saying goodbye to the water's friends.",
         progress="Go well, little fish-man.",
         reward="Take this. A little totem for a little traveller. Hold it up when the water is angry, and remember the drum.",
         details=["talk", "bow"], reward_emotes=["bow", "wave"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("sound", "self", 11773), ("wait", 2000),
                 ("face", "self", "glubbub"), ("emote", "self", "bow"), ("wait", 2500), ("face", "self", "sea_w"),
                 ("state", "self", "work")],
         complete=[("emote", "self", "wave"), ("sound", "self", 6056)],
         poi=["tawa", "tawa_inland"]),

    # 9.28: the storm calls (Elder Glubbub's first vision: the Dream Brine again)
    dict(key="ch9_vision", title="The Storm Calls", giver="elder_glubbub", ender="elder_glubbub", level=48, xp=8,
         tone="serious", prev="ch9_staff", source="ch1:dream_brine",
         interact=[("elder_glubbub", "Drink the Dream Brine.")], interact_goal="Elder Glubbub's vision seen",
         interact_beats=[("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("take", "ch1:dream_brine", 1),
                         ("aura", "player", "ch1:dreaming"), ("music", 9462), ("wait", 1500),
                         ("teleport", "player", "vision_eye", 4.712), ("wait", 24000),
                         ("teleport", "player", "glubbub_wake", 4.712), ("unaura", "player", "ch1:dreaming"), ("wait", 1000),
                         ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 1200),
                         ("emote", "self", "point"), ("sound", "self", 30)],
         goal="Drink the Dream Brine beside Elder Glubbub, and see his first vision as Elder.",
         text="The same dream. Again. Every night since he went to the sea. The bay, the storm, the great pearl... closer "
              "now. Drink with me, little one. The Elder sees. Now I am the one who has to see.",
         progress="Drink. Drink!",
         reward="You saw her. Her face, in the storm, and the eggs hung around the pearl like fish in a net. Our clutch. The "
                "bay is in the north, little one. The storm is calling us.",
         details=["spell", "talk"], reward_emotes=["exclamation", "point"],
         accept=[("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "spell"),
                 ("wait", 1500), ("emote", "self", "eat"), ("sound", "self", 1197), ("wait", 1500), ("emote", "self", "talk")],
         complete=[("emote", "self", "exclamation"), ("sound", "self", 30), ("wait", 1500), ("face", "self", "arches"),
                   ("emote", "self", "point"), ("wait", 2000), ("emote", "self", "cry"), ("wait", 2500), ("face", "self", "sea_w")],
         poi=["glubbub"]),

    # 9.29: to the Storm Bay (three taps; the tribe answers; the turtle; thunder)
    dict(key="ch9_end", title="To the Storm Bay", giver="elder_glubbub", ender="ch0:shellback", level=48, xp=8,
         tone="serious", prev="ch9_vision", choice=["shell_leggings", "shell_breeches", "shell_legguards"],
         goal="When the tribe is ready, climb onto Grandmother Shellback, resting in the sea off the camp, for the ride north "
              "to the bay of the vision.",
         text="Three taps. That is how we begin things, and that is how we leave them. The bay of the storm is far, and the "
              "old turtle is tired. Climb on, little one. We go north. All of us.",
         progress="...",
         reward="...",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=TAPS + [("wait", 1500)] + ANSWER_MURLORGA + [("wait", 900)] + ANSWER_GRRMLGRRL
                + [("wait", 900)] + ANSWER_BLRRGL + [("wait", 900)] + ANSWER_MRRK + [("wait", 900)]
                + ANSWER_SLOSHY + [("wait", 1200), ("face", "self", "shellback"), ("emote", "self", "point"),
                                            ("sound", "ch0:shellback", "splash_big")],
         complete=[("sound", "self", "splash_big"), ("visual", "self", 36005), ("wait", 1500), ("sound", "self", 30),
                   ("visual", "self", 10387), ("emote", "ch1:murlorga", "wave"), ("emote", "ch1:sloshy", "cheer"),
                   ("sound", "ch1:grrmlgrrl", "murloc_aggro"), ("music", 8455), ("wait", 2500), ("sound", "self", 3090),
                   ("visual", "self", 51347), ("wait", 1200), ("teleport", "player", "ch10:hub", 0.0)],
         poi=["shellback"]),
]
