#!/usr/bin/env bash
# Tests the World of Warcraft app's server package (warcraft/android/server/server.tar.xz) the way
# the phone runs it: unpacked into /data/data/com.logie.warcraft/files, driven by its ctl.sh, on a
# Linux machine of the same architecture that has no musl of its own (so the package has to bring
# everything it needs).
#
#   1. MariaDB starts from the seed data folder.
#   2. dbimport creates and fills the auth, characters and world databases.
#   3. The auth server starts; an account made the way the app makes them logs in and gets the
#      realm list, with the realm's address.
#   4. The world server, on jemalloc, loads its configs and modules and updates the databases
#      (the first ChromieCraft progression brackets, the playerbots module's own database).
#      With the server's data (WOW_DATA_ZIP: the data.zip the app downloads, see
#      warcraft/server-data.env), it starts all the way, a character is created and enters the
#      world, a GM command answers, and the server shuts down the way the app stops it.
#      Without it, it stops where it needs the data (dbc).
#      The app's add-on message (where the spellbook is) is kept for the app, and cleared at the
#      logout.
#   5. What earlier versions' custom races left (their SQL in the world database, their files, a
#      character of one of them) is taken out the way the realm's start does it (ctl.sh races):
#      the world database is made again, the files go, the world server starts, and the
#      character is left out of the character list but kept. A module that was in the realm and
#      isn't now (ctl.sh modules) takes what it put in the world database with it, and the
#      realm's modules put theirs in again.
#   6. Wrath Remix, the second realm: its databases are made, its world server starts with the
#      mod-wrath-remix module on (the ChromieCraft realm's said it was off), its SQL is in its
#      databases and not in ChromieCraft's, both realms are in the realm list, and a new
#      character there is a level 10 Timerunner at the Infinite Bazaar who plays the prologue
#      (warcraft/server/remix_prologue.steps) to the first chapter, with Northrend's creatures at
#      its levels, and has its class's starter kit on, its abilities learned and its weapon skill
#      at its level's maximum; Moratari walks with a Timerunner in the Borean Tundra, fights
#      beside them, steps away to her post and waits when asked (remix_companion.steps); buys from the Bazaar's Bronze vendors' windows (Bronze an item, a
#      price an ItemExtendedCost of Bronze); every NPC Remix placed stands on the floor
#      (remix_check.py floors); the realm writes the game's patch with Bronze's rows
#      (remix_check.py patch) and ChromieCraft's world server takes it out; the realm's bots
#      leave where characters are made for their chapters. The campaign from Chapter II to the end is
#      played on each side (warcraft/server/remix_campaign_*.steps): the story's quests and scenes,
#      Eternus's agents and her last hour, the return to the Bazaar and the goodbyes; both
#      Timerunners go home, and ChromieCraft's world server takes them in, in their capitals.
#   7. The auth server starts again the way the app starts it, and the account logs in.
#   8. With strace, no server program made a system call Android's seccomp policy forbids apps.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILES=/data/data/com.logie.warcraft/files
PKG="$ROOT/warcraft/android/server/server.tar.xz"
SUDO=""
[ "$(id -u)" = 0 ] || SUDO=sudo

# Server programs left from an earlier run would hold the ports.
$SUDO pkill -f "$FILES/server/bin/" 2> /dev/null && sleep 5 || true
$SUDO rm -rf "$FILES"
$SUDO mkdir -p "$FILES"
$SUDO chown "$(id -u):$(id -g)" "$FILES"
tar -C "$FILES" -xJf "$PKG"
cat "$FILES/server/VERSION"
export FILES
DATA_ZIP="${WOW_DATA_ZIP:-}"
if [ -n "$DATA_ZIP" ]; then
	echo "== server data"
	unzip -q "$DATA_ZIP" -d "$FILES/data"
	du -sh "$FILES"/data/*
fi

# Android kills an app's process that makes a system call its seccomp policy doesn't allow (the
# server runs as the app). With strace, every server program here runs under a filter that stops
# only on such calls, and the test fails if one is made.
TRACE=()
if command -v strace > /dev/null; then
	filter=$(python3 -I "$ROOT/warcraft/server/seccomp_check.py" filter)
	TRACE=(strace -f --seccomp-bpf -qq -e signal=none -e "trace=$filter")
	mkdir -p "$FILES/logs/syscalls"
else
	echo "No strace: the system calls aren't checked against Android's policy."
fi
CTL() {
	if [ ${#TRACE[@]} -gt 0 ]; then
		"${TRACE[@]}" -o "$FILES/logs/syscalls/$1.$BASHPID.$RANDOM" sh "$FILES/server/ctl.sh" "$@"
	else
		sh "$FILES/server/ctl.sh" "$@"
	fi
}

pids=()
cleanup() {
	for pid in "${pids[@]}"; do kill "$pid" 2> /dev/null || true; done
	pkill -f "$FILES/server/bin/" 2> /dev/null || true
	wait 2> /dev/null || true
}
trap cleanup EXIT
# A character's side's language (Common 98, Orcish 109) in its skills; when it isn't there, what the
# realm holds about it is shown before the test fails.
knows_language() {
	local name=$1 language=$2 known
	known=$(echo "SELECT COUNT(*) FROM character_skills s JOIN characters c ON c.guid = s.guid WHERE c.name = '$name' AND s.skill = $language" | CTL sql acore_characters)
	[ "$known" = 1 ] && return 0
	{
		echo "--- $name's skills; Testhero's (a human's) languages"
		echo "SELECT c.name, c.race, c.class, s.skill, s.value, s.max FROM character_skills s JOIN characters c ON c.guid = s.guid WHERE c.name IN ('$name', 'Testhero') ORDER BY c.name, s.skill" | CTL sql acore_characters
		echo "--- the world's language rows"
		echo "SELECT * FROM skillraceclassinfo_dbc WHERE SkillID IN (98, 109)" | CTL sql acore_world
		echo "SELECT * FROM playercreateinfo_skills WHERE skill IN (98, 109)" | CTL sql acore_world
		echo "--- the realm's words on skills"
		grep -ihE "skill|race/class" "$FILES/logs/world.out" "$FILES/logs/Server.log" "$FILES/logs/Errors.log" 2>/dev/null | grep -v "ListSpellsAction" | head -20 || true
		echo "--- a GM command from $name (needs the language)"
		printf 'cmd .gps\n' > "$FILES/run/language.steps"
		# (said in the language it should know: the race given only picks it, the character is there)
		python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 "$name" "$([ "$language" = 109 ] && echo 2 || echo 1)" 1 \
			"$FILES/run/language.steps" || true
	} >&2
	return 1
}

fail() {
	echo "FAILED: $*" >&2
	for log in "$FILES"/logs/*; do
		[ -f "$log" ] || continue
		echo "--- $log" >&2
		tail -40 "$log" >&2
	done
	exit 1
}
wait_for() { # seconds, description, command...
	local seconds=$1 what=$2
	shift 2
	for _ in $(seq "$seconds"); do
		"$@" > /dev/null 2>&1 && return 0
		sleep 1
	done
	fail "$what"
}

echo "== configure"
CTL configure
ls "$FILES/etc" "$FILES/etc/modules"
# The app's first-run settings (Server.applySettings): the first ChromieCraft brackets, and 50
# random bots that only play while someone's logged in.
sed -i 's/^ProgressionSystem.Bracket_0 .*/ProgressionSystem.Bracket_0 = 1/; s/^ProgressionSystem.Bracket_1_19 .*/ProgressionSystem.Bracket_1_19 = 1/' \
	"$FILES/etc/modules/progression_system.conf"
sed -i 's/^Playerbots.MinRandomBots .*/Playerbots.MinRandomBots = 50/; s/^Playerbots.MaxRandomBots .*/Playerbots.MaxRandomBots = 50/; s/^Playerbots.DisabledWithoutRealPlayer .*/Playerbots.DisabledWithoutRealPlayer = 1/' \
	"$FILES/etc/modules/playerbots.conf"
grep -E "^Playerbots.(MinRandomBots|MaxRandomBots|DisabledWithoutRealPlayer) " "$FILES/etc/modules/playerbots.conf"

echo "== MariaDB"
CTL db & pids+=($!)
wait_for 60 "MariaDB didn't start" CTL db-ping
echo "MariaDB is up"

echo "== dbimport"
start=$(date +%s)
CTL dbimport > "$FILES/logs/dbimport.out" 2>&1 || fail "dbimport exited with $?"
echo "dbimport took $(($(date +%s) - start)) s"
# (acore_playerbots is filled by the playerbots module when the world server starts: checked there.)
for db in acore_auth acore_characters acore_world; do
	tables=$(echo "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$db'" | CTL sql)
	echo "$db: $tables tables"
	[ "$tables" -gt 0 ] || fail "$db has no tables"
done
creatures=$(echo "SELECT COUNT(*) FROM creature_template" | CTL sql acore_world)
echo "creature_template: $creatures rows"
[ "$creatures" -gt 20000 ] || fail "the world database looks empty"

echo "== the realm's modules on record for the world database (ctl.sh modules, as each start runs it)"
# A game folder for the modules' patch and Wrath Remix's (the phone has the client there; CI only
# the folder).
mkdir -p "$FILES/client/Data"
CTL modules > "$FILES/logs/modules.out" 2>&1 || fail "ctl.sh modules failed: $(tail -5 "$FILES/logs/modules.out")"
cat "$FILES/logs/modules.out"
grep -qxF mod-zone-difficulty "$FILES/mysql/.world-modules" || fail "the realm's modules aren't on record"
if grep -q "Taking out" "$FILES/logs/modules.out"; then fail "the first start made the world database again"; fi
# Modules the app's user picked that change the game's DBC files (scripts/module-files.py): the
# world server reads theirs over the game's, and their patch is in the game.
if [ -d "$FILES/server/share/dbc" ]; then
	cat "$FILES/server/share/module-files.txt"
	grep -q "^DataDir = \"$FILES/data-modules\"" "$FILES/etc/worldserver.conf" || fail "the world server doesn't read the modules' DBC files"
	for file in "$FILES"/server/share/dbc/*; do
		[ "$(ls "$FILES/data-modules/dbc" | grep -icxF "${file##*/}")" = 1 ] || fail "${file##*/} is in the server's data twice or not at all"
	done
	[ "$(ls "$FILES/data-modules/dbc" | wc -l)" -ge "$(ls "$FILES/data/dbc" | wc -l)" ] || fail "the modules' data lacks some of the game's DBC files"
	cmp -s "$FILES/server/share/client.stamp" "$FILES/client/Data/patch-M.MPQ/realm-modules.stamp" || fail "the modules' patch isn't in the game"
	CTL modules > "$FILES/logs/modules-same.out" 2>&1 || fail "ctl.sh modules failed the second time"
	if grep -q "Putting" "$FILES/logs/modules-same.out"; then fail "the modules' patch was copied again for nothing"; fi
	echo "The world server reads the modules' DBC files; their patch is in the game."
fi

echo "== auth server"
python3 "$ROOT/warcraft/server/auth_check.py" account-sql tester secret123 | CTL sql acore_auth
echo "UPDATE realmlist SET address = '192.168.1.50', localAddress = '127.0.0.1' WHERE id = 1" | CTL sql acore_auth
CTL auth > "$FILES/logs/auth.out" 2>&1 & pids+=($!)
port_open() { (echo > "/dev/tcp/127.0.0.1/$1") 2> /dev/null; }
wait_for 60 "the auth server didn't open port 3724" port_open 3724
realms=$(python3 "$ROOT/warcraft/server/auth_check.py" login 127.0.0.1 tester secret123) ||
	fail "the test account couldn't log in"
echo "$realms"
echo "$realms" | grep -q "127.0.0.1:8085" || fail "the realm list doesn't point the phone's own client at 127.0.0.1"
if python3 "$ROOT/warcraft/server/auth_check.py" login 127.0.0.1 tester wrongpass > /dev/null 2>&1; then
	fail "a wrong password logged in"
fi

echo "== world server"
start_world() { # log name [realm]
	world_log="$FILES/logs/$1"
	rm -f "$FILES/run/world.in"
	mkfifo "$FILES/run/world.in"
	CTL world ${2:-} < "$FILES/run/world.in" > "$world_log" 2>&1 & pids+=($!)
	world=$!
	# Its console: the app stops it with a command there.
	exec 3> "$FILES/run/world.in"
}
# Up to "ready", as the app waits for it (Server.READY).
wait_world_ready() {
	local start ready=""
	start=$(date +%s)
	for _ in $(seq 1800); do
		kill -0 "$world" 2> /dev/null || break
		[ -n "$jemalloc" ] || ! on_jemalloc || jemalloc=1
		if grep -q "(worldserver-daemon) ready" "$world_log"; then ready=1; break; fi
		sleep 1
	done
	if [ -z "$ready" ]; then
		# (how it ended: 0 is a shutdown, its console's end among them; 1 an error; over 128 a signal)
		if ! kill -0 "$world" 2> /dev/null; then
			wait "$world" 2> /dev/null && echo "The world server exited with 0." || echo "The world server exited with $?."
			ls -l "$FILES/run/world.in" /proc/$$/fd/3 2>&1 || true
		fi
		fail "the world server didn't start"
	fi
	echo "The world server was ready in $(($(date +%s) - start)) s."
}
stop_world() {
	echo "server shutdown 1" >&3
	for _ in $(seq 90); do kill -0 "$world" 2> /dev/null || break; sleep 1; done
	if kill -0 "$world" 2> /dev/null; then fail "the world server didn't shut down"; fi
	grep -q "Halting process" "$world_log" || fail "the world server didn't shut down cleanly"
	exec 3>&-
	tail -3 "$world_log"
	echo "The world server shut down."
}
# A character erased the way the realm erases one (its every row: Player::DeleteFromDB), from the
# world server's console, while it runs.
erase_character() {
	local name=$1 guid
	guid=$(echo "SELECT guid FROM characters WHERE name = '$name'" | CTL sql acore_characters)
	[ -n "$guid" ] || return 0
	echo "character erase $name" >&3
	for _ in $(seq 30); do
		if [ "$(echo "SELECT (SELECT COUNT(*) FROM characters WHERE guid = $guid) + (SELECT COUNT(*) FROM character_achievement_progress WHERE guid = $guid)" | CTL sql acore_characters)" = 0 ]; then
			return 0
		fi
		sleep 1
	done
	return 1
}
# A stand-in for the game the Skyborne's patch is made from (mod-skyborne): the server's tables as
# the game's language archive (a folder, which the module reads like one). No textures in it.
if [ -n "$DATA_ZIP" ]; then
	game="$FILES/client/Data/enUS/locale-enUS.MPQ"
	mkdir -p "$game/Interface/GlueXML"
	ln -s "$FILES/data/dbc" "$game/DBFilesClient"
	printf 'GlueParent.lua\r\nCharacterCreate.xml\r\n' > "$game/Interface/GlueXML/GlueXML.toc"
fi
start_world world.out
jemalloc=""
on_jemalloc() {
	local pid
	pid=$(cat "$FILES/run/worldserver.pid" 2> /dev/null || true)
	[ -n "$pid" ] && grep -q libjemalloc "/proc/$pid/maps" 2> /dev/null
}
check_modules() {
	[ -n "$jemalloc" ] || fail "the world server didn't run on jemalloc"
	echo "The world server ran on jemalloc."
	grep -q "Loading mod-progression-system updates" "$FILES/logs/world.out" || fail "the world server didn't load its modules"
	grep -qi "playerbots" "$FILES/logs/world.out" || fail "the world server doesn't mention playerbots"
	progression=$(echo "SELECT COUNT(*) FROM updates WHERE name LIKE '%progression%'" | CTL sql acore_world)
	echo "progression updates applied: $progression"
	[ "$progression" -gt 0 ] || fail "the progression brackets' SQL wasn't applied"
	tables=$(echo "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'acore_playerbots'" | CTL sql)
	echo "acore_playerbots: $tables tables (made by the playerbots module)"
	[ "$tables" -gt 0 ] || fail "the playerbots module didn't set up its database"
	# ALE (mod-ale), the Lua engine: on, reading the package's scripts.
	grep -q "^ALE.ScriptPath = \"$FILES/server/lua_scripts\"" "$FILES/etc/modules/mod_ale.conf" ||
		fail "ALE doesn't read the package's Lua scripts"
	[ -d "$FILES/server/lua_scripts" ] || fail "the package has no Lua scripts folder"
	grep -rh "\[ALE\]" "$FILES/logs" 2> /dev/null | head -3 || true
}

if [ -n "$DATA_ZIP" ]; then
	wait_world_ready
	grep -E "^(Loading|>>) .*(DBC|Maps|MMap|VMap|Creature Data|GameObject Data|Quest)" "$FILES/logs/world.out" | head -12 || true
	check_modules

	echo "== a character in the world"
	python3 "$ROOT/warcraft/server/auth_check.py" world 127.0.0.1 tester secret123 Testhero ".server info" |
		tee "$FILES/logs/world-client.out" || fail "the character couldn't get into the world"
	grep -q "in the world on map" "$FILES/logs/world-client.out" || fail "the character didn't enter the world"
	grep -qi "players online\|uptime" "$FILES/logs/world-client.out" || fail "the GM command didn't answer"
	characters=$(echo "SELECT COUNT(*) FROM characters" | CTL sql acore_characters)
	echo "characters: $characters (the test's, and the random bots')"
	# Data made for another version of the core (vmaps, mmaps) is refused when a map loads.
	if grep -iE "mmtile.*(generator|version|navmesh)|vmap.*(version|magic)" "$FILES/logs/world.out" | head -5 | grep .; then
		fail "the server data doesn't match this server"
	fi

	echo "== the app's add-on: where the spellbook is"
	python3 "$ROOT/warcraft/server/auth_check.py" world-note 127.0.0.1 tester secret123 Testhero "$FILES/run/interface" |
		tee "$FILES/logs/world-note.out" || fail "the realm didn't keep the add-on's note for the app"
	[ "$(cat "$FILES/run/interface")" = "-" ] || fail "the add-on's note stayed after the logout"
	echo "The realm kept the note, and cleared it at the logout."

	echo "== the Skyborne (mod-skyborne)"
	grep -E "Skyborne: The Skyborne's patch is in the game: 17 tables" "$FILES/logs/world.out" ||
		fail "the world server didn't make the Skyborne's patch"
	[ -s "$FILES/client/Data/patch-Z.MPQ" ] && [ -s "$FILES/client/Data/patch-Z.MPQ.skyborne" ] || fail "the Skyborne's patch isn't in the game"
	for race in 13 14; do
		[ "$(echo "SELECT Flags & 1 FROM chrraces_dbc WHERE ID = $race" | CTL sql acore_world)" = 0 ] || fail "race $race isn't playable"
	done
	# A warrior of the High Order in Northshire, a shaman of the Windshapers at Camp Narache, each with
	# their racials.
	# (Where they are is read from the characters table: .gps is a GM's command, and the test account isn't one.)
	printf 'wait 2\n' > "$FILES/run/skyborne.steps"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Skyhighorder 13 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/skyborne-alliance.out" || fail "the High Order's warrior didn't get into the world"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Skywindshape 14 7 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/skyborne-horde.out" || fail "the Windshapers' shaman didn't get into the world"
	for who in Skyhighorder:1:1:Northshire Skywindshape:6:7:"Camp Narache"; do
		IFS=: read -r name race class place <<EOF
$who
EOF
		at=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM characters WHERE name = '$name'" | CTL sql acore_characters)
		start=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM playercreateinfo WHERE race = $race AND class = $class" | CTL sql acore_world)
		echo "$name at $at, $place's start $start"
		[ -n "$at" ] && [ "$at" = "$start" ] || fail "$name didn't start in $place ($at, not $start)"
	done
	for who in Skyhighorder:98701,98703,98704,98705 Skywindshape:98701,98702,98704,98705; do
		name=${who%%:*} spells=${who#*:}
		learned=$(echo "SELECT COUNT(*) FROM character_spell s JOIN characters c ON c.guid = s.guid WHERE c.name = '$name' AND s.spell IN ($spells)" | CTL sql acore_characters)
		[ "$learned" = 4 ] || fail "$name has $learned of its 4 racials"
	done
	# Their side's language (up to 1.0.236 they had none: the allied races' SQL, applied before theirs,
	# changed the skill rows they looked for, and they were in the other side's tiered language row).
	for who in Skyhighorder:98 Skywindshape:109; do
		knows_language "${who%%:*}" "${who#*:}" || fail "${who%%:*} doesn't know its side's language (skill ${who#*:})"
	done
	echo "The Skyborne start where their side's start races do, with their racials and their side's language."

	echo "== the void elves, the nightborne, the Lightforged Draenei and the Zandalari Trolls (mod-allied-races)"
	grep -E "Allied races: The races' patch is in the game: 19 tables, [0-9]+ files" "$FILES/logs/world.out" ||
		fail "the world server didn't make the races' patch"
	[ -s "$FILES/client/Data/patch-V.MPQ" ] && [ -s "$FILES/client/Data/patch-V.MPQ.alliedraces" ] || fail "the races' patch isn't in the game"
	# Made before Wrath Remix's and the Skyborne's patches, which the game reads after it: they carry
	# its rows on only when it's there as they're made.
	allied=$(grep -n -m1 "Allied races: The races' patch is in the game" "$FILES/logs/world.out" | cut -d: -f1 || true)
	# (a patch not made in this run, Wrath Remix's on ChromieCraft's realm, is no failure: under
	# set -e a grep that finds nothing would end the test here, silently)
	for later in "Skyborne: The Skyborne's patch is in the game" "Wrath Remix: the game's patch written"; do
		at=$(grep -n -m1 "$later" "$FILES/logs/world.out" | cut -d: -f1 || true)
		echo "world.out: the races' patch at line ${allied:-?}, '$later' at line ${at:-none}"
		[ -z "$at" ] || [ "$allied" -lt "$at" ] || fail "the races' patch was made after the one read over it ($later)"
	done
	for race in 15 16 17 18; do
		[ "$(echo "SELECT Flags & 1 FROM chrraces_dbc WHERE ID = $race" | CTL sql acore_world)" = 0 ] || fail "race $race isn't playable"
	done
	looks=$(echo "SELECT COUNT(*) FROM charsections_dbc WHERE RaceID IN (15, 16, 17, 18)" | CTL sql acore_world)
	[ "$looks" -gt 28000 ] || fail "the races' looks aren't in the world database ($looks rows)"
	# The start quests cloned for them, the originals still closed to them; the quests that need a
	# cloned one first cloned too (the class training), and chained to the clones.
	clones=$(echo "SELECT COUNT(*) FROM quest_template WHERE AllowableRaces = 65536" | CTL sql acore_world)
	[ "$clones" -ge 20 ] || fail "the Lightforged Draenei's start quests aren't cloned ($clones)"
	clones=$(echo "SELECT COUNT(*) FROM quest_template WHERE AllowableRaces = 131072" | CTL sql acore_world)
	[ "$clones" -ge 15 ] || fail "the Zandalari's start quests aren't cloned ($clones)"
	[ "$(echo "SELECT AllowableRaces & 131072 FROM quest_template WHERE ID = 747" | CTL sql acore_world)" = 0 ] || fail "The Hunt Begins is open to the Zandalari: only its clone should be"
	[ "$(echo "SELECT PrevQuestID FROM quest_template_addon WHERE ID = 960750" | CTL sql acore_world)" = 960747 ] || fail "the clone of The Hunt Continues doesn't follow the clone of The Hunt Begins"
	[ "$(echo "SELECT PrevQuestID FROM quest_template_addon WHERE ID = 959288" | CTL sql acore_world)" = 959280 ] || fail "a void elf's Hunter Training doesn't follow the clone of the quest before it"

	echo "== WoW: Forever's new quests (mod-forever-quests)"
	# All in ChromieCraft's world, and the world server
	# loaded them without a word about any of them (a creature, an item or a quest it couldn't find).
	forever_ids=$(python3 -c 'import json, sys; print(" ".join(json.load(open(sys.argv[1]))["quests"]))' \
		"$ROOT/warcraft/modules/mod-forever-quests/data/forever/quests.json")
	forever=$(echo "SELECT COUNT(*) FROM quest_template WHERE ID IN ($(echo $forever_ids | tr ' ' ','))" | CTL sql acore_world)
	[ "$forever" = "$(echo $forever_ids | wc -w)" ] || fail "WoW: Forever's quests aren't all in ChromieCraft's world ($forever)"
	complaints=$(grep -ihwE "quest.*($(echo $forever_ids | tr ' ' '|'))" "$FILES/logs/world.out" "$FILES/logs/Errors.log" "$FILES/logs/Server.log" 2>/dev/null || true)
	[ -z "$complaints" ] || { echo "$complaints" | head -20; fail "the world server complained about WoW: Forever's quests"; }
	# Nor about their new people and creatures (their spawns too) or items.
	forever_others=$(python3 -c 'import json, sys; d = json.load(open(sys.argv[1])); print("|".join([n for n, v in d["npcs"].items() if v.get("new")] + list(d["items"]) + list(d["rewards"])))' \
		"$ROOT/warcraft/modules/mod-forever-quests/data/forever/quests.json")
	complaints=$(grep -ihwE "(creature|item|entry).*($forever_others)" "$FILES/logs/Errors.log" "$FILES/logs/Server.log" 2>/dev/null || true)
	[ -z "$complaints" ] || { echo "$complaints" | head -20; fail "the world server complained about WoW: Forever's NPCs or items"; }
	spawned=$(echo "SELECT COUNT(*) FROM creature WHERE guid BETWEEN 8600000 AND 8699999" | CTL sql acore_world)
	[ "$spawned" -gt 0 ] || fail "WoW: Forever's new NPCs aren't in ChromieCraft's world"
	echo "WoW: Forever's quests: $forever in ChromieCraft's world, $spawned spawns of their new NPCs"
	# A void elf warrior in Ammen Vale, a nightborne warrior in Deathknell, a Lightforged Draenei
	# warrior in Ammen Vale, a Zandalari warrior at Camp Narache, each with their racials.
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Voidtester 15 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/allied-voidelf.out" || fail "the void elf warrior didn't get into the world"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Nighttester 16 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/allied-nightborne.out" || fail "the nightborne warrior didn't get into the world"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Lightester 17 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/allied-lightforged.out" || fail "the Lightforged Draenei warrior didn't get into the world"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Zandtester 18 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/allied-zandalari.out" || fail "the Zandalari warrior didn't get into the world"
	for who in Voidtester:11:1:"Ammen Vale" Nighttester:5:1:Deathknell Lightester:11:1:"Ammen Vale" Zandtester:6:1:"Camp Narache"; do
		IFS=: read -r name race class place <<EOF
$who
EOF
		at=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM characters WHERE name = '$name'" | CTL sql acore_characters)
		start=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM playercreateinfo WHERE race = $race AND class = $class" | CTL sql acore_world)
		echo "$name at $at, $place's start $start"
		[ -n "$at" ] && [ "$at" = "$start" ] || fail "$name didn't start in $place ($at, not $start)"
	done
	for who in Voidtester:98711,98713,98715,98716,98717:5 Nighttester:98718,98720,98721,98722:4 Lightester:98723,98725,98726,98728,98729:5 Zandtester:98730,98731,98733,98734:4; do
		name=${who%%:*} rest=${who#*:} spells=${rest%%:*} count=${rest#*:}
		learned=$(echo "SELECT COUNT(*) FROM character_spell s JOIN characters c ON c.guid = s.guid WHERE c.name = '$name' AND s.spell IN ($spells)" | CTL sql acore_characters)
		[ "$learned" = "$count" ] || fail "$name has $learned of its $count racials"
	done
	# Their side's language: no /say and no chat command without it. Up to 1.0.236 they had none
	# (their place in the other side's tiered language row).
	for who in Voidtester:98 Nighttester:109 Lightester:98 Zandtester:109; do
		knows_language "${who%%:*}" "${who#*:}" || fail "${who%%:*} doesn't know its side's language (skill ${who#*:})"
	done
	echo "The void elves and the Lightforged Draenei start with the Draenei, the nightborne with the Forsaken, the Zandalari with the Tauren, each with their racials and their side's language."
	# In the world: their racials at work (Preternatural Calm's aura, Spatial Rift through the rift,
	# Arcane Pulse's damage, Light's Reckoning's and Judgment's the character's own, Regeneratin',
	# Pterrordax Swoop), their own first quests offered and the start race's not, and Rescue the
	# Survivors! done with a lent Gift of the Naaru, taken back as it's handed in.
	for who in Voidtester:15:voidelf Nighttester:16:nightborne Lightester:17:lightforged Zandtester:18:zandalari; do
		IFS=: read -r name race file <<EOF
$who
EOF
		python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 "$name" "$race" 1 \
			"$ROOT/warcraft/server/allied_$file.steps" | tee "$FILES/logs/allied-$file-world.out" ||
			fail "$name's racials and quests didn't work in the world (logs/allied-$file-world.out)"
	done
	echo "Their racials work in the world, their first quests are their own, and Rescue the Survivors! can be done."
	# An undead paladin (Paladin for the Forsaken) at Deathknell's priest trainer: greeted as a
	# priest, trained as a paladin.
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Lighttaker 5 2 \
		"$ROOT/warcraft/server/allied_undead_paladin.steps" | tee "$FILES/logs/allied-undead-paladin.out" ||
		fail "Deathknell's priest trainer didn't train the undead paladin as a paladin (logs/allied-undead-paladin.out)"
	echo "An undead paladin trains at the priest trainers."
	# It goes again: a realm keeps ten characters an account, and Wrath Remix's way home (below)
	# needs room on ChromieCraft for the Timerunners it brings back.
	# (erased the way the realm erases one: a partial delete leaves rows a later character with its
	# guid collides with)
	erase_character Lighttaker || fail "the undead paladin test character is still there"

	echo "== the Worgen and Goblins (mod-worgen-goblin, from mod-worgoblin)"
	grep -E "Worgen and Goblins: The Worgen's and Goblins' patch is in the game: 30 tables, [0-9]+ files" "$FILES/logs/world.out" ||
		fail "the world server didn't make the Worgen's and Goblins' patch"
	[ -s "$FILES/client/Data/patch-U.MPQ" ] && [ -s "$FILES/client/Data/patch-U.MPQ.worgengoblin" ] || fail "the Worgen's and Goblins' patch isn't in the game"
	# Made before the allied races' patch (and so the Skyborne's and Wrath Remix's), which are made
	# from the game with it in.
	worgen=$(grep -n -m1 "Worgen and Goblins: The Worgen's and Goblins' patch is in the game" "$FILES/logs/world.out" | cut -d: -f1 || true)
	echo "world.out: the Worgen's and Goblins' patch at line ${worgen:-?}, the allied races' at line ${allied:-?}"
	[ -n "$worgen" ] && [ -n "$allied" ] && [ "$worgen" -lt "$allied" ] || fail "the Worgen's and Goblins' patch was made after the allied races'"
	grep -q "Worgen and Goblins: their rows are in the world's tables" "$FILES/logs/world.out" ||
		fail "the world server didn't put the Worgen's and Goblins' rows in its tables"
	for race in 9 12; do
		[ "$(echo "SELECT Flags & 1 FROM chrraces_dbc WHERE ID = $race" | CTL sql acore_world)" = 0 ] || fail "race $race isn't playable"
	done
	looks=$(echo "SELECT COUNT(*) FROM charsections_dbc WHERE RaceID IN (9, 12)" | CTL sql acore_world)
	[ "$looks" -ge 1642 ] || fail "the Worgen's and Goblins' looks aren't in the world database ($looks rows)"
	# mod-worgoblin's own SQL in ChromieCraft's world alone (Wrath Remix's is checked below).
	[ "$(echo "SELECT COUNT(*) FROM updates_include WHERE path LIKE '%mod-worgen-goblin/data/sql/chromiecraft/world'" | CTL sql acore_world)" = 1 ] ||
		fail "ChromieCraft's world database doesn't list the Worgen's and Goblins' SQL"
	# Every race's standing in the capitals' reputations, the allied races' and the Skyborne's too:
	# until 1.0.328 whichever module's SQL went in last took the others' races out of those rows.
	# Stormwind (72): the Worgen (2048), void elves (16384), High Order (4096); Orgrimmar (76): the
	# Goblins (256), nightborne (32768), Windshapers (8192).
	for want in 72:2048:Worgen 72:16384:void-elves 72:4096:High-Order 76:256:Goblins 76:32768:nightborne 76:8192:Windshapers; do
		faction=${want%%:*} rest=${want#*:} bit=${rest%%:*} who=${rest#*:}
		masks=$(echo "SELECT (ReputationRaceMask_1 | ReputationRaceMask_2 | ReputationRaceMask_3 | ReputationRaceMask_4) & $bit FROM faction_dbc WHERE ID = $faction" | CTL sql acore_world)
		[ -n "$masks" ] && [ "$masks" != 0 ] || fail "the $who have no standing in faction $faction's row"
	done
	# A Worgen warrior in Shadowglen and a Goblin warrior in the Valley of Trials (mod-worgoblin's
	# starts), each with their racials and their side's language.
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Worgtester 12 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/worgen.out" || fail "the Worgen warrior didn't get into the world"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Gobtester 9 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/goblin.out" || fail "the Goblin warrior didn't get into the world"
	for who in "Worgtester:12:1:Shadowglen" "Gobtester:9:1:the Valley of Trials"; do
		name=${who%%:*} rest=${who#*:} race=${rest%%:*} rest=${rest#*:} class=${rest%%:*} place=${rest#*:}
		at=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM characters WHERE name = '$name'" | CTL sql acore_characters)
		start=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM playercreateinfo WHERE race = $race AND class = $class" | CTL sql acore_world)
		echo "$name at $at, $place's start $start"
		[ -n "$at" ] && [ "$at" = "$start" ] || fail "$name didn't start in $place ($at, not $start)"
	done
	# Their racials are a racial skill's (789 the Worgen's, 790 the Goblins'), as the game's own races'
	# are: the core teaches its spells at every login and keeps them out of character_spell, so the
	# skill is checked, and its spells given to the race in the world's tables.
	for who in Worgtester:789:2048:68975,68976,68978,68992:4 Gobtester:790:256:69041,69042,69044,69045,69046,69070:6; do
		name=${who%%:*} rest=${who#*:} skill=${rest%%:*} rest=${rest#*:} bit=${rest%%:*} rest=${rest#*:} spells=${rest%%:*} count=${rest#*:}
		knows=$(echo "SELECT COUNT(*) FROM character_skills s JOIN characters c ON c.guid = s.guid WHERE c.name = '$name' AND s.skill = $skill" | CTL sql acore_characters)
		[ "$knows" = 1 ] || fail "$name hasn't its racial skill ($skill)"
		given=$(echo "SELECT COUNT(DISTINCT Spell) FROM skilllineability_dbc WHERE SkillLine = $skill AND Spell IN ($spells) AND RaceMask & $bit" | CTL sql acore_world)
		[ "$given" = "$count" ] || fail "$name's racial skill gives $given of its $count racials"
	done
	for who in Worgtester:98 Gobtester:109; do
		knows_language "${who%%:*}" "${who#*:}" || fail "${who%%:*} doesn't know its side's language (skill ${who#*:})"
	done
	echo "The Worgen start in Shadowglen and the Goblins in the Valley of Trials, with their racials and their side's language."
	# The two go again: a realm keeps ten characters an account, and Wrath Remix's way home (below)
	# needs room on ChromieCraft for the Timerunners it brings back (1.0.330's run had no room). The
	# world server erases them, everything of theirs (1.0.331's run deleted their rows in SQL and left
	# their achievements behind: the next character the realm made had their guid, and a Timerunner
	# coming home on it collided with them).
	for name in Worgtester Gobtester; do
		erase_character "$name" || fail "$name wasn't erased"
	done

	echo "== the Murlocs and the Naga (mod-murloc-naga)"
	grep -E "Murlocs and Naga: The races' patch is in the game: [0-9]+ tables, [0-9]+ files" "$FILES/logs/world.out" ||
		fail "the world server didn't make the Murlocs' and the Naga's patch"
	[ -s "$FILES/client/Data/enUS/patch-enUS-T.MPQ" ] && [ -s "$FILES/client/Data/enUS/patch-enUS-T.MPQ.murlocnaga" ] ||
		fail "the Murlocs' and the Naga's patch isn't in the game"
	# Made before the other race modules' patches, which the game reads after it and which are made
	# from the game with it in, carrying its rows.
	murloc_naga=$(grep -n -m1 "Murlocs and Naga: The races' patch is in the game" "$FILES/logs/world.out" | cut -d: -f1 || true)
	for later in "Worgen and Goblins: The Worgen's and Goblins' patch is in the game" "Allied races: The races' patch is in the game" \
			"Skyborne: The Skyborne's patch is in the game"; do
		at=$(grep -n -m1 "$later" "$FILES/logs/world.out" | cut -d: -f1 || true)
		echo "world.out: the Murlocs' and the Naga's patch at line ${murloc_naga:-?}, '$later' at line ${at:-none}"
		[ -z "$at" ] || [ "$murloc_naga" -lt "$at" ] || fail "the Murlocs' and the Naga's patch was made after one read over it ($later)"
	done
	for race in 19 20; do
		[ "$(echo "SELECT Flags & 1 FROM chrraces_dbc WHERE ID = $race" | CTL sql acore_world)" = 0 ] || fail "race $race isn't playable"
	done
	[ "$(echo "SELECT ClientFilestring FROM chrraces_dbc WHERE ID = 30" | CTL sql acore_world)" = Taunka ] || fail "the Taunka aren't at race 30"
	# The naga's standing: neutral with Darnassus, Ironforge and the Gnomeregan Exiles (their last slot),
	# hated by the rest of the Horde.
	for faction in 69 47 54; do
		[ "$(echo "SELECT CONCAT(ReputationRaceMask_4 & 524288, ' ', ReputationBase_4) FROM faction_dbc WHERE ID = $faction" | CTL sql acore_world)" = "524288 0" ] ||
			fail "the naga aren't neutral to faction $faction"
	done
	# A murloc warrior in the Wrathtail's pens at the Zoram Strand and a naga shaman at Rethress Sanctum in Azshara
	# (their stories' starts), at level 10, with their racials,
	# their side's language and their class's spells to level 10.
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Murloctester 19 1 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/murloc.out" || fail "the murloc warrior didn't get into the world"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Nagatester 20 7 "$FILES/run/skyborne.steps" |
		tee "$FILES/logs/naga.out" || fail "the naga shaman didn't get into the world"
	for who in "Murloctester:19:1:the murlocs' pens" "Nagatester:20:7:Rethress Sanctum"; do
		name=${who%%:*} rest=${who#*:} race=${rest%%:*} rest=${rest#*:} class=${rest%%:*} place=${rest#*:}
		at=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM characters WHERE name = '$name'" | CTL sql acore_characters)
		start=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM playercreateinfo WHERE race = $race AND class = $class" | CTL sql acore_world)
		echo "$name at $at, $place's start $start"
		[ -n "$at" ] && [ "$at" = "$start" ] || fail "$name didn't start in $place ($at, not $start)"
		level=$(echo "SELECT level FROM characters WHERE name = '$name'" | CTL sql acore_characters)
		[ "$level" = 10 ] || fail "$name is level $level, not 10"
		spells=$(echo "SELECT COUNT(*) FROM character_spell s JOIN characters c ON c.guid = s.guid WHERE c.name = '$name' AND s.spell IN
			(SELECT ts.SpellId FROM acore_world.trainer_spell ts JOIN acore_world.trainer t ON t.Id = ts.TrainerId
			 WHERE t.Type = 0 AND t.Requirement = $class AND ts.ReqLevel BETWEEN 2 AND 10)" | CTL sql acore_characters)
		[ "$spells" -ge 3 ] || fail "$name hasn't its class's spells to level 10 ($spells)"
	done
	for who in Murloctester:98882,98883,98884:3 Nagatester:98885,98886,98887:3; do
		name=${who%%:*} rest=${who#*:} spells=${rest%%:*} count=${rest#*:}
		learned=$(echo "SELECT COUNT(*) FROM character_spell s JOIN characters c ON c.guid = s.guid WHERE c.name = '$name' AND s.spell IN ($spells)" | CTL sql acore_characters)
		[ "$learned" = "$count" ] || fail "$name has $learned of its $count racials"
	done
	# (the murlocs' Nerglish: the game's Titan, skill 140; the naga's Orcish)
	for who in Murloctester:140 Nagatester:109; do
		knows_language "${who%%:*}" "${who#*:}" || fail "${who%%:*} doesn't know its side's language (skill ${who#*:})"
	done
	# In the world (each story's steps, warcraft/server/murloc_naga_*.steps): the murloc's pens, its chapters'
	# hubs, Auberdine's quests closed to it; the naga in its phase alone at Rethress Sanctum, its first chapter's
	# quests, a memory gone into, died in and woken from, a question answered, Valormok's quests closed to it.
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Murloctester 19 1 \
		"$ROOT/warcraft/server/murloc_naga_murloc.steps" | tee "$FILES/logs/murloc-world.out" ||
		fail "the murloc's pens and first quests didn't work in the world (logs/murloc-world.out)"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Nagatester 20 7 \
		"$ROOT/warcraft/server/murloc_naga_naga.steps" | tee "$FILES/logs/naga-world.out" ||
		fail "the naga's story (its start, a memory, its gate) didn't work in the world (logs/naga-world.out)"
	echo "The murlocs start at level 10 in the pens and the naga at Rethress Sanctum, with their racials, language and class spells."
	for name in Murloctester Nagatester; do
		erase_character "$name" || fail "$name wasn't erased"
	done

	# The starting areas (mod-worgen-goblin's data/zones, the zones job's package): installed the way
	# the app installs it and turned on, the two races' new characters start in Gilneas and Kezan;
	# nothing of the game's own world changes for anyone else (the Humans and Orcs start where they
	# always have, the game's creatures, objects and quests are as they were), and no other race's
	# character is let onto their maps. Then off again: their rows go, and the starts are back.
	if [ -n "${WOW_ZONES_TAR:-}" ]; then
		echo "== the Worgen's and Goblins' starting areas (mod-worgen-goblin, data/zones)"
		# (the game's own: every row outside the starting areas' ranges, mod-worgen-goblin's
		# tools/zones/build_world.py: ids from 6000000, spawns from 10000000)
		world_rows() {
			echo "SELECT CONCAT_WS(' ', (SELECT COUNT(*) FROM creature_template WHERE entry NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM creature WHERE guid NOT BETWEEN 10000000 AND 12999999),
				(SELECT COUNT(*) FROM gameobject_template WHERE entry NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM gameobject WHERE guid NOT BETWEEN 10000000 AND 12999999),
				(SELECT COUNT(*) FROM quest_template WHERE ID NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM item_template WHERE VerifiedBuild IS NULL OR VerifiedBuild <> -15595),
				(SELECT COUNT(*) FROM smart_scripts WHERE entryorguid NOT BETWEEN 6000000 AND 6999999
					AND -entryorguid NOT BETWEEN 10000000 AND 12999999 AND entryorguid NOT BETWEEN 600000000 AND 699999999),
				(SELECT COUNT(*) FROM creature_queststarter WHERE quest NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM creature_questender WHERE quest NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM creature_loot_template WHERE Entry NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM npc_vendor WHERE entry NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM spell_area WHERE area NOT IN (SELECT ID FROM areatable_dbc
					WHERE ContinentID IN (638, 648, 654, 655, 656, 659, 661))),
				(SELECT COUNT(*) FROM areatrigger_involvedrelation WHERE quest NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM creature_text WHERE CreatureID NOT BETWEEN 6000000 AND 6999999),
				(SELECT COUNT(*) FROM gossip_menu WHERE MenuID NOT BETWEEN 6000000 AND 6999999),
				(SELECT GROUP_CONCAT(CONCAT(race, ':', class, ':', map, ':', ROUND(position_x)) ORDER BY race, class) FROM playercreateinfo WHERE race NOT IN (9, 12)))" |
				CTL sql acore_world
		}
		before=$(world_rows)
		stop_world
		mkdir -p "$FILES/zones"
		tar -xJf "$WOW_ZONES_TAR" -C "$FILES/zones" --strip-components=1
		cat "$FILES/zones/TAG" "$FILES/zones/VERSION"
		sed -i 's/^WorgenGoblin.StartingAreas .*/WorgenGoblin.StartingAreas = 1/' "$FILES/etc/modules/mod_worgen_goblin.conf"
		start_world world-zones.out
		wait_world_ready
		grep -E "The starting areas' maps are in the world server's data \([0-9]+ files\)" "$world_log" ||
			fail "ctl.sh didn't put the starting areas' maps in the world server's data"
		grep -E "Worgen and Goblins: The starting areas are in it: [0-9]+ files" "$world_log" ||
			fail "the game's patch hasn't the starting areas"
		grep -q "Worgen and Goblins: the starting areas are in the world" "$world_log" || fail "the starting areas aren't in the world"
		for map in 638 648 654 655 656 659 661; do
			[ -s "$FILES/data/mmaps/$(printf %03d "$map").mmap" ] || fail "map $map has no paths in the world server's data"
		done
		[ "$(echo "SELECT COUNT(*) FROM map_dbc WHERE ID IN (638, 648, 654, 655, 656, 659, 661)" | CTL sql acore_world)" = 7 ] ||
			fail "the world's tables haven't the starting areas' seven maps"
		areas=$(echo "SELECT COUNT(*) FROM areatable_dbc WHERE ContinentID IN (648, 654)" | CTL sql acore_world)
		[ "$areas" = 92 ] || fail "the world's tables have $areas of the starting areas' 92 areas"
		# Every script their rows name has its code (src/WorgenGoblinGilneas.cpp, WorgenGoblinKezan.cpp, WorgenGoblinZones.cpp).
		names=$(grep -oE "'(npc|go|at|spell)_[a-z_]+'" "$FILES/server/src/modules/mod-worgen-goblin/data/zones/server/zones_world.sql" 2> /dev/null |
			tr -d "'" | sort -u | paste -sd'|' -)
		if [ -n "$names" ] && grep -E "Script named '($names)' is assigned in the database, but has no code" "$FILES/logs/Errors.log"; then
			fail "the starting areas name scripts the world server hasn't"
		fi
		# Every one of their creatures and objects loads (a creature whose display has no
		# creature_model_info row never does: seen on a phone as nobody there).
		if grep -iE "Creature \(Entry: 6[0-9]{6}\) has no model|gameobject \(GUID: 1[0-9]{7} .*not loaded" "$FILES/logs/Errors.log" | head -5 | grep .; then
			fail "some of the starting areas' creatures or objects don't load"
		fi
		# Their spawns' ids under AzerothCore's limit (a new spawn's id is one after the highest, and
		# the world server stops when it would pass 0xFFFFFF).
		spawns=$(echo "SELECT GREATEST((SELECT MAX(guid) FROM creature), (SELECT MAX(guid) FROM gameobject))" | CTL sql acore_world)
		[ "$spawns" -lt 15000000 ] || fail "the starting areas' spawns' ids reach $spawns: a new spawn would stop the world server"
		after=$(world_rows)
		echo "the game's own world: $before"
		[ "$after" = "$before" ] || fail "the game's own creatures, objects, quests or starts changed: $after"
		# Their new characters, where Cataclysm starts them: a Worgen warrior in Gilneas City (on map
		# 638, Gilneas as it is until quest 14222), a Goblin warrior in Kezan; a Human and an Orc
		# where they always have. (On an account of their own: the tester's has the realm's ten
		# characters by now.)
		python3 "$ROOT/warcraft/server/auth_check.py" account-sql zoner secret123 | CTL sql acore_auth
		for who in "Zonewolf:12:1:638" "Zonegoblin:9:1:648" "Zonehuman:1:1:0" "Zoneorc:2:1:1"; do
			IFS=: read -r name race class map <<EOF2
$who
EOF2
			python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 zoner secret123 "$name" "$race" "$class" "$FILES/run/skyborne.steps" |
				tee "$FILES/logs/zones-$name.out" || fail "$name didn't get into the world (logs/zones-$name.out)"
			at=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM characters WHERE name = '$name'" | CTL sql acore_characters)
			start=$(echo "SELECT CONCAT(map, ' ', ROUND(position_x), ' ', ROUND(position_y)) FROM playercreateinfo WHERE race = $race AND class = $class" | CTL sql acore_world)
			echo "$name at $at, its start $start"
			[ -n "$at" ] && [ "$at" = "$start" ] && [ "${at%% *}" = "$map" ] || fail "$name didn't start on map $map ($at, its start $start)"
		done
		# No other race's character on their maps: one there anyway (a Human put on Gilneas's map) is
		# taken home as it logs in, on an account that isn't a game master's.
		python3 "$ROOT/warcraft/server/auth_check.py" account-sql plainer secret123 | CTL sql acore_auth
		echo "DELETE FROM account_access WHERE id = (SELECT id FROM account WHERE username = 'PLAINER')" | CTL sql acore_auth
		python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 plainer secret123 Plainhuman 1 1 "$FILES/run/skyborne.steps" > /dev/null ||
			fail "a player's Human didn't get into the world"
		echo "UPDATE characters SET map = 654, position_x = -1451.53, position_y = 1403.35, position_z = 35.5561 WHERE name = 'Plainhuman'" |
			CTL sql acore_characters
		python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 plainer secret123 Plainhuman 1 1 "$FILES/run/skyborne.steps" |
			tee "$FILES/logs/zones-plainhuman.out" > /dev/null || fail "the Human put on Gilneas's map didn't get into the world"
		at=$(echo "SELECT map FROM characters WHERE name = 'Plainhuman'" | CTL sql acore_characters)
		[ "$at" = 0 ] || fail "a Human on Gilneas's map was left there (map $at)"
		echo "A Human on Gilneas's map is taken home."
		for name in Zonewolf Zonegoblin Zonehuman Zoneorc Plainhuman; do
			erase_character "$name" || fail "$name wasn't erased"
		done
		# Off again.
		stop_world
		sed -i 's/^WorgenGoblin.StartingAreas .*/WorgenGoblin.StartingAreas = 0/' "$FILES/etc/modules/mod_worgen_goblin.conf"
		start_world world-zones-off.out
		wait_world_ready
		grep -q "Worgen and Goblins: no starting areas" "$world_log" || fail "the world server didn't take the starting areas out"
		[ "$(echo "SELECT COUNT(*) FROM map_dbc WHERE ID IN (638, 648, 654, 655, 656, 659, 661)" | CTL sql acore_world)" = 0 ] ||
			fail "the starting areas' maps are still in the world's tables"
		[ "$(echo "SELECT map FROM playercreateinfo WHERE race = 12 AND class = 1" | CTL sql acore_world)" = 1 ] ||
			fail "the Worgen don't start in Shadowglen again"
		[ "$(world_rows)" = "$before" ] || fail "the game's own world isn't as it was after the starting areas went"
		echo "The starting areas are in and out again, the game's own world as it was."
	fi

	# WoW: Forever's new pairs, each at its start with its race's Forever racials, trained by another
	# class's trainer there as its own class's trainer does; each erased after (room for Remix's
	# way home).
	for who in Humhunter:1:3:human_hunter Dwarfshaman:3:7:dwarf_shaman Gnomepriest:7:5:gnome_priest \
		Orcmage:2:8:orc_mage Trollwarlock:8:9:troll_warlock; do
		IFS=: read -r name race class file <<EOF
$who
EOF
		python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 "$name" "$race" "$class" \
			"$ROOT/warcraft/server/forever_$file.steps" | tee "$FILES/logs/forever-$file.out" ||
			fail "$name's racials or trainer weren't Forever's (logs/forever-$file.out)"
		erase_character "$name" || fail "$name wasn't erased"
	done
	echo "Human hunters, dwarf shamans, gnome priests, orc mages and troll warlocks: Forever's racials, trained at their host class's trainers."

	echo "== quest drops (mod-quest-drops): rare quest items drop at 75% (under 75%) or 50% (10% or less)"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Dropper 5 9 \
		"$ROOT/warcraft/server/quest_drops.steps" | tee "$FILES/logs/quest-drops.out" ||
		fail "the Rattlecage Skeletons' skulls didn't drop at the raised rate (logs/quest-drops.out)"
	erase_character Dropper || fail "Dropper wasn't erased"
	echo "Quest drops roll 75% under 75%, 50% at 10% or less; twenty Rattlecage Skeletons dropped their skulls at that rate."

	echo "== a home in Brill (mod-brill-home): Cedric Harrow's house, Jamie Nore's quests, the bed and the furniture"
	[ "$(echo "SELECT COUNT(*) FROM gameobject WHERE guid = 970100 AND id = 970100" | CTL sql acore_world)" = 1 ] ||
		fail "the house isn't in ChromieCraft's world"
	# Corn (the quest dog, his pet and a hunter's companion): the game's pug display (the patch makes it his model).
	[ "$(echo "SELECT COUNT(*) FROM creature_template_model WHERE CreatureID IN (970112,970115,970116) AND CreatureDisplayID = 31174" | CTL sql acore_world)" = 3 ] ||
		fail "the Brill dog isn't the game's pug display"
	# The module's patch in the game: the language folder's patch-<locale>-V, its table (the cellar's looks)
	# and Corn's coat at the pug's coat's path, made after the allied races'.
	grep -E "Brill home: The Brill home's patch is in the game: 1 tables" "$FILES/logs/world.out" ||
		fail "the world server didn't make the Brill home's patch (Corn, the cellar)"
	grep -E "Brill home: The Brill home's patch is in the game: .*Corn the (Forsaken|plain) pug" "$FILES/logs/world.out" || true
	ls "$FILES"/client/Data/*/patch-*-V.MPQ > /dev/null 2>&1 || fail "the Brill home's patch isn't in the game"
	brill=$(grep -n -m1 "Brill home: The Brill home's patch is in the game" "$FILES/logs/world.out" | cut -d: -f1 || true)
	echo "world.out: the Brill home's patch at line ${brill:-?}, the allied races' at line ${allied:-?}"
	[ -n "$brill" ] && [ -n "$allied" ] && [ "$brill" -gt "$allied" ] || fail "the Brill home's patch was made before the allied races'"
	complaints=$(grep -ihwE "(entry|quest|guid|creature|gameobject)[^0-9]*9701[0-4][0-9]" "$FILES/logs/Errors.log" "$FILES/logs/Server.log" 2>/dev/null || true)
	[ -z "$complaints" ] || { echo "$complaints" | head -20; fail "the world server complained about the house's rows"; }
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Homesteader 5 1 \
		"$ROOT/warcraft/server/brill_home.steps" | tee "$FILES/logs/brill-home.out" ||
		fail "the house's quests, bed or furniture didn't work (logs/brill-home.out)"
	erase_character Homesteader || fail "Homesteader wasn't erased"
	# A hunter's dog: one more out beside their own pet, not in its place (an orc hunter).
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Dogkeeper 2 3 \
		"$ROOT/warcraft/server/brill_home_hunter.steps" | tee "$FILES/logs/brill-home-hunter.out" ||
		fail "a hunter's dog didn't come out beside them (logs/brill-home-hunter.out)"
	erase_character Dogkeeper || fail "Dogkeeper wasn't erased"
	echo "Cedric leaves the house, Jamie Nore's deed and bed, a night's sleep in it with rested experience, a rug bought."

	echo "== Brill: A Place Among the Forsaken (mod-brill-home's town questlines, tools/town)"
	grep -E "Brill town: [0-9]+ phase rows" "$FILES/logs/world.out" || fail "the world server didn't read the town's questlines"
	complaints=$(grep -ihwE "(entry|quest|guid|creature|gameobject)[^0-9]*(970[2-9][0-9][0-9]|971[0-6][0-9][0-9])" "$FILES/logs/Errors.log" "$FILES/logs/Server.log" 2>/dev/null || true)
	[ -z "$complaints" ] || { echo "$complaints" | head -20; fail "the world server complained about the town's rows"; }
	# Each line played through by its own new character (an undead warrior), erased after.
	n=0
	for steps in "$ROOT"/warcraft/server/brill_town_*.steps; do
		line=$(basename "$steps" .steps)
		line=${line#brill_town_}
		n=$((n + 1))
		# (a name the game takes: twelve letters at most, the first a capital)
		name="Brill$(echo "$line" | tr -cd 'a-z' | head -c7)"
		python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 "$name" 5 1 "$steps" |
			tee "$FILES/logs/brill-town-$line.out" || fail "Brill's $line questline didn't play through (logs/brill-town-$line.out)"
		erase_character "$name" || fail "$name wasn't erased"
	done
	echo "Brill's questlines: $n played through."

	echo "== world server shutdown, the way the app stops it"
	stop_world

	echo "== what earlier versions' custom races left, taken out"
	# A phone that had them on: their SQL in the world database (the table app_races says so),
	# their files, and a character of one of them (a Worgen, race 12: a copy of the human).
	echo "CREATE TABLE app_races (version VARCHAR(255) NOT NULL); INSERT INTO app_races VALUES ('races 52fd006');" |
		CTL sql acore_world
	echo "CREATE TEMPORARY TABLE wolf AS SELECT * FROM characters WHERE name = 'Testhero'; UPDATE wolf SET guid = (SELECT MAX(guid) + 1 FROM characters), name = 'Testwolf', race = 12; INSERT INTO characters SELECT * FROM wolf;" |
		CTL sql acore_characters
	mkdir -p "$FILES/races/dbc" "$FILES/data-races/dbc"
	touch "$FILES/races/on" "$FILES/races/world.sql"
	start=$(date +%s)
	CTL races > "$FILES/logs/races.out" 2>&1 || fail "taking the races out failed: $(tail -5 "$FILES/logs/races.out")"
	tail -3 "$FILES/logs/races.out"
	echo "took $(($(date +%s) - start)) s"
	tables=$(echo "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'acore_world' AND table_name = 'app_races'" | CTL sql)
	[ "$tables" = 0 ] || fail "the world database still has the races"
	if [ -e "$FILES/races" ] || [ -e "$FILES/data-races" ]; then fail "the races' files are still there"; fi
	if grep -q "data-races" "$FILES/etc/worldserver.conf"; then fail "the world server reads the races' tables"; fi

	echo "== a module taken out of the realm: what it put in the world database goes"
	# The realm swapped for one without a module (mod-gone) that had put a table in the world.
	echo "mod-gone" >> "$FILES/mysql/.world-modules"
	echo "CREATE TABLE mod_gone (id INT NOT NULL)" | CTL sql acore_world
	start=$(date +%s)
	CTL modules > "$FILES/logs/modules-gone.out" 2>&1 || fail "taking the module out failed: $(tail -5 "$FILES/logs/modules-gone.out")"
	tail -3 "$FILES/logs/modules-gone.out"
	echo "took $(($(date +%s) - start)) s"
	grep -q "Taking out of the world: mod-gone" "$FILES/logs/modules-gone.out" || fail "the module that went wasn't seen"
	tables=$(echo "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'acore_world' AND table_name = 'mod_gone'" | CTL sql)
	[ "$tables" = 0 ] || fail "the world database still has what the module put in"
	if grep -qxF mod-gone "$FILES/mysql/.world-modules"; then fail "the module that went is still on record"; fi
	CTL modules > "$FILES/logs/modules-again.out" 2>&1 || fail "ctl.sh modules failed the second time"
	if grep -q "Taking out" "$FILES/logs/modules-again.out"; then fail "the world database was made again for nothing"; fi

	start_world world-noraces.out
	wait_world_ready
	applied=$(echo "SELECT COUNT(*) FROM updates WHERE state = 'MODULE'" | CTL sql acore_world)
	echo "the realm's module updates in the new world database: $applied"
	[ "$applied" -gt 0 ] || fail "the realm's modules didn't put their SQL in again"
	python3 "$ROOT/warcraft/server/auth_check.py" characters 127.0.0.1 tester secret123 |
		tee "$FILES/logs/characters-noraces.out" || fail "the character list didn't come"
	grep -q "^Testhero" "$FILES/logs/characters-noraces.out" || fail "the human left the list"
	# Unless a module the app's user picked makes race 12 playable (mod-worgoblin's Worgen).
	worgen=$(echo "SELECT COUNT(*) FROM playercreateinfo WHERE race = 12" | CTL sql acore_world)
	if [ "$worgen" = 0 ]; then
		if grep -q "^Testwolf" "$FILES/logs/characters-noraces.out"; then fail "the Worgen is in the character list"; fi
	else
		echo "A module of this realm makes race 12 playable: the Worgen is listed."
	fi
	kept=$(echo "SELECT COUNT(*) FROM characters WHERE name = 'Testwolf'" | CTL sql acore_characters)
	echo "characters of the custom races kept: $kept"
	[ "$kept" = 1 ] || fail "the Worgen was deleted"
	python3 "$ROOT/warcraft/server/auth_check.py" world 127.0.0.1 tester secret123 Testhero ".remix" > "$FILES/logs/world-remix-off.out" ||
		fail "the human couldn't get into the world after the races went"
	cat "$FILES/logs/world-remix-off.out"
	grep -q "in the world on map" "$FILES/logs/world-remix-off.out" || fail "the human couldn't get into the world after the races went"
	grep -q "Wrath Remix: off on this realm" "$FILES/logs/world-remix-off.out" || fail "Wrath Remix answered on the ChromieCraft realm"
	stop_world
	grep -q "Wrath Remix: off" "$FILES/logs/world.out" || fail "the ChromieCraft realm's world server didn't say Wrath Remix is off"

	echo "== Wrath Remix: the second realm"
	start=$(date +%s)
	CTL dbimport remix > "$FILES/logs/dbimport-remix.out" 2>&1 || fail "the Remix databases weren't made: $(tail -5 "$FILES/logs/dbimport-remix.out")"
	echo "the Remix databases took $(($(date +%s) - start)) s"
	for db in acore_world_remix acore_characters_remix acore_playerbots_remix; do
		tables=$(echo "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$db'" | CTL sql)
		echo "$db: $tables tables"
	done
	[ "$(echo "SELECT COUNT(*) FROM creature_template" | CTL sql acore_world_remix)" -gt 20000 ] || fail "the Remix world database looks empty"
	[ "$(echo "SELECT COUNT(*) FROM updates_include WHERE path LIKE '%mod-wrath-remix%'" | CTL sql acore_world_remix)" = 1 ] ||
		fail "the Remix world database doesn't list Wrath Remix's SQL"
	[ "$(echo "SELECT COUNT(*) FROM updates_include WHERE path LIKE '%mod-wrath-remix%'" | CTL sql acore_world)" = 0 ] ||
		fail "the ChromieCraft world database lists Wrath Remix's SQL"
	CTL modules remix > "$FILES/logs/modules-remix.out" 2>&1 || fail "ctl.sh modules remix failed"
	[ -f "$FILES/mysql/.world-modules-remix" ] || fail "the Remix realm's modules aren't on record"
	grep -q "WrathRemix.Enable = 1" "$FILES/etc-remix/modules/mod_wrath_remix.conf" || fail "Wrath Remix isn't on in its realm's config"
	grep -q "WrathRemix.Enable = 0" "$FILES/etc/modules/mod_wrath_remix.conf" || fail "Wrath Remix isn't off in ChromieCraft's config"
	grep -q "^RealmID = 2" "$FILES/etc-remix/worldserver.conf" || fail "the Remix world server isn't realm 2"
	grep -q "^StartPlayerLevel = 10" "$FILES/etc-remix/worldserver.conf" || fail "Timerunners don't start at 10"

	# Both realms in the realm list (the auth server reads it again every 20 s or so).
	CTL realmlist 192.168.1.50 || fail "ctl.sh realmlist failed"
	for _ in $(seq 40); do
		realms=$(python3 "$ROOT/warcraft/server/auth_check.py" login 127.0.0.1 tester secret123 || true)
		echo "$realms" | grep -q "Wrath Remix" && break
		sleep 2
	done
	echo "$realms"
	echo "$realms" | grep -q "Wrath Remix	127.0.0.1:8086" || fail "the realm list doesn't have Wrath Remix at 127.0.0.1:8086"
	echo "$realms" | grep -q "ChromieCraft	127.0.0.1:8085" || fail "the realm list lost ChromieCraft"

	start_world world-remix.out remix
	wait_world_ready
	grep -q "Wrath Remix: on (realm 2)" "$world_log" || fail "Wrath Remix didn't turn on in its realm"
	grep -q "Wrath Remix: the game's patch written" "$world_log" || fail "Wrath Remix didn't write the game's patch"
	# The allied races are ChromieCraft's alone: their patch set aside (not in the game, kept for
	# ChromieCraft), none of their SQL in Remix's world, its races 15 to 18 the game's own.
	grep -q "^AlliedRaces.Enable = 0" "$FILES/etc-remix/modules/mod_allied_races.conf" || fail "the allied races aren't off in Wrath Remix's config"
	grep -q "^AlliedRaces.Enable = 1" "$FILES/etc/modules/mod_allied_races.conf" || fail "the allied races aren't on in ChromieCraft's config"
	# Quest drops' raised rates too are ChromieCraft's alone.
	grep -q "^QuestDrops.Enable = 1" "$FILES/etc-remix/modules/mod_quest_drops.conf" || fail "quest drops aren't on in Wrath Remix's config"
	grep -q "^LevelScaling.Enable = 0" "$FILES/etc-remix/modules/mod_level_scaling.conf" || fail "level scaling isn't off in Wrath Remix's config"
	grep -q "^LevelScaling.Enable = 1" "$FILES/etc/modules/mod_level_scaling.conf" || fail "level scaling isn't on in ChromieCraft's config"
	grep -q "^QuestDrops.Enable = 1" "$FILES/etc/modules/mod_quest_drops.conf" || fail "quest drops aren't on in ChromieCraft's config"
	# A home in Brill (mod-brill-home) is ChromieCraft's alone: off in Remix's config, its rows not in Remix's world.
	grep -q "^BrillHome.Enable = 0" "$FILES/etc-remix/modules/mod_brill_home.conf" || fail "the Brill home is on in Wrath Remix's config"
	grep -q "^BrillHome.Enable = 1" "$FILES/etc/modules/mod_brill_home.conf" || fail "the Brill home is off in ChromieCraft's config"
	[ "$(echo "SELECT COUNT(*) FROM gameobject_template WHERE entry BETWEEN 970100 AND 970109" | CTL sql acore_world_remix)" = 0 ] ||
		fail "the house is in Wrath Remix's world"
	! ls "$FILES"/client/Data/*/patch-*-V.MPQ > /dev/null 2>&1 && ls "$FILES"/client/Data/*/patch-*-V.MPQ.aside > /dev/null 2>&1 ||
		fail "the Brill home's patch (Corn, the cellar) is in the game on Wrath Remix (or wasn't kept aside)"
	[ ! -e "$FILES/client/Data/patch-V.MPQ" ] && [ -e "$FILES/client/Data/patch-V.MPQ.aside" ] ||
		fail "the allied races' patch is in the game on Wrath Remix (or wasn't kept aside)"
	[ "$(echo "SELECT COUNT(*) FROM playercreateinfo WHERE race IN (15, 16, 17, 18)" | CTL sql acore_world_remix)" = 0 ] ||
		fail "the allied races can be made on Wrath Remix"
	[ "$(echo "SELECT COUNT(*) FROM chrraces_dbc WHERE ID IN (15, 16, 17, 18, 24, 25, 26, 27)" | CTL sql acore_world_remix)" = 0 ] ||
		fail "Wrath Remix's world has the allied races' race rows"
	[ "$(echo "SELECT COUNT(*) FROM quest_template WHERE ID BETWEEN 950000 AND 979999" | CTL sql acore_world_remix)" = 0 ] ||
		fail "Wrath Remix's world has the allied races' quests"
	[ "$(echo "SELECT COUNT(*) FROM quest_template WHERE ID IN (98299, 97558, 86576)" | CTL sql acore_world_remix)" = 0 ] ||
		fail "Wrath Remix's world has WoW: Forever's quests"
	[ "$(echo "SELECT COUNT(*) FROM creature WHERE guid BETWEEN 8600000 AND 8699999" | CTL sql acore_world_remix)" = 0 ] ||
		fail "Wrath Remix's world has WoW: Forever's new NPCs"
	[ "$(echo "SELECT COUNT(*) FROM playercreateinfo WHERE race IN (15, 16, 17, 18)" | CTL sql acore_world)" -gt 0 ] ||
		fail "ChromieCraft lost the allied races"
	# The Murlocs and the Naga likewise: their patch set aside, none of their rows in Remix's world.
	grep -q "^MurlocNaga.Enable = 0" "$FILES/etc-remix/modules/mod_murloc_naga.conf" || fail "the Murlocs and the Naga aren't off in Wrath Remix's config"
	[ ! -e "$FILES/client/Data/enUS/patch-enUS-T.MPQ" ] && [ -e "$FILES/client/Data/enUS/patch-enUS-T.MPQ.aside" ] ||
		fail "the Murlocs' and the Naga's patch is in the game on Wrath Remix (or wasn't kept aside)"
	[ "$(echo "SELECT COUNT(*) FROM playercreateinfo WHERE race IN (19, 20)" | CTL sql acore_world_remix)" = 0 ] ||
		fail "Murlocs or Naga can be made on Wrath Remix"
	# The Worgen and Goblins likewise: their patch set aside, none of mod-worgoblin's SQL or rows in
	# Remix's world.
	grep -q "^WorgenGoblin.Enable = 0" "$FILES/etc-remix/modules/mod_worgen_goblin.conf" || fail "the Worgen and Goblins aren't off in Wrath Remix's config"
	grep -q "^WorgenGoblin.Enable = 1" "$FILES/etc/modules/mod_worgen_goblin.conf" || fail "the Worgen and Goblins aren't on in ChromieCraft's config"
	[ ! -e "$FILES/client/Data/patch-U.MPQ" ] && [ -e "$FILES/client/Data/patch-U.MPQ.aside" ] ||
		fail "the Worgen's and Goblins' patch is in the game on Wrath Remix (or wasn't kept aside)"
	[ "$(echo "SELECT COUNT(*) FROM playercreateinfo WHERE race IN (9, 12)" | CTL sql acore_world_remix)" = 0 ] ||
		fail "Worgen or Goblins can be made on Wrath Remix"
	[ "$(echo "SELECT COUNT(*) FROM charsections_dbc WHERE RaceID IN (9, 12)" | CTL sql acore_world_remix)" = 0 ] ||
		fail "Wrath Remix's world has the Worgen's and Goblins' looks"
	# Against the DBC files its world server read (the modules' over the game's, when there are).
	remix_data=$(sed -n 's/^DataDir = "\(.*\)"$/\1/p' "$FILES/etc-remix/worldserver.conf")
	python3 "$ROOT/warcraft/server/remix_check.py" patch "$FILES/client/Data/patch-Y.MPQ" "$remix_data/dbc" ||
		fail "Wrath Remix's patch for the game isn't right"
	grep -E "Wrath Remix: [0-9]+ level bands" "$world_log" || fail "Wrath Remix didn't load its tables"
	[ "$(echo "SELECT COUNT(*) FROM creature_template WHERE entry = 770001" | CTL sql acore_world_remix)" = 1 ] || fail "Moratari isn't in the Remix world"
	[ "$(echo "SELECT COUNT(*) FROM quest_template WHERE ID >= 1000000" | CTL sql acore_world_remix)" = 0 ] || fail "quests in the millions (the core's quest table grows to the highest id)"
	[ "$(echo "SELECT COUNT(*) FROM creature_template WHERE entry = 770001" | CTL sql acore_world)" = 0 ] || fail "Moratari is in the ChromieCraft world"
	[ "$(echo "SELECT QuestLevel FROM quest_template WHERE ID = 11672" | CTL sql acore_world)" = 71 ] || fail "Remix changed ChromieCraft's quests"
	echo "Enlistment Day: level $(echo "SELECT QuestLevel FROM quest_template WHERE ID = 11672" | CTL sql acore_world_remix) on Wrath Remix"

	export WORLD_PORT=8086
	python3 "$ROOT/warcraft/server/auth_check.py" world 127.0.0.1 tester secret123 Timerunner | tee "$FILES/logs/remix-client.out" ||
		fail "a character couldn't get into the Remix world"
	# (made in the Gilded Rose, in their chair, where the opening begins)
	grep -q "level 10, map 0, zone" "$FILES/logs/remix-client.out" || fail "the Timerunner isn't a level 10 in Stormwind's tavern"
	python3 "$ROOT/warcraft/server/auth_check.py" characters 127.0.0.1 tester secret123 | tee "$FILES/logs/remix-characters.out"
	if grep -q "^Testhero" "$FILES/logs/remix-characters.out"; then fail "ChromieCraft's character is on Wrath Remix"; fi

	echo "== Wrath Remix's prologue"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Timerunner 1 1 \
		"$ROOT/warcraft/server/remix_prologue.steps" | tee "$FILES/logs/remix-prologue.out" || fail "the prologue didn't play through"
	# Report Time Anomaly, asked for during the Bazaar's Keepers: the realm's report for the app to send to
	# GitHub, with the quest the Timerunner is on, who gave it, who they've spoken to since, and the
	# way they came.
	report=$(ls "$FILES/run/reports"/anomaly-*.md 2> /dev/null | head -1)
	[ -n "$report" ] || fail "Report Time Anomaly wrote no report in files/run/reports"
	echo "Time anomaly report $(basename "$report"):"
	sed -n '1,16p' "$report"
	for text in "# Time anomaly: The Bazaar's Keepers (Timerunner, level" "**What happened:** CI's report, from the Bazaar" \
		"**The Bazaar's Keepers** (77021), in progress" "from Moratari (770001)" "Spoken to since it was taken: Zephyr (770006)" \
		"### The way here" "Took **Out of Time** (77010)" "Turned in **The Plan** (77011)" \
		"Turned in **Old Habits** (77020)" "Spoke to Timeworn Instructor (770101)"; do
		grep -qF "$text" "$report" || fail "the time anomaly report hasn't \"$text\""
	done
	echo "== Moratari beside a Timerunner (the companion)"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Companion 1 1 \
		"$ROOT/warcraft/server/remix_companion.steps" | tee "$FILES/logs/remix-companion.out" ||
		fail "Moratari didn't walk with the Timerunner in the Borean Tundra"
	band=$(grep -o "band check: [0-9]* banded creatures, levels [0-9]* to [0-9]*" "$FILES/logs/remix-prologue.out" | tail -1)
	echo "Valiance Keep: $band"
	[ -n "$band" ] && [ "${band##* }" -le 23 ] || fail "Borean Tundra's creatures aren't at Chapter I's levels ($band)"
	row=$(echo "SELECT r.bronze, r.chapter FROM remix_character r JOIN characters c ON c.guid = r.guid WHERE c.name = 'Timerunner'" | CTL sql acore_characters_remix)
	echo "Timerunner's record (Bronze owed, chapter): $row"
	[ "$row" = "$(printf '0\t1')" ] || fail "the Timerunner's chapter wasn't kept, or Bronze is owed ($row)"
	bronze=$(echo "SELECT SUM(t.count) FROM item_instance t JOIN characters c ON c.guid = t.owner_guid WHERE c.name = 'Timerunner' AND t.itemEntry = 77001" | CTL sql acore_characters_remix)
	echo "Timerunner's Bronze: $bronze"
	# (at least the prologue's and the lesson's: more is fine, a Timerunner is meant to have plenty)
	[ "${bronze:-0}" -ge 11200 ] 2> /dev/null || fail "the Timerunner doesn't carry 11,200 Bronze or more ($bronze)"
	[ "$(echo "SELECT COUNT(*) FROM character_inventory i JOIN item_instance t ON t.guid = i.item JOIN characters c ON c.guid = i.guid WHERE c.name = 'Timerunner' AND t.itemEntry = 46017" | CTL sql acore_characters_remix)" = 1 ] ||
		fail "Val'anyr, bought from Durus, isn't in the bags"
	[ "$(echo "SELECT COUNT(*) FROM character_inventory i JOIN item_instance t ON t.guid = i.item JOIN characters c ON c.guid = i.guid WHERE c.name = 'Timerunner' AND t.itemEntry = 42985" | CTL sql acore_characters_remix)" = 1 ] ||
		fail "the heirloom bought from Alurmi isn't in the bags"
	# The warrior's starter kit, on (every piece in its slot: heirlooms and greens), its
	# abilities (Defensive Stance from the class quest, Bloodrage from the trainer) and its axe skill
	# at its level's maximum (five a level).
	kit=$(echo "SELECT GROUP_CONCAT(CONCAT(i.slot, ':', t.itemEntry) ORDER BY i.slot) FROM character_inventory i JOIN item_instance t ON t.guid = i.item JOIN characters c ON c.guid = i.guid WHERE c.name = 'Timerunner' AND i.bag = 0 AND i.slot < 19" | CTL sql acore_characters_remix)
	echo "Timerunner's gear: $kit"
	for piece in 2:42949 4:48685 5:832 6:2978 7:3302 9:2980 10:8350 11:50255 12:42991 14:2284 15:42943; do
		case ",$kit," in *",$piece,"*) ;; *) fail "the warrior's starter kit isn't on ($piece missing: $kit)" ;; esac
	done
	[ "$(echo "SELECT COUNT(*) FROM character_spell s JOIN characters c ON c.guid = s.guid WHERE c.name = 'Timerunner' AND s.spell IN (71, 2687)" | CTL sql acore_characters_remix)" = 2 ] ||
		fail "the warrior didn't learn Defensive Stance and Bloodrage"
	axe=$(echo "SELECT CONCAT(k.value, ' ', c.level * 5) FROM character_skills k JOIN characters c ON c.guid = k.guid WHERE c.name = 'Timerunner' AND k.skill = 172" | CTL sql acore_characters_remix)
	echo "Timerunner's two-handed axe skill, and its level's maximum: $axe"
	[ -n "$axe" ] && [ "${axe% *}" = "${axe#* }" ] || fail "the warrior's two-handed axe skill isn't its level's maximum ($axe)"
	[ "$(echo "SELECT kit FROM remix_character r JOIN characters c ON c.guid = r.guid WHERE c.name = 'Timerunner'" | CTL sql acore_characters_remix)" = 1 ] ||
		fail "the starter kit isn't on record"

	# The campaign's transitions after Chapter I, each side with a character of its own (the
	# original quests before them given by GM commands).
	echo "== Wrath Remix's campaign, Chapters II to VII and the end"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Wintergarde 1 1 \
		"$ROOT/warcraft/server/remix_campaign_alliance.steps" | tee "$FILES/logs/remix-campaign-alliance.out" ||
		fail "the campaign's transitions didn't play through for the Alliance"
	python3 "$ROOT/warcraft/server/auth_check.py" script 127.0.0.1 tester secret123 Agmarshammer 2 1 \
		"$ROOT/warcraft/server/remix_campaign_horde.steps" | tee "$FILES/logs/remix-campaign-horde.out" ||
		fail "the campaign's transitions didn't play through for the Horde"
	# Both went home at the end (Back to Your Own Time): written for ChromieCraft, and taken off
	# Wrath Remix once let go.
	echo "== Wrath Remix's Timerunners gone home"
	ls -l "$FILES/run/transfers"
	for name in Wintergarde Agmarshammer; do
		grep -q "^$name$" "$FILES"/run/transfers/*.who || fail "$name wasn't written to go home to ChromieCraft"
	done
	# (kept on Wrath Remix until ChromieCraft has them: never on neither realm)
	kept=$(echo "SELECT COUNT(*) FROM characters WHERE name IN ('Wintergarde', 'Agmarshammer')" | CTL sql acore_characters_remix)
	[ "$kept" = 2 ] || fail "only $kept of the Timerunners going home are still on Wrath Remix before ChromieCraft has them"

	echo "== Wrath Remix's NPCs on the floor"
	echo "SELECT guid, map, position_x, position_y, position_z, Comment FROM creature WHERE guid BETWEEN 7704001 AND 7704399 ORDER BY guid" |
		CTL sql acore_world_remix > "$FILES/logs/remix-spawns.tsv"
	python3 "$ROOT/warcraft/server/remix_check.py" floors 127.0.0.1 tester secret123 Timerunner "$FILES/logs/remix-spawns.tsv" |
		tee "$FILES/logs/remix-floors.out" || fail "Wrath Remix has NPCs floating or buried"
	unset WORLD_PORT
	stop_world

	# The realm's bots are made where Timerunners begin; each one in the world is sent to its
	# chapter (those in the world a moment, as it shut down, aside).
	echo "== Wrath Remix's bots out of the Infinite Bazaar"
	sent=$(grep -c "sent from the Infinite Bazaar" "$world_log" || true)
	echo "bots sent from the Infinite Bazaar to their chapters: $sent"
	[ "$sent" -gt 0 ] || fail "no bot was sent from the Infinite Bazaar"
	left=$(echo "SELECT COUNT(*) FROM characters c JOIN acore_auth.account a ON a.id = c.account WHERE a.username LIKE 'RNDBOT%' AND c.zone <> 0 AND c.totaltime >= 30 AND c.map = 571 AND c.position_x BETWEEN 6274 AND 6514 AND c.position_y BETWEEN 1746 AND 1986" | CTL sql acore_characters_remix)
	[ "$left" = 0 ] || fail "$left of the realm's bots stayed at the Infinite Bazaar"

	echo "== ChromieCraft takes Wrath Remix's patch out of the game, and its Timerunners in"
	start_world world-again.out
	wait_world_ready
	grep -q "Wrath Remix: its patch is out of the game" "$world_log" || fail "ChromieCraft's world server didn't take Wrath Remix's patch out"
	[ ! -e "$FILES/client/Data/patch-Y.MPQ" ] || fail "Wrath Remix's patch is still in the game on ChromieCraft"
	# (its language folder's too, which hid the allied races' sounds there; and theirs is back)
	for looks in "$FILES"/client/Data/*/patch-*-Y.MPQ; do
		[ ! -e "$looks" ] || fail "Wrath Remix's $looks is still in the game on ChromieCraft"
	done
	[ -e "$FILES/client/Data/patch-V.MPQ" ] && [ ! -e "$FILES/client/Data/patch-V.MPQ.aside" ] ||
		fail "the allied races' patch didn't come back on ChromieCraft"
	[ -e "$FILES/client/Data/patch-U.MPQ" ] && [ ! -e "$FILES/client/Data/patch-U.MPQ.aside" ] ||
		fail "the Worgen's and Goblins' patch didn't come back on ChromieCraft"
	# home in their side's capital: Stormwind (map 0, zone 1519) and Orgrimmar (map 1, zone 1637)
	# (the world server queues their writes as it starts: they can land a moment after it's ready)
	for expected in "Wintergarde	0	1519" "Agmarshammer	1	1637"; do
		name=${expected%%	*}
		for _ in $(seq 30); do
			row=$(echo "SELECT name, map, zone FROM characters WHERE name = '$name'" | CTL sql acore_characters)
			[ "$row" != "$expected" ] || break
			sleep 1
		done
		echo "came home: $row"
		[ "$row" = "$expected" ] || fail "$name didn't come home to ChromieCraft in their capital ($row)"
	done
	[ -z "$(ls "$FILES"/run/transfers/*.dump 2> /dev/null)" ] || fail "ChromieCraft left Timerunners waiting to come home"
	stop_world

	# Taken off Wrath Remix at its next start, now that ChromieCraft has them.
	echo "== Wrath Remix lets go of its Timerunners who went home"
	start_world world-remix-again.out remix
	wait_world_ready
	# (as the world server starts, after its ready line: the deletions are queued writes too)
	for _ in $(seq 30); do
		gone=$(echo "SELECT COUNT(*) FROM characters WHERE name IN ('Wintergarde', 'Agmarshammer')" | CTL sql acore_characters_remix)
		[ "$gone" != 0 ] || break
		sleep 1
	done
	[ "$gone" = 0 ] || fail "$gone of the Timerunners who went home are still on Wrath Remix"
	stop_world
else
	# Without the server's data, it runs until it needs dbc, then stops.
	for _ in $(seq 300); do
		kill -0 "$world" 2> /dev/null || break
		[ -n "$jemalloc" ] || ! on_jemalloc || jemalloc=1
		sleep 1
	done
	exec 3>&-
	check_modules
	grep -qi "dbc" "$FILES/logs/world.out" || fail "the world server stopped before reaching the client data"
	tail -5 "$FILES/logs/world.out"
	echo "The world server got as far as the client data (dbc), which this run doesn't have."
fi

echo "== auth server, started again after the world server"
# A world server that stopped while loading leaves the realm flagged; the app clears the flag
# before starting the auth server, which otherwise refuses to run.
kill "$(cat "$FILES/run/authserver.pid")" 2> /dev/null || true
sleep 3
echo "UPDATE realmlist SET flag = flag & ~1 WHERE id = 1" | CTL sql acore_auth
CTL auth > "$FILES/logs/auth2.out" 2>&1 & pids+=($!)
wait_for 60 "the auth server didn't start again" port_open 3724
python3 "$ROOT/warcraft/server/auth_check.py" login 127.0.0.1 tester secret123 ||
	fail "the test account couldn't log in after the restart"

CTL db-stop
wait "${pids[0]}" 2> /dev/null || true

if [ ${#TRACE[@]} -gt 0 ]; then
	echo "== system calls"
	if [ "$(uname -m)" = aarch64 ]; then
		python3 -I "$ROOT/warcraft/server/seccomp_check.py" check "$FILES/server/" "$FILES"/logs/syscalls/* ||
			fail "the server made system calls Android doesn't allow apps"
	else
		# Elsewhere musl makes the older calls the phone's arm64 doesn't have (open, poll, ...),
		# which Android's policy for that architecture leaves out: listed, not counted.
		python3 -I "$ROOT/warcraft/server/seccomp_check.py" check "$FILES/server/" "$FILES"/logs/syscalls/* ||
			echo "(Not arm64: only CI's arm64 run counts.)"
	fi
fi
echo "PASSED"
