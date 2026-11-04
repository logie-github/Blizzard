package com.logie.blizz.music

/**
 * The music: one track for the launcher and one for each game, downloaded to the phone the first time
 * the app opens (never packaged with it) and kept in the app's own folder ([MusicStore]). A game's
 * track plays from the moment its page is opened, and follows the version chosen (Warcraft III's
 * Reign of Chaos or The Frozen Throne). Plain Kotlin, unit-tested.
 */
object MusicCatalog {
    data class Track(val key: String, val label: String, val url: String)

    /** What plays on the shelf until a game is selected. */
    const val LAUNCHER = "launcher"

    val tracks: List<Track> = listOf(
        Track(LAUNCHER, "Blizzard: Arthas, My Son (Cinematic Intro)", "https://nu.vgmtreasurechest.com/soundtracks/world-of-warcraft-3-wrath-of-the-lich-king-complete/didrxqkd/110.%20Arthas%2C%20My%20Son%20%28Cinematic%20Intro%29.mp3"),
        Track("diablo", "Diablo: Menu", "https://vgmtreasurechest.com/soundtracks/diablo-1/shglmcau/01%20Menu.mp3"),
        Track("diablo2", "Diablo II: Act 0 Intro", "https://jetta.vgmtreasurechest.com/soundtracks/diablo-ii-original-soundtrack/inqqhkhf/Act%200%20-%20Intro.mp3"),
        // khinsider's page for the song: [MusicStore] reads the file's address from it.
        Track("starcraft", "StarCraft: Main Title", "https://downloads.khinsider.com/game-soundtracks/album/starcraft/01.%20Starcraft%20Main%20Title.mp3"),
        Track("starcraft2", "StarCraft II: Wings of Liberty", "https://lambda.vgmtreasurechest.com/soundtracks/starcraft-ii-wings-of-liberty-soundtrack/cpsutkvv/01.%20Wings%20of%20Liberty.mp3"),
        Track("warcraft", "Warcraft: Intro", "https://jetta.vgmtreasurechest.com/soundtracks/warcraft-remastered-windows-gamerip-2024/lijwejin/01.%20Intro%20%5BRemastered%5D.mp3"),
        Track("warcraft2", "Warcraft II: Intro", "https://jetta.vgmtreasurechest.com/soundtracks/warcraft-2-remastered-windows-gamerip-2024/xofjdpnw/01.%20Intro.mp3"),
        Track("warcraft3_roc", "Warcraft III: Reign of Chaos", "https://downloads.khinsider.com/game-soundtracks/album/warcraft-iii-reforged-gamerip/01.%20Reign%20Of%20Chaos.mp3"),
        Track("warcraft3_tft", "Warcraft III: The Frozen Throne", "https://lambda.vgmtreasurechest.com/soundtracks/warcraft-iii-reforged-gamerip/tjrfbqbj/36%20The%20Frozen%20Throne.mp3"),
        Track("wow", "World of Warcraft: Wrath of the Lich King (Main Title)", "https://nu.vgmtreasurechest.com/soundtracks/world-of-warcraft-3-wrath-of-the-lich-king-complete/lylhbnie/114.%20Wrath%20of%20the%20Lich%20King%20%28Main%20Title%29.mp3"),
        // The original game's title music: kept for a Classic version of the game; no tile uses it yet.
        Track("wow_classic", "World of Warcraft: Legends of Azeroth", "https://nu.vgmtreasurechest.com/soundtracks/world-of-warcraft-soundtrack/olngrskz/01.%20Main%20Title%20-%20Legends%20of%20Azeroth.mp3"),
    )

    /** The track that plays for [gameId] (the installation the page shows: StarCraft's Remastered and Diablo II's Resurrected share the original's), the launcher's when there's no game or no track. */
    fun keyFor(gameId: String?): String {
        val key = when (gameId) { "starcraft_remastered" -> "starcraft"; "diablo2_resurrected" -> "diablo2"; else -> gameId }
        return if (key != null && tracks.any { it.key == key }) key else LAUNCHER
    }

    fun track(key: String): Track? = tracks.firstOrNull { it.key == key }
}
