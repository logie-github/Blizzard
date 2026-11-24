package com.logie.blizz.ps1

import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Rect
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.os.Bundle
import android.os.SystemClock
import android.util.Log
import android.view.KeyEvent
import android.view.SurfaceHolder
import android.view.SurfaceView
import android.view.View
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.Toast
import com.logie.blizz.importer.LibraryEntry
import java.io.File

class Ps1Activity : Activity() {
    private lateinit var gestures: Ps1GestureView
    private lateinit var gameSurface: SurfaceView
    private var menu: AlertDialog? = null
    private var resumed = false
    @Volatile private var active = false
    @Volatile private var stopped = false
    @Volatile private var touchButtons = 0
    @Volatile private var gamepadButtons = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val image = intent.getStringExtra("disc")?.let(::File)
        val saves = intent.getStringExtra("saves")?.let(::File)
        if (image == null || !image.isFile || saves == null || (!saves.isDirectory && !saves.mkdirs())) {
            fail("Warcraft II couldn't open its disc or save folder. Open Install & repair to check the disc.")
            return
        }

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        gameSurface = SurfaceView(this)
        gestures = Ps1GestureView(this, { button, pressed ->
            val bit = when (button) {
                PsButton.CROSS -> CROSS
                PsButton.CIRCLE -> CIRCLE
                PsButton.SQUARE -> SQUARE
                PsButton.TRIANGLE -> TRIANGLE
                PsButton.START -> START
                PsButton.SELECT -> SELECT
                PsButton.L1 -> L1
                PsButton.R1 -> R1
                PsButton.DPAD_UP -> UP
                PsButton.DPAD_DOWN -> DOWN
                PsButton.DPAD_LEFT -> LEFT
                PsButton.DPAD_RIGHT -> RIGHT
            }
            touchButtons = if (pressed) touchButtons or bit else touchButtons and bit.inv()
        }, ::openMenu)
        setContentView(FrameLayout(this).apply {
            setBackgroundColor(Color.BLACK)
            addView(gameSurface)
            addView(gestures)
        })
        Thread({ runGame(image, saves) }, "PlayStation").start()
        if (savedInstanceState == null) {
            Toast.makeText(this, "Swipe to steer · Tap to confirm · Two fingers down to pause", Toast.LENGTH_LONG).show()
        }
    }

    override fun onResume() {
        super.onResume()
        resumed = true
        active = menu == null
        hideSystemBars()
    }

    override fun onPause() {
        resumed = false
        active = false
        if (::gestures.isInitialized) gestures.releaseAll()
        touchButtons = 0
        gamepadButtons = 0
        super.onPause()
    }

    override fun onDestroy() {
        stopped = true
        super.onDestroy()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) {
            hideSystemBars()
            if (resumed && menu == null && !isFinishing) active = true
        }
    }

    @Suppress("DEPRECATION")
    private fun hideSystemBars() {
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or
            View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN or
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
    }

    @Deprecated("Uses the platform Back callback for the app's target SDK.")
    override fun onBackPressed() = openMenu()

    private fun openMenu() {
        if (menu != null || !::gestures.isInitialized || isFinishing) return
        active = false
        gestures.releaseAll()
        touchButtons = 0
        gamepadButtons = 0
        menu = AlertDialog.Builder(this)
            .setTitle("Warcraft II")
            .setMessage("Swipe to steer · Tap for Cross · Hold for Circle · Double tap for Triangle\n\nTwo fingers up for Square · Down for Start · Right or left for L1 or R1")
            .setPositiveButton("Resume", null)
            .setNegativeButton("Return to Blizzard") { _, _ -> finish() }
            .create().apply {
                setOnDismissListener {
                    menu = null
                    active = resumed && !isFinishing && hasWindowFocus()
                }
                show()
            }
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        val bit = when (event.keyCode) {
            KeyEvent.KEYCODE_BUTTON_A -> CROSS
            KeyEvent.KEYCODE_BUTTON_B -> CIRCLE
            KeyEvent.KEYCODE_BUTTON_X -> SQUARE
            KeyEvent.KEYCODE_BUTTON_Y -> TRIANGLE
            KeyEvent.KEYCODE_BUTTON_START -> START
            KeyEvent.KEYCODE_BUTTON_SELECT -> SELECT
            KeyEvent.KEYCODE_BUTTON_L1 -> L1
            KeyEvent.KEYCODE_BUTTON_R1 -> R1
            KeyEvent.KEYCODE_BUTTON_L2 -> 1 shl 12
            KeyEvent.KEYCODE_BUTTON_R2 -> 1 shl 13
            KeyEvent.KEYCODE_DPAD_UP -> UP
            KeyEvent.KEYCODE_DPAD_DOWN -> DOWN
            KeyEvent.KEYCODE_DPAD_LEFT -> LEFT
            KeyEvent.KEYCODE_DPAD_RIGHT -> RIGHT
            else -> return super.dispatchKeyEvent(event)
        }
        if (active) {
            if (event.action == KeyEvent.ACTION_DOWN) gamepadButtons = gamepadButtons or bit
            if (event.action == KeyEvent.ACTION_UP) gamepadButtons = gamepadButtons and bit.inv()
            return true
        }
        return super.dispatchKeyEvent(event)
    }

    private fun runGame(image: File, saves: File) {
        // A previous instance may still be finishing when the player launches the game again.
        try {
            synchronized(Ps1Core) {
                if (stopped) return
                try {
                    val fps = Ps1Core.open(image.path, saves.path)
                    check(fps in 45.0..65.0) { "The emulator couldn't boot the disc" }
                    runFrames(fps)
                } finally {
                    Ps1Core.close()
                }
            }
        } catch (error: Exception) {
            Log.e("BlizzardPS1", "PlayStation session stopped", error)
            fail("Warcraft II couldn't run this disc. Check the image in Install & repair.")
        } catch (error: LinkageError) {
            Log.e("BlizzardPS1", "PlayStation core couldn't load", error)
            fail("This Blizzard build is missing its PlayStation emulator.")
        }
    }

    private fun runFrames(fps: Double) {
        val pixels = IntArray(1024 * 512)
        val samples = ShortArray(16384)
        val surface = gameSurface.holder
        val sound = createAudio()
        val paint = Paint(Paint.FILTER_BITMAP_FLAG)
        val target = Rect()
        var bitmap: Bitmap? = null
        var next = System.nanoTime()
        val frameTime = (1_000_000_000 / fps).toLong()
        try {
            while (!stopped) {
                if (!active || !surface.surface.isValid) {
                    if (sound?.playState == AudioTrack.PLAYSTATE_PLAYING) {
                        sound.pause()
                        sound.flush()
                    }
                    SystemClock.sleep(30)
                    next = System.nanoTime()
                    continue
                }
                if (sound != null && sound.playState != AudioTrack.PLAYSTATE_PLAYING) sound.play()
                val dimensions = Ps1Core.step(touchButtons or gamepadButtons, pixels)
                val width = dimensions ushr 16
                val height = dimensions and 0xffff
                if (width > 0 && height > 0) {
                    val frame = bitmap?.takeIf { it.width == width && it.height == height }
                        ?: Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888).also { bitmap = it }
                    frame.setPixels(pixels, 0, width, 0, 0, width, height)
                    draw(surface, frame, target, paint)
                }
                if (sound != null) {
                    val count = Ps1Core.readAudio(samples)
                    if (count > 0) sound.write(samples, 0, count, AudioTrack.WRITE_NON_BLOCKING)
                }
                next += frameTime
                val now = System.nanoTime()
                if (next < now - frameTime) next = now
                if (next > now) {
                    val delay = next - now
                    Thread.sleep(delay / 1_000_000, (delay % 1_000_000).toInt())
                }
            }
        } finally {
            sound?.release()
        }
    }

    private fun draw(surface: SurfaceHolder, frame: Bitmap, target: Rect, paint: Paint) {
        val canvas = try { surface.lockHardwareCanvas() } catch (_: IllegalStateException) { return }
        try {
            canvas.drawColor(Color.BLACK)
            val width = minOf(canvas.width, canvas.height * 4 / 3)
            val height = minOf(canvas.height, canvas.width * 3 / 4)
            val left = (canvas.width - width) / 2
            val top = (canvas.height - height) / 2
            target.set(left, top, left + width, top + height)
            canvas.drawBitmap(frame, null, target, paint)
        } finally {
            surface.unlockCanvasAndPost(canvas)
        }
    }

    private fun createAudio(): AudioTrack? = runCatching {
        val format = AudioFormat.Builder()
            .setSampleRate(44100)
            .setChannelMask(AudioFormat.CHANNEL_OUT_STEREO)
            .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
            .build()
        val bufferSize = AudioTrack.getMinBufferSize(44100, format.channelMask, format.encoding)
        AudioTrack.Builder()
            .setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).build())
            .setAudioFormat(format)
            .setBufferSizeInBytes(maxOf(bufferSize, 8820))
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build().let { if (it.state == AudioTrack.STATE_INITIALIZED) it else { it.release(); null } }
    }.getOrNull()

    private fun fail(message: String) {
        runOnUiThread {
            if (!isFinishing && !isDestroyed) {
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
                finish()
            }
        }
    }

    companion object {
        const val RUNTIME = "playstation"
        private const val CROSS = 1 shl 0
        private const val SQUARE = 1 shl 1
        private const val SELECT = 1 shl 2
        private const val START = 1 shl 3
        private const val UP = 1 shl 4
        private const val DOWN = 1 shl 5
        private const val LEFT = 1 shl 6
        private const val RIGHT = 1 shl 7
        private const val CIRCLE = 1 shl 8
        private const val TRIANGLE = 1 shl 9
        private const val L1 = 1 shl 10
        private const val R1 = 1 shl 11

        fun play(context: Context, entry: LibraryEntry) {
            context.startActivity(Intent(context, Ps1Activity::class.java)
                .putExtra("disc", File(entry.installPath, entry.executable).path)
                .putExtra("saves", entry.saveLocation)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        }
    }
}
