#!/usr/bin/env python3
"""Writes Moratari's part in the war (STORY.md, "Moratari in the war") as the world database's rows:
data/sql/remix/world/wrath_remix_world_0027_moratari.sql.

    python3 tools/story.py

The content is in the story_*.py files beside this one (and romance.py); this file puts it together
and writes the SQL. Each content file may define any of these lists:

- WORDS: what Moratari (or Eternus) says on a quest, as it's taken, as its objectives are done, as
  it's turned in (remix_quest_whisper; RemixMoratari.cpp says them beside the Timerunner when she
  walks with them, and whispers them when she doesn't).
- COMPANION: where she walks with the Timerunner (remix_companion).
- PLACES: somewhere a quest sends the Timerunner: its credit as they come near, or a scene there
  whose end gives it (remix_place).
- TALK: what the Timerunner can say, to her or to the war's own people (remix_talk), each with its
  reply (npc_text, written here), what it gives (a quest's credit) and what it does (a scene, an
  outing, she waits or comes). Those of the war's own people with nothing to say in the game are
  given the gossip flag (their own kept in remix_original_story_npcflag).
- QUESTS: the story's own quests in this file: their texts, givers, objectives, place in the game's
  chains (a previous quest, conditions), and where they take the Timerunner as they're taken or
  turned in.
- GATES: conditions on the game's own quests (and Remix's from other files that leave them to this
  one): a quest offered only once these are met (type 19).
- CREATURES: new creatures: credits (never spawned), and copies of the game's (a living William
  Allerton, a cult assassin, Unit S's captives).
- SPAWNS: where new creatures stand, and who sees them (type 30, by quest state).
- HIDE: the game's own spawns some Timerunners no longer see (Allerton's corpse, once he lives).
- RELATIONS: ("starter" or "ender", creature, quest): the game's quests this file's creatures give or
  take back.
- TEXTS: the game's quests whose texts change while Moratari and Eternus steer the war (the
  originals kept in remix_original_story_text, and put back for whatever is dropped from here).
- OUTINGS, LOOKS: somewhere Moratari takes the Timerunner, and her new looks (romance.py).
- OBJECT_TEMPLATES, OBJECTS: things that stand in the world (her tent at the Bazaar, and what is in
  it), in the phases they're seen in (a private outing's is 32768).
- FLAGS: (quest, title, what it means): quests never offered, "turned in" as flags the story's
  conditions read (romance.py's time jumper).
- SPARED: (creature, why): the game's own people the story sends the Timerunner to who would
  otherwise die in the fighting around them; they no longer fight creatures (their own unit flags
  kept in remix_original_story_unit_flags).

Text tokens, in chat and in replies alike: $N the name, $R the race, $C the class ($r and $c in lower
case), $Gmale:female; by the Timerunner's sex. Quest texts: $B a new line (the client's).
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from story_common import (MORATARI, BOTH, ALLIANCE, HORDE, ALLIANCE_RACES, HORDE_RACES, ICON_CHAT, QUEST_FLAG_ALONE,  # noqa: E402
                          sql_text)

CONTENT = ["story_moratari", "story_borean_alliance", "story_borean_horde", "story_dragonblight", "story_undo", "romance"]

# Ranges this file owns
CREATURE_FIRST, CREATURE_LAST = 770500, 770999
OBJECT_FIRST, OBJECT_LAST = 770100, 770199          # gameobject templates
OBJECT_GUID_FIRST, OBJECT_GUID_LAST = 7705300, 7705399
SPAWN_FIRST, SPAWN_LAST = 7704330, 7704399
TEXT_FIRST, TEXT_LAST = 7702600, 7702999
GAME_LAST = 700000                                  # the game's own creatures are below this

KEYS = ("WORDS", "COMPANION", "PLACES", "TALK", "QUESTS", "CREATURES", "SPAWNS", "HIDE", "OUTINGS", "LOOKS", "RELATIONS",
        "OBJECT_TEMPLATES", "OBJECTS", "FLAGS", "SPARED")
UNIT_FLAG_IMMUNE_TO_NPC = 0x200


def gather():
    lists = {k: [] for k in KEYS}
    gates, texts = {}, {}
    for name in CONTENT:
        if not os.path.exists(os.path.join(HERE, name + ".py")):
            continue
        module = importlib.import_module(name)
        for key in lists:
            lists[key].extend(getattr(module, key, []))
        for quest, groups in getattr(module, "GATES", {}).items():
            assert quest not in gates, f"two files gate quest {quest}"
            gates[quest] = groups
        for quest, cols in getattr(module, "TEXTS", {}).items():
            assert quest not in texts, f"two files change quest {quest}'s texts"
            texts[quest] = cols
    return lists, gates, texts


def conditions_rows(source_type, source_entry, source_id, groups, comment):
    rows = []
    for else_group, conds in enumerate(groups):
        for cond in conds:
            ctype, v1, v2, negative = (tuple(cond) + (0, 0, 0))[:4]
            rows.append(f"({source_type}, 0, {source_entry}, {source_id}, {else_group}, {ctype}, 0, {v1}, {v2}, 0, {negative}, 0, 0, '', "
                        f"{sql_text(comment)})")
    return rows


CONDITIONS_INSERT = ("INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, "
                     "`ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, "
                     "`ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES")


def write_companion(w, lists):
    w("INSERT INTO `remix_companion` (`id`, `side`, `zone`, `from_quest`, `until_quest`, `during_quest`, `comment`) VALUES")
    w(",\n".join(f"({i + 1}, {c['side']}, {c.get('zone', 0)}, {c.get('from', 0)}, {c.get('until', 0)}, {c.get('during', 0)}, "
                 f"{sql_text(c.get('why', ''))})" for i, c in enumerate(lists["COMPANION"])) + ";\n")
    if lists["PLACES"]:
        w("INSERT INTO `remix_place` (`quest`, `credit`, `map`, `x`, `y`, `radius`, `scene`, `text`) VALUES")
        w(",\n".join(f"({p['quest']}, {p['credit']}, {p.get('map', 571)}, {p['x']:.1f}, {p['y']:.1f}, {p.get('radius', 20):.1f}, "
                     f"{p.get('scene', 0)}, {sql_text(p.get('text', ''))})" for p in lists["PLACES"]) + ";\n")
    if lists["WORDS"]:
        rows, seqs = [], {}
        for entry in lists["WORDS"]:
            quest, moment, side, text = entry[:4]
            opts = entry[4] if len(entry) > 4 else {}
            key = (quest, moment, side)
            seqs[key] = seqs.get(key, 0) + 1
            rows.append(f"({quest}, {moment}, {side}, {seqs[key]}, {opts.get('speaker', MORATARI)}, {opts.get('delay', 3000)}, "
                        f"{opts.get('after', 0)}, {opts.get('before', 0)}, {opts.get('races', 0)}, {sql_text(text)})")
        w("INSERT INTO `remix_quest_whisper` (`quest`, `moment`, `side`, `seq`, `speaker`, `delay_ms`, `after_quest`, `before_quest`, `races`, "
          "`text`) VALUES")
        w(",\n".join(rows) + ";\n")


def write_talk(w, lists):
    """What can be said, and the replies (npc_text: the same words whoever asks; the client puts in $N,
    $R, $C and $G)."""
    texts_rows, rows, ids = [], [], {}
    for n, t in enumerate(lists["TALK"]):
        key = t.get("key", f"#{n}")
        assert key not in ids, f"two talk entries are {key}"
        ids[key] = 77001 + n
    order = {}
    for n, t in enumerate(lists["TALK"]):
        tid = ids[t.get("key", f"#{n}")]
        reply = 0
        if t.get("reply"):
            reply = TEXT_FIRST + len(texts_rows)
            assert reply <= TEXT_LAST, "out of NPC texts"
            texts_rows.append((reply, t["reply"]))
        parent = ids[t["parent"]] if t.get("parent") else 0
        order[(t["npc"], parent)] = order.get((t["npc"], parent), 0) + 1
        rows.append(f"({tid}, {t['npc']}, {parent}, {order[(t['npc'], parent)]}, {t.get('side', BOTH)}, {t.get('races', 0)}, "
                    f"{t.get('gender', 0)}, {t.get('quest', 0)}, {t.get('after', 0)}, {t.get('before', 0)}, {t.get('icon', ICON_CHAT)}, "
                    f"{sql_text(t['option'])}, {reply}, {t.get('credit', 0)}, {t.get('action', 0)}, {t.get('param', 0)})")
    w("INSERT INTO `remix_talk` (`id`, `npc`, `parent`, `ord`, `side`, `races`, `gender`, `quest`, `after_quest`, `before_quest`, `icon`, "
      "`option_text`, `reply`, `credit`, `action`, `param`) VALUES")
    w(",\n".join(rows) + ";\n")
    w(f"DELETE FROM `npc_text` WHERE `ID` BETWEEN {TEXT_FIRST} AND {TEXT_LAST};")
    if texts_rows:
        w("INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES")
        w(",\n".join(f"({i}, {sql_text(text)}, {sql_text(text)}, 1)" for i, text in texts_rows) + ";\n")
    # The war's own people spoken to who have nothing to say in the game (neither gossip nor quests:
    # the Warsong Captain on the wall) are given the gossip flag, their own flags kept the first time
    # and put back first each time.
    talkers = sorted({t["npc"] for t in lists["TALK"] if t["npc"] < GAME_LAST})
    w("""CREATE TABLE IF NOT EXISTS `remix_original_story_npcflag` (
  `entry` INT UNSIGNED NOT NULL,
  `npcflag` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
UPDATE `creature_template` c JOIN `remix_original_story_npcflag` o ON o.`entry` = c.`entry` SET c.`npcflag` = o.`npcflag`;
DELETE FROM `remix_original_story_npcflag`;""")
    if talkers:
        w("INSERT INTO `remix_original_story_npcflag` (`entry`, `npcflag`) SELECT `entry`, `npcflag` FROM `creature_template` "
          f"WHERE `entry` IN ({', '.join(map(str, talkers))}) AND (`npcflag` & 3) = 0;")
        w("UPDATE `creature_template` c JOIN `remix_original_story_npcflag` o ON o.`entry` = c.`entry` SET c.`npcflag` = c.`npcflag` | 1;")
    # The ones the fighting around them would kill before the Timerunner reaches them (the Warsong
    # Captain, under Ith'rix's assault on the south wall) no longer fight creatures, and so aren't
    # fought: the same keeping and putting back.
    spared = sorted({entry for entry, _ in lists["SPARED"]})
    assert all(entry < GAME_LAST for entry in spared), "SPARED is for the game's own creatures"
    w("""CREATE TABLE IF NOT EXISTS `remix_original_story_unit_flags` (
  `entry` INT UNSIGNED NOT NULL,
  `unit_flags` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
UPDATE `creature_template` c JOIN `remix_original_story_unit_flags` o ON o.`entry` = c.`entry` SET c.`unit_flags` = o.`unit_flags`;
DELETE FROM `remix_original_story_unit_flags`;""")
    if spared:
        w("INSERT INTO `remix_original_story_unit_flags` (`entry`, `unit_flags`) SELECT `entry`, `unit_flags` FROM `creature_template` "
          f"WHERE `entry` IN ({', '.join(map(str, spared))});")
        w("UPDATE `creature_template` c JOIN `remix_original_story_unit_flags` o ON o.`entry` = c.`entry` "
          f"SET c.`unit_flags` = c.`unit_flags` | {UNIT_FLAG_IMMUNE_TO_NPC};")
    w("")


def write_outings(w, lists):
    if lists["OUTINGS"]:
        w("INSERT INTO `remix_outing` (`id`, `map`, `x`, `y`, `z`, `o`, `scene`, `private`, `undress`, `back`, `flight_from`, `flight_to`, "
          "`mount`, `name`) VALUES")
        rows = []
        for o in lists["OUTINGS"]:
            flight = o.get("flight", (0, 0, 0))
            rows.append(f"({o['id']}, {o.get('map', 571)}, {o['x']:.2f}, {o['y']:.2f}, {o['z']:.2f}, {o.get('o', 0.0):.3f}, {o.get('scene', 0)}, "
                        f"{int(o.get('private', False))}, {int(o.get('undress', False))}, {int(o.get('back', True))}, {flight[0]}, {flight[1]}, "
                        f"{flight[2]}, {sql_text(o['name'])})")
        w(",\n".join(rows) + ";")
        lines = [(o["id"], at, text) for o in lists["OUTINGS"] for at, text in o.get("lines", [])]
        if lines:
            w("INSERT INTO `remix_outing_line` (`outing`, `at_ms`, `text`) VALUES")
            w(",\n".join(f"({i}, {at}, {sql_text(text)})" for i, at, text in lines) + ";")
        w("")
    if lists["LOOKS"]:
        looks = lists["LOOKS"]
        w("INSERT INTO `remix_look` (`display`, `from_display`, `extra`, `from_extra`, `bake`, `item1`, `item2`, `item3`, `item4`, `item5`, "
          "`item6`, `item7`, `item8`, `item9`, `item10`, `item11`) VALUES")
        w(",\n".join(f"({lk['display']}, {lk['from_display']}, {lk['extra']}, {lk['from_extra']}, {lk.get('bake', 0)}, "
                     + ", ".join(str(i) for i in lk["items"]) + ")" for lk in looks) + ";")
        # The server's own copy of the game's look tables, as the game's patch has them
        # (ClientPatch.cpp), so the server knows the new looks too.
        w(f"DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` IN ({', '.join(str(lk['display']) for lk in looks)});")
        w(f"DELETE FROM `creaturedisplayinfoextra_dbc` WHERE `ID` IN ({', '.join(str(lk['extra']) for lk in looks)});")
        w(f"DELETE FROM `creature_model_info` WHERE `DisplayID` IN ({', '.join(str(lk['display']) for lk in looks)});")
        for lk in looks:
            d, e = lk["server_display"], lk["server_extra"]
            w("INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, "
              "`CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, "
              "`BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES "
              f"({lk['display']}, {d['model']}, {d['sound']}, {lk['extra']}, {d['scale']}, {d['alpha']}, '', '', '', '', {d['blood_level']}, "
              f"{d['blood']}, {d['npc_sound']}, {d['particles']}, {d['geosets']}, {d['effects']});")
            w("INSERT INTO `creaturedisplayinfoextra_dbc` (`ID`, `DisplayRaceID`, `DisplaySexID`, `SkinID`, `FaceID`, `HairStyleID`, "
              "`HairColorID`, `FacialHairID`, `NPCItemDisplay1`, `NPCItemDisplay2`, `NPCItemDisplay3`, `NPCItemDisplay4`, `NPCItemDisplay5`, "
              "`NPCItemDisplay6`, `NPCItemDisplay7`, `NPCItemDisplay8`, `NPCItemDisplay9`, `NPCItemDisplay10`, `NPCItemDisplay11`, `Flags`, "
              "`BakeName`) VALUES "
              f"({lk['extra']}, {e['race']}, {e['sex']}, {e['skin']}, {e['face']}, {e['hair_style']}, {e['hair_color']}, {e['facial_hair']}, "
              + ", ".join(str(i) for i in lk["items"]) + f", {e['flags']}, '');")
            w("INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`, "
              f"`VerifiedBuild`) SELECT {lk['display']}, `BoundingRadius`, `CombatReach`, `Gender`, 0, 0 FROM `creature_model_info` "
              f"WHERE `DisplayID` = {lk['from_display']};")
        w("")


def write_creatures(w, lists):
    w(f"""-- The creatures this file owns ({CREATURE_FIRST} to {CREATURE_LAST}): credits never spawned, and copies of the game's.
DELETE FROM `creature_template` WHERE `entry` BETWEEN {CREATURE_FIRST} AND {CREATURE_LAST};
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {CREATURE_FIRST} AND {CREATURE_LAST};
DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN {CREATURE_FIRST} AND {CREATURE_LAST};
DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN {CREATURE_FIRST} AND {CREATURE_LAST};
DELETE FROM `creature_queststarter` WHERE `id` BETWEEN {CREATURE_FIRST} AND {CREATURE_LAST};
DELETE FROM `creature_questender` WHERE `id` BETWEEN {CREATURE_FIRST} AND {CREATURE_LAST};""")
    creatures = lists["CREATURES"]
    entries = [c["entry"] for c in creatures]
    assert len(set(entries)) == len(entries), "a creature twice"
    for c in creatures:
        assert CREATURE_FIRST <= c["entry"] <= CREATURE_LAST, c
    credits = [c for c in creatures if c.get("credit")]
    if credits:
        w("INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`, `speed_walk`, "
          "`speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`, `HealthModifier`, `DamageModifier`, "
          "`BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES")
        w(",\n".join(f"({c['entry']}, {sql_text(c['name'])}, NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, '')"
                     for c in credits) + ";")
        w("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES")
        w(",\n".join(f"({c['entry']}, 0, 19373, 1, 1, 0)" for c in credits) + ";\n")
    for c in creatures:
        if c.get("credit"):
            continue
        sets = [f"`entry` = {c['entry']}", "`KillCredit1` = 0", "`KillCredit2` = 0", f"`ScriptName` = {sql_text(c.get('script', ''))}",
                f"`AIName` = {sql_text(c.get('ai', ''))}", "`gossip_menu_id` = 0"]
        for col in ("name", "subname"):
            if col in c:
                sets.append(f"`{col}` = {sql_text(c[col]) if c[col] is not None else 'NULL'}")
        for col in ("npcflag", "faction", "unit_flags", "unit_flags2", "dynamicflags", "flags_extra", "minlevel", "maxlevel", "rank", "lootid",
                    "HealthModifier", "DamageModifier"):
            if col in c:
                sets.append(f"`{col}` = {c[col]}")
        tmp = f"remix_story_{c['entry']}"
        w(f"-- {c.get('why', c.get('name', ''))}")
        w(f"CREATE TEMPORARY TABLE `{tmp}` SELECT * FROM `creature_template` WHERE `entry` = {c['from']};")
        w(f"UPDATE `{tmp}` SET {', '.join(sets)};")
        w(f"INSERT INTO `creature_template` SELECT * FROM `{tmp}`;")
        w(f"DROP TEMPORARY TABLE `{tmp}`;")
        if c.get("display"):
            w("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) "
              f"VALUES ({c['entry']}, 0, {c['display']}, 1, 1, 0);")
        else:
            w("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) "
              f"SELECT {c['entry']}, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` "
              f"WHERE `CreatureID` = {c['from']};")
        if "auras" in c or "emote" in c or "stand" in c:
            w("INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) "
              f"VALUES ({c['entry']}, 0, 0, {c.get('stand', 0)}, 1, {c.get('emote', 0)}, 0, {sql_text(c.get('auras', ''))});")
        else:
            w("INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) "
              f"SELECT {c['entry']}, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` "
              f"WHERE `entry` = {c['from']};")
        w("INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) "
          f"SELECT {c['entry']}, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = {c['from']};")
    w("")


def write_objects(w, lists):
    import math
    w(f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {OBJECT_FIRST} AND {OBJECT_LAST};")
    w(f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {OBJECT_GUID_FIRST} AND {OBJECT_GUID_LAST};")
    if lists["OBJECT_TEMPLATES"]:
        w("INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`, `size`, `AIName`, "
          "`ScriptName`, `VerifiedBuild`) VALUES")
        w(",\n".join(f"({t['entry']}, 5, {t['display']}, {sql_text(t['name'])}, '', '', '', {t.get('size', 1.0)}, '', '', 0)"
                     for t in lists["OBJECT_TEMPLATES"]) + ";")
    if lists["OBJECTS"]:
        w("INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, "
          "`orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `ScriptName`, "
          "`VerifiedBuild`, `Comment`) VALUES")
        rows = []
        for g in lists["OBJECTS"]:
            assert OBJECT_GUID_FIRST <= g["guid"] <= OBJECT_GUID_LAST, g
            o = g.get("o", 0.0)
            rows.append(f"({g['guid']}, {g['entry']}, {g.get('map', 571)}, {g.get('zone', 0)}, 0, 1, {g.get('phase', 1)}, {g['x']:.2f}, {g['y']:.2f}, "
                        f"{g['z']:.2f}, {o:.4f}, 0, 0, {math.sin(o / 2):.6f}, {math.cos(o / 2):.6f}, 300, 100, 1, '', 0, "
                        f"{sql_text('Wrath Remix: ' + g.get('why', ''))})")
        w(",\n".join(rows) + ";")
    w("")


def write_spawns(w, lists):
    w(f"DELETE FROM `creature` WHERE `guid` BETWEEN {SPAWN_FIRST} AND {SPAWN_LAST};")
    w(f"DELETE FROM `creature_addon` WHERE `guid` BETWEEN {SPAWN_FIRST} AND {SPAWN_LAST};")
    spawns = lists["SPAWNS"]
    guids = [s["guid"] for s in spawns]
    assert len(set(guids)) == len(guids), "a spawn twice"
    if spawns:
        w("INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, "
          "`orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES")
        rows = []
        for s in spawns:
            assert SPAWN_FIRST <= s["guid"] <= SPAWN_LAST, s
            rows.append(f"({s['guid']}, {s['entry']}, {s.get('map', 571)}, 1, {s.get('phase', 1)}, {s.get('equip', 1)}, {s['x']:.2f}, {s['y']:.2f}, "
                        f"{s['z']:.2f}, {s.get('o', 0.0):.3f}, {s.get('respawn', 120)}, 0, 0, {sql_text('Wrath Remix: ' + s.get('why', ''))})")
        w(",\n".join(rows) + ";")
        addons = [s for s in spawns if "stand" in s or "emote" in s]
        if addons:
            w("INSERT INTO `creature_addon` (`guid`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES")
            w(",\n".join(f"({s['guid']}, 0, 0, {s.get('stand', 0)}, 1, {s.get('emote', 0)}, 0, '')" for s in addons) + ";")
    hidden = lists["HIDE"]
    w("""-- Who is seen (type 30, a spawn's own conditions by its guid): this file's spawns, and the game's that
-- some Timerunners no longer see. Quest states: 1 not taken, 2 objectives done, 8 in progress, 64 turned in.""")
    hide_guids = [h["guid"] for h in hidden]
    w(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND (`SourceId` BETWEEN {SPAWN_FIRST} AND {SPAWN_LAST}"
      + (f" OR `SourceId` IN ({', '.join(str(g) for g in hide_guids)})" if hide_guids else "") + ");")
    rows = []
    for s in spawns:
        if s.get("visible"):
            rows += conditions_rows(30, s["entry"], s["guid"], s["visible"], "Wrath Remix: " + s.get("why", ""))
    for h in hidden:
        rows += conditions_rows(30, h["entry"], h["guid"], h["visible"], "Wrath Remix: " + h.get("why", ""))
    if rows:
        w(CONDITIONS_INSERT)
        w(",\n".join(rows) + ";\n")


def write_quests(w, lists, gates):
    quests = lists["QUESTS"]
    qids = [q["id"] for q in quests]
    assert len(set(qids)) == len(qids), "a quest twice"
    if quests:
        idlist = ", ".join(str(i) for i in qids)
        for table in ("quest_template", "quest_template_addon", "quest_offer_reward", "quest_request_items"):
            w(f"DELETE FROM `{table}` WHERE `ID` IN ({idlist});")
        for table in ("creature_queststarter", "creature_questender"):
            w(f"DELETE FROM `{table}` WHERE `quest` IN ({idlist});")
        for table in ("remix_departure", "remix_bridge", "remix_quest_reward"):
            w(f"DELETE FROM `{table}` WHERE `quest` IN ({idlist});")
        w("INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, "
          "`Flags`, `AllowableRaces`, `StartItem`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`, "
          "`RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, "
          "`RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`, `ObjectiveText4`, "
          "`RequiredItemId1`, `RequiredItemCount1`, `VerifiedBuild`) VALUES")
        rows = []
        for q in quests:
            objs = list(q.get("objectives", []))
            assert len(objs) <= 4, q["id"]
            objs += [(0, 0, "")] * (4 - len(objs))
            races = {BOTH: 0, ALLIANCE: ALLIANCE_RACES, HORDE: HORDE_RACES}[q.get("side", BOTH)]
            item, count = (q.get("items") or [(0, 0)])[0]
            rows.append(f"({q['id']}, 2, {q.get('level', -1)}, {q.get('min', 10)}, {q.get('sort', 0)}, 5, 0, {q.get('flags', 0)}, {races}, "
                        f"{q.get('start_item', 0)}, {sql_text(q['title'])}, {sql_text(q['log'])}, {sql_text(q['desc'])}, "
                        f"{sql_text(q.get('done', ''))}, " + ", ".join(f"{e}, {n}" for e, n, _ in objs) + ", "
                        + ", ".join(sql_text(t) for _, _, t in objs) + f", {item}, {count}, 0)")
        w(",\n".join(rows) + ";")
        w("INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `NextQuestID`, `ExclusiveGroup`) VALUES")
        w(",\n".join(f"({q['id']}, {q.get('prev', 0)}, {q.get('next', 0)}, {q.get('excl', 0)})" for q in quests) + ";")
        w("INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES")
        w(",\n".join(f"({q['id']}, {sql_text(q['reward'])}, 0)" for q in quests) + ";")
        requests = [q for q in quests if q.get("request")]
        if requests:
            w("INSERT INTO `quest_request_items` (`ID`, `CompletionText`, `VerifiedBuild`) VALUES")
            w(",\n".join(f"({q['id']}, {sql_text(q['request'])}, 0)" for q in requests) + ";")
        for table, key in (("creature_queststarter", "giver"), ("creature_questender", "ender")):
            pairs = []
            for q in quests:
                who = q.get(key, MORATARI)
                for entry in (who if isinstance(who, (list, tuple)) else [who]):
                    pairs.append(f"({entry}, {q['id']})")
            w(f"INSERT INTO `{table}` (`id`, `quest`) VALUES " + ", ".join(pairs) + ";")
        departures = [q for q in quests if q.get("departure")]
        if departures:
            w("INSERT INTO `remix_departure` (`quest`, `map`, `x`, `y`, `z`, `o`) VALUES")
            w(",\n".join(f"({q['id']}, {q['departure'][0]}, {q['departure'][1]:.2f}, {q['departure'][2]:.2f}, {q['departure'][3]:.2f}, "
                         f"{q['departure'][4]:.3f})" for q in departures) + ";")
        bridges = [q for q in quests if q.get("bridge")]
        if bridges:
            w("INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES")
            w(",\n".join(f"({q['id']}, {q['bridge'].get('next', 0)}, {q['bridge'].get('chapter', 0)}, {q['bridge']['at'][0]}, "
                         f"{q['bridge']['at'][1]:.2f}, {q['bridge']['at'][2]:.2f}, {q['bridge']['at'][3]:.2f}, {q['bridge']['at'][4]:.3f}, "
                         f"{sql_text(q['bridge'].get('skipped', ''))})" for q in bridges) + ";")
        bronze = [q for q in quests if "bronze" in q]
        if bronze:
            w("INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES " + ", ".join(f"({q['id']}, {q['bronze']})" for q in bronze) + ";")
        w("")
    # Quest gates (type 19): this file's quests, and the game's it places in the story.
    all_gates = dict(gates)
    for q in quests:
        if q.get("gates"):
            assert q["id"] not in all_gates
            all_gates[q["id"]] = q["gates"]
    if all_gates:
        w(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN ({', '.join(str(i) for i in sorted(all_gates))});")
        rows = []
        for quest, groups in sorted(all_gates.items()):
            rows += conditions_rows(19, quest, 0, groups, f"Wrath Remix: quest {quest} in the story")
        w(CONDITIONS_INSERT)
        w(",\n".join(rows) + ";\n")
    # The game's quests some of this file's creatures give or take back (a living William Allerton).
    for kind, table in (("starter", "creature_queststarter"), ("ender", "creature_questender")):
        pairs = [(e, q) for k, e, q in lists["RELATIONS"] if k == kind]
        if pairs:
            w(f"INSERT INTO `{table}` (`id`, `quest`) VALUES " + ", ".join(f"({e}, {q})" for e, q in pairs) + ";")
    return all_gates


def write_texts(w, texts):
    w("""-- The game's quests' texts this file changes, from their originals (kept the first time, and put
-- back first each time, so a text dropped from here is the game's again).
CREATE TABLE IF NOT EXISTS `remix_original_story_text` (
  `quest` INT UNSIGNED NOT NULL,
  `col` VARCHAR(16) NOT NULL,                     -- desc, log, done, reward, request
  `text` TEXT NULL,                               -- NULL: the quest had no such row
  PRIMARY KEY (`quest`, `col`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
UPDATE `quest_template` q JOIN `remix_original_story_text` o ON o.`quest` = q.`ID` AND o.`col` = 'desc' SET q.`QuestDescription` = o.`text`;
UPDATE `quest_template` q JOIN `remix_original_story_text` o ON o.`quest` = q.`ID` AND o.`col` = 'log' SET q.`LogDescription` = o.`text`;
UPDATE `quest_template` q JOIN `remix_original_story_text` o ON o.`quest` = q.`ID` AND o.`col` = 'done' SET q.`QuestCompletionLog` = o.`text`;
UPDATE `quest_offer_reward` r JOIN `remix_original_story_text` o ON o.`quest` = r.`ID` AND o.`col` = 'reward' SET r.`RewardText` = o.`text` WHERE o.`text` IS NOT NULL;
DELETE r FROM `quest_offer_reward` r JOIN `remix_original_story_text` o ON o.`quest` = r.`ID` AND o.`col` = 'reward' WHERE o.`text` IS NULL;
UPDATE `quest_request_items` i JOIN `remix_original_story_text` o ON o.`quest` = i.`ID` AND o.`col` = 'request' SET i.`CompletionText` = o.`text` WHERE o.`text` IS NOT NULL;
DELETE i FROM `quest_request_items` i JOIN `remix_original_story_text` o ON o.`quest` = i.`ID` AND o.`col` = 'request' WHERE o.`text` IS NULL;
DELETE FROM `remix_original_story_text`;""")
    columns = {"desc": ("quest_template", "QuestDescription"), "log": ("quest_template", "LogDescription"),
               "done": ("quest_template", "QuestCompletionLog"), "reward": ("quest_offer_reward", "RewardText"),
               "request": ("quest_request_items", "CompletionText")}
    for quest, cols in sorted(texts.items()):
        for col, new in cols.items():
            table, column = columns[col]
            w(f"INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT {quest}, '{col}', "
              f"(SELECT `{column}` FROM `{table}` WHERE `ID` = {quest});")
            if table == "quest_template":
                w(f"UPDATE `quest_template` SET `{column}` = {sql_text(new)} WHERE `ID` = {quest};")
            else:
                w(f"INSERT INTO `{table}` (`ID`, `{column}`, `VerifiedBuild`) VALUES ({quest}, {sql_text(new)}, 0) "
                  f"ON DUPLICATE KEY UPDATE `{column}` = VALUES(`{column}`);")
    w("")


def main():
    lists, gates, texts = gather()
    out = []
    w = out.append
    w("""-- Moratari's part in the war (STORY.md, "Moratari in the war"), written by tools/story.py from the
-- story_*.py files and romance.py: edit those and run it again. Her words on the game's quests, where
-- she walks with the Timerunner, what can be said to her and to the war's own people, the
-- interventions before the turn and their undoing after it, and the romance (RemixMoratari.cpp,
-- RemixOutings.cpp). This file owns: creatures 770500-770999, spawns 7704330-7704399, NPC texts
-- 7702600-7702999, its quests, the conditions on the quests it gates, the texts it changes, the gossip
-- flag of the game's creatures it gives something to say, the unit flags of those it spares.
""")
    w(SCHEMA)
    write_companion(w, lists)
    write_talk(w, lists)
    write_outings(w, lists)
    write_creatures(w, lists)
    write_spawns(w, lists)
    write_objects(w, lists)
    all_gates = write_quests(w, lists, gates)
    write_texts(w, texts)
    flags = [(QUEST_FLAG_ALONE, "Walking Alone", "Moratari waits at her posts while you walk alone.")] + lists["FLAGS"]
    w(f"""-- Never offered: flags, "rewarded" while they hold (RemixMoratari.cpp): the Timerunner has asked Moratari to
-- wait, and the others the content files name.
DELETE FROM `quest_template` WHERE `ID` IN ({', '.join(str(f[0]) for f in flags)});
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `LogTitle`, `LogDescription`, `QuestDescription`, `VerifiedBuild`) VALUES""")
    w(",\n".join(f"({quest}, 2, 1, 1, 0, 0, {sql_text(title)}, '', {sql_text(meaning)}, 0)" for quest, title, meaning in flags) + ";\n")
    path = os.path.join(HERE, "..", "data", "sql", "remix", "world", "wrath_remix_world_0027_moratari.sql")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print(f"story: {len(lists['QUESTS'])} quests, {len(lists['WORDS'])} lines of Moratari's, {len(lists['TALK'])} things to say, "
          f"{len(lists['SPAWNS'])} spawns, {len(lists['CREATURES'])} creatures, {len(all_gates)} gated quests, {len(texts)} texts changed")


SCHEMA = """DROP TABLE IF EXISTS `remix_quest_whisper`;
CREATE TABLE `remix_quest_whisper` (
  `quest` INT UNSIGNED NOT NULL,
  `moment` TINYINT UNSIGNED NOT NULL,             -- 1 taken, 2 its objectives done, 3 turned in
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,     -- 0 both, 1 Alliance, 2 Horde
  `seq` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `speaker` INT UNSIGNED NOT NULL DEFAULT 770001,
  `delay_ms` INT UNSIGNED NOT NULL DEFAULT 3000,  -- after the line before it
  `after_quest` INT UNSIGNED NOT NULL DEFAULT 0,  -- said only once this is turned in
  `before_quest` INT UNSIGNED NOT NULL DEFAULT 0, -- said only until this is turned in
  `races` INT UNSIGNED NOT NULL DEFAULT 0,        -- a race mask (0: any)
  `text` TEXT NOT NULL,
  PRIMARY KEY (`quest`, `moment`, `side`, `seq`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_companion`;
CREATE TABLE `remix_companion` (
  `id` INT UNSIGNED NOT NULL,
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `zone` INT UNSIGNED NOT NULL DEFAULT 0,          -- 0: anywhere
  `from_quest` INT UNSIGNED NOT NULL DEFAULT 0,    -- turned in (0: from the start)
  `until_quest` INT UNSIGNED NOT NULL DEFAULT 0,   -- turned in ends it (0: never)
  `during_quest` INT UNSIGNED NOT NULL DEFAULT 0,  -- in the log (0: any time)
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_place`;
CREATE TABLE `remix_place` (
  `quest` INT UNSIGNED NOT NULL,
  `credit` INT UNSIGNED NOT NULL,                  -- given as they come within the radius
  `map` INT UNSIGNED NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `radius` FLOAT NOT NULL DEFAULT 20,
  `scene` INT UNSIGNED NOT NULL DEFAULT 0,         -- played there instead (its end gives the credit)
  `text` TEXT NOT NULL,                            -- Moratari's words there ('' for none)
  PRIMARY KEY (`quest`, `credit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_outing`;
CREATE TABLE `remix_outing` (
  `id` INT UNSIGNED NOT NULL,
  `map` INT UNSIGNED NOT NULL,
  `x` FLOAT NOT NULL, `y` FLOAT NOT NULL, `z` FLOAT NOT NULL, `o` FLOAT NOT NULL,
  `scene` INT UNSIGNED NOT NULL DEFAULT 0,          -- played there (remix_scene)
  `private` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- in a phase of its own
  `undress` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- the Timerunner's gear unseen while it lasts
  `back` TINYINT UNSIGNED NOT NULL DEFAULT 1,       -- back where they were after
  `flight_from` INT UNSIGNED NOT NULL DEFAULT 0,    -- a flight on her: from this flight point (at x y z)
  `flight_to` INT UNSIGNED NOT NULL DEFAULT 0,
  `mount` INT UNSIGNED NOT NULL DEFAULT 0,          -- her shape under them
  `name` VARCHAR(120) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_outing_line`;
CREATE TABLE `remix_outing_line` (
  `outing` INT UNSIGNED NOT NULL,
  `at_ms` INT UNSIGNED NOT NULL,                    -- after the flight starts
  `text` TEXT NOT NULL,
  PRIMARY KEY (`outing`, `at_ms`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_look`;
CREATE TABLE `remix_look` (
  `display` INT UNSIGNED NOT NULL,                  -- the new look (CreatureDisplayInfo)
  `from_display` INT UNSIGNED NOT NULL,             -- copied from
  `extra` INT UNSIGNED NOT NULL,                    -- its clothes (CreatureDisplayInfoExtra)
  `from_extra` INT UNSIGNED NOT NULL,               -- copied from
  `bake` TINYINT UNSIGNED NOT NULL DEFAULT 0,       -- keep the copied look's baked texture (0: dressed from its items)
  `item1` INT UNSIGNED NOT NULL DEFAULT 0, `item2` INT UNSIGNED NOT NULL DEFAULT 0, `item3` INT UNSIGNED NOT NULL DEFAULT 0,
  `item4` INT UNSIGNED NOT NULL DEFAULT 0, `item5` INT UNSIGNED NOT NULL DEFAULT 0, `item6` INT UNSIGNED NOT NULL DEFAULT 0,
  `item7` INT UNSIGNED NOT NULL DEFAULT 0, `item8` INT UNSIGNED NOT NULL DEFAULT 0, `item9` INT UNSIGNED NOT NULL DEFAULT 0,
  `item10` INT UNSIGNED NOT NULL DEFAULT 0, `item11` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`display`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_talk`;
CREATE TABLE `remix_talk` (
  `id` INT UNSIGNED NOT NULL,
  `npc` INT UNSIGNED NOT NULL,                     -- the creature it's said to
  `parent` INT UNSIGNED NOT NULL DEFAULT 0,        -- 0: in its first menu; else after that entry's reply
  `ord` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `races` INT UNSIGNED NOT NULL DEFAULT 0,
  `gender` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- 0 any, 1 male, 2 female
  `quest` INT UNSIGNED NOT NULL DEFAULT 0,         -- only while this is in the log, unfinished
  `after_quest` INT UNSIGNED NOT NULL DEFAULT 0,
  `before_quest` INT UNSIGNED NOT NULL DEFAULT 0,
  `icon` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `option_text` VARCHAR(255) NOT NULL,
  `reply` INT UNSIGNED NOT NULL DEFAULT 0,         -- npc_text (0: the menu closes)
  `credit` INT UNSIGNED NOT NULL DEFAULT 0,        -- a quest's credit, given as it's said
  `action` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- 1 scene [param], 2 close, 3 she waits, 4 she comes, 5 outing [param]
  `param` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


if __name__ == "__main__":
    main()
