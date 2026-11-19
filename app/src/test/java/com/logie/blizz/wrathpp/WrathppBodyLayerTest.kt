package com.logie.blizz.wrathpp

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * The body layer made on the phone ([WrathppBodyLayer]): on a small model of two body triangles facing the front and one
 * facing the back, the layer's vertices, section, batch and the model's arrays as the game reads them; no room, no body
 * under the layer; a body shape's vertices carried onto other looks. (The same bytes as the tool's `layer.py` on the
 * released looks' 22 women were checked with the tool beside it, 18 November 2026: not a test that runs here.)
 */
class WrathppBodyLayerTest {
    private fun le(n: Int) = Companion.le(n)
    private fun vertex(x: Float, y: Float, z: Float, nx: Float, bone: Int = 3) = Companion.vertex(x, y, z, nx, bone)
    private val vertices = Companion.vertices
    private fun model() = Companion.model()
    private fun skin(extraIndices: Int = 0) = Companion.skin(extraIndices)

    /** The small model and skin, for [WrathppBodyTest] too. */
    companion object {
    internal fun le(n: Int): ByteBuffer = ByteBuffer.allocate(n).order(ByteOrder.LITTLE_ENDIAN)

    /** A vertex record: its place, one bone at full weight, a normal, texture coordinates. */
    internal fun vertex(x: Float, y: Float, z: Float, nx: Float, bone: Int = 3): ByteArray =
        le(48).putFloat(x).putFloat(y).putFloat(z).put(255.toByte()).put(0).put(0).put(0).put(bone.toByte()).put(0).put(0).put(0)
            .putFloat(nx).putFloat(0f).putFloat(0f).putFloat(0.25f).putFloat(0.75f).putFloat(0f).putFloat(0f).array()

    internal val vertices = listOf(
        vertex(0.1f, -0.05f, 1.0f, 1f), vertex(0.1f, 0.05f, 1.0f, 1f), vertex(0.1f, 0.0f, 1.1f, 1f), vertex(0.1f, 0.05f, 1.1f, 1f),   // the front
        vertex(-0.1f, -0.05f, 1.0f, -1f), vertex(-0.1f, 0.05f, 1.0f, -1f), vertex(-0.1f, 0.0f, 1.1f, -1f))                              // the back

    /** A 3.3.5 model as far as the layer goes: the header, its name at 0x130, then the arrays the layer reads. */
    internal fun model(): ByteArray {
        val out = ByteArrayOutputStream()
        val head = le(0x138)
        head.put("MD20".toByteArray()).putInt(264)
        out.write(ByteArray(0x138))
        fun array(off: Int, count: Int, bytes: ByteArray) { head.putInt(off, count); head.putInt(off + 4, out.size()); out.write(bytes) }
        // (the name's place is 0x130 in a model without a combiner list: the header ends there)
        head.putInt(0x08, 4); head.putInt(0x0C, 0x130)
        array(0x3C, vertices.size, vertices.reduce { a, b -> a + b })
        array(0x50, 1, le(16).putInt(1).putInt(0).putInt(0).putInt(0).array())           // one texture: the body's
        array(0x68, 2, le(4).putShort(-1).putShort(0).array())                           // replaceable: type 1 is texture 0
        array(0x70, 1, le(4).putShort(0).putShort(0).array())
        array(0x78, 2, le(4).putShort(3).putShort(5).array())                            // bone combos
        array(0x80, 1, le(2).putShort(0).array())
        array(0x88, 1, le(2).putShort(0).array())
        array(0x90, 1, le(2).putShort(0).array())
        array(0x98, 1, le(2).putShort(-1).array())
        val bytes = out.toByteArray()
        System.arraycopy(head.array(), 0, bytes, 0, 0x130)
        "abc".toByteArray().copyInto(bytes, 0x130)
        return bytes
    }

    internal fun skin(extraIndices: Int = 0): ByteArray {
        val idx = intArrayOf(0, 1, 2, 1, 3, 2, 4, 6, 5) + IntArray(extraIndices) { 0 }
        val section = le(48)
        for (x in intArrayOf(0, 0, 0, 7, 0, 9, 2, 0, 1, 3)) section.putShort(x.toShort())
        val batch = le(24).put(16).put(2).putShort(7).putShort(0).putShort(0).putShort(-1).putShort(0).putShort(0).putShort(1)
            .putShort(0).putShort(0).putShort(0).putShort(0).array()
        val body = ByteArrayOutputStream()
        val head = le(48)
        head.put("SKIN".toByteArray())
        fun put(count: Int, bytes: ByteArray) {
            while ((48 + body.size()) % 16 != 0) body.write(0)
            head.putInt(count); head.putInt(48 + body.size()); body.write(bytes)
        }
        put(7, le(14).also { b -> (0 until 7).forEach { b.putShort(it.toShort()) } }.array())
        put(idx.size, le(idx.size * 2).also { b -> idx.forEach { b.putShort(it.toShort()) } }.array())
        put(7, ByteArray(28))
        put(1, section.array())
        put(1, batch)
        head.putInt(21)
        return head.array() + body.toByteArray()
    }
    }

    private val params = WrathppBodyLayer.Params(1.0, 1.0, setOf(0), intArrayOf(4, 3))
    private fun int(b: ByteArray, at: Int) = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).getInt(at)
    private fun short(b: ByteArray, at: Int) = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).getShort(at).toInt() and 0xFFFF
    private fun float(b: ByteArray, at: Int) = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).getFloat(at)

    @Test fun theLayerIsTheFrontOfTheBodyLiftedWithItsOwnSectionBatchAndTextures() {
        val base = model()
        val made = WrathppBodyLayer.add(base, skin(), null, params, "Character/Gnome/Female")
        val m = made.model
        // the two triangles facing the front, not the one facing the back
        assertEquals(2, made.triangles)
        assertEquals(9 + 6, made.indices)
        // the model: what it was up to its end but for the header, the combiner list flag, its arrays after its end
        assertArrayEquals(base.copyOfRange(0x138, base.size), m.copyOfRange(0x138, base.size))
        assertEquals(0x8, int(m, 0x10) and 0x8)
        val at = (base.size + 15) / 16 * 16
        assertEquals(7 + 4, int(m, 0x3C))
        assertTrue(int(m, 0x40) >= at)
        val v = int(m, 0x40)
        assertArrayEquals("the model's own vertices first", vertices.reduce { a, b -> a + b }, m.copyOfRange(v, v + 7 * 48))
        // a layer vertex: lifted 0.4 mm along its normal, the hair patch's coordinates, the design's square
        val l = v + 7 * 48
        assertEquals(0.1004f, float(m, l), 1e-6f)
        assertEquals(((4 + 0.25 + 0.5 * ((-0.05 + 0.105) / 0.21)) / 16).toFloat(), float(m, l + 32), 1e-6f)
        assertEquals(((3 + 0.25 + 0.5 * ((1.16 - 1.0) / 0.21)) / 16).toFloat(), float(m, l + 36), 1e-6f)
        assertEquals(((-0.05 + 0.105) / 0.21).toFloat(), float(m, l + 40), 1e-6f)
        assertEquals(((1.16 - 1.0) / 0.21).toFloat(), float(m, l + 44), 1e-6f)
        // the textures: the body's, the hair (type 6), the design (type 11) with the folder's empty design as its file
        assertEquals(3, int(m, 0x50))
        val t = int(m, 0x54)
        assertEquals(listOf(1, 6, 11), (0 until 3).map { int(m, t + it * 16) })
        val name = String(m, int(m, t + 2 * 16 + 12), int(m, t + 2 * 16 + 8) - 1, Charsets.ISO_8859_1)
        assertEquals("Character\\Gnome\\Female\\WppLayer_0.blp", name)
        assertEquals(at, int(m, t + 2 * 16 + 12))
        // the replaceable list names the design; the name moved; the combiner list where the name was
        assertEquals(12, int(m, 0x68)); assertEquals(2, short(m, int(m, 0x6C) + 11 * 2))
        assertEquals("abc", String(m, int(m, 0x0C), 3)); assertTrue(int(m, 0x0C) >= at)
        assertEquals(4, int(m, 0x130))
        assertEquals(listOf(1, 0, 1, 1), (0 until 4).map { short(m, int(m, 0x134) + it * 2) })
        // the combos: the layer's two textures and coordinates after the model's, its bone after the model's bone combos
        assertEquals(listOf(0, 1, 2), (0 until 3).map { short(m, int(m, 0x84) + it * 2) })
        assertEquals(listOf(0, 0, 1), (0 until 3).map { short(m, int(m, 0x8C) + it * 2) })
        assertEquals(listOf(3, 5, 3), (0 until 3).map { short(m, int(m, 0x7C) + it * 2) })
        assertEquals(2, int(m, 0x70)); assertEquals(2, short(m, int(m, 0x74) + 4 + 2))
        // the skin: the layer's vertices and indices after its own, a section 1901, a batch of two textures at combiner 1
        val s = made.skin
        assertEquals(11, int(s, 4)); assertEquals(15, int(s, 12)); assertEquals(2, int(s, 28)); assertEquals(2, int(s, 36))
        assertEquals(listOf(7, 8, 9, 10), (7 until 11).map { short(s, int(s, 8) + it * 2) })
        assertEquals(listOf(7, 8, 9, 8, 10, 9), (9 until 15).map { short(s, int(s, 16) + it * 2) })
        val sec = int(s, 32) + 48
        assertEquals(listOf(1901, 0, 7, 4, 9, 6, 1, 2, 1, 3), (0 until 10).map { short(s, sec + it * 2) })
        val b0 = int(s, 40); val b1 = b0 + 24
        assertEquals("every other batch at combiner 0", 0, short(s, b0 + 2))
        assertEquals(listOf(1, 1, 1), listOf(short(s, b1 + 2), short(s, b1 + 4), short(s, b1 + 6)))
        assertEquals(listOf(1, 0, 2, 1, 1, 1, 1), (10 until 24 step 2).map { short(s, b1 + it) })
        assertEquals(0, s[b1 + 1].toInt())
        assertEquals(21, int(s, 44))
    }

    @Test fun aRaceWithoutHairTexturesDrawsTheDesignOverHerBodysOwn() {
        val made = WrathppBodyLayer.add(model(), skin(), null, WrathppBodyLayer.Params(1.0, 1.0, setOf(0), intArrayOf(0, 0), texture = 1), "Character\\Worgen\\Female")
        val m = made.model
        assertEquals(2, int(m, 0x50))
        assertEquals(listOf(0, 0, 1), (0 until 3).map { short(m, int(m, 0x84) + it * 2) })       // the body's texture, then the design
        val l = int(m, 0x40) + 7 * 48
        assertEquals("her body's own coordinates stay", 0.25f, float(m, l + 32), 0f)
    }

    @Test fun aLayerThatStartsPastTheFirst65535IndicesIsWrittenWideAndReadBack() {
        // the skin has 70000 indices: the layer's section starts at 70000 = 1 * 65536 + 4464, the level (the id's top half-word) 1
        val made = WrathppBodyLayer.add(model(), skin(70000 - 9), null, params, "Character\\Gnome\\Female")
        val s = made.skin
        assertEquals(70006, int(s, 12))
        val sec = int(s, 32) + 48
        assertEquals(listOf(1901, 1, 7, 4, 4464, 6, 1, 2, 1, 3), (0 until 10).map { short(s, sec + it * 2) })
        assertEquals(70000, WrathppBodyLayer.wideStart(70006, 1, 4464, 6))
        // a second pass finds the layer already there
        try { WrathppBodyLayer.add(made.model, made.skin, null, params, "x"); fail("a model with the layer already") } catch (e: IOException) { }
    }

    @Test fun theClientsWideStartRule() {
        assertEquals("no level: the 16-bit start stands", 1234, WrathppBodyLayer.wideStart(70000, 0, 1234, 300))
        assertEquals(70000, WrathppBodyLayer.wideStart(70300, 1, 4464, 300))
        assertEquals("the window past the skin's end: a marker, not a start", 4464, WrathppBodyLayer.wideStart(70299, 1, 4464, 300))
        assertEquals("a level on a skin of 65535 indices or fewer", 10, WrathppBodyLayer.wideStart(65535, 5, 10, 3))
    }

    @Test fun aSkinWithoutRoomOrABodyElsewhereIsRefused() {
        val wide = WrathppBodyLayer.WIDE_MAX_INDICES
        try { WrathppBodyLayer.add(model(), skin(wide - 9 - 5), null, params, "Character\\Gnome\\Female"); fail("no room") } catch (e: WrathppBodyLayer.NoRoom) {
            assertEquals(5, e.free); assertEquals(6, e.needed)
        }
        assertNotNull(WrathppBodyLayer.add(model(), skin(wide - 9 - 6), null, params, "Character\\Gnome\\Female"))
        // a stock client's skin (16-bit starts: maxIndices = MAX_INDICES) has its own, smaller room
        val stock = WrathppBodyLayer.MAX_INDICES
        try { WrathppBodyLayer.add(model(), skin(stock - 9 - 5), null, params, "x", stock); fail("no room") } catch (e: WrathppBodyLayer.NoRoom) {
            assertEquals(5, e.free); assertEquals(6, e.needed)
        }
        assertNotNull(WrathppBodyLayer.add(model(), skin(stock - 9 - 6), null, params, "x", stock))
        for (bad in listOf(WrathppBodyLayer.Params(1.0, 3.0, setOf(0), intArrayOf(4, 3)), WrathppBodyLayer.Params(1.0, 1.0, setOf(401), intArrayOf(4, 3)),
            WrathppBodyLayer.Params(1.0, 1.0, setOf(0), intArrayOf(4, 3), x = 0.5))) {
            try { WrathppBodyLayer.add(model(), skin(), null, bad, "x"); fail("no body under the layer") } catch (e: WrathppBodyLayer.NoRoom) { fail("room") } catch (e: IOException) { }
        }
        val made = WrathppBodyLayer.add(model(), skin(), null, params, "x")
        try { WrathppBodyLayer.add(made.model, made.skin, null, params, "x"); fail("a model with the layer already") } catch (e: IOException) { }
    }

    @Test fun aShapesVerticesAreCarriedOntoLooksWhoseOtherVerticesChanged() {
        val was = vertices.reduce { a, b -> a + b }
        val moved = vertex(0.13f, -0.05f, 1.0f, 1f)
        val shape = moved + was.copyOfRange(48, was.size) + vertex(9f, 9f, 9f, 1f)             // the first vertex moved; one added by the refinement
        // other looks: a vertex more at the front of the array, the hair's last vertex elsewhere
        val looks = vertex(5f, 5f, 5f, 1f) + was.copyOfRange(0, 6 * 48) + vertex(-0.1f, 0.0f, 1.2f, -1f)
        val out = WrathppBodyLayer.carried(looks, was, shape)!!
        assertArrayEquals("the body's vertex takes the shape's record where it now is", moved, out.copyOfRange(48, 96))
        assertArrayEquals(looks.copyOfRange(0, 48), out.copyOfRange(0, 48))
        assertArrayEquals(looks.copyOfRange(96, looks.size), out.copyOfRange(96, out.size))
        assertEquals(looks.size, out.size)
        // looks that weigh the vertex anew (another bone): it takes the shape's place and keeps the looks' bone
        val weighed = vertex(5f, 5f, 5f, 1f) + vertex(0.1f, -0.05f, 1.0f, 1f, bone = 9) + was.copyOfRange(48, was.size)
        val kept = WrathppBodyLayer.carried(weighed, was, shape)!!
        assertArrayEquals(vertex(0.13f, -0.05f, 1.0f, 1f, bone = 9), kept.copyOfRange(48, 96))
        // looks whose body itself is another: the changed vertex is not found
        assertNull(WrathppBodyLayer.carried(vertex(5f, 5f, 5f, 1f) + was.copyOfRange(48, was.size), was, shape))
        assertNull("a shape that changes nothing", WrathppBodyLayer.carried(looks, was, was))
        // the carried vertices take the layer as the looks' own do
        val made = WrathppBodyLayer.add(model(), skin(), WrathppBodyLayer.carried(was, was, shape), params, "x")
        assertEquals(0.13f, float(made.model, int(made.model, 0x40)), 0f)
        assertEquals(0.1304f, float(made.model, int(made.model, 0x40) + 7 * 48), 1e-6f)
    }
}
