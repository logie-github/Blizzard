package com.logie.blizz.wrathpp

import java.io.File

/**
 * Wrath++'s graphics settings for a steady frame rate on the phone (the user: "optimize the shit out of the classic reforged
 * integration to make the game hold a steady fps"): with Project Reforged's HD world, creatures, gear and effects in, the
 * 3.3.5 client's own defaults draw far more than a phone holds at an even pace. The app writes these into Wrath++'s
 * `WTF/Config.wtf` before each start ([WowClientSetup][com.logie.blizz.game.WowClientSetup]), in place of what the game
 * had, so a frame costs about the same everywhere: the frame rate held rather than chased.
 *
 * Every name and range is the 3.3.5a client's own (its Video options panels, `VideoOptionsPanels.lua`: farclip 177..1277,
 * BaseMip and TerrainMip 0..1, groundEffectDensity 16..64, groundEffectDist 70..140, environmentDetail 0.5..1.5,
 * particleDensity 0.1..1, extShadowQuality 0..4, textureFilteringMode 0..5, weatherDensity 0..3); `maxFPS` and `maxFPSBk`
 * are its console's. The frame rate itself is also held by DXVK's limiter (the launch options' frame limit, 60 for World
 * of Warcraft unless chosen otherwise), which paces each frame more evenly than the game's own wait.
 */
object WrathppGraphics {
    enum class Profile(val title: String, val detail: String) {
        STEADY("Steady (recommended)", "60 frames a second held: Reforged's HD textures at half their size (still sharper than the game's own), a shorter view, fewer ground details and particles, no shadows or full-screen glow. Your characters keep their full detail."),
        GAME("The game's own", "The app leaves the game's graphics settings as they are: what you set in the game's Video options stays."),
    }

    private const val FILE = "wrathpp-graphics"

    fun chosen(filesDir: File): Profile =
        File(filesDir, FILE).takeIf { it.isFile }?.readText()?.trim()?.let { name -> Profile.entries.firstOrNull { it.name == name } } ?: Profile.STEADY

    fun choose(filesDir: File, profile: Profile) {
        File(filesDir, FILE).writeText(profile.name + "\n")
    }

    /** The Config.wtf settings [profile] owns (none for [Profile.GAME]). */
    fun values(profile: Profile): Map<String, String> = when (profile) {
        Profile.GAME -> emptyMap()
        Profile.STEADY -> linkedMapOf(
            // the pace: the game's own cap, and in the background slower still; no vertical sync wait or triple buffer
            // (DXVK's limiter paces the frames), and no forced CPU-GPU lock-step (gxFixLag costs a frame's overlap)
            "maxFPS" to "60", "maxFPSBk" to "10", "gxVSync" to "0", "gxTripleBuffer" to "0", "gxFixLag" to "0",
            // how far and how much is drawn: a third of the view distance's range, the ground clutter at its least
            "farclip" to "477", "groundEffectDensity" to "16", "groundEffectDist" to "70", "environmentDetail" to "0.75",
            // textures: Reforged's HD ones from their second level (half the size, a quarter of the memory and bandwidth),
            // the terrain's likewise, trilinear filtering; characters at full detail (the player's own textures)
            "BaseMip" to "1", "TerrainMip" to "1", "textureFilteringMode" to "1", "componentTextureLevel" to "9",
            // effects: half the particles, light weather, no shadows, no projected textures, no full-screen glow or death
            // effect, no terrain highlights
            "particleDensity" to "0.5", "weatherDensity" to "1", "extShadowQuality" to "0", "projectedTextures" to "0",
            "ffxGlow" to "0", "ffxDeath" to "0", "specular" to "0",
        )
    }
}
