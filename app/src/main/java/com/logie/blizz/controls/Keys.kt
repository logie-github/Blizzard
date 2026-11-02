package com.logie.blizz.controls

/**
 * A key and its modifiers ("Ctrl+1", "Shift+F2", "S"): what a function presses. [key] is one of
 * [KEYS]' names. Plain Kotlin, unit-tested.
 */
data class KeyCombo(val key: String, val ctrl: Boolean = false, val shift: Boolean = false, val alt: Boolean = false) {
    val label: String get() = buildString {
        if (ctrl) append("Ctrl+")
        if (alt) append("Alt+")
        if (shift) append("Shift+")
        append(key)
    }

    override fun toString() = label

    companion object {
        /** Every key the games can be sent, in the picker's order. */
        val KEYS: List<String> = ('A'..'Z').map { it.toString() } + ('0'..'9').map { it.toString() } +
            (1..12).map { "F$it" } +
            listOf("Esc", "Enter", "Tab", "Space", "Backspace", "Up", "Down", "Left", "Right", "Shift", "Ctrl", "Alt",
                "Insert", "Delete", "Home", "End", "PgUp", "PgDn", "PrtSc", "`", "-", "=", "[", "]", ";", "'", ",", ".", "/", "\\",
                "NumPlus", "NumMinus", "NumStar", "NumSlash", "NumEnter")

        fun parse(text: String?): KeyCombo? {
            if (text.isNullOrBlank()) return null
            val parts = text.split('+').map { it.trim() }.let { if (text.endsWith("++")) it.dropLast(2) + "+" else it }
            val key = parts.last().ifEmpty { return null }
            val mods = parts.dropLast(1).map { it.lowercase() }
            if (mods.any { it !in setOf("ctrl", "alt", "shift") }) return null
            val name = KEYS.firstOrNull { it.equals(key, ignoreCase = true) } ?: return null
            return KeyCombo(name, ctrl = "ctrl" in mods, shift = "shift" in mods, alt = "alt" in mods)
        }

        fun of(text: String) = parse(text) ?: error("not a key: $text")
    }
}

/** The X server's name for a key ([KeyCombo.KEYS] name → Winlator's XKeycode constant). */
fun xKeyName(key: String): String = "KEY_" + when (key) {
    "Esc" -> "ESC"; "Enter" -> "ENTER"; "Tab" -> "TAB"; "Space" -> "SPACE"; "Backspace" -> "BKSP"
    "Up" -> "UP"; "Down" -> "DOWN"; "Left" -> "LEFT"; "Right" -> "RIGHT"
    "Shift" -> "SHIFT_L"; "Ctrl" -> "CTRL_L"; "Alt" -> "ALT_L"
    "Insert" -> "INSERT"; "Delete" -> "DEL"; "Home" -> "HOME"; "End" -> "END"; "PgUp" -> "PRIOR"; "PgDn" -> "NEXT"; "PrtSc" -> "PRTSCN"
    "`" -> "GRAVE"; "-" -> "MINUS"; "=" -> "EQUAL"; "[" -> "BRACKET_LEFT"; "]" -> "BRACKET_RIGHT"; ";" -> "SEMICOLON"
    "'" -> "APOSTROPHE"; "," -> "COMMA"; "." -> "PERIOD"; "/" -> "SLASH"; "\\" -> "BACKSLASH"
    "NumPlus" -> "KP_ADD"; "NumMinus" -> "KP_SUBTRACT"; "NumStar" -> "KP_MULTIPLY"; "NumSlash" -> "KP_DIVIDE"; "NumEnter" -> "KP_ENTER"
    else -> key.uppercase()
}
