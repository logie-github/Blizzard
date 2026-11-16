package com.logie.blizz.forevernew.tact

/** Bob Jenkins' lookup3 `hashlittle` and `hashlittle2`, which Blizzard's local storage index and data headers are guarded with. Checked against the C original (CascLib's lookup3.c) in the tests. */
object Jenkins {
    private fun rot(x: Int, k: Int) = (x shl k) or (x ushr (32 - k))

    private class State(var a: Int, var b: Int, var c: Int) {
        fun mix() {
            a -= c; a = a xor rot(c, 4); c += b
            b -= a; b = b xor rot(a, 6); a += c
            c -= b; c = c xor rot(b, 8); b += a
            a -= c; a = a xor rot(c, 16); c += b
            b -= a; b = b xor rot(a, 19); a += c
            c -= b; c = c xor rot(b, 4); b += a
        }
        fun fin() {
            c = c xor b; c -= rot(b, 14)
            a = a xor c; a -= rot(c, 11)
            b = b xor a; b -= rot(a, 25)
            c = c xor b; c -= rot(b, 16)
            a = a xor c; a -= rot(c, 4)
            b = b xor a; b -= rot(a, 14)
            c = c xor b; c -= rot(b, 24)
        }
    }

    private fun u(d: ByteArray, i: Int) = d[i].toInt() and 0xff

    private fun run(d: ByteArray, off: Int, len: Int, pc: Int, pb: Int): State {
        val s = State(-0x21524111 + len + pc, -0x21524111 + len + pc, -0x21524111 + len + pc + pb)
        var p = off
        var left = len
        while (left > 12) {
            s.a += u(d, p) + (u(d, p + 1) shl 8) + (u(d, p + 2) shl 16) + (u(d, p + 3) shl 24)
            s.b += u(d, p + 4) + (u(d, p + 5) shl 8) + (u(d, p + 6) shl 16) + (u(d, p + 7) shl 24)
            s.c += u(d, p + 8) + (u(d, p + 9) shl 8) + (u(d, p + 10) shl 16) + (u(d, p + 11) shl 24)
            s.mix()
            p += 12; left -= 12
        }
        if (left == 0) return s
        // the last block: bytes 0..left-1 into a, b, c in order
        for (i in 0 until left) {
            val v = u(d, p + i)
            when (i / 4) { 0 -> s.a += v shl (8 * (i % 4)); 1 -> s.b += v shl (8 * (i % 4)); else -> s.c += v shl (8 * (i % 4)) }
        }
        s.fin()
        return s
    }

    fun hashlittle(data: ByteArray, off: Int = 0, len: Int = data.size - off, initval: Int = 0): Int = run(data, off, len, initval, 0).c

    /** (primary, secondary) with the given seeds, as `hashlittle2(data, len, &pc, &pb)` leaves pc and pb. */
    fun hashlittle2(data: ByteArray, off: Int, len: Int, pc: Int, pb: Int): Pair<Int, Int> {
        val s = run(data, off, len, pc, pb)
        return s.c to s.b
    }
}
