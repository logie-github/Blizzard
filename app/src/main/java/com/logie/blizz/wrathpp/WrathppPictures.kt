package com.logie.blizz.wrathpp

import java.io.ByteArrayOutputStream
import java.io.File
import java.util.Base64

/**
 * Pictures of Wrath++'s creator as the game draws it on the phone, sent with the app's reports (the user, 12 November
 * 2026: "Can you just test it on your rig rather than giving me shitty code"; the rig has no game: what the game makes of
 * the creator's art, fonts and places is seen only where the game is). When no pictures of this build, art and looks
 * went yet, the creator's patch carries `WrathppShots.lua` ([flag]); the creator then takes the game's own screenshot
 * of each of its two screens a moment after it is first up, and of the first list of choices opened (three at most).
 * When the game is left, [send] makes each smaller and sends it as an issue, its JPEG in base64 (in parts where it is
 * larger than an issue takes); `realm/warcraft/wrathpp/client-mod/rig/tools/fetch_pictures.py` puts them together.
 * Only ever the character creation screen, only pictures taken since the app asked. Plain files but for [shrink]
 * (Android's Bitmap): unit-tested. NOT run on a phone.
 */
object WrathppPictures {
    const val FLAG = "WrathppShots.lua"
    private const val SENT = "wrathpp-pictures-sent.txt"
    private const val ASKED = "wrathpp-pictures-asked.txt"
    /** An issue's text may be 65,536 characters: a part's base64 stays under this. */
    const val PART_CHARS = 57_000
    const val MAX_PARTS = 3
    const val TITLE = "Wrath++ creator picture"

    /** What the pictures are of: another build, art or looks is another set of pictures. */
    fun state(build: Int, art: String?, looks: String?): String = "build $build, art ${art?.take(8) ?: "none"}, looks ${looks?.take(8) ?: "none"}"

    /**
     * The file that asks the creator for pictures, when none of [state] went yet (and notes when it asked, so that only
     * pictures taken since are sent); null when they went.
     */
    fun flag(logs: File, state: String, now: Long = System.currentTimeMillis()): String? {
        if (runCatching { File(logs, SENT).readText().trim() }.getOrNull() == state) return null
        logs.mkdirs()
        val asked = runCatching { File(logs, ASKED).readLines() }.getOrNull()
        // (asked before and not answered: the first asking's hour stays, a picture taken since is still wanted)
        if (asked == null || asked.size < 2 || asked[0] != state) File(logs, ASKED).writeText("$state\n$now\n")
        return "-- Wrath++: the app has no pictures of the creator for $state yet (WrathppPictures).\nWrathppShots = \"${state.replace("\\", "").replace("\"", "")}\"\n"
    }

    /** The state asked for and the game's screenshots taken since: the newest [max] JPEGs of [screenshots], oldest first. Null when nothing was asked. */
    fun taken(logs: File, screenshots: File, max: Int = 3): Pair<String, List<File>>? {
        val asked = runCatching { File(logs, ASKED).readLines() }.getOrNull()?.takeIf { it.size >= 2 } ?: return null
        val since = asked[1].trim().toLongOrNull() ?: return null
        val files = screenshots.listFiles { f -> f.isFile && f.name.lowercase().let { it.endsWith(".jpg") || it.endsWith(".jpeg") } && f.lastModified() >= since - 2000 }
            ?.sortedBy { it.lastModified() }?.takeLast(max) ?: emptyList()
        return asked[0] to files
    }

    /** What the creator said each picture is of, in the order it took them ("shot 2: customize" in the runtime's log). */
    fun names(log: List<String>): List<String> =
        log.mapNotNull { Regex("""creator: shot \d+: (.+)$""").find(it)?.groupValues?.get(1)?.trim() }

    fun markSent(logs: File, state: String) {
        logs.mkdirs()
        File(logs, SENT).writeText("$state\n")
        File(logs, ASKED).delete()
    }

    private val WORDS = listOf("none", "one", "two", "three", "four", "five", "six")
    private fun word(n: Int) = WORDS.getOrElse(n) { "many" }

    /**
     * One picture as the issues it takes: title and text of each part, the JPEG's base64 between two marks, 76 to a line.
     * The titles say which picture and which part in words: the reports' queue tells two reports apart by their titles
     * without their digits, and two parts named by digits alone would be one report to it.
     */
    fun parts(what: String, state: String, number: Int, of: Int, jpeg: ByteArray): List<Pair<String, String>> {
        val text = Base64.getEncoder().encodeToString(jpeg)
        val chunks = text.chunked(PART_CHARS)
        return chunks.mapIndexed { i, chunk ->
            "$TITLE ${word(number)} of ${word(of)}, part ${word(i + 1)} of ${word(chunks.size)}: $what ($state)" to buildString {
                append("**$TITLE**\n\n$what, as the game drew it. $state.\n\n")
                append("picture $number of $of, part ${i + 1} of ${chunks.size}, ${jpeg.size} bytes of JPEG\n\n")
                append("```\n-----BEGIN PICTURE-----\n")
                chunk.chunked(76).forEach { append(it).append('\n') }
                append("-----END PICTURE-----\n```\n\n_Sent by the app by itself._\n")
            }
        }
    }

    /** Whether a JPEG of [bytes] goes in [MAX_PARTS] issues. */
    fun fits(bytes: Int): Boolean = (bytes + 2) / 3 * 4 <= PART_CHARS * MAX_PARTS

    /** [file] at half its size, as good a JPEG as [fits] (Android's Bitmap: not run in the unit tests). Null if it isn't a picture. */
    fun shrink(file: File): ByteArray? = runCatching {
        val options = android.graphics.BitmapFactory.Options().apply { inSampleSize = 2 }
        val bitmap = android.graphics.BitmapFactory.decodeFile(file.path, options) ?: return null
        try {
            for (quality in intArrayOf(72, 58, 45, 32, 20)) {
                val out = ByteArrayOutputStream()
                bitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, quality, out)
                if (fits(out.size())) return out.toByteArray()
            }
            null
        } finally {
            bitmap.recycle()
        }
    }.getOrNull()

    /**
     * After the game was left (and as the app starts): the pictures the creator took since they were asked for go,
     * once. With the creator saying it took some and no file there, that is said instead (the game's Screenshot made
     * nothing on this phone). Nothing asked, or the creator not opened since: nothing.
     */
    fun send(context: android.content.Context) {
        val layout = com.logie.blizz.wow.WowLayout.of(context)
        val client = layout.wrathppClient
        val logs = File(client, "Logs")
        val (state, files) = taken(logs, File(client, "Screenshots")) ?: return
        val said = names(runCatching { File(logs, "WarcraftXL.log").readLines() }.getOrDefault(emptyList()))
        if (files.isEmpty()) {
            if (said.isEmpty()) return
            com.logie.blizz.reports.BugReports.submit(context, com.logie.blizz.reports.BugReports.Report(
                "$TITLE: none ($state)",
                com.logie.blizz.reports.BugReports.body(TITLE, "The creator took ${said.size} (${said.joinToString(", ")}) and the game wrote no file into Screenshots.", listOf("Of" to state), log = null),
            ))
            markSent(logs, state)
            return
        }
        var sent = 0
        files.forEachIndexed { i, file ->
            val jpeg = shrink(file) ?: return@forEachIndexed
            val what = said.getOrNull(said.size - files.size + i) ?: "screen ${i + 1}"
            for ((title, body) in parts(what, state, i + 1, files.size, jpeg)) {
                com.logie.blizz.reports.BugReports.submit(context, com.logie.blizz.reports.BugReports.Report(title, body))
            }
            sent++
        }
        if (sent > 0) markSent(logs, state)
    }
}
