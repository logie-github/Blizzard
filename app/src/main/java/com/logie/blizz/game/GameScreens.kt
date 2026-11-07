package com.logie.blizz.game

import android.app.Activity
import android.graphics.Color as AndroidColor
import android.graphics.drawable.ColorDrawable
import android.view.ViewGroup
import android.view.WindowManager
import androidx.activity.ComponentDialog
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.type
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.logie.blizz.Games
import com.logie.blizz.R
import com.logie.blizz.ui.BlizzTheme
import com.logie.blizz.ui.Colors
import com.logie.blizz.ui.FrameButton
import com.logie.blizz.ui.FrameTitle
import com.logie.blizz.ui.Snow
import com.logie.blizz.ui.drawFrame

/**
 * The app's own screens over the game, in the launcher's look: the loading screen while Windows
 * and the game start ([GameLoading]), the menu four fingers open ([GameMenu]), and the text prompt
 * with the phone's keyboard ([GamePrompt]). From YeaBwoi's Warcraft app.
 */
private fun fullScreenDialog(activity: Activity, dim: Boolean, content: @Composable () -> Unit): ComponentDialog {
    val dialog = ComponentDialog(activity, android.R.style.Theme_Translucent_NoTitleBar_Fullscreen)
    dialog.setContentView(
        ComposeView(activity).apply { setContent { BlizzTheme(content) } },
        ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT),
    )
    dialog.window?.let { window ->
        window.setBackgroundDrawable(ColorDrawable(if (dim) 0x99000000.toInt() else AndroidColor.TRANSPARENT))
        window.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        window.addFlags(WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS)
        WindowCompat.getInsetsController(window, window.decorView).apply {
            hide(WindowInsetsCompat.Type.systemBars())
            systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }
    return dialog
}

/**
 * The loading screen until the game's first window shows: the game's box art, the logo, a spinner
 * and what's happening. The same calls as the game screen's own loading box, which it replaces
 * (patches/winlator/0004).
 */
class GameLoading(private val activity: Activity) {
    private val gameId = activity.intent?.getStringExtra(GestureView.EXTRA_SPLASH) ?: activity.intent?.getStringExtra(GestureView.EXTRA_GAME)
    private var dialog: ComponentDialog? = null
    private val text = mutableStateOf("")

    @Synchronized
    fun show(textResId: Int) {
        // A line of the loading lines, in place of the step's name.
        text.value = LoadingLines.next(text.value.takeIf { it.isNotEmpty() })
        if (dialog?.isShowing == true) return
        val created = dialog ?: fullScreenDialog(activity, dim = false) { Loading(gameId, text.value) }.also {
            it.setCancelable(false)
            dialog = it
        }
        created.show()
    }

    fun showOnUiThread(textResId: Int) = activity.runOnUiThread { show(textResId) }

    @Synchronized
    fun close() {
        runCatching { dialog?.dismiss() }
    }

    fun closeOnUiThread() = activity.runOnUiThread { close() }

    fun isShowing(): Boolean = dialog?.isShowing == true
}

@Composable
internal fun Loading(gameId: String?, text: String, layoutOverride: Splashes.Layout? = null, grid: Boolean = false) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val game = Games.find(gameId)
    val version by Splashes.version.collectAsState()
    // The person's own picture and logo (hold the game's art), else the game's own.
    val custom = remember(gameId, version) {
        fun load(kind: Splashes.Kind) = gameId?.let { Splashes.file(context, it, kind) }?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
        load(Splashes.Kind.BACKGROUND) to load(Splashes.Kind.LOGO)
    }
    val (customBackground, customLogo) = custom
    val layout = layoutOverride ?: remember(gameId, version) { gameId?.let { Splashes.layout(context, it) } ?: Splashes.Layout() }
    val art: Painter? = customBackground?.let { BitmapPainter(it) } ?: game?.splash?.let { painterResource(it) }
    val logo: Painter? = customLogo?.let { BitmapPainter(it) } ?: game?.splashLogo?.let { painterResource(it) }
    Box(Modifier.fillMaxSize().background(Colors.Abyss), contentAlignment = Alignment.Center) {
        if (art != null) {
            // The art filling the screen (cut at its sides, or below), its logo low over it, embers rising.
            Image(art, contentDescription = null, contentScale = ContentScale.Crop, alignment = BiasAlignment(0f, if (customBackground != null) 0f else game?.splashTop ?: -0.2f),
                modifier = Modifier.fillMaxSize().graphicsLayer { scaleX = layout.zoom; scaleY = layout.zoom; translationX = layout.panX * size.width; translationY = layout.panY * size.height })
            Box(Modifier.fillMaxSize().background(Brush.verticalGradient(0.45f to Color.Transparent, 1f to Color.Black.copy(alpha = 0.9f))))
            Snow(alpha = 0.8f, color = Color(0xFFFF8A3D), rising = true, flakes = 50)
            // A very wide screen (the cover screen sideways): the logo to the lower right, off the face.
            BoxWithConstraints(Modifier.fillMaxSize()) {
                val wide = maxWidth > maxHeight * 1.7f
                val logoWidth = (if (wide) maxWidth * 0.24f else 340.dp) * layout.logoScale
                if (layout.logoCell >= 0) {
                    // The person's place for the logo: a cell of the 3x3 grid; the status stays at the bottom centre.
                    val col = layout.logoCell % 3
                    val row = layout.logoCell / 3
                    logo?.let {
                        Image(it, contentDescription = game?.fullTitle, contentScale = ContentScale.Fit,
                            modifier = Modifier.align(BiasAlignment(col - 1f, row - 1f)).padding(horizontal = 24.dp, vertical = if (row == 2) 72.dp else 24.dp).width(logoWidth.coerceAtMost(maxWidth * 0.9f)))
                    }
                    Row(Modifier.align(Alignment.BottomCenter).padding(bottom = 28.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Spinner(26.dp, accent = Color(0xFFFF8A3D))
                        Text(text, style = MaterialTheme.typography.titleMedium, color = Color(0xFFE8C9A8))
                    }
                } else Column(
                    Modifier.fillMaxSize().padding(bottom = 28.dp, end = if (wide) 36.dp else 0.dp),
                    horizontalAlignment = if (wide) Alignment.End else Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(14.dp, Alignment.Bottom),
                ) {
                    logo?.let { Image(it, contentDescription = game?.fullTitle, contentScale = ContentScale.Fit, modifier = Modifier.width(logoWidth)) }
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Spinner(26.dp, accent = Color(0xFFFF8A3D))
                        Text(text, style = MaterialTheme.typography.titleMedium, color = Color(0xFFE8C9A8))
                    }
                }
            }
            if (grid) Canvas(Modifier.fillMaxSize()) {
                val line = Color.White.copy(alpha = 0.55f)
                for (i in 1..2) {
                    drawLine(line, Offset(size.width * i / 3, 0f), Offset(size.width * i / 3, size.height), 1.dp.toPx())
                    drawLine(line, Offset(0f, size.height * i / 3), Offset(size.width, size.height * i / 3), 1.dp.toPx())
                }
                drawLine(Colors.Ice.copy(alpha = 0.8f), Offset(size.width / 2 - 8.dp.toPx(), size.height / 2), Offset(size.width / 2 + 8.dp.toPx(), size.height / 2), 1.5.dp.toPx())
                drawLine(Colors.Ice.copy(alpha = 0.8f), Offset(size.width / 2, size.height / 2 - 8.dp.toPx()), Offset(size.width / 2, size.height / 2 + 8.dp.toPx()), 1.5.dp.toPx())
            }
            return@Box
        }
        if (game != null) {
            Image(
                painterResource(game.cover), contentDescription = null, contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize(),
            )
        }
        Box(Modifier.fillMaxSize().background(Brush.verticalGradient(listOf(Colors.Abyss.copy(alpha = 0.55f), Colors.Abyss.copy(alpha = 0.9f)))))
        Snow(alpha = 0.6f)
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(22.dp)) {
            if (logo != null) Image(logo, contentDescription = null, contentScale = ContentScale.Fit, modifier = Modifier.width(300.dp))
            else Image(painterResource(R.drawable.blizz_logo), contentDescription = null, contentScale = ContentScale.Fit, modifier = Modifier.width(260.dp))
            Spinner(44.dp)
            Text(text, style = MaterialTheme.typography.titleMedium, color = Colors.Mist, textAlign = TextAlign.Center)
        }
    }
}

/** Waiting: a bright arc running round a steel ring. */
@Composable
fun Spinner(size: Dp, modifier: Modifier = Modifier, accent: Color = Colors.Ice) {
    val motion = rememberInfiniteTransition(label = "spinner")
    val turn by motion.animateFloat(0f, 360f, infiniteRepeatable(tween(1_400, easing = LinearEasing)), label = "turn")
    Canvas(modifier.size(size)) {
        val r = this.size.minDimension / 2 * 0.86f
        drawCircle(Colors.Steel, r, style = Stroke(1.2.dp.toPx()))
        drawArc(
            Brush.sweepGradient(listOf(Color.Transparent, accent, if (accent == Colors.Ice) Colors.Glow else accent)),
            startAngle = turn, sweepAngle = 100f, useCenter = false,
            topLeft = Offset(center.x - r, center.y - r), size = Size(r * 2, r * 2),
            style = Stroke(2.2.dp.toPx(), cap = StrokeCap.Round),
        )
    }
}

@Composable
private fun Panel(modifier: Modifier, content: @Composable () -> Unit) {
    Box(
        modifier
            .drawBehind {
                drawRect(Brush.verticalGradient(listOf(Colors.Deep, Colors.Night)))
                drawFrame()
            }
            .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) {}
            .padding(20.dp),
    ) { content() }
}

/** The app's menu over the game (four fingers): back to the game, the keyboard, or leave. */
object GameMenu {
    fun show(activity: Activity, gameId: String?, onKeyboard: () -> Unit, onChat: () -> Unit, onTypeKey: (String) -> Unit, onLeave: () -> Unit, onReport: () -> Unit = {}) {
        var dialog: ComponentDialog? = null
        fun close(then: () -> Unit) = { dialog?.dismiss(); then() }
        dialog = fullScreenDialog(activity, dim = true) {
            Box(
                Modifier.fillMaxSize().clickable(interactionSource = remember { MutableInteractionSource() }, indication = null, onClick = close {}),
                contentAlignment = Alignment.Center,
            ) {
                Panel(Modifier.widthIn(max = 420.dp).padding(24.dp)) {
                    Column(Modifier.verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        FrameTitle(Games.find(gameId)?.fullTitle ?: stringResource(R.string.app_name))
                        FrameButton(stringResource(R.string.game_menu_back), Modifier.fillMaxWidth(), onClick = close {})
                        FrameButton(stringResource(R.string.game_menu_keyboard), Modifier.fillMaxWidth(), primary = false, onClick = close(onKeyboard))
                        FrameButton(stringResource(R.string.game_menu_chat), Modifier.fillMaxWidth(), primary = false, onClick = close(onChat))
                        FrameButton("Send a report (with the game's log)", Modifier.fillMaxWidth(), primary = false, onClick = close(onReport))
                        FrameButton(stringResource(R.string.game_menu_leave), Modifier.fillMaxWidth(), primary = false, onClick = close(onLeave))
                        Text(stringResource(R.string.game_menu_leave_note), style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
        dialog.show()
    }
}

/** The text prompt: a box at the top with the phone's keyboard, typed into the game when sent. */
object GamePrompt {
    fun show(activity: Activity, gameId: String?, chat: Boolean, onSend: (String) -> Unit, onCancel: () -> Unit, onBackspace: () -> Unit, password: Boolean = false): ComponentDialog {
        var dialog: ComponentDialog? = null
        var finished = false
        fun finish(text: String?) {
            if (finished) return
            finished = true
            dialog?.dismiss()
            if (text != null) onSend(text) else onCancel()
        }
        dialog = fullScreenDialog(activity, dim = false) {
            Prompt(chat, onSend = { finish(it) }, onCancel = { finish(null) }, onBackspace = onBackspace, password = password)
        }
        dialog.setOnCancelListener { finish(null) }
        dialog.window?.setSoftInputMode(
            WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING or WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE
        )
        dialog.show()
        return dialog
    }
}

@Composable
private fun Prompt(chat: Boolean, onSend: (String) -> Unit, onCancel: () -> Unit, onBackspace: () -> Unit, password: Boolean = false) {
    var text by remember { mutableStateOf("") }
    val focus = remember { FocusRequester() }
    val keyboard = LocalSoftwareKeyboardController.current
    LaunchedEffect(Unit) {
        focus.requestFocus()
        keyboard?.show()
    }
    Box(
        Modifier.fillMaxSize().clickable(interactionSource = remember { MutableInteractionSource() }, indication = null, onClick = onCancel),
        contentAlignment = Alignment.TopCenter,
    ) {
        Panel(Modifier.padding(top = 18.dp, start = 16.dp, end = 16.dp).widthIn(max = 640.dp).fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(Modifier.fillMaxWidth().background(Colors.Abyss).padding(horizontal = 12.dp, vertical = 10.dp)) {
                    BasicTextField(
                        value = text,
                        onValueChange = { text = it.replace("\n", "") },
                        singleLine = true,
                        textStyle = MaterialTheme.typography.bodyLarge,
                        cursorBrush = SolidColor(Colors.Ice),
                        visualTransformation = if (password) androidx.compose.ui.text.input.PasswordVisualTransformation() else androidx.compose.ui.text.input.VisualTransformation.None,
                        keyboardOptions = KeyboardOptions(
                            keyboardType = if (password) KeyboardType.Password else KeyboardType.Ascii,
                            autoCorrectEnabled = false,
                            imeAction = if (chat) ImeAction.Send else ImeAction.Done,
                        ),
                        keyboardActions = KeyboardActions(onAny = { onSend(text) }),
                        modifier = Modifier
                            .fillMaxWidth()
                            .focusRequester(focus)
                            // With nothing left here, Backspace goes on into the game's box.
                            .onPreviewKeyEvent { event ->
                                if (event.key != Key.Backspace || text.isNotEmpty()) return@onPreviewKeyEvent false
                                if (event.type == KeyEventType.KeyDown) onBackspace()
                                true
                            },
                    )
                }
                Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    FrameButton("⌫", primary = false, onClick = onBackspace)
                    FrameButton(stringResource(R.string.blizz_cancel), primary = false, onClick = onCancel)
                    FrameButton(stringResource(R.string.game_prompt_send)) { onSend(text) }
                }
            }
        }
    }
}
