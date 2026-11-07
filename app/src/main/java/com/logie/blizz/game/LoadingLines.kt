package com.logie.blizz.game

import kotlin.random.Random

/** The lines the loading dialogs show while a realm or the game's Windows starts: one at random, another every few seconds. */
object LoadingLines {
    val all = listOf(
        "Sharpening Worgen claws...",
        "Burning World Trees...",
        "Polishing Tauren horns...",
        "Feeding the Murlocs...",
        "Rebuilding Stormwind. Again...",
        "Committing questionable war crimes...",
        "Collecting Gnome punt statistics...",
        "Reattaching Forsaken limbs...",
        "Moisturizing Orc shoulders...",
        "Distributing Warchief titles...",
        "Resurrecting Hogger...",
        "Teaching Murlocs Common...",
        "Brushing Blood Elf eyebrows...",
        "Charging Goblin convenience fees...",
        "Counting Sylvanas' crimes...",
        "Hiding Jaina's emotional baggage...",
        "Repainting the Dark Portal...",
    )

    /** A line other than [previous]. */
    fun next(previous: String? = null, random: Random = Random): String {
        val others = all.filter { it != previous }
        return others[random.nextInt(others.size)]
    }
}
