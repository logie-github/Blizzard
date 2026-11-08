package com.logie.blizz.ui

import android.content.Context
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.onRoot
import androidx.test.core.app.ApplicationProvider
import com.logie.blizz.Games
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** The modern look's screens, rendered (see [UiShots]). */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w360dp-h780dp-xxhdpi")
class ModernUiTest {
    @get:Rule val rule = createComposeRule()
    private val context: Context = ApplicationProvider.getApplicationContext()

    @Before fun modern() {
        TileSettings.load(context)
        rule.mainClock.autoAdvance = false
    }

    private fun settle(ms: Long = 3000) { rule.mainClock.advanceTimeBy(ms); rule.waitForIdle() }

    @Test fun homeOnPhone() {
        rule.setContent { Launcher() }
        settle()
        rule.onNodeWithText("Install", ignoreCase = true).assertExists()
        UiShots.save("modern-home-phone", rule.onRoot())
    }

    @Test @Config(qualifiers = "w840dp-h780dp-xxhdpi") fun homeOnFoldInnerScreen() {
        rule.setContent { Launcher() }
        settle()
        UiShots.save("modern-home-fold", rule.onRoot())
    }

    @Test @Config(qualifiers = "w840dp-h780dp-xxhdpi") fun worldOfWarcraftOnFoldInnerScreen() {
        rule.setContent { BlizzTheme { ModernHome(0, Games.find("wow")!!, onSelect = {}, onPlay = {}, onChooseApp = {}) } }
        settle()
        rule.onNodeWithText("Legion", ignoreCase = true).assertExists()
        UiShots.save("modern-home-fold-wow", rule.onRoot())
    }

    @Test @Config(qualifiers = "w360dp-h780dp-xxhdpi") fun worldOfWarcraftOnPhone() {
        rule.setContent { BlizzTheme { ModernHome(0, Games.find("wow")!!, onSelect = {}, onPlay = {}, onChooseApp = {}) } }
        settle()
        UiShots.save("modern-home-phone-wow", rule.onRoot())
    }

    @Test fun holdMenu() {
        rule.setContent { BlizzTheme { HoldMenu(Games.find("wow")!!, onDismiss = {}) } }
        settle()
        UiShots.saveAll("modern-hold-menu", rule)
    }

    @Test fun launchOptions() {
        rule.setContent { BlizzTheme { GameOptionsDialog(Games.find("starcraft")!!, onDismiss = {}) } }
        settle()
        UiShots.saveAll("modern-launch-options", rule)
    }

    @Test fun settings() {
        rule.setContent { BlizzTheme { SettingsDialog(onDismiss = {}) } }
        settle()
        UiShots.saveAll("modern-settings", rule)
    }

    @Test fun addons() {
        rule.setContent { BlizzTheme { WowAddonManager("wow", onDismiss = {}) } }
        settle()
        UiShots.saveAll("modern-addons", rule)
    }

    @Test fun modules() {
        rule.setContent { BlizzTheme { WowModuleManager(onDismiss = {}) } }
        settle()
        UiShots.saveAll("modern-modules", rule)
    }

    @Test fun importWizard() {
        rule.setContent { BlizzTheme { ImportWizard(Games.find("diablo")!!, onDismiss = {}, onPlay = {}) } }
        settle()
        UiShots.saveAll("modern-wizard", rule)
    }

    @Test fun theMenusItemsOpenWhatTheySay() {
        rule.setContent { Launcher() }
        settle()
        rule.onNodeWithContentDescription("More").performClick()
        settle(500)
        rule.onNodeWithText("Launch options").performClick()
        settle(500)
        rule.onNodeWithText("Safe mode", ignoreCase = true).assertExists()
    }

    @Test fun theMenusArtOpensEveryPicture() {
        rule.setContent { Launcher() }
        settle()
        rule.onNodeWithContentDescription("More").performClick()
        settle(500)
        rule.onNodeWithText("Art").performClick()
        settle(500)
        rule.onNodeWithText("Box").assertExists()
        rule.onNodeWithText("Home picture").assertExists()
        rule.onNodeWithText("Loading picture").assertExists()
        rule.onNodeWithText("Box").assertExists()
        rule.onNodeWithText("Logo").assertExists()
        UiShots.saveAll("modern-art", rule)
    }

    @Test fun settingsHaveASteamGridKeyCard() {
        rule.setContent { BlizzTheme { SettingsDialog(onDismiss = {}) } }
        settle()
        rule.onNodeWithText("API key").assertExists()
        UiShots.saveAll("modern-settings-steamgrid", rule)
    }
}
