#!/bin/sh
# Builds WarcraftXL's own patcher code (WarcraftXL-Labs/core src/patcher/PeImage.cpp at WRATHPP's pinned core, with
# windows.h here standing in for the PE structures) natively, and patches IN into OUT the way wxl-core-patcher does:
# the reference the app's Kotlin patcher (WxlPatcher.kt, WxlPatcherTest) is held to.
#   run.sh CORE_CHECKOUT IN OUT
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
OUTDIR="$(mktemp -d)"
trap 'rm -rf "$OUTDIR"' EXIT
mkdir -p "$OUTDIR/inc/patcher"
cp "$HERE/windows.h" "$OUTDIR/inc/"
cp "$1/src/patcher/PeImage.hpp" "$OUTDIR/inc/patcher/"
c++ -std=c++20 -O1 -I"$OUTDIR/inc" -include windows.h -o "$OUTDIR/ref" "$HERE/ref.cpp" "$1/src/patcher/PeImage.cpp"
"$OUTDIR/ref" "$2" "$3"
sha256sum "$3"
