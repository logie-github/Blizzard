package com.logie.blizz.porter.port

import com.logie.blizz.wow.Realm

/**
 * The Character Porter's engine for the app's Wrath realms (AzerothCore 3.3.5a): makes a retail character, as the
 * Armory describes it ([PortCharacter]), into a playable character of one of the phone's realms.
 *
 * [plan] reads the realm (its databases through [db], its client data files through [files]) and never writes; it
 * returns everything that would be written and why ([PortPlan], [PortReport]). [apply] writes a plan: one transaction
 * in the characters database (the character's guid and its items' guids taken from the current highest at that moment,
 * nothing of any other character touched), then the login database's count of the account's characters on the realm.
 * The realm's world server must be stopped meanwhile (it keeps the next guids in memory): the screens see to it, and
 * start only the database.
 *
 * Every value that reaches SQL is a number, or a name that passed the realm's name rules and is quoted besides
 * ([Sql.text]).
 */
class Porter(
    private val db: RealmDb,
    val files: RealmFiles,
    /** Seconds since 1970: achievements' dates when the Armory gave none, and the character's last logout. */
    private val now: () -> Long = { System.currentTimeMillis() / 1000 },
    /** The realm's client data when it is already read (tests give theirs); else read from [files] when first needed. */
    data: RealmData? = null,
) {
    val realm: PortRealm get() = files.realm
    private var dataCache: RealmData? = data
    private var worldCache: Pair<Int?, RealmWorld>? = null

    /** The realm's client data (loaded once: Spell.dbc is large). */
    fun data(): RealmData = dataCache ?: RealmData.load(files.dbcDir(), db, realm.worldDb).also { dataCache = it }

    private fun world(classId: Int? = null): RealmWorld {
        worldCache?.let { (forClass, world) -> if (forClass == classId) return world }
        return RealmWorld.load(db, realm.worldDb, classId).also { worldCache = classId to it }
    }

    // ---- before planning: what the screen asks

    /** Whether this realm can take a ported character (and why not). */
    fun support(): RealmSupport {
        when (realm.realm) {
            Realm.REMIX -> return RealmSupport(false, RealmSupport.REMIX_REASON)
            Realm.CHROMIE, Realm.WRATHPP -> Unit
            else -> return RealmSupport(false, RealmSupport.NOT_WRATH_REASON)
        }
        val wanted = listOf(realm.authDb, realm.worldDb, realm.charactersDb)
        val present = try {
            db.query("information_schema", "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME IN (${wanted.joinToString(",") { Sql.text(it) }})")
                .mapNotNull { it.firstOrNull() }.toSet()
        } catch (e: RealmDbException) {
            return RealmSupport(false, "The realm's database didn't answer: ${e.message}")
        }
        val missing = wanted.filter { it !in present }
        if (missing.isNotEmpty()) {
            return RealmSupport(false, if (realm.realm == Realm.WRATHPP) "Wrath++ isn't set up on this phone yet (its databases aren't there)." else "The realm's databases aren't set up yet (${missing.joinToString()}): start the realm once.")
        }
        return RealmSupport(true)
    }

    fun levelCap(): LevelCap = files.levelCap()

    /** The retail level as a level of this realm: the same share of its cap (ChromieCraft's progression cap when it has one). */
    fun scaledLevel(retailLevel: Int): Int = PortLevels.scaled(retailLevel, levelCap().effective)

    /** The race and class pairs a character can be made as here (playercreateinfo: it has every module's races). */
    fun raceClassCombos(): List<RaceClass> = world().combos

    /** The side a race of this realm is on. */
    fun factionOf(race: Int): PortFaction = data().faction(race)

    /** What the retail character becomes here when its own race or class isn't the realm's (see [PortTargets.suggest]). */
    fun suggestTarget(character: PortCharacter, level: Int? = null): TargetSuggestion? {
        val cap = levelCap()
        return PortTargets.suggest(character, raceClassCombos(), ::factionOf, level ?: scaledLevel(character.level), cap.heroicStart)
    }

    /** What is wrong with [name] as a new character's name on this realm (the rules, the realm's reserved names, a character that has it), or null. */
    fun nameProblem(name: String): String? {
        val normalized = PortNames.normalize(name)
        PortNames.problem(normalized, files.minNameLength(), files.strictNames())?.let { return it }
        val lower = normalized.lowercase()
        val data = data()
        if (lower in data.reservedNames) return "That name is reserved."
        if (lower in data.profaneNames) return "That name isn't allowed."
        val q = Sql.text(normalized)
        val rows = db.queryAll(realm.charactersDb, listOf(
            "SELECT 1 FROM characters WHERE name = $q",
            "SELECT 1 FROM reserved_name WHERE name = $q",
            "SELECT 1 FROM profanity_name WHERE name = $q",
        ))
        if (rows[0].isNotEmpty()) return "A character of this realm already has that name."
        if (rows[1].isNotEmpty()) return "That name is reserved."
        if (rows[2].isNotEmpty()) return "That name isn't allowed."
        return null
    }

    // ---- the plan

    /** Works out the port of [character] as [options] say. Reads only. */
    fun plan(character: PortCharacter, options: PortOptions): PortPlan {
        val decisions = ArrayList<PortDecision>()
        val refusals = ArrayList<String>()
        fun decide(area: PortArea, subject: String, outcome: PortOutcome, detail: String = "") = decisions.add(PortDecision(area, subject, outcome, detail))
        fun refuse(text: String) {
            refusals.add(text)
            decide(PortArea.REALM, "refused", PortOutcome.REFUSED, text)
        }

        if (options.realm != realm.realm) refuse("The options are for ${options.realm.displayName}, this porter writes ${realm.realm.displayName}.")
        val support = support()
        if (!support.supported) {
            refuse(support.reason ?: "This realm can't take a ported character.")
            return empty(options, decisions, refusals)
        }

        val data = data()
        val world = world(options.classId)
        val cap = levelCap()
        val race = options.race
        val classId = options.classId
        val name = PortNames.normalize(options.name)
        nameProblem(name)?.let(::refuse)
        val create = world.createInfo(race, classId)
        if (create == null) refuse("This realm has no ${data.raceName(race)} ${data.className(classId)}.")
        if (options.gender !in 0..1) refuse("The gender is 0 (male) or 1 (female).")
        val level = options.level ?: PortLevels.scaled(character.level, cap.effective)
        when {
            level < 1 || level > cap.max -> refuse("Level $level is outside this realm's 1 to ${cap.max}.")
            classId == PortTargets.DEATH_KNIGHT && level < cap.heroicStart -> refuse("A death knight is at least level ${cap.heroicStart} on this realm.")
        }
        decide(PortArea.LEVEL, "level", if (options.level == null) PortOutcome.MAPPED else PortOutcome.NOTE,
            if (options.level == null) "retail ${character.level} of ${PortLevels.RETAIL_CAP} is $level of this realm's ${cap.effective}" +
                (if (cap.progression != null && cap.progression < cap.max) " (ChromieCraft's progression cap; the realm allows ${cap.max})" else "")
            else "$level, as chosen (retail ${character.level})")
        if (character.raceId != race || character.classId != classId) {
            decide(PortArea.CHARACTER, "race and class", PortOutcome.MAPPED,
                "${PortTargets.retailRaceName(character.raceId)} ${PortTargets.retailClassName(character.classId)} is a ${data.raceName(race)} ${data.className(classId)} here")
        }
        if (character.name != name) decide(PortArea.CHARACTER, "name", PortOutcome.MAPPED, "${character.name} is $name here")

        // The account, and room for one more character.
        val accountName = options.account.trim().uppercase()
        var accountId = 0
        if (!ACCOUNT.matches(accountName)) {
            refuse("\"${options.account}\" can't be an account name.")
        } else {
            val auth = db.queryAll(realm.authDb, listOf(
                "SELECT id FROM account WHERE username = ${Sql.text(accountName)}",
            ))
            accountId = auth[0].firstOrNull()?.firstOrNull()?.toIntOrNull() ?: 0
            if (accountId == 0) refuse("This phone's realms have no account $accountName.")
        }
        val counts = db.queryAll(realm.charactersDb, listOf(
            "SELECT COUNT(*) FROM characters WHERE account = $accountId",
            "SELECT COALESCE(MAX(guid), 0) FROM characters",
        ))
        val onRealm = counts[0].firstOrNull()?.firstOrNull()?.toIntOrNull() ?: 0
        val estimatedGuid = (counts[1].firstOrNull()?.firstOrNull()?.toIntOrNull() ?: 0) + 1
        if (accountId != 0 && onRealm >= files.charactersPerRealm()) refuse("The account has $onRealm characters on ${realm.realm.displayName}, as many as a realm's list holds.")
        if (refusals.isNotEmpty() || create == null) return empty(options, decisions, refusals)

        val side = data.faction(race)
        val money = (options.money ?: 0L).coerceIn(0L, MAX_MONEY)
        if ((options.money ?: 0L) > MAX_MONEY) decide(PortArea.CHARACTER, "money", PortOutcome.NOTE, "cut to the most a character can hold")

        // Spells and skills: class, quests, weapons, riding; then professions and mounts.
        val book = SpellBook(data, world, race, classId, level)
        val taught = book.learnClass()
        for ((source, count) in taught) if (count > 0) decide(PortArea.SPELLS, source.label, PortOutcome.ADDED, "$count spells up to level $level")
        var primaries = 0
        for (profession in character.professions) {
            val outcome = book.learnProfession(profession, primaries)
            if (outcome.problem != null) {
                decide(PortArea.PROFESSIONS, profession.name, PortOutcome.DROPPED, outcome.problem)
                continue
            }
            if (outcome.primary) primaries++
            decide(PortArea.PROFESSIONS, profession.name, PortOutcome.KEPT,
                "${outcome.value} of ${outcome.max} (retail Classic, Outland and Northrend: ${SpellBook.professionPoints(profession)}), ${outcome.recipes} recipes")
        }
        for (mount in book.learnMounts(character.mounts, side)) {
            when {
                mount.mount == null -> decide(PortArea.MOUNTS, "standard mount", PortOutcome.ADDED, mount.detail)
                mount.spell == null -> decide(PortArea.MOUNTS, mount.mount.name, PortOutcome.DROPPED, mount.detail)
                else -> decide(PortArea.MOUNTS, mount.mount.name, PortOutcome.KEPT, mount.detail)
            }
        }
        if (level < SpellBook.RIDING_APPRENTICE_LEVEL && book.learned.values.any { it == SpellSource.MOUNT }) {
            decide(PortArea.MOUNTS, "riding", PortOutcome.NOTE, "its mounts are ridden from level ${SpellBook.RIDING_APPRENTICE_LEVEL}, when a riding trainer teaches it")
        }

        // Reputations (some items ask for one).
        val reputations = planReputations(data, character, race, classId, decide = ::decide)
        val ranks = reputations.associate { it.faction to rankOf(baseReputation(data, it.faction, race, classId) + it.standing) }

        // Equipment.
        val role = character.spec?.role ?: defaultRole(classId)
        val primaryStat = character.spec?.primaryStat?.takeIf { character.classId == classId }
        val rules = GearRules(race, classId, level, side, options.gearTier)
        val crafted = HashSet<Int>()
        for (row in data.spells.rows()) for (item in data.createdItems(row.id)) crafted.add(item)
        val itemSource = RealmItemSource(db, realm.worldDb)
        val skillValues = book.skills.mapValues { it.value.value }
        val knownSpells = book.learned.keys + book.skillSpells() + book.customSpells
        val gear = GearPlanner(itemSource, rules, StatWeights.of(classId, role, primaryStat), role, skillValues, knownSpells, { ranks[it] ?: baseRank(data, it, race, classId) }, crafted, data::equipStats)
            .plan(character.equipment)
        decide(PortArea.EQUIPMENT, "weapons", PortOutcome.NOTE, gear.handsWhy)
        decide(PortArea.EQUIPMENT, "gear tier", PortOutcome.NOTE, if (level == 60 || level == 70 || level == 80) "${options.gearTier.label}: ${options.gearTier.about}, item level ${rules.maxItemLevel} at most"
            else "items of its level: item level ${rules.maxItemLevel} at most, ${if (rules.maxQuality >= GearRules.QUALITY_EPIC) "epics allowed" else "blues at best"} (${options.gearTier.label})")
        val items = ArrayList<PlannedItem>()
        for (choice in gear.choices) choice.item?.let { items.add(plannedItem(it, choice.slot, 1)) }

        // Bags, the hearthstone, and what the class needs to play: ammunition, a shaman's totems.
        val ammoId = planExtras(itemSource, crafted, rules, gear.choices, items, decide = ::decide)

        // Quests, achievements, titles.
        val quests = planQuests(character, race, decide = ::decide)
        val achievements = planAchievements(data, character, side, decide = ::decide)
        val (knownTitles, chosenTitle) = planTitles(data, character, decide = ::decide)

        // Where it is, and the map it knows.
        val position = planPosition(world, create, race, side, decide = ::decide)
        val continents = PortMap.continents(level)
        val explored = PortMap.exploredZones(data, continents)
        val taxi = PortMap.taxiMask(data, side, continents)
        decide(PortArea.MAP, "explored", PortOutcome.ADDED,
            if (continents.isEmpty()) "nothing yet (under level 10: its start, as a new character)" else continents.joinToString { it.name.lowercase().replace('_', ' ') } +
                ": ${explored.sumOf { Integer.bitCount(it) }} areas, ${taxi.sumOf { Integer.bitCount(it) }} flight paths of its side")

        // Its looks, kept to what its race and gender have.
        val appearance = planAppearance(data, character.appearance, race, options.gender, classId, decide = ::decide)

        // Spells and skills as written.
        val spells = book.written()
        val dropped = book.learned.keys.filter { it !in spells && it !in book.skillSpells() && it !in book.customSpells }
        if (dropped.isNotEmpty()) decide(PortArea.SPELLS, "not kept", PortOutcome.DROPPED, "${dropped.size} spells the realm would take away at login (another race's or class's skill)")
        val skills = book.skills.filter { data.skillInfo(it.key, race, classId) != null && it.value.value > 0 }
            .map { PlannedSkill(it.key, it.value.value, it.value.max) }.sortedBy { it.skill }
        decide(PortArea.SKILLS, "skills", PortOutcome.ADDED, "${skills.size}: weapon and other level-kept skills at ${level * 5}, its armour, languages, riding ${book.skillValue(SpellBook.SKILL_RIDING)}")

        // The action bars a new character of the race and class has, with the ranks it knows now.
        val actions = planActions(world, book, race, classId, itemSource, decide = ::decide)

        val noXp = cap.progression != null && level == cap.progression && realm.realm == Realm.CHROMIE
        if (noXp) decide(PortArea.LEVEL, "experience", PortOutcome.NOTE, "locked at the progression cap, as the realm locks a character reaching it (mod-chromie-xp)")

        val report = PortReport(decisions, gear.choices, linkedMapOf(
            "items" to items.size, "spells" to spells.size, "skills" to skills.size, "reputations" to reputations.size,
            "quests" to quests.size, "achievements" to achievements.size, "action buttons" to actions.size,
        ))
        return PortPlan(
            realm = realm, accountId = accountId, account = accountName, name = name, race = race, classId = classId, gender = options.gender,
            level = level, money = money, appearance = appearance, position = position,
            playerFlags = if (noXp) PLAYER_FLAGS_NO_XP_GAIN else 0, atLogin = AT_LOGIN_FIRST,
            exploredZones = explored, taxiMask = taxi, knownTitles = knownTitles, chosenTitle = chosenTitle, ammoId = ammoId,
            items = items, spells = spells, skills = skills, reputations = reputations, quests = quests, achievements = achievements,
            actions = actions, report = report, refusals = refusals, estimatedGuid = estimatedGuid,
        )
    }

    /** Writes [plan]. Throws [IllegalStateException] for a plan that isn't [PortPlan.ready], [RealmDbException] when the realm refuses it (nothing is left behind). */
    fun apply(plan: PortPlan): PortResult {
        check(plan.ready) { "The plan can't be written: ${plan.refusals.joinToString(" ")}" }
        check(plan.realm == realm) { "The plan is for another realm" }
        val rows = db.execute(realm.charactersDb, PortSql.characterScript(plan, files.charactersPerRealm(), now()))
        val result = rows.lastOrNull { it.size >= 2 && it[0] == "porter" } ?: throw RealmDbException("The realm didn't say which guid the character got")
        val guid = result[1]?.toIntOrNull() ?: throw RealmDbException("The realm didn't say which guid the character got")
        val firstItem = (result.getOrNull(2)?.toIntOrNull() ?: 0) + 1
        db.execute(realm.authDb, PortSql.realmCharactersScript(realm, plan.accountId))
        return PortResult(guid, firstItem, firstItem + plan.items.size - 1, plan.name)
    }

    // ---- the parts of a plan

    private fun empty(options: PortOptions, decisions: List<PortDecision>, refusals: List<String>) = PortPlan(
        realm = realm, accountId = 0, account = options.account, name = PortNames.normalize(options.name), race = options.race, classId = options.classId,
        gender = options.gender, level = options.level ?: 0, money = 0, appearance = PortAppearance(), position = PlannedPosition("", 0, 0, 0f, 0f, 0f, 0f),
        playerFlags = 0, atLogin = 0, exploredZones = emptyList(), taxiMask = emptyList(), knownTitles = emptyList(), chosenTitle = 0, ammoId = 0,
        items = emptyList(), spells = emptyList(), skills = emptyList(), reputations = emptyList(), quests = emptyList(), achievements = emptyList(),
        actions = emptyList(), report = PortReport(decisions, emptyList(), emptyMap()), refusals = refusals, estimatedGuid = 0,
    )

    private fun plannedItem(item: ItemTemplate, slot: Int, count: Int) =
        PlannedItem(item.entry, item.name, slot, count, item.maxDurability, item.charges.joinToString(" ", postfix = " "))

    private fun defaultRole(classId: Int): PortRole = when (classId) {
        PortTargets.PRIEST -> PortRole.HEALER
        else -> PortRole.DAMAGE
    }

    /**
     * The bags (four of the largest common bags of its level the game sells or crafts), the hearthstone, ammunition for
     * a gun, bow or crossbow, and a shaman's four totems (3.3.5a's totem spells need them). Returns the ammunition's id.
     */
    private fun planExtras(
        source: RealmItemSource,
        crafted: Set<Int>,
        rules: GearRules,
        gear: List<SlotChoice>,
        items: MutableList<PlannedItem>,
        decide: (PortArea, String, PortOutcome, String) -> Unit,
    ): Int {
        val level = rules.level
        val bag = source.bags(rules).filter { it.containerSlots > 0 && !GearPlanner.isUnreal(it.name) }
            .let { list -> val ok = source.obtainable(list.map { it.entry }, crafted); list.filter { it.entry in ok } }.firstOrNull()
        if (bag != null) {
            for (i in 0 until 4) items.add(plannedItem(bag, PortSlots.BAG_FIRST + i, 1))
            decide(PortArea.BAGS, "bags", PortOutcome.ADDED, "four ${bag.name} (${bag.containerSlots} slots)")
        } else decide(PortArea.BAGS, "bags", PortOutcome.NOTE, "no bag of its level found")
        var next = PortSlots.BACKPACK_FIRST
        val known = source.items(listOf(HEARTHSTONE) + TOTEMS.map { it.first })
        known[HEARTHSTONE]?.let { items.add(plannedItem(it, next++, 1)); decide(PortArea.BAGS, "hearthstone", PortOutcome.ADDED, "in the backpack, bound to where it starts") }
        var ammoId = 0
        val ranged = gear.firstOrNull { it.slot == PortSlots.RANGED }?.item
        if (ranged != null && ranged.itemClass == StatWeights.ITEM_WEAPON && ranged.subclass in setOf(GearPlanner.BOW, GearPlanner.GUN, GearPlanner.CROSSBOW)) {
            val kind = if (ranged.subclass == GearPlanner.GUN) AMMO_BULLET else AMMO_ARROW
            val ammo = source.ammo(rules, kind).let { list -> val ok = source.obtainable(list.map { it.entry }, crafted); list.filter { it.entry in ok } }.firstOrNull()
            if (ammo != null) {
                val stack = ammo.stackable.coerceIn(1, 1000)
                repeat(2) { items.add(plannedItem(ammo, next++, stack)) }
                ammoId = ammo.entry
                decide(PortArea.BAGS, "ammunition", PortOutcome.ADDED, "2 x $stack ${ammo.name} for its ${if (kind == AMMO_BULLET) "gun" else "bow"}")
            }
        }
        if (rules.classId == PortTargets.SHAMAN) {
            val totems = TOTEMS.filter { (_, at) -> level >= at }.mapNotNull { (id, _) -> known[id] }
            for (totem in totems) items.add(plannedItem(totem, next++, 1))
            if (totems.isNotEmpty()) decide(PortArea.BAGS, "totems", PortOutcome.ADDED, totems.joinToString { it.name } + " (its totem spells need them)")
        }
        return ammoId
    }

    /** Its reputations, matched by the faction's name in this game, as the realm keeps them (the race's and class's base taken off). */
    private fun planReputations(
        data: RealmData,
        character: PortCharacter,
        race: Int,
        classId: Int,
        decide: (PortArea, String, PortOutcome, String) -> Unit,
    ): List<PlannedReputation> {
        val byName = HashMap<String, MutableList<Int>>()
        for (row in data.factions.rows()) {
            if (row.int(RealmData.FACTION_LIST) < 0) continue
            byName.getOrPut(factionKey(row.string(RealmData.FACTION_NAME))) { ArrayList() }.add(row.id)
        }
        val out = LinkedHashMap<Int, PlannedReputation>()
        for (rep in character.reputations) {
            val key = factionKey(rep.factionName)
            val id = (byName[key] ?: byName[FACTION_ALIASES[key] ?: ""])?.minOrNull()
            val rank = STANDINGS[rep.standing.trim().lowercase()]
            when {
                id == null -> { decide(PortArea.REPUTATIONS, rep.factionName, PortOutcome.DROPPED, "no such faction in this game"); continue }
                rank == null -> { decide(PortArea.REPUTATIONS, rep.factionName, PortOutcome.DROPPED, "\"${rep.standing}\" has no counterpart in this game"); continue }
            }
            id!!
            val flags = defaultFlags(data, id, race, classId)
            if (flags and (FACTION_FLAG_INVISIBLE_FORCED or FACTION_FLAG_HIDDEN) != 0) {
                decide(PortArea.REPUTATIONS, rep.factionName, PortOutcome.DROPPED, "the game hides it from this race (the other side's)")
                continue
            }
            val target = RANK_START[rank!!] + (rep.value ?: 0).coerceIn(0, RANK_SIZE[rank] - 1)
            val base = baseReputation(data, id, race, classId)
            var written = flags or FACTION_FLAG_VISIBLE
            if (rank >= RANK_NEUTRAL) written = written and FACTION_FLAG_AT_WAR.inv()
            out[id] = PlannedReputation(id, target - base, written)
            decide(PortArea.REPUTATIONS, rep.factionName, PortOutcome.KEPT, "${STANDING_NAMES[rank]}${if ((rep.value ?: 0) > 0) " (${rep.value})" else ""}")
        }
        return out.values.toList()
    }

    /** ReputationMgr::GetBaseReputation: the faction's base for the race and class. */
    private fun baseReputation(data: RealmData, faction: Int, race: Int, classId: Int): Int = factionColumn(data, faction, race, classId, RealmData.FACTION_BASE)

    /** ReputationMgr::GetDefaultStateFlags. */
    private fun defaultFlags(data: RealmData, faction: Int, race: Int, classId: Int): Int = factionColumn(data, faction, race, classId, RealmData.FACTION_FLAGS)

    private fun factionColumn(data: RealmData, faction: Int, race: Int, classId: Int, first: Int): Int {
        val row = data.factions[faction] ?: return 0
        val raceBit = RealmData.raceBit(race)
        val classBit = RealmData.classBit(classId)
        for (i in 0..3) {
            val raceMask = row.int(RealmData.FACTION_RACE_MASK + i)
            val classMask = row.int(RealmData.FACTION_CLASS_MASK + i)
            if ((raceMask and raceBit != 0 || (raceMask == 0 && classMask != 0)) && (classMask and classBit != 0 || classMask == 0)) return row.int(first + i)
        }
        return 0
    }

    private fun baseRank(data: RealmData, faction: Int, race: Int, classId: Int): Int = rankOf(baseReputation(data, faction, race, classId))

    /** ReputationMgr::ReputationToRank. */
    private fun rankOf(reputation: Int): Int {
        for (rank in RANK_START.indices.reversed()) if (reputation >= RANK_START[rank]) return rank
        return 0
    }

    /**
     * Its completed quests that this realm has and are the same quests: by title when the Armory gave one, else only
     * the game's own (ids up to 26034, Wrath's last: above it are this realm's modules' quests, whose ids can be retail's
     * newer ones), and open to its race here. Written as rewarded; no reward is given again.
     */
    private fun planQuests(character: PortCharacter, race: Int, decide: (PortArea, String, PortOutcome, String) -> Unit): List<Int> {
        val wanted = character.completedQuests.filter { it.id > 0 }.distinctBy { it.id }
        if (wanted.isEmpty()) return emptyList()
        val realmQuests = HashMap<Int, RealmQuest>()
        for (chunk in wanted.chunked(2000)) {
            for (row in db.query(realm.worldDb, "SELECT ID, LogTitle, AllowableRaces FROM quest_template WHERE ID IN (${Sql.list(chunk.map { it.id })})")) {
                val id = row[0]?.toIntOrNull() ?: continue
                realmQuests[id] = RealmQuest(id, row.getOrNull(1) ?: "", row.getOrNull(2)?.toLongOrNull() ?: 0L)
            }
        }
        val raceBit = RealmData.raceBit(race).toLong()
        val kept = ArrayList<Int>()
        var missing = 0
        var other = 0
        var closed = 0
        for (quest in wanted) {
            val here = realmQuests[quest.id]
            when {
                here == null -> missing++
                quest.name != null && !GearPlanner.sameName(here.title, quest.name) -> other++
                quest.name == null && quest.id > STOCK_LAST_QUEST -> other++
                here.allowableRaces != 0L && here.allowableRaces and raceBit == 0L -> closed++
                else -> kept.add(quest.id)
            }
        }
        decide(PortArea.QUESTS, "completed quests", PortOutcome.KEPT, "${kept.size} of ${wanted.size}")
        if (missing > 0) decide(PortArea.QUESTS, "not in this game", PortOutcome.DROPPED, "$missing (later expansions')")
        if (other > 0) decide(PortArea.QUESTS, "another quest here", PortOutcome.DROPPED, "$other (the realm's quest of that id isn't the same quest)")
        if (closed > 0) decide(PortArea.QUESTS, "not open to its race here", PortOutcome.DROPPED, "$closed")
        return kept.sorted()
    }

    /**
     * Its achievements this game has (the client's own, not a module's), but statistics, hidden ones, realm firsts
     * (it wasn't first here) and the other side's.
     */
    private fun planAchievements(data: RealmData, character: PortCharacter, side: PortFaction, decide: (PortArea, String, PortOutcome, String) -> Unit): List<Pair<Int, Long>> {
        if (character.achievements.isEmpty()) return emptyList()
        val kept = LinkedHashMap<Int, Long>()
        var missing = 0
        var skipped = 0
        var otherSide = 0
        for (achievement in character.achievements) {
            val row = data.achievements[achievement.id]
            if (row == null || !data.achievements.inFile(achievement.id)) { missing++; continue }
            if (row.int(RealmData.ACHIEVEMENT_FLAGS) and (ACHIEVEMENT_COUNTER or ACHIEVEMENT_HIDDEN or ACHIEVEMENT_REALM_FIRST) != 0) { skipped++; continue }
            val faction = row.int(RealmData.ACHIEVEMENT_FACTION)
            if ((faction == 0 && side != PortFaction.HORDE) || (faction == 1 && side != PortFaction.ALLIANCE)) { otherSide++; continue }
            kept[achievement.id] = achievement.earnedAt?.takeIf { it > 0 } ?: now()
        }
        decide(PortArea.ACHIEVEMENTS, "earned", PortOutcome.KEPT, "${kept.size} of ${character.achievements.size}")
        if (missing > 0) decide(PortArea.ACHIEVEMENTS, "not in this game", PortOutcome.DROPPED, "$missing")
        if (skipped > 0) decide(PortArea.ACHIEVEMENTS, "statistics, hidden or realm-first", PortOutcome.DROPPED, "$skipped")
        if (otherSide > 0) decide(PortArea.ACHIEVEMENTS, "the other side's", PortOutcome.DROPPED, "$otherSide")
        return kept.entries.map { it.key to it.value }
    }

    /** Its titles this game has (CharTitles.dbc), as the known-titles bits, and the one it shows. */
    private fun planTitles(data: RealmData, character: PortCharacter, decide: (PortArea, String, PortOutcome, String) -> Unit): Pair<List<Int>, Int> {
        val bits = IntArray(KNOWN_TITLES_SIZE)
        var chosen = 0
        var kept = 0
        for (id in character.titleIds.distinct()) {
            val row = data.titles[id]
            if (row == null || !data.titles.inFile(id)) continue
            val bit = row.int(RealmData.TITLE_BIT)
            if (bit <= 0 || bit >= KNOWN_TITLES_SIZE * 32) continue
            bits[bit / 32] = bits[bit / 32] or (1 shl (bit % 32))
            kept++
            if (id == character.activeTitleId) chosen = bit
        }
        if (character.titleIds.isNotEmpty()) {
            decide(PortArea.TITLES, "titles", PortOutcome.KEPT, "$kept of ${character.titleIds.distinct().size}" + if (chosen != 0) ", its own shown" else "")
        }
        return bits.toList() to chosen
    }

    /**
     * Its place: its side's capital, a city a veteran of either side can stand in, its hearthstone set there; but for
     * the realm's races whose module begins them somewhere of their own and keeps them out of the side's cities (the
     * murlocs, Hostile with the towns until their story is done; the naga, whose story begins in Darkshore): where the
     * realm makes them. A death knight goes to the capital too (its own start is Acherus, the death knights' first quests).
     */
    private fun planPosition(world: RealmWorld, create: CreateInfo, race: Int, side: PortFaction, decide: (PortArea, String, PortOutcome, String) -> Unit): PlannedPosition {
        if (race !in OWN_STORY_RACES && side != PortFaction.NEUTRAL) {
            val (key, fallback, zone) = if (side == PortFaction.ALLIANCE) Triple("Stormwind", STORMWIND, ZONE_STORMWIND) else Triple("Orgrimmar", ORGRIMMAR, ZONE_ORGRIMMAR)
            val place = world.places[key] ?: fallback
            decide(PortArea.POSITION, "start", PortOutcome.NOTE, "${place.name}, its side's capital; its hearthstone is set there")
            return PlannedPosition(place.name, place.map, zone, place.x, place.y, place.z, place.o)
        }
        decide(PortArea.POSITION, "start", PortOutcome.NOTE, "where the realm makes this race (map ${create.map}, zone ${create.zone}): its own story begins there, and its side's cities aren't open to it yet; its hearthstone is set there")
        return PlannedPosition("start", create.map, create.zone, create.x, create.y, create.z, create.o)
    }

    /** Its looks, each kept to what the race and gender have in this game (CharSections, CharacterFacialHairStyles); 0s when none came. */
    private fun planAppearance(data: RealmData, wanted: PortAppearance?, race: Int, gender: Int, classId: Int, decide: (PortArea, String, PortOutcome, String) -> Unit): PortAppearance {
        if (wanted == null) {
            decide(PortArea.APPEARANCE, "looks", PortOutcome.NOTE, "none given: the race's first of each")
            return PortAppearance()
        }
        val dk = classId == PortTargets.DEATH_KNIGHT
        val skins = data.looks(race, gender, RealmData.SECTION_SKIN, dk).map { it.second }.toSet()
        val skin = clamp(wanted.skin, skins)
        val faces = data.looks(race, gender, RealmData.SECTION_FACE, dk).filter { it.second == skin }.map { it.first }.toSet()
        val hair = data.looks(race, gender, RealmData.SECTION_HAIR, dk)
        val style = clamp(wanted.hairStyle, hair.map { it.first }.toSet())
        val color = clamp(wanted.hairColor, hair.filter { it.first == style }.map { it.second }.toSet())
        val result = PortAppearance(skin, clamp(wanted.face, faces), style, color, clamp(wanted.facialHair, data.facialHairStyles(race, gender)))
        decide(PortArea.APPEARANCE, "looks", if (result == wanted) PortOutcome.KEPT else PortOutcome.MAPPED,
            "skin ${result.skin}, face ${result.face}, hair ${result.hairStyle} colour ${result.hairColor}, ${if (gender == 0) "facial hair" else "feature"} ${result.facialHair}")
        return result
    }

    /** [value] when the race has it, else the highest it has below it, else its lowest (0 when it has none). */
    private fun clamp(value: Int, valid: Set<Int>): Int = when {
        valid.isEmpty() -> 0
        value in valid -> value
        else -> valid.filter { it < value }.maxOrNull() ?: valid.min()
    }

    /** The race's and class's first action bars (playercreateinfo_action), each spell at the highest rank it knows; what it wouldn't know is left off (the core would drop it with an error). */
    private fun planActions(world: RealmWorld, book: SpellBook, race: Int, classId: Int, source: RealmItemSource, decide: (PortArea, String, PortOutcome, String) -> Unit): List<PlannedAction> {
        val rows = db.query(realm.worldDb, "SELECT button, action, type FROM playercreateinfo_action WHERE race = $race AND class = $classId ORDER BY button")
            .map { CreateAction(it[0]?.toIntOrNull() ?: -1, it[1]?.toIntOrNull() ?: 0, it[2]?.toIntOrNull() ?: -1) }
        val items = source.items(rows.filter { it.type == ACTION_ITEM }.map { it.action })
        val out = ArrayList<PlannedAction>()
        var left = 0
        for (row in rows) {
            if (row.button !in 0 until MAX_ACTION_BUTTONS) continue
            when (row.type) {
                ACTION_SPELL -> {
                    val best = world.chainOf(row.action).lastOrNull { book.knows(it) } ?: row.action.takeIf { book.knows(it) }
                    if (best == null) { left++; continue }
                    out.add(PlannedAction(row.button, best, ACTION_SPELL))
                }
                ACTION_ITEM -> if (row.action in items) out.add(PlannedAction(row.button, row.action, ACTION_ITEM)) else left++
                else -> left++
            }
        }
        decide(PortArea.ACTION_BARS, "action bars", PortOutcome.ADDED, "${out.size} buttons of a new ${data().raceName(race)} ${data().className(classId)}, at the ranks it knows" + if (left > 0) " ($left left off)" else "")
        return out
    }

    companion object {
        private val ACCOUNT = Regex("[A-Z0-9_.@-]{1,32}")
        const val MAX_MONEY = 0x7FFFFFFFL - 1
        const val AT_LOGIN_FIRST = 0x20
        const val PLAYER_FLAGS_NO_XP_GAIN = 0x02000000
        const val HEARTHSTONE = 6948
        /** A shaman's Earth, Fire, Water and Air Totems, and the level each comes at (3.3.5a's totem quests). */
        val TOTEMS = listOf(5175 to 4, 5176 to 10, 5177 to 20, 5178 to 30)
        const val AMMO_ARROW = 2
        const val AMMO_BULLET = 3
        const val KNOWN_TITLES_SIZE = 6
        const val MAX_ACTION_BUTTONS = 144
        const val ACTION_SPELL = 0
        const val ACTION_ITEM = 128
        /** The last quest id of Wrath of the Lich King (3.3.5a); this realm's modules use ids from 50000. */
        const val STOCK_LAST_QUEST = 26034
        const val ACHIEVEMENT_COUNTER = 0x1
        const val ACHIEVEMENT_HIDDEN = 0x2
        const val ACHIEVEMENT_REALM_FIRST = 0x100 or 0x200
        const val FACTION_FLAG_VISIBLE = 0x1
        const val FACTION_FLAG_AT_WAR = 0x2
        const val FACTION_FLAG_HIDDEN = 0x4
        const val FACTION_FLAG_INVISIBLE_FORCED = 0x8
        /** The realm's races with a start and story of their own outside their side's cities (mod-murloc-naga: the murlocs 19, the naga 20). */
        val OWN_STORY_RACES = setOf(19, 20)
        const val ZONE_STORMWIND = 1519
        const val ZONE_ORGRIMMAR = 1637
        /** game_tele's own places, should the realm's table lack them. */
        val STORMWIND = Place("Stormwind", 0, -8833.38f, 628.628f, 94.0066f, 1.06535f)
        val ORGRIMMAR = Place("Orgrimmar", 1, 1629.85f, -4373.64f, 31.5573f, 3.69762f)

        /** ReputationMgr's ranks: where each starts and how long it is (Hated ... Exalted). */
        val RANK_START = intArrayOf(-42000, -6000, -3000, 0, 3000, 9000, 21000, 42000)
        val RANK_SIZE = intArrayOf(36000, 3000, 3000, 3000, 6000, 12000, 21000, 1000)
        const val RANK_NEUTRAL = 3
        val STANDING_NAMES = listOf("Hated", "Hostile", "Unfriendly", "Neutral", "Friendly", "Honored", "Revered", "Exalted")
        val STANDINGS: Map<String, Int> = STANDING_NAMES.withIndex().associate { it.value.lowercase() to it.index }

        /** A faction's name as compared: no case, no punctuation, no leading "The". */
        fun factionKey(name: String): String = name.trim().lowercase().removePrefix("the ").filter { it.isLetterOrDigit() }

        /** Retail's names for factions 3.3.5a calls otherwise. */
        val FACTION_ALIASES = mapOf("gnomeregan" to "gnomeregan exiles").mapKeys { factionKey(it.key) }.mapValues { factionKey(it.value) }
    }
}

/** [ItemSource] on the realm's world database. */
class RealmItemSource(private val db: RealmDb, private val worldDb: String) : ItemSource {
    override fun items(ids: Collection<Int>): Map<Int, ItemTemplate> {
        if (ids.isEmpty()) return emptyMap()
        return db.query(worldDb, "${ItemTemplate.SELECT} WHERE entry IN (${Sql.list(ids.distinct())})").map(ItemTemplate::parse).associateBy { it.entry }
    }

    override fun candidates(inventoryTypes: Set<Int>, rules: GearRules, wide: Boolean): List<ItemTemplate> {
        if (inventoryTypes.isEmpty()) return emptyList()
        return db.query(worldDb, "${ItemTemplate.SELECT} WHERE ${rules.sqlFilter(inventoryTypes, wide)}").map(ItemTemplate::parse)
    }

    override fun obtainable(ids: Collection<Int>, crafted: Set<Int>): Set<Int> {
        val wanted = ids.distinct()
        if (wanted.isEmpty()) return emptySet()
        val out = HashSet(wanted.filter { it in crafted })
        for (chunk in wanted.chunked(3000)) {
            val list = Sql.list(chunk)
            val sources = listOf(
                "SELECT Item FROM creature_loot_template WHERE Item IN ($list)",
                "SELECT Item FROM reference_loot_template WHERE Item IN ($list)",
                "SELECT Item FROM gameobject_loot_template WHERE Item IN ($list)",
                "SELECT Item FROM item_loot_template WHERE Item IN ($list)",
                "SELECT item FROM npc_vendor WHERE item IN ($list)",
            ) + (1..4).map { "SELECT RewardItem$it FROM quest_template WHERE RewardItem$it IN ($list)" } +
                (1..6).map { "SELECT RewardChoiceItemID$it FROM quest_template WHERE RewardChoiceItemID$it IN ($list)" }
            for (rows in db.queryAll(worldDb, sources)) for (row in rows) row.firstOrNull()?.toIntOrNull()?.let(out::add)
        }
        return out
    }

    /**
     * Ordinary bags of the character's level, the largest first: as large as a character of its level carries (6 slots
     * under 10, then 2 more each ten levels, 16 from 50, 20 from 70, 22 at 80).
     */
    fun bags(rules: GearRules): List<ItemTemplate> = db.query(worldDb,
        "${ItemTemplate.SELECT} WHERE class = 1 AND subclass = 0 AND InventoryType = ${InventoryTypes.BAG} AND Quality BETWEEN 1 AND 3" +
            " AND RequiredLevel <= ${rules.level} AND ContainerSlots BETWEEN 1 AND ${bagSlots(rules.level)} AND maxcount = 0" +
            " AND (AllowableClass & ${RealmData.classBit(rules.classId)}) <> 0 AND (AllowableRace & ${RealmData.raceBit(rules.race)}) <> 0" +
            " AND (Flags & ${ItemTemplate.FLAG_CONJURED or ItemTemplate.FLAG_DEPRECATED}) = 0 AND (FlagsExtra & ${rules.otherSideFlag}) = 0" +
            " AND duration = 0 AND HolidayId = 0 AND Map = 0 ORDER BY ContainerSlots DESC, ItemLevel DESC, entry LIMIT 40",
    ).map(ItemTemplate::parse)

    private fun bagSlots(level: Int): Int = when {
        level < 10 -> 6
        level < 50 -> 6 + (level / 10) * 2
        level < 70 -> 16
        level < 80 -> 20
        else -> 22
    }

    /** Arrows (2) or bullets (3) a character of its level can shoot, the best first. */
    fun ammo(rules: GearRules, kind: Int): List<ItemTemplate> = db.query(worldDb,
        "${ItemTemplate.SELECT} WHERE class = 6 AND subclass = $kind AND InventoryType = ${InventoryTypes.AMMO} AND Quality BETWEEN 1 AND 3" +
            " AND RequiredLevel <= ${rules.level} AND (AllowableClass & ${RealmData.classBit(rules.classId)}) <> 0" +
            " AND (FlagsExtra & ${rules.otherSideFlag}) = 0 AND duration = 0 AND HolidayId = 0 ORDER BY ItemLevel DESC, entry LIMIT 40",
    ).map(ItemTemplate::parse)
}
