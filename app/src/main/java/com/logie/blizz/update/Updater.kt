package com.logie.blizz.update

import com.logie.blizz.importer.deleteTree

import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.content.FileProvider
import androidx.core.content.pm.PackageInfoCompat
import com.logie.blizz.BuildConfig
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import org.json.JSONArray
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/**
 * Updates from this repository's GitHub releases (blizzard-build-N, where N is the version code),
 * as YeaBwoi's apps update: checked each time the app comes to the front; a newer one is downloaded by itself
 * and handed to Android's installer, which asks for the one tap Android requires.
 */
object Updater {
    data class Update(val versionCode: Int, val title: String, val apkName: String, val apkUrl: String, val size: Long)

    sealed interface State {
        data object Idle : State
        data class Downloading(val update: Update, val done: Long, val total: Long) : State
        /** Downloaded; Android's installer is open, or waits for "install unknown apps" to be allowed. */
        data class Ready(val update: Update, val apk: File, val needsPermission: Boolean) : State
        data class Failed(val message: String) : State
    }

    class HttpException(val code: Int) : IOException("HTTP $code")
    class WrongApkException : IOException("Not an update for this app")

    private const val API_HOST = "api.github.com"
    private const val MAX_REDIRECTS = 5

    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    @Volatile private var lastCheck = 0L
    private const val RECHECK_MS = 5 * 60 * 1000L

    /** Each time the app comes to the front (at most every few minutes): look, and if there's a newer build, fetch it and open the installer. */
    fun checkAndInstall(context: Context) {
        val now = System.currentTimeMillis()
        if (_state.value is State.Downloading || _state.value is State.Ready) return
        if (now - lastCheck < RECHECK_MS) return
        lastCheck = now
        val app = context.applicationContext
        scope.launch {
            runCatching { clearInstalledUpdate(app) }
            // Offline or GitHub unreachable: carry on, and look again next time.
            val update = runCatching { findUpdate(app) }.getOrNull() ?: return@launch
            try {
                _state.value = State.Downloading(update, 0, update.size)
                val apk = download(app, update) { done, total -> _state.value = State.Downloading(update, done, total) }
                ready(app, update, apk)
            } catch (e: Exception) {
                com.logie.blizz.reports.BugReports.report(
                    app, "App update download", e.message ?: "IOException",
                    listOf("Update" to update.title, "Size" to update.size.toString()), log = e.stackTraceToString(),
                )
                _state.value = State.Failed("The update couldn't be downloaded (${e.message}). What arrived is kept: it carries on next time.")
            }
        }
    }

    /**
     * What is left of an update that is no longer one goes (230 MB of nothing): the downloaded build that is running now,
     * and half a download of it or of an older one. Half a download of a newer build stays: [download] carries on with it.
     */
    fun clearInstalledUpdate(context: Context) {
        val dir = File(context.cacheDir, "updates")
        dir.listFiles()?.forEach { f ->
            val code = if (f.name.endsWith(".apk")) runCatching { context.packageManager.getPackageArchiveInfo(f.path, 0)?.let { PackageInfoCompat.getLongVersionCode(it) } }.getOrNull() else null
            if (stale(f.name, code, BuildConfig.VERSION_CODE.toLong())) f.deleteTree()
        }
    }

    /** Whether a file of the updates' folder is of no use to a build numbered [current]: [apkCode] is a finished APK's own number. */
    internal fun stale(name: String, apkCode: Long?, current: Long): Boolean = when {
        name.endsWith(".part") -> (name.substringBefore('-').toLongOrNull() ?: 0L) <= current
        name.endsWith(".apk") -> (apkCode ?: 0L) <= current
        else -> true
    }

    private fun ready(context: Context, update: Update, apk: File) {
        val allowed = canInstall(context)
        _state.value = State.Ready(update, apk, needsPermission = !allowed)
        if (allowed) context.startActivity(installIntent(context, apk))
    }

    /** Back from Android's "install unknown apps" setting: on to the installer if it's allowed now. */
    fun retryInstall(context: Context) {
        val s = _state.value as? State.Ready ?: return
        // Only the return from the "install unknown apps" setting starts the installer again: after a cancel it would otherwise pop up at every resume.
        if (!s.needsPermission) return
        ready(context.applicationContext, s.update, s.apk)
    }

    fun dismiss() {
        if (_state.value is State.Failed) _state.value = State.Idle
    }

    /** This app's releases on GitHub (the latest fifty), as the API lists them. */
    fun releasesJson(): String =
        connect("https://$API_HOST/repos/${BuildConfig.UPDATE_REPO}/releases?per_page=50", "application/vnd.github+json").let { c ->
            try { c.inputStream.bufferedReader().use { it.readText() } } finally { c.disconnect() }
        }

    /** The newest release if it's newer than this build, otherwise null. With [context], the releases' patch notes are kept ([PatchNotes]). */
    fun findUpdate(context: Context? = null): Update? {
        val body = releasesJson()
        context?.let { runCatching { PatchNotes.keep(it, body) } }
        val update = UpdatePicker.pick(parse(body), BuildConfig.RELEASE_TAG_PREFIX, BuildConfig.VERSION_CODE) ?: return null
        return Update(update.versionCode, update.title, update.apk.name, update.apk.url, update.apk.size)
    }

    fun parse(json: String): List<UpdatePicker.Release> {
        val array = JSONArray(json)
        return List(array.length()) { index ->
            val release = array.getJSONObject(index)
            val assets = release.optJSONArray("assets") ?: JSONArray()
            UpdatePicker.Release(
                tag = release.optString("tag_name"),
                title = release.optString("name"),
                draft = release.optBoolean("draft"),
                prerelease = release.optBoolean("prerelease"),
                assets = List(assets.length()) { i ->
                    val asset = assets.getJSONObject(i)
                    UpdatePicker.Asset(asset.optString("name"), asset.optString("url"), asset.optLong("size"))
                },
            )
        }
    }

    /**
     * [update]'s APK into the cache, checked to be a newer build of this app. A download that breaks off is carried on
     * from where it stopped, now ([fetch]) and at the next check (the half is kept under the build's number): 260 MB
     * over a phone's connection rarely arrives in one piece, and six in a row were started again from nothing (reports
     * #94 to #101).
     */
    fun download(context: Context, update: Update, onProgress: (Long, Long) -> Unit): File {
        val directory = File(context.cacheDir, "updates")
        directory.mkdirs()
        val target = File(directory, update.apkName.replace('/', '_'))
        val partial = File(directory, "${update.versionCode}-${target.name}.part")
        directory.listFiles()?.forEach { if (it != partial) it.deleteTree() }       // another build's, or a finished one's
        fetch(update.apkUrl, partial, update.size, onProgress)
        if (!partial.renameTo(target)) throw IOException("can't save the download")
        val info = context.packageManager.getPackageArchiveInfo(target.path, 0)
        if (info == null || info.packageName != context.packageName || PackageInfoCompat.getLongVersionCode(info) <= BuildConfig.VERSION_CODE) {
            target.delete()                                                             // not carried on with: from nothing next time
            throw WrongApkException()
        }
        return target
    }

    private const val MAX_STALLS = 5

    /**
     * [url]'s file of [size] bytes (0: not known) into [partial], carrying on from what [partial] already holds. A
     * connection that drops or times out is opened again for the rest, as long as each try brings more; [MAX_STALLS]
     * tries in a row that bring nothing give up (what arrived stays, for the next call). An answer that says the file
     * isn't there (HTTP 4xx) gives up at once.
     */
    internal fun fetch(url: String, partial: File, size: Long, onProgress: (Long, Long) -> Unit, pause: (Long) -> Unit = { Thread.sleep(it) }) {
        var stalls = 0
        while (true) {
            val before = partial.length()
            try {
                fetchRest(url, partial, size, onProgress)
                return
            } catch (e: IOException) {
                if (e is HttpException && e.code in 400..499 && e.code != 408 && e.code != 429) throw e
                stalls = if (partial.length() > before) 0 else stalls + 1
                if (stalls >= MAX_STALLS) throw e
                pause(minOf(500L shl stalls, 15000L))
            }
        }
    }

    private fun fetchRest(url: String, partial: File, size: Long, onProgress: (Long, Long) -> Unit) {
        if (size > 0 && partial.length() > size) partial.delete()
        val have = partial.length()
        if (size > 0 && have == size) return
        val connection = try {
            connect(url, "application/octet-stream", from = have)
        } catch (e: HttpException) {
            // "no such part": what is held isn't the start of this file (or is all of a file whose size wasn't known)
            if (e.code == 416) { partial.delete(); throw IOException("the download is started again") }
            throw e
        }
        try {
            var start = 0L
            if (connection.responseCode == HttpURLConnection.HTTP_PARTIAL) {
                // "bytes 1000-2999/3000": the rest, from where the half ends; anything else is not carried on with
                val from = connection.getHeaderField("Content-Range")?.substringAfter("bytes ", "")?.substringBefore('-')?.trim()?.toLongOrNull()
                if (from != have) { partial.delete(); throw IOException("the download is started again") }
                start = have
            }
            val length = connection.contentLengthLong
            val total = if (size > 0) size else if (length > 0) start + length else 0L
            var done = start
            connection.inputStream.use { input ->
                java.io.FileOutputStream(partial, start > 0).buffered(1 shl 20).use { output ->
                    val buffer = ByteArray(64 * 1024)
                    var shown = done
                    onProgress(done, total)
                    while (true) {
                        val read = input.read(buffer)
                        if (read < 0) break
                        output.write(buffer, 0, read)
                        done += read
                        if (done - shown > (1 shl 20)) { shown = done; onProgress(done, total) }
                    }
                }
            }
            if (total > 0 && done != total) throw IOException("download ended early")
        } finally {
            connection.disconnect()
        }
    }

    fun canInstall(context: Context): Boolean =
        Build.VERSION.SDK_INT < Build.VERSION_CODES.O || context.packageManager.canRequestPackageInstalls()

    fun installIntent(context: Context, apk: File): Intent {
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.filesprovider", apk)
        return Intent(Intent.ACTION_VIEW)
            .setDataAndType(uri, "application/vnd.android.package-archive")
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
    }

    /** Opens [url], following GitHub's redirects to its file servers by hand; [from]: the file from that byte on. */
    private fun connect(url: String, accept: String, from: Long = 0): HttpURLConnection {
        var current = URL(url)
        repeat(MAX_REDIRECTS + 1) {
            val connection = (current.openConnection() as HttpURLConnection).apply {
                instanceFollowRedirects = false
                connectTimeout = 10000
                readTimeout = 20000
                setRequestProperty("Accept", accept)
                if (from > 0) setRequestProperty("Range", "bytes=$from-")
                setRequestProperty("User-Agent", "${BuildConfig.APPLICATION_ID}/${BuildConfig.VERSION_NAME}")
                if (current.host == API_HOST) setRequestProperty("X-GitHub-Api-Version", "2022-11-28")
            }
            when (val code = connection.responseCode) {
                HttpURLConnection.HTTP_OK, HttpURLConnection.HTTP_PARTIAL -> return connection
                in 300..399 -> {
                    val location = connection.getHeaderField("Location")
                    connection.disconnect()
                    current = URL(current, location ?: throw HttpException(code))
                }
                else -> {
                    connection.disconnect()
                    throw HttpException(code)
                }
            }
        }
        throw IOException("too many redirects")
    }
}
