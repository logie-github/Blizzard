"""Wowhead's Forever tooltips (nether.wowhead.com/forever/tooltip/<npc|item>/<id>, the JSON its tooltip
script reads): what a new NPC is (level, type, family, rank) and what a new reward item is (stats,
damage, armor, effects), cached as <kind>-<id>.json."""
import html
import json
import os
import re
import time
import urllib.request

URL = "https://nether.wowhead.com/forever/tooltip/%s/%d"
USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"

TYPES = {"Beast": 1, "Dragonkin": 2, "Demon": 3, "Elemental": 4, "Giant": 5, "Undead": 6, "Humanoid": 7,
         "Critter": 8, "Mechanical": 9, "Not specified": 10, "Totem": 11}
RANKS = {"Elite": 1, "Rare Elite": 2, "Boss": 3, "Rare": 4}
# Equip lines' ratings (<!--rtgN-->) as 3.3.5's item stats: Forever's spell damage and healing is
# 3.3.5's spell power; the others are the same numbers in both.
RATINGS = {41: 45, 42: 45, 45: 45, 38: 38, 39: 39, 43: 43, 12: 12, 13: 13, 14: 14, 15: 15, 31: 31, 32: 32, 35: 35, 36: 36, 37: 37, 44: 44, 47: 47, 48: 48}
RESISTANCES = {"Holy": "holy_res", "Fire": "fire_res", "Nature": "nature_res", "Frost": "frost_res",
               "Shadow": "shadow_res", "Arcane": "arcane_res"}


def fetch(kind, ids, cache):
    os.makedirs(cache, exist_ok=True)
    for i in ids:
        path = os.path.join(cache, "%s-%d.json" % (kind, i))
        if os.path.exists(path) and os.path.getsize(path):
            continue
        with urllib.request.urlopen(urllib.request.Request(URL % (kind, i), headers={"User-Agent": USER_AGENT}), timeout=60) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
        time.sleep(0.3)


def load(kind, i, cache):
    path = os.path.join(cache, "%s-%d.json" % (kind, i))
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    return data if data.get("tooltip") else None


def lines(tooltip):
    text = re.sub(r"<br\s*/?>|</tr>|</td>|</th>", "\n", tooltip)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    return [line.strip() for line in text.split("\n") if line.strip()]


def npc(data):
    """Level, type, family and rank from an NPC's tooltip."""
    out = {"type": 0, "family": "", "rank": 0, "level": None}
    rows = lines(data["tooltip"])
    for n, line in enumerate(rows):
        m = re.match(r"Level (\?\?|\d+)(?:\s*-\s*(\d+))?\s*(.*?)(?:\s*\(([^)]+)\))?$", line)
        if not m:
            continue
        if m.group(1) != "??":
            out["level"] = [int(m.group(1)), int(m.group(2) or m.group(1))]
        kind = m.group(3).strip()
        out["type"] = TYPES.get(kind, 0)
        out["rank"] = RANKS.get(m.group(4) or "", 0)
        if m.group(1) == "??" and not out["rank"]:
            out["rank"] = 3
        if n + 1 < len(rows) and not rows[n + 1].startswith(("Level", "<")):
            out["family"] = rows[n + 1]
        break
    return out


def item(data):
    """A reward item's own numbers from its tooltip."""
    t = data["tooltip"]
    out = {"name": data["name"], "quality": data.get("quality", 1), "icon": data.get("icon", ""), "stats": [], "use": [], "dropped": []}
    m = re.search(r"<!--ilvl-->(\d+)", t)
    out["item_level"] = int(m.group(1)) if m else 0
    m = re.search(r"<!--rlvl-->(\d+)", t)
    out["required_level"] = int(m.group(1)) if m else 0
    out["bonding"] = 1 if "Binds when picked up" in t else 2 if "Binds when equipped" in t else 3 if "Binds when used" in t else 0
    m = re.search(r"<!--scstart(\d+):(\d+)-->", t)
    out["class"], out["subclass"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    m = re.search(r"<!--dmg-->([\d.]+)\s*-\s*([\d.]+)\s*(\w+)?\s*Damage", t)
    if m:
        out["dmg"] = [float(m.group(1)), float(m.group(2))]
        out["dmg_school"] = {"Holy": 1, "Fire": 2, "Nature": 3, "Frost": 4, "Shadow": 5, "Arcane": 6}.get(m.group(3) or "", 0)
    m = re.search(r"<!--spd-->([\d.]+)", t)
    out["speed"] = float(m.group(1)) if m else 0
    m = re.search(r"(?:<!--amr-->)?(\d+) Armor", t)
    out["armor"] = int(m.group(1)) if m else 0
    for stat, value in re.findall(r"<!--stat(\d+)-->([+-]?\d+)", t):
        out["stats"].append([int(stat), int(value)])
    for value, school in re.findall(r"([+-]\d+) (Holy|Fire|Nature|Frost|Shadow|Arcane) Resistance", t):
        out[RESISTANCES[school]] = int(value)
    for rating, value in re.findall(r"<!--rtg(\d+)-->(\d+)", t):
        if int(rating) in RATINGS:
            out["stats"].append([RATINGS[int(rating)], int(value)])
        else:
            out["dropped"].append("rating %s" % rating)
    out["dropped"] += [html.unescape(re.sub(r"<[^>]+>", "", e)) for e in re.findall(r"Equip: ((?:(?!<!--rtg).)*?)</span>", t)
                       if "<!--rtg" not in e]
    out["use"] = [int(s) for s in re.findall(r"<!--useEffect:\d+:\d+--><a href=\"/forever/spell=(\d+)", t)]
    m = re.search(r"Durability (\d+) / \d+", t)
    out["durability"] = int(m.group(1)) if m else 0
    m = re.search(r"(\d+) Slot (?:\w+ )?Bag", t)
    out["bag_slots"] = int(m.group(1)) if m else 0
    gold = re.search(r'class="moneygold">(\d+)', t)
    silver = re.search(r'class="moneysilver">(\d+)', t)
    copper = re.search(r'class="moneycopper">(\d+)', t)
    out["sell"] = sum(int(m.group(1)) * k for m, k in ((gold, 10000), (silver, 100), (copper, 1)) if m)
    m = re.search(r"Max Stack: (\d+)", t)
    out["stack"] = int(m.group(1)) if m else 1
    m = re.search(r"<td>([A-Z][\w -]+)</td><th>", t)
    out["slot"] = m.group(1) if m else ""
    return out
