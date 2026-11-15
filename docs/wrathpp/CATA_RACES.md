# Wrath++: the Worgen, the Goblins and Cataclysm's starting areas

Wanted (the user, 2026-11-15): "Add the fix and the cata files to wrath++": Gilneas, Kezan and the Lost Isles with the Worgen and
Goblins playable and starting there, as on ChromieCraft (`realm/warcraft/modules/mod-worgen-goblin`), and the black-batch fix
(fires, waterfalls and rain drawn black; `tools/zones/package.py`, `single_textures`, in the zone package from 2026-11-15).

Status: **in progress; nothing here has run in the game or on a phone.**

## Races playable in Wrath++ (21 today, 23 with these)

The ten of 3.3.5 (Human, Orc, Dwarf, Night Elf, Undead, Tauren, Gnome, Troll, Blood Elf, Draenei), the ten allied races
(`ALLIED_RACES.md`) and the High Elf; then the Worgen and the Goblins. The Ice Troll was never playable: it is one of the
game's creature-only race rows, which is why its id is what the High Elf takes now.

## Ids

Worgen 12 and Goblin 9 as the module has them. High Elf 21 (was 12). Creature rows: Northrend Skeleton 20 folded into Skeleton 15,
Ice Troll 21 into Forest Troll 18 (their race row and looks dropped, their creatures take the other's), then Goblin creatures
9 to 20 and Fel Orc creatures 12 to 32 (`MOVED`). The module's own moves (9 and 12 to 28 and 29) are those of ChromieCraft's
ids and are replaced for Wrath++.

## Stages

1. **Ids** (done in the generator: `FOLDED` in `mod-allied-races/tools/build_data.py`, the profile): the committed
   `wrathpp_races_world.sql` is regenerated from the next looks run's artifact (CI warns while it differs).
2. **The module's tables for Wrath++**: `mod-worgen-goblin/tools/build_data.py` with a Wrath++ profile (its `MOVED` empty: stage 1 moves
   them), its client change files and the zones' merged into the looks package (`sl_looks.py assemble`).
3. **The server**: `WorgenGoblin.Enable 1` and `StartingAreas 1` for Wrath++ (`ctl.sh`), its world SQL in `acore_world_wrathpp`
   (never another realm's), the zone maps in Wrath++'s own data folder (never the shared `data/`: `ISOLATION_MANIFEST.md`),
   the zone package in `WOW_ZONES_DIR`.
4. **The app**: the zone package downloaded for Wrath++, the creator's Worgen and Goblin buttons (`WrathppAlliedRaces`).
5. **Tests**: `test-isolation.sh` for the new paths, the rig with 23 races.
