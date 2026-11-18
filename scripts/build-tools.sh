#!/bin/sh
# Builds the programs the importers run on the phone (tools.env) into app/tools/jniLibs/arm64-v8a
# (git-ignored): libbldl.so (blizzard-legacy-dl), libinnoextract.so and libhactool.so. Android runs programs from
# the app's native library folder, named like libraries.
#
# TOOLS_WORK is where to keep sources and builds (default build/tools).
# ANDROID_NDK_ROOT, else $ANDROID_HOME/ndk/<TOOLS_NDK>, is the NDK.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../tools.env
. "$ROOT/tools.env"
WORK="${TOOLS_WORK:-$ROOT/build/tools}"
NDK="${ANDROID_NDK_ROOT:-${ANDROID_HOME:-/opt/android-sdk}/ndk/$TOOLS_NDK}"
OUT="$ROOT/app/tools/jniLibs/arm64-v8a"
JOBS="$(nproc 2> /dev/null || echo 4)"
mkdir -p "$WORK" "$OUT"

fetch() { # repo commit dir
	if [ ! -d "$3/.git" ]; then
		git init -q "$3"
		git -C "$3" remote add origin "$1"
	fi
	git -C "$3" cat-file -e "$2^{commit}" 2> /dev/null || git -C "$3" fetch -q --depth 1 origin "$2"
	git -C "$3" checkout -q --force "$2"
	git -C "$3" clean -qfdx
}
download() { # url sha256 file
	if [ ! -f "$3" ] || ! echo "$2  $3" | sha256sum -c - > /dev/null 2>&1; then
		curl -fsSL -o "$3" "$1"
		echo "$2  $3" | sha256sum -c - > /dev/null || { echo "$3: wrong SHA-256" >&2; exit 1; }
	fi
}

# blizzard-legacy-dl ---------------------------------------------------------------------------
download "$ZIG_URL" "$ZIG_SHA256" "$WORK/zig.tar.xz"
if [ ! -x "$WORK/zig/zig" ]; then
	mkdir -p "$WORK/zig"
	tar -xJf "$WORK/zig.tar.xz" -C "$WORK/zig" --strip-components 1
fi
fetch "$BLDL_REPO" "$BLDL_COMMIT" "$WORK/bldl"
for patch in "$ROOT"/patches/blizzard-legacy-dl/*.patch; do
	git -C "$WORK/bldl" apply "$patch"
done
fetch "$LIBD2_REPO" "$LIBD2_COMMIT" "$WORK/libd2"
sed -i "s#\.url = \"git+https://github.com/jaenster/libd2[^\"]*\",#.path = \"../libd2\",#; /\.hash = \"libd2-/d" "$WORK/bldl/build.zig.zon"
grep -q "\.path = \"../libd2\"" "$WORK/bldl/build.zig.zon" || { echo "build.zig.zon: libd2 not pointed at ../libd2" >&2; exit 1; }
(
	cd "$WORK/bldl"
	"$WORK/zig/zig" build -Doptimize=ReleaseSafe -Dtarget=aarch64-linux-musl -Dpie=true --prefix "$WORK/bldl-out" 2> "$WORK/bldl.log"
) || { tail -40 "$WORK/bldl.log"; exit 1; }
"$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip" -o "$OUT/libbldl.so" "$WORK/bldl-out/bin/blizzard-legacy-dl"

# borderless.exe (tools/borderless/borderless.c): the session keeper every Windows game is started through. It makes
# the games' desktop the one that takes the mouse, takes a windowed game's title bar and frame away (the picture is
# then the whole screen) and ends the session with the game. Built with the same Zig for x86_64 Windows, the Windows
# subsystem (no console), into app/tools/assets, which the app packages.
ASSETS="$ROOT/app/tools/assets"
mkdir -p "$ASSETS"
"$WORK/zig/zig" cc -target x86_64-windows-gnu -O2 -s -Wl,--subsystem,windows "$ROOT/tools/borderless/borderless.c" -luser32 -lkernel32 -o "$ASSETS/borderless.exe" 2> "$WORK/borderless.log" ||
	{ tail -40 "$WORK/borderless.log"; exit 1; }

# innoextract ----------------------------------------------------------------------------------
android() { # source build [cmake args...]
	src="$1"; build="$2"; shift 2
	cmake -S "$src" -B "$build" -G "Unix Makefiles" \
		-DCMAKE_TOOLCHAIN_FILE="$NDK/build/cmake/android.toolchain.cmake" \
		-DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=26 -DANDROID_STL=c++_static \
		-DCMAKE_BUILD_TYPE=Release "$@" > "$build.cmake.log"
}
TOOLCHAIN="$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin"
CC="$TOOLCHAIN/aarch64-linux-android26-clang"
PREFIX="$WORK/prefix"
rm -rf "$PREFIX" "$WORK/zlib" "$WORK/bzip2" "$WORK/xz" "$WORK/boost"
mkdir -p "$PREFIX/include" "$PREFIX/lib" "$WORK/zlib" "$WORK/bzip2" "$WORK/xz" "$WORK/boost"
download "$ZLIB_URL" "$ZLIB_SHA256" "$WORK/zlib.tar.gz"
download "$BZIP2_URL" "$BZIP2_SHA256" "$WORK/bzip2.tar.gz"
download "$XZ_URL" "$XZ_SHA256" "$WORK/xz.tar.gz"
download "$BOOST_URL" "$BOOST_SHA256" "$WORK/boost.tar.bz2"
tar -xzf "$WORK/zlib.tar.gz" -C "$WORK/zlib" --strip-components 1
tar -xzf "$WORK/bzip2.tar.gz" -C "$WORK/bzip2" --strip-components 1
tar -xzf "$WORK/xz.tar.gz" -C "$WORK/xz" --strip-components 1
tar -xjf "$WORK/boost.tar.bz2" -C "$WORK/boost" --strip-components 1

(cd "$WORK/zlib" && CC="$CC" CFLAGS="-O2 -fPIC" ./configure --static --prefix="$PREFIX" > "$WORK/zlib.log" && make -j"$JOBS" install >> "$WORK/zlib.log") ||
	{ tail -40 "$WORK/zlib.log"; exit 1; }
(cd "$WORK/bzip2" && make -j"$JOBS" libbz2.a CC="$CC" AR="$TOOLCHAIN/llvm-ar" RANLIB="$TOOLCHAIN/llvm-ranlib" CFLAGS="-O2 -fPIC -D_FILE_OFFSET_BITS=64" > "$WORK/bzip2.log" &&
	cp libbz2.a "$PREFIX/lib/" && cp bzlib.h "$PREFIX/include/") || { tail -40 "$WORK/bzip2.log"; exit 1; }
android "$WORK/xz" "$WORK/xz-build" -DBUILD_SHARED_LIBS=OFF -DXZ_NLS=OFF -DXZ_DOC=OFF \
	-DXZ_TOOL_XZ=OFF -DXZ_TOOL_XZDEC=OFF -DXZ_TOOL_LZMADEC=OFF -DXZ_TOOL_LZMAINFO=OFF -DXZ_TOOL_SCRIPTS=OFF \
	-DCMAKE_INSTALL_PREFIX="$PREFIX"
make -C "$WORK/xz-build" -j"$JOBS" install > "$WORK/xz.make.log" || { tail -40 "$WORK/xz.make.log"; exit 1; }
(
	cd "$WORK/boost"
	./bootstrap.sh --with-libraries=filesystem,iostreams,program_options,system,date_time > "$WORK/boost.bootstrap.log"
	echo "using clang : android : $TOOLCHAIN/aarch64-linux-android26-clang++ : <archiver>$TOOLCHAIN/llvm-ar <ranlib>$TOOLCHAIN/llvm-ranlib <cxxflags>-fPIC <cflags>-fPIC ;" > android-config.jam
	./b2 -j"$JOBS" --user-config=android-config.jam toolset=clang-android target-os=android \
		architecture=arm address-model=64 binary-format=elf abi=aapcs link=static runtime-link=static \
		threading=multi variant=release cxxstd=17 \
		--with-filesystem --with-iostreams --with-program_options --with-system --with-date_time \
		-sNO_LZMA=1 -sNO_ZSTD=1 -sZLIB_INCLUDE="$PREFIX/include" -sZLIB_LIBRARY_PATH="$PREFIX/lib" -sZLIB_NAME=z \
		-sBZIP2_INCLUDE="$PREFIX/include" -sBZIP2_LIBRARY_PATH="$PREFIX/lib" -sBZIP2_NAME=bz2 \
		--prefix="$PREFIX" install > "$WORK/boost.b2.log"
) || { tail -40 "$WORK/boost.b2.log"; exit 1; }
fetch "$INNOEXTRACT_REPO" "$INNOEXTRACT_COMMIT" "$WORK/innoextract"
android "$WORK/innoextract" "$WORK/innoextract-build" \
	-DUSE_STATIC_LIBS=ON -DWITH_CONV=builtin -DBUILD_TESTS=OFF \
	-DCMAKE_FIND_ROOT_PATH="$PREFIX" -DBoost_ROOT="$PREFIX" -DBoost_NO_SYSTEM_PATHS=ON \
	-DBoost_USE_STATIC_RUNTIME=ON \
	-DLZMA_INCLUDE_DIR="$PREFIX/include" -DLZMA_LIBRARY="$PREFIX/lib/liblzma.a" \
	-DZLIB_INCLUDE_DIR="$PREFIX/include" -DZLIB_LIBRARY="$PREFIX/lib/libz.a" \
	-DBZIP2_INCLUDE_DIR="$PREFIX/include" -DBZIP2_LIBRARIES="$PREFIX/lib/libbz2.a" -DBZIP2_LIBRARY="$PREFIX/lib/libbz2.a" \
	"-DCMAKE_EXE_LINKER_FLAGS=-L$PREFIX/lib"
make -C "$WORK/innoextract-build" -j"$JOBS" innoextract > "$WORK/innoextract.make.log" || { tail -40 "$WORK/innoextract.make.log"; exit 1; }
"$TOOLCHAIN/llvm-strip" -o "$OUT/libinnoextract.so" "$WORK/innoextract-build/innoextract"

# hactool ---------------------------------------------------------------------------------------
fetch "$HACTOOL_REPO" "$HACTOOL_COMMIT" "$WORK/hactool"
(
	cd "$WORK/hactool"
	# Its --basenca-less fake base file bumps a FILE pointer to make it non-NULL, which Android's libc (FILE is opaque)
	# doesn't compile; the same, written as a cast.
	sed -i 's|nca_ctx.tool_ctx->base_file++;|nca_ctx.tool_ctx->base_file = (FILE *)1;|' main.c
	grep -q 'base_file = (FILE \*)1;' main.c || { echo "hactool main.c: base_file patch didn't apply" > "$WORK/hactool.log"; exit 1; }
	# Its Makefile builds the vendored mbedtls and then its own sources; the same files, in one command.
	"$CC" -O2 -w -fPIE -pie -D_BSD_SOURCE -D_POSIX_SOURCE -D_POSIX_C_SOURCE=200112L -D_DEFAULT_SOURCE -D_FILE_OFFSET_BITS=64 \
		-I mbedtls/include ./*.c mbedtls/library/*.c -o hactool > "$WORK/hactool.log" 2>&1
) || { tail -40 "$WORK/hactool.log"; exit 1; }
"$TOOLCHAIN/llvm-strip" -o "$OUT/libhactool.so" "$WORK/hactool/hactool"

# blizzmaria: the mariadb client dbimport and the world server start, a freestanding program with no libc (see its source) -----
"$CC" -O2 -static -nostdlib -ffreestanding -fno-stack-protector -fno-pic -fno-pie -Wl,--build-id=none \
	-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384 -o "$WORK/blizzmaria" "$ROOT/tools/blizzmaria.c" || { echo "blizzmaria.c didn't build" >&2; exit 1; }
"$TOOLCHAIN/llvm-strip" -o "$OUT/libblizzmaria.so" "$WORK/blizzmaria"

{
	echo "blizzard-legacy-dl $BLDL_COMMIT"
	echo "innoextract $INNOEXTRACT_COMMIT"
	echo "hactool $HACTOOL_COMMIT"
} > "$ROOT/app/tools/VERSION"
ls -la "$OUT"
