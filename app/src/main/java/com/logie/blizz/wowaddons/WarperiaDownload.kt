// Ported from the World of Warcraft app (com.logie.warcraft), apart from its package.

package com.logie.blizz.wowaddons

import java.io.File
import java.io.IOException

/** What the add-on manager needs from the web. */
interface Web {
    /** A page's text. */
    fun get(url: String): String

    /** Sends a form the way a page's script does, from [referer]; the answer's text. */
    fun post(url: String, form: List<Pair<String, String>>, referer: String): String

    /** Saves a file to [to]; [progress] gets the bytes so far and the size (-1 when not known). */
    fun save(url: String, to: File, progress: (Long, Long) -> Unit)
}

/** A web server's refusal. */
class HttpException(val code: Int) : IOException("HTTP $code")

/**
 * An add-on's zip from warperia.com, the way the site's own free download goes: its waiting page,
 * the few seconds it asks for, then the link it gives (the site's Premium skips the wait; the app
 * waits like any visitor).
 */
object WarperiaDownload {
    sealed interface Step {
        data class Waiting(val secondsLeft: Int) : Step
        data class Downloading(val bytes: Long, val size: Long) : Step
    }

    fun fetch(
        web: Web,
        slug: String,
        to: File,
        onStep: (Step) -> Unit,
        sleep: (Long) -> Unit = { Thread.sleep(it) },
        flavor: Warperia.Flavor = Warperia.Flavor.WOTLK,
    ) {
        val page = Warperia.downloadPageUrl(slug, flavor)
        val ticket = Warperia.parseTicket(web.get(page))
        for (left in ticket.seconds downTo 1) {
            onStep(Step.Waiting(left))
            sleep(1_000)
        }
        var again = true
        while (true) {
            val link = Warperia.parseDownloadAnswer(web.post(Warperia.AJAX, Warperia.downloadForm(ticket), page))
            try {
                web.save(link, to) { bytes, size -> onStep(Step.Downloading(bytes, size)) }
                return
            } catch (e: HttpException) {
                // The link is only for the address that asked for it: ask once more if the phone's
                // address changed in between (Wi-Fi to mobile data).
                if (e.code != 403 || !again) throw e
                again = false
            }
        }
    }
}
