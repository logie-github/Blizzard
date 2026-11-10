package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File
import java.nio.file.Files
import java.util.concurrent.TimeUnit

/**
 * A pure-JVM harness for the realm runtime, on the WoW app's REAL files: `ctl.sh` (copied from
 * warcraft/server/ctl.sh) and the modules' real `.conf.dist` files (test/resources/wow/fixtures);
 * the core's three `.conf.dist` are written for the test with the keys `ctl.sh` sets (the core isn't
 * in the repository: CI compiles it).
 *
 * It lays out a server like the WoW app's `files/` (ctl.sh's own `configure` makes the configs), copies it
 * the way the importer does (no mode bits, no `run/`), then runs Blizzard's [WowPathRewrite], [WowCtl]
 * and the generated `ctl.blizz.sh` in a real shell with programs that only record how they were
 * started. The same commands are run with the original `ctl.sh` and its programs run directly, and
 * the two recordings are compared.
 *
 * What it can't show: musl's loader, the real programs and MariaDB (see WowRealm's notes).
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WowRuntimeHarnessTest {
    @get:Rule val tmp = TemporaryFolder()

    private val shell = "sh"
    private val programs = listOf(
        "worldserver", "authserver", "dbimport", "mariadbd", "mariadb", "mariadb-admin", "mariadb-dump",
        "map_extractor", "vmap4_extractor", "vmap4_assembler", "mmaps_generator",
    )
    private val coreDists = listOf("worldserver.conf.dist", "dbimport.conf.dist", "authserver.conf.dist")
    private val moduleDists = listOf(
        "mod_allied_races", "mod_base_model", "mod_brill_home", "mod_level_scaling", "mod_murloc_naga", "mod_quest_drops",
        "mod_ralia", "mod_skyborne", "mod_worgen_goblin", "mod_wrath_remix", "mod_ale", "playerbots", "progression_system", "chromie-xp",
    ).map { "$it.conf.dist" }

    private fun resource(name: String): String =
        checkNotNull(javaClass.classLoader!!.getResourceAsStream("wow/fixtures/$name")) { "missing fixture $name" }.use { it.readBytes().toString(Charsets.UTF_8) }

    /** The ctl.sh to test: the fixture (a copy of the WoW app's), or with [live] the repository's current one. */
    private fun ctlText(live: Boolean): String =
        if (live) File("/home/user/YeaBwoi/warcraft/server/ctl.sh").readText() else resource("ctl.sh")

    private fun recorder(name: String) = "#!/bin/sh\n${resource("record.sh")}record $name \"\$@\"\n"

    private val loaderScript: String get() = """#!/bin/sh
${resource("record.sh")}
if [ "${'$'}1" != --library-path ] || [ ! -f "${'$'}3" ]; then
	echo "bad loader call: ${'$'}*" >> "${'$'}CALLS_LOG.err"
	exit 97
fi
echo "LIBPATH ${'$'}2" >> "${'$'}CALLS_LOG.lib"
prog=${'$'}(basename "${'$'}3")
shift 3
record "${'$'}prog" "${'$'}@"
"""

    private fun write(file: File, text: String, executable: Boolean = false) {
        file.parentFile!!.mkdirs()
        file.writeText(text)
        if (executable) file.setExecutable(true, false)
    }

    private class Run(val code: Int, val output: String)

    private fun sh(
        script: File, args: List<String>, dir: File, env: Map<String, String>, interpreter: String = shell,
    ): Run {
        val builder = ProcessBuilder(listOf(interpreter, script.path) + args).directory(dir).redirectErrorStream(true)
        builder.redirectInput(File("/dev/null"))
        builder.environment().putAll(env)
        val process = builder.start()
        val output = process.inputStream.bufferedReader().readText()
        check(process.waitFor(60, TimeUnit.SECONDS)) { "timeout: ${script.name} $args" }
        return Run(process.exitValue(), output)
    }

    /** The WoW app's files folder after its own `ctl.sh configure`: the "source". */
    private fun buildSource(root: File, ctl: String): File {
        val server = File(root, "server")
        write(File(server, "ctl.sh"), ctl)
        for (p in programs) write(File(server, "bin/$p"), recorder(p), executable = true)
        write(File(server, "bin/legacy-tool"), "ELF\u0000/data/data/com.logie.warcraft/files/server/lib/ld-musl-aarch64.so.1\u0000")
        write(File(server, "lib/ld-musl-aarch64.so.1"), loaderScript, executable = true)
        for (lib in listOf("libandroidcompat.so", "libjemalloc.so.2", "libstdc++.so.6", "ossl-modules/legacy.so")) write(File(server, "lib/$lib"), "ELF\u0000lib", executable = true)
        for (name in coreDists) write(File(server, "etc/$name"), resource("etc/$name"))
        write(File(server, "etc/mmaps-config.yaml"), "threads: 1\n")
        for (name in moduleDists) write(File(server, "etc/modules/$name"), resource("modules/$name"))
        write(File(server, "mariadb-seed/mysql/user.MAD"), "seed")
        write(File(server, "lua_scripts/hello.lua"), "-- path: /data/data/com.logie.warcraft/files/server/lua_scripts\n")
        write(File(server, "VERSION"), "core abc\n")
        File(root, "mysql/mysql").mkdirs()
        for (db in listOf("acore_auth", "acore_characters", "acore_world")) File(root, "mysql/$db").mkdirs()
        write(File(root, "mysql/ibdata1"), "ibdata")
        write(File(root, "mysql/ib_logfile0"), "iblog")
        for (d in listOf("dbc", "maps", "vmaps", "mmaps")) write(File(root, "data/$d/f"), "x")
        File(root, "run/tmp").mkdirs()
        val configure = sh(File(server, "ctl.sh"), listOf("configure"), root, mapOf("FILES" to root.path, "CALLS_LOG" to File(root, "run/calls.log").path))
        assertEquals(configure.output, 0, configure.code)
        // a realm with the Remix databases, as the WoW app leaves it
        File(root, "mysql/acore_characters_remix").mkdirs()
        File(root, "run").deleteRecursively()
        return root
    }

    /**
     * What the importer produces from [source]: the files only (no `run/`, no `.pid`), no mode bits,
     * with the old folder written the way the WoW app has it ([oldPrefix]) in every text file.
     */
    private fun importFrom(source: File, oldPrefix: String, linkSpelling: String? = null): WowLayout {
        val game = File(tmp.root, "blizz/files/games/wow")
        val root = File(game, "files")
        source.walkTopDown().filter { it.isFile }.forEach { f ->
            val target = File(root, f.relativeTo(source).path)
            target.parentFile!!.mkdirs()
            val bytes = f.readBytes()
            val isText = bytes.take(8192).none { it == 0.toByte() }
            if (isText) target.writeText(f.readText().replace(source.path, oldPrefix)) else target.writeBytes(bytes)
            target.setExecutable(false, false)
        }
        source.walkTopDown().filter { it.isDirectory }.forEach { File(root, it.relativeTo(source).path).mkdirs() }
        if (linkSpelling != null) {
            // data-modules: links into the game's data, with the other spelling of the old folder
            File(root, "data-modules/dbc").mkdirs()
            Files.createSymbolicLink(File(root, "data-modules/dbc/Map.dbc").toPath(), File("$linkSpelling/data/dbc/f").toPath())
            Files.createSymbolicLink(File(root, "data-modules/maps").toPath(), File("$oldPrefix/data/maps").toPath())
        }
        File(game, ".export").mkdirs()
        File(game, ".export/export.json").writeText("{\"format\":1,\"sourceFilesDir\":\"$oldPrefix\"}")
        return WowLayout(root, File(game, ".export"))
    }

    private val standardOld = WowPathRewrite.DEFAULT_OLD[0]

    /** A source, imported, rewritten and prepared, the way [RealmController] does it before `configure`. */
    private fun prepared(live: Boolean = false, oldPrefix: String = standardOld, linkSpelling: String? = WowPathRewrite.DEFAULT_OLD[1]): WowLayout {
        val source = buildSource(File(tmp.root, "source/files"), ctlText(live))
        val layout = importFrom(source, oldPrefix, linkSpelling)
        WowPathRewrite.rewrite(layout, WowPathRewrite.oldPrefixes(WowExportInfo.sourceFilesDir(layout)), layout.root.path)
        WowCtl.prepare(layout)
        return layout
    }

    private fun textFiles(root: File): List<File> = root.walkTopDown()
        .filter { it.isFile && !Files.isSymbolicLink(it.toPath()) }
        .filter { f -> f.inputStream().use { i -> i.readNBytes(8192).none { it == 0.toByte() } } }
        .toList()

    private fun env(layout: WowLayout, blizz: Boolean, log: File) = buildMap {
        put("FILES", layout.root.path)
        put("TZ", "<+0000>-00:00")
        put("CALLS_LOG", log.path)
        if (blizz) put("BLIZZ_LDSO", layout.loader()!!.path)
    }

    // ---- (1) the rewrite ----

    @Test fun noOldPackagePathRemainsInAnyTextFileOrLink() {
        for (live in listOf(false)) {
            val l = prepared(live)
            val offenders = textFiles(l.root).filter { "com.logie.warcraft" in it.readText() }.map { it.relativeTo(l.root).path }
            // (ctl.blizz.sh and the blizz/ wrapper are written after the rewrite from the rewritten ctl.sh)
            assertEquals("text files that still name the old app", emptyList<String>(), offenders)
            l.root.walkTopDown().filter { Files.isSymbolicLink(it.toPath()) }.forEach {
                val target = Files.readSymbolicLink(it.toPath()).toString()
                assertTrue("$it -> $target", target.startsWith(l.root.path))
            }
            assertEquals(l.root.path, WowPathRewrite.recordedPrefix(l))
            // the old folder is baked into the programs and nothing can change that: they are run by the loader
            assertTrue("com.logie.warcraft" in File(l.server, "bin/legacy-tool").readText(Charsets.ISO_8859_1))
        }
    }

    @Test fun theManifestsFolderIsRewrittenToo() {
        // The export records the WoW app's real path (what filesDir was); it need not be the standard one.
        val odd = File(tmp.root, "elsewhere/files")
        val l = prepared(oldPrefix = odd.path, linkSpelling = null)
        assertEquals(emptyList<String>(), textFiles(l.root).filter { odd.path in it.readText() }.map { it.name })
        assertTrue(l.ctl.readText().contains("FILES=\"\${FILES:-${l.root.path}}\""))
    }

    @Test fun rewriteIsIdempotentAndTouchesNothingTheSecondTime() {
        val l = prepared()
        val again = WowPathRewrite.rewrite(l, WowPathRewrite.oldPrefixes(WowExportInfo.sourceFilesDir(l)), l.root.path)
        assertFalse(again.changed)
    }

    // ---- (1) the generated script ----

    @Test fun generatedScriptPassesShellSyntaxChecks() {
        val l = prepared()
        val bash = runCatching {
            ProcessBuilder("bash", "-n", l.blizzCtl.path).redirectErrorStream(true).start().let { p ->
                val out = p.inputStream.bufferedReader().readText(); p.waitFor(); p.exitValue() to out
            }
        }.getOrNull()
        if (bash != null) assertEquals(bash.second, 0, bash.first)
        val posix = ProcessBuilder(shell, "-n", l.blizzCtl.path).redirectErrorStream(true).start().let { p ->
            val out = p.inputStream.bufferedReader().readText(); p.waitFor(); p.exitValue() to out
        }
        assertEquals(posix.second, 0, posix.first)
    }

    @Test fun everyProgramStartInTheScriptGoesThroughTheLoader() {
        val l = prepared()
        val original = l.ctl.readText().lines()
        val generated = l.blizzCtl.readText().lines()
        assertEquals("one line to one line", original.size, generated.size)
        val ld = "\"\$BLIZZ_LDSO\" --library-path \"\$SERVER/lib\" "
        var starts = 0
        for ((i, line) in generated.withIndex()) {
            if ("\"\$SERVER/bin/" !in line) continue
            if ("MySQLExecutable" in line) {
                assertTrue(line, "\\\"\$SERVER/blizz/mariadb\\\"" in line && "/bin/" !in line)
                continue
            }
            starts++
            assertTrue("line ${i + 1}: $line", ld + "\"\$SERVER/bin/" in line)
            assertEquals("the loader appears once per start: $line", 1, line.split("BLIZZ_LDSO").size - 1)
            // nothing else on the line changed
            assertEquals(original[i], line.replace(ld, ""))
        }
        // db, db-ping, db-stop, auth, world, maps, vmap extract/assemble, mmaps, dbimport, mariadb client
        assertEquals(11, starts)
        assertEquals(1, original.count { "MySQLExecutable" in it && "bin/mariadb" in it })
    }

    // ---- (1) configs the script writes ----

    private fun conf(file: File): Map<String, String> = file.readLines()
        .filter { it.contains('=') && !it.trimStart().startsWith("#") && !it.startsWith("[") }
        .associate { it.substringBefore('=').trim() to it.substringAfter('=').trim().removeSurrounding("\"") }

    @Test fun configureWritesConsistentConfigsInsideTheFolder() {
        val l = prepared()
        val run = sh(l.blizzCtl, listOf("configure"), l.run, env(l, true, File(l.run, "calls.log")))
        assertEquals(run.output, 0, run.code)
        val root = l.root.path
        val db = "127.0.0.1;${Realm.DATABASE_PORT};acore;acore"
        for ((etc, realm, logs, suffix) in listOf(
            listOf(l.etc, Realm.CHROMIE, l.logs, ""),
            listOf(l.etcRemix, Realm.REMIX, File(l.logs, "remix"), "_remix"),
        ).map { Quad(it[0] as File, it[1] as Realm, it[2] as File, it[3] as String) }) {
            val world = conf(File(etc, "worldserver.conf"))
            assertEquals(logs.path, world["LogsDir"])
            assertEquals(l.data.path, world["DataDir"])
            assertEquals("$root/run/tmp", world["TempDir"])
            assertEquals("$root/server/src", world["SourceDirectory"])
            assertEquals("$root/server/blizz/mariadb", world["MySQLExecutable"])
            assertEquals("$root/run/worldserver.pid", world["PidFile"])
            assertEquals(realm.id.toString(), world["RealmID"])
            assertEquals(realm.port.toString(), world["WorldServerPort"])
            assertEquals("$db;acore_auth", world["LoginDatabaseInfo"])
            assertEquals("$db;acore_world$suffix", world["WorldDatabaseInfo"])
            assertEquals("$db;${realm.charactersDatabase}", world["CharacterDatabaseInfo"])
            assertEquals("1", world["PlayerStart.CustomSpells"])
            val import = conf(File(etc, "dbimport.conf"))
            assertEquals("$root/server/blizz/mariadb", import["MySQLExecutable"])
            assertEquals(world["WorldDatabaseInfo"], import["WorldDatabaseInfo"])
            assertEquals(world["CharacterDatabaseInfo"], import["CharacterDatabaseInfo"])
            assertEquals(logs.path, import["LogsDir"])
            assertEquals("7", import["Updates.EnableDatabases"])
            assertEquals("$db;acore_playerbots$suffix", conf(File(etc, "modules/playerbots.conf"))["PlayerbotsDatabaseInfo"])
            assertEquals("$root/server/lua_scripts", conf(File(etc, "modules/mod_ale.conf"))["ALE.ScriptPath"])
        }
        // one auth server, the main realm's
        assertFalse(File(l.etcRemix, "authserver.conf").exists())
        val auth = conf(File(l.etc, "authserver.conf"))
        assertEquals("$root/run/authserver.pid", auth["PidFile"])
        assertEquals(l.logs.path, auth["LogsDir"])
        assertEquals("$root/server/blizz/mariadb", auth["MySQLExecutable"])
        assertEquals("$db;acore_auth", auth["LoginDatabaseInfo"])
        assertEquals(Realm.AUTH_PORT.toString(), auth["RealmServerPort"]) // the core's default; ctl.sh doesn't set it
        // the realms differ where they must
        assertEquals("1", conf(File(l.etcRemix, "modules/mod_wrath_remix.conf"))["WrathRemix.Enable"])
        assertEquals("0", conf(File(l.etc, "modules/mod_wrath_remix.conf"))["WrathRemix.Enable"])
        assertEquals("0", conf(File(l.etcRemix, "modules/mod_allied_races.conf"))["AlliedRaces.Enable"])
        assertEquals("1", conf(File(l.etc, "modules/mod_allied_races.conf"))["AlliedRaces.Enable"])
        assertEquals("10", conf(File(l.etcRemix, "worldserver.conf"))["StartPlayerLevel"])
        assertEquals("1", conf(File(l.etc, "worldserver.conf"))["StartPlayerLevel"])
        // Remix and Chromie share nothing but the auth database and the data
        assertTrue(Realm.CHROMIE.port != Realm.REMIX.port)
        // every absolute path any config now holds is inside the folder (nothing of the old app, nothing outside)
        val absolute = Regex("\"(/[^\"]+)\"")
        listOf(l.etc, l.etcRemix).forEach { etc ->
            etc.walkTopDown().filter { it.isFile }.forEach { f ->
                absolute.findAll(f.readText()).forEach { m ->
                    assertTrue("${f.relativeTo(l.root)}: ${m.groupValues[1]}", m.groupValues[1].startsWith(root))
                }
            }
        }
        // the constants WowRealm uses are what the script uses
        assertTrue("DB_PORT=\"\${DB_PORT:-${Realm.DATABASE_PORT}}\"" in l.ctl.readText())
        assertTrue(l.ctl.readText().contains("R_PORT=${Realm.CHROMIE.port}") && l.ctl.readText().contains("R_PORT=${Realm.REMIX.port}"))
        assertTrue(l.ctl.readText().contains("R_CHARACTERS=${Realm.REMIX.charactersDatabase}"))
    }

    private data class Quad(val etc: File, val realm: Realm, val logs: File, val suffix: String)

    @Test fun configureDiffersFromTheOriginalsOnlyInTheMariadbClientPath() {
        val l = prepared()
        val log = File(l.run, "calls.log")
        fun snapshot() = listOf(l.etc, l.etcRemix).flatMap { it.walkTopDown().filter { f -> f.isFile } }
            .associate { it.relativeTo(l.root).path to it.readText() }
        assertEquals(0, sh(l.ctl, listOf("configure"), l.run, env(l, false, log)).code)
        val original = snapshot()
        assertEquals(0, sh(l.blizzCtl, listOf("configure"), l.run, env(l, true, log)).code)
        val blizz = snapshot()
        assertEquals(original.keys, blizz.keys)
        for ((name, text) in original) {
            val other = blizz.getValue(name)
            if (text == other) continue
            val a = text.lines(); val b = other.lines()
            assertEquals(name, a.size, b.size)
            a.zip(b).filter { it.first != it.second }.forEach { (x, y) ->
                assertTrue("$name: $x vs $y", x.startsWith("MySQLExecutable") && y.startsWith("MySQLExecutable"))
                assertTrue(y, y.endsWith("/server/blizz/mariadb\""))
            }
        }
    }

    // ---- (1) the commands, compared with the original ----

    private val commands = listOf(
        listOf("db"), listOf("db-ping"), listOf("db-stop"), listOf("auth"),
        listOf("dbimport", "main"), listOf("dbimport", "remix"), listOf("modules", "main"), listOf("modules", "remix"),
        listOf("realmlist", "192.168.1.5"), listOf("sql", "acore_auth"),
        listOf("world", "main"), listOf("world", "remix"),
        listOf("maps", "/the/client"), listOf("vmaps", "/the/client"), listOf("mmaps", "2"),
        listOf("races"),
    )

    private class Call(val prog: String, val args: List<String>, val cwd: String, val env: Map<String, String>)

    private fun calls(log: File): List<Call> {
        if (!log.isFile) return emptyList()
        val result = ArrayList<Call>()
        var prog = ""; var args = ArrayList<String>(); var cwd = ""; var env = LinkedHashMap<String, String>()
        for (line in log.readLines()) {
            when {
                line.startsWith("PROG ") -> { prog = line.removePrefix("PROG "); args = ArrayList(); env = LinkedHashMap() }
                line.startsWith("ARG ") -> args += line.removePrefix("ARG ")
                line.startsWith("CWD ") -> cwd = line.removePrefix("CWD ")
                line.startsWith("ENV ") -> env[line.substringAfter("ENV ").substringBefore('=')] = line.substringAfter('=')
                line == "END" -> result += Call(prog, args, cwd, env)
            }
        }
        return result
    }

    private fun runAll(l: WowLayout, script: File, blizz: Boolean): List<Call> {
        val log = File(l.run, if (blizz) "blizz.log" else "original.log").also { it.delete() }
        // start from the same state each time
        assertEquals(0, sh(script, listOf("configure"), l.run, env(l, blizz, File(l.run, "x.log"))).code)
        for (command in commands) {
            val run = sh(script, command, l.run, env(l, blizz, log))
            assertEquals("${script.name} $command:\n${run.output}", 0, run.code)
        }
        return calls(log)
    }

    private fun commandsAreTheOriginals(live: Boolean) {
        val l = prepared(live)
        val original = runAll(l, l.ctl, blizz = false)
        val blizz = runAll(l, l.blizzCtl, blizz = true)
        assertFalse(File(l.run, "blizz.log.err").exists() && File(l.run, "blizz.log.err").readText().isNotEmpty())
        assertEquals("programs ran", 16, original.size)
        assertEquals(original.size, blizz.size)
        for ((a, b) in original.zip(blizz)) {
            assertEquals(a.prog, b.prog)
            assertEquals(a.prog, a.args, b.args)
            assertEquals(a.prog, a.cwd, b.cwd)
            assertEquals(a.prog, a.env, b.env)
        }
        // the loader got the server's own lib folder every time and nothing else
        val libs = File(l.run, "blizz.log.lib").readLines().toSet()
        assertEquals(setOf("LIBPATH ${l.server.path}/lib"), libs)

        // every path anything was started with is in the folder; ports are the realm's
        val root = l.root.path
        for (c in blizz) {
            val paths = c.args.flatMap { it.split('=', ';').filter { p -> p.startsWith("/") } } + c.env.values.flatMap { it.split(':') }.filter { it.startsWith("/") }
            for (p in paths) assertTrue("${c.prog}: $p", p.startsWith(root) || p == "/the/client" || p.startsWith("/the/client/"))
            assertFalse(c.prog, "com.logie.warcraft" in c.args.joinToString())
        }
        val byProg = blizz.groupBy { it.prog }
        val db = byProg.getValue("mariadbd").single()
        val expected = listOf(
            "--no-defaults", "--datadir=$root/mysql", "--basedir=$root/server", "--lc-messages-dir=$root/server/share/mariadb",
            "--character-sets-dir=$root/server/share/mariadb/charsets", "--plugin-dir=$root/server/lib/mariadb-plugins", "--tmpdir=$root/run/tmp",
            "--socket=$root/run/mysqld.sock", "--pid-file=$root/run/mysqld.pid", "--bind-address=127.0.0.1", "--port=${Realm.DATABASE_PORT}",
            "--skip-name-resolve", "--innodb-use-native-aio=0", "--innodb-log-file-size=48M", "--innodb-buffer-pool-size=256M",
            "--max-allowed-packet=64M", "--log-error=$root/logs/mariadb.log",
        )
        // (as root, as on a test machine, ctl.sh adds --user=root)
        assertEquals(expected, db.args.filter { it != "--user=root" })
        assertEquals("$root/server/lib/libandroidcompat.so", db.env["LD_PRELOAD"])
        assertTrue(db.args.none { "my.cnf" in it || "defaults-file" in it })
        for (admin in byProg.getValue("mariadb-admin")) {
            assertTrue(admin.args.containsAll(listOf("--no-defaults", "-h127.0.0.1", "-P${Realm.DATABASE_PORT}", "-uacore")))
        }
        assertEquals(listOf("ping"), byProg.getValue("mariadb-admin")[0].args.takeLast(1))
        assertEquals(listOf("shutdown"), byProg.getValue("mariadb-admin")[1].args.takeLast(1))
        for (client in byProg.getValue("mariadb")) assertTrue(client.args.containsAll(listOf("--no-defaults", "-h127.0.0.1", "-P${Realm.DATABASE_PORT}")))
        val auth = byProg.getValue("authserver").single()
        assertEquals(listOf("-c", "${l.etc.path}/authserver.conf"), auth.args)
        assertEquals(l.run.path, auth.cwd)
        val worlds = byProg.getValue("worldserver")
        assertEquals(listOf("-c", "${l.etc.path}/worldserver.conf"), worlds[0].args)
        assertEquals(listOf("-c", "${l.etcRemix.path}/worldserver.conf"), worlds[1].args)
        assertEquals("${l.etc.path}/modules", worlds[0].env["WOW_MODULES_CONF_DIR"])
        assertEquals("${l.etcRemix.path}/modules", worlds[1].env["WOW_MODULES_CONF_DIR"])
        assertEquals("$root/server/lib/libandroidcompat.so:$root/server/lib/libjemalloc.so.2", worlds[0].env["LD_PRELOAD"])
        assertEquals("$root/client", worlds[0].env["WOW_CLIENT_DIR"])
        assertEquals("$root/server/lib/ossl-modules", worlds[0].env["OPENSSL_MODULES"])
        assertEquals("1", worlds[0].env["AC_DISABLE_INTERACTIVE"])
        assertEquals(root, worlds[0].env["HOME"])
        assertEquals("$root/run/tmp", worlds[0].env["TMPDIR"])
        assertEquals("<+0000>-00:00", worlds[0].env["TZ"])
        val imports = byProg.getValue("dbimport")
        assertEquals(listOf("-c", "${l.etc.path}/dbimport.conf"), imports[0].args)
        assertEquals(listOf("-c", "${l.etcRemix.path}/dbimport.conf"), imports[1].args)
        // the world server's data comes from the conf; the module-data step may point it at data-modules
        assertTrue(conf(File(l.etc, "worldserver.conf"))["DataDir"]!!.startsWith(root))
    }

    @Test fun everyCommandStartsTheSameProgramsWithTheSameArgumentsAsTheOriginal() = commandsAreTheOriginals(live = false)

    @Test fun theSameAgainstTheRepositorysCurrentCtlShWhenItIsThere() {
        assumeTrue(File("/home/user/YeaBwoi/warcraft/server/ctl.sh").isFile)
        commandsAreTheOriginals(live = true)
    }

    @Test fun theMariadbWrapperRunsTheClientThroughTheLoaderWithTheShimPreloaded() {
        val l = prepared()
        val wrapper = File(l.blizzBin, "mariadb")
        assertTrue(wrapper.canExecute())
        val log = File(l.run, "wrapper.log")
        // (the shebang is Android's shell; here the shell is run on it)
        val run = sh(wrapper, listOf("-e", "select 1"), l.run, env(l, false, log) + ("LD_PRELOAD" to "/elsewhere/jemalloc.so"))
        assertEquals(run.output, 0, run.code)
        val c = calls(log).single()
        assertEquals("mariadb", c.prog)
        assertEquals(listOf("-e", "select 1"), c.args)
        assertEquals("${l.server.path}/lib/libandroidcompat.so", c.env["LD_PRELOAD"])
    }

    // ---- (4) permissions ----

    @Test fun importedProgramsAndLibrariesBecomeExecutableAndItIsIdempotent() {
        val source = buildSource(File(tmp.root, "source/files"), ctlText(false))
        val l = importFrom(source, standardOld)
        val everything = listOf("bin/worldserver", "bin/mariadbd", "bin/mariadb", "bin/mariadb-admin", "lib/ld-musl-aarch64.so.1", "lib/libandroidcompat.so",
            "lib/libjemalloc.so.2", "lib/ossl-modules/legacy.so", "ctl.sh")
        for (f in everything) assertFalse("$f before", File(l.server, f).canExecute())
        // a symlink in lib (as an alpine package may have) is left as it is
        Files.createSymbolicLink(File(l.server, "lib/libz.so.1").toPath(), File("libstdc++.so.6").toPath())
        val first = WowCtl.restoreExecutableBits(l)
        assertTrue(first >= everything.size)
        for (f in everything) assertTrue("$f after", File(l.server, f).canExecute())
        assertFalse("data is not made executable", File(l.databases, "ibdata1").canExecute())
        assertFalse(File(l.server, "etc/worldserver.conf.dist").canExecute())
        assertEquals(0, WowCtl.restoreExecutableBits(l))
        // prepare does it before anything runs, on its own
        for (f in everything) File(l.server, f).setExecutable(false, false)
        WowCtl.prepare(l)
        for (f in everything) assertTrue("$f after prepare", File(l.server, f).canExecute())
        assertTrue(l.blizzCtl.canExecute())
        assertTrue(File(l.blizzBin, "mariadb").canExecute())
    }

    // ---- (4) the imported database ----

    @Test fun theDatabaseFolderIsNeitherRewrittenNorGivenFlagsOrMarkersThatForceRecovery() {
        val l = prepared()
        assertEquals("ibdata", File(l.databases, "ibdata1").readText())
        assertEquals("iblog", File(l.databases, "ib_logfile0").readText())
        val script = l.blizzCtl.readText()
        assertFalse("innodb-force-recovery" in script || "innodb_force_recovery" in script)
        // the log file size is the one the data was written with (ctl.sh sets it for the WoW app)
        assertTrue("--innodb-log-file-size=48M" in script)
        // socket and pid file are in run/, which the export leaves out; the importer never has stale ones
        assertFalse(File(l.databases, "mysqld.pid").exists())
    }

    @Test fun theSocketPathFitsUnixLimitsOnARealPhone() {
        val socket = "/data/user/0/com.logie.blizz/files/games/wow/files/run/mysqld.sock"
        assertTrue(socket.length.toString(), socket.length < 108)
    }

    // ---- (3) the realm chosen ----

    @Test fun theChosenRealmIsReadFromTheWowAppsOwnPreferencesFormat() {
        val l = prepared()
        l.prefsDir.mkdirs()
        // exactly what PrefsDump.toJson writes for the realms preferences
        fun dump(realm: String) = "{\n  \"realm\": {\"type\": \"string\", \"value\": \"$realm\"}\n}\n"
        File(l.prefsDir, "realms.json").writeText(dump("remix"))
        assertEquals(Realm.REMIX, WowExportInfo.chosenRealm(l))
        File(l.prefsDir, "realms.json").writeText(dump("main"))
        assertEquals(Realm.CHROMIE, WowExportInfo.chosenRealm(l))
        File(l.prefsDir, "realms.json").writeText("{}\n")
        assertEquals(Realm.CHROMIE, WowExportInfo.chosenRealm(l))
        // a type that isn't a string is not a realm
        File(l.prefsDir, "realms.json").writeText("{\n  \"realm\": {\"type\": \"int\", \"value\": 2}\n}\n")
        assertEquals(Realm.CHROMIE, WowExportInfo.chosenRealm(l))
        // the realm keys and ports are the WoW app's Realms.kt; Wrath++ (docs/wrathpp) is Blizzard's own, ctl.sh's realm wrathpp
        assertEquals(listOf("main" to 8085, "remix" to 8086, "octo" to 8090, "legion" to 8095, "wrathpp" to 8087), Realm.entries.map { it.key to it.port })
        assertEquals(listOf(1, 2, 3, 4, 5), Realm.entries.map { it.id })
        assertEquals(listOf("acore_characters", "acore_characters_remix", "tw_char", "characters", "acore_characters_wrathpp"), Realm.entries.map { it.charactersDatabase })
        assertNotNull(Realm.byKey("remix"))
    }

    // ---- the settings the WoW app applies ----

    @Test fun settingsFollowTheDataFoldersLikeTheWowApp() {
        val l = prepared()
        assertEquals(0, sh(l.blizzCtl, listOf("configure"), l.run, env(l, true, File(l.run, "c.log"))).code)
        File(l.data, "mmaps").deleteRecursively()
        WowSettings.apply(l)
        for (etc in listOf(l.etc, l.etcRemix)) {
            val c = conf(File(etc, "worldserver.conf"))
            assertEquals("1", c["vmap.enableLOS"])
            assertEquals("1", c["vmap.enableIndoorCheck"])
            assertEquals("0", c["MoveMaps.Enable"])
        }
        File(l.data, "vmaps").deleteRecursively()
        WowSettings.apply(l)
        assertEquals("0", conf(File(l.etc, "worldserver.conf"))["vmap.enableHeight"])
        // the first time only: the bots and the first brackets
        assertEquals("50", conf(File(l.etc, "modules/playerbots.conf"))["Playerbots.MinRandomBots"])
        assertEquals("1", conf(File(l.etc, "modules/progression_system.conf"))["ProgressionSystem.Bracket_0"])
        assertEquals("0", conf(File(l.etc, "modules/progression_system.conf"))["ProgressionSystem.Bracket_20_29"])
        File(l.etc, "modules/playerbots.conf").writeText("Playerbots.MinRandomBots = 7\n")
        WowSettings.apply(l)
        assertEquals("7", conf(File(l.etc, "modules/playerbots.conf"))["Playerbots.MinRandomBots"])
    }
}
