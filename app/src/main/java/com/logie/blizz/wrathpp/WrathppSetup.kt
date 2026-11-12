package com.logie.blizz.wrathpp

import android.content.Context
import com.logie.blizz.wow.WowLayout

/**
 * What Play on Wrath++'s page does before its realm starts: its server package ([WrathppServerPackage], downloaded the
 * first time and when a newer one is published) and its own copy of the game ([WrathppClient], made once from Wrath+'s).
 * Each step reports its words and share done, thinned out ([Reports]) so the screen moves without being flooded.
 */
object WrathppSetup {
    fun run(context: Context, say: (String, Float?) -> Unit) {
        val layout = WowLayout.of(context)
        val report = Reports(say)
        WrathppServerPackage.ensure(layout, report::say)
        if (!WrathppClient.isMade(layout.wrathppClient)) {
            report.say("Making Wrath++'s copy of the game (step 4 of 4)", 0f)
            WrathppClient.make(layout.client, layout.wrathppClient, report::say)
        }
        // The add-on (WarcraftXL's runtime and the native mod: the creator's numbers): Wrath++ still plays without it.
        val notes = StringBuilder()
        runCatching { WrathppAddon.ensure(layout.wrathppClient, report::say) }
            .onSuccess { notes.append("add-on: ${WrathppAddon.installedSha(layout.wrathppClient) ?: "none"}\n") }
            .onFailure { e -> notes.append("add-on FAILED: ${e.message}\n") }
        // Shadowlands' looks for the ten races (WrathppLooks): without them, the game's own.
        runCatching { WrathppLooks.ensure(layout.wrathppClient, layout.wrathppServer, report::say) }
            .onSuccess { notes.append("looks: ${WrathppLooks.installedSha(layout.wrathppClient, layout.wrathppServer) ?: "none"}\n") }
            .onFailure { e -> notes.append("looks FAILED: ${e.message}\n") }
        // The undead skins you imported (WrathppUndead): new colours after each race's own in the looks' tables, taken out
        // again when the import is removed. Without the looks there is nothing to add them to.
        val undead = runCatching { WrathppUndead.apply(WrathppUndead.store(context), layout.wrathppClient, layout.wrathppServer) }
            .onSuccess { notes.append("undead skins: ${if (it != null) "in" else "none"}\n") }
            .onFailure { e -> notes.append("undead skins FAILED: ${e.message}\n") }
            .getOrNull()
        // The creator (Shadowlands' two screens), from the app itself, whatever happened to the add-on; with it what it
        // shows: the looks' own list of options (made with them: sl_creator.py) and the undead skins' (written above).
        report.say("Putting in Wrath++'s character creator", null)
        runCatching {
            WrathppAddon.writeGluePatch(layout.wrathppClient, glue(context.assets.open(GLUE_ASSET).use { it.readBytes() }, layout.wrathppClient, undead))
        }.onSuccess { notes.append("creator patch: written\n") }.onFailure { e -> notes.append("creator patch FAILED: ${e.message}\n") }
        val log = java.io.File(layout.realmLogs(com.logie.blizz.wow.Realm.WRATHPP), "setup.log")
        runCatching { log.parentFile?.mkdirs(); log.writeText(notes.toString()) }
    }

    const val GLUE_ASSET = "wrathpp/WrathppCreate.lua"
    const val LOOKS_DATA = "WrathppLooks.lua"

    /**
     * The creator's files for its patch: the script ([creator]), the looks' options from the looks in [client] when they
     * are in (`Data/patch-Z.MPQ/Interface/GlueXML/WrathppLooks.lua`), and the undead skins' ([undead], [WrathppUndead.apply]'s).
     * The script reads the other two when the creator opens, so the order they load in doesn't matter.
     */
    fun glue(creator: ByteArray, client: java.io.File, undead: String?): Map<String, ByteArray> {
        val files = LinkedHashMap<String, ByteArray>()
        files["WrathppCreate.lua"] = creator
        java.io.File(client, "Data/${WrathppLooks.PATCH}/Interface/GlueXML/$LOOKS_DATA").takeIf { it.isFile }?.let { files[LOOKS_DATA] = it.readBytes() }
        if (undead != null) files[WrathppUndead.LUA] = undead.toByteArray(Charsets.UTF_8)
        return files
    }

    /**
     * After Wrath++'s game has started: a report of what it was set up with and how WarcraftXL's runtime got on (its log), so
     * that a start that looked like stock 3.3.5 says why without anyone pasting anything.
     */
    fun report(context: Context) {
        val layout = WowLayout.of(context)
        val client = layout.wrathppClient
        val setup = runCatching { java.io.File(layout.realmLogs(com.logie.blizz.wow.Realm.WRATHPP), "setup.log").readText() }.getOrDefault("no setup.log")
        val wxl = java.io.File(client, "Logs/WarcraftXL.log")
        val wxlLog = runCatching { wxl.readLines().takeLast(120).joinToString("\n") }.getOrDefault("no Logs/WarcraftXL.log (the runtime didn't start, or wrote elsewhere)")
        val files = listOf(WrathppAddon.EXE, "WarcraftXL.dll", "Mods/wrathpp.native/bin/x86/wrathpp-native.dll", "Mods/wxl.lua/bin/x86/wxl-lua.dll",
            "Mods/wxl.glue-unlock/bin/x86/glue-unlock.dll", "Data/${WrathppAddon.PATCH}", "WowPatched.exe", "Wow.exe")
            .joinToString("\n") { name -> val f = java.io.File(client, name); "$name: ${if (f.exists()) "${f.length()} bytes" else "missing"}" }
        // The game's archives in the order it reads them, folders (patch-M, patch-Z: the looks) marked.
        val archives = java.io.File(client, "Data").listFiles()?.filter { it.name.endsWith(".mpq", ignoreCase = true) }?.sortedBy { it.name.lowercase() }
            ?.joinToString("\n") { "Data/${it.name}: ${if (it.isDirectory) "folder" else "${it.length()} bytes"}" } ?: "no Data"
        runCatching {
            com.logie.blizz.reports.BugReports.report(
                context, "Wrath++ start", "What Wrath++'s game was started with",
                details = listOf("Add-on" to (WrathppAddon.installedSha(client) ?: "none"),
                    "Looks" to (WrathppLooks.installedSha(client, layout.wrathppServer) ?: "none")),
                log = "$setup\n$files\n$archives\n\n--- WarcraftXL.log ---\n$wxlLog",
            )
        }
    }

    /**
     * Passes a report on when its words' step changed, its share moved by half a percent, or a quarter second passed;
     * the rest are dropped (a download reports every 64 KiB).
     */
    class Reports(private val out: (String, Float?) -> Unit, private val clock: () -> Long = System::currentTimeMillis) {
        private var lastStep: String? = null
        private var lastFraction: Float? = null
        private var lastAt = 0L

        fun say(message: String, fraction: Float?) {
            val step = message.substringBefore(':')
            val now = clock()
            val moved = fraction != null && (lastFraction == null || fraction - lastFraction!! >= 0.005f || fraction >= 1f)
            if (step != lastStep || moved || now - lastAt >= 250) {
                lastStep = step; lastFraction = fraction; lastAt = now
                out(message, fraction)
            }
        }
    }
}
