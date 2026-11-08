# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 5 of the naga's story: The Eye (levels 30 to 33), the bible's section 12.

The Hollow (chapter 2's camp on the islet in the Bay of Storms) is the hub: Lady Szaria where chapter 1 put her
(ch1:hollow_szaria), Isshara by her pool at the islet's south-east end, Ssaveth on his dune, Vyssa at her pot, the hub
kit round the islet: chapter 2's spawns. This chapter's scenes move them as little as they can (Vyssa goes down to the
pool and keeps her hands in the water through her song; Ssaveth sits down in the shallows through his; both go home
when they wake), and everyone who comes for one scene is summoned in it.

The present's other places:
  - Valormok (the world's and the naga's): Jediga, Ag'tor Bloodfist and Kroum are the game's own and act only in
    their quest windows (the game's creatures run no scenes of the story's); chapter 2's Peon Grukk, Jediga's runner,
    does what the bible gives Jediga to do, at her table, with her curio box beside her.
  - the sea stack in the Bay of Storms (3650-3770, -6000 to -6130: a rock forty yards high off the bay's west
    shallows, 330 yards west of the Hollow): the Spitelash's coral beds in the shallows round its west and south
    feet, guarded by Coral-Guards; the Unsingers' ring on the flat shelf at the waterline under its north face.
  - the west road below Valormok (the corridor running west from the camp toward the Southfury): Blood Guard Grozak
    keeps its head; the Spitelash war party comes up it from the river.
  - the high rock off the north strand, across the water from the Hollow (the shaman's wind), and the low islet north
    of the Hollow (where Ssethis is seen after 5.23).

Two memories, both bit A (the bible's 18.2), both sung by Isshara at her pool (one wakes on its shore):
  - m7, The Ruins of Dalaran (Vyssa's): Lake Mennar's bowl as the drowned heart of Dalaran: rubble, the statue
    of an archmage, broken arcane crystals and smoke on the slopes; four ethereal summoners hovering over the lake
    round the floating Eye; Illidan on the north shore; Lady Serpentra before a broken tower beside him; the paladin
    in a naga cage on the north-east slope; night elves and Alliance footmen on the south rim.
  - m8, The Brothers Stormrage (Ssaveth's): the Southfury's Azshara bank as the River Arevass: Illidan's camp on the
    plateau, a shelf below it, the river in its gorge, Tyrande on the low bank with the dead coming at her, the trolls'
    dam of bones and logs across the river upstream.
They stand 1450 yards apart, and 600 and 930 yards from chapter 6's crater (M12, bit A too).

Phases in Azshara: the coral beds and their guards, the bay snappers round the Hollow, the hunter's tracks and the
mage's signal fire share chapter 2's rule for the Hollow's people (HOLLOW: no bit of their own, gone with the Hollow at
7.02). This chapter's two rules are Ssethis's fates: from 5.23a he watches the Hollow from the top of the islet to
the north (and dives if anyone comes near); from 5.23b he wanders that islet's beach, unsung, and Isshara turns her
back on the one who did it whenever they come to her pool (an unseen watcher there, in the same phase). Everything
else of the present stands always (the naga's phase: the Blood Guard, Kroum's wind rider, Jediga's curio box, the
shaman's stone) or is summoned for its scene.

Choices: 1.20a/b give 5.22 two versions (Ssethis, the war party's officer, lays down his trident; or is beaten down
and dragged off screaming), as chapter 3's 3.03; 4.19a/b give 5.14 two (the ward broken with Shaelyn's moonstone
arrows, or with the Watcher's glaive: each road's own thing, given again by Isshara if it was lost); 5.23a/b is the
chapter's hero/menace pair (the fixed keys ch5_ssethis_a and ch5_ssethis_b).

Plain data: tools/murloc/SCHEMA.md, tools/naga/SCHEMA.md."""

HOLLOW = ("between", "ch2:ch2_arrival", "ch7:ch7_overturned")   # chapter 2's rule for the Hollow's people (no new bit)
SSETHIS_A = ("from", "ch5_ssethis_a")                           # Ssethis set free (5.23a): he watches from the islet
SSETHIS_B = ("from", "ch5_ssethis_b")                           # Ssethis unsung (5.23b): he wanders the islet's beach
M7 = ("memory", "m7")                                           # The Ruins of Dalaran (Vyssa's), Lake Mennar
M8 = ("memory", "m8")                                           # The Brothers Stormrage (Ssaveth's), the Southfury

CHAPTER = dict(key="ch5", title="The Eye", levels=(30, 34), map=1, zones=[16], hub="hollow")

TOWNS = ["Valormok"]

# Valormok's own people, the game's (their quests are given and taken by them; their scenes go to the story's people
# beside them: the game's creatures run no scenes of the story's)
AGTOR, JEDIGA, KROUM = 8576, 8587, 8610

PLACES = {
    # -- the Hollow (chapter 2's places; Szaria at ch1:hollow_szaria) ---------------------------------------------
    "hollow": (3955.0, -6278.0), "szaria": (3954.0, -6266.0), "pool_shore": (3959.0, -6311.0),
    "isshara": (3963.0, -6316.0), "pool": (3969.0, -6323.0), "vyssa_home": (3966.0, -6285.0),
    "vyssa_pool": (3961.0, -6320.0), "ssaveth_home": (3978.0, -6278.0), "ssaveth_water": (3967.0, -6329.0),
    "sea_south": (3880.0, -6268.0, 0.0), "sea_east": (3950.0, -6360.0, 0.0), "toward_valormok": (3681.0, -4407.0),
    "banner": (3945.0, -6258.0), "banner_front": (3948.0, -6262.0),
    # the scout comes up out of the south water (5.12), and where she's brought, and sits (5.15, the priest's lesson)
    "scout_rise": (3909.0, -6268.0, -1.0), "scout_beach": (3924.0, -6270.0), "scout_camp": (3944.0, -6272.0),
    "scout_pool": (3959.0, -6314.0), "scout_rest": (3956.0, -6305.0), "prisoner_pool": (3955.0, -6318.0),
    "scout_ache": (3948.0, -6296.0),
    # Ssethis brought in bound (5.23), the myrmidons who bring him, and the water he goes back into
    "ssethis_rise": (3912.0, -6262.0, -1.0), "ssethis_bound": (3940.0, -6266.0), "ssethis_guard_1": (3937.0, -6262.0),
    "ssethis_guard_2": (3937.0, -6271.0), "ssethis_sea": (3896.0, -6262.0, -1.0), "ssethis_shore": (3924.0, -6290.0),
    # the warrior's sand (5.16), the mage's signal fire on Ssaveth's dune
    "duel": (3965.0, -6249.0), "kessh": (3975.0, -6250.0), "signal_fire": (3982.0, -6272.0),
    # bay snappers schooling in the water round the islet (5.25)
    "school_1": (3990.0, -6262.0), "school_2": (3920.0, -6305.0), "school_3": (3930.0, -6232.0),
    "school_4": (3988.0, -6320.0), "school_5": (3908.0, -6250.0), "school_6": (3948.0, -6338.0),
    "schools": (3950.0, -6290.0),
    # the islet north of the Hollow: Ssethis's watch (5.23a on) and the beach he wanders (5.23b on)
    "islet_top": (4090.0, -6192.0), "islet_beach": (4078.0, -6172.0), "islet_dive": (4066.0, -6185.0, -1.0),
    "pool_watch": (3958.0, -6306.0),
    # the high rock off the north strand: the shaman's wind-stone on its summit
    "wind_stone": (4166.0, -6047.0),

    # -- the sea stack in the bay: the coral beds, their guards, the Unsingers' ring on the north shelf ------------
    "stack": (3700.0, -6070.0), "coral_beds": (3655.0, -6060.0),
    "coral_1": (3646.0, -6025.0), "coral_2": (3641.0, -6038.0), "coral_3": (3646.0, -6070.0), "coral_4": (3644.0, -6096.0),
    "coral_5": (3656.0, -6122.0), "coral_6": (3698.0, -6014.0), "coral_7": (3685.0, -6012.0), "coral_8": (3668.0, -6004.0),
    "coral_9": (3762.0, -6068.0), "coral_10": (3640.0, -6058.0),
    "cg_1": (3655.0, -6030.0), "cg_2": (3650.0, -6080.0), "cg_3": (3660.0, -6110.0), "cg_4": (3690.0, -6025.0),
    "cg_5": (3672.0, -6015.0), "cg_6": (3648.0, -6050.0), "cg_7": (3652.0, -6100.0), "cg_8": (3705.0, -6020.0),
    "ring": (3747.0, -6052.0), "ring_1": (3751.5, -6052.0), "ring_2": (3742.5, -6052.0), "ring_3": (3747.0, -6047.5),
    "ring_4": (3747.0, -6056.5),
    "unsinger_rise_1": (3760.0, -6062.0), "unsinger_rise_2": (3757.0, -6040.0, -1.0), "ring_free": (3754.0, -6045.0),
    # the felhunter on the stack's west beach (the warlock's lesson), the Coral-Guards' tracks (the hunter's)
    "felhunter": (3658.0, -6085.0), "track_1": (3676.0, -6012.0), "track_2": (3653.0, -6046.0), "track_3": (3652.0, -6094.0),

    # -- Valormok: Jediga's table and curio box, Grukk beside them, Ag'tor at his fire, Kroum and the wind rider ---
    "jediga": (3603.0, -4421.0), "agtor": (3601.0, -4406.0), "kroum": (3664.0, -4390.0), "grukk_home": (3607.0, -4426.0),
    "curio": (3604.5, -4418.0), "curio_side": (3606.0, -4421.5), "pearl_1": (3604.0, -4417.0, 113.3),
    "pearl_2": (3605.2, -4417.6, 113.3), "agtor_front": (3598.0, -4411.0), "wind_rider": (3658.0, -4384.0),
    "rider_lie": (3659.0, -4386.0),
    # -- the west road below Valormok: the Blood Guard at its head, the line, the war party coming up from the river --
    "bguard": (3600.0, -4318.0),
    "myr_1": (3590.0, -4286.0), "myr_2": (3610.0, -4286.0), "szaria_road": (3596.0, -4292.0),
    "line": (3600.0, -4284.0), "line_l": (3594.0, -4282.0), "line_r": (3606.0, -4282.0),
    "back_1": (3597.0, -4277.0), "back_2": (3599.0, -4279.0), "back_e1": (3594.0, -4270.0), "back_e2": (3603.0, -4286.0),
    "wp_1": (3596.0, -4262.0), "wp_2": (3603.0, -4265.0), "wp_3": (3590.0, -4268.0), "wp_4": (3608.0, -4260.0),
    "ssethis_back": (3600.0, -4252.0), "ssethis_down": (3600.0, -4268.0),
    "dragged": (3598.0, -4300.0), "west_road": (3600.0, -4270.0),

    # -- memory m7 (bit A): the ruins of Dalaran at Lake Mennar --------------------------------------------------
    "m7_centre": (2645.0, -5320.0), "m7_arrive": (2735.0, -5300.0), "m7_director": (2694.0, -5314.0),
    "m7_vyssa": (2690.0, -5312.0), "m7_serpentra": (2693.0, -5326.0), "m7_serp_side": (2690.0, -5323.0),
    "m7_tower": (2701.0, -5336.0), "m7_illidan": (2690.0, -5348.0), "m7_eye": (2638.0, -5340.0),
    "m7_sum_n": (2650.0, -5340.0), "m7_sum_s": (2626.0, -5340.0), "m7_sum_w": (2638.0, -5328.0), "m7_sum_e": (2638.0, -5352.0),
    "m7_cage": (2702.0, -5284.0), "m7_cage_door": (2699.0, -5286.0), "m7_bowl": (2700.5, -5285.0),
    "m7_magroth_out": (2716.0, -5262.0), "m7_breaker": (2708.0, -5276.0),
    "m7_guardpost": (2598.0, -5336.0), "m7_guard_1": (2596.0, -5328.0), "m7_guard_2": (2603.0, -5352.0),
    "m7_myr_1": (2684.0, -5334.0), "m7_myr_2": (2680.0, -5300.0), "m7_south": (2570.0, -5330.0),
    "p_1": (2572.0, -5284.0), "p_2": (2566.0, -5300.0), "p_3": (2576.0, -5318.0), "p_4": (2564.0, -5332.0),
    "p_5": (2578.0, -5348.0), "p_6": (2566.0, -5362.0), "p_7": (2580.0, -5376.0), "p_8": (2560.0, -5310.0),
    "p_9": (2556.0, -5345.0), "p_10": (2592.0, -5392.0), "perimeter": (2570.0, -5335.0),
    "m7_att_1": (2668.0, -5298.0), "m7_att_2": (2676.0, -5290.0), "m7_att_3": (2672.0, -5304.0),
    "m7_chim_1": (2632.0, -5318.0), "m7_chim_2": (2655.0, -5362.0), "m7_chim_3": (2675.0, -5330.0),
    "m7_frost_1": (2770.0, -5300.0), "m7_frost_2": (2770.0, -5250.0), "m7_frost_3": (2765.0, -5350.0),
    "khadgar": (2724.0, -5276.0), "rubble_1": (2716.0, -5300.0), "rubble_2": (2728.0, -5322.0), "rubble_3": (2712.0, -5352.0),
    "crystal_1": (2706.0, -5300.0), "crystal_2": (2720.0, -5340.0), "crystal_3": (2600.0, -5300.0),
    "crystal_4": (2610.0, -5384.0), "smoke_1": (2740.0, -5270.0), "smoke_2": (2580.0, -5330.0),
    "m7_banner": (2696.0, -5320.0), "m7_torch_1": (2686.0, -5318.0), "m7_torch_2": (2694.0, -5304.0),

    # -- memory m8 (bit A): the River Arevass on the Southfury's Azshara bank ------------------------------------
    "m8_centre": (2860.0, -3880.0), "m8_arrive": (2795.0, -3872.0), "m8_ssaveth": (2808.0, -3850.0),
    "m8_illidan": (2802.0, -3886.0), "m8_camp_1": (2796.0, -3892.0), "m8_camp_2": (2806.0, -3894.0),
    "m8_naga_1": (2798.0, -3878.0), "m8_naga_2": (2790.0, -3888.0),
    "m8_tyrande": (2846.0, -3840.0), "m8_sen_1": (2848.0, -3832.0), "m8_sen_2": (2842.0, -3850.0),
    "m8_overlook": (2826.0, -3840.0), "m8_river": (2860.0, -3850.0),
    # the dead on the lower slope and the bank (40 yards and more below young Ssaveth's post at the shelf's edge)
    "u_1": (2832.0, -3806.0), "u_2": (2808.0, -3806.0), "u_3": (2820.0, -3812.0), "u_4": (2838.0, -3818.0),
    "u_5": (2832.0, -3830.0), "u_6": (2838.0, -3824.0), "u_7": (2844.0, -3830.0), "u_8": (2850.0, -3872.0),
    "u_9": (2856.0, -3878.0), "u_10": (2844.0, -3872.0), "u_11": (2844.0, -3866.0), "u_12": (2832.0, -3812.0),
    "undead_shore": (2838.0, -3836.0),
    "m8_dam": (2928.0, -3910.0, 36.2), "m8_dam_2": (2934.0, -3904.0, 36.2), "dam": (2930.0, -3912.0),
    "m8_chief": (2952.0, -3946.0), "t_1": (2946.0, -3936.0), "t_2": (2952.0, -3940.0), "t_3": (2958.0, -3948.0),
    "t_4": (2950.0, -3952.0), "t_5": (2940.0, -3940.0), "t_6": (2908.0, -3920.0), "t_7": (2904.0, -3916.0),
    "t_8": (2944.0, -3946.0), "t_9": (2958.0, -3940.0), "t_10": (2916.0, -3936.0),
    "flood_1": (2915.0, -3900.0, 38.5), "flood_2": (2895.0, -3888.0, 38.5), "flood_3": (2872.0, -3870.0, 38.5),
    "m8_ill_land": (2842.0, -3846.0), "m8_malf": (2850.0, -3848.0), "m8_portal": (2838.0, -3838.0),
    "m8_cut_1": (2843.0, -3843.0), "m8_cut_2": (2848.0, -3846.0), "m8_illidan_step": (2839.0, -3840.0),
}

# -- looks and models -------------------------------------------------------------------------------------------------
CAGE = "World\\EXPANSION01\\DOODADS\\COILFANG\\PASSIVEDOODADS\\cages\\cf_groundcage.m2"
CHAINS = "World\\Expansion01\\Doodads\\Generic\\Ogre\\Chains\\OM_Chains_01.mdx"
CORAL_TREE = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree01.mdx"
CORAL_TREE_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree02.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
KHADGAR = 139                     # StatueKhadgar: an archmage of Dalaran, standing in the ruins
RUBBLE = 134                      # RockWallRubble
CRYSTAL_BROKEN = 1687             # FloatingPurpleCrystalBroken02: a broken arcane device, still glowing
CRYSTAL = 1667                    # FloatingPurpleCrystal01
SMOKE = 4852                      # StratholmeSmokeEmitter
EMBERS = 4251                     # StratholmeFireSmokeEmberS
TOWER = 2937                      # NightElfRuins04: the broken tower Serpentra stands before
BONE_DAM = 7002                   # outland_bone_dam: the trolls' dam of bones and logs
WOODPILE = 289                    # FirewoodPile03
CAMPFIRE = 192                    # ElwynnCampfire
TIGHT_WOOD = 6193                 # DarkIronWoodPile01: the unlit signal fire
TROLL_TOTEM = 653                 # stranglethorntikihead
EYE_LOOK = 2421                   # the Eye of Kilrogg's floating eye, made great: the Eye of Sargeras
CHIMAERA = 6884                   # Young Chimaera
WIND_RIDER = 6851                 # a wind rider of the Horde's
FELHUNTER = 850
WISP = 10045                      # a wisp's light: the pearl forming in the ring
PHOENIX = 17765                   # Kael'thas's phoenix
SENTINEL, SENTINEL_2, HUNTRESS = 2306, 4841, 4843
FOOTMAN, FOOTMAN_2 = 16276, 4125  # Lordaeron footmen
PALADIN = 1499
GHOUL, GHOUL_2, SKELETON = 570, 137, 200
TROLL_M, TROLL_M2, TROLL_F, TROLL_F2, TROLL_CHIEF = 28234, 28223, 3990, 3994, 28231   # forest trolls (Witherbark)
GRUNT, GRUNT_2, GRUNT_3 = 4259, 4260, 9798

# Spells for their look (tools/murloc/SCHEMA.md "visual"; scratchpad/murloc/effects.md). Instant ones are "visual"
# beats; the lasting ones (glows, banish shells, channels) are put on with "aura" and taken off with "unaura".
WATER, ARCANE_BURST, EXPLOSION, HOLY_NOVA, LIGHTNING, LIGHTNING_NOVA = 36005, 35426, 34602, 57771, 10387, 57322
FROST_HAND, ICE_SPIKE, TELEPORT, BIND, DUST, GREEN_SPLASH = 32992, 53539, 51347, 72469, 69216, 60059
INCINERATE, SPLASH_SPOUT, CORAL_FLASH = 45863, 47479, 19473
GLOW_PURPLE, GLOW_BLACK, GLOW_BLUE, BANISH_PURPLE, BANISH_WHITE = 22581, 22578, 22576, 32566, 35709
SHADOW_CHANNEL, ARCANE_CHANNEL, MANA_BEAM, SPIRIT, SPIRIT_PURPLE = 12380, 39550, 46906, 17327, 28126
FEL_SMOKE, SNOWSTORM, FROST_COLUMN, SKY_PORTAL, FEL_PORTAL, NATURE_PORTAL = 35411, 54717, 70715, 39952, 46907, 61722
BUCKET, STUN_STARS, SLEEPING, FIRE, BURNING, SPOTLIGHT = 42336, 43328, 6431, 51195, 59216, 25824
# Sounds (SoundEntries)
HORN, GRUNT_HORN, CHEST_OPEN, CHEST_CLOSE, LOCKPICK, GEMS, RING = 7054, 15880, 1277, 1278, 1164, 1221, 1193
CRACK, DAM_BREAK, SPLASH_BIG, ORC_HM, ORC_LAUGH, ORC_SIGH_F = 9122, 1269, 1097, 1345, 6943, 7921
ELF_LAUGH, ELF_SIGH, HUMAN_LAUGH, GHOUL_AGGRO, TROLL_WARCRY, TROLL_AGGRO = 6928, 7915, 6923, 409, 6200, 12009
WYVERN_AGGRO, WYVERN_FIDGET, WYVERN_FIDGET_2, CHEER_HORDE = 761, 764, 765, 8573

NPCS = [
    # -- the present: the Hollow's scenes (summoned) ------------------------------------------------------------
    # the scout who comes back from the bay with nothing in her (5.12), and the same scout later by the pool, still
    # blank (5.15), and after, aching (the priest's lesson); Ossk, the renegade the Unsingers were emptying in the ring
    dict(key="scout_blank", name="Scout Neshra", subname="The Tide-Broken", look=22869, size=1.0, level=30, role="ambient",
         untouchable=True, summoned=True, gossip="...Who is Neshra? Is she yours? You all look at me as if I should know.",
         idle=[("aura", "self", GLOW_BLACK), ("every", 13000, [("emote", "self", "question")])]),
    dict(key="scout_home", name="Scout Neshra", subname="The Tide-Broken", look=22869, size=1.0, level=30, role="ambient",
         untouchable=True, summoned=True, gossip="I don't know your name. I'm sorry. I don't know mine either. It's a nice one?",
         idle=[("aura", "self", GLOW_BLACK), ("state", "self", "sit")]),
    dict(key="prisoner_home", name="Ossk", subname="The Tide-Broken", look=22874, size=1.1, level=30, role="ambient",
         untouchable=True, summoned=True, gossip="Water. The water is... it's... I had a word for it.",
         idle=[("aura", "self", GLOW_BLACK), ("state", "self", "sit")]),
    dict(key="scout_ache", name="Scout Neshra", subname="The Tide-Broken", look=22869, size=1.0, level=30, role="ambient",
         untouchable=True, summoned=True, plural="Scout Neshra",
         gossip="Everything came back at once. The whole war, all of it, in one breath. My head won't stop ringing.",
         idle=[("state", "self", "sit"), ("every", 9000, [("emote", "self", "cry")])]),
    # Ssethis brought in bound (5.23) by two myrmidons, and their prisoner
    dict(key="ssethis_bound", name="Ssethis", subname="Prisoner of the Tide-Broken", look=11265, scale=0.95,
         equip=(0, 0, 0), level=33, role="ambient", untouchable=True, summoned=True,
         gossip="Go on. Ask me something. I'll tell you the creed. It's all I've got that you haven't taken.",
         idle=[("aura", "self", 68341), ("state", "self", "stun")]),
    # (people whom others' scenes move, turn or send away have an idle habit of their own: a creature with no scene
    # of its own is given no SmartAI by the compiler, and the beats handed to it would do nothing)
    dict(key="escort_myr", name="Tide-Broken Myrmidon", look=18389, equip=(15910, 0, 0), size=1.2, level=32, role="ambient",
         untouchable=True, summoned=True,
         idle=[("state", "self", "ready_thrown"), ("every", 37000, [("emote", "self", "roar")])]),
    dict(key="escort_myr_2", name="Tide-Broken Myrmidon", look=22874, equip=(15910, 0, 0), size=1.2, level=32,
         role="ambient", untouchable=True, summoned=True,
         idle=[("state", "self", "ready_thrown"), ("every", 41000, [("emote", "self", "roar")])]),
    # the warrior's trial: Ssaveth, sparring (Kessh calls him down to the sand; he yields at a quarter)
    dict(key="spar_ssaveth", name="Myrmidon Ssaveth", subname="Sparring", look="naga_warrior", equip=(15910, 0, 0),
         level=32, side="neutral", role="enemy", health=2.2, damage=0.45, summoned=True,
         abilities=[(11976, 6000), (11428, 16000)],
         at_health=(25, [("faction", "self", "tribe"), ("evade", "self"), ("emote", "self", "battle_roar"),
                         ("sound", "self", "naga_aggro"), ("wait", 1500),
                         ("say", "self", "Ha! There it is. That's the anger. Keep it, and keep it on a leash.", "talk"),
                         ("state", "self", "ready_thrown")]),
         idle=[("state", "self", "ready_thrown")]),
    # the mage's signal fire, burning; the light in the pool that takes a phoenix's shape (5.24)
    dict(key="signal_flame", name="Signal Fire", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("aura", "self", FIRE), ("every", 8000, [("visual", "self", EXPLOSION)])]),
    dict(key="pool_phoenix", name="A Shape on the Water", look=PHOENIX, size=0.5, level=1, role="ambient",
         unit_flags=0x02000002, summoned=True, idle=[("aura", "self", BURNING)]),
    dict(key="pool_glow", name="Isshara's Pool", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("aura", "self", SPOTLIGHT)]),
    # the shaman's wind (a gust on the headland)
    dict(key="gust", name="The Wind", look="trigger", level=1, role="ambient", unit_flags=0x02000002, summoned=True,
         idle=[("aura", "self", 36178)]),

    # -- the present: after 5.23, Ssethis on the islet north of the Hollow (one of two, by the road taken) ------------
    # freed (5.23a): on the islet's crown, looking at the Tide-Broken's banner across the water; whoever comes near,
    # he roars once and dives
    dict(key="ssethis_watching", name="Ssethis", subname="", look=11265, scale=0.95, equip=(5745, 0, 0), level=33,
         role="ambient", untouchable=True, at="islet_top", facing=3.9, phase=SSETHIS_A, respawn=180,
         gossip="I'm not here. You didn't see me. Tell your lady... nothing. Tell her nothing.",
         watch=(22, [("face", "self", "player"), ("emote", "self", "roar"), ("sound", "self", "naga_aggro"), ("wait", 2000),
                     ("move", "self", "islet_dive", "run"), ("wait", 3500), ("sound", "self", "splash"), ("despawn", "self")],
                120000),
         idle=[("state", "self", "ready_thrown"), ("every", 61000, [("face", "self", "banner")])]),
    # unsung (5.23b): wandering the islet's beach, lost
    dict(key="ssethis_lost", name="Ssethis", subname="Unsung", look=11265, scale=0.95, level=33, role="ambient",
         untouchable=True, at="islet_beach", facing=3.5, wander=9.0, phase=SSETHIS_B,
         gossip="Is this the crèche? I'm late for the creed. I'm always late. The Matron writes it down.",
         idle=[("aura", "self", GLOW_BLACK), ("every", 47000, [("emote", "self", "stun")])]),
    # and Isshara turns her back on the one who did it whenever they come to her pool (an unseen watcher there, seen
    # by those of that road alone; it shares the story's scene bit with her, so its beats reach her)
    dict(key="pool_cold", name="Isshara's Silence", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="pool_watch", phase=SSETHIS_B,
         watch=(9, [("face", "ch0:isshara", "sea_east"), ("visual", "ch0:isshara", WATER),
                    ("sound", "ch0:isshara", "pickup_water")], 60000)),

    # -- the present: the sea stack (the Spitelash's coral beds; the Unsingers' ring) ---------------------------------
    dict(key="coral_guard", name="Spitelash Coral-Guard", plural="Spitelash Coral-Guards", look=6747, looks=[11265],
         equip=(5745, 0, 0), size=1.1, level=(30, 31), side="naga", role="enemy", phase=HOLLOW, respawn=45, wander=5.0,
         abilities=[(15284, 8000), (6533, 20000)],
         at=["cg_1", "cg_2", "cg_3", "cg_4", "cg_5", "cg_6", "cg_7", "cg_8"]),
    # the Unsingers singing their ring, warded (5.13: summoned there by Isshara's hearing them), and the same four
    # unwarded when the ward breaks (5.14)
    dict(key="unsinger_warded", name="Unsinger", subname="Inquisitor of the Empress", look=11266, equip=(5284, 0, 0),
         size=1.15, level=33, role="ambient", untouchable=True, summoned=True,
         idle=[("face", "self", "ring"), ("state", "self", "channel_directed"), ("aura", "self", BANISH_PURPLE),
               ("aura", "self", SHADOW_CHANNEL), ("every", 17000, [("sound", "self", "siren_hiss")])]),
    dict(key="unsinger", name="Unsinger", plural="Unsingers", subname="Inquisitor of the Empress", look=11266,
         equip=(5284, 0, 0), size=1.15, level=(32, 33), side="naga", role="enemy", caster=True, health=1.3,
         summoned=True, abilities=[(9613, 5000), (12548, 15000)], idle=[("aura", "self", GLOW_BLACK)]),
    dict(key="ring_prisoner", name="Ossk", subname="The Tide-Broken", look=22874, size=1.1, level=30, role="ambient",
         untouchable=True, summoned=True,
         idle=[("state", "self", "kneel"), ("aura", "self", 68341), ("every", 19000, [("sound", "self", "naga_wound")])]),
    # the pearl forming over his head as his eyes go out: a cold light, warded with the ring (5.14 strikes it)
    dict(key="forming_pearl", name="A Pearl, Forming", look=WISP, size=0.3, sky=2, level=30, role="ambient",
         untouchable=True, summoned=True, gossip="It hums two songs at once, very faintly. One of them is a woman's name.",
         idle=[("aura", "self", GLOW_PURPLE), ("aura", "self", SPIRIT_PURPLE)]),
    # the warlock's lesson: a felhunter that has smelled the Unsingers' magic and come down to the stack to feed
    dict(key="wild_felhunter", name="Starving Felhunter", look=FELHUNTER, size=1.1, level=31, side="hostile",
         role="enemy", type="demon", health=1.6, summoned=True, abilities=[(3391, 9000)],
         idle=[("aura", "self", FEL_SMOKE)]),

    # -- the present: Valormok and the west road --------------------------------------------------------------------
    # Kroum's wind rider, who doesn't hold with fish-people (5.25)
    dict(key="wind_rider", name="Kroum's Wind Rider", look=WIND_RIDER, size=0.9, level=40, role="ambient", type="beast",
         side="faction:76", at="wind_rider", facing=5.6,
         gossip="The wind rider lowers its head, flattens its ears, and hisses at you. It keeps hissing.",
         watch=(7, [("face", "self", "player"), ("sound", "self", WYVERN_AGGRO)], 30000),
         idle=[("every", 37000, [("sound", "self", WYVERN_FIDGET)])]),
    # the west road's watch: Blood Guard Grozak, and what he sends down the road with you (5.22)
    dict(key="bguard", name="Blood Guard Grozak", subname="Valormok's West Road", look=GRUNT_3, equip=(5288, 0, 0),
         size=1.1, level=40, side="faction:76", language="orcish", role="ambient", at="bguard", facing=1.62,
         gossip="Road runs west to the river. Things come up the river. I stand here so they don't come further.",
         idle=[("every", 53000, [("emote", "self", "roar")])]),
    dict(key="road_grunt", name="Valormok Grunt", look=GRUNT, looks=[GRUNT_2, GRUNT_3], equip=(1905, 0, 0), level=32,
         side="ally", language="orcish", role="ambient", health=4.0, damage=0.15, summoned=True),
    dict(key="road_myr", name="Tide-Broken Myrmidon", look=18389, looks=[22874, 18398], equip=(15910, 0, 0), size=1.15,
         level=32, side="ally", role="ambient", health=4.0, damage=0.15, summoned=True,
         idle=[("every", 23000, [("emote", "self", "battle_roar")])]),
    # the grunt and the myrmidon who end up back to back
    dict(key="back_grunt", name="Valormok Grunt", look=GRUNT_2, equip=(5287, 0, 0), level=32, side="ally",
         language="orcish", role="ambient", health=6.0, damage=0.1, summoned=True,
         idle=[("every", 6000, [("emote", "self", "attack")])]),
    dict(key="back_myr", name="Tide-Broken Myrmidon", look=22874, equip=(15910, 0, 0), size=1.15, level=32, side="ally",
         role="ambient", health=6.0, damage=0.1, summoned=True, idle=[("every", 6500, [("emote", "self", "attack2h")])]),
    dict(key="szaria_road", name="Lady Szaria", subname="The Tide-Broken", look="siren", level=40, role="ambient",
         untouchable=True, summoned=True, gossip="Stand with them. We've stood with worse.",
         idle=[("every", 21000, [("emote", "self", "spell"), ("visual", "self", FROST_HAND)])]),
    dict(key="war_party", name="Spitelash Warmonger", plural="Spitelash Warmongers", look=11265, looks=[6747],
         equip=(5745, 0, 0), size=1.1, level=(33, 34), side="naga", role="enemy", health=1.1, summoned=True,
         abilities=[(15284, 8000), (11428, 18000)]),
    dict(key="war_witch", name="Spitelash Wave-Witch", look=11266, equip=(5284, 0, 0), level=33, side="naga",
         role="enemy", caster=True, summoned=True, abilities=[(9672, 6000), (11831, 20000)]),
    # Ssethis, the war party's officer (one look for both roads; what he does is each road's scene)
    dict(key="ssethis_officer", name="Ssethis", subname="War-Party Officer", look=11265, scale=0.95, equip=(5745, 0, 0),
         level=34, role="ambient", untouchable=True, summoned=True,
         idle=[("state", "self", "ready_thrown"), ("every", 27000, [("emote", "self", "battle_roar")])]),

    # -- memory m7: The Ruins of Dalaran (Vyssa's) --------------------------------------------------------------------
    dict(key="serpentra_m7", name="Lady Serpentra", subname="Sea Witch of Illidan's Host", look=18392, equip=(1907, 0, 0),
         size=1.35, level=40, role="quest", untouchable=True, language="universal", at="m7_serpentra", facing=3.4,
         phase=M7, respawn=30, gossip="Lord Illidan holds the Eye. We hold everything else. Is that clear, little one?",
         idle=[("every", 15000, [("emote", "self", "omnicast"), ("visual", "self", FROST_HAND)])]),
    dict(key="illidan_m7", name="Illidan Stormrage", subname="The Betrayer", look="illidan", equip=(32632, 32633, 0),
         size=1.1, level=40, role="ambient", untouchable=True, language="universal", at="m7_illidan", facing=3.14,
         phase=M7, respawn=30, idle=[("every", 8000, [("visual", "self", FEL_SMOKE)]),
                                     ("every", 23000, [("cast", "self", MANA_BEAM, "eye")])]),
    dict(key="eye", name="The Eye of Sargeras", look=EYE_LOOK, size=2.6, sky=10, level=1, role="ambient",
         unit_flags=0x02000002, at="m7_eye", phase=M7, respawn=30,
         idle=[("aura", "self", BANISH_PURPLE), ("every", 16000, [("visual", "self", ARCANE_BURST)])]),
    # the four ethereal summoners hovering over the lake round the Eye (only magic harms them: here, nothing does)
    dict(key="sum_n", name="Naga Summoner", subname="Of Illidan's Host", look=18392, equip=(2177, 0, 0), size=1.1, sky=3,
         level=33, role="ambient", untouchable=True, language="universal", at="m7_sum_n", facing=3.14, phase=M7, respawn=40,
         idle=[("aura", "self", SPIRIT), ("state", "self", "channel_directed"),
               ("every", 14000, [("cast", "self", MANA_BEAM, "eye")])]),
    dict(key="sum_s", name="Naga Summoner", subname="Of Illidan's Host", look=18392, equip=(2177, 0, 0), size=1.1, sky=3,
         level=33, role="ambient", untouchable=True, language="universal", at="m7_sum_s", facing=0.0, phase=M7, respawn=40,
         idle=[("aura", "self", SPIRIT), ("state", "self", "channel_directed"),
               ("every", 14000, [("cast", "self", MANA_BEAM, "eye")])]),
    dict(key="sum_w", name="Naga Summoner", subname="Of Illidan's Host", look=18392, equip=(2177, 0, 0), size=1.1, sky=3,
         level=33, role="ambient", untouchable=True, language="universal", at="m7_sum_w", facing=4.71, phase=M7, respawn=40,
         idle=[("aura", "self", SPIRIT), ("state", "self", "channel_directed"),
               ("every", 14000, [("cast", "self", MANA_BEAM, "eye")])]),
    dict(key="sum_e", name="Naga Summoner", subname="Of Illidan's Host", look=18392, equip=(2177, 0, 0), size=1.1, sky=3,
         level=33, role="ambient", untouchable=True, language="universal", at="m7_sum_e", facing=1.57, phase=M7, respawn=40,
         idle=[("aura", "self", SPIRIT), ("state", "self", "channel_directed"),
               ("every", 14000, [("cast", "self", MANA_BEAM, "eye")])]),
    # the summoners' guard (myrmidons on the shores)
    dict(key="guard_m7", name="Summoners' Guard", plural="the summoners' guard", look=18389, looks=[18398],
         equip=(15910, 0, 0), size=1.2, level=31, role="ambient", untouchable=True, language="universal",
         at=["m7_guard_1", "m7_guard_2", "m7_myr_1", "m7_myr_2"], facing=3.4, phase=M7,
         gossip="Keep clear of the circle. The Eye is drinking. It drinks anything that stands too close.",
         idle=[("state", "self", "ready_thrown"), ("every", 41000, [("emote", "self", "roar")])]),
    # the paladin in the naga cage (WC3's Magroth the Defender; his words here are the line's own)
    dict(key="magroth", name="Magroth the Defender", subname="Paladin of the Silver Hand", look=PALADIN, level=34,
         role="ambient", untouchable=True, language="universal", at="m7_cage", facing=3.6, phase=M7, respawn=40,
         gossip="Gloat, serpent. The Light has outlived worse jailers than you.",
         idle=[("state", "self", "sit"), ("every", 33000, [("emote", "self", "no")])]),
    dict(key="cage_breaker", name="Sentinel", look=SENTINEL_2, equip=(3432, 0, 0), level=31, role="ambient",
         untouchable=True, language="universal", summoned=True, idle=[("every", 9000, [("emote", "self", "point")])]),
    # the perimeter (5.08): night elf scouts and Alliance footmen on the south rim
    dict(key="ne_scout", name="Night Elf Scout", plural="Night Elf Scouts", look=SENTINEL, looks=[SENTINEL_2, HUNTRESS],
         equip=(3432, 0, 2550), level=(30, 31), side="hostile", role="enemy", language="universal", phase=M7, respawn=40,
         abilities=[(6660, 4000)], at=["p_1", "p_3", "p_5", "p_7", "p_9"], facing=0.2),
    dict(key="footman", name="Alliance Footman", plural="Alliance Footmen", look=FOOTMAN, looks=[FOOTMAN_2],
         equip=(1899, 1984, 0), level=(30, 31), side="hostile", role="enemy", language="universal", phase=M7, respawn=40,
         abilities=[(11976, 7000)], at=["p_2", "p_4", "p_6", "p_8", "p_10"], facing=0.2),
    # the night elves who come for the summoners (5.09), and their chimaeras
    dict(key="attacker", name="Sentinel Raider", plural="Sentinel Raiders", look=HUNTRESS, looks=[SENTINEL, SENTINEL_2],
         equip=(5598, 0, 0), level=(31, 32), side="hostile", role="enemy", language="universal", summoned=True,
         abilities=[(22887, 6000)]),
    dict(key="chimaera", name="Chimaera", look=CHIMAERA, size=1.6, level=33, role="ambient", type="beast",
         unit_flags=0x02000002, summoned=True, idle=[("every", 6000, [("sound", "self", 1103)])]),
    dict(key="chimaera_2", name="Chimaera", look=CHIMAERA, size=1.6, level=33, role="ambient", type="beast",
         unit_flags=0x02000002, summoned=True, idle=[("every", 7000, [("sound", "self", 1103)])]),
    # the cold wind from the north (5.06), and the spectacle as one first comes down into the ruins
    dict(key="north_wind", name="A Cold Wind", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("aura", "self", SNOWSTORM), ("every", 3000, [("visual", "self", ICE_SPIKE)])]),
    dict(key="m7_director", name="The Ruins of Dalaran", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="m7_director", phase=M7,
         watch=(14, [("music", 9461), ("visual", "eye", ARCANE_BURST), ("wait", 1500), ("visual", "sum_n", ARCANE_BURST),
                     ("visual", "sum_s", ARCANE_BURST), ("wait", 800), ("visual", "sum_w", ARCANE_BURST),
                     ("visual", "sum_e", ARCANE_BURST), ("cast", "illidan_m7", MANA_BEAM, "eye")], 150000)),

    # -- memory m8: The Brothers Stormrage (Ssaveth's) ------------------------------------------------------------------
    dict(key="illidan_m8", name="Illidan Stormrage", subname="The Betrayer", look="illidan", equip=(32632, 32633, 0),
         size=1.1, level=40, role="ambient", untouchable=True, language="universal", at="m8_illidan", facing=0.6,
         phase=M8, respawn=25, idle=[("every", 8000, [("visual", "self", FEL_SMOKE)])]),
    dict(key="tyrande_m8", name="Tyrande Whisperwind", subname="High Priestess of Elune", look="tyrande",
         equip=(5598, 0, 14105), size=1.05, level=40, role="ambient", untouchable=True, language="universal",
         at="m8_tyrande", facing=2.5, phase=M8, respawn=25,
         watch=(45, [("face", "self", "u_5"), ("yell", "self", "Come forth, you mindless wretches, and taste the wrath of the "
                                                         "Sentinels! Elune's light shall never falter!", "shout"),
                     ("visual", "self", HOLY_NOVA)], 90000),
         idle=[("state", "self", "ready_bow"), ("every", 7000, [("emote", "self", "attack")])]),
    dict(key="sentinel_m8", name="Sentinel", plural="Tyrande's sentinels", look=SENTINEL, looks=[SENTINEL_2],
         equip=(5598, 0, 2550), level=31, role="ambient", untouchable=True, language="universal",
         at=["m8_sen_1", "m8_sen_2"], facing=2.2, phase=M8,
         idle=[("every", 5000, [("emote", "self", "attack")])]),
    dict(key="malfurion_m8", name="Malfurion Stormrage", subname="Archdruid", look="malfurion", equip=(13339, 0, 0),
         size=1.25, level=40, role="ambient", untouchable=True, language="universal", summoned=True,
         idle=[("every", 20000, [("visual", "self", 13236)])]),
    dict(key="host_m8", name="Naga of Illidan's Host", plural="Illidan's naga", look=18398, looks=[18392, 22874],
         equip=(15910, 0, 0), size=1.1, level=31, role="ambient", untouchable=True, language="universal",
         at=["m8_naga_1", "m8_naga_2"], facing=0.5, phase=M8,
         idle=[("state", "self", "ready_thrown"), ("every", 47000, [("emote", "self", "roar")])]),
    dict(key="ghoul", name="Ghoul", plural="Ghouls", look=GHOUL, looks=[GHOUL_2], level=(31, 32), side="hostile",
         role="enemy", type="undead", language="universal", phase=M8, respawn=40, wander=3.0, abilities=[(9080, 9000)],
         at=["u_1", "u_3", "u_4", "u_5", "u_7", "u_9", "u_11", "u_12"]),
    dict(key="skeleton", name="Skeletal Warrior", plural="Skeletal Warriors", look=SKELETON, equip=(1899, 0, 0),
         level=(31, 32), side="hostile", role="enemy", type="undead", language="universal", phase=M8, respawn=40,
         abilities=[(11976, 7000)], at=["u_2", "u_6", "u_8", "u_10"]),
    # the dead Illidan cuts through on his way to her (5.21)
    dict(key="fodder", name="Ghoul", look=GHOUL, level=32, role="ambient", untouchable=True, type="undead",
         language="universal", summoned=True, idle=[("every", 2500, [("emote", "self", "attack")])]),
    dict(key="fodder_2", name="Skeletal Warrior", look=SKELETON, equip=(1899, 0, 0), level=32, role="ambient",
         untouchable=True, type="undead", language="universal", summoned=True,
         idle=[("every", 2700, [("emote", "self", "attack")])]),
    dict(key="troll", name="Forest Troll", plural="Forest Trolls", look=TROLL_M, looks=[TROLL_M2, TROLL_F, TROLL_F2],
         equip=(1905, 0, 5870), level=(32, 33), side="hostile", role="enemy", language="universal", phase=M8, respawn=40,
         abilities=[(22887, 6000), (15580, 9000)],
         at=["t_1", "t_2", "t_3", "t_4", "t_5", "t_6", "t_7", "t_8", "t_9", "t_10"]),
    dict(key="troll_chief", name="Forest Troll Chieftain", look=TROLL_CHIEF, size=1.25, equip=(5287, 0, 0), level=33,
         side="hostile", role="enemy", language="universal", health=2.5, phase=M8, respawn=60, at="m8_chief",
         facing=2.4, abilities=[(8599, 25000), (13730, 18000), (15284, 7000)],
         watch=(30, [("yell", "self", "Dis river be ours! Turn back, snakes!", "shout", TROLL_WARCRY)], 60000)),
    dict(key="flood", name="The River", look="trigger", level=1, role="ambient", unit_flags=0x02000002, summoned=True,
         idle=[("every", 1500, [("visual", "self", SPLASH_SPOUT)])]),
]

OBJECTS = [
    # -- the present: the Hollow ----------------------------------------------------------------------------------
    dict(key="signal_wood", model=TIGHT_WOOD, name="Unlit Signal Fire", kind="use", quest="ch5_lesson_mage",
         consumable=False, at="signal_fire", scale=0.8, goal="Signal fire lit", phase=HOLLOW,
         beats=[("visual", "player", ARCANE_BURST), ("summon", "signal_flame", "signal_fire", 120),
                ("emote", "ch0:lyrenne", "roar"), ("face", "ch0:ssaveth", "signal_fire"), ("emote", "ch0:ssaveth", "roar")]),
    dict(key="snapper_school", model=SHELL, name="Bay Snapper School", kind="use", quest="ch5_wind_rider",
         consumable=True, respawn=30, scale=1.2, phase=HOLLOW,
         at=["school_1", "school_2", "school_3", "school_4", "school_5", "school_6"],
         beats=[("give", "bay_snapper", 1), ("sound", "player", "splash"), ("visual", "player", WATER)]),
    dict(key="wind_stone", model=SHELL, name="Wind-Worn Stone", kind="use", quest="ch5_lesson_shaman", consumable=False,
         at="wind_stone", scale=2.2, goal="The wind caught on the headland",
         beats=[("summon", "gust", "wind_stone", 12), ("visual", "player", LIGHTNING_NOVA), ("sound", "player", 3090)]),
    dict(key="dropped_trident_obj", model=TRIDENT, name="Ssethis's Trident", kind="doodad", scale=0.9),
    dict(key="pearl_glint", model="great_pearl", name="Singing Pearl", kind="doodad", scale=0.07),
    dict(key="bowl_left", model=SHELL, name="Bowl of Gruel", kind="doodad", scale=0.45),
    # -- the present: the coral beds round the sea stack, and the Coral-Guards' tracks ---------------------------------
    dict(key="coral_bed", model=CORAL_TREE_2, name="Enchanted Coral", kind="use", quest="ch5_coral", consumable=True,
         respawn=40, scale=0.7, phase=HOLLOW,
         at=["coral_1", "coral_2", "coral_3", "coral_4", "coral_5", "coral_6", "coral_7", "coral_8", "coral_9", "coral_10"],
         beats=[("give", "enchanted_coral", 1), ("visual", "player", CORAL_FLASH), ("sound", "player", GEMS)]),
    dict(key="guard_tracks", model=SHELL, name="Coral-Guard Tracks", kind="use", quest="ch5_lesson_hunter",
         consumable=True, respawn=30, scale=0.4, phase=HOLLOW, at=["track_1", "track_2", "track_3"],
         goal="Coral-Guard tracks read", beats=[("sound", "player", 1187), ("visual", "player", DUST)]),
    # -- the present: Valormok ------------------------------------------------------------------------------------
    # Jediga's curio box on her table (the rogue picks its lock and locks it again)
    dict(key="curio_box", model="chest", name="Jediga's Curio Box", kind="use", quest="ch5_lesson_rogue",
         consumable=False, at="curio", scale=0.45, facing=1.2, goal="Jediga's lock picked, and locked again",
         beats=[("sound", "player", LOCKPICK), ("wait", 1800), ("sound", "player", CHEST_OPEN), ("wait", 1500),
                ("sound", "player", CHEST_CLOSE), ("sound", "player", LOCKPICK), ("face", "ch2:grukk", "curio"),
                ("emote", "ch2:grukk", "question"), ("wait", 2500), ("face", "ch2:grukk", "player"),
                ("emote", "ch2:grukk", "shy")]),

    # -- memory m7: the ruins (rubble, an archmage's statue, broken crystals, smoke), Serpentra's tower, the cage ------
    dict(key="m7_khadgar", model=KHADGAR, name="Statue of an Archmage", kind="doodad", at="khadgar", facing=3.6,
         scale=1.1, phase=M7),
    dict(key="m7_rubble", model=RUBBLE, name="Rubble", kind="doodad", at=["rubble_1", "rubble_2", "rubble_3"], scale=1.3,
         phase=M7),
    dict(key="m7_crystal", model=CRYSTAL_BROKEN, name="Broken Arcane Device", kind="doodad",
         at=["crystal_1", "crystal_2", "crystal_3", "crystal_4"], scale=0.8, phase=M7),
    dict(key="m7_smoke", model=SMOKE, name="Smoke", kind="doodad", at=["smoke_1", "smoke_2"], phase=M7),
    dict(key="m7_tower", model=TOWER, name="Broken Tower", kind="doodad", at="m7_tower", facing=3.5, scale=1.2, phase=M7),
    dict(key="m7_banner", model="naga_banner", name="Illidan's Banner", kind="doodad", at="m7_banner", facing=3.4, phase=M7),
    dict(key="m7_torch", model="naga_torch", name="Naga Torch", kind="doodad", at=["m7_torch_1", "m7_torch_2"], phase=M7),
    dict(key="m7_cage", model=CAGE, name="Naga Cage", kind="doodad", at="m7_cage", facing=3.6, scale=1.2, phase=M7),
    dict(key="m7_cage_bars", model=CHAINS, name="The Cage's Bars", kind="use", quest="ch5_paladin", consumable=False,
         scale=0.6, at="m7_cage_door", facing=0.4, goal="Bowl set inside the paladin's cage", phase=M7,
         beats=[("take", "gruel", 1), ("object", "bowl_left", "m7_bowl", 60), ("sound", "player", 1186),
                ("face", "magroth", "player"), ("wait", 1200),
                ("say", "magroth", "Keep your slop, serpent. The Alliance is coming, and the Light comes with it.", "no"),
                ("wait", 3500), ("emote", "magroth", "rude"), ("wait", 2000), ("face", "magroth", "m7_eye")]),

    # -- memory m8: Illidan's camp, the trolls' dam ------------------------------------------------------------------
    dict(key="m8_banner", model="naga_banner", name="Illidan's Banner", kind="doodad", at="m8_camp_2", facing=0.5, phase=M8),
    dict(key="m8_torch", model="naga_torch", name="Naga Torch", kind="doodad", at="m8_camp_1", phase=M8),
    dict(key="m8_dam_doodad", model=WOODPILE, name="Troll Dam", kind="doodad", at="m8_dam_2", scale=2.5, facing=1.0, phase=M8),
    dict(key="m8_totem", model=TROLL_TOTEM, name="Troll Totem", kind="doodad", at="t_5", scale=0.9, facing=2.2, phase=M8),
    dict(key="dam", model=BONE_DAM, name="The Trolls' Dam", kind="use", quest="ch5_dam", consumable=True, respawn=60,
         at="m8_dam", facing=1.0, scale=0.6, goal="The trolls' dam broken", phase=M8,
         beats=[("sound", "player", DAM_BREAK), ("visual", "player", WATER), ("summon", "flood", "flood_1", 12),
                ("summon", "flood", "flood_2", 12), ("summon", "flood", "flood_3", 12), ("sound", "player", SPLASH_BIG),
                ("wait", 1500), ("sound", "player", SPLASH_BIG)]),
]

ITEMS = [
    # what quests ask for and hand over
    dict(key="enchanted_coral", name="Enchanted Coral", icon="item:20029", stack=8,
         description="It glows when it's broken off, and goes on glowing in the bag. The Spitelash fight over it."),
    dict(key="vyssa_pearl", name="Song-Pearl: The Ruins of Dalaran", icon="item:5500",
         description="It hums cheerfully. Then it stops, the way someone stops in the middle of a laugh."),
    dict(key="ssaveth_pearl", name="Song-Pearl: The River Arevass", icon="item:5500",
         description="It hums like a river. Somewhere in it a myrmidon is out of breath."),
    dict(key="gruel", name="Bowl of Gruel", icon=22417, description="Lake water and fish. It was warm once."),
    dict(key="unsung_pearl", name="Unfinished Song-Pearl", icon="pearl",
         description="Half-made, cold, humming two songs at once. One of them is a woman's name."),
    dict(key="blank_pearl", name="Unsinger's Empty Pearl", icon="pearl",
         description="Taken from the ring on the rock. It's waiting for something to fill it."),
    dict(key="bay_snapper", name="Bay Snapper", icon="fish", stack=5, description="Snaps. Even now."),

    # rewards (the game's quests' greens at these levels)
    dict(key="coral_cuffs", name="Coral-Studded Cuffs", kind="armor:mail:wrist", quality=2, level=30,
         stats=[("str", 5), ("sta", 4)]),
    dict(key="coral_wraps", name="Coral-Woven Wraps", kind="armor:cloth:wrist", quality=2, level=30,
         stats=[("int", 5), ("spi", 4)]),
    dict(key="coral_bracers", name="Coralhide Bracers", kind="armor:leather:wrist", quality=2, level=30,
         stats=[("agi", 5), ("sta", 4)]),
    dict(key="ember_mantle", name="Eye-Scorched Mantle", kind="armor:cloth:shoulder", quality=2, level=31,
         stats=[("int", 8), ("spi", 6), ("sta", 3)]),
    dict(key="guard_leggings", name="Summoners'-Guard Leggings", kind="armor:leather:legs", quality=2, level=31,
         stats=[("agi", 10), ("sta", 8)]),
    dict(key="ruin_girdle", name="Girdle of the Fallen City", kind="armor:mail:waist", quality=2, level=31,
         stats=[("str", 8), ("sta", 6)]),
    dict(key="water_cord", name="Serpentra's Water-Cord", kind="armor:cloth:waist", quality=2, level=31,
         stats=[("sta", 6), ("int", 5), ("spi", 5)],
         description="A siren's belt of braided kelp. Vyssa carried her lady's water on it."),
    dict(key="ward_trident", name="Ward-Breaker Trident", kind="weapon:spear", quality=2, level=32,
         stats=[("str", 14), ("sta", 10)]),
    dict(key="unsinger_bane", name="Unsinger's Bane", kind="weapon:dagger", quality=2, level=32,
         stats=[("agi", 6), ("sta", 4)]),
    dict(key="keeper_staff", name="Keeper's Driftwood Staff", kind="weapon:staff", quality=2, level=32,
         stats=[("int", 14), ("spi", 10)]),
    dict(key="neshra_ring", name="Neshra's Shell Ring", kind="ring", quality=2, level=32, stats=[("sta", 5), ("spi", 4)],
         description="She pushed it into your hand and laughed. She couldn't remember buying it. Now she can."),
    # the lessons' small things
    dict(key="kessh_band", name="Sparring Band", kind="ring", quality=2, level=31, stats=[("str", 4), ("sta", 4)]),
    dict(key="snaptamer_quiver", name="Coral-Guard Trail Cloak", kind="armor:cloth:back", quality=2, level=31,
         stats=[("agi", 5), ("sta", 3)]),
    dict(key="quickfin_pick", name="Quickfin's Pick", kind="weapon:dagger", quality=2, level=31, stats=[("agi", 5), ("sta", 3)]),
    dict(key="lyrenne_ember", name="Lyrenne's Banked Ember", kind="offhand", quality=2, level=31,
         stats=[("int", 5), ("spi", 3)], description="Still warm. Her eyebrows are fine. Mostly."),
    dict(key="thessa_shell", name="Thessa's Quiet Shell", kind="offhand", quality=2, level=31, stats=[("int", 4), ("spi", 5)]),
    dict(key="nazreth_charm", name="Felhunter's Collar", kind="neck", quality=2, level=31, stats=[("sta", 4), ("int", 4)]),
    # the river's (5.21)
    dict(key="arevass_robe", name="Robe of the River Arevass", kind="armor:cloth:chest", quality=2, level=32,
         stats=[("int", 11), ("sta", 7), ("spi", 6)]),
    dict(key="arevass_jerkin", name="Riverbank Jerkin", kind="armor:leather:chest", quality=2, level=32,
         stats=[("agi", 12), ("sta", 10)]),
    dict(key="arevass_hauberk", name="Dam-Breaker's Hauberk", kind="armor:mail:chest", quality=2, level=32,
         stats=[("str", 12), ("sta", 10)]),
    # the west road's (5.22)
    dict(key="war_axe", name="Valormok Road-Axe", kind="weapon:axe", quality=2, level=33, stats=[("str", 7), ("sta", 5)]),
    dict(key="back_blade", name="Back-to-Back Blade", kind="weapon:sword", quality=2, level=33, stats=[("agi", 7), ("sta", 5)]),
    dict(key="grunt_staff", name="Grunt-Carved Spirit Staff", kind="weapon:staff", quality=2, level=33,
         stats=[("int", 15), ("spi", 11)]),
    # the chapter's last (5.24)
    dict(key="phoenix_gloves", name="Phoenix-Shadow Gloves", kind="armor:cloth:hands", quality=2, level=33,
         stats=[("int", 8), ("spi", 6)]),
    dict(key="pool_grips", name="Pool-Keeper's Grips", kind="armor:leather:hands", quality=2, level=33,
         stats=[("agi", 8), ("sta", 6)]),
    dict(key="tide_gauntlets", name="Gauntlets of the Turning Tide", kind="armor:mail:hands", quality=2, level=33,
         stats=[("str", 8), ("sta", 6)]),
    dict(key="feather", name="Wind Rider's Moulted Feather", kind="trinket", quality=2, level=33,
         stats=[("agi", 4), ("sta", 4)], description="It sneezed this out. Kroum says that's how you know it likes you."),
    dict(key="snapper_snack", name="Grilled Bay Snapper", kind="food", level=30, icon="fish"),
]

AURAS = [
    dict(key="dark_sky", name="The Sky Darkens", kind="screen", screen=342, seconds=10),
    dict(key="white_burst", name="The Eye Breaks", kind="screen", screen=161, seconds=3),
    dict(key="wind_slap", name="Sneezed On", kind="mark", seconds=20, icon=36005, visual=0,
         text="A wind rider sneezed on you. It's warm. It's everywhere."),
]

MEMORIES = [
    dict(key="m7", name="The Ruins of Dalaran", whose="Vyssa", bit="A",
         text="Vyssa's memory: the ruins of Dalaran, the summoners round the Eye, Lady Serpentra. What she saw, you see.",
         stage="m7_arrive", facing=3.53, centre="m7_centre", radius=130, pool="pool_shore", pool_facing=0.83,
         singer="ch0:isshara", again="Sing Vyssa's song again. Send me back to Dalaran."),
    dict(key="m8", name="The Brothers Stormrage", whose="Ssaveth", bit="A",
         text="Myrmidon Ssaveth's memory: the River Arevass, and the priestess on its bank. What he saw, you see.",
         stage="m8_arrive", facing=0.56, centre="m8_centre", radius=135, pool="pool_shore", pool_facing=0.83,
         singer="ch0:isshara", again="Sing Ssaveth's river song again."),
]

QUESTS = [
    # 5.01: Jediga's price (funny): her runner opens the box, the pearls hum, he snaps it shut, and counts for her
    dict(key="ch5_price", title="Jediga's Price", giver=JEDIGA, ender=JEDIGA, level=30, xp=8, tone="funny",
         prev="ch4:ch4_end",
         interact=[("ch2:grukk", "Ask to see the singing pearls.")], interact_goal="Jediga's curio box opened for you",
         interact_beats=[("face", "self", "player"), ("emote", "self", "yes"), ("move", "self", "curio_side", "walk"),
                         ("wait", 2500), ("face", "self", "curio"), ("emote", "self", "work"), ("sound", "self", CHEST_OPEN),
                         ("object", "pearl_glint", "pearl_1", 6), ("object", "pearl_glint", "pearl_2", 6),
                         ("sound", "self", "siren_hiss"), ("wait", 3500), ("emote", "self", "work"),
                         ("sound", "self", CHEST_CLOSE), ("wait", 1000), ("face", "self", "player"),
                         ("say", "self", "Boss says five.", "talk"), ("wait", 2000), ("face", "self", "jediga"), ("wait", 1500),
                         ("face", "self", "player"), ("say", "self", "Boss says TEN.", "exclamation"), ("wait", 2500),
                         ("say", "self", "Not gold. Boss says she has gold. Boss says shiny coral, the kind the fish-people "
                                         "fight over. Buyer in Orgrimmar.", "talk"),
                         ("wait", 3000), ("move", "self", "grukk_home", "walk")],
         goal="Ask Peon Grukk, beside Jediga at Valormok, to show you the singing pearls in her curio box, then hear "
              "Jediga's price.",
         text="Pearls? I have a box. In the box, maybe pearls. Maybe they sing. A naga deserter sold them to me for a "
              "sack of bread, and since then they hum all night and my runner can't sleep. Grukk! Show the fish what's "
              "in the box. Show, not touch.",
         progress="You looked. Now you know the price. Why are you still here?",
         reward="Enchanted Coral. The Spitelash's own, the stuff that glows. A buyer in Orgrimmar puts it in rings for "
                "officers' wives. Eight pieces, and the pearls are yours. That is a very fair price. I am famous for fair.",
         details=["talk", "point"], reward_emotes=["point", "talk", "no", "talk"],
         poi=["curio"]),

    # 5.02: the coral beds (boring): Coral-Guards walk the shallows round the sea stack; each coral glows as it breaks
    dict(key="ch5_coral", title="Enchanted Coral", giver=JEDIGA, ender=JEDIGA, level=30, xp=8, tone="boring",
         prev="ch5_price", items=[("enchanted_coral", 8)], choice=["coral_cuffs", "coral_wraps", "coral_bracers"],
         goal="Break 8 pieces of Enchanted Coral from the Spitelash's coral beds in the shallows round the sea stack, "
              "west of the Hollow in the Bay of Storms, and bring them to Jediga.",
         text="The Spitelash grow it round the big rock in the bay, the one west of your camp, under the water and on the "
              "sand. They guard it like it was their mothers. You are a fish-person; you swim; you know how to look "
              "harmless to other fish-people. Eight pieces. Not seven. Grukk counts.",
         progress="Grukk is counting the coral you didn't bring. It's taking him no time at all.",
         reward="Eight. Grukk, eight? ...Grukk says nine, but Grukk can't count past his fingers and he lost one to a "
                "kodo. Eight. Good. Glowing. Very good. Take something for your wrists; I have more wrists than coral.",
         details=["talk"], reward_emotes=["talk", "point"],
         poi=["coral_beds"]),

    # 5.03: the commission (funny): one pearl across the table, one kept; the chief clears his throat behind her
    dict(key="ch5_commission", title="Jediga's Commission", giver=JEDIGA, ender="ch0:isshara", level=30, xp=8,
         tone="funny", prev="ch5_coral", rep=[(76, 150)],
         interact=[("ch2:grukk", "Hold out your hand for the pearls.")], interact_goal="The pearls paid out",
         interact_beats=[("face", "self", "player"), ("move", "self", "curio_side", "walk"), ("wait", 2500),
                         ("face", "self", "curio"), ("emote", "self", "work"), ("sound", "self", CHEST_OPEN),
                         ("object", "pearl_glint", "pearl_2", 12), ("wait", 1500), ("face", "self", "player"),
                         ("give", "vyssa_pearl", 1), ("sound", "player", GEMS),
                         ("say", "self", "One. For the coral.", "talk"), ("wait", 2500), ("emote", "self", "point"),
                         ("say", "self", "That one, boss keeps. Commission.", "talk"), ("wait", 3000),
                         ("sound", "self", ORC_HM), ("face", "self", "agtor"), ("emote", "self", "shy"), ("wait", 2500),
                         ("face", "self", "jediga"), ("sound", "self", ORC_SIGH_F), ("wait", 2000), ("face", "self", "curio"),
                         ("emote", "self", "work"), ("face", "self", "player"), ("give", "ssaveth_pearl", 1),
                         ("sound", "player", GEMS), ("say", "self", "...Both. Boss says both. Chief was looking.", "talk"),
                         ("emote", "self", "bow"), ("wait", 2500), ("move", "self", "grukk_home", "walk")],
         items=[("vyssa_pearl", 1), ("ssaveth_pearl", 1)],
         goal="Collect your pearls from Peon Grukk at Jediga's table, and take them to Isshara at her pool in the Hollow.",
         text="Business. You pay, I pay. The coral for one pearl, and one pearl stays here as my commission, for the "
              "finding, and the keeping, and the humming all night. That is how a market works. Grukk, give the fish "
              "its pearl.",
         progress="Two songs. I can hear them in your bag from here. Bring them to me, little one.",
         reward="Two. Ah. Listen to them... One is bright and silly and sad underneath, and one is out of breath. I know "
                "whose they are. Oh, I know. Sit down a moment. Both of them are going to need us.",
         details=["talk", "no"], reward_emotes=["talk"],
         complete=[("face", "self", "player"), ("visual", "self", WATER), ("sound", "self", "pickup_water"), ("wait", 1500),
                   ("emote", "self", "omnicast"), ("sound", "self", ELF_LAUGH), ("wait", 2000), ("face", "self", "vyssa_home"),
                   ("wait", 2000), ("face", "self", "ssaveth_home"), ("wait", 1500), ("face", "self", "player")],
         poi=["curio", "isshara"]),

    # 5.04: Vyssa's song (into m7): the cheerful one goes quiet and keeps her hands in the water
    dict(key="ch5_vyssa_song", title="Vyssa's Song", giver="ch0:isshara", ender="ch0:vyssa_young", level=30, xp=8,
         tone="serious", prev="ch5_commission", memory="m7", explore="m7_vyssa", radius=9,
         goal="Touch the water while Isshara sings Vyssa's pearl. In the memory, find young Vyssa on the slope above the "
              "lake.",
         text="The first one is Vyssa's. You'd never know it, the way she laughs at her pot. It's Dalaran, the ruins of "
              "it, the night Illidan held the Eye, and she was there, and she has never once said so. Vyssa. Come here, my "
              "dear. Come and sit by the water. You don't have to look. Only listen.",
         progress="Find her. She'll be carrying something heavy. She always was.",
         reward="Oh! You're new. Here, take one side of this. Lady Serpentra's water, all the way from the lake, and Lady "
                "Serpentra will know if I spill a drop. Don't look at the light too long. It looks back.",
         details=["talk"], reward_emotes=["laugh", "wave"],
         accept=[("face", "self", "vyssa_home"), ("emote", "self", "talk"),
                 ("say", "self", "Vyssa. Come and sit by the water.", "talk"),
                 ("state", "ch0:vyssa", "none"), ("face", "ch0:vyssa", "isshara"), ("wait", 1500),
                 ("move", "ch0:vyssa", "vyssa_pool", "walk"), ("wait", 14500), ("face", "ch0:vyssa", "pool"),
                 ("emote", "ch0:vyssa", "work"), ("visual", "ch0:vyssa", WATER), ("sound", "ch0:vyssa", "pickup_water"),
                 ("state", "ch0:vyssa", "work"), ("wait", 2500),
                 ("face", "self", "pool"), ("state", "self", "channel"), ("sound", "self", "siren_hiss"), ("music", 9461),
                 ("visual", "player", ARCANE_BURST), ("wait", 3500), ("relive", "m7"), ("wait", 2000), ("state", "self", "none")],
         complete=[("emote", "self", "laugh"), ("wait", 1200), ("emote", "self", "point"), ("wait", 1500),
                   ("face", "self", "m7_eye"), ("wait", 1500), ("face", "self", "player")],
         poi=["m7_vyssa"]),

    # 5.05: the ruined city: down through the streets to the summoners' guard on the far shore
    dict(key="ch5_ruined_city", title="The Ruined City", giver="ch0:vyssa_young", ender="ch0:vyssa_young", level=30,
         xp=8, tone="serious", prev="ch5_vyssa_song", memory="m7", explore="m7_guardpost", radius=14,
         goal="In Vyssa's memory, go round the lake through Dalaran's ruins to the summoners' guard on the south shore, "
              "and come back to young Vyssa.",
         text="The summoners need the guard to know the water's coming. Go round the lake, through the streets, to the "
              "guard on the far shore, and tell them. Go round, not across! You don't swim near the circle. Nobody swims "
              "near the circle. Lady Serpentra says the Eye drinks anything that comes close, and she says it like a joke, "
              "and it isn't.",
         progress="Round the lake. Not across.",
         reward="You went round? Good. I went across once. Only once. Lady Serpentra pulled me out by the hair and it hasn't "
                "lain flat since. Look at it.",
         details=["point", "talk"], reward_emotes=["laugh"],
         accept=[("aura", "self", BUCKET), ("face", "self", "m7_guardpost"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "m7_eye"), ("emote", "self", "shy"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "laugh"), ("sound", "self", "pickup_water")],
         complete=[("emote", "self", "laugh"), ("sound", "self", "pickup_water"), ("wait", 1500), ("emote", "self", "point"),
                   ("emote", "guard_m7", "roar"), ("wait", 1500), ("face", "self", "m7_eye")],
         poi=["m7_guardpost"]),

    # 5.06: it's working (Illidan wields the Eye; the sky darkens; a cold wind from the north)
    dict(key="ch5_working", title="It's Working", giver="ch0:vyssa_young", ender="ch0:vyssa_young", level=31, xp=8,
         tone="serious", prev="ch5_ruined_city", memory="m7", event="Illidan's spell seen",
         goal="In Vyssa's memory, stand with young Vyssa on the slope and watch Illidan wield the Eye.",
         text="He's going to do it now. Look at the summoners: they've stopped humming, they're only breathing. Stand "
              "here with me. Lady Serpentra says when it starts the whole north will feel it. The whole north! From here!",
         progress="Watch him. Watch the Eye.",
         reward="Did you feel it? The whole world leaned. Like a boat when everyone runs to one side. I spilled the water. "
                "Don't tell her.",
         details=["point", "talk"], reward_emotes=["cheer", "laugh"],
         accept=[("face", "self", "m7_illidan"), ("emote", "self", "point"), ("wait", 1500), ("music", 9462),
                 ("face", "illidan_m7", "m7_eye"), ("cast", "illidan_m7", MANA_BEAM, "eye"), ("visual", "eye", ARCANE_BURST),
                 ("wait", 2500),
                 ("yell", "illidan_m7", "It's working! Nothing can withstand the power of the Eye! Soon now, my master's "
                                        "enemies will be undone, and I will claim my just reward."),
                 ("aura", "eye", SKY_PORTAL), ("aura", "player", "dark_sky"), ("wait", 3000),
                 ("visual", "sum_n", ARCANE_BURST), ("visual", "sum_s", ARCANE_BURST), ("visual", "sum_w", ARCANE_BURST),
                 ("visual", "sum_e", ARCANE_BURST), ("wait", 2000),
                 ("summon", "north_wind", "m7_frost_1", 25), ("summon", "north_wind", "m7_frost_2", 25),
                 ("summon", "north_wind", "m7_frost_3", 25), ("sound", "self", 3090), ("wait", 2500),
                 ("face", "self", "m7_frost_1"), ("emote", "self", "question"), ("wait", 2500),
                 ("visual", "eye", ARCANE_BURST), ("emote", "serpentra_m7", "battle_roar"), ("sound", "serpentra_m7", "siren_aggro"),
                 ("emote", "guard_m7", "roar"), ("wait", 3000), ("credit", "ch5_working"), ("wait", 8000),
                 ("unaura", "eye", SKY_PORTAL)],
         complete=[("emote", "self", "cheer"), ("visual", "self", WATER), ("sound", "self", "pickup_water"), ("wait", 1500),
                   ("emote", "self", "shy"), ("wait", 1500), ("face", "self", "m7_eye")],
         poi=["m7_vyssa"]),

    # 5.07: the paladin in the cage (boring): you're his jailer, as you once carried a basket to Isshara's
    dict(key="ch5_paladin", title="The Paladin in the Cage", giver="ch0:vyssa_young", ender="ch0:vyssa_young", level=31,
         xp=8, tone="boring", prev="ch5_working", memory="m7", source="gruel", objects=[("m7_cage_bars", 1)],
         goal="In Vyssa's memory, set the Bowl of Gruel inside the bars of the paladin's cage on the slope above the lake.",
         text="The human in the cage has to eat. Lady Serpentra says so. Lord Illidan says nothing, which means Lady "
              "Serpentra decides. Take him this. Put it inside the bars and come away. He talks. Don't listen; he talks "
              "the way a cliff talks to the sea.",
         progress="Did he eat it? He never eats it.",
         reward="He didn't eat it. He never does. He'll be thin when they come for him, and they'll be angry about that "
                "too.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "m7_cage"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk"), ("face", "magroth", "m7_vyssa")],
         complete=[("face", "self", "m7_cage"), ("emote", "self", "no"), ("wait", 1500), ("face", "self", "player"),
                   ("emote", "self", "shy")],
         poi=["m7_cage"]),

    # 5.08: Serpentra's orders: hold the perimeter (she directs from before her broken tower)
    dict(key="ch5_perimeter", title="Serpentra's Orders", giver="serpentra_m7", ender="serpentra_m7", level=31, xp=8,
         tone="serious", prev="ch5_paladin", memory="m7", kill=[("ne_scout", 5), ("footman", 5)],
         goal="In Vyssa's memory, kill 5 Night Elf Scouts and 5 Alliance Footmen creeping along the lake's south rim.",
         text="The land-walkers crawl along the rim like crabs: night elves out of the trees, humans out of their "
              "fallen city. The spell needs time and silence. Hold the perimeter. Nothing comes down that slope to my "
              "summoners while Lord Illidan holds the Eye.",
         progress="I can still see them on the rim.",
         reward="Ten. The rim is quiet. Quiet is not empty, little one. Watch the trees.",
         details=["spell", "talk"], reward_emotes=["talk"],
         accept=[("face", "self", "m7_south"), ("emote", "self", "point"), ("cast", "self", FROST_HAND, "player"),
                 ("wait", 1500), ("emote", "self", "spell"), ("visual", "self", LIGHTNING), ("wait", 1200),
                 ("emote", "guard_m7", "battle_roar"), ("sound", "guard_m7", "naga_aggro"), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "m7_south"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                   ("emote", "self", "talk"), ("visual", "self", FROST_HAND)],
         poi=["perimeter"]),

    # 5.09: only magic (the night elves come for the summoners; chimaeras break them one by one; the cage opened)
    dict(key="ch5_only_magic", title="Only Magic", giver="serpentra_m7", ender="ch0:vyssa_young", level=31, xp=8,
         tone="serious", prev="ch5_perimeter", memory="m7", kill=[("attacker", 8)],
         goal="In Vyssa's memory, kill 8 Sentinel Raiders as they come down to the lake for the summoners.",
         text="They're coming. Down the slopes, all of them at once. Hold the shore! Blades, tridents, teeth: whatever "
              "you have, put it between them and my summoners. The spell is nearly done. Nearly.",
         progress="Hold!",
         reward="They're breaking. The summoners are breaking. The beasts in the sky only had to breathe on them, and not "
                "one of our tridents could touch the beasts... Lady Serpentra. Where's Lady Serpentra?",
         details=["battle_roar"], reward_emotes=["cry"],
         accept=[("face", "self", "m7_south"), ("emote", "self", "point"), ("sound", "self", "siren_aggro"),
                 ("yell", "self", "They come for the summoners! Hold them! Hold them until the spell is done!", "battle_roar"),
                 ("music", 6077), ("summon", "attacker", "m7_att_1", 240), ("summon", "attacker", "m7_att_2", 240),
                 ("summon", "attacker", "m7_att_3", 240), ("wait", 2500),
                 ("sky", "chimaera", "m7_chim_1", 18, 75), ("sky", "chimaera_2", "m7_chim_2", 18, 75), ("wait", 3500),
                 ("cast", "chimaera", INCINERATE, "sum_s"), ("wait", 1300), ("visual", "sum_s", ARCANE_BURST),
                 ("sound", "sum_s", "siren_death"), ("despawn", "sum_s"), ("wait", 5000),
                 ("summon", "attacker", "m7_att_1", 220), ("summon", "attacker", "m7_att_2", 220),
                 ("summon", "attacker", "m7_att_3", 220), ("wait", 2000),
                 ("cast", "chimaera_2", INCINERATE, "sum_e"), ("wait", 1300), ("visual", "sum_e", ARCANE_BURST),
                 ("sound", "sum_e", "siren_death"), ("despawn", "sum_e"), ("wait", 3000),
                 ("summon", "cage_breaker", "m7_breaker", 40), ("visual", "magroth", HOLY_NOVA), ("state", "magroth", "none"),
                 ("say", "magroth", "Light be praised! To me, Sentinels!", "shout"), ("wait", 2000),
                 ("move", "magroth", "m7_magroth_out", "run"), ("move", "cage_breaker", "m7_magroth_out", "run"),
                 ("wait", 3000), ("cast", "chimaera", INCINERATE, "sum_w"), ("wait", 1300), ("visual", "sum_w", ARCANE_BURST),
                 ("sound", "sum_w", "siren_death"), ("despawn", "sum_w"),
                 ("summon", "attacker", "m7_att_1", 200), ("summon", "attacker", "m7_att_2", 200),
                 ("summon", "attacker", "m7_att_3", 200), ("wait", 6000), ("summon", "attacker", "m7_att_2", 180),
                 ("summon", "attacker", "m7_att_3", 180),
                 ("despawn", "magroth"),
                 ("cast", "chimaera_2", INCINERATE, "sum_n"), ("wait", 1300), ("visual", "sum_n", ARCANE_BURST),
                 ("sound", "sum_n", "siren_death"), ("despawn", "sum_n"), ("wait", 1500),
                 ("yell", "self", "The summoners! No... no!", "battle_roar")],
         complete=[("emote", "self", "cry"), ("wait", 1500), ("face", "self", "m7_serpentra"), ("emote", "self", "question"),
                   ("wait", 1500), ("face", "self", "player")],
         poi=["m7_serpentra"]),

    # 5.10: the Eye breaks (a set piece): Serpentra falls beside you, young Vyssa holds her, white; awake by the pool
    dict(key="ch5_eye_breaks", title="The Eye Breaks", giver="ch0:vyssa_young", ender="ch0:vyssa", level=31, xp=8,
         tone="serious", prev="ch5_only_magic", memory="m7", wake=True, event="The Eye of Sargeras broken",
         choice=["ember_mantle", "guard_leggings", "ruin_girdle"],
         goal="In Vyssa's memory, stay with young Vyssa by Lady Serpentra until the end.",
         text="She's there, by the tower, she's still standing, she's still holding them... Come with me. Please. I don't "
              "want to be the only one who sees.",
         progress="Stay.",
         reward="...",
         details=["cry"], reward_emotes=["talk"],
         accept=[("face", "self", "m7_serpentra"), ("sky", "chimaera", "m7_chim_3", 14, 25), ("wait", 2500),
                 ("cast", "chimaera", INCINERATE, "serpentra_m7"), ("wait", 1300), ("visual", "serpentra_m7", EXPLOSION),
                 ("emote", "serpentra_m7", "wound"), ("sound", "serpentra_m7", "siren_death"), ("wait", 900),
                 ("state", "serpentra_m7", "dead"), ("music", 5174),
                 ("unaura", "self", BUCKET), ("visual", "self", WATER), ("sound", "self", SPLASH_BIG),
                 ("move", "self", "m7_serp_side", "run"), ("wait", 2000), ("face", "self", "m7_serpentra"),
                 ("emote", "self", "cry"), ("state", "self", "kneel"), ("wait", 4000),
                 ("face", "illidan_m7", "m7_serpentra"), ("wait", 2000), ("face", "illidan_m7", "m7_eye"),
                 ("visual", "eye", ARCANE_BURST), ("wait", 1500), ("visual", "eye", ARCANE_BURST), ("aura", "eye", BANISH_WHITE),
                 ("wait", 1500), ("visual", "eye", EXPLOSION), ("sound", "self", 12549), ("aura", "player", "white_burst"),
                 ("visual", "eye", ARCANE_BURST), ("credit", "ch5_eye_breaks"), ("wait", 9000),
                 ("unaura", "eye", BANISH_WHITE), ("state", "serpentra_m7", "none"), ("state", "self", "none"),
                 ("move", "self", "m7_vyssa", "walk")],
         complete=[("state", "self", "none"), ("face", "self", "pool"), ("visual", "self", WATER),
                   ("sound", "self", "pickup_water"), ("wait", 2000), ("emote", "self", "work"), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["m7_serpentra"]),

    # 5.11: after the Eye: Vyssa laughs about something else, and stops; her lady's water-cord
    dict(key="ch5_after", title="After the Eye", giver="ch0:vyssa", ender="ch0:vyssa", level=31, xp=8, tone="serious",
         prev="ch5_eye_breaks", event="Vyssa heard out", rewards=["water_cord"],
         goal="Stay with Vyssa the Coral-Keeper at Isshara's pool while she talks.",
         text="I was her acolyte. I carried her water. That's all an acolyte is, you know: someone who carries the water "
              "and listens very hard. She said magic was only listening very hard. I listened. I listened so hard I "
              "didn't hear the chimaeras until they were over us. Stay a moment. Don't say anything.",
         progress="...",
         reward="This was hers. Her water-cord. I took it off her when... I've worn it under my apron for twenty years and "
                "never once thought about it. Take it. I want it carried by someone who's walking somewhere.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000),
                 ("say", "self", "Do you know, the fish in this bay have no sense at all? One swam into my pot yesterday. "
                                 "Into the pot. While it was boiling.", "talk"),
                 ("sound", "self", ELF_LAUGH), ("wait", 2500), ("sound", "self", ELF_LAUGH), ("wait", 1500),
                 ("face", "self", "pool"), ("wait", 4000), ("visual", "self", WATER), ("sound", "self", "pickup_water"),
                 ("wait", 3000), ("face", "ch0:isshara", "vyssa_pool"), ("visual", "ch0:isshara", WATER), ("wait", 2000),
                 ("credit", "ch5_after")],
         complete=[("face", "self", "player"), ("emote", "self", "work"), ("wait", 2000), ("move", "self", "vyssa_home", "walk"),
                   ("wait", 14500), ("state", "self", "work")],
         poi=["vyssa_pool"]),

    # 5.12: the blank-eyed scout (a set piece): she comes back from the bay with nothing in her
    dict(key="ch5_scout", title="The Blank-Eyed Scout", giver="ch0:szaria", ender="ch0:isshara", level=31, xp=8,
         tone="serious", prev="ch5_after", event="The scout come home",
         goal="Be at the Hollow when Scout Neshra comes back out of the bay, and go with her to Isshara.",
         text="Neshra went out three tides ago to watch the rocks west of here. The Spitelash have been coming and going "
              "there by night with something that sings. She's overdue. ...No. There. In the water. She's swimming like "
              "she's never swum before. Come down to the beach with me.",
         progress="Bring her to the keeper.",
         reward="Neshra. Neshra, child... There's nothing there. I put my hand on her face and there's nothing behind it, "
                "not even fear. Unsung. Somebody has sung her out of herself and left the shell on our beach.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "sea_south"), ("emote", "self", "talk"), ("summon", "scout_blank", "scout_rise", 120),
                 ("wait", 800), ("sound", "self", "splash"), ("move", "scout_blank", "scout_beach", "walk"), ("wait", 6500),
                 ("move", "scout_blank", "scout_camp", "walk"), ("move", "self", "banner_front", "walk"), ("wait", 8500),
                 ("face", "scout_blank", "szaria"), ("face", "self", "scout_camp"),
                 ("say", "self", "Neshra. Report.", "talk"), ("wait", 3000), ("face", "scout_blank", "vyssa_home"),
                 ("wait", 2500), ("face", "scout_blank", "ssaveth_home"), ("wait", 2500), ("face", "scout_blank", "player"),
                 ("wait", 2000), ("say", "scout_blank", "...Who is Neshra?", "question"), ("wait", 2500),
                 ("emote", "ch0:ssaveth", "stun"), ("emote", "self", "battle_roar"), ("wait", 2000),
                 ("move", "scout_blank", "scout_pool", "walk"), ("wait", 18000), ("face", "scout_blank", "isshara"),
                 ("face", "ch0:isshara", "scout_pool"), ("emote", "ch0:isshara", "spell"), ("wait", 2000),
                 ("yell", "ch0:isshara", "Unsung.", "battle_roar", "siren_aggro"), ("credit", "ch5_scout"), ("wait", 3000),
                 ("move", "self", "ch1:hollow_szaria", "walk"), ("state", "scout_blank", "drowned")],
         complete=[("face", "self", "player"), ("visual", "self", WATER), ("sound", "self", "pickup_water"), ("wait", 2000),
                   ("face", "self", "ring"), ("emote", "self", "omnicast"), ("wait", 1500), ("face", "self", "player")],
         poi=["scout_beach", "isshara"]),

    # 5.13: the Unsingers' circle: on the sea stack's north shelf, four sirens in a ring round a bound renegade
    dict(key="ch5_circle", title="The Unsingers' Circle", giver="ch0:isshara", ender="ch0:isshara", level=31, xp=8,
         tone="serious", prev="ch5_scout", explore="ring", radius=24,
         goal="Find where Scout Neshra was taken: swim west to the shelf at the foot of the sea stack's north face, see "
              "what sings there, and come back to Isshara.",
         text="Listen. No, with your skin, not your ears. West, on the big rock in the bay. Four of them, singing in a "
              "ring. I know that song. I sang its opposite all my life. Go and look. Only look. Whatever you see there, "
              "it can't see you yet.",
         progress="Is it a ring? Tell me it isn't a ring.",
         reward="A ring. Four of them, round a bound one, and a pearl growing over his head as his eyes go out. ...That "
                "is what the summoners looked like round the Eye, at Dalaran. Vyssa saw it tonight with you. The same "
                "ring. The same fools who think a circle is a wall.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "ring"), ("state", "self", "channel"), ("sound", "self", "siren_hiss"), ("wait", 3000),
                 ("summon", "unsinger_warded", "ring_1", 720), ("summon", "unsinger_warded", "ring_2", 720),
                 ("summon", "unsinger_warded", "ring_3", 720), ("summon", "unsinger_warded", "ring_4", 720),
                 ("summon", "ring_prisoner", "ring", 720), ("sky", "forming_pearl", "ring", 2, 720),
                 ("state", "self", "none"), ("emote", "self", "stun"),
                 ("wait", 1500), ("visual", "self", WATER), ("sound", "self", "pickup_water"), ("face", "self", "player"),
                 ("emote", "self", "talk")],
         complete=[("face", "self", "ring"), ("emote", "self", "battle_roar"), ("wait", 1500), ("visual", "self", WATER),
                   ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["ring"]),

    # 5.14 (two versions, by chapter 4's road): only magic, again: the ward broken with what the player carries
    dict(key="ch5_magic_arrows", title="Only Magic, Again", giver="ch0:isshara", ender="ch0:isshara", level=32, xp=8,
         tone="serious", prev=["ch5_circle", "ch4:ch4_keeper"], source="ch4:moonstone_arrows",
         use=[("ch4:moonstone_arrows", "forming_pearl", 1,
               [("give", "ch4:moonstone_arrows", 1), ("visual", "self", ARCANE_BURST), ("sound", "player", CRACK),
                ("visual", "unsinger_warded", ARCANE_BURST), ("despawn", "unsinger_warded"), ("summon", "unsinger", "ring_1", 400),
                ("wait", 700), ("sound", "player", CRACK), ("visual", "unsinger_warded", ARCANE_BURST),
                ("despawn", "unsinger_warded"), ("summon", "unsinger", "ring_2", 400), ("wait", 700),
                ("sound", "player", CRACK), ("visual", "unsinger_warded", ARCANE_BURST), ("despawn", "unsinger_warded"),
                ("summon", "unsinger", "ring_3", 400), ("wait", 700), ("sound", "player", CRACK),
                ("visual", "unsinger_warded", ARCANE_BURST), ("despawn", "unsinger_warded"),
                ("summon", "unsinger", "ring_4", 400), ("wait", 700), ("despawn", "unsinger_warded"), ("wait", 700),
                ("despawn", "unsinger_warded"), ("wait", 700), ("despawn", "unsinger_warded"), ("wait", 700),
                ("despawn", "unsinger_warded"), ("give", "unsung_pearl", 1), ("sound", "player", GEMS),
                ("unaura", "ring_prisoner", 68341), ("state", "ring_prisoner", "none"),
                ("move", "ring_prisoner", "ring_free", "run"), ("wait", 2500), ("despawn", "ring_prisoner"), ("wait", 700),
                ("despawn", "ring_prisoner"), ("wait", 10000), ("summon", "unsinger", "unsinger_rise_1", 300),
                ("summon", "unsinger", "unsinger_rise_2", 300), ("despawn", "forming_pearl"), ("wait", 700), ("despawn", "self")])],
         kill=[("unsinger", 4)], choice=["ward_trident", "unsinger_bane", "keeper_staff"],
         goal="Loose one of Shaelyn's Moonstone Arrows into the pearl forming in the Unsingers' ring on the sea stack's "
              "north shelf, and kill 4 Unsingers when the ward breaks.",
         text="Steel won't touch them. Their ring is a ward, and a ward is a song, and a song turns a blade the way the "
              "sea turns a stone. It took magic at Dalaran; it takes magic now. You carry some. The girl's arrows: "
              "moonstone, Elune's own light, and she gave them to you for a naga's heart. Give the ring one. And catch "
              "what falls.",
         progress="Is the ring broken?",
         reward="The pearl... give it here a moment. Two songs in it, twisted together. His, and Neshra's. They were "
                "singing her out of herself into it when you broke them. The Empress's people have learned a new trick, "
                "little one. Good. So have we.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "ring"),
                 ("emote", "self", "omnicast"), ("sound", "self", "siren_hiss"),
                 ("summon", "unsinger_warded", "ring_1", 1800), ("summon", "unsinger_warded", "ring_2", 1800),
                 ("summon", "unsinger_warded", "ring_3", 1800), ("summon", "unsinger_warded", "ring_4", 1800),
                 ("summon", "ring_prisoner", "ring", 1800), ("sky", "forming_pearl", "ring", 2, 1800), ("wait", 2000),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("emote", "self", "spell"), ("visual", "self", WATER), ("wait", 2000),
                   ("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro")],
         poi=["ring"]),
    dict(key="ch5_magic_glaive", title="Only Magic, Again", giver="ch0:isshara", ender="ch0:isshara", level=32, xp=8,
         tone="serious", prev=["ch5_circle", "ch4:ch4_glaive"], source="ch4:glaive",
         use=[("ch4:glaive", "forming_pearl", 1,
               [("give", "ch4:glaive", 1), ("visual", "self", ARCANE_BURST), ("sound", "player", CRACK),
                ("visual", "unsinger_warded", ARCANE_BURST), ("despawn", "unsinger_warded"), ("summon", "unsinger", "ring_1", 400),
                ("wait", 700), ("sound", "player", CRACK), ("visual", "unsinger_warded", ARCANE_BURST),
                ("despawn", "unsinger_warded"), ("summon", "unsinger", "ring_2", 400), ("wait", 700),
                ("sound", "player", CRACK), ("visual", "unsinger_warded", ARCANE_BURST), ("despawn", "unsinger_warded"),
                ("summon", "unsinger", "ring_3", 400), ("wait", 700), ("sound", "player", CRACK),
                ("visual", "unsinger_warded", ARCANE_BURST), ("despawn", "unsinger_warded"),
                ("summon", "unsinger", "ring_4", 400), ("wait", 700), ("despawn", "unsinger_warded"), ("wait", 700),
                ("despawn", "unsinger_warded"), ("wait", 700), ("despawn", "unsinger_warded"), ("wait", 700),
                ("despawn", "unsinger_warded"), ("give", "unsung_pearl", 1), ("sound", "player", GEMS),
                ("unaura", "ring_prisoner", 68341), ("state", "ring_prisoner", "none"),
                ("move", "ring_prisoner", "ring_free", "run"), ("wait", 2500), ("despawn", "ring_prisoner"), ("wait", 700),
                ("despawn", "ring_prisoner"), ("wait", 10000), ("summon", "unsinger", "unsinger_rise_1", 300),
                ("summon", "unsinger", "unsinger_rise_2", 300), ("despawn", "forming_pearl"), ("wait", 700), ("despawn", "self")])],
         kill=[("unsinger", 4)], choice=["ward_trident", "unsinger_bane", "keeper_staff"],
         goal="Strike the pearl forming in the Unsingers' ring on the sea stack's north shelf with the Broken Watcher's "
              "Glaive, and kill 4 Unsingers when the ward breaks.",
         text="Steel won't touch them. Their ring is a ward, and a ward is a song, and a song turns a blade the way the "
              "sea turns a stone. It took magic at Dalaran; it takes magic now. You carry a warden's glaive. A warden's "
              "blade remembers what it was made to cut, and it was made to cut us. Let it remember. And catch what falls.",
         progress="Is the ring broken?",
         reward="The pearl... give it here a moment. Two songs in it, twisted together. His, and Neshra's. They were "
                "singing her out of herself into it when you broke them. ...You cut them with Maiev's steel. I won't ask "
                "how it felt. It felt like something, I hope.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "ring"),
                 ("emote", "self", "omnicast"), ("sound", "self", "siren_hiss"),
                 ("summon", "unsinger_warded", "ring_1", 1800), ("summon", "unsinger_warded", "ring_2", 1800),
                 ("summon", "unsinger_warded", "ring_3", 1800), ("summon", "unsinger_warded", "ring_4", 1800),
                 ("summon", "ring_prisoner", "ring", 1800), ("sky", "forming_pearl", "ring", 2, 1800), ("wait", 2000),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("emote", "self", "spell"), ("visual", "self", WATER), ("wait", 2000),
                   ("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro")],
         poi=["ring"]),

    # 5.15: giving back (the scout and Ossk by the pool, blank; the pearl given back)
    dict(key="ch5_giving_back", title="Giving Back", giver="ch0:isshara", ender="ch0:isshara", level=32, xp=8,
         tone="serious", prev_any=["ch5_magic_arrows", "ch5_magic_glaive"], source="unsung_pearl",
         use=[("unsung_pearl", "scout_home", 1,
               [("visual", "self", BIND), ("unaura", "self", GLOW_BLACK), ("state", "self", "none"), ("wait", 1500),
                ("visual", "prisoner_home", BIND), ("unaura", "prisoner_home", GLOW_BLACK), ("state", "prisoner_home", "none"),
                ("wait", 1500), ("face", "self", "szaria"), ("wait", 1500), ("emote", "self", "roar"),
                ("sound", "self", "siren_aggro"), ("emote", "prisoner_home", "battle_roar"), ("wait", 2000),
                ("emote", "self", "laugh"), ("sound", "self", ELF_LAUGH), ("wait", 2500), ("emote", "self", "laugh"),
                ("sound", "self", ELF_LAUGH), ("wait", 2500), ("emote", "self", "cry"), ("wait", 3000),
                ("emote", "ch0:szaria", "battle_roar"), ("sound", "ch0:szaria", "siren_aggro"), ("state", "self", "sit")])],
         rewards=["neshra_ring"],
         goal="Give the Unfinished Song-Pearl back to Scout Neshra, sitting by Isshara's pool.",
         text="Memories can go back where they came from. Nobody told the Empress's people that, because nobody asked them. "
              "Neshra is sitting by the water with Ossk; we brought him in off the rock. Give her the pearl. Hold it to "
              "her, the way you'd hold a shell to a hatchling's ear. The song knows its way home.",
         progress="Give it to her.",
         reward="Do you hear that? She's laughing. She's laughing and she can't stop, and now she's crying, and she knows "
                "why she's crying. That's what a person is, little one: knowing why. Here. She wants you to have this, "
                "and she wants you to know she remembers buying it.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("summon", "scout_home", "prisoner_pool", 1200), ("summon", "prisoner_home", "scout_rest", 1200),
                 ("face", "self", "prisoner_pool"), ("emote", "self", "spell"), ("visual", "self", WATER), ("wait", 2000),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "prisoner_pool"), ("sound", "self", ELF_LAUGH), ("wait", 2000), ("visual", "self", WATER),
                   ("sound", "self", "pickup_water"), ("emote", "self", "omnicast")],
         poi=["prisoner_pool"]),

    # 5.16: lessons at thirty (each class at its trainer)
    dict(key="ch5_lesson_warrior", title="Lessons at Thirty", giver="ch0:kessh", ender="ch0:kessh", level=31, xp=8,
         tone="funny", classes=["warrior"], prev="ch5_after", learn=[2458], rewards=["kessh_band"],
         emotes=[("spar_ssaveth", "salute", 1, [("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"),
                                                 ("wait", 2000), ("move", "self", "ssaveth_home", "walk")])],
         goal="Spar with Myrmidon Ssaveth on the drill sand until he yields, then salute him.",
         text="Defensive stance keeps you alive. Battle stance keeps you honest. The third keeps nothing: it's for when "
              "you've decided to stop keeping things. Ssaveth will teach you that one. He likes it far too much. Down "
              "on the sand. Fight him until he says enough, then salute him like a soldier.",
         progress="He hasn't said enough. He never says enough first.",
         reward="You heard him laugh? He laughs when somebody hits him properly. Twice a year, maybe. That's the stance: "
                "the fight first, everything else after. Take it. Take this too.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("face", "self", "ssaveth_home"), ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"),
                 ("face", "ch0:ssaveth", "duel"), ("emote", "ch0:ssaveth", "roar"), ("move", "ch0:ssaveth", "duel", "walk"),
                 ("wait", 13000), ("despawn", "ch0:ssaveth"), ("summon", "spar_ssaveth", "duel", 115),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "battle_roar"), ("wait", 1500), ("emote", "self", "talk")],
         poi=["duel"]),
    dict(key="ch5_lesson_hunter", title="Lessons at Thirty", giver="ch0:thessk", ender="ch0:thessk", level=31, xp=8,
         tone="serious", classes=["hunter"], prev="ch5_after", objects=[("guard_tracks", 3)], rewards=["snaptamer_quiver"],
         goal="Read 3 sets of Coral-Guard tracks on the sea stack's west beach.",
         text="A beast leaves tracks; so does a naga. The Coral-Guards on the big rock think the tide wipes theirs out. It "
              "doesn't, not on that beach. Three sets. Read where they turn, where they stop, where they stand and argue. "
              "A patrol is a habit with a trident.",
         progress="Three sets. Where do they stop?",
         reward="They stop by the dry rocks every time, because their sergeant has a bad tail. Now you know where they'll "
                "be before they do. That's the whole craft.",
         details=["point"], reward_emotes=["laugh"],
         accept=[("face", "self", "stack"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk")],
         complete=[("emote", "self", "laugh"), ("wait", 1500), ("emote", "self", "point")],
         poi=["track_2"]),
    dict(key="ch5_lesson_rogue", title="Lessons at Thirty", giver="ch0:shivra", ender="ch0:shivra", level=31, xp=8,
         tone="funny", classes=["rogue"], prev="ch5_after", objects=[("curio_box", 1)], rewards=["quickfin_pick"],
         goal="Pick the lock on Jediga's curio box at Valormok, and lock it again, without taking anything.",
         text="Anybody can open a box. Opening it and leaving it exactly as it was, so the owner never knows: that's a "
              "lesson. The orc woman at Valormok, the one who sold us our own pearls, keeps a curio box on her table. "
              "Open it. Look. Close it. Take nothing. If you take something I'll know, and so will she.",
         progress="Did you take anything? Show me your hands. All of them.",
         reward="Her runner scratched his head? Good. He'll scratch it for a week and never know why. That's a clean job.",
         details=["shy"], reward_emotes=["shy"],
         accept=[("face", "self", "toward_valormok"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "shy")],
         complete=[("emote", "self", "laugh"), ("wait", 1200), ("emote", "self", "shy")],
         poi=["curio"]),
    dict(key="ch5_lesson_mage", title="Lessons at Thirty", giver="ch0:lyrenne", ender="ch0:lyrenne", level=31, xp=8,
         tone="funny", classes=["mage"], prev="ch5_after", objects=[("signal_wood", 1)], rewards=["lyrenne_ember"],
         goal="Light the signal fire on Ssaveth's dune at the Hollow.",
         text="Anyone can throw fire. Putting it exactly where you meant, at the size you meant, while somebody shouts at "
              "you: that's a mage. Ssaveth wants the signal fire on his dune lit. With a spell. Not a tinderbox, not a "
              "torch, and not, please, my sister's cooking.",
         progress="It's still dark up there.",
         reward="Lit, and nobody's eyebrows went with it. Ssaveth roared at it. He roars at everything, but that was a "
                "pleased roar. Keep this; it's warm.",
         details=["spell"], reward_emotes=["spell"],
         accept=[("face", "self", "signal_fire"), ("emote", "self", "spell"), ("visual", "self", FROST_HAND), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "spell"), ("visual", "self", FROST_HAND), ("wait", 1500), ("emote", "self", "talk")],
         poi=["signal_fire"]),
    dict(key="ch5_lesson_priest", title="Lessons at Thirty", giver="ch0:thessa_trainer", ender="ch0:thessa_trainer",
         level=32, xp=8, tone="serious", classes=["priest"], prev="ch5_giving_back", rewards=["thessa_shell"],
         emotes=[("scout_ache", "soothe", 1, [("emote", "self", "yes"), ("sound", "self", ELF_SIGH), ("wait", 2500),
                                              ("state", "self", "sleep")])],
         goal="Soothe Scout Neshra, sitting by the pool with her memories all come back at once.",
         text="Neshra's memories came home all at once, every tide of the war in one breath, and her head won't stop "
              "ringing. A healer doesn't always heal. Sometimes she sits down beside someone and makes the world quieter. "
              "Go and sit with her. Be quiet with her. Soothe her.",
         progress="Quietly.",
         reward="She's asleep. The first time since she came back. You didn't cast anything, did you? Good. You don't "
                "always have to.",
         details=["talk"], reward_emotes=["omnicast"],
         accept=[("summon", "scout_ache", "scout_ache", 600), ("face", "self", "scout_ache"), ("emote", "self", "omnicast"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", HOLY_NOVA), ("wait", 1500), ("emote", "self", "talk")],
         poi=["scout_ache"]),
    dict(key="ch5_lesson_shaman", title="Lessons at Thirty", giver="ch0:oshra", ender="ch0:oshra", level=31, xp=8,
         tone="serious", classes=["shaman"], prev="ch5_after", objects=[("wind_stone", 1)], rewards=[5178],
         goal="Climb the high rock off the north strand, across the water north of the Hollow, and put your hand on the "
              "wind-worn stone at its top.",
         text="Earth, fire and water you have. Air is last because air is the hardest to hold: it never stays. On the high "
              "rock off the north strand, over the water above the Hollow, there's a stone the wind has been worrying at "
              "since the Well went down. Put your hand on it. Let the wind find you.",
         progress="The air still doesn't know you.",
         reward="Your scales are standing up. That's the wind's handshake. Now it's yours, carved in a totem. Plant it, "
                "and the air comes when you call.",
         details=["omnicast"], reward_emotes=["omnicast"],
         accept=[("face", "self", "wind_stone"), ("emote", "self", "omnicast"), ("visual", "self", LIGHTNING), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", LIGHTNING_NOVA), ("wait", 1500), ("emote", "self", "talk")],
         poi=["wind_stone"]),
    dict(key="ch5_lesson_warlock", title="Lessons at Thirty", giver="ch0:nazreth", ender="ch0:nazreth", level=31, xp=8,
         tone="serious", classes=["warlock"], prev="ch5_after", learn=[691], kill=[("wild_felhunter", 1)],
         rewards=["nazreth_charm"],
         goal="Break the Starving Felhunter feeding on the Unsingers' leavings on the sea stack's west beach, so it can "
              "be bound.",
         text="Demons, for instance. Somebody said that once, to a prince who was hungry. A felhunter came through some "
              "crack in the world and smelled the Unsingers' magic on the rock in the bay, and it's been licking the "
              "stones there ever since. Break it. A felhunter eats magic. Imagine what it'll do to theirs.",
         progress="Is it still feeding?",
         reward="It knows your scent now, and it hates it, which is the right way round. Call it and it comes, and it "
                "eats the spells out of the air. Don't let it eat yours.",
         details=["spell"], reward_emotes=["spell"],
         accept=[("summon", "wild_felhunter", "felhunter", 900), ("face", "self", "stack"), ("visual", "self", 43167),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "spell"), ("visual", "self", 43167), ("wait", 1500), ("emote", "self", "talk")],
         poi=["felhunter"]),

    # 5.17: Ssaveth's river song (into m8): "You found a priestess once." He groans and sits down in the water
    dict(key="ch5_river_song", title="Ssaveth's River Song", giver="ch0:isshara", ender="ch0:ssaveth_young", level=32,
         xp=8, tone="funny", prev="ch5_giving_back", memory="m8", explore="m8_ssaveth", radius=9,
         goal="Touch the water while Isshara sings Ssaveth's pearl. In the memory, find young Ssaveth at Illidan's camp "
              "above the river.",
         text="The second pearl is Ssaveth's too. That's two of his I've sung now, and he hasn't sat through either of "
              "them with his eyes open. This one he'll like. Or he'll hate it, which with Ssaveth is the same face. Ssaveth! "
              "You found a priestess once. Come and hear yourself do it.",
         progress="Find him. He'll be the one out of breath.",
         reward="You're the new one? You swim like a hatchling. Lord Illidan's priestess is somewhere on this river, and "
                "the dead are on it too, and I've been up and down it twice already. Keep up.",
         details=["laugh"], reward_emotes=["roar"],
         accept=[("face", "self", "ssaveth_home"), ("sound", "self", ELF_LAUGH),
                 ("say", "self", "You found a priestess once.", "talk"), ("wait", 2500),
                 ("emote", "ch0:ssaveth", "wound"), ("sound", "ch0:ssaveth", "naga_wound"), ("state", "ch0:ssaveth", "none"),
                 ("wait", 1500), ("move", "ch0:ssaveth", "ssaveth_water", "walk"), ("wait", 21000),
                 ("face", "ch0:ssaveth", "sea_east"), ("state", "ch0:ssaveth", "drowned"), ("sound", "ch0:ssaveth", "splash"),
                 ("wait", 1500), ("face", "self", "pool"), ("state", "self", "channel"), ("sound", "self", "siren_hiss"),
                 ("music", 9461), ("visual", "player", WATER), ("wait", 3000), ("relive", "m8"), ("wait", 2000),
                 ("state", "self", "none")],
         complete=[("emote", "self", "roar"), ("wait", 1500), ("face", "self", "m8_river"), ("emote", "self", "point"),
                   ("wait", 1500), ("face", "self", "player")],
         poi=["m8_ssaveth"]),

    # 5.18: we have found your priestess (Tyrande on the bank below; back to Illidan with the news)
    dict(key="ch5_priestess", title="We Have Found Your Priestess", giver="ch0:ssaveth_young", ender="ch0:ssaveth_young",
         level=32, xp=8, tone="serious", prev="ch5_river_song", memory="m8", explore="m8_overlook", radius=14,
         goal="In Ssaveth's memory, go down the shelf to where you can see the river's bank below, find the priestess, "
              "and come back to young Ssaveth.",
         text="Lord Illidan's priestess. The night elves' high priestess, the one with the moon on her. She went into the "
              "river at the bridge and the river took her down here, and the dead followed. Go down the shelf and look "
              "along the bank. Then come back and we tell him together. I want to see his face.",
         progress="Did you see her? Is she alive?",
         reward="Alive. Fighting. Then we tell him.",
         details=["point"], reward_emotes=["roar"],
         accept=[("face", "self", "m8_river"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk")],
         complete=[("face", "self", "m8_illidan"), ("move", "self", "m8_naga_1", "walk"), ("wait", 11500),
                   ("say", "self", "Lord Illidan, we have found your missing priestess. She and her warriors fight on against "
                                   "the undead, but I doubt they can hold out much longer.", "talk"),
                   ("face", "illidan_m8", "m8_naga_1"), ("wait", 6000), ("face", "illidan_m8", "m8_river"),
                   ("visual", "illidan_m8", FEL_SMOKE), ("wait", 1500),
                   ("say", "self", "You'd best hurry if you're to save her!", "talk"), ("wait", 2500),
                   ("move", "self", "m8_ssaveth", "walk")],
         poi=["m8_overlook"]),

    # 5.19: the undead shore (Tyrande holding on the bank)
    dict(key="ch5_undead", title="The Undead Shore", giver="ch0:ssaveth_young", ender="ch0:ssaveth_young", level=32,
         xp=8, tone="serious", prev="ch5_priestess", memory="m8", kill=[("ghoul", 8), ("skeleton", 4)],
         goal="In Ssaveth's memory, kill 8 Ghouls and 4 Skeletal Warriors on the shelf and the slope down to the river.",
         text="He says hold them off her until he can get there. He didn't say please. He never says please; he says "
              "it like the water says it. The dead are on the shelf and all down the slope. Thin them.",
         progress="She can't hold much longer. Nobody could.",
         reward="She's still standing. I don't know what night elves are made of. Something that doesn't drown.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 1500),
                 ("face", "tyrande_m8", "u_4"),
                 ("yell", "tyrande_m8", "Keep fighting, my warriors! They may be our end, but they will never defeat our "
                                        "spirit!", "shout"),
                 ("visual", "tyrande_m8", HOLY_NOVA), ("emote", "sentinel_m8", "attack"), ("wait", 2000),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "m8_tyrande"), ("emote", "self", "roar"), ("wait", 1500), ("face", "self", "player"),
                   ("emote", "self", "talk")],
         poi=["undead_shore"]),

    # 5.20: the dam (the trolls' tributary; their chieftain; the dam breaks with a roar of water)
    dict(key="ch5_dam", title="The Dam", giver="ch0:ssaveth_young", ender="ch0:ssaveth_young", level=32, xp=8,
         tone="serious", prev="ch5_undead", memory="m8", kill=[("troll", 10), ("troll_chief", 1)], objects=[("dam", 1)],
         goal="In Ssaveth's memory, swim up the river to the trolls' dam, kill 10 Forest Trolls and their Chieftain, and "
              "break the dam.",
         text="Up the river, round the bend, the trolls have dammed it with bones and logs. Their water, they say. Lord "
              "Illidan says the stream behind the dam runs straight to her. We break it and we ride the water down. Kill "
              "the trolls. Kill the big one. Then break their dam.",
         progress="The dam?",
         reward="Hear that? That's the river remembering where it was going. Now we go with it.",
         details=["point"], reward_emotes=["battle_roar"],
         accept=[("face", "self", "m8_illidan"),
                 ("say", "self", "Lord Illidan, we've discovered a dam blocking one of the river's tributaries. The dam is "
                                 "guarded by forest trolls, but the stream beyond it might provide us a faster route to "
                                 "your friend.", "talk"),
                 ("wait", 5500), ("face", "illidan_m8", "dam"), ("visual", "illidan_m8", FEL_SMOKE), ("wait", 1500),
                 ("face", "self", "dam"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 1500), ("face", "self", "m8_river"),
                   ("emote", "self", "point")],
         poi=["dam"]),

    # 5.21: brothers (a set piece): Illidan goes down to her; Malfurion is there; a portal; the fade
    dict(key="ch5_brothers", title="Brothers", giver="ch0:ssaveth_young", ender="ch0:ssaveth", level=32, xp=8,
         tone="serious", prev="ch5_dam", memory="m8", wake=True, event="Illidan gone through his portal",
         choice=["arevass_robe", "arevass_jerkin", "arevass_hauberk"],
         goal="In Ssaveth's memory, stand with young Ssaveth at the shelf's edge and watch Illidan go down to the "
              "priestess.",
         text="The water's through. He's going. Stand with me. I want somebody to see this who isn't me, because nobody "
              "is going to believe me afterwards.",
         progress="Watch.",
         reward="...I sat down in the water. I sat down in the water in front of the whole camp. Don't. Don't say it.",
         details=["point"], reward_emotes=["talk"],
         accept=[("face", "self", "m8_tyrande"), ("emote", "self", "point"), ("music", 3900),
                 ("summon", "fodder", "m8_cut_1", 30), ("summon", "fodder_2", "m8_cut_2", 30), ("wait", 1500),
                 ("face", "illidan_m8", "m8_ill_land"), ("visual", "illidan_m8", FEL_SMOKE), ("wait", 1000),
                 ("jump", "illidan_m8", "m8_ill_land"), ("wait", 2500), ("emote", "illidan_m8", "attack"),
                 ("state", "fodder", "dead"), ("wait", 900), ("emote", "illidan_m8", "attack"), ("state", "fodder_2", "dead"),
                 ("wait", 1500), ("summon", "malfurion_m8", "m8_malf", 40), ("visual", "malfurion_m8", NATURE_PORTAL),
                 ("wait", 1500), ("face", "tyrande_m8", "m8_ill_land"), ("state", "tyrande_m8", "none"),
                 ("say", "tyrande_m8", "By Elune.", "talk", "TyrandeYes2"), ("wait", 2500),
                 ("unaura", "malfurion_m8", NATURE_PORTAL), ("face", "malfurion_m8", "m8_ill_land"),
                 ("face", "illidan_m8", "m8_malf"), ("wait", 4000), ("move", "illidan_m8", "m8_illidan_step", "walk"),
                 ("wait", 2000), ("face", "illidan_m8", "m8_river"), ("face", "malfurion_m8", "m8_river"), ("wait", 5000),
                 ("face", "illidan_m8", "m8_tyrande"), ("visual", "illidan_m8", TELEPORT), ("aura", "illidan_m8", FEL_PORTAL),
                 ("say", "illidan_m8", "By aiding you, I have betrayed my new master.", "talk"), ("wait", 4500),
                 ("emote", "malfurion_m8", "talk"), ("wait", 2000), ("visual", "illidan_m8", TELEPORT),
                 ("despawn", "illidan_m8"), ("wait", 2000), ("emote", "self", "stun"), ("credit", "ch5_brothers"),
                 ("wait", 6000), ("despawn", "malfurion_m8"), ("state", "tyrande_m8", "ready_bow")],
         complete=[("state", "self", "none"), ("face", "self", "sea_south"), ("emote", "self", "roar"),
                   ("sound", "self", "naga_aggro"), ("wait", 2500), ("face", "self", "player"), ("emote", "self", "talk"),
                   ("say", "ch0:szaria", "Ag'tor's runner came while you were under. Spitelash on his west road. Go and "
                                         "stand with him.", "talk"),
                   ("wait", 2000), ("move", "self", "ssaveth_home", "walk"), ("wait", 21000), ("state", "self", "ready_thrown")],
         poi=["m8_tyrande"]),

    # 5.22 (two versions, by chapter 1's road): our enemies are the same: the west road, with Ag'tor's grunts
    dict(key="ch5_war_party", title="Our Enemies Are the Same", giver=AGTOR, ender=AGTOR, level=33, xp=8,
         tone="serious", path="hero", prev=["ch5_brothers", "ch1:ch1_rival_a"], rep=[(76, 500)],
         choice=["war_axe", "back_blade", "grunt_staff"],
         interact=[("bguard", "The Tide-Broken are with you. Sound the horn.")], interact_goal="The horn sounded",
         interact_beats=[
             ("face", "self", "player"), ("emote", "self", "roar"), ("sound", "self", GRUNT_HORN), ("wait", 800),
             ("yell", "self", "Valormok! The fish-people stand with us! DOWN THE ROAD!", "shout"),
             ("summon", "road_grunt", "line_l", 360), ("summon", "road_grunt", "line", 360),
             ("summon", "road_myr", "line_r", 360), ("summon", "road_myr", "myr_1", 360),
             ("summon", "szaria_road", "szaria_road", 600), ("summon", "back_grunt", "back_1", 360),
             ("summon", "back_myr", "back_2", 360), ("wait", 1200),
             ("face", "back_grunt", "back_e1"), ("face", "back_myr", "back_e2"), ("state", "back_grunt", "ready"),
             ("state", "back_myr", "ready_thrown"),
             ("yell", "szaria_road", "Tide-Broken! With the orcs! Era'sazjar!", "battle_roar"),
             ("sound", "szaria_road", "siren_aggro"), ("wait", 1500),
             ("summon", "war_party", "wp_1", 330), ("summon", "war_party", "wp_2", 330), ("summon", "war_party", "wp_3", 330),
             ("summon", "war_witch", "wp_4", 330), ("sound", "self", HORN), ("wait", 15000),
             ("summon", "war_party", "wp_1", 300), ("summon", "war_party", "wp_2", 300), ("summon", "war_party", "wp_3", 300),
             ("summon", "war_party", "wp_4", 300), ("emote", "back_grunt", "attack"), ("emote", "back_myr", "attack2h"),
             ("wait", 1500), ("emote", "back_grunt", "attack"), ("emote", "back_myr", "attack2h"), ("wait", 14000),
             ("summon", "ssethis_officer", "ssethis_back", 120), ("summon", "war_party", "wp_1", 280),
             ("summon", "war_party", "wp_3", 280), ("summon", "war_party", "wp_4", 280), ("summon", "war_witch", "wp_2", 280),
             ("emote", "ssethis_officer", "battle_roar"), ("sound", "ssethis_officer", "naga_aggro"),
             ("yell", "ssethis_officer", "Hold! Hold the road, for the Empress!", "battle_roar"), ("wait", 15000),
             ("summon", "war_party", "wp_1", 260), ("summon", "war_party", "wp_2", 260), ("summon", "war_party", "wp_3", 260),
             ("summon", "war_party", "wp_4", 260), ("emote", "back_grunt", "attack"), ("emote", "back_myr", "attack2h"),
             ("wait", 8000),
             # (1.20a: he kept the heretic's secret once; now he lays down his trident)
             ("face", "ssethis_officer", "player"), ("wait", 3000), ("emote", "ssethis_officer", "roar"), ("wait", 2000),
             ("emote", "ssethis_officer", "throw"), ("object", "dropped_trident_obj", "ssethis_down", 90),
             ("state", "ssethis_officer", "none"), ("move", "ssethis_officer", "ssethis_down", "walk"), ("wait", 4000),
             ("state", "ssethis_officer", "stun"), ("move", "road_myr", "ssethis_down", "walk"), ("wait", 4000),
             ("move", "ssethis_officer", "dragged", "walk"), ("move", "road_myr", "dragged", "walk"), ("wait", 9000),
             ("despawn", "ssethis_officer")],
         emotes=[("szaria_road", "roar", 1,
                  [("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro"), ("emote", "road_grunt", "roar"),
                   ("emote", "back_grunt", "roar"), ("sound", "back_grunt", CHEER_HORDE), ("emote", "road_myr", "battle_roar"),
                   ("emote", "back_myr", "battle_roar"), ("wait", 2500), ("move", "self", "agtor_front", "run"),
                   ("wait", 17500), ("face", "self", "agtor"), ("emote", "self", "spell"), ("visual", "self", WATER),
                   ("wait", 4000), ("emote", "self", "battle_roar")])],
         goal="Tell Blood Guard Grozak at the head of Valormok's west road to sound the horn, kill 12 Spitelash "
              "Warmongers with the grunts and the Tide-Broken, then /roar at Lady Szaria and return to Ag'tor.",
         text="Your people and my people, both on my west road, both bleeding for it. A Spitelash war party is coming "
              "up from the river, and this time they have an officer who shouts. Good. Grozak has the horn at the "
              "road's head. Tell him. My grunts go down with you. Your lady says hers will be there. We will see.",
         progress="The road?",
         reward="She came up the road wet to the elbows and held out her hand to me. Cold. Wet. A grip like a shark. I "
                "took it. ...Don't look at me like that, snake. The Horde shakes on things. Take your pick of the "
                "armoury. You earned it on the road, with my grunts watching.",
         details=["talk", "point"], reward_emotes=["salute", "talk", "roar"],
         poi=["bguard", "west_road"]),
    dict(key="ch5_war_party_b", title="Our Enemies Are the Same", giver=AGTOR, ender=AGTOR, level=33, xp=8,
         tone="serious", path="hero", prev=["ch5_brothers", "ch1:ch1_rival_b"], rep=[(76, 500)],
         choice=["war_axe", "back_blade", "grunt_staff"],
         interact=[("bguard", "The Tide-Broken are with you. Sound the horn.")], interact_goal="The horn sounded",
         interact_beats=[
             ("face", "self", "player"), ("emote", "self", "roar"), ("sound", "self", GRUNT_HORN), ("wait", 800),
             ("yell", "self", "Valormok! The fish-people stand with us! DOWN THE ROAD!", "shout"),
             ("summon", "road_grunt", "line_l", 360), ("summon", "road_grunt", "line", 360),
             ("summon", "road_myr", "line_r", 360), ("summon", "road_myr", "myr_1", 360),
             ("summon", "szaria_road", "szaria_road", 600), ("summon", "back_grunt", "back_1", 360),
             ("summon", "back_myr", "back_2", 360), ("wait", 1200),
             ("face", "back_grunt", "back_e1"), ("face", "back_myr", "back_e2"), ("state", "back_grunt", "ready"),
             ("state", "back_myr", "ready_thrown"),
             ("yell", "szaria_road", "Tide-Broken! With the orcs! Era'sazjar!", "battle_roar"),
             ("sound", "szaria_road", "siren_aggro"), ("wait", 1500),
             ("summon", "war_party", "wp_1", 330), ("summon", "war_party", "wp_2", 330), ("summon", "war_party", "wp_3", 330),
             ("summon", "war_witch", "wp_4", 330), ("sound", "self", HORN), ("wait", 15000),
             ("summon", "war_party", "wp_1", 300), ("summon", "war_party", "wp_2", 300), ("summon", "war_party", "wp_3", 300),
             ("summon", "war_party", "wp_4", 300), ("emote", "back_grunt", "attack"), ("emote", "back_myr", "attack2h"),
             ("wait", 1500), ("emote", "back_grunt", "attack"), ("emote", "back_myr", "attack2h"), ("wait", 14000),
             ("summon", "ssethis_officer", "ssethis_back", 120), ("summon", "war_party", "wp_1", 280),
             ("summon", "war_party", "wp_3", 280), ("summon", "war_party", "wp_4", 280), ("summon", "war_witch", "wp_2", 280),
             ("emote", "ssethis_officer", "battle_roar"), ("sound", "ssethis_officer", "naga_aggro"),
             ("yell", "ssethis_officer", "Hold! Hold the road, for the Empress!", "battle_roar"), ("wait", 15000),
             ("summon", "war_party", "wp_1", 260), ("summon", "war_party", "wp_2", 260), ("summon", "war_party", "wp_3", 260),
             ("summon", "war_party", "wp_4", 260), ("emote", "back_grunt", "attack"), ("emote", "back_myr", "attack2h"),
             ("wait", 8000),
             # (1.20b: the shard in his bedding; he has hunted the heretic since: he charges, is beaten down, dragged off)
             ("face", "ssethis_officer", "player"),
             ("yell", "ssethis_officer", "YOU. Heretic! It was YOUR shard! Everyone heard me! NOBODY LISTENED!", "battle_roar"),
             ("sound", "ssethis_officer", "naga_aggro"), ("move", "ssethis_officer", "ssethis_down", "run"), ("wait", 2500),
             ("move", "road_myr", "ssethis_down", "run"), ("wait", 2500), ("emote", "road_myr", "attack2h"),
             ("emote", "ssethis_officer", "wound"), ("sound", "ssethis_officer", "naga_wound"), ("wait", 900),
             ("emote", "road_myr", "attack2h"), ("visual", "ssethis_officer", STUN_STARS), ("state", "ssethis_officer", "drowned"),
             ("sound", "ssethis_officer", "naga_wound"), ("wait", 3500), ("state", "ssethis_officer", "none"),
             ("move", "ssethis_officer", "dragged", "walk"), ("move", "road_myr", "dragged", "walk"),
             ("yell", "ssethis_officer", "It was the heretic's! It was always the heretic's!", "battle_roar"), ("wait", 9000),
             ("despawn", "ssethis_officer")],
         emotes=[("szaria_road", "roar", 1,
                  [("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro"), ("emote", "road_grunt", "roar"),
                   ("emote", "back_grunt", "roar"), ("sound", "back_grunt", CHEER_HORDE), ("emote", "road_myr", "battle_roar"),
                   ("emote", "back_myr", "battle_roar"), ("wait", 2500), ("move", "self", "agtor_front", "run"),
                   ("wait", 17500), ("face", "self", "agtor"), ("emote", "self", "spell"), ("visual", "self", WATER),
                   ("wait", 4000), ("emote", "self", "battle_roar")])],
         goal="Tell Blood Guard Grozak at the head of Valormok's west road to sound the horn, kill 12 Spitelash "
              "Warmongers with the grunts and the Tide-Broken, then /roar at Lady Szaria and return to Ag'tor.",
         text="Your people and my people, both on my west road, both bleeding for it. A Spitelash war party is coming "
              "up from the river, and this time they have an officer who shouts. Good. Grozak has the horn at the "
              "road's head. Tell him. My grunts go down with you. Your lady says hers will be there. We will see.",
         progress="The road?",
         reward="She came up the road wet to the elbows and held out her hand to me. Cold. Wet. A grip like a shark. I "
                "took it. ...And the screaming one. He screamed your name all the way down the road. You have a friend "
                "there, snake. Take your pick of the armoury. You earned it on the road, with my grunts watching.",
         details=["talk", "point"], reward_emotes=["salute", "talk", "roar"],
         poi=["bguard", "west_road"]),

    # 5.23a: mercy for Ssethis (hero): his bonds cut; he looks at the banner a long time, and goes
    dict(key="ch5_ssethis_a", title="Mercy for Ssethis", giver="ch0:szaria", ender="ch0:szaria", level=33, xp=8,
         tone="serious", path="hero", exclusive=1, prev_any=["ch5_war_party", "ch5_war_party_b"],
         interact=[("ssethis_bound", "Cut his bonds.")], interact_goal="Ssethis set free",
         interact_beats=[("unaura", "self", 68341), ("state", "self", "none"), ("sound", "self", 1193), ("wait", 1500),
                         ("face", "self", "player"), ("wait", 3000), ("face", "self", "banner"), ("wait", 7000),
                         ("emote", "self", "roar"), ("wait", 2500), ("move", "self", "ssethis_sea", "walk"), ("wait", 17500),
                         ("sound", "self", "splash"), ("despawn", "self"), ("move", "escort_myr", "ssethis_guard_1", "walk"),
                         ("move", "escort_myr_2", "ssethis_guard_2", "walk")],
         goal="Cut the bonds of Ssethis, the war party's officer, held by the banner at the Hollow, and let him go back "
              "to the sea.",
         text="The officer from Ag'tor's road. Ssethis. He knows you; that much was plain on the road. The orcs wanted "
              "his head on a pole. I said he was ours. Now I have to decide what ours means. Cut him loose. Let him swim "
              "home and tell them the renegades let him go. Let the Empress's people chew on that.",
         progress="He's still tied.",
         reward="He didn't thank you. Good. If he'd thanked you I'd have worried. He looked at the banner a long time. "
                "They always do, the first time they see someone's chosen it.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "sea_south"), ("sound", "self", HORN), ("summon", "ssethis_bound", "ssethis_rise", 300),
                 ("summon", "escort_myr", "ssethis_rise", 300), ("summon", "escort_myr_2", "ssethis_rise", 300),
                 ("wait", 800), ("sound", "self", "splash"), ("move", "ssethis_bound", "ssethis_bound", "walk"),
                 ("move", "escort_myr", "ssethis_guard_1", "walk"), ("move", "escort_myr_2", "ssethis_guard_2", "walk"),
                 ("wait", 11500),
                 ("face", "ssethis_bound", "player"), ("emote", "self", "talk"), ("face", "self", "player")],
         complete=[("face", "self", "sea_south"), ("wait", 2000), ("emote", "self", "work"), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["ssethis_bound"]),

    # 5.23b: the empty rival (menace): the Unsingers' own trick on him; he wanders off; Isshara turns her back
    dict(key="ch5_ssethis_b", title="The Empty Rival", giver="ch0:szaria", ender="ch0:szaria", level=33, xp=8,
         tone="serious", path="menace", exclusive=1, prev_any=["ch5_war_party", "ch5_war_party_b"], source="blank_pearl",
         use=[("blank_pearl", "ssethis_bound", 1,
               [("aura", "self", GLOW_BLACK), ("visual", "self", SPIRIT_PURPLE), ("sound", "self", "siren_hiss"),
                ("wait", 2500), ("unaura", "self", 68341), ("state", "self", "none"), ("face", "ch0:isshara", "sea_east"),
                ("visual", "ch0:isshara", WATER), ("wait", 1500), ("face", "self", "banner"), ("wait", 2500),
                ("face", "self", "player"), ("wait", 2500), ("emote", "self", "stun"), ("wait", 2000),
                ("move", "self", "ssethis_shore", "walk"), ("wait", 11500), ("move", "self", "ssethis_sea", "walk"),
                ("wait", 16000), ("despawn", "self")])],
         goal="Use the Unsinger's Empty Pearl on Ssethis, held by the banner at the Hollow, and let him go harmless.",
         text="The officer from Ag'tor's road. Ssethis. He knows where we are now, and what we are, and he'll tell them. "
              "Unless he doesn't know. You kept one of their pearls from the rock; I saw. You know what it does. I won't "
              "do it. I won't stop you. That's as far as I go.",
         progress="Do it or don't.",
         reward="He went along the shore like a hatchling looking for the crèche. ...Isshara heard it. She heard it all. "
                "She's turned her back to the pool, and she won't turn round. Give her time. Or don't; I don't think time "
                "is the thing she wants from you.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "sea_south"), ("sound", "self", HORN), ("summon", "ssethis_bound", "ssethis_rise", 300),
                 ("summon", "escort_myr", "ssethis_rise", 300), ("summon", "escort_myr_2", "ssethis_rise", 300),
                 ("wait", 800), ("sound", "self", "splash"), ("move", "ssethis_bound", "ssethis_bound", "walk"),
                 ("move", "escort_myr", "ssethis_guard_1", "walk"), ("move", "escort_myr_2", "ssethis_guard_2", "walk"),
                 ("wait", 11500),
                 ("face", "ssethis_bound", "player"), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 1500), ("face", "self", "sea_south")],
         complete=[("face", "self", "isshara"), ("wait", 2000), ("face", "ch0:isshara", "sea_east"),
                   ("visual", "ch0:isshara", WATER), ("sound", "ch0:isshara", "pickup_water"), ("wait", 2000),
                   ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["ssethis_bound"]),

    # 5.24: the shape of the prince (the chapter's last): a flame like a phoenix on the pool; a blood elf at Valormok
    dict(key="ch5_end", title="The Shape of the Prince", giver="ch0:isshara", ender=AGTOR, level=33, xp=8,
         tone="serious", prev_any=["ch5_ssethis_a", "ch5_ssethis_b"], choice=["phoenix_gloves", "pool_grips", "tide_gauntlets"],
         goal="Go to Valormok and ask Ag'tor Bloodfist about a blood elf with four singing pearls.",
         text="Four more songs. I can feel them the way you feel a storm in your scales. Not Szaria's, not Ssaveth's: mine. "
              "My years at Vashj's side with the prince of the blood elves, Kael'thas, from the lake to the portal. Four "
              "pearls, and... a blood elf has them. Look at the water. Tell me what's on it. ...Yes. Go to the orc. Something with "
              "red and gold on it has come to his camp.",
         reward="A blood elf? Yes. Came up the road two days ago, red and gold, nose in the air. Asks about the old "
                "witch's renegades. Asks about pearls. I told him the snakes are my neighbours now. He didn't like that. "
                "He's over there, not liking it.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "pool"), ("state", "self", "channel"), ("sound", "self", "siren_hiss"),
                 ("summon", "pool_glow", "pool", 25), ("wait", 3500), ("sky", "pool_phoenix", "pool", 3, 12),
                 ("sound", "self", 3090), ("music", 6074), ("wait", 4500), ("state", "self", "none"),
                 ("face", "self", "toward_valormok"), ("emote", "self", "spell"), ("wait", 2000), ("face", "self", "player"),
                 ("emote", "self", "talk")],
         poi=["agtor"]),

    # 5.25: the wind rider's fish (stupid): it sniffs you, sneezes on you, eats, and lies down on your tail
    dict(key="ch5_wind_rider", title="The Wind Rider's Fish", giver=KROUM, ender=KROUM, level=33, xp=8, tone="stupid",
         prev_any=["ch5_war_party", "ch5_war_party_b"], rep=[(76, 150)], rewards=["feather", "snapper_snack"],
         use=[("bay_snapper", "wind_rider", 5,
               [("face", "self", "player"), ("sound", "self", WYVERN_FIDGET_2), ("wait", 1500), ("visual", "player", WATER),
                ("aura", "player", "wind_slap"), ("sound", "self", WYVERN_FIDGET), ("wait", 1500),
                ("sound", "self", 1189), ("wait", 2000), ("move", "self", "rider_lie", "walk"), ("wait", 1500),
                ("state", "self", "sleep"), ("wait", 20000), ("state", "self", "none"), ("move", "self", "wind_rider", "walk")])],
         goal="Catch 5 Bay Snappers in the water round the Hollow and feed them to Kroum's Wind Rider at Valormok.",
         text="Ha! Look at it. It thinks you're a fish. A big fish, with hair. It doesn't eat things that think. Listen: "
              "every flier at Valormok has to know your smell, or one day it drops you in the bay. Bring it fish. Bay "
              "snappers, the fat ones that school round your islet. Five. Feed it from the hand. If you still have a hand.",
         progress="It's still hissing. Fish. More fish.",
         reward="It sneezed on you! Ha! HA! It likes you! When it lies on your tail, that means it owns you. You belong "
                "to a wind rider now, snake. Ha! Here, take this, it moulted it on purpose for you. Probably.",
         details=["laugh", "point"], reward_emotes=["laugh", "laugh", "point", "laugh"],
         poi=["schools", "wind_rider"]),
]

# -- more of someone already made -------------------------------------------------------------------------------------
SPAWNS = [
    # young Vyssa in Dalaran's ruins (m7); young Ssaveth at Illidan's camp above the river (m8)
    dict(npc="ch0:vyssa_young", at="m7_vyssa", facing=3.4, phase=M7),
    dict(npc="ch0:ssaveth_young", at="m8_ssaveth", facing=0.4, phase=M8),
]
