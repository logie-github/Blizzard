#!/bin/sh
# Packs the World of Warcraft app's private server into warcraft/android/server/server.tar.xz
# (git-ignored), which the app ships as an asset and unpacks into its storage: the programs
# scripts/compile-azerothcore.sh left in build/azerothcore-dist with every library they load,
# Alpine's MariaDB, OpenSSL's legacy provider, the system call shim, the SQL, the configs, a seed
# database folder and ctl.sh. Takes a few minutes, compiling nothing but the shim.
#
# The programs run from /data/data/com.logie.warcraft/files/server, the way Termux runs its
# programs from its own folder: each one's interpreter is that folder's lib/ld-musl-*.so.1 and it
# finds its libraries in ../lib, so they need nothing from the phone but the kernel.
#
# On a machine with Docker, runs itself in the same Alpine as the compile (the libraries it copies
# are the ones the programs were built against). DOCKER_RUN_ARGS adds arguments to `docker run`.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../warcraft/server-version.env
. "$ROOT/warcraft/server-version.env"
# Modules the app's user picked (fetch-azerothcore.sh), for VERSION.
MODULES="$MODULES
${WOW_EXTRA_MODULES:-}"

if [ -z "${IN_ALPINE:-}" ]; then
	# shellcheck disable=SC2086
	exec docker run --rm -e IN_ALPINE=1 -e WOW_EXTRA_MODULES="${WOW_EXTRA_MODULES:-}" ${DOCKER_RUN_ARGS:-} \
		-v "$ROOT:/repo" -w /repo "alpine:$ALPINE_VERSION" /repo/scripts/package-azerothcore.sh
fi

APP_FILES=/data/data/com.logie.warcraft/files
PREFIX="$APP_FILES/server"
DIST=/repo/build/azerothcore-dist
STAGE=/repo/build/warcraft-server
OUT=/repo/warcraft/android/server
# Left when the allied races' files weren't all made (a fetch that failed): CI doesn't keep a
# package without them, so the next build fetches them again.
INCOMPLETE=/repo/build/package-incomplete
rm -f "$INCOMPLETE"

if [ ! -x "$DIST/bin/worldserver" ]; then
	echo "No compiled server in build/azerothcore-dist: run scripts/compile-azerothcore.sh first." >&2
	exit 1
fi

apk add -q --no-progress build-base patchelf xz tar python3 boost-dev openssl-dev mariadb-connector-c-dev \
	readline-dev bzip2-dev zlib-dev mariadb mariadb-client jemalloc

# The app's own modules' data (their SQL, the files a module makes the game's patch from...) as the
# repository has it now, over what the compile copied: the compile's cache key covers only what's
# compiled (the modules' sources and configs), so a change to a module's data, tools or docs packages
# the server again without compiling it (.github/workflows/build-warcraft.yml).
for dir in /repo/warcraft/modules/*/; do
	dir=${dir%/}
	name=$(basename "$dir")
	for sub in data/sql data/client data/server data/zones data/patch sql; do
		rm -rf "${DIST:?}/modules/$name/$sub"
		[ -d "$dir/$sub" ] || continue
		mkdir -p "$DIST/modules/$name/$(dirname "$sub")"
		cp -r "$dir/$sub" "$DIST/modules/$name/$sub"
	done
done

# The package: programs, their libraries, MariaDB, SQL and configs.
rm -rf "$STAGE"
pkg="$STAGE/server"
mkdir -p "$pkg/bin" "$pkg/lib" "$pkg/etc/modules" "$pkg/share" "$pkg/src/data"
cp "$DIST"/bin/* "$pkg/bin/"
for prog in mariadbd mariadb mariadb-admin mariadb-dump; do
	cp "$(command -v "$prog")" "$pkg/bin/"
done
cp -L /usr/lib/libjemalloc.so.2 "$pkg/lib/"
# OpenSSL 3's legacy provider: RC4, which encrypts the game's packet headers, is only there. The
# world server loads it when it starts (ctl.sh points OPENSSL_MODULES here); without it, it stops
# the moment a client enters the world.
mkdir -p "$pkg/lib/ossl-modules"
cp -L /usr/lib/ossl-modules/legacy.so "$pkg/lib/ossl-modules/"
# System calls Android doesn't allow apps, made with ones it does (preloaded by ctl.sh).
cc -O2 -shared -fPIC -o "$pkg/lib/libandroidcompat.so" /repo/warcraft/server/android_compat.c
cp -r /usr/share/mariadb "$pkg/share/mariadb"
cp "$DIST"/etc/*.conf.dist "$DIST/etc/mmaps-config.yaml" "$pkg/etc/"
cp "$DIST"/etc/modules/*.conf.dist "$pkg/etc/modules/"

# SQL, where the servers look for it (SourceDirectory): the core's (base, updates and custom),
# the modules' and the progression system's brackets.
cp -r "$DIST/sql" "$pkg/src/data/sql"
for dir in "$DIST"/modules/*/; do
	dir=${dir%/}
	name=$(basename "$dir")
	# mod-worgoblin's SQL is ChromieCraft's alone: mod-worgen-goblin's package step (below) puts it in
	# that module's data/sql/chromiecraft, which only ChromieCraft's world database reads (ctl.sh).
	[ "$name" != mod-worgoblin ] || continue
	if [ -d "$dir/data/sql" ]; then
		mkdir -p "$pkg/src/modules/$name/data"
		cp -r "$dir/data/sql" "$pkg/src/modules/$name/data/sql"
	fi
	# What a module makes the game's patch from as the world server starts (mod-skyborne's).
	if [ -d "$dir/data/client" ]; then
		mkdir -p "$pkg/src/modules/$name/data"
		cp -r "$dir/data/client" "$pkg/src/modules/$name/data/client"
	fi
	# SQL a module runs itself as the world server starts (mod-worgen-goblin's).
	if [ -d "$dir/data/server" ]; then
		mkdir -p "$pkg/src/modules/$name/data"
		cp -r "$dir/data/server" "$pkg/src/modules/$name/data/server"
	fi
	# mod-worgen-goblin's starting areas: their rows for the game's tables and the world's (their
	# files for the game and the server's data are the cata-zones package's, which the app downloads).
	if [ -d "$dir/data/zones" ]; then
		mkdir -p "$pkg/src/modules/$name/data/zones"
		cp -r "$dir/data/zones/client" "$dir/data/zones/server" "$pkg/src/modules/$name/data/zones/"
	fi
	# Older modules (mod-npc-talent-template) keep theirs in sql/<database>, which the servers
	# don't read: it goes where they look, data/sql/db-<database>. Without it the world server
	# stops at the end of loading, on a table that isn't there. The servers know an applied file
	# by its name alone, so each is named after the module (mod-chromie-xp has a production.sql
	# too). Its development.sql (a test NPC) is written for an older world database and fails.
	for sql in "$dir"/sql/auth "$dir"/sql/characters "$dir"/sql/world; do
		[ -d "$sql" ] || continue
		db=$(basename "$sql")
		to="$pkg/src/modules/$name/data/sql/db-$db"
		mkdir -p "$to"
		find "$sql" -name '*.sql' ! -name 'development.sql' | while read -r file; do
			cp "$file" "$to/$name-$db-$(basename "$file")"
		done
	done
	for sql in "$dir"/src/Bracket_*/sql; do
		[ -d "$sql" ] || continue
		rel=${sql#"$dir/"}
		mkdir -p "$pkg/src/modules/$name/$(dirname "$rel")"
		cp -r "$sql" "$pkg/src/modules/$name/$rel"
	done
done

# Moratari's own voice (mod-wrath-remix, tools/voices.py): her Legion Remix lines, fetched from the
# game's files by their ids and made WAVs here (they are never in the repository); the world server
# puts them in the game's patch. Without them she speaks in text alone.
if [ -d "$DIST/modules/mod-wrath-remix" ]; then
	apk add -q --no-progress ffmpeg
	python3 /repo/warcraft/modules/mod-wrath-remix/tools/voices.py fetch "$pkg/src/modules/mod-wrath-remix/data/voices" ||
		echo "Moratari's voice wasn't all fetched: she speaks without it where it's missing" >&2
	# Eternus's own shape (tools/models.py): her dragon from the game's files by their ids, made a
	# model 3.3.5 draws. Its list of files is written last; without it she keeps the dragonspawn's.
	python3 /repo/warcraft/modules/mod-wrath-remix/tools/models.py fetch "$pkg/src/modules/mod-wrath-remix/data/models" ||
		echo "Eternus's own shape wasn't fetched: she keeps the dragonspawn's" >&2
fi

# The void elves' and the nightborne's models, textures and voices (mod-allied-races, tools/package.py):
# Blizzard's files of today, fetched by their ids and made 3.3.5's here (they are never in the
# repository; build/allied-races-cache keeps what was fetched, CI caches it); the world server puts
# them in the game's patch with the module's tables. Without them the races aren't in the game.
if [ -d "$DIST/modules/mod-allied-races" ]; then
	apk add -q --no-progress ffmpeg py3-numpy py3-pillow
	python3 /repo/warcraft/modules/mod-allied-races/tools/package.py fetch /repo/build/allied-races-cache \
		"$pkg/src/modules/mod-allied-races/data/files" ||
		{ echo "The allied races' files weren't all made (tools/package.py says which): the races aren't in the game" >&2
		  echo "mod-allied-races" >> "$INCOMPLETE"; }
fi

# The Worgen's and Goblins' files (mod-worgen-goblin, tools/package.py): mod-worgoblin's files for
# the game (its models, textures, sounds, icons and texts: never in the repository), laid out for the
# game's patch the world server makes, and its SQL for ChromieCraft's world database alone. Without
# them the races aren't in the game.
if [ -d "$DIST/modules/mod-worgen-goblin" ] && [ -d "$DIST/modules/mod-worgoblin" ]; then
	apk add -q --no-progress py3-numpy py3-pillow
	python3 /repo/warcraft/modules/mod-worgen-goblin/tools/package.py "$DIST/modules/mod-worgoblin" \
		"$pkg/src/modules/mod-worgen-goblin/data" ||
		{ echo "mod-worgoblin's files weren't all made (tools/package.py says why): the Worgen and Goblins aren't in the game" >&2
		  echo "mod-worgen-goblin" >> "$INCOMPLETE"; }
fi

# The murlocs' model and textures and the naga's headdresses and outfits (mod-murloc-naga,
# tools/murloc_model.py and tools/naga_parts.py): Blizzard's newer murloc with its fins in styles and
# colours and its kin's parts (horns, lure, Maria's hair and dress...) made a 3.3.5 character's, and the naga's own crowns, helms and
# outfits as parts, from the game's files by their ids (never in the repository; what was fetched is
# kept with the allied races' cache); the world server puts them in the game's patch-<locale>-T with the
# module's tables, the naga's parts added to the client's own naga. Each list of files is written last;
# without the murlocs' they aren't drawn, without the naga's they have no headdresses or outfits.
if [ -d "$DIST/modules/mod-murloc-naga" ]; then
	apk add -q --no-progress py3-numpy py3-pillow
	MURLOC_CACHE=/repo/build/allied-races-cache/murloc python3 /repo/warcraft/modules/mod-murloc-naga/tools/murloc_model.py fetch \
		"$pkg/src/modules/mod-murloc-naga/data/files" ||
		{ echo "The murlocs' model wasn't made (tools/murloc_model.py says why): the murlocs aren't drawn" >&2
		  echo "mod-murloc-naga" >> "$INCOMPLETE"; }
	MURLOC_CACHE=/repo/build/allied-races-cache/murloc python3 /repo/warcraft/modules/mod-murloc-naga/tools/naga_parts.py fetch \
		"$pkg/src/modules/mod-murloc-naga/data/files" ||
		{ echo "The naga's headdresses and outfits weren't made (tools/naga_parts.py says why)" >&2
		  echo "mod-murloc-naga" >> "$INCOMPLETE"; }
	# The naga's story's assets: their emotes (today's naga's and the night elves' animations, merged
	# into the client's naga as the patch is made), its people's models (today's sea witch, warden and
	# Queen Azshara made 3.3.5's) and its Warcraft III voices (warcraft.wiki.gg's files, or Wowpedia's
	# copies, checked by their SHA-1). Each list is written last; without one, those emotes, models or
	# voices aren't in the game (the voices' lines show as text, the models' people their FALLBACK
	# looks) and the realm works as before. The emotes and models are wago.tools' files, as the
	# murlocs' model is: a fetch that fails marks the package incomplete (made, not kept or published,
	# so the next run tries again). The voices come from a wiki that may refuse CI's runners: one that
	# isn't fetched is left out with a line here, and the package is kept without it.
	apk add -q --no-progress ffmpeg
	MURLOC_CACHE=/repo/build/allied-races-cache/murloc python3 /repo/warcraft/modules/mod-murloc-naga/tools/naga_emotes.py fetch \
		"$pkg/src/modules/mod-murloc-naga/data/files" ||
		{ echo "The naga's emotes weren't made (tools/naga_emotes.py says why): the naga play only the game's own" >&2
		  echo "mod-murloc-naga" >> "$INCOMPLETE"; }
	MURLOC_CACHE=/repo/build/allied-races-cache/murloc python3 /repo/warcraft/modules/mod-murloc-naga/tools/naga_models.py fetch \
		"$pkg/src/modules/mod-murloc-naga/data/files" ||
		{ echo "The naga's story's models weren't made (tools/naga_models.py says why): their looks draw nothing" >&2
		  echo "mod-murloc-naga" >> "$INCOMPLETE"; }
	MURLOC_CACHE=/repo/build/allied-races-cache/murloc python3 /repo/warcraft/modules/mod-murloc-naga/tools/naga_voices.py fetch \
		"$pkg/src/modules/mod-murloc-naga/data/files" ||
		echo "The naga's story's voices weren't all fetched: their lines show as text where they're missing" >&2
fi

# Lua scripts for ALE (mod-ale): its own, and those of the modules the app's user picked that are
# Lua (a module's .lua files, but for the game's add-ons it may bring: folders of .toc files, or
# named client, addon or interface).
mkdir -p "$pkg/lua_scripts"
[ ! -d "$DIST/lua_scripts" ] || cp -r "$DIST/lua_scripts/." "$pkg/lua_scripts/"
echo "${WOW_EXTRA_MODULES:-}" | awk 'NF { print $1 }' | while read -r name; do
	dir="/repo/build/azerothcore/modules/$name"
	[ -d "$dir" ] || continue
	find "$dir" -name '*.lua' ! -path '*/.git/*' | while read -r file; do
		rel=${file#"$dir/"}
		case "$(echo "$rel" | tr 'A-Z' 'a-z')" in
		*client*|*addon*|*interface*) continue ;;
		esac
		[ -z "$(find "$(dirname "$file")" -maxdepth 1 -iname '*.toc' | head -1)" ] || continue
		mkdir -p "$pkg/lua_scripts/$name/$(dirname "$rel")"
		cp "$file" "$pkg/lua_scripts/$name/$rel"
	done
done

# The game files the modules the app's user picked bring: the DBC files they change, for the
# server's data and the game, and their patch for the game (scripts/module-files.py; ctl.sh puts
# them in place). Read from the sources the compile used: a module left out isn't there.
extra=$(echo "${WOW_EXTRA_MODULES:-}" | awk 'NF { print "/repo/build/azerothcore/modules/" $1 }')
if [ -n "$extra" ]; then
	# shellcheck disable=SC2086
	python3 /repo/scripts/module-files.py "$pkg/share" $extra
fi

# Every library the programs load, then the programs pointed at them. The Alpine here has to have
# what they were built against (CI caches the compile, while Alpine's packages move on).
missing=$(for prog in "$pkg"/bin/* "$pkg/lib/libjemalloc.so.2" "$pkg/lib/ossl-modules/legacy.so"; do
	ldd "$prog" 2>&1 | grep "not found" | sed "s|^|$(basename "$prog"): |"
done)
if [ -n "$missing" ]; then
	echo "$missing" >&2
	echo "Libraries the programs were built against aren't in this Alpine: compile again." >&2
	exit 1
fi
ldso=$(ls /lib/ld-musl-*.so.1)
cp "$ldso" "$pkg/lib/"
interp="$PREFIX/lib/$(basename "$ldso")"
copy_deps() {
	ldd "$1" 2>/dev/null | awk '/=>/ { print $3 }' | while read -r lib; do
		[ -f "$lib" ] || continue
		base=$(basename "$lib")
		case "$base" in ld-musl-*|libc.musl-*) continue ;; esac
		[ -f "$pkg/lib/$base" ] && continue
		cp -L "$lib" "$pkg/lib/$base"
		copy_deps "$lib"
	done
}
for prog in "$pkg"/bin/* "$pkg/lib/libjemalloc.so.2"; do
	copy_deps "$prog"
done
# musl's libc is its loader; programs ask for it as libc.musl-<arch>.so.1.
cp "$ldso" "$pkg/lib/libc.musl-$(uname -m).so.1"
for prog in "$pkg"/bin/*; do
	strip "$prog"
	patchelf --set-interpreter "$interp" --set-rpath '$ORIGIN/../lib' "$prog"
done
for lib in "$pkg"/lib/*.so*; do
	case "$(basename "$lib")" in ld-musl-*|libc.musl-*) continue ;; esac
	strip --strip-unneeded "$lib"
	patchelf --set-rpath '$ORIGIN' "$lib"
done
strip --strip-unneeded "$pkg/lib/ossl-modules/legacy.so"
patchelf --set-rpath '$ORIGIN/..' "$pkg/lib/ossl-modules/legacy.so"

# An empty MariaDB data folder with the server's databases and user, made here by the same
# MariaDB, so the phone only copies it.
seed="$pkg/mariadb-seed"
mariadb-install-db --no-defaults --auth-root-authentication-method=normal --skip-test-db \
	--user=root --datadir="$seed" > /dev/null
mariadbd --no-defaults --user=root --datadir="$seed" --socket=/tmp/seed.sock --skip-networking \
	--innodb-use-native-aio=0 --innodb-log-file-size=48M > /tmp/seed.log 2>&1 &
for _ in $(seq 60); do mariadb-admin --socket=/tmp/seed.sock ping > /dev/null 2>&1 && break; sleep 1; done
mariadb --socket=/tmp/seed.sock -uroot < /repo/warcraft/server/create-databases.sql
mariadb-admin --socket=/tmp/seed.sock -uroot shutdown
wait
rm -f "$seed"/*.err "$seed"/*.pid "$seed"/aria_log_control.lock

cat > "$pkg/VERSION" <<EOF
core $CORE_COMMIT
playerbot-core $PLAYERBOT_CORE_COMMIT
merged $(cat "$DIST/merged")
$(echo "$MODULES" | awk 'NF { print $1, $3 }')
$(for dir in /repo/warcraft/modules/*/; do [ -d "$dir" ] && echo "$(basename "$dir") app"; done)
mariadb $(mariadbd --version | awk '{ print $3 }')
alpine $(cat /etc/alpine-release) $(uname -m)
EOF
cp /repo/warcraft/server/ctl.sh "$pkg/ctl.sh"

mkdir -p "$OUT"
tar -C "$STAGE" -cf - server | xz -T0 -6 > "$OUT/server.tar.xz"
du -sh "$pkg" "$OUT/server.tar.xz"
cat "$pkg/VERSION"
