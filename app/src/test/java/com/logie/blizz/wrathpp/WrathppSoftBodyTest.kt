package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class WrathppSoftBodyTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun naturalUntilChosenAndThenKept() {
        assertEquals(WrathppSoftBody.Level.NATURAL, WrathppSoftBody.chosen(tmp.root))
        WrathppSoftBody.choose(tmp.root, WrathppSoftBody.Level.OFF)
        assertEquals(WrathppSoftBody.Level.OFF, WrathppSoftBody.chosen(tmp.root))
    }

    @Test fun theScriptSetsTheNumberTheAddOnReads() {
        assertEquals("WrathppSoftBodyLevel = 3\n", String(WrathppSoftBody.script(WrathppSoftBody.Level.STRONG)))
    }
}
