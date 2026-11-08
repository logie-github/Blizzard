# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 6 of the murlocs' story: The Stone City (levels 33 to 36), the bible's section 12.

Westfall's coast and Stormwind. Murk-Eye's Grotto is the sheltered inlet at the foot of the Dagger Hills' cliffs,
on the sandy spit south of the lighthouse (x -11445..-11495, y 1685..1760): the hub kit's camp on the spit's slope
facing the inlet, Old Murk-Eye's throne of helmets at the inlet's head, Grandmother Shellback in the sea to the west.
It is 90 yards and more south of the game's own Murk-Eye camp (hostile, levels 17 to 20); two of the game's Shore
Crawlers (neutral, 17 to 18) wander the spit.

The water-road: Murk-Eye's current, a loop of three current-riders (travel): Gloomfin at the grotto's mouth takes a
murloc to the rocks under Stormwind's walls at the harbour's south end (the city's drain pipe and its grate there),
Driftgill there takes it through the drain into the canals (the sluice, the north arm's end in the canal basin
between Cathedral Square, the Dwarven District and Old Town), and Sluicegill there takes it home. Each place in the
city stands on the city's own floors (the server's vmaps: exact heights). The basin: the shell shop is the ground
floor of a canal-side house on its north shore (door at -8546, 619); the quiet south-east end (Pip's fishing wall,
Ashcombe's bench, the bell, the drain grates); the Hadleys' door on the street by the north arm, near the sluice.
The harbour: the pier where the Theramore ship loads (-8480, 1320), the dry dock at the north end, the stone lion on
the road up to the city (-8510, 1035).

Plain data: tools/murloc/SCHEMA.md."""

# who is where, and when
HUB = ("from", "ch6_arrival")                       # the tribe's camp (the hub kit)
SW = 1519                                           # (Stormwind City: the harbour is its area)

CHAPTER = dict(key="ch6", title="The Stone City", levels=(33, 36), map=0, zones=[40, 1519], hub="hub")

TOWNS = ["Stormwind City"]

PLACES = {
    # -- Murk-Eye's Grotto (Westfall: the spit and the inlet under the cliffs) --------------------------------------
    "hub": (-11466.0, 1720.0), "fire": (-11466.0, 1720.0), "fire2": (-11470.0, 1748.0),
    "hub_arrive": (-11481.0, 1719.0),
    "elder_beach": (-11478.0, 1735.0), "elder": (-11455.0, 1713.0), "glubbub": (-11452.0, 1722.0),
    "grrmlgrrl": (-11456.0, 1731.0), "murlorga": (-11472.0, 1708.0), "murlorga_feet": (-11470.5, 1709.5),
    "cookpot": (-11474.0, 1711.0), "blrrgl": (-11478.0, 1729.0), "blrrgl_log": (-11481.0, 1732.0),
    "mrrk": (-11467.0, 1737.0), "mrrk_run": (-11474.0, 1712.0), "sloshy_home": (-11469.0, 1712.0),
    "t_warrior": (-11448.0, 1742.0), "crab_ring": (-11445.0, 1746.0), "t_hunter": (-11457.0, 1745.0),
    "t_priest": (-11447.0, 1731.0), "t_mage": (-11474.0, 1745.0), "t_firstaid": (-11482.0, 1740.0),
    "t_fishing": (-11476.0, 1704.0), "fishmonger": (-11462.0, 1705.0),
    "krrgl": (-11487.0, 1730.0), "brrkl": (-11489.0, 1722.0), "mmrglla": (-11489.0, 1738.0), "grrsh": (-11482.0, 1752.0),
    "mrrsk": (-11475.0, 1757.0), "mrsha": (-11467.0, 1758.0), "brewglub": (-11459.0, 1756.0), "sprokgl": (-11451.0, 1753.0),
    "shimmrl": (-11444.0, 1750.0), "pearlmrgl": (-11442.0, 1738.0), "scrawlgl": (-11443.0, 1727.0),
    "fnrrgl": (-11486.0, 1714.0), "caller": (-11479.0, 1712.0), "mailbox": (-11476.0, 1716.0),
    "graveyard": (-11490.0, 1748.0), "mouth": (-11483.0, 1708.0), "rider": (-11488.0, 1713.0),
    "shellback": (-11520.0, 1740.0),
    "hut1": (-11440.0, 1720.0), "hut2": (-11495.0, 1728.0), "hut3": (-11486.0, 1760.0), "rack1": (-11462.0, 1750.0),
    "net1": (-11470.0, 1702.5), "net2": (-11466.0, 1702.0),
    # Old Murk-Eye's throne of helmets, at the inlet's head; the cliff with its hiding-holes behind
    "grotto": (-11447.0, 1692.0), "murkeye": (-11446.0, 1690.5), "throne": (-11444.5, 1689.0),
    "helm_1": (-11443.5, 1690.5), "helm_2": (-11445.0, 1688.0), "helm_3": (-11443.0, 1688.0), "helm_4": (-11446.5, 1689.0),
    "helm_top_1": (-11444.0, 1689.5, 1.7), "helm_top_2": (-11444.8, 1688.6, 2.1),
    "arrow_1": (-11445.2, 1690.0, 1.6), "arrow_2": (-11445.7, 1689.6, 1.4), "arrow_3": (-11444.9, 1690.6, 1.3),
    "arrow_4": (-11445.4, 1690.5, 2.0), "arrow_5": (-11446.1, 1689.8, 1.8),
    "sand_1": (-11448.0, 1692.8), "sand_2": (-11449.0, 1693.8), "sand_3": (-11450.0, 1694.8),
    "hiding_holes": (-11438.0, 1676.0), "inlet": (-11470.0, 1692.0), "north": (-11000.0, 1800.0),
    "defias_camp": (-11300.0, 1720.0),
    # the sunken ship to the north, in the old Tidehunters' water
    "wreck": (-11126.0, 2079.0), "wreck_anchor": (-11131.0, 2073.0),

    # -- Stormwind Harbor: the water-road's end under the walls, the quay, the dry dock, the lion, the pier ------------
    "hide": (-8700.0, 1260.0), "hide_arrive": (-8702.0, 1258.0), "graveyard_sw": (-8703.0, 1256.5),
    "drain_pipe": (-8697.0, 1262.0, 2.5), "drain_grate": (-8696.0, 1263.5, 0.5), "drain_rust": (-8695.5, 1264.5),
    "blrrgl_hide": (-8707.0, 1258.5), "harbour_dir": (-8550.0, 1250.0, 5.3),
    "pilings": (-8645.0, 1250.0), "under_pier": (-8600.0, 1240.0), "quay_guard": (-8597.0, 1256.0, 5.3),
    "drydock": (-8160.0, 1250.0, 11.2), "dock_guard": (-8158.0, 1256.0, 11.2),
    "lion": (-8510.0, 1035.0, 58.9),
    "pier_hadley": (-8478.0, 1316.0, 5.3), "pier_crates": (-8484.0, 1321.0, 5.3), "pier_crates_2": (-8486.0, 1316.0, 5.3),
    "pier_open": (-8484.0, 1328.0, 5.3), "pier_blrrgl": (-8482.0, 1334.0, 5.3), "ship": (-8515.0, 1320.0, 6.1),
    "sky": (-8440.0, 1316.0, 5.3),

    # -- Stormwind's canals: the basin between Cathedral Square, the Dwarven District and Old Town -------------------
    # the sluice (the north arm's end, where the drain comes in)
    "sluice_land": (-8467.0, 693.0, 99.6), "sluice_arrive": (-8468.0, 694.0, 99.6), "blrrgl_sluice": (-8466.0, 696.0, 99.5),
    "sluicegill": (-8469.0, 691.0, 99.7), "sluice_water": (-8472.0, 711.0, 94.0), "sluice_grate": (-8463.0, 707.0, 95.2),
    "sluice_weed": (-8470.0, 711.0, 86.2),
    # the shell shop: the ground floor of a house on the basin's north shore
    "shop_door": (-8546.5, 619.5, 101.9), "shop_sign": (-8548.0, 617.5, 104.5), "shop_front": (-8542.0, 616.0, 102.9),
    "tank": (-8531.0, 607.0, 102.9), "ashcombe": (-8534.0, 610.0, 102.9), "owl": (-8529.0, 613.0, 102.9),
    "cage_1": (-8538.0, 610.0, 102.9), "cage_2": (-8541.0, 613.0, 102.9), "cage_3": (-8536.0, 607.0, 102.9),
    "cage_4": (-8540.0, 617.0, 102.9),
    "curio_1": (-8543.0, 616.0, 102.9), "curio_2": (-8542.0, 610.0, 102.9), "curio_3": (-8539.0, 606.0, 102.9),
    "curio_4": (-8534.0, 605.0, 102.9), "curio_5": (-8530.0, 611.0, 102.9), "curio_6": (-8535.0, 618.0, 103.0),
    "jar_1": (-8537.0, 605.5, 102.9), "jar_2": (-8527.0, 609.0, 102.9),
    "blrrgl_door": (-8548.0, 621.0, 101.6), "pip_corner": (-8551.0, 623.5, 101.5),
    "barrel": (-8527.0, 590.0, 101.4), "patrol_south": (-8530.0, 575.0, 101.8), "patrol_north": (-8525.0, 600.0, 101.8),
    # the quiet south-east end: Pip's wall, the bell, Ashcombe's bench, the drain grates
    "pip_wall": (-8553.0, 514.0, 99.0), "pip_back": (-8554.0, 519.0, 99.6), "pip_rod": (-8551.5, 516.5, 99.1),
    "basin_water": (-8560.0, 507.0, 95.0), "bell": (-8550.0, 520.0, 101.3),
    "bench": (-8533.0, 491.0, 101.2), "ashcombe_bench": (-8533.5, 490.0, 101.2), "coat": (-8532.0, 492.0, 101.6),
    "grate_1": (-8559.0, 511.0, 95.3), "grate_2": (-8549.0, 497.0, 95.3), "grate_3": (-8541.0, 484.0, 95.3),
    "pip_stuck": (-8544.0, 486.0, 94.5), "grate_out": (-8540.0, 489.0, 100.3),
    # the Hadleys' door, on the street by the north arm
    "hadley_door": (-8487.0, 667.0, 100.9), "pip_home": (-8489.0, 664.0, 100.8), "pip_between": (-8488.5, 670.0, 100.9),
    "house_door": (-8486.0, 669.0, 100.9), "door_lamp": (-8490.0, 674.0, 100.6), "door_lamp_2": (-8484.0, 676.0, 100.9),
}

# -- the people -----------------------------------------------------------------------------------------------------

NPCS = [
    # Pip Hadley, a boy who fishes in the canals and doesn't scream (a sympathizer: the tribe's friend whatever the
    # murloc's standing in the city). His other places are SPAWNS.
    dict(key="pip", name="Pip Hadley", subname="", look=221, level=10, side="tribe", role="quest", language="common",
         at="pip_wall", facing=3.93, phase=("until", "ch6_hide"),
         greeting="Hello! Hello, fish-friend. Are you hungry? I've got an apple. I've always got an apple.",
         idle=[("every", 29000, [("emote", "self", "laugh"), ("sound", "self", 11821)]),
               ("every", 41000, [("emote", "self", "wave")])]),
    # Sergeant Garrett Hadley of the City Guard, at his door (always: he lives there)
    dict(key="hadley", name="Sergeant Garrett Hadley", subname="Stormwind City Guard", look=3167, level=70, side="tribe",
         role="quest", language="common", health=5.0, at="hadley_door", facing=1.44,
         greeting="Evening. Mind the canal, it's deeper than it looks. ...Light, what are you?",
         idle=[("every", 47000, [("emote", "self", "yes"), ("sound", "self", 5971)])]),
    # Ambrose Ashcombe, the collector, who loves Sloshy and will never let him go (yellow, but not to be hurt)
    dict(key="ashcombe", name="Ambrose Ashcombe", subname="Curiosities", look=5075, level=35, side="neutral",
         unit_flags=0x2, role="ambient", language="common", at="ashcombe", facing=5.5, phase=("until", "ch6_window"),
         idle=[("every", 26000, [("move", "self", "tank", "walk"), ("wait", 3500), ("face", "self", "tank"),
                                 ("emote", "self", "talk"), ("say", "self", "There, my treasure. Supper. Who's a handsome fellow?"),
                                 ("wait", 2000), ("emote", "self", "eat"), ("object", "tank_fish", "tank", 15),
                                 ("sound", "self", "splash_small"), ("wait", 4000), ("move", "self", "ashcombe", "walk")])]),
    # Sloshy in Ashcombe's tank (until the heist)
    dict(key="sloshy_tank", name="Sloshy", subname="", look="murloc_blue", scale=0.6, level=5, role="ambient",
         at="tank", facing=2.43, respawn=60, phase=("until", "ch6_heist"),
         watch=(14, [("face", "self", "player"), ("emote", "self", "beg"), ("sound", "self", "baby_murloc"), ("wait", 1500),
                     ("emote", "self", "beg"), ("wait", 1500), ("emote", "self", "cry"), ("sound", "self", "baby_murloc"),
                     ("wait", 2000), ("emote", "self", "cry")], 20000),
         idle=[("every", 30000, [("visual", "self", 35929)]), ("every", 23000, [("emote", "self", "cry")])]),
    # Sloshy free: the heist's follower, out of the broken tank
    dict(key="sloshy_free", name="Sloshy", subname="", look="murloc_blue", scale=0.6, level=5, role="ambient",
         summoned=True),
    # Sloshy at the grotto's mouth: he won't go in without you (6.14's giver)
    dict(key="sloshy_mouth", name="Sloshy", subname="", look="murloc_blue", scale=0.6, level=5, role="quest",
         at="mouth", facing=0.4, respawn=60, phase=("between", "ch6_heist", "ch6_home"),
         greeting="Mrgl? Mrgl! You! You you you!",
         idle=[("every", 19000, [("face", "self", "murlorga"), ("emote", "self", "shy"), ("sound", "self", "baby_murloc")]),
               ("every", 61000, [("move", "self", "mouth", "walk")])]),
    # the water-road's current-riders
    dict(key="gloomfin", name="Gloomfin", subname="Water-Road", look="murloc_abyssal", level=35, role="travel",
         at="rider", facing=3.97, travel=[("hide_arrive", "ch6_roads")],
         greeting="Murk-Eye's road. Down the coast, under the stone men's feet. Hold your breath. ...Or don't. We're murlocs.",
         idle=[("every", 31000, [("visual", "self", 36005), ("sound", "self", "splash")])]),
    dict(key="driftgill", name="Driftgill", subname="Water-Road", look="murloc_bronze", level=35, role="travel",
         at="hide", facing=1.57, travel=[("sluice_arrive", None)],
         greeting="The drain. It smells. It goes into their city. Everything goes into their city.",
         idle=[("every", 33000, [("visual", "self", 36005), ("sound", "self", "splash_small")]),
               ("every", 47000, [("face", "self", "harbour_dir"), ("emote", "self", "shy")])]),
    dict(key="sluicegill", name="Sluicegill", subname="Water-Road", look="murloc_ice", level=35, role="travel",
         at="sluicegill", facing=1.74, travel=[("hub_arrive", None)],
         greeting="Out through the sluice, out to the sea, home to the old one. Quick, before a boot comes.",
         idle=[("every", 37000, [("visual", "self", 36005), ("sound", "self", "splash_small")])]),
    # a City Guard on his round (scenes only: he walks, knocks, shrugs)
    dict(key="patrol", name="Stormwind City Guard", subname="", look=3167, level=70, side="neutral", unit_flags=0x2,
         role="ambient", language="common", health=5.0, summoned=True),
    dict(key="lantern_guard", name="Stormwind Harbor Guard", subname="", look=3167, level=65, side="neutral",
         unit_flags=0x2, role="ambient", language="common", health=5.0, summoned=True),
    # Ashcombe's other curiosities, in cages (while Pip's quest to free them is in the log)
    dict(key="parrot", name="Ashcombe's Parrot", look=5207, level=1, role="ambient", at="cage_1", facing=2.4,
         respawn=40, phase=("during", "ch6_free"), idle=[("every", 17000, [("sound", "self", 4005)])]),
    dict(key="baby_croc", name="Baby Crocolisk", look=22388, level=1, role="ambient", at="cage_2", facing=2.4,
         respawn=40, phase=("during", "ch6_free"), idle=[("every", 21000, [("emote", "self", "attack")])]),
    dict(key="fireflies", name="Jar of Fireflies", look=18722, scale=0.5, level=1, role="ambient", at="cage_3", facing=2.4,
         respawn=40, phase=("during", "ch6_free"), idle=[("every", 15000, [("visual", "self", 22580)])]),
    dict(key="tortoise", name="Very Old Tortoise", look=16359, level=1, role="ambient", at="cage_4", facing=2.4,
         respawn=40, phase=("during", "ch6_free")),
]

# -- things -------------------------------------------------------------------------------------------------------

HELM = "World\\Expansion02\\Doodads\\Generic\\Northrend_Helm_0{}.mdx"
ARROW = "World\\GENERIC\\HUMAN\\PASSIVE DOODADS\\WEAPONS&ARMOR\\HumanArrow.mdx"
GRATE = "World\\Expansion02\\Doodads\\Dalaran\\Dalaran_SewerGrate_01.mdx"
PIPE = "World\\Expansion02\\Doodads\\Dalaran\\Dalaran_sewer_oldworld_pipe01.mdx"
SEWERFALL = "World\\EXPANSION01\\DOODADS\\BLACKTEMPLE\\PASSIVEDOODADS\\SEWERWATER\\BT_SewerFall.mdx"
PET_CAGE = "World\\Expansion02\\Doodads\\Dalaran\\Dalaran_PetCage_01.mdx"
TANK = "World\\EXPANSION01\\DOODADS\\TEMPESTKEEP\\PASSIVEDOODADS\\Container\\TK_Container_01.mdx"
JAR = "World\\AZEROTH\\ELWYNN\\PASSIVEDOODADS\\Jars\\Jar0{}.mdx"
VIALS = "World\\GENERIC\\HUMAN\\PASSIVE DOODADS\\VIALS\\VialsBottles.mdx"
OWL = "World\\AZEROTH\\KARAZAHN\\PASSIVEDOODADS\\OWLSTATUE\\Karazahn_owlstatue.mdx"
SHOP_SIGN = "World\\AZEROTH\\ELWYNN\\PASSIVEDOODADS\\Signs\\Shop\\HumanMagicshopSign.mdx"
BENCH = "World\\GENERIC\\HUMAN\\PASSIVE DOODADS\\Benches\\StormWindBench01.mdx"
BELL = "World\\Goober\\G_BellShip.mdx"
SW_CRATE = "World\\GENERIC\\HUMAN\\PASSIVE DOODADS\\CRATES\\StormwindCrate01.mdx"
CRATE = "World\\GENERIC\\PASSIVEDOODADS\\Crate01\\Crate01.mdx"
POLE = "World\\AZEROTH\\BOOTYBAY\\PASSIVEDOODAD\\FishingPoles\\FishingPole01.mdx"
BOWL = "World\\AZEROTH\\WESTFALL\\PASSIVEDOODADS\\Utensils\\Bowl.mdx"
ROWBOAT = "World\\AZEROTH\\WESTFALL\\PASSIVEDOODADS\\WRECKEDROWBOAT\\WreckedRowBoat.mdx"
ANCHOR = "World\\AZEROTH\\WESTFALL\\PASSIVEDOODADS\\SunkenAnchor\\SunkenAnchor.mdx"
TRIDENT = "World\\Generic\\PassiveDoodads\\Weapons\\Naga_Trident.mdx"
SHELL = "World\\Kalimdor\\Azshara\\PassiveDoodads\\SeaShells\\AzsharaShell03.mdx"
FISH = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishDeadBlue.mdx"
FISH_RACK = "World\\Azeroth\\BootyBay\\PassiveDoodad\\DeadFish\\FishRack.mdx"
LOG = "World\\Azeroth\\SwampOSorrow\\PassiveDoodads\\TreeLogs\\SwampTreeLog01.mdx"
NET = "World\\Expansion02\\Doodads\\Generic\\TUSKARR\\Fishing\\TS_FishingBasket_empty_02.mdx"
LAMP = "World\\AZEROTH\\WESTFALL\\PASSIVEDOODADS\\LAMPPOST\\WestfallLampPost01.mdx"
DOOR_SIGN = "World\\AZEROTH\\ELWYNN\\PASSIVEDOODADS\\Signs\\GenericPosts\\GenericSmallSignPost01.mdx"
KELP = "World\\Generic\\Underwater\\PassiveDoodads\\Seaweed\\GenericSeaweed01.mdx"

OBJECTS = [
    # the camp (the hub kit's): huts, fires, Murlorga's pot, Blrrgl's log, nets, a fish rack
    dict(key="hut", model="murloc_hut", name="Hut", at=["hut1", "hut3"], kind="doodad", scale=1.0, facing=3.0, phase=HUB),
    dict(key="hut_b", model="murloc_hut2", name="Hut", at="hut2", kind="doodad", scale=1.0, facing=0.3, phase=HUB),
    dict(key="bonfire", model="bonfire", name="Fire", at="fire", kind="doodad", phase=HUB),
    dict(key="campfire", model="campfire", name="Fire", at="fire2", kind="doodad", phase=HUB),
    dict(key="cookpot", model=6849, name="Murlorga's Pot", at="cookpot", kind="doodad", scale=1.1, phase=HUB),
    dict(key="hollow_log", model=LOG, name="Hollow Log", at="blrrgl_log", kind="doodad", scale=0.6, facing=1.0, phase=HUB),
    dict(key="nets", model=NET, name="Fishing Basket", at=["net1", "net2"], kind="doodad", scale=0.8, phase=HUB),
    dict(key="fish_rack", model=FISH_RACK, name="Fish Rack", at="rack1", kind="doodad", facing=1.6, phase=HUB),
    # Old Murk-Eye's throne (always: it was here long before the tribe)
    dict(key="helm_1", model=HELM.format(1), name="Hero's Helmet", at=["helm_1", "helm_top_1"], kind="doodad", scale=1.2),
    dict(key="helm_2", model=HELM.format(2), name="Hero's Helmet", at=["helm_2", "helm_top_2"], kind="doodad", scale=1.2),
    dict(key="helm_3", model=HELM.format(3), name="Hero's Helmet", at="helm_3", kind="doodad", scale=1.2),
    dict(key="helm_4", model=HELM.format(4), name="Hero's Helmet", at="helm_4", kind="doodad", scale=1.2),
    # 6.03: the arrows in Murk-Eye's back
    dict(key="arrow", model=ARROW, name="Old Arrow", kind="use", quest="ch6_arrows", goal="Old arrow pulled", scale=1.4,
         at=["arrow_1", "arrow_2", "arrow_3", "arrow_4", "arrow_5"], phase=("during", "ch6_arrows"),
         beats=[("give", "old_arrow", 1), ("emote", "ch0:murkeye", "roar"), ("sound", "ch0:murkeye", "murloc_wound_crit"),
                ("sound", "ch0:murkeye", 6526), ("wait", 1500), ("emote", "ch0:murkeye", "cry")]),
    # 6.15: the sunken ship's last gift
    dict(key="old_spear", model=TRIDENT, name="Barnacled Spear", kind="loot", loot=[("old_spear", 1, 1)],
         quest="ch6_spear", scale=1.3, at="wreck", phase=("during", "ch6_spear")),
    dict(key="anchor", model=ANCHOR, name="Sunken Anchor", at="wreck_anchor", kind="doodad"),
    # the water-road's harbour end: the city's drain under the walls, its grate
    dict(key="drain_pipe", model=PIPE, name="Old Drain", at="drain_pipe", kind="doodad", facing=1.57, scale=1.5),
    dict(key="drain_fall", model=SEWERFALL, name="Drain Water", at="drain_pipe", kind="doodad", facing=1.57, scale=0.4),
    dict(key="drain_grate", model=GRATE, name="Drain Grate", at="drain_grate", kind="doodad", facing=1.57),
    # 6.04: the route's marks
    dict(key="piling_barnacle", model="clam", name="Barnacled Piling", kind="loot", loot=[("piling_barnacle", 1, 1)],
         quest="ch6_roads", scale=1.4, at="pilings"),
    dict(key="sluice_weed", model=KELP, name="Sluice Weed", kind="loot", loot=[("sluice_weed", 1, 1)],
         quest="ch6_roads", scale=0.8, at="sluice_weed"),
    dict(key="sluice_grate", model=GRATE, name="Sluice Grate", at="sluice_grate", kind="doodad", facing=0.0),
    # 6.05: three places in the harbour by night (each one, a guard's lantern comes looking)
    dict(key="pier_mussel", model="clam", name="Pier Mussels", kind="use", quest="ch6_harbor", at="under_pier",
         scale=1.3, phase=("during", "ch6_harbor"),
         beats=[("give", "pier_mussel", 1), ("summon", "lantern_guard", "quay_guard", 12), ("wait", 500),
                ("face", "lantern_guard", "under_pier"), ("emote", "lantern_guard", "point"),
                ("yell", "lantern_guard", "Who's down there? Show yourself!", None, 5973), ("wait", 4000),
                ("emote", "lantern_guard", "question"), ("wait", 3000), ("despawn", "lantern_guard")]),
    dict(key="dock_tar", model="barrel", name="Tar Barrel", kind="use", quest="ch6_harbor", at="drydock",
         phase=("during", "ch6_harbor"),
         beats=[("give", "drydock_tar", 1), ("summon", "lantern_guard", "dock_guard", 12), ("wait", 500),
                ("face", "lantern_guard", "player"), ("emote", "lantern_guard", "point"),
                ("yell", "lantern_guard", "Oi! Who's in the dry dock?", None, 5973), ("wait", 4000),
                ("emote", "lantern_guard", "no"), ("wait", 3000), ("despawn", "lantern_guard")]),
    dict(key="drain_rust", model="sack", name="Rusted Bars", kind="loot", loot=[("grate_rust", 1, 1)],
         quest="ch6_harbor", scale=0.5, at="drain_rust", phase=("during", "ch6_harbor")),
    # the shell shop: its sign, its shelves, Sloshy's tank, the cages (always: the shop is the shop)
    dict(key="shop_sign", model=SHOP_SIGN, name="Ashcombe's Curiosities", at="shop_sign", kind="doodad", facing=2.4),
    dict(key="shop_jar", model=JAR.format(1), name="Jar of Something", at=["jar_1", "jar_2"], kind="doodad", scale=0.9),
    dict(key="shop_owl", model=OWL, name="Stuffed Owl", at="owl", kind="doodad", scale=0.25, facing=2.4),
    dict(key="tank", model=TANK, name="Glass Tank", kind="use", quest="ch6_heist", goal="Sloshy's tank broken",
         at="tank", scale=0.45, facing=2.4,
         beats=[("summon", "sloshy_free", "tank", 240), ("wait", 300), ("sound", "sloshy_free", 12334),
                ("despawn", "sloshy_tank"), ("wait", 800), ("emote", "sloshy_free", "cheer"),
                ("sound", "sloshy_free", "baby_murloc"), ("follow", "sloshy_free"), ("wait", 2000),
                ("emote", "sloshy_free", "cry"), ("sound", "sloshy_free", "baby_murloc")]),
    # 6.11a: the cages
    dict(key="cage_parrot", model=PET_CAGE, name="Parrot Cage", kind="use", quest="ch6_free", goal="Parrot freed",
         at="cage_1", scale=0.8, facing=2.4,
         beats=[("sound", "parrot", 4005), ("move", "parrot", "shop_door", "run"), ("wait", 2500),
                ("sound", "parrot", 4000), ("move", "parrot", "pip_corner", "run"), ("wait", 3000), ("despawn", "parrot")]),
    dict(key="cage_croc", model=PET_CAGE, name="Crocolisk Cage", kind="use", quest="ch6_free", goal="Crocolisk freed",
         at="cage_2", scale=0.8, facing=2.4,
         beats=[("move", "baby_croc", "blrrgl_door", "run"), ("wait", 2500), ("emote", "baby_croc", "attack"),
                ("sound", "baby_croc", 1225), ("emote", "ch1:blrrgl", "cry"), ("sound", "ch1:blrrgl", "murloc_wound"),
                ("wait", 2000), ("move", "baby_croc", "basin_water", "run"), ("wait", 4000), ("despawn", "baby_croc")]),
    dict(key="cage_fireflies", model=PET_CAGE, name="Firefly Jar", kind="use", quest="ch6_free", goal="Fireflies freed",
         at="cage_3", scale=0.8, facing=2.4,
         beats=[("visual", "fireflies", 22580), ("visual", "fireflies", 22576), ("move", "fireflies", "shop_front", "walk"),
                ("wait", 4000), ("visual", "fireflies", 22581), ("move", "fireflies", "pip_corner", "walk"), ("wait", 4000),
                ("emote", "pip", "applaud"), ("despawn", "fireflies")]),
    dict(key="cage_tortoise", model=PET_CAGE, name="Tortoise Cage", kind="use", quest="ch6_free", goal="Tortoise freed",
         at="cage_4", scale=0.8, facing=2.4,
         beats=[("face", "tortoise", "player"), ("wait", 4000), ("sound", "tortoise", 1463), ("wait", 6000),
                ("face", "tortoise", "shop_door")]),
    # 6.11b: what's worth something
    dict(key="curio_vials", model=VIALS, name="Curious Vials", kind="use", quest="ch6_loot", at=["curio_1", "curio_4"],
         scale=0.8, beats=[("give", "curio", 1), ("aura", "player", "heavy_bag"), ("emote", "ch1:blrrgl", "point"),
                           ("emote", "ch1:blrrgl", "laugh"), ("emote", "pip", "no")]),
    dict(key="curio_jar", model=JAR.format(2), name="Painted Jar", kind="use", quest="ch6_loot", at=["curio_2", "curio_5"],
         beats=[("give", "curio", 1), ("aura", "player", "heavy_bag"), ("emote", "ch1:blrrgl", "point"),
                ("emote", "ch1:blrrgl", "beg"), ("sound", "ch1:blrrgl", "murloc_fidget")]),
    dict(key="curio_box", model=SW_CRATE, name="Brass-Bound Box", kind="use", quest="ch6_loot", at=["curio_3", "curio_6"],
         scale=0.4, beats=[("give", "curio", 1), ("aura", "player", "heavy_bag"), ("emote", "ch1:blrrgl", "point"),
                           ("emote", "ch1:blrrgl", "point"), ("emote", "ch1:blrrgl", "laugh"), ("emote", "pip", "cry")]),
    # the quiet end: Pip's rod, the bell, Ashcombe's bench and coat, the drain grates
    dict(key="pip_pole", model=POLE, name="Pip's Fishing Rod", at="pip_rod", kind="doodad", facing=3.9,
         phase=("until", "ch6_hide")),
    dict(key="pip_pole_left", model=POLE, name="Pip's Fishing Rod", at="pip_rod", kind="doodad", facing=0.6,
         phase=("between", "ch6_heist", "ch6_hadley")),
    dict(key="bell", model=BELL, name="Canal Bell", at="bell", kind="doodad", facing=2.0),
    dict(key="bench", model=BENCH, name="Canal Bench", at="bench", kind="doodad", facing=3.4),
    dict(key="coat", model="sack", name="Velvet Coat", kind="loot", loot=[("shop_key", 1, 1)], quest="ch6_key",
         scale=0.6, at="coat", phase=("during", "ch6_key")),
    dict(key="drain_grates", model=GRATE, name="Drain Grate", at=["grate_1", "grate_2", "grate_3"], kind="doodad", facing=3.9),
    # the Hadleys' door: a sign and the street's lanterns
    dict(key="hadley_sign", model=DOOR_SIGN, name="Hadley", at="house_door", kind="doodad", facing=1.44, scale=0.6),
    dict(key="lamp", model=LAMP, name="Lantern", at=["door_lamp", "door_lamp_2"], kind="doodad"),
    # 6.07: the barrel Pip points at
    dict(key="barrel", model=32, name="Barrel", kind="use", quest="ch6_hide", goal="Hid in the barrel", at="barrel",
         beats=[("aura", "player", "barrel"), ("summon", "patrol", "patrol_south", 25), ("wait", 600),
                ("move", "patrol", "barrel", "walk"), ("emote", "pip", "shy"), ("wait", 7000), ("face", "patrol", "barrel"),
                ("emote", "patrol", "attack"), ("sound", "patrol", 1194), ("wait", 900), ("emote", "patrol", "attack"),
                ("sound", "patrol", 1194), ("wait", 1500), ("emote", "patrol", "question"), ("wait", 2500),
                ("emote", "patrol", "no"), ("sound", "patrol", 7914), ("move", "patrol", "patrol_north", "walk"),
                ("wait", 1500), ("emote", "pip", "laugh"), ("sound", "pip", 11821), ("wait", 9000), ("despawn", "patrol")]),
    # 6.18 and 6.19: the Theramore ship's crates on the pier, one with its lid off
    dict(key="pier_crates", model=SW_CRATE, name="Crate for Theramore", at=["pier_crates", "pier_crates_2"], kind="doodad",
         facing=0.3, phase=("from", "ch6_hadley")),
    dict(key="crate_open", model=CRATE, name="Open Crate", kind="use", quest="ch6_end", goal="Climbed into the crate",
         at="pier_open", scale=1.3, facing=1.2, phase=("during", "ch6_end"),
         beats=[("aura", "player", "crated"), ("sound", "ch1:blrrgl", 8016), ("emote", "ch1:blrrgl", "cheer"),
                ("sound", "ch1:blrrgl", "murloc_fidget")]),

    # set out by scenes
    dict(key="thrown_fish", model=FISH, name="Fish", kind="doodad", scale=1.2),
    dict(key="tank_fish", model=FISH, name="Supper", kind="doodad", scale=0.5),
    dict(key="sand_shell", model=SHELL, name="Drawing in the Sand", kind="doodad", scale=1.0),
    dict(key="sand_ship", model=ROWBOAT, name="Drawing in the Sand", kind="doodad", scale=0.15),
    dict(key="sand_spear", model=TRIDENT, name="Drawing in the Sand", kind="doodad", scale=0.5),
    dict(key="dropped_ladle", model=BOWL, name="Murlorga's Ladle", kind="doodad", scale=1.2),
    dict(key="tiny_coat", model="sack", name="A Tiny Coat", kind="doodad", scale=0.25),
    dict(key="lid_off", model=CRATE, name="Open Crate", kind="doodad", scale=1.3),
]

# -- items -------------------------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for
    dict(key="helmet", name="Battered Defias Helm", icon="item:829", stack=6, description="It still smells of the last head."),
    dict(key="old_arrow", name="Old Arrow", icon="item:2512", stack=5, description="A hero's. The hero's gone."),
    dict(key="piling_barnacle", name="Piling Barnacle", icon="shell"),
    dict(key="sluice_weed", name="Sluice Weed", icon="kelp"),
    dict(key="pier_mussel", name="Pier Mussel", icon="mussel"),
    dict(key="drydock_tar", name="Dry Dock Tar", icon="item:3372"),
    dict(key="grate_rust", name="Grate Rust", icon="item:2880"),
    dict(key="shop_key", name="Shop Key", icon="key", description="Brass, and warm from a coat pocket."),
    dict(key="curio", name="Dusty Curio", icon="trinket", stack=6),
    dict(key="stew_bucket", name="Bucket of Westfall Stew", icon="item:733",
         description="Murlorga made it. Murlorga is not responsible for what happens next."),
    dict(key="old_spear", name="Murk-Eye's Old Spear", icon="spear", description="Barnacles. A lot of barnacles."),
    dict(key="pips_drawing", name="Pip's Drawing", icon="letter",
         description="A box of water, a small murloc in it, and a shop sign shaped like a shell. Drawn in coal, with love."),

    # rewards (levels 33 to 36: the game's quests' greens at these levels)
    dict(key="throne_cap", name="Throne-Polished Cap", kind="armor:cloth:head", quality=2, level=34,
         stats=[("int", 6), ("spi", 5), ("sta", 4)]),
    dict(key="throne_hood", name="Throne-Polished Hood", kind="armor:leather:head", quality=2, level=34,
         stats=[("agi", 7), ("sta", 6)]),
    dict(key="throne_helm", name="Throne-Polished Helm", kind="armor:mail:head", quality=2, level=34,
         stats=[("str", 7), ("sta", 6)]),
    dict(key="arrowhead", name="Hero-Bane Arrowhead", kind="neck", quality=2, level=34, stats=[("agi", 4), ("sta", 4)]),
    dict(key="dodger_trousers", name="Lantern-Dodger's Trousers", kind="armor:cloth:legs", quality=2, level=35,
         stats=[("int", 7), ("spi", 6), ("sta", 4)]),
    dict(key="dodger_breeches", name="Lantern-Dodger's Breeches", kind="armor:leather:legs", quality=2, level=35,
         stats=[("agi", 8), ("sta", 6)]),
    dict(key="dodger_legguards", name="Lantern-Dodger's Legguards", kind="armor:mail:legs", quality=2, level=35,
         stats=[("str", 8), ("sta", 6)]),
    dict(key="hoop_cuffs", name="Barrel-Hoop Cuffs", kind="armor:cloth:wrist", quality=2, level=34,
         stats=[("int", 4), ("spi", 3)]),
    dict(key="hoop_bracers", name="Barrel-Hoop Bracers", kind="armor:leather:wrist", quality=2, level=34,
         stats=[("agi", 4), ("sta", 3)]),
    dict(key="hoop_vambraces", name="Barrel-Hoop Vambraces", kind="armor:mail:wrist", quality=2, level=34,
         stats=[("str", 4), ("sta", 3)]),
    dict(key="road_slippers", name="Water-Road Slippers", kind="armor:cloth:feet", quality=2, level=36,
         stats=[("int", 6), ("sta", 5)]),
    dict(key="road_treads", name="Water-Road Treads", kind="armor:leather:feet", quality=2, level=36,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="road_sabatons", name="Water-Road Sabatons", kind="armor:mail:feet", quality=2, level=36,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="firefly_jar", name="Jar of Loose Fireflies", kind="offhand", quality=2, level=35, stats=[("int", 5), ("spi", 4)],
         description="Empty. That's the point."),
    dict(key="spyglass", name="Ashcombe's Brass Spyglass", kind="trinket", quality=2, level=35, stats=[("agi", 5), ("sta", 4)],
         description="Found. On a shelf. Nobody was using it."),
    dict(key="watch_gloves", name="Night Watch Gloves", kind="armor:cloth:hands", quality=2, level=36,
         stats=[("int", 6), ("spi", 6)]),
    dict(key="lamplighter_grips", name="Lamplighter's Grips", kind="armor:leather:hands", quality=2, level=36,
         stats=[("agi", 7), ("sta", 5)]),
    dict(key="sergeant_gauntlets", name="Sergeant's Spare Gauntlets", kind="armor:mail:hands", quality=2, level=36,
         stats=[("str", 7), ("sta", 5)]),
    dict(key="sloshy_ring", name="Sloshy's Shell Ring", kind="ring", quality=2, level=35, stats=[("sta", 5), ("spi", 4)],
         description="He made it in the tank. He had a lot of time in the tank."),
    dict(key="murkeye_spear", name="Murk-Eye's Spear", kind="weapon:spear", quality=2, level=36,
         stats=[("str", 10), ("sta", 9)], description="It sank a ship once. It can do it again."),
    dict(key="murkeye_tooth", name="Murk-Eye's Old Tooth", kind="weapon:dagger", quality=2, level=36,
         stats=[("agi", 6), ("sta", 5)], description="He says it fell out. He says a lot of things."),
    dict(key="murkeye_staff", name="Murk-Eye's Driftwood Staff", kind="weapon:staff", quality=2, level=36,
         stats=[("int", 10), ("spi", 9)], description="He leaned on it for a hundred years. Lean on it a little."),
    dict(key="grotto_stew", name="Bowl of Grotto Stew", kind="food", level=35, icon="item:733"),
    dict(key="mrrk_tooth", name="Mrrk's Grudging Tooth", kind="neck", quality=2, level=35, stats=[("str", 5), ("agi", 4)]),
    dict(key="sergeant_cloak", name="Sergeant's Old Cloak", kind="armor:cloth:back", quality=2, level=36,
         stats=[("sta", 5), ("agi", 3)], description="Somebody left it on the pier. Nobody saw who."),
    dict(key="stowaway_robe", name="Stowaway's Robe", kind="armor:cloth:chest", quality=2, level=36,
         stats=[("int", 9), ("spi", 7), ("sta", 6)]),
    dict(key="stowaway_jerkin", name="Stowaway's Jerkin", kind="armor:leather:chest", quality=2, level=36,
         stats=[("agi", 9), ("sta", 8)]),
    dict(key="stowaway_hauberk", name="Stowaway's Hauberk", kind="armor:mail:chest", quality=2, level=36,
         stats=[("str", 9), ("sta", 8)]),
]

# -- auras -------------------------------------------------------------------------------------------------------

AURAS = [
    dict(key="barrel", name="In a Barrel", kind="disguise", look=29775, seconds=25, icon=1784,
         text="You are a barrel. Barrels don't breathe."),
    dict(key="crated", name="Cargo", kind="disguise", look=20366, seconds=40, icon=1784, text="You are a crate for Theramore."),
    dict(key="heavy_bag", name="Heavy Bag", kind="slow", percent=25, seconds=90, icon=246,
         text="A bag of other people's curiosities."),
]

# -- the tribe at the grotto, and its people in the city -----------------------------------------------------------------

SPAWNS = [
    # the Elder on the beach, as the turtle lands (the chapter's first quest), and in the camp after
    dict(npc="ch1:elder", at="elder_beach", facing=5.39, phase=("between", "ch5:ch5_end", "ch6_arrival")),
    dict(npc="ch1:elder", at="elder", facing=2.57, phase=HUB),
    # Old Murk-Eye on his throne (always: he has been here longer than anyone)
    dict(npc="ch0:murkeye", at="murkeye", facing=2.32),
    # the hub kit (17.1)
    dict(npc="ch1:grrmlgrrl", at="grrmlgrrl", facing=3.97, phase=HUB),
    dict(npc="ch1:murlorga", at="murlorga", facing=1.11, phase=HUB),
    dict(npc="ch1:blrrgl", at="blrrgl", facing=5.64, phase=HUB),
    dict(npc="ch1:glubbub", at="glubbub", facing=3.28, phase=HUB),
    dict(npc="ch1:brrgmrk", at="t_warrior", facing=4.03, phase=HUB),
    dict(npc="ch1:mrrgasha", at="t_hunter", facing=4.37, phase=HUB),
    dict(npc="ch1:glubba", at="t_priest", facing=3.67, phase=HUB),
    dict(npc="ch1:fizzmrgl", at="t_mage", facing=5.02, phase=HUB),
    dict(npc="ch1:slubb", at="t_firstaid", facing=5.39, phase=HUB),
    dict(npc="ch1:gurgle", at="t_fishing", facing=5.18, phase=HUB),
    dict(npc="ch1:mrrlglr", at="fishmonger", facing=1.83, phase=HUB),
    dict(npc="ch0:krrgl", at="krrgl", facing=5.84, phase=HUB),
    dict(npc="ch0:brrkl", at="brrkl", facing=6.2, phase=HUB),
    dict(npc="ch0:mmrglla", at="mmrglla", facing=5.62, phase=HUB),
    dict(npc="ch0:grrsh", at="grrsh", facing=5.18, phase=HUB),
    dict(npc="ch0:mrrsk", at="mrrsk", facing=4.95, phase=HUB),
    dict(npc="ch0:mrsha", at="mrsha", facing=4.74, phase=HUB),
    dict(npc="ch0:brewglub", at="brewglub", facing=4.52, phase=HUB),
    dict(npc="ch0:sprokgl", at="sprokgl", facing=4.29, phase=HUB),
    dict(npc="ch0:shimmrl", at="shimmrl", facing=4.08, phase=HUB),
    dict(npc="ch0:pearlmrgl", at="pearlmrgl", facing=3.79, phase=HUB),
    dict(npc="ch0:scrawlgl", at="scrawlgl", facing=3.44, phase=HUB),
    dict(npc="ch0:fnrrgl", at="fnrrgl", facing=0.29, phase=HUB),
    dict(npc="ch0:caller", at="caller", facing=0.71, phase=HUB),
    dict(npc="ch0:mrrk", at="mrrk", facing=4.77, phase=HUB),
    dict(object="ch0:mailbox", at="mailbox", facing=1.0, phase=HUB),
    # Grandmother Shellback in the sea outside, until the tribe leaves for the marsh
    dict(npc="ch0:shellback", at="shellback", facing=0.4, phase=("between", "ch5:ch5_end", "ch6_end")),
    # Sloshy at home (6.14 on): in every hub from here
    dict(npc="ch1:sloshy", at="sloshy_home", facing=1.21, phase=("from", "ch6_home")),

    # Blrrgl in the city: hiding under the walls on the first night, at the sluice, in the shop's doorway during the
    # heist, by the crates on the pier at the end
    dict(npc="ch1:blrrgl", at="blrrgl_hide", facing=1.2, phase=("during", "ch6_harbor"), state="cower"),
    dict(npc="ch1:blrrgl", at="blrrgl_sluice", facing=1.98, phase=("between", "ch6_roads", "ch6_missing")),
    dict(npc="ch1:blrrgl", at="blrrgl_door", facing=5.5, phase=("during", "ch6_heist")),
    dict(npc="ch1:blrrgl", at="pier_blrrgl", facing=3.4, phase=("during", "ch6_end")),
    # Pip: at the shop's corner (lookout), stuck in the third grate after the bell, home with his father after
    dict(npc="pip", at="pip_corner", facing=5.56, phase=("between", "ch6_hide", "ch6_heist")),
    dict(npc="pip", at="pip_stuck", facing=1.0, phase=("between", "ch6_heist", "ch6_hadley")),
    dict(npc="pip", at="pip_home", facing=1.44, phase=("from", "ch6_hadley")),
    # Ashcombe asleep on his bench after lunch (while the key's quest is in the log)
    dict(npc="ashcombe", at="ashcombe_bench", facing=3.39, phase=("during", "ch6_key"), state="sleep"),
    # the sergeant on the pier, looking at the sky
    dict(npc="hadley", at="pier_hadley", facing=3.03, phase=("between", "ch6_hadley", "ch6_end")),
]

GRAVEYARDS = [
    dict(at="graveyard", name="Murk-Eye's Grotto", phase=HUB, facing=5.42),
    dict(at="graveyard_sw", name="under Stormwind's walls", facing=1.57),
]

# -- the quests ------------------------------------------------------------------------------------------------------

TAP = [("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977),
       ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977)]

QUESTS = [
    # 6.01: the oldest murloc
    dict(key="ch6_arrival", title="The Oldest Murloc", giver="ch1:elder", ender="ch0:murkeye", level=33, xp=8, tone="funny",
         prev="ch5:ch5_end", explore="grotto", radius=10,
         goal="Find Old Murk-Eye's grotto at the head of the inlet under the cliffs, on the spit south of the Westfall lighthouse.",
         text="Smell that? Old fish. Very, very old fish. The song said he lives here, under the cliffs... the oldest murloc "
              "alive. Older than me. Go and find him. Be polite. Be very polite.",
         progress="Did you find him? Did he eat you?",
         reward="HAH! More of you! Little scarred ones, all in a row! Come in, come in. I have outlived a hundred heroes. "
                "I will outlive you too.",
         details=["talk", "point"], reward_emotes=["laugh", "talk"],
         accept=[("emote", "self", "question"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("face", "self", "grotto"),
                 ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "attack"), ("sound", "self", 977),
                 ("wait", 1200), ("face", "self", "hub_arrive")],
         complete=[("state", "self", "none"), ("emote", "self", "question"), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                   ("emote", "self", "question"), ("wait", 1500), ("sound", "self", "murloc_aggro"), ("emote", "self", "laugh"),
                   ("wait", 2000), ("face", "self", "blrrgl"), ("emote", "self", "throw"),
                   ("object", "thrown_fish", "blrrgl", 30), ("sound", "ch1:blrrgl", 1189), ("emote", "ch1:blrrgl", "cry"),
                   ("sound", "ch1:blrrgl", "murloc_wound"), ("wait", 1500), ("emote", "self", "laugh"),
                   ("sound", "self", "murloc_aggro_old"), ("wait", 3000), ("face", "self", "inlet"), ("state", "self", "sit")],
         poi=["grotto"]),

    # 6.02: helmets for the throne
    dict(key="ch6_helmets", title="Helmets for the Throne", giver="ch0:murkeye", ender="ch0:murkeye", level=33, xp=8,
         tone="funny", prev="ch6_arrival", items=[("helmet", 6)], drops={"helmet": [(122, 45), (449, 45), (121, 45)]},
         goal="Take 6 Battered Defias Helms from the Defias Highwaymen camped on the hill east of the grotto.",
         text="My throne is a pile of the hats of men who came to kill me. A good pile. Not a high pile. The dry-skins on the "
              "hill wear hats. 6 hats! Then I sit higher, and see farther, and laugh longer.",
         progress="Hats. I count no hats.",
         reward="1, 2, 3, 4, 5, 6! Up, up, up... HAH! Look at me! King of all the hats!",
         details=["talk", "point", "laugh"], reward_emotes=["cheer", "laugh"],
         choice=["throne_cap", "throne_hood", "throne_helm"],
         accept=[("state", "self", "none"), ("emote", "self", "work"), ("sound", "self", 1194), ("wait", 1500),
                 ("emote", "self", "flex"), ("wait", 1500), ("face", "self", "defias_camp"), ("emote", "self", "point"),
                 ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", "murloc_aggro"), ("wait", 1500),
                 ("face", "self", "inlet"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("object", "helm_1", "helm_top_1", 60), ("sound", "self", 1194), ("wait", 900),
                   ("object", "helm_2", "helm_top_2", 60), ("sound", "self", 1194), ("wait", 1200),
                   ("jump", "self", "throne"), ("wait", 1500), ("emote", "self", "dance"), ("sound", "self", "murloc_aggro"),
                   ("wait", 2500), ("emote", "self", "cheer"), ("wait", 2000), ("move", "self", "murkeye", "walk"),
                   ("wait", 1500), ("face", "self", "inlet"), ("state", "self", "sit")],
         poi=["defias_camp"]),

    # 6.03: a hundred arrows
    dict(key="ch6_arrows", title="A Hundred Arrows", giver="ch0:murkeye", ender="ch0:murkeye", level=33, xp=8, tone="funny",
         prev="ch6_arrival", objects=[("arrow", 5)],
         goal="Pull 5 Old Arrows out of Old Murk-Eye's back, at his throne.",
         text="Every hero who came to kill me left me something. Mostly arrows. Mostly in my back, because I was running. "
              "Running is how you get old. Pull them out. Gently. Gently! ...Not gently. Just pull. 5 of them.",
         progress="Itches. Still itches.",
         reward="Ahhh. Light as a fry. You see these holes? Every one, a hero. And where are the heroes now? Hm? "
                "Hide. Live. That is all the wisdom I have. It is enough.",
         details=["talk", "point"], reward_emotes=["talk", "point"], rewards=["arrowhead"],
         accept=[("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "point"),
                 ("wait", 1200), ("emote", "self", "beg"), ("sound", "self", "murloc_fidget2")],
         complete=[("state", "self", "none"), ("face", "self", "player"), ("wait", 2500), ("emote", "self", "point"),
                   ("wait", 1500), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "shy"), ("music", 6075),
                   ("wait", 2500), ("face", "self", "hiding_holes"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 4000), ("face", "self", "inlet"), ("state", "self", "sit")],
         poi=["murkeye"]),

    # 6.04: the water-roads (boring: and the heist's road)
    dict(key="ch6_roads", title="The Water-Roads", giver="ch0:murkeye", ender="ch0:murkeye", level=33, xp=8, tone="boring",
         prev="ch6_arrival", interact=[("gloomfin", "Ride the current.")], interact_goal="Rode Murk-Eye's current",
         interact_beats=[("visual", "self", 36005), ("sound", "self", "splash_big"), ("emote", "self", "point"),
                         ("wait", 1500), ("visual", "player", 36005), ("sound", "self", 4123), ("wait", 800),
                         ("teleport", "player", "hide_arrive", 1.57)],
         items=[("piling_barnacle", 1), ("sluice_weed", 1)],
         goal="Ride Gloomfin's current from the grotto's mouth to Stormwind Harbor. Pull a Piling Barnacle from under the "
              "harbour's south quay, ride Driftgill's current through the drain into the city's canals, take Sluice Weed "
              "from under the sluice at the canal's end, and ride Sluicegill's current home.",
         text="The water-roads. Old roads. Only murlocs and fish know them. Down the coast, into the stone men's harbour, under "
              "their feet, through their drain, into their canals... and home again. Watch. I draw it. Again. Again. "
              "Now you go.",
         progress="Long, isn't it? It is supposed to be long.",
         reward="You came back the same way you went. Good. A water-road is only a road if you come home on it.",
         details=["talk", "point"], reward_emotes=["yes", "talk"],
         accept=[("state", "self", "none"), ("emote", "self", "kneel"), ("object", "sand_shell", "sand_1", 50),
                 ("sound", "self", 1194), ("wait", 4000), ("object", "sand_shell", "sand_2", 50), ("sound", "self", 1194),
                 ("wait", 4000), ("object", "sand_shell", "sand_3", 50), ("sound", "self", 1194), ("wait", 4000),
                 ("emote", "self", "kneel"), ("sound", "self", 1194), ("wait", 4000), ("emote", "self", "kneel"),
                 ("sound", "self", 1194), ("wait", 4000), ("emote", "self", "kneel"), ("sound", "self", 1194), ("wait", 3000),
                 ("face", "self", "rider"), ("emote", "self", "point"), ("wait", 2000), ("face", "self", "inlet"),
                 ("state", "self", "sit")],
         complete=[("emote", "self", "yes"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "talk")],
         poi=["rider", "pilings", "sluice_grate"]),

    # 6.05: the harbour at night
    dict(key="ch6_harbor", title="The Harbor at Night", giver="ch0:murkeye", ender="ch0:murkeye", level=34, xp=8,
         tone="serious", prev="ch6_roads", objects=[("pier_mussel", 1), ("dock_tar", 1)], items=[("grate_rust", 1)],
         goal="Ride the water-road to Stormwind Harbor by night and touch three places: the mussels under the south quay, "
              "the tar barrel in the dry dock at the harbour's north end, and the rusted bars by the drain under the city's "
              "walls. Keep clear of the guards' lanterns.",
         text="The stone men's harbour. Big. Bigger than anything. Lanterns everywhere, and under every lantern a man with a "
              "sword. Go at night. Go under. Touch 3 things and come back and tell me how big it was.",
         progress="Did they see you? You still have your head. They did not see you.",
         reward="HAH! You smell of tar and fear. Good smells. The smells of a murloc who goes places and comes back.",
         details=["talk", "point", "laugh"], reward_emotes=["laugh", "flex"],
         choice=["dodger_trousers", "dodger_breeches", "dodger_legguards"],
         accept=[("state", "self", "none"), ("face", "self", "north"), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", 430), ("sound", "self", "murloc_alert"), ("wait", 1800), ("emote", "self", "laugh"),
                 ("sound", "self", "murloc_aggro"), ("wait", 1500), ("face", "self", "inlet"), ("state", "self", "sit")],
         complete=[("emote", "self", "laugh"), ("sound", "self", "murloc_aggro"), ("wait", 1500), ("emote", "self", "flex")],
         poi=["under_pier", "drydock", "drain_rust"]),

    # 6.06: Pip
    dict(key="ch6_pip", title="Pip", giver="ch0:murkeye", ender="pip", level=34, xp=8, tone="serious", path="hero",
         prev="ch6_harbor", rep=[(72, 250)],
         goal="Find the boy who fishes at the quiet south-east end of Stormwind's canals. The water-road's drain brings you "
              "into the canals at the sluice; follow the water south.",
         text="The current-song says a small dry-skin fishes in the canals and does not scream. A dry-skin that does not "
              "scream! I have lived a long time and never met one. Go and look. If he screams, run.",
         reward="Oh! Oh... you're real. You're really, really real. Don't be scared, I won't tell. Here, do you like apples? "
                "And look, I drew this. That's your friend, isn't it? In the shell shop.",
         details=["talk", "point"], reward_emotes=["exclamation", "talk"], rewards=["pips_drawing"],
         accept=[("state", "self", "none"), ("emote", "self", "shy"), ("wait", 1500), ("face", "self", "north"),
                 ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("face", "self", "inlet"),
                 ("state", "self", "sit")],
         complete=[("emote", "self", "exclamation"), ("sound", "self", 11818), ("wait", 2500), ("emote", "self", "beg"),
                   ("give", 4536, 1), ("wait", 1500), ("move", "self", "pip_back", "walk"), ("wait", 2500),
                   ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 2000), ("emote", "self", "point"),
                   ("sound", "self", 11821), ("wait", 3000), ("move", "self", "pip_wall", "walk"), ("wait", 2500),
                   ("face", "self", "basin_water")],
         poi=["pip_wall"]),

    # 6.07: hide-and-seek in the canals
    dict(key="ch6_hide", title="Hide-and-Seek in the Canals", giver="pip", ender="pip", level=34, xp=8, tone="funny",
         path="hero", prev="ch6_pip", rep=[(72, 250)], escort=("pip", ["pip_wall", "barrel", "shop_door"]), radius=6,
         objects=[("barrel", 1)],
         goal="Take Pip along the canal walks to the shell shop on the north shore of the canal basin. When a guard comes, "
              "hide in the barrel by the street on the way.",
         text="Want to see him? Come on! Stay close, stay low. If a guard comes, I know a trick. Follow me... I mean, I'll "
              "follow you. Whatever. Go!",
         progress="Shh! Are we there yet?",
         reward="We made it! Did you see the guard's face? Knock, knock! Nobody home! Hee hee! Look, there's the shop. "
                "The shell sign.",
         details=["wave", "point"], reward_emotes=["laugh", "point"], choice=["hoop_cuffs", "hoop_bracers", "hoop_vambraces"],
         accept=[("emote", "self", "wave"), ("sound", "self", 11821), ("wait", 1500), ("face", "self", "barrel"),
                 ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "shy")],
         complete=[("emote", "self", "laugh"), ("sound", "self", 11821), ("wait", 1500), ("face", "self", "shop_sign"),
                   ("emote", "self", "point"), ("wait", 2000), ("emote", "self", "cheer"), ("wait", 2000),
                   ("move", "self", "pip_wall", "run")],
         poi=["barrel", "shop_door"]),

    # 6.08: the shop window
    dict(key="ch6_window", title="The Shop Window", giver="pip", ender="pip", level=34, xp=8, tone="serious",
         prev="ch6_hide", explore="shop_door", radius=4,
         goal="Look in through the shell shop's door, on the canal basin's north shore.",
         text="That's it. Mister Ashcombe's shop. He's nice. He's nice to everyone, he gives me sweets. But he won't let your "
              "friend go. I asked. Go and look. Be quiet.",
         progress="Did you see him? Is he all right?",
         reward="He saw you. He was so happy... and so sad. We have to get him out. We have to.",
         details=["point", "shy"], reward_emotes=["cry", "yes"],
         accept=[("face", "self", "shop_door"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "shy"),
                 ("wait", 1500), ("face", "self", "player")],
         complete=[("emote", "self", "cry"), ("sound", "self", 11818), ("wait", 2500), ("emote", "self", "yes"),
                   ("wait", 1000), ("emote", "self", "flex")],
         poi=["shop_door"]),

    # 6.09: the keeper's key
    dict(key="ch6_key", title="The Keeper's Key", giver="pip", ender="pip", level=35, xp=8, tone="serious",
         prev="ch6_window", rep=[(72, -100)], items=[("shop_key", 1)],
         goal="Take the Shop Key from Ambrose Ashcombe's coat while he dozes on his bench at the canal's quiet south-east end.",
         text="Every day after lunch he sits on his bench by the water and falls asleep. Snore, snore. The key's in his coat. "
              "I'll keep watch. I'm a good watcher. I'll whistle if anyone comes.",
         progress="Got it? Got it?",
         reward="You got it! I whistled. Did you hear me whistle? ...I'm not very good at whistling.",
         details=["talk", "point"], reward_emotes=["applaud", "laugh"],
         accept=[("emote", "self", "beg"), ("wait", 1500), ("state", "self", "sleep"), ("visual", "self", 6431),
                 ("wait", 3000), ("state", "self", "none"), ("face", "self", "bench"), ("emote", "self", "point"),
                 ("wait", 1500), ("sound", "self", 7968), ("emote", "self", "laugh"), ("wait", 1500), ("face", "self", "player")],
         complete=[("sound", "self", 7968), ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", 11821),
                   ("wait", 1000), ("emote", "self", "applaud")],
         poi=["bench"]),

    # 6.10: night of the murloc (the heist)
    dict(key="ch6_heist", title="Night of the Murloc", giver="pip", ender="ch1:blrrgl", level=35, xp=8, tone="serious",
         path="hero", prev="ch6_key", time=180, objects=[("tank", 1)], explore="sluice_land", radius=8,
         goal="When Pip rings the bell, slip into the shell shop, break Sloshy's tank, and take him along the canal to "
              "Blrrgl at the sluice, the north arm's end, before the patrol comes round. You have 3 minutes.",
         text="Tonight. When the bell rings, the patrol walks to the far end to see why. That's me, ringing it! Then you "
              "have... 3 minutes? Maybe 3. Get him out and run to your green friend at the sluice. Ready? Ready!",
         progress="Where? Where is he? Is that him?",
         reward="Sloshy! SLOSHY! Look at him, fat as a pearl! Come, come, little one... Blrrgl takes you home. The long way. "
                "The safe way.",
         details=["yes", "point"], reward_emotes=["cheer", "cry"],
         choice=["road_slippers", "road_treads", "road_sabatons"],
         accept=[("emote", "self", "yes"), ("summon", "patrol", "patrol_north", 45), ("wait", 600),
                 ("move", "self", "bell", "run"), ("wait", 17000), ("face", "self", "bell"), ("emote", "self", "attack"),
                 ("sound", "self", 6555), ("wait", 1200), ("emote", "self", "attack"), ("sound", "self", 6555), ("wait", 1200),
                 ("emote", "self", "attack"), ("sound", "self", 6555), ("move", "patrol", "bell", "walk"),
                 ("sound", "patrol", 5973), ("wait", 3000), ("move", "self", "grate_out", "run"), ("wait", 20000),
                 ("move", "self", "pip_corner", "run")],
         complete=[("emote", "self", "cheer"), ("sound", "self", "murloc_fidget"), ("emote", "sloshy_free", "dance"),
                   ("sound", "sloshy_free", "baby_murloc"), ("music", 6837), ("wait", 3000), ("emote", "self", "cry"),
                   ("move", "sloshy_free", "sluice_water", "run"), ("wait", 2500), ("sound", "sloshy_free", "splash"),
                   ("despawn", "sloshy_free")],
         poi=["tank", "sluice_land"]),

    # 6.11a: free the curiosities (hero) and 6.11b: everything not nailed down (menace): while you're inside
    dict(key="ch6_free", title="Free the Curiosities", giver="pip", ender="pip", level=35, xp=8, tone="funny", path="hero",
         prev="ch6_key", exclusive=61, rep=[(72, 250)],
         objects=[("cage_parrot", 1), ("cage_croc", 1), ("cage_fireflies", 1), ("cage_tortoise", 1)],
         goal="While you're inside the shell shop, open the 4 cages: the parrot, the baby crocolisk, the jar of fireflies "
              "and the very old tortoise.",
         text="If you go in... the others too? There's a bird that says rude things, and a baby crocodile, and fireflies "
              "in a jar, and a really old tortoise. They're sad. Everyone in there is sad. Let them out too. All 4!",
         progress="Are they out? Did the bird say the rude word?",
         reward="They're free! The bird flew right over the guard's head! The fireflies are all over the canal now, it's "
                "like stars fell in. Thank you, thank you!",
         details=["talk", "point"], reward_emotes=["applaud", "cheer"], rewards=["firefly_jar"],
         accept=[("emote", "self", "talk"), ("wait", 1200), ("emote", "self", "talk"), ("wait", 1200),
                 ("face", "self", "shop_door"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "cheer"),
                 ("face", "self", "player")],
         complete=[("emote", "self", "applaud"), ("sound", "self", 11821), ("wait", 1500), ("emote", "self", "cheer")],
         poi=["cage_1"]),
    dict(key="ch6_loot", title="Everything Not Nailed Down", giver="ch1:blrrgl", ender="ch1:blrrgl", level=35, xp=8,
         tone="funny", path="menace", prev="ch6_key", exclusive=61, rep=[(72, -500)], items=[("curio", 6)],
         goal="While you're inside the shell shop, take 6 Dusty Curios worth something from its shelves.",
         text="A shop. A shop full of shinies, and the old one asleep upstairs, and nobody counting. Nobody! 6 shinies. "
              "Small ones. Shiny ones. The log is so empty here... so empty.",
         progress="More! There was a brass thing! I saw a brass thing!",
         reward="Ooooh. Ooh. Look at it all. Into the bag... the bag is heavy... the bag is wonderful.",
         details=["beg", "laugh"], reward_emotes=["laugh", "beg"], rewards=["spyglass"],
         accept=[("face", "self", "sluice_water"), ("wait", 900), ("face", "self", "sluice_land"), ("wait", 900),
                 ("emote", "self", "beg"), ("sound", "self", "murloc_fidget"), ("wait", 1500), ("emote", "self", "point"),
                 ("wait", 1200), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2")],
         complete=[("emote", "self", "laugh"), ("sound", "self", 120), ("wait", 1500), ("emote", "self", "beg"),
                   ("wait", 1000), ("emote", "self", "cheer")],
         poi=["curio_2"]),

    # 6.12: Pip is missing
    dict(key="ch6_missing", title="Pip Is Missing", giver="ch1:blrrgl", ender="pip", level=35, xp=8, tone="serious",
         path="hero", prev="ch6_heist", interact=[("pip", "Pull the grate.")], interact_goal="Pip pulled out of the grate",
         interact_beats=[("sound", "self", 16465), ("wait", 800), ("jump", "self", "grate_out"), ("wait", 1500),
                         ("emote", "self", "cry"), ("sound", "self", 11818), ("wait", 2500), ("emote", "self", "cheer"),
                         ("wait", 30000), ("jump", "self", "pip_stuck")],
         goal="Pip didn't come home after ringing the bell. Follow the drain grates at the canal's south-east end, past his "
              "rod on the wall, and pull him out of the one he's stuck in.",
         text="The little dry-skin. His stick, his fishing stick... it's lying on the wall at the far end. He didn't come back. "
              "Dry-skins don't swim. Do they? Do they swim? Go! Go and look!",
         progress="Help... help me...",
         reward="I fell in! I fell in and the grate caught my trousers and the water came up and... you came. "
                "You came back for me.",
         details=["exclamation", "point"], reward_emotes=["cry", "cheer"],
         accept=[("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 1500),
                 ("face", "self", "pip_rod"), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "cry"),
                 ("sound", "self", "murloc_fidget2")],
         complete=[("emote", "self", "cry"), ("sound", "self", 11818), ("wait", 2500), ("emote", "self", "talk"),
                   ("wait", 1500), ("emote", "self", "cheer")],
         poi=["pip_stuck"]),

    # 6.13: Sergeant Hadley (a set piece)
    dict(key="ch6_hadley", title="Sergeant Hadley", giver="pip", ender="hadley", level=35, xp=8, tone="serious", path="hero",
         prev="ch6_missing", rep=[(72, 1000)], escort=("pip", ["grate_out", "hadley_door"]), radius=8,
         goal="Walk Pip home to his door on the street by the canal's north arm, near the sluice.",
         text="Will you walk me home? Papa will be so worried. He's a guard. A sergeant! Don't be scared of him. "
              "I'll tell him. I'll tell him everything.",
         progress="Pip? Pip, is that you?",
         reward="Pip... Pip, come here. Behind me. No? ...He says you pulled him out of the water. Light help me. "
                "Go on, little one. Go home, before I remember what I am.",
         details=["wave", "talk"], reward_emotes=["kneel", "talk"],
         choice=["watch_gloves", "lamplighter_grips", "sergeant_gauntlets"],
         accept=[("emote", "self", "wave"), ("sound", "self", 11821), ("wait", 1500), ("face", "self", "hadley_door"),
                 ("emote", "self", "point")],
         complete=[("sound", "self", 8015), ("face", "self", "player"), ("sound", "self", 700), ("state", "self", 333),
                   ("yell", "self", "Pip! Get away from that thing!", "shout", 5973), ("wait", 1500),
                   ("move", "pip", "pip_between", "run"), ("wait", 1500),
                   ("yell", "pip", "No! Papa, no! He saved me! He pulled me out!", "exclamation", 11818),
                   ("wait", 5000), ("emote", "pip", "beg"), ("wait", 3000), ("state", "self", "none"), ("wait", 2500),
                   ("state", "self", "kneel"), ("music", 4517), ("wait", 2500), ("emote", "self", "talk"), ("wait", 6000),
                   ("emote", "pip", "cheer"), ("sound", "pip", 11821), ("wait", 6000), ("state", "self", "none"),
                   ("move", "pip", "pip_home", "walk")],
         poi=["hadley_door"]),

    # 6.14: Sloshy comes home (a set piece)
    dict(key="ch6_home", title="Sloshy Comes Home", giver="sloshy_mouth", ender="ch1:murlorga", level=35, xp=8,
         tone="serious", prev="ch6_heist", escort=("sloshy_mouth", ["mouth", "murlorga"]), radius=6,
         goal="Walk Sloshy from the grotto's mouth to Murlorga at her cook-pot. He won't go in without you.",
         text="You came! Blrrgl brought me, but... but I want YOU to bring me. Hold my fin. Is Murlorga there? Is she cross? "
              "Is there soup?",
         progress="Who's there? Who's that behind you?",
         reward="Sloshy... SLOSHY! Let me look at you. You're fat! They fed you! Who said you could be fat without me? "
                "Come here, come here, come here. And look! The coat! The dry-skin's little coat! It fits!",
         details=["cheer", "shy"], reward_emotes=["cry", "cheer", "kiss"], rewards=["sloshy_ring"],
         accept=[("emote", "self", "cheer"), ("sound", "self", "baby_murloc"), ("wait", 1500), ("emote", "self", "shy")],
         complete=[("state", "self", "none"), ("sound", "self", 973), ("object", "dropped_ladle", "murlorga_feet", 40),
                   ("emote", "self", "exclamation"), ("wait", 1500), ("emote", "self", "cheer"), ("sound", "self", "murloc_aggro"),
                   ("emote", "ch1:grrmlgrrl", "cheer"), ("emote", "ch1:glubbub", "cheer"), ("emote", "ch1:blrrgl", "cheer"),
                   ("emote", "ch0:mrrk", "cheer"), ("sound", "ch1:blrrgl", "murloc_aggro"), ("sound", "ch1:grrmlgrrl", 15995),
                   ("move", "sloshy_mouth", "mouth", "walk"), ("object", "tiny_coat", "sloshy_home", 60),
                   ("emote", "ch1:sloshy", "dance"), ("sound", "ch1:sloshy", "baby_murloc_dance"), ("music", 4454),
                   ("wait", 3000), ("emote", "ch1:elder", "attack"), ("sound", "ch1:elder", 977), ("wait", 700),
                   ("emote", "ch1:elder", "attack"), ("sound", "ch1:elder", 977), ("wait", 700),
                   ("emote", "ch1:elder", "attack"), ("sound", "ch1:elder", 977), ("wait", 1500),
                   ("emote", "ch1:grrmlgrrl", "attack"), ("emote", "ch1:glubbub", "attack"), ("emote", "ch1:blrrgl", "attack"),
                   ("emote", "ch0:mrrk", "attack"), ("emote", "ch0:krrgl", "attack"), ("sound", "ch1:glubbub", 977),
                   ("sound", "ch1:grrmlgrrl", 977), ("wait", 700), ("emote", "ch1:grrmlgrrl", "attack"),
                   ("emote", "ch1:glubbub", "attack"), ("emote", "ch1:blrrgl", "attack"), ("emote", "self", "attack"),
                   ("sound", "ch1:blrrgl", 977), ("sound", "self", 977), ("wait", 700), ("emote", "ch1:grrmlgrrl", "attack"),
                   ("emote", "ch1:glubbub", "attack"), ("emote", "self", "attack"), ("sound", "ch0:mrrk", 977),
                   ("sound", "self", 977), ("wait", 2000), ("emote", "self", "kiss"), ("wait", 2000),
                   ("emote", "ch1:sloshy", "dance"), ("wait", 4000), ("face", "self", "cookpot"), ("state", "self", "work")],
         poi=["mouth", "murlorga"]),

    # 6.15: Murk-Eye's old spear
    dict(key="ch6_spear", title="Murk-Eye's Old Spear", giver="ch0:murkeye", ender="ch0:murkeye", level=34, xp=8,
         tone="serious", prev="ch6_arrows", items=[("old_spear", 1)],
         goal="Bring up Murk-Eye's Old Spear from the sunken ship off the coast to the north, in the Tidehunters' water.",
         text="Before I hid, I fought. Once. A ship came, full of shouting. It sank. I won. My spear stayed in it... down "
              "there, to the north, with the shouting ones' bones. Bring it. I want to hold it one more time.",
         progress="My hand remembers it. Hurry, before my hand forgets.",
         reward="There... there it is. Hm. Heavier than I remember. Or I am weaker. ...Take it. It should hit things again. "
                "I am done hitting things.",
         details=["talk", "point"], reward_emotes=["talk", "bow"],
         choice=["murkeye_spear", "murkeye_tooth", "murkeye_staff"],
         accept=[("state", "self", "none"), ("emote", "self", "kneel"), ("object", "sand_ship", "sand_1", 40),
                 ("sound", "self", 1194), ("wait", 2500), ("emote", "self", "kneel"), ("object", "sand_spear", "sand_2", 40),
                 ("wait", 2500), ("emote", "self", "beg"), ("sound", "self", "murloc_fidget2"), ("wait", 2000),
                 ("face", "self", "wreck"), ("emote", "self", "point"), ("wait", 2000), ("face", "self", "inlet"),
                 ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("object", "sand_spear", "sand_1", 15), ("emote", "self", "flex"),
                   ("sound", "self", "murloc_aggro_old"), ("wait", 2500), ("emote", "self", "shy"), ("wait", 2000),
                   ("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"), ("wait", 2500), ("state", "self", "sit")],
         poi=["wreck"]),

    # 6.16: Murk-Eye's bath
    dict(key="ch6_bath", title="Murk-Eye's Bath", giver="ch1:murlorga", ender="ch0:murkeye", level=34, xp=8, tone="stupid",
         prev="ch6_helmets", source="stew_bucket", use=[("stew_bucket", "ch0:murkeye", 1)],
         goal="Take Murlorga's Bucket of Westfall Stew to Old Murk-Eye at his throne and scrub his back with it.",
         text="He asked for a bath. In stew. STEW! The dry-skins' brown stew, from the farm pots up the hill. I made it anyway. "
              "Don't tell me why he wants it. Don't tell me anything. Take it.",
         progress="Mm? Stew?",
         reward="Mmmmmrrrrrrgl... Lower. Lower. Ahhhh. Now I smell like a farmer's supper. Every crab on the coast will love me.",
         details=["no", "rude"], reward_emotes=["eat", "beg"], rewards=["grotto_stew"],
         accept=[("state", "self", "none"), ("emote", "self", "no"), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("emote", "self", "rude"), ("wait", 1500), ("emote", "self", "talk"), ("sound", "self", 973), ("wait", 1500),
                 ("face", "self", "cookpot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("sound", "self", 1197), ("sound", "self", "murloc_fidget"), ("wait", 1500),
                   ("emote", "self", "work"), ("sound", "self", 414), ("wait", 2000), ("emote", "self", "dance"),
                   ("sound", "self", 414), ("wait", 2500), ("emote", "self", "beg"), ("wait", 2000), ("state", "self", "sit")],
         poi=["murkeye"]),

    # 6.17: touch the lion (Mrrk's dare)
    dict(key="ch6_lion", title="Touch the Lion", giver="ch0:mrrk", ender="ch0:mrrk", level=35, xp=8, tone="stupid",
         prev="ch6_harbor", explore="lion", radius=4,
         goal="Touch the stone lion on the road up from Stormwind Harbor, under the guards' noses, and get back to Mrrk "
              "Sharpfin at the grotto.",
         text="You think you're brave. You think you're the Tidehunter's favourite. The stone men have a stone cat on their "
              "harbour road. Big. Teeth. Touch its nose and come back. I did it. Twice. ...Once.",
         progress="Scared? Hah. Scared.",
         reward="You... touched it? With the guards right there? Hmph. Lucky. That was lucky. I'm still better.",
         details=["point", "chicken"], reward_emotes=["no", "flex"], rewards=["mrrk_tooth"],
         accept=[("face", "self", "north"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "roar"),
                 ("sound", "self", "murloc_aggro"), ("wait", 1500), ("emote", "self", "rude"), ("wait", 1000),
                 ("move", "self", "mrrk_run", "run"), ("wait", 3000), ("move", "self", "mrrk", "run"), ("wait", 3000),
                 ("face", "self", "player"), ("emote", "self", "laugh"), ("wait", 1200), ("emote", "self", "chicken"),
                 ("sound", "self", "murloc_fidget")],
         complete=[("emote", "self", "no"), ("wait", 1500), ("emote", "self", "flex"), ("sound", "self", "murloc_fidget2"),
                   ("wait", 1500), ("emote", "self", "laugh")],
         poi=["lion"]),

    # 6.18: the sergeant looks away
    dict(key="ch6_look", title="The Sergeant Looks Away", giver="hadley", ender="hadley", level=36, xp=8, tone="serious",
         path="hero", prev="ch6_hadley", rep=[(72, 250)],
         goal="Meet Sergeant Hadley on the pier in Stormwind Harbor where the Theramore ship is loading.",
         text="Pip says your people need a way out of the city. A ship sails for Theramore at dawn: all crates and no "
              "questions. I'll be on the pier. I'll be looking at the sky. A man can't see what he isn't looking at.",
         reward="There's the ship. There's a crate. I see neither. Lovely clouds tonight.",
         details=["talk", "point"], reward_emotes=["point", "talk"], rewards=["sergeant_cloak"],
         accept=[("emote", "self", "talk"), ("wait", 1500), ("emote", "self", "point"), ("wait", 1500),
                 ("emote", "self", "yes"), ("emote", "pip", "wave"), ("sound", "pip", 11821)],
         complete=[("face", "self", "ship"), ("emote", "self", "point"), ("wait", 2000),
                   ("object", "lid_off", "pier_open", 40), ("face", "self", "pier_open"), ("emote", "self", "point"),
                   ("wait", 2500), ("face", "self", "sky"), ("sound", "self", 7914), ("wait", 20000), ("face", "self", "ship")],
         poi=["pier_hadley"]),

    # 6.19: stowaways (the chapter's end: in a crate on a Theramore ship)
    dict(key="ch6_end", title="Stowaways", giver="ch1:elder", ender="ch1:blrrgl", level=36, xp=8, tone="funny",
         prev=["ch6_look", "ch6_home"], objects=[("crate_open", 1)],
         goal="Climb into the open crate on the Theramore ship's pier in Stormwind Harbor, then tell Blrrgl, hiding by the "
              "crates, that you're in.",
         text="The turtle swims slowly, and the clutch's road goes south, to the marsh where the little king sits on his fish. "
              "Shellback takes the tribe. You and Blrrgl take the fast way: a box on a dry-skin ship. Into the box. "
              "Be cargo. Be quiet cargo.",
         progress="In the box? Are you in the box? I'm in my box. ...I don't like my box.",
         reward="Lid on. Lid on! It's dark. It's moving. Oh. Oh no. It's moving...",
         details=["talk", "point"], reward_emotes=["cry", "talk"],
         choice=["stowaway_robe", "stowaway_jerkin", "stowaway_hauberk"],
         accept=TAP + [("wait", 1500), ("face", "self", "north"), ("emote", "self", "point"), ("wait", 1500),
                       ("emote", "self", "work"), ("emote", "ch1:murlorga", "cry"), ("sound", "ch1:murlorga", "murloc_fidget2"),
                       ("wait", 1500), ("face", "self", "hub")],
         complete=[("aura", "self", "crated"), ("aura", "player", "crated"), ("sound", "self", 8016), ("wait", 1500),
                   ("sound", "self", 9054), ("sound", "self", 4216), ("wait", 2500), ("music", 11805), ("wait", 3000),
                   ("sound", "self", "murloc_wound"), ("wait", 2500), ("sound", "self", 9054), ("wait", 1500),
                   ("sound", "self", "murloc_wound_crit"), ("wait", 3000), ("visual", "player", 36005),
                   ("teleport", "player", "ch7:hub", 0.0)],
         poi=["pier_open"]),
]
