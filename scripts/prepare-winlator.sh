#!/bin/sh
# Brings Winlator (https://github.com/brunodev85/winlator, LGPL-2.1: Wine, Box64, the graphics
# drivers and an X server, which run the games) into the app as app/winlator (git-ignored), as
# YeaBwoi's scripts/prepare-winlator-app.sh does for its Warcraft app:
#
#     scripts/prepare-winlator.sh
#
# winlator-version.env names Winlator's commit, the app's package (APP_PACKAGE) and where the app
# puts the runtime (APP_ROOTFS_PATH, the same length as Winlator's own path); patches/winlator/
# holds the app's changes to it. Its Java code is compiled into the app's module with the app's R;
# its runtime's archives are rewritten for the app's path (scripts/winlator-rewrite.py).
#
# WINLATOR_SRC is where to keep the checkout (default build/winlator-app).
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1090
. "$ROOT/winlator-version.env"
: "${APP_PACKAGE:?APP_PACKAGE missing from winlator-version.env}"
SRC="${WINLATOR_SRC:-$ROOT/build/winlator-app}"
OUT="$ROOT/app/winlator"

if [ "${#WINLATOR_ROOTFS_PATH}" -ne "${#APP_ROOTFS_PATH}" ]; then
	echo "$APP_ROOTFS_PATH isn't as long as $WINLATOR_ROOTFS_PATH." >&2
	exit 1
fi

if [ ! -d "$SRC/.git" ]; then
	git init -q "$SRC"
	git -C "$SRC" remote add origin "$WINLATOR_APP_REPO"
fi
git -C "$SRC" cat-file -e "$WINLATOR_APP_COMMIT^{commit}" 2> /dev/null ||
	git -C "$SRC" fetch -q --depth 1 origin "$WINLATOR_APP_COMMIT"
git -C "$SRC" checkout -q --force "$WINLATOR_APP_COMMIT"
git -C "$SRC" clean -qfdx
set -- "$ROOT"/patches/winlator/*.patch
if [ -f "$1" ]; then
	git -C "$SRC" -c user.name=blizz -c user.email=blizz@users.noreply.github.com am -q "$@"
fi

main="$SRC/app/src/main"
rm -rf "$OUT"
mkdir -p "$OUT"
for dir in java res assets cpp jniLibs; do
	cp -r "$main/$dir" "$OUT/$dir"
done
cp "$main/AndroidManifest.xml" "$OUT/AndroidManifest.upstream.xml"

# Paths with Winlator's package in the source (compiled again, so any length).
pkg_re=$(printf '%s' "$APP_PACKAGE" | sed 's/\./\\./g')
grep -rlF "/data/data/com.winlator" "$OUT/java" "$OUT/cpp" | while read -r file; do
	sed -i "s|$WINLATOR_ROOTFS_PATH|$APP_ROOTFS_PATH|g; s|/data/data/com\.winlator/|/data/data/$APP_PACKAGE/|g" "$file"
done
if grep -rF "com.winlator/" "$OUT/java" "$OUT/cpp" | grep -F "/data/"; then
	echo "Paths with Winlator's package left in its source." >&2
	exit 1
fi

# One module: Winlator's code uses the app's R.
find "$OUT/java" -name '*.java' | while read -r file; do
	sed -i "s/^import com\.winlator\.R;\$/import $APP_PACKAGE.R;/" "$file"
	if grep -qE '(^|[^.A-Za-z0-9_])R\.' "$file" && ! grep -q "^import $pkg_re\.R;" "$file"; then
		sed -i "0,/^package .*;/s//&\nimport $APP_PACKAGE.R;/" "$file"
	fi
done

# The resources the app has its own of: its name (in every language) and its file provider's paths.
python3 -I - "$OUT/res" <<'PY'
import glob, re, sys
res = sys.argv[1]
for path in glob.glob(res + "/values*/strings.xml"):
    text = open(path, encoding="utf-8").read()
    new = re.sub(r'\s*<string name="app_name"[^>]*>.*?</string>', "", text, flags=re.S)
    if new != text:
        open(path, "w", encoding="utf-8").write(new)
PY
rm -f "$OUT/res/xml/file_paths.xml"

# The runtime, for this app's path.
find "$OUT/assets" -name '*.tzst' | sort > "$OUT/.archives"
# shellcheck disable=SC2046
python3 "$ROOT/scripts/winlator-rewrite.py" "$WINLATOR_ROOTFS_PATH" "$APP_ROOTFS_PATH" $(cat "$OUT/.archives")
rm "$OUT/.archives"

echo "Winlator $WINLATOR_VERSION ($(git -C "$SRC" rev-parse --short HEAD)) in $OUT"
