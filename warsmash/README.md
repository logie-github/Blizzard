# Embedded Warsmash

Blizzard embeds sandstranger's Android Warsmash 1.0.4 (F-Droid version code 5), not a second installed app. `scripts/prepare-warsmash.sh` fetches the published source archive and verifies SHA-256 `95845f526c08a106d16a3cb9d083dbb8758fe052130dc9f160201d30c0c461ac`. Sources, the upstream license and bundled Android backends go into ignored `app/warsmash/`. No Warcraft game files are committed or bundled.

Source: https://f-droid.org/repo/net.warsmash.phone_5_src.tar.gz
Upstream: https://github.com/Retera/WarsmashModEngine
Android port: sandstranger, https://f-droid.org/en/packages/net.warsmash.phone/
License: GNU Affero General Public License v3.0; preserve upstream and dependency notices. The full upstream archive remains available from the source URL; the build script records the local adaptation (explicit archive ordering instead of the directory scan).

The library modules compile the core, parsers, shared code, AWT compatibility code and native pathfinding. The host supplies the game folder and an explicitly ordered data-source configuration. The game runs in `:warsmash`, separate from the launcher and Winlator. Leaving it disposes the screen and ends only that engine process, so another launch starts fresh.

Initial support targets classic MPQ installations (1.22–1.29), with both war3.mpq and war3x.mpq. CASC-only/Reforged installations are rejected by the Warsmash importer; the two existing Windows modes continue to accept their existing formats. Android OpenGL ES 3.2 is required by this port's shaders. A keyboard/mouse or gamepad is supported by the upstream engine; the host adds touch buttons for right-click orders, Escape and exit. Device gameplay remains unverified until tested with actual game files.
