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

## What does not exist (do not read the page as a working game)

1. **Starting the game.** Upstream needs the login certificate trusted inside the game's Wine, the portal name resolving to
   the phone inside that Wine only, and the launcher writing the server's public key into the running client every start
   (`WoWForeverLauncher.exe`, release asset 19). None of that is built or tested. The installer ends at "server running".
2. **Getting the client.** Karrz ships no client and no authorised Battle.net download is implemented. The client is the user's
   own installation; the in-app "Import & Install" (folder picker, copy, validate) **is not written**. `ForeverSteps.client()`
   reads `files/realms/forever-v2/client-path.txt`, which nothing creates yet.
3. **Any phone run**: the loader running these programs inside the app sandbox, MariaDB's bootstrap, the SQL updater on Karrz's
   dumps (whether their `updates` rows are present is unknown), map extraction time and space on a phone, bots under memory.
4. **Map extraction space**: upstream says ~45 GB at the peak. The app refuses below that; streaming extraction is not written.
5. **Optional vanilla 1.12 values** (step 11), **backup/restore/update/repair buttons** (step 15) and the account editor.
6. The `account set gmlevel 1#1 3 -1` console line and `bnetaccount` commands are taken from TrinityCore's command set; unverified here.

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

`client-builds.txt` and `SHA256SUMS.txt` match the pinned hashes; the pinned commit is the head of `forever-bots`; 34 unit
tests pass in a standalone JVM harness (Kotlin compiler + JUnit against the new files). The Gradle/Android build was NOT run
(no Android SDK in this environment), so the Compose dialog and the Android-API lines (`ForeverLayout.of`, `ForeverPlay`) are uncompiled.
