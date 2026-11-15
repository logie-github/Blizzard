// Draws the character porter's preview on a desktop, without a window, to check the viewer against the game's own files
// (porter/README.md, "The harness"). Two uses:
//
//   harness --deps MODEL_FILE [ANIM,ANIM,...]     prints the ids of the files that model's file names (its skin, its own
//                                                 textures, its skeleton, the animations asked for); asked again once
//                                                 those are beside it, it names what the skeleton names
//   harness COMMANDS                              reads commands, one a line:
//
//     files DIR                                   the downloaded files, each named by its id
//     character MODEL [G=V,G=V,...]               the race's model and its geoset groups
//     canvas TYPE WIDTH HEIGHT                    one of its textures painted from the layers that follow, until `end`
//       layer FILE X Y WIDTH HEIGHT BLEND
//     end
//     texture TYPE FILE                           one of its textures as one file
//     attach ATTACHMENT MODEL [T=F,T=F,...]       an item on an attachment point
//     skinned MODEL [T=F,...|-] [ID,ID,...]       an item that moves with the skeleton, and the geosets of it to show
//     anim ID
//     view YAW PITCH ZOOM LIFT                    degrees, degrees, 1 = whole character, 0..1 up the character
//     paint TYPE OUT.ppm                          writes a painted texture by itself
//     render OUT.ppm WIDTH HEIGHT TIME_MS
//
// Build: porter/harness/build.sh (EGL and OpenGL ES 3 from Mesa).
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl3.h>

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <vector>

#include "../engine/viewer.h"

using namespace wc;

static std::vector<std::string> split(const std::string& s, char c) {
    std::vector<std::string> out;
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, c)) if (!item.empty()) out.push_back(item);
    return out;
}

static std::map<uint32_t, uint32_t> pairs(const std::string& text) {
    std::map<uint32_t, uint32_t> out;
    if (text == "-") return out;
    for (auto& kv : split(text, ',')) {
        auto p = split(kv, '=');
        if (p.size() == 2) out[uint32_t(std::strtoul(p[0].c_str(), nullptr, 10))] = uint32_t(std::strtoul(p[1].c_str(), nullptr, 10));
    }
    return out;
}

static void writePpm(const std::string& path, int w, int h, const uint8_t* rgba, bool flip) {
    FILE* f = std::fopen(path.c_str(), "wb");
    if (!f) { std::fprintf(stderr, "can't write %s\n", path.c_str()); return; }
    std::fprintf(f, "P6\n%d %d\n255\n", w, h);
    for (int y = 0; y < h; ++y) {
        int row = flip ? h - 1 - y : y;
        for (int x = 0; x < w; ++x) std::fwrite(&rgba[(size_t(row) * w + x) * 4], 1, 3, f);
    }
    std::fclose(f);
}

int main(int argc, char** argv) {
    if (argc >= 3 && std::string(argv[1]) == "--deps") {
        std::vector<uint16_t> anims;
        if (argc >= 4) for (auto& a : split(argv[3], ',')) anims.push_back(uint16_t(std::atoi(a.c_str())));
        std::vector<uint32_t> out;
        // The model's folder holds the other files by their ids (its skeleton, once fetched, names more).
        std::string model = argv[2];
        std::string folder = model.substr(0, model.find_last_of('/'));
        FileLookup beside = [&](uint32_t id) {
            std::string p = folder + "/" + std::to_string(id);
            struct stat st;
            return stat(p.c_str(), &st) == 0 ? p : std::string();
        };
        if (!M2Model::dependencies(model, anims, out, &beside)) { std::fprintf(stderr, "not a model: %s\n", argv[2]); return 1; }
        for (uint32_t id : out) std::printf("%u\n", id);
        return 0;
    }
    if (argc < 2) { std::fprintf(stderr, "usage: harness COMMANDS | harness --deps MODEL [ANIMS]\n"); return 2; }

    EGLDisplay dpy = EGL_NO_DISPLAY;
    auto getPlatformDisplay = (PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
    if (getPlatformDisplay) dpy = getPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA, EGL_DEFAULT_DISPLAY, nullptr);
    if (dpy == EGL_NO_DISPLAY) dpy = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    if (!eglInitialize(dpy, nullptr, nullptr)) { std::fprintf(stderr, "eglInitialize failed\n"); return 1; }
    eglBindAPI(EGL_OPENGL_ES_API);
    EGLint cfgAttr[] = {EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT, EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_NONE};
    EGLConfig cfg; EGLint n = 0;
    eglChooseConfig(dpy, cfgAttr, &cfg, 1, &n);
    EGLint ctxAttr[] = {EGL_CONTEXT_MAJOR_VERSION, 3, EGL_NONE};
    EGLContext ctx = eglCreateContext(dpy, n ? cfg : nullptr, EGL_NO_CONTEXT, ctxAttr);
    if (ctx == EGL_NO_CONTEXT || !eglMakeCurrent(dpy, EGL_NO_SURFACE, EGL_NO_SURFACE, ctx)) {
        std::fprintf(stderr, "no GLES 3 context\n"); return 1;
    }
    std::fprintf(stderr, "GL: %s / %s\n", glGetString(GL_RENDERER), glGetString(GL_VERSION));

    std::string dir;
    FileLookup files = [&](uint32_t id) {
        std::string p = dir + "/" + std::to_string(id);
        struct stat st;
        return stat(p.c_str(), &st) == 0 ? p : std::string();
    };
    Viewer viewer(files);
    viewer.initGl();
    std::map<uint32_t, std::pair<std::pair<int, int>, std::vector<Layer>>> canvases;

    std::ifstream in(argv[1]);
    std::string line;
    uint32_t canvasType = 0;
    bool inCanvas = false;
    while (std::getline(in, line)) {
        std::istringstream ss(line);
        std::string cmd;
        ss >> cmd;
        if (cmd.empty() || cmd[0] == '#') continue;
        if (cmd == "files") ss >> dir;
        else if (cmd == "character") {
            uint32_t model; std::string geo;
            ss >> model >> geo;
            std::map<int, int> groups;
            for (auto& [k, v] : pairs(geo)) groups[int(k)] = int(v);
            bool ok = viewer.setCharacter(model, groups);
            std::fprintf(stderr, "character %u: %s (%.2f tall)\n", model, ok ? "ok" : "FAILED", viewer.height());
        } else if (cmd == "canvas") {
            int w, h;
            ss >> canvasType >> w >> h;
            canvases[canvasType] = {{w, h}, {}};
            inCanvas = true;
        } else if (cmd == "layer" && inCanvas) {
            Layer l;
            ss >> l.fileId >> l.x >> l.y >> l.width >> l.height >> l.blend;
            canvases[canvasType].second.push_back(l);
        } else if (cmd == "end" && inCanvas) {
            auto& c = canvases[canvasType];
            viewer.setCanvas(canvasType, c.first.first, c.first.second, c.second);
            inCanvas = false;
        } else if (cmd == "texture") {
            uint32_t type, file;
            ss >> type >> file;
            viewer.setTexture(type, file);
        } else if (cmd == "attach") {
            uint32_t att, model; std::string tex = "-";
            ss >> att >> model >> tex;
            bool ok = viewer.attach(att, model, pairs(tex));
            std::fprintf(stderr, "attach %u at %u: %s\n", model, att, ok ? "ok" : "FAILED");
        } else if (cmd == "skinned") {
            uint32_t model; std::string tex = "-", geo;
            ss >> model >> tex >> geo;
            std::vector<int> ids;
            for (auto& g : split(geo, ',')) ids.push_back(std::atoi(g.c_str()));
            bool ok = viewer.addSkinned(model, pairs(tex), ids);
            std::fprintf(stderr, "skinned %u: %s\n", model, ok ? "ok" : "FAILED");
        } else if (cmd == "anim") {
            int anim; ss >> anim; viewer.setAnim(uint16_t(anim));
        } else if (cmd == "view") {
            float yaw, pitch, zoom, lift;
            ss >> yaw >> pitch >> zoom >> lift;
            const float rad = 3.14159265f / 180.0f;
            viewer.setView(yaw * rad, pitch * rad, zoom, lift);
        } else if (cmd == "paint") {
            uint32_t type; std::string out;
            ss >> type >> out;
            auto it = canvases.find(type);
            if (it == canvases.end()) { std::fprintf(stderr, "no canvas %u\n", type); continue; }
            Image img;
            composite(files, it->second.first.first, it->second.first.second, it->second.second, img);
            writePpm(out, img.width, img.height, img.rgba.data(), false);
            std::fprintf(stderr, "painted %s (%dx%d, %zu layers)\n", out.c_str(), img.width, img.height, it->second.second.size());
        } else if (cmd == "render") {
            std::string out; int w, h; uint32_t t;
            ss >> out >> w >> h >> t;
            unsigned fbo, color, depth;
            glGenFramebuffers(1, &fbo); glBindFramebuffer(GL_FRAMEBUFFER, fbo);
            glGenRenderbuffers(1, &color); glBindRenderbuffer(GL_RENDERBUFFER, color);
            glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, w, h);
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color);
            glGenRenderbuffers(1, &depth); glBindRenderbuffer(GL_RENDERBUFFER, depth);
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, w, h);
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth);
            viewer.render(w, h, t);
            std::vector<uint8_t> px(size_t(w) * h * 4);
            glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, px.data());
            writePpm(out, w, h, px.data(), true);
            std::fprintf(stderr, "wrote %s (GL error %#x)\n", out.c_str(), glGetError());
            glDeleteFramebuffers(1, &fbo);
            glDeleteRenderbuffers(1, &color);
            glDeleteRenderbuffers(1, &depth);
        }
    }
    return 0;
}
