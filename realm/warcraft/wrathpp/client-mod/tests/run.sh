#!/bin/sh
# Tests the Wrath++ client mod under LuaJIT (the runtime wxl.lua embeds) on a mock of its API: the
# server's messages made by the Python encoders the live server test checks against the server,
# and what the mod sends decoded as the server decodes it.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
WPP="$(cd "$HERE/../.." && pwd)"
OUT="$(mktemp -d "${TMPDIR:-/tmp}/wrathpp-mod.XXXXXX")"
trap 'rm -rf "$OUT"' EXIT
python3 -I - "$WPP" "$OUT" << 'PY'
import sys, os
wpp, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(wpp, "tools"))
import registry, struct, wrathpp_protocol as wp
version, blob, digest = registry.build(registry.DEFAULT)
hello = struct.pack("<IHHHI", wp.MAGIC, 1, 1, version, digest)
guid = 0x0000000000000042
appearance = struct.pack("<B", 1) + struct.pack("<QBBB", guid, 10, 0, 2) + wp.appearance(version, {1002: 2, 1003: 2})
result = struct.pack("<BQBH", 1, guid, 5, 1003)
with open(os.path.join(out, "fixtures.lua"), "w") as f:
    f.write("return {\n")
    for k, v in (("hello", hello), ("registry", blob), ("appearance", appearance), ("result", result)):
        f.write(f'  {k} = "{v.hex()}",\n')
    f.write(f'  hash = "{digest:08x}",\n  guid = "0x{guid:016X}",\n}}\n')
PY
luajit "$HERE/test_client_mod.lua" "$HERE" "$WPP/client-mod/wrathpp/init.lua" "$OUT/fixtures.lua" "$OUT/sent.txt"
python3 -I - "$WPP" "$OUT/sent.txt" << 'PY'
import sys, os, struct
sys.path.insert(0, os.path.join(sys.argv[1], "tools"))
import registry, wrathpp_protocol as wp
_, _, digest = registry.build(registry.DEFAULT)
sent = []
for line in open(sys.argv[2]):
    op, _, body = line.strip().partition(" ")
    sent.append((int(op, 16), bytes.fromhex(body)))
fails = 0
def check(cond, what):
    global fails
    print(("ok   " if cond else "FAIL ") + what)
    fails += 0 if cond else 1
def decode_set(b):
    kind, guid, race, sex, cls, version, n = struct.unpack_from("<BQBBBHB", b)
    entries = dict(struct.unpack_from("<HH", b, 15 + 4 * i) for i in range(n))
    assert 15 + 4 * n == len(b), "trailing bytes"
    return kind, guid, race, sex, cls, version, entries
ops = [op for op, _ in sent]
check(ops == [wp.CMSG_HELLO, wp.CMSG_SET_APPEARANCE, wp.CMSG_SET_APPEARANCE, wp.CMSG_QUERY], f"the mod sent hello, two choices and a query ({[hex(o) for o in ops]})")
magic, proto, h, caps = struct.unpack("<IHII", sent[0][1])
check(magic == wp.MAGIC and proto == 1 and h == digest and caps == wp.CAP_GEOSET, "  its hello: the magic, protocol 1, the registry's hash, geosets")
check(decode_set(sent[1][1]) == (0, 0, 10, 0, 2, 2, {1002: 2, 1003: 2}), "  the new character's: pending, blood elf man paladin, horns 2, blindfold 2")
check(decode_set(sent[2][1]) == (1, 0x42, 10, 0, 2, 2, {1002: 3, 1003: 2}), "  the change: that character, horns 3, blindfold kept at 2")
check(sent[3][1] == struct.pack("<BQ", 1, 0xAA), "  the query: one guid, 0xAA")
print("decoded as the server does:", "all passed" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
PY
# The creator (app/src/main/assets/wrathpp/WrathppCreate.lua) is tested on the rig (client-mod/rig/run.sh: the game's own
# creation screen, its creation logic and its tables), with the looks, by wrathpp-looks.yml. It had a stand-in screen
# of its own here, which passed three builds that failed on the phone, and is gone.
