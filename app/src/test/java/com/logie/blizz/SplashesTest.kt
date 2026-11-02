package com.logie.blizz

import android.graphics.Bitmap
import android.graphics.Color
import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import com.logie.blizz.game.Splashes
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/** Hold a game's art: the splash picture and logo the person picks, kept per game. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class SplashesTest {
    @get:Rule val tmp = TemporaryFolder()
    private val context get() = ApplicationProvider.getApplicationContext<android.app.Application>()

    private fun image(name: String, width: Int, height: Int): Uri {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888).apply { eraseColor(Color.RED) }
        val file = File(tmp.root, name)
        file.outputStream().use { bitmap.compress(Bitmap.CompressFormat.PNG, 100, it) }
        return Uri.fromFile(file)
    }

    @Test fun aPictureAndALogoAreKeptPerGameAndScaledDown() {
        assertNull(Splashes.file(context, "diablo", Splashes.Kind.BACKGROUND))
        assertTrue("${Splashes.lastError}", Splashes.set(context, "diablo", Splashes.Kind.BACKGROUND, image("big.png", 4000, 2500)))
        assertTrue("${Splashes.lastError}", Splashes.set(context, "diablo", Splashes.Kind.LOGO, image("logo.png", 600, 200)))
        val background = Splashes.file(context, "diablo", Splashes.Kind.BACKGROUND)
        assertNotNull(background)
        val bounds = android.graphics.BitmapFactory.Options().apply { inJustDecodeBounds = true }
        android.graphics.BitmapFactory.decodeFile(background!!.path, bounds)
        assertTrue("${bounds.outWidth}x${bounds.outHeight}", maxOf(bounds.outWidth, bounds.outHeight) <= 1920 && bounds.outWidth > bounds.outHeight)
        // Another game's splash is its own.
        assertNull(Splashes.file(context, "diablo2", Splashes.Kind.LOGO))
    }

    @Test fun theFramingIsKeptPerGameAndResetWithTheArt() {
        val context = ApplicationProvider.getApplicationContext<android.content.Context>()
        val layout = Splashes.Layout(zoom = 2.5f, panX = 0.2f, panY = -0.1f, logoCell = 6, logoScale = 1.4f)
        Splashes.setLayout(context, "diablo", layout)
        assertEquals(layout, Splashes.layout(context, "diablo"))
        assertEquals(Splashes.Layout(), Splashes.layout(context, "diablo2"))
        Splashes.clear(context, "diablo")
        assertEquals(Splashes.Layout(), Splashes.layout(context, "diablo"))
    }

    @Test fun resetGoesBackToTheBuiltInPicture() {
        Splashes.set(context, "starcraft", Splashes.Kind.BACKGROUND, image("a.png", 100, 100))
        Splashes.set(context, "starcraft", Splashes.Kind.LOGO, image("b.png", 100, 100))
        val before = Splashes.version.value
        Splashes.clear(context, "starcraft", Splashes.Kind.LOGO)
        assertNotNull(Splashes.file(context, "starcraft", Splashes.Kind.BACKGROUND))
        assertNull(Splashes.file(context, "starcraft", Splashes.Kind.LOGO))
        Splashes.clear(context, "starcraft")
        assertNull(Splashes.file(context, "starcraft", Splashes.Kind.BACKGROUND))
        assertTrue(Splashes.version.value > before)
    }

    @Test fun somethingThatIsNotAnImageChangesNothing() {
        val text = File(tmp.root, "x.txt").apply { writeText("hello") }
        assertFalse(Splashes.set(context, "diablo", Splashes.Kind.BACKGROUND, Uri.fromFile(text)))
        assertEquals(false, Splashes.file(context, "diablo", Splashes.Kind.BACKGROUND)?.exists() ?: false)
    }
}
