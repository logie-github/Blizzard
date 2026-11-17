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

## The client: downloaded from Blizzard's own servers (new)

The game is not bundled and not mirrored: `forevernew/tact/*` is an installer that reads Blizzard's public version server
(`https://us.version.battle.net/wowf/versions`, `.../cdns`) and content servers (`us.cdn.blizzard.com`, `tpr/wow`), the ones the
Battle.net app uses, with no account. Written new from the documented TACT/CASC formats and CascLib's source; nothing from earlier work.

What was measured against the live servers on 15 November 2026 (build 70938, `1.60.1.70938`):

| | |
|---|---|
| Whole download manifest, all platforms and languages | 2,208,764 files, 118 GiB |
| Windows + x64 + English text and speech | 47.1 GiB: 0.43 GiB at Blizzard's priority 0, 36.4 GiB priority 1, 10.2 GiB priority 2 |
| Programs (install manifest, Windows x64) | 39 files, about 140 MB, each checked against its MD5 |
| The installer's essential run (`maxPriority 0`) | 1,487 files / 439 MB into `Data/data` plus the programs, about 1 GB on disk, a few minutes |

Checked: the storage it writes (index files with Blizzard's Jenkins-hash guards, 30-byte local headers, data files) was opened with
**CascLib itself** (the library the server's extractors use) on that essential install: it opened the build, resolved the TVFS root,
listed 2,209,354 files, and read the build's encoding (141 MB), download, install and root files and the files it holds with no error. `ForeverClient.inspect` accepts the folder
(`Ok`, build 70938, `_forever_/Wow.exe`). The real `Wow.exe` from that install was then started under the phone's own Wine
(x86_64 desktop rig, no GPU): it loaded, created its window, wrote its logs and started its network layer.

Not checked: that the real client accepts this storage the way it accepts Battle.net's own (CascLib is lenient where Blizzard's code may not be:
the index files here have no second journal page and there is no `shmem` or `.product.db`); the full 47 GiB download (only the
essential set was run); the client past its first seconds. **On the desktop rig the game's network-adapter enumeration crashes in Wine's
`iphlpapi` (a 10-line program that calls `GetAdaptersAddresses` crashes the same way there, so it's Wine and that sandbox's interfaces, not the
game or this app); whether the phone's Wine does the same is unknown.** No GPU on the rig, so no picture was drawn: the login screen, an account,
a character and an NPC were not reached.

## Run on a rig (16 November 2026): the real servers from the CI package, under qemu

The package CI built (`forever-android-arm64.tar.xz`, 51 MB; TrinityCore `51b5ae0971fa`, MariaDB 11.4.13, all linux aarch64 musl) was
unpacked on the desktop rig and run through its own musl loader under `qemu-aarch64-static`, with the app's own code producing the inputs
(compiled in a JVM harness): the bootstrap SQL, the database/user SQL, the `SqlCompat` filter, the configs, the certificate commands and the account SQL.

| Step | Result |
|---|---|
| `bnetserver`, `worldserver`, `mariadbd` `--version` through the shipped loader | run (TrinityCore 51b5ae0971fa forever-bots; MariaDB 11.4.13) |
| Real range read of `sql/world.sql` and `sql/hotfixes.sql` out of Karrz's 490 MB repack | both matched their pinned SHA-256 |
| MariaDB bootstrap with the app's SQL | **failed twice, fixed**: bootstrap mode takes one statement per line; 11.4's files are `mariadb_*.sql`, not `mysql_*.sql` (and the install-db order). Now exit 0, `mysql`, `performance_schema`, `sys` made |
| Database, user and 5 schemas from `ForeverDb.createSql` | created |
| Imports through `SqlCompat`: auth, characters, playerbot schema (34 lines rewritten) and data, hotfixes (484 tables), world (270 tables) | all loaded; **world.sql stopped at its first view: `ERROR 1227` (a `DEFINER` of a user that isn't the importer): the filter now drops `DEFINER=`**; the 3 views then created |
| Certificates: the app's openssl commands run with the package's own `openssl` | root (name-constrained to `actual.battle.net`) and `trinity.actual.battle.net` leaf; `openssl verify` OK, SAN and EKU as upstream |
| `bnetserver` with a config of only the app's settings | **exited with code 1 and no message**; built on the `.conf.dist` with the app's settings put in (as now written) it runs: auth updates applied, REST handlers registered, `Added realm "Forever" at 127.0.0.1 (port 8097)` |
| TLS to `trinity.actual.battle.net:8082` | the generated chain verifies against the generated root (`openssl s_client`, `curl --cacert`) |
| REST login with `logie@wow.server` / `Logie`, the account made by `ForeverAccount.sql` (SRP v2, in Kotlin) | `login_ticket` returned; a wrong password and `logie` (other case) return no ticket. The verifier for a fixed salt is now a unit test |
| `worldserver` | connected, applied the world/custom/hotfix updates, `Using World DB: TDB 1210.26091`, `Realm running as realm ID 70`, then stopped on **`Map file .../0000_43_31.map does not exist`**: it needs the extracted map data |

| `mapextractor` (arm64, from the package) on the essential install the app's TACT installer wrote | **opened the storage** (`Opened casc storage .../Data`, `Detected client build 70938 for locale enUS`), then stopped at the first db2 (`AccountStoreCategory.db2: FILE_NOT_FOUND`), which isn't in Blizzard's priority-0 set: the realm needs the full download. It also warns that its online encryption-key list returned `426` here (non-fatal; some encrypted files may not extract) |

Two more facts from the real `Wow.exe` on the rig (Wine 10.10, no GPU): its first act is to call `GetAdaptersAddresses`, which crashes inside Wine's `iphlpapi`
here (reproduced by a 10-line program; the game's own crash handler writes a report, then the game stalls); and **the client refuses a replaced `iphlpapi`**
(a stub, or a forwarding wrapper, in the game folder or in the prefix's `system32`: "Internal Error 0x1100, Unsupported software detected, IPHLPAPI.DLL"), so
that crash can't be worked around by a DLL override. Whether the phone's Wine hits it is unknown; if it does, the fix is in the runtime's Wine, not in this app.

**The realm's map extraction found no file in the downloaded game (the phone, 16 November 2026), found and fixed:** "map data: Extracting maps and data tables failed (code 1). Extracted 0 files … Invalid CinematicCamera.db2 file format! FILE_NOT_FOUND", after the whole download. The row above read the same error on the essential install as "not in the priority-0 set"; it was not that. Blizzard's download list has that file (number 1294214) at priority 1 with the tags the app selects, and every selected file has priority 0, 1 or 2, so `ALL` is all of it. The cause: build 70938's config names a VFS root and **583 further VFS files** (`vfs-1` … `vfs-583`, 133 MB together), and CascLib reaches the game's file numbers through them (TVFS, then the root they lead it back to). The installer stored the VFS root alone, so CascLib opened the storage and listed 2.2 million entries with no file number among them. Reproduced here with CascLib (upstream, built for this machine) on a storage this installer made: every file asked for by number, error 2. With the VFS files stored (`TactInstaller.metadataKeys`): 40 of 41 sampled priority-0 files read, the 41st being a `HighRes` variant the app's tags leave out; and the package's own arm64 `mapextractor` (under `qemu-user`) on that essential install extracted 93 db2 files and said `FILE_OFFLINE` for the ones not downloaded, where it had said `FILE_NOT_FOUND` for all. A game already downloaded is completed, not downloaded again: before the extraction, `ForeverClientDownload.repairIndex` fetches the VFS files (and the root, by its key in the encoding file) the storage lacks, 587 files in about four and a half minutes here, one after another. **Not checked:** the whole extraction on a whole download (47 GiB; this machine has 9 GB free), and anything on a phone.

**The database step after the maps (the phone, 16 November 2026: the map building ran to its end), two faults, found and fixed:** "mariadbd did not become ready in 3 minutes", with MariaDB's own log under it saying *ready for connections* on port 3313; then, at the next press, "Port 3313 is already in use; mariadbd can't start". The wait was three minutes by the clock, looked at every half second: an app Android stops while it is out of sight (after hours of map building) finds its three minutes gone without having looked once more, and gives up on a database that is up. Android then ended the app; `mariadbd`, started by it, went on by itself and held the port, and the new app knew nothing of it. Now the wait is counted in looks and looks once more at its end (`ForeverLeftovers.await`), and a program of this server left running (its pid file's process, when its command line names this server's `bin`) is ended with SIGTERM before another is started (`ForeverLeftovers.end`; SIGKILL after a minute). Checked here with the package's own `mariadbd` under `qemu-user`, created and started the app's way: ready in 3 s, and the one left running ended cleanly (*Shutdown completed*), the port free after. Not run on a phone.

**The realm's settings (the phone, 16 November 2026: the database made and filled), found and fixed:** "database: …/server/etc/worldserver.conf.d/zz-0-playerbot-defaults.conf: open failed: ENOENT". `writeConfigs` copied the package's `worldserver.conf.d` files "into the settings folder", which is that same folder (`ForeverLayout.etc` is `server/etc`): a file copied onto itself with `overwrite` is deleted first and then not found, so each Play deleted the first file of the folder and stopped. The copy is gone (the files are in place as unpacked). The file it deleted is put back by `ForeverPackage.restoreEtc` at the package step: the installed package's own archive is fetched (51 MB, once for a server installed before), its `etc/` files that are missing are written and none that is there is touched, and the list of them is kept (`manifests/installed-etc.txt`) so a later loss is seen without the archive. Checked here against the published package: the deleted file back, the same bytes. Also: a new server package set the old server's folder aside whole, **the map data in `server/data` with it** (hours of work on a phone), to be deleted after the next good start; `install` now carries `data` over to the new server. Not run on a phone.

**The login server "did not become ready" (the phone, 16 November 2026: the database and the settings done), found and fixed:** "login server: bnetserver did not become ready in 3 minutes", over its REST handlers and `Added realm "Forever" at 127.0.0.1 (port 8097).` It was up. The app waited for a line with "Bnet server", "Listening", "Starting up" or "ready", and the login server prints none of them: "Added realm" is its last word, after which it listens. `ForeverServer.BNET_READY` now is that line (the port being open is asked beside it, as before). Run here: the package's own `bnetserver` under `qemu-user`, against the package's `mariadbd` with the auth base and its updates applied and the app's settings in its `.conf.dist`: the same last lines, ports 1120 and 8082 open, the old words in none of its 60-odd lines. The world server's line (`World initialized in`) is in its program's own text; it was not run here (no map data on this machine). Not run on a phone.

**The realm up, and Winlator's file manager in place of the game (the phone, 16 November 2026), found and fixed:** Play ended in a window named "Computer" listing C:, D:, S:, T:, X:, Z:. The game is in `files/realms/forever-v2/client`, and the games' Windows had drives for the games, the saves and the importers' work folder only: a program on no drive has no Windows path (`WineUtils.unixToDOSPath` gives none), and Winlator then starts nothing and shows its file manager. `WindowsRuntime.drivesOf` adds **F:** for `files/realms` (set on the container at every start, as the others are); `ExecPathTest` has the program's path with and without it (`F:\forever-v2\client\_forever_\foreverkey.exe`). Not run on a phone. What comes after it has not run on a phone either, and is where the earlier work stopped: the PC client (`Wow.exe`, x86_64) through Box64, which drew no window there (reports 174 to 181).

**The world server ended itself once loaded (the phone, 16 November 2026: with the game's drive in, the next Play):** "worldserver stopped (code 139: SIGSEGV) … TC> World Thread hangs for 60029 ms, forcing a crash! … Main.cpp:645 in Handler ABORTED". The world had loaded (its console prompt is up, after the bots' quest index). That line is the core's own freeze watch (`MaxCoreStuckTime`, 60 in the package's `worldserver.conf.dist`): it ends the server when the world's loop has not turned for a minute. On a phone a minute goes by without a fault: Android stops the app's programs while the app is out of sight, and the bots' first set-up holds the loop for long. The app now writes `MaxCoreStuckTime = 0` (off). Which of the two held the loop that minute is not known; not run on a phone, and the world server was not run here (no map data on this machine).

**Failures are reported (17 November 2026).** Until then every failure of the install or the realm's start reached the developer as a screenshot only, and a crash of the whole app as the word "crashed": no Forever report had arrived in two days. `ForeverPlay.sendFailure` now sends one for each (title "WoW Forever: <the step's message>"; the build, the phone's RAM and, attached, its memory and processes; the event log and the last of `worldserver.log`, `bnetserver.log` and `mariadbd.err`). A crash that ends the app itself leaves nothing to send; the system's exit reason of the last run is in the next start's report (`Diagnostics`).

**First phone run (Z Fold 8, 16 November 2026), two stalls, both found and fixed:** (1) "Storing the build's metadata" never moved: the cdns file's plain `Hosts` include `level3.blizzard.com`, an HTTP-only server, which the app asked over HTTPS first; the HTTPS hosts of its Servers column now come first and a host that answered stays first. (2) After the metadata it showed "0 / 0 MB (5 of 5)" and sat there: the next step downloaded and parsed Blizzard's file list (2.2 million entries) with an object per entry and a decoded copy of 56 MB twice, far over a phone's heap. Reproduced on the desktop with `-Xmx256m` (an `OutOfMemoryError` reading the encoding file's 60 MB frames); the list is now read in place from its bytes, the wanted files are numbers in primitive arrays, the writer keeps its index in arrays, one decoded frame is cached, and every phase reports progress. With a 256 MB heap the whole plan (1,042,079 files, 48,230 MB, all 1404 archive indexes) now completes in 99 s, and the essential install (439 MB + 39 programs) runs end to end, opens in CascLib and passes `ForeverClient.inspect`. The app also asks for a large heap now.

**Download speed (measured on the desktop rig against Blizzard's servers, priority 0 to 1, English text, 256 MB heap):** one connection 9 MB/s, 8 connections 60 MB/s, 16 connections 115 MB/s (the default now). The index lookup (1404 files) runs on 16 connections too. Voice-over audio is not downloaded (about 3 GB; the game is silent where it would speak): the whole set is about 44 GB (36.9 GB at priority 0 and 1, the rest at priority 2).

What this rig could not do: the maps need the full client (47 GiB) and then the map extraction (about 45 GB at its peak, hours); the rig has 18 GB free.
So the world server was not brought up, and nothing past the login server's REST login (the Battle.net client handshake on port 1120, the realm list,
the character screen, a world, an NPC) has been run: no GPU here, and the real client crashes in Wine's network code on this rig.

## What is still not done or not known

1. **Nothing has run on a phone** (Z Fold) and the real WoW Forever client was never available here. Unknown until then: whether the client runs under Wine/Box64 and which graphics path it needs (D3D11 through DXVK is the shared container's default), whether it trusts the Wine root store, whether the key table is found in a Box64-run client, and how long a start takes.
2. **The server package has never built successfully.** The first CI run reached the compile and stopped on musl incompatibilities in the bundled gSOAP (patched at build time in `compile-forever-new.sh`, along with `NOJEM`); more may follow. The loader step, the manifest and the release come after that, and the release is published only from `main`.
3. **Getting the client**: downloaded from Blizzard's own servers by the app (above); "Import & Install" stays as the way to use a folder you already have.
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
