package com.logie.blizz.forever

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.file.Files

class WebView2Test {
    @Test
    fun `the installer lives under webview2 in the Forever folder`() {
        val root = Files.createTempDirectory("forever").toFile()
        assertEquals("webview2", WebView2.dir(root).name)
        assertEquals("MicrosoftEdgeWebView2Setup.exe", WebView2.installerIn(root).name)
        assertEquals(WebView2.dir(root), WebView2.installerIn(root).parentFile)
    }

    @Test
    fun `downloaded is true only for a whole installer file`() {
        val root = Files.createTempDirectory("forever").toFile()
        assertFalse(WebView2.downloaded(root))
        val installer = WebView2.installerIn(root)
        installer.parentFile?.mkdirs()
        // A stub (an interrupted download) doesn't count.
        installer.writeBytes(ByteArray(500))
        assertFalse(WebView2.downloaded(root))
        // A plausibly-whole file does.
        installer.writeBytes(ByteArray(2_000_000))
        assertTrue(WebView2.downloaded(root))
    }
}
