# SPDX-License-Identifier: GPL-3.0-or-later
"""Chapter 8 of the murlocs' story: Red Sails (levels 40 to 44), the bible's section 14.

Stranglethorn's south coast (map 0). The hub is the wreck of the Lucky Cod, a merchantman beached on the
Wild Shore south of Booty Bay (around -14700, 303: 45 yards and more from every hostile spawn of the game's,
the Bloodsail's warlock camp to the north-east and their three ships to the south-west). Around it: the
Bloodsail's ships and islets (the lookouts, the crates, Keelhaul's and Firallon's decks), the Bloodsail's
north-beach camp (the parrot, the shark-bait posts in its shallows), the reef north of the wreck (the giant
clams), the Saltscale's beach and the Mosh'Ogg's cook-pot along the shore to the east, the jungle slopes
behind the wreck (herbs). Booty Bay (a town: the goblins start Unfriendly, -500): Fizzbo's den on the sand
under the lowest pier, the anglers on that pier, the Salty Sailor Tavern's kitchen corner by its stove (the
chef and the glowing egg basket). The naga's dig is at Nek'mani Wellspring, the troll ruins on the hill
north of Booty Bay (the bible's "Vile Reef" naga: the game's Naga Explorers and Lord Sakrasis live there,
not at the Vile Reef): a drowned shrine at the bottom of its pool, chained murloc diggers, Ilyssa and Lord
Sakrasis over the egg net.

The eggs come home either way (8.08a, a fair trade through Fizzbo, or 8.08b, the heist), and 8.09 follows
either (prev_any). Booty Bay's own people (the Bruisers, the chef, the anglers, the bookie) are the town's
(faction:21); Fizzbo, his porter and Zalja are the tribe's friends.

Plain data: tools/murloc/SCHEMA.md."""

# -- when people and things are there ------------------------------------------------------------
HUB = ("from", "ch8_arrival")                              # the hub kit, the camp
ELDER = ("between", "ch7:ch7_end", "ch9:ch9_elder")        # the Elder, from the landing until he dies
TURTLE = ("between", "ch7:ch7_end", "ch8_end")             # Grandmother Shellback in the shallows
KITCHEN = ("until", "ch8_hatch")                           # the Salty Sailor's chef and the egg basket
HATCHED = ("from", "ch8_hatch")                            # the hatchlings at home; Zalja in port
POT = ("until", "ch8_pot")                                 # Mrrk in the Mosh'Ogg's pot
MRRK_HOME = ("from", "ch8_pot")                            # Mrrk at the wreck
DIG = ("until", "ch8_sakrasis")                            # the naga's dig at the wellspring

CHAPTER = dict(key="ch8", title="Red Sails", levels=(40, 44), map=0, zones=[33], hub="hub")

TOWNS = ["Booty Bay"]

PLACES = {
    # the wreck of the Lucky Cod: the fire in the middle, the cast around it, the trainers and trades in rings
    "hub": (-14700.0, 303.0), "wreck": (-14729.0, 303.0, -0.2), "hold": (-14727.0, 303.0),
    "elder": (-14708.0, 303.0), "elder_cough": (-14708.6, 303.7), "elder_draw": (-14705.0, 300.0),
    "draw_a": (-14704.0, 298.8), "draw_b": (-14704.0, 301.4), "draw_a2": (-14703.0, 298.6), "draw_b2": (-14703.0, 301.6),
    "draw_mid": (-14703.6, 300.1), "elder_shore": (-14716.0, 300.0),
    "grrmlgrrl": (-14693.9, 308.1), "grrm_draw": (-14695.8, 306.4), "grrm_draw2": (-14696.6, 305.2), "grrm_lie": (-14713.5, 310.0),
    "mrrk": (-14700.0, 311.0), "mrrk_draw": (-14700.2, 308.8),
    "glubbub": (-14705.7, 308.7), "glubbub_front": (-14704.2, 307.2), "glubbub_front2": (-14703.6, 306.4),
    "glubbub_away": (-14710.0, 313.0), "glubbub_shore": (-14717.0, 296.0), "altar": (-14708.5, 311.8),
    "krrgl": (-14707.4, 297.8), "krrgl_front": (-14706.2, 299.0), "krrgl_anvil": (-14709.6, 296.0),
    "murlorga": (-14700.7, 295.0), "pot": (-14700.5, 297.6), "murlorga_feet": (-14701.6, 296.4),
    "basket_spot": (-14702.6, 296.4), "bribe_fish": (-14699.0, 297.9), "bribe_fish2": (-14698.4, 298.8),
    "bribe_fish3": (-14699.8, 299.1),
    "blrrgl": (-14694.1, 297.6), "blrrgl_log": (-14692.0, 295.6), "blrrgl_lean": (-14696.0, 299.4), "blrrgl_hop": (-14696.6, 300.4),
    "sloshy": (-14693.0, 303.0), "slubb": (-14690.4, 314.5), "slubb_front": (-14691.4, 313.4),
    "brrgmrk": (-14690.4, 291.5), "mrrgasha": (-14686.4, 296.7), "fizzmrgl": (-14685.0, 303.0), "glubba": (-14686.4, 309.3),
    "mrsha": (-14696.1, 317.5), "brewglub": (-14701.8, 317.9), "grrsh": (-14707.3, 316.1), "mrrsk": (-14711.7, 312.4),
    "mrrlglr": (-14712.3, 294.4), "fnrrgl": (-14707.5, 290.0), "caller": (-14695.6, 290.8), "runner": (-14701.4, 287.1),
    "brrkl": (-14685.9, 288.9), "mmrglla": (-14682.2, 293.9), "sprokgl": (-14680.2, 299.9), "shimmrl": (-14680.2, 306.1),
    "pearlmrgl": (-14682.2, 312.1), "scrawlgl": (-14685.9, 317.1), "gurgle": (-14720.5, 318.0),
    "mailbox": (-14690.0, 285.5), "graveyard": (-14713.0, 283.0),
    "hut_1": (-14717.0, 323.0), "hut_2": (-14676.0, 296.0), "hut_3": (-14690.0, 325.0), "rack": (-14714.0, 290.5),
    "net_pile": (-14719.5, 309.0), "crates_hub": (-14711.0, 319.0), "barrel_hub": (-14687.5, 321.5),
    "hatch_r0": (-14703.0, 295.5), "hatch_r1": (-14704.5, 297.5), "hatch_r2": (-14698.0, 295.5),
    "hatch_s1": (-14704.0, 294.0), "hatch_s2": (-14702.0, 293.5), "hatch_s3": (-14703.5, 292.5),
    "tidepool": (-14703.0, 263.5), "crawler_beach": (-14805.0, 380.0), "elder_away": (-14713.0, 296.5),
    "draw_k": (-14705.5, 302.6), "grrm_help": (-14715.0, 302.5),
    "shellback": (-14752.0, 296.0), "turtle_side": (-14738.0, 298.0),
    # where people look
    "ships_view": (-14950.0, 300.0), "booty_dir": (-14440.0, 450.0), "saltscale_dir": (-14490.0, 182.0),
    "ogre_dir": (-14424.0, 172.0), "jungle_dir": (-14520.0, 240.0), "look_left": (-14700.0, 340.0),
    "look_right": (-14700.0, 266.0), "north_camp": (-14695.0, 490.0), "reef": (-14640.0, 695.0),
    "wellspring": (-13818.0, 398.0),
    # the Bloodsail's ships: three lookouts on the islets, the crates, the props a lookout sees
    "lookout_north": (-14882.0, 444.0), "lookout_west": (-14966.0, 302.0), "lookout_south": (-14881.0, 69.0),
    "lb_north": (-14905.0, 392.0, 0.0), "cr_north": (-14896.0, 385.0), "lb_west": (-14985.0, 290.0, 0.0),
    "cr_west": (-14972.0, 296.0), "lb_south": (-14900.0, 92.0, 0.0), "cr_south": (-14889.0, 80.0),
    "crate_1": (-14886.0, 450.0), "crate_2": (-14877.0, 438.0), "crate_3": (-14959.0, 295.0), "crate_4": (-14971.0, 311.0),
    "crate_5": (-14947.0, 301.0), "crate_6": (-14886.0, 61.0), "crate_7": (-14875.0, 77.0), "crate_8": (-14893.0, 320.0),
    # the Bloodsail's rum: their warlock camp east of the wreck, their north-beach camp, their sandbar
    "rum_1": (-14615.0, 341.0), "rum_2": (-14620.0, 320.0), "rum_3": (-14603.0, 336.0), "rum_4": (-14691.0, 481.0),
    "rum_5": (-14683.0, 494.0), "rum_6": (-14706.0, 490.0), "rum_7": (-14897.0, 316.0), "rum_8": (-14884.0, 303.0),
    "rum_east": (-14615.0, 330.0),
    # the north-beach camp: the parrot; the shark-bait posts in its shallows; the shark
    "parrot": (-14689.0, 484.5),
    "post_1": (-14736.0, 458.0), "post_2": (-14730.0, 458.0), "post_3": (-14724.0, 458.0), "post_4": (-14718.0, 458.5),
    "bait_1": (-14736.0, 459.6), "bait_2": (-14730.0, 459.6), "bait_3": (-14724.0, 459.6), "bait_4": (-14718.0, 460.1),
    "bait_flee": (-14745.0, 400.0), "shark": (-14768.0, 446.0),
    # the reef north of the wreck: giant clams
    "clam_1": (-14690.0, 680.0), "clam_2": (-14660.0, 702.0), "clam_3": (-14630.0, 665.0), "clam_4": (-14600.0, 700.0),
    "clam_5": (-14640.0, 725.0), "clam_6": (-14712.0, 700.0), "clam_7": (-14575.0, 688.0), "clam_8": (-14560.0, 718.0),
    "clam_9": (-14615.0, 738.0), "clam_10": (-14680.0, 655.0),
    # the Bloodsail's warlock camp: the Saltscale Oracle's post
    "oracle_post": (-14616.0, 326.0), "oracle_tied": (-14616.5, 327.8), "oracle_free": (-14619.0, 329.0),
    # the Saltscale's beach, east along the shore
    "sb_v": (-14490.0, 182.0), "sb_chief": (-14486.0, 183.0), "sp_a": (-14500.0, 190.0), "sp_b": (-14497.0, 194.5),
    "sp_c": (-14503.5, 186.0), "sb_hut": (-14481.0, 188.0), "sb_hut2": (-14488.0, 174.0), "sb_villager": (-14484.0, 179.0),
    "sb_fry": (-14492.0, 186.0),
    # the Saltscale who stalk the wreck (8.11b)
    "amb_1": (-14660.0, 200.0), "amb_2": (-14650.0, 215.0), "amb_3": (-14640.0, 190.0), "amb_4": (-14625.0, 210.0),
    "amb_5": (-14610.0, 195.0), "amb_6": (-14600.0, 225.0), "amb_7": (-14640.0, 235.0), "amb_8": (-14590.0, 200.0),
    "amb_9": (-14575.0, 215.0), "amb_10": (-14560.0, 195.0), "amb_11": (-14630.0, 175.0), "amb_12": (-14600.0, 175.0),
    "amb_13": (-14665.0, 225.0), "amb_14": (-14575.0, 185.0),
    # the Mosh'Ogg's cook-pot at the foot of the hills east along the beach
    "ogre_pot": (-14424.0, 172.0), "cook_a": (-14420.0, 168.0), "cook_b": (-14421.0, 177.0), "ogre_fire": (-14427.5, 167.5),
    "mrrk_out": (-14431.0, 173.0), "ogre_g1": (-14436.0, 166.0), "ogre_g2": (-14417.0, 158.0), "ogre_g3": (-14434.0, 186.0),
    # the jungle slopes behind the wreck
    "herb_1": (-14540.0, 230.0), "herb_2": (-14530.0, 250.0), "herb_3": (-14512.0, 240.0), "herb_4": (-14495.0, 225.0),
    "herb_5": (-14520.0, 215.0), "herb_6": (-14550.0, 245.0), "herb_7": (-14505.0, 258.0), "herb_8": (-14485.0, 245.0),
    # Booty Bay: Fizzbo's den on the sand under the lowest pier
    "fizzbo_den": (-14449.5, 424.5), "fizzbo_crate": (-14451.2, 423.2), "fizzbo_front": (-14448.3, 426.0),
    "fizzbo_run": (-14441.0, 422.5),
    # the lowest pier: the porter, the Bruiser who checks barrels, the barrel's end, the anglers and their bobbers
    "porter_post": (-14450.5, 469.0, 4.3), "dock_bruiser": (-14447.5, 452.0, 4.1), "barrel_spot": (-14445.5, 436.5, 4.1),
    "eggs_float": (-14440.0, 428.0, 0.0),
    "fisher_1": (-14438.3, 466.8, 3.9), "fisher_2": (-14437.6, 461.0, 3.9), "fisher_3": (-14441.0, 456.8, 3.9),
    "fisher_4": (-14442.5, 444.0, 4.1), "fisher_5": (-14441.5, 434.5, 4.2),
    "bob_1": (-14432.8, 466.8, 0.0), "bob_2": (-14432.1, 461.0, 0.0), "bob_3": (-14435.5, 456.8, 0.0),
    "bob_4": (-14437.0, 444.0, 0.0), "bob_5": (-14436.0, 434.5, 0.0),
    "zalja_dock": (-14451.5, 466.0, 4.2), "zalja_front": (-14450.0, 464.5, 4.2), "zalja_boat": (-14432.0, 473.0, 0.0),
    "bookie": (-14454.5, 457.0, 4.1),
    # the Salty Sailor Tavern: its kitchen corner by the stove, and the jump into the bay below it
    "tavern_up": (-14451.0, 491.0, 15.2), "stove": (-14450.9, 496.6, 15.0), "chef": (-14452.6, 498.4, 15.2),
    "chef_egg": (-14451.9, 497.3, 16.6), "egg_basket": (-14454.4, 499.6, 15.15), "basket_eggs": (-14454.4, 499.6, 15.4),
    "kitchen_bruiser": (-14452.0, 488.0, 15.2), "kitchen_window": (-14448.0, 490.0, 15.2), "the_jump": (-14438.0, 500.0, -1.0),
    # Nek'mani Wellspring: the drowned shrine at the bottom of its pool, the diggers, the tablets
    "shrine": (-13822.0, 397.0), "egg_net": (-13823.0, 396.5), "ilyssa_shrine": (-13826.5, 399.0),
    "sakrasis_watch": (-13818.5, 394.0), "sakrasis_fight": (-13820.0, 398.0), "shrine_egg": (-13825.2, 397.8, 51.6),
    "shrine_peek": (-13840.0, 401.0), "statue_a": (-13831.0, 405.0), "statue_b": (-13812.0, 389.0), "statue_c": (-13836.0, 392.0),
    "dig_1": (-13836.0, 400.0), "dig_2": (-13830.0, 406.0), "dig_3": (-13810.0, 403.0), "dig_4": (-13804.0, 396.0),
    "dig_5": (-13814.0, 389.5), "dig_6": (-13828.0, 389.0), "dig_7": (-13798.0, 402.0),
    "shk_1": (-13835.2, 400.6), "shk_2": (-13829.3, 405.2), "shk_3": (-13809.2, 402.4), "shk_4": (-13803.2, 395.4),
    "shk_5": (-13813.3, 390.2), "shk_6": (-13827.2, 389.7),
    "tab_1": (-13845.0, 405.0), "tab_2": (-13834.0, 395.0), "tab_3": (-13800.0, 406.0), "tab_4": (-13790.0, 394.0),
    "tab_5": (-13826.0, 418.0), "tab_6": (-13796.0, 380.0), "tab_7": (-13840.0, 384.0), "tab_8": (-13808.0, 412.0),
}

# -- the people ------------------------------------------------------------------------------------

NPCS = [
    # the Elder's wet cough (an unseen thing at his feet: his own idle is chapter 1's)
    dict(key="elder_cough", name="Wet Cough", look="trigger", level=1, role="ambient", at="elder_cough",
         unit_flags=0x02000002, phase=ELDER,
         idle=[("every", 46000, [("sound", "self", 5736), ("wait", 900), ("sound", "self", "murloc_wound")])]),

    # Fizzbo's runner: the auction house, through the fence
    dict(key="runner", name="Grizzik", subname="Fizzbo's Runner", look=7112, level=35, role="auctioneer",
         language="common", at="runner", facing=1.48, phase=HUB,
         gossip="Fizzbo says you're good for it. Fizzbo says that about everybody who pays.",
         idle=[("every", 24000, [("emote", "self", "beg"), ("sound", "self", 895)]),
               ("every", 37000, [("emote", "self", "talk")])]),

    # the hatchlings: the three who decide you're their mother (8.09), and the ones at home after (later hubs too)
    dict(key="hatch_a", name="Hatchling", look="murloc_green", scale=0.35, level=3, role="ambient", summoned=True,
         idle=[("every", 9000, [("sound", "self", "baby_murloc"), ("emote", "self", "cheer")])]),
    dict(key="hatch_b", name="Hatchling", look="murloc_pale", scale=0.35, level=3, role="ambient", summoned=True,
         idle=[("every", 11000, [("state", "self", "dead"), ("sound", "self", "baby_murloc"), ("wait", 1300),
                                 ("state", "self", "none")])]),
    dict(key="hatch_c", name="Hatchling", look="murloc_orange", scale=0.35, level=3, role="ambient", summoned=True,
         idle=[("every", 13000, [("emote", "self", "dance"), ("sound", "self", "baby_murloc_dance")])]),
    dict(key="hatchling", name="Hatchling", plural="hatchlings", look="murloc_green", looks=["murloc_pale", "murloc_orange"],
         scale=0.35, level=3, role="ambient",
         idle=[("every", 17000, [("emote", "self", "dance"), ("sound", "self", "baby_murloc")]),
               ("every", 29000, [("emote", "self", "cheer")])]),

    # Booty Bay: the porter, the Bruiser who checks his barrel, the Salty Sailor's chef and his doorman
    dict(key="porter", name="Gizzle", subname="Porter", look=7112, level=30, side="tribe", role="quest",
         language="common", at="porter_post", facing=3.3, respawn=30, phase=("during", "ch8_trade"),
         greeting="Fizzbo sent ya? Heh. Fish on top, eggs underneath. Nobody looks under fish.",
         idle=[("every", 14000, [("sound", "self", 11800), ("emote", "self", "talk")])]),
    dict(key="dock_bruiser", name="Booty Bay Bruiser", look=7102, level=60, side="faction:21", role="ambient",
         language="common", health=10.0, at="dock_bruiser", facing=1.6, phase=("during", "ch8_trade"),
         watch=(7, [("face", "self", "player"), ("emote", "self", "question"),
                    ("say", "self", "Hold it. What's in the barrel? Open it.", None, 5963), ("wait", 1800),
                    ("emote", "self", "kneel"), ("wait", 1200), ("sound", "self", 11995), ("emote", "self", "rude"),
                    ("wait", 1200), ("say", "self", "Ugh! Fish! Week-old fish! Go on, get it outta here.", "wave")], 25000)),
    dict(key="chef", name="Chef Grubbo Fryfizz", subname="Salty Sailor Kitchen", look=18744, level=45, side="faction:21",
         role="ambient", language="common", health=5.0, at="chef", facing=5.47, phase=KITCHEN,
         idle=[("state", "self", "work"),
               ("every", 26000, [("state", "self", "none"), ("object", "ch1:held_egg", "chef_egg", 7), ("emote", "self", "talk"),
                                 ("sound", "self", 6763), ("wait", 2500), ("emote", "self", "flex"), ("sound", "self", 1198),
                                 ("wait", 2000), ("emote", "self", "laugh"),
                                 ("say", "self", "Not yet, my beauty. You're for the special.", None, 5964), ("wait", 2500),
                                 ("face", "self", "egg_basket"), ("emote", "self", "kneel"), ("wait", 1500),
                                 ("face", "self", "stove"), ("state", "self", "work")])],
         watch=(4, [("state", "self", "none"), ("face", "self", "player"), ("emote", "self", "attack"),
                    ("yell", "self", "Hey! HEY! No fish in my kitchen!", "shout", 5966), ("aura", "player", "collared"),
                    ("wait", 4000), ("face", "self", "stove"), ("state", "self", "work")], 15000)),
    dict(key="kitchen_bruiser", name="Booty Bay Bruiser", subname="Kitchen Door", look=7102, level=60, side="faction:21",
         role="guard", language="common", health=10.0, at="kitchen_bruiser", facing=1.2, phase=KITCHEN,
         idle=[("every", 21000, [("emote", "self", "talk"), ("sound", "self", 5961)])],
         watch=(5, [("face", "self", "player"), ("emote", "self", "point"),
                    ("yell", "self", "Oi! Kitchen's off limits, fishy!", None, 5963), ("aura", "player", "collared")], 12000)),

    # Booty Bay: the anglers on the lowest pier, and the bookie who took Zalja's bet
    dict(key="angler", name="Booty Bay Angler", plural="anglers", look=7354, looks=[7184, 7074, 7172], level=30,
         side="faction:21", role="ambient", language="common",
         at=["fisher_1", "fisher_2", "fisher_3", "fisher_4", "fisher_5"], facing=0.0,
         idle=[("state", "self", "fish"), ("every", 33000, [("sound", "self", 3354)]),
               ("every", 47000, [("say", "self", "Nothin'. Again. A whole week of nothin'.", None, 5960)])]),
    dict(key="bookie", name="Gazzik", subname="Bookie", look=15237, level=30, side="faction:21", role="ambient",
         language="common", at="bookie", facing=0.4, phase=HATCHED,
         idle=[("every", 23000, [("emote", "self", "beg"), ("sound", "self", 895)]),
               ("every", 41000, [("say", "self", "Biggest claw on the coast, troll. Biggest! Ten gold says no.", "point")])]),

    # the Saltscale: their chief and spearmen on their beach, their oracle tied to a Bloodsail post
    dict(key="saltscale_chief", name="Chieftain Glrrgul", subname="Saltscale", look="murloc_slate", scale=1.1, level=40,
         role="quest", at="sb_chief", facing=2.6,
         greeting="Back. BACK. ...You smell of dry-skin boats.",
         idle=[("every", 31000, [("emote", "self", "roar"), ("sound", "self", "murloc_alert")]),
               ("every", 43000, [("emote", "self", "talk")])]),
    dict(key="spear_a", name="Saltscale Spearman", look="murloc_green", level=38, role="ambient", at="sp_a", facing=2.6,
         idle=[("every", 27000, [("emote", "self", "attack"), ("sound", "self", "murloc_alert")])]),
    dict(key="spear_b", name="Saltscale Spearman", look="murloc_grey", level=38, role="ambient", at="sp_b", facing=2.6,
         idle=[("every", 33000, [("emote", "self", "point")])]),
    dict(key="spear_c", name="Saltscale Spearman", look="murloc_bronze", level=38, role="ambient", at="sp_c", facing=2.6,
         idle=[("every", 29000, [("emote", "self", "roar")])]),
    dict(key="saltscale", name="Saltscale Villager", plural="Saltscale", look="seer", looks=["netter"], level=36,
         role="ambient", at=["sb_villager", "sb_fry"], wander=3.0),
    dict(key="oracle_tied", name="Saltscale Oracle", subname="Bait", look="murloc_ice", level=38, role="ambient",
         at="oracle_tied", facing=4.7, respawn=30, phase=("during", "ch8_oracle"),
         idle=[("state", "self", "kneel"), ("every", 9000, [("emote", "self", "cry"), ("sound", "self", "murloc_wound")])]),
    dict(key="oracle_follow", name="Saltscale Oracle", look="murloc_ice", level=38, role="ambient", summoned=True,
         idle=[("every", 7000, [("emote", "self", "spell"), ("sound", "self", "murloc_fidget2")])]),

    # Mrrk in the Mosh'Ogg's pot, Mrrk let out, and the two ogres arguing about salt
    dict(key="mrrk_pot", name="Mrrk Sharpfin", subname="In the Pot", look="murloc_orange", level=40, role="ambient",
         at="ogre_pot", facing=1.6, respawn=30, phase=POT,
         idle=[("every", 8000, [("emote", "self", "roar"), ("sound", "self", "murloc_wound")]),
               ("every", 19000, [("emote", "self", "rude"), ("sound", "self", "murloc_aggro")])]),
    dict(key="mrrk_follow", name="Mrrk Sharpfin", look="murloc_orange", level=40, role="ambient", summoned=True,
         idle=[("every", 10000, [("emote", "self", "rude"), ("sound", "self", "murloc_fidget")]),
               ("every", 15000, [("sound", "self", "splash_small")])]),
    dict(key="cook_a", name="Mosh'Ogg Cook", look=655, level=42, side="hostile", role="enemy", language="orcish",
         at="cook_a", facing=1.4, respawn=90,
         idle=[("every", 16000, [("face", "self", "ogre_pot"), ("say", "self", "More salt! Fish-man needs more salt!", "roar", 395)])]),
    dict(key="cook_b", name="Mosh'Ogg Cook", look=416, level=42, side="hostile", role="enemy", language="orcish",
         at="cook_b", facing=4.6, respawn=90,
         idle=[("every", 19000, [("face", "self", "ogre_pot"), ("say", "self", "No! Too much salt! You always too much salt!", "talk", 396)])]),

    # the shark-bait murlocs at the north camp's posts, and the shark
    dict(key="bait_murloc", name="Tied Murloc", plural="tied murlocs", look="murloc_grey", looks=["murloc_green", "murloc_red", "murloc_pale"],
         level=36, role="ambient", at=["bait_1", "bait_2", "bait_3", "bait_4"], facing=3.1, respawn=40,
         phase=("during", "ch8_bait"),
         idle=[("state", "self", "kneel"), ("every", 8000, [("emote", "self", "cry"), ("sound", "self", "murloc_wound")])]),
    dict(key="shark", name="Bloodsail Shark", look=1557, level=43, side="hostile", role="enemy", at="shark", wander=10.0,
         respawn=60, phase=("during", "ch8_bait"), idle=[("every", 20000, [("sound", "self", 3188)])]),

    # the Bloodsail's parrot
    dict(key="parrot", name="Bloodsail Parrot", look=6190, level=5, side="neutral", role="ambient", at="parrot",
         facing=3.1, respawn=45, greeting="Squawk! Pieces of eight! Squawk!",
         idle=[("every", 14000, [("sound", "self", 4004)])]),

    # the naga's dig at Nek'mani Wellspring
    dict(key="ilyssa_shrine", name="Sea Witch Ilyssa", look="sea_witch", level=48, side="neutral", role="ambient",
         language="naga", health=20.0, unit_flags=0x2, at="ilyssa_shrine", facing=5.5, phase=DIG,
         idle=[("state", "self", "work"), ("every", 34000, [("cast", "self", 32992, "self"), ("sound", "self", "siren_hiss")])]),
    dict(key="sakrasis_watch", name="Lord Sakrasis", look=4910, level=45, side="neutral", role="ambient", language="naga",
         health=10.0, unit_flags=0x2, at="sakrasis_watch", facing=2.2, phase=DIG,
         idle=[("state", "self", "work"), ("every", 39000, [("emote", "self", "talk"), ("sound", "self", "naga_lord_hiss")])]),
    dict(key="sakrasis", name="Lord Sakrasis", look=4910, level=45, side="naga", role="enemy", language="naga", rank=4,
         health=2.2, damage=1.2, summoned=True, abilities=[(15496, 9000)]),
    dict(key="digger", name="Chained Digger", plural="chained diggers", look="murloc_grey",
         looks=["murloc_abyssal", "murloc_bronze", "murloc_slate"], level=36, role="ambient",
         at=["dig_1", "dig_2", "dig_3", "dig_4", "dig_5", "dig_6"], respawn=45, phase=DIG,
         idle=[("state", "self", "work"), ("every", 21000, [("sound", "self", 1194)]),
               ("every", 37000, [("sound", "self", 1005), ("emote", "self", "cry")])]),
    dict(key="digger_habit", name="Old Digger", subname="", look="murloc_ice", level=36, role="ambient", at="dig_7",
         facing=4.0, respawn=45, phase=DIG, greeting="Dig. Dig. Dig...",
         idle=[("state", "self", "work"), ("every", 9000, [("sound", "self", 1194)])]),
]

# -- things --------------------------------------------------------------------------------------------

EGG = "World\\Expansion02\\Doodads\\Generic\\Oracle\\O_Egg_01.mdx"
POST = "World\\Azeroth\\Stranglethorn\\PassiveDoodads\\Post\\BootyBayPost.mdx"
SCROLL = 164

OBJECTS = [
    # the camp in the wreck of the Lucky Cod
    dict(key="wreck", model="World\\wmo\\Dungeon\\MD_Shipwreck\\Shipwreck_A.wmo", name="The Lucky Cod", at="wreck",
         kind="doodad", scale=0.55, facing=1.6),
    dict(key="hut", model="murloc_hut", name="Hut", kind="doodad", scale=0.9, at=["hut_1", "hut_2", "hut_3"], phase=HUB),
    dict(key="campfire", model=192, name="Campfire", kind="doodad", at="hub", phase=HUB),
    dict(key="net_pile", model="World\\Expansion02\\Doodads\\Generic\\SeaVrykul\\Shore\\VRS_NetPile_01.mdx", name="Nets",
         kind="doodad", scale=0.8, at="net_pile", facing=1.2, phase=HUB),
    dict(key="crates", model=275, name="Salvaged Crates", kind="doodad", at="crates_hub", phase=HUB),
    dict(key="anvil", model="World\\Azeroth\\Elwynn\\PassiveDoodads\\Anvil\\Anvil.mdx", name="Salvaged Anvil",
         kind="doodad", scale=0.8, at="krrgl_anvil", facing=0.6, phase=HUB),

    # things scenes set out
    dict(key="crate_scrap", model=275, name="Crate Scrap", kind="doodad", scale=0.25),
    dict(key="coins", model=2614, name="Coins", kind="doodad", scale=0.5),
    dict(key="pebbles", model="World\\Azeroth\\Burningsteppes\\PassiveDoodads\\Rocks\\LavaRock01.mdx", name="Pebbles",
         kind="doodad", scale=0.15),
    dict(key="broken_ladle", model="World\\Generic\\Orc\\Passive Doodads\\Utensils\\LadleWood.mdx", name="Broken Ladle",
         kind="doodad", scale=0.8),
    dict(key="pearl_prop", model="great_pearl", name="Black Pearl", kind="doodad", scale=0.12),
    dict(key="chart_prop", model=SCROLL, name="Sea-Chart", kind="doodad", scale=1.2),
    dict(key="flag_drawing", model=7589, name="Drawing in the Sand", kind="doodad", scale=0.35),
    dict(key="serpent", model=212, name="Serpent Statue", kind="doodad", scale=0.8,
         at=["statue_a", "statue_b", "statue_c"], phase=DIG),
    dict(key="tablet_prop", model=5, name="Carved Tablets", kind="doodad", scale=0.4),
    dict(key="rowboat", model=124, name="Longboat", kind="doodad", scale=1.0),
    dict(key="ogre_fire", model=4611, name="Ogre Cookfire", kind="doodad", at="ogre_fire", scale=0.8),

    # the lookouts over the Bloodsail's ships (8.01): each shows a longboat unloading crates
    dict(key="lookout_north", model=627, name="Driftwood Lookout", kind="use", quest="ch8_sails", consumable=False,
         goal="North ship watched", scale=1.3, at="lookout_north", beats=[("object", "rowboat", "lb_north", 40),
                                               ("object", "crates", "cr_north", 40)]),
    dict(key="lookout_west", model=627, name="Driftwood Lookout", kind="use", quest="ch8_sails", consumable=False,
         goal="West ship watched", scale=1.3, at="lookout_west", beats=[("object", "rowboat", "lb_west", 40),
                                              ("object", "crates", "cr_west", 40)]),
    dict(key="lookout_south", model=627, name="Driftwood Lookout", kind="use", quest="ch8_sails", consumable=False,
         goal="South ship watched", scale=1.3, at="lookout_south", beats=[("object", "rowboat", "lb_south", 40),
                                               ("object", "crates", "cr_south", 40)]),
    # the Bloodsail's rum (8.03) and their crates' marks (8.04)
    dict(key="rum_cask", model=32, name="Cask of Bloodsail Rum", kind="loot", loot=[("rum", 1, 1)], quest="ch8_rum",
         scale=0.8, at=["rum_1", "rum_2", "rum_3", "rum_4", "rum_5", "rum_6", "rum_7", "rum_8"]),
    dict(key="bloodsail_crate", model=275, name="Bloodsail Crate", kind="use", quest="ch8_crates", scale=0.9,
         goal="Crate's marks seen",
         at=["crate_1", "crate_2", "crate_3", "crate_4", "crate_5", "crate_6", "crate_7", "crate_8"]),
    # the reef's giant clams (8.07)
    dict(key="clam", model="clam", name="Giant Clam", kind="loot", loot=[("black_pearl", 1, 2)], quest="ch8_pearls", scale=1.4,
         at=["clam_1", "clam_2", "clam_3", "clam_4", "clam_5", "clam_6", "clam_7", "clam_8", "clam_9", "clam_10"]),
    # 8.08a: the porter's barrel at the pier's end (set out when he starts walking)
    dict(key="fish_barrel", model=32, name="Barrel of Fish", kind="use", quest="ch8_trade", scale=1.0,
         beats=[("give", "bb_eggs", 1), ("aura", "player", "glowing_eggs"), ("object", "ch1:eggs", "eggs_float", 25),
                ("emote", "ch0:fizzbo", "bow"), ("emote", "porter", "cheer"), ("wait", 3000), ("despawn", "porter")]),
    # 8.08b: the egg basket in the Salty Sailor's kitchen
    dict(key="kitchen_basket", model="World\\Expansion02\\Doodads\\Generic\\Tuskarr\\Fishing\\TS_FishingBasket_Empty_02.mdx",
         name="Basket of Glowing Eggs", kind="use", quest="ch8_heist", scale=0.7, at="egg_basket", phase=KITCHEN,
         beats=[("give", "bb_eggs", 1), ("aura", "player", "glowing_eggs"), ("state", "chef", "none"),
                ("face", "chef", "player"), ("yell", "chef", "THIEF! My eggs! Stop that fish!", "shout", 5966),
                ("sound", "chef", 6555), ("wait", 1500), ("sound", "kitchen_bruiser", 6555), ("emote", "kitchen_bruiser", "point"),
                ("wait", 1500), ("sound", "chef", 6555)]),
    # 8.10: the anglers' bobbers
    dict(key="bobber", model=6366, name="Fishing Bobber", kind="use", quest="ch8_pier", scale=0.35, goal="Hook baited",
         at=["bob_1", "bob_2", "bob_4", "bob_5"],
         beats=[("take", "fat_fish", 1), ("state", "angler", "none"), ("sound", "angler", 3355),
                ("emote", "angler", "cheer"), ("wait", 2500), ("emote", "angler", "laugh"), ("wait", 2500),
                ("state", "angler", "fish")]),
    dict(key="bobber_lucky", model=6366, name="Fishing Bobber", kind="use", quest="ch8_pier", scale=0.35, at="bob_3",
         goal="The lucky angler's hook baited",
         beats=[("take", "fat_fish", 1), ("state", "angler", "none"), ("sound", "angler", 3355),
                ("emote", "angler", "cheer"), ("wait", 2000), ("emote", "angler", "throw"), ("sound", "angler", 120),
                ("give", "lucky_copper", 1), ("wait", 2500), ("state", "angler", "fish")]),
    # 8.11a: the post the Saltscale Oracle is tied to
    dict(key="oracle_post", model=POST, name="Bloodsail Bait Post", kind="use", quest="ch8_oracle", scale=0.8,
         goal="Saltscale Oracle cut loose",
         at="oracle_post", phase=("during", "ch8_oracle"),
         beats=[("despawn", "oracle_tied"), ("summon", "oracle_follow", "oracle_free", 420), ("wait", 700),
                ("follow", "oracle_follow"), ("emote", "oracle_follow", "spell")]),
    # 8.19: the Mosh'Ogg's stew pot, with Mrrk in it
    dict(key="stew_pot", model=216, name="Mosh'Ogg Stew Pot", kind="use", quest="ch8_pot", scale=2.2, at="ogre_pot",
         goal="Stew pot tipped over",
         beats=[("despawn", "mrrk_pot"), ("summon", "mrrk_follow", "mrrk_out", 240), ("wait", 700),
                ("follow", "mrrk_follow"), ("emote", "mrrk_follow", "rude"), ("sound", "mrrk_follow", "murloc_aggro")]),
    # 8.24: the shark-bait posts
    dict(key="bait_post", model=POST, name="Bait Post", kind="use", quest="ch8_bait", scale=0.8, goal="Murloc cut loose",
         at=["post_1", "post_2", "post_3", "post_4"], phase=("during", "ch8_bait"),
         beats=[("state", "bait_murloc", "none"), ("emote", "bait_murloc", "cheer"),
                ("sound", "bait_murloc", "splash"), ("wait", 1200), ("despawn", "bait_murloc")]),
    # 8.14: the crack in the drowned shrine's wall
    dict(key="shrine_peek", model=9463, name="Cracked Shrine Stone", kind="use", quest="ch8_dive", consumable=False,
         goal="Drowned shrine seen",
         scale=0.5, at="shrine_peek",
         beats=[("state", "ilyssa_shrine", "none"), ("object", "ch1:held_egg", "shrine_egg", 9),
                ("face", "ilyssa_shrine", "shrine_peek"), ("wait", 1500), ("cast", "ilyssa_shrine", 32992, "self"),
                ("sound", "ilyssa_shrine", "siren_hiss"), ("wait", 2500), ("emote", "ilyssa_shrine", "talk"),
                ("sound", "ilyssa_shrine", "siren_hiss"), ("emote", "sakrasis_watch", "talk"), ("wait", 5000),
                ("face", "ilyssa_shrine", "egg_net"), ("state", "ilyssa_shrine", "work")]),
    # 8.16: the diggers' shackles
    dict(key="shackle", model="World\\Expansion01\\Doodads\\Generic\\Ogre\\Chains\\OM_Chains_01.mdx", name="Digger's Shackle",
         kind="use", quest="ch8_diggers", scale=0.4, phase=DIG, goal="Digger's shackle broken",
         at=["shk_1", "shk_2", "shk_3", "shk_4", "shk_5", "shk_6"],
         beats=[("state", "digger", "none"), ("sound", "digger", 1206),
                ("emote", "digger", "question"), ("wait", 2500), ("emote", "digger", "cry"), ("sound", "digger", "murloc_fidget2"),
                ("wait", 2500), ("sound", "digger", "splash"), ("despawn", "digger")]),
    # 8.17: the carved tablets the naga dug up
    dict(key="tablet", model=5, name="Carved Gurubashi Tablet", kind="loot", loot=[("tablet", 1, 1)], quest="ch8_stones",
         scale=0.6, at=["tab_1", "tab_2", "tab_3", "tab_4", "tab_5", "tab_6", "tab_7", "tab_8"]),
    # 8.18: the egg net (Lord Sakrasis comes for it)
    dict(key="egg_net", model="World\\Expansion02\\Doodads\\Generic\\SeaVrykul\\Shore\\VRS_NetPile_01.mdx", name="Egg Net",
         kind="use", quest="ch8_sakrasis", scale=0.7, at="egg_net", phase=DIG,
         beats=[("despawn", "sakrasis_watch"), ("summon", "sakrasis", "sakrasis_fight", 150),
                ("sound", "ilyssa_shrine", "siren_hiss"), ("state", "ilyssa_shrine", "none"), ("face", "ilyssa_shrine", "player"),
                ("wait", 22000), ("cast", "ilyssa_shrine", 45776, "self"), ("sound", "ilyssa_shrine", 3076), ("wait", 1500),
                ("cast", "ilyssa_shrine", 53539, "self"), ("sound", "ilyssa_shrine", 29), ("wait", 600),
                ("despawn", "ilyssa_shrine")]),
    # 8.20: the jungle's bitter herbs
    dict(key="herb", model=677, name="Jungle Herb", kind="loot", loot=[("herb", 1, 1)], quest="ch8_cough", scale=0.6,
         at=["herb_1", "herb_2", "herb_3", "herb_4", "herb_5", "herb_6", "herb_7", "herb_8"]),
]

# -- items ---------------------------------------------------------------------------------------------

ITEMS = [
    # what quests ask for
    dict(key="rum", name="Cask of Bloodsail Rum", icon="item:2595", stack=6),
    dict(key="black_pearl", name="Black Pearl", icon="item:7971", stack=10),
    dict(key="bb_eggs", name="Basket of Glowing Eggs", icon="item:12207", description="Warm. Still warm."),
    dict(key="fat_fish", name="Fat Fish", icon="fish", stack=5),
    dict(key="lucky_copper", name="Lucky Copper", icon=55288, description="An angler threw it in for luck. You caught it."),
    dict(key="crab_claw", name="Enormous Crab Claw", icon="item:2675", description="Bigger. Definitely bigger."),
    dict(key="tablet", name="Carved Gurubashi Tablet", icon="item:6288", stack=6, description="It hums. It shouldn't hum."),
    dict(key="reef_eggs", name="The Reef's Eggs", icon="item:12207", description="Four eggs. Only four."),
    dict(key="herb", name="Jungle Herb", icon="item:3357", stack=6),
    dict(key="ledger", name="Firallon's Ledger", icon="item:7294",
         description="Names, prices, and a sea-chart pinned inside the back cover."),
    dict(key="sea_chart", name="Fizzbo's Sea-Chart", icon="item:3920",
         description="Every reef, every rock, every shark. A thumbprint over one corner."),

    # rewards (levels 41 to 46: the game's quests' greens at these levels)
    dict(key="bilge_wraps", name="Bilge-Rat Wristwraps", kind="armor:cloth:wrist", quality=2, level=41,
         stats=[("int", 6), ("spi", 5)]),
    dict(key="bilge_bracers", name="Bilge-Rat Bracers", kind="armor:leather:wrist", quality=2, level=41,
         stats=[("agi", 6), ("sta", 5)]),
    dict(key="bilge_cuffs", name="Bilge-Rat Cuffs", kind="armor:mail:wrist", quality=2, level=41,
         stats=[("str", 6), ("sta", 5)]),
    dict(key="fence_ring", name="Fizzbo's Discount Ring", kind="ring", quality=2, level=42, stats=[("agi", 5), ("sta", 5)]),
    dict(key="egg_mitts", name="Egg-Warm Mitts", kind="armor:cloth:hands", quality=2, level=43, stats=[("int", 8), ("spi", 6)]),
    dict(key="egg_grips", name="Basket-Carrier's Grips", kind="armor:leather:hands", quality=2, level=43,
         stats=[("agi", 8), ("sta", 6)]),
    dict(key="egg_gauntlets", name="Pier-Jumper's Gauntlets", kind="armor:mail:hands", quality=2, level=43,
         stats=[("str", 8), ("sta", 6)]),
    dict(key="hatchling_basket", name="Hatchling Basket", kind="bag", slots=14, level=40, icon="item:12207"),
    dict(key="saltscale_necklace", name="Saltscale Shell Necklace", kind="neck", quality=2, level=42,
         stats=[("int", 6), ("spi", 5)]),
    dict(key="oracle_tidecharm", name="Oracle's Tidecharm", kind="neck", quality=2, level=42, stats=[("agi", 6), ("sta", 5)]),
    dict(key="grudge_tooth", name="Grudge-Tooth Charm", kind="neck", quality=2, level=42, stats=[("str", 6), ("sta", 5)]),
    dict(key="spearhead_pendant", name="Spearhead Pendant", kind="neck", quality=2, level=42, stats=[("agi", 5), ("sta", 6)]),
    dict(key="zalja_knot", name="Zalja's Lucky Knot", kind="ring", quality=2, level=43, stats=[("sta", 6), ("spi", 5)]),
    dict(key="reef_spear", name="Grrmlgrrl's Reef-Coral Spear", kind="weapon:spear", quality=2, level=44,
         stats=[("str", 13), ("sta", 11)],
         description="Cut from the reef under the red sails. The same coral as the first. Longer."),
    dict(key="reef_staff", name="Reef-Coral Staff", kind="weapon:staff", quality=2, level=44, stats=[("int", 13), ("spi", 11)],
         description="Cut from the same reef as Grrmlgrrl's spear."),
    dict(key="reef_shank", name="Reef-Coral Shank", kind="weapon:dagger", quality=2, level=44, stats=[("agi", 7), ("sta", 6)],
         description="Cut from the same reef as Grrmlgrrl's spear."),
    dict(key="shrine_robe", name="Drowned Shrine Robe", kind="armor:cloth:chest", quality=2, level=45,
         stats=[("int", 12), ("sta", 9), ("spi", 8)]),
    dict(key="shrine_jerkin", name="Wellspring Diver's Jerkin", kind="armor:leather:chest", quality=2, level=45,
         stats=[("agi", 12), ("sta", 11)]),
    dict(key="shrine_hauberk", name="Naga-Scale Hauberk", kind="armor:mail:chest", quality=2, level=45,
         stats=[("str", 12), ("sta", 11)]),
    dict(key="deck_slippers", name="Deck-Swabber's Slippers", kind="armor:cloth:feet", quality=2, level=44,
         stats=[("int", 8), ("sta", 7)]),
    dict(key="deck_boots", name="Keelhaul's Sea-Boots", kind="armor:leather:feet", quality=2, level=44,
         stats=[("agi", 8), ("sta", 7)]),
    dict(key="deck_greaves", name="Boarding Greaves", kind="armor:mail:feet", quality=2, level=44,
         stats=[("str", 8), ("sta", 7)]),
    dict(key="ledger_sash", name="Fleet Master's Sash", kind="armor:cloth:waist", quality=2, level=44,
         stats=[("int", 8), ("spi", 7)]),
    dict(key="ledger_belt", name="Chart-Keeper's Belt", kind="armor:leather:waist", quality=2, level=44,
         stats=[("agi", 8), ("sta", 7)]),
    dict(key="ledger_girdle", name="Red-Sail Girdle", kind="armor:mail:waist", quality=2, level=44,
         stats=[("str", 8), ("sta", 7)]),
    dict(key="shark_tooth", name="Shark-Tooth Charm", kind="trinket", quality=2, level=43, stats=[("ap", 24)]),
    dict(key="ogre_stew", name="Mosh'Ogg Pot Stew", kind="food", level=45, icon="item:4599"),
    dict(key="voyage_mantle", name="Voyager's Kelp Mantle", kind="armor:cloth:shoulder", quality=2, level=45,
         stats=[("int", 9), ("sta", 7), ("spi", 6)]),
    dict(key="voyage_pauldrons", name="Turtle-Rider's Pauldrons", kind="armor:leather:shoulder", quality=2, level=45,
         stats=[("agi", 10), ("sta", 9)]),
    dict(key="voyage_spaulders", name="Shellback Spaulders", kind="armor:mail:shoulder", quality=2, level=45,
         stats=[("str", 10), ("sta", 9)]),
]

# -- auras ---------------------------------------------------------------------------------------------

AURAS = [
    dict(key="glowing_eggs", name="Basket of Glowing Eggs", kind="mark", seconds=900, icon=22576, visual=6589,
         text="Warm eggs in your arms. Mind them."),
    dict(key="collared", name="Collared", kind="stun", seconds=3, icon=7922, visual=2816,
         text="A goblin hand on your neck."),
]

# -- more of other chapters' people and things, and the game's creatures in the murlocs' phase -----------

SPAWNS = [
    # the core cast at the wreck
    dict(npc="ch1:elder", at="elder", phase=ELDER, facing=0.0),
    dict(npc="ch1:grrmlgrrl", at="grrmlgrrl", phase=HUB, facing=3.84, state="none"),
    dict(npc="ch1:murlorga", at="murlorga", phase=HUB, facing=1.48),
    dict(npc="ch1:blrrgl", at="blrrgl", phase=HUB, facing=2.41),
    dict(npc="ch1:glubbub", at="glubbub", phase=HUB, facing=5.5),
    dict(npc="ch1:sloshy", at="sloshy", phase=HUB, facing=3.14, wander=3.0),
    dict(npc="ch0:mrrk", at="mrrk", phase=MRRK_HOME, facing=4.71),
    dict(npc="ch0:shellback", at="shellback", phase=TURTLE, facing=1.3),
    # the hub kit: the class trainers, the trades, travel, the mailbox
    dict(npc="ch1:brrgmrk", at="brrgmrk", phase=HUB, facing=2.27),
    dict(npc="ch1:mrrgasha", at="mrrgasha", phase=HUB, facing=2.71),
    dict(npc="ch1:fizzmrgl", at="fizzmrgl", phase=HUB, facing=3.14),
    dict(npc="ch1:glubba", at="glubba", phase=HUB, facing=3.58),
    dict(npc="ch1:slubb", at="slubb", phase=HUB, facing=4.01),
    dict(npc="ch1:gurgle", at="gurgle", phase=HUB, facing=3.14),
    dict(npc="ch1:mrrlglr", at="mrrlglr", phase=HUB, facing=0.61),
    dict(npc="ch0:mrsha", at="mrsha", phase=HUB, facing=4.45),
    dict(npc="ch0:brewglub", at="brewglub", phase=HUB, facing=4.83),
    dict(npc="ch0:grrsh", at="grrsh", phase=HUB, facing=5.22),
    dict(npc="ch0:mrrsk", at="mrrsk", phase=HUB, facing=5.6),
    dict(npc="ch0:krrgl", at="krrgl", phase=HUB, facing=0.61),
    dict(npc="ch0:brrkl", at="brrkl", phase=HUB, facing=2.36),
    dict(npc="ch0:mmrglla", at="mmrglla", phase=HUB, facing=2.67),
    dict(npc="ch0:sprokgl", at="sprokgl", phase=HUB, facing=2.98),
    dict(npc="ch0:shimmrl", at="shimmrl", phase=HUB, facing=3.3),
    dict(npc="ch0:pearlmrgl", at="pearlmrgl", phase=HUB, facing=3.61),
    dict(npc="ch0:scrawlgl", at="scrawlgl", phase=HUB, facing=3.93),
    dict(npc="ch0:fnrrgl", at="fnrrgl", phase=HUB, facing=1.05),
    dict(npc="ch0:caller", at="caller", phase=HUB, facing=1.92),
    dict(object="ch0:mailbox", at="mailbox", phase=HUB, facing=1.6),
    dict(object="ch1:cookpot", at="pot", phase=HUB),
    dict(object="ch1:hollow_log", at="blrrgl_log", phase=HUB, facing=2.4),
    dict(object="ch1:altar", at="altar", phase=HUB),
    dict(object="ch1:smoke_rack", at="rack", phase=HUB, facing=0.8),
    dict(object="ch1:barrel", at="barrel_hub", phase=HUB),
    # the hatchlings at home, from 8.09
    dict(npc="hatchling", at=["hatch_r0", "hatch_r1", "hatch_r2"], phase=HATCHED, wander=2.0),
    # Booty Bay: Fizzbo under the pier; Zalja's boat in port from 8.09; the eggs in the kitchen's basket
    dict(npc="ch0:fizzbo", at="fizzbo_den", facing=1.0),
    dict(object="crates", at="fizzbo_crate", facing=0.4),
    dict(npc="ch0:zalja", at="zalja_dock", phase=HATCHED, facing=0.0),
    dict(object="rowboat", at="zalja_boat", phase=HATCHED, facing=1.6),
    dict(object="ch1:held_egg", at="basket_eggs", phase=KITCHEN),
    # the Saltscale's beach
    dict(object="hut", at=["sb_hut", "sb_hut2"], facing=3.6),
    dict(object="campfire", at="sb_v"),
    # the naga's dig: the eggs in the net, the naga's crates and torches
    dict(object="ch1:eggs", at="egg_net", phase=DIG),
    dict(object="ch1:naga_crates", at="statue_c", phase=DIG),
    # the Saltscale who stalk the wreck (8.11b), in the murlocs' phase while it's in the log
    dict(npc=871, at=["amb_1", "amb_3", "amb_5", "amb_7", "amb_9", "amb_11"], phase=("during", "ch8_grudge"), wander=5.0,
         respawn=45),
    dict(npc=879, at=["amb_2", "amb_4", "amb_6", "amb_8", "amb_13"], phase=("during", "ch8_grudge"), wander=5.0, respawn=45),
    dict(npc=873, at=["amb_10", "amb_12", "amb_14"], phase=("during", "ch8_grudge"), wander=4.0, respawn=45),
    # the Mosh'Ogg who guard their cook-pot
    dict(npc=709, at=["ogre_g1", "ogre_g2", "ogre_g3"], wander=4.0, respawn=120),
]

GRAVEYARDS = [
    dict(at="graveyard", name="the wreck of the Lucky Cod", phase=HUB, facing=0.6),
]

# -- the quests ------------------------------------------------------------------------------------------

QUESTS = [
    # the landing: the Lucky Cod becomes the tribe's (the hub kit appears with its reward)
    dict(key="ch8_arrival", title="The Lucky Cod", giver="ch1:elder", ender="ch1:elder", level=40, min=38, xp=8,
         tone="serious", prev="ch7:ch7_end", explore="hold", radius=8,
         goal="Go into the hold of the wrecked ship on the Wild Shore, south of Booty Bay, and see that it's safe.",
         text="Mm. Black sand. Red sails. And there... a dry-skin boat, on its side, belly up like a dead fish. "
              "Its belly is a house, little one. Go in. See if it bites. If it doesn't bite... we live in it.",
         progress="Did it bite?",
         reward="Empty. Dry. Only crabs and a bad smell. Good! Then it is ours... until the sea says otherwise. "
                "Call them in. Call everyone!",
         details=["talk", "point"], reward_emotes=["cheer", "roar"],
         accept=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200),
                 ("face", "self", "wreck"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget"), ("wait", 1800),
                 ("face", "self", "player"), ("emote", "self", "attack"), ("sound", "self", 417), ("wait", 600),
                 ("emote", "self", "attack"), ("sound", "self", 417), ("wait", 1200), ("sound", "self", 5736),
                 ("emote", "self", "no"), ("wait", 2000), ("face", "self", "hub")],
         complete=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                   ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1000),
                   ("yell", "self", "Saltscar! Here! Home... for now!", "roar", "murloc_aggro"), ("music", 6837),
                   ("wait", 3000), ("emote", "self", "cheer"), ("sound", "self", "murloc_fidget")],
         poi=["hold"]),

    # 8.01: red sails on the horizon
    dict(key="ch8_sails", title="Red Sails on the Horizon", giver="ch1:elder", ender="ch1:grrmlgrrl", level=40, xp=8,
         tone="serious", prev="ch8_arrival", objects=[("lookout_north", 1), ("lookout_west", 1), ("lookout_south", 1)],
         goal="Watch the Bloodsail ships off the Wild Shore from the three driftwood lookouts on the islets: north of the "
              "ships, between the two western ships, and south by the third.",
         text="Three ships. Red sails. A skull on every sail... I have seen that skull before, on a crate, in a cold "
              "place far to the north. Watch them, little one. From 3 places. Low. Quiet. Count what they carry. "
              "Then tell Grrmlgrrl.",
         progress="...Well?",
         reward="3 ships. Crates going off, never coming on. Mm. Krrgl! Come. Look.",
         details=["talk", "point", "no"], reward_emotes=["point", "roar"],
         accept=[("face", "self", "ships_view"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1800), ("emote", "self", "point"), ("wait", 1500), ("sound", "self", 5736), ("wait", 1000),
                 ("face", "self", "player"), ("emote", "self", "no"), ("wait", 1500), ("emote", "self", "attack"),
                 ("sound", "self", 417), ("wait", 1500), ("face", "self", "hub")],
         complete=[("move", "self", "grrm_lie", "walk"), ("wait", 5500), ("face", "self", "ships_view"),
                   ("state", "self", "sleep"), ("wait", 3500), ("state", "self", "none"), ("emote", "self", "point"),
                   ("sound", "self", "murloc_fidget2"), ("object", "crate_scrap", "krrgl_front", 30),
                   ("emote", "ch0:krrgl", "kneel"), ("sound", "ch0:krrgl", 1194), ("wait", 1500), ("emote", "ch0:krrgl", "attack"),
                   ("wait", 900), ("emote", "ch0:krrgl", "attack"), ("wait", 1200), ("emote", "ch0:krrgl", "yes"), ("wait", 3000),
                   ("move", "self", "grrmlgrrl", "walk"), ("wait", 5500), ("face", "self", "hub")],
         poi=["lookout_north", "lookout_west", "lookout_south"]),

    # 8.02: bilge rats
    dict(key="ch8_bilge", title="Bilge Rats", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=40, xp=8, tone="serious",
         path="hero", prev="ch8_sails", kill=[(4505, 8), (4506, 4)], rep=[(21, 350)],
         goal="Kill 8 Bloodsail Deckhands and 4 Bloodsail Swabbies aboard the Bloodsail ships off the Wild Shore.",
         text="Ships. I hate ships. They float where fish should swim. The small ones scrub the decks and carry the "
              "crates... 12 of them. The deckhands and the swabbies. Fewer hands, fewer crates. Go.",
         progress="Still floating?",
         reward="12. Good. The ships are lighter. And the goblins in the cliff-town watched you do it. "
                "They like it when the red sails lose.",
         details=["talk", "attack"], reward_emotes=["flex", "talk"], choice=["bilge_wraps", "bilge_bracers", "bilge_cuffs"],
         accept=[("move", "self", "grrm_draw", "walk"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "flag_drawing", "grrm_draw2", 30), ("sound", "self", 1194), ("wait", 2000),
                 ("emote", "self", "rude"), ("sound", "self", 1197), ("wait", 1500), ("face", "self", "ships_view"),
                 ("emote", "self", "point"), ("wait", 1500), ("move", "self", "grrmlgrrl", "walk"), ("wait", 1500),
                 ("face", "self", "hub")],
         complete=[("emote", "self", "flex"), ("sound", "self", 417), ("wait", 900), ("emote", "self", "flex"),
                   ("sound", "self", 417), ("wait", 900), ("face", "self", "player"), ("emote", "self", "point"),
                   ("sound", "self", "murloc_fidget2")]),

    # 8.03: rum for the wounded
    dict(key="ch8_rum", title="Rum for the Wounded", giver="ch1:slubb", ender="ch1:slubb", level=40, xp=8, tone="funny",
         prev="ch8_sails", items=[("rum", 6)], rep=[(21, 150)],
         goal="Take 6 Casks of Bloodsail Rum from the Bloodsail camps: east of the wreck, on the north beach, and on the "
              "sandbar by their ships.",
         text="Cuts. Scrapes. Crab-pinches. Everyone came off the turtle bleeding a little. The dry-skins have a brown "
              "water that burns... burns the bad out of a cut. 6 casks, from the red-sail camps. Don't drink it. Don't.",
         progress="Hold still. HOLD... no. The casks first.",
         reward="Ahh. Smell it. Terrible. Perfect. Watch... a drop on the cut... ow. Ow ow ow. Good! It works!",
         details=["talk", "no"], reward_emotes=["yes", "laugh"],
         accept=[("face", "self", "rum_east"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "eat"), ("wait", 1200), ("emote", "self", "no"), ("sound", "self", "murloc_fidget"),
                 ("wait", 1500), ("emote", "self", "talk")],
         complete=[("object", "crates", "slubb_front", 30), ("emote", "self", "kneel"), ("sound", "self", 1197),
                   ("wait", 1500), ("emote", "self", "wound"), ("sound", "self", "murloc_wound"), ("wait", 1500),
                   ("emote", "self", "yes"), ("move", "ch1:blrrgl", "slubb_front", "run"), ("wait", 4000),
                   ("emote", "ch1:blrrgl", "eat"), ("sound", "ch1:blrrgl", 1197), ("wait", 1500), ("visual", "ch1:blrrgl", 6431),
                   ("emote", "self", "exclamation"), ("wait", 6000), ("move", "ch1:blrrgl", "blrrgl", "walk")],
         poi=["rum_east", "rum_4", "rum_7"]),

    # 8.19: Mrrk in the pot (early: Mrrk went for crabs and didn't come back)
    dict(key="ch8_pot", title="Mrrk in the Pot", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=41, xp=8, tone="funny",
         path="hero", prev="ch8_arrival", objects=[("stew_pot", 1)],
         goal="Tip over the Mosh'Ogg stew pot at the foot of the hills east along the beach and get Mrrk out. "
              "The ogres guarding it won't like it.",
         text="Mrrk went for crabs. Mrrk didn't come back. ...I smelled smoke. Ogre smoke. Onion smoke. On the hills "
              "east, along the beach. Get him out. He'll hate that it was you. Good.",
         progress="...",
         reward="Hm. Wet. Angry. Alive. ...He smells like onions.",
         details=["talk", "point", "laugh"], reward_emotes=["laugh", "flex"], rewards=["ogre_stew"],
         accept=[("face", "self", "ogre_dir"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1500), ("emote", "self", "eat"), ("wait", 1500), ("emote", "self", "roar"),
                 ("sound", "self", "murloc_aggro"), ("wait", 1800), ("face", "self", "player"), ("emote", "self", "laugh")],
         complete=[("move", "mrrk_follow", "mrrk", "walk"), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"),
                   ("wait", 1500), ("emote", "mrrk_follow", "rude"), ("sound", "mrrk_follow", "murloc_aggro"),
                   ("wait", 1500), ("emote", "self", "flex"), ("wait", 900), ("emote", "self", "flex"), ("wait", 4000),
                   ("despawn", "mrrk_follow")],
         poi=["ogre_pot"]),

    # 8.23: polly wants a mrgl
    dict(key="ch8_parrot", title="Polly Wants a Mrgl", giver="ch1:blrrgl", ender="ch1:blrrgl", level=41, xp=8, tone="funny",
         prev="ch8_bilge", interact=[("parrot", "Grab the bird.")], interact_goal="Bloodsail parrot grabbed",
         interact_beats=[("sound", "self", 4005), ("say", "self", "Mrgl! Mrgl! Mrgl!", None, 4004), ("wait", 1500),
                         ("despawn", "self")],
         goal="Grab a Bloodsail parrot from the Bloodsail camp on the north beach, a short way north of the wreck.",
         text="The red-sail ones have birds. Talking birds! On their shoulders! Squawk, squawk. I want one. I NEED one. "
              "In the camp up the beach, north. 1 bird. A bird that talks! Imagine!",
         progress="Bird? Bird?",
         reward="Say it! Say it! ...It said Mrgl! It said MRGL! Oh, it's perfect. Here. You keep it. No. Yes. "
                "You keep it. It likes you better. Hmph.",
         details=["laugh", "beg"], reward_emotes=["cheer", "laugh"], rewards=[8494],
         accept=[("face", "self", "look_left"), ("wait", 900), ("face", "self", "look_right"), ("wait", 900),
                 ("face", "self", "player"), ("emote", "self", "flex"), ("sound", "self", 4005), ("wait", 1200),
                 ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1200),
                 ("face", "self", "north_camp"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "beg")],
         complete=[("sound", "self", 4004), ("emote", "self", "cheer"), ("wait", 1200),
                   ("say", "self", "Mrgl!", None, 4005), ("wait", 1500), ("emote", "self", "laugh"),
                   ("sound", "self", "murloc_fidget2")],
         poi=["parrot"]),

    # 8.04: the crate marks (the clutch was split)
    dict(key="ch8_crates", title="The Crate Marks", giver="ch0:krrgl", ender="ch1:elder", level=41, xp=8, tone="boring",
         prev="ch8_sails", objects=[("bloodsail_crate", 6)],
         goal="Look closely at the marks on 6 Bloodsail crates on the islets around their ships, then go back to the "
              "Elder at the wreck with Krrgl's Scrap of Egg-Jelly.",
         text="Crates. Crates crates crates. Every one has the skull. And under the skull... something else. Little "
              "marks. Go and look at 6 of them, close. And take this... the scrap of egg-jelly from the cold bay. I kept "
              "one. Show the Elder both.",
         progress="The marks? What marks?",
         reward="A coin... and a trident. Coin, trident. Coin, trident. ...Mm. Half here, half there. They split our "
                "children like a catch, little one. Half for the goblins. Half for the long ones.",
         details=["talk", "question"], reward_emotes=["talk", "bow"],
         accept=[("object", "crate_scrap", "krrgl_front", 30), ("emote", "self", "kneel"), ("sound", "self", 1194),
                 ("wait", 1500), ("emote", "self", "attack"), ("sound", "self", 4614), ("wait", 1200),
                 ("face", "self", "player"), ("emote", "self", "talk"), ("give", "ch4:egg_jelly", 1), ("sound", "self", 1197),
                 ("wait", 1500), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "question"),
                 ("sound", "self", "murloc_fidget2")],
         complete=[("move", "self", "elder_draw", "walk"), ("wait", 2500), ("emote", "self", "kneel"),
                   ("object", "coins", "draw_a", 40), ("sound", "self", 120), ("wait", 1500),
                   ("object", "ch1:sand_spear", "draw_b", 40), ("sound", "self", 1194), ("wait", 1500),
                   ("move", "ch0:krrgl", "draw_k", "walk"), ("wait", 2000), ("emote", "ch0:krrgl", "kneel"),
                   ("object", "pebbles", "draw_a2", 40), ("sound", "ch0:krrgl", 1194), ("wait", 900),
                   ("emote", "ch0:krrgl", "kneel"), ("object", "pebbles", "draw_b2", 40), ("wait", 1200),
                   ("take", "ch4:egg_jelly", 1), ("object", "ch1:sand_egg", "draw_mid", 40), ("emote", "ch0:krrgl", "yes"),
                   ("wait", 1500), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "point"), ("wait", 1500),
                   ("emote", "self", "bow"), ("sound", "self", 5736), ("music", 6074), ("wait", 4000),
                   ("move", "ch0:krrgl", "krrgl", "walk"), ("move", "self", "elder", "walk"), ("wait", 2500),
                   ("face", "self", "hub"), ("face", "ch0:krrgl", "hub")],
         poi=["crate_1", "crate_4", "crate_6"]),

    # 8.11a: the Saltscale Oracle (hero)
    dict(key="ch8_oracle", title="The Saltscale Oracle", giver="ch1:elder", ender="saltscale_chief", level=41, xp=8,
         tone="serious", path="hero", prev="ch8_pot", exclusive=2, objects=[("oracle_post", 1)], explore="sb_v", radius=14,
         goal="Cut the Saltscale Oracle loose from the bait post in the Bloodsail camp just east of the wreck, and walk "
              "her home to the Saltscale's beach farther east along the shore.",
         text="The Saltscale, down the beach... they hiss at us. They think we are the red sails' dogs, because we came "
              "on a dry-skin boat. Hm. Their oracle is tied to a post in the red-sail camp east of here. Cut her loose. "
              "Walk her home. Slowly. Old ones walk slowly.",
         progress="Back. BACK! ...Who is that behind you?",
         reward="Our oracle. OUR oracle! They said the Saltscar were the dry-skins' dogs. Dogs don't bring oracles home. "
                "...Lower the spears. Lower them.",
         details=["talk", "point"], reward_emotes=["bow", "talk"], choice=["saltscale_necklace", "oracle_tidecharm"],
         accept=[("face", "self", "saltscale_dir"), ("emote", "self", "point"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1800), ("face", "self", "rum_east"), ("emote", "self", "point"), ("wait", 1500),
                 ("face", "self", "player"), ("emote", "self", "talk"), ("wait", 1200), ("sound", "self", 5736)],
         complete=[("emote", "spear_a", "kneel"), ("sound", "spear_a", "murloc_fidget"), ("wait", 1500),
                   ("emote", "spear_b", "kneel"), ("sound", "spear_b", "murloc_fidget"), ("wait", 1500),
                   ("emote", "spear_c", "kneel"), ("sound", "spear_c", "murloc_fidget"), ("wait", 1500),
                   ("emote", "self", "bow"), ("music", 4454), ("move", "oracle_follow", "sb_hut", "walk"),
                   ("emote", "oracle_follow", "spell"), ("wait", 8000), ("despawn", "oracle_follow")],
         poi=["oracle_post", "sb_v"]),

    # 8.11b: the Saltscale grudge (a menace to murlocs)
    dict(key="ch8_grudge", title="The Saltscale Grudge", giver="ch0:mrrk", ender="ch0:mrrk", level=41, xp=8, tone="serious",
         path="menace", prev="ch8_pot", exclusive=2, kill=[(871, 6), (879, 4), (873, 2)],
         goal="Kill 6 Saltscale Warriors, 4 Saltscale Hunters and 2 Saltscale Oracles skulking on the beach east of the wreck.",
         text="They hissed at me. At ME. Saltscale. Fish-men with spears, sneaking round our wreck at night. I say no "
              "more sneaking. 12 of them, on the beach east of here. You're good at this, right? Everyone says you're "
              "good at this.",
         progress="Only that many? I'd have done more.",
         reward="12. ...Good. Good. They won't sneak again. ...The Elder won't look at me. Why won't he look at me?",
         details=["flex", "point"], reward_emotes=["flex", "shy"], choice=["grudge_tooth", "spearhead_pendant"],
         accept=[("emote", "self", "kneel"), ("object", "ch1:sand_mound", "mrrk_draw", 30), ("sound", "self", 1194),
                 ("wait", 1800), ("emote", "self", "attack"), ("sound", "self", 417), ("wait", 700),
                 ("emote", "self", "attack"), ("sound", "self", 417), ("wait", 1000), ("face", "ch1:elder", "mrrk_draw"),
                 ("wait", 1500), ("emote", "ch1:elder", "no"), ("move", "ch1:elder", "elder_away", "walk"),
                 ("face", "self", "saltscale_dir"), ("emote", "self", "point"), ("wait", 1200), ("face", "self", "player"),
                 ("emote", "self", "flex"), ("wait", 9000), ("move", "ch1:elder", "elder", "walk"), ("wait", 3500),
                 ("face", "ch1:elder", "hub")],
         complete=[("emote", "self", "flex"), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"),
                   ("wait", 2500), ("face", "self", "elder"), ("emote", "self", "question"), ("wait", 2500),
                   ("emote", "self", "shy"), ("wait", 2000), ("face", "self", "hub")]),

    # 8.24: shark bait
    dict(key="ch8_bait", title="Shark Bait", giver="ch1:mrrgasha", ender="ch1:mrrgasha", level=42, xp=8, tone="serious",
         path="hero", prev="ch8_bilge", objects=[("bait_post", 4)], time=120,
         goal="Within 2 minutes, cut loose the 4 murlocs tied to the bait posts in the shallows of the Bloodsail camp on "
              "the north beach, before the shark gets them. Mind the shark.",
         text="Smell that? Blood in the water. The red-sail ones tie our kind to posts by their camp, up the beach. "
              "Bait. For sharks. For fun. 4 of them. Cut them loose. Quick... the fin is already circling.",
         progress="Quick! QUICK!",
         reward="They came in. All 4. They swam past me without looking back... that's right. That's how you swim "
                "away from a post. You don't look back.",
         details=["exclamation", "point"], reward_emotes=["salute", "yes"], rewards=["shark_tooth"],
         accept=[("sound", "self", "splash"), ("emote", "self", "exclamation"), ("wait", 1200),
                 ("face", "self", "north_camp"), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "attack"),
                 ("sound", "self", 1206), ("wait", 1200), ("face", "self", "player"), ("emote", "self", "exclamation")],
         complete=[("emote", "self", "salute"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("emote", "self", "yes"),
                   ("emote", "self", "eat")],
         poi=["post_1", "post_4"]),

    # 8.05: the kitchen window
    dict(key="ch8_window", title="The Kitchen Window", giver="ch1:elder", ender="ch1:murlorga", level=41, xp=8,
         tone="serious", prev="ch8_crates", explore="kitchen_window", radius=8,
         goal="Sneak up into Booty Bay to the Salty Sailor Tavern above the harbour, and look into its kitchen corner by "
              "the stove. The goblins won't attack you, but they won't like it.",
         text="The coin is the cliff-town's. The goblins. Goblins buy everything... and goblins eat everything. Go up "
              "into their town, little one, where they eat and drink and shout. Find where they cook. Look. Only look.",
         progress="Well? WELL?",
         reward="In a pot. In a POT. For a special... our little ones... our clutch, for a goblin's supper...",
         details=["talk", "eat", "no"], reward_emotes=["cry", "roar"],
         accept=[("face", "self", "booty_dir"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "eat"), ("wait", 1500), ("emote", "self", "no"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1500), ("sound", "self", 5736), ("face", "self", "hub")],
         complete=[("state", "self", "none"), ("emote", "self", "attack"), ("wait", 1500), ("sound", "self", 1198),
                   ("sound", "self", 3202), ("object", "broken_ladle", "murlorga_feet", 45), ("wait", 1200),
                   ("emote", "self", "cry"), ("sound", "self", "murloc_wound"), ("wait", 2500), ("emote", "self", "roar"),
                   ("sound", "self", "murloc_aggro"), ("wait", 3000), ("state", "self", "work")],
         poi=["kitchen_window"]),

    # 8.06: Fizzbo the Fence (after the Bloodsail's losses have made the goblins Neutral)
    dict(key="ch8_fence", title="Fizzbo the Fence", giver="ch1:blrrgl", ender="ch0:fizzbo", level=41, xp=8, tone="funny",
         prev="ch8_window", rep=[(21, 250)],
         goal="Find Fizzbo Gillgrin, the goblin fence who lives on the sand under Booty Bay's lowest pier, by the "
              "south cliff.",
         text="Psst. Psst! Under the goblin town, between its legs, where it's wet and dark... there's a goblin who "
              "buys things nobody should sell. I know him. Well. I know the smell of him. Go. Goblins love a shiny.",
         progress="Yeah? Whaddaya got?",
         reward="A fish-man! Under MY pier! Ha! You got the look of a customer. Eggs, huh? I know a guy. I know every "
                "guy. It'll cost ya.",
         details=["beg", "laugh"], reward_emotes=["beg", "point"],
         accept=[("face", "self", "look_left"), ("wait", 900), ("face", "self", "look_right"), ("wait", 900),
                 ("move", "self", "blrrgl_lean", "walk"), ("emote", "self", "beg"), ("sound", "self", "murloc_fidget"),
                 ("wait", 1500), ("emote", "self", "laugh"), ("face", "self", "booty_dir"), ("emote", "self", "point"),
                 ("wait", 1500), ("move", "self", "blrrgl", "walk")],
         complete=[("emote", "self", "beg"), ("sound", "self", 120), ("wait", 1000), ("sound", "self", 895),
                   ("object", "coins", "fizzbo_front", 25), ("object", "pearl_prop", "fizzbo_front", 25),
                   ("emote", "self", "talk"), ("wait", 1500), ("face", "self", "tavern_up"), ("emote", "self", "point"),
                   ("wait", 1800), ("face", "self", "player"), ("emote", "self", "laugh")],
         poi=["fizzbo_den"]),

    # 8.07: black pearls (Fizzbo's price)
    dict(key="ch8_pearls", title="Black Pearls", giver="ch0:fizzbo", ender="ch0:fizzbo", level=41, xp=8, tone="boring",
         path="hero", prev="ch8_fence", items=[("black_pearl", 10)],
         goal="Dive for 10 Black Pearls in the giant clams on the reef north of the wreck, off the coast between the Wild "
              "Shore and Booty Bay's mouth.",
         text="Here's the deal, fish-face. The cook upstairs paid good coin for them eggs. You wanna buy 'em back? "
              "Black pearls. 10 of 'em. The big clams on the reef north of your wreck grow 'em. 10. I can count, ya know.",
         progress="That ain't 10. I'm lookin' right at it. That ain't 10.",
         reward="1... real. 2... real. 3, 4... real, real... they're ALL real. Nobody brings me real! Okay. Okay. "
                "A deal's a deal.",
         details=["talk", "beg"], reward_emotes=["beg", "laugh"], rewards=["fence_ring"],
         accept=[("emote", "self", "talk"), ("emote", "self", "beg"), ("sound", "self", 895), ("wait", 1500),
                 ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "question")],
         complete=[("emote", "self", "eat"), ("sound", "self", 1221), ("wait", 1200), ("emote", "self", "eat"),
                   ("sound", "self", 1221), ("wait", 900), ("emote", "self", "eat"), ("sound", "self", 1221), ("wait", 900),
                   ("emote", "self", "talk"), ("wait", 1200), ("emote", "self", "question"), ("wait", 1200),
                   ("move", "self", "fizzbo_run", "run"), ("wait", 2500), ("emote", "self", "cheer"), ("sound", "self", 895),
                   ("wait", 1200), ("move", "self", "fizzbo_den", "walk"), ("wait", 2500), ("face", "self", "player")],
         poi=["reef"]),

    # 8.08a: a fair trade (hero)
    dict(key="ch8_trade", title="A Fair Trade", giver="ch0:fizzbo", ender="ch1:murlorga", level=42, xp=8, tone="funny",
         path="hero", prev="ch8_pearls", exclusive=1, rep=[(21, 1000)],
         interact=[("porter", "Nod. Time to go.")], interact_goal="Gizzle rolling his barrel",
         interact_beats=[("emote", "self", "yes"), ("sound", "self", 11800), ("follow", "self"),
                         ("object", "fish_barrel", "barrel_spot", 180), ("wait", 12000), ("sound", "self", 11800),
                         ("wait", 12000), ("sound", "self", 11800), ("wait", 18000), ("despawn", "self")],
         items=[("bb_eggs", 1)],
         goal="Nod to Gizzle the porter at the north end of Booty Bay's lowest pier, walk him and his barrel past the "
              "Bruiser to the pier's south end, and tip the barrel into the bay. Bring the eggs home to Murlorga.",
         text="Plan's simple. Gizzle rolls a barrel of fish outta the kitchen. Under the fish... your eggs. Nobody looks "
              "under fish. You walk with him to the end of the pier, nice and slow, and you tip it in. The bay does "
              "the rest. Gizzle's by the bait shop.",
         progress="Where are they? Where?",
         reward="Oh... oh, look at them. Warm. Still warm. Shh, shh, little ones. Murlorga has you. Murlorga has you.",
         details=["beg", "point"], reward_emotes=["cry", "kiss"], choice=["egg_mitts", "egg_grips", "egg_gauntlets"],
         accept=[("emote", "self", "beg"), ("sound", "self", 895), ("wait", 1200), ("emote", "self", "point"),
                 ("wait", 1500), ("say", "self", "Nice and slow, fish-face. Nice and slow.", "talk"), ("wait", 1500),
                 ("emote", "self", "bow")],
         complete=[("state", "self", "none"), ("unaura", "player", "glowing_eggs"), ("object", "ch1:basket", "basket_spot", 90),
                   ("object", "ch1:held_egg", "basket_spot", 90), ("emote", "self", "kneel"), ("music", 4454),
                   ("sound", "self", "murloc_fidget2"), ("wait", 2500), ("emote", "self", "cry"), ("wait", 2000),
                   ("sound", "self", "baby_murloc"), ("emote", "self", "exclamation"), ("wait", 1500),
                   ("sound", "self", "baby_murloc"), ("emote", "self", "cheer"), ("wait", 4000), ("state", "self", "work")],
         poi=["porter_post", "barrel_spot"]),

    # 8.08b: the kitchen job (menace)
    dict(key="ch8_heist", title="The Kitchen Job", giver="ch1:blrrgl", ender="ch1:murlorga", level=42, xp=8, tone="funny",
         path="menace", prev="ch8_fence", exclusive=1, rep=[(21, -1500)], time=180,
         items=[("bb_eggs", 1)], explore="the_jump", radius=10,
         goal="Within 3 minutes: get into the Salty Sailor Tavern's kitchen corner in Booty Bay, grab the basket of "
              "glowing eggs by the stove, and jump from the tavern into the bay below. The cook and the kitchen's "
              "Bruiser grab whoever comes close.",
         text="Pay? PAY? For our own eggs? Hee... no. No no. The cook turns his back to stir. Stir, stir, stir. In "
              "through the inn, grab the basket, out, and JUMP. Into the water. Goblins don't swim. 3 minutes, before "
              "the whole town wakes up.",
         progress="Did you get them? Are they hurt?",
         reward="You... jumped. Off the goblin town. With the eggs. ...Oh, come here. Look at them. Warm. Still warm. "
                "Shh, little ones. Murlorga has you.",
         details=["laugh", "point"], reward_emotes=["no", "cry"], choice=["egg_mitts", "egg_grips", "egg_gauntlets"],
         accept=[("face", "self", "look_left"), ("wait", 800), ("face", "self", "look_right"), ("wait", 800),
                 ("face", "self", "player"), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget"), ("wait", 1200),
                 ("emote", "self", "attack"), ("wait", 1200), ("face", "self", "booty_dir"), ("emote", "self", "point"),
                 ("wait", 1200), ("jump", "self", "blrrgl_hop"), ("sound", "self", "splash_small"), ("wait", 2500),
                 ("move", "self", "blrrgl", "walk")],
         complete=[("state", "self", "none"), ("unaura", "player", "glowing_eggs"), ("emote", "self", "no"),
                   ("wait", 1500), ("object", "ch1:basket", "basket_spot", 90), ("object", "ch1:held_egg", "basket_spot", 90),
                   ("emote", "self", "kneel"), ("music", 4454), ("wait", 2500), ("emote", "self", "cry"),
                   ("sound", "self", "baby_murloc"), ("wait", 2000), ("emote", "self", "exclamation"),
                   ("sound", "self", "baby_murloc"), ("wait", 4000), ("state", "self", "work")],
         poi=["egg_basket", "the_jump"]),

    # 8.09: hatchlings! (after either way the eggs came home)
    dict(key="ch8_hatch", title="Hatchlings!", giver="ch1:murlorga", ender="ch1:murlorga", level=42, xp=8,
         tone="funny", prev_any=["ch8_trade", "ch8_heist"], explore="tidepool", radius=10,
         goal="Three eggs hatched on the way home, and the hatchlings follow you everywhere: take them for their first "
              "swim in the tide pool on the beach east of the wreck, then bring them back to Murlorga.",
         text="Three of them hatched! On the way home! And look... look how they look at you. They think you're their "
              "mother. Ha! Well, mother... they need a swim. Their first swim. The tide pool, by the beach. All 3. "
              "Then bring them back to me.",
         progress="Are they wet? Are they all still there? 1, 2, 3?",
         reward="They won't let go of you. Look at them! Here, little ones... fish! Fish! ...Ha! Fish wins. Fish always wins.",
         details=["cheer", "point"], reward_emotes=["laugh", "cheer"], rewards=["hatchling_basket"],
         accept=[("state", "self", "none"), ("emote", "self", "cheer"), ("sound", "self", "baby_murloc"),
                 ("summon", "hatch_a", "hatch_s1", 420), ("summon", "hatch_b", "hatch_s2", 420),
                 ("summon", "hatch_c", "hatch_s3", 420), ("wait", 900), ("follow", "hatch_a"), ("follow", "hatch_b"),
                 ("follow", "hatch_c"), ("sound", "hatch_a", "baby_murloc"), ("wait", 1500), ("emote", "self", "laugh"),
                 ("wait", 1200), ("face", "self", "tidepool"), ("emote", "self", "point"), ("wait", 2000),
                 ("face", "self", "pot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "beg"), ("wait", 1200),
                   ("object", "ch1:big_fish", "bribe_fish", 25), ("sound", "self", 973), ("wait", 500),
                   ("sound", "self", 973), ("move", "hatch_a", "bribe_fish", "run"), ("move", "hatch_b", "bribe_fish2", "run"),
                   ("move", "hatch_c", "bribe_fish3", "run"), ("wait", 3000), ("emote", "hatch_a", "eat"),
                   ("emote", "hatch_b", "eat"), ("emote", "hatch_c", "eat"), ("sound", "hatch_b", "baby_murloc"),
                   ("emote", "self", "laugh"), ("wait", 4000), ("despawn", "hatch_a"), ("despawn", "hatch_b"),
                   ("despawn", "hatch_c"), ("face", "self", "pot"), ("state", "self", "work")],
         poi=["tidepool"]),

    # 8.10: under the pier (Fizzbo's)
    dict(key="ch8_pier", title="Under the Pier", giver="ch0:fizzbo", ender="ch0:fizzbo", level=42, xp=8, tone="funny",
         path="hero", prev="ch8_hatch", objects=[("bobber", 4), ("bobber_lucky", 1)], rep=[(21, 350)],
         goal="Swim under Booty Bay's lowest pier and hang a Fat Fish on each of the 5 sulking anglers' hooks: their "
              "bobbers float in the water off the pier's edge.",
         text="My boys on the pier ain't caught a thing in a week. Bad luck. Bad luck's bad for business. You swim "
              "under, right? Hang a fish on each hook, nice and quiet. 5 hooks. They think the luck's back... and the "
              "luck IS back. That's how luck works.",
         progress="Them boys still sulkin'?",
         reward="Listen to 'em! Whoopin' like they caught a shark! Luck's back, business is back. You're good for "
                "business, fish-face. Don't tell nobody.",
         details=["talk", "point"], reward_emotes=["cheer", "laugh"],
         accept=[("give", "fat_fish", 5), ("emote", "self", "point"), ("wait", 1500), ("emote", "self", "cry"),
                 ("wait", 1500), ("emote", "self", "laugh"), ("sound", "self", 895)],
         complete=[("emote", "self", "cheer"), ("sound", "self", 120), ("wait", 1200), ("emote", "self", "beg"),
                   ("wait", 1200), ("emote", "self", "laugh")],
         poi=["bob_3"]),

    # 8.12: Zalja in port
    dict(key="ch8_zalja", title="Zalja in Port", giver="ch1:blrrgl", ender="ch0:zalja", level=42, xp=8, tone="funny",
         path="hero", prev="ch8_hatch", rep=[(530, 750)],
         goal="Find the Horde fishing boat tied up at Booty Bay's lowest pier, and whoever is laughing on it.",
         text="A boat came in. Little boat. Fish boat. Horde boat! And on it... a big laugh. BIG laugh. I heard it from "
              "here! I know that laugh. You know that laugh. Go see.",
         progress="Hah!",
         reward="HAH! Da little fishman! All da way out here! Look at you, mon, you grow! Here, catch! ...Wait. Dem "
                "little ones at your camp? Dey yours? HAHAHA!",
         details=["laugh", "point"], reward_emotes=["laugh", "point"],
         accept=[("face", "self", "booty_dir"), ("emote", "self", "laugh"), ("sound", "self", "murloc_fidget2"),
                 ("wait", 1500), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "laugh")],
         complete=[("emote", "self", "laugh"), ("sound", "self", 6958), ("wait", 1500), ("emote", "self", "laugh"),
                   ("sound", "self", 6958), ("wait", 1200), ("emote", "self", "throw"), ("object", "ch1:big_fish", "zalja_front", 20),
                   ("give", 6887, 1), ("wait", 2000), ("emote", "self", "point"), ("wait", 900), ("emote", "self", "laugh"),
                   ("sound", "self", 6958)],
         poi=["zalja_dock"]),

    # 8.13: Zalja's bet
    dict(key="ch8_bet", title="Zalja's Bet", giver="ch0:zalja", ender="ch0:zalja", level=43, xp=8, tone="funny", path="hero",
         prev="ch8_zalja", items=[("crab_claw", 1)], drops={"crab_claw": [(2544, 30)]}, rep=[(530, 750)],
         goal="Bring Zalja an Enormous Crab Claw from the Southern Sand Crawlers on the Wild Shore.",
         text="Dis goblin, he say his cousin catch a crab claw dis big. Dis BIG! Zalja say, Zalja's fishman friend bring "
              "one bigger. Da sand crawlers on da beach by your wreck, mon. Bring me da biggest claw on dis coast. Just 1. "
              "Zalja got 10 gold on it.",
         progress="Bigger, mon. Zalja need BIGGER.",
         reward="LOOK at dat! Look at it, goblin! Pay up! Pay UP, mon! HAHAHA! Here, little fishman. Your share.",
         details=["talk", "point"], reward_emotes=["laugh", "cheer"], rewards=["zalja_knot"],
         accept=[("emote", "self", "flex"), ("wait", 1500), ("face", "self", "bookie"), ("emote", "self", "point"),
                 ("wait", 1200), ("emote", "bookie", "flex"), ("emote", "bookie", "laugh"), ("wait", 1800),
                 ("face", "self", "player"), ("emote", "self", "laugh"), ("sound", "self", 6958)],
         complete=[("face", "self", "bookie"), ("emote", "self", "attack"), ("wait", 900), ("emote", "self", "attack"),
                   ("sound", "self", 6958), ("wait", 1200), ("emote", "bookie", "cry"), ("wait", 1200),
                   ("sound", "bookie", 895), ("emote", "bookie", "beg"), ("wait", 1500), ("face", "self", "player"),
                   ("emote", "self", "laugh"), ("sound", "self", 6958)],
         poi=["crawler_beach"]),

    # 8.20: the Elder's cough
    dict(key="ch8_cough", title="The Elder's Cough", giver="ch1:murlorga", ender="ch1:murlorga", level=42, xp=8,
         tone="serious", prev="ch8_hatch", items=[("herb", 6)],
         goal="Gather 6 Jungle Herbs on the green hill slopes east of the wreck, for the Elder's cough.",
         text="Hear that? ...There. Again. He says it's the sea air. The sea air! He has breathed sea air for a hundred "
              "years. The jungle has leaves for a wet chest. Bitter ones. 6 bunches. Don't tell him.",
         progress="Shh! He's listening. Pretend we're talking about fish.",
         reward="Good, good. Into the pot... he'll drink it if I say it's soup. He always drinks it if I say it's soup.",
         details=["talk", "no", "point"], reward_emotes=["yes", "talk"],
         accept=[("state", "self", "none"), ("face", "self", "elder"), ("sound", "ch1:elder", 5736),
                 ("emote", "ch1:elder", "wound"), ("wait", 1500), ("sound", "ch1:elder", 5736), ("wait", 1200),
                 ("emote", "ch1:elder", "no"), ("wait", 1500), ("emote", "self", "no"),
                 ("wait", 1500), ("face", "self", "player"), ("emote", "self", "cry"), ("wait", 1500),
                 ("face", "self", "jungle_dir"), ("emote", "self", "point"), ("wait", 2000), ("face", "self", "pot"),
                 ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "yes"), ("sound", "self", 1187), ("wait", 1200),
                   ("sound", "self", 973), ("wait", 500), ("sound", "self", 973), ("emote", "self", "talk"), ("wait", 2000),
                   ("face", "self", "pot"), ("state", "self", "work")],
         poi=["herb_3"]),

    # 8.14: the wellspring dive
    dict(key="ch8_dive", title="The Wellspring Dive", giver="ch1:elder", ender="ch1:elder", level=43, xp=8, tone="serious",
         prev="ch8_hatch", objects=[("shrine_peek", 1)],
         goal="Swim down into the pool at Nek'mani Wellspring, the troll ruins on the hill north of Booty Bay, and peer "
              "through the cracked stone of the drowned shrine at its bottom.",
         text="Half the eggs are home. Half. The other half went with the long ones... the trident on the crates. North, "
              "past the goblin town, there is a hill with a pool on top and dry-skin ruins all round it. The long ones "
              "dig there. Go down into the pool. Look. Only look.",
         progress="What did you see?",
         reward="...She was there. The cold one. The one who burned the mark into you. ...Mm. Mm. Sit by me a moment, "
                "little one.",
         details=["talk", "point", "no"], reward_emotes=["bow", "talk"],
         accept=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 900), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 900), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200),
                 ("face", "self", "wellspring"), ("emote", "self", "point"), ("wait", 1500), ("sound", "self", 5736),
                 ("face", "self", "player"), ("emote", "self", "no")],
         complete=[("emote", "self", "bow"), ("sound", "self", "murloc_fidget2"), ("music", 6074), ("wait", 3000),
                   ("sound", "self", 5736), ("wait", 2000), ("emote", "self", "bow")],
         poi=["shrine_peek"]),

    # 8.15: naga explorers (and Grrmlgrrl's coral spear, longer)
    dict(key="ch8_explorers", title="Naga Explorers", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=43, xp=8,
         tone="serious", path="hero", prev="ch8_dive", kill=[(1907, 12)],
         goal="Kill 12 Naga Explorers at Nek'mani Wellspring and on the hills of the Cape around it, north of Booty Bay.",
         text="Long ones. On the hill. Digging up dead dry-skins' stones with our people's hands. ...12. Kill 12. "
              "Start with the ones holding whips.",
         progress="More.",
         reward="12. Here. I cut it from the reef while you were gone. Same coral as the first one. Longer.",
         details=["talk", "attack"], reward_emotes=["salute", "flex"], choice=["reef_spear", "reef_staff", "reef_shank"],
         accept=[("move", "self", "grrm_draw", "walk"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "ch1:map_reef", "grrm_draw2", 30),
                 ("object", "ch1:sand_spear", "grrm_draw", 30), ("sound", "self", 1194), ("wait", 1800),
                 ("emote", "self", "attack"), ("sound", "self", 417), ("wait", 700), ("emote", "self", "attack"),
                 ("sound", "self", 417), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 417),
                 ("wait", 1500), ("emote", "self", "roar"), ("move", "self", "grrmlgrrl", "walk"), ("wait", 1500),
                 ("face", "self", "hub")],
         complete=[("object", "ch1:spear_parts", "grrm_draw", 30), ("sound", "self", 1194), ("wait", 1500),
                   ("face", "self", "player"), ("emote", "self", "salute"), ("wait", 1200), ("emote", "self", "flex"),
                   ("sound", "self", "murloc_fidget2")]),

    # 8.16: diggers in chains
    dict(key="ch8_diggers", title="Diggers in Chains", giver="ch1:murlorga", ender="ch1:murlorga", level=43, xp=8,
         tone="serious", path="hero", prev="ch8_dive", objects=[("shackle", 5)],
         interact=[("digger_habit", "Touch his shoulder.")], interact_goal="The old digger stopped digging",
         interact_beats=[("state", "self", "none"), ("emote", "self", "question"), ("sound", "self", 1206), ("wait", 2500),
                         ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"), ("wait", 2500),
                         ("emote", "self", "bow"), ("wait", 1500), ("sound", "self", "splash"), ("despawn", "self")],
         goal="Break the shackles of 5 murloc diggers working for the naga in the pool at Nek'mani Wellspring, and touch "
              "the shoulder of the old digger who won't stop digging.",
         text="Murlocs. In chains. Digging for the long ones... like we did. Like WE did. 6 of them, at least. Break the "
              "chains. Then... let them choose where to swim.",
         progress="Did they swim away? Did they?",
         reward="6. Free. ...Did any of them come this way? No? No. That's all right. They'll find their own shore. "
                "Everyone deserves their own shore.",
         details=["cry", "point"], reward_emotes=["yes", "cry"],
         accept=[("state", "self", "none"), ("emote", "self", "cry"), ("sound", "self", "murloc_wound"), ("wait", 1800),
                 ("emote", "self", "attack"), ("sound", "self", 1206), ("wait", 1500), ("face", "self", "wellspring"),
                 ("emote", "self", "point"), ("wait", 1500), ("face", "self", "pot"), ("state", "self", "work")],
         complete=[("state", "self", "none"), ("emote", "self", "yes"), ("wait", 1500), ("emote", "self", "cry"),
                   ("sound", "self", "murloc_fidget2"), ("wait", 3000), ("state", "self", "work")],
         poi=["dig_3", "dig_7"]),

    # 8.17: Gurubashi stones (a shadow of Hakkar; never followed)
    dict(key="ch8_stones", title="Gurubashi Stones", giver="ch1:glubbub", ender="ch1:glubbub", level=43, xp=8,
         tone="serious", prev="ch8_dive", items=[("tablet", 6)],
         poi=["tab_2", "tab_5"],
         goal="Bring Oracle Glubbub 6 Carved Gurubashi Tablets from the naga's dig in and around the pool at Nek'mani "
              "Wellspring.",
         text="The long ones dig for stones. Old stones. Carved. Why would the long ones want dry-skin stones? ...Bring "
              "me 6. I want to see what they see. I want to... no. I don't want to. Bring them anyway.",
         progress="The stones... do they hum? Tell me they don't hum.",
         reward="...Put them down. Down. Don't look at them. ...Sand. More sand. Cover it. Cover all of it.",
         details=["spell", "question"], reward_emotes=["no", "cry"],
         accept=[("state", "self", "none"), ("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("wait", 1500),
                 ("emote", "self", "question"), ("wait", 1200), ("face", "self", "wellspring"), ("emote", "self", "point"),
                 ("wait", 1500), ("emote", "self", "no"), ("state", "self", "sit")],
         complete=[("state", "self", "none"), ("emote", "self", "kneel"), ("object", "tablet_prop", "glubbub_front", 40),
                   ("sound", "self", 1194), ("wait", 2000), ("object", "serpent", "glubbub_front2", 10), ("wait", 1500),
                   ("visual", "self", 52878), ("sound", "self", "murloc_wound_crit"), ("wait", 3500),
                   ("emote", "self", "kneel"), ("object", "ch1:sand_mound", "glubbub_front", 40), ("sound", "self", 1194),
                   ("wait", 1500), ("emote", "self", "no"), ("face", "self", "glubbub_away"), ("state", "self", "sit")]),

    # 8.18: Lord Sakrasis
    dict(key="ch8_sakrasis", title="Lord Sakrasis", giver="ch1:elder", ender="ch1:murlorga", level=44, xp=8, tone="serious",
         path="hero", prev=["ch8_explorers", "ch8_diggers"], kill=[("sakrasis", 1)], items=[("reef_eggs", 1)],
         drops={"reef_eggs": [("sakrasis", 100)]},
         goal="Lay hands on the egg net at the bottom of the pool at Nek'mani Wellspring to draw out Lord Sakrasis, kill "
              "him, and bring Murlorga the eggs he guards.",
         text="Her lord. The long one with our eggs in his net. Take the net, little one. He will come for it. When he "
              "comes... Grrmlgrrl taught you what to do. Bring back what you can. Whatever you can.",
         progress="Are they safe? How many? HOW MANY?",
         reward="4. Only 4. ...4 is not none. 4 is not none. Come here, little ones. Into the basket with your brothers "
                "and sisters.",
         details=["talk", "point"], reward_emotes=["cry", "bow"], choice=["shrine_robe", "shrine_jerkin", "shrine_hauberk"],
         accept=[("emote", "self", "attack"), ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"),
                 ("sound", "self", 977), ("wait", 700), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1200),
                 ("face", "self", "wellspring"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "attack"), ("sound", "self", 417), ("wait", 1200), ("sound", "self", 5736)],
         complete=[("state", "self", "none"), ("object", "ch1:basket", "basket_spot", 60),
                   ("object", "ch1:held_egg", "basket_spot", 60), ("emote", "self", "kneel"), ("wait", 1500),
                   ("emote", "self", "cry"), ("sound", "self", "murloc_fidget2"), ("music", 6075), ("wait", 3000),
                   ("emote", "self", "bow"), ("wait", 3000), ("state", "self", "work")],
         poi=["egg_net"]),

    # 8.21: Captain Keelhaul
    dict(key="ch8_keelhaul", title="Captain Keelhaul", giver="ch1:grrmlgrrl", ender="ch1:grrmlgrrl", level=44, xp=8,
         tone="serious", path="hero", prev="ch8_sakrasis", kill=[(2548, 1)], rep=[(21, 500)],
         goal="Kill Captain Keelhaul aboard the northern Bloodsail ship off the Wild Shore.",
         text="The goblin with the hook. On the north ship. He bought our eggs from the long ones and sold them to the "
              "cook. ...He is the one. Go.",
         progress="...",
         reward="Done. ...Mm. It doesn't feel like I thought it would.",
         details=["talk", "point"], reward_emotes=["no", "talk"], choice=["deck_slippers", "deck_boots", "deck_greaves"],
         accept=[("move", "self", "grrm_draw", "walk"), ("wait", 1500), ("emote", "self", "kneel"),
                 ("object", "flag_drawing", "grrm_draw", 30), ("sound", "self", 1194), ("wait", 1500),
                 ("move", "ch1:blrrgl", "grrm_draw2", "walk"), ("wait", 3500), ("emote", "ch1:blrrgl", "kneel"),
                 ("object", "flag_drawing", "grrm_draw2", 30), ("emote", "ch1:blrrgl", "laugh"), ("sound", "ch1:blrrgl", "murloc_fidget"),
                 ("wait", 2000), ("emote", "self", "rude"), ("wait", 1500), ("move", "ch1:blrrgl", "blrrgl", "walk"),
                 ("move", "self", "grrmlgrrl", "walk"), ("wait", 1500), ("face", "self", "ships_view"),
                 ("emote", "self", "point")],
         complete=[("emote", "self", "no"), ("sound", "self", "murloc_fidget2"), ("wait", 1500), ("state", "self", "sit"),
                   ("wait", 9000), ("state", "self", "none"), ("face", "self", "hub")]),

    # 8.22: Firallon's ledger (the chart to the arches)
    dict(key="ch8_ledger", title="Firallon's Ledger", giver="ch1:elder", ender="ch1:glubbub", level=44, xp=8, tone="serious",
         path="hero", prev="ch8_keelhaul", kill=[(2546, 1)], items=[("ledger", 1)], drops={"ledger": [(2546, 100)]},
         rep=[(21, 500)],
         goal="Kill Fleet Master Firallon aboard the south-western Bloodsail ship, take his ledger, and bring it to Oracle "
              "Glubbub at the wreck.",
         text="Keelhaul bought. Someone sold. Someone always writes down who. The red-sail chief on the south-west ship "
              "keeps a book. Bring me the book... no. Bring it to Glubbub. Glubbub reads what nobody can read.",
         progress="The book? Give... give.",
         reward="A map. A map in the book... a red mark... two great stone arches over the sea. I... I have seen them. "
                "In the water. In the dream. That's where she's going. That's where we're going.",
         details=["talk", "point"], reward_emotes=["exclamation", "talk"], choice=["ledger_sash", "ledger_belt", "ledger_girdle"],
         accept=[("face", "self", "ships_view"), ("emote", "self", "point"), ("wait", 1500), ("face", "self", "player"),
                 ("emote", "self", "talk"), ("wait", 1200), ("face", "self", "glubbub"), ("emote", "self", "point"),
                 ("wait", 1200), ("sound", "self", 5736), ("face", "self", "hub")],
         complete=[("state", "self", "none"), ("emote", "self", "kneel"), ("object", "chart_prop", "glubbub_front", 30),
                   ("sound", "self", 1192), ("wait", 1500), ("emote", "self", "point"), ("wait", 900),
                   ("visual", "self", 35426), ("sound", "self", "murloc_fidget2"), ("emote", "self", "spell"), ("wait", 2500),
                   ("emote", "self", "exclamation"), ("sound", "self", "murloc_alert"), ("wait", 2000), ("state", "self", "sit")]),

    # 8.25: Fizzbo's sea-chart (a better chart)
    dict(key="ch8_chart", title="Fizzbo's Sea-Chart", giver="ch0:fizzbo", ender="ch1:elder", level=44, xp=8, tone="funny",
         prev="ch8_ledger", source="sea_chart", rep=[(21, 350)],
         goal="Take Fizzbo's Sea-Chart to the Elder at the wreck.",
         text="Arches, huh? Two big rocks over the water? I got a chart. Better'n any pirate's. Every reef, every rock, "
              "every shark. Price: 1 black pearl. ...You ain't got one? Fine. Fine! Pay me next time. Business is "
              "friendship.",
         progress="A chart? Mm. Show me.",
         reward="Every rock. Every reef. The goblin drew the whole sea... except the part under his thumb. Hm! Even so. "
                "Even so, it is a good map.",
         details=["beg", "point"], reward_emotes=["yes", "talk"],
         accept=[("object", "chart_prop", "fizzbo_front", 20), ("emote", "self", "talk"), ("wait", 1200),
                 ("emote", "self", "shy"), ("wait", 1200), ("emote", "self", "point"), ("wait", 1200), ("emote", "self", "beg"),
                 ("sound", "self", 895), ("take", "black_pearl", 1), ("wait", 1200), ("emote", "self", "laugh")],
         complete=[("move", "self", "elder_draw", "walk"), ("wait", 2500), ("object", "chart_prop", "draw_mid", 30),
                   ("emote", "self", "kneel"), ("sound", "self", 1192), ("wait", 1500), ("emote", "self", "point"),
                   ("wait", 1200), ("sound", "self", 5736), ("wait", 1200), ("emote", "self", "yes"), ("wait", 1500),
                   ("move", "self", "elder", "walk"), ("wait", 2500), ("face", "self", "hub")]),

    # 8.26: Grandmother's rest
    dict(key="ch8_rest", title="Grandmother's Rest", giver="ch1:glubbub", ender="ch0:shellback", level=44, xp=8,
         tone="serious", prev="ch8_ledger",
         goal="Wade out to Grandmother Shellback, resting in the shallows off the wreck, and sit with her a while.",
         text="She carried us round the world. Round the world, little one, on her back. She is very old. Older than the "
              "Elder. ...Go and sit with her. Just sit. I will sing.",
         progress="...",
         reward="...",
         details=["talk", "point"], reward_emotes=["talk"],
         accept=[("state", "self", "none"), ("move", "self", "glubbub_shore", "walk"), ("wait", 6000),
                 ("face", "self", "shellback"), ("state", "self", "sit"), ("music", 4454), ("sound", "self", "murloc_fidget2"),
                 ("wait", 4000), ("sound", "self", "murloc_fidget2"), ("wait", 4000), ("sound", "self", "murloc_fidget2"),
                 ("wait", 4000), ("sound", "self", "murloc_fidget2"), ("wait", 12000), ("state", "self", "none"),
                 ("move", "self", "glubbub", "walk"), ("wait", 6000), ("face", "self", "hub"), ("state", "self", "sit")],
         complete=[("sound", "self", 1463), ("wait", 2000), ("emote", "self", "attack"), ("sound", "self", "splash"),
                   ("wait", 2500), ("sound", "self", 1463)],
         poi=["shellback"]),

    # 8.27: west again (the ride to Feralas)
    dict(key="ch8_end", title="West Again", giver="ch1:elder", ender="ch1:elder", level=44, xp=8, tone="serious",
         prev=["ch8_rest", "ch8_chart"], explore="turtle_side", radius=8,
         goal="Wade out to Grandmother Shellback and see the tribe aboard, then come back and help the Elder onto her shell.",
         text="The book says arches. The goblin's map says arches. Glubbub's dream says arches. ...Then it is arches. "
              "Grandmother is ready. The tribe is on her back already, all but me. ...I am slow today. Go first. I will "
              "follow.",
         progress="Is everyone aboard?",
         reward="Give me your arm, little one. ...There. There. ...Mm. West again.",
         details=["talk", "point"], reward_emotes=["bow"], choice=["voyage_mantle", "voyage_pauldrons", "voyage_spaulders"],
         accept=[("sound", "self", 5736), ("wait", 1500), ("face", "self", "shellback"), ("emote", "self", "point"),
                 ("sound", "self", "murloc_fidget2"), ("wait", 1800), ("face", "self", "player"), ("emote", "self", "talk"),
                 ("wait", 1500), ("emote", "self", "bow")],
         complete=[("move", "ch1:grrmlgrrl", "grrm_help", "walk"), ("move", "self", "elder_shore", "walk"), ("wait", 5000),
                   ("state", "self", "kneel"), ("sound", "self", 5736), ("wait", 1500), ("face", "ch1:grrmlgrrl", "elder_shore"),
                   ("emote", "ch1:grrmlgrrl", "kneel"), ("wait", 1500), ("state", "self", "none"),
                   ("emote", "ch1:grrmlgrrl", "salute"), ("face", "self", "shellback"), ("emote", "self", "attack"),
                   ("sound", "self", 977), ("wait", 1300), ("emote", "self", "attack"), ("sound", "self", 977),
                   ("wait", 1300), ("emote", "self", "attack"), ("sound", "self", 977), ("wait", 1500),
                   ("sound", "self", "splash_big"), ("visual", "player", 51347), ("music", 6837), ("wait", 1200),
                   ("teleport", "player", "ch9:hub", 1.6), ("wait", 3000), ("move", "self", "elder", "walk"),
                   ("move", "ch1:grrmlgrrl", "grrmlgrrl", "walk"), ("wait", 5000), ("face", "self", "hub"),
                   ("face", "ch1:grrmlgrrl", "hub")],
         poi=["turtle_side"]),
]
