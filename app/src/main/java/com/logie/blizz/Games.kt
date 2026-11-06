package com.logie.blizz

import androidx.annotation.DrawableRes

/** A game on the shelf: its box art, and the app it's played with when none is chosen. */
data class Game(
    val id: String,
    val title: String,
    val subtitle: String?,
    val year: Int,
    @DrawableRes val cover: Int,
    val suggestedPackage: String? = null,
    /** The game's own loading screen: its art, and its logo over it (the box art and Blizzard's otherwise). */
    @DrawableRes val splash: Int? = null,
    @DrawableRes val splashLogo: Int? = null,
    /** Wide art for the tile layout (a horizontal tile); without it the loading screen's art or the box art is cut to fit. */
    @DrawableRes val wide: Int? = null,
    /** Where the splash is held when it's cut to the screen: -1 its top edge, 0 its middle. */
    val splashTop: Float = -0.2f,
    /** Other installations of the game, each its own game (its own files, saves and controls): the Remastered StarCraft beside the classic one. */
    val variants: List<Game> = emptyList(),
    /** What the person calls this installation on the page's chooser. */
    val variantLabel: String? = null,
) {
    val fullTitle: String get() = if (subtitle == null) title else "$title: $subtitle"
}

object Games {
    /** The shelf, in alphabetical order. */
    val all: List<Game> = listOf(
        Game("diablo", "Diablo", null, 1996, R.drawable.cover_diablo, splash = R.drawable.splash_diablo, splashLogo = R.drawable.splash_logo_diablo),
        // Resurrected: the Switch release's own program through D2R Mobile's host ([com.logie.blizz.d2r.D2r]); the art is the original's until you change it.
        Game("diablo2", "Diablo II", null, 2000, R.drawable.cover_diablo2, splash = R.drawable.splash_diablo2, splashLogo = R.drawable.splash_logo_diablo2, splashTop = -1f,
            variantLabel = "Original",
            variants = listOf(Game("diablo2_resurrected", "Diablo II", "Resurrected", 2021, R.drawable.cover_diablo2, variantLabel = "Resurrected"))),
        Game("starcraft", "StarCraft", null, 1998, R.drawable.cover_starcraft, variantLabel = "Classic",
            variants = listOf(Game("starcraft_remastered", "StarCraft", "Remastered", 2017, R.drawable.cover_starcraft, variantLabel = "Remastered"))),
        Game("starcraft2", "StarCraft II", null, 2010, R.drawable.cover_starcraft2),
        Game("warcraft", "Warcraft", "Orcs & Humans", 1994, R.drawable.cover_warcraft),
        Game("warcraft2", "Warcraft II", "Tides of Darkness", 1995, R.drawable.cover_warcraft2),
        // One tile for both: the page's chooser (and the tile) switch the art, the music and the game between the two, and the choice is kept.
        Game("warcraft3_roc", "Warcraft III", "Reign of Chaos", 2002, R.drawable.cover_warcraft3_roc, variantLabel = "Reign of Chaos",
            variants = listOf(Game("warcraft3_tft", "Warcraft III", "The Frozen Throne", 2003, R.drawable.cover_warcraft3_tft, variantLabel = "The Frozen Throne"))),
        // One tile, each game mode its own version (and its own zip from the WoW app): Wrath+ plays; the others are imported and kept.
        Game("wow", "World of Warcraft", "Wrath+", 2008, R.drawable.cover_wow, wide = R.drawable.wide_wow, variantLabel = "Wrath+",
            variants = listOf(
                Game("wow_legion", "World of Warcraft", "Legion", 2016, R.drawable.cover_wow, wide = R.drawable.wide_wow, variantLabel = "Legion"),
                Game("wow_octowow", "World of Warcraft", "OctoWoW", 2004, R.drawable.cover_wow, wide = R.drawable.wide_wow, variantLabel = "OctoWoW"),
                Game("wow_forever", "World of Warcraft", "Forever", 2004, R.drawable.cover_wow, wide = R.drawable.wide_wow, variantLabel = "Forever"),
            )),
    ).sortedWith(compareBy(String.CASE_INSENSITIVE_ORDER, Game::title).thenBy(String.CASE_INSENSITIVE_ORDER) { it.subtitle.orEmpty() })

    /** A game or one of its variants, by id. */
    fun find(id: String?): Game? = all.firstNotNullOfOrNull { g -> if (g.id == id) g else g.variants.firstOrNull { it.id == id } }
}
