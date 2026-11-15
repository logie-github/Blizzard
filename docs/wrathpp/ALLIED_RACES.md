# Wrath++: the allied races

Wanted (the user): every allied race, and a High Elf for the Alliance, complete (racials too), on Wrath++; a start of
the closest 3.3.5 race for those that have none ("draenei to draenei, orc to orc"); the intro's narration from wago.tools;
the intro's camera the start race's own.

Status 2026-11-15: the models (below) are converted and checked; nothing else is built. Nothing is in the game.

## Races, ids and starts

The ten of Shadowlands' 9.2.7 tables (`tools/sl_looks.py`, `ALLIED`) and a High Elf. Wrath++ keeps its own id space:
the other realms' race modules (ChromieCraft's allied races 15 to 18, murlocs 19, 20, the Skyborne 13, 14, the Worgen and
Goblins 9, 12, and the creatures' races they moved to 22 to 31) are off there, but the module that makes these races must
not need them off, so the ids are ones no module uses.

3.3.5's race mask holds ids up to 32 (`1 << (id - 1)`), the game's `ChrRaces` has rows up to 21 (creatures' races), so the
new races take **22 to 31** (ten); the High Elf takes **9** (the Goblins' unused row: its creature rows move as the other modules move theirs).

| Race | Side | Start (the start race's quests, gear, standing, camera) | Model |
|---|---|---|---|
| Void Elf | Alliance | Draenei (Ammen Vale) | Shadowlands, `LEGACY` |
| Lightforged Draenei | Alliance | Draenei | `LEGACY` |
| Kul Tiran | Alliance | Human (Northshire) | converted, renders right |
| Dark Iron Dwarf | Alliance | Dwarf (Coldridge Valley) | converted, renders right |
| Mechagnome | Alliance | Gnome (Coldridge Valley) | converted, **limbs missing**: head and torso only; the legs and arms are the "Modification" and "Upgrade" options' separate models (skinned models), which the converter doesn't add yet |
| High Elf | Alliance | Night Elf (Shadowglen) | to be made (see below) |
| Nightborne | Horde | Blood Elf (Sunstrider Isle) | `LEGACY` |
| Highmountain Tauren | Horde | Tauren (Camp Narache) | converted, renders right |
| Zandalari Troll | Horde | Troll (Valley of Trials) | `LEGACY` |
| Mag'har Orc | Horde | Orc (Valley of Trials) | converted, renders right |
| Vulpera | Horde | Orc (Valley of Trials; a desert race) | converted, renders right (the male's edges slightly torn) |

The two that `mod-allied-races` has with other starts (Nightborne: the Forsaken's, Zandalari: the Tauren's) take the kin's
here, as asked.

## Done

- `tools/sl_looks.py allied`: each race and sex's skins, faces and eye colours, hair styles and colours and a feature slider
  of its facial options, the same as for the ten races (`SHADOWLANDS_OPTIONS.md`), from Shadowlands' tables.
- The six races 3.3.5 never had converted by `tools/sl_looks.py package` (the allied races' converter): Dark Iron,
  Highmountain, Kul Tiran, Mag'har and Vulpera render right in `tools/render_m2.py`; Mechagnome's limbs are missing (table).
- Notes: the Mag'har woman's feature slider is 68 of 255 (earrings and nose rings) after the earrings; Vulpera have one hair
  style and no hair colour (their fur is their skin): their creator has to cope with an empty slider.

## To do

1. **Intro narration from wago.tools.** `mod-allied-races` has the user's own four MP3s. The ten races' intros are not in
   wago's `interface/cinematics` (the BfA and Legion movies there are the stories'). Legion's four have music
   (`sound/music/legion/mus_735_ar_rtc_<race>_flythrough.mp3`, file ids 1864281, 1862321, 1864280, 1862320: Void Elf,
   Nightborne, Lightforged, Highmountain) and a narrator's lines (Void Elf: `sound/creature/alleria_windrunner`). Which files
   make each race's narration is not in any table reachable here (SoundKitName is not served). Needs a decision.
2. **High Elf.** No such race in 9.2.7. Candidates: Blood Elf's model with the high elf skins the Void Elf's tables carry and
   blue eyes, for the Alliance. The Blood Elf man's model does not convert yet (`SKIP` in `sl_looks.py`).
3. **Wiring**, a race at a time (a module of Wrath++'s own, its realm only): `ChrRaces`, `CharBaseInfo`, `CharStartOutfit`,
   display and model rows, the looks' tables (done for the ten), the intro's cinematic and camera (the start race's),
   `playercreateinfo*` and the class and race masks, the world database's own SQL.
4. **Racials** (3.3.5 spells and scripts), each race four to five: an aura-only racial is a spell row; the rest are C++
   (`AlliedRacesSpells.cpp` has the Void Elf's, Nightborne's, Lightforged's and Zandalari's to build on).
5. **The creator**: Wrath++'s two-step creator has its own race buttons; the new races need buttons there and their
   icons (the race icons are in wago as `interface/glues/charactercreate/...`).
