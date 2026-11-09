package com.logie.blizz.ui

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.core.app.ApplicationProvider
import com.logie.blizz.Games
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w360dp-h780dp-xxhdpi")
class ArtCropUiTest {
    @get:Rule val rule = createComposeRule()
    private val context: Context = ApplicationProvider.getApplicationContext()

    /** The first picture a cold test JVM opens fails ("Failed to create image decoder"): opened once here, so the tests' own pictures open. */
    @org.junit.Before fun warmUpTheImageDecoder() {
        val f = File(context.cacheDir, "warm.jpg")
        Bitmap.createBitmap(8, 8, Bitmap.Config.ARGB_8888).compress(Bitmap.CompressFormat.JPEG, 90, f.outputStream())
        repeat(3) { runCatching { android.graphics.BitmapFactory.decodeFile(f.path) } }
    }

    /** The picture is opened off the main thread: the clock runs until the Save button is there and on screen (a full run's load can make that slow). */
    private fun untilSaveShows() {
        rule.mainClock.autoAdvance = true
        rule.waitUntil(120_000) {
            runCatching { rule.onNodeWithText("Save", ignoreCase = true).performScrollTo().assertIsDisplayed() }.isSuccess
        }
        rule.waitForIdle()
    }

    private fun picture(w: Int, h: Int): File {
        val f = File(context.cacheDir, "crop-$w.jpg")
        Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888).apply { eraseColor(Color.RED) }.compress(Bitmap.CompressFormat.JPEG, 90, f.outputStream())
        return f
    }

    @Test fun theBoxCropCanBeSavedOnAPhone() {
        // The box's frame is tall (3:4): on a phone it used to push Save off the screen.
        rule.mainClock.autoAdvance = false
        var saved: Bitmap? = null
        rule.setContent { BlizzTheme { CropDialog("Crop · Box", picture(1600, 1200), 3f / 4f, onSave = { saved = it }, onDismiss = {}) } }
        untilSaveShows()
        rule.onNodeWithText("Save", ignoreCase = true).performScrollTo().assertIsDisplayed()
        UiShots.saveAll("modern-crop-box", rule)
        rule.onNodeWithText("Save", ignoreCase = true).performClick()
        rule.waitForIdle()
        assertNotNull(saved)
        // 3:4 of a 1600 x 1200 picture: the full height, three quarters of it wide
        assertEquals(900, saved!!.width); assertEquals(1200, saved!!.height)
    }

    @Test fun theHomeCropCanBeSavedToo() {
        rule.mainClock.autoAdvance = false
        var saved: Bitmap? = null
        rule.setContent { BlizzTheme { CropDialog("Crop · Home picture", picture(2000, 800), 1.077f, onSave = { saved = it }, onDismiss = {}) } }
        untilSaveShows()
        rule.onNodeWithText("Save", ignoreCase = true).performScrollTo().assertIsDisplayed()
        rule.onNodeWithText("Save", ignoreCase = true).performClick()
        rule.waitForIdle()
        assertNotNull(saved)
    }

    @Test fun theMusicDialogOffersChangeAndTheTrackThatPlays() {
        rule.mainClock.autoAdvance = false
        rule.setContent { BlizzTheme { MusicDialog(Games.find("diablo")!!, onDismiss = {}) } }
        rule.mainClock.advanceTimeBy(1500); rule.waitForIdle()
        rule.onNodeWithText("Change").assertIsDisplayed()
        rule.onNodeWithText("Diablo: Menu").assertIsDisplayed()
        UiShots.saveAll("modern-music", rule)
    }
}
