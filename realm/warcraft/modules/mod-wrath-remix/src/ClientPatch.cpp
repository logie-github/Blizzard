// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * Wrath Remix's patch for the game. The client shows a vendor's prices from its own
 * ItemExtendedCost.dbc, the currency tab from CurrencyTypes.dbc and some item icons from Item.dbc,
 * and Remix adds rows to all three (Bronze, and a price for each step of its ladder: the world
 * database's *_dbc tables, which the core reads over its DBC files). So as Wrath Remix's world
 * server starts, the module writes those three files, the server's own with the rows added, into
 * an archive in the app's client, Data/patch-Y.MPQ, which the game reads over its own; and as
 * ChromieCraft's starts, it takes the archive out again. WOW_CLIENT_DIR (ctl.sh) says where the
 * client is; without it, or without the client, nothing happens. The archive also carries the
 * game's CreatureDisplayInfo.dbc with the voices Remix gives some of its people's looks
 * (remix_display_sound: Moratari's is a death knight's otherwise), and the looks Remix adds
 * (remix_look: Moratari in an evening dress, and as she is in her tent), each one of the game's
 * with other clothes, in CreatureDisplayInfo.dbc and CreatureDisplayInfoExtra.dbc.
 *
 * The archive is an MPQ of the first format, the one the 3.3.5a client reads, its files stored as
 * Blizzard's own patches store theirs: in sectors of 4096 bytes, each compressed with zlib, after a
 * table of where each sector starts; the hash and block tables encrypted as the format has it.
 */

#include "WrathRemix.h"
#include "../../mod-skyborne/src/SkyborneFiles.h"
#include "Config.h"
#include "DatabaseEnv.h"
#include "Field.h"
#include "Log.h"
#include "QueryResult.h"
#include <algorithm>
#include <array>
#include <cctype>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <map>
#include <set>
#include <system_error>
#include <utility>
#include <vector>
#include <zlib.h>

namespace fs = std::filesystem;

namespace WrathRemix
{
    namespace
    {
        constexpr char const* PATCH = "patch-Y.MPQ";
        constexpr char const* MARK = "patch-Y.MPQ.wrath-remix";
        // The clothes of Remix's new looks (CreatureDisplayInfoExtra.dbc), in the game's language
        // folder: patch-<locale>-Y.MPQ, read after patch-Y and every HD look's patch, and before the
        // Skyborne's patch-Z (mod-skyborne), which makes its own copy of that table from the patches
        // before it, this one included (it leaves out patch-Y, which comes and goes with the realm).
        // It stays on ChromieCraft's realm too, so the Skyborne's patch isn't made again at each
        // change of realm: rows of looks only Remix's people wear.
        constexpr char const* LOOKS_MARK_SUFFIX = ".wrath-remix";

        using Bytes = std::vector<uint8>;

        // The format's table of keys.
        std::array<uint32, 0x500> const& CryptTable()
        {
            static std::array<uint32, 0x500> const table = []
            {
                std::array<uint32, 0x500> t{};
                uint32 seed = 0x00100001;
                for (uint32 i = 0; i < 0x100; ++i)
                {
                    for (uint32 j = 0, index = i; j < 5; ++j, index += 0x100)
                    {
                        seed = (seed * 125 + 3) % 0x2AAAAB;
                        uint32 high = (seed & 0xFFFF) << 16;
                        seed = (seed * 125 + 3) % 0x2AAAAB;
                        t[index] = high | (seed & 0xFFFF);
                    }
                }
                return t;
            }();
            return table;
        }

        // A file name's hash of [type]: 0 its place in the hash table, 1 and 2 its two checks, 3 a key.
        uint32 Hash(std::string const& text, uint32 type)
        {
            auto const& table = CryptTable();
            uint32 seed1 = 0x7FED7FED, seed2 = 0xEEEEEEEE;
            for (char c : text)
            {
                uint32 ch = uint32(std::toupper(static_cast<unsigned char>(c == '/' ? '\\' : c)));
                seed1 = table[type * 0x100 + ch] ^ (seed1 + seed2);
                seed2 = ch + seed1 + seed2 + (seed2 << 5) + 3;
            }
            return seed1;
        }

        void Encrypt(std::vector<uint32>& data, uint32 key)
        {
            auto const& table = CryptTable();
            uint32 seed = 0xEEEEEEEE;
            for (uint32& value : data)
            {
                seed += table[0x400 + (key & 0xFF)];
                uint32 plain = value;
                value = plain ^ (key + seed);
                key = ((~key << 0x15) + 0x11111111) | (key >> 0x0B);
                seed = plain + seed + (seed << 5) + 3;
            }
        }

        void Put32(Bytes& out, size_t at, uint32 value)
        {
            for (int i = 0; i < 4; ++i)
                out[at + i] = uint8(value >> (8 * i));
        }

        void Append32(Bytes& out, uint32 value)
        {
            for (int i = 0; i < 4; ++i)
                out.push_back(uint8(value >> (8 * i)));
        }

        uint32 Get32(Bytes const& in, size_t at)
        {
            return uint32(in[at]) | uint32(in[at + 1]) << 8 | uint32(in[at + 2]) << 16 | uint32(in[at + 3]) << 24;
        }

        constexpr uint32 SECTOR = 4096;                 // 512 << 3, the header's sector size
        constexpr uint32 MPQ_FILE_COMPRESS = 0x00000200;
        constexpr uint32 MPQ_FILE_EXISTS = 0x80000000;

        // A file as the archive stores it: the sectors' offset table, then each sector zlib-compressed
        // (a byte saying zlib, then the stream) or, when that saves nothing, as it is.
        Bytes Stored(Bytes const& data)
        {
            uint32 sectors = std::max<uint32>(1, uint32((data.size() + SECTOR - 1) / SECTOR));
            Bytes out(size_t(sectors + 1) * 4, 0);
            std::vector<uint32> offsets{ uint32(out.size()) };
            for (uint32 i = 0; i < sectors; ++i)
            {
                size_t from = size_t(i) * SECTOR, length = std::min<size_t>(SECTOR, data.size() - from);
                uLongf size = compressBound(uLong(length));
                Bytes packed(size);
                if (compress2(packed.data(), &size, data.data() + from, uLong(length), 9) == Z_OK && size + 1 < length)
                {
                    out.push_back(0x02);                // MPQ_COMPRESSION_ZLIB
                    out.insert(out.end(), packed.begin(), packed.begin() + size);
                }
                else
                    out.insert(out.end(), data.begin() + from, data.begin() + from + length);
                offsets.push_back(uint32(out.size()));
            }
            for (size_t i = 0; i < offsets.size(); ++i)
                Put32(out, i * 4, offsets[i]);
            return out;
        }

        Bytes Archive(std::vector<std::pair<std::string, Bytes>> const& files)
        {
            uint32 hashSize = 16;
            while (hashSize < files.size() * 2)
                hashSize *= 2;

            Bytes out(32, 0);
            std::vector<uint32> blocks;
            for (auto const& [name, data] : files)
            {
                Bytes stored = Stored(data);
                blocks.push_back(uint32(out.size()));   // where it starts
                blocks.push_back(uint32(stored.size())); // stored size
                blocks.push_back(uint32(data.size()));  // size
                blocks.push_back(MPQ_FILE_EXISTS | MPQ_FILE_COMPRESS);
                out.insert(out.end(), stored.begin(), stored.end());
            }

            std::vector<uint32> hashes(hashSize * 4, 0xFFFFFFFF);
            for (uint32 i = 0; i < files.size(); ++i)
            {
                std::string const& name = files[i].first;
                uint32 index = Hash(name, 0) & (hashSize - 1);
                while (hashes[index * 4 + 3] != 0xFFFFFFFF)
                    index = (index + 1) & (hashSize - 1);
                hashes[index * 4 + 0] = Hash(name, 1);
                hashes[index * 4 + 1] = Hash(name, 2);
                hashes[index * 4 + 2] = 0;               // locale 0 (neutral), platform 0
                hashes[index * 4 + 3] = i;
            }
            Encrypt(hashes, Hash("(hash table)", 3));
            Encrypt(blocks, Hash("(block table)", 3));

            uint32 hashPos = uint32(out.size());
            for (uint32 value : hashes)
                Append32(out, value);
            uint32 blockPos = uint32(out.size());
            for (uint32 value : blocks)
                Append32(out, value);

            std::memcpy(out.data(), "MPQ\x1A", 4);
            Put32(out, 4, 32);                          // header size
            Put32(out, 8, uint32(out.size()));          // archive size
            out[12] = 0; out[13] = 0;                   // format 0
            out[14] = 3; out[15] = 0;                   // sectors of 4096 bytes
            Put32(out, 16, hashPos);
            Put32(out, 20, blockPos);
            Put32(out, 24, hashSize);
            Put32(out, 28, uint32(files.size()));
            return out;
        }

        Bytes Read(fs::path const& path)
        {
            std::ifstream in(path, std::ios::binary);
            return Bytes(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
        }

        // [base], a DBC file of [fields] whole-number fields, with [rows] in (a row with an id
        // already there in its place). Empty when [base] isn't such a file.
        Bytes WithRows(Bytes const& base, uint32 fields, std::vector<std::vector<int32>> const& rows)
        {
            if (base.size() < 20 || std::memcmp(base.data(), "WDBC", 4) != 0)
                return {};
            uint32 count = Get32(base, 4), fieldCount = Get32(base, 8), size = Get32(base, 12), strings = Get32(base, 16);
            if (fieldCount != fields || size != fields * 4 || base.size() < 20 + size_t(count) * size + strings)
                return {};
            std::set<uint32> ids;
            for (auto const& row : rows)
                ids.insert(uint32(row[0]));

            Bytes out(base.begin(), base.begin() + 20);
            uint32 kept = 0;
            for (uint32 i = 0; i < count; ++i)
            {
                size_t at = 20 + size_t(i) * size;
                if (ids.count(Get32(base, at)))
                    continue;
                out.insert(out.end(), base.begin() + at, base.begin() + at + size);
                ++kept;
            }
            for (auto const& row : rows)
                for (int32 value : row)
                    Append32(out, uint32(value));
            Put32(out, 4, kept + uint32(rows.size()));
            size_t stringsAt = 20 + size_t(count) * size;
            out.insert(out.end(), base.begin() + stringsAt, base.begin() + stringsAt + strings);
            return out;
        }

        // [base], a DBC file of [fields] whole-number fields, with the field at [field] of the rows
        // [values] names (by id) set to its value. Empty when [base] isn't such a file.
        Bytes WithValues(Bytes const& base, uint32 fields, uint32 field, std::map<uint32, uint32> const& values)
        {
            if (base.size() < 20 || std::memcmp(base.data(), "WDBC", 4) != 0 || field >= fields)
                return {};
            uint32 count = Get32(base, 4), fieldCount = Get32(base, 8), size = Get32(base, 12), strings = Get32(base, 16);
            if (fieldCount != fields || size != fields * 4 || base.size() < 20 + size_t(count) * size + strings)
                return {};
            Bytes out = base;
            for (uint32 i = 0; i < count; ++i)
            {
                size_t at = 20 + size_t(i) * size;
                if (auto it = values.find(Get32(base, at)); it != values.end())
                    Put32(out, at + field * 4, it->second);
            }
            return out;
        }

        // The row of [base] (a DBC file of [fields] whole-number fields) with that id, or none.
        std::vector<int32> RowOf(Bytes const& base, uint32 fields, uint32 id)
        {
            if (base.size() < 20 || std::memcmp(base.data(), "WDBC", 4) != 0 || Get32(base, 8) != fields)
                return {};
            uint32 count = Get32(base, 4), size = Get32(base, 12);
            for (uint32 i = 0; i < count; ++i)
            {
                size_t at = 20 + size_t(i) * size;
                if (base.size() < at + size)
                    break;
                if (Get32(base, at) != id)
                    continue;
                std::vector<int32> row;
                for (uint32 f = 0; f < fields; ++f)
                    row.push_back(int32(Get32(base, at + f * 4)));
                return row;
            }
            return {};
        }

        // [base] (a DBC file of [fields] fields) with [texts] added to its strings, their offsets in
        // [at]: for rows of its with text, put in after with WithRows. Empty when [base] isn't such a file.
        Bytes WithStrings(Bytes const& base, uint32 fields, std::vector<std::string> const& texts, std::vector<int32>& at)
        {
            if (base.size() < 20 || std::memcmp(base.data(), "WDBC", 4) != 0)
                return {};
            uint32 count = Get32(base, 4), size = Get32(base, 12), strings = Get32(base, 16);
            size_t stringsAt = 20 + size_t(count) * size;
            if (Get32(base, 8) != fields || size != fields * 4 || base.size() < stringsAt + strings)
                return {};
            Bytes grown(base.begin(), base.begin() + stringsAt + strings);
            for (std::string const& text : texts)
            {
                at.push_back(int32(grown.size() - stringsAt));
                grown.insert(grown.end(), text.begin(), text.end());
                grown.push_back(0);
            }
            Put32(grown, 16, uint32(grown.size() - stringsAt));
            return grown;
        }

        // A sound: a SoundEntries row of one file in a folder (the game's own spoken lines' kind).
        struct Sound { uint32 id; std::string name, file, folder; };

        // [base], SoundEntries.dbc (30 fields; the name, the ten files and the folder are strings),
        // with [sounds] in (a row with an id already there in its place), their strings added to
        // the file's. Empty when [base] isn't that file.
        Bytes WithSounds(Bytes const& base, std::vector<Sound> const& sounds)
        {
            constexpr uint32 FIELDS = 30;
            if (base.size() < 20 || std::memcmp(base.data(), "WDBC", 4) != 0)
                return {};
            uint32 count = Get32(base, 4), size = Get32(base, 12), strings = Get32(base, 16);
            size_t stringsAt = 20 + size_t(count) * size;
            if (Get32(base, 8) != FIELDS || size != FIELDS * 4 || base.size() < stringsAt + strings)
                return {};
            Bytes grown(base.begin(), base.begin() + stringsAt + strings);
            auto add = [&grown, stringsAt](std::string const& text)
            {
                int32 at = int32(grown.size() - stringsAt);
                grown.insert(grown.end(), text.begin(), text.end());
                grown.push_back(0);
                return at;
            };
            std::vector<std::vector<int32>> rows;
            for (Sound const& sound : sounds)
            {
                std::vector<int32> row(FIELDS, 0);
                float const volume = 1.0f, near = 15.0f, far = 60.0f;
                row[0] = int32(sound.id);
                row[1] = 10;                                // a scripted line, as Tirion's at the Lich King
                row[2] = add(sound.name);
                row[3] = add(sound.file);                   // the first of ten files; its frequency:
                row[13] = 1;
                row[23] = add(sound.folder);
                std::memcpy(&row[24], &volume, 4);
                std::memcpy(&row[26], &near, 4);
                std::memcpy(&row[27], &far, 4);
                rows.push_back(std::move(row));
            }
            Put32(grown, 16, uint32(grown.size() - stringsAt));
            return WithRows(grown, FIELDS, rows);
        }

        std::vector<std::vector<int32>> Rows(std::string const& sql, uint32 fields)
        {
            std::vector<std::vector<int32>> rows;
            if (QueryResult result = WorldDatabase.Query(sql))
            {
                do
                {
                    Field* f = result->Fetch();
                    std::vector<int32> row;
                    for (uint32 i = 0; i < fields; ++i)
                        row.push_back(int32(f[i].Get<int64>()));
                    rows.push_back(std::move(row));
                } while (result->NextRow());
            }
            return rows;
        }

        // A table's columns as whole numbers, in the DBC file's order.
        std::string Select(std::vector<char const*> const& columns, char const* table)
        {
            std::string sql = "SELECT ";
            for (size_t i = 0; i < columns.size(); ++i)
                sql += std::string(i ? ", " : "") + "CAST(`" + columns[i] + "` AS SIGNED)";
            return sql + " FROM `" + table + "` ORDER BY 1";
        }

        bool WriteIfChanged(fs::path const& path, Bytes const& data)
        {
            if (fs::exists(path) && Read(path) == data)
                return false;
            fs::path part = path;
            part += ".part";
            {
                std::ofstream out(part, std::ios::binary | std::ios::trunc);
                out.write(reinterpret_cast<char const*>(data.data()), std::streamsize(data.size()));
            }
            std::error_code error;
            fs::rename(part, path, error);
            if (error)
            {
                LOG_ERROR("module", "Wrath Remix: couldn't write {}: {}", path.string(), error.message());
                fs::remove(part, error);
                return false;
            }
            return true;
        }
    }

    // The game's language folder (Data/enUS...: the one with its locale-xxXX.MPQ), if it has one.
    static fs::path LocaleFolder(fs::path const& data)
    {
        std::error_code error;
        for (auto const& entry : fs::directory_iterator(data, error))
        {
            std::string name = entry.path().filename().string();
            if (name.size() == 4 && entry.is_directory(error) && fs::exists(entry.path() / ("locale-" + name + ".MPQ"), error))
                return entry.path();
        }
        return {};
    }

    // Writes (or, with no tables, takes out) the tables the Skyborne's patch must take in with the
    // game's (it's made from the patches before it but patch-Y): the clothes of Remix's new looks and
    // Moratari's voice's sounds; false when there's no language folder to put them in.
    static bool UpdateLooksPatch(fs::path const& data, std::vector<std::pair<std::string, Bytes>> const& tables)
    {
        fs::path locale = LocaleFolder(data);
        if (locale.empty())
            return false;
        fs::path looks = locale / ("patch-" + locale.filename().string() + "-Y.MPQ"), mark = looks;
        mark += LOOKS_MARK_SUFFIX;
        std::error_code error;
        bool ours = fs::exists(mark, error);
        if (!ours && fs::exists(looks, error))
        {
            LOG_WARN("module", "Wrath Remix: {} isn't Wrath Remix's; left alone, so Remix's new looks have no clothes", looks.string());
            return true;
        }
        if (tables.empty())
        {
            if (ours)
            {
                fs::remove(looks, error);
                fs::remove(mark, error);
            }
            return true;
        }
        std::vector<std::pair<std::string, Bytes>> files = tables;
        std::string list;
        for (auto const& [name, table] : tables)
            list += name + "\r\n";
        files.emplace_back("(listfile)", Bytes(list.begin(), list.end()));
        std::string const note = "Wrath Remix's new looks' clothes and Moratari's voice's sounds for the game: its world server writes this as it "
            "starts; it stays for ChromieCraft's realm too (rows only Remix's people use).\n";
        WriteIfChanged(mark, Bytes(note.begin(), note.end()));
        if (WriteIfChanged(looks, Archive(files)))
            LOG_INFO("module", "Wrath Remix: its looks' clothes and voice's sounds written ({})", looks.string());
        return true;
    }

    void UpdateClientPatch()
    {
        char const* client = std::getenv("WOW_CLIENT_DIR");
        if (!client || !*client)
            return;
        fs::path data = fs::path(client) / "Data";
        std::error_code error;
        if (!fs::is_directory(data, error))
            return;
        fs::path patch = data / PATCH, mark = data / MARK;
        bool ours = fs::exists(mark, error);

        if (!Active())
        {
            // ChromieCraft: the game as it is, its language folder's patch out too (made from the
            // game's tables as Remix last started, it was read over the allied races' patch and hid
            // their sounds, its SoundEntries the server's own; taken out here, before the Skyborne's
            // patch is made from the game's tables).
            if (ours)
            {
                fs::remove(patch, error);
                fs::remove(mark, error);
                LOG_INFO("module", "Wrath Remix: its patch is out of the game ({})", patch.string());
            }
            UpdateLooksPatch(data, {});
            return;
        }
        if (!ours && fs::exists(patch, error))
        {
            LOG_WARN("module", "Wrath Remix: {} isn't Wrath Remix's; left alone, so the game won't show Bronze's prices", patch.string());
            return;
        }

        fs::path dbc = fs::path(sConfigMgr->GetOption<std::string>("DataDir", "./")) / "dbc";
        // The looks' and models' tables as the game has them (its own, the HD looks' patches and
        // the other modules' in: mod-allied-races' patch-V.MPQ adds the void elves' and the
        // nightborne's looks and models), so this patch, read after them, carries their rows too;
        // the server's file where the game hasn't one.
        Skyborne::Game clientGame(data, { "patch-y.mpq", "patch-z.mpq" });
        auto clientTable = [&](char const* name) -> Bytes
        {
            Bytes table;
            if (clientGame.Read(std::string("DBFilesClient\\") + name, table) && !table.empty())
                return table;
            return Read(dbc / name);
        };
        struct File { char const* name; char const* table; std::vector<char const*> columns; };
        std::vector<File> const tables = {
            { "Item.dbc", "item_dbc", { "ID", "ClassID", "SubclassID", "Sound_Override_Subclassid", "Material",
                                        "DisplayInfoID", "InventoryType", "SheatheType" } },
            { "ItemExtendedCost.dbc", "itemextendedcost_dbc", { "ID", "HonorPoints", "ArenaPoints", "ArenaBracket",
                "ItemID_1", "ItemID_2", "ItemID_3", "ItemID_4", "ItemID_5", "ItemCount_1", "ItemCount_2", "ItemCount_3",
                "ItemCount_4", "ItemCount_5", "RequiredArenaRating", "ItemPurchaseGroup" } },
            { "CurrencyTypes.dbc", "currencytypes_dbc", { "ID", "ItemID", "CategoryID", "BitIndex" } },
        };

        std::vector<std::pair<std::string, Bytes>> files;
        std::string list;
        for (File const& file : tables)
        {
            Bytes base = Read(dbc / file.name);
            Bytes patched = WithRows(base, uint32(file.columns.size()), Rows(Select(file.columns, file.table), uint32(file.columns.size())));
            if (patched.empty())
            {
                LOG_ERROR("module", "Wrath Remix: {} isn't the DBC file it expects; the game's patch isn't written", (dbc / file.name).string());
                return;
            }
            std::string name = std::string("DBFilesClient\\") + file.name;
            files.emplace_back(name, std::move(patched));
            list += name + "\r\n";
        }
        // The voices some of Remix's people speak with as they're clicked on (remix_display_sound):
        // CreatureDisplayInfo.dbc's NPCSoundID, field 12 of 16, for their looks.
        std::map<uint32, uint32> voices;
        if (QueryResult result = WorldDatabase.Query("SELECT `display`, `npc_sound` FROM `remix_display_sound`"))
        {
            do
            {
                Field* f = result->Fetch();
                voices[f[0].Get<uint32>()] = f[1].Get<uint32>();
            } while (result->NextRow());
        }
        // The looks Remix adds (remix_look): a CreatureDisplayInfoExtra row (21 fields) copied from one
        // of the game's with its clothes (fields 8 to 18) changed, and without its baked texture (field
        // 20, the name's offset: 0 is the empty name), so the game dresses the look from those; and a
        // CreatureDisplayInfo row (16 fields) copied from the game's look, with that extra (field 3).
        Bytes const displayBase = clientTable("CreatureDisplayInfo.dbc"), extraBase = clientTable("CreatureDisplayInfoExtra.dbc");
        std::vector<std::vector<int32>> looks, lookExtras;
        if (QueryResult result = WorldDatabase.Query("SELECT `display`, `from_display`, `extra`, `from_extra`, `bake`, `item1`, `item2`, `item3`, `item4`, `item5`, "
                                                     "`item6`, `item7`, `item8`, `item9`, `item10`, `item11` FROM `remix_look` ORDER BY `display`"))
        {
            do
            {
                Field* f = result->Fetch();
                std::vector<int32> look = RowOf(displayBase, 16, f[1].Get<uint32>()), extra = RowOf(extraBase, 21, f[3].Get<uint32>());
                if (look.empty() || extra.empty())
                {
                    LOG_ERROR("module", "Wrath Remix: look {} is copied from a look ({}) or clothes ({}) the game hasn't", f[0].Get<uint32>(), f[1].Get<uint32>(), f[3].Get<uint32>());
                    continue;
                }
                look[0] = int32(f[0].Get<uint32>());
                look[3] = int32(f[2].Get<uint32>());
                extra[0] = int32(f[2].Get<uint32>());
                for (uint32 i = 0; i < 11; ++i)
                    extra[8 + i] = int32(f[5 + i].Get<uint32>());
                if (!f[4].Get<uint8>())
                    extra[20] = 0;
                looks.push_back(std::move(look));
                lookExtras.push_back(std::move(extra));
            } while (result->NextRow());
        }
        // Eternus's own shape (RemixModels.cpp, tools/models.py): her model's files from the module's
        // data/models; a CreatureModelData row (28 fields, the model's name the third) copied from
        // the game's dragon's (Creature\Dragon\Dragon.mdx, her size), with her model and its bounds;
        // and her look's CreatureDisplayInfo row (copied from that dragon's look), her skin both of
        // its textures, at scale 1 (each of her parts has its own).
        std::vector<std::string> const& shape = EternusShapeFiles();
        Bytes modelData;
        std::vector<int32> dragonLook;
        std::vector<std::pair<std::string, Bytes>> shapeFiles;
        if (!shape.empty())
        {
            constexpr uint32 GAME_DRAGON_MODEL = 2723, GAME_DRAGON_LOOK = 23746;
            constexpr float BOUNDS[6] = { -19.34f, -9.86f, -0.55f, 10.24f, 9.66f, 13.43f };   // her model's, standing (the newer games')
            Bytes const modelBase = clientTable("CreatureModelData.dbc");
            std::vector<int32> model = RowOf(modelBase, 28, GAME_DRAGON_MODEL), at;
            dragonLook = RowOf(displayBase, 16, GAME_DRAGON_LOOK);
            Bytes grown = model.empty() ? Bytes() : WithStrings(modelBase, 28, { "Creature\\Eternus\\Eternus.mdx" }, at);
            if (!grown.empty() && !dragonLook.empty())
            {
                model[0] = int32(MODEL_ETERNUS_DRAGON);
                model[2] = at[0];
                std::memcpy(&model[17], BOUNDS, sizeof(BOUNDS));
                modelData = WithRows(grown, 28, { model });
            }
            for (std::string const& file : shape)
            {
                Bytes data = Read(fs::path(ModelsFolder()) / file);
                std::string name = file;
                std::replace(name.begin(), name.end(), '/', '\\');
                if (data.empty())
                {
                    modelData.clear();
                    break;
                }
                shapeFiles.emplace_back(name, std::move(data));
            }
            if (modelData.empty())
            {
                LOG_ERROR("module", "Wrath Remix: {} or her files aren't what it expects; Eternus keeps the dragonspawn's shape",
                    (dbc / "CreatureModelData.dbc").string());
                dragonLook.clear();
            }
        }
        // (the tables the Skyborne's patch takes in: in their own patch, read after it makes its copy;
        // in patch-Y if the game has no language folder)
        std::vector<std::pair<std::string, Bytes>> localeTables;
        bool dragon = false;
        if (!voices.empty() || !looks.empty() || !dragonLook.empty())
        {
            Bytes patched = voices.empty() ? displayBase : WithValues(displayBase, 16, 12, voices);
            if (!patched.empty() && !dragonLook.empty())
            {
                std::vector<int32> at;
                patched = WithStrings(patched, 16, { "EternusSkin" }, at);
                if (!patched.empty())
                {
                    float const scale = 1.0f;
                    dragonLook[0] = int32(DISPLAY_ETERNUS_DRAGON);
                    dragonLook[1] = int32(MODEL_ETERNUS_DRAGON);
                    dragonLook[3] = 0;                          // no extra: a creature's look
                    std::memcpy(&dragonLook[4], &scale, 4);
                    dragonLook[5] = 255;
                    dragonLook[6] = dragonLook[7] = at[0];
                    dragonLook[8] = dragonLook[9] = 0;
                    dragonLook[12] = dragonLook[13] = dragonLook[14] = dragonLook[15] = 0;
                    looks.push_back(dragonLook);
                    dragon = true;
                }
            }
            if (!patched.empty() && !looks.empty())
                patched = WithRows(patched, 16, looks);
            if (patched.empty())
                LOG_ERROR("module", "Wrath Remix: {} isn't the DBC file it expects; Remix's people keep the game's voices and looks",
                    (dbc / "CreatureDisplayInfo.dbc").string());
            else
            {
                std::string name = "DBFilesClient\\CreatureDisplayInfo.dbc";
                files.emplace_back(name, std::move(patched));
                list += name + "\r\n";
                if (dragon)
                {
                    files.emplace_back("DBFilesClient\\CreatureModelData.dbc", std::move(modelData));
                    list += "DBFilesClient\\CreatureModelData.dbc\r\n";
                    for (auto& [path, file] : shapeFiles)
                    {
                        list += path + "\r\n";
                        files.emplace_back(path, std::move(file));
                    }
                    EternusShapeInPatch();
                    LOG_INFO("module", "Wrath Remix: Eternus's own shape in the game's patch ({} files)", shapeFiles.size());
                }
                if (!lookExtras.empty())
                {
                    Bytes extras = WithRows(extraBase, 21, lookExtras);
                    if (extras.empty())
                        LOG_ERROR("module", "Wrath Remix: {} isn't the DBC file it expects; Remix's new looks have no clothes",
                            (dbc / "CreatureDisplayInfoExtra.dbc").string());
                    else
                        localeTables.emplace_back("DBFilesClient\\CreatureDisplayInfoExtra.dbc", std::move(extras));
                }
            }
        }
        // Moratari's own voice (remix_voice, tools/voices.py): each line a SoundEntries row and its
        // WAV, from the module's data/voices, where the server package fetches them (the game's
        // files are never in the repository). Without them, she speaks in text alone.
        std::vector<Sound> sounds;
        std::vector<std::pair<std::string, Bytes>> wavs;
        fs::path const voiceFolder = VoicesFolder();
        std::string const soundFolder = "Sound\\Creature\\Moratari";
        if (QueryResult result = WorldDatabase.Query("SELECT `sound`, `number`, `file` FROM `remix_voice` ORDER BY `sound`"))
        {
            do
            {
                Field* f = result->Fetch();
                std::string const file = f[2].Get<std::string>();
                Bytes wav = Read(voiceFolder / file);
                if (wav.size() <= 44)
                    continue;
                sounds.push_back({ f[0].Get<uint32>(), Acore::StringFormat("RemixMoratari{:02}", f[1].Get<uint32>()), file, soundFolder });
                wavs.emplace_back(soundFolder + "\\" + file, std::move(wav));
            } while (result->NextRow());
        }
        if (!sounds.empty())
        {
            // (onto the game's table, the HD looks' sounds and the other modules' in: the server's own,
            // read over theirs, took them away)
            Bytes patched = WithSounds(clientTable("SoundEntries.dbc"), sounds);
            if (patched.empty())
                LOG_ERROR("module", "Wrath Remix: {} isn't the DBC file it expects; Moratari speaks without her voice",
                    (dbc / "SoundEntries.dbc").string());
            else
            {
                localeTables.emplace_back("DBFilesClient\\SoundEntries.dbc", std::move(patched));
                for (auto& [path, wav] : wavs)
                {
                    list += path + "\r\n";
                    files.emplace_back(path, std::move(wav));
                }
            }
        }
        if (!UpdateLooksPatch(data, localeTables))
            for (auto& [name, table] : localeTables)
            {
                list += name + "\r\n";
                files.emplace_back(name, std::move(table));
            }
        files.emplace_back("(listfile)", Bytes(list.begin(), list.end()));

        std::string const note = "Wrath Remix's patch for the game (Bronze and its prices, its people's voices and looks): its world server writes " +
            std::string(PATCH) + " as it starts, and ChromieCraft's takes it out.\n";
        WriteIfChanged(mark, Bytes(note.begin(), note.end()));
        if (WriteIfChanged(patch, Archive(files)))
            LOG_INFO("module", "Wrath Remix: the game's patch written ({})", patch.string());
        else
            LOG_INFO("module", "Wrath Remix: the game's patch is up to date ({})", patch.string());
    }
}
