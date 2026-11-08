# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 3 of the naga's story: The Tomb (levels 20 to 24), the bible's section 10.

Present day. The Hollow (the Tide-Broken's islet in the Bay of Storms, chapter 2's hub: its people and the hub kit
are chapter 2's spawns) and the Spitelash's sea-shrine of Lady Sesspira on the strand below the Ruins of Eldarath's
north-east cliffs (x 3700-3850, y -5560 to -5700, z 8-15: the beach where the ruins' plateau falls to the bay). The
shrine is at the cliff's foot: a pool, an altar, the Empress's sigil cut into one of Eldarath's own rune-stones, and
Tidecaller Vyrash who sings Sesspira's image up out of the pool; pickets hold the ruins' edge north and south of it;
a Valormok grunt sits in a cage by the cliff; a shoulder of rock 40 yards up the cliff (3790, -5551, z 49) looks down
on all of it. The shore road runs north along the strand from the shrine; Snapjaw hunts the shallows off the Hollow's
south-west beach. Valormok (3.22b) is the Horde's.

Two memories, sung by Isshara at the Hollow's pool:
  m3, The Broken Isles (Ssaveth's, bit A): the Ruins of Eldarath's plaza as Suramar's ruins, newly risen, and the
      Temple of Zin-Malor's great stair as the way up to the Tomb of Sargeras's door (the stair climbs east from the
      plaza, z 86 to 109; the door at its top, 3546, -5303). Young Ssaveth stands guard at the stair's foot.
  m4, The Tomb of Sargeras (Isshara's, bit B): the half-drowned Temple of Arkkoran (a building on the bay: every place
      in it is given its height, from the game's own creatures standing there). One comes in at its south-western ledge,
      walks the long hall to the queen's statue, and leaves by the sea gate on its north-eastern ramp.

Phases: none of this chapter's own in Azshara (its budget is none). Everyone in the present stands in the naga's phase
(always) and quest prerequisites decide what's offered; who appears for one scene is summoned in it; the memories'
people are in their memory's bit. The outpost's Spitelash are therefore there for any naga who passes, before and
after this chapter (and, from chapter 7's live world, beside the game's own Spitelash on that strand).

Chapter 2's camp on the Hollow stands where chapter 2 put it (its HUB phase): Szaria by the landing (chapter 1's),
Ssaveth on the dune to the north, Vyssa at the fire, Isshara by her pool at the east end (one wakes on its shore), the
trainers round the islet. This chapter's scenes use those places: Ssaveth's own quests walk him to the sand by his dune
and the beach below it and send him home (evade); the sigil of 3.25 is drawn at Szaria's feet; Thessa, whom chapter 2
leaves lying in the shallows by the pool without a spawn of her own, is brought there for the priest's lesson (3.13).
Chapter 2's courier halts on the bay road a hundred yards south-east of the shrine (3730, -5690): the same Spitelash.

Choices carried by their quests: 1.20a/b give 3.03 its two versions (Ssethis lets you pass, or attacks), as chapter 1's
1.21 and 1.22 do; 3.22a/b is the chapter's hero/menace pair.

Plain data: tools/murloc/SCHEMA.md, tools/naga/SCHEMA.md."""

M3 = ("memory", "m3")                       # The Broken Isles (Ssaveth's): Eldarath's plaza and Zin-Malor's stair
M4 = ("memory", "m4")                       # The Tomb of Sargeras (Isshara's): the Temple of Arkkoran

CHAPTER = dict(key="ch3", title="The Tomb", levels=(20, 25), map=1, zones=[16], hub="hollow_pool")

TOWNS = ["Valormok"]

PLACES = {
    # -- the Hollow (chapter 2's camp on the islet in the bay: who stands where is chapter 2's; these are the spots this
    #    chapter's scenes use round them) -----------------------------------------------------------------------------
    "hollow_pool": (3959.0, -6311.0),           # the shore of Isshara's pool (chapter 2's pool_shore): where one wakes
    "isshara_spot": (3963.0, -6316.0), "ssaveth_spot": (3978.0, -6278.0), "szaria": (3954.0, -6266.0),
    "away_from_pool": (3982.0, -6236.0),        # the way Ssaveth faces with his back to the pool (3.05)
    "sea_east": (3992.0, -6300.0),              # the open bay off the islet's north-east beach
    "sigil_spot": (3949.0, -6270.0),            # the sigil Szaria draws at her feet (3.25)
    "rn_from_1": (3966.0, -6250.0), "rn_from_2": (3930.0, -6282.0), "rn_from_3": (3970.0, -6292.0),
    "rn_from_4": (3936.0, -6250.0),
    "line_1": (3952.0, -6273.0), "line_2": (3946.0, -6273.0), "line_3": (3946.0, -6267.0), "line_4": (3952.0, -6267.0),
    "trident_spot": (3982.0, -6272.0), "trident_sand": (3984.5, -6270.0), "beach_away": (3982.0, -6306.0),
    "sea_look": (4005.0, -6268.0),
    "ssaveth_draw": (3972.0, -6268.0), "draw_1": (3969.5, -6265.0), "draw_2": (3970.0, -6269.5),
    "draw_3": (3973.5, -6264.5),
    "cask_spot": (3958.0, -6284.0),             # by the camp's fire
    "murgul_sea": (3994.0, -6262.0, -0.5), "murgul_shore": (3976.0, -6266.0),
    "thessa_rest": (3972.0, -6330.0),           # where Thessa lies in the shallows (chapter 2's)
    "snapjaw": (3888.0, -6226.0), "trap_1": (3894.0, -6232.0, -0.4), "trap_2": (3900.0, -6222.0, -0.4),
    "tr_1": (3922.0, -6251.0), "tr_2": (3921.0, -6247.0), "tr_3": (3920.0, -6244.0),
    "tide_pool": (3931.0, -6293.0),

    # -- the Spitelash's sea-shrine on the strand below the Ruins of Eldarath --------------------------------------
    "lookout": (3790.0, -5551.0),               # the shoulder of rock 40 yards up the cliff, over the shrine
    "lookout_eye": (3790.0, -5553.0),
    "shrine_pool": (3788.0, -5614.0), "image_rise": (3788.0, -5614.0),
    "vyrash": (3794.0, -5605.0), "altar": (3800.0, -5596.0),
    "pearl_1": (3799.3, -5596.4, 13.4), "pearl_2": (3800.7, -5595.6, 13.4),
    "sigil_stone": (3779.0, -5602.0),
    "ac_1": (3772.0, -5624.0), "ac_2": (3782.0, -5632.0), "ac_3": (3800.0, -5630.0), "ac_4": (3808.0, -5610.0),
    "ac_5": (3812.0, -5594.0), "ac_6": (3768.0, -5594.0), "ac_7": (3762.0, -5608.0), "ac_8": (3794.0, -5638.0),
    "shrinewarden": (3776.0, -5642.0),
    "pk_1": (3836.0, -5596.0), "pk_2": (3846.0, -5612.0), "pk_3": (3828.0, -5622.0), "pk_4": (3750.0, -5596.0),
    "pk_5": (3738.0, -5612.0), "pk_6": (3726.0, -5628.0), "pk_7": (3744.0, -5642.0), "pk_8": (3760.0, -5658.0),
    "pk_9": (3792.0, -5664.0), "pk_10": (3816.0, -5652.0), "pickets": (3790.0, -5625.0),
    "shieldbearer": (3820.0, -5640.0), "dozing": (3716.0, -5592.0),
    "cage": (3820.0, -5584.0), "cage_out": (3824.0, -5590.0), "throk_road": (3860.0, -5630.0),
    "throk_road_2": (3896.0, -5676.0),
    "ob_1": (3772.0, -5616.0), "ob_2": (3806.0, -5618.0), "ot_1": (3783.0, -5600.0), "ot_2": (3797.0, -5621.0),
    "ot_3": (3816.0, -5586.0), "pagoda": (3742.0, -5582.0), "weapons": (3832.0, -5606.0), "crate_1": (3752.0, -5587.0),
    "crate_2": (3755.0, -5590.0), "jar_1": (3804.0, -5590.0),
    "spring": (3758.0, -5537.0),                # Isshara's spring, under the cliff south-west of the shrine
    "succubus": (3884.0, -5600.0), "drowned_ruin": (3888.0, -5598.0),
    # the shore road north of the shrine (3.03): a heap of driftwood, the patrol's way, the sea
    "blind_a": (3884.0, -5668.0), "blind_b": (3886.0, -5664.0), "road": (3890.0, -5680.0),
    "patrol_start": (3912.0, -5716.0), "patrol_start_2": (3916.0, -5720.0), "patrol_start_3": (3908.0, -5722.0),
    "patrol_stop": (3894.0, -5684.0), "patrol_stop_2": (3897.0, -5689.0), "patrol_stop_3": (3891.0, -5690.0),
    "patrol_turn": (3934.0, -5640.0), "orders_spot": (3892.0, -5680.0), "sea_escape": (3880.0, -5792.0),

    # -- Valormok (3.22b): Ag'tor Bloodfist's yard ------------------------------------------------------------------
    "valormok_yard": (3610.0, -4412.0), "valormok_watch": (3613.0, -4416.0), "agtor_side": (3605.0, -4410.0),

    # -- memory m3 (bit A): the Broken Isles, newly risen: Eldarath's plaza as Suramar, Zin-Malor's stair to the Tomb --
    "m3_centre": (3510.0, -5222.0), "m3_arrive": (3544.0, -5222.0),
    "m3_ssaveth": (3550.0, -5232.0), "m3_ssaveth_near": (3547.0, -5229.0),
    "tg_1": (3540.0, -5232.0), "tg_2": (3558.0, -5228.0), "tg_3": (3534.0, -5226.0),
    "m3_door": (3546.0, -5303.0, 109.6), "m3_door_in": (3546.0, -5306.5, 109.4),
    "illidan_top": (3546.0, -5296.0, 110.6), "vashj_top": (3540.0, -5294.0, 111.0), "stair_mid": (3546.0, -5262.0),
    "m3_ruins": (3500.0, -5196.0), "m3_statue": (3502.0, -5196.0), "m3_statue_eye": (3506.0, -5200.0),
    "col_illidan": (3508.0, -5202.0), "col_1": (3500.0, -5190.0), "col_2": (3496.0, -5198.0), "col_3": (3504.0, -5186.0),
    "col_1_end": (3546.0, -5246.0), "col_2_end": (3540.0, -5246.0), "col_3_end": (3552.0, -5246.0),
    "col_illidan_end": (3546.0, -5254.0),
    "maiev_near": (3500.0, -5196.0), "maiev_blink": (3540.0, -5228.0),
    "wave_1": (3520.0, -5200.0), "wave_2": (3512.0, -5214.0), "wave_3": (3528.0, -5192.0), "wave_4": (3524.0, -5206.0),
    "wave_5": (3506.0, -5204.0), "wave_6": (3532.0, -5198.0), "over_from": (3530.0, -5214.0),
    "w_1": (3470.0, -5150.0), "w_2": (3480.0, -5170.0), "w_3": (3460.0, -5180.0), "w_4": (3490.0, -5140.0),
    "w_5": (3450.0, -5160.0), "w_6": (3500.0, -5160.0), "w_7": (3470.0, -5200.0), "w_8": (3455.0, -5210.0),
    "w_9": (3485.0, -5215.0), "w_10": (3440.0, -5190.0), "plaza": (3470.0, -5180.0),
    "pit_1": (3492.0, -5236.0), "pit_2": (3478.0, -5250.0), "pit_3": (3500.0, -5268.0), "pits": (3490.0, -5252.0),
    "sp_1": (3488.0, -5228.0), "sp_2": (3498.0, -5240.0), "sp_3": (3484.0, -5244.0), "sp_4": (3472.0, -5244.0),
    "sp_5": (3480.0, -5260.0), "sp_6": (3470.0, -5256.0), "sp_7": (3494.0, -5272.0), "sp_8": (3506.0, -5262.0),
    "sp_9": (3502.0, -5278.0), "drakthul": (3486.0, -5266.0),
    "st_1": (3520.0, -5180.0), "st_2": (3480.0, -5210.0), "st_3": (3530.0, -5240.0),
    "fish_1": (3544.0, -5250.0), "fish_2": (3548.0, -5266.0), "fish_3": (3540.0, -5258.0), "fish_4": (3552.0, -5240.0),
    "kelp_1": (3535.8, -5220.0), "kelp_2": (3494.9, -5233.4), "kelp_3": (3534.1, -5250.1),
    "bone_1": (3486.0, -5240.0), "bone_2": (3496.0, -5264.0),

    # -- memory m4 (bit B): the Tomb of Sargeras in the Temple of Arkkoran (its floors' heights, from the game's own
    #    creatures standing there) --------------------------------------------------------------------------------
    "m4_centre": (3870.0, -7180.0), "m4_arrive": (3784.1, -7134.6, 26.6), "m4_entry": (3787.0, -7137.0, 26.5),
    "voice_spot": (3774.8, -7147.4, 26.5), "voice_hall": (3816.2, -7172.5, 25.1),
    "m4_isshara": (3880.8, -7152.0, 23.5),
    "statue": (3880.2, -7177.8, 22.4), "statue_front": (3874.0, -7175.0, 22.4), "statue_touch": (3876.5, -7174.0, 22.4),
    "vashj_statue": (3874.6, -7175.5, 22.4),
    "vashj_from": (3816.2, -7172.5, 25.1), "vashj_to": (3852.2, -7195.9, 22.9),
    "mt_1": (3816.2, -7172.5, 25.1), "mt_2": (3845.4, -7157.2, 23.4), "mt_3": (3875.1, -7199.7, 22.4),
    "mt_4": (3849.8, -7134.5, 25.0),
    "ng_1": (3847.0, -7133.6, 25.4), "ng_2": (3893.6, -7154.4, 25.1),
    "maiev_in": (3816.2, -7172.5, 25.1), "maiev_stop": (3837.3, -7171.4, 23.1),
    "naisha_in": (3814.2, -7189.4, 26.3), "naisha_stop": (3836.0, -7177.0, 23.1),
    "wa_in": (3826.4, -7144.7, 25.7), "wa_stop": (3841.4, -7158.8, 22.9), "wb_in": (3814.2, -7189.4, 26.3),
    "wb_stop": (3838.0, -7182.0, 23.1), "maiev_out": (3784.1, -7134.6, 26.6),
    "vision_statue": (3852.2, -7195.9, 22.9),
    "hb_1": (3852.0, -7190.0, 22.9), "hb_2": (3847.5, -7192.5, 22.9), "hb_3": (3856.5, -7192.5, 22.9),
    "hb_4": (3848.5, -7199.0, 22.9), "hb_5": (3856.0, -7199.0, 22.9),
    "eye_door": (3897.0, -7184.0, 26.1),
    "rune_1": (3826.4, -7144.7, 25.7), "rune_2": (3814.2, -7189.4, 26.3), "rune_3": (3863.0, -7210.3, 25.0),
    "g1_from": (3826.0, -7148.0, 25.7), "g1_to": (3834.0, -7154.0, 24.0),
    "g2_from": (3816.0, -7186.0, 26.3), "g2_to": (3826.0, -7184.0, 24.5),
    "g3_from": (3861.0, -7206.0, 25.0), "g3_to": (3858.0, -7200.0, 23.5),
    "shade_1": (3866.0, -7214.0, 25.0), "shade_2": (3852.2, -7195.9, 22.9), "shade_3": (3863.0, -7193.0, 23.0),
    "tt_1": (3843.0, -7160.5, 22.9), "tt_2": (3839.0, -7174.0, 23.1), "tt_3": (3877.0, -7202.0, 22.4),
    "tt_4": (3865.0, -7213.0, 25.0), "tt_5": (3895.5, -7156.5, 25.1), "dt": (3929.9, -7160.2, 26.6),
    "torches": (3860.0, -7180.0, 23.0),
    "lt_1": (3828.0, -7147.5, 25.7), "lt_2": (3851.5, -7136.5, 25.0), "lt_3": (3883.0, -7181.0, 22.4),
    "lt_4": (3883.0, -7173.0, 22.4), "lt_5": (3899.0, -7193.0, 26.1),
    "eye_spot": (3901.4, -7190.1, 26.1), "eye_hand": (3898.6, -7187.6, 28.4),
    "illidan_eye_from": (3893.6, -7154.4, 25.1), "illidan_eye": (3897.4, -7185.8, 26.1),
    "vashj_eye": (3893.0, -7193.0, 26.0), "illidan_out": (3929.9, -7160.2, 26.6), "vashj_out": (3941.8, -7181.0, 26.6),
    "fall_1": (3897.0, -7180.0, 26.0), "fall_2": (3941.8, -7181.0, 26.6), "fall_3": (3929.3, -7228.3, 26.8),
    "fall_4": (3953.7, -7215.4, 22.3),
    "naisha_fall": (3893.6, -7154.4, 25.1), "maiev_flee": (3875.2, -7140.8, 45.7),
    "wg_1": (3941.8, -7181.0, 26.6), "wg_2": (3953.7, -7215.4, 22.3), "wg_3": (3929.3, -7228.3, 26.8),
    "wg_4": (3937.2, -7156.1, 26.5), "wg_5": (3900.3, -7232.2, 26.5), "wg_6": (3929.9, -7164.0, 26.6),
    "sea_gate": (3974.7, -7222.2, 14.5), "gate_watch": (3972.0, -7221.0, 15.5),
    "vashj_gate": (3986.0, -7226.0, 0.0), "vashj_sea": (4004.0, -7232.0, 0.0),
}

# -- looks and models ---------------------------------------------------------------------------------------------
CAGE = "World\\EXPANSION01\\DOODADS\\COILFANG\\PASSIVEDOODADS\\cages\\cf_groundcage.m2"
POOL = "World\\Expansion02\\Doodads\\BoreanTundra\\Geysers\\Borean_MineralPool_01.m2"
ARK = "World\\Expansion01\\Doodads\\Generic\\Naga\\Ark\\NA_Ark.m2"
RUNESTONE = 235                                     # Eldarath's rune-stones (the game's Rune of Jin'yael)
RUBBLE = "World\\Kalimdor\\DireMaul\\PassiveDoodads\\Rubble\\DireMaulStoneStatue02.m2"
NAGA_FLAG = "World\\Kalimdor\\Azshara\\PassiveDoodads\\NagaFlags\\NagaFlag01.m2"
BASIN = "World\\Azeroth\\Elwynn\\PassiveDoodads\\WaterBasin\\WaterBasin.m2"
RUIN = "World\\Azeroth\\TheBlastedLands\\PassiveDoodads\\Ruins\\BrokenGateSide01.m2"
DRIFTWOOD = "World\\Azeroth\\Westfall\\PassiveDoodads\\Detail\\WestfallDriftwood.m2"
TRAP = "World\\Expansion02\\Doodads\\Generic\\Tuskarr\\TS_CrabBasket_Broken.m2"
TRACKS = "World\\Expansion02\\Doodads\\Generic\\CatWolfTracks\\CatWolf_Footprint_Mud01.m2"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell01.mdx"
SHELL_2 = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
CORAL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Coral\\Coral01.mdx"
KELP = "World\\Generic\\Underwater\\PassiveDoodads\\Seaweed\\GenericSeaweed01.mdx"
SEAWEED = "World\\Kalimdor\\Azshara\\PassiveDoodads\\Seaweed\\SeaWeed01.mdx"
ARCH = "World\\Azeroth\\TheBlastedLands\\PassiveDoodads\\Ruins\\BrokenGateArch.m2"
SEALED_DOOR = "World\\Expansion01\\Doodads\\BlackTemple\\ActiveDoodads\\Doors\\BT_Gate_Solid.m2"
STATUE_HEAD = "World\\Generic\\NightElf\\Passive Doodads\\Statues\\StatueAszharaHead.m2"
STEAM = "World\\Expansion01\\Doodads\\Coilfang\\PassiveDoodads\\Steam\\Coilfang_Steam.m2"
FISH_BLUE = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadBlue.m2"
FISH_GREEN = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadGreen.m2"
PIT = "World\\Kalimdor\\DireMaul\\ActiveDoodads\\WarlockCircle\\WarlockMountRitualCircle01.m2"
BONES = "World\\Azeroth\\TheBlastedLands\\PassiveDoodads\\Bones\\BlastedLandsBonePile02.m2"
NAGA_STATUE = "World\\Kalimdor\\Blackfathom\\PassiveDoodads\\Statue\\BFD_StatueNagaPriestess.m2"
GOLDEN_STATUE = "World\\Kalimdor\\DireMaul\\PassiveDoodads\\GoldenHighElfStatue01.m2"
DEAD_TORCH = "World\\Expansion02\\Doodads\\Generic\\Vrykul\\Torch\\VR_Torch_Broken_01.m2"

WATCHERS = ["warden_2", "warden_3", "warden_4"]      # Maiev's Watchers (Legion's warden, converted: tools/naga/looks.py)

# -- the people ---------------------------------------------------------------------------------------------------
NPCS = [
    # ---- the sea-shrine below Eldarath (the Spitelash's; there in the naga's phase) ----------------------------------
    dict(key="vyrash", equip=(5284, 0, 5259), name="Tidecaller Vyrash", subname="Hand of Lady Sesspira", look="spitelash_siren", size=1.3,
         level=25, side="naga", role="enemy", caster=True, health=2.5, abilities=[(9672, 7000)], at="vyrash",
         facing=4.12, respawn=120,
         idle=[("every", 26000, [("emote", "self", "omnicast"), ("sound", "self", "siren_hiss")])],
         at_health=(60, [("yell", "self", "Lady! Lady Sesspira, rise and see who comes into your water!", "omnicast"),
                         ("summon", "sesspira_fight", "image_rise", 14), ("visual", "sesspira_fight", 44816),
                         ("sound", "self", "siren_aggro")])),
    dict(key="picket", equip=(5745,), name="Spitelash Picket", plural="spitelash pickets", look="spitelash_myrmidon", looks=[6747],
         level=(20, 21), side="naga", role="enemy",
         at=["pk_1", "pk_2", "pk_3", "pk_4", "pk_5", "pk_6", "pk_7", "pk_8", "pk_9", "pk_10"], wander=3.0, respawn=45,
         idle=[("state", "self", "ready_thrown")]),
    dict(key="acolyte", equip=(5284,), name="Spitelash Acolyte", plural="spitelash acolytes", look="spitelash_siren", level=(22, 23),
         side="naga", role="enemy", caster=True, health=0.9, abilities=[(9532, 9000)],
         at=["ac_1", "ac_2", "ac_3", "ac_4", "ac_5", "ac_6", "ac_7", "ac_8"], wander=2.0, respawn=45,
         idle=[("every", 31000, [("emote", "self", "omnicast"), ("sound", "self", "siren_hiss")])]),
    dict(key="shrinewarden", equip=(1899,), name="Spitelash Shrinewarden", look=11267, size=1.5, level=22, side="naga", role="enemy",
         health=2.5, abilities=[(12057, 8000)], at="shrinewarden", facing=4.71, respawn=90,
         idle=[("state", "self", "ready_thrown"), ("every", 47000, [("emote", "self", "battle_roar")])]),
    dict(key="shieldbearer", equip=(1899,), name="Spitelash Shieldbearer", look=11267, size=1.3, level=21, side="naga", role="enemy",
         health=1.8, at="shieldbearer", facing=5.4, respawn=60,
         idle=[("state", "self", "ready_thrown")],
         at_health=(40, [("sound", "self", 13092), ("emote", "self", "stun"), ("emote", "self", "battle_roar")])),
    dict(key="dozing_picket", equip=(5745,), name="Dozing Picket", look="spitelash_myrmidon", level=21, side="neutral", role="ambient",
         at="dozing", facing=1.2, respawn=60, gossip="Hsss... zzz... my watch... is it my watch... zzz...",
         idle=[("state", "self", "drowned"), ("every", 30000, [("visual", "self", 6431)])]),
    # the image Vyrash sings up out of the pool (3.01, 3.23), and the one that fights beside her (3.12)
    dict(key="sesspira_image", equip=(2147, 0, 2550), name="Image of Lady Sesspira", look=11261, scale=1.4, level=30, role="ambient",
         untouchable=True, summoned=True, idle=[("every", 3000, [("visual", "self", 44816)])]),
    dict(key="sesspira_fight", equip=(2147, 0, 2550), name="Image of Lady Sesspira", look=11261, scale=1.4, level=25, side="naga", role="enemy",
         caster=True, health=1.2, abilities=[(8435, 20000)], summoned=True, detection=40.0,
         idle=[("every", 3000, [("visual", "self", 44816)])]),
    dict(key="pearl_glow", name="Song-Pearl's Light", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 2000, [("visual", "self", 22576)])]),
    dict(key="sigil_light", name="The Empress's Sigil", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="sigil_stone", respawn=90, idle=[("every", 6000, [("visual", "self", 22581)])]),
    # the lookout over the shrine: whoever comes up sees Vyrash sing Sesspira's image up out of the pool (3.01)
    dict(key="lookout_watch", name="The Cliff Above the Shrine", look="trigger", level=1, role="ambient",
         unit_flags=0x02000002, at="lookout",
         watch=(14, [("music", 5037), ("state", "vyrash", "channel"), ("sound", "vyrash", "siren_hiss"),
                     ("object", "altar_pearl", "pearl_1", 50), ("object", "altar_pearl", "pearl_2", 50),
                     ("summon", "pearl_glow", "pearl_1", 50), ("summon", "pearl_glow", "pearl_2", 50), ("wait", 4000),
                     ("sound", "vyrash", "siren_aggro"), ("summon", "sesspira_image", "image_rise", 26),
                     ("visual", "sesspira_image", 44816), ("scale", "sesspira_image", 0.3), ("wait", 700),
                     ("scale", "sesspira_image", 0.7), ("wait", 700), ("scale", "sesspira_image", 1.1), ("wait", 700),
                     ("scale", "sesspira_image", 1.4), ("visual", "sesspira_image", 36005),
                     ("sound", "sesspira_image", "splash_big"), ("wait", 1500), ("state", "vyrash", "none"),
                     ("emote", "vyrash", "drown"), ("visual", "vyrash", 36005), ("wait", 3000),
                     ("emote", "sesspira_image", "omnicast"), ("wait", 2500), ("face", "sesspira_image", "lookout_eye"),
                     ("wait", 4000), ("face", "sesspira_image", "vyrash"), ("emote", "sesspira_image", "talk"),
                     ("emote", "vyrash", "omnicast"), ("wait", 4000), ("scale", "sesspira_image", 1.0), ("wait", 600),
                     ("scale", "sesspira_image", 0.6), ("wait", 600), ("scale", "sesspira_image", 0.2),
                     ("despawn", "sesspira_image"), ("emote", "vyrash", "spell")], 90000)),
    # the Valormok grunt the Spitelash caged at the shrine (3.22a/b), and the same grunt on a rope (3.22b)
    dict(key="throk", equip=(5289,), name="Grunt Throk", subname="Valormok", look=4259, level=20, side="ally", role="ambient",
         language="orcish", at="cage", facing=5.4, respawn=60,
         gossip="Come to look at the orc in the box? Look, then. And when you're done looking, I hope you choke on it.",
         idle=[("state", "self", "sit"), ("every", 34000, [("emote", "self", "rude"), ("sound", "self", 6363)])]),
    dict(key="throk_rope", equip=(5289,), name="Grunt Throk", subname="On a Rope", look=4259, level=20, side="ally", role="ambient",
         language="orcish", summoned=True,
         idle=[("every", 27000, [("emote", "self", "rude"), ("sound", "self", 6363)])]),
    # Ag'tor's yard at Valormok: whoever comes in with Throk on a rope, Throk tells the whole camp (3.22b; the game's
    # Ag'tor can't be given a scene of the story's, so the grunt makes it)
    dict(key="valormok_watch", name="Ag'tor's Yard", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="valormok_watch",
         watch=(20, [("emote", "throk_rope", "rude"), ("sound", "throk_rope", 6363),
                     ("yell", "throk_rope", "Ag'tor! Chieftain! The fish are selling me back to you! The FISH, Ag'tor!",
                      "talk"),
                     ("wait", 3500), ("move", "throk_rope", "agtor_side", "walk"), ("wait", 4500),
                     ("face", "throk_rope", "player"), ("emote", "throk_rope", "rude"), ("wait", 2500),
                     ("emote", "throk_rope", "no")], 60000)),
    # the shore road's patrol (3.03): Ssethis, older and taller, and the Spitelash who walk with him
    dict(key="ssethis_a", equip=(5745,), name="Ssethis", subname="Spitelash Patrol", look=11265, scale=0.92, level=21, role="ambient",
         untouchable=True, summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="patroller_a1", equip=(5745,), name="Spitelash Patroller", look=6747, level=20, role="ambient", untouchable=True,
         summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="patroller_a2", equip=(5745,), name="Spitelash Patroller", look=11265, level=20, role="ambient", untouchable=True,
         summoned=True, idle=[("state", "self", "ready_thrown")]),
    dict(key="ssethis_b", equip=(5745,), name="Ssethis", subname="Spitelash Patrol", look=11265, scale=0.92, level=21, side="naga",
         role="enemy", health=1.6, summoned=True, detection=30.0,
         at_health=(50, [("yell", "self", "This isn't finished, heretic! Ssethis remembers! Ssethis ALWAYS remembers!",
                          "battle_roar"),
                         ("faction", "self", "neutral"), ("evade", "self"), ("move", "self", "sea_escape", "run"),
                         ("wait", 9000), ("despawn", "self")])),
    dict(key="sergeant_b", equip=(5745,), name="Patrol-Sergeant Hessk", look=6747, size=1.4, level=21, side="naga", role="enemy",
         health=1.3, abilities=[(12057, 9000)], summoned=True, detection=30.0),
    dict(key="patroller_b", equip=(5745,), name="Spitelash Patroller", look=11265, level=20, side="naga", role="enemy", summoned=True,
         detection=30.0),
    # the class lessons' quarry: a demon on the strand (the warlock's), Snapjaw (the hunter's tracks; 3.26)
    dict(key="tidelure", name="Tidelure Succubus", look=4162, level=20, side="hostile", role="enemy", type="demon",
         caster=True, health=1.5, at="succubus", facing=4.0, respawn=60,
         idle=[("every", 9000, [("visual", "self", 43167)])]),
    dict(key="snapjaw", name="Snapjaw", look=4872, scale=0.5, level=24, side="hostile", role="enemy", type="beast",
         health=2.5, abilities=[(7367, 12000)], at="snapjaw", wander=6.0, respawn=90,
         idle=[("every", 12000, [("emote", "self", "attack"), ("sound", "self", 448)]),
               ("every", 21000, [("sound", "self", 452)])]),
    dict(key="frozen_pool", name="Frozen Tide Pool", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 2000, [("visual", "self", 47543)])]),
    # scenes at the Hollow: the mur'gul from Rethress (3.27), the renegades who cut their lines (3.25)
    dict(key="murgul_messenger", name="Mur'gul Messenger", subname="From Rethress", look="murloc_abyssal", scale=0.9,
         level=8, role="ambient", untouchable=True, summoned=True,
         idle=[("every", 9000, [("emote", "self", "beg"), ("sound", "self", "murloc_fidget")])]),
    dict(key="renegade_1", equip=(5745,), name="Tide-Broken Renegade", look=18389, size=1.15, level=25, role="ambient", untouchable=True,
         summoned=True),
    dict(key="renegade_2", equip=(5284, 0, 5259), name="Tide-Broken Renegade", look=18395, size=1.05, level=25, role="ambient", untouchable=True,
         summoned=True),
    dict(key="renegade_3", equip=(5745,), name="Tide-Broken Renegade", look=22874, size=1.15, level=25, role="ambient", untouchable=True,
         summoned=True),
    dict(key="renegade_4", equip=(5284, 0, 5259), name="Tide-Broken Renegade", look=22871, size=1.05, level=25, role="ambient", untouchable=True,
         summoned=True),

    # ---- memory m3: the Broken Isles (Ssaveth's) -----------------------------------------------------------------
    dict(key="tomb_guard_1", equip=(5745,), name="Guard of the Tomb", look=18398, size=1.2, level=30, role="ambient", untouchable=True,
         at="tg_1", facing=2.52, phase=M3, idle=[("state", "self", "ready_thrown")]),
    dict(key="tomb_guard_2", equip=(5745,), name="Guard of the Tomb", look=22874, size=1.2, level=30, role="ambient", untouchable=True,
         at="tg_2", facing=2.52, phase=M3, idle=[("state", "self", "ready_thrown")]),
    dict(key="tomb_guard_3", equip=(5745,), name="Guard of the Tomb", look=22876, size=1.2, level=30, role="ambient", untouchable=True,
         at="tg_3", facing=2.52, phase=M3, idle=[("state", "self", "ready_thrown")]),
    dict(key="watcher", equip=(5598,), name="Watcher", subname="Maiev's Watchers", plural="watchers", look="warden", looks=WATCHERS,
         level=(20, 22), side="hostile", role="enemy", abilities=[(10277, 10000)],
         at=["w_1", "w_2", "w_3", "w_4", "w_5", "w_6", "w_7", "w_8", "w_9", "w_10"], wander=4.0, respawn=30, phase=M3),
    dict(key="watcher_wave", equip=(5598,), name="Watcher", subname="Maiev's Watchers", plural="watchers", look="warden",
         looks=WATCHERS, level=(21, 22), side="hostile", role="enemy", health=0.75, abilities=[(10277, 11000)],
         detection=45.0, summoned=True),
    dict(key="watcher_over", equip=(5598,), name="Watcher", subname="Maiev's Watchers", look="warden_3", level=22, role="ambient",
         untouchable=True, summoned=True),
    dict(key="restless_spirit", name="Restless Spirit", plural="restless spirits", look=201, looks=[200], level=(21, 22),
         side="hostile", role="enemy", type="undead", health=0.9,
         at=["sp_1", "sp_2", "sp_3", "sp_4", "sp_5", "sp_6", "sp_7", "sp_8", "sp_9"], wander=3.0, respawn=30, phase=M3,
         idle=[("every", 4000, [("visual", "self", 44816), ("visual", "self", 35838)])]),
    dict(key="pit_glow", name="Summoning Pit", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at=["pit_1", "pit_2", "pit_3"], phase=M3, idle=[("every", 5000, [("visual", "self", 32567)])]),
    dict(key="drakthul", equip=(854,), name="Drak'thul", subname="Of the Stormreaver Clan", look=4514, level=35, role="ambient",
         untouchable=True, at="drakthul", facing=0.57, phase=M3,
         gossip="Ha! More of you! Fish-folk and moon-elves, killing each other over a dead man's door. Go on, then. Gul'dan "
                "raised these islands for the same door, and look where it got him.",
         idle=[("every", 4000, [("visual", "self", 35838), ("visual", "self", 44816)]),
               ("every", 19000, [("emote", "self", "laugh"), ("sound", "self", 6943)])]),
    # the scenes' speakers (bible 18.3: summoned for the player who starts the scene)
    dict(key="illidan_m3", equip=(32632, 32633), name="Illidan Stormrage", subname="The Betrayer", look="illidan", size=1.1, level=40,
         role="ambient", untouchable=True, summoned=True, idle=[("every", 8000, [("visual", "self", 35411)])]),
    dict(key="vashj_m3", equip=(23481, 0, 31325), name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         summoned=True),
    dict(key="maiev_m3", equip=(32425, 32425, 27543), name="Maiev Shadowsong", subname="Warden", look="maiev", level=40, role="ambient",
         untouchable=True, summoned=True),
    dict(key="column_1", equip=(5745,), name="Naga of the Column", look=18389, size=1.1, level=25, role="ambient", untouchable=True,
         summoned=True),
    dict(key="column_2", equip=(5284, 0, 5259), name="Naga of the Column", look=18392, size=1.0, level=25, role="ambient", untouchable=True,
         summoned=True),
    dict(key="column_3", equip=(5745,), name="Naga of the Column", look=22875, size=1.1, level=25, role="ambient", untouchable=True,
         summoned=True),
    dict(key="door_fx", name="The Tomb's Door", look="trigger", scale=2.0, level=1, role="ambient", unit_flags=0x02000002,
         summoned=True, idle=[("every", 1200, [("visual", "self", 40108), ("visual", "self", 43401)])]),
    dict(key="doorway_dark", name="The Tomb's Doorway", look="trigger", scale=2.0, level=1, role="ambient",
         unit_flags=0x02000002, summoned=True,
         idle=[("every", 2000, [("visual", "self", 22578), ("visual", "self", 35411)])]),

    # ---- memory m4: the Tomb of Sargeras (Isshara's) ---------------------------------------------------------------
    dict(key="murgul_torch", name="Mur'gul Torchbearer", plural="mur'gul torchbearers", look="murloc_abyssal", scale=0.85,
         level=10, role="ambient", untouchable=True, at=["mt_1", "mt_2", "mt_3", "mt_4"], phase=M4,
         idle=[("every", 4000, [("visual", "self", 45275)]),
               ("every", 23000, [("emote", "self", "cry"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="hall_naga", equip=(5745,), name="Naga of the Deep", look=18389, looks=[22877], size=1.15, level=30, role="ambient",
         untouchable=True, at=["ng_1", "ng_2"], facing=4.0, phase=M4, idle=[("state", "self", "ready_thrown")]),
    dict(key="statue_light", name="The Queen's Statue", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="statue", phase=M4, idle=[("every", 8000, [("visual", "self", 22580), ("visual", "self", 25824)])]),
    dict(key="rune_glow", name="Gul'dan's Rune", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at=["rune_1", "rune_2", "rune_3"], phase=M4, idle=[("every", 6000, [("visual", "self", 22577)])]),
    dict(key="torch_flame", name="Guttering Flame", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at=["tt_1", "tt_2", "tt_3", "tt_4", "tt_5", "dt"], phase=M4),
    dict(key="watcher_gate", equip=(5598,), name="Watcher", subname="Maiev's Watchers", plural="watchers", look="warden",
         looks=WATCHERS, level=(22, 23), side="hostile", role="enemy", health=0.6,
         at=["wg_1", "wg_2", "wg_3", "wg_4", "wg_5", "wg_6"], wander=2.0, respawn=20, phase=M4),
    # the arrival: Vashj ahead in the dark with her bow, Maiev's voice far behind (3.14)
    dict(key="m4_entry", name="The Tomb's Mouth", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="m4_entry", phase=M4,
         watch=(16, [("music", 5174), ("summon", "vashj_m4", "vashj_from", 26), ("state", "vashj_m4", "ready_bow"),
                     ("face", "vashj_m4", "vashj_to"), ("wait", 2500), ("move", "vashj_m4", "vashj_to", "walk"),
                     ("emote", "murgul_torch", "cry"), ("sound", "murgul_torch", "murloc_fidget2"), ("wait", 5000),
                     ("summon", "maiev_voice", "voice_spot", 8),
                     ("yell", "maiev_voice", "I don't know, Naisha, but her image chills me to the core.")], 90000)),
    # the sea gate: Vashj looks back, once (3.20)
    dict(key="gate_watch", name="The Sea Gate", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         at="gate_watch", phase=M4,
         watch=(14, [("summon", "vashj_m4", "vashj_gate", 14), ("face", "vashj_m4", "player"), ("wait", 3000),
                     ("face", "vashj_m4", "vashj_sea"), ("move", "vashj_m4", "vashj_sea", "walk"),
                     ("sound", "vashj_m4", "splash_big")], 60000)),
    dict(key="vashj_m4", equip=(23481, 0, 31325), name="Lady Vashj", look="vashj", size=1.4, level=40, role="ambient", untouchable=True,
         summoned=True),
    dict(key="illidan_m4", equip=(32632, 32633), name="Illidan Stormrage", subname="The Betrayer", look="illidan", size=1.1, level=40,
         role="ambient", untouchable=True, summoned=True, idle=[("every", 8000, [("visual", "self", 35411)])]),
    dict(key="maiev_m4", equip=(32425, 32425, 27543), name="Maiev Shadowsong", subname="Warden", look="maiev", level=40, role="ambient",
         untouchable=True, summoned=True),
    dict(key="maiev_voice", name="Maiev Shadowsong", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True),
    dict(key="watcher_voice", name="Watcher", look="trigger", level=1, role="ambient", unit_flags=0x02000002,
         summoned=True),
    dict(key="naisha", equip=(5598,), name="Naisha", subname="Maiev's Lieutenant", look="warden_4", level=35, role="ambient",
         untouchable=True, summoned=True),
    dict(key="watcher_m4a", equip=(5598,), name="Watcher", subname="Maiev's Watchers", look="warden", level=30, role="ambient",
         untouchable=True, summoned=True),
    dict(key="watcher_m4b", equip=(5598,), name="Watcher", subname="Maiev's Watchers", look="warden_2", level=30, role="ambient",
         untouchable=True, summoned=True),
    # the flashback inside the Tomb: the Highborne before the queen's golden statue (3.17), translucent, a vision
    dict(key="hb_vashj", name="Handmaiden Vashj", look="handmaiden_vashj", level=30, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 3000, [("visual", "self", 44816)])]),
    dict(key="hb_court_1", name="Highborne", look="highborne_1", level=30, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 3000, [("visual", "self", 44816)])]),
    dict(key="hb_court_2", name="Highborne", look="highborne_2", level=30, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 3000, [("visual", "self", 44816)])]),
    dict(key="hb_court_3", name="Highborne", look="highborne_3", level=30, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 3000, [("visual", "self", 44816)])]),
    dict(key="hb_court_4", name="Highborne", look="highborne_4", level=30, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 3000, [("visual", "self", 44816)])]),
    # Gul'dan's last walk in his runes, and the shapes at the gate (3.15)
    dict(key="guldan_ghost", equip=(854,), name="Gul'dan", look="guldan", language="orcish", level=40, role="ambient", untouchable=True, summoned=True,
         idle=[("every", 2500, [("visual", "self", 44816), ("visual", "self", 35838)])]),
    dict(key="shade_1", name="Shape of the Legion", look="felguard", level=40, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 2500, [("visual", "self", 44816), ("visual", "self", 37816)])]),
    dict(key="shade_2", name="Shape of the Legion", look="felguard", level=40, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 2500, [("visual", "self", 44816), ("visual", "self", 37816)])]),
    dict(key="shade_3", name="Shape of the Legion", look="felguard", level=40, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 2500, [("visual", "self", 44816), ("visual", "self", 37816)])]),
    # the Eye of Sargeras, floating over its pedestal (3.19); the stones coming down (3.19, 3.20)
    dict(key="eye", name="The Eye of Sargeras", look=2421, size=1.6, level=40, role="ambient", untouchable=True,
         summoned=True, idle=[("every", 3000, [("visual", "self", 22577), ("visual", "self", 35411)])]),
    dict(key="falling_stone", name="Falling Stone", look="trigger", scale=2.0, level=1, role="ambient",
         unit_flags=0x02000002, summoned=True,
         idle=[("every", 2600, [("visual", "self", 43258), ("visual", "self", 46419)])]),
]

# -- things -------------------------------------------------------------------------------------------------------
OBJECTS = [
    # the sea-shrine and the Spitelash outpost round it
    dict(key="shrine_pool", model=POOL, name="Sesspira's Pool", at="shrine_pool", kind="doodad", scale=1.0),
    dict(key="altar", model=ARK, name="Shrine of Lady Sesspira", at="altar", kind="doodad", facing=4.12, scale=1.1),
    dict(key="altar_pearl", model="great_pearl", name="Song-Pearl", kind="doodad", scale=0.12),
    dict(key="outpost_banner", model="naga_banner", name="The Empress's Sigil", at=["ob_1", "ob_2"], kind="doodad",
         facing=4.12, scale=1.2),
    dict(key="outpost_flag", model=NAGA_FLAG, name="Spitelash Standard", at="pk_4", kind="doodad", scale=0.9),
    dict(key="outpost_torch", model="naga_torch", name="Naga Torch", at=["ot_1", "ot_2", "ot_3"], kind="doodad"),
    dict(key="outpost_pagoda", model="naga_pagoda", name="Spitelash Pagoda", at="pagoda", kind="doodad", facing=0.3),
    dict(key="outpost_weapons", model="naga_weapons", name="Spitelash Weapons", at="weapons", kind="doodad", facing=3.0),
    dict(key="outpost_crate", model="naga_crate", name="Spitelash Crate", at=["crate_1", "crate_2"], kind="doodad"),
    dict(key="outpost_jar", model="naga_jar", name="Sealed Jar", at="jar_1", kind="doodad"),
    dict(key="cage", model=CAGE, name="Spitelash Cage", at="cage", kind="doodad", scale=1.1, facing=5.4),
    dict(key="drowned_ruin", model=RUIN, name="Drowned Ruin", at="drowned_ruin", kind="doodad", scale=0.8, facing=4.4),
    # the sigil-stone (3.23): one of Eldarath's rune-stones with the Empress's sigil cut over the runes
    dict(key="sigil_stone", model=RUNESTONE, name="The Empress's Sigil-Stone", at="sigil_stone", kind="use",
         quest="ch3_shrine", consumable=True, respawn=90, scale=1.3, facing=5.5, goal="Sigil-stone toppled",
         beats=[("sound", "sigil_light", 13092), ("visual", "sigil_light", 34602), ("despawn", "sigil_light"),
                ("object", "broken_stone", "sigil_stone", 90), ("wait", 2500),
                ("summon", "sesspira_image", "image_rise", 16), ("visual", "sesspira_image", 44816),
                ("scale", "sesspira_image", 0.5), ("wait", 600), ("scale", "sesspira_image", 1.0), ("wait", 600),
                ("scale", "sesspira_image", 1.4), ("visual", "sesspira_image", 36005),
                ("face", "sesspira_image", "player"), ("wait", 2500),
                ("say", "sesspira_image", "Little runner. The Empress has a long memory.", "talk"), ("wait", 5500),
                ("emote", "sesspira_image", "omnicast"), ("wait", 1500), ("scale", "sesspira_image", 0.8),
                ("wait", 600), ("scale", "sesspira_image", 0.3), ("despawn", "sesspira_image")]),
    dict(key="broken_stone", model=RUBBLE, name="Broken Sigil-Stone", kind="doodad", scale=0.6),
    # the shore road (3.03): a heap of driftwood to lie still in; the orders, where they fall
    dict(key="blind_a", model=DRIFTWOOD, name="Heap of Driftwood", at="blind_a", kind="use", quest="ch3_ssethis_a",
         consumable=True, respawn=60, scale=1.2, facing=0.9,
         beats=[("summon", "ssethis_a", "patrol_start", 60), ("summon", "patroller_a1", "patrol_start_2", 60),
                ("summon", "patroller_a2", "patrol_start_3", 60), ("move", "ssethis_a", "patrol_stop", "walk"),
                ("move", "patroller_a1", "patrol_stop_2", "walk"), ("move", "patroller_a2", "patrol_stop_3", "walk"),
                ("wait", 14000), ("face", "ssethis_a", "player"), ("wait", 3000), ("face", "ssethis_a", "patrol_turn"),
                ("wait", 1500), ("object", "dropped_orders", "orders_spot", 120),
                ("move", "ssethis_a", "patrol_turn", "walk"), ("move", "patroller_a1", "patrol_turn", "walk"),
                ("move", "patroller_a2", "patrol_turn", "walk")]),
    dict(key="blind_b", model=DRIFTWOOD, name="Heap of Driftwood", at="blind_b", kind="use", quest="ch3_ssethis_b",
         consumable=True, respawn=60, scale=1.2, facing=0.9,
         beats=[("summon", "ssethis_b", "patrol_start", 90), ("summon", "sergeant_b", "patrol_start_2", 90),
                ("summon", "patroller_b", "patrol_start_3", 90), ("move", "ssethis_b", "patrol_stop", "walk"),
                ("move", "sergeant_b", "patrol_stop_2", "walk"), ("move", "patroller_b", "patrol_stop_3", "walk"),
                ("wait", 12000), ("face", "ssethis_b", "player"), ("wait", 1500),
                ("yell", "ssethis_b", "YOU. Heretic! I knew they'd send you. Kill it! KILL IT!", "battle_roar"),
                ("sound", "ssethis_b", "naga_aggro")]),
    dict(key="dropped_orders", model="sack", name="Dropped Patrol Orders", kind="loot", loot=[("orders", 1, 1)],
         quest="ch3_ssethis_a", scale=0.6),
    # Isshara's spring (the shaman's lesson)
    dict(key="spring", model=BASIN, name="Isshara's Spring", at="spring", kind="loot", loot=[("spring_water", 1, 1)],
         quest="ch3_lesson_shaman", scale=1.4),

    # the Hollow: fish traps Snapjaw eats, its tracks, a tide pool, Ssaveth's drawings, his trident, the cask, the sigil
    dict(key="fish_trap", model=TRAP, name="Chewed Fish Trap", at=["trap_1", "trap_2"], kind="doodad", scale=1.0),
    dict(key="tracks", model=TRACKS, name="Snapjaw's Tracks", at=["tr_1", "tr_2", "tr_3"], kind="use",
         quest="ch3_lesson_hunter", consumable=True, respawn=45, scale=1.5, goal="Snapjaw's tracks read",
         beats=[("sound", "ch0:thessk", 1194), ("emote", "snapjaw", "attack")]),
    dict(key="tide_pool_obj", model=POOL, name="Tide Pool", at="tide_pool", kind="use", quest="ch3_lesson_mage",
         consumable=True, respawn=60, scale=0.4, goal="Tide pool frozen",
         beats=[("summon", "frozen_pool", "tide_pool", 40), ("sound", "frozen_pool", 3076)]),
    dict(key="sand_cliff", model=SHELL_2, name="Drawing in the Sand", kind="doodad", scale=0.8),
    dict(key="sand_shrine", model=CORAL, name="Drawing in the Sand", kind="doodad", scale=0.3),
    dict(key="sand_line", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.4),
    dict(key="trident_standing", model=TRIDENT, name="Ssaveth's Trident", kind="doodad", scale=1.4),
    dict(key="trident_loot", model=TRIDENT, name="Ssaveth's Trident", kind="loot", loot=[("trident_item", 1, 1)],
         quest="ch3_trident", scale=1.4),
    dict(key="grog_cask", model="barrel", name="Cask of Valormok Grog", kind="doodad", scale=0.8),
    dict(key="sigil_sand", model=SHELL_2, name="The Empress's Sigil, Drawn in the Sand", kind="use", quest="ch3_name",
         consumable=True, scale=1.8, goal="Your line cut through the sigil",
         beats=[("object", "crossed_lines", "sigil_spot", 900), ("sound", "ch0:szaria", 1194),
                ("emote", "ch0:szaria", "roar")]),
    dict(key="crossed_lines", model=TRIDENT, name="Lines in the Sand", kind="doodad", scale=0.7),
    dict(key="thessa_kelp", model=SEAWEED, name="Kelp Blanket", kind="doodad", scale=0.6),

    # memory m3: Suramar's ruins steaming out of the sea; the Tomb's door; Drak'thul's pits
    dict(key="m3_arch", model=ARCH, name="The Tomb of Sargeras", at="m3_door", kind="doodad", facing=1.57, scale=1.2,
         phase=M3),
    dict(key="sealed_door", model=SEALED_DOOR, name="The Tomb's Door", kind="doodad", scale=0.7, facing=1.57),
    dict(key="m3_head", model=STATUE_HEAD, name="Broken Statue", at="m3_statue", kind="doodad", facing=1.0, scale=0.7,
         phase=M3),
    dict(key="m3_steam", model=STEAM, name="Steam", at=["st_1", "st_2", "st_3"], kind="doodad", phase=M3),
    dict(key="m3_fish", model=FISH_BLUE, name="Dead Fish", at=["fish_1", "fish_2"], kind="doodad", phase=M3),
    dict(key="m3_fish_2", model=FISH_GREEN, name="Dead Fish", at=["fish_3", "fish_4"], kind="doodad", phase=M3),
    dict(key="m3_kelp", model=KELP, name="Kelp", at=["kelp_1", "kelp_2", "kelp_3"], kind="doodad", scale=1.3, phase=M3),
    dict(key="m3_seaweed", model=SEAWEED, name="Seaweed", at=["st_2", "w_9"], kind="doodad", scale=0.8, phase=M3),
    dict(key="m3_pit", model=PIT, name="Summoning Pit", at=["pit_1", "pit_2", "pit_3"], kind="doodad", scale=0.5,
         phase=M3),
    dict(key="m3_bones", model=BONES, name="Bones", at=["bone_1", "bone_2"], kind="doodad", scale=0.8, phase=M3),

    # memory m4: the Tomb's hall, the queen's statue, the runes, the torches, the Eye's pedestal
    dict(key="m4_statue", model=NAGA_STATUE, name="Statue of Queen Azshara", at="statue", kind="doodad", facing=2.89,
         scale=1.3, phase=M4),
    dict(key="golden_statue", model=GOLDEN_STATUE, name="Statue of Queen Azshara", kind="doodad", scale=1.1),
    dict(key="tail_statue", model=NAGA_STATUE, name="Statue of Queen Azshara", kind="doodad", scale=1.1),
    dict(key="m4_pedestal", model=ARK, name="Pedestal", at="eye_spot", kind="doodad", facing=2.4, phase=M4),
    dict(key="m4_torch", model="naga_torch", name="Naga Torch", at=["lt_1", "lt_2", "lt_3", "lt_4", "lt_5"],
         kind="doodad", phase=M4),
    dict(key="guttering_torch", model=DEAD_TORCH, name="Guttering Torch", at=["tt_1", "tt_2", "tt_3", "tt_4", "tt_5"],
         kind="use", quest="ch3_torches", consumable=True, respawn=45, goal="Guttering torch relit", phase=M4,
         beats=[("aura", "torch_flame", "torch_fire"), ("sound", "torch_flame", 1484), ("face", "murgul_torch", "player"),
                ("emote", "murgul_torch", "kiss"), ("sound", "murgul_torch", "murloc_fidget")]),
    dict(key="drowned_torch", model=DEAD_TORCH, name="Torch at the Water's Edge", at="dt", kind="use",
         quest="ch3_torches", consumable=True, respawn=45, goal="Torch at the water's edge relit", phase=M4,
         beats=[("aura", "torch_flame", "torch_fire"), ("face", "murgul_torch", "player"), ("emote", "murgul_torch", "kiss"),
                ("wait", 5000), ("unaura", "torch_flame", "torch_fire"), ("sound", "torch_flame", "splash"),
                ("emote", "murgul_torch", "cry"), ("sound", "murgul_torch", "murloc_wound")]),
    dict(key="rune_1", model=RUNESTONE, name="Gul'dan's Rune", at="rune_1", kind="use", quest="ch3_runes",
         consumable=True, respawn=60, facing=5.0, goal="The first rune touched", phase=M4,
         beats=[("summon", "guldan_ghost", "g1_from", 12), ("visual", "guldan_ghost", 44816),
                ("sound", "guldan_ghost", 3418), ("move", "guldan_ghost", "g1_to", "walk"), ("wait", 7000),
                ("despawn", "guldan_ghost")]),
    dict(key="rune_2", model=RUNESTONE, name="Gul'dan's Rune", at="rune_2", kind="use", quest="ch3_runes",
         consumable=True, respawn=60, facing=0.6, goal="The second rune touched", phase=M4,
         beats=[("summon", "guldan_ghost", "g2_from", 14), ("visual", "guldan_ghost", 44816),
                ("sound", "guldan_ghost", 3418), ("move", "guldan_ghost", "g2_to", "walk"), ("wait", 5000),
                ("face", "guldan_ghost", "player"), ("wait", 2500), ("face", "guldan_ghost", "statue"), ("wait", 1500),
                ("despawn", "guldan_ghost")]),
    dict(key="rune_3", model=RUNESTONE, name="Gul'dan's Rune", at="rune_3", kind="use", quest="ch3_runes",
         consumable=True, respawn=60, facing=2.0, goal="The rune at the gate touched", phase=M4,
         beats=[("summon", "guldan_ghost", "g3_from", 16), ("visual", "guldan_ghost", 44816),
                ("move", "guldan_ghost", "g3_to", "walk"), ("wait", 4000),
                ("summon", "shade_1", "shade_1", 9), ("summon", "shade_2", "shade_2", 9), ("summon", "shade_3", "shade_3", 9),
                ("move", "shade_1", "g3_to", "run"), ("move", "shade_2", "g3_to", "run"), ("move", "shade_3", "g3_to", "run"),
                ("wait", 1500), ("emote", "shade_1", "attack"), ("emote", "shade_2", "attack"),
                ("emote", "guldan_ghost", "wound"), ("sound", "guldan_ghost", 1322), ("wait", 900),
                ("emote", "shade_3", "attack"), ("state", "guldan_ghost", "dead"), ("wait", 3000),
                ("despawn", "shade_1"), ("despawn", "shade_2"), ("despawn", "shade_3"), ("wait", 1500),
                ("despawn", "guldan_ghost")]),
]

# -- items --------------------------------------------------------------------------------------------------------
ITEMS = [
    # what the quests ask for and hand over
    dict(key="orders", name="Patrol Orders", icon=1096,
         description="Sealed with Lady Sesspira's sigil. Watches, tides, and who stands where at the shrine."),
    dict(key="gate_pearl", name="Song-Pearl: The Gate", icon=16209,
         description="Hold it to your ear: a trident on stone, and someone young breathing hard."),
    dict(key="tomb_pearl", name="Song-Pearl: The Tomb", icon=24730,
         description="Warm, as if someone has just let go of it. It hums in the dark."),
    dict(key="spring_water", name="Flask of Spring Water", icon=18084,
         description="Sweet water from under the oldest cliffs in Azshara."),
    dict(key="trident_item", name="Ssaveth's Trident", icon=8747,
         description="Salt has started on the barbs. He drove it in hard."),
    dict(key="message_shell", name="Shell from Mrgl-Who-Counts", icon=7714,
         description="Scratched on the inside: the crèche. A row of hatchlings. Four sirens in a ring around one of "
                     "them, and that one's eyes scratched out."),

    # rewards (the game's quests' greens at these levels)
    dict(key="gate_trident", name="Shrine-Breaker Trident", kind="weapon:spear", quality=2, level=21,
         stats=[("str", 6), ("sta", 4)]),
    dict(key="gate_knife", name="Picket-Gutter Knife", kind="weapon:dagger", quality=2, level=21,
         stats=[("agi", 4), ("sta", 3)]),
    dict(key="gate_rod", name="Pearl-Diver's Rod", kind="weapon:staff", quality=2, level=21,
         stats=[("int", 6), ("spi", 4)]),
    dict(key="gate_mantle", name="Mantle of the Gate-Guard", kind="armor:mail:shoulder", quality=2, level=22,
         stats=[("str", 4), ("sta", 4)]),
    dict(key="ruin_spaulders", name="Ruinwalker Spaulders", kind="armor:leather:shoulder", quality=2, level=22,
         stats=[("agi", 4), ("sta", 4)]),
    dict(key="suramar_amice", name="Suramar Silk Amice", kind="armor:cloth:shoulder", quality=2, level=22,
         stats=[("int", 4), ("spi", 3)]),
    dict(key="tidecaller_choker", name="Tidecaller's Choker", kind="neck", quality=2, level=23,
         stats=[("int", 3), ("spi", 3), ("sta", 2)]),
    dict(key="coral_band", name="Vyrash's Coral Band", kind="ring", quality=2, level=23, stats=[("str", 3), ("sta", 3)]),
    dict(key="shrine_cloak", name="Shrine-Silk Cloak", kind="armor:cloth:back", quality=2, level=23,
         stats=[("agi", 3), ("sta", 3)]),
    dict(key="gate_legguards", name="Sea-Gate Legguards", kind="armor:mail:legs", quality=2, level=24,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="tomb_breeches", name="Tomb-Runner Breeches", kind="armor:leather:legs", quality=2, level=24,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="torch_leggings", name="Torchbearer's Leggings", kind="armor:cloth:legs", quality=2, level=24,
         stats=[("int", 6), ("spi", 4), ("sta", 2)]),
    dict(key="moonstone", name="Isshara's Moonstone", kind="trinket", quality=3, level=24, stats=[("sta", 5), ("spi", 5)],
         description="A handmaiden's earring, worn ten thousand years. The stone is cloudy, like her eyes."),
    dict(key="grog", name="Valormok Grog", kind="drink", level=25, icon=18084,
         description="There's an axe-mark on the cask it came in."),
    dict(key="valormok_axe", name="Valormok Hand-Axe", kind="weapon:axe", quality=2, level=24,
         stats=[("str", 5), ("sta", 3)], description="Paid over without a word, and without a look away."),
    dict(key="sigil_gauntlets", name="Sigil-Breaker Gauntlets", kind="armor:mail:hands", quality=2, level=24,
         stats=[("str", 4), ("sta", 4)]),
    dict(key="acolyte_gloves", name="Acolyte-Hide Gloves", kind="armor:leather:hands", quality=2, level=24,
         stats=[("agi", 4), ("sta", 4)]),
    dict(key="ash_handwraps", name="Shrine-Ash Handwraps", kind="armor:cloth:hands", quality=2, level=24,
         stats=[("int", 4), ("spi", 4)]),
    dict(key="tabard", name="Tabard of the Tide-Broken", kind="tabard", quality=1, level=20,
         description="No sigil on it. Lines, crossing."),
    dict(key="snapjaw_stew", name="Snapjaw Stew", kind="food", level=25, icon=7996,
         description="Vyssa's. It's terrible. Eat it anyway."),
    dict(key="broken_sabatons", name="Tide-Broken Sabatons", kind="armor:mail:feet", quality=2, level=24,
         stats=[("str", 5), ("sta", 4)]),
    dict(key="broken_treads", name="Tide-Broken Treads", kind="armor:leather:feet", quality=2, level=24,
         stats=[("agi", 5), ("sta", 4)]),
    dict(key="broken_slippers", name="Tide-Broken Slippers", kind="armor:cloth:feet", quality=2, level=24,
         stats=[("int", 5), ("spi", 4)]),
    # the lessons' small rewards
    dict(key="kessh_buckler", name="Kessh's Drill Buckler", kind="shield", quality=2, level=20,
         stats=[("sta", 3), ("str", 2)]),
    dict(key="snaptamer_ring", name="Snaptamer's Thumb-Ring", kind="ring", quality=2, level=20,
         stats=[("agi", 3), ("sta", 2)]),
    dict(key="quickfin_knife", name="Quickfin's Pocket-Knife", kind="weapon:dagger", quality=2, level=20,
         stats=[("agi", 3), ("sta", 2)]),
    dict(key="rime_shell", name="Rime-Kissed Shell", kind="offhand", quality=2, level=20, stats=[("int", 3), ("spi", 2)]),
    dict(key="sea_glass", name="Ulmara's Sea-Glass", kind="offhand", quality=2, level=20, stats=[("int", 2), ("spi", 3)]),
    dict(key="siren_charm", name="Siren-Bone Charm", kind="offhand", quality=2, level=20, stats=[("int", 2), ("sta", 3)]),
]

# -- auras --------------------------------------------------------------------------------------------------------
AURAS = [
    # the flashback inside Isshara's memory (3.17): the Caverns of Time's warp on the screen while the Highborne kneel
    dict(key="time_warp", name="The Queen's Court", kind="screen", screen=161, seconds=24),
    # the light dims as Ssaveth falls on the steps (3.10)
    dict(key="dim", name="The Light Dims", kind="screen", screen=201, seconds=3),
    # a guttering torch relit (3.18): the flame on its unseen keeper
    dict(key="torch_fire", name="Torch Flame", kind="mark", seconds=150, icon=51195, visual=11228, text="Burning."),
]

# -- memories -----------------------------------------------------------------------------------------------------
MEMORIES = [
    dict(key="m3", name="The Broken Isles", whose="Ssaveth", bit="A",
         text="Ssaveth's memory, sung by Isshara: the Broken Isles, the night the Tomb was found. What he saw, you see.",
         stage="m3_arrive", facing=4.74, centre="m3_centre", radius=110, pool="hollow_pool", pool_facing=0.0,
         singer="ch0:isshara", again="Sing Ssaveth's song again. Let me go back to the stair."),
    dict(key="m4", name="The Tomb of Sargeras", whose="Isshara", bit="B",
         text="Isshara's memory: the Tomb of Sargeras, under the Broken Isles. What she saw, you see.",
         stage="m4_arrive", facing=5.93, centre="m4_centre", radius=135, pool="hollow_pool", pool_facing=0.0,
         singer="ch0:isshara", again="Sing the Tomb again."),
]

# -- quests -------------------------------------------------------------------------------------------------------
QUESTS = [
    # 3.01: Sesspira's hand (from the rocks above the shrine: Vyrash sings Sesspira's image up out of the pool)
    dict(key="ch3_hand", title="Sesspira's Hand", giver="ch0:szaria", ender="ch0:szaria", level=20, min=19, xp=8,
         tone="serious", prev="ch2:ch2_end", explore="lookout", radius=10,
         goal="Climb to the shoulder of rock above the Spitelash's sea-shrine, on the strand below the Ruins of "
              "Eldarath's north-east cliffs, and watch what the Tidecaller does there.",
         text="Isshara says her pearls are at the Ruins of Eldarath. I say Isshara is blind and hopeful. So you go and "
              "look. Below the ruins, where the cliffs come down to the strand, the Spitelash keep a shrine to Lady "
              "Sesspira, and a tidecaller keeps the shrine. There's a shoulder of rock up the cliff that looks straight "
              "down on it. Get up there. Don't fight. Don't be seen. Watch, and come back and tell me what's on that "
              "altar.",
         progress="Well? What's on the altar?",
         reward="Two pearls, and a siren singing Sesspira's face up out of a puddle. Hm. Isshara will be unbearable. "
                "Sesspira watches Krellian for the Empress, and Krellian is the Empress's fist. If they've given her the "
                "keeper's songs to guard, they know what the songs are worth.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "lookout"),
                 ("emote", "self", "spell"), ("wait", 2000), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "sea_east"), ("wait", 2500),
                   ("face", "self", "player"), ("emote", "self", "roar")],
         poi=["lookout"]),

    # 3.02: the pickets (Ssaveth draws the ruins in the sand and stabs each picket's place)
    dict(key="ch3_pickets", title="Spitelash Pickets", giver="ch0:ssaveth", ender="ch0:ssaveth", level=20, xp=8,
         tone="serious", prev="ch3_hand", kill=[("picket", 10)],
         goal="Kill 10 Spitelash Pickets at the ruins' edge, north and south of the sea-shrine below Eldarath.",
         text="A shrine has a wall even when it has no wall. Pickets. Here, and here, and here. They stand where they can "
              "see the strand and the cliff path both. Ten of them. When the pickets are gone, the shrine is blind on the "
              "land side, and the land side is where we come in.",
         progress="How many still stand?",
         reward="Ten. Good. Now they'll send new ones, and the new ones won't know the ground. That is how a shrine is "
                "taken. Slowly. Then all at once.",
         details=["battle_roar"], reward_emotes=["roar"],
         accept=[("move", "self", "ssaveth_draw", "walk"), ("wait", 5000), ("face", "self", "draw_1"),
                 ("emote", "self", "work"), ("object", "sand_cliff", "draw_1", 120), ("wait", 1500),
                 ("emote", "self", "work"), ("object", "sand_shrine", "draw_2", 120), ("wait", 1500),
                 ("emote", "self", "work"), ("object", "sand_line", "draw_3", 120), ("wait", 1500),
                 ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 900), ("face", "self", "draw_2"),
                 ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 900), ("face", "self", "draw_3"),
                 ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "roar"), ("wait", 4000), ("evade", "self")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "battle_roar"),
                   ("sound", "self", "naga_aggro")],
         poi=["pickets"]),

    # 3.03 (two versions, by chapter 1's road): Ssethis on the shore road
    dict(key="ch3_ssethis_a", title="Ssethis, Again", giver="ch0:szaria", ender="ch0:szaria", level=20, xp=8,
         tone="serious", prev=["ch3_hand", "ch1:ch1_rival_a"], items=[("orders", 1)],
         goal="Lie still in the heap of driftwood on the shore road north of the sea-shrine until the Spitelash patrol "
              "passes, and bring Lady Szaria its orders.",
         text="A patrol walks the shore road north of the shrine twice a tide, and it carries the shrine's orders: who "
              "stands where, and when the watches change. I want them. There's a heap of driftwood on the road where a "
              "naga can lie still. Lie still. Let the patrol come to you.",
         progress="The orders?",
         reward="He dropped them. On purpose? The Spitelash don't drop things on purpose. ...You know him. No, don't tell "
                "me. I can see it on you, and I don't need to know.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "road"),
                 ("emote", "self", "spell"), ("wait", 2000), ("face", "self", "player")],
         complete=[("emote", "self", "work"), ("sound", "self", 1192), ("wait", 2000), ("emote", "self", "talk"),
                   ("wait", 2000), ("face", "self", "sea_east"), ("wait", 1500), ("face", "self", "player")],
         poi=["blind_a", "road"]),
    dict(key="ch3_ssethis_b", title="Ssethis, Again", giver="ch0:szaria", ender="ch0:szaria", level=20, xp=8,
         tone="serious", prev=["ch3_hand", "ch1:ch1_rival_b"], items=[("orders", 1)],
         drops={"orders": [("sergeant_b", 100)]},
         goal="Lie still in the heap of driftwood on the shore road north of the sea-shrine until the Spitelash patrol "
              "passes, and bring Lady Szaria its orders.",
         text="A patrol walks the shore road north of the shrine twice a tide, and its sergeant carries the shrine's "
              "orders: who stands where, and when the watches change. I want them. There's a heap of driftwood on the "
              "road where a naga can lie still. Lie still. Let the patrol come to you.",
         progress="The orders?",
         reward="He knew you. The one who ran into the sea, bleeding, screaming your name. That one will come back, and "
                "he'll come back with friends. You make enemies the way Vyssa makes soup: too many, all at once.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "road"),
                 ("emote", "self", "spell"), ("wait", 2000), ("face", "self", "player")],
         complete=[("emote", "self", "work"), ("sound", "self", 1192), ("wait", 2000), ("emote", "self", "talk"),
                   ("wait", 2000), ("face", "self", "road"), ("wait", 1500), ("face", "self", "player")],
         poi=["blind_b", "road"]),

    # 3.04: the gate pearl ("This one isn't mine.")
    dict(key="ch3_gate", title="The Gate Pearl", giver="ch0:isshara", ender="ch0:isshara", level=21, xp=8,
         tone="serious", prev="ch3_pickets", prev_any=["ch3_ssethis_a", "ch3_ssethis_b"], kill=[("shrinewarden", 1)],
         items=[("gate_pearl", 1)], drops={"gate_pearl": [("shrinewarden", 100)]},
         goal="Kill the Spitelash Shrinewarden at the sea-shrine's gate below Eldarath, and bring Isshara the Song-Pearl "
              "he carries.",
         text="The orders say the shrinewarden carries one pearl and the tidecaller keeps the other. I can hear them from "
              "here, little one: two songs, very faint, like someone humming in another room. Bring me the warden's "
              "first. I want to know whose voice is in it.",
         progress="Is it in your hand? I can't hear it yet.",
         reward="Give it... ah. Ah. No. This one isn't mine. Listen: a trident on stone, and someone young breathing hard. "
                "I know that breath. So do you. He's standing over there pretending not to listen.",
         details=["talk"], reward_emotes=["talk"], choice=["gate_trident", "gate_knife", "gate_rod"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("sound", "self", "siren_hiss"), ("wait", 3000), ("state", "self", "none"), ("face", "self", "lookout"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player")],
         complete=[("state", "self", "channel"), ("wait", 3000), ("state", "self", "none"), ("face", "self", "ssaveth_spot"),
                   ("say", "self", "This one isn't mine.", "talk"), ("wait", 1500), ("face", "ch0:ssaveth", "isshara_spot"),
                   ("emote", "ch0:ssaveth", "stun"), ("wait", 3000), ("face", "self", "player")],
         poi=["shrinewarden"]),

    # 3.05: Ssaveth's song (he won't listen: his back to the pool)
    dict(key="ch3_song", title="Ssaveth's Song", giver="ch0:isshara", ender="ch0:ssaveth_young", level=21, xp=8,
         tone="serious", prev="ch3_gate", memory="m3", explore="m3_ssaveth", radius=9,
         goal="Touch the water while Isshara sings Ssaveth's pearl. In his memory, go to young Ssaveth at the foot of "
              "the great stair.",
         text="It's his. Ssaveth's. Serena's singers took it out of him years ago, and he never knew what he'd lost; only "
              "that there was a hole where a night should be. He won't come to the pool. Let him stand there with his "
              "back to it. You touch the water. I'll sing. If he won't hear it, someone should.",
         progress="The stair. He's at the foot of the stair.",
         reward="You're late. The column's been coming up out of the water all night. Stand here, by me. The master says "
                "this is the place.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "ch0:ssaveth", "away_from_pool"), ("state", "ch0:ssaveth", "ready_thrown"), ("face", "self", "player"),
                 ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"), ("sound", "self", "siren_hiss"),
                 ("music", 9461), ("visual", "self", 36005), ("visual", "self", 57771), ("wait", 3500), ("relive", "m3"), ("wait", 2000),
                 ("state", "self", "none")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1200), ("face", "self", "m3_door"),
                   ("emote", "self", "point"), ("wait", 1500), ("face", "self", "m3_ruins"),
                   ("state", "self", "ready_thrown")],
         poi=["m3_ssaveth"]),

    # 3.06: new islands (the column comes up through Suramar's ruins; they go quiet at the broken statue)
    dict(key="ch3_islands", title="New Islands", giver="ch0:ssaveth_young", ender="ch0:ssaveth_young", level=21, xp=8,
         tone="serious", prev="ch3_song", memory="m3", explore="m3_statue", radius=12,
         goal="In Ssaveth's memory, go down into the ruins to the great broken statue, and walk back up to the stair "
              "with the column.",
         text="Islands. Yesterday there was only sea here. Now there are islands, and towers, and stairs, and all of it "
              "steaming and stinking of fish. The column is still coming up through the ruins behind the master. Go down "
              "to them. Walk up with them. Don't touch anything.",
         progress="Are they coming?",
         reward="The whole column, up out of the sea and through a dead city. Did you see them go quiet at the statue? "
                "Nobody told them to. Everyone just... did.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "m3_ruins"), ("emote", "self", "point"), ("music", 9462),
                 ("summon", "illidan_m3", "col_illidan", 40), ("summon", "column_1", "col_1", 45),
                 ("summon", "column_2", "col_2", 45), ("summon", "column_3", "col_3", 45),
                 ("face", "column_1", "m3_statue_eye"), ("face", "column_2", "m3_statue_eye"),
                 ("face", "column_3", "m3_statue_eye"), ("wait", 3000), ("move", "illidan_m3", "col_illidan_end", "walk"),
                 ("wait", 4000), ("emote", "column_1", "bow"), ("emote", "column_2", "bow"), ("emote", "column_3", "kneel"),
                 ("wait", 5000), ("move", "column_1", "col_1_end", "walk"), ("move", "column_2", "col_2_end", "walk"),
                 ("move", "column_3", "col_3_end", "walk"), ("face", "self", "player"), ("state", "self", "ready_thrown")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "m3_door"),
                   ("wait", 1500), ("emote", "self", "bow"), ("wait", 1500), ("face", "self", "m3_ruins")],
         poi=["m3_statue"]),

    # 3.07: at last (Illidan at the Tomb's door: the door blown open, and he goes in with Vashj)
    dict(key="ch3_atlast", title="At Last", giver="ch0:ssaveth_young", ender="ch0:ssaveth_young", level=21, xp=8,
         tone="serious", prev="ch3_islands", memory="m3", event="The Tomb of Sargeras found",
         goal="In Ssaveth's memory, go up the great stair and stand by while Illidan opens the Tomb's door.",
         text="He's at the top. The master. Standing at that door with his face to it, like he can see through stone. "
              "Maybe he can. Go up. When he speaks, listen. I'll hold the foot of the stair.",
         progress="Up. Up the stair.",
         reward="In. Into the dark, him and the Lady both, and the door still smoking. And us out here. 'My trusted "
                "servants.' He said trusted.",
         details=["talk", "point"], reward_emotes=["talk", "salute"],
         accept=[("face", "self", "m3_door"), ("emote", "self", "point"), ("summon", "illidan_m3", "illidan_top", 30),
                 ("summon", "vashj_m3", "vashj_top", 30), ("object", "sealed_door", "m3_door", 20),
                 ("face", "illidan_m3", "m3_door"), ("face", "vashj_m3", "m3_door"), ("wait", 6000),
                 ("yell", "illidan_m3", "At last! The Tomb of Sargeras is found!"), ("wait", 3500),
                 ("say", "illidan_m3", "Evil draws close.", None, "IllidanYes4"), ("wait", 2500),
                 ("face", "illidan_m3", "stair_mid"),
                 ("yell", "illidan_m3", "You, my trusted servants, must remain here and guard the entrance. If that "
                                        "wretched warden managed to reach this island, she'll certainly try to follow us."),
                 ("wait", 7000), ("face", "illidan_m3", "m3_door"), ("emote", "illidan_m3", "spell"),
                 ("summon", "door_fx", "m3_door", 5), ("sound", "door_fx", 12549), ("visual", "player", 61029),
                 ("wait", 1200), ("summon", "doorway_dark", "m3_door_in", 120), ("wait", 2500),
                 ("move", "illidan_m3", "m3_door_in", "walk"), ("move", "vashj_m3", "m3_door_in", "walk"),
                 ("wait", 4000), ("despawn", "illidan_m3"), ("despawn", "vashj_m3"), ("credit", "ch3_atlast"),
                 ("face", "self", "m3_ruins")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "tomb_guard_1", "salute"),
                   ("emote", "tomb_guard_2", "salute"), ("face", "self", "m3_ruins"), ("state", "self", "ready_thrown")],
         poi=["m3_door"]),

    # 3.08: guard the entrance (Maiev's Watchers come up through the ruins)
    dict(key="ch3_entrance", title="Guard the Entrance", giver="ch0:ssaveth_young", ender="ch0:ssaveth_young", level=22,
         xp=8, tone="serious", prev="ch3_atlast", memory="m3", kill=[("watcher", 10)],
         goal="In Ssaveth's memory, kill 10 Watchers coming up through the ruins toward the Tomb's stair.",
         text="Night elves. In the ruins, more of them every time I look. Green cloaks, moon-blades. They followed us "
              "across the whole sea. The master said guard the entrance. So: we guard it.",
         progress="More of them. Always more.",
         reward="They fight like they've waited ten thousand years for it. So have we.",
         details=["battle_roar"], reward_emotes=["battle_roar"],
         accept=[("summon", "maiev_m3", "maiev_near", 10), ("visual", "maiev_m3", 36937),
                 ("yell", "maiev_m3", "More naga! Slay them, sisters!"), ("wait", 2500), ("face", "self", "m3_ruins"),
                 ("yell", "self", "Night elves! Kill them all in the empress' name!", "battle_roar"), ("wait", 2500),
                 ("yell", "self", "Land-walkers! Destroy them quickly!", "battle_roar"), ("sound", "self", "naga_aggro"),
                 ("emote", "tomb_guard_1", "battle_roar"), ("emote", "tomb_guard_2", "roar"),
                 ("emote", "tomb_guard_3", "battle_roar"), ("visual", "maiev_m3", 36937), ("despawn", "maiev_m3"),
                 ("music", 6077)],
         complete=[("face", "self", "player"),
                   ("say", "self", "After ten thousand years, our revenge... is at hand.", None, "NagaMyrmadonPissed1"),
                   ("wait", 5500), ("emote", "self", "battle_roar"), ("face", "self", "m3_ruins")],
         poi=["plaza"]),

    # 3.09: ghosts of the pits (and an old orc's ghost laughing at both sides)
    dict(key="ch3_pits", title="Ghosts of the Pits", giver="ch0:ssaveth_young", ender="ch0:ssaveth_young", level=22,
         xp=8, tone="serious", prev="ch3_entrance", memory="m3", kill=[("restless_spirit", 8)],
         goal="In Ssaveth's memory, kill 8 Restless Spirits rising from the three green-glowing pits in the ruins below "
              "the stair.",
         text="Something in the ruins doesn't like any of us. There are pits down there glowing green, and bones climbing "
              "out of them, and they kill night elves and naga the same. And there's an orc. A dead orc, I think. He "
              "laughs. Make the bones lie down.",
         progress="Still climbing out?",
         reward="The orc stopped laughing for one breath when the last of them fell. Then he started again. I don't think "
                "he was laughing at us. I think he was laughing at all of it.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "pits"), ("emote", "self", "point"), ("wait", 1500), ("emote", "drakthul", "laugh"),
                 ("sound", "drakthul", 6943), ("wait", 2000), ("face", "self", "player")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "drakthul", "laugh"),
                   ("sound", "drakthul", 6943), ("wait", 1500), ("face", "self", "m3_ruins")],
         poi=["pits"]),

    # 3.10: Ash-thero-sauguine (a set piece: the main force on the stair; the guards fall; a glaive; the fade)
    dict(key="ch3_ash", title="Ash-thero-sauguine", giver="ch0:ssaveth_young", ender="ch0:ssaveth", level=22, xp=8,
         tone="serious", prev="ch3_pits", memory="m3", wake=True, time=300, kill=[("watcher_wave", 12)],
         event="The stair held to the end",
         goal="In Ssaveth's memory, hold the great stair against Maiev's main force: kill 12 of the Watchers who come up "
              "it within 5 minutes, and stay with the guards to the end.",
         text="Horns in the ruins. All of them, this time. The warden herself. Stand on the steps with me and don't give "
              "them a single stair. Whatever happens. Whatever happens to me.",
         progress="...",
         reward="...You were there. On the steps. I... a glaive. I remember a glaive, and then nothing, and then a ship, "
                "and nobody would tell me what had happened to the others. I thought I'd run. All these years, I "
                "thought I ran.",
         details=["battle_roar"], reward_emotes=["talk"], choice=["gate_mantle", "ruin_spaulders", "suramar_amice"],
         accept=[("music", 6077), ("sound", "self", 7054), ("summon", "maiev_m3", "maiev_near", 8),
                 ("visual", "maiev_m3", 36937), ("yell", "maiev_m3", "More of the vile serpents! Let none survive!"),
                 ("wait", 2500), ("face", "self", "m3_ruins"),
                 ("yell", "self", "Ash-thero-sauguine! Ba'anthalso-dorei!", "battle_roar"), ("sound", "self", "naga_aggro"),
                 ("emote", "tomb_guard_1", "battle_roar"), ("emote", "tomb_guard_2", "battle_roar"),
                 ("emote", "tomb_guard_3", "battle_roar"), ("visual", "maiev_m3", 36937), ("despawn", "maiev_m3"),
                 # the waves: two at a time up the ruins, every sixteen seconds (eighteen in all, for twelve)
                 ("summon", "watcher_wave", "wave_1", 170), ("summon", "watcher_wave", "wave_2", 170), ("wait", 16000),
                 ("summon", "watcher_wave", "wave_3", 170), ("summon", "watcher_wave", "wave_4", 170), ("wait", 16000),
                 ("summon", "watcher_wave", "wave_5", 170), ("summon", "watcher_wave", "wave_6", 170),
                 ("emote", "tomb_guard_1", "wound"), ("sound", "tomb_guard_1", "naga_death"),
                 ("state", "tomb_guard_1", "dead"), ("wait", 16000),
                 ("summon", "watcher_wave", "wave_1", 170), ("summon", "watcher_wave", "wave_3", 170), ("wait", 14000),
                 # the warden among the guards
                 ("summon", "maiev_m3", "maiev_blink", 6), ("visual", "maiev_m3", 36937),
                 ("say", "maiev_m3", "Tor ilisar'thera'nal!", None, "MaievWarcry1"), ("emote", "maiev_m3", "attack"),
                 ("emote", "tomb_guard_2", "wound"), ("sound", "tomb_guard_2", "naga_death"),
                 ("state", "tomb_guard_2", "dead"), ("summon", "watcher_wave", "wave_2", 170),
                 ("summon", "watcher_wave", "wave_5", 170), ("wait", 2500), ("visual", "maiev_m3", 36937),
                 ("despawn", "maiev_m3"), ("wait", 13500),
                 ("summon", "watcher_wave", "wave_4", 170), ("summon", "watcher_wave", "wave_6", 170), ("wait", 16000),
                 ("summon", "watcher_wave", "wave_1", 170), ("summon", "watcher_wave", "wave_2", 170),
                 ("emote", "tomb_guard_3", "wound"), ("sound", "tomb_guard_3", "naga_death"),
                 ("state", "tomb_guard_3", "dead"), ("wait", 16000),
                 ("summon", "watcher_wave", "wave_3", 170), ("summon", "watcher_wave", "wave_5", 170), ("wait", 16000),
                 ("summon", "watcher_wave", "wave_4", 170), ("summon", "watcher_wave", "wave_6", 170), ("wait", 14000),
                 # the end: a glaive, and young Ssaveth falls; the light dims; a Watcher steps over him; the fade
                 ("summon", "maiev_m3", "maiev_blink", 10), ("visual", "maiev_m3", 36937),
                 ("face", "maiev_m3", "m3_ssaveth"), ("cast", "maiev_m3", 36507, "ch0:ssaveth_young"), ("wait", 700),
                 ("emote", "self", "wound"), ("sound", "self", "naga_wound"), ("wait", 600), ("state", "self", "dead"),
                 ("sound", "self", "naga_death"), ("credit", "ch3_ash"), ("aura", "player", "dim"),
                 ("summon", "watcher_over", "over_from", 10), ("move", "watcher_over", "m3_ssaveth_near", "walk"),
                 ("wait", 2500), ("visual", "maiev_m3", 36937), ("despawn", "maiev_m3"), ("wait", 9000),
                 ("state", "self", "ready_thrown"), ("state", "tomb_guard_1", "ready_thrown"),
                 ("state", "tomb_guard_2", "ready_thrown"), ("state", "tomb_guard_3", "ready_thrown")],
         complete=[("face", "self", "player"), ("wait", 2000), ("emote", "self", "wound"), ("sound", "self", "naga_wound"),
                   ("wait", 3000), ("face", "self", "sea_east"), ("state", "self", "ready_thrown")],
         poi=["m3_ssaveth"]),

    # 3.11: what he didn't remember (the trident left standing in the sand; a roar at the sea)
    dict(key="ch3_after", title="What He Didn't Remember", giver="ch0:ssaveth", ender="ch0:szaria", level=22, xp=8,
         tone="serious", prev="ch3_ash",
         goal="Leave Ssaveth to himself, and go to Lady Szaria.",
         text="Isshara says the others died on the steps. Every one of them. And I lived, and didn't remember them, and "
              "didn't remember living. ...Go to Szaria. Tell her I'll take the next watch. Tell her I'm fine.",
         reward="He's fine. Of course he is. He left his trident standing in the sand down on the beach and went off along "
                "the shore like a hatchling who's been told his mother's dead. Leave him. He'll come back when the tide "
                "does.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("wait", 4000), ("move", "self", "trident_spot", "walk"), ("wait", 4500),
                 ("face", "self", "trident_sand"), ("emote", "self", "work"), ("object", "trident_standing", "trident_sand", 1800),
                 ("sound", "self", 977), ("wait", 2500), ("face", "self", "sea_look"), ("wait", 2500),
                 ("emote", "self", "roar"), ("sound", "self", "naga_aggro"), ("wait", 3000),
                 ("move", "self", "beach_away", "walk"), ("wait", 16000), ("evade", "self")],
         complete=[("face", "self", "beach_away"), ("wait", 2000), ("emote", "self", "talk"), ("wait", 1500),
                   ("face", "self", "player")]),

    # 3.12: the Tomb pearl (Vyrash sings Sesspira's image up to fight beside her)
    dict(key="ch3_tomb_pearl", title="The Tomb Pearl", giver="ch0:szaria", ender="ch0:isshara", level=23, xp=8,
         tone="serious", prev="ch3_after", kill=[("vyrash", 1)], items=[("tomb_pearl", 1)],
         drops={"tomb_pearl": [("vyrash", 100)]},
         goal="Kill Tidecaller Vyrash at her sea-shrine below the Ruins of Eldarath, and bring Isshara the Song-Pearl she "
              "carries.",
         text="The second pearl. The tidecaller keeps it on her, and she sings Sesspira up out of that pool whenever she's "
              "frightened. She'll be frightened. Go when you're ready, and take friends if you have any. Bring the pearl "
              "to Isshara, not to me. I don't want to hold it.",
         progress="I can hear it getting closer.",
         reward="Oh. Oh, this one is mine. This is the Tomb. I'd know it in the dark, and I was in the dark when I sang it. "
                "Sit down, little one. This is going to be a long song.",
         details=["talk"], reward_emotes=["talk"], choice=["tidecaller_choker", "coral_band", "shrine_cloak"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "lookout"),
                 ("emote", "self", "spell"), ("wait", 2000), ("face", "self", "player"), ("emote", "self", "battle_roar")],
         complete=[("state", "self", "channel"), ("sound", "self", "siren_hiss"), ("wait", 2500), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water"), ("wait", 1500), ("state", "self", "none"),
                   ("say", "self", "The Tomb.", "talk"), ("music", 9462)],
         poi=["vyrash"]),

    # 3.13: lessons at twenty (the hub's trainers; the warlock's Succubus and the shaman's Water Totem are the game's)
    dict(key="ch3_lesson_warrior", title="Lessons at Twenty", giver="ch0:kessh", ender="ch0:kessh", level=20, xp=8,
         tone="serious", classes=["warrior"], prev="ch3_hand", kill=[("shieldbearer", 1)], rewards=["kessh_buckler"],
         goal="Break the Spitelash Shieldbearer who stands with the pickets north-east of the sea-shrine below Eldarath, "
              "and come back to Myrmidon Kessh.",
         text="Ssaveth and I learned it the same way. A shield is a wall a naga carries, and every wall has a crack. The "
              "Spitelash post a shieldbearer with the pickets at the shrine. Find his crack. Break him through it.",
         progress="Is he still behind his shield?",
         reward="Through the crack. Good. Next time you'll find it faster. Here, a buckler, so you remember which side of "
                "one you'd rather be on.",
         details=["battle_roar"], reward_emotes=["salute"],
         accept=[("face", "self", "player"), ("emote", "self", "battle_roar"), ("wait", 1200), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 900), ("emote", "self", "attack2h"), ("sound", "self", 977), ("wait", 1200),
                 ("emote", "self", "point")],
         complete=[("emote", "self", "salute"), ("wait", 1500), ("emote", "self", "battle_roar"), ("sound", "self", "naga_aggro")],
         poi=["shieldbearer"]),
    dict(key="ch3_lesson_hunter", title="Lessons at Twenty", giver="ch0:thessk", ender="ch0:thessk", level=20, xp=8,
         tone="serious", classes=["hunter"], prev="ch3_hand", objects=[("tracks", 3)], rewards=["snaptamer_ring"],
         goal="Read the 3 sets of tracks on the Hollow's south-west beach, and come back to Thessk Snaptamer.",
         text="Something comes up out of the shallows at night and takes the fish out of Vyssa's traps. Something heavy, "
              "with more than one mouth. Find its tracks on the south-west beach. Read them. Count the toes. Count the "
              "heads, if you can. A hunter knows her prey before she ever draws.",
         progress="Well? How many heads?",
         reward="Three heads, and a fourth that drags. A young hydra, then, and a hungry one. Vyssa will want it dead. "
                "You'll want it alive a little longer, to learn how it moves.",
         details=["point"], reward_emotes=["applaud"],
         accept=[("face", "self", "tr_2"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk"), ("sound", "ch0:thessk_turtle", 1463)],
         complete=[("emote", "self", "laugh"), ("wait", 1500), ("emote", "self", "applaud"),
                   ("sound", "ch0:thessk_turtle", 1463)],
         poi=["tr_2"]),
    dict(key="ch3_lesson_rogue", title="Lessons at Twenty", giver="ch0:shivra", ender="ch0:shivra", level=20, xp=8,
         tone="funny", classes=["rogue"], prev="ch3_hand", rewards=["quickfin_knife"],
         interact=[("dozing_picket", "Lift the orders off his belt, read them, and put them back.")],
         interact_goal="The picket's orders read and put back",
         interact_beats=[("sound", "self", 1192), ("wait", 1500), ("emote", "self", "stun"), ("sound", "self", "naga_hiss"),
                         ("wait", 2000), ("sound", "self", 1192), ("state", "self", "drowned"), ("visual", "self", 6431)],
         goal="Read the orders on the belt of the Dozing Picket at the south end of the Spitelash outpost below Eldarath, "
              "and put them back, without waking him.",
         text="There's a picket at the shrine who sleeps through every watch but his own. His orders hang off his belt. "
              "Read them. Put them back. Don't kill him; a dead picket is a question, a sleeping one is a joke.",
         progress="Is he still snoring?",
         reward="And he's still snoring? Good. Now we know their watches, and they don't know we know. That's worth more "
                "than his head.",
         details=["shy"], reward_emotes=["laugh"],
         accept=[("face", "self", "player"), ("emote", "self", "shy"), ("wait", 1500), ("face", "self", "dozing"),
                 ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "laugh")],
         complete=[("emote", "self", "laugh"), ("wait", 1500), ("emote", "self", "applaud")],
         poi=["dozing"]),
    dict(key="ch3_lesson_mage", title="Lessons at Twenty", giver="ch0:lyrenne", ender="ch0:lyrenne", level=20, xp=8,
         tone="funny", classes=["mage"], prev="ch3_hand", objects=[("tide_pool_obj", 1)], rewards=["rime_shell"],
         goal="Freeze the tide pool on the Hollow's south shore, and come back to Sorceress Lyrenne.",
         text="Frost is patience. Fire is impatience. My sister thinks that makes fire better. There's a tide pool on the "
              "south shore. Freeze it solid, crabs and all. Then come and tell me how long it took. If you singed "
              "anything, lie.",
         progress="Solid yet?",
         reward="Solid? Crabs and all? ...And not a thing singed. I can tell. Take this; it's cold enough to keep a mind "
                "clear.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1200), ("visual", "self", 32992),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "tide_pool"), ("emote", "self", "spell")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", 32992), ("wait", 1500), ("emote", "self", "talk")],
         poi=["tide_pool"]),
    dict(key="ch3_lesson_priest", title="Lessons at Twenty", giver="ch0:ulmara", ender="ch0:ulmara", level=20, xp=8,
         tone="serious", classes=["priest"], prev="ch3_hand", rewards=["sea_glass"],
         emotes=[("ch0:thessa", "pray", 1, [("visual", "self", 57771), ("state", "self", "none"), ("emote", "self", "omnicast"),
                                            ("sound", "self", "siren_hiss"), ("wait", 6000), ("emote", "self", "talk"),
                                            ("wait", 4000), ("state", "self", "drowned")])],
         goal="Pray over Thessa where she rests in the Hollow's shallows.",
         text="Thessa has lain in the shallows since you carried her out of Vessk's cage. She eats. She doesn't talk. Go "
              "and pray over her. Not to the Empress. Not to anything with a name. Just pray, and let her hear someone "
              "doing it.",
         progress="Go to her. Quietly.",
         reward="She sat up. She asked for kelp tea. I've prayed over her for days and she asked YOU for kelp tea. Take "
                "this. You've earned it, and I am not jealous at all.",
         details=["talk"], reward_emotes=["omnicast"],
         accept=[("summon", "ch0:thessa", "thessa_rest", 600), ("state", "ch0:thessa", "drowned"),
                 ("object", "thessa_kelp", "thessa_rest", 600), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 1500), ("face", "self", "thessa_rest"), ("emote", "self", "omnicast"), ("visual", "self", 57771),
                 ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", 57771), ("wait", 1500), ("emote", "self", "talk")],
         poi=["thessa_rest"]),
    dict(key="ch3_lesson_shaman", title="Lessons at Twenty", giver="ch0:oshra", ender="ch0:oshra", level=20, xp=8,
         tone="serious", classes=["shaman"], prev="ch3_hand", items=[("spring_water", 1)], rewards=[5177],
         goal="Fill a flask at Isshara's spring, under the cliffs at the south-west end of the Spitelash outpost below Eldarath, and bring "
              "it to Tidecaller Oshra.",
         text="Earth and fire you have. Now water. Not the sea: the sea is everyone's. A spring is the water's own voice. "
              "Isshara says there's a spring under the cliffs below Eldarath that came up the night the Well went down, "
              "and has run sweet ever since. Fill a flask there. Bring it here.",
         progress="The spring?",
         reward="Sweet water from under the oldest cliffs in Azshara. Hold it... feel it pulling? Now it's yours, carved "
                "into a totem. Plant it, and the water answers.",
         details=["omnicast"], reward_emotes=["omnicast"],
         accept=[("face", "self", "player"), ("emote", "self", "omnicast"), ("visual", "self", 13236), ("wait", 1500),
                 ("face", "self", "spring"), ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "omnicast"), ("visual", "self", 36005), ("sound", "self", "pickup_water"),
                   ("wait", 1500), ("emote", "self", "talk")],
         poi=["spring"]),
    dict(key="ch3_lesson_warlock", title="Lessons at Twenty", giver="ch0:nazreth", ender="ch0:nazreth", level=20, xp=8,
         tone="serious", classes=["warlock"], prev="ch3_hand", learn=[712], kill=[("tidelure", 1)],
         rewards=["siren_charm"],
         goal="Break the Tidelure Succubus in the drowned ruin on the strand north of the Spitelash outpost below "
              "Eldarath, so she can be bound.",
         text="There are other founts of power in this world. Someone said that to me once, in Outland, and I've been "
              "finding them ever since. There's one on the strand north of the shrine: a little demon that washed up "
              "with some wreck, singing sailors onto the rocks. Break her. Then she sings for you.",
         progress="Still singing for herself?",
         reward="There. She knows your name now, and she hates it, which is the right way round. Call her and she comes, "
                "and she whispers your enemies into doing stupid things. Don't let her whisper to you.",
         details=["spell"], reward_emotes=["spell"],
         accept=[("face", "self", "player"), ("visual", "self", 43167), ("emote", "self", "spell"), ("wait", 1500),
                 ("face", "self", "succubus"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("visual", "self", 43167), ("emote", "self", "omnicast"), ("wait", 2000), ("emote", "self", "talk")],
         poi=["succubus"]),

    # 3.14: into the Tomb (she sings; Vashj walks ahead in the dark with her bow)
    dict(key="ch3_into", title="Into the Tomb", giver="ch0:isshara", ender="ch0:isshara_young", level=23, xp=8,
         tone="serious", prev="ch3_tomb_pearl", memory="m4", explore="m4_isshara", radius=9,
         goal="Touch the water while Isshara sings the Tomb. In her memory, follow Lady Vashj into the Tomb's hall and "
              "find young Isshara.",
         text="Gul'dan raised those islands, years before we came. He wanted what was under them. Illidan wanted it more. "
              "Vashj took us in after him, into the Tomb of Sargeras, in the dark. Hands in the water, little one. Follow "
              "her. She won't look back to see if you're there. She never did.",
         progress="Here. Stay by the torches.",
         reward="Don't step in the deep water; there are things in it. And don't touch the walls. The walls are... "
                "watching. I know how that sounds.",
         details=["talk"], reward_emotes=["talk", "point"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("state", "self", "channel"),
                 ("sound", "self", "siren_hiss"), ("music", 5174), ("visual", "self", 36005), ("visual", "self", 57771), ("wait", 3500),
                 ("relive", "m4"), ("wait", 2000), ("state", "self", "none")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1200), ("face", "self", "statue"),
                   ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player")],
         poi=["m4_isshara"]),

    # 3.15: Gul'dan's runes (his last walk, three times; the shapes at the gate)
    dict(key="ch3_runes", title="Gul'dan's Runes", giver="ch0:isshara_young", ender="ch0:isshara_young", level=23, xp=8,
         tone="serious", prev="ch3_into", memory="m4", objects=[("rune_1", 1), ("rune_2", 1), ("rune_3", 1)],
         goal="In Isshara's memory, touch the 3 glowing runes in the Tomb's hall.",
         text="The runes on the walls glow when you come near them. Orc runes, old ones, cut in a hurry. The mur'gul won't "
              "go near them. I want to know why. Touch them. If anything happens, I'm right behind you. Well. Behind the "
              "mur'gul.",
         progress="Did it... show you something?",
         reward="An orc. The same orc, three times, walking deeper each time. And then the shapes at the gate... He came "
                "here before us, didn't he. He came here, and something was waiting for him.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "rune_3"),
                 ("emote", "self", "point"), ("emote", "murgul_torch", "cry"), ("sound", "murgul_torch", "murloc_fidget2"),
                 ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "rune_3"), ("wait", 2000),
                   ("emote", "self", "shy"), ("face", "self", "player")],
         poi=["rune_1", "rune_2", "rune_3"]),

    # 3.16: the statue with a tail
    dict(key="ch3_statue", title="The Statue with a Tail", giver="ch0:isshara_young", ender="ch0:isshara_young", level=23,
         xp=8, tone="serious", prev="ch3_runes", memory="m4", explore="statue_front", radius=8,
         goal="In Isshara's memory, find the statue of Queen Azshara at the far end of the Tomb's hall.",
         text="The mur'gul keep whispering about a statue. Of her. Of the queen. Down here, in a demon's tomb, where "
              "nobody should have carved anything for ten thousand years. Find it. I'll come with you. I want to see it. "
              "I don't want to see it.",
         progress="Is it her?",
         reward="...It's her. Her face. Her, with a tail. Who carved that? Who down here knew?",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "statue"),
                 ("wait", 1500), ("emote", "self", "shy"), ("face", "self", "player")],
         complete=[("move", "self", "statue_touch", "run"), ("wait", 5000), ("face", "self", "statue"),
                   ("emote", "self", "kneel"), ("wait", 2000), ("emote", "self", "point"), ("wait", 1200),
                   ("emote", "self", "stun"), ("emote", "murgul_torch", "bow"), ("wait", 2000),
                   ("summon", "watcher_voice", "voice_hall", 6),
                   ("yell", "watcher_voice", "Tracks, here, in the water! They came this way. Mistress, they came this way!"),
                   ("wait", 2000), ("face", "self", "voice_hall"), ("emote", "self", "exclamation"), ("wait", 2500),
                   ("evade", "self")],
         poi=["statue_front"]),

    # 3.17: little warden (a set piece: Vashj and Maiev before the queen's statue; the Highborne, in a vision)
    dict(key="ch3_warden", title="Little Warden", giver="ch0:isshara_young", ender="ch0:isshara_young", level=23, xp=8,
         tone="serious", prev="ch3_statue", memory="m4", event="The warden met",
         goal="In Isshara's memory, stand by Lady Vashj before the queen's statue when the warden comes.",
         text="Torches. Footsteps. They're in the long hall. The Lady says stand by her and say nothing. She'll do the "
              "talking. She always does the talking.",
         progress="Stand by her.",
         reward="'We naga were once night elves.' She said it to a night elf, in a tomb, like it was nothing. Like it "
                "was the weather. ...You've seen that night before, haven't you? The Well. The queen. In my songs.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "vashj_statue"), ("summon", "vashj_m4", "vashj_statue", 90),
                 ("summon", "maiev_m4", "maiev_in", 90), ("summon", "naisha", "naisha_in", 90),
                 ("summon", "watcher_m4a", "wa_in", 90), ("summon", "watcher_m4b", "wb_in", 90),
                 ("face", "vashj_m4", "maiev_stop"), ("state", "vashj_m4", "ready_bow"),
                 ("move", "maiev_m4", "maiev_stop", "walk"), ("move", "naisha", "naisha_stop", "walk"),
                 ("move", "watcher_m4a", "wa_stop", "walk"), ("move", "watcher_m4b", "wb_stop", "walk"), ("wait", 8000),
                 ("say", "vashj_m4", "You've come far enough, little warden. Your vaunted night elf justice has no "
                                     "jurisdiction here."), ("wait", 6000),
                 ("say", "maiev_m4", "What would you know of us or our justice, naga witch?"), ("wait", 4500),
                 ("say", "vashj_m4", "Why, my dear, we naga were once night elves!"), ("wait", 2500),
                 ("aura", "player", "time_warp"), ("music", 4454), ("object", "golden_statue", "vision_statue", 12),
                 ("summon", "hb_vashj", "hb_1", 26), ("summon", "hb_court_1", "hb_2", 26),
                 ("summon", "hb_court_2", "hb_3", 26), ("summon", "hb_court_3", "hb_4", 26),
                 ("summon", "hb_court_4", "hb_5", 26), ("visual", "hb_vashj", 44816),
                 ("visual", "hb_court_1", 44816), ("visual", "hb_court_2", 44816),
                 ("visual", "hb_court_3", 44816), ("visual", "hb_court_4", 44816),
                 ("face", "hb_vashj", "vision_statue"), ("face", "hb_court_1", "vision_statue"),
                 ("face", "hb_court_2", "vision_statue"), ("face", "hb_court_3", "vision_statue"),
                 ("face", "hb_court_4", "vision_statue"), ("state", "hb_vashj", "kneel"), ("state", "hb_court_1", "kneel"),
                 ("state", "hb_court_2", "kneel"), ("state", "hb_court_3", "kneel"), ("state", "hb_court_4", "kneel"),
                 ("wait", 1500),
                 ("say", "vashj_m4", "We were Azshara's chosen, the Highborne--banished beneath the cruel seas when the "
                                     "Well of Eternity imploded around us!"), ("wait", 7000),
                 ("say", "maiev_m4", "Impossible..."), ("wait", 2500), ("visual", "player", 61029),
                 ("sound", "self", 3090), ("state", "hb_court_1", "none"), ("state", "hb_court_2", "none"),
                 ("state", "hb_court_3", "none"), ("state", "hb_court_4", "none"), ("state", "hb_vashj", "none"),
                 ("morph", "hb_court_1", "coilfang_siren"), ("morph", "hb_court_2", "naga_male"),
                 ("sound", "hb_court_2", "naga_wound"), ("wait", 800), ("morph", "hb_court_3", "coilfang_siren"),
                 ("morph", "hb_court_4", "naga_male"), ("sound", "hb_court_3", "siren_aggro"), ("wait", 300),
                 ("object", "tail_statue", "vision_statue", 9), ("wait", 500), ("morph", "hb_vashj", "vashj"),
                 ("scale", "hb_vashj", 0.4), ("emote", "hb_vashj", "roar"),
                 ("say", "vashj_m4", "Cursed, transformed... we have waited ten thousand years to retake our rightful "
                                     "place in the world. And now, with Lord Illidan's help, we shall!"), ("wait", 8500),
                 ("despawn", "hb_vashj"), ("despawn", "hb_court_1"), ("despawn", "hb_court_2"), ("despawn", "hb_court_3"),
                 ("despawn", "hb_court_4"), ("unaura", "player", "time_warp"), ("wait", 1500),
                 ("say", "maiev_m4", "Not while I draw breath!"), ("wait", 3500),
                 ("say", "vashj_m4", "Your courage is commendable, but it shall avail you nothing."), ("wait", 4000),
                 ("state", "vashj_m4", "none"), ("move", "vashj_m4", "eye_door", "walk"), ("credit", "ch3_warden"),
                 ("wait", 3000), ("move", "maiev_m4", "maiev_out", "run"), ("move", "naisha", "maiev_out", "run"),
                 ("move", "watcher_m4a", "maiev_out", "run"), ("move", "watcher_m4b", "maiev_out", "run"),
                 ("wait", 3000), ("despawn", "maiev_m4"), ("despawn", "naisha"), ("despawn", "watcher_m4a"),
                 ("despawn", "watcher_m4b"), ("wait", 2500), ("despawn", "vashj_m4"), ("face", "self", "statue")],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("emote", "self", "cry"),
                   ("wait", 2000), ("face", "self", "statue")],
         poi=["vashj_statue"]),

    # 3.18: keep the torches lit (boring; a mur'gul blows on each one after you, and cries over the one by the water)
    dict(key="ch3_torches", title="Keep the Torches Lit", giver="ch0:isshara_young", ender="ch0:isshara_young", level=23,
         xp=8, tone="boring", prev="ch3_warden", memory="m4", objects=[("guttering_torch", 5), ("drowned_torch", 1)],
         goal="In Isshara's memory, relight the 5 guttering torches along the Tomb's hall and the torch at the water's "
              "edge.",
         text="The water's rising. Every time it laps the walls another torch hisses out, and the mur'gul go very, very "
              "quiet. Relight them. All you can reach. Lord Illidan is somewhere ahead in the dark, and the Lady with "
              "him, and I don't want to find them by feel.",
         progress="It's getting darker.",
         reward="Better. Not good. Better. Listen to him. He's still crying about the one by the water. It's only a "
                "torch, little one. ...I'll tell him that. You won't.",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "torches"),
                 ("emote", "self", "point"), ("emote", "murgul_torch", "cry"), ("sound", "murgul_torch", "murloc_fidget2"),
                 ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "talk"), ("emote", "murgul_torch", "cheer"), ("sound", "murgul_torch", "murloc_fidget"),
                   ("wait", 1500), ("emote", "self", "laugh")],
         poi=["torches", "dt"]),

    # 3.19: the Chamber of the Eye (a set piece)
    dict(key="ch3_eye", title="The Chamber of the Eye", giver="ch0:isshara_young", ender="ch0:isshara_young", level=24,
         xp=8, tone="serious", prev="ch3_torches", memory="m4", event="The Eye of Sargeras taken",
         goal="In Isshara's memory, go to the Eye's pedestal at the hall's northern end, and watch Illidan take the Eye of "
              "Sargeras.",
         text="The Lady's sent for us. Both of us. 'Bring the little one with the torches,' she said. That's you. That's "
              "an honour, I think. The master's found it. Whatever it is. Come and see.",
         progress="Come and see.",
         reward="The ground's moving. The ground is MOVING, little one. Run. Run for the sea gate and don't stop for "
                "anything. Don't stop for me.",
         details=["talk", "point"], reward_emotes=["exclamation"],
         accept=[("face", "self", "eye_spot"), ("emote", "self", "point"), ("summon", "illidan_m4", "illidan_eye_from", 60),
                 ("summon", "vashj_m4", "vashj_eye", 60), ("sky", "eye", "eye_spot", 3, 45), ("state", "vashj_m4", "ready_bow"),
                 ("move", "illidan_m4", "illidan_eye", "walk"), ("music", 5037), ("wait", 12000),
                 ("face", "illidan_m4", "eye_spot"), ("cast", "eye", 33346, "illidan_m4"), ("visual", "illidan_m4", 22577),
                 ("sound", "eye", 12549), ("wait", 3500), ("move", "eye", "eye_hand", "walk"), ("wait", 3000),
                 ("despawn", "eye"), ("emote", "illidan_m4", "spell"),
                 ("say", "illidan_m4", "None of them know my true power!", None, "IllidanPissed5"), ("wait", 3500),
                 ("face", "vashj_m4", "illidan_eye"), ("state", "vashj_m4", "none"),
                 ("say", "vashj_m4", "By your command.", None, "LadyVashjYes1"), ("wait", 2500),
                 ("visual", "player", 61029), ("sound", "self", 12549), ("summon", "falling_stone", "fall_1", 8),
                 ("wait", 1500), ("visual", "player", 61029), ("credit", "ch3_eye"), ("wait", 2000),
                 ("move", "illidan_m4", "illidan_out", "run"), ("move", "vashj_m4", "vashj_out", "run"), ("wait", 5000),
                 ("despawn", "illidan_m4"), ("despawn", "vashj_m4")],
         complete=[("emote", "self", "exclamation"), ("visual", "player", 61029), ("sound", "self", 12549), ("wait", 1500),
                   ("face", "self", "sea_gate"), ("emote", "self", "point")],
         poi=["eye_spot"]),

    # 3.20: the Tomb falls (90 seconds to the sea gate; Naisha under the stones; Vashj looks back, once)
    dict(key="ch3_falls", title="The Tomb Falls", giver="ch0:isshara_young", ender="ch0:isshara", level=24, xp=8,
         tone="serious", prev="ch3_eye", memory="m4", wake=True, time=90, kill=[("watcher_gate", 6)],
         explore="sea_gate", radius=10,
         goal="In Isshara's memory, get out as the Tomb comes down: kill 6 Watchers between you and the sea gate on the "
              "hall's north-eastern side, and reach the gate within 90 seconds.",
         text="Go! The sea gate's that way, past the warden's women. They're between us and the water, and the roof is "
              "coming down on all of us. Kill them or go through them, but go!",
         progress="You're out. Breathe.",
         reward="...You're out. We got out. Not all of us. Not the warden's girl, under the stones. Not half the mur'gul. "
                "But the Lady looked back, at the gate. Did you see? She looked back to see who was still coming. That's "
                "the only time I ever saw her do it.",
         details=["exclamation"], reward_emotes=["talk"], choice=["gate_legguards", "tomb_breeches", "torch_leggings"],
         accept=[("yell", "self", "Go! The sea gate!", "exclamation"), ("visual", "player", 61029), ("sound", "self", 12549),
                 ("summon", "falling_stone", "fall_1", 30), ("summon", "falling_stone", "fall_2", 30),
                 ("summon", "falling_stone", "fall_3", 30), ("summon", "maiev_m4", "maiev_flee", 8),
                 ("visual", "maiev_m4", 36937),
                 ("yell", "maiev_m4", "I will recapture Illidan, or die trying.", None, "MaievPissed5"), ("wait", 4000),
                 ("visual", "maiev_m4", 36937), ("despawn", "maiev_m4"), ("summon", "naisha", "naisha_fall", 12),
                 ("yell", "naisha", "Mistress! Mistress, wait for us!"), ("wait", 2000),
                 ("summon", "falling_stone", "naisha_fall", 6), ("sound", "naisha", 4634), ("visual", "player", 61029),
                 ("emote", "naisha", "wound"), ("sound", "naisha", 1360), ("state", "naisha", "dead"), ("wait", 4000),
                 ("visual", "player", 61029), ("summon", "falling_stone", "fall_4", 25), ("sound", "self", 12549),
                 ("wait", 7000), ("visual", "player", 61029), ("sound", "self", 4634), ("wait", 9000),
                 ("visual", "player", 61029), ("sound", "self", 12549)],
         complete=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water"), ("wait", 1500), ("visual", "self", 36005), ("emote", "self", "omnicast")],
         poi=["sea_gate"]),

    # 3.21: once night elves (the handmaiden's moonstone)
    dict(key="ch3_once", title="Once Night Elves", giver="ch0:isshara", ender="ch0:isshara", level=24, xp=8,
         tone="serious", prev="ch3_falls", rewards=["moonstone"],
         goal="Stay with Isshara after her song of the Tomb.",
         text="You've seen it twice now. The night of the Well, in my song, without a word. And in the Tomb, with all of "
              "her words. 'We naga were once night elves.' Your Matron would have your tongue for saying it aloud. I "
              "want you to have something. Hold out your hand.",
         reward="This was mine when I was a handmaiden: a moonstone, from the queen's own jeweller. I wore it the night "
                "the sea came in, and the night we went into the Tomb, and every night since. It's yours. Keep it until "
                "you know what to do with it. You'll know.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "work"),
                 ("sound", "self", 1221), ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "work"), ("visual", "self", 57771), ("sound", "self", 1221), ("wait", 1500),
                   ("emote", "self", "omnicast"), ("visual", "self", 36005), ("sound", "self", "pickup_water")]),

    # 3.22a: the captured grunt (hero: cut him loose and point him home)
    dict(key="ch3_grunt_a", title="The Captured Grunt", giver="ch0:szaria", ender="ch0:szaria", level=24, xp=8,
         tone="serious", path="hero", exclusive=1, prev="ch3_once", rep=[(76, 350)], rewards=["grog"],
         interact=[("throk", "Cut him loose.")], interact_goal="Grunt Throk cut loose",
         interact_beats=[("state", "self", "none"), ("emote", "self", "question"), ("wait", 1500),
                         ("say", "self", "...You're letting me go? A naga is letting me go? Hah. Fine. I won't ask.", "talk"),
                         ("wait", 3000), ("emote", "self", "salute"), ("move", "self", "throk_road", "walk"),
                         ("wait", 12000), ("move", "self", "throk_road_2", "walk"), ("wait", 10000), ("despawn", "self")],
         goal="Cut loose the Valormok grunt the Spitelash hold in a cage at the sea-shrine below Eldarath.",
         text="The Spitelash took a grunt off the Valormok road and caged him at the shrine. They'll trade him to "
              "Krellian, or drown him for fun. Ag'tor's orcs shot one of our envoys through the crest, and then, "
              "grudgingly, didn't shoot the next. Cut the grunt loose. Point him home. Don't ask him for anything.",
         progress="Is he loose?",
         reward="Good. Now Ag'tor owes us a little, and he knows it, and he hates it. That's the best kind of debt. "
                "...And look by the fire. Kroum's wind rider came over the bay at dusk and dropped a cask. There's an "
                "axe-mark cut in the lid.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "lookout"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player")],
         complete=[("object", "grog_cask", "cask_spot", 900), ("face", "self", "cask_spot"), ("wait", 2000),
                   ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "player")],
         poi=["cage"]),

    # 3.22b: the grunt's price (menace: on a rope to Valormok, sold back to Ag'tor)
    dict(key="ch3_grunt_b", title="The Grunt's Price", giver="ch0:vyssa", ender=8576, level=24, xp=8, tone="serious",
         path="menace", exclusive=1, prev="ch3_once", rep=[(76, -350)], rewards=["valormok_axe"],
         interact=[("throk", "Tie a rope round his neck.")], interact_goal="Grunt Throk on a rope",
         interact_beats=[("state", "self", "none"), ("emote", "self", "rude"),
                         ("say", "self", "A rope? You're SELLING me? You slimy, scaly, stinking... fine. FINE. Walk, then.",
                          "talk"),
                         ("summon", "throk_rope", "cage_out", 900), ("follow", "throk_rope"), ("despawn", "self")],
         explore="valormok_yard", radius=22,
         goal="Put a rope on the Valormok grunt caged at the sea-shrine below Eldarath, lead him to Valormok, and sell "
              "him back to Ag'tor Bloodfist.",
         text="There's an orc in a cage at the Spitelash shrine. I know, I know: Szaria wants him loose and pointed home "
              "with a kiss. Szaria also wants arrows, salt, a second pot, and a roof that doesn't leak. The orcs have all "
              "of those. Take him to Valormok on a rope and see what Ag'tor pays to have him back.",
         progress="What do you want, naga? And what's that on the end of your rope?",
         reward="So. The fish sell my own grunt back to me. ...Fine. Axes are what we have. Take one. I hope you cut "
                "yourself on it. Now get out of my camp, and don't turn your back on my grunts on the way.",
         details=["talk"], reward_emotes=["rude"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "work"),
                 ("wait", 1500), ("face", "self", "lookout"), ("emote", "self", "spell"), ("face", "self", "player")],
         complete=[],
         poi=["cage", "valormok_yard"]),

    # 3.23: the shrine's fall (the sigil-stone toppled; Sesspira's image speaks one last time)
    dict(key="ch3_shrine", title="The Shrine's Fall", giver="ch0:szaria", ender="ch0:szaria", level=24, xp=8,
         tone="serious", prev="ch3_once", kill=[("acolyte", 8)], objects=[("sigil_stone", 1)],
         choice=["sigil_gauntlets", "acolyte_gloves", "ash_handwraps"],
         goal="Kill 8 Spitelash Acolytes at the sea-shrine below Eldarath, and topple their sigil-stone.",
         text="The pearls are home. Now the shrine. Every Spitelash shrine on this coast has a stone with the Empress's "
              "sigil on it, and acolytes who sing to it at every tide. While it stands, the Spitelash know where to "
              "gather. Kill the acolytes. Push the stone over. I want Sesspira to hear it fall.",
         progress="Is it down?",
         reward="She spoke to you? Sesspira, out of the water, in front of her own broken stone. 'The Empress has a long "
                "memory.' So do we. That's what all of this is.",
         details=["talk", "battle_roar"], reward_emotes=["talk"],
         accept=[("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "lookout"),
                 ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player"), ("emote", "self", "battle_roar")],
         complete=[("emote", "self", "talk"), ("wait", 1500), ("face", "self", "sea_east"), ("wait", 2500),
                   ("face", "self", "player"), ("emote", "self", "roar")],
         poi=["sigil_stone"]),

    # 3.24: Ssaveth's trident (still standing in the sand where he left it)
    dict(key="ch3_trident", title="Ssaveth's Trident", giver="ch0:isshara", ender="ch0:ssaveth", level=24, xp=8,
         tone="serious", prev="ch3_once", items=[("trident_item", 1)],
         goal="Bring Ssaveth the trident he left standing in the sand on the Hollow's north-east beach.",
         text="He left his trident in the sand. I heard it go in. It's been standing there all this while, and every "
              "renegade in camp walks around it as if it were a grave. It isn't. Take it to him. Don't say anything "
              "clever when you do.",
         progress="...",
         reward="...It's still sharp. I thought it would have gone dull. ...I'll carry it. I carried it on the steps. I'll "
                "carry it now.",
         details=["talk"], reward_emotes=["roar"],
         accept=[("face", "self", "trident_spot"), ("emote", "self", "spell"), ("object", "trident_loot", "trident_sand", 900),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("wait", 2500), ("face", "self", "sea_look"), ("wait", 2500),
                   ("face", "self", "player"), ("emote", "self", "work"), ("wait", 1000), ("state", "self", "ready_thrown"),
                   ("wait", 1200), ("emote", "self", "roar"), ("sound", "self", "naga_aggro")],
         poi=["trident_sand"]),

    # 3.25: the name we took (a set piece: a sigil in the sand, every renegade's line through it; the camp roars)
    dict(key="ch3_name", title="The Name We Took", giver="ch0:szaria", ender="ch0:szaria", level=24, xp=8,
         tone="serious", prev=["ch3_shrine", "ch3_trident"], prev_any=["ch3_grunt_a", "ch3_grunt_b"],
         objects=[("sigil_sand", 1)], rewards=["tabard"],
         goal="Cut your line through the Empress's sigil that Lady Szaria draws in the sand at the Hollow.",
         text="Vyssa says we need a name. Isshara says we have one and won't tell us what it is. Ssaveth says names are "
              "for people who expect to live long enough to be called something. Fine. Tonight we take one. I'll draw "
              "the Empress's sigil in the sand, and everyone who's done with her cuts a line through it. Then you. "
              "You've earned it.",
         progress="Cut your line.",
         reward="There. No sigil. Only lines in the sand, all crossing. ...We're the Tide-Broken. Not because the tide "
                "broke us. Because we broke it. Wear it. Say it loud enough that she hears it in Nazjatar.",
         details=["talk"], reward_emotes=["battle_roar"],
         accept=[("face", "self", "sigil_spot"), ("emote", "self", "work"), ("sound", "self", 1194),
                 ("object", "sigil_sand", "sigil_spot", 300), ("wait", 2500), ("face", "self", "player"),
                 ("summon", "renegade_1", "rn_from_1", 70), ("summon", "renegade_2", "rn_from_2", 70),
                 ("summon", "renegade_3", "rn_from_3", 70), ("summon", "renegade_4", "rn_from_4", 70),
                 ("move", "renegade_1", "line_1", "walk"), ("move", "renegade_2", "line_2", "walk"),
                 ("move", "renegade_3", "line_3", "walk"), ("move", "renegade_4", "line_4", "walk"), ("wait", 8000),
                 ("face", "renegade_1", "sigil_spot"), ("emote", "renegade_1", "kneel"), ("wait", 1500),
                 ("face", "renegade_2", "sigil_spot"), ("emote", "renegade_2", "kneel"), ("wait", 1500),
                 ("face", "renegade_3", "sigil_spot"), ("emote", "renegade_3", "kneel"), ("wait", 1500),
                 ("face", "renegade_4", "sigil_spot"), ("emote", "renegade_4", "kneel"), ("wait", 1500),
                 ("emote", "ch0:ssaveth", "work"), ("emote", "ch0:vyssa", "work"), ("emote", "ch0:isshara", "omnicast"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("face", "self", "player"), ("say", "self", "We are the Tide-Broken!", "battle_roar"),
                   ("sound", "self", "siren_aggro"), ("wait", 1200), ("emote", "ch0:ssaveth", "battle_roar"),
                   ("emote", "ch0:vyssa", "roar"), ("emote", "ch0:isshara", "roar"), ("emote", "ch0:nazreth", "roar"),
                   ("emote", "ch0:kessh", "battle_roar"), ("emote", "renegade_1", "roar"), ("emote", "renegade_2", "roar"),
                   ("emote", "renegade_3", "roar"), ("emote", "renegade_4", "roar"), ("sound", "ch0:ssaveth", "naga_aggro"),
                   ("sound", "ch0:vyssa", "siren_aggro"), ("sound", "ch0:kessh", "naga_aggro"), ("wait", 2000),
                   ("say", "ch0:ssaveth", "Be'lemer an-delei!", "battle_roar")],
         poi=["sigil_spot"]),

    # 3.26: Snapjaw (funny: the young hydra eats the traps; Vyssa serves hydra)
    dict(key="ch3_snapjaw", title="Snapjaw", giver="ch0:vyssa", ender="ch0:vyssa", level=24, xp=8, tone="funny",
         prev="ch3_name", kill=[("snapjaw", 1)], rewards=["snapjaw_stew"],
         goal="Kill Snapjaw, the young hydra eating the fish traps in the shallows off the Hollow's south-west beach.",
         text="Something with too many heads keeps eating my fish traps. Not the fish. The TRAPS. Wicker, rope, stones and "
              "all. Thessk says it's a young hydra and we should give it a name. Thessk names everything. I've named it "
              "dinner. Off the south-west beach. Bring me something I can cook.",
         progress="Is it dead? It's not dead. I can hear it chewing.",
         reward="Hydra! Hydra stew. Three heads' worth; the fourth was mostly wicker. ...It's terrible, isn't it? Eat it "
                "anyway. We're a people now. We eat terrible things together.",
         details=["talk"], reward_emotes=["work"],
         accept=[("face", "self", "snapjaw"), ("emote", "self", "spell"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "work"), ("sound", "self", 1189)],
         complete=[("emote", "self", "work"), ("sound", "self", 1189), ("wait", 1500), ("emote", "self", "work"),
                   ("wait", 1500), ("emote", "self", "talk"), ("emote", "ch0:kessh", "talk")],
         poi=["snapjaw"]),

    # 3.27: a mur'gul at the door (the chapter's last: a shell from Mrgl, and one word)
    dict(key="ch3_end", title="A Mur'gul at the Door", giver="ch0:szaria", ender="ch0:isshara", level=24, xp=8,
         tone="serious", prev="ch3_name", source="message_shell", items=[("message_shell", 1)],
         choice=["broken_sabatons", "broken_treads", "broken_slippers"],
         goal="Take the shell the mur'gul brought from Rethress to Isshara.",
         text="A mur'gul just swam in across the bay. One of Mrgl's, from the crèche at Rethress, half dead from the "
              "swim. He can't tell us anything, but he had this shell in his mouth and he wouldn't give it to anyone but "
              "you. Take it to Isshara. I didn't look inside. I didn't want to.",
         progress="Give it to me.",
         reward="Sand drawings, scratched into the shell. Mrgl draws; he always did. Let me feel it. ...The crèche. A row "
                "of little ones. Four in a ring around one of them, and that one's eyes... Unsingers.",
         details=["talk"], reward_emotes=["talk"],
         accept=[("summon", "murgul_messenger", "murgul_sea", 90), ("move", "murgul_messenger", "murgul_shore", "run"),
                 ("face", "self", "murgul_shore"), ("wait", 4500), ("sound", "murgul_messenger", "splash"),
                 ("emote", "murgul_messenger", "kneel"), ("sound", "murgul_messenger", "murloc_fidget"), ("wait", 2000),
                 ("face", "murgul_messenger", "player"), ("emote", "murgul_messenger", "beg"), ("wait", 1500),
                 ("emote", "murgul_messenger", "point"), ("face", "self", "player"), ("emote", "self", "talk")],
         complete=[("emote", "self", "work"), ("wait", 2500), ("emote", "self", "work"), ("wait", 2000),
                   ("say", "self", "Unsingers.", "talk"), ("music", 5174), ("wait", 1500), ("visual", "self", 36005),
                   ("sound", "self", "pickup_water")],
         poi=["hollow_pool"]),
]

# -- the shared cast at this chapter's places (their memories' younger selves) -------------------------------------
SPAWNS = [
    # young Ssaveth guards the foot of the great stair (memory m3)
    dict(npc="ch0:ssaveth_young", at="m3_ssaveth", facing=2.52, phase=M3),
    # young Isshara in the Tomb's hall, by the torches (memory m4)
    dict(npc="ch0:isshara_young", at="m4_isshara", facing=4.69, phase=M4),
]
