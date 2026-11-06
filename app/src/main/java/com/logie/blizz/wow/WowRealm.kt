package com.logie.blizz.wow

import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat
import com.logie.blizz.reports.BugReports
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import java.net.Inet4Address
import java.net.InetSocketAddress
import java.net.NetworkInterface
import java.net.Socket

/**
 * The World of Warcraft (Wrath of the Lich King) realm on the phone, run by Blizzard from the files
 * the World of Warcraft app exported (`files/games/wow/files`): the same MariaDB databases and
 * characters, the same programs and configs, no rebuild. ChromieCraft listens on 8085, Wrath Remix
 * on 8086, the login server on 3724; the game's own login (127.0.0.1) is set up in the realm list.
 *
 * - [start] brings the realm up in [WowRealmService]'s foreground and returns at once; follow [status].
 * - [awaitUp] waits for the world server to be ready.
 * - [stop] saves the characters and stops everything (the service's Stop action does the same).
 * - [chosenRealm] is the realm the user last chose in the WoW app.
 *
 * What runs and how ([WowCtl], [WowPathRewrite], [RealmController]) is unit-tested with a fake
 * process runner. NOT verified, since it needs the user's data and a phone: the real server
 * programs running through musl's loader from this folder, MariaDB opening the imported
 * databases, the world server reaching "ready".
 */
object WowRealm {
    enum class Phase { STOPPED, STARTING, RUNNING, STOPPING, FAILED }

    enum class Step { PREPARING, CONFIGURING, DATABASE, IMPORT, MODULES, AUTH, WORLD }

    /**
     * How the realm is: [step] while starting, [message] a line for the user (the step's latest
     * output). After a failure [error] says why and [log] is the end of the log that says more.
     */
    data class Status(
        val phase: Phase = Phase.STOPPED,
        val step: Step? = null,
        val message: String? = null,
        val realm: Realm = Realm.CHROMIE,
        val error: String? = null,
        val log: String? = null,
    )

    private val _status = MutableStateFlow(Status())
    val status: StateFlow<Status> = _status

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    @Volatile private var controller: RealmController? = null
    @Volatile private var job: Job? = null

    fun isRunning(): Boolean = _status.value.phase.let { it == Phase.STARTING || it == Phase.RUNNING }

    /** The realm the user last chose in the WoW app (its `realms` preference in the export), ChromieCraft if none. */
    // Wrath Remix is gone from the app: Wrath+ (internally ChromieCraft) is the one realm.
    fun chosenRealm(@Suppress("UNUSED_PARAMETER") context: Context): Realm = Realm.CHROMIE

    /** Starts [realm] (and the service that keeps it alive). Does nothing while a realm is starting or running. */
    @Synchronized
    fun start(context: Context, realm: Realm = Realm.CHROMIE) {
        if (isRunning()) return
        val app = context.applicationContext
        val layout = WowLayout.of(app)
        val c = RealmController(
            layout = layout, runner = SystemRunner(), scope = scope,
            lanAddress = ::lanAddress,
            portOpen = ::portOpen,
            onFailure = { message, log -> report(app, realm, message, log) },
            _status = _status,
        )
        controller = c
        // Starting already, so the service doesn't see the realm stopped and end itself.
        _status.value = Status(phase = Phase.STARTING, step = Step.PREPARING, realm = realm)
        runCatching { ContextCompat.startForegroundService(app, Intent(app, WowRealmService::class.java)) }
        job = scope.launch { c.run(realm) }
    }

    /** Stops the realm (characters saved first) and the service. Returns at once. */
    fun stop(@Suppress("UNUSED_PARAMETER") context: Context) {
        val c = controller ?: return
        val running = job
        scope.launch {
            running?.cancel()
            running?.join()
            c.shutDown()
        }
    }

    /** Stops the realm and waits until it is down. Background thread. */
    suspend fun stopAndWait(context: Context) {
        stop(context)
        withTimeoutOrNull(180_000) { _status.first { it.phase == Phase.STOPPED || it.phase == Phase.FAILED } }
    }

    /** Waits until the world server is up: true; or the start failed, or [timeoutMs] passed: false. */
    suspend fun awaitUp(timeoutMs: Long): Boolean =
        withTimeoutOrNull(timeoutMs) { _status.first { it.phase == Phase.RUNNING || it.phase == Phase.FAILED } }?.phase == Phase.RUNNING

    /** A command for the world server's console (`saveall`; no dot). False if the world server isn't running. */
    fun worldCommand(command: String): Boolean = controller?.worldCommand(command) == true

    private fun report(context: Context, realm: Realm, message: String, log: String?) {
        runCatching {
            BugReports.report(
                context, "World of Warcraft realm", message,
                details = listOf("Realm" to realm.displayName, "Step" to _status.value.step?.name),
                log = log,
            )
        }
    }

    private fun portOpen(port: Int): Boolean =
        runCatching { Socket().use { it.connect(InetSocketAddress("127.0.0.1", port), 500) } }.isSuccess

    /** The phone's IPv4 address on Wi-Fi, for a PC's client to log in (the realm list). */
    private fun lanAddress(): String? = runCatching {
        NetworkInterface.getNetworkInterfaces().toList()
            .filter { it.isUp && !it.isLoopback }
            .sortedBy { if (it.name.startsWith("wlan")) 0 else 1 }
            .flatMap { it.inetAddresses.toList() }
            .filterIsInstance<Inet4Address>()
            .firstOrNull { it.isSiteLocalAddress }
            ?.hostAddress
    }.getOrNull()
}
