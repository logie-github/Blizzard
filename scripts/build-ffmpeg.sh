#!/bin/sh
# FFmpeg's Bink pieces for Warcraft III's movies (the Warsmash player, movie/player.c): the bink demuxer, the bink
# video and Bink audio decoders, swscale and swresample, as static libraries. Nothing else of FFmpeg is built.
#
#   scripts/build-ffmpeg.sh          the phone's (arm64-v8a, Android 26) into app/ffmpeg/arm64-v8a (git-ignored)
#   scripts/build-ffmpeg.sh --host   this machine's (x86_64 Linux) into build/ffmpeg-host, for the desktop tests
#
# FFMPEG_WORK is where to keep the source and the builds (default build/ffmpeg). ANDROID_NDK_ROOT, else
# $ANDROID_HOME/ndk/$FFMPEG_NDK, is the NDK. FFmpeg is LGPL 2.1: built without any GPL or non-free part.
set -eu

FFMPEG_VERSION=7.1.1
# The release tarball as ffmpeg.org signs it (checked against FFmpeg's release key FCF986EA15E6E293A5644F10B4322F04D67658D8).
FFMPEG_SHA256=733984395e0dbbe5c046abda2dc49a5544e7e0e1e2366bba849222ae9e3a03b1
FFMPEG_NDK=24.0.8215888

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${FFMPEG_WORK:-$ROOT/build/ffmpeg}"
JOBS="$(nproc 2> /dev/null || echo 4)"
HOST=0
[ "${1:-}" = "--host" ] && HOST=1
mkdir -p "$WORK"

ARCHIVE="$WORK/ffmpeg-$FFMPEG_VERSION.tar.xz"
if [ ! -f "$ARCHIVE" ] || ! echo "$FFMPEG_SHA256  $ARCHIVE" | sha256sum -c - > /dev/null 2>&1; then
	curl -fsSL --retry 3 --connect-timeout 30 -o "$ARCHIVE.part" "https://ffmpeg.org/releases/ffmpeg-$FFMPEG_VERSION.tar.xz"
	mv "$ARCHIVE.part" "$ARCHIVE"
fi
echo "$FFMPEG_SHA256  $ARCHIVE" | sha256sum -c - > /dev/null || { echo "$ARCHIVE: wrong SHA-256" >&2; exit 1; }

if [ "$HOST" = 1 ]; then
	OUT="$ROOT/build/ffmpeg-host"
	SRC="$WORK/src-host"
else
	OUT="$ROOT/app/ffmpeg/arm64-v8a"
	SRC="$WORK/src-android"
fi
STAMP="$FFMPEG_SHA256 $(sha256sum "$0" | cut -c1-64)"
if [ -f "$OUT/STAMP" ] && [ "$(cat "$OUT/STAMP")" = "$STAMP" ]; then
	echo "FFmpeg $FFMPEG_VERSION already built in $OUT"
	exit 0
fi
rm -rf "$SRC" "$OUT"
mkdir -p "$SRC"
tar -xJf "$ARCHIVE" -C "$SRC" --strip-components 1

# Only what plays a Bink file: its container, its video and audio, the picture's conversion and the sound's.
COMMON="--disable-everything --disable-programs --disable-doc --disable-network --disable-autodetect
	--disable-avdevice --disable-avfilter --disable-debug --enable-static --disable-shared --enable-pic
	--enable-avcodec --enable-avformat --enable-avutil --enable-swscale --enable-swresample
	--enable-demuxer=bink --enable-decoder=bink --enable-decoder=binkaudio_rdft --enable-decoder=binkaudio_dct
	--enable-protocol=file"

if [ "$HOST" = 1 ]; then
	# shellcheck disable=SC2086
	(cd "$SRC" && ./configure --prefix="$OUT" $COMMON --disable-x86asm) > "$WORK/configure-host.log" 2>&1 ||
		{ tail -30 "$WORK/configure-host.log"; exit 1; }
else
	NDK="${ANDROID_NDK_ROOT:-${ANDROID_HOME:-/opt/android-sdk}/ndk/$FFMPEG_NDK}"
	TC="$NDK/toolchains/llvm/prebuilt/linux-x86_64"
	# shellcheck disable=SC2086
	(cd "$SRC" && ./configure --prefix="$OUT" $COMMON \
		--target-os=android --arch=aarch64 --cpu=armv8-a --enable-cross-compile \
		--cc="$TC/bin/aarch64-linux-android26-clang" --cxx="$TC/bin/aarch64-linux-android26-clang++" \
		--ar="$TC/bin/llvm-ar" --nm="$TC/bin/llvm-nm" --ranlib="$TC/bin/llvm-ranlib" --strip="$TC/bin/llvm-strip" \
		--sysroot="$TC/sysroot" --extra-cflags="-O2 -fPIC") > "$WORK/configure-android.log" 2>&1 ||
		{ tail -30 "$WORK/configure-android.log"; exit 1; }
fi
(cd "$SRC" && make -j"$JOBS" > "$WORK/make.log" 2>&1 && make install > "$WORK/install.log" 2>&1) || { tail -40 "$WORK/make.log"; exit 1; }
# The libraries and headers are what the player needs: the rest of the install (pkg-config files, share/) goes.
rm -rf "$OUT/share"
cp "$SRC/COPYING.LGPLv2.1" "$OUT/COPYING.LGPLv2.1"
printf '%s\n' "$STAMP" > "$OUT/STAMP"
echo "FFmpeg $FFMPEG_VERSION (Bink only) built in $OUT"
