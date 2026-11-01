# Blizzard

An Android launcher for Blizzard's games, styled after the World of Warcraft app in
`logie-github/YeaBwoi` (`warcraft/android`): the same frost palette, Cinzel and Jost, the game's
window frames and the drifting snow, in Blizzard's blue. Package `com.logie.blizz`, Android 8 or later.

## Use

- The shelf: the ice field and the Blizzard logo over the games' box art, in alphabetical order:
  Diablo, Diablo II, StarCraft, StarCraft II, Warcraft: Orcs & Humans, Warcraft II: Tides of
  Darkness, Warcraft III: Reign of Chaos, Warcraft III: The Frozen Throne.
- Tap a box: the game's page. **Play** opens the app the game is played with. The first time,
  it asks which installed app that is; after that the app's icon sits in the box's corner, and
  tapping the app's name under Play changes it (or sets it to none).
- The Warcraft games open the Warcraft app (`com.logie.warcrafts`) on their own when it's installed.
- Made for the Galaxy Z Fold:
  - **Cover screen:** the shelf two boxes across; a game's page opens over it, Back returns.
  - **Inner screen:** the shelf on the left of the hinge, the chosen game on the right.
  - **Half-open, like a laptop (tabletop):** the box art stands on the top half; Play and the
    row of boxes lie on the bottom half.
  - Folding or unfolding keeps the game you were on.
- A controller or keyboard moves between the boxes; the focused one lifts and lights up.

The launcher opens apps; it holds no game files, accounts or downloads.

## Art

The user's art is in `branding/` (box art in `branding/covers/`, the header, logo, icon and the
footer reference). `python3 tools/make-art.py` (from the repository root) makes the app's
pictures and its adaptive icon from it into `app/src/main/res`; their output is committed.

## Build

JDK 21 and Android SDK 35 (`ANDROID_HOME`, or `sdk.dir` in `local.properties`).

```sh
./gradlew :app:assembleDebug :app:testDebugUnitTest
```

`testDebugUnitTest` also renders the screens to `app/build/reports/previews/` (Robolectric).
Every build is signed with `app/sideload.keystore`, so each release installs over the last.

## Releases

A push to `main` builds, tests and publishes the APK as the release `Blizzard 1.0.N`
(tag `blizzard-build-N`, `.github/workflows/build-apk.yml`).

Not affiliated with Blizzard Entertainment. All trademarks referenced herein are the properties
of their respective owners.
