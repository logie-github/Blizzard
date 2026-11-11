# Embedded Warsmash

Blizzard embeds sandstranger's Android Warsmash 1.0.4 (F-Droid version code 5), not a second installed app. `scripts/prepare-warsmash.sh` fetches the published source archive and verifies SHA-256 `95845f526c08a106d16a3cb9d083dbb8758fe052130dc9f160201d30c0c461ac`. Sources, the upstream license and bundled Android backends go into ignored `app/warsmash/`. No Warcraft game files are committed or bundled.

Source: https://f-droid.org/repo/net.warsmash.phone_5_src.tar.gz
Upstream: https://github.com/Retera/WarsmashModEngine
Android port: sandstranger, https://f-droid.org/en/packages/net.warsmash.phone/
License: GNU Affero General Public License v3.0; preserve upstream and dependency notices. The full upstream archive remains available from the source URL; the build script records the local adaptation (explicit archive ordering instead of the directory scan).

The library modules compile the core, parsers, shared code, AWT compatibility code and native pathfinding. The host supplies the game folder, an explicitly ordered data-source configuration and the game to play: the engine's GameVersion, 0 for Reign of Chaos and 1 for The Frozen Throne (both of Warcraft III's tiles play here). The launcher's changes to the engine are patches in `patches/warsmash/`, applied in order by the build script after the upstream copy (`0001`: a drag that begins on the minimap slides the view by the finger's travel instead of jumping to the touched point); the prepared tree is made again whenever the source or a patch changes. The game runs in `:warsmash`, separate from the launcher and Winlator. Leaving it disposes the screen and ends only that engine process, so another launch starts fresh.

It plays classic MPQ installations (1.22–1.29): war3.mpq, and war3x.mpq for The Frozen Throne. CASC (1.30 and later) and Reforged installations are refused by the importer (`Warcraft3WarsmashImporter`), whose Retry brings Blizzard's 1.27 instead. Android OpenGL ES 3.2 is required by this port's shaders. A keyboard/mouse or gamepad is supported by the upstream engine; the host adds nothing over the game (Back is Escape; the game's menu quits). Device gameplay remains unverified until tested with actual game files.
