package com.logie.blizz.wowmodules

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ModuleSourceTest {
    @Test
    fun theReleaseComesFromTheWowAppsVersion() {
        assertEquals(52, ModuleSource.versionCodeOf("1.0.52"))
        assertEquals(7, ModuleSource.versionCodeOf(" 1.0.7 "))
        assertNull(ModuleSource.versionCodeOf("1.0"))
        assertNull(ModuleSource.versionCodeOf("1.0.0"))
        assertNull(ModuleSource.versionCodeOf("1.0.x"))
        assertNull(ModuleSource.versionCodeOf(""))
        assertNull(ModuleSource.versionCodeOf(null))
        assertEquals("wow-build-52", ModuleBuild.release(ModuleSource.RELEASE_TAG_PREFIX, 52))
    }

    @Test
    fun theWorkflowAndTheReleaseAreInTheWowAppsRepository() {
        assertEquals("logie-github/YeaBwoi", ModuleSource.REPO)
        assertEquals(
            "https://api.github.com/repos/logie-github/YeaBwoi/actions/workflows/build-warcraft-modules.yml",
            ModuleSource.workflowUrl(),
        )
        assertEquals("https://api.github.com/repos/logie-github/YeaBwoi/releases/tags/wow-build-52", ModuleSource.releaseUrl("wow-build-52"))
        assertEquals("https://api.github.com/repos/logie-github/YeaBwoi/actions/runs/9", ModuleSource.runUrl(9))
        assertTrue(ModuleSource.runsUrl().endsWith("/runs?event=workflow_dispatch&per_page=30"))
    }

    @Test
    fun theRealmsOwnModulesAreSkipped() {
        val base = ModuleSource.BASE_MODULES
        assertTrue("mod-playerbots" in base)
        assertEquals(9, base.size)
        val sha = "1".repeat(40)
        val picks = listOf(
            ModuleBuild.Chosen("liyunfan1223/mod-playerbots", "master", commit = sha),
            ModuleBuild.Chosen("azerothcore/mod-transmog", "master", commit = sha),
        )
        assertEquals("azerothcore/mod-transmog@$sha", ModuleBuild.modulesInput(picks, base))
    }

    @Test
    fun readsReleaseAssets() {
        val digest = "a".repeat(64)
        val json = """
            {"tag_name": "wow-build-52", "assets": [
              {"name": "server-abc123def456.tar.xz", "url": "https://api.github.com/repos/r/releases/assets/1", "size": 93000000, "digest": "sha256:$digest"},
              {"name": "server-abc123def456.json", "url": "https://api.github.com/repos/r/releases/assets/2", "size": 120, "digest": null},
              {"name": "odd.bin", "url": "https://x/3", "size": 1, "digest": "sha256:short"},
              {"name": "", "url": "https://x/4"},
              {"name": "no-url.bin"}
            ]}
        """.trimIndent()
        val assets = ModuleSource.parseAssets(json)
        assertEquals(listOf("server-abc123def456.tar.xz", "server-abc123def456.json", "odd.bin"), assets.map { it.name })
        assertEquals(93_000_000L, assets[0].size)
        assertEquals(digest, assets[0].sha256)
        assertNull(assets[1].sha256)
        assertNull(assets[2].sha256)
        assertEquals(emptyList<Any>(), ModuleSource.parseAssets("{}"))
    }

    @Test
    fun readsTheDefaultBranch() {
        assertEquals("main", ModuleSource.parseDefaultBranch("""{"default_branch": "main"}"""))
        assertNull(ModuleSource.parseDefaultBranch("""{"default_branch": "../x"}"""))
        assertNull(ModuleSource.parseDefaultBranch("{}"))
        assertFalse(ModuleBuild.isBranch("a b"))
    }
}
