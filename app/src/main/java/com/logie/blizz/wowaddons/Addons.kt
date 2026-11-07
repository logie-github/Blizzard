// Ported from the World of Warcraft app (com.logie.warcraft.Addons), for Blizzard's three clients.

package com.logie.blizz.wowaddons

import android.content.Context
import android.net.Uri
import java.io.File
import java.io.IOException
import java.util.zip.ZipFile

/**
 * A game's add-ons ([AddonGame]), in the client's `Interface/AddOns`: any the user picks, from warperia.com
 * ([AddonStoreOf]) or from zips (none come with the app). A zip's add-ons are found however it's
 * packed ([AddonLayout]) and put in place, each replacing an older copy of itself. An add-on that's
 * turned off waits in `Interface/AddOns-off`, where the game doesn't look. The game loads them the
 * next time it starts (or `/reload` in the game).
 */
object Addons {
    data class Addon(
        val folder: String,
        val title: String,
        val version: String?,
        /** Made for this version of the game (3.3.5a's 30300, Legion's 70300, OctoWoW's 11200); others load too (the app turns the check off). */
        val forThisGame: Boolean,
        /** In `AddOns`, where the game loads it; else turned off. */
        val on: Boolean,
    )

    class NoAddonException : IOException("No add-on in this zip")

    fun folder(context: Context, game: AddonGame) = File(game.client(context), "Interface/AddOns")

    /** Where turned-off add-ons wait, next to `AddOns`. */
    private fun offFolder(context: Context, game: AddonGame) = File(game.client(context), "Interface/AddOns-off")

    fun list(context: Context, game: AddonGame): List<Addon> =
        (read(folder(context, game), on = true, game) + read(offFolder(context, game), on = false, game).filter { off ->
            // A copy in both places: the one the game loads counts.
            !File(folder(context, game), off.folder).isDirectory
        }).sortedBy { it.title.lowercase() }

    private fun read(dir: File, on: Boolean, game: AddonGame): List<Addon> =
        // The app's own add-ons (the touch controls', the bots') aren't the user's to manage.
        dir.listFiles { file -> file.isDirectory && file.name.lowercase() !in game.ownFolders }.orEmpty()
            .mapNotNull { addon ->
                val toc = addon.listFiles { file -> file.isFile && file.name.equals("${addon.name}.toc", ignoreCase = true) }
                    ?.firstOrNull() ?: return@mapNotNull null
                val fields = runCatching { AddonLayout.tocFields(toc.readText()) }.getOrDefault(emptyMap())
                Addon(
                    folder = addon.name,
                    title = fields["Title"]?.takeIf { it.isNotBlank() } ?: addon.name,
                    version = fields["Version"]?.takeIf { it.isNotBlank() },
                    forThisGame = fields["Interface"]?.trim() == game.interfaceVersion,
                    on = on,
                )
            }

    /** Installs the add-ons in the zip at [uri]; returns their folders. Background thread. */
    fun install(context: Context, uri: Uri, game: AddonGame): List<String> {
        val copy = game.check(context, File(game.temp(context).also { game.mkdirs(context, it) }, "addon.zip"))
        try {
            context.contentResolver.openInputStream(uri)?.use { input ->
                copy.outputStream().use { input.copyTo(it) }
            } ?: throw IOException("Couldn't open the file")
            return installZip(context, copy, game)
        } finally {
            game.delete(context, copy)
        }
    }

    /**
     * Installs the add-ons in [zip]; returns their folders. Each goes where its older copy is: an
     * add-on that was turned off stays off. Background thread.
     */
    fun installZip(context: Context, zip: File, game: AddonGame): List<String> {
        val addOns = folder(context, game)
        val off = offFolder(context, game)
        ZipFile(zip).use { file ->
            val entries = file.entries().toList().filterNot { it.isDirectory }
            val plan = AddonLayout.plan(entries.map { it.name })
            if (plan.folders.isEmpty()) throw NoAddonException()
            game.mkdirs(context, addOns)
            val places = plan.folders.associateWith { name ->
                if (File(off, name).isDirectory && !File(addOns, name).isDirectory) off else addOns
            }
            // Each add-on whole: older copies go first, so files it no longer has don't linger.
            for (name in plan.folders) {
                game.delete(context, File(addOns, name))
                game.delete(context, File(off, name))
            }
            for (entry in entries) {
                val target = plan.targets[entry.name.replace('\\', '/').trimStart('/')] ?: continue
                val place = places[target.substringBefore('/')] ?: continue
                val out = File(place, target)
                if (!out.canonicalPath.startsWith(place.canonicalPath + File.separator)) continue
                out.parentFile?.let { game.mkdirs(context, it) }
                file.getInputStream(entry).use { input -> game.check(context, out).outputStream().use { input.copyTo(it) } }
            }
            return plan.folders
        }
    }

    /** Turns an add-on on (the game loads it) or off (it waits outside `AddOns`). */
    fun setOn(context: Context, folder: String, on: Boolean, game: AddonGame): Boolean {
        val (fromPlace, toPlace) = if (on) offFolder(context, game) to folder(context, game) else folder(context, game) to offFolder(context, game)
        val from = File(fromPlace, folder)
        val to = File(toPlace, folder)
        if (!isIn(from, fromPlace) || !isIn(to, toPlace)) return false
        if (!from.isDirectory) return to.isDirectory
        to.parentFile?.let { game.mkdirs(context, it) }
        game.delete(context, to)
        return game.move(context, from, to)
    }

    fun delete(context: Context, folder: String, game: AddonGame): Boolean {
        var gone = false
        for (place in listOf(folder(context, game), offFolder(context, game))) {
            val dir = File(place, folder)
            if (isIn(dir, place) && dir.exists()) gone = game.delete(context, dir) || gone
        }
        return gone
    }

    /** The add-on's folder is there, on or off. */
    fun exists(context: Context, folder: String, game: AddonGame): Boolean =
        File(folder(context, game), folder).isDirectory || File(offFolder(context, game), folder).isDirectory

    /** [dir] is a folder right inside [place], not anywhere else a name like `..` leads. */
    private fun isIn(dir: File, place: File): Boolean =
        dir.canonicalFile.parentFile?.path == place.canonicalPath

    // What came from warperia.com ----------------------------------------------------------------

    @Synchronized
    fun records(context: Context, game: AddonGame): List<AddonRecord> =
        game.recordsFile(context).takeIf { it.isFile }?.let { AddonRecords.parse(it.readText()) }.orEmpty()

    /** Changes the records in one go, so changes made at the same time don't undo each other. */
    @Synchronized
    fun updateRecords(context: Context, game: AddonGame, change: (List<AddonRecord>) -> List<AddonRecord>) {
        val before = records(context, game)
        val after = change(before)
        if (after != before) saveRecords(context, game, after)
    }

    @Synchronized
    private fun saveRecords(context: Context, game: AddonGame, records: List<AddonRecord>) {
        val file = game.recordsFile(context)
        file.parentFile?.let { game.mkdirs(context, it) }
        val temp = game.check(context, File(file.path + ".new"))
        temp.writeText(AddonRecords.format(records))
        if (!game.replace(context, temp, file)) throw IOException("Couldn't save the add-ons list")
    }
}
