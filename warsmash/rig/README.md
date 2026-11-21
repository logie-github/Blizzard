# Warsmash test rig

Runs the embedded Warsmash engine (the prepared tree in `app/warsmash`, `scripts/prepare-warsmash.sh`) on this machine
without a phone or a GPU: libGDX's headless backend with a stand-in OpenGL, the engine's real simulation and map
scripts, and Warcraft III 1.27's own files. Nothing here ships in the app.

- `shims/`: the six Android classes the engine imports (`Os`, `Log`, `Bitmap`, `GLES20`, `GLUtils`), enough for a desktop build.
- `src/rig/Main.java`: starts the engine's menu screen, starts the map given, and hands every frame of the map to a scenario.
  Data sources are layered as the app's `WarsmashConfig` layers them (the game's MPQs, its folders, the engine's support files).
- `src/rig/Idle.java`: loads the map and lets it run 300 frames (the map loads, its scripts start, the simulation ticks).
- `src/rig/AbilitySmoke.java`: for each line of `$ABLIST` (`code alias target`, target one of `enemy`, `caster` (an enemy
  with mana), `ally`, `air`, `point`, `none`, `passive`), a Blood Mage beside two enemies, an ally and an enemy flyer
  (attacks off), given that ability and made to cast it; prints what changed (life, mana, buffs, gold, lumber), why a
  cast was refused (the engine's own error key) and any exception. `abilities-0008.txt` to `abilities-0012.txt` are the lists for engine patches 0008 to 0012 (0011's: the ability builder's data abilities) (a fourth column names the caster's unit type when the Blood Mage can't cast it, e.g. a Kodo for Devour); `fx=` counts the spell-effect events the cast fired; `p0`, `ill`, `corpses`, `eOwner` and `allyMoved` count the caster's player's living units, illusions and corpses, name the first enemy's owner and how far the ally moved; `type` shows the caster's unit type changing (a form or a morph). A cast whose missing research or upgrade would refuse it has it granted first. A target `corpse` (or `corpseenemy`) kills the two enemy soldiers first and casts on their bodies, `summoned` makes the enemy a summoned unit, `hero` has the hero learn a skill first. A relative `ABLIST` is read from this folder.
- `src/rig/Combat.java`: plain fights (melee, missile, splash, bounce, line, air, magic, a hero) side by side; prints each
  pair's life after 900 frames. `src/rig/CombatDebug.java`: one attacker (`ATK`, default a Paladin) against a grunt,
  frame by frame.
- `src/rig/CombatAbilities.java`: one fight at a time from `$FIGHTLIST` (`attacker defender ability`, `-` for none),
  the ability given to the attacker with autocast on; prints both lives, the attacker's mana spent and every buff the
  defender carried. `fights-0011.txt` is the arrows and orbs, each beside the same attacker without it.
- `src/rig/Setups.java`: abilities that need a scene of their own (a tree, a building to hit, peons to call, an
  upgrade, a neutral critter, a walk before a channel): each case builds it, waits and prints what it measured.
- `Idle` also prints when the cinematic filter (fades) shows and hides, and at its end the quest log, what the Quests dialog shows when opened, and every player's gold and lumber (`DRAIN=1` empties player 3's gold halfway, to see a map's top-up trigger). `Dump` with `MAPS=a.w3m:b.w3x` copies each map's `war3map.j` out. `Setups` has cases for the land mine, creep sleep, the Tavern (hire and Awaken), siege minimum range, and natives called through the map's script scope (alliances, orders, visibility, the damage event, the cinematic filter), and the campaign natives (`0040`: the game cache saved, reloaded and a hero restored from it, XP suspension, script revive, selection; `0041`: the game difficulty and the campaign difficulty menu), and a hidden caster's Dark Conversion with its summon event (`0042`), and the unit events (`0043`: owner change, hero skill, training and construction start, item use and drop). `Idle` also takes `MOVETO=frame:x,y` (puts player `MOVEPLAYER`'s first hero there, default index 1), and `COUNT` shows each type's owners. `Setups` case `0045` covers unit selected, target acquired and loaded. `Idle` also takes `HASH=1` (a state hash every frame, to compare two runs), `DUMPTICK=n` (every unit at tick n) and `RNGLOG=file` (every draw of the seeded random with its caller). `Setups` case `0047` shows what the campaign screen offers for a fresh profile and after wins. `FRAMETIMES=1` (frame time percentiles, worst frames, stage times), `PROFILE=1` (sampling profiler; `SLOW_US` keeps only slow frames) and `rig.PathCheck` (300 fixed path queries, a hash of the paths and their time) measure speed (`0047`). `rig.SaveSpike` (`SAVEAT=frame`) writes the live simulation through the save-graph writer (patch `0046`, groundwork for quicksave, not used by the game yet) and prints object count, size, time and what it had to drop. `Idle` also takes `COUNT=type,type` (living units of those types every 100 frames), `KILL=frame:type` (kills one, by player 2's hero), `DUMPTYPE`/`TRACETYPE` (a type's abilities and behaviour).
- `src/rig/NativeAudit.java` (`NATIVES=` a file of native names): each one the engine registered without code (`RIG: NOCODE`).
- `src/rig/TypeScan.java`: every ability alias listed in `$ALIASES` that the engine has no ability type for.
- `Idle` runs `$FRAMES` frames (300 by default); a failed script thread prints `JASS thread ended on error`.
- `src/rig/Skirmish.java`: a melee game with computer players (`COMPUTERS=1,2,3`, `FRAMES`): every 300 frames each player's units, workers, buildings, resources, food, blight around the hall and units lost; `UNITS=N` adds player N's units with their behaviours and each harvester's load, tree and target every 1500 frames, `BPLAYER=N` whose buildings to list.
- `src/rig/Reach.java`: flood fill on foot from `$FROM` to `$TO` (x,y) at radius `$R`: whether the pathing grid joins them. `src/rig/ProgressCheck.java` (`RIGMAIN=rig.ProgressCheck`): the campaign openings in order. `Setups` runs only the cases whose name contains `$CASE`.
- `src/rig/Dump.java`: copies files out of the game's MPQs (`Units\AbilityData.slk` and the like; `EXTRA` adds more MPQs, a map's own `war3map.j` with the map file there; run with `RIGMAIN=rig.Dump`).

A frame that takes more than 3 s prints the render thread's stack (`RIG: HANG`), so a hang shows where it is.

## Running

The game files: Blizzard's 1.27 download, built as the app builds it (`blizzard-legacy-dl install WAR3 --no-base --game
DIR` then `W3XP`, the tool built for x86_64 from `tools.env`'s commit with `patches/blizzard-legacy-dl`). Then:

```
scripts/prepare-warsmash.sh
cd warsmash/rig
GAME=/path/to/game GV=1 gradle run --args='Maps\FrozenThrone\(2)EchoIsles.w3x rig.Idle'
GAME=/path/to/game GV=1 ABLIST=abilities-0008.txt gradle run --args='Maps\FrozenThrone\(2)EchoIsles.w3x rig.AbilitySmoke'
```

`GV` is the engine's GameVersion (0 Reign of Chaos, 1 The Frozen Throne). The engine's pathfinding library is built
for this machine first (`nativeLib`, g++). Gradle 8.14 and JDK 17 or later. Nothing is drawn: the rig sees the
simulation, not the picture.
