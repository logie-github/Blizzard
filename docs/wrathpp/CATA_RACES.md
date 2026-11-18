# Wrath++: the Worgen, the Goblins and Cataclysm's starting areas

Wanted (the user, 2026-11-15): "Add the fix and the cata files to wrath++": Gilneas, Kezan and the Lost Isles with the Worgen and
Goblins playable and starting there, as on ChromieCraft (`realm/warcraft/modules/mod-worgen-goblin`), and the black-batch fix
(fires, waterfalls and rain drawn black; `tools/zones/package.py`, `single_textures`, in the zone package from 2026-11-15).

Status 2026-11-17: **the native mod's half is built (283c959: the saved choices' array moved at load where the creation code holds the expected 5 to 48 operands; WrathPP_MaxRace says 21 or 63; compiled by CI, not run on a phone: the next start report's log line `race ids past 21:` says how many operands it found); the rest is not started.** It was blocked on the native mod: Race ids 1 to 21 are all taken (the High Elf 9, the allied races 12 to 20, the Dark Troll 21), and the client's creation screen holds ids to 21 only (`m_charPreferences[22][2]`), so the Worgen (12) and Goblin (9) cannot be added until the native mod moves that array (every instruction naming `0x00B6B0D0..0x00B6B17F` pointed at a larger one; only to be done where the patch can be checked against the real client, as a bad patch would stop every race), and the module's own ids (9, 12 in its C++, SQL and quest masks) are re-numbered. The Cataclysm zone package (YeaBwoi's `cata-zones`, with the black-batch fix of 2026-11-15) is ready for it.

## Races playable in Wrath++ (21 today, 23 with these)

The ten of 3.3.5 (Human, Orc, Dwarf, Night Elf, Undead, Tauren, Gnome, Troll, Blood Elf, Draenei), the ten allied races
(`ALLIED_RACES.md`) and the High Elf; then the Worgen and the Goblins. The Ice Troll was never playable: it is one of the
game's creature-only race rows, which is why its id is what the High Elf takes now.

## Ids

The client's `m_charPreferences[22][2]` takes race ids to 21 only (`ALLIED_RACES.md`), and the allied races and the High Elf now fill
9 and 12 to 21, the ids the Worgen (12) and Goblins (9) need. So these two races wait for a change of the native mod: the array moved to
a larger one (every instruction that names `0x00B6B0D0` to `0x00B6B17F` pointed at it), and the other tables the client sizes by race
(`SoundInterface2Emotes::m_soundIds[22][2]`) checked. Until then their zones can be reached by teleport only.

## Stages

1. **Ids** (done: the profile; `FOLDED` in the generator is unused now): the committed `wrathpp_races_world.sql` is regenerated from the next looks run's artifact (CI warns while it differs).
1b. **The native mod's array**: `m_charPreferences` relocated to 40 races (not started).
2. **The module's tables for Wrath++**: `mod-worgen-goblin/tools/build_data.py` with a Wrath++ profile (its `MOVED` empty: stage 1 moves
   them), its client change files and the zones' merged into the looks package (`sl_looks.py assemble`).
3. **The server**: `WorgenGoblin.Enable 1` and `StartingAreas 1` for Wrath++ (`ctl.sh`), its world SQL in `acore_world_wrathpp`
   (never another realm's), the zone maps in Wrath++'s own data folder (never the shared `data/`: `ISOLATION_MANIFEST.md`),
   the zone package in `WOW_ZONES_DIR`.
4. **The app**: the zone package downloaded for Wrath++, the creator's Worgen and Goblin buttons (`WrathppAlliedRaces`).
5. **Tests**: `test-isolation.sh` for the new paths, the rig with 23 races.

## Where the module's race ids stand (2026-11-17)

- **C++**: the two races' ids are now config keys, `WorgenGoblin.GoblinRace` (default 9) and `WorgenGoblin.WorgenRace` (default 12), read in
  `WorgenGoblin.cpp` and `WorgenGoblinForms.cpp`; ChromieCraft's behaviour is unchanged. Wrath++ would set them to 22 and 23.
- **Not yet**: `tools/build_data.py` and `tools/zones/quests.py` take the ids and masks (`GOBLIN, WORGEN = 9, 12`; `1 << 8`, `1 << 11`) as constants, and the
  rows they copy from mod-worgoblin (ChrRaces, CharStartOutfit, CharBaseInfo, the races' bits in reputation, skill and spell masks) carry 9 and 12 and
  their bits: those need a map from the old ids and bits to the new ones, and the data regenerated (it needs the mod-worgoblin source and the core's base
  SQL). The creature races that move (`MOVED` in `races_profile.py`) would have to leave 22 and 23 free: 9 to 32, 12 to 24, 13 to 25 ... 19 to 31 and the
  two folded (20 into 15, 21 into 18).

## Update (2026-11-17, later)

- The module's data builder takes the two races' ids (`WORGEN_GOBLIN_RACES=22,23`, goblin then worgen) and gives mod-worgoblin's rows, race fields and mask bits
  the new ids; with its own ids it still makes the committed data byte for byte (CI: `wrathpp-cata-data.yml`, which also makes Wrath++'s: an artifact).
- Wrath++'s creature races now move so that 22 and 23 stay free: 9 to 32, 12 to 19 up by twelve (24 to 31), and the Northrend Skeletons (20) and Ice Trolls (21)
  fold into the Skeletons and Forest Trolls (`races_profile.py`).
- Still to do: the zone data (`tools/zones`) for these ids; the module's client changes merged into the looks package and its SQL into the Wrath++ server; the
  realm's config (`WorgenGoblin.Enable 1`, `GoblinRace 22`, `WorgenRace 23`) and data folder; the app's zone download; the creator's buttons; all after the phone's check of the array move.

## Change of plan (2026-11-17, evening): the Worgen and Goblin keep 9 and 12

Instead of giving the module new ids (its C++, SQL and the third-party mod-worgoblin's own code name 9 and 12), Wrath++ leaves 9 and 12 to the Goblins and
Worgen and puts its own races above 21: the High Elf is **22** and the Void Elf **23** (the allied races 13 to 20 and the Dark Troll 21 stay). The native mod's
larger saved-choices array (`WrathPP_MaxRace`, 283c959) is what races 22 and 23 need; if it didn't apply on a phone, those two races crash the creation screen, and
the next start report's `race ids past 21:` line says whether it did. The creatures' races move clear: 13 to 19 to 24-27, 30-32; the module moves 9 and 12 to 28 and
29 itself. The realm (`ctl.sh`) turns the module on for Wrath++ (`WorgenGoblin.Enable 1`; `StartingAreas 1` once the app has downloaded the zones package, 18 November 2026: `WrathppZones`, `zones_data_realm`; else 0: they start with the Night Elves and Orcs) and runs mod-worgoblin's SQL into `acore_world_wrathpp`; the looks package carries the module's client table changes (`wrathpp-looks.yml`).
