package com.logie.blizz.importer

import java.io.File

/**
 * World of Warcraft, from the World of Warcraft app's export (see [WowExport]): its client, realms
 * (databases with their characters), add-ons, modules and settings, copied over with every file
 * checked against the export's SHA-256 list. Nothing is rebuilt: the files are the ones the other
 * app had. A copy, never a move: the original stays where it was.
 *
 * The big copy can be stopped and carried on: files already copied and checked are listed in a
 * journal beside the half-made copy, which isn't thrown away when an import fails or is cancelled
 * (Reset removes it). The finished copy is moved into place whole.
 *
 * Playing: the realms still run in the World of Warcraft app (the entry's runtime is
 * [LibraryEntry.RUNTIME_EXTERNAL]); porting their runtime is the next step, and the copy keeps the
 * export's manifest (which paths the data was made under) for it.
 */
class WowImporter : GameImporter {
    override val gameId = "wow"
    override val title = "World of Warcraft"

    companion object {
        const val PROMPT = "Pick the WoW-export folder the World of Warcraft app made (its button: Export everything to Blizzard), or the folder that holds it."
        const val EXPORT_COPY = ".export"
        val isExportRoot: (Set<String>) -> Boolean = { WowExport.MANIFEST in it && "files/" in it && WowExport.CHECKSUMS in it }
        private const val JOURNAL = ".journal"
        /** The files the export lists that weren't found and were left out (one path a line), in `.export/`. */
        const val MISSING = "missing.txt"

        /** What can't be left out: the databases, the client and the server programs. */
        fun isCritical(path: String) = path.startsWith("mysql/") || path.startsWith("client/") || path.startsWith("server/bin/") || path.startsWith("server/lib/") || path == "server/ctl.sh"
    }

    private fun work(env: ImportEnv) = File(env.paths.staging, "$gameId-work")

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for the World of Warcraft export"))
        val found = LinkedHashMap<String, SourceNode>()
        env.searchRoots().firstNotNullOfOrNull { Packages.findRoot(it, 5, isExportRoot) }?.let { found["install"] = it }
        return Detection(validateDir(env.paths.game(gameId)).filesOk, found)
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()
    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val have = File(env.paths.game(gameId), EXPORT_COPY).isDirectory || detection.found["install"] != null || supplied["install"] is Supplied.Picked
        return if (have) emptyList() else listOf(MissingInput("install", PROMPT, PickKind.FOLDER))
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val source = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
            ?: throw ImportException(Problem.MISSING_SOURCE_DATA, PROMPT)
        val root = if (isExportRoot(Packages.names(source.children()))) source
        else Packages.findRoot(source, 5, isExportRoot) ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no finished export in that folder (export.json, checksums.tsv and files/). $PROMPT")
        val manifest = WowExport.parseManifest(root.child(WowExport.MANIFEST)!!.open().use { it.readBytes().toString(Charsets.UTF_8) })
        val allEntries = WowExport.parseChecksums(root.child(WowExport.CHECKSUMS)!!.open().use { it.readBytes().toString(Charsets.UTF_8) })
        if (allEntries.isEmpty()) throw ImportException(Problem.MISSING_SOURCE_DATA, "The export lists no files.")
        allEntries.forEach { WowExport.safePath(it.path) }
        var entries = allEntries

        env.progress(Progress(Stage.EXTRACTING, "Reading the export's folders"))
        val nodes = HashMap<String, SourceNode>()
        fun walk(node: SourceNode, prefix: String) {
            for (child in node.children()) {
                env.cancel.check()
                if (child.isDirectory) walk(child, "$prefix${child.name}/") else nodes[prefix + child.name] = child
            }
        }
        walk(root.child("files") ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "The export has no files/ folder."), "")
        // Where each file is: the stored name the export's manifest gives, else its own, else (an export made before
        // names that differ only in case were kept apart) the likely spots for the twin ("name (1).ext", another case).
        val byLower = HashMap<String, SourceNode>().also { m -> nodes.forEach { (p, n) -> m.putIfAbsent(p.lowercase(), n) } }
        val located = HashMap<String, SourceNode>()
        for (e in entries) {
            val stored = manifest.renames[e.path] ?: e.path
            val own = nodes[stored]
            if (own != null) { located[e.path] = own; continue }
            if (e.path in manifest.renames) continue
            // An export from before the renames: the file that holds this entry's bytes, by checksum, among where it may be.
            WowExport.candidates(e.path, byLower).firstOrNull { c -> runCatching { c.open().use { WowExport.sha256(it) } }.getOrNull() == e.sha256 }
                ?.let { located[e.path] = it }
        }
        // Then by content: what's still missing is looked for by its size and SHA-256 among every file in the folder that
        // was picked, whatever it's called and wherever it is (a copy renamed by the storage, put in the wrong folder...).
        var searched = 0
        val stillMissing = entries.filter { it.path !in located }
        if (stillMissing.isNotEmpty()) {
            env.progress(Progress(Stage.EXTRACTING, "Looking for ${stillMissing.size} missing files by size and checksum"))
            val bySize = HashMap<Long, MutableList<SourceNode>>()
            val used = located.values.map { it.display }.toHashSet()
            fun index(node: SourceNode, depth: Int) {
                if (depth > 12 || searched > 400_000) return
                for (child in node.children()) {
                    env.cancel.check()
                    if (child.isDirectory) index(child, depth + 1)
                    else { searched++; if (child.display !in used) bySize.getOrPut(child.size) { ArrayList() }.add(child) }
                }
            }
            // The folder that was picked, then every folder the person added with Search a folder.
            for (start in listOf(source) + env.searchRoots()) runCatching { index(start, 0) }.onFailure { if (it is ImportException) throw it }
            for (e in stillMissing) {
                if (e.size < 1) continue
                val found = bySize[e.size].orEmpty().take(60).firstOrNull { c -> runCatching { c.open().use { WowExport.sha256(it) } }.getOrNull() == e.sha256 } ?: continue
                located[e.path] = found
                used += found.display
            }
        }
        // What can't be found anywhere. Data the realm and client rebuild or can do without is left out with a note
        // (the person's own words: "those should be fine to leave out"); the databases, the client and the server
        // programs are never skipped: without them it isn't their game.
        val missing = entries.filter { it.path !in located }
        val critical = missing.filter { isCritical(it.path) }
        if (critical.isNotEmpty()) {
            throw ImportException(
                Problem.MISSING_SOURCE_DATA,
                "${critical.size} files the game can't do without aren't in the folder (the first: ${critical.first().path}). They weren't found by name, by their other likely names, or by content (size and checksum, among $searched files; Search a folder with a bigger folder to look further). Update the World of Warcraft app (an export made before its fix loses files whose names differ only in capital letters from another's), run Export everything to Blizzard again (it only copies what changed), then import again.",
                critical.take(20).joinToString("\n") { it.path },
            )
        }
        val skipped = missing
        entries = entries.filter { it.path in located }

        val work = work(env).also { it.mkdirs() }
        val files = File(work, "files").also { it.mkdirs() }
        val journal = File(work, JOURNAL)
        val done = HashSet<String>()
        if (journal.isFile) journal.forEachLine { line -> line.split('\t', limit = 3).takeIf { it.size == 3 }?.let { done += line } }
        val total = entries.sumOf { it.size }
        var copied = 0L
        fun alreadyDone(e: WowExport.Entry): Boolean = "${e.sha256}\t${e.size}\t${e.path}" in done && File(files, e.path).let { it.isFile && it.length() == e.size }
        val remaining = entries.filter { !alreadyDone(it) }
        copied = total - remaining.sumOf { it.size }
        FileValidator.requireSpace(env.paths.games, remaining.sumOf { it.size })

        journal.parentFile?.mkdirs()
        journal.appendText("")
        val out = java.io.FileWriter(journal, true)
        try {
            for (e in remaining) {
                env.cancel.check()
                env.progress(Progress(Stage.EXTRACTING, "Copying ${e.path.substringAfterLast('/')} (${e.path.substringBefore('/')})", copied, total))
                val target = File(files, e.path)
                target.parentFile?.mkdirs()
                val temp = File(target.parentFile, ".${target.name}.part")
                val (sha, bytes) = located.getValue(e.path).open().use { input ->
                    temp.outputStream().buffered(1 shl 20).use { o -> WowExport.copyHashed(input, o, env.cancel) { n -> copied += n; } }
                }
                if (bytes != e.size || sha != e.sha256) {
                    temp.delete()
                    throw ImportException(
                        Problem.CORRUPT_ARCHIVE,
                        "${e.path} doesn't match the export (it was ${if (bytes != e.size) "$bytes bytes, not ${e.size}" else "changed"}). Run the export again, or use Verify in the World of Warcraft app.",
                        "expected ${e.sha256}, got $sha",
                    )
                }
                target.delete()
                if (!temp.renameTo(target)) throw ImportException(Problem.PERMISSION_DENIED, "${e.path} couldn't be put in place.")
                out.write("${e.sha256}\t${e.size}\t${e.path}\n"); out.flush()
            }
        } finally {
            out.close()
        }

        // The export's own manifest, checksums and settings, kept for what comes next.
        val keep = File(work, EXPORT_COPY).also { it.mkdirs() }
        if (skipped.isNotEmpty()) File(keep, MISSING).writeText(skipped.joinToString("\n", postfix = "\n") { it.path })
        for (name in listOf(WowExport.MANIFEST, WowExport.CHECKSUMS)) root.child(name)?.let { copyInto(it, keep, name, env.cancel) }
        root.child("prefs")?.children()?.filter { !it.isDirectory }?.forEach { copyInto(it, File(keep, "prefs").also { d -> d.mkdirs() }, it.name, env.cancel) }
        File(work, "MANIFEST-FORMAT").writeText("${manifest.format}\n")

        env.progress(Progress(Stage.VALIDATING, "Checking the copy"))
        val check = validateDir(work)
        if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "The copy didn't check out.")

        // Whole: the finished copy becomes the installation.
        journal.delete()
        val asm = Assembler(env.paths, gameId)
        asm.staging.deleteRecursively()
        asm.staging.parentFile?.mkdirs()
        if (!work.renameTo(asm.staging)) throw ImportException(Problem.PERMISSION_DENIED, "The copy couldn't be put in place.")
        asm.commit()
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val keep = File(dir, EXPORT_COPY)
        val manifestFile = File(keep, WowExport.MANIFEST)
        val manifest = runCatching { WowExport.parseManifest(manifestFile.readText()) }.getOrNull()
        val entries = runCatching { WowExport.parseChecksums(File(keep, WowExport.CHECKSUMS).readText()) }.getOrNull()
        val files = File(dir, "files")
        val checks = ArrayList<Check>()
        checks += Check("Export manifest", manifest != null, manifest?.let { "made by the World of Warcraft app ${it.appVersion} on ${it.createdAt}" } ?: "missing")
        val left = runCatching { File(keep, MISSING).readLines().filter { it.isNotBlank() }.toSet() }.getOrDefault(emptySet())
        val missing = entries?.filter { e -> e.path !in left }?.filter { e -> File(files, e.path).let { !it.isFile || it.length() != e.size } }?.size
        checks += Check("Every file present at its size", entries != null && missing == 0,
            if (entries == null) "no checksums" else if (missing == 0) "${entries.size - left.size} files" + (if (left.isNotEmpty()) ", ${left.size} left out (.export/$MISSING)" else "") else "$missing missing or the wrong size")
        val folders = manifest?.folders.orEmpty()
        // (a folder all of whose files were left out isn't expected)
        val absent = folders.filter { f -> !File(files, f).isDirectory && entries.orEmpty().any { it.path.startsWith("$f/") && it.path !in left } }
        checks += Check("Folders (${folders.joinToString().ifEmpty { "none" }})", manifest != null && absent.isEmpty() && folders.isNotEmpty(), if (absent.isEmpty()) "present" else "missing ${absent.joinToString()}")
        val ok = checks.all { it.passed }
        val problem = if (ok) null else Problem.MISSING_SOURCE_DATA
        return Validation(checks, manifest?.let { "World of Warcraft app ${it.appVersion} export (${it.files} files)" }, ok, problem, if (ok) null else PROMPT)
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = title,
        products = listOf("WOW"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = "$EXPORT_COPY/${WowExport.MANIFEST}",
        runtime = LibraryEntry.RUNTIME_EXTERNAL,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = null,
        controlProfile = "",
    )
}
