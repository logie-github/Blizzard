package com.logie.blizz.wow

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WowLoginOwnTest {
    private val context: Context get() = ApplicationProvider.getApplicationContext()

    private fun exportLogin(layout: WowLayout, file: String, name: String, password: String) {
        File(layout.prefsDir, file).apply { parentFile!!.mkdirs() }
            .writeText("""{"name":{"type":"string","value":"$name"},"password":{"type":"string","value":"$password"}}""")
    }

    @Test
    fun everyVersionTakesItsOwnLoginBeforeTheExportedOne() {
        WowLogin.clearOwn(context, WowLogin.WRATH); WowLogin.clearOwn(context, WowLogin.OCTO); WowLogin.clearOwn(context, WowLogin.LEGION)
        assertNull(WowLogin.forVersion(context, WowLogin.OCTO))

        exportLogin(WowLayout.of(context), "login.json", "wrath", "w1")
        exportLogin(WowLayout.octo(context), "turtle_login.json", "octo", "o1")
        exportLogin(WowLayout.legion(context), "felsong_login.json", "me@x.y", "l1")
        assertEquals(WowLogin.Login("wrath", "w1"), WowLogin.forVersion(context, WowLogin.WRATH))
        assertEquals(WowLogin.Login("octo", "o1"), WowLogin.forVersion(context, WowLogin.OCTO))
        assertEquals(WowLogin.Login("me@x.y", "l1"), WowLogin.forVersion(context, WowLogin.LEGION))

        WowLogin.setOwn(context, WowLogin.OCTO, " mine ", "secret")
        assertEquals(WowLogin.Login("mine", "secret"), WowLogin.forVersion(context, WowLogin.OCTO))
        assertEquals(WowLogin.Login("wrath", "w1"), WowLogin.forVersion(context, WowLogin.WRATH))

        WowLogin.clearOwn(context, WowLogin.OCTO)
        assertEquals(WowLogin.Login("octo", "o1"), WowLogin.forVersion(context, WowLogin.OCTO))
    }

    @Test
    fun aVersionWithNothingExportedStillLogsInOnceItHasItsOwn() {
        WowLogin.clearOwn(context, WowLogin.LEGION)
        File(WowLayout.legion(context).prefsDir, "felsong_login.json").delete()
        assertNull(WowLogin.forVersion(context, WowLogin.LEGION))
        WowLogin.setOwn(context, WowLogin.LEGION, "a@b.c", "pw")
        assertEquals(WowLogin.Login("a@b.c", "pw"), WowLogin.forVersion(context, WowLogin.LEGION))
        assertEquals(WowLogin.LEGION, WowLogin.versionOf(com.logie.blizz.game.LegionClientSetup.VERSION))
        assertEquals(WowLogin.OCTO, WowLogin.versionOf(com.logie.blizz.game.OctoClientSetup.VERSION))
        assertEquals(WowLogin.WRATH, WowLogin.versionOf("3.3.5a"))
    }
}
