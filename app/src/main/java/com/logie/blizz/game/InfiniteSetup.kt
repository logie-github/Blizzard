package com.logie.blizz.game

import android.content.Context
import android.system.Os
import com.logie.blizz.importer.InfiniteImporter
import com.logie.blizz.wow.WowLogin
import com.winlator.core.EnvVars
import java.io.DataInputStream
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.file.Files
import java.nio.file.StandardCopyOption
import java.util.Locale

internal object InfiniteSetup {
    const val GAME_ID = "wow_infinite"
    private const val STOP_FILE = "blizz-infinite.stop"
    const val LOGIN_HOST = "trinity.actual.battle.net"
    private const val SERVER_PATH = "C:\\ForeverNXT-Server"
    private val nativeOverrides = listOf(
        "iphlpapi", "icu", "msvcp140", "msvcp140_1", "msvcp140_2", "msvcp140_atomic_wait",
        "msvcp140_codecvt_ids", "vcruntime140", "vcruntime140_1", "vcruntime140_threads", "concrt140",
    )

    fun environment(current: String): String = EnvVars(current).apply {
        val overrides = get("WINEDLLOVERRIDES").orEmpty().split(';')
        val inherited = overrides.filter { it.isNotBlank() && it.substringBefore('=') !in nativeOverrides }
        put("WINEDLLOVERRIDES", (inherited + nativeOverrides.map { "$it=n,b" }).joinToString(";"))
    }.toString()

    fun prepare(context: Context, game: File, program: File, containerRoot: File) {
        val server = File(game, InfiniteImporter.SERVER).canonicalFile
        val config = child(server, "config")
        val releases = child(server, "releases")
        val bin = releases.listFiles().orEmpty().filter { it.isDirectory }.mapNotNull { release ->
            release.listFiles().orEmpty().firstOrNull { it.isDirectory && it.name.equals("bin", true) }
        }.filter { folder ->
            val names = folder.list().orEmpty().map { it.lowercase(Locale.ROOT) }
            "bnetserver.exe" in names && "worldserver.exe" in names
        }.singleOrNull() ?: error("Infinite needs one server release with bnetserver.exe and worldserver.exe.")
        val mysql = child(server, "mysql").walkTopDown().maxDepth(3)
            .firstOrNull { it.isFile && it.name.equals("mysqld.exe", true) }
            ?: error("Infinite's mysqld.exe is missing.")
        val mysqlConfig = child(config, "mysql.ini")
        val worldConfig = child(config, "worldserver.conf")
        val loginConfig = child(config, "bnetserver.conf")
        child(child(checkNotNull(bin.parentFile), "sql"), "playerbot_v2")
        configure(worldConfig, mapOf(
            "Playerbot.LLM.Enable" to "0",
            "NXTBattlePets.Enable" to "0",
            "Playerbot.World.Enable" to "0",
            "Playerbot.Bg.Coordinator.Enable" to "0",
            "Playerbot.Bg.QueueFill.Enable" to "0",
            "Playerbot.Raid.Enable" to "0",
            "RankedArena.Enable" to "0",
            "BindIP" to "\"127.0.0.1\"",
        ))
        configure(loginConfig, mapOf(
            "BindIP" to "\"127.0.0.1\"",
            "LoginREST.ExternalAddress" to "\"$LOGIN_HOST\"",
            "LoginREST.LocalAddress" to "\"$LOGIN_HOST\"",
        ))
        val data = child(server, "data")
        for (name in listOf("dbc", "gt", "maps", "vmaps", "mmaps")) {
            check(child(data, name).isDirectory) { "Infinite's data/$name folder is missing." }
        }
        seedEmptyTilelists(child(data, "maps"))

        val drive = File(containerRoot, ".wine/drive_c")
        val mount = File(drive, "ForeverNXT-Server")
        if (!Files.isSymbolicLink(mount.toPath()) || mount.canonicalFile != server) {
            check(!mount.exists() || Files.isSymbolicLink(mount.toPath())) { "Infinite's C: server path is already occupied." }
            Files.deleteIfExists(mount.toPath())
            Os.symlink(server.path, mount.path)
        }
        val temp = File(drive, "tmp")
        check(temp.isDirectory || temp.mkdirs()) { "Could not create Infinite's MySQL temporary folder." }
        val windows = File(drive, "windows")
        Files.deleteIfExists(File(windows, STOP_FILE).toPath())
        for ((asset, target) in listOf(
            "iphlpapi.dll" to File(bin, "iphlpapi.dll"),
            "iphlpapi.dll" to File(windows, "system32/iphlpapi.dll"),
            "icu.dll" to File(windows, "system32/icu.dll"),
        )) {
            val bytes = context.assets.open(asset).use { it.readBytes() }
            if (!target.isFile || !target.readBytes().contentEquals(bytes)) write(target, bytes)
        }

        fun windowsPath(file: File): String {
            val relative = file.relativeTo(server).invariantSeparatorsPath
            check(relative.none { it in "\r\n\"" }) { "Infinite's server path contains unsupported characters." }
            return "$SERVER_PATH\\${relative.replace('/', '\\')}"
        }
        val settings = mapOf(
            "mysql" to windowsPath(mysql),
            "mysqlConfig" to windowsPath(mysqlConfig),
            "mysqlAdmin" to windowsPath(child(checkNotNull(mysql.parentFile), "mysqladmin.exe")),
            "mysqlAdminConfig" to windowsPath(child(config, "mysql-admin.ini")),
            "login" to windowsPath(child(bin, "bnetserver.exe")),
            "loginConfig" to windowsPath(loginConfig),
            "world" to windowsPath(child(bin, "worldserver.exe")),
            "worldConfig" to windowsPath(worldConfig),
            "bin" to windowsPath(bin),
            "worldPort" to (Regex("""(?m)^\s*WorldServerPort\s*=\s*(\d+)""")
                .find(worldConfig.readText())?.groupValues?.get(1) ?: "8085"),
            "ca" to windowsPath(child(child(config, "tls"), "ca.cer")),
        )
        val ini = settings.entries.joinToString("\r\n", "\uFEFF[Infinite]\r\n", "\r\n") { "${it.key}=${it.value}" }
        write(File(windows, "blizz-infinite.ini"), ini.toByteArray(Charsets.UTF_16LE))

        val wtf = program.parentFile?.let { client ->
            client.listFiles().orEmpty().firstOrNull { it.isDirectory && it.name.equals("WTF", true) }
                ?: File(client, "WTF")
        } ?: error("Infinite's client folder is missing.")
        check(wtf.isDirectory || wtf.mkdir()) { "Could not create Infinite's client settings folder." }
        val clientConfig = wtf.listFiles().orEmpty().firstOrNull { it.isFile && it.name.equals("Config.wtf", true) }
            ?: File(wtf, "Config.wtf")
        val current = if (clientConfig.isFile) clientConfig.readText() else ""
        val updated = WowClientSetup.updateConfig(current, mapOf("portal" to LOGIN_HOST))
        if (current != updated) write(clientConfig, updated.toByteArray())
    }

    fun bundledLogin(game: File): WowLogin.Login? {
        val file = File(game, "${InfiniteImporter.SERVER}/config/FIRST_LOGIN.txt")
        if (!file.isFile) return null
        val lines = runCatching { file.readLines() }.getOrNull() ?: return null
        val fields = lines.associate { line ->
            line.substringBefore(':').trim().removePrefix("\uFEFF").lowercase(Locale.ROOT) to
                line.substringAfter(':', "").trim()
        }
        val email = fields["email"]?.takeIf { it.isNotEmpty() } ?: return null
        val password = fields["password"]?.takeIf { it.isNotEmpty() } ?: return null
        return WowLogin.Login(email, password)
    }

    fun requestStop(): Boolean = runCatching {
        val windows = GameLog.keeperLog?.parentFile ?: return false
        File(windows, STOP_FILE).writeText("")
        true
    }.getOrDefault(false)

    private fun child(folder: File, name: String): File =
        folder.listFiles().orEmpty().firstOrNull { it.name.equals(name, true) }
            ?: error("Infinite's ${folder.name}/$name is missing.")

    private fun configure(file: File, settings: Map<String, String>) {
        val original = file.readText()
        val pending = settings.toMutableMap()
        val activeSetting = Regex("""^\s*([\w.]+)\s*=.*$""")
        val newline = if ("\r\n" in original) "\r\n" else "\n"
        val lines = original.lineSequence().map { line ->
            val key = activeSetting.matchEntire(line)?.groupValues?.get(1)
            val value = settings[key]
            if (value == null) line else {
                pending.remove(key)
                "$key = $value"
            }
        }.toList()
        val updated = (lines + pending.map { (key, value) -> "$key = $value" }).joinToString(newline)
        if (updated != original) write(file, updated.toByteArray())
    }

    private fun seedEmptyTilelists(maps: File) {
        val files = maps.listFiles() ?: error("Infinite's terrain files are missing.")
        val tilelists = files.filter { it.name.endsWith(".tilelist", ignoreCase = true) }
        val terrain = files.filter { it.name.endsWith(".map", ignoreCase = true) }
            .map { it.name.substringBefore('_').substringBefore('.').toIntOrNull() }.toSet()
        val existing = tilelists.mapTo(HashSet()) { it.name.lowercase(Locale.ROOT) }
        val empty = ByteArray(12 + 4096) { '0'.code.toByte() }
        // Copy the package's map version and build. Empty indexes avoid thousands of Wine file probes for maps with no terrain.
        val header = tilelists.firstNotNullOfOrNull { file ->
            if (file.length() != empty.size.toLong()) return@firstNotNullOfOrNull null
            val bytes = ByteArray(12)
            DataInputStream(file.inputStream()).use { it.readFully(bytes) }
            val version = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).getInt(4)
            bytes.takeIf { String(it, 0, 4, Charsets.US_ASCII) == "MAPS" && version == 10 }
        } ?: return
        header.copyInto(empty)
        for (id in 0 until 5000) {
            val name = "${id.toString().padStart(4, '0')}.tilelist"
            if (id !in terrain && name !in existing) write(File(maps, name), empty)
        }
    }

    private fun write(file: File, bytes: ByteArray) {
        val temp = File.createTempFile(".infinite-", ".tmp", file.parentFile)
        try {
            temp.writeBytes(bytes)
            Files.move(temp.toPath(), file.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING)
        } finally {
            temp.delete()
        }
    }
}
