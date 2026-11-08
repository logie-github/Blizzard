package com.logie.blizz.forever

import com.logie.blizz.wow.WowCtl
import java.io.File

/**
 * How the Forever realm's `ctl.sh` is run. The programs have this app's own path baked in as their
 * ELF interpreter, so nothing is rewritten (unlike the imported WoW realms): `ctl.sh` is run as-is
 * with Android's shell, and `FILES` points it at the realm folder.
 *
 * Pure (no Android): unit-tested.
 */
object ForeverCtl {
    /** The pid files the realm's programs write, for ending leftovers after the app was killed. */
    val PID_FILES = listOf("worldserver.pid", "bnetserver.pid", "mysqld.pid")

    fun command(layout: ForeverLayout, vararg args: String): WowCtl.Command = WowCtl.Command(
        argv = listOf("/system/bin/sh", layout.ctl.path) + args,
        env = mapOf(
            "FILES" to layout.root.path,
            "TZ" to WowCtl.posixTimeZone(),
        ),
        directory = layout.run,
    )

    /** The package has no executable bits after a plain unpack: set them on the programs, the loader and ctl.sh. */
    fun makeExecutable(layout: ForeverLayout): Int {
        var changed = 0
        val targets = buildList {
            add(layout.ctl)
            File(layout.server, "bin").listFiles()?.let(::addAll)
            File(layout.server, "lib").listFiles()?.let(::addAll)
        }
        for (file in targets) if (file.isFile && !file.canExecute() && file.setExecutable(true, false)) changed++
        return changed
    }
}
