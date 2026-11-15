package com.logie.blizz.porter.look

import java.io.File
import java.io.RandomAccessFile

/**
 * The other files a model's file names, read from the model alone, so they can be fetched before it is drawn: its first
 * skin (the triangles), the textures it names itself, its skeleton (today's character models keep their bones and
 * animations in a file of their own, which may borrow from a parent skeleton) and the animation files of the animations
 * asked for. The chunks are read where they are, without loading the whole model (a character's can be 30 MB).
 * Mirrors `M2Model::dependencies` in porter/engine. Plain Kotlin, unit-tested.
 */
object ModelFiles {
    /** The standing animation: the preview's. */
    val STAND = setOf(0)

    data class Found(
        val skin: Int?,
        val textures: List<Int>,
        val animations: List<Int>,
        val skeleton: Int?,
    ) {
        fun all(): List<Int> = listOfNotNull(skin, skeleton) + textures + animations
    }

    /** What the model's file [file] names; null when it isn't a model of today's kind (an old one names nothing). */
    fun of(file: File, anims: Set<Int> = STAND): Found? = RandomAccessFile(file, "r").use { f -> read(f, anims) }

    /** What a skeleton file names: its animations and its parent skeleton. */
    fun skeleton(file: File, anims: Set<Int> = STAND): Found? = RandomAccessFile(file, "r").use { f -> read(f, anims) }

    private fun read(f: RandomAccessFile, anims: Set<Int>): Found? {
        val length = f.length()
        var offset = 0L
        var skin: Int? = null
        val textures = ArrayList<Int>()
        val animations = ArrayList<Int>()
        var skeleton: Int? = null
        var parent: Int? = null
        var any = false
        while (offset + 8 <= length) {
            f.seek(offset)
            val tag = ByteArray(4).also { f.readFully(it) }.toString(Charsets.ISO_8859_1)
            val size = Integer.reverseBytes(f.readInt()).toLong() and 0xffffffffL
            val body = offset + 8
            if (body + size > length) break
            when (tag) {
                "MD21", "SKL1" -> any = true
                "SFID" -> if (size >= 4) le(f, body).takeIf { it != 0 }?.let { skin = it }
                "TXID" -> for (i in 0 until size / 4) le(f, body + 4 * i).takeIf { it != 0 }?.let { textures += it }
                "SKID" -> if (size >= 4) le(f, body).takeIf { it != 0 }?.let { skeleton = it }
                "SKPD" -> if (size >= 12) le(f, body + 8).takeIf { it != 0 }?.let { parent = it }
                "AFID" -> for (i in 0 until size / 8) {
                    f.seek(body + 8 * i)
                    val anim = java.lang.Short.reverseBytes(f.readShort()).toInt() and 0xffff
                    val variation = java.lang.Short.reverseBytes(f.readShort()).toInt() and 0xffff
                    val id = Integer.reverseBytes(f.readInt())
                    if (id != 0 && variation == 0 && anim in anims) animations += id
                }
            }
            offset = body + size
        }
        if (!any) return null
        return Found(skin, textures, animations, skeleton ?: parent)
    }

    private fun le(f: RandomAccessFile, at: Long): Int {
        f.seek(at)
        return Integer.reverseBytes(f.readInt())
    }
}
