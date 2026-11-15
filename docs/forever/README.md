# WoW Forever (new integration, 15 November 2026)

Written from nothing. No earlier Forever code, patch, binary, launcher, shortcut or data of this repository was read,
restored or reused (`files/forever`, `imagefs`, `imagefs_shared`, `forever-arm64` are neither read nor touched). The
sources are Karrz's current projects, pinned in `realm/warcraft/forever-new/forever-version.env`.

## What exists

| Part | Where | State |
|---|---|---|
| Server source pin (Karrz1/TrinityCore `forever-bots` @ `51b5ae09…`) | `forever-version.env` | pinned, commit checked to exist |
| arm64 musl compile (PlayerbotV2 on, CMake lines checked) | `realm/scripts/compile-forever-new.sh` | **never run** |
| Package (programs, libs, MariaDB, openssl, shim, SQL, configs, legal) | `realm/scripts/package-forever-new.sh` | **never run** |
| CI: compile, package, run the shipped loader, manifest, publish release `forever-android-server` | `.github/workflows/build-forever-native.yml` | **never run**; the release does not exist yet |
| App: package download (resume, SHA-256, bounded extraction, swap, rollback) | `forevernew/ForeverPackage.kt`, `ForeverDownloads.kt` | unit-tested |
| App: client detection (`.build.info`, `Data`, `_forever_`, build list) | `ForeverClient.kt` | unit-tested on synthetic folders; the real `.build.info` Product value is unverified |
| App: world + hotfix databases out of Karrz's repack by range requests | `RangeZip.kt`, `ForeverRepackData.kt` | unit-tested; the two SHA-256 values were measured against v0.1.36.1 |
| App: MariaDB-compatible SQL filter, DB plan, accounts, configs, RAM-aware bot presets | `SqlCompat.kt`, `ForeverDb.kt`, `ForeverAuth.kt`, `ForeverConfig.kt` | unit-tested text |
| App: map extraction plan (upstream's four tools), checkpoints, 45 GB check | `ForeverMaps.kt` | unit-tested plan |
| App: add-on install into `_forever_/Interface/AddOns/ForeverBots` | `ForeverBots.kt` | unit-tested |
| App: process start-up through the musl loader, readiness, stop order | `ForeverServer.kt`, `ForeverSteps.kt` | **not run anywhere** |
| App: stage machine and the Install & Play dialog | `ForeverInstaller.kt`, `ForeverPlay.kt`, `ui/ForeverDialog.kt` | order unit-tested; the dialog **not compiled or seen** |

## The game side (added after the first pass; what each piece was checked against)

| Piece | What it does | Checked |
|---|---|---|
| `tools/foreverkey/foreverkey.c` → `foreverkey.exe` | Written new from upstream's `Play-WoWForever.ps1`: starts `Wow.exe -config ForeverLauncher.wtf`, finds the client's 12-record login key table in memory by its layout and writes the realm's public key into region group 8's record; keeps watching | Run under the phone's own Wine 10.10 (x86_64, Xvfb, `scripts/build-tools.sh`'s target) against a stand-in client holding such a table: the key was written to record 8 and records 7 and 9 were untouched, and the arguments were passed as `-config ForeverLauncher.wtf`. **Not against the real client.** |
| `WineCerts.kt` | Adds the realm's own name-constrained root CA to the games' Windows root store (registry `Blob`, both views) | Same Wine: a chain check of the portal certificate went from `CERT_TRUST_IS_PARTIAL_CHAIN` (0x10000) to no error after the entry was added. **Whether the real client uses that store is unverified** (upstream imports into Windows' `LocalMachine\Root`, which this matches). |
| `forever_resolve.c` (preloaded into the servers) | The login server resolves `trinity.actual.battle.net` at start; Android has no hosts file an app may edit, so any name under `.actual.battle.net` answers 127.0.0.1 for these programs only | Built and run with `LD_PRELOAD` on glibc here; not on musl/Android. |
| `Offline.hosts(…, local)` | The games' runtime hosts file (never Android's) maps the portal to the phone | Unit-tested text. |
| `ForeverLaunch.kt` | `WTF/ForeverLauncher.wtf` (portal, language from `.build.info`, screen), `foreverkey.cfg`, the keeper copied beside the client, the entry Winlator starts | Unit-tested files; the player's `Config.wtf` is never changed. |
| `ForeverClientImport.kt`, `ForeverSafTree.kt` | "Import & Install": one Android folder pick; copies only `.build.info`, `Data`, `_forever_` into the app (resumable, never writes to the picked folder) | Walk, resume, refusals and space check unit-tested on a fake tree; the Android picker/DocumentsContract part is **not compiled or run**. |
| `ForeverAuth.kt` account | Upstream's way: the world console's `bnetaccount create`, then `account set gmlevel <id>#1 3 -1`; certificates from upstream's own openssl settings | Command text and SQL unit-tested; not run. |
| `ForeverPlay.kt` | One action: install, start the realm, make the account, then `WindowsRuntime.play` like Legion/Wrath++ | **Not run.** |

## What is still not done or not known

1. **Nothing has run on a phone** (Z Fold) and the real WoW Forever client was never available here. Unknown until then: whether the client runs under Wine/Box64 and which graphics path it needs (D3D11 through DXVK is the shared container's default), whether it trusts the Wine root store, whether the key table is found in a Box64-run client, and how long a start takes.
2. **The server package has never built successfully.** The first CI run reached the compile and stopped on musl incompatibilities in the bundled gSOAP (patched at build time in `compile-forever-new.sh`, along with `NOJEM`); more may follow. The loader step, the manifest and the release come after that, and the release is published only from `main`.
3. **Getting the client**: there is no authorised download; the user installs Forever with Battle.net on a computer and picks the folder once.
4. **Map extraction space**: ~45 GB at the peak per upstream; the app refuses below that. Streaming extraction is not written.
5. **Optional vanilla 1.12 values**, **backup/restore/repair/update buttons** and an account editor are not written.
6. `Realm.AlsoAcceptBuilds` needs each build in `auth.build_info`; nothing checks that yet. Whether the repack dumps carry the `updates` rows is unknown.

## Facts found in Karrz's sources that shaped this

* The world and hotfix databases (`sql/world.sql` 613,883,583 bytes, `sql/hotfixes.sql` 339,516,733 bytes) are only in the Windows
  repack, not in the source tree. They are data, so the app reads those two entries (pinned SHA-256) and nothing else of it.
* `sql/old` is 4.2 GB and is never packaged.
* `playerbot_shared_schema.sql` uses `utf8mb4_0900_ai_ci` and a MySQL 8 `ENCRYPTION` option, which MariaDB can reject:
  `SqlCompat` rewrites them while streaming the file in.
* `RealmID` must be 70 and `auth.realmlist` the same (upstream `doc/ForeverSetup.md`); `Realm.AlsoAcceptBuilds` is comma
  separated and needs each build in `auth.build_info` (checked by neither the app nor the tests yet).
* The extractors are `mapextractor -i … -o … -e 15 -f 1 -l enUS`, `vmap4extractor -d …`, `vmap4assembler Buildings vmaps`,
  `mmaps_generator --input … --output …`; the product defaults to `wowf`.
* Own ports: database 3313, bnet 1120, REST 8082, world 8097, instance 8098 (none used by another realm).

## Verified from here

`client-builds.txt` and `SHA256SUMS.txt` match the pinned hashes; the pinned commit is the head of `forever-bots`; 41 unit
tests pass in a standalone JVM harness (Kotlin compiler + JUnit against the new files). The Gradle/Android build was NOT run
(no Android SDK in this environment), so the Compose dialog and the Android-API lines (`ForeverLayout.of`, `ForeverPlay`) are uncompiled.
