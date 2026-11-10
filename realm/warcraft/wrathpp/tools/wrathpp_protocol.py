"""Wrath++ appearance protocol in Python: the same bytes as protocol/wrathpp_appearance.h, for the
tests that talk to a Wrath++ world server as a client would (tests/server_protocol_test.py).
docs/wrathpp/PROTOCOL.md is the specification."""
import struct

MAGIC = 0x31505057
PROTOCOL = 1
SMSG_HELLO, CMSG_HELLO, SMSG_REGISTRY, CMSG_SET_APPEARANCE, SMSG_APPEARANCE, SMSG_RESULT, CMSG_QUERY = range(0x521, 0x528)
RESULTS = ["ok", "malformed", "unsupported_version", "unknown_category", "unknown_option", "ineligible",
           "duplicate", "too_many", "not_owner", "registry_mismatch", "disabled", "character_mismatch"]
PENDING_CREATE, EXISTING = 0, 1
CAP_GEOSET = 1


def appearance(registry_version, entries):
    """entries: {category: option}; written sorted, one per category."""
    out = struct.pack("<HB", registry_version, len(entries))
    for cat in sorted(entries):
        out += struct.pack("<HH", cat, entries[cat])
    return out


def client_hello(registry_hash, protocol=PROTOCOL, capabilities=CAP_GEOSET):
    return struct.pack("<IHII", MAGIC, protocol, registry_hash, capabilities)


def set_appearance(kind, guid, race, sex, cls, registry_version, entries):
    return struct.pack("<BQBBB", kind, guid, race, sex, cls) + appearance(registry_version, entries)


def query(guids):
    return struct.pack("<B", len(guids)) + b"".join(struct.pack("<Q", g) for g in guids)


def server_hello(body):
    magic, pmin, pmax, version, digest = struct.unpack("<IHHHI", body)
    if magic != MAGIC:
        raise ValueError("bad magic")
    return {"protocol_min": pmin, "protocol_max": pmax, "registry_version": version, "registry_hash": digest}


def appearances(body):
    """SMSG_APPEARANCE: {guid: (race, sex, class, registry_version, {category: option})}."""
    count, pos, out = body[0], 1, {}
    for _ in range(count):
        guid, race, sex, cls, version, n = struct.unpack_from("<QBBBHB", body, pos)
        pos += 14
        entries = {}
        for _ in range(n):
            cat, opt = struct.unpack_from("<HH", body, pos)
            pos += 4
            entries[cat] = opt
        out[guid] = (race, sex, cls, version, entries)
    if pos != len(body):
        raise ValueError("trailing bytes")
    return out


def result(body):
    kind, guid, code, category = struct.unpack("<BQBH", body)
    return {"kind": kind, "guid": guid, "code": RESULTS[code] if code < len(RESULTS) else code, "category": category}
