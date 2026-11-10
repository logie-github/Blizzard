package com.logie.blizz.forever

import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.util.zip.ZipInputStream

/**
 * The Forever Launcher is a Tauri app: its window is drawn by Microsoft's WebView2 runtime (Edge/Chromium). The
 * games' Windows doesn't have it, and Microsoft's own installer fails under Wine (its updater can't start services:
 * report #83, `0x80040708`). So instead of installing, this places the **fixed-version** WebView2 runtime — the
 * loose files, no installer, no updater — into the container and points the launcher at it with an environment
 * variable. The runtime is Microsoft's, redistributed through the `WebView2.Runtime.X64` NuGet package (a plain zip
 * on a stable URL), pinned to **145.0.3800.97**: the version the launcher was built for, and old enough to accept
 * the software-GL flag that newer runtimes reject under Wine (`--use-gl=swiftshader`, WebView2Feedback #5720).
 *
 * Whether a Chromium runtime renders under Wine through Box64 is still unproven on a phone — but this removes the
 * install failure and uses the runtime most likely to work; the launcher opening is the test.
 */
object WebView2 {
    const val VERSION = "145.0.3800.97"

    /** The NuGet package (a zip) that carries the fixed-version runtime. Stable, permanent URL. */
    const val NUPKG_URL = "https://api.nuget.org/v3-flatcontainer/webview2.runtime.x64/$VERSION/webview2.runtime.x64.$VERSION.nupkg"

    /** Inside the package, the runtime's files live under this folder. */
    const val ZIP_PREFIX = "contentFiles/any/any/WebView2/"

    /** Where the runtime is unpacked in the container (drive C:), and the matching Windows path. */
    const val DIR_NAME = "webview2"
    const val DIR_WINDOWS = "C:\\webview2"
    const val USER_DATA_WINDOWS = "C:\\users\\xuser\\AppData\\Local\\ForeverWebView2"

    /**
     * The environment the launcher's WebView2 is started with, written into the client's Wine `HKCU\Environment`
     * (which keeps spaces, unlike the container's env string): use the fixed runtime above, a writable data folder,
     * and the arguments Chromium needs under Wine — no sandbox (fails under Wine), software GL (no GPU under Box64;
     * 145 still accepts `swiftshader`), and no code-integrity check (fails under Wine).
     */
    val ENV: List<Pair<String, String>> = listOf(
        "WEBVIEW2_BROWSER_EXECUTABLE_FOLDER" to DIR_WINDOWS,
        "WEBVIEW2_USER_DATA_FOLDER" to USER_DATA_WINDOWS,
        "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS" to
            "--no-sandbox --disable-gpu --disable-gpu-compositing --use-angle=swiftshader --disable-features=RendererCodeIntegrity",
    )

    /** The runtime folder inside [driveC], and the program that proves it's unpacked. */
    fun runtimeDir(driveC: File) = File(driveC, DIR_NAME)
    private fun marker(driveC: File) = File(runtimeDir(driveC), "msedgewebview2.exe")

    /** Whether the runtime is already unpacked in the container (its main program present and non-trivial). */
    fun installed(driveC: File) = marker(driveC).let { it.isFile && it.length() > 1_000_000L }

    /**
     * Puts the fixed-version runtime into the container (drive C:) if it isn't there: downloads the NuGet zip and
     * unpacks its `WebView2/` files into `C:\webview2`. [onProgress] gets bytes done and the total (-1 before it's
     * known) during the download. Off the main thread. Returns the runtime folder, or throws.
     */
    fun provision(driveC: File, onProgress: (Long, Long) -> Unit): File {
        val dir = runtimeDir(driveC)
        if (installed(driveC)) return dir
        driveC.mkdirs()
        val temp = File(driveC, "$DIR_NAME.nupkg.part")
        download(NUPKG_URL, temp, onProgress)
        val staging = File(driveC, "$DIR_NAME.new")
        staging.deleteRecursively(); staging.mkdirs()
        unpack(temp, staging)
        temp.delete()
        if (!File(staging, "msedgewebview2.exe").isFile) { staging.deleteRecursively(); throw java.io.IOException("WebView2 runtime package had no msedgewebview2.exe") }
        dir.deleteRecursively()
        if (!staging.renameTo(dir)) { staging.deleteRecursively(); throw java.io.IOException("Couldn't put the WebView2 runtime in place") }
        return dir
    }

    /** Unpacks the `WebView2/` entries of the NuGet zip [nupkg] into [into] (flattened: the prefix is stripped). */
    fun unpack(nupkg: File, into: File) {
        ZipInputStream(nupkg.inputStream().buffered(1 shl 16)).use { zip ->
            while (true) {
                val entry = zip.nextEntry ?: break
                val name = entry.name.replace('\\', '/')
                if (!name.startsWith(ZIP_PREFIX)) { zip.closeEntry(); continue }
                val rel = name.removePrefix(ZIP_PREFIX)
                if (rel.isEmpty() || rel.contains("..")) { zip.closeEntry(); continue }
                val target = File(into, rel)
                if (entry.isDirectory) { target.mkdirs(); zip.closeEntry(); continue }
                target.parentFile?.mkdirs()
                target.outputStream().buffered(1 shl 16).use { out ->
                    val buf = ByteArray(1 shl 16)
                    while (true) { val n = zip.read(buf); if (n < 0) break; out.write(buf, 0, n) }
                }
                zip.closeEntry()
            }
        }
    }

    private fun download(url: String, target: File, onProgress: (Long, Long) -> Unit) {
        var connection = URL(url).openConnection() as HttpURLConnection
        var redirects = 0
        while (true) {
            connection.instanceFollowRedirects = true
            connection.connectTimeout = 30_000
            connection.readTimeout = 60_000
            val code = connection.responseCode
            if (code in 300..399 && redirects < 5) {
                val location = connection.getHeaderField("Location") ?: break
                connection.disconnect()
                connection = URL(URL(url), location).openConnection() as HttpURLConnection
                redirects++
                continue
            }
            if (code != HttpURLConnection.HTTP_OK) throw java.io.IOException("WebView2 runtime download failed: HTTP $code")
            break
        }
        val total = connection.contentLengthLong
        connection.inputStream.use { input ->
            target.outputStream().buffered(1 shl 16).use { out ->
                val buf = ByteArray(1 shl 16)
                var done = 0L
                onProgress(0, total)
                while (true) {
                    val n = input.read(buf)
                    if (n < 0) break
                    out.write(buf, 0, n); done += n
                    onProgress(done, total)
                }
            }
        }
        connection.disconnect()
        if (target.length() < 1_000_000L) { target.delete(); throw java.io.IOException("WebView2 runtime download was incomplete (${target.length()} bytes)") }
    }
}
