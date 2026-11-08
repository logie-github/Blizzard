# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 3 of the murlocs' story: Saltscar (levels 19 to 24), the bible's section 9.

The Zoram Strand again, in the world's phase now (the game's Wrathtail are real enemies). Three camps:
- the Drowned Pier, where chapter 2 ends, on Darkshore's side of the Strand's north tip (4298, 1146): the
  Greymist war band, Mother Mrrgula, Mrrk, Blrrgl and Sloshy, a graveyard; a drowned elven dock in the shallows;
- the pens as the naga still keep them (chapter 1's layout, chapter 1's people and things): the slaves'
  yard behind a coral stockade along its north and east sides, where the tribe's trainers and Murlorga
  serve through the bars of the north wall (x 4122, y 1100-1136), the Elder among them;
- from the uprising (3.21) the freed, burned pens: the Saltscar camp, "hub", in the yard (4106, 1112),
  the whole hub kit in two rings, 40 yards and more from every hostile spawn of the game's.

The phases (story bits: 9 in Ashenvale, 4 at the pier in Darkshore): the pier's people and the world's places from chapter 2's
end; the kept pens until the uprising; the camp from it; the clutch, Sloshy and Glimmrl until 3.19; the
Elder (one spawn, at the bars, then in the camp) until chapter 9's death; Kezzith, Ssarnath and the
standing statue between the uprising and 3.23; the tithe's people while 3.12 is in the log; Grandmother
Shellback from 3.27; the Blindlight deserter from 3.13. A scene's people share its owner's phase, so the
set pieces with the Elder (3.19, 3.20, 3.21, 3.24a, 3.25) bring their own (summoned) people.
Plain data: tools/murloc/SCHEMA.md."""

PRE = ("from", "ch2:ch2_end")                       # the pier, the towns' friends, the world's places
PENS = ("between", "ch2:ch2_end", "ch3_uprising")    # the pens as the naga keep them (and Blrrgl at the pier)
CAMP = ("from", "ch3_uprising")                      # the Saltscar camp in the burned pens
CLUTCH = ("between", "ch2:ch2_end", "ch3_smile")     # the eggs, Sloshy, Glimmrl
ELDER = ("between", "ch2:ch2_end", "ch9:ch9_elder")  # the Elder: at the bars, then in the camp
FIGHT = ("between", "ch3_uprising", "ch3_tidebinder")  # Kezzith, Ssarnath, the standing statue
TITHE = ("during", "ch3_tithe")
CONCH = ("from", "ch3_conch")
DESERTER = ("from", "ch3_cages")

CHAPTER = dict(key="ch3", title="Saltscar", levels=(19, 24), map=1, zones=[331], hub="hub")

TOWNS = ["Zoram'gar Outpost", "Maestra's Post"]

PLACES = {
    # the Drowned Pier (chapter 2's end, on Darkshore's side of the Strand's north tip: its beach and its ruins)
    "pier": (4298.0, 1146.0), "pier_sand": (4295.0, 1149.5), "pier_sand_2": (4296.5, 1151.0), "pier_sand_a": (4294.0, 1148.5),
    "pier_sand_b": (4296.0, 1148.5), "pier_sand_c": (4298.0, 1148.5), "pier_sand_k": (4296.0, 1151.5),
    "warleader": (4293.0, 1151.0), "warleader_side": (4291.0, 1148.0), "mrrgula": (4302.0, 1139.0), "mrrk": (4290.0, 1141.0),
    "blrrgl_pier": (4301.0, 1151.0), "blrrgl_log": (4304.5, 1148.5), "sloshy_pier": (4296.0, 1137.0),
    "glimmrl_pier": (4284.0, 1150.0), "deserter": (4309.0, 1160.0), "deserter_sway": (4313.0, 1168.0), "crab_spot": (4311.5, 1162.5),
    "fighter_1": (4292.0, 1145.0), "fighter_2": (4296.0, 1153.0), "fighter_3": (4303.0, 1146.0), "fighter_4": (4298.0, 1139.5),
    "fighter_5": (4288.0, 1146.0), "fighter_6": (4300.0, 1156.0), "weeper": (4287.0, 1155.0), "giggler": (4305.0, 1157.0),
    "cruncher": (4306.0, 1142.0), "pier_grave": (4291.0, 1132.0), "pier_hut_1": (4287.0, 1136.0), "pier_hut_2": (4307.0, 1134.0),
    "pier_spears": (4293.0, 1157.0), "dock": (4308.0, 1176.0, -1.5), "column_1": (4326.0, 1172.0), "column_2": (4300.0, 1180.0),
    "column_3": (4330.0, 1158.0), "anchor": (4314.0, 1152.0), "island": (4150.0, 1270.0), "silk_camp": (3640.0, 1100.0),
    "maestra_road": (3222.0, 214.0), "murkdeep_dunes": (4152.0, 1038.0), "razortail_camp": (3622.0, 1107.0),
    "crawler_beach": (3852.0, 1095.0),
    # the cliff above the pens
    "look_1": (4215.0, 1045.0), "look_2": (4205.0, 1075.0), "look_3": (4178.0, 1112.0),
    # the pens' north wall and its bars (the trainers inside, the player outside)
    "bars_1": (4120.0, 1100.0), "bars_2": (4120.0, 1104.0), "bars_3": (4120.0, 1108.0), "bars_4": (4120.0, 1112.0),
    "bars_5": (4120.0, 1116.0), "elder": (4120.0, 1120.0), "bars_6": (4120.0, 1124.0), "bars_7": (4120.0, 1128.0),
    "bars_8": (4120.0, 1132.0), "bars_9": (4120.0, 1136.0), "pens_pot": (4116.0, 1133.0), "outside_bars": (4126.0, 1118.0),
    "bars_bowl": (4124.5, 1132.0), "grrm_out": (4124.5, 1140.0), "grrm_statue": (4112.0, 1142.0), "lasher_grrm": (4108.0, 1139.0),
    "ssarnath_pens": (4101.0, 1150.0), "shade_pens": (4098.0, 1152.0), "pens_lasher_1": (4098.0, 1122.0), "pens_lasher_2": (4084.0, 1140.0),
    "slave_a": (4100.0, 1116.0), "slave_b": (4094.0, 1124.0), "slave_c": (4090.0, 1112.0), "slave_d": (4104.0, 1106.0),
    "slave_line_1": (4108.0, 1145.0), "slave_line_2": (4102.0, 1140.0), "slave_line_3": (4095.0, 1134.0),
    "wall_n1": (4122.5, 1092.0), "wall_n2": (4122.5, 1097.0), "wall_n3": (4122.5, 1106.0), "wall_n4": (4122.5, 1111.0),
    "wall_n5": (4122.5, 1116.0), "wall_n6": (4122.5, 1122.0), "wall_n7": (4122.5, 1127.0), "wall_n8": (4122.5, 1132.0),
    "wall_n9": (4122.5, 1138.0), "wall_n10": (4122.5, 1144.0), "wall_n11": (4122.5, 1158.0), "wall_n12": (4122.5, 1164.0),
    "wall_e1": (4116.0, 1088.0), "wall_e2": (4110.0, 1088.0), "wall_e3": (4104.0, 1088.0), "wall_e4": (4090.0, 1088.0),
    "wall_e5": (4084.0, 1088.0), "wall_e6": (4078.0, 1088.0), "wall_e7": (4072.0, 1088.0), "wall_e8": (4066.0, 1088.0),
    "wall_e9": (4060.0, 1088.0), "wall_e10": (4054.0, 1088.0),
    # the uprising: the 3 gates, the jar of name-shells, who comes through
    "gate_north": (4122.5, 1101.5), "gate_east": (4097.0, 1088.0), "gate_sea": (4084.0, 1152.0), "shell_jar": (4117.0, 1042.0),
    "guards_n": (4136.0, 1101.0), "guards_n2": (4138.0, 1106.0), "guards_e": (4097.0, 1074.0), "guards_e2": (4092.0, 1072.0),
    "guards_s": (4085.0, 1158.0), "guards_s2": (4080.0, 1160.0), "slaves_n": (4116.0, 1104.0), "slaves_e": (4097.0, 1096.0),
    "slaves_s": (4086.0, 1144.0), "dunes": (4146.0, 1060.0), "jar_crowd_1": (4114.0, 1046.0), "jar_crowd_2": (4120.0, 1048.0),
    "shells_1": (4116.0, 1044.5), "shells_2": (4119.0, 1040.0), "count_1": (4089.0, 1058.0), "count_2": (4089.0, 1068.0),
    "jubilant_1": (4126.0, 1124.0), "jubilant_2": (4126.0, 1114.0), "jubilant_3": (4114.0, 1126.0), "jubilant_4": (4114.0, 1114.0),
    "fire_1": (4116.0, 1046.0), "fire_2": (4100.0, 1082.0),
    # the Saltscar camp (the freed pens): the hub kit in two rings around the fire
    "hub": (4106.0, 1112.0), "camp_fire": (4106.0, 1112.0),
    "c_grrmlgrrl": (4114.0, 1112.0), "c_murlorga": (4111.7, 1117.7), "c_glubbub": (4106.0, 1120.0), "c_blrrgl": (4100.3, 1117.7),
    "c_caller": (4098.0, 1112.0), "c_mrrlglr": (4100.3, 1106.3), "c_fnrrgl": (4106.0, 1104.0), "c_krrgl": (4111.7, 1106.3),
    "c_brrgmrk": (4114.6, 1124.3), "c_mrrgasha": (4109.9, 1126.5), "c_glubba": (4104.7, 1126.9), "c_fizzmrgl": (4099.7, 1125.6),
    "c_slubb": (4095.4, 1122.6), "c_gurgle": (4092.4, 1118.3), "c_mrsha": (4091.1, 1113.3), "c_brewglub": (4091.5, 1108.1),
    "c_grrsh": (4093.7, 1103.4), "c_mrrsk": (4097.4, 1099.7), "c_brrkl": (4102.1, 1097.5), "c_mmrglla": (4107.3, 1097.1),
    "c_sprokgl": (4112.3, 1098.4), "c_shimmrl": (4116.6, 1101.4), "c_pearlmrgl": (4119.6, 1105.7), "c_scrawlgl": (4120.9, 1110.7),
    "c_pot": (4113.5, 1121.0), "c_log": (4098.0, 1121.0), "c_mail": (4110.0, 1133.0), "c_hut_1": (4106.0, 1134.0),
    "c_hut_2": (4093.0, 1129.0), "c_hut_3": (4100.0, 1090.0), "camp_grave": (4094.0, 1140.0),
    "c_freed_1": (4096.0, 1132.0), "c_freed_2": (4114.0, 1131.0), "c_freed_3": (4088.0, 1124.0), "c_freed_4": (4112.0, 1091.0),
    "whip_spot": (4116.0, 1110.0),
    # the burned pens
    "burn_1": (4116.0, 1046.0), "burn_2": (4124.0, 1022.0), "burn_3": (4074.0, 1106.0), "smoke_1": (4110.0, 1052.0),
    "smoke_2": (4082.0, 1095.0), "ash_1": (4101.0, 1080.0), "ash_2": (4088.0, 1145.0), "statue_rubble": (4111.0, 1146.0),
    "post_stump_1": (4122.5, 1120.0), "post_stump_2": (4122.5, 1150.0), "post_stump_3": (4075.0, 1088.0),
    # the fights after the uprising
    "kez_gong": (4123.0, 1045.0), "kezzith_fight": (4119.0, 1040.0), "kez_ally_1": (4112.0, 1052.0), "kez_ally_2": (4108.0, 1046.0),
    "kez_ally_3": (4114.0, 1058.0), "ssarnath_fight": (4109.0, 1153.0), "ssa_ally_1": (4100.0, 1140.0), "ssa_ally_2": (4096.0, 1146.0),
    "ssa_ally_3": (4104.0, 1136.0), "ssa_grrm": (4103.0, 1143.0), "ssa_elem_1": (4112.0, 1160.0), "ssa_elem_2": (4102.0, 1158.0),
    "fallen_statue": (4110.0, 1151.0, -3.0),
    # the pool, the jetty, the shore below the statue
    "pool": (4104.0, 1160.0), "pool_ilyssa": (4102.0, 1157.0), "pool_net": (4103.0, 1159.0), "pool_dive": (4100.0, 1176.0),
    "sloshy_run": (4106.0, 1153.0), "shape_1": (4070.0, 1172.0), "shape_2": (4078.0, 1166.0), "shape_3": (4086.0, 1161.0),
    "jetty_foot": (4091.0, 1149.0), "jetty_end": (4090.0, 1163.0, 0.0), "jetty_stroke": (4091.5, 1151.5), "smile_watch": (4100.0, 1146.0),
    "shell_splash": (4112.0, 1180.0),
    "ship_3": (4238.0, 1212.0, 0.0), "deck": (4238.5, 1211.0, 3.5), "ship_far": (4300.0, 1300.0, 0.0), "deck_far": (4300.5, 1299.0, 3.5),
    "chase_1": (4128.0, 1170.0), "chase_2": (4196.0, 1186.0), "chase_3": (4246.0, 1188.0),
    "shellback_wait": (4060.0, 1215.0, -2.0), "shellback_shore": (4082.0, 1182.0, -1.0), "shellback_back": (4083.0, 1180.0, 1.0),
    "conch_stone": (4094.0, 1157.0), "climb_1": (4090.0, 1165.0), "climb_2": (4086.0, 1170.0),
    "shells_row_1": (4097.0, 1150.0), "shells_row_2": (4099.5, 1151.0), "shells_row_3": (4102.0, 1152.0),
    "shells_row_4": (4104.5, 1153.0), "shells_row_5": (4107.0, 1154.0),
    "raft": (4090.0, 1166.0, 0.0), "raft_far": (4040.0, 1230.0, 0.0), "mourn_1": (4088.0, 1158.0), "mourn_2": (4093.0, 1160.0),
    "mourn_3": (4098.0, 1162.0), "clacker": (3998.0, 1218.0),
    "line_1": (4108.0, 1148.0), "line_2": (4104.0, 1148.0), "line_3": (4100.0, 1148.0), "line_4": (4096.0, 1148.0),
    "line_5": (4092.0, 1148.0), "line_you": (4106.0, 1145.0), "glimmrl_tied": (4113.0, 1129.0), "glimmrl_sea": (4080.0, 1176.0),
    "brine_pit": (4110.0, 1062.0), "glimmrl_pit": (4112.0, 1066.0),
    # the temple's mouth (Blackfathom Deeps): its floor is the ruin's, so the cages' heights are the game's spawns'
    "tithe_watch": (4195.0, 1000.0), "tithe_priestess": (4156.0, 978.0), "tp_front": (4158.0, 974.0),
    "tithe_slave_1": (4152.0, 982.0), "tithe_slave_2": (4149.0, 985.0), "tithe_slave_3": (4146.0, 988.0),
    "gelihast": (4164.0, 958.0, -15.5), "gelihast_out": (4158.0, 972.0), "tithe_cultist": (4151.0, 972.0),
    "sarevess": (4180.0, 936.0, -12.5), "cage_a": (4167.0, 952.0, -17.0), "cage_b": (4185.0, 931.0, -12.5),
    "cage_c": (4206.0, 923.0, -9.0), "cage_blind": (4222.0, 904.0, -7.0), "cage_run": (4140.0, 1000.0),
    # Lake Falathim, Ordil'Aran
    "mudgrin": (3172.0, 530.0), "lake_fish": (3168.0, 522.0), "spring": (3180.0, 516.0), "spring_2": (3177.0, 520.0),
    "poison_pool": (3166.0, 526.0), "reeds_1": (3162.0, 540.0), "reeds_2": (3165.0, 548.0), "reeds_3": (3158.0, 534.0),
    "lake_mud": (3176.0, 536.0), "lake_hut": (3180.0, 540.0), "ordilaran": (3490.0, -100.0),
    # Zoram'gar's shore
    "zalja": (3428.0, 1060.0), "zalja_net": (3425.0, 1057.0), "zalja_box": (3424.0, 1063.0), "zalja_lunch": (3427.0, 1063.5),
    "zalja_swim": (3436.0, 1070.0), "float_1": (3446.0, 1090.0, 0.0), "float_2": (3452.0, 1102.0, 0.0),
    "float_3": (3440.0, 1110.0, 0.0), "float_4": (3448.0, 1080.0, 0.0), "float_5": (3430.0, 1098.0, 0.0),
    "float_6": (3456.0, 1118.0, 0.0), "rack_1": (3368.0, 1042.0), "rack_2": (3373.0, 1048.0), "rack_3": (3364.0, 1050.0),
    "wrathtail_beach": (3500.0, 1080.0),
    # Maestra's Post
    "nerelith_post": (3222.0, 214.0), "sentinel_1": (3243.0, 246.0), "sentinel_2": (3236.0, 253.0), "post_table": (3219.0, 211.0),
    "post_sand": (3224.0, 217.0), "post_gate": (3237.0, 243.0),
    # the siren's rock, Ruuzel's island, the hunter's crawler
    "vespia_rock": (3740.0, 950.0), "vespia_rise": (3752.0, 972.0), "key_chest": (4166.0, 1281.0), "ruuzel_rise": (4160.0, 1276.0),
    "thrashclaw": (4160.0, 1005.0),
}

# -- the people -------------------------------------------------------------------------------------

NPCS = [
    # the Greymist war band at the pier
    dict(key="warleader", name="Rrlgash Tidespear", subname="Greymist War Leader", look="murloc_slate", level=26, role="quest",
         at="warleader", facing=5.5, phase=PRE,
         greeting="Spears up. Spears down. Spears up again. The long ones will learn what a spear is for.",
         idle=[("every", 31000, [("emote", "self", "flex")]), ("every", 47000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget")])]),
    dict(key="fighter", name="Greymist Fighter", plural="Greymist fighters", look="murloc_grey", looks=["murloc_green", "murloc_blue"],
         level=(19, 21), role="ambient", at=["fighter_1", "fighter_2", "fighter_3", "fighter_4", "fighter_5", "fighter_6"],
         facing=None, phase=PRE, greeting="Mrgl. Spear's sharp. Belly's empty.",
         idle=[("state", "self", "work"), ("every", 29000, [("sound", "self", 1194)])]),
    dict(key="weeper", name="Greymist Fighter", look="murloc_blue", level=19, role="ambient", at="weeper", facing=5.6, phase=PRE,
         idle=[("state", "self", "sit"), ("every", 43000, [("sound", "self", "murloc_fidget2")])]),
    dict(key="giggler", name="Greymist Fighter", look="murloc_orange", level=20, role="ambient", at="giggler", facing=4.15, phase=PRE,
         idle=[("every", 37000, [("emote", "self", "laugh"), ("sound", "self", "murloc_fidget")])]),
    dict(key="cruncher", name="Greymist Fighter", look="murloc_red", scale=1.15, level=21, role="ambient", at="cruncher", facing=2.68,
         phase=PRE, idle=[("every", 41000, [("emote", "self", "eat")])]),

    # the Saltspittle of Lake Falathim
    dict(key="mudgrin", name="Old Mudgrin", subname="Elder of the Saltspittle", look="murloc_bronze", scale=1.1, level=26,
         role="quest", at="mudgrin", facing=5.23, phase=PRE,
         greeting="The lake was clear once. Clear to the bottom. Now I can't see my own feet.",
         idle=[("every", 39000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="reed_warrior", name="Saltspittle Warrior", look="murloc_green", looks=["murloc_bronze"], level=20, role="ambient",
         summoned=True, idle=[("every", 9000, [("emote", "self", "cheer")])]),

    # Blrrgl along on the way to the lake (3.05)
    dict(key="blrrgl_tag", name="Blrrgl the Snatcher", look="murloc_green", level=24, role="ambient", summoned=True),

    # the Blindlight deserter (from 3.13 at the pier), and his crab
    dict(key="deserter", name="Pale Mmurk", subname="Blindlight Deserter", look="murloc_pale", level=21, role="quest",
         at="deserter", facing=0.79, phase=DESERTER, greeting="I hear you. I know your feet. You walk like the one who opened the cage.",
         idle=[("every", 40000, [("face", "self", "crab_spot"), ("emote", "self", "kneel"), ("sound", "self", 1186)])]),
    dict(key="pier_crab", name="Pinchy", look=9566, scale=0.35, level=1, role="ambient", at="crab_spot", facing=3.93,
         phase=DESERTER, idle=[("every", 23000, [("sound", "self", 1229)])]),
    dict(key="deserter_freed", name="Pale Mmurk", subname="Blindlight Deserter", look="murloc_pale", level=21, role="ambient",
         summoned=True),
    dict(key="caged_slave", name="Tithe Slave", look="murloc_grey", looks=["murloc_green", "murloc_bronze"], level=12,
         role="ambient", summoned=True),

    # Maestra's Post: its sentinels at the road (the module warns a murloc it doesn't like, in Darnassian)
    dict(key="sentinel", name="Maestra's Post Sentinel", look=4849, looks=[2867], level=25, side="faction:69", role="guard",
         language="darnassian", flags_extra=0x8000, detection=5.0, at=["sentinel_1", "sentinel_2"], facing=0.8, phase=PRE),

    # the pens as the naga keep them: the Lasher who whips Grrmlgrrl for standing
    dict(key="lasher_grrm", name="Wrathtail Lasher", look="naga_male", level=26, side="neutral", role="ambient", language="naga",
         health=4.0, at="lasher_grrm", facing=0.64, phase=PENS,
         idle=[("every", 15000, [("emote", "self", "attack"), ("sound", "self", 3338), ("wait", 900),
                                 ("emote", "ch1:grrmlgrrl", "roar"), ("sound", "ch1:grrmlgrrl", "murloc_wound")]),
               ("every", 41000, [("say", "self", "Sit. SIT, slave.", "roar", "naga_hiss")])]),

    # the uprising: the pens' guards, and who fights beside you
    dict(key="pen_guard", name="Wrathtail Pen-Guard", plural="Pen-Guards", look="naga_male", looks=["myrmidon"], level=(21, 22),
         side="naga", role="enemy", language="naga", summoned=True, abilities=[(11976, 7000)]),
    dict(key="freed_slave", name="Freed Slave", look="murloc_grey", looks=["murloc_green", "murloc_orange", "murloc_blue"],
         level=20, side=250, role="ambient", health=1.5, damage=0.4, summoned=True),
    dict(key="greymist_ally", name="Greymist Warrior", look="murloc_slate", looks=["murloc_grey"], level=21, side=250,
         role="ambient", health=2.0, damage=0.5, summoned=True),
    dict(key="grrm_ally", name="Grrmlgrrl the Tidehunter", look="murloc_slate", scale=1.15, level=24, side=250, role="ambient",
         health=4.0, damage=0.8, summoned=True, abilities=[(11976, 6000)]),
    dict(key="jubilant", name="Freed Slave", look="murloc_green", looks=["murloc_orange", "murloc_purple", "murloc_ice"], level=15,
         role="ambient", summoned=True, idle=[("every", 5000, [("emote", "self", "cheer"), ("sound", "self", "murloc_aggro")])]),

    # Kezzith and the Tidebinder, killable after the uprising
    dict(key="kezzith_fight", name="Overseer Kezzith", look="myrmidon", level=23, side="naga", role="enemy", language="naga",
         health=2.5, at="kezzith_fight", facing=0.9, respawn=60, phase=FIGHT, abilities=[(11976, 8000), (6533, 16000)],
         watch=(30, [("face", "self", "player"), ("sound", "self", 12827), ("yell", "self", "COUNT! Back to your shells! COUNT!", "roar"),
                     ("sound", "self", 3338), ("summon", "freed_slave", "kez_ally_1", 60), ("summon", "freed_slave", "kez_ally_2", 60),
                     ("summon", "freed_slave", "kez_ally_3", 60)], 60000)),
    dict(key="ssarnath_fight", name="Lord Ssarnath the Tidebinder", look="naga_lord", scale=1.1, level=24, side="naga", role="enemy",
         language="naga", health=3.0, at="ssarnath_fight", facing=5.88, respawn=60, phase=FIGHT,
         abilities=[(9672, 9000), (11831, 20000)],
         at_health=(17, [("yell", "self", "My face... MY FACE!", "roar", 11691), ("sound", "self", 12549),
                         ("object", "fallen_statue", "fallen_statue", 60), ("visual", "self", 34602), ("aura", "self", "crushed"),
                         ("emote", "grrm_ally", "roar"), ("sound", "grrm_ally", "murloc_aggro")]),
         watch=(35, [("face", "self", "player"), ("yell", "self", "Kneel! KNEEL, all of you! I am your lord!", "roar", "naga_lord_aggro"),
                     ("sound", "self", 9938), ("summon", "tide_elemental", "ssa_elem_1", 90), ("summon", "tide_elemental", "ssa_elem_2", 90),
                     ("summon", "grrm_ally", "ssa_grrm", 90), ("summon", "greymist_ally", "ssa_ally_1", 90),
                     ("summon", "greymist_ally", "ssa_ally_2", 90), ("summon", "freed_slave", "ssa_ally_3", 90)], 90000)),
    dict(key="tide_elemental", name="Tidebound Elemental", look=525, scale=0.7, level=21, side="naga", role="enemy", health=0.8,
         summoned=True),

    # the tithe at the temple's mouth (while 3.12 is in the log): seen, never fought
    dict(key="tithe_priestess", name="Blackfathom Tide Priestess", look=4983, level=22, side="neutral", role="ambient",
         language="naga", unit_flags=0x302, at="tithe_priestess", facing=5.03, phase=TITHE,
         watch=(55, [("emote", "self", "talk"), ("sound", "self", "siren_hiss"), ("move", "self", "tp_front", "walk"),
                     ("move", "tithe_slave_a", "tithe_slave_1", "walk"), ("sound", "tithe_slave_a", 1005),
                     ("move", "gelihast", "gelihast_out", "walk"), ("wait", 6000),
                     ("emote", "gelihast", "bow"), ("emote", "self", "talk"), ("wait", 2500), ("emote", "gelihast", "point"),
                     ("move", "tithe_slave_a", "gelihast", "walk"), ("emote", "tithe_slave_a", "cry"), ("sound", "tithe_slave_a", 1188),
                     ("emote", "tithe_cultist", "talk"), ("sound", "tithe_cultist", 120), ("wait", 900), ("sound", "tithe_cultist", 895),
                     ("move", "gelihast", "gelihast", "walk"), ("wait", 3000), ("face", "sarevess", "player"),
                     ("sound", "sarevess", "siren_aggro"), ("wait", 1500), ("cast", "sarevess", 24199, "player"), ("music", 5037),
                     ("wait", 12000), ("move", "tithe_slave_a", "tithe_slave_1", "walk"), ("move", "self", "tithe_priestess", "walk")],
               120000)),
    dict(key="tithe_slave_a", name="Chained Slave", look="murloc_grey", level=12, role="ambient", unit_flags=0x302,
         at="tithe_slave_1", facing=5.0, phase=TITHE, idle=[("every", 17000, [("emote", "self", "cry")])]),
    dict(key="tithe_slave_b", name="Chained Slave", look="murloc_green", level=12, role="ambient", unit_flags=0x302,
         at="tithe_slave_2", facing=5.0, phase=TITHE, idle=[("every", 21000, [("emote", "self", "beg")])]),
    dict(key="tithe_slave_c", name="Chained Slave", look="murloc_bronze", level=11, role="ambient", unit_flags=0x302,
         at="tithe_slave_3", facing=5.0, phase=TITHE, idle=[("every", 19000, [("sound", "self", 1005)])]),
    dict(key="gelihast", name="Gelihast", subname="", look="murloc_gold", scale=1.35, level=26, side="neutral", role="ambient",
         unit_flags=0x302, at="gelihast", facing=1.98, phase=TITHE),
    dict(key="tithe_cultist", name="Twilight Acolyte", look=2882, level=22, side="neutral", role="ambient", language="common",
         unit_flags=0x302, at="tithe_cultist", facing=0.88, phase=TITHE, idle=[("every", 15000, [("sound", "self", 120)])]),
    dict(key="sarevess", name="Lady Sarevess", look=4979, scale=1.6, level=25, side="neutral", role="ambient", language="naga",
         unit_flags=0x302, at="sarevess", facing=1.34, phase=TITHE),

    # rares called by their places (3.16, 3.17)
    dict(key="vespia", name="Lady Vespia", look=4979, level=22, side="naga", role="enemy", language="naga", health=2.0,
         summoned=True, abilities=[(12548, 9000)],
         watch=(35, [("face", "self", "player"), ("yell", "self", "Come home, little one... home, to the water...", None, 4025)], 30000)),
    dict(key="ruuzel", name="Ruuzel", look=5029, level=22, side="naga", role="enemy", language="naga", health=2.0, summoned=True,
         abilities=[(11976, 7000)],
         watch=(35, [("face", "self", "player"), ("yell", "self", "My keys! Who touches MY keys?", "roar", "siren_aggro")], 30000)),
    # the hunter's lesson, the Strand's biggest crawler
    dict(key="thrashclaw", name="Thrashclaw", look=1001, scale=1.6, level=22, side="hostile", role="enemy", health=2.0,
         at="thrashclaw", wander=5.0, respawn=90, phase=PRE, abilities=[(3427, 12000)]),
    # 3.27: the old crab on the Great Conch, in the deepest water
    dict(key="old_clacker", name="Old Clacker", look=9566, scale=1.9, level=24, side="hostile", role="enemy", health=3.0,
         at="clacker", respawn=120, phase=CAMP, abilities=[(3427, 12000)]),

    # the night of the smile, and the clutch taken (summoned in the Elder's scenes)
    dict(key="glimmrl_night", name="Glimmrl the Smiling", look="murloc_gold", level=16, role="ambient", summoned=True),
    dict(key="tithe_ship", name="Tithe Ship", look=23278, scale=0.55, level=1, side="neutral", role="ambient", unit_flags=0x02000002,
         summoned=True),
    dict(key="sloshy_deck", name="Sloshy", look="murloc_blue", scale=0.6, level=5, role="ambient", summoned=True,
         watch=(40, [("face", "self", "player"), ("emote", "self", "wave"), ("sound", "self", "baby_murloc"), ("wait", 1800),
                     ("emote", "self", "wave"), ("wait", 1500), ("emote", "self", "cry"), ("music", 6074), ("credit", "ch3_clutch"),
                     ("wait", 2500), ("sound", "self", 419), ("wait", 3000), ("move", "tithe_ship", "ship_far", "walk"),
                     ("move", "self", "deck_far", "walk")], 60000)),

    # Glimmrl, tied (3.24a and b)
    dict(key="glimmrl_tied", name="Glimmrl the Smiling", subname="Bound", look="murloc_gold", level=16, role="ambient",
         summoned=True, greeting="...", idle=[("state", "self", "kneel"), ("every", 11000, [("emote", "self", "beg")])]),

    # the tribe, named and climbing (3.25, 3.28)
    dict(key="namer", name="Saltscar", look="murloc_grey", looks=["murloc_blue", "murloc_green", "murloc_purple"],
         level=15, role="ambient", summoned=True),
    dict(key="kelp_raft", name="Funeral Raft", look=30874, scale=0.45, level=1, side="neutral", role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 3000, [("visual", "self", 22576)])]),

    # the camp's freed slaves
    dict(key="freed", name="Freed Slave", plural="freed slaves", look="murloc_purple", looks=["murloc_bronze", "murloc_ice"],
         level=(14, 16), role="ambient", at=["c_freed_3", "c_freed_4"], phase=CAMP,
         idle=[("state", "self", "work"), ("every", 33000, [("sound", "self", 1194)])]),
]

# -- things ------------------------------------------------------------------------------------------

CORAL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\Coral01.mdx"
CORAL_TREE = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree01.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
SHELL_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
MOUND = "World\\Azeroth\\Duskwood\\PassiveDoodads\\Tombs\\DirtMound01.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
FISH = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadBlue.mdx"
FISH_BIG = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadOrange.mdx"
FISH_RACK = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishRack.mdx"
CHAINS = "World\\Expansion01\\Doodads\\Generic\\Ogre\\Chains\\OM_Chains_01.mdx"
BASKET = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\Fishing\\TS_FishingBasket_Empty_02.mdx"
WALL = ["wall_n1", "wall_n2", "wall_n3", "wall_n4", "wall_n5", "wall_n6", "wall_n7", "wall_n8", "wall_n9", "wall_n10", "wall_n11",
        "wall_n12", "wall_e1", "wall_e2", "wall_e3", "wall_e4", "wall_e5", "wall_e6", "wall_e7", "wall_e8", "wall_e9", "wall_e10"]

OBJECTS = [
    # the Drowned Pier
    dict(key="dock", model=6557, name="The Drowned Pier", at="dock", kind="doodad", facing=0.9, phase=PRE),
    dict(key="ruin_column", model=2934, name="Elven Ruin", at=["column_1", "column_3"], kind="doodad", scale=0.8, phase=PRE),
    dict(key="ruin_column_b", model=249, name="Elven Ruin", at="column_2", kind="doodad", scale=0.7, facing=2.0, phase=PRE),
    dict(key="anchor", model=4873, name="Drowned Anchor", at="anchor", kind="doodad", scale=0.7, facing=0.4, phase=PRE),
    dict(key="pier_hut", model="murloc_hut", name="Greymist Hut", at=["pier_hut_1", "pier_hut_2"], kind="doodad", scale=0.9, phase=PRE),
    dict(key="pier_fire", model="campfire", name="Campfire", at="pier", kind="doodad", phase=PRE),
    dict(key="pier_spears", model="naga_weapons", name="Spears", at="pier_spears", kind="doodad", scale=0.7, facing=0.3, phase=PRE),

    # the stockade and the uprising
    dict(key="stockade_post", model=CORAL_TREE, name="Stockade", at=WALL, kind="doodad", scale=0.8, phase=PENS),
    dict(key="gate_north", model=CHAINS, name="North Pen Gate", at="gate_north", kind="use", quest="ch3_uprising", facing=0.0,
         phase=PENS,
         beats=[("give", "broken_lock", 1), ("sound", "ch1:mrrlglr", 12712), ("summon", "pen_guard", "guards_n", 120),
                ("summon", "pen_guard", "guards_n2", 120), ("summon", "pen_guard", "guards_n", 120),
                ("summon", "pen_guard", "guards_n2", 120), ("summon", "grrm_ally", "slaves_n", 90),
                ("summon", "freed_slave", "slaves_n", 90), ("summon", "freed_slave", "slaves_n", 90),
                ("summon", "greymist_ally", "dunes", 90), ("summon", "greymist_ally", "dunes", 90),
                ("emote", "ch1:mrrlglr", "cheer"), ("sound", "ch1:mrrlglr", "murloc_aggro"),
                ("move", "ch2:murkdeep", "guards_n", "run"), ("emote", "ch2:murkdeep", "roar"), ("wait", 45000),
                ("move", "ch2:murkdeep", "murkdeep_dunes", "walk")]),
    dict(key="gate_east", model=CHAINS, name="East Pen Gate", at="gate_east", kind="use", quest="ch3_uprising", facing=1.57,
         phase=PENS,
         beats=[("give", "broken_lock", 1), ("sound", "ch1:squirt", 12712), ("summon", "pen_guard", "guards_e", 120),
                ("summon", "pen_guard", "guards_e2", 120), ("summon", "pen_guard", "guards_e", 120),
                ("summon", "pen_guard", "guards_e2", 120), ("summon", "freed_slave", "slaves_e", 90),
                ("summon", "freed_slave", "slaves_e", 90), ("summon", "freed_slave", "slaves_e", 90),
                ("emote", "ch1:squirt", "cheer"), ("sound", "ch1:squirt", "murloc_aggro")]),
    dict(key="gate_sea", model=CHAINS, name="Sea Gate", at="gate_sea", kind="use", quest="ch3_uprising", facing=1.6, phase=PENS,
         beats=[("give", "broken_lock", 1), ("sound", "ch1:gurp", 12712), ("summon", "pen_guard", "guards_s", 120),
                ("summon", "pen_guard", "guards_s2", 120), ("summon", "pen_guard", "guards_s", 120),
                ("summon", "pen_guard", "guards_s2", 120), ("summon", "freed_slave", "slaves_s", 90),
                ("summon", "freed_slave", "slaves_s", 90), ("summon", "freed_slave", "slaves_s", 90),
                ("emote", "ch1:gurp", "cheer"), ("sound", "ch1:gurp", "murloc_aggro")]),
    dict(key="name_jar", model="naga_jar", name="Jar of Name-Shells", at="shell_jar", kind="use", quest="ch3_uprising", scale=1.4,
         phase=PENS,
         beats=[("credit", "ch3_uprising"), ("sound", "ch1:beaten_slave", 12334), ("object", "shell_pile", "shells_1", 60),
                ("object", "shell_pile", "shells_2", 60), ("move", "ch1:beaten_slave", "jar_crowd_1", "run"),
                ("move", "ch1:sitter", "jar_crowd_2", "run"), ("wait", 5000), ("emote", "ch1:beaten_slave", "cheer"),
                ("sound", "ch1:beaten_slave", "murloc_aggro"), ("emote", "ch1:sitter", "cry"), ("wait", 15000),
                ("move", "ch1:beaten_slave", "count_1", "walk"), ("move", "ch1:sitter", "count_2", "walk")]),

    # the camp: the burned pens
    dict(key="camp_fire", model="bonfire", name="Saltscar Fire", at="camp_fire", kind="doodad", phase=CAMP),
    dict(key="camp_hut", model="murloc_hut", name="Saltscar Hut", at=["c_hut_1", "c_hut_3"], kind="doodad", scale=0.9, phase=CAMP),
    dict(key="camp_hut_2", model="murloc_hut2", name="Saltscar Hut", at="c_hut_2", kind="doodad", scale=0.9, phase=CAMP),
    dict(key="burnt_tent", model=5834, name="Burned Tent", at=["burn_1", "burn_2"], kind="doodad", scale=0.6, phase=CAMP),
    dict(key="burnt_ground", model=7438, name="Burned Ground", at=["burn_1", "burn_2", "burn_3", "ash_1"], kind="doodad", phase=CAMP),
    dict(key="smoke", model=2390, name="Smoke", at=["smoke_1", "smoke_2"], kind="doodad", phase=CAMP),
    dict(key="ash", model=7256, name="Ash", at=["ash_1", "ash_2"], kind="doodad", phase=CAMP),
    dict(key="broken_gate", model=6683, name="Broken Gate", at=["gate_north", "gate_east"], kind="doodad", scale=0.8, phase=CAMP),
    dict(key="post_stump", model=CORAL_TREE, name="Broken Stockade", at=["post_stump_1", "post_stump_2", "post_stump_3"],
         kind="doodad", scale=0.35, phase=CAMP),
    dict(key="rubble", model=4318, name="Rubble", at="statue_rubble", kind="doodad", scale=0.5, phase=CAMP),
    dict(key="brine_pit", model="naga_jar", name="The Brine Pit", at="brine_pit", kind="use", quest="ch3_brinepit", scale=2.6,
         consumable=False, phase=CAMP,
         beats=[("move", "glimmrl_tied", "brine_pit", "walk"), ("state", "glimmrl_tied", "none"), ("emote", "glimmrl_tied", "beg"),
                ("sound", "glimmrl_tied", "murloc_wound"), ("wait", 2500), ("emote", "glimmrl_tied", "beg"), ("wait", 1500),
                ("despawn", "glimmrl_tied"), ("sound", "ch1:murlorga", 1207), ("credit", "ch3_brinepit"), ("wait", 1500),
                ("face", "ch1:murlorga", "c_pot"), ("state", "ch1:murlorga", "none")]),
    dict(key="fallen_shell", model=SHELL_2, name="Name-Shell of the Fallen", kind="loot", loot=[("fallen_shell", 1, 1)],
         quest="ch3_shells", scale=1.2, at=["shells_row_1", "shells_row_2", "shells_row_3", "shells_row_4", "shells_row_5"],
         facing=1.0, phase=CAMP),

    # Grandmother Shellback's stone (from 3.27)
    dict(key="conch_stone", model=CORAL, name="Conch-Stone", at="conch_stone", kind="use", quest="ch3_end", scale=0.9,
         consumable=False, phase=CONCH,
         beats=[("music", 7034), ("move", "ch0:shellback", "shellback_shore", "walk"), ("sound", "ch0:shellback", 1463),
                ("cast", "ch0:shellback", 36005, "self"), ("wait", 4000), ("sound", "ch0:shellback", "splash_big"),
                ("cast", "ch0:shellback", 47479, "self"), ("credit", "ch3_end")]),

    # the temple's mouth: the tithe cages
    dict(key="cage_a", model=7295, name="Tithe Cage", at="cage_a", kind="use", quest="ch3_cages", facing=1.0, phase=PRE,
         beats=[("give", "broken_shackle", 1), ("summon", "caged_slave", "cage_a", 25), ("sound", "caged_slave", 1005),
                ("emote", "caged_slave", "cheer"), ("move", "caged_slave", "cage_run", "run")]),
    dict(key="cage_b", model=7295, name="Tithe Cage", at="cage_b", kind="use", quest="ch3_cages", facing=2.0, phase=PRE,
         beats=[("give", "broken_shackle", 1), ("summon", "caged_slave", "cage_b", 25), ("sound", "caged_slave", 1005),
                ("emote", "caged_slave", "cheer"), ("move", "caged_slave", "cage_run", "run")]),
    dict(key="cage_c", model=7295, name="Tithe Cage", at="cage_c", kind="use", quest="ch3_cages", facing=0.5, phase=PRE,
         beats=[("give", "broken_shackle", 1), ("summon", "caged_slave", "cage_c", 25), ("sound", "caged_slave", 1005),
                ("emote", "caged_slave", "cheer"), ("move", "caged_slave", "cage_run", "run")]),
    dict(key="cage_blind", model=7295, name="Tithe Cage", at="cage_blind", kind="use", quest="ch3_cages", facing=2.5, phase=PRE,
         beats=[("give", "broken_shackle", 1), ("summon", "deserter_freed", "cage_blind", 180), ("sound", "deserter_freed", 1005),
                ("face", "deserter_freed", "player"), ("emote", "deserter_freed", "beg"), ("sound", "deserter_freed", "murloc_fidget2"),
                ("wait", 2500), ("emote", "deserter_freed", "kiss"), ("follow", "deserter_freed")]),

    # the siren's rock, Ruuzel's chest
    dict(key="vespia_rock", model=8052, name="Siren's Rock", at="vespia_rock", kind="use", quest="ch3_vespia", scale=0.7,
         phase=PRE, beats=[("summon", "vespia", "vespia_rise", 120)]),
    dict(key="key_chest", model="naga_crate", name="Ruuzel's Key Chest", at="key_chest", kind="use", quest="ch3_key", scale=0.8,
         facing=2.4, phase=PRE, beats=[("summon", "ruuzel", "ruuzel_rise", 120)]),

    # Lake Falathim: Mudgrin's hut, the reeds, the spring (and the lessons there)
    dict(key="lake_hut", model="murloc_hut2", name="Mudgrin's Hut", at="lake_hut", kind="doodad", scale=0.8, phase=PRE),
    dict(key="reeds", model="kelp", name="Reeds", at=["reeds_1", "reeds_2", "reeds_3"], kind="doodad", scale=1.3, phase=PRE),
    dict(key="spring_loot", model="seaweed", name="Falathim Spring", at="spring", kind="loot", loot=[("spring_water", 1, 1)],
         quest="ch3_lesson_shaman", phase=PRE),
    dict(key="spring_bless", model=4136, name="Spring of Falathim", at="spring_2", kind="use", quest="ch3_lesson_priest",
         consumable=False, phase=PRE,
         beats=[("take", "blessing_vial", 1), ("cast", "mudgrin", 57771, "self"), ("sound", "mudgrin", "murloc_fidget2"),
                ("credit", "ch3_lesson_priest")]),
    dict(key="poison_pool", model=7040, name="Black Brew Slick", at="poison_pool", kind="use", quest="ch3_lesson_mage",
         consumable=False, phase=PRE,
         beats=[("cast", "mudgrin", 32992, "self"), ("sound", "mudgrin", "murloc_alert"), ("credit", "ch3_lesson_mage")]),

    # Zoram'gar's shore: Zalja's tackle, the floats, the outpost's drying racks
    dict(key="zalja_box", model=6396, name="Zalja's Tackle", at="zalja_box", kind="doodad", facing=2.0, phase=PRE),
    dict(key="net_float", model=6366, name="Net Float", kind="loot", loot=[("net_float", 1, 1)], quest="ch3_floats", scale=0.35,
         at=["float_1", "float_2", "float_3", "float_4", "float_5", "float_6"], phase=PRE),
    dict(key="drying_rack", model=FISH_RACK, name="Drying Rack", kind="loot", loot=[("zoram_fish", 2, 2)], quest="ch3_larder",
         at=["rack_1", "rack_2", "rack_3"], facing=1.2, phase=PRE),

    # Maestra's Post
    dict(key="post_table", model=6608, name="Sentinel's Table", at="post_table", kind="doodad", facing=0.9, phase=PRE),

    # set out by scenes
    dict(key="sand_naga", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.5),
    dict(key="sand_mound", model=MOUND, name="Drawing in the Sand", kind="doodad", scale=0.25),
    dict(key="sand_gate", model=6683, name="Drawing in the Sand", kind="doodad", scale=0.12),
    dict(key="sand_key", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.2),
    dict(key="spear_shaft", model=TRIDENT, name="Headless Spear", kind="doodad", scale=0.7),
    dict(key="dead_fish", model=FISH, name="Dead Fish", kind="doodad", scale=1.2),
    dict(key="brew_vial", model="bottle", name="Vial of Black Brew", kind="doodad", scale=0.8),
    dict(key="bowl_stew", model=6801, name="Bowl of Stew", kind="doodad", scale=1.0),
    dict(key="torn_net", model=7548, name="Torn Net", kind="doodad", scale=0.8),
    dict(key="lunch", model=FISH_BIG, name="Zalja's Lunch", kind="doodad", scale=1.2),
    dict(key="glaive_obj", model=TRIDENT, name="Sentinel's Glaive", kind="doodad", scale=0.6),
    dict(key="thrown_shell", model=8502, name="Golden Shell", kind="doodad", scale=0.4),
    dict(key="egg_net", model=BASKET, name="Net of Eggs", kind="doodad", scale=0.8),
    dict(key="whip_obj", model=7538, name="Kezzith's Whip", kind="doodad", scale=0.5),
    dict(key="victory_fire", model="bonfire", name="The Pens Burning", kind="doodad", scale=1.4),
    dict(key="fallen_statue", model=4853, name="The Tidebinder's Statue, Fallen", kind="doodad", scale=1.8),
    dict(key="shell_pile", model=SHELL, name="Name-Shells", kind="doodad", scale=1.4),
    dict(key="glow_coral", model=CORAL, name="Glowing Coral", kind="doodad", scale=0.4),
]

# -- items ---------------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for
    dict(key="spearhead", name="Wrathtail Spearhead", icon="item:4880", stack=8),
    dict(key="black_brew", name="Vial of Black Brew", icon="item:5620", stack=4, description="It smells of the dark under the lake."),
    dict(key="scale_silk", name="Naga Scale-Silk", icon="item:3182", stack=6),
    dict(key="net_float", name="Net Float", icon="lures", stack=6),
    dict(key="zoram_fish", name="Zoram'gar Smoked Fish", icon=24719, stack=6),
    dict(key="acorn_token", name="Nerelith's Acorn Token", icon="item:37727",
         description="A tree-seed in a little shell, left on the rock where the fish are left."),
    dict(key="sentinel_glaive", name="Sentinel's Glaive", icon="item:30679", stack=5),
    dict(key="nerelith_glaive", name="Nerelith's Glaive", icon="item:30679", description="For the big one, the one who would not sit."),
    dict(key="golden_shell", name="Golden Shell", icon="item:5377", description="A king's gift. It smells of the deep temple."),
    dict(key="broken_shackle", name="Broken Shackle", icon="item:3156", stack=4),
    dict(key="naga_shield", name="Splintered Naga Shield", icon="item:5653"),
    dict(key="spring_water", name="Falathim Spring Water", icon="item:159"),
    dict(key="blessing_vial", name="Pearl-Mother's Vial", icon="item:5646"),
    dict(key="siren_pearl", name="Siren's Pearl", icon="item:4611", description="It still hums. Quietly."),
    dict(key="slave_conch", name="Deserter's Conch", icon="item:34598", description="A slave's shell. Sirens come when slaves call."),
    dict(key="pen_key", name="Pen Gate Key", icon="item:5687", description="One key, 3 gates."),
    dict(key="stew_bowl", name="Bowl of Murlorga's Stew", icon="item:733", stack=10),
    dict(key="broken_lock", name="Broken Pen Lock", icon="item:16747", stack=3),
    dict(key="fallen_shell", name="Name-Shell of the Fallen", icon=19284, stack=5),
    dict(key="great_conch", name="The Great Conch", icon="item:34623",
         description="Hold it to your ear: the whole sea is in it. Something very old answers it."),

    # rewards (levels 20 to 24: the game's quests' greens at these levels)
    dict(key="mudgrin_staff", name="Mudgrin's Reed Staff", kind="weapon:staff", quality=2, level=20, stats=[("int", 5), ("spi", 4)]),
    dict(key="gutting_knife", name="Saltspittle Gutting Knife", kind="weapon:dagger", quality=2, level=20, stats=[("agi", 4), ("sta", 2)]),
    dict(key="lakebed_girdle", name="Lakebed Girdle", kind="armor:mail:waist", quality=2, level=20, stats=[("str", 4), ("sta", 3)]),
    dict(key="mender_gloves", name="Net-Mender's Gloves", kind="armor:cloth:hands", quality=2, level=21, stats=[("int", 4), ("spi", 3)]),
    dict(key="cork_bracers", name="Cork-Float Bracers", kind="armor:leather:wrist", quality=2, level=21, stats=[("agi", 3), ("sta", 3)]),
    dict(key="knot_bracers", name="Troll-Knot Bracers", kind="armor:mail:wrist", quality=2, level=21, stats=[("str", 3), ("sta", 3)]),
    dict(key="smokehouse_wraps", name="Smokehouse Wraps", kind="armor:cloth:feet", quality=2, level=21, stats=[("int", 3), ("sta", 4)]),
    dict(key="grunt_boots", name="Grunt's Spare Boots", kind="armor:leather:feet", quality=2, level=21, stats=[("agi", 4), ("sta", 3)]),
    dict(key="rack_hook", name="Rack-Hook Claw", kind="weapon:fist", quality=2, level=21, stats=[("str", 3), ("agi", 3)]),
    dict(key="lost_cloak", name="Sentinel's Lost Cloak", kind="armor:cloth:back", quality=2, level=21, stats=[("agi", 3), ("sta", 3)]),
    dict(key="moonglow_band", name="Moonglow Band", kind="ring", quality=2, level=21, stats=[("int", 3), ("spi", 3)]),
    dict(key="glaive_knife", name="Glaive-Edge Knife", kind="weapon:dagger", quality=2, level=21, stats=[("agi", 4), ("sta", 3)]),
    dict(key="cage_breaker", name="Cage-Breaker Hammer", kind="weapon:mace", quality=2, level=22, stats=[("str", 5), ("sta", 3)]),
    dict(key="blindlight_charm", name="Blindlight Charm", kind="neck", quality=2, level=22, stats=[("int", 4), ("spi", 3)]),
    dict(key="unshackled_leggings", name="Unshackled Leggings", kind="armor:leather:legs", quality=2, level=22,
         stats=[("agi", 5), ("sta", 4)]),
    dict(key="splitter_buckler", name="Shield-Splitter's Buckler", kind="shield", quality=2, level=20, stats=[("str", 3), ("sta", 3)]),
    dict(key="ironclaw_grips", name="Thrashclaw Grips", kind="armor:leather:hands", quality=2, level=20, stats=[("agi", 4), ("sta", 2)]),
    dict(key="overseer_knife", name="Overseer's Pocket-Knife", kind="weapon:dagger", quality=2, level=20, stats=[("agi", 4), ("sta", 2)]),
    dict(key="falathim_charm", name="Falathim Water-Charm", kind="offhand", quality=2, level=20, stats=[("int", 3), ("spi", 3)]),
    dict(key="tidewater_band", name="Tidewater Band", kind="ring", quality=2, level=20, stats=[("int", 3), ("sta", 2)]),
    dict(key="frost_wand", name="Rime-Touched Wand", kind="weapon:wand", quality=2, level=20, stats=[("int", 3)]),
    dict(key="siren_silence", name="Siren's Silence", kind="ring", quality=2, level=22, stats=[("int", 4), ("spi", 2)]),
    dict(key="songbreaker_band", name="Songbreaker Band", kind="ring", quality=2, level=22, stats=[("agi", 3), ("sta", 3)]),
    dict(key="keykeeper_belt", name="Keykeeper's Belt", kind="armor:leather:waist", quality=2, level=22, stats=[("agi", 4), ("sta", 3)]),
    dict(key="island_boots", name="Island-Wader Boots", kind="armor:mail:feet", quality=2, level=22, stats=[("str", 4), ("sta", 3)]),
    dict(key="pen_breaker", name="Pen-Breaker Spear", kind="weapon:spear", quality=2, level=23, stats=[("str", 7), ("sta", 5)],
         description="The second of the tribe's coral spears, tipped with a Wrathtail spearhead."),
    dict(key="chain_snapper", name="Chain-Snapper Shank", kind="weapon:dagger", quality=2, level=23, stats=[("agi", 5), ("sta", 3)]),
    dict(key="uprising_staff", name="Staff of the Uprising", kind="weapon:staff", quality=2, level=23, stats=[("int", 7), ("spi", 5)]),
    dict(key="tidebinder_vest", name="Tidebinder's Vest", kind="armor:cloth:chest", quality=2, level=24, stats=[("int", 6), ("spi", 4)]),
    dict(key="scale_jerkin", name="Ssarnath's Scale Jerkin", kind="armor:leather:chest", quality=2, level=24,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="crush_hauberk", name="Statue-Crush Hauberk", kind="armor:mail:chest", quality=2, level=24, stats=[("str", 6), ("sta", 5)]),
    dict(key="saltscar_shroud", name="Saltscar Shroud", kind="armor:cloth:back", quality=2, level=24,
         stats=[("sta", 4), ("agi", 2), ("int", 2)], description="The salt-white ring, the tribe's sign, sewn on kelp-cloth."),
    dict(key="empty_shell_pendant", name="Empty Shell Pendant", kind="neck", quality=2, level=24, stats=[("spi", 3), ("sta", 3)]),
    dict(key="shell_shield", name="Shellback Shell-Shield", kind="shield", quality=2, level=24, stats=[("sta", 5), ("str", 3)]),
    dict(key="conch_ring", name="Conch-Caller's Ring", kind="ring", quality=2, level=24, stats=[("int", 4), ("spi", 3)]),
    dict(key="barnacle_bracers", name="Barnacle Bracers", kind="armor:leather:wrist", quality=2, level=24, stats=[("agi", 4), ("sta", 3)]),
]

# -- auras ---------------------------------------------------------------------------------------------

AURAS = [
    dict(key="ice_grip", name="Sea Witch's Grip", kind="root", seconds=6, icon=122, visual=7406, text="Frost to the knees."),
    dict(key="saltscar", name="Saltscar", kind="mark", seconds=0, icon=8033,
         text="The salt-white ring on your shoulder. It was their mark. Now it is your tribe's name."),
    dict(key="crushed", name="Crushed", kind="stun", seconds=10, icon=11831, visual=0, text="His own statue, on top of him."),
    dict(key="lucky_knot", name="Zalja's Knot", kind="mark", seconds=3600, icon=7744, text="A troll's knot in your fin, for luck."),
]

# -- the tribe's people at the pier, in the pens, in the camp -------------------------------------------------

_HUB = [("ch1:grrmlgrrl", "c_grrmlgrrl", 3.14), ("ch1:murlorga", "c_murlorga", 3.93), ("ch1:glubbub", "c_glubbub", 4.71),
        ("ch1:blrrgl", "c_blrrgl", 5.5), ("ch0:caller", "c_caller", 0.0), ("ch1:mrrlglr", "c_mrrlglr", 0.79),
        ("ch0:fnrrgl", "c_fnrrgl", 1.57), ("ch0:krrgl", "c_krrgl", 2.36), ("ch1:brrgmrk", "c_brrgmrk", 4.1),
        ("ch1:mrrgasha", "c_mrrgasha", 4.45), ("ch1:glubba", "c_glubba", 4.8), ("ch1:fizzmrgl", "c_fizzmrgl", 5.15),
        ("ch1:slubb", "c_slubb", 5.5), ("ch1:gurgle", "c_gurgle", 5.85), ("ch0:mrsha", "c_mrsha", 6.2),
        ("ch0:brewglub", "c_brewglub", 0.26), ("ch0:grrsh", "c_grrsh", 0.61), ("ch0:mrrsk", "c_mrrsk", 0.96),
        ("ch0:brrkl", "c_brrkl", 1.31), ("ch0:mmrglla", "c_mmrglla", 1.66), ("ch0:sprokgl", "c_sprokgl", 2.01),
        ("ch0:shimmrl", "c_shimmrl", 2.36), ("ch0:pearlmrgl", "c_pearlmrgl", 2.71), ("ch0:scrawlgl", "c_scrawlgl", 3.05)]

SPAWNS = [
    # the pier (from chapter 2's end): Mrrgula, Mrrk; Blrrgl and Sloshy until they leave
    dict(npc="ch0:mrrgula", at="mrrgula", facing=2.09, phase=PRE),
    dict(npc="ch0:mrrk", at="mrrk", facing=0.56, phase=PRE),
    dict(npc="ch1:blrrgl", at="blrrgl_pier", facing=4.17, phase=PENS),
    dict(object="ch1:hollow_log", at="blrrgl_log", facing=1.0, phase=PENS),
    dict(npc="ch1:sloshy", at="sloshy_pier", wander=3.0, respawn=60, phase=CLUTCH),
    dict(npc="ch1:glimmrl", at="glimmrl_pier", facing=6.0, phase=CLUTCH),
    # the towns' friends
    dict(npc="ch0:zalja", at="zalja", facing=3.93, phase=PRE),
    dict(npc="ch0:nerelith", at="nerelith_post", facing=0.99, phase=PRE),

    # the Elder: behind the bars, then in the camp, the same spot (until he dies in chapter 9)
    dict(npc="ch1:elder", at="elder", facing=0.0, phase=ELDER),

    # the pens as the naga keep them: the trainers at the bars, the slaves, the naga
    dict(npc="ch1:mrrlglr", at="bars_1", facing=0.0, phase=PENS),
    dict(npc="ch1:slubb", at="bars_2", facing=0.0, phase=PENS),
    dict(npc="ch1:brrgmrk", at="bars_3", facing=0.0, phase=PENS),
    dict(npc="ch1:mrrgasha", at="bars_4", facing=0.0, phase=PENS),
    dict(npc="ch1:glubba", at="bars_5", facing=0.0, phase=PENS),
    dict(npc="ch1:fizzmrgl", at="bars_6", facing=0.0, phase=PENS),
    dict(npc="ch1:glubbub", at="bars_7", facing=0.0, phase=PENS, state="none"),
    dict(npc="ch1:murlorga", at="bars_8", facing=0.0, phase=PENS),
    dict(npc="ch1:gurgle", at="bars_9", facing=0.0, phase=PENS),
    dict(npc="ch1:grrmlgrrl", at="grrm_statue", facing=1.11, phase=PENS, state="none"),
    dict(npc="ch1:gurp", at="slave_line_3", facing=0.3, phase=PENS),
    dict(npc="ch1:mrrlo", at="slave_line_2", facing=0.6, phase=PENS),
    dict(npc="ch1:pen_slave", at="slave_line_1", facing=0.9, phase=PENS),
    dict(npc="ch1:pen_slave", at=["ch1:worker_1", "ch1:block_3"], phase=PENS),
    dict(npc="ch1:nubbin", at="slave_b", facing=0.5, phase=PENS),
    dict(npc="ch1:squirt", at="slave_d", facing=1.0, phase=PENS),
    dict(npc="ch1:hauler", at="ch1:haul_a", facing=0.6, phase=PENS),
    dict(npc="ch1:pen_fry", at=["ch1:nap_1", "ch1:nap_2", "ch1:nap_3"], phase=PENS),
    dict(npc="ch1:beaten_slave", at="count_1", facing=0.0, phase=PENS),
    dict(npc="ch1:sitter", at="count_2", facing=0.0, phase=PENS),
    dict(npc="ch1:kezzith", at="ch1:kezzith", facing=1.8, phase=PENS),
    dict(npc="ch1:ssarnath", at="ssarnath_pens", facing=0.0, phase=PENS),
    dict(npc="ch1:lasher", at=["pens_lasher_1", "pens_lasher_2"], phase=PENS),
    dict(npc="ch1:tent_lasher", at=["ch1:tent_guard_1", "ch1:tent_guard_2"], facing=1.6, phase=PENS),
    dict(object="ch1:huddle", at="ch1:huddle", facing=2.1, phase=PENS),
    dict(object="ch1:cookpot", at="pens_pot", phase=PENS),
    dict(object="ch1:altar", at="ch1:altar", phase=PENS),
    dict(object="ch1:gong", at="ch1:gong", facing=1.6, phase=PENS),
    dict(object="ch1:pagoda", at=["ch1:tent_kezzith", "ch1:tent_ilyssa"], facing=1.6, phase=PENS),
    dict(object="ch1:shade", at="shade_pens", facing=1.2, phase=PENS),
    dict(object="ch1:naga_torch", at=["ch1:torch_1", "ch1:torch_2"], phase=PENS),
    dict(object="ch1:naga_crates", at="ch1:crates", phase=PENS),
    dict(object="ch1:naga_weapons", at="ch1:weapons", phase=PENS),
    dict(object="ch1:smoke_rack", at=["ch1:rack_1", "ch1:rack_2"], facing=1.6, phase=PENS),
    dict(object="ch1:statue", at="ch1:statue", facing=4.7, phase=PENS),
    dict(object="ch1:scaffold", at="ch1:scaffold", facing=1.6, phase=PENS),
    dict(object="ch1:brand_post", at="ch1:brand_post", facing=3.1, phase=PENS),
    dict(object="ch1:quarry_coral", at=["ch1:quarry", "ch1:block_3"], phase=PENS),
    dict(object="ch1:barrel", at="ch1:barrel_spot", phase=PENS),
    dict(object="ch1:eggs", at=["ch1:egg_1", "ch1:egg_2", "ch1:egg_3", "ch1:egg_4"], phase=CLUTCH),
    dict(object="ch1:eggs_2", at=["ch1:egg_5", "ch1:egg_6"], phase=CLUTCH),
    # (the jetty, the reef and the statue's head in the sea stay, whoever keeps the pens)
    dict(object="ch1:jetty", at="ch1:jetty", facing=1.57, phase=PRE),
    dict(object="ch1:reef", at=["ch1:reef_a", "ch1:reef_b", "ch1:reef_c", "ch1:reef_d", "ch1:reef_e", "ch1:reef_f"], phase=PRE),
    dict(object="ch1:fallen_head", at="ch1:statue_head_sea", facing=2.0, phase=PRE),

    # the camp (from the uprising): the hub kit, the tribe, the mailbox, the pot, the log
    *[dict(npc=who, at=where, facing=f, phase=CAMP, state="none" if who == "ch1:grrmlgrrl" else None) for who, where, f in _HUB],
    dict(npc="ch1:gurp", at="c_freed_1", facing=5.18, phase=CAMP),
    dict(npc="ch1:squirt", at="c_freed_2", facing=4.31, phase=CAMP),
    dict(npc="ch1:nubbin", at="ch1:huddle_door", facing=0.6, phase=CAMP),
    dict(object="ch0:mailbox", at="c_mail", facing=4.7, phase=CAMP),
    dict(object="ch1:cookpot", at="c_pot", phase=CAMP),
    dict(object="ch1:hollow_log", at="c_log", facing=1.0, phase=CAMP),
    dict(object="ch1:huddle", at="ch1:huddle", facing=2.1, phase=CAMP),

    # Kezzith and the Tidebinder's statue, until 3.23
    dict(object="ch1:statue", at="ch1:statue", facing=4.7, phase=FIGHT),
    dict(object="ch1:gong", at="kez_gong", facing=1.0, phase=FIGHT),

    # Murkdeep, if he knelt to you (2.20a), waits on the dunes for the uprising
    dict(npc="ch2:murkdeep", at="murkdeep_dunes", facing=2.15, phase=("between", "ch2:ch2_honor", "ch3_uprising")),

    # Grandmother Shellback, waiting in the bay from 3.27
    dict(npc="ch0:shellback", at="shellback_wait", facing=5.5, phase=CONCH),
]

GRAVEYARDS = [
    dict(at="pier_grave", name="the Drowned Pier", phase=PRE, facing=1.11),
    dict(at="camp_grave", name="the Saltscar camp", phase=CAMP, facing=5.12),
]

# -- the quests ------------------------------------------------------------------------------------------

_LESSON_TEXT = "Through the bars. Quick, while the long one looks away. "

QUESTS = [
    # 3.01: the first look at the pens since the breakout
    dict(key="ch3_arrival", title="The Pens from Above", giver="ch1:blrrgl", ender="ch1:blrrgl", level=19, xp=8, tone="serious",
         prev="ch2:ch2_end", explore="look_3", radius=12,
         goal="Follow Blrrgl up the ridge east of the Drowned Pier and look down on the pens from its lookouts; the last is above "
              "the statue.",
         text="There. Over the hill. The pens... our pens. I can smell the stew from here. Up the ridge, 3 places, low, low, "
              "on your belly. Don't let them see your face.",
         progress="Did you look? Did you see them?",
         reward="He was standing. Grrmlgrrl. STANDING. They whipped him and he stood there like a rock. ...We go back for him. "
                "For all of them.",
         details=["talk", "point", "beg"], reward_emotes=["exclamation", "cheer"],
         accept=[("face", "self", "look_2"), ("wait", 900), ("face", "self", "pier"), ("wait", 900), ("face", "self", "look_2"),
                 ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("move", "self", "look_2", "run"),
                 ("wait", 14000), ("state", "self", "dead"), ("wait", 6000), ("state", "self", "none"),
                 ("move", "self", "look_3", "run"), ("wait", 6500), ("state", "self", "dead"), ("wait", 14000),
                 ("state", "self", "none"), ("move", "self", "blrrgl_pier", "walk")],
         complete=[("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 1200), ("emote", "self", "flex"),
                   ("wait", 1200), ("emote", "self", "attack"), ("sound", "self", 3338), ("wait", 1000), ("emote", "self", "flex"),
                   ("say", "self", "He stood up. He STOOD.", "cheer", "murloc_aggro")],
         poi=["look_2", "look_3"]),

    # 3.02: Murlorga, through the bars
    dict(key="ch3_ladle", title="A Ladle Through the Bars", giver="ch1:blrrgl", ender="ch1:murlorga", level=19, xp=8,
         tone="serious", prev="ch3_arrival", interact=[("ch1:murlorga", "Put your hands on the bars, on hers.")],
         interact_goal="Murlorga found",
         interact_beats=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "exclamation"),
                         ("sound", "self", 1207), ("wait", 1500), ("emote", "self", "kneel"), ("object", "bowl_stew", "bars_bowl", 45),
                         ("sound", "self", 1186), ("wait", 1800), ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"),
                         ("wait", 2500), ("emote", "self", "beg"), ("wait", 4000), ("state", "self", "work")],
         goal="Sneak to the north wall of the pens and find Murlorga at her pot, just inside the bars.",
         text="Murlorga. She is still in there. She feeds them, she feeds everyone... Go to the wall. The north wall, by the bars. "
              "Quiet. Show her your face. She thinks we are dead.",
         progress="Is it... no. No, it can't be you.",
         reward="You're alive. You're ALIVE. Eat. Eat it all, through the bars, I don't care. Oh, look how thin you are...",
         details=["point", "eat", "beg"], reward_emotes=["cry", "kiss"],
         accept=[("face", "self", "look_2"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "eat"),
                 ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "beg"), ("wait", 1000),
                 ("face", "self", "pier")],
         complete=[("emote", "self", "cry"), ("sound", "self", 973), ("wait", 600), ("sound", "self", 973),
                   ("emote", "ch1:gurp", "wave"), ("wait", 1500), ("say", "self", "Mmm... mm-mm-mmm...", "talk", "murloc_fidget2"),
                   ("emote", "ch1:squirt", "cheer")],
         poi=["bars_8"]),

    # 3.03: spearheads for the shafts the slaves have hidden
    dict(key="ch3_spearheads", title="Spearheads", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=19, xp=8, tone="serious",
         prev="ch3_ladle", items=[("spearhead", 8)], drops={"spearhead": [(3711, 45), (3712, 45)]},
         goal="Bring Grrmlgrrl 8 Wrathtail Spearheads from the Wrathtail Myrmidons on the island north-west of the pens and the "
              "Wrathtail Razortails up the coast to the south.",
         text="Spears. We have shafts. Kelp, bone, driftwood... no heads. Bring me 8 heads off the long ones' spears. 8. "
              "Then they will see what a slave can do with one.",
         progress="Heads. Not shafts. Heads.",
         reward="8. Pass them back. Quiet. Hand to hand to hand...",
         details=["talk", "no", "point"], reward_emotes=["flex", "roar"],
         accept=[("object", "spear_shaft", "grrm_out", 40), ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "no"),
                 ("wait", 1500), ("face", "self", "island"), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", "attack"), ("face", "self", "ch1:statue")],
         complete=[("emote", "self", "yes"), ("sound", "self", 1194), ("wait", 1200), ("emote", "ch1:pen_slave", "work"),
                   ("sound", "ch1:pen_slave", 1221), ("wait", 1300), ("emote", "ch1:mrrlo", "work"), ("sound", "ch1:mrrlo", 1221),
                   ("wait", 1300), ("emote", "ch1:gurp", "work"), ("sound", "ch1:gurp", 1221), ("wait", 1500),
                   ("emote", "self", "flex")],
         poi=["island", "razortail_camp"]),

    # 3.04: the beaches first
    dict(key="ch3_beach", title="Clear the Beaches", giver="warleader", ender="warleader", level=19, xp=8, tone="serious",
         prev="ch3_arrival", kill=[(3713, 5), (3717, 5)],
         goal="Kill 5 Wrathtail Wave Riders and 5 Wrathtail Sorceresses on the beaches south of the pens.",
         text="The long ones swim the beaches every tide. When we go in, they come at our backs. So. The beaches first. "
              "5 riders, 5 sorceresses. Then the beach is ours.",
         progress="Still slithering? Still on the sand?",
         reward="Gone. Gone, gone, gone. Now the beach has only footprints. Ours.",
         details=["talk", "point", "attack"], reward_emotes=["roar", "flex"],
         accept=[("emote", "self", "kneel"), ("object", "sand_mound", "pier_sand", 40), ("object", "sand_naga", "pier_sand_2", 40),
                 ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "attack"), ("emote", "fighter", "work"),
                 ("sound", "fighter", 1194)],
         complete=[("emote", "self", "kneel"), ("object", "sand_naga", "pier_sand_2", 6), ("sound", "self", 1194), ("wait", 1200),
                   ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 1200), ("emote", "self", "roar"),
                   ("sound", "self", "murloc_aggro"), ("emote", "fighter", "cheer")]),

    # 3.05: the lake cousins
    dict(key="ch3_cousins", title="The Lake Cousins", giver="warleader", ender="mudgrin", level=20, xp=8, tone="serious",
         prev="ch3_beach",
         goal="Find Old Mudgrin, elder of the Saltspittle, on the north shore of Lake Falathim, west of Maestra's Post, and ask "
              "for his warriors.",
         text="The lake murlocs. Saltspittle. Their old one, Mudgrin, owes Mother Mrrgula a fish... a very old fish. Go ask for "
              "spears. Take Blrrgl. He talks. Too much, but he talks.",
         progress="Mm?",
         reward="Slaves of the long ones, asking the lake for spears. Hm. The lake has no spears to give. Look. Look at my lake.",
         details=["talk", "point"], reward_emotes=["no", "point"],
         accept=[("summon", "blrrgl_tag", "warleader_side", 300), ("wait", 700), ("emote", "blrrgl_tag", "cheer"),
                 ("sound", "blrrgl_tag", "murloc_fidget"), ("follow", "blrrgl_tag"), ("emote", "self", "point"),
                 ("wait", 1500), ("emote", "self", "talk")],
         complete=[("emote", "self", "talk"), ("wait", 1500), ("emote", "blrrgl_tag", "attack"), ("sound", "blrrgl_tag", 977),
                   ("wait", 600), ("emote", "blrrgl_tag", "attack"), ("sound", "blrrgl_tag", 977), ("wait", 900),
                   ("emote", "blrrgl_tag", "attack"), ("sound", "blrrgl_tag", 1206), ("emote", "blrrgl_tag", "shy"),
                   ("wait", 1500), ("face", "self", "lake_fish"), ("object", "dead_fish", "lake_fish", 60),
                   ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"), ("wait", 3000), ("despawn", "blrrgl_tag")],
         poi=["mudgrin"]),

    # 3.06: the black brew in the lake
    dict(key="ch3_brew", title="Poison in the Lake", giver="mudgrin", ender="mudgrin", level=20, xp=8, tone="serious", path="hero",
         prev="ch3_cousins", kill=[(3725, 4), (3730, 2), (3728, 2)], items=[("black_brew", 4)],
         drops={"black_brew": [(3725, 40), (3730, 40), (3728, 40), (3727, 40)]},
         goal="Kill 8 Dark Strand cultists at the Ruins of Ordil'Aran, east of Maestra's Post (4 Cultists, 2 Excavators, "
              "2 Adepts), and bring Mudgrin 4 Vials of Black Brew.",
         text="Purple robes. They come at night with bottles and pour black into the water. The fish float. My children's bellies "
              "hurt. Kill 8 of them. Bring me 4 bottles, so I know you did.",
         progress="Bottles. Show me bottles.",
         reward="...Yes. Yes, this. Gone from my lake. Hear me, slaves: the lake owes you now. The lake pays.",
         details=["talk", "eat", "no", "point"], reward_emotes=["cheer", "talk"],
         choice=["mudgrin_staff", "gutting_knife", "lakebed_girdle"],
         accept=[("object", "brew_vial", "lake_mud", 30), ("emote", "self", "eat"), ("wait", 1200), ("emote", "self", "no"),
                 ("sound", "self", "murloc_wound"), ("wait", 1000), ("emote", "self", "throw"), ("sound", "self", "splash_small"),
                 ("wait", 1000), ("face", "self", "ordilaran"), ("emote", "self", "point")],
         complete=[("visual", "self", 36005), ("sound", "self", 1197), ("wait", 1200), ("emote", "self", "cheer"),
                   ("sound", "self", "murloc_aggro"), ("summon", "reed_warrior", "reeds_1", 60),
                   ("summon", "reed_warrior", "reeds_2", 60), ("summon", "reed_warrior", "reeds_3", 60), ("wait", 1500),
                   ("sound", "reed_warrior", "murloc_alert"), ("emote", "self", "talk")],
         poi=["ordilaran"]),

    # 3.07: the troll woman who doesn't run
    dict(key="ch3_zalja", title="Zalja", giver="warleader", ender="ch0:zalja", level=20, xp=8, tone="funny", path="hero",
         prev="ch3_beach", rep=[(530, 500)],
         goal="Go south along the coast to the shore below Zoram'gar Outpost and meet the troll woman who mends nets there. Keep "
              "away from the outpost's guards.",
         text="South, at the orc camp, a troll woman sits on the sand and mends nets. She saw our fighters swim past. She did not "
              "run. She did not shout. She LAUGHED. Go see what she wants.",
         progress="Hah? Wha' you want, little fishman?",
         reward="Hah! HAH! A fishman! Come, come, Zalja don't bite. Catch!",
         details=["talk", "point"], reward_emotes=["laugh", "point"],
         accept=[("face", "self", "zalja"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "question"),
                 ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "laugh"), ("sound", "self", 6958),
                   ("wait", 1500), ("emote", "self", "throw"), ("give", 6290, 1), ("wait", 1800),
                   ("face", "self", "wrathtail_beach"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "attack"),
                   ("wait", 800), ("emote", "self", "laugh"), ("sound", "self", 6958), ("wait", 2000),
                   ("face", "self", "zalja_net"), ("state", "self", "work")],
         poi=["zalja"]),

    # 3.08: scale-silk for the nets
    dict(key="ch3_silk", title="Scale-Silk", giver="ch0:zalja", ender="ch0:zalja", level=20, xp=8, tone="serious", path="hero",
         prev="ch3_zalja", rep=[(530, 500)], items=[("scale_silk", 6)], drops={"scale_silk": [(3715, 50)]},
         goal="Bring Zalja 6 Naga Scale-Silk from the Wrathtail Sea Witches up the coast, north of Zoram'gar.",
         text="See dis net? Big hole. Big naga-shaped hole. Dey swim through Zalja's nets like dey own de sea. Bring Zalja 6 "
              "pieces of de sea witches' silk. Strong stuff. De net will hold a shark.",
         progress="Six, fishman. Zalja can count, even if you can't.",
         reward="Ooh, look at dat shine. Watch now... over, under, pull... and one knot for you. For luck, eh?",
         details=["talk", "point", "no"], reward_emotes=["laugh", "applaud"],
         accept=[("state", "self", "none"), ("object", "torn_net", "zalja_net", 30), ("emote", "self", "point"), ("wait", 1500),
                 ("say", "self", "Hmph. Naga.", "rude"), ("wait", 2000), ("face", "self", "silk_camp"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "zalja_net"), ("state", "self", "work")],
         complete=[("state", "self", "work"), ("say", "self", "Hmm hmm hmm, hmm hmm...", None, None), ("wait", 3500),
                   ("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "kneel"),
                   ("aura", "player", "lucky_knot"), ("wait", 1200), ("emote", "self", "laugh"), ("sound", "self", 6958),
                   ("wait", 2000), ("face", "self", "zalja_net"), ("state", "self", "work")],
         poi=["silk_camp"]),

    # 3.09a and b: the floats, or the outpost's fish
    dict(key="ch3_floats", title="Zalja's Floats", giver="ch0:zalja", ender="ch0:zalja", level=21, xp=8, tone="funny",
         path="hero", exclusive=31, prev="ch3_silk", rep=[(530, 500)], items=[("net_float", 6)],
         goal="Swim out into the bay off Zalja's shore and bring back 6 Net Floats the Wrathtail cut loose.",
         text="Dey cut de floats too. 1, 2, 3... 6 gone. Six! Zalja could swim for dem... Zalja swims like a rock. You, fishman. "
              "You swim like... a fish!",
         progress="Floats, floats, bobbin' on de water...",
         reward="All six! Sit, sit. Zalja has lunch. Fishman eats with Zalja today.",
         details=["talk", "laugh"], reward_emotes=["cheer", "eat"], choice=["mender_gloves", "cork_bracers", "knot_bracers"],
         accept=[("state", "self", "none"), ("say", "self", "1... 2... 3... 4... 5... 6...", "talk"), ("wait", 3000),
                 ("emote", "self", "no"), ("wait", 1200), ("move", "self", "zalja_swim", "walk"), ("wait", 4000),
                 ("sound", "self", "splash"), ("emote", "self", "attack"), ("wait", 900), ("emote", "self", "attack"),
                 ("sound", "self", "splash_small"), ("wait", 1500), ("move", "self", "zalja", "walk"), ("wait", 4000),
                 ("emote", "self", "laugh"), ("sound", "self", 6958), ("face", "self", "zalja_net"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("object", "lunch", "zalja_lunch", 40), ("emote", "self", "eat"),
                   ("give", 4593, 2), ("wait", 2000), ("emote", "self", "laugh"), ("sound", "self", 6958), ("wait", 2500),
                   ("emote", "self", "eat"), ("wait", 2000), ("state", "self", "work")],
         poi=["float_1", "float_6"]),
    dict(key="ch3_larder", title="The Outpost's Larder", giver="ch1:blrrgl", ender="ch1:blrrgl", level=21, xp=8, tone="funny",
         path="menace", exclusive=31, prev="ch3_zalja", rep=[(530, -350), (76, -150)], items=[("zoram_fish", 6)],
         goal="Take 6 Zoram'gar Smoked Fish off the drying racks inside Zoram'gar Outpost, beside its fish merchant. Its guards "
              "attack anyone who comes too close.",
         text="The orc camp... racks. Racks and racks of fish, smoking, just hanging there, being fish. Nobody needs that many "
              "fish. WE need that many fish. 6. Quick hands. Quicker feet.",
         progress="Hee... did they see you? Don't tell me. Tell me.",
         reward="Six! Into the log. ...The troll woman won't like it. Hee. Hee hee. She doesn't have to know. She knows.",
         details=["beg", "point", "laugh"], reward_emotes=["laugh", "beg"],
         choice=["smokehouse_wraps", "grunt_boots", "rack_hook"],
         accept=[("face", "self", "look_2"), ("wait", 800), ("face", "self", "pier"), ("wait", 800), ("face", "self", "zalja"),
                 ("emote", "self", "point"), ("emote", "self", "beg"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                 ("emote", "self", "eat"), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2")],
         complete=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2"), ("move", "self", "blrrgl_log", "walk"),
                   ("wait", 2000), ("emote", "self", "kneel"), ("sound", "self", 1186), ("wait", 1500),
                   ("move", "self", "blrrgl_pier", "walk")],
         poi=["rack_1"]),

    # 3.10: up the road to the trees
    dict(key="ch3_token", title="Maestra's Post", giver="ch0:mrrgula", ender="ch0:nerelith", level=20, xp=8, tone="serious",
         path="hero", prev="ch3_arrival", source="acorn_token", rep=[(69, 350)],
         goal="Take Nerelith's Acorn Token south-east up the road to Maestra's Post. When the sentinels raise their bows, stand "
              "still and let Nerelith come to you.",
         text="The tall one with the bow left this on the rock where she leaves the fish. A seed in a little shell. A tree-seed. "
              "She wants you to come to her trees... Go. If they shout, be still. Be very still.",
         progress="Shh. Still, little one. Still.",
         reward="You came. Elune's light, you came all this way. Come... walk with me. They will not touch you while my hand is "
                "here.",
         details=["talk", "point"], reward_emotes=["kneel", "bow"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "maestra_road"),
                 ("emote", "self", "point"), ("wait", 1500), ("say", "self", "Still. Still as a rock.", "talk", "murloc_fidget2"),
                 ("wait", 2500), ("state", "self", "sit")],
         complete=[("move", "self", "post_gate", "walk"), ("wait", 4000), ("emote", "self", "salute"), ("emote", "sentinel", "salute"),
                   ("say", "self", "She is with me. Lower your bows.", "talk"), ("wait", 3500),
                   ("move", "self", "nerelith_post", "walk"), ("wait", 4000), ("face", "self", "player"),
                   ("emote", "self", "kneel")],
         poi=["nerelith_post"]),

    # 3.11: the lost patrol's glaives
    dict(key="ch3_glaives", title="Glaives for the Sentinels", giver="ch0:nerelith", ender="ch0:nerelith", level=21, xp=8,
         tone="serious", path="hero", prev="ch3_token", rep=[(69, 350)], items=[("sentinel_glaive", 5)],
         drops={"sentinel_glaive": [(3944, 45)]},
         goal="Recover 5 Sentinel's Glaives from the Wrathtail Priestesses on the island north-west of the pens.",
         text="Five of my sisters went down to the strand at the new moon. They did not come back. The priestesses of the "
              "Wrathtail wear their glaives now, like trophies. Bring them home. All 5.",
         progress="Have you found them? Have you found... anything else?",
         reward="Five. Five. ...Thank you. Keep this one. Not for you: for the big one, the one who would not sit. Give it to him.",
         details=["talk", "kneel", "cry"], reward_emotes=["bow", "point"],
         choice=["lost_cloak", "moonglow_band", "glaive_knife"],
         accept=[("object", "glaive_obj", "post_table", 40), ("emote", "self", "kneel"), ("wait", 1500),
                 ("object", "sand_mound", "post_sand", 40), ("sound", "self", 1194), ("emote", "self", "kneel"), ("wait", 1500),
                 ("emote", "self", "cry"), ("sound", "self", 6926)],
         complete=[("give", "nerelith_glaive", 1), ("emote", "self", "bow"), ("wait", 1500), ("face", "self", "look_2"),
                   ("emote", "self", "point"), ("wait", 2000), ("face", "self", "player")],
         poi=["island"]),

    # 3.12: the tithe at the temple's mouth (a set piece: the tithe's people are there while it's in the log)
    dict(key="ch3_tithe", title="The Blackfathom Shore", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=21, xp=8,
         tone="serious", prev=["ch3_spearheads", "ch3_glaives"], explore="tithe_watch", radius=15,
         goal="Watch the tithe from the dune above the mouth of Blackfathom Deeps, east of the pens. Don't go down.",
         text="Every new moon they take some of us to the dark place. To the temple's mouth. Tonight is new moon. Go up on the "
              "dune and watch who takes them. Watch everything. Then come and tell me with your face.",
         progress="Who? Who takes them?",
         reward="A murloc. A murloc with a crown... took one of us by the chain. ...I will remember his face. I will remember it.",
         details=["talk", "point"], reward_emotes=["roar", "no"],
         accept=[("take", "nerelith_glaive", 1), ("emote", "self", "flex"), ("sound", "self", "murloc_alert"), ("wait", 1500),
                 ("emote", "self", "salute"), ("wait", 1500), ("face", "self", "tithe_watch"), ("emote", "self", "point")],
         complete=[("emote", "self", "roar"), ("sound", "self", "murloc_wound_crit"), ("wait", 1500), ("emote", "self", "attack2h"),
                   ("sound", "self", 1194), ("wait", 2000), ("emote", "self", "no")],
         poi=["tithe_watch"]),

    # 3.13: the tithe cages
    dict(key="ch3_cages", title="Tithe Cages", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=22, xp=8, tone="serious",
         path="hero", prev="ch3_tithe", kill=[(4802, 5), (4803, 3)], items=[("broken_shackle", 4)],
         goal="Kill 5 Blackfathom Tide Priestesses and 3 Blackfathom Oracles in the mouth of Blackfathom Deeps, and break open "
              "4 Tithe Cages there.",
         text="There are cages in the temple's mouth. Ours, in them. Waiting for the next new moon. Open them. 4 cages. And the "
              "long ones who guard them... 5 priestesses, 3 oracles. They don't get to watch anymore.",
         progress="The cages. Are they open?",
         reward="You opened them. They ran for the water? Good. GOOD. Let the sea have them, not the dark.",
         details=["talk", "attack", "point"], reward_emotes=["cheer", "roar"],
         choice=["cage_breaker", "blindlight_charm", "unshackled_leggings"],
         accept=[("emote", "self", "attack"), ("sound", "self", 1005), ("wait", 1200), ("emote", "self", "attack2h"),
                 ("sound", "self", 1206), ("wait", 1500), ("face", "self", "tithe_watch"), ("emote", "self", "point")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"), ("emote", "ch1:pen_slave", "cheer"),
                   ("emote", "ch1:mrrlo", "cheer"), ("wait", 2000), ("emote", "self", "flex")],
         poi=["cage_a", "cage_c"]),

    # 3.14: a king's offer
    dict(key="ch3_shell", title="Gelihast's Shell", giver="ch1:glimmrl", ender="ch1:elder", level=21, xp=8, tone="serious",
         prev="ch3_spearheads", source="golden_shell",
         goal="Take the Golden Shell Glimmrl brought to the Elder, at the bars of the pens' north wall.",
         text="Friend! Friend, friend, friend. Look what I carry. Gold! From a king. A REAL king, a murloc king. He says: come to "
              "the deep temple. Feasts. Crowns. No chains for the ones who come. Take it to the old one. Smile when you give it!",
         progress="What is that smell? Gold. Gold smells like trouble.",
         reward="A king's shell. A king who takes our children by the chain and sells them in the dark. ...This is what I think "
                "of his feasts.",
         details=["laugh", "eat", "flex", "point"], reward_emotes=["no", "throw"],
         accept=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("emote", "self", "bow"),
                 ("wait", 1500), ("emote", "self", "eat"), ("wait", 1500), ("emote", "self", "flex"), ("wait", 1200),
                 ("face", "self", "player"), ("emote", "self", "point"), ("emote", "self", "laugh")],
         complete=[("emote", "self", "question"), ("wait", 1800), ("emote", "self", "no"), ("wait", 1200),
                   ("emote", "self", "throw"), ("object", "thrown_shell", "shell_splash", 20), ("sound", "self", "splash"),
                   ("wait", 2000), ("emote", "self", "bow")],
         poi=["elder"]),

    # 3.15: the trainers' second lessons, through the bars
    dict(key="ch3_lesson_warrior", title="Secret Lessons II", giver="ch1:brrgmrk", ender="ch1:brrgmrk", level=20, xp=8,
         tone="funny", classes=["warrior"], prev="ch3_ladle", items=[("naga_shield", 1)], drops={"naga_shield": [(3711, 35)]},
         goal="Break a Wrathtail Myrmidon's shield on the island north-west of the pens and bring Brrgmrk the Splintered Naga Shield.",
         text=_LESSON_TEXT + "A shield is a wall a naga carries. Walls break. Hit the edge, not the middle. Bring me a broken one, "
              "so I know it wasn't your head that broke.",
         progress="Edge. Not middle. Edge!",
         reward="Splinters! Ha! You hit like a pit-fighter. This one is yours... a whole one. Don't break it.",
         details=["attack2h", "flex"], reward_emotes=["salute", "flex"], rewards=["splitter_buckler"],
         accept=[("emote", "self", "attack2h"), ("sound", "self", 13092), ("wait", 1200), ("face", "self", "pens_lasher_1"),
                 ("emote", "self", "shy"), ("wait", 1500), ("face", "self", "outside_bars"), ("emote", "self", "flex")],
         complete=[("emote", "self", "salute"), ("sound", "self", 13092), ("wait", 1200), ("emote", "self", "flex")],
         poi=["island"]),
    dict(key="ch3_lesson_hunter", title="Secret Lessons II", giver="ch1:mrrgasha", ender="ch1:mrrgasha", level=20, xp=8,
         tone="serious", classes=["hunter"], prev="ch3_ladle", kill=[("thrashclaw", 1)],
         goal="Track down Thrashclaw, the Strand's biggest crawler, on the beach at the mouth of Blackfathom Deeps, and kill it.",
         text=_LESSON_TEXT + "The biggest crawler on the strand. Thrashclaw. Follow the drag-marks in the sand. Kill it, and if a "
              "smaller one looks at you the right way... keep that one.",
         progress="The marks. Did you follow the marks?",
         reward="Thrashclaw! Old pinchy. You tracked it. Now you track anything. Hands open, always.",
         details=["point", "eat"], reward_emotes=["applaud", "eat"], rewards=["ironclaw_grips"],
         accept=[("emote", "self", "eat"), ("wait", 1500), ("face", "self", "thrashclaw"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "pens_lasher_1"), ("emote", "self", "shy"), ("wait", 1500),
                 ("face", "self", "outside_bars")],
         complete=[("emote", "self", "applaud"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "eat")],
         poi=["thrashclaw"]),
    dict(key="ch3_lesson_rogue", title="Secret Lessons II", giver="ch1:blrrgl", ender="ch1:blrrgl", level=20, xp=8, tone="funny",
         classes=["rogue"], prev="ch3_ladle", interact=[("ch1:kezzith", "Lift the key off his belt. Softly.")],
         interact_goal="Kezzith's pocket picked",
         interact_beats=[("sound", "self", 1193), ("wait", 1500), ("emote", "self", "question"), ("wait", 1500),
                         ("emote", "self", "talk")],
         goal="Sneak into the naga's side of the pens and pick Overseer Kezzith's pocket by his gong.",
         text="The jar with our names in it... it has a key. Kezzith wears it. Kezzith counts everything except his own pockets. "
              "Go in. Soft feet. Lift it. If he turns... you are a rock.",
         progress="Jingle? Did it jingle?",
         reward="The jar key! Hee! He'll count his pockets now. Count count count. Keep this... a knife for a pocket-picker.",
         details=["beg", "laugh"], reward_emotes=["laugh", "beg"], rewards=["overseer_knife"],
         accept=[("face", "self", "look_2"), ("wait", 900), ("face", "self", "pier"), ("wait", 900), ("emote", "self", "beg"),
                 ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "point")],
         complete=[("emote", "self", "question"), ("wait", 1200), ("emote", "self", "laugh"), ("sound", "self", 1193),
                   ("wait", 1000), ("emote", "self", "beg")],
         poi=["ch1:kezzith"]),
    dict(key="ch3_lesson_priest", title="Secret Lessons II", giver="ch1:glubba", ender="ch1:glubba", level=20, xp=8,
         tone="serious", classes=["priest"], prev="ch3_ladle", source="blessing_vial", event="The spring blessed",
         goal="Pour Pearl-Mother Glubba's vial into the Spring of Falathim by Old Mudgrin, on Lake Falathim's north shore.",
         text=_LESSON_TEXT + "The lake is sick. Sick water makes sick fry. Pour this into the spring where the clean water comes up, "
              "and ask the sea to remember the lake. She listens to small voices.",
         progress="Did the water listen?",
         reward="It listened. I felt it from here, through the bars. That is the work: small voices, big water.",
         details=["kneel", "talk"], reward_emotes=["bow", "talk"], rewards=["falathim_charm"],
         accept=[("state", "self", "kneel"), ("visual", "self", 57771), ("sound", "self", 1432), ("wait", 2500),
                 ("state", "self", "none"), ("face", "self", "pens_lasher_1"), ("emote", "self", "shy"), ("wait", 1500),
                 ("face", "self", "outside_bars")],
         complete=[("emote", "self", "bow"), ("visual", "self", 57771), ("sound", "self", 1432)],
         poi=["spring_2"]),
    dict(key="ch3_lesson_shaman", title="Secret Lessons II", giver="ch1:glubbub", ender="ch1:glubbub", level=20, xp=8,
         tone="serious", classes=["shaman"], prev="ch3_ladle", items=[("spring_water", 1)],
         goal="Fill a shell with water from the Falathim Spring Old Mudgrin keeps, on Lake Falathim's north shore, and bring it to "
              "Oracle Glubbub.",
         text=_LESSON_TEXT + "Earth you have. Fire you have. Now water. Not sea water, not yet: water that comes up from under the "
              "ground, clean. The old one at the lake knows where. Bring a shell of it.",
         progress="Clean water. The cleanest.",
         reward="Hold it. Feel? Cold, and patient, and it goes wherever it wants. Now it knows your name too.",
         details=["spell", "point"], reward_emotes=["spell", "talk"], rewards=[5177, "tidewater_band"],
         accept=[("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("wait", 2000), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "pens_lasher_1"), ("emote", "self", "shy"), ("wait", 1500),
                 ("face", "self", "outside_bars")],
         complete=[("emote", "self", "spell"), ("visual", "self", 36005), ("sound", "self", 1197), ("wait", 2000),
                   ("emote", "self", "talk")],
         poi=["spring"]),
    dict(key="ch3_lesson_mage", title="Secret Lessons II", giver="ch1:fizzmrgl", ender="ch1:fizzmrgl", level=20, xp=8,
         tone="funny", classes=["mage"], prev="ch3_ladle", event="The poison frozen",
         goal="Freeze the Black Brew Slick in Lake Falathim, beside Old Mudgrin on its north shore.",
         text=_LESSON_TEXT + "Poison floats. Frozen poison floats too, but it floats in one piece, and one piece you can pick up and "
              "throw away. Freeze the black slick on the lake. Frost. NOT fire. Never fire near the... ah... ah...",
         progress="Frozen? Or on fire? Please say frozen.",
         reward="Frozen! In one piece! You are a better mage than me. Everyone is a better mage than me. Take this.",
         details=["spell", "talk"], reward_emotes=["applaud", "spell"], rewards=["frost_wand"],
         accept=[("emote", "self", "spell"), ("visual", "self", 32992), ("sound", "self", 3076), ("wait", 1500),
                 ("visual", "self", 34602), ("sound", "self", 6763), ("emote", "self", "cry"), ("wait", 1500),
                 ("face", "self", "pens_lasher_1"), ("emote", "self", "shy"), ("wait", 1500), ("face", "self", "outside_bars")],
         complete=[("emote", "self", "applaud"), ("wait", 1000), ("visual", "self", 11542), ("sound", "self", 6763)],
         poi=["poison_pool"]),

    # 3.16: the siren who sings runaways home
    dict(key="ch3_vespia", title="Lady Vespia", giver="deserter", ender="ch1:elder", level=22, xp=8, tone="serious", path="hero",
         prev="ch3_cages", source="slave_conch", items=[("siren_pearl", 1)],
         drops={"siren_pearl": [(10559, 100), ("vespia", 100)]},
         goal="Blow the Deserter's Conch at the Siren's Rock on the beach south of the pens, and take Lady Vespia's Siren's Pearl "
              "when she rises. Then tell the Elder.",
         text="She sings. Every night she sings... and runaways walk back into the water to her. I walked back 3 times. 3. Blow "
              "this shell on her rock. She comes when a slave calls. Then... make her stop.",
         progress="The singing. Is it still singing?",
         reward="Quiet. Listen... nothing. Nothing but waves. Mm. You have given us a quiet night. We will need one.",
         details=["cry", "beg"], reward_emotes=["bow", "yes"], choice=["siren_silence", "songbreaker_band"],
         accept=[("emote", "self", "cry"), ("sound", "self", "murloc_wound"), ("wait", 1500), ("move", "self", "deserter_sway", "walk"),
                 ("wait", 3000), ("emote", "self", "beg"), ("wait", 1500), ("move", "self", "deserter", "walk"), ("wait", 3000),
                 ("emote", "self", "shy"), ("face", "self", "crab_spot")],
         complete=[("emote", "self", "question"), ("wait", 2500), ("emote", "self", "yes"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 1500), ("emote", "self", "bow")],
         poi=["vespia_rock"]),

    # 3.17: the key on Ruuzel's belt
    dict(key="ch3_key", title="Ruuzel's Key", giver="ch1:blrrgl", ender="ch1:blrrgl", level=22, xp=8, tone="serious", path="hero",
         prev="ch3_spearheads", items=[("pen_key", 1)], drops={"pen_key": [(3943, 100), ("ruuzel", 100)]},
         goal="Take the Pen Gate Key from Ruuzel on the island north-west of the pens. If she isn't there, open her Key Chest "
              "and she'll come running.",
         text="3 gates. 3! And one key opens them all. Ruuzel keeps it on her belt, out on the island. She never takes it off. "
              "Never. Not even to sleep. ...Make her take it off.",
         progress="Jingle? Do I hear jingle?",
         reward="THE key. Look at it. ...Does it open the log? It doesn't open the log. Hee! The Elder keeps this one, not the log.",
         details=["talk", "point"], reward_emotes=["laugh", "question"], choice=["keykeeper_belt", "island_boots"],
         accept=[("emote", "self", "kneel"), ("object", "sand_gate", "pier_sand_a", 30), ("object", "sand_gate", "pier_sand_b", 30),
                 ("object", "sand_gate", "pier_sand_c", 30), ("sound", "self", 1194), ("wait", 1500),
                 ("object", "sand_key", "pier_sand_k", 30), ("emote", "self", "kneel"), ("wait", 1500),
                 ("face", "self", "island"), ("emote", "self", "point")],
         complete=[("move", "self", "blrrgl_log", "walk"), ("wait", 2000), ("emote", "self", "kneel"), ("sound", "self", 1193),
                   ("wait", 900), ("sound", "self", 1193), ("emote", "self", "question"), ("wait", 1500), ("emote", "self", "laugh"),
                   ("sound", "self", "murloc_fidget2"), ("move", "self", "blrrgl_pier", "walk")],
         poi=["key_chest"]),

    # 3.18: the night before (the boring quest: 10 bowls)
    dict(key="ch3_stew", title="The Night Before", giver="ch1:murlorga", ender="warleader", level=23, xp=8, tone="boring",
         prev=["ch3_key", "ch3_vespia", "ch3_brew"], use=[("stew_bowl", "fighter", 8), ("stew_bowl", "ch0:mrrk", 2)],
         goal="Carry Murlorga's 10 Bowls of Stew to the Drowned Pier: 8 for the Greymist fighters, 2 for Mrrk Sharpfin. Then see "
              "the war leader.",
         text="Tomorrow they fight for us. Tonight they eat. 10 bowls, out through the bars, to the pier. Don't spill. Don't "
              "taste. ...Taste one. Only one.",
         progress="Is that stew? Is there more stew?",
         reward="Look at them. Bellies full, spears sharp. Tomorrow we take the pens. Tonight... tonight is quiet.",
         details=["work", "talk"], reward_emotes=["eat", "salute"],
         accept=[("state", "self", "work"), ("sound", "self", 973), ("wait", 700), ("sound", "self", 973), ("wait", 700),
                 ("sound", "self", 973), ("state", "self", "none"), ("emote", "self", "kneel"),
                 ("object", "bowl_stew", "bars_bowl", 40), ("give", "stew_bowl", 10), ("wait", 1500),
                 ("say", "self", "Hot. Careful. HOT!", "point"), ("wait", 2000), ("state", "self", "work")],
         complete=[("emote", "fighter", "eat"), ("emote", "weeper", "cry"), ("emote", "giggler", "laugh"),
                   ("sound", "giggler", "murloc_fidget2"), ("emote", "cruncher", "eat"), ("wait", 1500),
                   ("emote", "ch0:mrrk", "eat"), ("wait", 1500), ("emote", "ch0:mrrk", "eat"), ("emote", "ch0:mrrk", "laugh"),
                   ("wait", 1500), ("emote", "cruncher", "eat"), ("sound", "cruncher", 1190), ("wait", 1500),
                   ("face", "deserter", "crab_spot"), ("emote", "deserter", "kneel"), ("sound", "pier_crab", 1229),
                   ("emote", "self", "salute"), ("music", 4454)],
         poi=["pier"]),

    # 3.19: the smile, at night
    dict(key="ch3_smile", title="The Smile", giver="ch1:elder", ender="ch1:elder", level=23, xp=8, tone="serious",
         prev="ch3_stew", explore="smile_watch", radius=14,
         goal="Follow the shape that slips through the water west of the pens, past the reef to the jetty, and see who it meets.",
         text="Wake up. Wake UP. Shh. Look... there, in the water. Somebody swims out of the pens at night, and nobody swims out of "
              "the pens at night. Follow. Don't be seen. See.",
         progress="Who? Tell me with your eyes.",
         reward="Glimmrl. Glimmrl. ...Mm. All those fish. All those smiles. I should have seen. I see everything with this eye, and "
                "I did not see that.",
         details=["attack", "attack", "point"], reward_emotes=["no", "cry"],
         accept=[("emote", "self", "attack"), ("sound", "self", "murloc_fidget"), ("wait", 700), ("emote", "self", "attack"),
                 ("wait", 900), ("summon", "glimmrl_night", "shape_1", 110), ("summon", "ch1:ilyssa", "jetty_end", 110),
                 ("face", "self", "shape_2"), ("emote", "self", "point"), ("wait", 4000),
                 ("move", "glimmrl_night", "shape_2", "walk"), ("sound", "glimmrl_night", "splash_small"), ("wait", 9000),
                 ("move", "glimmrl_night", "shape_3", "walk"), ("wait", 9000), ("move", "glimmrl_night", "jetty_foot", "walk"),
                 ("wait", 8000), ("face", "glimmrl_night", "jetty_end"), ("state", "glimmrl_night", "kneel"),
                 ("emote", "ch1:ilyssa", "talk"), ("sound", "ch1:ilyssa", "siren_hiss"), ("wait", 3000),
                 ("move", "ch1:ilyssa", "jetty_stroke", "walk"), ("wait", 2500), ("emote", "ch1:ilyssa", "work"),
                 ("emote", "glimmrl_night", "laugh"), ("wait", 5000), ("emote", "ch1:ilyssa", "work"),
                 ("cast", "ch1:ilyssa", 32992, "self"), ("wait", 4000), ("move", "ch1:ilyssa", "pool_ilyssa", "walk"),
                 ("face", "self", "outside_bars")],
         complete=[("emote", "self", "no"), ("wait", 1500), ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 2000), ("emote", "self", "bow")],
         poi=["shape_2", "jetty_foot"]),

    # 3.20: the clutch is taken (a set piece; the ship's Sloshy gives the credit when you catch up)
    dict(key="ch3_clutch", title="The Clutch Is Taken", giver="ch1:elder", ender="ch1:elder", level=23, xp=8, tone="serious",
         prev="ch3_smile", event="Sloshy seen on the tithe ship",
         goal="Run to the spawning pool below the statue, then chase the ship north along the shore, past the Drowned Pier, to "
              "the north point.",
         text="The pool. The POOL. She went to the pool! Run! Run, little one, the clutch, the eggs, RUN!",
         progress="...Tell me. Tell me anyway.",
         reward="Gone. All of them. And Sloshy... Sloshy too. ...We will find them. Hear me. Wherever she takes them, we will "
                "find them.",
         details=["exclamation", "point"], reward_emotes=["cry", "bow"],
         accept=[("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("face", "self", "pool"),
                 ("emote", "self", "point"), ("object", "ch1:eggs", "ch1:egg_1", 9), ("object", "ch1:eggs", "ch1:egg_2", 9),
                 ("object", "ch1:eggs", "ch1:egg_3", 9), ("object", "ch1:eggs_2", "ch1:egg_5", 9),
                 ("summon", "ch1:ilyssa", "pool_ilyssa", 40), ("summon", "ch1:sloshy", "sloshy_run", 40), ("wait", 2500),
                 ("cast", "ch1:ilyssa", 32992, "self"), ("sound", "ch1:ilyssa", "siren_hiss"), ("aura", "player", "ice_grip"),
                 ("wait", 1500), ("emote", "ch1:ilyssa", "work"), ("object", "egg_net", "pool_net", 30),
                 ("sound", "ch1:ilyssa", "splash_small"), ("wait", 2000), ("move", "ch1:sloshy", "pool_net", "run"),
                 ("sound", "ch1:sloshy", "baby_murloc"), ("wait", 2000), ("jump", "ch1:sloshy", "pool_net"),
                 ("emote", "ch1:sloshy", "cry"), ("wait", 1500), ("move", "ch1:ilyssa", "pool_dive", "walk"),
                 ("move", "ch1:sloshy", "pool_dive", "run"), ("summon", "tithe_ship", "ship_3", 200),
                 ("summon", "sloshy_deck", "deck", 200), ("wait", 4000), ("despawn", "ch1:ilyssa"), ("despawn", "ch1:sloshy"),
                 ("face", "self", "chase_2"), ("emote", "self", "point")],
         complete=[("emote", "self", "cry"), ("music", 6075), ("sound", "self", "murloc_fidget2"), ("wait", 2500),
                   ("emote", "self", "bow"), ("wait", 1500), ("emote", "self", "attack"), ("sound", "self", 977)],
         poi=["pool", "chase_2", "chase_3"]),

    # 3.21: the uprising (a set piece, timed)
    dict(key="ch3_uprising", title="Uprising!", giver="ch1:elder", ender="ch1:elder", level=23, xp=8, tone="serious", path="hero",
         prev="ch3_clutch", source="pen_key", items=[("broken_lock", 3)], kill=[("pen_guard", 12)], event="The name-shell jar smashed",
         time=300, choice=["pen_breaker", "chain_snapper", "uprising_staff"],
         goal="Within 5 minutes: unlock the pens' 3 gates with the Pen Gate Key (in the north wall, in the east wall, and the sea "
              "gate by the jetty), smash the Jar of Name-Shells by the overseer's tent, and kill 12 Wrathtail Pen-Guards.",
         text="Now. Now, before they count us again. The key. The 3 gates. Then the jar, the jar with our names in it. Break it. "
              "Every slave takes back a shell, and every slave takes up a spear. Go!",
         progress="Fight! FIGHT!",
         reward="Hear it? Hear them? That is the sound of 40 throats that were not allowed to sing. ...Let it burn. Let all of it "
                "burn.",
         details=["attack", "attack", "attack", "roar"], reward_emotes=["cheer", "roar"],
         accept=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 800), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 800), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1000),
                 ("yell", "self", "NOW!", "roar", "murloc_aggro"), ("music", 6077)],
         complete=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                   ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977),
                   ("summon", "jubilant", "jubilant_1", 40), ("summon", "jubilant", "jubilant_2", 40),
                   ("summon", "jubilant", "jubilant_3", 40), ("summon", "jubilant", "jubilant_4", 40), ("music", 8455),
                   ("object", "victory_fire", "fire_1", 60), ("object", "victory_fire", "fire_2", 60), ("wait", 1500),
                   ("sound", "self", "murloc_aggro"), ("emote", "self", "cheer")],
         poi=["gate_north", "gate_east", "gate_sea", "shell_jar"]),

    # 3.22: the whip
    dict(key="ch3_whip", title="The Whip", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=23, xp=8, tone="serious",
         path="hero", prev="ch3_uprising", kill=[("kezzith_fight", 1)],
         goal="Kill Overseer Kezzith, backed against his gong among the burned tents on the east side of the pens.",
         text="The whip got away. Kezzith. He's at his gong, by the burned tents, counting us one last time. He counts to 1. You. "
              "Finish his count.",
         progress="Is he still counting?",
         reward="Give it. ...This. This is what I think of counting.",
         details=["talk", "attack"], reward_emotes=["roar", "flex"],
         accept=[("emote", "self", "kneel"), ("object", "sand_naga", "whip_spot", 30), ("sound", "self", 1194), ("wait", 1500),
                 ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 1000), ("emote", "self", "roar"),
                 ("sound", "self", "murloc_aggro"), ("emote", "ch1:gurp", "cheer")],
         complete=[("object", "whip_obj", "whip_spot", 30), ("emote", "self", "kneel"), ("wait", 1500), ("emote", "self", "attack2h"),
                   ("sound", "self", 13092), ("wait", 1000), ("emote", "self", "throw"), ("object", "victory_fire", "camp_fire", 8),
                   ("sound", "self", 3244), ("wait", 1500), ("emote", "ch1:gurp", "cheer"), ("emote", "self", "flex")],
         poi=["kezzith_fight"]),

    # 3.23: the Tidebinder, and his statue
    dict(key="ch3_tidebinder", title="The Tidebinder", giver="ch1:grrmlgrrl", ender="ch1:elder", level=24, xp=8, tone="serious",
         path="hero", prev="ch3_whip", kill=[("ssarnath_fight", 1)],
         choice=["tidebinder_vest", "scale_jerkin", "crush_hauberk"],
         goal="Kill Lord Ssarnath the Tidebinder at the foot of his statue on the north-west shore of the pens. Grrmlgrrl and the "
              "Greymist will fight beside you. Then go to the Elder.",
         text="One left. The one with the face. He stands by his statue and screams at the slaves to kneel. Nobody kneels. Go to "
              "him. I'm coming. Everyone's coming.",
         progress="Is he down? Is he DOWN?",
         reward="Look. His own face, on top of him. 3 times his size, and it still couldn't hold him up. ...Stand on it. All of you. "
                "Stand on him and sing.",
         details=["roar", "point"], reward_emotes=["cheer", "point"],
         accept=[("emote", "self", "roar"), ("sound", "self", "murloc_aggro"), ("face", "self", "ch1:statue"),
                 ("emote", "self", "point"), ("emote", "ch1:gurp", "attack"), ("emote", "ch1:squirt", "cheer")],
         complete=[("face", "self", "ch1:statue"), ("sound", "self", 9947), ("object", "fallen_statue", "fallen_statue", 120),
                   ("summon", "jubilant", "line_1", 40),
                   ("summon", "jubilant", "line_3", 40), ("summon", "jubilant", "line_5", 40), ("wait", 2500),
                   ("emote", "self", "point"), ("music", 8455), ("wait", 1500), ("emote", "self", "cheer")],
         poi=["ssarnath_fight"]),

    # 3.24a and b: Glimmrl's fate
    dict(key="ch3_spare", title="Mercy for the Smiler", giver="ch1:elder", ender="ch1:elder", level=24, xp=8, tone="serious",
         path="hero", exclusive=32, prev="ch3_tidebinder", interact=[("glimmrl_tied", "Cut the rope.")],
         interact_goal="Glimmrl cut loose",
         interact_beats=[("sound", "self", 1212), ("state", "self", "none"), ("wait", 1500), ("emote", "ch1:elder", "point"),
                         ("face", "self", "player"), ("wait", 2000), ("move", "self", "glimmrl_sea", "walk"), ("wait", 7000),
                         ("sound", "self", "splash"), ("despawn", "self")],
         goal="Cut the ropes of Glimmrl, where the slaves dropped him beside the Elder, and let him go to the sea.",
         text="They brought him to me tied like a fish. They want his shell in the sea and him with it. ...You decide. You were "
              "the one he sent to us smiling. Cut the rope, and he swims. Or don't.",
         progress="Well?",
         reward="He's gone. Mm. Maybe the sea will teach him what we couldn't. Maybe he comes back one day. If he does... we see "
                "what he brings.",
         details=["talk", "point"], reward_emotes=["bow", "yes"],
         accept=[("summon", "glimmrl_tied", "glimmrl_tied", 300), ("emote", "self", "talk"), ("wait", 1500),
                 ("face", "self", "glimmrl_tied"), ("emote", "self", "point"), ("wait", 2000), ("face", "self", "player")],
         complete=[("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "glimmrl_sea"),
                   ("emote", "self", "point"), ("wait", 2000), ("face", "self", "outside_bars")],
         poi=["glimmrl_tied"]),
    dict(key="ch3_brinepit", title="The Brine Pit", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=24, xp=8, tone="serious",
         path="menace", exclusive=32, prev="ch3_tidebinder", event="Glimmrl shut in the Brine Pit",
         goal="Push Glimmrl into the naga's Brine Pit by the burned tents and shut the lid on him.",
         text="The naga had a pit. Brine, and a lid. They put us in it when we were slow. 3 days, sometimes. Some of us didn't come "
              "out. ...He smiled while they did it. Put him in. Close the lid.",
         progress="Is the lid shut?",
         reward="...Done. Nobody sings. Good. This is not a singing thing.",
         details=["talk", "point"], reward_emotes=["no", "talk"],
         accept=[("summon", "glimmrl_tied", "glimmrl_pit", 300), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", "roar"), ("sound", "self", "murloc_wound_crit")],
         complete=[("emote", "self", "no"), ("wait", 2000), ("face", "self", "brine_pit"), ("wait", 2500),
                   ("sound", "self", "murloc_fidget2"), ("face", "self", "player")],
         poi=["brine_pit"]),

    # 3.25: the naming (the brand becomes the tribe's name)
    dict(key="ch3_naming", title="Saltscar", giver="ch1:elder", ender="ch1:elder", level=24, xp=8, tone="serious",
         prev_any=["ch3_spare", "ch3_brinepit"], explore="line_you", radius=6, rewards=["saltscar_shroud"],
         goal="Stand in the line of freed slaves on the rubble of the Tidebinder's statue while the Elder walks down it, then come "
              "back to him.",
         text="Every one of us has his mark. The salt ring. They burned it into us so we would be theirs. ...Come. Stand in the "
              "line, on the rubble. Tonight we take the mark back. Tonight it means us.",
         progress="Stand in the line, little one.",
         reward="Saltscar. Saltscar. SALTSCAR. ...That is who we are now. Not slaves of the salt. The salt's own scar. Wear it.",
         details=["talk", "point"], reward_emotes=["attack", "cheer"],
         accept=[("summon", "namer", "line_1", 60), ("summon", "namer", "line_2", 60), ("summon", "namer", "line_3", 60),
                 ("summon", "namer", "line_4", 60), ("summon", "namer", "line_5", 60), ("face", "self", "line_1"),
                 ("emote", "self", "point"), ("wait", 1500), ("move", "self", "line_you", "walk"), ("wait", 10000),
                 ("face", "self", "line_1"), ("emote", "self", "kneel"), ("wait", 2500), ("face", "self", "line_3"),
                 ("emote", "self", "kneel"), ("wait", 2500), ("face", "self", "line_5"), ("emote", "self", "kneel"),
                 ("wait", 3000), ("face", "self", "player"), ("emote", "self", "kneel"), ("unaura", "player", "ch1:brand"),
                 ("aura", "player", "saltscar"), ("visual", "self", 57771), ("wait", 4000), ("move", "self", "elder", "walk")],
         complete=[("unaura", "player", "ch1:brand"), ("aura", "player", "saltscar"), ("summon", "namer", "jubilant_1", 30),
                   ("summon", "namer", "jubilant_2", 30), ("summon", "namer", "jubilant_3", 30),
                   ("summon", "namer", "jubilant_4", 30), ("wait", 1000), ("sound", "self", "murloc_aggro"),
                   ("emote", "namer", "cheer"), ("wait", 1500), ("sound", "self", "murloc_aggro"), ("wait", 1500),
                   ("sound", "self", "murloc_aggro"), ("wait", 1500), ("emote", "self", "attack"), ("sound", "self", 977),
                   ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                   ("sound", "self", 977), ("music", 4517)],
         poi=["line_you"]),

    # 3.26: the empty shells (the first funeral)
    dict(key="ch3_shells", title="The Empty Shells", giver="ch1:glubbub", ender="ch1:glubbub", level=24, xp=8, tone="serious",
         prev="ch3_naming", items=[("fallen_shell", 5)], rewards=["empty_shell_pendant"],
         goal="Gather the 5 Name-Shells of the Fallen laid in a row on the beach below the statue, and bring them to Oracle "
              "Glubbub.",
         text="Five did not get up. Five shells with nobody in them. A murloc's shell goes to the sea when the murloc does... "
              "Bring them. All 5. We give them to her together.",
         progress="Gently. They are still somebody's.",
         reward="Shh... listen. Hum with us. Mmmm... mmmm...",
         details=["kneel", "talk"], reward_emotes=["bow", "cry"],
         accept=[("state", "self", "none"), ("emote", "self", "kneel"), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("face", "self", "shells_row_3"), ("emote", "self", "point"), ("visual", "self", 35426)],
         complete=[("summon", "kelp_raft", "raft", 45), ("object", "glow_coral", "mourn_2", 40),
                   ("move", "ch1:gurp", "mourn_1", "walk"), ("move", "ch1:squirt", "mourn_3", "walk"),
                   ("sound", "self", "murloc_fidget2"), ("music", 6075), ("wait", 3000), ("visual", "self", 22576),
                   ("sound", "ch1:gurp", "murloc_fidget2"), ("wait", 3000), ("move", "kelp_raft", "raft_far", "walk"),
                   ("sound", "self", 7294), ("wait", 9000), ("move", "ch1:gurp", "c_freed_1", "walk"),
                   ("move", "ch1:squirt", "c_freed_2", "walk"), ("emote", "self", "bow")],
         poi=["shells_row_3"]),

    # 3.27: the Great Conch
    dict(key="ch3_conch", title="The Oracle's Conch", giver="ch1:glubbub", ender="ch1:glubbub", level=24, xp=8, tone="serious",
         prev="ch3_shells", kill=[("old_clacker", 1)], items=[("great_conch", 1)], drops={"great_conch": [("old_clacker", 100)]},
         goal="Dive into the deepest water west of the pens, past the reef, kill Old Clacker and bring up the Great Conch he sits on.",
         text="We need a big voice. Bigger than mine. Bigger than everyone's. Out there, in the deep, there is a shell as big as a "
              "fry... and a crab older than me sitting on it. Bring me the shell. The crab you can keep.",
         progress="The deep is cold. The conch is colder. Go on.",
         reward="Ooh. Oh. Hold it to your ear... the whole sea is in it. With this, little one, we can call someone very, very old.",
         details=["beg", "question", "point"], reward_emotes=["exclamation", "talk"],
         accept=[("state", "self", "none"), ("emote", "self", "beg"), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("emote", "self", "question"), ("wait", 1500), ("face", "self", "clacker"), ("emote", "self", "point")],
         complete=[("emote", "self", "exclamation"), ("visual", "self", 35426), ("sound", "self", 13706), ("wait", 2000),
                   ("emote", "self", "talk")],
         poi=["clacker"]),

    # 3.28: Grandmother Shellback (the chapter's end: she carries the tribe to the Wetlands)
    dict(key="ch3_end", title="Grandmother Shellback", giver="ch1:glubbub", ender="ch0:shellback", level=24, xp=8,
         tone="serious", prev="ch3_conch", event="Grandmother Shellback called",
         choice=["shell_shield", "conch_ring", "barnacle_bracers"],
         goal="Blow the Great Conch from the Conch-Stone at the water's edge by the jetty, and climb onto whatever answers.",
         text="The Elder says go. The water says go. Everyone says go, and the long ones will come back with more spears if we "
              "stay. Blow the conch at the water's edge, little one. Blow it long. Then we see who comes.",
         progress="...Hrrrmmm?",
         reward="Hrrrmmm... little ones. So many little ones. Climb. Hold on to the barnacles. It is a long way to the other shore.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("give", "great_conch", 1), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "conch_stone"),
                 ("emote", "self", "point"), ("visual", "self", 35426), ("sound", "self", "murloc_fidget2")],
         complete=[("sound", "self", 1463), ("summon", "namer", "climb_1", 30), ("summon", "namer", "climb_2", 30), ("wait", 1500),
                   ("move", "namer", "shellback_back", "walk"), ("sound", "self", 17471), ("wait", 4000), ("music", 6837),
                   ("sound", "self", 13717), ("sound", "self", "ocean"), ("wait", 4000), ("visual", "self", 47479),
                   ("teleport", "player", "ch4:hub", 0.0)],
         poi=["conch_stone"]),

    # chores (17.10): repeatable, at the camp
    dict(key="ch3_pot", title="Something for the Pot", giver="ch1:murlorga", ender="ch1:murlorga", level=23, min=20, xp=3,
         tone="boring", repeatable=True, prev="ch3_uprising", items=[(2674, 10)], drops={2674: [(3812, 50), (3814, 50)]},
         goal="Bring Murlorga 10 Crawler Meat from the Clattering and Spined Crawlers along the Strand.",
         text="40 mouths. 40! Free mouths eat twice as much as slave mouths, I don't know why. Crawler meat, 10 of it. Into the pot.",
         progress="The pot is empty again. It's always empty again.",
         reward="Good, good. Tonk, tonk. Nobody goes hungry in a free camp. Nobody.",
         details=["work", "talk"], reward_emotes=["yes", "talk"],
         accept=[("sound", "self", 973), ("wait", 600), ("sound", "self", 973), ("emote", "self", "talk")],
         complete=[("emote", "self", "yes"), ("sound", "self", 973), ("wait", 600), ("sound", "self", 973)],
         poi=["crawler_beach"]),
    dict(key="ch3_patrol", title="Patrol", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=23, min=20, xp=3, tone="boring",
         repeatable=True, prev="ch3_uprising", kill=[(3711, 6), (3944, 4)],
         goal="Kill 6 Wrathtail Myrmidons and 4 Wrathtail Priestesses on the island north-west of the camp.",
         text="The long ones on the island watch us. Every day. Go and make them watch somewhere else. 10 of them.",
         progress="Still watching?",
         reward="Good. The camp sleeps easier. I don't sleep. But the camp does.",
         details=["point", "attack"], reward_emotes=["flex", "salute"],
         accept=[("face", "self", "island"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "attack")],
         complete=[("emote", "self", "flex"), ("sound", "self", "murloc_fidget2"), ("wait", 1200), ("emote", "self", "salute")]),
]
