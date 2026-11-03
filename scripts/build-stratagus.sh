#!/bin/sh
# Builds Warcraft I and II for Blizzard, native on Android (arm64): the Stratagus engine
# (stratagus.env) as SDL's libmain.so, War1gus's and Wargus's data tools as programs (shipped as
# libwar1tool.so and libwartool.so, which Android lets the app run), SDL's Java activity, and the
# two games' scripts. innoextract is not built here: scripts/build-tools.sh makes it (libinnoextract.so).
# Into app/stratagus (git-ignored):
#
#   jniLibs/arm64-v8a/   libmain.so libwartool.so libwar1tool.so
#   java/                org/libsdl/app/*.java (SDL's, for the engine's screen)
#   assets/stratagus/    war1gus.zip wargus.zip VERSION (scripts, campaigns, maps, contrib, shaders)
#
# STRATAGUS_WORK is where to keep the sources and builds (default build/stratagus-android).
# ANDROID_NDK_ROOT, else $ANDROID_HOME/ndk/<STRATAGUS_NDK>, is the NDK.
#
# --placeholders: builds nothing. Makes tiny dummy files with the real names (a few bytes each; the
# zips are valid empty zips) so Gradle configuration and compilation pass on a machine without
# the NDK. They are NOT the engine: never ship an APK built from them.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../stratagus.env
. "$ROOT/stratagus.env"
WORK="${STRATAGUS_WORK:-$ROOT/build/stratagus-android}"
NDK="${ANDROID_NDK_ROOT:-${ANDROID_HOME:-/opt/android-sdk}/ndk/$STRATAGUS_NDK}"
OUT="$ROOT/app/stratagus"
JOBS="$(nproc 2> /dev/null || echo 4)"

if [ "${1:-}" = "--placeholders" ]; then
	rm -rf "$OUT"
	mkdir -p "$OUT/jniLibs/arm64-v8a" "$OUT/java" "$OUT/assets/stratagus"
	for lib in libmain.so libwartool.so libwar1tool.so; do
		echo "placeholder" > "$OUT/jniLibs/arm64-v8a/$lib"
	done
	# An empty zip is just the end-of-central-directory record.
	for game in war1gus wargus; do
		printf 'PK\005\006\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' > "$OUT/assets/stratagus/$game.zip"
	done
	echo "placeholders" > "$OUT/assets/stratagus/VERSION"
	echo "Placeholders in $OUT (not a real build)."
	exit 0
fi
mkdir -p "$WORK"

fetch() { # repo commit dir
	if [ ! -d "$3/.git" ]; then
		git init -q "$3"
		git -C "$3" remote add origin "$1"
	fi
	git -C "$3" remote set-url origin "$1"
	git -C "$3" cat-file -e "$2^{commit}" 2> /dev/null || git -C "$3" fetch -q --depth 1 origin "$2"
	git -C "$3" checkout -q --force "$2"
	git -C "$3" clean -qfdx
}

fetch "$STRATAGUS_REPO" "$STRATAGUS_COMMIT" "$WORK/stratagus"
git -C "$WORK/stratagus" submodule update -q --init --depth 1 --force third-party
git -C "$WORK/stratagus/third-party" clean -qfdx
fetch "$WARGUS_REPO" "$WARGUS_COMMIT" "$WORK/wargus"
fetch "$WAR1GUS_REPO" "$WAR1GUS_COMMIT" "$WORK/war1gus"

for patch in "$ROOT"/patches/stratagus/*.patch; do
	git -C "$WORK/stratagus" apply "$patch"
done
for patch in "$ROOT"/patches/stratagus-deps/*.patch; do
	git -C "$WORK/stratagus/third-party" apply "$patch"
done

# tolua++ for this machine: it writes the engine's Lua bindings during the build.
cmake -S "$WORK/stratagus/third-party/lua-5.1.5" -B "$WORK/host-lua" -DCMAKE_BUILD_TYPE=Release > /dev/null
make -C "$WORK/host-lua" -j"$JOBS" toluapp > /dev/null

android() { # source build [cmake args...]
	src="$1"; build="$2"; shift 2
	cmake -S "$src" -B "$build" -G "Unix Makefiles" \
		-DCMAKE_TOOLCHAIN_FILE="$NDK/build/cmake/android.toolchain.cmake" \
		-DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=26 -DANDROID_STL=c++_static \
		-DCMAKE_BUILD_TYPE=Release "$@" > "$build.cmake.log"
}

mkdir -p "$WORK/engine" "$WORK/tools"
android "$WORK/stratagus" "$WORK/engine" \
	-DBUILD_VENDORED_LUA=ON -DBUILD_VENDORED_SDL=ON -DBUILD_VENDORED_MEDIA_LIBS=ON \
	-DSTRATAGUS_HOST_TOLUAPP="$WORK/host-lua/toluapp" \
	-DWITH_STACKTRACE=OFF -DWITH_OPENMP=OFF -DBUILD_TESTING=OFF -DENABLE_USEGAMEDIR=ON
make -C "$WORK/engine" -j"$JOBS" stratagus > "$WORK/engine.make.log" || { tail -40 "$WORK/engine.make.log"; exit 1; }

android "$ROOT/patches/stratagus/tools" "$WORK/tools" \
	-DSTRATAGUS_SRC="$WORK/stratagus" -DSTRATAGUS_BUILD="$WORK/engine" \
	-DSTRATAGUS_INCLUDE_DIR="$WORK/stratagus/gameheaders" \
	-DWARGUS_SRC="$WORK/wargus" -DWAR1GUS_SRC="$WORK/war1gus" -DSTORM_SKIP_INSTALL=ON \
	-DZLIB_INCLUDE_DIR="$WORK/engine/zlib/src/zlib-build" -DZLIB_LIBRARY="$WORK/engine/zlib/src/zlib-build/libz.a" \
	-DBZIP2_INCLUDE_DIR="$WORK/stratagus/third-party/bzip2" -DBZIP2_LIBRARIES="$WORK/engine/bzip2/src/bzip2-build/libbz2.a"
make -C "$WORK/tools" -j"$JOBS" wartool war1tool > "$WORK/tools.make.log" || { tail -40 "$WORK/tools.make.log"; exit 1; }

strip="$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip"
rm -rf "$OUT"
mkdir -p "$OUT/jniLibs/arm64-v8a" "$OUT/java" "$OUT/assets/stratagus"
"$strip" -o "$OUT/jniLibs/arm64-v8a/libmain.so" "$WORK/engine/libmain.so"
"$strip" -o "$OUT/jniLibs/arm64-v8a/libwartool.so" "$WORK/tools/wartool"
"$strip" -o "$OUT/jniLibs/arm64-v8a/libwar1tool.so" "$WORK/tools/war1tool"
cp -r "$WORK/stratagus/third-party/SDL/android-project/app/src/main/java/org" "$OUT/java/"

# The games' own files, which the tools' data goes beside.
for game in war1gus wargus; do
	(cd "$WORK/$game" && zip -qr -X "$OUT/assets/stratagus/$game.zip" scripts campaigns maps contrib shaders)
done

{
	echo "stratagus $STRATAGUS_COMMIT"
	echo "wargus $WARGUS_COMMIT"
	echo "war1gus $WAR1GUS_COMMIT"
} > "$OUT/assets/stratagus/VERSION"
ls -la "$OUT/jniLibs/arm64-v8a" "$OUT/assets/stratagus"
