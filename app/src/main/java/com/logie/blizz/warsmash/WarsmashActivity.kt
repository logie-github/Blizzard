package com.logie.blizz.warsmash

import android.app.ActivityManager
import android.app.AlertDialog
import android.content.Context
import android.opengl.GLES30
import android.opengl.GLES32
import android.os.Bundle
import android.system.Os
import android.view.KeyEvent
import android.view.ViewGroup
import com.badlogic.gdx.Gdx
import com.badlogic.gdx.Input
import com.badlogic.gdx.audio.Sound
import com.badlogic.gdx.backends.android.AndroidApplication
import com.badlogic.gdx.backends.android.AndroidApplicationConfiguration
import com.etheller.warsmash.KeysEmulator
import com.etheller.warsmash.WarsmashGdxMenuScreen
import com.etheller.warsmash.WarsmashGdxMultiScreenGame
import com.etheller.warsmash.units.DataTable
import com.etheller.warsmash.util.MovieHost
import com.etheller.warsmash.util.StringBundle
import com.etheller.warsmash.viewer5.AudioContext
import com.etheller.warsmash.viewer5.AudioDestination
import com.etheller.warsmash.viewer5.gl.ANGLEInstancedArrays
import com.etheller.warsmash.viewer5.gl.AudioExtension
import com.etheller.warsmash.viewer5.gl.DynamicShadowExtension
import com.etheller.warsmash.viewer5.gl.Extensions
import com.etheller.warsmash.viewer5.gl.WireframeExtension
import com.logie.blizz.importer.Warcraft3WarsmashImporter
import java.io.File

/** Embedded engine screen in its own process; no standalone launcher or broad storage permission. */
class WarsmashActivity : AndroidApplication() {
    private val keys = KeysEmulator()
    private var started = false
    private var overlay: MovieOverlay? = null
    private var foreground = false

    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        val path = intent.getStringExtra(WarsmashRuntime.EXTRA_DATA)
        val gameDir = path?.let(::File)
        // Reign of Chaos or The Frozen Throne: the engine's own GameVersion (0 or 1), as its main menu's edition button sets it.
        val edition = runCatching { WarsmashRuntime.Edition.valueOf(intent.getStringExtra(WarsmashRuntime.EXTRA_EDITION).orEmpty()) }
            .getOrDefault(WarsmashRuntime.Edition.TFT)
        if (gameDir == null || !Warcraft3WarsmashImporter.validateDir(gameDir, edition).filesOk) {
            error("Warcraft III's classic files are missing. Go back, hold its box and use Install & repair.")
            return
        }
        val gl = (getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager).deviceConfigurationInfo.reqGlEsVersion
        if (gl < 0x30002) {
            error("This Warsmash engine needs OpenGL ES 3.2.")
            return
        }
        try {
            val support = File(filesDir, "warsmash-support/1.0.4/resources")
            copyAssets("resources", support)
            File(gameDir, "Maps/Download").mkdirs()
            Os.setenv("game_files", gameDir.absolutePath, true)
            Os.setenv("GAME_VERSION", edition.gameVersion.toString(), true)
            val minor = com.logie.blizz.importer.Warcraft3Importer(com.logie.blizz.importer.Warcraft3Importer.Product.TFT)
                .versionOf(gameDir)?.split('.')?.getOrNull(1)?.toIntOrNull()
            Os.setenv("PLAYERS_COUNT", if (minor != null && minor >= 29) "28" else "16", true)
            Os.setenv("SERVER", "warsmash.net", true)
            Os.setenv("SCREEN_WIDTH", "", true)
            Os.setenv("SCREEN_HEIGHT", "", true)
            val ini = assets.open("warsmash.ini").bufferedReader().use { it.readText() }
            val emulator = ini.substring(ini.indexOf("[GamingNetwork]"))
            val table = DataTable(StringBundle.EMPTY).apply {
                // Classic+ (its models and textures) over the game's files when it is on (ClassicPlus).
                (WarsmashConfig.sources(gameDir, support, ClassicPlus.layer(this@WarsmashActivity)) + "\n" + emulator).byteInputStream().use { readTXT(it, true) }
            }
            extensions()
            movies(gameDir)
            val game = WarsmashGdxMultiScreenGame { engine ->
                engine.screen = WarsmashGdxMenuScreen(table, engine, keys)
            }
            initialize(game, AndroidApplicationConfiguration().apply { useGL30 = true })
            started = true
            // No buttons over the game (the person asked them away): Back is Escape, and the game's own menu has Quit.
        } catch (e: Exception) {
            error("Warsmash could not start: ${e.message}")
        }
    }

    private fun error(message: String) {
        // AndroidApplication's lifecycle needs a backend even when preflight fails.
        if (!started) {
            initialize(object : com.badlogic.gdx.ApplicationAdapter() {}, AndroidApplicationConfiguration())
            started = true
        }
        AlertDialog.Builder(this).setTitle("Warsmash").setMessage(message)
            .setPositiveButton("Return") { _, _ -> finish() }.setOnCancelListener { finish() }.show()
    }

    private fun copyAssets(path: String, to: File) {
        val children = assets.list(path).orEmpty()
        if (children.isEmpty()) {
            if (!to.isFile) { to.parentFile?.mkdirs(); assets.open(path).use { input -> to.outputStream().use { input.copyTo(it) } } }
        } else {
            to.mkdirs()
            children.forEach { copyAssets("$path/$it", File(to, it)) }
        }
    }

    private fun escape() { Gdx.app.postRunnable { keys.onKeyDownListener?.invoke(Input.Keys.ESCAPE); keys.onKeyUpListener?.invoke(Input.Keys.ESCAPE) } }
    @Deprecated("Game back maps to Escape")
    override fun onBackPressed() { if (started) escape() else finish() }

    /**
     * Warcraft III's movies, where the engine asks for them (MovieHost, patches/warsmash/0003): the files in the game's
     * Movies folder, played by MovieOverlay over the engine, whose drawing and sound wait meanwhile. The once-only ones
     * (the introduction, each campaign's opening for a profile) are remembered here.
     */
    private fun movies(gameDir: File) {
        val seen = getSharedPreferences("warsmash-movies", MODE_PRIVATE)
        MovieHost.player = object : MovieHost.Player {
            override fun play(names: Array<String>, captions: Array<String?>, done: Runnable) {
                runOnUiThread { showMovies(gameDir, names, captions, done) }
            }

            override fun seen(key: String) = seen.getBoolean(key, false)
            override fun markSeen(key: String) { seen.edit().putBoolean(key, true).apply() }
        }
    }

    private fun showMovies(gameDir: File, names: Array<String>, captions: Array<String?>, done: Runnable) {
        val movies = names.indices.mapNotNull { i -> WarsmashMovies.find(gameDir, names[i])?.let { MovieOverlay.Movie(it, captions.getOrNull(i)) } }
        if (movies.isEmpty() || overlay != null || isFinishing) {
            done.run()
            return
        }
        Gdx.graphics.isContinuousRendering = false
        audio.pause()
        lateinit var shown: MovieOverlay
        shown = MovieOverlay(this, movies) {
            (shown.parent as? ViewGroup)?.removeView(shown)
            overlay = null
            // Away from the app the sound comes back with it (AndroidApplication's onResume).
            if (foreground) audio.resume()
            Gdx.graphics.isContinuousRendering = true
            done.run()
        }
        overlay = shown
        addContentView(shown, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
    }

    /** While a movie plays the keys are its: Back skips them all, Escape, Space and Enter the one playing. */
    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        val shown = overlay ?: return super.dispatchKeyEvent(event)
        if (event.action == KeyEvent.ACTION_UP) {
            when (event.keyCode) {
                KeyEvent.KEYCODE_BACK -> shown.skipAll()
                KeyEvent.KEYCODE_ESCAPE, KeyEvent.KEYCODE_SPACE, KeyEvent.KEYCODE_ENTER -> shown.skipOne()
            }
        }
        return true
    }

    override fun onResume() {
        super.onResume()
        foreground = true
    }

    override fun onPause() {
        foreground = false
        super.onPause()
    }
    override fun onDestroy() {
        super.onDestroy()
        if (isFinishing) android.os.Process.killProcess(android.os.Process.myPid())
    }

    private fun extensions() {
        Extensions.angleInstancedArrays = object : ANGLEInstancedArrays {
            override fun glVertexAttribDivisorANGLE(index: Int, divisor: Int) = GLES30.glVertexAttribDivisor(index, divisor)
            override fun glDrawElementsInstancedANGLE(mode: Int, count: Int, type: Int, indicesOffset: Int, instanceCount: Int) = GLES30.glDrawElementsInstanced(mode, count, type, indicesOffset, instanceCount)
            override fun glDrawArraysInstancedANGLE(mode: Int, first: Int, count: Int, instanceCount: Int) = GLES30.glDrawArraysInstanced(mode, first, count, instanceCount)
        }
        Extensions.dynamicShadowExtension = object : DynamicShadowExtension {
            override fun glFramebufferTexture(target: Int, attachment: Int, texture: Int, level: Int) = GLES32.glFramebufferTexture(target, attachment, texture, level)
            override fun glDrawBuffer(mode: Int) { GLES30.glDrawBuffers(1, intArrayOf(mode), 0) }
        }
        Extensions.wireframeExtension = WireframeExtension { _, _ -> }
        Extensions.audio = object : AudioExtension {
            override fun getDuration(sound: Sound?) = if (sound == null) 1f else 2f
            override fun play(buffer: Sound, volume: Float, pitch: Float, x: Float, y: Float, z: Float, is3dSound: Boolean, maxDistance: Float, refDistance: Float, looping: Boolean): Long =
                if (looping) buffer.loop(volume, pitch, 0f) else buffer.play(volume, pitch, 0f)
            override fun createContext(world: Boolean) = AudioContext(AudioContext.Listener.DO_NOTHING, object : AudioDestination {})
        }
        Extensions.GL_LINE = 0
        Extensions.GL_FILL = 0
    }
}
