#!/bin/sh
# Compiles the World of Warcraft app's private server for Linux on musl (Alpine), for this
# machine's architecture: AzerothCore at the revision ChromieCraft runs with the playerbots fork's
# core changes merged onto it, the modules in warcraft/server-version.env, and AzerothCore's data
# tools. Leaves what scripts/package-azerothcore.sh packs in build/azerothcore-dist: the programs,
# their configs, mmaps_generator's settings, and the core's and the modules' SQL.
#
# This is the slow part. CI caches its output by its own inputs (the pins, the patches, this script
# and the fetch script), so a change to the packaging (ctl.sh, the libraries, the SQL layout)
# compiles nothing, and ccache makes a new revision of the core quicker.
#
# On a machine with Docker, runs itself in an Alpine container of the machine's architecture
# (GitHub's ubuntu-24.04-arm runners build the phone's arm64). DOCKER_RUN_ARGS adds arguments to
# `docker run` (a proxy, for example). FETCH=0 compiles build/azerothcore as it is, without
# checking it out again (for trying a change to the source).
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../warcraft/server-version.env
. "$ROOT/warcraft/server-version.env"

if [ -z "${IN_ALPINE:-}" ]; then
	mkdir -p "$ROOT/build"
	# shellcheck disable=SC2086
	exec docker run --rm -e IN_ALPINE=1 -e JOBS="${JOBS:-}" -e NINJA_ARGS="${NINJA_ARGS:-}" -e FETCH="${FETCH:-1}" \
		-e WOW_EXTRA_MODULES="${WOW_EXTRA_MODULES:-}" \
		${DOCKER_RUN_ARGS:-} -v "$ROOT:/repo" -w /repo "alpine:$ALPINE_VERSION" /repo/scripts/compile-azerothcore.sh
fi

APP_FILES=/data/data/com.logie.warcraft/files
PREFIX="$APP_FILES/server"
SRC=/repo/build/azerothcore
BUILD=/repo/build/azerothcore-build
DIST=/repo/build/azerothcore-dist
JOBS="${JOBS:-$(nproc)}"

apk add -q --no-progress build-base cmake samurai git ccache boost-dev openssl-dev \
	mariadb-connector-c-dev readline-dev bzip2-dev zlib-dev linux-headers
export CCACHE_DIR=/repo/build/ccache CCACHE_MAXSIZE=2G
# The core and its scripts are built with precompiled headers, which ccache only caches with these
# settings (ccache's manual, "Precompiled headers"); without them each of those files is compiled
# again every time.
export CCACHE_SLOPPINESS=pch_defines,time_macros,include_file_mtime,include_file_ctime
git config --global --add safe.directory '*'

[ "${FETCH:-1}" = 0 ] || sh /repo/scripts/fetch-azerothcore.sh "$SRC"

# musl gives new threads a 128 KiB stack unless the program asks for more; glibc gives 8 MiB.
# AzerothCore's own jemalloc is configured for glibc (NOJEM): the world server gets Alpine's
# instead, preloaded by ctl.sh, since musl's malloc is slow for a server's many threads.
cmake -S "$SRC" -B "$BUILD" -G Ninja \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX="$PREFIX" \
	-DCONF_DIR="$APP_FILES/etc" \
	-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,-z,stack-size=8388608" \
	-DAPPS_BUILD=all -DTOOLS_BUILD=all -DSCRIPTS=static -DMODULES=static -DNOJEM=1 \
	-DWITH_WARNINGS=0 -DUSE_COREPCH=1 -DUSE_SCRIPTPCH=1 > "$BUILD.cmake.log" 2>&1 ||
	{ tail -50 "$BUILD.cmake.log"; exit 1; }
grep -E "^\s*\+- mod-|Modules" "$BUILD.cmake.log" || true
ccache -z > /dev/null
# shellcheck disable=SC2086
ninja -C "$BUILD" -j "$JOBS" ${NINJA_ARGS:-}
ccache -s

# The programs and their configs, installed for the phone's paths, then the SQL: the core's, and
# each module's wherever it keeps it (data/sql, sql/<database>, the progression brackets'), and the
# files a module makes the game's patch from (data/client: mod-skyborne's).
rm -rf "$DIST" "$DIST.install"
DESTDIR="$DIST.install" ninja -C "$BUILD" install > /dev/null
mkdir -p "$DIST/bin" "$DIST/etc/modules" "$DIST/modules"
for prog in worldserver authserver dbimport map_extractor vmap4_extractor vmap4_assembler mmaps_generator; do
	cp "$DIST.install$PREFIX/bin/$prog" "$DIST/bin/"
done
cp "$DIST.install$APP_FILES"/etc/*.conf.dist "$DIST/etc/"
cp "$DIST.install$APP_FILES"/etc/modules/*.conf.dist "$DIST/etc/modules/"
# ALE's (mod-ale, the Lua engine) own scripts.
[ ! -d "$DIST.install$PREFIX/bin/lua_scripts" ] || cp -r "$DIST.install$PREFIX/bin/lua_scripts" "$DIST/lua_scripts"
rm -rf "$DIST.install"
strip "$DIST"/bin/*
cp "$SRC/src/tools/mmaps_generator/mmaps-config.yaml" "$DIST/etc/"
cp -r "$SRC/data/sql" "$DIST/sql"
# Only base, updates and custom are read: the archive (ArchivedRedundancy is off), the old
# releases' updates and the create scripts aren't, and come to 500 MB.
rm -rf "$DIST/sql/archive" "$DIST/sql/create" "$DIST/sql/old"
for dir in "$SRC"/modules/*/; do
	dir=${dir%/}
	name=$(basename "$dir")
	# (data/patch: a module's files for the game, mod-worgoblin's: package-azerothcore.sh makes the
	# game's patch's files from them; data/server: SQL a module runs itself, mod-worgen-goblin's;
	# data/zones: its starting areas' rows for the game's tables and the world's)
	for sql in "$dir"/data/sql "$dir"/data/client "$dir"/data/server "$dir"/data/zones "$dir"/data/patch "$dir"/sql "$dir"/src/Bracket_*/sql; do
		[ -d "$sql" ] || continue
		rel=${sql#"$dir/"}
		mkdir -p "$DIST/modules/$name/$(dirname "$rel")"
		cp -r "$sql" "$DIST/modules/$name/$rel"
	done
done
git -C "$SRC" rev-parse HEAD > "$DIST/merged"
du -sh "$DIST"
