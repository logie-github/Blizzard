package com.logie.blizz.update

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
 * as YeaBwoi's apps update: checked each time the app opens; a newer one is downloaded by itself
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
    @Volatile private var checked = false

    /** Once per launch of the app: look, and if there's a newer build, fetch it and open the installer. */
    fun checkAndInstall(context: Context) {
        if (checked) return
        checked = true
        val app = context.applicationContext
        scope.launch {
            // Offline or GitHub unreachable: carry on, and look again next time.
            val update = runCatching { findUpdate() }.getOrNull() ?: return@launch
            try {
                _state.value = State.Downloading(update, 0, update.size)
                val apk = download(app, update) { done, total -> _state.value = State.Downloading(update, done, total) }
                ready(app, update, apk)
            } catch (e: IOException) {
                com.logie.blizz.reports.BugReports.report(
                    app, "App update download", e.message ?: "IOException",
                    listOf("Update" to update.title, "Size" to update.size.toString()), log = e.stackTraceToString(),
                )
                _state.value = State.Failed("The update couldn't be downloaded (${e.message}). It'll be tried again next time.")
            }
        }
    }

    private fun ready(context: Context, update: Update, apk: File) {
        val allowed = canInstall(context)
        _state.value = State.Ready(update, apk, needsPermission = !allowed)
        if (allowed) context.startActivity(installIntent(context, apk))
    }

    /** Back from Android's "install unknown apps" setting: on to the installer if it's allowed now. */
    fun retryInstall(context: Context) {
        val s = _state.value as? State.Ready ?: return
        ready(context.applicationContext, s.update, s.apk)
    }

    fun dismiss() {
        if (_state.value is State.Failed) _state.value = State.Idle
    }

    /** The newest release if it's newer than this build, otherwise null. */
    fun findUpdate(): Update? {
        val body = connect("https://$API_HOST/repos/${BuildConfig.UPDATE_REPO}/releases?per_page=50", "application/vnd.github+json").let { c ->
            try { c.inputStream.bufferedReader().use { it.readText() } } finally { c.disconnect() }
        }
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

    /** [update]'s APK into the cache, checked to be a newer build of this app. */
    fun download(context: Context, update: Update, onProgress: (Long, Long) -> Unit): File {
        val directory = File(context.cacheDir, "updates")
        directory.deleteRecursively()
        directory.mkdirs()
        val target = File(directory, update.apkName.replace('/', '_'))
        val partial = File(directory, "${target.name}.part")
        val connection = connect(update.apkUrl, "application/octet-stream")
        try {
            val total = connection.contentLengthLong.takeIf { it > 0 } ?: update.size
            connection.inputStream.use { input ->
                partial.outputStream().buffered(1 shl 20).use { output ->
                    val buffer = ByteArray(64 * 1024)
                    var done = 0L
                    var shown = 0L
                    while (true) {
                        val read = input.read(buffer)
                        if (read < 0) break
                        output.write(buffer, 0, read)
                        done += read
                        if (done - shown > (1 shl 20)) { shown = done; onProgress(done, total) }
                    }
                    if (total > 0 && done != total) throw IOException("download ended early")
                }
            }
        } finally {
            connection.disconnect()
        }
        if (!partial.renameTo(target)) throw IOException("can't save the download")
        val info = context.packageManager.getPackageArchiveInfo(target.path, 0) ?: throw WrongApkException()
        if (info.packageName != context.packageName || PackageInfoCompat.getLongVersionCode(info) <= BuildConfig.VERSION_CODE) throw WrongApkException()
        return target
    }

    fun canInstall(context: Context): Boolean =
        Build.VERSION.SDK_INT < Build.VERSION_CODES.O || context.packageManager.canRequestPackageInstalls()

    fun installIntent(context: Context, apk: File): Intent {
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.filesprovider", apk)
        return Intent(Intent.ACTION_VIEW)
            .setDataAndType(uri, "application/vnd.android.package-archive")
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
    }

    /** Opens [url], following GitHub's redirects to its file servers by hand. */
    private fun connect(url: String, accept: String): HttpURLConnection {
        var current = URL(url)
        repeat(MAX_REDIRECTS + 1) {
            val connection = (current.openConnection() as HttpURLConnection).apply {
                instanceFollowRedirects = false
                connectTimeout = 6000
                readTimeout = 20000
                setRequestProperty("Accept", accept)
                setRequestProperty("User-Agent", "${BuildConfig.APPLICATION_ID}/${BuildConfig.VERSION_NAME}")
                if (current.host == API_HOST) setRequestProperty("X-GitHub-Api-Version", "2022-11-28")
            }
            when (val code = connection.responseCode) {
                HttpURLConnection.HTTP_OK -> return connection
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
