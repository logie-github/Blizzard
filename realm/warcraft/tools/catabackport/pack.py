"""Stages `pack` and `assemble`.

pack: a unit's output as `cata-<unit>.tar.xz` + `cata-<unit>.json`, in the layout the app's `zones_data_realm` and WrathppZones read
(cata-zones: TAG, client/files/..., client/files.txt, client/same.txt, client/minimap.txt, server/{maps,vmaps,mmaps,cameras},
server/same.txt) plus client/dbc/*.txt (the unit's table rows), server/world.sql, server/world_off.sql and pack.json. Deterministic:
sorted names, fixed times and owners (util.det_tar), same bytes for the same input.
assemble: every pack's json into index.json (what the app reads: pack, size, sha256, maps, status, requires), summary.txt and
report.json. Idempotent; a pack that is not `ok` or `partial` is listed with its reason and left out of the index's installable list.
"""
import json
import os
import shutil

from . import util, zones_adapter

SERVER_PARTS = ("maps", "vmaps", "mmaps", "cameras")


def build_dir(unit_dir, pack_dir, unit, m, status, input_hash):
    """<pack_dir> as the archive's content. unit_dir has out/client and out/server (and world.sql)."""
    pkg = zones_adapter.load("package")
    shutil.rmtree(pack_dir, ignore_errors=True)
    out = os.path.join(unit_dir, "out")
    client = os.path.join(pack_dir, "client")
    shutil.copytree(os.path.join(out, "client"), client)
    os.makedirs(os.path.join(client, "files"), exist_ok=True)
    server = os.path.join(pack_dir, "server")
    os.makedirs(server, exist_ok=True)
    if os.path.isdir(os.path.join(out, "server")):
        for part in SERVER_PARTS:
            if os.path.isdir(os.path.join(out, "server", part)):
                shutil.copytree(os.path.join(out, "server", part), os.path.join(server, part))
    for name in ("world.sql", "world_off.sql"):
        if os.path.exists(os.path.join(out, name)):
            shutil.copyfile(os.path.join(out, name), os.path.join(server, name))
    for part, folder in (("client", os.path.join(client, "files")), ("server", server)):
        same = pkg.dedupe(folder) if part == "client" or os.path.isdir(os.path.join(server, "maps")) else []
        with open(os.path.join(pack_dir, part, "same.txt"), "w", newline="\n") as f:
            f.write("".join(f"{a.replace(os.sep, chr(92)) if part == 'client' else a}\t"
                            f"{b.replace(os.sep, chr(92)) if part == 'client' else b}\n" for a, b in same))
    listed = []
    for root, _, names in os.walk(os.path.join(client, "files")):
        for name in names:
            listed.append(os.path.relpath(os.path.join(root, name), os.path.join(client, "files")).replace(os.sep, "\\"))
    listed += [l.split("\t")[0] for l in open(os.path.join(client, "same.txt")) if l.strip()]
    util.write_atomic(os.path.join(client, "files.txt"), "\n".join(sorted(listed)) + "\n" if listed else "")
    util.write_atomic(os.path.join(pack_dir, "TAG"), f"{unit['unit']}-{input_hash}\n")
    util.dump_json(os.path.join(pack_dir, "pack.json"), {"unit": unit["unit"], "map": m["id"], "new_id": m["new_id"], "dir": m["new_dir"],
                                                         "status": status, "input_hash": input_hash})
    return len(listed)


def run(unit_dir, release_dir, unit, m, status, report, pins, requires=()):
    """Packs one unit into release_dir. Returns the unit's index entry."""
    input_hash = unit["input_hash"]
    pack_dir = os.path.join(unit_dir, "pack")
    nfiles = build_dir(unit_dir, pack_dir, unit, m, status, input_hash)
    unpacked = sum(os.path.getsize(os.path.join(r, n)) for r, _, ns in os.walk(pack_dir) for n in ns)
    name = f"cata-{unit['unit']}.tar.xz"
    dest = os.path.join(release_dir, name)
    util.det_tar(pack_dir, dest, pins["pack_epoch"])
    entry = {"unit": unit["unit"], "asset": name, "map": m["id"], "new_id": m["new_id"], "dir": m["new_dir"], "name": m.get("name", ""),
             "group": m["group"], "part": unit["part"], "parts": unit["parts"], "status": status, "input_hash": input_hash,
             "size": os.path.getsize(dest), "unpacked": unpacked, "files": nfiles, "sha256": util.sha256_file(dest),
             "requires": list(requires), "report": report}
    util.dump_json(os.path.join(release_dir, f"cata-{unit['unit']}.json"), entry)
    return entry


def assemble(release_dir, pins, extra_notes=()):
    """index.json, summary.txt and report.json of every cata-*.json in release_dir. Returns the index."""
    entries = []
    for n in sorted(os.listdir(release_dir)):
        if n.startswith("cata-") and n.endswith(".json"):
            e = util.load_json(os.path.join(release_dir, n))
            if e and "unit" in e:
                entries.append(e)
    ok = [e for e in entries if e["status"] in ("ok", "partial")]
    index = {"version": 1, "build": pins["build"], "pins": {k: pins[k] for k in ("build", "converter", "core")},
             "packs": [{k: e[k] for k in ("unit", "asset", "map", "new_id", "dir", "name", "group", "part", "parts", "status",
                                           "input_hash", "size", "unpacked", "sha256", "requires")} for e in ok],
             "not_installable": [{"unit": e["unit"], "status": e["status"]} for e in entries if e["status"] not in ("ok", "partial")]}
    util.dump_json(os.path.join(release_dir, "index.json"), index)
    util.dump_json(os.path.join(release_dir, "report.json"), {"entries": entries, "notes": list(extra_notes)})
    lines = [f"Cataclysm backport, build {pins['build']}: {len(ok)} packs installable of {len(entries)} made",
             f"packed {sum(e['size'] for e in ok) >> 20} MB, unpacked {sum(e['unpacked'] for e in ok) >> 20} MB"]
    for e in entries:
        lines.append(f"  {e['status']:8} {e['unit']}: {e['files']} files, {e['size'] >> 10} KB packed"
                     + (f", {len(e['report'].get('problems', []))} problems" if e.get("report") else ""))
        for pb in (e.get("report") or {}).get("problems", [])[:5]:
            lines.append(f"           - {pb}")
    lines += [f"note: {n}" for n in extra_notes]
    util.write_atomic(os.path.join(release_dir, "summary.txt"), "\n".join(lines) + "\n")
    return index
