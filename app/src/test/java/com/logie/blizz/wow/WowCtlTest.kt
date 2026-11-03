package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File
import java.util.TimeZone

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WowCtlTest {
    @get:Rule val tmp = TemporaryFolder()

    /** The lines of the WoW app's ctl.sh that start programs (copied from warcraft/server/ctl.sh). */
    private val ctl = """
        SERVER="${'$'}FILES/server"
        		setkey "${'$'}conf" MySQLExecutable "\"${'$'}SERVER/bin/mariadb\""
        	LD_PRELOAD="${'$'}COMPAT" "${'$'}SERVER/bin/mariadb" --no-defaults -h127.0.0.1 "${'$'}@"
        	(cd "${'$'}RUN" && musl_programs && WOW_MODULES_CONF_DIR="${'$'}R_ETC/modules" "${'$'}SERVER/bin/dbimport" -c "${'$'}R_ETC/dbimport.conf")
        	exec "${'$'}SERVER/bin/mariadbd" --no-defaults --datadir="${'$'}DB_DIR" --basedir="${'$'}SERVER" \
        	exec "${'$'}SERVER/bin/mariadb-admin" --no-defaults -h127.0.0.1 ping
        	exec "${'$'}SERVER/bin/authserver" -c "${'$'}ETC/authserver.conf"
        	exec "${'$'}SERVER/bin/worldserver" -c "${'$'}R_ETC/worldserver.conf"
    """.trimIndent()

    private fun layout(): WowLayout {
        val game = tmp.newFolder("games", "wow")
        return WowLayout(File(game, "files").apply { mkdirs() }, File(game, ".export").apply { mkdirs() })
    }

    @Test fun everyProgramGoesThroughTheLoader() {
        val out = WowCtl.transform(ctl)
        val ld = "\"\$BLIZZ_LDSO\" --library-path \"\$SERVER/lib\""
        assertTrue("exec $ld \"\$SERVER/bin/worldserver\" -c" in out)
        assertTrue("exec $ld \"\$SERVER/bin/authserver\" -c" in out)
        assertTrue("exec $ld \"\$SERVER/bin/mariadbd\" --no-defaults" in out)
        assertTrue("exec $ld \"\$SERVER/bin/mariadb-admin\" --no-defaults" in out)
        assertTrue("LD_PRELOAD=\"\$COMPAT\" $ld \"\$SERVER/bin/mariadb\" --no-defaults" in out)
        assertTrue("WOW_MODULES_CONF_DIR=\"\$R_ETC/modules\" $ld \"\$SERVER/bin/dbimport\"" in out)
        // Every start of a program has the loader before it.
        out.lines().filter { "\$SERVER/bin/" in it && "MySQLExecutable" !in it }.forEach { line ->
            assertTrue(line, "$ld \"\$SERVER/bin/" in line)
        }
    }

    @Test fun theProgramsStartedByProgramsAreAScript() {
        val out = WowCtl.transform(ctl)
        assertTrue("MySQLExecutable \"\\\"\$SERVER/blizz/mariadb\\\"\"" in out)
        assertFalse("MySQLExecutable \"\\\"\$SERVER/bin/mariadb\\\"\"" in out)
    }

    @Test fun transformIsStable() {
        val once = WowCtl.transform(ctl)
        // (it is made from the imported ctl.sh each time, never from its own output)
        assertEquals(once, WowCtl.transform(ctl))
    }

    @Test fun commandHasTheShellScriptAndEnvironment() {
        val l = layout()
        val loader = File(l.server, "lib/ld-musl-aarch64.so.1")
        val c = WowCtl.command(l, loader, "<+0100>-01:00", "world", "remix")
        assertEquals(listOf("/system/bin/sh", File(l.server, "ctl.blizz.sh").path, "world", "remix"), c.argv)
        assertEquals(l.root.path, c.env["FILES"])
        assertEquals(loader.path, c.env["BLIZZ_LDSO"])
        assertEquals("<+0100>-01:00", c.env["TZ"])
        assertEquals(l.run, c.directory)
    }

    @Test fun posixTimeZone() {
        assertEquals("<+0530>-05:30", WowCtl.posixTimeZone(TimeZone.getTimeZone("Asia/Kolkata"), 0))
        assertEquals("<-0500>+05:00", WowCtl.posixTimeZone(TimeZone.getTimeZone("America/New_York"), 1_700_000_000_000))
        assertEquals("<+0000>-00:00", WowCtl.posixTimeZone(TimeZone.getTimeZone("UTC"), 0))
    }

    @Test fun prepareWritesTheScriptsAndFindsTheLoader() {
        val l = layout()
        File(l.server, "lib").mkdirs()
        File(l.server, "bin").mkdirs()
        File(l.server, "lib/ld-musl-aarch64.so.1").writeText("x")
        File(l.server, "bin/worldserver").writeText("x")
        l.ctl.writeText(ctl)

        val loader = WowCtl.prepare(l)

        assertEquals("ld-musl-aarch64.so.1", loader.name)
        assertTrue(l.blizzCtl.readText().contains("BLIZZ_LDSO"))
        assertEquals(ctl, l.ctl.readText())
        val wrapper = File(l.blizzBin, "mariadb").readText()
        assertTrue(wrapper.startsWith("#!/system/bin/sh\n"))
        assertTrue("exec \"${loader.path}\" --library-path \"${l.server.path}/lib\" \"${l.server.path}/bin/mariadb\" \"\$@\"" in wrapper)
        assertTrue(File(l.server, "bin/worldserver").canExecute())
        assertTrue(l.blizzCtl.canExecute())
        assertTrue(File(l.run, "tmp").isDirectory)
        assertTrue(File(l.logs, "remix").isDirectory)
        // A second time changes nothing.
        WowCtl.prepare(l)
        assertEquals(WowCtl.transform(ctl), l.blizzCtl.readText())
    }

    @Test fun prepareWithoutALoaderFails() {
        val l = layout()
        l.ctl.apply { parentFile!!.mkdirs(); writeText(ctl) }
        try {
            WowCtl.prepare(l)
            throw AssertionError("should have failed")
        } catch (e: java.io.IOException) {
            assertTrue(e.message!!.contains("loader"))
        }
    }

    @Test fun chosenRealmComesFromTheExportedPreferences() {
        val l = layout()
        assertEquals(Realm.CHROMIE, WowExportInfo.chosenRealm(l))
        l.prefsDir.mkdirs()
        File(l.prefsDir, "realms.json").writeText("{\n  \"realm\": {\"type\": \"string\", \"value\": \"remix\"}\n}\n")
        assertEquals(Realm.REMIX, WowExportInfo.chosenRealm(l))
        File(l.prefsDir, "realms.json").writeText("{\"realm\": {\"type\": \"string\", \"value\": \"main\"}}")
        assertEquals(Realm.CHROMIE, WowExportInfo.chosenRealm(l))
        File(l.prefsDir, "realms.json").writeText("{\"realm\": {\"type\": \"string\", \"value\": \"nope\"}}")
        assertEquals(Realm.CHROMIE, WowExportInfo.chosenRealm(l))
    }

    @Test fun sourceFilesDirFromTheManifest() {
        val l = layout()
        assertEquals(null, WowExportInfo.sourceFilesDir(l))
        l.manifest.writeText("{\"format\":1,\"sourceFilesDir\":\"/data/user/0/com.logie.warcraft/files\"}")
        assertEquals("/data/user/0/com.logie.warcraft/files", WowExportInfo.sourceFilesDir(l))
    }
}
