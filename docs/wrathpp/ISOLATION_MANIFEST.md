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
| `server-wrathpp/` | its server build (installed by a future Wrath++ package; nothing installs it today) |
| `client-wrathpp/` | its private copy of the game (Alternative HD baseline + its own patches); must not be a link and must not share files (hard links) with `client/` |
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

## Not yet isolated (because not yet built)

- The Android app has no Wrath++ entry: nothing on the phone selects, installs or starts it.
- No Wrath++ server or client package exists; `server-wrathpp/` and `client-wrathpp/` are only
  ever made by hand or by the tests.
- The shared MariaDB (port 3310) and auth server are shared by design (one account set); Wrath++
  adds only its realm list row and its own three databases.
