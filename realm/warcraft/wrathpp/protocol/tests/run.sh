#!/bin/sh
# Builds and runs the protocol's tests: the registry built by tools/registry.py, then the C++ codec
# tests against it (with warnings as errors, and with the sanitizers where the compiler has them).
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
WPP="$(cd "$HERE/../.." && pwd)"
OUT="${TMPDIR:-/tmp}/wrathpp-protocol-tests.$$"
mkdir -p "$OUT"
trap 'rm -rf "$OUT"' EXIT
CXX="${CXX:-c++}"
line=$(python3 "$WPP/tools/registry.py" build "$WPP/registry/registry.json" "$OUT/registry.bin")
echo "$line"
hash=$(echo "$line" | sed -n 's/.*hash 0x\([0-9a-f]*\).*/\1/p')
san="-fsanitize=address,undefined"
"$CXX" -std=c++17 -Wall -Wextra -Werror -O1 $san "$HERE/test_codec.cpp" -o "$OUT/test_codec" 2> /dev/null ||
	{ san=; "$CXX" -std=c++17 -Wall -Wextra -Werror -O1 "$HERE/test_codec.cpp" -o "$OUT/test_codec"; }
"$OUT/test_codec" "$OUT/registry.bin" "$hash"
python3 -I "$WPP/tools/test_registry.py"
python3 -I "$WPP/tools/test_sl_inventory.py"
