package com.logie.blizz.update

import androidx.test.core.app.ApplicationProvider
import android.content.Context
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class PatchNotesTest {
    /** GitHub's releases list as the updater reads it: descriptions as scripts/release-notes.sh writes them. */
    private val json = """[
        {"tag_name":"blizzard-build-207","name":"Blizzard 1.0.207","draft":false,"prerelease":false,
         "body":"- Character Porter: port a character into ChromieCraft.\n- Patch notes in Settings, Games.\n\nInstall Blizzard.apk on the phone; it installs over earlier releases."},
        {"tag_name":"blizzard-build-208","name":"Blizzard 1.0.208","draft":true,"prerelease":false,"body":"- A draft's note."},
        {"tag_name":"blizzard-build-206","name":"Blizzard 1.0.206","draft":false,"prerelease":false,
         "body":"Install Blizzard.apk on the phone; it installs over earlier releases."},
        {"tag_name":"blizzard-build-205","name":"Blizzard 1.0.205","draft":false,"prerelease":false,"body":"-   Spaces trimmed.   \r\n- \n"},
        {"tag_name":"realm-modules","name":"Realm modules","draft":false,"prerelease":false,"body":"- Not the app's."},
        {"tag_name":"blizzard-build-x","name":"x","draft":false,"prerelease":false,"body":"- No number."}
    ]"""

    @Test fun theNotesOfEachReleaseNewestFirst() {
        val releases = PatchNotes.parse(json, "blizzard-build")
        assertEquals(listOf(207, 205), releases.map { it.versionCode })
        assertEquals(listOf("Character Porter: port a character into ChromieCraft.", "Patch notes in Settings, Games."), releases[0].lines)
        assertEquals(listOf("Spaces trimmed."), releases[1].lines)
    }

    @Test fun aReleaseWithoutNotesAddsNothing() {
        assertEquals(emptyList<String>(), PatchNotes.lines("Install Blizzard.apk on the phone; it installs over earlier releases."))
    }

    @Test fun keptReleasesStayWhenTheListMovesOn() {
        val old = listOf(PatchNotes.Release(100, listOf("An old note.")), PatchNotes.Release(207, listOf("Before.")))
        val merged = PatchNotes.merge(old, PatchNotes.parse(json, "blizzard-build"))
        assertEquals(listOf(207, 205, 100), merged.map { it.versionCode })
        assertEquals("Character Porter: port a character into ChromieCraft.", merged[0].lines[0])
    }

    @Test fun keptInTheAppsFilesAndReadBack() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        PatchNotes.forget(context)
        PatchNotes.keep(context, json)
        assertEquals(listOf(207, 205), PatchNotes.kept.value?.map { it.versionCode })
        val file = File(context.filesDir, "patch-notes.json")
        assert(file.isFile)
        // A list without them later (offline, or fallen off the fifty) keeps what was had.
        PatchNotes.keep(context, "[]")
        assertEquals(listOf(207, 205), PatchNotes.kept.value?.map { it.versionCode })
        // Not JSON: nothing changes.
        PatchNotes.keep(context, "<html>")
        assertEquals(listOf(207, 205), PatchNotes.kept.value?.map { it.versionCode })
        // Read back from the file alone, as after the app starts again.
        val kept = PatchNotes.kept.value
        PatchNotes.forget(context)
        file.parentFile!!.mkdirs()
        PatchNotes.keep(context, json)
        assertEquals(kept, PatchNotes.kept.value)
    }
}
