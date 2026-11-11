package com.logie.blizz.porter

import android.content.Context
import com.logie.blizz.BuildConfig
import com.logie.blizz.porter.armory.Appearance
import com.logie.blizz.porter.armory.Armory
import com.logie.blizz.porter.armory.ArmoryCharacter
import com.logie.blizz.porter.armory.BattleNet
import com.logie.blizz.porter.look.CharacterLook
import com.logie.blizz.porter.look.Looks
import com.logie.blizz.porter.look.ModelFiles
import com.logie.blizz.porter.look.Worn
import com.logie.blizz.porter.net.HttpNet
import com.logie.blizz.porter.wago.GameFiles
import com.logie.blizz.porter.wago.WagoTables
import java.io.File
import java.io.IOException

/**
 * The Character Porter's work behind its screens (ui/CharacterPorter.kt): the Armory, and a character's look made ready to
 * draw from wago.tools (the game's tables for the look, the game's files for the models and textures), everything kept under
 * the app's `files/porter` for the live build of the game (a newer build fetches anew, and the older one's files go).
 */
object Porter {
    private val wagoNet = HttpNet("BlizzardLauncher/${BuildConfig.VERSION_NAME} (+https://github.com/logie-github/Blizzard)")
    val armory = Armory(HttpNet(HttpNet.BROWSER))

    fun dir(context: Context) = File(context.applicationContext.filesDir, "porter")

    /** Where the game's files are kept for [build]: the preview reads them from there. */
    fun filesDir(context: Context, build: String) = File(File(dir(context), "files"), build)

    /** The game's build the look is made from: asked of wago.tools once a day, the last one known when it can't be asked. */
    fun build(context: Context): String {
        val prefs = context.applicationContext.getSharedPreferences("porter", Context.MODE_PRIVATE)
        val known = prefs.getString("build", null)
        val at = prefs.getLong("buildAt", 0L)
        if (known != null && System.currentTimeMillis() - at < DAY) return known
        return try {
            WagoTables.liveBuild(wagoNet).also { prefs.edit().putString("build", it).putLong("buildAt", System.currentTimeMillis()).apply() }
        } catch (e: IOException) {
            known ?: throw IOException("wago.tools can't be reached for the game's build (${e.message})")
        }
    }

    sealed interface Step {
        data object Tables : Step
        data class Files(val done: Int, val total: Int, val megabytes: Long) : Step
    }

    /** A look ready to draw: every file it names, and those its models name, are on the phone under [files]. */
    class Ready(val look: CharacterLook, val files: File, val build: String)

    /**
     * What [c] wears as the look shows it: the Armory's items with the looks they were given, or, with Blizzard's API's
     * [appearance], what each slot shows by its item and variant (the Armory's inventory type kept, for the hand a weapon hangs in).
     */
    fun worn(c: ArmoryCharacter, appearance: Appearance?): List<Worn> {
        val armory = c.items.map { Worn(it.slot, it.id, it.transmogItemId, it.modifiedAppearanceId, it.inventoryType) }
        if (appearance == null || appearance.shown.isEmpty()) return armory
        val shown = appearance.shown.mapNotNull { s -> BattleNet.armorySlot(s.slotType)?.let { slot -> slot to s } }.toMap()
        val types = c.items.associate { it.slot to it.inventoryType }
        return armory.filter { it.slot !in shown } + shown.map { (slot, s) -> Worn(slot, s.item, inventoryType = types[slot].orEmpty(), modifier = s.modifier) }
    }

    /**
     * [c]'s look, with what it needs fetched; with Blizzard's API's [appearance] (the person's key), their own face and hair.
     * Long (the first time a race is seen, its model and skeleton are tens of MB): call off the main thread.
     */
    fun prepare(context: Context, c: ArmoryCharacter, appearance: Appearance? = null, cancelled: () -> Boolean = { false }, progress: (Step) -> Unit = {}): Ready {
        val build = build(context)
        progress(Step.Tables)
        val tables = WagoTables(wagoNet, build, File(dir(context), "tables"))
        val look = Looks(tables).of(c.raceId, c.gender, c.classId, worn(c, appearance), appearance?.choices.orEmpty())
        val files = GameFiles(wagoNet, build, File(dir(context), "files"))
        var bytes = 0L
        var done = 0
        var total = 0
        fun fetch(ids: Collection<Int>) {
            val missing = ids.filter { !files.has(it) }.distinct()
            if (missing.isEmpty()) return
            total += missing.size
            val before = done
            files.fetch(missing, cancelled) { p ->
                done = before + p.done
                progress(Step.Files(done, total, (bytes + p.bytes) / 1_048_576))
            }
            bytes += missing.sumOf { files.path(it)?.length() ?: 0L }
        }
        fetch(look.files())
        // What the models name: their skins, their own textures, their skeletons, the standing animation.
        for (model in look.models()) {
            val path = files.path(model) ?: continue
            val found = ModelFiles.of(path) ?: continue
            fetch(found.all())
            var skeleton = found.skeleton
            var depth = 0
            while (skeleton != null && depth++ < 3) {
                fetch(listOf(skeleton))
                val s = files.path(skeleton)?.let { ModelFiles.skeleton(it) } ?: break
                fetch(s.animations)
                skeleton = s.skeleton
            }
        }
        // The kept tables and files of an older build don't fit this one.
        files.forgetOtherBuilds()
        File(dir(context), "tables").listFiles()?.filter { it.isDirectory && it.name != build }?.forEach { it.deleteRecursively() }
        return Ready(look, filesDir(context, build), build)
    }

    /** The game's tables for the live build, as wago.tools gives them (kept under `files/porter/tables`). */
    fun tables(context: Context): WagoTables = WagoTables(wagoNet, build(context), File(dir(context), "tables"))

    /**
     * What a port carries beyond the Armory's summary ([ArmoryPort.Extras]), and what the person should know of it: the
     * Armory's mounts and standings, each mount's spell (the game's Mount table), and with the person's Battle.net key their
     * quests, achievements, titles and looks (today's choices made into the old creator's: [ArmoryPort.appearance]). What
     * can't be had is left out and said; nothing here stops a port. Network: call off the main thread.
     */
    fun extras(context: Context, c: ArmoryCharacter, step: (String) -> Unit = {}): Pair<ArmoryPort.Extras, List<String>> {
        val notes = ArrayList<String>()
        fun <T> tried(what: String, default: T, block: () -> T): T = try {
            block()
        } catch (e: Exception) {
            notes.add("$what couldn't be read (${e.message ?: e.javaClass.simpleName}): left out.")
            default
        }
        step("Reading ${c.name}'s mounts and standings from the Armory")
        val mounts = tried("Their mounts", emptyList()) { armory.mounts(c.region, c.realmSlug, c.slug) }
        val reputations = tried("Their standings", emptyList()) { armory.reputations(c.region, c.realmSlug, c.slug) }
        val tables = tables(context)
        if (mounts.isNotEmpty()) step("Finding each mount's spell (wago.tools)")
        val spells = tried("The mounts' spells", emptyMap()) { ArmoryPort.mountSpells(tables, mounts.map { it.id }) }
        val api = BattleNetKey.client(context)
        if (api == null) {
            notes.add("Without a Battle.net key (the key button above) the port has no quests, achievements or titles, and their face and hair are the realm's first.")
            return ArmoryPort.Extras(mounts, spells, reputations) to notes
        }
        step("Asking Blizzard's API for their quests, achievements, titles and looks")
        val quests = tried("Their quests", emptyList()) { api.completedQuests(c.region, c.realmSlug, c.slug) }
        val achievements = tried("Their achievements", emptyList()) { api.achievements(c.region, c.realmSlug, c.slug) }
        val titles = tried("Their titles", null) { api.titles(c.region, c.realmSlug, c.slug) }
        val choices = tried("Their looks", null) { api.appearance(c.region, c.realmSlug, c.slug) }?.choices.orEmpty()
        val looks = if (choices.isEmpty()) null else tried("Their looks", null) { ArmoryPort.appearance(tables, c.raceId, c.gender, choices) }
        if (choices.isEmpty()) notes.add("Blizzard's API gave no looks for them: their face and hair are the realm's first.")
        looks?.second?.takeIf { it.isNotEmpty() }?.let { newer ->
            notes.add("Their ${newer.joinToString(" and ")} ${if (newer.size == 1) "is" else "are"} newer than the old character creator: the realm's first is used.")
        }
        return ArmoryPort.Extras(mounts, spells, reputations, quests, achievements, titles, looks?.first) to notes
    }

    /** How much the porter keeps on the phone (the game's files and tables). */
    fun size(context: Context): Long = dir(context).walkTopDown().filter { it.isFile }.sumOf { it.length() }

    fun clear(context: Context) {
        dir(context).deleteRecursively()
    }

    private const val DAY = 24L * 60 * 60 * 1000
}
