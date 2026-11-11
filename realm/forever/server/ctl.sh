#!/bin/sh
# Runs the Forever realm on the phone (TrinityCore's "forever" branch): its own MariaDB, the Battle.net login server
# (bnetserver), the world server (worldserver) and the server's data tools. Everything is under $FILES
# (files/forever), apart from the other realms'. The app runs it with Android's shell (/system/bin/sh): POSIX sh only.
# Server commands `exec`, so the process the app holds is the server itself. Made after the World of Warcraft app's
# Felsong ctl.sh.
#
#   ctl.sh configure               write the configs (from the shipped .dist files), the folders and, the first time,
#                                  this phone's own certificate authority and the login server's certificate
#   ctl.sh db-init                 make MariaDB's data folder from the seed (moved, not copied), if there's none
#   ctl.sh db                      run MariaDB (makes its data folder from the seed first)
#   ctl.sh db-ping | db-stop       ask MariaDB if it's up / to shut down
#   ctl.sh sql [database]          run the SQL on stdin (prints tab-separated rows)
#   ctl.sh account NAME PASSWORD   make a game account (NAME is an e-mail address), or set its password
#   ctl.sh realm-build BUILD       offer realm 70 at the client's build (fails, saying which it supports, if unknown)
#   ctl.sh bnetserver | worldserver run the login server / world server
#   ctl.sh maps|vmaps|mmaps CLIENT make the server's data from the Forever client's folder (the one with .build.info)
#   ctl.sh data-done               put the data made (data.work) in place of data
#
# FILES is the Forever folder; the programs are built to run from $FILES/server.
set -eu

FILES="${FILES:-/data/data/com.logie.blizz/files/forever}"
SERVER="$FILES/server"
ETC="$FILES/etc"
DATA="$FILES/data"
DB_DIR="$FILES/mysql"
LOGS="$FILES/logs"
RUN="$FILES/run"
CA_DIR="$FILES/ca"
# The client's Battle.net port (1119) and REST login (8081) are fixed by the client and shared with the Legion realm:
# the app stops one before starting the other. The rest are Forever's own.
DB_PORT="${DB_PORT:-3313}"
BNET_PORT=1119
REST_PORT=8081
WORLD_PORT=8105
INSTANCE_PORT=8106
DB_USER=forever
DB_PASS=forever
HOSTNAME_LOGIN=trinity.actual.battle.net
# Android's shell (mksh) takes TMPDIR only if it is a writable folder when it is set (here-documents are written there;
# otherwise it falls back to /data/local, which an app can't write): make the folder first.
mkdir -p "$RUN/tmp"
export HOME="$FILES" TMPDIR="$RUN/tmp"
export OPENSSL_MODULES="$SERVER/lib/ossl-modules" OPENSSL_CONF="$SERVER/etc/openssl.cnf"

case "$FILES" in
*/files/forever) ;;
*) echo "FILES must be the app's files/forever folder, not $FILES" >&2; exit 2 ;;
esac

setkey() {
	file=$1 key=$2 value=$3
	if grep -q "^$key[[:space:]]*=" "$file"; then
		escaped=$(printf '%s' "$value" | sed 's/[|&\\]/\\&/g')
		sed -i "s|^$key[[:space:]]*=.*|$key = $escaped|" "$file"
	else
		printf '%s = %s\n' "$key" "$value" >> "$file"
	fi
}

config_from_dist() {
	[ -f "$2" ] || cp "$1" "$2"
}

dbinfo() {
	echo "\"127.0.0.1;$DB_PORT;$DB_USER;$DB_PASS;$1\""
}

COMPAT="$SERVER/lib/libandroidcompat.so"
musl_programs() {
	export LD_PRELOAD="$COMPAT"
}

openssl_() {
	LD_PRELOAD="$COMPAT" "$SERVER/bin/openssl" "$@"
}

# This phone's own certificate authority, made here the first time and never shared: it may only sign names under
# actual.battle.net (nameConstraints), and only the game's Windows trusts it (the app adds ca.pem there). The login
# server's certificate for trinity.actual.battle.net is signed with it.
make_certificates() {
	mkdir -p "$CA_DIR"
	if [ ! -s "$CA_DIR/ca.pem" ] || [ ! -s "$CA_DIR/ca.key" ]; then
		cat > "$CA_DIR/ca.ext" <<EOF
basicConstraints = critical,CA:TRUE
keyUsage = critical,keyCertSign,cRLSign
nameConstraints = critical,permitted;DNS:actual.battle.net
subjectKeyIdentifier = hash
EOF
		openssl_ req -new -newkey rsa:2048 -nodes -keyout "$CA_DIR/ca.key" -subj "/CN=Blizzard app Forever realm CA" \
			-out "$CA_DIR/ca.csr"
		openssl_ x509 -req -in "$CA_DIR/ca.csr" -signkey "$CA_DIR/ca.key" -days 7300 -sha256 \
			-extfile "$CA_DIR/ca.ext" -out "$CA_DIR/ca.pem"
		rm -f "$CA_DIR/ca.csr" "$CA_DIR/server.pem"
	fi
	if [ ! -s "$CA_DIR/server.pem" ] || [ ! -s "$CA_DIR/server.key" ]; then
		cat > "$CA_DIR/server.ext" <<EOF
basicConstraints = CA:FALSE
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = DNS:$HOSTNAME_LOGIN
EOF
		openssl_ req -new -newkey rsa:2048 -nodes -keyout "$CA_DIR/server.key" -subj "/CN=$HOSTNAME_LOGIN" \
			-out "$CA_DIR/server.csr"
		openssl_ x509 -req -in "$CA_DIR/server.csr" -CA "$CA_DIR/ca.pem" -CAkey "$CA_DIR/ca.key" -CAcreateserial \
			-days 3650 -sha256 -extfile "$CA_DIR/server.ext" -out "$CA_DIR/server.crt"
		cat "$CA_DIR/server.crt" "$CA_DIR/ca.pem" > "$CA_DIR/server.pem"
		rm -f "$CA_DIR/server.csr" "$CA_DIR/server.crt"
	fi
	chmod 600 "$CA_DIR"/*.key
}

configure() {
	mkdir -p "$ETC" "$DATA" "$LOGS" "$RUN/tmp"
	make_certificates
	for name in bnetserver worldserver; do
		config_from_dist "$SERVER/etc/$name.conf.dist" "$ETC/$name.conf"
	done
	conf="$ETC/bnetserver.conf"
	setkey "$conf" LoginDatabaseInfo "$(dbinfo auth)"
	setkey "$conf" LogsDir "\"$LOGS\""
	setkey "$conf" BattlenetPort "$BNET_PORT"
	setkey "$conf" LoginREST.Port "$REST_PORT"
	setkey "$conf" LoginREST.ExternalAddress "$HOSTNAME_LOGIN"
	setkey "$conf" LoginREST.LocalAddress "$HOSTNAME_LOGIN"
	setkey "$conf" CertificatesFile "\"$CA_DIR/server.pem\""
	setkey "$conf" PrivateKeyFile "\"$CA_DIR/server.key\""
	setkey "$conf" Realm.CfgContentSetID 137
	setkey "$conf" BindIP "\"127.0.0.1\""
	setkey "$conf" Updates.EnableDatabases 0
	setkey "$conf" MySQLExecutable "\"$SERVER/bin/mariadb\""
	conf="$ETC/worldserver.conf"
	setkey "$conf" LoginDatabaseInfo "$(dbinfo auth)"
	setkey "$conf" WorldDatabaseInfo "$(dbinfo world)"
	setkey "$conf" CharacterDatabaseInfo "$(dbinfo characters)"
	setkey "$conf" HotfixDatabaseInfo "$(dbinfo hotfixes)"
	setkey "$conf" DataDir "\"$DATA\""
	setkey "$conf" LogsDir "\"$LOGS\""
	setkey "$conf" WorldServerPort "$WORLD_PORT"
	setkey "$conf" InstanceServerPort "$INSTANCE_PORT"
	setkey "$conf" BindIP "\"127.0.0.1\""
	# The Classic client only accepts realm 70; the branch's settings for it.
	setkey "$conf" RealmID 70
	setkey "$conf" Expansion 0
	setkey "$conf" Network.SkipBuildAuthKeyCheck 1
	setkey "$conf" Network.EnterEncryptedModeRegionGroup 8
	setkey "$conf" SourceDirectory "\"$SERVER\""
	setkey "$conf" MySQLExecutable "\"$SERVER/bin/mariadb\""
	setkey "$conf" Updates.EnableDatabases 15
	setkey "$conf" Updates.AutoSetup 0
	setkey "$conf" Console.Enable 1
	setkey "$conf" Ra.Enable 0
	setkey "$conf" SOAP.Enabled 0
	setkey "$conf" GameType 0
	# Pathfinding data takes hours to make on a phone: off until mmaps are made (ctl.sh mmaps).
	if [ -d "$DATA/mmaps" ]; then setkey "$conf" MoveMaps.Enable 1; else setkey "$conf" MoveMaps.Enable 0; fi
	if [ -d "$DATA/vmaps" ]; then
		setkey "$conf" vmap.enableLOS 1; setkey "$conf" vmap.enableHeight 1
	else
		setkey "$conf" vmap.enableLOS 0; setkey "$conf" vmap.enableHeight 0
	fi
	setkey "$conf" GridUnload 1
	setkey "$conf" ThreadPool 2
	setkey "$conf" MapUpdate.Threads 2
}

db_client() {
	LD_PRELOAD="$COMPAT" "$SERVER/bin/mariadb" --no-defaults -h127.0.0.1 -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$@"
}

db_init() {
	if [ ! -d "$DB_DIR/mysql" ]; then
		[ -d "$SERVER/mariadb-seed/mysql" ] || { echo "No database and no seed to make it from: reinstall the realm server." >&2; exit 1; }
		rm -rf "$DB_DIR"
		# Moved, not copied: the seed is ~2 GB and is only ever used once (same file system: instant).
		mv "$SERVER/mariadb-seed" "$DB_DIR"
	fi
	# A newer package brings a seed of its own; the database made from the first one is kept (it holds the characters).
	rm -rf "$SERVER/mariadb-seed"
}

# The realm on offer (70) at the client's own build: the client lists only realms of its build, and the login server
# accepts only builds it knows (build_info). ctl.sh realm-build BUILD
realm_build() {
	case "$1" in ''|*[!0-9]*) echo "Not a build number: $1" >&2; exit 2 ;; esac
	known=$(echo "SELECT COUNT(*) FROM build_info WHERE build = $1;" | db_client --batch --skip-column-names auth)
	if [ "$known" != 1 ]; then
		# Self-hosting: the build auth key check is off (configure: Network.SkipBuildAuthKeyCheck 1), so the realm can
		# accept whatever build the client auto-updated to. Rather than refuse a client that is merely newer than the
		# seed database, add the build to build_info, copied from the newest known build (through a temporary table, so
		# it does not depend on the table's exact columns). The copied auth seeds are never checked (the check is off).
		db_client auth >/dev/null 2>&1 <<SQL
CREATE TEMPORARY TABLE _blizz_bi LIKE build_info;
INSERT INTO _blizz_bi SELECT * FROM build_info ORDER BY build DESC LIMIT 1;
UPDATE _blizz_bi SET build = $1;
INSERT IGNORE INTO build_info SELECT * FROM _blizz_bi;
DROP TEMPORARY TABLE _blizz_bi;
SQL
		known=$(echo "SELECT COUNT(*) FROM build_info WHERE build = $1;" | db_client --batch --skip-column-names auth)
	fi
	if [ "$known" != 1 ]; then
		builds=$(echo "SELECT GROUP_CONCAT(build ORDER BY build) FROM build_info WHERE build >= 70000;" |
			db_client --batch --skip-column-names auth)
		echo "This realm couldn't be set to Forever client build $1 (it knows: $builds). Reinstall the realm server." >&2
		exit 3
	fi
	echo "UPDATE realmlist SET gamebuild = $1 WHERE id = 70;" | db_client auth
	echo "Realm 70 offered at build $1"
}

cmd=${1:-}
[ $# -gt 0 ] && shift
case "$cmd" in
configure)
	configure "$@"
	;;
db-init)
	mkdir -p "$RUN/tmp" "$LOGS"
	db_init
	;;
db)
	mkdir -p "$RUN/tmp" "$LOGS"
	db_init
	[ "$(id -u)" = 0 ] && set -- --user=root "$@"
	musl_programs
	exec "$SERVER/bin/mariadbd" --no-defaults --datadir="$DB_DIR" --basedir="$SERVER" \
		--lc-messages-dir="$SERVER/share/mariadb" --character-sets-dir="$SERVER/share/mariadb/charsets" \
		--plugin-dir="$SERVER/lib/mariadb-plugins" --tmpdir="$RUN/tmp" \
		--socket="$RUN/mysqld.sock" --pid-file="$RUN/mysqld.pid" \
		--bind-address=127.0.0.1 --port="$DB_PORT" --skip-name-resolve \
		--character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci \
		--innodb-use-native-aio=0 --innodb-log-file-size=96M --innodb-buffer-pool-size=256M \
		--max-allowed-packet=64M --log-error="$LOGS/mariadb.log" "$@"
	;;
db-ping)
	musl_programs
	exec "$SERVER/bin/mariadb-admin" --no-defaults -h127.0.0.1 -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" \
		--connect-timeout=2 ping
	;;
db-stop)
	musl_programs
	exec "$SERVER/bin/mariadb-admin" --no-defaults -h127.0.0.1 -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" shutdown
	;;
sql)
	db_client --batch --skip-column-names ${1:+"$1"}
	;;
realm-build)
	[ $# -eq 1 ] || { echo "ctl.sh realm-build BUILD" >&2; exit 2; }
	realm_build "$1"
	;;
account)
	# TrinityCore's own command, through the world server's console: bnetaccount create (or set password).
	[ $# -eq 2 ] || { echo "ctl.sh account NAME PASSWORD" >&2; exit 2; }
	cd "$RUN"
	musl_programs
	printf 'bnetaccount create %s %s\nbnetaccount set password %s %s %s\nserver shutdown 1\n' "$1" "$2" "$1" "$2" "$2" |
		exec "$SERVER/bin/worldserver" -c "$ETC/worldserver.conf"
	;;
bnetserver)
	cd "$RUN"
	musl_programs
	exec "$SERVER/bin/bnetserver" -c "$ETC/bnetserver.conf"
	;;
worldserver)
	cd "$RUN"
	musl_programs
	exec "$SERVER/bin/worldserver" -c "$ETC/worldserver.conf"
	;;
maps)
	# dbc, gt, maps and cameras, read from the client's CASC storage (product wowf). The tool reads the client from
	# the folder given and writes into its working folder.
	rm -rf "$DATA.work"
	mkdir -p "$DATA.work" && cd "$DATA.work"
	musl_programs
	exec "$SERVER/bin/mapextractor" -i "$1" -o "$DATA.work"
	;;
vmaps)
	mkdir -p "$DATA.work/vmaps" && cd "$DATA.work"
	musl_programs
	"$SERVER/bin/vmap4extractor" -d "$1"
	"$SERVER/bin/vmap4assembler" Buildings vmaps
	rm -rf Buildings
	;;
mmaps)
	cd "$DATA.work"
	musl_programs
	exec "$SERVER/bin/mmaps_generator"
	;;
data-done)
	[ -d "$DATA.work/dbc" ] && [ -d "$DATA.work/maps" ] || { echo "No dbc and maps in $DATA.work" >&2; exit 1; }
	rm -rf "$DATA.old"
	[ ! -d "$DATA" ] || mv "$DATA" "$DATA.old"
	mv "$DATA.work" "$DATA"
	rm -rf "$DATA.old"
	;;
*)
	sed -n '2,20p' "$0" >&2
	exit 2
	;;
esac
