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
        // Shadowlands' creator's own art (WrathppArt): without it the creator draws with 3.3.5's pictures in the same places.
        runCatching { WrathppArt.ensure(layout.wrathppClient, report::say) }
            .onSuccess { notes.append("creator art: ${WrathppArt.installedSha(layout.wrathppClient) ?: "none"}\n") }
            .onFailure { e -> notes.append("creator art FAILED: ${e.message}\n") }
        // Ralia's mod, when you imported it (WrathppRalia): its skins in place of the looks' they are named for.
        // Its zip is looked for by its name where downloads are (ImportFinder), and taken in by itself the first time.
        runCatching {
            val store = WrathppRalia.store(context)
            val found = runCatching { ImportFinder.find("ralia.zip") }.getOrNull()
            val taken = runCatching { WrathppRalia.lookFor(store, found) }.onFailure { e -> notes.append("ralia.zip not read: ${e.message}\n") }.getOrNull()
            if (taken != null) notes.append("ralia.zip found (${found?.parent}): $taken textures\n")
            WrathppRalia.apply(store, layout.wrathppClient, report::say)
        }
            .onSuccess { notes.append("ralia: $it skins\n") }
            .onFailure { e -> notes.append("ralia FAILED: ${e.message}\n") }
        // The undead skins you imported (WrathppUndead): new colours after each race's own in the looks' tables, taken out
        // again when the import is removed. Without the looks there is nothing to add them to.
        val undead = runCatching { WrathppUndead.apply(WrathppUndead.store(context), layout.wrathppClient, layout.wrathppServer) }
            .onSuccess { notes.append("undead skins: ${if (it != null) "in" else "none"}\n") }
            .onFailure { e -> notes.append("undead skins FAILED: ${e.message}\n") }
            .getOrNull()
        // The women are drawn without underwear (WrathppBare), whatever the three above put into the table.
        runCatching { WrathppBare.apply(layout.wrathppClient) }
            .onSuccess { notes.append("women's underwear: $it rows cleared now\n") }
            .onFailure { e -> notes.append("women's underwear FAILED: ${e.message}\n") }
        // The creator (Shadowlands' two screens), from the app itself, whatever happened to the add-on; with it what it
        // shows: the looks' own list of options (made with them: sl_creator.py) and the undead skins' (written above).
        report.say("Putting in Wrath++'s character creator", null)
        // A crash of an earlier launch that wasn't reported goes now; one with the creator on the screen leaves the
        // creator out for the rest of this build (WrathppLogs): the game's own screen, with a line saying so.
        runCatching { reportCrashes(context) }
        val creatorOff = WrathppLogs.creatorOff(java.io.File(layout.wrathppClient, "Logs"), com.logie.blizz.BuildConfig.VERSION_CODE)
        runCatching {
            // (pictures of the creator as the game draws it are asked for until those of this build, art and looks went: WrathppPictures)
            val shots = WrathppPictures.flag(java.io.File(layout.wrathppClient, "Logs"), WrathppPictures.state(com.logie.blizz.BuildConfig.VERSION_CODE,
                WrathppArt.installedSha(layout.wrathppClient), WrathppLooks.installedSha(layout.wrathppClient, layout.wrathppServer)))
            val files = if (creatorOff) mapOf(OFF_NOTE to offNote(com.logie.blizz.BuildConfig.VERSION_CODE).toByteArray(Charsets.UTF_8))
            else glue(context.assets.open(GLUE_ASSET).use { it.readBytes() }, layout.wrathppClient, undead, shots)
            WrathppAddon.writeGluePatch(layout.wrathppClient, files)
            files
        }.onSuccess { files ->
            notes.append("creator patch: " + (if (creatorOff) "the creator LEFT OUT (the game crashed with it up in this build); " else "") + files.entries.joinToString(", ") { "${it.key} ${it.value.size}" } + "\n")
        }.onFailure { e -> notes.append("creator patch FAILED: ${e.message}\n") }
        val log = java.io.File(layout.realmLogs(com.logie.blizz.wow.Realm.WRATHPP), "setup.log")
        runCatching { log.parentFile?.mkdirs(); log.writeText(notes.toString()) }
    }

    const val GLUE_ASSET = "wrathpp/WrathppCreate.lua"
    const val LOOKS_DATA = "WrathppLooks.lua"
    const val OFF_NOTE = "WrathppCreateOff.lua"

    /** In place of the creator after a crash with it up: the game's own screen, and a line at its top saying why. */
    fun offNote(build: Int): String = """
        -- Wrath++: the creator is left out after the game crashed with it on the screen (app build $build); the report was sent.
        pcall(function()
        	local screen = CharacterCreateFrame or CharacterCreate
        	local s = screen:CreateFontString(nil, "OVERLAY", "GlueFontHighlightSmall")
        	s:SetPoint("TOP", screen, "TOP", 0, -4)
        	s:SetText("Wrath++'s creator is off after a crash (build $build): the report was sent, the next update turns it on again")
        end)
    """.trimIndent() + "\n"

    /**
     * The creator's files for its patch: the script ([creator]), the asking for pictures of it ([shots], [WrathppPictures.flag]),
     * Shadowlands' art's table when the art is in ([WrathppArt]),
     * the looks' options from the looks in [client] when they are in
     * (`Data/patch-Z.MPQ/Interface/GlueXML/WrathppLooks.lua`), and the undead skins' ([undead], [WrathppUndead.apply]'s).
     * The script reads the other two when the creator opens, so the order they load in doesn't matter.
     */
    fun glue(creator: ByteArray, client: java.io.File, undead: String?, shots: String? = null): Map<String, ByteArray> {
        val files = LinkedHashMap<String, ByteArray>()
        files["WrathppCreate.lua"] = creator
        if (shots != null) files[WrathppPictures.FLAG] = shots.toByteArray(Charsets.UTF_8)
        WrathppArt.atlas(client)?.let { files[WrathppArt.ATLAS] = it.readBytes() }
        java.io.File(client, "Data/${WrathppLooks.PATCH}/Interface/GlueXML/$LOOKS_DATA").takeIf { it.isFile }?.let { files[LOOKS_DATA] = it.readBytes() }
        if (undead != null) files[WrathppUndead.LUA] = undead.toByteArray(Charsets.UTF_8)
        return files
    }

    /**
     * After Wrath++'s game has started: a report of what it was set up with and how WarcraftXL's runtime got on (its log), so
     * that a start that looked like stock 3.3.5 says why without anyone pasting anything. Sent whenever what it says
     * differs from the last one sent (another build of the app, add-on or looks, or the creator saying other things):
     * as an ordinary report it had gone once a day, its title being the same sentence every time, and a day of changes
     * said nothing (the user: "I don't think the reporter works right").
     */
    fun report(context: Context) {
        val layout = WowLayout.of(context)
        val client = layout.wrathppClient
        runCatching { reportCrashes(context) }
        val setup = runCatching { java.io.File(layout.realmLogs(com.logie.blizz.wow.Realm.WRATHPP), "setup.log").readText() }.getOrDefault("no setup.log")
        val logs = java.io.File(client, "Logs")
        val wxl = java.io.File(logs, "WarcraftXL.log")
        val lines = runCatching { wxl.readLines() }.getOrNull()
        val wxlLog = lines?.takeLast(120)?.joinToString("\n") ?: "no Logs/WarcraftXL.log (the runtime didn't start, or wrote elsewhere)"
        val creator = WrathppLogs.lastCreatorLines(logs)
        val files = listOf(WrathppAddon.EXE, "WarcraftXL.dll", "Mods/wrathpp.native/bin/x86/wrathpp-native.dll", "Mods/wxl.lua/bin/x86/wxl-lua.dll",
            "Mods/wxl.glue-unlock/bin/x86/glue-unlock.dll", "Data/${WrathppAddon.PATCH}", "WowPatched.exe", "Wow.exe")
            .joinToString("\n") { name -> val f = java.io.File(client, name); "$name: ${if (f.exists()) "${f.length()} bytes" else "missing"}" }
        // The game's archives in the order it reads them, folders (patch-M, patch-Z: the looks) marked.
        val archives = java.io.File(client, "Data").listFiles()?.filter { it.name.endsWith(".mpq", ignoreCase = true) }?.sortedBy { it.name.lowercase() }
            ?.joinToString("\n") { "Data/${it.name}: ${if (it.isDirectory) "folder" else "${it.length()} bytes"}" } ?: "no Data"
        val addon = WrathppAddon.installedSha(client) ?: "none"
        val looks = WrathppLooks.installedSha(client, layout.wrathppServer) ?: "none"
        val state = listOf(com.logie.blizz.BuildConfig.VERSION_CODE.toString(), addon, looks, setup.replace(Regex("\\d+"), "#"), WrathppLogs.creatorSaid(creator)).joinToString("|")
        val last = java.io.File(com.logie.blizz.reports.BugReports.dir(context), "wrathpp-start.state")
        if (runCatching { last.readText() }.getOrNull() == state) return
        runCatching {
            com.logie.blizz.reports.BugReports.submit(context, com.logie.blizz.reports.BugReports.Report(
                "Wrath++ start: build ${com.logie.blizz.BuildConfig.VERSION_CODE}, add-on ${addon.take(8)}, looks ${looks.take(8)}",
                com.logie.blizz.reports.BugReports.body("Wrath++ start", "What Wrath++'s game was started with",
                    listOf("Add-on" to addon, "Looks" to looks, "Creator" to (creator.lastOrNull()?.substringAfter("creator: ") ?: "said nothing (not opened yet, or the native mod without WrathPP_Log)")),
                    log = "$setup\n$files\n$archives\n\n--- the creator's lines (this launch, or the one before) ---\n${creator.joinToString("\n")}\n\n--- WarcraftXL.log ---\n$wxlLog"),
            ))
            last.parentFile?.mkdirs()
            last.writeText(state)
        }
    }

    /**
     * Crashes of Wrath++'s game that were not reported yet, each sent once whatever went before ([WrathppLogs]: the
     * runtime writes a crash into the launch's log, and the launches' logs stay on the phone), with the game's own
     * crash file of that time (`Errors/`). Called as the app starts, before each start of the game, a while after it
     * and when the game's screen goes. A crash with the creator on the screen leaves the creator out of this build.
     */
    @Synchronized
    fun reportCrashes(context: Context) {
        val layout = WowLayout.of(context)
        val client = layout.wrathppClient
        val logs = java.io.File(client, "Logs")
        if (!logs.isDirectory) return
        // (the creator's pictures of itself, taken since the app asked for them: sent now that the game was left)
        runCatching { WrathppPictures.send(context) }
        val setup = runCatching { java.io.File(layout.realmLogs(com.logie.blizz.wow.Realm.WRATHPP), "setup.log").readText() }.getOrDefault("no setup.log")
        for (crash in WrathppLogs.unreported(logs)) {
            if (crash.creatorUp) WrathppLogs.creatorCrashed(logs, com.logie.blizz.BuildConfig.VERSION_CODE)
            // the game's own report of it: the file of its Errors folder written nearest the launch's log
            val log = java.io.File(logs, crash.file)
            val own = java.io.File(client, "Errors").listFiles { f -> f.isFile && f.name.endsWith(".txt") }
                ?.minByOrNull { kotlin.math.abs(it.lastModified() - log.lastModified()) }
                ?.takeIf { kotlin.math.abs(it.lastModified() - log.lastModified()) < 10 * 60 * 1000L }
            val ownText = own?.let { f -> runCatching { f.readText().take(6000) }.getOrNull() }
            com.logie.blizz.reports.BugReports.submit(context, com.logie.blizz.reports.BugReports.Report(
                "Wrath++ crash: ${crash.what.take(140)}",
                com.logie.blizz.reports.BugReports.body("Wrath++ crash", crash.what,
                    listOf("Launch" to crash.file, "Creator on the screen" to (if (crash.creatorUp) "yes: left out for the rest of this build" else "no, or it said nothing"),
                        "Add-on" to (WrathppAddon.installedSha(client) ?: "none"), "Looks" to (WrathppLooks.installedSha(client, layout.wrathppServer) ?: "none")),
                    log = "--- the game's own crash file (${own?.name ?: "none near that time"}) ---\n${ownText ?: ""}\n\n--- setup ---\n$setup\n--- ${crash.file} ---\n${crash.text}"),
            ))
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
