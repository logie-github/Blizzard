package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Test

class EsyncSettingTest {
    private val winlator = "ZINK_DESCRIPTORS=lazy ZINK_DEBUG=compact MESA_SHADER_CACHE_DISABLE=false MESA_SHADER_CACHE_MAX_SIZE=512MB mesa_glthread=true WINEESYNC=1 TU_DEBUG=noconform"

    @Test fun `off, the rest kept`() {
        assertEquals(winlator.replace("WINEESYNC=1", "WINEESYNC=0"), EsyncSetting.apply(winlator, on = false))
    }

    @Test fun `back on for the next game`() {
        assertEquals(winlator, EsyncSetting.apply(EsyncSetting.apply(winlator, on = false), on = true))
    }

    @Test fun `added when absent`() {
        assertEquals("A=1 WINEESYNC=0", EsyncSetting.apply("A=1", on = false))
        assertEquals("WINEESYNC=1", EsyncSetting.apply("", on = true))
    }
}
