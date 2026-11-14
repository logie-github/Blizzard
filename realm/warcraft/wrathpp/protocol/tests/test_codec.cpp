// Tests of wrathpp_appearance.h (run.sh builds and runs them with the registry tools/registry.py
// wrote): the codec round trips, every malformed or invalid message refused with its own code,
// and the registry the Python tool encodes read and written again byte for byte.
#include "../wrathpp_appearance.h"

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <string>

using namespace wrathpp;

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #cond); ++failures; } } while (0)

static Registry SampleRegistry() {
    Registry reg;
    reg.version = 7;
    Category horns;
    horns.id = 1002; horns.kind = CategoryKind::Geoset; horns.geosetGroup = 24; horns.defaultOption = 1; horns.name = "Horns";
    horns.eligibility = {{10, 3, 0}, {4, 2, 0}};               // blood elves both sexes, night elf women
    horns.options = {{1, 1, 0, "None"}, {2, 2, 0, "Horns 1"}, {3, 3, 1u << (8 - 1), "Mage horns"}};
    Category blind;
    blind.id = 1003; blind.kind = CategoryKind::Geoset; blind.geosetGroup = 25; blind.defaultOption = 1; blind.name = "Blindfold";
    blind.eligibility = {{10, 3, 1u << (2 - 1)}};               // blood elf paladins only
    blind.options = {{1, 1, 0, "None"}, {2, 2, 0, "Blindfold 1"}};
    reg.categories = {horns, blind};
    return reg;
}

static void TestAppearanceRoundTrip() {
    Appearance a;
    a.registryVersion = 7;
    a.Set(1003, 2);
    a.Set(1002, 2);
    a.Set(1002, 3); // replaces, stays one entry per category
    CHECK(a.entries.size() == 2 && a.entries[0].category == 1002 && a.entries[0].option == 3);
    SetAppearance s;
    s.kind = SetKind::Existing; s.guid = 0x1234; s.race = 10; s.sex = 0; s.classId = 8; s.appearance = a;
    std::vector<uint8_t> bytes = EncodeSetAppearance(s);
    SetAppearance back;
    CHECK(DecodeSetAppearance(bytes.data(), bytes.size(), back) == Result::Ok);
    CHECK(back.appearance == a && back.guid == 0x1234 && back.kind == SetKind::Existing && back.classId == 8);
    // Deterministic: the same appearance built in another order is the same bytes.
    Appearance b; b.registryVersion = 7; b.Set(1002, 3); b.Set(1003, 2);
    s.appearance = b;
    CHECK(EncodeSetAppearance(s) == bytes);
}

static void TestMalformed() {
    SetAppearance s; s.kind = SetKind::PendingCreate; s.guid = 0; s.race = 10; s.sex = 1; s.classId = 2;
    s.appearance.registryVersion = 7; s.appearance.Set(1002, 2);
    std::vector<uint8_t> good = EncodeSetAppearance(s);
    SetAppearance out;
    for (std::size_t cut = 0; cut < good.size(); ++cut)
        CHECK(DecodeSetAppearance(good.data(), cut, out) != Result::Ok);       // every truncation
    std::vector<uint8_t> extra = good; extra.push_back(0);
    CHECK(DecodeSetAppearance(extra.data(), extra.size(), out) == Result::Malformed); // trailing byte
    std::vector<uint8_t> badKind = good; badKind[0] = 9;
    CHECK(DecodeSetAppearance(badKind.data(), badKind.size(), out) == Result::Malformed);
    std::vector<uint8_t> pendingWithGuid = good; pendingWithGuid[1] = 1;
    CHECK(DecodeSetAppearance(pendingWithGuid.data(), pendingWithGuid.size(), out) == Result::Malformed);
    // Duplicate / unsorted categories.
    Writer w; w.u8(0); w.u64(0); w.u8(10); w.u8(0); w.u8(1);
    w.u16(7); w.u8(2); w.u16(1002); w.u16(1); w.u16(1002); w.u16(2);
    CHECK(DecodeSetAppearance(w.bytes.data(), w.bytes.size(), out) == Result::Duplicate);
    // Too many entries.
    Writer m; m.u8(0); m.u64(0); m.u8(10); m.u8(0); m.u8(1); m.u16(7); m.u8(uint8_t(kMaxEntries + 1));
    CHECK(DecodeSetAppearance(m.bytes.data(), m.bytes.size(), out) == Result::TooMany);
    // Hello: bad magic, future protocol.
    ClientHello h; h.registryHash = 5;
    std::vector<uint8_t> hb = EncodeClientHello(h);
    ClientHello hout;
    CHECK(DecodeClientHello(hb.data(), hb.size(), hout) == Result::Ok && hout.registryHash == 5);
    hb[0] ^= 1;
    CHECK(DecodeClientHello(hb.data(), hb.size(), hout) == Result::Malformed);
    h.protocol = kProtocolMax + 1; hb = EncodeClientHello(h);
    CHECK(DecodeClientHello(hb.data(), hb.size(), hout) == Result::UnsupportedVersion);
    ServerHello sh; sh.protocolMin = kProtocolMax + 1; sh.protocolMax = kProtocolMax + 2;
    std::vector<uint8_t> shb = EncodeServerHello(sh);
    ServerHello shout;
    CHECK(DecodeServerHello(shb.data(), shb.size(), shout) == Result::UnsupportedVersion);
}

static void TestValidate() {
    Registry reg = SampleRegistry();
    CHECK(CheckRegistry(reg) == Result::Ok);
    Appearance a; a.registryVersion = 7; a.Set(1002, 2);
    uint16_t bad = 0;
    CHECK(Validate(reg, a, 10, 0, 1) == Result::Ok);
    CHECK(Validate(reg, a, 4, 0, 1, &bad) == Result::Ineligible && bad == 1002);  // night elf men: no
    CHECK(Validate(reg, a, 4, 1, 1) == Result::Ok);                                // night elf women: yes
    CHECK(Validate(reg, a, 1, 0, 1) == Result::Ineligible);                        // humans
    a.Set(1002, 3);
    CHECK(Validate(reg, a, 10, 0, 1) == Result::Ineligible);                       // option for mages only
    CHECK(Validate(reg, a, 10, 0, 8) == Result::Ok);
    a.Set(1002, 9);
    CHECK(Validate(reg, a, 10, 0, 8) == Result::UnknownOption);
    Appearance c; c.registryVersion = 7; c.Set(4000, 1);
    CHECK(Validate(reg, c, 10, 0, 8) == Result::UnknownCategory);
    Appearance d; d.registryVersion = 6; d.Set(1002, 1);
    CHECK(Validate(reg, d, 10, 0, 8) == Result::RegistryMismatch);
    Appearance e; e.registryVersion = 7; e.Set(1003, 2);
    CHECK(Validate(reg, e, 10, 0, 2) == Result::Ok);                               // paladin
    CHECK(Validate(reg, e, 10, 0, 8) == Result::Ineligible);                       // mage
}

static void TestResolve() {
    Registry reg = SampleRegistry();
    // A blood elf paladin with no rows: both categories at their defaults.
    Appearance none;
    Appearance r = Resolve(reg, none, 10, 0, 2);
    CHECK(r.entries.size() == 2 && r.Find(1002)->option == 1 && r.Find(1003)->option == 1);
    // Stored choices kept; the other category untouched (independence).
    Appearance stored; stored.Set(1003, 2);
    r = Resolve(reg, stored, 10, 0, 2);
    CHECK(r.Find(1002)->option == 1 && r.Find(1003)->option == 2);
    stored.Set(1002, 2);
    r = Resolve(reg, stored, 10, 0, 2);
    CHECK(r.Find(1002)->option == 2 && r.Find(1003)->option == 2);
    // A removed option, an unknown category: default, dropped.
    Appearance stale; stale.Set(1002, 77); stale.Set(5555, 1);
    r = Resolve(reg, stale, 10, 0, 2);
    CHECK(r.Find(1002)->option == 1 && !r.Find(5555));
    // An ineligible character gets nothing of the category.
    r = Resolve(reg, stored, 10, 0, 8);
    CHECK(r.Find(1002) && !r.Find(1003));
    // Geosets the renderer is asked for.
    std::vector<uint16_t> g = GeosetsFor(reg, Resolve(reg, stored, 10, 0, 2));
    CHECK(g.size() == 2 && g[0] == 2402 && g[1] == 2502);
}

static void TestBatchAndQuery() {
    std::vector<CharacterAppearance> list(3);
    for (std::size_t i = 0; i < list.size(); ++i) {
        list[i].guid = 100 + i; list[i].race = 10; list[i].classId = 2;
        list[i].appearance.registryVersion = 7; list[i].appearance.Set(1002, uint16_t(1 + i % 2));
    }
    std::vector<uint8_t> bytes = EncodeAppearances(list);
    std::vector<CharacterAppearance> back;
    CHECK(DecodeAppearances(bytes.data(), bytes.size(), back) == Result::Ok && back.size() == 3);
    CHECK(back[1].guid == 101 && back[1].appearance == list[1].appearance);
    std::vector<uint64_t> guids = {1, 2, 0xFFFFFFFFFFFFull};
    std::vector<uint8_t> q = EncodeQuery(guids);
    std::vector<uint64_t> qb;
    CHECK(DecodeQuery(q.data(), q.size(), qb) == Result::Ok && qb == guids);
    q[0] = uint8_t(kMaxBatch + 1);
    CHECK(DecodeQuery(q.data(), q.size(), qb) == Result::TooMany);
    ResultMessage m; m.kind = SetKind::Existing; m.guid = 9; m.code = Result::Ineligible; m.category = 1003;
    std::vector<uint8_t> mb = EncodeResult(m);
    ResultMessage mo;
    CHECK(DecodeResult(mb.data(), mb.size(), mo) == Result::Ok && mo.code == Result::Ineligible && mo.category == 1003);
}

static void TestRegistryRoundTrip() {
    Registry reg = SampleRegistry();
    Writer w; WriteRegistry(w, reg);
    Reader r(w.bytes.data(), w.bytes.size());
    Registry back;
    CHECK(ReadRegistry(r, back) == Result::Ok);
    Writer w2; WriteRegistry(w2, back);
    CHECK(w.bytes == w2.bytes && RegistryHash(reg) == RegistryHash(back));
    Registry broken = reg; broken.categories[0].defaultOption = 42;
    CHECK(CheckRegistry(broken) == Result::UnknownOption);
    broken = reg; std::swap(broken.categories[0], broken.categories[1]);
    CHECK(CheckRegistry(broken) == Result::Duplicate);
    broken = reg; broken.categories[0].options[1].value = 100;
    CHECK(CheckRegistry(broken) == Result::Malformed);
}

// The registry tools/registry.py built: read, checked, written again to the same bytes, its hash
// the one the tool printed.
static void TestToolRegistry(const char* path, const char* expectedHash) {
    std::ifstream f(path, std::ios::binary);
    std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    CHECK(!bytes.empty());
    Reader r(bytes.data(), bytes.size());
    Registry reg;
    CHECK(ReadRegistry(r, reg) == Result::Ok);
    CHECK(CheckRegistry(reg) == Result::Ok);
    Writer w; WriteRegistry(w, reg);
    CHECK(w.bytes == bytes);
    CHECK(RegistryHash(reg) == uint32_t(std::strtoul(expectedHash, nullptr, 16)));
    std::printf("tool registry: version %u, %zu categories, hash %08x\n", reg.version, reg.categories.size(), RegistryHash(reg));
    // the body options' display: a Human woman's defaults change nothing; a Curvy Draenei with style 16 at 75%,
    // a Petite Orc with no style, style 3 at None on an As drawn Gnome; a man and a race not in the list: nothing
    auto shown = [&](uint8_t race, uint8_t sex, uint16_t shape, uint16_t style, uint16_t density) {
        Appearance a; a.registryVersion = reg.version;
        a.Set(kBodyShape, shape); a.Set(kBodyStyle, style); a.Set(kBodyDensity, density);
        return BodyDisplay(reg, Resolve(reg, a, race, sex, 1), race);
    };
    CHECK(shown(1, 1, 1, 1, 5) == 0);
    CHECK(shown(11, 1, 3, 17, 4) == 42000 + 9 * 260 + 2 * 65 + 1 + 15 * 4 + 2);
    CHECK(shown(2, 1, 2, 1, 5) == 42000 + 1 * 260 + 1 * 65);
    CHECK(shown(7, 1, 1, 4, 1) == 0);
    CHECK(shown(1, 0, 3, 5, 5) == 0);
    CHECK(shown(9, 1, 3, 5, 5) == 0);
    CHECK(shown(10, 1, 4, 2, 2) == 42000 + 8 * 260 + 3 * 65 + 1);
}

int main(int argc, char** argv) {
    TestAppearanceRoundTrip();
    TestMalformed();
    TestValidate();
    TestResolve();
    TestBatchAndQuery();
    TestRegistryRoundTrip();
    if (argc == 3) TestToolRegistry(argv[1], argv[2]);
    std::printf(failures ? "%d FAILED\n" : "all passed\n", failures);
    return failures ? 1 : 0;
}
