# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 7 of the naga's story: Dust (levels 38 to 43), the bible's section 14.

The keeper's death. The Hollow (chapter 2's islet in the Bay of Storms) is attacked at dawn: Serena Scarscale's fleet
rises out of the bay, the camp is overturned, and her honor guard drags Isshara to a raft. Nobody is left to sing, so
the player lays the dropped pearl in the righted basin and a voice answers out of the water (7.05): the memory of how
Vashj and Kael took Illidan's cage from the Watchers in Outland (m13). The raft's wake leads east along the Shattered
Strand to a cove under the Bitter Reaches' cliffs (x 4110-4170, y -6880 to -6980), where the raft is moored under
guard; Valormok rides out (7.12) and makes its line on the beach south of the cove (4085, -7075); the cage is taken
and lost and taken again (7.14) and Taelon breaks Serena's frost off the keeper at the line. She sings her last memory
lying on the sand (m14), and dies, and is given to the sea in the shallows below the line. Then the Tide-Broken go
inland, up the north path of Forlorn Ridge (from its foot at 3245, -4620) to the dry crater (floor 2920-3010,
-4730 to -4820, z 228-245), where Vashj once held a portal open, and carry water up to it; and from its east rim,
at last, Azshara as it is appears (7.24: chapter 1's alone_until).

Two memories, both bit B (the bible's 18.2):
  - m13, The Dusts of Outland and The Search for Illidan (Isshara's, sung by the player at the Hollow's righted
    basin): the Bitter Reaches' plateau as Hellfire Peninsula under an amber haze (screen 161, "Time Warp"): Kael's
    camp at its west edge, the dry basin of the waste to the east with its mud springs, the Watchers' stronghold on
    the high ground beyond, and the road between where the cage is hauled. One wakes at the Hollow's pool.
  - m14, Illidan's Task (Isshara's last, sung by her as she lies on the sand): Illidan's camp on the same plateau's
    north-west, 530 yards from m13's centre (two bit-B memories must stand 500 apart: the bible's "a short vision at
    M13's stage" can't share its ground), with Kil'jaeden in a storm above the hill behind it. One wakes beside her
    at Valormok's line.

Phases in Azshara (three rules of this chapter's own, and two reused):
  - OVERTURNED ("between", "ch7_overturned", "ch7_crater"): the Hollow overturned (its wreck, its dead, the hub kit
    still at its posts, Vyssa at the righted basin), the raft and its guards in the cove.
  - LINE ("between", "ch7_rides", "ch7_crater"): Valormok's war party, from Ag'tor's whistle (7.12) to the crater:
    the Horde's line on the beach, the grunts fighting at the raft, the wind riders over the cove, the Tide-Broken
    there with them, and the column waiting at the foot of Forlorn Ridge.
  - CRATER ("from", "ch7_crater"): the crater camp and its hub kit, the rim's sentries, the pool (with the little
    water the column carried up: 7.20 fills it), the quests' things at Lake Mennar and Valormok after it.
  - Reused, no bit: chapter 2's HOLLOW (the dawn patrol's markers), chapter 4's ENVOY (Valormok's warcaller).
Isshara after the raid is never a standing spawn (a rule of her own would have been a fourth): each scene that needs
her summons her (the raft vision, the tug, her last song, her death, the funeral), and each quest's accept summons
her again, so a quest taken over still finds her.

People of other chapters placed here: Szaria, Ssaveth, Vyssa, the hub kit and Mrgl the banker (ch0) at the
overturned Hollow, Valormok's line and the crater; Taelon Emberveil (chapter 6's, ch6:taelon, who stands at Valormok
always) at the line and the crater, and running to Ag'tor in 7.12's scene; Shaelyn (chapter 2's) summoned on the rise
in 7.17a. Scene doubles of this chapter's own (never mistaken for the shared ones by a scene looking for the nearest):
the column's Vyssa, Ssaveth and Mrgl (7.19), the line's Ag'tor (the game's stays at Valormok), the two Ssethis of 7.26
(chapter 5's stand on their islet).

Choices that change a later scene, one quest per road (a scene can't ask which road a player took): 7.17 (Shaelyn on
the rise if 4.19a, no one if 4.19b) and 7.26 (Ssethis free if 5.23a, unsung if 5.23b). The chapter's last quest,
ch7_end (The New Moon, Szaria's watch set and Ssaveth's line in the sand), takes either 7.26 (chapter 8 starts after
it): it isn't one of the bible's numbered quests; it's there so the chapter ends on one quest whichever road.

The engine has no cut of Vashj's "Water... is life." (the bible's 18.5, optional): 7.20a has the words as text from
the water, no voice.

Plain data: tools/murloc/SCHEMA.md, tools/naga/SCHEMA.md."""

OVERTURNED = ("between", "ch7_overturned", "ch7_crater")     # the Hollow overturned (7.02's reward to 7.19's)
LINE = ("between", "ch7_rides", "ch7_crater")                # Valormok's war party out (7.12's reward to 7.19's)
CRATER = ("from", "ch7_crater")                              # the crater camp, from 7.19's reward on
HOLLOW = ("between", "ch2:ch2_arrival", "ch7_overturned")    # chapter 2's rule for the Hollow (reused: no bit)
ENVOY = ("from", "ch4:ch4_envoy")                            # chapter 4's rule at Valormok (reused: no bit)
M13 = ("memory", "m13")                                      # The Dusts of Outland (Isshara's), the Bitter Reaches
M14 = ("memory", "m14")                                      # Illidan's Task (Isshara's last), the Bitter Reaches

CHAPTER = dict(key="ch7", title="Dust", levels=(38, 43), map=1, zones=[16], hub="c_szaria")

TOWNS = ["Valormok"]

AGTOR = 8576                                # Ag'tor Bloodfist, the game's (no scenes of the story's: 7.12, 7.13, 7.23)

PLACES = {
    # -- the Hollow overturned (chapter 2's islet; its places are chapter 2's and 4's: ch2:pool_shore, ch4:pool_side) --
    "basin": (3964.0, -6318.0), "basin_use": (3966.0, -6319.0), "pool_voice": (3967.0, -6320.0),
    "dead_1": (3948.0, -6295.0), "dead_2": (3970.0, -6306.0), "dead_3": (3936.0, -6272.0), "pearl_glint": (3970.5, -6307.5),
    "hurt_1": (3955.0, -6248.0), "hurt_2": (3941.0, -6286.0), "smoke_1": (3962.0, -6280.0), "smoke_2": (3976.0, -6298.0),
    "wreck_1": (3958.0, -6283.0), "wreck_2": (3972.0, -6291.0), "wreck_3": (3946.0, -6262.0), "wreck_4": (3966.0, -6298.0),
    "wreck_5": (3939.0, -6278.0), "burn_1": (3922.0, -6305.0, 0.0), "burn_2": (3918.0, -6262.0, 0.0),
    "burn_3": (3990.0, -6312.0, 0.0), "o_ssaveth": (3930.0, -6243.0), "o_vyssa": (3958.0, -6315.0),
    "o_torch_1": (3975.0, -6286.0),
    # the dawn patrol's markers round the islet (7.01), and the dead fish along the east shore
    "marker_1": (3926.0, -6246.0), "marker_2": (3982.0, -6258.0), "marker_3": (3934.0, -6300.0), "marker_4": (3980.0, -6322.0),
    "fish_1": (3988.0, -6318.0, 0.0), "fish_2": (3992.0, -6326.0, 0.0), "fish_3": (3984.0, -6334.0, 0.0),
    "fish_4": (3996.0, -6312.0, 0.0), "fish_5": (3976.0, -6338.0, 0.0), "fish_6": (3998.0, -6300.0, 0.0),
    "east_sea": (4040.0, -6330.0, 0.0),
    # the attack (7.02): Serena on the rock off the islet's south-west, the rows rising out of the bay, the beach
    "serena_rock": (3864.0, -6276.0), "rise_1": (3905.0, -6250.0, -1.0), "rise_2": (3903.0, -6268.0, -1.0),
    "rise_3": (3906.0, -6286.0, -1.0), "rise_4": (3912.0, -6304.0, -1.0), "rise_5": (3908.0, -6236.0, -1.0),
    "rise_6": (3898.0, -6278.0, -1.0), "land_1": (3927.0, -6252.0), "land_2": (3924.0, -6268.0), "land_3": (3928.0, -6284.0),
    "land_4": (3933.0, -6298.0), "fallback_1": (3980.0, -6262.0), "fallback_2": (3984.0, -6270.0), "fallback_3": (3976.0, -6256.0),
    # the keeper taken (7.03): Serena in the water off the pool, her guards, the raft and the way it goes
    "serena_near": (3936.0, -6312.0, -1.0), "guard_rise_1": (3972.0, -6334.0, -1.0), "guard_rise_2": (3962.0, -6332.0, -1.0),
    "seize_1": (3966.0, -6318.0), "seize_2": (3960.0, -6320.0), "raft_dock": (3975.0, -6338.0, 0.0),
    "raft_away_1": (4010.0, -6380.0, 0.0), "raft_away_2": (4060.0, -6450.0, 0.0),
    # the raft's wake (7.11): torn kelp, the hairpin's rock, the ledge above the cove
    "wake_kelp": (4040.0, -6430.0, 0.0), "wake_rock": (4134.0, -6384.0), "lookout": (4185.0, -6905.0),

    # -- the cove under the Bitter Reaches: the raft moored, its guards on the beach ---------------------------------
    "raft": (4128.0, -6890.0, 0.2), "raft_cage": (4128.0, -6890.0, 0.6), "raft_banner": (4124.0, -6887.0, 0.6),
    "raft_isshara": (4128.0, -6890.0, 0.8), "raft_prod": (4136.0, -6896.0, 0.0), "cove_beach": (4140.0, -6930.0),
    "rg_1": (4146.0, -6912.0), "rg_2": (4142.0, -6918.0), "rg_3": (4150.0, -6935.0), "rg_4": (4138.0, -6945.0),
    "rg_5": (4125.0, -6930.0), "rg_6": (4155.0, -6955.0), "rg_7": (4130.0, -6960.0), "rg_8": (4145.0, -6970.0),
    "rg_9": (4120.0, -6950.0), "rg_10": (4160.0, -6925.0), "rg_11": (4148.0, -6926.0), "rg_12": (4152.0, -6948.0),
    # the Horde's line on the beach south of the cove (from 7.12): the tent, the fire, the people
    "line_tent": (4086.0, -7078.0), "line_fire": (4080.0, -7072.0), "line_banner": (4092.0, -7068.0),
    "line_szaria": (4078.0, -7060.0), "line_ssaveth": (4094.0, -7056.0), "line_vyssa": (4072.0, -7066.0),
    "line_taelon": (4090.0, -7064.0), "line_agtor": (4084.0, -7052.0), "line_isshara": (4082.0, -7068.0),
    "line_wake": (4076.0, -7064.0), "taelon_lock": (4085.0, -7066.0), "vyssa_kneel": (4080.0, -7067.0),
    "lg_1": (4100.0, -7045.0), "lg_2": (4092.0, -7040.0), "lg_3": (4070.0, -7080.0), "lg_4": (4096.0, -7085.0),
    "fg_1": (4118.0, -6982.0), "fg_2": (4128.0, -6988.0), "fg_3": (4110.0, -6990.0), "fm_1": (4135.0, -6992.0),
    "fm_2": (4104.0, -6996.0), "wr_1": (4118.0, -7010.0), "wr_2": (4096.0, -6985.0),
    "ring_1": (4078.0, -7074.0), "ring_2": (4086.0, -7072.0), "ring_3": (4088.0, -7064.0), "ring_4": (4084.0, -7060.0),
    "ring_5": (4076.0, -7061.0), "ring_6": (4074.0, -7068.0), "ring_gap": (4070.0, -7058.0),
    "sea_view": (4040.0, -7030.0, 0.0), "inland": (3600.0, -6400.0), "agtor_beside": (4074.0, -7056.0),
    # the tug (7.14): from the beach by the raft to the line's tent; the Spitelash rise from the surf at the midpoint
    "tug_1": (4135.0, -6938.0), "tug_2": (4126.0, -6975.0), "tug_mid": (4114.0, -7008.0), "tug_4": (4100.0, -7040.0),
    "tug_end": (4087.0, -7076.0), "sn_1": (4066.0, -7000.0, -0.5), "sn_2": (4072.0, -6988.0), "sn_3": (4062.0, -7018.0, -0.5),
    # the funeral (7.17): the shallows below the line, the renegades with their cups, the rise above the cove
    "shallows": (4058.0, -7008.0, -0.5), "cup_1": (4062.0, -7002.0), "cup_2": (4064.0, -7013.0), "cup_3": (4054.0, -7014.0),
    "carry_1": (4070.0, -7040.0), "carry_2": (4066.0, -7024.0), "shaelyn_rise": (4084.0, -6972.0), "deep": (4030.0, -7040.0),

    # -- Forlorn Ridge: its foot (north), the path up, the north rim, the crater ---------------------------------------
    "ridge_foot": (3245.0, -4620.0), "foot_szaria": (3248.0, -4614.0), "foot_bearer_1": (3253.0, -4620.0),
    "foot_bearer_2": (3250.0, -4627.0), "foot_basket_1": (3242.0, -4628.0), "foot_basket_2": (3256.0, -4612.0),
    "shell_spot": (3238.0, -4610.0), "col_1": (3250.0, -4610.0), "col_2": (3244.0, -4612.0), "col_3": (3252.0, -4624.0),
    "col_4": (3246.0, -4630.0), "col_5": (3240.0, -4618.0), "foot_jar_1": (3258.0, -4616.0), "foot_jar_2": (3244.0, -4633.0),
    "up_1": (3205.0, -4650.0), "up_2": (3165.0, -4700.0), "up_3": (3145.0, -4735.0), "up_4": (3115.0, -4730.0),
    "rim_n": (3085.0, -4735.0), "down_1": (3050.0, -4785.0), "crater_floor": (2990.0, -4790.0),
    "sc_1": (3215.0, -4640.0), "sc_2": (3192.0, -4662.0), "sc_3": (3175.0, -4690.0), "sc_4": (3160.0, -4712.0),
    "sc_5": (3150.0, -4728.0), "sc_6": (3128.0, -4720.0), "sc_7": (3110.0, -4740.0), "sc_8": (3098.0, -4752.0),
    "sc_9": (3230.0, -4600.0), "sc_10": (3185.0, -4640.0), "sc_11": (3170.0, -4675.0), "sc_12": (3140.0, -4705.0),
    "sc_13": (3120.0, -4755.0), "sc_14": (3200.0, -4680.0),
    # the crater camp (7.19 on)
    "c_pool": (2984.0, -4758.0, 227.2), "c_pool_use": (2981.0, -4764.0), "c_voice": (2985.0, -4760.0),
    "c_stone_1": (2978.0, -4752.0), "c_stone_2": (2991.0, -4752.0), "c_stone_3": (2990.0, -4765.0),
    "c_szaria": (2975.0, -4776.0), "c_ssaveth": (2958.0, -4800.0), "c_vyssa": (2994.0, -4770.0), "c_taelon": (2946.0, -4762.0),
    "c_mrgl": (2953.0, -4745.0), "c_clam": (2950.0, -4741.0), "c_tidecaller": (2979.0, -4804.0),
    "c_mailbox": (2968.0, -4792.0), "c_graveyard": (2930.0, -4790.0), "c_singer": (2927.0, -4795.0),
    "c_kessh": (2935.0, -4775.0), "c_thessk": (2938.0, -4786.0), "c_snap": (2942.0, -4790.0), "c_shivra": (2947.0, -4808.0),
    "c_thessa": (2989.0, -4746.0), "c_oshra": (2999.0, -4754.0), "c_lyrenne": (2962.0, -4812.0), "c_nazreth": (2970.0, -4817.0),
    "c_hookfin": (3006.0, -4778.0), "c_ysh": (3004.0, -4789.0), "c_varra": (3000.0, -4799.0), "c_oleth": (2994.0, -4807.0),
    "c_sheshk": (2986.0, -4814.0), "c_hissra": (2978.0, -4818.0), "c_grosh": (2940.0, -4752.0), "c_rhazz": (2944.0, -4740.0),
    "c_lysse": (2955.0, -4818.0), "c_sszix": (2932.0, -4805.0), "c_avessa": (2960.0, -4735.0), "c_nyss": (2967.0, -4730.0),
    "c_thalassa": (2928.0, -4765.0), "c_ishra": (3000.0, -4764.0), "c_tessh": (3005.0, -4770.0),
    "c_pagoda_1": (2965.0, -4760.0), "c_pagoda_2": (3002.0, -4800.0), "c_banner_1": (2972.0, -4785.0),
    "c_banner_2": (2983.0, -4742.0), "c_torch_1": (2960.0, -4790.0), "c_torch_2": (2990.0, -4785.0),
    "c_torch_3": (2945.0, -4775.0), "c_torch_4": (2978.0, -4765.0), "c_crates": (2998.0, -4810.0), "c_jars": (2997.0, -4776.0),
    "c_bed_1": (2935.0, -4760.0), "c_bed_2": (2952.0, -4825.0),
    "c_r1": (2966.0, -4770.0), "c_r2": (2982.0, -4795.0), "c_r3": (2950.0, -4790.0), "c_r4": (2958.0, -4752.0),
    "c_ssaveth_mud": (2962.0, -4790.0), "c_vyssa_mud": (2965.0, -4792.0),
    "c_north_in": (3040.0, -4790.0), "c_north_path": (3065.0, -4760.0), "c_ssethis": (2984.0, -4780.0),
    "c_ssethis_in": (3014.0, -4787.0),
    "c_rim_look": (2990.0, -4918.0), "c_szaria_rim": (2988.0, -4912.0), "c_moon": (2700.0, -4800.0),
    "rim_e": (2990.0, -4922.0), "rim_w": (2962.0, -4650.0), "rim_s": (2850.0, -4790.0), "thirsty_rim": (3060.0, -4770.0),
    "line_sand": (2961.0, -4797.0), "thirsty_in": (3036.0, -4786.0),

    # -- Valormok: the warcaller at Ag'tor's side, the barracks, Kurll's stores, the two lines before the chief -------
    "ruzga": (3607.0, -4400.0), "agtor": (3601.0, -4406.0), "kurll": (3580.0, -4383.0), "kurll_argue": (3584.0, -4388.0),
    "barracks": (3592.0, -4416.0), "rack": (3598.0, -4422.0), "east_gate": (3640.0, -4470.0), "taelon_v": (3612.0, -4398.0),
    "barrel_1": (3574.0, -4376.0), "barrel_2": (3571.0, -4388.0), "barrel_3": (3586.0, -4374.0), "barrel_4": (3576.0, -4394.0),
    "kin_g1": (3612.0, -4392.0), "kin_g2": (3615.0, -4395.0), "kin_g3": (3618.0, -4398.0), "kin_n1": (3620.0, -4388.0),
    "kin_n2": (3623.0, -4391.0), "kin_n3": (3626.0, -4394.0), "kin_szaria": (3608.0, -4398.0), "kin_ssaveth": (3611.0, -4394.0),

    # -- Lake Mennar's north-west shore: the jars (7.20a) and the mud (7.21) ----------------------------------------
    "jar_1": (2680.0, -5288.0), "jar_2": (2672.0, -5298.0), "jar_3": (2688.0, -5296.0), "jar_4": (2664.0, -5290.0),
    "jar_5": (2676.0, -5278.0), "mud_1": (2668.0, -5300.0), "mud_2": (2660.0, -5296.0), "mud_3": (2683.0, -5302.0),
    "mud_4": (2694.0, -5299.0), "mud_5": (2655.0, -5288.0), "mud_6": (2700.0, -5292.0), "lake": (2676.0, -5292.0),

    # -- memory m13 (bit B): the Bitter Reaches as Hellfire Peninsula ---------------------------------------------------
    "m13_centre": (4680.0, -7130.0), "m13_arrive": (4572.0, -6995.0), "m13_director": (4574.0, -6998.0),
    "m13_kael": (4585.0, -7005.0), "m13_vashj": (4590.0, -6995.0), "m13_isshara": (4578.0, -7010.0), "m13_fire": (4592.0, -7015.0),
    "be_1": (4570.0, -6988.0), "be_2": (4600.0, -6990.0), "be_3": (4568.0, -7020.0), "be_4": (4606.0, -7020.0),
    "m13_crate_1": (4563.0, -7015.0), "m13_crate_2": (4610.0, -7012.0),
    "hn_1": (4585.0, -6985.0), "hn_2": (4575.0, -7025.0), "hn_3": (4595.0, -7028.0), "hn_4": (4560.0, -7005.0),
    "m13_overlook": (4615.0, -7040.0), "kael_look": (4618.0, -7044.0), "vashj_look": (4620.0, -7034.0),
    "waste": (4750.0, -7220.0), "m13_scent": (4702.0, -7192.0), "kael_scent": (4705.0, -7196.0), "vashj_scent": (4708.0, -7186.0),
    "spring_1": (4728.0, -7150.0), "spring_2": (4745.0, -7190.0), "spring_3": (4760.0, -7230.0), "spring_4": (4740.0, -7262.0),
    "spring_5": (4770.0, -7290.0), "spring_6": (4720.0, -7240.0), "springs": (4745.0, -7220.0),
    "base": (4800.0, -7295.0), "base_1": (4795.0, -7280.0), "base_2": (4805.0, -7300.0), "base_3": (4790.0, -7310.0),
    "base_4": (4812.0, -7275.0), "base_5": (4782.0, -7292.0), "base_6": (4818.0, -7290.0), "base_tent": (4808.0, -7310.0),
    "base_lantern_1": (4790.0, -7268.0), "base_lantern_2": (4815.0, -7296.0),
    "seen_start": (4758.0, -7232.0), "seen_end": (4800.0, -7295.0), "seen_h1": (4762.0, -7238.0), "seen_h2": (4754.0, -7228.0),
    "cg_1": (4765.0, -7250.0), "cg_2": (4772.0, -7190.0), "cg_mid": (4762.0, -7120.0), "cg_4": (4705.0, -7060.0),
    "cg_5": (4640.0, -7020.0), "cg_end": (4598.0, -7008.0),
    "ha_1": (4770.0, -7258.0), "ha_2": (4760.0, -7262.0), "ha_3": (4772.0, -7244.0),
    "rt_1": (4790.0, -7140.0), "rt_2": (4785.0, -7110.0), "rt_3": (4775.0, -7150.0), "maiev_spot": (4782.0, -7128.0),
    "kael_fight": (4745.0, -7100.0), "vashj_fight": (4740.0, -7112.0), "cage_spot": (4597.0, -7006.0),
    "vul_1": (4700.0, -7150.0), "vul_2": (4650.0, -7080.0), "vul_3": (4760.0, -7210.0),
    "rub_1": (4610.0, -7040.0), "rub_2": (4680.0, -7120.0), "rub_3": (4720.0, -7180.0), "rub_4": (4560.0, -7040.0),
    "rub_5": (4650.0, -6990.0), "thorn_1": (4625.0, -7000.0), "thorn_2": (4700.0, -7100.0), "thorn_3": (4735.0, -7205.0),

    # -- memory m14 (bit B): Illidan's camp on the plateau's north-west; the storm over the hill -------------------------
    "m14_centre": (4560.0, -6610.0), "m14_arrive": (4545.0, -6596.0), "m14_director": (4550.0, -6600.0),
    "m14_fire": (4561.0, -6611.0), "m14_illidan": (4566.0, -6615.0), "m14_kael": (4556.0, -6617.0),
    "m14_vashj": (4569.0, -6604.0), "m14_kj": (4600.0, -6650.0), "m14_storm": (4590.0, -6640.0),
    "m14_naga_1": (4548.0, -6622.0), "m14_naga_2": (4575.0, -6620.0), "m14_elf_1": (4553.0, -6628.0),
    "m14_rub": (4540.0, -6612.0),
}

# -- looks, models, visuals -------------------------------------------------------------------------------------------
ROWBOAT = 30236                                  # RowBoat01_vehicle (a creature look: a boat that moves): Serena's raft
GLAIVE_CART = 29642                              # GlaiveThrowerVehicle: the Watchers' wheeled cart for Illidan's cage
WIND_RIDER = 295                                 # Wyvern.mdx: Valormok's wind riders
VULTURE = 16880                                  # CarrionBirdOutland: Outland's carrion birds over the waste
ORC_GRUNT_M, ORC_GRUNT_F, ORC_GRUNT_M2, ORC_GRUNT_F2 = 4259, 4260, 9798, 9800
AGTOR_LOOK = 7871                                # Ag'tor Bloodfist's own display (the line's Ag'tor)
BLOOD_ELVES = [18980, 18981, 18982, 18983]       # the Thalassian Base Camp's blood elves: Kael's host in m13 and m14
CAGE = "World\\EXPANSION01\\DOODADS\\COILFANG\\PASSIVEDOODADS\\cages\\cf_groundcage.m2"     # chapter 1's naga cage
SHELL_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
FLOATING_BOARDS, BURNING_BOARDS, BROKEN_BARREL = 6682, 6723, 9
WATER_BASIN, POOL_WATER, BARNACLE_ROCK = 5112, 7331, 888
DEAD_FISH, DEAD_FISH_2 = 242, 4321
ORC_TENT, HORDE_BANNER, CAMPFIRE, WATER_BARREL = 8184, 5111, 192, 7483
OUTLAND_RUBBLE = [4318, 6726, 6727, 6728]
HELLFIRE_THORN, OUTLAND_PLANT, DIRT = 6757, 3052, 20
NE_TENT, NE_LANTERN, NE_BANNER, BE_CAMPFIRE, BE_CRATE = 9177, 6913, 6390, 6744, 6616
SEAWEED = 6316
TRIDENT_DARK, TRIDENT, GLAIVE, BOW = 15910, 5747, 5598, 2550
ORC_AXE, ORC_AXE_2, BUCKET, SWORD = 10611, 10612, 12801, 2244

FROST_HAND, WATER, SPOUT, GLOW_BLUE, LIGHTNING, BLINK = 32992, 36005, 47479, 22576, 10387, 36937
FROZEN, FREEZE_ANIM, DUST, FIRE, EXPLOSION, ARCANE_BOOM = 47543, 16245, 69216, 51195, 34602, 35426
BLUE_BEAM, STORM_CLOUD, HOLY_NOVA, PURPLE_BANISH, GLOW_BLACK = 38034, 45213, 57771, 32566, 22578

# sounds (SoundEntries) by what they are
HORN, FROST_NOVA, ICE_CRACK, GLASS, QUAKE = 7054, 3076, 15696, 12334, 12549
SIREN_DEATH, ORC_WHISTLE, ORC_LAUGH, ORC_ROAR, ORC_CRY, ELF_LAUGH = 4023, 7971, 6943, 9110, 6941, 9652
KJ_ROAR, KJ_GROWL, THUNDER, CARRION = 12330, 12368, 30, 447
MUSIC_OUTLAND, MUSIC_SHADOWMOON, MUSIC_GLOOMY, MUSIC_SACRED, MUSIC_BATTLE, MUSIC_NAGA = 10610, 9285, 6074, 4454, 6077, 9462

# -- the people ------------------------------------------------------------------------------------------------------
NPCS = [
    # -- the attack on the Hollow (7.02, 7.03): summoned for the scenes ---------------------------------------------
    dict(key="serena_sing", name="Serena Scarscale", subname="Envoy of the Empress", look="serena", size=1.3, level=45,
         role="ambient", untouchable=True, summoned=True,
         idle=[("state", "self", "channel"), ("every", 9000, [("visual", "self", FROST_HAND), ("sound", "self", "siren_hiss")])]),
    dict(key="serena", name="Serena Scarscale", subname="Envoy of the Empress", look="serena", size=1.3, level=45,
         role="ambient", untouchable=True, summoned=True, idle=[("every", 9000, [("visual", "self", FROST_HAND)])]),
    dict(key="honor_guard_1", name="Honor Guard of the Empress", look="vashjir_guard", size=1.5, level=45, role="ambient",
         untouchable=True, summoned=True, equip=(TRIDENT_DARK, 0, 0), idle=[("state", "self", "ready_thrown")]),
    dict(key="honor_guard_2", name="Honor Guard of the Empress", look="vashjir_guard", size=1.5, level=45, role="ambient",
         untouchable=True, summoned=True, equip=(TRIDENT_DARK, 0, 0), idle=[("state", "self", "ready_thrown")]),
    dict(key="royal_guard", name="Spitelash Royal Guard", plural="Spitelash royal guards", look=11267, looks=[11271],
         size=1.15, level=(39, 40), side="naga", role="enemy", summoned=True, equip=(TRIDENT, 0, 0),
         abilities=[(845, 9000), (14516, 12000)]),
    dict(key="attack_siren", name="Spitelash Siren", plural="Spitelash sirens", look=11266, level=(39, 40), side="naga",
         role="enemy", summoned=True, abilities=[(9672, 7000), (12548, 15000)]),
    dict(key="isshara_taken", name="Isshara the Keeper", subname="Keeper of Songs", look="sea_witch", speed=0.7, level=45,
         role="ambient", untouchable=True, summoned=True),
    dict(key="serena_raft", name="Serena's Raft", look=ROWBOAT, scale=1.3, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True, speed=0.8),

    # -- the Hollow overturned (7.02's reward to 7.19's) ----------------------------------------------------------------
    dict(key="dead_renegade", name="Fallen Tide-Broken", look=18389, looks=[22874, 18395], level=30, role="ambient",
         at=["dead_1", "dead_2", "dead_3"], facing=1.0, phase=OVERTURNED, idle=[("state", "self", "dead")]),
    dict(key="hurt_renegade", name="Wounded Tide-Broken", plural="wounded Tide-Broken", look=22875, looks=[22869],
         level=30, role="ambient", at=["hurt_1", "hurt_2"], facing=3.0, phase=OVERTURNED,
         gossip="They came out of the water singing. Singing. I've never been so cold.",
         idle=[("state", "self", "drowned"), ("every", 31000, [("sound", "self", "naga_wound")])]),
    dict(key="pool_voice", name="A Voice in the Water", look="trigger", level=1, role="ambient", at="pool_voice",
         unit_flags=0x02000002, phase=OVERTURNED, idle=[("every", 40000, [("visual", "self", WATER)])]),
    dict(key="wreck_fire", name="Burning Wreckage", look="trigger", level=1, role="ambient", at=["smoke_1", "smoke_2"],
         unit_flags=0x02000002, phase=OVERTURNED, idle=[("every", 60000, [("visual", "self", FIRE)])]),

    # -- the raft's wake (7.11): the keeper in the raft's cage, seen from the ledge -----------------------------------
    dict(key="isshara_caged", name="Isshara the Keeper", subname="Serena's Prisoner", look="sea_witch", level=45,
         role="ambient", untouchable=True, summoned=True,
         idle=[("state", "self", "drowned"), ("every", 7000, [("visual", "self", FROST_HAND)])]),
    dict(key="raft_prodder", name="Spitelash Raft-Guard", look=6747, level=40, role="ambient", untouchable=True,
         summoned=True, equip=(TRIDENT, 0, 0)),

    # -- the cove: the raft's guards (OVERTURNED: from the raid until the Tide-Broken leave the sea) ---------------------
    dict(key="raft_guard", name="Spitelash Raft-Guard", plural="Spitelash raft-guards", look=6747, looks=[11265, 11266],
         level=(40, 41), side="naga", role="enemy", equip=(TRIDENT, 0, 0), respawn=60, phase=OVERTURNED,
         at=["rg_1", "rg_2", "rg_3", "rg_4", "rg_5", "rg_6", "rg_7", "rg_8", "rg_9", "rg_10", "rg_11", "rg_12"],
         wander=4.0, abilities=[(6533, 22000), (14516, 10000)]),

    # -- the Horde's line (LINE: from Ag'tor's whistle until the crater) ---------------------------------------------
    # the line's Ag'tor (the game's stays at Valormok: this one rode out with his grunts, and acts in the scenes)
    dict(key="agtor_line", name="Ag'tor Bloodfist", look=AGTOR_LOOK, level=45, language="orcish", role="ambient",
         at="line_agtor", facing=4.0, phase=LINE,
         gossip="My grunts fight. My wind riders watch. You fish keep your keeper alive. That's the deal.",
         idle=[("every", 47000, [("emote", "self", "talk")])]),
    dict(key="line_grunt", name="Valormok Grunt", plural="Valormok grunts", look=ORC_GRUNT_M, looks=[ORC_GRUNT_F, ORC_GRUNT_M2],
         level=40, language="orcish", role="ambient", equip=(ORC_AXE, 0, 0), at=["lg_1", "lg_2", "lg_3", "lg_4"], facing=1.0,
         phase=LINE, gossip="Chief says we hold this sand. We hold this sand.",
         idle=[("state", "self", "ready"), ("every", 61000, [("emote", "self", "roar")])]),
    dict(key="fight_grunt", name="Valormok Grunt", look=ORC_GRUNT_M2, looks=[ORC_GRUNT_F2], level=40, language="orcish",
         role="ambient", equip=(ORC_AXE_2, 0, 0), at=["fg_1", "fg_2", "fg_3"], facing=0.4, phase=LINE,
         idle=[("every", 5000, [("emote", "self", "attack2h"), ("sound", "self", 977)]),
               ("every", 23000, [("emote", "self", "roar"), ("sound", "self", ORC_ROAR)])]),
    dict(key="fight_myrmidon", name="Tide-Broken Myrmidon", look=18389, looks=[22874], size=1.15, level=38,
         role="ambient", equip=(TRIDENT, 0, 0), at=["fm_1", "fm_2"], facing=0.4, phase=LINE,
         idle=[("every", 6000, [("emote", "self", "attack2h"), ("sound", "self", "naga_attack")])]),
    dict(key="wind_rider", name="Valormok Wind Rider", look=WIND_RIDER, level=40, role="ambient", sky=28,
         at=["wr_1", "wr_2"], facing=0.5, phase=LINE),
    # the column waiting at the foot of Forlorn Ridge (from 7.12: the Tide-Broken pack up while the Horde fights)
    dict(key="foot_bearer", name="Tide-Broken Bearer", plural="Tide-Broken bearers", look=18398, looks=[22876], size=1.1,
         level=35, role="ambient", equip=(BUCKET, 0, 0), at=["foot_bearer_1", "foot_bearer_2"], facing=4.0, phase=LINE,
         gossip="Jars, baskets, nets, the clam. Mrgl counted it all twice. He says we're one jar short. We're not.",
         idle=[("state", "self", "sit"), ("every", 49000, [("emote", "self", "question")])]),

    # -- the keeper after the raid, summoned by each scene that needs her --------------------------------------------
    dict(key="isshara_bound", name="Isshara the Keeper", subname="Serena's Prisoner", look="sea_witch", speed=0.55,
         level=45, role="ambient", untouchable=True, summoned=True,
         idle=[("every", 4000, [("visual", "self", FROST_HAND)])]),
    dict(key="snatcher", name="Spitelash Snatcher", plural="Spitelash snatchers", look=11265, looks=[6747], level=40,
         side="naga", role="enemy", summoned=True, equip=(TRIDENT, 0, 0), abilities=[(6533, 18000)]),
    dict(key="isshara_dying", name="Isshara the Keeper", subname="Keeper of Songs", look="sea_witch", level=45,
         role="ambient", untouchable=True, summoned=True,
         gossip="...little one. You're warm. Sit. The sand's warm too. I can feel the sun on it.",
         idle=[("state", "self", "drowned"), ("every", 21000, [("visual", "self", WATER), ("sound", "self", "pickup_water")])]),
    dict(key="isshara_still", name="Isshara the Keeper", subname="Keeper of Songs", look="sea_witch", level=45,
         role="ambient", untouchable=True, summoned=True, gossip="She doesn't answer. The sand under her is still warm.",
         idle=[("state", "self", "drowned")]),
    dict(key="isshara_body", name="Isshara", subname="Keeper of Songs", look="sea_witch", level=45, role="ambient",
         untouchable=True, summoned=True, gossip="The water holds her up. She's lighter than she ever looked.",
         idle=[("state", "self", "drowned")]),
    dict(key="bearer_1", name="Tide-Broken Bearer", look=18398, size=1.1, level=35, role="ambient", untouchable=True,
         summoned=True, speed=0.6),
    dict(key="bearer_2", name="Tide-Broken Bearer", look=22876, size=1.1, level=35, role="ambient", untouchable=True,
         summoned=True, speed=0.6),

    # -- the column up the ridge (7.19): summoned at the foot, following -----------------------------------------------
    dict(key="col_bearer_1", name="Tide-Broken Bearer", look=18398, size=1.1, level=35, role="ambient", untouchable=True,
         summoned=True, equip=(BUCKET, 0, 0)),
    dict(key="col_bearer_2", name="Tide-Broken Bearer", look=22876, size=1.1, level=35, role="ambient", untouchable=True,
         summoned=True, equip=(BUCKET, 0, 0)),
    dict(key="col_siren", name="Tide-Broken Siren", look=18395, level=35, role="ambient", untouchable=True, summoned=True),
    dict(key="col_vyssa", name="Vyssa the Coral-Keeper", look="sorceress", level=35, role="ambient", untouchable=True,
         summoned=True, equip=(BUCKET, 0, 0)),
    dict(key="col_ssaveth", name="Myrmidon Ssaveth", look="naga_warrior", level=40, role="ambient", untouchable=True,
         summoned=True, equip=(TRIDENT_DARK, 0, 0)),
    dict(key="col_mrgl", name="Mrgl-Who-Counts", look="murloc_abyssal", level=20, role="ambient", untouchable=True,
         summoned=True),
    # where the column comes over the north rim: Vyssa knows the place (Vashj held the portal here: m12)
    dict(key="rim_memory", name="The North Rim", look="trigger", level=1, role="ambient", at="rim_n",
         unit_flags=0x02000002, phase=LINE,
         watch=(18, [("face", "col_vyssa", "crater_floor"), ("wait", 1500),
                     ("say", "col_vyssa", "Wait. Wait, I know this place."), ("wait", 3000),
                     ("emote", "col_vyssa", "spell"),
                     ("say", "col_vyssa", "Isshara sang it. The square in the ruins, the towers, the light. She held a door "
                                          "open here, to another world, and every elf went through it."),
                     ("music", MUSIC_NAGA), ("wait", 5000), ("say", "col_vyssa", "Vashj. Right down there."),
                     ("wait", 2500), ("emote", "col_siren", "cry")], 90000)),

    # -- the crater camp (CRATER) ----------------------------------------------------------------------------------------
    dict(key="crater_pool", name="The Crater's Pool", look="trigger", level=1, role="ambient", at="c_voice",
         unit_flags=0x02000002, phase=CRATER, idle=[("every", 26000, [("visual", "self", WATER)])]),
    dict(key="crater_voice", name="A Voice in the Water", look="trigger", level=1, role="ambient", at="c_pool",
         unit_flags=0x02000002, phase=CRATER),
    dict(key="rim_sentry", name="Tide-Broken Sentry", plural="sentries", look=18389, looks=[22874], size=1.2, level=38,
         role="ambient", equip=(TRIDENT, 0, 0), at=["rim_n", "rim_e", "rim_s", "rim_w"], facing=2.0, phase=CRATER,
         gossip="From up here you can see the sea. Don't tell anyone. They'll all want a turn.",
         idle=[("state", "self", "ready_thrown"), ("every", 64000, [("emote", "self", "roar")])]),
    dict(key="camp_renegade", name="Tide-Broken Renegade", plural="Tide-Broken renegades", look=22875, looks=[22871, 18396],
         level=30, role="ambient", at=["c_r1", "c_r2", "c_r3", "c_r4"], facing=1.5, phase=CRATER,
         gossip="Sand everywhere. Dry sand. It gets in places sand should never get. But nobody comes up here. Nobody.",
         idle=[("state", "self", "work"), ("every", 57000, [("emote", "self", "laugh")])]),
    dict(key="ridge_scout", name="Spitelash Scout", plural="Spitelash scouts", look=6747, looks=[11265, 11266],
         level=(41, 42), side="naga", role="enemy", summoned=True, equip=(TRIDENT, 0, 0),
         abilities=[(22887, 7000), (6533, 20000)]),
    dict(key="thirsty_grunt", name="Thirsty Grunt", look=ORC_GRUNT_M, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True),
    # Ssethis (chapter 5's fates: ch5:ssethis_watching, ch5:ssethis_lost stand on their islet): this chapter's doubles
    # for the one scene on the ridge
    dict(key="ssethis_free", name="Ssethis", subname="", look=11265, scale=0.95, level=40, role="ambient",
         untouchable=True, summoned=True, equip=(5745, 0, 0)),
    dict(key="ssethis_blank", name="Ssethis", subname="Unsung", look=11265, scale=0.95, speed=0.6, level=40,
         role="ambient", untouchable=True, summoned=True, idle=[("every", 6000, [("visual", "self", GLOW_BLACK)])]),

    # -- Valormok (Ag'tor and Kurll are the game's: their story is played round them by the story's people) -----------
    dict(key="ruzga", name="Warcaller Ruzga", subname="Valormok", look=ORC_GRUNT_F2, level=45, side="faction:76",
         language="orcish", role="ambient", equip=(ORC_AXE, 0, 0), at="ruzga", facing=3.9, phase=ENVOY,
         gossip="I blow the horn, they come running. I don't blow the horn, they stand around eating. Chief likes the horn.",
         idle=[("every", 51000, [("emote", "self", "talk"), ("face", "self", "agtor")]),
               ("every", 83000, [("emote", "self", "laugh"), ("face", "self", "east_gate")])]),
    dict(key="runner_1", name="Valormok Grunt", look=ORC_GRUNT_M, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True, equip=(ORC_AXE, 0, 0)),
    dict(key="runner_2", name="Valormok Grunt", look=ORC_GRUNT_F, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True, equip=(ORC_AXE_2, 0, 0)),
    dict(key="runner_3", name="Valormok Grunt", look=ORC_GRUNT_M2, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True, equip=(ORC_AXE, 0, 0)),
    dict(key="arguing_grunt", name="Valormok Grunt", look=ORC_GRUNT_M2, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True),
    dict(key="kin_grunt_1", name="Valormok Grunt", look=ORC_GRUNT_M, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True, equip=(ORC_AXE, 0, 0)),
    dict(key="kin_grunt_2", name="Valormok Grunt", look=ORC_GRUNT_F, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True, equip=(ORC_AXE, 0, 0)),
    dict(key="kin_grunt_3", name="Valormok Grunt", look=ORC_GRUNT_M2, level=40, language="orcish", role="ambient",
         untouchable=True, summoned=True, equip=(ORC_AXE_2, 0, 0)),
    dict(key="kin_naga_1", name="Tide-Broken Myrmidon", look=18389, size=1.15, level=38, role="ambient", untouchable=True,
         summoned=True, equip=(TRIDENT, 0, 0)),
    dict(key="kin_naga_2", name="Tide-Broken Siren", look=18395, level=38, role="ambient", untouchable=True, summoned=True),
    dict(key="kin_naga_3", name="Tide-Broken Myrmidon", look=22874, size=1.15, level=38, role="ambient", untouchable=True,
         summoned=True, equip=(TRIDENT, 0, 0)),

    # -- memory m13: Outland (Kael's camp, the waste, the Watchers' road and stronghold) --------------------------------
    dict(key="m13_director", name="Outland", look="trigger", level=1, role="ambient", at="m13_director",
         unit_flags=0x02000002, phase=M13, watch=(20, [("music", MUSIC_OUTLAND)], 120000)),
    dict(key="kael_m13", name="Prince Kael'thas Sunstrider", subname="", look="kaelthas", level=42, role="ambient",
         untouchable=True, at="m13_kael", facing=0.6, phase=M13,
         idle=[("every", 44000, [("emote", "self", "talk")])]),
    dict(key="vashj_m13", name="Lady Vashj", look="vashj", size=1.4, level=42, role="ambient", untouchable=True,
         at="m13_vashj", facing=5.8, phase=M13, idle=[("every", 39000, [("emote", "self", "roar")])]),
    dict(key="kael_elf", name="Blood Elf of Kael's Host", plural="Kael's blood elves", look=BLOOD_ELVES[0],
         looks=BLOOD_ELVES[1:], level=36, role="ambient", untouchable=True, at=["be_1", "be_2", "be_3", "be_4"], facing=0.5,
         phase=M13, idle=[("every", 47000, [("emote", "self", "talk")])]),
    dict(key="host_naga", name="Naga of Vashj's Host", plural="Vashj's naga", look=18389, looks=[18392, 22874, 22870],
         size=1.05, level=36, role="ambient", untouchable=True, at=["hn_1", "hn_2", "hn_3", "hn_4"], facing=0.5, phase=M13,
         idle=[("every", 52000, [("emote", "self", "shy")])]),
    dict(key="vulture", name="Carrion Bird", plural="carrion birds", look=VULTURE, level=35, role="ambient", sky=26,
         untouchable=True, at=["vul_1", "vul_2", "vul_3"], phase=M13, idle=[("every", 29000, [("sound", "self", CARRION)])]),
    dict(key="watcher_m13", name="Watcher", subname="Maiev's Watchers", plural="Watchers", look="warden",
         looks=["warden_2", "warden_3", "warden_4"], equip=(GLAIVE, GLAIVE, 0), level=(39, 40), side="hostile",
         role="enemy", language="universal", at=["base_1", "base_2", "base_3", "base_4", "base_5", "base_6"], facing=2.4,
         respawn=60, phase=M13, abilities=[(22887, 8000)]),
    # the rise over the Watchers' road (7.08): the rest of the prelude plays when one comes up beside them
    dict(key="scent_rise", name="The Rise over the Road", look="trigger", level=1, role="ambient", at="m13_scent",
         unit_flags=0x02000002, phase=M13,
         watch=(16, [("wait", 1500), ("face", "vashj_m13", "base"), ("emote", "vashj_m13", "battle_roar"),
                     ("say", "vashj_m13", "Night elves! What could they be doing here?"), ("wait", 3500),
                     ("face", "kael_m13", "base"),
                     ("say", "kael_m13", "The warden, Maiev, swore to capture Illidan at any cost. She must have brought "
                                         "her warriors here to hunt him!", "talk"), ("wait", 5000),
                     ("summon", "cage_seen", "seen_start", 60), ("summon", "seen_hauler_1", "seen_h1", 60),
                     ("summon", "seen_hauler_2", "seen_h2", 60), ("wait", 1000), ("move", "cage_seen", "seen_end", "walk"),
                     ("move", "seen_hauler_1", "seen_end", "walk"), ("move", "seen_hauler_2", "seen_end", "walk"),
                     ("face", "kael_m13", "seen_start"), ("emote", "kael_m13", "spell"),
                     ("say", "kael_m13", "There! Illidan lies chained in that cage! The night elves must be taking him "
                                         "to their stronghold."), ("wait", 5000),
                     ("say", "vashj_m13", "Then we must rescue him before they reach safety.", "battle_roar"),
                     ("wait", 8000), ("move", "kael_m13", "m13_kael", "walk"), ("move", "vashj_m13", "m13_vashj", "walk")],
               90000)),
    dict(key="cage_seen", name="Illidan's Cage", look=GLAIVE_CART, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, speed=0.6, summoned=True, idle=[("every", 3000, [("visual", "self", PURPLE_BANISH)])]),
    dict(key="seen_hauler_1", name="Watcher", look="warden_2", equip=(GLAIVE, 0, 0), level=40, role="ambient",
         untouchable=True, summoned=True, speed=0.6),
    dict(key="seen_hauler_2", name="Watcher", look="warden_3", equip=(GLAIVE, 0, 0), level=40, role="ambient",
         untouchable=True, summoned=True, speed=0.6),
    # the tug's cart (7.09) and the Watchers who haul it and take it back
    dict(key="illidan_cage", name="Illidan's Cage", look=GLAIVE_CART, level=40, side="neutral", role="ambient",
         untouchable=True, unit_flags=0x02000002, speed=0.75, summoned=True,
         idle=[("every", 3000, [("visual", "self", PURPLE_BANISH)])]),
    dict(key="cage_hauler", name="Watcher Cage-Hauler", plural="Watcher cage-haulers", look="warden_2", looks=["warden_3"],
         equip=(GLAIVE, 0, 0), level=(39, 40), side="hostile", role="enemy", language="universal", summoned=True,
         abilities=[(22887, 9000)]),
    dict(key="watcher_retaker", name="Watcher", subname="Maiev's Watchers", look="warden", looks=["warden_4"],
         equip=(GLAIVE, GLAIVE, 0), level=(39, 40), side="hostile", role="enemy", language="universal", summoned=True,
         abilities=[(22887, 8000)]),
    dict(key="maiev_m13", name="Maiev Shadowsong", subname="Warden", look="maiev", level=45, role="ambient",
         untouchable=True, language="universal", summoned=True),
    dict(key="illidan_m13", name="Illidan Stormrage", subname="The Betrayer", look="illidan", size=1.1, level=45,
         role="ambient", untouchable=True, summoned=True),

    # -- memory m14: Illidan's camp, and the storm --------------------------------------------------------------------
    dict(key="illidan_m14", name="Illidan Stormrage", subname="The Betrayer", look="illidan", size=1.1, level=45,
         role="ambient", untouchable=True, at="m14_illidan", facing=3.9, phase=M14,
         idle=[("every", 9000, [("visual", "self", 35411)])]),
    dict(key="kiljaeden", name="Kil'jaeden", subname="The Deceiver", look="kiljaeden", level=73, role="ambient",
         untouchable=True, unit_flags=0x02000002, summoned=True),
    dict(key="storm", name="The Storm", look="trigger", scale=3.0, level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 2500, [("visual", "self", LIGHTNING)]), ("every", 6000, [("visual", "self", STORM_CLOUD)])]),
    dict(key="m14_director", name="Illidan's Camp", look="trigger", level=1, role="ambient", at="m14_director",
         unit_flags=0x02000002, phase=M14,
         watch=(30, [("music", MUSIC_SHADOWMOON), ("wait", 4000), ("face", "illidan_m14", "m14_kj"),
                     ("aura", "player", "kj_storm"), ("sky", "kiljaeden", "m14_kj", 40, 22),
                     ("summon", "storm", "m14_storm", 22), ("sound", "illidan_m14", KJ_ROAR), ("wait", 3000),
                     ("sound", "illidan_m14", THUNDER), ("visual", "illidan_m14", 35411), ("wait", 4000),
                     ("sound", "illidan_m14", KJ_GROWL), ("wait", 3500),
                     ("say", "illidan_m14", "It shall be done, great one. It shall be done."), ("wait", 5000),
                     ("sound", "illidan_m14", THUNDER), ("wait", 5000), ("unaura", "player", "kj_storm"),
                     ("face", "illidan_m14", "m14_kael"), ("wait", 2500),
                     ("say", "illidan_m14", "At Dalaran, I attempted to use the Eye of Sargeras to melt away the polar "
                                            "icecaps surrounding the Icecrown Glacier. If the spell had succeeded, the Lich "
                                            "King would have been vanquished forever."), ("wait", 9000),
                     ("say", "vashj_m13", "But the cursed night elves intervened."), ("wait", 3500),
                     ("say", "illidan_m14", "And the spell went awry. Given my failure, I fled to this desolate place to "
                                            "evade Kil'jaeden's wrath. Now, if I am to remain here in exile, we will need to "
                                            "ensure that Kil'jaeden's agents have been cleansed from the land."),
                     ("wait", 11000), ("emote", "kael_m13", "talk"), ("emote", "vashj_m13", "roar"), ("wait", 2500),
                     ("credit", "ch7_last_song")], 60000)),
]

# -- things -------------------------------------------------------------------------------------------------------------
OBJECTS = [
    # -- the Hollow overturned -----------------------------------------------------------------------------------------
    dict(key="basin_obj", model=WATER_BASIN, name="The Keeper's Basin", at="basin", kind="doodad", scale=1.1, facing=2.4,
         phase=OVERTURNED),
    dict(key="wreck_crate", model="naga_crate", name="Smashed Crates", at=["wreck_1", "wreck_2", "wreck_3"], kind="doodad",
         facing=2.0, scale=0.9, phase=OVERTURNED),
    dict(key="wreck_barrel", model=BROKEN_BARREL, name="Broken Barrel", at=["wreck_4", "wreck_5"], kind="doodad",
         phase=OVERTURNED),
    dict(key="wreck_weapons", model="naga_weapons", name="Scattered Tridents", at="wreck_3", kind="doodad", facing=4.0,
         phase=OVERTURNED),
    dict(key="burning_boards", model=BURNING_BOARDS, name="Burning Wreckage", at=["burn_1", "burn_2", "burn_3"],
         kind="doodad", facing=1.0, phase=OVERTURNED),
    dict(key="o_torch", model="naga_torch", name="Naga Torch", at=["o_torch_1", "o_vyssa"], kind="doodad", phase=OVERTURNED),
    # the dawn patrol's markers (7.01) round the islet before the raid; the fourth on the east point
    dict(key="marker", model="driftwood", name="Patrol Marker", kind="use", quest="ch7_quiet", consumable=True, respawn=60,
         at=["marker_1", "marker_2", "marker_3"], goal="Marker walked", phase=HOLLOW,
         beats=[("sound", "player", 1096)]),
    dict(key="marker_east", model="driftwood", name="East Marker", kind="use", quest="ch7_quiet", consumable=False,
         at="marker_4", goal="East marker walked", phase=HOLLOW,
         beats=[("object", "dead_fish", "fish_1", 600), ("object", "dead_fish_2", "fish_2", 600),
                ("object", "dead_fish", "fish_3", 600), ("object", "dead_fish_2", "fish_4", 600),
                ("object", "dead_fish", "fish_5", 600), ("object", "dead_fish_2", "fish_6", 600),
                ("face", "ch0:ssaveth", "marker_4"), ("state", "ch0:ssaveth", "none")]),
    dict(key="dead_fish", model=DEAD_FISH, name="Dead Fish", kind="doodad", scale=1.2),
    dict(key="dead_fish_2", model=DEAD_FISH_2, name="Dead Fish", kind="doodad", scale=1.2),
    # the pearl Serena dropped (7.04), under a fallen renegade
    dict(key="pearl_glint", model="great_pearl", name="Something Pale in the Sand", kind="loot",
         loot=[("cage_pearl", 1, 1)], quest="ch7_fallen_pearl", scale=0.12, respawn=30, at="pearl_glint", phase=OVERTURNED),

    # -- the raft's wake (7.11) ----------------------------------------------------------------------------------------
    dict(key="wake_kelp", model="kelp", name="Torn Kelp", kind="use", quest="ch7_wake", consumable=False, scale=1.4,
         at="wake_kelp", goal="Torn kelp in the raft's wake found", phase=OVERTURNED, beats=[("sound", "player", 1096)]),
    dict(key="hairpin_rock", model=BARNACLE_ROCK, name="Barnacled Rock", kind="loot", loot=[("hairpin", 1, 1)],
         quest="ch7_wake", scale=0.6, respawn=30, at="wake_rock", phase=OVERTURNED),
    dict(key="wake_lookout", model="driftwood", name="Ledge over the Cove", kind="use", quest="ch7_wake", consumable=False,
         at="lookout", facing=3.4, goal="The raft found", phase=OVERTURNED,
         beats=[("summon", "isshara_caged", "raft_isshara", 240), ("summon", "raft_prodder", "raft_prod", 240),
                ("wait", 2500), ("face", "raft_prodder", "raft_isshara"), ("emote", "raft_prodder", "attack2h"),
                ("wait", 2000), ("emote", "isshara_caged", "stun"), ("wait", 3000), ("face", "isshara_caged", "lookout"),
                ("emote", "isshara_caged", "spell")]),
    # the cove: the raft moored (boards, a cage, the Empress's banner)
    dict(key="raft_boards", model=FLOATING_BOARDS, name="Serena's Raft", at="raft", kind="doodad", scale=2.4, facing=1.2,
         phase=OVERTURNED),
    dict(key="raft_cage", model=CAGE, name="The Raft's Cage", at="raft_cage", kind="doodad", scale=0.9, facing=1.2,
         phase=OVERTURNED),
    dict(key="raft_banner", model="naga_banner", name="The Empress's Sigil", at="raft_banner", kind="doodad", facing=1.2,
         phase=OVERTURNED),

    # -- the Horde's line --------------------------------------------------------------------------------------------
    dict(key="line_tent", model=ORC_TENT, name="Valormok's Tent", at="line_tent", kind="doodad", facing=0.9, scale=0.9,
         phase=LINE),
    dict(key="line_banner", model=HORDE_BANNER, name="Valormok's Banner", at="line_banner", kind="doodad", facing=0.9,
         phase=LINE),
    dict(key="line_fire", model=CAMPFIRE, name="Campfire", at="line_fire", kind="doodad", phase=LINE),
    # the foot of Forlorn Ridge: the column's baskets and jars
    dict(key="foot_basket", model="basket", name="Tide-Broken Baskets", at=["foot_basket_1", "foot_basket_2"],
         kind="doodad", facing=1.0, phase=LINE),
    dict(key="foot_jar", model="naga_jar", name="Water Jars", at=["foot_jar_1", "foot_jar_2"], kind="doodad", phase=LINE),

    # -- the crater camp ------------------------------------------------------------------------------------------------
    dict(key="pool_water", model=POOL_WATER, name="The Crater's Pool", at="c_pool", kind="doodad", scale=1.6, phase=CRATER),
    dict(key="pool_stone", model=BARNACLE_ROCK, name="Pool Stone", at=["c_stone_1", "c_stone_2", "c_stone_3"],
         kind="doodad", scale=0.5, facing=0.8, phase=CRATER),
    dict(key="c_pagoda", model="naga_pagoda", name="Tide-Broken Pagoda", at=["c_pagoda_1", "c_pagoda_2"], kind="doodad",
         facing=0.6, phase=CRATER),
    dict(key="c_banner", model="naga_banner", name="Tide-Broken Banner", at=["c_banner_1", "c_banner_2"], kind="doodad",
         facing=0.3, phase=CRATER),
    dict(key="c_horde_banner", model=HORDE_BANNER, name="Valormok's Banner", at="c_north_in", kind="doodad", facing=2.6,
         phase=CRATER),
    dict(key="c_torch", model="naga_torch", name="Naga Torch", at=["c_torch_1", "c_torch_2", "c_torch_3", "c_torch_4"],
         kind="doodad", phase=CRATER),
    dict(key="c_crates", model="naga_crate", name="Salvaged Crates", at="c_crates", kind="doodad", facing=1.3, phase=CRATER),
    dict(key="c_jars", model="naga_jar", name="Water Jars", at="c_jars", kind="doodad", phase=CRATER),
    dict(key="c_bed", model=SEAWEED, name="Dried Kelp Bedding", at=["c_bed_1", "c_bed_2"], kind="doodad", scale=1.2,
         phase=CRATER),
    # the jars at Lake Mennar (7.20a), the mud (7.21), Valormok's water barrels (7.20b), the herald's shell (7.25)
    dict(key="lake_jar", model="naga_jar", name="Empty Water Jar", kind="loot", loot=[("lake_jar", 1, 2)],
         quest="ch7_water", scale=0.8, respawn=30, at=["jar_1", "jar_2", "jar_3", "jar_4", "jar_5"], phase=CRATER),
    dict(key="lake_mud", model=DIRT, name="Lake Mud", kind="loot", loot=[("mud", 1, 2)], quest="ch7_dry_scales",
         scale=0.6, respawn=30, at=["mud_1", "mud_2", "mud_3", "mud_4", "mud_5", "mud_6"], phase=CRATER),
    dict(key="water_barrel", model=WATER_BARREL, name="Valormok's Water Barrel", kind="use", quest="ch7_barrels",
         consumable=True, respawn=90, at=["barrel_1", "barrel_2", "barrel_3", "barrel_4"], goal="Water barrel rolled off",
         phase=CRATER,
         beats=[("sound", "player", 1183), ("summon", "arguing_grunt", "kurll_argue", 20), ("wait", 800),
                ("face", "arguing_grunt", "kurll"), ("emote", "arguing_grunt", "rude"),
                ("say", "arguing_grunt", "Cook! Where's the water? There was water here!"), ("wait", 2500),
                ("emote", "arguing_grunt", "point"), ("wait", 2000), ("emote", "arguing_grunt", "shout")]),
    dict(key="herald_shell", model=SHELL_2, name="A Herald's Shell", kind="loot", loot=[("herald_shell", 1, 1)],
         quest="ch7_price", scale=1.2, respawn=30, at="shell_spot", facing=2.0, phase=CRATER),
    dict(key="sand_line", model="naga_weapons", name="A Line in the Sand", kind="doodad", scale=0.4),

    # -- memory m13 ------------------------------------------------------------------------------------------------------
    dict(key="m13_rubble", model=OUTLAND_RUBBLE[0], name="Shattered Stone", at=["rub_1", "rub_2"], kind="doodad",
         facing=0.4, scale=1.2, phase=M13),
    dict(key="m13_rubble_2", model=OUTLAND_RUBBLE[1], name="Shattered Stone", at=["rub_3", "rub_4"], kind="doodad",
         facing=2.4, scale=1.3, phase=M13),
    dict(key="m13_rubble_3", model=OUTLAND_RUBBLE[2], name="Shattered Stone", at="rub_5", kind="doodad", facing=1.4,
         phase=M13),
    dict(key="m13_thorn", model=HELLFIRE_THORN, name="Thornbush", at=["thorn_1", "thorn_2", "thorn_3"], kind="doodad",
         phase=M13),
    dict(key="m13_fire", model=BE_CAMPFIRE, name="Campfire", at="m13_fire", kind="doodad", phase=M13),
    dict(key="m13_crates", model=BE_CRATE, name="Supplies", at=["m13_crate_1", "m13_crate_2"], kind="doodad", facing=0.8,
         phase=M13),
    dict(key="base_tent", model=NE_TENT, name="Watchers' Tent", at="base_tent", kind="doodad", facing=2.6, phase=M13),
    dict(key="base_lantern", model=NE_LANTERN, name="Lantern", at=["base_lantern_1", "base_lantern_2"], kind="doodad",
         phase=M13),
    dict(key="base_banner", model=NE_BANNER, name="Watchers' Banner", at="base", kind="doodad", facing=2.6, phase=M13),
    dict(key="spring", model=DIRT, name="Muddy Spring", kind="loot", loot=[("waterskin", 1, 1)], quest="ch7_three_days",
         scale=0.9, respawn=30, at=["spring_1", "spring_2", "spring_3", "spring_4", "spring_5", "spring_6"], phase=M13),
    dict(key="cage_object", model=CAGE, name="Maiev's Cage", kind="doodad", scale=1.3),

    # -- memory m14 ------------------------------------------------------------------------------------------------------
    dict(key="m14_fire", model=CAMPFIRE, name="Campfire", at="m14_fire", kind="doodad", phase=M14),
    dict(key="m14_rubble", model=OUTLAND_RUBBLE[3], name="Shattered Stone", at="m14_rub", kind="doodad", facing=0.9,
         phase=M14),
]

# -- items --------------------------------------------------------------------------------------------------------------
ITEMS = [
    dict(key="cage_pearl", name="Song-Pearl: The Cage", icon="pearl",
         description="Cold, the way Serena's hand is cold. Hold it near water and it hums."),
    dict(key="hairpin", name="Isshara's Hairpin", icon=12410,
         description="Coral and old silver. She wore it in her hair for ten thousand years."),
    dict(key="waterskin", name="Waterskin of Brown Water", icon="item:159", stack=6,
         description="Mud, mostly. It's what there is."),
    dict(key="lake_jar", name="Heavy Jar of Lake Water", icon="item:159", stack=8, carry="heavy_jar",
         description="Lake Mennar, cold and clean, and very heavy."),
    dict(key="mud", name="Lump of Lake Mennar Mud", icon="item:7067", stack=8,
         description="Cool and grey and it smells of the lake."),
    dict(key="herald_shell", name="A Herald's Shell", icon="shell",
         description="Serena's hand, scratched on the inside: \"Your memories for your lives. Give the keeper's pearls back "
                     "to the Empress's water and you may keep your tails. Refuse, and I will sing you all empty. The tide "
                     "always turns back.\""),

    # rewards (the game's quests' greens at these levels)
    dict(key="fleet_mantle", name="Fleet-Breaker Mantle", kind="armor:cloth:shoulder", quality=2, level=38,
         stats=[("int", 7), ("sta", 6), ("spi", 4)]),
    dict(key="fleet_spaulders", name="Hollow-Watch Spaulders", kind="armor:leather:shoulder", quality=2, level=38,
         stats=[("agi", 8), ("sta", 7)]),
    dict(key="fleet_pauldrons", name="Hollow-Guard Pauldrons", kind="armor:mail:shoulder", quality=2, level=38,
         stats=[("str", 8), ("sta", 7)]),
    dict(key="brown_water", name="Brackish Waterskin", kind="drink", level=35, icon="item:159"),
    dict(key="dust_staff", name="Staff of the Red Waste", kind="weapon:staff", quality=2, level=39,
         stats=[("int", 13), ("sta", 9), ("spi", 8)]),
    dict(key="cage_spear", name="Cage-Breaker Trident", kind="weapon:spear", quality=2, level=39,
         stats=[("str", 13), ("sta", 11)]),
    dict(key="cage_dagger", name="Watcher's Lost Knife", kind="weapon:dagger", quality=2, level=39,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="keeper_gloves", name="Keeper's Wraps", kind="armor:cloth:hands", quality=2, level=40,
         stats=[("int", 7), ("sta", 6), ("spi", 4)]),
    dict(key="hauler_grips", name="Raft-Hauler's Grips", kind="armor:leather:hands", quality=2, level=40,
         stats=[("agi", 8), ("sta", 6)]),
    dict(key="frost_gauntlets", name="Frostbreaker Gauntlets", kind="armor:mail:hands", quality=2, level=40,
         stats=[("str", 8), ("sta", 7)]),
    dict(key="three_cups_shroud", name="Shroud of Three Cups", kind="armor:cloth:back", quality=2, level=41,
         stats=[("sta", 6), ("spi", 6)]),
    dict(key="singer_band", name="The Singer's Band", kind="ring", quality=2, level=41, stats=[("int", 6), ("sta", 5)]),
    dict(key="shore_band", name="Band of the Shore", kind="ring", quality=2, level=41, stats=[("str", 5), ("agi", 5), ("sta", 3)]),
    dict(key="ridge_sandals", name="Ridge-Climber's Sandals", kind="armor:cloth:feet", quality=2, level=41,
         stats=[("int", 7), ("sta", 7), ("spi", 4)]),
    dict(key="ridge_boots", name="Ridgewalker Boots", kind="armor:leather:feet", quality=2, level=41,
         stats=[("agi", 8), ("sta", 8)]),
    dict(key="ridge_greaves", name="Forlorn Greaves", kind="armor:mail:feet", quality=2, level=41,
         stats=[("str", 8), ("sta", 8)]),
    dict(key="crater_water", name="Crater Pool Water", kind="drink", level=40, icon="item:159"),
    dict(key="rim_sash", name="Rimwatch Sash", kind="armor:cloth:waist", quality=2, level=42,
         stats=[("int", 8), ("sta", 7), ("spi", 4)]),
    dict(key="rim_belt", name="Rimwatch Belt", kind="armor:leather:waist", quality=2, level=42,
         stats=[("agi", 9), ("sta", 7)]),
    dict(key="rim_girdle", name="Rimwatch Girdle", kind="armor:mail:waist", quality=2, level=42,
         stats=[("str", 9), ("sta", 7)]),
    dict(key="valormok_axe", name="Valormok War Axe", kind="weapon:axe", quality=2, level=42, stats=[("str", 7), ("sta", 6)]),
    dict(key="valormok_bow", name="Wind Rider's Longbow", kind="weapon:bow", quality=2, level=42, stats=[("agi", 6), ("sta", 4)]),
    dict(key="valormok_rod", name="Warcaller's Totem Rod", kind="weapon:staff", quality=2, level=42,
         stats=[("int", 14), ("sta", 10), ("spi", 8)]),
    dict(key="crater_leggings", name="Leggings of the Dry Crater", kind="armor:cloth:legs", quality=2, level=43,
         stats=[("int", 11), ("sta", 10), ("spi", 7)]),
    dict(key="crater_breeches", name="Crater-Dust Breeches", kind="armor:leather:legs", quality=2, level=43,
         stats=[("agi", 12), ("sta", 11)]),
    dict(key="crater_legguards", name="Legguards of the Keeper's Watch", kind="armor:mail:legs", quality=2, level=43,
         stats=[("str", 12), ("sta", 11)]),
]

# -- auras ---------------------------------------------------------------------------------------------------------------
AURAS = [
    # 7.05: the keeper's craft is the player's from now on (chapter 8's "Keeper's Voice": ch7:keepers_voice)
    dict(key="keepers_voice", name="Keeper's Voice", kind="mark", seconds=0, icon=12508,
         text="Isshara's craft, and now yours: lay a Song-Pearl in seawater and sing it, and whoever touches the water "
              "lives what it holds."),
    dict(key="serena_frost", name="Serena's Frost", kind="root", seconds=16, icon=122, visual=7406,
         text="Frozen where you stand. The ice won't break."),
    dict(key="heavy_jar", name="Heavy Jar", kind="slow", percent=30, seconds=0, icon=42336,
         text="Lake water, up a mountain, in a jar. Slowly."),
    dict(key="kj_storm", name="The Storm", kind="screen", screen=222, seconds=24),
    dict(key="mud_grey", name="Mud-Grey Scales", kind="mark", seconds=900, icon=10255,
         text="Lake Mennar mud, plastered on. It cracks when you smile."),
]

# -- memories -------------------------------------------------------------------------------------------------------------
MEMORIES = [
    dict(key="m13", name="The Dusts of Outland", whose="Isshara", bit="B", screen=161,
         text="Isshara's memory, sung by you: Outland, the dust, and the Watchers' cage. What she saw, you see.",
         stage="m13_arrive", facing=5.7, centre="m13_centre", radius=235, pool="ch2:pool_shore", pool_facing=5.0,
         singer="ch0:vyssa", again="Hold the basin for me. I'll sing the dust again."),
    dict(key="m14", name="Illidan's Task", whose="Isshara", bit="B",
         text="Isshara's last memory, sung by her to you: the night in the dust when Illidan told them why he fled.",
         stage="m14_arrive", facing=5.5, centre="m14_centre", radius=70, pool="line_wake", pool_facing=0.2,
         singer="isshara_dying", again="Sing it once more, keeper. I'm listening."),
]

# -- quests ---------------------------------------------------------------------------------------------------------------
QUESTS = [
    # 7.01: quiet on the bay (boring, until the fourth marker)
    dict(key="ch7_quiet", title="Quiet on the Bay", giver="ch0:ssaveth", ender="ch0:ssaveth", level=38, xp=8,
         tone="boring", prev="ch6:ch6_end", objects=[("marker", 3), ("marker_east", 1)],
         goal="Walk Ssaveth's dawn patrol: touch the four driftwood markers round the Hollow's islet, and report back.",
         text="Dawn patrol. Four markers, round the islet, touch each one so I know you were there. West end, north "
              "shore, south shore, the east point. Watch the water while you walk. Nothing ever happens. That's the point "
              "of a patrol.",
         progress="All four? The east point too?",
         reward="Dead fish. All along the east shore, belly-up, and the water flat as a plate. ...A siren's song does "
                "that. Sung under the water, all night, close. Nothing ever happens. Get Szaria. Now.",
         details=["talk"], reward_emotes=["talk", "battle_roar"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "marker_1"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "marker_4"), ("emote", "self", "spell"),
                 ("wait", 1500), ("face", "self", "player"), ("state", "self", "ready_thrown")],
         complete=[("state", "self", "none"), ("face", "self", "east_sea"), ("wait", 2500), ("emote", "self", "talk"),
                   ("wait", 1500), ("emote", "self", "roar"), ("sound", "self", "naga_aggro"), ("wait", 1500),
                   ("face", "self", "ch1:hollow_szaria"), ("emote", "self", "battle_roar")],
         poi=["marker_1", "marker_2", "marker_3", "marker_4"]),

    # 7.02: the envoy's fleet (a set piece, timed: six minutes for fifteen Spitelash)
    dict(key="ch7_overturned", title="The Envoy's Fleet", giver="ch0:szaria", ender="ch0:szaria", level=38, xp=8,
         tone="serious", prev="ch7_quiet", time=360, kill=[("royal_guard", 8), ("attack_siren", 7)],
         goal="Hold the Hollow against Serena's fleet: kill 8 Spitelash Royal Guards and 7 Spitelash Sirens as they come "
              "up out of the bay, within 6 minutes.",
         text="Conches. Hear them? Out in the bay, all round us. She's not sending a herald this time. Every trident to "
              "the west beach, now. Keep them off the sand, keep them off the pool. Whatever she's singing out there, "
              "don't listen to it.",
         progress="Fight! The sand, hold the sand!",
         reward="They've gone back into the water. All of them, at once, the way a wave goes. ...Look at the camp. Look at "
                "the pool. That wasn't an attack. That was someone clearing a table.",
         details=["battle_roar"], reward_emotes=["talk"], choice=["fleet_mantle", "fleet_spaulders", "fleet_pauldrons"],
         accept=[("sound", "self", HORN), ("music", MUSIC_BATTLE), ("summon", "serena_sing", "serena_rock", 200),
                 ("face", "self", "land_2"), ("yell", "self", "To the beach! Every trident to the west beach!", "battle_roar"),
                 ("sound", "self", "siren_aggro"), ("emote", "ch0:ssaveth", "battle_roar"),
                 ("sound", "ch0:ssaveth", "naga_aggro"), ("emote", "ch2:sentry", "battle_roar"), ("wait", 3000),
                 # the first rows, out of the bay
                 ("summon", "royal_guard", "rise_1", 300), ("summon", "royal_guard", "rise_2", 300),
                 ("summon", "attack_siren", "rise_3", 300), ("wait", 800),
                 ("yell", "royal_guard", "Drown them all!", None, "NagaRoyalGuardYesAttack1"), ("sound", "self", HORN),
                 ("wait", 16000),
                 ("summon", "royal_guard", "rise_4", 300), ("summon", "attack_siren", "rise_5", 300),
                 ("summon", "attack_siren", "rise_6", 300), ("wait", 18000),
                 # the pool: a siren's bolt over the camp, the keeper's water thrown up and the basin knocked flat
                 ("visual", "ch2:keepers_pool", EXPLOSION), ("sound", "ch2:keepers_pool", QUAKE),
                 ("visual", "ch2:keepers_pool", SPOUT), ("state", "ch0:isshara", "stun"), ("emote", "ch0:vyssa", "wound"),
                 ("sound", "ch0:vyssa", "naga_wound"), ("summon", "royal_guard", "rise_2", 300),
                 ("summon", "royal_guard", "rise_5", 300), ("summon", "attack_siren", "rise_1", 300), ("wait", 18000),
                 ("yell", "self", "Back! Back to the dune, all of you! Ssaveth, hold the line for them!", "battle_roar"),
                 ("move", "ch0:vyssa", "fallback_1", "run"), ("move", "ch2:sentry", "fallback_2", "run"),
                 ("move", "ch2:camp_siren", "fallback_3", "run"),
                 ("summon", "royal_guard", "rise_3", 300), ("summon", "attack_siren", "rise_4", 300),
                 ("summon", "attack_siren", "rise_6", 300), ("wait", 18000),
                 ("summon", "royal_guard", "rise_1", 300), ("summon", "royal_guard", "rise_6", 300),
                 ("summon", "attack_siren", "rise_2", 300), ("sound", "self", HORN), ("wait", 18000),
                 ("summon", "royal_guard", "rise_4", 300), ("summon", "royal_guard", "rise_5", 300),
                 ("summon", "attack_siren", "rise_3", 300), ("summon", "attack_siren", "rise_1", 300), ("wait", 20000),
                 ("summon", "royal_guard", "rise_2", 300), ("summon", "attack_siren", "rise_5", 300),
                 ("summon", "royal_guard", "rise_6", 300), ("wait", 4000), ("state", "ch0:isshara", "none"),
                 ("move", "ch0:vyssa", "ch2:vyssa", "walk"), ("move", "ch2:sentry", "ch2:sentry_1", "walk"),
                 ("move", "ch2:camp_siren", "ch2:siren_1", "walk")],
         complete=[("face", "self", "ch2:isshara"), ("wait", 2000), ("emote", "self", "talk"), ("wait", 1500),
                   ("face", "self", "serena_rock"), ("emote", "self", "roar"), ("sound", "self", "siren_aggro"),
                   ("wait", 2000), ("face", "self", "player")],
         poi=["land_2"]),

    # 7.03: taken (the frost you can't break; the raft away north-east along the bay)
    dict(key="ch7_taken", title="Taken", giver="ch0:szaria", ender="ch0:szaria", level=38, xp=8, tone="serious",
         prev="ch7_overturned", event="The keeper taken", poi=["ch2:isshara"],
         goal="Run to Isshara at her pool on the Hollow's east end.",
         text="Isshara. Where's Isshara? She was at the pool when the first conch went, and nobody's seen her since. "
              "Find her. Go!",
         progress="Is she there? Is she there?",
         reward="I saw. All of it, from here, and I couldn't move either. Ice to the knees and that woman's voice in my "
                "ears. ...She knew exactly who to take. Of course she did. She unsung her.",
         details=["battle_roar"], reward_emotes=["talk"],
         accept=[("summon", "isshara_taken", "ch2:isshara", 90), ("emote", "self", "talk"), ("wait", 4000),
                 ("summon", "serena", "serena_near", 60), ("visual", "serena", WATER), ("sound", "serena", "splash_big"),
                 ("summon", "honor_guard_1", "guard_rise_1", 60), ("summon", "honor_guard_2", "guard_rise_2", 60),
                 ("wait", 2500), ("face", "serena", "player"), ("emote", "serena", "spell"), ("visual", "serena", FROST_HAND),
                 ("sound", "serena", FROST_NOVA), ("aura", "player", "serena_frost"), ("emote", "self", "stun"),
                 ("wait", 1500),
                 ("move", "honor_guard_1", "seize_1", "walk"), ("move", "honor_guard_2", "seize_2", "walk"), ("wait", 3500),
                 ("face", "isshara_taken", "player"), ("emote", "isshara_taken", "spell"),
                 ("say", "isshara_taken", "Little one? I hear you. Stay where you are. Stay."), ("wait", 3500),
                 ("summon", "serena_raft", "raft_dock", 60), ("move", "isshara_taken", "raft_dock", "walk"),
                 ("move", "honor_guard_1", "raft_dock", "walk"), ("move", "honor_guard_2", "raft_dock", "walk"),
                 ("wait", 5500), ("face", "isshara_taken", "player"), ("emote", "isshara_taken", "spell"),
                 ("sound", "isshara_taken", "siren_hiss"), ("wait", 2000),
                 ("say", "serena", "The tide always turns back.", "talk"), ("wait", 3000),
                 ("move", "serena_raft", "raft_away_1", "walk"), ("move", "isshara_taken", "raft_away_1", "walk"),
                 ("move", "honor_guard_1", "raft_away_1", "walk"), ("move", "honor_guard_2", "raft_away_1", "walk"),
                 ("visual", "serena", WATER), ("despawn", "serena"), ("wait", 9000),
                 ("move", "serena_raft", "raft_away_2", "walk"), ("move", "isshara_taken", "raft_away_2", "walk"),
                 ("move", "honor_guard_1", "raft_away_2", "walk"), ("move", "honor_guard_2", "raft_away_2", "walk"),
                 ("wait", 4000), ("unaura", "player", "serena_frost"), ("credit", "ch7_taken"), ("emote", "self", "roar"),
                 ("sound", "self", "siren_aggro")],
         complete=[("face", "self", "raft_away_2"), ("wait", 2500), ("emote", "self", "work"), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "talk")]),

    # 7.04: the fallen pearl (Vyssa digs in the overturned pool with her hands)
    dict(key="ch7_fallen_pearl", title="The Fallen Pearl", giver="ch0:vyssa", ender="ch0:vyssa", level=38, xp=8,
         tone="serious", prev="ch7_taken", items=[("cage_pearl", 1)], poi=["pearl_glint"],
         goal="Search the wrecked camp for the Song-Pearl Serena dropped, and bring it to Vyssa at the keeper's basin.",
         text="She dropped something. When the ice went over you, I saw it fall out of her hand, white, into the sand by "
              "the dead. A pearl. One of Isshara's. I can't... I've looked by the basin. I can't look over there. You "
              "look. Please.",
         progress="Did you find it? Is it whole?",
         reward="It's whole. It's cold, the way her hand is cold. ...That one was under Thessik? Under him. He was "
                "holding it. Of course he was. Give it here. Gently.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "work"), ("wait", 2500), ("state", "self", "none"), ("face", "self", "dead_2"),
                 ("emote", "self", "spell"), ("wait", 2000), ("visual", "self", WATER), ("sound", "self", "pickup_water"),
                 ("wait", 1500), ("face", "self", "basin"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("visual", "self", HOLY_NOVA), ("wait", 2500),
                   ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", WATER), ("sound", "self", "pickup_water")]),

    # 7.05: is it time? (the player sings for the first time; a voice answers out of the water)
    dict(key="ch7_time", title="Is It Time?", giver="ch0:vyssa", ender="ch0:isshara_young", level=38, xp=8,
         tone="serious", prev="ch7_fallen_pearl", memory="m13", source="cage_pearl", poi=["basin", "m13_isshara"],
         use=[("cage_pearl", "basin_use", 1,
               [("visual", "player", GLOW_BLUE), ("visual", "pool_voice", WATER), ("wait", 4500),
                ("say", "pool_voice", "Is it time?", None, "LadyVashjWhat1"), ("wait", 2500),
                ("aura", "player", "keepers_voice"), ("music", MUSIC_NAGA), ("wait", 2000), ("relive", "m13"),
                ("wait", 1500), ("unaura", "player", GLOW_BLUE)])],
         goal="Lay Song-Pearl: The Cage in the water of the keeper's basin at the Hollow, and listen until something "
              "answers. In the song, find young Isshara in the prince's camp.",
         text="Nobody's left to sing it. Szaria can't, she's never had the voice. I can't, I only ever cooked for the "
              "ones who could. So it's you. She taught you more than she taught any of us, she just didn't say so. Right "
              "the basin. Lay the pearl in the water. Don't sing yet. Listen first. Something will tell you when.",
         progress="Listen. Just listen.",
         reward="You! You came up through the dust. Don't stare at the sky, the sky's red here, it's red everywhere. "
                "Outland, the prince calls it. Keep your eyes on the ground and your hands near your trident.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("state", "self", "none"), ("face", "self", "basin"), ("emote", "self", "work"), ("sound", "self", 1194),
                 ("wait", 2000), ("visual", "pool_voice", WATER), ("sound", "self", "pickup_water"), ("wait", 1500),
                 ("emote", "self", "work"), ("visual", "self", WATER), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "m13_overlook"),
                   ("emote", "self", "talk")]),

    # 7.06: the dusts of Outland (Kael and Vashj on the plateau's edge)
    dict(key="ch7_dusts", title="The Dusts of Outland", giver="ch0:isshara_young", ender="ch0:isshara_young", level=39,
         xp=8, tone="serious", prev="ch7_time", memory="m13", explore="m13_overlook", radius=12, poi=["m13_overlook"],
         goal="In Isshara's memory, go with Prince Kael'thas and Lady Vashj to the edge of the plateau over the waste.",
         text="The prince wants to see it. Everything. Lady Vashj says we've marched for hours and he still looks at "
              "the sky like it owes him money. Go with them to the edge. Stand behind her, not beside. Listen.",
         progress="Go on, to the edge. They're waiting.",
         reward="All that remains of Draenor. She said it like a tide-chart. And the prince... he wants a cure. I think he "
                "thinks the master is a healer.",
         details=["point"], reward_emotes=["talk"],
         accept=[("face", "self", "m13_overlook"), ("emote", "self", "point"), ("move", "kael_m13", "kael_look", "walk"),
                 ("move", "vashj_m13", "vashj_look", "walk"), ("wait", 12000), ("face", "kael_m13", "waste"),
                 ("face", "vashj_m13", "waste"),
                 ("say", "kael_m13", "What is this desolate place, Vashj?", "talk"), ("wait", 3500),
                 ("say", "vashj_m13", "This shattered world is called Outland, young prince. It is all that remains of "
                                      "Draenor, the former homeland of the orcish Horde.", "talk"), ("wait", 6500),
                 ("say", "kael_m13", "Amazing. I remember when Khadgar led the Alliance Expedition here, years ago. He "
                                     "almost succeeded in wiping the orcs out for good.", "talk"), ("wait", 6500),
                 ("say", "kael_m13", "In an attempt to escape, Ner'zhul opened a number of massive dimensional gateways, "
                                     "but all they succeeded in doing was tearing the planet apart."), ("wait", 6500),
                 ("emote", "vashj_m13", "spell"),
                 ("say", "vashj_m13", "Yes. And now, amongst the ruins of this dead world, we have come to find the "
                                      "master."), ("wait", 5000),
                 ("say", "kael_m13", "Illidan... why here? What could possibly interest him in this barren wasteland?",
                  "talk"), ("wait", 5000),
                 ("say", "vashj_m13", "That I do not know. Regardless, we should seek him out quickly."), ("wait", 4500),
                 ("say", "kael_m13", "Agreed. Actually, I am anxious to meet him again. If he can cure my people of their "
                                     "hunger for magic, I will gladly pledge myself to his service.", "talk"),
                 ("wait", 7000), ("move", "kael_m13", "m13_kael", "walk"), ("move", "vashj_m13", "m13_vashj", "walk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "m13_kael"),
                   ("emote", "self", "shy")]),

    # 7.07: three days lost (boring: the springs are mud; Vashj drinks last)
    dict(key="ch7_three_days", title="Three Days Lost", giver="ch0:isshara_young", ender="ch0:isshara_young", level=39,
         xp=8, tone="boring", prev="ch7_dusts", memory="m13", items=[("waterskin", 6)], poi=["springs"],
         rewards=["brown_water"],
         goal="In Isshara's memory, fill 6 Waterskins of Brown Water at the muddy springs in the dry basin east of the "
              "camp, and bring them to young Isshara.",
         text="Three days. Three days of walking over red stone and nobody has found the master, or a tree, or a cloud. "
              "There are springs in the hollow to the east. Springs is a kind word. Fill the skins anyway. Six. The "
              "elves are starting to look at us like we're the water.",
         progress="Six skins. Even brown water is water.",
         reward="Mud. Six skins of mud. Watch: the elves first, then the host, then us. She drinks last. Every time. "
                "Don't say anything about it. She'll know you noticed and she'll hate it.",
         details=["talk"], reward_emotes=["eat"],
         accept=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "springs"), ("emote", "self", "point"),
                 ("wait", 1500), ("emote", "host_naga", "cry"), ("face", "self", "player"), ("emote", "self", "laugh")],
         complete=[("emote", "self", "eat"), ("emote", "kael_elf", "eat"), ("wait", 2500), ("emote", "host_naga", "eat"),
                   ("emote", "kael_m13", "talk"), ("wait", 3000), ("face", "vashj_m13", "m13_fire"),
                   ("emote", "vashj_m13", "work"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "shy")]),

    # 7.08: the scent (Vashj smells them before anyone sees them; the cage on the Watchers' road)
    dict(key="ch7_scent", title="The Scent", giver="ch0:isshara_young", ender="ch0:isshara_young", level=39, xp=8,
         tone="serious", prev="ch7_three_days", memory="m13", explore="m13_scent", radius=12, poi=["m13_scent"],
         goal="In Isshara's memory, scout ahead with Lady Vashj and the prince to the rise over the Watchers' road.",
         text="Lady Vashj stopped in the middle of a sentence and tasted the air. Then she went that way without a word, "
              "and the prince went after her. She smelled something. Go. Quietly. I'll keep the host here.",
         progress="What is it? What did she smell?",
         reward="Night elves. Here. The warden's Watchers, all the way through the portal after him, and they've got "
                "him in a cage on wheels. Lady Vashj's tail hasn't stopped twitching since she saw it.",
         details=["point"], reward_emotes=["talk"],
         accept=[("face", "self", "m13_scent"), ("emote", "self", "point"), ("face", "kael_m13", "m13_scent"),
                 ("say", "kael_m13", "This place is unnerving. We've marched for three days and seen no signs of life. "
                                     "Still, I can't shake the feeling that we're not alone out here.", "talk"),
                 ("wait", 7000), ("face", "vashj_m13", "base"), ("emote", "vashj_m13", "spell"),
                 ("say", "vashj_m13", "We aren't. I caught the scent just as the wind shifted..."), ("wait", 3500),
                 ("move", "vashj_m13", "vashj_scent", "run"), ("move", "kael_m13", "kael_scent", "run"),
                 ("face", "self", "player"), ("emote", "self", "shy")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "base"),
                   ("emote", "self", "ready_bow")]),

    # 7.09: the cage (the tug: taken, lost, taken again)
    dict(key="ch7_illidans_cage", title="The Cage", giver="ch0:isshara_young", ender="ch0:isshara_young", level=39,
         xp=8, tone="serious", prev="ch7_scent", memory="m13", kill=[("cage_hauler", 3)], poi=["cg_mid", "cg_end"],
         event="Illidan's cage brought to the prince's camp",
         tug=dict(cart="illidan_cage", path=["cg_1", "cg_2", "cg_mid", "cg_4", "cg_5", "cg_end"], midpoint="cg_mid",
                  enemies=[("watcher_retaker", "rt_1"), ("watcher_retaker", "rt_2"), ("watcher_retaker", "rt_3")],
                  taken=[("summon", "maiev_m13", "maiev_spot", 25), ("visual", "maiev_m13", BLINK),
                         ("yell", "maiev_m13", "I grow tired of these games! Illidan will be mine!"), ("wait", 3500),
                         ("say", "maiev_m13", "For the Watchers!", None, "MaievYesAttack1"), ("wait", 2000),
                         ("say", "kael_m13", "Damn! We lost the cage!"), ("wait", 3000),
                         ("say", "vashj_m13", "There is still time, Kael. If we move quickly, we can reclaim it before "
                                              "the night elves reach sanctuary."), ("wait", 5000),
                         ("say", "kael_m13", "They've retaken the cage! We must get it back!"), ("wait", 4000),
                         ("visual", "maiev_m13", BLINK), ("despawn", "maiev_m13")],
                  retaken=[("visual", "self", ARCANE_BOOM), ("emote", "kael_m13", "spell"), ("emote", "vashj_m13", "battle_roar"),
                           ("wait", 2500), ("move", "kael_m13", "m13_kael", "walk"), ("move", "vashj_m13", "m13_vashj", "walk")],
                  radius=45, seconds=420),
         goal="In Isshara's memory, kill the 3 Watcher Cage-Haulers on the road through the waste, take Illidan's cage, "
              "and stay with it until it rolls into the prince's camp.",
         text="Now. Lady Vashj and the prince are going down onto the road and the host goes with them. The haulers "
              "first: three of them, on the yoke. When the cage is ours, stay beside it all the way back to camp. They'll "
              "try to take it back. They'll fail.",
         progress="Stay with the cage!",
         reward="It's in the camp. It's ours. He's in there, I could feel him through the bars, like standing next to a "
                "fire you can't see. The prince is pacing. The lock won't open for him.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro"), ("move", "kael_m13", "kael_fight", "run"),
                 ("move", "vashj_m13", "vashj_fight", "run"), ("summon", "cage_hauler", "ha_1", 420),
                 ("summon", "cage_hauler", "ha_2", 420), ("summon", "cage_hauler", "ha_3", 420), ("music", MUSIC_BATTLE),
                 ("wait", 4000), ("emote", "host_naga", "battle_roar")],
         complete=[("emote", "self", "roar"), ("wait", 1500), ("face", "self", "cage_spot"), ("emote", "self", "talk"),
                   ("emote", "host_naga", "cheer")]),

    # 7.10: most timely (Vashj breaks the cage; the master and the prince; the fade)
    dict(key="ch7_timely", title="Most Timely", giver="ch0:isshara_young", ender="ch0:vyssa", level=39, xp=8,
         tone="serious", prev="ch7_illidans_cage", memory="m13", wake=True, event="The cage broken",
         choice=["dust_staff", "cage_spear", "cage_dagger"], poi=["cage_spot"],
         goal="In Isshara's memory, stand by while Lady Vashj breaks Maiev's cage in the prince's camp.",
         text="The prince says the lock will take days. Lady Vashj says it won't. Stand with the host. You'll want to "
              "remember this part.",
         progress="...",
         reward="You're back. Look at your hands, you're shaking. Sit. ...You took it, and they took it back, and you took "
                "it again. Just like that. She used to say the song shows you the shape of a thing so your hands know it "
                "when it comes.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("object", "cage_object", "cage_spot", 14), ("summon", "illidan_m13", "cage_spot", 75),
                 ("state", "illidan_m13", "stun"), ("move", "kael_m13", "m13_isshara", "walk"),
                 ("say", "kael_m13", "Illidan is unconscious, and his magical lock will take too long to open out here!",
                  "talk"), ("wait", 4500), ("move", "vashj_m13", "cg_end", "walk"), ("wait", 3000),
                 ("face", "vashj_m13", "cage_spot"), ("state", "vashj_m13", "channel_directed"),
                 ("visual", "vashj_m13", FROST_HAND), ("sound", "vashj_m13", "siren_hiss"), ("wait", 5000),
                 ("visual", "illidan_m13", ARCANE_BOOM), ("sound", "vashj_m13", 1277), ("state", "vashj_m13", "none"),
                 ("wait", 2000), ("state", "illidan_m13", "none"), ("visual", "illidan_m13", 35411),
                 ("say", "illidan_m13", "I have been caged in darkness.", None, "IllidanPissed1"), ("wait", 3500),
                 ("face", "illidan_m13", "cg_end"),
                 ("say", "illidan_m13", "Lady Vashj, your rescue was most timely. The thought of spending another ten "
                                        "thousand years in Maiev's prison was not a pleasant one."), ("wait", 7000),
                 ("say", "vashj_m13", "We could not forsake you, Lord Illidan. But you owe your freedom to them."),
                 ("wait", 3500), ("face", "vashj_m13", "m13_kael"), ("emote", "vashj_m13", "spell"), ("wait", 2000),
                 ("face", "illidan_m13", "m13_isshara"),
                 ("say", "illidan_m13", "Who are they, Vashj? The young elf looks familiar, but..."), ("wait", 4500),
                 ("say", "vashj_m13", "They call themselves the blood elves, my lord. They are the last mortal "
                                      "descendants of the Highborne who served you long ago."), ("wait", 6500),
                 ("say", "vashj_m13", "This is Prince Kael'thas. He and his brethren have come to bask in your "
                                      "wisdom--and pledge themselves to your will."), ("wait", 6000),
                 ("emote", "kael_m13", "talk"), ("emote", "kael_elf", "kneel"), ("emote", "host_naga", "bow"),
                 ("wait", 3000), ("credit", "ch7_timely"), ("wait", 8000), ("move", "kael_m13", "m13_kael", "walk"),
                 ("move", "vashj_m13", "m13_vashj", "walk"), ("despawn", "illidan_m13")],
         complete=[("face", "self", "player"), ("say", "self", "Now you know how to take a cage."), ("wait", 2500),
                   ("visual", "self", WATER), ("sound", "self", "pickup_water"), ("emote", "self", "work")]),

    # 7.11: the raft's wake (torn kelp; her hairpin, dropped for you; the raft moored in the cove)
    dict(key="ch7_wake", title="The Raft's Wake", giver="ch0:ssaveth", ender="ch0:ssaveth", level=40, xp=8,
         tone="serious", prev="ch7_timely", objects=[("wake_kelp", 1), ("wake_lookout", 1)], items=[("hairpin", 1)],
         poi=["wake_kelp", "wake_rock", "lookout"],
         goal="Follow the raft's wake east along the Shattered Strand: find the torn kelp in the bay, search the "
              "barnacled rock past the stone islet, and climb to the ledge over the cove under the Bitter Reaches' "
              "cliffs. Then come back to Ssaveth.",
         text="The raft went north-east, along the strand, towed. Towed means slow. Slow means a wake, and a wake means "
              "something torn. Follow it. Swim deep, come up only to look. If you find her, don't go in. Come back and "
              "tell me where.",
         progress="Where is she?",
         reward="Her hairpin. On a rock. She dropped it there for us; she knew we'd look; she's blind, not stupid. ...The "
                "cove under the Reaches. Guards on the beach and her in a cage on the water. I'll keep this. She'll want "
                "it back.",
         details=["talk"], reward_emotes=["roar"],
         accept=[("state", "self", "none"), ("face", "self", "east_sea"), ("emote", "self", "spell"), ("wait", 2000),
                 ("emote", "self", "work"), ("sound", "self", 977), ("wait", 1500), ("face", "self", "player"),
                 ("state", "self", "ready_thrown")],
         complete=[("state", "self", "none"), ("emote", "self", "work"), ("wait", 2000), ("face", "self", "east_sea"),
                   ("emote", "self", "roar"), ("sound", "self", "naga_aggro"), ("wait", 2000), ("face", "self", "player"),
                   ("state", "self", "ready_thrown")]),

    # 7.12: Valormok rides (hero): the warcaller, the whistle, the grunts running for their axes, Taelon's sword
    dict(key="ch7_rides", title="Valormok Rides", giver="ch0:szaria", ender=AGTOR, level=40, xp=8, tone="serious",
         path="hero", prev="ch7_wake", rep=[(76, 350)], poi=["ruzga"],
         interact=[("ruzga", "Ask the warcaller to bring you before the chief: the Spitelash have taken the keeper.")],
         interact_goal="Ag'tor told",
         interact_beats=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "agtor"),
                         ("yell", "self", "Chief! The fish-folk's old singer. The Spitelash took her. Dragged her off on a "
                                          "raft, east, to the Reaches.", "shout"), ("wait", 4500),
                         ("sound", "self", ORC_WHISTLE), ("wait", 1000), ("sound", "self", HORN),
                         ("summon", "runner_1", "barracks", 40), ("summon", "runner_2", "barracks", 40),
                         ("summon", "runner_3", "rack", 40), ("face", "ch6:taelon", "agtor"), ("emote", "ch6:taelon", "ready1h"),
                         ("state", "ch6:taelon", 333), ("wait", 800),
                         ("move", "runner_1", "rack", "run"), ("move", "runner_2", "rack", "run"), ("emote", "runner_3", "roar"),
                         ("sound", "runner_3", ORC_ROAR), ("move", "ch6:taelon", "taelon_v", "run"), ("wait", 3000),
                         ("move", "runner_1", "east_gate", "run"), ("move", "runner_2", "east_gate", "run"),
                         ("move", "runner_3", "east_gate", "run"), ("emote", "self", "roar"), ("wait", 4000),
                         ("face", "ch6:taelon", "player"),
                         ("say", "ch6:taelon", "Nobody should be put in a cage for what they remember. I'm coming."),
                         ("wait", 3500), ("state", "ch6:taelon", "none"), ("move", "ch6:taelon", "ch6:taelon", "walk"),
                         ("face", "self", "player")],
         goal="Go to Valormok, the orcs' camp on the hills west of the bay, and have Warcaller Ruzga bring you before "
              "Ag'tor Bloodfist. Then speak to Ag'tor.",
         text="She's in a cage in that cove, and I've thirty tridents, half of them hurt. The Spitelash have a hundred. "
              "...Valormok has orcs. Ag'tor has a horn and a temper and a debt he thinks we don't remember. Go and ask "
              "him. Ask, mind. Not beg. We don't beg.",
         progress="",
         reward="I heard your warcaller. Half of Azshara heard her. An old blind singer, on a raft, and that frost-woman "
                "who looks at my camp from the water at night. ...Hah. You see my grunts running? That's your answer, "
                "snake. Valormok rides. Get to your cove.",
         details=["talk", "point"], reward_emotes=["roar", "talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "agtor"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player")],
         complete=[]),

    # 7.13: the raft guards (grunts and myrmidons side by side; the wind riders over the cove)
    dict(key="ch7_raft_guards", title="The Raft Guards", giver=AGTOR, ender="ch0:ssaveth", level=40, xp=8,
         tone="serious", prev="ch7_rides", kill=[("raft_guard", 10)], poi=["cove_beach"],
         goal="Kill 10 Spitelash Raft-Guards on the beach of the cove under the Bitter Reaches, where Valormok's line "
              "is, and report to Myrmidon Ssaveth there.",
         text="My grunts are on your beach already. My wind riders too, up top, where the frost-woman can't sing at them. "
              "You fish know where to stick a trident on a fish. Go and do it. Ten of the guards on the sand. Then your "
              "big one can have his raft.",
         progress="The sand's still crowded.",
         reward="Ten. Grunts on my left, our tridents on my right, and the wind riders screaming over all of it. I've "
                "fought beside worse. I've fought beside Spitelash.",
         details=["talk", "point"], reward_emotes=["roar"],
         accept=[], complete=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 1500),
                              ("emote", "line_grunt", "cheer"), ("wait", 1500), ("emote", "self", "talk")]),

    # 7.14: Isshara's cage (the same as the song, and you know how; Taelon breaks the frost at the line)
    dict(key="ch7_issharas_cage", title="Isshara's Cage", giver="ch0:ssaveth", ender="ch0:szaria", level=40, xp=8,
         tone="serious", path="hero", prev="ch7_raft_guards", poi=["tug_mid", "line_tent"],
         event="Isshara brought to Valormok's line",
         tug=dict(cart="isshara_bound", path=["tug_1", "tug_2", "tug_mid", "tug_4", "tug_end"], midpoint="tug_mid",
                  back="tug_1", enemies=[("snatcher", "sn_1"), ("snatcher", "sn_2"), ("snatcher", "sn_3")],
                  taken=[("yell", "snatcher", "Land-born scum!", None, "NagaRoyalGuardYesAttack2"),
                         ("emote", "self", "spell"), ("sound", "self", "siren_hiss"), ("wait", 2500),
                         ("emote", "fight_grunt", "roar")],
                  retaken=[("emote", "self", "spell"), ("sound", "self", "siren_hiss")], radius=40, seconds=420),
         goal="Take Isshara from the Spitelash on the cove's beach and stay beside her all the way to the tent at "
              "Valormok's line. They'll try to drag her back to the sea: don't let them.",
         text="They've got her off the raft, ice on her wrists, and they mean to put her back on it before the tide. Same "
              "as the song. You take her, they take her back, you take her again. Walk beside her. She can't see the "
              "way; she'll know your voice.",
         progress="Stay with her!",
         reward="She's here. She's here. Look at her hands. ...Elf! Elf, do your trick. Whatever it is your kind do to "
                "magic, do it to that.",
         details=["battle_roar"], reward_emotes=["talk"], choice=["keeper_gloves", "hauler_grips", "frost_gauntlets"],
         accept=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"),
                 ("say", "self", "Same as the song. Take her, lose her, take her again."), ("wait", 2500),
                 ("state", "line_grunt", "ready"), ("emote", "line_grunt", "roar"), ("face", "self", "tug_1"),
                 ("state", "self", "ready_thrown")],
         complete=[("summon", "isshara_dying", "line_isshara", 1800), ("wait", 600), ("visual", "isshara_dying", FROZEN),
                   ("move", "ch6:taelon", "taelon_lock", "walk"), ("wait", 3500), ("face", "ch6:taelon", "line_isshara"),
                   ("cast", "ch6:taelon", BLUE_BEAM, "isshara_dying"), ("wait", 3500), ("sound", "isshara_dying", ICE_CRACK),
                   ("unaura", "isshara_dying", FROZEN), ("visual", "isshara_dying", WATER), ("wait", 1500),
                   ("move", "ch0:vyssa", "vyssa_kneel", "run"), ("face", "self", "line_isshara"), ("emote", "self", "work"),
                   ("wait", 3000), ("move", "ch6:taelon", "line_taelon", "walk"), ("visual", "ch0:vyssa", WATER)]),

    # 7.15: her last song (M14: the camp in the dust, the storm, Illidan's task; "Ash'valana thure.")
    dict(key="ch7_last_song", title="Her Last Song", giver="ch0:szaria", ender="ch0:szaria", level=41, xp=8,
         tone="serious", prev="ch7_issharas_cage", memory="m14", wake=True, event="Isshara's last song heard",
         poi=["line_isshara"],
         goal="Stay by Isshara on the sand at Valormok's line while she sings her last memory to you, and stay in "
              "her song until it ends.",
         text="They emptied her. All the way down, on the raft, while we were finding the cove. She doesn't know my "
              "name. She doesn't know Vashj's. ...But she's singing. Something too deep for them to reach. She keeps "
              "turning her face to where you are. Go. Put your hand in the water by her. It's for you.",
         progress="Is she... still singing?",
         reward="What did she say to you? No. Don't tell me. That one's yours.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("despawn", "isshara_dying"), ("summon", "isshara_dying", "line_isshara", 1800), ("wait", 1500),
                 ("face", "self", "line_isshara"), ("emote", "self", "talk"), ("wait", 2500),
                 ("visual", "isshara_dying", GLOW_BLUE), ("sound", "isshara_dying", "siren_hiss"), ("wait", 3500),
                 ("visual", "player", GLOW_BLUE), ("music", MUSIC_NAGA), ("wait", 2500), ("relive", "m14"), ("wait", 1500),
                 ("unaura", "player", GLOW_BLUE), ("unaura", "isshara_dying", GLOW_BLUE)],
         complete=[("face", "isshara_dying", "player"), ("wait", 2500),
                   ("say", "isshara_dying", "Ash'valana thure.", None, "NagaSirenYes3"), ("wait", 3500),
                   ("visual", "isshara_dying", WATER), ("wait", 2000), ("face", "self", "sea_view"),
                   ("emote", "self", "stun")]),

    # 7.16: the keeper sleeps (a ring of naga and orcs; they part for you)
    dict(key="ch7_isshara", title="The Keeper Sleeps", giver="ch0:szaria", ender="ch0:szaria", level=41, xp=8,
         tone="serious", prev="ch7_last_song", poi=["line_isshara"],
         interact=[("isshara_still", "Touch her hand.")], interact_goal="The keeper's hand touched",
         interact_beats=[("sound", "ch0:vyssa", SIREN_DEATH), ("emote", "ch0:vyssa", "roar"), ("music", MUSIC_GLOOMY),
                         ("wait", 2500), ("state", "ch6:taelon", "kneel"), ("emote", "agtor_line", "bow"),
                         ("summon", "ch0:mrgl", "ring_gap", 60), ("wait", 1500), ("emote", "ch0:mrgl", "cry"),
                         ("sound", "ch0:mrgl", "murloc_wound"), ("emote", "line_grunt", "bow"), ("wait", 3000),
                         ("emote", "ch0:mrgl", "cry"), ("emote", "ch0:ssaveth", "roar"), ("wait", 6000),
                         ("state", "ch6:taelon", "none")],
         goal="Go through the ring at Valormok's line and touch Isshara's hand.",
         text="She stopped. Just now. Between one breath and the next, with her face turned to the sea. ...Nobody wants "
              "to be the one. Go on. She'd want it to be you.",
         progress="",
         reward="Ash'valana thure. Ten thousand years and those are the last words, and she won't be here to not "
                "translate them for us. ...Leave us a while.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("despawn", "isshara_dying"), ("summon", "isshara_still", "line_isshara", 1800), ("wait", 1000),
                 ("move", "ch0:vyssa", "ring_1", "walk"), ("move", "ch0:ssaveth", "ring_3", "walk"),
                 ("move", "ch6:taelon", "ring_4", "walk"), ("move", "agtor_line", "ring_5", "walk"),
                 ("move", "self", "ring_6", "walk"), ("wait", 6000), ("face", "ch0:vyssa", "line_isshara"),
                 ("face", "ch0:ssaveth", "line_isshara"), ("face", "ch6:taelon", "line_isshara"),
                 ("face", "agtor_line", "line_isshara"), ("face", "self", "player"), ("wait", 1500),
                 ("move", "agtor_line", "ring_gap", "walk"), ("emote", "self", "spell")],
         complete=[("face", "self", "sea_view"), ("wait", 3000), ("visual", "self", WATER), ("sound", "self", "pickup_water"),
                   ("emote", "self", "work"), ("wait", 2000), ("move", "agtor_line", "line_agtor", "walk"),
                   ("move", "ch0:ssaveth", "line_ssaveth", "walk")]),

    # 7.17a: three cups (the girl from Nendis on the rise: 4.19a)
    dict(key="ch7_cups_a", title="Three Cups", giver="ch0:szaria", ender="ch0:szaria", level=41, xp=8, tone="serious",
         prev=["ch7_isshara", "ch4:ch4_keeper"], poi=["shallows"],
         interact=[("isshara_body", "Pour the third cup over her: for the singer.")], interact_goal="The third cup poured",
         interact_beats=[("visual", "self", WATER), ("sound", "self", "pickup_water"), ("wait", 1500),
                         ("emote", "ch0:ssaveth", "work"), ("wait", 2000), ("state", "ch0:szaria", "channel"),
                         ("state", "ch0:vyssa", "channel"), ("sound", "ch0:vyssa", "siren_hiss"), ("music", MUSIC_SACRED),
                         ("wait", 4000), ("face", "ch0:ssaveth", "deep"), ("emote", "ch0:ssaveth", "roar"),
                         ("sound", "ch0:ssaveth", "naga_aggro"), ("wait", 2000), ("state", "ch2:shaelyn", "ready_bow"),
                         ("wait", 1500), ("emote", "ch2:shaelyn", "salute"), ("wait", 2500), ("visual", "self", SPOUT),
                         ("sound", "self", "splash_big"), ("state", "ch0:szaria", "none"), ("state", "ch0:vyssa", "none"),
                         ("despawn", "self")],
         goal="Give the keeper to the sea in the shallows below Valormok's line: pour the third cup over her.",
         text="Three cups. One for the deep, she came out of it. One for the shore, she sang to it. One for the singer, "
              "because there's always a singer after. I'll pour the first. Vyssa the second. You pour the third. ...It's "
              "dusk. It's time.",
         progress="",
         reward="The deep has her. ...Did you see the rise, over the cove? The night elf, with the bow. She didn't come "
                "down. She didn't have to.",
         details=["talk"], reward_emotes=["talk"], choice=["three_cups_shroud", "singer_band", "shore_band"],
         accept=[("despawn", "isshara_still"), ("summon", "ch2:shaelyn", "shaelyn_rise", 300),
                 ("summon", "bearer_1", "line_isshara", 40), ("summon", "bearer_2", "ring_2", 40), ("wait", 800),
                 ("move", "bearer_1", "carry_1", "walk"), ("move", "bearer_2", "carry_1", "walk"), ("wait", 7000),
                 ("move", "bearer_1", "carry_2", "walk"), ("move", "bearer_2", "carry_2", "walk"), ("wait", 6000),
                 ("summon", "isshara_body", "shallows", 600), ("despawn", "bearer_1"), ("despawn", "bearer_2"),
                 ("move", "self", "cup_1", "walk"), ("move", "ch0:vyssa", "cup_2", "walk"), ("move", "ch0:ssaveth", "cup_3", "walk"),
                 ("wait", 9000), ("face", "self", "shallows"), ("emote", "self", "work"), ("visual", "isshara_body", WATER),
                 ("say", "self", "One for the deep."), ("wait", 3500), ("face", "ch0:vyssa", "shallows"),
                 ("emote", "ch0:vyssa", "work"), ("visual", "isshara_body", WATER), ("say", "ch0:vyssa", "One for the shore."),
                 ("wait", 2500), ("face", "self", "player")],
         complete=[("move", "self", "line_szaria", "walk"), ("move", "ch0:vyssa", "line_vyssa", "walk"),
                   ("move", "ch0:ssaveth", "line_ssaveth", "walk"), ("wait", 4000), ("face", "self", "shaelyn_rise"),
                   ("emote", "self", "roar")]),

    # 7.17b: three cups (no one on the rise: 4.19b)
    dict(key="ch7_cups_b", title="Three Cups", giver="ch0:szaria", ender="ch0:szaria", level=41, xp=8, tone="serious",
         prev=["ch7_isshara", "ch4:ch4_glaive"], poi=["shallows"],
         interact=[("isshara_body", "Pour the third cup over her: for the singer.")], interact_goal="The third cup poured",
         interact_beats=[("visual", "self", WATER), ("sound", "self", "pickup_water"), ("wait", 1500),
                         ("emote", "ch0:ssaveth", "work"), ("wait", 2000), ("state", "ch0:szaria", "channel"),
                         ("state", "ch0:vyssa", "channel"), ("sound", "ch0:vyssa", "siren_hiss"), ("music", MUSIC_SACRED),
                         ("wait", 4000), ("face", "ch0:ssaveth", "deep"), ("emote", "ch0:ssaveth", "roar"),
                         ("sound", "ch0:ssaveth", "naga_aggro"), ("wait", 4000), ("visual", "self", SPOUT),
                         ("sound", "self", "splash_big"), ("state", "ch0:szaria", "none"), ("state", "ch0:vyssa", "none"),
                         ("despawn", "self")],
         goal="Give the keeper to the sea in the shallows below Valormok's line: pour the third cup over her.",
         text="Three cups. One for the deep, she came out of it. One for the shore, she sang to it. One for the singer, "
              "because there's always a singer after. I'll pour the first. Vyssa the second. You pour the third. ...It's "
              "dusk. It's time.",
         progress="",
         reward="The deep has her. ...I looked up at the rise over the cove, just once. I don't know who I thought would "
                "be there. Nobody was.",
         details=["talk"], reward_emotes=["talk"], choice=["three_cups_shroud", "singer_band", "shore_band"],
         accept=[("despawn", "isshara_still"), ("summon", "bearer_1", "line_isshara", 40), ("summon", "bearer_2", "ring_2", 40),
                 ("wait", 800), ("move", "bearer_1", "carry_1", "walk"), ("move", "bearer_2", "carry_1", "walk"),
                 ("wait", 7000), ("move", "bearer_1", "carry_2", "walk"), ("move", "bearer_2", "carry_2", "walk"),
                 ("wait", 6000), ("summon", "isshara_body", "shallows", 600), ("despawn", "bearer_1"),
                 ("despawn", "bearer_2"), ("move", "self", "cup_1", "walk"), ("move", "ch0:vyssa", "cup_2", "walk"),
                 ("move", "ch0:ssaveth", "cup_3", "walk"), ("wait", 9000), ("face", "self", "shallows"),
                 ("emote", "self", "work"), ("visual", "isshara_body", WATER), ("say", "self", "One for the deep."),
                 ("wait", 3500), ("face", "ch0:vyssa", "shallows"), ("emote", "ch0:vyssa", "work"),
                 ("visual", "isshara_body", WATER), ("say", "ch0:vyssa", "One for the shore."), ("wait", 2500),
                 ("face", "self", "player")],
         complete=[("move", "self", "line_szaria", "walk"), ("move", "ch0:vyssa", "line_vyssa", "walk"),
                   ("move", "ch0:ssaveth", "line_ssaveth", "walk"), ("wait", 4000), ("face", "self", "shaelyn_rise"),
                   ("wait", 2500), ("face", "self", "sea_view")]),

    # 7.18: nowhere by the sea (Szaria looks at the sea a long time; Ag'tor points inland)
    dict(key="ch7_nowhere", title="Nowhere by the Sea", giver="ch0:szaria", ender="ch0:szaria", level=41, xp=8,
         tone="serious", prev_any=["ch7_cups_a", "ch7_cups_b"], explore="ridge_foot", radius=14, poi=["ridge_foot"],
         goal="Go inland to the foot of Forlorn Ridge, south-east of Valormok, where the Tide-Broken are gathering with "
              "everything they could carry, and find Lady Szaria there.",
         text="She knew where the Hollow was. She'll know where the next cove is, and the one after. Every beach in "
              "Azshara is the Empress's water, sooner or later. ...The orc says there's a mountain nobody climbs, with a "
              "hole in the top of it. Dry as bone. Go on ahead. I'll bring them.",
         progress="",
         reward="Everything we own, in baskets. It looked like more on the sand. ...Look at it. Up there. It's ugly and "
                "dry and there's no sea for a thousand yards. Nobody sings at you from a mountain.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "sea_view"), ("state", "self", "none"), ("wait", 9000),
                 ("move", "agtor_line", "agtor_beside", "walk"), ("wait", 4000), ("face", "agtor_line", "inland"),
                 ("emote", "agtor_line", "point"), ("say", "agtor_line", "No one goes up there."), ("wait", 4000),
                 ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500),
                 ("move", "agtor_line", "line_agtor", "walk")],
         complete=[("face", "self", "rim_n"), ("emote", "self", "spell"), ("wait", 2000), ("emote", "foot_bearer", "question"),
                   ("face", "self", "player"), ("emote", "self", "talk")]),

    # 7.19: up the ridge (the column; a jar smashes; the rim; the camp goes up in the bowl)
    dict(key="ch7_crater", title="Up the Ridge", giver="ch0:szaria", ender="ch0:szaria", level=41, xp=8,
         tone="serious", prev="ch7_nowhere", poi=["rim_n", "crater_floor"],
         escort=("ch0:szaria", ["up_1", "up_2", "up_3", "up_4", "rim_n", "down_1", "crater_floor"]), radius=14,
         choice=["ridge_sandals", "ridge_boots", "ridge_greaves"],
         goal="Lead Lady Szaria and the Tide-Broken column up the north path of Forlorn Ridge, over the north rim and "
              "down into the dry crater at the top.",
         text="Lead. You've walked it in a song, I haven't. Slowly; the old ones are carrying the jars, and Mrgl is "
              "carrying the count, and he'll tell us every time it changes. If anyone falls, we stop. If anyone drops "
              "anything, we stop. Nobody gets left on a mountain.",
         progress="",
         reward="Here. We stop here. ...Empty the jars into that hollow in the stone, all of them. It isn't much. It's a "
                "puddle. It's ours.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("summon", "col_bearer_1", "col_1", 600), ("summon", "col_bearer_2", "col_2", 600),
                 ("summon", "col_siren", "col_3", 600), ("summon", "col_vyssa", "col_4", 600),
                 ("summon", "col_ssaveth", "col_5", 600), ("summon", "col_mrgl", "col_1", 600), ("wait", 800),
                 ("follow", "col_bearer_1"), ("follow", "col_bearer_2"), ("follow", "col_siren"), ("follow", "col_vyssa"),
                 ("follow", "col_ssaveth"), ("follow", "col_mrgl"), ("say", "self", "Up. All of you. Up."),
                 ("wait", 30000),
                 # a jar smashes on the path, and everyone stops
                 ("emote", "col_bearer_2", "stun"), ("visual", "col_bearer_2", WATER), ("sound", "col_bearer_2", GLASS),
                 ("wait", 1200), ("emote", "col_bearer_2", "cry"), ("emote", "col_mrgl", "question"),
                 ("sound", "col_mrgl", "murloc_fidget"), ("emote", "col_ssaveth", "roar"), ("wait", 3000),
                 ("emote", "col_vyssa", "talk"),
                 ("emote", "col_bearer_1", "point"), ("wait", 2500), ("emote", "col_bearer_2", "shy"), ("wait", 2000),
                 ("emote", "col_mrgl", "point"), ("emote", "col_mrgl", "cry")],
         complete=[("emote", "self", "talk"), ("emote", "self", "roar"), ("despawn", "col_bearer_1"), ("despawn", "col_bearer_2"),
                   ("despawn", "col_siren"), ("despawn", "col_vyssa"), ("despawn", "col_ssaveth"), ("despawn", "col_mrgl"),
                   ("wait", 1500), ("evade", "self")]),

    # 7.20a: water is life (boring: the jars up from Lake Mennar, one splash at a time; the voice from the water)
    dict(key="ch7_water", title="Water Is Life", giver="ch0:vyssa", ender="ch0:vyssa", level=42, xp=8, tone="boring",
         exclusive=1, prev="ch7_crater", poi=["lake", "c_pool"], rewards=["crater_water"],
         use=[("lake_jar", "c_pool_use", 8,
               [("visual", "crater_pool", SPOUT), ("sound", "crater_pool", "splash"), ("emote", "camp_renegade", "cheer")])],
         goal="Fill the jars from the shore of Lake Mennar, south-east of the crater, carry them up, and empty 8 Heavy "
              "Jars of Lake Water into the crater's pool.",
         text="A puddle. Thirty naga and a puddle. The lake's down there, look, south and east, shining at us like it "
              "thinks it's funny. Jars on the shore where the old road comes down. Fill them and carry them up. It's "
              "heavy. It's boring. It's water.",
         progress="Every jar. Every splash. I'm counting.",
         reward="Look at it. Look at them, standing round it like it's a feast day. ...Hush. Hush! Did you hear that? "
                "From the water. Did you hear it?",
         details=["talk", "point"], reward_emotes=["cheer"],
         accept=[("state", "self", "none"), ("face", "self", "lake"), ("emote", "self", "spell"), ("wait", 2000),
                 ("face", "self", "c_pool"), ("emote", "self", "work"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk")],
         complete=[("visual", "crater_pool", SPOUT), ("emote", "camp_renegade", "cheer"), ("emote", "ch0:mrgl_banker", "dance"),
                   ("wait", 4000), ("emote", "self", "stun"), ("wait", 1500), ("visual", "crater_voice", HOLY_NOVA),
                   ("whisper", "crater_voice", "Water... is life."), ("wait", 3500), ("face", "self", "player"),
                   ("emote", "self", "talk")]),

    # 7.20b: Valormok's barrels (menace, funny): Kurll argues with a grunt; the pool fills in no time
    dict(key="ch7_barrels", title="Valormok's Barrels", giver="ch0:vyssa", ender="ch0:vyssa", level=42, xp=8,
         tone="funny", path="menace", exclusive=1, prev="ch7_crater", rep=[(76, -350)], objects=[("water_barrel", 4)],
         poi=["barrel_1"],
         goal="Roll 4 of Valormok's Water Barrels away from Kurll's stores at Valormok while nobody's watching, for the "
              "crater's pool.",
         text="Or. Or! The orcs have barrels. Big ones, behind the cook, full, and the cook spends all day arguing with "
              "grunts about stew. Four barrels and the pool's full by supper. They'd give them to us if we asked. "
              "...Probably. Don't ask.",
         progress="Barrels! Rolling! Quietly!",
         reward="Four barrels, one splash, done. Look at it, full to the stones! ...What? Nobody saw. Nobody saw. The "
                "orcs are always shouting about something.",
         details=["laugh"], reward_emotes=["cheer"],
         accept=[("state", "self", "none"), ("face", "self", "thirsty_rim"), ("emote", "self", "spell"), ("wait", 1500),
                 ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "work")],
         complete=[("visual", "crater_pool", SPOUT), ("sound", "crater_pool", "splash_big"), ("emote", "camp_renegade", "cheer"),
                   ("wait", 3000), ("summon", "thirsty_grunt", "thirsty_in", 30), ("wait", 1000),
                   ("face", "thirsty_grunt", "c_pool"), ("emote", "thirsty_grunt", "rude"), ("wait", 2500),
                   ("say", "thirsty_grunt", "Our water. That's OUR water. Chief's going to hear about this."),
                   ("emote", "thirsty_grunt", "no"), ("wait", 3000), ("move", "thirsty_grunt", "c_north_path", "walk"),
                   ("face", "self", "thirsty_rim"), ("emote", "self", "stun")]),

    # 7.21: dry scales (funny): mud from the lake; Ssaveth stands like a statue; Taelon laughs out loud
    dict(key="ch7_dry_scales", title="Dry Scales", giver="ch0:vyssa", ender="ch0:vyssa", level=42, xp=8, tone="funny",
         prev_any=["ch7_water", "ch7_barrels"], items=[("mud", 8)], poi=["lake"],
         goal="Bring Vyssa 8 Lumps of Lake Mennar Mud from the lake shore below the crater, for a salve.",
         text="Look at my arms. Flaking. Ssaveth's tail looks like a dropped plate. We were made to be wet and we're on "
              "a mountain in the sun. Mud. Lake mud, cold and grey, eight good lumps. I'll make a salve. It won't smell "
              "nice. Nothing up here smells nice.",
         progress="Is that mud or are you just dusty?",
         reward="Perfect. Disgusting. Perfect. Ssaveth! Stand still. Stand STILL. ...There. Look at him. And now you. "
                "And now everyone. By tonight this whole camp's going to be the colour of a rock.",
         details=["talk"], reward_emotes=["laugh"],
         accept=[("state", "self", "none"), ("emote", "self", "work"), ("visual", "self", DUST), ("wait", 1500),
                 ("face", "self", "c_ssaveth"), ("emote", "self", "spell"), ("wait", 1500), ("emote", "ch0:ssaveth", "roar"),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("move", "self", "c_vyssa_mud", "walk"), ("wait", 4000), ("face", "self", "c_ssaveth"),
                   ("emote", "self", "work"), ("visual", "ch0:ssaveth", DUST), ("visual", "ch0:ssaveth", FREEZE_ANIM),
                   ("wait", 3500), ("emote", "self", "work"), ("visual", "ch0:ssaveth", DUST), ("wait", 2500),
                   ("emote", "ch6:taelon", "laugh"), ("sound", "ch6:taelon", ELF_LAUGH), ("wait", 2000),
                   ("emote", "camp_renegade", "laugh"), ("aura", "player", "mud_grey"), ("visual", "player", DUST),
                   ("wait", 6000), ("unaura", "ch0:ssaveth", FREEZE_ANIM), ("emote", "ch0:ssaveth", "roar"),
                   ("move", "self", "c_vyssa", "walk")]),

    # 7.22: the crater's rim (Spitelash scouts followed the column; sentries at four points)
    dict(key="ch7_rim", title="The Crater's Rim", giver="ch0:ssaveth", ender="ch0:ssaveth", level=42, xp=8,
         tone="serious", prev="ch7_dry_scales", kill=[("ridge_scout", 10)], poi=["up_2"],
         choice=["rim_sash", "rim_belt", "rim_girdle"],
         goal="Kill 10 Spitelash Scouts on the north path up Forlorn Ridge.",
         text="Tracks on the path. Spitelash tracks, naga tracks, coming up behind the column the whole way. Scouts. If "
              "even one of them swims home, she knows where we sleep. I've put a sentry on the rim north, east, south and "
              "west. Four points. You take the path.",
         progress="How many on the path?",
         reward="Ten. None swam home. ...The sentries call down every hour now. North, east, south, west, all quiet. I "
                "don't know why four. Four felt right.",
         details=["talk", "battle_roar"], reward_emotes=["roar"],
         accept=[("state", "self", "none"), ("face", "self", "rim_n"), ("emote", "self", "spell"), ("wait", 1500),
                 ("face", "self", "rim_e"), ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "rim_s"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "rim_w"), ("emote", "self", "spell"),
                 ("summon", "ridge_scout", "sc_1", 900), ("summon", "ridge_scout", "sc_2", 900),
                 ("summon", "ridge_scout", "sc_3", 900), ("summon", "ridge_scout", "sc_4", 900),
                 ("summon", "ridge_scout", "sc_5", 900), ("summon", "ridge_scout", "sc_6", 900),
                 ("summon", "ridge_scout", "sc_7", 900), ("summon", "ridge_scout", "sc_8", 900),
                 ("summon", "ridge_scout", "sc_9", 900), ("summon", "ridge_scout", "sc_10", 900),
                 ("summon", "ridge_scout", "sc_11", 900), ("summon", "ridge_scout", "sc_12", 900),
                 ("summon", "ridge_scout", "sc_13", 900), ("summon", "ridge_scout", "sc_14", 900), ("wait", 1500),
                 ("face", "self", "player"), ("state", "self", "ready_thrown")],
         complete=[("state", "self", "none"), ("emote", "self", "roar"), ("sound", "self", "naga_aggro"), ("wait", 2000),
                   ("face", "self", "rim_n"), ("wait", 1500), ("face", "self", "player"), ("state", "self", "ready_thrown")]),

    # 7.23: Valormok's kin (hero): two lines before the chief; "Our alliance binds me."
    dict(key="ch7_kin", title="Valormok's Kin", giver="ch0:szaria", ender=AGTOR, level=42, xp=8, tone="serious",
         path="hero", prev="ch7_rim", rep=[(76, 500), (530, 250)], poi=["ruzga"],
         choice=["valormok_axe", "valormok_bow", "valormok_rod"],
         interact=[("ruzga", "Ask the warcaller to sound the horn: the Tide-Broken stand before the chief.")],
         interact_goal="The Tide-Broken stood before Ag'tor",
         interact_beats=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1000), ("sound", "self", HORN),
                         ("summon", "kin_grunt_1", "kin_g1", 50), ("summon", "kin_grunt_2", "kin_g2", 50),
                         ("summon", "kin_grunt_3", "kin_g3", 50), ("summon", "kin_naga_1", "kin_n1", 50),
                         ("summon", "kin_naga_2", "kin_n2", 50), ("summon", "kin_naga_3", "kin_n3", 50),
                         ("summon", "ch0:szaria", "kin_szaria", 50), ("summon", "ch0:ssaveth", "kin_ssaveth", 50),
                         ("wait", 1000), ("face", "kin_grunt_1", "agtor"), ("face", "kin_grunt_2", "agtor"),
                         ("face", "kin_grunt_3", "agtor"), ("face", "kin_naga_1", "agtor"), ("face", "kin_naga_2", "agtor"),
                         ("face", "kin_naga_3", "agtor"), ("face", "ch0:szaria", "agtor"), ("face", "ch0:ssaveth", "agtor"),
                         ("emote", "kin_grunt_1", "salute"), ("emote", "kin_grunt_2", "salute"), ("wait", 2500),
                         ("say", "ch0:szaria", "Chief. We are the Tide-Broken. We came out of the sea with nothing and "
                                               "you gave us a tent, and grunts on our beach, and a mountain. We have no "
                                               "Empress and no master. We ask the Horde for what it gives its own: a "
                                               "place, and a shield.", "talk"), ("wait", 9000),
                         ("say", "ch0:ssaveth", "Our alliance binds me.", "roar", "NagaMyrmadonYes3"), ("wait", 2500),
                         ("emote", "kin_naga_1", "salute"), ("emote", "kin_naga_2", "bow"), ("emote", "kin_naga_3", "salute"),
                         ("wait", 1500), ("emote", "kin_grunt_1", "roar"), ("emote", "kin_grunt_3", "cheer"),
                         ("sound", "kin_grunt_1", ORC_ROAR), ("emote", "self", "cheer")],
         goal="Go to Valormok and have Warcaller Ruzga sound the horn while the Tide-Broken stand before Ag'tor Bloodfist. "
              "Then speak to Ag'tor.",
         text="Ag'tor fought for us on a beach that wasn't his. He'll do it again, I think, but I won't have it be a "
              "favour. Favours get called in. We go to Valormok, all of us who can be spared, and we ask properly, in "
              "front of his warriors. The way they do. Come and stand with us.",
         progress="",
         reward="Long speech, for a fish. Good speech. ...Here. My hand. You take it and it means you stand with the "
                "Horde and the Horde stands with you. Valormok's fires are your fires. Don't drink all our water.",
         details=["talk"], reward_emotes=["talk", "salute"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "rim_n"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player")],
         complete=[]),

    # 7.24: the tide recedes (from the east rim, Azshara as it is: the live world's phase from its reward)
    dict(key="ch7_live_world", title="The Tide Recedes", giver="ch0:szaria", ender="ch0:szaria", level=42, xp=8,
         tone="serious", prev="ch7_kin", explore="c_rim_look", radius=10, poi=["c_rim_look"],
         goal="Climb to the crater's east rim with Lady Szaria and look out over Azshara.",
         text="Walk up to the rim with me. The east side, over the lake. I keep looking at the sea, and the sea keeps "
              "looking back. I want to look the other way for once.",
         progress="",
         reward="...They were always there. We weren't looking.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "c_szaria_rim"), ("emote", "self", "talk"), ("wait", 1500),
                 ("move", "self", "c_szaria_rim", "walk")],
         complete=[("face", "self", "c_rim_look"), ("music", MUSIC_SACRED), ("wait", 5000), ("emote", "self", "talk"),
                   ("wait", 4000), ("face", "self", "player"), ("emote", "self", "omnicast"), ("wait", 6000),
                   ("evade", "self")]),

    # 7.25: Serena's price (a herald's shell at the foot of the ridge; Szaria crushes it)
    dict(key="ch7_price", title="Serena's Price", giver="ch0:ssaveth", ender="ch0:szaria", level=43, xp=8,
         tone="serious", prev="ch7_live_world", items=[("herald_shell", 1)], poi=["shell_spot"],
         goal="Fetch the herald's shell left at the foot of Forlorn Ridge's north path, and take it to Lady Szaria.",
         text="The north sentry saw a siren at the foot of the path at dawn. Open shell held up high, the old way, the "
              "parley way. She left it on a stone and went. Nobody's touched it. Bring it to Szaria. Don't open it. "
              "Don't listen to it.",
         progress="She wrote to us? She wrote?",
         reward="\"Your memories for your lives.\" Ten thousand years of memory, for a tail and a mountain. ...She'd "
                "keep the bargain, too. That's the worst of it.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "rim_n"), ("emote", "self", "spell"), ("wait", 2000),
                 ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "player"), ("state", "self", "ready_thrown")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 3500), ("emote", "self", "work"),
                   ("sound", "self", GLASS), ("visual", "self", DUST), ("wait", 2000), ("emote", "self", "roar"),
                   ("emote", "ch0:ssaveth", "battle_roar")]),

    # 7.26a: Ssethis at the ridge (5.23a: he comes up alone with a warning and leaves without waiting for thanks)
    dict(key="ch7_ssethis_a", title="Ssethis at the Ridge", giver="ch0:szaria", ender="ch0:szaria", level=43, xp=8,
         tone="serious", prev=["ch7_price", "ch5:ch5_ssethis_a"], event="Ssethis's warning heard", poi=["c_ssethis"],
         goal="Stay by Lady Szaria in the crater while someone comes down from the north rim.",
         text="Someone's coming up the path. Alone, the north sentry says, and slow, and carrying a trident like he's "
              "forgotten he's holding it. Stay by me. Whoever comes up a mountain alone has something to say.",
         progress="",
         reward="The new moon. She's going to sing every naga in Azshara empty at once, at the new moon. ...And the "
                "boy came all the way up here to tell us, and didn't stay to be thanked. Your crèche-mate. Huh.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "c_north_in"), ("summon", "ssethis_free", "c_ssethis_in", 70), ("wait", 1000),
                 ("move", "ssethis_free", "c_ssethis", "walk"), ("wait", 14000),
                 ("face", "ssethis_free", "player"), ("emote", "ssethis_free", "talk"), ("wait", 1500),
                 ("say", "ssethis_free", "Don't. Don't say anything. I'm not staying."), ("wait", 3500),
                 ("face", "ssethis_free", "c_szaria"),
                 ("say", "ssethis_free", "The envoy's sirens. All three choirs, the beach, the ruins, the broken statue, "
                                         "singing into one pearl at the temple. At the new moon. Every naga in Azshara "
                                         "who hears it forgets Vashj. Forgets everything but the Empress."), ("wait", 9000),
                 ("say", "ssethis_free", "Yours too. All of you. That's all."), ("wait", 2500),
                 ("emote", "ssethis_free", "roar"), ("credit", "ch7_ssethis_a"), ("wait", 1500),
                 ("move", "ssethis_free", "c_north_in", "walk"), ("wait", 12000), ("despawn", "ssethis_free")],
         complete=[("face", "self", "c_north_in"), ("wait", 2500), ("emote", "self", "talk"), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "roar")]),

    # 7.26b: Ssethis at the ridge (5.23b: blank, lost; Serena's voice out of him, as a threat)
    dict(key="ch7_ssethis_b", title="Ssethis at the Ridge", giver="ch0:szaria", ender="ch0:szaria", level=43, xp=8,
         tone="serious", prev=["ch7_price", "ch5:ch5_ssethis_b"], event="Serena's threat heard", poi=["c_ssethis"],
         goal="Stay by Lady Szaria in the crater while someone comes down from the north rim.",
         text="Someone's coming up the path. Alone, the north sentry says, and slow, and carrying a trident like he's "
              "forgotten he's holding it. Stay by me. Whoever comes up a mountain alone has something to say.",
         progress="",
         reward="That was her. Out of his mouth, in her voice. ...The new moon. Every naga in Azshara, at once. And she "
                "sent it to us in a boy you left empty, so we'd know exactly what empty looks like.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "c_north_in"), ("summon", "ssethis_blank", "c_ssethis_in", 80), ("wait", 1000),
                 ("move", "ssethis_blank", "c_ssethis", "walk"), ("wait", 20000),
                 ("face", "ssethis_blank", "c_pool"), ("wait", 3000), ("face", "ssethis_blank", "player"),
                 ("emote", "ssethis_blank", "stun"), ("visual", "ssethis_blank", FROST_HAND), ("wait", 2000),
                 ("say", "ssethis_blank", "Little tide-runner. Little keeper. Did you think a mountain was far enough from "
                                          "the sea?"), ("wait", 5000),
                 ("say", "ssethis_blank", "At the new moon my choirs sing into the Empress's Pearl, and every naga in "
                                          "Azshara who hears it will remember only her. You will hear it. Everyone "
                                          "hears it. The tide always turns back."), ("wait", 9000),
                 ("visual", "ssethis_blank", FROST_HAND), ("emote", "ssethis_blank", "stun"), ("credit", "ch7_ssethis_b"),
                 ("wait", 2500), ("face", "ssethis_blank", "c_pool"), ("move", "ssethis_blank", "c_north_in", "walk"),
                 ("wait", 14000), ("despawn", "ssethis_blank")],
         complete=[("face", "self", "c_north_in"), ("wait", 3000), ("emote", "self", "stun"), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "talk")]),

    # the chapter's last (not one of the bible's numbered quests: one end for both of 7.26's roads): the new moon
    dict(key="ch7_end", title="The New Moon", giver="ch0:szaria", ender="ch0:ssaveth", level=43, xp=8, tone="serious",
         prev_any=["ch7_ssethis_a", "ch7_ssethis_b"], poi=["c_ssaveth"],
         choice=["crater_leggings", "crater_breeches", "crater_legguards"],
         goal="Tell Myrmidon Ssaveth to count the nights to the new moon.",
         text="Look up. The moon's a fingernail tonight. In a few nights there won't be one at all. ...Tell Ssaveth. "
              "Tell him to count the nights, out loud, every night, so nobody can say they didn't know. And then tell "
              "him we're going down off this mountain. All of us. Into Azshara as it is.",
         progress="",
         reward="Count them. ...I'll count them. Here.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "c_moon"), ("wait", 3000), ("emote", "self", "omnicast"), ("visual", "self", HOLY_NOVA),
                 ("wait", 2500), ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500),
                 ("face", "self", "c_ssaveth")],
         complete=[("state", "self", "none"), ("move", "self", "line_sand", "walk"), ("wait", 3000),
                   ("emote", "self", "work"), ("object", "sand_line", "line_sand", 600), ("sound", "self", 977),
                   ("wait", 2000), ("emote", "self", "attack2h"), ("sound", "self", 977), ("wait", 1500),
                   ("face", "self", "c_moon"), ("emote", "self", "roar"), ("sound", "self", "naga_aggro"), ("wait", 3000),
                   ("move", "self", "c_ssaveth", "walk"), ("state", "self", "ready_thrown")]),
]

# -- more of someone already made ------------------------------------------------------------------------------------------
SPAWNS = [
    # the Hollow overturned: the Tide-Broken (Szaria is chapter 1's, there always) and the hub kit at its posts
    dict(npc="ch0:ssaveth", at="o_ssaveth", facing=3.2, phase=OVERTURNED),
    dict(npc="ch0:vyssa", at="ch4:pool_side", facing=5.3, phase=OVERTURNED),
    dict(npc="ch0:kessh", at="ch2:kessh", facing=3.4, phase=OVERTURNED),
    dict(npc="ch0:thessk", at="ch2:thessk", facing=0.8, phase=OVERTURNED),
    dict(npc="ch0:thessk_turtle", at="ch2:snap", facing=0.8, phase=OVERTURNED),
    dict(npc="ch0:shivra", at="ch2:shivra", facing=0.5, phase=OVERTURNED),
    dict(npc="ch0:oshra", at="ch2:oshra", facing=3.2, phase=OVERTURNED),
    dict(npc="ch0:lyrenne", at="ch2:lyrenne", facing=0.3, phase=OVERTURNED),
    dict(npc="ch0:nazreth", at="ch2:nazreth", facing=0.6, phase=OVERTURNED),
    dict(npc="ch0:hookfin", at="ch2:hookfin", facing=3.3, phase=OVERTURNED),
    dict(npc="ch0:ysh", at="ch2:ysh", facing=0.2, phase=OVERTURNED),
    dict(npc="ch0:varra", at="ch2:varra", facing=0.2, phase=OVERTURNED),
    dict(npc="ch0:oleth", at="ch2:oleth", facing=0.2, phase=OVERTURNED),
    dict(npc="ch0:sheshk", at="ch2:sheshk", facing=0.6, phase=OVERTURNED),
    dict(npc="ch0:grosh", at="ch2:grosh", facing=4.7, phase=OVERTURNED),
    dict(npc="ch0:rhazz", at="ch2:rhazz", facing=4.7, phase=OVERTURNED),
    dict(npc="ch0:hissra", at="ch2:hissra", facing=0.8, phase=OVERTURNED),
    dict(npc="ch0:lysse", at="ch2:lysse", facing=1.0, phase=OVERTURNED),
    dict(npc="ch0:sszix", at="ch2:sszix", facing=1.2, phase=OVERTURNED),
    dict(npc="ch0:avessa", at="ch2:avessa", facing=1.4, phase=OVERTURNED),
    dict(npc="ch0:nyss", at="ch2:nyss", facing=1.8, phase=OVERTURNED),
    dict(npc="ch0:thalassa", at="ch2:thalassa", facing=1.2, phase=OVERTURNED),
    dict(npc="ch0:ishra", at="ch2:ishra", facing=3.6, phase=OVERTURNED),
    dict(npc="ch0:tessh", at="ch2:tessh", facing=3.6, phase=OVERTURNED),
    dict(npc="ch0:mrgl_banker", at="ch4:mrgl_count", facing=4.0, phase=OVERTURNED),
    dict(npc="ch0:tidecaller", at="ch2:tidecaller", facing=0.0, phase=OVERTURNED),
    dict(npc="ch0:drowned_singer", at="ch2:singer", facing=0.5, phase=OVERTURNED),
    dict(object="ch0:mail_jar", at="ch2:mailbox", facing=1.0, phase=OVERTURNED),
    dict(object="ch0:giant_clam", at="ch2:clam", facing=2.0, phase=OVERTURNED),

    # Valormok's line on the beach south of the cove, and the foot of Forlorn Ridge (LINE)
    dict(npc="ch0:szaria", at="line_szaria", facing=5.6, phase=LINE),
    dict(npc="ch0:ssaveth", at="line_ssaveth", facing=1.2, phase=LINE),
    dict(npc="ch0:vyssa", at="line_vyssa", facing=0.6, phase=LINE),
    dict(npc="ch6:taelon", at="line_taelon", facing=3.6, phase=LINE),
    dict(npc="ch0:szaria", at="foot_szaria", facing=3.9, phase=LINE),

    # the crater camp (CRATER): the Tide-Broken, Taelon, the hub kit (bible 18.9), the bank's clam, the mail jar
    dict(npc="ch0:szaria", at="c_szaria", facing=0.4, phase=CRATER),
    dict(npc="ch0:ssaveth", at="c_ssaveth", facing=0.6, phase=CRATER),
    dict(npc="ch0:vyssa", at="c_vyssa", facing=2.6, phase=CRATER),
    dict(npc="ch6:taelon", at="c_taelon", facing=0.0, phase=CRATER),
    dict(npc="ch0:mrgl_banker", at="c_mrgl", facing=5.0, phase=CRATER),
    dict(npc="ch0:kessh", at="c_kessh", facing=0.2, phase=CRATER),
    dict(npc="ch0:thessk", at="c_thessk", facing=0.4, phase=CRATER),
    dict(npc="ch0:thessk_turtle", at="c_snap", facing=0.4, wander=2.0, phase=CRATER),
    dict(npc="ch0:shivra", at="c_shivra", facing=0.8, phase=CRATER),
    dict(npc="ch0:thessa_trainer", at="c_thessa", facing=4.2, phase=CRATER),
    dict(npc="ch0:oshra", at="c_oshra", facing=3.8, phase=CRATER),
    dict(npc="ch0:lyrenne", at="c_lyrenne", facing=1.6, phase=CRATER),
    dict(npc="ch0:nazreth", at="c_nazreth", facing=1.8, phase=CRATER),
    dict(npc="ch0:hookfin", at="c_hookfin", facing=3.2, phase=CRATER),
    dict(npc="ch0:ysh", at="c_ysh", facing=3.0, phase=CRATER),
    dict(npc="ch0:varra", at="c_varra", facing=2.8, phase=CRATER),
    dict(npc="ch0:oleth", at="c_oleth", facing=2.6, phase=CRATER),
    dict(npc="ch0:sheshk", at="c_sheshk", facing=2.2, phase=CRATER),
    dict(npc="ch0:hissra", at="c_hissra", facing=1.9, phase=CRATER),
    dict(npc="ch0:grosh", at="c_grosh", facing=5.6, phase=CRATER),
    dict(npc="ch0:rhazz", at="c_rhazz", facing=5.4, phase=CRATER),
    dict(npc="ch0:lysse", at="c_lysse", facing=1.4, phase=CRATER),
    dict(npc="ch0:sszix", at="c_sszix", facing=0.9, phase=CRATER),
    dict(npc="ch0:avessa", at="c_avessa", facing=5.2, phase=CRATER),
    dict(npc="ch0:nyss", at="c_nyss", facing=4.9, phase=CRATER),
    dict(npc="ch0:thalassa", at="c_thalassa", facing=0.0, phase=CRATER),
    dict(npc="ch0:ishra", at="c_ishra", facing=3.4, phase=CRATER),
    dict(npc="ch0:tessh", at="c_tessh", facing=3.3, phase=CRATER),
    dict(npc="ch0:tidecaller", at="c_tidecaller", facing=0.4, phase=CRATER),
    dict(npc="ch0:drowned_singer", at="c_singer", facing=0.5, phase=CRATER),
    dict(object="ch0:mail_jar", at="c_mailbox", facing=1.0, phase=CRATER),
    dict(object="ch0:giant_clam", at="c_clam", facing=5.0, phase=CRATER),

    # memory m13: young Isshara in the prince's camp; memory m14: the prince, the witch and their people by the fire
    dict(npc="ch0:isshara_young", at="m13_isshara", facing=0.5, phase=M13),
    dict(npc="kael_m13", at="m14_kael", facing=0.6, phase=M14),
    dict(npc="vashj_m13", at="m14_vashj", facing=3.8, phase=M14),
    dict(npc="host_naga", at=["m14_naga_1", "m14_naga_2"], facing=0.8, phase=M14),
    dict(npc="kael_elf", at="m14_elf_1", facing=0.9, phase=M14),
]

GRAVEYARDS = [
    dict(at="ch2:graveyard", name="the Hollow", phase=OVERTURNED, facing=0.6),
    dict(at="c_graveyard", name="the crater", phase=CRATER, facing=0.4),
]
