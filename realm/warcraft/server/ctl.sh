#!/bin/sh
# Runs the World of Warcraft app's private server: MariaDB, the database import, the auth and world
# servers, the client data tools. The app runs it with Android's shell (/system/bin/sh) and CI runs
# it with busybox's, so it sticks to POSIX sh. The servers (db, auth, world) are `exec`ed, so the
# process the app holds is the server itself.
#
#   ctl.sh configure                write both realms' configs (from the shipped .dist files) and folders
#   ctl.sh configure-realm REALM    write one realm's configs only (the app configures Wrath++ so)
#   ctl.sh db                       run MariaDB (makes its data folder from the seed first)
#   ctl.sh db-ping | db-stop        ask MariaDB if it's up / to shut down
#   ctl.sh sql [database]           run the SQL on stdin (prints tab-separated rows)
#   ctl.sh dbimport [REALM]         create and update the realm's databases (and the shared auth one)
#   ctl.sh realmlist [ADDRESS]      both realms in the auth database, for this phone and the Wi-Fi
#   ctl.sh races                    take out what earlier versions' custom races left (MariaDB up)
#   ctl.sh modules [REALM]          the realm's world database without what modules no longer in put
#                                   in it; the modules' DBC files for the world server, their patch in the game
#   ctl.sh auth | world [REALM]     run the auth server / the realm's world server
#   ctl.sh maps|vmaps|mmaps CLIENT  extract the server's data from a 3.3.5a client folder
#   ctl.sh wrathpp-check            Wrath++'s paths and databases, and the checks that keep it apart
#                                   from the other realms (changes nothing)
#   ctl.sh wrathpp-register [ADDR]  add Wrath++ to the auth database's realm list (its own row only,
#                                   the list backed up first); wrathpp-unregister takes that row out
#
# Two realms share the auth server, its accounts and the server's data; each has its own world
# server, configs and world, characters and playerbots databases. One world server runs at a time.
#   main   ChromieCraft (realm 1, port 8085): $FILES/etc, acore_world, acore_characters
#   remix  Wrath Remix (realm 2, port 8086): $FILES/etc-remix, acore_world_remix, ...; the
#          mod-wrath-remix module is on, and its SQL goes into these databases only
# A third, experimental and off unless its own server is installed (docs/wrathpp/):
#   wrathpp  Wrath++ (realm 5, port 8087): its own server build $FILES/server-wrathpp (the extended
#          appearance protocol), $FILES/etc-wrathpp, acore_*_wrathpp, its own run, log and data
#          folders and its own game folder $FILES/client-wrathpp. Nothing of it is made, written or
#          started by the commands for main and remix, and its own never write theirs.
#
# FILES is the app's files folder; the programs are built to run from $FILES/server.
set -eu

FILES="${FILES:-/data/data/com.logie.warcraft/files}"
SERVER="$FILES/server"
ETC="$FILES/etc"
DATA="$FILES/data"
RACES="$FILES/races"
DATA_RACES="$FILES/data-races"
DB_DIR="$FILES/mysql"
# The world server's data with the DBC files of the realm's modules over the game's (ctl.sh modules).
DATA_MODULES="$FILES/data-modules"
# The Worgen's and Goblins' starting areas' package (Gilneas, Kezan, the Lost Isles: cata-zones, the
# release the app downloads; mod-worgen-goblin's README): client/ for the game's patch, server/ for
# the world server's data (zones_data).
ZONES="$FILES/zones"
# What the modules the app's user picked bring for the game's files (scripts/module-files.py).
MODULE_FILES="$SERVER/share"
# The modules whose SQL went into the world database (ctl.sh modules); goes with the databases.
WORLD_MODULES="$DB_DIR/.world-modules"
LOGS="$FILES/logs"
RUN="$FILES/run"
DB_PORT="${DB_PORT:-3310}"
DB_USER=acore
DB_PASS=acore
export HOME="$FILES" TMPDIR="$RUN/tmp"
export AC_DISABLE_INTERACTIVE=1
# OpenSSL's legacy provider (RC4, for the game's packet headers), shipped with the server.
export OPENSSL_MODULES="$SERVER/lib/ossl-modules"

# Sets `Key = value` in a config file, adding the line if the file doesn't have the key.
setkey() {
	file=$1 key=$2 value=$3
	if grep -q "^$key[[:space:]]*=" "$file"; then
		escaped=$(printf '%s' "$value" | sed 's/[|&\\]/\\&/g')
		sed -i "s|^$key[[:space:]]*=.*|$key = $escaped|" "$file"
	else
		printf '%s = %s\n' "$key" "$value" >> "$file"
	fi
}

# Copies a shipped .dist config to the live one the first time; settings the user changed stay.
# Says whether it made it (for the realm's first-time settings).
config_from_dist() {
	dist=$1 conf=$2
	[ ! -f "$conf" ] || return 1
	cp "$dist" "$conf"
}

dbinfo() {
	echo "\"127.0.0.1;$DB_PORT;$DB_USER;$DB_PASS;$1\""
}

# Wrath++'s own folders (realm wrathpp): its server build, game folder and run folder. Its
# commands run its programs as "$SERVER/bin/<name>" like the others' (the Blizzard app starts
# programs by that text: WowCtl.transform), realm() pointing SERVER at its build.
MAIN_SERVER="$SERVER"
WRATHPP_SERVER="$FILES/server-wrathpp"
WRATHPP_CLIENT="$FILES/client-wrathpp"

# The realm a command is for (main, remix or wrathpp): its configs, logs, databases, id and port;
# the server build it runs (R_SERVER), its run folder, the game folder its modules write their
# patches into, and the world server's data with its modules' DBC files.
realm() {
	REALM=${1:-main}
	SERVER="$MAIN_SERVER"
	R_RUN="$RUN" R_CLIENT="$FILES/client" R_DATA_MODULES="$DATA_MODULES" R_MODULE_FILES="$MODULE_FILES"
	case "$REALM" in
	main)
		R_ETC="$ETC" R_LOGS="$LOGS" R_ID=1 R_PORT=8085 R_NAME=ChromieCraft
		R_WORLD=acore_world R_CHARACTERS=acore_characters R_BOTS=acore_playerbots
		R_WORLD_MODULES="$WORLD_MODULES"
		;;
	remix)
		R_ETC="$FILES/etc-remix" R_LOGS="$LOGS/remix" R_ID=2 R_PORT=8086 R_NAME="Wrath Remix"
		R_WORLD=acore_world_remix R_CHARACTERS=acore_characters_remix R_BOTS=acore_playerbots_remix
		R_WORLD_MODULES="$WORLD_MODULES-remix"
		;;
	wrathpp)
		R_ETC="$FILES/etc-wrathpp" R_LOGS="$LOGS/wrathpp" R_ID=5 R_PORT=8087 R_NAME="Wrath++"
		R_WORLD=acore_world_wrathpp R_CHARACTERS=acore_characters_wrathpp R_BOTS=acore_playerbots_wrathpp
		R_WORLD_MODULES="$WORLD_MODULES-wrathpp"
		SERVER="$WRATHPP_SERVER" R_RUN="$RUN/wrathpp" R_CLIENT="$WRATHPP_CLIENT"
		R_DATA_MODULES="$FILES/data-modules-wrathpp" R_MODULE_FILES="$WRATHPP_SERVER/share"
		;;
	*)
		echo "No realm \"$REALM\" (main, remix or wrathpp)" >&2
		exit 2
		;;
	esac
	R_SERVER="$SERVER"
	COMPAT="$SERVER/lib/libandroidcompat.so"
}

# Refuses (exits) unless a database is one of the realm's own three; for Wrath++, also unless its
# name ends in _wrathpp. Every command that drops or rewrites a realm database asks first.
realm_database() {
	case "$1" in
	"$R_WORLD" | "$R_CHARACTERS" | "$R_BOTS") ;;
	*)
		echo "Refused: $1 isn't one of realm $REALM's databases" >&2
		exit 3
		;;
	esac
	if [ "$REALM" = wrathpp ]; then
		case "$1" in
		*_wrathpp) ;;
		*)
			echo "Refused: $1 isn't a Wrath++ database" >&2
			exit 3
			;;
		esac
	fi
}

# Wrath++ only: refuses (exits) if its own server build isn't installed, or if its game folder is
# the shared one or reaches it (a link), so that nothing it writes lands in the other realms' game.
wrathpp_guard() {
	[ "$REALM" = wrathpp ] || return 0
	if [ ! -x "$WRATHPP_SERVER/bin/worldserver" ]; then
		echo "Wrath++'s server isn't installed ($WRATHPP_SERVER)" >&2
		exit 4
	fi
	if [ -e "$WRATHPP_CLIENT" ]; then
		if [ -L "$WRATHPP_CLIENT" ] || [ -L "$WRATHPP_CLIENT/Data" ]; then
			echo "Refused: $WRATHPP_CLIENT (or its Data) is a link" >&2
			exit 4
		fi
		if [ -d "$FILES/client/Data" ] && [ "$(cd "$WRATHPP_CLIENT/Data" 2> /dev/null && pwd -P)" = "$(cd "$FILES/client/Data" && pwd -P)" ]; then
			echo "Refused: $WRATHPP_CLIENT/Data is the shared game's Data" >&2
			exit 4
		fi
	fi
}

# Sets every `Prefix<anything> = ...` line of a config file to the value.
setall() {
	file=$1 prefix=$2 value=$3
	sed -i "s|^\($prefix[A-Za-z0-9_.]*\)[[:space:]]*=.*|\1 = $value|" "$file"
}

configure() {
	mkdir -p "$DATA" "$RUN/tmp"
	configure_realm main
	configure_realm remix
	# Wrath++ only once its own server is installed (nothing of it is made before).
	[ ! -x "$WRATHPP_SERVER/bin/worldserver" ] || configure_realm wrathpp
	realm main
	setkey "$ETC/authserver.conf" PidFile "\"$RUN/authserver.pid\""
	cp "$SERVER/etc/mmaps-config.yaml" "$ETC/mmaps-config.yaml"
}

configure_realm() {
	realm "$1"
	wrathpp_guard
	mkdir -p "$R_ETC/modules" "$R_LOGS" "$R_RUN/tmp"
	# The auth server is the main realm's (one for both).
	names="worldserver dbimport"
	[ "$REALM" != main ] || names="$names authserver"
	for name in $names; do
		conf="$R_ETC/$name.conf"
		new=
		config_from_dist "$SERVER/etc/$name.conf.dist" "$conf" && new=1
		setkey "$conf" LogsDir "\"$R_LOGS\""
		setkey "$conf" TempDir "\"$R_RUN/tmp\""
		setkey "$conf" SourceDirectory "\"$SERVER/src\""
		setkey "$conf" MySQLExecutable "\"$SERVER/bin/mariadb\""
		setkey "$conf" LoginDatabaseInfo "$(dbinfo acore_auth)"
		setkey "$conf" Updates.AutoSetup 1
		if [ "$name" = worldserver ] && [ -n "$new" ] && [ "$REALM" = remix ]; then
			remix_defaults "$conf"
		fi
	done
	for name in worldserver dbimport; do
		conf="$R_ETC/$name.conf"
		setkey "$conf" WorldDatabaseInfo "$(dbinfo "$R_WORLD")"
		setkey "$conf" CharacterDatabaseInfo "$(dbinfo "$R_CHARACTERS")"
	done
	setkey "$R_ETC/dbimport.conf" Updates.EnableDatabases 7
	setkey "$R_ETC/worldserver.conf" DataDir "\"$DATA\""
	setkey "$R_ETC/worldserver.conf" PidFile "\"$R_RUN/worldserver.pid\""
	setkey "$R_ETC/worldserver.conf" RealmID "$R_ID"
	setkey "$R_ETC/worldserver.conf" WorldServerPort "$R_PORT"
	# Spells learned at creation from playercreateinfo_spell_custom (the Skyborne's racials; the core's
	# own table is empty): off by default in the core, which then teaches none.
	setkey "$R_ETC/worldserver.conf" PlayerStart.CustomSpells 1
	for dist in "$SERVER"/etc/modules/*.conf.dist; do
		conf="$R_ETC/modules/$(basename "$dist" .dist)"
		if config_from_dist "$dist" "$conf" && [ "$REALM" = remix ]; then
			remix_module_defaults "$conf"
		fi
	done
	# ALE (mod-ale) reads the Lua scripts the package has (its own, and Lua modules picked in the app).
	if [ -f "$R_ETC/modules/mod_ale.conf" ]; then
		setkey "$R_ETC/modules/mod_ale.conf" ALE.ScriptPath "\"$SERVER/lua_scripts\""
	fi
	if [ -f "$R_ETC/modules/playerbots.conf" ]; then
		setkey "$R_ETC/modules/playerbots.conf" PlayerbotsDatabaseInfo "$(dbinfo "$R_BOTS")"
	fi
	# What makes each realm what it is, every time: Wrath Remix's module on in its realm alone,
	# and Remix's world as Wrath left it (no progression brackets, nothing stopped at 19).
	remix_conf="$R_ETC/modules/mod_wrath_remix.conf"
	if [ -f "$remix_conf" ]; then
		if [ "$REALM" = remix ]; then
			setkey "$remix_conf" WrathRemix.Enable 1
			setkey "$remix_conf" WrathRemix.RealmID "$R_ID"
			remix_bronze_rates "$remix_conf"
		else
			setkey "$remix_conf" WrathRemix.Enable 0
		fi
	fi
	# The allied races (mod-allied-races) are ChromieCraft's alone: off on Wrath Remix's realm, where
	# the module takes its patch out of the game (and realm_sql keeps its SQL out of the databases).
	allied_conf="$R_ETC/modules/mod_allied_races.conf"
	if [ -f "$allied_conf" ]; then
		if [ "$REALM" != main ]; then
			setkey "$allied_conf" AlliedRaces.Enable 0
		else
			setkey "$allied_conf" AlliedRaces.Enable 1
		fi
	fi
	# The Worgen and Goblins (mod-worgen-goblin, from mod-worgoblin) likewise; and mod-worgoblin's
	# message at every login ("This server is running the Worgoblin module") is off.
	worgen_conf="$R_ETC/modules/mod_worgen_goblin.conf"
	if [ -f "$worgen_conf" ]; then
		if [ "$REALM" != main ]; then
			setkey "$worgen_conf" WorgenGoblin.Enable 0
		else
			setkey "$worgen_conf" WorgenGoblin.Enable 1
			# Their starting areas on (the module takes them in only with their package, which the
			# app downloads): set once, as a realm made before they could be turned on has them off
			# (a later choice of off is kept).
			if [ ! -f "$R_ETC/modules/.worgen_goblin_zones" ]; then
				setkey "$worgen_conf" WorgenGoblin.StartingAreas 1
				: > "$R_ETC/modules/.worgen_goblin_zones"
			fi
		fi
	fi
	[ ! -f "$R_ETC/modules/mod_worgoblin.conf" ] || setkey "$R_ETC/modules/mod_worgoblin.conf" Announce.enable false
	# Level scaling (mod-level-scaling, each character's choice at their class trainer) is
	# ChromieCraft's: Wrath Remix has its own Northrend at your level.
	level_scaling_conf="$R_ETC/modules/mod_level_scaling.conf"
	if [ -f "$level_scaling_conf" ]; then
		if [ "$REALM" != main ]; then
			setkey "$level_scaling_conf" LevelScaling.Enable 0
		else
			setkey "$level_scaling_conf" LevelScaling.Enable 1
		fi
	fi
	# The Murlocs and the Naga (mod-murloc-naga) are ChromieCraft's alone: off on Wrath Remix's realm,
	# where the module sets its patch aside out of the game (and realm_sql keeps its SQL out).
	murloc_naga_conf="$R_ETC/modules/mod_murloc_naga.conf"
	if [ -f "$murloc_naga_conf" ]; then
		if [ "$REALM" != main ]; then
			setkey "$murloc_naga_conf" MurlocNaga.Enable 0
		else
			setkey "$murloc_naga_conf" MurlocNaga.Enable 1
		fi
	fi
	# A home in Brill (mod-brill-home: the house, its quests and furniture) is ChromieCraft's alone.
	brill_home_conf="$R_ETC/modules/mod_brill_home.conf"
	if [ -f "$brill_home_conf" ]; then
		if [ "$REALM" != main ]; then
			setkey "$brill_home_conf" BrillHome.Enable 0
		else
			setkey "$brill_home_conf" BrillHome.Enable 1
		fi
	fi
	# Quest drops (mod-quest-drops: rare quest items, and epics in dungeons and from rare spawns, drop
	# more often) on in both realms, set once (a later choice of off is kept: README, Drop rates).
	quest_drops_conf="$R_ETC/modules/mod_quest_drops.conf"
	if [ -f "$quest_drops_conf" ] && [ ! -f "$R_ETC/modules/.quest_drops_on" ]; then
		setkey "$quest_drops_conf" QuestDrops.Enable 1
		: > "$R_ETC/modules/.quest_drops_on"
	fi
	# Wrath++'s module on in its realm alone, told its realm (it also refuses databases not its own).
	wrathpp_conf="$R_ETC/modules/mod_wrathpp_customization.conf"
	if [ -f "$wrathpp_conf" ]; then
		if [ "$REALM" = wrathpp ]; then
			setkey "$wrathpp_conf" Wrathpp.Enable 1
			setkey "$wrathpp_conf" Wrathpp.RealmID "$R_ID"
		else
			setkey "$wrathpp_conf" Wrathpp.Enable 0
		fi
	fi
	if [ "$REALM" = remix ]; then
		[ ! -f "$R_ETC/modules/progression_system.conf" ] ||
			setall "$R_ETC/modules/progression_system.conf" ProgressionSystem.Bracket_ 0
		[ ! -f "$R_ETC/modules/chromie-xp.conf" ] ||
			setkey "$R_ETC/modules/chromie-xp.conf" Chromie.Stable.MaxPlayerLevel 80
	fi
}

# Wrath Remix's world server, the first time its config is made (the user's changes stay after):
# Timerunners start at 10 (death knights at their own 55), quests give three times the experience
# and kills twice, and no race's intro plays (they start with Moratari, not at home).
remix_defaults() {
	setkey "$1" StartPlayerLevel 10
	setkey "$1" Rate.XP.Quest 3
	setkey "$1" Rate.XP.Kill 2
	setkey "$1" SkipCinematics 2
}

# Bronze is earned in Legion Remix's amounts: twenty times what it was since build 66, and since
# the story's end eight times that again, enough by the end to buy everything the Bazaar sells a
# class. Each rate still at one of its old defaults takes its new one; one the user changed stays.
remix_bronze_rates() {
	for rate in Quest:25,500:4000 Kill:1,15:75 Elite:4,60:300 Rare:20,500:3000 DungeonBoss:40,1000:6000 RaidBoss:150,5000:30000; do
		key=WrathRemix.Bronze.${rate%%:*} olds=${rate#*:} olds=${olds%:*} new=${rate##*:}
		for old in $(echo "$olds" | tr ',' ' '); do
			! grep -q "^$key[[:space:]]*=[[:space:]]*$old[[:space:]]*$" "$1" || setkey "$1" "$key" "$new"
		done
	done
}

# Wrath Remix's module configs, the first time: as the main realm's first start sets them (50
# random bots, idle while nobody plays), and the dungeons' and raids' own damage and health
# (mod-zone-difficulty's ChromieCraft tuning) off, since Remix sets its own.
remix_module_defaults() {
	case "$(basename "$1")" in
	playerbots.conf)
		setkey "$1" Playerbots.MinRandomBots 50
		setkey "$1" Playerbots.MaxRandomBots 50
		setkey "$1" Playerbots.DisabledWithoutRealPlayer 1
		;;
	mod-zone-difficulty.conf)
		setkey "$1" ModZoneDifficulty.Enable 0
		;;
	esac
}

# The server's programs (musl) run with libandroidcompat preloaded: it makes the system calls
# Android doesn't allow apps with ones it does. Only for them: Android's own programs (sed, cp, the
# shell) can't load it.
COMPAT="$SERVER/lib/libandroidcompat.so"
musl_programs() {
	export LD_PRELOAD="$COMPAT${1:+:$1}"
}

db_client() {
	LD_PRELOAD="$COMPAT" "$SERVER/bin/mariadb" --no-defaults -h127.0.0.1 -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$@"
}

# The realm's world database as dbimport makes it, without anything added since (custom races,
# modules taken out). realm() first.
rebuild_world() {
	realm_database "$R_WORLD"
	echo "Making the world database again"
	printf 'DROP DATABASE IF EXISTS `%s`;\nCREATE DATABASE `%s` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n' \
		"$R_WORLD" "$R_WORLD" | db_client
	run_dbimport
}

# dbimport for the realm (realm() first): the auth database and the realm's own two.
run_dbimport() {
	(cd "$R_RUN" && musl_programs && WOW_MODULES_CONF_DIR="$R_ETC/modules" "$SERVER/bin/dbimport" -c "$R_ETC/dbimport.conf")
	realm_sql
}

# SQL for one realm alone, in module folders the servers don't look in on their own: the realm's
# databases' update lists name them, so it goes into that realm's and never the other's. Run after
# dbimport (which makes the lists); the world server applies it as it starts.
# - Wrath Remix's own (its NPCs, quests, hub and the changes to the world it makes): mod-wrath-remix's
#   data/sql/remix, into the Remix databases.
# - The allied races' (mod-allied-races, ChromieCraft's alone): data/sql/chromiecraft, into
#   ChromieCraft's world database; and data/sql/remix, which takes earlier releases' rows of theirs
#   out of Remix's.
# - The Worgen's and Goblins' (mod-worgen-goblin: mod-worgoblin's own SQL, which the package puts
#   there in place of the module's data/sql), into ChromieCraft's world database.
# - WoW: Forever's new quests (mod-forever-quests, ChromieCraft's alone): data/sql/chromiecraft.
# - A home in Brill (mod-brill-home, ChromieCraft's alone): data/sql/chromiecraft, its world and
#   characters databases.
# - The Murlocs and the Naga (mod-murloc-naga, ChromieCraft's alone): data/sql/chromiecraft, last (its
#   rows OR its races' bits into the rows the other race modules' SQL puts in).
realm_sql() {
	if [ "$REALM" = wrathpp ]; then
		# Wrath++ takes nothing of the other realms' own SQL (its module's is in its db-* folders).
		set --
	elif [ "$REALM" = remix ]; then
		set -- "mod-wrath-remix/data/sql/remix/world acore_world_remix" "mod-wrath-remix/data/sql/remix/characters acore_characters_remix" \
			"mod-allied-races/data/sql/remix/world acore_world_remix"
	else
		set -- "mod-allied-races/data/sql/chromiecraft/world acore_world" "mod-worgen-goblin/data/sql/chromiecraft/world acore_world" \
			"mod-forever-quests/data/sql/chromiecraft/world acore_world" \
			"mod-brill-home/data/sql/chromiecraft/world acore_world" "mod-brill-home/data/sql/chromiecraft/characters acore_characters" \
			"mod-murloc-naga/data/sql/chromiecraft/world acore_world"
	fi
	for entry in "$@"; do
		folder=${entry% *} db=${entry##* }
		[ -d "$SERVER/src/modules/$folder" ] || continue
		realm_database "$db"
		dir="\$/modules/$folder"
		printf "DELETE FROM updates_include WHERE path = '%s';\nINSERT INTO updates_include (path, state) VALUES ('%s', 'CUSTOM');\n" \
			"$dir" "$dir" | db_client "$db"
	done
}

# The realms in the auth database: the game on this phone reaches them at 127.0.0.1, a PC's
# client on the Wi-Fi at the phone's address there ($1). Also clears each realm's "version
# mismatch" flag: a world server sets it while it starts and clears it once it's up, so one that
# stopped while loading leaves it set, and the auth server won't run if every realm is offline
# and flagged so.
realmlist() {
	address=${1:-127.0.0.1}
	for name in main remix; do
		realm "$name"
		printf "INSERT INTO realmlist (id, name, address, localAddress, localSubnetMask, port, icon, flag, timezone, allowedSecurityLevel, gamebuild)
VALUES (%s, '%s', '%s', '127.0.0.1', '255.255.255.0', %s, 0, 2, 1, 0, 12340)
ON DUPLICATE KEY UPDATE name = VALUES(name), address = VALUES(address), localAddress = VALUES(localAddress),
localSubnetMask = VALUES(localSubnetMask), port = VALUES(port), flag = flag & ~1;\n" \
			"$R_ID" "$R_NAME" "$address" "$R_PORT"
	done | db_client acore_auth
	echo "Realms: ChromieCraft and Wrath Remix at $address (127.0.0.1 here)"
}

# What's left of the custom races (versions 1.0.44 to 1.0.48 of the app had a Races switch; it's
# gone): their SQL in the world database (the table app_races says it's there) goes with the world
# database made again, and their files ($RACES, $DATA_RACES) go. Characters made with them stay in
# the characters database, left out of the character list (the core lists the races it knows).
races() {
	realm main
	applied=$(echo "SELECT version FROM app_races" | db_client --batch --skip-column-names acore_world 2> /dev/null || true)
	[ -z "$applied" ] || rebuild_world
	rm -rf "$DATA_RACES" "$RACES"
	setkey "$ETC/worldserver.conf" DataDir "\"$DATA\""
	echo "Custom races taken out"
}

# The modules in the realm package with SQL for the world database, a name a line: in the folders
# the servers read, and in the realm's own (realm_sql: data/sql/chromiecraft or data/sql/remix).
world_modules_now() {
	case "${REALM:-main}" in remix) own=remix ;; wrathpp) own=wrathpp ;; *) own=chromiecraft ;; esac
	for dir in "$SERVER"/src/modules/*/data/sql/db-world* "$SERVER"/src/modules/*/data/sql/$own/world; do
		[ -d "$dir" ] || continue
		dir=${dir#"$SERVER/src/modules/"}
		echo "${dir%%/*}"
	done | sort -u
}

# A realm swapped for one without a module (the app's Modules screen) leaves that module's SQL in
# the world database: its creatures, items, changes to the game's own. If a module whose SQL went
# in ($R_WORLD_MODULES, one record a realm) isn't in this realm package, the realm's world database
# is made again, and the package's modules put theirs in again as the world server starts. What
# modules keep in the characters database stays (the core keeps a module's applied files on
# record, so one put back finds it). realm() first.
modules() {
	now=$(world_modules_now)
	gone=
	if [ -f "$R_WORLD_MODULES" ]; then
		while read -r name; do
			[ -n "$name" ] || continue
			echo "$now" | grep -qxF "$name" || gone="$gone $name"
		done < "$R_WORLD_MODULES"
	fi
	if [ -n "$gone" ]; then
		echo "Taking out of the world:$gone"
		rebuild_world
	fi
	echo "$now" > "$R_WORLD_MODULES.new"
	mv "$R_WORLD_MODULES.new" "$R_WORLD_MODULES"
	echo "World database matches the realm's modules"
	module_data
	module_client
}

# A module that adds races or classes (mod-arac, mod-worgoblin) changes DBC files, which its README
# has copied over the server's (data/dbc). The world server reads $DATA_MODULES instead: links to
# the game's data, with the module's files in place of the game's of the same name (whatever its
# case). A realm without such modules reads $DATA. realm() first.
module_data() {
	if [ ! -d "$R_MODULE_FILES/dbc" ] || [ ! -d "$DATA/dbc" ]; then
		rm -rf "$R_DATA_MODULES"
		setkey "$R_ETC/worldserver.conf" DataDir "\"$DATA\""
		return
	fi
	rm -rf "$R_DATA_MODULES.new"
	mkdir -p "$R_DATA_MODULES.new/dbc"
	for entry in "$DATA"/*; do
		[ "${entry##*/}" = dbc ] || ln -s "$entry" "$R_DATA_MODULES.new/${entry##*/}"
	done
	for file in "$DATA"/dbc/*; do
		ln -s "$file" "$R_DATA_MODULES.new/dbc/${file##*/}"
	done
	count=0
	for file in "$R_MODULE_FILES"/dbc/*; do
		name=${file##*/}
		game=$(ls "$DATA/dbc" | grep -ixF -m1 "$name" || true)
		rm -f "$R_DATA_MODULES.new/dbc/${game:-$name}"
		ln -s "$file" "$R_DATA_MODULES.new/dbc/${game:-$name}"
		count=$((count + 1))
	done
	rm -rf "$R_DATA_MODULES"
	mv "$R_DATA_MODULES.new" "$R_DATA_MODULES"
	setkey "$R_ETC/worldserver.conf" DataDir "\"$R_DATA_MODULES\""
	echo "The world server reads $count DBC files of the realm's modules over the game's"
}

# The starting areas' maps in the world server's data (maps, vmaps, mmaps; and cameras, the race
# intros' camera flights, which the server follows to send the game what each passes): their files linked in
# (hard links, or copies where the phone's storage has none), never in place of a file that's there
# (a building's collision model the game's own data has already is the game's); a file the package
# has once for several names (a terrain swap's tiles that are its base map's) under each of them
# (server/same.txt). Once a package: data/.zones says which is in.
zones_data() {
	[ -f "$ZONES/TAG" ] && [ -d "$ZONES/server/maps" ] && [ -d "$DATA/maps" ] || return 0
	tag=$(cat "$ZONES/TAG")
	[ "$(cat "$DATA/.zones" 2> /dev/null)" != "$tag" ] || return 0
	count=0
	for part in maps vmaps mmaps cameras; do
		mkdir -p "$DATA/$part"
		# (the world server reads $DATA_MODULES' links to the data's folders when it's there)
		[ ! -d "$DATA_MODULES" ] || [ -e "$DATA_MODULES/$part" ] || ln -s "$DATA/$part" "$DATA_MODULES/$part"
		for file in "$ZONES/server/$part"/*; do
			[ -f "$file" ] || continue
			dest="$DATA/$part/${file##*/}"
			[ -e "$dest" ] && continue
			ln "$file" "$dest" 2> /dev/null || cp "$file" "$dest"
			count=$((count + 1))
		done
	done
	if [ -f "$ZONES/server/same.txt" ]; then
		while IFS="$(printf '\t')" read -r name kept; do
			[ -n "$name" ] && [ ! -e "$DATA/$name" ] || continue
			ln "$ZONES/server/$kept" "$DATA/$name" 2> /dev/null || cp "$ZONES/server/$kept" "$DATA/$name"
			count=$((count + 1))
		done < "$ZONES/server/same.txt"
	fi
	echo "$tag" > "$DATA/.zones"
	echo "The starting areas' maps are in the world server's data ($count files)"
}

# The modules' patch for the game (their models, interface, the DBC files above) goes in the game's
# Data as patch-M.MPQ, a folder the game reads like an archive; a realm without one takes it out.
# realm-modules.stamp in it says which it is, so it's copied again only when the realm's changes
# (hard links where the phone's storage allows, so it isn't stored twice). A patch-M.MPQ of the
# user's own is left alone.
module_client() {
	wrathpp_guard
	data="$R_CLIENT/Data"
	patch="$data/patch-M.MPQ"
	mark="$patch/realm-modules.stamp"
	[ -d "$data" ] || return 0
	if [ -f "$R_MODULE_FILES/client.stamp" ]; then
		! cmp -s "$R_MODULE_FILES/client.stamp" "$mark" 2> /dev/null || return 0
		if [ -e "$patch" ] && [ ! -f "$mark" ]; then
			echo "The game has a Data/patch-M.MPQ of its own: the modules' files for the game aren't put in"
			return 0
		fi
		echo "Putting the realm's modules' files in the game (Data/patch-M.MPQ)"
		rm -rf "$patch" "$patch.new"
		cp -rl "$R_MODULE_FILES/client" "$patch.new" 2> /dev/null || { rm -rf "$patch.new"; cp -r "$R_MODULE_FILES/client" "$patch.new"; }
		cp "$R_MODULE_FILES/client.stamp" "$patch.new/realm-modules.stamp"
		mv "$patch.new" "$patch"
	elif [ -f "$mark" ]; then
		echo "Taking the modules' files out of the game (Data/patch-M.MPQ)"
		rm -rf "$patch"
	fi
}

# Whether a Wrath++ game file may be the shared game's own (a hard link): an archive (.MPQ) that
# is not a patch the realms' modules write (patch-4, F, M, U, V, W, Y, Z) nor a marker beside one.
wrathpp_shareable() {
	name=$(basename "$1" | tr 'A-Z' 'a-z')
	case "$name" in
	patch-[4fmuvwyz].mpq | patch-[4fmuvwyz].mpq.*) return 1 ;;
	*.mpq) return 0 ;;
	*) return 1 ;;
	esac
}

# Wrath++: what it would use and write, and whether it stays apart from the other realms. Changes
# nothing; exits non-zero if a check fails.
wrathpp_check() {
	realm wrathpp
	failed=0
	echo "Wrath++ (realm $R_ID, port $R_PORT)"
	echo "  server   $R_SERVER $( [ -x "$R_SERVER/bin/worldserver" ] && echo installed || echo "not installed" )"
	echo "  configs  $R_ETC"
	echo "  logs     $R_LOGS"
	echo "  run      $R_RUN"
	echo "  game     $R_CLIENT $( [ -d "$R_CLIENT/Data" ] && echo present || echo absent )"
	echo "  data     $R_DATA_MODULES"
	echo "  dbs      $R_WORLD $R_CHARACTERS $R_BOTS"
	for db in "$R_WORLD" "$R_CHARACTERS" "$R_BOTS"; do
		(realm_database "$db") || failed=1
	done
	for path in "$R_ETC" "$R_LOGS" "$R_RUN" "$R_CLIENT" "$R_DATA_MODULES" "$R_SERVER"; do
		case "$path" in
		*wrathpp*) ;;
		*) echo "  FAIL $path isn't a Wrath++ path"; failed=1 ;;
		esac
	done
	for shared in "$ETC" "$FILES/etc-remix" "$FILES/client" "$DATA_MODULES" "$MAIN_SERVER"; do
		for path in "$R_ETC" "$R_CLIENT" "$R_DATA_MODULES" "$R_SERVER"; do
			[ "$path" != "$shared" ] || { echo "  FAIL $path is shared ($shared)"; failed=1; }
		done
	done
	if [ -e "$R_CLIENT" ]; then
		if [ -L "$R_CLIENT" ] || [ -L "$R_CLIENT/Data" ]; then
			echo "  FAIL $R_CLIENT or its Data is a link"; failed=1
		fi
		# A file of the Wrath++ game hard linked to the shared game's: a write would reach both. Only
		# the game's own archives may be shared that way (the app links them rather than copy gigabytes:
		# the game and the realm only ever read them); never a patch a realm module writes.
		if [ -d "$FILES/client/Data" ] && [ -d "$R_CLIENT/Data" ]; then
			shared_inodes=$(find "$FILES/client/Data" -maxdepth 2 -type f -exec stat -c '%d:%i' {} + 2> /dev/null | sort -u)
			for file in $(find "$R_CLIENT/Data" -maxdepth 2 -type f -links +1 2> /dev/null); do
				echo "$shared_inodes" | grep -qxF "$(stat -c '%d:%i' "$file")" || continue
				if wrathpp_shareable "$file"; then
					echo "  shared, read only: ${file#"$R_CLIENT/"}"
				else
					echo "  FAIL $file is the shared game's file (a hard link)"; failed=1
				fi
			done
		fi
	fi
	if [ "$failed" = 0 ]; then echo "Wrath++ checks passed"; else echo "Wrath++ checks FAILED" >&2; fi
	return "$failed"
}

# Wrath++ in the auth database's realm list: only its own row (id 5, named Wrath++). Refuses if id 5
# or port 8087 is another realm's. The list is saved first ($FILES/backups/wrathpp).
wrathpp_register() {
	realm wrathpp
	wrathpp_guard
	address=${1:-127.0.0.1}
	backup="$FILES/backups/wrathpp/realmlist-$(date +%Y%m%d%H%M%S).tsv"
	mkdir -p "${backup%/*}"
	echo "SELECT * FROM realmlist" | db_client --batch acore_auth > "$backup"
	other=$(printf "SELECT id FROM realmlist WHERE (id = %s AND name <> '%s') OR (port = %s AND id <> %s);\n" \
		"$R_ID" "$R_NAME" "$R_PORT" "$R_ID" | db_client --batch --skip-column-names acore_auth)
	if [ -n "$other" ]; then
		echo "Refused: realm id $R_ID or port $R_PORT is another realm's (ids: $other); realm list saved in $backup" >&2
		exit 5
	fi
	printf "INSERT INTO realmlist (id, name, address, localAddress, localSubnetMask, port, icon, flag, timezone, allowedSecurityLevel, gamebuild)
VALUES (%s, '%s', '%s', '127.0.0.1', '255.255.255.0', %s, 0, 2, 1, 0, 12340)
ON DUPLICATE KEY UPDATE address = VALUES(address), flag = flag & ~1;\n" "$R_ID" "$R_NAME" "$address" "$R_PORT" | db_client acore_auth
	echo "Wrath++ is in the realm list at $address (the list before: $backup)"
}

wrathpp_unregister() {
	realm wrathpp
	printf "DELETE FROM realmlist WHERE id = %s AND name = '%s';\n" "$R_ID" "$R_NAME" | db_client acore_auth
	echo "Wrath++ is out of the realm list"
}

cmd=${1:-}
[ $# -gt 0 ] && shift
case "$cmd" in
configure)
	configure
	;;
configure-realm)
	configure_realm "${1:-main}"
	;;
db)
	mkdir -p "$RUN/tmp" "$LOGS"
	if [ ! -d "$DB_DIR/mysql" ]; then
		rm -rf "$DB_DIR.new"
		cp -r "$SERVER/mariadb-seed" "$DB_DIR.new"
		rm -rf "$DB_DIR"
		mv "$DB_DIR.new" "$DB_DIR"
	fi
	# MariaDB refuses to run as root unless told to (only on a test machine: never on a phone).
	[ "$(id -u)" = 0 ] && set -- --user=root "$@"
	musl_programs
	# Android's app sandbox blocks io_uring, so InnoDB does its own asynchronous I/O.
	exec "$SERVER/bin/mariadbd" --no-defaults --datadir="$DB_DIR" --basedir="$SERVER" \
		--lc-messages-dir="$SERVER/share/mariadb" --character-sets-dir="$SERVER/share/mariadb/charsets" \
		--plugin-dir="$SERVER/lib/mariadb-plugins" --tmpdir="$RUN/tmp" \
		--socket="$RUN/mysqld.sock" --pid-file="$RUN/mysqld.pid" \
		--bind-address=127.0.0.1 --port="$DB_PORT" --skip-name-resolve \
		--innodb-use-native-aio=0 --innodb-log-file-size=48M --innodb-buffer-pool-size=256M \
		--max-allowed-packet=64M --log-error="$LOGS/mariadb.log" "$@"
	;;
db-ping)
	musl_programs
	exec "$SERVER/bin/mariadb-admin" --no-defaults -h127.0.0.1 -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" \
		--connect-timeout=2 ping
	;;
db-stop)
	musl_programs
	exec "$SERVER/bin/mariadb-admin" --no-defaults -h127.0.0.1 -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" \
		shutdown
	;;
sql)
	db_client --batch --skip-column-names ${1:+"$1"}
	;;
races)
	races
	;;
modules)
	realm "${1:-main}"
	wrathpp_guard
	modules
	;;
dbimport)
	realm "${1:-main}"
	# The Remix databases are made here the first time (the seed has the main realm's).
	wrathpp_guard
	if [ "$REALM" != main ]; then
		for db in "$R_WORLD" "$R_CHARACTERS" "$R_BOTS"; do
			realm_database "$db"
			printf 'CREATE DATABASE IF NOT EXISTS `%s` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n' "$db"
		done | db_client
	fi
	run_dbimport
	;;
realmlist)
	realmlist "${1:-}"
	;;
wrathpp-check)
	wrathpp_check
	;;
wrathpp-register)
	wrathpp_register "${1:-}"
	;;
wrathpp-unregister)
	wrathpp_unregister
	;;
auth)
	cd "$RUN"
	musl_programs
	exec "$SERVER/bin/authserver" -c "$ETC/authserver.conf"
	;;
world)
	realm "${1:-main}"
	wrathpp_guard
	realm_sql
	[ "$REALM" != main ] || zones_data
	mkdir -p "$R_LOGS" "$R_RUN"
	cd "$R_RUN"
	# jemalloc in place of musl's malloc, which is slow for the world server's many threads.
	musl_programs "$SERVER/lib/libjemalloc.so.2"
	# Whether the phone's player just selected an enemy, for the app's touch controls
	# (patches/azerothcore/0007).
	export WOW_SELECTION_FILE="$R_RUN/selection"
	# Whether a cutscene plays for the phone's player: a hold skips it (patches/azerothcore/0008).
	export WOW_CUTSCENE_FILE="$R_RUN/cutscene"
	# Where the app's add-on says the spellbook is: a drag there drags its icons (patches/azerothcore/0009).
	export WOW_INTERFACE_FILE="$R_RUN/interface"
	# Where Wrath Remix writes the reports its Report Time Anomaly asks for, for the app to send to
	# GitHub (mod-wrath-remix, RemixReport.cpp).
	export WOW_REPORTS_DIR="$R_RUN/reports"
	# Where a Wrath Remix Timerunner going home is written for ChromieCraft's world server to take
	# in (mod-wrath-remix, RemixEnding.cpp; the app restarts the server there: Homecomings.kt).
	export WOW_TRANSFERS_DIR="$R_RUN/transfers"
	# The realm's own module configs (patches/azerothcore/0010).
	export WOW_MODULES_CONF_DIR="$R_ETC/modules"
	# The game's folder: Wrath Remix writes its patch there as it starts (Bronze and its prices,
	# Data/patch-Y.MPQ) and ChromieCraft's world server takes it out (mod-wrath-remix).
	# (Wrath++'s own game folder for Wrath++: its modules' patches never reach the shared one.)
	export WOW_CLIENT_DIR="$R_CLIENT"
	# The Worgen's and Goblins' starting areas (mod-worgen-goblin), ChromieCraft's alone.
	if [ "$REALM" = main ] && [ -f "$ZONES/client/files.txt" ]; then
		export WOW_ZONES_DIR="$ZONES"
	fi
	exec "$SERVER/bin/worldserver" -c "$R_ETC/worldserver.conf"
	;;
maps)
	# dbc, Cameras and maps, from the client's Data folder.
	mkdir -p "$DATA.work" && cd "$DATA.work"
	musl_programs
	exec "$SERVER/bin/map_extractor" -i "$1" -o "$DATA.work"
	;;
vmaps)
	mkdir -p "$DATA.work/vmaps" && cd "$DATA.work"
	musl_programs
	"$SERVER/bin/vmap4_extractor" -d "$1/Data/"
	exec "$SERVER/bin/vmap4_assembler" Buildings vmaps
	;;
mmaps)
	# Pathfinding, from maps and vmaps (the slow one).
	cd "$DATA.work"
	musl_programs
	exec "$SERVER/bin/mmaps_generator" --config "$ETC/mmaps-config.yaml" ${1:+--threads "$1"}
	;;
*)
	sed -n '/^set -eu/q;2,$p' "$0" >&2
	exit 2
	;;
esac
