# Wrath++: the allied races

Wanted (the user): every allied race, and a High Elf for the Alliance, complete (racials too), on Wrath++; a start of
the closest 3.3.5 race for those that have none ("draenei to draenei, orc to orc"); the intro's narration from wago.tools;
the intro's camera the start race's own.

Status 2026-11-15: built and tested here as far as the files go (tables, SQL, packaging, the app's installer, the creator's
glue on a mock); **nothing has run in the game or on a phone**. Two models are not right (below): the Mechagnome's limbs are
missing, and the converted Blood Elf man was left out.

## Races, ids and starts

The ten of Shadowlands' 9.2.7 tables (`tools/sl_looks.py`, `ALLIED`) and a High Elf. Wrath++ keeps its own id space:
the other realms' race modules (ChromieCraft's allied races 15 to 18, murlocs 19, 20, the Skyborne 13, 14, the Worgen and
Goblins 9, 12, and the creatures' races they moved to 22 to 31) are off there, but the module that makes these races must
not need them off, so the ids are ones no module uses.

3.3.5's race mask holds ids up to 32 (`1 << (id - 1)`), the game's `ChrRaces` has rows up to 21 (creatures' races), so the
new races take **22 to 31** (ten). The Worgen and Goblins (Cataclysm's starting areas, `CATA_RACES.md`) keep the ids their module has, 12 and 9, so the High Elf takes **21**: the Ice Trolls' row, a creatures' race, folded into the Forest Trolls' 18 (the Northrend Skeletons' 20 folds into the Skeletons' 15 and is the Goblin creatures' new race; the Fel Orc creatures' race moves from 12 to 32). `FOLDED` and `MOVED` in `tools/races_profile.py`.

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

## How it is made

1. `tools/sl_looks.py data` reads Shadowlands' tables for the ten races and writes the races data (the format of the allied
   races module's `data/retail/races.json`: each race's models, skins, faces and eye colours, hair, a feature slider of its facial
   options, voices and names). The High Elf is the Void Elf's models with only the skins and faces of the high elf kind (today's
   Void Elf tables carry both), renumbered from 0 (`names.py`'s `file_index`), its voices and names the Blood Elves'.
2. `tools/sl_looks.py package` converts the models (the allied races' converter), textures, voices, the intros' narrations
   (the user's four MP3s where the allied races module has them; wago.tools' Highmountain flythrough music for the Highmountain;
   the other races' intro is the start race's flight without a voice) and the race icons (wago.tools') into the game's paths.
3. The allied races module's own generator, `tools/build_data.py`, run with Wrath++'s profile (`tools/races_profile.py`,
   `BUILD_PROFILE=...`), writes the table changes (`CharBaseInfo`, `CharSections`, `ChrRaces`, `Spell`... as change files) and the
   world SQL (`wrathpp_races_world.sql`, committed under `modules/mod-wrathpp-customization/data/sql/db-world`: starts, skills,
   actions, stats, quests, standing, racials learned at creation). Unset, the generator makes ChromieCraft's allied races as before
   (checked: its output is byte for byte the committed one).
4. `tools/sl_looks.py assemble` merges the change files (the ten races' rows too) and applies them to the server's tables
   (`tools/apply_client.py`); the package carries the change files, not tables.
5. The app (`WrathppLooks`, `DbcChanges`) applies the change files to the tables **the client itself reads** (the HD look's patches
   change them) and writes them into `Data/patch-Z.MPQ/DBFilesClient`; `WrathppAlliedRaces.xml/.lua` (written into the interface
   patch at every Play) give the creation screen the buttons, pictures, columns, scenes and texts.

## What each race has

Ids 22 to 31 (Void Elf, Nightborne, Lightforged Draenei, Zandalari Troll, Highmountain Tauren, Kul Tiran, Dark Iron Dwarf, Vulpera,
Mag'har Orc, Mechagnome) and 12 for the High Elf (the Fel Orcs' creature race moves to 32). Starts are the table above: the start
race's place, quests, standing, gear, action bars, skills, stats (its kin's; Vulpera: the Gnomes') and intro camera.

Classes (3.3.5's; retail's Monk, Demon Hunter and Evoker don't exist): Void Elf, Nightborne: Warrior, Hunter, Rogue, Priest, Death
Knight, Mage, Warlock. Lightforged: Warrior, Paladin, Hunter, Priest, Death Knight, Mage. Zandalari: all but Warlock. Highmountain:
Warrior, Hunter, Death Knight, Shaman, Druid. Kul Tiran: Warrior, Hunter, Rogue, Priest, Death Knight, Mage, Shaman, Druid. Dark Iron:
Warrior, Paladin, Hunter, Rogue, Priest, Death Knight, Mage, Warlock, Shaman. Vulpera, Mag'har: Warrior, Hunter, Rogue, Priest, Death
Knight, Mage, Warlock, Shaman. Mechagnome: Warrior, Hunter, Rogue, Priest, Death Knight, Mage, Warlock. High Elf: Warrior, Paladin,
Hunter, Rogue, Priest, Death Knight, Mage, Warlock. A class the start race hasn't takes the gear, bars and skills of the first race
of the side that has it (`races_profile.py`, `TEMPLATE`).

Racials (3.3.5 has no Monk, and its auras are fewer than retail's: the retail ones as near as they come):

| Race | Racials |
|---|---|
| Void Elf, Nightborne, Lightforged, Zandalari | the allied races module's own (spells and C++ scripts, built into the Wrath++ server): Spatial Rift, Entropic Embrace, Chill of Night, Preternatural Calm, Cantrips; Arcane Pulse, Arcane Resistance, Magical Affinity, Ancient History; Light's Judgment, Forge of Light, Light's Reckoning, Holy Resistance, Demonbane; Regeneratin', Embrace of Pa'ku, Pterrordax Swoop, City of Gold |
| Mag'har Orc | Ancestral Call (+10% damage 12 sec), Brawn (+2% crit damage and healing), the Orcs' Hardiness and Command |
| Dark Iron Dwarf | Fireblood (Stoneform's effects), Forged in Flames (-10% Fire damage) |
| Kul Tiran | Brush It Off (-2% damage), Haymaker (a War Stomp), the Humans' Diplomacy, the Undead's Underwater Breathing (Child of the Sea) |
| Highmountain Tauren | Mountaineer (+3% Stamina), Bull Rush (+30% speed 3 sec), the Tauren's Endurance |
| Vulpera | Bag of Tricks (Physical damage around you), Nose for Trouble (stealth detection), Rummaging (Skinning +10), the Gnomes' Escape Artist |
| Mechagnome | Combat Analysis (+2% crit), Skillful Scavenger (Engineering +15), Escape Artist, Engineering Specialization |
| High Elf | the Blood Elves': Arcane Torrent by class, Magic Resistance, Arcane Affinity |

Left out (3.3.5 can't or it was too much blind): Mole Machine, Hyper Organic Light Originator, Emergency Failsafe, Make Camp, Pass
the Torch; the intros' voices other than the five; the Mechagnome's mechanical limbs.

## Open

- **The Mechagnome**: head and torso only (the limbs are the "Modification" and "Upgrade" options' separate models).
- **The Blood Elf man** (one of the ten races' models) still keeps the game's own look.
- **Not run anywhere but on these files**: the race ids 22 to 31 and 12 on the client and the core (the core sizes its race table
  from the game's own rows, as `mod-allied-races`' 15 to 18 rely on); the creator's new buttons (a mock only); whether an HD
  look's model names are the stock ones (the package's models take the stock paths: where the HD patch names its models
  differently, the Shadowlands ones are not drawn).
- **The server** has to be built again and downloaded to have the SQL (`modules/mod-wrathpp-customization/data/sql`): the
  `build-wrathpp-server.yml` build starts when that is pushed to `main` (an hour, 424 MB for the phone).
- **Wrath++'s creator buttons** are by their file string: `HighElf` is the High Elf's (its models' folder is the Void Elf's).
