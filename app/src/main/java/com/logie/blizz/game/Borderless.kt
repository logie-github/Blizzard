package com.logie.blizz.game

import android.content.Context
import java.io.File

/**
 * borderless.exe (tools/borderless/borderless.c, built by scripts/build-tools.sh into the app's assets): the Windows
 * program that takes the title bar and frame off a windowed game's window and puts it at the top left at its client
 * area's size, so the picture is the whole screen. Wine 10.10 draws the bars itself in its desktop (no window manager
 * on Winlator's X server) and has no setting against it, and a game started in a window at the screen's size sat under
 * its own bar, pushed down and cut at the bottom (the phone, 9 November 2026). Run inside the games' Windows by the game
 * screen once the game's window is up ([GestureView.onGameWindowShown], through winhandler), for the games played in a
 * window; it keeps watching while the game runs and ends with the Windows. Plain Kotlin apart from the asset copy; unit-tested.
 */
object Borderless {
    const val ASSET = "borderless.exe"
    /** Where it lives in the games' Windows, and the command winhandler runs. */
    const val PATH = "C:\\windows\\borderless.exe"

    /** Whether the game [gameId] plays in a window the program should take the frame off (the World of Warcraft clients run fullscreen; an installer wants its own frames). */
    fun wanted(gameId: String?): Boolean = gameId != null && gameId != "installer" && gameId != "wow-client" && gameId != "wow" && !gameId.startsWith("wow_")

    /** Puts the program into the games' Windows at [containerRoot] (Winlator's container rootDir), over an older copy. */
    fun install(context: Context, containerRoot: File) {
        val target = File(containerRoot, ".wine/drive_c/windows/$ASSET")
        if (!target.parentFile!!.isDirectory) return
        val bytes = context.assets.open(ASSET).use { it.readBytes() }
        if (target.isFile && target.length() == bytes.size.toLong() && target.readBytes().contentEquals(bytes)) return
        target.writeBytes(bytes)
    }
}
