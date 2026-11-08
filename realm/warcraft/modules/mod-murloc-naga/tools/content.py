"""What the Murlocs' and the Naga's first starts held: their people, things and quests, in Darkshore
(map 1). tools/build_data.py places them (each on the ground the server's maps give, or where a
creature of the game's stands) and writes their SQL.

Both are retired, kept here for the record and for their ids (still taken: what came after them keeps
its ids): the murlocs' village on the island west of Auberdine (their story starts in the Wrathtail's
pens: tools/murloc/) and the renegade naga's camp on the island north of it, with its five quests (the
naga's story starts at Rethress Sanctum in Azshara: tools/naga/). Lady Szaria, Myrmidon Ssaveth and Vyssa
the Coral-Keeper keep their creature entries (975017 to 975019) as the naga's story's people
(tools/naga/ch0_*.py: tools/murloc/profiles.py's KEPT_ENTRIES).

The murlocs speak murloc. What they want is shown, not told: what they do as they speak (in
brackets), never what they mean. The naga, the night elves and the trolls speak plainly.

Positions are (x, y) on the ground, (x, y, z) where the ground isn't the map's (a building's
floor, a dock), or "water" (the sea floor) for things under the sea."""

MAP, DARKSHORE, ASHENVALE = 1, 148, 331
MURLOC, NAGA = 19, 20
PHASE = {MURLOC: 1024, NAGA: 2048}             # their own phases (and the world's, 1, as well)

# Ids: creatures, objects, quests, items and texts 975000 to 975999; spawns 9750000 on.
NPC_BASE, GO_BASE, QUEST_BASE, ITEM_BASE, TEXT_BASE = 975000, 975100, 975200, 975300, 975400
SPAWN_BASE, GO_SPAWN_BASE = 9750000, 9751000

# Creatures of the game's, by entry: their fights are the quests' (no change to them, but a quest
# item they drop for those on the quest).
PYGMY_TIDE_CRAWLER, DARKSHORE_THRESHER = 2231, 2185
WRATHTAIL_MYRMIDON, WRATHTAIL_RAZORTAIL = 3711, 3712
THUNDRIS_WINDWEAVER, GLYNDA_NALSHEA, ONU, MARUKAI = 3649, 2930, 3616, 12719
NAGA_AT_THE_ZORAM_STRAND = 6442                # Marukai's (Zoram'gar), the Horde's own
RETURN_TO_ONU = 950

# The game's looks (CreatureDisplayInfo) the people wear.
LOOK = {
    "oracle": 4920, "tidehunter": 478, "seer": 3940, "coastrunner": 3619, "netter": 2597,
    "warrior": 540, "hunter": 652, "raider": 346, "flagglemurk": 1305, "murkdeep": 1079,
    "fry_green": 15394, "fry_blue": 15393, "fry_pink": 15396, "fry_purple": 15397,
    "naga_male": 4036, "siren": 4980, "sorceress": 4973, "naga_warrior": 11269,
    "naga_lord": 4762, "sea_witch": 4981, "myrmidon": 6747, "troll_scout": 31737,
}

# --------------------------------------------------------------------------------------------
# The murlocs' village
# --------------------------------------------------------------------------------------------
VILLAGE = (6255, 965)
# (key, name, subname, look, (x, y), facing, role): role "quest", "vendor", "ambient" or "fry".
MURLOC_PEOPLE = [
    ("elder", "Elder Mrrglmrgl", "Village Elder", "oracle", (6252, 968), 4.71, "quest"),
    ("chief", "Grrmlgrrl the Tidehunter", None, "tidehunter", (6240, 976), 5.2, "quest"),
    ("cook", "Murlorga", "Village Cook", "seer", (6263, 981), 4.1, "quest"),
    ("snatcher", "Blrrgl the Snatcher", None, "coastrunner", (6278, 958), 4.71, "quest"),
    ("oracle", "Oracle Glubbub", None, "murkdeep", (6246, 952), 0.4, "quest"),
    ("fishmonger", "Mrrlglr", "Fishmonger", "netter", (6268, 970), 3.6, "vendor"),
    ("villager1", "Murloc Villager", None, "warrior", (6236, 965), 1.5, "ambient"),
    ("villager2", "Murloc Villager", None, "hunter", (6258, 988), 3.0, "ambient"),
    ("villager3", "Murloc Villager", None, "raider", (6271, 975), 2.2, "ambient"),
    ("villager4", "Murloc Villager", None, "netter", (6244, 984), 5.5, "ambient"),
    ("fry1", "Murloc Fry", None, "fry_blue", (6256, 975), 0.0, "fry"),
    ("fry2", "Murloc Fry", None, "fry_pink", (6249, 962), 0.0, "fry"),
    ("fry3", "Murloc Fry", None, "fry_purple", (6265, 962), 0.0, "fry"),
]
# The baby who wanders off: under Auberdine's dock, by the beach (Gubber Blump fishes there).
SLOSHY = ("sloshy", "Sloshy", None, "fry_green", (6331.0, 589.0, 0.9), 2.4, "quest")

# The things of the village: (game model, name, (x, y), facing, scale).
MURLOC_THINGS = [
    ("World\\AZEROTH\\SWAMPOSORROW\\PASSIVEDOODADS\\WATERHUTS\\WaterHut01.mdx", "Murloc Hut", (6247, 991), 0.3, 1.0),
    ("World\\AZEROTH\\SWAMPOSORROW\\PASSIVEDOODADS\\WATERHUTS\\WaterHut02.mdx", "Murloc Hut", (6266, 994), 5.9, 1.0),
    ("World\\AZEROTH\\SWAMPOSORROW\\PASSIVEDOODADS\\WATERHUTS\\WaterHut01.mdx", "Murloc Hut", (6229, 974), 1.1, 0.9),
    ("World\\AZEROTH\\SWAMPOSORROW\\PASSIVEDOODADS\\WATERHUTS\\WaterHut02.mdx", "Murloc Hut", (6283, 978), 4.9, 0.9),
    ("World\\GENERIC\\Murloc\\Passive Doodads\\Pearl\\GreatPearl_01.mdx", "Great Pearl", (6241, 949), 0.0, 1.0),
]
ALTAR = ("World\\GENERIC\\Murloc\\Passive Doodads\\Altars\\MurlocAltar_01.mdx", "Murloc Altar", (6249, 956), 1.2, 1.0)

# The naga raiders' island, south of the village, and their leader.
RAIDERS = [(5915, 765), (5926, 779), (5930, 762), (5912, 776), (5921, 788), (5935, 771), (5918, 755), (5928, 790),
           (5910, 783), (5938, 780), (5923, 770), (5913, 760)]
SSSILITH = (5924, 773)
# Crawlers on the village's beaches (the game's Pygmy Tide Crawlers, in the murlocs' phase).
CRAWLERS = [(6232, 945), (6228, 990), (6290, 960), (6284, 940), (6222, 965), (6270, 1000), (6295, 975), (6236, 1001)]

# What the murlocs steal in Auberdine, where it stands (on the ground, by the town's people).
TRINKET_CRATES = [(6375.0, 572.5, 0.3), (6399.5, 497.0, 8.1), (6431.5, 493.5, 8.0), (6516.5, 466.0, 7.2),
                  (6541.0, 446.0, 7.5), (6504.0, 484.5, 6.8), (6423.5, 485.0, 7.9), (6531.0, 435.0, 7.4)]
BREAD_BASKETS = [(6410.5, 525.0, 8.7), (6402.5, 509.5, 8.7), (6419.0, 521.0, 8.7), (6412.5, 512.0, 8.7), (6404.0, 527.5, 8.7)]
LURE_BOX = (6368.0, 580.5, 0.2)

# --------------------------------------------------------------------------------------------
# The renegade naga's camp
# --------------------------------------------------------------------------------------------
CAMP = (6705, 800)
NAGA_PEOPLE = [
    ("szaria", "Lady Szaria", "The Tide-Broken", "siren", (6705, 801), 4.71, "quest"),
    ("ssaveth", "Myrmidon Ssaveth", None, "naga_warrior", (6713, 793), 4.3, "ambient"),
    ("vyssa", "Vyssa the Coral-Keeper", "Provisions", "sorceress", (6699, 809), 5.5, "vendor"),
    ("guard1", "Renegade Myrmidon", None, "naga_male", (6716, 806), 4.0, "ambient"),
    ("guard2", "Renegade Myrmidon", None, "naga_male", (6695, 792), 5.0, "ambient"),
    ("siren1", "Renegade Siren", None, "sea_witch", (6709, 812), 2.0, "ambient"),
]
NAGA_THINGS = [
    ("World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Pagoda\\NagaPagodaHut01.mdx", "Naga Pagoda", (6712, 812), 4.0, 0.8),
    ("World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Banner\\NA_Banner01.mdx", "Renegade Banner", (6700, 797), 4.71, 1.0),
    ("World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\TORCH\\NA_Torch01.mdx", "Naga Torch", (6710, 796), 0.0, 1.0),
    ("World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\TORCH\\NA_Torch01.mdx", "Naga Torch", (6698, 806), 0.0, 1.0),
    ("World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Crates\\NA_Crate01.mdx", "Naga Crate", (6702, 812), 1.0, 1.0),
    ("World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\WeaponStacks\\NA_WeaponStack01.mdx", "Naga Weapons", (6717, 799), 3.5, 1.0),
    ("World\\EXPANSION01\\DOODADS\\GENERIC\\NAGA\\Jars\\NA_Jar01.mdx", "Naga Jar", (6694, 802), 0.0, 1.0),
]
# The Stormscale who hunt them, on the island to the north.
INFILTRATORS = [(6975, 805), (6988, 815), (6970, 820), (6995, 800), (6982, 828), (6965, 810), (6998, 822), (6978, 795),
                (6990, 808), (6969, 828)]
# The Darkspear scout at the Zoram Strand (Ashenvale), on the beach north of the Wrathtail.
SCOUT = ("scout", "Scout Zun'jin", "Darkspear Trolls", "troll_scout", (4176, 880), 3.6, "quest")

# --------------------------------------------------------------------------------------------
# Quest items (class 12: (key, name, look, stack)) and rewards
# --------------------------------------------------------------------------------------------
ITEMS = [
    ("mussel", "Plump Mussel", 22193, 20),
    ("trinket", "Elven Trinket", 12410, 20),
    ("roll", "Auberdine Sweet Roll", 21203, 20),
    ("trident", "Sssilith's Trident", 8747, 1),
    ("kelp", "Fresh Kelp", 18089, 20),
    ("coral", "Glowing Coral", 6652, 20),
    ("lures", "Box of Shiny Lures", 7914, 1),
    ("pearl", "Glimmering Pearl", 12310, 1),
    ("orders", "Stormscale Orders", 3093, 20),
]
THRESHER_EYE = 5412                            # the game's own quest item (Thresher Eye)
# Rewards of the murlocs' rite and the naga's alliance: (key, name, look, inventory type, class,
# subclass, quality, level, stats [(type, value)], armour)
REWARDS = [
    ("pearl_charm", "Elder's Pearl Charm", 6539, 2, 4, 0, 2, 15, [(7, 3), (6, 2)], 0),
    ("kelp_wrap", "Murlorga's Kelp Wrap", 23108, 16, 4, 1, 2, 15, [(3, 2), (7, 2)], 12),
    ("tide_spear", "Tidehunter's Coral Spear", 8747, 17, 2, 6, 2, 15, [(4, 4), (7, 3)], 0),
    ("szaria_band", "Band of the Tide-Broken", 9835, 11, 4, 0, 2, 19, [(5, 3), (7, 3)], 0),
    ("darkspear_cloak", "Darkspear Scout's Cloak", 23025, 16, 4, 1, 2, 19, [(3, 3), (7, 3)], 15),
]

# --------------------------------------------------------------------------------------------
# Quests. Each: id offset, giver ("npc:<key>", "go:altar", or a creature entry), ender, level,
# min level, XP difficulty, title, objectives (kill [(entry or "npc:<key>", count)], items
# [(item, count)], explore "<key>"), the log's text, the giver's words, the words while
# unfinished, the ender's words, the quest before, reward items (choices), money, standing.
# --------------------------------------------------------------------------------------------
MURLOC_QUESTS = [
    dict(n=0, title="Mrrgl?", giver="npc:elder", ender="npc:chief", level=10, min=10, xp=2,
         log="Speak with Grrmlgrrl the Tidehunter.",
         text="Mrrgl? Mrgl mrrrgl...$B$B(The old murloc squints at you with one enormous eye, then pokes your belly with a webbed finger, twice.)$B$BMrgl! MRGLMRGL!$B$B(He points his staff at the broad murloc sharpening a spear beside the huts, and jabs the air.)",
         reward="Hrrmmgl.$B$B(The big murloc looks you up and down, unimpressed. He thumps his own chest twice, then yours once, much harder.)$B$BMrrrgllgh!"),
    dict(n=1, title="Snap Snap", giver="npc:chief", ender="npc:chief", level=10, min=10, xp=7, prev=0,
         log="Kill 10 Pygmy Tide Crawlers on the beaches of the island and around Auberdine.",
         kill=[(PYGMY_TIDE_CRAWLER, 10)],
         text="(Grrmlgrrl clacks two fingers together like pincers, then points at the little crabs scuttling along the sand. He lifts one foot high and brings it down with a squelch.)$B$BMrgl! Mrgl mrgl!$B$B(He pats his belly and looks at you hopefully.)",
         progress="(Grrmlgrrl holds up both hands and wiggles every finger. Then he points at the beach.)",
         reward="(Grrmlgrrl counts the cracked shells on his fingers, runs out of fingers, and gives up with a happy gurgle.)$B$BMrrrgl!"),
    dict(n=2, title="Mussel Memory", giver="npc:cook", ender="npc:cook", level=10, min=10, xp=7,
         log="Gather 8 Plump Mussels from the shallows around the island.",
         items=[("mussel", 8)],
         text="(Murlorga stirs a bubbling pot. She lifts the ladle, sniffs it, and lets out a long, sad, empty gurgle.)$B$BMrrrrgl...$B$B(She points at the shallow water around the island, then mimes prying something open with her claws and slurping it down.)",
         progress="(Murlorga taps the empty pot with her ladle. Tonk. Tonk.)",
         reward="(Murlorga tips the mussels into the pot, shells and all. The smell is indescribable. Every murloc in the village turns its head at once.)$B$BMrglmrglmrgl!"),
    dict(n=3, title="Shinies!", giver="npc:snatcher", ender="npc:snatcher", level=11, min=10, xp=7,
         log="Steal 6 Elven Trinkets from the crates of Auberdine, across the water.",
         items=[("trinket", 6)],
         text="(Blrrgl looks left. He looks right. He leans so close you can smell the fish on his breath.)$B$Bmrgl... mrgl mrgl...$B$B(He points across the water at the lights of the elven town, tiptoes in a little circle, then stuffs his cheeks with imaginary treasure and giggles wetly.)",
         progress="(Blrrgl rubs his fingers together, very fast.)",
         reward="(Blrrgl snatches the trinkets, holds each one up to his eye, and stuffs them into a hollow log already overflowing with spoons.)$B$BMrrgl mrgl!"),
    dict(n=4, title="The Sweetest Bread", giver="npc:snatcher", ender="npc:snatcher", level=11, min=10, xp=7, prev=3,
         log="Steal 5 Auberdine Sweet Rolls from the baskets by the inn.",
         items=[("roll", 5)],
         text="(Blrrgl mimes taking a bite of something round. His eyes roll back. He sways. Then he points at the great tree where the elves sleep, and a long string of drool reaches the sand.)$B$BMrgl... mrrrrgl...",
         progress="(Blrrgl pats his stomach and makes a small, pitiful noise.)",
         reward="(Blrrgl eats the first roll in one bite. He eats the second in one bite. He hides the other three under his fins and looks at you as if nothing happened.)"),
    dict(n=5, title="Scales in the Water", giver="npc:chief", ender="npc:chief", level=12, min=10, xp=7, prev=1,
         log="Kill 10 Stormscale Raiders on the island to the south.",
         kill=[("npc:raider", 10)],
         text="(Grrmlgrrl's fins flatten against his head. He points south, at the next island, then drags his spear through the sand in a long, slithering line, and stabs it. Again. Again.)$B$BMRRRGL! MRGL MRGL!$B$B(Behind you, the villagers duck into their huts.)",
         progress="(Grrmlgrrl draws another slithering line in the sand. It isn't stabbed yet.)",
         reward="(Grrmlgrrl stamps the slithering lines flat, one by one, and roars until a fry runs to hide behind Murlorga.)$B$BMrglmrgl!"),
    dict(n=6, title="The Tidecaller", giver="npc:chief", ender="npc:chief", level=13, min=11, xp=8, prev=5,
         log="Bring Sssilith's Trident to Grrmlgrrl the Tidehunter.",
         items=[("trident", 1)],
         text="(Grrmlgrrl draws a bigger slithering line, and gives it a crown of spikes. He snaps his own spear in two over his knee, hands you the sharp end, and points south.)$B$BMrgl.",
         progress="(Grrmlgrrl stares at your empty hands, then at the island to the south.)",
         reward="(Grrmlgrrl takes the trident in both hands and holds it over his head. The whole village gurgles at once, louder and louder, until he bangs it on the ground and they stop.)$B$B(He gives you a long look, and nods once.)",
         rewards=["tide_spear"]),
    dict(n=7, title="Kelp Wraps", giver="npc:cook", ender="npc:cook", level=11, min=10, xp=7, prev=2,
         log="Gather 6 Fresh Kelp from the sea floor around the island.",
         items=[("kelp", 6)],
         text="(Murlorga holds up a mussel and wraps an invisible leaf around it, very carefully. She bites it. She frowns. She points at the water and pulls an invisible something up out of it, hand over hand.)$B$BMrgl mrgl.",
         progress="(Murlorga holds up the unwrapped mussel and shakes her head.)",
         reward="(Murlorga wraps each mussel in kelp and lays them in a row. Then she wraps one more and gives it to you, and watches until you eat it.)",
         rewards=["kelp_wrap"]),
    dict(n=8, title="Where's Sloshy?", giver="npc:cook", ender="npc:sloshy", level=11, min=10, xp=3, prev=2,
         log="Find Sloshy.",
         text="(Murlorga counts the fry around her legs. One, two, three. She counts again. One, two, three. She spins around and gives a piercing shriek that sends every bird on the island into the air.)$B$BSLOSHY! MRRRRGL!$B$B(She points across the water, toward the elves' docks, and covers her eyes.)",
         reward="(A small green murloc peers out from under the dock, sees you, and bursts into tears of relief. Or the sea. It's hard to tell with murlocs.)$B$Bmrgl? mrgl mrgl!"),
    dict(n=9, title="Sloshy Goes Home", giver="npc:sloshy", ender="npc:cook", level=11, min=10, xp=5, prev=8,
         log="Take Sloshy home to Murlorga.",
         text="(Sloshy wraps both arms around your leg and won't let go. He points at the island, then at you, then at the island again, and wails.)",
         progress="(Sloshy is still holding on to your leg.)",
         reward="(Murlorga scoops Sloshy up, scolds him in a long, furious gurgle, then hugs him so hard he squeaks. Over his head, she looks at you, and her eyes are wet.)$B$BMrgl."),
    dict(n=10, title="Glow of the Deep", giver="npc:oracle", ender="npc:oracle", level=11, min=10, xp=7,
         log="Gather 6 Glowing Coral from the sea floor around the island.",
         items=[("coral", 6)],
         text="(Oracle Glubbub cups his hands together, slowly opens them, and stares into them as if they held a light. They don't. He points down, into the sea.)$B$BMmmrrrglll...",
         progress="(Oracle Glubbub's hands are still cupped, still empty.)",
         reward="(Oracle Glubbub lays the coral in a circle around himself and sits in the middle of it, humming a low, bubbling hum. The coral pulses with him.)"),
    dict(n=11, title="Eyes of the Thresher", giver="npc:oracle", ender="npc:oracle", level=12, min=10, xp=7, prev=10,
         log="Bring 6 Thresher Eyes to Oracle Glubbub. The threshers swim in the deep water off Darkshore's coast.",
         items=[(THRESHER_EYE, 6)],
         text="(Oracle Glubbub taps one of his own eyes, then the other. He makes a fish of his hand and swims it through the air, mouth open, until it bites your arm.)$B$BMrgl!",
         progress="(Oracle Glubbub taps his eye again and waits.)",
         reward="(Oracle Glubbub drops the eyes into the coral circle, one by one. He stares into them for a long time. Then he looks up at you, very differently than before.)"),
    dict(n=12, title="Gubber's Lures", giver="npc:snatcher", ender="npc:snatcher", level=12, min=10, xp=7, prev=4,
         log="Steal the Box of Shiny Lures from Gubber Blump's dock in Auberdine.",
         items=[("lures", 1)],
         text="(Blrrgl mimes a short, round fellow casting a line. He mimes the line jerking. He mimes the short, round fellow celebrating. Then he mimes himself, the fish on the hook, outraged.)$B$B(He points at the dock, and rubs his hands together.)",
         progress="(Blrrgl looks at the dock, then at you, then at the dock.)",
         reward="(Blrrgl opens the box. The lures shine. Blrrgl shines. He hangs every single one of them from his fins and jingles away down the beach.)"),
    dict(n=13, title="A Gift from the Deep", giver="npc:elder", ender="npc:elder", level=12, min=11, xp=7, prev=6,
         log="Find the Glimmering Pearl in the giant clam deep off the island's western shore.",
         items=[("pearl", 1)],
         text="(Elder Mrrglmrgl draws a circle in the air, very round, very carefully. He points west, out to sea, and then down, and down, and down.)$B$BMrrrglll...$B$B(He holds his breath until his cheeks bulge, and lets it out with a gasp.)",
         progress="(Elder Mrrglmrgl draws the circle in the air again, slower.)",
         reward="(Elder Mrrglmrgl turns the pearl over and over in his hands. Then he gives it back to you, and closes your fingers around it.)"),
    dict(n=14, title="The Oracle's Vision", giver="npc:oracle", ender="npc:oracle", level=12, min=11, xp=7, prev=11,
         log="Climb to the top of the island and look out over the sea.",
         explore="summit",
         text="(Oracle Glubbub puts a cold, wet hand over your eyes. When he takes it away, he points to the very top of the island, then sweeps his arm across the whole sea.)$B$BMrgl. Mrgl mrgl mrgl.",
         progress="(Oracle Glubbub points at the top of the island again.)",
         reward="(Oracle Glubbub listens as you gurgle what you saw: the elves' town, the slithering ones on their islands, the long coast to the south. He nods slowly, as if you told him something he already knew.)"),
    dict(n=15, title="The Rite of the Pearl", giver="npc:elder", ender="go:altar", level=13, min=11, xp=8, prev=13,
         log="Place the Glimmering Pearl on the Murloc Altar in the village.",
         items=[("pearl", 1)], source_item="pearl",
         text="(Elder Mrrglmrgl leads you by the hand to the old altar at the edge of the village. He lifts your hand, with the pearl in it, over the shell at its top, and lets go.)$B$BMrglmrgl.",
         progress="(The shell at the altar's top is empty.)",
         reward="(The pearl settles into the altar's shell with a soft click. Behind you, the whole village erupts in gurgling cheers. Grrmlgrrl lifts you off your feet. Murlorga cries. Blrrgl steals something from your pack in the confusion and gives it back.)",
         rewards=["pearl_charm"]),
    dict(n=16, title="Mrgl Mrgl, Land-Walker!", giver="npc:elder", ender=THUNDRIS_WINDWEAVER, level=13, min=11, xp=3, prev=15,
         log="Take the Elder's scroll to Thundris Windweaver in Auberdine.",
         text="(Elder Mrrglmrgl presses a soggy scroll into your hands. On it is a drawing: a murloc and a tall elf with long ears, shaking hands. He points at the elves' town, and gives you a gentle push toward the water.)",
         reward="A murloc... carrying a letter. Well. Stranger things have washed up in Auberdine, though not many.$B$BIf you mean us no harm, little one, there is more than enough work here for anyone who would help. The Highborne ruins, the corrupted furbolgs, the creatures of the coast... Darkshore is sick, and we could use every hand. Even a webbed one."),
]

NAGA_QUESTS = [
    dict(n=30, title="Blood in the Water", giver="npc:szaria", ender="npc:szaria", level=10, min=10, xp=7,
         log="Kill 6 Stormscale Infiltrators on the island to the north.",
         kill=[("npc:infiltrator", 6)],
         text="You came to us out of the deep, like the rest of us. Good. Then you know what follows us.$B$BThe Stormscale do not let their deserters go. They have sent hunters after us, and they wait on the island to the north for the night we sleep too soundly. Go there first. Remind them what we were trained to do.",
         progress="The Stormscale still wait on the northern island.",
         reward="Then the water around us is ours again, for now. You fight like one who remembers the old drills. We all do. That is what frightens them."),
    dict(n=31, title="Sealed Orders", giver="npc:szaria", ender=GLYNDA_NALSHEA, level=11, min=10, xp=7, prev=30,
         log="Take 4 Stormscale Orders from the infiltrators and bring them to Sentinel Glynda Nal'Shea in Auberdine.",
         items=[("orders", 4)],
         text="The hunters carry orders, sealed in the old way. What the Stormscale plan, the night elves of Auberdine will want to know.$B$BI know what they will think when one of us walks into their town. Go anyway. Give the orders to the sentinel who commands there. If we are to live on this coast, we must be worth more to them alive than dead.",
         progress="Speak quickly, naga. My archers are watching you.",
         reward="These are Stormscale seals. Real ones.$B$B...I will not pretend I am glad to see your kind on my docks. Ten thousand years ago your people drowned my world, and the Stormscale still kill my sentinels on this very coast. But you brought me their plans, and I am not too proud to read them.$B$BYou may stay. Help us, and we will see. Betray us, and the sentinels have long memories.",
         standing=[(69, 250)]),
    dict(n=32, title="The Tide Turns", giver=ONU, ender="npc:scout", level=18, min=17, xp=5,
         log="Travel south along the coast to the Zoram Strand in Ashenvale and find out what stirs the Wrathtail naga.",
         text="The Wrathtail have woken, to the south, on the Zoram Strand. Their witches sing at night, and the sea answers them. Whatever they are calling up, it will not stop at Ashenvale's shore.$B$BYou have earned the elves' trust, or their tolerance, which is as much as any of us will get. Now go south and see what the Wrathtail are doing. Go carefully. They will know you for a deserter the moment they see you.",
         onu_text="The Wrathtail stir in the south, young one, on the shore the elves call the Zoram Strand. I hear the sea grow restless there, and I hear in it voices like yours: naga voices, singing to something in the deep.$B$BYou have done much for the forest of Darkshore. Go now, and see what the Wrathtail are about. Whatever you find there, I suspect it is your own path, and not ours.",
         reward="Mon, you got a death wish? Walkin' up on me like dat, scales and all... Ha! Lucky for you, you ain't one of dem Wrathtail, or you'd have a spear in ya already.$B$BZun'jin of the Darkspear. Scouting dis beach for Zoram'gar."),
    dict(n=33, title="Strangers on the Shore", giver="npc:scout", ender="npc:scout", level=18, min=17, xp=6, prev=32,
         log="Kill 4 Wrathtail Myrmidons and 4 Wrathtail Razortails on the Zoram Strand.",
         kill=[(WRATHTAIL_MYRMIDON, 4), (WRATHTAIL_RAZORTAIL, 4)],
         text="Dem Wrathtail been pushin' me up dis beach all mornin'. Too many of dem for one troll, even a good one.$B$BYou wanna prove you ain't one of dem? Easy. Thin 'em out. Myrmidons and Razortails, the ones closest to my hidin' spot. Then we talk.",
         progress="Still hearin' dem hiss out dere.",
         reward="Ha! Dat's how it's done! You fight like you got somethin' to prove, mon. I like dat."),
    dict(n=34, title="An Unlikely Allegiance", giver="npc:scout", ender=MARUKAI, level=19, min=17, xp=5, prev=33,
         log="Speak with Marukai at Zoram'gar Outpost, on the Zoram Strand.",
         text="Listen. Dere be a Horde outpost down dis coast: Zoram'gar. Marukai runs things dere for the Darkspear, and he got the same problem I got: Wrathtail.$B$BThe Darkspear know what it is to be cast out by your own kind, mon. Vol'jin took us out of the jungle when our own tried to sacrifice us. I'll put in a word for you. Go to Zoram'gar and talk to Marukai. Don't let 'em spear you on the way in.",
         reward="Zun'jin sent a naga to my outpost. A naga.$B$B...He says you fought beside him, and that the Wrathtail hate you more than they hate us. That counts for something. Not everything. Something.$B$BThe Horde is made of those the world threw away, so I will not throw you away before I see what you are. The Wrathtail are your people's enemies and ours. Show me what you will do to them.",
         rewards_choice=["szaria_band", "darkspear_cloak"], standing=[(530, 250), (76, 150)]),
]

# The naga's camp and its quests: retired (the user: their story in Azshara, 10 to 55, their camp retired).
NAGA_CAMP = False
# What the retired camp's Darkshore did to the world database, undone by tools/build_data.py's SQL on a
# realm that had it: these quests (leading out of Darkshore to the Alliance) were closed to the naga by
# conditions, and these (the Alliance's alone) opened to them.
RETIRED_NAGA_CLOSED = [741, 942, 943, 968, 967, 970, 973, 1140, 1167, 981, 1143, 1133, 5321]
RETIRED_DARKSHORE_ALLIANCE_ONLY = [4722, 4723, 4725, 4727, 4728, 4730, 4731, 4732, 4733, 4811, 4812]
# Factions neutral to the naga from the start (the Horde's other races are hated by them): Darnassus
# (Azshara's Talrendis Point and Shadowsong Shrine are its people's: bible 18.1), Ironforge (the Explorers'
# League), Gnomeregan Exiles (the retired camp's Darkshore had theirs; harmless).
NAGA_NEUTRAL_FACTIONS = [69, 47, 54]

# The murlocs' language: the game's Titan (Languages.dbc 9, skill 140), named Nerglish in the patch.
NERGLISH_LANGUAGE = 9
# The murlocs' village off Auberdine and its quests: retired (the user: the murlocs start at the Zoram
# Strand, Ashenvale, under the Wrathtail naga: tools/murloc/). Kept here, off, for the record.
MURLOC_VILLAGE = False
# The murlocs' story's chapters released (tools/murloc/ch0 to chN): the ones after are still being written.
MURLOC_CHAPTERS = 10
# The naga's story's chapters released (tools/naga/ch0 to chN).
NAGA_CHAPTERS = 1
