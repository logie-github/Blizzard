// The World of Warcraft app's look (YeaBwoi, warcraft/android/.../ui/WowTheme.kt), in Blizzard's blue.
package com.logie.blizz.ui

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.ui.draw.clip
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.ExperimentalTextApi
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontVariation
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.em
import androidx.compose.ui.unit.sp
import com.logie.blizz.R
import kotlin.math.PI
import kotlin.math.sin

/** The palette. Each colour follows the look that is on ([Look]): Classic's Northrend frost and gold, or Modern's ([Modern]). */
object Colors {
    val Abyss: Color get() = if (Look.modern) Modern.Background else Color(0xFF02070D)
    val Night: Color get() = if (Look.modern) Modern.Surface else Color(0xFF061320)
    val Deep: Color get() = if (Look.modern) Modern.SurfaceHigh else Color(0xFF0B2233)
    val Frost: Color get() = if (Look.modern) Modern.SurfaceTop else Color(0xFF123A52)
    val Steel: Color get() = if (Look.modern) Color(0xFF2A3546) else Color(0xFF2E5670)
    /** The logo's blue: what's selected. */
    val Ice: Color get() = if (Look.modern) Modern.AccentBright else Color(0xFF3CC4FF)
    val Glow: Color get() = if (Look.modern) Color(0xFFE6F3FF) else Color(0xFFDDF7FF)
    val Gold: Color get() = if (Look.modern) Modern.Gold else Color(0xFFE8B34A)
    val Text: Color get() = if (Look.modern) Modern.Text else Color(0xFFE6F1F7)
    val Mist: Color get() = if (Look.modern) Modern.Muted else Color(0xFF8FA9BC)
}

@OptIn(ExperimentalTextApi::class)
val DisplayFont = FontFamily(
    Font(R.font.blizz_cinzel, FontWeight.Normal, variationSettings = FontVariation.Settings(FontVariation.weight(500))),
    Font(R.font.blizz_cinzel, FontWeight.SemiBold, variationSettings = FontVariation.Settings(FontVariation.weight(650))),
    Font(R.font.blizz_cinzel, FontWeight.Bold, variationSettings = FontVariation.Settings(FontVariation.weight(800))),
)

val BodyFont = FontFamily(
    Font(R.font.blizz_jost_light, FontWeight.Light),
    Font(R.font.blizz_jost_regular, FontWeight.Normal),
    Font(R.font.blizz_jost_medium, FontWeight.Medium),
)

/** Cinzel, the Blizzard titles' face, whatever the look (the modern home's game names). */
val CinzelStyle = TextStyle(fontFamily = DisplayFont, fontWeight = FontWeight.SemiBold, color = Color(0xFFE6F1F7), letterSpacing = 0.08.em)

/** The display face of the look that is on: Cinzel (Classic), or Jost medium (Modern). */
val DisplayStyle: TextStyle
    get() = if (Look.modern) TextStyle(fontFamily = BodyFont, fontWeight = FontWeight.Medium, color = Modern.Text, letterSpacing = 0.02.em) else CinzelStyle
val GoldShadow = Shadow(Color.Black.copy(alpha = 0.85f), Offset(0f, 2f), 6f)
val IceGlow = Shadow(Color(0xFF3CC4FF).copy(alpha = 0.8f), Offset.Zero, 16f)
private val Body = TextStyle(fontFamily = BodyFont, color = Color(0xFFE6F1F7))

/** The modern look's type: Jost throughout, titles medium and white. */
private val ModernTypography = Typography(
    headlineLarge = Body.copy(fontSize = 28.sp, lineHeight = 34.sp, fontWeight = FontWeight.Medium, color = Modern.Text),
    headlineSmall = Body.copy(fontSize = 20.sp, lineHeight = 26.sp, fontWeight = FontWeight.Medium, color = Modern.Text),
    titleLarge = Body.copy(fontSize = 17.sp, lineHeight = 22.sp, fontWeight = FontWeight.Medium, color = Modern.Text),
    titleMedium = Body.copy(fontSize = 16.sp, lineHeight = 21.sp, fontWeight = FontWeight.Medium, color = Modern.Text),
    bodyLarge = Body.copy(fontSize = 16.sp, lineHeight = 23.sp, color = Modern.Text),
    bodyMedium = Body.copy(fontSize = 15.sp, lineHeight = 21.sp, color = Modern.Text),
    bodySmall = Body.copy(fontSize = 13.sp, lineHeight = 18.sp, color = Modern.Muted),
    labelLarge = Body.copy(fontSize = 15.sp, fontWeight = FontWeight.Medium, color = Modern.Text),
    labelMedium = Body.copy(fontSize = 13.sp, fontWeight = FontWeight.Medium, color = Modern.Muted),
    titleSmall = Body.copy(fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Modern.Text),
)

@Composable
fun BlizzTheme(content: @Composable () -> Unit) {
    if (Look.modern) {
        MaterialTheme(
            colorScheme = darkColorScheme(
                primary = Modern.Accent, onPrimary = Color.White, secondary = Modern.Gold,
                background = Modern.Background, onBackground = Modern.Text, surface = Modern.Surface, onSurface = Modern.Text,
                surfaceVariant = Modern.SurfaceHigh, onSurfaceVariant = Modern.Muted, outline = Modern.OutlineStrong,
                surfaceContainer = Modern.SurfaceHigh, surfaceContainerHigh = Modern.SurfaceTop,
            ),
            typography = ModernTypography,
            content = content,
        )
        return
    }
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Colors.Ice, onPrimary = Colors.Abyss, secondary = Colors.Gold,
            background = Colors.Night, onBackground = Colors.Text, surface = Colors.Deep, onSurface = Colors.Text,
            surfaceVariant = Colors.Frost, onSurfaceVariant = Colors.Mist, outline = Colors.Steel,
        ),
        typography = Typography(
            headlineLarge = DisplayStyle.copy(fontSize = 26.sp, lineHeight = 34.sp),
            headlineSmall = DisplayStyle.copy(fontSize = 17.sp, lineHeight = 24.sp, color = Colors.Gold),
            titleLarge = DisplayStyle.copy(fontSize = 14.sp, lineHeight = 20.sp, color = Colors.Mist),
            titleMedium = Body.copy(fontSize = 16.sp, lineHeight = 21.sp, fontWeight = FontWeight.Medium),
            bodyLarge = Body.copy(fontSize = 16.sp, lineHeight = 23.sp),
            bodyMedium = Body.copy(fontSize = 15.sp, lineHeight = 21.sp),
            bodySmall = Body.copy(fontSize = 12.sp, lineHeight = 17.sp, color = Colors.Mist),
            labelLarge = Body.copy(fontSize = 15.sp, fontWeight = FontWeight.Medium),
        ),
        content = content,
    )
}

/** The game's window frame: a steel hairline, a short bracket and a small diamond at each corner. */
fun DrawScope.drawFrame(
    corner: Color = Colors.Gold,
    alpha: Float = 1f,
    arm: Float = 10.dp.toPx(),
    stroke: Float = 1.3.dp.toPx(),
    line: Color? = Colors.Steel,
) {
    val w = size.width
    val h = size.height
    // The modern look: a quiet hairline, no brackets (its panels are rounded by [panel] and [box]).
    if (Look.modern) {
        drawRect(Color.White.copy(alpha = 0.12f * alpha), style = Stroke(1.dp.toPx()))
        return
    }
    if (line != null) drawRect(line, style = Stroke(1.dp.toPx()), alpha = 0.75f * alpha)
    val corners = listOf(Offset(0f, 0f) to Offset(1f, 1f), Offset(w, 0f) to Offset(-1f, 1f), Offset(0f, h) to Offset(1f, -1f), Offset(w, h) to Offset(-1f, -1f))
    val d = 3.dp.toPx()
    for ((point, dir) in corners) {
        drawLine(corner, point, Offset(point.x + dir.x * arm, point.y), stroke, alpha = alpha)
        drawLine(corner, point, Offset(point.x, point.y + dir.y * arm), stroke, alpha = alpha)
        val c = Offset(point.x + dir.x * d * 1.6f, point.y + dir.y * d * 1.6f)
        val diamond = Path().apply {
            moveTo(c.x, c.y - d); lineTo(c.x + d, c.y); lineTo(c.x, c.y + d); lineTo(c.x - d, c.y); close()
        }
        drawPath(diamond, corner, alpha = alpha)
    }
}

/** Gold letters on frost, in the frame; the others plain. */
@Composable
fun FrameButton(text: String, modifier: Modifier = Modifier, primary: Boolean = true, onClick: () -> Unit) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val focused by interaction.collectIsFocusedAsState()
    val lit by animateFloatAsState(if (pressed || focused) 1f else 0f, spring(dampingRatio = 0.7f, stiffness = 900f), label = "lit")
    val haptics = androidx.compose.ui.platform.LocalHapticFeedback.current
    if (Look.modern) {
        val shape = androidx.compose.foundation.shape.RoundedCornerShape(Modern.ButtonCorner)
        Box(
            modifier
                .graphicsLayer { val k = 1f - 0.03f * lit; scaleX = k; scaleY = k }
                .heightIn(min = 44.dp)
                .clip(shape)
                .then(if (primary) Modifier.background(Modern.AccentBrush) else Modifier.background(Color.White.copy(alpha = 0.07f)).border(1.dp, Modern.Outline, shape))
                .drawBehind { drawRect(Color.White.copy(alpha = 0.10f * lit)) }
                .clickable(interactionSource = interaction, indication = null, onClick = {
                    haptics.performHapticFeedback(androidx.compose.ui.hapticfeedback.HapticFeedbackType.TextHandleMove)
                    onClick()
                })
                .padding(horizontal = 18.dp, vertical = 10.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(modernLabel(text), style = MaterialTheme.typography.labelLarge.copy(color = if (primary) Color.White else Modern.Text, fontSize = if (primary) 15.sp else 14.sp), maxLines = 1)
        }
        return
    }
    Box(
        modifier
            .graphicsLayer { val k = 1f - 0.04f * lit; scaleX = k; scaleY = k }
            .heightIn(min = 48.dp)
            .drawBehind {
                if (primary) {
                    drawRect(Brush.verticalGradient(listOf(Colors.Frost, Colors.Deep)))
                    drawRect(Colors.Ice.copy(alpha = 0.2f * lit))
                    drawFrame(alpha = 0.85f + 0.15f * lit, arm = 8.dp.toPx())
                } else {
                    drawRect(Colors.Ice.copy(alpha = 0.10f * lit))
                    drawFrame(corner = Colors.Mist, alpha = 0.7f + 0.3f * lit, arm = 7.dp.toPx())
                }
            }
            .clickable(interactionSource = interaction, indication = null, onClick = {
                haptics.performHapticFeedback(androidx.compose.ui.hapticfeedback.HapticFeedbackType.TextHandleMove)
                onClick()
            })
            .padding(horizontal = 22.dp, vertical = 12.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text.uppercase(),
            style = DisplayStyle.copy(
                fontSize = if (primary) 18.sp else 14.sp,
                color = if (primary) Colors.Gold else Colors.Text,
                shadow = if (primary) GoldShadow else null,
                letterSpacing = 0.18.em,
            ),
            maxLines = 1,
        )
    }
}

/** A title in Cinzel with a hairline running off to its right (the modern look: plain, medium weight). */
@Composable
fun FrameTitle(text: String, modifier: Modifier = Modifier, style: TextStyle = MaterialTheme.typography.headlineSmall) {
    if (Look.modern) {
        Text(text, style = MaterialTheme.typography.headlineSmall, maxLines = 1, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis, modifier = modifier)
        return
    }
    Row(modifier, verticalAlignment = Alignment.CenterVertically) {
        Text(text, style = style, maxLines = 1)
        Spacer(Modifier.width(12.dp))
        Box(Modifier.weight(1f).height(1.dp).background(Brush.horizontalGradient(listOf(Colors.Steel, Color.Transparent))))
    }
}

/** A button's words in the modern look: as written, but a label written all in capitals is put in sentence case. */
internal fun modernLabel(text: String): String =
    if (text.length > 1 && text == text.uppercase() && text.any { it.isLetter() }) text.lowercase().replaceFirstChar { it.uppercase() } else text

/**
 * Particles drifting over a picture: snow, or embers rising. Their colours are [palette]'s (the picture's own highs and lows, with a few
 * accents: [ArtPalette.of]); [palette] null is white snow (or [color], for embers of one colour).
 */
@Composable
fun Snow(modifier: Modifier = Modifier, flakes: Int = 70, alpha: Float = 1f, color: Color = Colors.Glow, rising: Boolean = false, palette: ArtPalette? = null) {
    val motion = rememberInfiniteTransition(label = "snow")
    val time by motion.animateFloat(0f, 1f, infiniteRepeatable(tween(20_000, easing = LinearEasing)), label = "time")
    val seeds = remember(flakes) {
        val random = java.util.Random(7)
        // x, y, depth, phase, colour seed
        List(flakes) { floatArrayOf(random.nextFloat(), random.nextFloat(), 0.4f + random.nextFloat() * 0.6f, random.nextFloat(), random.nextFloat()) }
    }
    val goesUp = palette?.warm ?: rising
    Canvas(modifier.fillMaxSize().graphicsLayer { this.alpha = alpha }) {
        for (seed in seeds) {
            val x0 = seed[0]; val y0 = seed[1]; val depth = seed[2]; val phase = seed[3]
            val travel = (y0 + time * (1f + 2f * depth)) % 1f
            val fall = if (goesUp) 1f - travel else travel
            val sway = sin((time * 6f + phase) * 2 * PI).toFloat() * (if (goesUp) 0.02f else 0.012f)
            val x = ((x0 + sway - time * 0.15f * depth) % 1f + 1f) % 1f
            val tint = palette?.pick(seed[4]) ?: color
            // Embers glow brighter near the bottom where they start; snow keeps one brightness.
            val glow = if (goesUp) 0.35f + 0.55f * (1f - fall).coerceIn(0f, 1f) else 0.25f + 0.5f * depth
            drawCircle(
                tint.copy(alpha = glow.coerceIn(0f, 1f)),
                radius = (0.8f + 1.8f * depth).dp.toPx(),
                center = Offset(x * size.width, fall * size.height),
            )
        }
    }
}
