"""Stage `tables`: a unit's rows of the game's tables, in 3.3.5a's layouts, in the format of mod-skyborne's client table files
(`types<TAB>...` then `put<TAB>id<TAB>...`, as mod-worgen-goblin/data/zones/client/dbc/*.txt).

Generic: for each field of the 3.3.5a table (named by WoWDBDefs through the zones' `common.layout`), take the Cataclysm column of
the same name (a localized string's `_lang` column; arrays `name_0`...), 0 or empty where there is none. Columns of 3.3.5a with no
Cataclysm source, and Cataclysm columns nothing took, are returned for the report: nothing is silently zero.
Built: Map and AreaTable (ids, parents, explore bits through ids.json). Not built yet (listed in docs/wrathpp/CATA_BACKPORT.md):
Light*, WMOAreaTable, WorldMapArea/Overlay, LoadingScreens, ZoneMusic, SoundEntries, the displays; the server's `*_dbc` SQL twin.
"""
import os

from . import util, zones_adapter

# 3.3.5a's area flags that mean other things in Cataclysm (expansion-only flying, Wintergrasp, ...): dropped as the zones' build does
# (build_tables.AREA_FLAGS_DROPPED).
AREA_FLAGS_DROPPED = 0x400 | 0x2000 | 0x4000 | 0x20000 | 0x01000000 | 0x10000000 | 0x20000000 | 0x40000000 | 0x80000000


def layout(dbd_dir, name):
    return zones_adapter.load("common").layout(dbd_dir, name)


def csv_column(field):
    """The CSV column a 3.3.5a field is named by in Cataclysm's tables; None for the filler a localized string has."""
    if "#" in field:
        return None
    return field


def convert_row(fields, row, used):
    """One CSV row as 3.3.5a's field values, in order. `used` collects the CSV columns taken; a field without a source is
    returned in the second list."""
    values, lacking = [], []
    for name, kind in fields:
        if "#" in name:
            values.append(0 if name.endswith("#flags") else "")
            continue
        col = name if name in row else (name + "_lang" if name + "_lang" in row else None)
        if col is None:
            lacking.append(name)
            values.append("" if kind == "s" else 0)
            continue
        used.add(col)
        raw = row[col]
        if kind == "s":
            values.append((raw or "").replace("\t", " ").replace("\n", " "))
        elif kind == "f":
            try:
                values.append(float(raw))
            except (TypeError, ValueError):
                values.append(0.0)
        else:
            try:
                values.append(int(float(raw))) if raw not in ("", None) else values.append(0)
            except ValueError:
                values.append(0)
    return values, lacking


def render(fields, rows):
    """The text file: types line and one `put` per row (the first field is the id)."""
    types = "".join(k for _, k in fields)
    out = [f"types\t{types}"]
    for values in rows:
        out.append("put\t" + "\t".join(repr(v) if isinstance(v, float) else str(v) for v in values))
    return "\n".join(out) + "\n"


def map_table(dbd_dir, csv_rows, manifest, plan_ids):
    """Rows of the manifest's maps (the unit's), the Map table. Returns (text, report dict)."""
    fields = layout(dbd_dir, "Map")
    ids = (plan_ids or {}).get("maps", {})
    rows, rep = [], {"lacking": set(), "unused": set()}
    by_id = {int(r["ID"]): r for r in csv_rows}
    used = set()
    names = [n for n, _ in fields]
    for m in manifest:
        r = by_id.get(m["id"])
        if r is None:
            continue
        values, lacking = convert_row(fields, r, used)
        rep["lacking"].update(lacking)
        values[names.index("ID")] = m["new_id"]
        values[names.index("Directory")] = m["new_dir"]
        for ref in ("ParentMapID", "CorpseMapID", "CosmeticParentMapID"):
            if ref in names:
                v = values[names.index(ref)]
                values[names.index(ref)] = ids.get(str(v), 0) if v else 0   # (a map not in the expansion's plan: none)
        rows.append(values)
    rep["unused"] = set(csv_rows[0]) - used if csv_rows else set()
    rep["lacking"], rep["unused"] = sorted(rep["lacking"]), sorted(rep["unused"])
    return render(fields, rows), rep


def area_table(dbd_dir, csv_rows, unit_map_ids, plan):
    """Rows of the areas on the unit's maps, ids, parents, maps and explore bits through the whole expansion's id plan."""
    fields = layout(dbd_dir, "AreaTable")
    names = [n for n, _ in fields]
    areas, mapids, bits = plan["areas"], plan["maps"], plan["explore_bits"]
    rows, lacking, used = [], set(), set()
    for r in csv_rows:
        if int(float(r.get("ContinentID") or -1)) not in unit_map_ids:
            continue
        values, lk = convert_row(fields, r, used)
        lacking.update(lk)
        aid = str(values[names.index("ID")])
        values[names.index("ID")] = areas.get(aid, int(aid))
        for ref in ("ParentAreaID",):
            if ref in names and values[names.index(ref)]:
                values[names.index(ref)] = areas.get(str(values[names.index(ref)]), values[names.index(ref)])
        if "ContinentID" in names:
            v = values[names.index("ContinentID")]
            values[names.index("ContinentID")] = mapids.get(str(v), v)
        for bit in ("AreaBit", "ExploreFlag"):
            if bit in names:
                values[names.index(bit)] = bits.get(aid, 0)
        for flags in ("Flags", "Flags_0"):
            if flags in names:
                values[names.index(flags)] &= ~AREA_FLAGS_DROPPED & 0xFFFFFFFF
        rows.append(values)
    rep = {"lacking": sorted(lacking), "unused": sorted((set(csv_rows[0]) - used) if csv_rows else []),
           "no_explore_bit": [a for a in plan.get("no_explore_bit", [])]}
    return render(fields, rows), rep


def run(source, unit_maps, plan_ids, dbd_dir, out_dir):
    """Writes Map.txt and AreaTable.txt for a unit; returns the report."""
    from .inventory import rows as csv_rows
    maps_csv = csv_rows(source.table("Map"))
    text, r1 = map_table(dbd_dir, maps_csv, unit_maps, plan_ids)
    util.write_atomic(os.path.join(out_dir, "client", "dbc", "Map.txt"), text)
    area_csv = csv_rows(source.table("AreaTable"))
    text, r2 = area_table(dbd_dir, area_csv, {m["id"] for m in unit_maps}, plan_ids)
    util.write_atomic(os.path.join(out_dir, "client", "dbc", "AreaTable.txt"), text)
    return {"Map": r1, "AreaTable": r2}
