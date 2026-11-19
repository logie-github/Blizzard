#!/usr/bin/env python3
"""The launcher's converter, one expansion at a time (the user, 19 November 2026: "Under launcher game options have a converter. It will
take from Legion and it will import the data from Cataclysm on in terms of maps, quests ... for now just make it in 3.3.5 format. Take it
by expansion."). A thin driver over the catabackport tool (realm/warcraft/tools/catabackport: inventory, plan, fetch, convert, tables,
validate, pack): it picks the maps of one expansion from the Map table's ExpansionID, runs the stages unit by unit and keeps
`<root>/<expansion>/progress.json` for the launcher to read (state, stage, unit, done/total, a line of text), so a screen can show progress
and a rerun carries on (the tool resumes what is done).

    python3 convert.py run EXPANSION --root DIR [--stages S,S] [--tool DIR] [--python CMD] [--source wago] [--listfile CSV] [--jobs N]
    python3 convert.py list                      the expansions
    python3 convert.py status EXPANSION --root DIR

Output: <root>/<expansion>/release/ (the tool's packs: `cata-<map>.tar.xz` with the 3.3.5a layout, `index.json`) and `work/` (its work folder).
Exit status: 0 done, 2 usage, 3 every unit failed, 75 the source was down (run again).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STAGES = ["fetch", "convert", "tables", "validate", "pack"]      # no native tools and no database: they run on a phone
EX_DEFERRED = 75


def expansions():
    with open(os.path.join(HERE, "expansions.json"), encoding="utf-8") as f:
        return json.load(f)["expansions"]


def expansion(key):
    for e in expansions():
        if e["key"] == key:
            return e
    raise SystemExit("no expansion %r (%s)" % (key, ", ".join(e["key"] for e in expansions())))


def pins_for(base, ex):
    """The tool's pins for [ex]: its build, and every expansion up to its own in the manifest (the driver picks its own maps after)."""
    pins = dict(base)
    pins["build"] = ex["build"]
    pins["max_expansion"] = ex["id"]
    return pins


def select_maps(manifest, ex):
    """The manifest's maps of [ex]: those whose Map.ExpansionID is the expansion's, and the maps 3.3.5a has that it made over when
    [with_revamped]; never one that is the same as 3.3.5a's ("stock"), never one already made elsewhere unless it is the expansion's own."""
    out = []
    for m in manifest.get("maps", []):
        if m.get("status") == "same_as_stock":
            continue
        own = m.get("expansion") == ex["id"]
        revamped = ex.get("with_revamped") and m.get("origin") == "revamped"
        if own or revamped:
            out.append(m)
    return out


class Progress:
    """`progress.json`: what the launcher shows. Written whole each time (a temp file renamed), so a reader never sees half of it."""

    def __init__(self, path, ex, stages):
        self.path = path
        self.data = {"expansion": ex["key"], "name": ex["name"], "build": ex["build"], "state": "starting", "stage": "", "unit": "",
                     "done": 0, "total": 0, "message": "", "stages": stages, "started": int(time.time()), "updated": 0,
                     "units": {}, "errors": []}

    def set(self, **kw):
        self.data.update(kw)
        self.data["updated"] = int(time.time())
        tmp = self.path + ".tmp"
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=1)
        os.replace(tmp, self.path)

    def unit(self, name, state, message=""):
        self.data["units"][name] = {"state": state, "message": message}
        self.set()


def load_progress(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def tool_command(python, tool_dir):
    """The command prefix that runs the tool from [tool_dir] (the folder that holds `catabackport/`)."""
    return python.split() + ["-m", "catabackport"], tool_dir


def run_tool(prefix, cwd, args, log, runner=subprocess.run):
    """One tool command; its output appended to [log]. Returns its exit status."""
    with open(log, "a", encoding="utf-8") as out:
        out.write("$ %s\n" % " ".join(prefix + args))
        out.flush()
        return runner(prefix + args, cwd=cwd, stdout=out, stderr=subprocess.STDOUT).returncode


def units_of(plan):
    return [u["unit"] for u in plan.get("units", [])]


def run(key, root, stages=None, tool=None, python=None, source="wago", listfile=None, jobs=None, runner=subprocess.run):
    ex = expansion(key)
    stages = stages or list(DEFAULT_STAGES)
    base = os.path.join(root, ex["key"])
    work, release = os.path.join(base, "work"), os.path.join(base, "release")
    os.makedirs(work, exist_ok=True)
    os.makedirs(release, exist_ok=True)
    log = os.path.join(base, "convert.log")
    progress = Progress(os.path.join(base, "progress.json"), ex, stages)
    tool = tool or os.path.join(HERE, "..", "tools")
    prefix, cwd = tool_command(python or sys.executable, tool)

    # the tool's own pins, with the expansion's build
    with open(os.path.join(cwd, "catabackport", "pins.json"), encoding="utf-8") as f:
        pins = pins_for(json.load(f), ex)
    pins_path = os.path.join(work, "pins.json")
    with open(pins_path, "w", encoding="utf-8") as f:
        json.dump(pins, f, indent=1)

    common = ["--work", work, "--pins", pins_path, "--source", source]
    if listfile:
        common += ["--listfile", listfile]

    progress.set(state="running", stage="inventory", message="Reading %s's maps from build %s" % (ex["name"], ex["build"]))
    manifest_path = os.path.join(work, "manifest.json")
    if not os.path.isfile(manifest_path):
        status = run_tool(prefix, cwd, ["inventory"] + common, log, runner)
        if status == EX_DEFERRED:
            progress.set(state="deferred", message="The source (wago.tools) is not answering: run it again later")
            return EX_DEFERRED
        if status != 0 or not os.path.isfile(manifest_path):
            progress.set(state="failed", message="The inventory failed (status %d): see convert.log" % status)
            return 3
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    maps = select_maps(manifest, ex)
    if not maps:
        progress.set(state="done", message="No maps of %s to convert in build %s" % (ex["name"], ex["build"]), total=0)
        return 0
    spec = ",".join(str(m["id"]) for m in maps)

    progress.set(stage="plan", message="%d maps" % len(maps))
    plan_path = os.path.join(work, "plan.json")
    status = run_tool(prefix, cwd, ["plan", "--work", work, "--maps", spec], log, runner)
    plan = None
    if status == 0 and os.path.isfile(plan_path):
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
    if not plan or not plan.get("units"):
        progress.set(state="failed", message="Nothing could be planned (status %d): see convert.log" % status)
        return 3
    units = units_of(plan)
    progress.set(total=len(units), done=0, message="%d units" % len(units))

    failures, deferred = 0, 0
    for i, unit in enumerate(units):
        progress.set(stage=",".join(stages), unit=unit, done=i, message="%s (%d of %d)" % (unit, i + 1, len(units)))
        args = ["run"] + common + ["--release", release, "--stages", ",".join(stages), "--only", unit]
        if jobs:
            args += ["--jobs", str(jobs)]
        status = run_tool(prefix, cwd, args, log, runner)
        if status == 0:
            progress.unit(unit, "done")
        elif status == EX_DEFERRED:
            deferred += 1
            progress.unit(unit, "deferred", "the source was down")
        else:
            failures += 1
            progress.unit(unit, "failed", "status %d" % status)
            progress.data["errors"].append("%s: status %d" % (unit, status))
        progress.set(done=i + 1)
    run_tool(prefix, cwd, ["assemble", "--release", release], log, runner)
    state = "done" if not failures and not deferred else ("deferred" if deferred and not failures else "partial")
    progress.set(state=state, stage="", unit="", done=len(units), message={
        "done": "%d units converted into %s" % (len(units), release), "deferred": "wago.tools did not answer for some units: run it again",
        "partial": "%d of %d units failed: see convert.log" % (failures, len(units))}[state])
    return 3 if failures == len(units) else (EX_DEFERRED if state == "deferred" else 0)


def main(argv):
    if len(argv) < 2 or argv[1] not in ("run", "list", "status"):
        print(__doc__)
        return 2
    if argv[1] == "list":
        for e in expansions():
            print("%-10s %-22s ExpansionID %d  build %s" % (e["key"], e["name"], e["id"], e["build"]))
        return 0

    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    if len(argv) < 3 or not opt("--root"):
        print(__doc__)
        return 2
    if argv[1] == "status":
        data = load_progress(os.path.join(opt("--root"), argv[2], "progress.json"))
        print(json.dumps(data, indent=1) if data else "not started")
        return 0
    stages = opt("--stages")
    return run(argv[2], opt("--root"), stages.split(",") if stages else None, tool=opt("--tool"), python=opt("--python"),
               source=opt("--source", "wago"), listfile=opt("--listfile"), jobs=opt("--jobs"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
