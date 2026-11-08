#!/usr/bin/env python3
"""The committed data of mod-murloc-naga checked against itself: every quest's giver, ender, required
creature and item is there (the module's own or the game's named in tools/content.py), every spawn's
creature and object, every look's texture the patch makes; every id in the module's ranges; the
retired starts gone (the murlocs' village, the naga's Darkshore camp: their ids kept, the camp's three
people the naga's story's); the two stories' SQL apart (each its own ranges and tables, no phase of one on
the other's people, each DELETE its own rows); the intros' cameras read as the world server reads them
(one camera, keys in time order, the flight's length); the narrations' recipe names the game's files."""
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "mod-allied-races", "tools"))
import cameras  # noqa: E402
import content as C  # noqa: E402
import sqlrows  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
SQL = open(os.path.join(DATA, "sql", "chromiecraft", "world", "murloc_naga_world.sql"), encoding="utf-8").read()
failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


def rows(table):
    """The rows of [table]'s INSERTs, as dicts."""
    out = []
    for m in re.finditer(r"INSERT INTO `%s` \(([^)]*)\) VALUES\n" % table, SQL):
        cols = [c.strip(" `") for c in m.group(1).split(",")]
        end = SQL.index(";\n", m.end())
        for r in sqlrows.values("INSERT INTO x VALUES " + SQL[m.end():end + 1]):
            out.append(dict(zip(cols, r)))
    return out


creatures = {int(r["entry"]): r for r in rows("creature_template")}
gos = {int(r["entry"]): r for r in rows("gameobject_template")}
items = {int(r["entry"]): r for r in rows("item_template")}
quests = {int(r["ID"]): r for r in rows("quest_template")}
game_creatures = {C.PYGMY_TIDE_CRAWLER, C.DARKSHORE_THRESHER, 2187, C.WRATHTAIL_MYRMIDON, C.WRATHTAIL_RAZORTAIL,
                  C.THUNDRIS_WINDWEAVER, C.GLYNDA_NALSHEA, C.ONU, C.MARUKAI}
# (the murlocs' Darkshore village and the naga's camp are retired: their quests are their stories', tools/murloc/
# and tools/naga/)
village = C.MURLOC_QUESTS if C.MURLOC_VILLAGE else []
camp = C.NAGA_QUESTS if C.NAGA_CAMP else []
check(len(quests) == len(village) + len(camp), f"every quest is there ({len(quests)}: the retired starts' none)")
check(all(C.QUEST_BASE <= q < C.QUEST_BASE + 100 for q in quests), "the quests' ids are the module's")
check(all(C.NPC_BASE <= e < C.NPC_BASE + 100 for e in creatures), "the creatures' ids are the module's")
check(all(C.GO_BASE <= e < C.GO_BASE + 100 for e in gos), "the objects' ids are the module's")
check(all(C.ITEM_BASE <= e < C.ITEM_BASE + 100 for e in items), "the items' ids are the module's")
check(sum(1 for q in quests.values() if int(q["AllowableRaces"]) == 1 << 18) == len(village), "the murlocs' village quests: retired")
check(sum(1 for q in quests.values() if int(q["AllowableRaces"]) == 1 << 19) == len(camp), "the naga's camp quests: retired")
check(not any(int(e) in (975017, 975018, 975019) for e in creatures), "the camp's three people aren't this file's (the naga story's)")
check("mod-murloc-naga: not for the naga" not in SQL.split("DELETE FROM `conditions`")[0] and
      "INSERT INTO `conditions`" not in SQL, "the camp's Darkshore conditions: taken out, none put in")

starters = {(int(r["id"]), int(r["quest"])) for r in rows("creature_queststarter")}
enders = {(int(r["id"]), int(r["quest"])) for r in rows("creature_questender")}
go_enders = {(int(r["id"]), int(r["quest"])) for r in rows("gameobject_questender")}
known = set(creatures) | game_creatures
for q in quests:
    givers = [c for c, quest in starters if quest == q]
    ends = [c for c, quest in enders if quest == q] + [g for g, quest in go_enders if quest == q]
    check(givers and all(c in known for c in givers), f"quest {q} ({quests[q]['LogTitle']}): offered by {givers}")
    check(len(ends) == 1 and (ends[0] in known or ends[0] in gos), f"...handed in to {ends}")
    for i in range(1, 5):
        n = int(quests[q][f"RequiredNpcOrGo{i}"])
        if n:
            check(n in known, f"...its creature {n} is there")
    for i in range(1, 7):
        it = int(quests[q][f"RequiredItemId{i}"])
        if it:
            check(it in items or it == C.THRESHER_EYE, f"...its item {it} is there")
addons = {int(r["ID"]): r for r in rows("quest_template_addon")}
for q, a in addons.items():
    prev = int(a["PrevQuestID"])
    check(prev == 0 or prev in quests, f"quest {q} comes after {prev or 'nothing'}")
if C.NAGA_CAMP:
    tide = C.QUEST_BASE + 32
    check((C.ONU, tide) in starters and quests[tide]["MinLevel"] == "17", "The Tide Turns: Onu's, from level 17")
    check((C.MARUKAI, C.QUEST_BASE + 34) in enders, "An Unlikely Allegiance: handed in to Marukai at Zoram'gar")

spawned = [int(r["id"]) for r in rows("creature")]
check(all(e in known for e in spawned), f"every creature spawned is there ({len(spawned)} spawns)")
phases = {int(r["phaseMask"]) for r in rows("creature")} | {int(r["phaseMask"]) for r in rows("gameobject")}
check(phases <= {C.PHASE[C.MURLOC], C.PHASE[C.NAGA]}, f"everything in the races' own phases ({phases})")
check(all(int(r["id"]) in gos for r in rows("gameobject")), "every object placed is there")
loot = {int(r["Entry"]) for r in rows("gameobject_loot_template")}
check(all(int(g["Data1"]) in loot for g in gos.values() if g["type"] == "3"), "every chest has its loot")

# The looks' textures: the murlocs' are tools/murloc_model.py's (named by tools/murloc_looks.py), the
# naga's new colours the patch's (looks.txt).
import murloc_looks as ML  # noqa: E402
looks = [l.rstrip("\n").split("\t") for l in open(os.path.join(DATA, "client", "looks.txt")) if not l.startswith("#")]
check(len([l for l in looks if l[0] == "naga_colour"]) == 8, "the naga's four new colours a sex")
sections = open(os.path.join(DATA, "client", "dbc", "CharSections.txt")).read()
made = {"MurlocBase"} | {"MurlocBody%02d" % c for c in range(len(ML.SKINS))} \
    | {"MurlocEyes%02d_%02d" % (f, c) for f in range(len(ML.EYE_COLOURS)) for c in range(len(ML.SKINS))} \
    | {ML.fin_texture(s, h).split("\\")[-1][:-4] for s in range(len(ML.FIN_STYLES)) for h in range(len(ML.FIN_COLOURS))}
named = set(re.findall(r"Character\\\\Murloc\\\\([A-Za-z0-9_]+)\.blp", sections))
check(named and named <= made, f"every murloc texture the looks name is one tools/murloc_model.py makes ({sorted(named - made)})")
check(named == made, f"the murlocs' {len(ML.SKINS)} skin colours, {len(ML.EYE_COLOURS)} eye colours, "
      f"{len(ML.FIN_STYLES)} fin styles in {len(ML.FIN_COLOURS)} colours ({sorted(made - named)[:4]})")
check(not re.search(r"Murloc(Skin|Hair)", sections), "no skin \"extra\" or hair texture for the murlocs (the game draws neither for them)")
geosets = open(os.path.join(DATA, "client", "dbc", "CharHairGeosets.txt")).read()
murloc_hair = [l.split("\t") for l in geosets.splitlines() if re.match(r"^put\t\d+\t19\t", l)]
check(len(murloc_hair) == 2 * len(ML.FIN_STYLES), "a fin style row each (murlocs)")
check(all(int(r[5]) >= 2 for r in murloc_hair), "...each a geoset of its own (2 and up)")
facial = open(os.path.join(DATA, "client", "dbc", "CharacterFacialHairStyles.txt")).read()
styles = [bytes.fromhex(l.split("\t")[1]) for l in facial.splitlines() if l.startswith("appendraw")]
styles = [struct.unpack("<%dI" % (len(b) // 4), b) for b in styles]
check(len([r for r in styles if r[0] == 19]) == sum(len(v) for v in ML.FEATURES.values()), "a feature row each (murlocs)")
check(all(r[3] >= 1 for r in styles if r[0] in (19, 20)), "no feature's geoset 0 (the game shows every one of the group's meshes for it)")
# The game draws a player as a character (its composed skin, its chosen fins and features) only on a model
# flagged a player's (CreatureModelData's 0x4); otherwise as a creature, white, with every geoset at once.
models = open(os.path.join(DATA, "client", "dbc", "CreatureModelData.txt")).read()
murloc_models = {int(l.split("\t")[1]): int(l.split("\t")[2]) for l in models.splitlines()
                 if l.startswith("put\t") and "Character\\\\Murloc\\\\" in l}
check(len(murloc_models) == 2 and all(f & 0x4 for f in murloc_models.values()),
      f"the murlocs' models are a player's (flag 0x4: {', '.join(hex(f) for f in murloc_models.values())})")
check(all(f"or\t{m}\t1\t4" in models.splitlines() for m in (2353, 2354)), "...and the naga's (the game's naga male hasn't it)")
# Each SQL file takes out its own loot rows only: the server applies a file again when it changes, and the
# other's rows (the naga camp's quest drop, the story's) must stay.
story_sql = open(os.path.join(DATA, "sql", "chromiecraft", "world", "murloc_story.sql"), encoding="utf-8").read()
camp_loot = rows("creature_loot_template")
check((bool(camp_loot) == C.NAGA_CAMP) and all(r["Comment"] == "mod-murloc-naga: camp" for r in camp_loot),
      f"the camp's loot rows are the camp's (comment), none with the camp retired ({len(camp_loot)})")
story_delete = re.search(r"DELETE FROM `creature_loot_template` WHERE ([^;]*);", story_sql).group(1)
check("'mod-murloc-naga: story'" in story_delete and f"NOT BETWEEN {C.NPC_BASE} AND {C.NPC_BASE + 99}" in story_delete,
      "...and the story's delete leaves them (" + story_delete[:60] + "...)")

# The naga's story (tools/naga/: naga_story.sql), apart from the murlocs' (murloc_story.sql).
naga_sql = open(os.path.join(DATA, "sql", "chromiecraft", "world", "naga_story.sql"), encoding="utf-8").read()


def rows_of(text, table):
    out = []
    for m in re.finditer(r"INSERT INTO `%s` \(([^)]*)\) VALUES\n" % table, text):
        cols = [c.strip(" `") for c in m.group(1).split(",")]
        end = text.index(";\n", m.end())
        for r in sqlrows.values("INSERT INTO x VALUES " + text[m.end():end + 1]):
            out.append(dict(zip(cols, r)))
    return out


kept = {975017, 975018, 975019}
naga_creatures = {int(r["entry"]) for r in rows_of(naga_sql, "creature_template")}
check(naga_creatures and all(990000 <= e <= 991999 or e in kept for e in naga_creatures),
      f"the naga's story's creatures in its range, or the camp's three kept ({len(naga_creatures)})")
check(kept <= naga_creatures, "...Lady Szaria, Myrmidon Ssaveth and Vyssa among them (their entries kept)")
check(all(992000 <= int(r["ID"]) <= 992599 and int(r["AllowableRaces"]) == 1 << 19 for r in rows_of(naga_sql, "quest_template")),
      "the naga's story's quests: its range, the naga's alone")
check(all(993000 <= int(r["entry"]) <= 993799 for r in rows_of(naga_sql, "item_template")), "...its items, its range")
spawn_rows = rows_of(naga_sql, "creature") + rows_of(naga_sql, "gameobject")
check(spawn_rows and all(9900000 <= int(r["guid"]) <= 9939999 for r in spawn_rows), "...its spawns, its range")
check(all(int(r["phaseMask"]) & (1 | 1024) == 0 for r in spawn_rows), "...none in the world's phase or the murlocs'")
murloc_spawns = rows_of(story_sql, "creature") + rows_of(story_sql, "gameobject")
check(all(int(r["phaseMask"]) & 2048 == 0 for r in murloc_spawns), "the murlocs' spawns: none in the naga's phase")
naga_bits = set()
for r in rows_of(naga_sql, "spell_area"):
    naga_bits.add(int(r["spell"]))
check(all(int(r["aura_spell"]) == -994002 and int(r["racemask"]) == 1 << 19 for r in rows_of(naga_sql, "spell_area")),
      "the naga's phase rows: the naga's alone, none while reliving a memory (the marker absent)")
check(any(int(r["area"]) == 1237 for r in rows_of(naga_sql, "spell_area")), "...Valormok: the world's and theirs from the first login")
deletes = re.findall(r"DELETE FROM `([a-z_]+)` WHERE ([^;]*);", naga_sql)
check(all(("990000" in w or "992000" in w or "993000" in w or "9900000" in w or "9930000" in w or "1990000" in w or "994000" in w
           or "9900" in w or "10400" in w or "40200" in w or "25000" in w or "naga story" in w) for t, w in deletes),
      f"every DELETE of the naga's SQL is of its own rows ({len(deletes)})")
check(not re.search(r"DELETE FROM `(murloc_naga_story|murloc_naga_story_learn|murloc_naga_graveyards)`", naga_sql),
      "...never the murlocs' tables (the naga have theirs)")
memories = rows_of(naga_sql, "naga_story_memories")
check(memories and all(int(m["bit"]) in (2, 4, 8) for m in memories), f"the memories: one of the three memory bits each ({len(memories)})")
check(re.search(r"\('marker_spell', 994002\)", naga_sql) and re.search(r"\('fade_spell', 994003\)", naga_sql),
      "the module's marker and fade named")
world_delete = re.search(r"DELETE FROM `creature_template` WHERE ([^;]*);", SQL).group(1)
check("NOT IN (975017, 975018, 975019)" in world_delete, "this file's camp DELETE leaves the kept three (" + world_delete + ")")
steps = open(os.path.join(HERE, "..", "..", "..", "server", "murloc_naga_naga.steps")).read()
check(not any("{" in l for l in steps.splitlines() if not l.startswith("#")) and "992001" in steps,
      "the naga's server steps: the story's ids")

import naga_looks as NL  # noqa: E402
naga_hair = len(re.findall(r"^put\t\d+\t20\t", geosets, re.M))
check(naga_hair == sum(len(NL.HEADDRESSES[s]) + 1 for s in ("Male", "Female")), f"a headdress row each (naga: {naga_hair})")
check(all(NL.headdress_texture(s, h, c).replace("\\", "\\\\") in sections for s in ("Male", "Female")
          for h in range(1, len(NL.HEADDRESSES[s]) + 1) for c in range(NL.colours(s))), "the headdresses' colours in CharSections")
check(not re.search(r"Naga_\\\\(Hair|Scalp|Facial)", sections), "no naga hair, scalp or facial hair texture the game hasn't")
check(sections.count("put\t") > 100, "the races' looks")

# The cameras, as the world server reads them.
for race, length in (("Murloc", 42000), ("Naga", 61000)):
    m2 = open(os.path.join(DATA, "client", "Cameras", f"Flyby{race}.m2"), "rb").read()
    skin = open(os.path.join(DATA, "client", "Cameras", f"Flyby{race}00.skin"), "rb").read()
    check(m2[:4] == b"MD20" and struct.unpack_from("<I", m2, 4)[0] == 264 and skin[:4] == b"SKIN", f"{race}'s camera is a 3.3.5 model")
    pos, tgt = cameras.read_positions(m2)
    check(len(pos) >= 8 and len(tgt) == len(pos) and pos[-1][0] == length, f"...{len(pos)} keys, {length} ms")
    check(all(a[0] < b[0] for a, b in zip(pos, pos[1:])), "...in time order")
    seq = struct.unpack_from("<I", m2, struct.unpack_from("<I", m2, 0x20)[0] + 4)[0]
    check(seq == length, "...its sequence as long")

narration = [l.rstrip("\n").split("\t") for l in open(os.path.join(DATA, "client", "narration.txt")) if not l.startswith("#")]
check({l[0] for l in narration} == {"Murloc", "Naga"} and all(l[2].startswith("Sound\\") for l in narration), "the narrations: the game's sounds")
check(sum(1 for l in narration if "LadyVashj" in l[2]) == 6, "the naga's: six of Lady Vashj's lines")
check(not any("Death01" in l[2] or "Slay03" in l[2] for l in narration), "...not her death (the naga's story's end)")

# The naga's story's assets (tools/naga/, tools/naga_assets.py): every voice and look in the module's
# ranges and in the tables, the emotes' ids the game's.
from naga import looks as LK, sounds as S  # noqa: E402
import naga_emotes as NE  # noqa: E402
voices = [l.split("\t") for l in open(os.path.join(DATA, "client", "dbc", "SoundEntries.txt")).read().splitlines()
          if l.startswith("put\t") and S.FIRST_ID <= int(l.split("\t")[1]) <= S.LAST_ID]
check(len(S.VOICES) == 82 and len(S.SOUNDS) == 82 and len(set(S.SOUNDS.values())) == 82, "the naga's story's 82 Warcraft III voices, an id each")
check(all(S.FIRST_ID <= i <= S.LAST_ID for i in S.SOUNDS.values()), "...in SoundEntries 995000 to 995199")
check({int(v[1]): v[4] for v in voices} == {i: n + ".wav" for n, i in S.SOUNDS.items()}
      and all(v[24] == S.DIRECTORY.replace("\\", "\\\\") for v in voices), "...each a SoundEntries row naming its WAV in Sound\\Creature\\WC3Voices")
check(all(len(sha1) == 40 and size > 44 and words for _, sha1, size, _, words in S.VOICES), "...each pinned by its SHA-1 and size, with its words")
check(len(re.findall(r"\(99[5]\d\d\d, 10, 'NagaStory_", SQL)) == 82, "...and in the world database's soundentries_dbc")
display_rows = {int(l.split("\t")[1]): l.split("\t") for l in open(os.path.join(DATA, "client", "dbc", "CreatureDisplayInfo.txt")).read().splitlines()
                if l.startswith("put\t")}
extra_rows = {int(l.split("\t")[1]): l.split("\t") for l in open(os.path.join(DATA, "client", "dbc", "CreatureDisplayInfoExtra.txt")).read().splitlines()
              if l.startswith("put\t")}
model_rows = {int(l.split("\t")[1]): l.split("\t") for l in models.splitlines() if l.startswith("put\t")}
check(all(LK.DISPLAY_FIRST <= d <= LK.DISPLAY_LAST and d in display_rows for d in LK.LOOKS.values()), "every look's CreatureDisplayInfo row, 40000 to 40299")
check(set(LK.EMOTES) == set(LK.LOOKS) and set(LK.FALLBACK) <= set(LK.LOOKS), "every look says which emotes it plays")
check(all(LK.MODEL_DATA_FIRST <= c["model_data"] <= LK.MODEL_DATA_LAST and c["model_data"] in model_rows
          and model_rows[c["model_data"]][3] == "%s\\\\%s.mdx" % (c["folder"].replace("/", "\\\\"), c["name"]) for c in LK.CREATURES),
      "the converted models' CreatureModelData rows, 3800 to 3849, naming their files")
check(all(int(display_rows[d][2]) == m and display_rows[d][7:10] == list(s) for d, (m, _, _, s) in LK.CREATURE_LOOKS.items()),
      "...their looks with their skins")
check(all(LK.EXTRA_FIRST <= x <= LK.EXTRA_LAST and x in extra_rows and int(display_rows[d][4]) == x
          and [int(v) for v in extra_rows[x][9:20]] == list(items) for d, (x, _, _, _, _, _, _, _, _, items) in LK.PARTS_LOOKS.items()),
      "the looks of the game's parts: their CreatureDisplayInfoExtra rows (25000 to 25099), their items")
check(all(f"({d}, 0.306, 1.5, " in SQL for d in LK.LOOKS.values()), "...every look's size in creature_model_info")
emote_ids = [a for a, _ in NE.EMOTES]
check(len(emote_ids) == len(set(emote_ids)) and all(0 < a <= 505 for a in emote_ids), "the naga's emotes: ids 3.3.5 has, each once")
check(all(how[1] in emote_ids for _, how in NE.EMOTES if how[0] == "alias"), "...every alias of one of them")

print("PASSED" if not failures else f"FAILED ({failures})")
sys.exit(1 if failures else 0)
