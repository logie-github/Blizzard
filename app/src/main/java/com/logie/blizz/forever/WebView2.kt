package com.logie.blizz.forever

import android.content.Context
import java.io.File
import java.net.HttpURLConnection
import java.net.URL

/**
 * The Forever Launcher is a Tauri app: its window is drawn by Microsoft's WebView2 runtime (Edge/Chromium), which
 * isn't in the games' Windows. Without it the launcher stops at "A Windows component is missing" and can't do its
 * job (write the realm's server key into the client). This downloads Microsoft's own WebView2 runtime installer and
 * runs it once in the shared Wine container, so the launcher finds the runtime at the next Play.
 *
 * This is the supported way to add WebView2 (the Evergreen Standalone installer, which carries the runtime and
 * installs with no network). Whether a Chromium runtime actually renders under Wine through Box64 on the phone is
 * not something that can be checked here; this provides the runtime, and the launcher is the test.
 */
object WebView2 {
    /** Microsoft Edge WebView2 Evergreen **Standalone** installer (x64): carries the runtime, installs offline. */
    const val INSTALLER_URL = "https://go.microsoft.com/fwlink/?linkid=2124701"

    private const val INSTALLER_NAME = "MicrosoftEdgeWebView2Setup.exe"
    private const val MIN_SIZE = 1_000_000L

    /** Where the downloaded installer is kept (under the Forever folder, which is drive F: in the container). */
    fun dir(root: File) = File(root, "webview2")
    fun installerIn(root: File) = File(dir(root), INSTALLER_NAME)
    fun dir(context: Context) = dir(ForeverLayout.of(context).root)
    fun installer(context: Context) = installerIn(ForeverLayout.of(context).root)

    /** Whether the installer has already been fetched (a complete, non-empty file). */
    fun downloaded(root: File) = installerIn(root).let { it.isFile && it.length() > MIN_SIZE }
    fun downloaded(context: Context) = downloaded(ForeverLayout.of(context).root)

    /**
     * Downloads the WebView2 installer (about 210 MB) to [installer], resuming isn't needed (Microsoft serves it
     * whole). [onProgress] gets bytes done and the total (or -1 before it's known). Off the main thread. Returns the
     * file, or throws.
     */
    fun download(context: Context, onProgress: (Long, Long) -> Unit): File {
        val target = installer(context)
        if (downloaded(context)) return target
        target.parentFile?.mkdirs()
        val part = File(target.parentFile, target.name + ".part")
        var connection = URL(INSTALLER_URL).openConnection() as HttpURLConnection
        // fwlink redirects to the CDN; follow it (including https->https, which HttpURLConnection won't do on its own).
        var redirects = 0
        while (true) {
            connection.instanceFollowRedirects = true
            connection.connectTimeout = 30_000
            connection.readTimeout = 60_000
            val code = connection.responseCode
            if (code in 300..399 && redirects < 5) {
                val location = connection.getHeaderField("Location") ?: break
                connection.disconnect()
                connection = URL(URL(INSTALLER_URL), location).openConnection() as HttpURLConnection
                redirects++
                continue
            }
            if (code != HttpURLConnection.HTTP_OK) throw java.io.IOException("WebView2 download failed: HTTP $code")
            break
        }
        val total = connection.contentLengthLong
        connection.inputStream.use { input ->
            part.outputStream().buffered(1 shl 16).use { out ->
                val buffer = ByteArray(1 shl 16)
                var done = 0L
                onProgress(0, total)
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    done += n
                    onProgress(done, total)
                }
            }
        }
        connection.disconnect()
        if (part.length() < MIN_SIZE) { part.delete(); throw java.io.IOException("WebView2 download was incomplete (${part.length()} bytes)") }
        if (!part.renameTo(target)) { target.delete(); if (!part.renameTo(target)) throw java.io.IOException("Couldn't put the WebView2 installer in place") }
        return target
    }
}
