package com.logie.blizz.importer

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.DocumentsContract
import android.provider.Settings
import java.io.File

/**
 * The phone's own storage, read by path once the person allows it ("Search the phone" in a game's import): the importers then
 * find a game's files by themselves, wherever they were put, and a file that was picked has its neighbours (an installer's
 * data files beside it). The document picker gives one file with nothing beside it, or a folder to be chosen exactly; the
 * phone's reports of 4 to 10 November 2026 were mostly that (Warcraft II's installer without its .bin, StarCraft II's and
 * StarCraft: Remastered's "needs its data files").
 *
 * The app targets Android 9 for the games' programs, so Android's storage permission still reads all of the phone's storage for
 * it; where a newer Android says no, its "all files" switch does. Nothing is written or deleted here.
 */
object PhoneStorage {
    const val PERMISSION = android.Manifest.permission.READ_EXTERNAL_STORAGE

    /** Top folders of the phone's storage that hold photos, music and other apps' files, never a game: not searched. */
    val SKIPPED = setOf("android", "dcim", "pictures", "movies", "music", "podcasts", "ringtones", "alarms", "notifications", "audiobooks", "recordings")

    fun root(): File = Environment.getExternalStorageDirectory()

    /** Whether the app can read the phone's storage by path now. */
    fun readable(context: Context): Boolean = runCatching {
        val all = Build.VERSION.SDK_INT >= 30 && Environment.isExternalStorageManager()
        val granted = context.checkSelfPermission(PERMISSION) == PackageManager.PERMISSION_GRANTED
        (all || granted) && root().listFiles() != null
    }.getOrDefault(false)

    /** Android's page where the person switches on "all files" for this app (Android 11 and later). */
    fun allFilesSettings(context: Context): Intent? {
        if (Build.VERSION.SDK_INT < 30) return null
        val own = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, Uri.parse("package:${context.packageName}"))
        val any = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
        return listOf(own, any).firstOrNull { it.resolveActivity(context.packageManager) != null }
    }

    /** The phone's storage as a place to search: everything but [SKIPPED] and hidden folders. */
    fun searchRoot(root: File = root()): SourceNode = StorageNode(root, top = true)

    /**
     * The file a document id of Android's own storage names: `primary:Roms/Warcraft/setup.exe` is `<root>/Roms/Warcraft/setup.exe`,
     * `1A2B-3C4D:Games/x` is on the card of that name under [volumes]. Null for anything else (a path that climbs out, an id
     * without a volume). Plain Kotlin, unit-tested.
     */
    fun pathOf(documentId: String, root: File, volumes: File = File("/storage")): File? {
        val volume = documentId.substringBefore(':', "")
        val path = documentId.substringAfter(':', "")
        if (volume.isEmpty() || !documentId.contains(':')) return null
        if (path.split('/').any { it == ".." }) return null
        val base = when {
            volume.equals("primary", ignoreCase = true) -> root
            volume.matches(Regex("[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}")) -> File(volumes, volume)
            else -> return null
        }
        return if (path.isEmpty()) base else File(base, path)
    }

    /** The file or folder a picked [uri] is on the phone's storage (a document or a folder of Android's storage picker), if it is there to read. */
    fun fileOf(uri: Uri, tree: Boolean, root: File = root()): File? = runCatching {
        if (uri.authority != "com.android.externalstorage.documents") return null
        val id = if (tree) DocumentsContract.getTreeDocumentId(uri) else DocumentsContract.getDocumentId(uri)
        pathOf(id, root)?.takeIf { if (tree) it.isDirectory else it.isFile }
    }.getOrNull()
}

/** A folder of the phone's storage as the importers search it: no hidden folders, and at the top none of [PhoneStorage.SKIPPED]. */
private class StorageNode(file: File, private val top: Boolean) : FileNode(file) {
    override fun children(): List<SourceNode> = file.listFiles().orEmpty()
        .filter { !it.name.startsWith(".") && !(top && it.isDirectory && it.name.lowercase() in PhoneStorage.SKIPPED) }
        .sortedBy { it.name }
        .map { if (it.isDirectory) StorageNode(it, top = false) else FileNode(it) }
}
