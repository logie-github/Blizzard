#!/bin/sh
# The launcher's converter runtime (build/converter-runtime/converter-runtime.tar.xz and .json: size, SHA-256, unpacked size, commit):
# Python 3 with numpy and Pillow for arm64 musl (Alpine's own packages, run on the phone through musl's loader as the realm's programs
# are: WowCtl), the converter tool (realm/warcraft/tools/catabackport), the launcher's driver (realm/warcraft/converter), the zones tools
# the tool's texture and model fixes import, mod-allied-races' blp.py, and the pinned Converter (Bar3b0n3s/Converter, pure Python).
#
#   scripts/package-converter-runtime.sh          (an arm64 machine with docker: the CI job's runner; any machine with an arm64 docker)
#
# Layout of the package (the folder `converter-runtime/`): python/ (PYTHONHOME), lib/ (every shared library Python and its modules
# need, and the loader ld-musl-aarch64.so.1), repo/realm/warcraft/... (the tools by their repository paths, so their imports of each
# other hold), wotlkconv/ (the Converter's source), bin/python3 (a wrapper that runs python through the loader: the tool starts the
# Converter as `python3 -m wotlkconv`), VERSION.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/realm/build/converter-runtime"
rm -rf "$OUT"
mkdir -p "$OUT"
docker run --rm -v "$ROOT:/repo" -v "$OUT:/out" -e COMMIT="${GITHUB_SHA:-local}" alpine:3.20 sh /repo/realm/scripts/converter-runtime-inner.sh
cd "$OUT"
size=$(stat -c %s converter-runtime.tar.xz)
sha=$(sha256sum converter-runtime.tar.xz | cut -d' ' -f1)
unpacked=$(xz -dc converter-runtime.tar.xz | wc -c)
printf '{"size": %s, "sha256": "%s", "unpacked": %s, "format": 1, "commit": "%s"}\n' "$size" "$sha" "$unpacked" "${GITHUB_SHA:-local}" > converter-runtime.json
cat converter-runtime.json
