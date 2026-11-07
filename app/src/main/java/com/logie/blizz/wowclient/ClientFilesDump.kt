package com.logie.blizz.wowclient

import android.content.Context
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
    fun send(context: Context, pieces: List<Piece>) {
        for (piece in pieces) {
            BugReports.report(
                context, "Client file ${piece.name}", "The 3.3.5 client's character creation (${piece.text.length} characters)",
                details = listOf("Part" to piece.name),
                files = piece.text,
            )
        }
    }

    /** Sent the first time only. */
    fun sendOnce(context: Context, client: File) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (prefs.getBoolean("sent", false)) return
        // Marked first: a start that dies halfway must not send it again and again.
        prefs.edit().putBoolean("sent", true).apply()
        runCatching { send(context, collect(File(client, "Data"))) }
    }

    fun sendNow(context: Context, client: File): Int {
        val pieces = collect(File(client, "Data"))
        send(context, pieces)
        return pieces.size
    }
}
