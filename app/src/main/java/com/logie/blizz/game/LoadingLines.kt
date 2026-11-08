package com.logie.blizz.game

import kotlin.random.Random

/**
 * The lines the loading screens show while a game starts: each game its own (Diablo's, StarCraft's, the Warcraft family's), one at a
 * time, another every few seconds. **A line is never shown twice in the same load**: they come off a shuffled deck, and the deck is
 * only dealt again once every line has been shown (then never starting with the one just shown). A load is the run of lines asked
 * for one game with less than [LOAD_GAP_MS] between them; another game, or a pause longer than that, begins a new load.
 * Plain Kotlin (the clock and the dice are passed in), unit-tested.
 */
object LoadingLines {
    /** World of Warcraft, Warcraft: the lines it has always had. */
    val warcraft = listOf(
        "Sharpening Worgen claws...", "Burning World Trees...", "Polishing Tauren horns...", "Feeding the Murlocs...",
        "Rebuilding Stormwind. Again...", "Committing questionable war crimes...", "Collecting Gnome punt statistics...",
        "Reattaching Forsaken limbs...", "Moisturizing Orc shoulders...", "Distributing Warchief titles...", "Resurrecting Hogger...",
        "Teaching Murlocs Common...", "Brushing Blood Elf eyebrows...", "Charging Goblin convenience fees...",
        "Counting Sylvanas' crimes...", "Hiding Jaina's emotional baggage...", "Repainting the Dark Portal...",
    )

    val diablo = listOf(
        "Polishing Diablo's horns...",
        "Reopening the gates of Hell...",
        "Feeding the Butcher...",
        "Sharpening Wirt's leg...",
        "Reanimating unpaid interns...",
        "Rebuilding Tristram. Again...",
        "Teaching skeletons to play dead...",
        "Moisturizing Lilith's wings...",
        "Giving Inarius another superiority complex...",
        "Refilling the blood fountains...",
        "Replacing missing Necromancer organs...",
        "Counting the Prime Evils...",
        "Summoning additional emotional damage...",
        "Convincing demons to unionize...",
        "Teaching Treasure Goblins to share...",
        "Recalculating Hell's property taxes...",
        "Harvesting fresh corpses...",
        "Teaching Barbarians indoor voices...",
        "Removing the good loot...",
        "Adding another layer to Hell...",
        "Increasing the Butcher's cholesterol...",
        "Replacing Tyrael's missing feathers...",
        "Teaching Druids to use litter boxes...",
        "Restocking the Horadric Cube...",
        "Making Sanctuary less sanitary...",
        "Giving Mephisto anger management lessons...",
        "Lowering legendary drop rates...",
        "Reattaching severed limbs...",
        "Explaining mortality to Necromancers...",
        "Repainting the pentagrams...",
        "Adding more teeth to the demons...",
        "Convincing Deckard Cain to stay awhile...",
        "Removing the stairs from the cathedral...",
        "Giving fallen shamans more friends to resurrect...",
        "Preparing another unnecessarily complicated ritual...",
        "Searching for the nonexistent Cow Level...",
        "Blessing questionable equipment...",
        "Filing demonic tax returns...",
        "Replacing the villagers with cultists...",
        "Making sure nobody stays dead...",
        "Teaching the undead personal hygiene...",
        "Giving Lilith custody of Sanctuary...",
        "Recalibrating the screams of the damned...",
        "Filling dungeons with suspicious barrels...",
        "Convincing angels they're the good guys...",
        "Generating another 47 identical cellars...",
        "Replacing health potions with disappointment...",
        "Teaching demons the importance of consent...",
        "Making the Eternal Conflict slightly more eternal...",
        "Putting Diablo back in his soulstone..."
    )

    val starcraft = listOf(
        "Constructing additional Pylons...",
        "Spawning more Overlords...",
        "Polishing Marine helmets...",
        "Feeding the Zerglings...",
        "Recharging Protoss shields...",
        "Refilling Siege Tank ammunition...",
        "Teaching SCVs basic labor rights...",
        "Increasing the supply cap...",
        "Expanding the Creep...",
        "Repainting the Hyperion...",
        "Applying fresh Stim Packs...",
        "Reattaching Zerg limbs...",
        "Rebuilding Aiur. Again...",
        "Teaching Hydralisks to hug...",
        "Sharpening Zealot blades...",
        "Washing the Creep off the floor...",
        "Giving Kerrigan another makeover...",
        "Counting the Queen of Blades' victims...",
        "Convincing Raynor to stop drinking...",
        "Replacing Tychus' cigar...",
        "Installing windows on Battlecruisers...",
        "Asking the Protoss to stop monologuing...",
        "Making the Swarm slightly swarmier...",
        "Polishing Archon balls...",
        "Adding more lasers to the Void Rays...",
        "Teaching Mutalisks to fly in straight lines...",
        "Recalibrating Yamato Cannons...",
        "Increasing the price of Vespene Gas...",
        "Teaching Probes to say hello...",
        "Extracting additional minerals...",
        "Convincing Drones that becoming buildings is normal...",
        "Repairing the Dominion's propaganda machine...",
        "Preparing another Mengsk betrayal...",
        "Replacing expendable Marines...",
        "Distributing new red shirts...",
        "Teaching Ghosts to be less visible...",
        "Hiding Dark Templars in plain sight...",
        "Asking Artanis to construct additional Pylons...",
        "Recharging the Spear of Adun...",
        "Giving Abathur more biomass...",
        "Evolving unnecessary appendages...",
        "Removing unnecessary appendages...",
        "Reattaching necessary appendages...",
        "Teaching Banelings anger management...",
        "Inflating Banelings...",
        "Warning Marines about inflated Banelings...",
        "Rebuilding the mineral line...",
        "Sending another worker to its death...",
        "Convincing SCVs to stop saying \"What's going on?\"...",
        "Teaching Siege Tanks to reverse...",
        "Adjusting the size of Ultralisk tusks...",
        "Asking the Overmind to use its inside voice...",
        "Unclogging the Nydus Worm...",
        "Teaching Infestors personal boundaries...",
        "Purifying another innocent planet...",
        "Explaining free will to the Purifiers...",
        "Installing antivirus software on the Protoss...",
        "Giving Zeratul another cryptic prophecy...",
        "Telling Tassadar to stop crashing Carriers...",
        "Preparing the Nuclear Launch Detected announcement...",
        "Moving the red dot slightly closer...",
        "Rebuilding the Command Center for the fifth time...",
        "Replacing the Marine who forgot to Stim...",
        "Teaching Medivacs to heal emotional damage...",
        "Calculating how many Zerglings fit inside an Ultralisk...",
        "Blaming everything on Amon...",
        "Telling the Terrans to stop touching Xel'Naga artifacts...",
        "Waiting for the Carrier interceptors to finish building...",
        "Randomizing the next cannon rush location...",
        "Ensuring the enemy always has better upgrades..."
    )

    /** What every game shows unless it has lines of its own. */
    val all: List<String> get() = warcraft

    /** The lines of a game ([gameId] as the shelf has it: "diablo2_resurrected", "starcraft_remastered", "wow_legion"...). */
    fun forGame(gameId: String?): List<String> = when {
        gameId == null -> warcraft
        gameId.startsWith("diablo") -> diablo
        gameId.startsWith("starcraft") -> starcraft
        else -> warcraft
    }

    /** A load goes on while the next line is asked for within this long of the last. */
    const val LOAD_GAP_MS = 60_000L

    private val used = mutableSetOf<String>()
    private var loadGame: String? = null
    private var lastAt = 0L
    private var last: String? = null

    /**
     * The next line of [gameId]'s load: one not yet shown in it. Every line shown goes on the used list; when none is left the list
     * is cleared and a line other than the last is dealt.
     */
    @Synchronized
    fun next(gameId: String?, random: Random = Random, now: Long = System.currentTimeMillis()): String {
        val lines = forGame(gameId)
        if (gameId != loadGame || now - lastAt > LOAD_GAP_MS) { used.clear(); last = null }
        loadGame = gameId
        lastAt = now
        var fresh = lines.filter { it !in used }
        if (fresh.isEmpty()) {
            used.clear()
            fresh = lines.filter { it != last }.ifEmpty { lines }
        }
        val line = fresh[random.nextInt(fresh.size)]
        used += line
        last = line
        return line
    }

    /** Forgets the load in progress (the next line begins a new one). */
    @Synchronized
    fun reset() { used.clear(); loadGame = null; last = null }
}
