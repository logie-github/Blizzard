#include "m2.h"

#include <algorithm>

namespace wc {

namespace {

constexpr size_t kSequenceSize = 64, kBoneSize = 88, kTrackSize = 20, kVertexSize = 48;

M2Track readTrack(const Reader& r, size_t off, uint8_t home = 0) {
    M2Track t;
    t.home = home;
    t.interpolation = r.u16(off);
    t.globalSeq = r.u16(off + 2);
    t.timestamps = readArray(r, off + 4);
    t.values = readArray(r, off + 12);
    return t;
}

float unpackShort(int16_t s) { return float(s < 0 ? s + 32768 : s - 32767) / 32767.0f; }

} // namespace

bool M2Model::dependencies(const std::string& path, const std::vector<uint16_t>& animIds, std::vector<uint32_t>& out,
                           const FileLookup* files) {
    Bytes file;
    if (path.empty() || !readFile(path, file)) return false;
    Reader whole(file);
    if (whole.u32(0) == tag("MD20")) return true;   // an old model: everything by name, nothing to list
    bool found = false;
    auto anims = [&](const Reader& cr, uint32_t size) {
        for (uint32_t i = 0; i + 8 <= size; i += 8) {
            uint16_t anim = cr.u16(i), variation = cr.u16(i + 2);
            uint32_t id = cr.u32(i + 4);
            if (id && variation == 0 && std::find(animIds.begin(), animIds.end(), anim) != animIds.end()) out.push_back(id);
        }
    };
    uint32_t skel = 0;
    for (const Chunk& c : chunks(whole, 0, file.size())) {
        Reader cr(file.data() + c.offset, c.size);
        if (c.tag == tag("MD21")) found = true;
        else if (c.tag == tag("SFID")) { if (c.size >= 4 && cr.u32(0)) out.push_back(cr.u32(0)); }
        else if (c.tag == tag("TXID")) { for (uint32_t i = 0; i + 4 <= c.size; i += 4) if (cr.u32(i)) out.push_back(cr.u32(i)); }
        else if (c.tag == tag("AFID")) anims(cr, c.size);
        else if (c.tag == tag("SKID") && c.size >= 4) skel = cr.u32(0);
    }
    // The skeleton, its animations, and the skeleton it borrows from (two deep at most).
    for (int depth = 0; skel && depth < 3; ++depth) {
        out.push_back(skel);
        std::string sp = files ? (*files)(skel) : std::string();
        Bytes sb;
        if (sp.empty() || !readFile(sp, sb)) break;
        Reader sr(sb);
        uint32_t parent = 0;
        for (const Chunk& c : chunks(sr, 0, sb.size())) {
            Reader cr(sb.data() + c.offset, c.size);
            if (c.tag == tag("AFID")) anims(cr, c.size);
            else if (c.tag == tag("SKPD") && c.size >= 12) parent = cr.u32(8);
        }
        skel = parent;
    }
    return found;
}

bool M2Model::load(uint32_t id, const FileLookup& files) {
    fileId = id;
    std::string path = files(id);
    if (path.empty() || !readFile(path, file_)) return false;
    Reader whole(file_);

    std::vector<uint32_t> skinIds, texIds;
    uint32_t skelId = 0;
    if (whole.u32(0) == tag("MD20")) {
        base_ = 0;
    } else {
        bool found = false;
        for (const Chunk& c : chunks(whole, 0, file_.size())) {
            Reader cr(file_.data() + c.offset, c.size);
            if (c.tag == tag("MD21")) { base_ = c.offset; found = true; }
            else if (c.tag == tag("SFID")) for (uint32_t i = 0; i + 4 <= c.size; i += 4) skinIds.push_back(cr.u32(i));
            else if (c.tag == tag("TXID")) for (uint32_t i = 0; i + 4 <= c.size; i += 4) texIds.push_back(cr.u32(i));
            else if (c.tag == tag("SKID") && c.size >= 4) skelId = cr.u32(0);
            else if (c.tag == tag("AFID"))
                for (uint32_t i = 0; i + 8 <= c.size; i += 8)
                    afid_.push_back({uint32_t(cr.u16(i)) | uint32_t(cr.u16(i + 2)) << 16, cr.u32(i + 4)});
        }
        if (!found) return false;
    }
    Reader r(file_.data() + base_, file_.size() - base_);
    if (r.u32(0) != tag("MD20")) return false;
    flags = r.u32(16);

    M2Array a = readArray(r, 20);
    for (uint32_t i = 0; i < a.count; ++i) globalLoops.push_back(r.u32(a.offset + 4 * i));

    a = readArray(r, 28);
    for (uint32_t i = 0; i < a.count; ++i) {
        size_t o = a.offset + i * kSequenceSize;
        M2Sequence s;
        s.id = r.u16(o); s.variation = r.u16(o + 2); s.duration = r.u32(o + 4);
        s.moveSpeed = r.f32(o + 8); s.flags = r.u32(o + 12);
        s.blendIn = r.u16(o + 28);
        s.variationNext = r.i16(o + 60); s.aliasNext = r.u16(o + 62);
        sequences.push_back(s);
    }

    a = readArray(r, 44);
    for (uint32_t i = 0; i < a.count; ++i) {
        size_t o = a.offset + i * kBoneSize;
        M2Bone b;
        b.keyBoneId = r.i32(o); b.flags = r.u32(o + 4); b.parent = r.i16(o + 8);
        b.nameCrc = r.u32(o + 12);
        b.translation = readTrack(r, o + 16);
        b.rotation = readTrack(r, o + 16 + kTrackSize);
        b.scale = readTrack(r, o + 16 + 2 * kTrackSize);
        b.pivot = V3(r.f32(o + 76), r.f32(o + 80), r.f32(o + 84));
        bones.push_back(b);
    }

    a = readArray(r, 60);
    vertices.resize(a.count);
    for (uint32_t i = 0; i < a.count; ++i) {
        size_t o = a.offset + i * kVertexSize;
        if (!r.has(o, kVertexSize)) { vertices.resize(i); break; }
        std::memcpy(&vertices[i], r.data + o, kVertexSize);
    }

    if (!vertices.empty()) {
        extentMin = extentMax = V3(vertices[0].pos[0], vertices[0].pos[1], vertices[0].pos[2]);
        for (const M2Vertex& v : vertices) {
            extentMin = V3(std::min(extentMin.x, v.pos[0]), std::min(extentMin.y, v.pos[1]), std::min(extentMin.z, v.pos[2]));
            extentMax = V3(std::max(extentMax.x, v.pos[0]), std::max(extentMax.y, v.pos[1]), std::max(extentMax.z, v.pos[2]));
        }
    }

    a = readArray(r, 72);
    for (uint32_t i = 0; i < a.count; ++i) {
        colorRgb.push_back(readTrack(r, a.offset + i * 40));
        colorAlpha.push_back(readTrack(r, a.offset + i * 40 + 20));
    }
    a = readArray(r, 80);
    for (uint32_t i = 0; i < a.count; ++i) {
        M2Texture t;
        t.type = r.u32(a.offset + i * 16);
        t.flags = r.u32(a.offset + i * 16 + 4);
        if (i < texIds.size()) t.fileId = texIds[i];
        textures.push_back(t);
    }
    a = readArray(r, 88);
    for (uint32_t i = 0; i < a.count; ++i) weights.push_back(readTrack(r, a.offset + i * kTrackSize));
    a = readArray(r, 112);
    for (uint32_t i = 0; i < a.count; ++i) materials.push_back({r.u16(a.offset + 4 * i), r.u16(a.offset + 4 * i + 2)});
    a = readArray(r, 128);
    for (uint32_t i = 0; i < a.count; ++i) textureCombos.push_back(r.u16(a.offset + 2 * i));
    a = readArray(r, 96);
    for (uint32_t i = 0; i < a.count; ++i) {
        size_t o = a.offset + i * 3 * kTrackSize;
        textureTransforms.push_back({readTrack(r, o), readTrack(r, o + 2 * kTrackSize)});
    }
    a = readArray(r, 136);
    for (uint32_t i = 0; i < a.count; ++i) textureCoordCombos.push_back(r.i16(a.offset + 2 * i));
    a = readArray(r, 152);
    for (uint32_t i = 0; i < a.count; ++i) textureTransformCombos.push_back(r.i16(a.offset + 2 * i));
    a = readArray(r, 144);
    for (uint32_t i = 0; i < a.count; ++i) weightCombos.push_back(r.u16(a.offset + 2 * i));
    boundsMin = V3(r.f32(160), r.f32(164), r.f32(168));
    boundsMax = V3(r.f32(172), r.f32(176), r.f32(180));
    a = readArray(r, 240);
    for (uint32_t i = 0; i < a.count; ++i) {
        size_t o = a.offset + i * 40;
        attachments.push_back({r.u32(o), r.u16(o + 4), V3(r.f32(o + 8), r.f32(o + 12), r.f32(o + 16))});
    }
    a = readArray(r, 248);
    for (uint32_t i = 0; i < a.count; ++i) attachmentLookup.push_back(r.i16(a.offset + 2 * i));

    // Today's character models keep their skeleton in a file of its own (bones, animations, attachment points), which may
    // borrow what it lacks from a parent skeleton: each part is taken from the nearest file that has it.
    bool haveBones = false, haveSequences = false, haveAttachments = false, haveAnims = !afid_.empty();
    for (int depth = 0; skelId && depth < 3; ++depth) {
        Bytes sb;
        std::string sp = files(skelId);
        if (sp.empty() || !readFile(sp, sb)) return false;
        Reader sr(sb);
        uint32_t parent = 0;
        size_t bonesAt = 0;
        bool bonesHere = false;
        for (const Chunk& c : chunks(sr, 0, sb.size())) {
            Reader cr(sb.data() + c.offset, sb.size() - c.offset);
            if (c.tag == tag("SKS1") && !haveSequences) {
                M2Array loops = readArray(cr, 0), seqs = readArray(cr, 8);
                for (uint32_t i = 0; i < loops.count; ++i) skelLoops_.push_back(cr.u32(loops.offset + 4 * i));
                for (uint32_t i = 0; i < seqs.count; ++i) {
                    size_t o = seqs.offset + i * kSequenceSize;
                    M2Sequence q;
                    q.id = cr.u16(o); q.variation = cr.u16(o + 2); q.duration = cr.u32(o + 4);
                    q.moveSpeed = cr.f32(o + 8); q.flags = cr.u32(o + 12);
                    q.blendIn = cr.u16(o + 28);
                    q.variationNext = cr.i16(o + 60); q.aliasNext = cr.u16(o + 62);
                    sequences.push_back(q);
                }
                haveSequences = seqs.count > 0;
            } else if (c.tag == tag("SKB1") && !haveBones) {
                M2Array bs = readArray(cr, 0);
                for (uint32_t i = 0; i < bs.count; ++i) {
                    size_t o = bs.offset + i * kBoneSize;
                    M2Bone b;
                    b.keyBoneId = cr.i32(o); b.flags = cr.u32(o + 4); b.parent = cr.i16(o + 8);
                    b.nameCrc = cr.u32(o + 12);
                    b.translation = readTrack(cr, o + 16, 1);
                    b.rotation = readTrack(cr, o + 16 + kTrackSize, 1);
                    b.scale = readTrack(cr, o + 16 + 2 * kTrackSize, 1);
                    b.pivot = V3(cr.f32(o + 76), cr.f32(o + 80), cr.f32(o + 84));
                    bones.push_back(b);
                }
                if (bs.count > 0) { haveBones = true; bonesHere = true; bonesAt = c.offset; }
            } else if (c.tag == tag("SKA1") && !haveAttachments) {
                M2Array at = readArray(cr, 0), lk = readArray(cr, 8);
                for (uint32_t i = 0; i < at.count; ++i) {
                    size_t o = at.offset + i * 40;
                    attachments.push_back({cr.u32(o), cr.u16(o + 4), V3(cr.f32(o + 8), cr.f32(o + 12), cr.f32(o + 16))});
                }
                for (uint32_t i = 0; i < lk.count; ++i) attachmentLookup.push_back(cr.i16(lk.offset + 2 * i));
                haveAttachments = at.count > 0;
            } else if (c.tag == tag("AFID") && !haveAnims) {
                Reader ar(sb.data() + c.offset, c.size);
                for (uint32_t i = 0; i + 8 <= c.size; i += 8)
                    afid_.push_back({uint32_t(ar.u16(i)) | uint32_t(ar.u16(i + 2)) << 16, ar.u32(i + 4)});
            } else if (c.tag == tag("SKPD") && c.size >= 12) {
                parent = Reader(sb.data() + c.offset, c.size).u32(8);
            }
        }
        if (!afid_.empty()) haveAnims = true;
        if (bonesHere) { skel_ = std::move(sb); skelBase_ = bonesAt; }
        skelId = parent;
    }

    // The first (most detailed) skin.
    if (skinIds.empty() || !skinIds[0]) return false;
    Bytes skin;
    std::string skinPath = files(skinIds[0]);
    if (skinPath.empty() || !readFile(skinPath, skin)) return false;
    Reader s(skin);
    if (s.u32(0) != tag("SKIN")) return false;
    M2Array lookup = readArray(s, 4), tris = readArray(s, 12), subs = readArray(s, 28), bats = readArray(s, 36);
    indices.reserve(tris.count);
    for (uint32_t i = 0; i < tris.count; ++i) {
        uint16_t local = s.u16(tris.offset + 2 * i);
        uint32_t global = local < lookup.count ? s.u16(lookup.offset + 2 * local) : 0;
        indices.push_back(global < vertices.size() ? global : 0);
    }
    for (uint32_t i = 0; i < subs.count; ++i) {
        size_t o = subs.offset + i * 48;
        M2Submesh m;
        m.id = s.u16(o);
        m.indexStart = s.u16(o + 8) + (uint32_t(s.u16(o + 2)) << 16);
        m.indexCount = s.u16(o + 10);
        m.sortCenter = V3(s.f32(o + 32), s.f32(o + 36), s.f32(o + 40));
        if (m.indexStart + m.indexCount > indices.size()) m.indexCount = 0;
        submeshes.push_back(m);
    }
    for (uint32_t i = 0; i < bats.count; ++i) {
        size_t o = bats.offset + i * 24;
        M2Batch b;
        b.flags = s.u8(o); b.priority = int8_t(s.u8(o + 1)); b.shaderId = s.u16(o + 2);
        b.submesh = s.u16(o + 4); b.colorIndex = s.u16(o + 8); b.material = s.u16(o + 10);
        b.layer = s.u16(o + 12); b.textureCount = s.u16(o + 14); b.textureCombo = s.u16(o + 16);
        b.coordCombo = s.u16(o + 18);
        b.transformCombo = s.u16(o + 22);
        b.weightCombo = s.u16(o + 20);
        batches.push_back(b);
    }
    return true;
}

int M2Model::findSequence(uint16_t animId) const {
    for (size_t i = 0; i < sequences.size(); ++i)
        if (sequences[i].id == animId && sequences[i].variation == 0) return int(i);
    for (size_t i = 0; i < sequences.size(); ++i)
        if (sequences[i].id == animId) return int(i);
    return -1;
}

int M2Model::dataSequence(int seq) const {
    int guard = 0;
    while (seq >= 0 && size_t(seq) < sequences.size() && (sequences[seq].flags & 0x40) && guard++ < 16)
        seq = sequences[seq].aliasNext;
    return seq;
}

bool M2Model::sequenceReady(int seq) const {
    int d = dataSequence(seq);
    if (d < 0 || size_t(d) >= sequences.size()) return false;
    return (sequences[d].flags & 0x20) || animFiles_.count(d);
}

void M2Model::ensureSequence(int seq, const FileLookup& files) {
    int d = dataSequence(seq);
    if (d < 0 || size_t(d) >= sequences.size() || sequenceReady(d)) return;
    uint32_t key = uint32_t(sequences[d].id) | uint32_t(sequences[d].variation) << 16;
    for (auto& e : afid_) {
        if (e.first != key || !e.second) continue;
        std::string path = files(e.second);
        Bytes b;
        if (path.empty() || !readFile(path, b)) return;
        // An old animation file is the model's keys from its start; today's is in chunks: the model's own keys, and the
        // skeleton's bones'.
        size_t modelOff = 0, skelOff = 0;
        Reader ar(b);
        if (ar.u32(0) == tag("AFM2") || ar.u32(0) == tag("AFSA") || ar.u32(0) == tag("AFSB")) {
            for (const Chunk& c : chunks(ar, 0, b.size())) {
                if (c.tag == tag("AFM2")) modelOff = c.offset;
                else if (c.tag == tag("AFSB")) skelOff = c.offset;
            }
            if (!skelOff) skelOff = modelOff;
            if (!modelOff) modelOff = skelOff;
        }
        animBase_[d] = modelOff;
        animSkelBase_[d] = skelOff;
        animFiles_[d] = std::move(b);
        return;
    }
}

bool M2Model::keys(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs,
                   const uint8_t*& data, size_t& dataSize, uint32_t& tsOff, uint32_t& valOff,
                   uint32_t& count, uint32_t& time) const {
    // A bone of a model with a skeleton file has its keys there; everything else in the model itself.
    bool inSkel = t.home == 1 && !skel_.empty();
    Reader r = inSkel ? Reader(skel_.data() + skelBase_, skel_.size() - skelBase_) : Reader(file_.data() + base_, file_.size() - base_);
    uint32_t idx;
    bool inModel;
    if (t.globalSeq != 0xFFFF) {
        idx = 0; inModel = true;
        const std::vector<uint32_t>& loops = inSkel ? skelLoops_ : globalLoops;
        uint32_t loop = t.globalSeq < loops.size() ? loops[t.globalSeq] : 0;
        time = loop ? globalMs % loop : 0;
    } else {
        int d = dataSequence(seq);
        if (d < 0 || size_t(d) >= sequences.size()) return false;
        idx = uint32_t(d);
        inModel = (sequences[d].flags & 0x20) != 0;
        time = timeMs;
    }
    if (idx >= t.timestamps.count || idx >= t.values.count) return false;
    M2Array ts = readArray(r, t.timestamps.offset + 8 * idx), vs = readArray(r, t.values.offset + 8 * idx);
    count = std::min(ts.count, vs.count);
    if (!count) return false;
    if (inModel) {
        data = r.data; dataSize = r.size; tsOff = ts.offset; valOff = vs.offset;
    } else {
        auto it = animFiles_.find(int(idx));
        if (it == animFiles_.end()) return false;
        size_t b = inSkel ? animSkelBase_.at(int(idx)) : animBase_.at(int(idx));
        data = it->second.data() + b; dataSize = it->second.size() - b;
        tsOff = ts.offset; valOff = vs.offset;
    }
    return true;
}

namespace {

// The key pair around `time` and how far between them it is.
void bracket(const Reader& r, uint32_t tsOff, uint32_t count, uint32_t time, uint32_t& a, uint32_t& b, float& f) {
    uint32_t last = count - 1;
    if (count == 1 || time <= r.u32(tsOff)) { a = b = 0; f = 0; return; }
    if (time >= r.u32(tsOff + 4 * last)) { a = b = last; f = 0; return; }
    uint32_t lo = 0, hi = last;
    while (hi - lo > 1) {
        uint32_t mid = (lo + hi) / 2;
        if (r.u32(tsOff + 4 * mid) <= time) lo = mid; else hi = mid;
    }
    a = lo; b = hi;
    uint32_t t0 = r.u32(tsOff + 4 * a), t1 = r.u32(tsOff + 4 * b);
    f = t1 > t0 ? float(time - t0) / float(t1 - t0) : 0;
}

} // namespace

V3 M2Model::evalV3(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs, V3 def) const {
    const uint8_t* d; size_t n; uint32_t tsOff, valOff, count, time;
    if (!keys(t, seq, timeMs, globalMs, d, n, tsOff, valOff, count, time)) return def;
    Reader r(d, n);
    uint32_t a, b; float f;
    bracket(r, tsOff, count, time, a, b, f);
    size_t stride = t.interpolation >= 2 ? 36 : 12;
    auto at = [&](uint32_t k) { size_t o = valOff + k * stride; return V3(r.f32(o), r.f32(o + 4), r.f32(o + 8)); };
    return t.interpolation == 0 ? at(a) : lerp(at(a), at(b), f);
}

Quat M2Model::evalQuat(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs) const {
    const uint8_t* d; size_t n; uint32_t tsOff, valOff, count, time;
    if (!keys(t, seq, timeMs, globalMs, d, n, tsOff, valOff, count, time)) return Quat();
    Reader r(d, n);
    uint32_t a, b; float f;
    bracket(r, tsOff, count, time, a, b, f);
    size_t stride = t.interpolation >= 2 ? 24 : 8;
    auto at = [&](uint32_t k) {
        size_t o = valOff + k * stride;
        return Quat(unpackShort(r.i16(o)), unpackShort(r.i16(o + 2)), unpackShort(r.i16(o + 4)), unpackShort(r.i16(o + 6))).normalized();
    };
    return t.interpolation == 0 ? at(a) : nlerp(at(a), at(b), f);
}

float M2Model::evalShort(const M2Track& t, int seq, uint32_t timeMs, uint32_t globalMs, float def) const {
    const uint8_t* d; size_t n; uint32_t tsOff, valOff, count, time;
    if (!keys(t, seq, timeMs, globalMs, d, n, tsOff, valOff, count, time)) return def;
    Reader r(d, n);
    uint32_t a, b; float f;
    bracket(r, tsOff, count, time, a, b, f);
    size_t stride = t.interpolation >= 2 ? 6 : 2;
    float va = r.i16(valOff + a * stride) / 32767.0f, vb = r.i16(valOff + b * stride) / 32767.0f;
    return t.interpolation == 0 ? va : va + (vb - va) * f;
}

void M2Model::pose(int seq, uint32_t timeMs, uint32_t globalMs, std::vector<BonePose>& out) const {
    out.resize(bones.size());
    for (size_t i = 0; i < bones.size(); ++i) {
        const M2Bone& b = bones[i];
        out[i].t = evalV3(b.translation, seq, timeMs, globalMs, V3(0, 0, 0));
        out[i].r = evalQuat(b.rotation, seq, timeMs, globalMs);
        out[i].s = evalV3(b.scale, seq, timeMs, globalMs, V3(1, 1, 1));
    }
}

void M2Model::bonesToMatrices(const std::vector<BonePose>& poses, std::vector<M4>& out, const V3* facing) const {
    size_t n = bones.size();
    out.assign(n, M4());
    std::vector<uint8_t> done(n, 0);
    // Parents normally come first; the loop repeats for any that don't.
    for (int pass = 0; pass < 8; ++pass) {
        bool all = true;
        for (size_t i = 0; i < n; ++i) {
            if (done[i]) continue;
            int p = bones[i].parent;
            if (p >= 0 && size_t(p) < n && !done[p]) { all = false; continue; }
            const M2Bone& b = bones[i];
            const BonePose& q = i < poses.size() ? poses[i] : BonePose();
            M4 local = M4::translation(b.pivot) * M4::translation(q.t) * M4::rotation(q.r) *
                       M4::scaling(q.s) * M4::translation(b.pivot * -1.0f);
            out[i] = (p >= 0 && size_t(p) < n) ? out[p] * local : local;
            if (facing && (b.flags & 0x8)) {
                // A billboard: where the bone is and how big, but turned to the eye (its x toward it, y across, z up).
                M4& m = out[i];
                V3 at = m.point(b.pivot);
                float sx = V3(m.at(0, 0), m.at(1, 0), m.at(2, 0)).length();
                float sy = V3(m.at(0, 1), m.at(1, 1), m.at(2, 1)).length();
                float sz = V3(m.at(0, 2), m.at(1, 2), m.at(2, 2)).length();
                M4 turn;
                for (int r = 0; r < 3; ++r) {
                    float fx = r == 0 ? facing[0].x : r == 1 ? facing[0].y : facing[0].z;
                    float fy = r == 0 ? facing[1].x : r == 1 ? facing[1].y : facing[1].z;
                    float fz = r == 0 ? facing[2].x : r == 1 ? facing[2].y : facing[2].z;
                    turn.at(r, 0) = fx * sx; turn.at(r, 1) = fy * sy; turn.at(r, 2) = fz * sz;
                }
                m = M4::translation(at) * turn * M4::translation(b.pivot * -1.0f);
            }
            done[i] = 1;
        }
        if (all) break;
    }
}

float M2Model::evalWeight(int index, int seq, uint32_t timeMs, uint32_t globalMs) const {
    if (index < 0 || size_t(index) >= weightCombos.size()) return 1;
    uint16_t w = weightCombos[index];
    if (w >= weights.size()) return 1;
    return std::clamp(evalShort(weights[w], seq, timeMs, globalMs, 1), 0.0f, 1.0f);
}

M4 M2Model::evalTexTransform(const M2Batch& b, int which, int seq, uint32_t timeMs, uint32_t globalMs) const {
    size_t at = size_t(b.transformCombo) + size_t(which);
    if (b.transformCombo == 0xFFFF || at >= textureTransformCombos.size()) return M4();
    int16_t index = textureTransformCombos[at];
    if (index < 0 || size_t(index) >= textureTransforms.size()) return M4();
    const TexTransform& t = textureTransforms[size_t(index)];
    V3 move = evalV3(t.translation, seq, timeMs, globalMs, V3(0, 0, 0));
    V3 size = evalV3(t.scale, seq, timeMs, globalMs, V3(1, 1, 1));
    // Stretched about the middle of the picture, then slid.
    const V3 middle(0.5f, 0.5f, 0);
    return M4::translation(middle + move) * M4::scaling(size) * M4::translation(middle * -1.0f);
}

void M2Model::evalColor(int index, int seq, uint32_t timeMs, uint32_t globalMs, float rgba[4]) const {
    rgba[0] = rgba[1] = rgba[2] = rgba[3] = 1;
    if (index < 0 || size_t(index) >= colorRgb.size()) return;
    V3 c = evalV3(colorRgb[index], seq, timeMs, globalMs, V3(1, 1, 1));
    rgba[0] = c.x; rgba[1] = c.y; rgba[2] = c.z;
    rgba[3] = std::clamp(evalShort(colorAlpha[index], seq, timeMs, globalMs, 1), 0.0f, 1.0f);
}

} // namespace wc
