package com.logie.blizz.porter.port

/** The parts of a port the report speaks of. */
enum class PortArea(val label: String) {
    REALM("Realm"),
    CHARACTER("Character"),
    LEVEL("Level"),
    POSITION("Where"),
    EQUIPMENT("Equipment"),
    BAGS("Bags"),
    SPELLS("Spells"),
    SKILLS("Skills"),
    PROFESSIONS("Professions"),
    MOUNTS("Mounts"),
    REPUTATIONS("Reputations"),
    QUESTS("Quests"),
    ACHIEVEMENTS("Achievements"),
    TITLES("Titles"),
    APPEARANCE("Looks"),
    MAP("Map"),
    ACTION_BARS("Action bars"),
}

/** What became of something of the retail character. */
enum class PortOutcome { KEPT, MAPPED, ADDED, DROPPED, REFUSED, NOTE }

/** One decision: what it is about ([subject]), what became of it, and why. */
data class PortDecision(val area: PortArea, val subject: String, val outcome: PortOutcome, val detail: String) {
    override fun toString() = "${area.label}: $subject: ${outcome.name.lowercase()}${if (detail.isEmpty()) "" else " ($detail)"}"
}

/** The report of a plan: every decision, the equipment slot by slot, and counts of what will be written. */
data class PortReport(val decisions: List<PortDecision>, val equipment: List<SlotChoice>, val counts: Map<String, Int>) {
    fun of(area: PortArea): List<PortDecision> = decisions.filter { it.area == area }

    /** The report as lines of text, for a log or a plain screen. */
    fun lines(): List<String> {
        val out = ArrayList<String>()
        for (area in PortArea.entries) {
            val list = of(area)
            if (area == PortArea.EQUIPMENT) {
                if (equipment.isEmpty() && list.isEmpty()) continue
                out.add("${area.label}:")
                for (d in list) out.add("  ${d.subject}: ${d.detail}")
                for (slot in equipment) {
                    val retail = slot.retail?.let { "${it.name} (${it.itemId})" } ?: "-"
                    val item = slot.item?.let { "${it.name} (${it.entry}, item level ${it.itemLevel})" } ?: "nothing"
                    out.add("  ${slot.slotName}: $retail -> $item [${slot.how.name.lowercase()}] ${slot.why}")
                }
                continue
            }
            if (list.isEmpty()) continue
            out.add("${area.label}:")
            for (d in list) out.add("  ${d.subject}: ${d.outcome.name.lowercase()}${if (d.detail.isEmpty()) "" else " - ${d.detail}"}")
        }
        if (counts.isNotEmpty()) out.add("Written: " + counts.entries.joinToString(", ") { "${it.value} ${it.key}" })
        return out
    }
}

/** An item the port puts on the character or in its bags. */
data class PlannedItem(
    val entry: Int,
    val name: String,
    /** The slot in the character's own inventory (0-18 worn, 19-22 bags, 23-38 the backpack). */
    val slot: Int,
    val count: Int,
    val durability: Int,
    /** The item's spell charges, as item_instance keeps them ("0 0 0 0 0 "). */
    val charges: String,
)

data class PlannedSkill(val skill: Int, val value: Int, val max: Int)

data class PlannedReputation(val faction: Int, val standing: Int, val flags: Int)

data class PlannedAction(val button: Int, val action: Int, val type: Int)

/** Where the character is, and its home (the hearthstone's place). */
data class PlannedPosition(val name: String, val map: Int, val zone: Int, val x: Float, val y: Float, val z: Float, val o: Float)

/**
 * Everything a port will write, worked out from the realm without writing anything: the character's row and every row
 * of its spells, skills, items, reputations, quests, achievements and action bars, with the report of each decision.
 * [refusals] say why it can't be written (a name taken, a race and class the realm hasn't, ...); [ready] when none.
 */
data class PortPlan(
    val realm: PortRealm,
    val accountId: Int,
    val account: String,
    val name: String,
    val race: Int,
    val classId: Int,
    val gender: Int,
    val level: Int,
    val money: Long,
    val appearance: PortAppearance,
    val position: PlannedPosition,
    val playerFlags: Int,
    val atLogin: Int,
    val exploredZones: List<Int>,
    val taxiMask: List<Int>,
    val knownTitles: List<Int>,
    val chosenTitle: Int,
    val ammoId: Int,
    val items: List<PlannedItem>,
    val spells: List<Int>,
    val skills: List<PlannedSkill>,
    val reputations: List<PlannedReputation>,
    val quests: List<Int>,
    val achievements: List<Pair<Int, Long>>,
    val actions: List<PlannedAction>,
    val report: PortReport,
    val refusals: List<String>,
    /** The guid the character would have if nothing else is written before [Porter.apply] (it takes the next free one then). */
    val estimatedGuid: Int,
) {
    val ready: Boolean get() = refusals.isEmpty()
}

/** What [Porter.apply] wrote: the character's guid, and its items' first and last guids. */
data class PortResult(val guid: Int, val firstItemGuid: Int, val lastItemGuid: Int, val name: String)
