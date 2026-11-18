#!/usr/bin/env python3
"""Applies the allied races module's change files (the .txt files build_data.py writes: put, putraw, appendraw, copyrow,
remapfield, or, set, and Wrath++'s own drop and map) to the game's own tables (WDBC), as mod-skyborne's SkyborneFiles.cpp ApplyChanges does as a realm
starts: Wrath++ makes its tables here, at packaging, so its app only installs them.

Wrath++'s own two (the app's DbcChanges.kt does the same):
    drop  FIELD VALUE [FIELD VALUE...]              the rows whose fields are those values are taken out
    map   WHERE FROM TO DEFAULT [KEY=VALUE...]      a rule over whatever rows the table has: in every row that WHERE holds for
          ("-": every row; else FIELD=VALUE[,FIELD=VALUE...], all of them), field TO becomes the VALUE listed for the row's
          values of the fields FROM (FIELD[,FIELD...]; KEY: their values, comma separated, as the row has them when the line
          is reached), or DEFAULT for a key that isn't listed ("-": such a row is left as it is). Every row is looked up
          once: 1=2 2=3 makes a 1 a 2, not a 3.

    python3 tools/apply_client.py STOCK_DBC_DIR CHANGES_DIR OUT_DIR     (a table without changes is copied as it is
                                                                         only if it has a file: the changed ones are written)
"""
import os
import struct
import sys


class Table:
    def __init__(self, data):
        magic, count, self.fields, self.size, text = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC":
            raise ValueError("not a WDBC table")
        self.records = [data[20 + i * self.size:20 + (i + 1) * self.size] for i in range(count)]
        self.text = bytearray(data[20 + count * self.size:20 + count * self.size + text])
        self.strings = {}
        at = 0
        while at < len(self.text):
            end = self.text.index(b"\0", at)
            self.strings.setdefault(bytes(self.text[at:end]), at)
            at = end + 1
        if not self.text:
            self.text = bytearray(b"\0")
            self.strings[b""] = 0

    def string(self, value):
        raw = value.encode("utf-8")
        if raw not in self.strings:
            self.strings[raw] = len(self.text)
            self.text += raw + b"\0"
        return self.strings[raw]

    def write(self):
        return (struct.pack("<4s4I", b"WDBC", len(self.records), self.fields, self.size, len(self.text))
                + b"".join(self.records) + bytes(self.text))

    def get(self, row, field):
        return struct.unpack_from("<I", self.records[row], field * 4)[0]

    def set(self, row, field, value):
        r = bytearray(self.records[row])
        struct.pack_into("<I", r, field * 4, value & 0xFFFFFFFF)
        self.records[row] = bytes(r)


def unescape(text):
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            out.append({"t": "\t", "n": "\n", "\\": "\\"}.get(text[i + 1], text[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def sort_char_sections(table):
    """CharSections in the order the client's component code needs (BuildComponentArray reads a table in runs of one race, sex,
    section and variation: a group split over several runs is sized by its last run, and an earlier run's higher variation writes
    past the array): a stable sort on those four, the order within a group kept. The same sort the app makes at every Play
    (WrathppSections), done here so the server's tables, the rig's and CI's checks read the table as the game will."""
    import struct as _s
    keyed = sorted(range(len(table.records)),
                   key=lambda i: (_s.unpack_from("<I", table.records[i], 4)[0], _s.unpack_from("<I", table.records[i], 8)[0],
                                  _s.unpack_from("<I", table.records[i], 12)[0], _s.unpack_from("<I", table.records[i], 32)[0], i))
    table.records = [table.records[i] for i in keyed]


def apply(table, changes):
    """The changes (a file's text) applied to [table]; raises ValueError with the line on anything it can't do."""
    has_ids = table.size >= 4
    by_id = {}
    if has_ids:
        for i in range(len(table.records)):
            by_id.setdefault(table.get(i, 0), i)
    whole = set(table.records)
    types = ""

    def place(record):
        if has_ids:
            rid = struct.unpack_from("<I", record)[0]
            if rid in by_id:
                table.records[by_id[rid]] = record
                return
            by_id[rid] = len(table.records)
        table.records.append(record)

    for number, line in enumerate(changes.split("\n"), 1):
        line = line.rstrip("\r")
        if not line or line[0] == "#":
            continue
        f = line.split("\t")
        op = f[0]
        where = " (line %d)" % number
        try:
            if op == "types":
                types = f[1] if len(f) > 1 else ""
                if len(types) != table.fields or table.size != table.fields * 4:
                    raise ValueError("the table isn't the one these changes are for: %d fields, %d expected" % (table.fields, len(types)))
            elif op == "put":
                if not types or len(f) != len(types) + 1:
                    raise ValueError("a row of the wrong size" + where)
                record = bytearray(table.size)
                for i, kind in enumerate(types):
                    v = f[i + 1]
                    if kind == "s":
                        value = table.string(unescape(v))
                    elif kind == "f":
                        value = struct.unpack("<I", struct.pack("<f", float(v)))[0]
                    else:
                        value = int(v) & 0xFFFFFFFF
                    struct.pack_into("<I", record, i * 4, value)
                place(bytes(record))
            elif op in ("putraw", "appendraw"):
                record = bytes.fromhex(f[1]) if len(f) == 2 else b""
                if len(record) != table.size:
                    raise ValueError("a record of the wrong size" + where)
                if op == "putraw":
                    place(record)
                elif record not in whole:
                    whole.add(record)
                    table.records.append(record)
            elif op == "copyrow":
                src, dst = int(f[1]), int(f[2])
                if not has_ids:
                    raise ValueError("a row copy the table can't take" + where)
                if src in by_id and dst not in by_id:
                    r = bytearray(table.records[by_id[src]])
                    struct.pack_into("<I", r, 0, dst)
                    place(bytes(r))
            elif op == "remapfield":
                field, old, new = int(f[1]), int(f[2]), int(f[3])
                if field >= table.size // 4:
                    raise ValueError("no such field" + where)
                for row in range(len(table.records)):
                    if table.get(row, field) == old:
                        table.set(row, field, new)
                whole = set(table.records)
                if field == 0 and has_ids:
                    by_id = {}
                    for row in range(len(table.records)):
                        by_id.setdefault(table.get(row, 0), row)
            elif op == "drop":
                # Wrath++'s own (not the realm module's): the rows whose fields are those values (field, value, field, value...)
                pairs = [(int(f[i]), int(f[i + 1])) for i in range(1, len(f) - 1, 2)]
                if not pairs or len(f) % 2 == 0:
                    raise ValueError("a row drop of the wrong size" + where)
                table.records = [r for i, r in enumerate(table.records) if not all(table.get(i, a) == b for a, b in pairs)]
                whole = set(table.records)
                by_id = {}
                if has_ids:
                    for row in range(len(table.records)):
                        by_id.setdefault(table.get(row, 0), row)
            elif op == "map":
                # Wrath++'s own: a field looked up from other fields' values, in the rows a condition chooses
                if len(f) < 5:
                    raise ValueError("a map of the wrong size" + where)
                count = table.size // 4
                conds = [] if f[1] == "-" else [tuple(int(x) for x in c.split("=")) for c in f[1].split(",")]
                src = [int(x) for x in f[2].split(",")]
                dst = int(f[3])
                default = None if f[4] == "-" else int(f[4]) & 0xFFFFFFFF
                if any(len(c) != 2 for c in conds):
                    raise ValueError("a map's condition that isn't FIELD=VALUE" + where)
                if any(not 0 <= x < count for x in [c[0] for c in conds] + src + [dst]):
                    raise ValueError("no such field" + where)
                lookup = {}
                for pair in f[5:]:
                    key, _, value = pair.partition("=")
                    key = tuple(int(x) & 0xFFFFFFFF for x in key.split(","))
                    if len(key) != len(src):
                        raise ValueError("a map's key of the wrong size" + where)
                    lookup[key] = int(value) & 0xFFFFFFFF
                for row in range(len(table.records)):
                    if all(table.get(row, a) == b & 0xFFFFFFFF for a, b in conds):
                        value = lookup.get(tuple(table.get(row, x) for x in src), default)
                        if value is not None:
                            table.set(row, dst, value)
                whole = set(table.records)
                if dst == 0 and has_ids:
                    by_id = {}
                    for row in range(len(table.records)):
                        by_id.setdefault(table.get(row, 0), row)
            elif op in ("or", "set"):
                rid, field, value = int(f[1]), int(f[2]), int(f[3])
                if not has_ids or field >= table.size // 4:
                    raise ValueError("a field change the table can't take" + where)
                if rid in by_id:
                    row = by_id[rid]
                    table.set(row, field, (table.get(row, field) | value) if op == "or" else value)
            else:
                raise ValueError('unknown change "%s"%s' % (op, where))
        except (IndexError, ValueError) as e:
            raise ValueError(str(e) if "line" in str(e) else "%s%s" % (e, where))
    return table


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    stock, changes, out = argv[1:]
    os.makedirs(out, exist_ok=True)
    for name in sorted(os.listdir(changes)):
        if not name.endswith(".txt"):
            continue
        table_name = name[:-4]
        with open(os.path.join(stock, table_name + ".dbc"), "rb") as f:
            table = Table(f.read())
        with open(os.path.join(changes, name), encoding="utf-8") as f:
            apply(table, f.read())
        with open(os.path.join(out, table_name + ".dbc"), "wb") as f:
            f.write(table.write())
        print("%s: %d rows" % (table_name, len(table.records)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
