#!/usr/bin/env python3
"""The Brill home's and town's quests on the maps: the game's own quest markers and Questie's.

Made from the module's world SQL (data/sql/chromiecraft/world/brill_home_world.sql and
brill_town_world.sql, made by tools/build_sql.py and tools/build_town.py), so run it after them:

- data/sql/chromiecraft/world/brill_quest_poi.sql: the game's quest markers (quest_poi and
  quest_poi_points, 3.3.5a's world map blobs and the quest tracker's map button) for each quest: a
  blob around the places each objective is done at (the objects that give it, the creatures to talk
  to or to kill) and one at whoever takes the quest back (objective -1). The game's own creatures'
  places are read from the world database as the file is applied.
- data/client/addon/BrillTown/BrillTown.lua (with BrillTown.toc): an add-on for Questie's 3.3.5 port
  (Questie-335), which doesn't know the module's quests and creatures. As Questie's database starts it
  adds them to the database's own runtime additions (QuestieDB's questDataOverrides,
  npcDataOverrides), and the quests' numbers to the list Questie checks a quest log's quests against:
  its tracker, its objective icons on the maps and minimap, its turn-in marks and its "!" at the
  givers (for the quests a character can take whenever the giver is there; not for those that wait on
  a choice, a project's stage or a character's own marks, which Questie can't know). The add-on is put
  into the client's Interface/AddOns by the module (src/BrillHomePatch.cpp) at the realm's start.

Coordinates are each zone's map percent (WorldMapArea.dbc's bounds for the zones the quests reach).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SQL_DIR = os.path.join(DATA, "sql", "chromiecraft", "world")
SOURCES = [os.path.join(SQL_DIR, "brill_home_world.sql"), os.path.join(SQL_DIR, "brill_town_world.sql")]
POI_OUT = os.path.join(SQL_DIR, "brill_quest_poi.sql")
ADDON = os.path.join(DATA, "client", "addon", "BrillTown")

# The zones (WorldMapArea.dbc, 3.3.5a: its ID, the zone's AreaTable ID, and its bounds: left (y), right (y),
# top (x), bottom (x)); Undercity's only below the ruins' ground (the city is under Tirisfal's map).
ZONES = [
    # (WorldMapArea, zone, left, right, top, bottom, z below)
    (382, 1497, 873.19, -86.18, 1877.95, 1237.84, -20.0),
    (20, 85, 3033.33, -1485.42, 3837.5, 825.0, None),
    (21, 130, 3450.0, -750.0, 1666.67, -1133.33, None),
    (22, 28, 416.67, -3883.33, 3366.67, 500.0, None),
    (24, 267, 1066.67, -2133.33, 400.0, -1733.33, None),
    (15, 36, 783.33, -2016.67, 1500.0, -366.67, None),
]
TIRISFAL = 85
FIRST, LAST = 970100, 971699       # the module's numbers
BLOB = 6.0                         # yards around a single place, for its blob
# The house's credits, given by src/BrillHome.cpp rather than the town's tables: where each is earned
# (tools/build_sql.py's numbers: the bed, Corn, the footlocker, Carolai, the lily).
HOME_CREDITS = {
    970111: ("go", [970101]),        # Slept in your new bed: the bed
    970113: ("npc", [970112]),       # Played fetch: Corn
    970114: ("npc", [970112]),       # Scratched behind the ears: Corn
    970151: ("go", [970108]),        # Carolai's locket: the old footlocker at Solliden
    970150: ("npc", [970118]),       # Shared tea with Carolai: her visit to the house
    970152: ("go", [970109]),        # Moonpetal lily: by Brightwater Lake
    970153: ("npc", [2132]),         # Gave Carolai your answer: Carolai Anise, at her post (the game's)
}


def statements(sql, table):
    """The rows of every `INSERT INTO `table` (columns) VALUES ...;` in [sql], as dicts."""
    out = []
    for m in re.finditer(r"INSERT INTO `%s` \(([^)]*)\) VALUES\s*" % re.escape(table), sql):
        cols = [c.strip().strip("`") for c in m.group(1).split(",")]
        i, rows = m.end(), []
        while True:
            while sql[i] in " \n,":
                i += 1
            if sql[i] != "(":
                break
            i += 1
            vals = []
            while True:
                while sql[i] == " ":
                    i += 1
                if sql[i] == "'":
                    j, s = i + 1, []
                    while sql[j] != "'":
                        if sql[j] == "\\":
                            j += 1
                        s.append(sql[j])
                        j += 1
                    vals.append("".join(s))
                    i = j + 1
                else:
                    j = i
                    while sql[j] not in ",)":
                        j += 1
                    tok = sql[i:j].strip()
                    vals.append(None if tok == "NULL" else float(tok) if "." in tok else int(tok))
                    i = j
                if sql[i] == ",":
                    i += 1
                    continue
                i += 1          # ")"
                break
            rows.append(dict(zip(cols, vals)))
        out.extend(rows)
    return out


def zone_of(m, x, y, z):
    """(WorldMapArea, zone, map x %, map y %) of a place, or None."""
    if m != 0:
        return None
    for wma, zone, left, right, top, bottom, below in ZONES:
        if right <= y <= left and bottom <= x <= top and (below is None or z < below):
            return wma, zone, round((left - y) / (left - right) * 100, 2), round((top - x) / (top - bottom) * 100, 2)
    return None


def lua(v):
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(v, dict):
        return "{" + ", ".join(f"[{lua(k)}] = {lua(x)}" for k, x in v.items()) + "}"
    return "{" + ", ".join(lua(x) for x in v) + "}"


def main():
    sql = "\n".join(open(p, encoding="utf-8").read() for p in SOURCES)
    get = lambda t: statements(sql, t)
    quests = {r["ID"]: r for r in get("quest_template") if r.get("LogTitle") and not r["LogTitle"].startswith("[")}
    addon = {r["ID"]: r for r in get("quest_template_addon")}
    starts = {}
    for r in get("creature_queststarter"):
        starts.setdefault(r["quest"], []).append(r["id"])
    ends = {}
    for r in get("creature_questender"):
        ends.setdefault(r["quest"], []).append(r["id"])
    creatures = {r["entry"]: r for r in get("creature_template")}
    gos = {r["entry"]: r for r in get("gameobject_template")}
    cspawns, gspawns = {}, {}
    for r in get("creature"):
        cspawns.setdefault(r["id"], []).append((r["map"], r["position_x"], r["position_y"], r["position_z"], r["phaseMask"]))
    for r in get("gameobject"):
        gspawns.setdefault(r["id"], []).append((r["map"], r["position_x"], r["position_y"], r["position_z"], r["phaseMask"]))
    # what gives each credit: the objects used for it, the creatures whose option gives it
    credit_gos, credit_npcs = {}, {}
    for r in get("brill_town_use"):
        if r["credit"]:
            credit_gos.setdefault(r["credit"], set()).add(r["go"])
    for r in get("brill_town_gossip"):
        if r["credit"]:
            credit_npcs.setdefault(r["credit"], set()).add(r["npc"])
    # quests that wait on more than the one before them (conditions 19), and where they're given
    gated = {r for r in quests if re.search(r"\(19, 0, %d, " % r, sql)}
    have_poi = {r["QuestID"] for r in get("quest_poi")}

    # Questie: the creatures (the module's own: givers, takers, those to kill or talk to; and the
    # credits: their names are the objectives' words, their places those of what gives them).
    npc_data, quest_data, borrowed = {}, {}, {}

    def places(spawns):
        out = {}
        for m, x, y, z, _ph in spawns:
            p = zone_of(m, x, y, z)
            if p:
                out.setdefault(p[1], []).append([p[2], p[3]])
        return out

    def own_npc(entry):
        if entry in npc_data or entry not in creatures:
            return
        c = creatures[entry]
        sp = places(cspawns.get(entry, []))
        npc_data[entry] = {1: c["name"], 4: c["minlevel"], 5: c["maxlevel"], 6: c.get("rank", 0) or 0, 7: sp,
                           9: next(iter(sp), TIRISFAL), 10: [], 11: [], 13: "AH" if c["faction"] not in (14,) else None,
                           14: c.get("subname")}

    poi, poi_points, poi_npc = [], [], []

    def blob(qid, idx, n, pts):
        """A blob (quest_poi n) of objective idx around world points (map, x, y, z) in one zone."""
        byzone = {}
        for m, x, y, z in pts:
            p = zone_of(m, x, y, z)
            if p:
                byzone.setdefault(p[0], []).append((x, y))
        for wma, xy in byzone.items():
            xs, ys = [a for a, _ in xy], [b for _, b in xy]
            x0, x1, y0, y1 = min(xs) - BLOB, max(xs) + BLOB, min(ys) - BLOB, max(ys) + BLOB
            poi.append(f"({qid}, {n}, {idx}, 0, {wma}, 0, 0, 1, 0)")
            for k, (px, py) in enumerate(((x0, y0), (x0, y1), (x1, y1), (x1, y0))):
                poi_points.append(f"({qid}, {n}, {k}, {round(px)}, {round(py)}, 0)")
            n += 1
        return n

    for qid, qt in sorted(quests.items()):
        ad = addon.get(qid, {})
        giver, ender = starts.get(qid, []), ends.get(qid, [])
        for e in giver + ender:
            own_npc(e)
        objectives, labels = [], []
        n = 0
        for k in range(1, 5):
            target, count, label = qt.get(f"RequiredNpcOrGo{k}"), qt.get(f"RequiredNpcOrGoCount{k}"), qt.get(f"ObjectiveText{k}")
            if not target:
                continue
            idx = k - 1
            pts, from_npcs = [], []
            c = creatures.get(target)
            is_credit = c is not None and (c.get("unit_flags") == 33554432 and c.get("faction") == 35)
            if is_credit:
                kind, things = HOME_CREDITS.get(target, ("", []))
                for t in things:
                    if kind == "npc" and t < FIRST:
                        from_npcs.append(t)
                    else:
                        pts += [s[:4] for s in (gspawns if kind == "go" else cspawns).get(t, [])]
                for g in sorted(credit_gos.get(target, ())):
                    pts += [s[:4] for s in gspawns.get(g, [])]
                for npc in sorted(credit_npcs.get(target, ())):
                    if npc in cspawns:
                        pts += [s[:4] for s in cspawns[npc]]
                    elif npc < FIRST:
                        from_npcs.append(npc)
                sp = places([(m, x, y, z, 1) for m, x, y, z in pts])
                npc_data[target] = {1: label or c["name"], 4: 1, 5: 1, 6: 0, 7: sp, 9: next(iter(sp), TIRISFAL), 13: "AH"}
                if from_npcs:
                    borrowed[target] = from_npcs
            elif target in creatures:
                own_npc(target)
                pts += [s[:4] for s in cspawns.get(target, [])]
            elif target < 0:
                continue        # (a game object as the objective: none of the module's)
            else:
                from_npcs.append(target)        # (one of the game's own creatures to kill: Questie has it)
            objectives.append([target, label if is_credit or not label else label])
            if qid not in have_poi:
                n = blob(qid, idx, n, pts)
                for npc in from_npcs:
                    poi_npc.append((qid, n, idx, npc))
                    n += 1
        # the turn-in
        if qid not in have_poi:
            for e in ender:
                if e in cspawns:
                    n = blob(qid, -1, n, [s[:4] for s in cspawns[e]])
                else:
                    poi_npc.append((qid, n, -1, e))
                    n += 1
        repeat = (ad.get("SpecialFlags") or 0) & 1
        offered = (giver and qid not in gated and all(
            g < FIRST or all(s[4] == 1 for s in cspawns.get(g, [])) for g in giver))
        quest_data[qid] = {
            1: qt["LogTitle"], 2: [giver] if offered else [], 3: [ender], 4: qt.get("MinLevel") or 1,
            6: 0, 7: 0, 8: [qt.get("LogDescription") or ""],
            10: [objectives] if objectives else None,
            13: [ad["PrevQuestID"]] if ad.get("PrevQuestID") else None,
            17: TIRISFAL, 23: qt.get("Flags") or 0, 24: 1 if repeat else 0,
        }
        for e in giver:
            if offered and e in npc_data:
                npc_data[e][10].append(qid)
        for e in ender:
            if e in npc_data:
                npc_data[e][11].append(qid)
    # the game's own givers and takers: the module's quests added to theirs as Questie starts
    stock_starts, stock_ends = {}, {}
    for qid, d in quest_data.items():
        for e in (d[2] or [[]])[0] if d[2] else []:
            if e < FIRST:
                stock_starts.setdefault(e, []).append(qid)
        for e in d[3][0]:
            if e < FIRST:
                stock_ends.setdefault(e, []).append(qid)

    # the game's quest markers
    out = ["-- The Brill home's and town's quests on the game's maps (quest_poi): made by tools/build_questie.py from",
           "-- brill_home_world.sql and brill_town_world.sql; don't edit by hand. Written to be applied again.",
           f"DELETE FROM `quest_poi` WHERE `QuestID` BETWEEN {FIRST} AND {LAST}" + (
               f" AND `QuestID` NOT IN ({', '.join(map(str, sorted(have_poi)))})" if have_poi else "") + ";",
           f"DELETE FROM `quest_poi_points` WHERE `QuestID` BETWEEN {FIRST} AND {LAST}" + (
               f" AND `QuestID` NOT IN ({', '.join(map(str, sorted(have_poi)))})" if have_poi else "") + ";"]
    if poi:
        out.append("INSERT INTO `quest_poi` (`QuestID`, `id`, `ObjectiveIndex`, `MapID`, `WorldMapAreaId`, `Floor`, `Priority`, `Flags`, `VerifiedBuild`) VALUES")
        out.append(",\n".join(poi) + ";")
        out.append("INSERT INTO `quest_poi_points` (`QuestID`, `Idx1`, `Idx2`, `X`, `Y`, `VerifiedBuild`) VALUES")
        out.append(",\n".join(poi_points) + ";")
    if poi_npc:
        out.append("-- The game's own creatures: where the world database has them (Tirisfal's map: 20; the Undercity's: 382).")
        for qid, n, idx, npc in poi_npc:
            out.append(f"INSERT INTO `quest_poi` (`QuestID`, `id`, `ObjectiveIndex`, `MapID`, `WorldMapAreaId`, `Floor`, `Priority`, `Flags`, `VerifiedBuild`) "
                       f"SELECT {qid}, {n}, {idx}, 0, IF(`position_z` < -20 AND `position_x` BETWEEN 1237 AND 1878 AND `position_y` BETWEEN -87 AND 874, 382, 20), "
                       f"0, 0, 1, 0 FROM `creature` WHERE `id` = {npc} AND `map` = 0 ORDER BY `guid` LIMIT 1;")
            for k, (dx, dy) in enumerate(((-BLOB, -BLOB), (-BLOB, BLOB), (BLOB, BLOB), (BLOB, -BLOB))):
                out.append(f"INSERT INTO `quest_poi_points` (`QuestID`, `Idx1`, `Idx2`, `X`, `Y`, `VerifiedBuild`) "
                           f"SELECT {qid}, {n}, {k}, ROUND(`position_x` + {dx}), ROUND(`position_y` + {dy}), 0 FROM `creature` "
                           f"WHERE `id` = {npc} AND `map` = 0 ORDER BY `guid` LIMIT 1;")
    with open(POI_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    # Questie's add-on
    os.makedirs(ADDON, exist_ok=True)
    with open(os.path.join(ADDON, "BrillTown.toc"), "w", encoding="utf-8") as f:
        f.write("## Interface: 30300\n## Title: Brill Town (for Questie)\n"
                "## Notes: The Brill home's and town's quests for Questie (mod-brill-home); made by the realm\n"
                "## OptionalDeps: Questie-335, Questie\nBrillTown.lua\n")
    lines = [
        "-- SPDX-License-Identifier: GPL-3.0-or-later",
        "-- The Brill home's and town's quests for Questie's 3.3.5 port (mod-brill-home). Made by tools/build_questie.py",
        "-- from the module's world SQL; don't edit by hand. Questie doesn't know the module's quests and creatures:",
        "-- as its database starts (QuestieDB:Initialize, at login) this adds them to the database's own runtime",
        "-- additions and the quests' numbers to the list Questie checks a quest log against. Nothing else of",
        "-- Questie's is changed; without Questie this does nothing.",
        "",
        "local QUESTS = " + lua(quest_data),
        "local NPCS = " + lua(npc_data),
        "-- the game's own creatures whose words give a credit: their places, from Questie, are the credit's",
        "local BORROWED = " + lua(borrowed),
        "-- the game's own givers and takers: the module's quests added to theirs",
        "local STARTS = " + lua(stock_starts),
        "local ENDS = " + lua(stock_ends),
        "",
        LUA_BODY,
    ]
    with open(os.path.join(ADDON, "BrillTown.lua"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{POI_OUT}: {len(poi) + len(poi_npc)} markers for {len(quest_data) - len(have_poi & set(quest_data))} quests; "
          f"{ADDON}: {len(quest_data)} quests, {len(npc_data)} creatures")


LUA_BODY = r"""
local function apply(QuestieDB)
	local level = UnitLevel("player") or 1
	local quests, npcs = QuestieDB.questDataOverrides, QuestieDB.npcDataOverrides
	for id, q in pairs(QUESTS) do
		q[5] = level            -- (the module's quests are the player's level, -1 in the game)
		quests[id] = q
	end
	for id, n in pairs(NPCS) do
		npcs[id] = n
	end
	for id, from in pairs(BORROWED) do
		local spawns = npcs[id][7] or {}
		for _, npc in ipairs(from) do
			local theirs = QuestieDB.QueryNPCSingle and QuestieDB.QueryNPCSingle(npc, "spawns")
			if type(theirs) == "table" then
				for zone, points in pairs(theirs) do
					spawns[zone] = spawns[zone] or {}
					for _, p in ipairs(points) do
						table.insert(spawns[zone], p)
					end
				end
			end
		end
		npcs[id][7] = spawns
		for zone in pairs(spawns) do npcs[id][9] = zone; break end
	end
	local function merge(list, index, key)
		for npc, add in pairs(list) do
			local have = QuestieDB.QueryNPCSingle and QuestieDB.QueryNPCSingle(npc, key)
			local all = {}
			if type(have) == "table" then
				for _, q in ipairs(have) do table.insert(all, q) end
			end
			for _, q in ipairs(add) do table.insert(all, q) end
			npcs[npc] = npcs[npc] or {}
			npcs[npc][index] = all
		end
	end
	merge(STARTS, 10, "questStarts")
	merge(ENDS, 11, "questEnds")
	-- (the list Questie checks a quest log against: a copy with these, the database's own left as it is)
	local pointers = {}
	for id, p in pairs(QuestieDB.QuestPointers or {}) do pointers[id] = p end
	for id in pairs(QUESTS) do pointers[id] = pointers[id] or true end
	QuestieDB.QuestPointers = pointers
end

if type(QuestieLoader) == "table" and QuestieLoader.ImportModule then
	local QuestieDB = QuestieLoader:ImportModule("QuestieDB")
	if type(QuestieDB) == "table" and type(QuestieDB.Initialize) == "function" then
		local initialize = QuestieDB.Initialize
		QuestieDB.Initialize = function(...)
			local result = initialize(...)
			local ok, problem = pcall(apply, QuestieDB)
			if not ok and DEFAULT_CHAT_FRAME then
				DEFAULT_CHAT_FRAME:AddMessage("Brill Town: Questie's database didn't take the town's quests: " .. tostring(problem))
			end
			return result
		end
	end
end
"""

if __name__ == "__main__":
    main()
