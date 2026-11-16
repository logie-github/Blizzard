package com.logie.blizz.forevernew

import android.content.Context
import java.io.File

/**
 * Forever's own folders, `files/realms/forever-v2/`. Nothing of the other realms' folders, and the old
 * `files/forever`, `imagefs`, `imagefs_shared` and `forever-arm64` of earlier work are never read, imported or deleted.
 */
class ForeverLayout(val root: File) {
    val server = File(root, "server")
    val bin = File(server, "bin")
    val lib = File(server, "lib")
    val etc = File(server, "etc")
    val sql = File(server, "src/sql")
    val data = File(server, "data")
    val logs = File(root, "logs")
    val run = File(root, "run")
    val keys = File(root, "keys")
    val db = File(root, "db")
    val client = File(root, "client")
    val manifests = File(root, "manifests")
    val downloads = File(root, "downloads")
    val backups = File(root, "backups")
    val checkpoints = File(root, "checkpoints")
    val stateFile = File(root, "state.json")
    val credentials = File(keys, "account.json")
    val installedManifest = File(manifests, "installed-package.json")

    fun loader(): File? = lib.listFiles { f -> f.name.startsWith("ld-musl-") && f.name.endsWith(".so.1") }?.minByOrNull { it.name }
    fun hasServer(): Boolean = loader() != null && listOf("worldserver", "bnetserver", "mariadbd").all { File(bin, it).isFile }
    fun hasMaps(): Boolean = listOf("maps", "vmaps", "mmaps", "dbc").all { File(data, it).list()?.isNotEmpty() == true }

    companion object {
        const val NAME = "forever-v2"
        fun of(context: Context) = ForeverLayout(File(context.applicationContext.filesDir, "realms/$NAME"))
    }
}
