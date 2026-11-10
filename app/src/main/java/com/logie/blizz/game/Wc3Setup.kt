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

    /**
     * 1.0 to 1.27's window: `-window`. Those versions know none of 1.30's switches and so ran exclusive fullscreen under Wine, where the
     * first dialog to take the focus (the game's own "video hardware changed" at a first start) left a black screen with the menu music
     * playing (the phone, 9 November 2026). A window the launcher stretches to the screen is what the game gets instead.
     */
    const val WINDOW_1_2X = "-window"

    private val VERSION = Regex("""(?:^|\D)1\.(\d{1,2})\.""")

    /** Whether [clientVersion] (a program version such as 1.27.0.52240, or a title with one in it) is from before 1.28. */
    fun isBefore128(clientVersion: String?): Boolean {
        val minor = clientVersion?.let { VERSION.find(it)?.groupValues?.get(1)?.toIntOrNull() } ?: return false
        return minor < 28
    }

    /** [own] with the window mode and renderer added, unless [own] already sets them; the window mode of [clientVersion] when given. */
    fun of(own: String, openGl: Boolean, clientVersion: String? = null): String {
        val parts = mutableListOf(own.trim())
        if (!WINDOW.containsMatchIn(own)) parts += if (isBefore128(clientVersion)) WINDOW_1_2X else FULLSCREEN
        if (openGl && !RENDERER.containsMatchIn(own)) parts += if (isBefore128(clientVersion)) "-opengl" else OPENGL
        return parts.filter { it.isNotEmpty() }.joinToString(" ")
    }

    /** [stored] (a library entry's arguments, made for 1.30) as [clientVersion] wants them: 1.2x's window switch in place of 1.30's fullscreen ones. */
    fun forVersion(stored: String, clientVersion: String?): String {
        if (!isBefore128(clientVersion)) return stored
        val own = stored.replace(FULLSCREEN, "").replace(OPENGL, "-opengl").trim()
        return of(own, openGl = false, clientVersion = clientVersion)
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

    /** The app's own key in the games' registry: what it has set up once. */
    const val APP = "Software\\Logie\\Blizz"
    /** [APP]'s value for "the game's video options were put at their best": [BEST_VIDEO_VERSION] once done. */
    const val BEST_VIDEO = "wc3video"
    const val BEST_VIDEO_VERSION = "1"

    /**
     * The game's own Video options at their best, by the names and numbers 1.27 writes them with (read from the registry after the
     * game ran on the desktop rig, 10 November 2026): model detail, animation quality, texture quality, particles, lights and
     * spell detail High (2), unit shadows and occlusion on, 32-bit colour and textures. Left to itself the game picked Low
     * models, Medium everything else and 16-bit colour there; with these written it showed High throughout and kept them.
     */
    val BEST: List<Pair<String, Int>> = listOf(
        "modeldetail" to 2, "animquality" to 2, "texquality" to 2, "particles" to 2, "lights" to 2, "spellfilter" to 2,
        "unitshadows" to 1, "occlusion" to 1, "colordepth" to 32, "texcolordepth" to 32,
    )

    /**
     * The values to write: the game's resolution at the phone's size and fullscreen, the repack's launcher language (kept if
     * [locale] already has one; enUS otherwise), and, when [installDos] is given (`D:\warcraft3_roc\`), the folder where the
     * game's installer would have recorded it. (A 1.2x window's title bar is taken off by borderless.exe, not here: Wine 10.10
     * draws it itself in its desktop and has no setting against it.) With [best], the game's video options at their best
     * ([BEST]) and the mark that this was done: once, so what the person changes in the game's own Options afterwards stays.
     */
    fun writes(width: Int, height: Int, locale: String?, installDos: String?, best: Boolean = false): List<Write> = buildList {
        add(Write(Hive.USER, VIDEO, "reswidth", width))
        add(Write(Hive.USER, VIDEO, "resheight", height))
        add(Write(Hive.USER, VIDEO, "windowmode", WINDOW_MODE_FULLSCREEN))
        if (best) {
            for ((name, value) in BEST) add(Write(Hive.USER, VIDEO, name, value))
            add(Write(Hive.USER, APP, BEST_VIDEO, BEST_VIDEO_VERSION))
        }
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
        val (locale, bestDone) = if (userReg.isFile) open(userReg).use { it.getString(LAUNCHER, "Locale") to (it.getString(APP, BEST_VIDEO) == BEST_VIDEO_VERSION) } else "" to false
        applyWrites(containerRoot, writes(width, height, locale, installDos, best = !bestDone), open)
    }

    /**
     * Makes [all] in the games' Windows at [containerRoot] (the Winlator container's rootDir): `user.reg` and `system.reg` under
     * `.wine`. A hive that isn't there yet (Wine makes them at the first start) is skipped.
     */
    fun applyWrites(containerRoot: File, all: List<Write>, open: (File) -> Registry = ::wine) {
        val userReg = File(containerRoot, ".wine/user.reg")
        val systemReg = File(containerRoot, ".wine/system.reg")
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

    internal fun wineRegistry(file: File): Registry = wine(file)

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

    /** The keys in a pasted text, each for the game its own product says. */
    data class Wc3Keys(val reignOfChaos: String?, val frozenThrone: String?, val unrecognised: Int) {
        val any: Boolean get() = reignOfChaos != null || frozenThrone != null
    }

    /**
     * Warcraft III's keys in whatever [text] the person pasted: 26 letters and digits written with or without spaces and dashes, in any
     * grouping (`XXXXXX XXXX-XXXXXX-XXXX-XXXXXX`), one a line or several, a label before one allowed. Each is put with the game its
     * decoding says (14 Reign of Chaos, 18 The Frozen Throne). Returned upper-case, as typed into the game.
     */
    fun wc3(text: String): Wc3Keys {
        val candidates = LinkedHashSet<String>()
        val lines = text.lines().map { line -> line.filter { it.isLetterOrDigit() } }.filter { it.isNotEmpty() }
        for (line in lines) {
            if (line.length == 26) candidates += line
            else if (line.length > 26) {
                // A label before the key ("ROC", "Reign of Chaos"), or two keys on a line: the windows of 26 that are keys.
                var i = 0
                while (i + 26 <= line.length) {
                    val w = line.substring(i, i + 26)
                    if (Wc3KeyCodec.product(w.uppercase()) in listOf(Wc3KeyCodec.ROC, Wc3KeyCodec.TFT) && w.all { it in Wc3KeyCodec.ALPHABET || it.uppercaseChar() in Wc3KeyCodec.ALPHABET }) { candidates += w; i += 26 } else i++
                }
            }
        }
        // A key broken over several lines: all the text, run together, in keys of 26.
        if (candidates.isEmpty()) {
            val all = lines.joinToString("")
            if (all.length % 26 == 0 && all.length in 26..52) all.chunked(26).forEach { candidates += it }
        }
        var roc: String? = null
        var tft: String? = null
        var other = 0
        for (c in candidates) {
            val key = c.uppercase()
            when (Wc3KeyCodec.product(key)) {
                Wc3KeyCodec.ROC -> if (roc == null) roc = key
                Wc3KeyCodec.TFT -> if (tft == null) tft = key
                else -> other++
            }
        }
        return Wc3Keys(roc, tft, other)
    }

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

/**
 * Diablo II before 1.14 on Wine 10 (Winlator 11's): the game's Fog.dll, on a Windows it takes for NT, checks every critical section
 * it locks for the debug block Windows NT puts behind it, and Wine 10.10 stores the "no debug block" marker (0xffffffff) instead
 * (`RtlInitializeCriticalSectionEx`, unless asked to force one). The first lock after Fog's init fails the check, Fog reports
 * "Unrecoverable internal error", and its reporter locks again: a stack overflow in Fog.dll within six seconds of the start, on
 * the phone (9 November 2026) and in Winlator's own Wine run on a desktop, where the chain was read from a relay trace. Told it
 * runs on Windows 98 (a platform 1.13 shipped for), Fog skips the check, and the game runs to its menu and into a game (verified
 * on that desktop). So Game.exe of a 1.13 install gets Wine's per-program Windows version 98; 1.14 (Windows 7 and later only,
 * and without the check) is left alone. Plain Kotlin, unit-tested.
 */
object Diablo2Setup {
    const val APP_DEFAULTS = "Software\\Wine\\AppDefaults\\Game.exe"
    const val WIN98 = "win98"

    /** Whether [clientVersion] (a title with the version in it, or the program's 1.0.13.60) is a 1.0 to 1.13 client. */
    fun isBefore114(clientVersion: String?): Boolean {
        val v = clientVersion ?: return false
        if (Regex("""(^|\D)1\.0\.(\d{1,2})\.""").containsMatchIn(v)) return true
        val m = Regex("""(^|\D)1\.(\d{1,2})(\D|$)""").find(v) ?: return false
        val minor = m.groupValues[2].toIntOrNull() ?: return false
        return minor in 0..13
    }

    const val GAME_KEY = "Software\\Blizzard Entertainment\\Diablo II"
    /** The game's `Resolution` value: 0 is 640x480, 1 is 800x600 (Lord of Destruction's largest, the game screen's size here). */
    const val RESOLUTION_800 = 1

    /**
     * The writes for a Diablo II of [clientVersion]: the Windows 98 version for Game.exe before 1.14 (nothing after), and 800x600
     * in game for every version (Lord of Destruction's menus are 800x600 already), so the picture is the whole 800x600 screen
     * instead of 640x480 inside it (seen on the desktop rig, 9 November 2026: Act I at 800x600).
     */
    fun writes(clientVersion: String?): List<Wc3Setup.Write> = buildList {
        if (isBefore114(clientVersion)) add(Wc3Setup.Write(Wc3Setup.Hive.USER, APP_DEFAULTS, "Version", WIN98))
        add(Wc3Setup.Write(Wc3Setup.Hive.USER, GAME_KEY, "Resolution", RESOLUTION_800))
    }

    fun apply(containerRoot: File, clientVersion: String?, open: (File) -> Wc3Setup.Registry = Wc3Setup::wineRegistry) =
        Wc3Setup.applyWrites(containerRoot, writes(clientVersion), open)
}

/**
 * Diablo II's start-up switches: a window (`-w`), which Winlator stretches to the screen. Fullscreen asks the X server for an
 * 800x600 display mode, which it has not (Error 22, "initializing DirectDraw", seen in Winlator's Wine on a desktop); in a window
 * 1.13 draws through GDI (D2Gdi.dll) and ran to its menu and into a game there. Plain Kotlin, unit-tested.
 */
object Diablo2Arguments {
    private val WINDOW = Regex("(?i)(^|\\s)-w(\\s|$)")

    /** [own] for [gameId], with `-w` added for Diablo II unless it is there. */
    fun of(gameId: String, own: String): String =
        if (gameId != "diablo2" || WINDOW.containsMatchIn(own)) own else listOf(own.trim(), "-w").filter { it.isNotEmpty() }.joinToString(" ")
}

/** The command line a game starts with: the library entry's arguments, the app's own switches, then the person's extra ones (Launch options). */
object GameArguments {
    fun of(gameId: String, entryArguments: String, extra: String, clientVersion: String? = null): String {
        val base = when {
            gameId.startsWith("warcraft3") -> Wc3Arguments.forVersion(entryArguments, clientVersion)
            else -> Diablo2Arguments.of(gameId, entryArguments)
        }
        return listOf(base, extra.trim()).filter { it.isNotEmpty() }.joinToString(" ")
    }
}
