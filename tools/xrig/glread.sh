#!/bin/sh
# Builds glread (the phone's look at a game's frame, on this machine's OpenGL ES: glread.c) and runs it on every
# <name>.png in a folder of the game's frames, leaving <name>.rgba beside each: the frame as the app's drawing thread
# reads it out of Winlator's texture. Wc3ScreenTest then reads the game's state from those as the phone would
# (BLIZZ_WC3_FRAMES=<the folder>). The EGL and OpenGL ES headers are the NDK's; the libraries this machine's Mesa.
#
#   tools/xrig/glread.sh <frames dir> [<work dir>]
set -e
here=$(cd "$(dirname "$0")" && pwd)
frames=${1:?the folder of the game\'s frames}
work=${2:-${TMPDIR:-/tmp}/glread}
ndk=${ANDROID_NDK_HOME:-$(ls -d "${ANDROID_HOME:-/opt/android-sdk}"/ndk/* | tail -1)}
include=$ndk/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/include
mkdir -p "$work/include"
cp -r "$include/EGL" "$include/GLES2" "$include/KHR" "$work/include/"
cc -O1 -Wall -DEGL_NO_X11 -DMESA_EGL_NO_X11_HEADERS -I"$work/include" -o "$work/glread" "$here/glread.c" -l:libEGL.so.1 -l:libGLESv2.so.2 -lm
for png in "$frames"/*.png; do
    size=$(python3 -I -c 'import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
open(sys.argv[2], "wb").write(im.tobytes())
print(*im.size)' "$png" "$work/frame.rgb")
    EGL_PLATFORM=surfaceless "$work/glread" "$work/frame.rgb" $size "${png%.png}.rgba"
done
