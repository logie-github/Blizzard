package com.logie.blizz.wowmodules

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.logie.blizz.wow.WowLayout
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ModuleStoreTest {
    private val context: Context get() = ApplicationProvider.getApplicationContext()
    private val sha = "1".repeat(40)

    @Before
    fun clean() {
        File(context.filesDir, "wowmodules").deleteRecursively()
        File(context.filesDir, "games").deleteRecursively()
        context.getSharedPreferences("wow_modules_github", Context.MODE_PRIVATE).edit().clear().commit()
        ModuleStore.resetForTests()
    }

    /** The imported realm: the files `WowLayout.isImported` looks for, and the export's manifest. */
    private fun importRealm(appVersion: String? = "1.0.52"): WowLayout {
        val layout = WowLayout.of(context)
        for (path in listOf("ctl.sh", "bin/worldserver", "bin/mariadbd")) {
            File(layout.server, path).also { it.parentFile!!.mkdirs() }.writeText("x")
        }
        File(layout.databases, "mysql").mkdirs()
        layout.exportDir.mkdirs()
        layout.manifest.writeText(JSONObject().apply { if (appVersion != null) put("appVersion", appVersion) }.toString())
        return layout
    }

    private fun listing(fullName: String, branch: String = "master"): ModuleCatalog.Listing =
        ModuleCatalog.listing(
            JSONObject().put("full_name", fullName).put("description", "d").put("stargazers_count", 3)
                .put("default_branch", branch).put("owner", JSONObject().put("avatar_url", "https://a/1")),
        )!!

    @Test
    fun theRealmMustBeImported() {
        assertTrue(ModuleStore.unavailableReason(context)!!.contains("isn't imported"))

        importRealm(appVersion = null)
        assertNull(ModuleStore.unavailableReason(context))
        assertEquals(ModuleSource.REALM_SOURCE, ModuleStore.versionCode(context))
        assertEquals("realm-modules", ModuleStore.release(context))
    }

    @Test
    fun thePicksAreKept() {
        ModuleStore.load(context)
        ModuleStore.add(context, listing("azerothcore/mod-transmog"))
        ModuleStore.add(context, listing("azerothcore/mod-transmog"))
        // The realm has this one already; and a branch that isn't safe is refused.
        ModuleStore.add(context, listing("liyunfan1223/mod-playerbots"))
        ModuleStore.add(context, listing("someone/mod-evil", branch = "../x"))
        assertEquals(listOf("azerothcore/mod-transmog"), ModuleStore.chosen.value.map { it.fullName })
        assertTrue(ModuleStore.isChosen("AzerothCore/Mod-Transmog"))

        ModuleStore.resetForTests()
        ModuleStore.load(context)
        assertEquals(listOf("azerothcore/mod-transmog"), ModuleStore.chosen.value.map { it.fullName })
        assertEquals("master", ModuleStore.chosen.value[0].branch)

        ModuleStore.remove(context, "azerothcore/MOD-transmog")
        assertTrue(ModuleStore.chosen.value.isEmpty())
        ModuleStore.resetForTests()
        ModuleStore.load(context)
        assertTrue(ModuleStore.chosen.value.isEmpty())
    }

    @Test
    fun theTokenStaysInThePrivatePreferences() {
        ModuleStore.load(context)
        assertFalse(ModuleStore.hasToken.value)
        assertNull(ModuleStore.token(context))
        context.getSharedPreferences("wow_modules_github", Context.MODE_PRIVATE).edit().putString("token", "ghp_secret").commit()
        ModuleStore.resetForTests()
        ModuleStore.load(context)
        assertTrue(ModuleStore.hasToken.value)
        assertEquals("ghp_secret", ModuleStore.token(context))
        // Not written into the files the screen reads.
        ModuleStore.add(context, listing("azerothcore/mod-transmog"))
        val files = File(context.filesDir, "wowmodules").walkTopDown().filter { it.isFile }.map { it.readText() }
        assertTrue(files.none { "ghp_secret" in it })
        ModuleStore.clearToken(context)
        assertFalse(ModuleStore.hasToken.value)
        assertNull(ModuleStore.token(context))
    }

    @Test
    fun theRealmInIsReadFromTheStampInServer() {
        val layout = importRealm()
        val built = ModuleBuild.Built(52, "abc123def456", listOf(ModuleBuild.Chosen("azerothcore/mod-transmog", "master", commit = sha)), 1000L)
        File(context.filesDir, "wowmodules").mkdirs()
        File(context.filesDir, "wowmodules/realm.json").writeText(ModuleBuild.builtToJson(built))

        ModuleStore.load(context)
        // The realm's own is in (no stamp): realm.json is stale, as after a game imported again.
        assertNull(ModuleStore.realm.value)

        File(layout.server, RealmPackage.STAMP).writeText(ModuleBuild.stamp(built))
        ModuleStore.syncRealm(context)
        assertEquals(built, ModuleStore.realm.value)

        File(layout.server, RealmPackage.STAMP).writeText("52:modules:zzzzzzzz9999")
        ModuleStore.syncRealm(context)
        assertNull(ModuleStore.realm.value)
    }

    @Test
    fun realmsOfOlderSourcesLoseTheirPackages() {
        importRealm()
        val modules = listOf(ModuleBuild.Chosen("azerothcore/mod-transmog", "master", commit = sha))
        val old = ModuleBuild.Built(ModuleSource.REALM_SOURCE - 1, "aaaaaaaa1111", modules, 1L, size = 100)
        val current = ModuleBuild.Built(ModuleSource.REALM_SOURCE, "bbbbbbbb2222", modules, 2L, size = 100)
        val dir = File(context.filesDir, "wowmodules").also { it.mkdirs() }
        File(dir, "realms.json").writeText(ModuleBuild.savedToJson(listOf(current, old)))
        val realms = File(dir, "realms").also { it.mkdirs() }
        File(realms, ModuleBuild.assetName("aaaaaaaa1111")).writeText("old")
        File(realms, ModuleBuild.assetName("bbbbbbbb2222")).writeText("current")
        File(realms, "server-orphan000000.tar.xz").writeText("nobody lists me")

        ModuleStore.load(context)
        val saved = ModuleStore.saved.value
        assertEquals(listOf("bbbbbbbb2222", "aaaaaaaa1111"), saved.map { it.request })
        assertEquals(100L, saved[0].size)
        assertEquals(0L, saved[1].size)
        assertTrue(ModuleStore.canPutIn(context, saved[0]))
        assertFalse(ModuleStore.canPutIn(context, saved[1]))
        assertTrue(File(realms, ModuleBuild.assetName("bbbbbbbb2222")).isFile)
        assertFalse(File(realms, ModuleBuild.assetName("aaaaaaaa1111")).exists())
        assertFalse(File(realms, "server-orphan000000.tar.xz").exists())

        ModuleStore.deleteSaved(context, "bbbbbbbb2222")
        assertEquals(listOf("aaaaaaaa1111"), ModuleStore.saved.value.map { it.request })
        assertFalse(File(realms, ModuleBuild.assetName("bbbbbbbb2222")).exists())
    }

    @Test
    fun usesAKeptRealmsModulesAsThePicks() {
        ModuleStore.load(context)
        val built = ModuleBuild.Built(
            52, "abc123def456",
            listOf(
                ModuleBuild.Chosen("azerothcore/mod-transmog", "master", commit = sha),
                ModuleBuild.Chosen("liyunfan1223/mod-playerbots", "master", commit = sha),
            ),
        )
        ModuleStore.useModules(context, built)
        assertEquals(listOf("mod-transmog"), ModuleStore.chosen.value.map { it.name })
    }

    @Test
    fun theSummaryFollowsTheState() {
        assertEquals("Needs the Wrath+ realm imported", modulesSummary(context))
        importRealm()
        assertEquals("AzerothCore modules for your realm", modulesSummary(context))
        ModuleStore.add(context, listing("azerothcore/mod-transmog"))
        assertEquals("1 module picked, not built yet", modulesSummary(context))
        ModuleStore.add(context, listing("azerothcore/mod-ah-bot"))
        assertEquals("2 modules picked, not built yet", modulesSummary(context))
        assertNotNull(ModuleStore.chosen.value.firstOrNull())
    }

    @Test
    fun launchedWorkIsRefusedWhileNothingCanBeDone() {
        // Without the realm imported, putting a build in fails with the reason; the screen shows it.
        ModuleStore.load(context)
        ModuleStore.installBuilt(context)
        val deadline = System.currentTimeMillis() + 10_000
        while (ModuleStore.work.value is ModuleStore.Work.Running && System.currentTimeMillis() < deadline) Thread.sleep(20)
        val failed = ModuleStore.work.value as ModuleStore.Work.Failed
        assertTrue(failed.message.contains("isn't imported"))
        ModuleStore.clearWork()
        assertTrue(ModuleStore.work.value is ModuleStore.Work.Idle)
    }
}
