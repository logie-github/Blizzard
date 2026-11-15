package com.logie.blizz.porter.view

import android.annotation.SuppressLint
import android.content.Context
import android.opengl.GLSurfaceView
import android.os.SystemClock
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import com.logie.blizz.porter.look.CharacterLook
import java.io.File
import javax.microedition.khronos.egl.EGLConfig
import javax.microedition.khronos.opengles.GL10
import kotlin.math.PI

/**
 * The character in 3D, turned with a finger: drag across to turn them, up and down to look from above or below, pinch to come
 * closer (the view then rises toward the face), double tap to stand back. Draws [CharacterLook]s from the game's files kept in
 * [files] (porter/engine's viewer, libporter.so, OpenGL ES 3). A look is handed over with [show]; it is put together on the
 * drawing thread at its next frame. Nothing here can stop the app: a look whose files aren't all there draws what is.
 */
@SuppressLint("ViewConstructor")
class PreviewView(context: Context, private val files: File) : GLSurfaceView(context) {
    @Volatile private var pending: CharacterLook? = null
    @Volatile private var yaw = 0.35f
    @Volatile private var pitch = 0.06f
    @Volatile private var zoom = 1f
    private var handle = 0L
    private var width = 1
    private var height = 1
    /** Told (on the drawing thread) when a look has been put together, and whether its body could be read. */
    var onShown: ((Boolean) -> Unit)? = null

    init {
        setEGLContextClientVersion(3)
        setEGLConfigChooser(8, 8, 8, 8, 16, 0)
        preserveEGLContextOnPause = true
        setRenderer(object : Renderer {
            override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
                if (handle == 0L) handle = Native.create(files.path) else Native.releaseGl(handle)
                Native.initGl(handle)
                Native.setBackdrop(handle, floatArrayOf(0.17f, 0.19f, 0.25f), floatArrayOf(0.035f, 0.04f, 0.055f))
            }

            override fun onSurfaceChanged(gl: GL10?, w: Int, h: Int) {
                width = maxOf(1, w)
                height = maxOf(1, h)
            }

            override fun onDrawFrame(gl: GL10?) {
                if (handle == 0L) return
                pending?.let { look ->
                    pending = null
                    val ok = put(look)
                    onShown?.invoke(ok)
                }
                // Coming closer looks at the face.
                val lift = 0.5f + 0.38f * ((zoom - 1f) / 2.2f).coerceIn(0f, 1f)
                Native.setView(handle, yaw, pitch, zoom, lift)
                Native.render(handle, width, height, SystemClock.uptimeMillis())
            }
        })
        renderMode = RENDERMODE_CONTINUOUSLY
    }

    /** Shows [look] (it replaces the one shown). */
    fun show(look: CharacterLook) {
        pending = look
    }

    private fun put(look: CharacterLook): Boolean {
        val groups = look.geosetGroups.entries.sortedBy { it.key }
        val ok = Native.setCharacter(handle, look.model, groups.map { it.key }.toIntArray(), groups.map { it.value }.toIntArray())
        if (!ok) return false
        for ((type, canvas) in look.canvases) {
            val flat = IntArray(canvas.layers.size * 6)
            canvas.layers.forEachIndexed { i, l ->
                flat[i * 6] = l.file; flat[i * 6 + 1] = l.x; flat[i * 6 + 2] = l.y; flat[i * 6 + 3] = l.width; flat[i * 6 + 4] = l.height; flat[i * 6 + 5] = l.blend
            }
            Native.setCanvas(handle, type, canvas.width, canvas.height, flat)
        }
        for ((type, file) in look.textures) Native.setTexture(handle, type, file)
        for (h in look.hung) Native.attach(handle, h.attachment, h.model, h.textures.keys.toIntArray(), h.textures.values.toIntArray())
        for (s in look.skinned) Native.addSkinned(handle, s.model, s.textures.keys.toIntArray(), s.textures.values.toIntArray(), s.geosets.toIntArray())
        Native.setAnim(handle, 0)
        return true
    }

    private val scale = ScaleGestureDetector(context, object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
        override fun onScale(detector: ScaleGestureDetector): Boolean {
            zoom = (zoom * detector.scaleFactor).coerceIn(0.8f, 3.2f)
            return true
        }
    })

    private val gestures = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent) = true

        override fun onScroll(e1: MotionEvent?, e2: MotionEvent, dx: Float, dy: Float): Boolean {
            if (e2.pointerCount > 1) return false
            val perPixel = (2 * PI / maxOf(width, 1)).toFloat()
            yaw -= dx * perPixel
            pitch = (pitch - dy * perPixel * 0.6f).coerceIn(-0.5f, 0.9f)
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            yaw = 0.35f; pitch = 0.06f; zoom = 1f
            return true
        }
    })

    @SuppressLint("ClickableViewAccessibility")
    override fun onTouchEvent(event: MotionEvent): Boolean {
        // The view turns the character: the screens around it don't scroll meanwhile.
        parent?.requestDisallowInterceptTouchEvent(true)
        scale.onTouchEvent(event)
        if (!scale.isInProgress) gestures.onTouchEvent(event)
        return true
    }

    override fun onDetachedFromWindow() {
        // The drawing thread is stopped and waited for first; then nothing uses the viewer.
        super.onDetachedFromWindow()
        if (handle != 0L) {
            Native.destroy(handle)
            handle = 0L
        }
    }
}
