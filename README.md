# Blizzard

An Android launcher for Blizzard's games, styled after the World of Warcraft app in
`logie-github/YeaBwoi` (`warcraft/android`): its frost palette, Cinzel and Jost, the game's window
frames and the drifting snow, in Blizzard's blue. Package `com.logie.blizz`, Android 8 or later,
arm64 phones. Made for the Galaxy Z Fold.

## The shelf

The ice field and the Blizzard logo over the games' box art (3:4), in alphabetical order:
Diablo, Diablo II, StarCraft, StarCraft II, Warcraft: Orcs & Humans, Warcraft II, Warcraft III:
Reign of Chaos and The Frozen Throne (one Warcraft III tile with a version chooser).

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
Every button gives a small press (a shrink and a tick of haptic feedback); the wizard's steps and progress bars fade and glide, and when the game is ready **Play** takes the full width above Reset and Repair.
again for **Repair**.

Where it looks: the app's import folder (`Android/data/com.logie.blizz/files/import`, which a
computer can copy into over USB) and every folder chosen with **Search a folder** (kept).

| Game | Where it comes from | Asks for |
| --- | --- | --- |
| **Diablo** (+ Hellfire) | DevilutionX's Windows build from its GitHub release (GitHub's SHA-256 checked), or a release zip you have | `DIABDAT.MPQ`: the file, a folder, a disc image or GOG's offline installer (unpacked by innoextract, never run). Hellfire's four archives are optional. |
| **Diablo II** + Lord of Destruction | Blizzard's own legacy servers (base game, then the expansion; every piece checked), or your installation folder or a zip of it | Nothing when online. No CD key: optional fields take the original keys if you want them stored. |
| **StarCraft** + Brood War | Blizzard's own legacy servers (1.15.2, disc-free), or your installation folder | `StarCraft.mpq` / `BroodWar.mpq` when an installation lacks them: the archive, the disc's `INSTALL.EXE` or the disc image. |
| **StarCraft II** any build (made for 3.0.5.39117 and 3.1.4.41219) | Your files only; never downloaded | The installation in any form: its folder, a zip, 7z, tar (gz, xz, bz2, zst), a disc image, or an installer (`Setup.exe` with its data files beside it, whatever they're called: innoextract reads Inno Setup ones). `StarCraft II Offline.exe` if it isn't in it (else the game's own program starts). Any build with a `Versions/Base<number>` folder is taken as it is. |
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
- **Classic 2D games** (Diablo II, StarCraft, Warcraft II) draw through cnc-ddraw (OpenGL by default, see Launch options) instead of Wine's DirectDraw, aimed at the low frame rate and missing videos. Untested on a phone.

## Launch options

Each game that runs in Windows (not Warcraft I and II, which are native) has its own **Launch options**, to fix a black screen, missing sound or videos, or a slow game on your phone without waiting for an update: hold the game's tile (or open the game's page) and choose Launch options. A choice is kept and used at the game's next start; **Reset** puts the game's choices back.

- **Safe mode:** the slowest, safest of everything at once (cnc-ddraw's software GDI drawing, Box64 Stability, 30 frames a second, the default graphics driver and Direct3D layer); the other choices are ignored while it is on. Try it first when a game shows nothing.
- **DirectDraw** (the classic games): Wine's own, cnc-ddraw GDI, OpenGL or Direct3D 9. **Frames a second** (30, 60, no limit), **vsync**, **Keep redrawing** (cnc-ddraw's `nonexclusive` and `minfps`, for videos, menus and loading screens that stay invisible) and **Pin to one CPU core** (`singlecpu`).
- **Box64:** Stability, Compatible, Intermediate or Performance (Winlator's presets).
- The **graphics driver**, the **Direct3D layer** and the **resolution** have no setting: the app picks them (Turnip on an Adreno GPU such as the Fold's, Vortek elsewhere; DXVK; always the Fold's inside screen, its shape and its lines, whichever screen Play is pressed on: on the cover screen the game starts at the inside screen's shape between black bars, so opening the phone changes nothing. The inside screen's size is learned whenever the launcher is on it (a Fold 8's 2520x2340 until then). On an Adreno GPU, DXVK tells the games they have an AMD Radeon RX 6800 XT, the same card at every start, so their own checks pick their best settings and give no hardware or driver warnings (safe mode reports the phone's own GPU). The drivers are Winlator's newest: Turnip 26.2.0 and DXVK 2.4.1. Every game is drawn at 60 frames a second by default; nothing is lowered for heat.
- **Defaults** (Diablo II, StarCraft, Warcraft II): cnc-ddraw with OpenGL, borderless fullscreen, 60 frames, redrawing on, **no** CPU pinning (the first release pinned the game to the phone's CPU0, a slow core, which fits the 3 frames a second and the sound that never started), Box64 Intermediate. Other games keep Winlator's defaults (Performance, Vortek, DXVK).
- The games share one Windows, so every option is written at every start; changing the DirectDraw choice, the Box64 preset, the driver or the Direct3D layer also makes Winlator put its files in again. Diablo II has no switch to skip its videos, so there is none here. Untested on a phone.

## Art editor

Hold a game's art to open it. Pinch the preview to zoom the picture and drag to move it (or use the Picture zoom slider); the 3x3 grid (with a centre mark) helps line it up. Pick which of the nine cells holds the logo, and its size. Auto logo returns to the built-in place; Reset removes your pictures and framing.

## StarCraft: Remastered folders and classic-game graphics

- 1.23.x keeps its program in `x86/` and `x86_64/` (the folder's top has `StarCraft Launcher.exe`); the import accepts that layout and starts `x86/StarCraft.exe`.
- Diablo II, StarCraft and Warcraft II use cnc-ddraw, its `ddraw.ini` written at every start from the game's Launch options (below; GDI is Safe mode's renderer). Untested on a phone.

## Game log

While a game runs, the app keeps the last 400 lines Wine printed (errors and the libraries it loaded). The game menu (four fingers) has **Send a report (with the game's log)**, which files it as a GitHub issue, for black screens that leave no crash behind.

- **Back twice** (within a second) opens the app's menu, for when four fingers don't.
- A game that shows no window for 90 seconds, and every game one minute in, send their Wine log as an issue (once a day per game), so a black screen is reported without anyone reaching the menu.
- **Repack installers** (Setup.exe with `Data01.dxn`-style files: ISDone, unarc, xtool, lolz) make the game's files only when they run. The import says so and offers **Run the installer**: the installer and its data files are copied into the app (about the game's size again is needed free, twice over with the install), run silently in the app's Windows (`/SILENT ... /DIR=T:\<game>-installer\out`), and when it has finished, **Import what it installed** (Retry until then) imports it and deletes the copy. Pick the **folder** that holds Setup.exe and its data files: a single Setup.exe picked as a file has no neighbours the app can see, so it asks for the folder. The copy shows bytes, goes on from where it stopped (files already copied are kept), and can be removed ("Remove the installer's copy", or Reset). While the installer runs the wizard says so and looks again when you come back; a game that has stopped changing for 3 minutes counts as finished, in `out` or, when the installer ignored `/DIR`, in the app's Windows C: drive (Program Files, Blizzard Entertainment, users), whence it is moved into `out`. If the installer ends having written nothing, the wizard says so with Wine's last output, and **Run the installer** again tries the next set of switches (`/SILENT`, `/VERYSILENT`, `/SP-`, `/NOCANCEL`, `/LANG=english`, no `/DIR`). Under emulation this can take hours. Untested on a phone.

## Warcraft I, II and III

All four Warcraft games are imported and played in this app (no other app is needed).

- **Warcraft I and II** run natively on the Stratagus engine (War1gus and Wargus), from your GOG offline installers (Setup.exe and its .bin files, picked as a folder or file) or an installed GOG folder, also as zip, 7z, tar or disc image. The app unpacks the installer with innoextract and converts the data with war1tool or wartool (case-fixed first), then plays it with your Controls rules; a game that stops is reported with its output and log. Reset keeps the engine's preferences and saves.
- **Warcraft III: Reign of Chaos and The Frozen Throne** run on the app's Winlator, offline. Both share one install (1.30 is one program): import either and the other uses the same folder. Files from you in any form, or Blizzard's legacy servers for the original game where they offer it (unverified). The screen size and install path are written to Wine's registry at each start. CD keys: paste the ones you have in the keys box on the game's import screen (kept in `cdkeys.txt` apart from the game); the app never generates keys.
- Nothing here has run on a phone. The first CI build also compiles the Stratagus engine and tools (cached afterwards).

## World of Warcraft (from the WoW app, nothing rebuilt)

The shelf's **World of Warcraft** box (placeholder art until you send yours) brings over what the World of Warcraft app (`com.logie.warcraft`) holds: its client, realm databases with their characters, add-ons, modules, settings and the other environments' data. In the WoW app tap **Export everything to Blizzard**, choose where to save, and it writes **one zip file** (`WoW-export.zip`: `files/`, `prefs/`, `checksums.tsv`, and `export.json` as its last entries). In Blizzard, tap the World of Warcraft box, **Auto Import**, and pick that zip. (An export folder made by older versions of the WoW app is still read.) Here, open the box and pick that folder (or the one holding it).

- **The zip is read in one pass**, each file hashed as it is written and compared with `checksums.tsv` at the end; a zip without `export.json` (cut off, or the export didn't finish) is refused, and a zip isn't resumable (a stopped import starts over, and what it wrote is removed). Nothing is renamed inside a zip, so capital-letter twins arrive as they were.
- It's a **copy**: the WoW app and its data are untouched. Every file is checked against the export's SHA-256 list while it's copied, and the finished copy replaces nothing until it's whole. A file that doesn't match is named and nothing is installed.
- A stopped or failed import is **carried on**: files already copied and checked are kept in `staging/wow-work` with a journal; Retry continues. Reset removes it.
- The copy keeps the export's manifest and settings (`.export/`), including the paths the data was made under, for the next step: running the realms here. **Play starts the realm and the game here** (the WoW app isn't needed).
- **OctoWoW** (its own zip, `wow-octowow.zip`, imported on its own page) now plays here too: Play starts OctoWoW's realm (its own database on 3311, the login server on 3724, the world on 8090; ChromieCraft's login port is shared, so starting one stops the other first), points its 1.18.1 client (`files/turtle/client`: the export's folder still has that name on disk) at it, types the saved account at the login screen, and starts the client on the app's Windows with the same touch controls. Never run on a phone: the first start may show a step that fails, and the report it files says which.
- **Legion** (its own zip, `wow-legion.zip`) plays here too: Play starts LegionCore 7.3.5's realm (its own database on 3312, the Battle.net login server on 1119 with its REST login on 8081, the world on 8095; no port shared with the other realms), patches the 7.3.5 client for it the first time (the connection patcher: `Wow-64_Patched.exe` and the certificate bundle, which goes into the game's Windows at each start), points its `portal` at the phone and starts the client with the Box64 that carries the signal-flags fix Legion's start-up protection needs (`scripts/build-box64.sh`, built by CI beside Winlator's; Winlator patch 0007). Same touch controls, the saved e-mail typed at the login screen. Never run on a phone; Legion's start-up protection was the open question in the WoW app too.
- **A successful import deletes the files you picked for it** (the zip, 7z, disc image, installer, Switch package): the game is in the app and checked, and the copy took the same room twice. Only picked *files*: never a folder (it may be Downloads), never your console keys, never the app's own files. A document the picker gave no write access to stays, and the wizard says which. The setting *Delete the files I picked after a successful import* (Settings, Launcher, Imports) turns it off. Files the app found by itself are not deleted; World of Warcraft's export folder has its own explicit *Delete the export* button.
- **What an import leaves behind is cleared once the game is in and checked**: the unpacked archive and the installer's copy and what it made (`staging/<game>-*`), the aside copy of an old installation, the downloads kept for a second try (Diablo II: Resurrected's, the legacy downloader's pieces), and what an installer filled Windows' temporary folders with. Never the game, its saves or its state. Settings, Launcher, *Imports* shows how much is still there and has *Free the space*. The downloaded app update is removed once the version it holds is the one running.
- **Modern character creation (in progress).** It has to be written for the exact files of your client, so the first Wrath+ start (and *Send the creation screen's files* on Wrath+'s settings page) reads the client's character-creation interface files from its archives (`Interface\\GlueXML`: Lua, XML and the table of contents; text only, no game art) and sends them as reports. The archive reader and writer it uses (`wowclient/Mpq.kt`) are a port of the World of Warcraft app's, checked against its C++ reader; they are also what will write the client patch with the new screen.
- **Settings (hold the Blizzard logo) have two pages.** *Launcher*: layout, touch, music, tests. *Games*: every version of every game on its own row (Warcraft III's Reign of Chaos and The Frozen Throne apart; World of Warcraft's Wrath+, Legion, OctoWoW and Forever apart). A version's page sets its **box art** (shelf, page, tiles), its **loading screen** (picture, logo and place) and its **music** (a song of your own for that page; Original puts the downloaded track back), with its launch options and controls. The loading screen you set is the one shown when you press Play (the realm's start and the game's Windows start), with a line from the loading lines on it. It is framed at the inside screen's shape everywhere, the art filling it and cut beyond it, and the art editor's preview shows that same frame. World of Warcraft shows one loading screen from the realm's start to the game's window, with no return to the launcher between them; the game's screen fades in over it. The music fades on its own thread (an equal-power curve, 1.5 s between songs, 2.2 s from silence), pauses where it is while a game runs and picks up from there afterwards.
- While a realm or the game's Windows starts, the dialog shows a line chosen at random (Sharpening Worgen claws..., Feeding the Murlocs...), another every few seconds, in place of the step names.
- Names that differ only in case (the client's `FlyByWorgen.m2` and a module's `flybyworgen.m2`) can't live side by side on shared storage, so the WoW app stores them under `<name>~<8 hex>` and lists them in `export.json` (`renames`); the import follows that. An export made before that fix is read too: a missing file is looked for in another case and as `name (1).ext`, and still checked against its SHA-256.
- Files the export lists that can't be found anywhere (by name, by their other likely names, or by size and checksum) are **left out with a note** (`.export/missing.txt`) instead of stopping the import, unless the game can't do without them: the databases (`mysql/`), the client (`client/`) and the server programs (`server/bin`, `server/lib`, `ctl.sh`) are always required.
- Once the copy is verified and in place, the wizard offers **Delete the export** (the zip, or the folder) to free the space; the picker is asked for write access for that. If a file manager won't allow it from here, it says so and you delete it in Files.
- You need free space for the zip plus this copy (about twice the zip's size while it imports).

## Music

A track for the shelf (Arthas, My Son) and one for each game plays from the moment the game is selected, looped, and stops while a game runs. Warcraft III is one tile: choose Reign of Chaos or The Frozen Throne on its page and the art, the music and the game follow, kept until you change it. The tracks aren't in the app: they are downloaded the first time it opens (the settings' **Music** section shows how many are on the phone and has **Download music** for any that failed), into the app's own folder. A song's address can be the file or the song's page on khinsider, which is read for the file. The settings also have music on/off and a volume. The World of Warcraft tile plays the Wrath of the Lich King main title; the original game's Legends of Azeroth is downloaded and kept for a Classic version. Untested on a phone.

## Diablo II: Resurrected

Diablo II's tile has a second version, **Resurrected** (the chooser on its page; the choice is kept, and the art, here the original's until you use Change Art, and the music, Diablo II's, follow it). It is the Nintendo Switch release's own ARM64 program, run on the phone on Vulkan through the open-source host of [D2R Mobile](https://github.com/jhaizhou-ops/d2r-mobile) (MIT). Nothing of it is packaged with Blizzard.

**Auto Import** (the page's wizard) does two things:

1. **Downloads the module first:** D2R Mobile's newest release, from GitHub, of which Blizzard keeps the native library, code and assets (in `modules/d2r`); the release's APK itself is never installed.
2. **Imports your Switch files**, which must be your own Diablo II: Resurrected with Reign of the Warlock, updated to 1.0.34.0 (PC 3.3.94012): pick the **base game** (the .nsp, a folder with it, or the 7z, zip or tar that holds it), the **update** (the same, or skip when it is in the same package) and your **prod.keys**. The app unpacks them with hactool the way the project's own `extract_game.sh` does: title keys from the tickets in the .nsp files (a personalized ticket, tied to the console it came from, holds none: put that title's key in the keys file), the base game's program and the update's told apart by what hactool reports, the update extracted over the base, the three ExeFS files checked against the 3.3.94012 ones (SHA-256), and only what the game reads kept (the 18 resource archives, `.build.config`, the manifest, ExeFS: about 5.6 GB). It needs about 26 GB free while it works. The keys are copied to a private folder for the unpacking and deleted with it; nothing is uploaded.

**Not done yet:** playing it. The port runs from an *import pack* its tool makes from those files (the game's program rewritten for Android, about 6,900 translated shader bundles, the touch overlay and some tables). That tool needs Python with several packages, the .NET SDK and the Vulkan SDK's shader tools, which a phone doesn't have, so for now Play only says the files are imported. Hosting the library inside the app is feasible (a stub of the class its native code binds to, `System.load`, and a surface and touch Activity: about 1,600 lines of the project's MIT Java source adapted), but needs the pack. Untested on a phone.

## When an install fails

A failed import (the first failure of its kind each day) is sent to this repository as an issue, with what the app knows: the problem, the checks that failed, the log, and **a listing of the files involved** (what you picked, the installed folder and what the import left in staging): each file's path, size and a hash of its size and its first and last 64 KB, never its content, so the files themselves needn't be sent. Sending needs the `BLIZZ_REPORT_TOKEN` secret built into the release (see Launch test).

## World of Warcraft controls

The Wrath+ client has the World of Warcraft app's own touch controls, ported as they are (`wowinput/`, with the app's tests): its gestures, tap-to-click that waits for the game's cursor and reads it to talk, loot and attack, camera and movement, the action bars, character creation turning, cutscenes, and the text prompt. At the login screen the saved password (from the export's `prefs/login.json`) is typed by itself, or the prompt asks for it. Back is Escape; twice opens the app's menu. The other games keep the app's own controls.

## Launch test

From the settings' **Run the launch test now** (it no longer runs by itself), every game is checked and each installed one is started: **is it installed** (its import record and files: where an import stopped and why), **did it finish installing**, **does it launch** (the game's first window comes up and stays for ten seconds; Warcraft I and II: Stratagus starts and stays up) and **does it run OK**. Each game is then closed. Games that were never imported are noted, not started. World of Warcraft starts its realm first (minutes the first time) and stops it afterwards. The result is a report: a table of every game, the failures with their notes and the end of the Wine log, saved on the phone, shown to copy, and sent to this repository as an issue labelled `launch-test`. If the app itself dies during a game, the next start sends what was done and names the game it died on. Sending needs the `BLIZZ_REPORT_TOKEN` secret built into the release; without it the dialog says so and the report can be copied. Untested on a phone.

## Tiles and settings

**Hold the Blizzard logo** for the settings: the layout (**Classic shelf**, as it was, or **Tiles**), how many tiles across, vibration, the music, and a reset for the tile layout.

In **Tiles**:
- **Pinch** the tiles to make them bigger or smaller (one more or fewer across), like the 3DS's grid; one finger still scrolls.
- **Wrath+, Legion and OctoWoW have an Add-ons card** (version page in Settings, Games): search warperia.com for that client's add-ons (3.3.5a, 7.3.5 or 1.12), install them one at a time into the client's `Interface/AddOns` (the site's few seconds' wait included), turn them on and off, delete them, update them, or add a zip. **Wrath+ also has a Modules card**: search GitHub's `azerothcore-module` topic, read a module's README, pick modules, and ask for a realm built with them (it needs your own GitHub token for this repository, kept in the app only: Actions read and write, Contents read). The build is this repository's own workflow (`build-realm-modules.yml`, from the sources in `realm/`; nothing of the World of Warcraft app's repository is used), and its package goes on the release `realm-modules`; the built realm replaces the realm's own, which is kept to put back. Untested on a phone. Every module is fitted in by the build (one whose loader isn't named for its folder gets a file that calls it); one that still doesn't compile with the realm's AzerothCore is left out, and the app says which and why. The core has the `OnPlayerGetRestBonusMax` hook some modules need.
- **Hold a box** (on the shelf, its page or a tile) for its menu: **Loading screen**, **Launch options**, and for World of Warcraft **Add-ons** (Wrath+, Legion, OctoWoW) and **Modules** (Wrath+). The token the modules need is explained click by click in the app's token box.
- **Launch options** are in the settings pages' look: a card per setting with its note, choice lists with the chosen one lit.
- **Hold a tile** for its menu: **Change Art** (vertical or horizontal, your own picture for either, or the original), **Rearrange**, **Reinstall** (removes the imported files and starts the import again; saved games stay) and **Loading screen** (the art editor).
- **Rearrange**: the tiles wiggle; hold one and drag it where it goes; Done keeps the order.
- A horizontal tile spreads across the whole row (at least two columns; the tall tiles beside it take its height) and shows its wide art whole; it uses the game's wide art (the World of Warcraft box has Wrath's header; the others use their loading-screen art or the box art cut to fit until you choose a picture).
- Tiles glide to their places when the order, shape or size changes, press in when touched, and the grid follows a pinch a little before the columns change.
- Tapping a tile opens the game's page, as the shelf does.
Classic shelf keeps its own hold (the loading-screen editor).

### World of Warcraft: Play from the imported files

Play starts MariaDB, the auth server and the world server of the realm you last used in the WoW app (read from the imported settings: ChromieCraft or Wrath Remix) from `games/wow/files/server`, with the imported databases as they are (a realm whose `acore_*` folders are in `mysql/` is never rebuilt), then the imported 3.3.5a client on Blizzard's Winlator, with its `realmlist.wtf` and `WTF/Config.wtf` pointed at it (your add-ons, characters and other settings are kept; the account name is filled in, you type the password).
- The server programs were built with the old app's folder as their loader path, so they're started through the musl loader (`server/ctl.blizz.sh`, made from `ctl.sh`, which is left as it was), and the old app's folder in the text configs and scripts is rewritten to this one (never in binaries or databases; `files/.blizz-paths` records it).
- A realm that fails to start reports its log tail as an issue. The first start can take minutes.
- Not verified on a phone: the programs running through the loader from this folder, MariaDB opening the imported InnoDB files, the world server reaching ready, and Wow.exe under DXVK/Box64.
