# mod-ralia: Ralia's mod and Alternate Female Options

Two sets of character textures, one at a time, from your own zips: **Ralia's mod** (Ralia's patches,
made for the game of today) and **Alternate Female Options** (another set, its women's textures alone),
in the game while the launcher's **Game options** switch for one is on. Both realms (it's the client's
look). Nothing of either is in this repository or the app: the app reads the zip you pick on the phone.
Below, "Ralia's" means either set's.

## Turning it on and off

**Game options → Ralia's mod** or **Alternate Female Options**. The first time, each asks for its zip;
the app keeps the zip's `Character` folder (`files/ralia/files`, `files/alternate-female/files`) and
nothing else from it. **Choose the zip again** replaces them. Turning one on turns the other off (its
textures are kept). It takes effect at the realm's next start: the world server makes the game's patch as it
starts (a few seconds to a minute the first time; again only when the zip, the client or the realm
changes, or the other set is turned on), and takes it out while neither is on. Existing installs rebuild
the patch after the gnome support update. If your imported zip has no gnome textures, use **Choose the
zip again** with a copy that includes them. Turning one off also takes the patch out of your client at
once; the copy of its textures in the Skyborne's patch (below) goes at the realm's next start.

`Ralia.Enable = 0` in the realm's `modules/mod_ralia.conf` keeps both out whatever the switches say. To take
the module out of the realm altogether, delete this folder: nothing else needs it (the other race
modules only leave its patch out of what they're made from).

## What it changes

The skin and the pelvis and torso textures of the game's character table (`CharSections`, sections 0
and 4) for the races in the game: all eight races of 1.x, including gnomes, the blood elves, the Draenei, the
Worgen and Goblins (`mod-worgen-goblin`), and the allied races (`mod-allied-races`: void elves,
nightborne, Lightforged Draenei, Zandalari Trolls). The Skyborne (`mod-skyborne`) take the blood elves':
their skins, and the blood elves' Dark Ranger skin, are the blood elves' first colour recoloured, made
after this patch from the game with it in (tested: the set's blood elf texture shows through both). The
murlocs and the naga are left as they are (and with Alternate Female Options, the gnomes), as are the
races Ralia's patches have that the
game doesn't (Pandaren, Kul Tirans, Dark Iron dwarves, Highmountain Tauren, the orcs' clan skins).

- **Each texture takes Ralia's file of the same name**: the game's names without their underscores or
  their case are today's, with `_hd` after the newer models' (`HumanFemaleSkin00_03.blp` takes
  `humanfemaleskin00_03_hd.blp`). The allied races' colours are numbered as this game's tables have them,
  not as today's files are: `data/client/sources.txt` (made by `tools/build_data.py` from
  `mod-allied-races/data/retail/races.json` and today's file names, `data/retail_paths.json`) names the
  file each takes. The Worgen's pelvis and torso textures (named `_regular` and `_dk`) take Ralia's of
  their kind.
- **Alternate Female Options takes the women's textures alone** (`\Female\` in their path).
- **The tauren's fur** (a skin's second texture, `_Extra`): a set's file of the same name, when it has
  one; a colour without one keeps the game's.
- **The older models' file or the newer's**: where a set has a texture both as the older models' and as
  the newer's (`_hd`), the one nearer the game's own picture is used (the game draws the older models,
  or an HD look's newer ones).
- **Only part of a skin**: classic's layout's TorsoUpper, TorsoLower and LegUpper sections (the right
  half's top five eighths) come from the set, its colours
  scaled to the game's skin there; the rest of the skin stays the game's own, so what an HD look's models
  draw from other parts of it (the Draenei's horns, faces, hands) stays as it was. A colour with no file
  takes its nearest colour's change where that file is the game's picture changed, else that file's body
  part in its own skin colour (an HD look's skins are other pictures than today's).
- **The game's size and format**: a skin of today is twice as wide as it is high, the body (classic's
  layout) in its left half, which is what's used; each texture is made the size the game's is, and
  palettized (256 colours), as 3.3.5 composes characters from. A skin keeps the game's own alpha.
- **A colour Ralia's patches don't have** (the allied races' newer skin colours, the creatures' skins of
  the playable races) takes the change Ralia's file makes to the nearest colour that has one: where that
  colour's file differs from the game's, this colour's picture is changed as much, so its own colour
  stays. The allied races' tattooed skins take their plain colour's change the same way, so their tattoos
  stay. A colour whose nearest file is another picture altogether (more than a twentieth of it changed)
  is left as it is.

## The patch

`Data/<locale>/patch-<locale>-Z.MPQ` (with `patch-<locale>-Z.MPQ.ralia`, what it was made from, and
`patch-<locale>-Z.MPQ.files`, the paths it has). It was taken to be the last archive the game reads,
but in the game the `Data` folder's patches won over it: with the Alternative HD Patch, only the
Skyborne's skins (made from its blood elf texture, at paths of their own) showed the set, while every
other race kept the HD look's (`patch-A`), the Worgen and Goblins' (`patch-U`) or the allied races'
(`patch-V`) textures. So the Skyborne's `Data/patch-Z.MPQ` (`mod-skyborne`), made after this from the
game with it in, carries every listed texture too, byte for byte: the highest of the `Data` patches,
it puts the set over an HD look's and the race modules' whichever folder the game reads last. It's made from the game as those leave it,
as the world database's own tables are loaded (after `patch-U` and `patch-V`, made as the configuration
is read), and before the Skyborne's `patch-Z` and Wrath Remix's `patch-Y`, which it isn't made from. A
`patch-<locale>-Z.MPQ` that isn't this module's is left alone, and then the mod isn't in the game.

## Files

| File | What it is |
| --- | --- |
| `src/Ralia.cpp` | The world server's part: makes the patch from the set that's on, or takes it out, as the world starts. |
| `src/RaliaPatch.cpp` | Which file each texture takes, and the patch. |
| `src/RaliaImage.cpp` | Resizing, the nearest colour's change, palettized BLP2 textures. |
| `data/client/sources.txt` | The allied races' colours' files (`tools/build_data.py`). |
| `data/retail_paths.json` | Today's file names of the allied races' textures (`tools/build_data.py --fetch`, from wago.tools). |
| `tools/test_patch.cpp` | The patch made from a stand-in game and stand-in files, and the Skyborne's after it (CI's unit tests). |

Tested: the patch's pieces against stand-ins (`tools/test_patch.cpp`), the change carried to another
colour against Ralia's own file for it (a void elf colour: within 6 levels a channel where Ralia's
changes are). Gnome regression checks cover male and female skins, a colour without its own file,
and the pelvis and torso overlays. Not seen in the game: nothing here runs the 3.3.5 client.
