package com.logie.blizz.ui

import android.content.Context
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import com.logie.blizz.porter.Porter
import com.logie.blizz.porter.armory.Appearance
import com.logie.blizz.porter.armory.Armory
import com.logie.blizz.porter.armory.ArmoryCharacter
import com.logie.blizz.porter.armory.Found
import com.logie.blizz.porter.armory.Region
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** The Character Porter's screens, on the Armory's pages kept in the tests (no network), rendered (see [UiShots]). */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w900dp-h690dp-xxhdpi")
class PorterUiTest {
    @get:Rule val rule = createComposeRule()

    private fun fixture(name: String) = String(javaClass.classLoader!!.getResourceAsStream("porter/$name")!!.readBytes())

    /** The Armory's kept pages; the 3D look stays downloading (no GL here). */
    private inner class Pages : PorterSource {
        override fun search(region: Region, query: String, page: Int) = Armory.parseSearch(region, fixture("armory-search.html")) to true
        override fun character(found: Found): ArmoryCharacter = Armory.parseCharacter(found.region, fixture("armory-model.json"))
        override fun counts(c: ArmoryCharacter) = Armory.parseMounts(fixture("armory-mounts.json")).size to Armory.parseReputations(fixture("armory-reputation.json")).size
        override fun appearance(context: Context, c: ArmoryCharacter): Appearance? = null
        override fun progress(context: Context, c: ArmoryCharacter): Pair<Int, Int>? = null
        override fun prepare(context: Context, c: ArmoryCharacter, appearance: Appearance?, progress: (Porter.Step) -> Unit): Porter.Ready {
            progress(Porter.Step.Files(31, 87, 46))
            Thread.sleep(60_000)
            error("not drawn in tests")
        }
    }

    @Before fun fresh() {
        rule.mainClock.autoAdvance = false
    }

    private fun settle(ms: Long = 2000) {
        rule.mainClock.advanceTimeBy(ms)
        rule.waitForIdle()
        Thread.sleep(300)
        rule.mainClock.advanceTimeBy(500)
        rule.waitForIdle()
    }

    @Test fun searchThenACharacter() {
        rule.setContent { BlizzTheme { CharacterPorter(onDismiss = {}, source = Pages()) } }
        settle()
        rule.onNodeWithText("Character name").performTextInput("testhero")
        rule.onNodeWithText("Search").performClick()
        settle()
        rule.onNodeWithText("Testheroine").assertExists()
        rule.onAllNodesWithText("Level 80 Orc Warlock · Test Realm").fetchSemanticsNodes().let { assert(it.size == 1) }
        UiShots.saveAll("porter-search", rule)
        rule.onNodeWithText("Testhero").performClick()
        settle(3000)
        rule.onNodeWithText("Skull of the Damned Necrolyte").assertExists()
        rule.onNodeWithText("Level 90 Orc Warlock · Destruction").assertExists()
        UiShots.saveAll("porter-character", rule)
    }

    @Test @Config(qualifiers = "w380dp-h800dp-xxhdpi") fun onTheCoverScreen() {
        rule.setContent { BlizzTheme { CharacterPorter(onDismiss = {}, source = Pages()) } }
        settle()
        rule.onNodeWithText("Character name").performTextInput("testhero")
        rule.onNodeWithText("Search").performClick()
        settle()
        rule.onNodeWithText("Testhero").performClick()
        settle(3000)
        rule.onNodeWithText("Skull of the Damned Necrolyte").assertExists()
        UiShots.saveAll("porter-character-cover", rule)
    }
}
