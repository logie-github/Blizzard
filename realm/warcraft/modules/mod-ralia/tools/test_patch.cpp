// SPDX-License-Identifier: GPL-3.0-or-later
// The character textures' patch (Ralia's mod, Alternate Female Options) made from a stand-in game and
// stand-in files (no game needed), and the Skyborne's patch made after it:
//
//   g++ -std=c++17 -O2 tools/test_patch.cpp src/RaliaPatch.cpp src/RaliaImage.cpp \
//     ../mod-skyborne/src/SkyborneFiles.cpp ../mod-skyborne/src/SkybornePatch.cpp -lz
//   ./a.out [SKYBORNE_DATA]          (mod-skyborne's data/client; ../mod-skyborne/data/client)
//
// The game: a CharSections with skins and pelvis and torso textures of several races, the textures
// palettized as the game's are; a patch-Z (the Skyborne's) with a CharSections of its own, which the
// patch is made without. Ralia's files: today's (twice as wide as high, DXT) for some of them. Checked:
// a texture with Ralia's file takes its body half at the game's size, palettized; a colour without
// one takes its nearest colour's change and keeps its own colour (and a tattoo, through sources.txt's
// "="); one whose nearest file is another picture is left out; sources.txt's named file is used for
// a colour numbered otherwise; male and female gnome textures are included; the patch isn't made again
// unchanged; it's taken out with no files, and one that isn't the module's is left alone. Where a set has
// a texture as the older models' and the newer's ("_hd"), the one nearer the game's picture is used;
// Alternate Female Options takes the women's alone, and leaves the gnomes as they are. The Skyborne's
// patch, made after it, makes the Skyborne's skins and the blood elves' Dark Ranger skin from the set's
// blood elf skin.

#include "../src/RaliaImage.h"
#include "../src/RaliaPatch.h"
#include "../../mod-skyborne/src/SkybornePatch.h"

#include <cmath>
#include <fstream>
#include <functional>
#include <iostream>
#include <thread>

using namespace Ralia;
using Skyborne::Dbc;

static int failures = 0;

static void Check(bool ok, std::string const& what)
{
    std::cout << (ok ? "ok   " : "FAIL ") << what << "\n";
    if (!ok)
        ++failures;
}

struct Rgb { int r, g, b; };

static Image Make(uint32_t w, uint32_t h, std::function<Rgb(uint32_t, uint32_t)> const& colour, uint8_t alpha = 255)
{
    Image image;
    image.width = w;
    image.height = h;
    image.rgba.resize(size_t(w) * h * 4);
    for (uint32_t y = 0; y < h; ++y)
        for (uint32_t x = 0; x < w; ++x)
        {
            Rgb c = colour(x, y);
            uint8_t* p = &image.rgba[(size_t(y) * w + x) * 4];
            p[0] = uint8_t(c.r); p[1] = uint8_t(c.g); p[2] = uint8_t(c.b); p[3] = alpha;
        }
    return image;
}

static Image Flat(uint32_t w, uint32_t h, Rgb c, uint8_t alpha = 255)
{
    return Make(w, h, [c](uint32_t, uint32_t) { return c; }, alpha);
}

static void Write(fs::path const& path, Bytes const& data)
{
    fs::create_directories(path.parent_path());
    std::ofstream out(path, std::ios::binary);
    out.write(reinterpret_cast<char const*>(data.data()), std::streamsize(data.size()));
}

static void WriteText(fs::path const& path, std::string const& text)
{
    fs::create_directories(path.parent_path());
    std::ofstream(path, std::ios::binary) << text;
}

static fs::path Local(fs::path const& root, std::string game)
{
    for (char& c : game)
        if (c == '\\')
            c = '/';
    return root / game;
}

// A game texture: palettized, as 3.3.5's are.
static void GameTexture(fs::path const& archive, std::string const& path, Image const& image, bool alpha = false)
{
    Write(Local(archive, path), EncodePalette(image, alpha));
}

// One of Ralia's: today's, DXT.
static void RaliaTexture(fs::path const& files, std::string const& path, Image const& image)
{
    Write(files / path, Skyborne::EncodeDxt5(image));
}

static Dbc Sections()
{
    Dbc dbc;
    dbc.fields = 10;
    dbc.size = 40;
    dbc.strings = { 0 };
    return dbc;
}

static void Row(Dbc& dbc, uint32_t id, uint32_t race, uint32_t sex, uint32_t section, std::string const& t0, std::string const& t1, uint32_t colour)
{
    Bytes record(dbc.size, 0);
    dbc.records.push_back(record);
    size_t row = dbc.records.size() - 1;
    dbc.Set(row, 0, id);
    dbc.Set(row, 1, race);
    dbc.Set(row, 2, sex);
    dbc.Set(row, 3, section);
    dbc.Set(row, 4, dbc.String(t0));
    dbc.Set(row, 5, dbc.String(t1));
    dbc.Set(row, 7, 17);
    dbc.Set(row, 9, colour);
}

static bool Near(Image const& image, uint32_t x, uint32_t y, Rgb c, int tolerance)
{
    if (x >= image.width || y >= image.height)
        return false;
    uint8_t const* p = &image.rgba[(size_t(y) * image.width + x) * 4];
    return std::abs(p[0] - c.r) <= tolerance && std::abs(p[1] - c.g) <= tolerance && std::abs(p[2] - c.b) <= tolerance;
}

static std::string Show(Image const& image, uint32_t x, uint32_t y)
{
    if (x >= image.width || y >= image.height)
        return "(none)";
    uint8_t const* p = &image.rgba[(size_t(y) * image.width + x) * 4];
    return "(" + std::to_string(p[0]) + "," + std::to_string(p[1]) + "," + std::to_string(p[2]) + "," + std::to_string(p[3]) + ")";
}

int main(int argc, char** argv)
{
    fs::path skyborneData = argc > 1 ? fs::path(argv[1]) : fs::path("../mod-skyborne/data/client");
    Set const ralia { "Ralia's mod", false, {} }, alternate { "Alternate Female Options", true, { "character\\gnome\\" } };
    fs::path root = fs::temp_directory_path() / "ralia-test";
    fs::remove_all(root);
    fs::path data = root / "client" / "Data", common = data / "common.MPQ", files = root / "ralia" / "files";
    fs::create_directories(data / "enUS" / "locale-enUS.MPQ");
    WriteText(data / "enUS" / "locale-enUS.MPQ" / "readme.txt", "");

    Rgb human0 { 200, 160, 140 }, human1 { 120, 90, 70 }, changed { 230, 120, 120 };
    Rgb nightborne { 90, 60, 120 }, tattoo { 20, 200, 220 };
    auto withSquare = [](Rgb base, Rgb square) { return [=](uint32_t x, uint32_t y) { return x >= 40 && x < 48 && y >= 10 && y < 18 ? square : base; }; };

    // The game's table and textures.
    Dbc dbc = Sections();
    std::string const H = "Character\\Human\\Female\\";
    Row(dbc, 1, 1, 1, 0, H + "HumanFemaleSkin00_00.blp", "", 0);
    Row(dbc, 2, 1, 1, 0, H + "HumanFemaleSkin00_01.blp", "", 1);
    Row(dbc, 3, 1, 1, 4, H + "HumanFemaleNakedPelvisSkin00_00.blp", H + "HumanFemaleNakedTorsoSkin00_00.blp", 0);
    Row(dbc, 4, 1, 1, 4, H + "HumanFemaleNakedPelvisSkin00_01.blp", H + "HumanFemaleNakedTorsoSkin00_01.blp", 1);
    GameTexture(common, H + "HumanFemaleSkin00_00.blp", Flat(64, 64, human0));
    GameTexture(common, H + "HumanFemaleSkin00_01.blp", Flat(64, 64, human1));
    for (std::string c : { "00", "01" })
        for (std::string part : { "Pelvis", "Torso" })
            GameTexture(common, H + "HumanFemaleNaked" + part + "Skin00_" + c + ".blp", Flat(32, 16, { 250, 250, 250 }), true);
    std::string const O = "Character\\Orc\\Female\\";
    Row(dbc, 5, 2, 1, 0, O + "OrcFemaleSkin00_00.blp", "", 0);
    Row(dbc, 6, 2, 1, 0, O + "OrcFemaleSkin00_01.blp", "", 1);
    GameTexture(common, O + "OrcFemaleSkin00_00.blp", Make(64, 64, [](uint32_t x, uint32_t y) { return ((x / 8 + y / 8) % 2) ? Rgb{ 30, 120, 30 } : Rgb{ 160, 200, 90 }; }));
    GameTexture(common, O + "OrcFemaleSkin00_01.blp", Flat(64, 64, { 60, 110, 50 }));
    std::string const G = "Character\\Gnome\\Female\\";
    Row(dbc, 7, 7, 1, 0, G + "GnomeFemaleSkin00_00.blp", "", 0);
    GameTexture(common, G + "GnomeFemaleSkin00_00.blp", Flat(64, 64, human0));
    Row(dbc, 12, 7, 1, 0, G + "GnomeFemaleSkin00_01.blp", "", 1);
    GameTexture(common, G + "GnomeFemaleSkin00_01.blp", Flat(64, 64, human1));
    Row(dbc, 13, 7, 1, 4, G + "GnomeFemaleNakedPelvisSkin00_00.blp", G + "GnomeFemaleNakedTorsoSkin00_00.blp", 0);
    for (std::string part : { "Pelvis", "Torso" })
        GameTexture(common, G + "GnomeFemaleNaked" + part + "Skin00_00.blp", Flat(32, 16, { 250, 250, 250 }), true);
    std::string const GM = "Character\\Gnome\\Male\\";
    Row(dbc, 14, 7, 0, 0, GM + "GnomeMaleSkin00_00.blp", "", 0);
    GameTexture(common, GM + "GnomeMaleSkin00_00.blp", Flat(64, 64, human0));
    std::string const V = "Character\\VoidElf\\Female\\";
    Row(dbc, 8, 29, 1, 0, V + "VoidElfFemaleSkin00_07.blp", "", 7);
    GameTexture(common, V + "VoidElfFemaleSkin00_07.blp", Flat(64, 64, { 180, 170, 220 }));
    std::string const N = "Character\\Nightborne\\Female\\";
    Row(dbc, 9, 27, 1, 0, N + "NightborneFemaleSkin00_00.blp", "", 0);
    Row(dbc, 10, 27, 1, 0, N + "NightborneFemaleSkin00_10.blp", "", 10);
    GameTexture(common, N + "NightborneFemaleSkin00_00.blp", Flat(64, 64, nightborne));
    GameTexture(common, N + "NightborneFemaleSkin00_10.blp",
        Make(64, 64, [&](uint32_t, uint32_t y) { return y >= 50 && y < 54 ? tattoo : nightborne; }));
    std::string const W = "Character\\Worgen\\Female\\";
    Row(dbc, 11, 22, 1, 0, W + "WORGENFEMALESKIN00_00.blp", "", 0);
    GameTexture(common, W + "WORGENFEMALESKIN00_00.blp", Flat(64, 64, { 100, 80, 60 }));
    // A set's texture as the older models' and the newer's: the one nearer the game's own is used.
    std::string const D = "Character\\Draenei\\Female\\";
    Row(dbc, 21, 11, 1, 0, D + "DraeneiFemaleSkin00_00.blp", "", 0);
    Row(dbc, 22, 11, 1, 0, D + "DraeneiFemaleSkin00_01.blp", "", 1);
    auto stripes = [](uint32_t x, uint32_t) { return (x / 4) % 2 ? Rgb{ 150, 120, 200 } : Rgb{ 110, 90, 170 }; };
    Rgb horn { 250, 250, 40 };
    // (a horn: what an HD look's model draws from outside the body part)
    GameTexture(common, D + "DraeneiFemaleSkin00_00.blp", Make(64, 64, [&](uint32_t x, uint32_t y)
        { return x >= 8 && x < 16 && y >= 48 && y < 56 ? horn : stripes(x, y); }));
    GameTexture(common, D + "DraeneiFemaleSkin00_01.blp", Flat(64, 64, { 130, 100, 180 }));
    // A man's, and the blood elves' first colour (the Skyborne's and the Dark Ranger's).
    std::string const HM = "Character\\Human\\Male\\", B = "Character\\BloodElf\\Female\\";
    Row(dbc, 23, 1, 0, 0, HM + "HumanMaleSkin00_00.blp", "", 0);
    GameTexture(common, HM + "HumanMaleSkin00_00.blp", Flat(64, 64, { 190, 150, 130 }));
    Row(dbc, 24, 10, 1, 0, B + "BloodElfFemaleSkin00_00.blp", "", 0);
    GameTexture(common, B + "BloodElfFemaleSkin00_00.blp", Flat(64, 64, { 230, 190, 160 }));
    Write(common / "DBFilesClient" / "CharSections.dbc", dbc.Write());

    // The Skyborne's patch-Z (read after this one): a table of its own, left out of what it's made from.
    Dbc other = Sections();
    Row(other, 1, 7, 1, 0, G + "GnomeFemaleSkin00_00.blp", "", 0);
    Write(data / "patch-Z.MPQ" / "DBFilesClient" / "CharSections.dbc", other.Write());

    // Ralia's files.
    auto today = [](Rgb, std::function<Rgb(uint32_t, uint32_t)> left)
    {
        return Make(128, 64, [=](uint32_t x, uint32_t y) { return x < 64 ? left(x, y) : Rgb{ 0, 0, 255 }; });
    };
    RaliaTexture(files, "Character/Human/Female/humanfemaleskin00_00_hd.blp", today(human0, withSquare(human0, changed)));
    RaliaTexture(files, "Character/Human/Female/humanfemalenakedpelvisskin00_00_hd.blp", Flat(64, 32, { 0, 0, 0 }, 0));
    RaliaTexture(files, "Character/Human/Female/humanfemalenakedtorsoskin00_00_hd.blp", Flat(64, 32, { 0, 0, 0 }, 0));
    RaliaTexture(files, "Character/Orc/Female/orcfemaleskin00_00_hd.blp",
        today({}, [](uint32_t x, uint32_t) { return Rgb{ int(x * 3), 100, 50 }; }));
    RaliaTexture(files, "Character/Gnome/Female/gnomefemaleskin00_00_hd.blp", today(human0, withSquare(human0, changed)));
    RaliaTexture(files, "Character/Gnome/Male/gnomemaleskin00_00_hd.blp", today(human0, withSquare(human0, changed)));
    RaliaTexture(files, "Character/Gnome/Female/gnomefemalenakedpelvisskin00_00_hd.blp", Flat(64, 32, { 0, 0, 0 }, 0));
    RaliaTexture(files, "Character/Gnome/Female/gnomefemalenakedtorsoskin00_00_hd.blp", Flat(64, 32, { 0, 0, 0 }, 0));
    RaliaTexture(files, "Character/BloodElf/Female/bloodelffemaleskin00_01_hd.blp", today({}, withSquare({ 180, 170, 220 }, { 20, 220, 20 })));
    RaliaTexture(files, "Character/Nightborne/Female/nightbornefemaleskin00_00.blp", today(nightborne, withSquare(nightborne, changed)));
    RaliaTexture(files, "Character/Worgen/Female/worgenfemaleskin00_00.blp", Make(32, 32, [](uint32_t x, uint32_t y)
        { return x >= 20 && x < 24 && y >= 5 && y < 9 ? Rgb{ 220, 30, 30 } : Rgb{ 100, 80, 60 }; }));
    // (draenei 00: the newer is the game's picture changed, the older another; 01: the older is nearer)
    RaliaTexture(files, "Character/Draenei/Female/draeneifemaleskin00_00.blp", today({}, [](uint32_t, uint32_t) { return Rgb{ 250, 20, 20 }; }));
    RaliaTexture(files, "Character/Draenei/Female/draeneifemaleskin00_00_hd.blp", today({}, [&](uint32_t x, uint32_t y)
        { return x >= 40 && x < 48 && y >= 10 && y < 18 ? changed : stripes(x, y); }));
    RaliaTexture(files, "Character/Draenei/Female/draeneifemaleskin00_01.blp", today({}, [](uint32_t, uint32_t) { return Rgb{ 132, 102, 182 }; }));
    RaliaTexture(files, "Character/Draenei/Female/draeneifemaleskin00_01_hd.blp", today({}, [](uint32_t, uint32_t) { return Rgb{ 20, 250, 20 }; }));
    RaliaTexture(files, "Character/Human/Male/humanmaleskin00_00.blp", today({}, [](uint32_t, uint32_t) { return Rgb{ 10, 10, 10 }; }));
    Rgb bloodElf { 230, 190, 160 }, mark { 120, 40, 200 };
    RaliaTexture(files, "Character/BloodElf/Female/bloodelffemaleskin00_00_hd.blp", today({}, withSquare(bloodElf, mark)));
    fs::path sources = root / "sources.txt";
    WriteText(sources, "# test\n"
        "Character\\VoidElf\\Female\\VoidElfFemaleSkin00_07.blp\tcharacter/bloodelf/female/bloodelffemaleskin00_01_hd.blp\n"
        "Character\\Nightborne\\Female\\NightborneFemaleSkin00_00.blp\tcharacter/nightborne/female/nightbornefemaleskin00_00.blp\n"
        "Character\\Nightborne\\Female\\NightborneFemaleSkin00_10.blp\t=Character\\Nightborne\\Female\\NightborneFemaleSkin00_00.blp\n");

    auto log = [](std::string const& line) { std::cout << "  | " << line << "\n"; };
    fs::path patch = data / "enUS" / "patch-enUS-Z.MPQ";
    Check(UpdatePatch(ralia, files, sources, data, log), "the patch is made");
    Check(fs::exists(patch) && fs::exists(fs::path(patch.string() + ".ralia")), "Data/enUS/patch-enUS-Z.MPQ, marked the module's");

    auto archive = Skyborne::OpenArchive(patch);
    auto read = [&](std::string const& name, Image& image, uint8_t& encoding, uint8_t& alphaDepth) -> bool
    {
        Bytes b;
        if (!archive->Read(name, b) || b.size() < 148)
            return false;
        encoding = b[8];
        alphaDepth = b[9];
        return Skyborne::Decode(b, image);
    };
    Image image;
    uint8_t encoding = 0, alphaDepth = 0;

    bool ok = read(H + "HumanFemaleSkin00_00.blp", image, encoding, alphaDepth);
    Check(ok && encoding == 1 && alphaDepth == 0 && image.width == 64 && image.height == 64,
        "a colour with Ralia's file: palettized, the game's size (64 x 64), no alpha as the game's has none");
    Check(ok && Near(image, 44, 14, changed, 6) && Near(image, 5, 5, human0, 6),
        "  its body half (the change at 44,14 " + Show(image, 44, 14) + "; elsewhere " + Show(image, 5, 5) + "), not the head's half");

    ok = read(H + "HumanFemaleSkin00_01.blp", image, encoding, alphaDepth);
    Rgb expected { human1.r * (changed.r + 8) / (human0.r + 8), human1.g * (changed.g + 8) / (human0.g + 8), human1.b * (changed.b + 8) / (human0.b + 8) };
    Check(ok && Near(image, 44, 14, expected, 8) && Near(image, 5, 5, human1, 6),
        "a colour without one takes its nearest's change in its own colour (" + Show(image, 44, 14) + "; elsewhere " + Show(image, 5, 5) + ")");

    for (std::string c : { "00", "01" })
        for (std::string part : { "Pelvis", "Torso" })
        {
            ok = read(H + "HumanFemaleNaked" + part + "Skin00_" + c + ".blp", image, encoding, alphaDepth);
            Check(ok && encoding == 1 && alphaDepth == 8 && image.width == 32 && image.height == 16 && image.rgba[3] == 0,
                "the " + part + " texture of colour " + c + ": Ralia's (" + (c == "00" ? "its own" : "the nearest colour's") + "), alpha and all, at the game's size");
        }

    ok = read(O + "OrcFemaleSkin00_00.blp", image, encoding, alphaDepth);
    auto red = [&](uint32_t x, uint32_t y) { return int(image.rgba[(size_t(y) * image.width + x) * 4]); };
    Check(ok && red(62, 20) > red(34, 20) + 40 && (Near(image, 5, 5, { 30, 120, 30 }, 8) || Near(image, 5, 5, { 160, 200, 90 }, 8)),
        "Ralia's file where it's another picture than the game's: its body part (its gradient: " + Show(image, 34, 20) + " to "
        + Show(image, 62, 20) + "), the rest the game's own " + Show(image, 5, 5));
    ok = read(O + "OrcFemaleSkin00_01.blp", image, encoding, alphaDepth);
    Check(ok && red(62, 20) > red(34, 20) + 20 && Near(image, 5, 5, { 60, 110, 50 }, 6),
        "a colour whose nearest file is another picture takes that file's body part in its own skin " + Show(image, 62, 20) + ", the rest its own " + Show(image, 5, 5));
    ok = read(G + "GnomeFemaleSkin00_00.blp", image, encoding, alphaDepth);
    Check(ok && image.width == 64 && encoding == 1 && Near(image, 44, 14, changed, 8), "female gnome skin takes Ralia's body half, palettized at the game's size");
    ok = read(GM + "GnomeMaleSkin00_00.blp", image, encoding, alphaDepth);
    Check(ok && Near(image, 44, 14, changed, 8), "male gnome skin takes its matching Ralia texture");
    ok = read(G + "GnomeFemaleSkin00_01.blp", image, encoding, alphaDepth);
    Rgb gnomeChanged { human1.r * (changed.r + 8) / (human0.r + 8), human1.g * (changed.g + 8) / (human0.g + 8), human1.b * (changed.b + 8) / (human0.b + 8) };
    Check(ok && Near(image, 5, 5, human1, 6) && Near(image, 44, 14, gnomeChanged, 8), "a gnome colour without a file keeps its own colour and takes the nearest change");
    for (std::string part : { "Pelvis", "Torso" })
    {
        ok = read(G + "GnomeFemaleNaked" + part + "Skin00_00.blp", image, encoding, alphaDepth);
        Check(ok && image.width == 32 && image.height == 16 && image.rgba[3] == 0, "female gnome " + part + " uses Ralia's overlay and alpha");
    }

    ok = read(V + "VoidElfFemaleSkin00_07.blp", image, encoding, alphaDepth);
    Check(ok && Near(image, 44, 14, { 20, 220, 20 }, 10) && Near(image, 10, 50, { 180, 170, 220 }, 6),
        "sources.txt's file for a colour numbered otherwise (its mark " + Show(image, 44, 14) + ")");

    ok = read(N + "NightborneFemaleSkin00_10.blp", image, encoding, alphaDepth);
    // (the same colour as the plain one's: its change, scaled as the plain colour's is)
    Rgb plainChanged { nightborne.r * (changed.r + 8) / (nightborne.r + 8), nightborne.g * (changed.g + 8) / (nightborne.g + 8),
                       nightborne.b * (changed.b + 8) / (nightborne.b + 8) };
    Check(ok && Near(image, 5, 51, tattoo, 6) && Near(image, 5, 5, nightborne, 6) && Near(image, 44, 14, plainChanged, 8),
        "a tattooed colour takes its plain colour's change and keeps its tattoo (" + Show(image, 5, 51) + ", " + Show(image, 44, 14) + ")");

    ok = read(W + "WORGENFEMALESKIN00_00.blp", image, encoding, alphaDepth);
    Check(ok && image.width == 64 && red(44, 14) > 150 && image.rgba[(14 * 64 + 44) * 4 + 1] < 90 && Near(image, 10, 50, { 100, 80, 60 }, 6),
        "a square file (the Worgen's) is all body, at the game's size (its mark " + Show(image, 44, 14) + ")");

    ok = read(D + "DraeneiFemaleSkin00_00.blp", image, encoding, alphaDepth);
    Check(ok && Near(image, 44, 14, changed, 8) && !Near(image, 5, 5, { 250, 20, 20 }, 40),
        "a texture both as the older models' and the newer's: the newer, nearer the game's picture " + Show(image, 44, 14));
    Check(ok && Near(image, 12, 52, horn, 8), "outside the body part the game's own stays (an HD look's horns " + Show(image, 12, 52) + ")");
    ok = read(D + "DraeneiFemaleSkin00_01.blp", image, encoding, alphaDepth);
    Check(ok && Near(image, 5, 5, { 132, 102, 182 }, 6), "  and the older where it's the nearer " + Show(image, 5, 5));
    Check(archive->Has(HM + "HumanMaleSkin00_00.blp"), "Ralia's mod takes the men's textures it has");

    // The Skyborne's patch, made after this one from the game with it in: their skins and the Dark
    // Ranger's are the set's blood elf skin recoloured (the square of another colour stays one).
    archive.reset();
    fs::remove_all(data / "patch-Z.MPQ");
    Skyborne::UpdatePatch(skyborneData, data, [](std::string const& line) { std::cout << "  | skyborne: " << line.substr(0, 120) << "\n"; });
    {
        auto sky = Skyborne::OpenArchive(data / "patch-Z.MPQ");
        // ...and it carries the set's textures (the HD look's and the race modules' Data patches won over
        // the language folder's in the game): byte for byte the language folder patch's, every listed path.
        {
            auto ours = Skyborne::OpenArchive(patch);
            std::ifstream list(patch.string() + ".files");
            size_t listed = 0, same = 0;
            for (std::string path; std::getline(list, path);)
            {
                ++listed;
                Bytes a, b;
                if (ours->Read(path, a) && sky->Read(path, b) && a == b)
                    ++same;
            }
            Check(listed > 0 && same == listed, "the Skyborne's patch carries the set's " + std::to_string(listed)
                + " textures (" + std::to_string(same) + " the same)");
        }
        for (std::string name : { B + "BloodElfFemaleSkin00_19.blp", std::string("Character\\Skyborne\\Female\\SkyborneFemaleSkin00_19.blp") })
        {
            Bytes b;
            Image made;
            bool decoded = sky->Read(name, b) && Skyborne::Decode(b, made);
            auto at = [&](uint32_t x, uint32_t y) { uint8_t const* p = &made.rgba[(size_t(y) * made.width + x) * 4]; return std::abs(p[0] - p[2]) + std::abs(p[1] - p[2]); };
            Check(decoded && made.width == 64 && std::abs(int(at(44, 14)) - int(at(5, 5))) + std::abs(int(made.rgba[(14 * 64 + 44) * 4]) - int(made.rgba[(5 * 64 + 5) * 4])) > 12,
                name.substr(name.find_last_of('\\') + 1) + ", the Skyborne's patch's, is the set's blood elf skin recoloured: the square is in it (" + (decoded ? Show(made, 44, 14) + " against " + Show(made, 5, 5) : std::string("not made")) + ")");
        }
    }
    fs::remove(data / "patch-Z.MPQ");
    fs::remove(data / "patch-Z.MPQ.skyborne");

    // Alternate Female Options: the women's textures alone (made again: another set).
    Check(UpdatePatch(alternate, files, sources, data, log), "Alternate Female Options' patch is made");
    archive = Skyborne::OpenArchive(patch);
    Check(!archive->Has(HM + "HumanMaleSkin00_00.blp") && archive->Has(H + "HumanFemaleSkin00_00.blp") && !archive->Has(G + "GnomeFemaleSkin00_00.blp"),
        "  with the women's textures alone (and still no gnomes)");
    archive.reset();
    Check(UpdatePatch(ralia, files, sources, data, log), "Ralia's mod's made again in its place");
    archive = Skyborne::OpenArchive(patch);
    Check(archive->Has(HM + "HumanMaleSkin00_00.blp"), "  with the men's again");

    archive.reset();
    auto time = fs::last_write_time(patch);
    std::this_thread::sleep_for(std::chrono::milliseconds(1100));
    Check(UpdatePatch(ralia, files, sources, data, log) && fs::last_write_time(patch) == time, "made once: the same files and game make no new patch");

    fs::remove_all(files);
    fs::create_directories(files);
    Check(!UpdatePatch(ralia, files, sources, data, log) && !fs::exists(patch), "with no files it's taken out of the game");

    WriteText(patch, "not the module's");
    RaliaTexture(files, "Character/Human/Female/humanfemaleskin00_00_hd.blp", today(human0, withSquare(human0, changed)));
    Check(!UpdatePatch(ralia, files, sources, data, log) && fs::exists(patch), "a patch-enUS-Z.MPQ that isn't the module's is left alone");
    fs::remove(patch);
    Check(UpdatePatch(ralia, files, sources, data, log) && fs::exists(patch), "made again once it's gone");
    RemovePatch(data, log);
    Check(!fs::exists(patch) && !fs::exists(fs::path(patch.string() + ".ralia")) && !fs::exists(fs::path(patch.string() + ".files")),
        "RemovePatch takes it, its mark and its list out");

    fs::remove_all(root);
    std::cout << (failures ? "FAILED: " + std::to_string(failures) : std::string("all passed")) << "\n";
    return failures ? 1 : 0;
}
