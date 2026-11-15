// M2, the game's model format (characters, creatures, props), as today's game stores it: an MD21
// chunk holding the MD20 model, with its skins (.skin), animations (.anim) and textures named by
// file id. This side holds the data and evaluates the skeleton; m2_gl draws it.
#pragma once

#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "bytes.h"
#include "wmath.h"

namespace wc {

// Finds a game file by its file id: the path it was downloaded to, or "" when it isn't there.
using FileLookup = std::function<std::string(uint32_t)>;

struct M2Vertex {
    float pos[3];
    uint8_t weights[4];
    uint8_t bones[4];
    float normal[3];
    float uv[2];
    float uv2[2];
};

struct M2Track {
    uint16_t interpolation = 0;
    uint16_t globalSeq = 0xFFFF;
    uint8_t home = 0;     // 0: the keys are the model's own; 1: its skeleton file's (bones of a model that has one)
    M2Array timestamps;   // one (count, offset) per sequence
    M2Array values;
};

struct M2Bone {
    int32_t keyBoneId = -1;
    uint32_t flags = 0;
    int16_t parent = -1;
    uint32_t nameCrc = 0;    // the bone's name, hashed: how an item model's bones find the character's
    M2Track translation, rotation, scale;
    V3 pivot;
};

struct M2Sequence {
    uint16_t id = 0, variation = 0;
    uint32_t duration = 0;
    float moveSpeed = 0;
    uint32_t flags = 0;
    int16_t variationNext = -1;
    uint16_t aliasNext = 0;
    uint16_t blendIn = 150;
};

struct M2Texture {
    uint32_t type = 0;      // 0: the file below; otherwise a slot the look fills (1 skin, 2 cape, 6 hair, 11-13 creature skins, ...)
    uint32_t flags = 0;     // 1 wrap U, 2 wrap V
    uint32_t fileId = 0;
};

struct M2Submesh {
    uint16_t id = 0;        // geoset id
    uint32_t indexStart = 0, indexCount = 0;
    V3 sortCenter;
};

struct M2Batch {
    uint8_t flags = 0;
    int8_t priority = 0;
    uint16_t shaderId = 0;
    uint16_t submesh = 0;
    uint16_t colorIndex = 0xFFFF;
    uint16_t material = 0;
    uint16_t layer = 0;
    uint16_t textureCount = 1;
    uint16_t textureCombo = 0;
    uint16_t coordCombo = 0;      // into textureCoordCombos: which of the vertex's two texture coordinates each texture uses
    uint16_t transformCombo = 0xFFFF;   // into textureTransformCombos: how each texture's picture slides and stretches
    uint16_t weightCombo = 0xFFFF;
};

struct M2Material {
    uint16_t flags = 0;     // 1 unlit, 2 unfogged, 4 two-sided, 8 no depth test, 16 no depth write
    uint16_t blend = 0;     // 0 opaque, 1 alpha key, 2 alpha, 3 no-alpha add, 4 add, 5 mod, 6 mod2x, 7 blend add
};

struct M2Attachment {
    uint32_t id = 0;
    uint16_t bone = 0;
    V3 position;
};

// Each bone's position, turn and size at one moment of one animation, before the hierarchy.
struct BonePose {
    V3 t;
    Quat r;
    V3 s{1, 1, 1};
};

class M2Model {
public:
    bool load(uint32_t fileId, const FileLookup& files);
    // The other files a model's file names, read from the model alone (before its skin is there): its first skin, the
    // textures it names itself, and the animation file of each (animation id, variation 0) asked for.
    // A model with a skeleton file names it; the skeleton names its animations and maybe a parent skeleton, so this is asked
    // again once those are there, until it adds nothing new.
    static bool dependencies(const std::string& path, const std::vector<uint16_t>& animIds, std::vector<uint32_t>& out,
                             const FileLookup* files = nullptr);

    uint32_t fileId = 0;
    uint32_t flags = 0;
    std::vector<M2Vertex> vertices;
    std::vector<uint32_t> indices;           // the first skin's triangles, as model vertex numbers
    std::vector<M2Submesh> submeshes;
    std::vector<M2Batch> batches;
    std::vector<M2Texture> textures;
    std::vector<uint16_t> textureCombos;
    std::vector<int16_t> textureCoordCombos;   // 0: the first coordinates, 1: the second, -1: a reflection
    std::vector<int16_t> textureTransformCombos;   // -1: none
    struct TexTransform { M2Track translation, scale; };
    std::vector<TexTransform> textureTransforms;
    std::vector<M2Material> materials;
    std::vector<uint16_t> weightCombos;
    std::vector<M2Track> weights;            // texture weights (int16 alpha)
    std::vector<M2Track> colorRgb, colorAlpha;
    std::vector<M2Bone> bones;
    std::vector<M2Sequence> sequences;
    std::vector<uint32_t> globalLoops;
    std::vector<M2Attachment> attachments;
    std::vector<int16_t> attachmentLookup;
    V3 boundsMin, boundsMax;     // as the file gives them (the animations' reach)
    V3 extentMin, extentMax;     // of the vertices themselves

    // The sequence index playing `animId` (its first variation), or -1.
    int findSequence(uint16_t animId) const;
    // Loads the .anim file a sequence's keys are in, when they aren't in the model.
    void ensureSequence(int seq, const FileLookup& files);
    bool sequenceReady(int seq) const;

    // The local pose of every bone at `timeMs` into sequence `seq` (`globalMs` drives looping
    // effects that run on their own clock).
    void pose(int seq, uint32_t timeMs, uint32_t globalMs, std::vector<BonePose>& out) const;
    // Turns local poses into each bone's matrix in model space. With `facing` (three vectors in the model's own space:
    // toward the eye, to the eye's left as the model sees it, and up), bones that always face the viewer (glows, flames) do.
    void bonesToMatrices(const std::vector<BonePose>& poses, std::vector<M4>& out, const V3* facing = nullptr) const;

    float evalWeight(int index, int seq, uint32_t timeMs, uint32_t globalMs) const;
    // How texture `which` (0 or 1) of a batch moves over its surface now: a matrix for its texture coordinates.
    M4 evalTexTransform(const M2Batch& b, int which, int seq, uint32_t timeMs, uint32_t globalMs) const;
    void evalColor(int index, int seq, uint32_t timeMs, uint32_t globalMs, float rgba[4]) const;

private:
    Bytes file_;
    size_t base_ = 0;                       // where MD20 starts in file_
    Bytes skel_;                            // the skeleton file the bones came from, when the model has one
    size_t skelBase_ = 0;                   // where its bones' chunk starts
    std::vector<uint32_t> skelLoops_;       // the skeleton's own looping clocks
    std::map<int, Bytes> animFiles_;        // sequence -> its .anim keys
    std::map<int, size_t> animBase_;        // offset of the model's keys within that file
    std::map<int, size_t> animSkelBase_;    // offset of the skeleton's keys within that file
    std::vector<std::pair<uint32_t, uint32_t>> afid_;   // (animId | variation << 16, file id)

    int dataSequence(int seq) const;         // follows aliases
    bool keys(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs,
              const uint8_t*& data, size_t& dataSize, uint32_t& tsOff, uint32_t& valOff,
              uint32_t& count, uint32_t& time) const;
    V3 evalV3(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs, V3 def) const;
    Quat evalQuat(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs) const;
    float evalShort(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs, float def) const;
};

} // namespace wc
