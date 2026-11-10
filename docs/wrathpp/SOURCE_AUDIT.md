# Wrath++ source audit (2026-11-10)

What was read before any change, and what it showed. Every SHA below was resolved with
`git ls-remote` / `git log` on the day; nothing here is assumed from the mission file.

## This repository

| Item | Value |
|---|---|
| Branch | `claude/new-session-4nmarl`, from `main` at `17cd42e` |
| Working tree at start | clean |
| CI | `build-apk.yml` builds and releases every push to `main` (`blizzard-build-N`); `build-realm-modules.yml` runs only on `workflow_dispatch` (and once, doing nothing, when the file itself changes) |
| Realm control | `realm/warcraft/server/ctl.sh` (POSIX sh, runs on Android's `/system/bin/sh` and busybox) |
| Realms in `acore_auth.realmlist` | 1 ChromieCraft (8085), 2 Wrath Remix (8086) |
| App realm ids (`WowLayout.kt` `Realm`) | 1 CHROMIE 8085, 2 REMIX 8086, 3 OCTO 8090 (own DB on 3311), 4 LEGION 8095 (own DB on 3312) |
| Wrath++ identity chosen | id **5** (3 and 4 are the app's OctoWoW and Legion ids, even though those live in other databases), port **8087** (unused anywhere in the repo) |

### Server pins (`realm/warcraft/server-version.env`, unchanged)

| Component | Commit |
|---|---|
| chromiecraft/azerothcore-wotlk | `4ce7da02a361af539f2ef33f43add70844672d77` |
| mod-playerbots core fork | `2a2211cd8f3d157da432ec0175ddd4b8a191931f` |
| Merged + this repo's 13 core patches | `5361f196da` (as `scripts/fetch-azerothcore.sh` produced it on 2026-11-10) |
| Wrath++ core patch on top | `9213e3f8ff` (local; the patch file is `realm/warcraft/wrathpp/patches/azerothcore/0001-*.patch`) |
| Server data | wowgaming/client-data v20.0, SHA-256 `a3d4df63…a4610` (`server-data.env`) |

### Shared-write hazards found in `ctl.sh` (before this change)

| Function | Shared write | Wrath++ handling |
|---|---|---|
| `world` | `WOW_CLIENT_DIR="$FILES/client"`: modules write `patch-U/V/Y/Z.MPQ` into the shared game | Wrath++ gets `$FILES/client-wrathpp` |
| `module_client` | writes `$FILES/client/Data/patch-M.MPQ` | writes `client-wrathpp/Data` only, after `wrathpp_guard` (no link, not the shared Data) |
| `module_data` | rebuilds `$FILES/data-modules`, sets `DataDir` | `data-modules-wrathpp` |
| `zones_data` | hard links into the shared `$FILES/data` | main only (it ran for "not remix" before; now only for main) |
| `modules` → `rebuild_world` | `DROP DATABASE` of the realm's world DB | `realm_database` refuses any name that isn't the realm's own, and for Wrath++ any name not ending `_wrathpp` |
| `realmlist` | rewrites rows 1 and 2 | untouched; Wrath++'s row only through `wrathpp-register` (backup first, refuses a taken id/port) |
| `configure` | writes `etc`, `etc-remix` | `etc-wrathpp` only once `server-wrathpp` is installed |
| `fetch-azerothcore.sh` | `checkout --force` + `git clean -fdx` of the folder given | `fetch-wrathpp.sh` refuses any folder without `wrathpp` in its path and the other realms' `build/azerothcore` |
| Blizzard app | `WowCtl.transform` rewrites the literal text `"$SERVER/bin/<name>"` and the `MySQLExecutable` line to start programs through musl's loader | every program line kept literal; Wrath++ re-points `SERVER` inside `realm()` instead (a first draft used `$R_SERVER/bin/...`, which would have broken main's start on the phone; caught by reading `WowCtl.kt`, now asserted by the isolation test) |

`warcraft/modules/*` is copied into **every** realm build by `fetch-azerothcore.sh`, so the Wrath++
module lives in `realm/warcraft/wrathpp/modules/`, outside that glob.

## WarcraftXL (client side)

| Repository | Commit (2026-11-10) | License | Notes |
|---|---|---|---|
| WarcraftXL-Labs/client `main` | `fdb9ad1819e68085d4cde4e33b2a17f772fcf85d` (2026-10-30) | **none** (NOTICE.md: decompilation of Blizzard's 3.3.5a `Wow.exe`; no grant possible) | x64 Windows target, MSVC; Win32 compiles but doesn't link at this fork point; README says ABI 0.1.46 |
| WarcraftXL-Labs/core `gitea-sync` | `f7d6cdaf4393e3b89b7ccb889b295aa871d45ca9` (2026-10-28) | MIT | has `include/wxl/seams/*.def`, `tools/seams`: what the client's CMake requires |
| WarcraftXL-Labs/sdk `gitea-sync` | `2920b6e3143169a4244dde6e9d832cd7721f2489` (2026-10-28) | MIT | ABI **0.1.46** (matches the client) |
| WarcraftXL-Labs/core, sdk `main` | `e393e1be…`, `772ba938…` (2026-10-25) | MIT | ABI 0.1.21: **older than the client expects** |
| WarcraftXL/core (default `v1.1`) | `f39aa1c9…` | GPL-3.0 | the older injected framework: no `seams/`, no `tools/`; **not** buildable with the Labs client |
| WarcraftXL/sdk `main` | `d8fde3d2…` | — | only LICENSE and .gitignore at HEAD |
| WarcraftXL/wxl-modern-m2 | `dc0b7dfa…` | — | not evaluated beyond cloning |
| WarcraftXL-Extensions/wxl-modern-assets | `eb7c7c66…` | — | not evaluated beyond cloning |
| WarcraftXL/wxl-db2 | `30e4f2c8…` | — | publishes `wxl.appearance` recipes for **modern** (retail) tables; not Legion 7.3.5 data |

The client README's links point at `WarcraftXL/core` and `WarcraftXL/sdk`, which are the older,
incompatible repositories; the matching pair is the **Labs** organisation's `gitea-sync` branches.
These pins are in `realm/warcraft/wrathpp/wrathpp.env`. Nothing of the client is vendored here.

### Where the client source can carry an extended appearance

| Concern | Location at `fdb9ad18` | Finding |
|---|---|---|
| Five stock fields | `WoW/Source/Glue/Types.h` `CHAR_CUSTOMIZATION_TYPE` (0-4); `CharacterPreferences` (0x20 bytes) inside `ComponentData` | fixed; not extended (the extension stays beside them) |
| Creation state | `WoW/Source/Glue/CharacterCreation.{h,cpp}`, `CharacterCreation_Scripts.cpp` (glue Lua) | `CycleCharCustomization`, `m_prev*Index` per field |
| Geosets | `WoW/Common/ComponentCore/CharacterComponent.cpp` `CCharacterComponent::GeosRenderPrep` (line ~3430) | hides 0-2999, shows the five fields' geosets, then **forces `group*100+1` visible for groups 20-29** (WarcraftXL's change for HD bodies). Any per-character choice in groups 20-29 must be applied **after** this, inside the same function |
| Same compositor everywhere | `CCharacterComponent` is used by creation (`CCharacterCreation::m_character`), selection (`CharacterSelectionDisplay`), units (`Unit_C`), corpses, dress-up | one insertion point covers all |
| Network | `WoW/Source/Net/NetClient/NetClient.cpp` `ProcessMessage`, handler table sized `NUM_MSG_TYPES = 0x51F`; seam `NetClient.ProcessMessage` (Gate) routes mod-claimed opcodes ≥ 0x521 |
| Mod services available (SDK 0.1.46) | `wxl.net` (claim/send/handlers, send gate), `wxl.script` (register glue+game functions/events), Glue events (`OnGlueCharacter` with guid), Object events (`OnObjectCreate`, `OnAppearanceChanged` with model pointer), `wxl.m2` (`SetGeosets` only on models the mod created) |
| Missing | a seam in `GeosRenderPrep`, and a way to set geosets on the **client's** character model from a mod | the Gate C blocker (CLIENT_PROBE.md) |

## AzerothCore (server side), at the merged tree

- `WorldSocket::ReadHeaderHandler` rejects `cmd >= NUM_OPCODE_HANDLERS` (0x521) and closes the
  connection: new numbers need a core patch, i.e. a **separate Wrath++ server build**.
- `STATUS_AUTHED` handlers run with or without a player in the world (character screen and world).
- Hooks used: `ServerScript::CanPacketSend` (before `SMSG_CHAR_ENUM`), `PlayerScript::OnPlayerCreate`
  (called after the character row is committed, before `SMSG_CHAR_CREATE` success),
  `OnPlayerDelete`, `OnPlayerLogin`, `AccountScript::OnAccountLogin`, `WorldScript::OnAfterConfigLoad`/`OnStartup`.

## Toolchain here

Linux x86_64, 4 cores, clang 18 / g++ 13, CMake 3.28, LuaJIT 2.1, MariaDB 10.11 (installed for the
live test). **No MSVC, no Windows, no phone**: the client cannot be built or run in this session.
