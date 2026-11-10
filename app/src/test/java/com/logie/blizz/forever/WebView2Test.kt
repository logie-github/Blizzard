package com.logie.blizz.forever

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class WebView2Test {
    private fun zip(file: File, entries: Map<String, ByteArray>) {
        ZipOutputStream(file.outputStream()).use { out ->
            for ((name, bytes) in entries) {
                out.putNextEntry(ZipEntry(name)); out.write(bytes); out.closeEntry()
            }
        }
    }

    @Test
    fun `unpack takes only the WebView2 files, flattened, and refuses traversal`() {
        val dir = Files.createTempDirectory("wv2").toFile()
        val nupkg = File(dir, "pkg.nupkg")
        zip(nupkg, mapOf(
            "contentFiles/any/any/WebView2/msedgewebview2.exe" to ByteArray(2_000_000),
            "contentFiles/any/any/WebView2/EBWebView/x64/locales/en-US.pak" to byteArrayOf(1, 2, 3),
            "lib/net45/Microsoft.Web.WebView2.Core.dll" to byteArrayOf(9), // not runtime: skipped
            "contentFiles/any/any/WebView2/../../../evil.exe" to byteArrayOf(0), // traversal: skipped
            "[Content_Types].xml" to byteArrayOf(0),
        ))
        val into = File(dir, "out")
        WebView2.unpack(nupkg, into)
        assertTrue(File(into, "msedgewebview2.exe").isFile)
        assertEquals(2_000_000L, File(into, "msedgewebview2.exe").length())
        assertArrayEquals(byteArrayOf(1, 2, 3), File(into, "EBWebView/x64/locales/en-US.pak").readBytes())
        assertFalse(File(into, "Microsoft.Web.WebView2.Core.dll").exists())
        assertFalse(File(dir, "evil.exe").exists())
    }

    @Test
    fun `installed is true only once the runtime's program is in place`() {
        val driveC = Files.createTempDirectory("drivec").toFile()
        assertFalse(WebView2.installed(driveC))
        val exe = File(WebView2.runtimeDir(driveC), "msedgewebview2.exe")
        exe.parentFile?.mkdirs()
        exe.writeBytes(ByteArray(500)) // a stub doesn't count
        assertFalse(WebView2.installed(driveC))
        exe.writeBytes(ByteArray(2_000_000))
        assertTrue(WebView2.installed(driveC))
    }

    @Test
    fun `the environment points the launcher at the fixed runtime with no-sandbox software GL`() {
        val env = WebView2.ENV.toMap()
        assertEquals("C:\\webview2", env["WEBVIEW2_BROWSER_EXECUTABLE_FOLDER"])
        assertTrue(env.getValue("WEBVIEW2_USER_DATA_FOLDER").startsWith("C:\\"))
        val args = env.getValue("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS")
        assertTrue("--no-sandbox" in args && "--disable-gpu" in args && "swiftshader" in args)
    }

    private fun assertArrayEquals(a: ByteArray, b: ByteArray) = org.junit.Assert.assertArrayEquals(a, b)
}
