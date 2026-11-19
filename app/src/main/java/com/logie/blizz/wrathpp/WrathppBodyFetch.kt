package com.logie.blizz.wrathpp

import java.io.File
import java.io.IOException
import java.io.InputStream

/**
 * Wrath++'s body options package fetched by the app itself (the user, 19 November 2026: "Be sure body options is fully
 * functional in game. Right now it's wired and you can select options but it doesn't actually change the appearance"):
 * until then the package ([WrathppBody]) was an import of yours only, and a phone without one had the Body tab's three
 * rows, saved every choice and drew none of them (no layer on the women's models, no designs, no body shapes' models, no
 * displays for the realm to give).
 *
 * CI makes the package from each looks release (`.github/workflows/wrathpp-body.yml`, release `wrathpp-body`:
 * `wrathpp-body.zip` and `wrathpp-body.json` with its size, SHA-256, how many models it has and the looks it was made for)
 * and this takes it in through [WrathppBody.importZip], as an import is:
 *  - when nothing is imported;
 *  - when what is in is an earlier release's ([MARK]);
 *  - when what is in is your own and has fewer models than the release's (the first packages had the ten races of 3.3.5
 *    and the Human's shapes only): a package of yours as complete as the release's stays.
 * Never after the package was removed on Settings' Wrath++ page (until one is picked there again), and only when the
 * parts are being refreshed ([update]) or nothing is in. Offline, or with no release yet: what is in stays.
 *
 * Plain Kotlin (the fetching, hashing and importing are passed in), so it is unit-tested without the phone.
 */
object WrathppBodyFetch {
    const val RELEASE = "wrathpp-body"
    /** In the package's store: the SHA-256 of the release's zip that was taken in (absent for a package of yours). */
    const val MARK = "release"

    /** What the release says of its package (`wrathpp-body.json`). */
    data class Published(val size: Long, val sha256: String, val models: Int, val looks: String)

    /** The release's `wrathpp-body.json` (a flat JSON object; read without a JSON library, so this file stays plain Kotlin). */
    fun parse(text: String): Published {
        fun text(key: String) = Regex("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"").find(text)?.groupValues?.get(1)
        fun number(key: String) = Regex("\"" + key + "\"\\s*:\\s*(\\d+)").find(text)?.groupValues?.get(1)?.toLongOrNull()
        val sha = text("sha256")?.lowercase()?.takeIf { it.matches(Regex("[0-9a-f]{64}")) } ?: throw IOException("The body options' release names no package.")
        val size = number("size")?.takeIf { it > 0 } ?: throw IOException("The body options' release names no size.")
        return Published(size, sha, (number("models") ?: 0L).toInt(), text("looks").orEmpty().lowercase())
    }

    /**
     * Whether the release's package is to be taken in: [removed] (taken off by hand), [installed] (the SHA-256 of the
     * package in, or null), [ours] (what is in came from a release), [models] (how many models it has).
     */
    fun wanted(removed: Boolean, installed: String?, ours: Boolean, models: Int, published: Published): Boolean = when {
        removed -> false
        installed == null -> true
        installed.equals(published.sha256, ignoreCase = true) -> false
        ours -> true
        else -> models < published.models
    }

    /** The package in [store] is a release's (and which), or null for none or one of yours. */
    fun ours(store: File): String? = File(store, MARK).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }

    /**
     * The release's package taken in where [wanted]; returns a line for the start report. [base]: the release's download
     * address; [tmp]: where the download is kept until it is in; [update]: the parts are being refreshed (else only a
     * phone with no package asks). [installed], [models], [removed]: what [store] has now. [importZip] takes a zip in
     * and returns how many models it has.
     */
    fun ensure(
        store: File, tmp: File, base: String, update: Boolean, removed: Boolean, installed: String?, models: Int,
        fetchText: (String) -> String, download: (String, File, (Long, Long) -> Unit) -> Unit, sha256: (File) -> String,
        importZip: (InputStream) -> Int, say: (String, Float?) -> Unit = { _, _ -> },
    ): String {
        val mine = ours(store)
        val what = when { installed == null -> "none in"; mine != null -> "the release's ${installed.take(8)}"; else -> "yours (${installed.take(8)}, $models models)" }
        if (removed) return "$what: removed on Settings' Wrath++ page, the release's not asked for"
        if (!update && installed != null) return "$what, kept (not refreshed at this start)"
        val published = try { parse(fetchText("$base/wrathpp-body.json")) } catch (e: Exception) {
            return "$what; the release's not fetched (${e.message ?: e.javaClass.simpleName}; the release $RELEASE may not exist yet)"
        }
        if (!wanted(false, installed, mine != null, models, published)) {
            return if (installed.equals(published.sha256, ignoreCase = true)) "the release's ${published.sha256.take(8)} (${published.models} models), as published"
            else "$what, kept: as many models as the release's ${published.sha256.take(8)} (${published.models})"
        }
        val free = (tmp.parentFile ?: tmp).usableSpace
        if (free in 1 until published.size * 4) return "$what; the release's not fetched: about ${published.size * 4 shr 20} MB is needed, ${free shr 20} MB is free"
        try {
            say("Downloading Wrath++'s body options", 0f)
            download("$base/wrathpp-body.zip", tmp) { done, total ->
                say("Downloading Wrath++'s body options: ${done shr 20} / ${total shr 20} MB", if (total > 0) done.toFloat() / total else null)
            }
            if (!sha256(tmp).equals(published.sha256, ignoreCase = true)) throw IOException("the download didn't match its checksum")
            say("Putting in Wrath++'s body options", null)
            val n = tmp.inputStream().use { importZip(it) }
            File(store, MARK).writeText(published.sha256 + "\n")
            return "the release's ${published.sha256.take(8)} taken in ($n models, made for looks ${published.looks.take(8).ifEmpty { "?" }}), in place of: $what"
        } catch (e: Exception) {
            return "$what; the release's ${published.sha256.take(8)} not taken in (${e.message ?: e.javaClass.simpleName})"
        } finally {
            tmp.delete()
        }
    }
}
