package com.logie.blizz.forevernew

import java.io.File
import java.io.IOException

/**
 * The one "Install & Play" workflow, as an ordered list of stages with checkpoints. Each stage reports through [Steps]
 * (injected, so the order, the failure handling and the resume are unit-tested without a phone). What is wired to real work
 * today and what isn't is in [Plan.notImplemented]; the installer never reports READY past a stage it could not run, and
 * never starts the game it cannot start ([ForeverAuth.Launch.NOT_WIRED]).
 */
class ForeverInstaller(private val layout: ForeverLayout, private val steps: Steps, private val store: ForeverStateStore, private val logs: ForeverLogs,
    private val freeBytes: (File) -> Long = { it.usableSpace }) {
    /** The work of each stage. Each returns null on success or the error text, and says its own progress through [say]. */
    interface Steps {
        fun package_(say: (String, Float?) -> Unit): String?
        /** A complete, supported client, or null when one still has to be imported (the page then shows Import & Install). */
        fun client(): ForeverClient.Result.Ok?
        fun extractData(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit): String?
        fun database(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit): String?
        fun addon(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit): String?
        fun startAuth(): String?
        fun startWorld(): String?
    }

    enum class Outcome { READY, AWAITING_CLIENT, FAILED }
    data class Result(val outcome: Outcome, val message: String)

    fun run(say: (ForeverState, String, Float?) -> Unit): Result {
        fun enter(state: ForeverState, text: String, progress: Float? = null) { store.save(state, text); logs.event("${state.name} $text"); say(state, text, progress) }
        fun fail(state: ForeverState, subsystem: String, message: String): Result {
            store.save(ForeverState.FAILED, message, ForeverFailure(state, subsystem, message)); logs.event("FAILED $subsystem: $message")
            say(ForeverState.FAILED, "$subsystem: $message", null)
            return Result(Outcome.FAILED, "$subsystem: $message")
        }
        return try {
            enter(ForeverState.DOWNLOADING, "Preparing Forever's server")
            steps.package_ { t, p -> say(ForeverState.DOWNLOADING, t, p) }?.let { return fail(ForeverState.DOWNLOADING, "server package", it) }

            val client = steps.client()
            if (client == null) {
                enter(ForeverState.AWAITING_CLIENT, "Select your complete World of Warcraft folder once (Import & Install)")
                return Result(Outcome.AWAITING_CLIENT, "The WoW Forever client is needed: it can't be downloaded by the app.")
            }

            if (!layout.hasMaps() || ForeverMaps.remaining(layout).isNotEmpty()) {
                ForeverMaps.checkSpace(freeBytes(layout.data.apply { mkdirs() }))?.let { return fail(ForeverState.BUILDING_MAPS, "map data", it) }
                enter(ForeverState.EXTRACTING, "Extracting the map data from your client")
                steps.extractData(client) { t, p -> say(ForeverState.BUILDING_MAPS, t, p) }?.let { return fail(ForeverState.BUILDING_MAPS, "map data", it) }
            }
            if (!layout.hasMaps()) return fail(ForeverState.BUILDING_MAPS, "map data", "Maps, vmaps and mmaps are missing; bots and the world stay off.")

            enter(ForeverState.INSTALLING_DB, "Setting up Forever's database")
            steps.database(client) { t, p -> say(ForeverState.INSTALLING_DB, t, p) }?.let { return fail(ForeverState.INSTALLING_DB, "database", it) }

            steps.addon(client) { t, p -> say(ForeverState.INSTALLING_DB, t, p) }?.let { return fail(ForeverState.INSTALLING_DB, "add-on", it) }

            enter(ForeverState.STARTING_AUTH, "Starting the login server")
            steps.startAuth()?.let { return fail(ForeverState.STARTING_AUTH, "login server", it) }
            enter(ForeverState.STARTING_WORLD, "Starting the world server")
            steps.startWorld()?.let { return fail(ForeverState.STARTING_WORLD, "world server", it) }
            enter(ForeverState.READY, "The server is running. ${ForeverAuth.Launch.NOT_WIRED}")
            Result(Outcome.READY, "The server is running. ${ForeverAuth.Launch.NOT_WIRED}")
        } catch (e: IOException) {
            fail(store.load().state, "io", e.message ?: e.javaClass.simpleName)
        }
    }

    /** What the installer does and does not do yet. Shown by the page and written into the log: nothing here is claimed as working on a phone. */
    object Plan {
        val notImplemented = listOf(
            "Starting the game: Wine trust of the login certificate and the launcher's server key (WoWForeverLauncher.exe) are not built or tested.",
            "Downloading the game client: no authorised Battle.net download exists in the app; the client is imported once from the user's own installation.",
            "Nothing here has run on a real phone.",
        )
    }
}
