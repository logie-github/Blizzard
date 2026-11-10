#!/bin/bash
# The Wrath++ world server, live: a private MariaDB, the auth server, the Wrath++ world server
# (AzerothCore with wrathpp/patches/azerothcore and mod-wrathpp-customization), and
# server_protocol_test.py speaking the protocol as a Wrath++ client would, before and after a
# restart of the world server. Also checks that
#   - the module's rows are in acore_characters_wrathpp alone, and a canary acore_characters
#     database (standing in for ChromieCraft's) is byte for byte as it was;
#   - the same server on a characters database not named *_wrathpp refuses to serve Wrath++.
#
#   run-server-test.sh AC_SOURCE AC_BUILD SERVER_DATA WORK
#
# AC_SOURCE: the core with the Wrath++ patch and module (realm/scripts/fetch-wrathpp.sh);
# AC_BUILD: its build folder (bin/worldserver, bin/authserver); SERVER_DATA: AzerothCore's
# client-data (dbc, maps, ...: realm/warcraft/server-data.env); WORK: an empty folder of this test's.
# Needs mariadbd, mariadb and mariadb-install-db, python3. Runs nothing as root of the machine's
# own MariaDB: a server of its own on port 3399.
set -euo pipefail

SRC=$1 BUILD=$2 DATA=$3 WORK=$4
HERE="$(cd "$(dirname "$0")" && pwd)"
WPP="$(cd "$HERE/.." && pwd)"
SERVER_DIR="$(cd "$WPP/../server" && pwd)"
PORT=3399 WORLD_PORT=8087
case "$WORK" in /|"$HOME"|/home|/root) echo "refused: WORK=$WORK" >&2; exit 2 ;; esac
mkdir -p "$WORK"
[ -z "$(ls -A "$WORK")" ] || { echo "refused: $WORK isn't empty" >&2; exit 2; }
mkdir -p "$WORK/db" "$WORK/etc/modules" "$WORK/logs" "$WORK/run"
pids=()
cleanup() {
	for pid in "${pids[@]}"; do kill "$pid" 2> /dev/null || true; done
	wait 2> /dev/null || true
}
trap cleanup EXIT

# A program of the build: in its bin/ (installed) or where CMake links it.
bin() { if [ -x "$BUILD/bin/$1" ]; then echo "$BUILD/bin/$1"; else echo "$BUILD/src/server/apps/$1"; fi; }
sql() { mariadb --no-defaults -h127.0.0.1 -P"$PORT" -uroot "$@"; }

echo "== MariaDB (port $PORT)"
mariadb-install-db --no-defaults --datadir="$WORK/db" --user="$(id -un)" --auth-root-authentication-method=normal > "$WORK/logs/install-db.log" 2>&1
mariadbd --no-defaults --datadir="$WORK/db" --port="$PORT" --bind-address=127.0.0.1 --socket="$WORK/run/mysqld.sock" \
	--pid-file="$WORK/run/mysqld.pid" --log-error="$WORK/logs/mariadb.log" --user="$(id -un)" &
pids+=($!)
for _ in $(seq 60); do sql -e "SELECT 1" > /dev/null 2>&1 && break; sleep 1; done
sql << 'EOF'
CREATE USER 'acore'@'127.0.0.1' IDENTIFIED BY 'acore';
GRANT ALL PRIVILEGES ON *.* TO 'acore'@'127.0.0.1' WITH GRANT OPTION;
CREATE DATABASE acore_auth DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE acore_world_wrathpp DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE acore_characters_wrathpp DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- The canary: ChromieCraft's characters database's name, with a character in it.
CREATE DATABASE acore_characters DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE TABLE acore_characters.characters (guid INT UNSIGNED PRIMARY KEY, account INT UNSIGNED, name VARCHAR(12), race TINYINT, class TINYINT, skin TINYINT, face TINYINT);
INSERT INTO acore_characters.characters VALUES (1, 1, 'Canary', 10, 2, 3, 4);
FLUSH PRIVILEGES;
EOF
canary() { sql -N -e "CHECKSUM TABLE acore_characters.characters EXTENDED; SELECT GROUP_CONCAT(table_name ORDER BY table_name) FROM information_schema.tables WHERE table_schema = 'acore_characters'"; }
canary_before=$(canary)

# The core's SQL names MySQL 8's utf8mb4_0900_ai_ci, which MariaDB knows from 11.4 on (the phone's
# Alpine MariaDB). On an older MariaDB the test reads a copy of the SQL with utf8mb4_unicode_ci.
SQLSRC="$SRC"
if [ -z "$(sql -N -e "SHOW COLLATION LIKE 'utf8mb4_0900_ai_ci'")" ]; then
	echo "== this MariaDB lacks utf8mb4_0900_ai_ci: a copy of the SQL with utf8mb4_unicode_ci"
	SQLSRC="$WORK/source"
	mkdir -p "$SQLSRC/modules"
	cp -r "$SRC/data" "$SQLSRC/data"
	for mod in "$SRC"/modules/*/; do
		[ -d "$mod/data/sql" ] || continue
		mkdir -p "$SQLSRC/modules/$(basename "$mod")/data"
		cp -r "$mod/data/sql" "$SQLSRC/modules/$(basename "$mod")/data/"
	done
	grep -rl 'utf8mb4_0900_ai_ci' "$SQLSRC" | xargs -r sed -i 's/utf8mb4_0900_ai_ci/utf8mb4_unicode_ci/g'
fi

echo "== configs"
dbinfo() { echo "\"127.0.0.1;$PORT;acore;acore;$1\""; }
setkey() {
	local file=$1 key=$2 value=$3
	if grep -q "^$key[[:space:]]*=" "$file"; then
		local escaped
		escaped=$(printf '%s' "$value" | sed 's/[|&\\]/\\&/g')
		sed -i "s|^$key[[:space:]]*=.*|$key = $escaped|" "$file"
	else
		printf '%s = %s\n' "$key" "$value" >> "$file"
	fi
}
cp "$SRC/src/server/apps/authserver/authserver.conf.dist" "$WORK/etc/authserver.conf"
cp "$SRC/src/server/apps/worldserver/worldserver.conf.dist" "$WORK/etc/worldserver.conf"
cp "$SRC/modules/mod-wrathpp-customization/conf/mod_wrathpp_customization.conf.dist" "$WORK/etc/modules/mod_wrathpp_customization.conf"
python3 "$WPP/tools/registry.py" build "$WPP/registry/registry.json" "$WORK/registry.bin"
for conf in authserver worldserver; do
	c="$WORK/etc/$conf.conf"
	setkey "$c" LoginDatabaseInfo "$(dbinfo acore_auth)"
	setkey "$c" LogsDir "\"$WORK/logs\""
	setkey "$c" TempDir "\"$WORK/run\""
	setkey "$c" SourceDirectory "\"$SQLSRC\""
	setkey "$c" MySQLExecutable "\"$(command -v mariadb)\""
	setkey "$c" Updates.AutoSetup 1
	setkey "$c" Console.Enable 0
done
w="$WORK/etc/worldserver.conf"
setkey "$w" WorldDatabaseInfo "$(dbinfo acore_world_wrathpp)"
setkey "$w" CharacterDatabaseInfo "$(dbinfo acore_characters_wrathpp)"
setkey "$w" Updates.EnableDatabases 7
setkey "$w" DataDir "\"$DATA\""
setkey "$w" RealmID 5
setkey "$w" WorldServerPort "$WORLD_PORT"
setkey "$w" PidFile "\"$WORK/run/worldserver.pid\""
setkey "$w" MoveMaps.Enable 0
m="$WORK/etc/modules/mod_wrathpp_customization.conf"
setkey "$m" Wrathpp.Enable 1
setkey "$m" Wrathpp.RealmID 5
setkey "$m" Wrathpp.Registry "\"$WORK/registry.bin\""
export WOW_MODULES_CONF_DIR="$WORK/etc/modules"

echo "== auth server and accounts"
(cd "$WORK/run" && exec "$(bin authserver)" -c "$WORK/etc/authserver.conf" > "$WORK/logs/authserver.out" 2>&1) &
pids+=($!)
for _ in $(seq 120); do sql -N -e "SELECT COUNT(*) FROM acore_auth.realmlist" > /dev/null 2>&1 && break; sleep 1; done
for _ in $(seq 120); do (exec 3<> /dev/tcp/127.0.0.1/3724) 2> /dev/null && break; sleep 1; done
{
	python3 "$SERVER_DIR/auth_check.py" account-sql WPPA wpp
	python3 "$SERVER_DIR/auth_check.py" account-sql WPPB wpp
	echo "DELETE FROM realmlist; INSERT INTO realmlist (id, name, address, localAddress, localSubnetMask, port, icon, flag, timezone, allowedSecurityLevel, gamebuild) VALUES (5, 'Wrath++', '127.0.0.1', '127.0.0.1', '255.255.255.0', $WORLD_PORT, 0, 2, 1, 0, 12340);"
} | sql acore_auth

world_pid=
start_world() {
	local log=$1
	(cd "$WORK/run" && exec "$(bin worldserver)" -c "$w" > "$WORK/logs/$log" 2>&1) &
	world_pid=$!
	pids+=("$world_pid")
	for _ in $(seq 1800); do
		(exec 3<> /dev/tcp/127.0.0.1/$WORLD_PORT) 2> /dev/null && return 0
		kill -0 "$world_pid" 2> /dev/null || { tail -40 "$WORK/logs/$log"; echo "the world server stopped" >&2; return 1; }
		sleep 1
	done
	echo "the world server didn't open its port" >&2
	return 1
}
stop_world() {
	kill -INT "$world_pid"
	for _ in $(seq 120); do kill -0 "$world_pid" 2> /dev/null || break; sleep 1; done
	kill -0 "$world_pid" 2> /dev/null && kill -9 "$world_pid" || true
	wait "$world_pid" 2> /dev/null || true
}

echo "== world server (first start fills the Wrath++ world database)"
start_world world-1.log
grep -E "Wrath\+\+" "$WORK/logs/world-1.log" "$WORK/logs/Server.log" 2> /dev/null | head -5 || true
python3 "$HERE/server_protocol_test.py" create 127.0.0.1 "$WORLD_PORT" WPPA WPPB wpp "$WORK/state.json"
stop_world

echo "== world server again"
start_world world-2.log
python3 "$HERE/server_protocol_test.py" after-restart 127.0.0.1 "$WORLD_PORT" WPPA WPPB wpp "$WORK/state.json"
stop_world

echo "== databases"
rows=$(sql -N -e "SELECT guid, category_id, option_id FROM acore_characters_wrathpp.wrathpp_character_customization ORDER BY guid, category_id")
echo "$rows"
guid=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['guid'])" "$WORK/state.json")
[ "$(echo "$rows" | awk -v g="$guid" '$1 == g { print $2 ":" $3 }' | tr '\n' ' ')" = "1002:2 1003:2 " ] ||
	{ echo "FAIL the character's rows aren't horns 2, blindfold 2"; exit 1; }
echo "ok   the character's rows in acore_characters_wrathpp: horns 2, blindfold 2"
[ "$(sql -N -e "SELECT COUNT(*) FROM acore_characters_wrathpp.characters WHERE guid = $guid AND skin = 0 AND face = 0 AND hairStyle = 0 AND hairColor = 0 AND facialStyle = 0")" = 1 ] ||
	{ echo "FAIL the stock five fields were changed"; exit 1; }
echo "ok   the stock five fields untouched (all 0, as created)"
[ "$(canary)" = "$canary_before" ] || { echo "FAIL the canary acore_characters changed"; exit 1; }
echo "ok   the canary acore_characters database unchanged, no Wrath++ table in it"

echo "== the same server on a database not Wrath++'s"
sql -e "CREATE DATABASE acore_characters_guardtest DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
setkey "$w" CharacterDatabaseInfo "$(dbinfo acore_characters_guardtest)"
start_world world-guard.log
grep -q "Wrath++: refusing to run" "$WORK/logs/world-guard.log" "$WORK/logs/Server.log" 2> /dev/null ||
	{ echo "FAIL no refusal logged"; exit 1; }
echo "ok   the module refuses to run on acore_characters_guardtest (logged)"
python3 - "$SERVER_DIR" "$WORLD_PORT" << 'EOF'
import os, sys
sys.path.insert(0, sys.argv[1])
import auth_check as ac
os.environ["WORLD_PORT"] = sys.argv[2]
session, _ = ac.world_session("127.0.0.1", "WPPA", "wpp", int(sys.argv[2]))
seen = []
session.send(ac.CMSG_CHAR_ENUM)
session.wait_for([ac.SMSG_CHAR_ENUM], seen=seen)
wpp = [hex(o) for o, _ in seen if 0x521 <= o <= 0x527]
if wpp:
    raise SystemExit(f"FAIL Wrath++ messages from a refusing server: {wpp}")
print("ok   and sends no Wrath++ message to the character screen")
EOF
stop_world
[ "$(sql -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'acore_characters_guardtest' AND table_name = 'wrathpp_character_customization'")" = 0 ] && echo "note: dbimport made no Wrath++ table there either" || echo "note: the table exists there (the core's update system applies module SQL on any database it serves); the module still refused to use it"
echo "== all passed"
