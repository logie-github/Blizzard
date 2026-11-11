#!/usr/bin/env bash
# Builds the .NET runtime (wine-mono) the Forever Launcher needs, as the app expects it:
#   wine-mono.tar.xz  — the C:\windows\mono tree (its single top folder is "mono"), unpacked by [WineMono]
#   wine-mono.json    — {"version","size","sha256","unpacked"} the app checks the download against
#
# The launcher is a WinForms (.NET 4) program and Winlator's Wine ships no .NET runtime. Wine 10.10 finds the
# runtime at C:\windows\mono by path alone, so the app only has to drop these files in — no installer is run in
# the container, which is what left the launcher's window black (an install finishing while it already started).
#
# The tree is the payload of the official wine-mono MSI, obtained by installing it into a throwaway Wine prefix
# (the same way it reaches a real prefix), then taring C:\windows\mono. No registry is shipped; it is not needed.
set -euo pipefail

VERSION="${WINE_MONO_VERSION:-10.1.0}"
MSI="wine-mono-${VERSION}-x86.msi"
URL="https://dl.winehq.org/wine/wine-mono/${VERSION}/${MSI}"
OUT="${1:-build/wine-mono}"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
export WINEPREFIX="$work/prefix" WINEDEBUG=-all WINEDLLOVERRIDES="mscoree=d;mshtml=d"
mkdir -p "$OUT"

echo "Downloading $MSI"
curl -fL --retry 4 "$URL" -o "$work/$MSI"

echo "Creating a clean Wine prefix (no mono, no gecko)"
xvfb-run -a wine wineboot -i
wineserver -w

echo "Installing the runtime from the MSI"
msi_win="$(winepath -w "$work/$MSI")"
# Re-enable mscoree so the MSI's files land under C:\windows\mono; /qn is a silent install.
WINEDLLOVERRIDES="" xvfb-run -a wine msiexec /i "$msi_win" /qn || true
wineserver -w

mono="$WINEPREFIX/drive_c/windows/mono"
if [ ! -d "$mono/mono-2.0" ]; then
  echo "error: the MSI did not produce C:\\windows\\mono\\mono-2.0" >&2
  exit 1
fi

echo "Packing wine-mono.tar.xz"
tar -C "$WINEPREFIX/drive_c/windows" -cf - mono | xz -T0 -6 > "$OUT/wine-mono.tar.xz"

unpacked="$(du -sb "$mono" | cut -f1)"
size="$(stat -c%s "$OUT/wine-mono.tar.xz")"
sha="$(sha256sum "$OUT/wine-mono.tar.xz" | cut -d' ' -f1)"
printf '{"version":"%s","size":%s,"sha256":"%s","unpacked":%s}\n' "$VERSION" "$size" "$sha" "$unpacked" > "$OUT/wine-mono.json"
echo "Wrote $OUT/wine-mono.tar.xz ($((size/1024/1024)) MB) and wine-mono.json"
cat "$OUT/wine-mono.json"
