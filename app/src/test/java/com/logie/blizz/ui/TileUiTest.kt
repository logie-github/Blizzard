package com.logie.blizz.ui

import android.content.Context
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.test.center
import androidx.compose.ui.test.down
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.longClick
import androidx.compose.ui.test.moveTo
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.performSemanticsAction
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.up
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** The tile layout rendered under Robolectric, driven like a person, with screenshots (see [UiShots]). */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w360dp-h1700dp-xxhdpi")
class TileUiTest {
    @get:Rule val rule = createComposeRule()
    private val context: Context = ApplicationProvider.getApplicationContext()

    @Before fun fresh() {
        TileSettings.load(context)
        TileSettings.reset(context)
        TileSettings.setMode(context, TileSettings.Mode.TILES)
        rule.mainClock.autoAdvance = false
    }

    private fun show() {
        rule.setContent { BlizzTheme { TileScreen(onOpen = {}) } }
        settle()
    }

    private fun settle(ms: Long = 3000) { rule.mainClock.advanceTimeBy(ms); rule.waitForIdle() }

    @Test fun twoColumnsWideAlone() {
        TileSettings.setColumns(context, 2); TileSettings.setWide(context, "wow", true)
        show()
        UiShots.saveAll("tiles-2col-wide-alone", rule)
    }

    @Test fun threeColumnsWideMixed() {
        TileSettings.setColumns(context, 3); TileSettings.setWide(context, "wow", true)
        TileSettings.setOrder(context, listOf("wow", "diablo"))
        show()
        UiShots.saveAll("tiles-3col-wide-mixed", rule)
    }

    @Test fun threeColumnsWideAlone() {
        TileSettings.setColumns(context, 3); TileSettings.setWide(context, "wow", true)
        TileSettings.setOrder(context, listOf("diablo", "diablo2", "starcraft", "starcraft2", "warcraft", "warcraft2", "warcraft3_roc", "warcraft3_tft", "wow"))
        show()
        UiShots.saveAll("tiles-3col-wide-alone", rule)
    }

    @Test fun fourColumnsWideMixed() {
        TileSettings.setColumns(context, 4); TileSettings.setWide(context, "wow", true)
        TileSettings.setOrder(context, listOf("diablo", "wow", "diablo2"))
        show()
        UiShots.saveAll("tiles-4col-wide-mixed", rule)
    }

    @Test fun fourColumnsAllTall() {
        TileSettings.setColumns(context, 4)
        show()
        UiShots.saveAll("tiles-4col-tall", rule)
    }

    @Test fun holdMenuAndRearrangeAndDrag() {
        TileSettings.setColumns(context, 2)
        show()
        rule.onNodeWithContentDescription("Diablo").performTouchInput { longClick() }
        settle(500)
        for (item in listOf("Change Art", "Rearrange", "Reinstall", "Loading screen")) rule.onNodeWithText(item).assertExists()
        UiShots.saveAll("tiles-hold-menu", rule)

        rule.onNodeWithText("Rearrange").performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.OnClick)
        settle(800)
        println("DEBUG roots=" + rule.onAllNodes(androidx.compose.ui.test.isRoot()).fetchSemanticsNodes().size + " rearrange=" + rule.onAllNodesWithText("Rearrange").fetchSemanticsNodes().size + " hold=" + rule.onAllNodesWithText("Hold a tile, then drag it").fetchSemanticsNodes().size + " done=" + rule.onAllNodesWithText("Done").fetchSemanticsNodes().size)
        rule.onNodeWithText("Done", ignoreCase = true).assertExists()
        UiShots.saveAll("tiles-rearrange", rule)

        val before = TileSettings.state.value.order
        // Hold the first tile, drag it onto the fourth, let go.
        val target = rule.onNodeWithContentDescription("StarCraft II").fetchSemanticsNode().boundsInRoot.center
        val start = rule.onNodeWithContentDescription("Diablo").fetchSemanticsNode().boundsInRoot.center
        rule.onNodeWithContentDescription("Diablo").performTouchInput { down(center) }
        rule.mainClock.advanceTimeBy(900)
        rule.onNodeWithContentDescription("Diablo").performTouchInput { moveTo(center + Offset(10f, 10f)) }
        rule.mainClock.advanceTimeBy(50)
        rule.onNodeWithContentDescription("Diablo").performTouchInput { moveTo(center + (target - start)) }
        rule.mainClock.advanceTimeBy(200)
        UiShots.saveAll("tiles-dragging", rule)
        rule.onNodeWithContentDescription("Diablo").performTouchInput { up() }
        settle(1000)
        val after = TileSettings.state.value.order
        println("order before=$before after=$after")
        assertNotEquals(before, after)
        assertTrue(after.indexOf("diablo") > after.indexOf("diablo2"))
        UiShots.saveAll("tiles-after-drag", rule)
    }

    @Test fun changeArtDialog() {
        TileSettings.setColumns(context, 2); TileSettings.setWide(context, "wow", true)
        show()
        rule.onNodeWithContentDescription("World of Warcraft").performTouchInput { longClick() }
        settle(500)
        rule.onNodeWithText("Change Art").performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.OnClick)
        settle(800)
        rule.onNodeWithText("Choose picture", ignoreCase = true).assertExists()
        UiShots.saveAll("tiles-change-art", rule)
    }

    @Test fun settingsDialog() {
        TileSettings.setColumns(context, 3)
        rule.setContent { BlizzTheme { SettingsDialog(onDismiss = {}) } }
        settle()
        println("DEBUG settings roots=" + rule.onAllNodes(androidx.compose.ui.test.isRoot()).fetchSemanticsNodes().size)
        rule.onNodeWithText("Reset tile layout", ignoreCase = true).assertExists()
        UiShots.saveAll("settings", rule)
    }

    @Test fun launcherInTileMode() {
        TileSettings.setColumns(context, 3)
        rule.setContent { Launcher(fold = null) }
        settle()
        UiShots.saveAll("launcher-tiles-3col", rule)
    }
}
