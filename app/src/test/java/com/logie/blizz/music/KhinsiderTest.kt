package com.logie.blizz.music

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class KhinsiderTest {
    private val publisher = """
        <html><body><div id="pageContent"><table class="albumList">
        <tr><th>&nbsp;</th><th>Album</th><th>Platforms</th><th>Year</th></tr>
        <tr>
          <td class="albumIcon"><a href="/game-soundtracks/album/diablo-1"><img src="https://jetta.vgmtreasurechest.com/soundtracks/diablo-1/thumbs_small/cover.jpg"></a></td>
          <td><a href="/game-soundtracks/album/diablo-1">Diablo</a></td><td>Windows</td><td>1996</td></tr>
        <tr>
          <td class="albumIcon"><a href="/game-soundtracks/album/diablo-ii-original-soundtrack"><img src="https://nu.vgmtreasurechest.com/soundtracks/d2/thumbs_small/c.png"></a></td>
          <td><a href="/game-soundtracks/album/diablo-ii-original-soundtrack">Diablo II &amp; Lord of Destruction</a></td><td>Windows</td><td>2000</td></tr>
        <tr><td><a href="/game-soundtracks/browse/B">Browse B</a></td><td><a href="/game-soundtracks/album/diablo-1/01%20Menu.mp3">a song page</a></td></tr>
        <tr><td><a href="https://evil.example/x"><img src="https://evil.example/a.jpg"></a></td></tr>
        </table></div></body></html>"""

    @Test fun theAlbumsOfAPublisherPageAreFound() {
        val albums = Khinsider.parseAlbums(publisher)
        assertEquals(listOf("diablo-1", "diablo-ii-original-soundtrack"), albums.map { it.slug })
        assertEquals("Diablo", albums[0].title)
        assertEquals("Diablo II & Lord of Destruction", albums[1].title)
        assertEquals("https://downloads.khinsider.com/game-soundtracks/album/diablo-1", albums[0].url)
        assertEquals("https://jetta.vgmtreasurechest.com/soundtracks/diablo-1/thumbs_small/cover.jpg", albums[0].thumb)
    }

    private val album = """
        <html><head><title>Diablo (Windows) Soundtrack - Download</title></head><body><div id="pageContent">
        <h2>Diablo</h2>
        <div class="albumImage"><a href="https://jetta.vgmtreasurechest.com/soundtracks/diablo-1/cover.jpg"><img src="https://jetta.vgmtreasurechest.com/soundtracks/diablo-1/thumbs/cover.jpg"></a></div>
        <table id="songlist">
         <tr id="songlist_header"><th>&nbsp;</th><th>CD</th><th>#</th><th>Song Name</th><th>Time</th><th>MP3</th><th>FLAC</th></tr>
         <tr><td><img src="/x.png"></td><td align="right">1</td><td align="right">1.</td>
           <td class="clickable-row"><a href="/game-soundtracks/album/diablo-1/01%2520Menu.mp3">Menu</a></td>
           <td class="clickable-row" align="right"><a href="/x">3:36</a></td><td class="clickable-row" align="right"><a href="/x">5.40 MB</a></td></tr>
         <tr><td></td><td align="right">1</td><td align="right">2.</td>
           <td class="clickable-row"><a href="/game-soundtracks/album/diablo-1/02%2520Tristram.mp3">Tristram &amp; Cathedral</a></td>
           <td class="clickable-row" align="right"><a href="/x">1:02:03</a></td><td><a href="/x">120.5 MB</a></td></tr>
         <tr id="songlist_footer"><td></td><td></td><td></td><td><b>Total:</b></td><td><b>4:38</b></td></tr>
        </table></div></body></html>"""

    @Test fun anAlbumPageGivesItsNameCoverAndSongs() {
        val page = Khinsider.parseAlbum(album, "https://downloads.khinsider.com/game-soundtracks/album/diablo-1")
        assertEquals("Diablo", page.title)
        assertEquals("https://jetta.vgmtreasurechest.com/soundtracks/diablo-1/thumbs/cover.jpg", page.cover)
        assertEquals(page.songs.joinToString { it.title + "@" + it.number }, 2, page.songs.size)
        val first = page.songs[0]
        assertEquals(1, first.number); assertEquals("Menu", first.title); assertEquals("3:36", first.length); assertEquals(216, first.seconds); assertEquals("5.40 MB", first.size)
        assertEquals("https://downloads.khinsider.com/game-soundtracks/album/diablo-1/01%2520Menu.mp3", first.pageUrl)
        assertEquals(2, page.songs[1].number); assertEquals("Tristram & Cathedral", page.songs[1].title); assertEquals(3723, page.songs[1].seconds)
    }

    @Test fun songsWithoutANumberColumnAreNumberedInOrder() {
        val html = """<table id="songlist"><tr><td><a href="/game-soundtracks/album/a/x.mp3">One</a></td><td>0:30</td></tr>
            <tr><td><a href="/game-soundtracks/album/a/y.mp3">Two</a></td><td>1:00</td></tr></table>"""
        val songs = Khinsider.parseAlbum(html, "https://downloads.khinsider.com/game-soundtracks/album/a").songs
        assertEquals(listOf(1, 2), songs.map { it.number }); assertEquals(listOf("0:30", "1:00"), songs.map { it.length })
    }

    @Test fun lengthsAreReadAndOnlyTheSitesAddressesAreUsed() {
        assertEquals(216, Khinsider.seconds("3:36")); assertEquals(3723, Khinsider.seconds("1:02:03")); assertNull(Khinsider.seconds("soon"))
        assertTrue(Khinsider.isSiteUrl("https://downloads.khinsider.com/x")); assertTrue(Khinsider.isSiteUrl("https://jetta.vgmtreasurechest.com/x"))
        assertFalse(Khinsider.isSiteUrl("http://downloads.khinsider.com/x")); assertFalse(Khinsider.isSiteUrl("https://khinsider.com.evil.example/x"))
        assertFalse(Khinsider.isSiteUrl("file:///data/x"))
    }

    @Test fun theBrowserCheckIsRecognised() {
        assertTrue(Khinsider.looksLikeBrowserCheck("<title>Just a moment...</title><script src=\"https://challenges.cloudflare.com/x\">challenge</script>"))
        assertFalse(Khinsider.looksLikeBrowserCheck(publisher))
    }
}
