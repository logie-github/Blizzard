package com.logie.blizz

import android.app.Application
import android.graphics.Bitmap
import android.graphics.Canvas
import androidx.activity.ComponentActivity
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithContentDescription
import androidx.compose.ui.test.onFirst
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.unit.dp
import com.logie.blizz.ui.Fold
import com.logie.blizz.ui.Launcher
import java.io.File
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Pictures of the launcher (build/reports/previews) on a Fold's screens. The sizes are close to the
 * Fold's, not exact: the cover screen about 411x960dp, the inner screen about 840x750dp.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34], application = Application::class)
class PreviewTest {
    @get:Rule val compose = createAndroidComposeRule<ComponentActivity>()

    private fun screenshot(name: String) {
        compose.mainClock.advanceTimeBy(3000)
        compose.waitForIdle()
        compose.runOnIdle {
            val view = compose.activity.window.decorView
            val bitmap = Bitmap.createBitmap(view.width, view.height, Bitmap.Config.ARGB_8888)
            view.draw(Canvas(bitmap))
            val output = File("build/reports/previews/$name.jpg")
            output.parentFile!!.mkdirs()
            output.outputStream().use { bitmap.compress(Bitmap.CompressFormat.JPEG, 88, it) }
        }
    }

    private fun open(title: String) {
        compose.mainClock.advanceTimeBy(3000)
        compose.onAllNodesWithContentDescription(title).onFirst().performScrollTo().performClick()
    }

    @Config(qualifiers = "w411dp-h960dp-xxhdpi")
    @Test fun coverShelf() {
        compose.setContent { Launcher(fold = null) }
        screenshot("cover-shelf")
    }

    @Config(qualifiers = "w411dp-h960dp-xxhdpi")
    @Test fun coverShelfBottom() {
        compose.setContent { Launcher(fold = null) }
        compose.mainClock.advanceTimeBy(3000)
        compose.onAllNodesWithContentDescription("World of Warcraft: Wrath+").onFirst().performScrollTo()
        screenshot("cover-shelf-bottom")
    }

    @Config(qualifiers = "w411dp-h960dp-xxhdpi")
    @Test fun coverGame() {
        compose.setContent { Launcher(fold = null) }
        open("World of Warcraft: Wrath+")
        screenshot("cover-game")
    }

    @Config(qualifiers = "w891dp-h411dp-xxhdpi")
    @Test fun diabloSplash() {
        compose.setContent { com.logie.blizz.ui.BlizzTheme { com.logie.blizz.game.Loading("diablo", "Starting…") } }
        screenshot("splash-diablo")
    }

    @Config(qualifiers = "w840dp-h750dp-xxhdpi")
    @Test fun diabloSplashInner() {
        compose.setContent { com.logie.blizz.ui.BlizzTheme { com.logie.blizz.game.Loading("diablo", "Starting…") } }
        screenshot("splash-diablo-inner")
    }

    @Config(qualifiers = "w891dp-h411dp-xxhdpi")
    @Test fun diablo2Splash() {
        compose.setContent { com.logie.blizz.ui.BlizzTheme { com.logie.blizz.game.Loading("diablo2", "Starting…") } }
        screenshot("splash-diablo2")
    }

    @Config(qualifiers = "w840dp-h750dp-xxhdpi")
    @Test fun diablo2SplashInner() {
        compose.setContent { com.logie.blizz.ui.BlizzTheme { com.logie.blizz.game.Loading("diablo2", "Starting…") } }
        screenshot("splash-diablo2-inner")
    }

    @Config(qualifiers = "w840dp-h750dp-xxhdpi")
    @Test fun inner() {
        compose.setContent { Launcher(fold = null) }
        screenshot("inner")
    }

    @Config(qualifiers = "w840dp-h750dp-xxhdpi")
    @Test fun innerChosen() {
        compose.setContent { Launcher(fold = null) }
        open("StarCraft II")
        screenshot("inner-chosen")
    }

    @Config(qualifiers = "w750dp-h840dp-xxhdpi")
    @Test fun innerUpright() {
        compose.setContent { Launcher(fold = null) }
        screenshot("inner-upright")
    }

    @Config(qualifiers = "w840dp-h750dp-xxhdpi")
    @Test fun innerTabletop() {
        compose.setContent { Launcher(fold = Fold(vertical = false, halfOpen = true, start = 365.dp, end = 385.dp)) }
        screenshot("inner-tabletop")
    }
}
