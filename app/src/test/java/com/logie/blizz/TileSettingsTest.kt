package com.logie.blizz.ui

import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class TileSettingsTest {
    private val context get() = ApplicationProvider.getApplicationContext<android.app.Application>()

    @Test fun theChoicesAreKeptAndLoadedAgain() {
        TileSettings.setMode(context, TileSettings.Mode.TILES)
        TileSettings.setOrder(context, listOf("wow", "diablo"))
        TileSettings.setWide(context, "wow", true)
        TileSettings.setColumns(context, 3)
        TileSettings.load(context)
        val s = TileSettings.state.value
        assertEquals(TileSettings.Mode.TILES, s.mode)
        assertEquals(listOf("wow", "diablo"), s.order)
        assertTrue("wow" in s.wide)
        assertEquals(3, s.columns)
        TileSettings.setWide(context, "wow", false)
        assertTrue("wow" !in TileSettings.state.value.wide)
    }

    @Test fun resetPutsTheTilesBackButKeepsTheMode() {
        TileSettings.setMode(context, TileSettings.Mode.TILES)
        TileSettings.setOrder(context, listOf("b", "a"))
        TileSettings.setColumns(context, 5)
        TileSettings.reset(context)
        val s = TileSettings.state.value
        assertEquals(TileSettings.Mode.TILES, s.mode)
        assertTrue(s.order.isEmpty() && s.wide.isEmpty())
        assertEquals(0, s.columns)
    }

    @Test fun columnsStayInRange() {
        TileSettings.setColumns(context, 99)
        assertEquals(TileLayout.MAX_COLUMNS, TileSettings.state.value.columns)
        TileSettings.setColumns(context, -4)
        assertEquals(0, TileSettings.state.value.columns)
    }
}
