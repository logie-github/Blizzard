package com.logie.blizz.wow

import android.content.Context
import com.logie.blizz.game.RealmControl
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.stateIn

/** [WowPlay][com.logie.blizz.game.WowPlay]'s view of the realm: [WowRealm] under the interface Play is written against. */
object WowRealmControl : RealmControl {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    fun map(s: WowRealm.Status): RealmControl.Status = RealmControl.Status(
        phase = when (s.phase) {
            WowRealm.Phase.STOPPED, WowRealm.Phase.STOPPING -> RealmControl.Phase.STOPPED
            WowRealm.Phase.STARTING -> RealmControl.Phase.STARTING
            WowRealm.Phase.RUNNING -> RealmControl.Phase.UP
            WowRealm.Phase.FAILED -> RealmControl.Phase.FAILED
        },
        detail = s.message,
        error = s.error,
    )

    override val status: StateFlow<RealmControl.Status> =
        WowRealm.status.map { map(it) }.stateIn(scope, SharingStarted.Eagerly, map(WowRealm.status.value))

    override fun start(context: Context, realm: String) =
        WowRealm.start(context, when (realm) { "remix" -> Realm.REMIX; "octo" -> Realm.OCTO; "legion" -> Realm.LEGION; "wrathpp" -> Realm.WRATHPP; else -> Realm.CHROMIE })

    override suspend fun awaitUp(timeoutMs: Long): RealmControl.Status {
        WowRealm.awaitUp(timeoutMs)
        return map(WowRealm.status.value)
    }

    override fun chosenRealm(context: Context): String = WowRealm.chosenRealm(context).let { if (it == Realm.REMIX) "remix" else "main" }
}
