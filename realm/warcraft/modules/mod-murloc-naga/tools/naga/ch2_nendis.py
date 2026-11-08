# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 2 of the naga's story: Nendis Burns (levels 15 to 19), the bible's section 9.

The Hollow is the sand islet in the Shattered Strand (x 3920-3985, y -6235 to -6330, z 0 to 9; the bible's "3950,
-6270"), where Lady Szaria takes chapter 1's breakout and the renegades keep their camp: the fire and Vyssa's pot in
the middle, Ssaveth on the dune to the north, the drill sand at the west end, Isshara's pool where the islet runs into
the water on the east, the trades round the south shore, the landing and the drowned singer's graveyard at the west
end. Round it: the reef in the shallows to the north-east (living coral), the open sea to the south-east (clean
water), the camp's fish traps in the shallows. The Spitelash hunt along the north strand under the cliffs (x 4150 to
4230); their courier halts on the bay road along the bay's west shore (3730, -5690); Captain Vessk camps on the same
shore's north end (3925, -5860), across the water from the Hollow. Valormok (the world's and the naga's) is the
Horde's: its people are the game's own (Ag'tor Bloodfist, Jediga, Kurll give and take their quests as they are: the
game's creatures have no scenes of the story's), with the story's grunts, a peon and Kurll's pot round them for the
show; the west road runs down from Valormok to the Southfury, where the Spitelash raiders come up out of the river.
Shadowsong Shrine is the world's (2866, -4022).

Two memories, both Isshara's and both bit A (the bible's M2, Rise of the Naga, in its two songs): m2, the road to
Nendis, on Legash's plateau (the column at dawn on the rim above the gorge south of Legash, the march north to the
satyrs' camp, the maddened furbolgs in the woods west of it, the Watchers' arrows on the trail behind, the wildkin in
the pass south-east toward the Bitter Reaches, the satyrs' pitch); m2b, the port of Nendis, on the Jagged Reef's
beach (4980 to 5000, -7120 to -7240) round its harbour (the round basin at 5000, -7280) with the reef spit beyond
(5010, -7340). They stand 990 yards apart.

Phases: this chapter's one story phase in Azshara is the Hollow's (HUB below: from 2.01's reward until chapter 7
overturns the camp), and everything of the chapter's present carries it: the camp and the hub kit, the Spitelash it
fights, Valormok's story people, the west shore's camps, the shrine's flowers. During 2.01 itself the camp isn't there
yet: the renegades who greet the newcomer are summoned for the scene, and the camp appears at its reward.

Plain data: tools/murloc/SCHEMA.md, tools/naga/SCHEMA.md."""

HUB = ("between", "ch2_arrival", "ch7:ch7_overturned")   # the Hollow and everything of the chapter's present
M2 = ("memory", "m2")                                    # the road to Nendis (Isshara's), Legash's plateau
M2B = ("memory", "m2b")                                  # the port of Nendis (Isshara's), the Jagged Reef's beach

CHAPTER = dict(key="ch2", title="Nendis Burns", levels=(15, 20), map=1, zones=[16], hub="hollow")

TOWNS = ["Valormok"]

# Valormok's own people, the game's (their quests are given and taken by them; scenes go to the story's people
# round them: the game's creatures run no scenes of the story's)
AGTOR, JEDIGA, KURLL = 8576, 8587, 3621

PLACES = {
    # -- the Hollow: the islet (ch1's hollow_szaria, 3954 -6266, is Szaria's; ch0's hollow_landing, 3946 -6262) -------
    "hollow": (3955.0, -6278.0), "hollow_fire": (3962.0, -6280.0), "hollow_fire_szaria": (3958.0, -6277.0),
    "vyssa": (3966.0, -6285.0), "vyssa_pot": (3965.0, -6281.0),
    "ssaveth": (3978.0, -6278.0), "ssaveth_sand": (3972.0, -6268.0), "sand_mark": (3970.0, -6266.0),
    "isshara": (3963.0, -6316.0), "pool": (3969.0, -6323.0), "pool_shore": (3959.0, -6311.0),
    "ring_n": (3972.0, -6321.0), "ring_s": (3966.0, -6325.0), "ring_e": (3970.0, -6327.0), "ring_w": (3967.0, -6319.0),
    "nest": (3961.0, -6318.0), "mirror": (3984.0, -6295.0),
    # where the keeper is laid to rest as the newcomer comes ashore (2.01), and the renegades who greet them
    "rest": (3930.0, -6283.0), "rest_bearer_1": (3933.0, -6280.0), "rest_bearer_2": (3934.0, -6288.0),
    "rest_step_1": (3938.0, -6278.0), "rest_step_2": (3937.0, -6292.0), "rest_step_3": (3933.0, -6296.0),
    "rise_ssaveth": (3946.0, -6248.0), "behind_szaria": (3958.0, -6262.0), "szaria_front": (3950.0, -6268.0),
    "rise_vyssa": (3926.0, -6268.0),
    # the drill sand at the west end, the trainers and the trades round the edges
    "kessh": (3975.0, -6250.0), "recruit_1": (3966.0, -6247.0), "recruit_2": (3963.0, -6250.0),
    "recruit_3": (3958.0, -6243.0), "recruit_squeak": (3970.0, -6252.0), "recruit_cobra": (3961.0, -6255.0),
    "drill": (3965.0, -6249.0),
    "pagoda": (3976.0, -6300.0), "siren_1": (3979.0, -6310.0), "sentry_1": (3984.0, -6285.0), "sentry_2": (3926.0, -6240.0),
    "thessk": (3945.0, -6242.0), "snap": (3942.0, -6246.0), "shivra": (3937.0, -6248.0), "ulmara": (3952.0, -6306.0),
    "oshra": (3978.0, -6316.0), "lyrenne": (3946.0, -6292.0), "nazreth": (3940.0, -6300.0),
    "hookfin": (3926.0, -6252.0), "ysh": (3929.0, -6262.0), "varra": (3929.0, -6272.0), "oleth": (3930.0, -6282.0),
    "sheshk": (3934.0, -6290.0), "grosh": (3950.0, -6238.0), "rhazz": (3956.0, -6240.0), "anvil": (3955.0, -6236.0),
    "hissra": (3939.0, -6294.0), "lysse": (3943.0, -6302.0), "sszix": (3948.0, -6305.0), "avessa": (3955.0, -6300.0),
    "nyss": (3958.0, -6306.0), "thalassa": (3944.0, -6306.0),
    "ishra": (3972.0, -6288.0), "tessh": (3976.0, -6292.0), "clamwarden": (3962.0, -6292.0), "clam": (3964.0, -6296.0),
    "mailbox": (3950.0, -6258.0), "tidecaller": (3942.0, -6264.0), "graveyard": (3932.0, -6241.0), "singer": (3934.0, -6238.0),
    "banner_1": (3945.0, -6258.0), "banner_2": (3956.0, -6312.0), "torch_1": (3958.0, -6262.0), "torch_2": (3972.0, -6276.0),
    "torch_3": (3960.0, -6312.0), "torch_4": (3940.0, -6282.0), "crates": (3970.0, -6290.0), "weapons": (3980.0, -6268.0),
    "jars": (3968.0, -6296.0), "kelp_bed_1": (3936.0, -6298.0), "kelp_bed_2": (3974.0, -6312.0),
    "thessa_rest": (3972.0, -6330.0), "thessa_kelp": (3972.5, -6330.5),
    "hollow_east": (3970.0, -6340.0), "hollow_west": (3950.0, -6200.0), "hollow_north": (4010.0, -6270.0),
    "hollow_south": (3900.0, -6280.0),
    "far_light_a": (3952.0, -6202.0, 2.5), "far_light_b": (3956.0, -6130.0, 2.5),
    "envoy": (3946.0, -6270.0), "envoy_look": (3948.0, -6274.0),
    # the reef (living coral), the open sea (clean water), the camp's fish traps
    "coral_1": (4000.0, -6238.0), "coral_2": (4006.0, -6252.0), "coral_3": (4012.0, -6265.0), "coral_4": (4018.0, -6242.0),
    "coral_5": (4022.0, -6278.0), "coral_6": (4026.0, -6256.0), "coral_7": (3996.0, -6292.0), "coral_8": (4008.0, -6302.0),
    "coral_9": (4034.0, -6270.0), "coral_10": (3998.0, -6270.0), "reef": (4012.0, -6262.0),
    "current_1": (3880.0, -6345.0), "current_2": (3874.0, -6365.0), "current_3": (3886.0, -6385.0),
    "current_4": (3864.0, -6352.0), "current_5": (3868.0, -6396.0), "current_6": (3892.0, -6368.0), "open_sea": (3878.0, -6370.0),
    "trap_1": (3918.0, -6258.0), "trap_2": (3915.0, -6280.0), "trap_3": (3990.0, -6262.0), "trap_4": (3992.0, -6312.0),
    "trap_5": (3945.0, -6322.0), "trap_6": (3920.0, -6300.0), "traps": (3950.0, -6280.0),
    # the north strand under the cliffs and the rocky islet off it: the Spitelash Tide-Hunters
    "th_1": (4210.0, -6080.0), "th_2": (4210.0, -6064.0), "th_3": (4226.0, -6036.0), "th_4": (4218.0, -6116.0),
    "th_5": (4226.0, -6196.0), "th_6": (4218.0, -6232.0), "th_7": (4202.0, -6146.0), "th_8": (4186.0, -6148.0),
    "th_9": (4170.0, -6148.0), "th_10": (4154.0, -6144.0), "th_11": (4226.0, -6044.0), "th_12": (4218.0, -6224.0),
    "north_shore": (4200.0, -6140.0),
    # the bay's west shore: the bay road (the courier's halt) and Captain Vessk's camp
    "courier": (3730.0, -5690.0), "courier_g1": (3736.0, -5683.0), "courier_g2": (3724.0, -5698.0),
    "courier_fire": (3727.0, -5684.0), "courier_post": (3733.0, -5694.0), "bay_road": (3730.0, -5690.0),
    "vessk": (3925.0, -5860.0), "vessk_banner": (3930.0, -5852.0), "vessk_cage": (3918.0, -5869.0),
    "vessk_lock": (3921.0, -5866.0), "vessk_g1": (3933.0, -5846.0), "vessk_g2": (3912.0, -5852.0),
    "vessk_g3": (3936.0, -5872.0), "vessk_g4": (3928.0, -5880.0), "vessk_fire": (3926.0, -5853.0),
    "vessk_crate": (3916.0, -5858.0), "vessk_camp": (3925.0, -5860.0),
    # Valormok: the east approach (its grunts), Jediga's table, Kurll's pot (the game's people: AGTOR, JEDIGA, KURLL)
    "gate_grunt": (3628.0, -4448.0), "gate_grunt_2": (3622.0, -4453.0), "gate_grunt_3": (3634.0, -4442.0),
    "gate_east": (3660.0, -4485.0), "gate_aside": (3620.0, -4440.0), "gate_aside_2": (3638.0, -4452.0),
    "agtor": (3601.0, -4406.0), "jediga": (3603.0, -4421.0), "kurll": (3580.0, -4383.0),
    "grukk": (3607.0, -4426.0), "grukk_round": (3615.0, -4428.0), "grukk_jediga": (3605.0, -4423.0),
    "stewpot": (3580.0, -4388.0), "strongbox": (3579.5, -4378.5),
    "line_1": (3582.0, -4393.0), "line_2": (3585.0, -4397.0), "line_3": (3588.0, -4401.0),
    "hungry_1": (3590.0, -4392.0), "hungry_2": (3594.0, -4396.0),
    # the west road down to the Southfury: the broken cart, the raiders, the snappers in the river
    "cart": (3600.0, -4190.0), "kodo": (3594.0, -4196.0), "carter": (3605.0, -4186.0), "sacks": (3603.0, -4195.0),
    "west_road": (3605.0, -4090.0),
    "rd_1": (3610.0, -4110.0), "rd_2": (3590.0, -4095.0), "rd_3": (3625.0, -4085.0), "rd_4": (3600.0, -4070.0),
    "rd_5": (3580.0, -4060.0), "rd_6": (3615.0, -4050.0), "rd_7": (3595.0, -4035.0), "rd_8": (3630.0, -4120.0),
    "rd_9": (3570.0, -4085.0), "rd_10": (3585.0, -4115.0),
    "sn_1": (3570.0, -3962.0), "sn_2": (3590.0, -3965.0), "sn_3": (3610.0, -3960.0), "sn_4": (3630.0, -3963.0),
    "sn_5": (3650.0, -3960.0), "sn_6": (3670.0, -3963.0), "sn_7": (3600.0, -3970.0), "sn_8": (3640.0, -3968.0),
    "river": (3620.0, -3963.0),
    # Shadowsong Shrine: the broken pillar, the treeline she comes out of and goes back into
    "pillar": (2866.0, -4022.0), "flowers": (2867.0, -4024.0), "fresh_flowers": (2867.5, -4025.0),
    "shaelyn_trees": (2885.0, -4052.0), "shaelyn_kneel": (2869.5, -4026.5), "shaelyn_away": (2900.0, -4082.0),

    # -- memory m2 (bit A): the road to Nendis, on Legash's plateau ---------------------------------------------------
    "m2_centre": (4620.0, -6300.0), "m2_stage": (4458.0, -6300.0), "m2_director": (4462.0, -6305.0),
    "m2_vashj": (4444.0, -6336.0), "m2_sun": (4430.0, -6420.0), "m2_vashj_away": (4430.0, -6360.0),
    "c_1": (4462.0, -6290.0), "c_2": (4470.0, -6306.0), "c_3": (4452.0, -6316.0), "c_4": (4472.0, -6296.0),
    "m2_guide": (4472.0, -6303.0), "m2_camp": (4735.0, -6316.0), "m2_isshara": (4742.0, -6322.0), "m2_fire": (4748.0, -6312.0),
    "m2_c1_end": (4730.0, -6306.0), "m2_c2_end": (4728.0, -6322.0), "m2_c3_end": (4724.0, -6312.0), "m2_c4_end": (4732.0, -6296.0),
    "rest_a": (4752.0, -6300.0), "rest_b": (4758.0, -6318.0), "rest_c": (4746.0, -6334.0), "rest_d": (4735.0, -6300.0),
    "rest_e": (4762.0, -6330.0), "satyr_a": (4728.0, -6290.0), "satyr_b": (4770.0, -6310.0),
    "quartermaster": (4722.0, -6340.0), "store_1": (4718.0, -6346.0), "store_2": (4725.0, -6351.0),
    "store_3": (4714.0, -6339.0), "store_4": (4731.0, -6354.0), "store_5": (4711.0, -6350.0), "store_6": (4720.0, -6358.0),
    "worker_a": (4728.0, -6345.0), "worker_b": (4708.0, -6343.0), "worker_c": (4716.0, -6355.0), "worker_d": (4733.0, -6339.0),
    "stores": (4720.0, -6348.0),
    "f_1": (4740.0, -6150.0), "f_2": (4760.0, -6130.0), "f_3": (4780.0, -6160.0), "f_4": (4750.0, -6175.0),
    "f_5": (4770.0, -6110.0), "f_6": (4730.0, -6125.0), "f_7": (4790.0, -6135.0), "f_8": (4745.0, -6105.0),
    "f_9": (4775.0, -6185.0), "f_10": (4760.0, -6150.0), "woods": (4760.0, -6145.0), "woods_satyr": (4745.0, -6200.0),
    "a_1": (4505.0, -6302.0), "a_2": (4530.0, -6318.0), "a_3": (4560.0, -6296.0), "a_4": (4590.0, -6320.0),
    "a_5": (4620.0, -6300.0), "a_6": (4650.0, -6322.0), "a_7": (4675.0, -6298.0), "a_8": (4700.0, -6320.0),
    "trail": (4600.0, -6310.0),
    "pass": (4565.0, -6495.0), "vashj_pass": (4578.0, -6512.0), "vashj_pass_away": (4600.0, -6560.0),

    # -- memory m2b (bit A): the port of Nendis, on the Jagged Reef's beach round its harbour --------------------------
    "m2b_centre": (4998.0, -7215.0), "m2b_stage": (5012.0, -7345.0), "m2b_director": (5012.0, -7340.0),
    "overlook": (5016.0, -7330.0), "m2b_isshara": (4992.0, -7242.0),
    "ship_1": (5004.0, -7272.0, 0.0), "ship_2": (5018.0, -7290.0, 0.0), "ship_3": (4988.0, -7292.0, 0.0),
    "rig_1": (5004.0, -7265.0, 0.5), "rig_2": (5016.0, -7283.0, 0.5), "rig_3": (4990.0, -7285.0, 0.5),
    "dock_1": (4987.0, -7246.0, 0.5), "dock_2": (4975.0, -7248.0, 0.5),
    "house_1": (4986.0, -7150.0), "house_2": (4988.0, -7176.0), "house_3": (4981.0, -7200.0), "house_burn": (4972.0, -7215.0),
    "house_in": (4972.0, -7213.0), "house_front": (4978.0, -7220.0), "house_out": (4980.0, -7224.0),
    "water_edge": (4976.0, -7238.0), "hills": (4990.0, -7132.0),
    "bell": (4991.0, -7232.0), "lamp_1": (4993.0, -7160.0), "lamp_2": (4991.0, -7190.0), "lamp_3": (4986.0, -7222.0),
    "lamp_4": (4996.0, -7240.0), "banner": (4990.0, -7140.0), "crates_dock": (4994.0, -7238.0), "barrels_dock": (4983.0, -7236.0),
    "watchman": (4990.0, -7205.0), "watchman_run": (4992.0, -7150.0), "bellringer": (4988.0, -7230.0),
    "sleeper_1": (4983.0, -7165.0), "sleeper_2": (4979.0, -7186.0), "townsfolk_run": (4995.0, -7120.0),
    "w_1": (5000.0, -7100.0), "w_2": (5006.0, -7112.0), "w_3": (4995.0, -7118.0), "w_4": (5010.0, -7095.0), "w_5": (4988.0, -7108.0),
    "dock_watcher_1": (4990.0, -7226.0), "dock_watcher_2": (4984.0, -7232.0), "dock_watcher_3": (4995.0, -7222.0),
    "maiev": (4986.0, -7228.0),
    "vashj_rise": (5010.0, -7300.0, -8.0), "vashj_surface": (5010.0, -7300.0, 0.0), "vashj_sink": (5016.0, -7305.0, -12.0),
    "town": (4985.0, -7180.0), "sea": (5040.0, -7330.0), "harbour": (5000.0, -7280.0),
    "fire_1": (5002.0, -7270.0, 3.0), "fire_2": (5006.0, -7276.0, 3.0), "fire_3": (5016.0, -7287.0, 3.0),
    "fire_4": (5020.0, -7293.0, 3.0), "fire_5": (4986.0, -7289.0, 3.0), "fire_6": (4990.0, -7296.0, 3.0),
    "fire_house_1": (4972.0, -7215.0), "fire_house_2": (4968.0, -7210.0), "fire_town_1": (4986.0, -7150.0),
    "fire_town_2": (4981.0, -7200.0), "fire_town_3": (4988.0, -7176.0),
}

# -- models ----------------------------------------------------------------------------------------------------------
CAGE = "World\\EXPANSION01\\DOODADS\\COILFANG\\PASSIVEDOODADS\\cages\\cf_groundcage.m2"
CHAINS = "World\\Expansion01\\Doodads\\Generic\\Ogre\\Chains\\OM_Chains_01.mdx"
CORAL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\Coral01.mdx"
CORAL_TREE = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree01.mdx"
CORAL_TREE_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree02.mdx"
SEAWEED = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Seaweed\\SeaWeed01.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
SHELL_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
EGG = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_01.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
BROKEN_CART = "World\\Azeroth\\Westfall\\PassiveDoodads\\BrokenCart\\BrokenCart.m2"
ARROW = "World\\Generic\\Human\\Passive Doodads\\Weapons&Armor\\HumanArrow.m2"
NE_HOUSE = "World\\Generic\\NightElf\\Passive Doodads\\Gazibos\\KalidarGazibo.m2"
NE_TENT = "World\\Generic\\NightElf\\Passive Doodads\\Tent\\NightElfSingleTent01.m2"
NE_LAMP = "World\\Generic\\NightElf\\Passive Doodads\\Lamps\\DarnassusStreetLamp01.m2"
NE_BANNER = "World\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\Banners\\NightElfOwlBanner01.m2"
NE_CRATE = "World\\Generic\\NightElf\\Passive Doodads\\Crates\\ElfCrate01.m2"
NE_BARREL = "World\\Generic\\NightElf\\Passive Doodads\\Barrel\\ElfBarrel01.m2"
SHIP = "World\\Kalimdor\\Darkshore\\PassiveDoodads\\Boats\\DarkshoreBoat.m2"
DOCK = "World\\Azeroth\\Redridge\\PassiveDoodads\\Docks\\RedridgeDocks01.m2"
BELL = 4052                                           # the game's ship's bell (GameObjectDisplayInfo)
FLOWERS_OLD = "World\\Azeroth\\Elwynn\\PassiveDoodads\\Detail\\ElwynnFlower01.m2"
FLOWERS_NEW = "World\\Expansion01\\Doodads\\Silvermoon\\Flowers\\SilvermoonFlower02.m2"
RUIN = "World\\Generic\\NightElf\\Passive Doodads\\Ruins\\NewElfRuin03.m2"
DOOR = "World\\Generic\\NightElf\\ActiveDoodads\\Doors\\BFD_BrassDoors.m2"
STEWPOT = 6849                                        # the game's cooking pot (GameObjectDisplayInfo), as chapter 1's

# -- the people --------------------------------------------------------------------------------------------------------
NPCS = [
    # 2.01's welcome: the renegades who greet the newcomer before the camp is theirs to see (summoned for the scene)
    dict(key="isshara_carried", name="Isshara the Keeper", subname="Keeper of Songs", look="sea_witch", level=45,
         role="ambient", summoned=True, idle=[("state", "self", "drowned")]),
    dict(key="bearer", name="Tide-Broken Myrmidon", look=18389, size=1.2, level=30, role="ambient", summoned=True),
    dict(key="ssaveth_greet", name="Myrmidon Ssaveth", subname="The Tide-Broken", look="naga_warrior", level=40,
         role="ambient", summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="vyssa_greet", name="Vyssa the Coral-Keeper", subname="Innkeeper", look="sorceress", level=35, role="ambient",
         summoned=True),

    # the camp's own (the hub kit is ch0's, placed below with SPAWNS)
    dict(key="sentry", name="Tide-Broken Sentry", plural="sentries", look=18389, looks=[22874], size=1.2, level=30,
         role="ambient", at=["sentry_1", "sentry_2"], facing=0.4, phase=HUB,
         gossip="The water's quiet. When it isn't, you'll hear me before you see them.",
         idle=[("state", "self", "ready_thrown"), ("every", 63000, [("emote", "self", "roar")])]),
    dict(key="camp_siren", name="Tide-Broken Siren", look=18395, size=1.0, level=30, role="ambient", at="siren_1",
         facing=4.2, phase=HUB, gossip="Nets. Always nets. The sea gives fish to those who mend.",
         idle=[("state", "self", "work"), ("every", 57000, [("emote", "self", "laugh")])]),
    dict(key="recruit", name="Tide-Broken Recruit", plural="recruits", look=22875, looks=[22871, 22877], size=0.95,
         level=12, role="ambient", at=["recruit_1", "recruit_2", "recruit_3"], facing=0.2, phase=HUB,
         gossip="Ssaveth says I roar like a hatchling with a cold. I don't have a cold.",
         idle=[("state", "self", "ready_thrown"), ("every", 49000, [("emote", "self", "shy")])]),
    dict(key="recruit_squeak", name="Recruit Ilthi", subname="Tide-Broken Recruit", look=22869, size=0.9, level=12,
         role="ambient", at="recruit_squeak", facing=0.2, phase=HUB,
         gossip="I can roar. I can! It just comes out... higher.",
         idle=[("every", 44000, [("emote", "self", "question")])]),
    dict(key="recruit_cobra", name="Recruit Kossh", subname="Tide-Broken Recruit", look=22874, size=1.0, level=12,
         role="ambient", at="recruit_cobra", facing=0.2, phase=HUB,
         gossip="I've been practising. In my head. It's going to be very good.",
         idle=[("state", "self", "ready_thrown"), ("every", 53000, [("emote", "self", "flex")])]),
    # the pool's water and the camp's fire, for the scenes' looks (nobody sees them as people)
    dict(key="keepers_pool", name="Isshara's Pool", look="trigger", level=1, role="ambient", at="pool",
         unit_flags=0x02000002, phase=HUB, idle=[("every", 34000, [("visual", "self", 36005)])]),
    dict(key="fire_spirit", name="The Camp's Fire", look="trigger", level=1, role="ambient", at="hollow_fire",
         unit_flags=0x02000002, phase=HUB),
    dict(key="pool_vision", name="A Shape on the Water", look="trigger", scale=2.0, level=1, role="ambient",
         unit_flags=0x02000002, summoned=True),
    # 2.06's light far out on the water, moving west: the courier's boat-lantern
    dict(key="courier_light", name="A Light on the Water", look="trigger", level=1, role="ambient", sky=3,
         unit_flags=0x02000002, summoned=True, idle=[("every", 3000, [("visual", "self", 44880)])]),
    # 2.12's envoy, back from Valormok with an arrow through his crest
    dict(key="envoy", name="Tide-Broken Envoy", look=18389, size=1.15, level=25, role="ambient", summoned=True),

    # -- what the Spitelash send against the Hollow --------------------------------------------------------------------
    dict(key="tide_hunter", name="Spitelash Tide-Hunter", plural="spitelash tide-hunters", look=6747, looks=[11265],
         level=(15, 17), side="naga", role="enemy", at=["th_1", "th_2", "th_3", "th_4", "th_5", "th_6", "th_7", "th_8",
                                                      "th_9", "th_10", "th_11", "th_12"],
         wander=5.0, respawn=45, phase=HUB, abilities=[(6533, 21000)]),
    dict(key="courier", name="Spitelash Courier", subname="Bound for Lady Sesspira", look=11264, size=1.1, level=17,
         health=2.6, side="naga", role="enemy", at="courier", facing=2.3, respawn=90, phase=HUB,
         abilities=[(6546, 11000)], idle=[("every", 3000, [("visual", "self", 44880)])]),
    dict(key="courier_guard", name="Spitelash Escort", plural="spitelash escorts", look=6747, level=16, side="naga",
         role="enemy", at=["courier_g1", "courier_g2"], facing=2.3, respawn=90, phase=HUB, abilities=[(6533, 25000)]),
    dict(key="vessk", name="Captain Vessk", subname="Hunt-Captain of the Spitelash", look=11271, size=1.25, level=19,
         health=3.5, damage=1.3, side="naga", role="enemy", at="vessk", facing=3.0, respawn=120, phase=HUB,
         abilities=[(5242, 26000), (845, 9000)],
         watch=(26, [("face", "self", "player"), ("emote", "self", "battle_roar"), ("sound", "self", 11695)], 30000)),
    dict(key="vessk_hunter", name="Spitelash Hunter", plural="spitelash hunters", look=6747, looks=[11265], level=(17, 18),
         side="naga", role="enemy", at=["vessk_g1", "vessk_g2", "vessk_g3", "vessk_g4"], wander=3.0, respawn=60, phase=HUB,
         abilities=[(6533, 24000)]),
    # the renegade in Vessk's cage (2.24: her name is Thessa)
    dict(key="caged_siren", name="Caged Siren", subname="Prisoner of the Spitelash", look=11266, size=1.15, level=20,
         role="ambient", at="vessk_cage", facing=1.2, respawn=120, phase=HUB,
         gossip="...water. Is there... water...",
         idle=[("state", "self", "drowned"), ("every", 27000, [("sound", "self", 4021)])]),

    # -- Valormok: the story's people round the game's (orcs, readable: the naga speak Orcish) --------------------------
    dict(key="gate_grunt", name="Grunt Morgash", subname="Valormok", look=4259, level=30, side="faction:76",
         language="orcish", role="ambient", at="gate_grunt", facing=5.36, phase=HUB,
         gossip="Keep your hands where I can see them, fish. All four of them. However many you've got.",
         idle=[("every", 51000, [("emote", "self", "rude")])]),
    dict(key="gate_grunt_b", name="Valormok Grunt", look=4260, level=28, side="faction:76", language="orcish",
         role="ambient", at="gate_grunt_2", facing=5.36, phase=HUB,
         gossip="Chief says you're allowed. Chief says a lot of things."),
    dict(key="gate_grunt_c", name="Valormok Grunt", look=9798, level=28, side="faction:76", language="orcish",
         role="ambient", at="gate_grunt_3", facing=5.36, phase=HUB,
         gossip="I've got my eye on you. Both eyes. Don't make me use the axe."),
    dict(key="grukk", name="Peon Grukk", subname="Jediga's Runner", look=10038, level=10, side="faction:76",
         language="orcish", role="ambient", at="grukk", facing=2.0, phase=HUB,
         gossip="Boss says measure. Grukk measures. Boss says fetch. Grukk fetches. Grukk is very busy.",
         idle=[("every", 39000, [("emote", "self", "work")])]),
    dict(key="hungry_grunt", name="Hungry Grunt", look=9799, level=26, side="faction:76", language="orcish",
         role="ambient", at="hungry_1", facing=4.5, phase=HUB,
         gossip="It's grey. Stew isn't supposed to be grey. I've been in three wars and stew was never grey.",
         idle=[("every", 46000, [("emote", "self", "no")])]),
    dict(key="hungry_grunt_2", name="Hungry Grunt", look=9801, level=26, side="faction:76", language="orcish",
         role="ambient", at="hungry_2", facing=4.5, phase=HUB,
         gossip="Don't look in the pot. I looked in the pot. Don't.",
         idle=[("every", 53000, [("emote", "self", "cry")])]),
    dict(key="carter", name="Grunt Mukra", subname="Valormok's Carter", look=9800, level=25, side="faction:76",
         language="orcish", role="ambient", at="carter", facing=1.6, phase=HUB,
         gossip="Up out of the river, they came. Tridents. Took the meal sacks. Took my kodo's... took my kodo.",
         idle=[("state", "self", "sit")],
         watch=(20, [("face", "self", "player"), ("emote", "self", "point"),
                     ("say", "self", "Down there. They come up out of the river. Go on, if you're going.", "point")], 50000)),
    dict(key="dead_kodo", name="Dead Kodo", look=1453, level=10, role="ambient", type="beast", at="kodo", facing=2.0,
         unit_flags=0x02000000, phase=HUB, idle=[("state", "self", "dead")]),
    dict(key="raider", name="Spitelash Raider", plural="spitelash raiders", look=11265, looks=[6747], level=(16, 18),
         side="naga", role="enemy", at=["rd_1", "rd_2", "rd_3", "rd_4", "rd_5", "rd_6", "rd_7", "rd_8", "rd_9", "rd_10"],
         wander=5.0, respawn=45, phase=HUB, abilities=[(6546, 12000)]),
    dict(key="snapper", name="Southfury Snapper", plural="southfury snappers", look=6368, size=0.7, level=(15, 16),
         side="neutral", role="enemy", type="beast", health=0.9,
         at=["sn_1", "sn_2", "sn_3", "sn_4", "sn_5", "sn_6", "sn_7", "sn_8"], wander=6.0, respawn=30, phase=HUB),

    # -- Shaelyn Harborsong, the last of Nendis (chapter 4's, and later chapters': she appears here for one scene) -----
    dict(key="shaelyn", name="Shaelyn Harborsong", subname="The Last of Nendis", look="shaelyn", level=40,
         side="faction:69", language="darnassian", role="quest",
         gossip="Elune-adore. Go back to the sea, serpent. There is nothing for you at this shrine.",
         idle=[("every", 47000, [("emote", "self", "talk")])]),

    # -- memory m2: the road to Nendis (the column's people; Illidan's satyrs; what bars the way) -----------------------
    dict(key="m2_director", name="Legash, the Morning After", look="trigger", level=1, role="ambient", at="m2_director",
         unit_flags=0x02000002, phase=M2,
         watch=(18, [("music", 9462), ("summon", "vashj_dawn", "m2_vashj", 55), ("summon", "guide_satyr", "m2_guide", 75),
                     ("summon", "column_a", "c_1", 75), ("summon", "column_b", "c_2", 75),
                     ("summon", "column_c", "c_3", 75), ("summon", "column_d", "c_4", 75), ("wait", 1500),
                     ("face", "vashj_dawn", "m2_sun"), ("emote", "vashj_dawn", "omnicast"), ("wait", 1500),
                     ("say", "vashj_dawn", "It's far too bright in this surface world, and this... fresh air is irritating my eyes!",
                      "talk", "LadyVashjPissed5"), ("wait", 6000),
                     ("emote", "column_a", "laugh"), ("wait", 400), ("emote", "column_c", "laugh"), ("wait", 300),
                     ("emote", "column_b", "chicken"), ("emote", "column_d", "laugh"), ("emote", "guide_satyr", "laugh"),
                     ("sound", "guide_satyr", 6517), ("wait", 1500), ("face", "vashj_dawn", "m2_guide"),
                     ("emote", "vashj_dawn", "roar"), ("emote", "column_a", "shy"), ("emote", "column_b", "shy"),
                     ("wait", 2000), ("emote", "guide_satyr", "bow"),
                     ("say", "guide_satyr", "This way, my lovely scaled friends! Lord Illidan's road runs north, and so do we.", "talk"),
                     ("wait", 2500), ("move", "guide_satyr", "m2_camp", "run"), ("move", "vashj_dawn", "m2_vashj_away", "walk"),
                     ("wait", 1500), ("move", "column_a", "m2_c1_end", "run"), ("wait", 600),
                     ("move", "column_b", "m2_c2_end", "run"), ("wait", 600), ("move", "column_c", "m2_c3_end", "run"),
                     ("wait", 600), ("move", "column_d", "m2_c4_end", "run")], 90000)),
    dict(key="vashj_dawn", name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         summoned=True),
    dict(key="guide_satyr", name="Satyr Pathfinder", subname="Servant of Illidan", look=11331, level=30, role="ambient",
         untouchable=True, summoned=True),
    dict(key="column_a", name="Naga of Vashj's Host", look=18389, size=1.05, level=20, role="ambient", untouchable=True,
         summoned=True),
    dict(key="column_b", name="Naga of Vashj's Host", look=18392, size=1.0, level=20, role="ambient", untouchable=True,
         summoned=True),
    dict(key="column_c", name="Naga of Vashj's Host", look=22874, size=1.05, level=20, role="ambient", untouchable=True,
         summoned=True),
    dict(key="column_d", name="Naga of Vashj's Host", look=22870, size=1.0, level=20, role="ambient", untouchable=True,
         summoned=True),
    dict(key="host", name="Naga of Vashj's Host", plural="naga of the host", look=18398, looks=[18395, 22875, 22872],
         size=1.05, level=20, role="ambient", untouchable=True, at=["rest_a", "rest_b", "rest_c", "rest_d", "rest_e"],
         phase=M2, idle=[("state", "self", "sit"), ("every", 61000, [("emote", "self", "talk")])]),
    dict(key="camp_satyr", name="Satyr Servitor", subname="Servant of Illidan", plural="satyr servitors", look=2878,
         looks=[6743, 11338], level=30, role="ambient", untouchable=True, at=["satyr_a", "satyr_b"], phase=M2,
         idle=[("every", 33000, [("emote", "self", "laugh"), ("sound", "self", 1011)])]),
    dict(key="woods_satyr", name="Satyr Servitor", subname="Servant of Illidan", look=11338, level=30, role="ambient",
         untouchable=True, at="woods_satyr", facing=1.7, phase=M2,
         idle=[("every", 13000, [("face", "self", "woods"), ("emote", "self", "laugh"), ("sound", "self", 6335)])]),
    dict(key="quartermaster", name="Satyr Quartermaster", subname="Servant of Illidan", look=11332, level=30,
         role="ambient", untouchable=True, at="quartermaster", facing=0.6, phase=M2,
         gossip="Pitch! Lovely, sticky, flammable pitch. Take all you can carry, darling. It's for a good cause.",
         idle=[("every", 21000, [("emote", "self", "laugh"), ("sound", "self", 6517)])]),
    dict(key="naga_worker", name="Naga of Vashj's Host", look=22876, looks=[18393], size=1.05, level=20, role="ambient",
         untouchable=True, at=["worker_a", "worker_b"], phase=M2, idle=[("state", "self", "work")]),
    dict(key="satyr_worker", name="Satyr Servitor", subname="Servant of Illidan", look=6743, level=30, role="ambient",
         untouchable=True, at=["worker_c", "worker_d"], phase=M2,
         idle=[("state", "self", "work"), ("every", 9000, [("sound", "self", 1011)])]),
    dict(key="furbolg", name="Maddened Furbolg", plural="maddened furbolgs", look=936, looks=[6825, 6826, 6746],
         level=(15, 17), side="hostile", role="enemy",
         at=["f_1", "f_2", "f_3", "f_4", "f_5", "f_6", "f_7", "f_8", "f_9", "f_10"], wander=5.0, respawn=30, phase=M2,
         abilities=[(99, 16000)], idle=[("every", 20000, [("visual", "self", 22577)])]),
    dict(key="wildkin", name="Berserk Wildkin", look=12235, level=18, health=3.0, damage=1.2, side="hostile",
         role="enemy", type="beast", at="pass", facing=2.0, respawn=60, phase=M2, abilities=[(99, 13000), (3391, 8000)],
         idle=[("every", 15000, [("visual", "self", 35411)])],
         watch=(30, [("face", "self", "player"), ("emote", "self", "roar"), ("sound", "self", 3605)], 20000),
         at_health=(70, [("summon", "vashj_passing", "vashj_pass", 18), ("sound", "self", 3601), ("wait", 900),
                         ("face", "vashj_passing", "pass"), ("emote", "vashj_passing", "spell"), ("wait", 600),
                         ("visual", "self", 10387),
                         ("emote", "self", "stun"), ("sound", "self", 3602), ("wait", 1500),
                         ("move", "vashj_passing", "vashj_pass_away", "run")])),
    dict(key="vashj_passing", name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         summoned=True),

    # -- memory m2b: the port of Nendis (asleep; then burning) ----------------------------------------------------------
    dict(key="m2b_director", name="Nendis, the Harbour Asleep", look="trigger", level=1, role="ambient", at="m2b_director",
         unit_flags=0x02000002, phase=M2B,
         watch=(18, [("music", 3900), ("wait", 3000), ("sound", "self", 6674), ("wait", 4000), ("sound", "self", 11820),
                     ("wait", 5000), ("sound", "self", 6674)], 120000)),
    dict(key="watchman", name="Nendis Watchman", look=1729, level=30, role="ambient", at="watchman", facing=1.5, phase=M2B,
         gossip="Quiet night. Quiet sea. The Watchers' riders went through yesterday. Hunting something.",
         idle=[("every", 37000, [("emote", "self", "talk")]), ("every", 58000, [("face", "self", "harbour")])]),
    dict(key="bellringer", name="Old Harbourmaster", look=1722, level=30, role="ambient", at="bellringer", facing=4.7,
         phase=M2B, gossip="Third bell. All's well in Nendis. All's always well in Nendis.",
         idle=[("every", 64000, [("sound", "self", 6674), ("emote", "self", "work")])]),
    dict(key="sleeper", name="Townsfolk of Nendis", plural="townsfolk", look=1730, looks=[1727, 1701], level=10,
         role="ambient", at=["sleeper_1", "sleeper_2"], facing=1.5, phase=M2B, idle=[("state", "self", "sleep")]),
    dict(key="watcher", name="Watcher", subname="Maiev's Watchers", plural="watchers", look="warden",
         looks=["warden_2", "warden_3", "warden_4"], level=(16, 19), side="hostile", role="enemy",
         at=["w_1", "w_2", "w_3", "w_4", "w_5"], wander=3.0, respawn=45, phase=M2B, abilities=[(2764, 7000)]),
    dict(key="maiev", name="Maiev Shadowsong", subname="Warden", look="maiev", level=45, role="ambient",
         untouchable=True, summoned=True),
    dict(key="girl", name="Frightened Girl", look=1730, scale=0.55, level=1, role="ambient", language="darnassian",
         summoned=True),
    dict(key="ship_fire", name="Fire", look="trigger", scale=3.0, level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 4000, [("visual", "self", 42726)])]),
    dict(key="house_fire", name="Fire", look="trigger", scale=2.0, level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 4000, [("visual", "self", 51195)])]),
    dict(key="vashj_nendis", name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         summoned=True),
]

# -- things ------------------------------------------------------------------------------------------------------------
OBJECTS = [
    # the Hollow: the camp's pagoda, banners, torches, stores, its fire, Isshara's pool ring, the egg from the crèche
    dict(key="pagoda", model="naga_pagoda", name="Tide-Broken Pagoda", at="pagoda", kind="doodad", facing=3.6, phase=HUB),
    dict(key="banner", model="naga_banner", name="Tide-Broken Banner", at=["banner_1", "banner_2"], kind="doodad",
         facing=1.0, phase=HUB),
    dict(key="torch", model="naga_torch", name="Naga Torch", at=["torch_1", "torch_2", "torch_3", "torch_4"], kind="doodad",
         phase=HUB),
    dict(key="crates", model="naga_crate", name="Salvaged Crates", at="crates", kind="doodad", facing=0.7, phase=HUB),
    dict(key="weapons", model="naga_weapons", name="Tridents", at="weapons", kind="doodad", facing=2.2, phase=HUB),
    dict(key="jars", model="naga_jar", name="Sealed Jars", at="jars", kind="doodad", phase=HUB),
    dict(key="campfire", model="campfire", name="Campfire", at="hollow_fire", kind="doodad", phase=HUB),
    dict(key="anvil", model="naga_weapons", name="Forgecoil's Rack", at="anvil", kind="doodad", facing=0.0, scale=0.8, phase=HUB),
    dict(key="pool_stone", model=CORAL, name="Isshara's Pool", at=["ring_n", "ring_s", "ring_e", "ring_w"], kind="doodad",
         scale=0.55, phase=HUB),
    dict(key="kelp_bed", model=SEAWEED, name="Kelp Bedding", at=["kelp_bed_1", "kelp_bed_2"], kind="doodad", scale=0.6,
         phase=HUB),
    dict(key="nest", model=SEAWEED, name="Kelp Nest", at="nest", kind="doodad", scale=0.45, phase=HUB),
    dict(key="nest_egg", model=EGG, name="The Crèche's Egg", at="nest", kind="doodad", scale=0.3, phase=HUB),

    # quests' things at the Hollow: the still pool where the sigil comes off, the reef's coral, the open sea's springs,
    # the camp's fish traps
    dict(key="still_pool", model=SHELL_2, name="Still Tide Pool", kind="use", quest="ch2_sigil", consumable=False,
         scale=1.3, at="mirror", facing=1.0, goal="The Empress's sigil scratched out", phase=HUB,
         beats=[("take", "coral_shard", 1), ("aura", "player", "scratched"), ("sound", "player", "naga_wound"),
                ("unaura", "player", "ch1:tide_sworn"), ("aura", "player", "tide_broken"), ("wait", 1500),
                ("emote", "ch0:ssaveth", "roar"), ("sound", "ch0:ssaveth", "naga_aggro"), ("wait", 1300),
                ("emote", "sentry", "roar"), ("wait", 1700), ("emote", "ch0:szaria", "roar"),
                ("sound", "ch0:szaria", "siren_aggro"), ("wait", 900), ("emote", "camp_siren", "roar"), ("wait", 2100),
                ("emote", "ch0:vyssa", "roar"), ("wait", 1100), ("emote", "ch0:kessh", "battle_roar"),
                ("sound", "ch0:kessh", "naga_aggro")]),
    dict(key="living_coral", model=CORAL_TREE_2, name="Living Coral", kind="loot", loot=[("living_coral", 1, 1)],
         quest="ch2_coral", scale=0.6, respawn=30, phase=HUB,
         at=["coral_1", "coral_2", "coral_3", "coral_4", "coral_5", "coral_6", "coral_7", "coral_8", "coral_9", "coral_10"]),
    dict(key="clean_spring", model=SHELL, name="Clean Spring", kind="loot", loot=[("sea_jug", 1, 1)], quest="ch2_seawater",
         scale=1.4, respawn=25, phase=HUB, at=["current_1", "current_2", "current_3", "current_4", "current_5", "current_6"]),
    dict(key="fish_trap", model="crab_basket", name="Tide-Broken Fish Trap", kind="loot", loot=[("bay_fish", 1, 2)],
         quest="ch2_fish", respawn=30, phase=HUB, at=["trap_1", "trap_2", "trap_3", "trap_4", "trap_5", "trap_6"]),

    # set out by the Hollow's scenes
    dict(key="living_coral_set", model=CORAL_TREE, name="Living Coral", kind="doodad", scale=0.4),
    dict(key="sand_line", model=TRIDENT, name="A Line in the Sand", kind="doodad", scale=0.45),
    dict(key="sand_mark", model=SHELL_2, name="Drawing in the Sand", kind="doodad", scale=0.5),
    dict(key="kelp_blanket", model=SEAWEED, name="Kelp Blanket", kind="doodad", scale=0.7),
    dict(key="door_vision", model=DOOR, name="A Shape on the Water", kind="doodad", scale=0.3),

    # Valormok: Kurll's pot and his strongbox (behind him); the broken cart and its spilled sacks on the west road
    dict(key="stewpot", model=STEWPOT, name="Kurll's Stewpot", kind="use", quest="ch2_larder", consumable=False, scale=1.2,
         at="stewpot", goal="Kurll's grey stew tipped out", phase=HUB,
         beats=[("sound", "player", 7035), ("emote", KURLL, "eat"), ("wait", 1500), ("emote", KURLL, "no"),
                ("sound", "player", 1197), ("wait", 1200), ("move", "hungry_grunt", "line_1", "walk"),
                ("move", "hungry_grunt_2", "line_2", "walk"), ("wait", 2500), ("emote", "hungry_grunt", "cheer"),
                ("emote", "hungry_grunt_2", "cheer"), ("wait", 1500), ("face", "hungry_grunt", "player"),
                ("emote", "hungry_grunt", "yes"), ("wait", 8000), ("move", "hungry_grunt", "hungry_1", "walk"),
                ("move", "hungry_grunt_2", "hungry_2", "walk")]),
    dict(key="strongbox_obj", model="chest", name="Kurll's Strongbox", kind="use", quest="ch2_strongbox",
         consumable=True, respawn=120, at="strongbox", facing=1.6, goal="Kurll's strongbox taken", phase=HUB,
         beats=[("give", "strongbox", 1), ("sound", "player", 1277), ("sound", "player", 7035), ("emote", KURLL, "work"),
                ("wait", 2500), ("face", "hungry_grunt_2", "player"), ("emote", "hungry_grunt_2", "question")]),
    dict(key="broken_cart", model=BROKEN_CART, name="Broken Supply Cart", at="cart", kind="doodad", facing=1.2, phase=HUB),
    dict(key="spilled_sacks", model="sack", name="Torn Meal Sacks", at="sacks", kind="doodad", facing=0.4, phase=HUB),

    # the west shore: the courier's halt on the bay road, Captain Vessk's camp and its cage
    dict(key="courier_fire", model="campfire", name="Campfire", at="courier_fire", kind="doodad", phase=HUB),
    dict(key="courier_torch", model="naga_torch", name="Naga Torch", at="courier_post", kind="doodad", phase=HUB),
    dict(key="vessk_banner", model="naga_banner", name="Spitelash Banner", at="vessk_banner", kind="doodad", facing=2.8,
         scale=1.3, phase=HUB),
    dict(key="vessk_cage", model=CAGE, name="Spitelash Cage", at="vessk_cage", kind="doodad", facing=1.2, phase=HUB),
    dict(key="vessk_fire", model="campfire", name="Campfire", at="vessk_fire", kind="doodad", phase=HUB),
    dict(key="vessk_crate", model="naga_crate", name="Spitelash Stores", at="vessk_crate", kind="doodad", phase=HUB),
    dict(key="cage_lock", model=CHAINS, name="The Cage's Chains", kind="use", quest="ch2_caged", consumable=False,
         scale=0.6, at="vessk_lock", facing=1.2, goal="The cage opened", phase=HUB,
         beats=[("sound", "player", 1277), ("state", "caged_siren", "none"), ("wait", 1500),
                ("face", "caged_siren", "player"), ("emote", "caged_siren", "talk"), ("sound", "caged_siren", 4024),
                ("wait", 1200), ("follow", "caged_siren")]),

    # Shadowsong Shrine: the old flowers at the broken pillar (2.22), and the fresh ones she lays
    dict(key="shrine_ruin", model=RUIN, name="Broken Pillar", at="pillar", kind="doodad", scale=0.6, facing=2.0, phase=HUB),
    dict(key="old_flowers", model=FLOWERS_OLD, name="Withered Flowers", kind="use", quest="ch2_flowers", consumable=False,
         scale=1.2, at="flowers", goal="The flowers at the pillar looked at", phase=HUB,
         beats=[("sound", "player", 1187), ("summon", "shaelyn", "shaelyn_trees", 70), ("wait", 1500),
                ("move", "shaelyn", "shaelyn_kneel", "walk"), ("wait", 11000), ("state", "shaelyn", "kneel"),
                ("object", "new_flowers", "fresh_flowers", 300), ("wait", 4000), ("state", "shaelyn", "none"),
                ("face", "shaelyn", "player"), ("emote", "shaelyn", "exclamation"), ("wait", 1200),
                ("state", "shaelyn", "ready_bow"), ("sound", "shaelyn", 1144), ("wait", 6000),
                ("state", "shaelyn", "none"), ("wait", 1500), ("move", "shaelyn", "shaelyn_away", "walk"), ("wait", 14000),
                ("despawn", "shaelyn")]),
    dict(key="new_flowers", model=FLOWERS_NEW, name="Fresh Flowers", kind="doodad", scale=1.0),

    # -- memory m2: the camp's fire, the satyrs' stores (pitch), the Watchers' arrows on the trail ----------------------
    dict(key="m2_campfire", model="campfire", name="Campfire", at="m2_fire", kind="doodad", phase=M2),
    dict(key="m2_barrels", model="barrel", name="Pitch Barrels", at="stores", kind="doodad", scale=1.1, phase=M2),
    dict(key="satyr_stores", model="crate", name="Satyr Stores", kind="loot", loot=[("pitch_pot", 1, 2)], quest="ch2_pitch",
         respawn=20, phase=M2, at=["store_1", "store_2", "store_3", "store_4", "store_5", "store_6"]),
    dict(key="arrow", model=ARROW, name="Watcher's Arrow", kind="loot", loot=[("watcher_arrow", 1, 1)], quest="ch2_arrows",
         scale=1.6, respawn=20, phase=M2, at=["a_1", "a_2", "a_3", "a_4", "a_5", "a_6", "a_7", "a_8"]),

    # -- memory m2b: Nendis, its houses, docks, lamps and bell, three boats in the harbour ------------------------------
    dict(key="ne_house", model=NE_HOUSE, name="House of Nendis", at=["house_1", "house_2", "house_3"], kind="doodad",
         facing=1.6, phase=M2B),
    dict(key="burning_house", model=NE_HOUSE, name="House of Nendis", at="house_burn", kind="doodad", facing=1.0, phase=M2B),
    dict(key="ne_tent", model=NE_TENT, name="Tent", at="fire_town_3", kind="doodad", facing=1.4, phase=M2B),
    dict(key="ne_lamp", model=NE_LAMP, name="Street Lamp", at=["lamp_1", "lamp_2", "lamp_3", "lamp_4"], kind="doodad",
         phase=M2B),
    dict(key="ne_banner", model=NE_BANNER, name="Banner of Nendis", at="banner", kind="doodad", facing=4.7, phase=M2B),
    dict(key="ne_crates", model=NE_CRATE, name="Crates", at="crates_dock", kind="doodad", phase=M2B),
    dict(key="ne_barrels", model=NE_BARREL, name="Barrels", at="barrels_dock", kind="doodad", phase=M2B),
    dict(key="harbour_bell", model=BELL, name="Harbour Bell", at="bell", kind="doodad", facing=4.7, phase=M2B),
    dict(key="dock", model=DOCK, name="Dock", at=["dock_1", "dock_2"], kind="doodad", facing=4.7, phase=M2B),
    dict(key="boat", model=SHIP, name="Ship of Nendis", at=["ship_1", "ship_2", "ship_3"], kind="doodad", scale=1.5,
         facing=4.4, phase=M2B),
    dict(key="rig_1", model="naga_crate", name="Ship's Rigging", kind="use", quest="ch2_ships", consumable=False, scale=0.7,
         at="rig_1", goal="The first ship burning", phase=M2B,
         beats=[("take", "pitch_pot", 1), ("summon", "ship_fire", "fire_1", 300), ("summon", "ship_fire", "fire_2", 300),
                ("sound", "player", 10947), ("wait", 600), ("sound", "bellringer", 6674), ("emote", "bellringer", "exclamation"),
                ("wait", 1500), ("sound", "watchman", 7054), ("move", "watchman", "watchman_run", "run")]),
    dict(key="rig_2", model="naga_crate", name="Ship's Rigging", kind="use", quest="ch2_ships", consumable=False, scale=0.7,
         at="rig_2", goal="The second ship burning", phase=M2B,
         beats=[("take", "pitch_pot", 1), ("summon", "ship_fire", "fire_3", 300), ("summon", "ship_fire", "fire_4", 300),
                ("sound", "player", 10947), ("wait", 600), ("sound", "bellringer", 6674), ("wait", 900),
                ("sound", "bellringer", 6674), ("sound", "player", 14987)]),
    dict(key="rig_3", model="naga_crate", name="Ship's Rigging", kind="use", quest="ch2_ships", consumable=False, scale=0.7,
         at="rig_3", goal="The third ship burning", phase=M2B,
         beats=[("take", "pitch_pot", 1), ("summon", "ship_fire", "fire_5", 300), ("summon", "ship_fire", "fire_6", 300),
                ("sound", "player", 10947), ("wait", 600), ("sound", "bellringer", 6674), ("wait", 700),
                ("sound", "bellringer", 6674), ("wait", 700), ("sound", "bellringer", 6674), ("sound", "player", 14556)]),
]

# -- items ---------------------------------------------------------------------------------------------------------------
ITEMS = [
    # what quests ask for and hand over
    dict(key="coral_cup", name="Vyssa's Coral Cup", kind="drink", level=15, icon=6652,
         description="Seawater, cold and clean, in a cup of red coral."),
    dict(key="coral_shard", name="Shard of Red Coral", icon=6652,
         description="Sharp along one edge. Ssaveth didn't say what for. He didn't need to."),
    dict(key="living_coral", name="Living Coral", icon=6652, stack=8, description="Still warm with the reef's colour."),
    dict(key="sea_jug", name="Jug of Open-Sea Water", icon=18102, stack=5, description="Clear and cold, from beyond the reef."),
    dict(key="nendis_pearl", name="Song-Pearl: The Port of Nendis", icon="pearl",
         description="Hold it to your ear: smoke, and a bell, and someone singing under it."),
    dict(key="watcher_arrow", name="Watcher's Arrow", icon="item:2512", stack=6,
         description="Night elf fletching. Fresh."),
    dict(key="pitch_pot", name="Pot of Pitch", icon=22927, stack=8, description="It sticks to everything. Everything."),
    dict(key="raider_trident", name="Spitelash Trident", icon="trident", stack=10),
    dict(key="snapper", name="Southfury Snapper", icon=24702, stack=8, description="It bites even now."),
    dict(key="strongbox", name="Kurll's Strongbox", icon=12644, carry="heavy_box",
         description="Heavy. It clinks. It belongs to an orc with a very large cleaver."),
    dict(key="vessk_sigil", name="Vessk's Sigil", icon=7246,
         description="The Empress's sigil in gold, worn on a hunt-captain's harness."),
    dict(key="bay_fish", name="Bay Bream", icon="fish", stack=10),

    # rewards (the game's quests' greens at these levels; food at 15)
    dict(key="vyssa_stew", name="Vyssa's Coral-Pot Stew", kind="food", level=15, icon=24702),
    dict(key="snapper_stew", name="Kurll's Snapper Stew", kind="food", level=15, icon=24702),
    dict(key="hunter_grips", name="Tide-Broken Grips", kind="armor:mail:hands", quality=2, level=15,
         stats=[("str", 4), ("sta", 3)]),
    dict(key="hunter_gloves", name="Tide-Broken Gloves", kind="armor:leather:hands", quality=2, level=15,
         stats=[("agi", 4), ("sta", 3)]),
    dict(key="hunter_wraps", name="Tide-Broken Handwraps", kind="armor:cloth:hands", quality=2, level=15,
         stats=[("int", 4), ("spi", 3)]),
    dict(key="road_boots", name="Bay Road Sabatons", kind="armor:mail:feet", quality=2, level=16,
         stats=[("str", 4), ("sta", 4)]),
    dict(key="road_treads", name="Bay Road Treads", kind="armor:leather:feet", quality=2, level=16,
         stats=[("agi", 4), ("sta", 4)]),
    dict(key="road_slippers", name="Bay Road Slippers", kind="armor:cloth:feet", quality=2, level=16,
         stats=[("int", 4), ("spi", 3), ("sta", 1)]),
    dict(key="pitch_spaulders", name="Pitch-Stained Spaulders", kind="armor:mail:shoulder", quality=2, level=16,
         stats=[("str", 5), ("sta", 3)]),
    dict(key="pitch_pads", name="Pitch-Stained Shoulderpads", kind="armor:leather:shoulder", quality=2, level=16,
         stats=[("agi", 5), ("sta", 3)]),
    dict(key="pitch_mantle", name="Pitch-Stained Mantle", kind="armor:cloth:shoulder", quality=2, level=16,
         stats=[("int", 5), ("spi", 3)]),
    dict(key="valormok_cleaver", name="Valormok Cleaver", kind="weapon:axe", quality=2, level=17,
         stats=[("str", 5), ("sta", 4)]),
    dict(key="grunt_shank", name="Grunt's Shank", kind="weapon:dagger", quality=2, level=17, stats=[("agi", 5), ("sta", 3)]),
    dict(key="kodo_staff", name="Kodo-Bone Staff", kind="weapon:staff", quality=2, level=17,
         stats=[("int", 7), ("spi", 5), ("sta", 2)]),
    dict(key="ember_legguards", name="Ember-Scarred Legguards", kind="armor:mail:legs", quality=2, level=18,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="ember_leggings", name="Ember-Scarred Leggings", kind="armor:leather:legs", quality=2, level=18,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="ember_trousers", name="Ember-Scarred Trousers", kind="armor:cloth:legs", quality=2, level=18,
         stats=[("int", 6), ("spi", 5)]),
    dict(key="vessk_trident", name="Vessk's Trident", kind="weapon:spear", quality=2, level=19,
         stats=[("str", 9), ("sta", 6)], description="Taken from a hunt-captain who won't be needing it."),
    dict(key="vessk_dirk", name="Hunt-Captain's Dirk", kind="weapon:dagger", quality=2, level=19,
         stats=[("agi", 5), ("sta", 4)]),
    dict(key="vessk_rod", name="Vessk's Net-Staff", kind="weapon:staff", quality=2, level=19,
         stats=[("int", 8), ("spi", 6), ("sta", 2)]),
    dict(key="kelp_band", name="Kelp-Wrapped Band", kind="ring", quality=2, level=19, stats=[("sta", 3), ("spi", 3)],
         description="Vyssa tied it from the kelp that covered a stranger."),
    dict(key="hollow_cloak", name="Hollow-Woven Cloak", kind="armor:cloth:back", quality=2, level=19,
         stats=[("sta", 4), ("agi", 3)]),
    dict(key="keeper_pendant", name="Keeper's Pearl Pendant", kind="neck", quality=2, level=19,
         stats=[("int", 4), ("sta", 3)], description="A pearl that never held a song, on a string Isshara knotted blind."),
    dict(key="tidebreaker_band", name="Tidebreaker Band", kind="ring", quality=2, level=19, stats=[("str", 4), ("sta", 3)]),
]

# -- auras ---------------------------------------------------------------------------------------------------------------
AURAS = [
    # the sigil scratched out (2.02): chapter 1's Tide-Sworn comes off, this goes on
    dict(key="tide_broken", name="Tide-Broken", kind="mark", seconds=0, icon=772,
         text="Where the Empress's sigil was, a scratch of red coral. Your tide is no one's but your own."),
    dict(key="scratched", name="Scratched Scales", kind="stun", seconds=1, icon=772, visual=121, text="It stings."),
    dict(key="plucked", name="Plucked", kind="stun", seconds=1, icon=772, text="A scale, for a buyer in Orgrimmar."),
    dict(key="song_touch", name="The Keeper's Song", kind="mark", seconds=4, icon=12508, visual=6589,
         text="The water round your hands is singing."),
    dict(key="heavy_box", name="Heavy Strongbox", kind="slow", percent=25, seconds=0, icon=46340,
         text="It clinks with every slither."),
]

# -- memories ------------------------------------------------------------------------------------------------------------
MEMORIES = [
    dict(key="m2", name="The Road to Nendis", whose="Isshara", bit="A",
         text="Isshara's memory: the morning after the Awakening, and the march to the sea. What she saw, you see.",
         stage="m2_stage", facing=4.4, centre="m2_centre", radius=300, pool="pool_shore", pool_facing=5.0,
         singer="ch0:isshara", again="Sing the road again. Take me back to the column."),
    dict(key="m2b", name="The Port of Nendis", whose="Isshara", bit="A",
         text="Isshara's memory: the night the naga burned Nendis. What she saw, you see.",
         stage="m2b_stage", facing=1.9, centre="m2b_centre", radius=150, pool="pool_shore", pool_facing=5.0,
         singer="ch0:isshara", again="Sing Nendis again."),
]

# -- quests ----------------------------------------------------------------------------------------------------------------
QUESTS = [
    # 2.01: the Hollow (the camp shows itself to the newcomer at the reward: the hub's phase begins with it)
    dict(key="ch2_arrival", title="The Hollow", giver="ch0:szaria", ender="ch0:szaria", level=15, xp=8, tone="serious",
         prev="ch1:ch1_end", event="Welcomed at the Hollow",
         goal="Stand with Lady Szaria on the Hollow's sand while the Tide-Broken come up out of the water to look at you.",
         text="Stand still. Let me look at you. Thin. Scared. The Matron's sigil still on your shoulder, shining like a "
              "lamp for anyone who wants to find us. And you carried the keeper out on your back. Well. My people will "
              "want to see you before they let you see them. Don't move.",
         progress="Still. They're looking.",
         reward="They've seen you. Now see them. This is the Hollow, little tide-runner: a sandbar, a fire, and everyone "
                "the Empress threw away. Nobody here owns you. Nobody here will feed you either, unless you work.",
         details=["talk"], reward_emotes=["talk", "roar"],
         accept=[("face", "self", "player"), ("state", "self", "none"), ("emote", "self", "talk"), ("wait", 2500),
                 ("face", "self", "hollow_east"), ("wait", 2500), ("face", "self", "player"),
                 ("summon", "ssaveth_greet", "rise_ssaveth", 60), ("sound", "self", "splash_big"), ("wait", 800),
                 ("move", "ssaveth_greet", "behind_szaria", "walk"), ("wait", 4500),
                 ("say", "ssaveth_greet", "From the murky depths I come.", None, "NagaMyrmadonReady1"), ("wait", 3000),
                 ("summon", "isshara_carried", "rest", 60), ("summon", "bearer", "rest_bearer_1", 45),
                 ("summon", "bearer", "rest_bearer_2", 45), ("sound", "self", "splash"), ("wait", 1500),
                 ("summon", "vyssa_greet", "rise_vyssa", 60), ("sound", "self", "splash"), ("wait", 600),
                 ("move", "vyssa_greet", "szaria_front", "walk"), ("wait", 7000), ("face", "vyssa_greet", "player"),
                 ("emote", "vyssa_greet", "work"), ("give", "coral_cup", 1), ("sound", "vyssa_greet", "pickup_water"),
                 ("wait", 1500), ("say", "vyssa_greet", "Drink. Slowly. You'll want it to last.", "talk"), ("wait", 2500),
                 ("move", "bearer", "rest_step_1", "walk"), ("wait", 2500), ("move", "bearer", "rest_step_2", "walk"),
                 ("wait", 2500), ("move", "bearer", "rest_step_3", "walk"), ("wait", 2000),
                 ("credit", "ch2_arrival")],
         complete=[("despawn", "ssaveth_greet"), ("despawn", "vyssa_greet"), ("despawn", "isshara_carried"),
                   ("despawn", "bearer"), ("sound", "self", "splash_big"), ("wait", 1500), ("emote", "self", "roar"),
                   ("sound", "self", "siren_aggro"), ("wait", 1200), ("emote", "ch0:ssaveth", "roar"),
                   ("emote", "sentry", "roar"), ("emote", "recruit", "cheer")],
         poi=["hollow"]),

    # 2.02: scratch the sigil
    dict(key="ch2_sigil", title="Scratch the Sigil", giver="ch0:ssaveth", ender="ch0:ssaveth", level=15, xp=8,
         tone="serious", prev="ch2_arrival", source="coral_shard", objects=[("still_pool", 1)],
         goal="Take the Shard of Red Coral to the still tide pool at the Hollow's north-east edge, where you can see your "
              "own shoulder in the water, and scratch the Empress's sigil off your scales.",
         text="That mark on your shoulder. Every one of us wore it. Every one of us took it off the same way: with a piece "
              "of the reef, at the still pool, looking at it. Not quickly. You look at it while you do it. That's the "
              "whole of it.",
         progress="It's still there. I can see it from here.",
         reward="Good. Now it's a scar. A scar is yours. The sigil was hers.",
         details=["talk"], reward_emotes=["roar"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "none"),
                 ("face", "self", "mirror"), ("emote", "self", "spell"), ("wait", 2000), ("face", "self", "player"),
                 ("emote", "self", "roar"), ("wait", 1500), ("state", "self", "ready_thrown"), ("face", "self", "hollow_north")],
         complete=[("face", "self", "player"), ("wait", 1500), ("emote", "self", "talk"), ("wait", 1500),
                   ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 2000),
                   ("face", "self", "hollow_north")],
         poi=["mirror"]),

    # 2.03: a pool for the keeper (boring)
    dict(key="ch2_coral", title="A Pool for the Keeper", giver="ch0:vyssa", ender="ch0:vyssa", level=15, xp=8,
         tone="boring", prev="ch2_arrival", items=[("living_coral", 8)],
         goal="Bring Vyssa the Coral-Keeper 8 Living Coral from the reef in the shallows north-east of the Hollow.",
         text="She needs a pool. Not a puddle, a pool: ringed, still, kept. The stones I've got are dead coral, and dead "
              "coral doesn't hold a song, so she tells me. Living coral, off the reef north-east of us. Eight pieces. Pick "
              "the red ones. The grey ones are sulking.",
         progress="I've got the ring started. Ring, but no coral. It's a very sad ring.",
         reward="Oh, these are good. Feel that? Warm. Here. Sit while I set them, there's stew if you don't ask what's "
                "in it.",
         details=["talk", "work"], reward_emotes=["talk"], rewards=["vyssa_stew"],
         accept=[("state", "self", "none"), ("move", "self", "pool_shore", "walk"), ("wait", 9000), ("face", "self", "pool"),
                 ("state", "self", "work"), ("wait", 1500), ("say", "self", "Eight. Red ones. And mind the eels.", "talk"),
                 ("state", "ch0:isshara", "none"), ("face", "ch0:isshara", "pool"), ("wait", 1500),
                 ("cast", "ch0:isshara", 36005, "self"), ("wait", 4000), ("state", "self", "none"), ("move", "self", "vyssa", "walk"),
                 ("wait", 9000), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("move", "self", "pool_shore", "walk"), ("wait", 8000), ("face", "self", "pool"),
                   ("emote", "self", "work"), ("object", "living_coral_set", "ring_n", 600), ("wait", 1500),
                   ("face", "ch0:isshara", "ring_n"), ("emote", "self", "work"), ("object", "living_coral_set", "ring_e", 600),
                   ("wait", 1500), ("face", "ch0:isshara", "ring_e"), ("emote", "self", "work"),
                   ("object", "living_coral_set", "ring_s", 600), ("wait", 1500), ("face", "ch0:isshara", "ring_s"),
                   ("emote", "self", "work"), ("object", "living_coral_set", "ring_w", 600), ("cast", "keepers_pool", 57771, "self"),
                   ("wait", 2000), ("move", "self", "vyssa", "walk"), ("wait", 9000), ("state", "self", "work")],
         poi=["reef"]),

    # 2.04: seawater for song (boring): she tastes the pool as it fills, and only the last jug makes it right
    dict(key="ch2_seawater", title="Seawater for Song", giver="ch0:isshara", ender="ch0:isshara", level=15, xp=8,
         tone="boring", prev="ch2_arrival", items=[("sea_jug", 5)],
         goal="Fill 5 jugs at the clean springs on the floor of the open sea south-east of the Hollow, beyond the reef, and "
              "bring them to Isshara at her pool.",
         text="Water near a camp tastes of the camp: smoke, fish, feet. A song sinks in water like that and comes up "
              "tasting of feet. Go out past the reef, where the floor drops away, and fill the jugs where the springs come "
              "up clean. Five. I'll know if you cheat.",
         progress="I can smell the camp on that. Further out.",
         reward="There. Now it's a pool. Now it remembers it was the sea. Sit by it with me a while. I'll tell you when "
                "it's ready to sing.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "open_sea"),
                 ("emote", "self", "spell"), ("wait", 1800), ("visual", "self", 36005), ("sound", "self", "pickup_water"),
                 ("wait", 1500), ("face", "self", "pool")],
         complete=[("state", "self", "none"), ("face", "self", "pool"), ("emote", "ch0:vyssa", "work"),
                   ("sound", "keepers_pool", 1215), ("cast", "keepers_pool", 36005, "self"), ("wait", 1200),
                   ("visual", "self", 36005), ("wait", 1000), ("face", "self", "hollow_west"), ("wait", 2000),
                   ("face", "self", "pool"), ("sound", "keepers_pool", 1215), ("cast", "keepers_pool", 36005, "self"), ("wait", 1200),
                   ("visual", "self", 36005), ("wait", 1000), ("face", "self", "hollow_south"), ("wait", 2000),
                   ("face", "self", "pool"), ("sound", "keepers_pool", 1215), ("cast", "keepers_pool", 36005, "self"), ("wait", 1200),
                   ("visual", "self", 36005), ("wait", 1000), ("face", "self", "hollow_west"), ("wait", 2000),
                   ("face", "self", "pool"), ("sound", "keepers_pool", 1215), ("cast", "keepers_pool", 36005, "self"), ("wait", 1200),
                   ("visual", "self", 36005), ("wait", 1000), ("face", "self", "hollow_north"), ("wait", 2000),
                   ("face", "self", "pool"), ("sound", "keepers_pool", 1215), ("cast", "keepers_pool", 47479, "self"), ("wait", 1500),
                   ("visual", "self", 36005), ("wait", 2500), ("state", "self", "channel"), ("cast", "keepers_pool", 57771, "self"),
                   ("sound", "self", "siren_hiss"), ("wait", 4000), ("state", "self", "none")],
         poi=["open_sea"]),

    # 2.05: Spitelash hunters on the north strand
    dict(key="ch2_hunters", title="Spitelash Hunters", giver="ch0:ssaveth", ender="ch0:ssaveth", level=15, xp=8,
         tone="serious", prev="ch2_sigil", kill=[("tide_hunter", 10)],
         goal="Kill 10 Spitelash Tide-Hunters searching the north strand and the rocky islet under the cliffs, north of "
              "the Hollow.",
         text="They're looking for the keeper. Here: the Hollow. Here: the north strand, under the cliffs. They come along "
              "the strand every tide, poking in the rocks. Sooner or later one of them looks south. Ten of them. Before "
              "one of them looks south.",
         progress="I counted the ones who came back along the strand. Too many came back.",
         reward="Ten. The strand will be quiet a while. Quiet doesn't last, but it'll do. Take something to keep your "
                "hands whole.",
         details=["talk", "battle_roar"], reward_emotes=["roar"], choice=["hunter_grips", "hunter_gloves", "hunter_wraps"],
         accept=[("state", "self", "none"), ("move", "self", "ssaveth_sand", "walk"), ("wait", 5000),
                 ("face", "self", "sand_mark"), ("emote", "self", "work"), ("object", "sand_mark", "sand_mark", 40),
                 ("wait", 1500), ("emote", "self", "work"), ("object", "sand_line", "sand_mark", 40), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "sand_mark"),
                 ("emote", "self", "attack2h"), ("sound", "self", 977), ("wait", 1200), ("face", "self", "north_shore"),
                 ("emote", "self", "spell"), ("wait", 2000), ("move", "self", "ssaveth", "walk"), ("wait", 5000),
                 ("state", "self", "ready_thrown"), ("face", "self", "hollow_north")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500),
                   ("emote", "self", "attack2h"), ("sound", "self", 977), ("wait", 1500), ("emote", "self", "roar"),
                   ("wait", 1500), ("state", "self", "ready_thrown"), ("face", "self", "hollow_north")],
         poi=["north_shore"]),

    # 2.06: the Nendis pearl (the courier and his escort on the bay road)
    dict(key="ch2_courier", title="The Nendis Pearl", giver="ch0:szaria", ender="ch0:isshara", level=16, xp=8,
         tone="serious", prev="ch2_hunters", prev_any=["ch2_coral", "ch2_seawater"], kill=[("courier", 1)],
         items=[("nendis_pearl", 1)], drops={"nendis_pearl": [("courier", 100)]},
         goal="Kill the Spitelash Courier at his halt on the bay road, on the bay's west shore across the water from the "
              "Hollow, and take Isshara the song-pearl he carries.",
         text="See it? Out there, west, moving. A lantern on the water. That's a Spitelash courier, and the hunters say he "
              "carries a pearl for Lady Sesspira at the ruins. One of Isshara's. They took everything she was and now they "
              "pass it round like a jar of salt. He'll halt on the bay road tonight, on the west shore. Take it back.",
         progress="The light's gone round the point. He'll stop for the night. Couriers always do.",
         reward="...I know this one. Before you're halfway across the sand I know it. Give it here. Listen. Smoke. A bell. "
                "My own voice, younger than yours. The Port of Nendis.",
         details=["talk", "spell"], reward_emotes=["talk"], choice=["road_boots", "road_treads", "road_slippers"],
         accept=[("face", "self", "hollow_west"), ("summon", "courier_light", "far_light_a", 40), ("wait", 1500),
                 ("move", "courier_light", "far_light_b", "walk"), ("wait", 1000), ("emote", "self", "spell"),
                 ("visual", "self", 32992), ("wait", 2500), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 2500), ("face", "self", "hollow_west")],
         complete=[("face", "self", "player"), ("emote", "self", "spell"), ("wait", 1500), ("state", "self", "channel"),
                   ("visual", "self", 36005), ("wait", 2500), ("say", "self", "The Port of Nendis.", "talk"), ("music", 9462),
                   ("wait", 2500), ("state", "self", "none")],
         poi=["courier"]),

    # 2.07: too bright (the first song: dawn on Legash, the line's first laugh)
    dict(key="ch2_bright", title="Too Bright", giver="ch0:isshara", ender="ch0:isshara_young", level=16, xp=8,
         tone="funny", prev="ch2_courier", memory="m2", explore="m2_camp", radius=14,
         goal="Touch the water while Isshara sings. In her memory, follow the satyr and the naga column north across "
              "Legash's plateau to the satyrs' camp, where young Isshara waits.",
         text="The morning after he called us up. We'd never seen a sun. Ten thousand years under the water, and then "
              "that. Hands in the pool, little one. You'll want to squint.",
         progress="North. Follow the goat-legs. Everyone else is.",
         reward="There you are! Did you hear her? 'Fresh air is irritating my eyes.' The whole column heard. Lady Vashj, "
                "the terror of the deep, sniffing at the sunrise. Don't tell her I laughed.",
         details=["talk"], reward_emotes=["laugh", "point"],
         accept=[("face", "self", "pool"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("sound", "self", "siren_hiss"), ("music", 9461), ("cast", "keepers_pool", 57771, "self"),
                 ("aura", "player", "song_touch"), ("wait", 3500), ("relive", "m2"), ("wait", 2000), ("state", "self", "none")],
         complete=[("emote", "self", "laugh"), ("wait", 1500), ("face", "self", "m2_sun"), ("emote", "self", "point"),
                   ("wait", 1500), ("face", "self", "player"), ("emote", "self", "laugh")],
         poi=["m2_camp"]),

    # 2.08: maddened kin (the furbolgs of Ursolan, fel in their eyes)
    dict(key="ch2_furbolgs", title="Maddened Kin", giver="ch0:isshara_young", ender="ch0:isshara_young", level=16, xp=8,
         tone="serious", prev="ch2_bright", memory="m2", kill=[("furbolg", 8)],
         goal="In Isshara's memory, kill 8 Maddened Furbolgs in the woods west of the satyrs' camp.",
         text="The bear-people. They came down out of Ursolan in the night with green fire in their eyes, and they don't "
              "stop when they're hurt. The goat-legs say it's the Legion's sickness. The goat-legs say a lot of things.",
         progress="Listen. Still howling.",
         reward="It's over. It wasn't them, you know. Something got into them. Something gets into everyone, in the end.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "woods"), ("emote", "self", "point"), ("wait", 1500), ("emote", "camp_satyr", "laugh"),
                 ("sound", "camp_satyr", 1011), ("wait", 1500), ("face", "self", "satyr_a"), ("wait", 2000),
                 ("face", "self", "player"), ("emote", "self", "no")],
         complete=[("face", "self", "woods"), ("wait", 1500), ("emote", "camp_satyr", "laugh"), ("sound", "camp_satyr", 6335),
                   ("wait", 1500), ("face", "self", "m2_fire"), ("emote", "self", "cry"), ("wait", 2500),
                   ("face", "self", "player")],
         poi=["woods"]),

    # 2.09: arrows on the trail (someone hunts the column)
    dict(key="ch2_arrows", title="Arrows on the Trail", giver="ch0:isshara_young", ender="ch0:isshara_young", level=16,
         xp=8, tone="serious", prev="ch2_bright", memory="m2", items=[("watcher_arrow", 6)],
         goal="In Isshara's memory, gather 6 Watcher's Arrows along the trail behind the column, between the rim of the "
              "gorge and the satyrs' camp.",
         text="The rearguard says arrows. Stuck in the trail behind us, in the trees, in a satyr who won't stop "
              "complaining about it. Somebody's following the column. Go back along the trail and bring me what they "
              "left. I want to smell them.",
         progress="Six. Bring them here.",
         reward="Moonwood shafts. Owl feathers. Night elves. Hunters, and patient ones. They're a day behind us, no more.",
         details=["talk"], reward_emotes=["question", "talk"],
         accept=[("face", "self", "trail"), ("wait", 2000), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "question"), ("wait", 1500), ("say", "self", "Night elves.", "talk"), ("wait", 2000),
                   ("face", "self", "m2_stage"), ("wait", 7000), ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["trail"]),

    # 2.10: the berserk wildkin (Vashj, passing below, staggers it with one bolt and doesn't look up)
    dict(key="ch2_wildkin", title="The Berserk Wildkin", giver="ch0:isshara_young", ender="ch0:isshara_young", level=16,
         xp=8, tone="serious", prev=["ch2_furbolgs", "ch2_arrows"], memory="m2", kill=[("wildkin", 1)],
         goal="In Isshara's memory, kill the Berserk Wildkin that blocks the pass south-east of the satyrs' camp, toward "
              "the Bitter Reaches.",
         text="The pass to the east coast is shut. A wildkin, the big owl-folk, standing in it screaming at the sky. It's "
              "taken the same sickness as the bears. The column can't go round. Make it stop screaming.",
         progress="I can still hear it. Everyone can still hear it.",
         reward="Did you see her? One bolt, and she never even looked up. That's our Lady. Everything is beneath her, "
                "and most of it is.",
         details=["talk", "point"], reward_emotes=["laugh"],
         accept=[("face", "self", "pass"), ("emote", "self", "point"), ("wait", 1500), ("sound", "self", 3605),
                 ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "laugh"), ("wait", 1500), ("face", "self", "pass"), ("emote", "self", "salute"),
                   ("wait", 2000), ("face", "self", "player")],
         poi=["pass"]),

    # 2.11: pitch for the ships (boring): the satyrs sing as they work; the song stops in the middle, and you wake
    dict(key="ch2_pitch", title="Pitch for the Ships", giver="ch0:isshara_young", ender="ch0:isshara", level=16, xp=8,
         tone="boring", prev="ch2_wildkin", memory="m2", wake=True, items=[("pitch_pot", 8)],
         goal="In Isshara's memory, collect 8 Pots of Pitch from the satyrs' stores by their quartermaster at the camp.",
         text="Pitch. Pots of it. The goat-legs carry it for something the master wants burned when we reach the sea, "
              "and the master doesn't tell us what. Their quartermaster will hand it out. He'll grin while he does it. "
              "Try not to look at his teeth.",
         progress="Eight pots. The satyrs are singing again. Don't sing along.",
         reward="...I'm sorry. I'm sorry, little one. I stopped. I couldn't... the next part is the sea, and the town on "
                "the sea, and I can't. Not yet. Not tonight.",
         details=["talk"], reward_emotes=["talk"], choice=["pitch_spaulders", "pitch_pads", "pitch_mantle"],
         accept=[("face", "self", "stores"), ("emote", "self", "point"), ("wait", 1500), ("emote", "quartermaster", "laugh"),
                 ("sound", "quartermaster", 6517), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("state", "self", "stun"), ("visual", "self", 36005), ("wait", 2500),
                   ("say", "self", "Not yet.", "talk"), ("wait", 2000), ("state", "self", "none"), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water"), ("wait", 1500), ("face", "self", "hollow_east")],
         poi=["stores"]),

    # 2.12: an arrow in the crest (the envoy's return; Valormok's grunts at the east approach; the chief looks)
    dict(key="ch2_arrow", title="An Arrow in the Crest", giver="ch0:szaria", ender=AGTOR, level=17, xp=8, tone="funny",
         prev="ch2_pitch",
         interact=[("gate_grunt", "Show him your empty hands.")], interact_goal="Valormok's grunts faced",
         interact_beats=[("face", "self", "player"), ("emote", "self", "rude"),
                         ("yell", "self", "Another fish-face! Turn around and swim, or I'll wear your tail for a belt!",
                          "shout"),
                         ("state", "gate_grunt_b", "ready"), ("state", "gate_grunt_c", "ready"), ("emote", "gate_grunt_c", "roar"),
                         ("wait", 2500),
                         ("say", "gate_grunt_b", "Look at it. It's got hair. Fish don't have hair.", "point"), ("wait", 2500),
                         ("emote", "self", "shout"), ("yell", "self", "Chief! The snakes are back!", "shout"), ("wait", 2000),
                         ("emote", AGTOR, "exclamation"), ("wait", 3500), ("face", "self", "agtor"), ("wait", 2000),
                         ("state", "gate_grunt_b", "none"), ("state", "gate_grunt_c", "none"), ("face", "self", "player"),
                         ("say", "self", "The chief's looking at you. Go on, then. Slowly.", "talk"),
                         ("move", "self", "gate_aside", "walk"), ("move", "gate_grunt_b", "gate_aside_2", "walk"),
                         ("wait", 9000), ("move", "self", "gate_grunt", "walk"), ("move", "gate_grunt_b", "gate_grunt_2", "walk")],
         goal="Go to Valormok, the orcs' camp on the hills west of the bay, face the grunts at its east approach, and speak "
              "to Ag'tor Bloodfist.",
         text="I sent an envoy to the orcs at Valormok. With an open shell, and our word, and good manners. This is what "
              "came back. Look at him. He hasn't noticed. Nobody tell him. The orcs are the only neighbours we have who "
              "aren't the Empress's, and I'm not sending him twice. You go.",
         progress="",
         reward="So. The snakes send a whelp this time. Last one had an arrow in his hat and didn't notice. You notice "
                "things? Good. I am Ag'tor. This is my camp. Speak, and speak short.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("summon", "envoy", "envoy", 50), ("wait", 800), ("aura", "envoy", 52627), ("face", "self", "envoy_look"),
                 ("wait", 2000), ("face", "ch0:ssaveth", "envoy"), ("face", "ch0:vyssa", "envoy"), ("face", "sentry", "envoy"),
                 ("wait", 3000), ("emote", "envoy", "talk"), ("wait", 1500), ("state", "ch0:vyssa", "none"),
                 ("move", "ch0:vyssa", "envoy_look", "walk"), ("wait", 7500), ("face", "ch0:vyssa", "envoy"),
                 ("emote", "ch0:vyssa", "work"), ("wait", 800), ("unaura", "envoy", 52627), ("emote", "envoy", "wound"),
                 ("sound", "envoy", "naga_wound"),
                 ("wait", 1500), ("say", "envoy", "I can't smell... I bit my tongue.", None, "NagaMyrmadonPissed3"),
                 ("wait", 3500), ("emote", "ch0:ssaveth", "roar"), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 2000), ("move", "ch0:vyssa", "vyssa", "walk"), ("despawn", "envoy")],
         complete=[], poi=["gate_grunt"]),

    # 2.13: proof for Ag'tor (hero): the raiders on the west road; he counts the tridents on his fingers
    dict(key="ch2_raiders", title="Proof for Ag'tor", giver=AGTOR, ender=AGTOR, level=17, xp=8, tone="serious",
         path="hero", prev="ch2_arrow", rep=[(76, 250)], items=[("raider_trident", 10)],
         drops={"raider_trident": [("raider", 100)]},
         goal="Kill the Spitelash Raiders on Valormok's west road, down toward the Southfury, and bring Ag'tor Bloodfist "
              "10 Spitelash Tridents.",
         text="Your kind come up out of the river. Not yours. The other kind. They take my carts on the west road and "
              "they leave my carters for the crows. You want to talk to Ag'tor? Bring me tridents. Ten. Then we talk.",
         progress="I count tridents. I don't count words.",
         reward="One. Two. Three... ten. Ten tridents. Hm. Ten raiders who don't come up the river tomorrow. That is a "
                "beginning, snake. Not more.",
         details=["talk", "point"], reward_emotes=["point", "point", "point", "talk"],
         choice=["valormok_cleaver", "grunt_shank", "kodo_staff"], poi=["west_road"]),

    # 2.14: Jediga's sample (stupid): his runner measures, plucks; Jediga writes a price and crosses it out
    dict(key="ch2_scale", title="Jediga's Sample", giver=JEDIGA, ender=JEDIGA, level=17, xp=8, tone="stupid",
         prev="ch2_arrow", rep=[(76, 150)], money=900,
         interact=[("grukk", "Stand still for Grukk's measuring string.")], interact_goal="Measured, and one scale plucked",
         interact_beats=[("face", "self", "player"), ("emote", "self", "work"), ("wait", 1500),
                         ("say", "self", "Hold still. Grukk measures nose to tail.", "talk"), ("wait", 2000),
                         ("move", "self", "grukk_round", "walk"), ("wait", 3000), ("face", "self", "player"),
                         ("emote", "self", "work"), ("wait", 1500),
                         ("say", "self", "Turn round. No, other round. Round the way with the tail.", "point"), ("wait", 2500),
                         ("emote", "self", "attack"), ("aura", "player", "plucked"), ("sound", "player", "naga_wound"),
                         ("wait", 1500), ("emote", "self", "cheer"), ("say", "self", "Got one! Shiny!", "talk"),
                         ("move", "self", "grukk_jediga", "run"), ("wait", 2500), ("emote", "self", "bow"),
                         ("emote", JEDIGA, "talk"), ("wait", 3000), ("move", "self", "grukk", "walk")],
         goal="Let Jediga's runner, Peon Grukk, take a naga scale for Jediga's buyer in Orgrimmar, then see Jediga.",
         text="A buyer in Orgrimmar pays good gold for curiosities. A living naga scale? Very curious. Very good gold. "
              "Grukk will take the sample. He has a string. Stand still for him, it hardly hurts. Then I pay you. Fairly. "
              "Mostly.",
         progress="Has Grukk measured you? He measures everything. Once he measured the wind rider.",
         reward="Ah! Look at it, in the light. Blue. Green. Blue again. This is worth... this much. No. Less. The light "
                "out here is very flattering. This much. Take it before I look again.",
         details=["talk", "point"], reward_emotes=["point", "talk", "no", "talk"], poi=["grukk"]),

    # 2.15a: Kurll's larder (hero): out with the grey stew, in with the snappers; the grunts line up
    dict(key="ch2_larder", title="Kurll's Larder", giver=KURLL, ender=KURLL, level=17, xp=8, tone="funny", path="hero",
         exclusive=1, prev="ch2_arrow", rep=[(76, 250)], items=[("snapper", 8)],
         drops={"snapper": [("snapper", 80)]}, objects=[("stewpot", 1)],
         goal="Tip Kurll's grey stew out of his pot, and bring him 8 Southfury Snappers from the river below Valormok's "
              "west road.",
         text="Smell that. No. Smell it. That is stew. That is supposed to be stew. It has gone grey and the grunts know it. "
              "You swim. Go down to the river and bring me snappers, eight, fat ones. And tip that out on your way. I "
              "can't look at it.",
         progress="Still grey. The grunts are looking at me. The grunts are hungry.",
         reward="Snappers! In they go. In, in, all of them. Now that is a colour. Hear that? That's the line forming. That "
                "grunt is nodding at you. He doesn't nod at me.",
         details=["talk", "eat"], reward_emotes=["eat", "cheer"], rewards=["snapper_stew"],
         poi=["river", "stewpot"]),

    # 2.15b: Kurll's strongbox (menace): taken from behind him while he cooks
    dict(key="ch2_strongbox", title="Kurll's Strongbox", giver="ch0:vyssa", ender="ch0:vyssa", level=17, xp=8,
         tone="funny", path="menace", exclusive=1, prev="ch2_pitch", rep=[(76, -350)], money=3000,
         objects=[("strongbox_obj", 1)],
         goal="Take the strongbox from behind Kurll, Valormok's cook, while his back is turned, and bring it to Vyssa "
              "the Coral-Keeper at the Hollow.",
         text="Look in this jar. That's the camp's money. That's a shell, two buttons and a fish-hook. The orcs at Valormok "
              "have a cook who keeps his coin in a box behind him while he stirs, and he stirs a lot. I'm not saying. "
              "I'm only saying.",
         progress="Heavy, is it? Good. Heavy is good.",
         reward="Oh! Oh, that's a lot of coin. That's soup for a season. Don't tell Szaria where it came from. Don't tell "
                "Isshara either, she'll know anyway. Here, your share.",
         details=["talk", "work"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "work"), ("sound", "self", 120),
                 ("wait", 1500), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "hollow_west"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("take", "strongbox", 1), ("emote", "self", "work"), ("sound", "self", 1277),
                   ("wait", 1200), ("sound", "self", 120), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "hollow_west"),
                   ("wait", 1500), ("face", "self", "player"), ("state", "self", "work")],
         poi=["strongbox"]),

    # 2.16: the port of Nendis (the second song: the harbour asleep, from the reef)
    dict(key="ch2_port", title="The Port of Nendis", giver="ch0:isshara", ender="ch0:isshara_young", level=17, xp=8,
         tone="serious", prev=["ch2_raiders", "ch2_scale"], memory="m2b",
         explore="overlook", radius=10,
         goal="Touch the water while Isshara sings. In her memory, look over Nendis's harbour from the tip of the reef, "
              "then swim across to young Isshara by the docks.",
         text="I can sing the rest now. I think I can. It's the sea, and a town on the sea, and the night. Hands in the "
              "water. Stay by me. Whatever you see, it already happened.",
         progress="Look at it. Look at it while it's still there.",
         reward="Three ships. Lanterns. One old fool with a bell. They sleep. The whole town sleeps, and the Watchers "
                "are a day behind us on the road, and the master is already at sea. Here.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "pool"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("sound", "self", "siren_hiss"), ("music", 9461), ("cast", "keepers_pool", 57771, "self"),
                 ("aura", "player", "song_touch"), ("wait", 3500), ("relive", "m2b"), ("wait", 2000), ("state", "self", "none")],
         complete=[("face", "self", "ship_1"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "ship_2"),
                   ("emote", "self", "point"), ("wait", 1200), ("face", "self", "ship_3"), ("emote", "self", "point"),
                   ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["overlook"]),

    # 2.17: burning ships
    dict(key="ch2_ships", title="Burning Ships", giver="ch0:isshara_young", ender="ch0:isshara_young", level=18, xp=8,
         tone="serious", prev="ch2_port", memory="m2b",
         objects=[("rig_1", 1), ("rig_2", 1), ("rig_3", 1)],
         goal="In Isshara's memory, swim out to the 3 ships in Nendis's harbour and set each one's rigging alight with "
              "the pitch.",
         text="The master doesn't wish to be followed. Those are the only ships on this coast. Pitch on the rigging, "
              "fire after it. Quickly, before the old man with the bell wakes up.",
         progress="Burn them!",
         reward="Look at it. Look at the water burning. They'll see that from Darnassus.",
         details=["battle_roar"], reward_emotes=["battle_roar"],
         accept=[("give", "pitch_pot", 3), ("face", "self", "harbour"), ("summon", "column_a", "dock_watcher_1", 120),
                 ("summon", "column_c", "dock_watcher_2", 120), ("wait", 1200),
                 ("yell", "self", "Quickly, you fools! The ships must be burned. The master doesn't wish to be followed.",
                  "battle_roar"), ("emote", "column_a", "battle_roar"), ("emote", "column_c", "roar"), ("sound", "self", "siren_aggro"),
                 ("wait", 2500),
                 ("face", "self", "player"), ("emote", "self", "point")],
         complete=[("face", "self", "harbour"), ("emote", "self", "battle_roar"), ("sound", "self", "siren_aggro"),
                   ("wait", 1500), ("sound", "bellringer", 6674), ("wait", 2000), ("face", "self", "player"),
                   ("emote", "self", "laugh")],
         poi=["harbour"]),

    # 2.18: the warden comes (Maiev, untouchable; the Watchers on the docks)
    dict(key="ch2_watchers", title="The Warden Comes", giver="ch0:isshara_young", ender="ch0:isshara_young", level=18,
         xp=8, tone="serious", prev="ch2_ships", memory="m2b", kill=[("watcher", 8)],
         goal="In Isshara's memory, kill 8 Watchers on Nendis's docks and along its beach.",
         text="Horns on the road. Torches. Here they come, the hunters from the trail. Stand with me on the docks.",
         progress="More of them! Keep them off the docks!",
         reward="They're broken. The warden's gone after the master's sails, and good luck to her. She'll be chasing "
                "him for ten thousand more years.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("sound", "watchman", 7054), ("summon", "watcher", "dock_watcher_1", 240),
                 ("summon", "watcher", "dock_watcher_2", 240), ("summon", "watcher", "dock_watcher_3", 240),
                 ("wait", 1500),
                 ("say", "watcher", "There, mistress! Those must be the creatures we're after.", "point"), ("wait", 3500),
                 ("face", "self", "dock_watcher_1"),
                 ("yell", "self", "Wretched night elves, you are no match for the naga!", "battle_roar"), ("wait", 3500),
                 ("summon", "maiev", "maiev", 50), ("wait", 300), ("cast", "maiev", 51347, "self"),
                 ("yell", "maiev", "I am the hand of justice!", None, "MaievReady1"), ("wait", 3500),
                 ("yell", "maiev", "Naga? Many craven races have tempted our wrath over the centuries. None have survived!",
                  "talk"), ("wait", 6000),
                 ("say", "self", "Wretched woman. We will retake the surface world and put an end to your vile race once and "
                                 "for all.", "talk"), ("wait", 6000),
                 ("yell", "maiev", "I cannot allow Illidan to escape again! We must slay those naga before they burn the ships.",
                  "talk"), ("wait", 5500),
                 ("say", "self", "You are too late, little warden. The master has already set sail for distant shores. "
                                 "However, he wished to thank you for the hospitality you provided during his imprisonment. "
                                 "He asked us to repay you... in kind.", "talk"), ("wait", 8000),
                 ("cast", "maiev", 51347, "self"), ("despawn", "maiev")],
         complete=[("face", "self", "sea"), ("wait", 2000), ("emote", "self", "laugh"), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "roar")],
         poi=["m2b_isshara", "w_3"]),

    # 2.19: the burning house (a set piece: the girl Isshara carried out of Nendis)
    dict(key="ch2_house", title="The Burning House", giver="ch0:isshara_young", ender="ch0:isshara_young", level=18,
         xp=8, tone="serious", prev="ch2_watchers", memory="m2b", event="Followed young Isshara through the burning town",
         goal="In Isshara's memory, follow young Isshara up the burning beach of Nendis and stay with her.",
         text="The town's burning now. All of it. Walk with me. Don't stop for anything.",
         progress="Stay with me.",
         reward="We don't speak of it. Not to the column, not to the Lady, not to anyone, ever. Come. Down to the water.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("say", "self", "I'll sing a requiem for the land-walkers.", "talk", "NagaSirenPissed1"),
                 ("summon", "house_fire", "fire_house_1", 120), ("summon", "house_fire", "fire_house_2", 120),
                 ("summon", "house_fire", "fire_town_1", 120), ("summon", "house_fire", "fire_town_2", 120),
                 ("summon", "house_fire", "fire_town_3", 120), ("sound", "self", 10947), ("wait", 3500),
                 ("move", "self", "house_front", "walk"), ("wait", 8000), ("face", "self", "house_burn"),
                 ("summon", "girl", "house_in", 60), ("wait", 1500), ("sound", "girl", 11819), ("wait", 2500),
                 ("face", "self", "town"), ("wait", 1800), ("face", "self", "harbour"), ("wait", 1800),
                 ("face", "self", "player"), ("wait", 2000), ("move", "self", "house_in", "run"), ("wait", 3500),
                 ("sound", "girl", 11819), ("wait", 1500), ("move", "self", "house_out", "walk"),
                 ("move", "girl", "house_out", "walk"), ("wait", 3500), ("move", "self", "water_edge", "walk"),
                 ("move", "girl", "water_edge", "walk"), ("wait", 5000), ("emote", "girl", "talk"), ("wait", 2000), ("face", "self", "hills"), ("emote", "self", "point"),
                 ("wait", 1200), ("move", "girl", "house_out", "run"), ("wait", 2500), ("face", "girl", "water_edge"),
                 ("emote", "girl", "cry"), ("sound", "girl", 11819), ("wait", 2000), ("move", "girl", "hills", "run"),
                 ("wait", 2000), ("face", "self", "player"), ("say", "self", "You saw nothing.", "talk"), ("wait", 3000),
                 ("credit", "ch2_house"), ("move", "self", "m2b_isshara", "walk")],
         complete=[("face", "self", "hills"), ("wait", 2500), ("face", "self", "player"), ("emote", "self", "shy"),
                   ("wait", 1500), ("emote", "self", "talk")],
         poi=["house_burn"]),

    # 2.20: in Azshara's name (Vashj rises by the last burning ship; you wake, and the old hands shake)
    dict(key="ch2_vashj", title="In Azshara's Name", giver="ch0:isshara_young", ender="ch0:isshara", level=18, xp=8,
         tone="serious", prev="ch2_house", memory="m2b", wake=True, event="The fleet's sailing watched from the burning dock",
         goal="In Isshara's memory, watch from the burning dock as the fleet sails.",
         text="The master's sails are out of sight. The town will burn till morning. One more thing, and then we follow "
              "him. Watch the water.",
         progress="Watch.",
         reward="...I'm here. I'm here. Give me a moment. My hands. Look at my hands, little one. Ten thousand years and "
                "they still remember the heat.",
         details=["talk"], reward_emotes=["talk"], choice=["ember_legguards", "ember_leggings", "ember_trousers"],
         accept=[("face", "self", "harbour"), ("summon", "ship_fire", "fire_5", 90), ("summon", "ship_fire", "fire_6", 90),
                 ("summon", "ship_fire", "fire_3", 90), ("music", 6074), ("wait", 2500),
                 ("summon", "vashj_nendis", "vashj_rise", 50), ("sound", "self", "splash_big"), ("wait", 500),
                 ("move", "vashj_nendis", "vashj_surface", "walk"), ("wait", 4500), ("face", "vashj_nendis", "town"),
                 ("wait", 1500),
                 ("yell", "vashj_nendis", "Soon, we will reclaim the surface world, and take vengeance upon the night elves!",
                  "battle_roar", "LadyVashjPissed1"), ("wait", 8000), ("face", "vashj_nendis", "sea"), ("wait", 2500),
                 ("say", "vashj_nendis", "In Azshara's name.", None, "LadyVashjYes5"), ("wait", 3500),
                 ("move", "vashj_nendis", "vashj_sink", "walk"), ("sound", "vashj_nendis", "splash"), ("wait", 3500),
                 ("despawn", "vashj_nendis"), ("credit", "ch2_vashj")],
         complete=[("state", "self", "stun"), ("visual", "self", 36005), ("wait", 3000), ("visual", "self", 36005),
                   ("wait", 2000), ("state", "self", "none"), ("face", "self", "pool"), ("state", "self", "channel"),
                   ("wait", 3000), ("state", "self", "none")],
         poi=["harbour"]),

    # 2.21: the smell of smoke (she asks the girl's face, and listens)
    dict(key="ch2_smoke", title="The Smell of Smoke", giver="ch0:isshara", ender="ch0:isshara", level=18, xp=8,
         tone="serious", prev="ch2_vashj",
         quiz=[dict(npc="ch0:isshara", ask="Sit with her.", goal="Isshara told about the girl",
                    question="I never saw her face, you know. I carried her out through the fire and I never saw it. You "
                             "saw it. Tell me.",
                    answers=[("Small. Ash in her hair. She was trying not to cry, and she was very bad at it.", True,
                              [("visual", "self", 36005), ("sound", "self", 1215), ("wait", 2200), ("visual", "self", 36005),
                               ("sound", "self", 1215), ("wait", 2200), ("visual", "self", 36005), ("sound", "self", 1215)]),
                             ("I didn't look at her.", False, [("say", "self", "You looked. Everyone looks. Tell me.", "talk")]),
                             ("She was only a land-walker.", False,
                              [("face", "self", "hollow_east"), ("say", "self", "So was I, once. Again.", "talk")])])],
         goal="Sit with Isshara by her pool after Nendis, and tell her about the girl.",
         text="Stay a moment. The smoke is still in my nose. It's always in my nose after that one.",
         progress="",
         reward="Trying not to cry, and very bad at it. Yes. Yes, that sounds right. I wonder what she grew up to be. "
                "Nobody lives as long as we do, little one, except the night elves. She might be out there still.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500),
                 ("face", "self", "pool"), ("cast", "keepers_pool", 36005, "self"), ("wait", 1500), ("face", "self", "player")],
         complete=[("face", "self", "hollow_west"), ("wait", 2500), ("emote", "self", "omnicast"), ("visual", "self", 36005),
                   ("wait", 2000), ("face", "self", "player")],
         poi=["isshara"]),

    # 2.22: flowers at Shadowsong (the woman at the broken pillar)
    dict(key="ch2_flowers", title="Flowers at Shadowsong", giver="ch0:isshara", ender="ch0:isshara", level=19, xp=8,
         tone="serious", prev="ch2_smoke", objects=[("old_flowers", 1)],
         goal="Go to Shadowsong Shrine, on the hills south of Valormok above the Southfury, look at the flowers left at "
              "its broken pillar, and come back to Isshara.",
         text="There's a shrine on the hills over the river. Shadowsong. The Warden's family name; the Warden whose sisters "
              "chased us out of Nendis. The sirens who swim up the river say someone leaves flowers there. Fresh ones. "
              "Who leaves flowers on a Shadowsong shrine? Go and see. Don't touch anything.",
         progress="Who was it?",
         reward="An old woman. Night elf. A bow, and she didn't shoot. And flowers. Hm. Leave her be for now, little one. "
                "Some people put flowers down for a long time before they're ready to pick anything up.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "hollow_west"), ("wait", 2000), ("visual", "self", 36005), ("sound", "self", "pickup_water"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "hollow_west"),
                   ("wait", 3000), ("emote", "self", "omnicast"), ("cast", "keepers_pool", 36005, "self")],
         poi=["pillar"]),

    # 2.23: Captain Vessk (Szaria throws his sigil in the fire, not the sea)
    dict(key="ch2_vessk", title="Captain Vessk", giver="ch0:ssaveth", ender="ch0:ssaveth", level=19, xp=8, tone="serious",
         prev="ch2_flowers", kill=[("vessk", 1)], items=[("vessk_sigil", 1)], drops={"vessk_sigil": [("vessk", 100)]},
         goal="Kill Captain Vessk at his camp on the north end of the bay's west shore, across the water from the Hollow, "
              "and bring Ssaveth his sigil.",
         text="The hunters who come along the strand: they come from somewhere. From a camp on the west shore, under a "
              "banner, with a cage. Their captain's called Vessk. He's the one who looks south. Kill him. Bring me what "
              "he wears on his chest.",
         progress="Vessk.",
         reward="This. This is what they wear on their chests. Give it to Szaria. Watch what she does with it.",
         details=["talk"], reward_emotes=["roar"], choice=["vessk_trident", "vessk_dirk", "vessk_rod"],
         accept=[("state", "self", "none"), ("face", "self", "hollow_west"), ("emote", "self", "spell"), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 1500),
                 ("state", "self", "ready_thrown"), ("face", "self", "hollow_north")],
         complete=[("state", "self", "none"), ("face", "self", "ch1:hollow_szaria"), ("emote", "self", "roar"), ("wait", 1000),
                   ("move", "ch0:szaria", "hollow_fire_szaria", "walk"), ("wait", 5000), ("face", "ch0:szaria", "hollow_fire"),
                   ("emote", "ch0:szaria", "throw"), ("wait", 600), ("cast", "fire_spirit", 40162, "self"),
                   ("sound", "fire_spirit", 10947), ("wait", 2500), ("emote", "ch0:szaria", "talk"), ("wait", 2000),
                   ("move", "ch0:szaria", "ch1:hollow_szaria", "walk"), ("wait", 4000), ("face", "ch0:szaria", "player"),
                   ("state", "self", "ready_thrown"), ("face", "self", "hollow_north")],
         poi=["vessk_camp"]),

    # 2.24: the caged renegade (she follows slowly; at the Hollow she lies down in the shallows; her name is Thessa)
    dict(key="ch2_caged", title="The Caged Renegade", giver="ch0:ssaveth", ender="ch0:vyssa", level=19, xp=8,
         tone="serious", prev="ch2_vessk", objects=[("cage_lock", 1)], explore="thessa_rest", radius=12,
         goal="Open the cage in Vessk's camp on the west shore, and bring the siren in it home to the Hollow's shallows by "
              "Isshara's pool. Vyssa will see to her.",
         text="The cage in Vessk's camp. There's one of ours in it, or one who would be. She's been in there since before "
              "the strand went quiet. Open it. Bring her home. Swim slow; she won't be quick.",
         progress="",
         reward="Oh, look at her. Look at her. Here, the shallows, lie down. There. Kelp over you, it's warm. ...She says "
                "her name is Thessa. She says thank you. She says it to you, not to me.",
         details=["talk"], reward_emotes=["talk"], rewards=["kelp_band"],
         accept=[("face", "self", "hollow_west"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 1500), ("emote", "self", "roar")],
         complete=[("state", "self", "none"), ("move", "self", "thessa_rest", "walk"), ("move", "caged_siren", "thessa_rest", "walk"),
                   ("wait", 8000), ("state", "caged_siren", "drowned"), ("emote", "self", "work"), ("object", "kelp_blanket", "thessa_kelp", 120), ("wait", 1500),
                   ("emote", "self", "work"), ("wait", 2000), ("emote", "caged_siren", "talk"), ("wait", 2500),
                   ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 20000), ("despawn", "caged_siren"),
                   ("move", "self", "vyssa", "walk"), ("wait", 9000), ("state", "self", "work")],
         poi=["vessk_cage", "thessa_rest"]),

    # 2.25: Ssaveth's drill (funny): /roar at the recruits until they roar back properly
    dict(key="ch2_drill", title="Ssaveth's Drill", giver="ch0:ssaveth", ender="ch0:ssaveth", level=19, xp=8,
         tone="funny", prev="ch2_vessk",
         emotes=[("recruit", "roar", 3, [("face", "self", "player"), ("emote", "self", "shy"), ("sound", "self", 4021)]),
                 ("recruit_squeak", "roar", 1, [("face", "self", "player"), ("emote", "self", "roar"),
                                                ("sound", "self", 1023)]),
                 ("recruit_cobra", "roar", 1, [("face", "self", "player"), ("emote", "self", "battle_roar"),
                                               ("yell", "self", "COOOOBRAAAAAAAA!", None, "NagaMyrmadonPissed4"),
                                               ("wait", 2500), ("face", "recruit", "recruit_cobra"),
                                               ("face", "recruit_squeak", "recruit_cobra"),
                                               ("face", "ch0:kessh", "recruit_cobra"), ("face", "ch0:szaria", "recruit_cobra"),
                                               ("face", "ch0:vyssa", "recruit_cobra"), ("face", "sentry", "recruit_cobra"),
                                               ("wait", 4000), ("emote", "self", "shy"),
                                               ("face", "ch0:ssaveth", "hollow_east")])],
         goal="Roar at the 5 recruits on the Hollow's drill sand, at its west end, until each one roars back.",
         text="Recruits. Five of them. Came across the strand last week with nothing but their names. They have to roar "
              "back when they're roared at. It's how a line holds. Roar at them. Teach them.",
         progress="I heard that. That wasn't a roar. That was a cough.",
         reward="...I'm not going to talk about it. Nobody is going to talk about it. The drill is over.",
         details=["battle_roar"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "drill"), ("emote", "self", "battle_roar"),
                 ("sound", "self", "naga_aggro"), ("wait", 1800), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 1500), ("state", "self", "ready_thrown"), ("face", "self", "drill")],
         complete=[("face", "self", "hollow_east"), ("wait", 3000), ("emote", "self", "talk"), ("wait", 1500),
                   ("face", "self", "hollow_north"), ("state", "self", "ready_thrown")],
         poi=["drill"]),

    # 2.26: the shape of the next song (a door in a cliff glows on the water; Sesspira's people have the Tomb)
    dict(key="ch2_end", title="The Shape of the Next Song", giver="ch0:isshara", ender="ch0:szaria", level=19, xp=8,
         tone="serious", prev=["ch2_caged", "ch2_drill"], prev_any=["ch2_larder", "ch2_strongbox"],
         goal="Tell Lady Szaria what Isshara felt in the pool: Sesspira's people have the songs of the Tomb.",
         text="The pool's full and still and listening. Let me listen with it. The pearls they took from me are scattered "
              "everywhere, but they're mine, and they call. Hush. There. Can you see it? On the water. A door, in a cliff, "
              "on an island that wasn't there before. Sesspira's people have the Tomb. Go and tell Szaria.",
         progress="",
         reward="The Tomb. The one place the master went that none of us came back from whole. And Sesspira has it in a "
                "box at the ruins. Then we go and get it. Rest tonight, tide-runner. You're one of us, and tomorrow we "
                "have work.",
         details=["talk"], reward_emotes=["talk", "roar"], choice=["hollow_cloak", "keeper_pendant", "tidebreaker_band"],
         accept=[("face", "self", "pool"), ("state", "self", "channel"), ("sound", "self", "siren_hiss"),
                 ("cast", "keepers_pool", 57771, "self"), ("wait", 3000), ("summon", "pool_vision", "pool", 25),
                 ("object", "door_vision", "pool", 25), ("wait", 500), ("aura", "pool_vision", 46907), ("music", 5174),
                 ("wait", 6000), ("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "hollow_west"),
                   ("emote", "self", "roar"), ("sound", "self", "siren_aggro"), ("wait", 1500), ("emote", "ch0:ssaveth", "roar"),
                   ("emote", "sentry", "roar")],
         poi=["szaria_front"]),

    # the hub's chores (bible 18.14): repeatable, small, for a slower pace
    dict(key="ch2_fish", title="Fish for the Pot", giver="ch0:vyssa", ender="ch0:vyssa", level=17, min=15, xp=2,
         tone="boring", repeatable=True, prev="ch2_coral", items=[("bay_fish", 10)],
         goal="Empty the Tide-Broken's fish traps in the shallows round the Hollow and bring Vyssa 10 Bay Bream.",
         text="The traps are full again, or they'd better be. Ten bream. Everyone eats. Everyone, every night, which is "
              "more than the Empress managed.",
         progress="The pot's waiting. The pot is always waiting.",
         reward="Ten. Lovely. Go away now, I'm cooking.",
         details=["work"], reward_emotes=["work"],
         accept=[("state", "self", "none"), ("face", "self", "traps"), ("emote", "self", "spell"), ("wait", 1500),
                 ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "work"), ("sound", "self", 1189), ("wait", 1500),
                   ("state", "self", "work")],
         poi=["traps"]),
    dict(key="ch2_patrol", title="Patrol", giver="ch0:ssaveth", ender="ch0:ssaveth", level=17, min=15, xp=2,
         tone="boring", repeatable=True, prev="ch2_hunters", kill=[("tide_hunter", 10)],
         goal="Walk the north strand and kill 10 Spitelash Tide-Hunters.",
         text="The strand again. Every tide. Every tide they come back, and every tide somebody walks it.",
         progress="The strand.",
         reward="Quiet. Good.",
         details=["talk"], reward_emotes=["roar"],
         accept=[("face", "self", "north_shore"), ("emote", "self", "spell"), ("wait", 1500), ("emote", "self", "roar")],
         complete=[("emote", "self", "roar"), ("wait", 1500), ("face", "self", "hollow_north")],
         poi=["north_shore"]),
]

# -- the shared cast at this chapter's places (ch0: the Tide-Broken, their younger selves, the hub kit) -----------------
SPAWNS = [
    # the Tide-Broken at the Hollow (Lady Szaria stands there already, chapter 1's)
    dict(npc="ch0:isshara", at="isshara", facing=4.7, phase=HUB),
    dict(npc="ch0:ssaveth", at="ssaveth", facing=0.0, phase=HUB),
    dict(npc="ch0:vyssa", at="vyssa", facing=2.0, phase=HUB),
    # the hub kit (bible 18.9): trainers, trades, stores, the bank's clam, the mail jar, the Tide-Caller, the singer
    dict(npc="ch0:kessh", at="kessh", facing=3.4, phase=HUB),
    dict(npc="ch0:thessk", at="thessk", facing=0.8, phase=HUB),
    dict(npc="ch0:thessk_turtle", at="snap", facing=0.8, wander=2.0, phase=HUB),
    dict(npc="ch0:shivra", at="shivra", facing=0.5, phase=HUB),
    dict(npc="ch0:ulmara", at="ulmara", facing=1.0, phase=HUB),
    dict(npc="ch0:oshra", at="oshra", facing=3.2, phase=HUB),
    dict(npc="ch0:lyrenne", at="lyrenne", facing=0.3, phase=HUB),
    dict(npc="ch0:nazreth", at="nazreth", facing=0.6, phase=HUB),
    dict(npc="ch0:hookfin", at="hookfin", facing=3.3, phase=HUB),
    dict(npc="ch0:ysh", at="ysh", facing=0.2, phase=HUB),
    dict(npc="ch0:varra", at="varra", facing=0.2, phase=HUB),
    dict(npc="ch0:oleth", at="oleth", facing=0.2, phase=HUB),
    dict(npc="ch0:sheshk", at="sheshk", facing=0.6, phase=HUB),
    dict(npc="ch0:grosh", at="grosh", facing=4.7, phase=HUB),
    dict(npc="ch0:rhazz", at="rhazz", facing=4.7, phase=HUB),
    dict(npc="ch0:hissra", at="hissra", facing=0.8, phase=HUB),
    dict(npc="ch0:lysse", at="lysse", facing=1.0, phase=HUB),
    dict(npc="ch0:sszix", at="sszix", facing=1.2, phase=HUB),
    dict(npc="ch0:avessa", at="avessa", facing=1.4, phase=HUB),
    dict(npc="ch0:nyss", at="nyss", facing=1.8, phase=HUB),
    dict(npc="ch0:thalassa", at="thalassa", facing=1.2, phase=HUB),
    dict(npc="ch0:ishra", at="ishra", facing=3.6, phase=HUB),
    dict(npc="ch0:tessh", at="tessh", facing=3.6, phase=HUB),
    dict(npc="ch0:clamwarden", at="clamwarden", facing=4.0, phase=HUB),
    dict(npc="ch0:tidecaller", at="tidecaller", facing=0.0, phase=HUB),
    dict(npc="ch0:drowned_singer", at="singer", facing=0.5, phase=HUB),
    dict(object="ch0:mail_jar", at="mailbox", facing=1.0, phase=HUB),
    dict(object="ch0:locked_clam", at="clam", facing=2.0, phase=HUB),
    # young Isshara in both songs: with the column at the satyrs' camp (m2), by Nendis's docks (m2b)
    dict(npc="ch0:isshara_young", at="m2_isshara", facing=2.9, phase=M2),
    dict(npc="ch0:isshara_young", at="m2b_isshara", facing=4.7, phase=M2B),
]

GRAVEYARDS = [
    dict(at="graveyard", name="the Hollow", phase=HUB, facing=0.6),
]
