#!/bin/sh
# Pinned F-Droid source for sandstranger's Warsmash 1.0.4. No Warcraft game data.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WARSMASH_WORK:-$ROOT/build/warsmash-source}"
OUT="$ROOT/app/warsmash"
ARCHIVE="$WORK/source.tar.gz"
SHA=95845f526c08a106d16a3cb9d083dbb8758fe052130dc9f160201d30c0c461ac
mkdir -p "$WORK"
if [ ! -f "$ARCHIVE" ]; then
    curl -fL --retry 3 https://f-droid.org/repo/net.warsmash.phone_5_src.tar.gz -o "$ARCHIVE.tmp"
    mv "$ARCHIVE.tmp" "$ARCHIVE"
fi
printf '%s  %s\n' "$SHA" "$ARCHIVE" | sha256sum -c -
# The prepared tree is the source and the patches over it (patches/warsmash, in order): it is made again when either changes.
PATCHES="$ROOT/patches/warsmash"
STAMP="$SHA $(cat "$PATCHES"/*.patch 2>/dev/null | sha256sum | cut -c1-64)"
if [ -f "$OUT/SOURCE_SHA256" ] && [ "$(cat "$OUT/SOURCE_SHA256")" = "$STAMP" ]; then exit 0; fi
mkdir -p "$WORK/unpacked"
tar -xzf "$ARCHIVE" -C "$WORK/unpacked" --strip-components=1
SRC="$WORK/unpacked"
mkdir -p "$OUT"
# A fresh copy each time, so nothing a patch added before (a new file) is left to trip the patches over it.
for dir in core shared fdfparser jassparser android-awt assets libgdx gdx-controllers-android; do
    rm -rf "${OUT:?}/$dir"
    cp -R "$SRC/$dir" "$OUT/"
done
cp "$SRC/LICENSE" "$OUT/LICENSE"
# The host supplies an explicit, ordered list of MPQs followed by its support resources.
# The upstream directory scan adds MPQs in filesystem order and overrides those resources.
python3 - "$OUT/core/src/com/etheller/warsmash/WarsmashGdxMapScreen.java" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text()
start = s.index('\t\tvar mpqFiles = new File(WarsmashConstants.GAME_PATH)')
end = s.index('\t\tfinal DataSource baseCompoundDataSource', start)
s = s[:start] + s[end:]
p.write_text(s)
PY
# The launcher's changes to the engine (patches/warsmash/NNNN-*.patch, paths from the source's root), in order.
for patch in "$PATCHES"/*.patch; do
    [ -f "$patch" ] || continue
    patch -p1 --forward --batch -d "$OUT" < "$patch"
done
printf '%s\n' "$STAMP" > "$OUT/SOURCE_SHA256"
echo "Warsmash 1.0.4 prepared in $OUT"
