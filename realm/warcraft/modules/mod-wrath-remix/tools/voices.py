#!/usr/bin/env python3
"""Moratari's own voice: her lines as Legion Remix has them (Moratari, 241140; the game's files
sound/creature/moratari/vo_1125_moratari_NN_f.ogg), the ones that fit Wrath Remix, each with the
moment the realm speaks it at.

    python3 tools/voices.py              writes data/sql/remix/world/wrath_remix_world_0028_voices.sql
    python3 tools/voices.py fetch DIR    puts each line's sound in DIR as a WAV (the game's own voices'
                                         format): from wago.tools by its file id, through ffmpeg

The sounds are the game's files, so they are never in this repository: the server package fetches
them (scripts/package-azerothcore.sh) into the module's data/voices, where the world server finds
them (ClientPatch.cpp puts them in the game's patch with their SoundEntries rows; RemixVoices.cpp
plays them as she says the words). Without them she speaks in text alone.

The words are what she says in each file (heard: the game's text for them isn't in its tables).
"""
import os
import subprocess
import sys
import time
import urllib.request

USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"   # (wago.tools turns away Python's own)

MODULE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL = os.path.join(MODULE, "data", "sql", "remix", "world", "wrath_remix_world_0028_voices.sql")
FIRST_SOUND = 77001  # SoundEntries ids (the game's own end at 18019)

# (file number, the game's file id, seconds, moment, words)
LINES = [
    # Clicked on: a greeting, as the game's people have.
    (20, 7074603, 1.61, "greet", "Our endeavor goes on."),
    (21, 7074604, 2.05, "greet", "Observe all that surrounds you."),
    (22, 7074605, 2.18, "greet", "The possibilities are infinite."),
    (23, 7074606, 2.36, "greet", "Never settle for the unknown."),
    (24, 7074607, 1.81, "greet", "It's a pleasure to work with you."),
    (25, 7074608, 1.80, "greet", "Who knows what knowledge we'll acquire?"),
    (26, 7074609, 3.16, "greet", "What is history, if not a series of variables?"),
    (27, 7074610, 3.17, "greet", "So much knowledge waiting to be gleaned."),
    (15, 7065444, 6.94, "greet", "So take heart in knowing that what you are doing here is important."),
    # Back after days away.
    (1, 7065394, 4.02, "welcome_back", "Champion, there you are. I thought we'd lost you."),
    (47, 7078231, 4.34, "catch_up", "Timerunner? Come back to the Infinite Bazaar when you can. We should catch up."),
    # Levels: every tenth, and the last.
    (29, 7075061, 7.04, "milestone", "Congratulations are in order, Timerunner. Come see me at the Infinite Bazaar. We have some things to discuss."),
    (30, 7075064, 6.98, "milestone", "Meet me at the Infinite Bazaar at your earliest convenience, Timerunner. We have yet more to learn, and we're running out of time."),
    (28, 7075060, 6.49, "level80", "A monumental achievement, Timerunner! Check in with me back at the Infinite Bazaar as soon as you're able."),
    # Taking the Timerunner past something: the story's transitions, the Chronologist, the opening let go.
    (34, 7075461, 1.66, "skip", "I think we can gloss over this one."),
    (35, 7075462, 0.52, "skip", "Skip."),
    (36, 7075463, 1.15, "skip", "Nothing to see here."),
    (37, 7075464, 0.86, "skip", "Moving on."),
    (38, 7075465, 0.78, "skip", "Jumping ahead!"),
    (39, 7075466, 0.67, "skip", "Job's done."),
    (40, 7075467, 1.69, "skip_training", "Let's skip basic training."),
    (41, 7075888, 3.47, "skip_study", "No offense, but this isn't really what we're here to study."),
    (31, 7075458, 5.27, "jump_forward", "Sorry for the interruption, but we're going to jump you forward in time past this moment."),
    # Sending the Timerunner somewhere.
    (46, 7078201, 1.78, "portal", "I will create a portal for you now."),
    (11, 7065440, 1.23, "one_moment", "One moment, please."),
    (19, 7065448, 1.19, "watch_step", "Watch your step."),
    (10, 7065439, 8.18, "back_to_dalaran", "If you're all set, let's get you back to Dalaran so you can rejoin the flow of events. You're always welcome back here, though."),
    # Her romance: the flight on her back, its landing, the promise in Icecrown.
    (12, 7065441, 8.60, "wings", "Oh, it feels good to stretch my wings. Hang on!"),
    (17, 7065446, 6.08, "low_profile", "After all, we're supposed to be keeping a low profile here."),
    (9, 7065435, 4.37, "time_we_have", "Well, then we'll simply have to make the most of the time we have, won't we?"),
    # After a fight beside the Timerunner, now and then.
    (5, 7065426, 0.68, "after_fight", "Are they gone?"),
    # Once each, at their moment in the story.
    (13, 7065442, 9.60, "eternus_praise", "Don't let this get to your head, but Eternus almost never gives anyone that much praise."),
    (14, 7065443, 8.40, "eternus_praise", "I should know, after all. I've known her for... well... forever."),
    (8, 7065432, 8.54, "plan_reply", "But not anymore, right? After all, that is what we came here to do. Introduce changes to the past and observe the results as they occur."),
    (32, 7075459, 7.41, "plan_ends", "Like Eternus mentioned before, this experiment will eventually end, so we have to be wise about how we spend our time."),
    (6, 7065427, 7.37, "back_to_eternus", "As exciting as all that was, I'll be glad to get back to the Infinite Bazaar. Eternus will surely want to speak with you too."),
    (33, 7075460, 7.62, "put_back", "See? Everything is the same. Except now, we are in control of our own time. We're ready to proceed."),
    # The last goodbye, before the way home: one after the other.
    (42, 7078189, 8.74, "farewell", "This has been quite the experiment, hasn't it? Now the sands of time slip through the hourglass, waiting to be turned over again."),
    (43, 7078190, 8.06, "farewell", "The strange thing about traveling through time is that goodbyes and hellos tend to blur together. It can be hard to tell them apart."),
    (44, 7078191, 8.33, "farewell", "And yet, they are, in their own way, so distinct from one another. I wonder why that is. Perhaps they deserve their own experiment."),
    (45, 7078192, 8.75, "farewell", "Well, if I ever decide to pursue it, I'd be thrilled to have you as an assistant. Then this goodbye would blur into a hello as well."),
]


def file_name(number):
    return "vo_1125_moratari_%02d_f.wav" % number


def sql_text(text):
    return text.replace("\\", "\\\\").replace("'", "''")


def write_sql():
    rows = []
    for number, fdid, seconds, moment, words in LINES:
        rows.append("(%d, '%s', %d, '%s', %d, %.2f, '%s')" % (
            FIRST_SOUND + number - 1, moment, number, file_name(number), fdid, seconds, sql_text(words)))
    with open(SQL, "w", newline="\n") as out:
        out.write("-- Moratari's own voice (made by tools/voices.py: edit that, not this): her Legion Remix lines\n"
                  "-- that fit Wrath Remix, the moment each is spoken at, its SoundEntries id and its file in the\n"
                  "-- module's data/voices (fetched by the server package; never in the repository).\n"
                  "DROP TABLE IF EXISTS `remix_voice`;\n"
                  "CREATE TABLE `remix_voice` (\n"
                  "  `sound` INT UNSIGNED NOT NULL COMMENT 'SoundEntries id (the game patch adds the row)',\n"
                  "  `moment` VARCHAR(32) NOT NULL COMMENT 'when she says it (RemixVoices.cpp)',\n"
                  "  `number` TINYINT UNSIGNED NOT NULL COMMENT 'the game file''s number',\n"
                  "  `file` VARCHAR(64) NOT NULL COMMENT 'its WAV in data/voices',\n"
                  "  `file_id` INT UNSIGNED NOT NULL COMMENT 'the game''s file id (FileDataID)',\n"
                  "  `seconds` FLOAT NOT NULL,\n"
                  "  `words` VARCHAR(255) NOT NULL,\n"
                  "  PRIMARY KEY (`sound`)\n"
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Wrath Remix: Moratari''s voice';\n\n"
                  "INSERT INTO `remix_voice` (`sound`, `moment`, `number`, `file`, `file_id`, `seconds`, `words`) VALUES\n")
        out.write(",\n".join(rows) + ";\n")
    print("wrote", os.path.relpath(SQL, MODULE), len(rows), "lines")


def fetch(folder):
    os.makedirs(folder, exist_ok=True)
    got = fetched = 0
    for number, fdid, seconds, moment, words in LINES:
        wav = os.path.join(folder, file_name(number))
        if os.path.exists(wav) and os.path.getsize(wav) > 44:
            got += 1
            continue
        ogg = wav[:-4] + ".ogg"
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request("https://wago.tools/api/casc/%d?download" % fdid,
                        headers={"User-Agent": USER_AGENT}), timeout=30) as response:
                    data = response.read()
                if data[:4] != b"OggS":
                    raise ValueError("not an Ogg file")
                with open(ogg, "wb") as out:
                    out.write(data)
                break
            except Exception as error:  # a network hiccup: once more, a little later
                print("voices: file %d (%s): %s" % (fdid, file_name(number), error), file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        if not os.path.exists(ogg):
            if not fetched:
                # (the first one not to come at all: the service isn't answering this machine,
                # so the build doesn't wait on each of the others too)
                print("voices: wago.tools isn't answering; the rest aren't tried", file=sys.stderr)
                break
            continue
        fetched += 1
        # 16-bit mono at 22,050 Hz, as the game's own voices
        # (and nothing else in the file: no tags)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", ogg, "-ac", "1", "-ar", "22050",
                        "-c:a", "pcm_s16le", "-map_metadata", "-1", "-bitexact", wav], check=True)
        os.remove(ogg)
        got += 1
    print("voices: %d of %d of Moratari's lines in %s" % (got, len(LINES), folder))
    return got == len(LINES)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "fetch":
        sys.exit(0 if fetch(sys.argv[2]) else 1)
    elif len(sys.argv) == 1:
        write_sql()
    else:
        print(__doc__)
        sys.exit(2)
