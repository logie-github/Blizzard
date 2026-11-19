#!/bin/sh
# Inside Alpine (package-converter-runtime.sh): makes /out/converter-runtime.tar.xz from the apk's Python, numpy and Pillow.
set -eu
apk add -q --no-progress python3 py3-numpy py3-pillow xz tar git file
PYV=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
PKG=/stage/converter-runtime
rm -rf /stage
mkdir -p "$PKG/python/bin" "$PKG/python/lib" "$PKG/lib" "$PKG/bin" "$PKG/repo/realm/warcraft"

# The interpreter and the standard library (without what a converter never uses: tests, IDLE, tkinter, turtle, ensurepip's wheels)
cp -L "$(command -v python3)" "$PKG/python/bin/python3"
cp -a "/usr/lib/python$PYV" "$PKG/python/lib/"
rm -rf "$PKG/python/lib/python$PYV"/test "$PKG/python/lib/python$PYV"/idlelib "$PKG/python/lib/python$PYV"/tkinter \
	"$PKG/python/lib/python$PYV"/turtledemo "$PKG/python/lib/python$PYV"/ensurepip "$PKG/python/lib/python$PYV"/lib2to3
rm -rf "$PKG/python/lib/python$PYV"/site-packages/pip "$PKG/python/lib/python$PYV"/site-packages/setuptools

# Every shared library the interpreter and its extension modules need (musl's loader first), found by ldd
need() {
	for f in "$@"; do
		ldd "$f" 2> /dev/null | sed -n 's/^[[:space:]]*\([^ ]*\) => \(\/[^ ]*\).*/\2/p'
	done
}
{
	need "$PKG/python/bin/python3"
	find "$PKG/python/lib" -name '*.so*' -type f | while read -r so; do need "$so"; done
	[ -e /usr/lib/libpython$PYV.so.1.0 ] && echo "/usr/lib/libpython$PYV.so.1.0"
	echo /lib/ld-musl-aarch64.so.1
} | sort -u | while read -r lib; do
	[ -f "$lib" ] || continue
	cp -L "$lib" "$PKG/lib/"
done

# The tools, by their repository paths (their imports reach each other through them)
W=/repo/realm/warcraft
for d in tools/catabackport converter modules/mod-worgen-goblin/tools/zones modules/mod-allied-races/tools; do
	mkdir -p "$PKG/repo/realm/warcraft/$(dirname "$d")"
	cp -a "$W/$d" "$PKG/repo/realm/warcraft/$d"
done
find "$PKG/repo" -name __pycache__ -type d -prune -exec rm -rf {} +
find "$PKG/repo" -name 'test_*' -prune -exec rm -rf {} + 2> /dev/null || true

# The Converter, at the commit the tool pins
COMMIT_PIN=$(python3 -c "import json; print(json.load(open('/repo/realm/warcraft/tools/catabackport/pins.json'))['converter']['commit'])")
REPO_PIN=$(python3 -c "import json; print(json.load(open('/repo/realm/warcraft/tools/catabackport/pins.json'))['converter']['repo'])")
git init -q /tmp/wotlkconv-src
git -C /tmp/wotlkconv-src fetch -q --depth 1 "$REPO_PIN" "$COMMIT_PIN"
git -C /tmp/wotlkconv-src checkout -q FETCH_HEAD
mkdir -p "$PKG/wotlkconv"
cp -a /tmp/wotlkconv-src/src/wotlkconv "$PKG/wotlkconv/wotlkconv"

# python3 through the loader (BLIZZ_LDSO: where the launcher keeps musl's loader), with the library path, home and module path set
cat > "$PKG/bin/python3" <<'WRAP'
#!/bin/sh
D="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONHOME="$D/python"
export PYTHONPATH="$D/repo/realm/warcraft/tools:$D/repo/realm/warcraft:$D/wotlkconv${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
export LD_LIBRARY_PATH="$D/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
LDSO="${BLIZZ_LDSO:-$D/lib/ld-musl-aarch64.so.1}"
exec "$LDSO" --library-path "$D/lib" "$D/python/bin/python3" "$@"
WRAP
chmod +x "$PKG/bin/python3"
echo "python $PYV, built from commit ${COMMIT:-local}" > "$PKG/VERSION"

# A smoke test on this machine (arm64 Alpine runs it natively): numpy, Pillow, the tool's and the driver's imports
(cd /tmp && "$PKG/bin/python3" -c "import numpy, PIL, catabackport, sys; print('python', sys.version.split()[0], 'numpy', numpy.__version__, 'Pillow', PIL.__version__)")
"$PKG/bin/python3" "$PKG/repo/realm/warcraft/converter/convert.py" list

tar -C /stage --sort=name --owner=0 --group=0 -cf - converter-runtime | xz -T0 -6 > /out/converter-runtime.tar.xz
