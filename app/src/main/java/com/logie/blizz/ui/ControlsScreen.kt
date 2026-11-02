package com.logie.blizz.ui

import android.annotation.SuppressLint
import android.view.MotionEvent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.CropFree
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material.icons.filled.Mouse
import androidx.compose.material.icons.filled.RestartAlt
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.foundation.focusable
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.isAltPressed
import androidx.compose.ui.input.key.isCtrlPressed
import androidx.compose.ui.input.key.isShiftPressed
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.type
import androidx.compose.ui.input.key.utf16CodePoint
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.pointerInteropFilter
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.controls.Area
import com.logie.blizz.controls.Bindings
import com.logie.blizz.controls.Catalog
import com.logie.blizz.controls.ControlsStore
import com.logie.blizz.controls.GameControls
import com.logie.blizz.controls.GameFunction
import com.logie.blizz.controls.GestureOutput
import com.logie.blizz.controls.Gestures
import com.logie.blizz.controls.KeyCombo
import com.logie.blizz.controls.Kind
import com.logie.blizz.controls.Rule
import com.logie.blizz.controls.Trigger
import kotlinx.coroutines.delay
import java.io.File

/** A game's controls: every function with its key and its gestures, and the gesture rules. */
@Composable
fun ControlsScreen(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val store = remember { ControlsStore(File(context.filesDir, "controls")) }
    val catalog = remember(game.id) { Catalog.of(game.id) }
    var controls by remember(game.id) { mutableStateOf(store.load(game.id)) }
    fun update(c: GameControls) { controls = c; store.save(c) }
    val bindings = Bindings(catalog, controls)
    var tab by remember { mutableStateOf(0) }
    var keyFor by remember { mutableStateOf<GameFunction?>(null) }
    var editing by remember { mutableStateOf<Pair<Int?, Rule>?>(null) }
    var recordFor by remember { mutableStateOf<String?>(null) }
    var recording by remember { mutableStateOf(false) }

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.fillMaxSize().background(Colors.Abyss).windowInsetsPadding(WindowInsets.safeDrawing).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                FrameTitle(game.fullTitle, Modifier.weight(1f))
                IconChip(Icons.Default.RestartAlt) { store.reset(game.id); controls = store.load(game.id) }
                IconChip(Icons.Default.Close, onClick = onDismiss)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Tab("Hotkeys", tab == 0) { tab = 0 }
                Tab("Gestures", tab == 1) { tab = 1 }
                Spacer(Modifier.weight(1f))
                IconChip(Icons.Default.FiberManualRecord, tint = Colors.Gold) { recordFor = null; recording = true }
            }
            if (tab == 0) {
                LazyColumn(Modifier.fillMaxWidth().weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    items(catalog.functions.filter { it.kind != Kind.NONE }, key = { it.id }) { function ->
                        HotkeyRow(
                            function, bindings, catalog,
                            onKey = { keyFor = function },
                            onRule = { rule -> editing = controls.rules.indexOf(rule) to rule },
                            onAdd = { recordFor = function.id; recording = true },
                        )
                    }
                }
            } else {
                LazyColumn(Modifier.fillMaxWidth().weight(1f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    items(controls.rules.withIndex().sortedBy { it.value.trigger.ordinal }.toList(), key = { "${it.index}:${it.value}" }) { (index, rule) ->
                        RuleRow(rule, catalog,
                            onChange = { new -> update(controls.copy(rules = controls.rules.toMutableList().also { it[index] = new })) },
                            onArea = { editing = index to rule },
                            onDelete = { update(controls.copy(rules = controls.rules.filterIndexed { i, _ -> i != index })) })
                    }
                    item {
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 6.dp)) {
                            IconChip(Icons.Default.Add) { editing = null to Rule(Trigger.TAP, Area.ANYWHERE.id, "click") }
                        }
                    }
                }
            }
        }
        keyFor?.let { f ->
            KeyPicker(bindings.keyOf(f), onDismiss = { keyFor = null }) { combo ->
                update(controls.copy(keys = controls.keys + (f.id to combo)))
                keyFor = null
            }
        }
        if (recording) {
            Recorder(catalog, initialFunction = recordFor, onDismiss = { recording = false }) { rule ->
                update(controls.copy(rules = controls.rules.filterNot { it.trigger == rule.trigger && it.area == rule.area } + rule))
                recording = false
            }
        }
        editing?.let { (index, rule) ->
            Recorder(catalog, initial = rule, onDismiss = { editing = null }, onDelete = index?.let { i -> {
                update(controls.copy(rules = controls.rules.filterIndexed { j, _ -> j != i }))
                editing = null
            } }) { new ->
                update(controls.copy(rules = if (index == null) controls.rules.filterNot { it.trigger == new.trigger && it.area == new.area } + new else controls.rules.toMutableList().also { it[index] = new }))
                editing = null
            }
        }
    }
}

// Pieces -------------------------------------------------------------------------------------

@Composable
private fun Tab(text: String, selected: Boolean, onClick: () -> Unit) {
    Text(
        text.uppercase(),
        style = DisplayStyle.copy(fontSize = 13.sp, color = if (selected) Colors.Gold else Colors.Mist),
        modifier = Modifier.clip(RoundedCornerShape(4.dp)).clickable(onClick = onClick)
            .drawBehind { if (selected) drawFrame(arm = 6.dp.toPx(), line = null) }.padding(horizontal = 14.dp, vertical = 10.dp),
    )
}

@Composable
private fun IconChip(icon: androidx.compose.ui.graphics.vector.ImageVector, tint: Color = Colors.Mist, onClick: () -> Unit) {
    Icon(icon, null, tint = tint, modifier = Modifier.clip(RoundedCornerShape(50)).clickable(onClick = onClick).padding(8.dp).size(22.dp))
}

@Composable
private fun Chip(text: String, color: Color = Colors.Text, onClick: (() -> Unit)?) {
    Text(
        text,
        style = MaterialTheme.typography.bodyMedium.copy(color = color),
        maxLines = 1,
        modifier = Modifier.clip(RoundedCornerShape(4.dp)).background(Colors.Deep).border(1.dp, Colors.Steel, RoundedCornerShape(4.dp))
            .let { if (onClick != null) it.clickable(onClick = onClick) else it }.padding(horizontal = 10.dp, vertical = 6.dp),
    )
}

/** A mouse function's sign, in place of a key. */
private fun mouseSign(kind: Kind): String = when (kind) {
    Kind.CLICK_LEFT -> "L"; Kind.CLICK_RIGHT -> "R"; Kind.DOUBLE_LEFT -> "L×2"; Kind.SHIFT_LEFT -> "Shift+L"
    Kind.SHIFT_RIGHT -> "Shift+R"; Kind.CTRL_LEFT -> "Ctrl+L"; Kind.DRAG_LEFT -> "L drag"; Kind.PAN -> "Arrows"
    Kind.WHEEL_UP -> "Wheel ▲"; Kind.WHEEL_DOWN -> "Wheel ▼"; Kind.PHONE_KEYBOARD -> "⌨"; Kind.APP_MENU -> "☰"; else -> "—"
}

private fun ruleLabel(rule: Rule, catalog: Catalog.Game): String {
    val area = catalog.area(rule.area)
    return if (area == null || area.id == Area.ANYWHERE.id) rule.trigger.label else "${rule.trigger.label} · ${area.label}"
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun HotkeyRow(function: GameFunction, bindings: Bindings, catalog: Catalog.Game, onKey: () -> Unit, onRule: (Rule) -> Unit, onAdd: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(function.label, style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
        Box(Modifier.widthIn(min = 92.dp), contentAlignment = Alignment.Center) {
            if (function.kind.usesKey) Chip(bindings.keyOf(function)?.label ?: "—", Colors.Gold, onKey) else Chip(mouseSign(function.kind), Colors.Mist, null)
        }
        FlowRow(Modifier.weight(1.2f).padding(start = 10.dp), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            for (rule in bindings.rulesFor(function.id)) Chip(ruleLabel(rule, catalog), Colors.Ice) { onRule(rule) }
            Icon(Icons.Default.Add, null, tint = Colors.Steel, modifier = Modifier.clip(RoundedCornerShape(50)).clickable(onClick = onAdd).padding(4.dp).size(20.dp))
        }
    }
}

@Composable
private fun RuleRow(rule: Rule, catalog: Catalog.Game, onChange: (Rule) -> Unit, onArea: () -> Unit, onDelete: () -> Unit) {
    var pick by remember { mutableStateOf(0) }
    Row(Modifier.fillMaxWidth().drawBehind { drawFrame(corner = Colors.Steel, arm = 5.dp.toPx(), line = null) }.padding(10.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("If", color = Colors.Mist, style = MaterialTheme.typography.bodyMedium)
        Chip(rule.trigger.label, Colors.Ice) { pick = 1 }
        Chip(catalog.area(rule.area)?.label ?: "?", Colors.Ice, onArea)
        Text("→", color = Colors.Mist)
        Box(Modifier.weight(1f)) { Chip(catalog.function(rule.function)?.label ?: rule.function, Colors.Gold) { pick = 2 } }
        IconChip(Icons.Default.Close, onClick = onDelete)
    }
    if (pick == 1) ListPicker(Trigger.entries.map { it.label }, onDismiss = { pick = 0 }) { i -> onChange(rule.copy(trigger = Trigger.entries[i])); pick = 0 }
    if (pick == 2) FunctionPicker(catalog, onDismiss = { pick = 0 }) { f -> onChange(rule.copy(function = f.id)); pick = 0 }
}

@Composable
private fun PanelDialog(onDismiss: () -> Unit, content: @Composable () -> Unit) {
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Box(Modifier.padding(18.dp).widthIn(max = 640.dp).fillMaxWidth().drawBehind { drawRect(Colors.Deep); drawFrame() }.padding(16.dp)) { content() }
    }
}

@Composable
private fun ListPicker(items: List<String>, onDismiss: () -> Unit, onPick: (Int) -> Unit) {
    PanelDialog(onDismiss) {
        LazyColumn(Modifier.heightIn(max = 520.dp)) {
            items(items.indices.toList()) { i ->
                Text(items[i], style = MaterialTheme.typography.titleMedium, modifier = Modifier.fillMaxWidth().clickable { onPick(i) }.padding(12.dp))
            }
        }
    }
}

@Composable
private fun FunctionPicker(catalog: Catalog.Game, onDismiss: () -> Unit, onPick: (GameFunction) -> Unit) {
    val functions = catalog.functions
    ListPicker(functions.map { f -> f.label + (f.key?.let { "  ·  ${it.label}" } ?: "") }, onDismiss) { onPick(functions[it]) }
}

/** A key: pressed on a keyboard, or picked, with Ctrl, Alt and Shift. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun KeyPicker(current: KeyCombo?, onDismiss: () -> Unit, onPick: (KeyCombo) -> Unit) {
    var ctrl by remember { mutableStateOf(current?.ctrl == true) }
    var alt by remember { mutableStateOf(current?.alt == true) }
    var shift by remember { mutableStateOf(current?.shift == true) }
    val focus = remember { FocusRequester() }
    LaunchedEffect(Unit) { runCatching { focus.requestFocus() } }
    PanelDialog(onDismiss) {
        Column(
            Modifier.focusRequester(focus).focusable().onPreviewKeyEvent { e ->
                if (e.type != KeyEventType.KeyDown) return@onPreviewKeyEvent false
                val name = keyName(e.nativeKeyEvent.keyCode, e.utf16CodePoint) ?: return@onPreviewKeyEvent false
                if (name in listOf("Ctrl", "Alt", "Shift")) return@onPreviewKeyEvent false
                onPick(KeyCombo(name, e.isCtrlPressed, e.isShiftPressed, e.isAltPressed))
                true
            }.verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Chip("Ctrl", if (ctrl) Colors.Gold else Colors.Mist) { ctrl = !ctrl }
                Chip("Alt", if (alt) Colors.Gold else Colors.Mist) { alt = !alt }
                Chip("Shift", if (shift) Colors.Gold else Colors.Mist) { shift = !shift }
            }
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                for (k in KeyCombo.KEYS) Chip(k, if (k == current?.key) Colors.Gold else Colors.Text) { onPick(KeyCombo(k, ctrl, shift, alt)) }
            }
        }
    }
}

/** An Android key code as a [KeyCombo.KEYS] name. */
private fun keyName(code: Int, char: Int): String? {
    val k = android.view.KeyEvent::class.java
    fun c(name: String) = runCatching { k.getField(name).getInt(null) }.getOrDefault(-1)
    return when (code) {
        in c("KEYCODE_A")..c("KEYCODE_Z") -> ('A' + (code - c("KEYCODE_A"))).toString()
        in c("KEYCODE_0")..c("KEYCODE_9") -> ('0' + (code - c("KEYCODE_0"))).toString()
        in c("KEYCODE_F1")..c("KEYCODE_F12") -> "F${code - c("KEYCODE_F1") + 1}"
        c("KEYCODE_ESCAPE") -> "Esc"; c("KEYCODE_ENTER") -> "Enter"; c("KEYCODE_TAB") -> "Tab"; c("KEYCODE_SPACE") -> "Space"
        c("KEYCODE_DEL") -> "Backspace"; c("KEYCODE_FORWARD_DEL") -> "Delete"; c("KEYCODE_DPAD_UP") -> "Up"; c("KEYCODE_DPAD_DOWN") -> "Down"
        c("KEYCODE_DPAD_LEFT") -> "Left"; c("KEYCODE_DPAD_RIGHT") -> "Right"; c("KEYCODE_PAGE_UP") -> "PgUp"; c("KEYCODE_PAGE_DOWN") -> "PgDn"
        c("KEYCODE_MOVE_HOME") -> "Home"; c("KEYCODE_MOVE_END") -> "End"; c("KEYCODE_INSERT") -> "Insert"; c("KEYCODE_SYSRQ") -> "PrtSc"
        c("KEYCODE_SHIFT_LEFT"), c("KEYCODE_SHIFT_RIGHT") -> "Shift"; c("KEYCODE_CTRL_LEFT"), c("KEYCODE_CTRL_RIGHT") -> "Ctrl"
        c("KEYCODE_ALT_LEFT"), c("KEYCODE_ALT_RIGHT") -> "Alt"
        else -> char.takeIf { it > 0 }?.toChar()?.toString()?.takeIf { it in KeyCombo.KEYS }
    }
}

/**
 * The gesture recorder: do a gesture on the pad (the game's screen) and it's named, with where it
 * was; change either, pick what it does, save. The square draws a custom area instead.
 */
@SuppressLint("ClickableViewAccessibility")
@OptIn(ExperimentalComposeUiApi::class, ExperimentalLayoutApi::class)
@Composable
private fun Recorder(
    catalog: Catalog.Game,
    initial: Rule? = null,
    initialFunction: String? = null,
    onDismiss: () -> Unit,
    onDelete: (() -> Unit)? = null,
    onSave: (Rule) -> Unit,
) {
    var trigger by remember { mutableStateOf(initial?.trigger) }
    var area by remember { mutableStateOf(initial?.area?.let { catalog.area(it) }) }
    var function by remember { mutableStateOf(catalog.function(initial?.function ?: initialFunction ?: "")) }
    var drawing by remember { mutableStateOf(false) }
    var dragStart by remember { mutableStateOf<Offset?>(null) }
    var pad by remember { mutableStateOf(IntSize.Zero) }
    var pick by remember { mutableStateOf(0) }
    val density = LocalDensity.current.density
    val recorder = remember {
        Gestures(NoOutput, density, bindings = null,
            locate = { x, y -> (x / pad.width.coerceAtLeast(1)) to (y / pad.height.coerceAtLeast(1)) },
            onRecord = { t, x, y ->
                trigger = t
                val nx = x / pad.width.coerceAtLeast(1)
                val ny = y / pad.height.coerceAtLeast(1)
                area = suggestArea(catalog, t, nx, ny)
            })
    }
    var ticks by remember { mutableStateOf(0) }
    LaunchedEffect(ticks) {
        while (recorder.needsTicks()) {
            delay(30)
            recorder.tick(android.os.SystemClock.uptimeMillis())
        }
    }

    PanelDialog(onDismiss) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Box(
                Modifier.fillMaxWidth().aspectRatio(4f / 3f).background(Colors.Abyss).border(1.dp, Colors.Steel)
                    .onSizeChanged { pad = it }
                    .let { m ->
                        if (drawing) m.pointerInput(Unit) {
                            detectDragGestures(
                                onDragStart = { dragStart = it },
                                onDrag = { change, _ ->
                                    val s = dragStart ?: return@detectDragGestures
                                    val e = change.position
                                    area = Area.custom(
                                        (minOf(s.x, e.x) / size.width).coerceIn(0f, 1f), (minOf(s.y, e.y) / size.height).coerceIn(0f, 1f),
                                        (maxOf(s.x, e.x) / size.width).coerceIn(0f, 1f), (maxOf(s.y, e.y) / size.height).coerceIn(0f, 1f),
                                    )
                                },
                                onDragEnd = { drawing = false },
                            )
                        } else m.pointerInteropFilter { e ->
                            val i = e.actionIndex
                            when (e.actionMasked) {
                                MotionEvent.ACTION_DOWN, MotionEvent.ACTION_POINTER_DOWN -> recorder.down(e.getPointerId(i), e.getX(i), e.getY(i), e.eventTime)
                                MotionEvent.ACTION_MOVE -> recorder.move(List(e.pointerCount) { j -> Gestures.Touch(e.getPointerId(j), e.getX(j), e.getY(j)) }, e.eventTime)
                                MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> recorder.up(e.getPointerId(i), e.getX(i), e.getY(i), e.eventTime)
                                MotionEvent.ACTION_CANCEL -> recorder.cancel()
                            }
                            ticks++
                            true
                        }
                    }
                    .drawBehind {
                        // The game's areas, faint; the chosen one lit.
                        for (a in catalog.areas.filter { it.size < 0.3f && it.id !in STANDARD_IDS }) {
                            drawRect(Colors.Steel.copy(alpha = 0.5f), Offset(a.left * size.width, a.top * size.height), Size((a.right - a.left) * size.width, (a.bottom - a.top) * size.height), style = Stroke(1.dp.toPx()))
                        }
                        area?.let { a ->
                            val o = Offset(a.left * size.width, a.top * size.height)
                            val s = Size((a.right - a.left) * size.width, (a.bottom - a.top) * size.height)
                            drawRect(Colors.Ice.copy(alpha = 0.18f), o, s)
                            drawRect(Colors.Ice, o, s, style = Stroke(2.dp.toPx()))
                        }
                    },
            ) {
                Icon(Icons.Default.CropFree, null, tint = if (drawing) Colors.Gold else Colors.Mist,
                    modifier = Modifier.align(Alignment.TopEnd).padding(6.dp).clip(RoundedCornerShape(50)).clickable { drawing = !drawing }.padding(6.dp).size(22.dp))
            }
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("If", color = Colors.Mist)
                Chip(trigger?.label ?: "…", Colors.Ice) { pick = 1 }
                Chip(area?.label ?: Area.ANYWHERE.label, Colors.Ice) { pick = 2 }
                Text("→", color = Colors.Mist)
                Chip(function?.label ?: "…", Colors.Gold) { pick = 3 }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End)) {
                if (onDelete != null) FrameButton("Delete", primary = false, onClick = onDelete)
                FrameButton("Save") {
                    val t = trigger ?: return@FrameButton
                    val f = function ?: return@FrameButton
                    onSave(Rule(t, (area ?: Area.ANYWHERE).id, f.id))
                }
            }
        }
    }
    if (pick == 1) ListPicker(Trigger.entries.map { it.label }, onDismiss = { pick = 0 }) { trigger = Trigger.entries[it]; pick = 0 }
    if (pick == 2) ListPicker(catalog.areas.map { it.label }, onDismiss = { pick = 0 }) { area = catalog.areas[it]; pick = 0 }
    if (pick == 3) FunctionPicker(catalog, onDismiss = { pick = 0 }) { function = it; pick = 0 }
}

private val STANDARD_IDS = Area.STANDARD.map { it.id }.toSet()

/** Where a recorded gesture was: the game's own area there, else its quarter; anywhere for multi-finger ones and flicks. */
internal fun suggestArea(catalog: Catalog.Game, trigger: Trigger, x: Float, y: Float): Area {
    if (trigger in listOf(Trigger.TWO_FINGER_TAP, Trigger.THREE_FINGER_TAP, Trigger.FOUR_FINGER_TAP, Trigger.TWO_THEN_ONE_TAP, Trigger.PINCH_IN, Trigger.PINCH_OUT) || trigger.isFlick) {
        return Area.ANYWHERE
    }
    catalog.areas.filter { it.id !in STANDARD_IDS && it.contains(x, y) }.minByOrNull { it.size }?.let { return it }
    val quarter = (if (y < 0.5f) "top-" else "bottom-") + (if (x < 0.5f) "left" else "right")
    return catalog.area(quarter) ?: Area.ANYWHERE
}

private object NoOutput : GestureOutput {
    override fun pointerTo(x: Float, y: Float) {}
    override fun click(button: com.logie.blizz.controls.Button) {}
    override fun doubleClick(button: com.logie.blizz.controls.Button) {}
    override fun buttonDown(button: com.logie.blizz.controls.Button) {}
    override fun buttonUp(button: com.logie.blizz.controls.Button) {}
    override fun wheel(up: Boolean) {}
    override fun keyDown(key: String) {}
    override fun keyUp(key: String) {}
    override fun openKeyboard() {}
    override fun showMenu() {}
    override fun feedback() {}
}

/** The Controls button on a game's page. */
@Composable
fun ControlsButton(shown: Game) {
    val game = effectiveGame(shown)
    var open by remember { mutableStateOf(false) }
    Icon(Icons.Default.Mouse, contentDescription = "Controls", tint = Colors.Mist,
        modifier = Modifier.clip(RoundedCornerShape(50)).clickable { open = true }.padding(10.dp).size(26.dp))
    if (open) ControlsScreen(game, onDismiss = { open = false })
}
