// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The game's files, for the Skyborne's patch (SkyborneClient.cpp): reading the client's archives
 * (MPQ files of the 3.3.5a format, and folders the game reads like one), its tables (DBC files)
 * and textures (BLP2), and writing an archive. Nothing here needs the server, so the module's
 * test (tools/test_client.cpp) builds it on its own.
 */

#ifndef MOD_SKYBORNE_FILES_H
#define MOD_SKYBORNE_FILES_H

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace Skyborne
{
    using Bytes = std::vector<uint8_t>;
    namespace fs = std::filesystem;

    // One of the game's archives: an MPQ file, or a folder of the game's paths.
    class Archive
    {
    public:
        virtual ~Archive() = default;
        // The file at [name] (the game's path, backslashes, any case) into [out].
        virtual bool Read(std::string const& name, Bytes& out) = 0;
        // Whether it has a file at [name] (without reading it).
        virtual bool Has(std::string const& name) = 0;
        fs::path path;
    };

    std::unique_ptr<Archive> OpenArchive(fs::path const& path);

    // The client's archives, in the order the game reads them (a later one's file wins): the game's
    // own, its language's, and the patches after them (patch-4.MPQ to patch-Z.MPQ, files or
    // folders). [skip]: the names (lower case) left out (the Skyborne's own patch).
    class Game
    {
    public:
        Game(fs::path const& data, std::vector<std::string> const& skip);
        bool Read(std::string const& name, Bytes& out) const;
        bool Has(std::string const& name) const;
        std::string locale;                 // enUS...
        std::vector<std::unique_ptr<Archive>> archives;
        // What the archives are (names, sizes, times), to know when the patch is to be made again.
        std::string Describe() const;
    };

    // Writes an MPQ file of the format the 3.3.5a client reads, a file at a time.
    class MpqWriter
    {
    public:
        explicit MpqWriter(fs::path const& path);
        bool Add(std::string const& name, Bytes const& data);
        // Another name for a file already added (its bytes stored once): false if there's none of [existing].
        bool AddSame(std::string const& name, std::string const& existing);
        bool Finish();
        bool ok() const { return _ok; }
    private:
        std::ofstream _out;
        std::vector<std::pair<std::string, std::vector<uint32_t>>> _blocks; // name, block entry
        std::vector<std::pair<std::string, uint32_t>> _same;                 // name, block
        uint64_t _pos = 32;
        bool _ok = true;
    };

    // A DBC table, to change.
    struct Dbc
    {
        uint32_t fields = 0, size = 0;
        std::vector<Bytes> records;
        Bytes strings;
        std::map<std::string, uint32_t> stringAt;

        bool Parse(Bytes const& data);
        Bytes Write() const;
        uint32_t String(std::string const& text);
        uint32_t Get(size_t row, uint32_t field) const;
        void Set(size_t row, uint32_t field, uint32_t value);
    };

    // A character table's rows in the order the game reads them: CharSections by race, sex, section,
    // variation and colour; CharHairGeosets and CharacterFacialHairStyles by race, sex and variation.
    // The game builds its look-up from runs of rows (CharSections: each race, sex and section's run
    // sizes its variations, each variation's run its colours), so a group split across the table (rows
    // added at its end) left the earlier runs' rows outside the arrays, and the character creation
    // screen read a missing row and crashed (crash reports #34, #44, #45, #47, #54: ERROR #132 at
    // 0x004EA77F, the underwear row of the preview's skin). Equal keys keep their order. Other tables
    // are left as they are.
    void SortCharacterTable(Dbc& dbc, std::string const& name);

    // The changes in a table's file (data/client/dbc/<Table>.txt, tools/build_data.py): "put" a row
    // (in place of the one with its id, or added), "putraw"/"appendraw" a record as bytes, "or" or
    // "set" a field of the row with an id, "copyrow" the client's own row to a free id, "remapfield"
    // a value of a field in every row that has it (a creature race moved out of a player race's
    // place, in the client's own rows whatever their ids). Says what went wrong, or nothing.
    std::string ApplyChanges(Dbc& dbc, std::string const& changes);

    // How a texture's colours change (data/client/textures.txt): a skin's (a blue), a face's eyes,
    // hair, or every colour's saturation turned down (the Dark Ranger's grey: saturation is the
    // part kept).
    struct Recipe
    {
        enum Kind { SKIN, EYES, HAIR, GREY } kind;
        double hue = 0, saturation = 0, lightness = 1;          // the skin's or hair's new colour
        double eyeHue = -1, eyeSaturation = 0, eyeLightness = 1; // the eyes' (-1: as they are)
    };
    bool ParseRecipe(std::string const& op, std::string const& params, Recipe& recipe);

    // [blp] with its colours changed (a palette's colours, compressed blocks' end colours, or each
    // pixel), in the same format and size. False when it isn't a texture this knows.
    bool Recolor(Bytes& blp, Recipe const& recipe);

    // The race icons (UI-CharacterCreate-Races and -RacesRound, 8 icons a row: Alliance men, Horde
    // men, Alliance women, Horde women), with the blood elf's (column 5) made a Skyborne (blue skin,
    // white hair, blue eyes) in column 7 of every row, as DXT5. False when [blp] isn't
    // such a texture.
    bool SkyborneIcons(Bytes& blp);

    // Decoding and encoding (for the icons, and the tests).
    struct Image
    {
        uint32_t width = 0, height = 0;
        std::vector<uint8_t> rgba;
    };
    bool Decode(Bytes const& blp, Image& image);
    Bytes EncodeDxt5(Image const& image);
}

#endif
