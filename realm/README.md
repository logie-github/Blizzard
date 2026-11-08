# The realm's sources

What `.github/workflows/build-realm-modules.yml` builds the Wrath realm from when the app asks for a realm with modules
(World of Warcraft, Wrath+ page, **Modules**). The layout is the scripts' own (they find `warcraft/...` beside `scripts/`):

- `scripts/`: `fetch-azerothcore.sh` (the core at ChromieCraft's revision, the playerbots core merged, `warcraft/patches/`, the
  modules, and each picked module fitted in: a module whose loader isn't named for its folder gets a small file that calls it),
  `compile-azerothcore.sh`, `package-azerothcore.sh`, `module-files.py`, `test-warcraft-server.sh`.
- `warcraft/server-version.env`: the pins (core, playerbots core, the realm's own modules). `server-data.env`: the server data the test uses.
- `warcraft/patches/`: the changes to the core (`azerothcore/`, including the `OnPlayerGetRestBonusMax` hook) and to modules.
- `warcraft/modules/`: the realm's own modules (races, Brill, Wrath Remix, ...), built in.
- `warcraft/server/`: the realm's `ctl.sh` and the test's scripts.

Copied from the World of Warcraft app's repository at its commit `0107568`, at the user's request ("move it all into Blizzard");
from here they are changed in this repository only. The built package goes on the release `realm-modules` (not an app release).
Never commit build outputs or game files here.
