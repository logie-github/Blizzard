package com.logie.blizz.forevernew

import com.logie.blizz.wow.WowCtl
import java.io.File

/**
 * How Forever's programs are started: through the package's own musl loader (`ld-musl-aarch64.so.1 --library-path lib prog args`),
 * the way the app runs the other realms' programs, with the compatibility shim preloaded and OpenSSL's legacy provider findable
 * (RC4 for the game's packet headers). No program path is compiled in (the package is built with EMBED_BUILD_PATHS=0). Every
 * config path is passed or written at start. NOT run on a phone.
 */
object ForeverServer {
    /** Start-up order and the line each program prints when it is ready. */
    data class Program(val key: String, val binary: String, val args: (ForeverLayout) -> List<String>, val ready: Regex, val log: String, val pid: String, val port: Int)

    private val BNET_READY = Regex("""Bnet server .*|Listening|Starting up|bnetserver.*ready""", RegexOption.IGNORE_CASE)
    // TrinityCore's own line when the world is up (also what the bots log after); kept as upstream prints it.
    private val WORLD_READY = Regex("""\(worldserver-daemon\) ready\.\.\.|World initialized in""")

    fun dbArgs(layout: ForeverLayout): List<String> = listOf(
        "--no-defaults", "--datadir=${layout.db.path}", "--basedir=${layout.server.path}",
        "--lc-messages-dir=${layout.server.path}/share/mariadb", "--character-sets-dir=${layout.server.path}/share/mariadb/charsets",
        "--plugin-dir=${layout.lib.path}", "--tmpdir=${File(layout.run, "tmp").path}",
        "--socket=${File(layout.run, "mariadb.sock").path}", "--pid-file=${File(layout.run, "mariadbd.pid").path}",
        "--bind-address=127.0.0.1", "--port=${ForeverPorts.DATABASE}", "--log-error=${File(layout.logs, "mariadbd.err").path}",
        "--skip-name-resolve", "--max-connections=60", "--innodb-buffer-pool-size=256M", "--innodb-flush-log-at-trx-commit=2",
    )

    val DATABASE = Program("db", "mariadbd", ::dbArgs, Regex("""ready for connections"""), "mariadbd.err", "mariadbd.pid", ForeverPorts.DATABASE)
    val AUTH = Program("auth", "bnetserver", { listOf("-c", File(it.etc, "bnetserver.conf").path) }, BNET_READY, "bnetserver.log", "bnetserver.pid", ForeverPorts.BNET)
    val WORLD = Program("world", "worldserver", { listOf("-c", File(it.etc, "worldserver.conf").path) }, WORLD_READY, "worldserver.log", "worldserver.pid", ForeverPorts.WORLD)

    /** Database first, then the login server, then the world: stopped in the opposite order. */
    val startOrder = listOf(DATABASE, AUTH, WORLD)
    val stopOrder = startOrder.reversed()

    fun command(layout: ForeverLayout, program: String, args: List<String>, directory: File = layout.run): WowCtl.Command {
        val loader = layout.loader() ?: throw java.io.IOException("Forever's server has no musl loader")
        return WowCtl.Command(
            argv = listOf(loader.path, "--library-path", layout.lib.path, File(layout.bin, program).path) + args,
            env = mapOf(
                "LD_PRELOAD" to (listOf("libandroidcompat.so", "libforeverresolve.so") + (if (program == "worldserver") listOf("libjemalloc.so.2") else emptyList()))
                    .map { File(layout.lib, it).path }.joinToString(":"),
                "OPENSSL_MODULES" to File(layout.lib, "ossl-modules").path,
                "HOME" to layout.run.path, "TMPDIR" to File(layout.run, "tmp").path,
            ),
            directory = directory,
        )
    }

    fun command(layout: ForeverLayout, program: Program): WowCtl.Command = command(layout, program.binary, program.args(layout))

    /** The extraction tools run in [ForeverLayout.data]. */
    fun toolCommand(layout: ForeverLayout, step: ForeverMaps.Step): WowCtl.Command {
        val bin = File(step.argv.first()).name
        return command(layout, bin, step.argv.drop(1), layout.data)
    }

    /** The mariadb client wrapper the servers run for SQL updates (`MySQLExecutable`): the app's static one when it has it, else a script. */
    fun clientWrapperScript(layout: ForeverLayout): String {
        val loader = layout.loader()!!
        return "#!/system/bin/sh\nexport LD_PRELOAD=\"${File(layout.lib, "libandroidcompat.so").path}\"\n" +
            "exec \"${loader.path}\" --library-path \"${layout.lib.path}\" \"${File(layout.bin, "mariadb").path}\" \"\$@\"\n"
    }

    fun clientWrapperPath(layout: ForeverLayout): String =
        WowCtl.nativeWrapper?.takeIf { it.canExecute() }?.path ?: File(layout.server, "blizz/mariadb").path

    /** A client invocation against Forever's database (loopback, the account's user). */
    fun clientArgs(user: String, password: String, vararg more: String): List<String> =
        listOf("--no-defaults", "-h", "127.0.0.1", "-P", ForeverPorts.DATABASE.toString(), "-u", user, "--password=$password") + more

    /** Fatal lines of the programs and what to tell the user. */
    val FATAL: List<Pair<Regex, String>> = listOf(
        Regex("""Could not resolve LoginREST""") to "The login server couldn't resolve its portal name. The portal name must map to this phone for the login server.",
        Regex("""Map file .* does not exist|Correct \*\.map files not found|vmap file .* missing|Incorrect DataDir""") to "The map data is missing or from another client. Repair re-extracts it.",
        Regex("""Could not connect to .* database|Cannot connect to database|DatabasePool .* NOT opened""") to "A server couldn't reach its database.",
        Regex("""Applying of file .* failed|Could not (update|populate)""") to "A database update failed. See the world server's log.",
        Regex("""Realm running as realm ID""") to "",
    ).filter { it.second.isNotEmpty() }

    fun explain(logTail: String): String? = FATAL.firstOrNull { it.first.containsMatchIn(logTail) }?.second
}
