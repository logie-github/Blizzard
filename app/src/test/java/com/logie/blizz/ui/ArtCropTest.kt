package com.logie.blizz.ui

import android.graphics.Bitmap
import android.graphics.Color
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ArtCropTest {
    @Test fun theFrameHoldsTheMostOfThePictureAtZoomOne() {
        // a wide picture, a portrait frame: the full height, a slice of the width
        val r = CropMath.rect(2000, 1000, 3f / 4f, 1f, 1000f, 500f)
        assertEquals(1000, r.h); assertEquals(750, r.w); assertEquals(625, r.x); assertEquals(0, r.y)
        // a tall picture, a wide frame: the full width
        val t = CropMath.rect(1000, 2000, 2f, 1f, 500f, 1000f)
        assertEquals(1000, t.w); assertEquals(500, t.h); assertEquals(750, t.y)
    }

    @Test fun zoomingInShowsLessAndThePanStaysInsideThePicture() {
        val z = CropMath.rect(2000, 1000, 1f, 2f, 1000f, 500f)
        assertEquals(500, z.w); assertEquals(500, z.h)
        // pushed past every edge: held at the edge
        val left = CropMath.rect(2000, 1000, 1f, 2f, -5000f, -5000f)
        assertEquals(0, left.x); assertEquals(0, left.y)
        val right = CropMath.rect(2000, 1000, 1f, 2f, 9000f, 9000f)
        assertEquals(1500, right.x); assertEquals(500, right.y)
        // the zoom is held between one and the most
        assertEquals(CropMath.rect(2000, 1000, 1f, 1f, 0f, 0f).w, CropMath.rect(2000, 1000, 1f, 0.2f, 0f, 0f).w)
        assertTrue(CropMath.rect(2000, 1000, 1f, 99f, 0f, 0f).w >= 1)
    }

    @Test fun aChosenPictureIsKeptWhole() {
        val context = ApplicationProvider.getApplicationContext<android.app.Application>()
        val source = File(context.cacheDir, "t.png")
        Bitmap.createBitmap(300, 200, Bitmap.Config.ARGB_8888).apply { eraseColor(Color.RED) }.compress(Bitmap.CompressFormat.PNG, 100, source.outputStream())
        val kept = ArtSources.stage(context, "diablo", "box", android.net.Uri.fromFile(source))
        assertNotNull(kept)
        assertEquals(kept, ArtSources.file(context, "diablo", "box"))
        val read = android.graphics.BitmapFactory.decodeFile(kept!!.path)
        assertEquals(300, read.width); assertEquals(200, read.height)
        ArtSources.clear(context, "diablo", "box")
        assertNull(ArtSources.file(context, "diablo", "box"))
        assertNull(ArtSources.stage(context, "diablo", "box", android.net.Uri.fromFile(File(context.cacheDir, "missing.png"))))
    }
}
