package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

@org.junit.runner.RunWith(org.robolectric.RobolectricTestRunner::class)
@org.robolectric.annotation.Config(sdk = [34])
class WowLoginTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun theSavedLoginIsReadFromTheExportsPrefs() {
        val f = tmp.newFile("login.json")
        f.writeText("""{"name": {"type": "string", "value": "LOGIE"}, "password": {"type": "string", "value": "pa ss"}}""")
        assertEquals(WowLogin.Login("LOGIE", "pa ss"), WowLogin.read(f))
        assertNull(WowLogin.read(tmp.newFile("none.json").also { it.delete() }))
        assertNull(WowLogin.read(tmp.newFile("bad.json").also { it.writeText("{}") }))
    }
}
