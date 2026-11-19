package com.logie.blizz.wrathpp

import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * The body layer made on the phone, on the looks' own model and skin (the user: one import must last): what
 * `realm/warcraft/wrathpp/tools/body_shapes/layer.py`'s `add` does, here, for a woman whose model the imported package
 * was not made for (a looks release changed it: the Gnome's of 17 November 2026 had three bones more, and her package's
 * patch no longer fitted). The package's list says how each race's layer lies ([Params]: `races[].layer`, measured by
 * `measure.py`); nothing else of the package is needed for a woman as drawn, and a body shape's vertices are carried over
 * by [carried].
 *
 * The layer is a skin section of its own (geoset 1901) after the model's: the body's triangles under the design's square
 * that face the front, their vertices the body's own lifted 0.4 mm with the hair patch's and the design's texture
 * coordinates, one batch of two textures (the character's hair, type 6, or for a race without hair textures her body's,
 * type 1; the design, type 11, whose own file is the folder's empty design), alpha blended, and the model's texture
 * combiner list (flag 0x8) [1, 0, 1, 1] with the layer's batch at index 1 (Combiners_Opaque_Mod: the alpha is the
 * design's alone). layer.py's docstring has how the game draws it.
 *
 * The tool makes room for the layer's indices by cutting the worn gear's pieces down; this does not: the looks' skin has
 * to have the room (the converter leaves it since 18 November 2026: `m2.py`'s `LAYER_RESERVE`), else [NoRoom], and the
 * woman stays as drawn until the package is made again. The same bytes as the tool's for the same model, skin and
 * numbers (checked on the released looks' 22 women); unit-tested on a small model. NOT run in the game.
 */
object WrathppBodyLayer {
    const val GEOSET = 1901
    const val EMPTY = "WppLayer_0"
    private const val SPAN = 0.21
    private const val TOP = 0.16
    private const val GRID = 16
    private const val LIFT = 0.0004
    private const val MIN_NX = 0.12
    private const val HAIR = 6
    private const val DESIGN = 11
    private val COMBINERS = intArrayOf(1, 0, 1, 1)
    private const val LAYER_COMBINER = 1
    private const val FLAG_COMBINERS = 0x8
    private const val MAX_BONES = 64
    private const val VERT = 48
    /** What a stock 3.3.5 skin holds: a section's start is 16 bits there. */
    const val MAX_INDICES = 0xFFFF
    /**
     * What a wide skin holds (Wrath++'s own client reads a section's start wide, `skinwide.py` / `wide_index_start`: the high
     * half in the section's level, the id's top half-word, taken when the window lies inside the skin): the converter's
     * `m2.WIDE_INDEX_BUDGET`. The skin's vertices stay under 65536 and a section's own count under 65536.
     */
    const val WIDE_MAX_INDICES = 262144
    const val MAX_SKIN_VERTICES = 0xFFFF

    /** The client's M2SkinSectionIndexStart: [level] << 16 | [start], when its window of [count] lies inside the skin's [total] indices. */
    fun wideStart(total: Int, level: Int, start: Int, count: Int): Int {
        val wide = (level shl 16) or start
        return if (wide != start && wide <= total && count <= total - wide) wide else start
    }

    // the header's arrays this changes
    private const val NAME = 0x08
    private const val VERTICES = 0x3C
    private const val TEXTURES = 0x50
    private const val REPLACEABLE = 0x68
    private const val MATERIALS = 0x70
    private const val BONE_COMBOS = 0x78
    private const val TEX_COMBOS = 0x80
    private const val COORD_COMBOS = 0x88
    private const val WEIGHT_COMBOS = 0x90
    private const val TRANSFORM_COMBOS = 0x98
    private const val COMBINER_COMBOS = 0x130

    /** How a race's layer lies (races.json: layer.py): her scale, the fold's height, the body's sections, the hair patch. */
    class Params(val k: Double, val fold: Double, val body: Set<Int>, val hairBlock: IntArray, val texture: Int = HAIR, val x: Double = 0.0)

    class Made(val model: ByteArray, val skin: ByteArray, val triangles: Int, val indices: Int)

    /** The looks' skin has no room for the layer's indices. */
    class NoRoom(val free: Int, val needed: Int) : IOException("the looks' skin has $free indices free, the layer needs $needed")

    private fun le(b: ByteArray): ByteBuffer = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN)

    private class Skin(b: ByteArray) {
        val verts: IntArray
        val idx: IntArray
        val props: ByteArray
        val secs: ArrayList<ByteArray>
        val batches: ArrayList<ByteArray>
        val maxBones: Int

        init {
            if (b.size < 48 || String(b, 0, 4, Charsets.ISO_8859_1) != "SKIN") throw IOException("not a skin")
            val h = le(b)
            fun count(i: Int) = h.getInt(4 + i * 8)
            fun at(i: Int) = h.getInt(8 + i * 8)
            fun inside(i: Int, size: Int) { if (count(i) < 0 || at(i) < 0 || at(i).toLong() + count(i).toLong() * size > b.size) throw IOException("the skin's arrays leave the file") }
            inside(0, 2); inside(1, 2); inside(2, 4); inside(3, 48); inside(4, 24)
            verts = IntArray(count(0)) { h.getShort(at(0) + it * 2).toInt() and 0xFFFF }
            idx = IntArray(count(1)) { h.getShort(at(1) + it * 2).toInt() and 0xFFFF }
            props = b.copyOfRange(at(2), at(2) + count(2) * 4)
            secs = ArrayList((0 until count(3)).map { b.copyOfRange(at(3) + it * 48, at(3) + it * 48 + 48) })
            batches = ArrayList((0 until count(4)).map { b.copyOfRange(at(4) + it * 24, at(4) + it * 24 + 24) })
            maxBones = h.getInt(44)
        }
    }

    private fun u16(b: ByteArray, at: Int) = (b[at].toInt() and 0xFF) or ((b[at + 1].toInt() and 0xFF) shl 8)
    private fun put16(b: ByteArray, at: Int, v: Int) { b[at] = v.toByte(); b[at + 1] = (v shr 8).toByte() }

    /** refine.py's write_skin: the header, then each array 16-byte aligned: vertices, indices, bone slots, sections, batches. */
    private fun writeSkin(verts: IntArray, idx: IntArray, props: ByteArray, secs: List<ByteArray>, batches: List<ByteArray>, maxBones: Int): ByteArray {
        val body = ByteArrayOutputStream()
        fun put(payload: ByteArray): Int {
            while ((48 + body.size()) % 16 != 0) body.write(0)
            val at = 48 + body.size()
            body.write(payload)
            return at
        }
        fun shorts(a: IntArray) = ByteArray(a.size * 2).also { o -> a.forEachIndexed { i, v -> put16(o, i * 2, v) } }
        fun join(l: List<ByteArray>) = ByteArrayOutputStream().also { o -> l.forEach { o.write(it) } }.toByteArray()
        val parts = listOf(verts.size to put(shorts(verts)), idx.size to put(shorts(idx)), props.size / 4 to put(props),
            secs.size to put(join(secs)), batches.size to put(join(batches)))
        val head = ByteBuffer.allocate(48).order(ByteOrder.LITTLE_ENDIAN)
        head.put("SKIN".toByteArray(Charsets.ISO_8859_1))
        for ((c, o) in parts) { head.putInt(c); head.putInt(o) }
        head.putInt(maxBones)
        return head.array() + body.toByteArray()
    }

    private class Vertices(val bytes: ByteArray) {
        val n = bytes.size / VERT
        private val b = le(bytes)
        fun f(i: Int, at: Int) = b.getFloat(i * VERT + at).toDouble()
        fun weight(i: Int, j: Int) = bytes[i * VERT + 12 + j].toInt() and 0xFF
        fun bone(i: Int, j: Int) = bytes[i * VERT + 16 + j].toInt() and 0xFF
    }

    /** The model's own vertex records (48 bytes each), as its header names them. */
    fun verticesOf(m2: ByteArray): ByteArray {
        val h = le(m2)
        val n = h.getInt(VERTICES)
        val o = h.getInt(VERTICES + 4)
        if (n <= 0 || o < 0 || o.toLong() + n.toLong() * VERT > m2.size) throw IOException("the model's vertices leave the file")
        return m2.copyOfRange(o, o + n * VERT)
    }

    /**
     * [m2] (a looks' model) with [vertices] (its own when null, or a body shape's: as many as its own or more) and the
     * layer's after them, and its [skin] with the layer's section and batch after its own. [folder]: the model's folder in
     * the game ("Character\\Gnome\\Female"), where the empty design is. Throws [NoRoom] when the skin's indices with the
     * layer's would pass [maxIndices], [IOException] for a model this can't be done to (not 3.3.5's, a combiner list of its
     * own, no body under the layer, more bones than a section takes).
     */
    fun add(m2: ByteArray, skin: ByteArray, vertices: ByteArray?, p: Params, folder: String, maxIndices: Int = MAX_INDICES): Made {
        if (m2.size < 0x138 || String(m2, 0, 4, Charsets.ISO_8859_1) != "MD20") throw IOException("not a 3.3.5 model")
        val h = le(m2)
        val flags = h.getInt(0x10)
        if (flags and FLAG_COMBINERS != 0) throw IOException("the model has a texture combiner list already")
        if (h.getInt(NAME + 4) != 0x130) throw IOException("the model's name isn't where the combiner list goes")
        val recBytes = vertices ?: verticesOf(m2)
        if (recBytes.size % VERT != 0) throw IOException("the vertices aren't whole")
        val v = Vertices(recBytes)
        val nv = v.n
        val sk = Skin(skin)
        if (sk.verts.any { it >= nv }) throw IOException("the skin names vertices the model hasn't")
        val span = SPAN * p.k
        val ztop = p.fold + TOP * p.k
        val zbot = ztop - span

        // the body's triangles under the layer's square that face the front (layer.py's triangles)
        val tris = ArrayList<IntArray>()
        var owner = -1
        for ((si, s) in sk.secs.withIndex()) {
            if (u16(s, 0) !in p.body) continue
            val count = u16(s, 10)
            val st = wideStart(sk.idx.size, u16(s, 2), u16(s, 8), count)
            if (st < 0 || st + count > sk.idx.size) throw IOException("a section's indices leave the skin")
            var t = 0
            while (t + 2 < count) {
                val a = sk.verts[sk.idx[st + t]]; val b = sk.verts[sk.idx[st + t + 1]]; val c = sk.verts[sk.idx[st + t + 2]]
                t += 3
                val ax = v.f(a, 0); val ay = v.f(a, 4); val az = v.f(a, 8)
                val bx = v.f(b, 0); val by = v.f(b, 4); val bz = v.f(b, 8)
                val cx = v.f(c, 0); val cy = v.f(c, 4); val cz = v.f(c, 8)
                if (!(maxOf(az, bz, cz) >= zbot && minOf(az, bz, cz) <= ztop && minOf(Math.abs(ay), Math.abs(by), Math.abs(cy)) <= span / 2)) continue
                // the face's normal: (b - a) x (c - a), its x over its length
                val ux = bx - ax; val uy = by - ay; val uz = bz - az
                val wx = cx - ax; val wy = cy - ay; val wz = cz - az
                val nx = uy * wz - uz * wy; val ny = uz * wx - ux * wz; val nz = ux * wy - uy * wx
                val len = Math.sqrt(nx * nx + ny * ny + nz * nz) + 1e-12
                if (!(nx / len >= MIN_NX && (ax + bx + cx) / 3.0 >= p.x)) continue
                if (owner < 0) owner = si
                tris.add(intArrayOf(a, b, c))
            }
        }
        if (tris.isEmpty()) throw IOException("no body under the layer")
        val used = tris.flatMap { it.asList() }.toSortedSet().toIntArray()
        val local = HashMap<Int, Int>()
        used.forEachIndexed { j, g -> local[g] = j }
        val free = maxIndices - sk.idx.size
        if (tris.size * 3 > free || tris.size * 3 > 0xFFFF) throw NoRoom(free, tris.size * 3)
        if (sk.verts.size + used.size > MAX_SKIN_VERTICES) throw IOException("too many skin vertices")

        // the layer's vertices: the body's own lifted, both texture coordinates its own
        val layer = ByteArray(used.size * VERT)
        val lb = le(layer)
        var cxs = 0.0; var cys = 0.0; var czs = 0.0
        for ((j, g) in used.withIndex()) {
            System.arraycopy(recBytes, g * VERT, layer, j * VERT, VERT)
            val px = v.f(g, 0) + v.f(g, 20) * LIFT; val py = v.f(g, 4) + v.f(g, 24) * LIFT; val pz = v.f(g, 8) + v.f(g, 28) * LIFT
            lb.putFloat(j * VERT, px.toFloat()); lb.putFloat(j * VERT + 4, py.toFloat()); lb.putFloat(j * VERT + 8, pz.toFloat())
            val u1 = (py + span / 2) / span
            val v1 = (ztop - pz) / span
            if (p.texture == HAIR) {
                lb.putFloat(j * VERT + 32, ((p.hairBlock[0] + 0.25 + 0.5 * u1.coerceIn(0.0, 1.0)) / GRID).toFloat())
                lb.putFloat(j * VERT + 36, ((p.hairBlock[1] + 0.25 + 0.5 * v1.coerceIn(0.0, 1.0)) / GRID).toFloat())
            }
            lb.putFloat(j * VERT + 40, u1.toFloat()); lb.putFloat(j * VERT + 44, v1.toFloat())
            cxs += v.f(g, 0); cys += v.f(g, 4); czs += v.f(g, 8)
        }
        // one section: its own bone list (the bones the layer's vertices hang on), each vertex's slots in it
        val bones = java.util.TreeSet<Int>()
        for (g in used) for (j in 0 until 4) if (v.weight(g, j) != 0) bones.add(v.bone(g, j))
        if (bones.size > MAX_BONES) throw IOException("the layer hangs on ${bones.size} bones")
        val slot = HashMap<Int, Int>()
        bones.forEachIndexed { i, b -> slot[b] = i }
        val lprops = ByteArray(used.size * 4)
        var influences = 1
        val weight = LinkedHashMap<Int, Int>()
        for ((i, g) in used.withIndex()) {
            var n = 0
            for (j in 0 until 4) if (v.weight(g, j) != 0) {
                lprops[i * 4 + j] = slot.getValue(v.bone(g, j)).toByte()
                weight[v.bone(g, j)] = (weight[v.bone(g, j)] ?: 0) + v.weight(g, j)
                n++
            }
            influences = maxOf(influences, n)
        }
        var centreBone = 0
        var most = -1
        for ((b, w) in weight) if (w > most) { most = w; centreBone = b }
        val centre = doubleArrayOf(cxs / used.size, cys / used.size, czs / used.size)
        var radius = 0.0
        for (g in used) {
            val dx = v.f(g, 0) - centre[0]; val dy = v.f(g, 4) - centre[1]; val dz = v.f(g, 8) - centre[2]
            radius = maxOf(radius, Math.sqrt(dx * dx + dy * dy + dz * dz))
        }

        // the model: its header's arrays, old and new, after its end (16-byte aligned)
        val baseLen = (m2.size + 15) / 16 * 16
        val blob = ByteArrayOutputStream()
        fun put(payload: ByteArray): Int {
            while ((baseLen + blob.size()) % 16 != 0) blob.write(0)
            val at = baseLen + blob.size()
            blob.write(payload)
            return at
        }
        fun array(off: Int, size: Int): ByteArray {
            val n = h.getInt(off); val o = h.getInt(off + 4)
            if (n < 0 || o < 0 || o.toLong() + n.toLong() * size > m2.size) throw IOException("the model's array at 0x${off.toString(16)} leaves the file")
            return m2.copyOfRange(o, o + n * size)
        }
        fun shortsOf(off: Int): MutableList<Int> = array(off, 2).let { a -> MutableList(a.size / 2) { u16(a, it * 2) } }
        fun bytesOf(values: List<Int>) = ByteArray(values.size * 2).also { o -> values.forEachIndexed { i, x -> put16(o, i * 2, x) } }
        val textures = ByteArrayOutputStream().also { it.write(array(TEXTURES, 16)) }
        var textureCount = textures.size() / 16
        fun texture(type: Int, flags: Int, nameLen: Int, nameAt: Int): Int {
            textures.write(ByteBuffer.allocate(16).order(ByteOrder.LITTLE_ENDIAN).putInt(type).putInt(flags).putInt(nameLen).putInt(nameAt).array())
            return textureCount++
        }
        val empty = (folder.replace('/', '\\').trimEnd('\\') + "\\" + EMPTY + ".blp").toByteArray(Charsets.ISO_8859_1) + 0.toByte()
        val first = if (p.texture == HAIR) texture(HAIR, 0, 0, 0)
        else {
            val own = textures.toByteArray()
            (0 until textureCount).firstOrNull { le(own).getInt(it * 16) == p.texture } ?: throw IOException("the model has no texture of type ${p.texture}")
        }
        val design = texture(DESIGN, 0, empty.size, put(empty))
        val replaceable = shortsOf(REPLACEABLE)
        while (replaceable.size <= DESIGN) replaceable.add(0xFFFF)
        if (replaceable[DESIGN] >= 0x8000) replaceable[DESIGN] = design
        val texCombos = shortsOf(TEX_COMBOS); val tc = texCombos.size; texCombos += listOf(first, design)
        val coordCombos = shortsOf(COORD_COMBOS); val cc = coordCombos.size; coordCombos += listOf(0, 1)
        val weightCombos = shortsOf(WEIGHT_COMBOS); val wc = weightCombos.size
        (if (weightCombos.isNotEmpty()) weightCombos[0] else 0).let { weightCombos += listOf(it, it) }
        val transformCombos = shortsOf(TRANSFORM_COMBOS); val xc = transformCombos.size; transformCombos += listOf(0xFFFF, 0xFFFF)
        val materials = array(MATERIALS, 4); val material = materials.size / 4
        val boneCombos = shortsOf(BONE_COMBOS); val bc = boneCombos.size; boneCombos += bones
        val out = m2.copyOf(baseLen)
        val oh = le(out)
        fun header(off: Int, count: Int, at: Int) { oh.putInt(off, count); oh.putInt(off + 4, at) }
        val name = array(NAME, 1)
        header(NAME, name.size, put(name))
        header(VERTICES, nv + used.size, put(recBytes + layer))
        header(TEXTURES, textureCount, put(textures.toByteArray()))
        header(REPLACEABLE, replaceable.size, put(bytesOf(replaceable)))
        header(MATERIALS, material + 1, put(materials + byteArrayOf(0, 0, 2, 0)))
        header(BONE_COMBOS, boneCombos.size, put(bytesOf(boneCombos)))
        header(TEX_COMBOS, texCombos.size, put(bytesOf(texCombos)))
        header(COORD_COMBOS, coordCombos.size, put(bytesOf(coordCombos)))
        header(WEIGHT_COMBOS, weightCombos.size, put(bytesOf(weightCombos)))
        header(TRANSFORM_COMBOS, transformCombos.size, put(bytesOf(transformCombos)))
        header(COMBINER_COMBOS, COMBINERS.size, put(bytesOf(COMBINERS.asList())))
        oh.putInt(0x10, flags or FLAG_COMBINERS)

        // the skin: the layer's vertices, triangles, section and batch after the model's own; every other batch's combiner 0
        val nsv = sk.verts.size
        val start = sk.idx.size
        val verts2 = sk.verts + IntArray(used.size) { nv + it }
        val idx2 = sk.idx + IntArray(tris.size * 3) { nsv + local.getValue(tris[it / 3][it % 3]) }
        val section = ByteBuffer.allocate(48).order(ByteOrder.LITTLE_ENDIAN)
        for (x in intArrayOf(GEOSET, start ushr 16, nsv, used.size, start and 0xFFFF, tris.size * 3, bones.size, bc, influences, centreBone)) section.putShort(x.toShort())
        for (x in centre) section.putFloat(x.toFloat())
        for (x in centre) section.putFloat(x.toFloat())
        section.putFloat(radius.toFloat())
        val ownerId = u16(sk.secs[owner], 0)
        val source = sk.batches.firstOrNull { b -> u16(b, 4).let { it < sk.secs.size && u16(sk.secs[it], 0) == ownerId } } ?: throw IOException("the body has no batch")
        val batches = sk.batches.map { it.copyOf().also { b -> put16(b, 2, 0) } }.toMutableList()
        val mine = source.copyOf()
        mine[1] = 0
        put16(mine, 2, LAYER_COMBINER)
        put16(mine, 4, sk.secs.size); put16(mine, 6, sk.secs.size)
        put16(mine, 10, material); put16(mine, 12, 0); put16(mine, 14, 2)
        put16(mine, 16, tc); put16(mine, 18, cc); put16(mine, 20, wc); put16(mine, 22, xc)
        batches.add(mine)
        val madeSkin = writeSkin(verts2, idx2, sk.props + lprops, sk.secs + section.array(), batches, maxOf(sk.maxBones, bones.size))
        return Made(out + blob.toByteArray(), madeSkin, tris.size, idx2.size)
    }

    /**
     * A body shape carried onto looks it was not made for: the looks' own vertices ([looks], 48 bytes each) with each
     * vertex the shape changed taking the shape's place, normal and texture coordinates, found by what those were in the
     * looks the package was made for ([was], and [shape] in the same order: the first vertices of the package's two
     * models). A vertex's bones and weights stay the looks' own (a looks release may weigh the body anew: the soft body's
     * bones). The vertices the package's refinement added are left out: the shape then lies on the looks' own, coarser
     * mesh. Null when fewer than 97 in 100 of the changed vertices are found in the new looks (her body itself changed: the
     * shape is not for these looks).
     */
    fun carried(looks: ByteArray, was: ByteArray, shape: ByteArray): ByteArray? {
        // (what a shape changes of a vertex: its place, 0 to 12; its normal and first texture coordinates, 20 to 40)
        fun key(b: ByteArray, i: Int): ByteBuffer = ByteBuffer.allocate(32).put(b, i * VERT, 12).put(b, i * VERT + 20, 20).also { it.flip() }
        val n = minOf(was.size, shape.size) / VERT
        val changed = HashMap<ByteBuffer, Int>()
        for (i in 0 until n) {
            val k = key(was, i)
            if (k != key(shape, i)) changed.putIfAbsent(k, i)
        }
        if (changed.isEmpty()) return null
        val out = looks.copyOf()
        val found = HashSet<Int>()
        for (j in 0 until looks.size / VERT) {
            val i = changed[key(looks, j)] ?: continue
            System.arraycopy(shape, i * VERT, out, j * VERT, 12)
            System.arraycopy(shape, i * VERT + 20, out, j * VERT + 20, 20)
            found.add(i)
        }
        return if (found.size * 100L >= changed.size * 97L) out else null
    }
}
