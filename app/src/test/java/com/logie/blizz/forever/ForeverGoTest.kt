package com.logie.blizz.forever

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File

@RunWith(RobolectricTestRunner::class)
class ForeverGoTest {
    @Test fun `the login body is the game's own form`() {
        val body = JSONObject(ForeverGo.loginBody("forever@forever.local", "pa\"ss"))
        assertEquals("1.0", body.getString("version"))
        val inputs = body.getJSONArray("inputs")
        assertEquals("account_name", inputs.getJSONObject(0).getString("input_id"))
        assertEquals("forever@forever.local", inputs.getJSONObject(0).getString("value"))
        assertEquals("password", inputs.getJSONObject(1).getString("input_id"))
        assertEquals("pa\"ss", inputs.getJSONObject(1).getString("value"))
    }

    @Test fun `the ticket is read from the realm's answer`() {
        // The answer of the rig's realm, 14 November 2026.
        assertEquals("TC-D174C0CE6C923C98E0BFCBCCC80D01B2BF776008",
            ForeverGo.ticketOf("{\"authentication_state\":\"DONE\",\"login_ticket\":\"TC-D174C0CE6C923C98E0BFCBCCC80D01B2BF776008\"}"))
        assertNull(ForeverGo.ticketOf("{\"authentication_state\":\"LOGIN\",\"error_code\":\"UNABLE_TO_DECODE\"}"))
        assertNull(ForeverGo.ticketOf("{\"login_ticket\":\"bad ticket\\n\"}"))
        assertNull(ForeverGo.ticketOf("<html>"))
    }

    @Test fun `the game account is the first one in good standing`() {
        assertEquals("WoW1", ForeverGo.accountOf("{\"game_accounts\":[{\"display_name\":\"WoW1\",\"expansion\":11}]}"))
        assertEquals("WoW2", ForeverGo.accountOf("{\"game_accounts\":[{\"display_name\":\"WoW1\",\"is_banned\":true},{\"display_name\":\"WoW2\"}]}"))
        assertNull(ForeverGo.accountOf("{\"game_accounts\":[]}"))
        assertNull(ForeverGo.accountOf("{}"))
    }

    @Test fun `the sign-in file and the wrapper`() {
        assertEquals("WoW1\nTC-1\n8105\n", ForeverGo.loginFile("WoW1", "TC-1"))
        assertEquals("C:\\windows\\forevergo.exe C:\\windows\\borderless.exe /noframes", ForeverGo.wrapper("C:\\windows\\borderless.exe /noframes"))
    }

    /** Against a running realm (the rig: README, "The Forever client and realm on the rig"): BLIZZ_FOREVER_REALM=1. */
    @Test fun `signs in at a running realm`() {
        assumeTrue(System.getenv("BLIZZ_FOREVER_REALM") == "1")
        val ca = File("/data/data/com.logie.blizz/files/forever/ca/ca.pem")
        val (account, ticket) = ForeverGo.signIn(ca, "forever@forever.local", "forever")
        assertEquals("WoW1", account)
        assertEquals(true, ticket.startsWith("TC-"))
    }
}
