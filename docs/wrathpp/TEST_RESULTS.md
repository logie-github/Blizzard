# Wrath++ test results

Machine: Linux x86_64 container, 4 cores, clang 18.1 / g++ 13.3, CMake 3.28, LuaJIT 2.1,
MariaDB 10.11 (Ubuntu). No Windows, no MSVC, no phone, no game client data.

## 2026-11-10

| Test | Command | Result |
|---|---|---|
| Codec + registry (C++, ASan/UBSan) and registry tool (Python) | `realm/warcraft/wrathpp/protocol/tests/run.sh` | **pass**: all C++ checks (round trips, every truncation, trailing bytes, duplicates, limits, validation, resolve, independence of categories, registry from the tool re-encoded byte for byte, hash `b4d1d700`); 5 Python tests |
| Client Lua mod on a mock runtime | `realm/warcraft/wrathpp/client-mod/tests/run.sh` | **pass**: 29 Lua checks; its 4 sent messages decoded as the server decodes them (5 checks); Lua FNV-1a equals the server's hash |
| `ctl.sh` isolation | `realm/warcraft/wrathpp/tests/test-isolation.sh` (base `17cd42e`) | **pass, 58/58**: main's and Remix's configs, world server environment, dbimport and realm list SQL identical to the previous `ctl.sh`; the app's program-rewrite lines unchanged; nothing of Wrath++ made while its server is absent, its commands refuse (exit 4); with it installed only Wrath++ paths/DBs written, SHA-256 of every other file unchanged; DROP only `acore_world_wrathpp`; a linked or hard-linked game folder refused; realm list row 5 only, refused when taken. Mutation check: pointing Wrath++'s game folder at the shared one makes 5 checks fail |
| Core patch + module compile | CMake/Ninja on `fetch-wrathpp.sh`'s tree (clang, `WITH_WARNINGS=1`) | **pass**: `Opcodes.cpp`, `WorldSession.cpp`, `WorldSocket.cpp`, `WrathppHandler.cpp`, the module (with its `static_assert` that the core's opcode numbers equal the protocol's): 0 warnings; full `worldserver` and `authserver` linked |
| Source reproducibility | `realm/scripts/fetch-wrathpp.sh <scratch>/ac-wrathpp-fetch` | **pass**: tree `2846dec0…` identical to the tree that was built and live-tested; a folder without `wrathpp` in its path refused (exit 2) |
| Live server | `realm/warcraft/wrathpp/tests/run-server-test.sh` (server data v20.0) | **pass**, below |

### Live server test (protocol client `tests/server_protocol_test.py`, real AzerothCore worldserver/authserver)

First start (34 checks): hello, registry and the account's looks arrive before `SMSG_CHAR_ENUM`;
registry bytes hash to the hello's hash and equal `registry.json`'s build; a choice before the
client's hello → `disabled`; wrong registry hash → `registry_mismatch`; protocol 9 →
`unsupported_version`; truncated, trailing byte, pending-with-guid → `malformed`; a category twice →
`duplicate`; 33 categories → `too_many`; option 99 → `unknown_option`; category 4242 →
`unknown_category`; horns for a human → `ineligible`; another registry version →
`registry_mismatch`; a blood elf paladin created with horns 2 + blindfold 2 (result names its guid);
choices validated for a paladin then a mage created → `character_mismatch`, mage at defaults; the
character list shows horns 2 / blindfold 2; horns changed to 3 alone, blindfold stays 2; a change
claiming the other sex → `character_mismatch`; another account's change → `not_owner`.

World server stopped (SIGINT) and started again (17 checks): character list shows horns 3 /
blindfold 2; in the world the player receives its own look; a second account's character beside
it asks (QUERY) and gets horns 3 / blindfold 2, nothing for a non-character guid; the first player
was told the second's look as it arrived; horns changed to 2 in the world reach the second player at
once, blindfold unchanged.

Databases: rows `(1,1002,2)`, `(1,1003,2)` in `acore_characters_wrathpp`; the character's five stock
fields untouched (0, as created); a canary `acore_characters` database (checksum + table list)
unchanged. Same server pointed at `acore_characters_guardtest`: module logs "Wrath++: refusing to
run" and sends no Wrath++ message.

Finding: the core's update system applied the module's `db-characters` SQL to
`acore_characters_guardtest` too (it applies a built-in module's SQL to whatever database the binary
serves). The module refused to use it, but this is why the module must exist only in the Wrath++
binary: built into main's server, it would create its table in `acore_characters`.

Note: MariaDB 10.11 lacks `utf8mb4_0900_ai_ci`, which the core's SQL names; the harness reads a copy
of the SQL with `utf8mb4_unicode_ci` on such a server (the phone's MariaDB 11.4 has the collation).

### Client build probe (`.github/workflows/wrathpp-client.yml`, windows-2022, MSVC 19.44.35229, CMake 3.31.6)

Pins: client `fdb9ad18`, core `f7d6cdaf`, sdk `2920b6e3`.

| Run | Result | What stopped it | Fix |
|---|---|---|---|
| [42872711989](https://github.com/logie-github/Blizzard/actions/runs/42872711989) | fail | `sdk/include/wxl/reflect.hpp(213): error C2131`, constexpr step limit 1048576 | `CXXFLAGS=/constexpr:steps16777216` in the workflow |
| [42873162423](https://github.com/logie-github/Blizzard/actions/runs/42873162423) | fail | core `src/gx/d3d9/shaders/draw.hlsl(43)`: `error X3000: unexpected token 'line'` (a reserved word), 4 shaders | core patch `patches/core/0001` (renamed to `lineInfo`) |
| [42873904737](https://github.com/logie-github/Blizzard/actions/runs/42873904737) | fail | core `src/tuning/Animate.cpp`: GCC-style `__asm__ volatile` (17 errors) | core patch `patches/core/0002` (`_mm_getcsr`/`_mm_setcsr`/`_mm_pause`; GCC form kept under clang/GCC) |
| [42874636845](https://github.com/logie-github/Blizzard/actions/runs/42874636845) | **pass**, 0 errors, 2557 warnings | — | — |

Built (SHA-256; binaries not kept): `WowClient64.exe` `420d846a87049c929f4de087668bd46d64a621c2c5bffdd1e9afb161ab26ccfc`,
`WarcraftXL.dll` `adcb189ad22bdae0c339c76a6c2fe67802808c1b8f65d1a833ded9dd072dc5da`,
`XvidDecoder.dll` `eeea0ff544874c2e8df8e1e39c55b55a6e2ed446e222b04a9001370b1d742146`.
The two core fixes suggest the upstream core is normally compiled with clang-cl or a newer MSVC;
that was not checked.

### Not tested

- Booting the client: the build passed (below), but nothing ran it (no game data in CI).
- Anything drawn: no extended category is rendered anywhere yet.
- The Lua mod inside the real WarcraftXL runtime.
- The server's arm64/musl build (the phone's) with the patch and module: only this machine's x86_64
  glibc build was compiled and run.
- Android: nothing.
- `ctl.sh` under Android's `/system/bin/sh` or busybox: run under dash (`sh`) here.
- The Android app's unit tests (`./gradlew :app:testDebugUnitTest`): this machine has no Android
  SDK; no app source changed. CI's `build-apk` runs them on the push to `main`.

## 2026-11-10, the app's Wrath++ page

| Test | Command | Result |
|---|---|---|
| App unit tests, all | `./gradlew :app:testDebugUnitTest` (Android SDK 35 installed here; Maven Central through its Google mirror, `--init-script`; Winlator prepared; native parts as placeholders) | **pass**: 616 tests, 0 failures, 20 skipped |
| New: `RealmControllerTest.wrathpp*` | | Wrath++'s own steps (`configure-realm`, `dbimport`, `modules`, `wrathpp-register`, `world`, realm `wrathpp`) run by `server-wrathpp/ctl.blizz.sh`, the shared ones (MariaDB, `configure`, `realmlist`, the login server) by the realms' script; its world log in `logs/wrathpp`; without its server it fails before running anything |
| New: `WowPlayTest.wrathpp*` | | Play makes its copy, starts realm `wrathpp`, points `client-wrathpp` at "Wrath++" and launches it; Wrath+'s game and `files/client-realm` untouched; set-up failures and a missing Wrath+ import are said and start nothing |
| New: `WrathppClientTest` | | the copy hard-links only game archives (never patch-4/F/M/U/V/W/Y/Z or their markers; since 2026-11-11 patch-M/U/V/Y/Z only, the HD look's F and W shared), copies the rest, leaves the game byte for byte as it was, refuses a copy inside the game; package manifest, when to install, tar paths |
| `ctl.sh` isolation | `realm/warcraft/wrathpp/tests/test-isolation.sh` | **pass, 61/61** (adds: `configure-realm wrathpp` touches nothing of main's/Remix's; archives may be shared read only, module patches may not). Fixed: the "no program started by another path" check had been passing because its grep pattern began with `-x` (read as an option); a mutation now makes it fail |

Not tested: the `wrathpp-server` package build (CI, `build-wrathpp-server.yml`), anything on a phone.

## 2026-11-11, the 32-bit add-on

| Test | Result |
|---|---|
| `WxlPatcherTest`: a synthetic 32-bit image patched by the Kotlin port | **same SHA-256** as WarcraftXL's own `PeImage.cpp` steps (`9b504c7d…`, built natively by `tools/patcher-reference/run.sh`) |
| `WrathppAddonTest`: the creator's GlueXML.toc (added last, other realms' module files dropped), the zip's paths | pass |
| App unit tests, all | **pass**: 623 tests, 0 failures, 20 skipped |
| `wrathpp-client.yml` job `addon` | **builds** (run 42928343249) after three fixes: WarcraftXL's test programs left out (they don't build on MSBuild here), only the targets shipped built, wxl.lua's target name |

Not run: anything in the game (the runtime under Wine/Box64, the native mod's reads, the creator's boxes).


## 2026-11-11, Shadowlands' options

| Test | Result |
|---|---|
| `tools/test_sl_inventory.py` (run by `protocol/tests/run.sh`): tables made in the test, the game's columns | **pass**, 4 tests: options and choices in the game's order per race and sex, other races' models left out, geoset ids (group × 100 + variant), materials, skinned models, restrictions for 3.3.5's classes (death knight only, all but death knights, demon hunter only, unlock type) |
| `sl_inventory.py build` on wago.tools' 9.2.7.45745 tables | 20 models, 277 options, 3529 choices (`docs/wrathpp/SHADOWLANDS_OPTIONS.md`) |

Not run: anything in the game; nothing drawn yet.

| `sl_looks.py package` (all twenty models fetched from wago.tools and converted here; 90 minutes) | 19 models built (the Blood Elf man left out), 6040 files, 847 MB; `sl_looks.py verify`: every file the new table rows name is in the package. Rendered (`render_m2.py`, Stand, a skin, face, hair and feature of each): the nineteen are right; the Blood Elf man's arms and legs came out shredded |
| `tools/test_sl_looks.py` (run by `protocol/tests/run.sh`) | pass, 2 tests: tables written and read back byte for byte, the rows of a race and sex replaced while the other sex's stay |
| App unit tests `com.logie.blizz.wrathpp.*` (`WrathppLooksTest`, `WrathppClientTest`) | pass: looks put in whole (game patch and server tables), a newer package replaces the old, a bad package leaves what was there, server tables restored from the patch; the game copy shares the HD look's patch-F/W and a copy made before gets them |
| `mod-allied-races` `tools/test_tools.py`, `test_safety.py` (the converter changed) | pass |
| `ctl.sh` isolation test | pass, 61/61 |

Not run: anything in the game; the package on a phone.


## 2026-11-12, Shadowlands' creator, the undead skins, the Dark Ranger eyes

Machine: Linux x86_64 container; LuaJIT 2.1, Python 3 with numpy and Pillow, Kotlin 2.0.21's compiler alone (no Android
SDK here: the app's own suite is CI's).

| Test | Result |
|---|---|
| `client-mod/tests/run.sh` | **pass**: the Lua mod's 29 + 5 checks as before; `test_creator.lua`, the new creator on a stand-in for the 3.3.5 screen: 57 checks (the two screens and the game's buttons moved; without the native mod the game's five; Shadowlands' rows in its order under its categories; a number unpacked into its options and packed back; a class's choices; an option nothing draws listed greyed; a choice by arrows and from the list, by the game's steps the shorter way round or the native set in one; the Undead switch, its skins, Randomize on either side; a list dragged, flicked, eased, the row not tapped; the character turned by a finger, carried on, turned by a held button; zoom by wheel, buttons and category; Finish, Back; a race without looks; an error putting the game's screen back) |
| `test_creator_data.lua` on `WrathppLooks.lua` made here from wago.tools' 9.2.7.45745 tables | **pass**: 19 races and sexes, 263 option rows, 3,439 choices each put on, read back as the one on, no other number moved |
| `protocol/tests/run.sh` | **pass**: as before, with `test_sl_creator.py` (6 tests: order, categories, parts of a number, choices as shown, swatches, class rules, an undrawn option, the Lua) and `test_undead_pack.py` (3 tests: skins in order, the textures read back at the sizes the models draw, the underwear note) |
| `sl_looks.py races` with the Dark Ranger eyes | only BloodElfFemale's looks change (eye 9 of 12 is 0xcc0000; the death knights' eye gone); the allied races' `races.json` is the same with and without the change to `races.py` |
| `sl_looks.py package` here (19 models, 6,040 files) | **pass** (its own `check_m2` on every model) |
| `WrathppUndeadTest` (the app's importer), compiled with kotlinc beside stand-ins for `WrathppLooks`' two names and Android's `Context` | **pass**, 7 tests: a table read back as written; skins as new colours after the race's own with a face row for every face number and an underwear row, nothing of the game's changed; applied twice or taken out leaves none twice; the zip taken in, a wrong one refused and the last kept; applied to a game and server folder, again after new looks, taken out |
| The importer on the looks made here and the 68-skin file | CharSections 3,721,240 -> 4,187,680 bytes, the same bytes for the game and the server; then `render_m2.py` (the game's reading of the tables and files) on each of the 17 models with each of its four undead skins: 68 of 68 drawn, the skins and faces in place |

### Not tested

- **The creator in the game**: nothing here runs the 3.3.5 client. On the phone the runtime, the native mod 0.1.0 and the
  Lua mod load (issue #99); whether `WrathPP_GetCustomization`'s numbers are right there, and everything of the new
  script, is not known.
- The native mod 0.2.0: compiled by CI only.
- The app's whole unit suite and its build with the new dialog and menu entry: CI (`build-apk`), run on this branch
  before the merge.
- The undead skins in the game, a character made with one accepted by the live server, and the import dialog on a phone.


## 2026-11-12 (later): a crash on Create Character, the reporter, Gear, Ralia's set, the women's underwear

**What was reported.** After app build 226 (the Shadowlands creator): "So far I'm not seeing the new options and also
I'm not seeing the shadowlands menu", then "The game crashed for me. When clicking on create character", then "I don't
think the reporter works right". Nothing had reached this repository after report #99 (03:49 UTC, app 219).

**Why nothing arrived.** (1) `BugReports.report` sends the same failure once a day, the same being the title with its
numbers out; the Wrath++ start report's title is one sentence, so every start after #99 was dropped on the phone.
(2) A game that closes by itself is reported for every game but World of Warcraft's client (`gameId == "wow-client"` is
left out of `GestureView`'s report). (3) The Wrath++ report went only 90 s into a launch. **The cause of the crash is
not known yet**: the client is the user's own and is not on this machine, so the creator has only been run on the
stand-in screen.

**What was changed.** `WrathppLogs` reads WarcraftXL's logs of the launches (the runtime writes `[crash]` lines: the
fault, the address as `WowWrathpp.exe+0x...`, the chain of calls; thirty launches are kept): each crash is sent once
(`Wrath++ crash`), as the app starts, before a start, 90 s after it and when the game's screen goes, so **the crash that
already happened is sent by the next build as the app opens**. The creator writes its steps to the same log
(`WrathPP_Log`, native 0.3.0). A crash with the creator on the screen leaves it out for that build. The start report
goes whenever its content changed.

**Tested here.** `WrathppLogsTest` (5: a crash read with where the creator was, handed out once across the log's
renaming, the creator's lines, the creator left out for one build), `WrathppBareTest` (1), `WrathppRaliaTest` (7, with
painted underwear over the looks' own and back), `BlpTest` (7, alpha), `WrathppUndeadTest` (7): 27 run here with
kotlinc against stubs of Android's classes; `UpdaterTest`'s six new ones (a local server that drops the connection)
run in CI only. The creator on the stand-in screen: 70 checks (Gear: 8, the log: 5). The native mod 0.3.0
(`WrathPP_SetGear`, `WrathPP_Log`) is compiled by CI (MSVC x86) and **has not run in the game**; nothing here has run
on a phone.

**Ralia's set, end to end here** (the app's own `WrathppRalia` and `WrathppBare`, compiled with kotlinc, on the looks
package as CI makes it and the user's zip): `lookFor` took the zip in by itself (693 textures) and not a second time;
`apply` put the set's over 133 of the looks' skins in 4.5 s (and nothing the second time); 127 of the women's 246
underwear rows lost their textures with it and the other 119 by `WrathppBare` (246 of 246); after Remove every skin
file is the looks' own again, byte for byte. Each written skin against the set's file it was made from (its body half
at 512 x 512): a mean difference of 1.1 to 2.2 of 255 a channel, the palette's doing. The looks' own skin of the same
number differs from the set's by under 2 on average too, which says the list of names pairs each skin with the right
file (the set repaints parts of the same picture). The list: 296 of the looks' skin files named (wago.tools' file
search, by the words `<model>skin`, and `nightelf_femaleskin` for the Night Elf women, whose files are named so); the
skins of Shadowlands' newer colours have names of another kind and keep the looks' own.

## 2026-11-12 (the crash on Create Character): what the phone's report said, and the fix

**The report** (#102 and #104, sent by build 232 from the logs on the phone; #104's launch was build 232 itself):
`unhandled access violation (0xC0000005) reading 0x1C at WowWrathpp.exe+0xE0A9B, the main thread, 25.8 s after launch`,
`eax=0 ecx=0 edi=004E0A60`, the frames above it the Lua machine's (`+0x45651C`, `+0x45898A`...). The creator's own lines
just before it: `creator: opened: native 0.3.0, looks' options in, undead skins in`, `creator: screen: race and class`,
then the crash 4 ms later.

**What is at that address** (the decompiled client at the pinned commit, `CharacterCreation_Scripts.cpp`): the function
at `0x004E0A60` is `Script_GetSelectedClass`, which pushes
`GetDisplayClassNameFromRecord(classRec, CCharacterCreation::m_character->m_data.m_preferences.m_sexID, ...)`: the
character's data is at +0x18 and the sex at +4 of it, so with no character it reads 0x1C. The creator called
`GetSelectedClass()` (to write the class's name over the class buttons) from its own frame's OnShow, which the game
runs before its own `CharacterCreate_OnShow`, whose `ResetCharCustomize` makes the character. That OnShow of the
creator's was added in build 226; builds 226 to 232 crash at the first opening of the creation screen in a launch.

**The fix.** Nothing of the creator runs before the game has its character (`hasCharacter`, asked by every handler:
the native mod's `WrathPP_GetCreating`, else a frame drawn since the screen was shown); the creator's own frame notes
that the screen was shown and the next frame opens the creator.

**Tested here.** The stand-in screen (`mock_glue.lua`) now has the game's character made by the game's own OnShow, and
counts a call made without it to any of the functions that read it unchecked. `test_creator.lua` shows the screen as the
client does (the creator's frame first, then the game's OnShow bound to its function, then a frame), with and without
the native mod: **the script of builds 226 to 232 fails it at `GetSelectedClass` and `GetAvailableRaces`; the fixed
script passes** (82 checks; the real data, 3,439 choices, with no such call). Not run in the game: the client is not on
this machine.

**The other record** (#103): a launch of 11 November (native 0.1.0, before this work), 7m 44s in: the game jumped to
`0x625AF8B0`, an address in no module, from `WowWrathpp.exe+0x28FAFC` under `WarcraftXL.dll+0xBDE1B`, with no frame
drawn for the 427 s before (the last events to mods are that old: the app was in the background). Not looked into.

## 2026-11-13: the rig, and what it found

**The phone, build 235** (report #107 and two screenshots): the crash on Create Character is gone (`creator: opened`,
`screen: race and class`), and 7.5 s later, at Customize: `creator: off: WrathppCreate.lua:331: bad argument #1 to
'min' (number expected, got nil)`. The game's own screen that came back was broken: no race, sex or class buttons, Back
over Randomize. The user: "Can you just test it on your rig rather than giving me shitty code".

**The rig** (`realm/warcraft/wrathpp/client-mod/rig`): the phone's own creation-screen files (issues #57 to #64), the
client's creation logic ported from its decompiled source, the game's tables, a widget engine that keeps to the
client's rules, the native mod's functions. Its picture of the game's own screen at the phone's shape matches the
phone's screenshot of it (the left panel with the banners, races, sexes, classes, the five rows and Randomize; the
race's and the class's texts on the right; Accept and Back under them; the name's box at the foot in the middle).

**The phone's failures on it, with the scripts the phone had.** Builds 226 to 232's script: `RIG CRASH: the game read
the character being created, and there is none` as the screen is shown (`GetSelectedClass` from the creator's own
OnShow, which runs before the game's). Builds 233 to 235's script with the phone's table: 124 race, sex and class
combinations opened and Customize tapped, **19 fail, every one a death knight**, each with the phone's own words
(`:331: bad argument #1 to 'min'`); the five numbers there read `face 1/0`: the game counts no face for a death knight
(the looks' faces carried flag 1, everyone's but a death knight's; 3.3.5's own tables have a death knight's faces
beside them, flag 5). The same script's full pass: 271 problems (lists of choices partly off the screen, rows with no
current choice); its off path: 3 failures.

**This build on it** (`run.sh`, two minutes): what the creator does, 33 checks; turned off, all 194 pieces of the
game's own screen where and as they are without the creator, none of the creator's left, the game's own buttons
working and Accept making the character chosen; every race, sex and class with every option's every choice: 9,094 taps
and 9,342 checks, 0 problems; without undead skins 7,360 taps, without the native mod 2,108, on a 4:3 screen 7,412, on
a 16:9 screen 7,412: 0 problems each. With the phone's present table (before the looks with the faces opened to every
class reach it) the creator stays on for a death knight and its skin cannot be changed, which is the game's own rule
there (`SetNextSkin` wants a face row the class may have).

**Not tested**: the game itself and the phone. The rig has no art and draws nothing; a wrong texture name, a font the
client lacks or a frame drawn under another are not seen on it.

**The textures' names, the same evening** (after CI's first run of the rig passed: `wrathpp-looks` run 19, "The creator
on the rig" 2 min 2 s, the looks with the faces opened to every class published). The rig now keeps every texture file
a Wrath++ script names with the line that named it, and each has to be a file the client is known to have: named by
the phone's own glue files, the icon of a 3.3.5 item or spell (`ItemDisplayInfo.dbc`'s icon column, `SpellIcon.dbc`),
or in `rig/textures335.txt` (20 names, each checked against the 3.3.5 interface file that uses it:
wowgaming/3.3.5-interface-files). 31 files named by the creator; **one was not a 3.3.5 file**:
`Interface\Buttons\UI-RefreshButton` (the reset-view button; 3.3.5's own Refresh buttons are text buttons), now
`Interface\PaperDollInfoFrame\UI-GearManager-Undo` (`PaperDollFrame.lua`). The fonts and button templates the creator
names (`GlueFontNormal`, `GlueFontNormalLarge`, `GlueFontHighlight`, `GlueFontHighlightSmall`, `GlueButtonTemplate`,
`GlueButtonSmallTemplate`) are each named by the phone's own files. Still not seen on the rig: how a texture looks at
the size it is given, and a frame drawn under another.

## 2026-11-13: Shadowlands' own art and layout

The user: "Literally why not just use the EXACT ASSETS from wago tools". The creator's buttons had been 3.3.5 pictures
standing in. What was done and run here:

- **The art** (`tools/sl_ui_art.py`): the atlas tables and sheets at 9.2.7.45745 from wago.tools; 238 pieces from 9
  sheets cut pixel for pixel, each a file of its own (a power-of-two canvas, the piece's edges carried outwards, plain
  32-bit colour with smaller levels), 72 of them a round button's picture with Shadowlands' mask already on it; 45 MB
  on disk, 8.2 MB zipped. A sheet of 30 of the pieces was looked at: the category pictures, the gold ring, the dice,
  the grey square button and its gold pictures, the dropdown box and arrows, a race's and a class's portrait trimmed
  round, the factions' rings and crests, the red button's three parts, the list's frame. The 3.3.5 client reading plain
  32-bit BLPs is read from its source (`CBLPFile::Lock2`, `COLOR_RAW`; `Script_SetTexture` gives nil for a file it
  cannot set), **not seen on the phone**.
- **The layout**: Shadowlands' own numbers from `Blizzard_CharacterCreate.xml`, `Blizzard_CharacterCustomize.xml` and
  `SharedUIPanelTemplates.xml`/`.lua` at 9.2.7 (Gethe/wow-ui-source), listed in README.
- **The rig painted** (`tools/paint.py`): both screens and an open list of 17 colours, at the phone's shape. The first
  picture showed the classes' row over Back and Customize (the phone's screen is narrower than 16:9) and "Death Knight"
  over "Shaman" (the name's box was wider than Shadowlands'): both fixed, and the rig now checks that no two of the
  creator's buttons lie over one another (with the first fault put back it finds 248, each named).
- **`run.sh` with the art** (about four minutes): what the creator does, 33 checks; turned off, the game's own screen
  whole; every race, sex and class with every option's every choice, 9,094 taps and 9,590 checks, 99 textures named, 86
  of them Shadowlands' pieces; without undead skins 7,360 taps; without the native mod 2,108; on 4:3 and 16:9 screens
  7,412 each; without the art 7,412 (21 textures, none of the art) and the off path again; with the art in and the game
  not setting its files 7,412: 0 problems each.
- **The app** (`WrathppArt`, 5 tests run here with kotlinc: the art put in as `Data/patch-S.MPQ`, a newer package
  replacing the old whole, a package without its table or with a path out of it leaving what was there, a file of the
  player's by that name replaced in the copy only, the creator's patch taking the table). The download and the whole
  app build: CI.
- **The packages**: two copies of the art made a second apart zip to the same checksum (`bda3d1e6...`); a zip made as it
  came did not, which is why every run of the workflow sent the looks to the phone again. Whether the looks' own files
  come out the same from one run to the next is seen from the next two runs' checksums.

**Not tested**: the game and the phone. Whether the art's files draw there, how the screen looks at the phone's size,
whether a tap lands where the rig says. Still not drawn by the game: the options marked "Not drawn yet".

**The name and the arrows, the same night** (build 241). The name's box is Shadowlands' (`NameChoiceFrame`,
`SharedEditBoxTemplate`: "Name" at 18 in white, the entry box's left piece 13 wide, its right 314, the middle between;
the game's own box laid over it without its border and its own "Name", as it was again when the creator goes off); the
foot's buttons carry `common-icon-forwardarrow` and `-backarrow`, 8 x 13. Looked at in the rig's painted picture;
`run.sh` with the art: the same nine passes, 0 problems, 104 textures named, 91 of them Shadowlands' pieces; the off
path still leaves all of the game's own screen as it is without the creator.

## 2026-11-13: the phone as the place where the game is seen

The 3.3.5 client the project builds from source in CI needs the game's own data to start (its shaders are the game's,
translated; its interface art and fonts the game's), and no machine here has that data: the creator cannot be run in
the game anywhere but on the phone. So the phone's game takes pictures of the creator and the app sends them
(`WrathppPictures`, README). Run here:

- the creator on the rig (`behaviour.lua`, 40 checks): no picture before a screen has been up a moment; one of the
  first screen, one of Customize, one of the first list opened, each said in the log; three at most; none when the
  app has not asked;
- `WrathppPicturesTest`, 5 of 5 with kotlinc: pictures asked for until those of this build, art and looks went (the
  first asking's hour kept); only the game's JPEGs taken since the asking go, the newest three; what each is of is
  what the creator's log said; a picture goes whole in one issue or in parts, read back byte for byte; titles that
  differ in more than digits (the reports' queue takes two titles alike but for their digits for one report: found
  while reading the code back, before it ran anywhere);
- `rig/tools/fetch_pictures.py` on issues made as the app makes them: a picture of 100,000 bytes in three parts and one
  of 30,000 in one, read back whole.

**Not run**: Android's making a picture smaller (`shrink`: `BitmapFactory`, `Bitmap.compress`), the game's
`Screenshot` under Wine on the phone, the sending. If the game writes no file there, the report says so.

## 2026-11-13: build 241 on the phone, the first sight of the art in the game

The user's screenshot of the race and class screen: **Shadowlands' art draws in the game** (the faction crests and
rings, the race and class portraits, the sex pictures, the gold ring of the one chosen, the red Back and Customize with
their arrows, the class names on two lines), so the 3.3.5 client reads the art's plain 32-bit BLPs on the phone. Two
faults, each found in the client's source and each now a rule of the rig:

- **The screen green but for a strip in the middle, where the character shows.** The screen-edge shading
  (`charactercreate-vignette-*`) is pieces 1 unit thick; the client draws no texture smaller than 8 on a side ("Texture
  size must be at least 8x8", `CreateBlpTexture` in `Texture.cpp`: a solid green texture instead), and the four
  pieces cover all of the screen but that strip. `sl_ui_art.py` now makes every file at least 8 x 8 (the piece's edge
  carried outwards, as for the rest); `full.lua` fails on an art file under 8 on a side (`RIG_ART_LIST`): on build
  241's art it names five.
- **The race and class portraits square, their clear corners drawn dark.** The creator called `SetDesaturated(nil)` on
  each picture of a round button; the client puts its own pixel shader on a texture for either value ("UI" or
  "Desaturate", `CSimpleTexture_Scripts.cpp`), where a texture left alone has none, and through it the portraits'
  alpha did not show. The creator dims a button that cannot be chosen by its colour only now; the rig notes every
  `SetDesaturated` and `full.lua` fails on one in a Wrath++ script: on build 241's script it finds it.

Run here after: `run.sh` with the new art, nine passes, 0 problems. Not run: the game; the next pictures are the phone's.

## 2026-11-13: the swipe on the creator, and the models' seams

The user, on build 243: "This is soooo much better ... The swipes on the character creator should not be pressing the
keyboard only turning the model. Also the models have lots of seam gaps." The phone's own pictures arrived too (issues
#109 to #111, build 242's two screens as the game drew them: `rig/tools/fetch_pictures.py` put them together).

**The swipe.** `WowGestureView` knew the creation screen only by a picture of the 3.3.5 creator's banners; on the
Shadowlands screen a finger walked. Now the creator says it is up (`WrathPP_SetScreen`, native 0.4.0; the touch's
`CreatorScreen`). Run here: the rig, `behaviour.lua` 45 checks (the creator up on both screens with nothing to drag on
the first, the option list's place on Customize, an open list's place, said once and not every frame, "creator 0" as it
closes); `CreatorScreenTest` 3 of 3 with kotlinc; the native mod's new function compiled here for syntax with g++ and
the SDK's headers (its Windows part only by reading: MSVC builds it in CI). Not run: the native mod in the game, the
touch on the phone.

**The seams.** Found in `decimate.py`: a vertex on a section's outline could slide along it, and two sections cut down
alone came apart where they meet. `m2.py` pins the joins and the bare body's outlines. Run here, from the cached source
files: all nineteen models converted (each within 3.3.5's 65535 indices), the openings measured before and after (README);
the Human woman rendered from four sides with the old and new cut, the old one's crack across the knee and slivers at
the ankle and heel found by machine (background seen through the figure) and by eye, gone in the new; `test_tools.py`
(two sections cut down pinned meet at every point of their join; not pinned they do not). Not run: the models in the
game; the next looks package carries them.

## 2026-11-13: the list of options under a finger

The user: "the screen needs to be smooth when scrolling in the character creator on the right". Found in the creator:
the rows read again four times a second while the list moved (every row's text and pictures set again), the list
jumping the drag's first six units as it began, a flick that only aimed at one place and eased there, the content on
fractions of a pixel, the word to the touch made every frame. Run here: `behaviour.lua`, a finger dragging the longest
list of a Human man frame by frame at 30 a second: unit for unit with the finger and no jump as it begins (steps 0, 7,
7, 7 for a finger moving 7 a frame); let go moving, on 45 units more, slowing every frame, stopping, never past the end;
not read again while it moved, read again once at rest; stopped then lifted, it stays; placed on whole pixels of 1248;
the whole rig with the art, 0 problems. Not run: the game; how many frames a second it draws on the phone.
