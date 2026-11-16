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

**First phone run (Z Fold 8, 16 November 2026), two stalls, both found and fixed:** (1) "Storing the build's metadata" never moved: the cdns file's plain `Hosts` include `level3.blizzard.com`, an HTTP-only server, which the app asked over HTTPS first; the HTTPS hosts of its Servers column now come first and a host that answered stays first. (2) After the metadata it showed "0 / 0 MB (5 of 5)" and sat there: the next step downloaded and parsed Blizzard's file list (2.2 million entries) with an object per entry and a decoded copy of 56 MB twice, far over a phone's heap. Reproduced on the desktop with `-Xmx256m` (an `OutOfMemoryError` reading the encoding file's 60 MB frames); the list is now read in place from its bytes, the wanted files are numbers in primitive arrays, the writer keeps its index in arrays, one decoded frame is cached, and every phase reports progress. With a 256 MB heap the whole plan (1,042,079 files, 48,230 MB, all 1404 archive indexes) now completes in 99 s, and the essential install (439 MB + 39 programs) runs end to end, opens in CascLib and passes `ForeverClient.inspect`. The app also asks for a large heap now.

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
