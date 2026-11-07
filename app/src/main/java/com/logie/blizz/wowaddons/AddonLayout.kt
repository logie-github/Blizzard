// Ported from the World of Warcraft app (com.logie.warcraft), apart from its package.

package com.logie.blizz.wowaddons

/**
 * Where the files of an add-on zip go in the client's `Interface/AddOns`. The game loads an
 * add-on from `AddOns/<Name>/<Name>.toc`, and zips come packed every way: the add-on's folder at
 * the top, several add-ons side by side, the folder inside `Interface/AddOns/`, a download's own
 * folder around it (`Name-1.2.3/`), or the add-on's files with no folder at all. Each `.toc` that
 * isn't inside another add-on's folder (a library's) marks an add-on; its folder takes the
 * `.toc`'s name, which the game needs.
 */
object AddonLayout {
    /** The add-ons in a zip ([folders], in order) and each entry's path under `AddOns` ([targets]). */
    data class Plan(val folders: List<String>, val targets: Map<String, String>)

    /** Version suffixes some add-ons ship extra `.toc`s with, for other versions of the game. */
    private val FLAVOUR = Regex("[-_](Classic|BCC|TBC|Wrath|WOTLKC|Vanilla|Mainline|Cata|Mists)$", RegexOption.IGNORE_CASE)

    fun plan(entries: List<String>): Plan {
        val files = entries.map { it.replace('\\', '/').trimStart('/') }
            .filter { it.isNotEmpty() && !it.endsWith("/") && !it.startsWith("__MACOSX/") && isSafe(it) }
        // Each folder with a .toc: the .toc that names the add-on.
        val tocs = files.filter { it.endsWith(".toc", ignoreCase = true) }
            .groupBy { it.substringBeforeLast('/', "") }
        val roots = tocs.mapValues { (dir, inDir) -> addonName(dir, inDir.map { it.substringAfterLast('/').dropLast(4) }) }
            .entries.sortedBy { it.key.count { c -> c == '/' } + if (it.key.isEmpty()) -1 else 0 }
        val chosen = mutableListOf<Pair<String, String>>()
        for ((dir, name) in roots) {
            if (chosen.any { (root, _) -> root.isEmpty() || dir.startsWith("$root/") }) continue
            if (chosen.any { (_, other) -> other.equals(name, ignoreCase = true) }) continue
            chosen += dir to name
        }
        val targets = LinkedHashMap<String, String>()
        for (file in files) {
            val (root, name) = chosen.firstOrNull { (root, _) -> root.isEmpty() || file.startsWith("$root/") } ?: continue
            val inside = if (root.isEmpty()) file else file.removePrefix("$root/")
            targets[file] = "$name/$inside"
        }
        return Plan(chosen.map { it.second }, targets)
    }

    /**
     * The add-on's name for a folder and the names of its `.toc`s: the folder's own name when one
     * matches it, else the `.toc` without a version suffix, else the shortest.
     */
    private fun addonName(dir: String, tocNames: List<String>): String {
        val folder = dir.substringAfterLast('/')
        tocNames.firstOrNull { it.equals(folder, ignoreCase = true) }?.let { return it }
        val plain = tocNames.filterNot { FLAVOUR.containsMatchIn(it) }
        return (plain.ifEmpty { tocNames }).minBy { it.length }
    }

    private fun isSafe(path: String) = path.split('/').none { it == ".." || it == "." }

    /** A `.toc`'s `## Key: value` lines (Title, Version, Interface, Notes...), with WoW's colour codes taken out of the values. */
    fun tocFields(text: String): Map<String, String> =
        text.lineSequence()
            .mapNotNull { Regex("""^##\s*([^:]+):\s*(.*)$""").find(it.trim()) }
            .associate { it.groupValues[1].trim() to plainText(it.groupValues[2].trim()) }

    /** WoW's text with its colour codes (`|cAARRGGBB` ... `|r`) taken out. */
    fun plainText(text: String): String = text.replace(Regex("""\|c[0-9A-Fa-f]{8}"""), "").replace("|r", "")

    /** The game's add-on version for 3.3.5a: add-ons for another one load only when the game doesn't check. */
    const val INTERFACE = "30300"
}
