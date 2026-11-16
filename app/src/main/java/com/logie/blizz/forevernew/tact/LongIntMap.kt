package com.logie.blizz.forevernew.tact

/** A map from Long to Int in two primitive arrays (open addressing): the installer holds a million keys, and a HashMap of boxed numbers and strings would not fit a phone's memory. */
class LongIntMap(expected: Int) {
    private var cap = Integer.highestOneBit((expected.coerceAtLeast(8) * 2) - 1) shl 1
    private var keys = LongArray(cap)
    private var vals = IntArray(cap)
    private var used = BooleanArray(cap)
    var size = 0
        private set

    private fun slot(k: Long): Int { var h = k * -0x61c8864680b583ebL; h = h xor (h ushr 32); return (h.toInt()) and (cap - 1) }

    operator fun get(k: Long): Int {
        var i = slot(k)
        while (used[i]) { if (keys[i] == k) return vals[i]; i = (i + 1) and (cap - 1) }
        return -1
    }

    operator fun set(k: Long, v: Int) {
        if ((size + 1) * 2 > cap) grow()
        var i = slot(k)
        while (used[i]) { if (keys[i] == k) { vals[i] = v; return }; i = (i + 1) and (cap - 1) }
        used[i] = true; keys[i] = k; vals[i] = v; size++
    }

    private fun grow() {
        val ok = keys; val ov = vals; val ou = used
        cap *= 2; keys = LongArray(cap); vals = IntArray(cap); used = BooleanArray(cap); size = 0
        for (i in ok.indices) if (ou[i]) set(ok[i], ov[i])
    }
}

/** The first 8 bytes of a key as a number: enough to tell a million keys apart (the chance of two sharing 64 bits is about 1 in 10^8), and the full key is checked where it matters. */
fun ByteArray.prefix64(off: Int = 0): Long {
    var r = 0L
    for (i in 0 until 8) r = (r shl 8) or (this[off + i].toLong() and 0xff)
    return r
}
