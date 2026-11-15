package com.logie.blizz.porter.port

/**
 * The map a ported character knows: the zones it has explored (the world map's fog lifted) and the flight paths it can
 * take.
 *
 * The decision: a character has been where its level took it. Below level 10 it has only its start (the core's own
 * flight path and nothing explored, as for a new character); from 10 the old world, Eastern Kingdoms and Kalimdor (with
 * the blood elves' and draenei's isles, which the game shows on those maps); from 58 Outland; from 68 Northrend, the
 * levels at which 3.3.5a sends a character there. On those continents every zone is explored and its side's flight
 * paths are known: a veteran of retail has seen all of them, and a black map with no flight paths would leave it
 * walking across a world it knows.
 */
object PortMap {
    enum class Continent { OLD_WORLD, OUTLAND, NORTHREND }

    /** The size of the core's explored-zones field (PLAYER_EXPLORED_ZONES_SIZE) and of its taxi mask (TaxiMaskSize). */
    const val EXPLORED_SIZE = 128
    const val TAXI_SIZE = 14
    private const val DEATH_KNIGHT_MOUNT = 32981

    fun continents(level: Int): Set<Continent> = buildSet {
        if (level >= 10) add(Continent.OLD_WORLD)
        if (level >= 58) add(Continent.OUTLAND)
        if (level >= 68) add(Continent.NORTHREND)
    }

    private fun continentOfMap(map: Int): Continent? = when (map) {
        0, 1 -> Continent.OLD_WORLD
        530 -> Continent.OUTLAND
        571 -> Continent.NORTHREND
        else -> null
    }

    /** Each zone of the world map and the continent the game shows it on (WorldMapArea: its virtual map, else its map). */
    fun zoneContinents(data: RealmData): Map<Int, Continent> {
        val out = HashMap<Int, Continent>()
        for (row in data.worldMapAreas.rows()) {
            val area = row.int(RealmData.MAP_AREA_AREA)
            if (area == 0) continue
            val virtual = row.int(RealmData.MAP_AREA_VIRTUAL)
            continentOfMap(if (virtual >= 0) virtual else row.int(RealmData.MAP_AREA_MAP))?.let { out[area] = it }
        }
        return out
    }

    /** The explored-zones field (characters.exploredZones): every area of those continents' zones. */
    fun exploredZones(data: RealmData, continents: Set<Continent>): List<Int> {
        val field = IntArray(EXPLORED_SIZE)
        if (continents.isEmpty()) return field.toList()
        val zones = zoneContinents(data)
        for (row in data.areas.rows()) {
            val parent = row.int(RealmData.AREA_ZONE)
            val zone = if (parent == 0) row.id else parent
            if (zones[zone] !in continents) continue
            val flag = row.int(RealmData.AREA_EXPLORE_FLAG)
            if (flag <= 0 || flag >= EXPLORED_SIZE * 32) continue
            field[flag / 32] = field[flag / 32] or (1 shl (flag % 32))
        }
        return field.toList()
    }

    /**
     * The flight paths known (characters.taximask): the side's nodes of those continents that the core counts as
     * nodes (DBCStores' sTaxiNodesMask: a node all of whose paths are spells' is not), not the death knights' own.
     */
    fun taxiMask(data: RealmData, side: PortFaction, continents: Set<Continent>): List<Int> {
        val mask = IntArray(TAXI_SIZE)
        if (continents.isEmpty() || side == PortFaction.NEUTRAL) return mask.toList()
        val spellPaths = HashSet<Int>()
        for (row in data.spells.rows()) {
            for (effect in 0..2) {
                if (row.int(SPELL_EFFECT + effect) == RealmData.EFFECT_SEND_TAXI) spellPaths.add(row.int(SPELL_MISC + effect))
            }
        }
        val paths = data.taxiPaths.rows().groupBy { it.int(1) }
        for (node in data.taxiNodes.rows()) {
            val id = node.id
            if (id < 1 || id > TAXI_SIZE * 32) continue
            val from = paths[id]
            if (from != null && from.none { it.int(3) > 0 || it.id !in spellPaths }) continue
            val mount = node.int(if (side == PortFaction.HORDE) RealmData.TAXI_MOUNT_HORDE else RealmData.TAXI_MOUNT_ALLIANCE)
            if (mount == 0 || mount == DEATH_KNIGHT_MOUNT) continue
            val continent = if (id in OLD_WORLD_NODES) Continent.OLD_WORLD else continentOfMap(node.int(RealmData.TAXI_MAP))
            if (continent !in continents) continue
            mask[(id - 1) / 32] = mask[(id - 1) / 32] or (1 shl ((id - 1) % 32))
        }
        return mask.toList()
    }

    /** Silvermoon's, Tranquillien's and the Exodar's nodes: in Outland's map, on the old world's continents (the core's own list). */
    private val OLD_WORLD_NODES = setOf(82, 83, 93, 94)
    private const val SPELL_EFFECT = 71
    private const val SPELL_MISC = 110
}
