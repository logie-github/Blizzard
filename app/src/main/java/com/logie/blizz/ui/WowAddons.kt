@file:OptIn(ExperimentalLayoutApi::class)

// The World of Warcraft app's add-on manager (YeaBwoi, warcraft/.../ui/WowAddons.kt), restyled in Blizzard's blue.
package com.logie.blizz.ui

import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.LruCache
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyGridState
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Extension
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.BuildConfig
import com.logie.blizz.wowaddons.AddonRecords
import com.logie.blizz.wowaddons.AddonStoreOf
import com.logie.blizz.wowaddons.Addons
import com.logie.blizz.wowaddons.Warperia
import com.logie.blizz.wowaddons.WowAddonGames
import com.logie.blizz.wowaddons.WowAddonStores
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * The add-on manager for one of the World of Warcraft clients ([gameId]: "wow" Wrath+, "wow_legion"
 * Legion, "wow_octowow" OctoWoW), over the launcher. Browse: warperia.com's add-ons for that client, searched,
 * by category and order, each installed in one tap or opened for its page. Installed: what's in
 * the client, from the site or from zips, with updates, on and off, and delete.
 */
@Composable
fun WowAddonManager(gameId: String, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val game = remember(gameId) { WowAddonGames.of(gameId) }
    val store = remember(gameId) { WowAddonStores.of(gameId) }
    if (game == null || store == null) {
        LaunchedEffect(gameId) { onDismiss() }
        return
    }
    val hasClient by produceState<Boolean?>(null, gameId) {
        value = withContext(Dispatchers.IO) { runCatching { game.hasClient(context) }.getOrDefault(false) }
    }
    var tab by rememberSaveable { mutableStateOf(AddonTab.BROWSE) }
    var open by rememberSaveable { mutableStateOf<String?>(null) }
    var picture by remember { mutableStateOf<String?>(null) }
    var importing by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val browse = remember(gameId) { AddonBrowseState(store) }
    val jobs by store.jobs.collectAsState()
    val installed by store.installed.collectAsState()
    val updates by store.updates.collectAsState()
    val shelf = AddonShelf(store, jobs, installed, updates)

    val pick = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri == null) return@rememberLauncherForActivityResult
        importing = true
        scope.launch {
            val result = runCatching { store.importZip(context, uri) }
            importing = false
            val message = result.fold(
                onSuccess = { "Installed: ${it.joinToString(", ")}" },
                onFailure = {
                    if (it is Addons.NoAddonException) NO_ADDON_IN_ZIP
                    else "Couldn't install it: ${it.message ?: it.javaClass.simpleName}"
                },
            )
            Toast.makeText(context, message, Toast.LENGTH_LONG).show()
        }
    }

    LaunchedEffect(gameId, hasClient) {
        if (hasClient == true) {
            store.refresh(context)
            store.checkUpdates(context, force = false)
        }
    }
    LaunchedEffect(gameId) {
        store.messages.collect { Toast.makeText(context, it, Toast.LENGTH_LONG).show() }
    }
    val back: () -> Unit = {
        when {
            picture != null -> picture = null
            open != null -> open = null
            else -> onDismiss()
        }
    }
    val label = when (gameId) {
        WowAddonGames.LEGION.libraryId -> "Legion"
        WowAddonGames.OCTOWOW.libraryId -> "OctoWoW"
        else -> "Wrath+"
    }
    val version = when (game.flavor) {
        Warperia.Flavor.WOTLK -> "3.3.5a"
        Warperia.Flavor.LEGION -> "Legion 7.3.5"
        Warperia.Flavor.VANILLA -> "1.12"
    }

    Dialog(onDismissRequest = { back() }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Box(Modifier.fillMaxSize().padding(14.dp), contentAlignment = Alignment.Center) {
            Column(
                Modifier
                    .widthIn(max = 920.dp)
                    .fillMaxSize()
                    .drawBehind {
                        drawRect(Brush.verticalGradient(listOf(Colors.Night, Colors.Deep)))
                        drawFrame()
                    },
            ) {
                val slug = open
                if (slug != null) {
                    AddonDetailsPane(store, slug, shelf, onBack = { open = null }, onPicture = { picture = it })
                } else {
                    Row(
                        Modifier.fillMaxWidth().padding(start = 20.dp, end = 8.dp, top = 14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        FrameTitle("Add-ons · $label", Modifier.weight(1f), style = MaterialTheme.typography.titleLarge)
                        AddonCloseIcon(onDismiss)
                    }
                    Box(Modifier.padding(horizontal = 18.dp, vertical = 10.dp)) {
                        Segmented(
                            listOf(
                                "Browse" to AddonTab.BROWSE,
                                "Installed" + (if (installed.isNotEmpty()) " (${installed.size})" else "") +
                                    (if (updates.isNotEmpty()) " ↑${updates.size}" else "") to AddonTab.INSTALLED,
                            ),
                            tab,
                        ) { tab = it }
                    }
                    Box(Modifier.fillMaxWidth().height(1.dp).background(Colors.Steel.copy(alpha = 0.6f)))
                    when {
                        hasClient == null -> Box(Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) { AddonSpinner(36.dp) }
                        hasClient == false -> Text(
                            game.noClientMessage(context),
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.padding(20.dp),
                        )
                        tab == AddonTab.BROWSE -> AddonBrowsePane(browse, shelf, version, Modifier.weight(1f), onOpen = { open = it })
                        else -> AddonInstalledPane(
                            shelf, importing, Modifier.weight(1f),
                            onImport = { pick.launch(arrayOf("application/zip", "application/x-zip-compressed", "application/octet-stream")) },
                            onOpen = { open = it },
                        )
                    }
                }
            }
            picture?.let { AddonPictureView(it, onClose = { picture = null }) }
        }
    }
}

private const val NO_ADDON_IN_ZIP = "There's no add-on in that zip (no .toc file)."

private enum class AddonTab { BROWSE, INSTALLED }

/** What's installed and what's under way, as one look for the whole screen. */
private class AddonShelf(
    val store: AddonStoreOf,
    val jobs: Map<String, AddonStoreOf.Job>,
    val installed: List<AddonStoreOf.Installed>,
    val updates: Map<String, Warperia.Details>,
) {
    fun installed(slug: String) = installed.firstOrNull { it.record?.slug == slug }

    /** Where the site's add-on [slug] stands; [updated] is the list's date for it, when known. */
    fun status(slug: String, updated: String? = null): AddonStatus {
        jobs[slug]?.let { job -> return if (job is AddonStoreOf.Job.Failed) AddonStatus.Failed else AddonStatus.Busy(job) }
        val record = installed(slug)?.record ?: return AddonStatus.New
        val newer = slug in updates || AddonRecords.isOutdated(record, null, updated)
        return if (newer) AddonStatus.Outdated else AddonStatus.Current
    }
}

private sealed interface AddonStatus {
    data object New : AddonStatus
    data object Current : AddonStatus
    data object Outdated : AddonStatus
    data object Failed : AddonStatus
    data class Busy(val job: AddonStoreOf.Job) : AddonStatus
}

// Small parts -------------------------------------------------------------------------------------

private val CardShape = RoundedCornerShape(4.dp)

@Composable
private fun AddonCloseIcon(onClose: () -> Unit) {
    Icon(
        Icons.Default.Close, "Close", tint = Colors.Mist,
        modifier = Modifier.clip(CircleShape).clickable(onClick = onClose).padding(12.dp).size(24.dp),
    )
}

@Composable
private fun AddonSpinner(size: Dp) {
    CircularProgressIndicator(
        modifier = Modifier.size(size),
        color = Colors.Ice,
        trackColor = Colors.Frost,
        strokeWidth = (size.value / 9f).coerceIn(2f, 4f).dp,
    )
}

/** A press shrinks the part a little and lights it; a part with no [onClick] is left as it is. */
@Composable
private fun Modifier.addonPress(onClick: (() -> Unit)?): Modifier {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val lit by animateFloatAsState(if (pressed) 1f else 0f, spring(dampingRatio = 0.7f, stiffness = 900f), label = "press")
    if (onClick == null) return this
    return this
        .graphicsLayer { val k = 1f - 0.02f * lit; scaleX = k; scaleY = k }
        .drawWithContent {
            drawContent()
            drawRect(Colors.Ice.copy(alpha = 0.10f * lit))
        }
        .clickable(interactionSource = interaction, indication = null, onClick = onClick)
}

/** A hairline-framed card, its corners soft; it grows and shrinks with what's in it. */
@Composable
private fun AddonPanel(modifier: Modifier = Modifier, onClick: (() -> Unit)? = null, content: @Composable ColumnScope.() -> Unit) {
    Column(
        modifier
            .fillMaxWidth()
            .animateContentSize()
            .addonPress(onClick)
            .clip(CardShape)
            .background(Colors.Abyss.copy(alpha = 0.55f))
            .border(1.dp, Colors.Steel.copy(alpha = 0.7f), CardShape)
            .padding(12.dp),
        content = content,
    )
}

/** A choice in a row of them: the chosen one lit. */
@Composable
private fun AddonChip(text: String, selected: Boolean, onClick: () -> Unit) {
    val fill by androidx.compose.animation.animateColorAsState(if (selected) Colors.Frost else Colors.Night.copy(alpha = 0.6f), label = "chip")
    Box(
        Modifier
            .heightIn(min = 36.dp)
            .addonPress(onClick)
            .clip(CardShape)
            .background(fill)
            .border(1.dp, if (selected) Colors.Ice.copy(alpha = 0.8f) else Colors.Steel.copy(alpha = 0.8f), CardShape)
            .padding(horizontal = 14.dp, vertical = 8.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, style = MaterialTheme.typography.labelLarge.copy(color = if (selected) Colors.Glow else Colors.Mist), maxLines = 1)
    }
}

@Composable
private fun AddonSection(text: String, modifier: Modifier = Modifier) {
    FrameTitle(text, modifier, style = DisplayStyle.copy(fontSize = 13.sp, color = Colors.Gold, letterSpacing = 0.18.sp))
}

/** A fact and its value, one line. */
@Composable
private fun AddonFact(label: String, value: String, good: Boolean = false) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(label, style = MaterialTheme.typography.bodySmall, modifier = Modifier.widthIn(min = 96.dp))
        Text(value, style = MaterialTheme.typography.bodyMedium.copy(color = if (good) Colors.Ice else Colors.Text), modifier = Modifier.weight(1f))
    }
}

// Pictures from the web ---------------------------------------------------------------------------

/** Pictures from the web (add-on logos and screenshots): kept in memory and in the app's cache. */
private object AddonImages {
    private val memory = object : LruCache<String, ImageBitmap>(32 * 1024 * 1024) {
        override fun sizeOf(key: String, value: ImageBitmap) = value.width * value.height * 4
    }
    /** A few at a time is plenty for a page of logos. */
    private val fetching = Semaphore(4)

    /** The picture at [url], no bigger than [maxPx] on its longer side; null when it can't be had. */
    suspend fun load(context: Context, url: String, maxPx: Int): ImageBitmap? {
        val key = "$maxPx $url"
        memory.get(key)?.let { return it }
        return withContext(Dispatchers.IO) {
            runCatching {
                val file = cached(context, url)
                val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
                BitmapFactory.decodeFile(file.path, bounds)
                var sample = 1
                while (maxOf(bounds.outWidth, bounds.outHeight) / (sample * 2) >= maxPx) sample *= 2
                val bitmap = BitmapFactory.decodeFile(file.path, BitmapFactory.Options().apply { inSampleSize = sample })
                    ?: return@runCatching null
                bitmap.asImageBitmap().also { memory.put(key, it) }
            }.getOrNull()
        }
    }

    private suspend fun cached(context: Context, url: String): File {
        val dir = File(context.cacheDir, "wowaddons-images")
        val file = File(dir, sha1(url))
        if (file.isFile) return file
        fetching.withPermit {
            if (file.isFile) return file
            dir.mkdirs()
            val connection = (URL(url).openConnection() as HttpURLConnection).apply {
                connectTimeout = 15_000
                readTimeout = 30_000
                setRequestProperty("User-Agent", "Blizzard/${BuildConfig.VERSION_NAME} (com.logie.blizz)")
            }
            try {
                if (connection.responseCode !in 200..299) throw java.io.IOException("HTTP ${connection.responseCode}")
                val part = File(dir, file.name + "." + System.nanoTime() + ".part")
                connection.inputStream.use { input -> part.outputStream().use { input.copyTo(it) } }
                part.renameTo(file)
            } finally {
                connection.disconnect()
            }
            trim(dir)
        }
        return file
    }

    /** The cache stays under about 60 MB: the oldest pictures go first. */
    private fun trim(dir: File) {
        val files = dir.listFiles().orEmpty().sortedBy { it.lastModified() }
        var total = files.sumOf { it.length() }
        for (file in files) {
            if (total < 60L * 1024 * 1024) break
            total -= file.length()
            file.delete()
        }
    }

    private fun sha1(text: String) =
        MessageDigest.getInstance("SHA-1").digest(text.toByteArray()).joinToString("") { "%02x".format(it) }
}

/** A picture from the web, with [placeholder] until it's there (and if it never is). */
@Composable
private fun AddonImage(
    url: String?,
    modifier: Modifier = Modifier,
    maxPx: Int = 256,
    contentScale: ContentScale = ContentScale.Crop,
    placeholder: @Composable () -> Unit = { Box(Modifier.fillMaxSize().background(Colors.Deep)) },
) {
    val context = LocalContext.current
    val image by produceState<ImageBitmap?>(null, url, maxPx) {
        value = url?.let { AddonImages.load(context, it, maxPx) }
    }
    Box(modifier, contentAlignment = Alignment.Center) {
        val shown = image
        if (shown != null) {
            Image(shown, contentDescription = null, contentScale = contentScale, modifier = Modifier.matchParentSize())
        } else {
            Box(Modifier.matchParentSize()) { placeholder() }
        }
    }
}

@Composable
private fun AddonLogo(url: String?, size: Dp) {
    val shape = RoundedCornerShape(6.dp)
    AddonImage(
        url,
        Modifier.size(size).clip(shape).border(1.dp, Colors.Steel.copy(alpha = 0.7f), shape),
        placeholder = {
            Box(Modifier.fillMaxSize().background(Colors.Deep), contentAlignment = Alignment.Center) {
                Icon(Icons.Default.Extension, contentDescription = null, tint = Colors.Steel, modifier = Modifier.size(size * 0.5f))
            }
        },
    )
}

/** A screenshot over everything, as big as the screen allows; a tap closes it. */
@Composable
private fun AddonPictureView(url: String, onClose: () -> Unit) {
    Box(
        Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.94f))
            .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null, onClick = onClose),
        contentAlignment = Alignment.Center,
    ) {
        AddonImage(
            url,
            Modifier.fillMaxSize().padding(12.dp),
            maxPx = 2048,
            contentScale = ContentScale.Fit,
            placeholder = { Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { AddonSpinner(44.dp) } },
        )
    }
}

// Install, Update, or how the install is going ------------------------------------------------------

@Composable
private fun AddonInstallButton(status: AddonStatus, onInstall: () -> Unit) {
    val width = Modifier.widthIn(min = 120.dp)
    when (status) {
        AddonStatus.New -> FrameButton("Install", width, onClick = onInstall)
        AddonStatus.Outdated -> FrameButton("Update", width, onClick = onInstall)
        AddonStatus.Failed -> FrameButton("Try again", width, onClick = onInstall)
        AddonStatus.Current -> Box(
            width.heightIn(min = 48.dp).drawBehind { drawFrame(corner = Colors.Steel, alpha = 0.5f, arm = 7.dp.toPx()) }.padding(horizontal = 16.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text("INSTALLED", style = DisplayStyle.copy(fontSize = 13.sp, color = Colors.Mist, letterSpacing = 0.18.sp), maxLines = 1)
        }
        is AddonStatus.Busy -> Row(
            width
                .heightIn(min = 48.dp)
                .drawBehind { drawFrame(corner = Colors.Mist, alpha = 0.7f, arm = 7.dp.toPx()) }
                .padding(horizontal = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
        ) {
            AddonSpinner(20.dp)
            Spacer(Modifier.width(8.dp))
            val job = status.job
            Text(
                when (job) {
                    AddonStoreOf.Job.Queued -> "Queued"
                    is AddonStoreOf.Job.Waiting -> "Starts in ${job.secondsLeft}"
                    is AddonStoreOf.Job.Downloading -> job.fraction?.let { "${(it * 100).toInt()}%" } ?: "Downloading"
                    AddonStoreOf.Job.Installing -> "Installing…"
                    is AddonStoreOf.Job.Failed -> ""
                },
                style = MaterialTheme.typography.bodySmall.copy(color = Colors.Text),
                maxLines = 1,
            )
        }
    }
}

// Browse ------------------------------------------------------------------------------------------

/** The list as far as it's been read, for what's searched; more pages as the list scrolls. */
@Stable
private class AddonBrowseState(val store: AddonStoreOf) {
    var search by mutableStateOf("")
    var query by mutableStateOf(Warperia.Query())
        private set
    val items = mutableStateListOf<Warperia.Listing>()
    var categories by mutableStateOf<List<Warperia.Category>>(emptyList())
    var page by mutableIntStateOf(0)
    var pages by mutableIntStateOf(1)
    var loading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    val grid = LazyGridState()
    /** Changes with the query: an answer to an older one is dropped. */
    private var generation = 0

    val hasMore get() = page == 0 || page < pages

    fun change(query: Warperia.Query) {
        if (query == this.query) return
        generation++
        this.query = query
        items.clear()
        page = 0
        pages = 1
        loading = false
        error = null
    }

    suspend fun loadMore() {
        if (loading || !hasMore) return
        val asked = generation
        loading = true
        error = null
        try {
            val result = store.list(query, page + 1)
            if (asked != generation) return
            if (categories.isEmpty()) categories = result.categories
            // Pages can shift while they're read (an add-on updated): none twice.
            val seen = items.mapTo(HashSet()) { it.slug }
            items += result.items.filter { seen.add(it.slug) }
            page += 1
            pages = if (result.items.isEmpty()) page else result.pages
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
private fun AddonBrowsePane(state: AddonBrowseState, shelf: AddonShelf, version: String, modifier: Modifier, onOpen: (String) -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val focus = LocalFocusManager.current

    // What's typed is searched once the typing stops.
    LaunchedEffect(state.search) {
        delay(700)
        state.change(state.query.copy(search = state.search.trim()))
    }
    LaunchedEffect(state.query) {
        if (state.page == 0) {
            state.grid.scrollToItem(0)
            state.loadMore()
        }
    }
    // The next page when the list nears its end.
    LaunchedEffect(state) {
        snapshotFlow {
            val info = state.grid.layoutInfo
            val near = (info.visibleItemsInfo.lastOrNull()?.index ?: 0) >= info.totalItemsCount - 6
            Triple(near, state.items.size, state.error)
        }.collect { (near, _, error) ->
            if (near && error == null && state.page > 0) state.loadMore()
        }
    }

    Column(modifier.fillMaxWidth()) {
        OutlinedTextField(
            value = state.search,
            onValueChange = { state.search = it },
            placeholder = { Text("Search $version add-ons", style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist)) },
            leadingIcon = { Icon(Icons.Default.Search, contentDescription = null, tint = Colors.Mist) },
            trailingIcon = {
                if (state.search.isNotEmpty()) {
                    IconButton2 { state.search = ""; state.change(state.query.copy(search = "")) }
                }
            },
            singleLine = true,
            shape = CardShape,
            textStyle = MaterialTheme.typography.bodyLarge,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search, autoCorrectEnabled = false),
            keyboardActions = KeyboardActions(onSearch = {
                state.change(state.query.copy(search = state.search.trim()))
                focus.clearFocus()
            }),
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Colors.Text,
                unfocusedTextColor = Colors.Text,
                focusedBorderColor = Colors.Ice,
                unfocusedBorderColor = Colors.Steel,
                cursorColor = Colors.Ice,
                focusedContainerColor = Colors.Night.copy(alpha = 0.7f),
                unfocusedContainerColor = Colors.Night.copy(alpha = 0.7f),
            ),
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
        )
        Box(Modifier.padding(horizontal = 16.dp, vertical = 2.dp)) {
            Segmented(
                listOf(
                    "Popular" to Warperia.Order.POPULAR,
                    "New" to Warperia.Order.NEW,
                    "Updated" to Warperia.Order.UPDATED,
                ),
                state.query.order,
            ) { state.change(state.query.copy(order = it)) }
        }
        if (state.categories.isNotEmpty()) {
            Row(
                Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()).padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                AddonChip("All", state.query.category == null) { state.change(state.query.copy(category = null)) }
                for (category in state.categories) {
                    AddonChip(category.name, state.query.category == category.slug) {
                        state.change(state.query.copy(category = category.slug))
                    }
                }
            }
        }
        LazyVerticalGrid(
            columns = GridCells.Adaptive(minSize = 340.dp),
            state = state.grid,
            contentPadding = PaddingValues(16.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.weight(1f).fillMaxWidth(),
        ) {
            items(state.items, key = { it.slug }) { listing ->
                AddonCard(
                    listing,
                    shelf.status(listing.slug, listing.updated),
                    onOpen = { onOpen(listing.slug) },
                    onInstall = { shelf.store.install(context, listing.slug) },
                )
            }
            item(span = { GridItemSpan(maxLineSpan) }) {
                Column(
                    Modifier.fillMaxWidth().padding(vertical = 12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    val error = state.error
                    when {
                        state.loading -> AddonSpinner(36.dp)
                        error != null -> {
                            Text("Couldn't reach warperia.com: $error", style = MaterialTheme.typography.bodyMedium)
                            FrameButton("Try again", primary = false) { scope.launch { state.loadMore() } }
                        }
                        state.items.isEmpty() && !state.hasMore ->
                            Text("No add-ons found.", style = MaterialTheme.typography.bodyMedium)
                    }
                    Text(
                        "Add-ons from warperia.com. An install waits the few seconds the site asks of free downloads, then goes into your client by itself.",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }
    }
}

/** The search field's clear button. */
@Composable
private fun IconButton2(onClick: () -> Unit) {
    Icon(
        Icons.Default.Close, "Clear the search", tint = Colors.Mist,
        modifier = Modifier.clip(CircleShape).clickable(onClick = onClick).padding(10.dp).size(22.dp),
    )
}

@Composable
private fun AddonCard(listing: Warperia.Listing, status: AddonStatus, onOpen: () -> Unit, onInstall: () -> Unit) {
    AddonPanel(onClick = onOpen) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            AddonLogo(listing.logo, 60.dp)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(listing.title, style = MaterialTheme.typography.titleMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                listing.author?.let {
                    Text("by $it", style = MaterialTheme.typography.bodySmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
                listing.summary?.let {
                    Text(it, style = MaterialTheme.typography.bodySmall.copy(color = Colors.Text.copy(alpha = 0.85f)), maxLines = 2, overflow = TextOverflow.Ellipsis)
                }
                val meta = listOfNotNull(
                    listing.downloads?.let { "$it downloads" },
                    listing.updated?.let { Warperia.showDay(it) },
                    listing.categories.firstOrNull(),
                ).joinToString(" · ")
                if (meta.isNotEmpty()) {
                    Text(meta, style = MaterialTheme.typography.bodySmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
            }
            Spacer(Modifier.width(10.dp))
            AddonInstallButton(status, onInstall)
        }
    }
}

// An add-on's page --------------------------------------------------------------------------------

@Composable
private fun AddonDetailsPane(store: AddonStoreOf, slug: String, shelf: AddonShelf, onBack: () -> Unit, onPicture: (String) -> Unit) {
    var attempt by remember { mutableIntStateOf(0) }
    val result by produceState<Result<Warperia.Details>?>(null, slug, attempt) {
        value = null
        value = try {
            Result.success(store.details(slug))
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    Row(Modifier.fillMaxWidth().padding(start = 6.dp, end = 12.dp, top = 8.dp), verticalAlignment = Alignment.CenterVertically) {
        Icon(
            Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = Colors.Mist,
            modifier = Modifier.clip(CircleShape).clickable(onClick = onBack).padding(12.dp).size(24.dp),
        )
        FrameTitle(
            result?.getOrNull()?.title ?: "",
            Modifier.weight(1f),
            style = DisplayStyle.copy(fontSize = 15.sp, color = Colors.Gold, letterSpacing = 0.08.sp),
        )
    }
    Box(Modifier.fillMaxWidth().height(1.dp).background(Colors.Steel.copy(alpha = 0.6f)))
    val current = result
    when {
        current == null -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { AddonSpinner(44.dp) }
        current.isFailure -> Column(Modifier.fillMaxSize().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            val error = current.exceptionOrNull()
            Text(
                "Couldn't open this add-on: ${error?.message ?: error?.javaClass?.simpleName.orEmpty()}",
                style = MaterialTheme.typography.bodyMedium,
            )
            FrameButton("Try again", primary = false) { attempt++ }
        }
        else -> AddonDetailsBody(current.getOrThrow(), shelf, onPicture)
    }
}

@Composable
private fun AddonDetailsBody(details: Warperia.Details, shelf: AddonShelf, onPicture: (String) -> Unit) {
    val context = LocalContext.current
    val store = shelf.store
    val installed = shelf.installed(details.slug)
    val status = shelf.status(details.slug, details.updated).let {
        // The page's own version and date against what's installed.
        val record = installed?.record
        if (it == AddonStatus.Current && record != null && AddonRecords.isOutdated(record, details.version, details.updated)) AddonStatus.Outdated else it
    }
    var confirmDelete by remember(details.slug) { mutableStateOf(false) }
    var allChanges by remember(details.slug) { mutableStateOf(false) }

    LazyColumn(
        Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 20.dp, end = 20.dp, top = 14.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        val column = Modifier.widthIn(max = 860.dp).fillMaxWidth()
        item {
            Row(column, verticalAlignment = Alignment.CenterVertically) {
                AddonLogo(details.logo, 88.dp)
                Spacer(Modifier.width(16.dp))
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(details.title, style = MaterialTheme.typography.headlineSmall.copy(color = Colors.Glow))
                    if (details.developers.isNotEmpty()) {
                        Text("by ${details.developers.joinToString(", ")}", style = MaterialTheme.typography.bodySmall)
                    }
                    details.summary?.let { Text(it, style = MaterialTheme.typography.bodyMedium) }
                }
            }
        }
        item {
            FlowRow(
                column.padding(vertical = 6.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                AddonInstallButton(status) { store.install(context, details.slug) }
                if (installed != null) {
                    FrameButton(if (installed.on) "Turn off" else "Turn on", primary = false) {
                        store.setOn(context, installed, !installed.on)
                    }
                    FrameButton(if (confirmDelete) "Delete for good" else "Delete", primary = false) {
                        if (!confirmDelete) {
                            confirmDelete = true
                        } else {
                            store.delete(context, installed)
                            confirmDelete = false
                        }
                    }
                }
                FrameButton("Website", primary = false) {
                    runCatching {
                        context.startActivity(
                            Intent(Intent.ACTION_VIEW, Uri.parse(Warperia.pageUrl(details.slug, store.game.flavor)))
                                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
                        )
                    }
                }
            }
        }
        item {
            AddonPanel(column) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    details.version?.let { AddonFact("Version", it) }
                    installed?.version?.let { AddonFact("Installed", it, good = status == AddonStatus.Current) }
                    details.updated?.let { AddonFact("Last updated", Warperia.showDay(it)) }
                    details.uploaded?.let { AddonFact("First uploaded", Warperia.showDay(it)) }
                    details.downloads?.let { AddonFact("Downloads", it) }
                    if (details.categories.isNotEmpty()) AddonFact("Categories", details.categories.joinToString(", "))
                }
            }
        }
        if (details.screenshots.isNotEmpty()) {
            item { AddonSection("Pictures", column.padding(top = 8.dp)) }
            item {
                LazyRow(column, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    items(details.screenshots) { url ->
                        AddonImage(
                            url,
                            Modifier
                                .height(170.dp)
                                .aspectRatio(16f / 10f)
                                .clip(CardShape)
                                .border(1.dp, Colors.Steel.copy(alpha = 0.7f), CardShape)
                                .clickable { onPicture(url) },
                            maxPx = 720,
                            placeholder = {
                                Box(Modifier.fillMaxSize().background(Colors.Deep), contentAlignment = Alignment.Center) { AddonSpinner(28.dp) }
                            },
                        )
                    }
                }
            }
        }
        if (details.description.isNotEmpty()) {
            item { AddonSection("About", column.padding(top = 8.dp)) }
            items(details.description) { block -> AddonDescriptionBlock(block, column) }
        }
        if (details.changelog.isNotEmpty()) {
            item { AddonSection("Changes", column.padding(top = 8.dp)) }
            val shown = if (allChanges) details.changelog else details.changelog.take(5)
            items(shown) { change ->
                Column(column) {
                    Text(
                        listOfNotNull(change.version, change.date?.let { Warperia.showDay(it) }).joinToString(" · "),
                        style = MaterialTheme.typography.titleMedium.copy(color = Colors.Glow),
                    )
                    change.notes?.let { Text(it, style = MaterialTheme.typography.bodySmall) }
                }
            }
            if (!allChanges && details.changelog.size > shown.size) {
                item {
                    Box(column) { FrameButton("Show all (${details.changelog.size})", primary = false) { allChanges = true } }
                }
            }
        }
    }
}

@Composable
private fun AddonDescriptionBlock(block: Warperia.Block, modifier: Modifier) {
    when (block) {
        is Warperia.Block.Heading -> Text(block.text, style = MaterialTheme.typography.titleMedium.copy(color = Colors.Gold), modifier = modifier.padding(top = 4.dp))
        is Warperia.Block.Paragraph -> Text(block.text, style = MaterialTheme.typography.bodyMedium, modifier = modifier)
        is Warperia.Block.Item -> Row(modifier) {
            Text(block.number?.let { "$it." } ?: "•", style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Ice), modifier = Modifier.width(24.dp))
            Text(block.text, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.weight(1f))
        }
        is Warperia.Block.Code -> Box(
            modifier
                .clip(CardShape)
                .background(Color.Black.copy(alpha = 0.45f))
                .horizontalScroll(rememberScrollState())
                .padding(10.dp),
        ) {
            Text(block.text, style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 12.sp, lineHeight = 16.sp, color = Colors.Mist))
        }
        Warperia.Block.Rule -> Box(modifier.padding(vertical = 4.dp).height(1.dp).background(Colors.Steel.copy(alpha = 0.6f)))
    }
}

// Installed ---------------------------------------------------------------------------------------

@Composable
private fun AddonInstalledPane(shelf: AddonShelf, importing: Boolean, modifier: Modifier, onImport: () -> Unit, onOpen: (String) -> Unit) {
    val context = LocalContext.current
    val store = shelf.store
    val checking by store.checking.collectAsState()

    LazyColumn(
        modifier.fillMaxWidth(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        val column = Modifier.widthIn(max = 860.dp).fillMaxWidth()
        item {
            Column(column, verticalArrangement = Arrangement.spacedBy(10.dp)) {
                FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    if (shelf.updates.isNotEmpty()) {
                        FrameButton("Update all (${shelf.updates.size})") { store.updateAll(context) }
                    }
                    FrameButton(if (checking) "Checking…" else "Check for updates", primary = false) {
                        if (!checking) store.checkUpdates(context, force = true)
                    }
                    FrameButton("Import zip", primary = false) { if (!importing) onImport() }
                }
                Text(
                    "Add-ons load the next time the game starts (or type /reload in the game). A turned-off one stays on the phone without loading.",
                    style = MaterialTheme.typography.bodySmall,
                )
                if (importing) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        AddonSpinner(28.dp)
                        Spacer(Modifier.width(10.dp))
                        Text("Installing…", style = MaterialTheme.typography.bodyMedium)
                    }
                }
                if (shelf.installed.isEmpty() && !importing) {
                    Text("No add-ons yet. Find some in Browse, or import a zip.", style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
        items(shelf.installed, key = { it.key }) { item -> AddonInstalledRow(item, shelf, column, onOpen) }
    }
}

@Composable
private fun AddonInstalledRow(item: AddonStoreOf.Installed, shelf: AddonShelf, modifier: Modifier, onOpen: (String) -> Unit) {
    val context = LocalContext.current
    val store = shelf.store
    var confirmDelete by remember(item.key) { mutableStateOf(false) }
    val record = item.record
    val status = record?.let { shelf.status(it.slug) }
    val newer = record?.let { shelf.updates[it.slug] }
    AddonPanel(modifier, onClick = record?.let { { onOpen(it.slug) } }) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                AddonLogo(record?.logo, 48.dp)
                Spacer(Modifier.width(12.dp))
                Column(Modifier.weight(1f)) {
                    Text(
                        item.title,
                        style = MaterialTheme.typography.titleMedium.copy(color = if (item.on) Colors.Text else Colors.Mist),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                    val line = listOfNotNull(
                        item.version,
                        if (record != null) "from warperia.com" else "from a zip",
                        if (item.on) null else "turned off",
                        if (item.forThisGame || record != null) null else "made for another version of the game",
                    ).joinToString(" · ")
                    Text(line, style = MaterialTheme.typography.bodySmall, maxLines = 2, overflow = TextOverflow.Ellipsis)
                    if (newer != null) {
                        Text(
                            "Update: " + listOfNotNull(newer.version, newer.updated?.let { Warperia.showDay(it) }).joinToString(" · "),
                            style = MaterialTheme.typography.bodySmall.copy(color = Colors.Gold),
                        )
                    }
                }
                Spacer(Modifier.width(8.dp))
                Switch(
                    item.on, { store.setOn(context, item, it) },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Colors.Glow, checkedTrackColor = Colors.Ice.copy(alpha = 0.55f),
                        uncheckedThumbColor = Colors.Mist, uncheckedTrackColor = Colors.Frost, uncheckedBorderColor = Colors.Steel,
                    ),
                )
            }
            Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                if (record != null && status != null && status != AddonStatus.Current) {
                    AddonInstallButton(status) { store.install(context, record.slug) }
                }
                FrameButton(if (confirmDelete) "Delete for good" else "Delete", primary = false) {
                    if (!confirmDelete) {
                        confirmDelete = true
                    } else {
                        store.delete(context, item)
                        confirmDelete = false
                    }
                }
            }
        }
    }
}
