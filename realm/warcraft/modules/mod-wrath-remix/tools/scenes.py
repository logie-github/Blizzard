#!/usr/bin/env python3
"""Writes Wrath Remix's scenes (STORY.md) as the world database's remix_scene and remix_scene_step:
data/sql/remix/world/wrath_remix_world_0014_scenes.sql.

    python3 tools/scenes.py

A scene is a list of steps, played for one Timerunner (RemixScenes.cpp): who is in it (people
summoned where the scene stands, or bound to the people already there), what they say (each line
is given time to be read: about 15 letters a second, at least four seconds), where they walk, what
they do. Positions are yards forward and to the left of the scene's anchor, as it faces; a facing
is added to the anchor's (pi: facing back the way it looks).
"""
import importlib
import math
import os
import sys

ACCEPT, REWARD = 1, 2

# The people (wrath_remix_world_0002_npcs.sql)
MORATARI, ETERNUS, ANDORMU, NOZARI = 770001, 770002, 770003, 770004
SYLVANAS, ALLERIA = 770011, 770012                       # at the Bazaar, as themselves
SYLVANAS_ABROAD, ALLERIA_ABROAD = 770014, 770015         # anywhere else, as two rangers
ACT_MORATARI = 770013
ACT_SYLVANAS, ACT_ALLERIA, ACT_ETERNUS, ACT_THORIM, ACT_SIF = 770051, 770052, 770053, 770054, 770055
THORIM_TERRACE = 30295
HIEROPHANT_THAYREEN, WINDSEER_GRAYHORN = 27295, 27262
# A scene's credit, given at its end to the scene's own quest alone (RemixScenes.cpp: another quest
# in the log asking for it doesn't get it), and the reason one cut short plays again at its anchor.
# Back to Your Own Time's is given by the way home too (RemixEnding.cpp).
SCENE_CREDIT = 770035
PLAYER = 255

SPELL_TELEPORT_VISUAL = 51347
SPELL_TIME_RIFT_CHANNEL = 31387
SPELL_TRANSPARENCY = 44816
EMOTE_TALK, EMOTE_BOW, EMOTE_POINT, EMOTE_NO, EMOTE_KNEEL = 1, 2, 25, 274, 16

ACTIONS = dict(summon=1, bind=2, move=3, say=4, yell=5, emote=6, cast=7, face=8, despawn=9, credit=10, sound=11,
               stand=12, text_emote=13, teleport=14, movie=15, cinematic=16, aura=17, remove_aura=18, whisper=19,
               face_angle=20, home=21, fade=22)


def say(actor, text):
    return ("say", actor, text)


def voiced(actor, text, seconds):
    """A line said in the game's own recording of it (tools/voices.py): the scene gives it as long as
    the recording runs, if that's longer than the time to read it."""
    extra = int(seconds * 1000) + 400 - max(4000, int(len(text) * 1000 / 15))   # (reading_time's, below)
    return [say(actor, text)] + ([("wait", extra)] if extra > 0 else [])


def scene(id, name, quest, trigger, anchor, steps, credit=0):
    return dict(id=id, name=name, quest=quest, trigger=trigger, anchor=anchor, credit=credit, steps=steps)


BACK = math.pi  # facing the way the anchor's eyes look from, i.e. towards it

SCENES = [
    # ---- Chapter III ----------------------------------------------------------------------------
    *[scene(sid, "The Hollow Crown: Alleria, as it is taken", quest, ACCEPT, ALLERIA_ABROAD, [
        ("bind", 1, ALLERIA_ABROAD),
        ("face", 1, PLAYER),
        say(1, "There is something under these hills, Timerunner. I felt it the moment the bronze set me down: a voice, so low you could take it for the wind."),
        say(1, "Eternus sees only the bear: a god driven mad, and to her that is a wound. Wind it back far enough, and the bear is whole again."),
        say(1, "But the madness is not a wound. It is a whisper, and whispers do not care what year it is. Turn Ursoc back, and it finds another ear. A druid's. A child's. Yours."),
        say(1, "I know this voice, or one of its cousins. I have had one in my own head for years, and it is poor company."),
        say(1, "Go and break her anchors. I will meet you at the den. If you are late, I will come looking, and you will not enjoy being found."),
    ]) for sid, quest in ((301, 77303), (302, 77313))],
    *[scene(sid, "Ursoc at peace: Alleria beside the Bear God's quest giver", quest, REWARD, giver, [
        ("summon", 1, ACT_ALLERIA, 2.0, -3.0, 0.0),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1500),
        ("face", 1, PLAYER),
        say(1, "He is at peace now. The voice is not. It runs far deeper than that tree's roots ever reached."),
        say(1, "You will hear it again at the bottom of Ulduar. ...You may. I cannot know that. When you reach the Storm Peaks, listen for it, and send me word."),
        say(1, "I want to know where it is. That is all. Do not read anything into it."),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1000),
        ("despawn", 1),
    ]) for sid, quest, giver in ((303, 12249, HIEROPHANT_THAYREEN), (304, 12236, WINDSEER_GRAYHORN))],
    scene(305, "A Friend of Questionable Judgment: Sylvanas at Drak'Tharon's door", 77302, ACCEPT, MORATARI, [
        ("summon", 1, ACT_SYLVANAS, 1.0, -3.0, 0.0),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1500),
        ("face", 1, PLAYER),
        say(1, "So this is Drakuru's errand: his own people, killed for him by a stranger he calls friend."),
        say(1, "I know the kind of gratitude he has in mind. I have shown it myself. Climb his keep for him, Timerunner. Only do not stand with your back to him."),
        say(1, "You never did listen to me about trolls. ...Go."),
        ("cast", 1, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1000),
        ("despawn", 1),
    ]),
    # ---- Chapter IV -----------------------------------------------------------------------------
    scene(401, "One Life Too Many: Sylvanas beneath Voltarus", 77405, ACCEPT, SYLVANAS_ABROAD, [
        ("bind", 1, SYLVANAS_ABROAD),
        ("face", 1, PLAYER),
        say(1, "Drakuru's. The troll who sold his own people to the Scourge for a little borrowed power. Eternus's agents are under Voltarus, opening a door to carry him out of history before his master comes for him."),
        say(1, "Here is what happens if they succeed. The Lich King comes to Voltarus for a traitor and finds no one. He never sees you. He never decides that you are worth keeping for the end."),
        say(1, "And the Frozen Throne waits on that decision."),
        say(1, "I served a king of ice once, because he left me no choice. Years later I knelt to a worse master, by choice, and called it freedom. Let the troll keep the price he agreed to."),
    ]),
    # ---- Chapter V: Moratari's ----------------------------------------------------------------------
    scene(501, "Stolen Hours: Eternus comes for Moratari", 77502, REWARD, MORATARI, [
        ("bind", 1, MORATARI),
        ("summon", 2, ACT_ETERNUS, 7.0, 1.0, BACK),
        ("cast", 2, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 2000),
        say(2, "Moratari."),
        ("face", 1, 2),
        say(1, "You should not be here."),
        say(2, "Neither should you. And yet here we both are, in a garden the titans built so that nothing living in it would ever be lost. They wanted what I want, Moratari. They simply had more time."),
        say(1, "Your siphons were drinking the Makers' pillar dry. No one needs that many hours unless she means to hold one still."),
        say(2, "One hour. Only one. The hour the Lich King falls."),
        say(1, "Why that one?"),
        say(2, "Because it is the keystone. Until it is set, every hour of this war is still sand, and sand can be shaped. Once it is set, every grave in Northrend is stone."),
        say(2, "I would keep it from setting long enough to go back. Grave by grave. Name by name."),
        say(1, "And the arch comes down on everyone standing under it."),
        say(2, "I would catch them."),
        say(1, "No one can catch a world, Eternus. Not even you."),
        say(2, "Come home, Moratari. You kept my records for ten thousand years. You know every name I want to save. Help me save them."),
        say(1, "I kept your records. That is exactly why I can't."),
        say(2, "Then I will remember them for both of us."),
        ("cast", 2, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1200),
        ("despawn", 2),
        ("wait", 2500),
        ("face", 1, PLAYER),
        say(1, "She was kind to me, $n, when no one else in my flight was. I hope you never have to choose between a kindness and the truth. I have now done it twice."),
    ]),
    # ---- Chapter VI: Eternus's grief ------------------------------------------------------------------
    scene(601, "A Gift of Grief: Eternus before Thorim", 77602, REWARD, MORATARI, [
        ("bind", 1, MORATARI),
        ("bind", 2, THORIM_TERRACE),
        ("summon", 3, ACT_ETERNUS, 10.0, 3.0, BACK),
        ("summon", 4, ACT_SIF, 8.0, -2.0, BACK),
        ("aura", 4, SPELL_TRANSPARENCY),
        ("cast", 3, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 2000),
        ("face", 3, 2),
        say(3, "Stormlord. I know what your brother took from you, and I can give it back. Not another vision: her, as she was, before he struck."),
        ("face", 2, 4),
        ("wait", 2500),
        say(2, "My brother gave me a story once. Arngrim, he said. Arngrim killed her. I believed him, because I wanted a name to hate, and I killed a good king for his lie."),
        ("face", 2, 3),
        say(2, "I have seen her a hundred times since she died, and every time it was a lie. I will not be lied to with her face again. Not by Loken. Not by you."),
        say(3, "It is no lie. It is a kindness."),
        say(2, "My brother called it that, too."),
        ("summon", 5, ACT_ALLERIA, 3.0, 4.0, 0.0),
        ("cast", 5, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1500),
        ("face", 5, 3),
        say(5, "Listen to him, dragon. Grief you lie to does not heal. It waits for the next liar."),
        say(5, "And there is something under these mountains that has fed on grief since the titans chained it there. It is listening to you right now."),
        ("wait", 2500),
        say(3, "...Keep your grief, Stormlord. I will keep mine."),
        ("cast", 4, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 800),
        ("despawn", 4),
        ("cast", 3, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1200),
        ("despawn", 3),
        ("wait", 2000),
        ("face", 2, PLAYER),
        say(2, "Whoever that was, she carries a grief like mine. I know the look of it. Come, little friend. My brother has much to answer for."),
        ("face", 5, PLAYER),
        say(5, "That was meant for you as much as for him. Whatever you were toasting when the bronze found you, do not let anyone sell it back to you."),
        say(5, "...As a matter of policy. Go on."),
        ("cast", 5, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1000),
        ("despawn", 5),
    ]),
    # ---- Chapter VII --------------------------------------------------------------------------------
    scene(701, "What He Was Offered: Eternus after Bridenbrad", 77702, ACCEPT, MORATARI, [
        ("bind", 1, MORATARI),
        ("wait", 2000),
        ("summon", 2, ACT_ETERNUS, 6.0, 2.0, BACK),
        ("cast", 2, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 2000),
        ("face", 2, PLAYER),
        say(2, "I went to him before the naaru did. I thought: here is one I can save without breaking anything. One paladin, dying in the snow. History would not miss a single tabard."),
        say(2, "I offered him a hundred years. Whole, and out of the plague's reach. He asked me if the Light would be in them."),
        say(2, "I could not lie to him. He thanked me, and he asked me to go, and he waited for the naaru."),
        say(2, "Tell me, Timerunner. Why is it always the ones who most deserve saving who will not let me?"),
        ("face", 1, 2),
        say(1, "Because they have already decided what their lives are for, Eternus. Did you ever once ask them?"),
        ("wait", 2000),
        say(2, "...No. I suppose I never did."),
        ("cast", 2, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 1200),
        ("despawn", 2),
    ], credit=SCENE_CREDIT),
    *[scene(sid, "The Armies Are in Place: Sylvanas before the Frozen Halls", quest, ACCEPT, SYLVANAS, [
        ("bind", 1, SYLVANAS),
        ("bind", 2, ALLERIA),
        ("face", 1, PLAYER),
        say(1, "The Frozen Halls. The last time I was there, I stood close enough to touch the blade that killed me."),
        *mid,
        ("face", 2, 1),
        say(2, "You don't have to go anywhere near it, sister."),
        ("face", 1, 2),
        say(1, "I have no intention of it. Once was enough. If she sees me..."),
        ("face", 1, PLAYER),
        say(1, "Uther waits in those halls, or what is left of him. He will tell you what the Lich King is for. Believe him. It will cost you nothing. It cost me everything to learn it."),
        say(1, "Go, $n. And do not let Arthas talk to you for long. He is very good at it."),
        ("face", 2, PLAYER),
        say(2, "She means be careful."),
        say(2, "So do I. A little. Go, before I say something foolish."),
    ], credit=SCENE_CREDIT) for sid, quest, mid in (
        (7011, 77701, [
            say(1, "Jaina Proudmoore will lead you in. On the Horde's side of that day, it was me. We went in for different reasons, she and I. She hoped there was something left of him to save. I wanted there to be nothing left of him at all. We both came out running."),
        ]),
        (7111, 77711, [
            say(1, "You will meet me in there: the Banshee Queen, as I was. She will lead you through the forge and into his halls."),
            say(1, "And when she finally stands before him, she will hate him with everything she has left. And then she will run."),
            say(1, "She will not know you. To her you will be one more champion of the Horde. Do not hold it against her. You have not happened to her yet."),
        ]),
    )],
    # ---- The end ------------------------------------------------------------------------------------
    scene(800, "The return: everyone at the Bazaar", 0, 0, MORATARI, [
        ("bind", 1, MORATARI),
        ("bind", 2, ANDORMU),
        ("bind", 3, NOZARI),
        ("bind", 4, SYLVANAS),
        ("bind", 5, ALLERIA),
        ("wait", 2500),
        ("face", 2, PLAYER),
        say(2, "The last hour came as it must. The sacrifices are neither erased nor forgotten."),
        ("face", 3, PLAYER),
        say(3, "Bolvar Fordragon sits the Frozen Throne, and every page of the record agrees. I have checked it twice."),
        ("face", 4, PLAYER),
        say(4, "He is gone. I have imagined saying those words since the day he killed me. They are quieter than I thought they would be."),
        ("face", 5, PLAYER),
        say(5, "Welcome back, Timerunner. You took your time. Not that anyone was counting."),
        ("face", 1, PLAYER),
        say(1, "Come and see me when you are ready. There is one more thing we have to talk about."),
    ]),
    scene(802, "Back to Your Own Time: the memories, and home", 77802, ACCEPT, MORATARI, [
        ("bind", 1, MORATARI),
        ("bind", 2, SYLVANAS),
        ("bind", 3, ALLERIA),
        ("face", 1, PLAYER),
        say(1, "This is the part I have been dreading."),
        ("face", 1, 2),
        say(1, "Sylvanas. Alleria. You know what I have to do."),
        ("face", 3, 1),
        say(3, "We know. Time is not fond of people who remember too much of it."),
        ("face", 2, 1),
        say(2, "Be quick about it, Moratari. I have had enough long goodbyes for one eternity."),
        ("face", 2, PLAYER),
        say(2, "$n. Whatever I become, whatever they say of me where you are going: you saw this. Keep it for me."),
        say(2, "And when we meet, the way we are meant to, do not tell me any of this. Let me find you the long way."),
        ("face", 3, PLAYER),
        say(3, "And if you meet my son... no. Tell him nothing. He will find us on his own."),
        say(3, "And you, $n. You heard me the first time. I will see you in the future. Do not be late."),
        ("cast", 1, SPELL_TIME_RIFT_CHANNEL, 2),
        ("wait", 2500),
        ("cast", 1, SPELL_TIME_RIFT_CHANNEL, 3),
        ("wait", 3500),
        say(3, "...Strange. I had the oddest feeling I was about to say goodbye to someone."),
        say(2, "Chromie. Take us home. Wherever this is, I do not like it."),
        ("cast", 2, SPELL_TELEPORT_VISUAL, 0),
        ("cast", 3, SPELL_TELEPORT_VISUAL, 0),
        ("wait", 2500),
        ("face", 1, PLAYER),
        say(1, "They will wake in their own times with nothing but a feeling they cannot name. It is the kindest thing I know how to do."),
        say(1, "Now you. Hold still. Northrend stays with you: the war, the echoes, the two of them. What they told you of your own years ahead does not."),
        ("cast", 1, SPELL_TIME_RIFT_CHANNEL, PLAYER),
        ("wait", 4000),
        say(1, "There. You go home knowing no more of what is coming than anyone else at that table. It is the only fair way to go."),
        # (her farewell in her own voice: Legion Remix's, tools/voices.py)
        *voiced(1, "This has been quite the experiment, hasn't it? Now the sands of time slip through the hourglass, waiting to be turned over again.", 8.74),
        *voiced(1, "The strange thing about traveling through time is that goodbyes and hellos tend to blur together. It can be hard to tell them apart.", 8.06),
        *voiced(1, "And yet, they are, in their own way, so distinct from one another. I wonder why that is. Perhaps they deserve their own experiment.", 8.33),
        *voiced(1, "Well, if I ever decide to pursue it, I'd be thrilled to have you as an assistant. Then this goodbye would blur into a hello as well.", 8.75),
        say(1, "But I will remember. Goodbye, Timerunner. Go home."),
        *voiced(1, "I will create a portal for you now.", 1.78),
        ("cast", 1, SPELL_TELEPORT_VISUAL, PLAYER),
        ("wait", 2500),
        ("home",),
    ], credit=SCENE_CREDIT),
]


def reading_time(text):
    return max(4000, int(len(text) * 1000 / 15))


def sql_text(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


# Moratari's part in the war (tools/story_*.py, romance.py) has scenes of its own: written here too.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for _name in ("story_borean_alliance", "story_borean_horde", "story_dragonblight", "story_undo", "romance"):
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), _name + ".py")):
        SCENES += [dict({"credit": 0}, **_s) for _s in getattr(importlib.import_module(_name), "SCENES", [])]


def main():
    rows, steps = [], []
    seen = set()
    for s in SCENES:
        assert s["id"] not in seen, f"scene {s['id']} twice"
        seen.add(s["id"])
    for s in SCENES:
        rows.append(f"({s['id']}, {s['quest']}, {s['trigger']}, {s['anchor']}, {s['credit']}, {sql_text(s['name'])})")
        at, n = 500, 0
        for step in s["steps"]:
            kind = step[0]
            if kind == "wait":
                at += step[1]
                continue
            actor, entry, param, x, y, z, o, text = 0, 0, 0, 0.0, 0.0, 0.0, 0.0, ""
            if kind in ("say", "yell", "whisper", "text_emote"):
                actor, text = step[1], step[2]
            elif kind == "fade":
                # ("fade", milliseconds, words): the screen goes dark with words on it (the app's add-on)
                param, text = step[1], step[2]
            elif kind == "sound":
                param = step[1]
            elif kind == "teleport":
                # ("teleport", map, x, y, z, o): the Timerunner, to absolute coordinates
                entry, x, y, z, o = step[1], step[2], step[3], step[4], step[5]
            elif kind == "face_angle":
                actor, o = step[1], step[2]
            elif kind in ("bind",):
                actor, entry = step[1], step[2]
            elif kind == "summon":
                actor, entry, x, y, o = step[1], step[2], step[3], step[4], step[5]
            elif kind == "move":
                actor, x, y, param = step[1], step[2], step[3], step[4]
            elif kind in ("cast",):
                actor, param, entry = step[1], step[2], step[3]
            elif kind in ("aura", "remove_aura", "emote", "stand"):
                actor, param = step[1], step[2]
            elif kind == "face":
                actor, entry = step[1], step[2]
            elif kind == "despawn":
                actor = step[1]
            elif kind == "credit":
                entry = step[1]
            elif kind == "home":
                pass
            else:
                raise ValueError(kind)
            n += 1
            steps.append(f"({s['id']}, {n}, {at}, {ACTIONS[kind]}, {actor}, {entry}, {param}, {x:.2f}, {y:.2f}, {z:.2f}, {o:.4f}, {sql_text(text)})")
            # what each step takes before the next one starts
            if kind in ("say", "yell", "whisper"):
                at += reading_time(text)
            elif kind == "fade":
                at += step[1]
            else:
                at += {"summon": 300, "cast": 600, "face": 300, "text_emote": 2500}.get(kind, 0)
    out = os.path.join(os.path.dirname(__file__), "..", "data", "sql", "remix", "world", "wrath_remix_world_0014_scenes.sql")
    ids = ", ".join(str(s["id"]) for s in SCENES)
    with open(out, "w") as f:
        f.write("""-- Wrath Remix's scenes (STORY.md), written by tools/scenes.py: edit that and run it again. Each is
-- played for one Timerunner as its quest is taken (trigger 1) or turned in (2), or by the module
-- (0: the return to the Bazaar), standing where its anchor stands (RemixScenes.cpp). Steps: at
-- (milliseconds from the start), action (RemixScenes.cpp's SceneAction), actor (a number within the
-- scene), entry, param, x y z o (yards forward, left, up, and the facing added to the anchor's).

CREATE TABLE IF NOT EXISTS `remix_scene` (
  `id` INT UNSIGNED NOT NULL,
  `quest` INT UNSIGNED NOT NULL DEFAULT 0,
  `trigger` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `anchor` INT UNSIGNED NOT NULL DEFAULT 0,
  `credit` INT UNSIGNED NOT NULL DEFAULT 0,
  `name` VARCHAR(120) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `remix_scene_step` (
  `scene` INT UNSIGNED NOT NULL,
  `step` SMALLINT UNSIGNED NOT NULL,
  `at` INT UNSIGNED NOT NULL,
  `action` TINYINT UNSIGNED NOT NULL,
  `actor` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `entry` INT UNSIGNED NOT NULL DEFAULT 0,
  `param` INT UNSIGNED NOT NULL DEFAULT 0,
  `x` FLOAT NOT NULL DEFAULT 0,
  `y` FLOAT NOT NULL DEFAULT 0,
  `z` FLOAT NOT NULL DEFAULT 0,
  `o` FLOAT NOT NULL DEFAULT 0,
  `text` TEXT NOT NULL,
  PRIMARY KEY (`scene`, `step`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

""")
        f.write("DELETE FROM `remix_scene` WHERE `id` IN (" + ids + ");\n")
        f.write("INSERT INTO `remix_scene` (`id`, `quest`, `trigger`, `anchor`, `credit`, `name`) VALUES\n")
        f.write(",\n".join(rows) + ";\n\n")
        f.write("DELETE FROM `remix_scene_step` WHERE `scene` IN (" + ids + ");\n")
        f.write("INSERT INTO `remix_scene_step` (`scene`, `step`, `at`, `action`, `actor`, `entry`, `param`, `x`, `y`, `z`, `o`, `text`) VALUES\n")
        f.write(",\n".join(steps) + ";\n")
    print(f"{len(SCENES)} scenes, {len(steps)} steps")


if __name__ == "__main__":
    main()
