"""Ids, decided by pure functions of the whole expansion (never by who ran which shard, never by hand).

The zones' rule (tools/zones/build_tables.py): a row keeps Cataclysm's id where 3.3.5a and the realm have no row of that id;
where they do (a different thing of the same number) it gets a new id from a range of its own. Everything here is sorted
and total, so the same inputs give the same ids in every shard and every run; `inventory` writes the result into ids.json.
"""
import json
import os

from . import util

DATA = os.path.join(util.HERE, "data")
MAP_BASE = 5000          # a Cataclysm map id the game has: 5000 + its id
AREA_BASE = 10000        # a Cataclysm area id the game has: the next free from here
FREE_BITS = range(3618, 4096)   # the character's explored-areas bits (128 x 32, Mirror.cpp:338) past stock 3.3.5a's last, 3617


def stock():
    return json.load(open(os.path.join(DATA, "stock_ids.json")))


def alloc_map_ids(cata_ids, taken_ids, taken_dirs=(), dirs=None):
    """{cata id: new id}. `dirs` {cata id: directory}: a directory 3.3.5a has is taken as well as an id."""
    taken = set(taken_ids)
    out = {}
    dirs = dirs or {}
    for i in sorted(cata_ids):
        clash = i in taken or dirs.get(i, "").lower() in taken_dirs
        new = i
        if clash:
            new = MAP_BASE + i
            while new in taken:
                new += 1
        out[i] = new
        taken.add(new)
    return out


def new_dir(directory, cata_id, new_id, taken_dirs):
    """A map that kept its id keeps its directory unless 3.3.5a has a directory of that name; one that was
    renumbered gets `<dir>Cata`."""
    if new_id != cata_id or directory.lower() in taken_dirs:
        return directory + "Cata"
    return directory


def alloc_area_ids(cata_ids, taken_ids):
    taken = set(taken_ids)
    out = {}
    nxt = AREA_BASE
    for i in sorted(cata_ids):
        if i in taken:
            while nxt in taken:
                nxt += 1
            out[i] = nxt
        else:
            out[i] = i
        taken.add(out[i])
    return out


def alloc_explore_bits(areas, taken_bits):
    """areas {area id: Cataclysm's explore bit}. Returns ({area id: bit}, [area ids left without one]): the bit is kept when
    free, else the next free one of FREE_BITS; none left is bit 0 (the area cannot be tracked as explored: a report line)."""
    taken = set(taken_bits)
    out, none = {}, []
    free = iter(b for b in FREE_BITS)
    for aid in sorted(areas):
        bit = areas[aid]
        if bit and bit not in taken and bit < 4096:
            out[aid] = bit
            taken.add(bit)
            continue
        if not bit:
            out[aid] = 0
            continue
        for cand in free:
            if cand not in taken:
                out[aid] = cand
                taken.add(cand)
                break
        else:
            out[aid] = 0
            none.append(aid)
    return out, none
