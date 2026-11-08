package com.logie.blizz.wowmodules

import org.json.JSONObject
import kotlin.random.Random
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ModuleBuildTest {
    private val sha1 = "1111111111111111111111111111111111111111"
    private val sha2 = "2222222222222222222222222222222222222222"
    private val transmog = ModuleBuild.Chosen("azerothcore/mod-transmog", "master", "Transmog", "https://a/1", sha1)
    private val ahbot = ModuleBuild.Chosen("azerothcore/mod-ah-bot", "master", null, null, sha2)

    @Test
    fun requests() {
        val request = ModuleBuild.newRequest(Random(7))
        assertEquals(12, request.length)
        assertTrue(ModuleBuild.isRequest(request))
        assertFalse(ModuleBuild.isRequest("short"))
        assertFalse(ModuleBuild.isRequest("UPPERCASE123"))
        assertFalse(ModuleBuild.isRequest("with space 12"))
        assertEquals("server-abc123def456.tar.xz", ModuleBuild.assetName("abc123def456"))
        assertEquals("46:modules:abc123def456", ModuleBuild.stamp(ModuleBuild.Built(46, "abc123def456", emptyList())))
    }

    @Test
    fun theModulesAskedFor() {
        val playerbots = ModuleBuild.Chosen("liyunfan1223/mod-playerbots", "master", commit = sha1)
        val unpinned = ModuleBuild.Chosen("someone/mod-x", "main")
        val twice = ModuleBuild.Chosen("fork/mod-transmog", "master", commit = sha2)
        assertEquals(
            "azerothcore/mod-transmog@$sha1\nazerothcore/mod-ah-bot@$sha2",
            ModuleBuild.modulesInput(listOf(transmog, playerbots, unpinned, ahbot, twice), setOf("mod-playerbots")),
        )
        val body = JSONObject(ModuleBuild.dispatchBody("main", "abc123def456", "a/b@$sha1"))
        assertEquals("main", body.getString("ref"))
        val inputs = body.getJSONObject("inputs")
        assertFalse(inputs.has("release"))
        assertEquals("abc123def456", inputs.getString("request"))
        assertEquals("a/b@$sha1", inputs.getString("modules"))
    }

    @Test
    fun branches() {
        assertTrue(ModuleBuild.isBranch("master"))
        assertTrue(ModuleBuild.isBranch("release/3.3.5"))
        assertFalse(ModuleBuild.isBranch(""))
        assertFalse(ModuleBuild.isBranch("../etc"))
        assertFalse(ModuleBuild.isBranch("a b"))
        assertFalse(ModuleBuild.isBranch("/root"))
        assertFalse(ModuleBuild.isBranch("x.lock"))
    }

    @Test
    fun findsItsRun() {
        val runs = """
            {"total_count": 2, "workflow_runs": [
              {"id": 9, "display_title": "Modules zzzzzzzzzzzz for wow-build-46", "status": "completed", "conclusion": "success", "html_url": "https://github.com/r/actions/runs/9"},
              {"id": 8, "display_title": "Modules abc123def456 for wow-build-46", "status": "in_progress", "conclusion": null, "html_url": "https://github.com/r/actions/runs/8"}
            ]}
        """.trimIndent()
        val run = ModuleBuild.findRun(runs, "abc123def456")!!
        assertEquals(8L, run.id)
        assertEquals("in_progress", run.status)
        assertNull(run.conclusion)
        assertFalse(run.isDone)
        assertEquals("https://github.com/r/actions/runs/8", run.url)
        assertNull(ModuleBuild.findRun(runs, "nothere12345"))
        assertNull(ModuleBuild.findRun("{}", "abc123def456"))

        val done = ModuleBuild.parseRun("""{"id": 8, "status": "completed", "conclusion": "failure", "html_url": "u"}""")
        assertTrue(done.isDone)
        assertFalse(done.succeeded)
    }

    @Test
    fun theStepItsOn() {
        val going = """
            {"jobs": [{"name": "Realm with the modules (build and test)", "steps": [
              {"name": "Set up job", "status": "completed", "conclusion": "success"},
              {"name": "Check what was asked", "status": "completed", "conclusion": "success"},
              {"name": "Run actions/checkout@v4", "status": "completed", "conclusion": "success"},
              {"name": "Compile the server", "status": "in_progress", "conclusion": null},
              {"name": "Package the server", "status": "queued", "conclusion": null}
            ]}]}
        """.trimIndent()
        assertEquals("Compile the server", ModuleBuild.currentStep(going))
        val failed = going.replace("\"in_progress\", \"conclusion\": null}", "\"completed\", \"conclusion\": \"failure\"}")
        assertEquals("Compile the server", ModuleBuild.currentStep(failed))
        val between = """
            {"jobs": [
              {"steps": [{"name": "Keep the package for the release", "status": "completed", "conclusion": "success"},
                         {"name": "Post Run actions/checkout@v4", "status": "completed", "conclusion": "success"},
                         {"name": "Complete job", "status": "completed", "conclusion": "success"}]},
              {"steps": []}
            ]}
        """.trimIndent()
        assertEquals("Keep the package for the release", ModuleBuild.currentStep(between))
        assertNull(ModuleBuild.currentStep("{\"jobs\": []}"))
    }

    @Test
    fun keptAsJson() {
        val chosen = listOf(transmog, ahbot.copy(commit = null))
        assertEquals(chosen, ModuleBuild.chosenFromJson(ModuleBuild.chosenToJson(chosen)))
        // Anything off is left out.
        val bad = org.json.JSONArray()
            .put(JSONObject().put("fullName", "not a name").put("branch", "master"))
            .put(JSONObject().put("fullName", "a/b").put("branch", "../x"))
            .put(JSONObject().put("fullName", "a/b").put("branch", "main").put("commit", "nope"))
            .put("a string")
        assertEquals(emptyList<Any>(), ModuleBuild.chosenFromJson(bad))

        val built = ModuleBuild.Built(46, "abc123def456", listOf(transmog), 1234L)
        assertEquals(built, ModuleBuild.builtFromJson(ModuleBuild.builtToJson(built)))
        assertNull(ModuleBuild.builtFromJson("""{"versionCode": 46, "request": "BAD", "modules": []}"""))
        assertNull(ModuleBuild.builtFromJson("not json"))
        assertNull(ModuleBuild.builtFromJson(null))

        val pending = ModuleBuild.Pending("abc123def456", "wow-build-46", 46, listOf(transmog), 100L)
        assertEquals(pending, ModuleBuild.pendingFromJson(ModuleBuild.pendingToJson(pending)))
        val run = ModuleBuild.Run(8, "completed", "success", "https://github.com/r/actions/runs/8")
        val seen = ModuleBuild.seen(pending, run, "Attach it", 200L)
        assertEquals(seen, ModuleBuild.pendingFromJson(ModuleBuild.pendingToJson(seen)))
        assertTrue(seen.succeeded)
        assertFalse(seen.failed)
        assertEquals(8L, seen.runId)
        assertEquals("Attach it", seen.step)
        // A refresh that sees no step keeps the last one.
        assertEquals("Attach it", ModuleBuild.seen(seen, run, null, 300L).step)
        assertTrue(ModuleBuild.seen(pending, run.copy(conclusion = "cancelled"), null, 1L).failed)
        // What went in, once read; a pending file from before builds kept a record has none read yet.
        val read = seen.copy(leftOut = listOf(ModuleBuild.LeftOut("mod-ah-bot", "src/a.h:1: error: x")))
        assertEquals(read, ModuleBuild.pendingFromJson(ModuleBuild.pendingToJson(read)))
        assertEquals(emptyList<Any>(), ModuleBuild.pendingFromJson(ModuleBuild.pendingToJson(seen.copy(leftOut = emptyList())))!!.leftOut)
        assertNull(ModuleBuild.pendingFromJson("""{"request": "abc123def456", "release": "wow-build-46", "versionCode": 46}""")!!.leftOut)
    }

    @Test
    fun whatTheBuildLeftOut() {
        // The workflow's build.json (server-<request>.json on the release).
        val record = """
            {"modules": ["mod-worgoblin", "mod-weekendbonus"],
             "leftOut": [
               {"name": "DungeonRespawn", "error": "src/DungeonRespawn.h:45:10: error: 'bool DSPlayerScript::OnBeforeTeleport' marked 'override', but does not override"},
               {"name": "bad name/../x", "error": "x"},
               {"name": "mod-long", "error": "${"e".repeat(500)}"}
             ]}
        """.trimIndent()
        val leftOut = ModuleBuild.parseLeftOut(record)
        assertEquals(listOf("DungeonRespawn", "mod-long"), leftOut.map { it.name })
        assertTrue(leftOut[0].error.startsWith("src/DungeonRespawn.h:45:10: error:"))
        assertEquals(300, leftOut[1].error.length)
        assertEquals(emptyList<Any>(), ModuleBuild.parseLeftOut("""{"modules": ["a"], "leftOut": []}"""))
        assertEquals(emptyList<Any>(), ModuleBuild.parseLeftOut("{}"))
        assertEquals("server-abc123def456.json", ModuleBuild.recordName("abc123def456"))

        val respawn = ModuleBuild.Chosen("AnchyDev/DungeonRespawn", "main", commit = sha1)
        assertEquals(listOf(transmog), ModuleBuild.without(listOf(transmog, respawn), leftOut))
        assertEquals(listOf(transmog, respawn), ModuleBuild.without(listOf(transmog, respawn), emptyList()))
    }

    @Test
    fun theRealmsKept() {
        val one = ModuleBuild.Built(49, "abc123def456", listOf(transmog), 1000L, listOf(ModuleBuild.LeftOut("DungeonRespawn", "e")), 93_000_000L)
        val two = ModuleBuild.Built(48, "zzz999yyy888", listOf(transmog, ahbot), 900L)
        val list = listOf(one, two)
        assertEquals(list, ModuleBuild.savedFromJson(ModuleBuild.savedToJson(list)))
        assertEquals(one, ModuleBuild.builtFromJson(ModuleBuild.builtToJson(one)))
        // realm.json from before realms were kept: nothing left out, no size.
        assertEquals(
            ModuleBuild.Built(46, "abc123def456", listOf(transmog), 1234L),
            ModuleBuild.builtFromJson("""{"versionCode": 46, "request": "abc123def456", "modules": ${ModuleBuild.chosenToJson(listOf(transmog))}, "builtAt": 1234}"""),
        )
        // The same build twice, a bad entry and bad JSON.
        assertEquals(listOf(one), ModuleBuild.savedFromJson(ModuleBuild.savedToJson(listOf(one, one.copy(builtAt = 5L)))))
        assertEquals(listOf(one), ModuleBuild.savedFromJson("[{\"request\": \"BAD\"}, ${ModuleBuild.builtToJson(one)}, 3]"))
        assertEquals(emptyList<Any>(), ModuleBuild.savedFromJson("not json"))
        assertEquals(emptyList<Any>(), ModuleBuild.savedFromJson(null))
    }
}
