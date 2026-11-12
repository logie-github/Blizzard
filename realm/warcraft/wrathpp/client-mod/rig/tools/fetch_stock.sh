#!/bin/sh
# The game's own creation screen, as the phone's client has it: the glue files the app read from the client's archives
# and sent to this repository as issues ("Client file CharacterCreate.xml: ...": ClientFilesDump.kt; text of the
# interface only, never in the repository's tree). Fetched with gh (in CI: GH_TOKEN and issues: read) into OUT.
#   fetch_stock.sh OUT [owner/repo]
set -eu
OUT="$1"
REPO="${2:-logie-github/Blizzard}"
mkdir -p "$OUT"
for f in GlueXML.toc GlueStrings.lua GlueButtons.xml GlueParent.xml CharacterCreate.xml CharacterCreate.lua; do
	[ -s "$OUT/$f" ] && continue
	gh api -X GET search/issues -f q="repo:$REPO is:issue \"Client file $f\" in:title" -f sort=created -f order=desc --jq '.items[0].body' > "$OUT/$f.issue"
	python3 -I - "$OUT/$f.issue" "$OUT/$f" << 'PY'
import re, sys
body = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"<summary>Files[^<]*</summary>\s*\n\s*```\n(.*)\n```\n</details>", body, re.S)
if not m:
    sys.exit("no file in the report for " + sys.argv[2] + " (" + str(len(body)) + " characters of it)")
open(sys.argv[2], "w", encoding="utf-8", newline="").write(m.group(1))
print(sys.argv[2].split("/")[-1], len(m.group(1)), "characters")
PY
	rm -f "$OUT/$f.issue"
done
