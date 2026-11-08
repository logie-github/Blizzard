# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 2 of the murlocs' story: The Free Shore (levels 14 to 19), the bible's section 8.

Darkshore's south coast (Twilight Shore). Greymist Cove, the hub, is the sheltered beach south-west of the
breakout's free shore (4888, 612): a sand flat under the cliffs (x 4790-4835, y 680-745), stilt huts in its
shallows, a sea-stack at its mouth, the rock outcrop to the west hiding it from Murkdeep's raiders on the
beach beyond (the game's Greymist Warriors and Hunters, 80 yards and more from anyone of the cove). Up the
shore to the north-east: the free shore, Murkdeep's camp and bonfire (4990, 550), Nerelith's rock (5125, 585)
and the Stormscale's slave-catchers on the north beach (5270-5410, 515-565) facing Sinslayer's sea-stack.
Inland to the south-east: the Twilight's Hammer at the Master's Glaive (4560, 410). Far up the coast:
Auberdine (its beach, its notice board). Down the coast to the south-west: the old elven pier at the
Zoram Strand's north end (4304, 1155), where the chapter ends and chapter 3's Drowned Pier begins.

The cove's own people (Mother Mrrgula, the sentries, the villagers, the fry) are always there; its teachers
and the tribe's runaways come from 2.01's reward. Phase rules in Darkshore kept few (the zone's story bits are
shared with chapter 3): from 2.01; Sloshy's; the Twilight camp's prisoners until 2.14; the two fates of
Murkdeep's warriors (2.20a, 2.20b); Auberdine's wagons after 2.22b; the march (while 2.25 is in the log).
Plain data: tools/murloc/SCHEMA.md."""

HUB = ("from", "ch2_arrival")                                   # the cove's teachers, the tribe's runaways
SLOSHY = ("between", "ch2_arrival", "ch3:ch3_clutch")          # Sloshy, at chapter 2's and 3's hubs
CAMP = ("between", "ch2_arrival", "ch2_chains")                # the Twilight camp's prisoners, until freed
MARCH = ("during", "ch2_end")                                   # the march south and its ambushes

CHAPTER = dict(key="ch2", title="The Free Shore", levels=(14, 19), map=1, zones=[148], hub="hub")

TOWNS = ["Auberdine"]

# models (paths in the game's files)
FISH = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadBlue.mdx"
FISH_BIG = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadOrange.mdx"
FISH_RACK = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishRack.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
CLUB = "World\\Generic\\PassiveDoodads\\Weapons\\BoneClub01.mdx"
BOW = "World\\Generic\\Human\\Passive Doodads\\Weapons&Armor\\HumanBow01.mdx"
MANACLE = "World\\Generic\\DarkIronDwarf\\Passive Doodads\\Manacles\\BlackrockOrcManacle01.mdx"
CRYSTAL = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Crystal_01.mdx"
ORACLE_HUT = "World\\Expansion02\\Doodads\\Oracle\\Huts\\Oracle_Hut01.mdx"
ORACLE_HUT_2 = "World\\Expansion02\\Doodads\\Oracle\\Huts\\Oracle_Hut02.mdx"
ORACLE_TOTEM = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Totem_01.mdx"
ORACLE_LAMP = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Lamppost_01.mdx"
SURFBOARD = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Surfboard01.mdx"
NET_PILE = "World\\Expansion02\\Doodads\\Generic\\SeaVrykul\\Shore\\VRS_NetPile_01.mdx"
NET_TORN = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\GiantNets\\TS_GiantNet01Destroyed.mdx"
NET_NEW = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\GiantNets\\TS_GiantNet01.mdx"
BASKET = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\Fishing\\TS_FishingBasket_Empty_02.mdx"
CRAB_BASKET = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\Fishing\\TS_CrabBasket_Empty01.mdx"
DRIFTWOOD = "World\\Azeroth\\Westfall\\PassiveDoodads\\Detail\\WestfallDriftwood.mdx"
BOULDER = "World\\Azeroth\\Westfall\\PassiveDoodads\\Rocks\\WestfallBoulder01.mdx"
LOG = "World\\Azeroth\\SwampOSorrow\\PassiveDoodads\\TreeLogs\\SwampTreeLog01.mdx"
TREE_BANNER = "World\\Generic\\NightElf\\Passive Doodads\\Banners\\NightElfTreeBanner01.mdx"
HORDE_BANNER = "World\\Expansion01\\Doodads\\Generic\\AncientOrc\\Banners\\AO_Banner01.mdx"
PILLAR = "World\\Kalimdor\\Ashenvale\\PassiveDoodads\\SatyrRuins\\RuinsSatyrPillar01.mdx"
ELF_RUIN = "World\\Generic\\NightElf\\Passive Doodads\\Ruins\\NightElfRuins01.mdx"
ELF_RUIN_2 = "World\\Generic\\NightElf\\Passive Doodads\\Ruins\\NightElfRuins02.mdx"
BOOK = "World\\Expansion01\\Doodads\\Generic\\BloodElf\\Books\\BE_Book_Large01.mdx"
DRUM = 7533                         # (the game's voodoo drum: the cove's alarm drum)
WAGON = 3678
POSTER = 3053
PLAQUE = 214

PLACES = {
    # Greymist Cove: the fire in the middle, Mother Mrrgula's seat on the slope, the cook-pot, the teachers
    "hub": (4816.0, 708.0), "mrrgula": (4803.0, 695.0), "greet": (4815.0, 702.0), "greet_fish": (4816.5, 704.0),
    "pot": (4826.0, 692.0), "cook": (4829.5, 689.5), "pot_hide": (4825.5, 694.5), "rack": (4835.0, 699.0),
    "fishwife": (4832.0, 702.5), "t_warrior": (4799.0, 724.0), "t_hunter": (4807.0, 733.0), "t_rogue": (4821.0, 735.0),
    "altar": (4792.0, 714.0), "t_priest": (4795.0, 711.0), "nrrglo": (4794.0, 702.0), "seer_totem": (4790.5, 699.5),
    "t_mage": (4806.0, 685.0), "t_firstaid": (4814.0, 687.0), "t_fishing": (4840.0, 696.0), "netweaver": (4829.0, 725.0),
    "net": (4832.5, 728.0), "netpile": (4834.0, 720.0), "baskets": (4831.0, 707.0), "lamp_1": (4808.0, 712.0),
    "lamp_2": (4826.0, 718.0), "surfboard": (4837.0, 717.0), "drum": (4810.0, 696.0), "drum_spot": (4808.5, 698.5),
    "graveyard": (4791.0, 716.0), "hut_1": (4846.0, 694.0), "hut_2": (4857.0, 706.0), "hut_3": (4857.0, 683.0),
    "hut_5": (4793.0, 690.0), "hut_post": (4843.5, 696.5),
    # the runaways: Blrrgl and his log and his hut wall, Sloshy, Mrrk
    "blrrgl": (4810.0, 728.0), "blrrgl_log": (4806.5, 731.0), "blrrgl_hut": (4799.0, 739.0), "hut_wall": (4802.0, 735.5),
    "hut_wall_b": (4799.5, 736.5), "hut_wall_front": (4805.0, 733.5), "blrrgl_hide": (4805.0, 734.0),
    "blrrgl_draw": (4813.0, 724.5), "blrrgl_throw": (4838.0, 722.0), "tiptoe": (4818.0, 722.0), "crawl_1": (4806.0, 722.0),
    "sloshy": (4819.0, 717.0), "mrrk": (4804.0, 716.0),
    # the cove's people: sentries at the north-east gap, villagers, the fry on the north beach
    "sentry_a": (4848.0, 661.0), "sentry_b": (4839.0, 652.0), "gate_in": (4836.0, 668.0), "gate_out": (4852.0, 648.0),
    "blrrgl_lead": (4850.0, 645.0), "grovel_1": (4846.0, 650.0), "grovel_2": (4849.0, 653.5), "grovel_3": (4852.5, 650.5),
    "villager_a": (4822.0, 712.0), "villager_b": (4811.0, 703.0), "villager_c": (4845.0, 690.0), "villager_d": (4826.0, 737.0),
    "fry_gloob": (4815.0, 744.0), "fry_pibbl": (4822.0, 747.0), "fry_snorkl": (4829.0, 744.0), "fry_mudpie": (4811.0, 740.0),
    "fry_gang": (4822.0, 745.0),
    # directions (to face or point)
    "pens_way": (4781.0, 727.0), "north_way": (4856.0, 703.0), "camp_way": (4790.0, 678.0), "crawler_way": (4847.0, 683.0),
    "shoals": (4858.0, 690.0), "raid_edge": (4805.0, 790.0), "murk_camp": (4995.0, 550.0),
    # Mrrgula's drawings in the sand, the moot's baskets, the scenes by the fire
    "mrrgula_draw": (4808.0, 703.0), "mrrgula_draw_a": (4810.0, 705.0), "mrrgula_draw_b": (4811.5, 702.5),
    "mrrgula_draw_c": (4813.0, 704.0), "mrrgula_draw_d": (4812.0, 706.5), "fire_side": (4813.0, 706.0),
    "ledger_spot": (4815.0, 707.0), "hydra_spot": (4816.5, 708.5), "back_1": (4826.0, 698.0), "back_2": (4845.0, 700.0),
    "stay_basket": (4812.0, 713.5), "go_basket": (4820.0, 713.5), "moot_spot": (4816.0, 717.0),
    "go_basket_front": (4820.0, 715.5), "stay_front": (4812.0, 715.5), "totem_spot": (4806.0, 699.0),
    "sullen_1": (4798.0, 690.0), "sullen_2": (4801.0, 686.0), "sullen_3": (4796.0, 694.0),
    "murk_seat": (4836.0, 674.0), "hard_1": (4840.0, 676.0), "hard_2": (4833.0, 678.0),
    # the raid, the fishing moot, the race, the sacred rock, the war band
    "waterline_1": (4840.0, 700.0), "waterline_2": (4838.0, 708.0), "waterline_3": (4836.0, 686.0),
    "waterline_4": (4842.0, 704.0), "raid_1": (4847.0, 700.0), "raid_2": (4851.0, 712.0), "raid_3": (4853.0, 690.0),
    "raid_4": (4843.0, 683.0), "contest_basket": (4836.0, 707.0), "best_shoal": (4860.0, 692.0), "thresher_rise": (4858.0, 712.0),
    "start_line": (4836.0, 716.0), "victory": (4826.0, 716.0),
    "buoy_1": (4880.0, 742.0, 0.0), "buoy_2": (4905.0, 712.0, 0.0), "buoy_3": (4895.0, 678.0, 0.0),
    "buoy_1_near": (4878.0, 738.0), "buoy_2_near": (4902.0, 710.0), "buoy_3_near": (4892.0, 680.0),
    "sacred_rock": (4836.0, 742.0), "rock_side": (4833.0, 738.0),
    "horizon_1": (4905.0, 795.0, 0.0), "horizon_2": (4925.0, 772.0, 0.0), "shapes_1": (4875.0, 760.0), "shapes_2": (4888.0, 752.0),
    "warband_1": (4832.0, 682.0), "warband_2": (4836.0, 678.0), "warband_3": (4828.0, 678.0),
    # the shallows and the beach: shoals, seaweed, driftwood
    "darter_1": (4850.0, 676.0), "darter_2": (4858.0, 684.0), "darter_3": (4866.0, 692.0), "darter_4": (4862.0, 670.0),
    "darter_5": (4870.0, 700.0), "darter_6": (4852.0, 700.0), "darter_7": (4864.0, 706.0), "darter_8": (4874.0, 682.0),
    "kelp_1": (4848.0, 704.0), "kelp_2": (4860.0, 694.0), "kelp_3": (4868.0, 678.0), "kelp_4": (4844.0, 688.0),
    "kelp_5": (4872.0, 708.0), "kelp_6": (4856.0, 668.0), "kelp_7": (4878.0, 692.0), "kelp_8": (4862.0, 712.0),
    "drift_1": (4862.0, 646.0), "drift_2": (4874.0, 632.0), "drift_3": (4886.0, 625.0), "drift_4": (4898.0, 612.0),
    "drift_5": (4910.0, 604.0), "drift_6": (4856.0, 655.0),
    # Murkdeep's raiders past the western rock; reef crawlers toward his camp
    "raid_g1": (4795.0, 795.0), "raid_g2": (4818.0, 800.0), "raid_g3": (4785.0, 778.0), "raid_g4": (4830.0, 806.0),
    "crab_1": (4925.0, 640.0), "crab_2": (4942.0, 602.0), "crab_3": (4960.0, 628.0), "crab_4": (5065.0, 600.0),
    # Murkdeep: his challenge fire on the beach below his camp, his den by the camp's bonfire
    "challenge_fire": (4930.0, 598.0), "wave_1": (4936.0, 616.0), "wave_2": (4926.0, 620.0), "wave_3": (4944.0, 612.0),
    "murk_rise": (4932.0, 622.0), "murk_kneel": (4931.0, 606.0), "murk_club": (4929.5, 603.5),
    "den": (5016.0, 546.0), "totem": (5019.0, 542.0),
    # the north beach: Nerelith's rock, the Stormscale slave-catchers, Sinslayer's sea-stack
    "nerelith": (5129.0, 556.0), "nerelith_kneel": (5126.0, 579.0), "nerelith_rock": (5125.0, 585.0),
    "rock_fish": (5124.0, 581.5), "draw_a": (5122.0, 574.0), "draw_b": (5125.0, 572.0), "draw_c": (5128.0, 573.0),
    "draw_d": (5131.0, 574.0), "band_center": (5340.0, 545.0),
    "wr_1": (5272.0, 548.0), "wr_2": (5298.0, 542.0), "wr_3": (5326.0, 552.0), "wr_4": (5352.0, 540.0), "wr_5": (5378.0, 548.0),
    "wr_6": (5404.0, 538.0), "siren_1": (5284.0, 530.0), "siren_2": (5312.0, 526.0), "siren_3": (5340.0, 530.0),
    "siren_4": (5366.0, 525.0), "siren_5": (5392.0, 524.0), "myr_1": (5290.0, 560.0), "myr_2": (5318.0, 562.0),
    "myr_3": (5346.0, 558.0), "myr_4": (5372.0, 560.0), "myr_5": (5398.0, 556.0),
    "sinslayer_horn": (5446.0, 550.0), "sinslayer_rise": (5440.0, 590.0),
    # the Twilight's Hammer at the Master's Glaive: the north bluff, the slave sale, the shackles
    "ridge": (4626.0, 440.0), "slaver_start": (4618.0, 400.0), "sold_a": (4621.0, 395.0), "sold_b": (4623.0, 402.0),
    "sold_c": (4619.0, 391.0), "sale_1": (4582.0, 408.0), "sale_a1": (4585.0, 403.0), "sale_b1": (4586.0, 411.0),
    "sale_c1": (4588.0, 399.0), "buyer": (4572.0, 410.0), "cage": (4566.0, 404.0), "cage_in_a": (4566.5, 404.5),
    "cage_in_b": (4565.5, 403.5), "cage_in_c": (4566.2, 405.6), "cage_front": (4569.5, 406.0),
    "shackle_1": (4545.0, 428.0), "shackle_2": (4556.0, 392.0), "shackle_3": (4584.0, 418.0), "shackle_4": (4535.0, 402.0),
    "shackle_5": (4578.0, 392.0), "chained_1": (4546.0, 429.5), "chained_2": (4557.5, 393.0), "chained_3": (4585.5, 419.0),
    "chained_4": (4536.5, 403.5), "chained_5": (4579.5, 393.5), "flee_point": (4622.0, 385.0),
    "disc_1": (4548.0, 415.0), "disc_2": (4590.0, 425.0), "disc_3": (4535.0, 390.0), "disc_4": (4560.0, 430.0),
    # Auberdine: the notice board by the inn; the grain wagons and Gubber Blump's fishing spot on the beach
    "poster": (6400.8, 501.5), "night_sentinel": (6391.0, 507.0),
    "wagon_a": (6330.0, 586.0), "wagon_b": (6345.0, 580.0), "carter": (6337.0, 568.0),
    "sack_1": (6327.0, 581.0), "sack_2": (6333.0, 591.0), "sack_3": (6325.0, 590.0), "sack_4": (6342.0, 575.0),
    "sack_5": (6349.0, 585.0), "sack_6": (6341.0, 586.0), "take_1": (6328.2, 581.8), "take_2": (6334.2, 591.8),
    "take_3": (6326.2, 590.8), "take_4": (6343.2, 575.8), "take_5": (6350.2, 585.8), "take_6": (6342.2, 586.8),
    "pearl_cart_a": (6331.5, 583.5), "pearl_cart_b": (6346.5, 577.5),
    "wagon_guard_1": (6322.0, 576.0), "wagon_guard_2": (6352.0, 590.0),
    "gubber_basket": (6366.0, 582.0), "box_left": (6366.8, 583.4), "tackle_sunk": (6380.0, 606.0), "prize_mount": (6375.0, 571.0),
    "sloshy_peek": (6356.0, 598.0),
    # the march south: the ambushes, and the old elven pier at the Zoram Strand's north end (chapter 3's Drowned Pier)
    "amb_n1": (4442.0, 930.0), "amb_n2": (4450.0, 920.0), "amb_n3": (4436.0, 918.0), "amb_n4": (4455.0, 933.0),
    "amb_t1": (4386.0, 1032.0), "amb_t2": (4378.0, 1022.0), "amb_t3": (4392.0, 1018.0),
    "drowned_pier": (4304.0, 1155.0), "blrrgl_pier": (4301.0, 1151.0), "pier_ruin_1": (4316.0, 1165.0),
    "pier_ruin_2": (4318.0, 1150.0), "pier_ruin_3": (4322.0, 1158.0), "camp_1": (4298.0, 1145.0), "camp_2": (4305.0, 1146.0),
    "camp_3": (4296.0, 1160.0), "pens_dir": (4260.0, 1140.0),
}

# -- the people -------------------------------------------------------------------------------------

NPCS = [
    # the cove's own (always there: the free Greymist were here before the runaways came)
    dict(key="sentry_l", name="Greymist Sentry", plural="Greymist sentries", look="murloc_slate", level=20, role="ambient",
         at="sentry_a", facing=5.5, greeting="Mrgl. Spear down. Mother says you are ours now.",
         watch=(7, [("face", "self", "player"), ("state", "self", 27), ("emote", "self", "attack"), ("sound", "self", "murloc_alert"),
                    ("wait", 2500), ("state", "self", "none"), ("face", "self", "hub"), ("emote", "self", "point"), ("wait", 4000),
                    ("face", "self", "gate_out")], 60000),
         idle=[("every", 41000, [("sound", "self", "murloc_fidget2")])]),
    dict(key="sentry_r", name="Greymist Sentry", plural="Greymist sentries", look="murloc_grey", level=20, role="ambient",
         at="sentry_b", facing=5.2,
         watch=(7, [("face", "self", "player"), ("state", "self", 27), ("emote", "self", "attack"), ("wait", 2500),
                    ("state", "self", "none"), ("face", "self", "gate_out")], 60000),
         idle=[("every", 47000, [("emote", "self", "flex")])]),
    dict(key="villager", name="Greymist Villager", plural="Greymist", look="murloc_orange", looks=["murloc_pale"], level=(13, 14),
         role="ambient", at=["villager_a", "villager_b"], idle=[("state", "self", "sit"), ("every", 37000, [("emote", "self", "eat")])]),
    dict(key="wader", name="Greymist Netter", look="murloc_blue", level=14, role="ambient", at="villager_c", facing=0.3,
         idle=[("state", "self", "work"), ("every", 33000, [("sound", "self", "splash_small")])]),
    dict(key="mender", name="Greymist Villager", look="murloc_gold", level=13, role="ambient", at="villager_d", facing=4.6,
         idle=[("state", "self", "work"), ("every", 45000, [("emote", "self", "laugh")])]),
    # the fry who pelt newcomers with mud (2.03)
    dict(key="gloob", name="Gloob", subname="Greymist Fry", look="murloc_green", scale=0.5, level=5, role="ambient", at="fry_gloob",
         facing=4.7, greeting="Hee! Splat!",
         watch=(9, [("face", "self", "player"), ("emote", "self", "throw"), ("sound", "self", 907), ("aura", "player", "muddy"),
                    ("emote", "self", "laugh"), ("sound", "self", "baby_murloc")], 45000),
         idle=[("every", 19000, [("emote", "self", "laugh"), ("sound", "self", "baby_murloc")])]),
    dict(key="pibbl", name="Pibbl", subname="Greymist Fry", look="murloc_orange", scale=0.5, level=5, role="ambient", at="fry_pibbl",
         facing=4.9, greeting="Mud! More mud!",
         watch=(9, [("face", "self", "player"), ("emote", "self", "throw"), ("sound", "self", 907), ("aura", "player", "muddy"),
                    ("emote", "self", "cheer")], 45000),
         idle=[("every", 23000, [("emote", "self", "throw"), ("sound", "self", 907)])]),
    dict(key="snorkl", name="Snorkl", subname="Greymist Fry", look="murloc_ice", scale=0.5, level=5, role="ambient", at="fry_snorkl",
         facing=4.4, greeting="...splat?",
         watch=(9, [("face", "self", "player"), ("emote", "self", "throw"), ("sound", "self", 907), ("aura", "player", "muddy"),
                    ("emote", "self", "shy")], 45000),
         idle=[("every", 29000, [("emote", "self", "shy")])]),
    dict(key="mudpie", name="Mudpie", subname="Greymist Fry", look="murloc_bronze", scale=0.55, level=6, role="ambient", at="fry_mudpie",
         facing=5.0, greeting="I am the boss of the mud. Bow.",
         watch=(9, [("face", "self", "player"), ("emote", "self", "throw"), ("sound", "self", 907), ("aura", "player", "muddy"),
                    ("emote", "self", "flex"), ("sound", "self", "baby_murloc")], 45000),
         idle=[("every", 26000, [("emote", "self", "flex")])]),

    # the Greymist's teachers (the bible's 17.1 trainer lists, other faces), from the runaways' welcome on
    dict(key="nrrglo", name="Seer Nrrglo", subname="Shaman Trainer", look="murloc_abyssal", level=26, role="quest+trainer:shaman",
         at="nrrglo", facing=0.4, phase=HUB, greeting="Sit. The water talks slowly. Sit, and it will get to you.",
         idle=[("state", "self", "sit"), ("every", 47000, [("visual", "self", 36005), ("sound", "self", "murloc_fidget2")])]),
    dict(key="grrlok", name="Grrlok Stonefin", subname="Warrior Trainer", look="murloc_grey", scale=1.1, level=30,
         role="trainer:warrior", at="t_warrior", facing=5.8, phase=HUB,
         greeting="Spear first. Spear always. Murkdeep's warriors think that makes them strong. It makes them pointy.",
         idle=[("every", 21000, [("emote", "self", "attack"), ("sound", "self", "murloc_attack")])]),
    dict(key="mrrsha", name="Mrrsha Longspear", subname="Hunter Trainer", look="murloc_bronze", level=30,
         role="trainer:hunter+stable", at="t_hunter", facing=5.3, phase=HUB,
         greeting="The threshers hunt by smell. The crabs by feel. We hunt by patience. Mostly.",
         idle=[("every", 31000, [("emote", "self", "point"), ("sound", "self", "murloc_fidget")])]),
    dict(key="slipgill", name="Slipgill", subname="Rogue Trainer", look="murloc_gold", level=30, role="trainer:rogue",
         at="t_rogue", facing=4.6, phase=HUB, greeting="You didn't see me. Good. Nobody sees me. That's the lesson.",
         idle=[("state", "self", 433), ("every", 29000, [("emote", "self", "laugh")])]),
    dict(key="ulmrra", name="Tide-Mother Ulmrra", subname="Priest Trainer", look="murloc_blue", level=30, role="trainer:priest",
         at="t_priest", facing=0.2, phase=HUB, greeting="The sea gives and the sea takes. In between, we patch each other up.",
         idle=[("every", 43000, [("visual", "self", 57771), ("sound", "self", 1432)])]),
    dict(key="blurgle", name="Blurgle the Bright", subname="Mage Trainer", look="murloc_red", level=30, role="trainer:mage",
         at="t_mage", facing=0.9, phase=HUB, greeting="Frost, for the fish. Fire, for the cooking. Arcane, for... showing off.",
         idle=[("every", 39000, [("visual", "self", 32992), ("sound", "self", 3076)])]),
    dict(key="bubbmrl", name="Bubbmrl the Cook", subname="Cook", look="murloc_orange", scale=1.1, level=24,
         role="innkeeper+profession:cooking", at="cook", facing=2.4, phase=HUB,
         greeting="Sit by the pot. Everyone sits by the pot. The pot doesn't care who you were.",
         idle=[("state", "self", "work"), ("every", 27000, [("sound", "self", 973)])]),
    dict(key="kelpwrap", name="Gurmla Kelpwrap", subname="First Aid Trainer", look="murloc_green", level=25,
         role="profession:first_aid", at="t_firstaid", facing=1.2, phase=HUB,
         greeting="Kelp, tight. Then tighter. Then it stops bleeding. Mostly.",
         idle=[("every", 35000, [("emote", "self", "work")])]),
    dict(key="snapjaw", name="Old Snapjaw", subname="Fishing Trainer", look="murloc_grey", level=25, role="profession:fishing",
         at="t_fishing", facing=0.1, phase=HUB, greeting="Fish are free. That is why they are so hard to catch.",
         idle=[("state", "self", "fish"), ("every", 39000, [("sound", "self", "splash_small")])]),
    dict(key="glimmrsh", name="Glimmrsh the Fishwife", subname="Food and Drink", look="murloc_pale", level=20, role="vendor",
         at="fishwife", facing=3.4, phase=HUB, greeting="Fresh fish! Old fish! Fish that was fresh this morning!",
         idle=[("every", 31000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget")])]),
    dict(key="netweaver", name="Grrma Holenet", subname="Net-Weaver", look="murloc_purple", level=25,
         role="quest+profession:tailoring", at="netweaver", facing=0.9, phase=HUB,
         greeting="Over, under, knot. Over, under, knot. Over... where was I?",
         idle=[("state", "self", "work"), ("every", 37000, [("sound", "self", "murloc_fidget2")])]),

    # Murkdeep (2.20): the fight at his challenge fire, the yield, his sleep, and his warriors after
    dict(key="hardliner", name="Murkdeep's Hardliner", look="warrior", looks=["hunter"], level=(17, 18), side="hostile",
         role="enemy", language="nerglish", summoned=True),
    dict(key="murkdeep_foe", name="Murkdeep", subname="Chief of the Hardliners", look="murloc_slate", scale=1.35, level=19,
         side="hostile", role="enemy", language="nerglish", health=2.0, damage=1.2, summoned=True),
    dict(key="murkdeep_yield", name="Murkdeep", subname="Chief of the Hardliners", look="murloc_slate", scale=1.35, level=19,
         role="ambient", summoned=True, greeting="...Take it. Take it! You beat me. Everyone saw."),
    dict(key="murkdeep_sleep", name="Murkdeep", subname="Asleep", look="murloc_slate", scale=1.35, level=19, role="ambient",
         summoned=True, idle=[("every", 6000, [("state", "self", "sleep")]), ("every", 21000, [("visual", "self", 6431),
                                                                                              ("sound", "self", 7940)])]),
    dict(key="murkdeep", name="Murkdeep", subname="Chief of the Hardliners", look="murloc_slate", scale=1.35, level=19,
         role="ambient", at="murk_seat", facing=2.2, phase=("from", "ch2_honor"),
         greeting="You beat me, and you gave it back. Nobody gives anything back. ...Hm.",
         idle=[("every", 43000, [("emote", "self", "flex"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="hardliner_ally", name="Greymist Hardliner", look="murloc_red", looks=["murloc_slate"], level=18, role="ambient",
         at=["hard_1", "hard_2"], facing=2.4, phase=("from", "ch2_honor"),
         idle=[("every", 51000, [("emote", "self", "flex")])]),
    dict(key="hardliner_sullen", name="Greymist Hardliner", look="murloc_red", looks=["murloc_slate"], level=18, role="ambient",
         at=["sullen_1", "sullen_2", "sullen_3"], facing=0.8, phase=("from", "ch2_totem"),
         idle=[("state", "self", "sit"), ("every", 47000, [("emote", "self", "no"), ("sound", "self", "murloc_fidget2")])]),

    # the Stormscale: raiders (2.19), the war party on the horizon (2.18), Lord Sinslayer (2.10), the slaver (2.13)
    dict(key="raider", name="Stormscale Raider", plural="Stormscale Raiders", look="myrmidon", looks=["naga_male"],
         level=(17, 18), side="naga", role="enemy", language="naga", summoned=True),
    dict(key="war_shape", name="Dark Shape", look="naga_male", level=18, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),
    dict(key="war_boat", name="Stormscale War-Boat", look=30874, scale=0.9, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),
    dict(key="sinslayer", name="Lord Sinslayer", subname="Slave-Catcher", look="naga_lord", level=17, side="naga", role="enemy",
         language="naga", health=3.0, damage=1.2, summoned=True, abilities=[(6533, 14000)]),
    dict(key="slaver", name="Stormscale Slaver", look="naga_male", level=18, side="naga", role="enemy", language="naga",
         at="slaver_start", facing=3.3, phase=CAMP, respawn=90,
         watch=(45, [("sound", "self", "naga_hiss"), ("emote", "self", "talk"), ("move", "self", "sale_1", "walk"),
                     ("move", "sold_a", "sale_a1", "walk"), ("move", "sold_b", "sale_b1", "walk"),
                     ("move", "sold_c", "sale_c1", "walk"), ("sound", "sold_a", 1005), ("wait", 9000),
                     ("face", "self", "buyer"), ("emote", "self", "talk"), ("sound", "self", "naga_hiss"),
                     ("emote", "buyer", "talk"), ("wait", 2500), ("emote", "buyer", 432), ("sound", "buyer", 120),
                     ("emote", "self", "roar"), ("wait", 2500), ("move", "buyer", "cage_front", "walk"),
                     ("move", "sold_a", "cage_in_a", "walk"), ("move", "sold_b", "cage_in_b", "walk"),
                     ("move", "sold_c", "cage_in_c", "walk"), ("sound", "sold_b", 1005), ("wait", 4500),
                     ("emote", "sold_a", "cry"), ("sound", "sold_b", "murloc_wound"), ("emote", "buyer", 432),
                     ("sound", "buyer", 1206), ("credit", "ch2_robes"), ("wait", 25000),
                     ("move", "self", "slaver_start", "walk"), ("move", "buyer", "buyer", "walk"),
                     ("move", "sold_a", "sold_a", "walk"), ("move", "sold_b", "sold_b", "walk"),
                     ("move", "sold_c", "sold_c", "walk")], 120000)),
    dict(key="buyer", name="Twilight Slave-Buyer", look=2873, level=18, side="naga", role="enemy", language="common",
         at="buyer", facing=0.2, phase=CAMP, respawn=90, idle=[("every", 33000, [("emote", "self", "talk")])]),
    dict(key="sold_a", name="Chained Greymist", look="murloc_pale", level=12, role="ambient", at="sold_a", facing=3.3,
         phase=CAMP, idle=[("every", 21000, [("emote", "self", "cry")])]),
    dict(key="sold_b", name="Chained Greymist", look="murloc_orange", level=12, role="ambient", at="sold_b", facing=3.3,
         phase=CAMP, idle=[("every", 27000, [("emote", "self", "beg")])]),
    dict(key="sold_c", name="Chained Greymist", look="murloc_grey", level=11, role="ambient", at="sold_c", facing=3.3,
         phase=CAMP, idle=[("every", 24000, [("sound", "self", "murloc_wound")])]),
    # the prisoners at the shackles (2.14): one each, so each shackle frees its own
    dict(key="chained_1", name="Chained Greymist", plural="Chained Greymist", look="murloc_blue", level=12, role="ambient",
         at="chained_1", facing=2.0, respawn=60, phase=CAMP, idle=[("state", "self", "kneel")]),
    dict(key="chained_2", name="Chained Greymist", plural="Chained Greymist", look="murloc_green", level=12, role="ambient",
         at="chained_2", facing=1.0, respawn=60, phase=CAMP, idle=[("state", "self", "kneel")]),
    dict(key="chained_3", name="Chained Greymist", plural="Chained Greymist", look="murloc_grey", level=11, role="ambient",
         at="chained_3", facing=3.4, respawn=60, phase=CAMP, idle=[("state", "self", "kneel")]),
    dict(key="chained_4", name="Chained Greymist", plural="Chained Greymist", look="murloc_ice", level=11, role="ambient",
         at="chained_4", facing=0.4, respawn=60, phase=CAMP, idle=[("state", "self", "kneel")]),
    dict(key="chained_5", name="Chained Greymist", plural="Chained Greymist", look="murloc_pale", level=12, role="ambient",
         at="chained_5", facing=1.9, respawn=60, phase=CAMP, idle=[("state", "self", "kneel")]),

    # what the seer sees in the ledger's smoke (2.15)
    dict(key="violet_flame", name="Violet Flame", look="trigger", level=1, role="ambient", unit_flags=0x02000002, summoned=True),
    dict(key="hydra_shadow", name="Shadow in the Smoke", look=10898, scale=0.35, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),

    # the shallows: shoals to spear (2.02, 2.16), and what eats the prize basket
    dict(key="darter", name="Silverfin Shoal", plural="Silverfin Shoals", look=4878, level=14, side="neutral", role="ambient",
         health=0.25, damage=0.1, at=["darter_1", "darter_2", "darter_3", "darter_4", "darter_5", "darter_6", "darter_7",
                                      "darter_8"], wander=4.0, respawn=20, phase=HUB),
    dict(key="basket_eater", name="Elder Darkshore Thresher", subname="Basket-Eater", look=994, level=18, side="hostile",
         role="enemy", health=1.3, summoned=True),

    # Auberdine's people of the story (the town's own Sentinels warn too: the module's)
    dict(key="night_sentinel", name="Auberdine Sentinel", look=4845, level=40, side="faction:69", role="guard",
         language="darnassian", at="night_sentinel", facing=5.6,
         watch=(20, [("face", "self", "player"), ("emote", "self", "point"),
                     ("yell", "self", "You! In the shadows! Not one step closer!", None, "sentinel_pissed"),
                     ("state", "self", 376), ("wait", 8000), ("state", "self", "none"), ("face", "self", "poster")], 30000)),
    dict(key="carter", name="Teloren", subname="Carter", look=4243, level=20, side="faction:69", role="ambient",
         language="darnassian", at="carter", facing=1.6, greeting="Zzz... the grain... zzz...",
         idle=[("state", "self", "sleep"), ("every", 25000, [("visual", "self", 6431), ("sound", "self", 7940)])]),
    dict(key="wagon_guard", name="Auberdine Sentinel", look=4846, looks=[4847], level=40, side="faction:69", role="guard",
         language="darnassian", at=["wagon_guard_1", "wagon_guard_2"], facing=2.0, phase=("from", "ch2_grain"),
         watch=(20, [("face", "self", "player"), ("emote", "self", "point"),
                     ("yell", "self", "Back to the water, thief! We remember you!", None, "sentinel_pissed"),
                     ("state", "self", 376), ("wait", 8000), ("state", "self", "none")], 30000)),

    # the ones who go along: Sloshy to Auberdine (2.12a), the war band south (2.25), Blrrgl at the pier
    dict(key="sloshy_tag", name="Sloshy", look="murloc_blue", scale=0.6, level=5, role="ambient", summoned=True),
    dict(key="warband_a", name="Greymist Spearman", look="murloc_red", level=18, role="ambient", summoned=True),
    dict(key="warband_b", name="Greymist Spearman", look="murloc_slate", level=18, role="ambient", summoned=True),
    dict(key="warband_c", name="Greymist Huntress", look="murloc_bronze", level=18, role="ambient", summoned=True),
    dict(key="blrrgl_pier", name="Blrrgl the Snatcher", look="murloc_green", level=24, role="quest", at="blrrgl_pier",
         facing=0.6, phase=MARCH, greeting="Here! Here! Over here! I found it first!",
         idle=[("every", 4000, [("emote", "self", "wave"), ("sound", "self", "murloc_fidget")])]),
]

# -- things ------------------------------------------------------------------------------------------------

OBJECTS = [
    # the cove
    dict(key="campfire", model="campfire", name="Cove Fire", at="hub", kind="doodad"),
    dict(key="stilt_hut", model="murloc_hut", name="Stilt Hut", at=["hut_1", "hut_3"], kind="doodad", scale=0.9, facing=4.0),
    dict(key="stilt_hut_2", model="murloc_hut2", name="Stilt Hut", at="hut_2", kind="doodad", scale=0.9, facing=3.6),
    dict(key="hut", model=ORACLE_HUT, name="Greymist Hut", at="hut_5", kind="doodad", scale=0.5, facing=0.6),
    dict(key="blrrgl_hut", model=ORACLE_HUT_2, name="Blrrgl's Hut", at="blrrgl_hut", kind="doodad", scale=0.45, facing=5.4,
         phase=HUB),
    dict(key="hollow_log", model=LOG, name="Hollow Log", at="blrrgl_log", kind="doodad", scale=0.6, facing=1.0, phase=HUB),
    dict(key="cookpot", model=6849, name="Bubbmrl's Pot", at="pot", kind="doodad", scale=1.1),
    dict(key="fish_rack", model=FISH_RACK, name="Fish Rack", at="rack", kind="doodad", facing=1.6),
    dict(key="seer_totem", model=ORACLE_TOTEM, name="Seer's Totem", at="seer_totem", kind="doodad", scale=0.5),
    dict(key="altar", model="murloc_altar", name="Tide Altar", at="altar", kind="doodad", scale=0.5),
    dict(key="lamp", model=ORACLE_LAMP, name="Shell Lamp", at=["lamp_1", "lamp_2"], kind="doodad", scale=0.6),
    dict(key="surfboard", model=SURFBOARD, name="Driftboard", at="surfboard", kind="doodad", scale=0.8, facing=2.0),
    dict(key="net_pile", model=NET_PILE, name="Nets", at="netpile", kind="doodad", scale=0.6, facing=1.2),
    dict(key="holey_net", model=NET_TORN, name="Holey Net", at="net", kind="doodad", scale=0.25, facing=0.9),
    dict(key="baskets", model=BASKET, name="Fish Basket", at="baskets", kind="doodad", scale=0.8),
    dict(key="alarm_drum", model=DRUM, name="Alarm Drum", at="drum", kind="doodad", scale=0.8),
    dict(key="stay_basket", model=CRAB_BASKET, name="Stay Basket", at="stay_basket", kind="doodad", scale=0.9),
    dict(key="go_basket", model=BASKET, name="Go Basket", at="go_basket", kind="use", quest="ch2_moot", consumable=False,
         scale=0.9, beats=[("take", "moot_fish", 1), ("credit", "ch2_moot"), ("object", "fish_pile", "go_basket", 60),
                           ("emote", "ch0:mrrgula", "cheer"), ("sound", "ch0:mrrgula", 11802), ("wait", 1500),
                           ("emote", "villager", "cheer"), ("sound", "villager", "murloc_aggro")]),
    dict(key="sacred_rock", model=BOULDER, name="The Very Important Rock", at="sacred_rock", kind="use", quest="ch2_rock",
         consumable=False, scale=0.35, facing=0.9,
         beats=[("aura", "player", "watching"), ("wait", 40000), ("summon", "war_boat", "horizon_1", 60),
                ("summon", "war_boat", "horizon_2", 60), ("summon", "war_shape", "shapes_1", 45),
                ("summon", "war_shape", "shapes_2", 45), ("wait", 7000), ("credit", "ch2_rock"), ("wait", 2000),
                ("unaura", "player", "watching")]),
    # what quests take in the cove: seaweed, driftwood, the race's buoys
    dict(key="seaweed", model="seaweed", name="Tough Seaweed", kind="loot", loot=[("seaweed", 1, 2)], quest="ch2_nets",
         at=["kelp_1", "kelp_2", "kelp_3", "kelp_4", "kelp_5", "kelp_6", "kelp_7", "kelp_8"]),
    dict(key="driftwood", model=DRIFTWOOD, name="Driftwood", kind="loot", loot=[("driftwood", 1, 1)], quest="ch2_nets",
         scale=0.8, at=["drift_1", "drift_2", "drift_3", "drift_4", "drift_5", "drift_6"]),
    dict(key="buoy_red", model=6366, name="Red Buoy", kind="use", quest="ch2_race", consumable=False, at="buoy_1",
         beats=[("give", "ribbon_red", 1)]),
    dict(key="buoy_blue", model=6366, name="Blue Buoy", kind="use", quest="ch2_race", consumable=False, at="buoy_2",
         beats=[("give", "ribbon_blue", 1), ("aura", "player", "tripped")]),
    dict(key="buoy_green", model=6366, name="Green Buoy", kind="use", quest="ch2_race", consumable=False, at="buoy_3",
         beats=[("give", "ribbon_green", 1)]),
    # Nerelith's rock, and the fish she leaves on it
    dict(key="nerelith_rock", model=BOULDER, name="Flat Rock", at="nerelith_rock", kind="doodad", scale=0.4, facing=2.0,
         phase=HUB),
    dict(key="dawn_fish", model=FISH, name="A Fish on the Rock", at="rock_fish", kind="use", quest="ch2_dawn",
         consumable=False, scale=1.2, phase=HUB,
         beats=[("credit", "ch2_dawn"), ("move", "ch0:nerelith", "nerelith_kneel", "walk"), ("wait", 6000),
                ("face", "ch0:nerelith", "player"), ("state", "ch0:nerelith", "kneel"), ("emote", "ch0:nerelith", "beg"),
                ("say", "ch0:nerelith", "Shh. Ishnu-alah, little one. It's yours. I won't hurt you."), ("wait", 7000),
                ("state", "ch0:nerelith", "none"), ("move", "ch0:nerelith", "nerelith", "walk"), ("wait", 6000),
                ("face", "ch0:nerelith", "nerelith_rock")]),
    # Sinslayer's banner on the beach facing his sea-stack (2.10)
    dict(key="horn_banner", model="naga_banner", name="Sinslayer's Banner", at="sinslayer_horn", kind="use",
         quest="ch2_sinslayer", consumable=True, respawn=120, facing=1.6,
         beats=[("summon", "sinslayer", "sinslayer_rise", 180), ("wait", 600), ("sound", "sinslayer", 7034),
                ("visual", "sinslayer", 47479), ("wait", 1500), ("sound", "sinslayer", "naga_lord_aggro"),
                ("yell", "sinslayer", "Who blows MY horn? A runaway... a runaway with a brand. Chains for you, little fish!")]),
    # Murkdeep's challenge fire (2.20a), his war-totem (2.20b)
    dict(key="challenge_fire", model="campfire", name="Murkdeep's Challenge Fire", at="challenge_fire", kind="use",
         quest="ch2_honor", consumable=True, respawn=90,
         beats=[("take", "offering_fish", 3), ("object", "fire_lit", "challenge_fire", 75),
                ("summon", "hardliner", "wave_1", 120), ("summon", "hardliner", "wave_2", 120),
                ("summon", "hardliner", "wave_3", 120), ("wait", 12000),
                ("summon", "hardliner", "wave_1", 120), ("summon", "hardliner", "wave_2", 120),
                ("summon", "hardliner", "wave_3", 120), ("wait", 12000), ("summon", "murkdeep_foe", "murk_rise", 30),
                ("wait", 500), ("sound", "murkdeep_foe", "murloc_aggro"),
                ("yell", "murkdeep_foe", "Naga-touched! You light MY fire? Then fight me, naga-touched!"),
                ("wait", 30500), ("summon", "murkdeep_yield", "murk_kneel", 150), ("object", "club", "murk_club", 150),
                ("wait", 500), ("state", "murkdeep_yield", "kneel"), ("sound", "murkdeep_yield", "murloc_wound")]),
    dict(key="fire_lit", model="bonfire", name="Challenge Fire", kind="doodad", scale=0.6),
    dict(key="club", model=CLUB, name="Murkdeep's Club", kind="doodad", scale=0.8),
    dict(key="war_totem", model=ORACLE_TOTEM, name="Murkdeep's War-Totem", kind="loot", loot=[("totem", 1, 1)],
         quest="ch2_totem", at="totem", scale=0.45, phase=HUB),
    # the Twilight camp: the cage the sold are pushed into, and the shackles of 2.14 (each frees its own prisoner)
    dict(key="cage", model="cage", name="Murloc Cage", at="cage", kind="doodad", scale=0.8, phase=CAMP),
    dict(key="shackle_1", model=MANACLE, name="Shackle", at="shackle_1", kind="use", quest="ch2_chains", consumable=True,
         respawn=90, phase=CAMP, beats=[("give", "shackle", 1), ("sound", "chained_1", 1164), ("state", "chained_1", "none"),
                                        ("emote", "chained_1", "bow"), ("sound", "chained_1", "murloc_fidget"), ("wait", 2000),
                                        ("move", "chained_1", "flee_point", "run"), ("wait", 3000), ("despawn", "chained_1")]),
    dict(key="shackle_2", model=MANACLE, name="Shackle", at="shackle_2", kind="use", quest="ch2_chains", consumable=True,
         respawn=90, phase=CAMP, beats=[("give", "shackle", 1), ("sound", "chained_2", 1164), ("state", "chained_2", "none"),
                                        ("emote", "chained_2", "bow"), ("sound", "chained_2", "murloc_fidget"), ("wait", 2000),
                                        ("move", "chained_2", "flee_point", "run"), ("wait", 3000), ("despawn", "chained_2")]),
    dict(key="shackle_3", model=MANACLE, name="Shackle", at="shackle_3", kind="use", quest="ch2_chains", consumable=True,
         respawn=90, phase=CAMP, beats=[("give", "shackle", 1), ("sound", "chained_3", 1164), ("state", "chained_3", "none"),
                                        ("emote", "chained_3", "bow"), ("sound", "chained_3", "murloc_fidget"), ("wait", 2000),
                                        ("move", "chained_3", "flee_point", "run"), ("wait", 3000), ("despawn", "chained_3")]),
    dict(key="shackle_4", model=MANACLE, name="Shackle", at="shackle_4", kind="use", quest="ch2_chains", consumable=True,
         respawn=90, phase=CAMP, beats=[("give", "shackle", 1), ("sound", "chained_4", 1164), ("state", "chained_4", "none"),
                                        ("emote", "chained_4", "bow"), ("sound", "chained_4", "murloc_fidget"), ("wait", 2000),
                                        ("move", "chained_4", "flee_point", "run"), ("wait", 3000), ("despawn", "chained_4")]),
    dict(key="shackle_5", model=MANACLE, name="Shackle", at="shackle_5", kind="use", quest="ch2_chains", consumable=True,
         respawn=90, phase=CAMP, beats=[("give", "shackle", 1), ("sound", "chained_5", 1164), ("state", "chained_5", "none"),
                                        ("emote", "chained_5", "bow"), ("sound", "chained_5", "murloc_fidget"), ("wait", 2000),
                                        ("move", "chained_5", "flee_point", "run"), ("wait", 3000), ("despawn", "chained_5")]),
    # Auberdine: the WANTED poster beside the town's board; the wagons, their sacks; Gubber Blump's beach
    dict(key="wanted_poster", model=POSTER, name="WANTED Poster", kind="loot", loot=[("poster", 1, 1)], quest="ch2_wanted",
         at="poster", facing=4.6),
    dict(key="wagon", model=WAGON, name="Grain Wagon", at=["wagon_a", "wagon_b"], kind="doodad", scale=0.8, facing=1.9),
    dict(key="paid_sack_a", model="sack", name="Sack of Grain", at=["sack_1", "sack_2", "sack_3"], kind="use", quest="ch2_pearls",
         consumable=True, respawn=60, beats=[("take", "pearls", 1), ("give", "grain", 1),
                                             ("object", "left_pearl", "pearl_cart_a", 600)]),
    dict(key="paid_sack_b", model="sack", name="Sack of Grain", at=["sack_4", "sack_5", "sack_6"], kind="use", quest="ch2_pearls",
         consumable=True, respawn=60, beats=[("take", "pearls", 1), ("give", "grain", 1),
                                             ("object", "left_pearl", "pearl_cart_b", 600)]),
    dict(key="stolen_sack", model="sack", name="Sack of Grain", at=["take_1", "take_2", "take_3", "take_4", "take_5", "take_6"],
         kind="use", quest="ch2_grain", consumable=True, respawn=60,
         beats=[("give", "grain", 1), ("state", "carter", "none"), ("emote", "carter", "point"),
                ("yell", "carter", "Thieves! Thieves at the wagons! Sentinels!", None, 2740), ("wait", 7000),
                ("state", "carter", "sleep")]),
    dict(key="left_pearl", model="great_pearl", name="A Pearl", kind="doodad", scale=0.12),
    dict(key="sunk_box", model="chest", name="Gubber's Tackle Box", kind="loot", loot=[("tackle_box", 1, 1)],
         quest="ch2_tackle", at="tackle_sunk", scale=0.5, facing=0.7),
    dict(key="bait_basket", model=BASKET, name="Gubber's Bait Basket", at="gubber_basket", kind="use", quest="ch2_tackle",
         consumable=False, scale=0.7,
         beats=[("take", "tackle_box", 1), ("object", "box_left", "box_left", 120), ("credit", "ch2_tackle"),
                ("emote", "sloshy_tag", "cheer"), ("sound", "sloshy_tag", "baby_murloc"), ("wait", 1500),
                ("move", "sloshy_tag", "sloshy_peek", "run"), ("wait", 2500), ("emote", "sloshy_tag", "wave"),
                ("wait", 1500), ("emote", "sloshy_tag", "wave"), ("sound", "sloshy_tag", "baby_murloc")]),
    dict(key="box_left", model="chest", name="Gubber's Tackle Box", kind="doodad", scale=0.5),
    dict(key="prize_plaque", model=PLAQUE, name="Plaque", at="prize_mount", kind="doodad", scale=1.4, facing=4.7),
    dict(key="prize_fish", model=FISH_BIG, name="Gubber's Prize Fish", kind="loot", loot=[("prize_fish", 1, 1)],
         quest="ch2_prize", at="prize_mount", scale=1.6, facing=4.7),
    # the old elven pier at the Strand's north end (a ruin in the shallows: chapter 3 camps on it)
    dict(key="pier_ruin", model=ELF_RUIN, name="Old Elven Pier", at=["pier_ruin_1", "pier_ruin_3"], kind="doodad", scale=0.7,
         facing=1.2),
    dict(key="pier_ruin_2", model=ELF_RUIN_2, name="Old Elven Pier", at="pier_ruin_2", kind="doodad", scale=0.7, facing=2.6),
    dict(key="pier_pillar", model=PILLAR, name="Drowned Pillar", at="drowned_pier", kind="doodad", scale=0.6, facing=0.3),

    # set out by scenes: sand drawings, the welcome fish, the new net, the ledger, trophies on Blrrgl's wall
    dict(key="gift_fish", model=FISH, name="A Fish", kind="doodad", scale=1.1),
    dict(key="own_fish_obj", model=FISH_BIG, name="Your Own Fish", kind="doodad", scale=0.9),
    dict(key="fish_pile", model=FISH_RACK, name="Fish in the Go Basket", kind="doodad", scale=0.3),
    dict(key="new_net", model=NET_NEW, name="New Net", kind="doodad", scale=0.25),
    dict(key="draw_bow", model=BOW, name="Drawing in the Sand", kind="doodad", scale=0.6),
    dict(key="draw_naga", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.5),
    dict(key="draw_tear", model=CRYSTAL, name="Drawing in the Sand", kind="doodad", scale=0.15),
    dict(key="draw_line", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.4),
    dict(key="draw_chain", model=MANACLE, name="Drawing in the Sand", kind="doodad", scale=0.4),
    dict(key="draw_little", model="murloc_altar", name="Drawing in the Sand", kind="doodad", scale=0.12),
    dict(key="draw_club", model=CLUB, name="Drawing in the Sand", kind="doodad", scale=0.4),
    dict(key="draw_kneel", model="murloc_altar", name="Drawing in the Sand", kind="doodad", scale=0.08),
    dict(key="draw_poster", model=POSTER, name="Drawing in the Sand", kind="doodad", scale=0.25),
    dict(key="draw_start", model=TRIDENT, name="Starting Line", kind="doodad", scale=0.7),
    dict(key="map_coast", model=DRIFTWOOD, name="The Coast, Drawn", kind="doodad", scale=0.4),
    dict(key="map_temple", model=PILLAR, name="The Temple, Drawn", kind="doodad", scale=0.1),
    dict(key="map_tree", model=TREE_BANNER, name="The Tree, Drawn", kind="doodad", scale=0.2),
    dict(key="map_banner", model=HORDE_BANNER, name="The Banner, Drawn", kind="doodad", scale=0.15),
    dict(key="ledger_obj", model=BOOK, name="Twilight Ledger", kind="doodad", scale=0.5),
    dict(key="prize_basket", model=BASKET, name="Prize Basket", kind="doodad", scale=1.0),
    dict(key="totem_set", model=ORACLE_TOTEM, name="Murkdeep's War-Totem", kind="doodad", scale=0.45),
    dict(key="hung_poster", model=POSTER, name="WANTED Poster (upside down)", kind="doodad", scale=0.5),
    dict(key="hung_fish", model=FISH_BIG, name="Gubber's Prize Fish", kind="doodad", scale=1.4),
]

# -- items -----------------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for and hand over (their names are the one thing a murloc reads)
    dict(key="spear", name="Greymist Fishing Spear", icon="spear", description="Mother Mrrgula's own. Bring it back."),
    dict(key="own_fish", name="Your Own Fish", kind="food", level=15, icon="fish",
         description="The first thing you have ever owned. Nobody takes it."),
    dict(key="mud_shell", name="Mud-Caked Shell", icon="shell", description="Mudpie's. Mudpie never gives anyone a shell."),
    dict(key="spiral_shell", name="Spiral Shell", icon=18054, description="A hat. For a very small, very proud fry."),
    dict(key="seaweed", name="Tough Seaweed", icon=7078, stack=8),
    dict(key="driftwood", name="Driftwood", icon=10190, stack=4),
    dict(key="moonstone", name="Moonstone Earring", icon=9849, description="It catches the moonlight, even under water."),
    dict(key="horn", name="Stormscale Hunting Horn", icon=24188, description="The Stormscale blow it to call their lord."),
    dict(key="chain", name="Slave-Catcher's Chain", icon=4829, description="Heavy, cold, and worn smooth by murloc ankles."),
    dict(key="poster", name="WANTED Poster", icon=20710,
         description="A murloc with a ring-shaped scar on its shoulder. The nose is too big."),
    dict(key="tackle_box", name="Gubber's Tackle Box", icon=9162, description="Hooks, floats, a pipe, and a very wet sandwich."),
    dict(key="prize_fish", name="Gubber's Prize Fish", icon="fish", description="Mounted. Varnished. Enormous."),
    dict(key="shackle", name="Broken Shackle", icon=7132, stack=5),
    dict(key="ledger", name="Twilight Ledger", icon=14008, description="Columns of marks, and a drawing of something with many heads."),
    dict(key="ribbon_red", name="Red Buoy Ribbon", icon=32746),
    dict(key="ribbon_blue", name="Blue Buoy Ribbon", icon=32746),
    dict(key="ribbon_green", name="Green Buoy Ribbon", icon=32746),
    dict(key="offering_fish", name="Offering Fish", icon="fish", stack=3),
    dict(key="totem", name="Murkdeep's War-Totem", icon=10365, description="Whoever holds it has warriors."),
    dict(key="sand_map", name="Nerelith's Sand-Map", icon=7047,
         description="The coast, a temple, a tree that might help, and a banner that might not."),
    dict(key="pearls", name="Blrrgl's Pearls", icon="pearl", stack=6,
         description="Six pearls from Blrrgl's hollow log. One of them came out of your cheek."),
    dict(key="grain", name="Sack of Auberdine Grain", icon=1297, stack=6),
    dict(key="fin", name="Thresher Fin", icon=10043, stack=6),
    dict(key="moot_fish", name="Moot Fish", icon="fish", description="One fish, two baskets. Choose."),

    # rewards (levels 15 to 19: the game's quests' greens at these levels)
    dict(key="greymist_wraps", name="Greymist Wristwraps", kind="armor:cloth:wrist", quality=2, level=15,
         stats=[("int", 2), ("spi", 2)]),
    dict(key="brother_bracers", name="Brother's Bracers", kind="armor:leather:wrist", quality=2, level=15,
         stats=[("agi", 2), ("sta", 2)]),
    dict(key="ridge_bracers", name="Ridge-Watch Bracers", kind="armor:mail:wrist", quality=2, level=15,
         stats=[("str", 2), ("sta", 2)]),
    dict(key="netknot_cloak", name="Net-Knot Cloak", kind="armor:cloth:back", quality=2, level=15, stats=[("sta", 2), ("spi", 1)]),
    dict(key="saltwind_moonstone", name="Saltwind Moonstone", kind="ring", quality=2, level=16, stats=[("sta", 2), ("spi", 3)],
         description="Liyara Saltwind's. Her sister gave it to you."),
    dict(key="siren_silk", name="Siren-Silk Leggings", kind="armor:cloth:legs", quality=2, level=17,
         stats=[("int", 4), ("sta", 3)]),
    dict(key="hound_hide", name="Hound-Hide Leggings", kind="armor:leather:legs", quality=2, level=17,
         stats=[("agi", 4), ("sta", 3)]),
    dict(key="stormscale_legs", name="Stormscale Legguards", kind="armor:mail:legs", quality=2, level=17,
         stats=[("str", 4), ("sta", 3)]),
    dict(key="poster_pin", name="Poster-Pin Dagger", kind="weapon:dagger", quality=2, level=17, stats=[("agi", 3), ("sta", 2)]),
    dict(key="board_mallet", name="Noticeboard Mallet", kind="weapon:mace", quality=2, level=17, stats=[("str", 3), ("sta", 2)]),
    dict(key="shackle_gauntlets", name="Shackle-Breaker Gauntlets", kind="armor:mail:hands", quality=2, level=17,
         stats=[("str", 3), ("sta", 3)]),
    dict(key="freed_gloves", name="Freed-Fin Gloves", kind="armor:leather:hands", quality=2, level=17,
         stats=[("agi", 3), ("sta", 3)]),
    dict(key="kelpweave_gloves", name="Kelpweave Gloves", kind="armor:cloth:hands", quality=2, level=17,
         stats=[("int", 3), ("spi", 3)]),
    dict(key="seer_charm", name="Seer's Smoke-Shell", kind="offhand", quality=2, level=17, stats=[("int", 3), ("spi", 3)]),
    dict(key="moot_gaff", name="Silverfin Gaff", kind="weapon:dagger", quality=2, level=18, stats=[("agi", 3), ("sta", 3)]),
    dict(key="moot_cord", name="Moot-Day Cord", kind="neck", quality=2, level=18, stats=[("sta", 3), ("spi", 3)]),
    dict(key="cove_spear", name="Cove-Defender's Spear", kind="weapon:spear", quality=2, level=18,
         stats=[("str", 6), ("sta", 4)]),
    dict(key="tidewall_shield", name="Tidewall Shield", kind="shield", quality=2, level=18, stats=[("sta", 3), ("str", 2)]),
    dict(key="greymist_staff", name="Greymist Tidestaff", kind="weapon:staff", quality=2, level=18,
         stats=[("int", 6), ("spi", 4)]),
    dict(key="hard_pauldrons", name="Hardliner's Pauldrons", kind="armor:mail:shoulder", quality=2, level=19,
         stats=[("str", 4), ("sta", 3)]),
    dict(key="hard_spaulders", name="Hardliner's Spaulders", kind="armor:leather:shoulder", quality=2, level=19,
         stats=[("agi", 4), ("sta", 3)]),
    dict(key="hard_mantle", name="Hardliner's Mantle", kind="armor:cloth:shoulder", quality=2, level=19,
         stats=[("int", 4), ("spi", 3)]),
    dict(key="sentinel_cloak", name="Folded Sentinel's Cloak", kind="armor:cloth:back", quality=2, level=18,
         stats=[("agi", 2), ("sta", 3)], description="Nerelith's, from when she still stood watch."),
    dict(key="grain_cord", name="Grain-Sack Cord", kind="armor:cloth:waist", quality=2, level=19, stats=[("int", 4), ("sta", 3)]),
    dict(key="grain_belt", name="Wagon-Strap Belt", kind="armor:leather:waist", quality=2, level=19, stats=[("agi", 4), ("sta", 3)]),
    dict(key="grain_girdle", name="Carter's Chain Girdle", kind="armor:mail:waist", quality=2, level=19,
         stats=[("str", 4), ("sta", 3)]),
    dict(key="warspear", name="Greymist War-Spear", kind="weapon:spear", quality=2, level=19, stats=[("str", 7), ("sta", 5)],
         description="Carried south by the Greymist war band."),
    dict(key="shore_dirk", name="Shore-Stalker's Dirk", kind="weapon:dagger", quality=2, level=19, stats=[("agi", 4), ("sta", 3)]),
    dict(key="seer_rod", name="Tide-Seer's Rod", kind="weapon:staff", quality=2, level=19, stats=[("int", 7), ("spi", 5)]),
]

# -- auras -------------------------------------------------------------------------------------------------

AURAS = [
    dict(key="muddy", name="Muddy", kind="mark", seconds=30, icon=3650, visual=776, text="Pelted with mud by the Greymist fry."),
    dict(key="tripped", name="Tripped", kind="slow", percent=60, seconds=4, icon=1715, text="Mrrk's foot. Somehow."),
    dict(key="watching", name="Watching the Tide", kind="root", seconds=50, icon=6196,
         text="Sit. Watch. Don't move. The rock knows if you move."),
    dict(key="war_paint", name="War Paint", kind="mark", seconds=3600, icon=6673, visual=6539,
         text="Thresher-fin red, from brow to belly. Very fierce."),
]

# -- the tribe's people at the cove, and the game's creatures in the murlocs' phase ---------------------------

SPAWNS = [
    dict(npc="ch0:mrrgula", at="mrrgula", facing=0.8),                                     # (always: she rules the cove)
    dict(npc="ch1:blrrgl", at="blrrgl", facing=5.0, phase=HUB),
    dict(npc="ch1:sloshy", at="sloshy", facing=4.7, wander=3.0, respawn=60, phase=SLOSHY),
    dict(npc="ch0:mrrk", at="mrrk", facing=5.9, phase=HUB),
    dict(npc="ch0:nerelith", at="nerelith", facing=1.7, phase=HUB),
    # Murkdeep's raiders past the western rock (2.04), with the game's own there
    dict(npc=2205, at=["raid_g1", "raid_g3"], wander=4.0, respawn=120, phase=HUB),
    dict(npc=2206, at=["raid_g2", "raid_g4"], wander=4.0, respawn=120, phase=HUB),
    # reef crawlers toward Murkdeep's camp (2.05)
    dict(npc=2235, at=["crab_1", "crab_2", "crab_3", "crab_4"], wander=5.0, respawn=60, phase=HUB),
    # the Stormscale slave-catchers on the north beach (2.08, 2.09)
    dict(npc=2179, at=["wr_1", "wr_2", "wr_3", "wr_4", "wr_5", "wr_6"], wander=5.0, respawn=90, phase=HUB),
    dict(npc=2180, at=["siren_1", "siren_2", "siren_3", "siren_4", "siren_5"], wander=4.0, respawn=90, phase=HUB),
    dict(npc=2181, at=["myr_1", "myr_2", "myr_3", "myr_4", "myr_5"], wander=4.0, respawn=90, phase=HUB),
    # more of the Twilight's Hammer's disciples at the Master's Glaive (2.15)
    dict(npc=2338, at=["disc_1", "disc_2", "disc_3", "disc_4"], wander=3.0, respawn=90, phase=HUB),
    # the march (2.25): a Stormscale ambush on the beach, Twilight thugs on the dunes
    dict(npc=2179, at=["amb_n1", "amb_n3"], wander=3.0, respawn=90, phase=MARCH),
    dict(npc=2181, at=["amb_n2", "amb_n4"], wander=3.0, respawn=90, phase=MARCH),
    dict(npc=2339, at=["amb_t1", "amb_t2", "amb_t3"], wander=3.0, respawn=90, phase=MARCH),
]

GRAVEYARDS = [
    dict(at="graveyard", name="Greymist Cove", phase=HUB, facing=0.2),
]

# -- the quests --------------------------------------------------------------------------------------------

QUESTS = [
    # 2.01: the Greymist (Blrrgl leads you into the cove; its sentries cross spears; Mrrgula comes down)
    dict(key="ch2_arrival", title="The Greymist", giver="ch1:blrrgl_free", ender="ch0:mrrgula", level=14, min=13, xp=7,
         tone="serious", prev="ch1:ch1_breakout",
         goal="Follow Blrrgl along the beach to the south-west, into Greymist Cove behind the rocks, past its sentries, and go to "
              "Mother Mrrgula.",
         text="Murlocs! Free ones! I smell their fires... that way, along the sand, in the cove behind the rocks. They have "
              "spears. Big spears. You go first. You are braver. I am right behind you. Very close behind.",
         progress="Who swims into my cove? Closer. Let me see you.",
         reward="Naga-marked. Oh... oh, little one. Who did this? The long ones. Always the long ones. Here. Eat. "
                "Nobody is hungry in my cove.",
         details=["talk", "point", "beg"], reward_emotes=["cry", "talk"],
         accept=[("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("emote", "self", "beg"),
                 ("wait", 1500), ("move", "self", "blrrgl_lead", "run"), ("wait", 9000),
                 ("face", "sentry_l", "blrrgl_lead"), ("face", "sentry_r", "blrrgl_lead"), ("state", "sentry_l", 27),
                 ("state", "sentry_r", 27), ("emote", "sentry_l", "attack"), ("emote", "sentry_r", "attack"),
                 ("yell", "sentry_l", "Stop! Who swims into the cove? Who?", None, "murloc_alert"), ("wait", 2000),
                 ("state", "self", "dead"), ("sound", "self", "murloc_wound"), ("wait", 2500), ("state", "self", "none"),
                 ("move", "self", "grovel_1", "walk"), ("wait", 1500), ("emote", "self", "beg"),
                 ("move", "self", "grovel_2", "walk"), ("wait", 1500), ("emote", "self", "beg"),
                 ("move", "self", "grovel_3", "walk"), ("wait", 1500), ("emote", "self", "beg"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "sentry_l", "laugh"),
                 ("state", "sentry_l", "none"), ("state", "sentry_r", "none"), ("face", "sentry_l", "hub"),
                 ("emote", "sentry_l", "point"), ("wait", 6000), ("face", "sentry_l", "gate_out"),
                 ("face", "sentry_r", "gate_out"), ("move", "self", "ch1:blrrgl_free", "walk")],
         complete=[("state", "self", "none"), ("move", "self", "greet", "walk"), ("wait", 3500), ("face", "self", "player"),
                   ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"), ("wait", 1800), ("face", "self", "pens_way"),
                   ("sound", "self", "naga_hiss"), ("emote", "self", "rude"), ("wait", 2000), ("face", "self", "player"),
                   ("object", "gift_fish", "greet_fish", 30), ("give", 787, 1), ("emote", "self", "beg"),
                   ("emote", "ch1:blrrgl", "beg"), ("sound", "ch1:blrrgl", "murloc_fidget"), ("wait", 3000),
                   ("emote", "villager", "cheer"), ("sound", "villager", "murloc_aggro"), ("wait", 2000),
                   ("move", "self", "mrrgula", "walk"), ("wait", 3500), ("face", "self", "hub"), ("state", "self", "sit")],
         poi=["hub"]),

    # 2.02: a fish you keep (the first thing a slave ever owned)
    dict(key="ch2_fish", title="A Fish You Keep", giver="ch0:mrrgula", ender="ch0:mrrgula", level=14, min=13, xp=8,
         tone="serious", prev="ch2_arrival", source="spear", kill=[("darter", 5)],
         emotes=[("ch0:mrrgula", "eat", 1, [("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "yes"),
                                            ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "villager", "cheer"),
                                            ("sound", "villager", "murloc_aggro"), ("emote", "wader", "cheer"),
                                            ("sound", "sentry_l", "murloc_aggro"), ("wait", 3000), ("state", "self", "sit")])],
         goal="Spear 5 Silverfin Shoals in the cove's shallows with the Greymist Fishing Spear, then eat in front of Mother "
              "Mrrgula (/eat at her).",
         text="Hungry? No. Not hungry... starving. I can see your ribs. Take my spear. The shoals swim in the shallows, there, "
              "by the huts. 5 fish for the pot. And then you eat. Here. In front of me. Where I can see.",
         progress="Eat, little one. Here. Where I can see.",
         reward="One for the pot. One for the pot. One for the pot... and this one? This one is yours. Nobody takes it. "
                "Nobody. Not ever again.",
         details=["talk", "point", "eat"], reward_emotes=["talk", "yes"], rewards=["own_fish"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1200), ("face", "self", "shoals"),
                 ("emote", "self", "point"), ("sound", "self", "splash_small"), ("wait", 1800), ("face", "self", "player"),
                 ("emote", "self", "eat"), ("wait", 1500), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "hub"),
                 ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("object", "own_fish_obj", "greet_fish", 20), ("emote", "self", "point"),
                   ("sound", "self", 1186), ("wait", 1500), ("state", "self", "sit"), ("wait", 5000), ("emote", "self", "yes"),
                   ("emote", "villager", "cheer"), ("sound", "villager", "murloc_aggro"), ("sound", "sentry_r", "murloc_aggro"),
                   ("emote", "wader", "cheer")],
         poi=["shoals", "mrrgula"]),

    # 2.03: the fry who pelt newcomers with mud (player emotes)
    dict(key="ch2_mud", title="Mud Throwers", giver="ch1:sloshy", ender="ch1:sloshy", level=14, min=13, xp=7, tone="funny",
         prev="ch2_arrival",
         emotes=[("gloob", "laugh", 1, [("emote", "self", "laugh"), ("sound", "self", "baby_murloc"), ("wait", 1500),
                                        ("emote", "self", "laugh")]),
                 ("pibbl", "dance", 1, [("state", "self", "dance"), ("sound", "self", "baby_murloc_dance"), ("wait", 4000),
                                        ("state", "self", "none"), ("emote", "self", "cheer")]),
                 ("snorkl", "wave", 1, [("emote", "self", "wave"), ("sound", "self", "baby_murloc"), ("wait", 1200),
                                        ("emote", "self", "shy")]),
                 ("mudpie", "dance", 1, [("state", "self", "dance"), ("sound", "self", "baby_murloc"), ("wait", 3000),
                                         ("state", "self", "none"), ("give", "mud_shell", 1), ("emote", "self", "shy")])],
         goal="Make peace with the 4 Greymist fry on the cove's north beach: /laugh at Gloob, /dance with Pibbl, /wave at Snorkl "
              "and /dance with Mudpie.",
         text="Mrgl... mrgl... they threw mud! At me! In my ears! 4 of them, on the beach by the big rock. They throw mud at all "
              "the new ones. You are new too. Make them stop? Make them like us?",
         progress="Still muddy. Still very muddy.",
         reward="They like us! They LIKE us! Mudpie gave you a shell? Mudpie never gives shells. Never ever!",
         details=["cry", "point"], reward_emotes=["cheer", 94],
         accept=[("aura", "self", "muddy"), ("emote", "self", "cry"), ("sound", "self", "baby_murloc"), ("wait", 1500),
                 ("face", "self", "fry_gang"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "cry"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "beg")],
         complete=[("unaura", "self", "muddy"), ("emote", "self", "cheer"), ("sound", "self", "baby_murloc"),
                   ("emote", "gloob", "wave"), ("emote", "pibbl", "wave"), ("state", "self", "dance"), ("wait", 4000),
                   ("state", "self", "none")],
         poi=["fry_gang"]),

    # 2.04: brother murlocs (Murkdeep's raiders: the same people)
    dict(key="ch2_raiders", title="Brother Murlocs", giver="ch0:mrrgula", ender="ch0:mrrgula", level=15, xp=7, tone="serious",
         prev="ch2_fish", kill=[(2205, 4), (2206, 4)],
         goal="Drive off Murkdeep's raiders: kill 4 Greymist Warriors and 4 Greymist Hunters on the beach past the cove's western "
              "rock and at Murkdeep's camp up the shore.",
         text="Look. Murlocs on the beach past the rock, spears pointed at my cove. Greymist, like us. Murkdeep's. They say "
              "you are naga-touched, and anyone who feeds you is too. 8 of them. Make them go home.",
         progress="Are they gone? I still hear them.",
         reward="They will come back. Murlocs always come back... but not today. Today we fish.",
         details=["point", "talk"], reward_emotes=["yes", "talk"], choice=["greymist_wraps", "brother_bracers", "ridge_bracers"],
         accept=[("state", "self", "none"), ("face", "self", "raid_edge"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "hub"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "applaud"),
                 ("wait", 1500), ("emote", "self", "cry"), ("sound", "self", 11802), ("wait", 2500),
                 ("sound", "self", "murloc_alert"), ("wait", 1500), ("state", "self", "sit")],
         complete=[("emote", "self", "yes"), ("sound", "self", "murloc_fidget2"), ("emote", "sentry_l", "cheer"),
                   ("emote", "grrlok", "flex"), ("sound", "grrlok", "murloc_aggro")],
         poi=["raid_edge", "murk_camp"]),

    # 2.05: a hat for Sloshy
    dict(key="ch2_hat", title="A Hat for Sloshy", giver="ch1:sloshy", ender="ch1:sloshy", level=15, xp=7, tone="stupid",
         prev="ch2_mud", items=[("spiral_shell", 1)], drops={"spiral_shell": [(2235, 30)]},
         goal="Kill Reef Crawlers on the beach north-east of the cove, toward Murkdeep's camp, until one gives up a Spiral Shell "
              "for Sloshy.",
         text="That crab. That one! It has a hat. A twisty hat, a shell like a horn! I want one. I will be the tallest fry. "
              "Taller than Mudpie. Please? Please please please?",
         progress="Hat? Hat? Is it a hat yet?",
         reward="My HAT! Look at me! Look how tall I am! Look how... where did everything go? Why is it dark?",
         details=["point", "cheer"], reward_emotes=["cheer", "laugh"], rewards=[4593],
         accept=[("face", "self", "crawler_way"), ("emote", "self", "point"), ("sound", "self", "baby_murloc"), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "flex"), ("wait", 1500), ("emote", "self", "cheer"),
                 ("sound", "self", "baby_murloc")],
         complete=[("emote", "self", "cheer"), ("visual", "self", 56494), ("sound", "self", "baby_murloc"), ("wait", 1500),
                   ("move", "self", "hut_post", "run"), ("wait", 3500), ("sound", "self", 916), ("state", "self", "dead"),
                   ("sound", "self", "baby_murloc"), ("wait", 2500), ("state", "self", "none"), ("emote", "self", "laugh"),
                   ("move", "self", "sloshy", "walk")],
         poi=["crab_1", "crab_4"]),

    # 2.06: nets of our own
    dict(key="ch2_nets", title="Nets of Our Own", giver="netweaver", ender="netweaver", level=15, xp=7, tone="boring",
         prev="ch2_fish", items=[("seaweed", 8), ("driftwood", 4)],
         goal="Gather 8 Tough Seaweed in the cove's shallows and 4 pieces of Driftwood on the beach north-east of the cove for "
              "Grrma Holenet.",
         text="This is a net. Look through it. You can see the whole sea through it! That is the problem. Seaweed, 8 strands, "
              "the tough kind. Driftwood, 4 pieces, for floats. Then we catch fish and don't just look at them.",
         progress="The fish swim through. Hello, fish. Goodbye, fish.",
         reward="Seaweed... wood... now watch. Over, under, knot. Over, under, knot. A net! A net with no sea in it!",
         details=["point", "no"], reward_emotes=["cheer", "talk"], rewards=["netknot_cloak"],
         accept=[("state", "self", "none"), ("face", "self", "net"), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", "kneel"), ("sound", "self", "murloc_fidget2"), ("wait", 2500), ("emote", "self", "no"),
                 ("face", "self", "player"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "kneel"), ("sound", "self", 1217), ("wait", 1500),
                   ("emote", "self", "kneel"), ("sound", "self", 1217), ("object", "new_net", "net", 120), ("wait", 1500),
                   ("emote", "self", "cheer"), ("emote", "snapjaw", "applaud"), ("wait", 2000), ("state", "self", "work")],
         poi=["kelp_2", "drift_3"]),

    # 2.07: a fish on the rock (Nerelith Saltwind, the first land-walker who is kind)
    dict(key="ch2_dawn", title="A Fish on the Rock", giver="ch1:blrrgl", ender="ch0:nerelith", level=15, xp=7, tone="serious",
         path="hero", prev="ch2_raiders", event="The fish on the rock found", rep=[(69, 250)],
         goal="Find the fish left on the flat rock of the north beach, past Murkdeep's camp, and whoever leaves it there every "
              "dawn. Then speak to her.",
         text="Every dawn there is a fish on a rock up the shore. A fat fish. Every dawn! Nobody leaves fish. Fish don't leave "
              "fish. Something with a bow is there, I saw it. Bow, string, zip... dead murloc. You go look. I will guard the cove.",
         progress="You came back. I hoped you would.",
         reward="So the little ones of the pens are real. I am Nerelith. My sister drowned off this shore... I leave a fish for "
                "anyone who is hungry. You were hungry.",
         details=["talk", "attack", "no"], reward_emotes=["kneel", "talk"],
         accept=[("object", "draw_bow", "blrrgl_draw", 30), ("emote", "self", "kneel"), ("sound", "self", 1194), ("wait", 1500),
                 ("emote", "self", "attack"), ("wait", 900), ("state", "self", "dead"), ("sound", "self", "murloc_death"),
                 ("wait", 2000), ("state", "self", "none"), ("emote", "self", "no"), ("wait", 900), ("emote", "self", "no"),
                 ("sound", "self", "murloc_fidget")],
         complete=[("face", "self", "player"), ("state", "self", "kneel"), ("wait", 2500), ("emote", "self", "talk"),
                   ("wait", 2000), ("state", "self", "none"), ("emote", "self", "bow")],
         poi=["nerelith_rock"]),

    # 2.08: her sister's moonstone
    dict(key="ch2_moonstone", title="Her Sister's Moonstone", giver="ch0:nerelith", ender="ch0:nerelith", level=16, xp=7,
         tone="serious", path="hero", prev="ch2_dawn", items=[("moonstone", 1)], drops={"moonstone": [(2180, 30)]},
         rep=[(69, 350)],
         goal="Take the Moonstone Earring from the Stormscale Sirens on the beach north of Nerelith's rock.",
         text="Do you see them, down the shore? The Stormscale. One of their sirens wears my sister's moonstone. Liyara wore "
              "one in each ear... the sea gave me back one. I would like the other one back.",
         progress="Did you find it? It catches the moonlight. You cannot miss it.",
         reward="Liyara's... after so long. Hold out your hand. One for me, one for you. She would have laughed at that. "
                "A murloc with a moonstone.",
         details=["kneel", "point"], reward_emotes=["kneel", "bow"], rewards=["saltwind_moonstone"],
         accept=[("face", "self", "player"), ("state", "self", "kneel"), ("object", "draw_naga", "draw_a", 30),
                 ("wait", 1500), ("object", "draw_tear", "draw_b", 30), ("emote", "self", "point"), ("wait", 2500),
                 ("state", "self", "none"), ("emote", "self", "talk"), ("face", "self", "band_center"), ("emote", "self", "point"),
                 ("wait", 2000), ("face", "self", "player")],
         complete=[("state", "self", "kneel"), ("music", 6076), ("wait", 4000), ("emote", "self", "cry"), ("wait", 2500),
                   ("state", "self", "none"), ("emote", "self", "bow")],
         poi=["band_center"]),

    # 2.09: Sinslayer's hounds
    dict(key="ch2_hounds", title="Sinslayer's Hounds", giver="ch0:mrrgula", ender="ch0:mrrgula", level=16, xp=7, tone="serious",
         prev="ch2_raiders", kill=[(2179, 6), (2181, 4)],
         goal="Kill 6 Stormscale Wave Riders and 4 Stormscale Myrmidons hunting runaways on the north beach, past Nerelith's rock.",
         text="Runaways come to my cove. From the pens, from everywhere the long ones raid. Some never come. The Stormscale wait "
              "for them up the shore and drag them back for silver. 10 of them, little one. 10.",
         progress="The sand still smells of them.",
         reward="Good. Now the shore is wider. Now more of you can get through.",
         details=["kneel", "attack"], reward_emotes=["yes"],
         accept=[("state", "self", "none"), ("move", "self", "mrrgula_draw", "walk"), ("wait", 2500), ("emote", "self", "kneel"),
                 ("object", "draw_line", "mrrgula_draw_a", 30), ("sound", "self", 1194), ("wait", 1500),
                 ("object", "draw_chain", "mrrgula_draw_b", 30), ("wait", 1200), ("object", "draw_little", "mrrgula_draw_c", 30),
                 ("wait", 1500), ("emote", "self", "attack"), ("sound", "self", 1225), ("wait", 1500),
                 ("move", "self", "mrrgula", "walk"), ("wait", 2500), ("face", "self", "hub"), ("state", "self", "sit")],
         complete=[("emote", "self", "yes"), ("sound", "self", "murloc_fidget2"), ("emote", "grrlok", "flex"),
                   ("emote", "sentry_l", "cheer")],
         poi=["band_center"]),

    # 2.10: Lord Sinslayer (his own horn calls him)
    dict(key="ch2_sinslayer", title="Lord Sinslayer", giver="ch1:blrrgl", ender="ch1:blrrgl", level=17, xp=8, tone="serious",
         path="hero", prev="ch2_hounds", source="horn", items=[("chain", 1)], drops={"chain": [("sinslayer", 100)]},
         rep=[(69, 250)],
         goal="Blow the Stormscale Hunting Horn at Sinslayer's Banner, on the beach facing the sea-stack at the far end of the "
              "north beach, and take the Slave-Catcher's Chain from Lord Sinslayer when he answers.",
         text="Look what I found on the long ones! A horn. Their horn. They blow it, and their lord comes. Lord Sinslayer. The one "
              "with the chains. Big chains. You blow it. Not me. My cheeks are... tired.",
         progress="Did he come? Is he gone? Can I come out now?",
         reward="His chain! The chain he drags us with! Watch. Watch this...",
         details=["talk", "eat", "no"], reward_emotes=["cheer", "laugh"],
         choice=["siren_silk", "hound_hide", "stormscale_legs"],
         accept=[("emote", "self", "talk"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("emote", "self", "eat"),
                 ("wait", 1500), ("emote", "self", "no"), ("move", "self", "blrrgl_hide", "run"), ("wait", 2000),
                 ("emote", "self", "shy"), ("wait", 2500), ("move", "self", "blrrgl", "walk")],
         complete=[("emote", "self", "cheer"), ("move", "self", "blrrgl_throw", "run"), ("wait", 3500), ("emote", "self", "attack"),
                   ("sound", "self", 1005), ("wait", 900), ("emote", "self", "attack"), ("sound", "self", 1005), ("wait", 900),
                   ("emote", "self", "throw"), ("sound", "self", "splash_big"), ("wait", 1500), ("emote", "self", "cheer"),
                   ("sound", "self", "murloc_aggro"), ("wait", 2000), ("move", "self", "blrrgl", "walk")],
         poi=["sinslayer_horn"]),

    # 2.11: wanted, one murloc (Auberdine, at night: the first town)
    dict(key="ch2_wanted", title="Wanted: One Murloc", giver="ch1:blrrgl", ender="ch1:blrrgl", level=17, xp=7, tone="funny",
         path="menace", prev="ch2_sinslayer", items=[("poster", 1)], rep=[(69, -250)],
         goal="Sneak into Auberdine, far up the coast to the north, at night, and take the WANTED poster beside the notice board "
              "by the inn. The town's Sentinels warn you off at 20 yards and strike at a few: keep your distance.",
         text="Psst. Up the shore, far far up, the dry-skins have a town. And on a board in the town... a drawing. Of a murloc. "
              "With your mark on the shoulder! You are famous! I want it, for my wall. Go at night. Go quiet.",
         progress="Famous murlocs are quiet murlocs. Shh.",
         reward="Hee! Look at it! That is you! Bigger nose... but you! On my wall it goes. Up. No, up. Hm. Up is fine.",
         details=["laugh", "point"], reward_emotes=["laugh", "cheer"], choice=["poster_pin", "board_mallet"],
         accept=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("emote", "self", "kneel"),
                 ("object", "draw_poster", "blrrgl_draw", 30), ("wait", 2000), ("emote", "self", "point"), ("wait", 1200),
                 ("face", "self", "north_way"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "laugh"),
                 ("face", "self", "player")],
         complete=[("emote", "self", "laugh"), ("move", "self", "hut_wall_front", "walk"), ("wait", 3000),
                   ("object", "hung_poster", "hut_wall", 900), ("sound", "self", 1192), ("wait", 1500),
                   ("emote", "self", "question"), ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2"),
                   ("move", "self", "blrrgl", "walk")],
         poi=["poster"]),

    # 2.12a: Gubber's tackle (Sloshy tags along to Auberdine's beach)
    dict(key="ch2_tackle", title="Gubber's Tackle", giver="ch1:sloshy", ender="ch1:sloshy", level=16, xp=7, tone="funny",
         path="hero", exclusive=1, prev="ch2_hat", event="The tackle box left in Gubber's bait basket", rep=[(47, 350)],
         goal="Dive for Gubber Blump's Tackle Box in the water off his fishing spot on Auberdine's beach, far up the coast, and "
              "leave it in his bait basket on the shore.",
         text="There is a dry-skin at the big town's water. A little one. He fishes all day and catches nothing! And his box fell "
              "in. His box of shiny hooks. He just stares at the water. Sad face. Help him? I'll come! I'll show you!",
         progress="Did he find it? Did he smile?",
         reward="He smiled! The little dry-skin smiled at the water! At us! Kind of at us!",
         details=["cheer", "point"], reward_emotes=["cheer", 94], rewards=[6529],
         accept=[("emote", "self", "cheer"), ("sound", "self", "baby_murloc"), ("face", "self", "north_way"),
                 ("emote", "self", "point"), ("wait", 1500), ("summon", "sloshy_tag", "sloshy", 900), ("wait", 300),
                 ("follow", "sloshy_tag"), ("sound", "self", "baby_murloc"), ("despawn", "self")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "baby_murloc"), ("despawn", "sloshy_tag"),
                   ("state", "self", "dance"), ("wait", 4000), ("state", "self", "none")],
         poi=["tackle_sunk", "gubber_basket"]),

    # 2.12b: Gubber's prize (for Blrrgl's wall)
    dict(key="ch2_prize", title="Gubber's Prize", giver="ch1:blrrgl", ender="ch1:blrrgl", level=16, xp=7, tone="funny",
         path="menace", exclusive=1, prev="ch2_hat", items=[("prize_fish", 1)], rep=[(47, -350)],
         goal="Take Gubber Blump's Prize Fish off its plaque by his fishing spot on Auberdine's beach, far up the coast, and "
              "bring it to Blrrgl.",
         text="The little dry-skin at the town's water has a fish. On a board. A dead fish on a board, that he looks at. It is "
              "THIS big. No. THIS big! He doesn't eat it. He doesn't need it. I need it. For my wall.",
         progress="This big. Remember. THIS big.",
         reward="Ooooh. It's bigger than me. It's bigger than YOU. On the wall, next to your face. The wall is getting good.",
         details=["cheer", "beg"], reward_emotes=["laugh", "applaud"], rewards=[6256],
         accept=[("emote", "self", "cheer"), ("wait", 1200), ("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"),
                 ("wait", 1500), ("emote", "self", "beg"), ("wait", 1200), ("face", "self", "north_way"),
                 ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player")],
         complete=[("move", "self", "hut_wall_front", "walk"), ("wait", 3000), ("object", "hung_fish", "hut_wall_b", 900),
                   ("sound", "self", 1189), ("wait", 1200), ("emote", "self", "applaud"), ("emote", "self", "laugh"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("move", "self", "blrrgl", "walk")],
         poi=["prize_mount"]),

    # 2.13: the purple robes (a slave sale, watched from the bluff)
    dict(key="ch2_robes", title="The Purple Robes", giver="ch1:blrrgl", ender="ch1:blrrgl", level=17, xp=7, tone="serious",
         prev="ch2_sinslayer", event="The slave sale seen",
         goal="Go inland to the Twilight's Hammer camp at the Master's Glaive, south-east of the cove, and watch from the bluff on "
              "its north side. Then tell Blrrgl what you saw.",
         text="I followed a long one. Inland, to the dry-skins in purple robes, by the giant sword in the ground. He had murlocs "
              "on a chain. Greymist. Come see, from the high rock on the north side. Low. Lower than that. Crawl.",
         progress="Did you see? Did you see what they paid?",
         reward="Coins. For murlocs. Not for fish, not for pearls... for us. Why do dry-skins want murlocs? What do they eat?",
         details=["wave", "point"], reward_emotes=["question", "cry"],
         accept=[("state", "self", 433), ("move", "self", "crawl_1", "walk"), ("wait", 2500), ("emote", "self", "wave"),
                 ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "wave"), ("wait", 1500),
                 ("state", "self", "none"), ("move", "self", "blrrgl", "walk")],
         complete=[("emote", "self", "question"), ("sound", "self", 120), ("wait", 1500), ("emote", "self", "no"),
                   ("wait", 1200), ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2")],
         poi=["ridge"]),

    # 2.14: break the chains
    dict(key="ch2_chains", title="Break the Chains", giver="ch0:mrrgula", ender="ch0:mrrgula", level=17, xp=7, tone="serious",
         path="hero", prev="ch2_robes", items=[("shackle", 5)], rep=[(69, 150)],
         goal="Open the shackles of 5 Chained Greymist in the Twilight's Hammer camp at the Master's Glaive.",
         text="Greymist. Mine. Sold for coins to dry-skins in purple. No. No no no. 5 of them, Blrrgl says, chained by the big "
              "sword. Open the shackles. Send them home to the sea.",
         progress="How many came home? Count them for me.",
         reward="5... 5 came home. Give me your hands. Both. There. There.",
         details=["exclamation", "point"], reward_emotes=["beg", "talk"],
         choice=["shackle_gauntlets", "freed_gloves", "kelpweave_gloves"],
         accept=[("state", "self", "none"), ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 1200),
                 ("face", "self", "camp_way"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "cry"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "hub"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "kneel"), ("wait", 1500),
                   ("emote", "self", "beg"), ("wait", 1200), ("emote", "self", "beg"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 2000), ("state", "self", "sit")],
         poi=["shackle_1", "shackle_3"]),

    # 2.15: what the cult wants (the ledger; the hydra in the smoke)
    dict(key="ch2_ledger", title="What the Cult Wants", giver="nrrglo", ender="nrrglo", level=17, xp=7, tone="serious",
         prev="ch2_robes", items=[("ledger", 1)], drops={"ledger": [(2338, 35)]},
         goal="Take the Twilight Ledger from a Twilight Disciple at the Master's Glaive and bring it to Seer Nrrglo.",
         text="The purple robes buy murlocs. Murlocs are not food for dry-skins... so what are we for? They keep marks on skins, "
              "in a book. Bring me the book. The water will read it to me, if I ask nicely.",
         progress="The book, little one. The marks.",
         reward="Mmmh. The marks are dry. Dry marks. But under the marks, something wet. Something old. Something hungry.",
         details=["talk", "point"], reward_emotes=["exclamation", "point"], rewards=["seer_charm"],
         accept=[("state", "self", "none"), ("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("face", "self", "camp_way"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "talk"),
                 ("wait", 1500), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("move", "self", "fire_side", "walk"), ("wait", 3500), ("emote", "self", "kneel"),
                   ("object", "ledger_obj", "ledger_spot", 30), ("sound", "self", 1184), ("wait", 1500), ("emote", "self", "talk"),
                   ("summon", "violet_flame", "hub", 25), ("wait", 600), ("visual", "violet_flame", 32566),
                   ("sound", "self", 4974), ("wait", 1500), ("summon", "hydra_shadow", "hydra_spot", 14), ("wait", 600),
                   ("visual", "hydra_shadow", 37816), ("sound", "self", 455), ("music", 6075),
                   ("move", "villager", "back_1", "run"), ("move", "wader", "back_2", "run"), ("emote", "mender", "cry"),
                   ("wait", 4000), ("face", "self", "pens_way"),
                   ("say", "self", "Blackfathom. The deep temple. They feed us... to something there.", "point", "murloc_fidget2"),
                   ("wait", 6000), ("move", "villager", "villager_a", "walk"), ("move", "wader", "villager_c", "walk"),
                   ("move", "self", "nrrglo", "walk"), ("wait", 3500), ("state", "self", "sit")],
         poi=["ridge", "disc_4"]),

    # 2.16: the fishing moot (a contest Mrrk always wins; a thresher eats the prize)
    dict(key="ch2_contest", title="The Fishing Moot", giver="ch0:mrrgula", ender="ch0:mrrgula", level=18, xp=8, tone="funny",
         prev="ch2_nets", time=180, kill=[("darter", 10), ("basket_eater", 1)],
         goal="Win the Greymist fishing contest: spear 10 Silverfin Shoals in the cove within 3 minutes, before Mrrk Sharpfin "
              "does. Something big may want the prize basket.",
         text="Every new moon, a moot! Every moot, a contest! Spear 10 fish before the drum stops. Mrrk wins every year. Every "
              "year. Mrrk is very... Mrrk. Beat him, and the prize basket is yours.",
         progress="Faster! Mrrk is winning! Mrrk is always winning!",
         reward="The basket... is inside a thresher. Mrrk says you lost. Mrrk says a lot of things. Here. Better than a basket.",
         details=["cheer", "point"], reward_emotes=["laugh", "talk"], choice=["moot_gaff", "moot_cord"],
         accept=[("state", "self", "none"), ("sound", "self", 11773), ("emote", "self", "cheer"),
                 ("object", "prize_basket", "contest_basket", 50), ("move", "ch0:mrrk", "best_shoal", "run"),
                 ("sound", "ch0:mrrk", "murloc_aggro"), ("emote", "villager", "cheer"), ("sound", "villager", "murloc_aggro"),
                 ("wait", 3000), ("state", "ch0:mrrk", "work"), ("emote", "self", "cheer"), ("wait", 2000),
                 ("state", "self", "sit"), ("wait", 41000), ("summon", "basket_eater", "thresher_rise", 180),
                 ("wait", 300), ("sound", "basket_eater", 1236), ("move", "basket_eater", "contest_basket", "run"),
                 ("emote", "villager", "exclamation"), ("state", "ch0:mrrk", "none"), ("move", "ch0:mrrk", "mrrk", "run")],
         complete=[("face", "villager", "mrrk"), ("emote", "villager", "point"), ("emote", "wader", "point"),
                   ("emote", "sentry_l", "point"), ("wait", 1500), ("face", "ch0:mrrk", "player"), ("emote", "ch0:mrrk", "point"),
                   ("emote", "ch0:mrrk", "laugh"), ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget")],
         poi=["best_shoal"]),

    # 2.17: Mrrk's race (he wins either way)
    dict(key="ch2_race", title="Mrrk's Race", giver="ch0:mrrk", ender="ch0:mrrk", level=18, xp=7, tone="stupid",
         prev="ch2_contest", time=120, items=[("ribbon_red", 1), ("ribbon_blue", 1), ("ribbon_green", 1)],
         goal="Race Mrrk Sharpfin: swim out to the red, blue and green buoys in the bay north-west of the cove, take a ribbon "
              "from each, and come back to him within 2 minutes.",
         text="You. New one. Everyone talks about you. Fish this, naga that. Race me. 3 buoys, out in the bay. Touch them all, "
              "come back. I'll even wait for the drum. Probably.",
         progress="Slow. So slow. Are you swimming or sinking?",
         reward="I won. Obviously. ...You were close. Closer than anyone. Don't tell anyone.",
         details=["laugh", "flex"], reward_emotes=["laugh", "flex"],
         accept=[("emote", "self", "laugh"), ("move", "self", "start_line", "walk"), ("wait", 3000), ("emote", "self", "kneel"),
                 ("object", "draw_start", "start_line", 40), ("wait", 1500), ("emote", "self", "flex"), ("wait", 800),
                 ("move", "self", "buoy_1_near", "run"), ("sound", "self", "splash"), ("wait", 1200),
                 ("sound", "ch0:mrrgula", 11773), ("wait", 8000), ("move", "self", "buoy_2_near", "run"), ("wait", 8000),
                 ("move", "self", "buoy_3_near", "run"), ("wait", 7000), ("move", "self", "victory", "run"), ("wait", 9000),
                 ("state", "self", "dance"), ("sound", "self", "murloc_aggro"), ("wait", 6000), ("state", "self", "none"),
                 ("move", "self", "mrrk", "walk")],
         complete=[("state", "self", "dance"), ("sound", "self", "murloc_aggro"), ("wait", 3000), ("state", "self", "none"),
                   ("emote", "self", "laugh"), ("emote", "self", "flex")],
         poi=["buoy_1", "buoy_2", "buoy_3"]),

    # 2.18: the very important rock (boring, until it isn't)
    dict(key="ch2_rock", title="The Very Important Rock", giver="nrrglo", ender="ch0:mrrgula", level=18, xp=7, tone="boring",
         prev=["ch2_ledger", "ch2_chains"], event="The tide watched",
         goal="Sit on Seer Nrrglo's sacred rock at the north tip of the cove and watch the tide without moving. Then tell Mother "
              "Mrrgula what you saw.",
         text="The rock. My rock. The very important rock. Every day someone sits on it and watches the tide. Today, you. Sit. "
              "Watch. Do not move, a whole minute. The tide tells the rock things, and the rock tells whoever sits on it.",
         progress="Did the tide say anything? It usually says splash.",
         reward="Boats? Long ones in the water, coming here? To my cove? To MY cove?",
         details=["point", "talk"], reward_emotes=["exclamation", "point"],
         accept=[("state", "self", "none"), ("move", "self", "rock_side", "walk"), ("wait", 5000), ("emote", "self", "point"),
                 ("state", "self", "sit"), ("wait", 3000), ("state", "self", "none"), ("emote", "self", "yes"),
                 ("move", "self", "nrrglo", "walk"), ("wait", 5000), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"),
                   ("face", "self", "horizon_1"), ("wait", 1500), ("emote", "self", "point"), ("emote", "sentry_l", "exclamation"),
                   ("emote", "villager", "cry"), ("wait", 2500), ("face", "self", "player")],
         poi=["sacred_rock"]),

    # 2.19: raid on the cove (three waves)
    dict(key="ch2_raid", title="Raid on the Cove", giver="ch0:mrrgula", ender="ch0:mrrgula", level=18, xp=8, tone="serious",
         path="hero", prev="ch2_rock", time=300, kill=[("raider", 10)],
         goal="Defend Greymist Cove: kill 10 Stormscale Raiders as they come out of the water in three waves, within 5 minutes.",
         text="They come. The Stormscale come for the runaways... for you. Not in my cove. NOT in my cove! Every spear to the "
              "water! 10 of them, little one, and the rest will remember.",
         progress="Hold the water! Hold it!",
         reward="...They're gone. They're GONE! Hear that? That is the cove. That is my whole cove, and it is still here.",
         details=["exclamation", "attack"], reward_emotes=["cheer", "talk"],
         choice=["cove_spear", "tidewall_shield", "greymist_staff"],
         accept=[("state", "self", "none"), ("move", "self", "drum_spot", "run"), ("wait", 1500), ("emote", "self", "attack"),
                 ("sound", "self", 11773), ("wait", 800), ("emote", "self", "attack"), ("sound", "self", 11773),
                 ("yell", "self", "To the water! Every spear to the water!", None, "murloc_aggro"),
                 ("move", "sentry_l", "waterline_1", "run"), ("move", "sentry_r", "waterline_2", "run"),
                 ("move", "grrlok", "waterline_3", "run"), ("move", "mender", "waterline_4", "run"),
                 ("move", "ch1:blrrgl", "pot_hide", "run"), ("wait", 2500), ("state", "ch1:blrrgl", 431),
                 ("sound", "ch1:blrrgl", "splash_small"), ("summon", "raider", "raid_1", 240), ("summon", "raider", "raid_2", 240),
                 ("summon", "raider", "raid_3", 240), ("summon", "raider", "raid_4", 240), ("sound", "self", "naga_aggro"),
                 ("wait", 20000), ("sound", "self", 11773), ("summon", "raider", "raid_1", 240), ("summon", "raider", "raid_2", 240),
                 ("summon", "raider", "raid_3", 240), ("summon", "raider", "raid_4", 240), ("wait", 20000),
                 ("yell", "self", "Again! They come again!", None, "murloc_alert"), ("summon", "raider", "raid_1", 240),
                 ("summon", "raider", "raid_2", 240), ("summon", "raider", "raid_3", 240), ("summon", "raider", "raid_4", 240),
                 ("wait", 8000), ("state", "ch1:blrrgl", "none"), ("move", "ch1:blrrgl", "blrrgl", "walk"),
                 ("move", "sentry_l", "sentry_a", "walk"), ("move", "sentry_r", "sentry_b", "walk"),
                 ("move", "grrlok", "t_warrior", "walk"), ("move", "mender", "villager_d", "walk")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"), ("emote", "sentry_l", "cheer"),
                   ("emote", "sentry_r", "cheer"), ("emote", "grrlok", "cheer"), ("emote", "villager", "cheer"),
                   ("sound", "sentry_l", 11802), ("sound", "villager", "murloc_aggro"), ("music", 8455), ("wait", 2500),
                   ("emote", "self", "cheer"), ("sound", "self", 11802)],
         poi=["raid_1"]),

    # 2.20a: Murkdeep's honor (beat him at his challenge fire, then give him back his club)
    dict(key="ch2_honor", title="Murkdeep's Honor", giver="ch0:mrrgula", ender="ch0:mrrgula", level=19, xp=8, tone="serious",
         path="hero", exclusive=2, prev="ch2_raid", source="offering_fish", kill=[("hardliner", 6)],
         interact=[("murkdeep_yield", "Take his club... and hand it back.")], interact_goal="Murkdeep's club handed back",
         interact_beats=[("state", "self", "none"), ("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"),
                         ("wait", 2000), ("emote", "self", "flex"), ("wait", 1200), ("emote", "self", "salute"),
                         ("sound", "self", "murloc_aggro"), ("wait", 2000), ("emote", "self", "cheer")],
         goal="Lay 3 Offering Fish on Murkdeep's Challenge Fire, on the beach below his camp up the shore, to call him out. "
              "Beat 6 of his hardliners and fight Murkdeep until he yields, then take the club he offers and hand it back.",
         text="Murkdeep. Big. Proud. Stupid... like every chief. He will not listen to me. He will listen to a fight. Lay 3 fish "
              "on his challenge fire and he must come out. Beat him. Don't kill him. Then give him back his pride.",
         progress="Is he kneeling? Murkdeep doesn't kneel. Make him kneel.",
         reward="He knelt, and you gave it back? Hah! Now he will follow you anywhere. Grumbling. All the way south.",
         details=["kneel", "point"], reward_emotes=["laugh", "cheer"],
         choice=["hard_pauldrons", "hard_spaulders", "hard_mantle"],
         accept=[("state", "self", "none"), ("move", "self", "mrrgula_draw", "walk"), ("wait", 2500), ("emote", "self", "kneel"),
                 ("object", "draw_club", "mrrgula_draw_a", 30), ("sound", "self", 1194), ("wait", 1500),
                 ("object", "draw_little", "mrrgula_draw_b", 30), ("object", "draw_little", "mrrgula_draw_c", 30),
                 ("wait", 1500), ("emote", "self", "kneel"), ("object", "draw_kneel", "mrrgula_draw_d", 30), ("wait", 1500),
                 ("give", "offering_fish", 2), ("emote", "self", "point"), ("wait", 1500), ("move", "self", "mrrgula", "walk"),
                 ("wait", 2500), ("face", "self", "hub"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                   ("emote", "self", "cheer"), ("emote", "murkdeep", "flex"), ("sound", "murkdeep", "murloc_aggro"),
                   ("emote", "hardliner_ally", "cheer")],
         poi=["challenge_fire"]),

    # 2.20b: Murkdeep's totem (stolen while he sleeps: his warriors follow whoever holds it)
    dict(key="ch2_totem", title="Murkdeep's Totem", giver="ch1:blrrgl", ender="ch0:mrrgula", level=19, xp=8, tone="funny",
         path="menace", exclusive=2, prev="ch2_raid", items=[("totem", 1)],
         goal="Sneak into Murkdeep's camp up the shore while he sleeps by his bonfire and lift the War-Totem beside him. Bring "
              "it to Mother Mrrgula.",
         text="Fight Murkdeep? Hah. No. Murkdeep sleeps. Snore, snore, big belly up. His totem stands right by his head, and his "
              "warriors follow the totem, not him. Whoever holds it... has warriors. Tiptoe. I'll hum.",
         progress="What is that? Where did you... oh. Oh, Blrrgl.",
         reward="His totem. Well. His warriors are mine now, I suppose... and they are not happy about it. Put it there. "
                "No, there. Where they can see it.",
         details=["laugh", "point"], reward_emotes=["no", "laugh"],
         choice=["hard_pauldrons", "hard_spaulders", "hard_mantle"],
         accept=[("summon", "murkdeep_sleep", "den", 600), ("state", "self", "sleep"), ("sound", "self", 7940), ("wait", 2500),
                 ("state", "self", "none"), ("emote", "self", "laugh"), ("wait", 1000), ("state", "self", 433),
                 ("move", "self", "tiptoe", "walk"), ("wait", 3500), ("state", "self", "none"), ("face", "self", "north_way"),
                 ("emote", "self", "point"), ("wait", 1500), ("move", "self", "blrrgl", "walk")],
         complete=[("state", "self", "none"), ("object", "totem_set", "totem_spot", 600), ("emote", "self", "point"),
                   ("sound", "self", 1194), ("wait", 1500), ("emote", "hardliner_sullen", "no"),
                   ("sound", "hardliner_sullen", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "laugh"),
                   ("state", "self", "sit")],
         poi=["totem"]),

    # 2.21: Nerelith's map (she draws the Zoram Strand in the sand)
    dict(key="ch2_map", title="Nerelith's Map", giver="ch0:nerelith", ender="ch0:nerelith", level=18, xp=7, tone="serious",
         path="hero", prev=["ch2_moonstone", "ch2_raid"], rep=[(69, 250)],
         interact=[("ch0:nerelith", "Watch her draw.")], interact_goal="Nerelith's map watched",
         interact_beats=[("state", "self", "kneel"), ("object", "map_coast", "draw_a", 40), ("sound", "self", 1194),
                         ("wait", 1500), ("object", "map_temple", "draw_b", 40), ("wait", 1500),
                         ("object", "map_tree", "draw_c", 40), ("wait", 1500), ("object", "map_banner", "draw_d", 40),
                         ("wait", 1500), ("face", "self", "draw_c"), ("emote", "self", "point"), ("wait", 1000),
                         ("emote", "self", "yes"), ("wait", 2000), ("face", "self", "draw_d"), ("emote", "self", "point"),
                         ("wait", 1000), ("emote", "self", "question"), ("wait", 2000), ("state", "self", "none"),
                         ("face", "self", "player")],
         goal="Watch Nerelith draw the Zoram Strand in the sand by her rock on the north beach.",
         text="You will go south. I see it in your people: spears, nets, and that one who never stops singing. South is the "
              "Zoram Strand. Let me show you what waits there... and who might help you.",
         progress="Look closely. Remember it.",
         reward="Take these. A Sentinel's cloak... I won't need it again. And the map. Sand doesn't keep, but you will.",
         details=["talk", "kneel"], reward_emotes=["bow", "salute"], rewards=["sentinel_cloak", "sand_map"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "draw_b"),
                 ("emote", "self", "point")],
         complete=[("emote", "self", "bow"), ("wait", 1500), ("emote", "self", "salute"), ("sound", "self", 2761)],
         poi=["nerelith"]),

    # 2.22a: pearls for grain (Blrrgl's log gives up its pearls)
    dict(key="ch2_pearls", title="Pearls for Grain", giver="ch0:mrrgula", ender="ch0:mrrgula", level=19, xp=7, tone="serious",
         path="hero", exclusive=3, prev="ch2_map", items=[("grain", 6)], rep=[(69, 150)],
         goal="Sneak into Auberdine's beach at night and take the 6 Sacks of Grain by its two wagons, leaving one of Blrrgl's "
              "Pearls in each one's place.",
         text="The war band needs food for the march south. The dry-skins of the town have grain on their wagons. Grain we cannot "
              "buy... but we can pay. Blrrgl has pearls. Blrrgl has always had pearls. 6 sacks. A pearl for each.",
         progress="A pearl for each, little one. We are not long ones.",
         reward="Grain! And the dry-skins have pearls. Fair. Fair is how free murlocs do things.",
         details=["point", "talk"], reward_emotes=["yes", "talk"], choice=["grain_cord", "grain_belt", "grain_girdle"],
         accept=[("state", "self", "none"), ("face", "self", "blrrgl"), ("emote", "self", "point"), ("wait", 1200),
                 ("move", "ch1:blrrgl", "blrrgl_log", "walk"), ("wait", 2500), ("emote", "ch1:blrrgl", "kneel"),
                 ("sound", "ch1:blrrgl", 1221), ("wait", 1500), ("emote", "ch1:blrrgl", "cry"),
                 ("sound", "ch1:blrrgl", "murloc_fidget2"), ("wait", 1500), ("move", "ch1:blrrgl", "greet", "walk"),
                 ("wait", 4000), ("emote", "ch1:blrrgl", "beg"), ("give", "pearls", 6), ("wait", 2000),
                 ("move", "ch1:blrrgl", "blrrgl", "walk"), ("face", "self", "hub"), ("state", "self", "sit")],
         complete=[("emote", "self", "yes"), ("sound", "self", "murloc_fidget2"), ("emote", "bubbmrl", "cheer"),
                   ("sound", "bubbmrl", 973)],
         poi=["wagon_a", "wagon_b"]),

    # 2.22b: grain for the war (and Auberdine remembers)
    dict(key="ch2_grain", title="Grain for the War", giver="ch1:blrrgl", ender="ch0:mrrgula", level=19, xp=7, tone="serious",
         path="menace", exclusive=3, prev="ch2_map", items=[("grain", 6)], rep=[(69, -350)],
         goal="Sneak into Auberdine's beach at night and take the 6 Sacks of Grain by its two wagons. Leave nothing. Bring them "
              "to Mother Mrrgula.",
         text="Pearls? For grain? Mrrgula is soft. Soft soft soft. The dry-skins have more grain than the sea has fish. They "
              "won't miss 6 sacks. Come, I know the way. Quiet feet. Grabby hands.",
         progress="Where did this grain come from? ...No. Don't tell me.",
         reward="Grain is grain, and the war band must eat. But the dry-skins will remember, little one. Dry-skins always remember.",
         details=["beg", "point"], reward_emotes=["no", "yes"], choice=["grain_cord", "grain_belt", "grain_girdle"],
         accept=[("emote", "self", "beg"), ("sound", "self", "murloc_fidget"), ("emote", "self", "laugh"), ("wait", 1200),
                 ("face", "self", "north_way"), ("emote", "self", "point"), ("state", "self", 433),
                 ("move", "self", "tiptoe", "walk"), ("wait", 3500), ("state", "self", "none"), ("move", "self", "blrrgl", "walk")],
         complete=[("state", "self", "none"), ("emote", "self", "no"), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                   ("emote", "self", "yes"), ("face", "self", "hub"), ("state", "self", "sit")],
         poi=["wagon_a", "wagon_b"]),

    # 2.23: war paint
    dict(key="ch2_paint", title="War Paint", giver="nrrglo", ender="nrrglo", level=19, xp=7, tone="funny", prev="ch2_raid",
         items=[("fin", 6)], drops={"fin": [(2187, 60), (2185, 45)]},
         goal="Bring Seer Nrrglo 6 Thresher Fins from the Elder Darkshore Threshers in the bay west of the cove.",
         text="A war band needs war paint. Red. Very red. Thresher red! The big threshers in the bay have fins full of it. "
              "6 fins. I grind, I mix, I paint. Everyone looks fierce. Even Blrrgl. Probably.",
         progress="Red needs fins. Fins need threshers. Threshers need to be... less alive.",
         reward="Hold still. Hold STILL. There! Fierce! Blrrgl, come here, your turn... hold still...",
         details=["point", "flex"], reward_emotes=["laugh", "flex"],
         accept=[("state", "self", "none"), ("face", "self", "pens_way"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "work"), ("wait", 1500), ("emote", "self", "flex"),
                 ("sound", "self", "murloc_fidget"), ("wait", 1500), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "work"), ("sound", "self", 1194), ("wait", 1500),
                   ("emote", "self", "kneel"), ("visual", "self", 36005), ("wait", 1500), ("emote", "self", "flex"),
                   ("aura", "player", "war_paint"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                   ("emote", "ch1:blrrgl", "question"), ("wait", 1000), ("sound", "ch1:blrrgl", "murloc_wound"),
                   ("emote", "ch1:blrrgl", "cry"), ("wait", 1000), ("emote", "self", "laugh"), ("state", "self", "sit")],
         poi=["raid_edge"]),

    # 2.24: the moot (the Greymist vote to march south)
    dict(key="ch2_moot", title="The Moot", giver="ch0:mrrgula", ender="ch0:mrrgula", level=19, xp=8, tone="serious",
         prev=["ch2_paint", "ch2_chains", "ch2_map"], source="moot_fish", event="Your fish in the go basket",
         emotes=[("ch0:mrrgula", "roar", 1, [("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", 11802),
                                             ("emote", "villager", "cheer"), ("emote", "sentry_l", "cheer"),
                                             ("emote", "sentry_r", "cheer"), ("emote", "grrlok", "cheer"),
                                             ("sound", "villager", "murloc_aggro"), ("sound", "sentry_l", "murloc_aggro"),
                                             ("emote", "ch0:mrrk", "cheer"), ("sound", "ch0:mrrk", 11802), ("music", 8455)])],
         goal="Drop your Moot Fish in the go basket by the cove's fire, then answer Mother Mrrgula's war-cry (/roar at her).",
         text="Tonight the cove decides. Stay, and fish, and hide from the long ones forever... or go south, and break the pens. "
              "Every Greymist has one fish and two baskets. You have one fish too. You are Greymist now.",
         progress="Your fish, little one. Which basket?",
         reward="The go basket. Every fish in the go basket! Then we go. South. To the pens. To bring them home.",
         details=["point", "talk"], reward_emotes=["cheer", "talk"],
         accept=[("state", "self", "none"), ("move", "self", "moot_spot", "walk"), ("wait", 2500), ("face", "self", "stay_basket"),
                 ("emote", "self", "point"), ("wait", 1200), ("face", "self", "go_basket"), ("emote", "self", "point"),
                 ("wait", 1200), ("move", "villager", "go_basket_front", "walk"), ("move", "wader", "go_basket_front", "walk"),
                 ("move", "mender", "stay_front", "walk"), ("wait", 4500), ("emote", "villager", "kneel"),
                 ("emote", "wader", "kneel"), ("emote", "mender", "kneel"), ("sound", "villager", 1189), ("wait", 2500),
                 ("move", "villager", "villager_a", "walk"), ("move", "wader", "villager_c", "walk"),
                 ("move", "mender", "villager_d", "walk"), ("face", "self", "player")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"), ("wait", 1500),
                   ("move", "self", "mrrgula", "walk"), ("wait", 3500), ("face", "self", "hub"), ("state", "self", "sit")],
         poi=["go_basket"]),

    # 2.25: south along the shore (the war band follows you to the old elven pier)
    dict(key="ch2_end", title="South Along the Shore", giver="ch0:mrrgula", ender="blrrgl_pier", level=19, xp=8,
         tone="serious", path="hero", prev="ch2_moot", explore="drowned_pier", radius=15,
         goal="Lead the Greymist war band south-west along the shore, past a Stormscale ambush and the Twilight's Hammer's "
              "thugs, to the old elven pier at the north end of the Zoram Strand, where Blrrgl waits.",
         text="The war band is ready. Spears, nets, war paint... and you at the front. You! The runaway who came for a fish and "
              "stayed for a fight. South along the shore, to the old elf pier by the Strand. Blrrgl went ahead. Blrrgl always "
              "goes ahead when there is no fighting yet.",
         progress="Here! Here! Over here!",
         reward="You came! With everyone! The pens are just there, past the rocks. Listen. I can hear the gong... I can hear "
                "the gong.",
         details=["point", "cheer"], reward_emotes=["cheer", "point"], choice=["warspear", "shore_dirk", "seer_rod"],
         accept=[("state", "self", "none"), ("summon", "warband_a", "warband_1", 900), ("summon", "warband_b", "warband_2", 900),
                 ("summon", "warband_c", "warband_3", 900), ("wait", 600), ("follow", "warband_a"), ("follow", "warband_b"),
                 ("follow", "warband_c"), ("emote", "self", "cheer"), ("sound", "self", 11802), ("emote", "villager", "cheer"),
                 ("sound", "villager", "murloc_aggro"), ("emote", "sentry_l", "salute"), ("emote", "sentry_r", "salute"),
                 ("wait", 2000), ("face", "self", "pens_way"), ("emote", "self", "point"), ("wait", 2000),
                 ("face", "self", "hub"), ("state", "self", "sit")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("emote", "warband_a", "cheer"),
                   ("sound", "warband_a", "murloc_aggro"), ("emote", "warband_b", "cheer"), ("emote", "warband_c", "cheer"),
                   ("move", "warband_a", "camp_1", "walk"), ("move", "warband_b", "camp_2", "walk"),
                   ("move", "warband_c", "camp_3", "walk"), ("wait", 3000), ("face", "self", "pens_dir"),
                   ("emote", "self", "point"), ("sound", "self", 12827), ("wait", 2500), ("sound", "self", 12827),
                   ("emote", "self", "cry")],
         poi=["drowned_pier", "amb_n2"]),
]
