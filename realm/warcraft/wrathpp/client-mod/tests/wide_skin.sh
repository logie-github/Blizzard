#!/bin/sh
# The wide skins' logic (wrathpp-native/src/WideSkin.hpp) compiled and run here against a stand-in of the stock client's
# shared index pool (wide_skin_test.cpp). Needs a C++17 compiler (g++ or clang++).
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(mktemp -d "${TMPDIR:-/tmp}/wrathpp-wide.XXXXXX")"
trap 'rm -rf "$OUT"' EXIT
CXX="${CXX:-g++}"
"$CXX" -std=c++17 -O1 -Wall -Wextra -Werror -o "$OUT/wide_skin_test" "$HERE/wide_skin_test.cpp"
"$OUT/wide_skin_test"
