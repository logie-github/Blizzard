# Blizzard

An Android launcher for Blizzard's games, styled after the World of Warcraft app in
`logie-github/YeaBwoi` (`warcraft/android`): its frost palette, Cinzel and Jost, the game's window
frames and the drifting snow, in Blizzard's blue. Package `com.logie.blizz`, Android 8 or later,
arm64 phones. Made for the Galaxy Z Fold.

## The shelf

The ice field and the Blizzard logo over the games' box art (3:4), in alphabetical order:
Diablo, Diablo II, StarCraft, StarCraft II, Warcraft: Orcs & Humans, Warcraft II, Warcraft III:
Reign of Chaos, Warcraft III: The Frozen Throne.

- **Cover screen:** two boxes across; a game's page opens over the shelf, Back returns.
- **Inner screen:** every box in one row under the header, the chosen one lifted; its game below.
- **Half-open like a laptop (tabletop):** the box art above the hinge, Play and the boxes below.

The Warcraft games open the Warcraft app (`com.logie.warcrafts`) when it's installed, or any app
chosen for them.

## Auto Import

Diablo, Diablo II, StarCraft and StarCraft II are imported into the app and played on its own
Winlator (Wine and Box64), offline, with the touch gestures of YeaBwoi's Warcraft app. On a game's
page, **Auto Import** opens the wizard: Detect, Acquire, Request (only what it can't get itself),
Install, Validate. Then the button becomes **Play**; the status line under it opens the wizard
again for **Repair**.

Where it looks: the app's import folder (`Android/data/com.logie.blizz/files/import`, which a
computer can copy into over USB) and every folder chosen with **Search a folder** (kept).

| Game | Where it comes from | Asks for |
| --- | --- | --- |
| **Diablo** (+ Hellfire) | DevilutionX's Windows build from its GitHub release (GitHub's SHA-256 checked), or a release zip you have | `DIABDAT.MPQ`: the file, a folder, a disc image or GOG's offline installer (unpacked by innoextract, never run). Hellfire's four archives are optional. |
| **Diablo II** + Lord of Destruction | Blizzard's own legacy servers (base game, then the expansion; every piece checked), or your installation folder or a zip of it | Nothing when online. No CD key: optional fields take the original keys if you want them stored. |
| **StarCraft** + Brood War | Blizzard's own legacy servers (1.15.2, disc-free), or your installation folder | `StarCraft.mpq` / `BroodWar.mpq` when an installation lacks them: the archive, the disc's `INSTALL.EXE` or the disc image. |
| **StarCraft II** 3.0.5.39117 or 3.1.4.41219 | Your files only; never downloaded | The installation in any form: its folder, a zip, 7z, tar (gz, xz, bz2, zst), a disc image, or an installer (`Setup.exe` with its data files beside it, whatever they're called: innoextract reads Inno Setup ones). `StarCraft II Offline.exe` if it isn't in it (else the game's own program starts). Any other build is refused. |
| **StarCraft: Remastered** 1.23.10.12409 | Your files only, in any of those forms | A second installation beside the classic StarCraft (its own folder, saves and controls): the game's page has a **Classic · Remastered** switch. Imported — Launch Untested. |

Statuses: Ready to Play, Imported — Launch Untested, Import Incomplete, Missing Required File,
Unsupported Client Version, Launch Test Failed. A game's first window coming up under Winlator is
recorded apart from the file checks.

What's checked: the game's program (Windows x86, its version), every DLL its import table names
(Windows' own aside), every data archive (an MPQ header), the expansion's archives. Saves are kept
apart from the game folders (`files/saves`, or inside the games' Windows) and no import or repair
writes over one. Blizzard's and Battle.net's names are blocked in the runtime's hosts file.

Version notes:

- Diablo II: 1.14 (1.14b is what Blizzard serves). Older clients are refused (they need the disc).
- StarCraft: Blizzard serves 1.15.2; installations at 1.15.2 to 1.16.1 are accepted. Blizzard no
  longer serves the 1.16.1 patch, so the app doesn't apply it. Remastered is refused.
- StarCraft II: stays **Imported — Launch Untested**: files can't show that the offline launcher
  works under Winlator or that the campaigns load.

DevilutionX is under its Sustainable Use License (non-commercial use, free distribution); the app
downloads the project's own release on the phone and redistributes nothing of it.

Diablo and Diablo II start behind their own splash (`branding/splash/`): the art fills the screen,
cut at its sides (Diablo II is never cut at its top), its logo low over it, embers rising.

## Bug reports

Crashes, failed imports and failed game starts are sent to this repository as GitHub issues by
themselves (labels `bug`, `auto-report`), with the app's version, the phone, the game, what the
app said, its checks and the end of the log; CD keys and tokens are taken out. They're queued in
`files/reports` and sent at once, again every minute while any wait, and the same failure goes
once a day at most. Only an import you stop yourself isn't sent; a full phone, an unsupported game version and a failed app-update download are.

They go with the token CI builds in, as YeaBwoi's apps carry theirs: the repository secret
`BLIZZ_REPORT_TOKEN` (a token that may open issues here). Without it, reports wait on the phone.

## Updates

Each time it opens, the app looks at this repository's releases (`blizzard-build-N`); a newer build
downloads by itself (a banner shows it) and Android's installer opens for the one tap Android
requires. The first time, Android asks to allow installs from this app.

## Controls

Each game's **Controls** button (beside Play) lists every function with its key and the gestures that run it, and the gesture rules: *If [gesture] [where] then [function]*. Keys are the game's own defaults (Diablo's are DevilutionX's); change a key by tapping it. Add a rule with the record button: do the gesture on the pad and it names the gesture and where it was; pick what it does. Where several rules match, the smallest area wins; "Nothing" switches a spot off. Saved per game; the reset button restores the defaults.


The one gesture system (`controls/Gestures.kt`), two profiles (`game/LaunchProfile.kt`):

| | StarCraft, StarCraft II | Diablo, Diablo II |
| --- | --- | --- |
| Tap | Right click (left on the game's panels) | Left click: walk, attack, pick up |
| Hold | Left click (twice: double click) | Right click: cast |
| Swipe | Pan the map | Drag: walk after the finger. Quick flick: the arrow key its way (menus) |
| Resting finger | Shift | Shift |
| Two / three / four fingers | Game menu / keyboard / app menu | Same |

A mouse, keyboard or controller works as on a PC. Back is Escape.

## Build

JDK 21, Android SDK 35, NDK 24.0.8215888 and CMake 3.22.1.

```sh
scripts/prepare-winlator.sh   # Winlator into app/winlator (winlator-version.env, patches/winlator)
scripts/build-tools.sh        # innoextract and blizzard-legacy-dl into app/tools (tools.env)
./gradlew :app:assembleDebug :app:testDebugUnitTest
```

blizzard-legacy-dl is built with Zig 0.17 for arm64 (static), with `patches/blizzard-legacy-dl`:
its name lookups go through the app (Android has no `/etc/resolv.conf`), and it's built
position-independent. `testDebugUnitTest` also renders the screens to `app/build/reports/previews/`.
`BLIZZ_REAL_GAMES=<dir>` points one test at real installations (`d2/`, `sc/`) to check the readers
on Blizzard's own programs.

The art is in `branding/`; `python3 tools/make-art.py` makes the app's pictures and icon from it.
Every build is signed with `app/sideload.keystore`, so each release installs over the last.

## Releases

A push to `main` builds, tests and publishes `Blizzard 1.0.N` (tag `blizzard-build-N`), which the
app installed on the phone picks up the next time it opens.

Not affiliated with Blizzard Entertainment. All trademarks referenced herein are the properties
of their respective owners.

## Reset and graphics notes

- **Reset installation:** every game's import screen has a Reset button (with a confirmation). It removes the game's imported files and state so the import runs again; saves are kept.
- **StarCraft key:** the downloaded StarCraft is installed with a placeholder key and owner (the game runs offline), which avoids the `font\font.gid` "File not found" error.
- **Classic 2D games** (Diablo II, StarCraft, Warcraft II) draw through cnc-ddraw (OpenGL) instead of Wine's DirectDraw, aimed at the low frame rate and missing videos. Untested on a phone.

## Art editor

Hold a game's art to open it. Pinch the preview to zoom the picture and drag to move it (or use the Picture zoom slider); the 3x3 grid (with a centre mark) helps line it up. Pick which of the nine cells holds the logo, and its size. Auto logo returns to the built-in place; Reset removes your pictures and framing.

## StarCraft: Remastered folders and classic-game graphics

- 1.23.x keeps its program in `x86/` and `x86_64/` (the folder's top has `StarCraft Launcher.exe`); the import accepts that layout and starts `x86/StarCraft.exe`.
- Diablo II, StarCraft and Warcraft II use cnc-ddraw's GDI renderer (no OpenGL or Direct3D needed), written to its `ddraw.ini` at every start. Untested on a phone.

## Game log

While a game runs, the app keeps the last 400 lines Wine printed (errors and the libraries it loaded). The game menu (four fingers) has **Send a report (with the game's log)**, which files it as a GitHub issue, for black screens that leave no crash behind.
