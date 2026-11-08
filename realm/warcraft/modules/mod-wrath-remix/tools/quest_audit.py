#!/usr/bin/env python3
"""Resolves the Wrath Remix guide's candidate quests (data/candidates.tsv) against a world database.

The guide names its campaign's original quests by title. A title isn't an id: Alliance and Horde
often have a quest each by the same name, some titles are written differently in the game, and some
aren't 3.3.5a quests at all. This looks every title up in the world database the realm runs on and
writes data/campaign_manifest.csv: one row per quest found (or one "missing" row per title), with
what the campaign needs to know before it skips or keeps it: side, levels, zone, the quests before
and after it, its exclusive group, breadcrumbs, who starts and ends it and where, and whether it's
a daily, a group or a dungeon quest. data/quest_audit.md sums it up.

    python3 tools/quest_audit.py --mysql "mariadb -uroot acore_world"

--mysql is the command that runs SQL on stdin against the world database and prints tab-separated
rows (mariadb's batch output).
"""

import argparse
import csv
import os
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

ALLIANCE = 1 | 4 | 8 | 64 | 1024  # human, dwarf, night elf, gnome, draenei
HORDE = 2 | 16 | 32 | 128 | 512  # orc, undead, tauren, troll, blood elf

ZONES = {
    3537: "Borean Tundra", 495: "Howling Fjord", 65: "Dragonblight", 394: "Grizzly Hills",
    66: "Zul'Drak", 3711: "Sholazar Basin", 67: "The Storm Peaks", 210: "Icecrown",
    2817: "Crystalsong Forest", 4395: "Dalaran", 4197: "Wintergrasp", 1519: "Stormwind City",
    1637: "Orgrimmar", 1497: "Undercity", 4742: "Hrothgar's Landing", 206: "Utgarde Keep",
    4265: "The Nexus", 4196: "Drak'Tharon Keep", 4375: "Gundrak", 4272: "Halls of Lightning",
    4264: "Halls of Stone", 4809: "The Forge of Souls", 4813: "Pit of Saron",
    4820: "Halls of Reflection", 4812: "Icecrown Citadel", 3456: "Naxxramas", 4277: "Azjol-Nerub",
}

# Quest sorts (negative QuestSortID) that say what kind of quest it is.
SORTS = {-1: "Epic", -22: "Seasonal", -241: "Tournament", -284: "Special", -365: "Ahn'Qiraj War",
         -366: "Lunar Festival", -368: "Invasion", -369: "Midsummer", -370: "Brewfest",
         -373: "Firework", -374: "Noblegarden", -375: "Pilgrim's Bounty", -376: "Love is in the Air"}

QUEST_FLAG_DAILY = 0x1000
QUEST_FLAG_WEEKLY = 0x8000


def run_sql(mysql, sql):
    out = subprocess.run(shlex.split(mysql) + ["--batch", "--skip-column-names"], input=sql,
                         capture_output=True, text=True, check=True).stdout
    return [line.split("\t") for line in out.splitlines() if line]


def side(races):
    races = int(races)
    if races == 0 or (races & ALLIANCE and races & HORDE):
        return "both"
    if races & ALLIANCE:
        return "Alliance"
    if races & HORDE:
        return "Horde"
    return f"races {races}"


def sql_str(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--mysql", required=True, help="command running SQL on the world database")
    args = parser.parse_args()

    with open(os.path.join(DATA, "candidates.tsv"), encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    candidates = list(csv.DictReader(lines, delimiter="\t"))
    titles = sorted({c["title"] for c in candidates})

    found = {}
    for row in run_sql(args.mysql, f"""
        SELECT q.ID, q.LogTitle, q.QuestLevel, q.MinLevel, q.QuestSortID, q.QuestInfoID, q.AllowableRaces,
               q.Flags, q.SuggestedGroupNum, q.RewardNextQuest,
               COALESCE(a.PrevQuestID, 0), COALESCE(a.NextQuestID, 0), COALESCE(a.ExclusiveGroup, 0),
               COALESCE(a.BreadcrumbForQuestId, 0), COALESCE(a.AllowableClasses, 0),
               (q.RewardItem1 > 0) + (q.RewardItem2 > 0) + (q.RewardItem3 > 0) + (q.RewardItem4 > 0)
                 + (q.RewardChoiceItemID1 > 0) + (q.RewardChoiceItemID2 > 0) + (q.RewardChoiceItemID3 > 0)
                 + (q.RewardChoiceItemID4 > 0) + (q.RewardChoiceItemID5 > 0) + (q.RewardChoiceItemID6 > 0),
               (SELECT GROUP_CONCAT(DISTINCT s.id ORDER BY s.id) FROM creature_queststarter s WHERE s.quest = q.ID),
               (SELECT GROUP_CONCAT(DISTINCT s.id ORDER BY s.id) FROM gameobject_queststarter s WHERE s.quest = q.ID),
               (SELECT GROUP_CONCAT(DISTINCT e.id ORDER BY e.id) FROM creature_questender e WHERE e.quest = q.ID),
               (SELECT GROUP_CONCAT(DISTINCT e.id ORDER BY e.id) FROM gameobject_questender e WHERE e.quest = q.ID),
               (SELECT COUNT(*) FROM disables d WHERE d.sourceType = 1 AND d.entry = q.ID)
        FROM quest_template q LEFT JOIN quest_template_addon a ON a.ID = q.ID
        WHERE TRIM(q.LogTitle) IN ({", ".join(sql_str(t) for t in titles)})
        ORDER BY q.ID;"""):
        quest = dict(zip(["id", "title", "level", "min_level", "sort", "info", "races", "flags", "group",
                          "reward_next", "prev", "next", "exclusive", "breadcrumb_for", "classes",
                          "reward_items", "starter_npcs", "starter_objects", "ender_npcs",
                          "ender_objects", "disabled"], row))
        found.setdefault(quest["title"].strip().lower(), []).append(quest)

    # Where the starters and enders stand (their first spawn), by map and position.
    npcs = sorted({int(n) for qs in found.values() for q in qs
                   for field in ("starter_npcs", "ender_npcs") for n in (q[field] or "").split(",")
                   if n and n != "NULL"})
    where = {}
    if npcs:
        for npc, name, map_id, x, y in run_sql(args.mysql, f"""
            SELECT t.entry, t.name, c.map, ROUND(c.position_x), ROUND(c.position_y)
            FROM creature_template t LEFT JOIN creature c ON c.guid =
              (SELECT MIN(c2.guid) FROM creature c2 WHERE c2.id = t.entry)
            WHERE t.entry IN ({", ".join(map(str, npcs))});"""):
            where[npc] = f"{name} ({map_id}: {x} {y})" if map_id != "NULL" else f"{name} (not spawned)"

    def npc_names(field):
        return "; ".join(where.get(n, n) for n in (field or "").split(",") if n and n != "NULL")

    out_path = os.path.join(DATA, "campaign_manifest.csv")
    missing, ambiguous, rows = [], [], 0
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["chapter", "group", "title", "status", "id", "side", "level", "min_level", "zone",
                    "kind", "prev", "next", "reward_next", "exclusive", "breadcrumb_for", "classes",
                    "reward_items", "starter", "ender", "disabled"])
        for c in candidates:
            quests = found.get(c["title"].lower(), [])
            if not quests:
                missing.append(c)
                w.writerow([c["chapter"], c["group"], c["title"], "missing"] + [""] * 16)
                rows += 1
                continue
            if len(quests) > 1:
                ambiguous.append((c, quests))
            for q in quests:
                sort = int(q["sort"])
                zone = ZONES.get(sort, sort) if sort > 0 else SORTS.get(sort, sort)
                kind = []
                flags = int(q["flags"])
                if flags & QUEST_FLAG_DAILY:
                    kind.append("daily")
                if flags & QUEST_FLAG_WEEKLY:
                    kind.append("weekly")
                if int(q["group"]) > 0:
                    kind.append(f"group {q['group']}")
                if int(q["info"]) in (1, 41, 62, 81, 82, 83, 84, 85, 88, 89):
                    kind.append({1: "group", 41: "PvP", 62: "raid", 81: "dungeon", 82: "world event",
                                 83: "legendary", 84: "escort", 85: "heroic", 88: "raid 10",
                                 89: "raid 25"}[int(q["info"])])
                starter = npc_names(q["starter_npcs"]) or (f"object {q['starter_objects']}"
                                                            if q["starter_objects"] not in ("", "NULL") else "")
                ender = npc_names(q["ender_npcs"]) or (f"object {q['ender_objects']}"
                                                        if q["ender_objects"] not in ("", "NULL") else "")
                w.writerow([c["chapter"], c["group"], c["title"],
                            "found" if len(quests) == 1 else "found, one of several",
                            q["id"], side(q["races"]), q["level"], q["min_level"], zone, " ".join(kind),
                            q["prev"], q["next"], q["reward_next"], q["exclusive"], q["breadcrumb_for"],
                            q["classes"], q["reward_items"], starter, ender,
                            "disabled" if int(q["disabled"]) else ""])
                rows += 1

    with open(os.path.join(DATA, "quest_audit.md"), "w", encoding="utf-8") as f:
        f.write("# Quest audit\n\nThe guide's candidate quests (`candidates.tsv`) looked up in the world "
                "database by `tools/quest_audit.py`; every row is in `campaign_manifest.csv`.\n\n")
        f.write(f"- Titles: {len(candidates)} ({len(titles)} different)\n")
        f.write(f"- Found: {len(candidates) - len(missing)}, of which {len(ambiguous)} name more than one "
                "quest (usually an Alliance and a Horde one, or a quest and its repeat)\n")
        f.write(f"- Not in the world database by that title: {len(missing)}\n\n")
        if missing:
            f.write("## Not found\n\nNot a 3.3.5a quest by this title (a retail name, a typo, or a quest "
                    "that doesn't exist): each needs its real title or comes out of the campaign.\n\n")
            for c in missing:
                f.write(f"- Chapter {c['chapter']}, {c['group']}: {c['title']}\n")
            f.write("\n")
        if ambiguous:
            f.write("## Titles with several quests\n\n")
            for c, quests in ambiguous:
                ids = ", ".join(f"{q['id']} ({side(q['races'])}, level {q['level']})" for q in quests)
                f.write(f"- Chapter {c['chapter']}, {c['title']}: {ids}\n")
    print(f"{rows} rows in {out_path}; {len(missing)} titles not found, {len(ambiguous)} ambiguous")
    return 0


if __name__ == "__main__":
    sys.exit(main())
