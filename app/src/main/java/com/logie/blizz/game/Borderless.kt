package com.logie.blizz.game

import android.content.Context
import java.io.File

/**
 * borderless.exe (tools/borderless/borderless.c, built by scripts/build-tools.sh into the app's assets): the keeper of a
 * Windows game's session. The game screen starts it first in the games' desktop (Winlator patch 0009: the `exec_wrapper`
 * extra), and it starts Winlator's winhandler.exe, which starts the game. While the game runs it
 *
 * - makes the games' desktop the one hardware input goes to: a game that locks the cursor from its start (Warcraft III) got
 *   no click and no move on the phone, because Wine reports a locked cursor's mouse without a window and its server gave
 *   that to the first desktop made, not the games';
 * - takes the title bar and frame off the game's windows and sizes them to the screen ([frames]: not for World of Warcraft
 *   or an installer), which Wine 10.10 draws itself in its desktop and has no setting against;
 * - ends the session when no program of the game's is left (winhandler.exe otherwise stays, and with it a black screen).
 *
 * Each read off Winlator's own X server run on a desktop with the same Wine (tools/xrig). Plain Kotlin apart from the asset
 * copy; unit-tested.
 */
object Borderless {
    const val ASSET = "borderless.exe"
    /** Where it lives in the games' Windows. */
    const val PATH = "C:\\windows\\borderless.exe"
    private const val NO_FRAMES = "/noframes"
    /** Its log of the session, beside it (started anew at each start): read for the reports ([GameLog.keeperLog]). */
    const val LOG = "borderless.log"

    fun logFile(containerRoot: File) = File(containerRoot, ".wine/drive_c/windows/$LOG")

    /**
     * The file the keeper keeps there for as long as a dialog box of the game's is up (an error message, a prompt: Windows'
     * own kind, which Winlator's X server cannot tell from a game's window). Set at each start of a game.
     */
    @Volatile var dialogFlag: File? = null

    fun dialogFile(containerRoot: File) = File(containerRoot, ".wine/drive_c/windows/borderless.dialog")

    /** Whether a dialog box of the game's is up now, by the keeper's word. */
    fun dialogUp(): Boolean = runCatching { dialogFlag?.exists() == true }.getOrDefault(false)

    /** Whether the game [gameId]'s windows lose their frames (the World of Warcraft clients run fullscreen; an installer wants its own frames). */
    fun frames(gameId: String?): Boolean = gameId != null && gameId != "installer" && gameId != "wow-client" && gameId != "wow" && !gameId.startsWith("wow_")

    /** What the game screen starts before winhandler.exe for [gameId] (the `exec_wrapper` extra). */
    fun command(gameId: String?): String = if (frames(gameId)) PATH else "$PATH $NO_FRAMES"

    /** Puts the program into the games' Windows at [containerRoot] (Winlator's container rootDir), over an older copy; whether it is there. */
    fun install(context: Context, containerRoot: File): Boolean {
        val target = File(containerRoot, ".wine/drive_c/windows/$ASSET")
        if (target.parentFile?.isDirectory != true) return false
        val bytes = context.assets.open(ASSET).use { it.readBytes() }
        if (target.isFile && target.length() == bytes.size.toLong() && target.readBytes().contentEquals(bytes)) return true
        target.writeBytes(bytes)
        return target.length() == bytes.size.toLong()
    }
}
