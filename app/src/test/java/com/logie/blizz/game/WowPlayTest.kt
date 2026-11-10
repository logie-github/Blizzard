package com.logie.blizz.game

import android.content.Context
import com.logie.blizz.importer.LibraryEntry
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
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

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WowPlayTest {
    @get:Rule val tmp = TemporaryFolder()

    private class Fake(var result: RealmControl.Status) : RealmControl {
        override val status: StateFlow<RealmControl.Status> = MutableStateFlow(RealmControl.Status(RealmControl.Phase.STARTING, "Loading", 0.5f))
        override fun start(context: Context, realm: String) = Unit
        override suspend fun awaitUp(timeoutMs: Long) = result
        override fun chosenRealm(context: Context) = "main"
    }

    private fun root(withClient: Boolean = true): File = tmp.newFolder("wow").also {
        if (withClient) {
            File(it, "files/client/Data/enUS").mkdirs(); File(it, "files/client/Wow.exe").writeText("MZ")
        }
        File(it, ".export/prefs").mkdirs()
        File(it, ".export/prefs/login.json").writeText("""{"name":{"type":"string","value":"ME"}}""")
    }

    private fun env(root: File, fake: Fake, started: MutableList<String>, launched: MutableList<LibraryEntry>) = WowPlay.Environment(
        root = root, realm = fake, size = 1920 to 864, start = { started += it }, chosenRealm = { "main" },
        launch = { launched += it }, report = { }, timeoutMs = 1000,
    )

    @Test fun theClientStartsOnceTheRealmIsUp() = runBlocking {
        val root = root(); val started = mutableListOf<String>(); val launched = mutableListOf<LibraryEntry>()
        assertNull(WowPlay.prepare(env(root, Fake(RealmControl.Status(RealmControl.Phase.UP)), started, launched)))
        assertEquals(listOf("main"), started)
        val e = launched.single()
        assertEquals("wow-client", e.gameId); assertEquals("Wow.exe", e.executable); assertEquals("wow", e.controlProfile)
        assertEquals(File(root, "files/client").path, e.installPath)
        assertEquals("set realmlist 127.0.0.1\r\n", File(root, "files/client/Data/enUS/realmlist.wtf").readText())
        assertTrue(File(root, "files/client/WTF/Config.wtf").readText().contains("SET accountName \"ME\""))
    }

    @Test fun aRealmThatFailsStopsTheStart() = runBlocking {
        val launched = mutableListOf<LibraryEntry>()
        val message = WowPlay.prepare(env(root(), Fake(RealmControl.Status(RealmControl.Phase.FAILED, error = "no mysql")), mutableListOf(), launched))
        assertEquals("no mysql", message); assertTrue(launched.isEmpty())
    }

    @Test fun aRealmStillLoadingAtTheTimeoutIsReported() = runBlocking {
        val message = WowPlay.prepare(env(root(), Fake(RealmControl.Status(RealmControl.Phase.STARTING)), mutableListOf(), mutableListOf()))
        assertNotNull(message)
    }

    @Test fun noClientIsSaidBeforeAnythingStarts() = runBlocking {
        val started = mutableListOf<String>()
        val message = WowPlay.prepare(env(root(withClient = false), Fake(RealmControl.Status(RealmControl.Phase.UP)), started, mutableListOf()))
        assertTrue(message!!.contains("Wow.exe")); assertTrue(started.isEmpty())
    }
    // Wrath++ (docs/wrathpp): set up first, then its own realm and its own copy of the game; Wrath+'s game untouched.

    private fun wrathppEnv(root: File, fake: Fake, started: MutableList<String>, launched: MutableList<LibraryEntry>, setUp: ((String, Float?) -> Unit) -> Unit) =
        WowPlay.Environment(
            root = root, realm = fake, size = 1920 to 864, start = { started += it }, chosenRealm = { "wrathpp" },
            launch = { launched += it }, report = { }, timeoutMs = 1000, wrathpp = true, setUpWrathpp = setUp,
        )

    @Test fun wrathppPlaysItsOwnRealmOnItsOwnCopyOfTheGame() = runBlocking {
        val root = root(); val started = mutableListOf<String>(); val launched = mutableListOf<LibraryEntry>()
        val wrathConfigBefore = File(root, "files/client/WTF/Config.wtf").exists()
        val message = WowPlay.prepare(wrathppEnv(root, Fake(RealmControl.Status(RealmControl.Phase.UP)), started, launched) { _ ->
            // (what WrathppSetup does: its copy of the game made from Wrath+'s)
            com.logie.blizz.wrathpp.WrathppClient.make(File(root, "files/client"), File(root, "files/client-wrathpp"))
        })
        assertNull(message)
        assertEquals(listOf("wrathpp"), started)
        assertEquals(File(root, "files/client-wrathpp").path, launched.single().installPath)
        assertTrue(File(root, "files/client-wrathpp/WTF/Config.wtf").readText().contains("SET realmName \"Wrath++\""))
        assertEquals("set realmlist 127.0.0.1\r\n", File(root, "files/client-wrathpp/Data/enUS/realmlist.wtf").readText())
        // Wrath+'s game and its realm record are as they were.
        assertEquals(wrathConfigBefore, File(root, "files/client/WTF/Config.wtf").exists())
        assertTrue(!File(root, "files/client-realm").exists())
        assertEquals("wrathpp\n", File(root, "files/client-wrathpp/client-realm").readText())
    }

    @Test fun wrathppSaysWhySetUpFailedAndStartsNothing() = runBlocking {
        val started = mutableListOf<String>()
        val message = WowPlay.prepare(wrathppEnv(root(), Fake(RealmControl.Status(RealmControl.Phase.UP)), started, mutableListOf()) { _ ->
            throw java.io.IOException("Wrath++'s server couldn't be fetched (offline)")
        })
        assertEquals("Wrath++'s server couldn't be fetched (offline)", message)
        assertTrue(started.isEmpty())
    }

    @Test fun wrathppNeedsWrathPlusImported() = runBlocking {
        val started = mutableListOf<String>(); var setUp = false
        val message = WowPlay.prepare(wrathppEnv(root(withClient = false), Fake(RealmControl.Status(RealmControl.Phase.UP)), started, mutableListOf()) { _ -> setUp = true })
        assertTrue(message!!.contains("Import World of Warcraft (Wrath+) first"))
        assertTrue(started.isEmpty()); assertTrue(!setUp)
    }
}
