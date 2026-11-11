package com.logie.blizz.ui

import android.content.Context
import android.graphics.BitmapFactory
import android.util.LruCache
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Key
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.logie.blizz.porter.BattleNetKey
import com.logie.blizz.porter.Porter
import com.logie.blizz.porter.armory.ArmoryCharacter
import com.logie.blizz.porter.armory.ArmoryItem
import com.logie.blizz.porter.armory.Found
import com.logie.blizz.porter.armory.Region
import com.logie.blizz.porter.view.PreviewView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * The Character Porter (World of Warcraft's options): find a character on Blizzard's Armory, by name in one of its regions, and
 * see them in 3D as they are dressed now, with what they wear, their professions, mounts and reputations. The look is made from
 * the game's own tables and files, fetched from wago.tools ([Porter]); porting the character into one of the phone's realms
 * comes next (the button says so).
 */
/** Where the porter's screens get what they show: the Armory, Blizzard's API and wago.tools ([LivePorterSource]); tests give their own. */
internal interface PorterSource {
    fun search(region: Region, query: String, page: Int): Pair<List<Found>, Boolean>
    fun character(found: Found): ArmoryCharacter
    /** How many mounts and factions with a standing; null when the Armory won't say. */
    fun counts(c: ArmoryCharacter): Pair<Int, Int>?
    fun appearance(context: Context, c: ArmoryCharacter): com.logie.blizz.porter.armory.Appearance?
    /** How many quests and achievements Blizzard's API gives (with a key). */
    fun progress(context: Context, c: ArmoryCharacter): Pair<Int, Int>?
    fun prepare(context: Context, c: ArmoryCharacter, appearance: com.logie.blizz.porter.armory.Appearance?, progress: (Porter.Step) -> Unit): Porter.Ready
}

internal object LivePorterSource : PorterSource {
    override fun search(region: Region, query: String, page: Int) = Porter.armory.search(region, query, page)
    override fun character(found: Found) = Porter.armory.character(found.region, found.realmSlug, found.slug)
    override fun counts(c: ArmoryCharacter) = runCatching {
        Porter.armory.mounts(c.region, c.realmSlug, c.slug).size to Porter.armory.reputations(c.region, c.realmSlug, c.slug).size
    }.getOrNull()
    override fun appearance(context: Context, c: ArmoryCharacter) =
        runCatching { BattleNetKey.client(context)?.appearance(c.region, c.realmSlug, c.slug) }.getOrNull()
    override fun progress(context: Context, c: ArmoryCharacter) = runCatching {
        val api = BattleNetKey.client(context) ?: return@runCatching null
        api.completedQuests(c.region, c.realmSlug, c.slug).size to api.achievements(c.region, c.realmSlug, c.slug).size
    }.getOrNull()
    override fun prepare(context: Context, c: ArmoryCharacter, appearance: com.logie.blizz.porter.armory.Appearance?, progress: (Porter.Step) -> Unit) =
        Porter.prepare(context, c, appearance, progress = progress)
}

private val LocalPorterSource = androidx.compose.runtime.staticCompositionLocalOf<PorterSource> { LivePorterSource }

@Composable
fun CharacterPorter(onDismiss: () -> Unit) = CharacterPorter(onDismiss, LivePorterSource)

@Composable
internal fun CharacterPorter(onDismiss: () -> Unit, source: PorterSource) = androidx.compose.runtime.CompositionLocalProvider(LocalPorterSource provides source) {
    CharacterPorterScreen(onDismiss)
}

@Composable
private fun CharacterPorterScreen(onDismiss: () -> Unit) {
    val context = LocalContext.current
    var picked by remember { mutableStateOf<Found?>(null) }
    var keyOpen by remember { mutableStateOf(false) }
    var keyStamp by remember { mutableStateOf(0) }
    val hasKey = remember(keyStamp) { BattleNetKey.get(context) != null }
    Dialog(onDismissRequest = { if (picked != null) picked = null else onDismiss() }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Box(Modifier.fillMaxSize().padding(14.dp), contentAlignment = Alignment.Center) {
            Column(Modifier.widthIn(max = 1180.dp).fillMaxSize().panel()) {
                Row(Modifier.fillMaxWidth().padding(start = 12.dp, end = 8.dp, top = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                    if (picked != null) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = Colors.Text,
                            modifier = Modifier.clip(RoundedCornerShape(50)).clickable { picked = null }.padding(10.dp).size(24.dp),
                        )
                    } else Spacer(Modifier.width(8.dp))
                    Column(Modifier.weight(1f).padding(start = 4.dp)) {
                        FrameTitle("Character Porter", style = MaterialTheme.typography.titleLarge)
                        Text(
                            "Find a character on the Armory, see them in 3D, bring them into your realm.",
                            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
                        )
                    }
                    Icon(
                        Icons.Default.Key, "Battle.net API key", tint = if (hasKey) Colors.Ice else Colors.Mist,
                        modifier = Modifier.clip(RoundedCornerShape(50)).clickable { keyOpen = true }.padding(10.dp).size(24.dp),
                    )
                    CloseButton(onDismiss)
                }
                val found = picked
                if (found == null) SearchPane(onPick = { picked = it }) else key(keyStamp) { CharacterPane(found, hasKey, onKey = { keyOpen = true }) }
            }
        }
    }
    if (keyOpen) KeyDialog(onDone = { keyOpen = false; keyStamp++ })
}

/** The person's own Battle.net API client: the id and the secret, tried before they are kept. */
@Composable
private fun KeyDialog(onDone: () -> Unit) {
    val context = LocalContext.current
    val kept = remember { BattleNetKey.get(context) }
    var id by remember { mutableStateOf(kept?.first.orEmpty()) }
    var secret by remember { mutableStateOf(kept?.second.orEmpty()) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    Dialog(onDismissRequest = onDone) {
        Column(Modifier.widthIn(max = 520.dp).panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("Battle.net API key (optional)", style = MaterialTheme.typography.titleMedium, color = Colors.Text)
            Text(
                "With a key of your own the porter also has the character's face, hair and skin as they chose them, the quests " +
                    "they completed and their achievements. Make one for free at develop.battle.net: sign in, API Access, Create " +
                    "Client (any name; no redirect address needed), then copy its Client ID and Client Secret here. They stay on this phone.",
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
            )
            OutlinedTextField(id, { id = it }, Modifier.fillMaxWidth(), singleLine = true, label = { Text("Client ID") })
            OutlinedTextField(secret, { secret = it }, Modifier.fillMaxWidth(), singleLine = true, label = { Text("Client Secret") },
                visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation())
            error?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = Modern.Bad) }
            Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                if (busy) CircularProgressIndicator(Modifier.size(24.dp))
                if (kept != null) FrameButton("Remove", primary = false) { BattleNetKey.clear(context); onDone() }
                FrameButton("Cancel", primary = false) { onDone() }
                FrameButton("Save") {
                    if (busy || id.isBlank() || secret.isBlank()) return@FrameButton
                    busy = true
                    error = null
                    scope.launch {
                        val r = withContext(Dispatchers.IO) { runCatching { BattleNetKey.tried(id, secret) } }
                        busy = false
                        r.onSuccess { BattleNetKey.set(context, id, secret); onDone() }
                            .onFailure { error = it.message ?: "Battle.net couldn't be reached." }
                    }
                }
            }
        }
    }
}

// Search -----------------------------------------------------------------------------------------------------------------

@Composable
private fun ColumnScope.SearchPane(onPick: (Found) -> Unit) {
    var region by rememberSaveable { mutableStateOf(Region.US) }
    var query by rememberSaveable { mutableStateOf("") }
    var results by remember { mutableStateOf<List<Found>?>(null) }
    var page by remember { mutableStateOf(1) }
    var more by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    val source = LocalPorterSource.current
    fun search(next: Boolean = false) {
        val q = query.trim()
        if (q.length < 2 || busy) return
        busy = true
        error = null
        val p = if (next) page + 1 else 1
        scope.launch {
            val r = withContext(Dispatchers.IO) { runCatching { source.search(region, q, p) } }
            busy = false
            r.onSuccess { (list, hasMore) ->
                results = if (next) results.orEmpty() + list else list
                page = p
                more = hasMore
            }.onFailure { error = "The Armory couldn't be searched: ${it.message ?: it.javaClass.simpleName}" }
        }
    }
    Column(Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        PillSegmented(Region.entries.map { it.label to it }, region) { region = it; results = null }
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            OutlinedTextField(
                query, { query = it }, Modifier.weight(1f),
                singleLine = true,
                placeholder = { Text("Character name") },
                leadingIcon = { Icon(Icons.Default.Search, null) },
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                keyboardActions = KeyboardActions(onSearch = { search() }),
            )
            FrameButton("Search", primary = true) { search() }
        }
        error?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = Modern.Bad) }
    }
    Box(Modifier.weight(1f).fillMaxWidth()) {
        val list = results
        when {
            list == null && busy -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
            list == null -> Text(
                "Type a character's name. The Armory lists characters who have played lately, above level 10, on Blizzard's own realms.",
                style = MaterialTheme.typography.bodyMedium, color = Colors.Mist, modifier = Modifier.padding(20.dp),
            )
            list.isEmpty() -> Text("No character of that name in ${region.label}.", style = MaterialTheme.typography.bodyMedium, color = Colors.Mist, modifier = Modifier.padding(20.dp))
            else -> LazyColumn(Modifier.fillMaxSize().padding(horizontal = 12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                items(list, key = { "${it.region.code}/${it.realmSlug}/${it.slug}" }) { f -> FoundRow(f) { onPick(f) } }
                if (more) item {
                    Box(Modifier.fillMaxWidth().padding(10.dp), contentAlignment = Alignment.Center) {
                        if (busy) CircularProgressIndicator(Modifier.size(28.dp)) else FrameButton("More", primary = false) { search(next = true) }
                    }
                }
            }
        }
    }
}

@Composable
private fun FoundRow(f: Found, onClick: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().box().clickable(onClick = onClick).padding(10.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        WebImage(f.avatar, Modifier.size(48.dp).clip(RoundedCornerShape(10.dp))) {
            Box(Modifier.fillMaxSize().background(Colors.Deep), contentAlignment = Alignment.Center) { Icon(Icons.Default.Person, null, tint = Colors.Steel) }
        }
        Column(Modifier.weight(1f)) {
            Text(f.name, style = MaterialTheme.typography.titleMedium, color = Colors.Text, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text("Level ${f.level} ${f.race} ${f.className} · ${f.realm}", style = MaterialTheme.typography.bodySmall, color = Colors.Mist, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
        Tag(f.faction, color = factionColor(f.faction), filled = true)
    }
}

// A character ------------------------------------------------------------------------------------------------------------

private sealed interface Shown {
    data object Loading : Shown
    data class Failed(val message: String) : Shown
    data class Ready(val c: ArmoryCharacter) : Shown
}

@Composable
private fun ColumnScope.CharacterPane(found: Found, hasKey: Boolean, onKey: () -> Unit) {
    val context = LocalContext.current
    val source = LocalPorterSource.current
    val character by produceState<Shown>(Shown.Loading, found) {
        value = withContext(Dispatchers.IO) {
            runCatching { Shown.Ready(source.character(found)) }
                .getOrElse { Shown.Failed(it.message ?: it.javaClass.simpleName) }
        }
    }
    when (val s = character) {
        Shown.Loading -> Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
        is Shown.Failed -> Text(s.message, style = MaterialTheme.typography.bodyMedium, color = Modern.Bad, modifier = Modifier.padding(20.dp))
        is Shown.Ready -> BoxWithConstraints(Modifier.weight(1f).fillMaxWidth()) {
            val wide = maxWidth > 720.dp
            if (wide) {
                Row(Modifier.fillMaxSize().padding(12.dp), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    ModelPane(context, s.c, hasKey, Modifier.weight(1.1f).fillMaxHeight())
                    Details(s.c, hasKey, onKey, Modifier.weight(1f).fillMaxHeight())
                }
            } else {
                Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(12.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    ModelPane(context, s.c, hasKey, Modifier.fillMaxWidth().height(460.dp))
                    Details(s.c, hasKey, onKey, Modifier.fillMaxWidth(), scroll = false)
                }
            }
        }
    }
}

private sealed interface Model {
    data class Working(val text: String, val fraction: Float?) : Model
    data class Failed(val message: String) : Model
    data class Ready(val ready: Porter.Ready) : Model
}

/** The character in 3D, made ready (downloaded) the first time with its progress. */
@Composable
private fun ModelPane(context: Context, c: ArmoryCharacter, hasKey: Boolean, modifier: Modifier) {
    val source = LocalPorterSource.current
    var state by remember(c) { mutableStateOf<Model>(Model.Working("Reading the game's tables…", null)) }
    LaunchedEffect(c, hasKey) {
        state = withContext(Dispatchers.IO) {
            runCatching {
                // With the person's key, the character's own face and hair (a refusal leaves the race's defaults).
                val appearance = if (!hasKey) null else {
                    state = Model.Working("Asking Blizzard's API for their face and hair…", null)
                    source.appearance(context, c)
                }
                source.prepare(context, c, appearance) { step ->
                    state = when (step) {
                        Porter.Step.Tables -> Model.Working("Reading the game's tables…", null)
                        is Porter.Step.Files -> Model.Working(
                            "Downloading ${c.race} and what they wear: ${step.done} of ${step.total} files, ${step.megabytes} MB",
                            if (step.total > 0) step.done / step.total.toFloat() else null,
                        )
                    }
                }
            }.fold({ Model.Ready(it) }, { Model.Failed(it.message ?: it.javaClass.simpleName) })
        }
    }
    Box(modifier.clip(RoundedCornerShape(16.dp)).background(Color(0xFF0B0E14)).border(1.dp, Modern.Outline, RoundedCornerShape(16.dp))) {
        when (val s = state) {
            is Model.Ready -> {
                PreviewSurface(s.ready)
                Text(
                    "Drag to turn · pinch to come closer · double tap to stand back",
                    style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
                    modifier = Modifier.align(Alignment.BottomCenter).padding(10.dp),
                )
            }
            is Model.Working -> Column(
                Modifier.align(Alignment.Center).padding(24.dp).widthIn(max = 420.dp),
                horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                if (s.fraction == null) CircularProgressIndicator() else LinearProgressIndicator(progress = { s.fraction }, modifier = Modifier.fillMaxWidth())
                Text(s.text, style = MaterialTheme.typography.bodyMedium, color = Colors.Text)
                Text(
                    "The game's models and textures come from wago.tools, once: the first character of a race takes a while (tens of MB).",
                    style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
                )
            }
            is Model.Failed -> Text(
                "The 3D look couldn't be made: ${s.message}",
                style = MaterialTheme.typography.bodyMedium, color = Modern.Bad, modifier = Modifier.align(Alignment.Center).padding(20.dp),
            )
        }
    }
}

@Composable
private fun PreviewSurface(ready: Porter.Ready) {
    val context = LocalContext.current
    var view by remember { mutableStateOf<PreviewView?>(null) }
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    DisposableEffect(lifecycle, view) {
        val v = view
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_PAUSE -> v?.onPause()
                Lifecycle.Event.ON_RESUME -> v?.onResume()
                else -> {}
            }
        }
        lifecycle.addObserver(observer)
        onDispose { lifecycle.removeObserver(observer) }
    }
    AndroidView(
        factory = { PreviewView(context, ready.files).also { it.show(ready.look); view = it } },
        update = { it.show(ready.look) },
        modifier = Modifier.fillMaxSize(),
    )
}

@Composable
private fun Details(c: ArmoryCharacter, hasKey: Boolean, onKey: () -> Unit, modifier: Modifier, scroll: Boolean = true) {
    val context = LocalContext.current
    val source = LocalPorterSource.current
    val inner = if (scroll) Modifier.verticalScroll(rememberScrollState()) else Modifier
    Column(modifier.then(inner), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Column {
            Text(c.name, style = MaterialTheme.typography.headlineSmall, color = Colors.Text)
            Text(
                "Level ${c.level} ${c.race} ${c.className}" + (c.spec?.let { " · $it" } ?: ""),
                style = MaterialTheme.typography.titleSmall, color = Colors.Gold,
            )
            Text(
                listOfNotNull(c.realm + " (" + c.region.code.uppercase() + ")", c.guild?.let { "<$it>" }, "item level ${c.averageItemLevel}").joinToString(" · "),
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
            )
            Row(Modifier.padding(top = 6.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Tag(c.faction.lowercase().replaceFirstChar { it.uppercase() }, color = factionColor(c.faction), filled = true)
                Tag(if (c.gender == 1) "Female" else "Male")
                if (c.achievementPoints > 0) Tag("${c.achievementPoints} achievement points")
            }
        }
        if (hasKey) {
            val more by produceState<Pair<Int, Int>?>(null, c) { value = withContext(Dispatchers.IO) { source.progress(context, c) } }
            Text(
                "Face, hair and skin as they chose them, from Blizzard's API" + (more?.let { (q, a) -> " · $q quests completed · $a achievements" } ?: ""),
                style = MaterialTheme.typography.bodySmall, color = Colors.Ice,
            )
        } else {
            Text(
                "Face, hair and skin are the race's defaults: the Armory's website doesn't say which a character chose. A Battle.net API key of your own adds them, with quests and achievements.",
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
            )
            FrameButton("Add a Battle.net key", primary = false) { onKey() }
        }
        SectionLabel("Equipped")
        for (item in c.items) ItemRow(item)
        if (c.professions.isNotEmpty()) {
            SectionLabel("Professions")
            for (p in c.professions) {
                val best = p.tiers.maxByOrNull { it.points }
                Text(
                    p.name + (best?.let { " · ${it.name} ${it.points}/${it.max}" } ?: ""),
                    style = MaterialTheme.typography.bodyMedium, color = Colors.Text,
                )
            }
        }
        val extra by produceState<Pair<Int, Int>?>(null, c) { value = withContext(Dispatchers.IO) { source.counts(c) } }
        extra?.let { (mounts, reputations) ->
            SectionLabel("Collections")
            Text("$mounts mounts · $reputations factions with a standing", style = MaterialTheme.typography.bodyMedium, color = Colors.Text)
        }
        SectionLabel("Port")
        Text(
            "Bringing this character into a realm on the phone (Wrath+'s ChromieCraft first: race, sex, class, level, gear chosen " +
                "from the realm's own items, gold, spells, mounts, reputations) is being finished and tested; the next update adds it here.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
    }
}

@Composable
private fun ItemRow(item: ArmoryItem) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        WebImage(item.icon, Modifier.size(36.dp).clip(RoundedCornerShape(6.dp)).border(1.dp, qualityColor(item.quality).copy(alpha = 0.7f), RoundedCornerShape(6.dp))) {
            Box(Modifier.fillMaxSize().background(Colors.Deep))
        }
        Column(Modifier.weight(1f)) {
            Text(item.name, style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Medium), color = qualityColor(item.quality), maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(
                listOfNotNull(slotName(item.slot), item.itemLevel.takeIf { it > 0 }?.let { "item level $it" }, item.transmogName?.let { "looks like $it" }).joinToString(" · "),
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist, maxLines = 1, overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

private fun slotName(slot: String) = when (slot) {
    "head" -> "Head"; "neck" -> "Neck"; "shoulder" -> "Shoulder"; "back" -> "Back"; "chest" -> "Chest"; "shirt" -> "Shirt"
    "tabard" -> "Tabard"; "wrist" -> "Wrist"; "hand" -> "Hands"; "waist" -> "Waist"; "leg" -> "Legs"; "foot" -> "Feet"
    "leftFinger", "rightFinger" -> "Finger"; "leftTrinket", "rightTrinket" -> "Trinket"; "weapon" -> "Main hand"; "offhand" -> "Off hand"
    else -> slot
}

private fun qualityColor(quality: String) = when (quality) {
    "POOR" -> Color(0xFF9D9D9D); "UNCOMMON" -> Color(0xFF1EFF00); "RARE" -> Color(0xFF0070DD); "EPIC" -> Color(0xFFA335EE)
    "LEGENDARY" -> Color(0xFFFF8000); "ARTIFACT" -> Color(0xFFE6CC80); "HEIRLOOM" -> Color(0xFF00CCFF); else -> Color(0xFFF3F6FA)
}

private fun factionColor(faction: String) = when (faction.uppercase()) {
    "HORDE" -> Color(0xFFE5484D); "ALLIANCE" -> Color(0xFF4C8DFF); else -> Modern.Muted
}

// Pictures from the Armory (portraits, item icons) -------------------------------------------------------------------------

private object PorterImages {
    private val memory = object : LruCache<String, ImageBitmap>(16 * 1024 * 1024) {
        override fun sizeOf(key: String, value: ImageBitmap) = value.width * value.height * 4
    }
    private val fetching = Semaphore(4)

    suspend fun load(context: Context, url: String): ImageBitmap? {
        memory.get(url)?.let { return it }
        return withContext(Dispatchers.IO) {
            runCatching {
                val dir = File(context.cacheDir, "porter-images")
                val file = File(dir, MessageDigest.getInstance("SHA-1").digest(url.toByteArray()).joinToString("") { "%02x".format(it) })
                if (!file.isFile) fetching.withPermit {
                    dir.mkdirs()
                    val connection = (URL(url).openConnection() as HttpURLConnection).apply {
                        connectTimeout = 15_000
                        readTimeout = 30_000
                        setRequestProperty("User-Agent", com.logie.blizz.porter.net.HttpNet.BROWSER)
                    }
                    try {
                        if (connection.responseCode !in 200..299) throw java.io.IOException("HTTP ${connection.responseCode}")
                        val part = File(dir, file.name + ".part")
                        connection.inputStream.use { input -> part.outputStream().use { input.copyTo(it) } }
                        part.renameTo(file)
                    } finally {
                        connection.disconnect()
                    }
                }
                BitmapFactory.decodeFile(file.path)?.asImageBitmap()?.also { memory.put(url, it) }
            }.getOrNull()
        }
    }
}

@Composable
private fun WebImage(url: String?, modifier: Modifier, placeholder: @Composable () -> Unit) {
    val context = LocalContext.current
    val image by produceState<ImageBitmap?>(null, url) { value = url?.let { PorterImages.load(context, it) } }
    Box(modifier) {
        val shown = image
        if (shown != null) Image(shown, null, contentScale = ContentScale.Crop, modifier = Modifier.matchParentSize())
        else Box(Modifier.matchParentSize()) { placeholder() }
    }
}
