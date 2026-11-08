# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 5 of the murlocs' story: Torn Fins (levels 29 to 33), the bible's section 11.

Hillsbrad's coast (map 0). Torn Fin Cove, the tribe's hub, is the one stretch of the Western Strand's
beach (around (-1066, -177)) that the game's Torn Fin raiders leave alone: 35 to 50 yards from their
nearest spawns, the sea to the south, a dune and the cliffs to the north. Hrrlga Half-Fin's friendly
Torn Fin live at its waterline; Grandmother Shellback rests in the shallows; a dead fisherman, Corwin
Slate, walks the sea floor 140 yards out. Hester Gale's cottage stands on the beach just south of
Southshore's docks, outside its guards' reach; the Daggerspine hold the Eastern Strand beyond it, their
pens and shrine at (-1320, -1035); the Mudsnout gnolls camp at Nethander Stead above them; Tarren Mill
is up the hill. The Oracle's vision (5.11) is staged on the islet west of the cove and the sea beside
it. The chapter ends on Grandmother Shellback's ride south to Westfall (chapter 6's hub).

Phases (zone 267 has 16 story bits; this chapter uses 15 rules, listed below). Plain data:
tools/murloc/SCHEMA.md."""

ARRIVED = ("from", "ch5_arrival")                          # the hub kit, the camp
TRIBE_HERE = ("between", "ch4:ch4_end", "ch9:ch9_elder")    # the Elder and the turtle, from the landing
WARM = ("until", "ch5_fins")                               # Hrrlga, before the fins
COLD = ("from", "ch5_fins")                                # Hrrlga and Murlorga, their backs turned
MURLORGA_WARM = ("between", "ch5_arrival", "ch5_fins")
NED_LOST = ("during", "ch5_ned")
NED_HOME = ("from", "ch5_ned")
GUARD_SHOUTS = ("until", "ch5_guard")
GUARD_WAVES = ("from", "ch5_guard")
FLAGS_UP = ("from", "ch5_flags")
NETTED = ("during", "ch5_netted")
NETS_CUT = ("from", "ch5_cut")
VISION = ("during", "ch5_shell")
CAGED = ("until", "ch5_cages")
FREED = ("from", "ch5_cages")

CHAPTER = dict(key="ch5", title="Torn Fins", levels=(29, 33), map=0, zones=[267], hub="hub")

TOWNS = ["Southshore", "Tarren Mill"]

PLACES = {
    # -- Torn Fin Cove: the Saltscar's camp, a ring around the fire (inner: the cast; outer: the trades)
    "hub": (-1069.5, -177.0), "fire": (-1066.0, -177.0), "camp_mid": (-1066.0, -177.0),
    "elder": (-1059.5, -177.0), "grrmlgrrl": (-1061.4, -172.4), "grrm_line": (-1062.6, -174.0),
    "murlorga": (-1067.1, -170.6), "pot": (-1066.6, -173.2), "bundle": (-1068.6, -172.0),
    "caller": (-1071.5, -173.6), "glubbub": (-1071.5, -180.4), "glubbub_side": (-1073.5, -182.0),
    "blrrgl": (-1066.9, -183.4), "log": (-1066.0, -186.4), "blrrgl_peek": (-1066.3, -185.0),
    "mrrlglr": (-1061.7, -181.8),
    "t_pearlmrgl": (-1054.2, -174.9), "t_sprokgl": (-1055.5, -171.2), "t_mrrsk": (-1058.0, -168.1),
    "t_brewglub": (-1061.3, -166.0), "t_mrsha": (-1065.2, -165.0), "t_mailbox": (-1069.1, -165.4),
    "t_fizzmrgl": (-1072.7, -167.1), "t_glubba": (-1075.6, -169.8), "t_slubb": (-1077.4, -173.3),
    "t_gurgle": (-1078.0, -177.2), "t_mrrgasha": (-1077.3, -181.1), "t_brrgmrk": (-1075.3, -184.6),
    "t_fnrrgl": (-1072.4, -187.2), "t_krrgl": (-1068.7, -188.7), "t_brrkl": (-1064.7, -188.9),
    "t_grrsh": (-1060.9, -187.9), "t_mmrglla": (-1057.7, -185.6), "t_shimmrl": (-1055.3, -182.4),
    "t_scrawlgl": (-1054.1, -178.7), "krrgl_crate": (-1069.8, -190.6),
    "hut_1": (-1061.6, -160.6), "hut_2": (-1061.6, -193.4), "hut_3": (-1049.5, -177.0),
    "lantern_1": (-1076.3, -164.7), "lantern_2": (-1076.3, -189.3), "rack": (-1068.9, -160.8),
    "driftwood": (-1050.0, -182.8), "graveyard": (-1049.0, -191.0),
    "flag_a": (-1064.6, -186.8), "flag_b": (-1067.6, -187.6), "tf_salute": (-1063.0, -191.5),
    # -- Hrrlga's Torn Fin, at the waterline
    "hrrlga": (-1084.0, -183.0), "behind_hrrlga": (-1086.8, -183.8), "elder_meet": (-1062.0, -178.2),
    "basket_hrrlga": (-1082.6, -181.0), "moot_fire": (-1081.5, -186.5), "moot_spot": (-1083.2, -184.4),
    "pile_1": (-1082.4, -185.4), "pile_2": (-1080.8, -185.4), "pile_3": (-1080.3, -186.8),
    "pile_4": (-1080.9, -188.0), "pile_5": (-1082.5, -188.2), "pile_6": (-1083.0, -186.9),
    "moot_1": (-1079.4, -184.4), "moot_2": (-1078.9, -186.6), "moot_3": (-1079.6, -189.2),
    "moot_4": (-1082.6, -190.0), "moot_5": (-1084.4, -188.6),
    "fry_row": (-1086.5, -175.0), "fry_a": (-1086.5, -172.5), "fry_b": (-1086.5, -175.0),
    "fry_c": (-1086.5, -177.5), "fry_fish": (-1084.8, -175.0),
    "tf_warrior": (-1082.5, -193.0), "tf_a": (-1083.5, -168.5), "tf_b": (-1087.5, -190.5),
    "tf_c": (-1081.0, -197.0), "tf_sick": (-1080.5, -164.5), "tf_hut": (-1080.0, -201.5),
    "tf_rack": (-1085.5, -196.5), "limp_from": (-1078.0, -212.0), "limp_to": (-1082.0, -185.2),
    "limp_trap": (-1081.4, -186.0),
    "freed_1": (-1088.5, -195.5), "freed_2": (-1086.0, -199.5), "freed_3": (-1090.5, -199.0),
    "freed_walk": (-1095.0, -204.0), "glubbub_hold": (-1093.6, -202.2),
    "hrrlga_draw_1": (-1081.4, -180.4), "hrrlga_draw_2": (-1081.0, -179.6), "hrrlga_draw_3": (-1079.6, -181.6),
    "hrrlga_draw_4": (-1079.0, -180.6), "hrrlga_draw_5": (-1078.4, -179.6), "south_hub": (-1250.0, -190.0),
    # -- the shallows: Southshore's fisherman and nets, the fish, Grandmother Shellback
    "fisherman": (-1086.5, -156.0), "fisher_net": (-1091.0, -155.5), "fish_found": (-1088.0, -157.4),
    "angry_1": (-1085.0, -151.0), "angry_2": (-1083.5, -147.5), "nets_poi": (-1097.0, -178.0),
    "net_s1": (-1095.0, -161.0), "net_s2": (-1099.0, -188.0), "net_t1": (-1097.0, -170.0),
    "net_t2": (-1095.0, -205.0), "net_g1": (-1093.0, -196.0), "net_g2": (-1101.0, -150.0),
    "sea_away": (-1135.0, -182.0),
    "cut_1": (-1104.0, -166.0), "cut_2": (-1092.5, -181.0), "cut_3": (-1103.0, -180.0), "cut_4": (-1100.0, -198.0),
    "cut_5": (-1106.0, -210.0), "cut_6": (-1093.0, -150.0), "cut_7": (-1108.0, -193.0), "cut_8": (-1097.5, -213.0),
    "shoal_1": (-1094.0, -176.0), "shoal_2": (-1097.0, -184.0), "shoal_3": (-1093.0, -166.0),
    "shoal_4": (-1099.0, -192.0), "shoal_5": (-1096.0, -158.0), "shoal_6": (-1101.0, -172.0),
    "shoals": (-1096.0, -178.0),
    "shellback": (-1108.0, -204.0), "turtle_scratch": (-1104.5, -199.5), "blrrgl_crush": (-1100.0, -197.0),
    "barn_1": (-1104.5, -201.5, 0.2), "barn_2": (-1105.0, -206.5, 0.2), "barn_3": (-1111.0, -201.0, 0.2),
    "barn_4": (-1111.5, -207.0, 0.2), "barn_5": (-1108.0, -199.5, 0.6), "barn_6": (-1108.0, -209.0, 0.6),
    "barn_7": (-1103.5, -204.0, 0.0), "barn_8": (-1112.5, -204.0, 0.0),
    # -- the beach around the cove: traps, the raiders, the lessons
    "trap_1": (-1080.0, -140.0), "trap_2": (-1076.0, -215.0), "trap_3": (-1068.0, -230.0),
    "trap_4": (-1062.0, -146.0), "trap_5": (-1084.0, -222.0), "traps_poi": (-1074.0, -180.0),
    "strand_poi": (-1100.0, -110.0), "strand_south": (-1085.0, -240.0),
    "gnashjaw": (-1096.0, -106.0),
    "beacon": (-1052.5, -170.0), "fizz_dunk": (-1090.0, -171.0),
    "air_stone": (-1024.0, -212.0),
    "track_1": (-1074.0, -204.0), "track_2": (-1060.0, -214.0), "track_3": (-1046.0, -222.0),
    "track_4": (-1034.0, -230.0), "scout": (-1024.0, -238.0),
    # -- the sea floor west of the cove: Corwin Slate and the crabs
    "corwin": (-1205.0, -200.0), "corwin_b": (-1214.0, -214.0), "corwin_far": (-1240.0, -240.0),
    "corwin_feet": (-1203.6, -198.6), "corwin_away": (-1230.0, -190.0),
    "crab_1": (-1196.0, -188.0), "crab_2": (-1210.0, -186.0), "crab_3": (-1222.0, -196.0), "crab_4": (-1220.0, -222.0),
    "crab_5": (-1202.0, -226.0), "crab_6": (-1230.0, -210.0), "crab_7": (-1190.0, -205.0),
    # -- the Oracle's vision: the islet west of the cove (a white city's corner), and the sea beside it
    "vision_city": (-1225.0, -110.5), "vision_tank": (-1227.5, -114.0), "vision_lamp": (-1222.5, -115.5),
    "vision_banner": (-1229.5, -108.0), "vision_sign": (-1229.0, -116.5), "vision_bench": (-1223.5, -107.5),
    "vision_sea": (-1258.0, -126.0, 0.3), "vision_ship": (-1280.0, -142.0, 0.0), "vision_ilyssa": (-1268.0, -133.0, 0.0),
    "vision_crate_1": (-1266.0, -137.0, 0.2), "vision_crate_2": (-1271.0, -129.0, 0.2), "vision_crate_3": (-1263.0, -142.0, 0.2),
    # -- the Daggerspine camp on the Eastern Strand, and the dune above it
    "dune": (-1218.0, -1022.0), "dune_look": (-1222.0, -1019.0),
    "dune_draw_1": (-1216.4, -1019.6), "dune_draw_2": (-1215.6, -1021.2), "dune_draw_3": (-1216.0, -1023.2),
    "dune_draw_4": (-1217.0, -1024.6), "grrm_stick": (-1219.2, -1021.0),
    "dag_camp": (-1320.0, -1035.0), "egg_net": (-1316.0, -1024.0, 6.5), "egg_post": (-1316.0, -1024.0),
    "cage_1": (-1328.0, -1032.0), "cage_2": (-1334.0, -1029.0), "cage_3": (-1340.0, -1033.0),
    "cage_4": (-1330.0, -1039.0), "cage_5": (-1337.0, -1041.0), "cage_6": (-1344.0, -1038.0),
    "cages_poi": (-1336.0, -1035.0), "cage_run": (-1262.0, -985.0),
    "shrine": (-1306.0, -1040.0), "shrine_fire": (-1304.5, -1038.0), "zephris_rise": (-1300.0, -1006.0),
    "pagoda_1": (-1352.0, -1054.0), "pagoda_2": (-1290.0, -1056.0), "weapons": (-1346.0, -1046.0),
    "torch_1": (-1320.0, -1044.0), "torch_2": (-1336.0, -1022.0), "torch_3": (-1310.0, -1030.0),
    "naga_flag_1": (-1300.0, -1032.0), "naga_flag_2": (-1358.0, -1036.0),
    "crate_1": (-1296.0, -1022.0), "crate_2": (-1312.0, -1050.0), "crate_3": (-1350.0, -1046.0),
    "crate_4": (-1362.0, -1028.0), "crate_5": (-1282.0, -1040.0), "crate_6": (-1324.0, -1058.0),
    "courier": (-1284.0, -1064.0), "sirens_poi": (-1080.0, -760.0), "screamers": (-1340.0, -1000.0),
    "nethander": (-934.0, -965.0),
    # -- Southshore: Hester's cottage on the beach south of the docks, the beach guard, the dock, the inn
    "cottage": (-932.0, -604.0), "fence_1": (-937.5, -609.5), "fence_2": (-927.5, -610.5),
    "hester": (-938.5, -597.0), "hester_run": (-944.0, -604.0), "basket_spot": (-939.6, -598.8),
    "bread_rock": (-946.0, -589.0), "bread_loaf": (-946.0, -589.0, 1.6), "south_sea": (-1060.0, -660.0),
    "ned_rock": (-978.0, -645.0), "ned": (-976.6, -643.4), "ned_home": (-935.5, -596.0),
    "naga_1": (-972.0, -651.0), "naga_2": (-985.0, -640.0), "naga_3": (-984.0, -653.0),
    "beach_guard": (-922.0, -573.0),
    "gift_fish": (-923.6, -574.4), "gift_shell": (-922.0, -575.2), "gift_flower": (-920.4, -574.4),
    "ss_banner": (-916.0, -543.0, 7.0),
    "inn": (-857.0, -573.0), "inn_mug": (-853.8, -573.4, 12.42), "barmaid": (-855.5, -576.2, 11.3),
    # -- Tarren Mill's west fence; the orchard at Hillsbrad Fields
    "tm_banner": (-104.0, -886.0),
    "orchard": (-612.0, -48.0), "apple_1": (-606.0, -40.0), "apple_2": (-614.0, -46.0), "apple_3": (-620.0, -38.0),
    "apple_4": (-608.0, -56.0), "apple_5": (-618.0, -60.0), "apple_6": (-626.0, -50.0), "apple_7": (-602.0, -50.0),
    "bucket_1": (-610.0, -35.0), "bucket_2": (-623.0, -44.0),
    "farmer": (-604.0, -44.0), "farmer_flee": (-590.0, -28.0), "child": (-616.0, -31.0),
}

# -- the people ----------------------------------------------------------------------------------------

NPCS = [
    # Hrrlga's Torn Fin, the cove's own people
    dict(key="hrrlga", name="Hrrlga Half-Fin", subname="Elder of the Torn Fin", look="murloc_pale", level=31, role="quest",
         at="hrrlga", facing=0.32, phase=WARM,
         greeting="The sea was full once. Full! Now there are nets, and long ones, and little ones with ribs. Sit. There is not much. Sit anyway.",
         idle=[("every", 37000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget2")]),
               ("every", 61000, [("emote", "self", "cry")])]),
    dict(key="fry_a", name="Torn Fin Fry", plural="Torn Fin fry", look="murloc_abyssal", scale=0.5, level=5, role="ambient",
         at="fry_a", facing=0.3, greeting="Mrgl...? Fish?",
         idle=[("state", "self", "sit"), ("every", 23000, [("sound", "self", "baby_murloc")])]),
    dict(key="fry_b", name="Torn Fin Fry", plural="Torn Fin fry", look="murloc_bronze", scale=0.5, level=5, role="ambient",
         at="fry_b", facing=0.3, greeting="...hungry.",
         idle=[("state", "self", "sit"), ("every", 29000, [("emote", "self", "cry")])]),
    dict(key="fry_c", name="Torn Fin Fry", plural="Torn Fin fry", look="murloc_grey", scale=0.45, level=4, role="ambient",
         at="fry_c", facing=0.3, greeting="Mrgl. Mrgl mrgl.",
         idle=[("state", "self", "sit"), ("every", 31000, [("sound", "self", "baby_murloc")])]),
    dict(key="tf_warrior", name="Gurrk Shellknife", subname="Torn Fin Warrior", look="murloc_slate", level=31, role="quest",
         at="tf_warrior", facing=0.6, greeting="Patient, Hrrlga says. Patient! I am patient with a knife in my hand.",
         idle=[("every", 29000, [("emote", "self", "attack"), ("sound", "self", "murloc_attack")])]),
    dict(key="tf_a", name="Blurgle", subname="Torn Fin", look="murloc_bronze", level=29, role="ambient", at="tf_a",
         facing=0.2, greeting="Mending. Always mending. The nets of the dry-skins never break. Ours always do.",
         idle=[("state", "self", "work"), ("every", 41000, [("sound", "self", "murloc_fidget")])]),
    dict(key="tf_b", name="Mmrgal", subname="Torn Fin", look="murloc_abyssal", level=29, role="ambient", at="tf_b",
         facing=0.7, greeting="You came on a turtle. On a TURTLE. Nobody believes me.",
         idle=[("every", 43000, [("emote", "self", "laugh")])]),
    dict(key="tf_c", name="Shrrk", subname="Torn Fin", look="murloc_grey", level=30, role="ambient", at="tf_c",
         facing=0.9, greeting="This is our beach. Ours. My mother's, her mother's. Ours.",
         idle=[("state", "self", "sit"), ("every", 47000, [("emote", "self", "no")])]),
    dict(key="tf_sick", name="Old Blubb", subname="Torn Fin", look="murloc_pale", scale=0.9, level=28, role="ambient",
         at="tf_sick", facing=0.1, greeting="Mmh... cold... the water is so cold this year...",
         idle=[("state", "self", "sleep"), ("every", 21000, [("sound", "self", "murloc_wound")])]),
    dict(key="tf_limper", name="Mrrgl Limpfoot", subname="Torn Fin", look="murloc_bronze", level=29, role="ambient",
         summoned=True),
    dict(key="tf_dazed", name="Ploonk", subname="Freed Torn Fin", look="murloc_slate", level=28, role="ambient",
         summoned=True),
    dict(key="tf_freed", name="Freed Torn Fin", plural="freed Torn Fin", look="murloc_abyssal", looks=["murloc_bronze", "murloc_slate"],
         level=28, role="ambient", at=["freed_1", "freed_2", "freed_3"], facing=0.6, phase=FREED,
         greeting="I was in a box. Now I am on a beach. The beach is better.",
         idle=[("every", 33000, [("emote", "self", "cheer"), ("sound", "self", "murloc_fidget")])]),
    dict(key="tf_salute", name="Brrgle", subname="Torn Fin", look="murloc_slate", level=29, role="ambient", at="tf_salute",
         facing=1.55, phase=FLAGS_UP, greeting="The flags! Blrrgl's flags! Every morning, we salute. Why? Nobody knows. We salute.",
         idle=[("every", 45000, [("face", "self", "flag_a"), ("emote", "self", "salute")])]),

    # Southshore's people, on the Torn Fin's beach and in their water
    dict(key="fisherman", name="Southshore Fisherman", look=3272, level=28, side="neutral", role="ambient",
         language="common", at="fisherman", facing=3.03,
         idle=[("state", "self", "fish"), ("every", 40000, [("sound", "self", "splash_small")])]),
    dict(key="angry_fisher", name="Southshore Fisherman", plural="fishermen", look=3272, looks=[4417], level=28,
         side="neutral", role="ambient", language="common", at=["angry_1", "angry_2"], facing=3.1, phase=NETS_CUT,
         idle=[("every", 26000, [("yell", "self", "My nets! Who cut my nets? WHO CUT THEM?", "shout", 5976)]),
               ("every", 17000, [("emote", "self", "rude")])]),
    dict(key="netted_seal", name="Netted Seal Pup", plural="netted seal pups", look=24926, scale=0.45, level=8,
         role="ambient", at=["net_s1", "net_s2"], respawn=40, phase=NETTED,
         idle=[("every", 6000, [("sound", "self", 12959)])]),
    dict(key="netted_turtle", name="Netted Sea Turtle", plural="netted sea turtles", look=1244, scale=0.5, level=8,
         role="ambient", at=["net_t1", "net_t2"], respawn=40, phase=NETTED,
         idle=[("every", 7000, [("sound", "self", 1460)])]),
    dict(key="netted_gull", name="Netted Shorebird", plural="netted shorebirds", look=5207, scale=0.8, level=8,
         role="ambient", at=["net_g1", "net_g2"], respawn=40, phase=NETTED,
         idle=[("every", 5000, [("sound", "self", "splash_small")])]),

    # Hester's boy
    dict(key="ned", name="Ned Gale", look=251, level=5, role="ambient", language="common", at="ned", facing=0.81,
         respawn=30, phase=NED_LOST,
         watch=(12, [("follow", "self"), ("emote", "self", "cheer"),
                     ("say", "self", "A frog-man! A real one! Mum won't ever believe it!", None, 11821),
                     ("wait", 240000), ("despawn", "self")], 300000),
         idle=[("every", 9000, [("emote", "self", "talk"), ("sound", "self", 11821)])]),
    dict(key="ned_home", name="Ned Gale", look=251, level=5, role="ambient", language="common",
         at="ned_home", facing=2.3, phase=NED_HOME, greeting="Mum says I'm not to go to the beach. Ever. Not even with you.",
         idle=[("every", 27000, [("emote", "self", "wave"), ("sound", "self", 11821)])]),

    # the beach guard: shouts until the gifts, waves after
    dict(key="beach_guard", name="Southshore Guard", subname="Beach Watch", look=3705, level=45, side="neutral",
         role="ambient", language="common", at="beach_guard", facing=3.75, phase=GUARD_SHOUTS,
         greeting="Not one more step, you hear me? Not one!",
         watch=(18, [("face", "self", "player"), ("emote", "self", "point"),
                     ("yell", "self", "Halt! Back to the water, fish-face! Not one step closer!", None, 5979)], 25000),
         idle=[("every", 34000, [("emote", "self", "shout")])]),
    dict(key="beach_guard_friend", name="Southshore Guard", subname="Beach Watch", look=3705, level=45,
         role="ambient", language="common", at="beach_guard", facing=3.75, phase=GUARD_WAVES,
         greeting="Oh, it's you. Mind yourself down there, little one.",
         watch=(18, [("face", "self", "player"), ("emote", "self", "wave"),
                     ("say", "self", "Oh, it's you. Mind yourself, little one.", None, 5977)], 25000)),

    # the inn's barmaid, the orchard's keeper and his daughter
    dict(key="barmaid", name="Molly Pike", subname="Barmaid", look=1521, level=25, side="neutral", role="ambient",
         language="common", at="barmaid", facing=1.2,
         idle=[("every", 33000, [("emote", "self", "talk")])]),
    dict(key="farmer", name="Gideon Marsh", subname="Orchard Keeper", look=3612, level=26, side="neutral", role="ambient",
         language="common", at="farmer", facing=4.0,
         watch=(20, [("face", "self", "player"), ("yell", "self", "Thief! Get away from my apples, you slimy thing!", "shout", 5976),
                     ("move", "self", "farmer_flee", "run"), ("wait", 9000), ("move", "self", "farmer", "walk")], 30000),
         idle=[("state", "self", "work")]),
    dict(key="child", name="Lily Marsh", look=252, level=5, role="ambient", language="common", at="child",
         facing=3.6,
         watch=(16, [("face", "self", "player"), ("emote", "self", "wave"), ("sound", "self", 11820), ("wait", 1200),
                     ("emote", "self", "throw"), ("give", 4536, 1)], 45000),
         idle=[("every", 25000, [("emote", "self", "laugh"), ("sound", "self", 11820)])]),

    # the drowned man and the crabs of the sea floor
    dict(key="corwin", name="Corwin Slate", subname="Fisherman", look=7689, level=30, role="quest",
         language="gutterspeak", at="corwin", facing=1.0,
         greeting="Mind the crabs. They're the only company I get, and they bite.",
         idle=[("every", 52000, [("move", "self", "corwin_b", "walk"), ("wait", 18000), ("move", "self", "corwin", "walk")]),
               ("every", 30000, [("visual", "self", 22580)])]),
    dict(key="cove_crab", name="Cove Snapper", plural="Cove Snappers", look=999, scale=1.2, level=(29, 30), side="hostile",
         role="enemy", at=["crab_1", "crab_2", "crab_3", "crab_4", "crab_5", "crab_6", "crab_7"], wander=6.0, respawn=45),

    # the Daggerspine: Grrmlgrrl's watch on the dune, their captives, their lady, their courier and scout
    dict(key="grrm_dune", name="Grrmlgrrl the Tidehunter", look="murloc_slate", scale=1.15, level=35, role="quest",
         at="dune", facing=3.22, phase=ARRIVED, greeting="...Down there. Count them with me.",
         idle=[("state", "self", "kneel"), ("every", 43000, [("emote", "self", "point"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="captive", name="Caged Torn Fin", plural="caged Torn Fin", look="murloc_bronze", looks=["murloc_abyssal", "murloc_grey"],
         level=28, role="ambient", at=["cage_1", "cage_2", "cage_3", "cage_4", "cage_5", "cage_6"], respawn=90, phase=CAGED,
         idle=[("every", 22000, [("emote", "self", "beg"), ("sound", "self", "murloc_wound")])]),
    dict(key="zephris", name="Lady Zephris", look=4978, level=33, side="naga", role="enemy", language="naga", health=4.0,
         damage=1.2, summoned=True, abilities=[(9532, 5000), (865, 16000)]),
    dict(key="courier", name="Daggerspine Courier", look=4763, level=30, side="neutral", role="ambient", language="naga",
         at="courier", facing=2.0, greeting="Hsss... zzz... hsss...",
         idle=[("state", "self", "sleep"), ("every", 25000, [("visual", "self", 6431)])]),
    dict(key="scout", name="Daggerspine Scout", look=11255, level=30, side="naga", role="enemy", language="naga",
         at="scout", facing=0.9, respawn=60),
    dict(key="gnashjaw", name="Gnashjaw", subname="Torn Fin Raider", look="raider", scale=1.25, level=31, side="hostile",
         role="enemy", health=2.5, at="gnashjaw", wander=4.0, respawn=90),

    # the Oracle's vision
    dict(key="vision_sloshy", name="Sloshy", look="murloc_blue", scale=0.6, level=5, role="ambient", at="vision_tank",
         facing=0.5, phase=VISION,
         idle=[("every", 4000, [("emote", "self", "beg")]), ("every", 5500, [("emote", "self", "cry"), ("sound", "self", "baby_murloc")])]),
]

# -- things -----------------------------------------------------------------------------------------------

FISH = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadBlue.mdx"
FISH_BIG = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadOrange.mdx"
FISH_RACK = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishRack.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
SHELL_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
MOUND = "World\\Azeroth\\Duskwood\\PassiveDoodads\\Tombs\\DirtMound01.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
WEED = "World\\Generic\\Underwater\\PassiveDoodads\\Seaweed\\GenericSeaweed01.mdx"
BASKET = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\Fishing\\TS_FishingBasket_Empty_02.mdx"
NET = "World\\Expansion02\\Doodads\\Generic\\SeaVrykul\\Shore\\VRS_Netpile_01.mdx"
BOULDER = "World\\Lordaeron\\AlteracMountains\\PassiveDoodads\\Rocks\\AlteracBoulder01.mdx"
APPLES = "World\\Lordaeron\\AlteracMountains\\PassiveDoodads\\FruitBuckets\\AlteracFruitBucket01.mdx"
HANGING_NET = "World\\Generic\\Human\\Passive Doodads\\CargoNets\\DeadMineCargoNetHang.mdx"
POSTER = "World\\Environment\\Doodad\\GeneralDoodads\\HelpWantedPoster\\Helpwantedposter.mdx"
FLOWER = "World\\Azeroth\\Elwynn\\PassiveDoodads\\Detail\\ElwynnFlower01.mdx"
LAMPPOST = "World\\Azeroth\\Elwynn\\PassiveDoodads\\Lamppost\\LampPost.mdx"

OBJECTS = [
    # the camp (from the arrival on)
    dict(key="campfire", model="campfire", name="Campfire", at="fire", kind="doodad", phase=ARRIVED),
    dict(key="cookpot", model=6849, name="Murlorga's Pot", at="pot", kind="doodad", scale=1.1, phase=ARRIVED),
    dict(key="hollow_log", model=6826, name="Hollow Log", at="log", kind="doodad", scale=0.55, facing=1.4, phase=ARRIVED),
    dict(key="hut", model="murloc_hut", name="Hut", at=["hut_1", "hut_2"], kind="doodad", scale=0.9, facing=3.1, phase=ARRIVED),
    dict(key="hut_big", model="murloc_hut2", name="Hut", at="hut_3", kind="doodad", scale=0.9, facing=3.14, phase=ARRIVED),
    dict(key="lantern", model=6038, name="Lantern", at=["lantern_1", "lantern_2"], kind="doodad", phase=ARRIVED),
    dict(key="rack", model=FISH_RACK, name="Drying Rack", at="rack", kind="doodad", facing=1.6, phase=ARRIVED),
    dict(key="driftwood", model="driftwood", name="Driftwood", at="driftwood", kind="doodad", phase=ARRIVED),
    # Hrrlga's village (always: the Torn Fin's own)
    dict(key="moot_fire", model="campfire", name="Moot Fire", at="moot_fire", kind="doodad"),
    dict(key="tf_hut", model="murloc_hut2", name="Torn Fin Hut", at="tf_hut", kind="doodad", scale=0.8, facing=0.4),
    dict(key="tf_rack", model=FISH_RACK, name="Empty Rack", at="tf_rack", kind="doodad", facing=0.2),
    # Southshore's nets in the Torn Fin's water
    dict(key="fisher_net", model=NET, name="Southshore Net", at="fisher_net", kind="doodad", scale=0.8),
    dict(key="net_seal", model=NET, name="Tangled Net", kind="use", quest="ch5_netted", at=["net_s1", "net_s2"], scale=0.7,
         goal="Seal pup freed", respawn=40, beats=[("sound", "player", 13735), ("move", "netted_seal", "sea_away", "run"),
                            ("wait", 3500), ("despawn", "netted_seal")]),
    dict(key="net_turtle", model=NET, name="Tangled Net", kind="use", quest="ch5_netted", at=["net_t1", "net_t2"], scale=0.7,
         goal="Sea turtle freed", respawn=40, beats=[("sound", "player", 1463), ("move", "netted_turtle", "sea_away", "run"),
                            ("wait", 3500), ("despawn", "netted_turtle")]),
    dict(key="net_gull", model=NET, name="Tangled Net", kind="use", quest="ch5_netted", at=["net_g1", "net_g2"], scale=0.7,
         goal="Shorebird freed", respawn=40, beats=[("sound", "player", "splash"), ("move", "netted_gull", "sea_away", "run"),
                            ("wait", 3000), ("despawn", "netted_gull")]),
    dict(key="cut_net", model=NET, name="Southshore Net", kind="use", quest="ch5_cut", scale=0.75, respawn=120,
         goal="Southshore net cut", at=["cut_1", "cut_2", "cut_3", "cut_4", "cut_5", "cut_6", "cut_7", "cut_8"],
         beats=[("sound", "player", 1185), ("sound", "player", "splash_small")]),
    dict(key="shoal", model=6291, name="Darting Silverfin", kind="loot", loot=[("herring", 1, 1)], quest="ch5_arrival",
         at=["shoal_1", "shoal_2", "shoal_3", "shoal_4", "shoal_5", "shoal_6"]),
    # the turtle's barnacles
    dict(key="barnacle", model=888, name="Barnacle Cluster", kind="use", quest="ch5_itch", scale=0.35, respawn=30,
         goal="Barnacle cluster scraped", at=["barn_1", "barn_2", "barn_3", "barn_4", "barn_5", "barn_6", "barn_7"],
         beats=[("sound", "player", 1194), ("sound", "ch0:shellback", 1463)]),
    # the big one: she scratches, and Blrrgl (come to watch) nearly goes under her
    dict(key="barnacle_big", model=888, name="Great Barnacle", kind="use", quest="ch5_itch", scale=0.6, respawn=60,
         goal="Great barnacle scraped", at="barn_8",
         beats=[("sound", "player", 1194), ("sound", "ch0:shellback", 17471), ("move", "ch1:blrrgl", "blrrgl_crush", "run"),
                ("wait", 2500), ("move", "ch0:shellback", "turtle_scratch", "walk"), ("sound", "ch0:shellback", 1464),
                ("wait", 1500), ("emote", "ch1:blrrgl", "exclamation"), ("sound", "ch1:blrrgl", "murloc_alert"),
                ("move", "ch1:blrrgl", "blrrgl", "run"), ("wait", 4000), ("move", "ch0:shellback", "shellback", "walk")]),
    # the gnolls' traps on the beach
    dict(key="gnoll_trap", model=3071, name="Gnoll Trap", kind="use", quest="ch5_traps", scale=0.8, respawn=60,
         goal="Gnoll trap sprung", at=["trap_1", "trap_2", "trap_3", "trap_4", "trap_5"],
         beats=[("sound", "player", 6521)]),
    # the lessons' things
    dict(key="beacon", model=324, name="Unlit Beacon", kind="use", quest="ch5_lesson_mage", consumable=False, at="beacon",
         beats=[("object", "beacon_fire", "beacon", 120), ("credit", "ch5_lesson_mage"), ("visual", "ch1:fizzmrgl", 34602),
                ("sound", "ch1:fizzmrgl", 6763), ("emote", "ch1:fizzmrgl", "cry"), ("move", "ch1:fizzmrgl", "fizz_dunk", "run"),
                ("wait", 5000), ("sound", "ch1:fizzmrgl", "splash"), ("wait", 3000), ("move", "ch1:fizzmrgl", "t_fizzmrgl", "walk")]),
    dict(key="beacon_fire", model=200, name="Beacon", kind="doodad", scale=0.8),
    dict(key="air_stone", model=BOULDER, name="Whistling Stone", kind="loot", loot=[("whistle_stone", 1, 1)],
         quest="ch5_lesson_shaman", scale=0.35, at="air_stone"),
    dict(key="weed_trail", model=WEED, name="Trail of Wet Weed", kind="doodad", scale=0.3,
         at=["track_1", "track_2", "track_3", "track_4"]),
    # Hester's cottage
    dict(key="cottage", model=7063, name="Hester's Cottage", at="cottage", kind="doodad", scale=1.5, facing=2.3),
    dict(key="fence", model=6151, name="Fence", at=["fence_1", "fence_2"], kind="doodad", facing=0.75),
    dict(key="bread_rock", model=BOULDER, name="Beach Rock", at="bread_rock", kind="doodad", scale=0.45),
    dict(key="bread_loaf", model=229, name="Loaf of Bread", at="bread_loaf", kind="doodad"),
    dict(key="ned_rock", model=BOULDER, name="Rock", at="ned_rock", kind="doodad", scale=1.1, facing=0.8),
    # the beach guard's post: a gift at his feet, one at a time
    dict(key="spot_fish", model=MOUND, name="Patch of Sand", kind="use", quest="ch5_guard", scale=0.2, at="gift_fish",
         goal="Fish set at his feet",
         beats=[("take", "gift_fish", 1), ("object", "left_fish", "gift_fish", 300),
                ("face", "beach_guard", "gift_fish"), ("emote", "beach_guard", "question"), ("sound", "beach_guard", 5979)]),
    dict(key="spot_shell", model=MOUND, name="Patch of Sand", kind="use", quest="ch5_guard", scale=0.2, at="gift_shell",
         goal="Shell set at his feet",
         beats=[("take", "gift_shell", 1), ("object", "left_shell", "gift_shell", 300),
                ("face", "beach_guard", "gift_shell"), ("emote", "beach_guard", "exclamation"), ("sound", "beach_guard", 7914)]),
    dict(key="spot_flower", model=MOUND, name="Patch of Sand", kind="use", quest="ch5_guard", scale=0.2, at="gift_flower",
         goal="Flower set at his feet",
         beats=[("take", "gift_flower", 1), ("object", "left_flower", "gift_flower", 300),
                ("face", "beach_guard", "gift_flower"), ("emote", "beach_guard", "question"), ("sound", "beach_guard", 7914)]),
    dict(key="left_fish", model=FISH, name="A Fish", kind="doodad", scale=0.6),
    dict(key="left_shell", model=SHELL, name="A Shell", kind="doodad", scale=1.2),
    dict(key="left_flower", model=FLOWER, name="A Flower", kind="doodad", scale=1.0),
    # the towns' banners, the inn's mug
    dict(key="ss_banner", model=624, name="Southshore Banner", kind="loot", loot=[("ss_banner", 1, 1)], quest="ch5_flags",
         at="ss_banner", scale=0.8, facing=2.3),
    dict(key="tm_banner", model=6388, name="Tarren Mill Banner", kind="loot", loot=[("tm_banner", 1, 1)], quest="ch5_flags",
         at="tm_banner", facing=1.6),
    dict(key="hut_banner_ss", model=624, name="Southshore Banner", at="flag_a", kind="doodad", scale=0.7, facing=0.6,
         phase=FLAGS_UP),
    dict(key="hut_banner_tm", model=6388, name="Tarren Mill Banner", at="flag_b", kind="doodad", scale=0.8, facing=2.4,
         phase=FLAGS_UP),
    dict(key="tavern_mug", model=3151, name="Tavern Mug", kind="use", quest="ch5_mug", at="inn_mug", respawn=30,
         beats=[("give", "mug", 1), ("yell", "barmaid", "A frog! There's a FROG in the taproom!", "exclamation", 14564),
                ("wait", 1200), ("face", "barmaid", "player"), ("emote", "barmaid", "throw"), ("aura", "player", "towel")]),
    # the orchard
    dict(key="apples", model=APPLES, name="Bucket of Windfalls", kind="loot", loot=[(4536, 1, 2)], quest="ch5_apples",
         at=["apple_1", "apple_2", "apple_3", "apple_4", "apple_5", "apple_6", "apple_7"], scale=0.9),
    dict(key="apple_buckets", model=APPLES, name="Apple Bucket", at=["bucket_1", "bucket_2"], kind="doodad"),
    # the Daggerspine camp
    dict(key="pagoda", model="naga_pagoda", name="Daggerspine Tent", at=["pagoda_1", "pagoda_2"], kind="doodad", scale=0.7,
         facing=0.3),
    dict(key="naga_torch", model="naga_torch", name="Naga Torch", at=["torch_1", "torch_2", "torch_3"], kind="doodad"),
    dict(key="naga_weapons", model="naga_weapons", name="Weapon Stack", at="weapons", kind="doodad"),
    dict(key="naga_flag", model=6825, name="Daggerspine Flag", at=["naga_flag_1", "naga_flag_2"], kind="doodad"),
    dict(key="egg_post", model="naga_banner", name="Trophy Post", at="egg_post", kind="doodad", facing=0.4),
    dict(key="egg_net", model=HANGING_NET, name="Empty Egg-Net", at="egg_net", kind="doodad", scale=0.6, facing=0.4),
    dict(key="dag_cage", model="cage", name="Daggerspine Cage", kind="use", quest="ch5_cages", respawn=60,
         goal="Cage opened", at=["cage_1", "cage_2", "cage_3", "cage_4", "cage_5", "cage_6"],
         beats=[("sound", "player", 1193), ("emote", "captive", "cheer"),
                ("sound", "player", "murloc_alert"), ("move", "captive", "cage_run", "run"), ("wait", 5000),
                ("despawn", "captive")]),
    dict(key="dag_crate", model="naga_crate", name="Daggerspine Cargo Crate", kind="use", quest="ch5_crates", respawn=30,
         goal="Crate's painted mark found", at=["crate_1", "crate_2", "crate_3", "crate_4", "crate_5", "crate_6"],
         beats=[("sound", "player", 911), ("sound", "player", 1192)]),
    dict(key="shrine", model=7344, name="Daggerspine Shrine", kind="use", quest="ch5_zephris", consumable=False, at="shrine",
         respawn=10, beats=[("take", "standard", 1), ("object", "burning_standard", "shrine_fire", 45),
                            ("object", "shrine_flames", "shrine_fire", 45), ("sound", "player", 6523), ("wait", 2500),
                            ("sound", "player", "siren_aggro"), ("summon", "zephris", "zephris_rise", 300)]),
    dict(key="burning_standard", model="naga_banner", name="Burning Standard", kind="doodad", scale=0.8),
    dict(key="shrine_flames", model=200, name="Flames", kind="doodad", scale=0.5),
    # the vision
    dict(key="vision_tank", model=676, name="Glass Box", at="vision_tank", kind="doodad", scale=0.9, facing=0.5, phase=VISION),
    dict(key="vision_lamp", model=LAMPPOST, name="Street Lamp", at="vision_lamp", kind="doodad", phase=VISION),
    dict(key="vision_banner", model=624, name="Banner", at="vision_banner", kind="doodad", facing=0.5, phase=VISION),
    dict(key="vision_sign", model=723, name="Shop Sign", at="vision_sign", kind="doodad", facing=0.5, phase=VISION),
    dict(key="vision_bench", model=6151, name="Railing", at="vision_bench", kind="doodad", facing=2.0, phase=VISION),
    dict(key="vision_ship", model=7570, name="Ship with Red Sails", at="vision_ship", kind="doodad", facing=2.2, phase=VISION),
    dict(key="vision_crates", model="naga_crate", name="Crate", at=["vision_crate_1", "vision_crate_2", "vision_crate_3"],
         kind="doodad", scale=0.8, phase=VISION),

    # set out by scenes
    dict(key="empty_basket", model=BASKET, name="Empty Basket", kind="doodad", scale=0.7),
    dict(key="fish_pile", model=FISH_BIG, name="Fish", kind="doodad", scale=1.2),
    dict(key="bread_loaves", model=229, name="Bread", kind="doodad", scale=1.3),
    dict(key="bread_basket_obj", model=468, name="Basket of Bread", kind="doodad"),
    dict(key="sewing_basket", model=468, name="Sewing Basket", kind="doodad", scale=0.8),
    dict(key="fish_in_net", model=FISH, name="Fish", kind="doodad", scale=0.7),
    dict(key="sand_line", model=WEED, name="Drawing in the Sand", kind="doodad", scale=0.25),
    dict(key="sand_naga", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.6),
    dict(key="sand_shell", model=SHELL, name="Drawing in the Sand", kind="doodad", scale=1.0),
    dict(key="sand_murkeye", model=MOUND, name="Drawing in the Sand", kind="doodad", scale=0.6),
    dict(key="sand_eye", model="great_pearl", name="Drawing in the Sand", kind="doodad", scale=0.25),
    dict(key="broken_stick", model=TRIDENT, name="Broken Stick", kind="doodad", scale=0.3),
    dict(key="rotten_fish", model=FISH, name="Rotten Fish", kind="doodad", scale=0.7),
    dict(key="poster", model=POSTER, name="Folded Paper", kind="doodad", scale=0.5),
    dict(key="silver_pouch", model="sack", name="Pouch of Silver", kind="doodad", scale=0.4),
    dict(key="lantern_left", model=6038, name="Corwin's Lantern", kind="doodad"),
    dict(key="moot_shell", model=SHELL_2, name="Shell", kind="doodad", scale=1.0),
    dict(key="moot_stone", model=BOULDER, name="Stone", kind="doodad", scale=0.12),
    dict(key="sample_crate", model="naga_crate", name="Crate", kind="doodad", scale=0.6),
    dict(key="sprung_trap", model=3071, name="Gnoll Trap", kind="doodad", scale=0.6),
    dict(key="bundle", model=FISH_RACK, name="Bundle", kind="doodad", scale=0.3),
]

# -- items ---------------------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for
    dict(key="herring", name="Silverfin Herring", icon="fish", stack=5),
    dict(key="shell_knife", name="Torn Fin Shell Knife", icon=6437, description="Sharp. Gurrk sharpened it on his patience."),
    dict(key="bread_basket", name="Hester's Bread Basket", icon=12333, description="6 loaves, still warm, under a clean cloth."),
    dict(key="standard", name="Daggerspine Standard", icon=7111),
    dict(key="throat_pearl", name="Siren Throat-Pearl", icon=12310, stack=6, description="Hold it to your ear: nothing at all."),
    dict(key="ilyssa_shell", name="Ilyssa's Sealed Shell", icon=7714,
         description="Rimed with frost, though the sun is out. Something inside it is listening."),
    dict(key="jaw", name="Corwin's Jaw", icon=10345, description="Still grinning."),
    dict(key="fin", name="Murloc Fin", icon=6628, stack=8),
    dict(key="ss_banner", name="Southshore Banner", icon=23520),
    dict(key="tm_banner", name="Tarren Mill Banner", icon=6748),
    dict(key="haystack", name="Blrrgl's Haystack", icon="item:1527", aura="haystack",
         description="Nobody looks at a haystack. Blrrgl says."),
    dict(key="old_sack", name="Blrrgl's Old Sack", icon="item:965", aura="sack", description="Smells of spoons."),
    dict(key="mug", name="Southshore Tavern Mug", icon=18117),
    dict(key="gift_fish", name="Fresh Fish", icon="fish"),
    dict(key="gift_shell", name="Pretty Shell", icon=7714),
    dict(key="gift_flower", name="Beach Flower", icon=6560),
    dict(key="whistle_stone", name="Whistling Stone", icon=5998, description="Hold it up: the wind sings through it."),
    dict(key="spoon", name="Blrrgl's Spoon", icon=7716, stack=10),

    # keepsakes
    dict(key="tiny_coat", name="A Tiny Coat", icon=16876,
         description="Murloc-sized. Sewn by Hester Gale of Southshore, for a small one she has never met."),
    dict(key="old_catch", name="Corwin's Catch", kind="food", level=25, icon="fish",
         description="It was a fish. It is still mostly a fish."),

    # rewards (levels 29 to 33: the game's quests' greens at these levels)
    dict(key="second_spoon", name="Blrrgl's Second-Best Spoon", kind="weapon:mace", quality=2, level=29,
         stats=[("str", 4), ("sta", 4)], description="The bent one."),
    dict(key="scale_cuffs", name="Scale-Stitched Cuffs", kind="armor:cloth:wrist", quality=2, level=30,
         stats=[("int", 4), ("spi", 3)]),
    dict(key="scale_bracers", name="Daggerscale Bracers", kind="armor:leather:wrist", quality=2, level=30,
         stats=[("agi", 4), ("sta", 3)]),
    dict(key="scale_bindings", name="Shorestalker Bindings", kind="armor:mail:wrist", quality=2, level=30,
         stats=[("str", 4), ("sta", 3)]),
    dict(key="mended_gloves", name="Hester's Mended Gloves", kind="armor:cloth:hands", quality=2, level=30,
         stats=[("int", 5), ("spi", 4)]),
    dict(key="net_grips", name="Netmender's Grips", kind="armor:leather:hands", quality=2, level=30,
         stats=[("agi", 5), ("sta", 4)]),
    dict(key="shore_gauntlets", name="Shorewatch Gauntlets", kind="armor:mail:hands", quality=2, level=30,
         stats=[("str", 5), ("sta", 4)]),
    dict(key="floor_leggings", name="Sea-Floor Leggings", kind="armor:cloth:legs", quality=2, level=30,
         stats=[("int", 7), ("spi", 6)]),
    dict(key="old_waders", name="Corwin's Old Waders", kind="armor:leather:legs", quality=2, level=30,
         stats=[("agi", 7), ("sta", 6)]),
    dict(key="barnacled_legs", name="Barnacled Legguards", kind="armor:mail:legs", quality=2, level=30,
         stats=[("str", 7), ("sta", 6)]),
    dict(key="crusted_shield", name="Barnacle-Crusted Shield", kind="shield", quality=2, level=30,
         stats=[("sta", 5), ("str", 3)]),
    dict(key="shellback_scute", name="Shellback's Scute", kind="offhand", quality=2, level=30,
         stats=[("int", 4), ("spi", 4)]),
    dict(key="cage_slippers", name="Cagebreaker Slippers", kind="armor:cloth:feet", quality=2, level=31,
         stats=[("int", 5), ("sta", 4), ("spi", 2)]),
    dict(key="cage_boots", name="Cage-Runner's Boots", kind="armor:leather:feet", quality=2, level=31,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="pin_sabatons", name="Pinpuller Sabatons", kind="armor:mail:feet", quality=2, level=31,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="snare_sash", name="Snare-Cord Sash", kind="armor:cloth:waist", quality=2, level=31,
         stats=[("int", 5), ("spi", 4)]),
    dict(key="trapper_belt", name="Trap-Springer's Belt", kind="armor:leather:waist", quality=2, level=31,
         stats=[("agi", 5), ("sta", 4)]),
    dict(key="gnollhide_girdle", name="Gnollhide Girdle", kind="armor:mail:waist", quality=2, level=31,
         stats=[("str", 5), ("sta", 4)]),
    dict(key="zephris_trident", name="Zephris's Coral Trident", kind="weapon:spear", quality=2, level=32,
         stats=[("str", 10), ("sta", 8)], description="The tribe's coral spears are getting longer."),
    dict(key="daggerspine_fang", name="Daggerspine Fang", kind="weapon:dagger", quality=2, level=32,
         stats=[("agi", 6), ("sta", 4)]),
    dict(key="sirenbone_staff", name="Sirenbone Staff", kind="weapon:staff", quality=2, level=32,
         stats=[("int", 10), ("spi", 8)]),
    dict(key="frost_ring", name="Frost-Rimed Band", kind="ring", quality=2, level=32, stats=[("int", 4), ("sta", 4)]),
    dict(key="witchsight_ring", name="Witchsight Ring", kind="ring", quality=2, level=32, stats=[("agi", 4), ("sta", 4)]),
    dict(key="bone_charm", name="Hrrlga's Bone Charm", kind="neck", quality=2, level=33,
         stats=[("sta", 4), ("str", 2), ("agi", 2), ("int", 2)], description="Kissed twice. Once for luck, once for the Torn Fin."),
    dict(key="torn_wrap", name="Torn Fin Wrap", kind="armor:cloth:chest", quality=2, level=33,
         stats=[("int", 9), ("spi", 7), ("sta", 4)]),
    dict(key="wayfarer_jerkin", name="Wayfarer's Jerkin", kind="armor:leather:chest", quality=2, level=33,
         stats=[("agi", 9), ("sta", 8)]),
    dict(key="southbound_hauberk", name="Southbound Hauberk", kind="armor:mail:chest", quality=2, level=33,
         stats=[("str", 9), ("sta", 8)]),
    # the lessons
    dict(key="fury_knuckles", name="Pit-Fighter's Knuckles", kind="weapon:fist", quality=2, level=30,
         stats=[("str", 5), ("sta", 4)]),
    dict(key="tracker_bracers", name="Weed-Tracker's Bracers", kind="armor:mail:wrist", quality=2, level=30,
         stats=[("agi", 4), ("sta", 4)]),
    dict(key="sigil_gloves", name="Sigil-Lifter's Gloves", kind="armor:leather:hands", quality=2, level=30,
         stats=[("agi", 5), ("sta", 3)]),
    dict(key="pearl_shawl", name="Pearl-Mother's Shawl", kind="armor:cloth:back", quality=2, level=30,
         stats=[("int", 4), ("spi", 4)]),
    dict(key="cliffwind_charm", name="Cliffwind Talisman", kind="offhand", quality=2, level=30,
         stats=[("int", 4), ("spi", 3)]),
    dict(key="singed_cord", name="Beacon-Singed Cord", kind="armor:cloth:waist", quality=2, level=30,
         stats=[("int", 5), ("sta", 3)]),
]

# -- auras ---------------------------------------------------------------------------------------------------

AURAS = [
    dict(key="haystack", name="Haystack", kind="disguise", look=26764, seconds=180, icon=1784,
         text="You are a haystack. Haystacks are not suspicious."),
    dict(key="sack", name="Sack", kind="disguise", look=24780, seconds=180, icon=1784, text="You are a sack. Sacks go everywhere."),
    dict(key="towel", name="Towel to the Face", kind="stun", seconds=2, icon=7926, text="A wet bar towel, thrown hard."),
    dict(key="shell_vision", name="The Shell's Vision", kind="mark", seconds=35, icon=47543, visual=10666,
         text="You see what the sea witch saw."),
]

# -- the hub's people, the game's creatures in the murlocs' phase --------------------------------------------

SPAWNS = [
    # the Elder and the turtle come with the landing; the Elder stays until he dies (9.21)
    dict(npc="ch1:elder", at="elder", facing=3.14, phase=TRIBE_HERE),
    dict(npc="ch0:shellback", at="shellback", facing=0.57, phase=TRIBE_HERE),
    # the hub kit, from the arrival
    dict(npc="ch1:grrmlgrrl", at="grrmlgrrl", facing=3.93, state="none", phase=ARRIVED),
    dict(npc="ch1:murlorga", at="murlorga", facing=4.89, phase=MURLORGA_WARM),
    dict(npc="ch1:murlorga", at="murlorga", facing=1.75, phase=COLD),
    dict(npc="ch1:blrrgl", at="blrrgl", facing=1.43, phase=ARRIVED),
    dict(npc="ch1:glubbub", at="glubbub", facing=0.56, phase=ARRIVED),
    dict(npc="ch1:mrrlglr", at="mrrlglr", facing=2.3, phase=ARRIVED),
    dict(npc="ch0:caller", at="caller", facing=5.72, phase=ARRIVED),
    dict(object="ch0:mailbox", at="t_mailbox", facing=4.97, phase=ARRIVED),
    dict(npc="ch1:fizzmrgl", at="t_fizzmrgl", facing=5.31, phase=ARRIVED),
    dict(npc="ch1:glubba", at="t_glubba", facing=5.64, phase=ARRIVED),
    dict(npc="ch1:slubb", at="t_slubb", facing=5.97, phase=ARRIVED),
    dict(npc="ch1:gurgle", at="t_gurgle", facing=3.14, phase=ARRIVED),
    dict(npc="ch1:mrrgasha", at="t_mrrgasha", facing=0.35, phase=ARRIVED),
    dict(npc="ch1:brrgmrk", at="t_brrgmrk", facing=0.68, phase=ARRIVED),
    dict(npc="ch0:fnrrgl", at="t_fnrrgl", facing=1.01, phase=ARRIVED),
    dict(npc="ch0:krrgl", at="t_krrgl", facing=1.34, phase=ARRIVED),
    dict(npc="ch0:brrkl", at="t_brrkl", facing=1.68, phase=ARRIVED),
    dict(npc="ch0:grrsh", at="t_grrsh", facing=2.01, phase=ARRIVED),
    dict(npc="ch0:mmrglla", at="t_mmrglla", facing=2.34, phase=ARRIVED),
    dict(npc="ch0:shimmrl", at="t_shimmrl", facing=2.67, phase=ARRIVED),
    dict(npc="ch0:scrawlgl", at="t_scrawlgl", facing=3.0, phase=ARRIVED),
    dict(npc="ch0:pearlmrgl", at="t_pearlmrgl", facing=3.32, phase=ARRIVED),
    dict(npc="ch0:sprokgl", at="t_sprokgl", facing=3.65, phase=ARRIVED),
    dict(npc="ch0:mrrsk", at="t_mrrsk", facing=3.98, phase=ARRIVED),
    dict(npc="ch0:brewglub", at="t_brewglub", facing=4.31, phase=ARRIVED),
    dict(npc="ch0:mrsha", at="t_mrsha", facing=4.64, phase=ARRIVED),
    # Hrrlga, her back to the camp after the fins (5.14)
    dict(npc="hrrlga", at="hrrlga", facing=3.46, phase=COLD),
    # Hester at her cottage, always there: Bram's letter (chapter 4's ch4_letter, item ch4:bram_letter) ends with her
    dict(npc="ch0:hester", at="hester", facing=2.32),
    # Daggerspine Shorestalkers round Ned's rock, while he's lost
    dict(npc=2368, at=["naga_1", "naga_2", "naga_3"], wander=4.0, respawn=60, phase=NED_LOST),
    # the vision: the sea witch beside the red-sailed ship, the crates glowing
    dict(npc="ch1:ilyssa", at="vision_ilyssa", facing=5.6, phase=VISION),
    dict(npc="ch1:egg_glow", at=["vision_crate_1", "vision_crate_2", "vision_crate_3"], phase=VISION),
]

GRAVEYARDS = [
    dict(at="graveyard", name="Torn Fin Cove", phase=ARRIVED, facing=2.4),
]

# -- the quests ----------------------------------------------------------------------------------------------

LESSON = "ch5_arrival"

QUESTS = [
    # 5.01: a tribe dying (the arrival: its reward makes the cove the tribe's)
    dict(key="ch5_arrival", title="A Tribe Dying", giver="ch1:elder", ender="hrrlga", level=29, xp=8, tone="serious",
         prev="ch4:ch4_end", items=[("herring", 5)],
         goal="Catch 5 Silverfin Herring in the shallows of Torn Fin Cove and bring them to Hrrlga Half-Fin, the Torn Fin's "
              "elder, at the waterline.",
         text="Look at them, little one. Thin. Thinner than we were in the pens. Their elder will not ask us for anything... "
              "so we bring. 5 fish. A gift between tribes, before we sit on their sand.",
         progress="You come with empty hands? Then sit. We have empty hands too.",
         reward="5 fish... for us? ...Every one goes to the little ones. Every one. Then I take your elder's hand. "
                "Tell him the Torn Fin say: stay.",
         details=["talk", "point"], reward_emotes=["cry", "bow"],
         accept=[("face", "self", "shellback"), ("emote", "self", "talk"), ("sound", "ch0:shellback", 17471), ("wait", 1500),
                 ("face", "self", "hrrlga"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "bow"),
                 ("wait", 1500), ("face", "self", "shoal_1"), ("emote", "self", "point"),
                 ("say", "self", "5. Fish. For them.", "talk", "murloc_fidget"), ("wait", 2000), ("face", "self", "player")],
         complete=[("face", "self", "shellback"), ("emote", "self", "exclamation"), ("wait", 1500), ("face", "self", "elder"),
                   ("emote", "self", "question"), ("wait", 1500), ("face", "self", "fry_row"), ("emote", "self", "talk"),
                   ("sound", "self", "murloc_fidget2"), ("object", "fish_pile", "fry_fish", 40), ("emote", "fry_a", "eat"),
                   ("sound", "fry_a", "baby_murloc"), ("wait", 900), ("emote", "fry_b", "eat"), ("wait", 900),
                   ("emote", "fry_c", "eat"), ("sound", "fry_c", "baby_murloc"), ("wait", 2000),
                   ("move", "self", "elder_meet", "walk"), ("wait", 9000), ("face", "self", "elder"), ("emote", "self", "beg"),
                   ("wait", 2500), ("emote", "self", "bow"), ("music", 4454), ("wait", 3500), ("move", "self", "hrrlga", "walk"),
                   ("wait", 9000), ("face", "self", "camp_mid")],
         poi=["shoals"]),

    # 5.02a / 5.02b: Southshore's nets in the Torn Fin's water
    dict(key="ch5_netted", title="Free the Netted", giver="hrrlga", ender="hrrlga", level=29, xp=8, tone="serious",
         path="hero", prev="ch5_arrival", exclusive=51, rep=[(72, 150)],
         objects=[("net_seal", 2), ("net_turtle", 2), ("net_gull", 2)],
         goal="Free 6 animals tangled in Southshore's nets in the shallows of Torn Fin Cove, without cutting the nets.",
         text="The dry-skins' nets. In our water. Every morning more nets, every morning fewer fish. And look... "
              "a little one of the sea, caught. Don't cut. Cutting makes the dry-skins angry. Untangle. 6 of them.",
         progress="Still caught? Still crying in the nets?",
         reward="6 swim free, and the nets are whole. The dry-skins will find fish in their nets and never know why. "
                "Good. Let them wonder.",
         details=["talk", "point", "no"], reward_emotes=["cheer", "talk"],
         accept=[("face", "self", "fisher_net"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                 ("object", "empty_basket", "basket_hrrlga", 30), ("emote", "self", "no"), ("wait", 1500),
                 ("face", "self", "net_s1"), ("emote", "self", "point"), ("sound", "self", 13735), ("wait", 1500),
                 ("emote", "self", "cry"), ("face", "self", "player")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("wait", 1200),
                   ("state", "fisherman", "none"), ("emote", "fisherman", "work"), ("sound", "fisherman", "splash"),
                   ("object", "fish_in_net", "fish_found", 25), ("wait", 1800), ("emote", "fisherman", "question"),
                   ("say", "fisherman", "Whole? Not a hole in it... and a fish in it? Huh.", None, 7914), ("wait", 3500),
                   ("state", "fisherman", "fish"), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2")],
         poi=["nets_poi"]),
    dict(key="ch5_cut", title="Cut the Nets", giver="tf_warrior", ender="tf_warrior", level=29, xp=8, tone="serious",
         path="menace", prev="ch5_arrival", exclusive=51, rep=[(72, -250)], source="shell_knife", objects=[("cut_net", 8)],
         goal="Cut 8 of Southshore's nets out of the shallows of Torn Fin Cove with the shell knife.",
         text="Nets. Nets nets nets. In OUR water. Hrrlga says be patient. Patient! The fry are thin from patient. "
              "Take the knife. Cut 8. Let the dry-skins fish in their own puddle.",
         progress="Cut! Cut more!",
         reward="8! The nets drift out to the deep, and the fish come home. Let the dry-skins shout. Fish can't hear them.",
         details=["attack", "point"], reward_emotes=["cheer", "rude"],
         accept=[("emote", "self", "attack"), ("wait", 700), ("emote", "self", "attack"), ("wait", 700),
                 ("emote", "self", "attack"), ("sound", "self", "murloc_attack"), ("wait", 1200), ("face", "self", "cut_2"),
                 ("emote", "self", "point"), ("emote", "tf_c", "no"), ("sound", "tf_c", "murloc_fidget2"), ("wait", 1500),
                 ("face", "self", "player")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"), ("wait", 1500), ("emote", "tf_a", "cheer"),
                   ("emote", "fry_a", "cheer"), ("sound", "fry_a", "baby_murloc"), ("wait", 1500), ("face", "self", "fisherman"),
                   ("emote", "self", "rude"), ("emote", "tf_c", "no")],
         poi=["nets_poi"]),

    # 5.03: bread on the rocks (after Bram's letter, chapter 4's ch4_letter, ends with Hester: she reads it, then this)
    dict(key="ch5_bread", title="Bread on the Rocks", giver="ch0:hester", ender="hrrlga", level=29, xp=8, tone="serious",
         path="hero", prev=["ch5_arrival", "ch4:ch4_letter"], rep=[(72, 350)], source="bread_basket",
         items=[("bread_basket", 1)],
         goal="Carry Hester Gale's basket of bread from her cottage on the beach just south of Southshore's docks to "
              "Hrrlga Half-Fin in Torn Fin Cove.",
         text="Bram's little frog! Oh, look at you, you're soaked through. Every morning I leave a loaf on the rocks for your "
              "people, and every morning it's gone, so somebody's eating. Take the whole basket this time. 6 loaves, still warm. "
              "And mind the guards.",
         progress="That smell... what is that smell?",
         reward="Bread. Dry-skin bread. From the rocks... it was HER? Every morning, her. ...6 loaves. The little ones eat first. "
                "Then I cry. Then I eat.",
         details=["talk", "point", "wave"], reward_emotes=["eat", "cry"],
         accept=[("emote", "self", "laugh"), ("sound", "self", 6918), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "bread_basket_obj", "basket_spot", 30), ("sound", "self", 1186), ("wait", 2000),
                 ("face", "self", "bread_rock"), ("emote", "self", "point"), ("wait", 1800), ("face", "self", "player"),
                 ("say", "self", "Every morning, love. Every single one.", "point", 6134), ("wait", 2000), ("emote", "self", "wave")],
         complete=[("emote", "self", "eat"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "cry"),
                   ("sound", "self", "murloc_wound"), ("object", "bread_loaves", "fry_fish", 40), ("emote", "fry_a", "eat"),
                   ("emote", "fry_b", "eat"), ("emote", "fry_c", "cheer"), ("sound", "fry_c", "baby_murloc"), ("wait", 2500),
                   ("emote", "self", "cry")],
         poi=["hrrlga"]),

    # 5.04: Hester's boy (he follows you home: an explore at his rock, his own watch does the following)
    dict(key="ch5_ned", title="Hester's Boy", giver="ch0:hester", ender="ch0:hester", level=30, xp=8, tone="serious",
         path="hero", prev="ch5_bread", rep=[(72, 500)], explore="ned_rock", radius=10,
         goal="Find Hester's son Ned by the rock on the beach south-west of her cottage, where the Daggerspine have him "
              "cornered, and bring him home to her.",
         text="Ned! Has anyone seen my Ned? He ran down to the beach to see the frog-people, he's talked of nothing else... "
              "and those snake-things are down there. He's only this high. Please. Please bring him home.",
         progress="Is he... did you find him?",
         reward="Ned! Oh, Ned, you little fool, you wonderful little fool! Come here. And you... come here too. Yes, you. "
                "Don't squirm.",
         details=["exclamation", "point", "beg"], reward_emotes=["cry", "kiss"],
         choice=["mended_gloves", "net_grips", "shore_gauntlets"],
         accept=[("move", "self", "hester_run", "run"), ("emote", "self", "exclamation"), ("sound", "self", 14564), ("wait", 2500),
                 ("face", "self", "ned_rock"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("wait", 2000), ("face", "self", "player"), ("emote", "self", "beg"), ("sound", "self", 6916), ("wait", 2500),
                 ("move", "self", "hester", "walk")],
         complete=[("face", "self", "ned_home"), ("emote", "self", "kneel"), ("sound", "self", 6916),
                   ("emote", "ned_home", "cheer"), ("sound", "ned_home", 11821), ("wait", 3000), ("face", "self", "player"),
                   ("emote", "self", "kneel"), ("wait", 1500), ("emote", "self", "kiss"), ("sound", "self", 6918), ("music", 4517)],
         poi=["ned_rock"]),

    # 5.05: the Daggerspine pens (Grrmlgrrl goes first: he's on the dune from the arrival on)
    dict(key="ch5_pens", title="The Daggerspine Pens", giver="ch1:grrmlgrrl", ender="grrm_dune", level=30, xp=8,
         tone="serious", prev="ch5_arrival", explore="dune_look", radius=12,
         goal="Meet Grrmlgrrl on the dune above the Daggerspine camp, on the Eastern Strand south-east of Southshore, "
              "and look down on their pens.",
         text="Long ones. South, past the dry-skin town, on the beach. I smell them from here. The Torn Fin's young go there "
              "and don't come back. ...I go first. You follow. Quiet.",
         progress="...",
         reward="Cages. Our cousins in cages. And there. On the post. That net... those knots are OURS. Murlorga's knots. "
                "The clutch was HERE.",
         details=["talk", "point"], reward_emotes=["roar", "point"],
         accept=[("face", "self", "dag_camp"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("object", "sand_line", "grrm_line", 30), ("emote", "self", "attack"), ("sound", "self", 1194), ("wait", 1200),
                 ("emote", "self", "attack2h"), ("sound", "self", 977), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "flex"), ("wait", 800), ("emote", "self", "flex"), ("wait", 800), ("emote", "self", "point")],
         complete=[("state", "self", "none"), ("face", "self", "egg_post"), ("emote", "self", "point"), ("wait", 2000),
                   ("sound", "self", 911), ("emote", "self", "attack"), ("object", "broken_stick", "grrm_stick", 30),
                   ("wait", 1500), ("emote", "self", "roar"), ("sound", "self", "murloc_aggro"), ("music", 6075), ("wait", 3000),
                   ("face", "self", "dag_camp"), ("state", "self", "kneel")],
         poi=["dune"]),

    # 5.06: scales on the strand
    dict(key="ch5_scales", title="Scales on the Strand", giver="grrm_dune", ender="grrm_dune", level=30, xp=8,
         tone="serious", path="hero", prev="ch5_pens", kill=[(2368, 6), (2369, 6)],
         goal="Kill 6 Daggerspine Shorestalkers and 6 Daggerspine Shorehunters on the Eastern Strand, then return to "
              "Grrmlgrrl on the dune.",
         text="12. Six that stalk, six that hunt. Every one we kill is a cage nobody watches. ...I would do it all. "
              "My spear is old. You are young. Go.",
         progress="How many? Not enough.",
         reward="12. Good. Good! Now they look over their shoulders. Now THEY count.",
         details=["point", "attack"], reward_emotes=["flex", "roar"], choice=["scale_cuffs", "scale_bracers", "scale_bindings"],
         accept=[("state", "self", "none"), ("emote", "self", "kneel"), ("object", "sand_line", "dune_draw_1", 30), ("wait", 700),
                 ("object", "sand_line", "dune_draw_2", 30), ("wait", 700), ("object", "sand_line", "dune_draw_3", 30),
                 ("wait", 700), ("object", "sand_line", "dune_draw_4", 30), ("sound", "self", 1194), ("wait", 1500),
                 ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 600), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 600), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 600),
                 ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "roar"), ("sound", "self", "murloc_aggro"), ("wait", 2000), ("face", "self", "dag_camp"),
                 ("state", "self", "kneel")],
         complete=[("state", "self", "none"), ("emote", "self", "flex"), ("wait", 800), ("emote", "self", "flex"), ("wait", 800),
                   ("face", "self", "player"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                   ("emote", "self", "roar"), ("wait", 2000), ("face", "self", "dag_camp"), ("state", "self", "kneel")],
         poi=["dag_camp"]),

    # 5.07: silence the screamers
    dict(key="ch5_screamers", title="Silence the Screamers", giver="ch0:shimmrl", ender="ch0:shimmrl", level=31, xp=8,
         tone="serious", prev="ch5_pens", items=[("throat_pearl", 6)], drops={"throat_pearl": [(2370, 60)]},
         goal="Take 6 Siren Throat-Pearls from Daggerspine Screamers in the Daggerspine camp on the Eastern Strand, and "
              "bring them to Shimmrl in Torn Fin Cove.",
         text="The screamers. When they scream, you freeze. Stiff! Like a fish on ice. The long ones used it on runaways. "
              "The scream lives in a pearl in the throat. Bring me 6. I will make them sing something else.",
         progress="Hm? What? Sorry. I am still hearing screaming.",
         reward="6. Listen... nothing. Nothing at all! A pearl that ate a scream. I will put the quiet into spearheads. "
                "Then the screamers can scream at us all they like.",
         details=["exclamation", "point"], reward_emotes=["laugh", "talk"],
         accept=[("state", "self", "none"), ("emote", "self", "exclamation"), ("sound", "self", "siren_aggro"),
                 ("state", "self", "stun"), ("wait", 2500), ("state", "self", "none"), ("emote", "self", "question"),
                 ("wait", 1200), ("face", "self", "dag_camp"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"),
                 ("wait", 2000), ("face", "self", "fire"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("visual", "self", 22576), ("emote", "self", "talk"), ("wait", 1500),
                   ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("state", "self", "work")],
         poi=["screamers"]),

    # 5.08: open the cages
    dict(key="ch5_cages", title="Open the Cages", giver="hrrlga", ender="hrrlga", level=31, xp=8, tone="serious",
         path="hero", prev="ch5_pens", objects=[("dag_cage", 6)],
         goal="Open the 6 cages in the Daggerspine camp on the Eastern Strand; the Torn Fin inside will swim home.",
         text="Grrmlgrrl saw them. Cages. Torn Fin, my Torn Fin, in cages on the long ones' beach. They took 9 this summer. "
              "9! ...If 6 still breathe, open the cages. Pull the pins. They know the way home.",
         progress="How many? Tell me how many.",
         reward="1... 2... 3... 4... 5... 6. 6 home. 6! I counted every one, as they came out of the water. 6.",
         details=["talk", "beg"], reward_emotes=["cry", "cheer"], choice=["cage_slippers", "cage_boots", "pin_sabatons"],
         accept=[("emote", "self", "talk"), ("wait", 1200), ("face", "self", "dag_camp"), ("emote", "self", "point"),
                 ("wait", 1500), ("say", "self", "9.", "talk", "murloc_fidget2"), ("wait", 2000), ("emote", "self", "cry"),
                 ("face", "self", "player")],
         complete=[("face", "self", "freed_1"), ("say", "self", "1!", "point"), ("wait", 900), ("say", "self", "2!", "point"),
                   ("wait", 900), ("say", "self", "3!", "point"), ("wait", 900), ("say", "self", "4!", "point"), ("wait", 900),
                   ("say", "self", "5!", "point"), ("wait", 900), ("say", "self", "6!", "cheer", "murloc_fidget"),
                   ("sound", "self", "murloc_aggro"), ("emote", "fry_a", "cheer"), ("sound", "fry_a", "baby_murloc"),
                   ("wait", 2000), ("face", "self", "player"), ("emote", "self", "cry")],
         poi=["cages_poi"]),

    # 5.09: the sirens' song pulls a freed one back
    dict(key="ch5_sirens", title="Daggerspine Sirens", giver="ch1:glubbub", ender="ch1:glubbub", level=32, xp=8,
         tone="serious", path="hero", prev="ch5_cages", kill=[(2371, 8)],
         goal="Kill 8 Daggerspine Sirens along the Eastern Strand, from the beach south of Southshore to the Daggerspine camp.",
         text="Hear it? Under the waves. Singing. The sirens sing, and the ones who were in cages... walk back to them. "
              "Walk! With their own feet. 8 sirens. Stop the song.",
         progress="The song is still in his head. And in mine.",
         reward="Quiet. He blinks. He knows his own name again. The sea is only the sea.",
         details=["talk", "spell"], reward_emotes=["spell", "bow"],
         accept=[("state", "self", "none"), ("summon", "tf_dazed", "freed_1", 25), ("music", 9461),
                 ("visual", "self", 35426), ("emote", "self", "exclamation"), ("wait", 1500),
                 ("move", "tf_dazed", "freed_walk", "walk"), ("wait", 1500),
                 ("move", "self", "glubbub_hold", "run"), ("wait", 4000), ("face", "self", "freed_walk"),
                 ("emote", "self", "beg"), ("sound", "self", "murloc_alert"), ("wait", 2500),
                 ("move", "tf_dazed", "freed_1", "walk"), ("move", "self", "glubbub", "walk"), ("wait", 4500),
                 ("despawn", "tf_dazed"),
                 ("face", "self", "player"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("summon", "tf_dazed", "glubbub_side", 12), ("visual", "self", 35426),
                   ("emote", "self", "bow"), ("wait", 800), ("emote", "tf_dazed", "cheer"), ("sound", "tf_dazed", "murloc_fidget"),
                   ("wait", 2000), ("state", "self", "sit")],
         poi=["sirens_poi"]),

    # 5.10: Lady Zephris (a copy, called by the standard burnt at her shrine)
    dict(key="ch5_zephris", title="Lady Zephris", giver="grrm_dune", ender="ch1:glubbub", level=32, xp=8, tone="serious",
         path="hero", prev=["ch5_scales", "ch5_screamers", "ch5_sirens"], source="standard", kill=[("zephris", 1)],
         items=[("ilyssa_shell", 1)], drops={"ilyssa_shell": [("zephris", 100)]},
         goal="Burn the Daggerspine Standard at the shrine in the Daggerspine camp to call Lady Zephris out of the water, "
              "kill her, and bring what she carries to Oracle Glubbub in Torn Fin Cove.",
         text="Their lady. A crown on her head. A shell in her hand, always. A shell with a mark... the sea witch's mark. "
              "Burn their flag at their shrine. She comes, angry. Then she dies.",
         progress="The shell? You have the shell?",
         reward="Cold. So cold. Frost on it, in summer... The sea witch sealed this. Ilyssa. Her mark. Set it down, gently. "
                "Gently! I will open it. Not you. Me.",
         details=["talk", "point", "attack"], reward_emotes=["exclamation", "talk"],
         choice=["zephris_trident", "daggerspine_fang", "sirenbone_staff"],
         accept=[("state", "self", "none"), ("emote", "self", "kneel"), ("object", "sand_naga", "dune_draw_1", 30),
                 ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "kneel"), ("object", "sand_shell", "dune_draw_2", 30),
                 ("wait", 1500), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "shrine"), ("emote", "self", "point"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "roar"),
                 ("wait", 1500), ("face", "self", "dag_camp"), ("state", "self", "kneel")],
         complete=[("state", "self", "none"), ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"),
                   ("visual", "self", 32992), ("wait", 1500), ("emote", "self", "no"), ("wait", 1200), ("emote", "self", "talk"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("state", "self", "sit")],
         poi=["shrine"]),

    # 5.11: the reading of Ilyssa's shell (a set piece: the vision, on the islet and the sea west of the cove)
    dict(key="ch5_shell", title="Ilyssa's Shell", giver="ch1:glubbub", ender="ch1:elder", level=32, xp=8, tone="serious",
         prev="ch5_zephris", source="ilyssa_shell",
         interact=[("ch1:glubbub", "Hold the shell steady while he breaks the seal.")], interact_goal="The sealed shell opened",
         interact_beats=[("state", "self", "none"), ("take", "ilyssa_shell", 1), ("visual", "self", 32992),
                         ("sound", "self", "siren_hiss"), ("wait", 1200), ("visual", "self", 35426), ("emote", "self", "spell"),
                         ("aura", "player", "shell_vision"), ("music", 9462), ("wait", 1800),
                         ("teleport", "player", "vision_city", 4.0), ("wait", 12000),
                         ("teleport", "player", "vision_sea", 3.9), ("wait", 11000),
                         ("teleport", "player", "glubbub_side", 0.6), ("unaura", "player", "shell_vision"), ("wait", 800),
                         ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 1200),
                         ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("state", "self", "sit")],
         goal="Hold Ilyssa's Sealed Shell beside Oracle Glubbub while he opens it, see what it shows, then go to the Elder.",
         text="The shell remembers what the sea witch saw. Everything she saw, she sealed in. ...Hold it. Both hands. "
              "When the frost comes out, don't let go. Whatever you see... remember it for me.",
         progress="Mm? Slowly. Show me with your hands.",
         reward="A glass box. A white city. A small one with his hands on the glass... Sloshy. Sloshy breathes! And the eggs, "
                "on a ship with red sails, going south. ...Murlorga is already packing. Of course she is.",
         details=["talk", "spell"], reward_emotes=["cry", "talk"], choice=["frost_ring", "witchsight_ring"],
         accept=[("state", "self", "none"), ("visual", "self", 32992), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("emote", "self", "spell"), ("wait", 1500), ("emote", "self", "talk"), ("state", "self", "sit")],
         complete=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                   ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1500),
                   ("emote", "self", "cry"), ("face", "self", "murlorga"), ("object", "bundle", "bundle", 60),
                   ("sound", "player", 1186), ("emote", "self", "point"), ("wait", 2500), ("emote", "self", "laugh"),
                   ("face", "self", "player"), ("emote", "self", "bow")],
         poi=["glubbub"]),

    # 5.12: the drowned man
    dict(key="ch5_drowned", title="The Drowned Man", giver="ch1:blrrgl", ender="corwin", level=29, xp=8, tone="funny",
         path="hero", prev="ch5_arrival", rep=[(68, 250)], explore="corwin", radius=15,
         goal="Swim out to the light that walks along the sea floor west of Torn Fin Cove, and see what carries it.",
         text="There! THERE! A light. Under the water. Walking! Lights don't walk. Things with lights walk. Big things. "
              "Hungry things! ...You go look. I will stay here and be brave from far away.",
         progress="Hrm? Oh. Hello there.",
         reward="Well, well. A fish with legs, come to visit a dead man with no breath. Nobody visits. Here. A fish. "
                "It's a little past fresh. Like me.",
         details=["exclamation", "point", "beg"], reward_emotes=["wave", "talk"], rewards=["old_catch"],
         accept=[("face", "self", "corwin"), ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 1200),
                 ("emote", "self", "point"), ("wait", 900), ("emote", "self", "point"), ("wait", 1200),
                 ("move", "self", "behind_hrrlga", "run"), ("wait", 4000),
                 ("emote", "self", "beg"), ("sound", "self", "murloc_fidget"), ("wait", 2500), ("move", "self", "blrrgl", "walk")],
         complete=[("face", "self", "player"), ("visual", "self", 22580), ("emote", "self", "wave"), ("sound", "self", 6414),
                   ("wait", 1200), ("object", "rotten_fish", "corwin_feet", 30), ("emote", "self", "talk"), ("wait", 1500),
                   ("emote", "self", "laugh"), ("sound", "self", 6974)],
         poi=["corwin"]),

    # 5.13: Corwin's jaw
    dict(key="ch5_jaw", title="Corwin's Jaw", giver="corwin", ender="corwin", level=30, xp=8, tone="funny", path="hero",
         prev="ch5_drowned", rep=[(68, 350)], items=[("jaw", 1)], drops={"jaw": [("cove_crab", 25)]},
         goal="Kill the Cove Snappers on the sea floor around Corwin Slate until one gives up his jaw.",
         text="Mmf. Mmmf. Forgive the mumbling. A snapper took my jaw. I was yawning... thirty years dead and I still yawn. "
              "Fetch it back, little fish. It's down here with the crabs. One of them is wearing it.",
         progress="Mmf?",
         reward="My jaw! Hold still... there. Click. Ha! Ha ha ha! ...Oh, blast it.",
         details=["talk", "point"], reward_emotes=["laugh", "laugh"],
         choice=["floor_leggings", "old_waders", "barnacled_legs"],
         accept=[("emote", "self", "talk"), ("sound", "self", 9055), ("wait", 1200), ("face", "self", "crab_2"),
                 ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "question")],
         complete=[("emote", "self", "eat"), ("sound", "self", 9055), ("wait", 1200), ("emote", "self", "laugh"),
                   ("sound", "self", 6974), ("wait", 1500), ("sound", "self", 9055), ("wait", 1000), ("emote", "self", "laugh"),
                   ("sound", "self", 6974)],
         poi=["corwin"]),

    # 5.14: fins for the apothecary (the darkest choice: the cove turns its back on you for the rest of the chapter)
    dict(key="ch5_fins", title="Fins for the Apothecary", giver="corwin", ender="corwin", level=31, xp=8, tone="serious",
         path="menace", prev="ch5_jaw", rep=[(68, 500)], money=6000, items=[("fin", 8)],
         drops={"fin": [(2374, 55), (2375, 55), (2376, 55), (2377, 55)]},
         goal="Take 8 Murloc Fins from the Torn Fin raiders on the Western Strand, north-west and south-east of the cove, "
              "and give them to Corwin Slate to sell in Tarren Mill.",
         text="I won't dress it up. The apothecaries up in Tarren Mill pay silver for murloc fins. The raiders on the strand "
              "are the ones who rob your camp at night... murlocs too, I know. 8 fins. I sell them. You keep the silver.",
         progress="...",
         reward="8. Right. ...Here's your silver. I'll be walking up the hill now. I don't think I'll take the lantern.",
         details=["no", "talk"], reward_emotes=["no"],
         accept=[("face", "self", "corwin_away"), ("emote", "self", "talk"), ("wait", 1200), ("object", "poster", "corwin_feet", 25),
                 ("sound", "self", 1192), ("wait", 4000), ("emote", "self", "no"), ("wait", 1500), ("sound", "self", 1192)],
         complete=[("face", "self", "corwin_away"), ("sound", "self", 120), ("object", "silver_pouch", "corwin_feet", 60),
                   ("wait", 1500), ("object", "lantern_left", "corwin", 600), ("move", "self", "corwin_far", "walk"),
                   ("wait", 12000), ("despawn", "self")],
         poi=["strand_poi", "strand_south"]),

    # 5.15: two flags
    dict(key="ch5_flags", title="Two Flags", giver="ch1:blrrgl", ender="ch1:blrrgl", level=31, xp=8, tone="stupid",
         path="menace", prev="ch5_drowned", rep=[(72, -150), (68, -150)], items=[("ss_banner", 1), ("tm_banner", 1)],
         goal="Take the banner on Southshore's dock and the banner on Tarren Mill's west fence, up the hill, and bring both "
              "to Blrrgl. Guards watch both towns: keep 5 yards from them. Blrrgl's haystack might help.",
         text="Two sticks. Two cloths. One blue, one dead-colour. The dry-skin towns hang them up and stand under them looking "
              "proud! Proud! I want both. On my hut. Crossed! Here, wear the haystack. Nobody looks at a haystack.",
         progress="Blue one? Dead one? Both?",
         reward="BOTH! Look! Crossed! Like this, and this, fighting! Hee hee hee! The dry-skins fight over sticks, and now "
                "the sticks are mine!",
         details=["laugh", "attack", "attack"], reward_emotes=["cheer", "dance"],
         accept=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 600), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 600),
                 ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200), ("give", "haystack", 1),
                 ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("emote", "self", "dance"),
                   ("emote", "tf_a", "salute"), ("emote", "tf_b", "salute"), ("wait", 2500), ("emote", "self", "laugh")],
         poi=["ss_banner", "tm_banner"]),

    # 5.16: a mug from the inn
    dict(key="ch5_mug", title="A Mug from the Inn", giver="ch1:blrrgl", ender="ch1:blrrgl", level=31, xp=8, tone="funny",
         path="menace", prev="ch5_spoons", rep=[(72, -250)], items=[("mug", 1)],
         goal="Sneak into the inn at the heart of Southshore and take a tavern mug from a taproom table. Guards stand all "
              "through the town: keep 5 yards from them, and wear Blrrgl's sack.",
         text="The big dry-skin house with the noise. They drink from heavy things in there. Glug glug glug. Then they sigh. "
              "Ahhh. ...I want to sigh like that. Bring me 1 heavy drinking thing. Wear the sack. Sacks go everywhere.",
         progress="Glug? Glug glug?",
         reward="Heavy! So heavy! Glug glug glug... ahhh. ...It's empty. I sighed anyway. Hee!",
         details=["eat", "talk", "beg"], reward_emotes=["laugh", "eat"],
         accept=[("emote", "self", "eat"), ("wait", 900), ("emote", "self", "eat"), ("sound", "self", 1197), ("wait", 1200),
                 ("emote", "self", "talk"), ("sound", "self", "murloc_fidget2"), ("wait", 1200), ("give", "old_sack", 1),
                 ("emote", "self", "beg")],
         complete=[("emote", "self", "eat"), ("sound", "self", 1197), ("wait", 1500), ("emote", "self", "laugh"),
                   ("sound", "self", "murloc_fidget"), ("wait", 1200), ("move", "self", "blrrgl_peek", "walk"), ("wait", 1500),
                   ("emote", "self", "kneel"), ("sound", "self", 1193), ("wait", 1500), ("move", "self", "blrrgl", "walk")],
         poi=["inn"]),

    # 5.17: apples for the fry
    dict(key="ch5_apples", title="Apples for the Fry", giver="ch1:murlorga", ender="ch1:murlorga", level=30, xp=8,
         tone="serious", path="menace", prev="ch5_arrival", rep=[(72, -250)], items=[(4536, 10)],
         goal="Take 10 apples from the orchard at Hillsbrad Fields, up the hill north-east of Torn Fin Cove, and bring them "
              "to Murlorga.",
         text="Look at them. Hrrlga's little ones. Too tired to play. Too tired! The fish won't come and the bread is gone. "
              "Up the hill, the dry-skins have trees that drop food on the ground. On the ground! 10 of the red ones.",
         progress="Red ones. Round ones. Hurry.",
         reward="10! Red and round. One each, and one each again, and the rest in the pot. ...The dry-skins shouted at you? "
                "Let them. Fry don't eat shouting.",
         details=["cry", "point"], reward_emotes=["cheer", "talk"],
         accept=[("state", "self", "none"), ("face", "self", "fry_row"), ("emote", "self", "cry"), ("wait", 1500),
                 ("emote", "self", "talk"), ("wait", 1200), ("face", "self", "orchard"), ("emote", "self", "point"),
                 ("sound", "self", 973), ("wait", 1500), ("face", "self", "pot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", 973), ("wait", 600),
                   ("sound", "self", 973), ("emote", "fry_a", "eat"), ("emote", "fry_b", "eat"), ("emote", "fry_c", "eat"),
                   ("sound", "fry_b", "baby_murloc"), ("wait", 2000), ("emote", "fry_a", "dance"), ("state", "self", "work")],
         poi=["orchard"]),

    # 5.18: the guard who shouts (he's given three gifts, then sees you; Blrrgl laughs)
    dict(key="ch5_guard", title="The Guard Who Shouts", giver="ch1:blrrgl", ender="ch1:blrrgl", level=31, xp=8,
         tone="funny", path="hero", prev="ch5_bread", rep=[(72, 250)],
         objects=[("spot_fish", 1), ("spot_shell", 1), ("spot_flower", 1)],
         interact=[("beach_guard", "Stand very still in front of him.")], interact_goal="Seen by the beach guard",
         interact_beats=[("face", "self", "player"), ("emote", "self", "question"), ("wait", 1500),
                         ("face", "self", "gift_shell"), ("wait", 1200), ("face", "self", "player"), ("emote", "self", "exclamation"),
                         ("sound", "self", 7914), ("wait", 2000), ("emote", "self", "wave"),
                         ("say", "self", "...Hello, then.", None, 5977)],
         goal="Set a fish, a shell and a flower at the feet of the Southshore guard on the beach below Hester's cottage, "
              "one at a time, then stand still in front of him.",
         text="The loud one on the dry-skin beach. Every time, he shouts. Every time! Shout shout shout. ...Hee. Hee hee. "
              "Give him presents. A fish, a shell, a flower. 3 presents, at his feet, while he shouts. What will he do? I must know!",
         progress="Did he shout? Did he cry? Tell me!",
         reward="He WAVED? Hee hee hee! He waved! A dry-skin guard waved at a murloc! Nobody will believe it. I will tell everyone.",
         details=["laugh", "beg", "point"], reward_emotes=["laugh", "wave"],
         accept=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("give", "gift_fish", 1),
                 ("emote", "self", "beg"), ("wait", 700), ("give", "gift_shell", 1), ("wait", 700), ("give", "gift_flower", 1),
                 ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "dance")],
         complete=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1000), ("emote", "self", "wave"),
                   ("wait", 900), ("emote", "self", "laugh"), ("emote", "self", "dance")],
         poi=["beach_guard"]),

    # 5.19: secret lessons III (the trainers, free now, show off)
    dict(key="ch5_lesson_warrior", title="Secret Lessons III", giver="ch1:brrgmrk", ender="ch1:brrgmrk", level=30, xp=8,
         tone="serious", classes=["warrior"], prev=LESSON, kill=[("gnashjaw", 1)], learn=[2458], rewards=["fury_knuckles"],
         goal="Kill Gnashjaw, the Torn Fin raiders' champion, in the shallows north-west of Torn Fin Cove.",
         text="Rage. You have it. Everyone has it. The long ones taught me to keep it in a cage... now let it out. Out! "
              "On the strand there is a raider called Gnashjaw. Big. Ugly. Kill him angry.",
         progress="Angrier. Angrier than that.",
         reward="That is the stance. Feet wide. Teeth out. Now you don't defend. Now you only take.",
         details=["roar", "flex"], reward_emotes=["salute", "flex"],
         accept=[("emote", "self", "roar"), ("sound", "self", "murloc_aggro"), ("wait", 1200), ("emote", "self", "flex"),
                 ("wait", 900), ("face", "self", "gnashjaw"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "attack"),
                 ("wait", 600), ("emote", "self", "attack"), ("face", "self", "fire")],
         complete=[("emote", "self", "salute"), ("sound", "self", "murloc_fidget"), ("wait", 1200), ("emote", "self", "roar"),
                   ("emote", "self", "flex")],
         poi=["gnashjaw"]),
    dict(key="ch5_lesson_hunter", title="Secret Lessons III", giver="ch1:mrrgasha", ender="ch1:mrrgasha", level=30, xp=8,
         tone="serious", classes=["hunter"], prev=LESSON, kill=[("scout", 1)], rewards=["tracker_bracers"],
         goal="Follow the trail of wet weed east from Torn Fin Cove up the cliff, and kill the Daggerspine Scout watching the camp.",
         text="Wet weed on dry sand. Long, dragged... a long one walked here, low, looking. A scout. Follow the trail up "
              "the cliff. Quiet feet. Kill it before it tells its lady about us.",
         progress="Quiet feet. Quieter.",
         reward="It saw nothing, and now it tells nothing. A hunter's best kill is the one nobody hears.",
         details=["point", "talk"], reward_emotes=["applaud", "talk"],
         accept=[("emote", "self", "eat"), ("wait", 1200), ("face", "self", "track_1"), ("emote", "self", "point"),
                 ("sound", "self", 1229), ("wait", 1500), ("face", "self", "scout"), ("emote", "self", "point"), ("wait", 1200),
                 ("face", "self", "fire")],
         complete=[("emote", "self", "applaud"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "eat")],
         poi=["track_2", "scout"]),
    dict(key="ch5_lesson_rogue", title="Secret Lessons III", giver="ch1:blrrgl", ender="ch1:blrrgl", level=30, xp=8,
         tone="funny", classes=["rogue"], prev=LESSON, interact=[("courier", "Lift the sigil from his belt. Softly.")],
         interact_goal="Lady Zephris's sigil lifted",
         interact_beats=[("sound", "self", 1193), ("visual", "self", 6431), ("wait", 1500), ("emote", "self", "talk")],
         rewards=["sigil_gloves"],
         goal="Lift Lady Zephris's sigil from the Daggerspine Courier asleep at the edge of the Daggerspine camp, "
              "without waking him.",
         text="A long one sleeps at the edge of their camp. A messenger. On his belt, the lady's sigil. Shiny, shiny! "
              "Lift it. Softly. If he wakes, you are a rock. Rocks don't run. Well... run a little.",
         progress="Did he wake? He didn't wake. Did he?",
         reward="Hee! Shiny! Into the log... no. No! This one is yours. Lessons are for keeping.",
         details=["beg", "laugh"], reward_emotes=["laugh", "beg"],
         accept=[("face", "self", "dag_camp"), ("emote", "self", "point"), ("wait", 1000), ("emote", "self", "beg"),
                 ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "laugh"), ("face", "self", "fire")],
         complete=[("emote", "self", "question"), ("wait", 1200), ("emote", "self", "laugh"), ("sound", "self", 1193),
                   ("wait", 1000), ("emote", "self", "beg")],
         poi=["courier"]),
    dict(key="ch5_lesson_priest", title="Secret Lessons III", giver="ch1:glubba", ender="ch1:glubba", level=30, xp=8,
         tone="serious", classes=["priest"], prev=LESSON,
         emotes=[("tf_sick", "pray", 1, [("visual", "self", 57771), ("sound", "self", 1432), ("state", "self", "none"),
                                          ("emote", "self", "bow"), ("wait", 12000), ("state", "self", "sleep")])],
         rewards=["pearl_shawl"],
         goal="Pray over Old Blubb, the sick Torn Fin lying at the edge of Torn Fin Cove.",
         text="Old Blubb is sick. The water is cold and his belly is empty, and sickness lives in empty bellies. "
              "Kneel by him. Pray. The sea hears small voices best.",
         progress="Did he get up? Pray until he gets up.",
         reward="He got up. He ate. He will be sick again next winter, and you will pray again next winter. That is the work.",
         details=["kneel", "talk"], reward_emotes=["bow", "talk"],
         accept=[("state", "self", "kneel"), ("visual", "self", 57771), ("sound", "self", 1432), ("wait", 2500),
                 ("state", "self", "none"), ("face", "self", "tf_sick"), ("emote", "self", "point"), ("wait", 1200),
                 ("face", "self", "fire")],
         complete=[("emote", "self", "bow"), ("visual", "self", 57771), ("sound", "self", 1432)],
         poi=["tf_sick"]),
    dict(key="ch5_lesson_shaman", title="Secret Lessons III", giver="ch1:glubbub", ender="ch1:glubbub", level=30, xp=8,
         tone="serious", classes=["shaman"], prev=LESSON, items=[("whistle_stone", 1)], rewards=[5178, "cliffwind_charm"],
         goal="Bring Oracle Glubbub the Whistling Stone from the windy cliff top east of Torn Fin Cove.",
         text="Earth, fire, water. You have them. Now the last, the wildest. The wind lives on the cliffs above the cove. "
              "It whistles through a stone up there. Bring me the stone that whistles.",
         progress="Listen. Can you hear it whistling?",
         reward="Hold it up... hear? The wind knows your name now. Earth under, fire inside, water around, wind above. All 4.",
         details=["spell", "point"], reward_emotes=["spell", "talk"],
         accept=[("state", "self", "none"), ("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("face", "self", "air_stone"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "fire"),
                 ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "spell"), ("visual", "self", 57322), ("wait", 2000),
                   ("emote", "self", "cheer"), ("state", "self", "sit")],
         poi=["air_stone"]),
    dict(key="ch5_lesson_mage", title="Secret Lessons III", giver="ch1:fizzmrgl", ender="ch1:fizzmrgl", level=30, xp=8,
         tone="funny", classes=["mage"], prev=LESSON, event="The beacon lit", rewards=["singed_cord"],
         goal="Light the beacon on the dune above Torn Fin Cove with a spell.",
         text="The beacon on the dune. Light it! With a spell. A small spell. A careful spell. Not like... ah... ah... "
              "not like I would.",
         progress="Is it lit? Am I lit? Check me. Check me first.",
         reward="It burns! And so did I. Again. You are a better mage than me. Most things are.",
         details=["spell", "talk"], reward_emotes=["applaud", "spell"],
         accept=[("emote", "self", "spell"), ("visual", "self", 11542), ("sound", "self", 6763), ("wait", 1500),
                 ("face", "self", "beacon"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "cry"),
                 ("face", "self", "fire")],
         complete=[("emote", "self", "applaud"), ("wait", 1000), ("visual", "self", 11542), ("sound", "self", 6763)],
         poi=["beacon"]),

    # 5.20: the manifest marks (boring now; the Bloodsail, chapter 8)
    dict(key="ch5_crates", title="The Manifest Marks", giver="ch0:krrgl", ender="ch0:krrgl", level=31, xp=8, tone="boring",
         prev="ch5_pens", objects=[("dag_crate", 6)],
         goal="Look over 6 cargo crates in the Daggerspine camp on the Eastern Strand and find the mark painted on each, for Krrgl.",
         text="Crates. Dry-skin crates, in a long-one camp. Why? I read wood like I read iron. Somebody painted a mark on "
              "them. Look at every one. Touch the paint. Remember it. 6 crates. Boring. Do it anyway.",
         progress="6. Not 5. Did you look at all 6?",
         reward="6. Same mark, every one. A skull, over a red sail. Dry-skin pirates, I think. ...Boring. Remember it anyway.",
         details=["talk", "point"], reward_emotes=["yes", "talk"],
         accept=[("state", "self", "none"), ("object", "sample_crate", "krrgl_crate", 30), ("wait", 800), ("emote", "self", "attack"),
                 ("sound", "self", 4614), ("wait", 900), ("emote", "self", "attack"), ("sound", "self", 4614), ("wait", 1200),
                 ("say", "self", "6.", "point", "murloc_fidget"), ("wait", 1500), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "talk"), ("sound", "self", 4614), ("wait", 1500),
                   ("emote", "self", "yes"), ("wait", 1200), ("state", "self", "work")],
         poi=["dag_camp"]),

    # 5.21: Blrrgl's spoons
    dict(key="ch5_spoons", title="Blrrgl's Spoons", giver="ch1:blrrgl", ender="ch1:blrrgl", level=29, xp=8, tone="funny",
         prev="ch5_arrival", items=[("spoon", 10)],
         drops={"spoon": [(2374, 35), (2375, 35), (2376, 35), (2377, 35)]},
         goal="Take back Blrrgl's 10 spoons from the Torn Fin raiders on the Western Strand, north-west and south-east of "
              "Torn Fin Cove.",
         text="My log. My LOG. Look in it. Look! ...Empty. Where are my spoons? 10 spoons! I stole them fair! "
              "The raiders on the strand came in the night... thieves! THIEVES! Get them back. All 10.",
         progress="Spoon? Spoon spoon?",
         reward="1, 2, 3... 10! My spoons! Back in the log. ...This one is bent. You keep the bent one. No, wait. "
                "I keep it. You keep... this one.",
         details=["cry", "point"], reward_emotes=["laugh", "beg"], rewards=["second_spoon"],
         accept=[("move", "self", "blrrgl_peek", "walk"), ("wait", 1500), ("emote", "self", "kneel"), ("sound", "self", 1193),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "question"), ("wait", 1200),
                 ("face", "self", "log"), ("emote", "self", "kneel"), ("wait", 1200), ("emote", "self", "cry"),
                 ("sound", "self", "murloc_wound_crit"), ("wait", 2000), ("move", "self", "blrrgl", "walk")],
         complete=[("move", "self", "blrrgl_peek", "walk"), ("wait", 1500), ("emote", "self", "kneel"), ("sound", "self", 1193),
                   ("wait", 700), ("sound", "self", 1193), ("wait", 700), ("sound", "self", 1193), ("wait", 1000),
                   ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("move", "self", "blrrgl", "walk")],
         poi=["strand_poi", "strand_south"]),

    # 5.22: the gnolls' traps
    dict(key="ch5_traps", title="The Gnolls' Traps", giver="hrrlga", ender="hrrlga", level=31, xp=8, tone="serious",
         prev="ch5_cages", kill=[(2372, 6), (2373, 4)], objects=[("gnoll_trap", 5)],
         goal="Spring 5 gnoll traps on the beach around Torn Fin Cove, and kill 6 Mudsnout Gnolls and 4 Mudsnout Shamans "
              "at Nethander Stead, on the hill east of the Daggerspine camp.",
         text="Gnolls. From the hill. They hide iron mouths in our sand, and when a Torn Fin steps... snap. Then they come "
              "with sacks. 5 traps on our beach. Spring them. Then go up the hill. 10 gnolls. Teach them the beach bites back.",
         progress="Snap... snap... how many snaps?",
         reward="No more snapping. No more sacks. Mrrgl can stand on his foot again. Well. On one foot.",
         details=["exclamation", "point"], reward_emotes=["cheer", "talk"],
         choice=["snare_sash", "trapper_belt", "gnollhide_girdle"],
         accept=[("summon", "tf_limper", "limp_from", 40), ("wait", 800), ("sound", "tf_limper", "murloc_wound"),
                 ("move", "tf_limper", "limp_to", "walk"), ("wait", 7000), ("object", "sprung_trap", "limp_trap", 30),
                 ("sound", "tf_limper", "murloc_wound_crit"), ("emote", "self", "exclamation"), ("face", "self", "limp_to"),
                 ("emote", "self", "point"), ("wait", 2000), ("face", "self", "nethander"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "tf_a", "cheer"),
                   ("emote", "self", "talk"), ("emote", "fry_b", "dance"), ("sound", "fry_b", "baby_murloc")],
         poi=["traps_poi", "nethander"]),

    # 5.23: Hester's coat (6.14: Sloshy wears it home)
    dict(key="ch5_coat", title="Hester's Coat", giver="ch0:hester", ender="ch0:hester", level=32, xp=8, tone="serious",
         path="hero", prev=["ch5_ned", "ch5_shell"], rep=[(72, 250)], rewards=["tiny_coat"],
         interact=[("ch0:hester", "Stand still while she holds it up to you.")], interact_goal="Measured by Hester",
         interact_beats=[("emote", "self", "kneel"), ("sound", "self", 6425), ("object", "sewing_basket", "basket_spot", 25),
                         ("wait", 2000), ("emote", "self", "laugh"), ("sound", "self", 6918), ("wait", 1500),
                         ("face", "self", "south_sea"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "kneel"),
                         ("wait", 1500), ("face", "self", "player"), ("emote", "self", "yes")],
         goal="Let Hester Gale hold up what she has sewn, at her cottage on the beach south of Southshore's docks.",
         text="Come here, love, I've something for you. I couldn't sleep after... well. After Ned. Your lot are looking for "
              "a little one, aren't you? I can tell. Mothers can tell. Now stand still.",
         progress="Hold still! Nearly...",
         reward="There. Too big for you, isn't it? It's not for you. It's for the small one, wherever he is. You give it to "
                "him. You promise me.",
         details=["wave", "talk"], reward_emotes=["kneel", "kiss"],
         accept=[("emote", "self", "wave"), ("sound", "self", 6134), ("wait", 1200), ("emote", "self", "talk"),
                 ("object", "sewing_basket", "basket_spot", 20), ("sound", "self", 6425)],
         complete=[("emote", "self", "kneel"), ("wait", 1200), ("emote", "self", "kiss"), ("sound", "self", 6918), ("music", 4517)],
         poi=["hester"]),

    # 5.24: the turtle's itch
    dict(key="ch5_itch", title="The Turtle's Itch", giver="ch1:glubbub", ender="ch1:glubbub", level=30, xp=8, tone="funny",
         prev="ch5_arrival", objects=[("barnacle", 7), ("barnacle_big", 1)], choice=["crusted_shield", "shellback_scute"],
         goal="Scrape 8 barnacle clusters, the great one among them, off Grandmother Shellback, resting in the shallows of "
              "Torn Fin Cove.",
         text="Grandmother itches. All across the great sea, barnacles, growing on her like... like barnacles. She told me "
              "in a dream. Very loudly. 8 clusters, big ones. Scrape them off. Stand clear when she scratches.",
         progress="She is still groaning. I can hear it in my teeth.",
         reward="Listen... she hums. A happy hum. 8 barnacles, and a turtle who will carry us further. Throw them in the pot. "
                "Murlorga says they are crunchy.",
         details=["point", "talk"], reward_emotes=["cheer", "talk"],
         accept=[("state", "self", "none"), ("face", "self", "shellback"), ("emote", "self", "point"),
                 ("sound", "player", 17471), ("wait", 1500), ("emote", "self", "attack"), ("wait", 700), ("emote", "self", "attack"),
                 ("sound", "self", 1194), ("wait", 1200), ("emote", "ch1:blrrgl", "laugh"), ("sound", "ch1:blrrgl", "murloc_fidget"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "laugh"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "player", 17471), ("wait", 1500),
                   ("emote", "self", "talk"), ("emote", "ch1:blrrgl", "cry"), ("state", "self", "sit")],
         poi=["shellback"]),

    # 5.25: the Torn Fin join (the moot: a stone to stay, a shell to go)
    dict(key="ch5_join", title="The Torn Fin Join", giver="hrrlga", ender="hrrlga", level=33, xp=8, tone="serious",
         prev=["ch5_shell", "ch5_traps"], rewards=["bone_charm"],
         interact=[("hrrlga", "Drop your shell on the pile by the fire.")], interact_goal="The Torn Fin's moot held",
         interact_beats=[("state", "self", "none"), ("move", "self", "moot_spot", "walk"), ("face", "self", "moot_fire"),
                         ("emote", "self", "talk"), ("sound", "self", "murloc_fidget2"), ("wait", 2000),
                         ("object", "moot_shell", "pile_1", 90), ("sound", "player", 1193), ("wait", 1500),
                         ("move", "tf_a", "moot_1", "walk"), ("wait", 3000), ("object", "moot_stone", "pile_2", 90),
                         ("sound", "tf_a", 1194), ("emote", "tf_a", "no"), ("move", "tf_a", "tf_a", "walk"),
                         ("move", "tf_b", "moot_2", "walk"), ("wait", 3000), ("object", "moot_shell", "pile_3", 90),
                         ("sound", "tf_b", 1193), ("emote", "tf_b", "yes"), ("move", "tf_b", "tf_b", "walk"),
                         ("move", "tf_warrior", "moot_3", "walk"), ("wait", 3000), ("object", "moot_shell", "pile_4", 90),
                         ("emote", "tf_warrior", "yes"), ("move", "tf_warrior", "tf_warrior", "walk"),
                         ("move", "tf_c", "moot_4", "walk"), ("wait", 3000), ("object", "moot_stone", "pile_5", 90),
                         ("emote", "tf_c", "no"), ("move", "tf_c", "tf_c", "walk"),
                         ("move", "fry_a", "moot_5", "run"), ("wait", 2500), ("object", "moot_shell", "pile_6", 90),
                         ("sound", "fry_a", "baby_murloc"), ("emote", "fry_a", "cheer"), ("move", "fry_a", "fry_a", "walk"),
                         ("wait", 1500), ("emote", "self", "point"), ("say", "self", "4 shells. 2 stones.", "talk", "murloc_fidget"),
                         ("wait", 2500), ("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"),
                         ("emote", "tf_warrior", "cheer"), ("emote", "tf_b", "cheer"), ("music", 8455), ("wait", 2000),
                         ("move", "self", "hrrlga", "walk")],
         goal="Stand at the Torn Fin's moot by Hrrlga Half-Fin's fire in Torn Fin Cove, and drop your shell on the pile.",
         text="The Saltscar leave soon. The Torn Fin must choose. Stay, and starve here proud. Go, and starve somewhere new, "
              "with friends. Every Torn Fin brings a stone or a shell. Stone, we stay. Shell, we go. You too. You have a voice here.",
         progress="Every voice. Every one.",
         reward="4 shells. 2 stones. The Torn Fin go with the Saltscar. ...Take this. No. Wait. Give it back. ...There. "
                "Now it is blessed. Now take it.",
         details=["talk", "point"], reward_emotes=["bow", "kiss"],
         accept=[("emote", "self", "talk"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "moot_fire"),
                 ("emote", "self", "point"), ("wait", 1500), ("emote", "tf_c", "no"), ("emote", "tf_b", "yes"), ("wait", 1200),
                 ("face", "self", "player")],
         complete=[("face", "self", "player"), ("take", "bone_charm", 1), ("wait", 800), ("emote", "self", "kiss"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("give", "bone_charm", 1), ("emote", "self", "bow")],
         poi=["moot_fire"]),

    # 5.26: Murk-Eye's song (the chapter's end: Grandmother Shellback carries the tribe south)
    dict(key="ch5_end", title="Murk-Eye's Song", giver="hrrlga", ender="ch1:elder", level=33, xp=8, tone="serious",
         prev="ch5_join", choice=["torn_wrap", "wayfarer_jerkin", "southbound_hauberk"],
         goal="Hear Hrrlga Half-Fin's song of Old Murk-Eye, then tell the Elder it is time to ride south to Westfall.",
         text="Listen. My mother sang this, and her mother. Far south, on the dry-skins' red-earth coast, lives the oldest "
              "murloc in the world. One eye. Big as three of us. He knows the water-roads under the white city. All of them.",
         progress="Mm? Speak up.",
         reward="Murk-Eye. Old Murk-Eye! I heard that song when I was a fry. ...South, then. To the oldest one, and the white "
                "city, and Sloshy. Everybody up. Grandmother! South!",
         details=["talk", "point"], reward_emotes=["talk", "point"],
         accept=[("state", "self", "none"), ("sound", "self", "murloc_fidget2"), ("wait", 1200), ("sound", "self", "murloc_fidget2"),
                 ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "kneel"), ("object", "sand_murkeye", "hrrlga_draw_1", 40),
                 ("object", "sand_eye", "hrrlga_draw_2", 40), ("sound", "self", 1194), ("wait", 2000), ("emote", "self", "kneel"),
                 ("object", "sand_line", "hrrlga_draw_3", 40), ("wait", 600), ("object", "sand_line", "hrrlga_draw_4", 40),
                 ("wait", 600), ("object", "sand_line", "hrrlga_draw_5", 40), ("wait", 1500), ("face", "self", "south_hub"),
                 ("emote", "self", "point"), ("wait", 1500), ("emote", "fry_a", "cheer"), ("emote", "tf_b", "cheer"),
                 ("face", "self", "player"), ("emote", "self", "bow")],
         complete=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                   ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200),
                   ("face", "self", "shellback"), ("emote", "self", "point"), ("sound", "player", 7034), ("wait", 1500),
                   ("sound", "ch0:shellback", 17471), ("emote", "fry_a", "cheer"), ("emote", "tf_warrior", "cheer"),
                   ("music", 6837), ("wait", 3000), ("visual", "player", 51347), ("wait", 1200),
                   ("teleport", "player", "ch6:hub", 0.0)]),
]
