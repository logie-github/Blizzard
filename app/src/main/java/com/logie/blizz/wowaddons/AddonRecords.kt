// Ported from the World of Warcraft app (com.logie.warcraft), apart from its package.

package com.logie.blizz.wowaddons

/** An add-on the app installed from warperia.com: which version, and the folders its zip put in `AddOns`. */
data class AddonRecord(
    val slug: String,
    val title: String,
    val version: String?,
    /** The site's "Last updated" day when it was installed, as [Warperia.day] writes it: "2026-10-12". */
    val updated: String?,
    val logo: String?,
    val folders: List<String>,
    val installedAt: Long,
)

/** The records, one line each in a small text file in the app. */
object AddonRecords {
    private const val HEADER = "warperia-addons 1"

    fun parse(text: String): List<AddonRecord> =
        text.lineSequence()
            .filter { it.isNotBlank() && it != HEADER }
            .mapNotNull { line ->
                val f = line.split('\t')
                if (f.size < 7 || f[0].isEmpty()) return@mapNotNull null
                AddonRecord(
                    slug = f[0],
                    title = f[1].ifEmpty { f[0] },
                    version = f[2].ifEmpty { null },
                    updated = f[3].ifEmpty { null },
                    logo = f[4].ifEmpty { null },
                    folders = f[5].split('/').filter { it.isNotEmpty() },
                    installedAt = f[6].toLongOrNull() ?: 0L,
                )
            }
            .toList()

    fun format(records: List<AddonRecord>): String = buildString {
        appendLine(HEADER)
        for (r in records) {
            appendLine(
                listOf(r.slug, r.title, r.version, r.updated, r.logo, r.folders.joinToString("/"), r.installedAt.toString())
                    .joinToString("\t") { clean(it) }
            )
        }
    }

    /** [record] with its install replaced by a newer one, or a new record, the others kept. */
    fun put(records: List<AddonRecord>, record: AddonRecord): List<AddonRecord> =
        records.filterNot { it.slug == record.slug } + record

    /** Whether the site's [version] or its [updated] date is not the installed one's. */
    fun isOutdated(record: AddonRecord, version: String?, updated: String?): Boolean =
        (version != null && record.version != null && version != record.version) ||
            (updated != null && record.updated != null && updated != record.updated)

    /** The folders of [record] no other record has: the ones that go when it goes. */
    fun ownFolders(record: AddonRecord, records: List<AddonRecord>): List<String> {
        val others = records.filter { it.slug != record.slug }.flatMap { it.folders }.map { it.lowercase() }.toSet()
        return record.folders.filter { it.lowercase() !in others }
    }

    private fun clean(value: String?) = value.orEmpty().replace(Regex("[\t\r\n]"), " ")
}
