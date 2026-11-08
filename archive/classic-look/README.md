# The classic look (archived)

The Northrend look the launcher had before the modern one: a shelf of boxes under the Blizzard logo and the snow, a page per game, the
open Fold's wide shelf with a page beside it, the half-open Fold's tabletop page, and the tile screen (rearrangeable tiles, tall or
wide, how many across). Cinzel type and gold-cornered frames.

It is out of the app: no setting, no gesture and no code path reaches it. Nothing here is compiled.

- `ui/ClassicShelf.kt`: the shelf, the pages and the wide and tabletop layouts, cut out of `Launcher.kt` (`WideLauncher`, `Shelf`,
  `Header`, `CoverGrid`, `Cover`, `GamePage`, `BigCover`, `Details`, `TabletopPage`, `PlayButton`, `ImportStatus`, `LogoMenu`).
- `ui/ClassicTiles.kt`: the tile screen (`TileScreen`, `Tile`, `TileArtDialog`, the pinch to change columns).
- `ui/TileLayout.kt`, `ui/TileSettings.kt`: the tile layout's arithmetic and its settings (order, shapes, columns, mode).
- `tests/`: its screenshot and layout tests.

To bring it back: copy those files into `app/src/main/java/com/logie/blizz/ui/` (and the tests under `app/src/test/`), put the
`Look.set`/`Look.load` switch back into `Look.kt` (the classic drawing of the shared pieces, `FrameButton`, `Modifier.panel`,
`Colors`, still sits behind `Look.modern`, which is now a constant `true`), call `Shelf`/`TileScreen`/`WideLauncher` from
`Launcher` again where `ModernHome` is, and add the settings' Look and Layout cards. The pieces `ModernHome` shares with it
(`boxArt`, `COVER_RATIO`, `LocalOpen*`, `ConfirmDialog`) stayed in the app.
