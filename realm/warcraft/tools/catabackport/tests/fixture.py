"""A tiny synthetic Cataclysm "build" for the tests: tables as CSV, a few files by id, a listfile. No game files."""
import os
import struct


def chunk(magic, body):
    """A chunk as files store it: the magic reversed."""
    return magic[::-1] + struct.pack("<I", len(body)) + body


def adt(textures=()):
    body = b"".join(chunk(b"MVER", struct.pack("<I", 18)) for _ in [0])
    body += chunk(b"MCIN", b"\0" * 4096)
    if textures:
        body += chunk(b"MTEX", b"".join(t.encode() + b"\0" for t in textures))
    return body


def wdt(tiles):
    main = bytearray(32768)
    for (x, y) in tiles:
        struct.pack_into("<I", main, (y * 64 + x) * 8, 1 | 2)      # (Cataclysm keeps flag 2 on empty tiles too)
    return chunk(b"MVER", struct.pack("<I", 18)) + chunk(b"MPHD", b"\0" * 32) + chunk(b"MAIN", bytes(main))


def blp(w=4, h=4):
    return b"BLP2" + struct.pack("<I", 1) + bytes([2, 8, 1, 1]) + struct.pack("<II", w, h) + b"\0" * 16


MAP_COLUMNS = ["ID", "Directory", "MapName_lang", "InstanceType", "ParentMapID", "ExpansionID", "WdtFileDataID"]
MAPS = [
    # id, directory, name, instance type, parent, expansion, wdt fdid
    (900, "TinyDungeon", "The Tiny Dungeon", 1, 0, 3, 5000),
    (901, "TinyDungeonPhase1", "The Tiny Dungeon (phase)", 0, 900, 3, 5001),
    (36, "DeadminesInstance", "Deadmines", 1, 0, 3, 5002),          # an id and a name 3.3.5a has
    (902, "BigWorld", "Big World", 0, 0, 3, 5003),                   # (a continent big enough to split)
    (903, "LaterExpansion", "Pandaria", 0, 0, 4, 5004),              # past Cataclysm
    (904, "", "No Directory", 0, 0, 3, 0),
    (389, "OrgrimmarInstance", "Ragefire Chasm", 1, 0, 0, 5005),   # (3.3.5a has it, Cataclysm did not make it over: stock)
    (905, "Development_Test", "dev", 0, 0, 3, 5006),               # (a developer map)
]
LISTFILE = [
    (5000, "world/maps/tinydungeon/tinydungeon.wdt"),
    (5001, "world/maps/tinydungeonphase1/tinydungeonphase1.wdt"),
    (5002, "world/maps/deadminesinstance/deadminesinstance.wdt"),
    (5003, "world/maps/bigworld/bigworld.wdt"),
    (5005, "world/maps/orgrimmarinstance/orgrimmarinstance.wdt"),
    (5006, "world/maps/development_test/development_test.wdt"),
    (6000, "world/maps/tinydungeon/tinydungeon_0_0.adt"),
    (6001, "world/maps/tinydungeon/tinydungeon_1_0.adt"),
    (6002, "world/maps/tinydungeon/tinydungeon_1_0.adt".replace(".adt", "_tex1.adt")),     # (not taken)
    (6100, "world/maps/tinydungeonphase1/tinydungeonphase1_1_0.adt"),
    (6200, "world/maps/deadminesinstance/deadminesinstance_0_0.adt"),
    (7000, "tileset/test/ground.blp"),
    (7001, "tileset/test/ground_s.blp"),
    (7100, "world/minimaps/tinydungeon/map00_00.blp"),
    (7101, "world/minimaps/tinydungeon/map01_00.blp"),
]
for n in range(10):
    LISTFILE.append((6300 + n, f"world/maps/bigworld/bigworld_{n}_0.adt"))
    LISTFILE.append((6400 + n, f"world/maps/bigworld/bigworld_{n}_1.adt"))


def build(root):
    """Writes the fixture under root: tables/, files/ (the source), listfile.csv. Returns the listfile path."""
    os.makedirs(os.path.join(root, "tables"), exist_ok=True)
    os.makedirs(os.path.join(root, "files"), exist_ok=True)
    with open(os.path.join(root, "tables", "Map.csv"), "w", encoding="utf-8") as f:
        f.write(",".join(MAP_COLUMNS) + "\n")
        for r in MAPS:
            f.write(",".join(str(v) for v in r) + "\n")
    with open(os.path.join(root, "tables", "AreaTable.csv"), "w", encoding="utf-8") as f:
        f.write("ID,ContinentID,ParentAreaID,AreaBit,Flags,AreaName_lang\n")
        f.write("9000,900,4000,4090,1049088,Tiny Hall\n")     # (an id 3.3.5a hasn't, under a parent it has; bit free; flying/subzone flags to drop)
        f.write("4000,900,0,10,0,Clash Hall\n")              # (an id 3.3.5a has; bit 10 taken)
    with open(os.path.join(root, "tables", "LiquidType.csv"), "w", encoding="utf-8") as f:
        f.write("ID,SoundBank\n1,0\n2,1\n")
    tiles = {5000: [(0, 0), (1, 0)], 5001: [(1, 0)], 5002: [(0, 0)], 5003: [(n, y) for n in range(10) for y in (0, 1)], 5005: [(0, 0)], 5006: [(0, 0)]}
    for fdid, t in tiles.items():
        open(os.path.join(root, "files", str(fdid)), "wb").write(wdt(t))
    for fdid in (6000, 6001):
        open(os.path.join(root, "files", str(fdid)), "wb").write(adt(["tileset/test/ground_s.blp"]))
    for fdid in [6100, 6200] + [6300 + n for n in range(10)] + [6400 + n for n in range(10)]:
        open(os.path.join(root, "files", str(fdid)), "wb").write(adt(["tileset/test/ground.blp"]))
    for fdid in (7000, 7001, 7100, 7101):
        open(os.path.join(root, "files", str(fdid)), "wb").write(blp())
    lf = os.path.join(root, "listfile.csv")
    with open(lf, "w", encoding="utf-8") as f:
        for fdid, path in LISTFILE:
            f.write(f"{fdid};{path}\n")
    # (a Map.dbd and an AreaTable.dbd in WoWDBDefs' form, 3.3.5a's layout only)
    dbd = os.path.join(root, "dbd")
    os.makedirs(dbd, exist_ok=True)
    open(os.path.join(dbd, "Map.dbd"), "w").write(
        "COLUMNS\nint ID\nstring Directory\nlocstring MapName_lang\nint ParentMapID\n\nLAYOUT 1\nBUILD 3.3.5.12340\n$id$ID<32>\nDirectory\nMapName_lang\nParentMapID<32>\n")
    open(os.path.join(dbd, "AreaTable.dbd"), "w").write(
        "COLUMNS\nint ID\nint ContinentID\nint ParentAreaID\nint AreaBit\nint Flags\nlocstring AreaName_lang\n\nLAYOUT 1\nBUILD 3.3.5.12340\n"
        "$id$ID<32>\nContinentID<32>\nParentAreaID<32>\nAreaBit<32>\nFlags<32>\nAreaName_lang\n")
    return lf


FAKE_CONVERTER = '''
import json, shutil, sys
a = sys.argv[1:]
assert a[0] == "convert"
src, out, rep = a[1], a[a.index("-o") + 1], a[a.index("--report") + 1]
shutil.copytree(src, out, dirs_exist_ok=True)
json.dump({"accounting": {"read": 1, "written": 1}}, open(rep, "w"))
'''
