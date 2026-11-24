#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ndk=${ANDROID_NDK_ROOT:?Set ANDROID_NDK_ROOT to the Android NDK}
revision=8e657bf29679a73e9ff2968600d8fd6353779824
source_dir="$PWD/build/pcsx-rearmed"
output="$PWD/app/ps1/jniLibs"
mkdir -p "$source_dir" "$output/arm64-v8a"
if [[ ! -d "$source_dir/.git" ]]; then
    git -C "$source_dir" init -q
    git -C "$source_dir" remote add origin https://github.com/notaz/pcsx_rearmed.git
fi
if ! git -C "$source_dir" cat-file -e "$revision^{commit}" 2>/dev/null; then
    git -C "$source_dir" fetch --depth 1 origin "$revision"
fi
git -C "$source_dir" checkout --detach "$revision"
git -C "$source_dir" submodule update --init --depth 1 deps/libchdr deps/libretro-common deps/lightning deps/lightrec
"$ndk/ndk-build" -C "$source_dir" APP_BUILD_SCRIPT="$source_dir/jni/Android.mk" APP_ABI=arm64-v8a APP_PLATFORM=android-26 \
    NDK_LIBS_OUT="$output" -j "$(getconf _NPROCESSORS_ONLN)"
"$ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang" \
    -shared -fPIC -O2 -Wall -Wextra -Werror -Wl,-z,max-page-size=16384 -Wl,--no-undefined \
    -I "$source_dir/deps/libretro-common/include" ps1/blizz_ps1.c \
    -L "$output/arm64-v8a" -lretro -o "$output/arm64-v8a/libblizz_ps1.so"
