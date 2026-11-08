#!/bin/sh
# Packs the Forever realm into build/forever/forever-server.tar.xz: the programs scripts/compile-trinity-forever.sh left
# in build/trinity-forever-dist with every library they load (from the phone's Alpine), Alpine's MariaDB and openssl
# for arm64, the system call shim, the SQL, the configs, a seed database folder with TrinityCore's databases made and
# the branch's world and hotfixes imported, and its ctl.sh. Next to it, forever-server.json: the package's size and
# SHA-256 (the app checks the download against them). Made after the World of Warcraft app's package-legioncore.sh.
#
# The branch's database release must be in build/trinity-forever-db (CI downloads it: its .sql files, or archives of
# them). The programs run from /data/data/com.logie.blizz/files/forever/server.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../forever/server-version.env
. "$ROOT/forever/server-version.env"

if [ -z "${IN_ALPINE:-}" ]; then
	# shellcheck disable=SC2086
	exec docker run --rm -e IN_ALPINE=1 ${DOCKER_RUN_ARGS:-} \
		-v "$ROOT:/repo" -w /repo "alpine:$ALPINE_VERSION" /repo/scripts/package-trinity-forever.sh
fi
[ "$(uname -m)" = aarch64 ] || { echo "Package this on an arm64 machine." >&2; exit 1; }

PREFIX=/data/data/com.logie.blizz/files/forever/server
DIST=/repo/build/trinity-forever-dist
STAGE=/repo/build/forever-stage
OUT=/repo/build/forever
DB_IN=/repo/build/trinity-forever-db

[ -x "$DIST/bin/worldserver" ] || { echo "No compiled realm in build/trinity-forever-dist: run scripts/compile-trinity-forever.sh first." >&2; exit 1; }

apk add -q --no-progress patchelf xz tar 7zip unzip curl clang20 lld20 llvm20 file \
	mariadb mariadb-client openssl libstdc++ boost-dev openssl-dev mariadb-connector-c-dev readline-dev bzip2-dev zlib-dev ncurses-dev

rm -rf "$STAGE"
pkg="$STAGE/server"
mkdir -p "$pkg/bin" "$pkg/lib" "$pkg/etc" "$pkg/share"
cp "$DIST"/bin/* "$pkg/bin/"
# Project-built shared libraries the programs load (libopenssl_ed25519.so); they aren't in Alpine, so stage them from
# the build before resolving dependencies, and resolve their own deps (openssl) below.
[ -d "$DIST/lib" ] && [ -n "$(ls -A "$DIST/lib" 2>/dev/null)" ] && cp -L "$DIST"/lib/*.so* "$pkg/lib/"
for prog in mariadbd mariadb mariadb-admin mariadb-dump openssl; do
	cp "$(command -v "$prog")" "$pkg/bin/"
done
cp -r /usr/share/mariadb "$pkg/share/mariadb"
cp "$DIST"/etc/* "$pkg/etc/"
cp /repo/forever/server/openssl.cnf "$pkg/etc/"
cp -r "$DIST/sql" "$pkg/sql"
mkdir -p "$pkg/lib/ossl-modules"
cp -L /usr/lib/ossl-modules/legacy.so "$pkg/lib/ossl-modules/"
clang --target=aarch64-alpine-linux-musl -fuse-ld=lld -O2 -shared -fPIC \
	-o "$pkg/lib/libandroidcompat.so" /repo/warcraft/server/android_compat.c

needed() {
	llvm-readelf -d "$1" 2>/dev/null | sed -n 's/.*Shared library: \[\(.*\)\]/\1/p'
}
copy_deps() {
	for name in $(needed "$1"); do
		case "$name" in ld-musl-*|libc.musl-*|libc.so) continue ;; esac
		[ -f "$pkg/lib/$name" ] && continue
		found=
		for dir in /usr/lib /lib; do
			[ -e "$dir/$name" ] && { found="$dir/$name"; break; }
		done
		[ -n "$found" ] || { echo "$(basename "$1") needs $name, which isn't in Alpine here" >&2; exit 1; }
		cp -L "$found" "$pkg/lib/$name"
		copy_deps "$pkg/lib/$name"
	done
}
for prog in "$pkg"/bin/* "$pkg"/lib/*.so* "$pkg/lib/ossl-modules/legacy.so" "$pkg/lib/libandroidcompat.so"; do
	[ -e "$prog" ] || continue
	copy_deps "$prog"
done
cp -L /lib/ld-musl-aarch64.so.1 "$pkg/lib/ld-musl-aarch64.so.1"
cp -L /lib/ld-musl-aarch64.so.1 "$pkg/lib/libc.musl-aarch64.so.1"
interp="$PREFIX/lib/ld-musl-aarch64.so.1"
for prog in "$pkg"/bin/*; do
	llvm-strip "$prog"
	patchelf --set-interpreter "$interp" --set-rpath '$ORIGIN/../lib' "$prog"
done
for lib in "$pkg"/lib/*.so*; do
	case "$(basename "$lib")" in ld-musl-*|libc.musl-*) continue ;; esac
	llvm-strip --strip-unneeded "$lib"
	patchelf --set-rpath '$ORIGIN' "$lib"
done
llvm-strip --strip-unneeded "$pkg/lib/ossl-modules/legacy.so"
patchelf --set-rpath '$ORIGIN/..' "$pkg/lib/ossl-modules/legacy.so"
for prog in "$pkg"/bin/* "$pkg"/lib/*.so* "$pkg/lib/ossl-modules/legacy.so"; do
	for name in $(needed "$prog"); do
		case "$name" in ld-musl-*|libc.musl-*|libc.so) continue ;; esac
		[ -f "$pkg/lib/$name" ] || { echo "$(basename "$prog") needs $name, not packed" >&2; exit 1; }
	done
done

# The branch's database release: its world and hotfixes SQL (archives unpacked first).
[ -d "$DB_IN" ] || { echo "No build/trinity-forever-db: download $TRINITY_DB_REPO's $TRINITY_DB_TAG release there." >&2; exit 1; }
for archive in "$DB_IN"/*.7z "$DB_IN"/*.zip "$DB_IN"/*.tar.* "$DB_IN"/*.gz; do
	[ -f "$archive" ] || continue
	case "$archive" in
	*.7z|*.zip) 7zz x -y -bd -o"$DB_IN" "$archive" > /dev/null ;;
	*.tar.*) tar -C "$DB_IN" -xf "$archive" ;;
	*.gz) gunzip -kf "$archive" ;;
	esac
done
world_sql=$(find "$DB_IN" -iname 'TDB_full_world*.sql' | head -1)
hotfixes_sql=$(find "$DB_IN" -iname 'TDB_full_hotfixes*.sql' | head -1)
[ -n "$world_sql" ] && [ -n "$hotfixes_sql" ] || { echo "The release has no world or hotfixes SQL:" >&2; find "$DB_IN" >&2; exit 1; }

seed="$pkg/mariadb-seed"
mariadb-install-db --no-defaults --auth-root-authentication-method=normal --skip-test-db \
	--user=root --datadir="$seed" > /dev/null
mariadbd --no-defaults --user=root --datadir="$seed" --socket=/tmp/seed.sock --port=3399 --bind-address=127.0.0.1 \
	--character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci \
	--innodb-use-native-aio=0 --innodb-log-file-size=96M --innodb-buffer-pool-size=1G \
	--max-allowed-packet=256M > /tmp/seed.log 2>&1 &
for _ in $(seq 60); do mariadb-admin --socket=/tmp/seed.sock ping > /dev/null 2>&1 && break; sleep 1; done
sqlc() { mariadb --socket=/tmp/seed.sock -uroot --max-allowed-packet=256M "$@"; }
for db in auth characters world hotfixes; do
	echo "CREATE DATABASE \`$db\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" | sqlc
done
sqlc auth < "$DIST/sql/base/auth_database.sql"
sqlc characters < "$DIST/sql/base/characters_database.sql"
sqlc world < "$world_sql"
sqlc hotfixes < "$hotfixes_sql"
sqlc < /repo/forever/server/seed.sql
creatures=$(echo "SELECT COUNT(*) FROM world.creature_template;" | sqlc -N)
echo "world: $creatures creature templates"
[ "$creatures" -gt 10000 ] || { echo "The world database looks empty" >&2; exit 1; }

# The database updates (TrinityCore's and the branch's sql/custom, including the realm's move to 70 and the client
# build), applied here by the world server's own updater so the phone's first start doesn't spend its time on them.
# The world server stops by itself after the updates (no client data here); what it printed is kept in the log.
mkdir -p /tmp/ws-etc /tmp/ws-logs
cp "$DIST/etc/worldserver.conf.dist" /tmp/ws-etc/worldserver.conf
cat >> /tmp/ws-etc/worldserver.conf <<EOF
LoginDatabaseInfo = "127.0.0.1;3399;root;;auth"
WorldDatabaseInfo = "127.0.0.1;3399;root;;world"
CharacterDatabaseInfo = "127.0.0.1;3399;root;;characters"
HotfixDatabaseInfo = "127.0.0.1;3399;root;;hotfixes"
SourceDirectory = "$pkg"
MySQLExecutable = "/usr/bin/mariadb"
Updates.EnableDatabases = 15
Updates.AutoSetup = 0
DataDir = "/tmp/ws-nodata"
LogsDir = "/tmp/ws-logs"
RealmID = $REALM_ID
Console.Enable = 0
EOF
echo "ALTER USER 'root'@'localhost' IDENTIFIED BY ''; FLUSH PRIVILEGES;" | sqlc || true
(cd /tmp && timeout 3600 "$DIST/bin/worldserver" -c /tmp/ws-etc/worldserver.conf > /tmp/ws-update.log 2>&1) || true
grep -iE "updat|applied|error" /tmp/ws-update.log | tail -40 || true
echo "SELECT id, name, address, gamebuild FROM auth.realmlist;" | sqlc
# The realm the client accepts (70), on this phone, on the realm's own ports (ctl.sh WORLD_PORT, INSTANCE_PORT).
echo "UPDATE auth.realmlist SET address = '127.0.0.1', localAddress = '127.0.0.1', port = 8105 WHERE id = $REALM_ID;" | sqlc
echo "SELECT id, name, address, port, gamebuild FROM auth.realmlist;" | sqlc
mariadb-admin --socket=/tmp/seed.sock -uroot shutdown
wait
rm -f "$seed"/*.err "$seed"/*.pid "$seed"/aria_log_control.lock

cat > "$pkg/VERSION" <<EOF
trinitycore-forever $(cat "$DIST/commit")
world $(basename "$world_sql" .sql)
client $CLIENT_BUILD
mariadb $(apk info -e -v mariadb)
alpine $ALPINE_VERSION aarch64
EOF
cp /repo/forever/server/ctl.sh "$pkg/ctl.sh"
chmod +x "$pkg/ctl.sh"

mkdir -p "$OUT"
rm -f "$OUT/forever-server.tar.xz"
tar -C "$STAGE" -cf - server | xz -T0 -6 > "$OUT/forever-server.tar.xz"
size=$(stat -c %s "$OUT/forever-server.tar.xz")
sha=$(sha256sum "$OUT/forever-server.tar.xz" | cut -d' ' -f1)
unpacked=$(du -sb "$pkg" | cut -f1)
cat > "$OUT/forever-server.json" <<EOF
{
  "file": "forever-server.tar.xz",
  "size": $size,
  "sha256": "$sha",
  "unpacked": $unpacked,
  "trinitycore": "$(cat "$DIST/commit")",
  "client_build": $CLIENT_BUILD,
  "realm_id": $REALM_ID,
  "arch": "aarch64"
}
EOF
du -sh "$pkg" "$OUT/forever-server.tar.xz"
cat "$pkg/VERSION" "$OUT/forever-server.json"
