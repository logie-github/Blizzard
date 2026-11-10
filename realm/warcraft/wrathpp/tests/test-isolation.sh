#!/bin/bash
# Wrath++'s isolation, tested on realm/warcraft/server/ctl.sh itself: a fake app folder (FILES) with
# stub programs in place of MariaDB's client, dbimport and the world server, which record what they
# were asked. Checks that
#   - main and Wrath Remix are configured and started exactly as the ctl.sh before Wrath++ did
#     (the same configs, the same world server environment), byte for byte;
#   - nothing of Wrath++ is made while its server isn't installed, and its commands refuse;
#   - Wrath++'s commands use its own configs, run folder, game folder, data and databases only,
#     and every file of main's and Remix's is unchanged after them (SHA-256 of the whole tree);
#   - a dropped world database is only ever acore_world_wrathpp;
#   - a Wrath++ game folder that is, or links to, the shared one is refused;
#   - the realm list gets Wrath++'s own row only, and never when its id or port is taken.
# Needs bash, coreutils, git (for the ctl.sh before Wrath++: BASE, default origin/main's).
#
#   realm/warcraft/wrathpp/tests/test-isolation.sh [BASE_REVISION]
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
CTL="$REPO/realm/warcraft/server/ctl.sh"
BASE="${1:-}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/wrathpp-isolation.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
pass=0
fail=0
ok() { echo "ok   $*"; pass=$((pass + 1)); }
bad() { echo "FAIL $*"; fail=$((fail + 1)); }
check() { local what=$1; shift; if "$@"; then ok "$what"; else bad "$what"; fi; }

# The ctl.sh before Wrath++ (the merge base with main, or the revision given).
if [ -z "$BASE" ]; then
	BASE=$(git -C "$REPO" merge-base HEAD origin/main 2> /dev/null || git -C "$REPO" rev-parse HEAD)
fi
OLD_CTL="$WORK/ctl.old.sh"
git -C "$REPO" show "$BASE:realm/warcraft/server/ctl.sh" > "$OLD_CTL"
if grep -q wrathpp "$OLD_CTL"; then
	echo "note: $BASE's ctl.sh already knows Wrath++; the main/remix comparison is against it"
fi

# A server folder with stub programs. $1: folder, $2: label written into what the stubs record.
make_server() {
	local dir=$1 label=$2
	mkdir -p "$dir/bin" "$dir/etc/modules" "$dir/lib" "$dir/src/modules" "$dir/share"
	cat > "$dir/bin/mariadb" << 'EOF'
#!/bin/bash
# Records the SQL it is given; answers SELECTs from STUB_SELECT (a file), else nothing.
args="$*"
sql=$(cat)
{ echo "== mariadb ${args##* }"; echo "$sql"; } >> "$STUB_LOG/sql.log"
case "$sql" in SELECT*) [ -n "${STUB_SELECT:-}" ] && [ -f "$STUB_SELECT" ] && cat "$STUB_SELECT" ;; esac
exit 0
EOF
	cat > "$dir/bin/dbimport" << EOF
#!/bin/bash
echo "== dbimport $label \$* (cwd \$PWD)" >> "\$STUB_LOG/dbimport.log"
EOF
	cat > "$dir/bin/worldserver" << EOF
#!/bin/bash
{
	echo "server=$label"
	echo "args=\$*"
	echo "cwd=\$PWD"
	env | grep -E '^(WOW_[A-Z_]+|LD_PRELOAD)=' | sed "s|\$FILES|FILES|g" | sort
} > "\$STUB_LOG/world.\$\$"
cat "\$STUB_LOG/world.\$\$"
EOF
	chmod +x "$dir/bin/"*
	for name in worldserver dbimport authserver; do
		printf 'LogsDir = ""\nTempDir = ""\nRealmID = 1\nWorldServerPort = 8085\nDataDir = "."\nLoginDatabaseInfo = ""\nWorldDatabaseInfo = ""\nCharacterDatabaseInfo = ""\n' \
			> "$dir/etc/$name.conf.dist"
	done
	printf 'mmaps: {}\n' > "$dir/etc/mmaps-config.yaml"
	printf '[worldserver]\nAlliedRaces.Enable = 1\n' > "$dir/etc/modules/mod_allied_races.conf.dist"
	printf '[worldserver]\nWrathRemix.Enable = 0\n' > "$dir/etc/modules/mod_wrath_remix.conf.dist"
	mkdir -p "$dir/src/modules/mod-allied-races/data/sql/chromiecraft/world" "$dir/src/modules/mod-wrath-remix/data/sql/remix/world"
}

# A fresh app folder: main's server, the shared game, MariaDB's folder. $1: folder.
make_files() {
	local f=$1
	mkdir -p "$f/client/Data/enUS" "$f/data/dbc" "$f/mysql" "$f/logs" "$f/run/tmp"
	make_server "$f/server" main
	echo "game archive" > "$f/client/Data/common.MPQ"
	echo "realmlist" > "$f/client/Data/enUS/realmlist.wtf"
}

# Wrath++ installed: its server (with its module's config) and its own copy of the game.
install_wrathpp() {
	local f=$1
	make_server "$f/server-wrathpp" wrathpp
	printf '[worldserver]\nWrathpp.Enable = 0\nWrathpp.RealmID = 0\n' > "$f/server-wrathpp/etc/modules/mod_wrathpp_customization.conf.dist"
	mkdir -p "$f/server-wrathpp/src/modules/mod-wrathpp-customization/data/sql/db-characters"
	mkdir -p "$f/client-wrathpp"
	cp -r "$f/client/Data" "$f/client-wrathpp/Data"
	# A module's patch for the game, as the Wrath++ package would ship it.
	mkdir -p "$f/server-wrathpp/share/client/Interface"
	echo "wrathpp glue" > "$f/server-wrathpp/share/client/Interface/test.lua"
	echo "wrathpp-1" > "$f/server-wrathpp/share/client.stamp"
}

# Runs a ctl.sh against an app folder, its stubs logging into $f/stub. Prints what it printed.
run() {
	local ctl=$1 f=$2
	shift 2
	mkdir -p "$f/stub"
	FILES="$f" STUB_LOG="$f/stub" STUB_SELECT="${STUB_SELECT:-}" sh "$ctl" "$@" 2>&1 | grep -v "cannot be preloaded" || true
}
status() {
	local ctl=$1 f=$2
	shift 2
	mkdir -p "$f/stub"
	FILES="$f" STUB_LOG="$f/stub" sh "$ctl" "$@" > /dev/null 2>&1 && echo 0 || echo $?
}

# Every file of the app folder but Wrath++'s own and the stubs' logs, with its SHA-256.
shared_manifest() {
	local f=$1
	(cd "$f" && find . \( -path ./stub -o -path ./client-wrathpp -o -path ./etc-wrathpp -o -path ./logs/wrathpp \
		-o -path ./run/wrathpp -o -path ./data-modules-wrathpp -o -path ./backups/wrathpp -o -path ./server-wrathpp \
		-o -name '.world-modules-wrathpp' \) -prune -o \( -type f -o -type l \) -print | LC_ALL=C sort | while read -r p; do
		if [ -L "$p" ]; then echo "link $p -> $(readlink "$p")"; else echo "$(sha256sum < "$p" | cut -c1-64) $p"; fi
	done)
}

echo "# 1. main and Wrath Remix are as before Wrath++ ($BASE)"
OLD="$WORK/old" NEW="$WORK/new"
make_files "$OLD"; make_files "$NEW"
run "$OLD_CTL" "$OLD" configure > /dev/null
run "$CTL" "$NEW" configure > /dev/null
# (each tree's own folder name in its configs read as FILES)
same_tree() {
	diff <(cd "$OLD/$1" && find . -type f | LC_ALL=C sort | while read -r p; do echo "== $p"; sed "s|$OLD|FILES|g" "$p"; done) \
		<(cd "$NEW/$1" && find . -type f | LC_ALL=C sort | while read -r p; do echo "== $p"; sed "s|$NEW|FILES|g" "$p"; done)
}
check "main's configs identical to the old ctl.sh's" same_tree etc
check "Remix's configs identical" same_tree etc-remix
for r in main remix; do
	o=$(run "$OLD_CTL" "$OLD" world "$r" | sed "s|$OLD|FILES|g")
	n=$(run "$CTL" "$NEW" world "$r" | sed "s|$NEW|FILES|g")
	check "$r's world server started exactly as before" [ "$o" = "$n" ]
done
rm -f "$OLD/stub/"* "$NEW/stub/"*
run "$OLD_CTL" "$OLD" dbimport remix > /dev/null
run "$CTL" "$NEW" dbimport remix > /dev/null
check "Remix's dbimport: the same SQL as before" diff "$OLD/stub/sql.log" "$NEW/stub/sql.log"
check "main's realm list: the same SQL as before" \
	[ "$(run "$OLD_CTL" "$OLD" realmlist; cat "$OLD/stub/sql.log")" = "$(run "$CTL" "$NEW" realmlist; cat "$NEW/stub/sql.log")" ]

# The Blizzard app starts the programs by rewriting the text "$SERVER/bin/<name>" (WowCtl.transform)
# and the MySQLExecutable line: both must be there for every program as before.
programs() { grep -oE '"\$SERVER/bin/[A-Za-z0-9_.-]+"' "$1" | LC_ALL=C sort -u; }
check "the programs the app's loader rewrite finds are the same" [ "$(programs "$OLD_CTL")" = "$(programs "$CTL")" ]
check "  every program line count kept or grown" [ "$(grep -cE '"\$SERVER/bin/' "$CTL")" -ge "$(grep -cE '"\$SERVER/bin/' "$OLD_CTL")" ]
check "  the MySQLExecutable line the app rewrites is there" grep -qF 'MySQLExecutable "\"$SERVER/bin/mariadb\""' "$CTL"
# (a program run as "$R_SERVER/bin/x" or "$WRATHPP_SERVER/bin/x" would escape the app's rewrite;
# "[ -x ... ]" tests of whether one is installed are fine)
direct_runs() { grep -nE '"\$(R_SERVER|WRATHPP_SERVER)/bin/[A-Za-z0-9_.-]+"' "$CTL" | grep -vE -e '-x "\$(R_SERVER|WRATHPP_SERVER)/bin/' || true; }
check "  no program started by another path to the server" [ -z "$(direct_runs)" ]

echo "# 2. Wrath++ not installed: nothing of it, and its commands refuse"
check "configure made no etc-wrathpp" [ ! -e "$NEW/etc-wrathpp" ]
check "world wrathpp refused (exit 4)" [ "$(status "$CTL" "$NEW" world wrathpp)" = 4 ]
check "modules wrathpp refused (exit 4)" [ "$(status "$CTL" "$NEW" modules wrathpp)" = 4 ]
check "dbimport wrathpp refused (exit 4)" [ "$(status "$CTL" "$NEW" dbimport wrathpp)" = 4 ]
check "no client-wrathpp, logs/wrathpp or run/wrathpp made" [ ! -e "$NEW/client-wrathpp" ] && [ ! -e "$NEW/logs/wrathpp" ] && [ ! -e "$NEW/run/wrathpp" ]
check "an unknown realm refused (exit 2)" [ "$(status "$CTL" "$NEW" world wrathpp2)" = 2 ]

echo "# 3. Wrath++ installed: its commands write only what is its own"
F="$WORK/f"
make_files "$F"
run "$CTL" "$F" configure > /dev/null      # main and remix as the app has them
install_wrathpp "$F"
before=$(shared_manifest "$F")
run "$CTL" "$F" configure > /dev/null
W="$F/etc-wrathpp/worldserver.conf"
check "Wrath++ configured in etc-wrathpp" [ -f "$W" ]
check "  realm 5 on port 8087" grep -qx 'RealmID = 5' "$W"
check "  port 8087" grep -qx 'WorldServerPort = 8087' "$W"
check "  its world database" grep -q 'WorldDatabaseInfo = "127.0.0.1;3310;acore;acore;acore_world_wrathpp"' "$W"
check "  its characters database" grep -q 'CharacterDatabaseInfo = "127.0.0.1;3310;acore;acore;acore_characters_wrathpp"' "$W"
check "  its own server's sources and programs" grep -q "SourceDirectory = \"$F/server-wrathpp/src\"" "$W"
check "  its pid file in run/wrathpp" grep -q "PidFile = \"$F/run/wrathpp/worldserver.pid\"" "$W"
check "  its module on, told its realm" grep -qx 'Wrathpp.Enable = 1' "$F/etc-wrathpp/modules/mod_wrathpp_customization.conf"
check "  realm id in the module's config" grep -qx 'Wrathpp.RealmID = 5' "$F/etc-wrathpp/modules/mod_wrathpp_customization.conf"
check "  the allied races (ChromieCraft's alone) off" grep -qx 'AlliedRaces.Enable = 0' "$F/etc-wrathpp/modules/mod_allied_races.conf"
check "  Wrath Remix's module off" grep -qx 'WrathRemix.Enable = 0' "$F/etc-wrathpp/modules/mod_wrath_remix.conf"
check "  no main or Remix database named in its configs" bash -c "! grep -rhoE 'acore_(world|characters|playerbots)(_remix)?\"' '$F/etc-wrathpp'"
check "  no auth server config of its own (main's serves all)" [ ! -f "$F/etc-wrathpp/authserver.conf" ]
check "main's configs unchanged by configuring Wrath++" [ "$before" = "$(shared_manifest "$F")" ]

out=$(run "$CTL" "$F" world wrathpp)
check "world wrathpp runs Wrath++'s own world server" grep -qx 'server=wrathpp' <<< "$out"
check "  with its own config" grep -q "args=-c $F/etc-wrathpp/worldserver.conf" <<< "$out"
check "  in run/wrathpp" grep -qx "cwd=$F/run/wrathpp" <<< "$out"
check "  its game folder is client-wrathpp" grep -qx 'WOW_CLIENT_DIR=FILES/client-wrathpp' <<< "$out"
check "  no starting areas of main's" bash -c "! grep -q WOW_ZONES_DIR <<< '$out'"
check "  its own libraries" grep -q 'LD_PRELOAD=FILES/server-wrathpp/lib/' <<< "$out"

rm -f "$F/stub/sql.log"
run "$CTL" "$F" dbimport wrathpp > /dev/null
check "dbimport wrathpp creates only *_wrathpp databases" bash -c "grep -o 'CREATE DATABASE IF NOT EXISTS \`[a-z_]*\`' '$F/stub/sql.log' | grep -v '_wrathpp\`' | wc -l | grep -qx 0"
check "  and creates all three" [ "$(grep -c '_wrathpp`' "$F/stub/sql.log")" -ge 3 ]
check "  dbimport run with Wrath++'s config" grep -q "dbimport wrathpp -c $F/etc-wrathpp/dbimport.conf" "$F/stub/dbimport.log"

# A module gone from the Wrath++ package: its world database (and only it) made again.
echo "mod-gone" > "$F/mysql/.world-modules-wrathpp"
rm -f "$F/stub/sql.log"
run "$CTL" "$F" modules wrathpp > /dev/null
check "modules wrathpp drops only acore_world_wrathpp" bash -c "grep -o 'DROP DATABASE IF EXISTS \`[a-z_]*\`' '$F/stub/sql.log' | sort -u | grep -qx 'DROP DATABASE IF EXISTS \`acore_world_wrathpp\`'"
check "  and no other database" [ "$(grep -c 'DROP DATABASE' "$F/stub/sql.log")" = 1 ]
check "  the modules' patch went into client-wrathpp" [ -f "$F/client-wrathpp/Data/patch-M.MPQ/Interface/test.lua" ]
check "  and not into the shared game" [ ! -e "$F/client/Data/patch-M.MPQ" ]
check "  its record of world modules is its own" [ -f "$F/mysql/.world-modules-wrathpp" ] && [ ! -f "$F/mysql/.world-modules" ]
run "$CTL" "$F" wrathpp-check > "$WORK/f-check.out" || true
check "wrathpp-check passes" grep -q "Wrath++ checks passed" "$WORK/f-check.out"

after=$(shared_manifest "$F")
check "every file of main's, Remix's and the shared game unchanged after Wrath++'s commands" [ "$before" = "$after" ]
[ "$before" = "$after" ] || diff <(echo "$before") <(echo "$after") || true

echo "# 4. a Wrath++ game folder that reaches the shared one is refused"
G="$WORK/g"
make_files "$G"; install_wrathpp "$G"
rm -rf "$G/client-wrathpp/Data"
ln -s "$G/client/Data" "$G/client-wrathpp/Data"
check "world wrathpp refused with Data a link to the shared game (exit 4)" [ "$(status "$CTL" "$G" world wrathpp)" = 4 ]
check "modules wrathpp refused likewise" [ "$(status "$CTL" "$G" modules wrathpp)" = 4 ]
check "  nothing written into the shared game" [ ! -e "$G/client/Data/patch-M.MPQ" ]
check "wrathpp-check fails" [ "$(status "$CTL" "$G" wrathpp-check)" != 0 ]
H="$WORK/h"
make_files "$H"; install_wrathpp "$H"
rm "$H/client-wrathpp/Data/common.MPQ"
ln "$H/client/Data/common.MPQ" "$H/client-wrathpp/Data/common.MPQ"
echo "allied races" > "$H/client/Data/patch-V.MPQ"
ln "$H/client/Data/patch-V.MPQ" "$H/client-wrathpp/Data/patch-V.MPQ"
run "$CTL" "$H" wrathpp-check > "$WORK/h-check.out" || true
check "wrathpp-check lets the game's own archive be shared read only (a hard link)" grep -q "shared, read only: Data/common.MPQ" "$WORK/h-check.out"
check "  but not a patch a realm module writes" grep -q "FAIL .*patch-V.MPQ is the shared game's file" "$WORK/h-check.out"

echo "# 4b. configure-realm wrathpp configures Wrath++ alone"
C="$WORK/c"
make_files "$C"
run "$CTL" "$C" configure > /dev/null
install_wrathpp "$C"
before_c=$(shared_manifest "$C")
run "$CTL" "$C" configure-realm wrathpp > /dev/null
check "configure-realm wrathpp makes etc-wrathpp" grep -qx 'RealmID = 5' "$C/etc-wrathpp/worldserver.conf"
check "  and changes no file of main's or Remix's" [ "$before_c" = "$(shared_manifest "$C")" ]

echo "# 5. the realm list"
rm -f "$F/stub/sql.log"
run "$CTL" "$F" wrathpp-register > /dev/null
check "wrathpp-register saves the realm list first" bash -c "ls '$F'/backups/wrathpp/realmlist-*.tsv > /dev/null"
check "  inserts realm 5, Wrath++, port 8087" grep -q "VALUES (5, 'Wrath++', '127.0.0.1', '127.0.0.1', '255.255.255.0', 8087" "$F/stub/sql.log"
check "  changes no other row (no UPDATE or DELETE)" bash -c "! grep -qE '^(UPDATE|DELETE)' '$F/stub/sql.log'"
echo 3 > "$WORK/taken"
rm -f "$F/stub/sql.log"
check "refused when id 5 or port 8087 is another realm's (exit 5)" [ "$(FILES="$F" STUB_LOG="$F/stub" STUB_SELECT="$WORK/taken" sh "$CTL" wrathpp-register > /dev/null 2>&1 && echo 0 || echo $?)" = 5 ]
check "  and inserted nothing" bash -c "! grep -q INSERT '$F/stub/sql.log'"
rm -f "$F/stub/sql.log"
run "$CTL" "$F" wrathpp-unregister > /dev/null
check "wrathpp-unregister deletes only Wrath++'s row" grep -qx "DELETE FROM realmlist WHERE id = 5 AND name = 'Wrath++';" "$F/stub/sql.log"
rm -f "$F/stub/sql.log"
run "$CTL" "$F" realmlist > /dev/null
check "the app's realmlist command leaves Wrath++ out" bash -c "! grep -q 'Wrath++' '$F/stub/sql.log'"

echo
echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
