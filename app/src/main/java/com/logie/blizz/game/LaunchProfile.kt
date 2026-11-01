package com.logie.blizz.game

import com.logie.blizz.controls.Profile

/**
 * A game's launch profile: how it's played by touch ([gestures]), where its own panels are (taps
 * there left-click), the key that opens its menu, and the screen it runs on (the X server's size,
 * which smaller game windows are scaled up to fill). The control mappings themselves are the one
 * gesture system ([com.logie.blizz.controls.Gestures]); a profile only picks between its modes.
 * Plain Kotlin, unit-tested.
 */
enum class LaunchProfile(
    val id: String,
    val gestures: Profile,
    /** How far down the screen the game's bottom panel starts (1: none). */
    val panelTop: Float,
    /** How far down its top bar ends (0: none). */
    val barBottom: Float,
    val menuKey: MenuKey,
    /** The game's own screen size, or null for the phone's shape at [lines] lines. */
    val fixedSize: Pair<Int, Int>?,
    val lines: Int = 720,
) {
    /** Diablo through DevilutionX at its original 640x480. */
    DIABLO("diablo", Profile.ARPG, panelTop = 1f, barBottom = 0f, MenuKey.ESCAPE, 640 to 480),
    /** Diablo II at 800x600, its largest. */
    DIABLO2("diablo2", Profile.ARPG, panelTop = 1f, barBottom = 0f, MenuKey.ESCAPE, 800 to 600),
    /** StarCraft at 640x480: its console is the bottom quarter. */
    STARCRAFT("starcraft", Profile.RTS, panelTop = 0.73f, barBottom = 0.04f, MenuKey.F10, 640 to 480),
    /** StarCraft II at the phone's shape: its console is the bottom fifth. */
    STARCRAFT2("starcraft2", Profile.RTS, panelTop = 0.78f, barBottom = 0.04f, MenuKey.F10, null);

    enum class MenuKey { ESCAPE, F10 }

    companion object {
        fun of(id: String?): LaunchProfile = entries.firstOrNull { it.id == id } ?: STARCRAFT
    }
}
