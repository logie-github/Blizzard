package com.logie.blizz.update

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class UpdaterTest {
    private val json = """[
        {"tag_name":"blizzard-build-15","name":"Blizzard 1.0.15","draft":false,"prerelease":false,"assets":[{"name":"Blizzard.apk","url":"https://api.github.com/a/15","size":200}]},
        {"tag_name":"blizzard-build-16","name":"Blizzard 1.0.16","draft":true,"prerelease":false,"assets":[{"name":"Blizzard.apk","url":"u16","size":1}]},
        {"tag_name":"blizzard-build-12","name":"Blizzard 1.0.12","draft":false,"prerelease":false,"assets":[{"name":"Blizzard.apk","url":"u12","size":1}]},
        {"tag_name":"other-build-99","name":"Other","draft":false,"prerelease":false,"assets":[{"name":"x.apk","url":"u99","size":1}]}
    ]"""

    @Test fun theNewestPublishedBuildOfThisApp() {
        val update = UpdatePicker.pick(Updater.parse(json), "blizzard-build", currentVersionCode = 12)!!
        assertEquals(15, update.versionCode)
        assertEquals("Blizzard 1.0.15", update.title)
        assertEquals("https://api.github.com/a/15", update.apk.url)
    }

    @Test fun nothingWhenUpToDate() {
        assertNull(UpdatePicker.pick(Updater.parse(json), "blizzard-build", currentVersionCode = 15))
    }
}
