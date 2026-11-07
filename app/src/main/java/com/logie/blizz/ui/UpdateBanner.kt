package com.logie.blizz.ui

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import com.logie.blizz.importer.FileValidator
import com.logie.blizz.update.Updater

/** The update, at the bottom centre of the launcher while it downloads; then Android's installer. */
@Composable
fun UpdateBanner() {
    val context = LocalContext.current
    // Back from "install unknown apps": on to the installer.
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { Updater.retryInstall(context); Updater.checkAndInstall(context) }
    val state by Updater.state.collectAsState()
    Box(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing), contentAlignment = Alignment.BottomCenter) {
        AnimatedVisibility(state !is Updater.State.Idle, enter = fadeIn() + slideInVertically { it }, exit = fadeOut() + slideOutVertically { it }) {
            Column(
                Modifier.padding(12.dp).widthIn(max = 520.dp).fillMaxWidth()
                    .drawBehind { drawRect(Colors.Deep.copy(alpha = 0.95f)); drawFrame(arm = 6.dp.toPx()) }
                    .padding(14.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                when (val s = state) {
                    is Updater.State.Downloading -> {
                        Text("Updating to ${s.update.title}", style = MaterialTheme.typography.titleMedium)
                        if (s.total > 0) {
                            LinearProgressIndicator(progress = { (s.done.toFloat() / s.total).coerceIn(0f, 1f) }, color = Colors.Ice, trackColor = Colors.Frost, modifier = Modifier.fillMaxWidth())
                            Text("${FileValidator.gb(s.done)} / ${FileValidator.gb(s.total)}", style = MaterialTheme.typography.bodySmall)
                        } else {
                            LinearProgressIndicator(color = Colors.Ice, trackColor = Colors.Frost, modifier = Modifier.fillMaxWidth())
                        }
                    }
                    is Updater.State.Ready -> {
                        Text("${s.update.title} is ready", style = MaterialTheme.typography.titleMedium)
                        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            if (s.needsPermission && Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                FrameButton("Allow installs") {
                                    context.startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:${context.packageName}")))
                                }
                            } else {
                                FrameButton("Install") { context.startActivity(Updater.installIntent(context, s.apk)) }
                            }
                        }
                    }
                    is Updater.State.Failed -> {
                        Text(s.message, style = MaterialTheme.typography.bodyMedium)
                        FrameButton("OK", primary = false) { Updater.dismiss() }
                    }
                    Updater.State.Idle -> {}
                }
            }
        }
    }
}
