#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Makes Brill: A Place Among the Forsaken's world SQL (data/sql/chromiecraft/world/brill_town_world.sql)
from its questlines (tools/town/*.py, each a LINE: see tools/town/README.md for what a line holds).

Each questline is optional and stands alone; this turns their data into the game's rows (creatures,
objects, quests, words) and into the module's own tables, which src/BrillTown.cpp reads as the world
server starts:
- brill_town_phase: which of the town's phases a player is in while in Brill (a bit, and the conditions
  for it: what a questline changed in the town for them);
- brill_town_gossip: what a creature says to a player (its greetings by condition) and the options the
  module adds to its menu (a quest's credit, a choice, a reply, its wares, the house's furniture);
- brill_town_use: what an object does when a player uses it (a quest's credit, words).

Run it after changing a questline; the output is committed.
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "sql", "chromiecraft", "world", "brill_town_world.sql")
TOWN = os.path.join(HERE, "town")

# The questlines, in order, and the ids each has (a hundred of each kind from its base: quests, creature
# entries, objects, words, and the spawns' guids).
LINES = ["house", "grave", "apprentice", "scarlet", "customer", "deathguard", "well", "gallows",
         # the Community Projects (opened by Brill Endures)
         "endures", "chapel", "library", "garden", "surgeon", "caravan", "brewery"]
BASE = {key: 970200 + 100 * i for i, key in enumerate(LINES)}

# The mod-brill-home ids a line may name (tools/build_sql.py).
KNOWN = {
    "home.house": 970120, "home.welcome": 970121, "home.bed": 970122, "home.dog": 970123,
    "carolai.tonic": 970124, "carolai.locket": 970125, "carolai.gift": 970126, "carolai.tea": 970127,
    "carolai.lily": 970128,
}
# The house's own flags (brill_home.flags: src/BrillHome.cpp) a condition may ask about.
FLAGS = {"DOG": 0x2, "LOVERS": 0x10, "FRIENDS": 0x20, "CAROLAI_HOME": 0x50}
# The phases the town's lines share out (the house's are 0x100 to 0x20000).
# (then 0x2 to 0x80: in Brill nothing of the game's own is in those)
FREE_PHASES = [1 << b for b in range(18, 32)] + [1 << b for b in range(1, 8)]
# A project's stages: the game's invisibility kinds (not 0, the general one, 3 traps', 6 drunkenness').
STAGE_TYPES = [1, 2, 4, 5, 7, 8, 9, 10, 11]
# The town's day (game events: their entries, when they start, how long, in minutes). A spawn "when" one is
# there only then.
SCHEDULES = {"morning": (230, 6 * 60, 4 * 60), "day": (231, 10 * 60, 8 * 60), "evening": (232, 18 * 60, 4 * 60),
             "night": (233, 22 * 60, 8 * 60)}

# The house (tools/build_sql.py): a line may place things in it by the house's own coordinates.
HOUSE_X, HOUSE_Y, HOUSE_O, FLOOR = 2275.0, 480.5, 5.0615, 29.96 + 4.1
# Brill, where the town's phases apply (src/BrillTown.cpp): a spawn in a phase must be in it.
BRILL_X, BRILL_Y, BRILL_RADIUS = 2275.0, 330.0, 165.0
NEAR_HOUSE = 35.0   # (and by the house, at Brill's north edge)

# The house's cellar (tools/town/house.py): the game's Duskwood_Inn.wmo (Brill's own tavern, the Gallows'
# End, is one), whose cellar is a stone room of 19 by 20 yards with its barrels, kegs, crates and cobwebs
# (the model's own, always drawn), placed as an object deep under the house, turned as the house is, its
# cellar's middle (the model's -27, 2) under the house's middle. Its top (23.2 above its base) is 6 yards
# under the lowest ground over it (33.4: the server's maps), so nothing of it shows above. A line places
# things in it by the model's own coordinates: ["cellar", x, y, dz, deg], dz above the cellar's floor
# (6.72 under the model's base). src/BrillTown.cpp keeps the same numbers (CELLAR_*).
CELLAR_O = HOUSE_O
CELLAR_MIDDLE = (-27.0, 2.0)
CELLAR_Z = 4.0
CELLAR_FLOOR = CELLAR_Z - 6.72
# New object looks (GameObjectDisplayInfo, the game's and the server's): the cellar and its ladder,
# models of the game's own (9700 to 9709: clear of the game's, the Worgen's and the Murlocs').
DISPLAYS = [
    (9700, "World\\wmo\\Azeroth\\Buildings\\Duskwood_Inn\\Duskwood_Inn.wmo", (-37.7, -13.5, -6.7, 21.9, 18.7, 23.2)),
    (9701, "World\\Expansion02\\Doodads\\Generic\\Human\\Northrend_HumanLadder\\Final\\HU_HumanLadder.mdx",
     (-0.04, -0.18, 0.0, 0.04, 0.37, 3.55)),
]
CLIENT_DBC = os.path.join(HERE, "..", "data", "client", "dbc")

MAP_ZONE = {0: 85}


def q(text):
    return "'" + str(text).replace("\\", "\\\\").replace("'", "\\'") + "'"


def die(line, message):
    sys.exit(f"tools/town/{line}.py: {message}")


def house_point(lx, ly, deg=0.0):
    c, s = math.cos(HOUSE_O), math.sin(HOUSE_O)
    return (HOUSE_X + lx * c - ly * s, HOUSE_Y + lx * s + ly * c, (HOUSE_O + math.radians(deg)) % (2 * math.pi))


def cellar_origin():
    c, s = math.cos(CELLAR_O), math.sin(CELLAR_O)
    mx, my = CELLAR_MIDDLE
    return HOUSE_X - (mx * c - my * s), HOUSE_Y - (mx * s + my * c)


def cellar_point(lx, ly, deg=0.0):
    ox, oy = cellar_origin()
    c, s = math.cos(CELLAR_O), math.sin(CELLAR_O)
    return (ox + lx * c - ly * s, oy + lx * s + ly * c, (CELLAR_O + math.radians(deg)) % (2 * math.pi))


def write_client_displays():
    """data/client/dbc/GameObjectDisplayInfo.txt: the new looks for the game's own table (src/BrillHomePatch.cpp
    puts them in the game's patch with Corn's display)."""
    with open(os.path.join(CLIENT_DBC, "GameObjectDisplayInfo.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# GameObjectDisplayInfo: the house's cellar and its ladder (tools/build_town.py)\n")
        f.write("types\tisiiiiiiiiiiffffffi\n")
        for d, path, box in DISPLAYS:
            # (a backslash written twice: the patch's reader takes one as an escape)
            f.write("put\t" + "\t".join([str(d), path.replace("\\", "\\\\")] + ["0"] * 10 + [repr(float(v)) for v in box] + ["0"]) + "\n")


def load(key):
    spec = importlib.util.spec_from_file_location(f"town_{key}", os.path.join(TOWN, f"{key}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LINE


class Ids:
    def __init__(self, key, base):
        self.key, self.base = key, base
        self.next = {}
        self.ids = {}

    def take(self, kind, name):
        if (kind, name) in self.ids:
            die(self.key, f"two {kind}s called {name}")
        n = self.next.get(kind, 0)
        if n >= 100:
            die(self.key, f"more than 100 {kind}s")
        self.next[kind] = n + 1
        self.ids[(kind, name)] = self.base + n
        return self.base + n


def main():
    lines = [(key, load(key)) for key in LINES if os.path.exists(os.path.join(TOWN, f"{key}.py"))]
    quests, npcs, objects, texts, phases = {}, {}, {}, {}, {}
    ids = {key: Ids(key, BASE[key]) for key, _ in lines}
    free = list(FREE_PHASES)
    stage_type, stage_count = {}, {}
    free_types = list(STAGE_TYPES)

    # First every line's names, so a line may name another's.
    for key, line in lines:
        i = ids[key]
        for quest in line.get("quests", []):
            quests[f"{key}.{quest['id']}"] = i.take("quest", quest["id"])
        for marker in line.get("markers", []):
            quests[f"{key}.{marker}"] = i.take("quest", marker)
        for npc in line.get("npcs", []):
            npcs[f"{key}.{npc['id']}"] = i.take("npc", npc["id"])
        for credit in line.get("credits", []):
            npcs[f"{key}.{credit['id']}"] = i.take("npc", credit["id"])
        for obj in line.get("objects", []):
            objects[f"{key}.{obj['id']}"] = i.take("object", obj["id"])
        for name in line.get("phases", {}):
            if not free:
                die(key, f"the town has no more phases to give ({len(FREE_PHASES)} in all)")
            phases[f"{key}.{name}"] = free.pop(0)
        if line.get("stages"):
            if not free_types:
                die(key, "no invisibility kind left for its stages")
            stage_type[key] = free_types.pop(0)
            stage_count[key] = len(line["stages"])
        # (a phase for each stage a line's spawns go at: they're there until it's reached)
        for k in sorted({t.get("until") for t in line.get("npcs", []) + line.get("objects", []) if t.get("until")}):
            if not line.get("stages") or not 1 <= k <= len(line["stages"]):
                die(key, f"\"until\": {k} isn't one of its stages")
            if not free:
                die(key, f"the town has no more phases to give ({len(FREE_PHASES)} in all)")
            phases[f"{key}.__until{k}"] = free.pop(0)

    def ref(key, table, name, what):
        if isinstance(name, int):
            return name
        full = name if "." in name else f"{key}.{name}"
        if table is quests and full in KNOWN:
            return KNOWN[full]
        if full not in table:
            die(key, f"no {what} called {name}")
        return table[full]

    def cond(key, items):
        out = []
        for item in items or []:
            neg = item.startswith("!")
            body = item[1:] if neg else item
            if body in FLAGS:
                out.append(("!F" if neg else "F") + str(FLAGS[body]))
            elif body == "OWN":
                out.append("!O" if neg else "O")
            elif body.startswith("UPG:"):
                out.append(("!U" if neg else "U") + str(int(body[4:])))
            elif body.startswith("DAY:"):
                out.append("D" + str(int(body[4:])))
            elif len(body) > 2 and body[1] == ":" and body[0] in "RTAICM":
                kind, name = body[0], body[2:]
                kind = "R" if kind == "M" else kind
                out.append(("!" if neg else "") + kind + str(ref(key, quests, name, "quest")))
            else:
                die(key, f"a condition I don't know: {item}")
        return " ".join(out)

    def place(key, spawn):
        """(map, x, y, z, o) from a spawn: [map, x, y, z, o] in the world, ["house", lx, ly, dz, deg] in the
        house or ["cellar", lx, ly, dz, deg] in its cellar."""
        if spawn[0] == "cellar":
            x, y, o = cellar_point(spawn[1], spawn[2], spawn[4] if len(spawn) > 4 else 0)
            return 0, x, y, CELLAR_FLOOR + (spawn[3] if len(spawn) > 3 else 0), o
        if spawn[0] == "house":
            x, y, o = house_point(spawn[1], spawn[2], spawn[4] if len(spawn) > 4 else 0)
            return 0, x, y, FLOOR + (spawn[3] if len(spawn) > 3 else 0), o
        if len(spawn) < 4:
            die(key, f"a spawn needs a map and x, y, z: {spawn}")
        return spawn[0], spawn[1], spawn[2], spawn[3], spawn[4] if len(spawn) > 4 else 0.0

    def phase_of(key, thing):
        name = thing.get("phase")
        if thing.get("until"):
            if name:
                die(key, f"{thing['id']} has both a phase and \"until\"")
            name = f"__until{thing['until']}"
        if not name:
            return 1
        full = name if "." in name else f"{key}.{name}"
        if full not in phases:
            die(key, f"no phase called {name}")
        return phases[full]

    def in_brill(m, x, y):
        return m == 0 and (math.hypot(x - BRILL_X, y - BRILL_Y) < BRILL_RADIUS or math.hypot(x - HOUSE_X, y - HOUSE_Y) < NEAR_HOUSE)

    def needs(key, thing):
        """The stages a spawn shows from: [(invisibility kind, stage)]: its own line's "from", others' "needs"."""
        out = []
        want = dict(thing.get("needs", {}))
        if thing.get("from"):
            want[key] = thing["from"]
        for other, k in want.items():
            if other not in stage_type:
                die(key, f"{thing['id']} needs {other}'s stages, which it hasn't")
            if not 1 <= k <= stage_count[other]:
                die(key, f"{thing['id']}: {other} has no stage {k}")
            out.append((stage_type[other], k))
        return out

    invis, events, conditions, trainer_of = [], [], [], []

    def spawned(key, thing, kind, guid, m, x, y):
        staged = needs(key, thing)
        if staged and not in_brill(m, x, y):
            die(key, f"{thing['id']} shows from a stage but is outside Brill, where no one would see it")
        for t, k in staged:
            invis.append(f"('{kind}', {guid}, {t}, {k})")
        when = thing.get("when")
        if when:
            if when not in SCHEDULES:
                die(key, f"{thing['id']}: no time of day called {when}")
            events.append((kind, SCHEDULES[when][0], guid))

    out = []
    w = out.append
    w("-- Brill: A Place Among the Forsaken (mod-brill-home; ChromieCraft's world database alone: ctl.sh")
    w("-- realm_sql). Made by tools/build_town.py from tools/town/*.py; don't edit by hand. Written to be")
    w("-- applied again: its own rows go first.")
    w("")
    w("CREATE TABLE IF NOT EXISTS `brill_town_phase` (`bit` INT UNSIGNED NOT NULL, `ord` INT UNSIGNED NOT NULL, "
      "`cond` VARCHAR(255) NOT NULL DEFAULT '', PRIMARY KEY (`bit`, `ord`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    w("CREATE TABLE IF NOT EXISTS `brill_town_gossip` (`npc` INT UNSIGNED NOT NULL, `ord` INT UNSIGNED NOT NULL, "
      "`kind` VARCHAR(8) NOT NULL, `cond` VARCHAR(255) NOT NULL DEFAULT '', `icon` TINYINT UNSIGNED NOT NULL DEFAULT 0, "
      "`text` TEXT, `text_id` INT UNSIGNED NOT NULL DEFAULT 0, `action` VARCHAR(16) NOT NULL DEFAULT '', "
      "`quest` INT UNSIGNED NOT NULL DEFAULT 0, `credit` INT UNSIGNED NOT NULL DEFAULT 0, `marker` INT UNSIGNED NOT NULL DEFAULT 0, "
      "`emote` INT UNSIGNED NOT NULL DEFAULT 0, `reply` TEXT, `arg` INT UNSIGNED NOT NULL DEFAULT 0, PRIMARY KEY (`npc`, `ord`)) "
      "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    w("CREATE TABLE IF NOT EXISTS `brill_town_stage` (`type` TINYINT UNSIGNED NOT NULL, `value` INT NOT NULL, `ord` INT UNSIGNED NOT NULL, "
      "`cond` VARCHAR(255) NOT NULL DEFAULT '', PRIMARY KEY (`type`, `value`, `ord`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    w("CREATE TABLE IF NOT EXISTS `brill_town_invis` (`kind` CHAR(1) NOT NULL, `guid` INT UNSIGNED NOT NULL, `type` TINYINT UNSIGNED NOT NULL, "
      "`value` INT NOT NULL, PRIMARY KEY (`kind`, `guid`, `type`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    w("DELETE FROM `brill_town_stage`;")
    w("DELETE FROM `brill_town_invis`;")
    # (made again each time: its columns have grown; every row is this file's)
    w("DROP TABLE IF EXISTS `brill_town_use`;")
    w("CREATE TABLE `brill_town_use` (`go` INT UNSIGNED NOT NULL, `ord` INT UNSIGNED NOT NULL, "
      "`cond` VARCHAR(255) NOT NULL DEFAULT '', `quest` INT UNSIGNED NOT NULL DEFAULT 0, `credit` INT UNSIGNED NOT NULL DEFAULT 0, "
      "`text_id` INT UNSIGNED NOT NULL DEFAULT 0, `marker` INT UNSIGNED NOT NULL DEFAULT 0, "
      "`tele_map` INT NOT NULL DEFAULT -1, `tele_x` FLOAT NOT NULL DEFAULT 0, `tele_y` FLOAT NOT NULL DEFAULT 0, "
      "`tele_z` FLOAT NOT NULL DEFAULT 0, `tele_o` FLOAT NOT NULL DEFAULT 0, PRIMARY KEY (`go`, `ord`)) "
      "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    w("DELETE FROM `brill_town_phase`;")
    w("DELETE FROM `brill_town_gossip`;")
    w("DELETE FROM `brill_town_use`;")
    lo, hi = 970200, 970200 + 100 * len(LINES) - 1
    for table, column in (("creature_template", "entry"), ("creature_template_model", "CreatureID"), ("creature", "guid"),
                          ("gameobject_template", "entry"), ("gameobject", "guid"), ("npc_text", "ID"),
                          ("quest_template", "ID"), ("quest_template_addon", "ID"), ("quest_offer_reward", "ID"),
                          ("quest_request_items", "ID"), ("creature_queststarter", "quest"), ("creature_questender", "quest"),
                          ("smart_scripts", "entryorguid"), ("gameobject_template_addon", "entry"), ("npc_vendor", "entry"),
                          ("game_event_creature", "guid"), ("game_event_gameobject", "guid"),
                          ("creature_default_trainer", "CreatureId"), ("creature_template_movement", "CreatureId")):
        extra = " AND `source_type` = 0" if table == "smart_scripts" else ""
        w(f"DELETE FROM `{table}` WHERE `{column}` BETWEEN {lo} AND {hi}{extra};")
    w(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` BETWEEN {lo} AND {hi};")
    w(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 23 AND `SourceGroup` BETWEEN {lo} AND {hi};")
    w(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND `SourceEntry` BETWEEN {lo} AND {hi};")
    entries = ", ".join(str(e) for e, _, _ in SCHEDULES.values())
    w(f"DELETE FROM `game_event` WHERE `eventEntry` IN ({entries});")
    w(f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN 9700 AND 9709;")
    w("INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `Sound_1`, `Sound_2`, `Sound_3`, `Sound_4`, `Sound_5`, `Sound_6`, "
      "`Sound_7`, `Sound_8`, `Sound_9`, `Sound_10`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, "
      "`ObjectEffectPackageID`) VALUES\n" + ",\n".join(
          f"({d}, {q(path.replace(chr(92) * 2, chr(92)))}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, " + ", ".join(str(v) for v in box) + ", 0)"
          for d, path, box in DISPLAYS) + ";")
    write_client_displays()
    w("INSERT INTO `game_event` (`eventEntry`, `start_time`, `end_time`, `occurence`, `length`, `holiday`, `description`, `world_event`, `announce`) VALUES")
    w(",\n".join(f"({e}, '2020-01-01 {start // 60:02d}:{start % 60:02d}:00', '2037-12-31 00:00:00', 1440, {length}, 0, "
                  f"{q('Brill: ' + name)}, 0, 0)" for name, (e, start, length) in SCHEDULES.items()) + ";")
    w("")

    for key, line in lines:
        i = ids[key]
        w(f"-- {line.get('title', key)}")
        # Its words: every text given by a name gets an npc_text row.
        def text(name, body, many=None):
            tid = i.take("text", name)
            if many:
                cols = ", ".join(f"`text{n}_0`, `text{n}_1`, `Probability{n}`" for n in range(len(many)))
                vals = ", ".join(f"{q(t)}, {q(t)}, {1 / len(many):.3f}" for t in many)
                texts[tid] = f"INSERT INTO `npc_text` (`ID`, {cols}) VALUES ({tid}, {vals});"
            else:
                texts[tid] = f"INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES ({tid}, {q(body)}, {q(body)}, 1);"
            return tid

        # Creatures (its own, and the credits for what its quests ask the player to do).
        rows, models, spawns, smart, movement = [], [], [], [], []
        for npc in line.get("npcs", []):
            entry = npcs[f"{key}.{npc['id']}"]
            flags = 0
            for f in npc.get("flags", ["gossip", "quest"]):
                flags |= {"gossip": 1, "quest": 2, "vendor": 128, "repair": 4096}[f]
            # (a trainer as one of the game's is: its training, and its trainer flags)
            if npc.get("trainer"):
                trainer_of.append((entry, npc["trainer"]))
            hostile = npc.get("hostile", False)
            faction = npc.get("faction", 14 if hostile else 68)
            level = npc.get("level", 20)
            lmin, lmax = (level, level) if isinstance(level, int) else level
            ai = "SmartAI" if npc.get("spells") else ""
            script = ""   # (the town's menus are src/BrillTown.cpp's, for any creature with rows)
            rows.append(f"({entry}, {q(npc['name'])}, {q(npc['subname']) if npc.get('subname') else 'NULL'}, 0, {lmin}, {lmax}, "
                        f"{faction}, {0 if hostile else flags}, 1, 1.14286, {npc.get('unit_class', 1)}, "
                        f"{npc.get('unit_flags', 0)}, {npc.get('type', 6)}, {npc.get('rank', 0)}, {npc.get('health', 1)}, "
                        f"{npc.get('damage', 1)}, {npc.get('gold', 0)}, {npc.get('gold', 0)}, {2 if not hostile else 0}, "
                        f"{q(ai)}, {q(script)})")
            if npc.get("movement"):
                # (creature_template_movement: Ground, Swim, Flight, Rooted, Chase, Random; the game's defaults else)
                m = {"Ground": 1, "Swim": 1, "Flight": 0, "Rooted": 0, "Chase": 0, "Random": 0, **npc["movement"]}
                movement.append(f"({entry}, {m['Ground']}, {m['Swim']}, {m['Flight']}, {m['Rooted']}, {m['Chase']}, {m['Random']}, 0)")
            displays = npc["display"] if isinstance(npc["display"], list) else [npc["display"]]
            for n, d in enumerate(displays):
                models.append(f"({entry}, {n}, {d}, {npc.get('scale', 1)}, 1)")
            for spawn in npc.get("spawns", []):
                m, x, y, z, o = place(key, spawn)
                ph = phase_of(key, npc)
                if ph != 1 and not in_brill(m, x, y):
                    die(key, f"{npc['id']} is in a phase but outside Brill, where no one would see it")
                guid = i.take("cguid", f"{npc['id']}{len(spawns)}")
                spawned(key, npc, "c", guid, m, x, y)
                spawns.append(f"({guid}, {entry}, {m}, {MAP_ZONE.get(m, 0)}, 0, 1, {ph}, {x:.3f}, {y:.3f}, {z:.3f}, {o:.4f}, "
                              f"{npc.get('respawn', 120 if hostile else 60)}, {npc.get('wander', 0)}, {1 if npc.get('wander') else 0}, "
                              f"{q('mod-brill-home town')})")
            for n, (spell, first, every) in enumerate(npc.get("spells", [])):
                smart.append(f"({entry}, 0, {n}, 0, 0, 0, 100, 0, {first[0]}, {first[1]}, {every[0]}, {every[1]}, 0, 0, 11, {spell}, "
                             f"0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, {q(npc['name'] + ' casts ' + str(spell))})")
            if npc.get("vendor"):
                # (an item may be sold only to some: {"item": entry, "cond": ["R:quest"]})
                items = [v if isinstance(v, dict) else {"item": v} for v in npc["vendor"]]
                w("INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES " +
                  ", ".join(f"({entry}, {n}, {v['item']}, 0, 0, 0)" for n, v in enumerate(items)) + ";")
                for v in items:
                    for c in v.get("cond", []):
                        neg = c.startswith("!")
                        body = c[1:] if neg else c
                        if body[:2] not in ("R:", "M:"):
                            die(key, f"a ware's condition must be R: or M: (rewarded), not {c}")
                        conditions.append(f"(23, {entry}, {v['item']}, 0, 0, 8, 0, {ref(key, quests, body[2:], 'quest')}, 0, 0, {1 if neg else 0}, "
                                          f"{q('mod-brill-home town: ' + npc['id'])})")
        for credit in line.get("credits", []):
            entry = npcs[f"{key}.{credit['id']}"]
            rows.append(f"({entry}, {q(credit['name'])}, NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '')")
            models.append(f"({entry}, 0, 11686, 1, 1)")
        if rows:
            w("INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, "
              "`npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, "
              "`mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES")
            w(",\n".join(rows) + ";")
            w("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES")
            w(",\n".join(models) + ";")
        if movement:
            w("INSERT INTO `creature_template_movement` (`CreatureId`, `Ground`, `Swim`, `Flight`, `Rooted`, `Chase`, `Random`, "
              "`InteractionPauseTimer`) VALUES " + ", ".join(movement) + ";")
        if spawns:
            w("INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, "
              "`position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES")
            w(",\n".join(spawns) + ";")
        if smart:
            w("UPDATE `creature_template` SET `AIName` = 'SmartAI' WHERE `entry` IN (" +
              ", ".join(str(npcs[f"{key}.{n['id']}"]) for n in line.get("npcs", []) if n.get("spells")) + ");")
            w("INSERT INTO `smart_scripts` (`entryorguid`, `source_type`, `id`, `link`, `event_type`, `event_phase_mask`, "
              "`event_chance`, `event_flags`, `event_param1`, `event_param2`, `event_param3`, `event_param4`, `event_param5`, "
              "`event_param6`, `action_type`, `action_param1`, `action_param2`, `action_param3`, `action_param4`, `action_param5`, "
              "`action_param6`, `target_type`, `target_param1`, `target_param2`, `target_param3`, `target_param4`, `target_x`, "
              "`target_y`, `target_z`, `target_o`, `comment`) VALUES")
            w(",\n".join(smart) + ";")

        # Objects.
        rows, spawns, uses, goobers = [], [], [], []
        for obj in line.get("objects", []):
            entry = objects[f"{key}.{obj['id']}"]
            # What kind: scenery (5) unless it's used. An object one quest uses is that quest's (a goober,
            # 10, with its quest): it sparkles and can be used only while the quest is in the log, as the
            # game's own quest objects; one used otherwise (several quests, the cellar's way down) stays
            # usable (2). Scenery never says anything (CLAUDE.md: show, don't tell).
            obj_uses = obj.get("use", [])
            quests_of = sorted({u["quest"] for u in obj_uses if u.get("quest")})
            only = quests_of[0] if len(quests_of) == 1 and all(u.get("quest") == quests_of[0] or u.get("marker") for u in obj_uses) else None
            kind = obj.get("type", (10 if only else 2) if obj_uses else 5)
            script = "go_brill_town" if kind in (2, 10) else ""
            data0, data1 = (1, 1) if kind == 7 else (0, ref(key, quests, only, "quest")) if kind == 10 else (0, 0)
            if kind == 10:
                goobers.append(entry)
            # (a quest's own thing in the world, there only while the quest is in a player's log)
            if obj.get("quest_only"):
                if not only:
                    die(key, f"{obj['id']} is \"quest_only\" but isn't one quest's")
                conditions.append(f"(30, 1, {entry}, 0, 0, 9, 0, {ref(key, quests, only, 'quest')}, 0, 0, 0, "
                                  f"{q('mod-brill-home town: ' + obj['id'] + ' while its quest is in the log')})")
            rows.append(f"({entry}, {kind}, {obj['display']}, {q(obj['name'])}, {obj.get('scale', 1)}, {data0}, {data1}, {q(script)})")
            for spawn in obj.get("spawns", []):
                m, x, y, z, o = place(key, spawn)
                ph = phase_of(key, obj)
                if ph != 1 and not in_brill(m, x, y):
                    die(key, f"{obj['id']} is in a phase but outside Brill, where no one would see it")
                guid = i.take("gguid", f"{obj['id']}{len(spawns)}")
                spawned(key, obj, "g", guid, m, x, y)
                spawns.append(f"({guid}, {entry}, {m}, {MAP_ZONE.get(m, 0)}, 0, 1, {ph}, {x:.3f}, {y:.3f}, {z:.3f}, {o:.4f}, "
                              f"0, 0, {math.sin(o / 2):.6f}, {math.cos(o / 2):.6f}, 0, 255, 1, {q('mod-brill-home town')})")
            for n, use in enumerate(obj.get("use", [])):
                tid = text(f"use:{obj['id']}:{n}", use["text"]) if use.get("text") else 0
                quest = ref(key, quests, use["quest"], "quest") if use.get("quest") else 0
                credit = ref(key, npcs, use["credit"], "credit") if use.get("credit") else 0
                marker = ref(key, quests, use["marker"], "marker") if use.get("marker") else 0
                tele = place(key, use["teleport"]) if use.get("teleport") else (-1, 0, 0, 0, 0)
                uses.append(f"({entry}, {n}, {q(cond(key, use.get('cond')))}, {quest}, {credit}, {tid}, {marker}, "
                            f"{tele[0]}, {tele[1]:.3f}, {tele[2]:.3f}, {tele[3]:.3f}, {tele[4]:.4f})")
        if rows:
            w("INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES")
            w(",\n".join(rows) + ";")
            # (a building: drawn as the game's own buildings out in the world are, never damaged: the house's kind)
            # (a quest's object: used only when the game says so, as its quest's; GO_FLAG_INTERACT_COND)
            buildings = [objects[f"{key}.{o['id']}"] for o in line.get("objects", []) if o.get("type") == 33]
            if buildings or goobers:
                w("INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES " +
                  ", ".join([f"({e}, 0, 32)" for e in buildings] + [f"({e}, 0, 4)" for e in goobers]) + ";")
        if spawns:
            w("INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, "
              "`position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, "
              "`state`, `Comment`) VALUES")
            w(",\n".join(spawns) + ";")
        if uses:
            w("INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, "
              "`tele_y`, `tele_z`, `tele_o`) VALUES")
            w(",\n".join(uses) + ";")

        # What creatures say, and the options the module adds to their menus.
        rows = []
        for n, g in enumerate(line.get("gossip", [])):
            npc = ref(key, npcs, g["npc"], "creature")
            if g["kind"] == "greet":
                tid = text(f"greet:{n}", g.get("text"), g.get("texts"))
                rows.append((npc, f"'greet', {q(cond(key, g.get('cond')))}, 0, NULL, {tid}, '', 0, 0, 0, 0, NULL, 0"))
            else:
                action = g["action"]
                if action not in ("credit", "choice", "say", "vendor", "upgrades", "furnish", "buy"):
                    die(key, f"an option's action I don't know: {action}")
                quest = ref(key, quests, g["quest"], "quest") if g.get("quest") else 0
                credit = ref(key, npcs, g["credit"], "credit") if g.get("credit") else 0
                marker = ref(key, quests, g["marker"], "marker") if g.get("marker") else 0
                if action == "buy" and not (g.get("marker") and g.get("arg")):
                    die(key, "a purchase (\"buy\") needs its price (\"arg\", copper) and a marker")
                icon = {"vendor": 1, "upgrades": 1, "buy": 1}.get(action, 0)
                rows.append((npc, f"'option', {q(cond(key, g.get('cond')))}, {icon}, {q(g['text'])}, 0, {q(action)}, {quest}, {credit}, "
                                  f"{marker}, {g.get('emote', 0)}, {q(g['reply']) if g.get('reply') else 'NULL'}, {g.get('arg', 0)}"))
        if rows:
            w("INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, "
              "`marker`, `emote`, `reply`, `arg`) VALUES")
            # (an order across lines: the line's place, then its row)
            w(",\n".join(f"({npc}, {LINES.index(key) * 1000 + n}, {rest})" for n, (npc, rest) in enumerate(rows)) + ";")
            # (a creature of the game's own given options: it has a menu to show them in)
            own = sorted({npc for npc, _ in rows if npc < 970000})
            if own:
                w("UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (" + ", ".join(map(str, own)) + ");")

        # The phases (a bit each, its conditions: any row's all).
        rows = []
        for name, alternatives in line.get("phases", {}).items():
            bit = phases[f"{key}.{name}"]
            for n, alt in enumerate(alternatives):
                rows.append(f"({bit}, {n}, {q(cond(key, alt))})")
        # (a stage's "until" phase: there while the stage isn't reached: any of its conditions not holding)
        for name, bit in phases.items():
            if name.startswith(f"{key}.__until"):
                k = int(name.split("__until")[1])
                for n, c in enumerate(line["stages"][k - 1]):
                    rows.append(f"({bit}, {n}, {q(cond(key, [c[1:] if c.startswith('!') else '!' + c]))})")
        if rows:
            w("INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES")
            w(",\n".join(rows) + ";")
        # Its stages (a project's: how far it's come for a player).
        if line.get("stages"):
            w("INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES")
            w(",\n".join(f"({stage_type[key]}, {k + 1}, 0, {q(cond(key, c))})" for k, c in enumerate(line["stages"])) + ";")

        # Quests.
        rows, addons, offers, requests, starters, enders = [], [], [], [], [], []
        for quest in line.get("quests", []):
            qid = quests[f"{key}.{quest['id']}"]
            objs = quest.get("objectives", [])
            if len(objs) > 4:
                die(key, f"{quest['id']} has more than four objectives")
            cols = []
            for n in range(4):
                if n < len(objs):
                    kind, what, count, label = objs[n]
                    target = ref(key, npcs, what, "creature") if kind != "kill" or isinstance(what, str) else what
                    cols.append(f"{target}, {count}, {q(label)}")
                else:
                    cols.append("0, 0, ''")
            items = quest.get("items", []) + [(0, 0)] * (4 - len(quest.get("items", [])))
            sort = quest.get("sort", 159)
            repeat = quest.get("repeat")
            if repeat not in (None, "daily", "weekly", "repeatable"):
                die(key, f"{quest['id']}: \"repeat\" is daily, weekly or repeatable")
            flags = (quest.get("flags", 0) | (0x10000 if quest.get("auto_complete") else 0)
                     | {"daily": 0x1000, "weekly": 0x8000}.get(repeat, 0))
            rows.append(f"({qid}, 2, -1, {quest.get('min_level', 5)}, {sort}, {flags}, {quest.get('xp', 3)}, {quest.get('money', 2500)}, 0, "
                        f"{q(quest['title'])}, {q(quest['log'])}, {q(quest['offer'])}, '', {q(quest.get('return', 'Return to ' + quest.get('ender_name', 'the quest giver') + '.'))}, "
                        + ", ".join(cols) + ", " + ", ".join(f"{a}, {b}" for a, b in items) + ")")
            prev = ref(key, quests, quest["prev"], "quest") if quest.get("prev") else 0
            addons.append(f"({qid}, {prev}, {1 if repeat else 0})")
            # (taken only once others are done: any n of some, or all of them)
            avail = quest.get("available")
            if avail:
                import itertools
                if "all" in avail:
                    groups = [avail["all"]]
                else:
                    groups = list(itertools.combinations(avail["of"], avail["any"]))
                for g, group in enumerate(groups):
                    for other in group:
                        conditions.append(f"(19, 0, {qid}, 0, {g}, 8, 0, {ref(key, quests, other, 'quest')}, 0, 0, 0, "
                                          f"{q('mod-brill-home town: ' + quest['id'])})")
            offers.append(f"({qid}, {quest.get('done_emote', 1)}, {q(quest['done'])})")
            if quest.get("progress"):
                requests.append(f"({qid}, 1, 1, {q(quest['progress'])})")
            giver = ref(key, npcs, quest["giver"], "creature")
            ender = ref(key, npcs, quest.get("ender", quest["giver"]), "creature")
            starters.append(f"({giver}, {qid})")
            enders.append(f"({ender}, {qid})")
        for marker in line.get("markers", []):
            # (a choice's mark: never given or seen, only set as rewarded: src/BrillTown.cpp)
            qid = quests[f"{key}.{marker}"]
            rows.append(f"({qid}, 2, 1, 1, -1, 0, 0, 0, 0, {q('[' + marker + ']')}, '', '', '', '', "
                        + ", ".join(["0, 0, ''"] * 4) + ", " + ", ".join(["0, 0"] * 4) + ")")
        if rows:
            w("INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, "
              "`RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, "
              "`RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, "
              "`RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, "
              "`RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES")
            w(",\n".join(rows) + ";")
        if addons:
            w("INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES " + ", ".join(addons) + ";")
            w("INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES\n" + ",\n".join(offers) + ";")
            if requests:
                w("INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES\n"
                  + ",\n".join(requests) + ";")
            w("INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES " + ", ".join(starters) + ";")
            w("INSERT INTO `creature_questender` (`id`, `quest`) VALUES " + ", ".join(enders) + ";")
            own = sorted({int(s.split(",")[0][1:]) for s in starters + enders if int(s.split(",")[0][1:]) < 970000})
            if own:
                w("UPDATE `creature_template` SET `npcflag` = `npcflag` | 3 WHERE `entry` IN (" + ", ".join(map(str, own)) + ");")
        w("")

    if trainer_of:
        w("-- Trainers: the training and the trainer flags of a creature of the game's own.")
        for entry, source in trainer_of:
            w(f"INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) SELECT {entry}, `TrainerId` FROM `creature_default_trainer` "
              f"WHERE `CreatureId` = {source};")
            w(f"UPDATE `creature_template` SET `npcflag` = `npcflag` | ((SELECT `npcflag` FROM (SELECT `npcflag` FROM `creature_template` "
              f"WHERE `entry` = {source}) AS t) & 112) WHERE `entry` = {entry};")
    if invis:
        w("-- The projects' spawns that show from a stage.")
        w("INSERT INTO `brill_town_invis` (`kind`, `guid`, `type`, `value`) VALUES\n" + ",\n".join(invis) + ";")
    for kind, table in (("c", "game_event_creature"), ("g", "game_event_gameobject")):
        rows = [f"({e}, {guid})" for k, e, guid in events if k == kind]
        if rows:
            w(f"INSERT INTO `{table}` (`eventEntry`, `guid`) VALUES " + ", ".join(rows) + ";")
    if conditions:
        w("INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, "
          "`ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, "
          "`Comment`) VALUES\n" + ",\n".join(conditions) + ";")
    if texts:
        w("-- The words.")
        for tid in sorted(texts):
            w(texts[tid])
    used = sum(1 for _ in phases)
    w(f"-- ({used} of the town's {len(FREE_PHASES)} phases used)")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"{OUT}: {len(lines)} questlines, {sum(len(l.get('quests', [])) for _, l in lines)} quests, {used} phases")


if __name__ == "__main__":
    main()
    # (the quests on the maps, the game's and Questie's: made from this SQL and the other's)
    import build_questie
    build_questie.main()
