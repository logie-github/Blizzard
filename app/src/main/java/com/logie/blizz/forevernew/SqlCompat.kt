package com.logie.blizz.forevernew

import java.io.BufferedReader
import java.io.BufferedWriter
import java.io.Reader
import java.io.Writer

/**
 * Karrz's SQL is MySQL 8 dumps; the phone's database is MariaDB. Two things in them MariaDB can fail on, fixed while the
 * file is streamed to the client (a 600 MB file is never held whole):
 *  - the collation `utf8mb4_0900_ai_ci` (older MariaDB hasn't it) becomes `utf8mb4_unicode_ci`;
 *  - views' and routines' `DEFINER=` of the dumping user (removed: the importer becomes the definer);
 *  - MySQL-8-only versioned comments (the ones numbered 80000 and up, such as a database's ENCRYPTION option), which MariaDB would run as code, are dropped.
 * Line by line; a statement is never rewritten otherwise. If a MariaDB new enough to know the collation is used, the
 * replacement still works (unicode_ci is always there).
 */
object SqlCompat {
    private val ENCRYPTION = Regex("""/\*!80\d{3}[^*]*\*/""")
    // mysqldump writes views and routines with the dumping user as their DEFINER; creating one for a user that isn't the importer needs
    // privileges the app's database user doesn't have (found importing world.sql: ERROR 1227 at its first view)
    private val DEFINER = Regex("""/\*!\d{5}\s+DEFINER=[^*]*\*/""")
    private val DEFINER_PLAIN = Regex("""\sDEFINER\s*=\s*`[^`]*`@`[^`]*`""")
    private val CONDITIONAL_8 = Regex("""/\*!(8\d{4})\s""")

    fun line(line: String): String {
        var out = line
        if (out.contains("utf8mb4_0900_ai_ci")) out = out.replace("utf8mb4_0900_ai_ci", "utf8mb4_unicode_ci")
        if (out.contains("DEFINER")) out = DEFINER_PLAIN.replace(DEFINER.replace(out, ""), "")
        if (out.contains("/*!8")) out = ENCRYPTION.replace(out, "")
        if (out.contains("/*!8") && CONDITIONAL_8.containsMatchIn(out)) {
            // A multi-statement conditional block would need the whole file; the ones in these dumps are single-line.
            out = out.replace(Regex("""/\*!8\d{4}\s.*?\*/"""), "")
        }
        return out
    }

    /** Copies [from] to [to] line by line through [line]; returns the number of lines changed. */
    fun stream(from: Reader, to: Writer, onProgress: (Long) -> Unit = {}): Long {
        var changed = 0L
        var chars = 0L
        val reader = if (from is BufferedReader) from else BufferedReader(from, 1 shl 20)
        val writer = if (to is BufferedWriter) to else BufferedWriter(to, 1 shl 20)
        while (true) {
            val l = reader.readLine() ?: break
            val n = line(l)
            if (n != l) changed++
            writer.write(n); writer.write("\n")
            chars += l.length + 1
            if (chars >= (8L shl 20)) { onProgress(chars); chars = 0 }
        }
        writer.flush()
        return changed
    }
}
