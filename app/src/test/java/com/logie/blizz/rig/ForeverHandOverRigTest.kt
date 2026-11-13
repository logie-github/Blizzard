package com.logie.blizz.rig

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.logie.blizz.game.GameLog
import com.logie.blizz.game.GestureView
import com.logie.blizz.wowinput.WowGestureView
import com.winlator.xserver.Window
import com.winlator.xserver.WindowManager
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import java.io.File
import java.time.Duration

/**
 * World of Warcraft: Forever's hand-over from the Forever Launcher to the game, with the app's real game screen
 * ([WowGestureView]) on Winlator's own X server and real Windows programs ([XRig]; run as [XServerRigTest] is).
 *
 * The fault it holds (the phone, 12 November 2026, report 108: a black screen): for the first seconds of every session
 * the server's focused window is Wine's desktop, which is as big as the screen; the screen took that for the game, typed
 * the account's password and Enter into the launcher, and the launcher minimized itself, leaving the empty desktop
 * (black on the phone). Read on this rig with the launcher itself; here the probe stands for it, as any program that is
 * not the game.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ForeverHandOverRigTest {
    class Host : AppCompatActivity() {
        override fun onCreate(savedInstanceState: Bundle?) {
            setTheme(androidx.appcompat.R.style.Theme_AppCompat)
            super.onCreate(savedInstanceState)
        }
    }

    private val log = File(XRig.windowsDir, "inputprobe.log")
    private fun typed() = if (log.isFile) log.readLines().filter { it.contains("CHAR") || it.contains("KEYDOWN") } else emptyList()

    /** The main thread's work done as the clock runs (the view's own timers), for [ms] or until [until] holds. */
    private fun pump(ms: Long, until: () -> Boolean = { false }) {
        val end = System.currentTimeMillis() + ms
        while (System.currentTimeMillis() < end && !until()) {
            shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(200))
            Thread.sleep(200)
        }
    }

    /** The game screen as the app makes it for Forever with a launcher, told of the first window as XServerDisplayActivity tells it. */
    private fun screen(rig: XRig): WowGestureView {
        val app = RuntimeEnvironment.getApplication()
        val intent = Intent(app, Host::class.java)
            .putExtra(GestureView.EXTRA_LAUNCHER, true)
            .putExtra(GestureView.EXTRA_LOGIN_NAME, "forever@forever.local")
            .putExtra(GestureView.EXTRA_LOGIN_PASSWORD, "forever")
        val activity = Robolectric.buildActivity(Host::class.java, intent).setup().get()
        val view = WowGestureView(activity, rig.xServer) {}
        activity.setContentView(view)
        var told = false
        rig.xServer.windowManager.addOnWindowModificationListener(object : WindowManager.OnWindowModificationListener {
            override fun onMapWindow(window: Window) {
                if (!told && window.isRenderable && window.className.isNotEmpty()) {
                    told = true
                    Handler(Looper.getMainLooper()).post { view.onGameWindowShown() }
                }
            }
        })
        return view
    }

    @Test fun theLauncherIsNotTakenForTheGameAndNothingIsTypedIntoIt() {
        assumeTrue(XRig.enabled)
        XRig(600, 400).use { rig ->
            GameLog.clear()
            val view = screen(rig)
            rig.install(File(XRig.programs, "inputprobe.exe"))
            log.delete()
            // The launcher: started as the app starts Forever's (the keeper with /noframes, winhandler.exe, the program).
            rig.game("C:\\windows", "inputprobe.exe", "fixed", frames = false)
            pump(30_000) { rig.window("inputprobe") != null && log.isFile && log.readText().contains("START") }
            assertTrue("the launcher's window", rig.window("inputprobe") != null)
            // Past the login's wait (15 s) and its typing.
            pump(22_000)
            assertFalse("taken for the game:\n${GameLog.snapshot()}", GameLog.snapshot().contains("game window up"))
            assertEquals("typed into the launcher", emptyList<String>(), typed())
            // A tap is one plain left click on the launcher (its PLAY NOW is pressed by hand): here, the middle of the screen.
            val before = log.readLines().count { it.startsWith("LDOWN") || it.contains(" LDOWN") }
            view.tapAt(com.winlator.core.AppUtils.getScreenWidth() / 2f, com.winlator.core.AppUtils.getScreenHeight() / 2f)
            pump(2_500)
            val lines = log.readLines()
            assertEquals("one press:\n${lines.takeLast(8).joinToString("\n")}", before + 1, lines.count { it.contains("LDOWN") })
            assertEquals(lines.count { it.contains("LDOWN") }, lines.count { it.contains("LUP") })
            assertEquals(0, lines.count { it.contains("RDOWN") || it.contains("LDBL") })
        }
    }

    @Test fun theGamesOwnWindowHandsOverAndGetsThePassword() {
        assumeTrue(XRig.enabled)
        XRig(600, 400).use { rig ->
            GameLog.clear()
            screen(rig)
            rig.install(File(XRig.programs, "inputprobe.exe"))
            log.delete()
            rig.game("C:\\windows", "inputprobe.exe", "fixed", frames = false)
            pump(30_000) { rig.window("inputprobe") != null && log.isFile && log.readText().contains("START") }
            pump(5_000)
            assertFalse(GameLog.snapshot().contains("game window up"))
            // The launcher's PLAY NOW: the game's program (the probe under the game's name: its windows say wow.exe).
            File(XRig.programs, "inputprobe.exe").copyTo(File(XRig.windowsDir, "Wow.exe"), overwrite = true)
            rig.run("C:\\windows\\Wow.exe")
            pump(30_000) { GameLog.snapshot().contains("game window up") }
            assertTrue("handed over:\n${GameLog.snapshot()}\n${rig.describe()}", GameLog.snapshot().contains("game window up"))
            assertEquals("wow.exe", rig.xServer.windowManager.focusedWindow?.className?.lowercase())
            assertEquals(emptyList<String>(), typed())
            pump(25_000) { GameLog.snapshot().contains("login: typed") }
            pump(3_000)
            val chars = typed().filter { it.contains("CHAR") }.mapNotNull { Regex("'(.)'").find(it)?.groupValues?.get(1) }.joinToString("")
            assertTrue("the password typed into the game: '$chars'\n${GameLog.snapshot()}", chars.contains("forever"))
        }
    }
}
