package com.logie.blizz.warsmash

import android.app.ActivityManager
import android.app.AlertDialog
import android.content.Context
import android.opengl.GLES30
import android.opengl.GLES32
import android.os.Bundle
import android.system.Os
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.FrameLayout
import com.badlogic.gdx.Gdx
import com.badlogic.gdx.Input
import com.badlogic.gdx.audio.Sound
import com.badlogic.gdx.backends.android.AndroidApplication
import com.badlogic.gdx.backends.android.AndroidApplicationConfiguration
import com.etheller.warsmash.KeysEmulator
import com.etheller.warsmash.WarsmashGdxMenuScreen
import com.etheller.warsmash.WarsmashGdxMultiScreenGame
import com.etheller.warsmash.units.DataTable
import com.etheller.warsmash.util.StringBundle
import com.etheller.warsmash.viewer5.AudioContext
import com.etheller.warsmash.viewer5.AudioDestination
import com.etheller.warsmash.viewer5.gl.ANGLEInstancedArrays
import com.etheller.warsmash.viewer5.gl.AudioExtension
import com.etheller.warsmash.viewer5.gl.DynamicShadowExtension
import com.etheller.warsmash.viewer5.gl.Extensions
import com.etheller.warsmash.viewer5.gl.WireframeExtension
import com.logie.blizz.importer.WarsmashImporter
import java.io.File

/** Embedded engine screen in its own process; no standalone launcher or broad storage permission. */
class WarsmashActivity : AndroidApplication() {
    private val keys = KeysEmulator()
    private var started = false

    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        val path = intent.getStringExtra(WarsmashRuntime.EXTRA_DATA)
        val gameDir = path?.let(::File)
        if (gameDir == null || !WarsmashImporter.validateDir(gameDir).filesOk) {
            error("Warcraft III's classic files are missing. Return to Warsmash and import them again.")
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
            Os.setenv("GAME_VERSION", "1", true)
            val minor = com.logie.blizz.importer.Warcraft3Importer(com.logie.blizz.importer.Warcraft3Importer.Product.TFT)
                .versionOf(gameDir)?.split('.')?.getOrNull(1)?.toIntOrNull()
            Os.setenv("PLAYERS_COUNT", if (minor != null && minor >= 29) "28" else "16", true)
            Os.setenv("SERVER", "warsmash.net", true)
            Os.setenv("SCREEN_WIDTH", "", true)
            Os.setenv("SCREEN_HEIGHT", "", true)
            val ini = assets.open("warsmash.ini").bufferedReader().use { it.readText() }
            val emulator = ini.substring(ini.indexOf("[GamingNetwork]"))
            val table = DataTable(StringBundle.EMPTY).apply {
                (WarsmashConfig.sources(gameDir, support) + "\n" + emulator).byteInputStream().use { readTXT(it, true) }
            }
            extensions()
            val game = WarsmashGdxMultiScreenGame { engine ->
                engine.screen = WarsmashGdxMenuScreen(table, engine, keys)
            }
            initialize(game, AndroidApplicationConfiguration().apply { useGL30 = true })
            started = true
            controls()
        } catch (e: Exception) {
            error("Warsmash could not start: ${e.message}")
        }
    }

    private fun error(message: String) {
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

    private fun controls() {
        val row = LinearLayout(this).apply { gravity = Gravity.CENTER; setBackgroundColor(0x99000000.toInt()) }
        fun button(label: String, action: () -> Unit) {
            row.addView(Button(this).apply { text = label; setOnClickListener { action() } }, LinearLayout.LayoutParams(-2, -2))
        }
        button("Order") { Gdx.app.postRunnable { keys.onTouchDown?.invoke(Input.Buttons.RIGHT); keys.onTouchUp?.invoke(Input.Buttons.RIGHT) } }
        button("Esc") { escape() }
        button("Exit") { finish() }
        addContentView(row, FrameLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.TOP or Gravity.END))
    }

    private fun escape() { Gdx.app.postRunnable { keys.onKeyDownListener?.invoke(Input.Keys.ESCAPE); keys.onKeyUpListener?.invoke(Input.Keys.ESCAPE) } }
    @Deprecated("Game back maps to Escape")
    override fun onBackPressed() { if (started) escape() else finish() }
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
