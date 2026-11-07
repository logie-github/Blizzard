package com.logie.blizz.wowclient

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.widget.Toast
import com.logie.blizz.reports.BugReports
import java.io.File

/**
 * The 3.3.5a client's character-creation screen as it is in the person's own client, read from its archives and sent as reports
 * (the interface's Lua, XML and table of contents only: text, no game art or data). A modern character creation is a screen written
 * for these exact files (their frames' names, what each one calls), so it is written against what is there. Sent once on the first
 * start of Wrath+, and by the button in Wrath+'s settings.
 */
object ClientFilesDump {
    private const val PREFS = "client-files-dump"

    /** The glue interface files that make the creation screen: those the table of contents names with one of these in the name. */
    private val WANTED = Regex("(?i)charactercreate|customiz|racecreate|characterselect|glueparent|gluestrings|gluebutton")

    class Piece(val name: String, val text: String)

    /** What [data] (the client's `Data` folder) has of the creation screen: the load order, who provides what, and the files. */
    fun collect(data: File): List<Piece> {
        val game = Mpq.Game(data)
        try {
            val toc = game.read("Interface\\GlueXML\\GlueXML.toc")?.let { String(it, Charsets.UTF_8) }
            val names = LinkedHashSet<String>()
            names += "Interface\\GlueXML\\GlueXML.toc"
            toc?.lineSequence()?.map { it.trim() }?.filter { it.isNotEmpty() && !it.startsWith("#") }?.forEach { line ->
                val name = "Interface\\GlueXML\\" + line.replace('/', '\\').removePrefix("\\")
                if (WANTED.containsMatchIn(line)) names += name
            }
            // What the creation screen's XML loads (its Lua, other XML): the screen's code is in those.
            val queue = ArrayDeque(names.filter { it.endsWith(".xml", true) && Regex("(?i)charactercreate").containsMatchIn(it) })
            val scripted = Regex("(?i)<(?:Script|Include)\\s+[^>]*?file\\s*=\\s*\"([^\"]+)\"")
            while (queue.isNotEmpty()) {
                val xml = queue.removeFirst()
                val text = game.read(xml)?.let { String(it, Charsets.UTF_8) } ?: continue
                for (m in scripted.findAll(text)) {
                    val file = m.groupValues[1].replace('/', '\\')
                    val name = if (file.contains('\\')) file else xml.substringBeforeLast('\\') + "\\" + file
                    if (names.add(name) && name.endsWith(".xml", true)) queue.addLast(name)
                }
            }
            val overview = buildString {
                appendLine("locale: ${game.locale.ifEmpty { "none found" }}")
                appendLine("archives in the order the game reads them (the last wins):")
                game.archives.forEach { appendLine("  ${it.path.name}${if (it.path.isDirectory) " (folder)" else " (${it.path.length()} bytes)"}") }
                appendLine("who provides each file:")
                names.forEach { appendLine("  ${it.substringAfterLast('\\')}: ${game.owner(it)?.name ?: "none"}") }
                appendLine("GlueXML.toc entries: ${toc?.lineSequence()?.count { it.isNotBlank() && !it.startsWith("#") } ?: 0}")
            }
            val out = arrayListOf(Piece("overview", overview))
            for (name in names) {
                val bytes = game.read(name) ?: continue
                val text = String(bytes, Charsets.UTF_8)
                out += Piece(name.substringAfterLast('\\'), text)
            }
            return out
        } finally {
            game.close()
        }
    }

    /** Sends [pieces] as reports, one each (the interface's text goes in the report's files section, cut at what an issue holds). */
    fun send(context: Context, pieces: List<Piece>): Int {
        var queued = 0
        for (piece in pieces) {
            if (BugReports.report(
                context, "Client file ${piece.name}", "The 3.3.5 client's character creation (${piece.text.length} characters)",
                details = listOf("Part" to piece.name),
                files = piece.text,
            )) queued++
        }
        announce(context, pieces.size, queued)
        return queued
    }

    /**
     * A pop-up (a toast, which shows over the game too) once the files have reached GitHub, or what is holding them: they are sent
     * a few seconds apart, so it waits for the queue to empty, up to a minute and a half.
     */
    private fun announce(context: Context, total: Int, queued: Int) {
        val app = context.applicationContext
        fun say(text: String) = Handler(Looper.getMainLooper()).post { Toast.makeText(app, text, Toast.LENGTH_LONG).show() }
        if (queued == 0) { say("Your client's character-creation files were already sent (within the last day)."); return }
        if (!BugReports.configured(app)) { say("This build can't send the character-creation files (no report token)."); return }
        Thread {
            val deadline = System.currentTimeMillis() + 90_000
            while (BugReports.waiting(app) > 0 && System.currentTimeMillis() < deadline) Thread.sleep(1000)
            say(
                if (BugReports.waiting(app) == 0) "Got it: your client's character-creation files ($total parts) reached GitHub."
                else "The character-creation files are waiting to be sent (is the phone online?). They go by themselves.",
            )
        }.apply { isDaemon = true }.start()
    }

    /** Sent the first time only. */
    fun sendOnce(context: Context, client: File) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        // (2: the files the screen's XML loads were added; a part already sent today isn't sent again)
        if (prefs.getBoolean("sent2", false)) return
        // Marked first: a start that dies halfway must not send it again and again.
        prefs.edit().putBoolean("sent2", true).apply()
        runCatching { send(context, collect(File(client, "Data"))) }
    }

    fun sendNow(context: Context, client: File): Int {
        val pieces = collect(File(client, "Data"))
        send(context, pieces)
        return pieces.size
    }
}
