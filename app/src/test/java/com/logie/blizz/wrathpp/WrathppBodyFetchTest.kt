package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.IOException
import java.io.InputStream

class WrathppBodyFetchTest {
    @get:Rule val tmp = TemporaryFolder()

    private val a = "a".repeat(64)
    private val b = "b".repeat(64)
    private fun manifest(sha: String, models: Int = 88) = """{"size": 1000, "sha256": "$sha", "format": 2, "models": $models, "looks": "${"c".repeat(64)}", "commit": "0123"}"""

    /** A phone's store and the release as the test says it is; [imports] counts what was taken in. */
    private inner class Phone(val published: String?, val zipSha: String = a) {
        val store: File = tmp.newFolder()
        val part = File(tmp.newFolder(), "wrathpp-body.zip.part")
        var imports = 0
        var asked = 0
        fun ensure(update: Boolean, removed: Boolean = false, installed: String? = null, models: Int = 0): String = WrathppBodyFetch.ensure(
            store, part, "https://example.invalid/r", update, removed, installed, models,
            fetchText = { url -> asked++; assertTrue(url.endsWith("/wrathpp-body.json")); published ?: throw IOException("HTTP 404") },
            download = { url, dest, progress -> assertTrue(url.endsWith("/wrathpp-body.zip")); dest.writeText("zip"); progress(3, 3) },
            sha256 = { zipSha },
            importZip = { input: InputStream -> assertEquals("zip", input.readBytes().toString(Charsets.UTF_8)); imports++; 88 },
        )
    }

    @Test fun theReleasesManifestIsRead() {
        val p = WrathppBodyFetch.parse(manifest(a.uppercase(), 92))
        assertEquals(WrathppBodyFetch.Published(1000, a, 92, "c".repeat(64)), p)
        assertTrue(runCatching { WrathppBodyFetch.parse("""{"size": 5}""") }.isFailure)
        assertTrue(runCatching { WrathppBodyFetch.parse("<html>Not Found</html>") }.isFailure)
    }

    @Test fun aPhoneWithoutAPackageTakesTheReleasesEvenWhenNothingIsRefreshed() {
        val phone = Phone(manifest(a))
        val said = phone.ensure(update = false)
        assertEquals(1, phone.imports)
        assertEquals(a, WrathppBodyFetch.ours(phone.store))
        assertTrue(said, said.startsWith("the release's aaaaaaaa taken in (88 models"))
        assertFalse(phone.part.exists())
    }

    @Test fun theReleasesOwnIsKeptUntilARefreshFindsANewerOne() {
        val phone = Phone(manifest(b), zipSha = b)
        File(phone.store, WrathppBodyFetch.MARK).writeText("$a\n")
        assertTrue(phone.ensure(update = false, installed = a, models = 88).contains("kept (not refreshed"))
        assertEquals(0, phone.asked)
        phone.ensure(update = true, installed = a, models = 88)
        assertEquals(1, phone.imports)
        assertEquals(b, WrathppBodyFetch.ours(phone.store))
        // and the one published is left alone
        val same = phone.ensure(update = true, installed = b, models = 88)
        assertEquals(1, phone.imports)
        assertTrue(same, same.endsWith("as published"))
    }

    @Test fun aPackageOfYoursStaysUnlessItHasFewerModelsThanTheReleases() {
        val phone = Phone(manifest(a, 88))
        assertTrue(phone.ensure(update = true, installed = b, models = 88).contains("yours (bbbbbbbb, 88 models), kept"))
        assertEquals(0, phone.imports)
        assertNull(WrathppBodyFetch.ours(phone.store))
        // the first packages: the ten races, the Human's three shapes
        phone.ensure(update = true, installed = b, models = 13)
        assertEquals(1, phone.imports)
    }

    @Test fun aRemovedPackageIsNotFetchedAgain() {
        val phone = Phone(manifest(a))
        assertTrue(phone.ensure(update = true, removed = true).contains("removed"))
        assertEquals(0, phone.asked)
        assertEquals(0, phone.imports)
    }

    @Test fun noReleaseABadDownloadOrABadPackageLeaveWhatIsIn() {
        val none = Phone(null)
        assertTrue(none.ensure(update = true).contains("not fetched (HTTP 404"))
        val bad = Phone(manifest(a), zipSha = b)
        val said = bad.ensure(update = true)
        assertTrue(said, said.contains("not taken in (the download didn't match its checksum)"))
        assertEquals(0, bad.imports)
        assertNull(WrathppBodyFetch.ours(bad.store))
        assertFalse(bad.part.exists())
    }

    @Test fun whatIsWanted() {
        val p = WrathppBodyFetch.Published(1, a, 88, "")
        assertTrue(WrathppBodyFetch.wanted(false, null, false, 0, p))
        assertFalse(WrathppBodyFetch.wanted(true, null, false, 0, p))
        assertFalse(WrathppBodyFetch.wanted(false, a.uppercase(), true, 88, p))
        assertTrue(WrathppBodyFetch.wanted(false, b, true, 88, p))
        assertFalse(WrathppBodyFetch.wanted(false, b, false, 88, p))
        assertTrue(WrathppBodyFetch.wanted(false, b, false, 87, p))
    }
}
