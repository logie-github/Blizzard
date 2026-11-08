#!/bin/sh
# Checks out the Forever realm's source into the folder given (default build/trinity-forever): TrinityCore's "forever"
# branch at the commit pinned in forever/server-version.env, with the app's patches (forever/patches/).
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../forever/server-version.env
. "$ROOT/forever/server-version.env"
SRC="${1:-$ROOT/build/trinity-forever}"

if [ ! -d "$SRC/.git" ]; then
	git init -q "$SRC"
	git -C "$SRC" remote add origin "$TRINITY_REPO"
fi
git -C "$SRC" fetch -q --depth 1 origin "$TRINITY_COMMIT"
git -C "$SRC" checkout -q --force "$TRINITY_COMMIT"
git -C "$SRC" clean -qfdx
set -- "$ROOT"/forever/patches/*.patch
if [ -f "$1" ]; then
	git -C "$SRC" -c user.name=blizz -c user.email=blizz@users.noreply.github.com am -q "$@"
fi
echo "TrinityCore forever $(git -C "$SRC" rev-parse --short HEAD) in $SRC"
