package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.fail
import org.junit.Test
import java.io.File
import kotlin.concurrent.thread

/** A program stopped by a cancel is the cancel, not a file error: the phone reported "read interrupted by close()" as PERMISSION_DENIED (issue 77). */
class ToolsCancelTest {
    @Test fun aCancelledProgramIsReportedAsTheCancel() {
        val dir = java.nio.file.Files.createTempDirectory("tools").toFile()
        val script = File(dir, "slow.sh").apply { writeText("#!/bin/sh\necho started\nsleep 30\n"); setExecutable(true) }
        val cancel = CancelToken()
        thread { Thread.sleep(600); cancel.cancel() }
        try {
            Tools.run(listOf(script.path), dir, cancel) { }
            fail("the run should have ended with the cancel")
        } catch (e: ImportException) {
            assertEquals(Problem.CANCELLED, e.problem)
        } catch (e: java.io.IOException) {
            // The reader may see the end of the output before the close reaches it: then the run returns the code, which is fine too.
            fail("an IOException escaped: $e")
        }
        dir.deleteRecursively()
    }
}
