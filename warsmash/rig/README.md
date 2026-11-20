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
  cast was refused (the engine's own error key) and any exception. `abilities-0008.txt`, `abilities-0009.txt` and `abilities-0010.txt` are the lists for engine patches 0008 to 0010 (a fourth column names the caster's unit type when the Blood Mage can't cast it, e.g. a Kodo for Devour); `fx=` counts the spell-effect events the cast fired; `p0`, `ill`, `corpses`, `eOwner` and `allyMoved` count the caster's player's living units, illusions and corpses, name the first enemy's owner and how far the ally moved. A target `corpse` (or `corpseenemy`) kills the two enemy soldiers first and casts on their bodies, `summoned` makes the enemy a summoned unit, `hero` has the hero learn a skill first. A relative `ABLIST` is read from this folder.
- `src/rig/Dump.java`: copies files out of the game's MPQs (`Units\AbilityData.slk` and the like).

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
