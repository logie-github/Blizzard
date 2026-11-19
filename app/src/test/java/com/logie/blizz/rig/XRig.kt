package com.logie.blizz.rig

import com.winlator.xconnector.UnixSocketConfig
import com.winlator.xenvironment.components.SysVSharedMemoryComponent
import com.winlator.xenvironment.components.XServerComponent
import com.winlator.xserver.Pointer
import com.winlator.xserver.ScreenInfo
import com.winlator.xserver.Window
import com.winlator.xserver.XKeycode
import com.winlator.xserver.XServer
import java.awt.image.BufferedImage
import java.io.File
import java.nio.file.Files
import javax.imageio.ImageIO

/**
 * The phone's X server on a desktop (tools/xrig/README.md): Winlator's own X server (the Java one the games' Windows draws on
 * and gets its mouse and keyboard from on the phone) started in this test JVM, with its native half built for this machine
 * (tools/xrig/build-lib.sh), listening as display [display]; Winlator's Wine (an x86_64 build: it runs natively here) started
 * against it. What a game is sent when the app injects a click or a key, and what the server holds of its windows, is then
 * read here instead of guessed at: the stock X server of the other rig (Xvfb) gets right what this one may get wrong.
 *
 * Nothing is drawn through a GPU here: programs that draw with GDI or plain X images are seen ([screenshot]); Direct3D,
 * OpenGL and Vulkan ones are not.
 *
 * Asked for with BLIZZ_XRIG=1 (and BLIZZ_XRIG_LIB, the folder of libwinlator.so, as java.library.path); skipped otherwise.
 */
class XRig(val width: Int = 800, val height: Int = 600, private val display: Int = 77) : AutoCloseable {
    companion object {
        val enabled: Boolean get() = System.getenv("BLIZZ_XRIG") == "1"
        /** Winlator's runtime unpacked where its Wine has its path compiled in (README, "Testing the Windows games here"). */
        val rootfs = File(System.getenv("BLIZZ_XRIG_ROOTFS") ?: "/data/data/com.logie.blizz/winrootfs")
        /** The Wine prefix of the rig. */
        val prefix = File(System.getenv("BLIZZ_XRIG_PREFIX") ?: "/tmp/wlc/.wine")
        /** Where the rig's Windows programs were built (tools/xrig/build-programs.sh). */
        val programs = File(System.getenv("BLIZZ_XRIG_LIB") ?: "build/xrig")
        val windowsDir: File get() = File(prefix, "drive_c/windows")
    }

    private val socketRoot = File("/tmp/xrig-$display")
    val xServer = XServer(null, ScreenInfo(width, height))
    /**
     * The phone's game view and its renderer, as XServerDisplayActivity makes them: the server hands its textures' disposal and
     * every change of its windows to them (without them the first freed pixmap ended the client's thread on a null renderer).
     * No surface ever comes, so nothing is drawn; what the renderer works out of the windows (which is stretched to the
     * screen, where a click then lands) is worked out as on the phone, the app's "fill the screen" switch on as GestureView sets it.
     */
    val view = com.winlator.widget.XServerView(org.robolectric.RuntimeEnvironment.getApplication(), xServer).also {
        it.renderer.isForceWindowsFullscreen = true
        xServer.renderer = it.renderer
    }
    /**
     * The Android half of Winlator's winhandler.exe (the helper every game is started through on the phone, which also runs
     * programs the app asks for: [com.winlator.winhandler.WinHandler.exec]), so [game] starts a program exactly as the app does.
     */
    val winHandler = com.winlator.winhandler.WinHandler(null).also { xServer.setWinHandler(it); it.start() }
    private val shm = SysVSharedMemoryComponent(xServer, UnixSocketConfig.create(socketRoot.path, UnixSocketConfig.SYSVSHM_SERVER_PATH))
    private val x = XServerComponent(xServer, UnixSocketConfig.create(socketRoot.path, UnixSocketConfig.XSERVER_PATH))
    /** Where this machine's X library looks for display [display]: a link to the server's socket (the phone's library has the runtime's path compiled in). */
    private val link = File("/tmp/.X11-unix/X$display")
    private val started = ArrayList<Process>()

    init {
        wineserver("-k")
        shm.start()
        // This machine's X library takes its shared memory from the kernel, not from Winlator's service: the server is handed
        // those, and the service's own too (the phone's arm64 libraries under Box64 and qemu ask the service, as on the phone).
        val service = SysVSharedMemoryComponent::class.java.getDeclaredField("sysVSharedMemory").apply { isAccessible = true }
            .get(shm) as com.winlator.sysvshm.SysVSharedMemory
        xServer.setSHMSegmentManager(com.winlator.xserver.SHMSegmentManager(HostSharedMemory(service)))
        x.start()
        link.parentFile?.mkdirs()
        Files.deleteIfExists(link.toPath())
        Files.createSymbolicLink(link.toPath(), File(socketRoot, UnixSocketConfig.XSERVER_PATH).toPath())
    }

    private fun environment(builder: ProcessBuilder, debug: String) {
        val env = builder.environment()
        env.keys.removeAll { it.startsWith("JAVA_") || it == "LD_LIBRARY_PATH" }
        env["DISPLAY"] = ":$display"
        env["HOME"] = File(rootfs, "home/xuser").path
        env["USER"] = "xuser"
        env["WINEPREFIX"] = prefix.path
        env["WINEESYNC"] = "1"
        env["WINE_DO_NOT_CREATE_DXGI_DEVICE_MANAGER"] = "1"
        env["WINEDEBUG"] = debug
        env["PATH"] = File(rootfs, "opt/wine/bin").path + ":/usr/bin:/bin"
    }

    private fun wineserver(vararg args: String) {
        val builder = ProcessBuilder(listOf(File(rootfs, "opt/wine/bin/wineserver").path) + args)
        environment(builder, "-all")
        builder.redirectErrorStream(true).redirectOutput(File("/dev/null"))
        runCatching { builder.start().waitFor() }
    }

    /** A Windows program on the games' desktop (`explorer /desktop=shell,WxH`, as the app starts them), its output into [log]. */
    fun run(program: String, vararg args: String, debug: String = "-all", log: File = File("/tmp/xrig-$display-wine.log"), directory: File? = null): Process {
        val command = listOf(File(rootfs, "opt/wine/bin/wine").path, "explorer", "/desktop=shell,${width}x$height", program) + args
        val builder = ProcessBuilder(command)
        environment(builder, debug)
        builder.directory(directory ?: prefix)
        builder.redirectErrorStream(true).redirectOutput(ProcessBuilder.Redirect.appendTo(log))
        return builder.start().also { started += it }
    }

    /**
     * A game started as the app starts it (XServerDisplayActivity.getWineStartCommand): the session's keeper (borderless.exe,
     * with `/noframes` unless [frames]; not at all without [keeper], as before build 179), which starts Winlator's
     * winhandler.exe on the games' desktop, told the game's folder ([dosDir], such as `D:\\d2`) and its program and arguments.
     */
    fun game(dosDir: String, program: String, vararg args: String, keeper: Boolean = true, frames: Boolean = true, debug: String = "-all", log: File = File("/tmp/xrig-$display-wine.log")): Process {
        // As the phone's start command is split (ProcessHelper.splitCommand): the folder with its backslashes doubled
        // (StringUtils.escapeDOSPath), the program's name still in its quotes.
        val helper = arrayOf("C:\\windows\\winhandler.exe", "/dir", com.winlator.core.StringUtils.escapeDOSPath(dosDir), "\"$program\"", *args)
        if (!keeper) return run(helper[0], *helper.drop(1).toTypedArray(), debug = debug, log = log)
        install(File(programs, "borderless.exe"))
        val switches = if (frames) emptyArray() else arrayOf("/noframes")
        return run("C:\\windows\\borderless.exe", *switches, *helper, debug = debug, log = log)
    }

    /** A program of the rig's (tools/xrig) or the app's (borderless.exe) put into the prefix's Windows folder. */
    fun install(file: File): File = File(windowsDir, file.name).also { file.copyTo(it, overwrite = true) }

    /** Every window the server holds, the root first, parents before children, lower before higher. */
    fun windows(): List<Window> = xServer.lock(XServer.Lockable.WINDOW_MANAGER).use {
        val out = ArrayList<Window>()
        fun walk(w: Window) { out += w; for (c in w.children) walk(c) }
        walk(xServer.windowManager.rootWindow)
        out
    }

    /** The mapped window with this name, if there is one. */
    fun window(name: String): Window? = windows().firstOrNull { it.attributes.isMapped && it.name == name }

    fun describe(): String = windows().joinToString("\n") { w ->
        var depth = 0
        var p = w.parent
        while (p != null) { depth++; p = p.parent }
        "  ".repeat(depth) + "0x${Integer.toHexString(w.id)} '${w.name}' ${w.className} ${w.width}x${w.height}@${w.x},${w.y}" +
            (if (w.attributes.isMapped) "" else " unmapped") + (if (w.isInputOutput) "" else " input-only") + (if (w.type == Window.Type.DIALOG) " dialog" else "") +
            (if (w.isLayered) " layered" else "") + (if (w.attributes.isTransparent) " transparent" else "") + alphaOf(w)
    }

    fun waitFor(what: String, timeoutMs: Long = 60_000, condition: () -> Boolean) {
        val end = System.currentTimeMillis() + timeoutMs
        while (System.currentTimeMillis() < end) {
            if (runCatching(condition).getOrDefault(false)) return
            Thread.sleep(200)
        }
        throw AssertionError("Waited ${timeoutMs / 1000} s for $what.\nWindows:\n${describe()}")
    }

    fun moveTo(x: Int, y: Int) = xServer.injectPointerMove(x, y)

    /**
     * Where on the screen the point [x],[y] of [window] is shown: stretched to the screen when the renderer does that to it (a
     * window smaller than the screen, with the app's "fill the screen" on), at its own place otherwise.
     */
    fun onScreen(window: Window, x: Int, y: Int): Pair<Int, Int> = xServer.lock(XServer.Lockable.WINDOW_MANAGER).use {
        val stretch = window.fullscreenTransformation
        if (stretch != null) {
            Pair(stretch.x + Math.round(x * stretch.width / window.width.toFloat()), stretch.y + Math.round(y * stretch.height / window.height.toFloat()))
        } else Pair(window.rootX + x, window.rootY + y)
    }

    /** The pointer to [x],[y] on the screen, a button pressed and let go, as the app's touch layer does a click (GestureView.click). */
    fun click(x: Int, y: Int, button: Pointer.Button = Pointer.Button.BUTTON_LEFT) {
        xServer.injectPointerMove(x, y)
        Thread.sleep(60)
        xServer.injectPointerButtonPress(button)
        Thread.sleep(40)
        xServer.injectPointerButtonRelease(button)
    }

    /** A key pressed and let go with [held] down, as the app's keyboard does (GestureView.pressKey). */
    fun key(key: XKeycode, vararg held: XKeycode) {
        held.forEach { xServer.injectKeyPress(it) }
        xServer.injectKeyPress(key)
        Thread.sleep(50)
        xServer.injectKeyRelease(key)
        held.reversed().forEach { xServer.injectKeyRelease(it) }
        Thread.sleep(50)
    }

    private fun button(name: String?): Pointer.Button = if (name == "right") Pointer.Button.BUTTON_RIGHT else Pointer.Button.BUTTON_LEFT

    private fun describe(w: Window?): String =
        if (w == null) "none" else "0x${Integer.toHexString(w.id)} '${w.name}' ${w.className} ${w.width}x${w.height}@${w.rootX},${w.rootY}" +
            (if (w.isInputOutput) "" else " input-only") + (w.fullscreenTransformation?.let { " stretched to ${it.width}x${it.height}@${it.x},${it.y}" } ?: "") +
            // What decides how the phone's renderer draws it (GLRenderer.collectRenderableWindows): a layered or transparent
            // window is blended by its own alpha, and one whose pixels carry alpha 0 is then not seen at all.
            (if (w.isLayered) " layered" else "") + (if (w.attributes.isTransparent) " transparent" else "") + alphaOf(w)

    /** " alpha MIN..MAX" of a mapped window's pixels (sampled), "" when it has none. */
    private fun alphaOf(w: Window): String {
        if (!w.attributes.isMapped) return ""
        val content = w.content ?: return ""
        val data = content.data ?: return ""
        val pixels = data.duplicate().order(java.nio.ByteOrder.LITTLE_ENDIAN).asIntBuffer()
        val n = minOf(pixels.capacity(), content.width.toInt() * content.height.toInt())
        if (n <= 0) return ""
        var lo = 255; var hi = 0
        var i = 0
        while (i < n) { val a = pixels.get(i) ushr 24; if (a < lo) lo = a; if (a > hi) hi = a; i += 97 }
        return " alpha $lo..$hi"
    }

    /** Where the pointer is, the window under it, a grab and what it asks for, the focus: what a click would meet. */
    fun state(): String = xServer.lock(XServer.Lockable.WINDOW_MANAGER, XServer.Lockable.INPUT_DEVICE).use {
        val grab = xServer.grabManager
        "pointer ${xServer.pointer.x},${xServer.pointer.y} buttons ${xServer.pointer.buttonMask.bits}\n" +
            "under   ${describe(xServer.inputDeviceManager.pointWindow)}\n" +
            "grab    ${describe(grab.window)}" + (if (grab.window != null) " ownerEvents=${grab.isOwnerEvents} releaseWithButtons=${grab.isReleaseWithButtons} mask=0x${Integer.toHexString(grab.eventListener.eventMask.bits)}" else "") + "\n" +
            "focus   ${describe(xServer.windowManager.focusedWindow)}\n" +
            "cursor  ${xServer.inputDeviceManager.pointWindow?.attributes?.cursor?.let { "${it.cursorImage?.width}x${it.cursorImage?.height} hot ${it.hotSpotX},${it.hotSpotY} id ${System.identityHashCode(it)}" } ?: "none"}"
    }

    /**
     * One command of the hold mode's: `move X Y`, `click X Y [right]`, `dclick X Y`, `down [right]`, `up [right]`,
     * `key NAME [HELD...]` (XKeycode names: KEY_A, KEY_ENTER, KEY_SHIFT_L...), `type TEXT` (letters, digits and spaces),
     * `shot [FILE]`, `pshot [FILE]` (as the phone's renderer shows it: [phoneScreenshot]), `windows`, `state`, `sleep MS`.
     */
    fun command(line: String): String {
        val parts = line.split(Regex("\\s+"))
        return when (parts[0]) {
            "move" -> { moveTo(parts[1].toInt(), parts[2].toInt()); "ok" }
            "click" -> { click(parts[1].toInt(), parts[2].toInt(), button(parts.getOrNull(3))); "ok" }
            "dclick" -> { click(parts[1].toInt(), parts[2].toInt()); Thread.sleep(60); click(parts[1].toInt(), parts[2].toInt()); "ok" }
            "down" -> { xServer.injectPointerButtonPress(button(parts.getOrNull(1))); "ok" }
            "up" -> { xServer.injectPointerButtonRelease(button(parts.getOrNull(1))); "ok" }
            "key" -> { key(XKeycode.valueOf(parts[1]), *parts.drop(2).map { XKeycode.valueOf(it) }.toTypedArray()); "ok" }
            "type" -> {
                for (c in line.substringAfter("type ")) {
                    when {
                        c == ' ' -> key(XKeycode.KEY_SPACE)
                        c.isUpperCase() -> key(XKeycode.valueOf("KEY_$c"), XKeycode.KEY_SHIFT_L)
                        c.isLetterOrDigit() -> key(XKeycode.valueOf("KEY_${c.uppercaseChar()}"))
                    }
                }
                "ok"
            }
            "shot" -> { val f = File(parts.getOrNull(1) ?: "/tmp/xrig-$display-screen.png"); screenshot(f); f.path }
            "pshot" -> { val f = File(parts.getOrNull(1) ?: "/tmp/xrig-$display-phone.png"); phoneScreenshot(f); f.path }
            "windows" -> describe()
            "state" -> state()
            "sleep" -> { Thread.sleep(parts[1].toLong()); "ok" }
            // What the app sends through winhandler: `exec C:\windows\borderless.exe`.
            "exec" -> { winHandler.exec(line.substringAfter("exec ")); "sent" }
            else -> "unknown command"
        }
    }

    /**
     * The screen as the phone's renderer composes it (GLRenderer, with the games' forced full screen): black first, then
     * each renderable window in the server's order; a plain undecorated window smaller than the screen is stretched over
     * it, and a layered or transparent window (or one whose parent is) is blended by its pixels' own alpha, so a window
     * whose pixels carry alpha 0 leaves what is behind it. [screenshot] ignores both and shows what the windows hold.
     */
    fun phoneScreenshot(file: File) {
        val image = BufferedImage(width, height, BufferedImage.TYPE_INT_RGB)
        val root = xServer.windowManager.rootWindow
        xServer.lock(XServer.Lockable.WINDOW_MANAGER, XServer.Lockable.DRAWABLE_MANAGER).use {
            fun draw(w: Window, ox: Int, oy: Int) {
                if (!w.isRenderable) return
                if (w !== root && w.attributes.isViewable) {
                    val parent = w.parent
                    val transparent = w.attributes.isTransparent || parent.attributes.isTransparent || parent.isLayered || w.isLayered
                    val inBounds = w.width >= com.winlator.xserver.ScreenInfo.MIN_WIDTH && w.height >= com.winlator.xserver.ScreenInfo.MIN_HEIGHT &&
                        w.width < width && w.height < height
                    val stretched = w.type == Window.Type.NORMAL && inBounds && w.hasNoDecorations()
                    val content = w.content
                    val data = content?.data
                    if (content != null && data != null) {
                        val pixels = data.duplicate().order(java.nio.ByteOrder.LITTLE_ENDIAN).asIntBuffer()
                        val cw = content.width.toInt(); val ch = content.height.toInt()
                        if (pixels.capacity() >= cw * ch) {
                            // (the stretch keeps the picture's shape, centred: FullscreenTransformation)
                            val scale = if (stretched) minOf(width / cw.toFloat(), height / ch.toFloat()) else 1f
                            val dw = if (stretched) Math.round(cw * scale) else cw
                            val dh = if (stretched) Math.round(ch * scale) else ch
                            val dx = if (stretched) (width - dw) / 2 else ox
                            val dy = if (stretched) (height - dh) / 2 else oy
                            for (y in 0 until dh) {
                                val sy = dy + y
                                if (sy < 0 || sy >= height) continue
                                val py = minOf(ch - 1, (y / scale).toInt())
                                for (x in 0 until dw) {
                                    val sx = dx + x
                                    if (sx < 0 || sx >= width) continue
                                    val src = pixels.get(py * cw + minOf(cw - 1, (x / scale).toInt()))
                                    val alpha = if (transparent) src ushr 24 else 255
                                    if (alpha == 255) { image.setRGB(sx, sy, src and 0xffffff); continue }
                                    if (alpha == 0) continue
                                    val dst = image.getRGB(sx, sy)
                                    fun mix(shift: Int) = (((src ushr shift) and 255) * alpha + ((dst ushr shift) and 255) * (255 - alpha)) / 255
                                    image.setRGB(sx, sy, (mix(16) shl 16) or (mix(8) shl 8) or mix(0))
                                }
                            }
                        }
                    }
                }
                if (w.attributes.isRenderSubwindows) for (c in w.children) draw(c, ox + c.x, oy + c.y)
            }
            draw(root, root.x.toInt(), root.y.toInt())
        }
        file.parentFile?.mkdirs()
        ImageIO.write(image, "png", file)
    }

    /** What the server holds of its mapped windows, drawn one over the other as the phone's screen would show them, as a PNG. */
    fun screenshot(file: File) {
        val image = BufferedImage(width, height, BufferedImage.TYPE_INT_RGB)
        xServer.lock(XServer.Lockable.WINDOW_MANAGER, XServer.Lockable.DRAWABLE_MANAGER).use {
            fun draw(w: Window, ox: Int, oy: Int) {
                if (!w.attributes.isMapped) return
                val content = w.content
                val data = content?.data
                if (content != null && data != null) {
                    val pixels = data.duplicate().order(java.nio.ByteOrder.LITTLE_ENDIAN).asIntBuffer()
                    val cw = content.width.toInt()
                    val ch = content.height.toInt()
                    if (pixels.capacity() >= cw * ch) {
                        for (y in 0 until ch) {
                            val sy = oy + y
                            if (sy < 0 || sy >= height) continue
                            for (x in 0 until cw) {
                                val sx = ox + x
                                if (sx < 0 || sx >= width) continue
                                image.setRGB(sx, sy, pixels.get(y * cw + x) and 0xffffff)
                            }
                        }
                    }
                }
                for (c in w.children) draw(c, ox + c.x, oy + c.y)
            }
            draw(xServer.windowManager.rootWindow, 0, 0)
        }
        file.parentFile?.mkdirs()
        ImageIO.write(image, "png", file)
    }

    override fun close() {
        runCatching { winHandler.stop() }
        wineserver("-k")
        started.forEach { runCatching { it.destroyForcibly() } }
        runCatching { x.stop() }
        runCatching { shm.stop() }
        runCatching { Files.deleteIfExists(link.toPath()) }
    }
}

/** This machine's own shared memory segments (System V), mapped for the server by number (tools/xrig/stubs/host.c). */
object HostShm {
    init { System.loadLibrary("winlator") }
    @JvmStatic external fun attach(shmid: Int): java.nio.ByteBuffer?
    @JvmStatic external fun detach(data: java.nio.ByteBuffer)
}

/** Winlator's shared memory, with the kernel's segments for the numbers it does not know itself (what Wine's X library uses on a desktop). */
class HostSharedMemory(private val service: com.winlator.sysvshm.SysVSharedMemory) : com.winlator.sysvshm.SysVSharedMemory() {
    private val attached = HashMap<Int, java.nio.ByteBuffer>()

    override fun attach(shmid: Int): java.nio.ByteBuffer? = service.attach(shmid) ?: synchronized(attached) {
        attached[shmid] ?: HostShm.attach(shmid)?.also { attached[shmid] = it }
    }

    override fun detach(data: java.nio.ByteBuffer) {
        val mine = synchronized(attached) {
            val key = attached.entries.firstOrNull { it.value === data }?.key
            if (key != null) attached.remove(key)
            key != null
        }
        if (mine) HostShm.detach(data) else service.detach(data)
    }
}
