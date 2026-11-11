package com.logie.blizz.wow

import android.content.Context
import android.os.SystemClock
import java.io.File
import java.io.IOException

/**
 * The Wrath realms' database by itself, for the Character Porter: MariaDB started through the realm's own `ctl.sh db` (as
 * Play starts it) while no world server runs, so a character can be written into the realm's databases with nothing else
 * holding them, then stopped again. The realm must have been started once in this app (Play): that is what makes its
 * configs, moves its paths here and sets its databases up; until then [open] says so.
 *
 * What is piped into [sqlCommand] (`ctl.sh sql <database>`) is the porter's SQL; MariaDB answers in batch rows.
 */
class RealmDatabase private constructor(
    val layout: WowLayout,
    private val loader: File,
    private val runner: ProcessRunner,
    private val db: RealmProcess,
) : AutoCloseable {

    /** `sh ctl.blizz.sh sql` with the realm's environment: the database is appended for each call. */
    fun sqlCommand(): WowCtl.Command = WowCtl.command(layout, loader, WowCtl.posixTimeZone(), "sql")

    /** Stops MariaDB (it flushes and ends; after a minute it is ended). */
    override fun close() {
        runCatching {
            val stop = runner.start(WowCtl.command(layout, loader, WowCtl.posixTimeZone(), "db-stop"), File(layout.logs, "db-stop.out"), false)
            stop.waitFor(30_000)
        }
        if (!db.waitFor(60_000)) {
            db.destroy()
            if (!db.waitFor(15_000)) db.destroyForcibly()
        }
    }

    companion object {
        /** Why [open] can't be had now, or null when it can (the realm imported and started once here). */
        fun problem(layout: WowLayout): String? = when {
            !layout.isImported() -> "World of Warcraft (Wrath+) isn't imported: import it first (its box, Auto Import)."
            !File(layout.databases, ".imported").exists() || !File(layout.etc, "worldserver.conf").isFile ->
                "Play Wrath+ once first: its first start sets its realm up here. Then come back to port."
            else -> null
        }

        /**
         * Stops the realm if it is running (characters saved first), then starts its database alone and waits for it to answer.
         * Background thread. [step] is told what is under way.
         */
        suspend fun open(context: Context, step: (String) -> Unit = {}, runner: ProcessRunner = SystemRunner()): RealmDatabase {
            val layout = WowLayout.of(context)
            problem(layout)?.let { throw IOException(it) }
            if (WowRealm.isRunning()) {
                step("Stopping the realm (its characters are saved first)")
                WowRealm.stopAndWait(context)
                if (WowRealm.isRunning()) throw IOException("The realm didn't stop: stop it in the game, then try again.")
            }
            step("Starting the realm's database")
            // As Play does before its database: paths moved here if the files came from elsewhere, the scripts written.
            WowPathRewrite.rewrite(layout, WowPathRewrite.oldPrefixes(WowExportInfo.sourceFilesDir(layout)), layout.root.path)
            val loader = WowCtl.prepare(layout)
            runner.endLeftovers(layout)
            for (name in listOf("mysqld.pid", "mysqld.sock", "mysqld.sock.lock")) File(layout.run, name).delete()
            val process = runner.start(WowCtl.command(layout, loader, WowCtl.posixTimeZone(), "db"), File(layout.logs, "db.out"), false)
            val deadline = SystemClock.uptimeMillis() + 120_000
            while (true) {
                if (!process.isAlive) throw IOException("The realm's database didn't start (logs/mariadb.log says why).")
                val ping = runner.start(WowCtl.command(layout, loader, WowCtl.posixTimeZone(), "db-ping"), File(layout.logs, "db-ping.out"), false)
                if (ping.waitFor(10_000) && ping.exitValue() == 0) break
                if (!ping.waitFor(0)) ping.destroyForcibly()
                if (SystemClock.uptimeMillis() > deadline) {
                    process.destroy()
                    throw IOException("The realm's database didn't answer in two minutes.")
                }
                Thread.sleep(1000)
            }
            return RealmDatabase(layout, loader, runner, process)
        }
    }
}
