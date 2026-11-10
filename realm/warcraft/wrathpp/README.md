# Wrath++ (realm `wrathpp`): sources

Experimental third Wrath realm with Legion 7.3.5-style independent customization categories.
Design, state and evidence: `docs/wrathpp/` (start with MILESTONES.md). Nothing here is built into
the other realms' server: `scripts/fetch-azerothcore.sh` copies `warcraft/modules/` and
`warcraft/patches/azerothcore/` only; this folder is used by `scripts/fetch-wrathpp.sh` alone.

| Path | What |
|---|---|
| `wrathpp.env` | realm id/port, protocol version, the pinned client/core/SDK commits |
| `protocol/wrathpp_appearance.h` | the protocol, registry and validation (C++17, header-only); `protocol/tests/run.sh` |
| `registry/registry.json` | the customization registry (engineering seed: unverified against 7.3.5) |
| `tools/registry.py` | registry checks, canonical binary, hash; `tools/test_registry.py` |
| `tools/wrathpp_protocol.py` | the protocol in Python, for the tests |
| `patches/azerothcore/` | the Wrath++ server's core patch (opcodes 0x521-0x527 routed to the module) |
| `modules/mod-wrathpp-customization/` | the server module: validation, `wrathpp_character_customization`, broadcast, refusal on non-Wrath++ databases |
| `client-mod/wrathpp/` | the client's Lua mod (WarcraftXL runtime): protocol, registry, glue API; `client-mod/tests/run.sh` |
| `tests/test-isolation.sh` | `ctl.sh`: main/remix unchanged, Wrath++ writes only its own paths and databases |
| `tests/run-server-test.sh` | the Wrath++ world server live, with `tests/server_protocol_test.py` |

## Tests

```sh
realm/warcraft/wrathpp/protocol/tests/run.sh          # codec + registry (C++ and Python)
realm/warcraft/wrathpp/client-mod/tests/run.sh        # Lua mod (LuaJIT, mock runtime)
realm/warcraft/wrathpp/tests/test-isolation.sh        # ctl.sh isolation (bash, git)
# live server: a built Wrath++ server (realm/scripts/fetch-wrathpp.sh, then CMake), AzerothCore's
# server data (warcraft/server-data.env), MariaDB's programs:
realm/warcraft/wrathpp/tests/run-server-test.sh AC_SOURCE AC_BUILD SERVER_DATA EMPTY_WORK_DIR
```
