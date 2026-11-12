# The rig: Wrath++'s creator run on the game's own creation screen

The 3.3.5a client is the user's own and is not on the machines this is developed on, so the creator
(`app/src/main/assets/wrathpp/WrathppCreate.lua`) was first tested on a hand-written stand-in for the creation screen.
The stand-in passed three builds that failed on the phone: a crash on Create Character (builds 226 to 232), a script
error at Customize for every death knight (233 to 235), and a game's own screen left broken when the creator turned
itself off. Each came from something the stand-in did not know about the real game. The rig is put together from the
real pieces instead:

| Piece | From | Here |
| --- | --- | --- |
| The creation screen: its frames, their names, parents, places, sizes and scripts | The phone's own `CharacterCreate.xml`, `CharacterCreate.lua`, `GlueButtons.xml`, `GlueParent.xml`, `GlueStrings.lua`, read from the client's archives by the app and sent as issues #57 to #64 (`ClientFilesDump.kt`) | fetched by `tools/fetch_stock.sh` at test time; **never in the repository** |
| What the game does: the random first character, next and previous of each of the five numbers, race, sex and class changes, the counts, Create | The client's decompiled source (WarcraftXL-Labs/client at the commit `wrathpp.env` pins: `CharacterCreation.cpp`, `CharacterCreation_Scripts.cpp`, `CharacterComponent.cpp`, `ComponentUtils.cpp`), ported function by function | `game.lua` |
| The game's tables | `data.zip`'s dbc (races, classes, which race may be which class) and the looks' own `CharSections`/`CharacterFacialHairStyles` (with undead skins put in as the app's import does: `tools/undead_rows.py`) | `tools/build_data.py` |
| The frames | A widget engine that keeps to what the client does | `engine.lua` |
| Wrath++'s native mod | `client-mod/wrathpp-native/src/Native.cpp`, the same functions over `game.lua`'s state | `game.lua` |

What the engine keeps to, each because the stand-in did not:

- **A method the client does not have is not there.** Calling it is the error it is in the game.
- **OnShow runs for a frame's children before the frame itself** (the client's `CSimpleFrame::ShowThis`; the phone's
  crash showed the order: the creator's own frame heard OnShow before the game's OnShow had made the character).
- **The game reads the character being created without looking whether there is one.** In `game.lua` that is a CRASH
  no `pcall` is let to swallow, as it is in the game.
- **Counts come from the tables by the client's own rules**, a death knight's rows needing their flag
  (`ComponentFlagsMatch`), the table's order deciding the sizes (`BuildComponentArray`).
- **A frame is on the screen only if it and every parent are shown**, is where its anchors put it on a screen of the
  phone's shape (1125 x 768), and inside a scroll frame only where the scroll frame shows it. A tap on what is not on
  the screen, is off its edge, scrolled out of sight or disabled is refused.
- **A script's error stops that script and is kept**, as the game stops it and goes on.

## Running it

    sh run.sh WORK app/src/main/assets/wrathpp/WrathppCreate.lua WrathppLooks.lua CLIENT_DBC STOCK_DBC

`CLIENT_DBC`: the looks' `DBFilesClient` folder; `STOCK_DBC`: `ChrRaces`, `ChrClasses`, `CharBaseInfo`,
`FactionTemplate` and `FactionGroup` from `data.zip`. Needs `luajit`, `python3` and `gh` (the phone's files are
fetched from this repository's issues). `wrathpp-looks.yml` runs it with the looks it has just made and does not
publish them if it fails. About two minutes:

- `behaviour.lua`: the screen opened (in the client's order), the two screens, the game's own buttons in the creator's
  panels doing the game's work, Undead, Gear, turning, nearer and back, a list under a finger, Finish, a death knight,
  no native mod.
- `off.lua`: the creator turned off; every piece of the game's own screen is where and as it is without the creator,
  none of the creator's is left, and the game's own buttons work.
- `full.lua`: every race, sex and class as the first character: Customize, every category, every row's arrows, every
  choice of every list (tapped where it is, scrolled to as a finger would), every switch, Randomize, Back, Finish,
  the screen closed and opened; after each tap no error, no crash, the creator on, the row showing what was chosen and
  the other rows as they were. Then again without undead skins, without the native mod, on a 4:3 and a 16:9 screen.
- `shot.lua` and `tools/draw.py`: the screen as a picture of where things are (not the game's art), to look at.

## What it is not

It is not the game. It has no art, no fonts and no 3D, and a frame's place is worked out, not drawn by the client. What
it does not know about the real client it cannot show; when the phone shows something it missed, the rig is taught it
(a rule in `engine.lua` or `game.lua`, from the client's source or the phone's report) before the creator is changed.
