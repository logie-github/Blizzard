#include "viewer.h"

#include <GLES3/gl3.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>

namespace wc {

namespace {

const char* kVs = R"(#version 300 es
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aUv;
layout(location = 3) in vec4 aBones;
layout(location = 4) in vec4 aWeights;
layout(location = 5) in vec2 aUv2;
uniform mat4 uWorld;
uniform mat4 uViewProj;
uniform mat4 uTexMat;
uniform mat4 uTexMat2;
uniform int uSecondCoords;
uniform highp sampler2D uBones;
out vec3 vNormal;
out vec2 vUv;
out vec2 vUv2;
mat4 bone(float i) {
    int b = int(i + 0.5);
    return mat4(texelFetch(uBones, ivec2(0, b), 0), texelFetch(uBones, ivec2(1, b), 0),
                texelFetch(uBones, ivec2(2, b), 0), texelFetch(uBones, ivec2(3, b), 0));
}
void main() {
    float total = aWeights.x + aWeights.y + aWeights.z + aWeights.w;
    mat4 skin = total > 0.0
        ? bone(aBones.x) * aWeights.x + bone(aBones.y) * aWeights.y + bone(aBones.z) * aWeights.z + bone(aBones.w) * aWeights.w
        : mat4(1.0);
    if (total > 0.0) skin = skin * (1.0 / total);
    vec4 p = uWorld * (skin * vec4(aPos, 1.0));
    vNormal = mat3(uWorld) * (mat3(skin) * aNormal);
    vUv = (uTexMat * vec4(aUv, 0.0, 1.0)).xy;
    vUv2 = (uTexMat2 * vec4(uSecondCoords == 1 ? aUv2 : aUv, 0.0, 1.0)).xy;
    gl_Position = uViewProj * p;
}
)";

const char* kFs = R"(#version 300 es
precision highp float;
in vec3 vNormal;
in vec2 vUv;
in vec2 vUv2;
uniform sampler2D uTex;
uniform sampler2D uTex2;
uniform int uTwo;       // 1: a second texture multiplied in
uniform vec4 uColor;
uniform float uAlphaRef;
uniform int uUnlit;
uniform int uOpaque;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uAmbient;
out vec4 fragColor;
void main() {
    vec4 c = texture(uTex, vUv) * uColor;
    if (uTwo != 0) c *= texture(uTex2, vUv2);
    if (c.a < uAlphaRef) discard;
    vec3 rgb = c.rgb;
    if (uUnlit == 0) {
        vec3 n = normalize(vNormal);
        // Lit from the front and above; the far side keeps some light, as the game's character screens do.
        float d = dot(n, -uSunDir);
        rgb *= uAmbient + uSunColor * (max(d, 0.0) + 0.25 * max(-d, 0.0));
    }
    fragColor = vec4(rgb, uOpaque == 1 ? 1.0 : c.a);
}
)";

const char* kBackVs = R"(#version 300 es
layout(location = 0) in vec2 aPos;
out float vUp;
void main() { vUp = aPos.y * 0.5 + 0.5; gl_Position = vec4(aPos, 0.9999, 1.0); }
)";

const char* kBackFs = R"(#version 300 es
precision highp float;
in float vUp;
uniform vec3 uTop;
uniform vec3 uBottom;
out vec4 fragColor;
void main() { fragColor = vec4(mix(uBottom, uTop, smoothstep(0.0, 1.0, vUp)), 1.0); }
)";

unsigned compile(unsigned kind, const char* src) {
    unsigned s = glCreateShader(kind);
    glShaderSource(s, 1, &src, nullptr);
    glCompileShader(s);
    int ok = 0;
    glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[2048]; glGetShaderInfoLog(s, sizeof log, nullptr, log);
        std::fprintf(stderr, "shader: %s\n", log);
    }
    return s;
}

unsigned program(const char* vs, const char* fs) {
    unsigned p = glCreateProgram();
    unsigned v = compile(GL_VERTEX_SHADER, vs), f = compile(GL_FRAGMENT_SHADER, fs);
    glAttachShader(p, v); glAttachShader(p, f);
    glLinkProgram(p);
    int ok = 0;
    glGetProgramiv(p, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[2048]; glGetProgramInfoLog(p, sizeof log, nullptr, log);
        std::fprintf(stderr, "program: %s\n", log);
    }
    glDeleteShader(v); glDeleteShader(f);
    return p;
}

void blendFor(uint32_t mode) {
    switch (mode) {
        case 3: glBlendFunc(GL_ONE, GL_ONE); break;
        case 4: glBlendFunc(GL_SRC_ALPHA, GL_ONE); break;
        case 5: glBlendFunc(GL_DST_COLOR, GL_ZERO); break;
        case 6: glBlendFunc(GL_DST_COLOR, GL_SRC_COLOR); break;
        case 7: glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA); break;
        default: glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); break;
    }
}

// Which of a character model's geosets show: the body, the first of most groups, then the look's choices and gear.
std::vector<uint16_t> characterGeosets(const M2Model& m, const std::map<int, int>& groups) {
    std::vector<uint16_t> out;
    for (const M2Submesh& sm : m.submeshes) {
        int id = sm.id, group = id < 100 ? 0 : id / 100, value = id < 100 ? id : id % 100;
        bool show = id == 0 || (id >= 100 && value == 1) || group == 32;
        if (group == 17 || group == 35) show = false;
        auto it = groups.find(group);
        if (id != 0 && it != groups.end()) show = value == it->second;
        if (show && std::find(out.begin(), out.end(), sm.id) == out.end()) out.push_back(sm.id);
    }
    if (out.empty()) out.push_back(0xFFFF);   // nothing to show rather than everything
    return out;
}

unsigned upload(const Image& img, bool repeat) {
    unsigned id = 0;
    glGenTextures(1, &id);
    // Always through the first texture unit: the second holds the bones of whatever is being drawn.
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, id);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.rgba.data());
    glGenerateMipmap(GL_TEXTURE_2D);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, repeat ? GL_REPEAT : GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, repeat ? GL_REPEAT : GL_CLAMP_TO_EDGE);
    return id;
}

inline uint8_t mix8(int under, int over, int alpha) { return uint8_t((under * (255 - alpha) + over * alpha + 127) / 255); }

} // namespace

void composite(const FileLookup& files, int width, int height, const std::vector<Layer>& layers, Image& out) {
    out.width = width;
    out.height = height;
    out.hasAlpha = false;
    out.rgba.assign(size_t(width) * height * 4, 0);
    for (const Layer& layer : layers) {
        if (!layer.fileId || layer.width <= 0 || layer.height <= 0) continue;
        std::string path = files(layer.fileId);
        Bytes file;
        Image src;
        if (path.empty() || !readFile(path, file) || !decodeBlp(file, std::max(layer.width, layer.height), src)) continue;
        if (src.width <= 0 || src.height <= 0) continue;
        for (int py = 0; py < layer.height; ++py) {
            int dy = layer.y + py;
            if (dy < 0 || dy >= height) continue;
            // The middle of each canvas pixel in the layer's picture, between its four nearest pixels.
            float fy = (py + 0.5f) * src.height / layer.height - 0.5f;
            int y0 = std::clamp(int(std::floor(fy)), 0, src.height - 1), y1 = std::min(y0 + 1, src.height - 1);
            float wy = std::clamp(fy - float(y0), 0.0f, 1.0f);
            for (int px = 0; px < layer.width; ++px) {
                int dx = layer.x + px;
                if (dx < 0 || dx >= width) continue;
                float fx = (px + 0.5f) * src.width / layer.width - 0.5f;
                int x0 = std::clamp(int(std::floor(fx)), 0, src.width - 1), x1 = std::min(x0 + 1, src.width - 1);
                float wx = std::clamp(fx - float(x0), 0.0f, 1.0f);
                const uint8_t* a = &src.rgba[(size_t(y0) * src.width + x0) * 4];
                const uint8_t* b = &src.rgba[(size_t(y0) * src.width + x1) * 4];
                const uint8_t* c = &src.rgba[(size_t(y1) * src.width + x0) * 4];
                const uint8_t* d = &src.rgba[(size_t(y1) * src.width + x1) * 4];
                int s[4];
                for (int k = 0; k < 4; ++k) {
                    float top = a[k] + (b[k] - a[k]) * wx, bottom = c[k] + (d[k] - c[k]) * wx;
                    s[k] = int(top + (bottom - top) * wy + 0.5f);
                }
                uint8_t* dst = &out.rgba[(size_t(dy) * width + dx) * 4];
                int alpha = s[3];
                if (layer.blend == 0 || dst[3] == 0) {
                    // Nothing under it (or the layer replaces what is): the picture as it is.
                    if (layer.blend == 0 || alpha > 0) { dst[0] = uint8_t(s[0]); dst[1] = uint8_t(s[1]); dst[2] = uint8_t(s[2]); dst[3] = uint8_t(alpha); }
                    continue;
                }
                if (alpha == 0) continue;
                for (int k = 0; k < 3; ++k) {
                    int under = dst[k], over = s[k];
                    switch (layer.blend) {
                        case 4: over = under * over / 255; break;
                        case 6: over = under < 128 ? 2 * under * over / 255 : 255 - 2 * (255 - under) * (255 - over) / 255; break;
                        case 7: over = 255 - (255 - under) * (255 - over) / 255; break;
                        default: break;
                    }
                    dst[k] = mix8(under, over, alpha);
                }
                dst[3] = uint8_t(alpha + dst[3] * (255 - alpha) / 255);
            }
        }
    }
    for (size_t i = 3; i < out.rgba.size(); i += 4) if (out.rgba[i] != 255) { out.hasAlpha = true; break; }
}

bool Viewer::initGl() {
    prog_ = program(kVs, kFs);
    backProg_ = program(kBackVs, kBackFs);
    glGenVertexArrays(1, &backVao_);
    glGenBuffers(1, &backVbo_);
    glBindVertexArray(backVao_);
    glBindBuffer(GL_ARRAY_BUFFER, backVbo_);
    const float quad[8] = {-1, -1, 1, -1, -1, 1, 1, 1};
    glBufferData(GL_ARRAY_BUFFER, sizeof quad, quad, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, (void*)0);
    glBindVertexArray(0);
    glGenTextures(1, &white_);
    uint8_t px[4] = {255, 255, 255, 255};
    glBindTexture(GL_TEXTURE_2D, white_);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, px);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glReady_ = true;
    // A context that was lost took everything with it: what the viewer holds is built again as it is drawn.
    for (auto& [id, m] : models_) if (m->ok) uploadModel(*m);
    return true;
}

void Viewer::releaseGl() {
    glReady_ = false;
    textures_.clear();
    for (auto& [id, m] : models_) m->vao = m->vbo = m->ibo = m->boneTex = 0;
    body_.boneTex = 0;
    for (auto& [type, canvas] : body_.canvases) canvas.tex = 0;
    for (Part& p : body_.parts) p.boneTex = 0;
}

void Viewer::clear() {
    if (glReady_) {
        if (body_.boneTex) glDeleteTextures(1, &body_.boneTex);
        for (auto& [type, canvas] : body_.canvases) if (canvas.tex) glDeleteTextures(1, &canvas.tex);
        for (Part& p : body_.parts) if (p.boneTex) glDeleteTextures(1, &p.boneTex);
    }
    body_ = Body();
}

unsigned Viewer::texture(uint32_t fileId) {
    auto it = textures_.find(fileId);
    if (it != textures_.end()) return it->second;
    unsigned id = white_;
    Bytes b;
    Image img;
    std::string path = fileId ? files_(fileId) : "";
    if (!path.empty() && readFile(path, b) && decodeBlp(b, 1024, img)) id = upload(img, true);
    textures_[fileId] = id;
    return id;
}

Viewer::ModelGl* Viewer::model(uint32_t fileId) {
    auto it = models_.find(fileId);
    if (it != models_.end()) return it->second->ok ? it->second.get() : nullptr;
    auto m = std::make_unique<ModelGl>();
    m->model = std::make_unique<M2Model>();
    m->ok = m->model->load(fileId, files_);
    if (m->ok && glReady_) uploadModel(*m);
    ModelGl* raw = m->ok ? m.get() : nullptr;
    models_[fileId] = std::move(m);
    return raw;
}

void Viewer::uploadModel(ModelGl& m) {
    const M2Model& md = *m.model;
    glGenVertexArrays(1, &m.vao);
    glBindVertexArray(m.vao);
    glGenBuffers(1, &m.vbo);
    glBindBuffer(GL_ARRAY_BUFFER, m.vbo);
    glBufferData(GL_ARRAY_BUFFER, md.vertices.size() * sizeof(M2Vertex), md.vertices.data(), GL_STATIC_DRAW);
    glGenBuffers(1, &m.ibo);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, m.ibo);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, md.indices.size() * 4, md.indices.data(), GL_STATIC_DRAW);
    const GLsizei st = sizeof(M2Vertex);
    glEnableVertexAttribArray(0); glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, st, (void*)0);
    glEnableVertexAttribArray(1); glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, st, (void*)20);
    glEnableVertexAttribArray(2); glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, st, (void*)32);
    glEnableVertexAttribArray(3); glVertexAttribPointer(3, 4, GL_UNSIGNED_BYTE, GL_FALSE, st, (void*)16);
    glEnableVertexAttribArray(4); glVertexAttribPointer(4, 4, GL_UNSIGNED_BYTE, GL_TRUE, st, (void*)12);
    glEnableVertexAttribArray(5); glVertexAttribPointer(5, 2, GL_FLOAT, GL_FALSE, st, (void*)40);
    glBindVertexArray(0);
    size_t n = std::max<size_t>(1, md.bones.size());
    std::vector<float> ident(n * 16, 0.0f);
    for (size_t i = 0; i < n; ++i) ident[i * 16] = ident[i * 16 + 5] = ident[i * 16 + 10] = ident[i * 16 + 15] = 1;
    glGenTextures(1, &m.boneTex);
    glBindTexture(GL_TEXTURE_2D, m.boneTex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 4, GLsizei(n), 0, GL_RGBA, GL_FLOAT, ident.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
}

bool Viewer::setCharacter(uint32_t modelFileId, const std::map<int, int>& geosetGroups) {
    clear();
    ModelGl* m = model(modelFileId);
    if (!m) return false;
    body_.mesh = m;
    body_.geosets = characterGeosets(*m->model, geosetGroups);
    setAnim(0);
    return true;
}

void Viewer::setCanvas(uint32_t textureType, int width, int height, const std::vector<Layer>& layers) {
    Canvas& c = body_.canvases[textureType];
    if (c.tex && glReady_) glDeleteTextures(1, &c.tex);
    c = Canvas{width, height, layers, 0};
}

void Viewer::setTexture(uint32_t textureType, uint32_t fileId) { body_.textures[textureType] = fileId; }

bool Viewer::attach(uint32_t attachmentId, uint32_t modelFileId, const std::map<uint32_t, uint32_t>& textures) {
    if (!body_.mesh) return false;
    ModelGl* m = model(modelFileId);
    if (!m) return false;
    Part p;
    p.mesh = m;
    p.attachment = attachmentId;
    p.textures = textures;
    // The item's own standing animation, where it has one: an item keeps parts folded away or faded out in it.
    M2Model& im = *m->model;
    p.seq = im.findSequence(0);
    if (p.seq < 0 && !im.sequences.empty()) p.seq = 0;
    if (p.seq >= 0) im.ensureSequence(p.seq, files_);
    body_.parts.push_back(std::move(p));
    return true;
}

bool Viewer::attachmentMatrix(uint32_t attachmentId, M4& out) const {
    const M2Model& bm = *body_.mesh->model;
    if (attachmentId >= bm.attachmentLookup.size()) return false;
    int idx = bm.attachmentLookup[attachmentId];
    if (idx < 0 || size_t(idx) >= bm.attachments.size()) return false;
    const M2Attachment& at = bm.attachments[size_t(idx)];
    M4 bone = at.bone < body_.mats.size() ? body_.mats[at.bone] : M4();
    out = bone * M4::translation(at.position);
    return true;
}

bool Viewer::addSkinned(uint32_t modelFileId, const std::map<uint32_t, uint32_t>& textures, const std::vector<int>& geosets) {
    if (!body_.mesh) return false;
    ModelGl* m = model(modelFileId);
    if (!m) return false;
    Part p;
    p.mesh = m;
    p.skinned = true;
    p.textures = textures;
    for (int g : geosets) p.geosets.push_back(uint16_t(g));
    // Each of the item's bones is the character's bone of the same name; one the character lacks follows its parent.
    const auto& mine = m->model->bones;
    const auto& theirs = body_.mesh->model->bones;
    p.boneOf.assign(mine.size(), -1);
    for (size_t i = 0; i < mine.size(); ++i) {
        for (size_t k = 0; k < theirs.size(); ++k)
            if (theirs[k].nameCrc == mine[i].nameCrc && mine[i].nameCrc != 0) { p.boneOf[i] = int(k); break; }
        if (p.boneOf[i] < 0 && mine[i].parent >= 0 && size_t(mine[i].parent) < i) p.boneOf[i] = p.boneOf[size_t(mine[i].parent)];
    }
    body_.parts.push_back(std::move(p));
    return true;
}

void Viewer::setAnim(uint16_t animId) {
    if (!body_.mesh) return;
    M2Model& m = *body_.mesh->model;
    int seq = m.findSequence(animId);
    if (seq < 0) seq = m.findSequence(0);
    if (seq < 0 && !m.sequences.empty()) seq = 0;
    if (seq >= 0) m.ensureSequence(seq, files_);
    body_.seq = seq;
    body_.animId = animId;
}

void Viewer::setView(float yaw, float pitch, float zoom, float lift) {
    yaw_ = yaw;
    pitch_ = std::clamp(pitch, -1.2f, 1.2f);
    zoom_ = std::clamp(zoom, 0.5f, 6.0f);
    lift_ = std::clamp(lift, 0.0f, 1.0f);
}

void Viewer::setBackdrop(const float top[3], const float bottom[3]) {
    for (int i = 0; i < 3; ++i) { top_[i] = top[i]; bottom_[i] = bottom[i]; }
}

float Viewer::height() const { return body_.mesh ? body_.high - body_.low : 2; }

// How tall and how wide the character stands in its pose: the model's own bounds reach as far as its animations do, and
// its vertices are in the pose it was built in (arms out), so the geosets that show are measured as they are drawn.
void Viewer::measure() {
    Body& a = body_;
    const M2Model& m = *a.mesh->model;
    float low = 1e9f, high = -1e9f, wide = 0;
    for (const M2Submesh& sm : m.submeshes) {
        if (std::find(a.geosets.begin(), a.geosets.end(), sm.id) == a.geosets.end()) continue;
        for (uint32_t i = sm.indexStart; i < sm.indexStart + sm.indexCount && i < m.indices.size(); i += 3) {
            const M2Vertex& v = m.vertices[m.indices[i]];
            V3 p(v.pos[0], v.pos[1], v.pos[2]), out(0, 0, 0);
            float total = 0;
            for (int k = 0; k < 4; ++k) {
                if (!v.weights[k] || v.bones[k] >= a.mats.size()) continue;
                float w = v.weights[k] / 255.0f;
                out = out + a.mats[v.bones[k]].point(p) * w;
                total += w;
            }
            if (total > 0) p = out * (1.0f / total);
            low = std::min(low, p.z); high = std::max(high, p.z); wide = std::max(wide, std::fabs(p.y));
        }
    }
    if (high > low + 0.2f) { a.low = low; a.high = high; a.wide = std::max(wide * 2, 0.5f); }
    a.measured = true;
}

namespace {

void bonesTexture(unsigned& tex, const std::vector<M4>& mats) {
    if (!tex) {
        glGenTextures(1, &tex);
        glBindTexture(GL_TEXTURE_2D, tex);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 4, GLsizei(mats.size()), 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    }
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 4, GLsizei(mats.size()), GL_RGBA, GL_FLOAT, mats.data());
}

// The eye's directions as a model placed by `world` sees them: toward the eye from the model, across, and up.
void facingIn(const M4& world, const V3& eye, V3 out[3]) {
    V3 origin = world.point(V3(0, 0, 0));
    V3 toEye = (eye - origin).normalized();
    V3 across = V3(0, 0, 1).cross(toEye).normalized();
    V3 up = toEye.cross(across).normalized();
    const V3 worldAxes[3] = {toEye, across, up};
    for (int i = 0; i < 3; ++i) {
        // Into the model's space: against the turn of `world` (its columns, made one long each).
        V3 cx = V3(world.at(0, 0), world.at(1, 0), world.at(2, 0)).normalized();
        V3 cy = V3(world.at(0, 1), world.at(1, 1), world.at(2, 1)).normalized();
        V3 cz = V3(world.at(0, 2), world.at(1, 2), world.at(2, 2)).normalized();
        out[i] = V3(worldAxes[i].dot(cx), worldAxes[i].dot(cy), worldAxes[i].dot(cz));
    }
}

} // namespace

void Viewer::animate(uint32_t now, const V3& eye) {
    Body& a = body_;
    M2Model& m = *a.mesh->model;
    V3 facing[3];
    facingIn(M4(), eye, facing);
    static const bool bind = std::getenv("PORTER_BIND") != nullptr;   // as the model was built, to tell a mesh's faults from its animation's
    if (bind || a.seq < 0 || size_t(a.seq) >= m.sequences.size()) {
        a.mats.assign(std::max<size_t>(1, m.bones.size()), M4());
    } else {
        uint32_t dur = std::max<uint32_t>(1, m.sequences[a.seq].duration);
        m.pose(a.seq, now % dur, now, a.pose);
        m.bonesToMatrices(a.pose, a.mats, facing);
        if (a.mats.empty()) a.mats.push_back(M4());
    }
    bonesTexture(a.boneTex, a.mats);
    for (Part& p : a.parts) {
        M2Model& pm = *p.mesh->model;
        if (p.skinned) {
            p.mats.assign(std::max<size_t>(1, p.boneOf.size()), M4());
            for (size_t i = 0; i < p.boneOf.size(); ++i)
                if (p.boneOf[i] >= 0 && size_t(p.boneOf[i]) < a.mats.size()) p.mats[i] = a.mats[size_t(p.boneOf[i])];
        } else {
            M4 world;
            attachmentMatrix(p.attachment, world);
            facingIn(world, eye, facing);
            if (p.seq >= 0 && size_t(p.seq) < pm.sequences.size()) {
                uint32_t dur = std::max<uint32_t>(1, pm.sequences[size_t(p.seq)].duration);
                pm.pose(p.seq, now % dur, now, p.pose);
            } else {
                p.pose.assign(pm.bones.size(), BonePose());
            }
            pm.bonesToMatrices(p.pose, p.mats, facing);
            if (p.mats.empty()) p.mats.push_back(M4());
        }
        bonesTexture(p.boneTex, p.mats);
    }
}

void Viewer::drawBackdrop() {
    glUseProgram(backProg_);
    glUniform3fv(glGetUniformLocation(backProg_, "uTop"), 1, top_);
    glUniform3fv(glGetUniformLocation(backProg_, "uBottom"), 1, bottom_);
    glBindVertexArray(backVao_);
    glDisable(GL_DEPTH_TEST);
    glDepthMask(GL_FALSE);
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
    glDepthMask(GL_TRUE);
    glEnable(GL_DEPTH_TEST);
    glBindVertexArray(0);
}

void Viewer::drawModel(ModelGl& mg, const M4& world, const std::map<uint32_t, unsigned>* glByType,
                       const std::map<uint32_t, uint32_t>* fileByType, const std::vector<uint16_t>* geosets,
                       unsigned boneTex, int seq, uint32_t t, uint32_t now, bool transparent) {
    const M2Model& m = *mg.model;
    unsigned p = prog_;
    glUniformMatrix4fv(glGetUniformLocation(p, "uWorld"), 1, GL_FALSE, world.m);
    glActiveTexture(GL_TEXTURE1);
    glBindTexture(GL_TEXTURE_2D, boneTex);
    glActiveTexture(GL_TEXTURE0);
    glUniform1i(glGetUniformLocation(p, "uBones"), 1);
    glBindVertexArray(mg.vao);
    static const bool debug = std::getenv("PORTER_DEBUG") != nullptr;
    if (debug && !transparent) {
        std::fprintf(stderr, "model %u: %zu bones, %zu sequences, textures:", m.fileId, m.bones.size(), m.sequences.size());
        for (const M2Texture& t : m.textures) std::fprintf(stderr, " (type %u file %u)", t.type, t.fileId);
        std::fprintf(stderr, "\n");
        for (const M2Batch& b : m.batches) {
            if (b.submesh >= m.submeshes.size()) continue;
            M2Material mat = b.material < m.materials.size() ? m.materials[b.material] : M2Material();
            uint16_t ti = b.textureCombo < m.textureCombos.size() ? m.textureCombos[b.textureCombo] : 0xFFFF;
            std::fprintf(stderr, "  batch geoset %u tris %u blend %u flags %#x shader %#x textures %u first %u prio %d layer %u\n", m.submeshes[b.submesh].id,
                         m.submeshes[b.submesh].indexCount / 3, mat.blend, mat.flags, b.shaderId, b.textureCount, ti, b.priority, b.layer);
        }
    }
    for (const M2Batch& b : m.batches) {
        if (b.submesh >= m.submeshes.size()) continue;
        const M2Submesh& sm = m.submeshes[b.submesh];
        if (!sm.indexCount) continue;
        if (geosets && !geosets->empty() && std::find(geosets->begin(), geosets->end(), sm.id) == geosets->end()) continue;
        static const char* only = std::getenv("PORTER_ONLY");   // one geoset by itself, to find which is at fault
        if (only && glByType && int(sm.id) != std::atoi(only)) continue;
        M2Material mat = b.material < m.materials.size() ? m.materials[b.material] : M2Material();
        bool blend = mat.blend >= 2;
        if (blend != transparent) continue;
        if (b.textureCombo >= m.textureCombos.size()) continue;
        uint16_t ti = m.textureCombos[b.textureCombo];
        if (ti >= m.textures.size()) continue;
        const M2Texture& tex = m.textures[ti];
        unsigned gl = 0;
        if (tex.type == 0) {
            if (tex.fileId) gl = texture(tex.fileId);
        } else {
            if (glByType) { auto it = glByType->find(tex.type); if (it != glByType->end()) gl = it->second; }
            if (!gl && fileByType) {
                auto it = fileByType->find(tex.type);
                // An item's model names its textures by type; one it has no file for takes the item's first.
                if (it == fileByType->end() && !glByType && !fileByType->empty()) it = fileByType->begin();
                if (it != fileByType->end() && it->second) gl = texture(it->second);
            }
        }
        if (!gl) continue;
        float c[4];
        m.evalColor(b.colorIndex == 0xFFFF ? -1 : int(b.colorIndex), seq, t, now, c);
        c[3] *= m.evalWeight(b.weightCombo == 0xFFFF ? -1 : int(b.weightCombo), seq, t, now);
        if (c[3] <= 0.004f) continue;
        // An effect made of two pictures multiplied together (a glow through a moving mask): both, or it is a plain rectangle.
        int two = 0, secondCoords = 0;
        if (b.textureCount >= 2 && mat.blend >= 2 && !(b.shaderId & 0x8000) && (b.shaderId & 7) == 1 && size_t(b.textureCombo) + 1 < m.textureCombos.size()) {
            uint16_t t2 = m.textureCombos[size_t(b.textureCombo) + 1];
            if (t2 < m.textures.size() && m.textures[t2].type == 0 && m.textures[t2].fileId) {
                unsigned second = texture(m.textures[t2].fileId);
                bool otherCoords = size_t(b.coordCombo) + 1 < m.textureCoordCombos.size() && m.textureCoordCombos[size_t(b.coordCombo) + 1] == 1;
                glActiveTexture(GL_TEXTURE2);
                glBindTexture(GL_TEXTURE_2D, second);
                two = 1;
                secondCoords = otherCoords ? 1 : 0;
            }
        }
        // Such an effect is drawn faint: its pictures slide and fade in ways only partly followed here, and a glow that is
        // too weak reads better than a sheet of colour over the character.
        if (two) c[3] *= 0.3f;
        glUniform1i(glGetUniformLocation(p, "uTwo"), two);
        glUniform1i(glGetUniformLocation(p, "uSecondCoords"), secondCoords);
        glUniformMatrix4fv(glGetUniformLocation(p, "uTexMat"), 1, GL_FALSE, m.evalTexTransform(b, 0, seq, t, now).m);
        glUniformMatrix4fv(glGetUniformLocation(p, "uTexMat2"), 1, GL_FALSE, m.evalTexTransform(b, 1, seq, t, now).m);
        glUniform1i(glGetUniformLocation(p, "uTex2"), 2);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, gl);
        glUniform4fv(glGetUniformLocation(p, "uColor"), 1, c);
        glUniform1f(glGetUniformLocation(p, "uAlphaRef"), mat.blend == 1 ? 0.5f : (mat.blend == 0 ? -1.0f : 0.004f));
        glUniform1i(glGetUniformLocation(p, "uOpaque"), mat.blend == 0 ? 1 : 0);
        glUniform1i(glGetUniformLocation(p, "uUnlit"), (mat.flags & 1) ? 1 : 0);
        if (blend) { glEnable(GL_BLEND); blendFor(mat.blend); glDepthMask(GL_FALSE); }
        if (mat.flags & 16) glDepthMask(GL_FALSE);
        glDrawElements(GL_TRIANGLES, GLsizei(sm.indexCount), GL_UNSIGNED_INT, (void*)(size_t(sm.indexStart) * 4));
        if (blend) glDisable(GL_BLEND);
        glDepthMask(GL_TRUE);
    }
    glBindVertexArray(0);
}

void Viewer::render(int width, int height, uint32_t nowMs) {
    if (!glReady_) return;
    glViewport(0, 0, width, height);
    glClearColor(bottom_[0], bottom_[1], bottom_[2], 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glDisable(GL_CULL_FACE);
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);
    drawBackdrop();
    if (!body_.mesh) return;

    // The character's own textures, painted when first drawn (and again after a lost context).
    std::map<uint32_t, unsigned> own;
    for (auto& [type, canvas] : body_.canvases) {
        if (!canvas.tex && canvas.width > 0 && canvas.height > 0) {
            Image img;
            composite(files_, canvas.width, canvas.height, canvas.layers, img);
            canvas.tex = upload(img, false);
        }
        if (canvas.tex) own[type] = canvas.tex;
    }

    const float fov = 30.0f * 3.14159265f / 180.0f;
    float aspect = height ? float(width) / float(height) : 1;
    V3 dir(std::cos(pitch_) * std::cos(yaw_), std::cos(pitch_) * std::sin(yaw_), std::sin(pitch_));
    if (!body_.measured) {
        // The first pose, to know how tall the character stands (the eye isn't placed yet: any will do for it).
        animate(nowMs, dir * 10.0f);
        measure();
    }
    float tall = body_.high - body_.low;
    // Far enough for the whole character, top to bottom and side to side (with what it carries), with a little air.
    float fitTall = (tall * 0.5f) / std::tan(fov * 0.5f);
    float fitWide = (std::max(body_.wide, tall * 0.55f) * 0.5f) / (std::tan(fov * 0.5f) * std::max(aspect, 0.1f));
    float dist = std::max(fitTall, fitWide) * 1.25f / zoom_;
    V3 centre(0, 0, body_.low + tall * lift_);
    V3 eye = centre + dir * dist;
    M4 view = M4::lookAt(eye, centre, V3(0, 0, 1));
    M4 proj = M4::perspective(fov, aspect, 0.05f, 200.0f);
    M4 viewProj = proj * view;

    animate(nowMs, eye);

    glUseProgram(prog_);
    glUniformMatrix4fv(glGetUniformLocation(prog_, "uViewProj"), 1, GL_FALSE, viewProj.m);
    // The light comes from over the viewer's left shoulder, wherever the viewer stands.
    V3 forward = (centre - eye).normalized();
    V3 side = forward.cross(V3(0, 0, 1)).normalized();
    V3 sun = (forward * 0.75f + V3(0, 0, -0.55f) + side * 0.35f).normalized();
    float sunDir[3] = {sun.x, sun.y, sun.z};
    const float sunColor[3] = {0.62f, 0.60f, 0.56f}, ambient[3] = {0.50f, 0.50f, 0.54f};
    glUniform3fv(glGetUniformLocation(prog_, "uSunDir"), 1, sunDir);
    glUniform3fv(glGetUniformLocation(prog_, "uSunColor"), 1, sunColor);
    glUniform3fv(glGetUniformLocation(prog_, "uAmbient"), 1, ambient);
    glUniform1i(glGetUniformLocation(prog_, "uTex"), 0);

    const M2Model& bm = *body_.mesh->model;
    uint32_t dur = std::max<uint32_t>(1, body_.seq >= 0 ? bm.sequences[size_t(body_.seq)].duration : 1);
    M4 world;
    for (int pass = 0; pass < 2; ++pass) {
        bool transparent = pass == 1;
        drawModel(*body_.mesh, world, &own, &body_.textures, &body_.geosets, body_.boneTex, body_.seq, nowMs % dur, nowMs, transparent);
        for (Part& part : body_.parts) {
            if (part.skinned) {
                drawModel(*part.mesh, world, nullptr, &part.textures, &part.geosets, part.boneTex, -1, 0, nowMs, transparent);
                continue;
            }
            M4 at;
            if (!attachmentMatrix(part.attachment, at)) continue;
            const M2Model& pm = *part.mesh->model;
            uint32_t pd = std::max<uint32_t>(1, part.seq >= 0 ? pm.sequences[size_t(part.seq)].duration : 1);
            drawModel(*part.mesh, world * at, nullptr, &part.textures, nullptr, part.boneTex, part.seq, nowMs % pd, nowMs, transparent);
        }
    }
}

} // namespace wc
