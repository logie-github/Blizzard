package com.logie.blizz.game

import androidx.test.core.app.ApplicationProvider
import com.logie.blizz.game.LaunchOptions.Box64
import com.logie.blizz.game.LaunchOptions.DDraw
import com.logie.blizz.game.LaunchOptions.Fps
import com.logie.blizz.game.LaunchOptions.Tri
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class LaunchOptionsTest {
    private val context get() = ApplicationProvider.getApplicationContext<android.app.Application>()

    @Test fun classicGamesDefaultToCncDdrawOpenGlWithoutCpuPinning() {
        for (id in listOf("diablo2", "starcraft", "warcraft2")) {
            val r = LaunchOptions().resolve(id)
            assertEquals("cnc-ddraw", r.ddrawWrapper)
            assertEquals("opengl", r.renderer)
            assertFalse(r.singleCpu)
            assertTrue(r.redraw)
            assertEquals("INTERMEDIATE", r.box64Preset)
            assertEquals("ddrawWrapper=cnc-ddraw", r.dxwrapperConfig)
        }
    }

    @Test fun otherGamesKeepWinlatorsDefaults() {
        val r = LaunchOptions().resolve("warcraft3")
        assertNull(r.ddrawWrapper)
        assertEquals("", r.dxwrapperConfig)
        assertEquals("PERFORMANCE", r.box64Preset)
        assertEquals("vortek,gladio", r.graphicsDriver)
        assertEquals("dxvk", r.dxwrapper)
        assertNull(LaunchOptions().ddrawIni("warcraft3"))
    }

    @Test fun theDirectDrawChoiceMapsToWrapperAndRenderer() {
        assertEquals("gdi", LaunchOptions(ddraw = DDraw.GDI).resolve("starcraft").renderer)
        assertEquals("direct3d9", LaunchOptions(ddraw = DDraw.D3D9).resolve("starcraft").renderer)
        assertEquals("opengl", LaunchOptions(ddraw = DDraw.OPENGL).resolve("starcraft").renderer)
        val wine = LaunchOptions(ddraw = DDraw.WINE).resolve("diablo2")
        assertNull(wine.ddrawWrapper)
        assertEquals("", wine.dxwrapperConfig)
        assertNull(LaunchOptions(ddraw = DDraw.WINE).ddrawIni("diablo2"))
        // not a classic game: the choice means nothing
        assertNull(LaunchOptions(ddraw = DDraw.GDI).resolve("starcraft2").ddrawWrapper)
    }

    @Test fun theBox64NamesAreWinlatorsPresetIds() {
        assertEquals("STABILITY", LaunchOptions(box64 = Box64.Preset.STABILITY).resolve("diablo2").box64Preset)
        assertEquals("CONSERVATIVE", LaunchOptions(box64 = Box64.Preset.COMPATIBLE).resolve("diablo2").box64Preset)
        assertEquals("INTERMEDIATE", LaunchOptions(box64 = Box64.Preset.INTERMEDIATE).resolve("starcraft2").box64Preset)
        assertEquals("PERFORMANCE", LaunchOptions(box64 = Box64.Preset.PERFORMANCE).resolve("diablo2").box64Preset)
        assertEquals(listOf("Default", "Stability", "Compatible", "Intermediate", "Performance"), Box64.Preset.entries.map { it.label })
    }

    @Test fun theAppChoosesTheDriverFromThePhone() {
        val adreno = LaunchOptions.Hardware(adreno = true)
        assertEquals("turnip,gladio", LaunchOptions().resolve("warcraft3", adreno).graphicsDriver)
        assertEquals("vortek,gladio", LaunchOptions().resolve("warcraft3").graphicsDriver)
        assertEquals("vortek,gladio", LaunchOptions(safeMode = true).resolve("warcraft3", adreno).graphicsDriver)
        assertEquals("dxvk", LaunchOptions().resolve("warcraft3", adreno).dxwrapper)
    }

    @Test fun safeModeIsTheMostConservativeOfEverything() {
        val chosen = LaunchOptions(
            safeMode = true, ddraw = DDraw.D3D9, box64 = Box64.Preset.PERFORMANCE,
            fps = Fps.UNLIMITED, vsync = Tri.ON, singleCpu = Tri.ON, redraw = Tri.OFF,
        )
        val r = chosen.resolve("starcraft")
        assertEquals("gdi", r.renderer)
        assertEquals("cnc-ddraw", r.ddrawWrapper)
        assertEquals("STABILITY", r.box64Preset)
        assertEquals("vortek,gladio", r.graphicsDriver)
        assertEquals("dxvk", r.dxwrapper)
        assertEquals(30, r.maxFps)
        assertFalse(r.vsync)
        assertFalse(r.singleCpu)
        assertTrue(r.redraw)
        assertNull(chosen.resolve("warcraft3").lines)
        assertEquals("STABILITY", chosen.resolve("warcraft3").box64Preset)
    }

    @Test fun resolutionIsTheScreensMostAndOnlyForGamesWithoutAFixedSize() {
        val o = LaunchOptions()
        assertEquals(Screen.MOST, o.resolve("warcraft3").lines)
        assertEquals(Screen.MOST, o.resolve("wow-client").lines)
        assertNull(o.resolve("diablo2").lines)
        assertNull(o.resolve("starcraft").lines)
    }

    @Test fun everyGameIsDrawnAtSixtyByDefault() {
        assertEquals(60, LaunchOptions().resolve("diablo2").maxFps)
        assertEquals(60, LaunchOptions().resolve("warcraft3").maxFps)
    }

    @Test fun theIniCarriesTheChoices() {
        val ini = LaunchOptions(ddraw = DDraw.GDI, fps = Fps.FPS_30, vsync = Tri.ON, singleCpu = Tri.ON, redraw = Tri.OFF).ddrawIni("diablo2")!!
        val lines = ini.lines().toSet()
        assertTrue("[ddraw]" in lines)
        assertTrue("renderer=gdi" in lines)
        assertTrue("maxfps=30" in lines)
        assertTrue("vsync=true" in lines)
        assertTrue("singlecpu=true" in lines)
        assertTrue("nonexclusive=false" in lines)
        assertTrue("minfps=0" in lines)
        assertTrue("windowed=true" in lines && "fullscreen=true" in lines)
        assertFalse("[StarCraft]" in lines)
        val sc = LaunchOptions().ddrawIni("starcraft")!!
        assertTrue(sc.contains("minfps=-1") && sc.contains("[StarCraft]\ngame_handles_close=true"))
        assertTrue(LaunchOptions(fps = Fps.UNLIMITED).ddrawIni("diablo2")!!.contains("maxfps=0"))
    }

    @Test fun theCacheKeyChangesWithWhatWinlatorCaches() {
        val base = LaunchOptions().resolve("starcraft").cacheKey
        assertNotEquals(base, LaunchOptions(ddraw = DDraw.WINE).resolve("starcraft").cacheKey)
        assertNotEquals(base, LaunchOptions(box64 = Box64.Preset.STABILITY).resolve("starcraft").cacheKey)
        assertEquals(base, LaunchOptions(fps = Fps.FPS_30).resolve("starcraft").cacheKey) // ini only
    }

    @Test fun nativeGamesHaveNoOptions() {
        assertFalse(LaunchOptions.hasOptions("warcraft"))
        assertFalse(LaunchOptions.hasOptions("warcraft2"))
        assertTrue(LaunchOptions.hasOptions("starcraft"))
        assertTrue(LaunchOptions.hasOptions("wow-client"))
    }

    @Test fun theStoreKeepsEachGamesChoicesApart() {
        val store = LaunchOptionsStore(context)
        assertEquals(LaunchOptions(), store.get("starcraft"))
        val o = LaunchOptions(safeMode = true, ddraw = DDraw.D3D9, box64 = Box64.Preset.COMPATIBLE, fps = Fps.FPS_30, redraw = Tri.OFF)
        store.set("starcraft", o)
        assertEquals(o, store.get("starcraft"))
        assertEquals(LaunchOptions(), store.get("diablo2"))
        store.set("wow-client", LaunchOptions(box64 = Box64.Preset.STABILITY))
        assertEquals(Box64.Preset.STABILITY, store.get("wow").box64)
        store.reset("starcraft")
        assertEquals(LaunchOptions(), store.get("starcraft"))
        assertEquals(Box64.Preset.STABILITY, store.get("wow").box64)
        assertNull(store.lastApplied())
        store.setLastApplied("x")
        assertEquals("x", store.lastApplied())
    }
}
