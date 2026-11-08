package com.logie.blizz.ui

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w360dp-h780dp-xxhdpi")
class ShelfUiTest {
    @get:Rule val rule = createComposeRule()

    /** These are the classic look's screens (the shelf and the tiles). */
    @org.junit.Before fun classic() { Look.set(androidx.test.core.app.ApplicationProvider.getApplicationContext(), false) }
    @org.junit.After fun modern() { Look.set(androidx.test.core.app.ApplicationProvider.getApplicationContext(), true) }

    @Test fun shelfOnPhone() {
        rule.mainClock.autoAdvance = false
        rule.setContent { Launcher(fold = null) }
        rule.mainClock.advanceTimeBy(3000)
        UiShots.save("shelf-phone", rule.onRoot())
    }

    @Test @Config(qualifiers = "w840dp-h780dp-xxhdpi") fun shelfOnFoldInnerScreen() {
        rule.mainClock.autoAdvance = false
        rule.setContent { Launcher(fold = null) }
        rule.mainClock.advanceTimeBy(3000)
        UiShots.save("shelf-fold-inner", rule.onRoot())
    }

    @Test @Config(qualifiers = "w840dp-h780dp-xxhdpi") fun tilesOnFoldInnerScreen() {
        val context = androidx.test.core.app.ApplicationProvider.getApplicationContext<android.content.Context>()
        TileSettings.load(context); TileSettings.reset(context)
        TileSettings.setMode(context, TileSettings.Mode.TILES)
        TileSettings.setWide(context, "wow", true)
        TileSettings.setOrder(context, listOf("diablo", "wow"))
        rule.mainClock.autoAdvance = false
        rule.setContent { Launcher(fold = null) }
        rule.mainClock.advanceTimeBy(3000)
        UiShots.save("tiles-fold-inner", rule.onRoot())
        TileSettings.setMode(context, TileSettings.Mode.SHELF)
    }
}
