package com.logie.blizz.forevernew

import java.io.File

/**
 * Maps, vmaps and mmaps from the user's own client, with Karrz's four tools in upstream's order (tools/extract_client_data.sh):
 *   mapextractor -i CLIENT -o OUT -e 15 -f 1 -l enUS   (dbc, maps, gt)
 *   vmap4extractor -d CLIENT                            (Buildings/, in the working folder)
 *   vmap4assembler Buildings vmaps
 *   mmaps_generator --input OUT --output OUT
 * Each stage is checkpointed (a marker file when its output verified) so an interrupted run continues at the stage it was in.
 * The tools read the client and write only [ForeverLayout.data]; the client folder is never written to.
 *
 * Disk: upstream says about 45 GB of temporary space on a desktop with about 2 GB left after (Buildings is intermediate and is
 * deleted after the assembler). That figure is not a promise for a phone: [spaceNeeded] is checked before the first stage and
 * the run is refused with the numbers when the phone has less; streaming or bounded-temp extraction is NOT implemented.
 * Bots are never turned on as ready without mmaps ([ForeverLayout.hasMaps]).
 */
object ForeverMaps {
    enum class Stage(val key: String, val label: String, val output: String) {
        MAPS("maps", "Extracting maps and data tables", "maps"),
        VMAP_EXTRACT("vmap-extract", "Extracting building models", "Buildings"),
        VMAP_ASSEMBLE("vmap-assemble", "Assembling vmaps", "vmaps"),
        MMAPS("mmaps", "Generating navigation meshes (mmaps)", "mmaps"),
    }

    /** Upstream's numbers: temporary space at the peak and what stays. */
    const val PEAK_BYTES = 45L shl 30
    const val KEPT_BYTES = 2L shl 30

    fun spaceNeeded(): Long = PEAK_BYTES

    /** An error text when [free] is below what the peak needs, else null. */
    fun checkSpace(free: Long): String? =
        if (free in 1 until spaceNeeded()) "Extracting Forever's map data needs about ${spaceNeeded() shr 30} GB free at its peak (about ${KEPT_BYTES shr 30} GB stay); ${free shr 30} GB are free. Free some space and try again." else null

    data class Step(val stage: Stage, val argv: List<String>)

    /** The commands, run with [ForeverLayout.data] as the working folder, each through the musl loader (the caller prefixes it). */
    fun plan(layout: ForeverLayout, clientRoot: File, threads: Int): List<Step> {
        val out = layout.data.path
        val t = if (threads > 0) listOf("--threads", threads.toString()) else emptyList()
        fun tool(name: String) = File(layout.bin, name).path
        return listOf(
            Step(Stage.MAPS, listOf(tool("mapextractor"), "-i", clientRoot.path, "-o", out, "-e", "15", "-f", "1", "-l", "enUS")),
            Step(Stage.VMAP_EXTRACT, listOf(tool("vmap4extractor"), "-d", clientRoot.path) + t),
            Step(Stage.VMAP_ASSEMBLE, listOf(tool("vmap4assembler"), "Buildings", "vmaps") + t),
            Step(Stage.MMAPS, listOf(tool("mmaps_generator"), "--input", out, "--output", out) + t),
        )
    }

    private fun marker(layout: ForeverLayout, stage: Stage) = File(layout.checkpoints, "maps-${stage.key}.done")

    fun isDone(layout: ForeverLayout, stage: Stage) = marker(layout, stage).isFile

    /** Marks a stage done only if its output has files; the next run skips it. A stage with no output is reported, not trusted. */
    fun complete(layout: ForeverLayout, stage: Stage): String? {
        val out = File(layout.data, stage.output)
        if (out.list().isNullOrEmpty()) return "${stage.label} left nothing in ${stage.output}."
        if (stage == Stage.MAPS && File(layout.data, "dbc").list().isNullOrEmpty()) return "The data tables (dbc) were not made."
        if (stage == Stage.VMAP_ASSEMBLE && !(File(layout.data, "vmaps").walkTopDown().any { it.name.endsWith(".vmtree") })) return "No vmap tree was made."
        marker(layout, stage).also { it.parentFile?.mkdirs() }.writeText(System.currentTimeMillis().toString())
        return null
    }

    /** Intermediate files upstream says can be deleted once the assembler has run. */
    fun cleanup(layout: ForeverLayout) {
        File(layout.data, "Buildings").deleteRecursively(); File(layout.data, "dir_bin").deleteRecursively()
    }

    /** A new client build or a repair: the stages run again. */
    fun reset(layout: ForeverLayout) { Stage.entries.forEach { marker(layout, it).delete() } }

    fun remaining(layout: ForeverLayout): List<Stage> = Stage.entries.filter { !isDone(layout, it) }
}
