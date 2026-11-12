package com.logie.blizz.warsmash

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** Warcraft III's movies on the phone's side: finding a movie's file, and reading the captions shown over it. */
class WarsmashMoviesTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun file(dir: File, path: String) = File(dir, path).apply { parentFile?.mkdirs(); writeBytes(byteArrayOf(1)) }

    @Test
    fun findsAMovieInAnyCase() {
        val game = tmp.newFolder("game")
        val movie = file(game, "MOVIES/HumanEd.MPQ")
        assertEquals(movie, WarsmashMovies.find(game, "HumanEd"))
        assertEquals(movie, WarsmashMovies.find(game, "humaned"))
        assertNull(WarsmashMovies.find(game, "OrcEd"))
    }

    @Test
    fun findsMoviesTheWindowsGameSetAside() {
        val game = tmp.newFolder("game")
        val aside = file(game, "Movies (off)/TutorialIn.mpq")
        assertEquals(aside, WarsmashMovies.find(game, "TutorialIn"))
    }

    @Test
    fun theMoviesFolderComesFirst() {
        val game = tmp.newFolder("game")
        val there = file(game, "Movies/IntroX.mpq")
        file(game, "Movies (off)/IntroX.mpq")
        assertEquals(there, WarsmashMovies.find(game, "IntroX"))
    }

    @Test
    fun noMoviesFolderNoMovie() {
        val game = tmp.newFolder("game")
        file(game, "War3.mpq")
        assertNull(WarsmashMovies.find(game, "TutorialIn"))
        assertNull(WarsmashMovies.find(File(game, "missing"), "TutorialIn"))
    }

    @Test
    fun readsCaptionsAsTheGameWritesThem() {
        val text = "00:00:01:12\t00:00:04:00\tA first line.\r\n" +
            "00:01:02:06\t00:01:05:18\tOne line<p> and the next.\r\n" +
            "not a caption\r\n" +
            "00:00:09:00\t00:00:08:00\tEnds before it starts.\r\n"
        val cues = WarsmashMovies.cues(text)
        assertEquals(2, cues.size)
        assertEquals(1.5, cues[0].start, 1e-9)
        assertEquals(4.0, cues[0].end, 1e-9)
        assertEquals("A first line.", cues[0].text)
        assertEquals(62.25, cues[1].start, 1e-9)
        assertEquals(65.75, cues[1].end, 1e-9)
        assertEquals("One line\nand the next.", cues[1].text)
    }

    @Test
    fun theCaptionShowingAtATime() {
        val cues = WarsmashMovies.cues("00:00:01:00\t00:00:02:00\tFirst\n00:00:03:00\t00:00:04:00\tSecond\n")
        assertNull(WarsmashMovies.at(cues, 0.5))
        assertEquals("First", WarsmashMovies.at(cues, 1.0)?.text)
        assertNull(WarsmashMovies.at(cues, 2.0))
        assertEquals("Second", WarsmashMovies.at(cues, 3.99)?.text)
        assertNull(WarsmashMovies.at(cues, 4.5))
    }
}
