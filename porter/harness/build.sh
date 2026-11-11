#!/usr/bin/env bash
# Builds the desktop harness that draws the character porter's preview off-screen (EGL, OpenGL ES 3 from Mesa). The headers
# are the NDK's (this machine has Mesa's libraries without their headers). Output: build/porter-harness/harness
# (or the folder given).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="${1:-$here/../../build/porter-harness}"
ndk="${ANDROID_NDK_HOME:-$(ls -d "${ANDROID_HOME:-/opt/android-sdk}"/ndk/* | tail -1)}"
include="$ndk/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/include"
mkdir -p "$out/include"
cp -r "$include/EGL" "$include/GLES2" "$include/GLES3" "$include/KHR" "$out/include/"
g++ -std=c++17 -O2 -Wall -Wno-unused-parameter -DEGL_NO_X11 -DMESA_EGL_NO_X11_HEADERS -I"$out/include" -I"$here/../engine" \
    "$here/harness.cpp" "$here"/../engine/bytes.cpp "$here"/../engine/blp.cpp "$here"/../engine/m2.cpp "$here"/../engine/viewer.cpp -l:libEGL.so.1 -l:libGLESv2.so.2 -o "$out/harness"
echo "$out/harness"
