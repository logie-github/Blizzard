# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 4 of the naga's story: Scarscale (levels 25 to 29), the bible's section 11.

The Hollow (chapter 2's camp on the islet in the Bay of Storms, 3920-3985, -6235 to -6330) is the hub: Lady Szaria
stands where chapter 1 put her (ch1:hollow_szaria); Isshara (by her pool at the islet's south-east end), Ssaveth, Vyssa
and the hub kit are chapter 2's spawns there. This chapter's scenes at the Hollow move them as little as possible:
Szaria walks and comes back, the others turn, gesture and speak where they stand, and whoever comes for one scene (a
herald, lancers, runaways, snappers, lookers) is summoned for it. Thessa, the priest trainer, is placed here (by the
pool, from 4.20). The present's other places: Southridge Beach across the bay (a Spitelash band under Serpentra's old
colours, and their buried cache), Shadowsong Shrine on its hill above the Southfury (Shaelyn Harborsong, her fire and
her broken pillar), Hetaera's rock south-west of the Hollow (Mrgl hides there), Valormok (Ag'tor gives his banner and
Jediga ends the chapter: the game's own, with no scenes of the story's; the envoy's tent at the camp's eastern edge).

Two memories, both Szaria's, sung by Isshara at her pool (one wakes on the pool's shore, chapter 2's pool_shore):
  - m5, Wrath of the Betrayer (bit B), on the Shattered Strand's eastern beach under the Tower of Eldara: the naga's
    dig on the beach, young Serena Scarscale on a rock above the Watchers' camp on the promontory, the landing at its
    eastern tip where the runner boards, and two broken pillars standing in the water there as the Pillars of Aszune.
    The bible's two points (4180, -6300 and the tower) are 1550 yards apart and the first is 230 yards from the
    Hollow's pool; a memory's ground is one circle that mustn't hold its pool, so both stages are the tower's.
  - m6, Balancing the Scales (bit A), on Southridge Beach: Serpentra's spawning ground and her dune at the beach's
    eastern rise, the night elf fleet offshore, the landing in the shallows before the base, the mountain giants at
    the foot of the cliffs to the west.

Phases in Azshara: the envoy's tent at Valormok with its Tide-Caller, Valormok's banner and Thessa at the Hollow, all
from 4.20's reward (ENVOY: this chapter's one rule). The present's enemies and quest things that stand (the Wavecallers,
their banners and their cache at Southridge, the kelp beds and the sea-glass round the Hollow) share chapter 2's own
rule for the Hollow's people (HOLLOW: from 2.01 until 7.02 overturns the Hollow): no bit of their own, gone with the
Hollow. Shaelyn (chapter 2's, placed here) and her shrine are there always (she's in later chapters too). The ghosts
of 4.17, the snappers of 4.23 and everyone who comes for one scene are summoned.

Choices: 4.19a (hero, the keeper brought to the girl) and 4.19b (menace, the glaive taken), either finishes the
chapter; 4.19a gives Shaelyn's Moonstone Arrows (ch4:moonstone_arrows) and 4.19b the Broken Watcher's Glaive
(ch4:glaive), which chapter 5's 5.14 uses to break the Unsingers' ward.

Plain data: tools/murloc/SCHEMA.md, tools/naga/SCHEMA.md."""

ENVOY = ("from", "ch4_envoy")                                      # the envoy's tent at Valormok, from 4.20's reward
HOLLOW = ("between", "ch2:ch2_arrival", "ch7:ch7_overturned")     # chapter 2's rule for the Hollow's people (no new bit)
M5 = ("memory", "m5")                                              # Wrath of the Betrayer (Szaria's), the Tower of Eldara
M6 = ("memory", "m6")                                              # Balancing the Scales (Szaria's), Southridge Beach

CHAPTER = dict(key="ch4", title="Scarscale", levels=(25, 30), map=1, zones=[16], hub="hollow")

PLACES = {
    # -- the Hollow: the islet in the Bay of Storms (Szaria at ch1:hollow_szaria, 3954, -6266) ---------------------
    "hollow": (3954.0, -6266.0), "hollow_inland": (3968.0, -6266.0),
    "hollow_pool": (3959.0, -6311.0), "isshara_bed": (3963.0, -6316.0), "pool_side": (3961.0, -6312.0),
    "pool_edge": (3958.0, -6320.0),
    "sea_south": (3880.0, -6268.0, 0.0), "sea_west": (3900.0, -6180.0, 0.0), "sea_east": (3950.0, -6360.0, 0.0),
    "toward_valormok": (3681.0, -4407.0), "toward_shadowsong": (2866.0, -4022.0), "toward_southridge": (2950.0, -6050.0),
    # the herald at the south waterline (4.01) and her return with lancers (4.21)
    "herald_rise": (3909.0, -6265.0, -1.0), "guard_rise_1": (3907.0, -6258.0, -1.0), "guard_rise_2": (3907.0, -6272.0, -1.0),
    "herald_sand": (3919.0, -6265.0), "guard_sand_1": (3920.0, -6259.0), "guard_sand_2": (3918.0, -6271.0),
    "szaria_down": (3926.0, -6265.0), "shell_sand": (3922.0, -6264.0), "herald_away": (3880.0, -6262.0, -2.0),
    "lancer_rise_1": (3903.0, -6248.0, -1.0), "lancer_rise_2": (3903.0, -6282.0, -1.0), "lancer_rise_3": (3898.0, -6262.0, -1.0),
    "lancer_rise_4": (3908.0, -6236.0, -1.0), "lancer_rise_5": (3908.0, -6296.0, -1.0), "lancer_rise_6": (3895.0, -6275.0, -1.0),
    "lancer_beach_1": (3922.0, -6252.0), "lancer_beach_2": (3922.0, -6278.0), "lancer_beach_3": (3924.0, -6265.0),
    # Valormok's banner (4.20 on), beside the camp's own at the islet's west end
    "hollow_banner": (3940.0, -6256.0), "banner_front": (3943.0, -6259.0),
    # Ssaveth's three rocks (4.23: the north one, the east one, the south one) and the snappers in the shallows
    "rock_1": (3918.0, -6244.0), "rock_2": (3989.0, -6268.0), "rock_3": (3946.0, -6313.0),
    "snap_1": (3905.0, -6232.0), "snap_2": (3895.0, -6205.0), "snap_3": (3878.0, -6250.0), "snap_4": (3886.0, -6285.0),
    "snap_5": (3900.0, -6318.0), "snap_6": (3925.0, -6338.0), "snap_7": (3952.0, -6345.0), "snap_8": (3985.0, -6345.0),
    "snap_9": (3998.0, -6332.0), "snap_10": (3868.0, -6215.0), "snap_11": (3912.0, -6190.0), "snap_12": (3940.0, -6352.0),
    "snap_13": (3972.0, -6352.0), "snap_14": (3892.0, -6262.0), "snap_15": (3915.0, -6300.0), "snap_16": (3925.0, -6205.0),
    "snappers": (3920.0, -6280.0),
    # Thessa, the priest trainer from 4.20, at the islet's south-east tip by the keeper's pool; her ring of lenses on
    # the sand there (4.24), and the renegades who come to look
    "thessa": (3983.0, -6324.0), "lens_ring": (3980.0, -6329.0), "lens_1": (3982.5, -6329.0), "lens_2": (3981.2, -6331.2),
    "lens_3": (3978.8, -6331.2), "lens_4": (3977.5, -6329.0), "lens_5": (3978.8, -6326.8), "lens_6": (3981.2, -6326.8),
    "looker_from_1": (3986.0, -6312.0), "looker_from_2": (3971.0, -6306.0), "looker_from_3": (3965.0, -6310.0),
    "looker_1": (3984.0, -6327.0), "looker_2": (3976.0, -6331.0), "looker_3": (3979.0, -6325.0),
    "thessa_glass": (3850.0, -6130.0),
    # sea-glass on the rocks in the bay (4.24), long kelp in the shallows (4.25)
    "glass_1": (3848.0, -6112.0), "glass_2": (3856.0, -6122.0), "glass_3": (3834.0, -6150.0), "glass_4": (4092.0, -6182.0),
    "glass_5": (4080.0, -6168.0), "glass_6": (4128.0, -6312.0), "glass_7": (4116.0, -6324.0), "glass_8": (4104.0, -6178.0),
    "kelp_1": (3895.0, -6290.0), "kelp_2": (3900.0, -6330.0), "kelp_3": (3960.0, -6345.0), "kelp_4": (4010.0, -6320.0),
    "kelp_5": (3870.0, -6235.0), "kelp_6": (4005.0, -6215.0), "kelp_7": (3880.0, -6305.0), "kelp_8": (3990.0, -6350.0),
    "kelp_beds": (3940.0, -6300.0),
    # the kelp blanket over the keeper's bed (4.25), and a siren who has opinions about it
    "blanket": (3963.0, -6316.0), "siren_watch": (3968.0, -6308.0),
    # Mrgl's rock (Hetaera's, south-west of the Hollow) and the patrols in the water between (4.22)
    "mrgl_rock": (3852.0, -6140.0), "runaway_1": (3848.0, -6136.0), "runaway_2": (3856.0, -6145.0),
    "runaway_3": (3846.0, -6146.0), "runaway_4": (3858.0, -6135.0), "crab": (3851.0, -6149.0),
    "picket_1": (3880.0, -6175.0, -1.0), "picket_2": (3905.0, -6212.0, -1.0), "picket_3": (3868.0, -6205.0, -1.0),
    "mrgl_count": (3966.0, -6302.0), "clam_spot": (3965.0, -6298.0),
    # -- Southridge Beach today: the Wavecallers under Serpentra's old colours (4.09) and their cache (4.10) ----------
    "southridge": (2950.0, -6050.0),
    "wc_1": (2932.0, -6002.0), "wc_2": (2946.0, -6022.0), "wc_3": (2962.0, -6040.0), "wc_4": (2936.0, -6046.0),
    "wc_5": (2950.0, -6070.0), "wc_6": (2966.0, -6084.0), "wc_7": (2924.0, -6082.0), "wc_8": (2955.0, -6012.0),
    "wc_9": (2972.0, -6060.0), "wc_10": (2940.0, -6100.0),
    "colours_1": (2948.0, -6062.0), "colours_2": (2930.0, -6028.0), "cache": (2944.0, -6110.0),
    # -- Shadowsong Shrine: Shaelyn's fire on the hilltop, her pillar behind her, the trail up from the south-west --
    "shaelyn": (2866.0, -4024.0), "shaelyn_step": (2858.0, -4018.0), "shaelyn_fire": (2873.0, -4030.0),
    "pillar": (2852.0, -4012.0),
    "flowers": (2853.5, -4014.5), "glaive_on_pillar": (2851.0, -4013.5), "pillar_front": (2855.0, -4015.0),
    "shaelyn_trees": (2895.0, -4045.0), "shrine_dark": (2880.0, -3975.0), "trail_foot": (2805.0, -3990.0),
    "bearer_foot": (2801.0, -3995.0), "trail_away": (2790.0, -3975.0),
    "draw_house": (2869.5, -4020.0), "draw_fire": (2870.5, -4021.0), "draw_long": (2868.0, -4019.0),
    "draw_small": (2867.0, -4018.0), "drawing": (2869.0, -4020.0),
    "ghost_1": (2840.0, -3990.0), "ghost_2": (2885.0, -4085.0), "ghost_3": (2830.0, -4050.0), "ghost_4": (2902.0, -4000.0),
    "ghost_5": (2850.0, -4078.0), "ghost_6": (2880.0, -3982.0), "ghost_7": (2930.0, -4010.0), "ghost_8": (2826.0, -4020.0),
    "ghost_9": (2868.0, -4092.0), "ghost_10": (2915.0, -4090.0), "ghost_11": (2835.0, -3970.0), "ghost_12": (2935.0, -3995.0),
    "ghost_13": (2820.0, -4065.0), "ghost_14": (2860.0, -3965.0),
    # -- Valormok: the envoy's tent at the camp's eastern edge, by the Tide-Caller's landing (ch0:envoy_landing) --
    "envoy_tent": (3686.0, -4428.0), "envoy": (3678.0, -4419.0), "envoy_tidecaller": (3671.0, -4409.0),
    "envoy_banner": (3692.0, -4417.0), "envoy_torch_1": (3680.0, -4433.0), "envoy_torch_2": (3690.0, -4410.0),
    "envoy_crate": (3693.0, -4431.0), "envoy_jar": (3675.0, -4426.0), "agtor": (3601.0, -4406.0), "jediga": (3603.0, -4421.0),

    # -- memory m5 (bit B): Wrath of the Betrayer, the strand and the promontory under the Tower of Eldara ----------
    "m5_centre": (4250.0, -7760.0), "m5_arrive": (4330.0, -7640.0),
    "szaria_dig": (4305.0, -7690.0), "serena_rock": (4270.0, -7732.0), "serena_tip": (4245.0, -7866.0),
    "dig_1": (4300.0, -7660.0), "dig_2": (4312.0, -7678.0), "dig_3": (4296.0, -7703.0), "dig_4": (4322.0, -7700.0),
    "dig_5": (4336.0, -7668.0), "dig_6": (4288.0, -7682.0), "dig_7": (4316.0, -7718.0), "dig_8": (4340.0, -7690.0),
    "digs": (4315.0, -7690.0),
    "ex_1": (4298.0, -7668.0), "ex_2": (4326.0, -7686.0), "ex_3": (4284.0, -7695.0), "ex_4": (4330.0, -7712.0),
    "ex_5": (4312.0, -7656.0), "m5_crate_1": (4318.0, -7672.0), "m5_crate_2": (4292.0, -7710.0), "m5_weapons": (4335.0, -7680.0),
    "camp": (4238.0, -7800.0), "tent_1": (4245.0, -7790.0), "tent_2": (4228.0, -7775.0), "tent_3": (4256.0, -7806.0),
    "lantern_1": (4238.0, -7798.0), "lantern_2": (4252.0, -7820.0), "m5_banner": (4232.0, -7810.0),
    "w_1": (4225.0, -7800.0), "w_2": (4240.0, -7815.0), "w_3": (4210.0, -7790.0), "w_4": (4250.0, -7832.0),
    "w_5": (4222.0, -7838.0), "w_6": (4205.0, -7815.0), "w_7": (4236.0, -7848.0), "w_8": (4262.0, -7845.0),
    "s_1": (4232.0, -7768.0), "s_2": (4245.0, -7784.0), "s_3": (4214.0, -7772.0), "s_4": (4263.0, -7798.0), "s_5": (4222.0, -7752.0),
    "host_1": (4262.0, -7758.0), "host_2": (4278.0, -7772.0), "host_3": (4252.0, -7745.0), "host_siren": (4285.0, -7752.0),
    # the runner's way: out of the camp to the boat at the promontory's eastern tip, between the Pillars to open sea
    "runner_start": (4235.0, -7795.0), "board_point": (4232.0, -7880.0), "boat_wait": (4228.0, -7893.0, 0.0),
    "open_sea": (4235.0, -7995.0, 0.0), "pillar_1": (4205.0, -7900.0), "pillar_2": (4262.0, -7902.0),
    "the_pillars": (4233.0, -7882.0),
    "swim_1": (4255.0, -7880.0, -1.0), "swim_2": (4215.0, -7885.0, -1.0), "swim_3": (4245.0, -7895.0, -1.0),
    "chase_1": (4240.0, -7962.0, -1.0), "chase_2": (4225.0, -7966.0, -1.0), "chase_3": (4250.0, -7970.0, -1.0),

    # -- memory m6 (bit A): Balancing the Scales, Southridge Beach ----------------------------------------------------
    "m6_centre": (2955.0, -6055.0), "m6_arrive": (2925.0, -6075.0), "szaria_m6": (2930.0, -6068.0),
    "serpentra": (2948.0, -6116.0), "spawning_ground": (2940.0, -6106.0),
    "guard_m6_1": (2938.0, -6100.0), "guard_m6_2": (2926.0, -6094.0), "guard_m6_3": (2952.0, -6098.0),
    "m6_banner_1": (2936.0, -6110.0), "m6_banner_2": (2957.0, -6104.0), "m6_torch_1": (2928.0, -6101.0),
    "m6_torch_2": (2947.0, -6093.0), "m6_coral_1": (2932.0, -6112.0), "m6_coral_2": (2944.0, -6118.0),
    "m6_egg_1": (2935.0, -6107.0), "m6_egg_2": (2943.0, -6111.0), "m6_egg_3": (2939.0, -6114.0),
    "ship_1": (3075.0, -5995.0, 0.0), "ship_2": (3085.0, -6065.0, 0.0),
    # the landing (4.11): two boats into the shallows before the base, the druid and the priestess ashore
    "lboat_1": (2995.0, -6060.0, 0.0), "lboat_2": (2997.0, -6085.0, 0.0),
    "lshore_1": (2985.0, -6054.0, 0.0), "lshore_2": (2987.0, -6080.0, 0.0),
    "malf_land": (2978.0, -6056.0), "tyr_land": (2978.0, -6076.0), "malf_ashore": (2955.0, -6050.0),
    "tyr_ashore": (2963.0, -6066.0), "elves_away": (2942.0, -5998.0),
    "lsen_1": (2980.0, -6062.0), "lsen_2": (2982.0, -6071.0), "lsen_3": (2979.0, -6050.0),
    "lsen_to_1": (2955.0, -6086.0), "lsen_to_2": (2958.0, -6078.0), "lsen_to_3": (2950.0, -6074.0),
    # the cliffs (4.12) and their giants; the night elves on the beach (4.13, 4.15); the warden far off (4.13)
    "malfurion_cliff": (2894.0, -6026.0), "cliff": (2890.0, -6020.0),
    "g_1": (2908.0, -5992.0), "g_2": (2912.0, -6012.0), "g_3": (2906.0, -6034.0), "g_4": (2918.0, -5978.0),
    "sen_1": (2965.0, -6010.0), "sen_2": (2972.0, -6025.0), "sen_3": (2958.0, -6000.0), "sen_4": (2950.0, -5990.0),
    "sen_5": (2975.0, -6040.0), "hu_1": (2945.0, -6020.0), "hu_2": (2938.0, -6005.0), "hu_3": (2960.0, -6030.0),
    "beach_m6": (2960.0, -6020.0), "maiev_far": (2942.0, -5992.0),
    # the net (4.14): Illidan by the base, the priestess comes to him; the druid and the warden after
    "illidan_m6": (2942.0, -6096.0), "tyr_arrive": (2970.0, -6050.0), "tyr_face": (2950.0, -6087.0),
    "malf_arrive": (2976.0, -6046.0), "malf_stop": (2958.0, -6070.0), "maiev_arrive": (2978.0, -6060.0),
    "maiev_stop": (2957.0, -6078.0),
    # Ash Karath (4.15): Illidan's boat, and the druid holding the priestess on the sand
    "illidan_shore": (2978.0, -6096.0), "iboat": (2992.0, -6100.0, 0.0), "iboat_out": (3075.0, -6125.0, 0.0),
    "malf_hold": (2962.0, -6058.0), "tyr_hold": (2960.0, -6062.0),
}

# -- looks and models -----------------------------------------------------------------------------------------------
GIANT_CLAM_OPEN = "World\\GENERIC\\ACTIVEDOODADS\\Clam\\GiantClamActive.m2"
GIANT_CLAM_SHUT = "World\\GENERIC\\ACTIVEDOODADS\\Clam\\GiantClamCLOSED.M2"
HORDE_BANNER = 5111                         # HordeBanner03 (GameObjectDisplayInfo)
NE_TENT = 9177                              # nightelfsingletent01
NE_TENT_2 = 9176                            # nightelfsingletent02
NE_LANTERN = 6913                           # NightElfLantern02
NE_BANNER = "World\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\Banners\\NightElfOwlBanner01.m2"
NE_RUIN = 2935                              # AZRElfRuin02: the broken pillar at Shadowsong
NE_RUIN_TALL = 2937                         # NightElfRuins04: the Pillars of Aszune
NE_SHIP = 7087                              # Transportship_NE (the Auberdine ships), a static object here
NE_GLAIVE = "World\\ENVIRONMENT\\DOODAD\\GENERALDOODADS\\NightElfWeapons\\NE_Glaive01.m2"
DIRT = 20                                   # DirtMound01
TABLET = "World\\Kalimdor\\Azshara\\ActiveDoodads\\StoneTablets\\AzsharaStoneTablet01.m2"
ROCK = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Rocks\\AzsharaRock01.m2"
CRYSTAL = "World\\Kalimdor\\Azshara\\ActiveDoodads\\ArcaneCrystal\\ArcaneCrystal.m2"
KELP = "World\\Generic\\Underwater\\PassiveDoodads\\Seaweed\\GenericSeaweed01.mdx"
SEAWEED = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Seaweed\\SeaWeed01.mdx"
CORAL_TREE = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree01.mdx"
EGG = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_01.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
FLOWERS = 6313                              # FlowersBunch04
CAMPFIRE = 192                              # ElwynnCampfire
ROWBOAT = 30874                             # DarkshoreBoat_vehicle (a creature look: a night elf boat that moves)

# Spells for their look (tools/murloc/SCHEMA.md "visual"; effects.md)
FROST_HAND, LIGHTNING, LIGHTNING_NOVA, WATER = 32992, 10387, 57322, 36005
GLOW_BLUE, GLOW_GREEN, NATURE, DUST, NET = 22576, 22577, 13236, 69216, 47021
FIRE, BURNING, SPIRIT, SPRINT, HOLY_NOVA = 51195, 59216, 17327, 2983, 57771
SPOTLIGHT, HOLY_ZONE, FEL_SMOKE, ARCANE_BURST, STUN_STARS = 25824, 70571, 35411, 35426, 43328
# Sounds (SoundEntries): conches, the night elves' own voices, a giant's, a laugh the naga kept from their elf days
HORN, ELF_LAUGH, ELF_CRY, ELF_SCREAM, ELF_WOUND = 7054, 6928, 6926, 1359, 1358
GIANT_ROAR, GIANT_STEP, PICK, CHEST, SPLASH_BIG = 3680, 3681, 1194, 1277, 1097

NPCS = [
    # -- the present: the Hollow's scenes (summoned) ------------------------------------------------------------
    # the herald under the open shell (4.01) and her honour guard; the same herald with lancers when it's war (4.21)
    dict(key="herald", name="Herald Thyssa", subname="Herald of the Empress's Envoy", look=11266, size=1.25, level=29,
         role="ambient", untouchable=True, summoned=True, idle=[("every", 7000, [("visual", "self", GLOW_BLUE)])]),
    dict(key="herald_guard", name="Honor Guard of the Empress", look=20200, equip=(15910, 0, 0), size=1.6, level=35,
         role="ambient", untouchable=True, summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="herald_guard_2", name="Honor Guard of the Empress", look=22877, equip=(15910, 0, 0), size=1.6, level=35,
         role="ambient", untouchable=True, summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="thyssa", name="Herald Thyssa", subname="Herald of the Empress's Envoy", look=11266, equip=(5284, 0, 0),
         size=1.25, level=29, side="naga", role="enemy", caster=True, health=2.5, damage=1.1, summoned=True,
         abilities=[(9672, 6000), (11831, 20000)]),
    dict(key="lancer", name="Spitelash Lancer", plural="Spitelash Lancers", look=6747, looks=[11265], equip=(5745, 0, 0),
         size=1.2, level=28, side="naga", role="enemy", health=0.9, summoned=True, abilities=[(15284, 9000), (6533, 22000)]),
    # Mrgl's runaways (4.22): four mur'gul from the crèche, and a crab that joined the line somewhere
    dict(key="runaway_1", name="Runaway Mur'gul", look="murloc_abyssal", scale=0.85, level=8, role="ambient", summoned=True,
         idle=[("every", 21000, [("emote", "self", "cry"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="runaway_2", name="Runaway Mur'gul", look="murloc_abyssal", scale=0.8, level=8, role="ambient", summoned=True,
         idle=[("every", 25000, [("emote", "self", "shy")])]),
    dict(key="runaway_3", name="Runaway Mur'gul", look="murloc_abyssal", scale=0.9, level=9, role="ambient", summoned=True,
         idle=[("every", 19000, [("emote", "self", "question"), ("sound", "self", "murloc_fidget")])]),
    dict(key="runaway_4", name="Hungry Mur'gul", look="murloc_abyssal", scale=0.85, level=8, role="ambient", summoned=True,
         idle=[("every", 11000, [("emote", "self", "eat"), ("sound", "self", 1189)])]),
    dict(key="stowaway", name="Shore Crab", look=999, scale=0.45, level=1, role="ambient", type="critter", summoned=True,
         idle=[("every", 17000, [("sound", "self", 1229)])]),
    dict(key="shorewatch", name="Spitelash Shore-Watch", plural="Spitelash Shore-Watches", look=6747, looks=[11265],
         equip=(2023, 0, 5870), size=1.15, level=28, side="naga", role="enemy", summoned=True, abilities=[(6533, 15000)]),
    # Thessa's ring (4.24): the light through the lenses, and the renegades who come one by one to look
    dict(key="lens_light", name="Light Through Sea-Glass", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 4000, [("visual", "self", SPOTLIGHT), ("visual", "self", HOLY_ZONE)])]),
    dict(key="looker_1", name="Tide-Broken Myrmidon", look=4765, equip=(5745, 0, 0), size=1.15, level=28, role="ambient",
         untouchable=True, summoned=True),
    dict(key="looker_2", name="Tide-Broken Siren", look=4974, size=1.0, level=27, role="ambient", untouchable=True,
         summoned=True),
    dict(key="looker_3", name="Tide-Broken Myrmidon", look=6765, size=1.1, level=28, role="ambient", untouchable=True,
         summoned=True),
    # the kelp blanket's critic (4.25)
    dict(key="watching_siren", name="Tide-Broken Siren", look=4983, size=1.05, level=27, role="ambient", untouchable=True,
         summoned=True),

    # -- the present: Southridge Beach (the Spitelash band under Serpentra's old colours) ---------------------------
    dict(key="wavecaller", name="Spitelash Wavecaller", plural="Spitelash Wavecallers", look=11266, looks=[4974, 4976],
         equip=(5284, 0, 0), size=1.05, level=(26, 28), side="naga", role="enemy", caster=True, phase=HOLLOW, respawn=45,
         abilities=[(9672, 8000), (12548, 16000)],
         at=["wc_1", "wc_2", "wc_3", "wc_4", "wc_5", "wc_6", "wc_7", "wc_8", "wc_9", "wc_10"], wander=4.0),

    # -- the present: the shallows round the Hollow (the snappers come up for Ssaveth's patrol, 4.23) -----------
    dict(key="snapper", name="Makrinni Snapper", plural="Makrinni Snappers", look="makrinni", size=0.9, level=(26, 28),
         side="neutral", role="enemy", type="beast", summoned=True),

    # -- the present: Shadowsong Shrine --------------------------------------------------------------------------
    # Shaelyn Harborsong, the last of Nendis (bible 6.4), is chapter 2's (ch2:shaelyn), placed here by her fire (SPAWNS).
    # Whoever comes up her hill: she stands, draws, shouts, comes a few steps closer, lowers the bow (bible 4.16).
    dict(key="shrine_watch", name="Shadowsong Shrine", look="trigger", level=1, role="ambient", at="shaelyn",
         unit_flags=0x02000002,
         watch=(40, [("state", "ch2:shaelyn", "none"), ("face", "ch2:shaelyn", "player"), ("state", "ch2:shaelyn", "ready_bow"),
                     ("yell", "ch2:shaelyn", "Stop there, serpent. One more coil and I loose."), ("sound", "ch2:shaelyn", 2754),
                     ("wait", 5000), ("move", "ch2:shaelyn", "shaelyn_step", "walk"), ("wait", 4000),
                     ("face", "ch2:shaelyn", "player"), ("state", "ch2:shaelyn", "none"), ("emote", "ch2:shaelyn", "no"),
                     ("wait", 2500), ("move", "ch2:shaelyn", "shaelyn", "walk"), ("wait", 4000),
                     ("face", "ch2:shaelyn", "shaelyn_fire"), ("state", "ch2:shaelyn", "sit")], 120000)),
    # the Highborne's ghosts that rise every night (4.17: summoned as Shaelyn's scene calls the dark down)
    dict(key="ghost", name="Restless Highborne", plural="Restless Highborne", look="highborne_apparition", level=(26, 28),
         side="hostile", role="enemy", type="undead", summoned=True, abilities=[(9613, 9000)],
         idle=[("every", 8000, [("visual", "self", SPIRIT)])]),
    # the keeper brought up the hill (4.19a), and the renegade who carried her to its foot
    dict(key="isshara_walk", name="Isshara the Keeper", subname="Keeper of Songs", look="sea_witch", speed=0.6, level=45,
         role="ambient", untouchable=True, summoned=True, gossip="Lead me. I'll know her when I hear her breathe.",
         idle=[("every", 23000, [("visual", "self", WATER), ("sound", "self", "pickup_water")])]),
    dict(key="bearer", name="Tide-Broken Bearer", equip=(5745, 0, 0), speed=0.6, look=6765, size=1.15, level=28,
         role="ambient", untouchable=True, summoned=True, idle=[("state", "self", "ready_thrown")]),

    # -- the present: Valormok, the envoy's tent (4.20 on) -------------------------------------------------------
    dict(key="envoy", name="Ssira", subname="Envoy of the Tide-Broken", look=18386, size=1.05, level=30, role="ambient",
         at="envoy", facing=2.99, phase=ENVOY,
         gossip="One tent, he said. Small. I've measured it twice. The grunts still walk around it like it might bite.",
         idle=[("every", 43000, [("emote", "self", "talk"), ("face", "self", "agtor")]),
               ("every", 71000, [("emote", "self", "laugh"), ("face", "self", "envoy_tidecaller")])]),

    # -- memory m5: Wrath of the Betrayer (Szaria's) ---------------------------------------------------------------
    # young Serena Scarscale (canon, untouchable): the look players met at the crèche's line in 1.13
    dict(key="serena_young", name="Serena Scarscale", subname="Sea Witch of Illidan's Host", look="serena", size=1.25,
         level=40, role="quest", untouchable=True, language="universal", at="serena_rock", facing=4.23, phase=M5,
         gossip="Speak, or dig. I haven't decided which you're better at.",
         idle=[("every", 9000, [("visual", "self", FROST_HAND)]), ("every", 37000, [("emote", "self", "spell")])]),
    dict(key="excavator", name="Naga Excavator", plural="naga excavators", look=18389, looks=[22874, 22876, 22869],
         equip=(3346, 0, 0), size=1.1, level=25, role="ambient", untouchable=True, phase=M5,
         at=["ex_1", "ex_2", "ex_3", "ex_4", "ex_5"],
         idle=[("state", "self", "work"), ("every", 17000, [("sound", "self", PICK)])]),
    dict(key="host", name="Myrmidon of Serena's Host", plural="myrmidons of Serena's host", look=18398, looks=[18389],
         equip=(15910, 0, 0), size=1.2, level=28, role="ambient", untouchable=True, phase=M5,
         at=["host_1", "host_2", "host_3"], facing=4.2,
         idle=[("state", "self", "ready_thrown"), ("every", 5000, [("emote", "self", "attack2h"), ("sound", "self", "naga_attack")])]),
    dict(key="host_siren", name="Siren of Serena's Host", equip=(0, 0, 2550), look=18386, size=1.05, level=27,
         role="ambient", untouchable=True, phase=M5, at="host_siren", facing=4.1,
         idle=[("state", "self", "ready_bow"), ("every", 6000, [("emote", "self", "spell"), ("visual", "self", FROST_HAND)])]),
    dict(key="watcher", name="Watcher", plural="Watchers", look="warden", looks=["warden_2", "warden_3", "warden_4"],
         equip=(5598, 5598, 0), level=(25, 27), side="hostile", role="enemy", language="universal", phase=M5, respawn=40,
         abilities=[(22887, 8000)], at=["w_1", "w_2", "w_3", "w_4", "w_5", "w_6", "w_7", "w_8"], facing=1.0),
    dict(key="watcher_sentinel", name="Watcher Sentinel", plural="Watcher Sentinels", look=4841, looks=[4842, 4843, 4844],
         equip=(3432, 0, 2550), level=(26, 27), side="hostile", role="enemy", language="universal", phase=M5, respawn=40,
         abilities=[(6660, 5000)], at=["s_1", "s_2", "s_3", "s_4", "s_5"], facing=1.0),
    # the runner, her boat, and the naga who close the water behind her (4.06)
    dict(key="runner", name="Maiev's Runner", equip=(3432, 0, 0), speed=1.4, look=4842, size=0.95, level=26,
         role="ambient", untouchable=True, language="universal", summoned=True),
    dict(key="runner_boat", name="Watchers' Transport", look=ROWBOAT, scale=1.2, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),
    dict(key="host_swimmer", name="Myrmidon of Serena's Host", equip=(15910, 0, 0), look=18389, size=1.15, level=28,
         role="ambient", untouchable=True, summoned=True),
    dict(key="host_swimmer_2", name="Myrmidon of Serena's Host", equip=(15910, 0, 0), look=18398, size=1.15, level=28,
         role="ambient", untouchable=True, summoned=True),
    dict(key="host_swimmer_3", name="Siren of Serena's Host", look=18386, size=1.05, level=27, role="ambient",
         untouchable=True, summoned=True),
    # a Watcher tent on fire (4.07)
    dict(key="tent_fire", name="Burning Tent", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 3000, [("visual", "self", FIRE), ("visual", "self", BURNING)])]),

    # -- memory m6: Balancing the Scales (Szaria's) -----------------------------------------------------------------
    dict(key="serpentra", name="Lady Serpentra", subname="Sea Witch of Illidan's Host", look=18392, equip=(1907, 0, 0),
         size=1.35, level=40, role="ambient", untouchable=True, language="universal", at="serpentra", facing=0.93, phase=M6,
         gossip="Stand on my dune, little siren, and watch the land-walkers come. They always come.",
         # the landing (4.11): whoever climbs her dune sees the fleet come in
         watch=(10, [("music", 3900), ("face", "self", "lshore_1"), ("emote", "self", "omnicast"),
                     ("summon", "landing_boat", "lboat_1", 70), ("summon", "landing_boat_2", "lboat_2", 70), ("wait", 600),
                     ("move", "landing_boat", "lshore_1", "walk"), ("move", "landing_boat_2", "lshore_2", "walk"),
                     ("wait", 7500),
                     ("summon", "malfurion", "malf_land", 70), ("summon", "tyrande", "tyr_land", 70),
                     ("sound", "self", "splash"), ("wait", 800),
                     ("move", "malfurion", "malf_ashore", "walk"), ("move", "tyrande", "tyr_ashore", "walk"), ("wait", 5000),
                     ("face", "tyrande", "spawning_ground"),
                     ("yell", "tyrande", "Sentinels, attack!", "point", "TyrandeWarcry1"),
                     ("summon", "landing_sentinel", "lsen_1", 22), ("summon", "landing_sentinel_2", "lsen_2", 22),
                     ("summon", "landing_sentinel_3", "lsen_3", 22), ("wait", 500),
                     ("move", "landing_sentinel", "lsen_to_1", "run"), ("move", "landing_sentinel_2", "lsen_to_2", "run"),
                     ("move", "landing_sentinel_3", "lsen_to_3", "run"), ("wait", 3000),
                     ("face", "malfurion", "spawning_ground"),
                     ("say", "malfurion", "Our sins have returned to haunt us.", "talk", "MalfurionPissed4"), ("wait", 4000),
                     ("say", "malfurion", "I don't know, but these creatures feel familiar somehow.", "talk"), ("wait", 4500),
                     ("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro"),
                     ("yell", "self", "Wretched night elves! We are the naga! We are the future.", "battle_roar"),
                     ("emote", "guard_m6", "battle_roar"), ("sound", "guard_m6", "naga_aggro"), ("wait", 4000),
                     ("credit", "ch4_landing"),
                     ("move", "malfurion", "elves_away", "walk"), ("move", "tyrande", "elves_away", "walk")], 120000),
         idle=[("every", 15000, [("emote", "self", "omnicast"), ("visual", "self", GLOW_GREEN)])]),
    dict(key="guard_m6", name="Spawnguard of Serpentra", equip=(15910, 0, 0), plural="Serpentra's spawnguards", look=18389,
         looks=[18398, 22877], size=1.2, level=28, role="ambient", untouchable=True, phase=M6,
         at=["guard_m6_1", "guard_m6_2", "guard_m6_3"], facing=0.8,
         idle=[("state", "self", "ready_thrown"), ("every", 47000, [("emote", "self", "roar")])]),
    dict(key="giant", name="Mountain Giant", plural="Mountain Giants", look=12813, looks=[12814, 1918], level=(27, 28),
         side="hostile", role="enemy", type="giant", health=1.8, phase=M6, respawn=45, abilities=[(8078, 14000)],
         at=["g_1", "g_2", "g_3", "g_4"], facing=0.3),
    dict(key="sentinel", name="Sentinel", plural="Sentinels", look=2306, looks=[4841], equip=(5598, 0, 2550),
         level=(27, 29), side="hostile", role="enemy", language="universal", phase=M6, respawn=40, abilities=[(6660, 5000)],
         at=["sen_1", "sen_2", "sen_3", "sen_4", "sen_5"], facing=3.9),
    dict(key="huntress", name="Huntress", plural="Huntresses", look=4843, looks=[4844], equip=(5598, 5598, 0),
         level=(27, 29), side="hostile", role="enemy", language="universal", phase=M6, respawn=40, abilities=[(22887, 7000)],
         at=["hu_1", "hu_2", "hu_3"], facing=3.9),
    # the canon figures who come for a scene (untouchable: bible 3.4)
    dict(key="malfurion", name="Malfurion Stormrage", equip=(13339, 0, 0), subname="Archdruid", look="malfurion",
         size=1.25, level=40, role="ambient", untouchable=True, language="universal", summoned=True),
    dict(key="tyrande", name="Tyrande Whisperwind", equip=(5598, 0, 14105), subname="High Priestess of Elune",
         look="tyrande", size=1.05, level=40, role="ambient", untouchable=True, language="universal", summoned=True,
         gossip="Stand aside, naga. My quarrel is with him."),
    dict(key="illidan", name="Illidan Stormrage", subname="The Betrayer", look="illidan", equip=(32632, 32633, 0),
         size=1.1, level=40, role="ambient", untouchable=True, language="universal", summoned=True,
         idle=[("every", 8000, [("visual", "self", FEL_SMOKE)])]),
    dict(key="maiev", name="Maiev Shadowsong", equip=(32425, 32425, 0), subname="Warden", look="maiev", size=1.0,
         level=40, role="ambient", untouchable=True, language="universal", summoned=True),
    dict(key="landing_boat", name="Night Elf Boat", look=ROWBOAT, scale=1.3, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),
    dict(key="landing_boat_2", name="Night Elf Boat", look=ROWBOAT, scale=1.3, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),
    dict(key="landing_sentinel", name="Sentinel", look=2306, equip=(5598, 0, 2550), level=28, role="ambient",
         untouchable=True, language="universal", summoned=True),
    dict(key="landing_sentinel_2", name="Sentinel", look=4841, equip=(5598, 0, 2550), level=28, role="ambient",
         untouchable=True, language="universal", summoned=True),
    dict(key="landing_sentinel_3", name="Huntress", look=4843, equip=(5598, 5598, 0), level=28, role="ambient",
         untouchable=True, language="universal", summoned=True),
]

OBJECTS = [
    # -- the present: the Hollow ----------------------------------------------------------------------------------
    dict(key="open_shell", model=GIANT_CLAM_OPEN, name="Open Parley-Shell", kind="doodad", scale=0.55),
    dict(key="shell_pearl", model="great_pearl", name="Song-Pearl", kind="doodad", scale=0.1),
    dict(key="shut_shell", model=GIANT_CLAM_SHUT, name="Closed Parley-Shell", kind="doodad", scale=0.5),
    dict(key="valormok_banner", model=HORDE_BANNER, name="Valormok's Banner", at="hollow_banner", kind="doodad",
         facing=3.1, phase=ENVOY),
    dict(key="marked_rock", model=ROCK, name="Trident-Scarred Rock", at=["rock_1", "rock_2", "rock_3"], kind="doodad",
         scale=0.35),
    dict(key="sea_glass", model=CRYSTAL, name="Sea-Glass", kind="loot", loot=[("lens", 1, 1)], quest="ch4_lenses",
         scale=0.18, respawn=45, phase=HOLLOW,
         at=["glass_1", "glass_2", "glass_3", "glass_4", "glass_5", "glass_6", "glass_7", "glass_8"]),
    dict(key="kelp_bed", model=KELP, name="Long Kelp", kind="loot", loot=[("long_kelp", 1, 2)], quest="ch4_kelp",
         scale=1.5, respawn=40, phase=HOLLOW,
         at=["kelp_1", "kelp_2", "kelp_3", "kelp_4", "kelp_5", "kelp_6", "kelp_7", "kelp_8"]),
    dict(key="lens", model=CRYSTAL, name="Sea-Glass Lens", kind="doodad", scale=0.12),
    dict(key="kelp_blanket", model=SEAWEED, name="The Kelp Blanket", kind="doodad", scale=2.4),
    dict(key="sand_line", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.4),
    # -- the present: Southridge Beach ---------------------------------------------------------------------------
    dict(key="colours", model="naga_banner", name="Serpentra's Colours", at=["colours_1", "colours_2"], kind="doodad",
         facing=1.0, scale=1.2, phase=HOLLOW),
    dict(key="cache", model=DIRT, name="Disturbed Sand", kind="loot", loot=[("priestess_pearl", 1, 1)],
         quest="ch4_priestess_pearl", scale=0.8, respawn=30, at="cache", phase=HOLLOW),
    # -- the present: Shadowsong Shrine --------------------------------------------------------------------------
    dict(key="pillar", model=NE_RUIN, name="Broken Pillar", at="pillar", kind="doodad", scale=0.7, facing=5.6),
    dict(key="flowers", model=FLOWERS, name="Flowers", at="flowers", kind="doodad", scale=0.8),
    dict(key="fire", model=CAMPFIRE, name="Shaelyn's Fire", at="shaelyn_fire", kind="doodad", scale=0.9),
    dict(key="glaive_pillar", model=NE_GLAIVE, name="Broken Watcher's Glaive", kind="use", quest="ch4_glaive",
         consumable=True, respawn=120, at="glaive_on_pillar", facing=2.4, goal="Watcher's glaive taken from the pillar",
         beats=[("give", "glaive", 1), ("sound", "player", 1193), ("wait", 7000),
                ("state", "ch2:shaelyn", "none"), ("face", "ch2:shaelyn", "pillar"), ("wait", 1500),
                ("move", "ch2:shaelyn", "pillar_front", "run"), ("wait", 3500), ("emote", "ch2:shaelyn", "exclamation"),
                ("sound", "ch2:shaelyn", ELF_SCREAM), ("wait", 1800), ("face", "ch2:shaelyn", "shrine_dark"),
                ("yell", "ch2:shaelyn", "Maiev! MAIEV! You left me the ashes and now they take the ashes too!", "rude"),
                ("sound", "ch2:shaelyn", ELF_WOUND), ("wait", 3500), ("emote", "ch2:shaelyn", "cry"), ("sound", "ch2:shaelyn", ELF_CRY),
                ("wait", 3000), ("move", "ch2:shaelyn", "shaelyn", "walk"), ("wait", 4500), ("face", "ch2:shaelyn", "shaelyn_fire"),
                ("state", "ch2:shaelyn", "sit")]),
    # what Shaelyn draws in the sand (4.18): a burning house, a long shape carrying a small one
    dict(key="draw_house", model=NE_TENT, name="Drawing in the Sand", kind="doodad", scale=0.1),
    dict(key="draw_fire", model=CAMPFIRE, name="Drawing in the Sand", kind="doodad", scale=0.22),
    dict(key="draw_long", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.3),
    dict(key="draw_small", model=SHELL, name="Drawing in the Sand", kind="doodad", scale=0.3),
    # -- the present: Valormok, the envoy's tent (4.20 on) ------------------------------------------------------
    dict(key="envoy_tent", model="naga_pagoda", name="The Envoy's Tent", at="envoy_tent", kind="doodad", scale=0.8,
         facing=2.9, phase=ENVOY),
    dict(key="envoy_banner", model="naga_banner", name="Banner of the Tide-Broken", at="envoy_banner", kind="doodad",
         facing=2.9, phase=ENVOY),
    dict(key="envoy_torch", model="naga_torch", name="Naga Torch", at=["envoy_torch_1", "envoy_torch_2"], kind="doodad",
         phase=ENVOY),
    dict(key="envoy_crate", model="naga_crate", name="Crate of Coral", at="envoy_crate", kind="doodad", facing=0.5,
         phase=ENVOY),
    dict(key="envoy_jar", model="naga_jar", name="Seawater Jar", at="envoy_jar", kind="doodad", phase=ENVOY),

    # -- memory m5 ------------------------------------------------------------------------------------------------
    dict(key="dig_site", model=DIRT, name="Dig Site", kind="loot", loot=[("relic", 1, 1)], quest="ch4_dig", scale=0.7,
         respawn=30, phase=M5, at=["dig_1", "dig_2", "dig_3", "dig_4", "dig_5", "dig_6", "dig_7", "dig_8"]),
    dict(key="dig_tablet", model=TABLET, name="Kaldorei Tablet", kind="doodad", scale=0.6, phase=M5,
         at=["dig_2", "dig_5", "dig_7"]),
    dict(key="m5_crate", model="naga_crate", name="Crate of Relics", kind="doodad", phase=M5,
         at=["m5_crate_1", "m5_crate_2"]),
    dict(key="m5_weapons", model="naga_weapons", name="Excavators' Tools", kind="doodad", phase=M5, at="m5_weapons"),
    dict(key="tent_1", model=NE_TENT, name="Watcher Tent", kind="use", quest="ch4_fury", consumable=True, respawn=90,
         at="tent_1", facing=1.2, phase=M5, goal="West tent burned",
         beats=[("summon", "tent_fire", "tent_1", 60), ("sound", "player", 38), ("face", "serena_young", "tent_1"),
                ("state", "serena_young", "none")]),
    dict(key="tent_2", model=NE_TENT_2, name="Watcher Tent", kind="use", quest="ch4_fury", consumable=True, respawn=90,
         at="tent_2", facing=0.6, phase=M5, goal="North tent burned",
         beats=[("summon", "tent_fire", "tent_2", 60), ("sound", "player", 38), ("face", "serena_young", "tent_2"),
                ("state", "serena_young", "none")]),
    dict(key="tent_3", model=NE_TENT, name="Watcher Tent", kind="use", quest="ch4_fury", consumable=True, respawn=90,
         at="tent_3", facing=2.1, phase=M5, goal="East tent burned",
         beats=[("summon", "tent_fire", "tent_3", 60), ("sound", "player", 38), ("face", "serena_young", "tent_3"),
                ("state", "serena_young", "none")]),
    dict(key="m5_lantern", model=NE_LANTERN, name="Lantern", kind="doodad", phase=M5, at=["lantern_1", "lantern_2"]),
    dict(key="m5_banner", model=NE_BANNER, name="Banner of the Watchers", kind="doodad", facing=1.6, phase=M5,
         at="m5_banner"),
    dict(key="pillars", model=NE_RUIN_TALL, name="The Pillars of Aszune", kind="doodad", scale=2.6, phase=M5,
         at=["pillar_1", "pillar_2"]),

    # -- memory m6 ------------------------------------------------------------------------------------------------
    dict(key="fleet", model=NE_SHIP, name="Night Elf Transport", kind="doodad", phase=M6, at=["ship_1", "ship_2"],
         facing=3.6),
    dict(key="m6_banner", model="naga_banner", name="Serpentra's Colours", kind="doodad", facing=0.9, scale=1.2, phase=M6,
         at=["m6_banner_1", "m6_banner_2"]),
    dict(key="m6_torch", model="naga_torch", name="Naga Torch", kind="doodad", phase=M6, at=["m6_torch_1", "m6_torch_2"]),
    dict(key="m6_coral", model=CORAL_TREE, name="Spawning Coral", kind="doodad", scale=1.1, phase=M6,
         at=["m6_coral_1", "m6_coral_2"]),
    dict(key="m6_egg", model=EGG, name="Naga Eggs", kind="doodad", scale=0.5, phase=M6, at=["m6_egg_1", "m6_egg_2",
         "m6_egg_3"]),
]

ITEMS = [
    # what quests ask for and hand over
    dict(key="szaria_pearl", name="Song-Pearl: Scarscale's Water", icon="item:5500",
         description="It hums. Szaria won't look at it. It came back in a herald's open shell, like a gift."),
    dict(key="relic", name="Kaldorei Relic", icon="item:5360", stack=8,
         description="Night elf silver, ten thousand years under the sea."),
    dict(key="relic_bag", name="Bag of Relics", icon="item:5424",
         description="Eight relics in a wet sack. The cup with the drillmaster's face is on top."),
    dict(key="priestess_pearl", name="Song-Pearl: The Priestess", icon="item:5500",
         description="Dug out of a Spitelash cache under Serpentra's old colours. It hums like a cracked bell."),
    dict(key="net", name="Weighted Net", icon=7914,
         description="A shark net, knotted by sirens. Throw it when he gives the sign."),
    dict(key="closed_shell", name="Closed Parley-Shell", icon="item:5524",
         description="Shut tight. The talking is over."),
    dict(key="banner_item", name="Valormok's Banner", icon="item:18607",
         description="Red, black and heavy. Ag'tor didn't say a word as he handed it over."),
    dict(key="lens", name="Sea-Glass Lens", icon="item:774", stack=6, description="Smoothed by the sea, clear as an eye."),
    dict(key="long_kelp", name="Long Kelp", icon="item:3820", stack=10, description="Thick, long, and slimy. Very slimy."),
    # kept: chapter 5's 5.14 breaks the Unsingers' ward with whichever the player has
    dict(key="moonstone_arrows", name="Shaelyn's Moonstone Arrows", icon="item:2512",
         description="Night elf arrows with heads of moonstone. Shaelyn pushed them into your hands without looking at you."),
    dict(key="glaive", name="Broken Watcher's Glaive", icon="item:32407",
         description="Dropped on the road out of Nendis. A warden's blade remembers who it was made to cut."),

    # rewards (the game's quests' greens at these levels)
    dict(key="pillar_mantle", name="Pillar-Watch Mantle", kind="armor:cloth:shoulder", quality=2, level=26,
         stats=[("int", 6), ("spi", 4)]),
    dict(key="strand_leggings", name="Strandrunner's Leggings", kind="armor:leather:legs", quality=2, level=26,
         stats=[("agi", 8), ("sta", 6)]),
    dict(key="excavator_girdle", name="Excavator's Girdle", kind="armor:mail:waist", quality=2, level=26,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="netcaster_bow", name="Netcaster's Longbow", kind="weapon:bow", quality=2, level=28, stats=[("agi", 5),
         ("sta", 3)]),
    dict(key="spawnguard_trident", name="Spawnguard's Trident", kind="weapon:spear", quality=2, level=28,
         stats=[("str", 12), ("sta", 9)]),
    dict(key="coral_staff", name="Serpentra's Coral Staff", kind="weapon:staff", quality=2, level=28,
         stats=[("int", 12), ("spi", 9)]),
    dict(key="ghostwatch_ring", name="Ghostwatch Ring", kind="ring", quality=2, level=28, stats=[("sta", 4), ("spi", 4)],
         description="Shaelyn tossed it into the sand at your tail. It was on one of the ghosts. She says."),
    dict(key="harborsong_cloak", name="Harborsong Cloak", kind="armor:cloth:back", quality=2, level=29,
         stats=[("agi", 4), ("sta", 4)], description="Green wool, mended many times. It smells of woodsmoke."),
    dict(key="herald_slippers", name="Herald-Breaker's Slippers", kind="armor:cloth:feet", quality=2, level=29,
         stats=[("int", 6), ("spi", 5)]),
    dict(key="tidebreaker_boots", name="Tidebreaker Boots", kind="armor:leather:feet", quality=2, level=29,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="lancer_boots", name="Lancer-Scale Boots", kind="armor:mail:feet", quality=2, level=29,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="counting_stone", name="Mrgl's Counting Stone", kind="trinket", quality=2, level=29, stats=[("sta", 4),
         ("spi", 3)],
         description="Five notches. Mrgl says six."),
    dict(key="snapper_claw", name="Snapper Claw Meat", kind="food", level=25, icon="item:5524"),
    dict(key="thessa_glass", name="Thessa's Sea-Glass", kind="offhand", quality=2, level=29, stats=[("int", 5), ("spi", 4)],
         description="Hold it up to the light. The light holds back."),
    dict(key="blanket_corner", name="A Corner of the Kelp Blanket", kind="armor:cloth:back", quality=2, level=29,
         stats=[("sta", 5), ("spi", 3)], description="Vyssa had some left over. It's still slimy."),
    dict(key="turned_robe", name="Robe of the Turned Tide", kind="armor:cloth:chest", quality=2, level=29,
         stats=[("int", 9), ("sta", 6), ("spi", 5)]),
    dict(key="turned_jerkin", name="Jerkin of the Turned Tide", kind="armor:leather:chest", quality=2, level=29,
         stats=[("agi", 10), ("sta", 9)]),
    dict(key="turned_hauberk", name="Hauberk of the Turned Tide", kind="armor:mail:chest", quality=2, level=29,
         stats=[("str", 10), ("sta", 9)]),
]

MEMORIES = [
    dict(key="m5", name="Wrath of the Betrayer", whose="Szaria", bit="B",
         text="Lady Szaria's memory, sung out of her by Serena Scarscale and sent back as a taunt: the Broken Isles, "
              "under Scarscale's command. What she saw, you see.",
         stage="m5_arrive", facing=4.25, centre="m5_centre", radius=220, pool="hollow_pool", pool_facing=0.83,
         singer="ch0:isshara", again="Sing Szaria's song again. Send me back to the Broken Isles."),
    dict(key="m6", name="Balancing the Scales", whose="Szaria", bit="A",
         text="Lady Szaria's memory: the beach where the night elves came across the sea for Illidan. What she saw, you see.",
         stage="m6_arrive", facing=0.75, centre="m6_centre", radius=150, pool="hollow_pool", pool_facing=0.83,
         singer="ch0:isshara", again="Sing the Priestess again. Send me back to Serpentra's beach."),
]

QUESTS = [
    # 4.01: the herald under the open shell (a set piece)
    dict(key="ch4_herald", title="The Herald", giver="ch0:szaria", ender="ch0:szaria", level=25, xp=8, tone="serious",
         prev="ch3:ch3_end", event="The herald's offer heard",
         goal="Stand with Lady Szaria at the Hollow's south waterline while the Spitelash herald speaks under the open shell.",
         text="Conches, out past the reef. Two long and one short: parley, the old way, the way Vashj's people did it before "
              "the Spitelash forgot there was any other way to talk. Someone has come under an open shell. Stand with me at "
              "the water and keep your trident down. Whatever she offers, I answer. Not you.",
         progress="She's still at the water. Waiting. They're very good at waiting.",
         reward="A pardon. As if remembering was the crime. ...And a present, the way you leave a fish for a cat you mean "
                "to drown. That pearl in the shell hums like something I lost. Don't touch it. Not yet.",
         details=["talk", "battle_roar"], reward_emotes=["talk"],
         accept=[("face", "self", "sea_south"), ("sound", "self", HORN), ("wait", 900), ("sound", "self", HORN), ("wait", 1600),
                 ("emote", "self", "talk"), ("say", "self", "Under an open shell. Tridents down, all of you.", "talk"),
                 ("summon", "herald", "herald_rise", 75), ("summon", "herald_guard", "guard_rise_1", 75),
                 ("summon", "herald_guard_2", "guard_rise_2", 75), ("wait", 500), ("sound", "herald", SPLASH_BIG),
                 ("visual", "herald", WATER), ("wait", 1200),
                 ("move", "herald", "herald_sand", "walk"), ("move", "herald_guard", "guard_sand_1", "walk"),
                 ("move", "herald_guard_2", "guard_sand_2", "walk"), ("move", "self", "szaria_down", "walk"), ("wait", 5500),
                 ("face", "herald", "szaria_down"), ("emote", "herald", "omnicast"), ("visual", "herald", GLOW_BLUE),
                 ("wait", 1500),
                 ("say", "herald", "Lady Szaria. The envoy of the Empress has heard of your hollow, and of what you keep in it.",
                  "talk"), ("wait", 5000),
                 ("say", "herald", "She offers pardon. Every renegade on this sand may swim home to the tide, forgiven, "
                                   "and sing the creed again. The price is one blind old witch.", "talk"), ("wait", 7000),
                 ("face", "self", "hollow_inland"), ("wait", 4000),
                 ("say", "herald", "She thought you would answer so. She sends a gift, then, so the answer costs you something.",
                  "spell"), ("wait", 4500),
                 ("emote", "herald", "work"), ("object", "open_shell", "shell_sand", 180), ("object", "shell_pearl", "shell_sand", 180),
                 ("visual", "herald", GLOW_BLUE), ("wait", 2500),
                 ("move", "herald", "herald_away", "walk"), ("move", "herald_guard", "herald_away", "walk"),
                 ("move", "herald_guard_2", "herald_away", "walk"), ("credit", "ch4_herald"), ("wait", 4000),
                 ("despawn", "herald"), ("despawn", "herald_guard"), ("despawn", "herald_guard_2"), ("face", "self", "shell_sand")],
         complete=[("face", "self", "shell_sand"), ("wait", 2000), ("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro"),
                   ("wait", 2000), ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500),
                   ("move", "self", "ch1:hollow_szaria", "walk")],
         poi=["herald_sand"]),

    # 4.02: the herald's gift is Szaria's own memory; Isshara sings it (into m5)
    dict(key="ch4_pearl", title="Szaria's Pearl", giver="ch0:szaria", ender="ch0:szaria_young", level=25, xp=8,
         tone="serious", prev="ch4_herald", memory="m5", source="szaria_pearl",
         use=[("szaria_pearl", "ch0:isshara", 1, [("face", "self", "player"), ("visual", "self", WATER), ("wait", 5500),
                                                 ("emote", "self", "omnicast"), ("wait", 1500), ("state", "self", "channel"),
                                                 ("sound", "self", "siren_hiss"), ("music", 9461), ("visual", "player", GLOW_BLUE),
                                                 ("wait", 3500), ("relive", "m5"), ("wait", 2000), ("state", "self", "none")])],
         goal="Carry Song-Pearl: Scarscale's Water to Isshara at her pool in the Hollow and give it to her. In the memory "
              "she sings, find young Szaria at the dig on the Broken Isles.",
         text="Serena Scarscale. That's the envoy's name, the one the Empress sent to Rethress. I served under her on the "
              "Broken Isles, before she swam home and I didn't. That pearl is mine. She sang it out of me, and now she sends "
              "it back to show me she can. I won't touch it. You carry it to the keeper. Let Isshara decide whether it's a "
              "gift or a hook.",
         progress="Still holding it? It doesn't bite. Take it to Isshara.",
         reward="There you are. Stop gawking at the sky; it's the same sky as Azshara's with more rocks under it. Grab a "
                "trowel. Scarscale wants the old elves' treasure out of the mud before the warden's people stop limping.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "shell_sand"), ("wait", 1500), ("emote", "self", "talk"),
                 ("say", "self", "Serena Scarscale.", "talk"), ("wait", 2500), ("face", "self", "hollow_inland"),
                 ("wait", 2000), ("emote", "self", "spell"), ("face", "self", "hollow_pool"), ("wait", 1500),
                 ("face", "ch0:isshara", "hollow"), ("visual", "ch0:isshara", WATER), ("sound", "ch0:isshara", "pickup_water")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "laugh"), ("wait", 1500),
                   ("face", "self", "serena_rock"), ("emote", "self", "point"), ("wait", 1500), ("state", "self", "work")],
         poi=["hollow_pool", "szaria_dig"]),

    # 4.03: the dig (boring); Szaria complains, the sea witch watches from her rock
    dict(key="ch4_dig", title="Dig Sites", giver="ch0:szaria_young", ender="ch0:szaria_young", level=25, xp=8,
         tone="boring",
         prev="ch4_pearl", memory="m5", items=[("relic", 8)],
         goal="In Szaria's memory, dig 8 Kaldorei Relics out of the dig sites along the strand.",
         text="Dig, they said. The Broken Isles came up out of the sea full of the Highborne's treasures, they said. "
              "Scarscale wants every carved stone and silver cup out of the mud before Lord Illidan comes back out of that "
              "tomb. Eight pieces. I'm a siren, not a mole. Neither are you, from the look of your claws, but here we are.",
         progress="Eight. The mud doesn't care how long your hair is.",
         reward="Eight. One of them's a cup with a face on it that looks exactly like my old drillmaster. Keep that one on "
                "top of the bag.",
         details=["talk", "work"], reward_emotes=["laugh"],
         accept=[("state", "self", "work"), ("emote", "self", "talk"), ("sound", "self", PICK), ("wait", 2500),
                 ("say", "self", "Mud. Mud in my hair, mud in my scales. Ten thousand years under the sea and I end up in mud.",
                  "talk"), ("wait", 3500), ("emote", "excavator", "work"), ("sound", "excavator", PICK), ("wait", 1500),
                 ("state", "self", "none"), ("face", "self", "serena_rock"), ("wait", 2500), ("face", "self", "player"),
                 ("emote", "self", "shy"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "laugh"), ("wait", 1500), ("emote", "self", "eat_nosheathe"),
                   ("wait", 1200), ("face", "self", "serena_rock"), ("emote", "self", "point"), ("wait", 1500),
                   ("state", "self", "work")],
         poi=["digs"]),

    # 4.04: young Serena (a set piece: the look she gave you at the crèche)
    dict(key="ch4_serena", title="Serena", giver="ch0:szaria_young", ender="serena_young", level=26, xp=8, tone="serious",
         prev="ch4_dig", memory="m5", source="relic_bag",
         goal="In Szaria's memory, bring the Bag of Relics to the sea witch on the rock above the Watchers' camp.",
         text="The relics go to her. On the rock, above the Watchers' camp. Don't look at her too long. Don't look away too "
              "fast, either. She notices both. ...I'll come with you. I always find a reason to.",
         progress="She's waiting. She doesn't like waiting.",
         reward="You dig like a soldier, not a scholar. Good. Scholars stop to read.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "serena_rock"), ("emote", "self", "point"), ("wait", 2000),
                 ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "shy"), ("wait", 1200),
                 ("face", "self", "serena_rock")],
         complete=[("emote", "self", "work"), ("wait", 2500), ("face", "self", "player"), ("emote", "self", "spell"),
                   ("cast", "self", FROST_HAND, "player"), ("music", 6074), ("wait", 5500),
                   ("face", "ch0:szaria_young", "serena_rock"), ("state", "ch0:szaria_young", "none"),
                   ("face", "self", "szaria_dig"), ("emote", "self", "talk"), ("wait", 2000), ("visual", "self", FROST_HAND),
                   ("face", "self", "player"), ("say", "self", "Faster. The warden's runner is loose.", "talk"), ("wait", 3000),
                   ("face", "self", "camp")],
         poi=["serena_rock"]),

    # 4.05: the Watchers' camp under siege
    dict(key="ch4_watchers", title="The Watchers' Camp", giver="serena_young", ender="serena_young", level=26, xp=8,
         tone="serious", prev="ch4_serena", memory="m5", kill=[("watcher", 10)],
         goal="In Szaria's memory, kill 10 Watchers holding the landing at the Watchers' camp on the promontory.",
         text="The warden came back from the tomb half dead, and her Watchers have dug in on the promontory to get her "
              "message off this island. A runner, a boat, a word for her druid. There will be no word. Clear the landing. "
              "Ten of them. Szaria: cover them.",
         progress="I still see glaives on the sand.",
         reward="Ten. They fight like their warden: as if dying were an argument they could still win.",
         details=["talk", "spell"], reward_emotes=["talk"],
         accept=[("face", "self", "camp"), ("emote", "self", "spell"), ("visual", "self", LIGHTNING_NOVA), ("wait", 1500),
                 ("state", "ch0:szaria_young", "ready_bow"), ("face", "ch0:szaria_young", "camp"),
                 ("emote", "ch0:szaria_young", "spell"), ("visual", "ch0:szaria_young", FROST_HAND), ("wait", 1200),
                 ("emote", "host", "battle_roar"), ("sound", "host", "naga_aggro"), ("emote", "host_siren", "spell"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "camp"), ("emote", "self", "omnicast"), ("visual", "self", FROST_HAND), ("wait", 2000),
                   ("emote", "ch0:szaria_young", "salute"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")]),

    # 4.06: the runner (timed; history: she got through)
    dict(key="ch4_runner", title="The Runner", giver="serena_young", ender="serena_young", level=26, xp=8, tone="serious",
         prev="ch4_watchers", memory="m5", time=120, explore="the_pillars", radius=18,
         goal="In Szaria's memory, pursue Maiev's runner east along the promontory to the Pillars of Aszune at its tip, "
              "within 2 minutes.",
         text="There. The runner, out of the tents with a message rolled in her belt. She's making for a boat under the "
              "Pillars. If that boat reaches open water, the warden's druid will know where we are by the next moon. Run "
              "her down. Now.",
         progress="Where is she?",
         reward="Gone. Through the Pillars, into the dark water. ...It doesn't matter. Let them come. It's only a druid.",
         details=["battle_roar"], reward_emotes=["talk"],
         accept=[("face", "self", "runner_start"), ("emote", "self", "spell"),
                 ("summon", "runner", "runner_start", 40), ("summon", "runner_boat", "boat_wait", 60), ("wait", 600),
                 ("visual", "runner", SPRINT), ("move", "runner", "board_point", "run"),
                 ("say", "self", "There. Run her down!", "battle_roar"), ("move", "self", "serena_tip", "run"),
                 ("wait", 15000), ("despawn", "runner"), ("sound", "runner_boat", "splash"),
                 ("move", "runner_boat", "open_sea", "run"),
                 ("summon", "host_swimmer", "swim_1", 40), ("summon", "host_swimmer_2", "swim_2", 40),
                 ("summon", "host_swimmer_3", "swim_3", 40), ("wait", 600), ("move", "host_swimmer", "chase_1", "run"),
                 ("move", "host_swimmer_2", "chase_2", "run"), ("move", "host_swimmer_3", "chase_3", "run"), ("wait", 4000),
                 ("face", "self", "open_sea"), ("emote", "self", "spell"), ("cast", "self", LIGHTNING, "runner_boat"),
                 ("wait", 1500), ("visual", "self", LIGHTNING_NOVA), ("sound", "self", "siren_aggro"), ("wait", 1500),
                 ("cast", "self", LIGHTNING, "runner_boat"), ("wait", 2500), ("emote", "self", "battle_roar"),
                 ("wait", 6000), ("move", "self", "serena_rock", "walk")],
         complete=[("face", "self", "open_sea"), ("wait", 2500), ("visual", "self", FROST_HAND), ("face", "self", "player"),
                   ("emote", "self", "talk")],
         poi=["the_pillars"]),

    # 4.07: Serena's fury (the camp burned; she watches the fires, Szaria watches her); awake at the Hollow
    dict(key="ch4_fury", title="Serena's Fury", giver="serena_young", ender="ch0:szaria", level=26, xp=8, tone="serious",
         prev="ch4_runner", memory="m5", wake=True, kill=[("watcher_sentinel", 8)],
         objects=[("tent_1", 1), ("tent_2", 1), ("tent_3", 1)],
         goal="In Szaria's memory, kill 8 Watcher Sentinels and burn the 3 Watcher tents in their camp on the promontory.",
         text="Burn it. The tents, the bedrolls, the arrows, all of it. Every Watcher still standing, put down. If the "
              "warden ever comes back to this island she will find nothing here to come back to.",
         progress="...",
         reward="...I'd forgotten the smell. Wet canvas, burning. She stood on that rock and watched it like a sunset. And "
                "I stood beside her and watched her. Give me a moment.",
         details=["talk"], reward_emotes=["talk"], choice=["pillar_mantle", "strand_leggings", "excavator_girdle"],
         accept=[("face", "self", "camp"), ("state", "self", "none"), ("wait", 1500), ("emote", "self", "spell"),
                 ("visual", "self", FROST_HAND), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 1200), ("face", "self", "camp"), ("emote", "host", "battle_roar"), ("state", "ch0:szaria_young", "none"),
                 ("face", "ch0:szaria_young", "serena_rock")],
         complete=[("face", "self", "sea_south"), ("wait", 3000), ("emote", "self", "talk"), ("wait", 2000),
                   ("face", "self", "player"), ("emote", "self", "work")],
         poi=["camp"]),

    # 4.08: what she was (Szaria at the pool; Isshara's hand closes on her wrist)
    dict(key="ch4_what_she_was", title="What She Was", giver="ch0:szaria", ender="ch0:szaria", level=26, xp=8,
         tone="serious", prev="ch4_fury", event="Szaria's pearl kept",
         goal="Go with Lady Szaria to Isshara's pool and see what she does with her pearl.",
         text="I was hers. Not a soldier under her: hers. I fetched her water, I carried her orders, I stood where she could "
              "see me and hoped she would. When she swam home to the Empress she didn't ask me to come, and I told myself I'd "
              "have refused. The pearl remembers otherwise. Come with me. I want it out of my sight.",
         progress="Come on.",
         reward="She caught my wrist. Blind, and she caught it exactly. ...Fine. It stays on my belt. A thing you carry "
                "is a thing nobody can hand back to you as a gift.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("move", "self", "pool_side", "walk"), ("wait", 7500), ("face", "self", "hollow_pool"), ("emote", "self", "talk"),
                 ("face", "ch0:isshara", "pool_side"), ("wait", 1500), ("emote", "ch0:isshara", "spell"),
                 ("visual", "ch0:isshara", WATER), ("wait", 2000),
                 ("move", "self", "pool_edge", "walk"), ("wait", 3000), ("face", "self", "sea_east"),
                 ("emote", "self", "battle_roar"), ("wait", 700),
                 ("face", "ch0:isshara", "pool_edge"), ("emote", "ch0:isshara", "spell"), ("emote", "self", "stun"),
                 ("sound", "self", "siren_hiss"), ("wait", 3500), ("face", "self", "hollow_pool"), ("wait", 2000),
                 ("emote", "self", "work"), ("wait", 1500), ("credit", "ch4_what_she_was"),
                 ("move", "self", "ch1:hollow_szaria", "walk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "work"),
                   ("wait", 1500), ("face", "self", "sea_south")],
         poi=["hollow_pool"]),

    # 4.09: a Spitelash band under Serpentra's old colours
    dict(key="ch4_colours", title="Serpentra's Colours", giver="ch0:ssaveth", ender="ch0:ssaveth", level=27, xp=8,
         tone="serious", prev="ch4_what_she_was", kill=[("wavecaller", 12)],
         goal="Kill 12 Spitelash Wavecallers on Southridge Beach, across the Bay of Storms to the south.",
         text="Scouts saw a Spitelash band on Southridge Beach, digging in the wrecks for coral and steel. Green and gold on "
              "their banner. Old colours. Szaria went quiet when she heard. Twelve of their Wavecallers. Go south across the "
              "bay, and come back with fewer of them in the world.",
         progress="I'm counting tridents. Yours has been clean too long.",
         reward="Twelve. The banner's still standing? Leave it. Let them see it with nobody under it.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("state", "self", "none"), ("face", "self", "toward_southridge"), ("emote", "self", "work"), ("wait", 2500),
                 ("emote", "self", "attack2h"), ("sound", "self", 977), ("wait", 1500),
                 ("face", "ch0:szaria", "toward_southridge"), ("state", "ch0:szaria", "none"), ("wait", 2500),
                 ("face", "self", "player"), ("state", "self", "ready_thrown")],
         complete=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 2000), ("emote", "self", "attack2h"),
                   ("sound", "self", 977), ("wait", 1200), ("state", "self", "ready_thrown")],
         poi=["southridge"]),

    # 4.10: the Priestess pearl in the Wavecallers' cache
    dict(key="ch4_priestess_pearl", title="The Priestess Pearl", giver="ch0:szaria", ender="ch0:isshara", level=27, xp=8,
         tone="serious", prev="ch4_what_she_was", items=[("priestess_pearl", 1)],
         goal="Dig the pearl out of the Spitelash Wavecallers' buried cache at the eastern end of Southridge Beach and bring "
              "it to Isshara at the Hollow.",
         text="Those colours were Serpentra's. Lady Serpentra, who took me when Scarscale went home. I don't know where that "
              "band found her banner. I know what else they found: the keeper hears a pearl humming on Southridge, under the "
              "sand by the rocks. If it's another of mine I want it before the Empress sends it back with a bow on it.",
         progress="Under the sand. It hums like a cracked bell.",
         reward="The Priestess. I know this one. Szaria's again. She was on that beach when the druid came for Illidan. Sit, "
                "little one. Let me hold it a while before I sing.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "toward_southridge"), ("emote", "self", "spell"), ("wait", 2000), ("face", "self", "player"),
                 ("emote", "self", "talk"), ("wait", 1500), ("face", "ch0:isshara", "toward_southridge"),
                 ("emote", "ch0:isshara", "omnicast")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", WATER), ("wait", 2500), ("face", "self", "ch1:hollow_szaria"),
                   ("emote", "self", "talk"), ("face", "ch0:szaria", "hollow_pool"), ("wait", 2000), ("face", "self", "player")],
         poi=["cache"]),

    # 4.11: the night elves land (Isshara sings the Priestess: into m6)
    dict(key="ch4_landing", title="The Night Elves Land", giver="ch0:isshara", ender="ch0:szaria_young", level=27, xp=8,
         tone="serious", prev=["ch4_colours", "ch4_priestess_pearl"], memory="m6", event="The night elves' landing watched",
         goal="Touch the water while Isshara sings. In Szaria's memory, climb the dune to Lady Serpentra and watch the night "
              "elf fleet land on the beach.",
         text="Scarscale went home, and Serpentra took her. And then the night elves came across the sea in their ships, the "
              "druid and the priestess at the bow, to drag Illidan back to his cage. Put your hands in the water, little one. "
              "Stand on Serpentra's dune and watch them come.",
         progress="Up the dune. Lady Serpentra wants everyone to see this.",
         reward="Did you see the priestess? She looked at us like we were vermin in her garden. ...Serpentra's smiling. That's "
                "never good.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("sound", "self", "siren_hiss"), ("music", 9461), ("visual", "player", GLOW_BLUE), ("wait", 3500),
                 ("relive", "m6"), ("wait", 2000), ("state", "self", "none"), ("unaura", "player", GLOW_BLUE)],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "serpentra"),
                   ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player")],
         poi=["serpentra"]),

    # 4.12: the giants wake
    dict(key="ch4_giants", title="Giants Wake", giver="ch0:szaria_young", ender="ch0:szaria_young", level=27, xp=8,
         tone="serious", prev="ch4_landing", memory="m6", kill=[("giant", 4)],
         goal="In Szaria's memory, kill 4 Mountain Giants as they come down the cliffs to the west of the beach.",
         text="Look at the cliffs. The druid is talking to the rock, and the rock is answering. Mountain giants, old as the "
              "hills because they are the hills. They'll walk down onto the spawning ground and crush everything that "
              "hatches. Four of them. Put them back to sleep.",
         progress="The ground's still shaking.",
         reward="Four. Rocks again. I am never standing under a cliff again in my life.",
         details=["point"], reward_emotes=["cheer"],
         accept=[("face", "self", "cliff"), ("emote", "self", "point"), ("summon", "malfurion", "malfurion_cliff", 35),
                 ("wait", 1500), ("visual", "malfurion", NATURE), ("visual", "malfurion", GLOW_GREEN), ("wait", 2500),
                 ("music", 6077), ("visual", "giant", DUST), ("sound", "giant", GIANT_STEP), ("emote", "giant", "battle_roar"),
                 ("wait", 2000), ("emote", "self", "exclamation"), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "cheer"), ("wait", 1500), ("face", "self", "cliff"), ("emote", "self", "rude"),
                   ("wait", 1500), ("face", "self", "player")],
         poi=["cliff"]),

    # 4.13: hold Serpentra's spawning ground (the warden, far off)
    dict(key="ch4_base", title="Serpentra's Base", giver="ch0:szaria_young", ender="ch0:szaria_young", level=28, xp=8,
         tone="serious", prev="ch4_giants", memory="m6", kill=[("sentinel", 6), ("huntress", 4)],
         goal="In Szaria's memory, kill 6 Sentinels and 4 Huntresses on the beach before Serpentra's spawning ground.",
         text="They're coming for the spawning ground. The eggs, the young, the coral we sang up out of the sand. Serpentra "
              "says hold, so we hold. Ten of them: their Sentinels and their Huntresses. I'll be right behind you. Mostly.",
         progress="Hold!",
         reward="Ten, and the eggs are whole. ...Did you hear the warden out there? She wants to strike soon. They always "
                "want to strike soon.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("state", "self", "ready_bow"), ("face", "self", "beach_m6"), ("emote", "self", "battle_roar"),
                 ("emote", "guard_m6", "battle_roar"), ("sound", "guard_m6", "naga_aggro"), ("wait", 2500),
                 ("summon", "maiev", "maiev_far", 20), ("wait", 1500),
                 ("yell", "maiev", "We're wasting too much time. The longer we wait to attack, the stronger Illidan's forces "
                                   "become. We must strike soon, Shan'do!", "talk"),
                 ("wait", 3000), ("face", "self", "maiev_far"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "player"), ("state", "self", "none")],
         complete=[("emote", "self", "roar"), ("wait", 1500), ("face", "self", "spawning_ground"), ("wait", 1500),
                   ("emote", "self", "cheer"), ("face", "self", "player")],
         poi=["beach_m6"]),

    # 4.14: the net (a set piece)
    dict(key="ch4_net", title="The Net", giver="ch0:szaria_young", ender="ch0:szaria_young", level=28, xp=8, tone="serious",
         prev="ch4_base", memory="m6", source="net",
         interact=[("tyrande", "Throw the net over her.")], interact_goal="The priestess netted",
         interact_beats=[("take", "net", 1), ("visual", "self", NET), ("visual", "self", STUN_STARS), ("emote", "self", "wound"),
                         ("sound", "self", ELF_WOUND), ("wait", 2000), ("face", "illidan", "tyr_face"),
                         ("say", "illidan", "Not yet, my little priestess. A pity you couldn't see things my way. Now you--and "
                                            "the whole world--will understand just what I'm capable of! Ash Karath!", "spell"),
                         ("visual", "illidan", FEL_SMOKE), ("wait", 8000),
                         ("summon", "malfurion", "malf_arrive", 60), ("summon", "maiev", "maiev_arrive", 60), ("wait", 500),
                         ("move", "malfurion", "malf_stop", "run"), ("move", "maiev", "maiev_stop", "run"), ("wait", 3500),
                         ("face", "malfurion", "illidan_m6"), ("face", "maiev", "illidan_m6"),
                         ("yell", "malfurion", "How dare you!", "point", "MalfurionYesAttack2"), ("wait", 2500),
                         ("face", "illidan", "malf_stop"),
                         ("say", "illidan", "Brother! What are you doing here?", "talk"), ("wait", 3000),
                         ("say", "malfurion", "I've come to stop you, Illidan. Instead of banishing you, I should have returned "
                                              "you to your cage when I had the chance! I was weak then--but no longer.", "talk"),
                         ("wait", 8500),
                         ("say", "illidan", "I have sworn allegiance to a new master, brother. I have a great task to perform "
                                            "in his service. I'm sorry, but I cannot allow you to stand in my way.", "talk"),
                         ("wait", 7500), ("emote", "maiev", "talk"), ("music", 6078)],
         goal="In Szaria's memory, wait while Illidan speaks with Tyrande Whisperwind; when he gives the sign, throw the "
              "Weighted Net over her.",
         text="Lord Illidan is here, and the priestess is coming to him. She thinks he'll listen to her. He wants her taken, "
              "not killed. Here: a weighted net, the kind we use on sharks. Wait until they're done talking. When he gives the "
              "sign, throw it over her. Don't miss, and don't hurt her. He was very clear about the second part.",
         progress="Wait for the sign.",
         reward="You didn't miss. ...Did you see his face when she said she chose his brother? I've never seen anyone look "
                "like that and stay standing.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("despawn", "tyrande"), ("despawn", "illidan"), ("despawn", "malfurion"), ("despawn", "maiev"),
                 ("summon", "illidan", "illidan_m6", 150), ("summon", "tyrande", "tyr_arrive", 150), ("wait", 800),
                 ("face", "illidan", "tyr_arrive"), ("move", "tyrande", "tyr_face", "walk"), ("music", 5174),
                 ("face", "self", "illidan_m6"), ("emote", "self", "kneel"), ("wait", 9500),
                 ("face", "tyrande", "illidan_m6"),
                 ("say", "illidan", "Tyrande! What are you doing here? This battle does not concern you.", "talk"), ("wait", 4500),
                 ("say", "tyrande", "I was wrong to set you free, Illidan. I can see that now. You've become a monster.", "talk"),
                 ("wait", 5500),
                 ("say", "illidan", "Monster? Is that what you think of me? I have always... cared about you, Tyrande. I "
                                    "sought only to prove my worthiness--my power!", "talk"), ("wait", 7000),
                 ("say", "tyrande", "Raw power is no substitute for true strength, Illidan. That is why I chose your brother "
                                    "over you.", "talk"), ("wait", 6000),
                 ("say", "illidan", "Still you refuse to see me for what I truly am. You believe me to be a villain--your "
                                    "enemy. But soon now, you will see our enemies are the same!", "talk"), ("wait", 6500),
                 ("emote", "illidan", "omnicast"), ("visual", "illidan", FEL_SMOKE),
                 ("whisper", "self", "That's the sign. Now. The net.", "point")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "tyr_face"),
                   ("wait", 2000), ("face", "self", "player")],
         poi=["tyr_face"]),

    # 4.15: Ash Karath (Illidan sails; the druid holds the priestess; the fade): awake at the Hollow
    dict(key="ch4_ash_karath", title="Ash Karath", giver="ch0:szaria_young", ender="ch0:szaria", level=28, xp=8,
         tone="serious", prev="ch4_net", memory="m6", wake=True, kill=[("sentinel", 5), ("huntress", 3)],
         goal="In Szaria's memory, cover Illidan's going: kill 5 Sentinels and 3 Huntresses on the beach.",
         text="He's going. The boat's in the water, the druid's on the sand, and the warden is right behind them both. Cover "
              "him. Every night elf on this beach is one that doesn't reach his boat. Eight. Then we follow him into the sea.",
         progress="...",
         reward="I knotted that net myself. I'd forgotten. My hands hadn't. ...He didn't take her, you know. He left her in "
                "it, on the sand, for his brother to find, and sailed. I used to think that was cruel. Now I think it was the "
                "kindest thing he ever did.",
         details=["battle_roar"], reward_emotes=["talk"], choice=["netcaster_bow", "spawnguard_trident", "coral_staff"],
         accept=[("despawn", "tyrande"), ("despawn", "illidan"), ("despawn", "malfurion"), ("despawn", "maiev"),
                 ("summon", "illidan", "illidan_shore", 40), ("summon", "landing_boat", "iboat", 60),
                 ("summon", "malfurion", "malf_hold", 70), ("summon", "tyrande", "tyr_hold", 70), ("wait", 1000),
                 ("face", "illidan", "malf_hold"), ("visual", "illidan", FEL_SMOKE),
                 ("say", "illidan", "My brother will pay dearly for his betrayal.", "talk", "IllidanPissed4"), ("wait", 4000),
                 ("move", "illidan", "iboat", "walk"), ("state", "tyrande", "kneel"), ("visual", "tyrande", NET),
                 ("face", "malfurion", "tyr_hold"), ("state", "malfurion", "kneel"), ("wait", 4000),
                 ("despawn", "illidan"), ("sound", "landing_boat", "splash"), ("move", "landing_boat", "iboat_out", "walk"),
                 ("wait", 2000),
                 ("say", "malfurion", "Don't worry, my love. We'll find Illidan wherever he runs. We'll find him.", "talk"),
                 ("wait", 4500), ("face", "self", "beach_m6"), ("emote", "self", "battle_roar"),
                 ("emote", "guard_m6", "battle_roar"), ("sound", "guard_m6", "naga_aggro"), ("music", 6079)],
         complete=[("face", "self", "sea_south"), ("wait", 3000), ("emote", "self", "work"), ("wait", 2000),
                   ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["beach_m6"]),

    # 4.16: the woman at the shrine (her bow at forty yards: the shrine's watch, shrine_watch)
    dict(key="ch4_shrine", title="The Woman at the Shrine", giver="ch0:isshara", ender="ch2:shaelyn", level=28, xp=8,
         tone="serious", prev="ch4_ash_karath",
         goal="Find the night elf woman who leaves flowers at Shadowsong Shrine, on its hill south-west of Valormok above "
              "the Southfury River. If she draws on you, stop.",
         text="Someone leaves flowers at Shadowsong Shrine, the shrine with the warden's family name on it. Night elf flowers. "
              "I smell them on your scales every time you come back from the west. Go up to the shrine and find her. Don't "
              "draw on her. If she draws on you, stop where you are. She has more right to be afraid than you do.",
         reward="Stop there. ...No. Closer. Let me see you. I know your kind. I watched you come out of the sea and burn my "
                "home and swim away singing. I have lived on this hill for years, waiting to put an arrow through one of you. "
                "And now one of you comes up my hill like a guest. What do you want?",
         details=["talk"], reward_emotes=["rude"],
         accept=[("face", "self", "toward_shadowsong"), ("wait", 1500), ("visual", "self", WATER), ("sound", "self", "pickup_water"),
                 ("wait", 1500), ("visual", "self", WATER), ("wait", 1200), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("wait", 2500), ("emote", "self", "no"),
                   ("wait", 1500), ("face", "self", "pillar"), ("wait", 2500), ("face", "self", "player"),
                   ("emote", "self", "talk")],
         poi=["shaelyn"]),

    # 4.17: ghosts at Shadowsong (hero): the dark comes down and the Highborne rise; Shaelyn shoots one at your back
    dict(key="ch4_ghosts", title="Ghosts at Shadowsong", giver="ch2:shaelyn", ender="ch2:shaelyn", level=28, xp=8,
         tone="serious",
         path="hero", prev="ch4_shrine", kill=[("ghost", 10)], rep=[(69, 250)], rewards=["ghostwatch_ring"],
         goal="Kill 10 Restless Highborne as they rise around Shadowsong Shrine.",
         text="Every night they come up out of the stones. The Highborne: the ones your kind came from, and mine, if you "
              "believe the priests that we were one people once. They wail at the pillar where I lay my flowers. Kill them. "
              "Ten. I don't care that you're a naga. I care that they're quiet.",
         progress="They're still wailing. I can hear them from here.",
         reward="Quiet. ...I didn't shoot that one for you. It was in my way.",
         details=["point"], reward_emotes=["no"],
         accept=[("state", "self", "none"), ("music", 10896), ("face", "self", "shrine_dark"), ("emote", "self", "point"),
                 ("summon", "ghost", "ghost_1", 900), ("summon", "ghost", "ghost_2", 900), ("summon", "ghost", "ghost_3", 900),
                 ("summon", "ghost", "ghost_4", 900), ("wait", 1500), ("summon", "ghost", "ghost_5", 900),
                 ("summon", "ghost", "ghost_6", 900), ("summon", "ghost", "ghost_7", 900), ("summon", "ghost", "ghost_8", 900),
                 ("wait", 1500), ("summon", "ghost", "ghost_9", 900), ("summon", "ghost", "ghost_10", 900),
                 ("summon", "ghost", "ghost_11", 900), ("summon", "ghost", "ghost_12", 900),
                 ("summon", "ghost", "ghost_13", 900), ("summon", "ghost", "ghost_14", 900), ("sound", "ghost", 1172),
                 ("move", "self", "shaelyn_trees", "walk"), ("wait", 6000), ("state", "self", "ready_bow"), ("wait", 2500),
                 ("cast", "self", 6660, "ghost")],
         complete=[("state", "self", "none"), ("move", "self", "shaelyn", "walk"), ("wait", 6000), ("face", "self", "player"),
                   ("emote", "self", "no"), ("wait", 1500), ("face", "self", "shaelyn_fire"), ("state", "self", "sit")],
         poi=["shaelyn"]),

    # 4.18: what burned at Nendis (a drawing in the sand)
    dict(key="ch4_nendis", title="What Burned at Nendis", giver="ch2:shaelyn", ender="ch2:shaelyn", level=28, xp=8,
         tone="serious",
         prev="ch4_ghosts",
         event="Shaelyn's drawing watched",
         goal="Stay by Shaelyn Harborsong's fire and watch what she draws in the sand.",
         text="You want to know why I hate you. Sit. Watch my hands, not my face. I don't trust my voice with this.",
         progress="Look at it.",
         reward="Nendis. A harbour on the north coast, when the north coast had harbours. I was small. A long shape came "
                "through the fire and picked me up. I thought it was a demon. It carried me to the water and pushed me toward "
                "the hills, and I ran, and I never saw it again. I've hated every naga since, because I couldn't hate that one.",
         details=["talk"], reward_emotes=["cry"],
         accept=[("state", "self", "none"), ("face", "self", "drawing"), ("state", "self", "kneel"), ("wait", 1500),
                 ("object", "draw_house", "draw_house", 150), ("wait", 1500), ("object", "draw_fire", "draw_fire", 150),
                 ("wait", 1800), ("object", "draw_long", "draw_long", 150), ("wait", 1500),
                 ("object", "draw_small", "draw_small", 150), ("wait", 2500), ("state", "self", "none"),
                 ("face", "self", "drawing"), ("wait", 3000), ("face", "self", "player"), ("wait", 3000),
                 ("face", "self", "drawing"), ("wait", 2500), ("emote", "self", "no"), ("credit", "ch4_nendis"),
                 ("wait", 1500), ("face", "self", "player")],
         complete=[("face", "self", "drawing"), ("emote", "self", "cry"), ("sound", "self", ELF_CRY), ("wait", 3000),
                   ("face", "self", "shaelyn_fire"), ("state", "self", "sit")],
         poi=["drawing"]),

    # 4.19a: the keeper and the girl (hero): the blind keeper led up the hill
    dict(key="ch4_keeper", title="The Keeper and the Girl", giver="ch2:shaelyn", ender="ch2:shaelyn", level=29, xp=8,
         tone="serious", path="hero", exclusive=1, prev="ch4_nendis", rep=[(69, 500)],
         rewards=["moonstone_arrows", "harborsong_cloak"],
         interact=[("isshara_walk", "Take my arm. Up the hill, slowly.")], interact_goal="Isshara led up the hill",
         interact_beats=[("face", "self", "player"), ("visual", "self", WATER), ("wait", 1200), ("follow", "self"),
                         ("follow", "bearer")],
         goal="Find Isshara the Keeper at the foot of the trail south-west of the shrine, take her arm, and lead her up the "
              "hill to Shaelyn Harborsong by her fire.",
         text="You say your keeper was there, at Nendis. You say she remembers. Then bring her. Bring her up this hill where I "
              "can see her face. If she's lying, I'll know. If she isn't... bring her.",
         progress="Where is she?",
         reward="She said... Little Shae. Nobody alive has called me that. My mother did. And the thing in the smoke said it, "
                "over and over, while it carried me, so I wouldn't scream. Take these. They were for a naga's heart. Go now. "
                "Please. Both of you. Before I say something I'll have to mean.",
         details=["talk"], reward_emotes=["cry"],
         accept=[("state", "self", "none"), ("face", "self", "trail_foot"), ("emote", "self", "point"),
                 ("summon", "isshara_walk", "trail_foot", 900), ("summon", "bearer", "bearer_foot", 900), ("wait", 2500),
                 ("face", "self", "player"), ("emote", "self", "talk"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("state", "self", "ready_bow"), ("wait", 2500),
                   ("face", "isshara_walk", "shaelyn"), ("wait", 2500),
                   ("say", "isshara_walk", "Little Shae.", "talk"), ("music", 4517), ("wait", 3500),
                   ("state", "self", "none"), ("emote", "self", "cry"), ("sound", "self", ELF_CRY), ("wait", 2000),
                   ("state", "self", "kneel"), ("face", "isshara_walk", "trail_away"), ("wait", 3000),
                   ("move", "isshara_walk", "trail_foot", "walk"), ("move", "bearer", "bearer_foot", "walk"), ("wait", 6000),
                   ("face", "self", "shaelyn_fire"), ("state", "self", "sit")],
         poi=["trail_foot", "shaelyn"]),

    # 4.19b: the glaive in the ashes (menace): taken from the pillar behind her fire
    dict(key="ch4_glaive", title="The Glaive in the Ashes", giver="ch0:szaria", ender="ch0:szaria", level=29, xp=8,
         tone="serious", path="menace", exclusive=1, prev="ch4_nendis", rep=[(69, -500)], objects=[("glaive_pillar", 1)],
         goal="Take the Broken Watcher's Glaive from the pillar behind Shaelyn Harborsong's fire at Shadowsong Shrine, and "
              "bring word to Lady Szaria.",
         text="The night elf at Shadowsong keeps a broken glaive on her pillar. A Watcher's, dropped on the road out of Nendis "
              "when the warden ran after Illidan. Do you know what a warden's blade does to a sea witch's ward? It goes "
              "through it like kelp. The Unsingers ward themselves. I want that glaive. She sits by her fire with her back "
              "to the pillar. Be quick, and be gone before she turns round.",
         progress="The glaive.",
         reward="Hold it by the haft; the blade remembers who it was made to kill. ...You heard her? I think I heard her from "
                "here. Don't tell me about it.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "toward_shadowsong"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "player"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "sea_south")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "toward_shadowsong"),
                   ("wait", 2000), ("emote", "self", "work")],
         poi=["glaive_on_pillar"]),

    # 4.20: Valormok's banner (hero): the envoy's tent at Valormok from now on. Ag'tor is the game's: he has no scene of
    # his own (his quest window's gestures are his), and the banner's hanging is Szaria's.
    dict(key="ch4_envoy", title="Valormok's Banner", giver=8576, ender="ch0:szaria", level=29, xp=8, tone="serious",
         path="hero", prev="ch4_ash_karath", source="banner_item", items=[("banner_item", 1)], rep=[(76, 350)],
         goal="Take Valormok's Banner from Ag'tor Bloodfist to Lady Szaria at the Hollow.",
         text="Your people swim past my camp at night. My grunts throw spears at shadows. Sooner or later one of them hits. "
              "Take this to your lady. Hang it where my scouts can see it from the ridge. And tell her: one tent. At the edge "
              "of my camp. Small.",
         progress="A Horde banner. In your hand. Well?",
         reward="A Horde banner. On my sand. Vashj would have laughed until her coils shook. ...Put it there, beside the "
                "Empress's rag, where every Spitelash scout can see them both. And the orc will have his envoy. One tent. "
                "Small. Ssira will measure it twice.",
         details=["point", "salute"], reward_emotes=["talk", "roar"],
         complete=[("move", "self", "banner_front", "walk"), ("wait", 3000), ("face", "self", "hollow_banner"),
                   ("emote", "self", "work"), ("sound", "self", 1183), ("wait", 2000), ("visual", "self", WATER),
                   ("emote", "ch0:ssaveth", "battle_roar"), ("sound", "ch0:ssaveth", "naga_aggro"), ("wait", 2500),
                   ("face", "self", "player"), ("emote", "self", "talk"), ("move", "self", "ch1:hollow_szaria", "walk")],
         poi=["agtor", "hollow"]),

    # 4.21: the herald returns, with lancers (the offer withdrawn)
    dict(key="ch4_herald_returns", title="The Herald Returns", giver="ch0:szaria", ender="ch0:szaria", level=29, xp=8,
         tone="serious", prev="ch4_envoy", kill=[("thyssa", 1), ("lancer", 6)], items=[("closed_shell", 1)],
         drops={"closed_shell": [("thyssa", 100)]}, choice=["herald_slippers", "tidebreaker_boots", "lancer_boots"],
         goal="Kill Herald Thyssa and 6 Spitelash Lancers when they come out of the bay onto the Hollow's south shore, and "
              "bring Lady Szaria the Closed Parley-Shell.",
         text="Conches again. Not parley: war. She's back, the herald, and she hasn't brought an open shell this time. She's "
              "brought lancers. The envoy has had my answer, and this is hers. Meet them at the water. Bring me back whatever "
              "she's carrying.",
         progress="The herald. Is she in the sea or under it?",
         reward="Closed. The parley-shell, shut tight: that's how they say the talking's over. ...I'll wear it. Let every "
                "Spitelash who comes to this beach see what their envoy's pardon was worth.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("face", "self", "sea_south"), ("sound", "self", HORN), ("wait", 500), ("sound", "self", HORN), ("wait", 500),
                 ("sound", "self", HORN), ("music", 6077),
                 ("summon", "thyssa", "herald_rise", 300), ("summon", "lancer", "lancer_rise_1", 300),
                 ("summon", "lancer", "lancer_rise_2", 300), ("summon", "lancer", "lancer_rise_3", 300), ("wait", 800),
                 ("sound", "self", SPLASH_BIG),
                 ("yell", "thyssa", "The envoy withdraws her pardon, Szaria. You had your answer; this is hers. The tide "
                                    "always turns back.", "battle_roar"),
                 ("move", "thyssa", "herald_sand", "walk"), ("move", "lancer", "lancer_beach_1", "run"),
                 ("emote", "self", "battle_roar"), ("say", "self", "Tide-Broken! To the water!", "battle_roar"),
                 ("wait", 20000), ("summon", "lancer", "lancer_rise_4", 280), ("summon", "lancer", "lancer_rise_5", 280),
                 ("summon", "lancer", "lancer_rise_6", 280), ("sound", "self", "splash"), ("wait", 600),
                 ("move", "lancer", "lancer_beach_2", "run"), ("wait", 20000),
                 ("summon", "lancer", "lancer_rise_1", 260), ("summon", "lancer", "lancer_rise_2", 260),
                 ("sound", "self", "splash"), ("wait", 600), ("move", "lancer", "lancer_beach_3", "run")],
         complete=[("emote", "self", "work"), ("object", "shut_shell", "szaria_down", 30), ("wait", 2000), ("face", "self", "sea_south"),
                   ("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro"), ("emote", "ch0:ssaveth", "roar"),
                   ("emote", "ch0:vyssa", "roar"), ("wait", 2000), ("face", "self", "player")],
         poi=["herald_sand"]),

    # 4.22: the mur'gul runaways (Isshara hears Mrgl counting out on Hetaera's rock; he follows you home)
    dict(key="ch4_runaways", title="Mur'gul Runaways", giver="ch0:isshara", ender="ch0:isshara", level=29, xp=8,
         tone="funny", prev="ch4_herald_returns", rewards=["counting_stone"],
         interact=[("ch0:mrgl", "Swim behind me. Stay close, all of you.")], interact_goal="Mrgl and the runaways following",
         interact_beats=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("wait", 1200),
                         ("emote", "self", "point"), ("follow", "self"), ("follow", "runaway_1"), ("follow", "runaway_2"),
                         ("follow", "runaway_3"), ("follow", "runaway_4"), ("follow", "stowaway")],
         goal="Swim to the rock south-west of the Hollow, where Mrgl-Who-Counts hides with the runaway mur'gul, tell him to "
              "follow you, and bring them past the Spitelash patrols to Isshara.",
         text="Listen. Out on Hetaera's rock, south-west of us. Do you hear it? Somebody counting. One, two, three, five. "
              "Only one creature in Azshara counts like that. Mrgl has run from the crèche, and he's brought others, and the "
              "Spitelash are in the water between him and us. Go and fetch them, little one. Gently. He'll be frightened, and "
              "he'll pretend he isn't.",
         progress="I can still hear him counting out there.",
         reward="One, two, three, five... five? There were four of them. ...There's a crab in the line. Oh, Mrgl. I haven't "
                "laughed like that since the crèche. Szaria, let him count the camp's things. Nobody's will ever go missing.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "mrgl_rock"), ("wait", 2500), ("emote", "self", "talk"),
                 ("say", "self", "One, two, three, five. Somebody out there still can't count.", "talk"),
                 ("sound", "self", ELF_LAUGH),
                 ("summon", "ch0:mrgl", "mrgl_rock", 1500), ("summon", "runaway_1", "runaway_1", 1500),
                 ("summon", "runaway_2", "runaway_2", 1500), ("summon", "runaway_3", "runaway_3", 1500),
                 ("summon", "runaway_4", "runaway_4", 1500), ("summon", "stowaway", "crab", 1500),
                 ("summon", "shorewatch", "picket_1", 1500), ("summon", "shorewatch", "picket_2", 1500),
                 ("summon", "shorewatch", "picket_3", 1500), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "spell")],
         complete=[("move", "ch0:mrgl", "mrgl_count", "walk"), ("wait", 3000), ("face", "ch0:mrgl", "player"),
                   ("emote", "ch0:mrgl", "point"), ("sound", "ch0:mrgl", "murloc_fidget"), ("wait", 900),
                   ("emote", "ch0:mrgl", "point"), ("wait", 900), ("emote", "ch0:mrgl", "point"), ("wait", 900),
                   ("emote", "ch0:mrgl", "point"), ("wait", 900), ("emote", "ch0:mrgl", "point"),
                   ("sound", "ch0:mrgl", "murloc_fidget2"), ("wait", 1200), ("emote", "ch0:mrgl", "question"), ("wait", 1500),
                   ("emote", "ch0:mrgl", "point"), ("wait", 900), ("emote", "ch0:mrgl", "exclamation"),
                   ("sound", "stowaway", 1229), ("wait", 1200), ("emote", "ch0:mrgl", "laugh"), ("sound", "self", ELF_LAUGH),
                   ("emote", "runaway_1", "dance"), ("emote", "runaway_3", "cheer"), ("emote", "runaway_4", "eat"),
                   ("wait", 2500), ("move", "ch0:mrgl", "clam_spot", "walk"), ("wait", 2000), ("state", "ch0:mrgl", "work")],
         poi=["mrgl_rock"]),

    # 4.23: the old drills (boring): the same three rocks, every day
    dict(key="ch4_drills", title="The Old Drills", giver="ch0:ssaveth", ender="ch0:ssaveth", level=29, xp=8, tone="boring",
         prev="ch4_ash_karath", kill=[("snapper", 12)], rewards=["snapper_claw"],
         goal="Kill 12 Makrinni Snappers as they come up off the reef into the shallows around the Hollow.",
         text="Patrol. The camp's beach and the shallows round it, the same way every day: the north rock, the east rock, the "
              "south rock, and back. The makrura come up off the reef at night and get into the fish traps. Twelve. I don't "
              "remember most of my life. I remember this. Go.",
         progress="North rock. East rock. South rock.",
         reward="Twelve. Same as yesterday. Same as tomorrow. Good.",
         details=["talk"], reward_emotes=["roar"],
         accept=[("summon", "snapper", "snap_1", 900), ("summon", "snapper", "snap_2", 900), ("summon", "snapper", "snap_3", 900),
                 ("summon", "snapper", "snap_4", 900), ("summon", "snapper", "snap_5", 900), ("summon", "snapper", "snap_6", 900),
                 ("summon", "snapper", "snap_7", 900), ("summon", "snapper", "snap_8", 900), ("summon", "snapper", "snap_9", 900),
                 ("summon", "snapper", "snap_10", 900), ("summon", "snapper", "snap_11", 900),
                 ("summon", "snapper", "snap_12", 900), ("summon", "snapper", "snap_13", 900),
                 ("summon", "snapper", "snap_14", 900), ("summon", "snapper", "snap_15", 900),
                 ("summon", "snapper", "snap_16", 900),
                 ("state", "self", "none"), ("face", "self", "rock_2"), ("emote", "self", "attack2h"), ("sound", "self", 977),
                 ("wait", 1500), ("face", "self", "rock_3"), ("emote", "self", "attack2h"), ("sound", "self", 977),
                 ("wait", 1500), ("face", "self", "rock_1"), ("emote", "self", "attack2h"), ("sound", "self", 977),
                 ("wait", 1500), ("face", "self", "player"), ("state", "self", "ready_thrown")],
         complete=[("state", "self", "none"), ("face", "self", "rock_2"), ("emote", "self", "attack2h"), ("wait", 1200),
                   ("face", "self", "rock_3"), ("emote", "self", "attack2h"), ("wait", 1200), ("face", "self", "rock_1"),
                   ("emote", "self", "attack2h"), ("wait", 1200), ("face", "self", "sea_south"), ("emote", "self", "roar"),
                   ("sound", "self", "naga_aggro"), ("state", "self", "ready_thrown")],
         poi=["snappers"]),

    # 4.24: Thessa's lenses (a shrine to the sea, not to the Empress)
    dict(key="ch4_lenses", title="Thessa's Lenses", giver="ch0:thessa_trainer", ender="ch0:thessa_trainer", level=29, xp=8,
         tone="serious", prev="ch4_envoy", items=[("lens", 6)], rewards=["thessa_glass"],
         goal="Gather 6 Sea-Glass Lenses from the rocks in the bay around the Hollow.",
         text="The crèche taught us to pray to a statue of the Empress. I want to pray to something that's actually "
              "listening. The sea throws glass up on the rocks out there, smoothed and clear, like eyes. Bring me six. I'll "
              "set them in a ring on the sand and let the light decide what it wants to show us.",
         progress="Six. Clear ones, if you can find them.",
         reward="There. Look how the light comes through... No, don't kneel. Just look. That's all this shrine asks of anyone.",
         details=["talk"], reward_emotes=["omnicast"],
         accept=[("face", "self", "sea_south"), ("emote", "self", "omnicast"), ("visual", "self", HOLY_NOVA), ("wait", 2500),
                 ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "thessa_glass"),
                 ("emote", "self", "spell")],
         complete=[("emote", "self", "work"), ("object", "lens", "lens_1", 180), ("wait", 700), ("object", "lens", "lens_2", 180),
                   ("wait", 700), ("object", "lens", "lens_3", 180), ("wait", 700), ("object", "lens", "lens_4", 180),
                   ("wait", 700), ("object", "lens", "lens_5", 180), ("wait", 700), ("object", "lens", "lens_6", 180),
                   ("wait", 1000), ("summon", "lens_light", "lens_ring", 180), ("emote", "self", "omnicast"), ("wait", 3000),
                   ("summon", "looker_1", "looker_from_1", 120), ("wait", 600), ("move", "looker_1", "looker_1", "walk"),
                   ("wait", 4000), ("summon", "looker_2", "looker_from_2", 120), ("wait", 600),
                   ("move", "looker_2", "looker_2", "walk"), ("wait", 4000), ("summon", "looker_3", "looker_from_3", 120),
                   ("wait", 600), ("move", "looker_3", "looker_3", "walk"), ("wait", 5000), ("face", "looker_1", "lens_ring"),
                   ("face", "looker_2", "lens_ring"), ("face", "looker_3", "lens_ring"), ("state", "looker_2", "channel")],
         poi=["glass_1", "glass_4", "glass_6"]),

    # 4.25: the kelp blanket (stupid): the keeper vanishes under it, and a siren asks the room a question
    dict(key="ch4_kelp", title="The Kelp Blanket", giver="ch0:vyssa", ender="ch0:vyssa", level=29, xp=8, tone="stupid",
         prev="ch4_ash_karath", items=[("long_kelp", 10)], rewards=["blanket_corner"],
         goal="Bring Vyssa the Coral-Keeper 10 Long Kelp from the kelp beds in the shallows around the Hollow.",
         text="Isshara won't say so, but she's cold at night. The old ones always are; the deep never lets go of them. I'm "
              "going to make her a blanket. Kelp. Long kelp, the good thick stuff from the beds round the camp. Ten strands. "
              "Don't make that face. You'll see.",
         progress="Ten strands. Long ones. The short ones fall apart.",
         reward="Done! It's... big. It's very big. And a bit slimy. She loves it: look, she's vanished under it. Don't tell "
                "her it smells.",
         details=["talk"], reward_emotes=["work"],
         accept=[("state", "self", "none"), ("face", "self", "hollow_pool"), ("emote", "self", "talk"), ("wait", 2000),
                 ("face", "self", "player"), ("emote", "self", "work"), ("wait", 1500), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "work"), ("wait", 1500), ("object", "kelp_blanket", "blanket", 240),
                   ("sound", "self", "splash"), ("state", "ch0:isshara", "drowned"), ("sound", "ch0:isshara", 7915),
                   ("wait", 3000), ("summon", "watching_siren", "siren_watch", 30), ("wait", 1500),
                   ("say", "watching_siren", "Do you find me alluring?", "talk", "NagaSirenPissed4"), ("wait", 3000),
                   ("emote", "self", "talk"), ("state", "self", "work")],
         poi=["kelp_beds"]),

    # 4.26: two pearls missing (the chapter's last): Isshara laughs out loud; Jediga, the game's, ends it
    dict(key="ch4_end", title="Two Pearls Missing", giver="ch0:isshara", ender=8587, level=29, xp=8, tone="serious",
         prev="ch4_runaways", prev_any=["ch4_keeper", "ch4_glaive"],
         choice=["turned_robe", "turned_jerkin", "turned_hauberk"],
         goal="Go to Valormok and ask Jediga about two singing pearls a Spitelash deserter sold there.",
         text="Two more songs. I can feel them the way you feel a tooth that isn't there any more. A Spitelash deserter dug "
              "them out of a vault and sold them. Sold them! To a land-walker. They're in Valormok, in some orc's box, humming "
              "to themselves. Go and see who's bought a pair of singing pearls, little one. Try not to pay more than they're "
              "worth.",
         reward="Pearls? I don't know anything about pearls. ...Humming pearls? Oh, those pearls. Well. They might be in a box. "
                "A locked box. A very valuable locked box. Let's talk about prices, naga.",
         details=["talk"], reward_emotes=["talk", "laugh"],
         accept=[("state", "self", "none"), ("face", "self", "toward_valormok"), ("emote", "self", "omnicast"), ("wait", 2500),
                 ("sound", "self", ELF_LAUGH), ("emote", "self", "talk"), ("wait", 1500), ("sound", "self", ELF_LAUGH),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["jediga"]),
]

# -- more of someone already made ----------------------------------------------------------------------------------
SPAWNS = [
    # young Szaria in her two memories: at the dig on the Broken Isles, on Serpentra's beach
    dict(npc="ch0:szaria_young", at="szaria_dig", facing=4.01, phase=M5),
    dict(npc="ch0:szaria_young", at="szaria_m6", facing=0.75, phase=M6),
    # the Tide-Caller at the envoy's tent, from 4.20 (bible 18.7)
    dict(npc="ch0:tidecaller", at="envoy_tidecaller", facing=5.9, phase=ENVOY),
    # Shaelyn Harborsong (chapter 2's) by her fire at Shadowsong Shrine, sitting with her back to her pillar: always
    # there (chapters 7, 8 and 10 come back to her)
    dict(npc="ch2:shaelyn", at="shaelyn", facing=5.57, state="sit"),
    # Thessa (2.24's caged siren) at the Hollow, the priest trainer (bible 18.9: from 4.24; here from 4.20, this
    # chapter's one rule), by the keeper's pool
    dict(npc="ch0:thessa_trainer", at="thessa", facing=2.6, phase=ENVOY),
]
