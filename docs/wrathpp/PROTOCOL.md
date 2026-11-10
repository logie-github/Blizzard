# Wrath++ appearance protocol, version 1

The extended appearance travels in messages of its own, beside the stock 3.3.5a (12340) protocol;
no stock packet carries extra bytes. Reference implementation:
`realm/warcraft/wrathpp/protocol/wrathpp_appearance.h` (C++17, header-only; the server module
uses it). Python mirror: `realm/warcraft/wrathpp/tools/wrathpp_protocol.py` and `tools/registry.py`.
Lua client: `realm/warcraft/wrathpp/client-mod/wrathpp/init.lua`.

## Numbers and framing

WarcraftXL's net service gives client mods the numbers above the stock client's and its servers'
(0x51F/0x520 are TrinityCore 9's redirect): mods start at **0x521**. The stock AzerothCore closes the
connection on any number ≥ 0x521; only the Wrath++ server build (core patch
`wrathpp/patches/azerothcore/0001`) knows these.

| Opcode | Direction | Name | Body |
|---|---|---|---|
| 0x521 | S→C | `SMSG_WRATHPP_HELLO` | u32 magic `0x31505057` ("WPP1"), u16 protocol_min, u16 protocol_max, u16 registry_version, u32 registry_hash |
| 0x522 | C→S | `CMSG_WRATHPP_HELLO` | u32 magic, u16 protocol, u32 registry_hash, u32 capabilities (1 geoset, 2 texture layer, 4 attachment) |
| 0x523 | S→C | `SMSG_WRATHPP_REGISTRY` | the registry, below |
| 0x524 | C→S | `CMSG_WRATHPP_SET_APPEARANCE` | u8 kind (0 pending create, 1 existing), u64 guid (0 for pending), u8 race, u8 sex, u8 class, Appearance |
| 0x525 | S→C | `SMSG_WRATHPP_APPEARANCE` | u8 count (≤ 64), then count × (u64 guid, u8 race, u8 sex, u8 class, Appearance) |
| 0x526 | S→C | `SMSG_WRATHPP_RESULT` | u8 kind, u64 guid, u8 code, u16 category (the offending one, or 0) |
| 0x527 | C→S | `CMSG_WRATHPP_QUERY` | u8 count (≤ 64), count × u64 guid |

Little-endian throughout. Bodies stay under 10000 bytes (the net service's `max_send`).

**Appearance**: u16 registry_version, u8 n (≤ 32), n × (u16 category, u16 option), categories
strictly ascending: one canonical byte form per look (a repeated or unsorted category is
`duplicate`).

**Registry**: u16 version, u16 category count, then per category (ascending id): u16 id, u8 kind
(1 geoset, 2 texture layer, 3 attachment), u16 geoset_group, u16 default_option, name (u8 length +
bytes, ≤ 48), u16 eligibility count × (u8 race, u8 sex_mask [1 male, 2 female], u32 class_mask
[bit class-1; 0 = all]), u16 option count × (u16 id, u16 value, u32 class_mask, name). Its hash is
FNV-1a 32 over exactly these bytes. Built from `registry/registry.json` by `tools/registry.py`, which
writes byte-for-byte what `WriteRegistry` writes (checked by `protocol/tests/run.sh`).

## Lifecycle

1. The server, on sending `SMSG_CHAR_ENUM`, first sends HELLO, REGISTRY and one APPEARANCE with the
   account's characters (resolved: every eligible category, stored choice or default). A WarcraftXL
   client's send gate opens on the first claimed message the server sends, so the client can never
   send a Wrath++ number to a server that doesn't know it.
2. The client checks the magic and the protocol range, hashes the registry bytes and compares
   with the hello; on success it sends CMSG_HELLO with that hash. A wrong hash is
   `registry_mismatch`, a protocol outside the range `unsupported_version`. Until a valid client
   hello on this connection, every other client message is answered `disabled`.
3. **Creation**: the client sends SET kind 0 (guid 0, the race/sex/class it is about to create),
   validated at once (answer: RESULT ok or the reason). It then sends the stock `CMSG_CHAR_CREATE`.
   When the character is committed, the server stores the choices only if the created character's
   race, sex and class are those they were validated for (else RESULT `character_mismatch`, and
   the character has the defaults), and sends RESULT ok with the new guid. One pending choice per
   account, consumed by the next creation.
4. **Change** (character screen or in the world): SET kind 1 with the guid. The server checks the
   character is the account's (`not_owner`), that race/sex/class are the character's
   (`character_mismatch`), validates, stores the full map, answers RESULT and APPEARANCE; a character
   in the world is also sent to every player within visibility range whose client said hello.
5. **In the world**: at login the player's look goes to the player and to the Wrath++ clients
   around it. A client seeing a player it has no look for sends QUERY (batches of up to 64); the
   server answers APPEARANCE for the guids that are players (unknown guids are left out).
6. A new connection (`OnAccountLogin`) forgets the hello and any pending choice.

## Result codes

0 ok, 1 malformed, 2 unsupported_version, 3 unknown_category, 4 unknown_option, 5 ineligible,
6 duplicate, 7 too_many, 8 not_owner, 9 registry_mismatch, 10 disabled, 11 character_mismatch.

## Validation (server, `Validate` in the header)

registry_version equal to the server's; ≤ 32 entries; categories strictly ascending; each category
in the registry; the character's race and sex in one of its eligibility rows with the class in that
row's mask; the option in the category; the class in the option's mask.

## Persistence

`acore_characters_wrathpp.wrathpp_character_customization (guid, category_id, option_id,
registry_version, updated)`, primary key (guid, category_id). Written as the full map in one
transaction. The stock five fields in `characters` are never written by this. A stored option the
registry no longer has, or a category the character is no longer eligible for, resolves to the
default (or is left out) when sent; it is never converted into the five fields. Rows of deleted
characters go with `OnPlayerDelete`; orphans (a creation that failed after storing) at start-up.

## Compatibility

- Stock client on the Wrath++ server: receives 0x521-0x525 before the character list. The decompiled
  `NetClient::ProcessMessage` ignores numbers it has no handler for; whether the stock binary behaves
  identically is **untested**. It never sends Wrath++ numbers, so it plays with default looks.
- Wrath++ client on a stock server: the server never sends 0x521, so the mod's send gate never opens
  and the mod sends nothing; the client plays as stock.
- A future protocol 2 server keeps answering protocol 1 clients as long as `protocol_min` ≤ 1.
