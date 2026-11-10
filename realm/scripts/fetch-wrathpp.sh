#!/bin/sh
# Checks out the Wrath++ server's source (docs/wrathpp/ARCHITECTURE.md) into a folder of its own
# (default build/azerothcore-wrathpp): the very source the other realms' server is built from
# (scripts/fetch-azerothcore.sh: the same pins, patches and modules), then on top, for Wrath++
# alone, warcraft/wrathpp/patches/azerothcore/ (the appearance protocol's opcodes) and
# warcraft/wrathpp/modules/ (mod-wrathpp-customization, with the protocol header and the
# registry built from warcraft/wrathpp/registry/registry.json).
#
# The folder must have "wrathpp" in its path: fetch-azerothcore.sh resets and cleans the folder it
# is given, and this script never hands it the other realms' source folder.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WPP="$ROOT/warcraft/wrathpp"
SRC="${1:-$ROOT/build/azerothcore-wrathpp}"
case "$SRC" in
*wrathpp*) ;;
*)
	echo "Refused: $SRC isn't a Wrath++ folder (its path must name wrathpp)" >&2
	exit 2
	;;
esac
if [ "$(cd "$(dirname "$SRC")" 2> /dev/null && pwd -P)/$(basename "$SRC")" = "$(cd "$ROOT" && pwd -P)/build/azerothcore" ]; then
	echo "Refused: $SRC is the other realms' source folder" >&2
	exit 2
fi

sh "$ROOT/scripts/fetch-azerothcore.sh" "$SRC"
set -- "$WPP"/patches/azerothcore/*.patch
if [ -f "$1" ]; then
	git -C "$SRC" -c user.name="World of Warcraft" -c user.email="warcraft@users.noreply.github.com" am -q "$@"
fi
for dir in "$WPP"/modules/*/; do
	[ -d "$dir" ] || continue
	rm -rf "$SRC/modules/$(basename "$dir")"
	cp -r "${dir%/}" "$SRC/modules/"
done
module="$SRC/modules/mod-wrathpp-customization"
cp "$WPP/protocol/wrathpp_appearance.h" "$module/src/"
mkdir -p "$module/data"
python3 "$WPP/tools/registry.py" build "$WPP/registry/registry.json" "$module/data/registry.bin"
echo "Wrath++ server source: $(git -C "$SRC" rev-parse --short HEAD) in $SRC"
