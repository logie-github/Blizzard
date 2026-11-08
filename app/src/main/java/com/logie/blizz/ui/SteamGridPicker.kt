package com.logie.blizz.ui

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.LruCache
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items as rowItems
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.steamgrid.SteamGrid
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * A game's pictures from SteamGridDB, to choose from: the game found by its name (the others its search found as chips to switch to),
 * its pictures of [slot]'s kind in a grid, a tap taking one: it is downloaded and given to [onPicked] as a file. "My files" goes to the
 * phone's own picker instead. Needs the key from Settings ([SteamGrid.key]).
 */
@Composable
fun SteamGridPicker(game: Game, slot: SteamGrid.Slot, slotName: String, onPicked: (File) -> Unit, onMyFiles: () -> Unit, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val key = remember { SteamGrid.key(context) }
    val scope = rememberCoroutineScope()
    var term by remember { mutableStateOf(SteamGrid.searchTerm(game.title, game.subtitle)) }
    var games by remember { mutableStateOf<List<SteamGrid.Game>>(emptyList()) }
    var chosen by remember { mutableStateOf<SteamGrid.Game?>(null) }
    val pictures = remember { mutableStateListOf<SteamGrid.Picture>() }
    var page by remember { mutableStateOf(0) }
    var hasMore by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf<String?>(null) }
    var taking by remember { mutableStateOf<Long?>(null) }

    fun loadPictures(g: SteamGrid.Game, nextPage: Int) {
        scope.launch {
            busy = true; message = null
            runCatching { withContext(Dispatchers.IO) { SteamGrid.pictures(key!!, slot, g.id, nextPage) } }
                .onSuccess { r ->
                    if (nextPage == 0) pictures.clear()
                    pictures += r.pictures; page = nextPage; hasMore = r.hasMore
                    if (pictures.isEmpty()) message = "SteamGridDB has no ${slotName.lowercase()} pictures for ${g.name}."
                }
                .onFailure { message = it.message ?: "Couldn't reach SteamGridDB." }
            busy = false
        }
    }

    fun search(text: String) {
        scope.launch {
            busy = true; message = null
            runCatching { withContext(Dispatchers.IO) { SteamGrid.search(key!!, text) } }
                .onSuccess { found ->
                    games = found.take(8); pictures.clear(); chosen = found.firstOrNull()
                    if (chosen == null) message = "SteamGridDB doesn't know \"$text\". Try another name." else loadPictures(chosen!!, 0)
                }
                .onFailure { message = it.message ?: "Couldn't reach SteamGridDB." }
            busy = false
        }
    }
    LaunchedEffect(Unit) { if (key != null) search(term) }

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Sheet("$slotName · SteamGridDB", onDismiss, maxWidth = 640.dp) {
            Column(Modifier.padding(horizontal = 20.dp).padding(bottom = 16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    OutlinedTextField(
                        value = term, onValueChange = { term = it }, singleLine = true, modifier = Modifier.weight(1f),
                        placeholder = { Text("Game name", color = Colors.Mist) },
                        leadingIcon = { Icon(Icons.Default.Search, null, tint = Colors.Mist) },
                        textStyle = MaterialTheme.typography.bodyLarge,
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search, autoCorrectEnabled = false),
                        keyboardActions = KeyboardActions(onSearch = { search(term) }),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = Colors.Text, unfocusedTextColor = Colors.Text, focusedBorderColor = Colors.Ice, unfocusedBorderColor = Colors.Steel,
                            cursorColor = Colors.Ice, focusedContainerColor = Colors.Abyss.copy(alpha = 0.55f), unfocusedContainerColor = Colors.Abyss.copy(alpha = 0.55f),
                        ),
                    )
                    FrameButton("My files", primary = false) { onDismiss(); onMyFiles() }
                }
                if (games.size > 1) LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    rowItems(games, key = { it.id }) { g ->
                        val on = g.id == chosen?.id
                        Text(
                            g.name, style = MaterialTheme.typography.bodyMedium.copy(color = if (on) Color.White else Colors.Mist), maxLines = 1,
                            modifier = Modifier.clip(RoundedCornerShape(50)).background(if (on) Modern.Accent else Color.White.copy(alpha = 0.07f))
                                .clickable { chosen = g; loadPictures(g, 0) }.padding(horizontal = 14.dp, vertical = 8.dp),
                        )
                    }
                }
                message?.let { Text(it, style = MaterialTheme.typography.bodyMedium, color = Modern.Warn) }
                if (busy && pictures.isEmpty()) Text("Looking…", style = MaterialTheme.typography.bodySmall)
                val portrait = slot == SteamGrid.Slot.BOX
                LazyVerticalGrid(
                    columns = GridCells.Fixed(if (portrait) 3 else 2), modifier = Modifier.fillMaxWidth().heightIn(max = 520.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    items(pictures, key = { it.id }) { pic ->
                        Box(
                            Modifier.fillMaxWidth().aspectRatio(if (portrait) 2f / 3f else if (slot == SteamGrid.Slot.LOGO) 1.6f else 3.1f / 1f)
                                .clip(RoundedCornerShape(12.dp)).background(if (slot == SteamGrid.Slot.LOGO) Color.Black.copy(alpha = 0.55f) else Color.White.copy(alpha = 0.05f))
                                .border(1.dp, if (taking == pic.id) Colors.Ice else Colors.Steel.copy(alpha = 0.7f), RoundedCornerShape(12.dp))
                                .clickable(enabled = taking == null) {
                                    taking = pic.id; message = null
                                    scope.launch {
                                        val dest = File(context.cacheDir, "steamgrid/${pic.id}-${slot.name.lowercase()}.img")
                                        runCatching { withContext(Dispatchers.IO) { SteamGrid.download(pic.url, dest) } }
                                            .onSuccess { onPicked(dest); onDismiss() }
                                            .onFailure { message = it.message ?: "Couldn't download that picture."; taking = null }
                                    }
                                },
                            contentAlignment = Alignment.Center,
                        ) {
                            RemoteThumb(pic.thumb, Modifier.fillMaxSize(), if (slot == SteamGrid.Slot.LOGO) ContentScale.Fit else ContentScale.Crop)
                            if (taking == pic.id) Text("Downloading…", style = MaterialTheme.typography.bodySmall.copy(color = Color.White), modifier = Modifier.background(Color.Black.copy(alpha = 0.6f)).padding(6.dp))
                        }
                    }
                    if (hasMore) item(span = { GridItemSpan(maxLineSpan) }) {
                        FrameButton(if (busy) "Looking…" else "More", primary = false, modifier = Modifier.fillMaxWidth()) { chosen?.let { if (!busy) loadPictures(it, page + 1) } }
                    }
                }
                Text("Pictures by the SteamGridDB community.", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

private val thumbs = object : LruCache<String, Bitmap>(24 * 1024 * 1024) {
    override fun sizeOf(key: String, value: Bitmap) = value.byteCount
}

/** A picture from SteamGridDB's own address, loaded once and kept for the session (no image library in the app). */
@Composable
private fun RemoteThumb(url: String, modifier: Modifier, scale: ContentScale) {
    val bitmap by produceState<Bitmap?>(thumbs.get(url), url) {
        if (value == null && SteamGrid.isSiteUrl(url)) value = withContext(Dispatchers.IO) {
            runCatching {
                val c = java.net.URL(url).openConnection() as java.net.HttpURLConnection
                c.connectTimeout = 15_000; c.readTimeout = 30_000
                try { c.inputStream.use { BitmapFactory.decodeStream(it) } } finally { c.disconnect() }
            }.getOrNull()?.also { thumbs.put(url, it) }
        }
    }
    bitmap?.let { Image(it.asImageBitmap(), null, modifier, contentScale = scale) } ?: Spacer(modifier)
}
