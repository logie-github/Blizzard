# The Character Porter's realm rig

The porter's engine (`app/src/main/java/com/logie/blizz/porter/port`) writes a retail character into one of the
app's Wrath realms. This rig is the proof that what it writes plays: the realm the phone runs, here, with a ported
character taken into its world.

- **The realm** is the phone's own package (`wow-server-bbaf5a665538`'s `server.tar.xz`: AzerothCore at ChromieCraft's
  revision with the playerbots core and every module of `realm/warcraft/modules`, musl arm64), unpacked as the app has
  it (`files/server`), driven by its own `ctl.sh`. This machine is x86_64 without binfmt, so `ctl.rig.sh` (made from
  `ctl.sh` by `rig.sh prepare`) starts every program as the app does (`WowCtl.transform`: through the musl loader), with
  `qemu-aarch64-static` in front of the loader; the realm's preloaded compatibility library goes to the arm64
  programs alone (`QEMU_SET_ENV`).
- **The database** is the package's own seed (`mariadb-seed`, MariaDB 11.4.13) served by MariaDB 11.4.13 built for
  x86_64 (from archive.mariadb.org, checked by its sha256): the same version, so it opens the seed as it is, and an
  emulated MariaDB would be slow. dbimport and the world server run the database client by their `MySQLExecutable`;
  `nopreload.c` (built by `prepare`) is that client, the x86_64 one without the arm64 preload.
- **The server's data**: `dbc`, `Cameras` and `maps` of `realm/warcraft/server-data.env`'s zip, fetched by HTTP range
  requests (`fetch-data.py`: 390 MB of the 1.2 GB zip). No vmaps or mmaps: the world server runs with them off, as a
  phone without them does (`WowSettings`).
- **The world server** starts in about 80 seconds (emulated; the first start applies the modules' SQL and takes a few
  minutes). No random bots (`Playerbots.MaxRandomBots 0`): an emulated world server is slow enough. The character
  loader's warnings and login line are logged (`Logger.entities.player`), which the realm's own setting leaves out.

## Running it

```sh
export BLIZZ_PORTER_RIG=/path/to/an/empty/folder        # about 3.1 GB when set up
tools/porter-rig/rig.sh setup                            # fetch, prepare, the databases, an account porter/porter123
# the engine ports the six fixture characters (PorterFixtures) into the realm, its database up, its world server stopped:
./gradlew --init-script ../YeaBwoi/scripts/maven-mirror.init.gradle :app:testDebugUnitTest --tests 'com.logie.blizz.porter.port.PorterRigTest'
tools/porter-rig/prove.sh                                # each into the world, and every check
tools/porter-rig/prove.sh control                        # the log check shown to catch what the realm refuses
tools/porter-rig/rig.sh stop                             # everything the rig started
```

`PorterRigTest` has two tests: `portsEachFixtureIntoTheRealm` (the six characters, written) and
`aFailedPortLeavesNothingBehind` (a port the database refuses after the character's row and items went in, and one
whose name was taken after it was planned: neither leaves a row). It leaves `<rig>/ported/<name>.report.txt` (the
plan's report), `<name>.expect` (what `prove.sh` checks) and `summary.txt`; `prove.sh` leaves `<name>.world.txt` (what
the headless client heard). Each run of the test first takes out the characters an earlier run made (their every row),
so it can be run again and again.

The rig takes about 3.1 GB: the realm package unpacked (1.5 GB, most of it the modules' SQL), its databases (1 GB),
the server's data (0.4 GB), MariaDB (70 MB). The downloads are deleted once unpacked.

`rig.sh` also runs one step at a time (`rig.sh` alone lists them): `db-start`, `auth-start`, `world-start`,
`world-console "server info"`, `sql acore_characters`, `status`, `stop`. It only ever ends processes it started (their
pids are in `<rig>/pids`).
