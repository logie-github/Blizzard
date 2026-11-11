package com.logie.blizz.porter.wago

import com.logie.blizz.porter.net.Net
import java.io.File
import java.io.IOException
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong

/**
 * The game's files the preview draws, by their file ids, fetched from wago.tools for one build of the game
 * (`https://wago.tools/api/casc/<id>?download&version=<build>`) and kept on the phone under [dir]/<build>/<id>. All of a
 * look's files come from the same build: a model and its skin or skeleton from two builds don't fit together (a blood elf
 * drawn from the newest model with last month's triangles is a tangle). Nothing of the game is in the app itself.
 */
class GameFiles(private val net: Net, val build: String, private val dir: File) {
    private val folder = File(dir, build)

    /** Where file [id] is on the phone, or null when it isn't there yet. */
    fun path(id: Int): File? = File(folder, id.toString()).takeIf { it.isFile && it.length() > 0 }

    fun has(id: Int): Boolean = path(id) != null

    /** How far [fetch] has come: files done of files wanted, and bytes so far. */
    data class Progress(val done: Int, val total: Int, val bytes: Long)

    /**
     * Fetches the files of [ids] that aren't there yet, four at a time; [progress] is told after each. Stops (throwing) when
     * [cancelled] says so. A file that can't be had after four tries fails the whole fetch with its id.
     */
    fun fetch(ids: Collection<Int>, cancelled: () -> Boolean = { false }, progress: (Progress) -> Unit = {}) {
        val missing = ids.filter { it > 0 && !has(it) }.distinct()
        if (missing.isEmpty()) return
        folder.mkdirs()
        val done = AtomicInteger(0)
        val bytes = AtomicLong(0)
        val stop = AtomicBoolean(false)
        val pool = Executors.newFixedThreadPool(4)
        try {
            val jobs = ArrayList<Future<*>>()
            for (id in missing) {
                jobs += pool.submit {
                    if (stop.get() || cancelled()) return@submit
                    one(id) { n -> bytes.addAndGet(n) }
                    progress(Progress(done.incrementAndGet(), missing.size, bytes.get()))
                }
            }
            for (job in jobs) {
                try {
                    job.get()
                } catch (e: java.util.concurrent.ExecutionException) {
                    stop.set(true)
                    throw (e.cause as? IOException) ?: IOException(e.cause?.message ?: e.toString())
                }
            }
            if (cancelled()) throw IOException("Stopped")
        } finally {
            pool.shutdownNow()
        }
    }

    private fun one(id: Int, counted: (Long) -> Unit) {
        val target = File(folder, id.toString())
        var last: Exception? = null
        for (attempt in 0 until 4) {
            var got = 0L
            try {
                net.save("${WagoTables.SITE}/api/casc/$id?download&version=$build", target) { total ->
                    counted(total - got)
                    got = total
                }
                return
            } catch (e: Exception) {
                counted(-got)
                last = e
                Thread.sleep(700L shl attempt)
            }
        }
        throw IOException("The game's file $id couldn't be fetched from wago.tools (${last?.message})")
    }

    /** Removes the files kept for other builds than this one (they don't fit this build's). */
    fun forgetOtherBuilds() {
        dir.listFiles()?.filter { it.isDirectory && it.name != build }?.forEach { it.deleteRecursively() }
    }

    /** How much the kept files take. */
    fun size(): Long = folder.listFiles()?.sumOf { it.length() } ?: 0L
}
