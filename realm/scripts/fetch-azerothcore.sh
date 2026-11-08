#!/bin/sh
# Checks out the World of Warcraft app's server source into the folder given (default
# build/azerothcore): AzerothCore at the revision ChromieCraft runs (warcraft/server-version.env),
# the playerbots fork's core changes merged onto it, the app's patches (warcraft/patches/azerothcore/),
# the modules at their pinned commits, and the app's own modules (warcraft/modules/: Wrath Remix's).
# Used by scripts/build-azerothcore.sh (the phone's server) and CI's Windows data tools.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../warcraft/server-version.env
. "$ROOT/warcraft/server-version.env"
SRC="${1:-$ROOT/build/azerothcore}"
# Modules the app's user picked (the module browser; .github/workflows/build-warcraft-modules.yml),
# as server-version.env lists them: "name repository commit" a line.
MODULES="$MODULES
${WOW_EXTRA_MODULES:-}"

if [ ! -d "$SRC/.git" ]; then
	git init -q "$SRC"
	git -C "$SRC" remote add origin "$CORE_REPO"
	git -C "$SRC" remote add playerbots "$PLAYERBOT_CORE_REPO"
fi
git -C "$SRC" fetch -q --filter=blob:none origin "$CORE_COMMIT"
git -C "$SRC" fetch -q --filter=blob:none playerbots "$PLAYERBOT_CORE_COMMIT"
git -C "$SRC" checkout -q --force "$CORE_COMMIT"
git -C "$SRC" clean -qfdx -e modules/
git -C "$SRC" -c user.name="World of Warcraft" -c user.email="warcraft@users.noreply.github.com" \
	merge -q --no-edit "$PLAYERBOT_CORE_COMMIT"
# The app's own changes to the core (warcraft/patches/azerothcore/).
set -- "$ROOT"/warcraft/patches/azerothcore/*.patch
if [ -f "$1" ]; then
	git -C "$SRC" -c user.name="World of Warcraft" -c user.email="warcraft@users.noreply.github.com" am -q "$@"
fi

echo "$MODULES" | while read -r name repo commit; do
	[ -n "$name" ] || continue
	dir="$SRC/modules/$name"
	if [ ! -d "$dir/.git" ]; then
		git init -q "$dir"
		git -C "$dir" remote add origin "$repo"
	fi
	git -C "$dir" fetch -q --depth 1 origin "$commit"
	git -C "$dir" checkout -q --force FETCH_HEAD
	git -C "$dir" clean -qfdx
	# Some modules bring their libraries as submodules.
	[ ! -f "$dir/.gitmodules" ] || git -C "$dir" submodule update -q --init --recursive --depth 1
	# Fitting a module in, whatever it is called. The core calls Add<folder name, - as _>Scripts() of each module,
	# and the folder is the repository's name, which a module's loader is often not written for (its README says
	# to clone it as mod-accountwide-mounts, the repository is wow-mod-accountwide-mounts). So that every module
	# picked links, a file of the module's own is added that defines the name the core calls and calls the
	# module's own top-level loaders (the Add...Scripts() it defines that nothing else of it calls). The module
	# keeps the name it was picked by, which this build's lists and the app use.
	want="Add$(echo "$name" | tr - _)Scripts"
	# (A module with its own CMakeLists.txt that registers its loader, AC_ADD_SCRIPT_LOADER, is not named for.)
	if [ -d "$dir/src" ] && ! grep -qs AC_ADD_SCRIPT_LOADER "$dir/CMakeLists.txt" && ! grep -rqE "^void[[:space:]]+$want[[:space:]]*\\(" "$dir" --include='*.cpp' --include='*.h' --include='*.hpp'; then
		defined=$(grep -rhE '^void[[:space:]]+Add[A-Za-z0-9_]+Scripts[[:space:]]*\([[:space:]]*\)[[:space:]]*(\{)?[[:space:]]*$' "$dir" --include='*.cpp' |
			tr -d '\r' | sed 's/^void[[:space:]]*//; s/[[:space:]]*(.*$//' | sort -u)
		called=$(grep -rhE '^[[:space:]]+Add[A-Za-z0-9_]+Scripts[[:space:]]*\([[:space:]]*\)[[:space:]]*;' "$dir" --include='*.cpp' --include='*.h' --include='*.hpp' |
			tr -d '\r' | sed 's/^[[:space:]]*//; s/[[:space:]]*(.*$//' | sort -u)
		top=$(printf '%s\n' "$defined" | grep -vxF "$called" | grep . || true)
		if [ -n "$top" ]; then
			{
				for fn in $top; do printf 'void %s();\n' "$fn"; done
				printf '\nvoid %s()\n{\n' "$want"
				for fn in $top; do printf '    %s();\n' "$fn"; done
				printf '}\n'
			} > "$dir/src/blizz_loader_alias.cpp"
			echo "$name: $want calls $(echo $top)"
		else
			echo "$name: no loader named $want, and none to call instead" >&2
		fi
	fi
	# The core changes a module needs and ships for itself (warcraft/module-core-patches.txt: module,
	# then its patch's path in the module): applied to the core when they apply cleanly. A module
	# is listed once its patch is known to be the one for the pinned module (some modules keep old
	# patches in patches/ that mustn't be applied). When it doesn't apply, the module is left as it
	# is and fails its own check, which the module build leaves it out for.
	while read -r mod patch; do
		[ "$mod" = "$name" ] && [ -f "$dir/$patch" ] || continue
		if git -C "$SRC" apply --ignore-space-change --check "$dir/$patch" 2> /dev/null; then
			git -C "$SRC" apply --ignore-space-change "$dir/$patch"
			echo "$name: applied its core patch $patch"
		else
			echo "$name: its core patch $patch doesn't apply to this core" >&2
		fi
	done < "$ROOT/warcraft/module-core-patches.txt"
	# The app's own changes to the module (warcraft/patches/<module>/).
	set -- "$ROOT"/warcraft/patches/"$name"/*.patch
	if [ -f "$1" ]; then
		# A module whose files have CRLF line endings looks modified after the checkout, which
		# git am refuses: the patches are applied as they are then.
		git -C "$dir" -c user.name="World of Warcraft" -c user.email="warcraft@users.noreply.github.com" am -q "$@" ||
			{
				git -C "$dir" -c user.name="World of Warcraft" -c user.email="warcraft@users.noreply.github.com" am --abort
				git -C "$dir" apply "$@"
			}
	fi
done
# The app's own modules, kept in this repository (warcraft/modules/), copied in as they are.
for dir in "$ROOT"/warcraft/modules/*/; do
	[ -d "$dir" ] || continue
	rm -rf "$SRC/modules/$(basename "$dir")"
	cp -r "${dir%/}" "$SRC/modules/"
done
# Every folder in modules/ is a module (the core keeps only files there): those not listed go.
for dir in "$SRC"/modules/*/; do
	[ -d "$dir" ] || continue
	name=$(basename "$dir")
	[ ! -d "$ROOT/warcraft/modules/$name" ] || continue
	echo "$MODULES" | grep -q "^$name " || rm -rf "$dir"
done
echo "AzerothCore $(git -C "$SRC" rev-parse --short HEAD) (ChromieCraft ${CORE_COMMIT%"${CORE_COMMIT#???????}"} + playerbots ${PLAYERBOT_CORE_COMMIT%"${PLAYERBOT_CORE_COMMIT#???????}"}) in $SRC"
