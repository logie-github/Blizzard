package com.logie.blizz.ui

import android.content.Intent
import android.net.Uri
import android.text.format.DateUtils
import android.text.format.Formatter
import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.Stable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.wow.Realm
import com.logie.blizz.wow.WowRealm
import com.logie.blizz.wowmodules.ModuleBuild
import com.logie.blizz.wowmodules.ModuleCatalog
import com.logie.blizz.wowmodules.ModuleReadme
import com.logie.blizz.wowmodules.ModuleSource
import com.logie.blizz.wowmodules.ModuleStore
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private val Good = Color(0xFF7BD88F)
private val Blood = Color(0xFFE5675C)

private enum class ModuleTab { BROWSE, REALM }

/**
 * The Wrath+ realm's module browser. Browse: AzerothCore's modules (GitHub's topic azerothcore-module),
 * searched and ordered, each added to the realm's list in one tap or opened for its README. Realm: the
 * picked modules, the realm built with them on GitHub (with the user's own token) and put in place of
 * the one Blizzard holds, or the realm's own back.
 */
@Composable
fun WowModuleManager(onDismiss: () -> Unit) {
    val context = LocalContext.current
    var tab by rememberSaveable { mutableStateOf(ModuleTab.BROWSE) }
    var open by remember { mutableStateOf<ModuleCatalog.Listing?>(null) }
    val browse = remember { ModuleBrowseState() }
    remember { ModuleStore.load(context) }
    val chosen by ModuleStore.chosen.collectAsState()
    val pending by ModuleStore.pending.collectAsState()

    Dialog(
        onDismissRequest = { if (open != null) open = null else onDismiss() },
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Column(
            Modifier.padding(14.dp).widthIn(max = 620.dp).fillMaxWidth().fillMaxHeight(0.94f).heightIn(max = 820.dp)
                .drawBehind {
                    drawRect(Brush.verticalGradient(listOf(Colors.Night, Colors.Deep)))
                    drawFrame()
                },
        ) {
            Row(Modifier.fillMaxWidth().padding(start = 20.dp, end = 8.dp, top = 14.dp), verticalAlignment = Alignment.CenterVertically) {
                val details = open
                if (details != null) {
                    Icon(
                        Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = Colors.Mist,
                        modifier = Modifier.clip(CircleShape).clickable { open = null }.padding(8.dp).size(24.dp),
                    )
                    FrameTitle(details.name, Modifier.weight(1f).padding(start = 4.dp), style = MaterialTheme.typography.titleLarge)
                } else {
                    FrameTitle("Modules", Modifier.weight(1f))
                }
                Icon(
                    Icons.Default.Close, "Close", tint = Colors.Mist,
                    modifier = Modifier.clip(CircleShape).clickable(onClick = onDismiss).padding(12.dp).size(24.dp),
                )
            }
            val unavailable = remember(tab, open) { ModuleStore.unavailableReason(context) }
            if (open == null) {
                Box(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp)) {
                    val building = pending?.isDone == false
                    Segmented(
                        listOf(
                            "Browse" to ModuleTab.BROWSE,
                            ("Realm" + (if (chosen.isNotEmpty()) " (${chosen.size})" else "") + (if (building) " …" else "")) to ModuleTab.REALM,
                        ),
                        tab,
                    ) { tab = it }
                }
            }
            Box(Modifier.fillMaxWidth().height(1.dp).background(Colors.Steel.copy(alpha = 0.6f)))
            val details = open
            Box(Modifier.weight(1f).fillMaxWidth()) {
                when {
                    details != null -> ModuleDetailsPane(details, chosen)
                    tab == ModuleTab.BROWSE -> ModuleBrowsePane(browse, chosen, onOpen = { open = it })
                    else -> RealmPane(unavailable)
                }
            }
        }
    }
}

// Pieces --------------------------------------------------------------------------------------------

@Composable
private fun Line(
    text: String,
    modifier: Modifier = Modifier,
    color: Color = Colors.Text,
    small: Boolean = false,
    maxLines: Int = Int.MAX_VALUE,
) {
    Text(
        text, modifier, color = color,
        style = if (small) MaterialTheme.typography.bodySmall else MaterialTheme.typography.bodyMedium,
        maxLines = maxLines, overflow = TextOverflow.Ellipsis,
    )
}

@Composable
private fun Heading(text: String, modifier: Modifier = Modifier) {
    Text(text, modifier, color = Colors.Text, style = MaterialTheme.typography.titleMedium, maxLines = 2, overflow = TextOverflow.Ellipsis)
}

/** [FrameButton], dimmed and doing nothing while it is not [enabled]. */
@Composable
private fun Btn(text: String, modifier: Modifier = Modifier, primary: Boolean = true, enabled: Boolean = true, onClick: () -> Unit) {
    if (enabled) {
        FrameButton(text, modifier, primary, onClick)
    } else {
        FrameButton(text, modifier.alpha(0.4f), primary) {}
    }
}

@Composable
private fun Spinner(size: Int = 22) {
    CircularProgressIndicator(Modifier.size(size.dp), color = Colors.Ice, strokeWidth = 2.dp)
}

@Composable
private fun ProgressBar(progress: Float?) {
    val modifier = Modifier.fillMaxWidth().height(4.dp)
    if (progress == null) {
        LinearProgressIndicator(modifier, color = Colors.Ice, trackColor = Colors.Frost)
    } else {
        LinearProgressIndicator({ progress.coerceIn(0f, 1f) }, modifier, color = Colors.Ice, trackColor = Colors.Frost)
    }
}

private fun openUrl(context: android.content.Context, url: String) {
    runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
}

/** A hairline-framed block that grows and shrinks with what's in it. */
@Composable
private fun Card(modifier: Modifier = Modifier, onClick: (() -> Unit)? = null, content: @Composable () -> Unit) {
    Column(
        modifier.fillMaxWidth()
            .animateContentSize()
            .background(Colors.Abyss.copy(alpha = 0.55f))
            .border(1.dp, Colors.Steel.copy(alpha = 0.7f))
            .let { if (onClick != null) it.clickable(onClick = onClick) else it }
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) { content() }
}

// Browse ------------------------------------------------------------------------------------------

/** The list as far as it's been read, for what's searched; more pages as the list scrolls. */
@Stable
private class ModuleBrowseState {
    var search by mutableStateOf("")
    var query by mutableStateOf("")
        private set
    var order by mutableStateOf(ModuleCatalog.Order.STARS)
        private set
    val items = mutableStateListOf<ModuleCatalog.Listing>()
    var total by mutableIntStateOf(0)
    var page by mutableIntStateOf(0)
    var loading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    val list = LazyListState()
    private var generation = 0

    // GitHub's search answers the first thousand.
    val hasMore get() = page == 0 || (items.size < minOf(total, 1000) && page * ModuleCatalog.PER_PAGE < 1000)

    fun change(query: String = this.query, order: ModuleCatalog.Order = this.order) {
        if (query == this.query && order == this.order) return
        generation++
        this.query = query
        this.order = order
        items.clear()
        total = 0
        page = 0
        loading = false
        error = null
    }

    suspend fun loadMore(context: android.content.Context) {
        if (loading || !hasMore) return
        val asked = generation
        loading = true
        error = null
        try {
            val result = ModuleStore.search(context, query, order, page + 1)
            if (asked != generation) return
            val seen = items.mapTo(HashSet()) { it.fullName }
            items += result.items.filter { seen.add(it.fullName) }
            total = if (result.items.isEmpty()) items.size else result.total
            page += 1
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            if (asked == generation) error = e.message ?: e.javaClass.simpleName
        } finally {
            if (asked == generation) loading = false
        }
    }
}

@Composable
private fun ModuleBrowsePane(state: ModuleBrowseState, chosen: List<ModuleBuild.Chosen>, onOpen: (ModuleCatalog.Listing) -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val focus = LocalFocusManager.current

    LaunchedEffect(state.search) {
        delay(700)
        state.change(query = state.search.trim())
    }
    LaunchedEffect(state.query, state.order) {
        if (state.page == 0) {
            state.list.scrollToItem(0)
            state.loadMore(context)
        }
    }
    LaunchedEffect(state) {
        snapshotFlow {
            val info = state.list.layoutInfo
            val near = (info.visibleItemsInfo.lastOrNull()?.index ?: 0) >= info.totalItemsCount - 6
            Triple(near, state.items.size, state.error)
        }.collect { (near, _, error) ->
            if (near && error == null && state.page > 0) state.loadMore(context)
        }
    }

    Column(Modifier.fillMaxSize()) {
        Column(Modifier.padding(horizontal = 18.dp, vertical = 10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            OutlinedTextField(
                value = state.search,
                onValueChange = { state.search = it },
                placeholder = { Text("Search modules", color = Colors.Mist) },
                leadingIcon = { Icon(Icons.Default.Search, null, tint = Colors.Mist) },
                trailingIcon = {
                    if (state.search.isNotEmpty()) {
                        Icon(
                            Icons.Default.Close, "Clear the search", tint = Colors.Mist,
                            modifier = Modifier.clip(CircleShape).clickable { state.search = ""; state.change(query = "") }.padding(8.dp).size(24.dp),
                        )
                    }
                },
                singleLine = true,
                textStyle = MaterialTheme.typography.bodyLarge,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search, autoCorrectEnabled = false),
                keyboardActions = KeyboardActions(onSearch = {
                    state.change(query = state.search.trim())
                    focus.clearFocus()
                }),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Colors.Text, unfocusedTextColor = Colors.Text,
                    focusedBorderColor = Colors.Ice, unfocusedBorderColor = Colors.Steel, cursorColor = Colors.Ice,
                    focusedContainerColor = Colors.Abyss.copy(alpha = 0.55f), unfocusedContainerColor = Colors.Abyss.copy(alpha = 0.55f),
                ),
                modifier = Modifier.fillMaxWidth(),
            )
            Segmented(
                listOf("Most stars" to ModuleCatalog.Order.STARS, "Recently changed" to ModuleCatalog.Order.UPDATED),
                state.order,
            ) { state.change(order = it) }
            if (state.total > 0) Line("${state.total} module${if (state.total == 1) "" else "s"}", color = Colors.Mist, small = true)
        }
        LazyColumn(
            Modifier.weight(1f).fillMaxWidth(),
            state = state.list,
            contentPadding = androidx.compose.foundation.layout.PaddingValues(start = 18.dp, end = 18.dp, bottom = 18.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            items(state.items, key = { it.fullName }) { listing ->
                ModuleCard(listing, chosen, onOpen = { onOpen(listing) })
            }
            item {
                Column(
                    Modifier.fillMaxWidth().padding(vertical = 12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    val error = state.error
                    when {
                        state.loading -> Spinner(32)
                        error != null -> {
                            Line("Couldn't load that from GitHub: $error")
                            Btn("Try again", primary = false) { scope.launch { state.loadMore(context) } }
                        }
                        state.items.isEmpty() && !state.hasMore -> Line("No modules found.", color = Colors.Mist)
                    }
                    Line(
                        "Modules from github.com/topics/azerothcore-module. Each is someone's own code: they change the realm itself.",
                        color = Colors.Mist, small = true,
                    )
                }
            }
        }
    }
}

/** A module's line of facts: stars, last change, language, archived. */
private fun facts(listing: ModuleCatalog.Listing): String = listOfNotNull(
    "★ ${listing.stars}",
    ModuleCatalog.day(listing.updated)?.let { "changed $it" },
    listing.language,
    if (listing.archived) "archived" else null,
).joinToString(" · ")

@Composable
private fun ModuleCard(listing: ModuleCatalog.Listing, chosen: List<ModuleBuild.Chosen>, onOpen: () -> Unit) {
    Card(onClick = onOpen) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Heading(listing.name)
                Line("by ${listing.owner}", color = Colors.Gold, small = true, maxLines = 1)
                listing.description?.let { Line(it, color = Colors.Text, small = true, maxLines = 3) }
                Line(facts(listing), color = Colors.Mist, small = true, maxLines = 1)
            }
            Spacer(Modifier.width(10.dp))
            AddButton(listing, chosen)
        }
    }
}

/** Add, Remove, or In the realm for the realm's own. */
@Composable
private fun AddButton(listing: ModuleCatalog.Listing, chosen: List<ModuleBuild.Chosen>) {
    val context = LocalContext.current
    val width = Modifier.widthIn(min = 100.dp)
    when {
        listing.name in ModuleStore.baseModules -> Line("In the realm", color = Good, small = true)
        chosen.any { it.fullName.equals(listing.fullName, ignoreCase = true) } ->
            Btn("Remove", width, primary = false) { ModuleStore.remove(context, listing.fullName) }
        else -> Btn("Add", width) { ModuleStore.add(context, listing) }
    }
}

// A module's page ---------------------------------------------------------------------------------

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun ModuleDetailsPane(listing: ModuleCatalog.Listing, chosen: List<ModuleBuild.Chosen>) {
    val context = LocalContext.current
    var attempt by remember { mutableIntStateOf(0) }
    val readme by produceState<Result<String?>?>(null, listing.fullName, attempt) {
        value = null
        value = try {
            Result.success(ModuleStore.readme(context, listing.fullName))
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    val blocks = remember(readme) { readme?.getOrNull()?.let { ModuleReadme.blocks(it) } ?: emptyList() }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(start = 18.dp, end = 18.dp, top = 14.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Line("by ${listing.owner}", color = Colors.Gold, small = true)
                listing.description?.let { Line(it) }
            }
        }
        item {
            FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                AddButton(listing, chosen)
                Btn("GitHub page", primary = false) { openUrl(context, listing.url) }
            }
        }
        item {
            SettingCard("Facts") {
                Fact("Stars", listing.stars.toString())
                ModuleCatalog.day(listing.updated)?.let { Fact("Last changed", it) }
                Fact("Branch", listing.defaultBranch)
                listing.language?.let { Fact("Language", it) }
                if (listing.archived) Fact("State", "archived", Blood)
                Line(
                    "A module is code built into the realm's world server. Added ones come in when the realm is built again (Realm), at the branch's newest commit. " +
                        "Its README says what it needs: some want settings, a client patch or a version of AzerothCore other than ChromieCraft's.",
                    color = Colors.Mist, small = true,
                )
            }
        }
        item { FrameTitle("README", style = MaterialTheme.typography.titleLarge) }
        val current = readme
        when {
            current == null -> item { Box(Modifier.fillMaxWidth().padding(8.dp), contentAlignment = Alignment.Center) { Spinner(32) } }
            current.isFailure -> item {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    val error = current.exceptionOrNull()
                    Line("Couldn't load that from GitHub: ${error?.message ?: error?.javaClass?.simpleName.orEmpty()}")
                    Btn("Try again", primary = false) { attempt++ }
                }
            }
            blocks.isEmpty() -> item { Line("It has no README.", color = Colors.Mist) }
            else -> items(blocks) { block -> ReadmeBlock(block) }
        }
    }
}

@Composable
private fun Fact(label: String, value: String, color: Color = Colors.Text) {
    Row(Modifier.fillMaxWidth()) {
        Line(label, Modifier.weight(1f), color = Colors.Mist, small = true)
        Line(value, color = color, small = true, maxLines = 1)
    }
}

@Composable
private fun ReadmeBlock(block: ModuleReadme.Block) {
    when (block) {
        is ModuleReadme.Block.Heading -> Text(block.text, color = Colors.Gold, style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 6.dp))
        is ModuleReadme.Block.Paragraph -> Line(block.text)
        is ModuleReadme.Block.Item -> Row {
            Text(if (block.number != null) "${block.number}." else "•", color = Colors.Mist, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.width(26.dp))
            Line(block.text, Modifier.weight(1f))
        }
        is ModuleReadme.Block.Code -> Text(
            block.text,
            color = Colors.Glow,
            style = MaterialTheme.typography.bodySmall.copy(fontFamily = FontFamily.Monospace, fontSize = 12.sp),
            modifier = Modifier.fillMaxWidth().background(Colors.Abyss).border(1.dp, Colors.Steel.copy(alpha = 0.5f)).padding(10.dp),
        )
        ModuleReadme.Block.Rule -> Box(Modifier.fillMaxWidth().height(1.dp).background(Colors.Steel.copy(alpha = 0.6f)))
    }
}

// Realm -------------------------------------------------------------------------------------------

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun RealmPane(unavailable: String?) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val chosen by ModuleStore.chosen.collectAsState()
    val pending by ModuleStore.pending.collectAsState()
    val realm by ModuleStore.realm.collectAsState()
    val saved by ModuleStore.saved.collectAsState()
    val hasToken by ModuleStore.hasToken.collectAsState()
    val stockKept by ModuleStore.stockKept.collectAsState()
    val work by ModuleStore.work.collectAsState()
    val realmStatus by WowRealm.status.collectAsState()
    var asking by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var tokenDialog by remember { mutableStateOf(false) }
    var confirmStock by remember { mutableStateOf(false) }

    val working = work is ModuleStore.Work.Running
    val ready = unavailable == null
    val wrathRunning = realmStatus.realm.let { it == Realm.CHROMIE || it == Realm.REMIX } && realmStatus.phase != WowRealm.Phase.STOPPED && realmStatus.phase != WowRealm.Phase.FAILED
    // The modules the newest build left out (they don't compile with this realm).
    val leftOut = (pending?.leftOut ?: realm?.leftOut).orEmpty()

    // Which realm is in, read again when the screen opens (a game imported again has its own).
    LaunchedEffect(Unit) { ModuleStore.syncRealm(context) }

    // How the build is going, every half minute while it goes (and once when the screen opens);
    // once it's built, what went in.
    LaunchedEffect(pending?.request, pending?.isDone, pending?.leftOut == null) {
        val build = pending ?: return@LaunchedEffect
        if (build.isDone) {
            if (build.succeeded && build.leftOut == null) {
                runCatching { ModuleStore.refresh(context) }.onFailure { if (it is CancellationException) throw it }
            }
            return@LaunchedEffect
        }
        while (true) {
            runCatching { ModuleStore.refresh(context) }
                .onFailure { if (it is CancellationException) throw it else error = it.message ?: it.javaClass.simpleName }
                .onSuccess { error = null }
            if (ModuleStore.pending.value?.isDone != false) break
            delay(30_000)
        }
    }

    fun startBuild() {
        asking = true
        error = null
        scope.launch {
            runCatching { ModuleStore.startBuild(context) }
                .onFailure { if (it is CancellationException) throw it else error = it.message ?: it.javaClass.simpleName }
            asking = false
        }
    }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(18.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Line(
                "The realm's world server is built with its modules in it, so a realm with yours is built again: by this app's repository on GitHub " +
                    "(its workflow build-realm-modules.yml: about an hour the first time, less after), from the realm's sources kept there, then tested " +
                    "the way the realm is tested. Blizzard then downloads it, checks it and puts it in place of the realm, which stops for it. " +
                    "Characters, accounts, bots and settings stay; each module's database changes are made at the realm's next start.",
                color = Colors.Mist, small = true,
            )
        }
        if (unavailable != null) item { Line(unavailable, color = Colors.Gold) }

        // The realm in now.
        item {
            SettingCard("The realm in") {
                val current = realm
                if (current != null) {
                    Line("With your modules: " + current.modules.joinToString(", ") { it.name }.ifEmpty { "none" }, color = Good)
                    if (current.builtAt > 0) Line("Built " + DateUtils.getRelativeTimeSpanString(current.builtAt), color = Colors.Mist, small = true)
                    if (current.leftOut.isNotEmpty()) {
                        Line(
                            "Built without " + current.leftOut.joinToString(", ") { it.name } +
                                ": it doesn't compile with this realm's AzerothCore (it was written for another one). Remove it from your modules, or look for an up-to-date fork of it.",
                            color = Colors.Mist, small = true,
                        )
                    }
                    if (stockKept) {
                        Btn(
                            if (confirmStock) "Put the realm's own back" else "The realm's own back",
                            primary = false, enabled = ready && !working,
                        ) {
                            if (!confirmStock) {
                                confirmStock = true
                            } else {
                                confirmStock = false
                                ModuleStore.clearWork()
                                ModuleStore.installStock(context)
                            }
                        }
                    } else {
                        Line("The realm's own programs aren't kept on the phone, so they can't be put back from here (import World of Warcraft again for that).", color = Colors.Mist, small = true)
                    }
                } else {
                    Line("The realm's own.")
                }
                Line("Built in always: " + ModuleStore.baseModules.sorted().joinToString(", "), color = Colors.Mist, small = true)
            }
        }

        // Putting a realm in (or back).
        if (work !is ModuleStore.Work.Idle) {
            item {
                SettingCard(null) {
                    when (val w = work) {
                        is ModuleStore.Work.Running -> {
                            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                Spinner()
                                Column(Modifier.weight(1f)) {
                                    Heading(w.title)
                                    w.detail?.let { Line(it, color = Colors.Mist, small = true, maxLines = 2) }
                                }
                            }
                            ProgressBar(w.progress)
                            Btn("Stop", primary = false) { ModuleStore.cancelWork() }
                        }
                        is ModuleStore.Work.Done -> {
                            Line(w.message, color = Good)
                            Btn("OK", primary = false) { ModuleStore.clearWork() }
                        }
                        is ModuleStore.Work.Failed -> {
                            Line(w.message, color = Blood)
                            Btn("OK", primary = false) { ModuleStore.clearWork() }
                        }
                        ModuleStore.Work.Idle -> {}
                    }
                }
            }
        }

        // The build.
        item {
            SettingCard("Build") {
                val build = pending
                val version = ModuleStore.versionCode(context)
                when {
                    build == null -> {
                        Line(
                            if (chosen.isEmpty()) "Add modules in Browse, then build the realm with them here."
                            else "To build in: " + chosen.joinToString(", ") { it.name },
                        )
                        Btn(
                            if (asking) "Asking GitHub…" else "Build the realm with them",
                            enabled = ready && chosen.isNotEmpty() && hasToken && !asking,
                        ) { startBuild() }
                    }
                    !build.isDone -> {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            Spinner()
                            Line(
                                build.step?.let { "Building on GitHub: $it" }
                                    ?: if (build.runId == null) "Waiting for GitHub to start the build…" else "Building on GitHub…",
                            )
                        }
                        Line(
                            "With " + build.modules.joinToString(", ") { it.name } + " · asked for " + DateUtils.getRelativeTimeSpanString(build.startedAt) +
                                ". It carries on with the app closed; the app looks again when it opens.",
                            color = Colors.Mist, small = true,
                        )
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            build.runUrl?.let { url -> Btn("Open on GitHub", primary = false) { openUrl(context, url) } }
                            Btn("Stop the build", primary = false) { scope.launch { runCatching { ModuleStore.cancelBuild(context) } } }
                        }
                    }
                    build.succeeded && build.versionCode != version -> {
                        Line("Built for another version of the World of Warcraft app: build it again for this one.")
                        Btn("Done with it", primary = false) { ModuleStore.dismissBuild(context) }
                    }
                    build.succeeded -> {
                        Line("Built and tested. Put it in to play with it.", color = Good)
                        build.leftOut?.takeIf { it.isNotEmpty() }?.let { out ->
                            Line(
                                "Built without " + out.joinToString(", ") { it.name } +
                                    ": it doesn't compile with this realm's AzerothCore (it was written for another one). Remove it from your modules, or look for an up-to-date fork of it.",
                                color = Blood,
                            )
                            for (module in out) {
                                if (module.error.isNotBlank()) Line("${module.name}: ${module.error}", color = Colors.Mist, small = true, maxLines = 3)
                            }
                        }
                        if (wrathRunning) Line("The realm stops while it goes in; start it again after.", color = Colors.Mist, small = true)
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Btn("Put it in", enabled = ready && !working) {
                                ModuleStore.clearWork()
                                ModuleStore.installBuilt(context)
                            }
                            Btn("Done with it", primary = false, enabled = !working) { ModuleStore.dismissBuild(context) }
                        }
                    }
                    else -> {
                        Line(build.step?.let { "The build failed at: $it. Its log is on GitHub; a module may not build with this realm's AzerothCore." } ?: "The build failed.", color = Blood)
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Btn(
                                if (asking) "Asking GitHub…" else "Build again",
                                enabled = ready && chosen.isNotEmpty() && hasToken && !asking,
                            ) { startBuild() }
                            build.runUrl?.let { url -> Btn("Open on GitHub", primary = false) { openUrl(context, url) } }
                            Btn("Done with it", primary = false) { ModuleStore.dismissBuild(context) }
                        }
                    }
                }
                error?.let { Line(it, color = Blood, small = true) }
            }
        }

        // The token GitHub takes the build from.
        item {
            SettingCard("GitHub token") {
                Line(
                    if (hasToken) "Your GitHub token is in (kept in this app only)."
                    else "GitHub needs your token to start a build: a fine-grained token for ${ModuleSource.REPO}.",
                    color = if (hasToken) Good else Colors.Mist,
                    small = true,
                )
                FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Btn(if (hasToken) "Change the token" else "Add your token", primary = !hasToken) { tokenDialog = true }
                    if (hasToken) Btn("Remove the token", primary = false) { ModuleStore.clearToken(context) }
                }
            }
        }

        // The realms kept, to swap between.
        if (saved.isNotEmpty()) {
            item { FrameTitle("Kept realms", style = MaterialTheme.typography.titleLarge) }
            item {
                Line(
                    "Each realm you put in is kept on the phone, so you can swap between them and the realm's own in a minute or two, without building again. " +
                        "The world database follows: what a module taken out added there goes at the realm's next start (a few minutes). Characters stay.",
                    color = Colors.Mist, small = true,
                )
            }
            items(saved, key = { "realm-" + it.request }) { built ->
                SavedRealm(built, inNow = realm?.request == built.request, working = working || !ready)
            }
        }

        // The picks.
        item { FrameTitle("Your modules", style = MaterialTheme.typography.titleLarge) }
        if (chosen.isEmpty()) item { Line("None yet.", color = Colors.Mist) }
        items(chosen, key = { it.fullName }) { module ->
            val built = realm?.modules?.any { it.fullName.equals(module.fullName, ignoreCase = true) } == true
            val broken = !built && leftOut.any { it.name.equals(module.name, ignoreCase = true) }
            Card {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                        Heading(module.name)
                        Line(
                            "by ${module.fullName.substringBefore('/')} · " + when {
                                built -> "in the realm"
                                broken -> "doesn't compile with this realm"
                                else -> "not built in yet"
                            },
                            color = when {
                                built -> Good
                                broken -> Blood
                                else -> Colors.Mist
                            },
                            small = true, maxLines = 1,
                        )
                        module.description?.let { Line(it, small = true, maxLines = 2) }
                    }
                    Spacer(Modifier.width(8.dp))
                    Btn("Remove", primary = false) { ModuleStore.remove(context, module.fullName) }
                }
            }
        }
    }

    if (tokenDialog) TokenDialog(onDismiss = { tokenDialog = false })
}

/** A realm kept on the phone: put in again, its modules made the picks, or deleted. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun SavedRealm(built: ModuleBuild.Built, inNow: Boolean, working: Boolean) {
    val context = LocalContext.current
    var confirmDelete by remember(built.request) { mutableStateOf(false) }
    val usable = remember(built) { ModuleStore.canPutIn(context, built) }
    val version = remember(built) { ModuleStore.versionCode(context) }
    Card {
        Heading("With " + built.modules.joinToString(", ") { it.name }.ifEmpty { "no modules of yours" })
        Line(
            when {
                usable -> "Built ${DateUtils.getRelativeTimeSpanString(built.builtAt)} · ${Formatter.formatShortFileSize(context, built.size)}"
                built.versionCode != version -> "Built from older realm sources: build it again to use it."
                else -> "That realm isn't on the phone any more: build it again."
            },
            color = Colors.Mist, small = true,
        )
        if (built.leftOut.isNotEmpty()) {
            Line("Built without " + built.leftOut.joinToString(", ") { it.name } + ": it doesn't compile with this realm's AzerothCore.", color = Colors.Mist, small = true)
        }
        FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            if (inNow) {
                Line("In now", color = Good)
            } else if (usable) {
                Btn("Put this one in", enabled = !working) {
                    ModuleStore.clearWork()
                    ModuleStore.putIn(context, built.request)
                }
            }
            Btn("Use these modules", primary = false) { ModuleStore.useModules(context, built) }
            if (!inNow) {
                Btn(if (confirmDelete) "Delete it" else "Delete", primary = false, enabled = !working) {
                    if (!confirmDelete) confirmDelete = true else ModuleStore.deleteSaved(context, built.request)
                }
            }
        }
    }
}

/** The user's GitHub token: checked against the repository's builds, then kept in the app. */
@Composable
private fun TokenDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var token by remember { mutableStateOf("") }
    var checking by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(14.dp).widthIn(max = 560.dp).fillMaxWidth()
                .drawBehind {
                    drawRect(Brush.verticalGradient(listOf(Colors.Night, Colors.Deep)))
                    drawFrame()
                }
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            FrameTitle("GitHub token")
            Line(
                "On github.com: Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token. " +
                    "Repository access: only ${ModuleSource.REPO}. Permissions: Actions, read and write; and Contents, read (to download the built realm if the repository is private). " +
                    "Paste it here: it's checked with GitHub, then kept in this app's own storage and sent to GitHub alone.",
                color = Colors.Mist, small = true,
            )
            OutlinedTextField(
                value = token,
                onValueChange = { token = it },
                label = { Text("Token", color = Colors.Mist) },
                singleLine = true,
                visualTransformation = PasswordVisualTransformation(),
                textStyle = MaterialTheme.typography.bodyLarge,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, autoCorrectEnabled = false),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = Colors.Text, unfocusedTextColor = Colors.Text,
                    focusedBorderColor = Colors.Ice, unfocusedBorderColor = Colors.Steel, cursorColor = Colors.Ice,
                    focusedContainerColor = Colors.Abyss.copy(alpha = 0.55f), unfocusedContainerColor = Colors.Abyss.copy(alpha = 0.55f),
                ),
                modifier = Modifier.fillMaxWidth(),
            )
            error?.let { Line(it, color = Blood, small = true) }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Btn("Cancel", primary = false, modifier = Modifier.weight(1f), onClick = onDismiss)
                Btn(if (checking) "Checking…" else "Check and keep", modifier = Modifier.weight(1f)) {
                    if (token.isBlank() || checking) return@Btn
                    checking = true
                    error = null
                    scope.launch {
                        runCatching { ModuleStore.setToken(context, token) }
                            .onSuccess { onDismiss() }
                            .onFailure {
                                if (it is CancellationException) throw it
                                error = "GitHub didn't take it: ${it.message ?: it.javaClass.simpleName}"
                            }
                        checking = false
                    }
                }
            }
        }
    }
}
