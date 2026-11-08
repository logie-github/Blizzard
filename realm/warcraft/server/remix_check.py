#!/usr/bin/env python3
"""Checks Wrath Remix: where its NPCs stand, and the patch it writes for the game.

    remix_check.py floors HOST USER PASSWORD CHARACTER SPAWNS
    remix_check.py patch PATCH DBC

SPAWNS is a tab-separated list of the Remix spawns (guid, map, x, y, z, comment), as
`SELECT guid, map, position_x, position_y, position_z, Comment FROM creature WHERE ...` prints
it. The character goes to each one and asks the realm what floor is there (.gps): an NPC more
than 2.5 yards above or below the floor under it is floating or buried. Prints every spawn's
floor and fails if any is off. WORLD_PORT names the realm's port, as for auth_check.py.

PATCH is the archive the Remix world server writes into the game's Data folder (patch-Y.MPQ), DBC
the server's DBC folder. The archive is read here as the game reads an MPQ (its own reading of
the format, not the module's writing of it), and its three DBC files are checked against the
server's: every row of the server's still there as it was, and Bronze's rows added (the item, the
currency, a price for every step of the ladder).
"""
import re
import struct
import sys
import zlib

import auth_check

TOLERANCE = 2.5
GPS = re.compile(r"Zone: (\d+).*?GroundZ: (-?[\d.]+) FloorZ: (-?[\d.]+)", re.S)


def floors(host, user, password, character, spawns_file):
    spawns = []
    with open(spawns_file) as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 5:
                spawns.append((fields[0], int(fields[1]), float(fields[2]), float(fields[3]), float(fields[4]),
                               fields[5] if len(fields) > 5 else ""))
    def check(spawns, again):
        steps = []
        for _, map_id, x, y, z, _ in spawns:
            steps += [f"go {map_id} {x:.2f} {y:.2f} {z + 0.5:.2f}", "cmd .gps"]
        transcript = auth_check.world(host, user, password, character, steps=steps)
        gps = [heard for line, heard in transcript if line == "cmd .gps"]
        off_the_floor = []
        for spawn, heard in zip(spawns, gps):
            guid, map_id, x, y, z, comment = spawn
            match = GPS.search("\n".join(heard))
            if not match:
                print(f"floor: {guid} ({comment}): no answer to .gps")
                off_the_floor.append(spawn)
                continue
            zone, ground, floor = int(match.group(1)), float(match.group(2)), float(match.group(3))
            off = z - floor
            ok = abs(off) <= TOLERANCE
            if not ok:
                off_the_floor.append(spawn)
            print(f"floor: {guid} map {map_id} zone {zone} z {z:.1f} floor {floor:.1f} ground {ground:.1f}"
                  f" {'ok' if ok else ('FLOATING' if off > 0 else 'BURIED')} ({comment}){' (again)' if again else ''}")
        off_the_floor += spawns[len(gps):]
        return off_the_floor

    # (one off the floor is looked at again, once: a reading taken as the character lands can be
    # the place it came from's)
    off_the_floor = check(spawns, False)
    if off_the_floor:
        off_the_floor = check(off_the_floor, True)
    return len(off_the_floor)


def _crypt_table():
    table, seed = [0] * 0x500, 0x00100001
    for i in range(0x100):
        index = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            high = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            table[index] = high | (seed & 0xFFFF)
            index += 0x100
    return table


CRYPT = _crypt_table()


def mpq_hash(name, kind):
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in name.upper().replace("/", "\\").encode():
        seed1 = (CRYPT[kind * 0x100 + ch] ^ (seed1 + seed2)) & 0xFFFFFFFF
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1


def mpq_decrypt(words, key):
    seed, out = 0xEEEEEEEE, []
    for value in words:
        seed = (seed + CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        plain = value ^ ((key + seed) & 0xFFFFFFFF)
        key = (((~key << 0x15) + 0x11111111) & 0xFFFFFFFF) | (key >> 0x0B)
        seed = (plain + seed + (seed << 5) + 3) & 0xFFFFFFFF
        out.append(plain)
    return out


def mpq_files(path):
    """name -> contents of an MPQ (format 0) whose files are stored uncompressed."""
    data = open(path, "rb").read()
    magic, header, size, version, shift, hash_pos, block_pos, hash_count, block_count = struct.unpack_from("<4sIIHHIIII", data, 0)
    assert magic == b"MPQ\x1a" and header == 32 and version == 0 and size == len(data), "not an MPQ of the first format"
    hashes = mpq_decrypt(struct.unpack_from(f"<{hash_count * 4}I", data, hash_pos), mpq_hash("(hash table)", 3))
    blocks = mpq_decrypt(struct.unpack_from(f"<{block_count * 4}I", data, block_pos), mpq_hash("(block table)", 3))

    def read(name):
        index = mpq_hash(name, 0) & (hash_count - 1)
        for _ in range(hash_count):
            a, b, locale, block = hashes[index * 4:index * 4 + 4]
            if block == 0xFFFFFFFF:
                return None
            if a == mpq_hash(name, 1) and b == mpq_hash(name, 2):
                pos, stored, length, flags = blocks[block * 4:block * 4 + 4]
                if flags == 0x80000000:
                    return data[pos:pos + length]
                # Compressed (not encrypted, not a single unit): the sectors' offsets, then each
                # sector, zlib (a byte saying so first) unless storing it whole was smaller.
                assert flags == 0x80000200, f"{name}: stored in a way this doesn't read ({flags:#x})"
                sector = 512 << shift
                count = (length + sector - 1) // sector or 1
                offsets = struct.unpack_from(f"<{count + 1}I", data, pos)
                out = b""
                for n in range(count):
                    chunk = data[pos + offsets[n]:pos + offsets[n + 1]]
                    want = min(sector, length - n * sector)
                    if len(chunk) < want:
                        assert chunk[0] == 0x02, f"{name}: a sector compressed other than with zlib"
                        chunk = zlib.decompress(chunk[1:])
                    out += chunk
                assert len(out) == length, f"{name}: {len(out)} bytes, not {length}"
                return out
            index = (index + 1) & (hash_count - 1)
        return None

    return read


def dbc_rows(data):
    magic, count, fields, size, strings = struct.unpack_from("<4s4I", data, 0)
    assert magic == b"WDBC" and size == fields * 4, "not a DBC of whole-number fields"
    rows = [struct.unpack_from(f"<{fields}i", data, 20 + n * size) for n in range(count)]
    return fields, rows, data[20 + count * size:20 + count * size + strings]


def patch(path, dbc):
    read = mpq_files(path)
    problems = []
    added = {}
    for name in ("Item.dbc", "ItemExtendedCost.dbc", "CurrencyTypes.dbc"):
        inside = read(f"DBFilesClient\\{name}")
        if inside is None:
            problems.append(f"{name} isn't in the patch")
            continue
        fields, rows, strings = dbc_rows(inside)
        base_fields, base_rows, base_strings = dbc_rows(open(f"{dbc}/{name}", "rb").read())
        by_id = {r[0]: r for r in rows}
        new = [r for r in rows if r[0] not in {b[0] for b in base_rows}]
        missing = [b[0] for b in base_rows if by_id.get(b[0]) != b and b[0] not in {n[0] for n in new}]
        changed = [b[0] for b in base_rows if b[0] in by_id and by_id[b[0]] != b]
        print(f"patch: {name}: {len(base_rows)} rows of the game's, {len(new)} added, {len(changed)} changed")
        if fields != base_fields or strings != base_strings:
            problems.append(f"{name}: fields or strings differ from the game's")
        if missing:
            problems.append(f"{name}: {len(missing)} of the game's rows lost")
        added[name] = {r[0]: r for r in new + [by_id[c] for c in changed]}
    if not problems:
        bronze = added["Item.dbc"].get(77001)
        if not bronze or bronze[1:3] != (10, 0):
            problems.append(f"Item.dbc: Bronze (77001) isn't a currency item ({bronze})")
        currency = [r for r in added["CurrencyTypes.dbc"].values() if r[1] == 77001]
        if not currency:
            problems.append("CurrencyTypes.dbc: Bronze isn't a currency")
        prices = {r[0]: r[9] for r in added["ItemExtendedCost.dbc"].values() if r[4] == 77001}
        print(f"patch: Bronze, currency {currency}, {len(prices)} prices from {min(prices.values(), default=0)} to {max(prices.values(), default=0)}")
        if prices.get(7708) != 300 or prices.get(7726) != 20000:
            problems.append(f"ItemExtendedCost.dbc: the ladder isn't there ({sorted(prices.items())[:5]}...)")
    for p in problems:
        print(f"patch: {p}")
    return problems


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "patch":
        problems = patch(sys.argv[2], sys.argv[3])
        print("patch: the game's patch has Bronze and its prices" if not problems else "patch: wrong")
        sys.exit(1 if problems else 0)
    if len(sys.argv) == 7 and sys.argv[1] == "floors":
        bad = floors(*sys.argv[2:7])
        print(f"floor: {bad} off" if bad else "floor: every spawn stands on the floor")
        sys.exit(1 if bad else 0)
    print(__doc__, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
