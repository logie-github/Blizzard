package com.logie.blizz.importer

import java.io.File
import java.net.InetAddress
import java.net.ServerSocket
import java.net.Socket
import kotlin.concurrent.thread

/**
 * Answers name lookups for blizzard-legacy-dl on 127.0.0.1 (Android has no /etc/resolv.conf for
 * its resolver; patches/blizzard-legacy-dl/0001): the name and a newline in, one address a line
 * back, looked up the way every Android app does.
 */
class LoopbackResolver(private val lookup: (String) -> List<String> = { name -> InetAddress.getAllByName(name).map { it.hostAddress ?: "" }.filter { it.isNotEmpty() } }) : AutoCloseable {
    private val server = ServerSocket(0, 16, InetAddress.getByName("127.0.0.1"))
    val port: Int get() = server.localPort

    init {
        thread(isDaemon = true, name = "loopback-resolver") {
            while (!server.isClosed) {
                val socket = runCatching { server.accept() }.getOrNull() ?: break
                thread(isDaemon = true) { answer(socket) }
            }
        }
    }

    private fun answer(socket: Socket) = socket.use { s ->
        s.soTimeout = 15_000
        val name = s.getInputStream().bufferedReader().readLine()?.trim().orEmpty()
        // Names only: nothing that could make the lookup do anything else.
        val addresses = if (name.matches(Regex("[A-Za-z0-9.-]{1,253}"))) runCatching { lookup(name) }.getOrDefault(emptyList()) else emptyList()
        s.getOutputStream().write(addresses.joinToString("") { "$it\n" }.toByteArray())
        s.getOutputStream().flush()
    }

    override fun close() = server.close()
}

/**
 * blizzard-legacy-dl (libbldl.so): Blizzard's legacy downloads (Diablo II, Lord of Destruction,
 * StarCraft) fetched piece by piece, each piece checked against its SHA-1, and the game folder
 * built from the payload's own install script, without running Blizzard's installer or Windows.
 * Pieces are cached ([GamePaths.legacyCache]): a stopped download resumes.
 */
class LegacyDownloader(private val program: File, private val cache: File) {
    data class Keys(val classic: String?, val expansion: String?, val owner: String?)

    /** `install <product> [version] [--no-base] --game <dir>`, its progress to [onProgress]. A [version] older than Blizzard's is made by patching what the payload carries. */
    fun install(product: String, game: File, noBase: Boolean, keys: Keys?, cancel: CancelToken, onProgress: (Progress) -> Unit, version: String? = null) {
        if (!program.canExecute()) throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "blizzard-legacy-dl is missing from this build of the app.")
        cache.mkdirs()
        game.mkdirs()
        val command = buildList {
            add(program.path); add("install"); add(product)
            if (version != null) add(version)
            if (noBase) add("--no-base")
            add("--game"); add(game.path)
            add("--jobs"); add("4")
            add("--no-tracker")
            if (keys?.classic != null) { add("--cdkey"); add(keys.classic) }
            if (keys?.expansion != null) { add("--cdkey-expansion"); add(keys.expansion) }
            if (keys?.owner != null && (keys.classic != null || keys.expansion != null)) { add("--owner"); add(keys.owner) }
        }
        LoopbackResolver().use { resolver ->
            val environment = mapOf(
                "BLDL_RESOLVER" to resolver.port.toString(),
                "BLIZZARD_LEGACY_DL_CACHE" to cache.path,
                "HOME" to cache.path,
            )
            val result = Tools.run(command, cache, cancel, environment) { line -> parse(product, line)?.let(onProgress) }
            if (result.code != 0) {
                val tail = result.tail.joinToString("\n")
                throw ImportException(
                    if (tail.contains("NoSpaceLeft", ignoreCase = true)) Problem.INSUFFICIENT_STORAGE else Problem.DOWNLOAD_FAILED,
                    "Blizzard's download of $product stopped. What's downloaded is kept: retry to go on from there.",
                    // Keys are never in the log: the command line isn't shown, and the tool doesn't print them.
                    tail,
                )
            }
        }
    }

    companion object {
        /**
         * What is stored where the games keep their CD key when the person gave none: Warcraft III 1.0 to 1.27 and StarCraft stop at start
         * ("unable to find a CD Key", "unable to open a required file") without one, and single player never checks it. A key of the
         * right shape and alphabet that no one was ever issued: it signs in nowhere.
         */
        const val PLACEHOLDER_KEY = "ZZZZZZZZZZZZZZZZZZZZZZZZZZ"
        const val PLACEHOLDER_OWNER = "Player"

        private val PIECES = Regex("""(\d+)/(\d+) pieces""")

        /** A progress line of the tool's, as [Progress]. Plain Kotlin, unit-tested. */
        fun parse(product: String, line: String): Progress? {
            PIECES.find(line)?.let { m ->
                return Progress(Stage.DOWNLOADING, "Downloading $product from Blizzard", m.groupValues[1].toLong(), m.groupValues[2].toLong())
            }
            if (line.startsWith("installing")) return Progress(Stage.ASSEMBLING, "Building $product's game folder")
            return null
        }
    }
}
