package com.logie.blizz.wowinput

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ScreenZonesTest {
    @Test
    fun theBottomAndTheRightEdgeAreTheActionBars() {
        // A Fold's inner screen, 2184 x 1968.
        assertTrue(ScreenZones.isActionBars(1092f, 1900f, 2184f, 1968f))
        assertTrue(ScreenZones.isActionBars(300f, 1600f, 2184f, 1968f))
        assertTrue(ScreenZones.isActionBars(2150f, 900f, 2184f, 1968f))
        // The world in the middle, the top of the screen.
        assertFalse(ScreenZones.isActionBars(1092f, 984f, 2184f, 1968f))
        assertFalse(ScreenZones.isActionBars(200f, 200f, 2184f, 1968f))
        assertFalse(ScreenZones.isActionBars(10f, 10f, 0f, 0f))
    }
}
