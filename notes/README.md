# Patch notes

One line for each change, in plain words for the player (the user: "Start leaving one line patch notes in the update
when you update the version. Put this only in the games, settings, gear button menu").

- Every change that reaches `main` adds **one file** here: `YYYY-MM-DD-what.txt` (the day, then a few words with
  hyphens, no spaces), holding **one line**: what the player gets, e.g. `Warcraft III: clicks land where you tap.`
- CI's release step (`scripts/release-notes.sh`) puts the lines of the files added since the previous release into the
  new release's description, one `- ` line each, oldest first.
- The app reads those lines from the releases it looks at for updates and shows them **only** on Settings' **Games**
  page (the gear button), newest first, the installed version marked: never in a popup, the update banner or anywhere
  else.
- A released note is never edited or removed (it is already in a release); a correction is a new note.
