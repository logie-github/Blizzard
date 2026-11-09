package com.logie.blizz.game

import android.app.Activity
import android.view.Gravity
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
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
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.logie.blizz.controls.KeyCombo
import com.logie.blizz.ui.BlizzTheme
import com.logie.blizz.ui.Colors

/**
 * The app's own keyboard's keys: a PC keyboard in six rows, every key one the X server has ([KeyCombo.KEYS], so what the
 * Controls can bind the keyboard can type), with the function keys and the arrows the games use and the phone's keyboard
 * has not. Plain Kotlin, unit-tested.
 */
object KeyboardLayout {
    /** The key that puts the keyboard away (not a key of the game's). */
    const val HIDE = "Hide"

    /**
     * One cap: [key] a [KeyCombo.KEYS] name (or [HIDE]); [label] what the cap shows (the key's name when null); [shifted] its label
     * while Shift is down; [weight] its width against a letter's.
     */
    data class Key(val key: String, val label: String? = null, val shifted: String? = null, val weight: Float = 1f) {
        /** Shift, Ctrl and Alt stay down for the next key instead of being typed. */
        val modifier: Boolean get() = key == "Shift" || key == "Ctrl" || key == "Alt"
        fun cap(shift: Boolean): String = (if (shift) shifted else null) ?: label ?: key
    }

    private fun k(key: String, label: String? = null, shifted: String? = null, weight: Float = 1f) = Key(key, label, shifted, weight)
    private fun letters(s: String) = s.map { k(it.toString(), it.lowercaseChar().toString(), it.toString()) }
    private val DIGITS = listOf("1" to "!", "2" to "@", "3" to "#", "4" to "$", "5" to "%", "6" to "^", "7" to "&", "8" to "*", "9" to "(", "0" to ")")

    val ROWS: List<List<Key>> = listOf(
        listOf(k("Esc", weight = 1.4f)) + (1..12).map { k("F$it", weight = 0.95f) } + listOf(k("Delete", "Del", weight = 1.4f)),
        listOf(k("`", "`", "~")) + DIGITS.map { (d, s) -> k(d, d, s) } + listOf(k("-", "-", "_"), k("=", "=", "+"), k("Backspace", "⌫", weight = 1.7f)),
        listOf(k("Tab", weight = 1.5f)) + letters("QWERTYUIOP") + listOf(k("[", "[", "{"), k("]", "]", "}"), k("\\", "\\", "|", weight = 1.2f)),
        listOf(k("Shift", weight = 1.9f)) + letters("ASDFGHJKL") + listOf(k(";", ";", ":"), k("'", "'", "\""), k("Enter", weight = 1.8f)),
        listOf(k("Ctrl", weight = 1.4f), k("Alt", weight = 1.4f)) + letters("ZXCVBNM") + listOf(k(",", ",", "<"), k(".", ".", ">"), k("/", "/", "?"), k("Up", "▲"), k("Insert", "Ins")),
        listOf(k("PgUp"), k("PgDn"), k("Home"), k("Space", weight = 5f), k("End"), k("Left", "◀"), k("Down", "▼"), k("Right", "▶"), k(HIDE, weight = 1.6f)),
    )
}

/**
 * The app's own keyboard over the game, for the games' names, cheats and keys (Esc, F-keys, arrows): a panel at the bottom
 * of the screen, drawn by the app, whose keys go to the X server as pressed, while the game above it still takes the
 * touches. Three fingers or the menu show it; Back or its Hide key puts it away. The phone's own keyboard (a prompt whose
 * text is typed in when sent, [GamePrompt]) stays for longer text: it needs nothing of the system's keyboard to show up.
 */
class GameKeyboard(private val activity: Activity, private val host: () -> ViewGroup?, private val onKey: (String, Set<String>) -> Unit) {
    private var view: ComposeView? = null
    val shown: Boolean get() = view != null

    fun toggle() = if (shown) hide() else show()

    fun show() {
        if (view != null) return
        val parent = host() ?: return
        val v = ComposeView(activity).apply { setContent { BlizzTheme { KeyboardPanel(onKey, ::hide) } } }
        parent.addView(v, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM))
        view = v
    }

    fun hide() {
        view?.let { (it.parent as? ViewGroup)?.removeView(it) }
        view = null
    }
}

@Composable
private fun KeyboardPanel(onKey: (String, Set<String>) -> Unit, onHide: () -> Unit) {
    var shift by remember { mutableStateOf(false) }
    var ctrl by remember { mutableStateOf(false) }
    var alt by remember { mutableStateOf(false) }
    // Six rows in at most two fifths of the screen, 30 to 42 dp a key.
    val keyHeight = (LocalConfiguration.current.screenHeightDp * 0.4f / KeyboardLayout.ROWS.size).coerceIn(30f, 42f).dp
    Column(
        Modifier
            .fillMaxWidth()
            .background(Colors.Abyss.copy(alpha = 0.93f))
            // The panel takes its touches: nothing under it is clicked through it.
            .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) {}
            .padding(horizontal = 6.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        for (row in KeyboardLayout.ROWS) {
            Row(Modifier.fillMaxWidth().height(keyHeight), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                for (key in row) {
                    val lit = (key.key == "Shift" && shift) || (key.key == "Ctrl" && ctrl) || (key.key == "Alt" && alt)
                    Cap(key.cap(shift), lit, key.weight) {
                        when {
                            key.key == KeyboardLayout.HIDE -> onHide()
                            key.key == "Shift" -> shift = !shift
                            key.key == "Ctrl" -> ctrl = !ctrl
                            key.key == "Alt" -> alt = !alt
                            else -> {
                                onKey(key.key, buildSet { if (shift) add("Shift"); if (ctrl) add("Ctrl"); if (alt) add("Alt") })
                                shift = false; ctrl = false; alt = false
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun RowScope.Cap(label: String, lit: Boolean, weight: Float, onClick: () -> Unit) {
    val haptics = LocalHapticFeedback.current
    val shape = RoundedCornerShape(6.dp)
    Box(
        Modifier
            .weight(weight)
            .fillMaxHeight()
            .clip(shape)
            .background(if (lit) Colors.Ice.copy(alpha = 0.45f) else Colors.Deep.copy(alpha = 0.95f))
            .border(1.dp, if (lit) Colors.Ice else Colors.Steel, shape)
            .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) {
                haptics.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                onClick()
            },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium.copy(fontSize = if (label.length > 3) 11.sp else 14.sp, fontWeight = FontWeight.Medium),
            color = Colors.Text,
            textAlign = TextAlign.Center,
            maxLines = 1,
        )
    }
}
