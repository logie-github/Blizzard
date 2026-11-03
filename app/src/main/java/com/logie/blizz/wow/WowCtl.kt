package com.logie.blizz.wow

import org.json.JSONObject
import java.io.File
import java.util.Locale
import java.util.TimeZone

/**
 * How the WoW app's server programs are run from Blizzard's folder.
 *
 * The programs (musl, built by scripts/package-azerothcore.sh) have `/data/data/com.logie.warcraft/
 * files/server/lib/ld-musl-aarch64.so.1` baked in as their ELF interpreter. In Blizzard that file
 * is not there (another app's folder, which Android keeps apart), so executing them directly fails
 * with "not found". They are run through musl's loader instead, which takes the program as an
 * argument: `ld-musl-aarch64.so.1 --library-path <server/lib> <server/bin/worldserver> args`.
 * (The rpath `$ORIGIN/../lib` also resolves from the program's path, the library path is a second way.)
 *
 * `ctl.sh` starts every program as `"$SERVER/bin/<name>"`, so [transform] makes a copy of it
 * (`ctl.blizz.sh`) with the loader in front of each; the one place a program is started by another
 * program (`MySQLExecutable`, which dbimport and the world server run to apply SQL) points at a
 * small wrapper script ([mariadbWrapper]), since the kernel can't run the program itself.
 * `ctl.sh` as imported is left alone. Everything else in it (configs, order, databases) is the WoW
 * app's own. NOT verified on a phone: only the text it produces is tested.
 */
object WowCtl {
    /** The text of `ctl.blizz.sh`: ctl.sh with the programs started through the loader. */
    fun transform(ctl: String): String {
        var text = ctl
        // dbimport and the world server run the mariadb client by this setting; a script they can exec.
        text = text.replace("MySQLExecutable \"\\\"\$SERVER/bin/mariadb\\\"\"", "MySQLExecutable \"\\\"\$SERVER/blizz/mariadb\\\"\"")
        text = Regex("\"\\\$SERVER/bin/([A-Za-z0-9_.-]+)\"").replace(text) { m ->
            "\"\$BLIZZ_LDSO\" --library-path \"\$SERVER/lib\" \"\$SERVER/bin/${m.groupValues[1]}\""
        }
        return text
    }

    /** `server/blizz/mariadb`: the mariadb client through the loader, with the compatibility shim preloaded. */
    fun mariadbWrapper(layout: WowLayout, loader: File): String = buildString {
        append("#!/system/bin/sh\n")
        append("export LD_PRELOAD=\"${layout.server.path}/lib/libandroidcompat.so\"\n")
        append("exec \"${loader.path}\" --library-path \"${layout.server.path}/lib\" \"${layout.server.path}/bin/mariadb\" \"\$@\"\n")
    }

    /** What to run for `ctl.sh <args>`: the shell, the script, and the environment it needs. */
    data class Command(val argv: List<String>, val env: Map<String, String>, val directory: File)

    fun command(layout: WowLayout, loader: File, timeZone: String, vararg args: String): Command = Command(
        argv = listOf("/system/bin/sh", layout.blizzCtl.path) + args,
        env = mapOf(
            // ctl.sh's own variable: every path it builds starts here.
            "FILES" to layout.root.path,
            "TZ" to timeZone,
            "BLIZZ_LDSO" to loader.path,
        ),
        directory = layout.run,
    )

    /** The phone's time zone for programs that can't read Android's: POSIX TZ with today's offset (`<+0200>-02:00`). */
    fun posixTimeZone(zone: TimeZone = TimeZone.getDefault(), now: Long = System.currentTimeMillis()): String {
        val minutes = zone.getOffset(now) / 60_000
        val abs = kotlin.math.abs(minutes)
        val name = String.format(Locale.ROOT, "%s%02d%02d", if (minutes >= 0) "+" else "-", abs / 60, abs % 60)
        return String.format(Locale.ROOT, "<%s>%s%02d:%02d", name, if (minutes >= 0) "-" else "+", abs / 60, abs % 60)
    }

    /**
     * Writes `ctl.blizz.sh` and `blizz/mariadb` and marks the programs executable (an import may
     * not have kept the bits). Returns the loader. Throws if the server has none.
     */
    fun prepare(layout: WowLayout): File {
        val loader = layout.loader() ?: throw java.io.IOException("The imported server has no musl loader (server/lib/ld-musl-ARCH.so.1)")
        loader.setExecutable(true, false)
        File(layout.server, "bin").listFiles()?.forEach { it.setExecutable(true, false) }
        File(layout.server, "lib/libjemalloc.so.2").takeIf { it.isFile }?.setExecutable(true, false)
        write(layout.blizzCtl, transform(layout.ctl.readText()), executable = true)
        layout.blizzBin.mkdirs()
        write(File(layout.blizzBin, "mariadb"), mariadbWrapper(layout, loader), executable = true)
        for (dir in listOf(layout.run, File(layout.run, "tmp"), layout.logs, layout.realmLogs(Realm.REMIX), layout.data)) dir.mkdirs()
        return loader
    }

    private fun write(file: File, text: String, executable: Boolean) {
        if (file.isFile && runCatching { file.readText() }.getOrNull() == text) {
            if (executable) file.setExecutable(true, false)
            return
        }
        val temp = File(file.path + ".tmp")
        temp.writeText(text)
        if (executable) temp.setExecutable(true, false)
        file.delete()
        if (!temp.renameTo(file)) throw java.io.IOException("Couldn't write ${file.path}")
    }
}

/** What the export recorded, read from `.export/` (the WoW app's `export.json` and `prefs/<name>.json`). */
object WowExportInfo {
    /** The WoW app's absolute files path at export time, if export.json has it. */
    fun sourceFilesDir(layout: WowLayout): String? = runCatching {
        JSONObject(layout.manifest.readText()).optString("sourceFilesDir").takeIf { it.isNotBlank() }
    }.getOrNull()

    /** A string preference from `prefs/<name>.json` (`{"key":{"type":"string","value":...}}`). */
    fun stringPref(layout: WowLayout, name: String, key: String): String? = runCatching {
        val entry = JSONObject(File(layout.prefsDir, "$name.json").readText()).optJSONObject(key) ?: return null
        entry.optString("value").takeIf { entry.optString("type") == "string" && it.isNotEmpty() }
    }.getOrNull()

    /**
     * The realm the user last chose in the WoW app: its `realms` preference `realm` ("main" or
     * "remix", written by `Realms.set`), ChromieCraft if it never chose.
     */
    fun chosenRealm(layout: WowLayout): Realm = Realm.byKey(stringPref(layout, "realms", "realm")) ?: Realm.CHROMIE
}
