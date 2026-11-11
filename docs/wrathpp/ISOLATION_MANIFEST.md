# Wrath++ isolation manifest

Everything Wrath++ owns, everything it may write, and how each boundary is enforced. Paths are
under the app's files folder (`$FILES`, `ctl.sh`'s variable).

## Identity

| | Value | Checked by |
|---|---|---|
| Name / key | Wrath++ / `wrathpp` | `ctl.sh realm()` |
| Realm id | 5 | `wrathpp-register` refuses if id 5 is another realm's; module refuses unless `RealmID == Wrathpp.RealmID` |
| World port | 8087 | `wrathpp-register` refuses if 8087 is another realm's |
| Databases | `acore_world_wrathpp`, `acore_characters_wrathpp`, `acore_playerbots_wrathpp` | `realm_database` in `ctl.sh`; module refuses non-`_wrathpp` databases (live-tested) |

## Paths Wrath++ writes (and only these)

| Path | What |
|---|---|
| `server-wrathpp/` | its server build, installed by the app from the `wrathpp-server` release (`WrathppServerPackage`) |
| `client-wrathpp/` | its private copy of the game, made by the app from Wrath+'s (`WrathppClient`); must not be a link. Only the game's own archives (`Data/` and `Data/<locale>/` `*.MPQ`, not the realm modules' patch-M/U/V/Y/Z; the HD look's patch-A/F/W are the game's) may be hard links to Wrath+'s, read only; everything else is its own copy (`ctl.sh wrathpp-check` holds it to that) |
| `etc-wrathpp/` | its configs (`configure` makes them only when `server-wrathpp/bin/worldserver` exists) |
| `logs/wrathpp/`, `run/wrathpp/` | logs, pid file, the app-signal files (`selection`, `cutscene`, ...) |
| `data-modules-wrathpp/` | the world server's data with its modules' DBC over the game's (links into the shared, read-only `data/`) |
| `mysql/.world-modules-wrathpp` | its record of modules whose SQL is in its world database |
| `backups/wrathpp/` | realm list backups taken by `wrathpp-register` |
| `acore_auth.realmlist` row id 5 | only via `wrathpp-register` (insert / its own row's address) and `wrathpp-unregister` (deletes `id = 5 AND name = 'Wrath++'`) |

## Paths and databases Wrath++ never writes

`etc/`, `etc-remix/`, `client/` (and everything in its `Data`), `data/` (no `zones_data` for
Wrath++), `data-modules/`, `server/`, `mysql/.world-modules*` of other realms, `acore_world`,
`acore_characters`, `acore_playerbots`, `*_remix`, every `acore_auth` table but its own realmlist
row, the Legion and OctoWoW databases (other servers on 3311/3312 that no Wrath++ code connects to).

## Enforcement

| Mechanism | Where |
|---|---|
| `realm wrathpp` sets every realm path (`R_*`), `SERVER`, `COMPAT` to Wrath++'s | `ctl.sh realm()` |
| `wrathpp_guard`: server installed, `client-wrathpp` and its `Data` not links, not the shared `Data` | before `configure_realm`, `dbimport`, `modules`, `module_client`, `world` for Wrath++ |
| `realm_database`: a dropped/created/updated database must be one of the realm's three, `_wrathpp` for Wrath++ | `rebuild_world`, `realm_sql`, `dbimport` |
| `wrathpp-check`: prints every path and database, fails on a shared path, a link, or a hard-linked game file | `ctl.sh wrathpp-check` (changes nothing) |
| The module refuses to run on non-Wrath++ databases or realm id | `mod-wrathpp-customization` `OnAfterConfigLoad` |
| The Wrath++ core patch and module exist only in the Wrath++ build | `realm/scripts/fetch-wrathpp.sh` (refuses folders without `wrathpp` in the path); the module lives outside `warcraft/modules/` |
| main/remix behaviour byte-identical to the previous `ctl.sh` | `realm/warcraft/wrathpp/tests/test-isolation.sh` (configs, world server environment, SQL) |
| The Blizzard app's program rewrite still sees every program line | same test (`"$SERVER/bin/<name>"` set unchanged) |

## The app

- The page **Wrath++ (experimental)** (`Games.kt` `wow_wrathpp`) plays through `WowPlay` with
  `wrathpp = true`: `WrathppSetup` installs `server-wrathpp` from the `wrathpp-server` release and makes
  `client-wrathpp`; `RealmController` runs Wrath++'s own steps (`configure-realm`, `dbimport`,
  `modules`, `wrathpp-register`, `world`, realm `wrathpp`) with Wrath++'s own script
  (`server-wrathpp/ctl.blizz.sh`) and only the shared ones (MariaDB, the realms' `configure` and
  `realmlist`, the login server) with the realms'. The game copy keeps its own realm record
  (`client-wrathpp/client-realm`), not Wrath+'s `files/client-realm`.
- The shared MariaDB (port 3310) and auth server are shared by design (one account set); Wrath++
  adds only its realm list row and its own three databases.
- Hard-linked archives: a later in-place rewrite of one of Wrath+'s base archives (nothing in the app
  or the realms does one today) would show in Wrath++'s copy too; Wrath++ itself never writes them.
