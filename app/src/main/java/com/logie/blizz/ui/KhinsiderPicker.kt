package com.logie.blizz.ui

import android.graphics.Bitmap
import android.graphics.BitmapFactory
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
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.music.Khinsider
import com.logie.blizz.music.MusicCatalog
import com.logie.blizz.music.MusicCustom
import com.logie.blizz.music.MusicPreview
import com.logie.blizz.music.MusicStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/** What the picker starts with when it is not to ask khinsider (the tests'): the albums, and optionally an album open with its page. */
class KhinsiderPreset(val albums: List<Khinsider.Album>, val open: Khinsider.Album? = null, val page: Khinsider.AlbumPage? = null)

/**
 * The music picker, on khinsider: Blizzard Entertainment's soundtracks (its publisher page) to choose an album from; an album's songs in
 * a table like khinsider's (number, play, name, length); a ▶ on each to hear it (a small player under the table shows the album art,
 * the song and the album); **Use** makes it the game's music. "My files" goes to the phone's own picker.
 */
@Composable
fun KhinsiderPicker(game: Game, onMyFiles: () -> Unit, onDismiss: () -> Unit, preset: KhinsiderPreset? = null) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var albums by remember { mutableStateOf<List<Khinsider.Album>?>(preset?.albums) }
    var error by remember { mutableStateOf<String?>(null) }
    var filter by remember { mutableStateOf("") }
    var open by remember { mutableStateOf<Khinsider.Album?>(preset?.open) }
    var page by remember { mutableStateOf<Khinsider.AlbumPage?>(preset?.page) }
    var loading by remember { mutableStateOf(false) }
    var taking by remember { mutableStateOf<String?>(null) }
    val preview by MusicPreview.state.collectAsState()
    androidx.compose.runtime.remember { Khinsider.attach(context) }

    // A page the app couldn't read goes to the developer (once a day): what it said, to fit the reading to the real page.
    fun reportUnreadable(e: Throwable) {
        if (e is Khinsider.Unreadable) com.logie.blizz.reports.BugReports.report(context, "khinsider picker", e.message ?: "unreadable page", listOf("Page" to e.url), log = e.html.take(7000))
    }
    fun loadAlbums() {
        scope.launch {
            loading = true; error = null
            runCatching { Khinsider.albums() }
                .onSuccess { albums = it }
                .onFailure { error = it.message ?: "Couldn't reach khinsider."; reportUnreadable(it) }
            loading = false
        }
    }
    fun openAlbum(a: Khinsider.Album) {
        open = a; page = null
        scope.launch {
            loading = true; error = null
            runCatching { Khinsider.album(a) }
                .onSuccess { page = it }
                .onFailure { error = it.message ?: "Couldn't reach khinsider."; reportUnreadable(it) }
            loading = false
        }
    }
    fun use(song: Khinsider.Song, album: String) {
        taking = song.pageUrl; error = null
        scope.launch {
            runCatching {
                // The song's file address from its page (read as a browser if need be), then the file itself.
                val audio = Khinsider.audioUrl(song.pageUrl)
                withContext(Dispatchers.IO) {
                    val dir = File(context.cacheDir, "khinsider").also { it.mkdirs(); it.listFiles()?.forEach { f -> f.delete() } }
                    val file = MusicStore(dir).download(MusicCatalog.Track("pick", song.title, audio))
                    check(MusicCustom.setFile(context, game.id, file, "${song.title} · $album")) { "That wasn't an audio file." }
                }
            }.onSuccess { MusicPreview.stop(); onDismiss() }
                .onFailure { error = it.message ?: "Couldn't download that song."; taking = null }
        }
    }
    LaunchedEffect(Unit) { if (preset == null) loadAlbums() }
    DisposableEffect(Unit) { onDispose { MusicPreview.stop() } }

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Sheet("${game.title} · Music", onDismiss, maxWidth = 680.dp, subtitle = "khinsider · Blizzard Entertainment") {
            Column(Modifier.padding(horizontal = 20.dp).padding(bottom = 16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                if (open == null) {
                    OutlinedTextField(
                        value = filter, onValueChange = { filter = it }, singleLine = true, modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("Find an album", color = Colors.Mist) }, leadingIcon = { Icon(Icons.Default.Search, null, tint = Colors.Mist) },
                        textStyle = MaterialTheme.typography.bodyLarge,
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search, autoCorrectEnabled = false),
                        colors = fieldColors(),
                    )
                    error?.let { Notice(it) { loadAlbums() } }
                    if (loading && albums == null) Text("Looking…", style = MaterialTheme.typography.bodySmall)
                    val shown = albums.orEmpty().filter { filter.isBlank() || it.title.contains(filter.trim(), ignoreCase = true) }
                    LazyColumn(Modifier.fillMaxWidth().heightIn(max = 520.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(shown, key = { it.slug }) { a ->
                            Row(
                                Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(Color.White.copy(alpha = 0.04f)).clickable { openAlbum(a) }.padding(10.dp),
                                verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp),
                            ) {
                                Cover(a.thumb, Modifier.size(52.dp))
                                Text(a.title, style = MaterialTheme.typography.titleMedium, maxLines = 2, overflow = TextOverflow.Ellipsis)
                            }
                        }
                    }
                } else {
                    val album = open!!
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Albums", tint = Colors.Text, modifier = Modifier.clip(CircleShape).clickable { MusicPreview.stop(); open = null; page = null; error = null }.padding(8.dp).size(24.dp))
                        Cover(page?.cover ?: album.thumb, Modifier.size(72.dp))
                        Column(Modifier.weight(1f)) {
                            Text(page?.title ?: album.title, style = MaterialTheme.typography.titleLarge, maxLines = 2, overflow = TextOverflow.Ellipsis)
                            page?.let { Text("${it.songs.size} songs", style = MaterialTheme.typography.bodySmall) }
                        }
                    }
                    error?.let { Notice(it) { openAlbum(album) } }
                    if (loading && page == null) Text("Looking…", style = MaterialTheme.typography.bodySmall)
                    page?.let { p ->
                        // The table, as khinsider has it: number, play, song name, length.
                        Row(Modifier.fillMaxWidth().padding(horizontal = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                            Header("#", Modifier.width(32.dp)); Spacer(Modifier.width(44.dp)); Header("Song name", Modifier.weight(1f)); Header("Length", Modifier.width(56.dp)); Spacer(Modifier.width(58.dp))
                        }
                        Box(Modifier.fillMaxWidth().height(1.dp).background(Color.White.copy(alpha = 0.1f)))
                        LazyColumn(Modifier.fillMaxWidth().heightIn(max = 430.dp)) {
                            items(p.songs, key = { it.pageUrl }) { song ->
                                val on = preview.pageUrl == song.pageUrl
                                Row(
                                    Modifier.fillMaxWidth().background(if (on) Modern.AccentSoft else Color.Transparent).padding(horizontal = 6.dp, vertical = 2.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                ) {
                                    Text("${song.number}", style = MaterialTheme.typography.bodySmall, modifier = Modifier.width(32.dp))
                                    PlayButton(playing = on && preview.playing, loading = on && preview.loading) { MusicPreview.toggle(context, song.pageUrl, song.title, p.title, p.cover ?: album.thumb) }
                                    Text(song.title, style = MaterialTheme.typography.bodyMedium, maxLines = 2, overflow = TextOverflow.Ellipsis, modifier = Modifier.weight(1f).padding(horizontal = 6.dp, vertical = 8.dp))
                                    Text(song.length ?: "", style = MaterialTheme.typography.bodySmall, modifier = Modifier.width(56.dp))
                                    Text(
                                        if (taking == song.pageUrl) "…" else "Use",
                                        style = MaterialTheme.typography.labelLarge.copy(color = Colors.Ice, fontSize = 14.sp),
                                        modifier = Modifier.width(58.dp).clip(RoundedCornerShape(8.dp)).clickable(enabled = taking == null) { use(song, p.title) }.padding(vertical = 10.dp),
                                    )
                                }
                                Box(Modifier.fillMaxWidth().height(1.dp).background(Color.White.copy(alpha = 0.05f)))
                            }
                        }
                    }
                    MiniPlayer(preview)
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Text("Songs from khinsider.com", style = MaterialTheme.typography.bodySmall)
                    Text("My files", style = MaterialTheme.typography.labelLarge.copy(color = Colors.Mist, fontSize = 14.sp), modifier = Modifier.clip(RoundedCornerShape(6.dp)).clickable { MusicPreview.stop(); onDismiss(); onMyFiles() }.padding(8.dp))
                }
            }
        }
    }
}

@Composable
private fun fieldColors() = OutlinedTextFieldDefaults.colors(
    focusedTextColor = Colors.Text, unfocusedTextColor = Colors.Text, focusedBorderColor = Colors.Ice, unfocusedBorderColor = Colors.Steel,
    cursorColor = Colors.Ice, focusedContainerColor = Colors.Abyss.copy(alpha = 0.55f), unfocusedContainerColor = Colors.Abyss.copy(alpha = 0.55f),
)

@Composable
private fun Notice(text: String, retry: () -> Unit) {
    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(Modern.Warn.copy(alpha = 0.12f)).padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(text, style = MaterialTheme.typography.bodyMedium, color = Modern.Warn)
        Text("Try again", style = MaterialTheme.typography.labelLarge.copy(color = Colors.Ice, fontSize = 14.sp), modifier = Modifier.clip(RoundedCornerShape(6.dp)).clickable(onClick = retry).padding(vertical = 4.dp))
    }
}

@Composable
private fun Header(text: String, modifier: Modifier) = Text(text.uppercase(), style = MaterialTheme.typography.bodySmall.copy(letterSpacing = 1.sp, fontSize = 11.sp), modifier = modifier)

@Composable
private fun PlayButton(playing: Boolean, loading: Boolean, onClick: () -> Unit) {
    Box(Modifier.size(44.dp).clip(CircleShape).clickable(onClick = onClick), contentAlignment = Alignment.Center) {
        Box(Modifier.size(32.dp).clip(CircleShape).background(if (playing || loading) Modern.Accent else Color.White.copy(alpha = 0.1f)), contentAlignment = Alignment.Center) {
            if (loading) Text("…", color = Color.White) else Icon(if (playing) Icons.Default.Pause else Icons.Default.PlayArrow, if (playing) "Pause" else "Play", tint = Color.White, modifier = Modifier.size(20.dp))
        }
    }
}

/** The small player: the album's art, the song and the album, play or pause, and how far it is. */
@Composable
private fun MiniPlayer(s: MusicPreview.State) {
    if (s.pageUrl == null) return
    val context = LocalContext.current
    Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(Color.White.copy(alpha = 0.06f)).border(1.dp, Modern.Outline, RoundedCornerShape(14.dp)).padding(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Cover(s.cover, Modifier.size(48.dp))
            Column(Modifier.weight(1f)) {
                Text(s.title, style = MaterialTheme.typography.titleMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(s.error ?: s.album, style = MaterialTheme.typography.bodySmall, color = if (s.error != null) Modern.Warn else Modern.Muted, maxLines = 1, overflow = TextOverflow.Ellipsis)
            }
            PlayButton(playing = s.playing, loading = s.loading) { MusicPreview.toggle(context, s.pageUrl, s.title, s.album, s.cover) }
        }
        val f = if (s.durationMs > 0) (s.positionMs.toFloat() / s.durationMs).coerceIn(0f, 1f) else 0f
        LinearProgressIndicator(progress = { f }, color = Modern.AccentBright, trackColor = Color.White.copy(alpha = 0.1f), modifier = Modifier.fillMaxWidth().height(3.dp).clip(CircleShape))
    }
}

private val covers = object : LruCache<String, Bitmap>(16 * 1024 * 1024) {
    override fun sizeOf(key: String, value: Bitmap) = value.byteCount
}

/** An album's cover, from khinsider's own address, loaded once per session; a grey square until it is (or when there is none). */
@Composable
private fun Cover(url: String?, modifier: Modifier) {
    val bitmap by produceState<Bitmap?>(url?.let { covers.get(it) }, url) {
        if (value == null && url != null && Khinsider.isSiteUrl(url)) value = withContext(Dispatchers.IO) {
            runCatching {
                val c = java.net.URL(url).openConnection() as java.net.HttpURLConnection
                c.connectTimeout = 15_000; c.readTimeout = 30_000
                c.setRequestProperty("User-Agent", Khinsider.AGENT)
                try { c.inputStream.use { BitmapFactory.decodeStream(it) } } finally { c.disconnect() }
            }.getOrNull()?.also { covers.put(url, it) }
        }
    }
    Box(modifier.aspectRatio(1f).clip(RoundedCornerShape(8.dp)).background(Color.White.copy(alpha = 0.08f))) {
        bitmap?.let { Image(it.asImageBitmap(), null, Modifier.matchParentSize(), contentScale = ContentScale.Crop) }
    }
}
