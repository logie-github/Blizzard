#!/usr/bin/env bash
# Takes every character the porter's rig test wrote (PorterRigTest: <rig>/ported/<name>.expect) into the realm's world
# with the realm's own headless client (realm/warcraft/server/auth_check.py), and checks what matters:
#
#   - it entered the world (the world server sent SMSG_LOGIN_VERIFY_WORLD) and its first login ran (at_login cleared);
#   - GM commands in the world answer with its level and money (.pinfo), its reputations, titles and place;
#   - after the logout (the world server saved it), the database still holds everything the porter wrote: its level
#     and money, each item in its slot (none mailed away as "can't be equipped"), every spell, skill, reputation,
#     quest, achievement and action button (the core deletes those it finds invalid as it loads a character);
#   - the world server's logs say nothing about it while it loaded and played (Errors.log, Server.log and its console:
#     lines naming it or its guid, and the loader's complaints).
#
#   prove.sh            starts the database, the login server and the world server as needed, checks every character,
#                       stops the world and login servers again (PORTER_KEEP=1 leaves them running)
#   prove.sh control    the check of the logs, shown to work: a ported character is given two rows the realm refuses
#                       (an action button of a spell that doesn't exist, a skill its class can't have), taken into the
#                       world, and the realm's complaints must be caught (the realm deletes the rows itself as it saves)
#
# BLIZZ_PORTER_RIG is the rig's folder (README.md beside this file). Exits non-zero if any check fails.
set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
RIG=${BLIZZ_PORTER_RIG:?set BLIZZ_PORTER_RIG to the folder of the rig}
FILES=$RIG/files
PORTED=$RIG/ported
ACCOUNT=${PORTER_ACCOUNT:-porter}
PASSWORD=${PORTER_PASSWORD:-porter123}
RIGSH=(bash "$HERE/rig.sh")
LOGS=(Errors.log Server.log world.out)
SQL() { "$RIG/mariadb/bin/mariadb" --no-defaults -h127.0.0.1 -P3310 -uacore -pacore --batch --skip-column-names "$@"; }

failures=0
fail() { echo "  FAIL: $*"; failures=$((failures + 1)); }
pass() { echo "  ok: $*"; }

declare -A E=() SIZE=()
# Reads <name>.expect into E.
expectations() {
	E=()
	while IFS=$'\t' read -r key value; do E[$key]=$value; done < "$1"
}

# Takes E's character into the world and runs its GM commands; the client's words in <name>.world.txt.
enter() {
	local name=${E[name]} steps=$PORTED/${E[name]}.steps
	for log in "${LOGS[@]}"; do SIZE[$log]=$(stat -c %s "$FILES/logs/$log" 2> /dev/null || echo 0); done
	printf '%s\n' "wait 3" "cmd .pinfo" "cmd .character reputation" "cmd .character titles" "cmd .gps" "wait 2" > "$steps"
	WORLD_PORT=8085 timeout 600 python3 -I "$REPO/realm/warcraft/server/auth_check.py" script 127.0.0.1 "$ACCOUNT" "$PASSWORD" \
		"$name" "${E[race]}" "${E[class]}" "$steps" > "$PORTED/$name.world.txt" 2>&1
}

# What the world server's logs said since enter(), its colours taken off.
said() {
	for log in "${LOGS[@]}"; do
		tail -c +$(( ${SIZE[$log]} + 1 )) "$FILES/logs/$log" 2> /dev/null | sed 's/\x1b\[[0-9;]*m//g' | sed "s|^|$log: |"
	done
}

# The lines of [said] about E's character, or the character loader's complaints (empty: none).
complaints() {
	local name=${E[name]} guid=${E[guid]}
	grep -E "$name|[Gg][Uu][Ii][Dd][: ]+$guid\b|Low: $guid\b|guid $guid\b|Player [^ ]*$guid\b" <<< "$1" | grep -vE "Login Character:|Logout Character:" || true
	grep -iE "Player::_Load|ActionButton loading problem|[Ww]ill be deleted|can't be loaded|doesn't exist|does not exist|not found|invalid" <<< "$1" || true
}

check() {
	local name=${E[name]} guid=${E[guid]} world=$PORTED/${E[name]}.world.txt
	echo "== $name (guid $guid): ${E[race]}/${E[class]}, level ${E[level]}"
	enter || fail "the session failed: $(tail -3 "$world" | tr '\n' ' ')"
	if grep -q "world: created" "$world"; then fail "auth_check made a new character: the ported one wasn't on the account"; fi
	if grep -q "in the world on map ${E[map]} " "$world"; then pass "entered the world: $(grep -m1 'in the world on map' "$world" | sed 's/^world: //')"; else fail "didn't enter the world on map ${E[map]}"; fi
	local level gold want
	level=$(grep -m1 -o '| Level: [0-9]*' "$world" | grep -o '[0-9]*$' || true)
	[ "$level" = "${E[level]}" ] && pass ".pinfo: level $level" || fail ".pinfo said level '${level}', not ${E[level]}"
	gold=$(grep -m1 -o '| Money: [0-9]*g[0-9]*s[0-9]*c' "$world" | sed 's/| Money: //' || true)
	want=$(( ${E[money]} / 10000 ))g$(( ${E[money]} / 100 % 100 ))s$(( ${E[money]} % 100 ))c
	[ "$gold" = "$want" ] && pass ".pinfo: money $gold" || fail ".pinfo said money '$gold', not $want"
	echo "  in the world: $(grep -c 'system:' "$world") lines from the realm; reputations it lists: $(grep -ciE 'exalted|revered|honored|friendly' "$world")"

	# After the logout: what the realm saved.
	local row db_level db_money db_online db_at_login items missing mailed spells skills reps quests achievements actions
	row=$(echo "SELECT level, money, online, at_login FROM characters WHERE guid = $guid" | SQL acore_characters)
	read -r db_level db_money db_online db_at_login <<< "$row"
	[ "$db_level" = "${E[level]}" ] && [ "$db_money" = "${E[money]}" ] && pass "saved: level $db_level, money $db_money" || fail "saved level/money $db_level/$db_money"
	[ "$db_online" = 0 ] && [ $(( db_at_login & 32 )) = 0 ] && pass "logged out, its first login done (at_login $db_at_login)" || fail "online $db_online, at_login $db_at_login"
	items=$(echo "SELECT CONCAT(ci.slot, ':', ii.itemEntry) FROM character_inventory ci JOIN item_instance ii ON ii.guid = ci.item WHERE ci.guid = $guid AND ci.bag = 0" | SQL acore_characters | sort)
	missing=0
	for item in ${E[items]}; do grep -qxF "$item" <<< "$items" || { missing=$((missing + 1)); echo "    missing item $item"; }; done
	[ "$missing" = 0 ] && pass "every item in its slot ($(wc -w <<< "${E[items]}"))" || fail "$missing items not where they were put"
	mailed=$(echo "SELECT COUNT(*) FROM mail WHERE receiver = $guid" | SQL acore_characters)
	[ "$mailed" = 0 ] && pass "nothing mailed away" || fail "$mailed mails (items the realm couldn't equip?)"
	spells=$(echo "SELECT spell FROM character_spell WHERE guid = $guid" | SQL acore_characters | sort -u)
	missing=$(comm -23 <(tr ' ' '\n' <<< "${E[spells]}" | grep . | sort -u) <(echo "$spells") | wc -l)
	[ "$missing" = 0 ] && pass "every spell kept ($(wc -w <<< "${E[spells]}") written, $(wc -l <<< "$spells") saved)" || fail "$missing spells the realm took away"
	skills=$(echo "SELECT CONCAT(skill, ':', value, ':', max) FROM character_skills WHERE guid = $guid" | SQL acore_characters)
	missing=0
	for skill in ${E[skills]}; do
		local id=${skill%%:*} rest=${skill#*:} value saved
		value=${rest%%:*}
		saved=$(grep "^$id:" <<< "$skills" | head -1)
		if [ -z "$saved" ]; then missing=$((missing + 1)); echo "    missing skill $skill"; continue; fi
		[ "$(cut -d: -f2 <<< "$saved")" -ge "$value" ] || { missing=$((missing + 1)); echo "    skill $id saved as $saved, written $skill"; }
	done
	[ "$missing" = 0 ] && pass "every skill kept ($(wc -w <<< "${E[skills]}"); riding $(grep '^762:' <<< "$skills" || echo none))" || fail "$missing skills lost or lowered"
	reps=$(echo "SELECT CONCAT(faction, ':', standing) FROM character_reputation WHERE guid = $guid" | SQL acore_characters)
	missing=0
	for rep in ${E[reputations]}; do grep -qxF "$rep" <<< "$reps" || { missing=$((missing + 1)); echo "    reputation $rep not kept"; }; done
	[ "$missing" = 0 ] && pass "every reputation kept ($(wc -w <<< "${E[reputations]}"))" || fail "$missing reputations changed"
	quests=$(echo "SELECT COUNT(*) FROM character_queststatus_rewarded WHERE guid = $guid" | SQL acore_characters)
	[ "$quests" = "${E[quests]}" ] && pass "$quests quests done" || fail "$quests quests done, ${E[quests]} written"
	achievements=$(echo "SELECT achievement FROM character_achievement WHERE guid = $guid" | SQL acore_characters | sort -u)
	missing=$(comm -23 <(tr ' ' '\n' <<< "${E[achievements]}" | grep . | sort -u) <(echo "$achievements") | wc -l)
	[ "$missing" = 0 ] && pass "every achievement kept ($(wc -w <<< "${E[achievements]}") written, $(grep -c . <<< "$achievements") saved)" || fail "$missing achievements lost"
	actions=$(echo "SELECT COUNT(*) FROM character_action WHERE guid = $guid" | SQL acore_characters)
	[ "$actions" -ge "${E[actions]}" ] && pass "$actions action buttons (${E[actions]} written)" || fail "$actions action buttons, ${E[actions]} written"

	# The world server's words while it loaded and played: none about it.
	local text found
	text=$(said)
	found=$(complaints "$text")
	if [ -z "$found" ]; then
		pass "the world server's logs say nothing about it ($(grep -c . <<< "$text") lines while it was in)"
	else
		fail "the world server said:"
		sort -u <<< "$found" | head -20 | sed 's/^/    /'
	fi
	grep -m1 "Login Character:\[$name\]" <<< "$text" | sed 's/^/  log: /' || true
}

ls "$PORTED"/*.expect > /dev/null 2>&1 || { echo "prove: nothing ported yet (run PorterRigTest)" >&2; exit 2; }
"${RIGSH[@]}" db-start
"${RIGSH[@]}" auth-start
"${RIGSH[@]}" world-start main

if [ "${1:-}" = control ]; then
	expect=$(ls "$PORTED"/*.expect | head -1)
	expectations "$expect"
	guid=${E[guid]}
	# A skill this class can't have: wands for the plate wearers, plate for the rest.
	case "${E[class]}" in 1 | 2 | 6) skill=228 ;; *) skill=293 ;; esac
	echo "== control: ${E[name]} (guid $guid) given an action button of spell 999999 (none) and skill $skill"
	printf 'REPLACE INTO character_action (guid, spec, button, action, type) VALUES (%s, 0, 100, 999999, 0);\nREPLACE INTO character_skills (guid, skill, value, max) VALUES (%s, %s, 1, 1);\n' \
		"$guid" "$guid" "$skill" | SQL acore_characters
	enter || fail "the session failed"
	found=$(complaints "$(said)")
	if grep -q "999999" <<< "$found" && grep -qE "skill \(?$skill\)?" <<< "$found"; then
		pass "the check caught both:"
		sort -u <<< "$found" | head -8 | sed 's/^/    /'
	else
		fail "the check missed them; it found: $found"
	fi
	left=$(echo "SELECT (SELECT COUNT(*) FROM character_action WHERE guid = $guid AND action = 999999) + (SELECT COUNT(*) FROM character_skills WHERE guid = $guid AND skill = $skill)" | SQL acore_characters)
	[ "$left" = 0 ] && pass "the realm deleted both rows as it saved the character" || fail "$left of the rows are still there"
else
	for expect in "$PORTED"/*.expect; do
		expectations "$expect"
		check
	done
fi

if [ "${PORTER_KEEP:-0}" != 1 ]; then
	"${RIGSH[@]}" world-stop
	"${RIGSH[@]}" auth-stop
fi
echo
if [ "$failures" = 0 ]; then echo "prove: all checks passed"; else echo "prove: $failures checks failed"; fi
[ "$failures" = 0 ]
