# Wrath++: start, stop, remove, roll back

Nothing here touches ChromieCraft's or Wrath Remix's files or databases. Run as the app runs
`ctl.sh` (its files folder in `FILES`). None of this is reachable from the app's screens yet.

## Check (changes nothing)

```sh
FILES=<app files> sh server/ctl.sh wrathpp-check
```

## Start / stop

```sh
sh server/ctl.sh configure                 # makes etc-wrathpp once server-wrathpp is installed
sh server/ctl.sh dbimport wrathpp          # creates/updates acore_*_wrathpp only
sh server/ctl.sh wrathpp-register          # its realm list row (backup in backups/wrathpp/)
sh server/ctl.sh auth &                    # the shared auth server, as for the other realms
sh server/ctl.sh world wrathpp             # its world server (one world server runs at a time)
kill -INT "$(cat run/wrathpp/worldserver.pid)"
```

## Back to the original realm

Stop Wrath++'s world server, then start ChromieCraft's as the app does (`ctl.sh world` /
`ctl.sh world remix`). Wrath++ writes no file or row the other realms read except its own realm
list row; to hide it from the realm list:

```sh
sh server/ctl.sh wrathpp-unregister        # DELETE ... WHERE id = 5 AND name = 'Wrath++'
```

## Remove Wrath++ entirely

```sh
sh server/ctl.sh wrathpp-unregister
for db in acore_world_wrathpp acore_characters_wrathpp acore_playerbots_wrathpp; do
	echo "DROP DATABASE IF EXISTS \`$db\`;" | sh server/ctl.sh sql
done
rm -rf server-wrathpp client-wrathpp etc-wrathpp logs/wrathpp run/wrathpp data-modules-wrathpp backups/wrathpp mysql/.world-modules-wrathpp
```

Check the names before running the `DROP`s: each ends in `_wrathpp`. `ctl.sh` has no command that
drops them for you on purpose.

## Restoring the realm list

`wrathpp-register` saved the whole `realmlist` table before writing
(`backups/wrathpp/realmlist-<time>.tsv`, tab-separated with a header line). Wrath++ only ever
inserts row 5 or changes row 5's address; deleting row 5 restores the list.

## Code rollback

Every Wrath++ change in this repository is additive except `realm/warcraft/server/ctl.sh`, whose
main/remix behaviour the isolation test compares byte for byte with the previous version. Reverting
the commit restores the previous `ctl.sh`; the Wrath++ folders (`realm/warcraft/wrathpp`,
`docs/wrathpp`, `realm/scripts/fetch-wrathpp.sh`) can be deleted without affecting any other build.
