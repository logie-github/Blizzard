#!/usr/bin/env python3
"""A live test of the Wrath++ world server's appearance protocol, as a Wrath++ client speaks it
(tests/run-server-test.sh starts the servers and calls this):

    server_protocol_test.py create HOST PORT USER_A USER_B PASSWORD STATE_FILE
        the character screen brings hello, registry and looks before the list; a client hello; every
        bad message refused with its own code; a blood elf made with two Legion categories chosen;
        one category changed without the other; the looks in the next character list
    server_protocol_test.py after-restart HOST PORT USER_A USER_B PASSWORD STATE_FILE
        after the world server was restarted: the same looks in the list; the character enters the
        world, another account's character beside it sees its looks (sent at login, and asked
        for), and a change made in the world reaches the other player at once

The registry it expects is registry/registry.json's (horns 1002 and blindfold 1003 for blood
elves and night elves). Exits non-zero at the first thing that isn't as it should be.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WPP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WPP, "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(WPP), "server"))
import auth_check as ac  # noqa: E402
import registry  # noqa: E402
import wrathpp_protocol as wp  # noqa: E402

HORNS, BLINDFOLD = 1002, 1003
BLOOD_ELF, HUMAN, PALADIN = 10, 1, 2
CMSG_CHAR_DELETE = 0x38
SMSG_CHAR_DELETE = 0x3C

checks = 0


def expect(cond, what):
    global checks
    if not cond:
        raise SystemExit(f"FAIL {what}")
    checks += 1
    print(f"ok   {what}")


def character_screen(session):
    """CMSG_CHAR_ENUM, and everything the server sends up to its answer."""
    seen = []
    session.send(ac.CMSG_CHAR_ENUM)
    session.wait_for([ac.SMSG_CHAR_ENUM], seen=seen)
    return seen


def screen_messages(seen):
    by = {}
    order = []
    for opcode, body in seen:
        by.setdefault(opcode, []).append(body)
        order.append(opcode)
    return by, order


def wait_wpp(session, opcodes, seconds=20):
    seen = []
    session.wait_for(opcodes, seconds=seconds, seen=seen)
    return seen[-1]


def result_of(session):
    _, body = wait_wpp(session, [wp.SMSG_RESULT])
    return wp.result(body)


def connect(host, port, user, password):
    os.environ["WORLD_PORT"] = str(port)
    session, characters = ac.world_session(host, user, password, port)
    return session, characters


def hello_and_registry(session):
    seen = character_screen(session)
    by, order = screen_messages(seen)
    expect(wp.SMSG_HELLO in by and wp.SMSG_REGISTRY in by and wp.SMSG_APPEARANCE in by,
           "the character screen brings Wrath++'s hello, registry and looks")
    expect(order.index(wp.SMSG_HELLO) < order.index(ac.SMSG_CHAR_ENUM)
           and order.index(wp.SMSG_APPEARANCE) < order.index(ac.SMSG_CHAR_ENUM),
           "  before the character list itself")
    hello = wp.server_hello(by[wp.SMSG_HELLO][-1])
    blob = by[wp.SMSG_REGISTRY][-1]
    expect(registry.fnv1a(blob) == hello["registry_hash"], "  the registry's bytes are the hash the hello names")
    reg = registry.decode(blob)
    _, expected_blob, expected_hash = registry.build(registry.DEFAULT)
    expect(blob == expected_blob and hello["registry_hash"] == expected_hash,
           "  and the registry is registry.json's, byte for byte")
    expect(hello["protocol_min"] <= wp.PROTOCOL <= hello["protocol_max"], "  protocol 1 spoken")
    return hello, reg, wp.appearances(by[wp.SMSG_APPEARANCE][-1])


def create(host, port, user_a, user_b, password, state_file):
    session, characters = connect(host, port, user_a, password)
    hello, reg, looks = hello_and_registry(session)
    session.send(wp.CMSG_SET_APPEARANCE, wp.set_appearance(wp.PENDING_CREATE, 0, BLOOD_ELF, 0, PALADIN, hello["registry_version"], {HORNS: 2}))
    r = result_of(session)
    expect(r["code"] == "disabled", "a choice before the client's hello is refused (disabled)")

    session.send(wp.CMSG_HELLO, wp.client_hello(hello["registry_hash"] ^ 1))
    expect(result_of(session)["code"] == "registry_mismatch", "a hello with another registry's hash is refused")
    session.send(wp.CMSG_HELLO, wp.client_hello(hello["registry_hash"], protocol=9))
    expect(result_of(session)["code"] == "unsupported_version", "a hello of a protocol the server doesn't speak is refused")
    session.send(wp.CMSG_HELLO, wp.client_hello(hello["registry_hash"]))

    version = hello["registry_version"]
    bad = [
        (b"\x00\x01", "malformed", "a truncated message"),
        (wp.set_appearance(wp.PENDING_CREATE, 0, BLOOD_ELF, 0, PALADIN, version, {HORNS: 2}) + b"\x00", "malformed", "trailing bytes"),
        (wp.set_appearance(wp.PENDING_CREATE, 5, BLOOD_ELF, 0, PALADIN, version, {HORNS: 2}), "malformed", "a new character's choice with a guid"),
        (struct.pack("<BQBBB", 0, 0, BLOOD_ELF, 0, PALADIN) + struct.pack("<HB", version, 2) + struct.pack("<HHHH", HORNS, 2, HORNS, 3),
         "duplicate", "a category twice"),
        (struct.pack("<BQBBB", 0, 0, BLOOD_ELF, 0, PALADIN) + struct.pack("<HB", version, 33), "too_many", "33 categories"),
        (wp.set_appearance(wp.PENDING_CREATE, 0, BLOOD_ELF, 0, PALADIN, version, {HORNS: 99}), "unknown_option", "an option that doesn't exist"),
        (wp.set_appearance(wp.PENDING_CREATE, 0, BLOOD_ELF, 0, PALADIN, version, {4242: 1}), "unknown_category", "a category that doesn't exist"),
        (wp.set_appearance(wp.PENDING_CREATE, 0, HUMAN, 0, PALADIN, version, {HORNS: 2}), "ineligible", "horns for a human"),
        (wp.set_appearance(wp.PENDING_CREATE, 0, BLOOD_ELF, 0, PALADIN, version + 1, {HORNS: 2}), "registry_mismatch", "a choice made against another registry version"),
    ]
    for body, code, what in bad:
        session.send(wp.CMSG_SET_APPEARANCE, body)
        r = result_of(session)
        expect(r["code"] == code, f"{what} is refused ({code})")

    # A blood elf paladin made with horns 2 and blindfold 2 chosen.
    name = "Wppa"
    session.send(wp.CMSG_SET_APPEARANCE, wp.set_appearance(wp.PENDING_CREATE, 0, BLOOD_ELF, 0, PALADIN, version, {HORNS: 2, BLINDFOLD: 2}))
    expect(result_of(session)["code"] == "ok", "the new character's choices are accepted")
    session.send(ac.CMSG_CHAR_CREATE, name.encode() + b"\0" + bytes([BLOOD_ELF, PALADIN, 0, 0, 0, 0, 0, 0, 0]))
    seen = []
    session.wait_for([ac.SMSG_CHAR_CREATE], seen=seen)
    expect(seen[-1][1][0] == ac.CHAR_CREATE_SUCCESS, "the character is created")
    results = [wp.result(b) for o, b in seen if o == wp.SMSG_RESULT]
    expect(results and results[-1]["code"] == "ok" and results[-1]["guid"] != 0, "  and its choices kept (the result names its guid)")
    guid = results[-1]["guid"]

    # A choice validated for a paladin, then a mage made: not kept.
    session.send(wp.CMSG_SET_APPEARANCE, wp.set_appearance(wp.PENDING_CREATE, 0, BLOOD_ELF, 0, PALADIN, version, {HORNS: 3}))
    expect(result_of(session)["code"] == "ok", "a second new character's choices accepted")
    session.send(ac.CMSG_CHAR_CREATE, b"Wppmage\0" + bytes([BLOOD_ELF, 8, 0, 0, 0, 0, 0, 0, 0]))
    seen = []
    session.wait_for([ac.SMSG_CHAR_CREATE], seen=seen)
    results = [wp.result(b) for o, b in seen if o == wp.SMSG_RESULT]
    expect(results and results[-1]["code"] == "character_mismatch", "  but a character of another class than they were checked for doesn't get them")
    mage = results[-1]["guid"]

    seen = character_screen(session)
    by, _ = screen_messages(seen)
    looks = wp.appearances(by[wp.SMSG_APPEARANCE][-1])
    expect(looks[guid][4] == {HORNS: 2, BLINDFOLD: 2}, "the character list's looks: horns 2, blindfold 2")
    expect(looks[mage][4] == {HORNS: 1, BLINDFOLD: 1}, "  the mage at the defaults")

    # One category changed, the other left as it was (independence).
    session.send(wp.CMSG_SET_APPEARANCE, wp.set_appearance(wp.EXISTING, guid, BLOOD_ELF, 0, PALADIN, version, {HORNS: 3, BLINDFOLD: 2}))
    expect(result_of(session)["code"] == "ok", "horns changed to 3 on the character screen")
    _, body = wait_wpp(session, [wp.SMSG_APPEARANCE])
    expect(wp.appearances(body)[guid][4] == {HORNS: 3, BLINDFOLD: 2}, "  blindfold still 2")
    session.send(wp.CMSG_SET_APPEARANCE, wp.set_appearance(wp.EXISTING, guid, BLOOD_ELF, 1, PALADIN, version, {HORNS: 3}))
    expect(result_of(session)["code"] == "character_mismatch", "a change for the character as another sex is refused")
    session.sock.close()

    # Another account can neither change nor see the change go through.
    other, _ = connect(host, port, user_b, password)
    hello_b, _, _ = hello_and_registry(other)
    other.send(wp.CMSG_HELLO, wp.client_hello(hello_b["registry_hash"]))
    other.send(wp.CMSG_SET_APPEARANCE, wp.set_appearance(wp.EXISTING, guid, BLOOD_ELF, 0, PALADIN, version, {HORNS: 1}))
    expect(result_of(other)["code"] == "not_owner", "another account's change to the character is refused")
    other.send(ac.CMSG_CHAR_CREATE, b"Wppb\0" + bytes([BLOOD_ELF, PALADIN, 1, 0, 0, 0, 0, 0, 0]))
    seen = []
    other.wait_for([ac.SMSG_CHAR_CREATE], seen=seen)
    expect(seen[-1][1][0] == ac.CHAR_CREATE_SUCCESS, "the second account's blood elf is created (no choices: defaults)")
    other.sock.close()

    with open(state_file, "w") as f:
        json.dump({"guid": guid, "mage": mage, "version": version}, f)


def after_restart(host, port, user_a, user_b, password, state_file):
    with open(state_file) as f:
        state = json.load(f)
    guid, version = state["guid"], state["version"]
    a, _ = connect(host, port, user_a, password)
    hello, _, looks = hello_and_registry(a)
    expect(looks[guid][4] == {HORNS: 3, BLINDFOLD: 2}, "after the world server's restart: horns 3, blindfold 2")
    a.send(wp.CMSG_HELLO, wp.client_hello(hello["registry_hash"]))
    a.send(ac.CMSG_PLAYER_LOGIN, struct.pack("<Q", guid))
    seen = []
    a.wait_for([ac.SMSG_LOGIN_VERIFY_WORLD], seconds=120, seen=seen)
    own = [wp.appearances(b) for o, b in seen if o == wp.SMSG_APPEARANCE]
    a.pump(3, seen)
    own += [wp.appearances(b) for o, b in seen if o == wp.SMSG_APPEARANCE]
    expect(any(guid in m and m[guid][4] == {HORNS: 3, BLINDFOLD: 2} for m in own), "in the world, the player is sent its own looks")

    b, characters = connect(host, port, user_b, password)
    hello_b, _, looks_b = hello_and_registry(b)
    b_guid = next(c[0] for c in characters() if c[1] == "Wppb")
    b.send(wp.CMSG_HELLO, wp.client_hello(hello_b["registry_hash"]))
    b.send(ac.CMSG_PLAYER_LOGIN, struct.pack("<Q", b_guid))
    b.wait_for([ac.SMSG_LOGIN_VERIFY_WORLD], seconds=120)
    b.send(wp.CMSG_QUERY, wp.query([guid, b_guid, 0xDEAD]))
    _, body = wait_wpp(b, [wp.SMSG_APPEARANCE])
    got = wp.appearances(body)
    while guid not in got:  # (its own looks, sent at login, may come first)
        _, body = wait_wpp(b, [wp.SMSG_APPEARANCE])
        got = wp.appearances(body)
    expect(got[guid][4] == {HORNS: 3, BLINDFOLD: 2}, "another player in the world, asking, gets the character's looks")
    expect(0xDEAD not in got, "  and nothing for a guid that is no character")

    seen = []
    a.pump(3, seen)
    told = {}
    for o, body in seen:
        if o == wp.SMSG_APPEARANCE:
            told.update(wp.appearances(body))
    expect(b_guid in told and told[b_guid][4] == {HORNS: 1, BLINDFOLD: 1}, "the first player was told the second's looks as it arrived")

    # A change in the world reaches the player beside it at once.
    a.send(wp.CMSG_SET_APPEARANCE, wp.set_appearance(wp.EXISTING, guid, BLOOD_ELF, 0, PALADIN, version, {HORNS: 2, BLINDFOLD: 2}))
    expect(result_of(a)["code"] == "ok", "horns changed to 2 in the world")
    seen = []
    b.pump(3, seen)
    told = {}
    for o, body in seen:
        if o == wp.SMSG_APPEARANCE:
            told.update(wp.appearances(body))
    expect(guid in told and told[guid][4] == {HORNS: 2, BLINDFOLD: 2}, "  the other player is told at once, blindfold unchanged")
    for s in (a, b):
        s.send(ac.CMSG_LOGOUT_REQUEST)
        s.wait_for([ac.SMSG_LOGOUT_COMPLETE], seconds=40)
        s.sock.close()


def main(argv):
    if len(argv) != 8 or argv[1] not in ("create", "after-restart"):
        print(__doc__, file=sys.stderr)
        return 2
    host, port, user_a, user_b, password, state = argv[2], int(argv[3]), argv[4], argv[5], argv[6], argv[7]
    (create if argv[1] == "create" else after_restart)(host, port, user_a, user_b, password, state)
    print(f"{checks} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
