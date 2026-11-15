#!/bin/sh
# Compiles Karrz's WoW Forever server (TrinityCore, branch forever-bots, PlayerbotV2) for Linux arm64 on musl
# (Alpine), the same loader/sysroot approach as the other realms (scripts/compile-azerothcore.sh): the programs
# are run through musl's loader from the app's own folder, so no path is compiled in (EMBED_BUILD_PATHS=0).
# Leaves what scripts/package-forever-new.sh packs in build/forever-new-dist.
#
# Source: the PINNED commit of https://github.com/Karrz1/TrinityCore (warcraft/forever-new/forever-version.env), never HEAD,
# never the bots repository's partial copy. CMake must print "Playerbot V2 module enabled" and "AddSC_playerbot_v2".
# DOCKER_RUN_ARGS adds arguments to `docker run`. FETCH=0 compiles build/forever-new as it is.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../warcraft/forever-new/forever-version.env
. "$ROOT/warcraft/forever-new/forever-version.env"

if [ -z "${IN_ALPINE:-}" ]; then
	mkdir -p "$ROOT/build"
	# shellcheck disable=SC2086
	exec docker run --rm -e IN_ALPINE=1 -e JOBS="${JOBS:-}" -e FETCH="${FETCH:-1}" ${DOCKER_RUN_ARGS:-} \
		-v "$ROOT:/repo" -w /repo "alpine:$ALPINE_VERSION" /repo/scripts/compile-forever-new.sh
fi

SRC=/repo/build/forever-new
BUILD=/repo/build/forever-new-build
DIST=/repo/build/forever-new-dist
JOBS="${JOBS:-$(nproc)}"

apk add -q --no-progress build-base cmake samurai git ccache boost-dev openssl-dev mariadb-connector-c-dev \
	readline-dev bzip2-dev zlib-dev linux-headers python3 xz
export CCACHE_DIR=/repo/build/ccache-forever CCACHE_MAXSIZE=2G
export CCACHE_SLOPPINESS=pch_defines,time_macros,include_file_mtime,include_file_ctime
git config --global --add safe.directory '*'

if [ "${FETCH:-1}" != 0 ]; then
	rm -rf "$SRC"
	git clone -q --branch "$CORE_BRANCH" --single-branch "$CORE_REPO" "$SRC"
	git -C "$SRC" checkout -q "$CORE_COMMIT"
	git -C "$SRC" submodule update --init --recursive
fi
[ "$(git -C "$SRC" rev-parse HEAD)" = "$CORE_COMMIT" ] || { echo "Source is not at the pinned commit $CORE_COMMIT" >&2; exit 1; }

# gSOAP (the world server's remote-access dependency) picks glibc's GNU variants of gethostbyname_r and strerror_r unless the
# POSIX ones are asked for; musl has only the POSIX ones. Asked for here, for that one library, at build time (the source stays as pinned).
if ! grep -q "forever-musl" "$SRC/dep/gsoap/CMakeLists.txt"; then
	printf '\n# forever-musl: musl has the POSIX gethostbyname_r and strerror_r only\ntarget_compile_definitions(gsoap PRIVATE _POSIX_C_SOURCE=200809L WITH_POSIX_STRERROR_R)\n' >> "$SRC/dep/gsoap/CMakeLists.txt"
fi

# musl gives a new thread a 128 KiB stack unless the program asks for more (glibc: 8 MiB).
cmake -S "$SRC" -B "$BUILD" -G Ninja \
	-DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/forever \
	-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
	-DCMAKE_EXE_LINKER_FLAGS="-Wl,-z,stack-size=8388608" \
	-DSERVERS=1 -DTOOLS=1 -DSCRIPTS=static -DBUILD_PLAYERBOT_V2=1 -DEMBED_BUILD_PATHS=0 \
	-DWITH_WARNINGS=0 -DUSE_COREPCH=1 -DUSE_SCRIPTPCH=1 > "$BUILD.cmake.log" 2>&1 || { tail -60 "$BUILD.cmake.log"; exit 1; }
grep -q "Playerbot V2 module enabled" "$BUILD.cmake.log" || { echo "CMake did not enable Playerbot V2" >&2; tail -30 "$BUILD.cmake.log"; exit 1; }
grep -q "AddSC_playerbot_v2" "$BUILD.cmake.log" || { echo "Modules: AddSC_playerbot_v2 missing from CMake output" >&2; exit 1; }
grep -E "Playerbot V2|Modules:" "$BUILD.cmake.log" || true

ccache -z > /dev/null
# -k 0: every failing file is reported in one run, not only the first.
if ! ninja -C "$BUILD" -k 0 -j "$JOBS" bnetserver worldserver mapextractor vmap4extractor vmap4assembler mmaps_generator > "$BUILD.ninja.log" 2>&1; then
	echo "=== compile errors ==="
	grep -E "^FAILED:|error:|undefined reference|cannot find" "$BUILD.ninja.log" | cut -c1-400 | head -80
	exit 1
fi
tail -3 "$BUILD.ninja.log"
ccache -s

rm -rf "$DIST"
mkdir -p "$DIST/bin" "$DIST/etc"
for prog in bnetserver worldserver mapextractor vmap4extractor vmap4assembler mmaps_generator; do
	f=$(find "$BUILD" -type f -name "$prog" -perm -u+x | head -1)
	[ -n "$f" ] || { echo "$prog was not built" >&2; exit 1; }
	cp "$f" "$DIST/bin/"
done
strip "$DIST"/bin/*
cp "$SRC/src/server/bnetserver/bnetserver.conf.dist" "$SRC/src/server/worldserver/worldserver.conf.dist" "$DIST/etc/"
mkdir -p "$DIST/etc/worldserver.conf.d"
cp "$SRC"/src/modules/PlayerbotV2/conf/playerbot.conf.dist "$SRC"/src/modules/PlayerbotV2/conf/zz-0-playerbot-defaults.conf \
	"$SRC"/src/modules/PlayerbotV2/conf/zz-forever-bots.conf "$DIST/etc/worldserver.conf.d/"
# SQL the servers apply themselves (SourceDirectory): base, updates, custom, the bots'. NOT sql/old (4 GB, never read).
mkdir -p "$DIST/sql"
for d in base updates custom create playerbot_shared playerbot_v2; do cp -r "$SRC/sql/$d" "$DIST/sql/$d"; done
mkdir -p "$DIST/legal"
cp "$SRC/COPYING" "$SRC/NOTICE.md" "$DIST/legal/"
cp "$SRC/src/modules/PlayerbotV2/NOTICE.md" "$DIST/legal/PlayerbotV2-NOTICE.md" 2>/dev/null || true
cp -r "$SRC/src/modules/PlayerbotV2/Addon/ForeverBots" "$DIST/ForeverBots-addon-source"
mmaps_cfg=$(find "$SRC/src/tools/mmaps_generator" -name '*.yaml' -o -name '*.conf*' | head -1)
[ -z "$mmaps_cfg" ] || cp "$mmaps_cfg" "$DIST/etc/"
git -C "$SRC" rev-parse HEAD > "$DIST/SOURCE_COMMIT"
du -sh "$DIST"
