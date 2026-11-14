// SPDX-License-Identifier: GPL-3.0-or-later
// Wrath++'s extended appearance on the server (docs/wrathpp/PROTOCOL.md, ARCHITECTURE.md): the
// registry served to clients, every client choice validated against it, the choices kept per
// character in the Wrath++ characters database (wrathpp_character_customization) and sent to the
// character screen, to the player and to the players around them.
//
// Built only into the Wrath++ server (realm/scripts/fetch-wrathpp.sh), which also carries the core
// patch that gives the messages their numbers. Even there it does nothing unless
// Wrathpp.Enable = 1, the realm is Wrathpp.RealmID, and both of the realm's databases are the
// Wrath++ ones (*_wrathpp): on any other database it refuses to start and says why.

#include "CharacterCache.h"
#include "Config.h"
#include "DBCStores.h"
#include "DatabaseEnv.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "ObjectAccessor.h"
#include "Player.h"
#include "ScriptMgr.h"
#include "WorldPacket.h"
#include "WorldSession.h"
#include "WrathppProtocol.h"
#include "wrathpp_appearance.h"

#include <fstream>
#include <iterator>
#include <mutex>
#include <optional>
#include <unordered_map>

// The core patch's numbers (Opcodes.h) are the protocol's.
static_assert(SMSG_WRATHPP_HELLO == uint16(wrathpp::Opcode::SmsgHello) && CMSG_WRATHPP_HELLO == uint16(wrathpp::Opcode::CmsgHello) &&
    SMSG_WRATHPP_REGISTRY == uint16(wrathpp::Opcode::SmsgRegistry) && CMSG_WRATHPP_SET_APPEARANCE == uint16(wrathpp::Opcode::CmsgSetAppearance) &&
    SMSG_WRATHPP_APPEARANCE == uint16(wrathpp::Opcode::SmsgAppearance) && SMSG_WRATHPP_RESULT == uint16(wrathpp::Opcode::SmsgResult) &&
    CMSG_WRATHPP_QUERY == uint16(wrathpp::Opcode::CmsgQuery), "Wrath++ opcodes differ between the core patch and the protocol");

namespace
{
    using namespace wrathpp;

    struct SessionState
    {
        bool hello = false;
        uint32 capabilities = 0;
        std::optional<SetAppearance> pendingCreate;
    };

    struct State
    {
        bool enabled = false;
        Registry registry;
        std::vector<uint8_t> registryBytes;
        uint32_t registryHash = 0;
        std::mutex mutex;                                        // sessions and cache
        std::unordered_map<uint32, SessionState> sessions;       // by account
        std::unordered_map<uint32, Appearance> cache;            // stored choices, by character low guid
    };

    State& S()
    {
        static State state;
        return state;
    }

    // The database name in a "host;port;user;password;database" setting.
    std::string DatabaseName(std::string const& info)
    {
        std::size_t at = info.rfind(';');
        return at == std::string::npos ? info : info.substr(at + 1);
    }

    bool EndsWith(std::string const& s, std::string const& tail)
    {
        return s.size() >= tail.size() && s.compare(s.size() - tail.size(), tail.size(), tail) == 0;
    }

    void Send(WorldSession* session, uint16 opcode, std::vector<uint8_t> const& body)
    {
        WorldPacket packet(opcode, body.size());
        if (!body.empty())
            packet.append(body.data(), body.size());
        session->SendPacket(&packet);
    }

    void SendResult(WorldSession* session, SetKind kind, uint64 guid, Result code, uint16 category = 0)
    {
        ResultMessage m;
        m.kind = kind;
        m.guid = guid;
        m.code = code;
        m.category = category;
        Send(session, SMSG_WRATHPP_RESULT, EncodeResult(m));
        if (code != Result::Ok)
            LOG_INFO("module", "Wrath++: account {} {} {}: {} (category {})", session->GetAccountId(),
                kind == SetKind::PendingCreate ? "new character" : "character", guid, ResultName(code), category);
    }

    // A character's stored choices: the cache, else its rows (cached from then on).
    Appearance Stored(uint32 low)
    {
        {
            std::lock_guard<std::mutex> lock(S().mutex);
            auto it = S().cache.find(low);
            if (it != S().cache.end())
                return it->second;
        }
        Appearance a;
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT category_id, option_id FROM wrathpp_character_customization WHERE guid = {} ORDER BY category_id", low))
        {
            do
            {
                Field* f = result->Fetch();
                a.Set(f[0].Get<uint16>(), f[1].Get<uint16>());
            } while (result->NextRow());
        }
        std::lock_guard<std::mutex> lock(S().mutex);
        S().cache[low] = a;
        return a;
    }

    void Store(uint32 low, Appearance const& a)
    {
        CharacterDatabaseTransaction trans = CharacterDatabase.BeginTransaction();
        trans->Append("DELETE FROM wrathpp_character_customization WHERE guid = {}", low);
        for (Entry const& e : a.entries)
            trans->Append("INSERT INTO wrathpp_character_customization (guid, category_id, option_id, registry_version) VALUES ({}, {}, {}, {})",
                low, e.category, e.option, a.registryVersion);
        CharacterDatabase.CommitTransaction(trans);
        std::lock_guard<std::mutex> lock(S().mutex);
        S().cache[low] = a;
    }

    bool SaidHello(WorldSession* session)
    {
        std::lock_guard<std::mutex> lock(S().mutex);
        auto it = S().sessions.find(session->GetAccountId());
        return it != S().sessions.end() && it->second.hello;
    }

    CharacterAppearance Shown(ObjectGuid guid, uint8 race, uint8 sex, uint8 classId)
    {
        CharacterAppearance c;
        c.guid = guid.GetRawValue();
        c.race = race;
        c.sex = sex;
        c.classId = classId;
        c.appearance = Resolve(S().registry, Stored(guid.GetCounter()), race, sex, classId);
        return c;
    }

    CharacterAppearance Shown(Player* player)
    {
        return Shown(player->GetGUID(), player->getRace(), player->getGender(), player->getClass());
    }

    // A woman's body options (Shape, Style, Density: wrathpp_appearance.h's BodyDisplay) as her display, when the tables
    // have that display (the app puts its rows in, with the game's, when the body options package is imported); her
    // race's own otherwise. Kept as her native display too, so a shapeshift or a transform comes back to it.
    void ApplyBody(Player* player)
    {
        if (player->getGender() != GENDER_FEMALE)
            return;
        uint8 race = player->getRace(true);                   // her own race's model, whatever race the world takes her for
        uint32 display = BodyDisplay(S().registry, Resolve(S().registry, Stored(player->GetGUID().GetCounter()), race, player->getGender(), player->getClass()), race);
        uint32 native = player->GetNativeDisplayId();
        bool ours = native >= kBodyDisplayBase && native < kBodyDisplayBase + 10 * 260;
        if (!display)
        {
            // none (any more): her race's own display, where one of these was hers
            PlayerInfo const* info = sObjectMgr->GetPlayerInfo(race, player->getClass());
            if (!ours || !info)
                return;
            display = info->displayId_f;
        }
        else if (!sCreatureDisplayInfoStore.LookupEntry(display))
        {
            LOG_INFO("module", "Wrath++: {}'s body options are display {}, which the tables don't have (no body options package imported)", player->GetName(), display);
            return;
        }
        if (native == display)
            return;
        // kept as her native display; her display as well unless something (a shapeshift, a transform) shows another now
        bool same = player->GetDisplayId() == native;
        player->SetNativeDisplayId(display);
        if (same)
            player->SetDisplayId(display);
    }

    // The player's look to the Wrath++ clients that can see them (and to the player).
    void Broadcast(Player* player)
    {
        std::vector<uint8_t> body = EncodeAppearances({Shown(player)});
        if (SaidHello(player->GetSession()))
            Send(player->GetSession(), SMSG_WRATHPP_APPEARANCE, body);
        Map* map = player->GetMap();
        if (!map)
            return;
        float range = player->GetVisibilityRange();
        for (MapRefMgr::const_iterator itr = map->GetPlayers().begin(); itr != map->GetPlayers().end(); ++itr)
        {
            Player* other = itr->GetSource();
            if (!other || other == player || !other->IsInWorld() || !other->IsWithinDist(player, range))
                continue;
            if (SaidHello(other->GetSession()))
                Send(other->GetSession(), SMSG_WRATHPP_APPEARANCE, body);
        }
    }

    // Before the character list: who the server is, its registry, and the looks of the account's characters.
    void SendCharacterScreen(WorldSession* session)
    {
        ServerHello hello;
        hello.registryVersion = S().registry.version;
        hello.registryHash = S().registryHash;
        Send(session, SMSG_WRATHPP_HELLO, EncodeServerHello(hello));
        Send(session, SMSG_WRATHPP_REGISTRY, S().registryBytes);
        std::vector<CharacterAppearance> list;
        if (QueryResult result = CharacterDatabase.Query(
                "SELECT guid, race, gender, class FROM characters WHERE account = {} AND deleteInfos_Account IS NULL ORDER BY guid LIMIT {}",
                session->GetAccountId(), uint32(kMaxBatch)))
        {
            do
            {
                Field* f = result->Fetch();
                list.push_back(Shown(ObjectGuid::Create<HighGuid::Player>(f[0].Get<uint32>()), f[1].Get<uint8>(), f[2].Get<uint8>(), f[3].Get<uint8>()));
            } while (result->NextRow());
        }
        Send(session, SMSG_WRATHPP_APPEARANCE, EncodeAppearances(list));
    }

    void HandleHello(WorldSession* session, std::vector<uint8_t> const& body)
    {
        ClientHello hello;
        Result r = DecodeClientHello(body.data(), body.size(), hello);
        if (r == Result::Ok && hello.registryHash != S().registryHash)
            r = Result::RegistryMismatch;
        if (r != Result::Ok)
        {
            SendResult(session, SetKind::PendingCreate, 0, r);
            return;
        }
        std::lock_guard<std::mutex> lock(S().mutex);
        SessionState& state = S().sessions[session->GetAccountId()];
        state.hello = true;
        state.capabilities = hello.capabilities;
        LOG_INFO("module", "Wrath++: account {} client speaks protocol {} (capabilities {:#x})", session->GetAccountId(), hello.protocol, hello.capabilities);
    }

    void HandleSet(WorldSession* session, std::vector<uint8_t> const& body)
    {
        SetAppearance set;
        Result r = DecodeSetAppearance(body.data(), body.size(), set);
        if (r != Result::Ok)
        {
            SendResult(session, set.kind, set.guid, r);
            return;
        }
        uint16 bad = 0;
        if (set.kind == SetKind::PendingCreate)
        {
            r = Validate(S().registry, set.appearance, set.race, set.sex, set.classId, &bad);
            if (r == Result::Ok)
            {
                std::lock_guard<std::mutex> lock(S().mutex);
                S().sessions[session->GetAccountId()].pendingCreate = set;
            }
            SendResult(session, set.kind, 0, r, bad);
            return;
        }
        // An existing character: the account's own, as it is (not as the client says it is).
        ObjectGuid guid(set.guid);
        CharacterCacheEntry const* entry = guid.IsPlayer() ? sCharacterCache->GetCharacterCacheByGuid(guid) : nullptr;
        if (!entry || entry->AccountId != session->GetAccountId())
        {
            SendResult(session, set.kind, set.guid, Result::NotOwner);
            return;
        }
        if (entry->Race != set.race || entry->Sex != set.sex || entry->Class != set.classId)
        {
            SendResult(session, set.kind, set.guid, Result::CharacterMismatch);
            return;
        }
        r = Validate(S().registry, set.appearance, entry->Race, entry->Sex, entry->Class, &bad);
        if (r != Result::Ok)
        {
            SendResult(session, set.kind, set.guid, r, bad);
            return;
        }
        Store(guid.GetCounter(), set.appearance);
        SendResult(session, set.kind, set.guid, Result::Ok);
        if (Player* player = ObjectAccessor::FindConnectedPlayer(guid); player && player->IsInWorld())
        {
            ApplyBody(player);
            Broadcast(player);
        }
        else
            Send(session, SMSG_WRATHPP_APPEARANCE, EncodeAppearances({Shown(guid, entry->Race, entry->Sex, entry->Class)}));
    }

    void HandleQuery(WorldSession* session, std::vector<uint8_t> const& body)
    {
        std::vector<uint64_t> guids;
        if (DecodeQuery(body.data(), body.size(), guids) != Result::Ok)
        {
            SendResult(session, SetKind::Existing, 0, Result::Malformed);
            return;
        }
        std::vector<CharacterAppearance> list;
        for (uint64_t raw : guids)
        {
            ObjectGuid guid(raw);
            if (!guid.IsPlayer())
                continue;
            if (Player* player = ObjectAccessor::FindConnectedPlayer(guid))
                list.push_back(Shown(player));
            else if (CharacterCacheEntry const* entry = sCharacterCache->GetCharacterCacheByGuid(guid))
                list.push_back(Shown(guid, entry->Race, entry->Sex, entry->Class));
        }
        Send(session, SMSG_WRATHPP_APPEARANCE, EncodeAppearances(list));
    }

    void HandlePacket(WorldSession* session, WorldPacket& packet)
    {
        std::vector<uint8_t> body(packet.size() - packet.rpos());
        if (!body.empty())
            packet.read(body.data(), body.size());
        if (!S().enabled)
            return;
        uint16 opcode = packet.GetOpcode();
        if (opcode == CMSG_WRATHPP_HELLO)
            HandleHello(session, body);
        else if (!SaidHello(session))
            SendResult(session, SetKind::PendingCreate, 0, Result::Disabled);
        else if (opcode == CMSG_WRATHPP_SET_APPEARANCE)
            HandleSet(session, body);
        else if (opcode == CMSG_WRATHPP_QUERY)
            HandleQuery(session, body);
    }

    bool LoadRegistry(std::string const& path)
    {
        std::ifstream f(path, std::ios::binary);
        std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
        Reader reader(bytes.data(), bytes.size());
        Registry registry;
        Result r = bytes.empty() ? Result::Malformed : ReadRegistry(reader, registry);
        if (r == Result::Ok)
            r = CheckRegistry(registry);
        if (r != Result::Ok)
        {
            LOG_ERROR("module", "Wrath++: the registry {} can't be used ({}): Wrath++ is off", path, ResultName(r));
            return false;
        }
        S().registry = std::move(registry);
        S().registryBytes = std::move(bytes);
        S().registryHash = RegistryHash(S().registry);
        LOG_INFO("module", "Wrath++: registry version {}, {} categories, hash {:08x}", S().registry.version,
            S().registry.categories.size(), S().registryHash);
        return true;
    }
}

class WrathppWorldScript : public WorldScript
{
public:
    WrathppWorldScript() : WorldScript("WrathppWorldScript", {WORLDHOOK_ON_AFTER_CONFIG_LOAD, WORLDHOOK_ON_STARTUP}) { }

    void OnAfterConfigLoad(bool /*reload*/) override
    {
        S().enabled = false;
        Wrathpp::SetPacketHandler(nullptr);
        if (!sConfigMgr->GetOption<bool>("Wrathpp.Enable", false))
            return;
        // The isolation guard: only the Wrath++ realm, only the Wrath++ databases.
        std::string characters = DatabaseName(sConfigMgr->GetOption<std::string>("CharacterDatabaseInfo", ""));
        std::string world = DatabaseName(sConfigMgr->GetOption<std::string>("WorldDatabaseInfo", ""));
        uint32 realmId = sConfigMgr->GetOption<uint32>("RealmID", 0);
        uint32 wanted = sConfigMgr->GetOption<uint32>("Wrathpp.RealmID", 0);
        if (!EndsWith(characters, "_wrathpp") || !EndsWith(world, "_wrathpp") || !wanted || realmId != wanted)
        {
            LOG_ERROR("module", "Wrath++: refusing to run on realm {} with databases {} / {} (only realm Wrathpp.RealmID={} with *_wrathpp databases)",
                realmId, world, characters, wanted);
            return;
        }
        std::string path = sConfigMgr->GetOption<std::string>("Wrathpp.Registry", "");
        if (path.empty())
            path = sConfigMgr->GetOption<std::string>("SourceDirectory", "") + "/modules/mod-wrathpp-customization/data/registry.bin";
        if (!LoadRegistry(path))
            return;
        S().enabled = true;
        Wrathpp::SetPacketHandler(&HandlePacket);
    }

    void OnStartup() override
    {
        if (!S().enabled)
            return;
        // Rows of characters that are gone (a creation that failed after its choices were stored).
        CharacterDatabase.DirectExecute("DELETE c FROM wrathpp_character_customization c LEFT JOIN characters ch ON ch.guid = c.guid WHERE ch.guid IS NULL");
    }
};

class WrathppServerScript : public ServerScript
{
public:
    WrathppServerScript() : ServerScript("WrathppServerScript", {SERVERHOOK_CAN_PACKET_SEND}) { }

    bool CanPacketSend(WorldSession* session, WorldPacket const& packet) override
    {
        if (S().enabled && session && packet.GetOpcode() == SMSG_CHAR_ENUM)
            SendCharacterScreen(session);
        return true;
    }
};

class WrathppAccountScript : public AccountScript
{
public:
    WrathppAccountScript() : AccountScript("WrathppAccountScript", {ACCOUNTHOOK_ON_ACCOUNT_LOGIN}) { }

    // A new connection says hello again.
    void OnAccountLogin(uint32 accountId) override
    {
        std::lock_guard<std::mutex> lock(S().mutex);
        S().sessions.erase(accountId);
    }
};

class WrathppPlayerScript : public PlayerScript
{
public:
    WrathppPlayerScript() : PlayerScript("WrathppPlayerScript", {PLAYERHOOK_ON_CREATE, PLAYERHOOK_ON_DELETE, PLAYERHOOK_ON_LOGIN, PLAYERHOOK_ON_LOAD_FROM_DB}) { }

    // Loaded, before the world sees her: her body options' display in place of her race's (InitDisplayIds).
    void OnPlayerLoadFromDB(Player* player) override
    {
        if (S().enabled)
            ApplyBody(player);
    }

    // The choices sent before CMSG_CHAR_CREATE, kept if the character is the one they were checked for.
    void OnPlayerCreate(Player* player) override
    {
        if (!S().enabled)
            return;
        WorldSession* session = player->GetSession();
        std::optional<SetAppearance> pending;
        {
            std::lock_guard<std::mutex> lock(S().mutex);
            auto it = S().sessions.find(session->GetAccountId());
            if (it == S().sessions.end() || !it->second.pendingCreate)
                return;
            pending = std::move(it->second.pendingCreate);
            it->second.pendingCreate.reset();
        }
        uint64 guid = player->GetGUID().GetRawValue();
        if (pending->race != player->getRace() || pending->sex != player->getGender() || pending->classId != player->getClass())
        {
            SendResult(session, SetKind::PendingCreate, guid, Result::CharacterMismatch);
            return;
        }
        Store(player->GetGUID().GetCounter(), pending->appearance);
        SendResult(session, SetKind::PendingCreate, guid, Result::Ok);
    }

    void OnPlayerDelete(ObjectGuid guid, uint32 /*accountId*/) override
    {
        if (!S().enabled)
            return;
        CharacterDatabase.Execute("DELETE FROM wrathpp_character_customization WHERE guid = {}", guid.GetCounter());
        std::lock_guard<std::mutex> lock(S().mutex);
        S().cache.erase(guid.GetCounter());
    }

    void OnPlayerLogin(Player* player) override
    {
        if (S().enabled)
            Broadcast(player);
    }
};

// Whether the module runs here (the Wrath++ realm, its databases, its registry): for its other scripts (WrathppUndeadStart).
bool WrathppIsEnabled()
{
    return S().enabled;
}

void AddWrathppCustomizationScripts()
{
    new WrathppWorldScript();
    new WrathppServerScript();
    new WrathppAccountScript();
    new WrathppPlayerScript();
}
