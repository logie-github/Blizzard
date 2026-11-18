"""Stage `world`: one map's creatures, objects, quests, vendors, gossip and paths, from TrinityCore's 4.3.4 world (the CPP TDB, loaded
into a MariaDB database `cpp_world`) into AzerothCore's tables (`ac_world`'s schema), as SQL.

Table-driven (data/world_plan.json): for each step the columns both schemas have are copied by name, `set` gives expressions
(the zones' id ranges ENTRY/GUID/PATH made data), a CPP-only column is dropped and counted, an AzerothCore-only one keeps its
default. Schemas are read from the two SQL dumps (parse_schema), so the stage's SQL and its report (dropped columns, steps with a
table one side lacks) come out without a database; running the SQL needs `mariadb` (Actions: apt install, or a service container).
Rows are always new, in ranges of their own (never a 3.3.5a row changed), removable by range (`world_off.sql`).
What is not built is in the plan's `not_built` and goes into the report, never silently.
"""
import json
import os
import re
import subprocess

from . import util

ENTRY = 6_000_000
GUID = 10_000_000
PATH = 600_000_000
GUID_LIMIT = 0xFFFFFF          # AzerothCore stops the server when a spawn id would pass it
PLAN = os.path.join(util.HERE, "data", "world_plan.json")


def parse_schema(sql_text):
    """{table: [column, ...]} from the CREATE TABLE statements of an SQL dump (MariaDB/MySQL dialect)."""
    out = {}
    for m in re.finditer(r"CREATE TABLE (?:IF NOT EXISTS )?`([^`]+)`\s*\((.*?)\)\s*ENGINE", sql_text, re.S | re.I):
        cols = []
        for line in m.group(2).split("\n"):
            c = re.match(r"\s*`([^`]+)`\s+\w", line)
            if c:
                cols.append(c.group(1))
        out[m.group(1)] = cols
    return out


def guid_bases(counts, stride=1000):
    """({map id: base}, {map id: span}): each map's spawn block, in map-id order, rounded up to `stride`, from GUID. `counts`
    {map id: most spawns of one table (creature or gameobject)}. Raises when the blocks would pass AzerothCore's limit."""
    base, bases, spans = GUID, {}, {}
    for mid in sorted(counts):
        span = -(-max(1, counts[mid]) // stride) * stride
        bases[mid], spans[mid] = base - GUID, span
        base += span
    if base > GUID_LIMIT:
        raise ValueError(f"spawn ids would pass {GUID_LIMIT}: {base}")
    return bases, spans


def render(expr, ctx):
    return (expr.replace("{CPP}", ctx["cpp"]).replace("{AC}", ctx["ac"]).replace("{TMP}", "cb_tmp").replace("{map}", str(ctx["map"]))
            .replace("{new_map}", str(ctx["new_map"])).replace("{E}", str(ENTRY)).replace("{G}", str(GUID + ctx["guid_base"]))
            .replace("{P}", str(PATH)))


def step_sql(step, cpp_cols, ac_cols, ctx):
    """(sql, report) for one step; sql is None when a side lacks the table."""
    t = step["table"]
    rep = {"table": t, "dropped": [], "defaulted": [], "missing_table": None}
    if t not in cpp_cols:
        rep["missing_table"] = "cpp"
        return None, rep
    if t not in ac_cols:
        rep["missing_table"] = "ac"
        return None, rep
    sets = step.get("set", {})
    dest, expr = [], []
    for col in ac_cols[t]:
        if col in sets:
            dest.append(col)
            expr.append(render(sets[col], ctx))
        elif col in cpp_cols[t]:
            dest.append(col)
            expr.append(f"`{col}`")
        else:
            rep["defaulted"].append(col)
    rep["dropped"] = [c for c in cpp_cols[t] if c not in ac_cols[t]]
    cols = ", ".join(f"`{c}`" for c in dest)
    sql = (f"INSERT IGNORE INTO {ctx['ac']}.`{t}` ({cols})\nSELECT {', '.join(expr)}\nFROM {ctx['cpp']}.`{t}`\n"
           f"WHERE {render(step['where'], ctx)};\n")
    return sql, rep


def generate(map_entry, cpp_cols, ac_cols, guid_base, guid_span, plan=None, cpp_db="cpp_world", ac_db="ac_world"):
    """(world.sql text, world_off.sql text, report dict) for one manifest map entry. The map's spawns are ids
    GUID + guid_base up to guid_span after (`guid_bases`)."""
    plan = plan or json.load(open(PLAN))
    ctx = {"cpp": cpp_db, "ac": ac_db, "map": map_entry["id"], "new_map": map_entry["new_id"], "guid_base": guid_base}
    out = [f"-- {map_entry.get('name') or map_entry['dir']} (CPP map {map_entry['id']} as {map_entry['new_id']}): catabackport world.py. "
           f"Ids: entries +{ENTRY}, spawns +{GUID + guid_base}, paths +{PATH}.\n",
           "CREATE DATABASE IF NOT EXISTS cb_tmp;\n"]
    for s in plan["scratch"]:
        out.append(f"DROP TABLE IF EXISTS cb_tmp.`{s['name']}`;\nCREATE TABLE cb_tmp.`{s['name']}` AS {render(s['sql'], ctx)};\n")
    reports, skipped = [], []
    for step in plan["steps"]:
        sql, rep = step_sql(step, cpp_cols, ac_cols, ctx)
        reports.append(rep)
        if sql is None:
            skipped.append(f"{step['table']}: the {rep['missing_table']} schema has no such table")
            continue
        out.append(sql)
    for s in plan["scratch"]:
        out.append(f"DROP TABLE IF EXISTS cb_tmp.`{s['name']}`;\n")
    lo = GUID + guid_base
    off = [f"-- {map_entry['dir']}: its spawns out again (templates and quests are shared with other maps and stay).\n"]
    for t in ("creature_addon", "creature", "gameobject_addon", "gameobject"):
        off.append(f"DELETE FROM `{t}` WHERE `guid` >= {lo} AND `guid` < {lo + guid_span};\n")
    return "".join(out), "".join(off), {"steps": reports, "skipped": skipped, "not_built": plan.get("not_built", [])}


def mariadb(db, sql_path, force=True):
    argv = ["mariadb"] + (["--force"] if force else []) + [db]
    with open(sql_path, "rb") as f:
        return subprocess.run(argv, stdin=f, capture_output=True, text=True)


def counts(cpp_db="cpp_world"):
    """{map id: most rows of creature or gameobject} from the CPP database (needs mariadb)."""
    out = {}
    for t in ("creature", "gameobject"):
        p = subprocess.run(["mariadb", "-B", "-N", cpp_db, "-e", f"SELECT `map`, COUNT(*) FROM `{t}` GROUP BY `map`"],
                           check=True, capture_output=True, text=True)
        for line in p.stdout.splitlines():
            m, n = line.split("\t")
            out[int(m)] = max(out.get(int(m), 0), int(n))
    return out
