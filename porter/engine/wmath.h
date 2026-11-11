// Small vector, quaternion and matrix helpers for the renderer. WoW's own axes are kept
// throughout: x and y across the ground, z up. Matrices are column-major, as OpenGL takes them.
#pragma once

#include <cmath>
#include <cstring>

namespace wc {

struct V3 {
    float x = 0, y = 0, z = 0;
    V3() = default;
    V3(float x, float y, float z) : x(x), y(y), z(z) {}
    V3 operator+(const V3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    V3 operator-(const V3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    V3 operator*(float s) const { return {x * s, y * s, z * s}; }
    float dot(const V3& o) const { return x * o.x + y * o.y + z * o.z; }
    V3 cross(const V3& o) const { return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x}; }
    float length() const { return std::sqrt(dot(*this)); }
    V3 normalized() const { float l = length(); return l > 1e-8f ? *this * (1.0f / l) : V3(0, 0, 1); }
};

inline V3 lerp(const V3& a, const V3& b, float t) { return a + (b - a) * t; }

struct Quat {
    float x = 0, y = 0, z = 0, w = 1;
    Quat() = default;
    Quat(float x, float y, float z, float w) : x(x), y(y), z(z), w(w) {}
    Quat normalized() const {
        float l = std::sqrt(x * x + y * y + z * z + w * w);
        return l > 1e-8f ? Quat(x / l, y / l, z / l, w / l) : Quat();
    }
};

// Normalised linear blend along the short arc: close enough to a slerp between neighbouring keys.
inline Quat nlerp(const Quat& a, Quat b, float t) {
    float d = a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w;
    if (d < 0) b = Quat(-b.x, -b.y, -b.z, -b.w);
    return Quat(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, a.w + (b.w - a.w) * t).normalized();
}

struct M4 {
    float m[16];
    M4() { identity(); }
    void identity() { std::memset(m, 0, sizeof m); m[0] = m[5] = m[10] = m[15] = 1; }
    float& at(int row, int col) { return m[col * 4 + row]; }
    float at(int row, int col) const { return m[col * 4 + row]; }

    M4 operator*(const M4& o) const {
        M4 r;
        for (int c = 0; c < 4; ++c)
            for (int rr = 0; rr < 4; ++rr) {
                float s = 0;
                for (int k = 0; k < 4; ++k) s += at(rr, k) * o.at(k, c);
                r.m[c * 4 + rr] = s;
            }
        return r;
    }
    V3 point(const V3& p) const {
        return {at(0, 0) * p.x + at(0, 1) * p.y + at(0, 2) * p.z + at(0, 3),
                at(1, 0) * p.x + at(1, 1) * p.y + at(1, 2) * p.z + at(1, 3),
                at(2, 0) * p.x + at(2, 1) * p.y + at(2, 2) * p.z + at(2, 3)};
    }

    static M4 translation(const V3& t) { M4 r; r.m[12] = t.x; r.m[13] = t.y; r.m[14] = t.z; return r; }
    static M4 scaling(const V3& s) { M4 r; r.m[0] = s.x; r.m[5] = s.y; r.m[10] = s.z; return r; }
    static M4 rotation(const Quat& q) {
        M4 r;
        float x = q.x, y = q.y, z = q.z, w = q.w;
        r.at(0, 0) = 1 - 2 * (y * y + z * z); r.at(0, 1) = 2 * (x * y - z * w);     r.at(0, 2) = 2 * (x * z + y * w);
        r.at(1, 0) = 2 * (x * y + z * w);     r.at(1, 1) = 1 - 2 * (x * x + z * z); r.at(1, 2) = 2 * (y * z - x * w);
        r.at(2, 0) = 2 * (x * z - y * w);     r.at(2, 1) = 2 * (y * z + x * w);     r.at(2, 2) = 1 - 2 * (x * x + y * y);
        return r;
    }
    static M4 rotationZ(float a) {
        M4 r; float c = std::cos(a), s = std::sin(a);
        r.at(0, 0) = c; r.at(0, 1) = -s; r.at(1, 0) = s; r.at(1, 1) = c;
        return r;
    }
    static M4 perspective(float fovY, float aspect, float zn, float zf) {
        M4 r; std::memset(r.m, 0, sizeof r.m);
        float f = 1.0f / std::tan(fovY * 0.5f);
        r.at(0, 0) = f / aspect; r.at(1, 1) = f;
        r.at(2, 2) = (zf + zn) / (zn - zf); r.at(2, 3) = 2 * zf * zn / (zn - zf);
        r.at(3, 2) = -1;
        return r;
    }
    static M4 lookAt(const V3& eye, const V3& target, const V3& up) {
        V3 f = (target - eye).normalized();
        V3 s = f.cross(up).normalized();
        V3 u = s.cross(f);
        M4 r;
        r.at(0, 0) = s.x; r.at(0, 1) = s.y; r.at(0, 2) = s.z; r.at(0, 3) = -s.dot(eye);
        r.at(1, 0) = u.x; r.at(1, 1) = u.y; r.at(1, 2) = u.z; r.at(1, 3) = -u.dot(eye);
        r.at(2, 0) = -f.x; r.at(2, 1) = -f.y; r.at(2, 2) = -f.z; r.at(2, 3) = f.dot(eye);
        return r;
    }
};

} // namespace wc
