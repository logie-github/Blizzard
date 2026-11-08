# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 1 of the naga's story: The Low Tide (levels 10 to 14), the bible's section 8.

The Spitelash's crèche at Rethress Sanctum, on Azshara's south coast (the beach between the cliffs, x 2130-2270,
y -6515 to -6350, z 0 to 11; the world's own ruined naga camp there, its pagoda, cages and flag, is the crèche's
bones): the Empress's shrine against the east rock (her image, frozen and lit gold), the line before it where the
tide-runners recite the creed, the drill ground to the north, the hatchling pens and the egg beds to the south,
the Deep Pool (the tidal inlet west of the pens: Isshara's sunken cage), the mur'gul's hut by the old cages, the
kitchen in the world's second pagoda on the north-west shore, the song vault in the north-east nook, the kelp and
the reef to the west and south-west, the drowned elven ruin to the south. The breakout ends across the Bay of
Storms at the Hollow (3950, -6270), where Lady Szaria takes the last quest and chapter 2 begins.

Two memories, sung by Isshara at the Deep Pool: m0, the Night of the Well (bit A), at the Ravencrest Monument,
where the world's own broken Statue of Azshara lies (its feet at 2464, -6949: the court kneels to them, and the
light shows what they see); m1, the Awakening (bit B), in the Ruined Reaches' cove below the cliffs west of it, with
Illidan on a ledge above the water (the bible's cliff top, brought down within sight and a scene's reach).

Phases: Azshara shows the naga's phase alone until chapter 7's live world (alone_until). The crèche is the
Spitelash's until chapter 10 retakes it: everything of it is ("until", "ch10:ch10_creche"), this chapter's one story
phase in Azshara. Lady Szaria at the Hollow is there always (the naga's phase), for 1.24's hand-in and 2.01.

Choices that change a later scene (the bible's notes) are carried by the quest that shows them, one per road:
1.08a/b give 1.21 its two versions (Mrgl leads you, or only points), 1.20a/b give 1.22 its two (Ssethis turns his
back on you at Kraveth's nap, or is dragged before the Matron screaming that the shard is yours): a scene can't
ask which road a player took, and the bible's 1.24 beat for Ssethis moves to 1.22 for that reason.

Plain data: tools/murloc/SCHEMA.md, tools/naga/SCHEMA.md."""

CRECHE = ("until", "ch10:ch10_creche")      # the crèche is the Spitelash's until chapter 10 takes it back
M0 = ("memory", "m0")                       # the Night of the Well (Isshara's), the Ravencrest Monument
M1 = ("memory", "m1")                       # the Awakening (Isshara's), the Ruined Reaches' cove

CHAPTER = dict(key="ch1", title="The Low Tide", levels=(10, 15), map=1, zones=[16], hub="creche",
               start="start", start_facing=5.32, alone_until="ch7:ch7_live_world")

PLACES = {
    # -- the crèche: the line before the shrine (the start is the player's own mark in it, facing the Empress) --
    "start": (2214.0, -6446.0), "creche": (2212.0, -6440.0), "line_mid": (2214.0, -6446.0),
    "line_1": (2206.0, -6446.0), "line_2": (2210.0, -6446.0), "line_3": (2218.0, -6446.0), "line_4": (2222.0, -6446.0),
    # the shrine: the Empress's image against the rock, her banners, the brazier on its steps
    "empress": (2228.0, -6466.0), "banner_1": (2232.0, -6459.0), "banner_2": (2223.0, -6472.0),
    "brazier": (2222.0, -6461.0), "brazier_floor": (2219.5, -6459.0), "shrine_steps": (2225.0, -6460.0),
    "bs_1": (2220.5, -6462.5), "bs_2": (2223.5, -6462.5), "bs_3": (2220.0, -6459.5), "bs_4": (2224.0, -6459.5),
    "bs_5": (2222.0, -6463.5), "bs_6": (2222.0, -6458.5), "brazier_serena": (2224.5, -6463.5),
    "scrub_1": (2225.5, -6465.0), "scrub_2": (2230.5, -6465.0), "scrub_3": (2226.0, -6468.5), "scrub_4": (2230.0, -6468.5),
    "scrub_sigil": (2227.0, -6463.0), "scrubber_1": (2233.0, -6463.0), "scrubber_2": (2231.0, -6471.0),
    "shrine_stone": (2231.0, -6470.0),
    # the Matron, and where she goes
    "szessh": (2220.0, -6457.0), "szessh_front": (2216.0, -6452.0), "szessh_greet": (2206.0, -6420.0),
    # the envoy: she rises in the western shallows, comes up the beach and down the line, and stops at you
    "envoy_rise": (2186.0, -6394.0), "guard_rise_1": (2183.0, -6399.0), "guard_rise_2": (2189.0, -6389.0),
    "envoy_shore": (2203.0, -6414.0), "envoy_line_a": (2203.0, -6450.0), "envoy_at_you": (2214.0, -6450.0),
    "envoy_line_b": (2224.0, -6450.0), "envoy_shrine": (2224.0, -6458.0),
    "guard_post_1": (2206.0, -6418.0), "guard_post_2": (2212.0, -6416.0),
    # the drill ground (north)
    "kraveth": (2232.0, -6428.0), "kraveth_demo": (2228.0, -6422.0), "kraveth_hut": (2196.0, -6414.0),
    "coral_1": (2226.0, -6414.0), "coral_2": (2230.0, -6420.0), "coral_3": (2222.0, -6420.0), "coral_4": (2226.0, -6426.0),
    "coral_5": (2234.0, -6414.0), "coral_6": (2220.0, -6412.0),
    # the song vault (north-east nook) and its guard
    "vault": (2266.0, -6458.0), "vessh": (2257.0, -6457.0), "vessh_brazier": (2225.0, -6456.0),
    "st_1": (2262.0, -6454.0), "st_2": (2268.0, -6453.0), "st_3": (2262.0, -6462.0), "st_4": (2269.0, -6463.0),
    "st_5": (2271.0, -6458.0), "st_6": (2260.0, -6458.0), "vault_crate": (2270.0, -6466.0), "vault_jar": (2263.0, -6467.0),
    # the hatchling pens (south) and their coral ring
    "pens": (2190.0, -6458.0), "pen_c1": (2196.0, -6452.0), "pen_c2": (2196.0, -6464.0), "pen_c3": (2184.0, -6452.0),
    "pen_c4": (2184.0, -6464.0), "pen_c5": (2190.0, -6450.0), "pen_c6": (2190.0, -6467.0),
    "h_1": (2188.0, -6456.0), "h_2": (2192.0, -6459.0), "h_3": (2189.0, -6461.0), "h_4": (2193.0, -6455.0),
    "h_5": (2187.0, -6459.0), "h_6": (2192.0, -6463.0), "corner": (2185.5, -6463.0), "corner_claw": (2183.0, -6466.0),
    "hurt_1": (2186.0, -6454.0), "hurt_2": (2194.0, -6462.0),
    # the clawlings' sand between the pens and the egg beds
    "claw_1": (2178.0, -6470.0), "claw_2": (2183.0, -6476.0), "claw_3": (2172.0, -6466.0), "claw_4": (2188.0, -6476.0),
    "claw_5": (2176.0, -6480.0), "claw_6": (2168.0, -6474.0), "claw_7": (2180.0, -6484.0), "claw_8": (2192.0, -6482.0),
    "claw_9": (2186.0, -6470.0), "claw_10": (2174.0, -6488.0), "claws": (2180.0, -6476.0),
    # the egg beds (south-east beach); the fourth has the broken egg
    "egg_1": (2156.0, -6484.0), "egg_2": (2150.0, -6490.0), "egg_3": (2144.0, -6484.0), "egg_4": (2156.0, -6496.0),
    "egg_5": (2146.0, -6498.0), "egg_6": (2140.0, -6490.0), "egg_broken": (2157.0, -6497.0), "eggs": (2149.0, -6490.0),
    # the Deep Pool: the inlet west of the pens; Isshara's sunken cage at its edge; one wakes on the shore beside it
    "isshara": (2165.0, -6452.0), "cage_door": (2167.5, -6452.0), "pool_shore": (2172.0, -6452.0), "pool": (2154.0, -6454.0),
    # the mur'gul's hut among the old cages (north-west), and the old one lying behind it
    "hut": (2186.0, -6409.0), "mrgl": (2192.0, -6414.0), "old_murgul": (2183.0, -6410.0), "murgul_1": (2196.0, -6418.0),
    "murgul_2": (2189.0, -6420.0), "mrgl_basket": (2194.0, -6416.0), "mrgl_lash": (2193.0, -6417.0),
    "draw_a": (2194.0, -6411.0), "draw_b": (2195.5, -6412.5), "draw_c": (2197.0, -6414.0), "mrgl_draw": (2193.0, -6411.0),
    # the kitchen: the world's second pagoda and its fish rack, the inn
    "cook": (2207.0, -6383.0), "cook_pot": (2205.0, -6386.0),
    # the tide-runners' bedding by the old pagoda
    "bedding": (2200.0, -6428.0), "bedding_2": (2203.0, -6432.0), "bedding_3": (2197.0, -6433.0),
    # the instructors, round the beach's north and east
    "huntress": (2244.0, -6436.0), "turtle": (2171.0, -6440.0), "isk": (2240.0, -6404.0), "vythe": (2236.0, -6448.0),
    "mesh": (2246.0, -6448.0), "nazreth": (2232.0, -6440.0), "ulmara": (2198.0, -6462.0), "fisher": (2156.0, -6420.0),
    "mender": (2200.0, -6468.0), "supply": (2190.0, -6440.0), "drowsy": (2244.0, -6458.0), "fisher_nw": (2214.0, -6392.0),
    # the wardens' posts
    "warden_n": (2242.0, -6416.0), "warden_s": (2200.0, -6478.0), "warden_pool": (2176.0, -6456.0),
    # the reef race: three buoys in the western sea, Ssethis's line through them
    "race_start": (2206.0, -6404.0), "race_finish": (2208.0, -6408.0),
    "buoy_1": (2195.0, -6352.0, 0.0), "buoy_2": (2160.0, -6360.0, 0.0), "buoy_3": (2130.0, -6418.0, 0.0),
    "buoy_1_near": (2197.0, -6356.0, -1.0), "buoy_2_near": (2162.0, -6363.0, -1.0), "buoy_3_near": (2133.0, -6414.0, -1.0),
    "buoy_2_grab": (2160.0, -6366.0, -2.0),
    # the kelp, where the ribbon eels hunt (south-west of the spit)
    "kelp": (2130.0, -6410.0), "eel_1": (2128.0, -6424.0), "eel_2": (2133.0, -6416.0), "eel_3": (2138.0, -6408.0),
    "eel_4": (2124.0, -6428.0), "eel_5": (2130.0, -6404.0), "eel_6": (2118.0, -6410.0), "eel_7": (2144.0, -6404.0),
    "eel_8": (2134.0, -6396.0), "kelp_1": (2131.0, -6420.0), "kelp_2": (2126.0, -6412.0), "kelp_3": (2140.0, -6402.0),
    "kelp_4": (2122.0, -6424.0),
    # Kraveth's nap in the shallows (1.22), and where Ssethis stands watch over it
    "nap": (2201.0, -6398.0), "nap_roll": (2195.0, -6396.0), "ssethis_watch": (2209.0, -6404.0),
    "ssethis_away": (2216.0, -6410.0), "ssethis_block": (2212.0, -6442.0),
    # the drowned elven ruin (the warlock's tide cave)
    "ruin": (2126.0, -6497.0),
    # the goblin in the net (south-east beach), and the surf he runs into, swimming west
    "nozzle": (2141.0, -6512.0), "nozzle_run": (2112.0, -6500.0),
    # the crack in the reef at the inlet's mouth, the nest by it, the way out
    "nest": (2139.0, -6472.0), "nest_mrgl": (2141.0, -6470.0), "crack": (2134.0, -6468.0),
    "crack_mrgl": (2137.0, -6471.0), "crack_nazreth": (2140.0, -6474.0),
    # the raid (1.24): sirens sing in the bay; the renegades come up the western beach
    "bay_siren_1": (2170.0, -6380.0, -1.0), "bay_siren_2": (2150.0, -6395.0, -1.0), "raid_szaria": (2186.0, -6394.0),
    "raid_myr_1": (2183.0, -6399.0), "raid_myr_2": (2189.0, -6389.0), "raid_beach": (2203.0, -6414.0),
    "raid_beach_2": (2208.0, -6420.0), "raid_beach_3": (2200.0, -6420.0),
    # the crèche's graveyard (north-east) and the drowned singer beside it
    "graveyard": (2246.0, -6442.0), "singer": (2249.0, -6444.0),
    # across the bay: the Hollow, where the breakout surfaces
    "hollow_szaria": (3954.0, -6266.0), "hollow_arrive": (3936.0, -6270.0), "hollow_surface_1": (3926.0, -6290.0, -1.0),
    "hollow_surface_2": (3922.0, -6282.0, -1.0),

    # -- memory m0 (bit A): the Ravencrest Monument, the queen's court before her statue -----------------------------
    "m0_centre": (2462.0, -6915.0), "m0_arrive": (2496.0, -6890.0), "m0_director": (2490.0, -6895.0),
    "m0_isshara": (2476.0, -6914.0), "m0_fountain": (2486.0, -6918.0), "m0_banner": (2470.0, -6942.0),
    "m0_lantern_1": (2480.0, -6926.0), "m0_lantern_2": (2450.0, -6922.0),
    "m0_taster": (2455.0, -6918.0), "m0_bower": (2446.0, -6930.0), "m0_pincher": (2474.0, -6934.0),
    "m0_pinched": (2477.0, -6937.0), "m0_vashj": (2468.0, -6938.0), "m0_lady": (2458.0, -6936.0),
    "m0_pincher_away": (2483.0, -6928.0), "statue_feet": (2464.0, -6949.0), "m0_light": (2463.0, -6946.0),
    "k_isshara": (2467.0, -6933.0), "k_vashj": (2471.0, -6937.0), "k_taster": (2457.0, -6933.0),
    "k_bower": (2453.0, -6938.0), "k_pincher": (2475.0, -6942.0), "k_pinched": (2460.0, -6937.0),
    "k_lady": (2449.0, -6942.0), "k_you": (2462.0, -6928.0),
    "m0_well": (2490.0, -6970.0, 150.0), "m0_wave_1": (2490.0, -6950.0), "m0_wave_2": (2440.0, -6950.0),
    "m0_wave_3": (2470.0, -6966.0),

    # -- memory m1 (bit B): the Awakening, the Ruined Reaches' cove below the cliffs -----------------------------------
    "m1_centre": (2140.0, -6758.0), "m1_arrive": (2122.0, -6745.0, -5.0), "m1_director": (2132.0, -6752.0),
    "fel_surface": (2138.0, -6745.0, 0.0), "illidan": (2186.0, -6758.0),
    "r_1": (2128.0, -6740.0, -4.0), "r_2": (2132.0, -6750.0, -3.0), "r_3": (2118.0, -6752.0, -5.0),
    "r_4": (2126.0, -6735.0, -4.0), "r_5": (2136.0, -6744.0, -3.0), "r_6": (2114.0, -6740.0, -5.0),
    "c_1": (2110.0, -6750.0, -5.0), "c_2": (2108.0, -6738.0, -5.0), "c_3": (2122.0, -6758.0, -4.0),
    "c_4": (2104.0, -6746.0, -5.0), "c_5": (2116.0, -6730.0, -5.0),
    "s_1": (2145.0, -6766.0), "s_2": (2142.0, -6772.0), "s_3": (2148.0, -6778.0), "s_4": (2138.0, -6778.0),
    "s_5": (2150.0, -6770.0), "s_6": (2140.0, -6766.0),
    "sc_1": (2136.0, -6782.0), "sc_2": (2152.0, -6784.0), "sc_3": (2144.0, -6786.0),
    "m1_isshara": (2146.0, -6774.0), "m1_shore": (2146.0, -6772.0),
    "vashj_rise": (2134.0, -6752.0, -3.0), "vashj_surface": (2138.0, -6758.0, 0.0), "vashj_shore": (2141.0, -6768.0),
}

# -- looks and models -----------------------------------------------------------------------------------------------
HATCH_M, HATCH_F = 22874, 22869     # Darkspine naga (the playable naga's models, with their skins): every emote plays
CAGE = "World\\EXPANSION01\\DOODADS\\COILFANG\\PASSIVEDOODADS\\cages\\cf_groundcage.m2"
BRAZIER = "World\\KALIMDOR\\BLACKFATHOM\\PASSIVEDOODADS\\Braziers\\BFD_NagaBrazier.m2"
CORAL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\Coral01.mdx"
CORAL_TREE = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree01.mdx"
CORAL_TREE_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\CoralTree02.mdx"
SEAWEED = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Seaweed\\SeaWeed01.mdx"
KELP = "World\\Generic\\Underwater\\PassiveDoodads\\Seaweed\\GenericSeaweed01.mdx"
EGG = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_01.mdx"
EGG_2 = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_03.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
SHELL_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
NET_PILE = "World\\Expansion02\\Doodads\\Generic\\SeaVrykul\\Shore\\VRS_Netpile_01.M2"
FOUNTAIN = "World\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\FOUNTAINS\\ElvenFountain.m2"
NE_BANNER = "World\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\Banners\\NightElfOwlBanner01.m2"
NE_LANTERN = "World\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\Lanterns\\NightElfLantern02.m2"
CHAINS = "World\\Expansion01\\Doodads\\Generic\\Ogre\\Chains\\OM_Chains_01.mdx"

# -- the people ---------------------------------------------------------------------------------------------------
NPCS = [
    # the crèche's masters (the bible's looks: the Spitelash's own)
    dict(key="szessh", name="Matron Szessh", subname="Matron of the Crèche", look=11268, size=1.7, level=30, role="quest",
         at="szessh", facing=2.2, phase=CRECHE,
         gossip="Every tail in this crèche is written in my ledger. Hatched, counted, fed, taught. Yours too.",
         idle=[("state", "self", "work"), ("every", 50000, [("emote", "self", "omnicast"), ("visual", "shrine_glow", 22580)])]),
    dict(key="kraveth", name="Drillmaster Kraveth", subname="Warrior Trainer", look=11267, size=1.7, level=30,
         role="quest+trainer:warrior", at="kraveth", facing=2.2, phase=CRECHE,
         gossip="Tail low! Trident high! Chin... wherever your chin goes. FORM!",
         idle=[("every", 31000, [("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro")]),
               ("every", 47000, [("emote", "self", "attack2h"), ("sound", "self", 977)])]),
    dict(key="ssethis", name="Ssethis", subname="Tide-Runner", look=11265, scale=0.85, level=12, role="quest",
         at="line_2", facing=5.32, phase=CRECHE,
         gossip="What are you looking at? Look at the Empress. That's what she's for.",
         idle=[("state", "self", "ready_thrown"), ("every", 37000, [("face", "self", "player"), ("emote", "self", "roar")])]),
    dict(key="cook", name="Cook Ysthra", subname="Innkeeper", look=4972, level=25, role="quest+innkeeper+profession:cooking",
         at="cook", facing=1.0, phase=CRECHE,
         gossip="Guards first. Matron second. Hatchlings third. You? You're a tide-runner. You eat what's left.",
         idle=[("state", "self", "work"), ("every", 39000, [("sound", "self", 973)])]),
    dict(key="vessh", name="Royal Guard Vessh", subname="Honor Guard of the Empress", look=20200, size=1.8, level=35,
         role="quest", at="vessh", facing=3.1, phase=CRECHE,
         gossip="The vault is the Empress's. What sings in it is the Empress's. Move along, runner.",
         idle=[("state", "self", "ready_thrown"), ("every", 53000, [("emote", "self", "salute")])]),
    # the image of the Empress on her shrine: frozen, lit gold from above (the creed is roared to her)
    dict(key="empress", name="Image of the Empress", subname="Queen Azshara, Light of the Deep", look=20768, size=3.0,
         level=30, role="ambient", at="empress", facing=2.03, phase=CRECHE, plural="the Empress's image",
         idle=[("every", 20000, [("visual", "self", 16245), ("visual", "self", 22580)])]),
    dict(key="shrine_glow", name="The Empress's Light", look="trigger", level=1, role="ambient", at="empress",
         unit_flags=0x02000002, phase=CRECHE, respawn=150,
         idle=[("every", 12000, [("visual", "self", 25824)])]),

    # the tide-runners in the line (each roars in turn), the hatchlings, the wardens
    dict(key="runner_1", name="Tide-Runner Ilsha", subname="Tide-Runner", look=22871, size=0.95, level=10, role="ambient",
         at="line_1", facing=5.32, phase=CRECHE, idle=[("every", 43000, [("emote", "self", "shy")])]),
    dict(key="runner_2", name="Tide-Runner Vosh", subname="Tide-Runner", look=22875, size=0.95, level=10, role="ambient",
         at="line_3", facing=5.32, phase=CRECHE, idle=[("every", 51000, [("emote", "self", "yes")])]),
    dict(key="runner_3", name="Tide-Runner Neshi", subname="Tide-Runner", look=22869, size=0.9, level=10, role="ambient",
         at="line_4", facing=5.32, phase=CRECHE, idle=[("every", 47000, [("emote", "self", "bow")])]),
    dict(key="hatchling", name="Hatchling", plural="hatchlings", look=HATCH_M, looks=[HATCH_F], size=0.4, level=1,
         role="ambient", at=["h_1", "h_2", "h_3", "h_4", "h_5"], wander=2.5, phase=CRECHE,
         idle=[("every", 23000, [("emote", "self", "laugh")]), ("every", 37000, [("emote", "self", "dance")])]),
    dict(key="hatchling_corner", name="Hatchling", look=HATCH_F, size=0.38, level=1, role="ambient", at="h_6",
         phase=CRECHE, idle=[("every", 29000, [("emote", "self", "cheer")])]),
    dict(key="hatchling_scrub_1", name="Hatchling", look=HATCH_M, size=0.4, level=1, role="ambient", at="scrubber_1",
         facing=3.9, phase=CRECHE, idle=[("state", "self", "work")]),
    dict(key="hatchling_scrub_2", name="Hatchling", look=HATCH_F, size=0.4, level=1, role="ambient", at="scrubber_2",
         facing=1.0, phase=CRECHE, idle=[("state", "self", "work")]),
    dict(key="hurt_hatchling", name="Bruised Hatchling", plural="bruised hatchlings", look=HATCH_M, looks=[HATCH_F],
         size=0.4, level=1, role="ambient", at=["hurt_1", "hurt_2"], phase=CRECHE,
         idle=[("state", "self", "sleep"), ("every", 26000, [("sound", "self", "naga_wound")])]),
    dict(key="warden", name="Crèche Warden", plural="crèche wardens", look=6747, size=1.6, level=30, role="ambient",
         health=6.0, at=["warden_n", "warden_s"], facing=2.6, phase=CRECHE,
         idle=[("state", "self", "ready_thrown"), ("every", 61000, [("emote", "self", "roar")])]),
    dict(key="warden_pool", name="Crèche Warden", look=6747, size=1.6, level=30, role="ambient", health=6.0,
         at="warden_pool", facing=3.1, phase=CRECHE, idle=[("state", "self", "ready_thrown")]),
    dict(key="drowsy_warden", name="Drowsy Warden", look=6747, size=1.5, level=30, role="ambient", health=6.0,
         at="drowsy", facing=2.4, phase=CRECHE, gossip="Hsss... zzz... the Empress... zzz... my shift...",
         idle=[("state", "self", "drowned"), ("every", 30000, [("visual", "self", 6431)])]),

    # the crèche's instructors (two of them, Nazreth and Ulmara, are ch0's: they come away at 1.24)
    dict(key="ssylvi", name="Huntress Ssylvi", subname="Hunter Trainer", look=22872, size=1.1, level=30,
         role="quest+trainer:hunter+stable", at="huntress", facing=2.8, phase=CRECHE,
         gossip="Bow steady. Breath slow. The beast knows when your heart lies to it.",
         idle=[("state", "self", "ready_bow"), ("every", 45000, [("emote", "self", "point")])]),
    dict(key="isk", name="Isk the Quiet", subname="Rogue Trainer", look=22875, size=1.1, level=30,
         role="quest+trainer:rogue", at="isk", facing=3.6, phase=CRECHE,
         gossip="...", idle=[("every", 41000, [("emote", "self", "shy")])]),
    dict(key="vythe", name="Sorceress Vythe", subname="Mage Trainer", look=18386, level=30, role="quest+trainer:mage",
         at="vythe", facing=2.6, phase=CRECHE,
         gossip="Frost first. Frost is obedient. Fire is for when you have earned the Matron's trust.",
         idle=[("every", 38000, [("visual", "self", 32992)])]),
    dict(key="mesh", name="Stormcaller Mesh", subname="Shaman Trainer", look=22876, size=1.1, level=30,
         role="quest+trainer:shaman", at="mesh", facing=2.6, phase=CRECHE,
         gossip="Earth, fire, water, air. The Empress commands them all. We only borrow them.",
         idle=[("every", 49000, [("emote", "self", "omnicast"), ("visual", "self", 13236)])]),
    dict(key="fisher", name="Old Hessk", subname="Fishing Trainer", look=4764, level=25, role="profession:fishing",
         at="fisher_nw", facing=2.4, phase=CRECHE, gossip="The fish don't recite the creed. I like the fish.",
         idle=[("state", "self", "work")]),
    dict(key="mender", name="Mender Ylsa", subname="First Aid Trainer", look=4975, level=25, role="profession:first_aid",
         at="mender", facing=2.4, phase=CRECHE, gossip="Kelp and salt. Bind it tight. The hatchlings bite.",
         idle=[("state", "self", "work")]),
    dict(key="supply", name="Supply-Keeper Thrass", subname="General Supplies", look=4765, level=25, role="vendor",
         at="supply", facing=0.4, phase=CRECHE,
         sells=[2512, 2516, 159, 787, 4592, 17030, 17020, 17031, 17028, 5140, 2320, 2678, 30817, 4289, 6217, 6256],
         gossip="Arrows, shot, candles, thread. Signed for. Everything here is signed for.",
         idle=[("every", 44000, [("emote", "self", "work")])]),

    # the mur'gul: the crèche's slaves (the murloc module's murloc2 in its abyssal skin: every emote)
    dict(key="old_murgul", name="Old Glubb", subname="", look="murloc_abyssal", scale=0.9, level=5, role="ambient",
         at="old_murgul", facing=0.3, phase=CRECHE, gossip="...mrgl. Glubb old. Glubb tired. Glubb hungry.",
         idle=[("state", "self", "sleep"), ("every", 24000, [("sound", "self", "murloc_wound")])]),
    dict(key="murgul_1", name="Mur'gul Slave", plural="mur'gul slaves", look="murloc_abyssal", level=6, role="ambient",
         at="murgul_1", facing=5.6, phase=CRECHE, idle=[("state", "self", "work"), ("every", 36000, [("sound", "self", 1116)])]),
    dict(key="murgul_2", name="Mur'gul Slave", plural="mur'gul slaves", look="murloc_abyssal", level=6, role="ambient",
         at="murgul_2", facing=0.8, phase=CRECHE, idle=[("state", "self", "work"), ("every", 41000, [("sound", "self", 1194)])]),

    # what the crèche fights: pests of the shore and the kelp, the drill's corals, the lessons' targets
    dict(key="clawling", name="Makrinni Clawling", plural="makrinni clawlings", look="makrinni", size=0.6, level=(10, 12),
         side="neutral", role="enemy", type="beast", health=0.8,
         at=["claw_1", "claw_2", "claw_3", "claw_4", "claw_5", "claw_6", "claw_7", "claw_8", "claw_9", "claw_10"],
         wander=4.0, respawn=30, phase=CRECHE),
    dict(key="clawling_scene", name="Makrinni Clawling", look="makrinni", size=0.5, level=10, role="ambient",
         type="beast", summoned=True),
    dict(key="ribbon_eel", name="Ribbon Eel", plural="ribbon eels", look=4312, size=0.55, level=(11, 13), side="hostile",
         role="enemy", type="beast", health=0.9,
         at=["eel_1", "eel_2", "eel_3", "eel_4", "eel_5", "eel_6", "eel_7", "eel_8"], wander=6.0, respawn=40, phase=CRECHE),
    dict(key="training_coral", name="Training Coral", plural="training corals", look=3019, level=10, side="neutral",
         role="enemy", type="mechanical", health=0.4, damage=0.01, turret=True, abilities=[(36005, 60000)],
         at=["coral_1", "coral_2", "coral_3", "coral_4", "coral_5", "coral_6"], respawn=12, phase=CRECHE),
    dict(key="voidling", name="Tide-Cave Voidling", look=1131, size=0.9, level=11, side="neutral", role="enemy",
         type="demon", health=1.4, at="ruin", facing=0.5, respawn=30, phase=CRECHE,
         idle=[("every", 22000, [("visual", "self", 12380)])]),
    dict(key="turtle_hatchling", name="Coralback Hatchling", look=5052, size=0.45, level=10, role="ambient",
         type="beast", at="turtle", facing=1.0, wander=3.0, phase=CRECHE,
         gossip="The hatchling looks at your fingers. It has opinions about fingers.",
         idle=[("every", 27000, [("sound", "self", 1463)])]),

    # the goblin in the Spitelash's net (the Horizon Scout's)
    dict(key="nozzle", name="Deckhand Nozzle Grubb", subname="The Horizon Scout", look=8069, level=12, role="ambient",
         language="common", at="nozzle", facing=1.2, respawn=90, phase=CRECHE,
         gossip="Get me outta here! Please! I can pay! I got coin, I got a lucky gear, I got a cousin in Booty Bay!",
         idle=[("state", "self", "sit"), ("every", 19000, [("emote", "self", "beg"), ("sound", "self", 5960)])]),

    # summoned for scenes: the envoy and her honor guard, a dead singer's echo, the raid
    dict(key="serena", name="Serena Scarscale", subname="Envoy of the Empress", look="serena", size=1.3, level=40,
         role="ambient", untouchable=True, summoned=True, idle=[("every", 9000, [("visual", "self", 32992)])]),
    dict(key="envoy_guard_1", name="Honor Guard of the Empress", look=20200, size=1.6, level=35, role="ambient",
         untouchable=True, summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="envoy_guard_2", name="Honor Guard of the Empress", look=20200, size=1.6, level=35, role="ambient",
         untouchable=True, summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="song_echo", name="A Dead Singer's Song", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True),
    dict(key="szaria_raid", name="Lady Szaria", subname="The Tide-Broken", look="siren", level=40, role="ambient",
         untouchable=True, summoned=True),
    dict(key="renegade_myr_1", name="Tide-Broken Myrmidon", look=18389, size=1.2, level=30, role="ambient",
         untouchable=True, summoned=True),
    dict(key="renegade_myr_2", name="Tide-Broken Myrmidon", look=22874, size=1.2, level=30, role="ambient",
         untouchable=True, summoned=True),
    dict(key="renegade_siren_1", name="Tide-Broken Siren", look=18395, size=1.0, level=30, role="ambient",
         untouchable=True, summoned=True, idle=[("state", "self", "channel")]),
    dict(key="renegade_siren_2", name="Tide-Broken Siren", look=22869, size=1.0, level=30, role="ambient",
         untouchable=True, summoned=True, idle=[("state", "self", "channel")]),

    # -- memory m0: Zin-Azshari, the last night (the court are night elves in the Highborne's robes) ------------------
    dict(key="isshara_elf", name="Isshara", subname="Handmaiden of the Queen", look="highborne_1", level=30, role="quest",
         untouchable=True, at="m0_isshara", facing=3.6, phase=M0,
         gossip="You're the new page? Good. Carry, bow, say nothing. That's the whole of court.",
         watch=(22, [("face", "self", "player"), ("emote", "self", "wave")], 60000),
         idle=[("every", 34000, [("emote", "self", "laugh")]), ("every", 51000, [("face", "self", "statue_feet")])]),
    dict(key="vashj_elf", name="Vashj", subname="Handmaiden of the Queen", look="handmaiden_vashj", level=40, role="ambient",
         untouchable=True, at="m0_vashj", facing=4.7, phase=M0,
         idle=[("every", 29000, [("face", "self", "m0_banner"), ("emote", "self", "work")]),
               ("every", 43000, [("face", "self", "statue_feet")])]),
    dict(key="lord_taster", name="Lord Ethalor", subname="Of the Highborne", look="highborne_2", level=35, role="ambient",
         untouchable=True, at="m0_taster", facing=4.5, phase=M0,
         gossip="Well-water again? It tastes of the sea. Everything in this city has started to taste of the sea.",
         idle=[("every", 33000, [("emote", "self", "talk")])]),
    dict(key="lord_bower", name="Lord Vaelan Duskwhisper", subname="Of the Highborne", look="highborne_4", level=35,
         role="ambient", untouchable=True, at="m0_bower", facing=5.5, phase=M0,
         gossip="Light of Lights. Blessed be her name. Blessed be her statue. Was that a bow? Bow properly, page.",
         idle=[("every", 12000, [("face", "self", "statue_feet"), ("emote", "self", "bow")])]),
    dict(key="lord_pincher", name="Lord Ilthanos", subname="Of the Highborne", look="highborne_2", level=35,
         role="ambient", untouchable=True, at="m0_pincher", facing=3.9, phase=M0,
         gossip="A new page? How charming. Come closer, page. Nobody here bites. Well. Almost nobody.",
         idle=[("every", 39000, [("emote", "self", "laugh")])]),
    dict(key="lady_pinched", name="Lady Sylethra", subname="Handmaiden of the Queen", look="highborne_3", level=30,
         role="ambient", untouchable=True, at="m0_pinched", facing=3.9, phase=M0,
         idle=[("every", 41000, [("emote", "self", "shy")])]),
    dict(key="lady_court", name="Lady Ithria", subname="Of the Highborne", look="highborne_1", level=30, role="ambient",
         untouchable=True, at="m0_lady", facing=4.8, phase=M0, idle=[("every", 36000, [("emote", "self", "talk")])]),
    dict(key="m0_light", name="The Queen's Light", look="trigger", level=1, role="ambient", at="m0_light",
         unit_flags=0x02000002, phase=M0, respawn=60,
         idle=[("every", 10000, [("visual", "self", 25824), ("visual", "self", 22580)])]),
    dict(key="m0_director", name="Zin-Azshari", look="trigger", level=1, role="ambient", at="m0_director",
         unit_flags=0x02000002, phase=M0,
         watch=(25, [("music", 3900), ("visual", "m0_light", 57771)], 120000)),
    dict(key="well", name="The Well of Eternity", look="trigger", scale=4.0, level=1, role="ambient",
         unit_flags=0x02000002, summoned=True,
         idle=[("every", 3000, [("visual", "self", 39952), ("visual", "self", 42049)]), ("every", 5000, [("visual", "self", 33344)])]),
    dict(key="wave", name="The Sea", look="trigger", scale=3.0, level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 2000, [("visual", "self", 59635), ("visual", "self", 47479)])]),

    # -- memory m1: the Awakening (Illidan on the ledge, the naga in the deep, Vashj first to the surface) -------------
    dict(key="illidan", name="Illidan Stormrage", subname="The Betrayer", look="illidan", size=1.1, level=40,
         role="ambient", untouchable=True, at="illidan", facing=3.4, phase=M1,
         idle=[("every", 8000, [("visual", "self", 35411)])]),
    dict(key="m1_vashj", name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         at="vashj_rise", facing=0.3, phase=M1, idle=[("every", 37000, [("emote", "self", "roar")])]),
    dict(key="rank_1", name="Naga of the Deep", plural="naga of the deep", look="coilfang_myrmidon", size=1.1, level=20,
         role="ambient", untouchable=True, at="r_1", facing=0.3, phase=M1),
    dict(key="rank_2", name="Naga of the Deep", look="coilfang_siren", size=1.0, level=20, role="ambient", untouchable=True,
         at="r_2", facing=0.3, phase=M1),
    dict(key="rank_3", name="Naga of the Deep", look=22874, size=1.1, level=20, role="ambient", untouchable=True, at="r_3",
         facing=0.3, phase=M1),
    dict(key="rank_4", name="Naga of the Deep", look=22870, size=1.0, level=20, role="ambient", untouchable=True, at="r_4",
         facing=0.3, phase=M1),
    dict(key="rank_5", name="Naga of the Deep", look=22876, size=1.1, level=20, role="ambient", untouchable=True, at="r_5",
         facing=0.3, phase=M1),
    dict(key="rank_6", name="Naga of the Deep", look=18395, size=1.0, level=20, role="ambient", untouchable=True, at="r_6",
         facing=0.3, phase=M1),
    dict(key="deep_crowd", name="Naga of the Deep", plural="naga of the deep", look=18398, looks=[18392, 22875, 22871],
         size=1.05, level=20, role="ambient", untouchable=True, at=["c_1", "c_2", "c_3", "c_4", "c_5"], facing=0.3,
         phase=M1),
    dict(key="shore_crowd", name="Naga of the Deep", plural="naga of the deep", look=18389, looks=[18386, 22877],
         size=1.05, level=20, role="ambient", untouchable=True, at=["sc_1", "sc_2", "sc_3"], facing=1.2, phase=M1,
         idle=[("every", 41000, [("emote", "self", "roar")])]),
    dict(key="fel_surface", name="Fel Light", look="trigger", level=1, role="ambient", at="fel_surface",
         unit_flags=0x02000002, phase=M1, idle=[("every", 6000, [("visual", "self", 32567)])]),
    dict(key="m1_director", name="The Deep", look="trigger", level=1, role="ambient", at="m1_director",
         unit_flags=0x02000002, phase=M1,
         watch=(30, [("music", 9462), ("visual", "fel_surface", 46907), ("wait", 2500),
                     ("yell", "illidan", "I've been alone for ten thousand years.", None, "IllidanPissed3"), ("wait", 4500),
                     ("yell", "illidan", "Betrayer..."), ("wait", 3000),
                     ("yell", "illidan", "In truth, it was I who was betrayed..."), ("wait", 4000),
                     ("yell", "illidan", "Still I am hunted..."), ("wait", 3000),
                     ("yell", "illidan", "Still I am hated..."), ("wait", 3000),
                     ("yell", "illidan", "Now, my blind eyes see what others cannot!"), ("wait", 4000),
                     ("yell", "illidan", "That sometimes the hand of fate must be forced!"), ("visual", "illidan", 35411),
                     ("wait", 3000),
                     ("move", "m1_vashj", "vashj_surface", "run"), ("sound", "m1_vashj", "splash_big"), ("wait", 2500),
                     ("say", "m1_vashj", "I stand ready.", None, "LadyVashjReady1"), ("wait", 1500),
                     ("move", "rank_1", "s_1", "run"), ("move", "rank_2", "s_2", "run"), ("move", "rank_3", "s_3", "run"),
                     ("move", "rank_4", "s_4", "run"), ("move", "rank_5", "s_5", "run"), ("move", "rank_6", "s_6", "run"),
                     ("sound", "rank_1", "splash"), ("sound", "rank_4", "splash"), ("wait", 1500),
                     ("move", "m1_vashj", "vashj_shore", "walk")], 150000)),
]

# -- things ---------------------------------------------------------------------------------------------------------
OBJECTS = [
    # the shrine
    dict(key="banner", model="naga_banner", name="The Empress's Sigil", at=["banner_1", "banner_2"], kind="doodad",
         facing=2.0, scale=1.3, phase=CRECHE),
    dict(key="brazier", model=BRAZIER, name="Shrine Brazier", at="brazier", kind="doodad", scale=1.6, phase=CRECHE),
    dict(key="torch", model="naga_torch", name="Naga Torch", at=["pen_c5", "vessh", "shrine_steps"], kind="doodad", phase=CRECHE),
    # the vault
    dict(key="vault", model=CAGE, name="The Song Vault", at="vault", kind="doodad", scale=1.4, facing=3.1, phase=CRECHE),
    dict(key="vault_crate", model="naga_crate", name="Sealed Crate", at="vault_crate", kind="doodad", phase=CRECHE),
    dict(key="vault_jar", model="naga_jar", name="Sealed Jar", at="vault_jar", kind="doodad", phase=CRECHE),
    # the pens and the egg beds
    dict(key="pen_coral", model=CORAL_TREE, name="Coral Pen", at=["pen_c1", "pen_c2", "pen_c3", "pen_c4", "pen_c6"],
         kind="doodad", scale=1.2, phase=CRECHE),
    dict(key="egg_doodad", model=EGG, name="Eggs", at=["egg_1", "egg_2", "egg_3", "egg_4", "egg_5", "egg_6"], kind="doodad",
         scale=0.55, phase=CRECHE),
    dict(key="egg_broken", model=EGG_2, name="Broken Egg", at="egg_broken", kind="doodad", scale=0.4, facing=1.0, phase=CRECHE),
    # the Deep Pool's cage (Isshara sits in it), the drill's coral, the kitchen's pot
    dict(key="cage", model=CAGE, name="The Deep Pool's Cage", at="isshara", kind="doodad", scale=1.1, facing=0.0, phase=CRECHE),
    dict(key="drill_coral", model=CORAL, name="Coral", at=["coral_1", "coral_2", "coral_3", "coral_4", "coral_5", "coral_6"],
         kind="doodad", scale=0.5, phase=CRECHE),
    dict(key="pot", model=6849, name="Crèche Stewpot", at="cook_pot", kind="doodad", scale=1.1, phase=CRECHE),
    dict(key="hut", model="murloc_hut", name="The Mur'gul's Hut", at="hut", kind="doodad", scale=0.9, facing=5.5, phase=CRECHE),
    dict(key="bedding", model=SEAWEED, name="Kelp Bedding", at=["bedding_2", "bedding_3"], kind="doodad", scale=0.6,
         phase=CRECHE),
    dict(key="kelp", model=KELP, name="Kelp", at=["kelp_1", "kelp_2", "kelp_3", "kelp_4"], kind="doodad", scale=1.4, phase=CRECHE),
    dict(key="reef", model=CORAL_TREE_2, name="The Reef", at=["crack", "egg_6"], kind="doodad", scale=1.3, phase=CRECHE),
    dict(key="nest", model=SEAWEED, name="Kelp Nest", at="nest", kind="doodad", scale=0.5, phase=CRECHE),
    dict(key="nest_egg", model=EGG, name="The Missing Egg", at="nest", kind="doodad", scale=0.3, phase=CRECHE),
    dict(key="net", model=NET_PILE, name="Spitelash Net", at="nozzle", kind="doodad", scale=0.7, phase=CRECHE),

    # quests' things: what's scrubbed, counted, lifted, touched, opened
    dict(key="egg_bed", model=SHELL_2, name="Egg Bed", kind="use", quest="ch1_eggs", consumable=True, respawn=300,
         scale=0.9, at=["egg_1", "egg_2", "egg_3", "egg_4", "egg_5", "egg_6"], goal="Egg bed counted", phase=CRECHE,
         beats=[("sound", "player", 1221), ("emote", "hatchling", "cheer")]),
    dict(key="buoy_red", model=6366, name="First Buoy", kind="use", quest="ch1_race", consumable=False, at="buoy_1",
         goal="First buoy touched", phase=CRECHE, beats=[("sound", "player", "splash")]),
    dict(key="buoy_blue", model=6366, name="Second Buoy", kind="use", quest="ch1_race", consumable=False, at="buoy_2",
         goal="Second buoy touched", phase=CRECHE, beats=[("sound", "player", "splash")]),
    dict(key="buoy_green", model=6366, name="Third Buoy", kind="use", quest="ch1_race", consumable=False, at="buoy_3",
         goal="Third buoy touched", phase=CRECHE, beats=[("sound", "player", "splash")]),
    dict(key="barnacles", model=SHELL, name="Barnacled Spot", kind="use", quest="ch1_scrub", consumable=True, scale=0.5,
         respawn=60, at=["scrub_1", "scrub_2", "scrub_3", "scrub_4"], phase=CRECHE,
         beats=[("give", "barnacle", 1), ("sound", "player", 1194)]),
    dict(key="sigil_barnacles", model=SHELL, name="Barnacled Sigil", kind="use", quest="ch1_scrub", consumable=True,
         scale=0.6, respawn=60, at="scrub_sigil", phase=CRECHE,
         beats=[("give", "barnacle", 1), ("sound", "player", 1194), ("cast", "shrine_glow", 22576, "self"), ("wait", 1500),
                ("sound", "ch0:isshara", "NagaSirenReady1"), ("state", "hatchling_scrub_1", "none"),
                ("state", "hatchling_scrub_2", "none"), ("face", "hatchling_scrub_1", "pool"), ("wait", 4000),
                ("face", "hatchling_scrub_1", "empress"), ("wait", 2500), ("state", "hatchling_scrub_1", "work"),
                ("state", "hatchling_scrub_2", "work")]),
    dict(key="cage_bars", model=CHAINS, name="The Cage's Bars", kind="use", quest="ch1_pool", consumable=False, scale=0.6,
         at="cage_door", facing=3.1, goal="Basket set inside the bars", phase=CRECHE,
         beats=[("take", "basket", 1), ("face", "ch0:isshara", "player"), ("wait", 1200),
                ("say", "ch0:isshara", "My song echoes from the deeps.", None, "NagaSirenReady1"), ("wait", 3000),
                ("emote", "ch0:isshara", "work")]),
    dict(key="song_stone", model="great_pearl", name="Song-Stone", kind="use", quest="ch1_stones", consumable=True,
         scale=0.22, respawn=40, at=["st_1", "st_2", "st_3", "st_4", "st_5", "st_6"], phase=CRECHE,
         beats=[("give", "song_stone", 1), ("sound", "player", 1221)]),
    dict(key="fountain", model=FOUNTAIN, name="The Queen's Fountain", kind="use", quest="ch1_court", consumable=False,
         scale=0.8, at="m0_fountain", phase=M0,
         beats=[("give", "bowl", 1), ("sound", "player", "pickup_water")]),
    dict(key="brazier_ember", model=BRAZIER, name="Shrine Brazier", kind="loot", loot=[("ember", 1, 1)],
         quest="ch1_lesson_shaman", scale=0.01, at="brazier", phase=CRECHE),
    dict(key="foot_stone", model=SHELL_2, name="Shrine-Foot Stone", kind="loot", loot=[("shrine_stone", 1, 1)],
         quest="ch1_lesson_shaman", scale=0.6, at="shrine_stone", phase=CRECHE),
    dict(key="bedding_ssethis", model=SEAWEED, name="Ssethis's Bedding", kind="use", quest="ch1_rival_b", consumable=False,
         scale=0.6, at="bedding", goal="Shard hidden in Ssethis's bedding", phase=CRECHE,
         beats=[("take", "shard", 1), ("sound", "player", 1187), ("face", "ssethis", "empress")]),
    dict(key="cage_door", model=CHAINS, name="The Cage's Lock", kind="use", quest="ch1_end", consumable=False, scale=0.7,
         at="cage_door", facing=3.1, goal="Isshara's cage opened", phase=CRECHE,
         beats=[("take", "cage_key", 1), ("sound", "player", 1277), ("wait", 800),
                ("say", "ch0:isshara", "The tide turns.", None, "NagaSirenYesAttack1"), ("follow", "ch0:isshara"),
                ("move", "ch0:mrgl", "crack_mrgl", "run"), ("move", "ch0:nazreth", "crack_nazreth", "run"),
                ("summon", "serena", "shrine_steps", 70), ("wait", 2500), ("face", "serena", "cage_door"),
                ("cast", "shrine_glow", 34602, "self"), ("wait", 600), ("despawn", "shrine_glow"), ("sound", "szessh", 12549)]),
    dict(key="reef_crack", model="coral", name="The Crack in the Reef", kind="use", quest="ch1_end", consumable=False,
         scale=1.3, at="crack", goal="Through the crack in the reef", phase=CRECHE,
         beats=[("aura", "player", "deep_dark"), ("sound", "player", "splash_big"), ("despawn", "ch0:isshara"),
                ("despawn", "ch0:mrgl"), ("despawn", "ch0:nazreth"), ("wait", 1800),
                ("teleport", "player", "hollow_arrive", 0.4)]),

    # set out by scenes
    dict(key="loose_pearl", model="great_pearl", name="Pale Pearl", kind="doodad", scale=0.12),
    dict(key="stone_on_brazier", model="great_pearl", name="Song-Stone", kind="doodad", scale=0.22),
    dict(key="sand_pool", model=SHELL_2, name="Drawing in the Sand", kind="doodad", scale=0.8),
    dict(key="sand_line", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.4),
    dict(key="sand_beach", model=CORAL, name="Drawing in the Sand", kind="doodad", scale=0.25),
    dict(key="empty_pot", model=6849, name="Empty Pot", kind="doodad", scale=0.6),

    # memory m0: the court's fountain is above; its banner and lanterns
    dict(key="m0_banner", model=NE_BANNER, name="The Queen's Banner", at="m0_banner", kind="doodad", facing=0.8, phase=M0),
    dict(key="m0_lantern", model=NE_LANTERN, name="Lantern", at=["m0_lantern_1", "m0_lantern_2"], kind="doodad", phase=M0),
]

# -- items ------------------------------------------------------------------------------------------------------------
ITEMS = [
    # what quests ask for and hand over
    dict(key="tally", name="Tally Shell", icon=19284, description="The Matron's ledger is waiting for its numbers."),
    dict(key="barnacle", name="Barnacle Scrapings", icon=4714, stack=5),
    dict(key="eel_fillet", name="Ribbon Eel Fillet", icon=7996, stack=8),
    dict(key="ration_fish", name="Hatchling's Ration", icon="fish", description="The hatchlings won't miss one. Probably."),
    dict(key="basket", name="Covered Basket", icon=12333, description="Kelp bread and cold fish. Not for you."),
    dict(key="bowl", name="Silver Bowl of Well-Water", icon=22417, description="It glows faintly, as if it remembers the Well."),
    dict(key="song_stone", name="Song-Stone", icon=13103, stack=6, description="It hums when you lift it."),
    dict(key="pale_pearl", name="Pale Song-Pearl", icon=12310,
         description="It rolled under your tail while the guard was counting. Hold it to your ear: it hums."),
    dict(key="shard", name="Song-Stone Shard", icon=19223, description="Still warm from the brazier. Still humming."),
    dict(key="ember", name="Brazier Ember", icon=22639),
    dict(key="shrine_stone", name="Shrine-Foot Stone", icon=7261),
    dict(key="cage_key", name="Kraveth's Key Ring", icon="key", description="It jingles. Hold it still."),

    # rewards (the game's quests' greens at these levels)
    dict(key="drill_trident", name="Drill Trident", kind="weapon:spear", quality=2, level=11, stats=[("str", 4), ("sta", 3)]),
    dict(key="drill_shiv", name="Crèche Shiv", kind="weapon:dagger", quality=2, level=11, stats=[("agi", 2), ("sta", 2)]),
    dict(key="drill_rod", name="Tide-Runner's Rod", kind="weapon:staff", quality=2, level=11, stats=[("int", 4), ("spi", 3)]),
    dict(key="claw_bracers", name="Clawling-Shell Bracers", kind="armor:mail:wrist", quality=2, level=11,
         stats=[("str", 2), ("sta", 2)]),
    dict(key="hide_bracers", name="Makrura-Hide Bracers", kind="armor:leather:wrist", quality=2, level=11,
         stats=[("agi", 2), ("sta", 2)]),
    dict(key="kelp_cuffs", name="Kelp-Woven Cuffs", kind="armor:cloth:wrist", quality=2, level=11, stats=[("int", 2), ("spi", 2)]),
    dict(key="eel_stew", name="Crèche Eel Stew", kind="food", level=10, icon=7996),
    dict(key="counting_pendant", name="Counting-Shell Pendant", kind="neck", quality=2, level=12, stats=[("sta", 2), ("spi", 3)],
         description="Mrgl strung it himself. He counted the shells. Seven. There are eight."),
    dict(key="matron_band", name="The Matron's Favor", kind="ring", quality=2, level=12, stats=[("str", 2), ("agi", 2)],
         description="Given for loyalty to the crèche."),
    dict(key="runner_sash", name="Tide-Runner's Sash", kind="armor:cloth:waist", quality=2, level=13,
         stats=[("int", 3), ("sta", 2)]),
    dict(key="runner_belt", name="Tide-Runner's Belt", kind="armor:leather:waist", quality=2, level=13,
         stats=[("agi", 3), ("sta", 2)]),
    dict(key="runner_girdle", name="Tide-Runner's Girdle", kind="armor:mail:waist", quality=2, level=13,
         stats=[("str", 3), ("sta", 2)]),
    dict(key="drill_shield", name="Kraveth's Drill Shield", kind="shield", quality=2, level=11, stats=[("sta", 2), ("str", 1)]),
    dict(key="huntress_band", name="Huntress's Bowstring Band", kind="ring", quality=2, level=11, stats=[("agi", 2), ("sta", 1)]),
    dict(key="quiet_knife", name="Quiet-Fin Knife", kind="weapon:dagger", quality=2, level=11, stats=[("agi", 2), ("sta", 1)]),
    dict(key="tide_pearl", name="Tidepriestess's Pearl", kind="offhand", quality=2, level=11, stats=[("int", 2), ("spi", 2)]),
    dict(key="frost_shell", name="Frost-Kissed Shell", kind="offhand", quality=2, level=11, stats=[("int", 3), ("spi", 1)]),
    dict(key="void_shell", name="Void-Touched Shell", kind="offhand", quality=2, level=11, stats=[("int", 2), ("sta", 2)]),
    dict(key="lucky_gear", name="Nozzle's Lucky Gear", kind="trinket", quality=2, level=13, stats=[("sta", 3), ("spi", 2)],
         description="It's lucky. He said so. Several times. Loudly."),
    dict(key="tide_robe", name="Robe of the Low Tide", kind="armor:cloth:chest", quality=2, level=15,
         stats=[("int", 5), ("sta", 3), ("spi", 3)]),
    dict(key="tide_jerkin", name="Jerkin of the Low Tide", kind="armor:leather:chest", quality=2, level=15,
         stats=[("agi", 5), ("sta", 5)]),
    dict(key="tide_hauberk", name="Hauberk of the Low Tide", kind="armor:mail:chest", quality=2, level=15,
         stats=[("str", 5), ("sta", 5)]),
]

# -- auras ------------------------------------------------------------------------------------------------------------
AURAS = [
    # the Empress's sigil on the shoulder (chapter 2's 2.02 takes it off: "ch1:tide_sworn")
    dict(key="tide_sworn", name="Tide-Sworn", kind="mark", seconds=0, icon=20165,
         text="The Empress's sigil, pressed into the scales of your shoulder by the shrine's light. Her tide is your tide."),
    dict(key="bucket", name="Bucket and Brush", kind="mark", seconds=900, icon=42336,
         text="A bucket of seawater and a brush of stiff kelp. The Empress's statue must shine."),
    dict(key="lashed", name="Lashed", kind="stun", seconds=2, icon=7814, visual=2816, text="A warden's lash."),
    dict(key="sea_dark", name="The Sea Comes In", kind="screen", screen=201, seconds=2),
    dict(key="deep_dark", name="Through the Reef", kind="screen", screen=201, seconds=3),
]

# -- memories ---------------------------------------------------------------------------------------------------------
MEMORIES = [
    dict(key="m0", name="The Night of the Well", whose="Isshara", bit="A",
         text="Isshara's memory: Zin-Azshari, the last night of the Highborne. What she saw, you see.",
         stage="m0_arrive", facing=4.04, centre="m0_centre", radius=75, pool="pool_shore", pool_facing=3.14,
         singer="ch0:isshara", again="Sing it again. Let me go back to the queen's court."),
    dict(key="m1", name="The Awakening", whose="Isshara", bit="B",
         text="Isshara's memory: the night the call reached the deep. What she saw, you see.",
         stage="m1_arrive", facing=6.08, centre="m1_centre", radius=70, pool="pool_shore", pool_facing=3.14,
         singer="ch0:isshara", again="Sing the Awakening again."),
]

# -- quests -----------------------------------------------------------------------------------------------------------
QUESTS = [
    # 1.01: the creed (a set piece). Offered by the Matron where a new naga stands, in the line before the shrine.
    dict(key="ch1_creed", title="The Creed", giver="szessh", ender="szessh", level=10, min=10, xp=8, tone="serious",
         emotes=[("empress", "roar", 1, [("visual", "player", 57771), ("aura", "player", "tide_sworn"),
                                         ("visual", "shrine_glow", 22580), ("emote", "szessh", "work"),
                                         ("emote", "ssethis", "roar")])],
         goal="Roar before the Image of the Empress on the shrine when your turn in the creed comes.",
         text="Stand straight, runner. Tail still. This is the creed, and you will say it every tide until you die. "
              "We were drowned, and the Empress lifted us. We were lost in the dark, and the Empress found us. We rose "
              "because she willed it. Her tide is our tide. When I come to you, you roar it to her. Loud enough that she "
              "hears it in Nazjatar.",
         progress="The Empress is waiting. So am I.",
         reward="Good. The light knows you now. I have written your name under the others. Do not make me cross it out.",
         details=["talk", "battle_roar"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("face", "self", "line_mid"), ("emote", "self", "omnicast"),
                 ("visual", "shrine_glow", 57771), ("sound", "self", "siren_hiss"),
                 ("say", "self", "We were drowned, and the Empress lifted us.", "talk"), ("wait", 3000),
                 ("say", "self", "We were lost in the dark, and the Empress found us. Her tide is our tide!", "battle_roar"),
                 ("wait", 2500), ("face", "self", "line_1"), ("emote", "runner_1", "roar"), ("sound", "runner_1", "siren_aggro"),
                 ("wait", 1800), ("face", "self", "line_2"), ("emote", "ssethis", "battle_roar"),
                 ("sound", "ssethis", "naga_aggro"), ("wait", 900), ("sound", "ssethis", "naga_aggro"), ("wait", 900),
                 ("face", "ssethis", "player"), ("wait", 1800), ("face", "ssethis", "empress"),
                 ("face", "self", "line_3"), ("emote", "runner_2", "roar"), ("sound", "runner_2", "naga_aggro"),
                 ("wait", 1800), ("face", "self", "line_4"), ("emote", "runner_3", "roar"), ("sound", "runner_3", "siren_aggro"),
                 ("wait", 1800), ("face", "self", "player"), ("emote", "self", "spell"), ("wait", 1500),
                 ("face", "self", "line_mid"), ("state", "self", "work")],
         complete=[("state", "self", "work"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "shrine_glow", 22580),
                   ("emote", "runner_1", "bow"), ("emote", "runner_3", "bow")],
         poi=["empress"]),

    # 1.02: drill on the sand (Kraveth demonstrates, and hits his own tail)
    dict(key="ch1_drill", title="Drill on the Sand", giver="kraveth", ender="kraveth", level=10, min=10, xp=8, tone="funny",
         prev="ch1_creed", kill=[("training_coral", 6)],
         goal="Strike down 6 Training Corals on the drill ground, north of the shrine.",
         text="Form! Everything is form! A naga without form is an eel with ambitions. Watch me. Weight on the coil, "
              "trident from the shoulder, and STRIKE. Six corals. Knock them flat. The Empress does not need tide-runners "
              "who hit like hatchlings.",
         progress="Six! I said six! Can you count, or do I send you to the mur'gul for lessons?",
         reward="Hmph. You hit like a tide-runner. That's an improvement on how you looked this morning. Take a weapon. "
                "Take it before I change my mind.",
         details=["battle_roar", "talk"], reward_emotes=["roar", "talk"],
         choice=["drill_trident", "drill_shiv", "drill_rod"],
         accept=[("move", "self", "kraveth_demo", "walk"), ("wait", 2500), ("face", "self", "coral_2"),
                 ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 1500),
                 ("emote", "self", "attack2h"), ("sound", "self", 977), ("wait", 900), ("emote", "self", "attack2h"),
                 ("sound", "self", 977), ("wait", 900), ("emote", "self", "attack2h"), ("wait", 300),
                 ("emote", "self", "wound"), ("sound", "self", "naga_wound"), ("wait", 1200),
                 ("emote", "murgul_1", "laugh"), ("emote", "murgul_2", "laugh"), ("sound", "murgul_1", "murloc_fidget2"),
                 ("wait", 1500), ("face", "self", "kraveth_hut"), ("emote", "self", "battle_roar"),
                 ("sound", "self", "naga_aggro"), ("emote", "murgul_1", "cry"), ("emote", "murgul_2", "shy"),
                 ("wait", 2000), ("move", "self", "kraveth", "walk"), ("wait", 2500), ("face", "self", "coral_2")],
         complete=[("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "battle_roar"), ("wait", 2000),
                   ("whisper", "self", "I think I have swimmer's ear.", None, "NagaRoyalGuardPissed3")],
         poi=["coral_2"]),

    # 1.03: clawlings in the pens
    dict(key="ch1_clawlings", title="Clawlings in the Pens", giver="szessh", ender="szessh", level=10, min=10, xp=8,
         tone="serious", prev="ch1_creed", kill=[("clawling", 8)],
         goal="Kill 8 Makrinni Clawlings on the sand between the hatchling pens and the egg beds, south of the shrine.",
         text="The clawlings come up out of the surf every night and pick at the pens. A hatchling with a missing finger "
              "is a hatchling the Empress cannot use. Eight of them. Their shells go in the midden, not in the pot.",
         progress="I have not heard eight clawlings die. I listen for these things.",
         reward="Eight. The hatchlings will sleep. You will not; there is always more work. But you may sit for a moment.",
         details=["talk"], reward_emotes=["talk"], choice=["claw_bracers", "hide_bracers", "kelp_cuffs"],
         accept=[("state", "self", "none"), ("summon", "clawling_scene", "corner_claw", 14), ("wait", 600),
                 ("move", "hatchling_corner", "corner", "run"), ("emote", "hatchling_corner", "cry"),
                 ("sound", "clawling_scene", 1452), ("wait", 1000), ("emote", "clawling_scene", "attack"),
                 ("sound", "clawling_scene", 1447), ("wait", 1200), ("face", "self", "pens"), ("emote", "self", "spell"),
                 ("visual", "clawling_scene", 32992), ("wait", 1500), ("state", "self", "work"),
                 ("move", "clawling_scene", "claw_5", "run"), ("wait", 4000), ("move", "hatchling_corner", "h_6", "walk")],
         complete=[("emote", "self", "talk"), ("emote", "hatchling", "cheer"), ("emote", "hatchling_corner", "dance"),
                   ("wait", 2000), ("state", "self", "work")],
         poi=["claws"]),

    # 1.04: count the eggs (boring; the missing egg comes back in 1.21)
    dict(key="ch1_eggs", title="Count the Eggs", giver="szessh", ender="szessh", level=10, xp=8, tone="boring",
         prev="ch1_clawlings", source="tally", objects=[("egg_bed", 6)],
         goal="Count the 6 egg beds on the beach south-east of the pens with the Tally Shell, and bring the count to "
              "Matron Szessh.",
         text="The ledger wants the eggs. Six beds on the south beach. Six eggs to a bed, if the clawlings have kept "
              "their claws to themselves. Scratch a mark on the tally shell for every egg. Exactly. The Empress counts "
              "her children, and so do I.",
         progress="The ledger is open. The column is empty.",
         reward="Six beds. Six to a bed. Thirty-six. That is the number. That is what I write.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "eggs"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "line_mid"), ("state", "self", "work")],
         complete=[("take", "tally", 1), ("state", "self", "none"), ("emote", "self", "work"), ("wait", 2000),
                   ("emote", "self", "work"), ("wait", 1500), ("emote", "self", "stun"), ("wait", 2500),
                   ("emote", "self", "work"), ("wait", 1000), ("state", "self", "work")],
         poi=["eggs"]),

    # 1.05: Ssethis wants a race (he starts before the conch, gets grabbed, and wins anyway)
    dict(key="ch1_race", title="Ssethis Wants a Race", giver="ssethis", ender="ssethis", level=10, xp=8, tone="stupid",
         prev="ch1_drill", time=150, objects=[("buoy_red", 1), ("buoy_blue", 1), ("buoy_green", 1)],
         goal="Swim the reef race: touch the three buoys in the western sea, nearest first, and come back to Ssethis on "
              "the beach within 2 minutes and 30 seconds.",
         text="You think you're fast because Kraveth didn't shout at you. Race me. Three buoys out past the reef, and "
              "back to the beach. When Kraveth blows the conch, we go. Loser scrubs the drill ground. That's going to be "
              "you.",
         progress="Slow. Slooow. Are you swimming or sinking?",
         reward="I won. Don't argue, I was on the beach first, everyone saw. And now Kraveth says we BOTH scrub the drill "
                "ground, because we were 'out of the line'. This is your fault.",
         details=["battle_roar", "talk"], reward_emotes=["battle_roar"],
         accept=[("state", "self", "none"), ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"),
                 ("move", "self", "buoy_1_near", "run"), ("wait", 2500), ("sound", "kraveth", 7054),
                 ("face", "kraveth", "race_start"), ("emote", "kraveth", "battle_roar"), ("wait", 11500),
                 ("move", "self", "buoy_2_near", "run"), ("wait", 7500),
                 ("summon", "clawling_scene", "buoy_2_grab", 12), ("emote", "clawling_scene", "attack"),
                 ("sound", "clawling_scene", 1447), ("state", "self", "stun"), ("emote", "self", "wound"),
                 ("sound", "self", "naga_wound"), ("wait", 1200), ("emote", "self", "wound"), ("sound", "self", "naga_wound"),
                 ("wait", 1500), ("state", "self", "none"), ("move", "self", "buoy_3_near", "run"), ("wait", 12000),
                 ("move", "self", "race_finish", "run"), ("wait", 14000), ("emote", "self", "battle_roar"),
                 ("sound", "self", "naga_aggro")],
         complete=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 2000),
                   ("emote", "kraveth", "battle_roar"), ("wait", 1500), ("move", "self", "line_2", "walk"), ("wait", 5000),
                   ("face", "self", "empress"), ("state", "self", "ready_thrown")],
         poi=["buoy_1", "buoy_2", "buoy_3"]),

    # 1.06: scrub the shrine (boring; the sigil flickers, and something sings under the water)
    dict(key="ch1_scrub", title="Scrub the Shrine", giver="kraveth", ender="kraveth", level=11, xp=8, tone="boring",
         prev="ch1_race", items=[("barnacle", 5)],
         goal="Scrub the barnacles off the 5 barnacled spots at the foot of the Empress's image on the shrine, and bring "
              "the scrapings to Drillmaster Kraveth.",
         text="Out of the line. Racing. RACING. The Empress's image has barnacles on her, and you two have nothing to do. "
              "Bucket. Brush. Five spots, and the sigil at her feet. When I can see my face in her I'll know you're done.",
         progress="I still can't see my face in her. That's barnacles, not my face.",
         reward="Hm. Shining. Good. ...What? Why are you looking at the pool? Nothing sings in the pool. Back to the line.",
         details=["battle_roar", "talk"], reward_emotes=["talk"],
         accept=[("aura", "player", "bucket"), ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"),
                 ("wait", 1500), ("face", "self", "empress"), ("emote", "self", "spell"), ("wait", 1500),
                 ("emote", "ssethis", "roar"), ("face", "self", "coral_2")],
         complete=[("unaura", "player", "bucket"), ("face", "self", "empress"), ("emote", "self", "talk"), ("wait", 1500),
                   ("face", "self", "pool"), ("wait", 1500), ("emote", "self", "battle_roar"), ("face", "self", "coral_2")],
         poi=["empress"]),

    # 1.07: eels for the larder (boring)
    dict(key="ch1_eels", title="Eels for the Larder", giver="cook", ender="cook", level=11, xp=8, tone="boring",
         prev="ch1_creed", items=[("eel_fillet", 8)], drops={"eel_fillet": [("ribbon_eel", 70)]},
         goal="Bring Cook Ysthra 8 Ribbon Eel Fillets from the Ribbon Eels in the kelp off the west spit.",
         text="Look at this pot. Look in it. That's the bottom of the pot. The guards eat, the Matron eats, the hatchlings "
              "eat, and the pot doesn't care. Ribbon eels, in the kelp past the spit. Eight fillets. Mind the teeth; they "
              "bite on the way down.",
         progress="Still empty. It echoes. A pot shouldn't echo.",
         reward="Eight. The guards first, then the Matron, then the hatchlings. The heads go to the mur'gul. You get the "
                "smell on your hands. That's tide-runner's wages.",
         details=["talk"], reward_emotes=["work"], rewards=["eel_stew"],
         accept=[("state", "self", "none"), ("object", "empty_pot", "cook_pot", 20), ("emote", "self", "work"),
                 ("sound", "self", 973), ("wait", 900), ("emote", "self", "work"), ("sound", "self", 973), ("wait", 1500),
                 ("emote", "self", "talk"), ("face", "self", "kelp"), ("emote", "self", "spell"), ("wait", 2000),
                 ("face", "self", "cook_pot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "work"), ("sound", "self", 1189), ("wait", 1500),
                   ("face", "self", "warden_n"), ("emote", "self", "throw"), ("wait", 1200), ("face", "self", "szessh"),
                   ("emote", "self", "throw"), ("wait", 1200), ("face", "self", "mrgl"), ("emote", "self", "throw"),
                   ("emote", "murgul_1", "eat"), ("sound", "murgul_1", "murloc_fidget"), ("emote", "ch0:mrgl", "cheer"),
                   ("wait", 2000), ("face", "self", "cook_pot"), ("state", "self", "work")],
         poi=["kelp"]),

    # 1.08a: an extra ration (hero): Mrgl begs for the old mur'gul
    dict(key="ch1_ration", title="An Extra Ration", giver="ch0:mrgl", ender="ch0:mrgl", level=11, xp=8, tone="serious",
         path="hero", exclusive=1, prev="ch1_eels", source="ration_fish",
         use=[("ration_fish", "old_murgul", 1, [("state", "self", "none"), ("emote", "self", "eat"), ("sound", "self", 1189),
                                                ("wait", 2500), ("emote", "self", "eat"), ("wait", 1500),
                                                ("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"),
                                                ("wait", 12000), ("state", "self", "sleep")])],
         goal="Slip the Hatchling's Ration to Old Glubb, the old mur'gul lying behind the mur'gul's hut.",
         text="Mrgl... Mrgl asks. Old Glubb no work, no fish. No fish, no Glubb. Hatchlings' basket has many fish. One "
              "fish. One! Nobody counts one. Mrgl counts, but Mrgl doesn't tell.",
         progress="Glubb still hungry? Mrgl hears his belly.",
         reward="Glubb eats! Glubb pats your tail! Kraveth counts the basket... Mrgl counts it for him. One, two, three, "
                "five. Kraveth says good. Mrgl says nothing.",
         details=["beg", "point"], reward_emotes=["cheer", "bow"], rewards=["counting_pendant"],
         accept=[("emote", "self", "beg"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("face", "self", "old_murgul"),
                 ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "beg")],
         complete=[("move", "kraveth", "mrgl_basket", "run"), ("emote", "self", "bow"), ("wait", 6000),
                   ("emote", "kraveth", "talk"), ("wait", 1200), ("face", "self", "mrgl_basket"), ("emote", "self", "point"),
                   ("sound", "self", "murloc_fidget"), ("wait", 900), ("emote", "self", "point"), ("wait", 900),
                   ("emote", "self", "point"), ("wait", 900), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 1200), ("emote", "kraveth", "battle_roar"), ("wait", 1500), ("move", "kraveth", "kraveth", "walk"),
                   ("wait", 1500), ("face", "self", "player"), ("emote", "self", "laugh")],
         poi=["old_murgul"]),

    # 1.08b: report the thief (menace)
    dict(key="ch1_thief", title="Report the Thief", giver="kraveth", ender="kraveth", level=11, xp=8, tone="serious",
         path="menace", exclusive=1, prev="ch1_eels",
         goal="Tell Drillmaster Kraveth who has been stealing from the hatchlings' basket.",
         text="The hatchlings' basket comes up short. Every night, one fish short. You sleep by the mur'gul's hut, runner. "
              "You hear things. A thief in the crèche is a crack in the Empress's wall. Name it, and I fill the crack.",
         progress="Well? Who?",
         reward="The counting one. Of course. They always think the count is theirs. Not any more. The Matron will hear "
                "you were loyal.",
         details=["battle_roar", "talk"], reward_emotes=["battle_roar"], rewards=["matron_band"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "kraveth_hut"),
                 ("emote", "self", "roar"), ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("face", "self", "kraveth_hut"),
                   ("move", "warden", "mrgl_lash", "run"), ("wait", 6500), ("emote", "warden", "attack"),
                   ("sound", "warden", 3338), ("aura", "ch0:mrgl", "lashed"), ("sound", "ch0:mrgl", "murloc_wound"),
                   ("emote", "ch0:mrgl", "cry"), ("wait", 1500), ("emote", "warden", "attack"), ("sound", "warden", 3338),
                   ("sound", "ch0:mrgl", "murloc_wound_crit"), ("wait", 2500), ("face", "ch0:mrgl", "old_murgul"),
                   ("move", "warden", "warden_n", "walk"), ("wait", 2000), ("face", "self", "coral_2")],
         poi=["kraveth"]),

    # 1.09: the Deep Pool (Szessh won't say for whom)
    dict(key="ch1_pool", title="The Deep Pool", giver="szessh", ender="ch0:isshara", level=11, xp=8, tone="serious",
         prev=["ch1_eggs", "ch1_scrub"], prev_any=["ch1_ration", "ch1_thief"], source="basket",
         objects=[("cage_bars", 1)],
         goal="Take the Covered Basket to the sunken cage at the edge of the Deep Pool, west of the pens, and set it inside "
              "the bars.",
         text="A basket. The Deep Pool, west of the pens. There is a cage at its edge. Put the basket inside the bars and "
              "come away. Do not talk. Do not listen. If it sings, swim faster.",
         progress="She won't eat if you hold it. Put it inside.",
         reward="You have a kind way of setting down a basket. Most of them throw it. Sit a moment, tide-runner. "
                "Nobody comes to the Deep Pool for the view.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "pool"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "line_mid"), ("state", "self", "work"),
                 ("face", "ch0:isshara", "player")],
         complete=[("emote", "self", "work"), ("wait", 1500), ("emote", "self", "talk"), ("wait", 1500),
                   ("visual", "self", 36005), ("sound", "self", "pickup_water")],
         poi=["isshara"]),

    # 1.10: don't be afraid (she sings; you are there)
    dict(key="ch1_afraid", title="Don't Be Afraid", giver="ch0:isshara", ender="isshara_elf", level=11, xp=8,
         tone="serious", prev="ch1_pool", memory="m0", explore="m0_isshara", radius=8,
         goal="Touch the water while Isshara sings. In her memory, go to the young handmaiden by the queen's fountain.",
         text="They tell you the Empress saved us. I was there, little one. I was a handmaiden in the queen's court the "
              "night the Well swallowed the world, and I remember it, because some things sink too deep to be taken. "
              "Put your hands in the water. I'll sing. You'll see what your Matron cannot.",
         progress="The fountain. Find her by the fountain.",
         reward="There you are! The new page. Stop gaping at the lanterns, everyone gapes at the lanterns. Come, there's "
                "work.",
         details=["talk"], reward_emotes=["laugh", "wave"],
         accept=[("face", "self", "player"), ("say", "self", "Don't be afraid.", "talk", "NagaSirenWhat2"), ("wait", 1500),
                 ("state", "self", "channel"), ("music", 9461), ("visual", "player", 22576), ("sound", "self", "siren_hiss"),
                 ("wait", 3500), ("relive", "m0"), ("wait", 2000), ("state", "self", "none"), ("unaura", "player", 22576)],
         complete=[("emote", "self", "laugh"), ("wait", 1200), ("face", "self", "m0_fountain"), ("emote", "self", "point"),
                   ("wait", 1500), ("face", "self", "player")],
         poi=["m0_isshara"]),

    # 1.11: the queen's court (the page's chore: silver bowls for the lords)
    dict(key="ch1_court", title="The Queen's Court", giver="isshara_elf", ender="isshara_elf", level=12, xp=8, tone="funny",
         prev="ch1_afraid", memory="m0",
         use=[("bowl", "lord_taster", 1, [("emote", "self", "eat"), ("wait", 1800), ("emote", "self", "no"),
                                          ("emote", "self", "rude"), ("sound", "self", "pickup_water")]),
              ("bowl", "lord_bower", 1, [("face", "self", "statue_feet"), ("emote", "self", "bow"), ("wait", 1500),
                                         ("face", "self", "player"), ("emote", "self", "bow"), ("wait", 1500),
                                         ("face", "self", "statue_feet"), ("emote", "self", "bow")]),
              ("bowl", "lord_pincher", 1, [("emote", "self", "eat"), ("wait", 1200), ("face", "self", "m0_pinched"),
                                           ("emote", "self", "laugh"), ("emote", "lady_pinched", "cry"),
                                           ("face", "vashj_elf", "m0_banner"), ("emote", "vashj_elf", "work"),
                                           ("wait", 2000), ("face", "vashj_elf", "m0_pincher"), ("emote", "vashj_elf", "no"),
                                           ("wait", 2500), ("emote", "self", "shy"),
                                           ("move", "self", "m0_pincher_away", "walk"), ("wait", 8000),
                                           ("move", "self", "m0_pincher", "walk"), ("face", "vashj_elf", "statue_feet")])],
         goal="In Isshara's memory, fill a silver bowl at the queen's fountain and carry it to Lord Ethalor, Lord Vaelan "
              "Duskwhisper and Lord Ilthanos, one bowl at a time.",
         text="Well-water for the lords before the queen comes out. From the fountain, in the silver bowls, one at a time, "
              "and don't spill. Lord Ethalor will taste it and complain. Lord Vaelan will bow to the statue. Lord Ilthanos "
              "will be Lord Ilthanos. Smile at all of them.",
         progress="One bowl, one lord. You can't carry the fountain.",
         reward="Spat out, bowed at, and Ilthanos sulking by the lanterns. Vashj gave him the look. You saw the look? "
                "Nobody survives the look. Now listen... the queen is coming out.",
         details=["point", "laugh"], reward_emotes=["laugh", "cheer"],
         accept=[("emote", "self", "talk"), ("wait", 1200), ("face", "self", "m0_fountain"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "m0_taster"), ("emote", "self", "point"), ("wait", 1200),
                 ("face", "self", "player"), ("emote", "self", "laugh")],
         complete=[("emote", "self", "laugh"), ("wait", 1500), ("face", "self", "statue_feet"), ("emote", "self", "bow"),
                   ("emote", "lord_bower", "bow"), ("wait", 1500), ("face", "self", "player")],
         poi=["m0_fountain", "m0_taster", "m0_bower"]),

    # 1.12: the Night of the Well (a set piece: no words at all)
    dict(key="ch1_well", title="The Night of the Well", giver="isshara_elf", ender="ch0:isshara", level=12, xp=8,
         tone="serious", prev="ch1_court", memory="m0", wake=True, event="The Night of the Well lived",
         goal="In Isshara's memory, kneel with the court before the queen's statue, and stay until the end.",
         text="Kneel when we kneel. Keep your eyes down. Whatever the light does, whatever the sky does, don't run. The "
              "queen has promised us a new world tonight, and the queen keeps her promises.",
         progress="Stay with us. Stay.",
         reward="...You're awake. Good. Breathe. Your Matron says the Empress saved us that night. Tell me, little one. "
                "Did you see anyone saving anyone?",
         details=["talk"], reward_emotes=["talk"],
         accept=[("move", "self", "k_isshara", "walk"), ("move", "vashj_elf", "k_vashj", "walk"),
                 ("move", "lord_taster", "k_taster", "walk"), ("move", "lord_bower", "k_bower", "walk"),
                 ("move", "lord_pincher", "k_pincher", "walk"), ("move", "lady_pinched", "k_pinched", "walk"),
                 ("move", "lady_court", "k_lady", "walk"), ("wait", 7000),
                 ("face", "self", "statue_feet"), ("face", "vashj_elf", "statue_feet"), ("face", "lord_taster", "statue_feet"),
                 ("face", "lord_bower", "statue_feet"), ("face", "lord_pincher", "statue_feet"),
                 ("face", "lady_pinched", "statue_feet"), ("face", "lady_court", "statue_feet"),
                 ("state", "self", "kneel"), ("state", "vashj_elf", "kneel"), ("state", "lord_taster", "kneel"),
                 ("state", "lord_bower", "kneel"), ("state", "lord_pincher", "kneel"), ("state", "lady_pinched", "kneel"),
                 ("state", "lady_court", "kneel"), ("music", 4454), ("visual", "m0_light", 57771), ("wait", 6000),
                 ("sky", "well", "m0_well", 10, 120), ("sound", "self", 3090), ("wait", 4000),
                 ("sound", "self", 30), ("visual", "m0_light", 10387), ("wait", 3500), ("sound", "self", 3090),
                 ("visual", "well", 35426), ("wait", 4000),
                 ("visual", "well", 34602), ("sound", "self", 12549), ("aura", "player", "sea_dark"),
                 ("summon", "wave", "m0_wave_1", 25), ("summon", "wave", "m0_wave_2", 25), ("summon", "wave", "m0_wave_3", 25),
                 ("sound", "self", "splash_big"), ("wait", 1500),
                 ("state", "self", "none"), ("state", "vashj_elf", "none"), ("state", "lord_taster", "none"),
                 ("state", "lord_bower", "none"), ("state", "lord_pincher", "none"), ("state", "lady_pinched", "none"),
                 ("state", "lady_court", "none"), ("sound", "self", 14556), ("sound", "lady_pinched", 14564),
                 ("sound", "lord_taster", 14560), ("emote", "lord_bower", "cry"), ("emote", "lady_court", "cry"),
                 ("wait", 2500), ("sound", "self", 14557), ("sound", "lady_court", 14565), ("music", 5174), ("wait", 4000),
                 ("morph", "lord_taster", "naga_male"), ("morph", "lord_bower", "naga_male"),
                 ("morph", "lord_pincher", "naga_male"), ("sound", "lord_pincher", "naga_wound"), ("wait", 1500),
                 ("morph", "lady_pinched", "coilfang_siren"), ("morph", "lady_court", "coilfang_siren"),
                 ("sound", "lady_court", "siren_aggro"), ("wait", 1500), ("morph", "self", "coilfang_siren"),
                 ("scale", "self", 0.85), ("sound", "self", "siren_aggro"), ("wait", 2000),
                 ("morph", "vashj_elf", "vashj"), ("scale", "vashj_elf", 0.4), ("emote", "vashj_elf", "roar"),
                 ("despawn", "m0_light"), ("wait", 4000),
                 ("credit", "ch1_well"), ("wait", 7000),
                 ("morph", "self", None), ("scale", "self", 1.0), ("morph", "vashj_elf", None), ("scale", "vashj_elf", 1.0),
                 ("morph", "lord_taster", None), ("morph", "lord_bower", None), ("morph", "lord_pincher", None),
                 ("morph", "lady_pinched", None), ("morph", "lady_court", None),
                 ("move", "self", "m0_isshara", "walk"), ("move", "vashj_elf", "m0_vashj", "walk"),
                 ("move", "lord_taster", "m0_taster", "walk"), ("move", "lord_bower", "m0_bower", "walk"),
                 ("move", "lord_pincher", "m0_pincher", "walk"), ("move", "lady_pinched", "m0_pinched", "walk"),
                 ("move", "lady_court", "m0_lady", "walk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water"), ("wait", 1500), ("visual", "self", 36005), ("emote", "self", "omnicast")],
         poi=["statue_feet"]),

    # 1.13: the envoy comes from Nazjatar (a set piece)
    dict(key="ch1_envoy", title="The Envoy", giver="szessh", ender="szessh", level=12, xp=8, tone="serious",
         prev="ch1_well", event="The envoy received",
         goal="Stand on your mark in the line before the shrine while the Empress's envoy comes up from the sea.",
         text="Listen. Conches, out past the reef. The Empress has sent her envoy out of Nazjatar, to us, today. Every "
              "tail to its mark. The envoy will walk the line and look at each of you. You will not move. You will not "
              "speak. You will be looked at.",
         progress="Your mark. Now.",
         reward="She stopped at you. She looked a long time. I have written that down too. I would like to know why.",
         details=["battle_roar", "talk"], reward_emotes=["talk"], choice=["runner_sash", "runner_belt", "runner_girdle"],
         accept=[("state", "self", "none"), ("sound", "vessh", 7054), ("wait", 1200), ("sound", "warden", 6423),
                 ("say", "self", "Lines! The Empress's envoy comes! Every tail to its mark!", "battle_roar"),
                 ("move", "ssethis", "line_2", "run"), ("move", "self", "szessh_greet", "walk"), ("wait", 6000),
                 ("summon", "serena", "envoy_rise", 150), ("summon", "envoy_guard_1", "guard_rise_1", 150),
                 ("summon", "envoy_guard_2", "guard_rise_2", 150), ("wait", 600), ("sound", "serena", "splash_big"),
                 ("visual", "serena", 36005), ("wait", 1500),
                 ("say", "envoy_guard_1", "I come to you now, at the turn of the tide.", None, "NagaRoyalGuardReady1"),
                 ("move", "serena", "envoy_shore", "walk"), ("move", "envoy_guard_1", "guard_post_1", "walk"),
                 ("move", "envoy_guard_2", "guard_post_2", "walk"), ("wait", 10500),
                 ("face", "self", "envoy_shore"), ("emote", "self", "spell"), ("visual", "self", 19473),
                 ("visual", "shrine_glow", 57771), ("move", "self", "szessh", "walk"),
                 ("move", "serena", "envoy_line_a", "walk"), ("wait", 14500), ("face", "serena", "line_1"), ("wait", 1500),
                 ("move", "serena", "envoy_at_you", "walk"), ("wait", 4500), ("face", "serena", "player"),
                 ("emote", "serena", "spell"), ("cast", "serena", 32992, "player"), ("wait", 5500),
                 ("move", "serena", "envoy_line_b", "walk"), ("wait", 4000), ("move", "serena", "envoy_shrine", "walk"),
                 ("wait", 3000), ("face", "serena", "line_mid"), ("credit", "ch1_envoy"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000),
                   ("emote", "self", "work"), ("wait", 1500), ("state", "self", "work")],
         poi=["line_mid"]),

    # 1.14: the vault's stones (boring; the one that matters)
    dict(key="ch1_stones", title="The Vault's Stones", giver="vessh", ender="vessh", level=12, xp=8, tone="boring",
         prev="ch1_envoy", items=[("song_stone", 6)],
         goal="Carry 6 Song-Stones from the song vault in the north-east nook to Royal Guard Vessh at the shrine's brazier.",
         text="The envoy wants the vault's stones on the brazier by dawn. Six of them, from the vault, to the brazier. "
              "Carry them in your hands. Do not hold them to your ear. They are only stones.",
         progress="Six. I count to six. I count very carefully.",
         reward="One, two, three, four, five, six. Six stones for the brazier. Go and sleep, runner. Dawn comes early on "
                "the shrine.",
         details=["talk"], reward_emotes=["salute"],
         accept=[("face", "self", "vault"), ("emote", "self", "kneel"), ("sound", "self", 1277), ("wait", 1800),
                 ("face", "self", "player"), ("emote", "self", "point"), ("wait", 1200),
                 ("move", "self", "vessh_brazier", "walk"), ("wait", 13500), ("face", "self", "brazier"),
                 ("state", "self", "ready_thrown")],
         complete=[("state", "self", "none"), ("face", "self", "brazier"), ("emote", "self", "point"), ("sound", "self", 1221),
                   ("wait", 900), ("emote", "self", "point"), ("sound", "self", 1221), ("wait", 900),
                   ("emote", "self", "point"), ("sound", "self", 1221), ("wait", 900), ("emote", "self", "point"),
                   ("object", "loose_pearl", "brazier_floor", 4), ("wait", 1500), ("give", "pale_pearl", 1),
                   ("emote", "self", "salute"), ("wait", 2000), ("move", "self", "vessh", "walk"), ("wait", 13500),
                   ("face", "self", "creche"), ("state", "self", "ready_thrown")],
         poi=["vault", "brazier"]),

    # 1.15: what rolled away (she hears it before you're near)
    dict(key="ch1_rolled", title="What Rolled Away", giver="ch0:isshara", ender="ch0:isshara", level=12, xp=8,
         tone="serious", prev="ch1_stones", items=[("pale_pearl", 1)],
         goal="Give Isshara the Pale Song-Pearl that rolled into your bags.",
         text="You carry something that sings. No, don't tell me where you got it. Don't tell anyone. Put it in my hand. "
              "Through the bars. Gently, little one. Gently.",
         progress="I can hear it from here. Give it to me.",
         reward="This one I know. It was mine, before they unsung it out of me. Listen... it still knows its own name. "
                "The Awakening.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "spell"), ("wait", 1500), ("emote", "self", "talk"),
                 ("visual", "self", 36005)],
         complete=[("state", "self", "channel"), ("wait", 2000), ("visual", "self", 36005), ("wait", 1500),
                   ("say", "self", "The Awakening.", "talk"), ("music", 9462), ("wait", 2500), ("state", "self", "none")],
         poi=["isshara"]),

    # 1.16: out of the deep (the Awakening, sung)
    dict(key="ch1_deep", title="Out of the Deep", giver="ch0:isshara", ender="ch0:isshara_young", level=13, xp=8,
         tone="serious", prev="ch1_rolled", memory="m1", explore="m1_shore", radius=10,
         goal="Touch the water while Isshara sings. In her memory, rise with the naga from the deep below the cliff, and "
              "come ashore where young Isshara waits.",
         text="We had been in the dark a long time. Ten thousand years of dark. Then something called down into the water, "
              "and it was not the Empress's voice. Hands in the water again. Rise with us.",
         progress="Up. Come up. Everyone is going up.",
         reward="You came up with us. Look at them all, on the sand, blinking like hatchlings. Look up. He's still there.",
         details=["talk"], reward_emotes=["roar", "point"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("sound", "self", "siren_hiss"), ("music", 9461), ("visual", "player", 22576), ("wait", 3500),
                 ("relive", "m1"), ("wait", 2000), ("state", "self", "none"), ("unaura", "player", 22576)],
         complete=[("emote", "self", "roar"), ("wait", 1500), ("face", "self", "illidan"), ("emote", "self", "point"),
                   ("wait", 1500), ("face", "self", "player")],
         poi=["m1_shore"]),

    # 1.17: upon all who would oppose us
    dict(key="ch1_oppose", title="Upon All Who Would Oppose Us", giver="ch0:isshara_young", ender="ch0:isshara", level=13,
         xp=8, tone="serious", prev="ch1_deep", memory="m1", wake=True,
         emotes=[("m1_vashj", "roar", 1, [("face", "self", "player"), ("emote", "self", "battle_roar"),
                                          ("sound", "self", "vashj_attack")])],
         goal="In Isshara's memory, stand in the ranks on the shore and answer the call: roar at Lady Vashj.",
         text="Stand with me. He's going to speak again. When she turns to us, answer her. Everyone will.",
         progress="Answer her!",
         reward="You're back. Your Matron says we rose for the Empress. You were there. You heard who called us up. "
                "So you tell me, little one. Who called?",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "illidan"), ("yell", "illidan", "Now go forth..."), ("wait", 3000),
                 ("yell", "illidan", "Unleash the tides of doom..."), ("wait", 3000),
                 ("yell", "illidan", "Upon all who would oppose us!", "battle_roar"), ("visual", "illidan", 35411),
                 ("wait", 3500), ("face", "m1_vashj", "s_3"),
                 ("say", "m1_vashj", "Illidan will show us the path to power!", "battle_roar", "LadyVashjPissed2"),
                 ("wait", 3500), ("emote", "rank_1", "roar"), ("emote", "rank_2", "roar"), ("emote", "rank_3", "battle_roar"),
                 ("emote", "rank_4", "roar"), ("emote", "rank_5", "battle_roar"), ("emote", "rank_6", "roar"),
                 ("emote", "shore_crowd", "roar"), ("sound", "rank_1", "naga_aggro"), ("sound", "rank_2", "siren_aggro"),
                 ("sound", "rank_5", "naga_aggro"), ("emote", "self", "roar"), ("sound", "self", "siren_aggro")],
         complete=[("face", "self", "player"), ("emote", "self", "omnicast"), ("wait", 1500), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water"), ("wait", 1500), ("emote", "self", "talk")],
         poi=["vashj_shore"]),

    # 1.18: first lessons, one per class (the crèche's instructors; they glance at the royal guard between moves)
    dict(key="ch1_lesson_warrior", title="First Lessons", giver="kraveth", ender="kraveth", level=10, xp=8, tone="funny",
         classes=["warrior"], prev="ch1_creed", learn=[71, 7386, 355],
         interact=[("kraveth", "Raise your shield. Hold.")], interact_goal="Kraveth's shield drill held",
         interact_beats=[("face", "self", "player"), ("emote", "self", "battle_roar"), ("wait", 1200),
                         ("emote", "self", "attack"), ("sound", "self", 973), ("wait", 900), ("emote", "self", "attack"),
                         ("sound", "self", 973), ("wait", 900), ("emote", "self", "attack2h"), ("sound", "self", 973),
                         ("wait", 1200), ("emote", "self", "roar"), ("sound", "self", "naga_aggro")],
         goal="Hold Drillmaster Kraveth's shield drill on the drill ground.",
         text="A trident is a tide-runner's. A shield is a warrior's. Stand. Shield up. I come at you, and you do not "
              "move. Not your coil, not your tail. When the wall doesn't move, the tide breaks on it.",
         progress="Shield. Up.",
         reward="You didn't move. Well... your tail moved. Tails always move. That stance is yours now: the wall's stance. "
                "Keep the shield, too. I have plenty. Hatchlings keep dropping them on me.",
         details=["battle_roar"], reward_emotes=["roar"], rewards=["drill_shield"],
         accept=[("face", "self", "vessh"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("emote", "self", "ready1h")],
         complete=[("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"), ("wait", 1500), ("face", "self", "vessh"),
                   ("wait", 1200), ("face", "self", "coral_2")],
         poi=["kraveth"]),
    dict(key="ch1_lesson_hunter", title="First Lessons", giver="ssylvi", ender="ssylvi", level=10, xp=8, tone="serious",
         classes=["hunter"], prev="ch1_creed", learn=[1515, 883, 2641, 6991, 982],
         interact=[("turtle_hatchling", "Hold out a strip of eel. Slowly.")], interact_goal="Coralback Hatchling won over",
         interact_beats=[("face", "self", "player"), ("sound", "self", 1463), ("wait", 1500), ("follow", "self"),
                         ("wait", 12000), ("evade", "self")],
         goal="Win over the Coralback Hatchling that crawls on the sand by the Deep Pool.",
         text="The crèche keeps beasts in pens. A huntress keeps beasts as friends. There's a coralback hatchling by the "
              "Deep Pool that bites everyone. Go slowly. Hand open. If it follows you, come back and I'll teach you the rest.",
         progress="It bit you? Good. Now it knows your taste.",
         reward="It followed you. Now: the beast you choose will choose you back, any beast, anywhere the sea reaches. "
                "Call it, send it away, feed it, wake it when it falls. That's the whole of it. The rest is love.",
         details=["point"], reward_emotes=["applaud", "point"], rewards=["huntress_band"],
         accept=[("face", "self", "vessh"), ("wait", 1500), ("face", "self", "turtle"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "applaud"), ("wait", 1500), ("face", "self", "vessh"), ("wait", 1200),
                   ("emote", "self", "laugh")],
         poi=["turtle"]),
    dict(key="ch1_lesson_rogue", title="First Lessons", giver="isk", ender="isk", level=10, xp=8, tone="funny",
         classes=["rogue"], prev="ch1_creed",
         interact=[("drowsy_warden", "Lift the key from his belt, and put it back.")], interact_goal="Key lifted and returned",
         interact_beats=[("sound", "self", 1193), ("wait", 1500), ("sound", "self", "naga_hiss"), ("emote", "self", "stun"),
                         ("wait", 2000), ("sound", "self", 1193), ("state", "self", "drowned")],
         goal="Lift the key from the belt of the Drowsy Warden asleep by the shrine, and put it back, without waking him.",
         text="...That one. By the shrine. Asleep. Key on his belt. Take it. Put it back. If he wakes, you were never "
              "here, and neither was I.",
         progress="...",
         reward="...Good. Now you know the weight of a thing that isn't yours. Remember it.",
         details=["shy"], reward_emotes=["yes"], rewards=["quiet_knife"],
         accept=[("face", "self", "vessh"), ("wait", 2000), ("face", "self", "drowsy"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "shy")],
         complete=[("emote", "self", "yes"), ("wait", 1500), ("face", "self", "vessh"), ("wait", 1500),
                   ("emote", "self", "shy")],
         poi=["drowsy"]),
    dict(key="ch1_lesson_priest", title="First Lessons", giver="ch0:ulmara", ender="ch0:ulmara", level=10, xp=8,
         tone="serious", classes=["priest"], prev="ch1_creed",
         emotes=[("hurt_hatchling", "pray", 2, [("visual", "self", 57771), ("state", "self", "none"), ("emote", "self", "cheer"),
                                                ("wait", 15000), ("state", "self", "sleep")])],
         goal="Pray over 2 Bruised Hatchlings in the pens.",
         text="Two of the little ones fought over a shell and lost. Kneel by them and pray. Not to the image on the shrine, "
              "not today. To the water, if you like. The water has always listened to me.",
         progress="Pray. Quietly. The wardens don't need to hear.",
         reward="They're up and fighting over the shell again. That's how you know a prayer worked. Keep this pearl; it "
                "was mine when I was a runner.",
         details=["talk"], reward_emotes=["omnicast"], rewards=["tide_pearl"],
         accept=[("face", "self", "vessh"), ("wait", 1800), ("face", "self", "hurt_1"), ("emote", "self", "omnicast"),
                 ("visual", "self", 57771), ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", 57771), ("wait", 1500), ("face", "self", "vessh"),
                   ("wait", 1500), ("face", "self", "player")],
         poi=["hurt_1", "hurt_2"]),
    dict(key="ch1_lesson_shaman", title="First Lessons", giver="mesh", ender="mesh", level=10, xp=8, tone="serious",
         classes=["shaman"], prev="ch1_creed", items=[("ember", 1), ("shrine_stone", 1)], rewards=[5175, 5176],
         goal="Bring Stormcaller Mesh an ember from the shrine's brazier and a stone from the foot of the Empress's image.",
         text="Fire and earth. The shrine's brazier never goes out, and the stones at the image's foot have heard the "
              "creed ten thousand times. Take an ember and a stone. The spirits will know whose they are.",
         progress="An ember. A stone. Before the wardens notice the brazier smoking.",
         reward="Hold them. Feel the earth under the stone, and the fire inside the ember? Now they're yours, carved into "
                "totems. Plant them, and they'll answer.",
         details=["omnicast"], reward_emotes=["omnicast"],
         accept=[("face", "self", "vessh"), ("wait", 1500), ("face", "self", "brazier"), ("emote", "self", "point"),
                 ("wait", 1500), ("face", "self", "shrine_stone"), ("emote", "self", "point"), ("wait", 1200),
                 ("face", "self", "player")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", 13236), ("wait", 2000), ("visual", "self", 34602),
                   ("wait", 1500), ("face", "self", "vessh")],
         poi=["brazier", "shrine_stone"]),
    dict(key="ch1_lesson_mage", title="First Lessons", giver="vythe", ender="vythe", level=10, xp=8, tone="funny",
         classes=["mage"], prev="ch1_creed", kill=[("clawling", 3)],
         goal="Kill 3 Makrinni Clawlings south of the pens with your spells.",
         text="Frost. Freeze the clawling, then break it. Not fire. Fire is for when the Matron trusts you, and the Matron "
              "trusts nobody. Three clawlings, on the sand by the pens. Watch the eggs.",
         progress="Is that smoke? I said frost.",
         reward="Three, and nothing on fire. Here. A shell that's been in the cold too long. It'll help you think.",
         details=["spell"], reward_emotes=["applaud"], rewards=["frost_shell"],
         accept=[("face", "self", "vessh"), ("wait", 1500), ("emote", "self", "spell"), ("visual", "self", 32992),
                 ("wait", 1500), ("face", "self", "claws"), ("emote", "self", "point"), ("face", "self", "player")],
         complete=[("emote", "self", "applaud"), ("visual", "self", 32992), ("wait", 1500), ("face", "self", "vessh")],
         poi=["claws"]),
    dict(key="ch1_lesson_warlock", title="First Lessons", giver="ch0:nazreth", ender="ch0:nazreth", level=10, xp=8,
         tone="serious", classes=["warlock"], prev="ch1_creed", learn=[697], kill=[("voidling", 1)],
         goal="Break the Tide-Cave Voidling in the drowned elven ruin south-west of the egg beds, so it can be bound.",
         text="Something lives in the drowned ruin past the egg beds. Not a fish. A little thing from the dark between "
              "worlds, washed in on the tide. I learned to bind such things in Outland, under a master the crèche doesn't "
              "name. Beat it until it knows you. Then it's yours to call.",
         progress="Still loose? Then it still thinks it's its own.",
         reward="There. It knows you now. Call it, and it comes, and it stands between you and whatever's coming. Don't "
                "tell the Matron where you learned that. Don't tell her where I learned it.",
         details=["spell"], reward_emotes=["spell"], rewards=["void_shell"],
         accept=[("face", "self", "vessh"), ("wait", 1500), ("visual", "self", 43167), ("emote", "self", "spell"),
                 ("wait", 1500), ("face", "self", "ruin"), ("face", "self", "player")],
         complete=[("visual", "self", 43167), ("visual", "self", 12380), ("emote", "self", "omnicast"), ("wait", 2000),
                   ("face", "self", "vessh")],
         poi=["ruin"]),

    # 1.19: dawn over the brazier (a set piece: the songs crushed)
    dict(key="ch1_dawn", title="Dawn Over the Brazier", giver="szessh", ender="szessh", level=13, xp=8, tone="serious",
         prev="ch1_oppose", event="The songs crushed",
         goal="Stand with the crèche at the shrine's brazier while the envoy speaks.",
         text="The envoy speaks to the crèche at the brazier this morning. All of you. You will stand. You will listen. "
              "You will remember only what she tells you to remember.",
         progress="To the brazier.",
         reward="You heard her. Be grateful. ...Why are you shaking? It is only noise. Go back to your work.",
         details=["battle_roar"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("sound", "vessh", 7054),
                 ("say", "self", "To the brazier. All of you. The envoy will speak.", "battle_roar"),
                 ("summon", "serena", "brazier_serena", 90), ("summon", "song_echo", "brazier", 60),
                 ("object", "stone_on_brazier", "bs_1", 9), ("object", "stone_on_brazier", "bs_2", 15),
                 ("object", "stone_on_brazier", "bs_3", 21), ("object", "stone_on_brazier", "bs_4", 27),
                 ("object", "stone_on_brazier", "bs_5", 33), ("object", "stone_on_brazier", "bs_6", 39), ("wait", 6000),
                 ("face", "serena", "brazier"), ("emote", "serena", "spell"), ("wait", 3000), ("visual", "serena", 35426),
                 ("say", "song_echo", "Ash'valana thure.", None, "NagaSirenYes3"), ("wait", 3000),
                 ("emote", "serena", "spell"), ("wait", 3000), ("visual", "serena", 35426),
                 ("say", "song_echo", "For Nazjatar!", None, "NagaMyrmadonWarcry1"), ("wait", 3000),
                 ("emote", "serena", "spell"), ("wait", 3000), ("visual", "serena", 35426),
                 ("say", "song_echo", "Our alliance binds me.", None, "NagaRoyalGuardYes3"), ("wait", 3000),
                 ("emote", "serena", "spell"), ("wait", 3000), ("visual", "serena", 35426),
                 ("say", "song_echo", "By land or sea.", None, "NagaSirenYes1"), ("wait", 3000),
                 ("emote", "serena", "spell"), ("wait", 3000), ("visual", "serena", 35426),
                 ("say", "song_echo", "I will honor our pact.", None, "NagaMyrmadonYes4"), ("wait", 3000),
                 ("emote", "serena", "spell"), ("wait", 3000), ("visual", "serena", 35426),
                 ("say", "song_echo", "The tide turns.", None, "NagaSirenYesAttack1"), ("wait", 4000),
                 ("sound", "ch0:isshara", 4022), ("emote", "ch0:isshara", "wound"), ("wait", 2500),
                 ("face", "serena", "line_mid"),
                 ("say", "serena", "These are the songs of the drowned and the disobedient. The Empress remembers for us. "
                                   "Be grateful.", "talk"), ("wait", 5000),
                 ("credit", "ch1_dawn"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500),
                   ("face", "self", "pool"), ("wait", 1500), ("state", "self", "work")],
         poi=["brazier"]),

    # 1.20a: a rival's silence (hero)
    dict(key="ch1_rival_a", title="A Rival's Silence", giver="ssethis", ender="ch0:isshara", level=13, xp=8,
         tone="serious", path="hero", exclusive=2, prev="ch1_dawn",
         goal="Ask Ssethis to keep quiet about the Deep Pool, then go to Isshara.",
         text="I saw you. At the Deep Pool. Every night. Talking to the thing in the cage. I could tell the Matron. I could "
              "tell her right now. Why shouldn't I?",
         progress="",
         reward="He saw, and he didn't speak? Then he's lonelier than you know. That one roars loudest because nobody ever "
                "answered him. Be careful with him, little one. And be kind, if you can.",
         details=["battle_roar"], reward_emotes=["talk"],
         accept=[("move", "self", "ssethis_block", "walk"), ("wait", 1500), ("face", "self", "player"),
                 ("state", "self", "ready_thrown"), ("wait", 2000), ("face", "self", "isshara"), ("wait", 2500),
                 ("face", "self", "player"), ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro"),
                 ("wait", 2000), ("state", "self", "none"), ("move", "self", "ssethis_away", "walk"), ("wait", 8000),
                 ("move", "self", "line_2", "walk"), ("wait", 6000), ("face", "self", "empress"),
                 ("state", "self", "ready_thrown")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water")],
         poi=["isshara"]),

    # 1.20b: a rival's fear (menace)
    dict(key="ch1_rival_b", title="A Rival's Fear", giver="ch0:isshara", ender="ch0:isshara", level=13, xp=8,
         tone="serious", path="menace", exclusive=2, prev="ch1_dawn", source="shard", objects=[("bedding_ssethis", 1)],
         goal="Hide the Song-Stone Shard in Ssethis's kelp bedding by the old pagoda.",
         text="The loud one saw you. If he talks, they unsing me, and then they start on you. Here. A shard of the stones "
              "she crushed; the wardens swept the dust into my pool, and this came with it. Put it in his bedding. If he talks, "
              "they search him first. A song in a tide-runner's bed is a heresy.",
         progress="His bedding. By the old pagoda. Quietly.",
         reward="Done? Then he's the heretic, if anyone is. I don't like it either. I've done worse to better people, a "
                "long time ago, for a queen. That's the trouble with surviving: you get the practice.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "spell"), ("wait", 1500), ("emote", "self", "talk"),
                 ("wait", 1500), ("face", "self", "bedding")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water"), ("wait", 1200), ("visual", "self", 36005)],
         poi=["bedding"]),

    # 1.21: Mrgl-Who-Counts (two versions: after 1.08a he leads you; after 1.08b he only points)
    dict(key="ch1_way", title="Mrgl-Who-Counts", giver="ch0:mrgl", ender="ch0:mrgl", level=14, xp=8, tone="serious",
         prev="ch1_ration", prev_any=["ch1_rival_a", "ch1_rival_b"], explore="nest", radius=6,
         goal="Follow Mrgl-Who-Counts to the crack in the reef at the Deep Pool's mouth, where the mur'gul keep a nest.",
         text="Mrgl knows a way. Mur'gul always know a way; nobody watches mur'gul. Pool... line... sea. Mrgl shows. "
              "Come. Quiet. Mrgl shows you something else too.",
         progress="Here! Here. Look in the kelp.",
         reward="The egg. The Matron's missing egg. Mur'gul keep it warm, here, by the Pool, so it hears her sing. One. "
                "Mrgl counts it. One. Mrgl counts it again. Still one.",
         details=["point", "beg"], reward_emotes=["cheer", "point"],
         accept=[("move", "self", "mrgl_draw", "walk"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "sand_pool", "draw_a", 45), ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "sand_line", "draw_b", 45), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "sand_beach", "draw_c", 45), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                 ("move", "self", "nest_mrgl", "walk")],
         complete=[("face", "self", "nest"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1200),
                   ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "cheer"),
                   ("wait", 3500), ("move", "self", "mrgl", "walk")],
         poi=["nest"]),
    dict(key="ch1_way_b", title="Mrgl-Who-Counts", giver="ch0:mrgl", ender="ch0:mrgl", level=14, xp=8, tone="serious",
         prev="ch1_thief", prev_any=["ch1_rival_a", "ch1_rival_b"], explore="nest", radius=6,
         goal="Find the crack in the reef at the Deep Pool's mouth that Mrgl-Who-Counts drew for you, then come back to him.",
         text="Mrgl... Mrgl knows a way. Mrgl doesn't take you. Mrgl draws. Pool... line... sea. There. Go. Look in the "
              "kelp. Then come back and say Mrgl counted right.",
         progress="Kelp. Look in the kelp.",
         reward="You saw the egg. The Matron's missing egg. Mur'gul keep it warm by the Pool so it hears her sing. Mrgl "
                "counts it. One. Mrgl counts it again. One. Mrgl still helps. Mrgl is that kind of mur'gul.",
         details=["point"], reward_emotes=["point", "cry"],
         accept=[("move", "self", "mrgl_draw", "walk"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "sand_pool", "draw_a", 45), ("sound", "self", 1194), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "sand_line", "draw_b", 45), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "sand_beach", "draw_c", 45), ("wait", 1500), ("face", "self", "nest"),
                 ("emote", "self", "point"), ("wait", 2500), ("move", "self", "mrgl", "walk")],
         complete=[("face", "self", "player"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"),
                   ("wait", 1200), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                   ("face", "self", "old_murgul"), ("emote", "self", "cry")],
         poi=["nest"]),

    # 1.22: Kraveth's keys (two versions: after 1.20a Ssethis sees, and turns his back; after 1.20b he is dragged off)
    dict(key="ch1_keys", title="Kraveth's Keys", giver="ch0:mrgl", ender="ch0:mrgl", level=14, xp=8, tone="funny",
         prev="ch1_rival_a", prev_any=["ch1_way", "ch1_way_b"],
         interact=[("kraveth", "Slip the key ring off his belt.")], interact_goal="Kraveth's key ring taken",
         interact_beats=[("say", "self", "The day of our invasion shall be known as B-Day.", None, "NagaRoyalGuardPissed7"),
                         ("wait", 5500), ("face", "self", "nap_roll"), ("give", "cage_key", 1), ("sound", "self", 1193),
                         ("wait", 1500), ("face", "ssethis", "player"), ("wait", 2500), ("face", "ssethis", "ssethis_away"),
                         ("state", "ssethis", "ready_thrown")],
         goal="Take the cage's key ring from Drillmaster Kraveth while he naps in the shallows by the mur'gul's hut.",
         text="Kraveth naps. After the drill, in the shallows, belly up. Snores like a shark. Keys on his belt. The cage key "
              "is the big one. Mrgl can't reach. Mrgl is short. You are long.",
         progress="Jingle? No jingle? Shh.",
         reward="Keys! Big key! Shh. Shh. Hide it. And the loud one... the loud one saw, and he looked away. Mrgl saw him "
                "look away.",
         details=["point"], reward_emotes=["laugh", "cheer"],
         accept=[("state", "self", "sleep"), ("wait", 2000), ("state", "self", "none"), ("face", "self", "nap"),
                 ("emote", "self", "point"), ("move", "kraveth", "nap", "run"), ("move", "ssethis", "ssethis_watch", "run"),
                 ("wait", 7000), ("state", "kraveth", "drowned"), ("visual", "kraveth", 6431), ("face", "ssethis", "nap"),
                 ("face", "self", "player"), ("emote", "self", "laugh")],
         complete=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                   ("state", "kraveth", "none"), ("move", "kraveth", "kraveth", "walk"), ("move", "ssethis", "line_2", "walk"),
                   ("emote", "self", "cheer"), ("wait", 6000), ("state", "ssethis", "ready_thrown")],
         poi=["nap"]),
    dict(key="ch1_keys_b", title="Kraveth's Keys", giver="ch0:mrgl", ender="ch0:mrgl", level=14, xp=8, tone="funny",
         prev="ch1_rival_b", prev_any=["ch1_way", "ch1_way_b"],
         interact=[("kraveth", "Slip the key ring off his belt.")], interact_goal="Kraveth's key ring taken",
         interact_beats=[("say", "self", "The day of our invasion shall be known as B-Day.", None, "NagaRoyalGuardPissed7"),
                         ("wait", 5500), ("face", "self", "nap_roll"), ("give", "cage_key", 1), ("sound", "self", 1193)],
         goal="Take the cage's key ring from Drillmaster Kraveth while he naps in the shallows by the mur'gul's hut.",
         text="Kraveth naps. After the drill, in the shallows, belly up. Keys on his belt. The cage key is the big one. "
              "...Listen. Wardens shouting. By the bedding. Mrgl thinks they found a song.",
         progress="Jingle? No jingle? Shh.",
         reward="Keys! Big key! Hide it. ...The loud one is gone to the Matron. Screaming. He screamed your name, you know. "
                "Nobody listened. Nobody ever listens to tide-runners.",
         details=["point"], reward_emotes=["laugh", "shy"],
         accept=[("face", "self", "bedding"), ("emote", "self", "point"), ("move", "warden", "bedding", "run"),
                 ("move", "kraveth", "nap", "run"), ("wait", 4000),
                 ("yell", "ssethis", "It isn't mine! It's the new one's! Ask the new one! ASK THEM!", "battle_roar"),
                 ("move", "ssethis", "szessh_front", "walk"), ("move", "warden", "szessh_front", "walk"), ("wait", 5000),
                 ("state", "kraveth", "drowned"), ("visual", "kraveth", 6431),
                 ("yell", "ssethis", "Matron! Matron, please! It was them!", "roar"), ("emote", "szessh", "work"),
                 ("wait", 3000), ("say", "szessh", "Take him to the deep cells. I will write it down.", "talk"),
                 ("move", "ssethis", "vault", "walk"), ("move", "warden", "vault", "walk"), ("wait", 12000),
                 ("state", "ssethis", "stun"), ("move", "warden", "warden_n", "walk"), ("face", "self", "player"),
                 ("emote", "self", "shy")],
         complete=[("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                   ("state", "kraveth", "none"), ("move", "kraveth", "kraveth", "walk"), ("face", "self", "vault"),
                   ("emote", "self", "shy")],
         poi=["nap"]),

    # 1.23a: the net-bound goblin (hero)
    dict(key="ch1_goblin_a", title="The Net-Bound Goblin", giver="ch0:mrgl", ender="ch0:mrgl", level=14, xp=8,
         tone="funny", path="hero", exclusive=3, prev_any=["ch1_keys", "ch1_keys_b"], rep=[(21, 250)],
         interact=[("nozzle", "Cut the net, and point him west.")], interact_goal="The goblin cut loose",
         interact_beats=[("state", "self", "none"), ("sound", "self", 14562), ("emote", "self", "exclamation"),
                         ("wait", 1500), ("sound", "self", 14563), ("emote", "self", "shy"), ("wait", 1800),
                         ("emote", "self", "question"), ("wait", 1200), ("emote", "self", "cheer"),
                         ("say", "self", "You're cutting me OUT? A naga with manners! Here, take it, take it, it's lucky, "
                                         "it's the luckiest thing I own!", "talk"),
                         ("give", "lucky_gear", 1), ("wait", 2500), ("emote", "self", "bow"),
                         ("move", "self", "nozzle_run", "run"), ("wait", 6000), ("despawn", "self")],
         goal="Cut the goblin out of the Spitelash net on the beach south-east of the egg beds, and send him on his way.",
         text="Mrgl found a thing in the net. Small. Green. Loud. Not mur'gul, not fish. From the broken ship, the one on "
              "the rocks. The wardens come for the nets at dusk. Mrgl thinks... Mrgl thinks it should not be there at dusk.",
         progress="Still in the net? Still loud?",
         reward="Gone? Running? Good! Running is good. Mrgl likes running. Mrgl hopes it runs all the way home.",
         details=["point"], reward_emotes=["cheer"],
         accept=[("face", "self", "nozzle"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                 ("emote", "self", "question"), ("wait", 1200), ("face", "self", "player"), ("emote", "self", "beg")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "dance")],
         poi=["nozzle"]),

    # 1.23b: the goblin's purse (menace)
    dict(key="ch1_goblin_b", title="The Goblin's Purse", giver="ch0:mrgl", ender="ch0:mrgl", level=14, xp=8,
         tone="funny", path="menace", exclusive=3, prev_any=["ch1_keys", "ch1_keys_b"], rep=[(21, -250)], money=2500,
         interact=[("nozzle", "Cut his purse from his belt, and leave him in the net.")], interact_goal="The goblin's purse taken",
         interact_beats=[("state", "self", "none"), ("emote", "self", "exclamation"), ("sound", "self", 5966),
                         ("wait", 1200), ("yell", "self", "Thief! THIEF! Somebody! That naga's a THIEF!", "point"),
                         ("wait", 1500), ("emote", "self", "rude"), ("sound", "self", 5966), ("wait", 2500),
                         ("state", "self", "sit")],
         goal="Cut the purse off the goblin in the Spitelash net on the beach south-east of the egg beds.",
         text="Mrgl found a thing in the net. Small. Green. Loud. It has a purse. Fat purse, on its belt. Coins for the "
              "road... if there is a road. The wardens come for the nets at dusk. They will take the purse. Somebody "
              "should take it first.",
         progress="Purse? Coins? Shh.",
         reward="Coins! Mrgl counts. One, two, three, five... the green one is screaming. Mrgl hears it from here. "
                "Mrgl doesn't like the screaming.",
         details=["point"], reward_emotes=["no"],
         accept=[("face", "self", "nozzle"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                 ("emote", "self", "question"), ("wait", 1200), ("face", "self", "player"), ("emote", "self", "beg")],
         complete=[("emote", "self", "point"), ("sound", "self", 120), ("wait", 1200), ("face", "self", "nozzle"),
                   ("wait", 1500), ("emote", "self", "cry")],
         poi=["nozzle"]),

    # 1.24: the breakout (the chapter's last: the Tide-Broken come for the keeper, and you go with them)
    dict(key="ch1_end", title="The Breakout", giver="ch0:isshara", ender="ch0:szaria", level=14, xp=8, tone="serious",
         path="hero", prev_any=["ch1_goblin_a", "ch1_goblin_b"], objects=[("cage_door", 1), ("reef_crack", 1)],
         goal="When the renegades raid the beach, open Isshara's cage with Kraveth's key, lead her to the crack in the reef "
              "at the Deep Pool's mouth and dive through it. Lady Szaria waits across the bay, at the Hollow.",
         text="Listen. In the bay. Hear them? Those are no sirens of the Empress's. They've come for me, little one, and "
              "they don't know you, and I can't see the way. Open the cage. Take my shoulder. The reef has a crack in it "
              "the mur'gul showed you. We go now, or I'm unsung by morning.",
         progress="The key, little one. The key.",
         reward="So this is the one who carried the keeper out. Mur'gul, a warlock, an egg, and a tide-runner with the "
                "Empress's sigil still on the shoulder. Welcome to the Hollow. Sit before you fall down. You're one of "
                "us now, whether you meant to be or not.",
         details=["talk"], reward_emotes=["talk", "roar"], choice=["tide_robe", "tide_jerkin", "tide_hauberk"],
         accept=[("face", "self", "pool"), ("music", 9461), ("summon", "renegade_siren_1", "bay_siren_1", 90),
                 ("summon", "renegade_siren_2", "bay_siren_2", 90), ("sound", "self", "siren_hiss"), ("wait", 3000),
                 ("summon", "szaria_raid", "raid_szaria", 80), ("summon", "renegade_myr_1", "raid_myr_1", 80),
                 ("summon", "renegade_myr_2", "raid_myr_2", 80), ("wait", 500), ("sound", "szaria_raid", "splash_big"),
                 ("yell", "szaria_raid", "Tide-Broken! The shrine! Leave the hatchlings be!", "battle_roar"),
                 ("move", "szaria_raid", "raid_beach", "run"), ("move", "renegade_myr_1", "raid_beach_2", "run"),
                 ("move", "renegade_myr_2", "raid_beach_3", "run"), ("sound", "warden", 7054), ("wait", 1500),
                 ("move", "warden", "raid_beach_2", "run"), ("move", "warden_pool", "raid_beach_3", "run"),
                 ("sound", "warden", "naga_aggro"), ("wait", 3000),
                 ("emote", "renegade_myr_1", "attack2h"), ("emote", "warden", "attack"), ("sound", "warden", 973),
                 ("face", "self", "player"), ("say", "self", "They've come. Open the cage, little one. Now.", "talk"),
                 ("wait", 2000), ("emote", "renegade_myr_2", "battle_roar"), ("emote", "szaria_raid", "spell")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("summon", "renegade_myr_1", "hollow_surface_1", 30),
                   ("summon", "renegade_myr_2", "hollow_surface_2", 30), ("sound", "self", "splash"), ("wait", 2000),
                   ("emote", "self", "roar"), ("emote", "renegade_myr_1", "roar")],
         poi=["isshara", "crack"]),
]

# -- more of someone already made: the shared cast at this chapter's places, the game's crabs ------------------------
SPAWNS = [
    dict(npc="ch0:isshara", at="isshara", facing=0.0, phase=CRECHE),
    dict(npc="ch0:mrgl", at="mrgl", facing=4.0, phase=CRECHE),
    dict(npc="ch0:nazreth", at="nazreth", facing=2.6, phase=CRECHE),
    dict(npc="ch0:ulmara", at="ulmara", facing=1.8, phase=CRECHE),
    dict(npc="ch0:drowned_singer", at="singer", facing=2.5, phase=CRECHE),
    # Lady Szaria at the Hollow (the bay's north shore): 1.24's ender and 2.01's giver, there in the naga's phase
    dict(npc="ch0:szaria", at="hollow_szaria", facing=3.3),
    # young Isshara in the Awakening (memory m1): she comes ashore with the ranks
    dict(npc="ch0:isshara_young", at="m1_isshara", facing=1.4, phase=M1),
    # the game's Young Reef Crawlers on the south-east sand (a hunter's first beast to tame, after 1.18)
    dict(npc=2234, at=[(2160.0, -6505.0), (2150.0, -6508.0), (2166.0, -6514.0)], wander=4.0, respawn=60, phase=CRECHE),
]

GRAVEYARDS = [
    dict(at="graveyard", name="the crèche", phase=CRECHE, facing=2.5),
]
