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
