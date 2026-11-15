#!/usr/bin/env bash
# The Character Porter's realm rig: the phone's own Wrath realm package (arm64, musl) run on this
# x86_64 machine under qemu-user, on the package's own database seed served by an x86_64 build of the
# same MariaDB, so that a character the porter's engine wrote can be taken into the world by the
# realm's real world server. README.md beside this file says what each step is for.
#
#   rig.sh setup               everything below up to a realm ready to start (fetch prepare db-init db-start import account)
#   rig.sh fetch               the realm package, the server data (dbc, Cameras, maps only), MariaDB for x86_64
#   rig.sh prepare             the qemu loader wrapper, the client wrapper, ctl.rig.sh, the configs
#   rig.sh db-init             the database folder, from the package's seed (as the phone makes it)
#   rig.sh db-start | db-stop  MariaDB on the realm's port (3310)
#   rig.sh import              the realm's databases (the package's own dbimport) and its modules' record
#   rig.sh account NAME PASS   a game master account, made the way the realm's test makes one
#   rig.sh auth-start | world-start [REALM] | world-stop | stop
#                              the login server; a realm's world server (main, remix); everything the rig started
#   rig.sh sql [DATABASE]      SQL on stdin through the x86_64 client (tab-separated rows)
#   rig.sh ctl ARGS...         the package's ctl.sh (ctl.rig.sh) with the rig's environment
#   rig.sh world-console TEXT  a line typed into the world server's console
#   rig.sh status              what is running
#
# The rig's folder is $BLIZZ_PORTER_RIG; nothing is written outside it.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
RIG=${BLIZZ_PORTER_RIG:?set BLIZZ_PORTER_RIG to the folder of the rig}
FILES=$RIG/files
DB_DIR=$FILES/mysql
MARIA=$RIG/mariadb
DB_PORT=${DB_PORT:-3310}
PIDS=$RIG/pids
QEMU=${QEMU:-/usr/bin/qemu-aarch64-static}
PACKAGE_URL=${PORTER_RIG_PACKAGE_URL:-https://github.com/logie-github/YeaBwoi/releases/download/wow-server-bbaf5a665538/server.tar.xz}
PACKAGE_SHA256=${PORTER_RIG_PACKAGE_SHA256:-742cf180f575d05febf9e0d2810bc49952a2acdc7730f638ec9a9174b05facf8}
# MariaDB for this machine: the version the package's seed was made with (server/VERSION), so it opens the seed as it is.
MARIADB_URL=${PORTER_RIG_MARIADB_URL:-https://archive.mariadb.org/mariadb-11.4.13/bintar-linux-systemd-x86_64/mariadb-11.4.13-linux-systemd-x86_64.tar.gz}
MARIADB_SHA256=${PORTER_RIG_MARIADB_SHA256:-3cebf63914df3154b7cb6d548337eb2be42c773aeb641110446b72e2746cfed7}
mkdir -p "$RIG" "$PIDS"

say() { echo "rig: $*"; }
die() { echo "rig: $*" >&2; exit 1; }
port_open() { (echo > "/dev/tcp/127.0.0.1/$1") 2> /dev/null; }
wait_for() { # seconds, what, command...
	local seconds=$1 what=$2
	shift 2
	for _ in $(seq "$seconds"); do
		"$@" > /dev/null 2>&1 && return 0
		sleep 1
	done
	die "$what"
}
# A process the rig started, by the name it was recorded under: still running?
running() { [ -f "$PIDS/$1.pid" ] && kill -0 "$(cat "$PIDS/$1.pid")" 2> /dev/null; }
# Ends one of the rig's own processes (only ever a pid the rig recorded).
end() {
	local name=$1 pid
	[ -f "$PIDS/$name.pid" ] || return 0
	pid=$(cat "$PIDS/$name.pid")
	if kill -0 "$pid" 2> /dev/null; then
		kill "$pid" 2> /dev/null || true
		for _ in $(seq 30); do kill -0 "$pid" 2> /dev/null || break; sleep 1; done
		kill -9 "$pid" 2> /dev/null || true
	fi
	rm -f "$PIDS/$name.pid"
}

sql() { "$MARIA/bin/mariadb" --no-defaults -h127.0.0.1 -P"$DB_PORT" -uacore -pacore --batch --skip-column-names ${1:+"$1"}; }

# The package's ctl.sh as the rig runs it (ctl.rig.sh), with the environment the app gives it.
ctl() {
	FILES="$FILES" DB_PORT="$DB_PORT" TZ=UTC BLIZZ_LDSO="$RIG/bin/qemu-ld" BLIZZ_MARIA="$RIG/bin/maria" \
		RIG_MARIADB="$MARIA/bin/mariadb" sh "$FILES/server/ctl.rig.sh" "$@"
}

# The same in place of the calling (sub)shell, for a server started in the background: ctl.sh execs the server, the
# loader wrapper execs qemu, so the pid the rig records ($!) is the server's own and ending it ends the server.
ctl_exec() {
	exec env FILES="$FILES" DB_PORT="$DB_PORT" TZ=UTC BLIZZ_LDSO="$RIG/bin/qemu-ld" BLIZZ_MARIA="$RIG/bin/maria" \
		RIG_MARIADB="$MARIA/bin/mariadb" sh "$FILES/server/ctl.rig.sh" "$@"
}

fetch() {
	mkdir -p "$RIG/dl" "$FILES"
	if [ ! -x "$FILES/server/bin/worldserver" ]; then
		if [ ! -f "$RIG/dl/server.tar.xz" ]; then
			say "downloading the realm package"
			curl -sS -L --fail --retry 5 -o "$RIG/dl/server.tar.xz.part" "$PACKAGE_URL"
			mv "$RIG/dl/server.tar.xz.part" "$RIG/dl/server.tar.xz"
		fi
		echo "$PACKAGE_SHA256  $RIG/dl/server.tar.xz" | sha256sum -c - > /dev/null || die "the realm package's checksum is wrong"
		say "unpacking the realm package"
		tar -C "$FILES" -xJf "$RIG/dl/server.tar.xz"
		# (424 MB the rig no longer needs)
		rm -f "$RIG/dl/server.tar.xz"
	fi
	cat "$FILES/server/VERSION"
	# shellcheck disable=SC1091
	. "$REPO/realm/warcraft/server-data.env"
	python3 -I "$HERE/fetch-data.py" "$SERVER_DATA_URL" "$FILES/data" dbc Cameras maps
	if [ ! -x "$MARIA/bin/mariadbd" ]; then
		say "downloading MariaDB (only its server and client programs are kept)"
		curl -sS -L --fail --retry 3 -o "$RIG/dl/mariadb.tar.gz" "$MARIADB_URL"
		echo "$MARIADB_SHA256  $RIG/dl/mariadb.tar.gz" | sha256sum -c - > /dev/null || die "MariaDB's checksum is wrong"
		rm -rf "$MARIA.new"
		mkdir -p "$MARIA.new"
		tar -C "$MARIA.new" -xzf "$RIG/dl/mariadb.tar.gz" --strip-components=1 --wildcards '*/bin/mariadbd' '*/bin/mariadb' '*/bin/mariadb-admin' \
			'*/lib/plugin/dialog.so' '*/lib/plugin/mysql_clear_password.so'
		rm -f "$RIG/dl/mariadb.tar.gz"
		strip "$MARIA.new"/bin/* 2> /dev/null || true
		mv "$MARIA.new" "$MARIA"
	fi
	"$MARIA/bin/mariadbd" --version
}

prepare() {
	[ -x "$QEMU" ] || die "no $QEMU (apt-get install -y qemu-user-static)"
	[ -x "$MARIA/bin/mariadbd" ] || die "no MariaDB in the rig: rig.sh fetch"
	local loader
	loader=$(ls "$FILES"/server/lib/ld-musl-*.so.1 | head -1)
	mkdir -p "$RIG/bin" "$FILES/logs" "$FILES/run/tmp" "$FILES/client/Data"
	# The app runs every program through musl's loader (WowCtl.transform); here qemu runs the loader.
	printf '#!/bin/sh\nexec "%s" "%s" "$@"\n' "$QEMU" "$loader" > "$RIG/bin/qemu-ld"
	chmod +x "$RIG/bin/qemu-ld"
	cc -static -O1 -o "$RIG/bin/maria" "$HERE/nopreload.c"
	# ctl.rig.sh: ctl.sh with (1) the programs through the loader, as the app's ctl.blizz.sh has them;
	# (2) the client dbimport and the world server run being the machine's own; (3) the realm's
	# preloaded libraries given to the arm64 programs alone (qemu's QEMU_SET_ENV), not to this
	# machine's shell and tools, which could not load them.
	sed -E \
		-e 's|MySQLExecutable "\\"\$SERVER/bin/mariadb\\""|MySQLExecutable "\\"$BLIZZ_MARIA\\""|' \
		-e 's|"\$SERVER/bin/([A-Za-z0-9_.-]+)"|"$BLIZZ_LDSO" --library-path "$SERVER/lib" "$SERVER/bin/\1"|g' \
		-e 's|export LD_PRELOAD="|export QEMU_SET_ENV="LD_PRELOAD=|' \
		-e 's|LD_PRELOAD="\$COMPAT" "\$BLIZZ_LDSO"|QEMU_SET_ENV="LD_PRELOAD=$COMPAT" "$BLIZZ_LDSO"|' \
		"$FILES/server/ctl.sh" > "$FILES/server/ctl.rig.sh"
	grep -q 'QEMU_SET_ENV="LD_PRELOAD=\$COMPAT" "\$BLIZZ_LDSO"' "$FILES/server/ctl.rig.sh" || die "ctl.sh changed: the client's line wasn't rewritten"
	grep -q 'export QEMU_SET_ENV=' "$FILES/server/ctl.rig.sh" || die "ctl.sh changed: the preload line wasn't rewritten"
	ctl configure
	# The app's own first-run settings (WowSettings.apply): ChromieCraft's first brackets; and what the
	# rig's data allows (no vmaps or mmaps here). No random bots: an emulated world server is slow enough.
	local conf=$FILES/etc/worldserver.conf
	setkey() { if grep -q "^$2[[:space:]]*=" "$1"; then sed -i "s|^$2[[:space:]]*=.*|$2 = $3|" "$1"; else printf '%s = %s\n' "$2" "$3" >> "$1"; fi; }
	for realm_etc in "$FILES/etc" "$FILES/etc-remix"; do
		conf=$realm_etc/worldserver.conf
		[ -f "$conf" ] || continue
		setkey "$conf" vmap.enableLOS 0
		setkey "$conf" vmap.enableHeight 0
		setkey "$conf" vmap.enableIndoorCheck 0
		setkey "$conf" MoveMaps.Enable 0
		setkey "$realm_etc/modules/playerbots.conf" Playerbots.MinRandomBots 0
		setkey "$realm_etc/modules/playerbots.conf" Playerbots.MaxRandomBots 0
		setkey "$realm_etc/modules/playerbots.conf" Playerbots.DisabledWithoutRealPlayer 1
	done
	# The character loader's warnings and its login line in the logs (the realm's own setting shows errors alone):
	# what prove.sh reads to see that the world server had nothing to say about a ported character.
	setkey "$FILES/etc/worldserver.conf" Logger.entities.player "4,Console Server"
	setkey "$FILES/etc/worldserver.conf" Logger.entities.player.loading "3,Console Server"
	if [ ! -f "$FILES/etc/.defaults" ]; then
		setkey "$FILES/etc/modules/progression_system.conf" ProgressionSystem.Bracket_0 1
		setkey "$FILES/etc/modules/progression_system.conf" ProgressionSystem.Bracket_1_19 1
		echo 1 > "$FILES/etc/.defaults"
	fi
	say "prepared: $FILES/server/ctl.rig.sh, configs in $FILES/etc"
}

db_init() {
	[ ! -d "$DB_DIR/mysql" ] || { say "the database folder is there already ($DB_DIR)"; return 0; }
	# As ctl.sh's own `db` makes it on the phone: the package's seed (its user acore, its empty databases).
	rm -rf "$DB_DIR.new"
	cp -r "$FILES/server/mariadb-seed" "$DB_DIR.new"
	rm -rf "$DB_DIR"
	mv "$DB_DIR.new" "$DB_DIR"
	say "the database folder is made from the package's seed"
}

db_start() {
	if running mariadbd; then say "MariaDB is running"; return 0; fi
	port_open "$DB_PORT" && die "port $DB_PORT is taken by another program"
	[ -d "$DB_DIR/mysql" ] || db_init
	mkdir -p "$FILES/run/tmp" "$FILES/logs"
	local user=()
	[ "$(id -u)" != 0 ] || user=(--user=root)
	# ctl.sh's own `db` line, with this machine's build of the server in place of the package's arm64
	# one (same version; the messages and character sets are the package's files).
	"$MARIA/bin/mariadbd" --no-defaults --datadir="$DB_DIR" --basedir="$MARIA" \
		--lc-messages-dir="$FILES/server/share/mariadb" --character-sets-dir="$FILES/server/share/mariadb/charsets" \
		--plugin-dir="$MARIA/lib/plugin" --tmpdir="$FILES/run/tmp" \
		--socket="$FILES/run/mysqld.sock" --pid-file="$FILES/run/mysqld.pid" \
		--bind-address=127.0.0.1 --port="$DB_PORT" --skip-name-resolve \
		--innodb-use-native-aio=0 --innodb-log-file-size=48M --innodb-buffer-pool-size=256M \
		--max-allowed-packet=64M --log-error="$FILES/logs/mariadb.log" "${user[@]}" > /dev/null 2>&1 &
	echo $! > "$PIDS/mariadbd.pid"
	wait_for 90 "MariaDB didn't start: $(tail -5 "$FILES/logs/mariadb.log" 2> /dev/null)" sh -c "echo 'SELECT 1' | '$MARIA/bin/mariadb' --no-defaults -h127.0.0.1 -P$DB_PORT -uacore -pacore"
	say "MariaDB is up on port $DB_PORT"
}

db_stop() {
	if running mariadbd; then
		"$MARIA/bin/mariadb-admin" --no-defaults -h127.0.0.1 -P"$DB_PORT" -uacore -pacore shutdown 2> /dev/null || true
		local pid
		pid=$(cat "$PIDS/mariadbd.pid")
		for _ in $(seq 60); do kill -0 "$pid" 2> /dev/null || break; sleep 1; done
	fi
	end mariadbd
}

import() {
	running mariadbd || db_start
	local start
	start=$(date +%s)
	say "dbimport (the package's own, under qemu; minutes)"
	ctl dbimport > "$FILES/logs/dbimport.out" 2>&1 || die "dbimport failed: $(tail -20 "$FILES/logs/dbimport.out")"
	say "dbimport took $(($(date +%s) - start)) s"
	for db in acore_auth acore_characters acore_world; do
		say "$db: $(echo "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$db'" | sql) tables"
	done
	ctl modules main > "$FILES/logs/modules.out" 2>&1 || die "ctl.sh modules failed: $(tail -5 "$FILES/logs/modules.out")"
	cat "$FILES/logs/modules.out"
	ctl realmlist 127.0.0.1
}

account() {
	local name=${1:?account name} password=${2:?password}
	if [ -n "$(echo "SELECT id FROM account WHERE username = UPPER('$name')" | sql acore_auth)" ]; then
		say "the account $name is there"
		return 0
	fi
	python3 -I "$REPO/realm/warcraft/server/auth_check.py" account-sql "$name" "$password" | sql acore_auth
	say "the account $name is made (a game master's)"
}

auth_start() {
	if running authserver; then say "the login server is running"; return 0; fi
	port_open 3724 && die "port 3724 is taken by another program"
	(ctl_exec auth) > "$FILES/logs/auth.out" 2>&1 &
	echo $! > "$PIDS/authserver.pid"
	wait_for 120 "the login server didn't open port 3724: $(tail -5 "$FILES/logs/auth.out")" port_open 3724
	say "the login server is up"
}

world_start() {
	local realm=${1:-main} port=8085 logs=$FILES/logs
	[ "$realm" != remix ] || { port=8086; logs=$FILES/logs/remix; }
	if running worldserver; then say "a world server is running"; return 0; fi
	port_open "$port" && die "port $port is taken by another program"
	mkdir -p "$logs"
	# Its console is a pipe the rig keeps open: world-stop types the shutdown there, as the app does.
	rm -f "$FILES/run/world.in"
	mkfifo "$FILES/run/world.in"
	tail -f /dev/null > "$FILES/run/world.in" &
	echo $! > "$PIDS/world-console.pid"
	: > "$logs/world.out"
	(ctl_exec world "$realm") < "$FILES/run/world.in" > "$logs/world.out" 2>&1 &
	echo $! > "$PIDS/worldserver.pid"
	echo "$logs/world.out" > "$PIDS/worldserver.log"
	local start
	start=$(date +%s)
	say "the world server ($realm) is starting (emulated: several minutes; the first start also applies the modules' SQL)"
	for _ in $(seq "${WORLD_WAIT:-3600}"); do
		running worldserver || die "the world server ended while starting: $(tail -30 "$logs/world.out")"
		grep -q "(worldserver-daemon) ready" "$logs/world.out" && break
		sleep 1
	done
	grep -q "(worldserver-daemon) ready" "$logs/world.out" || die "the world server didn't get ready"
	say "the world server was ready in $(($(date +%s) - start)) s"
}

world_console() {
	running worldserver || die "no world server is running"
	echo "$*" > "$FILES/run/world.in"
}

world_stop() {
	if running worldserver; then
		echo "server shutdown 1" > "$FILES/run/world.in"
		local pid
		pid=$(cat "$PIDS/worldserver.pid")
		for _ in $(seq 120); do kill -0 "$pid" 2> /dev/null || break; sleep 1; done
	fi
	end worldserver
	end world-console
	rm -f "$FILES/run/world.in"
	say "the world server is stopped"
}

status() {
	for name in mariadbd authserver worldserver; do
		if running "$name"; then echo "$name: running (pid $(cat "$PIDS/$name.pid"))"; else echo "$name: stopped"; fi
	done
	du -sh "$RIG" 2> /dev/null | sed 's/^/disk: /'
}

cmd=${1:-}
[ $# -gt 0 ] && shift
case "$cmd" in
setup)
	fetch
	prepare
	db_init
	db_start
	import
	account "${1:-porter}" "${2:-porter123}"
	;;
fetch) fetch ;;
prepare) prepare ;;
db-init) db_init ;;
db-start) db_start ;;
db-stop)
	db_stop
	say "MariaDB is stopped"
	;;
import) import ;;
account) account "$@" ;;
auth-start) auth_start ;;
auth-stop) end authserver ;;
world-start) world_start "$@" ;;
world-stop) world_stop ;;
world-console) world_console "$@" ;;
sql) sql "$@" ;;
ctl) ctl "$@" ;;
status) status ;;
stop)
	world_stop
	end authserver
	db_stop
	say "everything the rig started is stopped"
	;;
*)
	sed -n '2,/^set -euo/p' "$0" | sed '$d' >&2
	exit 2
	;;
esac
