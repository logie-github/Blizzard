package com.logie.blizz.ui

import androidx.compose.ui.test.SemanticsNodeInteraction
import java.io.File

/**
 * Screenshots from the UI tests: PNGs in the folder named by the system property `blizz.shots`
 * (default: the session's ui-shots folder). Never fails a test: a folder that can't be written is skipped.
 */
object UiShots {
    private val dir: File? = runCatching {
        File(System.getProperty("blizz.shots") ?: "/tmp/claude-0/-home-user/aec03bc0-04a6-58e1-9edb-60121159f071/scratchpad/ui-shots")
            .also { it.mkdirs() }.takeIf { it.isDirectory && it.canWrite() }
    }.getOrNull()

    fun save(name: String, node: SemanticsNodeInteraction) {
        val folder = dir ?: return
        runCatching {
            // captureToImage waits for a frame the paused Robolectric looper never runs: the view draws itself instead.
            var view = node.fetchSemanticsNode().root as android.view.View
            // A dialog or menu is drawn from its window's top view.
            while (view.parent is android.view.View) view = view.parent as android.view.View
            if (view !== (node.fetchSemanticsNode().root as android.view.View) || view.width <= 0) {
                // Robolectric never lays a dialog's or menu's window out: do it at the screen's size.
                val m = view.resources.displayMetrics
                view.measure(android.view.View.MeasureSpec.makeMeasureSpec(m.widthPixels, android.view.View.MeasureSpec.AT_MOST), android.view.View.MeasureSpec.makeMeasureSpec(m.heightPixels, android.view.View.MeasureSpec.AT_MOST))
                view.layout(0, 0, view.measuredWidth, view.measuredHeight)
            }
            if (view.width <= 0 || view.height <= 0) return
            val bitmap = android.graphics.Bitmap.createBitmap(view.width, view.height, android.graphics.Bitmap.Config.ARGB_8888)
            view.draw(android.graphics.Canvas(bitmap))
            File(folder, "$name.png").outputStream().use { bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG, 100, it) }
        }.onFailure { System.err.println("UiShots: $name not captured: ${it.stackTraceToString().lines().take(14).joinToString("\n")}") }
    }

    /** One PNG per window (the screen, then each dialog or menu over it): `name`, `name-2`, ... */
    fun saveAll(name: String, rule: androidx.compose.ui.test.junit4.ComposeTestRule) {
        val roots = rule.onAllNodes(androidx.compose.ui.test.isRoot())
        val n = roots.fetchSemanticsNodes().size
        for (i in 0 until n) save(if (i == 0) name else "$name-${i + 1}", roots[i])
    }
}
