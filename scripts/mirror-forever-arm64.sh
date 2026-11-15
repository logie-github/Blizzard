#!/bin/sh
# mirror-forever-arm64.sh OUT: downloads every file in forever-arm64/sources.txt into OUT and writes OUT/SHA256SUMS. The
# components-v1 files are checked against the hashes their makers published (tools/components.sha256 there); the rest are
# recorded as they are now. CI publishes OUT as the release named in forever-arm64/runtime.env.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$1"
mkdir -p "$OUT"
grep -v '^#' "$ROOT/forever-arm64/sources.txt" | while read -r name url; do
	[ -n "$name" ] || continue
	curl -fsSL --retry 4 --retry-delay 5 -o "$OUT/$name" "$url"
	echo "$name $(stat -c %s "$OUT/$name") bytes"
done
# The four components-v1 files against their makers' hashes.
cat > "$OUT/.expected" <<'H'
137807f4145b1b440075f83b2b1b3501d19c4eb618784b1a28418652cae3db03  proton-11.0-90624-arm64ec.wcp
f660b5c6422b3f93cec65664f309718942e58581b5b96fa2902d55d63ce1db8a  dxvk-2.4.1-wow-aarch64-test.wcp
02384f692735515f73aad8a544bc640abe3f35fe18e8df2e667be712c442e54c  turnip-wow-scheduler-test.zip
05434d3c102563a4577f514410cc713494bcf900f52c2b935391adf87a76b77a  turnip-V32-RP6sched.zip
H
(cd "$OUT" && sha256sum -c .expected) && rm "$OUT/.expected"
(cd "$OUT" && sha256sum $(grep -v '^#' "$ROOT/forever-arm64/sources.txt" | awk 'NF{print $1}') > SHA256SUMS)
cat "$OUT/SHA256SUMS"
