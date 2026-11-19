package com.logie.blizz.converter

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

@org.junit.runner.RunWith(org.robolectric.RobolectricTestRunner::class)
@org.robolectric.annotation.Config(sdk = [34])
class ConverterTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun theExpansionsAreTheDriversList() {
        val list = JSONObject(File("../realm/warcraft/converter/expansions.json").readText()).getJSONArray("expansions")
        assertEquals(Expansions.all.size, list.length())
        for (i in 0 until list.length()) {
            val j = list.getJSONObject(i)
            val e = Expansions.all[i]
            assertEquals(e, Expansion(j.getString("key"), j.getString("name"), j.getInt("id"), j.getString("build")))
        }
    }

    @Test fun progressIsReadFromTheDriversFile() {
        val p = ConverterProgress.parse(
            """{"expansion": "mop", "state": "running", "stage": "fetch", "unit": "u1", "done": 1, "total": 4, "message": "u1 (2 of 4)",
               "updated": 5, "units": {"a": {"state": "done"}, "b": {"state": "failed", "message": "status 1"}}}""",
        )
        assertNotNull(p)
        assertEquals(0.25f, p!!.fraction!!, 0.0001f)
        assertFalse(p.finished)
        assertEquals(1, p.failedUnits)
        val q = ConverterProgress.parse("""{"expansion": "mop", "state": "running", "done": 1, "total": 4, "fraction": 0.4, "label": "Deepholm: converting to 3.3.5 (2 of 4)", "detail": "12 of 40"}""")!!
        assertEquals(0.4f, q.fraction!!, 0.0001f)                                      // the driver's overall share, moving inside a unit
        assertEquals("Deepholm: converting to 3.3.5 (2 of 4)", q.label)
        assertEquals("12 of 40", q.detail)
        assertTrue(ConverterProgress.parse("""{"expansion": "x", "state": "partial"}""")!!.finished)
        assertNull(ConverterProgress.parse("not json"))
    }

    @Test fun theResultsGoWhereWrathppCanReachThem() {
        val files = tmp.newFolder("games")
        val layout = com.logie.blizz.wow.WowLayout(File(files, "files"), File(files, ".export"))
        assertEquals(File(File(files, "files"), "converter"), layout.converted)
        assertEquals(layout.converted, ConverterRuntime.paths(files, layout.converted).output)
    }

    @Test fun theRuntimeIsInstalledOnlyWithItsMarkerPythonAndDriver() {
        val paths = ConverterRuntime.paths(tmp.newFolder("files"))
        assertFalse(ConverterRuntime.isInstalled(paths))
        paths.python.parentFile!!.mkdirs(); paths.python.writeText("#!/bin/sh")
        paths.driver.parentFile!!.mkdirs(); paths.driver.writeText("x")
        assertFalse(ConverterRuntime.isInstalled(paths))
        File(paths.folder, ConverterRuntime.MARKER).writeText("a".repeat(64))
        assertTrue(ConverterRuntime.isInstalled(paths))
        assertEquals("a".repeat(64), ConverterRuntime.installedSha(paths))
    }
}
