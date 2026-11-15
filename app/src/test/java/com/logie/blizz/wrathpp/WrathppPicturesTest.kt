package com.logie.blizz.wrathpp

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.util.Base64

/** The creator's pictures for the app's reports ([WrathppPictures]): when they are asked for, which files go, and how. */
class WrathppPicturesTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun picturesAreAskedForUntilThoseOfThisStateWent() {
        val logs = tmp.newFolder("Logs")
        val state = WrathppPictures.state(241, "bda3d1e61828f2d9", "c9f6ca229bcab842")
        assertEquals("build 241, art bda3d1e6, looks c9f6ca22", state)
        val flag = WrathppPictures.flag(logs, state, now = 1000)
        assertNotNull(flag); assertTrue(flag!!.contains("WrathppShots = \"build 241, art bda3d1e6, looks c9f6ca22\""))
        // asked again before any went: still asked, and from the first asking's hour
        assertNotNull(WrathppPictures.flag(logs, state, now = 9000))
        assertEquals("1000", File(logs, "wrathpp-pictures-asked.txt").readLines()[1])
        WrathppPictures.markSent(logs, state)
        assertNull(WrathppPictures.flag(logs, state, now = 10_000))
        // another build's are asked for again
        assertNotNull(WrathppPictures.flag(logs, WrathppPictures.state(242, "bda3d1e6", "c9f6ca22"), now = 11_000))
    }

    @Test fun onlyTheGamesPicturesTakenSinceTheAskingGoTheNewestThree() {
        val logs = tmp.newFolder("Logs"); val shots = tmp.newFolder("Screenshots")
        assertNull(WrathppPictures.taken(logs, shots))
        fun shot(name: String, at: Long) = File(shots, name).apply { writeText(name); setLastModified(at) }
        shot("WoWScrnShot_old.jpg", 50_000)
        WrathppPictures.flag(logs, "s", now = 100_000)
        assertEquals("s" to emptyList<File>(), WrathppPictures.taken(logs, shots))
        shot("WoWScrnShot_1.jpg", 101_000); shot("WoWScrnShot_2.jpg", 102_000); shot("WoWScrnShot_3.JPG", 103_000); shot("WoWScrnShot_4.jpg", 104_000)
        shot("WoWScrnShot_5.tga", 105_000); File(shots, "folder.jpg").mkdirs()
        val (state, files) = WrathppPictures.taken(logs, shots)!!
        assertEquals("s", state)
        assertEquals(listOf("WoWScrnShot_2.jpg", "WoWScrnShot_3.JPG", "WoWScrnShot_4.jpg"), files.map { it.name })
        WrathppPictures.markSent(logs, "s")
        assertNull(WrathppPictures.taken(logs, shots))
    }

    @Test fun whatEachPictureIsOfIsWhatTheCreatorSaid() {
        val log = listOf(
            "[00:00:01.000] [INFO ] [wrathpp] creator: opened: native 0.3.0, looks' options in, undead skins in",
            "[00:00:03.000] [INFO ] [wrathpp] creator: shot 1: race and class",
            "[00:00:09.000] [INFO ] [wrathpp] creator: screen: customize",
            "[00:00:11.000] [INFO ] [wrathpp] creator: shot 2: customize",
            "[00:00:15.000] [INFO ] [wrathpp] creator: shot 3: a list",
        )
        assertEquals(listOf("race and class", "customize", "a list"), WrathppPictures.names(log))
    }

    private fun picture(body: String): String = body.substringAfter("-----BEGIN PICTURE-----\n").substringBefore("-----END PICTURE-----").replace("\n", "")

    @Test fun aPictureGoesWholeInOneIssueOrInParts() {
        val small = ByteArray(30_000) { (it * 7).toByte() }
        val one = WrathppPictures.parts("customize", "build 241", 2, 3, small)
        assertEquals(1, one.size)
        assertEquals("Wrath++ creator picture two of three, part one of one: customize (build 241)", one[0].first)
        assertTrue(one[0].second.contains("picture 2 of 3, part 1 of 1, 30000 bytes of JPEG"))
        assertTrue(one[0].second.length < 65_536)
        assertArrayEquals(small, Base64.getDecoder().decode(picture(one[0].second)))
        // every line of it short enough to read back whole
        assertTrue(one[0].second.lines().all { it.length <= 120 })

        val large = ByteArray(100_000) { (it * 31 + it / 256).toByte() }
        val three = WrathppPictures.parts("race and class", "build 241", 1, 3, large)
        assertEquals(3, three.size)
        assertTrue(three[0].first.contains("part one of three")); assertTrue(three[2].first.contains("part three of three"))
        assertTrue(three.all { it.second.length < 65_536 })
        assertArrayEquals(large, Base64.getDecoder().decode(three.joinToString("") { picture(it.second) }))
        // the parts' titles, and two pictures', differ in more than digits: the reports' queue takes titles alike but
        // for their digits for one report
        val titles = three.map { it.first } + WrathppPictures.parts("screen 2", "build 241", 2, 3, small).map { it.first } +
            WrathppPictures.parts("screen 3", "build 241", 3, 3, small).map { it.first }
        assertEquals(titles.size, titles.map { it.replace(Regex("\\d+"), "#") }.toSet().size)
    }

    @Test fun howLargeAPictureMayBe() {
        assertTrue(WrathppPictures.fits(120_000)); assertFalse(WrathppPictures.fits(140_000))
        val most = ByteArray(128_000)
        assertTrue(WrathppPictures.parts("x", "s", 1, 1, most).size <= WrathppPictures.MAX_PARTS + 1)
    }
}
