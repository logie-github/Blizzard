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

### Not tested

- The client: not built here (no MSVC); the CI probe's result is recorded below once it runs.
- Anything drawn: no extended category is rendered anywhere yet.
- The Lua mod inside the real WarcraftXL runtime.
- The server's arm64/musl build (the phone's) with the patch and module: only this machine's x86_64
  glibc build was compiled and run.
- Android: nothing.
- `ctl.sh` under Android's `/system/bin/sh` or busybox: run under dash (`sh`) here.
- The Android app's unit tests (`./gradlew :app:testDebugUnitTest`): this machine has no Android
  SDK; no app source changed. CI's `build-apk` runs them on the push to `main`.
