#!/usr/bin/env python3
"""The start quests the Draenei, the Forsaken and the Tauren alone have, cloned for the void elves, the
nightborne, the Lightforged and the Zandalari: the same quests from the same people, for the new race alone (the originals stay
their race's, untouched), with the quest-givers' words taking in who the player is before
sending them down the same road.

    python3 tools/quests.py WORLD_SQL_DIR    the core's data/sql/base/db_world

Writes data/sql/chromiecraft/world/allied_races_quests.sql (the clones: quest_template, its addon, texts,
map points, starters and enders) and data/retail/cloned_quests.json (which quests were cloned:
tools/build_data.py opens every other quest of the start race to the new race, these it leaves).

A clone's id is the original's plus 950000 (void elves, nightborne) or 960000 (Lightforged, Zandalari). Where a chain's next quest is cloned too, the clone
leads to the clone; where it isn't, to the original (open to the race by then).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sqlrows  # noqa: E402

MODULE = os.path.dirname(HERE)
OFFSET = {"voidelf": 950000, "nightborne": 950000, "lightforged": 960000, "zandalari": 960000}
BIT = {"voidelf": 1 << 14, "nightborne": 1 << 15, "lightforged": 1 << 16, "zandalari": 1 << 17}

# The quests cloned: the start race's own in its first zones (quests any Alliance or Horde
# character takes aren't here: those open to the race as they are).
CLONED = {
    "voidelf": [9279, 9280, 9283, 9463, 9473, 9505, 9612,            # Ammen Vale and Azuremyst Isle
                9603, 9604, 9605, 9606,                              # Bloodmyst: the hippogryph
                9753, 9756, 9759, 9760, 9761, 9762],                 # Bloodmyst: the prophecy
    "nightborne": [363,                                              # Deathknell (Welcome!, the Collector's Edition voucher, isn't cloned)
                   6321, 6323, 6322, 6324],                          # Silverpine: the ride to the Undercity
    "lightforged": [9279, 9280, 9283, 9463, 9473, 9505, 9612,        # the Draenei's, as the void elves'
                    9603, 9604, 9605, 9606,
                    9753, 9756, 9759, 9760, 9761, 9762],
    "zandalari": [747,                                               # Red Cloud Mesa: The Hunt Begins (the Horde's; the clone greets a Zandalari)
                  754, 758, 760,                                     # Mulgore: the Cleansing chain, the Tauren's alone
                  854,                                               # Journey to the Crossroads
                  6361, 6362, 6363, 6364],                           # the ride to Thunder Bluff
}

# What the quest-givers say to the new race before the quest's own words. $n: the player's name,
# $r: the race (Void Elf, Nightborne), $c: the class, $B: a line break (the game fills them in).
GREETING = {
    "voidelf": [
        "You are no draenei, yet the sea gave you to us with our own wounded. Ren'dorei, they call your kind: elves the Void has marked. The Light does not ask where a hand comes from, $n, only whether it will help.$B$B",
        "A $r among us. Word came from the Exodar that Umbric's exiles had taken the Alliance's side; I did not think to meet one here. Our need is the same as yours, then.$B$B",
        "You stand out among us, $n, and I'll not pretend otherwise. But you have bled for this shore like any draenei, and that is what I judge by.$B$B",
        "The Prophet himself said the ren'dorei would find their way to us. Whatever the Void left in you, it has not taken your will to help.$B$B",
    ],
    "nightborne": [
        "You're no corpse of ours, shal'dorei, though you slept like one. The Dark Lady's word came ahead of you: Suramar's children would learn the Forsaken's ways from the ground up, and the ground starts here, in Deathknell.$B$B",
        "A nightborne, in Tirisfal. Ten thousand years behind your shield, and now you walk among the dead. Good. We have use for an arcanist who doesn't flinch.$B$B",
        "Don't mind the stares, $n. The living are rare here, and your kind rarer. You wear the Horde's colors; that is all Deathknell asks.$B$B",
        "Suramar's magisters sent us their finest, they said. We'll see. Here, $r, the work speaks louder than the lineage.$B$B",
    ],
    "lightforged": [
        "You shine, $n, even in this gloom. Lightforged: so the Army of the Light's kin call themselves, and the Prophet said they would come to us one day. I did not think it would be out of the surf, among our own wounded.$B$B",
        "A Lightforged among us. The Exodar carried us here; the Light carried you, by the look of it. The need on this shore is the same for both.$B$B",
        "The Vindicaar's children, here. Your people fought the Legion for a thousand years; this will be a small thing to you, but it is not small to us.$B$B",
        "Your light does not fail, $r, even here. Lend it to us.$B$B",
    ],
    "zandalari": [
        "A Zandalari on Mulgore's grass, far from your golden city. The Earth Mother does not ask where a child was born, $n, only how it walks. Walk with us a while.$B$B",
        "Zandalari. Your people stood with the Horde against the Alliance's fleets; the shu'halo remember debts. This one is paid in work, not words.$B$B",
        "Your kind keeps loa; ours keeps the Earth Mother. Both ask the same of us this morning, $r: that the land be cared for.$B$B",
        "The elders said a troll of Zandalar would come down the mesa in the Horde's colors. You are taller than I pictured. Come, the work doesn't wait.$B$B",
    ],
}
# A quest whose own first words don't fit the new race gets these in their place.
REWRITTEN = {
    ("lightforged", 9279): "You... you are awake. And you shine, even through the wreck. A Lightforged: one of the Army of the Light's own, by your markings, washed up on this shore with the rest of us when the ship broke apart.$B$BWhatever the Light meant by bringing you here, $n, we have need of every pair of hands. Will you help us?",
    ("zandalari", 747): "A Zandalari, come down from the golden city to hunt with the shu'halo. You have a promising air about you, troll, and you will prove yourself to the tribe. Perhaps someday soon you will be welcomed into the great city of Thunder Bluff; before that can happen you must prove yourself to my father, Chief Hawkwind.$B$BUp here on Red Cloud Mesa we pride ourselves on keen hunting skills. Our supply of meats has run low and we require fresh plainstrider meat. Hunt the plainstriders of Red Cloud Mesa and return to me with their meat.",
    ("voidelf", 9279): "You... you are awake. And you are not one of ours. A ren'dorei, by the look of you: one of the void elves the Exodar's letters spoke of, washed up with the rest of us when the ship broke apart.$B$BWhatever brought you to this shore, $n, you are alive, and we have need of every pair of hands. Will you help us?",
    ("nightborne", 363): "About time you woke up. We were about to toss you into the fire with the others before someone noticed you were still breathing. A shal'dorei, they tell me: one of Suramar's nightborne, sent to learn how the Forsaken do things.$B$BWell. This is how. I am Mordo, the caretaker of the crypt of Deathknell, and you are nobody's slave here.$B$BSpeak with Shadow Priest Sarvis in the chapel at the base of the hill; he will tell you more of what you must know.$B$BTo get out of this crypt, take the steps up to the surface. Follow the road down to the chapel to find Sarvis.",
}
TEXT_FIXES = {
    "voidelf": [("fellow draenei", "friend of the draenei"), ("my fellow draenei", "my friend"), ("You are a draenei", "You stand with the draenei"),
                ("as a draenei", "as one who stands with the draenei")],
    "nightborne": [("fellow Forsaken", "friend of the Forsaken"), ("my fellow Forsaken", "my friend"), ("You are Forsaken", "You stand with the Forsaken"),
                   ("as a Forsaken", "as one who stands with the Forsaken"), ("undead such as yourself", "one who stands with us")],
    "lightforged": [("fellow draenei", "kin of the draenei"), ("my fellow draenei", "my kin"), ("You are a draenei", "You are of the draenei"),
                    ("as a draenei", "as one of the draenei's kin")],
    "zandalari": [("fellow tauren", "friend of the tauren"), ("my fellow tauren", "my friend"), ("You are a tauren", "You stand with the tauren"),
                  ("as a tauren", "as one who stands with the tauren"), ("young tauren", "young troll"), ("tauren such as yourself", "one who stands with us")],
}


def dependents(addons, roots):
    """The quests that need one of [roots] done first, and those that need those: with the
    original closed to the new race, the clone is the only way to open them."""
    ids = list(roots)
    seen = set(ids)
    grew = True
    while grew:
        grew = False
        for a in addons:
            q = int(a["ID"])
            if q not in seen and abs(int(a.get("PrevQuestID") or 0)) in seen:
                ids.append(q)
                seen.add(q)
                grew = True
    return ids


# SmartAI events (accepted, rewarded) and actions (quest credit) that name a quest by id.
SMART_QUEST_EVENTS = {19, 20}
SMART_QUEST_ACTIONS = {15, 26}
# Conditions on a quest's state: rewarded, taken, complete; and none (neither taken nor rewarded).
CONDITION_QUEST_STATES = {8, 9, 28}
CONDITION_QUEST_NONE = 14
SMART_ID_GAP = 1000             # the clones' script rows: their entry's highest id plus this, and on


def bindings(T, cloned, offset):
    """What the world database binds to an original quest's id, made the clones' too: a
    creature's script that starts on the quest's acceptance or reward (Demolitionist Legoso's
    escort on Ending Their World) gets a row for each clone; one that credits the quest (the
    escort's end) credits each clone as well, in the same chain of linked rows; a condition on
    the quest's state (a gossip shown while it's taken, or once it's done) holds for a clone the
    same way: a condition that it is (rewarded, taken, complete) is met by either, one that it
    isn't needs both. The originals' rows stay as they are but for a link to the new rows."""
    clones_of = {}
    for race, ids in cloned.items():
        for q in ids:
            clones_of.setdefault(q, []).append(q + offset[race])
    out = ["\n-- The scripts and conditions bound to the originals, for their clones too (tools/quests.py, bindings)."]
    cols, rows = T("smart_scripts")
    by_entry = {}
    for r in rows:
        by_entry.setdefault((r["entryorguid"], r["source_type"]), []).append(r)
    new_rows, links = [], []
    for key in sorted(by_entry, key=lambda k: (int(k[0]), int(k[1]))):
        entry_rows = sorted(by_entry[key], key=lambda r: int(r["id"]))
        next_id = [max(int(r["id"]) for r in entry_rows) + SMART_ID_GAP]
        base = next_id[0]

        def alloc():
            next_id[0] += 1
            return next_id[0] - 1

        for r in entry_rows:
            event_q = int(r["event_param1"]) if int(r["event_type"]) in SMART_QUEST_EVENTS else 0
            action_q = int(r["action_param1"]) if int(r["action_type"]) in SMART_QUEST_ACTIONS else 0
            q = event_q if event_q in clones_of else (action_q if action_q in clones_of else 0)
            if not q:
                continue
            made = []
            for clone in clones_of[q]:
                c = dict(r)
                c["id"] = alloc()
                if event_q in clones_of:
                    c["event_param1"] = event_q + (clone - q)
                if action_q in clones_of:
                    c["action_param1"] = action_q + (clone - q)
                c["comment"] = (r["comment"] or "") + " (allied races: the clone %d)" % clone
                made.append(c)
            if int(r["event_type"]) == 61:
                # a linked row: the clones' rows go into the chain after it
                for a, b in zip(made, made[1:]):
                    a["link"] = b["id"]
                made[-1]["link"] = r["link"]
                links.append((key, r["id"], made[0]["id"]))
            elif not event_q in clones_of:
                for c in made:
                    c["link"] = 0                          # its own event: a link would run the original's chain twice
            new_rows.extend(made)
        if any(int(c["id"]) >= base for c in new_rows if (c["entryorguid"], c["source_type"]) == key):
            out.append("DELETE FROM `smart_scripts` WHERE `entryorguid` = %s AND `source_type` = %s AND `id` >= %d;" % (key[0], key[1], base))
    if new_rows:
        out.append("INSERT INTO `smart_scripts` (%s) VALUES\n%s;" % (", ".join("`%s`" % c for c in cols),
                   ",\n".join("(" + ", ".join(sqlrows.quote(r[c]) for c in cols) + ")" for r in new_rows)))
    for (entry, source), row_id, first in links:
        out.append("UPDATE `smart_scripts` SET `link` = %d WHERE `entryorguid` = %s AND `source_type` = %s AND `id` = %s;" % (first, entry, source, row_id))

    cols, rows = T("conditions")
    groups = {}
    for r in rows:
        key = (r["SourceTypeOrReferenceId"], r["SourceGroup"], r["SourceEntry"], r["SourceId"])
        groups.setdefault(key, []).append(r)
    added = []
    for key in sorted(groups, key=lambda k: tuple(int(x) for x in k)):
        members = groups[key]
        next_else = max(int(r["ElseGroup"]) for r in members) + 1
        for else_group in sorted({int(r["ElseGroup"]) for r in members}):
            group = [r for r in members if int(r["ElseGroup"]) == else_group]
            bound = [r for r in group if int(r["ConditionValue1"]) in clones_of and
                     int(r["ConditionTypeOrReference"]) in CONDITION_QUEST_STATES | {CONDITION_QUEST_NONE}]
            if not bound:
                continue
            for r in bound:
                q = int(r["ConditionValue1"])
                positive = int(r["ConditionTypeOrReference"]) in CONDITION_QUEST_STATES and not int(r["NegativeCondition"])
                for clone in clones_of[q]:
                    if positive:
                        # "it is done": either the original or the clone, a group of its own
                        for g in group:
                            c = dict(g)
                            c["ElseGroup"] = next_else
                            if g is r:
                                c["ConditionValue1"] = clone
                            added.append(c)
                        next_else += 1
                    else:
                        # "it isn't": neither, in the same group
                        c = dict(r)
                        c["ConditionValue1"] = clone
                        added.append(c)
    if added:
        out.append("INSERT IGNORE INTO `conditions` (%s) VALUES\n%s;" % (", ".join("`%s`" % c for c in cols),
                   ",\n".join("(" + ", ".join(sqlrows.quote(r[c]) for c in cols) + ")" for r in added)))
    print("bindings: %d script rows, %d links, %d condition rows for the clones" % (len(new_rows), len(links), len(added)))
    return out


def main(world):
    T = lambda name: sqlrows.table(os.path.join(world, name + ".sql"))
    out = ["-- The start quests of the Draenei and the Forsaken, cloned for the void elves and the nightborne\n"
           "-- (mod-allied-races, tools/quests.py): the originals are untouched. Safe to run again."]
    quests_cols, quests = T("quest_template")
    by_id = {int(q["ID"]): q for q in quests}
    addon_cols, addons = T("quest_template_addon")
    addon_by_id = {int(a["ID"]): a for a in addons}
    offer_cols, offers = T("quest_offer_reward")
    request_cols, requests = T("quest_request_items")
    details_cols, details = T("quest_details")
    poi_cols, pois = T("quest_poi")
    poi_point_cols, poi_points = T("quest_poi_points")
    cqs_cols, cqs = T("creature_queststarter")
    cqe_cols, cqe = T("creature_questender")
    gqs_cols, gqs = T("gameobject_queststarter")
    gqe_cols, gqe = T("gameobject_questender")
    roots = {race: list(ids) for race, ids in CLONED.items()}
    for race in CLONED:
        CLONED[race] = dependents(addons, roots[race])
    def clone_id(race, q):
        return q + OFFSET[race] if q in CLONED[race] else q

    def insert(table, cols, rows):
        if not rows:
            return
        out.append("INSERT INTO `%s` (%s) VALUES\n%s;" % (table, ", ".join("`%s`" % c for c in cols),
                   ",\n".join("(" + ", ".join(sqlrows.quote(r[c]) for c in cols) + ")" for r in rows)))

    for race, ids in CLONED.items():
        offset = OFFSET[race]
        out.append("\n-- %s\nDELETE FROM `quest_template` WHERE `ID` IN (%s);" % (race, ", ".join(str(q + offset) for q in ids)))
        for table in ("quest_template_addon", "quest_offer_reward", "quest_request_items", "quest_details", "quest_poi", "quest_poi_points"):
            out.append("DELETE FROM `%s` WHERE `%s` IN (%s);" % (table, "ID" if table.startswith("quest_template") or table in ("quest_offer_reward", "quest_request_items", "quest_details") else "QuestID",
                                                                 ", ".join(str(q + offset) for q in ids)))
        for table in ("creature_queststarter", "creature_questender", "gameobject_queststarter", "gameobject_questender"):
            out.append("DELETE FROM `%s` WHERE `quest` IN (%s);" % (table, ", ".join(str(q + offset) for q in ids)))
        rows = []
        for n, qid in enumerate(ids):
            q = dict(by_id[qid])
            q["ID"] = qid + offset
            q["AllowableRaces"] = BIT[race]
            q["RewardNextQuest"] = clone_id(race, int(q["RewardNextQuest"] or 0))
            text = q["QuestDescription"] or ""
            for a, b in TEXT_FIXES[race]:
                text = text.replace(a, b)
            if (race, qid) in REWRITTEN:
                text = REWRITTEN[(race, qid)]
            elif qid in roots[race]:
                text = GREETING[race][n % len(GREETING[race])] + text
            q["QuestDescription"] = text
            for key in ("LogDescription", "QuestCompletionLog", "AreaDescription"):
                if q.get(key):
                    for a, b in TEXT_FIXES[race]:
                        q[key] = q[key].replace(a, b)
            q["VerifiedBuild"] = 12340
            rows.append(q)
        insert("quest_template", quests_cols, rows)
        rows = []
        for qid in ids:
            a = dict(addon_by_id.get(qid) or {c: 0 for c in addon_cols})
            a["ID"] = qid + offset
            for key in ("PrevQuestID", "NextQuestID", "BreadcrumbForQuestId"):
                v = int(a.get(key) or 0)
                a[key] = (-1 if v < 0 else 1) * clone_id(race, abs(v)) if v else 0
            v = int(a.get("ExclusiveGroup") or 0)
            a["ExclusiveGroup"] = (-1 if v < 0 else 1) * clone_id(race, abs(v)) if v else 0
            rows.append(a)
        insert("quest_template_addon", addon_cols, rows)
        for table, cols, source, key in (("quest_offer_reward", offer_cols, offers, "ID"), ("quest_request_items", request_cols, requests, "ID"),
                                         ("quest_details", details_cols, details, "ID"), ("quest_poi", poi_cols, pois, "QuestID"),
                                         ("quest_poi_points", poi_point_cols, poi_points, "QuestID")):
            rows = []
            for r in source:
                if int(r[key]) in ids:
                    c = dict(r)
                    c[key] = int(r[key]) + offset
                    if "RewardText" in c and c["RewardText"]:
                        for a, b in TEXT_FIXES[race]:
                            c["RewardText"] = c["RewardText"].replace(a, b)
                    if "CompletionText" in c and c["CompletionText"]:
                        for a, b in TEXT_FIXES[race]:
                            c["CompletionText"] = c["CompletionText"].replace(a, b)
                    rows.append(c)
            insert(table, cols, rows)
        for table, cols, source in (("creature_queststarter", cqs_cols, cqs), ("creature_questender", cqe_cols, cqe),
                                    ("gameobject_queststarter", gqs_cols, gqs), ("gameobject_questender", gqe_cols, gqe)):
            rows = []
            for r in source:
                if int(r["quest"]) in ids:
                    c = dict(r)
                    c["quest"] = int(r["quest"]) + offset
                    rows.append(c)
            insert(table, cols, rows)
    out.extend(bindings(T, CLONED, OFFSET))
    os.makedirs(os.path.join(MODULE, "data", "sql", "chromiecraft", "world"), exist_ok=True)
    with open(os.path.join(MODULE, "data", "sql", "chromiecraft", "world", "allied_races_quests.sql"), "w", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(MODULE, "data", "retail", "cloned_quests.json"), "w") as f:
        json.dump(CLONED, f, indent=1)
    for race, ids in CLONED.items():
        print("%s: %d quests cloned (%d of them because they need one cloned first): %s" % (
            race, len(ids), len(ids) - len(roots[race]), ", ".join(by_id[q]["LogTitle"] for q in ids)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
