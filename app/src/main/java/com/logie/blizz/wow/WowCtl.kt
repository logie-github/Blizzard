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
 * app's own. NOT verified on a phone: only the text it produces, and what a shell does with it
 * (WowRuntimeHarnessTest), is tested.
 *
 * What in the package names the old folder (scripts/compile-azerothcore.sh, package-azerothcore.sh),
 * and why nothing needs the old folder to exist:
 * - The ELF interpreter (`patchelf --set-interpreter <old>/server/lib/ld-musl-aarch64.so.1`): the
 *   programs are never exec'd directly, the loader is, with the program as its argument.
 * - The rpath (`$ORIGIN/../lib` on programs, `$ORIGIN` on libraries, `$ORIGIN/..` on legacy.so):
 *   relative, resolved from the program's path as given, and `--library-path <server>/lib` goes first.
 * - `CMAKE_INSTALL_PREFIX` (<old>/server) and `CONF_DIR` (<old>/etc), compiled into the core: only the
 *   defaults for a config path and for the modules' config folder. `ctl.sh` always passes
 *   `-c <config>` and exports `WOW_MODULES_CONF_DIR` (patches/azerothcore/0010), `ALE.ScriptPath`,
 *   `LogsDir`, `DataDir`, `TempDir`, `SourceDirectory`, `PidFile` are written into the configs at every
 *   start. AzerothCore's `AC_<KEY>` environment overrides are deliberately NOT used: they would beat
 *   the `DataDir` that `ctl.sh modules` points at `data-modules`.
 * - MariaDB: `--no-defaults`, and `--datadir --basedir --lc-messages-dir --character-sets-dir
 *   --plugin-dir --tmpdir --socket --pid-file --log-error` are all given. Its compiled-in paths
 *   (/usr/share/mariadb, /usr/lib/mariadb/plugin) are Alpine's, not the app's. The client programs
 *   (`mariadb`, `mariadb-admin`) are run with `--no-defaults` and TCP to 127.0.0.1; their plugin
 *   folder is Alpine's, which doesn't exist on the phone in the WoW app either (the acore user uses
 *   mysql_native_password, which is built in).
 * - `/proc/self/exe` is the loader, not the program, when run this way. Nothing in ctl.sh's
 *   commands depends on it (every folder is given), but this can't be checked without the programs.
 */
object WowCtl {
    /** The text of `ctl.blizz.sh`: ctl.sh with the programs started through the loader. */
    fun transform(ctl: String): String {
        var text = ctl
        // dbimport and the world server run the mariadb client by this setting; a script they can exec.
        // The static client wrapper when the app has one (BLIZZ_MARIA), else the script.
        text = text.replace("MySQLExecutable \"\\\"\$SERVER/bin/mariadb\\\"\"", "MySQLExecutable \"\\\"\${BLIZZ_MARIA:-\$SERVER/blizz/mariadb}\\\"\"")
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

    /**
     * The static mariadb client wrapper (libblizzmaria.so in the app's native library folder, set once by the app):
     * dbimport and the world server run it by their MySQLExecutable setting. The script wrapper's shell is Android's,
     * which can't load the musl compatibility library that dbimport hands down in LD_PRELOAD; this program is static.
     */
    @Volatile var nativeWrapper: File? = null

    /** What to run for `ctl.sh <args>`: the shell, the script, and the environment it needs. */
    data class Command(val argv: List<String>, val env: Map<String, String>, val directory: File)

    fun command(layout: WowLayout, loader: File, timeZone: String, vararg args: String): Command = Command(
        argv = listOf("/system/bin/sh", layout.blizzCtl.path) + args,
        env = mapOf(
            // ctl.sh's own variable: every path it builds starts here.
            "FILES" to layout.root.path,
            "TZ" to timeZone,
            "BLIZZ_LDSO" to loader.path,
            "BLIZZ_SERVER" to layout.server.path,
            // The static client wrapper's own log (what it was asked to do, the client's messages, how it ended).
            "BLIZZ_LOG" to File(layout.logs, "blizzmaria.log").path,
        ) + (nativeWrapper?.takeIf { it.canExecute() }?.let { mapOf("BLIZZ_MARIA" to it.path) } ?: emptyMap()),
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
     * Writes `ctl.blizz.sh` and `blizz/mariadb` and marks the programs executable
     * ([restoreExecutableBits]: an import doesn't keep the bits). Returns the loader. Throws if
     * the server has none.
     */
    fun prepare(layout: WowLayout): File {
        val loader = layout.loader() ?: throw java.io.IOException("The imported server has no musl loader (server/lib/ld-musl-ARCH.so.1)")
        restoreExecutableBits(layout)
        write(layout.blizzCtl, transform(layout.ctl.readText()), executable = true)
        layout.blizzBin.mkdirs()
        write(File(layout.blizzBin, "mariadb"), mariadbWrapper(layout, loader), executable = true)
        for (dir in listOf(layout.run, File(layout.run, "tmp"), layout.logs, layout.realmLogs(Realm.REMIX), layout.data)) dir.mkdirs()
        return loader
    }

    /**
     * The export has no mode bits and the importer writes plain files, so nothing is executable
     * after an import. The WoW app marks an entry executable when the package says its owner can
     * run it (ServerPackage.unpack: the programs in bin, the loader, the libraries, MariaDB's programs, ctl.sh);
     * this does the same for every file under `server/bin` and `server/lib` (the loader is run by
     * the kernel, so it needs the bit; the rest are mapped by the loader, which doesn't need it), and for `ctl.sh`. Idempotent;
     * symlinks and everything else under `server` are left alone. Returns how many files it changed.
     */
    fun restoreExecutableBits(layout: WowLayout): Int {
        var changed = 0
        fun mark(file: File) {
            if (file.canExecute()) return
            if (file.setExecutable(true, false)) changed++
        }
        for (dir in listOf("bin", "lib")) {
            File(layout.server, dir).walkTopDown()
                .filter { it.isFile && !java.nio.file.Files.isSymbolicLink(it.toPath()) }
                .forEach(::mark)
        }
        if (layout.ctl.isFile) mark(layout.ctl)
        return changed
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
