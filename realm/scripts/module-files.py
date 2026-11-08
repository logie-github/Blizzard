#!/usr/bin/env python3
"""The game files the modules the app's user picked bring, for the realm package
(scripts/package-azerothcore.sh): the server's DBC files they replace, and their patch for the game.

A module that adds races or classes (mod-arac, mod-worgoblin) changes DBC files, which the world
server reads from its data folder and the game from its archives: its README has them copied over
the server's own (server/data/dbc) and its patch put in the game's Data. Here:

  - share/dbc: every .dbc file a module has, by name. Where two modules change the same file
    (mod-arac and mod-worgoblin both change CharBaseInfo, CharStartOutfit and SkillRaceClassInfo),
    their records go together: each file is the game's own with the module's records added or
    changed, so one record (by its id) that both have and that differs keeps one module's values,
    the race and class masks of both (a skill for mod-arac's races and for mod-worgoblin's). A file
    with text that two modules change can't be put together that way: the later module's is used,
    and the report says so. ctl.sh puts these over the server's data each start (`modules`).
  - share/client: the modules' patch folders for the game (a folder named patch or patch-*.MPQ with
    the game's own folders in it: DBFilesClient, Interface, Character...), one over the other, with
    the DBC files above in its DBFilesClient. ctl.sh puts it in the game's Data as patch-M.MPQ.
    A module's .MPQ archives aren't opened: mod-arac's Patch-A.MPQ is its three DBC files.
  - share/client.stamp: what's in share/client, so the game's copy is made again only when it changes.
  - share/module-files.txt: what came from where, and what couldn't be put together.

  module-files.py OUT MODULE_DIR...    (the modules in the order they were picked)
"""

import hashlib
import os
import shutil
import struct
import sys

# Folders a patch for the game has at its top (the game's archives' own).
CLIENT_FOLDERS = {
    "character", "creature", "dbfilesclient", "dungeons", "environments", "fonts", "interface",
    "item", "particles", "sound", "spells", "textures", "tileset", "world", "xtextures",
}
# Fields (by index) that are race or class masks: two modules' masks for one record go together.
MASKS = {
    "skillraceclassinfo.dbc": (2, 3),
    "skilllineability.dbc": (3, 4),
}


def is_client_patch(path):
    name = os.path.basename(path).lower()
    if name != "patch" and not (name.startswith("patch") and name.endswith(".mpq")):
        return False
    return any(entry.lower() in CLIENT_FOLDERS for entry in os.listdir(path)
               if os.path.isdir(os.path.join(path, entry)))


def module_files(module):
    """A module's .dbc files (lowercase name: path) and its patch folders for the game."""
    dbcs, patches = {}, []
    for root, dirs, files in os.walk(module):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        if root != module and is_client_patch(root):
            patches.append(root)
        for name in sorted(files):
            if name.lower().endswith(".dbc"):
                # The same file twice in a module (a server copy and a client copy): the first.
                dbcs.setdefault(name.lower(), os.path.join(root, name))
    return dbcs, patches


class Dbc:
    def __init__(self, data, name):
        magic, self.count, self.fields, self.size, self.strings = struct.unpack("<4s4I", data[:20])
        if magic != b"WDBC" or len(data) != 20 + self.count * self.size + self.strings:
            raise ValueError(f"{name} isn't a DBC file")
        self.records = [data[20 + i * self.size:20 + (i + 1) * self.size] for i in range(self.count)]
        self.text = data[20 + self.count * self.size:]

    def ids(self):
        return [struct.unpack_from("<I", r)[0] for r in self.records]


def merge(name, sources, notes):
    """One DBC file from several modules' (module, bytes), later modules over earlier ones."""
    files = [(module, Dbc(data, name)) for module, data in sources]
    shapes = {(dbc.fields, dbc.size) for _, dbc in files}
    if len(shapes) > 1 or any(dbc.strings > 1 for _, dbc in files):
        module = files[-1][0]
        notes.append(f"{name}: changed by {', '.join(m for m, _ in files)}; "
                     f"{'its text' if len(shapes) == 1 else 'its layout'} can't be put together, {module}'s is used")
        return sources[-1][1]
    first = files[0][1]
    # Keyed by id when every file's first field is one (CharBaseInfo's records are two bytes, a
    # race and a class: the whole record).
    by_id = first.size == first.fields * 4 and all(len(set(dbc.ids())) == dbc.count for _, dbc in files)
    masks = MASKS.get(name.lower(), ())
    merged, owner = {}, {}
    for module, dbc in files:
        for record in dbc.records:
            key = struct.unpack_from("<I", record)[0] if by_id else record
            if key in merged and merged[key] != record:
                old = list(struct.unpack(f"<{first.fields}I", merged[key]))
                new = list(struct.unpack(f"<{first.fields}I", record))
                for i in masks:
                    new[i] |= old[i]
                others = [i for i in range(first.fields) if i not in masks and old[i] != new[i]]
                if others:
                    notes.append(f"{name}: record {key} differs in fields {others} between "
                                 f"{owner[key]} and {module}; {module}'s is used")
                record = struct.pack(f"<{first.fields}I", *new)
            merged[key] = record
            owner[key] = module
    records = [merged[key] for key in sorted(merged)]
    header = struct.pack("<4s4I", b"WDBC", len(records), first.fields, first.size, len(first.text))
    notes.append(f"{name}: {', '.join(m for m, _ in files)} put together ({len(records)} records)")
    return header + b"".join(records) + first.text


def copy_tree(source, target, names, folders):
    """Copies a patch folder over target. The game's paths ignore case, so a path is one file
    whatever its case: each folder and file keeps the case it first came with (names, folders:
    lowercase relative path: the one used)."""
    for root, dirs, files in os.walk(source):
        dirs.sort()
        for name in sorted(files):
            parts = os.path.relpath(os.path.join(root, name), source).split(os.sep)
            for i in range(1, len(parts)):
                folder = os.sep.join(parts[:i])
                parts[:i] = folders.setdefault(folder.lower(), folder).split(os.sep)
            rel = names.setdefault(os.sep.join(parts).lower(), os.sep.join(parts))
            dest = os.path.join(target, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(os.path.join(root, name), dest)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out, modules = sys.argv[1], sys.argv[2:]
    report, notes = [], []
    dbcs, patches = {}, []
    for module in modules:
        name = os.path.basename(module.rstrip("/"))
        found, folders = module_files(module)
        for key, path in found.items():
            dbcs.setdefault(key, []).append((name, path))
            report.append(f"{name}: {os.path.relpath(path, module)}")
        for folder in folders:
            patches.append(folder)
            report.append(f"{name}: {os.path.relpath(folder, module)}/ (for the game)")
    if not dbcs and not patches:
        print("The modules bring no game files")
        return

    server = os.path.join(out, "dbc")
    os.makedirs(server, exist_ok=True)
    written = {}
    for key in sorted(dbcs):
        sources = dbcs[key]
        name = os.path.basename(sources[-1][1])
        if len(sources) == 1:
            data = open(sources[0][1], "rb").read()
        else:
            data = merge(name, [(module, open(path, "rb").read()) for module, path in sources], notes)
        with open(os.path.join(server, name), "wb") as f:
            f.write(data)
        written[key] = (name, data)

    client = os.path.join(out, "client")
    names, folders = {}, {}
    for folder in patches:
        copy_tree(folder, client, names, folders)
    for key, (name, data) in written.items():
        rel = names.setdefault(os.path.join("dbfilesclient", key),
                               os.path.join(folders.get("dbfilesclient", "DBFilesClient"), name))
        os.makedirs(os.path.dirname(os.path.join(client, rel)), exist_ok=True)
        with open(os.path.join(client, rel), "wb") as f:
            f.write(data)

    stamp = hashlib.sha256()
    for key in sorted(names):
        stamp.update(names[key].encode() + b"\0")
        with open(os.path.join(client, names[key]), "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                stamp.update(block)
    with open(os.path.join(out, "client.stamp"), "w") as f:
        f.write(stamp.hexdigest() + "\n")
    with open(os.path.join(out, "module-files.txt"), "w") as f:
        f.write("\n".join(report + notes) + "\n")
    print("\n".join(report + notes))
    print(f"{len(written)} DBC files for the server; {len(names)} files for the game")


if __name__ == "__main__":
    main()
