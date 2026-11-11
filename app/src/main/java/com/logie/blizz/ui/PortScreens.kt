package com.logie.blizz.ui

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.porter.ArmoryPort
import com.logie.blizz.porter.armory.ArmoryCharacter
import com.logie.blizz.porter.port.GearTier
import com.logie.blizz.porter.port.LevelCap
import com.logie.blizz.porter.port.PortArea
import com.logie.blizz.porter.port.PortCharacter
import com.logie.blizz.porter.port.PortDecision
import com.logie.blizz.porter.port.PortFaction
import com.logie.blizz.porter.port.PortOptions
import com.logie.blizz.porter.port.PortOutcome
import com.logie.blizz.porter.port.PortPlan
import com.logie.blizz.porter.port.PortRealm
import com.logie.blizz.porter.port.PortResult
import com.logie.blizz.porter.port.ProcessRealmDb
import com.logie.blizz.porter.port.RaceClass
import com.logie.blizz.porter.port.RealmDb
import com.logie.blizz.porter.port.RealmFiles
import com.logie.blizz.porter.port.RealmSupport
import com.logie.blizz.porter.port.TargetSuggestion
import com.logie.blizz.wow.Realm
import com.logie.blizz.wow.RealmDatabase
import com.logie.blizz.wow.WowLayout
import com.logie.blizz.wow.WowLogin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.io.File
import java.io.IOException
import com.logie.blizz.porter.port.Porter as PortEngine

/**
 * Porting a character from the Armory into one of the phone's realms: the realm picked ([PortSection]), then [PortDialog]:
 * what the Armory and Blizzard's API add (mounts, standings; with a key, quests, achievements, titles, looks), the realm's
 * database started alone (the realm stopped first), the person's choices (name, race, class, sex, level, gold, gear,
 * account), the plan with every decision ([PortPlan]'s report), and the port itself. The realm's engine is
 * [com.logie.blizz.porter.port.Porter]; it never writes until Port is pressed.
 */

/** A realm a character can be ported to, and why not now when it can't. */
internal data class Destination(val realm: Realm, val title: String, val about: String, val problem: String?)

internal object Destinations {
    const val LATER = "Comes in a later update: this realm keeps its characters in other tables, which the porter doesn't write yet."

    fun of(context: Context): List<Destination> {
        val layout = WowLayout.of(context)
        val wrath = RealmDatabase.problem(layout)
        val wrathpp = wrath ?: if (!layout.hasWrathppServer() || !File(layout.root, "etc-wrathpp/worldserver.conf").isFile) {
            "Play Wrath++ once first: its first start sets its realm up here."
        } else null
        return listOf(
            Destination(Realm.CHROMIE, "ChromieCraft", "Wrath+ · the main realm", wrath),
            Destination(Realm.WRATHPP, "Wrath++", "Wrath+ · the experimental realm", wrathpp),
            Destination(Realm.REMIX, "Wrath Remix", "Wrath+ · the Remix realm", RealmSupport.REMIX_REASON),
            Destination(Realm.LEGION, "Legion", "LegionCore 7.3.5", LATER),
            Destination(Realm.OCTO, "OctoWoW", "Tortoise-WoW's 1.12 realm", LATER),
        )
    }
}

/** What the Armory and Blizzard's API add for a port, and what the person should know of it. */
internal data class PortExtras(val extras: ArmoryPort.Extras, val notes: List<String>)

/** A realm open for porting: its database running alone and the porter's engine on it. Every call is slow: a background thread. */
internal interface PortSession : AutoCloseable {
    val realm: Realm
    fun support(): RealmSupport
    fun levelCap(): LevelCap
    fun scaledLevel(retailLevel: Int): Int
    fun combos(): List<RaceClass>
    fun raceName(race: Int): String
    fun className(classId: Int): String
    fun factionOf(race: Int): PortFaction
    fun suggest(character: PortCharacter): TargetSuggestion?
    fun nameProblem(name: String): String?
    /** The realm's accounts (the login database's, shared by the Wrath realms). */
    fun accounts(): List<String>
    fun plan(character: PortCharacter, options: PortOptions): PortPlan
    fun apply(plan: PortPlan): PortResult
}

/** The live session: [RealmDatabase] (MariaDB through the realm's ctl.sh) and the engine reading and writing through it. */
internal class LivePortSession(private val database: RealmDatabase, private val db: RealmDb, private val engine: PortEngine) : PortSession {
    override val realm: Realm get() = engine.realm.realm
    override fun support() = engine.support()
    override fun levelCap() = engine.levelCap()
    override fun scaledLevel(retailLevel: Int) = engine.scaledLevel(retailLevel)
    override fun combos() = engine.raceClassCombos()
    override fun raceName(race: Int) = engine.data().raceName(race)
    override fun className(classId: Int) = engine.data().className(classId)
    override fun factionOf(race: Int) = engine.factionOf(race)
    override fun suggest(character: PortCharacter) = engine.suggestTarget(character)
    override fun nameProblem(name: String) = engine.nameProblem(name)
    override fun accounts() = db.query(engine.realm.authDb, "SELECT username FROM account ORDER BY id").mapNotNull { it.firstOrNull() }
    override fun plan(character: PortCharacter, options: PortOptions) = engine.plan(character, options)
    override fun apply(plan: PortPlan) = engine.apply(plan)
    override fun close() = database.close()

    companion object {
        /** Stops the realm if it runs, starts its database alone, and reads the realm's tables once. */
        suspend fun open(context: Context, realm: Realm, step: (String) -> Unit): PortSession {
            val port = PortRealm.of(realm) ?: throw IOException("${realm.displayName} can't take a ported character.")
            val database = RealmDatabase.open(context, step)
            try {
                val command = database.sqlCommand()
                val db = ProcessRealmDb(command.argv, command.env, command.directory)
                val engine = PortEngine(db, RealmFiles(database.layout.root, port))
                step("Reading the realm's own tables")
                engine.data()
                return LivePortSession(database, db, engine)
            } catch (e: Throwable) {
                runCatching { database.close() }
                throw e
            }
        }
    }
}

/** Keeps the open session, and closes it (the database stopped) once, off the main thread, whenever the dialog goes. */
private class SessionHolder {
    private var session: PortSession? = null
    private var closed = false

    @Synchronized fun get(): PortSession? = session

    /** False when the dialog went meanwhile: the session is closed at once. */
    @Synchronized fun set(s: PortSession): Boolean {
        if (closed) {
            Thread { runCatching { s.close() } }.start()
            return false
        }
        session = s
        return true
    }

    @Synchronized fun close() {
        closed = true
        val s = session ?: return
        session = null
        Thread { runCatching { s.close() } }.start()
    }
}

// The Port section of a character's page ----------------------------------------------------------------------------------

@Composable
internal fun PortSection(c: ArmoryCharacter) {
    val context = LocalContext.current
    val source = LocalPorterSource.current
    val destinations = remember { source.destinations(context) }
    var porting by remember { mutableStateOf<Destination?>(null) }
    SectionLabel("Port")
    Text(
        "Bring ${c.name} into one of the phone's realms: their race and sex, class, level, gear chosen from the realm's own items, " +
            "gold, spells and skills, professions, mounts and standings, and with a Battle.net key their quests, achievements, titles and looks.",
        style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
    )
    for (d in destinations) DestinationRow(d) { porting = d }
    porting?.let { PortDialog(c, it) { porting = null } }
}

@Composable
private fun DestinationRow(d: Destination, onClick: () -> Unit) {
    val open = d.problem == null
    Row(
        Modifier.fillMaxWidth().box().then(if (open) Modifier.clickable(onClick = onClick) else Modifier).padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Column(Modifier.weight(1f)) {
            Text(d.title, style = MaterialTheme.typography.titleMedium, color = if (open) Colors.Text else Colors.Mist)
            Text(d.about, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
            d.problem?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = Modern.Faint, modifier = Modifier.padding(top = 4.dp)) }
        }
        if (open) Icon(Icons.AutoMirrored.Filled.ArrowForward, "Port to ${d.title}", tint = Colors.Ice, modifier = Modifier.size(22.dp))
    }
}

// The port itself --------------------------------------------------------------------------------------------------------

private sealed interface Stage {
    data class Working(val text: String) : Stage
    data class Failed(val message: String) : Stage
    data object Choosing : Stage
    data class Planned(val plan: PortPlan) : Stage
    data class Porting(val plan: PortPlan) : Stage
    data class Done(val result: PortResult, val plan: PortPlan) : Stage
}

/** What the realm offers, read once when it opens. */
private class RealmInfo(
    val cap: LevelCap,
    val combos: List<RaceClass>,
    val races: Map<Int, String>,
    val classes: Map<Int, String>,
    val factions: Map<Int, PortFaction>,
    val accounts: List<String>,
    val suggestion: TargetSuggestion?,
    val scaledLevel: Int,
)

/** The person's choices. */
private data class Draft(
    val name: String,
    val race: Int,
    val classId: Int,
    val gender: Int,
    val level: Int,
    val gold: String,
    val tier: GearTier,
    val account: String,
)

@Composable
private fun PortDialog(c: ArmoryCharacter, destination: Destination, onClose: () -> Unit) {
    val context = LocalContext.current
    val source = LocalPorterSource.current
    val scope = rememberCoroutineScope()
    val holder = remember { SessionHolder() }
    val lock = remember { Mutex() }
    var stage by remember { mutableStateOf<Stage>(Stage.Working("Getting ready")) }
    var character by remember { mutableStateOf<PortCharacter?>(null) }
    var notes by remember { mutableStateOf(emptyList<String>()) }
    var info by remember { mutableStateOf<RealmInfo?>(null) }
    var draft by remember { mutableStateOf<Draft?>(null) }
    DisposableEffect(Unit) { onDispose { holder.close() } }

    LaunchedEffect(Unit) {
        val result = withContext(Dispatchers.IO) {
            runCatching {
                val extras = source.extras(context, c) { stage = Stage.Working(it) }
                val ported = ArmoryPort.character(c, extras.extras)
                val session = source.openRealm(context, destination.realm) { stage = Stage.Working(it) }
                if (!holder.set(session)) throw IOException("closed")
                val support = session.support()
                if (!support.supported) throw IOException(support.reason ?: "${destination.title} can't take a ported character.")
                val combos = session.combos()
                val races = combos.map { it.race }.distinct().sorted()
                val classes = combos.map { it.classId }.distinct().sorted()
                val read = RealmInfo(
                    cap = session.levelCap(),
                    combos = combos,
                    races = races.associateWith { session.raceName(it) },
                    classes = classes.associateWith { session.className(it) },
                    factions = races.associateWith { session.factionOf(it) },
                    accounts = session.accounts(),
                    suggestion = session.suggest(ported),
                    scaledLevel = session.scaledLevel(c.level),
                )
                Triple(ported, extras.notes, read)
            }
        }
        result.onSuccess { (ported, extraNotes, read) ->
            character = ported
            notes = extraNotes
            info = read
            val own = WowLogin.forVersion(context, WowLogin.WRATH)?.name?.trim()?.uppercase()
            val s = read.suggestion
            draft = Draft(
                name = c.name,
                race = s?.race ?: read.combos.firstOrNull()?.race ?: 1,
                classId = s?.classId ?: read.combos.firstOrNull()?.classId ?: 1,
                gender = s?.gender ?: c.gender,
                level = read.scaledLevel.coerceIn(1, read.cap.max),
                gold = "0",
                tier = GearTier.FRESH,
                account = read.accounts.firstOrNull { it.equals(own, ignoreCase = true) } ?: read.accounts.firstOrNull().orEmpty(),
            )
            stage = Stage.Choosing
        }.onFailure { e ->
            if (e.message != "closed") stage = Stage.Failed(e.message ?: e.javaClass.simpleName)
        }
    }

    val porting = stage is Stage.Porting
    Dialog(onDismissRequest = { if (!porting) onClose() }, properties = DialogProperties(usePlatformDefaultWidth = false, dismissOnClickOutside = false)) {
        Box(Modifier.fillMaxSize().padding(14.dp), contentAlignment = Alignment.Center) {
            Column(Modifier.widthIn(max = 880.dp).fillMaxSize().panel()) {
                Row(Modifier.fillMaxWidth().padding(start = 20.dp, end = 8.dp, top = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        FrameTitle("Port ${c.name}", style = MaterialTheme.typography.titleLarge)
                        Text("To ${destination.title} · ${destination.about}", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
                    }
                    if (!porting) CloseButton(onClose)
                }
                val session = holder.get()
                when (val s = stage) {
                    is Stage.Working -> Waiting(s.text)
                    is Stage.Failed -> Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        Text(s.message, style = MaterialTheme.typography.bodyMedium, color = Modern.Bad)
                        FrameButton("Close", primary = false) { onClose() }
                    }
                    Stage.Choosing -> {
                        val i = info
                        val d = draft
                        if (i != null && d != null && session != null) Choosing(
                            c, i, d, notes, session, lock, onChange = { draft = it },
                            onPlan = { options ->
                                val ch = character ?: return@Choosing
                                stage = Stage.Working("Working out the port")
                                scope.launch {
                                    val r = withContext(Dispatchers.IO) { runCatching { lock.withLock { session.plan(ch, options) } } }
                                    stage = r.fold({ Stage.Planned(it) }, { Stage.Failed("The port couldn't be worked out: ${it.message ?: it.javaClass.simpleName}") })
                                }
                            },
                        )
                    }
                    is Stage.Planned -> PlanView(
                        s.plan, info, destination, busy = false,
                        onBack = { stage = Stage.Choosing },
                        onPort = {
                            stage = Stage.Porting(s.plan)
                            scope.launch {
                                val r = withContext(Dispatchers.IO) { runCatching { lock.withLock { session!!.apply(s.plan) } } }
                                r.onSuccess { holder.close() } // the database stops: Play starts everything again
                                stage = r.fold({ Stage.Done(it, s.plan) }, { Stage.Failed("The port didn't go through, and nothing was kept: ${it.message ?: it.javaClass.simpleName}") })
                            }
                        },
                    )
                    is Stage.Porting -> PlanView(s.plan, info, destination, busy = true, onBack = {}, onPort = {})
                    is Stage.Done -> DoneView(s.result, s.plan, info, destination, onClose)
                }
            }
        }
    }
}

@Composable
private fun Waiting(text: String) {
    Column(
        Modifier.fillMaxWidth().padding(28.dp),
        horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        CircularProgressIndicator()
        Text(text, style = MaterialTheme.typography.bodyMedium, color = Colors.Text)
        Text(
            "The realm stops while a character is ported into it (its characters are saved first); Play starts it again.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
    }
}

/** A choice among several: a chip that is lit when chosen, big enough for a thumb. */
@Composable
private fun Pick(text: String, selected: Boolean, color: Color = Colors.Ice, onClick: () -> Unit) {
    val shape = RoundedCornerShape(20.dp)
    Text(
        text,
        style = MaterialTheme.typography.labelLarge,
        color = if (selected) Color.White else Colors.Text,
        modifier = Modifier.clip(shape)
            .background(if (selected) color.copy(alpha = 0.32f) else Color.White.copy(alpha = 0.05f))
            .border(1.dp, if (selected) color else Modern.Outline, shape)
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 12.dp),
    )
}

private fun factionTint(f: PortFaction?) = when (f) {
    PortFaction.HORDE -> Color(0xFFE5484D)
    PortFaction.ALLIANCE -> Color(0xFF4C8DFF)
    else -> Modern.Muted
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun ColumnScope.Choosing(
    c: ArmoryCharacter,
    info: RealmInfo,
    draft: Draft,
    notes: List<String>,
    session: PortSession,
    lock: Mutex,
    onChange: (Draft) -> Unit,
    onPlan: (PortOptions) -> Unit,
) {
    var nameProblem by remember { mutableStateOf<String?>(null) }
    var checked by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(draft.name) {
        delay(350)
        val name = draft.name
        nameProblem = withContext(Dispatchers.IO) { runCatching { lock.withLock { session.nameProblem(name) } }.getOrElse { it.message } }
        checked = name
    }
    val deathKnight = draft.classId == 6
    val minLevel = if (deathKnight) info.cap.heroicStart.coerceAtMost(info.cap.max) else 1
    Column(Modifier.fillMaxWidth().weight(1f).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        SectionLabel("Name")
        OutlinedTextField(draft.name, { onChange(draft.copy(name = it.take(12))) }, Modifier.fillMaxWidth(), singleLine = true)
        when {
            checked != draft.name -> Text("Checking the name…", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
            nameProblem != null -> Text(nameProblem!!, style = MaterialTheme.typography.bodySmall, color = Modern.Bad)
            else -> Text("Free on ${session.realm.displayName}.", style = MaterialTheme.typography.bodySmall, color = Modern.Good)
        }

        SectionLabel("Becomes")
        info.suggestion?.notes?.takeIf { it.isNotEmpty() }?.let { list ->
            for (n in list) Text(n, style = MaterialTheme.typography.bodySmall, color = if (info.suggestion.needsChoice) Modern.Warn else Colors.Mist)
        }
        Text("Race", style = MaterialTheme.typography.labelLarge, color = Colors.Mist)
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            for ((race, name) in info.races) Pick(name, draft.race == race, factionTint(info.factions[race])) {
                val classes = info.combos.filter { it.race == race }.map { it.classId }
                val classId = if (draft.classId in classes) draft.classId else info.suggestion?.classId?.takeIf { it in classes } ?: classes.firstOrNull() ?: draft.classId
                onChange(draft.copy(race = race, classId = classId))
            }
        }
        Text("Class", style = MaterialTheme.typography.labelLarge, color = Colors.Mist)
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            for (classId in info.combos.filter { it.race == draft.race }.map { it.classId }.distinct().sorted()) {
                Pick(info.classes[classId] ?: "class $classId", draft.classId == classId) {
                    val level = if (classId == 6) draft.level.coerceAtLeast(info.cap.heroicStart.coerceAtMost(info.cap.max)) else draft.level
                    onChange(draft.copy(classId = classId, level = level))
                }
            }
        }
        PillSegmented(listOf("Male" to 0, "Female" to 1), draft.gender) { onChange(draft.copy(gender = it)) }

        SectionLabel("Level")
        Text("Level ${draft.level}", style = MaterialTheme.typography.titleMedium, color = Colors.Text)
        if (info.cap.max > minLevel) {
            Slider(
                value = draft.level.toFloat(),
                onValueChange = { onChange(draft.copy(level = it.toInt().coerceIn(minLevel, info.cap.max))) },
                valueRange = minLevel.toFloat()..info.cap.max.toFloat(),
                colors = SliderDefaults.colors(thumbColor = Colors.Ice, activeTrackColor = Colors.Ice, inactiveTrackColor = Colors.Frost),
            )
        }
        Text(
            buildString {
                append("Level ${c.level} on retail is level ${info.scaledLevel} here (the same share of the way to the cap)")
                val progression = info.cap.progression
                if (progression != null && progression < info.cap.max) append(". ${session.realm.displayName} is open to level $progression for now; up to ${info.cap.max} can be chosen.")
                else append(".")
                if (deathKnight) append(" A death knight begins at ${info.cap.heroicStart}.")
            },
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )

        SectionLabel("Gold")
        OutlinedTextField(
            draft.gold, { t -> onChange(draft.copy(gold = t.filter { it.isDigit() }.take(6))) }, Modifier.fillMaxWidth(),
            singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            suffix = { Text("gold") },
        )
        Text("The Armory doesn't show a character's gold: choose what they bring.", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)

        SectionLabel("Gear")
        PillSegmented(GearTier.entries.map { it.label to it }, draft.tier) { onChange(draft.copy(tier = it)) }
        Text(
            "Each slot gets the realm's own item nearest what they wear, for their class and level: ${draft.tier.about}.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )

        SectionLabel("Account")
        if (info.accounts.isEmpty()) {
            Text("The realm has no account yet: play it once to make one, then port.", style = MaterialTheme.typography.bodySmall, color = Modern.Bad)
        } else {
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                for (a in info.accounts) Pick(a, draft.account == a) { onChange(draft.copy(account = a)) }
            }
            Text("The account the character will be on (the game logs in with it: World of Warcraft's Auto login).", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
        }

        if (notes.isNotEmpty()) {
            SectionLabel("Good to know")
            for (n in notes) Text(n, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
        }
        Spacer(Modifier.size(4.dp))
        val ready = draft.account.isNotEmpty() && checked == draft.name && nameProblem == null
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
            FrameButton("See the port", primary = ready) {
                if (!ready) return@FrameButton
                onPlan(
                    PortOptions(
                        realm = session.realm, account = draft.account, name = draft.name.trim(), race = draft.race, classId = draft.classId,
                        gender = draft.gender, level = draft.level, money = (draft.gold.toLongOrNull() ?: 0L) * 10_000L, gearTier = draft.tier,
                    ),
                )
            }
        }
        Spacer(Modifier.size(8.dp))
    }
}

private fun outcomeWord(o: PortOutcome) = when (o) {
    PortOutcome.KEPT -> "kept"
    PortOutcome.MAPPED -> "changed"
    PortOutcome.ADDED -> "added"
    PortOutcome.DROPPED -> "left out"
    PortOutcome.REFUSED -> "refused"
    PortOutcome.NOTE -> "note"
}

private fun outcomeColor(o: PortOutcome) = when (o) {
    PortOutcome.KEPT -> Modern.Good
    PortOutcome.MAPPED -> Modern.AccentBright
    PortOutcome.ADDED -> Modern.Gold
    PortOutcome.DROPPED -> Modern.Muted
    PortOutcome.REFUSED -> Modern.Bad
    PortOutcome.NOTE -> Modern.Muted
}

private fun describe(plan: PortPlan, info: RealmInfo?): String {
    val race = info?.races?.get(plan.race) ?: "race ${plan.race}"
    val classId = info?.classes?.get(plan.classId) ?: "class ${plan.classId}"
    return "Level ${plan.level} $race $classId, ${if (plan.gender == 1) "female" else "male"}"
}

private fun gold(copper: Long): String = "%,d gold".format(copper / 10_000)

@Composable
private fun PlanView(plan: PortPlan, info: RealmInfo?, destination: Destination, busy: Boolean, onBack: () -> Unit, onPort: () -> Unit) {
    Column(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Column(Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(plan.name, style = MaterialTheme.typography.headlineSmall, color = Colors.Text)
            Text(describe(plan, info), style = MaterialTheme.typography.titleSmall, color = Colors.Gold)
            Text("On ${destination.title}, account ${plan.account} · ${gold(plan.money)}", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
            for (r in plan.refusals) Text(r, style = MaterialTheme.typography.bodyMedium, color = Modern.Bad)
            for (area in PortArea.entries) {
                val decisions = plan.report.of(area)
                if (area == PortArea.EQUIPMENT) {
                    if (plan.report.equipment.isEmpty() && decisions.isEmpty()) continue
                    SectionLabel(area.label)
                    for (d in decisions) DecisionRow(d)
                    for (slot in plan.report.equipment) {
                        Column(Modifier.fillMaxWidth().padding(vertical = 2.dp)) {
                            Text(
                                slot.slotName + ": " + (slot.item?.let { "${it.name} (item level ${it.itemLevel})" } ?: "nothing"),
                                style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Medium), color = Colors.Text,
                            )
                            Text(
                                listOfNotNull(slot.retail?.let { "for ${it.name}" }, slot.why.takeIf { it.isNotBlank() }).joinToString(" · "),
                                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
                            )
                        }
                    }
                    continue
                }
                if (decisions.isEmpty()) continue
                SectionLabel(area.label)
                AreaDecisions(decisions)
            }
            if (plan.report.counts.isNotEmpty()) {
                SectionLabel("Written")
                Text(plan.report.counts.entries.joinToString(" · ") { "${it.value} ${it.key}" }, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
            }
        }
        Row(Modifier.fillMaxWidth().padding(bottom = 8.dp), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End), verticalAlignment = Alignment.CenterVertically) {
            if (busy) {
                CircularProgressIndicator(Modifier.size(26.dp))
                Text("Porting…", style = MaterialTheme.typography.bodyMedium, color = Colors.Text)
            } else {
                FrameButton("Change", primary = false) { onBack() }
                if (plan.ready) FrameButton("Port to ${destination.title}") { onPort() }
            }
        }
    }
}

/** An area's decisions: the first dozen, and the rest on a tap (a character's quests can be thousands). */
@Composable
private fun AreaDecisions(decisions: List<PortDecision>) {
    var all by remember(decisions) { mutableStateOf(false) }
    val shown = if (all) decisions else decisions.take(12)
    for (d in shown) DecisionRow(d)
    if (!all && decisions.size > shown.size) {
        Text(
            "Show all ${decisions.size}", style = MaterialTheme.typography.labelLarge, color = Colors.Ice,
            modifier = Modifier.clip(RoundedCornerShape(8.dp)).clickable { all = true }.padding(vertical = 10.dp, horizontal = 4.dp),
        )
    }
}

@Composable
private fun DecisionRow(d: PortDecision) {
    Row(verticalAlignment = Alignment.Top, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        Box(Modifier.width(78.dp)) { Tag(outcomeWord(d.outcome), color = outcomeColor(d.outcome), filled = true) }
        Column(Modifier.weight(1f)) {
            Text(d.subject, style = MaterialTheme.typography.bodyMedium, color = Colors.Text)
            if (d.detail.isNotBlank()) Text(d.detail, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
        }
    }
}

@Composable
private fun DoneView(result: PortResult, plan: PortPlan, info: RealmInfo?, destination: Destination, onClose: () -> Unit) {
    Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("${result.name} is on ${destination.title}.", style = MaterialTheme.typography.headlineSmall, color = Colors.Text)
        Text(describe(plan, info) + ", with ${gold(plan.money)}, on account ${plan.account}.", style = MaterialTheme.typography.bodyMedium, color = Colors.Gold)
        Text(
            "Play World of Warcraft and log in with that account: ${result.name} is in its character list. The realm starts again with Play.",
            style = MaterialTheme.typography.bodyMedium, color = Colors.Text,
        )
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) { FrameButton("Done") { onClose() } }
    }
}
