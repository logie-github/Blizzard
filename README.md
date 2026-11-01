# Blizzard Launcher

A standalone Android frontend showcase, named **Blizzard Launcher**, with application ID and namespace **com.logie.blizz**. Requires Android 8 or later.

This project is separate from `../YeaBwoi`. It does not depend on that checkout, its release feeds, native libraries, server packages, or build scripts.

The first stage includes:

- A dark blue Discover screen with a selectable featured universe.
- Warcraft, Diablo, StarCraft, and Warcraft strategy showcase entries.
- Category filters and universe detail dialogs.
- A Library of favorites persisted locally across launches.
- The supplied blue app icon, Blizzard wordmark, icy landscape background, and system bar inset handling.

Entries are previews, not claims of supported or installed games. No game launch, installation, account login, downloads, game files or runtime integrations are included. The interface uses a shared dark navy and electric blue palette, bordered translucent panels, and a dark overlay on the supplied icy landscape for readable text. Universe emblems remain typographic.

## Build

Use JDK 21 and Android SDK 35. Set `ANDROID_HOME` or put `sdk.dir=/path/to/android-sdk` in `local.properties`.

```sh
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
```

The APK is written to `app/build/outputs/apk/debug/app-debug.apk`.

## Source repository findings

YeaBwoi is a collection of independent Android game apps, rather than one shared emulator:

| Area | Structure and runtime |
| --- | --- |
| `overlay/`, `patches/`, `games/` | Shared Dolphin modifications and per-game identity/artwork, applied to pinned upstream source by preparation scripts. |
| `azuredreams/`, `parasiteeve/` | Android launchers around libretro PlayStation cores through LibretroDroid. |
| `v3gold/` | Vita3K-based Android app. |
| `warcraft/android/` | Compose launcher coupled to Winlator's Wine/Box64 Windows runtime, game imports, local realm servers, databases and per-realm services. |
| `warcrafts/` | Warcraft I/II through native Stratagus tooling; Warcraft III through Winlator. |

The existing Warcraft `MainActivity` coordinates the launcher, title music, update checks, and multiple game lifecycle handlers. Its Gradle app also compiles Winlator sources and native code and consumes server package configuration. Copying that app would bring these dependencies into a frontend-only milestone. This project starts with an independent Android application and a small local catalog instead.

## Next stage

Decide the concrete games and versions to support, then define their install and launch interfaces independently of the showcase. Integrate runtimes individually after that decision. A future migration of existing saves or realm data needs an explicit plan: this package has its own Android storage.

This is an independent project, unaffiliated with Blizzard Entertainment. Game names belong to their respective owners.


## Theme assets

Colors live in `app/src/main/res/values/colors.xml` and are shared by the app screens, controls, dialogs, and system bars. The supplied app icon and ice background are preserved in `drawable-nodpi`; the supplied SVG wordmark is represented as a native Android vector drawable. The app icon also supplies the adaptive launcher icon. These assets are bundled for offline use.
