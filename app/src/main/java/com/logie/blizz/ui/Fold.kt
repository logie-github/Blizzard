package com.logie.blizz.ui

import android.app.Activity
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Dp
import androidx.window.layout.FoldingFeature
import androidx.window.layout.WindowInfoTracker

/** The hinge, in the window's dp: [start] to [end] across it, along x when [vertical], else y. */
data class Fold(val vertical: Boolean, val halfOpen: Boolean, val start: Dp, val end: Dp) {
    /** Half-open with the hinge across the screen: the top half stands up, the bottom lies flat. */
    val tabletop: Boolean get() = halfOpen && !vertical
}

/** The Fold's hinge while the inner screen's on; null on the cover screen and on phones without one. */
@Composable
fun rememberFold(): Fold? {
    val activity = LocalContext.current as? Activity ?: return null
    val density = LocalDensity.current
    var fold by remember { mutableStateOf<Fold?>(null) }
    LaunchedEffect(activity) {
        WindowInfoTracker.getOrCreate(activity).windowLayoutInfo(activity).collect { info ->
            val feature = info.displayFeatures.filterIsInstance<FoldingFeature>().firstOrNull()
            fold = feature?.let {
                val vertical = it.orientation == FoldingFeature.Orientation.VERTICAL
                val b = it.bounds
                with(density) {
                    Fold(
                        vertical = vertical,
                        halfOpen = it.state == FoldingFeature.State.HALF_OPENED,
                        start = (if (vertical) b.left else b.top).toDp(),
                        end = (if (vertical) b.right else b.bottom).toDp(),
                    )
                }
            }
        }
    }
    return fold
}
