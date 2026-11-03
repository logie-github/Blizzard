package com.logie.blizz.music

import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/**
 * The downloaded music, one file per [MusicCatalog.Track] in [dir]. A song's address may be the
 * file or a page that holds it (khinsider's): the page's audio address is read and fetched instead.
 * A file only gets its name once it is whole and looks like audio. Plain Kotlin, unit-tested.
 */
class MusicStore(
    private val dir: File,
    private val open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection },
) {
    fun file(key: String) = File(dir, "$key.mp3")

    fun has(key: String): Boolean = file(key).let { it.isFile && it.length() >= MIN_BYTES }

    fun missing(): List<MusicCatalog.Track> = MusicCatalog.tracks.filter { !has(it.key) }

    fun delete() {
        dir.listFiles()?.forEach { it.delete() }
    }

    /** Downloads [track] unless it is there; the file. Throws [IOException] with what went wrong. */
    fun download(track: MusicCatalog.Track, onBytes: (Long) -> Unit = {}): File {
        val target = file(track.key)
        if (has(track.key)) return target
        dir.mkdirs()
        val part = File(dir, target.name + ".part")
        var url = track.url
        repeat(MAX_HOPS) {
            val connection = open(URL(url))
            try {
                connection.instanceFollowRedirects = true
                connection.connectTimeout = 15_000
                connection.readTimeout = 30_000
                connection.setRequestProperty("User-Agent", AGENT)
                val code = connection.responseCode
                if (code !in 200..299) throw IOException("${URL(url).host} answered $code")
                if (connection.contentType.orEmpty().lowercase().startsWith("text/html")) {
                    val html = connection.inputStream.use { readUpTo(it, PAGE_LIMIT) }
                    url = audioUrlFromHtml(String(html, Charsets.UTF_8), url) ?: throw IOException("no audio file on ${URL(url).host}'s page")
                    return@repeat
                }
                var done = 0L
                connection.inputStream.use { input ->
                    part.outputStream().use { out ->
                        val buffer = ByteArray(64 * 1024)
                        while (true) {
                            val n = input.read(buffer)
                            if (n < 0) break
                            out.write(buffer, 0, n)
                            done += n
                            onBytes(done)
                        }
                    }
                }
                if (part.length() < MIN_BYTES || !looksLikeAudio(part)) {
                    part.delete()
                    throw IOException("the download wasn't an audio file")
                }
                target.delete()
                if (!part.renameTo(target)) throw IOException("couldn't save the file")
                return target
            } finally {
                connection.disconnect()
            }
        }
        throw IOException("the address led to pages, not to a file")
    }

    companion object {
        const val MIN_BYTES = 20_000L
        private const val MAX_HOPS = 3
        private const val PAGE_LIMIT = 2_000_000
        private const val AGENT = "Mozilla/5.0 (Linux; Android 14) Blizzard"

        private val AUDIO_TAG = Regex("""<audio[^>]*?\ssrc="([^"]+)"""", RegexOption.IGNORE_CASE)
        private val MP3_LINK = Regex("""href="([^"]+\.mp3)"""", RegexOption.IGNORE_CASE)

        /** The song file a page points at (its audio player, or its first MP3 link), as a full address; null when there is none. */
        fun audioUrlFromHtml(html: String, base: String): String? {
            val found = AUDIO_TAG.find(html)?.groupValues?.get(1) ?: MP3_LINK.find(html)?.groupValues?.get(1) ?: return null
            return runCatching { URL(URL(base), found.replace("&amp;", "&")).toString() }.getOrNull()
        }

        /** MP3 (an ID3 tag or a frame sync), Ogg, FLAC or WAV. */
        fun looksLikeAudio(file: File): Boolean {
            val head = ByteArray(4)
            val n = file.inputStream().use { it.read(head) }
            if (n < 4) return false
            val text = String(head, Charsets.ISO_8859_1)
            return text.startsWith("ID3") || text == "OggS" || text == "fLaC" || text == "RIFF" ||
                ((head[0].toInt() and 0xff) == 0xff && (head[1].toInt() and 0xe0) == 0xe0)
        }

        private fun readUpTo(input: java.io.InputStream, limit: Int): ByteArray {
            val out = ByteArrayOutputStream()
            val buffer = ByteArray(16 * 1024)
            while (out.size() < limit) {
                val n = input.read(buffer)
                if (n < 0) break
                out.write(buffer, 0, n)
            }
            return out.toByteArray()
        }
    }
}
