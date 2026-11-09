package com.logie.blizz.game

/**
 * Warcraft III's 26-character CD keys, read the way the game and Battle.net read them (a port of the decoding in libd2's `cdkey.zig`):
 * which letters a key may hold, and the product it is for (Reign of Chaos 14, The Frozen Throne 18). Nothing is made or checked
 * against Battle.net: this only tells a pasted key's game, so each lands in the right archive. Plain Kotlin, unit-tested.
 */
object Wc3KeyCodec {
    const val ROC = 14
    const val TFT = 18

    /** The letters and digits a key is made of. */
    const val ALPHABET = "246789BCDEFGHJKMNPRTVWXYZbcdefghjkmnprtvwxyz"

    private val CHARTBL = intArrayOf(
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
        255, 255, 0, 255, 1, 255, 2, 3, 4, 5, 255, 255, 255, 255, 255, 255,
        255, 255, 6, 7, 8, 9, 10, 11, 12, 255, 13, 14, 255, 15, 16, 255,
        17, 255, 18, 255, 19, 255, 20, 21, 22, 23, 24, 255, 255, 255, 255, 255,
        255, 255, 6, 7, 8, 9, 10, 11, 12, 255, 13, 14, 255, 15, 16, 255,
        17, 255, 18, 255, 19, 255, 20, 21, 22, 23, 24, 255, 255, 255, 255, 255
    )

    private val SBOX = intArrayOf(
        9, 4, 7, 15, 13, 10, 3, 11, 1, 2, 12, 8, 6, 14, 5, 0,
        9, 11, 5, 4, 8, 15, 1, 14, 7, 0, 3, 2, 10, 6, 13, 12,
        12, 14, 1, 4, 9, 15, 10, 11, 13, 6, 0, 8, 7, 2, 5, 3,
        11, 2, 5, 14, 13, 3, 9, 0, 1, 15, 7, 12, 10, 6, 4, 8,
        6, 2, 4, 5, 11, 8, 12, 14, 13, 15, 7, 1, 10, 0, 3, 9,
        5, 4, 14, 12, 7, 6, 13, 10, 15, 2, 9, 1, 0, 11, 8, 3,
        12, 7, 8, 15, 11, 0, 5, 9, 13, 10, 6, 14, 2, 4, 3, 1,
        3, 10, 14, 8, 1, 11, 5, 4, 2, 15, 13, 12, 6, 7, 9, 0,
        12, 13, 1, 15, 8, 14, 5, 11, 3, 10, 9, 0, 7, 2, 4, 6,
        13, 10, 7, 14, 1, 6, 11, 8, 15, 12, 5, 2, 3, 0, 4, 9,
        3, 14, 7, 5, 11, 15, 8, 12, 1, 10, 4, 13, 0, 6, 9, 2,
        11, 6, 9, 4, 1, 8, 10, 13, 7, 14, 0, 12, 15, 2, 3, 5,
        12, 7, 8, 13, 3, 11, 0, 14, 6, 15, 9, 4, 10, 1, 5, 2,
        12, 6, 13, 9, 11, 0, 1, 2, 15, 7, 3, 4, 10, 14, 8, 5,
        3, 6, 1, 5, 11, 12, 8, 0, 15, 14, 9, 4, 7, 10, 13, 2,
        10, 7, 11, 15, 2, 8, 0, 13, 14, 12, 1, 6, 9, 3, 5, 4,
        10, 11, 13, 4, 3, 8, 5, 9, 1, 0, 15, 12, 7, 14, 2, 6,
        11, 4, 13, 15, 1, 6, 3, 14, 7, 10, 12, 8, 9, 2, 5, 0,
        9, 6, 7, 0, 1, 10, 13, 2, 3, 14, 15, 12, 5, 11, 4, 8,
        13, 14, 5, 6, 1, 9, 8, 12, 2, 15, 3, 7, 11, 4, 0, 10,
        9, 15, 4, 0, 1, 6, 10, 14, 2, 3, 7, 13, 5, 11, 8, 12,
        3, 14, 1, 10, 2, 12, 8, 4, 11, 7, 13, 0, 15, 6, 9, 5,
        7, 2, 12, 6, 10, 8, 11, 0, 15, 4, 3, 14, 9, 1, 13, 5,
        12, 4, 5, 9, 10, 2, 8, 13, 3, 15, 1, 14, 6, 7, 11, 0,
        10, 8, 14, 13, 9, 15, 3, 0, 4, 6, 1, 12, 7, 11, 2, 5,
        3, 12, 4, 10, 2, 15, 13, 14, 7, 0, 5, 8, 1, 6, 11, 9,
        10, 12, 1, 0, 9, 14, 13, 11, 3, 7, 15, 8, 5, 2, 4, 6,
        14, 10, 1, 8, 7, 6, 5, 12, 2, 15, 0, 13, 3, 11, 4, 9,
        3, 8, 14, 0, 7, 9, 15, 12, 1, 6, 13, 2, 5, 10, 11, 4,
        3, 10, 12, 4, 13, 11, 9, 14, 15, 6, 1, 7, 2, 0, 5, 8
    )

    private fun nib(t: LongArray, n: Int): Int = ((t[3 - (n shr 3)] ushr ((n and 7) * 4)) and 0xf).toInt()
    private fun setNib(t: LongArray, n: Int, v: Int) {
        val w = 3 - (n shr 3); val sh = (n and 7) * 4
        t[w] = ((v and 0xf).toLong() shl sh) or (t[w] and (0xfL shl sh).inv() and 0xffffffffL)
    }
    private fun bit(t: LongArray, b: Int): Int = ((t[3 - (b shr 5)] ushr (b and 31)) and 1).toInt()
    private fun setBit(t: LongArray, b: Int, v: Int) {
        val w = 3 - (b shr 5); val sh = b and 31
        t[w] = ((v and 1).toLong() shl sh) or (t[w] and (1L shl sh).inv() and 0xffffffffL)
    }

    /** The game a 26-character [key] is for (14 or 18 for Warcraft III), or null when it is not made of key letters. */
    fun product(key: String): Int? {
        if (key.length != 26) return null
        val base5 = IntArray(52)
        var out2 = 0x21
        for (i in 0 until 26) {
            val out1 = (out2 + 0x7b5) % 52
            out2 = (out1 + 0x7b5) % 52
            val dv = CHARTBL[key[i].code and 0x7f]
            if (dv == 0xff || key[i].code > 127) return null
            base5[out1] = dv / 5
            base5[out2] = dv % 5
        }
        val tok = LongArray(4)
        for (di in 52 downTo 1) {
            var carry = base5[di - 1].toLong()
            for (i in 4 downTo 1) {
                val p = tok[i - 1] * 5 + carry
                tok[i - 1] = p and 0xffffffffL
                carry = p ushr 32
            }
        }
        for (n in 29 downTo 0) {
            val row = n * 16
            var acc = nib(tok, n)
            for (k in 29 downTo n + 1) acc = SBOX[row + (nib(tok, k) xor SBOX[row + acc])]
            for (k in n - 1 downTo 0) acc = SBOX[row + (nib(tok, k) xor SBOX[row + acc])]
            setNib(tok, n, SBOX[row + acc] and 0xf)
        }
        val src = tok.copyOf()
        var sb = 0
        for (db in 0 until 120) {
            setBit(tok, db, bit(src, sb))
            sb += 11
            if (sb >= 120) sb -= 120
        }
        return (tok[0] ushr 10).toInt()
    }
}
