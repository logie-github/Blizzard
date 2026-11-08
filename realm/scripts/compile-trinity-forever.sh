#!/bin/sh
# Compiles the Forever realm for the phone, Linux arm64 on musl (Alpine): TrinityCore's "forever" branch
# (forever/server-version.env, with the app's patches) with its scripts compiled in, its Battle.net login server and
# its data tools (the map, vmap and mmap makers). Leaves what scripts/package-trinity-forever.sh packs in
# build/trinity-forever-dist. Made after the World of Warcraft app's scripts/compile-legioncore.sh.
#
# Natively on an arm64 machine (GitHub's ubuntu-24.04-arm runner), in an Alpine container when Docker is there.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../forever/server-version.env
. "$ROOT/forever/server-version.env"

if [ -z "${IN_ALPINE:-}" ]; then
	mkdir -p "$ROOT/build"
	# shellcheck disable=SC2086
	exec docker run --rm -e IN_ALPINE=1 -e JOBS="${JOBS:-}" -e FETCH="${FETCH:-1}" ${DOCKER_RUN_ARGS:-} \
		-v "$ROOT:/repo" -w /repo "alpine:$ALPINE_VERSION" /repo/scripts/compile-trinity-forever.sh
fi
[ "$(uname -m)" = aarch64 ] || { echo "Build this on an arm64 machine (the phone's architecture)." >&2; exit 1; }

PREFIX=/data/data/com.logie.blizz/files/forever/server
SRC=/repo/build/trinity-forever
BUILD=/repo/build/trinity-forever-build
DIST=/repo/build/trinity-forever-dist
JOBS="${JOBS:-$(nproc)}"

apk add -q --no-progress cmake samurai git ccache curl perl clang20 lld20 llvm20 \
	musl-dev libstdc++-dev gcc boost-dev openssl-dev mariadb-connector-c-dev readline-dev bzip2-dev zlib-dev ncurses-dev linux-headers
export CCACHE_DIR=/repo/build/ccache-trinity-forever CCACHE_MAXSIZE=4G
export CCACHE_SLOPPINESS=pch_defines,time_macros,include_file_mtime,include_file_ctime
git config --global --add safe.directory '*'

# musl's C++ NULL is nullptr; the core's scripts pass NULL where a number is meant (as LegionCore's do).
find /usr/include -maxdepth 1 -name '*.h' -exec sed -i 's/define NULL nullptr/define NULL 0L/' {} +

TOOLCHAIN=/repo/build/trinity-forever-toolchain.cmake
cat > "$TOOLCHAIN" <<TC
set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)
set(CMAKE_EXE_LINKER_FLAGS_INIT "-fuse-ld=lld")
set(CMAKE_SHARED_LINKER_FLAGS_INIT "-fuse-ld=lld")
TC

[ "${FETCH:-1}" = 0 ] || sh /repo/scripts/fetch-trinity-forever.sh "$SRC"

# Precompiled headers ON (USE_*PCH=1): the core and its scripts rely on the PCH to pull common headers (Map.h, Spell.h,
# Util.h...) into every file; without it, clang/libc++ fails them (incomplete type Map, undeclared ByteArrayToHexStr...).
# ccache caches PCH builds with CCACHE_SLOPPINESS (set above). armv8-a, every arm64 phone. musl gives new threads 128 KiB of stack unless the program asks for more: 8 MiB.
# _LARGEFILE64_SOURCE: Alpine musl exposes stat64/lstat64 (g3dlite uses them) only with it defined.
	# -include ctime/cstdint/cstring: musl + libc++ do not pull these in transitively the way glibc does, so some
	# headers (Util.h: time_t) fail to compile; force-including them fixes it without touching the sources.
	# NOJEM: jemalloc's bundled copy clashes with musl (JEMALLOC_SYS_NOTHROW on malloc/calloc vs musl's
	# declarations); the core runs on musl's own allocator, so leave jemalloc out (dep/CMakeLists gates it on NOT NOJEM).
cmake -S "$SRC" -B "$BUILD" -G Ninja \
	-DCMAKE_TOOLCHAIN_FILE="$TOOLCHAIN" \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX="$PREFIX" \
	-DCMAKE_C_FLAGS="-march=armv8-a -D_LARGEFILE64_SOURCE" -DCMAKE_CXX_FLAGS="-march=armv8-a -D_LARGEFILE64_SOURCE -include cstdint -include ctime -include cstring" \
	-DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
	-DCMAKE_EXE_LINKER_FLAGS="-fuse-ld=lld -Wl,-z,stack-size=8388608" \
	-DSERVERS=1 -DTOOLS=1 -DSCRIPTS=static -DWITH_WARNINGS=0 -DWITHOUT_GIT=1 -DUSE_COREPCH=1 -DUSE_SCRIPTPCH=1 \
	-DNOJEM=1 \
	> "$BUILD.cmake.log" 2>&1 || { tail -80 "$BUILD.cmake.log"; exit 1; }
ccache -z > /dev/null
ninja -C "$BUILD" -j "$JOBS" -k 0 > "$BUILD.ninja.log" 2>&1 || { grep -B5 -A25 -m5 "error:" "$BUILD.ninja.log" | head -250; tail -40 "$BUILD.ninja.log"; exit 1; }
ccache -s

rm -rf "$DIST" "$DIST.install"
DESTDIR="$DIST.install" ninja -C "$BUILD" install > /dev/null
mkdir -p "$DIST/bin" "$DIST/etc"
for prog in bnetserver worldserver mapextractor vmap4extractor vmap4assembler mmaps_generator; do
	found=$(find "$DIST.install" -type f -name "$prog" | head -1)
	[ -n "$found" ] || { echo "$prog wasn't built" >&2; exit 1; }
	cp "$found" "$DIST/bin/"
done
cp "$(find "$DIST.install" -name bnetserver.conf.dist | head -1)" "$(find "$DIST.install" -name worldserver.conf.dist | head -1)" "$DIST/etc/"
rm -rf "$DIST.install"
llvm-strip "$DIST"/bin/*
# The SQL: the login and characters bases, every database's updates and the branch's own (sql/custom).
mkdir -p "$DIST/sql"
cp -r "$SRC/sql/base" "$SRC/sql/updates" "$DIST/sql/"
[ ! -d "$SRC/sql/custom" ] || cp -r "$SRC/sql/custom" "$DIST/sql/"
[ ! -d "$SRC/sql/old" ] || cp -r "$SRC/sql/old" "$DIST/sql/"
echo "$TRINITY_COMMIT" > "$DIST/commit"
du -sh "$DIST"
