#!/bin/sh
# Builds the Box64 that local realms' sessions run (box64-version.env): Box64 at
# BOX64_COMMIT with patches/box64/ applied, for arm64 (the runtime's glibc), as Winlator
# packs its own: OUT_DIR/box64-BOX64_LEGION_VERSION.tzst, holding ./usr/local/bin/box64, its
# loader at Winlator's install path (scripts/prepare-winlator.sh rewrites it for this app).
#
# Needs aarch64-linux-gnu-gcc, cmake, patchelf and zstd. BOX64_SRC is where to keep the checkout
# (default build/box64-src).
#
# usage: scripts/build-box64.sh OUT_DIR
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../box64-version.env
. "$ROOT/box64-version.env"
# shellcheck source=../winlator-version.env
. "$ROOT/winlator-version.env"
OUT_DIR="$1"
SRC="${BOX64_SRC:-$ROOT/build/box64-src}"

if [ ! -d "$SRC/.git" ]; then
	git init -q "$SRC"
	git -C "$SRC" remote add origin "$BOX64_REPO"
fi
git -C "$SRC" cat-file -e "$BOX64_COMMIT^{commit}" 2> /dev/null ||
	git -C "$SRC" fetch -q --depth 1 origin "$BOX64_COMMIT"
git -C "$SRC" checkout -q --force "$BOX64_COMMIT"
git -C "$SRC" clean -qfdx
set -- "$ROOT"/patches/box64/*.patch
if [ -f "$1" ]; then
	git -C "$SRC" -c user.name=blizz -c user.email=blizz@users.noreply.github.com am -q "$@"
fi

build="$SRC/build"
mkdir -p "$build"
# (its output in the build folder; the end of it shown when it fails)
(
	cd "$build"
	cmake .. -DARM64=1 -DARM_DYNAREC=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo \
		-DCMAKE_SYSTEM_NAME=Linux -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
		-DCMAKE_C_COMPILER=aarch64-linux-gnu-gcc -DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++ > cmake.log 2>&1 ||
		{ tail -40 cmake.log >&2; exit 1; }
	make -j"$(nproc)" box64 > make.log 2>&1 || { grep -B5 -A5 -m 20 'error' make.log >&2; tail -20 make.log >&2; exit 1; }
)

stage="$build/package"
rm -rf "$stage"
mkdir -p "$stage/usr/local/bin"
cp "$build/box64" "$stage/usr/local/bin/box64"
aarch64-linux-gnu-strip "$stage/usr/local/bin/box64"
patchelf --set-interpreter "$WINLATOR_ROOTFS_PATH/lib/ld-linux-aarch64.so.1" "$stage/usr/local/bin/box64"
mkdir -p "$OUT_DIR"
tar -C "$stage" --owner=0 --group=0 -cf - ./usr | zstd -q -19 -f -o "$OUT_DIR/box64-$BOX64_LEGION_VERSION.tzst"
echo "Box64 $BOX64_LEGION_VERSION ($(git -C "$SRC" rev-parse --short HEAD)) in $OUT_DIR"
