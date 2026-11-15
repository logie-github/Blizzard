// The app's door into the character preview (com.logie.blizz.porter.view.Native): one Viewer a handle. Every call but
// create runs on the preview's GL thread. The game's files are read from the folder given to create, each named by its id.
#include <jni.h>
#include <sys/stat.h>

#include <map>
#include <string>
#include <vector>

#include "viewer.h"

using namespace wc;

namespace {

Viewer* viewer(jlong h) { return reinterpret_cast<Viewer*>(h); }

std::string str(JNIEnv* env, jstring s) {
    const char* c = env->GetStringUTFChars(s, nullptr);
    std::string out(c ? c : "");
    if (c) env->ReleaseStringUTFChars(s, c);
    return out;
}

std::vector<int> ints(JNIEnv* env, jintArray a) {
    std::vector<int> out;
    if (!a) return out;
    jsize n = env->GetArrayLength(a);
    out.resize(size_t(n));
    if (n) env->GetIntArrayRegion(a, 0, n, out.data());
    return out;
}

std::map<uint32_t, uint32_t> pairs(JNIEnv* env, jintArray keys, jintArray values) {
    std::map<uint32_t, uint32_t> m;
    auto k = ints(env, keys), v = ints(env, values);
    for (size_t i = 0; i < k.size() && i < v.size(); ++i) m[uint32_t(k[i])] = uint32_t(v[i]);
    return m;
}

} // namespace

#define FN(name) Java_com_logie_blizz_porter_view_Native_##name

extern "C" {

JNIEXPORT jlong JNICALL FN(create)(JNIEnv* env, jclass, jstring dir) {
    std::string base = str(env, dir);
    auto* v = new Viewer([base](uint32_t id) {
        std::string p = base + "/" + std::to_string(id);
        struct stat st;
        return stat(p.c_str(), &st) == 0 && st.st_size > 0 ? p : std::string();
    });
    return reinterpret_cast<jlong>(v);
}

JNIEXPORT void JNICALL FN(destroy)(JNIEnv*, jclass, jlong h) { delete viewer(h); }

JNIEXPORT void JNICALL FN(initGl)(JNIEnv*, jclass, jlong h) { viewer(h)->initGl(); }

JNIEXPORT void JNICALL FN(releaseGl)(JNIEnv*, jclass, jlong h) { viewer(h)->releaseGl(); }

JNIEXPORT void JNICALL FN(clear)(JNIEnv*, jclass, jlong h) { viewer(h)->clear(); }

JNIEXPORT jboolean JNICALL FN(setCharacter)(JNIEnv* env, jclass, jlong h, jint model, jintArray groupKeys, jintArray groupValues) {
    std::map<int, int> groups;
    for (auto& [k, v] : pairs(env, groupKeys, groupValues)) groups[int(k)] = int(v);
    return viewer(h)->setCharacter(uint32_t(model), groups) ? JNI_TRUE : JNI_FALSE;
}

// layers: six numbers each (file, x, y, width, height, blend).
JNIEXPORT void JNICALL FN(setCanvas)(JNIEnv* env, jclass, jlong h, jint type, jint width, jint height, jintArray layers) {
    std::vector<int> l = ints(env, layers);
    std::vector<Layer> out;
    for (size_t i = 0; i + 5 < l.size(); i += 6) out.push_back(Layer{uint32_t(l[i]), l[i + 1], l[i + 2], l[i + 3], l[i + 4], l[i + 5]});
    viewer(h)->setCanvas(uint32_t(type), width, height, out);
}

JNIEXPORT void JNICALL FN(setTexture)(JNIEnv*, jclass, jlong h, jint type, jint file) { viewer(h)->setTexture(uint32_t(type), uint32_t(file)); }

JNIEXPORT jboolean JNICALL FN(attach)(JNIEnv* env, jclass, jlong h, jint attachment, jint model, jintArray texKeys, jintArray texValues) {
    return viewer(h)->attach(uint32_t(attachment), uint32_t(model), pairs(env, texKeys, texValues)) ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jboolean JNICALL FN(addSkinned)(JNIEnv* env, jclass, jlong h, jint model, jintArray texKeys, jintArray texValues, jintArray geosets) {
    return viewer(h)->addSkinned(uint32_t(model), pairs(env, texKeys, texValues), ints(env, geosets)) ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT void JNICALL FN(setAnim)(JNIEnv*, jclass, jlong h, jint anim) { viewer(h)->setAnim(uint16_t(anim)); }

JNIEXPORT void JNICALL FN(setView)(JNIEnv*, jclass, jlong h, jfloat yaw, jfloat pitch, jfloat zoom, jfloat lift) {
    viewer(h)->setView(yaw, pitch, zoom, lift);
}

JNIEXPORT void JNICALL FN(setBackdrop)(JNIEnv* env, jclass, jlong h, jfloatArray top, jfloatArray bottom) {
    float t[3] = {0, 0, 0}, b[3] = {0, 0, 0};
    if (top && env->GetArrayLength(top) >= 3) env->GetFloatArrayRegion(top, 0, 3, t);
    if (bottom && env->GetArrayLength(bottom) >= 3) env->GetFloatArrayRegion(bottom, 0, 3, b);
    viewer(h)->setBackdrop(t, b);
}

JNIEXPORT void JNICALL FN(render)(JNIEnv*, jclass, jlong h, jint width, jint height, jlong nowMs) {
    viewer(h)->render(width, height, uint32_t(nowMs));
}

JNIEXPORT jboolean JNICALL FN(hasCharacter)(JNIEnv*, jclass, jlong h) { return viewer(h)->hasCharacter() ? JNI_TRUE : JNI_FALSE; }

} // extern "C"
