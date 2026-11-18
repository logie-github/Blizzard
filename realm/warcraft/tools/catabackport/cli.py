"""The command line: one command per stage (CATA_BACKPORT.md 6).

  python3 -m catabackport inventory --work W [--source wago|dir:F] [--listfile LF]
  python3 -m catabackport plan      --work W [--maps all|proof|ID,DIR,group:dungeon] [--shards N] [--done INDEX] [--matrix OUT]
  python3 -m catabackport run       --work W --release R --shard i/n [--stages fetch,convert,tables,extract,world,validate,pack] [--only MAP]
  python3 -m catabackport fetch|convert|tables|extract|world|validate|pack   (the same as `run --stages <that>`)
  python3 -m catabackport assemble  --release R

Exit codes: 0 done (units may be partial or deferred, all in the report), 2 usage, 3 every unit failed, 75 the source was down and
nothing could be done (nothing is wrong with the tool: run it again).
"""
import argparse
import json
import os
import sys
import time

from . import (convert as conv_stage, extract as extract_stage, fetch as fetch_stage, inventory, listfile as lf, pack as pack_stage,
               plan as plan_stage, source as src, tables as tables_stage, util, validate as validate_stage, world as world_stage)

STAGES = ["fetch", "convert", "tables", "extract", "world", "validate", "pack"]
EX_DEFERRED = 75


def add_common(p):
    p.add_argument("--work", required=True, help="the work folder (manifest.json, <unit>/ folders)")
    p.add_argument("--pins", help="pins.json (default: the tool's own)")
    p.add_argument("--source", default="wago", help="wago | dir:PATH | url:BASE, comma separated, in order")
    p.add_argument("--cache", help="a cache folder for files by id and tables (default: <work>/cache)")
    p.add_argument("--listfile", help="the community listfile csv")
    p.add_argument("--stage-budget", type=int, default=5400, help="seconds of waiting on a source before a stage is deferred")


def make_source(a, pins):
    cache = a.cache or os.path.join(a.work, "cache")
    return src.from_spec(a.source, pins["build"], cache=cache, budget_seconds=a.stage_budget)


def parser():
    ap = argparse.ArgumentParser(prog="catabackport", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory")
    add_common(p)
    p = sub.add_parser("plan")
    p.add_argument("--work", required=True)
    p.add_argument("--maps", default="all")
    p.add_argument("--shards", type=int)
    p.add_argument("--budget-tiles", type=int, default=600)
    p.add_argument("--max-tiles", type=int, default=plan_stage.MAX_TILES_PER_UNIT)
    p.add_argument("--done", help="a previous release's index.json: units with the same input hash are skipped")
    p.add_argument("--matrix", help="write the workflow's matrix json here")
    for name in ["run"] + STAGES:
        p = sub.add_parser(name)
        add_common(p)
        p.add_argument("--release", help="where packs go (default: <work>/release)")
        p.add_argument("--shard", default="all", help="i/n (the plan's shard i of n) or all")
        p.add_argument("--only", help="a unit, map id or directory: only that")
        p.add_argument("--stages", default=",".join(STAGES) if name == "run" else name)
        p.add_argument("--no-resume", action="store_true", help="redo stages whose state says done")
        p.add_argument("--dry-run", action="store_true", help="say what would be done, touch nothing")
        p.add_argument("--jobs", type=int, default=8)
        p.add_argument("--converter", help="the Converter's command (default: python3 -m wotlkconv)")
        p.add_argument("--converter-src", help="the Converter's src folder (pinned commit checked out)")
        p.add_argument("--dbd", help="WoWDBDefs' definitions folder")
        p.add_argument("--stock-dbc", help="the server's dbc folder (3.3.5a's tables)")
        p.add_argument("--tools", help="AzerothCore's extractors folder (map_extractor ... zones_mkmpq, mmaps-config.yaml)")
        p.add_argument("--cpp-schema", help="CPP's world SQL dump (for the world stage's column lists)")
        p.add_argument("--ac-schema", help="AzerothCore's base db_world SQL (idem)")
        p.add_argument("--run-sql", action="store_true", help="the world stage also runs its SQL with mariadb (cpp_world, ac_world) and dumps the rows")
        p.add_argument("--world-dir", help="a folder of <unit>/world.sql made by a job that has the database: the world stage takes them")
    p = sub.add_parser("assemble")
    p.add_argument("--release", required=True)
    p.add_argument("--pins")
    p = sub.add_parser("world-index", help="CPP's spawn counts per map -> the spawn id blocks (needs mariadb with cpp_world)")
    p.add_argument("--work", required=True)
    p.add_argument("--counts", help="a json {map id: count} instead of asking the database")
    return ap


def cmd_world_index(a):
    manifest = util.load_json(os.path.join(a.work, "manifest.json"))
    counts = {int(k): v for k, v in json.load(open(a.counts)).items()} if a.counts else world_stage.counts()
    ids_ = sorted(m["id"] for m in manifest["maps"])
    bases, spans = world_stage.guid_bases({i: counts.get(i, 0) for i in ids_})
    util.dump_json(os.path.join(a.work, "world-index.json"),
                   {"bases": {str(k): v for k, v in bases.items()}, "spans": {str(k): v for k, v in spans.items()}})
    log(f"world-index: {len(ids_)} maps, spawn ids up to {world_stage.GUID + sum(spans.values())}")
    return 0


def log(msg):
    print(msg, flush=True)


def cmd_inventory(a):
    pins = util.pins(a.pins)
    source = make_source(a, pins)
    try:
        m = inventory.run(source, pins, a.work, a.listfile)
    except src.SourceDown as e:
        log(f"inventory: the source is down ({e}); nothing written. Run again later.")
        return EX_DEFERRED
    except src.Missing as e:
        log(f"inventory: the build lacks {e}")
        return 3
    log(f"inventory: {len(m['maps'])} maps, proof map {m['proof']}; see {a.work}/inventory-report.txt")
    return 0


def cmd_plan(a):
    manifest = util.load_json(os.path.join(a.work, "manifest.json"))
    if not manifest:
        log("plan: no manifest.json: run inventory first")
        return 2
    done = None
    if a.done and os.path.exists(a.done):
        idx = util.load_json(a.done, {})
        done = {p["unit"]: p["input_hash"] for p in idx.get("packs", []) if p.get("status") == "ok"}
    plan = plan_stage.make(manifest, a.maps, a.shards, a.budget_tiles, done, a.max_tiles)
    util.dump_json(os.path.join(a.work, "plan.json"), plan)
    mx = plan_stage.matrix(plan)
    util.dump_json(a.matrix or os.path.join(a.work, "matrix.json"), mx)
    log(f"plan: {len(plan['units'])} units in {len(mx['include'])} shards, {len(plan['skipped'])} skipped (done or not possible)")
    return 0


class Ctx:
    pass


def stage_done(state, name, unit):
    s = state.get("stages", {}).get(name)
    return bool(s and s.get("status") == "done" and s.get("input_hash") == unit["input_hash"])


def run_unit(c, unit, stages):
    """Runs the stages for one unit; a failure or a down source ends the unit, never the run. Returns the unit's result."""
    m = c.by_id[unit["map"]]
    base_dir = os.path.join(c.work, unit["unit"])
    sp = os.path.join(base_dir, "state.json")
    state = util.load_json(sp, {})
    state.setdefault("stages", {})
    result = {"unit": unit["unit"], "status": "ok", "problems": [], "stages": {}}

    def mark(name, status, t0, **kw):
        state["stages"][name] = {"status": status, "input_hash": unit["input_hash"], "seconds": round(time.time() - t0, 1), **kw}
        result["stages"][name] = state["stages"][name]
        util.dump_json(sp, state)

    for name in stages:
        t0 = time.time()
        if c.resume and name not in ("pack",) and stage_done(state, name, unit):
            log(f"{unit['unit']}: {name} already done")
            result["stages"][name] = state["stages"][name]
            continue
        if c.dry_run:
            log(f"{unit['unit']}: would run {name}")
            continue
        try:
            if name == "fetch":
                r = fetch_stage.run(c.source, m, unit, c.by_id_fd, c.by_path, c.work, c.jobs, log)
                mark(name, "done", t0, files=r["files"], bytes=r["bytes"], missing=len(r["missing"]))
                if r["missing"]:
                    result["problems"].append(f"{len(r['missing'])} files are not in the build (first: {r['missing'][0]})")
            elif name == "convert":
                base_map = c.by_id.get(m.get("swap_of")) if unit.get("base") else None
                areas = {int(k): v for k, v in c.manifest.get("id_plan", {}).get("areas", {}).items() if int(k) != v}
                r = conv_stage.run(m, unit, c.work, c.listfile, c.conv_cmd, c.conv_env, c.liquids, c.jobs, unit.get("base"), base_map,
                                   log, areas)
                mark(name, "done", t0, tiles=r["tiles"], accounting=r["accounting"])
                result["problems"] += r["problems"]
                if r["status"] == "failed":
                    result["status"] = "failed"
            elif name == "tables" and not c.dbd:
                mark(name, "skipped", t0, why="no --dbd")
                result["problems"].append("table rows not made: no WoWDBDefs folder given (--dbd)")
            elif name == "tables":
                rep = tables_stage.run(c.source, [m], c.manifest.get("id_plan", {}), c.dbd, os.path.join(base_dir, "out"))
                mark(name, "done", t0, lacking=len(rep["Map"]["lacking"]) + len(rep["AreaTable"]["lacking"]))
            elif name == "extract":
                if not extract_stage.have_tools(c.tools):
                    mark(name, "skipped", t0, why="no AzerothCore tools (--tools)")
                    result["problems"].append("server maps/vmaps/mmaps not made: no extractor tools given")
                else:
                    counts = extract_stage.run([m], base_dir, c.tools, c.stock_dbc, log)
                    mark(name, "done", t0, counts=counts)
            elif name == "world":
                world_unit(c, m, unit, base_dir, result, mark, t0)
            elif name == "validate":
                rep = validate_stage.run(os.path.join(base_dir, "out", "client", "files"))
                mark(name, "done", t0, result=rep["status"], checked=rep["checked"], dropped=rep["dropped"],
                     unresolved=rep["unresolved"]["count"])
                result["problems"] += [f"{p}: {w}" for p, w in rep["bad"][:10]]
                if rep["unresolved"]["count"]:
                    result["problems"].append(f"{rep['unresolved']['count']} files named by tiles are not in the pack, e.g. "
                                              + ", ".join(rep["unresolved"]["sample"][:3]))
                if rep["status"] == "failed":
                    result["status"] = "failed"
                elif rep["status"] == "partial" and result["status"] == "ok":
                    result["status"] = "partial"
            elif name == "pack":
                if result["status"] == "failed":
                    log(f"{unit['unit']}: failed, not packed")
                    continue
                status = result["status"] if result["status"] != "ok" or not result["problems"] else "partial"
                entry = pack_stage.run(base_dir, c.release, unit, m, status, {"problems": result["problems"]}, c.pins,
                                       [unit["base"]] if unit.get("base") else [])
                mark(name, "done", t0, size=entry["size"])
                result["status"] = status
        except src.SourceDown as e:
            log(f"{unit['unit']}: {name} deferred, the source is down: {e}")
            mark(name, "deferred", t0, why=str(e))
            result["status"] = "deferred"
            result["problems"].append(f"{name} deferred: {e}")
            break
        except Exception as e:      # (one unit's fault never stops the others: it is the report's line)
            log(f"{unit['unit']}: {name} FAILED: {type(e).__name__}: {e}")
            mark(name, "failed", t0, why=f"{type(e).__name__}: {e}")
            result["status"] = "failed"
            result["problems"].append(f"{name} failed: {type(e).__name__}: {e}")
            break
    return result


def world_unit(c, m, unit, base_dir, result, mark, t0):
    pre = os.path.join(c.world_dir, unit["unit"]) if c.world_dir else None
    if pre and os.path.exists(os.path.join(pre, "world.sql")):            # (made by the world job, which has the database)
        for n in ("world.sql", "world_off.sql"):
            if os.path.exists(os.path.join(pre, n)):
                util.write_atomic(os.path.join(base_dir, "out", n), open(os.path.join(pre, n), "rb").read())
        mark("world", "done", t0, from_world_job=True)
        return
    if not (c.cpp_schema and c.ac_schema):
        mark("world", "skipped", t0, why="no --cpp-schema/--ac-schema")
        result["problems"].append("world data not made: no schemas given (the world stage needs CPP's and AzerothCore's SQL)")
        return
    cpp_cols = world_stage.parse_schema(open(c.cpp_schema, encoding="utf-8", errors="replace").read())
    ac_cols = world_stage.parse_schema(open(c.ac_schema, encoding="utf-8", errors="replace").read())
    wi = util.load_json(os.path.join(c.work, "world-index.json"))
    base, span = (wi["bases"].get(str(m["id"]), 0), wi["spans"].get(str(m["id"]), 1000)) if wi else (0, 1000)
    sql, off, rep = world_stage.generate(m, cpp_cols, ac_cols, base, span)
    out = os.path.join(base_dir, "out")
    util.write_atomic(os.path.join(base_dir, "world_transform.sql"), sql)
    util.write_atomic(os.path.join(out, "world_off.sql"), off)
    util.dump_json(os.path.join(base_dir, "world-report.json"), rep)
    rows = None
    if c.run_sql:
        tables = [s["table"] for s in rep["steps"] if not s["missing_table"]]
        errors, rows = world_stage.apply_and_dump(os.path.join(base_dir, "world_transform.sql"), os.path.join(out, "world.sql"), tables)
        util.write_atomic(os.path.join(base_dir, "world-sql-errors.txt"), errors)
        if errors.strip():
            result["problems"].append(f"world: {len(errors.splitlines())} lines of SQL errors (world-sql-errors.txt)")
        if not rows:
            result["problems"].append("world: no rows were made")
    else:
        result["problems"].append("world: the SQL was written but not run (no --run-sql: no database)")
    mark("world", "done", t0, skipped=len(rep["skipped"]), rows=rows, dropped_columns=sum(len(s["dropped"]) for s in rep["steps"]))
    if rep["skipped"]:
        result["problems"].append("world: " + "; ".join(rep["skipped"][:5]))
    result["problems"].append("world: not built: " + ", ".join(rep["not_built"]))


def cmd_run(a):
    pins = util.pins(a.pins)
    c = Ctx()
    c.work, c.pins, c.jobs, c.resume, c.dry_run = a.work, pins, a.jobs, not a.no_resume, a.dry_run
    c.release = a.release or os.path.join(a.work, "release")
    c.manifest = util.load_json(os.path.join(a.work, "manifest.json"))
    plan = util.load_json(os.path.join(a.work, "plan.json"))
    if not c.manifest or not plan:
        log("run: manifest.json and plan.json are needed (inventory, plan)")
        return 2
    c.by_id = {m["id"]: m for m in c.manifest["maps"]}
    units = plan_stage.for_shard(plan, a.shard)
    if a.only:
        units = [u for u in units if a.only in (u["unit"], str(u["map"]), c.by_id[u["map"]]["dir"].lower())]
    stages = [s for s in a.stages.split(",") if s]
    for s in stages:
        if s not in STAGES:
            log(f"run: unknown stage {s}")
            return 2
    c.listfile, c.dbd, c.stock_dbc, c.tools = a.listfile, a.dbd, a.stock_dbc, a.tools
    c.cpp_schema, c.ac_schema, c.run_sql, c.world_dir = a.cpp_schema, a.ac_schema, a.run_sql, a.world_dir
    c.conv_cmd, c.conv_env = conv_stage.converter_command(a.converter_src, a.converter)
    c.source = make_source(a, pins)
    c.by_id_fd, c.by_path = ({}, {})
    if any(s in stages for s in ("fetch",)) and not a.dry_run:
        if not a.listfile:
            log("run: fetch needs --listfile")
            return 2
        c.by_id_fd, c.by_path = lf.load(a.listfile)
    c.liquids = {}
    if "convert" in stages and not a.dry_run:
        try:
            from .inventory import rows
            kinds = {0: 1, 1: 2, 2: 3, 3: 4}
            c.liquids = {int(r["ID"]): kinds.get(int(r["SoundBank"]), 1) for r in rows(c.source.table("LiquidType"))}
        except (src.Missing, src.SourceDown, KeyError, ValueError) as e:
            log(f"run: no LiquidType table ({e}); unknown liquid kinds will be water")
    os.makedirs(c.release, exist_ok=True)
    results = []
    for unit in units:
        log(f"== {unit['unit']} (map {unit['map']}, weight {unit['weight']})")
        results.append(run_unit(c, unit, stages))
    status = {"results": results, "shard": a.shard, "stages": stages}
    util.dump_json(os.path.join(a.work, f"status-{a.shard.replace('/', 'of')}.json"), status)
    worst = [r["status"] for r in results]
    for r in results:
        log(f"{r['status']:9} {r['unit']}" + (f" ({len(r['problems'])} notes)" if r["problems"] else ""))
    if results and all(s == "failed" for s in worst):
        return 3
    if results and all(s == "deferred" for s in worst):
        return EX_DEFERRED
    return 0


def cmd_assemble(a):
    pins = util.pins(a.pins)
    idx = pack_stage.assemble(a.release, pins)
    log(f"assemble: {len(idx['packs'])} installable packs, {len(idx['not_installable'])} not")
    return 0


def main(argv=None):
    a = parser().parse_args(argv)
    if a.cmd == "inventory":
        return cmd_inventory(a)
    if a.cmd == "plan":
        return cmd_plan(a)
    if a.cmd == "assemble":
        return cmd_assemble(a)
    if a.cmd == "world-index":
        return cmd_world_index(a)
    return cmd_run(a)
