# Cataclysm backport: a converter that runs without an AI (`realm/warcraft/tools/catabackport`)

The user (18 November 2026): "Create a converter for the map etc files that I can run on device or on GitHub Actions that
would do the work for you of backporting the entire expansion of quests, NPC, locations, etc. That way it can still be done
you just don't have to do usage credits for it and after creating the tool you aren't involved at all."

This document is the design, written before the tool. Where a statement rests on something that was read or measured, the
source is named (`file:line`, a URL, a measured number). Where it does not, it says **UNVERIFIED**. Where a goal cannot be
met, it says so and says what the tool does instead (report, skip, flag).

Status of the tool is at the end ("What is built, what is not").

## 0. What "after creating the tool you aren't involved at all" asks of the tool

Everything an AI did by hand for the seven starting-area maps (Gilneas, Kezan, the Lost Isles and their terrain swaps:
`mod-worgen-goblin/tools/zones`) has to become code or pinned configuration:

| Done by hand for the seven maps | In the tool |
|---|---|
| Choosing which file ids a map needs (`data/zones/files.tsv`) | `inventory` + `fetch` read the maps' own files and take the closure of what the tiles place (ADT, M2, WMO, BLP), as `zones/files.py` does, for any map |
| Which map is a terrain swap of which (`common.OVERLAYS`) | `inventory` reads Cataclysm's own `Map.MapID`/`ParentMapID` (`UiMapAssignment`, `TerrainSwap`-style tables) into the manifest; a swap with no tiles of its own is made whole from its base (`package.maps`) |
| Fixing a format by looking at a crash | `validate` runs the Converter's checks and the tool's own structural checks on every output file; a file that fails is not shipped, is reported, and the map is marked `partial` |
| Picking ids for rows that clash (`build_tables.NEW_IDS`) | One pure function (`ids.py`): a stable id from the Cataclysm id, an allocation table written into the manifest, never chosen by hand |
| Knowing when a download failed | Retries with back-off, partial files named `.part`, a per-file size/hash record, a per-map `state.json`; a rerun does only what is missing |
| Reading the result | Every run writes `report.json` and `summary.txt` (per map: converted, skipped, failed, why) |

What cannot be made code (and so is a flag in the report, never a silent gap) is in sections 4 and 7.

## 1. Evidence gathered (and what could not be)

1. **wago.tools was down** (HTTP 500 on `/`, `/db2/Map/csv?build=4.4.2.60895`, `/api/builds`, `/api/casc/<id>`) on 18 November 2026,
   22:10 to 22:35 UTC, from this machine, repeated; the same text of 6.5 KB ("Server Error"). So **the build list, `Map.db2` and
   per-build counts could not be fetched**; the counts in section 2 come from the community listfile (below) and the existing
   zones code, and are labelled. This is also the first design requirement: a run must survive its source being down for
   hours (section 6, "Source outage").
2. **The community listfile** (`github.com/wowdev/wow-listfile`, release `community-listfile.csv`, 154 MB, 2,278,323 lines,
   fetched through the proxy) is the union of every build's names. It names 1,293 directories under `world/maps/`. It was used for the tile counts below. It
   is a union: a directory's count is an **upper bound** for any one build.
3. **The Converter** (`github.com/Bar3b0n3s/Converter`, MIT, HEAD `d71523c645ebe1313e15fe47fbea57577adf8c80` of 28 September 2026;
   README 24.5 KB, `docs/limits.md`, `src/wotlkconv/limits.py` read): pure Python 3.10+, no dependencies, 836 tests. The pin in
   `pins.json` is this sha unless the zones' own pin (kept in YeaBwoi, not in this repository: `realm/warcraft/server-version.env`
   does not carry it) is found; use the same sha as the zones package to get byte-identical results for the seven maps.
4. **The existing zones code** (`mod-worgen-goblin/tools/zones/*.py`, 4,588 lines read at the function level): file fetch by id from
   `https://wago.tools/api/casc/<fdid>?download&version=<BUILD>` with `BUILD = 4.4.2.60895` (Cataclysm Classic), tables from
   `https://wago.tools/db2/<Table>/csv?build=<BUILD>`, the cache layout `cache/files/<fdid>`, `cache/tables/<Name>.csv`
   (`common.py`), the conversion and the AzerothCore extractors (`package.py`), the world built from CPP's TDB in MariaDB
   (`build_world.py`, `db.py`).
5. **Measured by the seven maps** (the README of `mod-worgen-goblin`, `WrathppZones.kt`): `cata-zones.tar.xz` is 734,727,420 bytes,
   1,665,288,620 unpacked, for the 7 maps (listfile union: 60 + 149 + 11 + 4 + 4 + 12 + 1 = 241 root tiles; terrain swaps share tiles).
   That is about **3 MB packed and 7 MB unpacked per root tile**, including every model and texture those tiles place (shared
   between the maps). Its world: 601 kinds of creature, 277 of object, 19,162 creatures, 3,007 objects, 270 quests.
6. **The client's limit that matters most for ids**: the character's explored-areas bits are `PLAYER_EXPLORED_ZONES_1`, 128 fields of
   32 bits = 4,096 bits (`S/wxlsrc/WoW/Source/ObjectMgrClient/Mirror.cpp:338`); stock 3.3.5a uses bits to 3,617, so Cataclysm's
   (about 1,100 more areas than 3.3.5a) cannot all have their own bit: `build_tables.FREE_AREA_BITS` gives 3,618 to 4,095 (478 bits). Past
   that, areas share bits (flag them as "cannot be tracked as explored"; the world map still shows them).
7. **TrinityCore's Cataclysm Preservation Project** (CPP; `The-Cataclysm-Preservation-Project/TrinityCore`, branch `master` is 4.3.4, GPL-2.0 like TrinityCore):
   README read via `raw.githubusercontent.com`. Its releases page returns 403 through this machine's proxy, so the TDB asset's exact URL
   is **UNVERIFIED** here; the zones README names it: `TDB_full_world_434.22011_2022_01_09.sql`, then `sql/updates/world/4.3.4/*.sql`
   in order. The workflow downloads it with `gh release download` (Actions' own token reaches it) and records its SHA-256 in the
   run's report; the first run pins that hash.
8. Not verified here, flagged where used: what the Wrath++ phone does with 100+ maps (memory; see "Phone"), the sizes of Cataclysm's
   continents' tiles for the build.

## 2. Inventory of Cataclysm

### 2.1 Which builds exist and which is pinned
- **4.4.2.60895**, Cataclysm Classic (the last build of the 4.4.x line the zones package pins: `common.BUILD`). Its content is the
  post-Cataclysm 4.3.4 game (revamped Azeroth and Kalimdor, Deepholm, Hyjal, Vashj'ir, Uldum, Twilight Highlands, Tol Barad, the three raids and
  eleven dungeons of 4.0 to 4.3, battlegrounds), in today's file formats (split ADT, FileDataID-referenced M2/WMO, WDC4/5 DB2).
- **3.4.5.63697**, Wrath Classic (`common.WRATH_BUILD`): used only to tell the game's own files from Cataclysm's (`wrath_has`).
- Original **4.3.4.15595** (the last Cataclysm client) is MPQ-era: whether wago.tools serves it is **UNVERIFIED** (down), and its tables are pre-WDC (the Converter refuses them,
  README "Databases older than WDC1 ... are refused"). So **only Cataclysm Classic is a usable client source**, and the tool pins it
  (`pins.json`: `build`). `inventory` also lists the builds wago offers, when it is up, in the report, so a newer Cata Classic build is
  a one-line change, never an AI's job.

### 2.2 What the maps are
The real list is `Map.db2` at the pinned build (`inventory` writes it into `manifest.json`: id, directory, name, `InstanceType`, `ParentMapID`,
`ExpansionID`, tiles from the WDT, and the files the tiles name). This machine could not read it (item 1), so the following is the part the listfile shows
(root tiles and the number of listfile lines under the directory; **union over builds, upper bounds**):

| Group | Directories (listfile) | Root tiles | Listed files | Notes |
|---|---|---|---|---|
| Revamped continents | `azeroth` 1,368, `kalimdor` 1,043 (+`kalimdor 2`, 215) | up to 2,626 | 10,271 + 9,527 | These hold Hyjal, Vashj'ir, Twilight Highlands, Uldum, the Thousand Needles flood, the Barrens split. Cataclysm's zones are **areas of these maps**, not maps of their own |
| Old continents | `expansion01` 826, `northrend` 1,131 | | 4,994 | changed little in 4.x; **not converted by default** (Wrath++ has them) |
| New maps | `deephome` 100 (Deepholm), `lostisles` 149, `gilneas2` 60, `tolbarad` 42 + `tolbarad1` 51, `abyssalmaw` 25 (+ interior 9) | | | Deepholm is probably `Deephome` (the listfile has no `deepholm` directory; **UNVERIFIED**), which only the table can say (the zones code was given `Gilneas2`/`LostIsles` by hand) |
| Phased/terrain swaps | `gilneas`, `gilneasphase1/2`, `lostislesphase1/2`, `mounthyjalphase1`, `uldumphase*`, `twilighthighlands*phase*`, `hyjalpast` 30 | 1 to 30 each | | "made whole" by `package.maps` (3.3.5a cannot swap terrain) |
| Dungeons (4.0 to 4.3) | `deadminesinstance` 36, `shadowfang` 25, `grimbatoldungeon` 16, `deepholmedungeon` 16 (probably the Stonecore), `uldumdungeon` 16, `skywalldungeon` 25, `abyssalmaw` 25, `hyjal instance` 9, `zulaman` 25, `zul_gurub5man` 25, `blackrockspire_4_0` 9, `endtime`/`wellofeternity`/`hourof twilight` (names to be taken from the table) | 9 to 36 | 60 to 270 | small: the best proof maps |
| Raids | `blackwinglair` 16, `blackwingdescent` 9, `baradinhold` 9, `skywallraid` 9, `grimbatolraid` 16, `firelands1` 24 / `firelands2` 16, `dragonsoul`-era dirs (by table), `thehouroftwilight` 56 | 9 to 56 | | |
| Battlegrounds | `gilneas_bg_2` 16, `arathibasin2` 72 (the Cataclysm revamp), `warsonggulch2` 64, `tolbarad` (above) | | | |
| Scenario-like / later (not Cataclysm) | `azerothswarningscenario`, `hallsofvalor*scenario`, `*artifact`, `*classmount`, `islands_*`, numeric directories (modern) | | | **excluded**: `inventory` keeps only maps with `ExpansionID <= 3` at the pinned build and an existing WDT |

Developer maps in the listfile (`development` 1,838 tiles, `leveldesignland-devonly` 1,870) are named in no `Map.db2` row and are never taken.

### 2.3 Size and time, honestly
From item 5 (3 MB packed, 7 MB unpacked per root tile, 241 tiles took the zones package a Gilneas/Lost Isles CI job of about one build):
- A **small dungeon** (9 to 25 tiles): 30 to 75 MB packed; minutes.
- **Azeroth + Kalimdor as the revamped continents** (about 1,000 to 1,800 tiles with data in a Cataclysm build, **UNVERIFIED**; the listfile's 2,411 is the union of
  all builds): 3 to 5 GB packed, 7 to 12 GB unpacked, **above one release asset (2 GB)** and the cache (10 GB): split by tile row (section 6).
- Everything (continents, Deepholm, Tol Barad, about 14 dungeons, 8 raids, 4 battlegrounds): **6 to 10 GB packed**, 20 to 40 GB unpacked in total, but
  never more than one shard (about 1 to 3 GB) unpacked on a runner at a time.
- **Time**: the zones' conversion and extraction (`wotlkconv` at `-j4`, then `map_extractor`, `vmap4_extractor`, `vmap4_assembler`, `mmaps_generator`) was
  measured only in the zones' CI (build log, in YeaBwoi: not in this repository; **UNVERIFIED**). Planning figure: 2 to 6 core-hours per 100 tiles
  (mmaps dominate); the whole expansion is **60 to 150 runner-hours**, across about 40 to 120 jobs of under 3 hours: a day of wall time on free runners with a
  parallel limit of 20, and well inside the 6 h job limit. Fetching (about 20 to 60 k files over wago.tools) is the part that depends on the source's speed.

## 3. Client side: class by class

"Converter" = `wotlkconv` (item 3 above). "Tool" = what this tool adds. Limits are from `docs/limits.md`/`limits.py`.

| Class | Converter does | 3.3.5a cannot take | Handled |
|---|---|---|---|
| **ADT** (split `_tex0/_obj0/_lod`, `_tex1`/`_obj1`) | Merges root + `_tex0` + `_obj0` into the monolithic v18 tile with `MCIN`; names FileDataID placements; re-encodes liquid | 4 texture layers per chunk, 8x8 holes folded to 4x4, `_lod`, `_tex1/_obj1` (Legion); Cataclysm's 8-bit-alpha layers are fine | automatic. `files.map_files` filter (`.pm4 .h2o _tex1 _lod _obj1`) is reused. Liquid types missing from 3.3.5a's `LiquidType.dbc` are mapped to the kind (`package.fix_liquids`, `LIQUIDS_335`); not-fixable tiles: reported |
| **WDT** | v17, drops `MAID`, big-alpha flag; names a global WMO | `_lgt/_occ/_fogs/_mpv` sidecars | automatic; `package.fix_wdt`/`set_wdt_tiles` for swaps; the Tool verifies WDT tile set == tiles written |
| **WDL** | keeps the low-detail heightmap | | automatic; a missing WDL is copied from the base map (swaps) or reported |
| **WMO** (root, groups) | v17, rebuilds name tables, splits groups over 65,535 vertices, rebuilds BSP | shader > 6, blend > 6, > 2 UV/colour layers | automatic, lossy notes land in the report as `wmo.*` codes |
| **M2/skin/anim/skel** | MD21 to MD20 264, merges `.skel`, 4 profiles, `.anim` merge | > 65,535 vertices after compaction (`--split-models` makes new unplaced files), 4 texture units, bones > 256, Cata+ particle types, multi-texture emitters, packed gravity | automatic for the common case; `m2.limit.*` failures are **reported and the model is replaced by the zone's placeholder** list (`placeholders.json`, a small cube) so the tile still loads; never a crash |
| **BLP** | BC5 etc. to DXT/pal/raw; downscale | > 1024 (soft), non-power-of-two | `--max-texture-size 512` for the world, 4096 for interface, as `package.convert` (the 32-bit client's memory) |
| **DB2 to DBC** | `db convert` with a DBD definition and a 3.3.5a template; id offset | tables Wrath never had | **Not used for the whole table**: the zones' way, a row at a time (`build_tables.py`), because the rows must be renumbered into the realm's id space. The Tool does that generically (`tables.py`): for each 3.3.5a column name, take the Cataclysm column of the same name (WoWDBDefs, as `common.layout`), `0` if absent, and list unmatched columns in the report |
| **Map/AreaTable/Light/WMOAreaTable/WorldMapArea/Overlay/LoadingScreens/ZoneMusic/SoundAmbience** | no built-in mapping (`workflow.md`: "have no built-in mapping") | Cataclysm's area flags (flying, Wintergrasp bits) mean other things; explored bits past 4,095 (item 6) | `tables.py` generic rows with `AREA_FLAGS_DROPPED` and bit allocation (`ids.explore_bits`); a map's area count over the free bits is reported |
| **Minimaps** | writes `Textures/Minimap/<md5>.blp` and `md5translate.trs` | | automatic; `package.minimaps` logic reused through the line files |
| **Sounds/music** | copied byte for byte (ogg/mp3 are 3.3.5a's) | | copied; ids resolved with the listfile; SoundEntries rows for new files by `tables.py` |
| **Cameras (cinematics)** | | `CinematicCamera`'s M2 path | `package.cameras` logic, only for maps with intro cameras |
| **Interface art** (world map pictures, loading screens) | BLP conversion | | automatic; world maps of the new zones need `WorldMapArea` rows (`tables.py`) |
| **Textures with specular `_s` twins** | | the diffuse twin is wanted | `files.plain_twins` |
| **Terrain swaps** | | the client cannot swap | made into whole maps of their own (`package.maps`), as for Gilneas |

**What the client cannot do that no conversion fixes**, all reported per map, never hidden: (1) a revamped continent is a **changed** version of a map the
client already has: see "Replace or add" (section 5.1); (2) draw distance and the 32-bit memory budget on a phone (the zones' 512-pixel cap is kept);
(3) Cataclysm's cinematics and camera work (Deathwing's Cataclysm flythrough), flying in the old world (client allows it per area flag
and the server's `Flying` rules, flagged), worgen/goblin/Cata races' models (already done by the races session, not repeated here); (4) shaders:
water, lighting and sky `LightData` bands beyond 3.3.5a's (`build_tables.INT_BANDS`, floats) are mapped to the nearest, never exact.

## 4. Server side: the sources, the mapping, what is missing

### 4.1 Sources of content data
| Source | What | Licence | Schema | Completeness | Verdict |
|---|---|---|---|---|---|
| **CPP TDB 434** (TrinityCore 4.3.4 branch `master`, `sql/updates/world/4.3.4`) | world DB for the 4.3.4 client: `creature(_template, _addon, _equip, _text, _questender/starter, _loot)`, `gameobject*`, `quest_template(_addon)`, `smart_scripts`, `waypoint*`, `conditions`, `gossip_menu*`, `npc_vendor`, `trainer`, `spell_area`, `phase_area`, `graveyard_zone`, `areatrigger*`, `spell_*` | GPL-2.0 | TrinityCore 4.3.4 | the most complete: ~ 90% of Cata's world content, the reference source of the zones package | **primary**. Same engine lineage as AzerothCore: most columns match by name |
| **AzerothCore's own world** (`ac_world`) | the destination; also the 3.3.5a rows that already exist (do not duplicate) | AGPL-3.0 | | | destination and collision check |
| **cMaNGOS cata DB** (`cmangos/cata-db`) | partial 4.3.4 world | GPL-2.0 | MaNGOS-derived, different columns | partial; stale | **not used in v1** (second-source fallback hook only: a table CPP lacks) |
| **Other AzerothCore Cata efforts** | UNVERIFIED which are live; none is a maintained full DB | | | | not used |
| **Client tables** (Cata Classic DB2s from wago) | Map, AreaTable, CreatureDisplayInfo(+Extra), CreatureModelData, Item*, Spell*, Faction*, Vehicle*, Phase*, AreaTrigger, LoadingScreens | | WDC4/5 | exact | via `tables.py` |
| **wowhead / retail quest text** | | | | | not used (no scraping) |

### 4.2 Mapping onto AzerothCore (`world.py`)
The zones' `build_world.py` works by hand per table (ranges `ENTRY = 6,000,000`, `GUID = 10,000,000`, `PATH = 600,000,000`; masks `NPCFLAG_MASK`, `UNIT_FLAGS2_MASK`; race
map; `PHASES`). The generic tool works from a **table plan** (`world_plan.json`, data, not code) that says, for each destination table, the source query, the column rules and
the id rule. The rules are the same ones, made data:
- **Ids**: `entry' = 6,000,000 + entry` (templates, quests, gossip, texts, loot): the same on every map, so templates are **shared** and live in `core` packs, not per map.
  Spawn `guid` and `path`: `10,000,000 + guid_base(map) + n` (AzerothCore stops at `0xFFFFFF` = 16,777,215, so 6,777,215 spawns in total); `guid_base` is
  allocated by `inventory`/`world-index` from CPP's row counts per map, in the manifest (sorted by map id, stable).
- **Columns**: by name where the same; AzerothCore-only columns get their default; CPP-only columns are listed in the report (`dropped columns`); bit fields masked (`NPCFLAG_MASK 0x03FFFFFF`, `UNIT_FLAGS2_MASK`), races mapped through `RACES`, models through the display map.
- **Rows of 3.3.5a's own are never changed**: all rows are new, in ranges (the zones' rule, which makes a pack removable whole: `<map>_off.sql`).
- **SmartAI**: `smart_scripts` rows move with the new ids; actions/events AzerothCore's `SmartScriptMgr` lacks are looked up by the numeric id from a table (`smart_support.json`, built from `SmartScriptMgr.h` of the pinned core by `world-index`); a script using one is **dropped with a report line** and the creature keeps its template (it just does less).
- **Spells**: the zones' `spells.py` builds a 3.3.5a `Spell.dbc` row from Cataclysm's split tables (`Spell`, `SpellEffect`, `SpellAuraOptions`...) for the spells that content names; the tool takes the **closure of spell ids** named by a map's creatures, quests, auras, vendors, SmartAI and loot and calls that logic read-only for them (`world.py` imports `zones/spells.py`). Spell effects and auras 3.3.5a lacks: reported with a count per effect id (`spell.unsupported.<effect>`), the spell becomes a dummy.
- **Loot**: `*_loot_template` rows by entry; items by id: an item missing in AzerothCore's `item_template` is built from `Item-sparse` through `items.py` (read-only import), else the loot row is dropped and counted.
- **Phasing**: CPP's `phase_area`/`PhaseId`/`PhaseGroup` → 3.3.5a `phaseMask` bits (up to 31 plus the default per map) with `spell_area` auras (zones' `PHASES`, `GILNEAS_PHASES`): per map, the distinct phase ids are numbered into bits in order of first use; **more than 31 distinct phases on one map is a report line** and the excess merge into the default phase. `scripts.py` supplies the quest-gated phase auras generically as `quest_start/quest_end` of `phase_area`.
- **Vehicles**: `vehicles.py` (read-only) for the vehicle ids the closure names.

### 4.3 What a *faithful* whole expansion needs and AzerothCore lacks
Not automatable by a converter (it is C++ in the core or a design decision); the tool **detects and reports**, never claims done:

| Need | Why a converter cannot do it | What the tool does |
|---|---|---|
| Level 85 and Cataclysm's stat/item formulas | core data (`gtCombat*`, `player_xp_for_level`, `player_levelstats`, item scaling) | content at 80+ is taken as is; `mod-level-scaling` (ChromieCraft's, `warcraft/modules/mod-level-scaling`) shows how scaling is done there. Flag `content.level_above_cap` per map (count of creatures/quests above 80) |
| Mastery, new talent trees, reforging, guild perks and levels, archaeology, Cataclysm class changes, new spells' mechanics | core features and `Spell.dbc` semantic changes | not in scope; quest rewards that give such items are mapped to the nearest 3.3.5 item or dropped (report) |
| New aura/effect types of Cataclysm | core | dummy spell + report per id |
| PhaseGroup (many phases), `phase_definitions`, `terrainSwap` | the core's phasing is a 32-bit mask | mask bits (above); terrain swaps as separate maps (`add` mode) with `creature.map` duplicates for the swap maps (as `GILNEAS = (654, 638, 655)`) |
| Cataclysm scripting (C++ `ScriptName`s of CPP) | a script is code | the name is kept **only if AzerothCore or a module has it** (`scripts.py` logic); else the name is cleared and `left-for-later.txt`-style report lists the creature/spell/quest and the count. This is the largest gap: CPP has hundreds of C++ scripts for 4.x raids (Firelands, Dragon Soul, Bastion): **those raids will load with no boss mechanics**. The tool makes them *enterable and killable* (template stats scaled only by the `mod-zone-difficulty`-style tables, **UNVERIFIED**), not faithful |
| Flight in the old world | per-area flags (`AREA_FLAGS_DROPPED` removes 0x400 etc.) and core | the Wrath++ realm's config (not the tool); flagged |
| Phased quest chains with Cataclysm's `CriteriaTree`/scenarios | not in 3.3.5a | quest objectives with unsupported criteria are listed |
| Cataclysm's new races and classes starts | done by the races session | skipped (`playercreateinfo` is excluded from the plan) |

Honest bottom line: the tool can **bring in every map's geography, buildings, NPCs and spawns, vendors, quests with their text, objectives, rewards and
most scripts expressed in SmartAI**, and the data behind the zone lists, as the seven maps do. It cannot make the 4.x raid fights, Cataclysm's talents,
reforging, guild perks or level 85 exist: that is core C++ work, outside the data converter, listed in the report as `not_in_core` with counts.

## 5. Policies decided here (written so nobody has to decide again)

### 5.1 Replace or add (revamped Azeroth and Kalimdor)
Cataclysm's `Azeroth` (map 0) and `Kalimdor` (map 1) are the same ids and directories as 3.3.5a's. Putting their tiles over the old files **changes the whole old world** for every
character, bot and module of the realm. Decision: **add** (default, the only mode built): the Cataclysm continents get **new directories and new map ids** (`AzerothCata`, `KalimdorCata`, ids
`5000 + original` for any id 3.3.5a's `Map.dbc` has: `ids.map_id`), reachable by portal/teleport (`.tele` rows `game_tele`, generated), with their own spawns. `replace` is a manifest flag
(`mode: replace`), implemented as the same pack with the original names; it is documented, not built, because it needs the old world's AzerothCore spawns removed per area (UNVERIFIED how much of
`creature` would have to go).
Files: a path that 3.3.5a has is **never replaced** (the zones' rule). Where a Cataclysm file of the same path differs (revamped Stormwind buildings), the report lists `collision:<path>` (decided with
`wrath_has` + hash) and v1 keeps 3.3.5a's file; v2 would use the Converter's `--path-prefix` to give such files and the ADTs' references a `cata\` prefix (the Converter supports the prefix: README flag table).

### 5.2 Determinism
Same pins (`pins.json`: build, converter sha, TDB asset sha, WoWDBDefs sha, listfile sha, core sha) and same inputs give the same pack bytes: sorted traversals, `tar --sort=name --mtime=<pin date> --owner=0 --group=0`, `xz -T1`-independent, no timestamps in
files, ids from pure functions. A test (`test_determinism`) runs a stage twice on the fixture and compares bytes.

## 6. Pipeline architecture

```
inventory -> plan -> [fetch -> convert -> tables -> extract -> world] per map/shard -> validate -> pack -> assemble(index) -> publish
```

One command per stage (`python3 -m catabackport <stage> ...` from `realm/warcraft/tools`), all reading `manifest.json` and writing under `--work DIR`:

| Stage | Input | Output | Notes |
|---|---|---|---|
| `inventory` | source (wago, or `--source-dir` fixture), pins | `manifest.json` (one entry per map), `inventory-report.txt` | maps, directories, tiles, ids, swap bases, groups, weights, shard hint; the listfile is read here; works offline from the fixture |
| `plan` | manifest | `plan.json` + `matrix.json` | `--shard i/n`, `--maps all|1,2|group:dungeon`, `--budget-gb`; packs a group of maps (or a continent's row range) into shards by weight so that no shard passes the budget (default 6 GB unpacked, 3 h) |
| `fetch` | manifest, source | `cache/files/<fdid>`, `maps/<dir>/state.json` | the closure (`files.adt_refs`, `model_refs`), `ThreadPool(8)`, retries, `.part` then `os.replace`, per-file `size` and `sha256` recorded; `--resume` skips complete files; a missing id is recorded as `not_in_build` (the build lacks it) not as failure |
| `convert` | fetched files | `maps/<dir>/conv/` | `wotlkconv convert` per folder with the zones' options (`--max-texture-size`, `--listfile`, `-j`, `--report`), then the zones' post steps (`single_textures`, `fix_models`, `plain_textures`, aliases) imported read-only; swaps made whole |
| `tables` | CSVs, DBDs | `maps/<dir>/tables/*.txt` | generic 3.3.5a rows (section 3) |
| `extract` | converted maps, AzerothCore tools | `maps/<dir>/server/{maps,vmaps,mmaps}` | `server_data` of the zones' package, for one map (needs the tools built from the pinned core: Actions only, or a prebuilt tools release) |
| `world` | CPP DB, AC DB (MariaDB) | `maps/<dir>/world.sql`, `world_off.sql`, `world-report.json` | table plan; `core` pack (shared templates) is its own unit |
| `validate` | everything | `validate.json` | structural checks (ADT v18 + MCIN, WDT tile set, M2 version 264 + skins, WMO v17 groups, BLP, DBC header/size, SQL syntax by a parser pass), every referenced file exists, ids in range, no id clashes with 3.3.5a's tables; a map is `ok`, `partial` (some files replaced by placeholders/dropped) or `failed` |
| `pack` | validated map | `cata-<dir>.tar.xz`, `cata-<dir>.json` | the layout of `cata-zones` (`TAG`, `client/files/..`, `client/files.txt`, `client/same.txt`, `client/minimap.txt`, `server/maps|vmaps|mmaps|cameras`, `server/same.txt`) + `server/world.sql` + `pack.json`; the app's `zones_data_realm` already knows that layout |
| `assemble` | all packs' json | `index.json`, `summary.txt`, `report.json` | the release's index: pack, size, sha256, maps, `status`, what it needs (`requires: ["core"]`), dependencies between packs (a swap map requires its base) |
| `publish` | assembled dir | the release `cata-backport` | uploaded with `gh release upload --clobber`, per-asset; the previous good asset is never deleted until its replacement is complete |

### 6.1 GitHub Actions limits and the shard plan
Limits (GitHub's): 6 h per job, 256 jobs per matrix, 10 GB cache per repository (LRU), 2 GB per release asset; a standard `ubuntu-24.04` runner has about 14 GB of free disk (**from memory, UNVERIFIED**; the workflow prints `df` first), so a shard has to fit: that is what `--budget-gb` is for.
- A shard = a list of maps (whole small maps; large maps are split into row ranges of tiles: `azerothcata_r0..r3`). Weights in `plan` come from tile counts (from the WDT), so a shard has about equal work.
- The workflow's matrix is `fromJSON(plan.matrix)`; each job does `fetch..pack` for its maps and uploads **one artifact per pack**; `assemble` downloads them all.
- **Cache**: only what is expensive and shared: the *tables* and the *listfile* and `wotlkconv` checkout (`actions/cache`, key from `pins.json`); files by fdid are cached per shard keyed by the shard's id list hash (a rerun of a failed shard reuses them). The 10 GB cache is **not** a store for packs.
- **Resume**: three layers. (1) inside a job, `--resume` skips every file and every stage whose `state.json` says done and whose output hash matches. (2) a shard that failed is re-run alone: `workflow_dispatch` input `shards` ("3,7"). (3) packs of earlier runs live in the release: input `skip_done: true` makes `plan` drop maps whose pack in the release has the same `input_hash` (the pins + map manifest entry), so running the workflow again only does what changed or failed. Safe to run again (idempotent: release assets are replaced only after the new one verifies).
- **Source outage**: `fetch` takes a `--source` list in order (`wago`, then a mirror/URL template from the repo variable `CATA_MIRROR`, then `dir:` a local cache). A map whose files cannot be fetched after the retry budget (6 tries, back-off 1, 2, 4... capped at 60 s, plus jitter; **a whole stage budget of 90 minutes**) is `deferred`: its job ends **green** with a `deferred` line in the summary and the next run with `skip_done` picks it up. wago's own 500 (observed: item 1) therefore costs a rerun, not a failed pipeline.
- The workflow never runs on a push (`workflow_dispatch` and a `schedule` only if the repo variable `CATA_NIGHTLY` is set; it is **not**).
- A first run is cheap by construction: input `maps` defaults to `proof` (one small dungeon), `stages` to `inventory,fetch,convert,tables,validate,pack`, so the first run needs no MariaDB and no AzerothCore build; it reports whether wago answers, the Converter pin works, and the sizes. `extract` and `world` are separate switches.

### 6.2 The audit
Every run writes `report.json` (machine) and `summary.txt` (plain text): per map status, the counts (files fetched/converted/lossy/skipped/failed by Converter code), tables rows written and unmatched columns, spawns/quests/spells moved and dropped by reason code,
ids allocated, time per stage, the pins, the source used, `deferred` and `failed` with the exact reason, and the list of flags of section 4.3 as counts. Failures never abort other maps. The exit code is non-zero only if **no** map succeeded or the tool itself raised.

### 6.3 Release layout
`cata-backport` release assets: `index.json`, `summary.txt`, `report.json`, `cata-core.tar.xz` (templates, items, spells, display tables shared between maps), and per zone `cata-<dir>.tar.xz` + `.json` (each under 2 GB; a continent is several: `cata-azerothcata-r0.tar.xz`...). The app reads `index.json`, downloads the packs the user turns on (with `core`), checks SHA-256, and puts each in `files/zones-<dir>/` or merges into the zones layout; **the app change is not part of this tool** (`WrathppZones.kt` takes one package; a `WrathppBackport.kt` that reads the index is a separate, small piece of work: the index carries everything it needs: `requires`, sizes, sha, `unpacked`).

## 7. Phone

- Needs: Python 3.10+ (not in the app), the Converter (pure Python, OK), AzerothCore's extractors (native C++, built for arm64 musl by `scripts/build-azerothcore.sh` for the server, so tools exist for the phone only if built and shipped), MariaDB for `world` (the realm has one), the source (wago.tools over mobile data: tens of thousands of files), RAM and disk (a map's work folder is 2 to 7 GB).
- **Simplest honest answer**: **Actions does all the converting** and publishes per-zone packs; the app downloads the packs the user turns on (like `cata-zones` today). That is what this design ships.
- A true on-device run is possible in principle for **one small map** (Termux + Python + the Converter; client files only: `fetch`, `convert`, `tables`, `pack`) and **not reasonable** for `extract` and `world` (native tools, MariaDB, 14 GB work). The tool is pure Python and takes `--work`, so a Termux run works unchanged, but it is not offered in the app: shipping Python and 3 GB of work on the phone costs more than downloading the pack.

## 8. Testing and what the proof can show
- Unit tests use tiny synthetic fixtures (a made WDT, one ADT with an MTEX chunk, an M2 stub, a CSV `Map` with 3 maps), no game files: manifest, plan/shard split, closure, retry/back-off against a local HTTP server that fails N times, resume, determinism, id allocation, table row mapping, SQL plan generation, pack layout, index, summary.
- A dry run (`--source-dir tests/fixture`) runs `inventory -> pack` with no network.
- Real proof on this machine is limited by (1) wago.tools being down at the time (item 1), (2) no AzerothCore extractors built here and 6.7 GB of disk, (3) no MariaDB here. See the report for what ran.

## 9. What is built, what is not
Filled in by the commits (see the final section of this file, kept current).
