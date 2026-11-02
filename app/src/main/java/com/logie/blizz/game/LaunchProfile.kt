package com.logie.blizz.game

/**
 * A game's screen: its own size, or the phone's shape at [lines] lines (the X server's size, which
 * smaller game windows are scaled up to fill). Its controls are its own ([com.logie.blizz.controls]).
 */
enum class LaunchProfile(val id: String, val fixedSize: Pair<Int, Int>?, val lines: Int = 720) {
    /** Diablo through DevilutionX at its original 640x480. */
    DIABLO("diablo", 640 to 480),
    /** Diablo II at 800x600, its largest. */
    DIABLO2("diablo2", 800 to 600),
    STARCRAFT("starcraft", 640 to 480),
    STARCRAFT2("starcraft2", null),
    /** The remastered game draws at the phone's shape. */
    STARCRAFT_REMASTERED("starcraft_remastered", null),
    WARCRAFT3("warcraft3", null);

    companion object {
        fun of(id: String?): LaunchProfile = entries.firstOrNull { it.id == id } ?: STARCRAFT
    }
}
