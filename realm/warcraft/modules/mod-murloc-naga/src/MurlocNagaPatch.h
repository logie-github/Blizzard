// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The Murlocs' and the Naga's patch for the game (mod-murloc-naga): Data/<locale>/patch-<locale>-T.MPQ.
 */

#ifndef MOD_MURLOC_NAGA_PATCH_H
#define MOD_MURLOC_NAGA_PATCH_H

#include "../../mod-skyborne/src/SkyborneFiles.h"
#include <filesystem>
#include <functional>
#include <string>

namespace MurlocNaga
{
    namespace fs = std::filesystem;
    using Skyborne::Bytes;

    using Log = std::function<void(std::string const&)>;

    // Makes the patch in the client's Data folder [clientData] from the module's files
    // ([moduleData]: data/client) and the client's own (made again only when either changed).
    bool UpdatePatch(fs::path const& moduleData, fs::path const& clientData, Log const& log);
    // Takes the patch out of the game (the module's switch off).
    void RemovePatch(fs::path const& clientData, Log const& log);
    // Keeps the patch beside the game, out of it, for a realm without the races (Wrath Remix's).
    void SetPatchAside(fs::path const& clientData, Log const& log);
    // The intros' cameras in the server's data folder (its Cameras), where the world server reads
    // them to follow the camera.
    void PutCameras(fs::path const& moduleData, fs::path const& serverData, Log const& log);

    // The pieces, for the test (tools/test_patch.cpp).
    // [blp] recoloured: every colour's hue made [hue] (0 to 1 around the colour wheel; below 0, kept),
    // its saturation and lightness multiplied (a palette's colours; any other texture's pixels, then
    // palettized).
    bool Recolour(Bytes& blp, double hue, double saturation, double lightness);
    // [image] as a palettized BLP2 (256 colours by median cut, every mip level; alpha 8 bits when
    // [alpha]), the format of the game's own character textures.
    Bytes EncodePalette(Skyborne::Image const& image, bool alpha);
    // The naga's parts (tools/naga_parts.py's Naga<Sex>Parts.dat: headdresses and outfits) added to a
    // naga model ([m2], its [skin]): each part's vertices on the model's bones at their places, its
    // triangles a section of each of its uses' geosets, with its texture (the hair's, or its own).
    // False (and [why]) when the parts or the model aren't what this knows, or don't fit it.
    bool MergeParts(Bytes& m2, Bytes& skin, Bytes const& parts, std::string& why);
    // The naga's emotes (tools/naga_emotes.py's Naga<Sex>Emotes.dat: today's naga's skeleton and each
    // bone's own keys in each new sequence) added to a naga model ([m2]) as sequences of its own (those
    // it hasn't): where each of its bones goes in the world found from the emote bone at its place (the
    // rest held as it stands), its own keys worked out against its own parents. [added]: how many
    // sequences. False (and [why]) when the emotes or the model aren't what this knows.
    bool MergeEmotes(Bytes& m2, Bytes const& emotes, std::string& why, size_t* added = nullptr);
    // The narration: the game's sounds ([parts]: when, the sound's WAV), mixed into one WAV, 22050
    // Hz, mono, 16 bits.
    Bytes MixNarration(std::vector<std::pair<uint32_t, Bytes>> const& parts);
}

#endif
