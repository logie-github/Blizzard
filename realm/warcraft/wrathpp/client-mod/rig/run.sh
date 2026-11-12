#!/bin/sh
# Wrath++'s creator run on the rig: the 3.3.5 creation screen put together from the phone's own glue files, the client's
# decompiled creation logic and the game's tables (README.md).
#   run.sh WORK CREATOR.lua WrathppLooks.lua CLIENT_DBC STOCK_DBC
# WORK: a folder to work in (the phone's files are fetched into WORK/stock unless they are there).
# CLIENT_DBC: the looks' DBFilesClient (CharSections.dbc, CharacterFacialHairStyles.dbc), as the game has them.
# STOCK_DBC: the game's own tables (ChrRaces, ChrClasses, CharBaseInfo, FactionTemplate, FactionGroup: data.zip's dbc).
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$1"; CREATOR="$2"; LOOKS="$3"; CLIENT="$4"; STOCK="$5"
mkdir -p "$WORK/stock" "$WORK/data" "$WORK/plain"
sh "$HERE/tools/fetch_stock.sh" "$WORK/stock"
for f in GlueParent GlueButtons CharacterCreate; do
	python3 -I "$HERE/tools/xml2lua.py" "$WORK/stock/$f.xml" "$WORK/data/$f.xml.lua"
	cp "$WORK/data/$f.xml.lua" "$WORK/plain/$f.xml.lua"
done
# the tables twice: with undead skins in them as the app's import puts them, and as the looks alone have them
python3 -I "$HERE/tools/undead_rows.py" "$CLIENT/CharSections.dbc" "$WORK/CharSections.undead.dbc" "$WORK/WrathppUndead.lua"
python3 -I "$HERE/tools/build_data.py" "$STOCK" "$WORK/CharSections.undead.dbc" "$CLIENT/CharacterFacialHairStyles.dbc" "$WORK/data"
python3 -I "$HERE/tools/build_data.py" "$STOCK" "$CLIENT/CharSections.dbc" "$CLIENT/CharacterFacialHairStyles.dbc" "$WORK/plain"
export RIG_WORK="$WORK"
U="$WORK/WrathppUndead.lua"
echo "== what the creator does"
luajit "$HERE/behaviour.lua" "$HERE" "$CREATOR" "$LOOKS" "$U"
echo "== turned off: the game's own screen whole again"
luajit "$HERE/off.lua" "$HERE" "$CREATOR" "$LOOKS" "$U"
echo "== every race, sex and class, every option's every choice (the phone's screen, 1125 x 768)"
luajit "$HERE/full.lua" "$HERE" "$CREATOR" "$LOOKS" "$U"
echo "== without undead skins"
RIG_DATA="$WORK/plain" luajit "$HERE/full.lua" "$HERE" "$CREATOR" "$LOOKS" - quick
echo "== without the native mod"
RIG_NATIVE=0 luajit "$HERE/full.lua" "$HERE" "$CREATOR" "$LOOKS" "$U" quick
echo "== a 4:3 screen (1024 x 768)"
RIG_W=1024 luajit "$HERE/full.lua" "$HERE" "$CREATOR" "$LOOKS" "$U" quick
echo "== a 16:9 screen (1366 x 768)"
RIG_W=1366 luajit "$HERE/full.lua" "$HERE" "$CREATOR" "$LOOKS" "$U" quick
echo "the rig: all passed"
