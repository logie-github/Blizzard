package com.logie.blizz.ui

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * The app's two looks: **Modern** (the default: a clean dark launcher with rounded surfaces, one accent blue, sans-serif
 * type, the games' art up front) and **Classic** (the Northrend look it had: Cinzel, gold corners, the shelf and the tiles).
 * Holding the Blizzard logo switches between them. Every shared piece ([FrameButton], [FrameTitle], [SettingCard],
 * [Segmented], [Modifier.panel], [drawFrame]) draws the look that is on, so every menu and popup follows.
 */
object Look {
    /**
     * Always true: the classic look has been archived (`archive/classic-look/`, see its README), its screens and its options out of
     * the app. The classic drawing of the shared pieces ([FrameButton], [Modifier.panel], [Colors]...) still sits behind this flag.
     */
    const val modern = true
}

/** The modern look's palette: near-black blue surfaces, white type, Blizzard blue as the one accent, gold kept for small honours. */
object Modern {
    val Background = Color(0xFF070B11)
    val Surface = Color(0xFF0F151E)
    val SurfaceHigh = Color(0xFF161E2A)
    val SurfaceTop = Color(0xFF1E2836)
    val Outline = Color(0x1FFFFFFF)
    val OutlineStrong = Color(0x33FFFFFF)
    val Text = Color(0xFFF3F6FA)
    val Muted = Color(0xFF93A1B4)
    val Faint = Color(0xFF5F6C7E)
    val Accent = Color(0xFF1A8CFF)
    val AccentBright = Color(0xFF45B4FF)
    val AccentSoft = Color(0x261A8CFF)
    val Gold = Color(0xFFF0B84C)
    val Good = Color(0xFF39D98A)
    val Warn = Color(0xFFF5A524)
    val Bad = Color(0xFFFF5D5D)

    val Corner = 16.dp
    val SheetCorner = 24.dp
    val ButtonCorner = 12.dp

    val AccentBrush = Brush.horizontalGradient(listOf(Color(0xFF1477E6), Color(0xFF2AA3FF)))
    val SheetBrush = Brush.verticalGradient(listOf(Color(0xFF131A25), Color(0xFF0C121A)))
}

/**
 * A popup's or a panel's surface, in the look that is on: Classic is the frost gradient with the gold-cornered frame; Modern a
 * rounded sheet with a hairline edge and a soft shadow. [fill] is Classic's colour (Modern keeps its own).
 */
fun Modifier.panel(fill: Brush? = null, corner: Dp = Modern.SheetCorner, elevated: Boolean = true): Modifier =
    if (Look.modern) {
        val shape = RoundedCornerShape(corner)
        (if (elevated) this.shadow(24.dp, shape, ambientColor = Color.Black, spotColor = Color.Black) else this)
            .clip(shape).background(Modern.SheetBrush).border(1.dp, Modern.Outline, shape)
    } else {
        this.drawBehind {
            drawRect(fill ?: Brush.verticalGradient(listOf(Colors.Night, Colors.Deep)))
            drawFrame()
        }
    }

/** A small framed box inside a panel (a choice, a note): Classic's bracket corners in [accent]; Modern a rounded card, tinted when [selected]. */
fun Modifier.box(accent: Color = Colors.Steel, selected: Boolean = false, corner: Dp = 12.dp): Modifier =
    if (Look.modern) {
        val shape = RoundedCornerShape(corner)
        this.clip(shape).background(if (selected) Modern.AccentSoft else Color.White.copy(alpha = 0.035f))
            .border(1.dp, if (selected) Modern.Accent.copy(alpha = 0.7f) else Modern.Outline, shape)
    } else {
        this.drawBehind {
            if (selected) drawRect(Colors.Ice.copy(alpha = 0.1f))
            drawFrame(corner = accent, arm = 6.dp.toPx(), line = if (selected) null else Colors.Steel)
        }
    }

/** The standard popup: a sheet with its title, an optional subtitle, a close button and its content, in the look that is on. */
@Composable
fun Sheet(
    title: String,
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    maxWidth: Dp = 600.dp,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(modifier.padding(14.dp).widthIn(max = maxWidth).fillMaxWidth().panel()) {
        Row(
            Modifier.fillMaxWidth().padding(start = if (Look.modern) 22.dp else 20.dp, end = 8.dp, top = if (Look.modern) 16.dp else 14.dp, bottom = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(Modifier.weight(1f)) {
                FrameTitle(title, style = if (Look.modern) MaterialTheme.typography.headlineSmall else MaterialTheme.typography.titleLarge)
                subtitle?.let { Text(it, style = MaterialTheme.typography.bodyMedium, color = if (Look.modern) Modern.Muted else Colors.Mist, modifier = Modifier.padding(top = 2.dp)) }
            }
            CloseButton(onClose)
        }
        content()
    }
}

@Composable
fun CloseButton(onClick: () -> Unit) {
    if (Look.modern) {
        Box(
            Modifier.padding(6.dp).size(36.dp).clip(CircleShape).background(Color.White.copy(alpha = 0.06f)).clickable(onClick = onClick),
            contentAlignment = Alignment.Center,
        ) { Icon(Icons.Default.Close, "Close", tint = Modern.Text, modifier = Modifier.size(20.dp)) }
    } else {
        Icon(Icons.Default.Close, "Close", tint = Colors.Mist, modifier = Modifier.clip(CircleShape).clickable(onClick = onClick).padding(12.dp).size(24.dp))
    }
}

/** A round icon button with a label under it (the home screen's actions). */
@Composable
fun ActionChip(icon: ImageVector, label: String, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val press by animateFloatAsState(if (pressed) 1f else 0f, spring(dampingRatio = 0.7f, stiffness = 800f), label = "press")
    Row(
        modifier
            .graphicsLayer { val k = 1f - 0.04f * press; scaleX = k; scaleY = k }
            .clip(RoundedCornerShape(Modern.ButtonCorner))
            .background(Color.White.copy(alpha = 0.07f + 0.05f * press))
            .border(1.dp, Modern.Outline, RoundedCornerShape(Modern.ButtonCorner))
            .clickable(interactionSource = interaction, indication = null, onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Icon(icon, null, tint = Modern.Text, modifier = Modifier.size(18.dp))
        Text(label, style = MaterialTheme.typography.labelLarge.copy(color = Modern.Text, fontSize = 14.sp), maxLines = 1)
    }
}

/** A small rounded tag: "Installed", "1998", "Not imported". */
@Composable
fun Tag(text: String, color: Color = Modern.Muted, filled: Boolean = false) {
    Text(
        text,
        style = MaterialTheme.typography.bodySmall.copy(color = color, fontWeight = FontWeight.Medium, fontSize = 12.sp),
        maxLines = 1, overflow = TextOverflow.Ellipsis,
        modifier = Modifier.clip(CircleShape)
            .background(if (filled) color.copy(alpha = 0.16f) else Color.White.copy(alpha = 0.06f))
            .padding(horizontal = 10.dp, vertical = 4.dp),
    )
}

/** A pill-shaped segmented switch with a sliding highlight: the modern [Segmented]. */
@Composable
internal fun <T> PillSegmented(options: List<Pair<String, T>>, selected: T, modifier: Modifier = Modifier, onSelect: (T) -> Unit) {
    val index = options.indexOfFirst { it.second == selected }.coerceAtLeast(0)
    BoxWithConstraints(
        modifier.fillMaxWidth().height(44.dp).clip(RoundedCornerShape(22.dp)).background(Color.White.copy(alpha = 0.06f))
            .border(1.dp, Modern.Outline, RoundedCornerShape(22.dp)).padding(4.dp),
    ) {
        val cell = maxWidth / options.size.coerceAtLeast(1)
        val x by androidx.compose.animation.core.animateDpAsState(cell * index, spring(dampingRatio = 0.8f, stiffness = 500f), label = "pill")
        Box(Modifier.offset(x = x).width(cell).fillMaxHeight().clip(RoundedCornerShape(18.dp)).background(Modern.AccentBrush))
        Row(Modifier.fillMaxWidth().fillMaxHeight()) {
            options.forEachIndexed { i, (label, value) ->
                val on = i == index
                val color by animateColorAsState(if (on) Color.White else Modern.Muted, label = "pillText")
                Box(
                    Modifier.weight(1f).fillMaxHeight().clip(RoundedCornerShape(18.dp))
                        .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) { onSelect(value) },
                    contentAlignment = Alignment.Center,
                ) { Text(label, style = MaterialTheme.typography.labelLarge.copy(color = color, fontSize = 14.sp), maxLines = 1, overflow = TextOverflow.Ellipsis) }
            }
        }
    }
}

/** A section heading inside a sheet or page: small, quiet, in capitals. */
@Composable
fun SectionLabel(text: String, modifier: Modifier = Modifier) {
    Text(
        text.uppercase(),
        style = MaterialTheme.typography.bodySmall.copy(color = Modern.Muted, fontWeight = FontWeight.Medium, letterSpacing = 1.2.sp, fontSize = 11.sp),
        modifier = modifier,
    )
}

@Suppress("unused")
@Composable
private fun Dp.px(): Float = with(LocalDensity.current) { this@px.toPx() }

/** Spacer helpers kept local to the look. */
@Composable
fun Gap(height: Dp) = Spacer(Modifier.height(height))

/** A thin divider in the look that is on. */
@Composable
fun Divider(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxWidth().height(1.dp).background(if (Look.modern) Modern.Outline else Colors.Steel.copy(alpha = 0.6f)))
}

/** The heightIn helper for sheets' scrolling bodies. */
fun Modifier.sheetBody(maxHeight: Dp = 760.dp): Modifier = this.heightIn(max = maxHeight)
