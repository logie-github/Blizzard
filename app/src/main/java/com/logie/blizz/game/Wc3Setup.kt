package com.logie.blizz.game

import com.winlator.core.WineRegistryEditor
import java.io.File

/**
 * What Warcraft III is started with, beside the person's own arguments: fullscreen at the screen's
 * size, and OpenGL when chosen. Each in 1.30's words and in the ones patch 1.31 replaced them with
 * (the game passes over the ones it doesn't know). Plain Kotlin, unit-tested.
 */
object Wc3Arguments {
    /** Fullscreen: 1.30's `-nativefullscr`, 1.31's `-windowmode fullscreen`. */
    const val FULLSCREEN = "-windowmode fullscreen -nativefullscr"

    /** OpenGL in place of Direct3D: 1.30's `-opengl`, 1.31's `-graphicsapi OpenGL`. */
    const val OPENGL = "-opengl -graphicsapi OpenGL"

    private val WINDOW = Regex("(?i)(^|\\s)-(window|windowmode|fullscreen|nativefullscr)(\\s|$)")
    private val RENDERER = Regex("(?i)(^|\\s)-(opengl|d3d|graphicsapi)(\\s|$)")

    /** [own] with the window mode and renderer added, unless [own] already sets them. */
    fun of(own: String, openGl: Boolean): String {
        val parts = mutableListOf(own.trim())
        if (!WINDOW.containsMatchIn(own)) parts += FULLSCREEN
        if (openGl && !RENDERER.containsMatchIn(own)) parts += OPENGL
        return parts.filter { it.isNotEmpty() }.joinToString(" ")
    }
}

/**
 * Warcraft III's registry, which it reads its screen and language from, and where the games' own
 * installers write its folder: a pure list of writes ([writes]) and a function that makes them in the
 * games' Windows ([apply]), as WindowsRuntime.registerInstall does for StarCraft. Written before every
 * start, so a moved, reset or resized game is found again.
 */
object Wc3Setup {
    enum class Hive { USER, SYSTEM }

    /** One registry value: a string, or a number when [value] is an Int. */
    data class Write(val hive: Hive, val key: String, val name: String, val value: Any)

    const val VIDEO = "Software\\Blizzard Entertainment\\Warcraft III\\Video"
    const val LAUNCHER = "Software\\Blizzard Entertainment\\Classic Launcher\\w3"
    private val INSTALL_KEYS = listOf("Software\\Blizzard Entertainment\\Warcraft III", "Software\\Wow6432Node\\Blizzard Entertainment\\Warcraft III")

    /** Windowed 0, windowed fullscreen 1, fullscreen 2 (one guide's mapping, not confirmed for 1.30). */
    const val WINDOW_MODE_FULLSCREEN = 2

    /**
     * The values to write: the game's resolution at the phone's size and fullscreen, the repack's
     * launcher language (kept if [locale] already has one; enUS otherwise), and, when [installDos] is
     * given (`D:\warcraft3_roc\`), the folder where the game's installer would have recorded it.
     */
    fun writes(width: Int, height: Int, locale: String?, installDos: String?): List<Write> = buildList {
        add(Write(Hive.USER, VIDEO, "reswidth", width))
        add(Write(Hive.USER, VIDEO, "resheight", height))
        add(Write(Hive.USER, VIDEO, "windowmode", WINDOW_MODE_FULLSCREEN))
        if (locale.isNullOrEmpty()) add(Write(Hive.USER, LAUNCHER, "Locale", "enUS"))
        if (installDos != null) {
            val dos = if (installDos.endsWith("\\")) installDos else "$installDos\\"
            for (key in INSTALL_KEYS) {
                add(Write(Hive.SYSTEM, key, "InstallPath", dos))
                add(Write(Hive.SYSTEM, key, "InstallPathX", dos))
            }
        }
    }

    /**
     * Makes [writes] in the games' Windows at [containerRoot] (the Winlator container's rootDir):
     * `user.reg` and `system.reg` under `.wine`. A hive that isn't there yet (Wine makes them at the
     * first start) is skipped.
     */
    fun apply(containerRoot: File, width: Int, height: Int, installDos: String?, open: (File) -> Registry = ::wine) {
        val userReg = File(containerRoot, ".wine/user.reg")
        val systemReg = File(containerRoot, ".wine/system.reg")
        val locale = if (userReg.isFile) open(userReg).use { it.getString(LAUNCHER, "Locale") } else ""
        val all = writes(width, height, locale, installDos)
        for ((hive, file) in listOf(Hive.USER to userReg, Hive.SYSTEM to systemReg)) {
            if (!file.isFile) continue
            open(file).use { registry ->
                for (w in all.filter { it.hive == hive }) {
                    when (val v = w.value) {
                        is Int -> registry.setDword(w.key, w.name, v)
                        else -> registry.setString(w.key, w.name, v.toString())
                    }
                }
            }
        }
    }

    /** What [apply] needs of a registry file (Winlator's WineRegistryEditor in the app; a stand-in in tests). */
    interface Registry : java.io.Closeable {
        fun getString(key: String, name: String): String
        fun setString(key: String, name: String, value: String)
        fun setDword(key: String, name: String, value: Int)
    }

    private fun wine(file: File): Registry = object : Registry {
        private val editor = WineRegistryEditor(file)
        override fun getString(key: String, name: String): String = editor.getStringValue(key, name, "")
        override fun setString(key: String, name: String, value: String) = editor.setStringValue(key, name, value)
        override fun setDword(key: String, name: String, value: Int) = editor.setDwordValue(key, name, value)
        override fun close() = editor.close()
    }
}

/**
 * Warcraft III's CD keys: the ones the person pasted (one per line, a label before a key optional),
 * kept in `files/cdkeys.txt` apart from the game's folder (a reset or repair of the game never
 * touches them), and those in a key file that came with the game (`_SERIAL_KEYS.txt`). The app
 * takes the keys the person has; it makes, fetches and carries none. Keys are never logged. Plain
 * Kotlin, unit-tested.
 */
object Wc3CdKeys {
    /** A key with a label for it: the text before it on its line (like "Reign of Chaos:"), if any. */
    data class Found(val label: String, val key: String) {
        /** What a menu shows: the label and the key. */
        val display: String get() = if (label.isEmpty()) key else "$label: $key"
    }

    /** Groups of letters and digits joined by dashes (XXXX-XXXX-...), or 26 in a row (Warcraft III's). */
    private val KEY = Regex("(?<![A-Za-z0-9-])([A-Za-z0-9]{4,8}(?:-[A-Za-z0-9]{4,8}){2,7}|[A-Za-z0-9]{26})(?![A-Za-z0-9-])")

    /** File names that hold keys. */
    private val FILE = Regex("(?i).*(serial|cd[ _-]?key|keys?)[^/]*\\.txt")

    fun isKeyFile(name: String): Boolean = FILE.matches(name)

    /** The keys in [text] with the words before them as their label. */
    fun find(text: String): List<Found> {
        val found = mutableListOf<Found>()
        for (line in text.lines()) {
            for (match in KEY.findAll(line)) {
                val key = match.groupValues[1]
                // A 26-character run must mix letters and digits, like a key does (not a word).
                if ('-' !in key && (key.none { it.isDigit() } || key.none { it.isLetter() })) continue
                val label = line.substring(0, match.range.first).trim().trimEnd(':', '-', '=', '.').trim()
                found += Found(label.take(60), key.uppercase())
            }
        }
        return found.distinctBy { it.key }
    }

    /**
     * Keys the person pasted or typed, line by line: what [find] sees on a line, else a line that is
     * one run of 16 to 32 letters and digits (a key written without dashes).
     */
    fun findPasted(text: String): List<Found> =
        text.lines().flatMap { line ->
            find(line).ifEmpty {
                val bare = line.trim()
                if (bare.length in 16..32 && bare.all { it in 'A'..'Z' || it in 'a'..'z' || it in '0'..'9' }) {
                    listOf(Found("", bare.uppercase()))
                } else {
                    emptyList()
                }
            }
        }.distinctBy { it.key }

    /** The store: `cdkeys.txt` in the app's files folder (`context.filesDir`). */
    fun file(filesDir: File) = File(filesDir, "cdkeys.txt")

    /** What the person pasted, as written ("" if nothing). */
    fun text(filesDir: File): String = runCatching { file(filesDir).readText() }.getOrDefault("")

    /** Keeps [text] as the person pasted it; blank text removes the file. */
    fun save(filesDir: File, text: String) {
        val f = file(filesDir)
        if (text.isBlank()) { f.delete(); return }
        f.parentFile?.mkdirs()
        val tmp = File(f.parentFile, f.name + ".tmp")
        tmp.writeText(text)
        if (!tmp.renameTo(f)) { f.writeText(text); tmp.delete() }
    }

    /** The pasted keys. */
    fun stored(filesDir: File): List<Found> = findPasted(text(filesDir))

    /**
     * The keys in key files in the folder of [gameDir] itself (`_SERIAL_KEYS.txt` and the like):
     * read, never moved or changed.
     */
    fun inGame(gameDir: File): List<Found> =
        gameDir.listFiles().orEmpty()
            .filter { it.isFile && isKeyFile(it.name) && it.length() < 256 * 1024 }
            .sortedBy { it.name }
            .flatMap { f -> runCatching { find(f.readText()) }.getOrDefault(emptyList()) }
            .distinctBy { it.key }

    /**
     * What the game menu offers to type: the pasted keys, then those the game came with
     * ([gameDir] may be null). Each key once.
     */
    fun offered(filesDir: File, gameDir: File?): List<Found> =
        (stored(filesDir) + (gameDir?.let { inGame(it) } ?: emptyList())).distinctBy { it.key }
}
