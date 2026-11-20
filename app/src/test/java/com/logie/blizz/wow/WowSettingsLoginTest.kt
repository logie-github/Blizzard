package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** The login server reads the realms' states every 2 s (a game started while the world loads logs in once it is up). */
class WowSettingsLoginTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun theLoginServerReadsRealmStatesEveryTwoSeconds() {
        val l = WowLayout(tmp.newFolder("files"), tmp.newFolder(".export"))
        l.etc.mkdirs()
        val auth = File(l.etc, "authserver.conf").apply { writeText("LogLevel = 1\nRealmsStateUpdateDelay = 20\n") }
        WowSettings.apply(l)
        assertEquals("LogLevel = 1\nRealmsStateUpdateDelay = 2\n", auth.readText())
    }

    @Test fun noLoginServerConfigIsMadeWhereThereIsNone() {
        val l = WowLayout(tmp.newFolder("files"), tmp.newFolder(".export"))
        l.etc.mkdirs()
        WowSettings.apply(l)
        assertFalse(File(l.etc, "authserver.conf").exists())
    }
}
