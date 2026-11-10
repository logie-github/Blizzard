package com.logie.blizz.game

import android.opengl.GLES20
import android.os.SystemClock
import com.winlator.xserver.Drawable
import com.winlator.xserver.Window
import com.winlator.xserver.XServer
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Looks at Warcraft III's picture on the phone, for [Wc3Screen]: the few parts of it that say what a tap should be, read
 * where Winlator keeps the game's frame.
 *
 * The game draws through OpenGL (Wine's Direct3D on Winlator's own GL: the phone's report of 10 November 2026 names the
 * renderer "Gladio"), and each finished frame is copied into a texture that only the drawing thread can read. So a look is a
 * small job queued on that thread: the texture goes on a framebuffer of this class's own and four small rectangles are read
 * (the top band and the command card, each as it lies in the texture either way up: some 100,000 pixels, not the 700,000 of
 * the whole frame). A window drawn without the GPU keeps its pixels in memory, and those are read directly.
 *
 * Nothing here can stop the game: every step is inside one try, a failed look leaves [state] at [Wc3Screen.State.OTHER]
 * (a tap is then the left click), and the reason is kept for the reports ([problem]). Winlator's own screenshot function
 * was not used: it compiles a shader at every call and once ended the app from the drawing thread (the phone, 8 November 2026).
 */
class Wc3Watch(private val xServer: XServer) {
    /** What the last look saw. */
    @Volatile var state: Wc3Screen.State = Wc3Screen.State.OTHER
        private set
    /** When the last look that could read the picture finished ([SystemClock.uptimeMillis]); 0 before the first. */
    @Volatile var readAt = 0L
        private set
    /** Why the last look could not read the picture, if it could not. */
    @Volatile var problem: String? = null
        private set
    /** How the picture was last read: "gl" or "memory", with its size. */
    @Volatile var source: String = ""
        private set

    /** The last look read the picture ([state] is what it shows, not what a failed look leaves). */
    @Volatile private var seen = false
    @Volatile private var busy = false
    private var framebuffer = 0
    private var buffer: ByteBuffer? = null
    /** The parts' colours, kept from look to look (the same four sizes every time). */
    private val kept = arrayOfNulls<IntArray>(4)

    /** What a tap is now: an order only on a fresh look that saw the player's own selection. */
    fun commanding(now: Long = SystemClock.uptimeMillis()): Boolean = seen && state == Wc3Screen.State.COMMAND && now - readAt <= FRESH_MS

    /**
     * Something to leave is up, on a fresh look that read the picture: a scene, a menu, a box over the game ([Wc3Screen.State.OTHER]),
     * or a command waiting for its target. The two-finger tap is Escape then, and the game's menu otherwise.
     */
    fun leaving(now: Long = SystemClock.uptimeMillis()): Boolean =
        seen && now - readAt <= FRESH_MS && (state == Wc3Screen.State.OTHER || state == Wc3Screen.State.TARGET)

    /** Queues a look (one at a time); its result is in [state] a frame or two later. */
    fun look() {
        if (busy) return
        val renderer = xServer.renderer ?: return
        val drawable = gameDrawable() ?: run { unseen(); return }
        busy = true
        runCatching {
            renderer.xServerView.queueEvent {
                try {
                    read(drawable)
                } catch (t: Throwable) {
                    unseen()
                    problem = t.toString().take(200)
                } finally {
                    busy = false
                }
            }
            renderer.xServerView.requestRender()
        }.onFailure { busy = false; problem = it.toString().take(200) }
    }

    /** What the game draws into: the biggest window there is (the drawing surface inside the game's window, when it has one). */
    private fun gameDrawable(): Drawable? = runCatching {
        xServer.lock(XServer.Lockable.WINDOW_MANAGER, XServer.Lockable.DRAWABLE_MANAGER).use {
            val root = xServer.windowManager.rootWindow
            var best: Window? = null
            var bestArea = 0
            fun visit(window: Window) {
                if (!window.isRenderable) return
                val area = window.width * window.height
                if (window !== root && !window.isDesktopWindow && window.content != null && area >= bestArea && area > 1) {
                    best = window
                    bestArea = area
                }
                for (child in window.children) visit(child)
            }
            visit(root)
            best?.content
        }
    }.getOrNull()

    /** On the drawing thread. */
    private fun read(drawable: Drawable) {
        synchronized(drawable.renderLock) {
            val width = drawable.width.toInt()
            val height = drawable.height.toInt()
            val memory = drawable.data
            val pixels = if (memory != null) fromMemory(memory, width, height) else fromTexture(drawable, width, height)
            if (pixels == null) {
                unseen()
                return
            }
            state = Wc3Screen.state(width, height, pixels)
            source = (if (memory != null) "memory" else "gl") + " ${width}x$height"
            readAt = SystemClock.uptimeMillis()
            problem = null
            seen = true
        }
    }

    /** A look that read nothing: a tap is the left click, and nothing is known to be up. */
    private fun unseen() {
        seen = false
        state = Wc3Screen.State.OTHER
    }

    /** A window drawn without the GPU: its pixels as the X server keeps them (blue, green, red, alpha; the top row first). */
    private fun fromMemory(data: ByteBuffer, width: Int, height: Int): Wc3Screen.Pixels? {
        if (data.capacity() < width * height * 4) {
            problem = "the game's picture in memory is ${data.capacity()} bytes for ${width}x$height"
            return null
        }
        val view = data.duplicate().order(ByteOrder.LITTLE_ENDIAN)
        return Wc3Screen.Pixels { x, y -> view.getInt((y * width + x) * 4) }
    }

    /** One rectangle of the texture, read. */
    private class Part(val left: Int, val top: Int, val width: Int, val height: Int, val colors: IntArray) {
        fun has(x: Int, y: Int) = x >= left && x < left + width && y >= top && y < top + height
        fun at(x: Int, y: Int) = colors[(y - top) * width + (x - left)]
    }

    /** The game's frame in its texture: the parts [Wc3Screen] reads, as they lie either way up. Anything else reads black. */
    private fun fromTexture(drawable: Drawable, width: Int, height: Int): Wc3Screen.Pixels? {
        val texture = drawable.texture ?: return null
        if (!texture.isAllocated || width < 320 || height < 240) {
            problem = "the game's picture has no texture yet"
            return null
        }
        if (framebuffer == 0) {
            val ids = IntArray(1)
            GLES20.glGenFramebuffers(1, ids, 0)
            framebuffer = ids[0]
        }
        if (framebuffer == 0) {
            problem = "no framebuffer (the drawing thread has no OpenGL now)"
            return null
        }
        GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, framebuffer)
        try {
            GLES20.glFramebufferTexture2D(GLES20.GL_FRAMEBUFFER, GLES20.GL_COLOR_ATTACHMENT0, GLES20.GL_TEXTURE_2D, texture.textureId, 0)
            val status = GLES20.glCheckFramebufferStatus(GLES20.GL_FRAMEBUFFER)
            if (status != GLES20.GL_FRAMEBUFFER_COMPLETE) {
                // (a framebuffer from an OpenGL that has since been made anew is of no use: the next look makes another)
                problem = "the game's texture can't be read (framebuffer status 0x${Integer.toHexString(status)})"
                framebuffer = 0
                return null
            }
            val parts = ArrayList<Part>(4)
            for (band in listOf(Wc3Screen.TOP_BAND, Wc3Screen.CARD_BAND)) {
                val left = Math.floor((band.left * width).toDouble()).toInt().coerceIn(0, width - 1)
                val right = Math.ceil((band.right * width).toDouble()).toInt().coerceIn(left + 1, width)
                val top = Math.floor((band.top * height).toDouble()).toInt().coerceIn(0, height - 1)
                val bottom = Math.ceil((band.bottom * height).toDouble()).toInt().coerceIn(top + 1, height)
                // As it lies if the texture's first row is the picture's top, and if it is the picture's bottom.
                parts += part(parts.size, left, top, right - left, bottom - top)
                parts += part(parts.size, left, height - bottom, right - left, bottom - top)
            }
            GLES20.glFramebufferTexture2D(GLES20.GL_FRAMEBUFFER, GLES20.GL_COLOR_ATTACHMENT0, GLES20.GL_TEXTURE_2D, 0, 0)
            return Wc3Screen.Pixels { x, y -> parts.firstOrNull { it.has(x, y) }?.at(x, y) ?: BLACK }
        } finally {
            GLES20.glBindFramebuffer(GLES20.GL_FRAMEBUFFER, 0)
        }
    }

    private fun part(index: Int, left: Int, top: Int, width: Int, height: Int): Part {
        val bytes = width * height * 4
        val into = buffer?.takeIf { it.capacity() >= bytes } ?: ByteBuffer.allocateDirect(maxOf(bytes, 1 shl 18)).order(ByteOrder.LITTLE_ENDIAN).also { buffer = it }
        into.clear()
        GLES20.glPixelStorei(GLES20.GL_PACK_ALIGNMENT, 1)
        GLES20.glReadPixels(left, top, width, height, GLES20.GL_RGBA, GLES20.GL_UNSIGNED_BYTE, into)
        val colors = kept[index]?.takeIf { it.size == width * height } ?: IntArray(width * height).also { kept[index] = it }
        // Red, green, blue, alpha as bytes: read as one number they are alpha, blue, green, red; red and blue change places.
        for (i in colors.indices) {
            val c = into.getInt(i * 4)
            colors[i] = (c and 0xff00ff00.toInt()) or ((c and 0xff) shl 16) or ((c shr 16) and 0xff)
        }
        return Part(left, top, width, height, colors)
    }

    companion object {
        /** A look older than this says nothing about now. */
        const val FRESH_MS = 2500L
        private const val BLACK = 0xff000000.toInt()
    }
}
