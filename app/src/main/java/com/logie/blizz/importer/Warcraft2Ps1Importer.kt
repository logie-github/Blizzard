package com.logie.blizz.importer

import com.logie.blizz.ps1.Ps1Activity
import java.io.File
import java.io.RandomAccessFile

/** The Dark Saga disc is copied into app storage for the embedded PlayStation core. */
class Warcraft2Ps1Importer : GameImporter {
    override val gameId = "warcraft2"
    override val title = "Warcraft II: The Dark Saga"
    override val recipe = 3
    override val keptInGame = listOf("wargus", "Save", "SaveGames")
    private val prompt = "Pick your Warcraft II: The Dark Saga PlayStation disc (.iso, .chd, or a folder containing the .cue and .bin files)."

    override fun detect(env: ImportEnv): Detection {
        if (installedDisc(env.paths.game(gameId)) != null) return Detection(true, emptyMap())
        val name = Regex("""war\s*craft[ _.-]*(ii|2)(?![a-z0-9])|dark[ _.-]*saga|slus[_. -]*004[_. -]*80|sles[_. -]*008[_. -]*78""", RegexOption.IGNORE_CASE)
        val disc = Scan(env.searchRoots()).files.firstOrNull { imageExtension(it) in setOf("iso", "chd", "cue") && name.containsMatchIn(it.name) }
        return Detection(false, if (disc == null) emptyMap() else mapOf(DISC_INPUT to disc))
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) = emptyList<AutoSource>()
    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) =
        if (detection.installed || DISC_INPUT in detection.found) emptyList()
        else listOf(MissingInput(DISC_INPUT, prompt, PickKind.FILE_OR_FOLDER))

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        var source = (supplied[DISC_INPUT] as? Supplied.Picked)?.source ?: detection.found[DISC_INPUT]
        if (source == null && detection.installed) return
        if (source?.isDirectory == true) {
            val files = source.children().filterNot { it.isDirectory }
            source = files.singleOrNull { imageExtension(it) == "cue" }
                ?: files.singleOrNull { imageExtension(it) in setOf("iso", "chd") }
        }
        if (source == null) throw ImportException(Problem.MISSING_SOURCE_DATA, prompt)
        val assembler = Assembler(env.paths, gameId)
        val stage = assembler.begin()
        fun copy(node: SourceNode, name: String): File {
            var done = 0L
            return copyInto(node, stage, name, env.cancel) { bytes ->
                done += bytes
                env.progress(Progress(Stage.EXTRACTING, "Copying ${node.name}", done, node.size))
            }.also {
                if (node.size > 0 && it.length() != node.size) {
                    throw ImportException(Problem.CORRUPT_ARCHIVE, "The copy of ${node.name} is incomplete.")
                }
            }
        }
        try {
            when (imageExtension(source)) {
                "iso", "chd" -> copy(source, "disc.${imageExtension(source)}")
                "cue" -> {
                    val neighbors = source.siblings().orEmpty()
                    val text = source.open().bufferedReader().use { reader ->
                        val buffer = CharArray(65537)
                        val count = reader.readNCharsCompat(buffer)
                        if (count == buffer.size) throw ImportException(Problem.CORRUPT_ARCHIVE, "The CUE file is too large.")
                        String(buffer, 0, count)
                    }
                    val tracks = linkedMapOf<String, String>()
                    val cue = text.removePrefix("\uFEFF").lineSequence().map { line ->
                        val directive = cueWhitespace.split(line.trim())
                        if (directive.first().uppercase() in cueLayoutDirectives) {
                            return@map directive.joinToString(" ").uppercase()
                        }
                        if (!cueFileDirective.containsMatchIn(line.trimStart())) return@map line
                        val filename = cueFile.matchEntire(line.trim())?.let { it.groupValues[1].ifEmpty { it.groupValues[2] } }
                            ?: throw ImportException(Problem.CORRUPT_ARCHIVE, "The CUE must reference binary tracks.")
                        val name = tracks.getOrPut(filename.lowercase()) {
                            val track = neighbors.singleOrNull { !it.isDirectory && it.name.equals(filename, true) }
                                ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "Pick the folder with the CUE and all of its BIN tracks together. Missing: $filename")
                            val target = "track-${tracks.size + 1}.bin"
                            if (copy(track, target).length() < 2352) throw ImportException(Problem.CORRUPT_ARCHIVE, "The BIN track is incomplete: $filename")
                            target
                        }
                        "FILE \"$name\" BINARY"
                    }.joinToString("\n")
                    if (tracks.isEmpty()) throw ImportException(Problem.CORRUPT_ARCHIVE, "The CUE file contains no BIN tracks.")
                    File(stage, "disc.cue").writeText(cue)
                }
                else -> throw ImportException(Problem.UNSUPPORTED_VERSION, prompt)
            }
            if (installedDisc(stage) == null) throw ImportException(Problem.CORRUPT_ARCHIVE, "The disc image is incomplete or unreadable. Pick a complete copy. $prompt")
            env.cancel.check()
            assembler.reuse(keptInGame) { it.isDirectory }
            assembler.commit()
        } catch (error: Exception) {
            assembler.abandon()
            throw error
        }
    }

    override fun validate(env: ImportEnv): Validation {
        val disc = installedDisc(env.paths.game(gameId))
        return Validation(listOf(Check("PlayStation disc image", disc != null, disc?.extension?.uppercase().orEmpty())),
            "PlayStation", disc != null, if (disc == null) Problem.MISSING_SOURCE_DATA else null, if (disc == null) prompt else null)
    }

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation): LibraryEntry {
        val dir = env.paths.game(gameId)
        return LibraryEntry(gameId, title, listOf("WAR2"), "PlayStation", dir.path, checkNotNull(installedDisc(dir)).name,
            Ps1Activity.RUNTIME, "", Stage.IMPORTED_UNTESTED, env.paths.saves(gameId).path, "")
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    private fun imageExtension(source: SourceNode) = source.name.substringAfterLast('.', "").lowercase()

    private fun java.io.Reader.readNCharsCompat(buffer: CharArray): Int {
        var count = 0
        while (count < buffer.size) {
            val read = read(buffer, count, buffer.size - count)
            if (read < 0) break
            count += read
        }
        return count
    }

    companion object {
        const val DISC_INPUT = "ps1-disc"
        private val cueWhitespace = Regex("""\s+""")
        private val cueLayoutDirectives = setOf("TRACK", "INDEX", "PREGAP", "POSTGAP")
        private val cueFileDirective = Regex("""^FILE(?:\s|$)""", RegexOption.IGNORE_CASE)
        private val cueFile = Regex("""FILE\s+(?:"([^"]+)"|(\S+))\s+BINARY""", RegexOption.IGNORE_CASE)

        private fun installedDisc(dir: File): File? = listOf("iso", "chd", "cue")
            .map { File(dir, "disc.$it") }.firstOrNull(::isCompleteDisc)

        fun isCompleteDisc(file: File): Boolean = file.isFile && runCatching {
            when (file.extension.lowercase()) {
                "iso" -> hasIsoVolume(file)
                "chd" -> file.length() > 124 && RandomAccessFile(file, "r").use { input ->
                    if (input.readLong() != 0x4d436f6d70724844L) return@use false // MComprHD
                    val headerSize = input.readInt()
                    val version = input.readInt()
                    headerSize == 124 && version == 5 && input.length() > headerSize
                }
                "cue" -> {
                    val dir = file.parentFile
                    val tracks = file.useLines { lines ->
                        lines.mapNotNull { cueFile.matchEntire(it)?.groupValues?.get(1) }.toList()
                    }
                    tracks.firstOrNull() == "track-1.bin" && tracks.all { name ->
                        name.matches(Regex("""track-\d+\.bin""")) && File(dir, name).length() >= 2352
                    } && hasIsoVolume(File(dir, "track-1.bin"))
                }
                else -> false
            }
        }.getOrDefault(false)

        private fun hasIsoVolume(file: File): Boolean = RandomAccessFile(file, "r").use { input ->
            // Cooked ISO and raw Mode 1 / Mode 2 images.
            val signature = ByteArray(6)
            listOf(16L * 2048, 16L * 2352 + 16, 16L * 2352 + 24).any { offset ->
                if (input.length() < offset + 88) return@any false
                input.seek(offset)
                input.readFully(signature)
                if (!signature.contentEquals(byteArrayOf(1, 67, 68, 48, 48, 49))) return@any false
                // The boot executable can live near the start of an incomplete copy. Check the
                // disc's declared volume so missing campaign sectors are caught during import.
                input.seek(offset + 80)
                val littleEndian = Integer.reverseBytes(input.readInt())
                val bigEndian = input.readInt()
                val sectorSize = if (offset == 16L * 2048) 2048 else 2352
                littleEndian > 16 && littleEndian == bigEndian && input.length() / sectorSize >= littleEndian
            }
        }
    }
}
