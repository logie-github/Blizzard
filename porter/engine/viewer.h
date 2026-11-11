// One World of Warcraft character on a plain backdrop, drawn with OpenGL ES 3.0: the race's model, its skin painted from the
// game's layers (customizations, then what is worn), the geosets its look and gear show, items hung on its attachment points
// (helm, shoulders, weapons) and items that move with its skeleton (the parts of newer armour). The character porter's
// preview: the look itself is worked out in Kotlin from the game's tables (com.logie.blizz.porter.look), this draws it.
// WoW's own axes: x forward (the way the model faces), y to its left, z up, in yards.
#pragma once

#include <cstdint>
#include <map>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "blp.h"
#include "m2.h"
#include "wmath.h"

namespace wc {

// One picture painted into a character's texture: the file, where it goes on the canvas, and how it mixes with what is
// under it (the game's ChrModelTextureLayer.BlendMode: 1, 9, 15 alpha; 4 multiply; 6 overlay; 7 screen; 0 as it is).
struct Layer {
    uint32_t fileId = 0;
    int x = 0, y = 0, width = 0, height = 0;
    int blend = 1;
};

// Paints `layers` in order onto a canvas of width x height (transparent black to begin with). A layer whose file isn't
// there or can't be read is left out.
void composite(const FileLookup& files, int width, int height, const std::vector<Layer>& layers, Image& out);

class Viewer {
public:
    explicit Viewer(FileLookup files) : files_(std::move(files)) {}

    bool initGl();       // after a context is current; again after it was lost
    void releaseGl();    // the context is gone: forget its objects

    // Takes the character off, with everything on it.
    void clear();
    // The race's model. `geosetGroups` (group -> value; 0: none of that group) over the model's defaults.
    bool setCharacter(uint32_t modelFileId, const std::map<int, int>& geosetGroups);
    // One of the model's own textures by its type (1 skin, 6 hair, 19 eyes, ...), painted from layers.
    void setCanvas(uint32_t textureType, int width, int height, const std::vector<Layer>& layers);
    // One of the model's textures by its type, as one file (2: the cape's).
    void setTexture(uint32_t textureType, uint32_t fileId);
    // An item's model on an attachment point (11 helm, 6 and 5 the shoulders, 1 and 2 the hands, 0 a shield, 53 the buckle);
    // `textures` are the item's own by texture type (every type takes the first when its own isn't named).
    bool attach(uint32_t attachmentId, uint32_t modelFileId, const std::map<uint32_t, uint32_t>& textures);
    // An item's model that moves with the character's bones (they are matched by name). `geosets`: the ids to show, or all.
    bool addSkinned(uint32_t modelFileId, const std::map<uint32_t, uint32_t>& textures, const std::vector<int>& geosets);
    void setAnim(uint16_t animId);

    // Where the eye is: turned `yaw` around the character (0: in front of it), raised by `pitch` (radians), `zoom` 1 for the
    // whole character in the picture, more to come closer; `lift` moves the middle of the picture up the character (0 feet, 1 head).
    void setView(float yaw, float pitch, float zoom, float lift);
    void setBackdrop(const float top[3], const float bottom[3]);
    void render(int width, int height, uint32_t nowMs);

    bool hasCharacter() const { return body_.mesh != nullptr; }
    float height() const;

private:
    struct ModelGl {
        std::unique_ptr<M2Model> model;
        unsigned vao = 0, vbo = 0, ibo = 0;
        unsigned boneTex = 0;            // identity bones, for models drawn as they were built
        bool ok = false;
    };
    struct Part {
        ModelGl* mesh = nullptr;
        uint32_t attachment = 0;
        bool skinned = false;
        std::map<uint32_t, uint32_t> textures;
        std::vector<uint16_t> geosets;
        std::vector<int> boneOf;         // skinned: each of its bones' place in the character's skeleton, or -1
        int seq = -1;                    // hung: the item's own standing animation (it folds away what it shows only at times)
        unsigned boneTex = 0;
        std::vector<BonePose> pose;
        std::vector<M4> mats;
    };
    struct Canvas {
        int width = 0, height = 0;
        std::vector<Layer> layers;
        unsigned tex = 0;                // 0: not painted yet (or the context was lost)
    };
    struct Body {
        ModelGl* mesh = nullptr;
        std::vector<uint16_t> geosets;
        std::map<uint32_t, Canvas> canvases;
        std::map<uint32_t, uint32_t> textures;
        std::vector<Part> parts;
        int seq = -1;
        uint16_t animId = 0;
        unsigned boneTex = 0;
        std::vector<BonePose> pose;
        std::vector<M4> mats;
        bool measured = false;           // how tall and wide it stands, taken from its first pose
        float low = 0, high = 2, wide = 1;
    };

    FileLookup files_;
    bool glReady_ = false;
    unsigned prog_ = 0, backProg_ = 0, backVao_ = 0, backVbo_ = 0, white_ = 0;
    std::unordered_map<uint32_t, unsigned> textures_;
    std::unordered_map<uint32_t, std::unique_ptr<ModelGl>> models_;
    Body body_;
    float yaw_ = 0, pitch_ = 0.05f, zoom_ = 1, lift_ = 0.5f;
    float top_[3] = {0.16f, 0.17f, 0.22f}, bottom_[3] = {0.05f, 0.05f, 0.07f};

    unsigned texture(uint32_t fileId);
    ModelGl* model(uint32_t fileId);
    void uploadModel(ModelGl& m);
    void animate(uint32_t now, const V3& eye);
    bool attachmentMatrix(uint32_t attachmentId, M4& out) const;
    void measure();
    void drawBackdrop();
    void drawModel(ModelGl& m, const M4& world, const std::map<uint32_t, unsigned>* glByType, const std::map<uint32_t, uint32_t>* fileByType,
                   const std::vector<uint16_t>* geosets, unsigned boneTex, int seq, uint32_t t, uint32_t now, bool transparent);
};

} // namespace wc
