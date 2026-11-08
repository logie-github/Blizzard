package com.logie.blizz.music

import android.annotation.SuppressLint
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.webkit.WebView
import android.webkit.WebViewClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import org.json.JSONTokener
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * A page as a browser gets it: loaded in a WebView nobody sees, so a site's "checking your browser" page (khinsider's, Cloudflare's)
 * runs its test and goes on to the page itself, whose HTML is then read. Used only where a plain request was turned away.
 */
object BrowserFetch {
    private const val POLL_MS = 700L

    @SuppressLint("SetJavaScriptEnabled")
    suspend fun html(context: Context, url: String, timeoutMs: Long = 40_000): String = withContext(Dispatchers.Main) {
        suspendCancellableCoroutine { cont ->
            val web = WebView(context.applicationContext)
            val handler = Handler(Looper.getMainLooper())
            var finished = false
            fun done(result: Result<String>) {
                if (finished) return
                finished = true
                handler.removeCallbacksAndMessages(null)
                runCatching { web.stopLoading(); web.destroy() }
                result.fold({ cont.resume(it) }, { cont.resumeWithException(it) })
            }
            web.settings.javaScriptEnabled = true
            web.settings.domStorageEnabled = true
            web.webViewClient = object : WebViewClient() {}
            val deadline = SystemClock.uptimeMillis() + timeoutMs
            fun poll() {
                if (finished) return
                web.evaluateJavascript("(function(){return document.title + '\\u0001' + document.documentElement.outerHTML;})()") { raw ->
                    if (finished) return@evaluateJavascript
                    val page = runCatching { JSONTokener(raw).nextValue() as? String }.getOrNull()
                    if (page != null) {
                        val title = page.substringBefore('\u0001')
                        val body = page.substringAfter('\u0001')
                        // The check's page says "Just a moment..." until it has let the browser through.
                        if (!title.contains("Just a moment", true) && body.length > 1500 && !Khinsider.looksLikeBrowserCheck(body)) { done(Result.success(body)); return@evaluateJavascript }
                    }
                    if (SystemClock.uptimeMillis() > deadline) done(Result.failure(Khinsider.KhinsiderException("khinsider's browser check didn't let the app through. Try again in a moment.")))
                    else handler.postDelayed({ poll() }, POLL_MS)
                }
            }
            cont.invokeOnCancellation { handler.post { runCatching { web.stopLoading(); web.destroy() } } }
            web.loadUrl(url)
            handler.postDelayed({ poll() }, 1_500)
        }
    }
}
