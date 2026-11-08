# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's people who come back chapter after chapter (tools/naga/SCHEMA.md, tools/murloc/SCHEMA.md): the
Tide-Broken (the bible's 6.1), their younger selves for the memories, and the hub kit every hub has from 2.01 on
(the bible's 18.9). Nobody here stands anywhere: each chapter puts them at its places (SPAWNS), with its own phase
rules (a memory's spawn: phase=("memory", "<its key>")).

Lady Szaria, Myrmidon Ssaveth and Vyssa the Coral-Keeper were the retired Darkshore camp's people: they keep
their creature entries (entry=, tools/murloc/profiles.py's KEPT_ENTRIES), so a realm that had them has them
still, now the story's. Their pasts are the bible's (6.1).

Who is where, so far (each chapter adds its own):
  - chapter 1 (the crèche at Rethress Sanctum): Isshara in the Deep Pool's cage, Mrgl-Who-Counts by the mur'gul's
    hut, Nazreth and Tidepriestess Ulmara among the crèche's instructors (they come away at 1.24), young Isshara in
    the Awakening (memory m1); Lady Szaria at the Hollow (the bay's north shore), where 1.24 ends and 2.01 begins.
  - the hub kit (trainers, trades, vendors, the Tide-Caller, the drowned singer, the mailbox jar): from 2.01, at
    each hub.

Some people have two of themselves, one per part of the story, so a chapter can swap one for the other with its
phase rules: Thessa (rescued in 2.24; the priest trainer from 4.24), Mrgl-Who-Counts (the crèche's slave; the
banker from 4.22, at a giant clam). Before 4.22 the bank is the Clamwarden's locked clam.

The Tide-Caller's ways (travel=) go to the hubs' landings below, each once its quest is done (the fixed keys:
ch2_arrival, ch4_envoy, ch7_crater, ch10_creche); a hub's chapter moves its landing here if it moves the hub."""

CHAPTER = dict(key="ch0", title="The Tide-Broken", levels=(10, 55), map=1, zones=[])

# The hubs' landings (the bible's 7.3), checked on the server's maps: where the Tide-Caller sets one down.
PLACES = {
    "hollow_landing": (3946.0, -6262.0),        # the Hollow, the Bay of Storms' north shore (z 2.5)
    "envoy_landing": (3676.0, -4412.0),         # beside the envoy's tent, Valormok (z 110)
    "crater_landing": (2975.0, -4800.0),        # the crater's floor on Forlorn Ridge (z 235)
    "creche_landing": (2214.0, -6442.0),        # Rethress Sanctum's beach, the crèche (z 1.6)
}

_TRADE = "Learn it well. Out here, what you can't make, you go without."

NPCS = [
    # -- the Tide-Broken -------------------------------------------------------------------------------
    dict(key="szaria", entry=975017, name="Lady Szaria", subname="The Tide-Broken", look="siren", level=40, role="quest",
         gossip="We were the Empress's once. Then Vashj's. Now we are no one's but our own, and I mean to keep it that way.",
         idle=[("every", 40000, [("emote", "self", "talk")]), ("every", 67000, [("face", "self", "player")])]),
    dict(key="ssaveth", entry=975018, name="Myrmidon Ssaveth", subname="The Tide-Broken", look="naga_warrior", level=40,
         role="quest", gossip="I watch the water. Whatever comes, it comes from the water.",
         idle=[("state", "self", "ready_thrown"), ("every", 55000, [("emote", "self", "roar")])]),
    dict(key="vyssa", entry=975019, name="Vyssa the Coral-Keeper", subname="Innkeeper", look="sorceress", level=35,
         role="quest+innkeeper+profession:cooking",
         gossip="Coral, kelp, and a dry corner if you can find one. Sit. Eat something. Then tell me who you are.",
         idle=[("state", "self", "work"), ("every", 48000, [("sound", "self", "pickup_water")])]),
    # Isshara the Keeper: old, blind, a handmaiden of the queen and a siren of Vashj's war. She turns her head to
    # whoever comes near before they make a sound (watch); she pours water over her own hands (a splash).
    dict(key="isshara", name="Isshara the Keeper", subname="Keeper of Songs", look="sea_witch", level=45, role="quest",
         gossip="Come closer, little one. I can't see you, but I can hear the sea in you.",
         watch=(9, [("face", "self", "player")], 30000),
         idle=[("every", 45000, [("emote", "self", "omnicast"), ("sound", "self", "siren_hiss")]),
               ("every", 71000, [("visual", "self", 36005), ("sound", "self", "pickup_water")])]),
    dict(key="thessa", name="Thessa", subname="", look=11266, size=1.3, level=25, role="quest",
         gossip="The sea answers if you ask it quietly. The Empress never asked anything quietly.",
         idle=[("every", 52000, [("emote", "self", "omnicast")])]),
    dict(key="thessa_trainer", name="Thessa", subname="Priest Trainer", look=11266, size=1.3, level=35,
         role="quest+trainer:priest", gossip="Kneel if you like. The sea doesn't care how you pray, only that you listen.",
         idle=[("every", 52000, [("emote", "self", "omnicast"), ("visual", "self", 57771)])]),
    dict(key="nazreth", name="Nazreth", subname="Warlock Trainer", look=4982, level=35, role="quest+trainer:warlock",
         gossip="Illidan taught us to drink from the Legion's cup and keep our own minds. Most of us did. Mostly.",
         idle=[("every", 38000, [("visual", "self", 43167)]), ("every", 61000, [("emote", "self", "spell")])]),
    # Mrgl speaks no tongue a naga knows: he says nothing aloud and shows everything (the compiler writes a quest's
    # own texts in its giver's language, so his quest texts are his broken Nazja, readable).
    dict(key="mrgl", name="Mrgl-Who-Counts", subname="", look="murloc_abyssal", level=12, role="quest",
         gossip="Mrgl... one, two, three, five. Mrgl counts. Mrgl always counts.",
         idle=[("every", 29000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget")]),
               ("every", 47000, [("emote", "self", "point"), ("emote", "self", "question")])]),
    dict(key="mrgl_banker", name="Mrgl-Who-Counts", subname="Banker", look="murloc_abyssal", level=20, role="quest+banker",
         gossip="Mrgl counts it. Mrgl counts it again. Nobody's things go missing. Nobody's.",
         idle=[("every", 29000, [("emote", "self", "talk"), ("sound", "self", "murloc_fidget")])]),

    # -- their younger selves, for the memories (canon unnamed naga, invented attributions: the bible's 3.3) --
    dict(key="isshara_young", name="Isshara", subname="Siren of the Deep", look="coilfang_siren", size=1.1, level=30,
         role="quest", untouchable=True, gossip="Stay close to me. Whatever you see, it already happened.",
         idle=[("every", 43000, [("emote", "self", "omnicast")])]),
    dict(key="szaria_young", name="Szaria", subname="Siren of Serena's Host", look=18395, size=1.1, level=30, role="quest",
         untouchable=True, gossip="Keep your trident up and your mouth shut. Scarscale is watching.",
         idle=[("every", 47000, [("emote", "self", "talk")])]),
    dict(key="ssaveth_young", name="Ssaveth", subname="Myrmidon of the Deep", look="coilfang_myrmidon", size=1.3, level=30,
         role="quest", untouchable=True, gossip="Hold the line. That is the whole of it. Hold the line.",
         idle=[("state", "self", "ready_thrown"), ("every", 55000, [("emote", "self", "roar")])]),
    dict(key="vyssa_young", name="Vyssa", subname="Acolyte of Lady Serpentra", look=18396, size=1.0, level=30, role="quest",
         untouchable=True, gossip="Lady Serpentra says magic is only listening very hard. I listen very hard!",
         idle=[("every", 41000, [("emote", "self", "laugh")])]),

    # -- the hub kit (bible 18.9): every hub's from 2.01 on; the game's trainers' lists ------------------------
    dict(key="kessh", name="Myrmidon Kessh", subname="Warrior Trainer", look=18398, size=1.3, level=40,
         role="trainer:warrior", gossip="Ssaveth and I drilled on the same sand for a hundred years. He still drops his left.",
         idle=[("state", "self", "ready_thrown"), ("every", 44000, [("emote", "self", "battle_roar")])]),
    dict(key="thessk", name="Thessk Snaptamer", subname="Hunter Trainer", look=22872, size=1.1, level=40,
         role="trainer:hunter+stable", gossip="Beasts don't lie. Neither does a bowstring. I trust both.",
         idle=[("every", 47000, [("emote", "self", "point"), ("emote", "self", "laugh")])]),
    dict(key="thessk_turtle", name="Snap", subname="Thessk's Pet", look="dragon_turtle", size=0.45, level=20,
         role="ambient", type="beast", idle=[("every", 33000, [("sound", "self", 1463)])]),
    dict(key="shivra", name="Shivra Quickfin", subname="Rogue Trainer", look=18391, size=1.0, level=40,
         role="trainer:rogue", gossip="Quick fins, quiet tail. Whatever you're holding, hold it like it was always yours.",
         idle=[("every", 39000, [("emote", "self", "shy")])]),
    dict(key="ulmara", name="Tidepriestess Ulmara", subname="Priest Trainer", look=4974, level=35,
         role="quest+trainer:priest", gossip="The crèche taught me to pray to a statue. The sea taught me to pray to the sea.",
         idle=[("every", 46000, [("emote", "self", "omnicast"), ("visual", "self", 57771)])]),
    dict(key="oshra", name="Tidecaller Oshra", subname="Shaman Trainer", look=4979, level=40, role="trainer:shaman",
         gossip="Earth under the water, fire under the earth, air over the waves. And the water, everywhere.",
         idle=[("every", 50000, [("emote", "self", "omnicast"), ("visual", "self", 13236)])]),
    dict(key="lyrenne", name="Sorceress Lyrenne", subname="Mage Trainer", look=6766, level=40, role="trainer:mage",
         gossip="My sister cooks with fire. I study it. The difference is mostly in the eyebrows.",
         idle=[("every", 43000, [("visual", "self", 32992)]), ("every", 97000, [("visual", "self", 34602), ("emote", "self", "stun")])]),
    # the trades: renegades with a craft each (the game's trainer's list to Artisan)
    dict(key="hookfin", name="Old Nethris Hookfin", subname="Fishing Trainer", look=4764, level=35,
         role="profession:fishing", gossip="Fish don't care whose tide it is. Sit. Hold the line. Wait. That's all of it.",
         idle=[("state", "self", "work")]),
    dict(key="ysh", name="Mender Ysh", subname="First Aid Trainer", look=4976, level=35, role="profession:first_aid",
         gossip="Kelp, salt and a steady hand. Bind it before the sharks smell it.", idle=[("state", "self", "work")]),
    dict(key="varra", name="Kelpmother Varra", subname="Herbalism Trainer", look=4977, level=35, role="profession:herbalism",
         gossip="Everything that grows above the tide was once something that grew below it. Probably.", idle=[("state", "self", "work")]),
    dict(key="oleth", name="Brinewitch Oleth", subname="Alchemy Trainer", look=4975, level=35, role="profession:alchemy",
         gossip="Don't drink anything on that shelf. Don't smell that one. Don't look at that one too long.",
         idle=[("state", "self", "work"), ("every", 40000, [("visual", "self", 60059)])]),
    dict(key="sheshk", name="Sheshk the Flayer", subname="Skinning Trainer", look=4763, level=35, role="profession:skinning",
         gossip="Shark, crab, boar. Everything wears a coat. Take it off gently.", idle=[("state", "self", "work")]),
    dict(key="hissra", name="Hissra Tanscale", subname="Leatherworking Trainer", look=4983, level=35,
         role="profession:leatherworking", gossip="Sharkskin turns a blade and keeps the salt out. What more do you want from a coat?",
         idle=[("state", "self", "work")]),
    dict(key="grosh", name="Grosh Stonecoil", subname="Mining Trainer", look=4765, level=35, role="profession:mining",
         gossip="Under the sand, rock. Under the rock, ore. Under the ore, more rock. Dig.", idle=[("state", "self", "work")]),
    dict(key="rhazz", name="Forgecoil Rhazz", subname="Blacksmithing Trainer", look=6765, level=40,
         role="profession:blacksmithing+repair", sells=[2880, 3466, 3857, 5956, 2901],
         gossip="Salt eats steel. So I make more steel. Bring me what's broken.",
         idle=[("state", "self", "work"), ("every", 14000, [("sound", "self", 4614)])]),
    dict(key="lysse", name="Netweaver Lysse", subname="Tailoring Trainer", look=4978, level=35, role="profession:tailoring",
         gossip="A net is a robe with holes in it. Close the holes. Now it's a robe.", idle=[("state", "self", "work")]),
    dict(key="sszix", name="Tinker Sszix", subname="Engineering Trainer", look=4921, level=35, role="profession:engineering",
         gossip="The goblins throw away the best things. Gears! Springs! Things that go bang!",
         idle=[("state", "self", "work"), ("every", 45000, [("visual", "self", 34602)])]),
    dict(key="avessa", name="Pearlsinger Avessa", subname="Enchanting Trainer", look=4982, level=35,
         role="profession:enchanting", gossip="Sing to a pearl long enough and it remembers the song. So does a blade.",
         idle=[("state", "self", "work"), ("every", 37000, [("visual", "self", 22581)])]),
    dict(key="nyss", name="Coralcutter Nyss", subname="Jewelcrafting Trainer", look=4973, level=35,
         role="profession:jewelcrafting", gossip="Coral, pearl, a little stone from the land-walkers. Cut it true.",
         idle=[("state", "self", "work")]),
    dict(key="thalassa", name="Inkfin Thalassa", subname="Inscription Trainer", look=4972, level=35,
         role="profession:inscription", gossip="Squid ink on shell. Write it down, little one. Somebody will try to make you forget.",
         idle=[("state", "self", "work")]),
    # Vyssa's stores (the bible's vendors)
    dict(key="ishra", name="Ishra", subname="Trade Goods and Reagents", look=4974, level=30, role="vendor",
         sells=[2320, 2321, 4291, 8343, 2324, 2604, 2605, 6260, 3371, 3372, 8925, 18256, 2678, 30817, 4289, 6217, 6256,
                17030, 17020, 17031, 17032, 17028, 17029, 5140],
         gossip="Thread, salt, vials, candles, dust. Vyssa keeps the food; I keep everything else.",
         idle=[("every", 35000, [("emote", "self", "talk")])]),
    dict(key="tessh", name="Tessh Barbtail", subname="Ammunition and Poisons", look=4910, level=30, role="vendor",
         sells=[2512, 2515, 3030, 11285, 2516, 2519, 3033, 11284, 6947, 3775, 2892, 5237, 10918],
         gossip="Arrows, shot, and the things a rogue dips her blades in. Don't lick your fingers.",
         idle=[("every", 41000, [("emote", "self", "work")])]),
    # The bank before 4.22: the Clamwarden keeps the camp's things in a giant clam with a lock.
    dict(key="clamwarden", name="Clamwarden Ilsyra", subname="Banker", look=4977, level=30, role="banker",
         gossip="What goes into the clam stays in the clam. I have the only key. I sleep on it.",
         idle=[("every", 44000, [("emote", "self", "talk")])]),
    dict(key="tidecaller", name="Tide-Caller Venn", subname="Travel", look=22871, size=1.1, level=35, role="travel",
         travel=[("hollow_landing", "ch2:ch2_arrival", "Carry me to the Hollow."),
                 ("envoy_landing", "ch4:ch4_envoy", "Carry me to the envoy's tent at Valormok."),
                 ("crater_landing", "ch7:ch7_crater", "Carry me to the crater on Forlorn Ridge."),
                 ("creche_landing", "ch10:ch10_creche", "Carry me home, to Rethress Sanctum.")],
         gossip="The currents run under every shore of Azshara. Tell me where, and hold your breath.",
         idle=[("every", 30000, [("visual", "self", 36005)])]),
    # The graveyards' spirit healer is the game's (the engine places it); beside it at each hub a drowned siren sings.
    dict(key="drowned_singer", name="Drowned Singer", subname="", look=11266, size=1.2, level=30, role="ambient",
         idle=[("state", "self", "channel"), ("every", 20000, [("visual", "self", 10848)]),
               ("every", 59000, [("sound", "self", "siren_hiss")])]),
]

OBJECTS = [
    dict(key="mail_jar", model="naga_jar", name="Sealed Jar", kind="mailbox", scale=1.3),
    dict(key="locked_clam", model="World\\GENERIC\\ACTIVEDOODADS\\Clam\\GiantClamCLOSED.M2", name="Locked Clam",
         kind="doodad", scale=1.6),
    dict(key="giant_clam", model="World\\GENERIC\\ACTIVEDOODADS\\Clam\\GiantClamActive.m2", name="Mrgl's Clam",
         kind="doodad", scale=2.0),
]
