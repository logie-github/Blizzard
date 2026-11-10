// Wrath++ extended appearance: the wire format, the registry and the validation rules, shared by
// the Wrath++ world server module (mod-wrathpp-customization) and the Wrath++ client mod
// (client-mod/), so both sides parse the same bytes the same way. Header-only, C++17, no
// dependencies beyond the standard library. docs/wrathpp/PROTOCOL.md is the specification; this
// file is its reference implementation and protocol/tests/ hold its tests.
//
// An appearance here is a map category -> option kept beside the stock 3.3.5a five fields
// (skin, face, hair style, hair colour, facial hair), never folded into them.
#ifndef WRATHPP_APPEARANCE_H
#define WRATHPP_APPEARANCE_H

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace wrathpp {

constexpr uint32_t kMagic = 0x31505057u;            // "WPP1" little-endian
constexpr uint16_t kProtocolVersion = 1;
constexpr uint16_t kProtocolMin = 1;
constexpr uint16_t kProtocolMax = 1;
constexpr std::size_t kMaxEntries = 32;              // categories in one appearance
constexpr std::size_t kMaxBatch = 64;                // appearances in one SMSG_APPEARANCE / guids in one query
constexpr std::size_t kMaxBody = 10000;              // WarcraftXL net service's max_send
constexpr std::size_t kMaxName = 48;                 // bytes of a category or option label

// Opcodes above the stock client's and its servers' (WarcraftXL net service: mods start at
// 0x521). The client mod declares 0x521-0x52A in its mod.json.
// (Named apart from the server's own Opcodes.h names, SMSG_WRATHPP_* there, which carry the same
// numbers: the module checks they agree.)
enum class Opcode : uint16_t {
    SmsgHello = 0x521,
    CmsgHello = 0x522,
    SmsgRegistry = 0x523,
    CmsgSetAppearance = 0x524,
    SmsgAppearance = 0x525,
    SmsgResult = 0x526,
    CmsgQuery = 0x527,
};
constexpr uint16_t kFirstOpcode = 0x521;
constexpr uint16_t kLastOpcode = 0x527;

enum class Result : uint8_t {
    Ok = 0,
    Malformed = 1,          // truncated, trailing bytes, bad magic, over a limit
    UnsupportedVersion = 2, // protocol or registry version the other side doesn't speak
    UnknownCategory = 3,
    UnknownOption = 4,
    Ineligible = 5,         // the category or option isn't for this race / sex / class
    Duplicate = 6,          // a category twice, or entries out of order
    TooMany = 7,
    NotOwner = 8,           // a character of another account
    RegistryMismatch = 9,   // the client's registry hash isn't the server's
    Disabled = 10,          // the realm doesn't run Wrath++ (or the client didn't say hello)
    CharacterMismatch = 11, // the created character's race/sex/class isn't the one the appearance was validated for
};

inline const char* ResultName(Result r);

enum class CategoryKind : uint8_t {
    Geoset = 1,      // option value = geoset variant within the category's geoset group (group*100 + value)
    TextureLayer = 2, // option value = row of the Wrath++ texture-layer table (client asset bundle); not rendered by v1 clients
    Attachment = 3,   // option value = row of the Wrath++ attachment table; not rendered by v1 clients
};

enum class SetKind : uint8_t {
    PendingCreate = 0, // for the next CMSG_CHAR_CREATE on this session (guid must be 0)
    Existing = 1,      // an existing character of this account, out of the world (character screen)
};

// ---- Little-endian buffers ---------------------------------------------------------------------

class Writer {
public:
    std::vector<uint8_t> bytes;
    void u8(uint8_t v) { bytes.push_back(v); }
    void u16(uint16_t v) { u8(uint8_t(v)); u8(uint8_t(v >> 8)); }
    void u32(uint32_t v) { u16(uint16_t(v)); u16(uint16_t(v >> 16)); }
    void u64(uint64_t v) { u32(uint32_t(v)); u32(uint32_t(v >> 32)); }
    void str(const std::string& s) {
        std::size_t n = std::min(s.size(), kMaxName);
        u8(uint8_t(n));
        bytes.insert(bytes.end(), s.begin(), s.begin() + std::ptrdiff_t(n));
    }
};

class Reader {
public:
    Reader(const uint8_t* data, std::size_t size) : p_(data), end_(data + size) {}
    bool ok() const { return ok_; }
    bool done() const { return ok_ && p_ == end_; }
    uint8_t u8() { if (!need(1)) return 0; return *p_++; }
    uint16_t u16() { uint16_t lo = u8(); return uint16_t(lo | (uint16_t(u8()) << 8)); }
    uint32_t u32() { uint32_t lo = u16(); return lo | (uint32_t(u16()) << 16); }
    uint64_t u64() { uint64_t lo = u32(); return lo | (uint64_t(u32()) << 32); }
    std::string str() {
        uint8_t n = u8();
        if (n > kMaxName || !need(n)) { ok_ = false; return {}; }
        std::string s(reinterpret_cast<const char*>(p_), n);
        p_ += n;
        return s;
    }
private:
    bool need(std::size_t n) {
        if (!ok_ || std::size_t(end_ - p_) < n) { ok_ = false; return false; }
        return true;
    }
    const uint8_t* p_;
    const uint8_t* end_;
    bool ok_ = true;
};

// ---- Appearance --------------------------------------------------------------------------------

struct Entry {
    uint16_t category = 0;
    uint16_t option = 0;
    bool operator==(const Entry& o) const { return category == o.category && option == o.option; }
};

// Canonical form: entries sorted by category, one per category. Equal appearances serialize to
// equal bytes.
struct Appearance {
    uint16_t registryVersion = 0;
    std::vector<Entry> entries;

    void Set(uint16_t category, uint16_t option) {
        auto it = std::lower_bound(entries.begin(), entries.end(), category,
            [](const Entry& e, uint16_t c) { return e.category < c; });
        if (it != entries.end() && it->category == category) it->option = option;
        else entries.insert(it, Entry{category, option});
    }
    const Entry* Find(uint16_t category) const {
        for (const Entry& e : entries) if (e.category == category) return &e;
        return nullptr;
    }
    bool operator==(const Appearance& o) const { return registryVersion == o.registryVersion && entries == o.entries; }
};

inline void WriteAppearance(Writer& w, const Appearance& a) {
    w.u16(a.registryVersion);
    w.u8(uint8_t(a.entries.size()));
    for (const Entry& e : a.entries) { w.u16(e.category); w.u16(e.option); }
}

// Reads one appearance and checks its shape (not the registry: see Validate).
inline Result ReadAppearance(Reader& r, Appearance& a) {
    a.registryVersion = r.u16();
    uint8_t n = r.u8();
    if (!r.ok()) return Result::Malformed;
    if (n > kMaxEntries) return Result::TooMany;
    a.entries.clear();
    a.entries.reserve(n);
    for (uint8_t i = 0; i < n; ++i) {
        Entry e;
        e.category = r.u16();
        e.option = r.u16();
        if (!r.ok()) return Result::Malformed;
        if (!a.entries.empty() && e.category <= a.entries.back().category) return Result::Duplicate;
        a.entries.push_back(e);
    }
    return Result::Ok;
}

// ---- Registry ----------------------------------------------------------------------------------

struct Eligibility {
    uint8_t race = 0;        // ChrRaces id
    uint8_t sexMask = 0;     // bit 0 male, bit 1 female
    uint32_t classMask = 0;  // bit (class-1); 0 = every class
};

struct Option {
    uint16_t id = 0;         // stable: never reused for another look
    uint16_t value = 0;      // meaning per CategoryKind
    uint32_t classMask = 0;  // further restriction; 0 = whatever the category allows
    std::string name;
};

struct Category {
    uint16_t id = 0;         // stable
    CategoryKind kind = CategoryKind::Geoset;
    uint16_t geosetGroup = 0;    // Geoset kind: the M2 geoset group (e.g. 24)
    uint16_t defaultOption = 0;  // used when a character has no row, and for removed options
    std::string name;
    std::vector<Eligibility> eligibility;
    std::vector<Option> options; // sorted by id
};

struct Registry {
    uint16_t version = 0;
    std::vector<Category> categories; // sorted by id

    const Category* FindCategory(uint16_t id) const {
        for (const Category& c : categories) if (c.id == id) return &c;
        return nullptr;
    }
};

inline bool ClassAllowed(uint32_t mask, uint8_t classId) {
    return mask == 0 || (classId >= 1 && classId <= 32 && (mask & (1u << (classId - 1))));
}

inline const Eligibility* EligibilityFor(const Category& c, uint8_t race, uint8_t sex, uint8_t classId) {
    for (const Eligibility& e : c.eligibility)
        if (e.race == race && sex < 2 && (e.sexMask & (1u << sex)) && ClassAllowed(e.classMask, classId)) return &e;
    return nullptr;
}

inline const Option* FindOption(const Category& c, uint16_t id) {
    for (const Option& o : c.options) if (o.id == id) return &o;
    return nullptr;
}

// Server-side check of a client's appearance for a character of race/sex/class.
inline Result Validate(const Registry& reg, const Appearance& a, uint8_t race, uint8_t sex, uint8_t classId,
                       uint16_t* badCategory = nullptr) {
    if (a.registryVersion != reg.version) return Result::RegistryMismatch;
    if (a.entries.size() > kMaxEntries) return Result::TooMany;
    for (std::size_t i = 0; i < a.entries.size(); ++i) {
        const Entry& e = a.entries[i];
        if (badCategory) *badCategory = e.category;
        if (i && e.category <= a.entries[i - 1].category) return Result::Duplicate;
        const Category* c = reg.FindCategory(e.category);
        if (!c) return Result::UnknownCategory;
        if (!EligibilityFor(*c, race, sex, classId)) return Result::Ineligible;
        const Option* o = FindOption(*c, e.option);
        if (!o) return Result::UnknownOption;
        if (!ClassAllowed(o->classMask, classId)) return Result::Ineligible;
    }
    if (badCategory) *badCategory = 0;
    return Result::Ok;
}

// What a character shows: every category it is eligible for, its stored choice where that is
// still valid, the category's default otherwise. Unknown or ineligible stored rows are dropped
// (a registry that removed them), never converted into the five stock fields.
inline Appearance Resolve(const Registry& reg, const Appearance& stored, uint8_t race, uint8_t sex, uint8_t classId) {
    Appearance out;
    out.registryVersion = reg.version;
    for (const Category& c : reg.categories) {
        if (!EligibilityFor(c, race, sex, classId)) continue;
        uint16_t option = c.defaultOption;
        if (const Entry* e = stored.Find(c.id)) {
            const Option* o = FindOption(c, e->option);
            if (o && ClassAllowed(o->classMask, classId)) option = e->option;
        }
        out.entries.push_back(Entry{c.id, option});
    }
    return out;
}

inline void WriteRegistry(Writer& w, const Registry& reg) {
    w.u16(reg.version);
    w.u16(uint16_t(reg.categories.size()));
    for (const Category& c : reg.categories) {
        w.u16(c.id);
        w.u8(uint8_t(c.kind));
        w.u16(c.geosetGroup);
        w.u16(c.defaultOption);
        w.str(c.name);
        w.u16(uint16_t(c.eligibility.size()));
        for (const Eligibility& e : c.eligibility) { w.u8(e.race); w.u8(e.sexMask); w.u32(e.classMask); }
        w.u16(uint16_t(c.options.size()));
        for (const Option& o : c.options) { w.u16(o.id); w.u16(o.value); w.u32(o.classMask); w.str(o.name); }
    }
}

inline Result ReadRegistry(Reader& r, Registry& reg) {
    reg.version = r.u16();
    uint16_t nc = r.u16();
    if (!r.ok()) return Result::Malformed;
    if (nc > 256) return Result::TooMany;
    reg.categories.clear();
    for (uint16_t i = 0; i < nc; ++i) {
        Category c;
        c.id = r.u16();
        uint8_t kind = r.u8();
        if (kind < 1 || kind > 3) return Result::Malformed;
        c.kind = CategoryKind(kind);
        c.geosetGroup = r.u16();
        c.defaultOption = r.u16();
        c.name = r.str();
        uint16_t ne = r.u16();
        if (!r.ok() || ne > 64) return Result::Malformed;
        for (uint16_t j = 0; j < ne; ++j) { Eligibility e; e.race = r.u8(); e.sexMask = r.u8(); e.classMask = r.u32(); c.eligibility.push_back(e); }
        uint16_t no = r.u16();
        if (!r.ok() || no > 512) return Result::Malformed;
        for (uint16_t j = 0; j < no; ++j) { Option o; o.id = r.u16(); o.value = r.u16(); o.classMask = r.u32(); o.name = r.str(); c.options.push_back(o); }
        if (!r.ok()) return Result::Malformed;
        if (!reg.categories.empty() && c.id <= reg.categories.back().id) return Result::Duplicate;
        reg.categories.push_back(std::move(c));
    }
    return r.done() ? Result::Ok : Result::Malformed;
}

// Structural checks a registry must pass before a server serves it (the tool runs the same).
inline Result CheckRegistry(const Registry& reg) {
    for (std::size_t i = 0; i < reg.categories.size(); ++i) {
        const Category& c = reg.categories[i];
        if (c.id == 0 || (i && c.id <= reg.categories[i - 1].id)) return Result::Duplicate;
        if (c.options.empty() || c.eligibility.empty()) return Result::Malformed;
        if (!FindOption(c, c.defaultOption)) return Result::UnknownOption;
        for (std::size_t j = 1; j < c.options.size(); ++j)
            if (c.options[j].id <= c.options[j - 1].id) return Result::Duplicate;
        if (c.kind == CategoryKind::Geoset)
            for (const Option& o : c.options) if (o.value > 99) return Result::Malformed;
    }
    return Result::Ok;
}

// FNV-1a over the canonical registry bytes: the hash both sides compare.
inline uint32_t Fnv1a(const std::vector<uint8_t>& bytes) {
    uint32_t h = 2166136261u;
    for (uint8_t b : bytes) { h ^= b; h *= 16777619u; }
    return h;
}

inline uint32_t RegistryHash(const Registry& reg) {
    Writer w;
    WriteRegistry(w, reg);
    return Fnv1a(w.bytes);
}

// ---- Messages ----------------------------------------------------------------------------------

struct ServerHello { uint16_t protocolMin = kProtocolMin, protocolMax = kProtocolMax, registryVersion = 0; uint32_t registryHash = 0; };
struct ClientHello { uint16_t protocol = kProtocolVersion; uint32_t registryHash = 0; uint32_t capabilities = 0; };
enum ClientCapability : uint32_t { CAP_GEOSET = 1, CAP_TEXTURE_LAYER = 2, CAP_ATTACHMENT = 4 };

inline std::vector<uint8_t> EncodeServerHello(const ServerHello& h) {
    Writer w; w.u32(kMagic); w.u16(h.protocolMin); w.u16(h.protocolMax); w.u16(h.registryVersion); w.u32(h.registryHash);
    return w.bytes;
}
inline Result DecodeServerHello(const uint8_t* d, std::size_t n, ServerHello& h) {
    Reader r(d, n);
    if (r.u32() != kMagic) return Result::Malformed;
    h.protocolMin = r.u16(); h.protocolMax = r.u16(); h.registryVersion = r.u16(); h.registryHash = r.u32();
    if (!r.done()) return Result::Malformed;
    return (h.protocolMin <= kProtocolVersion && kProtocolVersion <= h.protocolMax) ? Result::Ok : Result::UnsupportedVersion;
}

inline std::vector<uint8_t> EncodeClientHello(const ClientHello& h) {
    Writer w; w.u32(kMagic); w.u16(h.protocol); w.u32(h.registryHash); w.u32(h.capabilities);
    return w.bytes;
}
inline Result DecodeClientHello(const uint8_t* d, std::size_t n, ClientHello& h) {
    Reader r(d, n);
    if (r.u32() != kMagic) return Result::Malformed;
    h.protocol = r.u16(); h.registryHash = r.u32(); h.capabilities = r.u32();
    if (!r.done()) return Result::Malformed;
    return (h.protocol >= kProtocolMin && h.protocol <= kProtocolMax) ? Result::Ok : Result::UnsupportedVersion;
}

struct SetAppearance {
    SetKind kind = SetKind::PendingCreate;
    uint64_t guid = 0;
    uint8_t race = 0, sex = 0, classId = 0;
    Appearance appearance;
};

inline std::vector<uint8_t> EncodeSetAppearance(const SetAppearance& s) {
    Writer w; w.u8(uint8_t(s.kind)); w.u64(s.guid); w.u8(s.race); w.u8(s.sex); w.u8(s.classId);
    WriteAppearance(w, s.appearance);
    return w.bytes;
}
inline Result DecodeSetAppearance(const uint8_t* d, std::size_t n, SetAppearance& s) {
    if (n > kMaxBody) return Result::Malformed;
    Reader r(d, n);
    uint8_t kind = r.u8();
    s.guid = r.u64(); s.race = r.u8(); s.sex = r.u8(); s.classId = r.u8();
    if (!r.ok() || kind > 1 || s.sex > 1) return Result::Malformed;
    s.kind = SetKind(kind);
    if ((s.kind == SetKind::PendingCreate) != (s.guid == 0)) return Result::Malformed;
    Result res = ReadAppearance(r, s.appearance);
    if (res != Result::Ok) return res;
    return r.done() ? Result::Ok : Result::Malformed;
}

struct CharacterAppearance { uint64_t guid = 0; uint8_t race = 0, sex = 0, classId = 0; Appearance appearance; };

inline std::vector<uint8_t> EncodeAppearances(const std::vector<CharacterAppearance>& list) {
    Writer w; w.u8(uint8_t(std::min(list.size(), kMaxBatch)));
    for (std::size_t i = 0; i < list.size() && i < kMaxBatch; ++i) {
        const CharacterAppearance& c = list[i];
        w.u64(c.guid); w.u8(c.race); w.u8(c.sex); w.u8(c.classId);
        WriteAppearance(w, c.appearance);
    }
    return w.bytes;
}
inline Result DecodeAppearances(const uint8_t* d, std::size_t n, std::vector<CharacterAppearance>& list) {
    Reader r(d, n);
    uint8_t count = r.u8();
    if (!r.ok()) return Result::Malformed;
    if (count > kMaxBatch) return Result::TooMany;
    list.clear();
    for (uint8_t i = 0; i < count; ++i) {
        CharacterAppearance c;
        c.guid = r.u64(); c.race = r.u8(); c.sex = r.u8(); c.classId = r.u8();
        if (!r.ok()) return Result::Malformed;
        Result res = ReadAppearance(r, c.appearance);
        if (res != Result::Ok) return res;
        list.push_back(std::move(c));
    }
    return r.done() ? Result::Ok : Result::Malformed;
}

struct ResultMessage { SetKind kind = SetKind::PendingCreate; uint64_t guid = 0; Result code = Result::Ok; uint16_t category = 0; };

inline std::vector<uint8_t> EncodeResult(const ResultMessage& m) {
    Writer w; w.u8(uint8_t(m.kind)); w.u64(m.guid); w.u8(uint8_t(m.code)); w.u16(m.category);
    return w.bytes;
}
inline Result DecodeResult(const uint8_t* d, std::size_t n, ResultMessage& m) {
    Reader r(d, n);
    m.kind = SetKind(r.u8()); m.guid = r.u64(); m.code = Result(r.u8()); m.category = r.u16();
    return r.done() ? Result::Ok : Result::Malformed;
}

inline std::vector<uint8_t> EncodeQuery(const std::vector<uint64_t>& guids) {
    Writer w; w.u8(uint8_t(std::min(guids.size(), kMaxBatch)));
    for (std::size_t i = 0; i < guids.size() && i < kMaxBatch; ++i) w.u64(guids[i]);
    return w.bytes;
}
inline Result DecodeQuery(const uint8_t* d, std::size_t n, std::vector<uint64_t>& guids) {
    Reader r(d, n);
    uint8_t count = r.u8();
    if (!r.ok()) return Result::Malformed;
    if (count > kMaxBatch) return Result::TooMany;
    guids.clear();
    for (uint8_t i = 0; i < count; ++i) guids.push_back(r.u64());
    return r.done() ? Result::Ok : Result::Malformed;
}

inline const char* ResultName(Result r) {
    switch (r) {
        case Result::Ok: return "ok";
        case Result::Malformed: return "malformed";
        case Result::UnsupportedVersion: return "unsupported_version";
        case Result::UnknownCategory: return "unknown_category";
        case Result::UnknownOption: return "unknown_option";
        case Result::Ineligible: return "ineligible";
        case Result::Duplicate: return "duplicate";
        case Result::TooMany: return "too_many";
        case Result::NotOwner: return "not_owner";
        case Result::RegistryMismatch: return "registry_mismatch";
        case Result::Disabled: return "disabled";
        case Result::CharacterMismatch: return "character_mismatch";
    }
    return "unknown";
}

// The geosets a Geoset-kind appearance asks the renderer to show: group*100 + value for each
// eligible geoset category (the client hides the rest of the group). Used by the client mod and
// by the tests; the server never renders.
inline std::vector<uint16_t> GeosetsFor(const Registry& reg, const Appearance& a) {
    std::vector<uint16_t> out;
    for (const Entry& e : a.entries) {
        const Category* c = reg.FindCategory(e.category);
        if (!c || c->kind != CategoryKind::Geoset) continue;
        const Option* o = FindOption(*c, e.option);
        if (!o) continue;
        out.push_back(uint16_t(c->geosetGroup * 100 + o->value));
    }
    return out;
}

} // namespace wrathpp

#endif
