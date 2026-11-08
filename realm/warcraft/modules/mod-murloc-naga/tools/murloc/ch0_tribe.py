# SPDX-License-Identifier: GPL-3.0-or-later
"""The tribe's people who come back chapter after chapter (tools/murloc/SCHEMA.md): the hub's trades
beyond chapter 1's (the Saltscar's hubs, from the uprising on: the story bible's hub kit), and the friends
and rivals met in one chapter and met again in others. Nobody here stands anywhere: each chapter puts
them at its places (SPAWNS), with its own phase rules. Chapter 1's people (the elder, the cook, the
class trainers...) are ch1's."""

CHAPTER = dict(key="ch0", title="The Tribe", levels=(10, 55), map=1, zones=[])

PLACES = {}

_TRADE = "Learn, and we all eat. Learn badly, and we all eat badly."

NPCS = [
    # The trades (bible 17.1): a profession each, the game's trainer's spell list to Artisan.
    dict(key="mrsha", name="Mrsha Kelpweaver", subname="Herbalism Trainer", look="murloc_green", level=35,
         role="profession:herbalism", gossip="Kelp, weed, bloom. The sea grows medicine if you ask it nicely.",
         idle=[("state", "self", "work"), ("every", 30000, [("emote", "self", "eat")])]),
    dict(key="brewglub", name="Brewglub the Stinky", subname="Alchemy Trainer", look="murloc_fel", level=35,
         role="profession:alchemy", gossip="Don't smell it. Don't drink it. Don't ask what happened to my last apprentice.",
         idle=[("state", "self", "work"), ("every", 25000, [("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2")])]),
    dict(key="grrsh", name="Grrsh Sharkskin", subname="Skinning Trainer", look="murloc_slate", level=35,
         role="profession:skinning", gossip="Everything in the sea has a skin. Everything.",
         idle=[("state", "self", "work")]),
    dict(key="mrrsk", name="Mrrsk Hidescraper", subname="Leatherworking Trainer", look="murloc_bronze", level=35,
         role="profession:leatherworking", gossip="Shark leather. Crab leather. Naga leather, if the long ones bother us again.",
         idle=[("state", "self", "work")]),
    dict(key="brrkl", name="Brrkl Stonegrip", subname="Mining Trainer", look="murloc_grey", level=35,
         role="profession:mining", gossip="Rocks under the water are rocks too. Harder to see. Same to hit.",
         idle=[("state", "self", "mine")]),
    dict(key="krrgl", name="Krrgl Coalbelly", subname="Blacksmithing Trainer", look="murloc_red", level=40,
         role="profession:blacksmithing+repair", sells=[2880, 3466, 3857, 5956, 2901],
         gossip="Naga steel, dwarf iron, goblin scrap. It all bends if you hit it enough.",
         idle=[("state", "self", "work"), ("every", 12000, [("sound", "self", 4614)])]),
    dict(key="mmrglla", name="Mmrglla Netknot", subname="Tailoring Trainer", look="murloc_purple", level=35,
         role="profession:tailoring", gossip="A net is a coat with holes. A coat is a net without them. Simple.",
         idle=[("state", "self", "work")]),
    dict(key="sprokgl", name="Sprokgl", subname="Engineering Trainer", look="murloc_orange", level=35,
         role="profession:engineering", gossip="It works. It will work. It worked once. Nearly.",
         idle=[("state", "self", "work"), ("every", 40000, [("visual", "self", 34602)])]),
    dict(key="shimmrl", name="Shimmrl", subname="Enchanting Trainer", look="murloc_ice", level=35,
         role="profession:enchanting", gossip="The pearl-glow goes into the spear. Then the spear glows. Then the naga run.",
         idle=[("state", "self", "work")]),
    dict(key="pearlmrgl", name="Pearlmrgl", subname="Jewelcrafting Trainer", look="murloc_pale", level=35,
         role="profession:jewelcrafting", gossip="The naga wore our pearls. Now we wear them.",
         idle=[("state", "self", "work")]),
    dict(key="scrawlgl", name="Scrawlgl", subname="Inscription Trainer", look="murloc_abyssal", level=35,
         role="profession:inscription", gossip="I scratch the shells. The shells remember. Nobody reads them. Still.",
         idle=[("state", "self", "read")]),
    dict(key="fnrrgl", name="Fnrrgl", subname="Stolen Goods", look="murloc_gold", level=30, role="vendor",
         sells=[17030, 17020, 17031, 17032, 17028, 17029, 5140, 6947, 3775, 2892, 5237, 10918, 2512, 2516, 2515, 2519,
                11285, 11284, 2320, 2321, 4291, 8343, 2324, 2604, 2605, 6260, 3371, 3372, 8925, 18256, 2880, 3466, 3857,
                4289, 2678, 3713, 30817, 159, 6529, 6530, 4470, 4399, 6217, 6256, 2901, 7005, 5956, 6219],
         gossip="Found it. All of it. Nobody was using it. Probably.",
         idle=[("every", 25000, [("emote", "self", "beg"), ("emote", "self", "laugh")])]),
    dict(key="caller", name="Current-Caller Blubb", subname="Travel", look="murloc_blue", level=30, role="travel",
         travel=[("ch2:hub", "ch2:ch2_arrival", "Greymist Cove."), ("ch3:hub", "ch3:ch3_uprising", "The Saltscar camp, in the pens."),
                 ("ch4:hub", "ch4:ch4_arrival", "Saltscar Shallows, by the Bluegill."), ("ch5:hub", "ch5:ch5_arrival", "Torn Fin Cove."),
                 ("ch6:hub", "ch6:ch6_arrival", "Murk-Eye's Grotto."), ("ch7:hub", "ch7:ch7_arrival", "The Mire Islets."),
                 ("ch8:hub", "ch8:ch8_arrival", "The wreck of the Lucky Cod."), ("ch9:hub", "ch9:ch9_arrival", "Colossal Cove."),
                 ("ch10:hub", "ch10:ch10_arrival", "Saltscar Landing. Home.")], gossip="The currents carry us. Where do you want to be carried?",
         idle=[("every", 30000, [("visual", "self", 36005)])]),

    # Friends and rivals met more than once (bible section 5). The land-walkers among them are on the tribe's
    # side (friendly to a murloc whatever its standing with their towns: they'd attack it on sight
    # otherwise), and speak their own languages.
    dict(key="mrrk", name="Mrrk Sharpfin", subname="", look="murloc_orange", level=(18, 50), role="quest",
         gossip="Mrgl. You again.", idle=[("every", 25000, [("emote", "self", "flex")])]),
    dict(key="mrrgula", name="Mother Mrrgula", subname="Matriarch of the Greymist", look="murloc_pale", level=30, role="quest",
         gossip="Every little one is a little one of mine. Even the loud ones. Especially the loud ones.",
         idle=[("state", "self", "sit")]),
    dict(key="nerelith", name="Nerelith Saltwind", subname="", look=1682, level=40, side="tribe", role="quest",
         language="darnassian", gossip="Ishnu-alah, little one. You are far from the water.",
         idle=[("every", 30000, [("emote", "self", "point")])]),
    dict(key="zalja", name="Zalja the Net-Mender", subname="", look=2734, level=35, side="tribe", role="quest",
         language="troll", gossip="Ha! Da little fishman! Come, come, Zalja got work for you.",
         idle=[("state", "self", "work"), ("every", 30000, [("emote", "self", "laugh")])]),
    dict(key="fizzbo", name="Fizzbo Gillgrin", subname="Fence", look=7097, level=45, side="tribe", role="quest",
         language="common", gossip="Business is business, and business is friendship, and friendship is ten percent.",
         idle=[("every", 20000, [("emote", "self", "beg")])]),
    dict(key="bram", name="Bram Coldkettle", subname="", look=3265, level=30, side="tribe", role="quest",
         language="dwarvish", gossip="Hic. Ye're a strange wee fish, ye are.",
         idle=[("state", "self", "sit"), ("every", 20000, [("emote", "self", "laugh")])]),
    dict(key="hester", name="Hester Gale", subname="", look=3330, level=25, side="tribe", role="quest",
         language="common", gossip="Oh! Oh, it's you. Come in out of the wind, love.",
         idle=[("every", 30000, [("emote", "self", "wave")])]),
    dict(key="murkeye", name="Old Murk-Eye", subname="The Oldest Murloc", look="murloc_slate", scale=1.3, level=40, role="quest",
         gossip="I have seen more tides than there are fish. Sit. Listen. Or don't. I'll talk anyway.",
         idle=[("state", "self", "sit"), ("every", 35000, [("emote", "self", "talk")])]),
    dict(key="shellback", name="Grandmother Shellback", subname="", look=29161, scale=4.0, level=60, role="quest",
         gossip="...", idle=[("every", 45000, [("sound", "self", "splash_big")])]),
]

OBJECTS = [
    dict(key="mailbox", model=7815, name="Bottle on a Post", kind="mailbox"),
]
