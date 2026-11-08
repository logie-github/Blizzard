package com.logie.blizz.steamgrid

import androidx.test.core.app.ApplicationProvider
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
class SteamGridTest {
    @Test fun theKeyIsKeptAndTakenAway() {
        val context = ApplicationProvider.getApplicationContext<android.app.Application>()
        SteamGrid.clearKey(context)
        assertNull(SteamGrid.key(context)); assertFalse(SteamGrid.hasKey(context))
        SteamGrid.setKey(context, "  abc123  ")
        assertEquals("abc123", SteamGrid.key(context))
        SteamGrid.setKey(context, "   ")
        assertFalse(SteamGrid.hasKey(context))
        SteamGrid.clearKey(context)
    }

    @Test fun theRequestsAskForTheRightLists() {
        assertEquals("https://www.steamgriddb.com/api/v2/search/autocomplete/Diablo%20II", SteamGrid.searchUrl(" Diablo II "))
        assertEquals(
            "https://www.steamgriddb.com/api/v2/grids/game/5254?dimensions=600x900,342x482,660x930&nsfw=false&humor=false&epilepsy=false&types=static",
            SteamGrid.picturesUrl(SteamGrid.Slot.BOX, 5254),
        )
        assertEquals(
            "https://www.steamgriddb.com/api/v2/heroes/game/7?dimensions=1920x620,3840x1240,1600x650&nsfw=false&humor=false&epilepsy=false&types=static&page=2",
            SteamGrid.picturesUrl(SteamGrid.Slot.HERO, 7, page = 2),
        )
        val logos = SteamGrid.picturesUrl(SteamGrid.Slot.LOGO, 9)
        assertTrue(logos, logos.startsWith("https://www.steamgriddb.com/api/v2/logos/game/9?mimes=image/png,image/webp&nsfw=false"))
        assertFalse(logos.contains("types="))
    }

    @Test fun onlyTheSitesOwnAddressesAreFetched() {
        assertTrue(SteamGrid.isSiteUrl("https://cdn2.steamgriddb.com/grid/abc.png"))
        assertTrue(SteamGrid.isSiteUrl("https://www.steamgriddb.com/x"))
        assertFalse(SteamGrid.isSiteUrl("http://cdn2.steamgriddb.com/grid/abc.png"))
        assertFalse(SteamGrid.isSiteUrl("https://steamgriddb.com.evil.example/x"))
        assertFalse(SteamGrid.isSiteUrl("https://evil.example/steamgriddb.com"))
        assertFalse(SteamGrid.isSiteUrl("file:///data/x"))
        assertFalse(SteamGrid.isSiteUrl("not a url"))
    }

    @Test fun gamesAndPicturesAreRead() {
        val games = SteamGrid.parseGames("""{"success":true,"data":[{"id":5254,"name":"Diablo","types":["steam"],"verified":true},{"id":1,"name":""},{"id":2,"name":"Diablo II"}]}""")
        assertEquals(listOf("Diablo", "Diablo II"), games.map { it.name })
        assertTrue(games[0].verified)

        val page = SteamGrid.parsePictures(
            """{"success":true,"page":0,"total":120,"limit":50,"data":[
              {"id":10,"score":3,"style":"alternate","width":600,"height":900,"mime":"image/png","url":"https://cdn2.steamgriddb.com/grid/a.png","thumb":"https://cdn2.steamgriddb.com/thumb/a.jpg","author":{"name":"someone"}},
              {"id":11,"style":["a","b"],"url":"https://cdn2.steamgriddb.com/grid/b.png"},
              {"id":12,"url":"https://evil.example/c.png","thumb":"https://evil.example/c.jpg"}]}""",
        )
        assertEquals(listOf(10L, 11L), page.pictures.map { it.id })
        assertEquals("alternate", page.pictures[0].style); assertEquals("a, b", page.pictures[1].style)
        assertEquals("someone", page.pictures[0].author)
        assertEquals(page.pictures[1].url, page.pictures[1].thumb)
        assertTrue(page.hasMore)
        assertFalse(SteamGrid.parsePictures("""{"success":true,"page":2,"total":120,"limit":50,"data":[]}""").hasMore)
    }

    @Test fun theSitesErrorsAreSaid() {
        val e = runCatching { SteamGrid.parsePictures("""{"success":false,"errors":["Game not found"]}""") }.exceptionOrNull()
        assertTrue(e is SteamGrid.SteamGridException)
        assertEquals("Game not found", e!!.message)
    }

    @Test fun aGameIsLookedUpByItsName() {
        assertEquals("Diablo II Resurrected", SteamGrid.searchTerm("Diablo II", "Resurrected"))
        assertEquals("Diablo", SteamGrid.searchTerm("Diablo", null))
        assertEquals("World of Warcraft", SteamGrid.searchTerm("World of Warcraft", "Wrath+"))
    }
}
