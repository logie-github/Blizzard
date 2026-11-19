package com.logie.blizz.wrathpp

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.nio.ByteBuffer
import java.nio.ByteOrder

class WrathppWideSkinsTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun int(b: ByteArray, at: Int) = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).getInt(at)
    private fun short(b: ByteArray, at: Int) = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).getShort(at).toInt() and 0xFFFF
    private val params = WrathppBodyLayer.Params(1.0, 1.0, setOf(0), intArrayOf(4, 3))

    @Test fun onUntilSwitchedOffAndThenKept() {
        assertTrue(WrathppWideSkins.on(tmp.root))
        WrathppWideSkins.set(tmp.root, false)
        assertFalse(WrathppWideSkins.on(tmp.root))
        WrathppWideSkins.set(tmp.root, true)
        assertTrue(WrathppWideSkins.on(tmp.root))
    }

    /** `WideSkin.hpp`'s SwitchedOn: off only when the script sets the number 0. */
    @Test fun theScriptSetsTheNumberTheNativeModReads() {
        assertEquals("WrathppWideSkins = 1\n", String(WrathppWideSkins.script(true)))
        assertEquals("WrathppWideSkins = 0\n", String(WrathppWideSkins.script(false)))
    }

    @Test fun theBodyOptionsListLineIsTheModelItsVerticesAndItsBytes() {
        val model = ByteArray(400)
        ByteBuffer.wrap(model).order(ByteOrder.LITTLE_ENDIAN).putInt(60, 33953)
        assertEquals("Character\\Human\\Female\\HumanFemale\t33953\t400", WrathppWideSkins.line("Character/Human/Female/HumanFemale.m2", model))
        assertEquals("Character/Human/Female/HumanFemale00w.skin", WrathppWideSkins.wideName("Character/Human/Female/HumanFemale00.skin"))
        val text = String(WrathppWideSkins.list(listOf("a\t1\t2", "b\t3\t4")))
        assertTrue(text.startsWith("#"))
        assertEquals(listOf("a\t1\t2", "b\t3\t4"), text.trim().lines().drop(1))
    }

    /** The whole skin of the same model (the same body, 70000 indices) gets the same layer after its own, its start wide. */
    @Test fun theLayerGoesOnTheWholeSkinTooWhenItsBodyIsTheSame() {
        val cut = WrathppBodyLayerTest.skin()
        val whole = WrathppBodyLayerTest.skin(70000 - 9)
        val alone = WrathppBodyLayer.add(WrathppBodyLayerTest.model(), cut, null, params, "Character\\Gnome\\Female")
        val made = WrathppBodyLayer.add(WrathppBodyLayerTest.model(), cut, null, params, "Character\\Gnome\\Female", wide = whole)
        assertNull("no whole skin given: none made", alone.wideSkin)
        assertArrayEquals("the model and her own skin are the same with or without it", alone.model, made.model)
        assertArrayEquals(alone.skin, made.skin)
        val w = made.wideSkin
        assertNotNull(w)
        assertEquals(70006, int(w!!, 12))
        val sec = int(w, 32) + 48
        assertEquals("the layer's section: geoset 1901, level 1, its vertices after the skin's 7, its 6 indices at 70000",
            listOf(1901, 1, 7, 4, 4464, 6), (0 until 6).map { short(w, sec + it * 2) })
        assertEquals(70000, WrathppBodyLayer.wideStart(70006, 1, 4464, 6))
        // the layer's batch: its own material (the model's one and the layer's) and texture combination, as in her own skin
        val own = made.skin
        val batchW = int(w, 40) + 24
        val batchO = int(own, 40) + 24
        assertEquals((5 until 12).map { short(own, batchO + it * 2) }, (5 until 12).map { short(w, batchW + it * 2) })
    }

    /** A whole skin whose body is other triangles (a looks release that did not keep her body as the cut skin's): none is made. */
    @Test fun aWholeSkinWithAnotherBodyGetsNoLayer() {
        val other = WrathppBodyLayerTest.skin(70000 - 9)
        // the first triangle's corners swapped for the back's: another body under the layer
        val at = int(other, 16)
        ByteBuffer.wrap(other).order(ByteOrder.LITTLE_ENDIAN).putShort(at, 4).putShort(at + 2, 6).putShort(at + 4, 5)
        val made = WrathppBodyLayer.add(WrathppBodyLayerTest.model(), WrathppBodyLayerTest.skin(), null, params, "x", wide = other)
        assertNull(made.wideSkin)
    }
}
