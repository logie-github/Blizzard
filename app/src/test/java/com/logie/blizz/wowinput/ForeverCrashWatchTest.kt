package com.logie.blizz.wowinput

import android.content.Intent
import android.os.Bundle
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.logie.blizz.game.GestureView
import com.winlator.widget.XServerView
import com.winlator.xserver.ScreenInfo
import com.winlator.xserver.XServer
import org.junit.Assert.assertEquals
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import java.io.File
import java.nio.file.Files
import java.time.Duration

/**
 * World of Warcraft: Forever's game screen leaves the game when the game writes a crash file (the real view, its own
 * watch and its lifecycle; [com.logie.blizz.forever.ForeverCtl.settledCrash] decides). On the desktop rig a game that had
 * written one stayed on its last frame and took no input.
 *
 * The view wants Winlator's X server, and that its native library: run as the X server rig's tests are, with
 * `BLIZZ_XRIG=1 BLIZZ_XRIG_LIB=<folder of libwinlator.so>` (tools/xrig/README.md); skipped otherwise.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ForeverCrashWatchTest {
    class Host : AppCompatActivity() {
        override fun onCreate(savedInstanceState: Bundle?) {
            setTheme(androidx.appcompat.R.style.Theme_AppCompat)
            super.onCreate(savedInstanceState)
        }
    }

    private fun idle(seconds: Long) = shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(seconds))

    private fun screen(errors: File?, onLeave: Runnable): Pair<org.robolectric.android.controller.ActivityController<Host>, WowGestureView> {
        assumeTrue("BLIZZ_XRIG=1 and BLIZZ_XRIG_LIB: Winlator's native library", System.getenv("BLIZZ_XRIG") == "1" && System.getenv("BLIZZ_XRIG_LIB") != null)
        val app = RuntimeEnvironment.getApplication()
        val intent = Intent(app, Host::class.java).apply { if (errors != null) putExtra(GestureView.EXTRA_CRASH_DIR, errors.path) }
        val controller = Robolectric.buildActivity(Host::class.java, intent).setup()
        val xServer = XServer(null, ScreenInfo(800, 600))
        xServer.renderer = XServerView(app, xServer).renderer
        val view = WowGestureView(controller.get(), xServer, onLeave)
        controller.get().setContentView(view)
        return controller to view
    }

    @Test
    fun `a crash file written while the game is up leaves the game, once`() {
        val errors = File(Files.createTempDirectory("forever").toFile(), "Errors")
        var left = 0
        val (controller, _) = screen(errors) { left++ }
        // The game runs: no folder yet, then a folder with an older crash file. Nothing happens.
        idle(10)
        assertEquals(0, left)
        errors.mkdirs()
        File(errors, "2026-11-11_Crash_1.txt").apply { writeText("old"); setLastModified(System.currentTimeMillis() - 86_400_000) }
        idle(10)
        assertEquals(0, left)
        // The game crashes: its file is there, and once it has not changed for three seconds the screen leaves.
        Thread.sleep(20)
        File(errors, "2026-11-12_Crash_2.txt").writeText("Exception: 0xC00000E5\n<ExceptionType> Security Crash\n")
        idle(2)
        assertEquals("not while the file is still fresh", 0, left)
        Thread.sleep(3_100)
        idle(4)
        assertEquals(1, left)
        idle(20)
        assertEquals("once", 1, left)
        controller.pause().stop().destroy()
    }

    @Test
    fun `the watch stops while the app is out of sight and goes on when it is back`() {
        val errors = File(Files.createTempDirectory("forever").toFile(), "Errors").apply { mkdirs() }
        var left = 0
        val (controller, _) = screen(errors) { left++ }
        controller.pause().stop()
        Thread.sleep(20)
        File(errors, "2026-11-12_Crash_3.txt").writeText("Exception")
        Thread.sleep(3_100)
        idle(10)
        assertEquals("out of sight: not looked at", 0, left)
        controller.start().resume()
        idle(4)
        assertEquals(1, left)
        controller.pause().stop().destroy()
    }

    @Test
    fun `another version of the game has no such watch`() {
        var left = 0
        val (controller, _) = screen(null) { left++ }
        idle(30)
        assertEquals(0, left)
        controller.pause().stop().destroy()
    }
}
