package com.logie.blizz.porter.view

import com.logie.blizz.porter.armory.Armory
import com.logie.blizz.porter.armory.Region
import com.logie.blizz.porter.look.CharacterLook
import com.logie.blizz.porter.look.Looks
import com.logie.blizz.porter.look.ModelFiles
import com.logie.blizz.porter.look.Worn
import com.logie.blizz.porter.net.HttpNet
import com.logie.blizz.porter.wago.GameFiles
import com.logie.blizz.porter.wago.WagoTables
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * The preview end to end on a desktop: the look the app makes (Kotlin, from wago.tools), its files fetched as the app fetches
 * them, drawn by porter/engine's viewer through the desktop harness (porter/harness, Mesa's OpenGL ES): the character must
 * fill a good part of the picture, in the colours of its gear. Needs `BLIZZ_PORTER_HARNESS=<the harness binary>`,
 * `BLIZZ_PORTER_WORK=<a folder for the files and the picture>` and the network; skipped otherwise.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class PreviewRenderTest {
    /** The harness's commands for [look], as PreviewView hands the same to the engine. */
    private fun script(look: CharacterLook, files: File, out: File): String = buildString {
        appendLine("files ${files.path}")
        appendLine("character ${look.model} " + (look.geosetGroups.entries.sortedBy { it.key }.joinToString(",") { "${it.key}=${it.value}" }.ifEmpty { "-" }))
        for ((type, c) in look.canvases) {
            appendLine("canvas $type ${c.width} ${c.height}")
            for (l in c.layers) appendLine("layer ${l.file} ${l.x} ${l.y} ${l.width} ${l.height} ${l.blend}")
            appendLine("end")
        }
        for ((type, file) in look.textures) appendLine("texture $type $file")
        for (h in look.hung) appendLine("attach ${h.attachment} ${h.model} " + (h.textures.entries.joinToString(",") { "${it.key}=${it.value}" }.ifEmpty { "-" }))
        for (s in look.skinned) appendLine("skinned ${s.model} " + (s.textures.entries.joinToString(",") { "${it.key}=${it.value}" }.ifEmpty { "-" }) + " " + s.geosets.joinToString(","))
        appendLine("view 20 5 1 0.5")
        appendLine("render ${out.path} 360 480 0")
    }

    @Test fun theArmorysCharacterDrawn() {
        val harness = System.getenv("BLIZZ_PORTER_HARNESS")?.let { File(it) }
        val work = System.getenv("BLIZZ_PORTER_WORK")?.let { File(it) }
        assumeTrue(harness != null && harness.canExecute() && work != null)
        val build = "12.1.5.70783"
        val net = HttpNet("BlizzardLauncher-test/1.0")
        val c = Armory.parseCharacter(Region.US, String(javaClass.classLoader!!.getResourceAsStream("porter/armory-model.json")!!.readBytes()))
        val look = Looks(WagoTables(net, build, File(work!!, "tables"))).of(c.raceId, c.gender, c.classId, c.items.map { Worn(it.slot, it.id, it.transmogItemId, it.modifiedAppearanceId, it.inventoryType) })
        val files = GameFiles(net, build, File(work, "files"))
        files.fetch(look.files())
        for (model in look.models()) {
            val found = ModelFiles.of(files.path(model)!!) ?: continue
            files.fetch(found.all())
            var skeleton = found.skeleton
            while (skeleton != null) {
                files.fetch(listOf(skeleton))
                val s = ModelFiles.skeleton(files.path(skeleton)!!) ?: break
                files.fetch(s.animations)
                skeleton = s.skeleton
            }
        }
        val out = File(work, "preview.ppm")
        val commands = File(work, "preview.txt").apply { writeText(script(look, File(work, "files/$build"), out)) }
        val process = ProcessBuilder(harness!!.path, commands.path).redirectErrorStream(true).start()
        val log = process.inputStream.bufferedReader().readText()
        process.waitFor()
        assertTrue(log, !log.contains("FAILED"))
        // The picture: P6, 360x480. The backdrop is a dark blue-grey; the character's pixels differ from it.
        val bytes = out.readBytes()
        val header = String(bytes, 0, 15)
        assertTrue(header, header.startsWith("P6\n360 480\n255\n"))
        val pixels = bytes.copyOfRange(15, bytes.size)
        var character = 0
        var red = 0
        for (i in pixels.indices step 3) {
            val r = pixels[i].toInt() and 0xff; val g = pixels[i + 1].toInt() and 0xff; val b = pixels[i + 2].toInt() and 0xff
            if (r > 70 || g > 70 || b > 90) character++
            if (r > g + 30 && r > b + 30) red++
        }
        val share = character / (360f * 480f)
        println("PreviewRenderTest: the character covers ${"%.1f".format(share * 100)}% of the picture, ${red * 100 / maxOf(character, 1)}% of it red")
        assertTrue("the character covers ${share * 100}%", share > 0.08f)
        // The warlock's robes are red (the Diabolic set).
        assertTrue("red ${red * 100 / maxOf(character, 1)}%", red > character / 5)
    }
}
