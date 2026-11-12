package com.logie.blizz.wrathpp

import android.os.Build
import android.os.Environment
import java.io.File

/**
 * A file of yours looked for by its name where downloads usually are (the user: "it will look for ralia.zip"): Download,
 * Downloads, Documents and the top of the phone's shared storage. Only where the app may read all files (the access the
 * importers ask for); otherwise nothing is found and the file is picked by hand.
 */
object ImportFinder {
    fun mayLook(): Boolean = Build.VERSION.SDK_INT < Build.VERSION_CODES.R || Environment.isExternalStorageManager()

    fun find(vararg names: String): File? {
        if (!mayLook()) return null
        val root = runCatching { Environment.getExternalStorageDirectory() }.getOrNull() ?: return null
        return find(listOf(File(root, "Download"), File(root, "Downloads"), File(root, "Documents"), root), names.toList())
    }

    /** The first of [folders] holding a file named one of [names] (whatever the letters' case), the newest of them. */
    fun find(folders: List<File>, names: List<String>): File? {
        val wanted = names.map { it.lowercase() }.toSet()
        for (folder in folders) {
            val found = runCatching { folder.listFiles { f -> f.isFile && f.name.lowercase() in wanted } }.getOrNull()?.maxByOrNull { it.lastModified() }
            if (found != null) return found
        }
        return null
    }
}
