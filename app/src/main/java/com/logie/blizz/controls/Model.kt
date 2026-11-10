package com.logie.blizz.controls

import org.json.JSONArray
import org.json.JSONObject

/** What the fingers did. */
enum class Trigger(val label: String) {
    TAP("Tap"),
    DOUBLE_TAP("Double tap"),
    HOLD("Hold"),
    DOUBLE_TAP_HOLD("Double tap hold"),
    DRAG("Drag"),
    /** A drag that starts after the finger has rested (the hold's buzz): a selection box where a plain drag scrolls. */
    HOLD_DRAG("Hold, then drag"),
    FLICK_UP("Flick up"),
    FLICK_DOWN("Flick down"),
    FLICK_LEFT("Flick left"),
    FLICK_RIGHT("Flick right"),
    TWO_FINGER_TAP("Two-finger tap"),
    TWO_THEN_ONE_TAP("Two then one tap"),
    THREE_FINGER_TAP("Three-finger tap"),
    FOUR_FINGER_TAP("Four-finger tap"),
    PINCH_OUT("Pinch out"),
    PINCH_IN("Pinch in"),
    REST_TAP("Rest + tap"),
    REST_HOLD("Rest + hold");

    val isFlick: Boolean get() = this == FLICK_UP || this == FLICK_DOWN || this == FLICK_LEFT || this == FLICK_RIGHT
}

/** Where on the game's screen, in fractions of it (0..1). */
data class Area(val id: String, val label: String, val left: Float, val top: Float, val right: Float, val bottom: Float) {
    fun contains(x: Float, y: Float) = x >= left && x <= right && y >= top && y <= bottom
    val size: Float get() = (right - left) * (bottom - top)

    companion object {
        val ANYWHERE = Area("anywhere", "Anywhere", 0f, 0f, 1f, 1f)
        val STANDARD = listOf(
            ANYWHERE,
            Area("top-left", "Top left", 0f, 0f, 0.5f, 0.5f),
            Area("top-right", "Top right", 0.5f, 0f, 1f, 0.5f),
            Area("bottom-left", "Bottom left", 0f, 0.5f, 0.5f, 1f),
            Area("bottom-right", "Bottom right", 0.5f, 0.5f, 1f, 1f),
            Area("top", "Top", 0f, 0f, 1f, 0.5f),
            Area("bottom", "Bottom", 0f, 0.5f, 1f, 1f),
            Area("left", "Left", 0f, 0f, 0.5f, 1f),
            Area("right", "Right", 0.5f, 0f, 1f, 1f),
            Area("center", "Center", 1f / 3, 1f / 3, 2f / 3, 2f / 3),
            Area("top-edge", "Top edge", 0f, 0f, 1f, 0.1f),
            Area("bottom-edge", "Bottom edge", 0f, 0.9f, 1f, 1f),
        )

        fun custom(left: Float, top: Float, right: Float, bottom: Float) =
            Area("custom:%.3f,%.3f,%.3f,%.3f".format(java.util.Locale.ROOT, left, top, right, bottom), "Custom", left, top, right, bottom)

        fun parseCustom(id: String): Area? {
            if (!id.startsWith("custom:")) return null
            val v = id.removePrefix("custom:").split(',').mapNotNull { it.toFloatOrNull() }
            return if (v.size == 4) custom(v[0], v[1], v[2], v[3]) else null
        }
    }
}

/** How a function acts in the game. */
enum class Kind {
    /** A mouse button clicked where the fingers are. */
    CLICK_LEFT, CLICK_RIGHT, DOUBLE_LEFT, SHIFT_LEFT, SHIFT_RIGHT, CTRL_LEFT,
    /**
     * A click whose button the game screen picks from what the game shows ([GestureOutput.smartButton]): the left button
     * to select or press, the right to order what is selected.
     */
    SMART_CLICK,
    /** The left button held while the finger moves (walk, box-select). */
    DRAG_LEFT,
    /** The arrow keys toward where the finger goes, held while it's away. */
    PAN,
    WHEEL_UP, WHEEL_DOWN,
    /** Its key pressed and let go. */
    KEY,
    /** Its key held for as long as the finger stays (a hold or a drag). */
    KEY_HOLD,
    /**
     * Its key (the game's menu), or Escape while the game shows something to leave ([GestureOutput.leaving]): a scene to skip,
     * a menu page or a box to close, a command waiting for its target to call off.
     */
    KEY_OR_ESCAPE,
    PHONE_KEYBOARD, APP_MENU, NONE;

    val usesKey: Boolean get() = this == KEY || this == KEY_HOLD || this == KEY_OR_ESCAPE
}

/** Something a game does: its name, how it acts, and its key (for [Kind.KEY] and [Kind.KEY_HOLD]). */
data class GameFunction(val id: String, val label: String, val kind: Kind, val key: KeyCombo? = null)

/** If [trigger] in [area] then [function]. */
data class Rule(val trigger: Trigger, val area: String, val function: String) {
    fun toJson(): JSONObject = JSONObject().put("trigger", trigger.name).put("area", area).put("function", function)

    companion object {
        fun fromJson(o: JSONObject): Rule? {
            val trigger = Trigger.entries.firstOrNull { it.name == o.optString("trigger") } ?: return null
            return Rule(trigger, o.optString("area", Area.ANYWHERE.id), o.optString("function"))
        }
    }
}

/** A game's controls: its functions' keys (as the person set them) and its gesture rules. */
data class GameControls(val gameId: String, val keys: Map<String, KeyCombo>, val rules: List<Rule>) {
    fun toJson(): JSONObject = JSONObject()
        .put("game", gameId)
        .put("keys", JSONObject().apply { keys.forEach { (id, combo) -> put(id, combo.label) } })
        .put("rules", JSONArray(rules.map { it.toJson() }))

    companion object {
        fun fromJson(o: JSONObject): GameControls {
            val keys = o.optJSONObject("keys")?.let { k -> k.keys().asSequence().mapNotNull { id -> KeyCombo.parse(k.getString(id))?.let { id to it } }.toMap() } ?: emptyMap()
            val rules = o.optJSONArray("rules")?.let { a -> (0 until a.length()).mapNotNull { Rule.fromJson(a.getJSONObject(it)) } } ?: emptyList()
            return GameControls(o.optString("game"), keys, rules)
        }
    }
}
