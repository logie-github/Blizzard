# Wrath++ architecture

Wrath++ is a third, experimental Wrath realm beside ChromieCraft (1) and Wrath Remix (2): 3.3.5a
gameplay, with Legion 7.3.5-style character customization carried as **independent categories
beside** the five stock fields, persisted by its own server, drawn by a modified client. It is off
unless its own server is installed, and nothing of it writes into the other realms' files or
databases (ISOLATION_MANIFEST.md).

```
 registry/registry.json ──tools/registry.py──▶ registry.bin (canonical bytes, FNV-1a hash)
        │                                              │
        │                                              ▼
        │                         ┌───────────────────────────────────────────┐
        │                         │ Wrath++ world server (separate build)     │
        │                         │  AzerothCore pins of main + core patch    │
        │                         │  0001 (opcodes 0x521-0x527 → module)      │
        │                         │  mod-wrathpp-customization:               │
        │                         │   validate · persist · resolve · broadcast│
        │                         │  acore_*_wrathpp only (refuses others)    │
        │                         └──────────────▲────────────────────────────┘
        │                    PROTOCOL.md (v1)    │ hello/registry/appearance/result/query
        ▼                                        ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ WarcraftXL-Labs client (x64, from source, pinned) + core/sdk (gitea-sync)│
 │  Lua mod wrathpp.appearance (client-mod/): protocol, registry, glue API  │
 │   WrathPP_* functions, WRATHPP_* events  ── implemented, mock-tested     │
 │  native: Component.GeosRenderPrep seam → per-character geosets           │
 │   (creation preview, character list, world, other players) ── NOT YET   │
 │  GlueXML creator controls ── NOT YET                                     │
 └──────────────────────────────────────────────────────────────────────────┘
```

## Layers

**A. Data model.** `registry/registry.json`: versioned; categories with stable ids, kind
(geoset / texture layer / attachment), geoset group, default, eligibility rows (race, sexes,
classes), options with stable ids, value and an optional class restriction, and Legion provenance
(`legion.verified`). Not a five-field struct and not a table of combinations: a character is a map
category → option. Removed options resolve to the default; ids are never reused.

**B. Client.** One compositor (`CCharacterComponent`) draws creation preview, character list,
the local player and other players, so one native insertion point (after the base geosets in
`GeosRenderPrep`) covers all four. The protocol and the glue API need no source change: the SDK's
`wxl.net`, `wxl.script`, Glue and Object events are enough, and they are implemented in the Lua mod.
What needs the client source: the seam in `GeosRenderPrep`, an owner for each component (which
guid, or "the creation preview"), and a way for a mod to set a geoset range on that component's
model (CLIENT_PROBE.md).

**C. Server.** A separate build (`realm/scripts/fetch-wrathpp.sh`): the other realms' exact source
plus one core patch and one module. The patch only adds numbers to the opcode table and routes the
client's to a handler the module sets; without the module (or with it refusing) they are dropped.
The module refuses to run unless `Wrathpp.Enable = 1`, `RealmID` = `Wrathpp.RealmID` and both world
and characters databases end in `_wrathpp`.

**D. UI.** The Legion 7.3.5 creator is adapted on top of the WrathPP_* functions once the renderer
exists; a control without a visible effect is not shipped (`WrathPP_Status()` reports
`renderer = false` until then).

## Decisions

| Decision | Why |
|---|---|
| New opcodes, not extra bytes on `CMSG_CHAR_CREATE`/`SMSG_CHAR_ENUM` | stock decoders don't accept trailing bytes; the net service's numbering and send gate make the extension negotiable and invisible to stock peers |
| Pending choice validated before `CMSG_CHAR_CREATE`, stored at `OnPlayerCreate` with a race/sex/class check | the stock create packet stays untouched; a choice can't attach to a character it wasn't checked for |
| Server sends the registry | client and server can't disagree on ids; the hash makes a mismatch explicit |
| Lua mod for protocol and glue API | runs on both the x64 source client and, by the SDK's design, the x86 injected runtime (fallback 2); no compiler needed to change it |
| Realm id 5, port 8087 | 3/4 are the app's OctoWoW/Legion ids |
| `$SERVER` re-pointed in `realm()` rather than new program paths | the Blizzard app rewrites the literal `"$SERVER/bin/<name>"` lines (`WowCtl.transform`) |
| Wrath++ module outside `warcraft/modules/` | `fetch-azerothcore.sh` copies that folder into every realm build |
