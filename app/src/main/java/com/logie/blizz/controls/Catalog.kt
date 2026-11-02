package com.logie.blizz.controls

/**
 * Each game's functions (with the game's own default keys), its screen areas and its default
 * gesture rules. The functions every game shares come from [common]; a game names them its way
 * (Diablo's left click walks, attacks and picks up; StarCraft's selects). Plain Kotlin, unit-tested.
 */
object Catalog {
    data class Game(val functions: List<GameFunction>, val areas: List<Area>, val rules: List<Rule>) {
        fun function(id: String) = functions.firstOrNull { it.id == id }
        fun area(id: String): Area? = areas.firstOrNull { it.id == id } ?: Area.parseCustom(id)
    }

    fun of(gameId: String): Game = when (gameId) {
        "diablo" -> DIABLO
        "diablo2" -> DIABLO2
        "starcraft" -> STARCRAFT
        "starcraft2" -> STARCRAFT2
        "warcraft" -> WARCRAFT
        "warcraft2" -> WARCRAFT2
        "warcraft3_roc", "warcraft3_tft" -> WARCRAFT3
        else -> STARCRAFT
    }

    private fun f(id: String, label: String, kind: Kind, key: String? = null) = GameFunction(id, label, kind, key?.let { KeyCombo.of(it) })
    private fun key(id: String, label: String, key: String) = f(id, label, Kind.KEY, key)

    /** What every game has; [labels] renames them for a game. */
    private fun common(labels: Map<String, String> = emptyMap()): List<GameFunction> = listOf(
        f("click", labels["click"] ?: "Left click", Kind.CLICK_LEFT),
        f("rclick", labels["rclick"] ?: "Right click", Kind.CLICK_RIGHT),
        f("dclick", labels["dclick"] ?: "Double click", Kind.DOUBLE_LEFT),
        f("shiftclick", labels["shiftclick"] ?: "Shift + left click", Kind.SHIFT_LEFT),
        f("shiftrclick", labels["shiftrclick"] ?: "Shift + right click", Kind.SHIFT_RIGHT),
        f("ctrlclick", labels["ctrlclick"] ?: "Ctrl + left click", Kind.CTRL_LEFT),
        f("drag", labels["drag"] ?: "Drag", Kind.DRAG_LEFT),
        f("pan", labels["pan"] ?: "Scroll", Kind.PAN),
        key("up", labels["up"] ?: "Up", "Up"),
        key("down", labels["down"] ?: "Down", "Down"),
        key("left", labels["left"] ?: "Left", "Left"),
        key("right", labels["right"] ?: "Right", "Right"),
        f("wheelup", labels["wheelup"] ?: "Wheel up", Kind.WHEEL_UP),
        f("wheeldown", labels["wheeldown"] ?: "Wheel down", Kind.WHEEL_DOWN),
        key("esc", "Escape", "Esc"),
        key("enter", labels["enter"] ?: "Enter", "Enter"),
        f("keyboard", "Phone keyboard", Kind.PHONE_KEYBOARD),
        f("menu", "App menu", Kind.APP_MENU),
        f("none", "Nothing", Kind.NONE),
    )

    private fun rule(trigger: Trigger, function: String, area: String = Area.ANYWHERE.id) = Rule(trigger, area, function)

    private val SHARED_RULES = listOf(
        rule(Trigger.THREE_FINGER_TAP, "keyboard"),
        rule(Trigger.FOUR_FINGER_TAP, "menu"),
    )

    /** Diablo's and Diablo II's: tap left-clicks, hold right-clicks, drag walks, flicks are the arrow keys. */
    private fun arpgRules(menu: String) = listOf(
        rule(Trigger.TAP, "click"),
        rule(Trigger.HOLD, "rclick"),
        rule(Trigger.DRAG, "drag"),
        rule(Trigger.FLICK_UP, "up"), rule(Trigger.FLICK_DOWN, "down"),
        rule(Trigger.FLICK_LEFT, "left"), rule(Trigger.FLICK_RIGHT, "right"),
        rule(Trigger.REST_TAP, "shiftclick"),
        rule(Trigger.TWO_FINGER_TAP, menu),
    ) + SHARED_RULES

    /** The strategy games': tap right-clicks (left on the panels), hold left-clicks, drag scrolls. */
    private fun rtsRules(menu: String, panels: List<String>) = listOf(
        rule(Trigger.TAP, "rclick"),
        rule(Trigger.HOLD, "click"),
        rule(Trigger.DOUBLE_TAP_HOLD, "dclick"),
        rule(Trigger.DRAG, "pan"),
        rule(Trigger.REST_TAP, "shiftrclick"),
        rule(Trigger.REST_HOLD, "shiftclick"),
        rule(Trigger.PINCH_OUT, "wheelup"), rule(Trigger.PINCH_IN, "wheeldown"),
        rule(Trigger.TWO_FINGER_TAP, menu),
    ) + panels.map { rule(Trigger.TAP, "click", it) } + SHARED_RULES

    private fun groups(): List<GameFunction> =
        (1..10).map { n -> val k = (n % 10).toString(); key("group$k", "Select group $k", k) } +
            (1..10).map { n -> val k = (n % 10).toString(); key("setgroup$k", "Set group $k", "Ctrl+$k") }

    // Diablo (DevilutionX's own defaults) -------------------------------------------------------

    val DIABLO = Game(
        functions = common(mapOf("click" to "Walk · attack · pick up", "rclick" to "Cast spell", "shiftclick" to "Attack in place", "drag" to "Walk",
            "wheelup" to "Previous quick spell", "wheeldown" to "Next quick spell")) + listOf(
            key("inventory", "Inventory", "I"), key("character", "Character", "C"), key("quests", "Quest log", "Q"),
            key("spellbook", "Spellbook", "B"), key("speedbook", "Speedbook", "S"), key("party", "Party", "Y"),
            key("automap", "Automap", "Tab"), key("maptype", "Map type", "M"), key("hide", "Hide info screens", "Space"),
            f("highlight", "Item highlighting", Kind.KEY_HOLD, "Alt"), key("togglehighlight", "Toggle item highlighting", "Ctrl"),
            key("zoom", "Zoom", "Z"), key("pause", "Pause", "P"), key("save", "Quick save", "F2"), key("load", "Quick load", "F3"),
            key("help", "Help", "F1"), key("info", "Game info", "V"), key("chatlog", "Chat log", "L"), key("sort", "Sort inventory", "R"),
            key("darker", "Darker", "F"), key("brighter", "Brighter", "G"), key("screenshot", "Screenshot", "PrtSc"),
        ) + (1..8).map { key("belt$it", "Belt $it", "$it") } + (1..4).map { key("quickspell$it", "Quick spell $it", "F${4 + it}") } +
            (1..4).map { key("message$it", "Quick message $it", "F${8 + it}") },
        areas = Area.STANDARD + listOf(Area("panel", "Control panel", 0f, 0.733f, 1f, 1f)),
        rules = arpgRules("esc"),
    )

    // Diablo II ---------------------------------------------------------------------------------

    val DIABLO2 = Game(
        functions = common(mapOf("click" to "Move · attack · pick up", "rclick" to "Right skill", "shiftclick" to "Stand still", "drag" to "Walk")) + listOf(
            key("character", "Character", "C"), key("inventory", "Inventory", "I"), key("party", "Party", "P"),
            key("messages", "Message log", "M"), key("quests", "Quest log", "Q"), key("skilltree", "Skill tree", "T"),
            key("skillbar", "Skill speed bar", "S"), key("hireling", "Hireling", "O"), key("help", "Help", "H"),
            key("automap", "Automap", "Tab"), key("swap", "Swap weapons", "W"), key("run", "Run / walk", "R"),
            f("showitems", "Show items", Kind.KEY_HOLD, "Alt"), key("clear", "Clear screen", "Space"),
            key("screenshot", "Screenshot", "PrtSc"),
        ) + (1..4).map { key("belt$it", "Belt $it", "$it") } + (1..8).map { key("skill$it", "Skill $it", "F$it") },
        areas = Area.STANDARD + listOf(Area("panel", "Control panel", 0f, 0.86f, 1f, 1f)),
        rules = arpgRules("esc"),
    )

    // StarCraft ----------------------------------------------------------------------------------

    private val RTS_LABELS = mapOf(
        "click" to "Select · press", "rclick" to "Move · attack · gather", "dclick" to "Select all of type",
        "shiftclick" to "Add to selection", "shiftrclick" to "Queue order", "drag" to "Box select", "pan" to "Scroll map", "enter" to "Chat",
    )

    private val RTS_COMMANDS = listOf(
        key("attack", "Attack", "A"), key("move", "Move", "M"), key("stop", "Stop", "S"), key("hold", "Hold position", "H"),
        key("patrol", "Patrol", "P"), key("build", "Build", "B"), key("advanced", "Advanced build", "V"),
        key("gamemenu", "Game menu", "F10"), key("alert", "Last alert", "Space"),
    )

    private val SC_AREAS = Area.STANDARD + listOf(
        Area("console", "Console", 0f, 0.73f, 1f, 1f), Area("minimap", "Minimap", 0f, 0.73f, 0.2f, 1f),
        Area("commands", "Command card", 0.77f, 0.73f, 1f, 1f), Area("menubar", "Menu bar", 0f, 0f, 1f, 0.04f),
    )

    val STARCRAFT = Game(
        functions = common(RTS_LABELS) + RTS_COMMANDS + listOf(
            key("camera1", "Camera 1", "F2"), key("camera2", "Camera 2", "F3"), key("camera3", "Camera 3", "F4"),
            key("setcamera1", "Save camera 1", "Shift+F2"), key("setcamera2", "Save camera 2", "Shift+F3"), key("setcamera3", "Save camera 3", "Shift+F4"),
        ) + groups(),
        areas = SC_AREAS,
        rules = rtsRules("gamemenu", listOf("console", "menubar")),
    )

    // StarCraft II -------------------------------------------------------------------------------

    val STARCRAFT2 = Game(
        functions = common(RTS_LABELS) + RTS_COMMANDS + listOf(
            key("idle", "Idle worker", "F1"), key("army", "Select army", "F2"), key("bases", "Cycle bases", "Backspace"),
            key("subgroup", "Next subgroup", "Tab"),
        ) + (1..4).map { key("camera$it", "Camera $it", "F${4 + it}") } + (1..4).map { key("setcamera$it", "Save camera $it", "Ctrl+F${4 + it}") } + groups(),
        areas = Area.STANDARD + listOf(
            Area("console", "Console", 0f, 0.78f, 1f, 1f), Area("minimap", "Minimap", 0f, 0.75f, 0.2f, 1f),
            Area("commands", "Command card", 0.75f, 0.75f, 1f, 1f), Area("menubar", "Menu bar", 0f, 0f, 1f, 0.04f),
        ),
        rules = rtsRules("gamemenu", listOf("console", "menubar")),
    )

    // Warcraft -----------------------------------------------------------------------------------

    val WARCRAFT3 = Game(
        functions = common(RTS_LABELS) + RTS_COMMANDS.filter { it.id != "build" && it.id != "advanced" } + listOf(
            key("hero1", "Hero 1", "F1"), key("hero2", "Hero 2", "F2"), key("hero3", "Hero 3", "F3"), key("subgroup", "Next subgroup", "Tab"),
            f("healthbars", "Health bars", Kind.KEY_HOLD, "Alt"),
        ) + groups(),
        areas = Area.STANDARD + listOf(
            Area("console", "Console", 0f, 0.76f, 1f, 1f), Area("minimap", "Minimap", 0f, 0.76f, 0.2f, 1f),
            Area("commands", "Command card", 0.75f, 0.76f, 1f, 1f), Area("menubar", "Menu bar", 0f, 0f, 1f, 0.05f),
        ),
        rules = rtsRules("gamemenu", listOf("console", "menubar")),
    )

    val WARCRAFT2 = Game(
        functions = common(RTS_LABELS) + RTS_COMMANDS.filter { it.id != "alert" } + groups(),
        areas = Area.STANDARD + listOf(Area("panel", "Side panel", 0f, 0f, 0.22f, 1f), Area("minimap", "Minimap", 0f, 0f, 0.22f, 0.3f)),
        rules = rtsRules("gamemenu", listOf("panel")),
    )

    val WARCRAFT = Game(
        functions = common(RTS_LABELS) + RTS_COMMANDS.filter { it.id != "alert" && it.id != "advanced" } + groups(),
        areas = Area.STANDARD + listOf(Area("panel", "Side panel", 0f, 0f, 0.22f, 1f), Area("minimap", "Minimap", 0f, 0f, 0.22f, 0.3f)),
        rules = rtsRules("gamemenu", listOf("panel")),
    )
}
