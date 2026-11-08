# SPDX-License-Identifier: GPL-3.0-or-later
"""The Surgeon's Hall (a Community Project, opened by Brill Endures): Surgeon Elspeth Rane, a Lordaeron
physician dead nine years, comes up the Undercity road with three injured travellers and finds a town of
the dead with nobody to mend them. A vacant farmhouse inside the cemetery's fence, by Junior Apothecary
Holland's gate, becomes the hall: first a treatment tent in its yard, then an examination room in the open
air, Timm Vetch's prosthetic arm (an apprentice who lost his own long after he died), the Royal
Apothecary Society's request to try its remedies on her patients (the player writes the charter: no
research at all, or only with a patient's free word and under her eye; the rewards are the same, the
words and Fenwick's stock follow), and the hall's first operation, on Agnes Morrow's leg. When Agnes walks
out of the ward, the hall opens: the farmhouse restored (the game's RedRidge_human_farm), its ward,
examination table and Timm's workbench inside, Fenwick Pike's wares and first aid taught as Nurse Neela
teaches it.

The hall stands at (2324, 376), its doorway toward the town's middle (2275, 330): turned 325.7 degrees,
the model's own doorway at 257.5 degrees from that (as the house's is). Its base is 30.29 high, the floor
(4.1 above the base) 0.2 above the highest ground under it, so things inside stand at 34.39. Outside, the
heights are the game's terrain's (map tile 0002731). The vacant farmhouse (the same building closed up)
stands there until the hall opens.

Stages (every project's): 1 open, 2 to 5 as each quest is done, 6 open, 7 the house's furnishings bought.
Daily life once it's open: Elspeth at the door; Fenwick at his counter and Timm at his bench; a patient in the
ward by day and another by night; Agnes Morrow in the yard by day and in the square of an evening; the
Society's apothecary of a morning; Carolai Anise with her basket of an evening.
"""
import math

# The hall: where it stands, how it's turned, its floor; a spot inside it by the hall's own coordinates
# (yards from its middle, the doorway's side at -y), as the house's are.
HALL_X, HALL_Y, HALL_O, HALL_BASE = 2324.0, 376.0, 5.6845, 30.29
HALL_FLOOR = HALL_BASE + 4.1


def hall(lx, ly, deg=0.0, dz=0.0):
    c, s = math.cos(HALL_O), math.sin(HALL_O)
    return [0, round(HALL_X + lx * c - ly * s, 2), round(HALL_Y + lx * s + ly * c, 2), round(HALL_FLOOR + dz, 2),
            round((HALL_O + math.radians(deg)) % (2 * math.pi), 3)]


# Outside (worked out from the hall's coordinates, at the terrain's heights; world x, y, z, facing).
AT = {
    "elspeth": [[0, 2313.9, 368.3, 33.97, 2.72]],
    "timm": [[0, 2318.2, 364.8, 33.78, 3.76]],
    "fenwick": [[0, 2321.1, 361.1, 33.66, 2.89]],
    "jory": [[0, 2318.0, 356.5, 34.16, 0.45]],
    "nan": [[0, 2323.2, 357.1, 33.78, 2.19]],
    "corwin": [[0, 2321.3, 352.5, 34.49, 1.5]],
    "agnes": [[0, 2332.5, 388.4, 33.98, 4.11]],
    "rep": [[0, 2308.7, 369.5, 34.04, 6.03]],
    "oswin": [[0, 2310.8, 377.1, 34.18, 6.21]],
    "worker": [[0, 2312.9, 382.4, 34.1, 5.68], [0, 2327.6, 363.2, 33.58, 2.54]],
    "carolai": [[0, 2320.4, 364.5, 33.7, 3.24]],
    "agnes_day": [[0, 2310.2, 369.1, 34.02, 4.64]],
    "crate": [[0, 2316.7, 363.5, 33.69, 6.03]],
    "tent": [[0, 2320.6, 355.9, 33.95, 5.68]],
    "lumber": [[0, 2315.4, 386.1, 33.93, 0.97]],
    "toolbox": [[0, 2312.4, 380.3, 34.03, 0.1]],
    "barrow": [[0, 2339.2, 375.3, 33.93, 6.21]],
    "cabparts": [[0, 2325.5, 363.1, 33.44, 5.68]],
    "exam1": [[0, 2311.0, 365.8, 33.8, 0.97]],
    "exam2": [[0, 2308.1, 361.6, 33.86, 5.68]],
    "cabinets": [[0, 2312.9, 371.2, 34.0, 4.11], [0, 2322.4, 364.8, 33.54, 4.11]],
    "lamps": [[0, 2307.5, 365.1, 33.85, 5.68], [0, 2311.6, 362.3, 33.73, 5.68]],
    "side": [[0, 2313.3, 363.9, 33.72, 5.68], [0, 2308.8, 367.2, 33.87, 5.68]],
    "vials": [[0, 2313.8, 364.3, 34.85, 0.97]],
    "post": [[0, 2316.4, 369.2, 33.9, 5.68]],
    "mech": [[0, 2334.0, 368.0, 33.77, 0.97]],
    "bench": [[0, 2331.3, 364.4, 33.69, 5.68]],
    "gear": [[0, 2333.8, 364.7, 33.93, 5.68]],
    "arm": [[0, 2330.9, 363.8, 34.55, 5.68]],
    "tbox": [[0, 2331.9, 365.2, 34.58, 5.68]],
    "records": [[0, 2335.1, 372.7, 33.65, 5.68]],
    "proposal": [[0, 2313.3, 363.9, 34.84, 0.97]],
    "tray": [[0, 2308.8, 367.2, 34.99, 0.97]],
    "ward": [[0, 2333.7, 390.3, 33.89, 0.97]],
    "ward_beds": [[0, 2331.5, 392.0, 33.89, 0.97], [0, 2336.2, 388.9, 33.86, 0.97]],
    "banner": [[0, 2319.9, 366.8, 33.68, 4.11]],
    "basket": [[0, 2321.3, 364.5, 33.57, 5.68]],
    "waiting_bench": [[0, 2310.0, 368.0, 33.88, 0.97]],
    # Agnes of an evening, by the Town Improvement Board in the square.
    "agnes_evening": [[0, 2295.5, 304.0, 35.28, 2.2]],
    # Holding Together: the medical wagon on the Undercity road (past the bend, before the crossroads).
    "wagon": [[0, 2092.0, 146.0, 34.97, 2.6]],
    # A Steady Hand: the Garrens' oak tables, in the yard at Garren's Haunt.
    "tables": [[0, 2920.0, 400.0, 30.99, 0.6], [0, 2926.0, 406.0, 31.03, 2.1]],
    # A Spare Arm and a Leg: the mill's gearing and the clockmaker's ruin at Agamand Mills.
    "gearing": [[0, 2790.0, 805.0, 113.25, 0.0], [0, 2805.0, 825.0, 111.84, 1.3], [0, 2780.0, 830.0, 111.84, 2.6]],
    "hand": [[0, 2770.0, 806.0, 112.99, 4.0]],
}

# The game's own: Brill's general store and trade supplies, the apothecaries, Deathguard Dillinger, Hamlin Atkins.
WINTERS, ABIGAIL, HOLLAND, JOHAAN, DILLINGER, HAMLIN, CAROLAI = 2134, 2118, 10665, 1518, 1496, 3547, 2132
FOREMAN = "endures.foreman"   # Rudd Carver, the builder's yard (Brill Endures)

LINE = {
    "title": "The Surgeon's Hall",
    "stages": [["R:endures.endures"], ["R:q1"], ["R:q2"], ["R:q3"], ["R:q4"], ["R:q5"], ["M:house_set"]],
    "quests": [
        {
            "id": "q1", "title": "Holding Together", "giver": "elspeth", "ender": "elspeth", "prev": "endures.endures",
            "log": "Speak with the three injured travellers in Surgeon Elspeth Rane's care, get linen from Mrs. Winters and "
                   "splints from Rudd Carver at the builder's yard, recover her instruments from the wagon she left on the "
                   "Undercity road, and look into the vacant farmhouse by the cemetery gate. Then return to Elspeth.",
            "offer": (
                "You. Can you hold a man's leg still while I set it? No? Then fetch, carry, and keep out of my light.$B$B"
                "Elspeth Rane. I was a physician in Lordaeron for twenty-two years and I have been a corpse for nine, and "
                "in neither condition have I seen a town this size without a single surgeon. Brill has an inn, a stable, "
                "a magistrate and two apothecaries who would sooner bottle my patients than mend them.$B$B"
                "I came up the Undercity road with three travellers who met something with teeth. Then my wagon lost a "
                "wheel, and the horse lost its nerve. Talk to them; they'll tell you more than they tell me. Bandages "
                "and splints, from whoever in this town sells cloth and wood. My instruments are still in the wagon, past "
                "the bend before the crossroads. And look over that boarded-up farmhouse. If it has four walls and a "
                "roof, it's a hospital."),
            "progress": "Bandages. Splints. Instruments. The house. I can count to four, $n, and so can you.",
            "done": (
                "(Under Elspeth's barked instructions the yard becomes a ward: canvas, cots, a fire for boiling, a "
                "table for cutting.)$B$B"
                "Adequate. Not good. Adequate. That word will have to carry a great deal of weight for a while.$B$B"
                "The house is sound, you say. Then that's where we'll be, once the Magistrate stops pretending to read my "
                "petition. I've sent to the Undercity for an orderly: Fenwick Pike, who held men together on the "
                "Darrowmere line while I stitched them. If he's still in one piece himself."),
            "objectives": [("credit", "traveler_credit", 3, "Injured travellers spoken with"),
                           ("credit", "supplies_credit", 2, "Linen and splints"),
                           ("credit", "wagon_credit", 1, "Surgical instruments recovered"),
                           ("credit", "property_credit", 1, "Vacant farmhouse inspected")],
            "return": "Return to Surgeon Elspeth Rane by the cemetery gate in Brill.",
            "money": 2500, "xp": 4, "min_level": 8, "items": [(1251, 5)],
        },
        {
            "id": "q2", "title": "A Steady Hand", "giver": "fenwick", "ender": "elspeth", "prev": "q1",
            "log": "Recover 2 oak tables from the yard at Garren's Haunt, get needles and thread from Abigail Shiel and glass "
                   "and cleaning spirit from Junior Apothecary Holland, and put together the cabinets by the farmhouse door. "
                   "Then report to Surgeon Elspeth Rane.",
            "offer": (
                "Fenwick Pike. Orderly. I was with the surgeons of the Second Regiment on the Darrowmere line, and then I "
                "wasn't with anybody for a while, and now she's sent for me and here I am, still holding things together. "
                "It's mostly what I'm for.$B$B"
                "She wants a proper examination room, and she wants it yesterday. Two tables, for a start: the Garrens, "
                "up at Garren's Haunt north of here, laid their dead out on good oak tables, and the gnolls have dragged "
                "them into the yard. Needles and gut, which Abigail Shiel sells for mending sails and won't ask what "
                "we're mending. Glass and something to clean with; Junior Apothecary Holland is the only one up this road "
                "who'll give us bottles without asking for a patient in return.$B$B"
                "And Rudd's lads have left cabinet parts by the door. Thatcher's chalked every piece. Thatcher says they "
                "go together in an hour. Thatcher says a lot of things."),
            "progress": "Tables, needles, glass, cabinets. She'll inspect every one. She inspects me twice a day.",
            "done": (
                "(Elspeth runs a finger along the tables, holds each needle to the light, and counts the bottles twice.)$B$B"
                "Adequate. ...No. Good. That's good work.$B$B"
                "Holland sent bottles. Clean ones. And a note offering me 'a promising preservative of the tissues, "
                "untested.' Every apothecary in Tirisfal has something untested in a jar that they'd like to try on "
                "someone who can't say no. I'm thinking of papering the walls with their notes.$B$B"
                "Set the tables out under the canvas. Brill can be examined in the open air for now, like livestock."),
            "objectives": [("credit", "table_credit", 2, "Oak tables recovered"),
                           ("credit", "needle_credit", 1, "Needles and thread"),
                           ("credit", "glass_credit", 1, "Glass and cleaning spirit"),
                           ("credit", "cabinet_credit", 1, "Medical cabinets put together")],
            "return": "Return to Surgeon Elspeth Rane by the cemetery gate in Brill.",
            "money": 3500, "xp": 4, "min_level": 8, "items": [(2581, 3)],
        },
        {
            "id": "q3", "title": "A Spare Arm and a Leg", "giver": "timm", "ender": "timm", "prev": "q2",
            "log": "Salvage 3 articulated joints from the rusted mill gearing at Agamand Mills, get leather straps and gears "
                   "from Rudd Carver at the builder's yard, find the hand in the burned clockmaker's shop at Agamand Mills, "
                   "then help Timm Vetch put his prosthetic together and test it.",
            "offer": (
                "Don't stare at the sleeve. Everyone stares at the sleeve. ...Fine. Stare.$B$B"
                "I lost it eight months ago. Not in the plague, not when I died: after. A beam came down in the "
                "Apothecarium's cellars and pinned it, and by the time they dug me out it had gone grey to the shoulder, "
                "and Elspeth said it had to come off. It doesn't grow back, $n. We don't heal. We wear out slower than "
                "we used to, and then all at once.$B$B"
                "So I've been reading. A tinker's plans, gnomish, torn out of a notebook somebody sold in the Undercity: a "
                "hand that closes when you flex your shoulder. Joints, straps, gears, and the hand itself. The mill at "
                "Agamand Mills has gearing rusting in the yard, joints and all. Rudd Carver will spare straps and gears. "
                "And the plans say 'begin with a good hand.' There was a clockmaker in the mill village; his shop's half "
                "burned. If anyone left a hand lying about, it'd be him."),
            "progress": "Joints, straps, gears, a hand. Then we find out whether I've been reading page nine upside down.",
            "done": (
                "(The arm lies on the bench: brass, leather and oak, the gnomish hand at the end of it curled loosely, "
                "like a sleeping thing.)$B$B"
                "It works. It works! Did you see it grab the... well, it grabbed you. Sorry about that. The spring on the "
                "third finger was wound backwards. It only twitches when it's cold now.$B$B"
                "Elspeth looked at it for a full minute. Then she said, 'Good. Practise on the frame for a month before "
                "you strap it to anyone.' That's the nicest thing she has ever said to me. I'm having it framed."),
            "objectives": [("credit", "joint_credit", 3, "Articulated joints salvaged"),
                           ("credit", "strap_credit", 1, "Leather straps and gears"),
                           ("credit", "hand_credit", 1, "The clockmaker's hand"),
                           ("credit", "test_credit", 1, "Prosthetic assembled and tested")],
            "return": "Return to Timm Vetch at the Surgeon's Hall in Brill.",
            "money": 4500, "xp": 5, "min_level": 9,
        },
        {
            "id": "q4", "title": "The Patient Comes First", "giver": "elspeth", "ender": "elspeth", "prev": "q3",
            "log": "Read the Royal Apothecary Society's proposal and Elspeth's case records, ask the three patients in the tent "
                   "what they make of it, consult Apothecary Johaan, then help Surgeon Elspeth Rane write the hall's charter.",
            "offer": (
                "An apothecary came to see me this morning, with Master Apothecary Faranell's seal on his papers. He was "
                "very polite. They're always very polite.$B$B"
                "The Royal Apothecary Society proposes, and I quote, 'to make use of the Surgeon's Hall's patients in the "
                "trial of promising remedies for the decay of the flesh.' Make use of. As if a patient were a field to be "
                "ploughed.$B$B"
                "I won't have it. I also won't be told I'm a sentimental old woman standing in the way of progress, so we "
                "will do this properly. Read the proposal; it's on the side table in the yard. Fetch my case records "
                "from the chest by the side wall; I want the facts. Ask the patients themselves. Ask Johaan, who has the "
                "Society's ear and, I'm told, a conscience somewhere about him. Then come back, and we'll write down what "
                "this hall is for, so nobody has to ask again."),
            "progress": "Proposal, records, patients, Johaan. Then the pen. I've sharpened it. I've sharpened several.",
            "done": (
                "(Elspeth reads the charter aloud, slowly, the way a sentence is read in court.)$B$B"
                "'No patient of this hall shall be made the subject of any trial, test or remedy without their knowledge. "
                "The surgeon's judgement in their care is final.' And then your clause, $n. Good. It's written. Things "
                "that are written are harder to forget, even for us.$B$B"
                "I'll send a copy to the Undercity. Faranell won't read it. Someone in his office will, and they'll "
                "remember the name at the bottom, which is mine. Now out of my ward; people are trying to rest in it."),
            "objectives": [("credit", "papers_credit", 2, "Proposal and case records read"),
                           ("credit", "patient_credit", 3, "Patients consulted"),
                           ("credit", "johaan_credit", 1, "Apothecary Johaan consulted"),
                           ("credit", "charter_credit", 1, "The patients' charter written")],
            "return": "Return to Surgeon Elspeth Rane at the Surgeon's Hall in Brill.",
            "money": 4500, "xp": 5, "min_level": 9,
        },
        {
            "id": "q5", "title": "The First Patient", "giver": "elspeth", "ender": "agnes", "prev": "q4",
            "log": "Prepare the examination table, help Fenwick Pike clean and splint Agnes Morrow's leg, help Timm Vetch fit "
                   "her brace and hand Surgeon Elspeth Rane her instruments through the operation. Then visit Agnes in the "
                   "ward once she's recovered.",
            "offer": (
                "Her name is Agnes Morrow. She walked from Tarren Mill on that leg, which is either very brave or very "
                "stupid, and in my experience the two are cousins.$B$B"
                "Bandits on the Hillsbrad road. A cudgel, then a fall, then nine days walking on it. The bone's split "
                "above the knee, the flesh round it has started to go, and if it goes much further she'll lose the leg, "
                "and with it the only thing she has, which is the road.$B$B"
                "This will be the hall's first proper operation, and I mean it to be done properly. Lay out the table, "
                "scrubbed, the lamps lit. Fenwick will clean and splint the limb; you'll hold what he tells you to hold. "
                "Timm has made her a brace; help him fit it, and don't let him improvise. Then stand at my right hand and "
                "give me what I ask for, the moment I ask for it.$B$B"
                "After, she'll need rest. Then go and see her. Patients remember who came back."),
            "progress": "(Agnes is propped on the cot, her leg splinted hip to ankle.) Is she done sharpening things? Tell her to get on with it. I've a road waiting.",
            "done": (
                "(Days later. Agnes Morrow is standing. The brace creaks, the cane trembles, and Fenwick hovers with his "
                "hands out like a man catching eggs. She waves him off.)$B$B"
                "Look at that. Nine days I walked on that leg thinking every step was the last it had in it.$B$B"
                "I meant to get patched up and move on. But Rane asked me every morning, 'Does it hurt? Good. That means "
                "it's still yours.' I think I'll stay a while.$B$B"
                "I've been dead for years. I'd rather not spend the next hundred crawling."),
            "objectives": [("credit", "prepare_credit", 1, "Examination table prepared"),
                           ("credit", "fenwick_credit", 1, "Agnes's leg cleaned and splinted"),
                           ("credit", "brace_credit", 1, "Brace fitted with Timm"),
                           ("credit", "instrument_credit", 1, "Instruments handed to Elspeth")],
            "return": "Visit Agnes Morrow in the ward of the Surgeon's Hall.",
            "money": 6000, "xp": 5, "min_level": 9, "items": [(858, 3), (2458, 2)],
        },
        # Repairs Required: a daily (from the opening).
        {
            "id": "repairs", "title": "Repairs Required", "giver": "elspeth", "ender": "elspeth", "prev": "q5",
            "repeat": "daily",
            "log": "Get clean linen from Mrs. Winters and thread from Abigail Shiel, close Deathguard Dillinger's shoulder and "
                   "stitch Hamlin Atkins's hand, then return to Surgeon Elspeth Rane.",
            "offer": (
                "Repairs, $n. Every day, repairs. A town of the dead is a town of things coming loose: stitches, joints, "
                "the odd ear. Most of them won't come to me until something falls off, so I go to them. Or rather, you "
                "do.$B$B"
                "Linen from Mrs. Winters, thread from Abigail Shiel. Dillinger's shoulder has opened again; he'll tell you "
                "it's nothing, so don't ask him, tell him. And Hamlin Atkins has cut his hand on a mushroom knife, again, "
                "and is trying to mend it with mushroom paste, again."),
            "progress": "Linen, thread, a shoulder, a hand. In that order, if you can manage it.",
            "done": (
                "Good. Every stitch you put in today is one I don't have to put in tomorrow. That isn't gratitude, $n, "
                "it's arithmetic.$B$B...Fine. It's a little gratitude. Take the bandages, and use them on yourself before "
                "you come to me. I'd like one person in Brill to arrive already mended."),
            "objectives": [("credit", "linen_credit", 1, "Linen from Mrs. Winters"),
                           ("credit", "thread_credit", 1, "Thread from Abigail Shiel"),
                           ("credit", "dillinger_credit", 1, "Deathguard Dillinger's shoulder closed"),
                           ("credit", "hamlin_credit", 1, "Hamlin Atkins's hand stitched")],
            "return": "Return to Surgeon Elspeth Rane at the Surgeon's Hall in Brill.",
            "money": 1200, "xp": 2, "min_level": 9, "items": [(1251, 4), (2581, 2)],
        },
    ],
    # The charter's clause (The Patient Comes First), the travellers spoken with and asked (each once), the
    # supplies (each once), and the house's furnishings bought.
    "markers": ["clinical", "voluntary", "spoke_jory", "spoke_nan", "spoke_corwin", "asked_jory", "asked_nan",
                "asked_corwin", "got_linen", "got_splints", "house_set"],
    "npcs": [
        # Elspeth: at the farmhouse door from the day she arrives (the door she'll keep).
        {"id": "elspeth", "name": "Surgeon Elspeth Rane", "subname": "Head Surgeon", "display": 4108, "level": 30,
         "from": 1, "spawns": AT["elspeth"]},
        # Timm, Fenwick and the travellers in the yard while it's built.
        {"id": "timm", "name": "Timm Vetch", "subname": "Apprentice Surgeon", "display": 2653, "level": 18, "from": 1,
         "until": 6, "spawns": AT["timm"]},
        {"id": "fenwick", "name": "Fenwick Pike", "subname": "Medical Orderly", "display": 2637, "level": 22, "from": 2,
         "until": 6, "spawns": AT["fenwick"]},
        {"id": "jory", "name": "Jory Haskett", "subname": "Carter", "display": 3880, "level": 12, "flags": ["gossip"],
         "from": 1, "until": 6, "spawns": AT["jory"]},
        {"id": "nan", "name": "Old Nan Thistle", "subname": "Peddler", "display": 2663, "level": 12, "flags": ["gossip"],
         "from": 1, "until": 6, "spawns": AT["nan"]},
        {"id": "corwin", "name": "Corwin Teague", "subname": "Deathguard Recruit", "display": 3863, "level": 10,
         "flags": ["gossip"], "from": 1, "until": 6, "spawns": AT["corwin"]},
        # Agnes in the ward tent (The First Patient), then about Brill once she walks.
        {"id": "agnes", "name": "Agnes Morrow", "subname": "Patient", "display": 4041, "level": 14, "from": 5, "until": 6,
         "spawns": AT["agnes"]},
        {"id": "agnes_day", "name": "Agnes Morrow", "display": 4041, "level": 14, "flags": ["gossip"], "from": 6,
         "when": "day", "spawns": AT["agnes_day"]},
        {"id": "agnes_evening", "name": "Agnes Morrow", "display": 4041, "level": 14, "flags": ["gossip"], "from": 6,
         "when": "evening", "spawns": AT["agnes_evening"]},
        # Inside the hall once it's open: Fenwick's counter (and first aid, as Nurse Neela teaches it), Timm's bench,
        # a patient by day and another by night.
        {"id": "fenwick_hall", "name": "Fenwick Pike", "subname": "Medical Orderly", "display": 2637, "level": 22,
         "from": 6, "flags": ["gossip", "vendor"], "trainer": 5759, "spawns": [hall(0.6, -3.8, 270)],
         "vendor": [1251, 2581, 3530, 6452, 2320, 2321, 3371, 118, 858, 2458, 5997, 3382, 2324, 4340,
                    {"item": 3531, "cond": ["M:clinical"]}, {"item": 2456, "cond": ["M:voluntary"]}]},
        {"id": "timm_bench", "name": "Timm Vetch", "subname": "Apprentice Surgeon", "display": 2653, "level": 18,
         "from": 6, "flags": ["gossip"], "spawns": [hall(3.0, -3.2, 0)]},
        # Timm ordering parts at the Caravan Office by day, once both are open (tools/town/caravan.py: the office's
        # floor 42.1, its counter at 2188.6, 282.5; he stands on the customers' side of it).
        {"id": "timm_caravan", "name": "Timm Vetch", "subname": "Apprentice Surgeon", "display": 2653, "level": 18,
         "from": 6, "needs": {"caravan": 6}, "when": "day", "flags": ["gossip"],
         "spawns": [[0, 2188.06, 280.38, 42.1, 1.31]]},
        {"id": "patient_day", "name": "Patient", "display": [2644, 2658, 2661, 2673], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "day", "spawns": [hall(-1.6, 2.4, 180)]},
        {"id": "patient_night", "name": "Patient", "display": [2644, 2658, 2661, 2673], "level": 10, "flags": ["gossip"],
         "from": 6, "when": "night", "spawns": [hall(-1.6, -2.0, 180)]},
        # The Society's man, of a morning (once the charter's written).
        {"id": "rep", "name": "Apothecary Tobin Crell", "subname": "Royal Apothecary Society", "display": 1965, "level": 25,
         "flags": ["gossip"], "from": 5, "when": "morning", "spawns": AT["rep"]},
        # While it's built: the builder's yard's hands, and the house's carpenter (by day).
        {"id": "worker", "name": "Builder's Yard Laborer", "display": [2655, 2641, 2645], "level": 15, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "wander": 2, "spawns": AT["worker"]},
        {"id": "oswin", "name": "Oswin Thatcher", "subname": "Carpenter", "display": 1638, "level": 25, "flags": ["gossip"],
         "from": 2, "until": 6, "when": "day", "spawns": AT["oswin"]},
        # Carolai with her basket of an evening, once it's open.
        {"id": "carolai", "name": "Carolai Anise", "subname": "Alchemy Trainer", "display": 1601, "level": 20,
         "flags": ["gossip"], "from": 6, "when": "evening", "spawns": AT["carolai"]},
    ],
    "credits": [
        {"id": "traveler_credit", "name": "Injured travellers spoken with"},
        {"id": "supplies_credit", "name": "Linen and splints"},
        {"id": "wagon_credit", "name": "Surgical instruments recovered"},
        {"id": "property_credit", "name": "Vacant farmhouse inspected"},
        {"id": "table_credit", "name": "Oak tables recovered"},
        {"id": "needle_credit", "name": "Needles and thread"},
        {"id": "glass_credit", "name": "Glass and cleaning spirit"},
        {"id": "cabinet_credit", "name": "Medical cabinets put together"},
        {"id": "joint_credit", "name": "Articulated joints salvaged"},
        {"id": "strap_credit", "name": "Leather straps and gears"},
        {"id": "hand_credit", "name": "The clockmaker's hand"},
        {"id": "test_credit", "name": "Prosthetic assembled and tested"},
        {"id": "papers_credit", "name": "Proposal and case records read"},
        {"id": "patient_credit", "name": "Patients consulted"},
        {"id": "johaan_credit", "name": "Apothecary Johaan consulted"},
        {"id": "charter_credit", "name": "The patients' charter written"},
        {"id": "prepare_credit", "name": "Examination table prepared"},
        {"id": "fenwick_credit", "name": "Agnes's leg cleaned and splinted"},
        {"id": "brace_credit", "name": "Brace fitted with Timm"},
        {"id": "instrument_credit", "name": "Instruments handed to Elspeth"},
        {"id": "linen_credit", "name": "Linen from Mrs. Winters"},
        {"id": "thread_credit", "name": "Thread from Abigail Shiel"},
        {"id": "dillinger_credit", "name": "Deathguard Dillinger's shoulder closed"},
        {"id": "hamlin_credit", "name": "Hamlin Atkins's hand stitched"},
    ],
    "objects": [
        # The vacant farmhouse (from the Board's going up until the hall opens), and the hall itself (from then).
        {"id": "vacant", "name": "Vacant Farmhouse", "display": 8020, "type": 33, "from": 1, "until": 6,
         "spawns": [[0, HALL_X, HALL_Y, HALL_BASE, HALL_O]]},
        {"id": "hall", "name": "Surgeon's Hall", "display": 8010, "type": 33, "from": 6,
         "spawns": [[0, HALL_X, HALL_Y, HALL_BASE, HALL_O]]},
        {"id": "door", "name": "Boarded Door", "display": 1248, "scale": 1.3, "from": 1, "until": 6,
         "spawns": [hall(-1.0, -6.6, 0)],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "property_credit"}]},
        # Holding Together: Elspeth's crate (until the hall opens), the wagon on the Undercity road (everyone's).
        {"id": "crate", "name": "Surgeon's Crate", "display": 6449, "scale": 0.8, "from": 1, "until": 6,
         "spawns": AT["crate"]},
        {"id": "wagon", "name": "Overturned Wagon", "quest_only": True, "display": 7524, "spawns": AT["wagon"],
         "use": [{"cond": ["I:q1"], "quest": "q1", "credit": "wagon_credit"}]},
        # The yard while it's built (from the second stage until the hall opens): the tent, the builders' lot.
        {"id": "tent", "name": "Treatment Tent", "display": 7873, "from": 2, "until": 6, "spawns": AT["tent"]},
        {"id": "lumber", "name": "Lumber", "display": 1109, "from": 2, "until": 6, "spawns": AT["lumber"]},
        {"id": "cabparts", "name": "Cabinet Parts", "quest_only": True, "display": 1108, "from": 2, "until": 6, "spawns": AT["cabparts"],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "cabinet_credit"}]},
        # A Steady Hand: the Garrens' tables (everyone's, at Garren's Haunt).
        {"id": "tables", "name": "Heavy Oak Table", "display": 221, "spawns": AT["tables"],
         "use": [{"cond": ["I:q2"], "quest": "q2", "credit": "table_credit"}]},
        # The examination room in the open (from the third stage until the hall opens), and its sign (stays).
        {"id": "exam1", "name": "Examination Table", "display": 8073, "scale": 0.85, "from": 3, "until": 6,
         "spawns": AT["exam1"],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "prepare_credit"}]},
        {"id": "exam2", "name": "Oak Table", "display": 151, "scale": 0.8, "from": 3, "until": 6, "spawns": AT["exam2"]},
        {"id": "cabinets", "name": "Medical Cabinet", "display": 4, "from": 3, "until": 6, "spawns": AT["cabinets"]},
        {"id": "side", "name": "Side Table", "display": 581, "from": 3, "until": 6, "spawns": AT["side"]},
        {"id": "vials", "name": "Bottles", "display": 4072, "from": 3, "until": 6, "spawns": AT["vials"]},
        # A Spare Arm and a Leg: Timm's test frame (from the third stage until the hall opens), the mill's gearing
        # and the clockmaker's hand (everyone's, at Agamand Mills).
        {"id": "mech", "name": "Practice Frame", "quest_only": True, "display": 1248, "scale": 0.8, "from": 3, "until": 6, "spawns": AT["mech"],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "test_credit"}]},
        {"id": "gearing", "name": "Rusted Mill Gearing", "quest_only": True, "display": 7000, "spawns": AT["gearing"],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "joint_credit"}]},
        {"id": "hand", "name": "Clockmaker's Hand", "quest_only": True, "display": 7731, "scale": 0.5, "spawns": AT["hand"],
         "use": [{"cond": ["I:q3"], "quest": "q3", "credit": "hand_credit"}]},
        # The workshop in the yard (from the fourth stage until the hall opens).
        {"id": "bench", "name": "Timm's Workbench", "display": 234, "from": 4, "until": 6, "spawns": AT["bench"]},
        # The Patient Comes First: the proposal and the case records (from the fourth stage until the hall opens).
        {"id": "proposal", "name": "The Society's Proposal", "quest_only": True, "display": 7751, "scale": 1.5, "from": 4, "until": 6,
         "spawns": AT["proposal"],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "papers_credit",
                  "text": "('PROPOSAL: the use of the Surgeon's Hall's patients, being already in a state of decay, in the trial of Formulae 12 through 31 for the arrest of necrotic progression. Patients shall be informed as necessary.'$B$BUnder Master Apothecary Faranell's seal. AS NECESSARY is underlined in red ink, three times.)"}]},
        {"id": "records", "name": "Case Records", "quest_only": True, "display": 1, "scale": 1.3, "from": 4, "until": 6,
         "spawns": AT["records"],
         "use": [{"cond": ["I:q4"], "quest": "q4", "credit": "papers_credit",
                  "text": "(Forty-one numbered folders. Under each: CONSENTED. Two say REFUSED, and under that, TREATED OTHERWISE. One says DIED (AGAIN). ATTENDED.)"}]},
        # The First Patient: the instrument tray, and the ward (from the fifth stage until the hall opens).
        {"id": "tray", "name": "Instrument Tray", "display": 6508, "scale": 0.7, "from": 5, "until": 6, "spawns": AT["tray"],
         "use": [{"cond": ["I:q5"], "quest": "q5", "credit": "instrument_credit"}]},
        # The hall open (from the sixth): inside, the ward, the table, Timm's bench and Fenwick's shelves; outside, the
        # Dark Lady's banner and a bench for whoever's waiting.
        {"id": "hall_beds", "name": "Ward Bed", "display": 3471, "scale": 0.75, "from": 6,
         "spawns": [hall(-3.6, 2.1, 90), hall(-3.6, -2.2, 90)]},
        {"id": "hall_table", "name": "Examination Table", "display": 8073, "scale": 0.8, "from": 6,
         "spawns": [hall(1.8, 0.8, 0)]},
        {"id": "hall_bench", "name": "Timm's Workbench", "display": 234, "from": 6, "spawns": [hall(4.3, -3.2, 0)]},
        {"id": "hall_cabinet", "name": "Medical Cabinet", "display": 4, "from": 6, "spawns": [hall(4.2, 4.4, 270)]},
        {"id": "hall_shelf", "name": "Shelf", "display": 187, "from": 6, "spawns": [hall(3.0, -5.6, 90)]},
        {"id": "hall_vials", "name": "Bottles", "display": 4073, "from": 6, "spawns": [hall(3.0, -5.4, 90, 1.78)]},
        {"id": "hall_basin", "name": "Washbasin", "display": 5112, "from": 6, "spawns": [hall(0.8, 3.4, 0)]},
        {"id": "banner", "name": "Forsaken Banner", "display": 7979, "from": 6, "spawns": AT["banner"]},
        {"id": "waiting_bench", "name": "Bench", "display": 682, "type": 7, "from": 6, "spawns": AT["waiting_bench"]},
        # Carolai's basket at the door, of an evening.
        {"id": "basket", "name": "Carolai's Basket", "display": 7494, "from": 6, "when": "evening", "spawns": AT["basket"]},
        # The house's furnishings (bought from Elspeth): a first-aid cabinet, a washbasin, an anatomy (against the
        # doorway's wall, left of the door: the slots asked for, (-2.6, -3.9) and (-3.6, -3.9), hold the brewery's
        # drinks cabinet at (-3.0, -3.8)).
        {"id": "house_cabinet", "name": "First-Aid Cabinet", "display": 6449, "scale": 0.55, "from": 7,
         "spawns": [["house", -4.1, -5.2, 0, 0]]},
        {"id": "house_basin", "name": "Washbasin", "display": 5112, "scale": 0.6, "from": 7,
         "spawns": [["house", 0.15, -5.15, 0, 90]]},
        {"id": "house_book", "name": "Varden's Anatomy of the Risen", "display": 7233, "scale": 0.35, "from": 7,
         "spawns": [["house", -4.1, -5.2, 0.97, 10]]},
    ],
    "gossip": [
        # Elspeth, by how far the hall's come (the first that holds). Once it's open, one day in two she remarks on
        # what became of Wendell Crane's work (the apothecary's line), if anything did.
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q5", "M:apprentice.surrendered", "DAY:2"],
         "text": "The Society has young Crane's notes now, I hear. Johaan's apprentice. I read a copy. Half of it is "
                 "genius and half of it is a crime, and the Society will keep the wrong half. Mind the step."},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q5", "M:apprentice.supervised", "DAY:2"],
         "text": "Johaan lets his apprentice go on brewing that 'Stay' of his, under supervision. I've asked to see the "
                 "notes. I've asked to see the subjects. So far I have seen neither. Supervision is a word, $n. I prefer "
                 "a register."},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q5", "M:apprentice.destroyed", "DAY:2"],
         "text": "Johaan burned his apprentice's work, I'm told. A tincture to slow the rot. I don't know whether to "
                 "thank him or weep. Probably neither. There's a patient waiting."},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q5", "M:clinical"], "texts": [
            "The hall's open, the charter's on the door, and not one apothecary has set foot past it. I'd call that a "
            "good week.",
            "Agnes walked to the square and back this morning. Twice. I didn't watch. Fenwick watched. I watched Fenwick.",
            "If you're bleeding, come in. If you're selling something, the Society's office is in the Undercity."]},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q5", "M:voluntary"], "texts": [
            "The Society's man comes of a morning with his little bottles, and signs the register in front of the "
            "patient, and I stand at the foot of the bed. So far he has been very polite. They're always very polite.",
            "Two patients volunteered for the Society's trials. One withdrew on the second day, and the apothecary "
            "thanked him for his time. I made sure of the thanking.",
            "Agnes walked to the square and back this morning. Twice. I didn't watch. Fenwick watched. I watched Fenwick."]},
        {"npc": "elspeth", "kind": "greet", "cond": ["A:q5"],
         "text": "Table, Fenwick, Timm, me. In that order. Agnes is counting on all of us, and I'm counting on you to "
                 "keep up."},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q4"],
         "text": "The charter's on the door, and there's a woman coming up the Hillsbrad road on a leg that needs more than "
                 "a charter. Are you ready, $n? Say yes. I haven't time for the other answer."},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q3"],
         "text": "Timm's arm works. I told him so. I didn't tell him I came back to the yard at midnight to watch it pick "
                 "up a teacup. Don't you tell him either."},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q2"],
         "text": "Tables, cabinets, lamps. It's beginning to look like a place where a person might get better, instead "
                 "of a place where a person waits to stop."},
        {"npc": "elspeth", "kind": "greet", "cond": ["R:q1"],
         "text": "A tent and three cots. Lordaeron's finest physicians would weep. I did, a little, in the privacy of my "
                 "own head."},
        {"npc": "elspeth", "kind": "greet",
         "text": "If you're bleeding, wait your turn. If you're not, make yourself useful or make yourself scarce."},
        # Elspeth: the charter's clause (The Patient Comes First).
        {"npc": "elspeth", "kind": "option", "cond": ["I:q4"],
         "text": "No research at all. This hall heals; it doesn't experiment.",
         "action": "choice", "quest": "q4", "credit": "charter_credit", "marker": "clinical", "emote": 273,
         "reply": "Clinical, then. No trials, no tinctures, no 'promising remedies'. The Society can find its volunteers "
                  "somewhere else; I'll give them directions. The clause reads: 'No research shall be done within these "
                  "walls.' Short. I like short."},
        {"npc": "elspeth", "kind": "option", "cond": ["I:q4"],
         "text": "Allow research, but only on those who freely agree, and under your eye.",
         "action": "choice", "quest": "q4", "credit": "charter_credit", "marker": "voluntary", "emote": 1,
         "reply": "Voluntary, supervised, and stopped the moment anyone says stop. I'll stand at the foot of every bed, and "
                  "their apothecary will sign the register in front of the patient, not behind a door. It's more than "
                  "they'd have offered and less than they wanted. That's usually where the right answer lives."},
        # Elspeth, once it's open: the charter, and the house's furnishings.
        {"npc": "elspeth", "kind": "option", "cond": ["R:q5", "M:clinical"], "text": "(Ask about the charter.)",
         "action": "say", "emote": 1,
         "reply": "It's nailed to the door, at the height of an apothecary's eyes. 'No research shall be done within "
                  "these walls.' Faranell's office wrote back to ask whether that included observation. I wrote back: yes."},
        {"npc": "elspeth", "kind": "option", "cond": ["R:q5", "M:voluntary"], "text": "(Ask about the charter.)",
         "action": "say", "emote": 1,
         "reply": "Nailed to the door. Consent freely given, freely withdrawn, the surgeon present. Crell comes of a "
                  "morning, signs, asks, is refused, signs again. He's learning. Slowly. Like a dog that can read."},
        {"npc": "elspeth", "kind": "option", "cond": ["R:q5", "OWN"], "text": "Could the hall spare anything for my house?",
         "action": "buy", "arg": 12000, "marker": "house_set", "emote": 1,
         "reply": "For your house. A first-aid cabinet, stocked; a washbasin, so you stop bleeding on your sheets; and "
                  "Varden's Anatomy of the Risen, the only useful book the Society ever printed. Fenwick will carry them "
                  "round. Read chapter four before you need it."},
        # Timm.
        {"npc": "timm", "kind": "greet", "cond": ["R:q3"],
         "text": "Gerald's on the bench. The arm. I've named it Gerald. Don't laugh. It only twitches when it's cold, and "
                 "it's always cold."},
        {"npc": "timm", "kind": "greet", "cond": ["A:q1"],
         "text": "Timm Vetch, apprentice. That's the sleeve everyone stares at. Go on, ask. Everyone asks."},
        {"npc": "timm", "kind": "greet",
         "text": "Timm Vetch. Apprentice surgeon. One day just surgeon. One day, Elspeth says, if I stop fidgeting."},
        {"npc": "timm", "kind": "option", "cond": ["!R:q3"], "text": "What happened to your arm?", "action": "say", "emote": 1,
         "reply": "Eight months ago. After I died, mind; not before. A beam came down in the Apothecarium's cellars. By the "
                  "time they dug me out it was grey to the shoulder. We don't heal, $n. People think that because we're "
                  "dead, nothing more can happen to us. Everything can still happen to us. It just doesn't get better."},
        {"npc": "timm", "kind": "option", "cond": ["I:q5"], "text": "Let's fit Agnes's brace.",
         "action": "credit", "quest": "q5", "credit": "brace_credit", "emote": 1,
         "reply": "Strap one above the knee. Strap two below. The hinge sits on the joint... not there, there. (The brace "
                  "clicks into place. Timm checks every buckle twice, then a third time when Elspeth looks over.) It's not "
                  "a hand. It's better than a hand. It doesn't twitch."},
        {"npc": "timm_bench", "kind": "greet",
         "texts": ["Design five. Springs in every finger, no more twitching. ...It twitched. Design six, then.",
                   "A Deathguard came in yesterday wanting a hook. A hook! I made him a hand. He cried. I think he cried. "
                   "Hard to tell with us.",
                   "Elspeth lets me do the stitching now. Only the straight bits. I do very straight bits."]},
        {"npc": "timm_caravan", "kind": "greet",
         "text": "Six brass springs, two dozen screws and a box of watch gears from Gilneas, which won't sell to us, so from "
                 "whoever's buying from Gilneas. The Quartermaster wants it in triplicate. I've only the one hand that writes."},
        # Fenwick.
        {"npc": "fenwick", "kind": "greet",
         "text": "Fenwick Pike. Hold still, I'm looking at your seams. ...You're fine. You'd be amazed how many aren't."},
        {"npc": "fenwick", "kind": "option", "cond": ["I:q5"], "text": "I'm ready to help with Agnes's leg.",
         "action": "credit", "quest": "q5", "credit": "fenwick_credit", "emote": 1,
         "reply": "Hold here. Both hands. Don't squeeze; steady. (Fenwick cuts the old wrappings away, washes the wound with "
                  "something that smells like a forge, picks grit and splinters out with a long needle, and binds the leg "
                  "straight between two boards, humming an old marching tune the whole time.) There. She'll hold. They "
                  "mostly do, if you give them something to hold on to."},
        {"npc": "fenwick_hall", "kind": "greet", "cond": ["M:voluntary"],
         "text": "Bandages, salves, a little something for the complexion. Gray dye sells best; nobody wants to look fresh. "
                 "And the Society's tonics, for those who've signed for them. Ask Elspeth first. Everyone asks Elspeth first."},
        {"npc": "fenwick_hall", "kind": "greet",
         "text": "Bandages, salves, a little something for the complexion. Gray dye sells best; nobody round here wants to "
                 "look fresh. And if you'd like to learn to tie a proper bandage, I teach. Elspeth says I'm patient. I've "
                 "had practice."},
        # The travellers, in the tent while it's built.
        {"npc": "jory", "kind": "greet",
         "text": "Jory Haskett. Carter. Or I was, before the horse decided it had better things to do than be eaten."},
        {"npc": "nan", "kind": "greet",
         "text": "Don't mind me, dear. I'm only lying here being brave. It's harder than it looks."},
        {"npc": "corwin", "kind": "greet",
         "text": "I'm... I'm fine. I'm a Deathguard. Recruit. We're supposed to be fine. Is it normal, that I can't feel "
                 "the other fingers either?"},
        {"npc": "jory", "kind": "option", "cond": ["I:q1"], "text": "How are you holding up?",
         "action": "credit", "quest": "q1", "credit": "traveler_credit", "marker": "spoke_jory", "emote": 1,
         "reply": "Holding up? Holding on, more like. Worgen, out of the Silverpine trees, three of them. Went for the horse "
                  "first, then me. Took a good bite of this arm and spat it out. Apparently I don't taste right any more. "
                  "First compliment I've had in years."},
        {"npc": "nan", "kind": "option", "cond": ["I:q1"], "text": "How are you holding up?",
         "action": "credit", "quest": "q1", "credit": "traveler_credit", "marker": "spoke_nan", "emote": 1,
         "reply": "Ribs. The cart went over on me when the horse bolted. I can hear them grinding when I breathe, which is "
                  "a funny thing to hear when you don't need to breathe. The surgeon says I'm lucky. I'm a hundred and four, "
                  "counting the dead years. I'm owed some luck."},
        {"npc": "corwin", "kind": "option", "cond": ["I:q1"], "text": "How are you holding up?",
         "action": "credit", "quest": "q1", "credit": "traveler_credit", "marker": "spoke_corwin", "emote": 1,
         "reply": "Three fingers. I can't feel them, which is right, I suppose, since they're gone. But I can't feel the "
                  "others either. Is that normal? The surgeon says it's normal. She says it like she's said it before. "
                  "A lot."},
        {"npc": "jory", "kind": "option", "cond": ["I:q4"], "text": "The Society wants to try its remedies on patients here. What do you think?",
         "action": "credit", "quest": "q4", "credit": "patient_credit", "marker": "asked_jory", "emote": 1,
         "reply": "If they'd pay me? I'd let them try anything short of setting me alight. ...Actually, ask them about "
                  "the alight. I've been cold for nine years."},
        {"npc": "nan", "kind": "option", "cond": ["I:q4"], "text": "The Society wants to try its remedies on patients here. What do you think?",
         "action": "credit", "quest": "q4", "credit": "patient_credit", "marker": "asked_nan", "emote": 1,
         "reply": "Try things on me? I've been tried on, dear. By the plague, by the Scourge, by a cart. I'd like "
                  "something to be my decision, for once. Ask me first. That's all. Ask, and listen to the answer."},
        {"npc": "corwin", "kind": "option", "cond": ["I:q4"], "text": "The Society wants to try its remedies on patients here. What do you think?",
         "action": "credit", "quest": "q4", "credit": "patient_credit", "marker": "asked_corwin", "emote": 1,
         "reply": "Would it hurt? Would it bring the fingers back? Would I be... I'm sorry. I don't know. I don't think I'd "
                  "want to be something they write down in a book. Is that a stupid thing to want?"},
        # Agnes: in the ward (The First Patient), then about Brill.
        {"npc": "agnes", "kind": "greet",
         "text": "Agnes Morrow. Traveller, until my leg had other ideas. If you're the help, help. If you're the "
                 "surgeon, I'm ready. If you're a priest, go away."},
        {"npc": "agnes_day", "kind": "greet",
         "texts": ["Round the yard, twice. Rane says three times by the end of the week. I say four. We'll see who's dead "
                   "first. Ha.",
                   "The brace creaks when I'm going uphill. Timm says that's a feature. Timm says a lot of things are "
                   "features.",
                   "I keep meaning to leave. The road's right there. But then someone new comes up it on a stretcher, "
                   "and I sit with them till Rane's ready, because somebody sat with me."]},
        {"npc": "agnes_evening", "kind": "greet",
         "text": "I walk to the square of an evening and read the Board. Then I walk back. That's all. Nine days I "
                 "couldn't. I like to read the Board."},
        # The ward's patients, once it's open.
        {"npc": "patient_day", "kind": "greet",
         "texts": ["The surgeon says I'll keep the hand. I didn't know that was in question. Nobody tells you anything.",
                   "I came in for a stitch and she found three more things. She always finds three more things.",
                   "Ghoul bite. From before. It's been bothering me for six years and I finally came in. Don't tell my wife.",
                   "The orderly sings while he stitches. Badly. It helps, somehow."]},
        {"npc": "patient_night", "kind": "greet",
         "texts": ["Can't sleep. Well. I never sleep. Can't lie still, I mean. Neither can the leg.",
                   "The lad with the brass arm came by at midnight to check my splint. I think he doesn't sleep either.",
                   "Quiet in here at night. The surgeon sits by the door with a lamp and a book. She doesn't turn the "
                   "pages. She's listening."]},
        # The Society's man, of a morning.
        {"npc": "rep", "kind": "greet", "cond": ["M:voluntary"],
         "text": "Apothecary Crell, Royal Apothecary Society. I have three volunteers and a register that must be "
                 "countersigned by the surgeon in triplicate. I've grown rather fond of triplicate. It's the only thing "
                 "here that's fond of me."},
        {"npc": "rep", "kind": "greet",
         "text": "Apothecary Crell, Royal Apothecary Society. I'm not here to conduct research. The charter forbids it. "
                 "I'm here to read the charter. Every morning. In case it's changed."},
        # The builders, and Oswin.
        {"npc": "worker", "kind": "greet",
         "texts": ["Roof's good. Floor's good. Walls are good. Surgeon still found eleven things wrong with it.",
                   "Working next to a graveyard. Rudd says it's quiet. It's not quiet. It's just not loud yet.",
                   "Don't go in the tent. The orderly sings."]},
        {"npc": "oswin", "kind": "greet",
         "text": "Oswin Thatcher. Rudd borrowed me. The surgeon wants the doorway wide enough for a stretcher and a "
                 "ghoul side by side. I asked her why a ghoul. She said 'experience.'"},
        # Carolai with her basket, of an evening (her own menu is src/BrillHome.cpp's; this is her at the hall).
        {"npc": "carolai", "kind": "greet", "cond": ["CAROLAI_HOME"],
         "text": "Willowbark and comfrey for the surgeon. I'll be home in a moment; I only have to watch her check every "
                 "bottle. She checks every bottle. I like that in a woman. Not too much."},
        {"npc": "carolai", "kind": "greet", "cond": ["LOVERS"],
         "text": "There you are. If you're hurt, my love, you come to me first. Not her. Me. I'll know what to do. I've "
                 "been practising."},
        {"npc": "carolai", "kind": "greet", "cond": ["FRIENDS"],
         "text": "Hello, friend. I bring the surgeon a basket every evening. She reads every label before she asks what's "
                 "in it. Nobody in Brill has ever read my labels first."},
        {"npc": "carolai", "kind": "greet",
         "text": "Carolai Anise. Herbal preparations for the surgeon: comfrey, willowbark, a sleeping draught. She won't let "
                 "Johaan near her patients. She lets me. I've decided not to find that suspicious."},
        # Carolai at her shop, on the hall (lovers, friends, or neither).
        {"npc": CAROLAI, "kind": "option", "cond": ["R:q5", "LOVERS"], "text": "(Ask her about the Surgeon's Hall.)",
         "action": "say", "emote": 1,
         "reply": "I take Elspeth a basket every evening. She holds every bottle up to the light before it goes near a "
                  "patient. I like her, my love. She doesn't trust anyone either. If you're ever hurt, you come to me "
                  "first. Not to her. To me."},
        {"npc": CAROLAI, "kind": "option", "cond": ["R:q5", "FRIENDS"], "text": "(Ask her about the Surgeon's Hall.)",
         "action": "say", "emote": 1,
         "reply": "Elspeth Rane buys my willowbark by the sack now. She's the first person in Brill who ever read the "
                  "label before asking me what's in it. If anything happens to you, friend, I want to hear it from you. "
                  "Not from her ledger."},
        {"npc": CAROLAI, "kind": "option", "cond": ["R:q5", "!LOVERS", "!FRIENDS"], "text": "(Ask her about the Surgeon's Hall.)",
         "action": "say", "emote": 1,
         "reply": "The surgeon by the cemetery sends for my willowbark every evening. She won't let Johaan near her "
                  "patients. She lets me. I've decided to take that as a compliment."},
        # Holding Together: the linen and the splints (each once).
        {"npc": WINTERS, "kind": "option", "cond": ["I:q1"], "text": "Surgeon Rane needs linen for bandages. Eight rolls.",
         "action": "credit", "quest": "q1", "credit": "supplies_credit", "marker": "got_linen", "emote": 1,
         "reply": "Linen for the new surgeon? Eight rolls, clean, none of the grey. Tell her it's on credit, and tell her "
                  "if she cuts it crooked I'll know."},
        {"npc": FOREMAN, "kind": "option", "cond": ["I:q1"], "text": "Surgeon Rane needs four splints.",
         "action": "credit", "quest": "q1", "credit": "supplies_credit", "marker": "got_splints", "emote": 1,
         "reply": "Splints. Straight ash, planed smooth; I've lath ends that'll do. Tell her if she ever needs a roof, I "
                  "do those too, but they don't fit in a sling."},
        # A Steady Hand: needles from Abigail Shiel, glass from Holland.
        {"npc": ABIGAIL, "kind": "option", "cond": ["I:q2"], "text": "Surgeon Rane needs needles and stitching thread.",
         "action": "credit", "quest": "q2", "credit": "needle_credit", "emote": 1,
         "reply": "Needles and gut for the surgeon. I'll give her the sailmaker's ones; they go through anything. Don't "
                  "tell me what anything is."},
        {"npc": HOLLAND, "kind": "option", "cond": ["I:q2"], "text": "Surgeon Rane needs clean glass and something to clean wounds with.",
         "action": "credit", "quest": "q2", "credit": "glass_credit", "emote": 1,
         "reply": "Bottles, yes, she's welcome to bottles, and carbolic, and spirit of wine. And would she like to try "
                  "this? It's a tincture for the preservation of... no? No. Tell her I asked nicely."},
        # A Spare Arm and a Leg: straps and gears from the builder's yard.
        {"npc": FOREMAN, "kind": "option", "cond": ["I:q3"], "text": "Timm Vetch needs leather straps and small gears for an arm.",
         "action": "credit", "quest": "q3", "credit": "strap_credit", "emote": 1,
         "reply": "An arm, is it? The lad with the sleeve. Here: harness leather, good and supple, and a tin of clock gears "
                  "off a dead wagon. Don't ask whose. Tell him if it works, I want to see it wave."},
        # The Patient Comes First: Johaan.
        {"npc": JOHAAN, "kind": "option", "cond": ["I:q4"], "text": "Surgeon Rane would like your view of the Society's proposal.",
         "action": "credit", "quest": "q4", "credit": "johaan_credit", "emote": 1,
         "reply": "Rane. She came to my door once to tell me a tincture of mine was a crime against the liver. ...Tell her "
                  "this, then. The Society does not ask. It never has. If she wants her patients asked, she must write it "
                  "down and make the Society sign it. That is the only kind of conscience it recognises."},
        # Repairs Required (daily): linen, thread, Dillinger's shoulder, Hamlin's hand.
        {"npc": WINTERS, "kind": "option", "cond": ["I:repairs"], "text": "Surgeon Rane needs clean linen again.",
         "action": "credit", "quest": "repairs", "credit": "linen_credit", "emote": 1,
         "reply": "Again? She goes through linen like the Scourge went through Andorhal. Here. And take the heavy roll for "
                  "Dillinger; he bleeds through the cheap stuff."},
        {"npc": ABIGAIL, "kind": "option", "cond": ["I:repairs"], "text": "Surgeon Rane needs more thread.",
         "action": "credit", "quest": "repairs", "credit": "thread_credit", "emote": 1,
         "reply": "Gut, heavy and light. I've started stocking it by the yard. It outsells candles now. I find that a very "
                  "Brill sentence."},
        {"npc": DILLINGER, "kind": "option", "cond": ["I:repairs"], "text": "Hold still. Surgeon's orders.",
         "action": "credit", "quest": "repairs", "credit": "dillinger_credit", "emote": 1,
         "reply": "It's nothing. ...Fine. Fine. (He holds still while you close the old crossbow wound in his shoulder.) "
                  "A Scarlet at the river, in the spring. My shoulder's still annoyed about it."},
        {"npc": HAMLIN, "kind": "option", "cond": ["I:repairs"], "text": "Let me see that hand.",
         "action": "credit", "quest": "repairs", "credit": "hamlin_credit", "emote": 1,
         "reply": "It's fine! It's mushroom paste. Very healing. ...It's gone blue. Is it meant to go blue? (You clean the "
                  "paste out and stitch the cut while Hamlin explains which mushrooms are good for wounds. None of them, "
                  "it turns out.)"},
    ],
}
