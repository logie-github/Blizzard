#!/bin/sh
# Builds the desktop check of the movie decoding (harness.c) against FFmpeg built for this machine
# (scripts/build-ffmpeg.sh --host), into build/movie-harness.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FF="$ROOT/build/ffmpeg-host"
[ -f "$FF/lib/libavcodec.a" ] || "$ROOT/scripts/build-ffmpeg.sh" --host
mkdir -p "$ROOT/build"
cc -O2 -Wall -Wextra -I"$FF/include" "$ROOT/movie/player.c" "$ROOT/movie/harness.c" -o "$ROOT/build/movie-harness" \
	"$FF/lib/libavformat.a" "$FF/lib/libavcodec.a" "$FF/lib/libswscale.a" "$FF/lib/libswresample.a" "$FF/lib/libavutil.a" \
	-lm -lpthread
echo "built $ROOT/build/movie-harness"
