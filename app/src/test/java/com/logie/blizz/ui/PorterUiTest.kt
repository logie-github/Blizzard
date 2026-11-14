package com.logie.blizz.ui

import android.content.Context
import androidx.compose.ui.test.hasSetTextAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.performSemanticsAction
import androidx.compose.ui.test.performTextInput
import androidx.compose.ui.test.performTextReplacement
import com.logie.blizz.porter.ArmoryPort
import com.logie.blizz.porter.port.GearTier
import com.logie.blizz.porter.port.LevelCap
import com.logie.blizz.porter.port.PlannedPosition
import com.logie.blizz.porter.port.PortAppearance
import com.logie.blizz.porter.port.PortArea
import com.logie.blizz.porter.port.PortCharacter
import com.logie.blizz.porter.port.PortDecision
import com.logie.blizz.porter.port.PortFaction
import com.logie.blizz.porter.port.PortOptions
import com.logie.blizz.porter.port.PortOutcome
import com.logie.blizz.porter.port.PortPlan
import com.logie.blizz.porter.port.PortRealm
import com.logie.blizz.porter.port.PortReport
import com.logie.blizz.porter.port.PortResult
import com.logie.blizz.porter.port.RaceClass
import com.logie.blizz.porter.port.RealmSupport
import com.logie.blizz.porter.port.TargetSuggestion
import com.logie.blizz.wow.Realm
import org.junit.Assert.assertEquals
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

    /** A realm that answers as the engine would, without a database: what was asked of it is kept. */
    private class StandInRealm : PortSession {
        var planned: PortOptions? = null
        var applied = false
        var closed = false
        override val realm = Realm.CHROMIE
        override fun support() = RealmSupport(true)
        override fun levelCap() = LevelCap(80, 19)
        override fun scaledLevel(retailLevel: Int) = 19
        override fun combos() = listOf(RaceClass(2, 1), RaceClass(2, 3), RaceClass(2, 9), RaceClass(5, 9), RaceClass(1, 9), RaceClass(2, 6))
        override fun raceName(race: Int) = mapOf(1 to "Human", 2 to "Orc", 5 to "Undead")[race] ?: "race $race"
        override fun className(classId: Int) = mapOf(1 to "Warrior", 3 to "Hunter", 6 to "Death Knight", 9 to "Warlock")[classId] ?: "class $classId"
        override fun factionOf(race: Int) = if (race == 1) PortFaction.ALLIANCE else PortFaction.HORDE
        override fun suggest(character: PortCharacter) = TargetSuggestion(2, 9, character.gender, false, emptyList())
        override fun nameProblem(name: String) = if (name.equals("Taken", ignoreCase = true)) "A character of this realm already has that name." else null
        override fun accounts() = listOf("PLAYER", "ALT")
        override fun plan(character: PortCharacter, options: PortOptions): PortPlan {
            planned = options
            val decisions = listOf(
                PortDecision(PortArea.CHARACTER, "race and class", PortOutcome.KEPT, "Orc Warlock"),
                PortDecision(PortArea.LEVEL, "level", PortOutcome.MAPPED, "90 on retail, ${options.level} here"),
                PortDecision(PortArea.MOUNTS, "Swift Razorwing", PortOutcome.DROPPED, "not in Wrath"),
                PortDecision(PortArea.MOUNTS, "Felsteed", PortOutcome.KEPT, "the warlock's own"),
                PortDecision(PortArea.REPUTATIONS, "Orgrimmar", PortOutcome.KEPT, "Exalted"),
            )
            return PortPlan(
                realm = PortRealm.of(Realm.CHROMIE)!!, accountId = 1, account = options.account, name = options.name, race = options.race,
                classId = options.classId, gender = options.gender, level = options.level ?: 19, money = options.money ?: 0, appearance = PortAppearance(),
                position = PlannedPosition("Orgrimmar", 1, 1637, 1676f, -4315f, 61f, 0f), playerFlags = 0, atLogin = 0, exploredZones = emptyList(),
                taxiMask = emptyList(), knownTitles = emptyList(), chosenTitle = 0, ammoId = 0, items = emptyList(), spells = emptyList(), skills = emptyList(),
                reputations = emptyList(), quests = emptyList(), achievements = emptyList(), actions = emptyList(),
                report = PortReport(decisions, emptyList(), mapOf("spells" to 112, "items" to 19)), refusals = emptyList(), estimatedGuid = 7,
            )
        }
        override fun apply(plan: PortPlan): PortResult {
            applied = true
            return PortResult(7, 100, 118, plan.name)
        }
        override fun close() {
            closed = true
        }
    }

    /** The kept pages, with ChromieCraft open for porting to [realm]. */
    private inner class Porting(val realm: StandInRealm) : PorterSource by Pages() {
        override fun destinations(context: Context) = listOf(
            Destination(Realm.CHROMIE, "ChromieCraft", "Wrath+ · the main realm", null),
            Destination(Realm.REMIX, "Wrath Remix", "Wrath+ · the Remix realm", RealmSupport.REMIX_REASON),
            Destination(Realm.LEGION, "Legion", "LegionCore 7.3.5", Destinations.LATER),
        )
        override fun extras(context: Context, c: ArmoryCharacter, step: (String) -> Unit) =
            PortExtras(ArmoryPort.Extras(), listOf("Without a Battle.net key the port has no quests, achievements or titles."))
        override suspend fun openRealm(context: Context, realm: Realm, step: (String) -> Unit): PortSession = this.realm
    }

    @Before fun fresh() {
        rule.mainClock.autoAdvance = false
    }

    /**
     * Until [text] is shown, at most [timeoutMs] of real time: what an answer from off the UI thread brings (the realm's
     * name check) comes in real time, which a loaded machine (CI, 14 November 2026) takes longer than [settle] allows.
     */
    private fun awaitText(text: String, timeoutMs: Long = 10_000) {
        val end = System.currentTimeMillis() + timeoutMs
        while (System.currentTimeMillis() < end) {
            rule.mainClock.advanceTimeBy(200)
            rule.waitForIdle()
            if (rule.onAllNodesWithText(text).fetchSemanticsNodes().isNotEmpty()) return
            Thread.sleep(100)
        }
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

    @Test fun portingToChromieCraft() {
        val realm = StandInRealm()
        rule.setContent { BlizzTheme { CharacterPorter(onDismiss = {}, source = Porting(realm)) } }
        settle()
        rule.onNodeWithText("Character name").performTextInput("testhero")
        rule.onNodeWithText("Search").performClick()
        settle()
        rule.onNodeWithText("Testhero").performClick()
        settle(3000)
        rule.onNodeWithText("ChromieCraft").performSemanticsAction(SemanticsActions.OnClick)
        settle(3000)
        awaitText("Free on ChromieCraft.")
        rule.onNodeWithText("Free on ChromieCraft.").assertExists()
        rule.onNodeWithText("Level 19").assertExists()
        UiShots.saveAll("porter-port-options", rule)
        rule.onNodeWithText("See the port").performSemanticsAction(SemanticsActions.OnClick)
        settle(2000)
        assertEquals("PLAYER", realm.planned?.account)
        assertEquals(GearTier.FRESH, realm.planned?.gearTier)
        rule.onNodeWithText("Swift Razorwing").assertExists()
        UiShots.saveAll("porter-port-plan", rule)
        rule.onNodeWithText("Port to ChromieCraft").performSemanticsAction(SemanticsActions.OnClick)
        settle(2000)
        rule.onNodeWithText("Testhero is on ChromieCraft.").assertExists()
        assert(realm.applied)
        UiShots.saveAll("porter-port-done", rule)
    }

    @Test @Config(qualifiers = "w380dp-h800dp-xxhdpi") fun portingOnTheCoverScreen() {
        val realm = StandInRealm()
        rule.setContent { BlizzTheme { CharacterPorter(onDismiss = {}, source = Porting(realm)) } }
        settle()
        rule.onNodeWithText("Character name").performTextInput("testhero")
        rule.onNodeWithText("Search").performClick()
        settle()
        rule.onNodeWithText("Testhero").performClick()
        settle(3000)
        rule.onNodeWithText("ChromieCraft").performSemanticsAction(SemanticsActions.OnClick)
        settle(3000)
        awaitText("Free on ChromieCraft.")
        rule.onNodeWithText("Free on ChromieCraft.").assertExists()
        // A name the realm has: said at once, and the port can't be asked for.
        rule.onNode(hasSetTextAction() and hasText("Testhero")).performTextReplacement("Taken")
        settle(1000)
        awaitText("A character of this realm already has that name.")
        rule.onNodeWithText("A character of this realm already has that name.").assertExists()
        rule.onNodeWithText("See the port").performSemanticsAction(SemanticsActions.OnClick)
        settle(1000)
        assertEquals(null, realm.planned)
        UiShots.saveAll("porter-port-options-cover", rule)
    }
}
