// Ported from the World of Warcraft app (com.logie.warcraft.AddonGame, turtle/, felsong/), for Blizzard's three clients.
package com.logie.blizz.wowaddons

import android.content.Context
import com.logie.blizz.game.LegionClientSetup
import com.logie.blizz.game.OctoClientSetup
import com.logie.blizz.game.WowClientSetup
import com.logie.blizz.game.WowPlay
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.wowinput.TouchAddon
import java.io.File
import java.io.IOException

/**
 * A game's add-ons: its client, warperia.com's section for it, and how its files are changed.
 * Blizzard has three: Wrath+ ([WowAddonGames.WRATH]), Legion ([WowAddonGames.LEGION]) and OctoWoW
 * ([WowAddonGames.OCTOWOW]), each in its imported client.
 */
interface AddonGame {
    val flavor: Warperia.Flavor

    /** The interface number add-ons made for this client carry ("30300" for 3.3.5a). */
    val interfaceVersion: String

    /** Add-on folders that are the app's own, not the user's to manage. */
    val ownFolders: Set<String>

    fun hasClient(context: Context): Boolean

    fun client(context: Context): File

    /** Where what came from warperia.com is recorded. */
    fun recordsFile(context: Context): File

    /** Where a download or a picked zip waits while it's installed. */
    fun temp(context: Context): File

    /** [file] may be written (an add-on's file, the records); returns it. */
    fun check(context: Context, file: File): File

    fun mkdirs(context: Context, folder: File)

    /** Deletes [target] (an add-on's folder, a file) and everything in it. */
    fun delete(context: Context, target: File): Boolean

    /** Moves [from] to [to], which isn't there (an add-on turned on or off). */
    fun move(context: Context, from: File, to: File): Boolean

    /** Puts the finished [temp] in place of [file]. */
    fun replace(context: Context, temp: File, file: File): Boolean

    /** What to say when there's no client to put add-ons in. */
    fun noClientMessage(context: Context): String
}

/**
 * An imported client of Blizzard's library ([libraryId]: "wow", "wow_legion", "wow_octowow") as an [AddonGame]. Its
 * add-ons are in `<client>/Interface/AddOns`; the records and the downloads wait next to the client
 * (`warperia-addons.tsv`, `addon-downloads`). Every change goes through an [AddonGuard] that
 * allows only the client's `Interface` folder, the downloads' folder and the records.
 */
class ClientAddonGame(
    val libraryId: String,
    override val flavor: Warperia.Flavor,
    override val interfaceVersion: String,
    override val ownFolders: Set<String>,
    private val clientOf: (root: File) -> File,
    private val isClient: (client: File) -> Boolean,
    private val noClientText: String,
) : AddonGame {
    private class Place(val at: Long, val client: File, val guard: AddonGuard)

    @Volatile private var place: Place? = null

    /** The client's place, read from the library at most every few seconds (an install asks for it once per file). */
    private fun place(context: Context): Place {
        val now = System.nanoTime()
        place?.let { if (now - it.at < KEEP_NS) return it }
        val paths = GameImportManager.paths(context)
        val entry = runCatching { GameImportManager.library(context).get(libraryId) }.getOrNull()
        val root = File(entry?.installPath ?: paths.game(libraryId).path)
        val client = clientOf(root)
        val guard = AddonGuard(
            roots = listOf(File(client, "Interface"), downloads(client)),
            files = listOf(records(client)),
        )
        return Place(now, client, guard).also { place = it }
    }

    private fun records(client: File) = File(client.parentFile ?: client, "warperia-addons.tsv")

    private fun downloads(client: File) = File(client.parentFile ?: client, "addon-downloads")

    override fun hasClient(context: Context) = isClient(place(context).client)

    override fun client(context: Context): File = place(context).client

    override fun recordsFile(context: Context): File = records(place(context).client)

    override fun temp(context: Context): File = downloads(place(context).client)

    override fun check(context: Context, file: File): File = place(context).guard.check(file)

    override fun mkdirs(context: Context, folder: File) {
        place(context).guard.mkdirs(folder)
    }

    override fun delete(context: Context, target: File): Boolean {
        place(context).guard.delete(target)
        return true
    }

    override fun move(context: Context, from: File, to: File): Boolean {
        place(context).guard.move(from, to)
        return true
    }

    override fun replace(context: Context, temp: File, file: File): Boolean {
        place(context).guard.replace(temp, file)
        return true
    }

    override fun noClientMessage(context: Context): String = noClientText

    private companion object {
        const val KEEP_NS = 3_000_000_000L
    }
}

/** Blizzard's three World of Warcraft clients, as add-on games. */
object WowAddonGames {
    /** The 3.3.5a client's add-ons carry `## Interface: 30300`. */
    const val WRATH_INTERFACE = AddonLayout.INTERFACE
    /** The 7.3.5 client's add-ons carry `## Interface: 70300`. */
    const val LEGION_INTERFACE = "70300"
    /** OctoWoW's client is 1.12's underneath: its add-ons carry `## Interface: 11200`. */
    const val OCTOWOW_INTERFACE = "11200"

    /** Wrath+ (3.3.5a): `games/wow/files/client`. */
    val WRATH = ClientAddonGame(
        libraryId = "wow",
        flavor = Warperia.Flavor.WOTLK,
        interfaceVersion = WRATH_INTERFACE,
        // The touch controls' own add-on is the app's, not the user's to manage.
        ownFolders = setOf(TouchAddon.FOLDER.lowercase()),
        clientOf = { root -> WowPlay.clientFolder(root) },
        isClient = { WowClientSetup.hasClient(it) },
        noClientText = "Import Wrath+ first (Games): add-ons go in its client.",
    )

    /** Legion (7.3.5): `games/wow_legion/files/felsong/client`. */
    val LEGION = ClientAddonGame(
        libraryId = WowPlay.LEGION_ID,
        flavor = Warperia.Flavor.LEGION,
        interfaceVersion = LEGION_INTERFACE,
        ownFolders = emptySet(),
        clientOf = { root -> File(root, "files/felsong/client") },
        isClient = { LegionClientSetup.hasClient(it) },
        noClientText = "Import Legion first (Games): add-ons go in its client.",
    )

    /** OctoWoW (1.12 underneath): `games/wow_octowow/files/turtle/client`. */
    val OCTOWOW = ClientAddonGame(
        libraryId = WowPlay.OCTO_ID,
        flavor = Warperia.Flavor.VANILLA,
        interfaceVersion = OCTOWOW_INTERFACE,
        // The bots' control add-on is the app's (put in at each start), not the user's to manage.
        ownFolders = setOf("tortoisebotsmanager"),
        clientOf = { root -> File(root, "files/turtle/client") },
        isClient = { OctoClientSetup.hasClient(it) },
        noClientText = "Import OctoWoW first (Games): add-ons go in its client.",
    )

    /** The game for a launcher game id ("wow", "wow_legion", "wow_octowow"), or null. */
    fun of(gameId: String): ClientAddonGame? = when (gameId) {
        "wow" -> WRATH
        WowPlay.LEGION_ID -> LEGION
        WowPlay.OCTO_ID -> OCTOWOW
        else -> null
    }

    /** What the person is told for a missing client, as an exception where one is thrown. */
    fun noClient(game: AddonGame, context: Context) = IOException(game.noClientMessage(context))
}
