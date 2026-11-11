package com.logie.blizz.ui

import android.content.Context
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performSemanticsAction
import androidx.test.core.app.ApplicationProvider
import com.logie.blizz.Games
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.importer.ImportRecord
import com.logie.blizz.importer.Outcome
import com.logie.blizz.importer.Problem
import com.logie.blizz.importer.Stage
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** The art editor, the import wizard, the controls screen and the settings, rendered (see [UiShots]). */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w360dp-h780dp-xxhdpi")
class DialogsUiTest {
    @get:Rule val rule = createComposeRule()
    private val context: Context = ApplicationProvider.getApplicationContext()

    @Before fun fresh() {
        TileSettings.load(context)
        rule.mainClock.autoAdvance = false
    }

    private fun settle(ms: Long = 3000) { rule.mainClock.advanceTimeBy(ms); rule.waitForIdle() }

    @Test fun splashEditor() {
        rule.setContent { BlizzTheme { SplashDialog(Games.find("diablo2")!!, onDismiss = {}) } }
        settle()
        rule.onNodeWithText("Home picture", ignoreCase = true).assertExists()
        UiShots.saveAll("splash-editor", rule)
    }

    @Test @Config(qualifiers = "w840dp-h780dp-xxhdpi") fun splashEditorFold() {
        rule.setContent { BlizzTheme { SplashDialog(Games.find("wow")!!, onDismiss = {}) } }
        settle()
        UiShots.saveAll("splash-editor-fold", rule)
    }

    @Test fun settingsGamesPage() {
        rule.setContent { BlizzTheme { SettingsDialog(onDismiss = {}) } }
        settle()
        rule.onNodeWithText("Games", ignoreCase = true).performClick()
        settle(500)
        rule.onNodeWithText("Legion", ignoreCase = true).assertExists()
        rule.onNodeWithText("The Frozen Throne", ignoreCase = true).assertExists()
        UiShots.saveAll("settings-games", rule)
    }

    @Test fun settingsGamesPageHasThePatchNotes() {
        val context = androidx.test.core.app.ApplicationProvider.getApplicationContext<android.content.Context>()
        com.logie.blizz.update.PatchNotes.forget(context)
        com.logie.blizz.update.PatchNotes.keep(
            context,
            """[{"tag_name":"blizzard-build-3","name":"Blizzard 1.0.3","body":"- Character Porter: bring a character from the Armory into ChromieCraft.\n- Patch notes: each update's one-line notes now show in Settings (the gear button), on the Games page.\n\nInstall Blizzard.apk."},
               {"tag_name":"blizzard-build-2","name":"Blizzard 1.0.2","body":"- Warcraft III: clicks land where you tap."},
               {"tag_name":"blizzard-build-1","name":"Blizzard 1.0.1","body":"- Diablo II starts at 800 by 600."},
               {"tag_name":"blizzard-build-0","name":"Blizzard 1.0.0","body":"- The first release."}]""",
        )
        rule.setContent { BlizzTheme { SettingsDialog(onDismiss = {}) } }
        settle()
        rule.onNodeWithText("Games", ignoreCase = true).performClick()
        settle(500)
        rule.onNodeWithText("Warcraft III: clicks land where you tap.").assertExists()
        rule.onNodeWithText("installed").assertExists()
        rule.onNodeWithText("Earlier updates (1)").assertExists()
        rule.onNodeWithText("The first release.").assertDoesNotExist()
        UiShots.saveAll("settings-games-patch-notes", rule)
    }

    @Test fun settingsForOneVersion() {
        rule.setContent { BlizzTheme { GameSettingsDialog(Games.find("wow_legion")!!, onDismiss = {}) } }
        settle()
        rule.onNodeWithText("Choose song", ignoreCase = true).assertExists()
        rule.onNodeWithText("Choose", ignoreCase = true).assertExists()
        UiShots.saveAll("settings-version", rule)
    }

    private fun record(id: String, r: ImportRecord) {
        GameImportManager.repo(context).save(r.copy(gameId = id))
        GameImportManager.refresh(context, id)
    }

    @Test fun wizardIdle() {
        record("diablo", ImportRecord("diablo"))
        rule.setContent { BlizzTheme { ImportWizard(Games.find("diablo")!!, onDismiss = {}, onPlay = {}) } }
        settle()
        UiShots.saveAll("wizard-idle", rule)
    }

    @Test fun wizardFailureWithDetails() {
        record("wow", ImportRecord("wow", stage = Stage.FAILED, outcome = Outcome.IMPORT_INCOMPLETE, problem = Problem.MISSING_SOURCE_DATA,
            message = "The World of Warcraft files weren't found. Pick the folder that holds Wow.exe and the Data folder.",
            detail = "Searched /storage/emulated/0/Download, /storage/emulated/0/Games/World of Warcraft/Data/enUS/patch-enUS-3.MPQ (missing); expected 2 of 2 required archives."))
        rule.setContent { BlizzTheme { ImportWizard(Games.find("wow")!!, onDismiss = {}, onPlay = {}) } }
        settle()
        UiShots.saveAll("wizard-failed", rule)
        rule.onNodeWithText("Details").performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.OnClick)
        settle(500)
        UiShots.saveAll("wizard-failed-details", rule)
    }

    @Test fun wizardReady() {
        record("starcraft", ImportRecord("starcraft", stage = Stage.READY))
        rule.setContent { BlizzTheme { ImportWizard(Games.find("starcraft")!!, onDismiss = {}, onPlay = {}) } }
        settle()
        UiShots.saveAll("wizard-ready", rule)
    }

    @Test fun controlsScreen() {
        rule.setContent { BlizzTheme { ControlsScreen(Games.find("diablo2")!!, onDismiss = {}) } }
        settle()
        UiShots.saveAll("controls", rule)
    }
}
