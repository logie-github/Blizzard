"""Stage `extract`: the world server's maps, vmaps and mmaps for one unit, with AzerothCore's own tools.

As zones/package.py `server_data`, for the unit's maps (that function loops over the seven starting-area maps, so this is the
same recipe, generic): a stand-in 3.3.5a game made of the unit's converted files and a Map.dbc of the unit's maps alone (from the
`tables` stage), then map_extractor, vmap4_extractor, vmap4_assembler and mmaps_generator from TOOLS (built from the realm's
core: scripts/build-azerothcore.sh; the workflow builds or downloads them). A unit without the tools is `skipped` with a report
line, never a failure: the client half of its pack is still good.
"""
import os
import shutil
import subprocess

from . import zones_adapter

COUNTS = ("maps", "vmaps", "mmaps")


def have_tools(tools):
    return bool(tools) and all(os.path.exists(os.path.join(tools, t)) for t in
                               ("map_extractor", "vmap4_extractor", "vmap4_assembler", "mmaps_generator", "zones_mkmpq"))


def run(unit_maps, unit_dir, tools, server_dbc, log=print):
    """unit_dir: <work>/<unit> (its conv/ and out/client/dbc/Map.txt). Writes out/server/{maps,vmaps,mmaps}. Returns counts."""
    pkg = zones_adapter.load("package")
    pkg.MKMPQ = os.path.join(tools, "zones_mkmpq")
    conv = os.path.join(unit_dir, "conv")
    work = os.path.join(unit_dir, "extract")
    out = os.path.join(unit_dir, "out", "server")
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)
    game = os.path.join(work, "game", "Data")
    loose = os.path.join(work, "loose")
    os.makedirs(os.path.join(game, "enUS"))
    os.makedirs(os.path.join(loose, "DBFilesClient"))
    with open(os.path.join(loose, "component.wow-enUS.txt"), "w") as f:
        f.write('<?xml version="1.0"?><componentinfo><component name="WoW" version="12340"/></componentinfo>')
    types, rows = None, []
    for line in open(os.path.join(unit_dir, "out", "client", "dbc", "Map.txt"), encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if parts[0] == "types":
            types = parts[1]
        elif parts[0] == "put":
            rows.append(parts[1:])
    pkg.dbc(os.path.join(loose, "DBFilesClient", "Map.dbc"), rows, types)
    shutil.copyfile(pkg.find(server_dbc, "LiquidType.dbc"), os.path.join(loose, "DBFilesClient", "LiquidType.dbc"))
    stock_go = zones_adapter.load("common").Dbc(pkg.find(server_dbc, "GameObjectDisplayInfo.dbc"))
    pkg.dbc(os.path.join(loose, "DBFilesClient", "GameObjectDisplayInfo.dbc"), [], "i" * stock_go.nfields)
    pkg.mpq(os.path.join(game, "enUS", "locale-enUS.MPQ"), loose,
            ["component.wow-enUS.txt", "DBFilesClient\\Map.dbc", "DBFilesClient\\LiquidType.dbc", "DBFilesClient\\GameObjectDisplayInfo.dbc"])
    world = [os.path.relpath(os.path.join(r, n), conv).replace("/", "\\") for r, _, ns in os.walk(conv)
             for n in ns if n.endswith((".adt", ".wdt", ".wdl", ".m2", ".skin", ".wmo"))]
    pkg.mpq(os.path.join(game, "common.MPQ"), conv, world)
    data = os.path.join(work, "data")
    os.makedirs(data)
    nul = subprocess.DEVNULL
    pkg.run(os.path.join(tools, "map_extractor"), "-i", os.path.join(work, "game"), "-o", data, "-e", "1", cwd=data, stdout=nul)
    pkg.run(os.path.join(tools, "vmap4_extractor"), "-d", game + "/", cwd=data, stdout=nul)
    os.makedirs(os.path.join(data, "vmaps"), exist_ok=True)
    pkg.run(os.path.join(tools, "vmap4_assembler"), "Buildings", "vmaps", cwd=data, stdout=nul)
    os.makedirs(os.path.join(data, "mmaps"), exist_ok=True)
    shutil.copyfile(os.path.join(tools, "mmaps-config.yaml"), os.path.join(data, "mmaps-config.yaml"))
    for m in unit_maps:
        pkg.run(os.path.join(tools, "mmaps_generator"), m["new_id"], "--config", "mmaps-config.yaml", "--threads",
                os.cpu_count() or 4, "--silent", cwd=data, stdout=nul)
    for part in COUNTS:
        dest = os.path.join(out, part)
        os.makedirs(dest, exist_ok=True)
        for name in sorted(os.listdir(os.path.join(data, part))):
            if name != "temp_gameobject_models":
                shutil.copyfile(os.path.join(data, part, name), os.path.join(dest, name))
    counts = {p: len(os.listdir(os.path.join(out, p))) for p in COUNTS}
    shutil.rmtree(work)
    log(f"{os.path.basename(unit_dir)}: server data {counts}")
    return counts
