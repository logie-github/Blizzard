#!/bin/sh
# Packs the compiled Forever server (build/forever-new-dist, from compile-forever-new.sh) into
# build/forever-new-publish/forever-android-arm64.tar.xz: the programs, every library they load, musl's loader,
# Alpine's MariaDB, OpenSSL's legacy provider (RC4 for the game's packet headers), the system-call shim, the SQL,
# the configs and the licence files. No game files, no keys, no credentials. Run in the same Alpine as the compile.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../warcraft/forever-new/forever-version.env
. "$ROOT/warcraft/forever-new/forever-version.env"

if [ -z "${IN_ALPINE:-}" ]; then
	# shellcheck disable=SC2086
	exec docker run --rm -e IN_ALPINE=1 ${DOCKER_RUN_ARGS:-} -v "$ROOT:/repo" -w /repo "alpine:$ALPINE_VERSION" /repo/scripts/package-forever-new.sh
fi

DIST=/repo/build/forever-new-dist
OUT=/repo/build/forever-new-publish
STAGE=/repo/build/forever-new-stage
[ -x "$DIST/bin/worldserver" ] || { echo "No compiled server in $DIST: run scripts/compile-forever-new.sh first." >&2; exit 1; }

apk add -q --no-progress build-base xz tar boost-dev openssl-dev mariadb-connector-c-dev readline-dev bzip2-dev zlib-dev \
	mariadb mariadb-client jemalloc patchelf openssl

rm -rf "$STAGE" "$OUT"
pkg="$STAGE/forever"
mkdir -p "$pkg/bin" "$pkg/lib/ossl-modules" "$pkg/etc" "$pkg/share" "$pkg/src"
cp "$DIST"/bin/* "$pkg/bin/"
for prog in mariadbd mariadb mariadb-admin mariadb-dump mariadb-install-db openssl; do
	p=$(command -v "$prog" || true)
	[ -n "$p" ] && cp -L "$p" "$pkg/bin/" || echo "note: $prog not found" >&2
done
cp -r /usr/share/mariadb "$pkg/share/mariadb"
cp -L /usr/lib/ossl-modules/legacy.so "$pkg/lib/ossl-modules/"
cp -L /usr/lib/libjemalloc.so.2 "$pkg/lib/"
cc -O2 -shared -fPIC -o "$pkg/lib/libandroidcompat.so" /repo/warcraft/server/android_compat.c
# The login server's own portal name (*.actual.battle.net) is this phone, answered for these programs only.
cc -O2 -shared -fPIC -o "$pkg/lib/libforeverresolve.so" /repo/warcraft/forever-new/forever_resolve.c

# Every shared library each program loads (musl's ldd), and musl's loader itself.
for exe in "$pkg"/bin/*; do
	ldd "$exe" 2>/dev/null | awk '/=>/ {print $3}' | while read -r lib; do
		[ -f "$lib" ] && cp -Ln "$lib" "$pkg/lib/" || true
	done
done
loader=$(ls /lib/ld-musl-*.so.1 | head -1)
cp -L "$loader" "$pkg/lib/"
# The programs run through the loader with --library-path, so their own interpreter and rpath don't matter; the rpath
# is relative anyway.
for exe in "$pkg"/bin/*; do patchelf --set-rpath '$ORIGIN/../lib' "$exe" 2>/dev/null || true; done

cp "$DIST"/etc/*.conf.dist "$pkg/etc/"
[ ! -d "$DIST/etc/worldserver.conf.d" ] || cp -r "$DIST/etc/worldserver.conf.d" "$pkg/etc/worldserver.conf.d"
cp "$DIST"/etc/*.yaml "$pkg/etc/" 2>/dev/null || true
cp -r "$DIST/sql" "$pkg/src/sql"
cp -r "$DIST/legal" "$pkg/legal"
cp -r "$DIST/ForeverBots-addon-source" "$pkg/ForeverBots-addon-source"
cp /repo/warcraft/forever-new/forever-version.env "$pkg/forever-version.env"
cp "$DIST/SOURCE_COMMIT" "$pkg/SOURCE_COMMIT"
printf 'WoW Forever server for Android (linux aarch64, musl)\nsource %s (Karrz1/TrinityCore forever-bots)\nupstream %s\nformat %s\n' \
	"$(cat "$DIST/SOURCE_COMMIT")" "$UPSTREAM_VERSION" "$PACKAGE_FORMAT" > "$pkg/VERSION"
# Component hashes, for the app's repair check.
(cd "$pkg" && find bin lib -type f -exec sha256sum {} + | sort -k2) > "$pkg/COMPONENTS.sha256"

mkdir -p "$OUT"
tar -C "$STAGE" -cf - forever | xz -T0 -6 > "$OUT/$PACKAGE_ASSET"
du -sh "$OUT/$PACKAGE_ASSET"
