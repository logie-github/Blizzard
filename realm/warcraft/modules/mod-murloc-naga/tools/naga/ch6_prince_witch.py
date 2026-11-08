# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 6 of the naga's story: The Prince and the Witch (levels 34 to 38), the bible's section 13.

Vashj's own years with Kael'thas, sung from the four pearls in a renegade magister's box, and a blood elf of
Silvermoon who was there. The present's places:
  - Valormok (the world's and the naga's): Ag'tor Bloodfist is the game's own and acts only in his quest window;
    Taelon Emberveil, the story's, stands west of the naga's envoy tent (always: later chapters use him there);
    Valormok's totem stands between them, with its keeper, Grunt Thokra.
  - the road east of Valormok (3665, -4590): an overturned cart and the bones of Belgrom's orcish guard.
  - Lake Mennar (a small lake in a bowl, 2600-2680, -5300 to -5380, water at z 76): Rimtori's renegade magisters
    dig on its north shore; Magister Vaelos keeps a tent on the west ridge (2575, -5215); their summoning circle is
    on the east ridge (2620, -5440); Taelon keeps a watch on the north-west ridge above the dig (2765, -5205).
  - Valormok's landing: a lookout's fire on the bay's west strand under the Eldarath cliffs (3630, -5764), where
    6.29's boats are brought.
  - the Hollow (chapter 2's camp; Isshara by her pool at its south-east end, chapter 2's spawn).

Four memories, all Isshara's, all sung at her pool (one wakes on its shore):
  - m9, Misconceptions (bit B): Lake Mennar as Lordamere Lake. Vashj, young Isshara and the naga float in the lake;
    the Alliance's camp (Kael'thas, Grand Marshal Garithos, blood elves, Lordaeron soldiers) on the north shore; the
    wrecked goblin shipyard on the south shore; three arcane observatories on the bowl's rim.
  - m10, A Dark Covenant (bit C): the same lake and camp the next day; the Scourge on the slope north of the camp,
    the dreadlord Dalvengyr above them; the reeds are the shallows at the lake's north-west corner.
  - m11, The Dungeons of Dalaran (bit B): the drowned stones under the Ruins of Eldarath where they fall into the bay
    (the Second Tide Pool, 3604, -5703, and the beach round it) as Dalaran's prison: the sewer water one comes up
    through, Kael's cell, four lieutenants' cells, the jailers, the ghostly archmagi, Jailor Kassan at the gate.
  - m12, The Crossing (bit A): the crater on Forlorn Ridge as Dalaran's portal square (the portal on the crater's
    floor, 2955, -4775); Garithos's people come down the crater's north slope.
M9 and M10 stand on the same ground in different bits; their canon figures are separate people (vashj9, vashj10...),
so a scene in one never finds the other's (every story person shares the scene bit). M12 stands 636 yards from
chapter 5's M7 (bit A too).

Taelon: three of him, never two in one place. "taelon" at Valormok (always); "taelon_lake" at his watch above Lake
Mennar (Hollow's rule), who walks down with the player (follow) in 6.02, 6.03 and 6.28 and fights beside them, and
goes home (evade) when it's done; and summoned copies for the Hollow's scenes ("taelon_visit": at the pool's edge in
6.09, sitting down hard in 6.14, the wine in 6.27; "taelon_water": in the shallows from 6.21a, crying in 6.26).
The Hollow has no Taelon of its own: its scenes summon him, and his quests are given and taken at Valormok or at
the lake.

Phases in Azshara: none of this chapter's own (its budget is none). The lake's renegades, their tent, dig and
circle, Taelon's watch, the bones on the road east and the landing's lookout share chapter 2's rule for the Hollow's
people (HOLLOW: no bit of their own, gone at 7.02, before chapter 7's live world). Valormok's Taelon, totem and
totem-keeper stand always (the naga's phase); whoever comes for one scene is summoned in it.

Choices: 6.21a (hero: Taelon stands in the water for his brother's song) and 6.21b (menace: he pays for it with his
signet); either opens 6.22. A memory's quest can't follow a pair (the compiler allows no prev_any in one), so 6.22,
the song's first quest, is a present quest (no memory=) whose giver sings the player in and whose ender is young
Isshara at the portal; M12's quests are 6.23 to 6.26. 6.21a's reward scene leaves Taelon in the shallows (a summon
of forty minutes), and 6.26's reward scene hands him its beats (he cries, then goes): on the menace road there is
no one there to do them, so they do nothing. Nobody else's scene depends on the road taken.

Plain data: tools/murloc/SCHEMA.md, tools/naga/SCHEMA.md."""

HOLLOW = ("between", "ch2:ch2_arrival", "ch7:ch7_overturned")   # chapter 2's rule for the Hollow's people (no new bit)
M9 = ("memory", "m9")                                           # Misconceptions (Isshara's): Lake Mennar as Lordamere
M10 = ("memory", "m10")                                         # A Dark Covenant (Isshara's): Lake Mennar's shore
M11 = ("memory", "m11")                                         # The Dungeons of Dalaran (Isshara's): Eldarath's drowned edge
M12 = ("memory", "m12")                                         # The Crossing (Isshara's): the crater on Forlorn Ridge

CHAPTER = dict(key="ch6", title="The Prince and the Witch", levels=(34, 38), map=1, zones=[16], hub="hollow_pool")

TOWNS = ["Valormok"]

AGTOR = 8576        # Ag'tor Bloodfist, the game's own: his quest window's gestures are his; he runs no scenes

PLACES = {
    # -- Valormok (area 1237: the world's and the naga's) ---------------------------------------------------------
    "agtor": (3601.0, -4406.0), "taelon": (3652.0, -4432.0), "envoy_tent": (3686.0, -4428.0),
    "totem": (3630.0, -4412.0), "totem_use": (3633.0, -4415.5), "totem_hang": (3630.4, -4411.6, 113.6),
    "thokra": (3625.0, -4419.0), "valormok_east": (3700.0, -4470.0),
    "toward_lake": (2765.0, -5205.0), "toward_hollow": (3950.0, -6270.0),
    # -- the road east: the overturned cart and the bones of Belgrom's guard -----------------------------------------
    "road_east": (3664.0, -4592.0), "cart": (3665.0, -4590.0),
    "bones_1": (3660.0, -4584.0), "bones_2": (3670.0, -4597.0), "bones_3": (3655.0, -4597.0), "bones_4": (3673.0, -4583.0),
    "bones_5": (3650.0, -4588.0), "bones_6": (3667.0, -4606.0), "bones_7": (3679.0, -4592.0), "bones_8": (3658.0, -4607.0),
    "skull_1": (3662.0, -4580.0), "skull_2": (3676.0, -4602.0),
    # -- Lake Mennar today: Rimtori's dig on the north shore, Vaelos's tent, the summoning circle, Taelon's watch ------
    "taelon_post": (2765.0, -5205.0), "dig": (2700.0, -5290.0), "lake": (2640.0, -5330.0),
    "dg_1": (2690.0, -5280.0), "dg_2": (2700.0, -5268.0), "dg_3": (2712.0, -5280.0), "dg_4": (2720.0, -5296.0),
    "dg_5": (2706.0, -5300.0), "dg_6": (2692.0, -5296.0), "dg_7": (2716.0, -5262.0), "dg_8": (2726.0, -5278.0),
    "dg_9": (2684.0, -5268.0), "dg_10": (2698.0, -5252.0),
    "wd_1": (2694.0, -5260.0), "wd_2": (2718.0, -5308.0), "wd_3": (2728.0, -5266.0), "wd_4": (2680.0, -5288.0),
    "dig_tent": (2730.0, -5290.0), "dig_crates": (2724.0, -5303.0), "dig_banner": (2708.0, -5256.0),
    "dig_stone_1": (2696.0, -5285.0), "dig_stone_2": (2711.0, -5272.0), "dig_stone_3": (2702.0, -5296.0),
    "vaelos": (2575.0, -5215.0), "vaelos_tent": (2569.0, -5207.0), "pearl_box": (2572.0, -5211.0),
    "vtab_1": (2580.0, -5205.0), "vtab_2": (2565.0, -5221.0), "vg_1": (2586.0, -5222.0), "vg_2": (2567.0, -5230.0),
    "vaelos_books": (2577.0, -5208.0),
    "circle": (2620.0, -5440.0), "page_1": (2627.0, -5434.0), "page_2": (2612.0, -5436.0), "page_3": (2621.0, -5449.0),
    "fm_1": (2635.0, -5440.0), "fm_2": (2608.0, -5448.0), "fm_3": (2625.0, -5425.0), "fm_4": (2600.0, -5432.0),
    "fm_5": (2640.0, -5455.0), "fm_6": (2615.0, -5462.0), "fm_7": (2645.0, -5425.0), "fm_8": (2596.0, -5455.0),
    "fm_9": (2630.0, -5465.0), "fm_10": (2610.0, -5420.0),
    # -- Valormok's landing on the bay's west strand -----------------------------------------------------------------
    "landing": (3618.0, -5785.0), "lookout": (3630.0, -5764.0), "lookout_fire": (3636.0, -5760.0),
    "lookout_banner": (3634.0, -5770.0), "szaria_rise": (3615.0, -5800.0), "szaria_shore": (3622.0, -5772.0),
    "bay": (3600.0, -5850.0),
    # -- the Hollow (chapter 2's camp: Isshara by her pool, Szaria by the landing; these are the spots its scenes use)
    "hollow_pool": (3959.0, -6311.0), "isshara_bed": (3963.0, -6316.0), "pool": (3969.0, -6323.0),
    "szaria": (3954.0, -6266.0), "vyssa": (3966.0, -6285.0), "ssaveth": (3978.0, -6278.0),
    "taelon_from": (3955.0, -6295.0), "taelon_edge": (3970.0, -6311.0), "taelon_rock": (3974.0, -6302.0),
    "taelon_shallows": (3966.0, -6327.0), "taelon_away": (3946.0, -6262.0), "wine_spot": (3964.0, -6318.0),
    "sea_south": (3880.0, -6268.0), "sea_east": (3992.0, -6300.0),
    "boats_1": (3925.0, -6290.0, 0.0), "boats_2": (3919.0, -6297.0, 0.0),

    # -- memory m9 (bit B): Misconceptions, Lake Mennar as Lordamere Lake ---------------------------------------------
    "m9_centre": (2645.0, -5320.0), "m9_arrive": (2628.0, -5338.0), "m9_director": (2630.0, -5336.0),
    "m9_isshara": (2640.0, -5330.0), "m9_vashj": (2648.0, -5326.0), "isshara_shore": (2680.0, -5318.0),
    "vashj_rise": (2686.0, -5318.0), "vashj_stumble": (2678.0, -5322.0), "vashj_watch_yard": (2614.0, -5344.0),
    "kael9": (2700.0, -5322.0), "garithos9": (2712.0, -5302.0), "g_jab": (2704.0, -5316.0), "g_stalk": (2738.0, -5296.0),
    "g_shore": (2690.0, -5310.0), "garithos_watch": (2664.0, -5262.0),
    "kael_shore": (2688.0, -5314.0), "boats_shore": (2683.0, -5322.0, 76.4),
    "m9_tent_1": (2716.0, -5332.0), "m9_tent_2": (2724.0, -5308.0), "m9_banner_1": (2706.0, -5336.0),
    "m9_banner_2": (2702.0, -5298.0), "m9_fire": (2712.0, -5318.0), "m9_crates": (2720.0, -5320.0),
    "sol_1": (2706.0, -5306.0), "sol_2": (2717.0, -5296.0), "sol_3": (2697.0, -5302.0),
    "elf_1": (2694.0, -5330.0), "elf_2": (2704.0, -5340.0), "elf_3": (2690.0, -5338.0),
    "n9_1": (2630.0, -5318.0), "n9_2": (2625.0, -5344.0), "n9_3": (2654.0, -5352.0), "n9_4": (2618.0, -5332.0),
    "shipwright": (2583.0, -5328.0), "yard": (2588.0, -5338.0), "yard_tent": (2573.0, -5345.0),
    "yard_lumber": (2578.0, -5315.0), "yard_wreck": (2591.0, -5364.0), "yard_tnt": (2576.0, -5331.0),
    "row_1": (2597.0, -5318.0), "row_2": (2597.0, -5340.0), "leaky": (2599.0, -5357.0),
    "boat_a": (2610.0, -5326.0, 76.4), "boat_b": (2610.0, -5340.0, 76.4), "sink": (2601.0, -5358.0, 76.4),
    "obs_1": (2655.0, -5250.0), "obs_2": (2640.0, -5412.0), "obs_3": (2580.0, -5265.0),
    "lens_1": (2658.0, -5253.0), "lens_2": (2643.0, -5409.0), "lens_3": (2583.0, -5268.0),
    "eng_1": (2652.0, -5255.0), "eng_2": (2637.0, -5408.0), "eng_3": (2577.0, -5270.0),

    # -- memory m10 (bit C): A Dark Covenant, the same lake and camp the next day ---------------------------------------
    "m10_centre": (2690.0, -5295.0), "m10_arrive": (2678.0, -5304.0), "m10_isshara": (2684.0, -5309.0),
    "vashj10_lake": (2652.0, -5324.0), "vashj10_shore": (2689.0, -5314.0),
    "kael10": (2700.0, -5322.0), "kael_fight": (2727.0, -5292.0),
    "e10_1": (2706.0, -5310.0), "e10_2": (2694.0, -5330.0), "e10_3": (2713.0, -5328.0),
    "n10_1": (2668.0, -5304.0), "n10_2": (2664.0, -5318.0),
    "sc_1": (2735.0, -5240.0), "sc_2": (2745.0, -5255.0), "sc_3": (2755.0, -5236.0), "sc_4": (2741.0, -5226.0),
    "sc_5": (2760.0, -5262.0), "sc_6": (2770.0, -5246.0), "sc_7": (2731.0, -5262.0), "sc_8": (2774.0, -5228.0),
    "sc_9": (2752.0, -5214.0), "sc_10": (2765.0, -5282.0), "sc_11": (2780.0, -5264.0), "sc_12": (2784.0, -5242.0),
    "sc_13": (2740.0, -5210.0), "sc_14": (2756.0, -5292.0), "slope": (2755.0, -5250.0),
    "dalvengyr": (2752.0, -5272.0),
    "sb_run": (2735.0, -5334.0), "sb_stop": (2706.0, -5320.0),
    "g10_arrive": (2724.0, -5292.0), "g10_camp": (2709.0, -5314.0), "s10_1": (2729.0, -5300.0),
    "s10_2": (2722.0, -5284.0), "led_away": (2765.0, -5300.0), "kael_led": (2676.0, -5297.0),
    "reeds": (2669.0, -5300.0), "reeds_isshara": (2666.0, -5306.0),

    # -- memory m11 (bit B): the Dungeons of Dalaran, the drowned stones under Eldarath --------------------------------
    "m11_centre": (3612.0, -5694.0), "m11_arrive": (3604.0, -5704.0), "m11_isshara": (3614.0, -5690.0),
    "vashj11_under": (3600.0, -5707.0), "vashj_surface": (3610.0, -5694.0), "cell_door": (3621.0, -5687.0),
    "kael_cell": (3626.0, -5688.0), "kael_out": (3619.0, -5682.0), "kael_gate": (3602.0, -5664.0),
    "vashj_gate": (3606.0, -5668.0), "guard_1": (3622.0, -5680.0), "guard_2": (3630.0, -5681.0),
    "cell_1": (3645.0, -5665.0), "cell_2": (3655.0, -5685.0), "cell_3": (3650.0, -5705.0), "cell_4": (3632.0, -5722.0),
    "lock_1": (3641.0, -5667.5), "lock_2": (3651.0, -5687.5), "lock_3": (3646.0, -5702.5), "lock_4": (3628.5, -5719.0),
    "rally": (3619.0, -5671.0), "lieutenants": (3645.0, -5690.0),
    "j_1": (3640.0, -5677.0), "j_2": (3660.0, -5676.0), "j_3": (3657.0, -5697.0), "j_4": (3640.0, -5712.0),
    "j_5": (3622.0, -5728.0), "j_6": (3600.0, -5682.0), "j_7": (3634.0, -5656.0), "j_8": (3616.0, -5718.0),
    "gh_1": (3648.0, -5679.0), "gh_2": (3637.0, -5695.0), "gh_3": (3628.0, -5707.0), "gh_4": (3661.0, -5700.0),
    "gh_5": (3626.0, -5666.0),
    "gate": (3590.0, -5655.0), "kassan": (3594.0, -5660.0), "kg_1": (3588.0, -5665.0), "kg_2": (3598.0, -5653.0),
    "alarm_from": (3631.0, -5676.0), "alarm_to": (3592.0, -5658.0),
    "torch_11_1": (3618.0, -5676.0), "torch_11_2": (3638.0, -5700.0),

    # -- memory m12 (bit A): The Crossing, the crater on Forlorn Ridge as Dalaran's portal square -----------------------
    "m12_centre": (2965.0, -4772.0), "m12_arrive": (2997.0, -4773.0), "m12_isshara": (2982.0, -4774.0),
    "portal": (2955.0, -4775.0), "portal_front": (2970.0, -4775.0), "portal_mouth": (2958.0, -4775.0),
    "vashj12": (2963.0, -4777.0), "kael12": (2975.0, -4763.0), "engineer12": (2984.0, -4790.0),
    "aelthir": (2988.0, -4757.0),
    "d12_1": (2992.0, -4762.0), "d12_2": (2993.0, -4786.0), "d12_3": (2978.0, -4796.0), "d12_4": (2977.0, -4750.0),
    "n12_1": (2958.0, -4763.0), "n12_2": (2958.0, -4789.0),
    "plot_1": (3015.0, -4760.0), "plot_2": (3015.0, -4790.0), "plot_3": (2990.0, -4745.0), "plot_4": (2990.0, -4805.0),
    "north_entry": (3045.0, -4775.0), "garithos_slope": (3026.0, -4776.0),
    "north_1": (3040.0, -4762.0), "north_2": (3040.0, -4788.0), "north_3": (3047.0, -4770.0), "north_4": (3047.0, -4782.0),
    "eb_1": (3030.0, -4766.0), "eb_2": (3035.0, -4785.0), "eb_3": (3046.0, -4760.0), "eb_4": (3049.0, -4791.0),
    "eb_5": (3041.0, -4775.0), "eb_6": (3026.0, -4796.0), "eb_7": (3025.0, -4752.0), "eb_8": (3054.0, -4776.0),
    "stream_1": (2922.0, -4790.0), "stream_2": (2919.0, -4771.0), "stream_3": (2926.0, -4756.0),
    "m12_banner_1": (2970.0, -4748.0), "m12_banner_2": (2970.0, -4800.0),
}

# -- looks, models, spells for their look, sounds -----------------------------------------------------------------
BE_M, BE_F, BE_DEF, BE_RANGER, BE_MAGISTER = 18982, 18983, 18984, 19822, 15912     # blood elves (all emotes)
FOOTMAN, SENTRY, SHIELD_GUARD, JAILOR_A, JAILOR_B, JAILOR_BIG = 4125, 3632, 3711, 3625, 3626, 1830
GHOUL, GHOUL_RED, SKELETON, DREADLORD, GHOST = 137, 414, 200, 10543, 146
BEAR, WOLF, IMP, GOBLIN, ROWBOAT = 806, 2327, 4449, 7109, 30236
ORC_GRUNT, ORC_LOOKOUT = 4260, 9800
DALARAN_CRYSTAL = 28876                     # Dalaran_BuildingCrystal_01: the arcane towers (a creature look)
# objects (GameObjectDisplayInfo)
HUMAN_TENT, LORDAERON_BANNER, BE_BANNER, CAMPFIRE, BE_CRATE, BE_CRATE_2 = 7194, 4715, 6794, 192, 6616, 6792
GOBLIN_TENT, LUMBER, WRECK, TNT_WAGON, GO_ROWBOAT, SCRYING_ORB, SCRYING_ORB_SMALL = 7725, 1109, 223, 7083, 124, 7150, 6476
HE_TENT, RUNE_TABLET, BE_BOOK, RITUAL_CIRCLE, OPEN_BOOK = 8398, 236, 6475, 5812, 4032
EXCAVATION_TENT, BROKEN_CART, BONES, ORC_SKULL, TOTEM, TOKEN_BANNER, HORDE_BANNER = 7211, 7524, 5732, 7220, 4718, 2552, 8526
PRISON_CELL, CELL_LOCK, PRISON_GATE, DARK_PORTAL, PORTAL_LIGHT, GROUND_RUNE, BOTTLE = 7154, 342, 2753, 8937, 672, 343, 6802
TORCH_OBJ = "naga_torch"
# spells for their look
WATER, GLOW_BLUE, GLOW_PURPLE = 36005, 22576, 22581
ARCANE_BURST, ARCANE_MASSIVE, FEL_SHIELD, FEL_SMOKE = 35426, 63660, 32567, 35411
CHAINS, LIGHTNING, LIGHTNING_HIT, TELEPORT = 45631, 10387, 45935, 41232
FROZEN, ICE_SPIKE, GHOSTLY = 47543, 53539, 35838
GREEN_SPLASH, FIRE_HIT, FEL_HIT, SPELLSTEAL = 60059, 40162, 40108, 30449
FEL_PORTAL = 46907
# sounds (SoundEntries)
HORN, CHEST, RING, GEMS, HAMMER, PAGE = 7054, 1277, 1193, 1221, 4614, 1192
ORC_LAUGH, BE_CRY, HUMAN_LAUGH = 6943, 9651, 6923
FROST_NOVA, ICE_CRACK, CHAINS_SOUND, GOBLIN_ANGRY, GOBLIN_WAIL = 3076, 9119, 1502, 5966, 5960
UNDEAD_AGGRO, HUMAN_DEATH, BE_DEATH = 1371, 1332, 1344
# music
NAGA_MOMENT, GLOOMY, BATTLE_1, BATTLE_6, HAUNTED, SPOOKY, ANGELIC, SILVERMOON = 9461, 6074, 6077, 6350, 5174, 5037, 4517, 9801

NPCS = [
    # -- the present: Valormok ---------------------------------------------------------------------------------------
    # Taelon Emberveil of Silvermoon, the spell breaker who ran in to tell the prince Garithos had come (invented). He
    # speaks Orcish to the naga (readable); his Thalassian is written as Thalassian.
    dict(key="taelon", name="Taelon Emberveil", subname="Envoy of Silvermoon", look="taelon", equip=(20835, 30984, 0),
         level=40, role="quest", language="orcish", at="taelon", facing=0.4,
         gossip="Shorel'aran. You want something, naga. Your kind always wants something.",
         idle=[("every", 47000, [("face", "self", "envoy_tent"), ("emote", "self", "no")]),
               ("every", 71000, [("face", "self", "agtor")])]),
    dict(key="thokra", name="Grunt Thokra", subname="Keeper of Valormok's Totem", look=ORC_GRUNT, level=32,
         side="faction:76", language="orcish", role="ambient", at="thokra", facing=0.3,
         gossip="Every grunt who dies in this camp's service gets a token on the pole. The pole is getting heavy.",
         idle=[("every", 53000, [("face", "self", "totem"), ("emote", "self", "kneel")])]),
    # -- the present: Lake Mennar ------------------------------------------------------------------------------------
    # Taelon at his watch over the dig: walks down with the player (follow) and fights beside them (ally: hostile to
    # the renegades), and goes home (evade) when the quest is handed in.
    dict(key="taelon_lake", name="Taelon Emberveil", subname="Envoy of Silvermoon", look="taelon", equip=(20835, 30984, 0),
         level=40, health=6.0, side="ally", role="quest", language="orcish", at="taelon_post", facing=3.9, respawn=60,
         phase=HOLLOW, abilities=[(SPELLSTEAL, 9000), (25710, 6000)],
         gossip="They dig. I watch. One day they will dig up something that bites them, and I would like to see it.",
         idle=[("every", 43000, [("face", "self", "dig"), ("emote", "self", "ready1h")])]),
    # Rimtori's renegade magisters (the Thalassian Base Camp's own looks): hostile to everyone
    dict(key="digger", name="Thalassian Digger", plural="Thalassian Diggers", look=BE_M, looks=[BE_F], equip=(2901, 0, 0),
         level=(34, 35), side="hostile", role="enemy", language="thalassian", phase=HOLLOW, respawn=45,
         abilities=[(11976, 9000)], at=["dg_1", "dg_2", "dg_3", "dg_4", "dg_5", "dg_6", "dg_7", "dg_8", "dg_9", "dg_10"],
         idle=[("state", "self", "work")]),
    dict(key="warden", name="Thalassian Warden", plural="Thalassian Wardens", look=18980, looks=[18981],
         equip=(20835, 27910, 0), level=(35, 36), side="hostile", role="enemy", language="thalassian", phase=HOLLOW,
         respawn=45, abilities=[(8242, 12000), (25710, 7000)],
         at=["wd_1", "wd_2", "wd_3", "wd_4", "vg_1", "vg_2"], wander=4.0),
    dict(key="vaelos", name="Magister Vaelos", subname="Rimtori's Buyer", look=BE_MAGISTER, equip=(34337, 0, 0),
         level=36, health=3.0, damage=1.3, side="hostile", role="enemy", language="thalassian", caster=True,
         phase=HOLLOW, at="vaelos", facing=5.6, respawn=60, abilities=[(13748, 6000), (11831, 15000)],
         watch=(24, [("face", "self", "player"), ("say", "self", "Anar'alah belore. Sin'dorei... no. Naga. Get out of my tent.",
                                                  "rude")], 30000),
         at_health=(50, [("visual", "self", FEL_SHIELD), ("sound", "self", 7594),
                         ("yell", "self", "Kim'jael! Felo... Bal'a dash! You think Silvermoon's dog frightens me?", "shout")]),
         idle=[("every", 38000, [("emote", "self", "talk"), ("visual", "self", GLOW_PURPLE)])]),
    dict(key="fel_magister", name="Fel-Touched Magister", plural="Fel-Touched Magisters", look=21010, looks=[21013],
         equip=(20839, 0, 0), level=(37, 38), side="hostile", role="enemy", language="thalassian", caster=True,
         phase=HOLLOW, respawn=45, abilities=[(9613, 6000), (11639, 15000)],
         at=["fm_1", "fm_2", "fm_3", "fm_4", "fm_5", "fm_6", "fm_7", "fm_8", "fm_9", "fm_10"], wander=3.0,
         idle=[("every", 21000, [("visual", "self", FEL_SMOKE)])]),
    # the half-called demon at the circle, as each page burns (summoned)
    dict(key="half_imp", name="Half-Called Imp", look=IMP, scale=1.1, level=30, role="ambient", type="demon",
         untouchable=True, summoned=True, language="thalassian", idle=[("every", 2000, [("visual", "self", FEL_SMOKE)])]),
    # -- the present: Valormok's landing ---------------------------------------------------------------------------------
    dict(key="lookout", name="Grunt Harruk", subname="Valormok's Lookout", look=ORC_LOOKOUT, level=30, side="faction:76",
         language="orcish", role="ambient", at="lookout", facing=3.6, phase=HOLLOW,
         gossip="Nothing on the water but your kind and the gulls. I count both. The gulls are easier.",
         idle=[("every", 41000, [("face", "self", "bay"), ("emote", "self", "point")])]),
    dict(key="szaria_landing", name="Lady Szaria", subname="The Tide-Broken", look="siren", level=40, role="ambient",
         untouchable=True, summoned=True),
    dict(key="spitelash_boat", name="Captured Spitelash Boat", look=ROWBOAT, scale=1.1, level=1, side="neutral",
         role="ambient", unit_flags=0x02000002, summoned=True),
    dict(key="spitelash_boat_2", name="Captured Spitelash Boat", look=ROWBOAT, scale=1.1, level=1, side="neutral",
         role="ambient", unit_flags=0x02000002, summoned=True),
    # -- the present: the Hollow's scenes (summoned: he has no place there of his own) -------------------------------
    dict(key="taelon_visit", name="Taelon Emberveil", subname="Envoy of Silvermoon", look="taelon", equip=(20835, 30984, 0),
         level=40, role="ambient", language="orcish", untouchable=True, summoned=True),
    dict(key="taelon_water", name="Taelon Emberveil", subname="Envoy of Silvermoon", look="taelon", level=40,
         role="ambient", language="orcish", untouchable=True, summoned=True),
    dict(key="pool_frost", name="The Keeper's Pool", look="trigger", scale=1.6, level=1, role="ambient",
         unit_flags=0x02000002, summoned=True),

    # -- memory m9: Misconceptions -----------------------------------------------------------------------------------
    dict(key="vashj9", name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         language="universal", at="m9_vashj", facing=0.3, phase=M9, respawn=30,
         idle=[("state", "self", "swim_idle"), ("every", 37000, [("face", "self", "kael9")])]),
    dict(key="kael9", name="Prince Kael'thas Sunstrider", subname="Prince of Quel'Thalas", look="kaelthas", size=1.0,
         level=40, role="ambient", untouchable=True, language="universal", at="kael9", facing=3.5, phase=M9, respawn=30,
         idle=[("every", 31000, [("emote", "self", "talk")])]),
    dict(key="garithos9", name="Grand Marshal Garithos", subname="Commander of the Alliance in Lordaeron", look="garithos",
         equip=(25825, 43085, 0), level=40, role="ambient", untouchable=True, language="universal", at="garithos9",
         facing=3.9, phase=M9, respawn=30, idle=[("every", 44000, [("emote", "self", "rude")])]),
    dict(key="naga9", name="Naga of Lady Vashj", plural="Lady Vashj's naga", look="coilfang_myrmidon",
         looks=["coilfang_siren", 18398, 18395], equip=(15910, 0, 0), size=1.1, level=30, role="ambient", untouchable=True,
         at=["n9_1", "n9_2", "n9_3", "n9_4"], facing=0.4, phase=M9, idle=[("state", "self", "swim_idle")]),
    dict(key="soldier9", name="Lordaeron Soldier", plural="Lordaeron soldiers", look=FOOTMAN, looks=[SENTRY],
         equip=(25825, 31200, 0), level=33, role="ambient", untouchable=True, language="universal",
         at=["sol_1", "sol_2", "sol_3"], facing=3.4, phase=M9, idle=[("every", 49000, [("emote", "self", "talk")])]),
    dict(key="elf9", name="Blood Elf of Quel'Thalas", plural="the prince's elves", look=BE_DEF, looks=[BE_RANGER, BE_F],
         equip=(20835, 20841, 0), level=33, role="ambient", untouchable=True, language="universal",
         at=["elf_1", "elf_2", "elf_3"], facing=2.8, phase=M9, idle=[("every", 57000, [("emote", "self", "no")])]),
    dict(key="shipwright", name="Gizbit Sprocketspanner", subname="Shipwright, Lordamere Yards", look=GOBLIN,
         equip=(5956, 0, 0), level=30, role="ambient", untouchable=True, language="universal", at="shipwright",
         facing=0.3, phase=M9, respawn=30,
         gossip="Six boats! I had SIX BOATS! Then the dead came through, and the dead don't pay for anything!",
         idle=[("every", 23000, [("emote", "self", "cry"), ("sound", "self", GOBLIN_WAIL)])]),
    dict(key="engineer9", name="Blood Elf Engineer", plural="the prince's engineers", look=BE_DEF, looks=[BE_F],
         equip=(5956, 0, 0), level=32, role="ambient", untouchable=True, language="universal",
         at=["eng_1", "eng_2", "eng_3"], facing=0.9, phase=M9, idle=[("state", "self", "work")]),
    dict(key="towed_boat", name="Goblin Rowboat", look=ROWBOAT, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),
    dict(key="towed_boat_2", name="Goblin Rowboat", look=ROWBOAT, level=1, side="neutral", role="ambient",
         unit_flags=0x02000002, summoned=True),
    dict(key="bubbles", name="Bubbles", look="trigger", level=1, role="ambient", unit_flags=0x02000002, summoned=True),
    dict(key="m9_director", name="Lordamere Lake", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="m9_director", phase=M9,
         watch=(18, [("music", NAGA_MOMENT), ("face", "vashj9", "kael9"), ("visual", "vashj9", WATER)], 150000)),

    # -- memory m10: A Dark Covenant -----------------------------------------------------------------------------------
    dict(key="vashj10", name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         language="universal", gossip="Speak quickly. The prince is watching us, and so is his master's dog.",
         at="vashj10_lake", facing=0.4, phase=M10, respawn=20, idle=[("state", "self", "swim_idle")]),
    dict(key="kael10", name="Prince Kael'thas Sunstrider", subname="Prince of Quel'Thalas", look="kaelthas", level=40,
         role="ambient", untouchable=True, language="universal", at="kael10", facing=0.7, phase=M10, respawn=40,
         idle=[("every", 33000, [("face", "self", "slope"), ("emote", "self", "talk")])]),
    dict(key="elf10_a", name="Blood Elf of Quel'Thalas", look=BE_DEF, equip=(20835, 20841, 0), level=34, role="ambient",
         untouchable=True, language="universal", at="e10_1", facing=0.7, phase=M10, respawn=30,
         idle=[("state", "self", "ready")]),
    dict(key="elf10_b", name="Blood Elf of Quel'Thalas", look=BE_F, equip=(20835, 20841, 0), level=34, role="ambient",
         untouchable=True, language="universal", at="e10_2", facing=0.7, phase=M10, idle=[("state", "self", "ready")]),
    dict(key="elf10_c", name="Blood Elf of Quel'Thalas", look=BE_RANGER, equip=(20835, 20841, 0), level=34,
         role="ambient", untouchable=True, language="universal", at="e10_3", facing=0.7, phase=M10, respawn=30,
         idle=[("state", "self", "ready")]),
    dict(key="naga10", name="Naga of Lady Vashj", plural="Lady Vashj's naga", look="coilfang_myrmidon",
         looks=["coilfang_siren"], equip=(15910, 0, 0), size=1.1, level=32, role="ambient", untouchable=True,
         at=["n10_1", "n10_2"], facing=0.7, phase=M10, idle=[("state", "self", "ready_thrown")]),
    dict(key="scourge", name="Scourge of Lordaeron", plural="Scourge", look=GHOUL, looks=[GHOUL_RED, SKELETON], level=(35, 36),
         side="hostile", role="enemy", type="undead", phase=M10, respawn=25, wander=4.0, abilities=[(11976, 8000)],
         at=["sc_1", "sc_2", "sc_3", "sc_4", "sc_5", "sc_6", "sc_7", "sc_8", "sc_9", "sc_10", "sc_11", "sc_12", "sc_13",
             "sc_14"]),
    dict(key="dalvengyr", name="Dalvengyr", subname="Dreadlord of the Scourge", look=DREADLORD, level=37, health=4.0,
         damage=1.4, side="hostile", role="enemy", type="demon", caster=True, language="universal", phase=M10,
         at="dalvengyr", facing=3.6, respawn=60, abilities=[(9613, 7000), (11639, 14000)],
         watch=(32, [("face", "self", "player"), ("emote", "self", "battle_roar"),
                     ("yell", "self", "Your soul is mine!", None, "HeroDreadlordWarcry1")], 60000),
         at_health=(25, [("yell", "kael10", "By fire be purged!", "spell", "KaelYesAttack1"),
                         ("emote", "kael10", "spell"), ("visual", "self", FIRE_HIT), ("emote", "self", "wound")])),
    # the young spell breaker who runs in with the news (Taelon, younger: invented)
    dict(key="taelon_young", name="Taelon Emberveil", subname="Spell Breaker of Quel'Thalas", look="taelon",
         equip=(20835, 30984, 0), speed=1.4, level=30, role="ambient", untouchable=True, language="universal",
         summoned=True),
    dict(key="garithos10", name="Grand Marshal Garithos", subname="Commander of the Alliance in Lordaeron",
         look="garithos", equip=(25825, 43085, 0), level=40, role="ambient", untouchable=True, language="universal",
         summoned=True),
    dict(key="soldier10_a", name="Lordaeron Soldier", look=FOOTMAN, equip=(25825, 31200, 0), level=34, role="ambient",
         untouchable=True, language="universal", summoned=True),
    dict(key="soldier10_b", name="Lordaeron Soldier", look=SENTRY, equip=(25825, 31200, 0), level=34, role="ambient",
         untouchable=True, language="universal", summoned=True),
    dict(key="elf10_led", name="Blood Elf of Quel'Thalas", look=BE_DEF, level=34, role="ambient", untouchable=True,
         language="universal", summoned=True),
    dict(key="elf10_led_2", name="Blood Elf of Quel'Thalas", look=BE_RANGER, level=34, role="ambient", untouchable=True,
         language="universal", summoned=True),
    dict(key="kael10_led", name="Prince Kael'thas Sunstrider", subname="Prince of Quel'Thalas", look="kaelthas", level=40,
         role="ambient", untouchable=True, language="universal", summoned=True),

    # -- memory m11: The Dungeons of Dalaran ---------------------------------------------------------------------------
    dict(key="vashj11", name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         language="universal", at="vashj11_under", facing=0.6, phase=M11, respawn=30,
         idle=[("every", 41000, [("emote", "self", "spell"), ("visual", "self", WATER)])]),
    dict(key="kael11", name="Prince Kael'thas Sunstrider", subname="Prisoner of Dalaran", look="kaelthas", level=40,
         role="ambient", untouchable=True, language="universal", at="kael_cell", facing=3.1, phase=M11, respawn=40,
         idle=[("every", 45000, [("emote", "self", "talk")])]),
    dict(key="lieutenant", name="Blood Elf Lieutenant", plural="the prince's lieutenants", look=19824,
         looks=[BE_MAGISTER, 21180, BE_RANGER], level=35, role="ambient", untouchable=True, language="universal",
         at=["cell_1", "cell_2", "cell_3", "cell_4"], facing=2.4, phase=M11, respawn=60, idle=[("state", "self", "sit")]),
    dict(key="lieutenant_free", name="Blood Elf Lieutenant", look=19824, looks=[BE_MAGISTER], level=35, role="ambient",
         untouchable=True, language="universal", summoned=True, idle=[("state", "self", "ready")]),
    dict(key="jailer", name="Dalaran Jailer", plural="Dalaran jailers", look=JAILOR_A, looks=[JAILOR_B, SHIELD_GUARD],
         equip=(25124, 0, 0), level=(36, 37), side="hostile", role="enemy", language="universal", phase=M11, respawn=30,
         abilities=[(25710, 7000)], at=["j_1", "j_2", "j_3", "j_4", "j_5", "j_6", "j_7", "j_8", "kg_1", "kg_2"],
         wander=3.0),
    dict(key="archmage_ghost", name="Ghostly Archmage", plural="Ghostly Archmagi", look=GHOST, level=37, side="hostile",
         role="enemy", type="undead", caster=True, language="universal", phase=M11, respawn=40,
         abilities=[(13748, 5000), (11831, 16000)], at=["gh_1", "gh_2", "gh_3", "gh_4", "gh_5"], wander=5.0,
         idle=[("every", 9000, [("visual", "self", GHOSTLY)])]),
    dict(key="kassan", name="Jailor Kassan", subname="Warden of Dalaran's Cells", look=JAILOR_BIG, size=1.25,
         equip=(25124, 31200, 0), level=37, health=3.0, damage=1.3, side="hostile", role="enemy", language="universal",
         phase=M11, at="kassan", facing=5.6, respawn=60, abilities=[(845, 9000), (8242, 14000)],
         watch=(25, [("face", "self", "player"), ("yell", "self", "Back in your cells, all of you! Guards!", "shout")], 45000),
         at_health=(35, [("yell", "kael11", "Alright, men. Pull back, back to the portal!", None, "KaelWarcry1"),
                         ("wait", 3500),
                         ("say", "vashj11", "Now, young prince, we take one final step towards destiny.", "talk")])),
    dict(key="guard_marcus", name="Guard Marcus", subname="Dalaran's Cells", look=SHIELD_GUARD, equip=(25825, 31200, 0),
         level=35, role="ambient", untouchable=True, language="universal", summoned=True),
    dict(key="guard_trogdar", name="Guard Trogdar", subname="Dalaran's Cells", look=FOOTMAN, equip=(25825, 31200, 0),
         level=35, role="ambient", untouchable=True, language="universal", summoned=True),
    dict(key="naga11", name="Naga of Lady Vashj", look="coilfang_myrmidon", equip=(15910, 0, 0), size=1.1, level=32,
         role="ambient", untouchable=True, summoned=True, idle=[("state", "self", "ready_thrown")]),

    # -- memory m12: The Crossing ---------------------------------------------------------------------------------------
    dict(key="vashj12", name="Lady Vashj", look="vashj", size=1.4, level=40, role="quest", untouchable=True,
         language="universal", at="vashj12", facing=3.14, phase=M12, respawn=30,
         gossip="Keep your eyes on the street. The light will look after itself.",
         idle=[("state", "self", "channel_directed"), ("every", 29000, [("visual", "self", GLOW_PURPLE)])]),
    dict(key="kael12", name="Prince Kael'thas Sunstrider", subname="Prince of Quel'Thalas", look="kaelthas", level=40,
         role="ambient", untouchable=True, language="universal", at="kael12", facing=0.2, phase=M12, respawn=60,
         idle=[("every", 34000, [("emote", "self", "talk")])]),
    dict(key="engineer12", name="Engineer Faelan Brightspire", subname="Engineer of Quel'Thalas", look=BE_DEF,
         equip=(5956, 0, 0), level=35, role="quest", untouchable=True, language="universal", at="engineer12",
         facing=0.4, phase=M12, gossip="Dalaran's stones remember being walls. We only have to remind them.",
         idle=[("state", "self", "work")]),
    dict(key="defender12", name="Blood Elf Defender", plural="the prince's defenders", look=BE_DEF, looks=[BE_RANGER, BE_F],
         equip=(20835, 20841, 0), level=36, role="ambient", untouchable=True, language="universal",
         at=["d12_1", "d12_2", "d12_3", "d12_4"], facing=0.0, phase=M12, idle=[("state", "self", "ready")]),
    # Taelon's brother, who held the square and didn't come through (invented)
    dict(key="aelthir", name="Aelthir Emberveil", subname="Spell Breaker of Quel'Thalas", look="taelon",
         equip=(20835, 30984, 0), level=36, role="ambient", untouchable=True, language="universal", at="aelthir",
         facing=0.0, phase=M12, respawn=120, idle=[("state", "self", "ready")]),
    dict(key="naga12", name="Naga of Lady Vashj", plural="Lady Vashj's naga", look="coilfang_siren",
         looks=["coilfang_myrmidon"], size=1.05, level=34, role="ambient", untouchable=True, at=["n12_1", "n12_2"],
         facing=0.0, phase=M12, idle=[("state", "self", "channel")]),
    dict(key="arcane_tower", name="Arcane Tower", look=DALARAN_CRYSTAL, scale=0.6, level=37, role="ambient",
         type="mechanical", turret=True, abilities=[(15124, 2500)], detection=30.0, summoned=True,
         idle=[("every", 6000, [("visual", "self", GLOW_PURPLE)])]),
    dict(key="bearer", name="Explosives Bearer", plural="Explosives Bearers", look=SENTRY, looks=[FOOTMAN],
         equip=(2884, 0, 0), level=38, side="hostile", role="enemy", language="universal", phase=M12, respawn=25,
         abilities=[(11976, 8000)], at=["eb_1", "eb_2", "eb_3", "eb_4", "eb_5", "eb_6", "eb_7", "eb_8"], wander=4.0),
    dict(key="garithos12", name="Grand Marshal Garithos", subname="Commander of the Alliance in Lordaeron",
         look="garithos", equip=(25825, 43085, 0), level=40, role="ambient", untouchable=True, language="universal",
         summoned=True),
    dict(key="wave_footman", name="Garithos's Footman", plural="Garithos's footmen", look=FOOTMAN, looks=[SENTRY],
         equip=(25825, 31200, 0), level=38, side="hostile", role="enemy", language="universal", summoned=True,
         abilities=[(25710, 7000)], idle=[("every", 2000, [("move", "self", "portal_front", "run")])]),
    dict(key="wave_beast", name="Beast from Garithos's Cages", plural="Garithos's beasts", look=BEAR, looks=[WOLF],
         level=38, side="hostile", role="enemy", type="beast", summoned=True, abilities=[(11976, 6000)],
         idle=[("every", 2000, [("move", "self", "portal_front", "run")])]),
    dict(key="exodus_1", name="Elf of Quel'Thalas", look=BE_M, level=30, role="ambient", untouchable=True,
         language="universal", summoned=True),
    dict(key="exodus_2", name="Elf of Quel'Thalas", look=BE_F, level=30, role="ambient", untouchable=True,
         language="universal", summoned=True),
    dict(key="exodus_3", name="Elf of Quel'Thalas", look=BE_MAGISTER, level=30, role="ambient", untouchable=True,
         language="universal", summoned=True),
    # the light at the portal's mouth: whoever steps into it goes white
    dict(key="portal_glow", name="The Portal", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="portal_mouth", phase=M12, watch=(5, [("aura", "player", "the_light"), ("sound", "player", 3090)], 6000)),
]

OBJECTS = [
    # -- the present ---------------------------------------------------------------------------------------------------
    dict(key="totem", model=TOTEM, name="Valormok's Totem", at="totem", kind="doodad", scale=1.4, facing=0.6),
    dict(key="hung_token", model=TOKEN_BANNER, name="War-Token", kind="doodad", scale=0.3),
    dict(key="cart", model=BROKEN_CART, name="Overturned Cart", at="cart", kind="doodad", facing=1.2, phase=HOLLOW),
    dict(key="orc_skull", model=ORC_SKULL, name="Bones", at=["skull_1", "skull_2"], kind="doodad", phase=HOLLOW),
    dict(key="grunt_bones", model=BONES, name="Fallen Grunt's Bones", kind="loot", loot=[("war_token", 1, 1)],
         quest="ch6_lost_guard", respawn=40, phase=HOLLOW,
         at=["bones_1", "bones_2", "bones_3", "bones_4", "bones_5", "bones_6", "bones_7", "bones_8"]),
    dict(key="dig_tent", model=EXCAVATION_TENT, name="Excavation Tent", at="dig_tent", kind="doodad", facing=2.0,
         phase=HOLLOW),
    dict(key="dig_crate", model=BE_CRATE, name="Blood Elf Crate", at=["dig_crates", "vtab_1"], kind="doodad", phase=HOLLOW),
    dict(key="dig_banner", model=BE_BANNER, name="Banner of the Sin'dorei", at=["dig_banner", "page_2"], kind="doodad",
         facing=3.0, phase=HOLLOW),
    dict(key="dig_stone", model=RUNE_TABLET, name="Highborne Tablet", at=["dig_stone_1", "dig_stone_2", "dig_stone_3",
                                                                          "vtab_2"], kind="doodad", phase=HOLLOW),
    dict(key="vaelos_tent", model=HE_TENT, name="Magister's Tent", at="vaelos_tent", kind="doodad", facing=5.6,
         phase=HOLLOW),
    dict(key="vaelos_books", model=BE_BOOK, name="Highborne Folio", at="vaelos_books", kind="doodad", phase=HOLLOW),
    dict(key="pearl_box", model=BE_CRATE_2, name="Magister's Pearl Box", at="pearl_box", kind="use", quest="ch6_vaelos",
         scale=0.55, respawn=60, phase=HOLLOW, goal="Pearl box opened",
         beats=[("give", "pearl_box", 1), ("sound", "player", CHEST), ("move", "taelon_lake", "vaelos", "walk"),
                ("wait", 2500), ("face", "taelon_lake", "pearl_box"), ("emote", "taelon_lake", "kneel"),
                ("visual", "taelon_lake", ARCANE_BURST), ("wait", 2200), ("emote", "taelon_lake", "wound"),
                ("sound", "taelon_lake", GEMS), ("wait", 1600), ("emote", "taelon_lake", "no"), ("wait", 1500),
                ("evade", "taelon_lake")]),
    dict(key="circle", model=RITUAL_CIRCLE, name="Summoning Circle", at="circle", kind="doodad", scale=1.2, phase=HOLLOW),
    dict(key="summoning_page", model=OPEN_BOOK, name="Torn Page of the Tome", kind="use", quest="ch6_tome", scale=0.9,
         respawn=60, phase=HOLLOW, at=["page_1", "page_2", "page_3"], goal="Torn page burned",
         beats=[("sound", "player", PAGE), ("summon", "half_imp", "circle", 7), ("wait", 600),
                ("visual", "half_imp", FEL_PORTAL), ("sound", "half_imp", 7594), ("wait", 3500),
                ("visual", "half_imp", FEL_HIT), ("despawn", "half_imp")]),
    dict(key="lookout_fire", model=CAMPFIRE, name="Lookout's Fire", at="lookout_fire", kind="doodad", phase=HOLLOW),
    dict(key="lookout_banner", model=HORDE_BANNER, name="Horde Banner", at="lookout_banner", kind="doodad", facing=3.6,
         phase=HOLLOW),
    dict(key="wine_bottle", model=BOTTLE, name="Bottle of Silvermoon Wine", kind="doodad", scale=1.4),

    # -- memory m9 -------------------------------------------------------------------------------------------------------
    dict(key="m9_tent", model=HUMAN_TENT, name="Alliance Tent", at=["m9_tent_1", "m9_tent_2"], kind="doodad", facing=2.2,
         phase=M9),
    dict(key="m9_lordaeron", model=LORDAERON_BANNER, name="Banner of Lordaeron", at="m9_banner_1", kind="doodad",
         facing=3.3, phase=M9),
    dict(key="m9_sunstrider", model=BE_BANNER, name="Banner of Quel'Thalas", at="m9_banner_2", kind="doodad",
         facing=3.3, phase=M9),
    dict(key="m9_fire", model=CAMPFIRE, name="Campfire", at="m9_fire", kind="doodad", phase=M9),
    dict(key="m9_crates", model=BE_CRATE, name="Supplies", at="m9_crates", kind="doodad", phase=M9),
    dict(key="yard_tent", model=GOBLIN_TENT, name="Shipwright's Tent", at="yard_tent", kind="doodad", facing=0.3, phase=M9),
    dict(key="yard_lumber", model=LUMBER, name="Lumber", at="yard_lumber", kind="doodad", phase=M9),
    dict(key="yard_wreck", model=WRECK, name="Wrecked Rowboat", at="yard_wreck", kind="doodad", facing=1.0, phase=M9),
    dict(key="yard_tnt", model=TNT_WAGON, name="Goblin Wagon", at="yard_tnt", kind="doodad", facing=4.0, phase=M9),
    dict(key="rowboat", model=GO_ROWBOAT, name="Goblin Rowboat", kind="use", quest="ch6_shipyard", respawn=90, phase=M9,
         at=["row_1", "row_2"], facing=0.2, goal="Rowboat taken in tow",
         beats=[("sound", "player", "splash"), ("visual", "player", WATER), ("face", "shipwright", "player"),
                ("yell", "shipwright", "HEY! That's MY boat! Do you have any idea what a boat costs in a war?!", "shout"),
                ("sound", "shipwright", GOBLIN_ANGRY), ("wait", 2500), ("emote", "shipwright", "cry")]),
    dict(key="leaky_boat", model=GO_ROWBOAT, name="Goblin Rowboat", kind="use", quest="ch6_shipyard", respawn=90,
         phase=M9, at="leaky", facing=5.9, goal="The third rowboat (it sank)",
         beats=[("sound", "player", "splash_big"), ("summon", "bubbles", "sink", 8), ("wait", 400),
                ("visual", "bubbles", WATER), ("wait", 1200), ("visual", "bubbles", 59562),
                ("face", "shipwright", "leaky"), ("emote", "shipwright", "cry"), ("sound", "shipwright", GOBLIN_WAIL),
                ("wait", 1800), ("say", "vashj9", "Brilliant.", "talk", "LadyVashjYes3")]),
    dict(key="observatory", model=SCRYING_ORB, name="Arcane Observatory", at=["obs_1", "obs_2", "obs_3"], kind="doodad",
         scale=1.6, phase=M9),
    dict(key="lens", model=SCRYING_ORB_SMALL, name="Cracked Focusing Lens", kind="use", quest="ch6_observatories",
         scale=0.6, respawn=90, phase=M9, at=["lens_1", "lens_2", "lens_3"], goal="Observatory repaired",
         beats=[("sound", "player", HAMMER), ("emote", "engineer9", "work"), ("wait", 1200), ("sound", "player", HAMMER),
                ("wait", 1200), ("visual", "engineer9", ARCANE_BURST), ("emote", "engineer9", "talk"),
                ("say", "garithos9", "I hate working with these... people.", "rude", "GarithosWhat3")]),

    # -- memory m11 ------------------------------------------------------------------------------------------------------
    dict(key="m11_cell", model=PRISON_CELL, name="Enchanted Cell", kind="doodad", phase=M11, scale=1.1,
         at=["kael_cell", "cell_1", "cell_2", "cell_3", "cell_4"], facing=2.4),
    dict(key="m11_gate", model=PRISON_GATE, name="The Prison Gate", at="gate", kind="doodad", facing=5.6, phase=M11),
    dict(key="m11_torch", model=TORCH_OBJ, name="Torch", at=["torch_11_1", "torch_11_2"], kind="doodad", phase=M11),
    dict(key="cell_lock", model=CELL_LOCK, name="Enchanted Lock", kind="use", quest="ch6_lieutenants", scale=0.8,
         respawn=60, phase=M11, at=["lock_1", "lock_2", "lock_3", "lock_4"], goal="Lieutenant freed",
         beats=[("sound", "player", 6616), ("visual", "lieutenant", ARCANE_BURST), ("despawn", "lieutenant"),
                ("summon", "lieutenant_free", "rally", 30), ("wait", 800),
                ("yell", "lieutenant_free", "Free! Up, brothers, up! The prince is out!", "shout")]),

    # -- memory m12 ------------------------------------------------------------------------------------------------------
    dict(key="m12_portal", model=DARK_PORTAL, name="The Dimensional Gate", at="portal", kind="doodad", facing=0.0,
         scale=1.2, phase=M12),
    dict(key="portal_light", model=PORTAL_LIGHT, name="The Portal's Light", kind="doodad", scale=2.2),
    dict(key="m12_banner", model=BE_BANNER, name="Banner of Quel'Thalas", at=["m12_banner_1", "m12_banner_2"],
         kind="doodad", facing=0.0, phase=M12),
]

ITEMS = [
    # what quests ask for and hand over
    dict(key="pearl_box", name="Magister's Pearl Box", icon="item:4632",
         description="Four pearls on blue silk. They hum, all four, slightly out of tune with each other."),
    dict(key="towline", name="Towline", icon="item:33069", description="Goblin rope. Probably not stolen. Probably."),
    dict(key="wrench", name="Engineer's Wrench", icon="item:7343",
         description="An elven wrench, engraved. Who engraves a wrench?"),
    dict(key="war_token", name="Valormok War-Token", icon="item:14544", stack=6,
         description="Iron, stamped with Valormok's mark, cold from lying on the road."),
    # rewards (the game's quests' greens at these levels; Taelon's signet and wine, the bible's)
    dict(key="ridge_cord", name="Ridgewatch Cord", kind="armor:cloth:waist", quality=2, level=34,
         stats=[("int", 7), ("spi", 5)]),
    dict(key="ridge_belt", name="Ridgewatch Belt", kind="armor:leather:waist", quality=2, level=34,
         stats=[("agi", 8), ("sta", 5)]),
    dict(key="ridge_girdle", name="Ridgewatch Girdle", kind="armor:mail:waist", quality=2, level=34,
         stats=[("str", 7), ("sta", 6)]),
    dict(key="lordamere_mantle", name="Lordamere Mantle", kind="armor:cloth:shoulder", quality=2, level=35,
         stats=[("int", 8), ("spi", 6)]),
    dict(key="lordamere_spaulders", name="Lordamere Spaulders", kind="armor:leather:shoulder", quality=2, level=35,
         stats=[("agi", 9), ("sta", 6)]),
    dict(key="lordamere_pauldrons", name="Lordamere Pauldrons", kind="armor:mail:shoulder", quality=2, level=35,
         stats=[("str", 8), ("sta", 7)]),
    dict(key="covenant_trident", name="Covenant Trident", kind="weapon:spear", quality=2, level=36,
         stats=[("str", 15), ("sta", 11)]),
    dict(key="witch_sting", name="The Witch's Sting", kind="weapon:bow", quality=2, level=36, stats=[("agi", 6), ("sta", 4)],
         description="Taste my sting!"),
    dict(key="covenant_staff", name="Staff of the Dark Covenant", kind="weapon:staff", quality=2, level=36,
         stats=[("int", 15), ("spi", 11)]),
    dict(key="totem_cuffs", name="Totem-Keeper's Cuffs", kind="armor:cloth:wrist", quality=2, level=36,
         stats=[("int", 5), ("spi", 5)]),
    dict(key="bloodfist_wraps", name="Bloodfist Wristwraps", kind="armor:leather:wrist", quality=2, level=36,
         stats=[("agi", 6), ("sta", 4)]),
    dict(key="guard_bracers", name="Valormok Guard's Bracers", kind="armor:mail:wrist", quality=2, level=36,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="damp_leggings", name="Dungeon-Damp Leggings", kind="armor:cloth:legs", quality=2, level=37,
         stats=[("int", 11), ("sta", 7), ("spi", 6)]),
    dict(key="jailbreak_breeches", name="Jailbreaker's Breeches", kind="armor:leather:legs", quality=2, level=37,
         stats=[("agi", 13), ("sta", 9)]),
    dict(key="jailor_legguards", name="Kirin Tor Jailor's Legguards", kind="armor:mail:legs", quality=2, level=37,
         stats=[("str", 12), ("sta", 10)]),
    dict(key="signet", name="Emberveil Signet", icon="item:30810", kind="ring", quality=3, level=37,
         stats=[("sta", 8), ("int", 7), ("spi", 6)],
         description="A Silvermoon house's ring, warm from the hand that pulled it off. It was never meant to be sold."),
    dict(key="crossing_robe", name="Robe of the Crossing", kind="armor:cloth:chest", quality=2, level=38,
         stats=[("int", 12), ("sta", 9), ("spi", 7)]),
    dict(key="crossing_jerkin", name="Jerkin of the Crossing", kind="armor:leather:chest", quality=2, level=38,
         stats=[("agi", 14), ("sta", 11)]),
    dict(key="crossing_hauberk", name="Hauberk of the Crossing", kind="armor:mail:chest", quality=2, level=38,
         stats=[("str", 13), ("sta", 11)]),
    dict(key="wine", name="Silvermoon Wine", kind="drink", level=35, icon="item:29454",
         description="Older than the Sunwell's fall. He left a bottle for her, and one for you."),
    dict(key="emberveil_buckler", name="Emberveil Buckler", kind="shield", quality=2, level=38,
         stats=[("sta", 8), ("str", 5)]),
    dict(key="tome_wand", name="Tome-Burner's Wand", kind="weapon:wand", quality=2, level=38, stats=[("int", 5), ("sta", 3)]),
    dict(key="page_cloak", name="Cloak of Burnt Pages", kind="armor:cloth:back", quality=2, level=38,
         stats=[("agi", 5), ("sta", 6)], description="It smells of ash and old paper, and very faintly of sulphur."),
    dict(key="boatman_boots", name="Bloodfist Boatman's Boots", kind="armor:mail:feet", quality=2, level=38,
         stats=[("str", 9), ("sta", 7)]),
    dict(key="tidewalker_boots", name="Tidewalker Boots", kind="armor:leather:feet", quality=2, level=38,
         stats=[("agi", 10), ("sta", 7)]),
    dict(key="dockside_slippers", name="Dockside Slippers", kind="armor:cloth:feet", quality=2, level=38,
         stats=[("int", 9), ("spi", 6)]),
    dict(key="cracked_pearl", name="Frost-Cracked Pearl", kind="neck", quality=2, level=38,
         stats=[("int", 7), ("spi", 5), ("sta", 4)], description="It was warm this morning."),
    dict(key="long_watch", name="Pendant of the Long Watch", kind="neck", quality=2, level=38,
         stats=[("agi", 8), ("sta", 6)]),
    dict(key="cold_choker", name="Choker of the Cold Pool", kind="neck", quality=2, level=38,
         stats=[("str", 8), ("sta", 6)]),
]

AURAS = [
    # stepping into the portal's light (6.26): the screen goes white for a breath
    dict(key="the_light", name="Into the Light", kind="screen", screen=502, seconds=3),
]

MEMORIES = [
    dict(key="m9", name="Misconceptions", whose="Isshara", bit="B",
         text="Isshara's memory, from a magister's box: Lordamere Lake, under the water, the day Vashj met the prince. "
              "What she saw, you see.",
         stage="m9_arrive", facing=0.3, centre="m9_centre", radius=115, pool="hollow_pool", pool_facing=0.83,
         singer="ch0:isshara", again="Sing Lordamere again. Let me go back under the lake."),
    dict(key="m10", name="A Dark Covenant", whose="Isshara", bit="C",
         text="Isshara's memory, from a magister's box: the prince's camp by the lake, the day the dead came. What she "
              "saw, you see.",
         stage="m10_arrive", facing=0.4, centre="m10_centre", radius=130, pool="hollow_pool", pool_facing=0.83,
         singer="ch0:isshara", again="Sing the prince's camp again."),
    dict(key="m11", name="The Dungeons of Dalaran", whose="Isshara", bit="B",
         text="Isshara's memory, from a magister's box: the cells under Dalaran, two days later. What she saw, you see.",
         stage="m11_arrive", facing=0.6, centre="m11_centre", radius=80, pool="hollow_pool", pool_facing=0.83,
         singer="ch0:isshara", again="Sing the dungeons again. Let me go back up through the water."),
    dict(key="m12", name="The Crossing", whose="Isshara", bit="A",
         text="Isshara's memory, from a magister's box: Dalaran's ruins, the portal square, the night of the Crossing. "
              "What she saw, you see.",
         stage="m12_arrive", facing=3.14, centre="m12_centre", radius=110, pool="hollow_pool", pool_facing=0.83,
         singer="ch0:isshara", again="Sing the Crossing again. Let me go back to the portal."),
]

QUESTS = [
    # 6.01: the Silvermoon envoy (Ag'tor is the game's: his quest window's gestures are his; the scene is Taelon's)
    dict(key="ch6_envoy", title="The Silvermoon Envoy", giver=AGTOR, ender="taelon", level=34, xp=8, tone="serious",
         prev="ch5:ch5_end",
         goal="Speak with the blood elf in red and gold who stands west of the naga's tent in Valormok.",
         text="Him. Red and gold, sword and shield, a face like he's smelling my camp. Silvermoon sent him after Rimtori's "
              "renegades, he says, and he wants to know who has been selling them songs. He asked about your kind. Not "
              "kindly. He stands by your envoy's tent and glares at it. Go and let him glare at you instead.",
         reward="Naga. Of course it would be a naga. ...I am Taelon Emberveil, of Silvermoon. I was at Dalaran, the night "
                "your Lady Vashj came up out of the sewers. I know exactly what you are. Say what you came to say.",
         details=["talk", "point"], reward_emotes=["no", "talk"],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "no"), ("wait", 1200),
                   ("say", "self", "Bal'a dash... naga. Anar'alah belore. Shorel'aran.", "rude"), ("wait", 3500),
                   ("say", "self", "Taelon Emberveil. Of Silvermoon. I was at Dalaran.", "talk"), ("wait", 3000),
                   ("face", "self", "envoy_tent"), ("wait", 2000), ("face", "self", "player")],
         poi=["taelon"]),

    # 6.02: Rimtori's diggers (hero): he walks down with you and fights beside you, and says nothing in between
    dict(key="ch6_diggers", title="Rimtori's Diggers", giver="taelon", ender="taelon_lake", level=34, xp=8, tone="serious",
         path="hero", prev="ch6_envoy", rep=[(911, 250)],
         interact=[("taelon_lake", "Go down to the dig with him.")], interact_goal="Taelon Emberveil at your side",
         interact_beats=[("face", "self", "player"), ("emote", "self", "ready1h"),
                         ("say", "self", "Keep out of my way.", "talk"), ("visual", "self", ARCANE_BURST),
                         ("follow", "self")],
         kill=[("digger", 6), ("warden", 4)],
         goal="Meet Taelon Emberveil at his watch on the ridge above Lake Mennar, south-east of Valormok; go down with him "
              "and kill 6 Thalassian Diggers and 4 Thalassian Wardens at Rimtori's dig on the lake's north shore.",
         text="Magus Rimtori took Silvermoon's coin and your warchief's trust and spent both on a hole in the ground. Her "
              "people dig at Lake Mennar for whatever the Highborne left there. I keep a watch on the ridge above them. Ten "
              "of them: the diggers and the wardens who stand over them. I'll be at my watch. Try to keep up.",
         progress="Still digging. Still breathing.",
         reward="...Adequate.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "toward_lake"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "ready1h"),
                 ("wait", 1200), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "dig"), ("emote", "self", "salute"), ("wait", 1500), ("face", "self", "player"),
                   ("emote", "self", "no"), ("wait", 1000), ("evade", "self")],
         poi=["taelon_post", "dig"]),

    # 6.03: pearls in a magister's box: he picks one up and puts it down as if it burned
    dict(key="ch6_vaelos", title="Pearls in a Magister's Box", giver="taelon_lake", ender="ch0:isshara", level=34, xp=8,
         tone="serious", prev="ch6_diggers", kill=[("vaelos", 1)], objects=[("pearl_box", 1)],
         choice=["ridge_cord", "ridge_belt", "ridge_girdle"],
         goal="Kill Magister Vaelos in his tent on Lake Mennar's west ridge, open the pearl box he keeps there, and take "
              "the pearls to Isshara at the Hollow.",
         text="Their magister keeps a tent on the west ridge, full of Highborne tablets and things that hum. Vaelos. He "
              "buys whatever the sea gives up and sends the best of it to Rimtori. Your kind's songs among it, I'm told. "
              "He is mine as much as yours. Walk with me.",
         progress="You carry something that sings. Give it here.",
         reward="Four. Four of mine, in a magister's box, on a land-walker's shelf, like sweets. ...This one is cold. "
                "Lordamere. I know a lake by its cold. Rest, little one, and then put your hands in the water.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("say", "self", "Walk with me.", "talk"), ("wait", 1200),
                 ("face", "self", "vaelos"), ("emote", "self", "point"), ("follow", "self")],
         complete=[("take", "pearl_box", 1), ("state", "self", "channel"), ("visual", "self", WATER),
                   ("sound", "self", "siren_hiss"), ("wait", 2000), ("emote", "self", "spell"), ("sound", "self", GEMS),
                   ("wait", 900), ("emote", "self", "spell"), ("sound", "self", GEMS), ("wait", 900),
                   ("emote", "self", "spell"), ("sound", "self", GEMS), ("wait", 900), ("emote", "self", "spell"),
                   ("sound", "self", GEMS), ("wait", 1200), ("state", "self", "none"), ("say", "self", "Four.", "talk")],
         poi=["vaelos", "hollow_pool"]),

    # 6.04: under Lordamere (M9, sung): Vashj floats among her naga, watching the camp
    dict(key="ch6_lordamere", title="Under Lordamere", giver="ch0:isshara", ender="ch0:isshara_young", level=34, xp=8,
         tone="serious", prev="ch6_vaelos", memory="m9", explore="m9_isshara", radius=9,
         goal="Touch the water while Isshara sings. In her memory, under Lordamere Lake, swim to young Isshara beside Lady "
              "Vashj.",
         text="After Dalaran, after the Eye, we had nowhere to go. Vashj took us down into a lake, and we lay on the bottom "
              "like stones and waited. The land-walkers made a camp on its shore and never once looked down. Hands in the "
              "water. Hold your breath, if it helps you.",
         progress="Here. Over here. Quietly.",
         reward="Shh. Not so close to the top. Look up there: humans in blue, and elves in red. Arguing. Lady Vashj has "
                "been watching them since dawn, and she hasn't moved a fin.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("music", NAGA_MOMENT), ("visual", "player", GLOW_BLUE), ("sound", "self", "siren_hiss"), ("wait", 3500),
                 ("relive", "m9"), ("wait", 2000), ("state", "self", "none"), ("unaura", "player", GLOW_BLUE)],
         complete=[("face", "self", "kael9"), ("emote", "self", "point"), ("wait", 1500), ("face", "vashj9", "kael9"),
                   ("say", "vashj9", "I grow anxious to act.", "talk", "LadyVashjWhat2"), ("wait", 2500),
                   ("face", "self", "player"), ("emote", "self", "shy")],
         poi=["m9_isshara"]),

    # 6.05: the goblin shipyard (funny): one boat sinks; "Brilliant."
    dict(key="ch6_shipyard", title="The Goblin Shipyard", giver="ch0:isshara_young", ender="ch0:isshara_young", level=34,
         xp=8, tone="funny", prev="ch6_lordamere", memory="m9", source="towline",
         objects=[("rowboat", 2), ("leaky_boat", 1)],
         goal="In Isshara's memory, swim to the wrecked goblin shipyard on the lake's south shore and take 3 of its "
              "rowboats in tow.",
         text="Lady Vashj wants boats. The goblins had a shipyard on the south shore until the dead came through it. The "
              "boats are still there, some of them. Take this line and tow them off the slip. If a goblin shouts at you, "
              "he's only a goblin. They always shout.",
         progress="Boats. Not driftwood. Boats.",
         reward="Two boats, and a third at the bottom of the lake. Lady Vashj said 'Brilliant.' I've known her ten "
                "thousand years. She meant it the other way.",
         details=["point", "laugh"], reward_emotes=["laugh", "talk"],
         accept=[("face", "self", "yard"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "laugh"), ("move", "vashj9", "vashj_watch_yard", "walk"), ("wait", 4000),
                 ("face", "vashj9", "yard")],
         complete=[("take", "towline", 1), ("emote", "self", "laugh"), ("wait", 1500), ("emote", "self", "no"),
                   ("wait", 1200), ("face", "self", "kael9"), ("move", "vashj9", "m9_vashj", "walk")],
         poi=["yard"]),

    # 6.06: a gesture of goodwill (a set piece): the boats come across behind her while she rises before the prince
    dict(key="ch6_goodwill", title="A Gesture of Goodwill", giver="ch0:isshara_young", ender="ch0:isshara_young",
         level=35, xp=8, tone="serious", prev="ch6_shipyard", memory="m9", explore="kael_shore", radius=9,
         goal="In Isshara's memory, bring the two goblin rowboats across the lake behind you to the shore below the "
              "land-walkers' camp, where Lady Vashj rises to meet the prince.",
         text="She's going up. Lady Vashj is going up out of the water to talk to them. To talk! Bring the boats across "
              "behind her, slowly, where they can see them. She says the boats will do half the talking.",
         progress="Slowly. Let them see the boats.",
         reward="She tripped. Did you see? On the way back in. On her own tail. Don't you dare laugh. I'm not laughing. "
                "I'm not.",
         details=["talk"], reward_emotes=["laugh", "no"],
         accept=[("summon", "towed_boat", "boat_a", 600), ("summon", "towed_boat_2", "boat_b", 600), ("wait", 600),
                 ("follow", "towed_boat"), ("follow", "towed_boat_2"), ("sound", "self", "splash"),
                 ("move", "self", "isshara_shore", "walk"), ("move", "vashj9", "vashj_rise", "walk"),
                 ("music", SILVERMOON), ("wait", 6000), ("sound", "vashj9", "splash_big"), ("visual", "vashj9", WATER),
                 ("face", "vashj9", "kael9"), ("face", "kael9", "vashj_rise"), ("state", "elf9", "ready"),
                 ("state", "soldier9", "ready")],
         complete=[("face", "kael9", "vashj_rise"),
                   ("yell", "kael9", "Naga! You fought for the demon Illidan!", "exclamation"), ("wait", 3500),
                   ("say", "vashj9", "We are on our own now, good prince. I am called Lady Vashj. My brethren and I come in "
                                     "peace, to offer you our aid.", "talk"), ("wait", 6500),
                   ("say", "kael9", "You have nothing I need, witch.", "talk"), ("wait", 2500),
                   ("move", "towed_boat", "boats_shore", "walk"), ("face", "vashj9", "boats_shore"), ("wait", 2500),
                   ("face", "vashj9", "kael9"),
                   ("say", "vashj9", "Is that so? I thought you might require boats to reach the observatories you seek.",
                    "talk"), ("wait", 5500),
                   ("say", "kael9", "And you would give these freely? Why should I trust you, my lady?", "talk"), ("wait", 4500),
                   ("say", "vashj9", "Our two races share a common ancestry, Kael. Now, against the undead, we share a "
                                     "common peril. These boats are merely a gesture of goodwill.", "talk"), ("wait", 8000),
                   ("say", "kael9", "Then I accept your offer. Thank you.", "bow"), ("wait", 2500),
                   ("move", "kael9", "kael9", "walk"), ("state", "elf9", "none"), ("state", "soldier9", "none"),
                   ("move", "vashj9", "vashj_stumble", "walk"), ("wait", 2500), ("emote", "vashj9", "stun"),
                   ("say", "vashj9", "Keep tripping over this damn tail!", None, "LadyVashjPissed3"), ("wait", 2000),
                   ("emote", "self", "laugh"), ("despawn", "towed_boat"), ("despawn", "towed_boat_2"),
                   ("move", "vashj9", "m9_vashj", "walk"), ("wait", 2500), ("move", "self", "m9_isshara", "walk")],
         poi=["kael_shore"]),

    # 6.07: observatories (boring): hold things for the engineers; Garithos stands on the shore with his arms folded
    dict(key="ch6_observatories", title="Observatories", giver="ch0:isshara_young", ender="ch0:isshara_young", level=35,
         xp=8, tone="boring", prev="ch6_goodwill", memory="m9", source="wrench", objects=[("lens", 3)],
         goal="In Isshara's memory, help the prince's engineers repair the 3 arcane observatories on the rim of the lake's "
              "bowl: fit the cracked focusing lens at each.",
         text="The prince's people want to read the stars from three towers round the lake. Something about finding "
              "their way to wherever they're going. Their engineers are hopeless with anything heavier than a book. Go "
              "and hold things for them. Yes, really. One of them gave me this for you.",
         progress="Hold it steady. Steady!",
         reward="Three. They didn't say thank you. The one with the wrench almost did. The human stood and watched the "
                "whole time with his arms folded, as if we were going to steal the lake.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "obs_1"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "talk"), ("move", "garithos9", "garithos_watch", "walk"),
                 ("wait", 1500), ("face", "self", "garithos9")],
         complete=[("take", "wrench", 1), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "obs_2"),
                   ("emote", "self", "point"), ("move", "garithos9", "garithos9", "walk")],
         poi=["obs_1", "obs_2", "obs_3"]),

    # 6.08: Garithos's warning (funny): "Never trust an elf!" "Inhuman beast!"; awake at the pool
    dict(key="ch6_warning", title="Garithos's Warning", giver="ch0:isshara_young", ender="ch0:isshara", level=35, xp=8,
         tone="funny", prev="ch6_observatories", memory="m9", wake=True, event="The Grand Marshal's warning heard",
         choice=["lordamere_mantle", "lordamere_spaulders", "lordamere_pauldrons"],
         goal="In Isshara's memory, stay in the shallows below the camp with her while the Grand Marshal speaks to the "
              "prince.",
         text="The human in blue and silver is the prince's commander. Garithos. He's coming down to the water, and he "
              "has seen us. Stay where you are. Let him look. Lady Vashj wants him to look.",
         progress="Stay still.",
         reward="'Inhuman beast.' He said it to you too? He said it to all of us, every day, for as long as we knew him. "
                "...I liked the boats. I'd forgotten the boats.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("move", "self", "isshara_shore", "walk"), ("move", "garithos9", "g_jab", "walk"), ("wait", 5000),
                 ("face", "garithos9", "kael9"), ("emote", "garithos9", "point"),
                 ("yell", "garithos9", "Never trust an elf!", "point", "GarithosPissed5"), ("emote", "kael9", "talk"),
                 ("wait", 3000), ("move", "garithos9", "g_shore", "walk"), ("wait", 3500), ("face", "garithos9", "isshara_shore"),
                 ("emote", "garithos9", "point"), ("yell", "garithos9", "Inhuman beast!", "rude", "GarithosYesAttack3"),
                 ("wait", 2500), ("move", "garithos9", "g_stalk", "walk"), ("face", "naga9", "g_stalk"),
                 ("face", "self", "g_stalk"), ("emote", "self", "laugh"), ("wait", 5000), ("credit", "ch6_warning"),
                 ("wait", 6000), ("move", "garithos9", "garithos9", "walk"), ("move", "self", "m9_isshara", "walk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("sound", "self", 6928),
                   ("visual", "self", WATER), ("sound", "self", "pickup_water"), ("wait", 1500), ("emote", "self", "omnicast")],
         poi=["isshara_shore"]),

    # 6.09: Taelon listens: he comes to the Hollow under the Horde's banner and stands at the pool's edge
    dict(key="ch6_listens", title="Taelon Listens", giver="taelon", ender="ch0:isshara_young", level=35, xp=8,
         tone="serious", prev="ch6_warning", memory="m10",
         interact=[("ch0:isshara", "Tell her the land-walker will hear the next song.")], interact_goal="The song begun",
         interact_beats=[("summon", "taelon_visit", "taelon_from", 1800), ("wait", 600),
                         ("move", "taelon_visit", "taelon_edge", "walk"), ("face", "self", "taelon_from"),
                         ("face", "ch0:vyssa", "taelon_from"), ("face", "ch0:ssaveth", "taelon_from"),
                         ("state", "ch0:ssaveth", "ready_thrown"), ("wait", 8000), ("face", "taelon_visit", "pool"),
                         ("face", "self", "pool"), ("state", "self", "channel"), ("sound", "self", "siren_hiss"),
                         ("music", NAGA_MOMENT), ("visual", "player", GLOW_BLUE), ("wait", 3500), ("relive", "m10"),
                         ("wait", 2000), ("state", "self", "none"), ("unaura", "player", GLOW_BLUE)],
         goal="Bring Taelon Emberveil's word to Isshara at the Hollow and touch the water while she sings. In her memory, "
              "find young Isshara at the water's edge below the prince's camp.",
         text="Your keeper has the prince's songs in a box. Four of them. I will hear the next one. I don't care what it "
              "costs your people or how little you like it. Tell her. I'll stand at the edge of her water, and I will hear "
              "every note.",
         progress="Here. By the camp, at the water.",
         reward="The next day. The dead came out of the hills before breakfast and took two of the prince's camps. Lady "
                "Vashj says this is the moment. Stay close to me.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "player"), ("say", "self", "I will hear it.", "talk"), ("wait", 2000),
                 ("face", "self", "toward_hollow"), ("emote", "self", "no")],
         complete=[("face", "self", "slope"), ("emote", "self", "point"), ("music", BATTLE_1), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "talk")],
         poi=["hollow_pool", "m10_isshara"]),

    # 6.10: a dark covenant: Vashj rises before the prince again; her first shot
    dict(key="ch6_covenant", title="A Dark Covenant", giver="ch0:isshara_young", ender="ch0:isshara_young", level=35,
         xp=8, tone="serious", prev="ch6_listens", memory="m10", kill=[("scourge", 12)],
         goal="In Isshara's memory, kill 12 of the Scourge coming down the slope north of the prince's camp.",
         text="There, on the slope. Ghouls, and the bone-men behind them. The prince's people can't hold the shore alone. "
              "Lady Vashj is going up to him again. When she shoots, we go.",
         progress="More of them on the slope.",
         reward="Twelve. The elves fight like they're angry at something that isn't here. Lady Vashj noticed. She notices "
                "everything.",
         details=["point"], reward_emotes=["cheer", "talk"],
         accept=[("face", "self", "kael10"),
                 ("say", "kael10", "Those bases are lost. We'll just have to improvise.", "talk"), ("wait", 3500),
                 ("move", "vashj10", "vashj10_shore", "walk"), ("wait", 4500), ("sound", "vashj10", "splash_big"),
                 ("visual", "vashj10", WATER), ("face", "vashj10", "kael10"),
                 ("say", "vashj10", "Ishnu-dal-dieb, Prince Kael. We've come to join your fight against the vile dead.",
                  "talk"), ("wait", 5000), ("face", "kael10", "vashj10_shore"),
                 ("say", "kael10", "Greetings, Lady Vashj. I would welcome your aid gladly, but the commander I serve "
                                   "does not approve of your kind.", "talk"), ("wait", 6000),
                 ("say", "vashj10", "I do not see him here, sharing your peril. Let me bolster your forces with my own. If "
                                    "not, you and your brethren will surely fall.", "talk"), ("wait", 6500),
                 ("say", "kael10", "What you say is true. But... I... I accept your offer, Vashj.", "talk"), ("wait", 4500),
                 ("say", "vashj10", "Good. Let's get to it, then.", "talk"), ("wait", 2500),
                 ("face", "vashj10", "slope"), ("emote", "vashj10", "ready_bow"),
                 ("yell", "vashj10", "Taste my sting!", None, "LadyVashjYesAttack2"), ("sound", "scourge", UNDEAD_AGGRO),
                 ("emote", "naga10", "battle_roar"),
                 ("sound", "naga10", "naga_aggro"), ("face", "self", "slope"), ("emote", "self", "point")],
         complete=[("emote", "self", "cheer"), ("wait", 1500), ("face", "self", "vashj10_shore"), ("emote", "self", "talk")],
         poi=["slope"]),

    # 6.11: Dalvengyr: "Your soul is mine!"; "By fire be purged!"
    dict(key="ch6_dalvengyr", title="Dalvengyr", giver="ch0:isshara_young", ender="ch0:isshara_young", level=36, xp=8,
         tone="serious", prev="ch6_covenant", memory="m10", kill=[("dalvengyr", 1)],
         goal="In Isshara's memory, kill the dreadlord Dalvengyr on the slope above the prince's camp.",
         text="That thing on the slope isn't a ghoul. It talks. It's the one sending them. The prince is going up after "
              "it, and Lady Vashj says we go with him. Don't look at its eyes.",
         progress="It's still up there. I can hear it laughing.",
         reward="It screamed when it died. Not like a ghoul. Like something that had expected to live forever.",
         details=["point"], reward_emotes=["cheer"],
         accept=[("face", "self", "dalvengyr"), ("emote", "self", "point"), ("wait", 1200),
                 ("move", "kael10", "kael_fight", "run"), ("face", "self", "player"), ("emote", "self", "exclamation")],
         complete=[("move", "kael10", "kael10", "walk"), ("emote", "self", "cheer"), ("wait", 1500),
                   ("face", "self", "vashj10_shore"), ("emote", "self", "talk")],
         poi=["dalvengyr"]),

    # 6.12: the hunger (a set piece): stand by Vashj while she talks with the prince
    dict(key="ch6_hunger", title="The Hunger", giver="ch0:isshara_young", ender="ch0:isshara_young", level=36, xp=8,
         tone="serious", prev="ch6_dalvengyr", memory="m10", event="Lady Vashj's words with the prince heard",
         interact=[("vashj10", "Stand by her.")], interact_goal="Stood by Lady Vashj",
         interact_beats=[("face", "self", "kael10"), ("face", "kael10", "vashj10_shore"), ("music", SILVERMOON),
                         ("say", "kael10", "You have my thanks, Lady. This victory would not have been possible without "
                                           "your aid, though I fear I may have doomed myself by accepting it.", "talk"),
                         ("wait", 7000),
                         ("say", "self", "The human you serve trusts no race but his own. His sense of honor runs no "
                                         "deeper than his tolerance.", "talk"), ("wait", 6000),
                         ("say", "kael10", "It is loyalty and duty that bind me to him and to this... failing Alliance. "
                                           "But now those tenets seem as distant as our ruined homeland. All I know is "
                                           "that my brethren and I hunger for something more.", "talk"), ("wait", 9000),
                         ("say", "self", "Then perhaps, young Kael, it is time to find a new path... to power and glory.",
                          "talk"), ("wait", 5500),
                         ("say", "kael10", "I can't explain it exactly, but ever since our homeland was destroyed, my "
                                           "brethren and I have felt empty... almost drained of our spirit.", "talk"),
                         ("wait", 7000),
                         ("say", "kael10", "There is a hunger now that has... hardened our hearts.", "talk"), ("wait", 4500),
                         ("say", "self", "I know this hunger, Kael. Like us, your people are addicted to magic!", "talk"),
                         ("wait", 5000),
                         ("say", "self", "It flowed through your veins for over ten thousand years. And now, with the "
                                         "corruption of your land and the Sunwell that empowered you...", "talk"),
                         ("wait", 7000),
                         ("say", "kael10", "We have been cut off from our power, from our birthright! Without a new "
                                           "source of magic, my people will surely die.", "talk"), ("wait", 6000),
                         ("emote", "self", "spell"), ("visual", "self", GLOW_PURPLE),
                         ("say", "self", "There are other founts of power in this world, Kael. Demons, for instance.",
                          "talk"), ("wait", 5500),
                         ("say", "kael10", "You speak of madness, my lady. We will never be that desperate.", "talk"),
                         ("wait", 4500),
                         ("say", "self", "Your aversion is understandable. But still--", "talk"),
                         ("summon", "taelon_young", "sb_run", 40), ("wait", 600), ("move", "taelon_young", "sb_stop", "run"),
                         ("wait", 3500), ("face", "taelon_young", "kael10"),
                         ("yell", "taelon_young", "Prince Kael! Grand Marshal Garithos has arrived. He's brought a full "
                                                  "battalion with him.", "exclamation"), ("wait", 5000),
                         ("face", "kael10", "slope"),
                         ("say", "kael10", "My hunger for magic is clouding my judgment!", None, "KaelPissed2"),
                         ("wait", 2500), ("credit", "ch6_hunger")],
         goal="In Isshara's memory, stand beside Lady Vashj while she speaks with the prince after the battle.",
         text="Lady Vashj is going to talk to the prince. She asked for you. Me? No, she asked for you. Go and stand by "
              "her and don't say anything. She'll do the talking. She always does.",
         progress="Go on. Stand by her.",
         reward="Demons. She said demons, to his face, and he didn't walk away. He said never, and then he didn't walk "
                "away. ...Who was that, running? The young one in red?",
         details=["point", "shy"], reward_emotes=["question", "talk"],
         accept=[("face", "self", "vashj10_shore"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "shy")],
         complete=[("emote", "self", "question"), ("wait", 1500), ("face", "self", "sb_stop"), ("emote", "self", "talk")],
         poi=["vashj10_shore"]),

    # 6.13: arrested: watch from the reeds; "Our will shall be done."; awake at the pool
    dict(key="ch6_arrested", title="Arrested", giver="ch0:isshara_young", ender="ch0:isshara", level=36, xp=8,
         tone="serious", prev="ch6_hunger", memory="m10", wake=True, event="The prince's arrest seen from the reeds",
         goal="In Isshara's memory, hide in the reeds at the lake's north-west corner with Lady Vashj and watch what the "
              "Grand Marshal does.",
         text="Horns. Human horns, on the ridge. That's the battalion. Into the reeds with Lady Vashj, now, and keep your "
              "head under the leaves. Whatever they do to the elves, we didn't see it. We weren't here.",
         progress="Down. Stay down.",
         reward="Our will shall be done. She whispered it. I was close enough to hear, and I've never known whether she "
                "meant it as a promise or a threat. ...Your land-walker is still standing at my water. Look at his face.",
         details=["point"], reward_emotes=["talk"],
         accept=[("emote", "self", "point"), ("say", "self", "Horns. Into the reeds. Down!", "point"),
                 ("move", "self", "reeds_isshara", "run"), ("move", "vashj10", "reeds", "walk"), ("music", GLOOMY),
                 ("sound", "self", HORN), ("summon", "garithos10", "g10_arrive", 70), ("summon", "soldier10_a", "s10_1", 70),
                 ("summon", "soldier10_b", "s10_2", 70), ("wait", 800), ("move", "garithos10", "g10_camp", "walk"),
                 ("move", "soldier10_a", "e10_1", "walk"), ("move", "soldier10_b", "e10_3", "walk"), ("wait", 7000),
                 ("face", "garithos10", "kael10"),
                 ("yell", "garithos10", "The lesser races must be purged from the kingdom.", "point", "GarithosPissed2"),
                 ("wait", 4500), ("despawn", "elf10_a"), ("despawn", "elf10_c"), ("summon", "elf10_led", "e10_1", 40),
                 ("summon", "elf10_led_2", "e10_3", 40), ("despawn", "kael10"), ("summon", "kael10_led", "kael10", 50),
                 ("wait", 600), ("visual", "elf10_led", CHAINS), ("visual", "elf10_led_2", CHAINS),
                 ("visual", "kael10_led", CHAINS), ("sound", "kael10_led", CHAINS_SOUND), ("wait", 2000),
                 ("move", "soldier10_a", "led_away", "walk"), ("move", "elf10_led", "led_away", "walk"),
                 ("move", "soldier10_b", "led_away", "walk"), ("move", "elf10_led_2", "led_away", "walk"),
                 ("move", "kael10_led", "kael_led", "walk"), ("wait", 9000), ("face", "kael10_led", "lake"),
                 ("say", "kael10_led", "The Alliance has failed my people.", "talk", "KaelPissed4"), ("wait", 4000),
                 ("move", "kael10_led", "led_away", "walk"), ("move", "garithos10", "led_away", "walk"), ("wait", 3500),
                 ("whisper", "vashj10", "Our will shall be done.", None, "LadyVashjWhat3"), ("wait", 2500),
                 ("credit", "ch6_arrested"), ("wait", 6000), ("despawn", "vashj10"), ("move", "self", "m10_isshara", "walk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", WATER),
                   ("sound", "self", "pickup_water"), ("wait", 1200), ("face", "self", "taelon_edge"),
                   ("face", "taelon_visit", "pool")],
         choice=["covenant_trident", "witch_sting", "covenant_staff"],
         poi=["reeds"]),

    # 6.14: that was me: he sits down hard; he says it was him; he looks at Isshara for the first time
    dict(key="ch6_that_was_me", title="That Was Me", giver="ch0:isshara", ender="taelon", level=36, xp=8, tone="serious",
         prev="ch6_arrested",
         goal="Follow Taelon Emberveil back to Valormok.",
         text="He's been standing at my water with his arms folded since you went in. When the boy ran in shouting about "
              "Garithos, I heard him breathe in, and he hasn't breathed out since. Go after him, little one. Don't say "
              "anything clever.",
         reward="...I was young. I thought I was bringing him good news. That's all. That's all of it.",
         details=["talk"], reward_emotes=["no"],
         accept=[("despawn", "taelon_visit"), ("summon", "taelon_visit", "taelon_edge", 60), ("wait", 1200),
                 ("face", "self", "taelon_rock"), ("move", "taelon_visit", "taelon_rock", "walk"), ("wait", 3000),
                 ("state", "taelon_visit", "sit"), ("sound", "taelon_visit", "thud_water"), ("wait", 2000),
                 ("say", "taelon_visit", "That was me. The spell breaker who ran in. That was me.", "talk"), ("wait", 4500),
                 ("face", "taelon_visit", "isshara_bed"), ("wait", 3500), ("emote", "self", "talk"), ("wait", 3000),
                 ("state", "taelon_visit", "none"), ("move", "taelon_visit", "taelon_away", "walk"), ("wait", 12000),
                 ("despawn", "taelon_visit")],
         complete=[("face", "self", "player"), ("wait", 1500), ("state", "self", "sit"), ("wait", 6000),
                   ("state", "self", "none")],
         poi=["taelon"]),

    # 6.15: Valormok's lost guard (hero): the tokens hung on the totem; Taelon stands by and says nothing
    dict(key="ch6_lost_guard", title="Valormok's Lost Guard", giver=AGTOR, ender=AGTOR, level=36, xp=8, tone="serious",
         path="hero", prev="ch6_that_was_me", rep=[(76, 350)], choice=["totem_cuffs", "bloodfist_wraps", "guard_bracers"],
         use=[("war_token", "totem_use", 6,
               [("object", "hung_token", "totem_hang", 900), ("sound", "player", RING), ("face", "thokra", "totem"),
                ("emote", "thokra", "bow"), ("face", "taelon", "totem"), ("state", "taelon", "none")])],
         goal="Take the War-Tokens from the bones of Valormok's guard by the overturned cart on the road east of the camp, "
              "and hang 6 of them on Valormok's totem.",
         text="When Belgrom sent the elf-woman Rimtori to Azshara, he sent an orcish guard with her. Good grunts. She "
              "thanked them and killed them on the road east and left them for the birds. Their war-tokens are still on "
              "their bones. Bring them home. Hang them on the totem, where we can see them.",
         reward="Six. Gharn, Ruk, the twins, old Mazga... and the boy. That's all of them. ...The elf stood there the "
                "whole time and didn't say a word. Good. There was nothing to say.",
         details=["talk", "point"], reward_emotes=["talk", "salute"],
         poi=["road_east", "totem"]),

    # 6.16: damn sea water (funny; M11, sung): up through the sewer water
    dict(key="ch6_sea_water", title="Damn Sea Water", giver="ch0:isshara", ender="ch0:isshara_young", level=36, xp=8,
         tone="funny", prev="ch6_lost_guard", memory="m11", explore="m11_isshara", radius=7,
         goal="Touch the water while Isshara sings. In her memory, come up through the flooded stones under Dalaran's "
              "prison with Lady Vashj, and find young Isshara at the water's edge.",
         text="Two days later the prince and his people were in Dalaran's cells, waiting to be executed. Vashj went to "
              "get him. Through the sewers. She complained the whole way. Hands in the water, little one. You'll want to "
              "hold your nose.",
         progress="Up. Quietly. There are guards.",
         reward="Did you hear what she said? About her hair? Don't tell her I told you. Don't tell anyone, ever.",
         details=["talk"], reward_emotes=["laugh", "talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("music", SPOOKY), ("visual", "player", GLOW_BLUE), ("sound", "self", "siren_hiss"), ("wait", 3500),
                 ("relive", "m11"), ("wait", 2000), ("state", "self", "none"), ("unaura", "player", GLOW_BLUE)],
         complete=[("summon", "guard_marcus", "guard_1", 45), ("summon", "guard_trogdar", "guard_2", 45), ("wait", 800),
                   ("face", "guard_marcus", "guard_2"),
                   ("say", "guard_marcus", "Don't worry. This prison was built by the Kirin Tor to keep their pets from "
                                           "getting loose. The elves' magic is useless inside those enchanted cells.",
                    "talk"), ("emote", "guard_trogdar", "laugh"), ("sound", "guard_trogdar", HUMAN_LAUGH), ("wait", 6500),
                   ("move", "vashj11", "vashj_surface", "walk"), ("wait", 2500), ("sound", "vashj11", "splash_big"),
                   ("visual", "vashj11", GREEN_SPLASH),
                   ("say", "vashj11", "Damn sea water! I'll never get these coils out of my hair!", None, "LadyVashjPissed4"),
                   ("wait", 3500), ("face", "vashj11", "guard_1"), ("emote", "vashj11", "spell"),
                   ("visual", "guard_marcus", LIGHTNING), ("visual", "guard_trogdar", LIGHTNING),
                   ("visual", "guard_marcus", LIGHTNING_HIT), ("visual", "guard_trogdar", LIGHTNING_HIT),
                   ("wait", 700), ("state", "guard_marcus", "dead"), ("sound", "guard_marcus", HUMAN_DEATH),
                   ("state", "guard_trogdar", "dead"), ("sound", "guard_trogdar", 1326), ("wait", 1500),
                   ("move", "vashj11", "cell_door", "walk"), ("wait", 4000), ("emote", "vashj11", "attack2h"),
                   ("visual", "kael11", ARCANE_BURST), ("sound", "vashj11", 6616), ("wait", 1200),
                   ("move", "kael11", "kael_out", "walk"), ("emote", "self", "laugh")],
         poi=["m11_isshara"]),

    # 6.17: a darker path (a set piece): Vashj frees the prince, and offers him the portal
    dict(key="ch6_darker_path", title="A Darker Path", giver="ch0:isshara_young", ender="ch0:isshara_young", level=36,
         xp=8, tone="serious", prev="ch6_sea_water", memory="m11", event="The darker path offered",
         goal="In Isshara's memory, stand with Lady Vashj at the door of the prince's cell while she speaks to him.",
         text="She's at his cell. The door's in pieces and he's still standing there like he doesn't believe it. Come "
              "and listen. This is the part I always remember wrong.",
         progress="Listen.",
         reward="As you will. That's all she said. ...I always remember her saying more.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "cell_door"), ("music", SILVERMOON), ("face", "vashj11", "kael_out"),
                 ("face", "kael11", "cell_door"),
                 ("say", "vashj11", "Greetings, Kael. I assume we're not too late.", "talk"), ("wait", 3500),
                 ("say", "kael11", "On the contrary, Vashj. Your timing is impeccable. Once again, I am in your debt. But "
                                   "even if we free my brethren, there is nowhere to run. Garithos' forces outnumber us "
                                   "ten to one.", "talk"), ("wait", 9000),
                 ("say", "vashj11", "You stand at a dangerous crossroads. You can either stay here and be slaughtered by "
                                    "human hands... or choose a darker path... to freedom.", "talk"), ("wait", 7500),
                 ("say", "kael11", "What is this darker path?", "question"), ("wait", 2500),
                 ("say", "vashj11", "In the city above us stands a portal--a gateway that leads to other worlds.", "talk"),
                 ("wait", 5000),
                 ("say", "kael11", "Yes, I know it. The lich, Kel'Thuzad, opened it to bring Archimonde here.", "talk"),
                 ("wait", 5000), ("emote", "vashj11", "spell"), ("visual", "vashj11", FEL_SMOKE),
                 ("say", "vashj11", "Yes. My master, Illidan, awaits us on the other side of that portal! Lead your people "
                                    "to him, and he will forge you a new destiny. He will sate your people's burning "
                                    "hunger.", "talk"), ("wait", 9000),
                 ("say", "kael11", "Side with a rogue demon... or lead my people to their certain deaths. There is no "
                                   "choice here, Vashj. We'll have to free my lieutenants first. They'll be able to rally "
                                   "the others while we assault the exit.", "talk"), ("wait", 9500),
                 ("say", "vashj11", "As you will.", "talk"), ("wait", 2000), ("credit", "ch6_darker_path")],
         complete=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "lieutenants"), ("emote", "self", "point")],
         poi=["cell_door"]),

    # 6.18: the lieutenants: break the locks, kill the jailers; "That guard means to sound the alarm!"
    dict(key="ch6_lieutenants", title="The Lieutenants", giver="ch0:isshara_young", ender="ch0:isshara_young", level=37,
         xp=8, tone="serious", prev="ch6_darker_path", memory="m11", objects=[("cell_lock", 4)], kill=[("jailer", 8)],
         goal="In Isshara's memory, break the Enchanted Locks on the 4 cells along the beach to free the prince's "
              "lieutenants, and kill 8 of Dalaran's jailers.",
         text="Four of the prince's captains are in the cells along the wall, and the jailers have the keys and the "
              "horns. Break the locks. Lady Vashj says the enchantment was made against elves, not against something "
              "that was never an elf. That's us.",
         progress="Locks. Jailers. Quickly.",
         reward="Four. They went down the row shouting names, and the cells shouted back. I never heard elves shout like "
                "that before. I never heard them shout at all.",
         details=["point"], reward_emotes=["cheer", "talk"],
         accept=[("summon", "jailer", "alarm_from", 60), ("wait", 600), ("move", "jailer", "alarm_to", "run"),
                 ("face", "kael11", "alarm_from"),
                 ("yell", "kael11", "That guard means to sound the alarm! Stop him!", "point"), ("face", "self", "alarm_from"),
                 ("emote", "self", "point")],
         complete=[("emote", "self", "cheer"), ("wait", 1500), ("face", "self", "rally"), ("emote", "self", "talk")],
         poi=["lieutenants"]),

    # 6.19: ghosts of Dalaran: "Outstanding!"
    dict(key="ch6_ghosts", title="Ghosts of Dalaran", giver="ch0:isshara_young", ender="ch0:isshara_young", level=37,
         xp=8, tone="serious", prev="ch6_lieutenants", memory="m11", kill=[("archmage_ghost", 4)],
         goal="In Isshara's memory, kill 4 Ghostly Archmagi drifting between the cells.",
         text="Something else is down here. Pale. Mages, or what's left of mages, still guarding Dalaran's prison after "
              "Dalaran fell. The prince says they'll warn the jailor. They don't look like they'd warn anyone. They look "
              "like they'd rather eat you.",
         progress="They're still drifting. I can feel them, cold, through the water.",
         reward="The prince said 'Outstanding.' To us! He said it to us.",
         details=["point"], reward_emotes=["laugh", "cheer"],
         accept=[("music", HAUNTED), ("face", "self", "gh_2"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "shy"),
                 ("visual", "self", GLOW_BLUE)],
         complete=[("face", "kael11", "m11_isshara"), ("say", "kael11", "Outstanding!", "talk", "KaelYes2"), ("wait", 1500),
                   ("emote", "self", "laugh"), ("emote", "self", "cheer")],
         poi=["gh_2"]),

    # 6.20: Jailor Kassan; the way up is open; the fade
    dict(key="ch6_kassan", title="Jailor Kassan", giver="ch0:isshara_young", ender="ch0:isshara", level=37, xp=8,
         tone="serious", prev="ch6_ghosts", memory="m11", wake=True, kill=[("kassan", 1)],
         choice=["damp_leggings", "jailbreak_breeches", "jailor_legguards"],
         goal="In Isshara's memory, kill Jailor Kassan at the prison's gate.",
         text="The gate. Kassan holds the gate himself. He's the one with the big key and the bigger mouth. Kill him and "
              "the way up is open: the street, the city, the portal, all of it.",
         progress="The gate, little one.",
         reward="One final step towards destiny. She liked that line. She said it twice that week. ...Breathe. There's "
                "one more song in the box, and it's the one I don't want to sing.",
         details=["point"], reward_emotes=["talk"],
         accept=[("face", "self", "gate"), ("emote", "self", "point"), ("move", "kael11", "kael_gate", "walk"),
                 ("move", "vashj11", "vashj_gate", "walk"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", WATER),
                   ("sound", "self", "pickup_water"), ("emote", "self", "omnicast")],
         poi=["kassan"]),

    # 6.21a: sing it for him (hero): his brother died at the Crossing; he stands in the water to see his face
    dict(key="ch6_sing", title="Sing It for Him", giver="taelon", ender="ch0:isshara", level=37, xp=8, tone="serious",
         path="hero", exclusive=1, prev="ch6_kassan", rep=[(911, 500)],
         goal="Tell Isshara at the Hollow that Taelon Emberveil will stand in her water for the song of the Crossing.",
         text="There is a song in that box of the night we crossed. My brother was in the square. Aelthir. He held it "
              "with the others while the rest of us went through, and he didn't come through after. I didn't see him fall. "
              "I was already on the other side. If I stand in your keeper's water... I'll see his face again? Ask her. "
              "Please.",
         reward="Tell him yes. Tell him to take his gloves off; the water has to touch skin. And tell him: it already "
                "happened. Whatever he sees, it already happened, and he can't change it. They never listen to that part.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("face", "self", "toward_hollow"),
                 ("emote", "self", "no")],
         complete=[("face", "self", "taelon_from"), ("summon", "taelon_water", "taelon_from", 2400), ("wait", 600),
                   ("move", "taelon_water", "taelon_shallows", "walk"), ("wait", 11000), ("face", "taelon_water", "pool"),
                   ("emote", "taelon_water", "kneel"), ("sound", "taelon_water", "pickup_water"), ("wait", 1500),
                   ("state", "taelon_water", "kneel"), ("visual", "taelon_water", WATER), ("face", "self", "taelon_shallows"),
                   ("emote", "self", "talk")],
         poi=["hollow_pool"]),

    # 6.21b: the price of a song (menace): his signet, dropped in your palm without touching you
    dict(key="ch6_price", title="The Price of a Song", giver="taelon", ender="taelon", level=37, xp=8, tone="serious",
         path="menace", exclusive=1, prev="ch6_kassan", rep=[(911, -500)], rewards=["signet"],
         goal="Name Taelon Emberveil the price of the song of the Crossing.",
         text="There is a song in that box of the night we crossed. My brother was in the square. Aelthir. He held it "
              "while the rest of us went through, and he didn't come through after. I want to hear it. Your keeper sings "
              "for nothing, I'm told. You don't. Fine. Name it.",
         reward="There. My house's signet. My father's, and his father's, back to the founding of Silvermoon. Take it. "
                "Don't touch my hand. ...Tell her to sing.",
         details=["talk"], reward_emotes=["no"],
         accept=[("face", "self", "player"), ("emote", "self", "no"), ("wait", 2000), ("emote", "self", "talk"),
                 ("face", "self", "envoy_tent")],
         complete=[("face", "self", "player"), ("emote", "self", "no"), ("wait", 1500), ("sound", "self", RING),
                   ("emote", "self", "point"), ("wait", 1500), ("face", "self", "valormok_east"), ("emote", "self", "no")],
         poi=["taelon"]),

    # 6.22: we have reached the portal (a set piece): the song of the Crossing begins (M12); the portal opens
    dict(key="ch6_portal", title="We Have Reached the Portal", giver="ch0:isshara", ender="ch0:isshara_young", level=37,
         xp=8, tone="serious", prev="ch6_kassan", prev_any=["ch6_sing", "ch6_price"], explore="m12_isshara", radius=9,
         goal="Touch the water while Isshara sings. In her memory, come up into the portal square in Dalaran's ruins and "
              "find young Isshara by the portal.",
         text="The Crossing. The last of the four. Dalaran's ruins, the portal square, the night the elves went through "
              "to Illidan and the humans tried to stop them. Everyone who was there remembers a different part of it. I "
              "remember the light. Hands in the water.",
         progress="Here! By the portal!",
         reward="Look at it. Look at it! She's going to open it. Stay by me, and watch.",
         details=["talk"], reward_emotes=["point", "talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("face", "taelon_water", "pool"),
                 ("visual", "taelon_water", WATER), ("wait", 1500), ("state", "self", "channel"), ("music", NAGA_MOMENT),
                 ("visual", "player", GLOW_BLUE), ("sound", "self", "siren_hiss"), ("wait", 3500), ("relive", "m12"),
                 ("wait", 2000), ("state", "self", "none"), ("unaura", "player", GLOW_BLUE)],
         complete=[("face", "self", "portal"),
                   ("say", "kael12", "My brethren are assembled, Vashj. Now all we need to do is reach this portal of yours "
                                     "and--", "talk"), ("wait", 4500), ("face", "vashj12", "kael12"),
                   ("say", "vashj12", "Hold, good prince. We will need to keep the portal open long enough to usher everyone "
                                      "through. But Garithos' forces will likely attack it before we can make our escape.",
                    "talk"), ("wait", 8000),
                   ("say", "kael12", "Then I will hold him at bay. I'll buy you all the time you'll need.", "talk"),
                   ("wait", 4000), ("face", "kael12", "north_entry"),
                   ("yell", "kael12", "Quickly, my brethren, take your positions. Garithos' forces will be here any moment.",
                    "point"), ("state", "defender12", "ready"), ("wait", 4500), ("face", "vashj12", "portal"),
                   ("say", "vashj12", "We have reached the portal, Kael. Now we'll attempt to open it!", "spell"),
                   ("state", "vashj12", "channel_directed"), ("state", "naga12", "channel"), ("music", ANGELIC),
                   ("wait", 3000), ("visual", "vashj12", GLOW_PURPLE), ("wait", 3000), ("visual", "naga12", ARCANE_BURST),
                   ("wait", 2000), ("object", "portal_light", "portal", 2400), ("visual", "vashj12", ARCANE_MASSIVE),
                   ("sound", "vashj12", 3090), ("wait", 2500),
                   ("yell", "vashj12", "We've done it. The portal is open. Let the exodus begin!", "battle_roar"),
                   ("wait", 4000), ("face", "kael12", "vashj12"),
                   ("say", "kael12", "Well done, Vashj. If we build more strategic towers, we should be able to hold off "
                                     "Garithos' forces long enough for our people to get through.", "talk"), ("wait", 7500),
                   ("say", "vashj12", "You'd better be right. If the portal falls, none of us will survive!", "talk"),
                   ("wait", 2000), ("face", "self", "player"), ("emote", "self", "point")],
         poi=["hollow_pool", "m12_isshara"]),

    # 6.23: towers from ruins: the engineer's crystals at four plots; arcane towers rise
    dict(key="ch6_towers", title="Towers from Ruins", giver="engineer12", ender="engineer12", level=37, xp=8,
         tone="serious", prev="ch6_portal", memory="m12",
         turrets=[dict(npc="arcane_tower", at=["plot_1", "plot_2", "plot_3", "plot_4"], seconds=900,
                       goal="Arcane tower raised", model=GROUND_RUNE, name="Tower Plot", scale=0.9)],
         goal="In Isshara's memory, raise an arcane tower at each of the 4 tower plots marked round the portal square.",
         text="You there, naga. You have hands, and the prince says they can be trusted. Four plots, marked on the stones "
              "round the square. Wake the crystal at each and stand back. Well back. They wake up angry.",
         progress="Four plots. I can still count to four, even tonight.",
         reward="Four towers, humming. Whatever Garithos sends up those streets will have to walk through them first.",
         details=["talk", "point"], reward_emotes=["cheer", "talk"],
         accept=[("face", "self", "kael12"),
                 ("say", "self", "Prince Kael, the other engineers and I helped to build Dalaran's original defenses. We "
                                 "could salvage materials from these ruins and construct whatever defensive towers you "
                                 "need.", "talk"), ("wait", 7500), ("emote", "kael12", "talk"), ("face", "self", "plot_1"),
                 ("emote", "self", "point"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("face", "self", "kael12"),
                   ("say", "self", "Prince Kael, the plans are complete for this new tower.", "talk"), ("wait", 3500),
                   ("emote", "self", "cheer"), ("state", "self", "work")],
         poi=["plot_1", "plot_2", "plot_3", "plot_4"]),

    # 6.24: Garithos's explosives: Vashj gives it ("I will not be trifled with.")
    dict(key="ch6_explosives", title="Garithos's Explosives", giver="vashj12", ender="vashj12", level=37, xp=8,
         tone="serious", prev="ch6_towers", memory="m12", kill=[("bearer", 10)],
         goal="In Isshara's memory, kill 10 of Garithos's Explosives Bearers coming down the crater's north slope toward "
              "the portal.",
         text="The human sends his sappers with fire and powder, as if a portal were a door to be kicked in. Meet them on "
              "the slope. None of them reaches the light.",
         progress="I still hear fuses.",
         reward="Good. Stay close to the light. He isn't finished. His kind never are.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("say", "self", "I will not be trifled with.", "talk", "LadyVashjWhat4"),
                 ("summon", "garithos12", "garithos_slope", 45), ("wait", 1500), ("face", "self", "north_entry"),
                 ("yell", "garithos12", "In memory of Terenas!", "point", "GarithosWarcry1"), ("wait", 2500),
                 ("yell", "garithos12", "Use these explosives on the portal!", "point"),
                 ("summon", "bearer", "north_1", 90), ("summon", "bearer", "north_2", 90), ("wait", 600),
                 ("move", "bearer", "portal_front", "run"), ("wait", 3000),
                 ("yell", "self", "The portal is under attack! Defend it at all costs!", "battle_roar"), ("wait", 3500),
                 ("yell", "garithos12", "Whoever destroys the portal will be a hero!", "shout"), ("wait", 4000),
                 ("yell", "self", "Protect the portal!", "spell"), ("wait", 6000),
                 ("yell", "self", "They're attacking the portal! It must be defended!", "battle_roar")],
         complete=[("emote", "self", "battle_roar"), ("wait", 1500), ("face", "self", "portal"),
                   ("state", "self", "channel_directed")],
         poi=["north_entry"]),

    # 6.25: hold Garithos at bay (a set piece: three waves in six minutes; the stream into the light; the brother falls)
    dict(key="ch6_hold", title="Hold Garithos at Bay", giver="ch0:isshara_young", ender="ch0:isshara_young", level=38,
         xp=8, tone="serious", prev="ch6_explosives", memory="m12", time=360,
         kill=[("wave_footman", 8), ("wave_beast", 4)],
         goal="In Isshara's memory, hold the portal square: kill 8 of Garithos's footmen and 4 of his beasts as they come "
              "down the north slope, within 6 minutes.",
         text="This is it. Everyone is going through, all of them, the whole of Quel'Thalas that's left, and Garithos has "
              "everything he owns coming down that slope. We hold until the last of them is in the light. Don't look at "
              "the light. Look at the slope.",
         progress="Hold! Hold the square!",
         reward="...The one by the tower, in red. He went down. Did you see him go down? I saw him go down. I don't know "
                "why I remember him. I never knew his name.",
         details=["battle_roar"], reward_emotes=["talk"],
         accept=[("music", BATTLE_6), ("face", "self", "north_entry"),
                 ("summon", "exodus_1", "stream_1", 15), ("summon", "exodus_2", "stream_2", 15),
                 ("summon", "exodus_3", "stream_3", 15), ("wait", 600), ("move", "exodus_1", "portal", "walk"),
                 ("move", "exodus_2", "portal", "walk"), ("move", "exodus_3", "portal", "walk"),
                 ("yell", "vashj12", "Kael, nearly half of our forces are through! You've got to hold Garithos at bay!",
                  "battle_roar"),
                 ("summon", "garithos12", "garithos_slope", 170), ("wait", 2000),
                 ("yell", "garithos12", "Humanity will rise again!", "point", "GarithosReady1"),
                 # the first wave: footmen
                 ("summon", "wave_footman", "north_1", 160), ("summon", "wave_footman", "north_2", 160),
                 ("summon", "wave_footman", "north_3", 160), ("summon", "wave_footman", "north_4", 160), ("wait", 30600),
                 ("summon", "exodus_1", "stream_1", 15), ("summon", "exodus_2", "stream_3", 15), ("wait", 600),
                 ("move", "exodus_1", "portal", "walk"), ("move", "exodus_2", "portal", "walk"), ("wait", 12000),
                 # the second: the cages opened
                 ("yell", "garithos12", "Bust open the cages! We'll need all the beasts we can use.", "point"),
                 ("summon", "wave_beast", "north_1", 140), ("summon", "wave_beast", "north_3", 140),
                 ("summon", "wave_beast", "north_2", 140), ("summon", "wave_footman", "north_4", 140),
                 ("summon", "wave_footman", "north_2", 140), ("wait", 600),
                 ("face", "kael12", "north_entry"),
                 ("yell", "kael12", "Endo-enah Quel'Thalas!", "battle_roar", "KaelWarcry1"), ("wait", 2500),
                 ("yell", "vashj12", "Era'sazjar!", "battle_roar", "LadyVashjYesAttack3"), ("wait", 30000),
                 ("summon", "exodus_3", "stream_2", 15), ("summon", "exodus_1", "stream_1", 15), ("wait", 600),
                 ("move", "exodus_3", "portal", "walk"), ("move", "exodus_1", "portal", "walk"), ("wait", 12000),
                 # the third: everything left; the spell breaker by the tower falls
                 ("summon", "wave_footman", "north_1", 110), ("summon", "wave_footman", "north_3", 110),
                 ("summon", "wave_footman", "north_4", 110), ("summon", "wave_footman", "north_2", 110),
                 ("summon", "wave_beast", "north_4", 110), ("summon", "wave_beast", "north_1", 110),
                 ("summon", "wave_beast", "north_3", 110), ("wait", 8600), ("emote", "aelthir", "wound"),
                 ("sound", "aelthir", BE_DEATH), ("state", "aelthir", "dead"), ("music", GLOOMY), ("wait", 6000),
                 ("yell", "vashj12", "Nearly everyone is through! Just a while longer, and we'll have done it!",
                  "battle_roar"),
                 ("summon", "exodus_2", "stream_2", 15), ("summon", "exodus_3", "stream_3", 15), ("wait", 600),
                 ("move", "exodus_2", "portal", "walk"), ("move", "exodus_3", "portal", "walk"), ("wait", 40000),
                 ("despawn", "aelthir")],
         complete=[("face", "self", "aelthir"), ("emote", "self", "cry"), ("wait", 2000), ("face", "self", "player"),
                   ("emote", "self", "talk")],
         poi=["north_entry"]),

    # 6.26: one final step: into the light; white; awake (and Taelon, if he stood in the water, crying)
    dict(key="ch6_step", title="One Final Step", giver="ch0:isshara_young", ender="ch0:isshara", level=38, xp=8,
         tone="serious", prev="ch6_hold", memory="m12", wake=True, explore="portal_mouth", radius=5,
         choice=["crossing_robe", "crossing_jerkin", "crossing_hauberk"],
         goal="In Isshara's memory, step into the portal's light after the prince.",
         text="Everyone's through. Everyone who's going. Lady Vashj is calling us back. Into the light, little one, right "
              "behind the prince. Don't stop. Don't look back at the slope.",
         progress="The light. Go!",
         reward="...You're back. Breathe. The light lets go of you slowly; it did then, too. Whatever you saw in the "
                "square, little one, it already happened.",
         details=["point"], reward_emotes=["talk"],
         accept=[("yell", "vashj12", "Kael, everyone is through! Fall back and we'll close the portal behind us!",
                  "battle_roar"), ("wait", 4500), ("face", "kael12", "d12_1"),
                 ("yell", "kael12", "All right, men! Pull back! Back to the portal!", "point"), ("wait", 3500),
                 ("face", "vashj12", "kael12"),
                 ("say", "vashj12", "Now, young prince, we take one final step... towards destiny.", "talk"),
                 ("wait", 3500), ("move", "kael12", "portal_mouth", "walk"), ("move", "self", "portal_front", "walk"),
                 ("wait", 7000), ("visual", "kael12", TELEPORT), ("despawn", "kael12")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", WATER),
                   ("face", "self", "taelon_shallows"), ("state", "taelon_water", "none"), ("emote", "taelon_water", "cry"),
                   ("sound", "taelon_water", BE_CRY), ("wait", 4000), ("emote", "taelon_water", "cry"),
                   ("sound", "taelon_water", BE_CRY), ("wait", 4000), ("move", "taelon_water", "taelon_away", "walk"),
                   ("wait", 14000), ("despawn", "taelon_water")],
         poi=["portal"]),

    # 6.27: the witch who bought us: "She didn't save us. She bought us." "Yes."; a bottle of wine by the pool
    dict(key="ch6_witch", title="The Witch Who Bought Us", giver="taelon", ender="ch0:isshara", level=38, xp=8,
         tone="serious", prev="ch6_step", rep=[(911, 250)], rewards=["wine"],
         goal="Take Taelon Emberveil's words to Isshara at the Hollow.",
         text="She didn't save us. She bought us. The boats, the cell door, the portal held open: every one of them a "
              "coin, and the price was a prince on his knees to a demon. Tell your keeper I said so. Tell her I want to "
              "hear her say I'm wrong.",
         reward="Yes.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("say", "self", "She didn't save us. She bought us.", "talk"), ("wait", 2500),
                 ("face", "self", "toward_hollow"), ("emote", "self", "no")],
         complete=[("face", "self", "sea_east"), ("summon", "taelon_visit", "taelon_from", 75), ("wait", 600),
                   ("move", "taelon_visit", "taelon_edge", "walk"), ("wait", 9000), ("face", "taelon_visit", "sea_south"),
                   ("wait", 3000), ("move", "taelon_visit", "taelon_away", "walk"), ("wait", 7000),
                   ("move", "taelon_visit", "wine_spot", "walk"), ("wait", 13000), ("emote", "taelon_visit", "kneel"),
                   ("object", "wine_bottle", "wine_spot", 1800), ("sound", "taelon_visit", 1186), ("wait", 2000),
                   ("move", "taelon_visit", "taelon_away", "walk"), ("visual", "self", WATER)],
         poi=["hollow_pool"]),

    # 6.28: Rimtori's tome (hero): the pages burn; the half-called demon sputters out; "Demons, for instance."
    dict(key="ch6_tome", title="Rimtori's Tome", giver="taelon_lake", ender="taelon_lake", level=38, xp=8,
         tone="serious", path="hero", prev="ch6_witch", rep=[(911, 350)], kill=[("fel_magister", 8)],
         objects=[("summoning_page", 3)], choice=["emberveil_buckler", "tome_wand", "page_cloak"],
         goal="Go with Taelon Emberveil to the summoning circle on Lake Mennar's east ridge: kill 8 Fel-Touched "
              "Magisters and burn the 3 torn pages of Rimtori's tome laid round the circle.",
         text="Rimtori's people found what they were digging for: a tome, Highborne, older than Silvermoon. They've torn "
              "its pages out and laid them round a circle on the east ridge, and something on the far side of that circle "
              "is answering. You heard the prince's hunger. This is what it looks like when it wins. With me.",
         progress="Burn them. All of them.",
         reward="Ash. Good. ...She said it to him like an offer of tea. 'Demons, for instance.' And he said never. We all "
                "said never.",
         details=["talk", "point"], reward_emotes=["talk", "no"],
         accept=[("face", "self", "player"), ("say", "self", "With me.", "talk"), ("wait", 1200), ("face", "self", "circle"),
                 ("emote", "self", "ready1h"), ("follow", "self")],
         complete=[("face", "self", "circle"), ("wait", 2000),
                   ("whisper", "self", "Demons, for instance.", None), ("wait", 2500), ("face", "self", "player"),
                   ("emote", "self", "no"), ("wait", 1000), ("evade", "self")],
         poi=["circle"]),

    # 6.29: boats for the Horde (hero): "These boats are merely a gesture of goodwill." Ag'tor laughs (in his window)
    dict(key="ch6_boats", title="Boats for the Horde", giver="ch0:szaria", ender=AGTOR, level=38, xp=8, tone="serious",
         path="hero", prev="ch6_witch", rep=[(76, 500)], explore="landing", radius=15,
         interact=[("lookout", "Tell him who sent the boats.")], interact_goal="The boats handed to Valormok's lookout",
         interact_beats=[("face", "self", "bay"), ("summon", "szaria_landing", "szaria_rise", 40), ("wait", 600),
                         ("sound", "szaria_landing", "splash_big"), ("move", "szaria_landing", "szaria_shore", "walk"),
                         ("wait", 6000), ("face", "szaria_landing", "lookout"), ("face", "self", "szaria_shore"),
                         ("say", "szaria_landing", "These boats are merely a gesture of goodwill.", "talk"), ("wait", 3500),
                         ("emote", "self", "laugh"), ("sound", "self", ORC_LAUGH), ("wait", 2500), ("sound", "self", HORN),
                         ("face", "self", "valormok_east"), ("yell", "self", "CHIEF! BOATS! The snakes brought us BOATS!",
                                                             "shout"),
                         ("move", "szaria_landing", "szaria_rise", "walk"), ("wait", 5000), ("despawn", "szaria_landing")],
         goal="Bring the two captured Spitelash boats along the coast from the Hollow to Valormok's landing on the bay's "
              "west strand, under the Eldarath cliffs; give them to the lookout there, then report to Ag'tor Bloodfist "
              "in Valormok.",
         text="Two Spitelash boats, taken off the Empress's lancers without a scratch. The orcs have looked at this bay for "
              "years with no way across it. Tow them along the coast to the orcs' landing under the Eldarath cliffs. I'll "
              "be there before you. I have a few words for Ag'tor's people, and I've been practising them.",
         progress="",
         reward="'A gesture of goodwill.' My lookout ran all the way up the hill to tell me. Word for word, he says, she "
                "said it word for word, and then she smiled at him. Ha! HA! ...Good boats. Tell your lady: accepted.",
         details=["talk", "point"], reward_emotes=["laugh", "talk"], choice=["boatman_boots", "tidewalker_boots",
                                                                             "dockside_slippers"],
         accept=[("face", "self", "boats_1"), ("summon", "spitelash_boat", "boats_1", 900),
                 ("summon", "spitelash_boat_2", "boats_2", 900), ("wait", 600), ("follow", "spitelash_boat"),
                 ("follow", "spitelash_boat_2"), ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player"),
                 ("say", "self", "These boats are merely a gesture of goodwill. ...Hm. I'll say it slower.", "talk"),
                 ("emote", "ch0:vyssa", "work"), ("sound", "ch0:vyssa", 6928)],
         poi=["landing", "agtor"]),

    # 6.30: something terrible (the chapter's last): the pool freezes for a moment and cracks; "She's coming for me."
    dict(key="ch6_end", title="Something Terrible", giver="ch0:isshara", ender="ch0:szaria", level=38, xp=8,
         tone="serious", prev=["ch6_tome", "ch6_boats"], choice=["cracked_pearl", "long_watch", "cold_choker"],
         goal="Tell Lady Szaria what Isshara heard in the water.",
         text="There's one more song. I can feel it. Not in any box: she has it. Serena keeps it herself now, on her own "
              "belt, close, where she can hear it hum. She's listening to it right now, little one, the way I listen to "
              "mine. ...Go and tell Szaria. Tell her she's coming for me.",
         reward="Then she'll find us awake. ...Vyssa! Ssaveth! Nobody sleeps tonight. Double the watch on the water, and "
                "somebody sit with the keeper. Not you. You've done enough singing for one season.",
         details=["talk"], reward_emotes=["talk", "roar"],
         accept=[("state", "self", "channel"), ("wait", 2000), ("summon", "pool_frost", "pool", 6), ("wait", 300),
                 ("visual", "pool_frost", FROZEN), ("sound", "self", FROST_NOVA), ("emote", "self", "stun"), ("wait", 3500),
                 ("visual", "pool_frost", ICE_SPIKE), ("sound", "self", ICE_CRACK), ("wait", 1500),
                 ("state", "self", "none"), ("face", "self", "player"), ("say", "self", "She's coming for me.", "talk"),
                 ("visual", "self", WATER)],
         complete=[("face", "self", "sea_south"), ("wait", 2500), ("emote", "self", "work"), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "battle_roar"), ("emote", "ch0:ssaveth", "battle_roar"),
                   ("sound", "ch0:ssaveth", "naga_aggro"), ("face", "ch0:vyssa", "sea_south")],
         poi=["szaria"]),
]

# -- more of someone already made: young Isshara in her four songs ---------------------------------------------------
SPAWNS = [
    dict(npc="ch0:isshara_young", at="m9_isshara", facing=0.3, phase=M9),
    dict(npc="ch0:isshara_young", at="m10_isshara", facing=0.6, phase=M10),
    dict(npc="ch0:isshara_young", at="m11_isshara", facing=0.6, phase=M11),
    dict(npc="ch0:isshara_young", at="m12_isshara", facing=3.14, phase=M12),
    # M10's camp is M9's (the next day): its tents, banners and fire again
    dict(object="m9_tent", at=["m9_tent_1", "m9_tent_2"], facing=2.2, phase=M10),
    dict(object="m9_sunstrider", at="m9_banner_2", facing=3.3, phase=M10),
    dict(object="m9_fire", at="m9_fire", phase=M10),
]
