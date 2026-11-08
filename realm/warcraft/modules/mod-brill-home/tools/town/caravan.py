# SPDX-License-Identifier: GPL-3.0-or-later
"""The Caravan Office (a Community Project, opened by Brill Endures: tools/town/endures.py): Quartermaster Irena
Sable, sent from the Undercity's supply office, builds Brill a loading yard, a warehouse and an office on the
Undercity road, with Dren Hollow (a driver), Garth Molt (a Deathguard given to the roads) and Selwyn Price (a
cheerful trader who buys anything, and who sold a Brill wagon's route to a bandit to pay a debt).

Five quests: the road's complaints and the site marked; the yard's crates, winch and platform; the missing
manifest (the bandit Bartle Kemp's camp on the hill west of the road, and a choice: Selwyn exposed to the
Merchants' Exchange, or let repay it under Irena's eye); the trading agreements, the guards and the first route
(a choice: the Undercity or Silverpine first); the first departure (the wagon loaded, the road cleared, the
receipt signed at the crossroads) and the office opened. Then a daily delivery contract, a traveller's wish to
stay (Wenna Dask, at the Wayfarer's Rest) and the house's delivery (its furniture).

The town changes a stage at a time (tools/town/README.md, "Projects"): Irena's field desk by the road and the
drivers' stalled wagons (1); survey stakes and Dren's wagon (2); the yard's warehouse (the Redridge stable),
its dock and crates (3); the office (a Redridge farmhouse) and its counter, maps and records (4); the route
signs, the noticeboard, the guards (5); the office open, the Wayfarer's Rest (a Westfall farmhouse) beside it,
the scheduled caravans (the Undercity's by day, Silverpine's in the evening), the yard's day (6); the house's
furniture (7). Marta Greaves, the Rest's innkeeper, is the brewery's (tools/town/brewery.py): she keeps a tent
on the Rest's ground until it's built.

The site (the terrain's heights, map tile 0002731): the warehouse at (2172, 261) turned 310 degrees, its open end
toward the road; the office at (2186, 282) turned 45, its floor 42.1; the Rest at (2198, 300) turned 30, its
floor 36.49; the yard between them and the road."""

SEVREN, ZYGAND, RENEE, JOHAAN, HAMLIN = 1499, 1515, 5688, 1518, 3547
ABE_WINTERS = 2135      # Apprentice Armorer, by Brill's smithy
FOREMAN = "endures.foreman"   # Rudd Carver, the builder's yard

# The office's floor (its farmhouse's), the Rest's.
OFFICE_FLOOR, REST_FLOOR = 42.1, 36.49

LINE = {
    "title": "The Caravan Office",
    "stages": [["R:endures.endures"], ["R:q1"], ["R:q2"], ["R:q3"], ["R:q4"], ["R:q5"], ["M:house_set"]],
    "quests": [
        {
            "id": "q1", "title": "The Road Isn't Empty", "giver": "irena_road", "ender": "irena_road",
            "log": "Interview three caravan drivers stranded on the Undercity road, inspect the road and two broken supply wagons, "
                   "ask Magistrate Sevren about a caravan office, and mark a site for it beside the road. Then return to "
                   "Quartermaster Irena Sable.",
            "offer": (
                "You'll be the one Sevren mentioned. Good. I have a form for you, but I'll spare you it.$B$B"
                "Irena Sable, quartermaster, late of the Undercity's supply office. The Merchants' Exchange sent me because "
                "Brill has become a complaint. Drivers arrive with no one to receive them. Goods are unloaded into the mud. "
                "Three shipments this season were signed for by nobody at all, which is a remarkable trick in a town of the "
                "dead.$B$B"
                "I need to know how bad it is before I tell anyone what to build. Talk to the drivers stuck along the road. "
                "Look at the road itself, and at the two wagons that broke trying to use it. Then ask the Magistrate whether "
                "Brill will give me ground for an office, and if he says yes, drive a stake into it before he changes his "
                "mind."),
            "progress": "Drivers, road, wagons, Magistrate, stake. Any order you like, so long as it ends with the stake.",
            "done": (
                "(Irena writes as you talk, without once looking down at the page.)$B$B"
                "Three drivers with nowhere to unload. Ruts deep enough to lose a wheel in. Two wagons broken on the same "
                "stretch, both picked clean. And a magistrate who said yes before I'd finished asking, which is the most "
                "alarming thing I've heard all week.$B$B"
                "Brill doesn't need a clerk at a table by the road. It needs a loading yard, a warehouse and an office with "
                "a door that locks. I'll draw it up tonight. In triplicate. Someone has to."),
            "return": "Return to Quartermaster Irena Sable on the Undercity road in Brill.",
            "objectives": [("credit", "drivers_credit", 3, "Caravan drivers interviewed"),
                           ("credit", "road_credit", 3, "Road and broken wagons inspected"),
                           ("credit", "sevren_credit", 1, "Magistrate Sevren consulted"),
                           ("credit", "site_credit", 1, "Caravan office site marked")],
            "money": 1200, "xp": 3, "min_level": 10,
        },
        {
            "id": "q2", "title": "A Place to Unload", "giver": "dren", "ender": "dren", "prev": "q1",
            "log": "Recover 6 dumped shipping crates along the Undercity road south of Brill, get a loading winch from Rudd "
                   "Carver at the builder's yard, timber from the yard and iron fittings from Abe Winters by Brill's smithy, "
                   "then help Dren Hollow raise the loading platform and stow the crates in the big tent.",
            "offer": (
                "So you're the one running the quartermaster's errands. Dren Hollow. I drive: the Undercity to Brill, Brill to "
                "the Sepulcher and back, for longer than I've been dead.$B$B"
                "Irena's drawn a yard on paper. Paper doesn't hold freight. What holds freight is a platform a wagon can back "
                "up to, a winch to get the heavy loads off, and a roof over what you've unloaded.$B$B"
                "Start with the crates. Every driver who couldn't find anyone to sign for his load dumped it in the ditch "
                "between here and the crossroads, and half of it's still lying there. Bring back what's sound. Rudd Carver at "
                "the builder's yard owes me a winch, though he'll tell you he doesn't. He's timber put by for us, too, and "
                "Abe Winters by the smithy can spare iron.$B$B"
                "Then we build."),
            "progress": "Crates, winch, timber, iron. You can't unload a wagon onto good intentions.",
            "done": (
                "(Dren stamps on the new platform twice, hard. It doesn't move.)$B$B"
                "That'll take a loaded wagon. The winch will lift a cask of oil without taking anybody's arm off, which is "
                "more than the last one I used could say.$B$B"
                "Twenty years I've driven into Brill and never once had somewhere to stop. I think I'll park here a while. "
                "Just to see what it feels like."),
            "return": "Return to Dren Hollow at the caravan yard in Brill.",
            "objectives": [("credit", "crates_credit", 6, "Dumped shipping crates recovered"),
                           ("credit", "winch_credit", 1, "Loading winch from Rudd Carver"),
                           ("credit", "iron_credit", 2, "Timber and iron fittings gathered"),
                           ("credit", "platform_credit", 4, "Loading platform raised and crates stowed")],
            "items": [(4496, 1)], "money": 1500, "xp": 3, "min_level": 10,
        },
        {
            "id": "q3", "title": "The Missing Manifest", "giver": "irena_road", "ender": "irena_road", "prev": "q2",
            "log": "Search the abandoned wagon on the Undercity road south of Brill and recover 3 missing shipping records, "
                   "follow the trail to the bandits' camp on the hill west of the road, kill Bartle Kemp and recover Brill's "
                   "cargo. Find out who altered the manifest, then settle it with Quartermaster Irena Sable.",
            "offer": (
                "A shipment bound for Brill has vanished on the Undercity road: lamp oil, nails, medicine, a crate of seed for "
                "Hamlin Atkins. The driver came in on foot and says he was set on by bandits.$B$B"
                "I believe in the bandits. I don't believe the manifest. Look at it. The cargo is in the clerk's hand, but "
                "the route and the hour have been scraped off and written in again by someone else. Someone with a better "
                "pen.$B$B"
                "The wagon's still where he left it, where the road bends south of town. Search it. The records that should be "
                "with it are gone, and paper doesn't walk; it blows, or it's carried. Follow it. Bandits who rob the right "
                "wagon, on the right road, at the right hour, were told where to stand. Find out who told them, and bring "
                "me back my cargo."),
            "progress": "Cargo, records and a name. I'll take the name last. I want to be sure of it.",
            "done": (
                "(Irena lays the recovered records beside the manifest and runs her finger down both, line by line.)$B$B"
                "Every crate accounted for. One way or another.$B$B"
                "The office will open with its books straight. That matters more than you'd think. The dead have long "
                "memories and very little else, and they remember who cheated them.$B$B"
                "The builders can have the inside of the office now. I'll keep my table by the road until it opens, thank "
                "you. Regulations."),
            "return": "Return to Quartermaster Irena Sable on the Undercity road in Brill.",
            "objectives": [("credit", "records_credit", 3, "Missing shipping records recovered"),
                           ("kill", "kemp", 1, ""),
                           ("credit", "cargo_credit", 1, "Brill's stolen cargo recovered"),
                           ("credit", "manifest_credit", 1, "The altered manifest settled")],
            "items": [(858, 3)], "money": 2500, "xp": 4, "min_level": 10,
        },
        {
            "id": "q4", "title": "Licenses and Liabilities", "giver": "irena_road", "ender": "irena_road", "prev": "q3",
            "log": "Secure a trading agreement from Aldous Penhallow of the Merchants' Exchange in the Undercity's Trade "
                   "Quarter and another from Lucan Ashgrove of the Sepulcher at the Gallows' End, recruit two caravan guards "
                   "(ask Executor Zygand for a Deathguard; Bastian Coyle waits at the yard), and choose with Dren Hollow which "
                   "road takes Brill's first caravan. Then bring the route maps to Quartermaster Irena Sable.",
            "offer": (
                "The office has a counter and a lock. What it hasn't got is anyone to trade with.$B$B"
                "A caravan office is a promise: that a wagon leaving Brill will arrive somewhere, and that someone there will "
                "pay for what's in it. I can't make that promise on my own authority. I need it in writing, from the "
                "Merchants' Exchange in the Undercity's Trade Quarter and from the Sepulcher's factor, who is lodging at the "
                "Gallows' End and charging his room to someone else.$B$B"
                "We'll want guards, too. I posted a notice and a man answered it; he's at the yard. And Executor Zygand owes "
                "this town a Deathguard for its roads. Ask him nicely. Then ask him again.$B$B"
                "Dren has the route maps. He'll want to argue about which road gets our first wagon. Let him, then choose."),
            "progress": "Two agreements, two guards, one road. I'm told the dead don't hurry. I'm told a great many things.",
            "done": (
                "(Irena spreads Dren's maps across her table and weighs the corners with an inkpot, an iron weight and a "
                "skull she apparently keeps for the purpose.)$B$B"
                "Penhallow's seal, Ashgrove's signature, and the Executor's mark on an escort order, which I intend to frame. "
                "Brill has trade routes. Two of them. On paper, which is where everything real begins.$B$B"
                "Now all we need is a wagon to go down one."),
            "return": "Return to Quartermaster Irena Sable on the Undercity road in Brill.",
            "objectives": [("credit", "undercity_credit", 1, "The Merchants' Exchange's agreement"),
                           ("credit", "silverpine_credit", 1, "The Sepulcher's agreement"),
                           ("credit", "guards_credit", 2, "Caravan guards recruited"),
                           ("credit", "route_credit", 1, "The first caravan's road chosen")],
            "items": [(929, 2)], "money": 2500, "xp": 4, "min_level": 10,
        },
        {
            "id": "q5", "title": "The First Departure", "giver": "dren", "ender": "irena_road", "prev": "q4",
            "log": "Load Brill's first wagon with its 3 chalk-marked crates and check its harness and wheels, brief its guards "
                   "Garth Molt and Bastian Coyle, kill 4 Hedge Ambushers on the Undercity road ahead of it, and have the "
                   "delivery receipt signed by Roadwarden Silas Hobb at the crossroads. Then return to Quartermaster Irena "
                   "Sable.",
            "offer": (
                "First wagon. Our wagon, out of our yard, with Brill's seal on the boards. Twenty years I've waited to drive "
                "one of those without somebody else's name on it.$B$B"
                "Here's how it goes. The three crates with the chalk marks go on first; they're the ones on the manifest, and "
                "Irena will know if you load the wrong three. Check the harness and the wheels, because I will, and I'd "
                "rather not find anything. Tell Garth and Bastian we roll at the bell.$B$B"
                "Then ride ahead of me down the Undercity road. Kemp's lads didn't all die on that hill, and they know what a "
                "new wagon looks like. Clear the hedges. At the crossroads the roadwarden signs for the load, and once that "
                "receipt's signed, Brill's a stop on the map."),
            "progress": "Crates, harness, guards, road, receipt. Then we're a caravan office and not a man with a wagon.",
            "done": (
                "(The yard is full. The guards are back, dusty and pleased with themselves; Dren is telling three people at "
                "once about the ambush; strangers with packs are asking where a body might sleep. Irena reads the signed "
                "receipt twice. Then she stands, straightens her coat and says, loudly enough for the whole yard:)$B$B"
                "The Brill Caravan Office is open.$B$B"
                "(Nobody cheers. The Forsaken rarely do. But nobody leaves, either.)$B$B"
                "Brill has an inn, a market, and people willing to buy things. The next logical step is paperwork. Lots of "
                "paperwork. I'll be in my office, $n. It has a door now. Do knock."),
            "return": "Return to Quartermaster Irena Sable at the caravan yard in Brill.",
            "objectives": [("credit", "loaded_credit", 4, "Wagon loaded and inspected"),
                           ("credit", "briefed_credit", 2, "Garth and Bastian briefed"),
                           ("kill", "ambusher", 4, ""),
                           ("credit", "receipt_credit", 1, "Delivery receipt signed at the crossroads")],
            "items": [(4498, 1)], "money": 4000, "xp": 5, "min_level": 10,
        },
        # The caravan office's delivery contract (the design's "delivery-contract system").
        {
            "id": "daily", "title": "Brill Deliveries", "giver": "irena", "ender": "irena", "prev": "q5", "repeat": "daily",
            "log": "Deliver the caravan office's parcels to Innkeeper Renee at the Gallows' End, Apothecary Johaan and Hamlin "
                   "Atkins in Brill, then return to Quartermaster Irena Sable.",
            "offer": (
                "Three parcels, three signatures, one trip. The contract pays by the parcel and penalizes by the hour.$B$B"
                "Innkeeper Renee is expecting candles and a barrel tap. Apothecary Johaan's is a crate of empty vials, which "
                "he will count in front of you, so let him. Hamlin Atkins has a sack of something for his mushroom beds that "
                "I've declined to examine; carry it at arm's length.$B$B"
                "Some days it's three parcels and some days it's thirty; today, mercifully, it's three. Bring back the "
                "signatures. Brill runs on trust, $n. The caravan office runs on receipts."),
            "progress": "Signatures, $n. A delivery without a signature is just a walk.",
            "done": (
                "Three signatures, in three inks, one of them possibly not ink. All valid. Here's your fee.$B$B"
                "If Renee told you I owe her for a bottle of port, I don't. I have the receipt. I always have the receipt.$B$B"
                "Same time tomorrow? Brill will still be here. So, regrettably, will the paperwork."),
            "return": "Return to Quartermaster Irena Sable at the Brill Caravan Office.",
            "objectives": [("credit", "d_renee", 1, "Parcel signed for by Innkeeper Renee"),
                           ("credit", "d_johaan", 1, "Parcel signed for by Apothecary Johaan"),
                           ("credit", "d_hamlin", 1, "Parcel signed for by Hamlin Atkins")],
            "money": 1500, "xp": 2, "min_level": 10,
        },
        # A traveller who stays (the design's visitors who become residents through their own small quests).
        {
            "id": "settle", "title": "Somewhere to Stay", "giver": "wenna", "ender": "wenna", "prev": "q5",
            "log": "Ask Magistrate Sevren to enter Wenna Dask on Brill's rolls and ask Hamlin Atkins whether he could use a hand, "
                   "then return to Wenna at the Wayfarer's Rest.",
            "offer": (
                "I was meant to go on to the Sepulcher with the next wagon. I've been meant to for a week. (She turns her "
                "room key over and over in her fingers.) I keep finding reasons. The wagon's full. The road's wet. Marta needs "
                "help with the sheets.$B$B"
                "I was a seamstress in Andorhal. I don't know anyone in Silverpine. I don't know anyone here either, but here "
                "people say good morning, even the ones without much of a face to say it with.$B$B"
                "Would you ask for me? The Magistrate keeps the rolls; if he puts my name in them I'll have to stay, won't I. "
                "And Hamlin Atkins looked like a man who could use steady hands. Mine are, mostly. I'd ask myself, but if "
                "they say no I'd rather hear it from you."),
            "progress": "Did they say no? You can tell me. I've been told no by better. Well. By worse.",
            "done": (
                "(Wenna reads the slip Sevren wrote twice, then folds it very small and tucks it inside her collar.)$B$B"
                "Resident of Brill. Wenna Dask, seamstress, of Andorhal and... here. (She laughs, and seems startled by "
                "it.)$B$B"
                "I'll tell Marta I'm keeping the room. Then I'll tell Hamlin I can't tell one mushroom from another, and we'll "
                "see if he still wants me."),
            "return": "Return to Wenna Dask at the Wayfarer's Rest in Brill.",
            "objectives": [("credit", "w_sevren", 1, "Magistrate Sevren asked"),
                           ("credit", "w_hamlin", 1, "Hamlin Atkins asked")],
            "money": 1000, "xp": 2, "min_level": 10,
        },
    ],
    # house_set: the house's furniture bought (stage 7). The drivers asked (each once), Abe's fittings given, the
    # cargo seen and Selwyn heard (the choice waits for both), the choices (q3: Selwyn exposed or supervised; q4: the
    # first road), the guards recruited and briefed.
    "markers": ["house_set", "asked_ostin", "asked_beatrix", "asked_jory", "abe_fittings", "cargo_seen", "heard_selwyn",
                "selwyn_exposed", "selwyn_supervised", "garth_assigned", "bastian_hired", "first_undercity",
                "first_silverpine", "garth_briefed", "bastian_briefed"],
    "npcs": [
        # Irena: at her field desk by the road until the office opens; then behind its counter (always: the
        # quartermaster doesn't keep hours, the ledgers do).
        {"id": "irena_road", "name": "Quartermaster Irena Sable", "subname": "Caravan Administrator", "display": 2666,
         "level": 30, "from": 1, "until": 6, "spawns": [[0, 2199.5, 261.0, 36.63, 5.34]]},
        {"id": "irena", "name": "Quartermaster Irena Sable", "subname": "Caravan Office", "display": 2666, "level": 30,
         "flags": ["gossip", "quest", "vendor"], "from": 6, "spawns": [[0, 2189.75, 283.63, OFFICE_FLOOR, 4.73]],
         # Bags, travel supplies and shipping materials.
         "vendor": [4496, 5571, 5572, 4498, 856, 159, 4540, 117, 4471, 4470, 2320, 5042, 5048]},
        # Dren: by his wagon from the survey on; from the opening, his day (the wagon each morning, the dock by day,
        # the Rest's porch in the evening, the yard's brazier at night).
        {"id": "dren", "name": "Dren Hollow", "subname": "Caravan Driver", "display": 3548, "level": 20,
         "from": 2, "until": 6, "spawns": [[0, 2188.5, 253.0, 37.95, 0.63]]},
        {"id": "selwyn", "name": "Selwyn Price", "subname": "Travelling Merchant", "display": 3672, "level": 15,
         "flags": ["gossip", "vendor"], "from": 1, "until": 6, "spawns": [[0, 2203.8, 263.4, 36.19, 3.65]],
         "vendor": [6529, 6530, 6256, 7005, 2901, 5956, 2604, 6260, 2324, 3371, 2678, 6217, 2880, 4399]},
        {"id": "garth", "name": "Garth Molt", "subname": "Caravan Guard", "display": 3523, "level": 25, "flags": ["gossip"],
         "from": 5, "spawns": [[0, 2193.0, 248.0, 35.71, 5.43]]},
        {"id": "bastian", "name": "Bastian Coyle", "subname": "Caravan Guard", "display": 2627, "level": 18, "flags": ["gossip"],
         "from": 4, "spawns": [[0, 2184.5, 245.5, 36.6, 5.5]]},
        # The drivers stranded on the road (The Road Isn't Empty), their wagons on the verge.
        {"id": "ostin", "name": "Ostin Marl", "subname": "Carter", "display": 2629, "level": 14, "flags": ["gossip"],
         "from": 1, "until": 6, "spawns": [[0, 2189.0, 226.5, 36.1, 1.32]]},
        {"id": "beatrix", "name": "Beatrix Fell", "subname": "Carter", "display": 2811, "level": 14, "flags": ["gossip"],
         "from": 1, "until": 6, "spawns": [[0, 2197.5, 231.0, 34.49, 2.24]]},
        {"id": "jory", "name": "Jory Thane", "subname": "Carter", "display": 2643, "level": 11, "flags": ["gossip"],
         "from": 1, "until": 6, "spawns": [[0, 2205.0, 235.5, 34.13, 1.78]]},
        # Licenses and Liabilities: the Exchange's factor in the Undercity's Trade Quarter (the upper ring, by Daniel
        # Bartlett), the Sepulcher's at the Gallows' End.
        {"id": "penhallow", "name": "Aldous Penhallow", "subname": "Merchants' Exchange", "display": 2648, "level": 30,
         "flags": ["gossip"], "spawns": [[0, 1639.7, 250.9, -43.02, 3.39]]},
        {"id": "ashgrove", "name": "Lucan Ashgrove", "subname": "Factor of the Sepulcher", "display": 2652, "level": 20,
         "flags": ["gossip"], "from": 4, "until": 6, "spawns": [[0, 2262.0, 251.0, 34.3, 3.9]]},
        # The First Departure: the crossroads south of Brill, by its signpost.
        {"id": "hobb", "name": "Roadwarden Silas Hobb", "display": 1589, "level": 25, "flags": ["gossip"],
         "spawns": [[0, 2049.5, 168.5, 34.64, 4.2]]},
        # Bartle Kemp's camp on the hill west of the Undercity road, and his men by its hedges (immune to the road's
        # Deathguard: theirs is no fight of the patrols').
        {"id": "kemp", "name": "Bartle Kemp", "subname": "The Road Toll", "display": 2631, "hostile": True, "faction": 14,
         "level": 12, "type": 7, "unit_class": 1, "health": 2.5, "damage": 1.3, "gold": 300, "unit_flags": 512, "respawn": 120,
         "spells": [(11976, (3000, 5000), (8000, 11000)), (8646, (6000, 8000), (12000, 15000))],
         "spawns": [[0, 2114.0, 229.0, 61.92, 5.5]]},
        {"id": "cutthroat", "name": "Kemp's Cutthroat", "display": [2639, 2659, 2620], "hostile": True, "faction": 14,
         "level": (10, 11), "type": 7, "unit_class": 1, "health": 1, "damage": 1, "gold": 60, "unit_flags": 512, "wander": 3,
         "spells": [(8646, (4000, 7000), (10000, 14000))],
         "spawns": [[0, 2118.5, 223.0, 60.31, 5.0], [0, 2109.5, 234.5, 61.98, 0.2], [0, 2120.0, 235.5, 60.8, 3.5],
                    [0, 2108.0, 226.0, 61.55, 1.0]]},
        {"id": "ambusher", "name": "Hedge Ambusher", "display": [2639, 2659], "hostile": True, "faction": 14,
         "level": (10, 11), "type": 7, "unit_class": 1, "health": 1, "damage": 1, "gold": 50, "unit_flags": 512, "wander": 2,
         "spells": [(11976, (2000, 4000), (9000, 12000))],
         "spawns": [[0, 2093.0, 141.0, 35.04, 2.4], [0, 2087.0, 139.0, 34.28, 1.8], [0, 2084.0, 144.5, 34.41, 1.2],
                    [0, 2097.5, 137.5, 35.77, 2.9]]},
        # The yard's day once it's open (each a time of day: none twice at once).
        {"id": "dren_morning", "name": "Dren Hollow", "subname": "Caravan Driver", "display": 3548, "level": 20,
         "flags": ["gossip"], "from": 6, "when": "morning", "spawns": [[0, 2188.0, 252.0, 37.75, 4.04]]},
        {"id": "dren_day", "name": "Dren Hollow", "subname": "Caravan Driver", "display": 3548, "level": 20,
         "flags": ["gossip"], "from": 6, "when": "day", "spawns": [[0, 2183.11, 250.09, 38.06, 2.27]]},
        {"id": "dren_evening", "name": "Dren Hollow", "subname": "Caravan Driver", "display": 3548, "level": 20,
         "flags": ["gossip"], "from": 6, "when": "evening", "spawns": [[0, 2199.42, 287.54, 36.38, 5.24]]},
        {"id": "dren_night", "name": "Dren Hollow", "subname": "Caravan Driver", "display": 3548, "level": 20,
         "flags": ["gossip"], "from": 6, "when": "night", "spawns": [[0, 2191.11, 252.23, 37.21, 2.62]]},
        {"id": "selwyn_day", "name": "Selwyn Price", "subname": "Travelling Merchant", "display": 3672, "level": 15,
         "flags": ["gossip", "vendor"], "from": 6, "when": "day", "spawns": [[0, 2202.0, 260.5, 36.0, 5.34]],
         "vendor": [6529, 6530, 6256, 7005, 2901, 5956, 2604, 6260, 2324, 3371, 2678, 6217, 2880, 4399]},
        {"id": "selwyn_evening", "name": "Selwyn Price", "subname": "Travelling Merchant", "display": 3672, "level": 15,
         "flags": ["gossip"], "from": 6, "when": "evening", "spawns": [[0, 2257.0, 249.5, 33.71, 0.4]]},
        # The scheduled caravans: the Undercity's by day, Silverpine's in the evening, in the same bay by the dock.
        {"id": "varley", "name": "Hugh Varley", "subname": "Undercity Teamster", "display": 2636, "level": 20,
         "flags": ["gossip", "vendor"], "from": 6, "when": "day", "spawns": [[0, 2181.66, 245.6, 37.18, 2.27]],
         "vendor": [4604, 4605, 4606, 2928, 2930, 5173, 3371, 2321, 4340, 2325]},
        {"id": "brannock", "name": "Odile Brannock", "subname": "Silverpine Peddler", "display": 2667, "level": 18,
         "flags": ["gossip", "vendor"], "from": 6, "when": "evening", "spawns": [[0, 2181.66, 245.6, 37.18, 2.27]],
         "vendor": [787, 4592, 6290, 6256, 6530, 4470, 4399, 2678]},
        {"id": "porter", "name": "Caravan Porter", "display": [1574, 1577], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "day", "spawns": [[0, 2177.81, 246.3, 38.17, 4.36], [0, 2182.65, 252.97, 39.1, 0.17]]},
        {"id": "hand", "name": "Yard Hand", "display": [3542, 2635], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "morning", "spawns": [[0, 2184.51, 253.87, 39.02, 1.22], [0, 2175.71, 242.58, 37.93, 3.49]]},
        {"id": "night_watch", "name": "Caravan Night Watch", "display": 1590, "level": 20, "flags": ["gossip"],
         "from": 6, "when": "night", "spawns": [[0, 2190.48, 249.09, 36.44, 5.41]]},
        # The Wayfarer's Rest: its lodgers (the evening's arrivals, the night's sleepless), and one who'd stay.
        {"id": "traveler", "name": "Weary Traveller", "display": [2656, 2614, 2617], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "evening", "spawns": [[0, 2196.73, 295.8, REST_FLOOR, 2.09]]},
        {"id": "traveler_night", "name": "Sleepless Traveller", "display": [2656, 2614, 2617], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "night", "spawns": [[0, 2195.8, 297.81, REST_FLOOR, 5.24]]},
        {"id": "wenna", "name": "Wenna Dask", "subname": "Seamstress", "display": 2665, "level": 10,
         "from": 6, "spawns": [[0, 2199.17, 302.98, REST_FLOOR, 3.67]]},
        # The building, by day: Oswin (the house's carpenter, coordinating with the yard) and the yard's men.
        {"id": "oswin", "name": "Oswin Thatcher", "subname": "Carpenter", "display": 1638, "level": 25, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "spawns": [[0, 2196.0, 271.0, 40.09, 2.45]]},
        {"id": "laborer", "name": "Builder's Yard Laborer", "display": [3516, 1638, 1604], "level": 15, "flags": [],
         "from": 2, "until": 6, "when": "day", "wander": 3,
         "spawns": [[0, 2191.66, 270.69, 40.42, 2.36], [0, 2168.99, 242.81, 40.6, 2.27]]},
    ],
    "credits": [
        {"id": "drivers_credit", "name": "Caravan drivers interviewed"},
        {"id": "road_credit", "name": "Road and broken wagons inspected"},
        {"id": "sevren_credit", "name": "Magistrate Sevren consulted"},
        {"id": "site_credit", "name": "Caravan office site marked"},
        {"id": "crates_credit", "name": "Dumped shipping crates recovered"},
        {"id": "winch_credit", "name": "Loading winch from Rudd Carver"},
        {"id": "iron_credit", "name": "Timber and iron fittings gathered"},
        {"id": "platform_credit", "name": "Loading platform raised and crates stowed"},
        {"id": "records_credit", "name": "Missing shipping records recovered"},
        {"id": "cargo_credit", "name": "Brill's stolen cargo recovered"},
        {"id": "manifest_credit", "name": "The altered manifest settled"},
        {"id": "undercity_credit", "name": "The Merchants' Exchange's agreement"},
        {"id": "silverpine_credit", "name": "The Sepulcher's agreement"},
        {"id": "guards_credit", "name": "Caravan guards recruited"},
        {"id": "route_credit", "name": "The first caravan's road chosen"},
        {"id": "loaded_credit", "name": "Wagon loaded and inspected"},
        {"id": "briefed_credit", "name": "Garth and Bastian briefed"},
        {"id": "receipt_credit", "name": "Delivery receipt signed at the crossroads"},
        {"id": "d_renee", "name": "Parcel signed for by Innkeeper Renee"},
        {"id": "d_johaan", "name": "Parcel signed for by Apothecary Johaan"},
        {"id": "d_hamlin", "name": "Parcel signed for by Hamlin Atkins"},
        {"id": "w_sevren", "name": "Magistrate Sevren asked"},
        {"id": "w_hamlin", "name": "Hamlin Atkins asked"},
    ],
    "objects": [
        # The buildings: the yard's warehouse (3), the office (4), the Wayfarer's Rest (6).
        {"id": "warehouse", "name": "Caravan Warehouse", "display": 8011, "type": 33, "from": 3,
         "spawns": [[0, 2172.0, 261.0, 40.85, 5.411]]},
        {"id": "office", "name": "Brill Caravan Office", "display": 8010, "type": 33, "from": 4,
         "spawns": [[0, 2186.0, 282.0, 38.0, 0.785]]},
        {"id": "rest", "name": "Wayfarer's Rest", "display": 7465, "type": 33, "from": 6,
         "spawns": [[0, 2198.0, 300.0, 32.39, 0.524]]},

        # 1: Irena's field desk by the road (until the office opens).
        {"id": "desk_tent", "name": "Quartermaster's Awning", "display": 8698, "scale": 0.7, "from": 1, "until": 6,
         "spawns": [[0, 2196.2, 264.6, 38.33, 5.34]]},
        {"id": "desk", "name": "Field Desk", "display": 234, "from": 1, "until": 6, "spawns": [[0, 2201.3, 259.4, 35.9, 5.34]]},
        {"id": "desk_box", "name": "Quartermaster's Strongbox", "display": 8, "from": 1, "until": 6,
         "spawns": [[0, 2197.6, 258.6, 36.63, 5.34]]},
        # The Road Isn't Empty: the drivers' wagons on the verge, the road's ruts, the two broken wagons, the stakes.
        {"id": "drivers_wagon", "name": "Stalled Supply Wagon", "display": 3678, "from": 1, "until": 6,
         "spawns": [[0, 2186.0, 224.0, 37.1, 0.5]]},
        {"id": "ruts", "name": "Rutted Roadway", "quest_only": True, "display": 20, "scale": 1.6, "from": 1, "until": 6,
         "spawns": [[0, 2192.0, 238.0, 34.96, 0.5]],
         "use": [
             {"cond": ["I:q1"], "quest": "q1", "credit": "road_credit"},
         ]},
        {"id": "broken_wagon", "name": "Broken Supply Wagon", "quest_only": True, "display": 7524, "from": 1, "until": 6,
         "spawns": [[0, 2178.0, 222.5, 38.46, 0.8], [0, 2156.0, 222.0, 42.59, 1.9]],
         "use": [
             {"cond": ["I:q1"], "quest": "q1", "credit": "road_credit"},
         ]},
        {"id": "site_stakes", "name": "Surveyor's Stakes", "quest_only": True, "display": 6134, "from": 1, "until": 6,
         "spawns": [[0, 2193.0, 274.0, 40.86, 0.8]],
         "use": [
             {"cond": ["I:q1"], "quest": "q1", "credit": "site_credit"},
         ]},

        # 2: the survey's stakes, Dren's wagon, the big tent the first crates go into, the timber at the builder's yard.
        {"id": "dren_wagon", "name": "Dren's Wagon", "display": 3678, "from": 2, "spawns": [[0, 2186.0, 249.5, 37.37, 0.55]]},
        {"id": "temp_tent", "name": "Temporary Warehouse", "display": 7195, "from": 2, "until": 6,
         "spawns": [[0, 2164.89, 244.59, 42.59, 5.41]]},
        {"id": "timber", "name": "Caravan Timber", "quest_only": True, "display": 1108, "from": 2, "until": 6,
         "spawns": [[0, 2307.0, 468.0, 34.4, 1.0]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "iron_credit"},
         ]},
        {"id": "platform_frame", "name": "Loading Platform Frame", "quest_only": True, "display": 1248, "from": 2, "until": 6,
         "spawns": [[0, 2179.34, 247.58, 38.15, 5.41]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "platform_credit"},
         ]},
        {"id": "stow_crates", "name": "Recovered Crates", "quest_only": True, "display": 113, "from": 2, "until": 6,
         "spawns": [[0, 2168.73, 243.9, 41.0, 5.41], [0, 2166.86, 246.9, 42.29, 5.41], [0, 2169.3, 246.33, 41.23, 5.41]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "platform_credit"},
         ]},
        # A Place to Unload: Brill's freight, dumped along the Undercity road by drivers with nowhere to unload.
        {"id": "dumped", "name": "Dumped Shipping Crate", "quest_only": True, "display": 18,
         "spawns": [[0, 2158.0, 196.0, 42.66, 0.3], [0, 2152.5, 181.0, 41.23, 1.2], [0, 2140.0, 163.5, 38.05, 2.0],
                    [0, 2117.0, 165.5, 37.76, 0.4], [0, 2104.0, 161.0, 36.46, 2.5], [0, 2071.5, 160.5, 34.82, 1.1]],
         "use": [
             {"cond": ["I:q2"], "quest": "q2", "credit": "crates_credit"},
         ]},

        # 3: the warehouse's dock, crates and a wagon in the yard.
        {"id": "dock", "name": "Loading Platform", "display": 36, "scale": 2.0, "from": 3, "spawns": [[0, 2180.68, 250.66, 38.73, 5.41]]},
        {"id": "yard_crates", "name": "Stacked Freight", "display": 31, "from": 3,
         "spawns": [[0, 2174.67, 246.92, 39.1, 5.76], [0, 2186.36, 254.77, 38.9, 0.35], [0, 2187.36, 262.14, 39.95, 5.41]]},
        {"id": "yard_wagon", "name": "Freight Wagon", "display": 3678, "from": 3, "spawns": [[0, 2157.42, 256.6, 42.93, 5.41]]},

        # The Missing Manifest: the wagon by the road, the records on the trail, the camp.
        {"id": "q3_wagon", "name": "Abandoned Supply Wagon", "quest_only": True, "display": 7524,
         "spawns": [[0, 2143.5, 174.0, 39.6, 0.6]],
         "use": [
             {"cond": ["I:q3"], "quest": "q3", "credit": "records_credit"},
         ]},
        {"id": "trail_records", "name": "Dropped Shipping Record", "quest_only": True, "display": 164,
         "spawns": [[0, 2133.0, 190.0, 49.35, 0.9], [0, 2124.5, 206.5, 54.02, 2.0]],
         "use": [
             {"cond": ["I:q3"], "quest": "q3", "credit": "records_credit",
              "text": "(A bill of lading for Hamlin Atkins's seed, torn off its pad.)"},
         ]},
        {"id": "camp_fire", "name": "Campfire", "display": 192, "spawns": [[0, 2115.0, 232.5, 61.84, 0.0]]},
        {"id": "camp_tent", "name": "Bandit's Tent", "display": 7873, "spawns": [[0, 2108.5, 230.5, 61.99, 0.4]]},
        {"id": "camp_crates", "name": "Stolen Goods", "display": 113, "spawns": [[0, 2112.0, 236.5, 61.8, 1.4]]},
        {"id": "cargo", "name": "Brill's Cargo", "display": 347, "spawns": [[0, 2111.5, 233.0, 62.03, 0.8]],
         "use": [
             {"cond": ["I:q3"], "quest": "q3", "credit": "cargo_credit", "marker": "cargo_seen"},
         ]},

        # 4: the office's counter, its route maps, ledgers and the locked records.
        {"id": "counter", "name": "Caravan Office Counter", "display": 7732, "from": 4,
         "spawns": [[0, 2188.62, 282.49, OFFICE_FLOOR, 4.73]]},
        {"id": "office_chair", "name": "Chair", "display": 91, "from": 4, "spawns": [[0, 2190.88, 283.2, OFFICE_FLOOR, 4.73]]},
        {"id": "map_table", "name": "Map Table", "display": 234, "from": 4, "spawns": [[0, 2181.76, 281.29, OFFICE_FLOOR, 0.79]]},
        {"id": "route_map", "name": "Route Maps", "display": 222, "from": 4, "spawns": [[0, 2181.76, 281.29, 43.05, 1.13]]},
        {"id": "ledgers", "name": "Caravan Ledgers", "display": 43, "from": 4, "spawns": [[0, 2187.84, 286.67, OFFICE_FLOOR, 0.79]]},
        {"id": "records_chest", "name": "Locked Records", "display": 8, "from": 4, "spawns": [[0, 2179.21, 282.28, OFFICE_FLOOR, 0.79]]},

        # 5: the route signs and the noticeboard; the first wagon, its marked crates.
        {"id": "first_wagon", "name": "Brill's First Wagon", "display": 3678, "from": 5, "until": 6,
         "spawns": [[0, 2178.91, 242.65, 37.17, 5.41]],
         "use": [
             {"cond": ["I:q5"], "quest": "q5", "credit": "loaded_credit"},
         ]},
        {"id": "marked_crates", "name": "Chalk-Marked Crate", "quest_only": True, "display": 31, "from": 5, "until": 6,
         "spawns": [[0, 2174.69, 243.02, 38.3, 5.58], [0, 2178.6, 239.13, 37.06, 6.11], [0, 2183.14, 242.28, 36.37, 0.35]],
         "use": [
             {"cond": ["I:q5"], "quest": "q5", "credit": "loaded_credit"},
         ]},

        # 6: the office's sign, the yard's brazier, the scheduled caravans' wagons, the Rest's furniture; wagons
        # bringing goods to the market and to the brewery once it's open.
        {"id": "uc_wagon", "name": "Undercity Caravan Wagon", "display": 3678, "from": 6, "when": "day",
         "spawns": [[0, 2178.91, 242.65, 37.17, 5.41]]},
        {"id": "selwyn_cart", "name": "Selwyn's Wagon", "display": 5392, "scale": 0.75, "from": 6, "when": "day",
         "spawns": [[0, 2199.0, 263.5, 37.35, 1.0]]},
        {"id": "rest_table", "name": "Table", "display": 221, "from": 6,
         "spawns": [[0, 2196.83, 297.02, REST_FLOOR, 0.52], [0, 2202.53, 299.15, REST_FLOOR, 0.52]]},
        {"id": "rest_bench", "name": "Bench", "display": 603, "from": 6,
         "spawns": [[0, 2197.63, 295.63, REST_FLOOR, 0.52], [0, 2196.03, 298.4, REST_FLOOR, 3.67]]},
        # The Wayfarer's Rest: its sign by the road, and Marta Greaves's tent on its ground until it's built.
        {"id": "rest_sign", "name": "Wayfarer's Rest", "display": 727, "from": 1, "spawns": [[0, 2206.53, 292.22, 34.29, 5.24]]},
        {"id": "marta_tent", "name": "Marta's Tent", "display": 7872, "from": 1, "until": 6,
         "spawns": [[0, 2198.93, 299.38, 34.29, 0.52]]},

        # 7: the house's delivery (design: storage chests, imported furniture, parcels), in the house's own coordinates.
        {"id": "house_chest", "name": "Sea Chest from the Sepulcher", "display": 8, "from": 7,
         "spawns": [["house", 0.25, -3.42, 0, 0]]},
        {"id": "house_parcels", "name": "Delivery Parcels", "display": 287, "scale": 0.7, "from": 7,
         "spawns": [["house", -0.6, 4.1, 0, 20]]},
    ],
    "gossip": [
        # Irena at her field desk, by how far the office has come and by Selwyn's fate.
        {"npc": "irena_road", "kind": "greet", "cond": ["M:selwyn_exposed"],
         "text": "The Exchange fined Price a year's profit and struck his license. He's working it off at a copper a crate, "
                 "under my eye. He says good morning to me every morning. I say it back. Neither of us means it."},
        {"npc": "irena_road", "kind": "greet", "cond": ["M:selwyn_supervised"],
         "text": "Price brought me his first payment this morning, on time, counted twice, in a little bag with a ribbon on "
                 "it. I've entered the payment. I've also entered the ribbon. Everything goes in the book, $n."},
        {"npc": "irena_road", "kind": "greet", "cond": ["T:q1"],
         "text": "Name, cargo, purpose. ...Oh, it's you. Good. You're the only person in Brill who doesn't make me fill in a "
                 "form about them."},
        {"npc": "irena_road", "kind": "greet",
         "text": "Name, cargo, destination. ...You're not a delivery. Pity. I was hoping for a delivery. I've had none that "
                 "arrived where they were going since I got here."},
        # Irena in the office (open): Selwyn's fate, the brewer's complaints, the books.
        {"npc": "irena", "kind": "greet", "cond": ["R:brewery.q5", "DAY:3"],
         "text": "Blackbarrel was in again about the carriage on his barley. I explained the tariff. He explained his father. "
                 "We were both very thorough. He'll be back tomorrow; I've already filled in his form."},
        {"npc": "irena", "kind": "greet", "cond": ["M:selwyn_exposed"], "texts": [
            "Price paid his weekly fine in coppers, every one of them face up. I believe that's his idea of an insult. I've "
            "counted them. It took a while. That's my idea of one.",
            "Forty-two shipments since the office opened, three lost, one stolen and recovered, none unaccounted for. The "
            "Exchange has asked me to write a report on how it's done. It will be very long."]},
        {"npc": "irena", "kind": "greet", "cond": ["M:selwyn_supervised"], "texts": [
            "Price's books are clean this week. Too clean. I'll go through them again. He'd be disappointed if I didn't.",
            "Forty-two shipments since the office opened, three lost, one stolen and recovered, none unaccounted for. The "
            "Exchange has asked me to write a report on how it's done. It will be very long."]},
        {"npc": "irena", "kind": "greet",
         "text": "Brill Caravan Office. Arrivals, departures, losses, complaints. Mostly complaints. I find them very soothing."},
        {"npc": "irena", "kind": "option", "cond": ["R:q5"], "text": "Let me see your supplies.", "action": "vendor"},
        # Post from the road: other lines' people, writing through the office.
        {"npc": "irena", "kind": "option", "cond": ["R:q5", "R:customer.closing"], "text": "Did anything come from the Sepulcher?",
         "action": "say", "emote": 1,
         "reply": "A parcel, for you. From an A. Balnir, laundress. (She hands over a soft bundle in brown paper.) Two "
                  "pillowcases, pressed, and a note: \"For the house. They were my mother's. Tell old Wicke to open the shutters "
                  "wider.\" I've entered them as household linen, no duty. Don't tell the Exchange."},
        {"npc": "irena", "kind": "option", "cond": ["R:q5", "M:apprentice.surrendered"], "text": "Any post from the Undercity?",
         "action": "say", "emote": 1,
         "reply": "One letter, from the Apothecarium, opened and resealed by the Society, which is legal and rude. (She reads "
                  "the cover note.) \"W. Crane, under supervision. Permitted one letter a month.\" He asks after Johaan's "
                  "knees and whether the Stay ever did anyone any good. I'd answer him myself, but he didn't ask me."},
        {"npc": "irena", "kind": "option", "cond": ["R:q5"], "text": "I'd like some furniture delivered to my house.",
         "action": "buy", "arg": 10000, "marker": "house_set", "emote": 1,
         "reply": "For the house by the road. (She opens a catalogue, which of course she has.) A sea chest from the Sepulcher, "
                  "oak, iron-bound, only slightly haunted. And a standing order: anything addressed to you comes up the road "
                  "and onto your floor, parcels and all. I'll have Dren deliver them. He'll complain. Sign here."},

        # Dren, by his wagon, and his day once the office is open.
        {"npc": "dren", "kind": "greet", "cond": ["R:q4"],
         "text": "First wagon's greased and waiting. I've walked round it eleven times. Don't count. I'm not counting."},
        {"npc": "dren", "kind": "greet", "cond": ["R:q2"],
         "text": "Platform's held three loads and a Deathguard who fell off the roof. Best thing I ever helped build. Don't tell "
                 "Irena I said 'best'. She'll want it in writing."},
        {"npc": "dren", "kind": "greet",
         "text": "Dren Hollow. Wagon's mine, horse is mine, the road belongs to whoever's got the biggest stick on it. Today "
                 "that's nobody. Make the most of it."},
        {"npc": "dren_morning", "kind": "greet", "texts": [
            "Every morning: wheels, axles, harness, then the horse, then me. The horse complains less.",
            "Grease, $n. Everyone thinks a road's about horses. It's about grease.",
            "Undercity wagon's due at the tenth bell. It's always late. I like that about it; it's reliable."]},
        {"npc": "dren_day", "kind": "greet", "texts": [
            "Mind the winch. It's kinder than Rudd's, but it doesn't know you.",
            "Sixty crates this week and not one in the ditch. I'd say I'd retire, but I'd only go and drive somewhere."]},
        {"npc": "dren_evening", "kind": "greet", "texts": [
            "Marta lets me sit here if I don't drink at her. I don't drink. I sit. It's nice.",
            "Evening. Silverpine's come in. Fish, timber and worry. Same as ever."]},
        {"npc": "dren_night", "kind": "greet", "texts": [
            "Can't sleep. Never could, even before. I watch the wagons. The wagons watch the road.",
            "Night, $n. Garth's on the gate, I'm on the brazier. Between us, nothing gets through but the fog."]},

        # Selwyn: before, during and after The Missing Manifest.
        {"npc": "selwyn", "kind": "greet", "cond": ["M:selwyn_exposed"],
         "text": "Selwyn Price, licensed by nobody, fined by everybody. (He smiles, a little too widely.) I'm still buying, $n. "
                 "Irena takes her share first. I'd do the same, in her place. I very nearly did, in mine."},
        {"npc": "selwyn", "kind": "greet", "cond": ["M:selwyn_supervised"],
         "text": "(Selwyn drops his voice.) Two payments made. Eleven to go. I've never paid anybody back before, $n. It's a "
                 "very strange feeling. Rather like being sober."},
        {"npc": "selwyn", "kind": "greet", "cond": ["A:q3"],
         "text": "Oh, it's you! Off to the hills? Terrible business. Terrible. Bandits. (He laughs, and stops.) Do mind "
                 "yourself up there."},
        {"npc": "selwyn", "kind": "greet", "texts": [
            "Selwyn Price, buyer of anything, seller of everything else! Tell the quartermaster I've waived her fee for "
            "listening to me. She might return the favor.",
            "Buying! Bones, buttons, bits of armor, the occasional heirloom. Selling! Mostly the same, at a modest markup.",
            "Irena says there's a form for being a merchant. I've asked for the form for not filling in forms. She says "
            "she's looking into it. I think we're becoming friends."]},
        {"npc": "selwyn", "kind": "option", "cond": ["I:q3", "M:cargo_seen"], "text": "Your name is on a bill of sale in a bandit camp, Selwyn.",
         "action": "say", "marker": "heard_selwyn", "emote": 18,
         "reply": "(For once, Selwyn has nothing cheerful to say.)$B$BI owe money, $n. To a lender at the Sepulcher who doesn't "
                  "write things down, which is the worst kind. The Scourge burned my stock and the Crusade burned the next. I "
                  "thought: one wagon. The Exchange insures it, nobody's hurt, Kemp gets his third, I sell Brill its own oil "
                  "at a fair price and pay my debt.$B$B...The driver walked home in the dark. I didn't think about the driver."},
        {"npc": "selwyn", "kind": "option", "text": "Let me see what you're selling.", "action": "vendor"},
        {"npc": "selwyn_day", "kind": "greet", "cond": ["M:selwyn_exposed"],
         "text": "Buying! Selling! Being audited! Step up, $n, it's all very fair now. Painfully fair."},
        {"npc": "selwyn_day", "kind": "greet", "cond": ["M:selwyn_supervised"],
         "text": "Down to nine payments. Irena smiled at me yesterday. At least, her face moved. I'm taking it as a smile."},
        {"npc": "selwyn_day", "kind": "greet",
         "text": "Selwyn Price, buyer of anything! The Undercity wagon's brought me a crate of mystery. I haven't opened it. "
                 "Mystery sells better shut."},
        {"npc": "selwyn_day", "kind": "option", "text": "Let me see what you're selling.", "action": "vendor"},
        {"npc": "selwyn_evening", "kind": "greet", "texts": [
            "Evening, $n. I'm not selling anything. I'm sitting. Renee says it's restful. I'm told I'll get the hang of it.",
            "(Selwyn is turning a copper over his knuckles.) One more payment on the debt this week, and nobody had to hold "
            "a wagon up for it. Imagine that."]},

        # The drivers on the road (The Road Isn't Empty: each asked once).
        {"npc": "ostin", "kind": "greet",
         "text": "Waiting. Been waiting since the third bell. Before that, I was waiting since the second."},
        {"npc": "ostin", "kind": "option", "cond": ["I:q1"], "text": "The quartermaster's asking what's gone wrong on the road to Brill.",
         "action": "credit", "quest": "q1", "credit": "drivers_credit", "marker": "asked_ostin", "emote": 1,
         "reply": "Wrong? Nothing's gone wrong. It's always been like this. I bring salt and lamp oil from the Undercity, I stop "
                  "here, and nobody comes. So I wait. Yesterday I waited so long a Deathguard asked if I was a new statue. In "
                  "the end somebody buys the lot off the back for half what it's worth, and I go home. Write that down, if "
                  "she likes writing."},
        {"npc": "beatrix", "kind": "greet",
         "text": "If you're from the builder's yard, I've your nails. If you're not, I've still got your nails. Nobody wants "
                 "nails until they need them."},
        {"npc": "beatrix", "kind": "option", "cond": ["I:q1"], "text": "Quartermaster Sable wants to know why you're stuck here.",
         "action": "credit", "quest": "q1", "credit": "drivers_credit", "marker": "asked_beatrix", "emote": 1,
         "reply": "Three crates of nails for the builder's yard and a receipt book with no one to sign it. I'm not leaving "
                  "nails on the road for the first ghoul with a hammer. Two days I've been here. If she wants a complaint, she "
                  "can have it in writing. I've already written it. Twice."},
        {"npc": "jory", "kind": "greet",
         "text": "(Jory is checking the ropes on his wagon, and then checking them again.) Hello. Sorry. Hello."},
        {"npc": "jory", "kind": "option", "cond": ["I:q1"], "text": "The quartermaster is asking the drivers what's gone wrong.",
         "action": "credit", "quest": "q1", "credit": "drivers_credit", "marker": "asked_jory", "emote": 1,
         "reply": "I lost a crate. Off the back, at the bend past the brazier, in the dark. By the time I'd turned round it was "
                  "gone, and so was the man who'd been walking behind me all the way from the crossroads. Friendly fellow. "
                  "Asked where I was bound and what I carried, and I told him. I tell everyone. ...I shouldn't, should I."},

        # Magistrate Sevren: ground for the office (The Road Isn't Empty); a resident for the rolls (Somewhere to Stay).
        {"npc": SEVREN, "kind": "option", "cond": ["I:q1"],
         "text": "Quartermaster Sable asks whether Brill will grant her ground for a caravan office.",
         "action": "credit", "quest": "q1", "credit": "sevren_credit", "emote": 1,
         "reply": "Grant it? Take it. That ground by the Undercity road has grown nothing but turkeys since the plague. (He "
                  "writes, blots, writes again.) Tell Quartermaster Sable she has the town's leave, and the town's sympathy. "
                  "She'll need both."},
        {"npc": SEVREN, "kind": "option", "cond": ["I:settle"],
         "text": "Wenna Dask, at the Wayfarer's Rest, would like to be entered on Brill's rolls.",
         "action": "credit", "quest": "settle", "credit": "w_sevren", "emote": 1,
         "reply": "A seamstress from Andorhal. (Sevren writes the name with great care, and blots it.) She'll be the first "
                  "person this year to come to Brill on purpose. Give her this. It says she lives here. It doesn't say it's "
                  "easy."},

        # A Place to Unload: the builder's yard's winch, the smithy's iron.
        {"npc": FOREMAN, "kind": "option", "cond": ["I:q2"], "text": "Dren Hollow says you owe him a loading winch.",
         "action": "credit", "quest": "q2", "credit": "winch_credit", "emote": 1,
         "reply": "Owe him? I lent Dren Hollow a winch in the plague year and he brought it back with a dead man still hanging "
                  "off the hook. ...Fine. Take the small one. Tell him the hook's been cleaned. Tell him I want it back."},
        {"npc": ABE_WINTERS, "kind": "option", "cond": ["I:q2"], "text": "The caravan yard needs iron fittings for a loading platform.",
         "action": "credit", "quest": "q2", "credit": "iron_credit", "marker": "abe_fittings", "emote": 1,
         "reply": "Fittings. Brackets, bolts, a hinge or six. (He sweeps a heap of black iron off his bench into a sack.) "
                  "Undercity pattern, every one. Tell the driver to bring the sack back. Sacks don't grow on trees. Nothing "
                  "grows on trees round here."},

        # The Missing Manifest: the choice, made with Irena once the cargo's found and Selwyn's been heard.
        {"npc": "irena_road", "kind": "option", "cond": ["I:q3", "M:heard_selwyn"],
         "text": "Selwyn Price altered the manifest. He sold the route to the bandits.",
         "action": "choice", "quest": "q3", "credit": "manifest_credit", "marker": "selwyn_exposed", "emote": 1,
         "reply": "(Irena's pen stops.) Price. Of course it's Price. He's asked me to waive his fees every day for a month, and I "
                  "took it for his manner.$B$BI'll write to the Exchange tonight. He'll be fined, his license struck, and "
                  "every coin he takes in Brill will pass through my ledger until the debt's paid. He can stay. Brill needs "
                  "somebody who'll buy anything. But he'll do it where I can see him."},
        {"npc": "irena_road", "kind": "option", "cond": ["I:q3", "M:heard_selwyn"],
         "text": "It was Selwyn, to pay a debt. Let him repay every copper and keep trading, under your eye.",
         "action": "choice", "quest": "q3", "credit": "manifest_credit", "marker": "selwyn_supervised", "emote": 1,
         "reply": "(Irena considers you for a long moment.) You're asking me not to report a theft.$B$B...No. You're asking me "
                  "to collect on it. That I can do. He'll repay the Exchange, the driver and the price of your boots, in full, "
                  "on my schedule, and he'll show me his books every week. If he misses one payment I'll report him myself, "
                  "and tell him you vouched for him. I suspect that will worry him more."},

        # Licenses and Liabilities: the agreements, the guards, the first road.
        {"npc": "penhallow", "kind": "greet", "cond": ["R:q4"],
         "text": "Brill's wagon arrives on the day, at the hour, with the seal unbroken. I find it unsettling. Give Sable my "
                 "regards. Tell her to stop writing to me."},
        {"npc": "penhallow", "kind": "greet",
         "text": "The Merchants' Exchange. Tariffs, licenses, disputes and condolences. Mostly disputes. Condolences are extra."},
        {"npc": "penhallow", "kind": "option", "cond": ["I:q4"],
         "text": "Quartermaster Sable of Brill asks the Exchange to agree terms for a regular caravan.",
         "action": "credit", "quest": "q4", "credit": "undercity_credit", "emote": 1,
         "reply": "Brill. (He says it the way one names an ailment.) Sable's prospectus arrived this morning: forty pages, "
                  "indexed. I have never been so thoroughly persuaded of anything in my unlife.$B$BVery well. The Exchange will "
                  "send a wagon a week and take one back, at the standard tariff, less a plague discount I have just invented. "
                  "Sign here. And here. And there."},
        {"npc": "ashgrove", "kind": "greet",
         "text": "Lucan Ashgrove, for the Sepulcher. Fish, timber and bad news, $g sir:madam;, all at very reasonable prices."},
        {"npc": "ashgrove", "kind": "option", "cond": ["I:q4"], "text": "Brill's caravan office wants an agreement with the Sepulcher.",
         "action": "credit", "quest": "q4", "credit": "silverpine_credit", "emote": 1,
         "reply": "The Sepulcher sells fish, timber and bad news, and we're always looking for somebody to sell them to. Brill "
                  "buys? Then Brill has a friend. (He signs with a flourish.) I'll say this for your quartermaster: she's the "
                  "first soul this side of the Greymane Wall who ever asked me for terms in writing. I nearly wept. I would "
                  "have, if I could."},
        {"npc": ZYGAND, "kind": "option", "cond": ["I:q4"], "text": "The caravan office needs a Deathguard to escort its wagons.",
         "action": "credit", "quest": "q4", "credit": "guards_credit", "marker": "garth_assigned", "emote": 1,
         "reply": "Civilian escort duty. (Zygand looks at you as if you'd asked him to knit.) ...Molt. Garth Molt. He's my best "
                  "road man, and he's been asking for a change. He'll hate it. He'll be good at it. Tell Sable she has him "
                  "until the Dark Lady says otherwise."},
        {"npc": "bastian", "kind": "option", "cond": ["I:q4"], "text": "Quartermaster Sable is hiring guards. Still interested?",
         "action": "credit", "quest": "q4", "credit": "guards_credit", "marker": "bastian_hired", "emote": 273,
         "reply": "Interested? I've been standing by this crate since dawn holding my own letter of recommendation. I wrote it "
                  "myself. (It is very short.) Bastian Coyle, Lordaeron militia, the Glades company, until the company stopped "
                  "being people. I know the roads, I can use a spear and I don't run. That last one's new. I'm proud of it."},
        {"npc": "dren", "kind": "option", "cond": ["I:q4"],
         "text": "Send the first wagon to the Undercity. The capital should see what Brill can do.",
         "action": "choice", "quest": "q4", "credit": "route_credit", "marker": "first_undercity", "emote": 273,
         "reply": "The Undercity it is. Safe road, big market, more paperwork than cargo, and Penhallow will be insufferable "
                  "about it. ...You're right, though. Let them see us coming up their road with our own seal on the boards."},
        {"npc": "dren", "kind": "option", "cond": ["I:q4"],
         "text": "Send the first wagon toward Silverpine. The Sepulcher needs it more.",
         "action": "choice", "quest": "q4", "credit": "route_credit", "marker": "first_silverpine", "emote": 273,
         "reply": "Silverpine. Worse road, wolves, worgen, and a market that pays in fish. (Dren grins, which on him looks "
                  "painful.) Good. The Sepulcher's lived on whatever the Undercity forgets to send. Let them be first at "
                  "something."},

        # The First Departure: the guards, the receipt at the crossroads.
        {"npc": "garth", "kind": "option", "cond": ["I:q5"], "text": "We roll at the bell. Dren wants the road ahead cleared.",
         "action": "credit", "quest": "q5", "credit": "briefed_credit", "marker": "garth_briefed", "emote": 273,
         "reply": "Heard. (Garth tests the edge of his axe with a grey thumb.) Twelve years on the north road, and they give me a "
                  "cart of nails to mind. ...It's a good cart. Don't tell Dren I said so."},
        {"npc": "bastian", "kind": "option", "cond": ["I:q5"], "text": "We roll at the bell, Bastian.",
         "action": "credit", "quest": "q5", "credit": "briefed_credit", "marker": "bastian_briefed", "emote": 273,
         "reply": "At the bell. (Bastian swallows, which he hasn't needed to do in years.) First real duty since the militia. "
                  "I'll be at the tailboard. If anything comes over that hedge, $n, it'll find me standing."},
        {"npc": "hobb", "kind": "greet", "cond": ["R:q5"],
         "text": "Brill's wagons go by twice a week now, crooked B on the tailboard. I sign them through. Best part of my day, "
                 "and I've a very long day."},
        {"npc": "hobb", "kind": "greet",
         "text": "Crossroads. Brill north, the Undercity south and west, Silverpine beyond. Sign in, move on, mind the wolves."},
        {"npc": "hobb", "kind": "option", "cond": ["I:q5", "M:first_undercity"], "text": "Brill's first caravan, for your signature.",
         "action": "credit", "quest": "q5", "credit": "receipt_credit", "emote": 1,
         "reply": "Brill, outbound for the Undercity. (He reads the docket, checks the seal and signs with a stub of pencil.) "
                  "Twenty years I've watched carts come down from Brill. Never seen one go up with its own seal on. There. "
                  "Signed. Tell your quartermaster the crossroads says welcome to the road."},
        {"npc": "hobb", "kind": "option", "cond": ["I:q5", "M:first_silverpine"], "text": "Brill's first caravan, for your signature.",
         "action": "credit", "quest": "q5", "credit": "receipt_credit", "emote": 1,
         "reply": "Brill, outbound for the Sepulcher. Silverpine! (He laughs, a dry sound.) Brave or daft. Signed. The "
                  "Sepulcher's own wagon passed an hour ago going the other way. I told them you'd be along. They didn't "
                  "believe me either."},

        # The guards: their duty, and what they've heard of the Scarlet leak (Whispers of the Scarlet's end).
        {"npc": "garth", "kind": "greet", "cond": ["M:scarlet.exposed"],
         "text": "Heard you found the lamplighter out. Two of ours died on the east road and he lit the lamp they walked under. "
                 "I change the hour of every wagon twice now, and I tell nobody. Not even Irena. Especially not Irena; she'd "
                 "write it down."},
        {"npc": "garth", "kind": "greet", "cond": ["M:scarlet.spared"],
         "text": "Marsh still lights the lamps. Executor's orders: nobody tells him the caravan hours, and he doesn't ask. "
                 "Suits me. A man who doesn't ask is a man who's learned something."},
        {"npc": "garth", "kind": "greet", "cond": ["M:scarlet.escaped"],
         "text": "Lamplighter went west one night and nobody's lit the north road since. A wagon in the dark is a wagon nobody "
                 "can count. I'm not sorry. I'm not glad. I'm on duty."},
        {"npc": "garth", "kind": "greet",
         "text": "Garth Molt. Caravan escort, by order of the Executor. I go where the wagon goes and I come back when it does. "
                 "That's the whole of it."},
        {"npc": "bastian", "kind": "greet", "cond": ["R:scarlet.fate"],
         "text": "Before I signed on, I asked Irena one thing: who knows the caravan hours? She showed me the list. It's short. "
                 "After that business with the lamplighter, short is how I like it."},
        {"npc": "bastian", "kind": "greet",
         "text": "Bastian Coyle, caravan guard. Still getting used to the 'guard' part. The 'caravan' part I'm told I'll get used "
                 "to when I've walked behind one for a year."},

        # The scheduled caravans' merchants, and which came first.
        {"npc": "varley", "kind": "greet", "cond": ["M:first_undercity"],
         "text": "Brill sent its first wagon to us, I hear. The Exchange talked of nothing else for a week. Penhallow had it "
                 "entered in the minutes. Now: mushrooms, dust and dye, what'll it be?"},
        {"npc": "varley", "kind": "greet",
         "text": "Undercity freight, by day, on the dot. Well. On a dot. Mushrooms, reagents, dyes. Mind the crates; they're "
                 "heavier than they look and so am I."},
        {"npc": "varley", "kind": "option", "text": "Let me see what the Undercity's sent.", "action": "vendor"},
        {"npc": "brannock", "kind": "greet", "cond": ["M:first_silverpine"],
         "text": "Brill's first ever wagon came to the Sepulcher. To us! Half the town turned out to look at it. Nobody had seen "
                 "a wagon arrive on purpose in years. Fish? I've fish."},
        {"npc": "brannock", "kind": "greet",
         "text": "Silverpine, come in at dusk. Fish, bait, timber, and what news the worgen haven't eaten."},
        {"npc": "brannock", "kind": "option", "text": "Let me see what's come from Silverpine.", "action": "vendor"},
        {"npc": "porter", "kind": "greet", "texts": [
            "Mind your back. No, mine. Mine's the one that comes off.",
            "Crates off, crates on. Same crates, some days. Nobody tells us."]},
        {"npc": "hand", "kind": "greet", "texts": [
            "Wheels greased, harness checked, horses fed. Dren says horses don't need feeding. Dren's horse disagrees.",
            "Early start, $g sir:madam;. The Undercity wagon waits for nobody, except when it's late."]},
        {"npc": "night_watch", "kind": "greet",
         "text": "Night watch on the yard. Nobody in, nobody out, unless they've got a form. I've been told about the forms."},
        {"npc": "traveler", "kind": "greet", "texts": [
            "Off the Undercity wagon. Is there a bed? There's a bed. Thank the Dark Lady, there's a bed.",
            "Bound for the Sepulcher in the morning. Or for here, if they'll have me. I haven't decided. I'm told nobody does, "
            "at first.",
            "They say Brill's got a brewery now. And a garden. I used to think Brill was where you went on the way to "
            "somewhere else."]},
        {"npc": "traveler_night", "kind": "greet", "texts": [
            "Can't sleep. Never can, in a new bed. Never could in an old one, either, since.",
            "(The traveller is sitting very still by the cold hearth.) It's quiet here. I'd forgotten quiet."]},

        # Wenna Dask, who'd stay (Somewhere to Stay).
        {"npc": "wenna", "kind": "greet", "cond": ["R:settle"], "texts": [
            "Morning, $n. Three shirts to mend for the Deathguard and Hamlin's apron, which I think used to be a sail.",
            "I've a door with my name on it. Well, on a card pinned to it. Marta says that counts."]},
        {"npc": "wenna", "kind": "greet",
         "text": "Is it raining? It's always about to rain here. That's a reason to wait, isn't it. One more day."},
        {"npc": HAMLIN, "kind": "option", "cond": ["I:settle"], "text": "Could you use a hand in your beds? Her name's Wenna Dask.",
         "action": "credit", "quest": "settle", "credit": "w_hamlin", "emote": 273,
         "reply": "Steady hands? I've a hundred yards of beds and two hands, one of them loose. Send her round at dawn. Tell her "
                  "to wear old clothes. Tell her everything's old clothes, out here."},

        # Brill Deliveries (the daily contract).
        {"npc": RENEE, "kind": "option", "cond": ["I:daily"], "text": "A parcel from the caravan office. Sign here?",
         "action": "credit", "quest": "daily", "credit": "d_renee", "emote": 1,
         "reply": "Candles and a barrel tap! The old tap's been weeping since the Third War. (She signs with a flourish.) Thank "
                  "Irena for me. Tell her she still owes me for that bottle of port."},
        {"npc": JOHAAN, "kind": "option", "cond": ["I:daily"], "text": "A crate of vials from the caravan office, for your signature.",
         "action": "credit", "quest": "daily", "credit": "d_johaan", "emote": 1,
         "reply": "(Johaan counts the vials, all of them, aloud.) ...forty-seven, forty-eight. Forty-eight. The order was for "
                  "forty-eight. Remarkable. Your quartermaster may be the only competent person in Tirisfal."},
        {"npc": HAMLIN, "kind": "option", "cond": ["I:daily"], "text": "A sack for your mushroom beds, from the caravan office.",
         "action": "credit", "quest": "daily", "credit": "d_hamlin", "emote": 4,
         "reply": "Ah, that's the good stuff. Bat guano from the caves under the Sepulcher, aged a year. (He breathes it in "
                  "deeply, though he can't smell a thing.) Lovely. The blues'll be up to my knees by summer."},

        # Oswin, the house's carpenter, helping the yard by day.
        {"npc": "oswin", "kind": "greet", "cond": ["OWN"], "texts": [
            "Your house is fine, before you ask. I'm only here because Rudd's lads hold a level like it owes them money.",
            "A caravan office, $n. Next it'll be a bank. Then Brill will be a city, and I'll have to charge city rates."]},
        {"npc": "oswin", "kind": "greet",
         "text": "Oswin Thatcher. I build roofs. This one's an office, which means it'll leak on paper. I'm doing my best."},
    ],
}
