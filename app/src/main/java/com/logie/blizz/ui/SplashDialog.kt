package com.logie.blizz.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.game.Loading
import com.logie.blizz.game.Splashes

/** Hold a game's art: its loading screen as it is now, with a picture and a logo to pick from the phone. */
@Composable
fun SplashDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    @Suppress("UNUSED_VARIABLE") val version by Splashes.version.collectAsState()
    val pickBackground = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) Splashes.set(context, game.id, Splashes.Kind.BACKGROUND, uri)
    }
    val pickLogo = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) Splashes.set(context, game.id, Splashes.Kind.LOGO, uri)
    }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(18.dp).widthIn(max = 620.dp).fillMaxWidth().drawBehind { drawRect(Colors.Deep); drawFrame() }.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle(game.fullTitle)
            // The loading screen itself, at a third of the size.
            Box(Modifier.fillMaxWidth().aspectRatio(16f / 9f).clipToBounds().border(1.dp, Colors.Steel).background(Colors.Abyss)) {
                Box(Modifier.graphicsLayer { scaleX = 0.5f; scaleY = 0.5f }) { Loading(game.id, "Starting…") }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.CenterHorizontally)) {
                FrameButton("Background") { pickBackground.launch(arrayOf("image/*")) }
                FrameButton("Logo") { pickLogo.launch(arrayOf("image/*")) }
                FrameButton("Reset", primary = false) { Splashes.clear(context, game.id) }
            }
        }
    }
}
