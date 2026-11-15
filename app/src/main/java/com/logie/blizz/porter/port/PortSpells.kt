package com.logie.blizz.porter.port

/** Why a ported character knows a spell. */
enum class SpellSource(val label: String) {
    CLASS_TRAINER("class trainer"),
    QUEST("class quest"),
    WEAPON_MASTER("weapon master"),
    RIDING("riding trainer"),
    PROFESSION("profession"),
    MOUNT("mount"),
}

/** A skill's value and its highest value now. */
data class SkillValue(val value: Int, val max: Int)

/**
 * The spells and skills of a ported character, given the way the realm's own trainers and the core give them: its
 * race's and class's skills (playercreateinfo_skills, as Player::LearnDefaultSkills), what its class trainers, weapon
 * masters and riding trainers teach up to its level (their tables, by Trainer::GetSpellState's rules), the class spells
 * the game teaches by quests, its professions and its mounts.
 *
 * Learning a spell does to the skills what the core's Player::_addSpell does (a profession's rank sets its skill, a
 * weapon or armour proficiency gives its skill). Spells the core gives from skills at every login
 * (Player::learnSkillRewardedSpells) and the realm's custom spells (playercreateinfo_spell_custom) are known but not
 * written: [written].
 *
 * Skills kept by level (weapons, defence) are at the level's maximum: a veteran's are.
 */
class SpellBook(private val data: RealmData, private val world: RealmWorld, val race: Int, val classId: Int, val level: Int) {
    val learned = LinkedHashMap<Int, SpellSource>()
    val skills = LinkedHashMap<Int, SkillValue>()
    private var skillSpellCache: Set<Int>? = null
    private val raceBit = RealmData.raceBit(race)
    private val classBit = RealmData.classBit(classId)

    /** The realm's spells given at every login to this race and class. */
    val customSpells: Set<Int> = world.createSpells.filter { matches(it.raceMask, it.classMask) && data.spellExists(it.spell) }.map { it.spell }.toSet()

    private fun matches(raceMask: Int, classMask: Int) = (raceMask == 0 || raceMask and raceBit != 0) && (classMask == 0 || classMask and classBit != 0)

    /** The spells its skills give (never written). */
    fun skillSpells(): Set<Int> = skillSpellCache ?: data.spellsOfSkills(skills.mapValues { it.value.value }, race, classId).also { skillSpellCache = it }

    fun knows(spell: Int): Boolean = spell in learned || spell in skillSpells() || spell in customSpells

    fun skillValue(skill: Int): Int = skills[skill]?.value ?: 0

    fun hasSkill(skill: Int): Boolean = skillValue(skill) > 0

    /** The spells to write: what was learned, but those the skills or the realm give by themselves, and those the core would delete. */
    fun written(): List<Int> {
        val given = skillSpells() + customSpells
        return learned.keys.filter { it !in given && data.spellExists(it) && data.spellKeptAtLogin(it, race, classId) }.sorted()
    }

    fun setSkill(skill: Int, value: Int, max: Int) {
        skills[skill] = SkillValue(value, max)
        skillSpellCache = null
    }

    /**
     * What the skills' own spells do to the skills as the core adds them at login (Player::_addSpell for each spell of
     * learnSkillRewardedSpells): a death knight's riding gives it Journeyman Riding by its skill, and that raises the
     * skill to 150, which the next riding lesson asks for.
     */
    fun applySkillSpellSteps() {
        repeat(6) {
            var changed = false
            for (spell in skillSpells()) {
                val (skill, rank) = data.skillStep(spell) ?: continue
                val max = rank * 75
                val current = skills[skill]
                val value = if (skill == SKILL_RIDING) max else maxOf(current?.value ?: 0, 1)
                if (current != null && current.max >= max && current.value >= value) continue
                if (data.skillInfo(skill, race, classId) == null) continue
                setSkill(skill, maxOf(current?.value ?: 0, value), maxOf(current?.max ?: 0, max))
                changed = true
            }
            if (!changed) return
        }
    }

    /** Player::LearnDefaultSkill, with skills kept by level at the level's maximum. */
    fun learnDefaultSkill(skill: Int, rank: Int) {
        val info = data.skillInfo(skill, race, classId) ?: return
        val levelMax = level * 5
        when (data.skillRange(info)) {
            SkillRange.LANGUAGE -> setSkill(skill, 300, 300)
            SkillRange.LEVEL -> setSkill(skill, levelMax, levelMax)
            SkillRange.MONO -> setSkill(skill, 1, 1)
            SkillRange.RANK -> {
                if (rank == 0) return
                val max = data.tierValue(info.tier, rank)
                if (max == 0) return
                val value = when {
                    info.flags and RealmData.SKILL_FLAG_ALWAYS_MAX != 0 -> max
                    classId == PortTargets.DEATH_KNIGHT -> minOf(maxOf(1, (level - 1) * 5), max)
                    else -> 1
                }
                setSkill(skill, value, max)
            }
            SkillRange.NONE -> Unit
        }
    }

    /** The race's and class's own skills (Player::LearnDefaultSkills). */
    fun learnDefaults() {
        for (row in world.createSkills) {
            if (!matches(row.raceMask, row.classMask) || hasSkill(row.skill)) continue
            learnDefaultSkill(row.skill, row.rank)
        }
    }

    /** Learns [spell], with what it does to the skills (Player::_addSpell). */
    fun learn(spell: Int, source: SpellSource) {
        if (spell in learned) return
        learned[spell] = source
        val step = data.skillStep(spell)
        if (step != null) {
            val (skill, rank) = step
            val max = rank * 75
            val current = skills[skill]
            val value = if (skill == SKILL_RIDING) max else maxOf(current?.value ?: 0, 1)
            if (data.skillInfo(skill, race, classId) != null) setSkill(skill, maxOf(current?.value ?: 0, value), maxOf(current?.max ?: 0, max))
            return
        }
        for (ability in data.abilitiesOf(spell)) {
            val special = (ability.skill == SKILL_LOCKPICKING || ability.skill == RealmData.SKILL_RUNEFORGING) && ability.trivialHigh == 0
            if ((ability.acquire == RealmData.ACQUIRE_ON_LEARN && !hasSkill(ability.skill)) || (special && !hasSkill(ability.skill))) {
                learnDefaultSkill(ability.skill, 0)
            }
        }
    }

    /** Whether a trainer would teach [spell] now (Trainer::GetDefaultSpellState is Available), and it suits this race and class. */
    fun canTeach(spell: TrainerSpell): Boolean {
        if (spell.reqLevel > level || knows(spell.spell) || !data.spellExists(spell.spell)) return false
        if (!data.spellFits(spell.spell, race, classId)) return false
        if (spell.reqSkill != 0 && skillValue(spell.reqSkill) < spell.reqSkillRank) return false
        if (spell.reqAbilities.any { !knows(it) }) return false
        val lessons = data.effects(spell.spell).filter { it.effect == RealmData.EFFECT_LEARN_SPELL && it.trigger > 0 }
        if (lessons.isNotEmpty()) {
            if (lessons.all { knows(it.trigger) }) return false
            for (lesson in lessons) {
                val previous = world.previousRank(lesson.trigger)
                if (previous != 0 && !knows(previous)) return false
                // (a lesson for the other side's race, the Horde's warhorse for an Alliance paladin, isn't this character's)
                if (!data.spellExists(lesson.trigger) || !data.spellFits(lesson.trigger, race, classId)) return false
            }
        } else {
            val previous = world.previousRank(spell.spell)
            if (previous != 0 && !knows(previous)) return false
        }
        if (world.required[spell.spell].orEmpty().any { !knows(it) }) return false
        return true
    }

    /** A trainer's lesson as it is cast (Trainer::TeachSpell): what it teaches, and the skill steps it gives. */
    fun teach(spell: TrainerSpell, source: SpellSource) {
        val effects = data.effects(spell.spell)
        val lessons = effects.filter { it.effect == RealmData.EFFECT_LEARN_SPELL && it.trigger > 0 }
        if (lessons.isEmpty()) {
            learn(spell.spell, source)
            return
        }
        for (lesson in lessons) learn(lesson.trigger, source)
        for (step in effects.filter { it.effect == RealmData.EFFECT_SKILL_STEP && it.misc > 0 }) {
            val skill = step.misc
            if (data.skillInfo(skill, race, classId) == null) continue
            val max = (step.base + 1) * 75
            val current = skills[skill]
            val value = if (skill == SKILL_RIDING) max else maxOf(current?.value ?: 0, 1)
            setSkill(skill, maxOf(current?.value ?: 0, value), maxOf(current?.max ?: 0, max))
        }
    }

    /** Teaches every spell of [spells] a trainer would, again and again until nothing more can be learned (a rank opens the next). */
    fun teachAll(spells: List<TrainerSpell>, source: SpellSource): Int {
        var count = 0
        repeat(40) {
            applySkillSpellSteps()
            var changed = false
            for (spell in spells) {
                if (!canTeach(spell)) continue
                teach(spell, source)
                count++
                changed = true
            }
            if (!changed) return count
        }
        return count
    }

    /** The class's trainers, its quest spells, its weapon masters and the riding trainers, up to its level. */
    fun learnClass(): Map<SpellSource, Int> {
        learnDefaults()
        val counts = LinkedHashMap<SpellSource, Int>()
        val classTrainers = world.trainerSpells.filter { it.type == TRAINER_CLASS && it.requirement == classId }
        val weaponMasters = world.trainerSpells.filter { it.type == TRAINER_TRADESKILL && isProficiency(it.spell) }
        val riding = world.trainerSpells.filter { it.type == TRAINER_MOUNT && (it.requirement == 0 || it.requirement == race) }
        // Quest spells first: trainers' next ranks ask for them (Sunder Armor's).
        var quest = 0
        for ((spell, at) in QUEST_SPELLS[classId].orEmpty()) {
            if (at > level || knows(spell) || !data.spellExists(spell) || !data.spellFits(spell, race, classId)) continue
            learn(spell, SpellSource.QUEST)
            quest++
        }
        repeat(4) {
            counts[SpellSource.CLASS_TRAINER] = (counts[SpellSource.CLASS_TRAINER] ?: 0) + teachAll(classTrainers, SpellSource.CLASS_TRAINER)
            counts[SpellSource.WEAPON_MASTER] = (counts[SpellSource.WEAPON_MASTER] ?: 0) + teachAll(weaponMasters, SpellSource.WEAPON_MASTER)
            counts[SpellSource.RIDING] = (counts[SpellSource.RIDING] ?: 0) + teachAll(riding, SpellSource.RIDING)
        }
        counts[SpellSource.QUEST] = quest
        return counts
    }

    /** A spell that gives a weapon skill as it is learned (a weapon master's lesson). */
    private fun isProficiency(spell: Int): Boolean =
        data.abilitiesOf(spell).any { it.acquire == RealmData.ACQUIRE_ON_LEARN && data.skillCategory(it.skill) == RealmData.CATEGORY_WEAPON }

    // ---- professions

    /** What happened to one retail profession. */
    data class ProfessionOutcome(val profession: PortProfession, val skill: Int, val value: Int, val max: Int, val recipes: Int, val primary: Boolean, val problem: String?)

    /**
     * A retail profession as this realm has it: the points of its Classic, Outland and Northrend parts together (3.3.5a's
     * whole range), cut to the highest rank a trainer would teach at the character's level; the rank spells up to there
     * and every recipe its trainers teach up to its value. [primaries] is how many primary professions it has already.
     */
    fun learnProfession(profession: PortProfession, primaries: Int): ProfessionOutcome {
        val skill = profession.skillLineId
        fun refuse(why: String) = ProfessionOutcome(profession, skill, 0, 0, 0, false, why)
        val category = data.skillCategory(skill)
        val primary = category == RealmData.CATEGORY_PROFESSION
        if (!primary && skill !in SECONDARY_PROFESSIONS) return refuse("this game has no such profession")
        if (data.skillInfo(skill, race, classId) == null) return refuse("this race and class can't learn it on this realm")
        val points = professionPoints(profession)
        if (points <= 0) return refuse("nothing learned in its Classic, Outland or Northrend parts")
        if (primary && primaries >= MAX_PRIMARY_PROFESSIONS) return refuse("a character has two primary professions at most")

        // Its ranks: the trainers' lessons whose spell sets the skill (Apprentice 75 ... Grand Master 450).
        val ranks = HashMap<Int, MutableList<TrainerSpell>>()
        for (spell in world.trainerSpells.filter { it.type == TRAINER_TRADESKILL }) {
            for (taught in data.taught(spell.spell)) {
                val step = data.skillStep(taught) ?: continue
                if (step.first == skill) ranks.getOrPut(step.second) { ArrayList() }.add(spell)
            }
        }
        var reachable = 0
        while (ranks[reachable + 1]?.any { it.reqLevel <= level } == true) reachable++
        if (reachable == 0) return refuse(if (ranks.isEmpty()) "no trainer of this realm teaches it" else "too low a level for its first rank")
        val wanted = (minOf(points, 450) + 74) / 75
        val step = minOf(wanted, reachable)
        val value = minOf(points, step * 75)
        for (rank in 1..step) {
            val lesson = ranks.getValue(rank).filter { it.reqLevel <= level }.minByOrNull { it.reqLevel } ?: continue
            teach(lesson, SpellSource.PROFESSION)
        }
        setSkill(skill, value, step * 75)
        val rankSpells = ranks.values.flatten().map { it.spell }.toSet()
        val recipes = world.trainerSpells.filter { it.type == TRAINER_TRADESKILL && it.reqSkill == skill && it.spell !in rankSpells && it.reqSkillRank <= value }
        val taught = teachAll(recipes, SpellSource.PROFESSION)
        return ProfessionOutcome(profession, skill, value, step * 75, taught, primary, null)
    }

    // ---- mounts

    /** What happened to one retail mount: the spell it became, or why none. */
    data class MountOutcome(val mount: PortMount?, val spell: Int?, val detail: String)

    private val mountsByName: Map<String, List<Int>> by lazy {
        data.abilitiesIn(SKILL_MOUNTS).map { it.spell }.distinct().filter { data.spellExists(it) }
            .groupBy { normalize(data.spells[it]!!.string(SPELL_NAME_FIELD)) }
            .mapValues { (_, spells) -> spells.sortedDescending() }
    }

    private fun isMountSpell(spell: Int) = data.abilitiesOf(spell).any { it.skill == SKILL_MOUNTS }

    /**
     * The retail mounts this game has (by the spell when it was given, else by name among the realm's mount spells),
     * for this race and class; and the race's own riding animals, and a flying one, when none of those fits its level.
     */
    fun learnMounts(mounts: List<PortMount>, side: PortFaction): List<MountOutcome> {
        val out = ArrayList<MountOutcome>()
        for (mount in mounts) {
            val candidates = (listOfNotNull(mount.spellId?.takeIf { isMountSpell(it) }) + mountsByName[normalize(mount.name)].orEmpty()).distinct()
            val spell = candidates.firstOrNull { data.spellFits(it, race, classId) }
            if (spell == null) {
                out.add(MountOutcome(mount, null, if (candidates.isEmpty()) "this game has no such mount" else "not for this race or class"))
                continue
            }
            learn(spell, SpellSource.MOUNT)
            out.add(MountOutcome(mount, spell, data.spellName(spell)))
        }
        val known = learned.filterValues { it == SpellSource.MOUNT }.keys + learned.keys.filter(::isMountSpell)
        val flying = known.any { data.isFlyingMount(it) }
        val ground = known.any { data.isGroundMount(it) }
        val standard = ArrayList<Int>()
        if (!ground) {
            val (basic, swift) = GROUND_MOUNTS[kinRace(side)] ?: GROUND_MOUNTS.getValue(if (side == PortFaction.HORDE) 2 else 1)
            if (level >= RIDING_APPRENTICE_LEVEL) standard.add(basic)
            if (level >= RIDING_JOURNEYMAN_LEVEL) standard.add(swift)
        }
        if (!flying) {
            val (basic, swift) = if (side == PortFaction.HORDE) FLYING_HORDE else FLYING_ALLIANCE
            if (level >= RIDING_EXPERT_LEVEL) standard.add(basic)
            if (level >= RIDING_ARTISAN_LEVEL) standard.add(swift)
        }
        for (spell in standard) {
            if (!data.spellExists(spell) || !data.spellFits(spell, race, classId) || knows(spell)) continue
            learn(spell, SpellSource.MOUNT)
            out.add(MountOutcome(null, spell, if (data.isFlyingMount(spell)) "${data.spellName(spell)}: its side's flying mount, as none of its own mounts flies here"
                else "${data.spellName(spell)}: its race's own riding animal, as none of its own mounts runs on the ground here"))
        }
        return out
    }

    /** The race whose riding animals a custom race of the realm takes (its kin), or the race itself. */
    private fun kinRace(side: PortFaction): Int = when (race) {
        9 -> 2          // Goblin: the Horde's wolves
        12 -> 1         // Worgen: Gilneas's horses
        13 -> 1
        14 -> 6         // the Windshapers of Mulgore
        15 -> 4         // Void Elf: the Alliance's elves
        16 -> 10        // Nightborne: the Horde's elves
        17 -> 11        // Lightforged Draenei
        18 -> 8         // Zandalari Troll
        in 1..11 -> race
        else -> if (side == PortFaction.HORDE) 2 else 1
    }

    companion object {
        const val SKILL_RIDING = 762
        const val SKILL_MOUNTS = 777
        const val SKILL_LOCKPICKING = 633
        const val TRAINER_CLASS = 0
        const val TRAINER_MOUNT = 1
        const val TRAINER_TRADESKILL = 2
        const val MAX_PRIMARY_PROFESSIONS = 2
        const val RIDING_APPRENTICE_LEVEL = 20
        const val RIDING_JOURNEYMAN_LEVEL = 40
        const val RIDING_EXPERT_LEVEL = 60
        const val RIDING_ARTISAN_LEVEL = 70
        private const val SPELL_NAME_FIELD = 136

        /** Cooking, Fishing and First Aid (3.3.5a's secondary professions; Riding is the riding trainers'). */
        val SECONDARY_PROFESSIONS = setOf(185, 356, 129)

        /**
         * The class spells 3.3.5a teaches by quests, not trainers, and the level each comes at: warriors' stances, Taunt
         * and Sunder Armor, hunters' pet spells, warlocks' demons, druids' bear form and Moonglade, rogues' poisons,
         * paladins' Redemption, death knights' Runeforging, Death Gate and Deathcharger. (Wrath Remix's module keeps the
         * same list, remix_class_spell, for the same reason.)
         */
        val QUEST_SPELLS: Map<Int, List<Pair<Int, Int>>> = mapOf(
            PortTargets.WARRIOR to listOf(71 to 10, 355 to 10, 7386 to 10, 2458 to 30),
            PortTargets.PALADIN to listOf(7328 to 12),
            PortTargets.HUNTER to listOf(1515 to 10, 883 to 10, 2641 to 10, 6991 to 10, 982 to 10),
            PortTargets.ROGUE to listOf(2842 to 20),
            PortTargets.WARLOCK to listOf(697 to 10, 712 to 20, 691 to 30, 1122 to 50, 18540 to 60),
            PortTargets.DRUID to listOf(5487 to 10, 6795 to 10, 6807 to 10, 18960 to 10),
            PortTargets.DEATH_KNIGHT to listOf(53428 to 55, 50977 to 55, 48778 to 55),
        )

        /** Each race's riding animals: the one sold at its home, and the swift one. */
        val GROUND_MOUNTS = mapOf(
            1 to (458 to 23229), 2 to (580 to 23250), 3 to (6899 to 23238), 4 to (10789 to 23221), 5 to (17462 to 17465),
            6 to (18990 to 23249), 7 to (10873 to 23225), 8 to (8395 to 23241), 10 to (34795 to 33660), 11 to (34406 to 35713),
        )
        val FLYING_ALLIANCE = 32235 to 32242
        val FLYING_HORDE = 32243 to 32246

        fun normalize(name: String): String = name.lowercase().filter { it.isLetterOrDigit() }

        /** The retail points of a profession that 3.3.5a has: its Classic, Outland and Northrend parts. */
        fun professionPoints(profession: PortProfession): Int = profession.tiers.filter { tier ->
            val name = tier.name.trim().lowercase()
            name.startsWith("classic") || name.startsWith("outland") || name.startsWith("northrend") || name == profession.name.trim().lowercase()
        }.sumOf { it.points.coerceAtLeast(0) }
    }
}
