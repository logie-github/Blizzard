package com.logie.blizz.controls

import org.json.JSONObject
import java.io.File

/** Each game's controls as the person set them (`controls/<game>.json`), else the game's defaults. */
class ControlsStore(private val dir: File) {
    private fun file(gameId: String) = File(dir, "$gameId.json")

    fun load(gameId: String): GameControls = runCatching { GameControls.fromJson(JSONObject(file(gameId).readText())) }
        .getOrNull()?.let { current(gameId, it) } ?: defaults(gameId)

    /**
     * [saved] as this build plays it. Warcraft III's layout was made anew on 10 November 2026 (the smart tap); rules saved
     * from the layout before it (they have no smart tap) would keep the tap a right click, so they give way to the new
     * defaults, the person's own keys kept.
     */
    private fun current(gameId: String, saved: GameControls): GameControls =
        if (gameId.startsWith("warcraft3") && saved.rules.none { it.function == "smart" }) saved.copy(rules = Catalog.of(gameId).rules) else saved

    /** Changes whenever the saved controls do (or are reset): to notice a change made while the game was running. */
    fun stamp(gameId: String): Long = file(gameId).let { if (it.isFile) it.lastModified() * 31 + it.length() else 0L }

    fun save(controls: GameControls) {
        dir.mkdirs()
        val temp = File(dir, ".${controls.gameId}.tmp")
        temp.writeText(controls.toJson().toString(2))
        temp.renameTo(file(controls.gameId))
    }

    fun reset(gameId: String) {
        file(gameId).delete()
    }

    companion object {
        fun defaults(gameId: String) = GameControls(gameId, emptyMap(), Catalog.of(gameId).rules)
    }
}

/** A game's controls ready to play with: which function a trigger at a spot runs, and its key. */
class Bindings(val game: Catalog.Game, val controls: GameControls) {
    fun keyOf(function: GameFunction): KeyCombo? = controls.keys[function.id] ?: function.key

    /** The function [trigger] at ([x], [y]) (fractions of the game's screen) runs: the rule with the smallest area there wins. */
    fun resolve(trigger: Trigger, x: Float, y: Float): GameFunction? = controls.rules.asSequence()
        .withIndex()
        .filter { it.value.trigger == trigger }
        .mapNotNull { (i, rule) -> game.area(rule.area)?.takeIf { it.contains(x, y) }?.let { area -> Triple(area, rule, i) } }
        // The smallest area wins; of equal areas the rule made last, so a rule the person adds beats the default it replaces.
        .sortedWith(compareBy<Triple<Area, Rule, Int>> { it.first.size }.thenByDescending { it.third })
        .map { it.first to it.second }
        .mapNotNull { (_, rule) -> game.function(rule.function) }
        .firstOrNull()
        // "Nothing" in a smaller area switches that spot off.
        ?.takeIf { it.kind != Kind.NONE }

    /** Rules that name this function (for the hotkey list). */
    fun rulesFor(functionId: String) = controls.rules.filter { it.function == functionId }

    companion object {
        fun of(gameId: String, controls: GameControls) = Bindings(Catalog.of(gameId), controls)
    }
}
