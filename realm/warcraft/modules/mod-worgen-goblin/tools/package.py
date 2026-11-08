#!/usr/bin/env python3
"""mod-worgoblin's files for ChromieCraft's realm, made as the server is packaged
(scripts/package-azerothcore.sh), from the module's checkout the compile used: never in this
repository (they're the game's: models, textures, sounds).

    python3 tools/package.py WORGOBLIN_DIR OUT

OUT is the module's data folder in the package (src/modules/mod-worgen-goblin/data). It gets:

  - files/: mod-worgoblin's patch for the game (its data/patch: the Worgen's and Goblins' models,
    textures, sounds, icons, their creation screen's backgrounds), laid out as the game's patch, with
    worgengoblin.files listing it (written last: a package that stops leaves none, and the world
    server then makes no patch). Left out: its 30 whole tables (DBFilesClient: the realm puts what they
    change into the game's own, data/client/dbc), its character screen's and FrameXML's files (the
    game's own, with its own few changes: data/client/Interface/GlueXML/WorgenGoblinCreate.lua does
    them on top of the others'), and its race icons (the game's whole icon sheet with its two races
    in the column the allied races' Lightforged and Zandalari have: theirs are cut out into a sheet of
    their own, UI-CharacterCreate-Worgoblin*.blp). Its race texts (from its GlueStrings.lua, the
    game's whole English text file) become Interface/GlueXML/WorgenGoblinStrings.lua.
  - sql/chromiecraft/world/: its SQL for the world database (the races' starts, stats, gear, action
    bars, skills, racials and quests; its death knights' quests and the goblins' trike vendor), named
    after the module (the servers know an applied file by its name alone, across every module),
    without the columns this core's tables haven't (GONE):
    ChromieCraft's alone (ctl.sh's realm_sql), never Wrath Remix's. Its *_dbc SQL isn't used: it
    takes whole rows the allied races' and the Skyborne's SQL also change
    (data/server/worgen_goblin_dbc.sql merges instead).
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "mod-allied-races", "tools"))

MANIFEST = "worgengoblin.files"
LEFT_OUT_FOLDERS = ("dbfilesclient/", "interface/gluexml/", "interface/framexml/")
ICONS = {
    "interface/glues/charactercreate/ui-charactercreate-races.blp": "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Worgoblin.blp",
    "interface/glues/charactercreate/ui-charactercreate-racesround.blp": "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-WorgoblinRound.blp",
}
ICON_COLUMN = 5                      # of 8: Worgen men, Goblin men, Worgen women, Goblin women, top to bottom
SQL = {
    "data/sql/db-world/worgoblin.sql": "worgen_goblin_races.sql",
    "data/sql/db-world/worgoblin_x_druid_quests.sql": "worgen_goblin_druid_quests.sql",
    "data/sql/supplementary/dk-quests.sql": "worgen_goblin_dk_quests.sql",
    "data/sql/supplementary/optional-mount-vendor.sql": "worgen_goblin_trike_vendor.sql",
}
STRINGS = re.compile(r"^(RACE_INFO|ABILITY_INFO)_(WORGEN|GOBLIN)\w*\s*=")
# Columns its SQL names that this core's tables haven't: its death knights' quests were written for an
# older core (quest_template's RewardBonusMoney; creature_template's models, scale, trainer and
# immunity columns; creature's id1 to id3). Taken out of its INSERTs, values and all, or renamed
# (RENAMED); a creature's models and scale go into creature_template_model, where this core keeps them.
GONE = {"quest_template": ("RewardBonusMoney",),
        "creature_template": ("modelid1", "modelid2", "modelid3", "modelid4", "scale", "trainer_type", "trainer_spell",
                              "trainer_class", "trainer_race", "mechanic_immune_mask", "spell_school_immune_mask"),
        "creature": ("id2", "id3")}
RENAMED = {"creature": {"id1": "id"}}


def values_of(text, at):
    """The rows of an INSERT's VALUES from [at]: each row's values as their SQL text, and where the
    statement's rows end."""
    rows, row, value, depth, i = [], [], [], 0, at
    while i < len(text):
        c = text[i]
        if c == "'" or c == '"':
            j = i + 1
            while j < len(text) and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            value.append(text[i:j + 1])
            i = j + 1
            continue
        if c == "(":
            depth += 1
            if depth == 1:
                row, value = [], []
                i += 1
                continue
        elif c == ")":
            depth -= 1
            if depth == 0:
                row.append("".join(value).strip())
                rows.append(row)
                i += 1
                continue
        elif c == "," and depth == 1:
            row.append("".join(value).strip())
            value = []
            i += 1
            continue
        elif c == ";" and depth == 0:
            return rows, i
        if depth >= 1:
            value.append(c)
        i += 1
    return rows, i


def drop_columns(sql):
    """[sql] with GONE's columns taken out of its INSERTs into those tables."""
    out, at = [], 0
    pattern = re.compile(r"INSERT INTO `?(\w+)`?\s*\(([^)]*)\)\s*VALUES", re.I)
    for m in pattern.finditer(sql):
        if m.start() < at:
            continue
        table, cols = m.group(1), [c.strip().strip("`") for c in m.group(2).split(",")]
        gone = [i for i, c in enumerate(cols) if c in GONE.get(table, ())]
        if not gone and not set(cols) & set(RENAMED.get(table, {})):
            continue
        cols = [RENAMED.get(table, {}).get(c, c) for c in cols]
        rows, end = values_of(sql, m.end())
        keep = [i for i in range(len(cols)) if i not in gone]
        assert all(len(r) == len(cols) for r in rows), (table, "a row of the wrong size")
        out.append(sql[at:m.start()])
        out.append(f"INSERT INTO `{table}` (" + ", ".join(f"`{cols[i]}`" for i in keep) + ") VALUES\n"
                   + ",\n".join("(" + ", ".join(r[i] for i in keep) + ")" for r in rows))
        if table == "creature_template":
            entry = cols.index("entry")
            scale = cols.index("scale") if "scale" in cols else None
            models = [(r[entry], n, r[i], r[scale] if scale is not None else "1") for r in rows
                      for n, i in enumerate(i for i in gone if cols[i].startswith("modelid")) if r[i] not in ("0", "")]
            if models:
                out.append(";\nDELETE FROM `creature_template_model` WHERE `CreatureID` IN ("
                           + ", ".join(sorted({e for e, _, _, _ in models})) + ");\n"
                           + "INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, "
                           + "`Probability`, `VerifiedBuild`) VALUES\n"
                           + ",\n".join(f"({e}, {n}, {d}, {sc}, 1, 0)" for e, n, d, sc in models))
        at = end
    out.append(sql[at:])
    text = "".join(out)
    # (and in the DELETEs that clear them first)
    for table, names in RENAMED.items():
        for old, new in names.items():
            text = re.sub(r"(DELETE FROM `?%s`? WHERE [^;]*?)`?\b%s\b`?" % (table, old), r"\1`%s`" % new, text, flags=re.I)
    return text


def icon_column(data):
    """The two races' column cut out of a race icon sheet (8 icons a row, 4 rows): a sheet of its own."""
    import blp
    rgba = blp.read(data)
    height, width = rgba.shape[:2]
    cell = width // 8
    column = rgba[:, ICON_COLUMN * cell:(ICON_COLUMN + 1) * cell].copy()
    return blp.write_dxt(column, alpha=True)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    worgoblin, out = sys.argv[1:]
    patch = os.path.join(worgoblin, "data", "patch")
    files = os.path.join(out, "files")
    manifest = os.path.join(files, MANIFEST)
    if os.path.exists(manifest):
        os.remove(manifest)
    listed = []
    for root, dirs, names in os.walk(patch):
        dirs.sort()
        for name in sorted(names):
            src = os.path.join(root, name)
            rel = os.path.relpath(src, patch).replace(os.sep, "/")
            low = rel.lower()
            if low.startswith(LEFT_OUT_FOLDERS):
                continue
            if low in ICONS:
                game = ICONS[low]
                data = icon_column(open(src, "rb").read())
            else:
                game = rel.replace("/", "\\")
                data = None
            dest = os.path.join(files, game.replace("\\", "/"))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if data is None:
                shutil.copyfile(src, dest)
            else:
                with open(dest, "wb") as f:
                    f.write(data)
            listed.append(game)

    # The two races' texts, from its English GlueStrings.lua.
    glue = os.path.join(patch, "Interface", "GlueXML", "GlueStrings.lua")
    lines = [l.rstrip("\r\n") for l in open(glue, encoding="utf-8", errors="replace") if STRINGS.match(l)]
    if not lines:
        sys.exit("mod-worgoblin's GlueStrings.lua has no texts for its races")
    game = "Interface\\GlueXML\\WorgenGoblinStrings.lua"
    dest = os.path.join(files, game.replace("\\", "/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("-- The Worgen's and Goblins' texts on the character creation screen (mod-worgoblin's GlueStrings.lua)\n")
        f.write("\n".join(lines) + "\n")
    listed.append(game)

    # Its SQL, ChromieCraft's world database's alone.
    sql = os.path.join(out, "sql", "chromiecraft", "world")
    os.makedirs(sql, exist_ok=True)
    for src, name in SQL.items():
        text = open(os.path.join(worgoblin, src), encoding="utf-8").read()
        with open(os.path.join(sql, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(drop_columns(text))

    with open(manifest + ".part", "w", newline="\n") as f:
        f.write("\n".join(listed) + "\n")
    os.replace(manifest + ".part", manifest)
    print(f"Worgen and Goblins: {len(listed)} files for the game, {len(SQL)} SQL files for ChromieCraft's world")


if __name__ == "__main__":
    main()
