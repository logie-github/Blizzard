package com.logie.blizz.game

import android.content.Context
import android.content.SharedPreferences

/**
 * A game's launch options: the graphics and speed settings of the Windows it runs in, which the
 * person can change on the phone (the game's hold menu and page: [com.logie.blizz.ui.GameOptionsDialog])
 * without waiting for a release when a game shows a black screen or runs slowly. Nothing here has
 * been tried on a phone, so these are the tool for finding what works.
 *
 * Every choice has a `DEFAULT`, which means "what the app judges best for this game"
 * ([resolve]); [safeMode] picks the most conservative of everything at once. Plain Kotlin apart
 * from [LaunchOptionsStore]; unit-tested.
 *
 * Applied by [WindowsRuntime] at every start. The games share one Windows (the "Blizzard" container),
 * so each start writes every value, the defaults included, never leaving the last game's behind.
 */
data class LaunchOptions(
    val safeMode: Boolean = false,
    val ddraw: DDraw = DDraw.DEFAULT,
    val box64: Box64.Preset = Box64.Preset.DEFAULT,
    val fps: Fps = Fps.DEFAULT,
    val vsync: Tri = Tri.DEFAULT,
    val singleCpu: Tri = Tri.DEFAULT,
    val redraw: Tri = Tri.DEFAULT,
) {
    /** Which DirectDraw the classic 2D games draw with (cnc-ddraw's renderers, or Wine's own). */
    enum class DDraw(val label: String, val note: String) {
        DEFAULT("Default", "Best guess for the game (OpenGL for the classic games)."),
        WINE("Wine's own", "No wrapper; Wine's DirectDraw. Slow, and plays no videos on some phones."),
        GDI("cnc-ddraw: GDI", "Software drawing; needs no OpenGL or Direct3D. The most likely to show something."),
        OPENGL("cnc-ddraw: OpenGL", "Drawn by the GPU through OpenGL."),
        D3D9("cnc-ddraw: Direct3D 9", "Drawn through Direct3D 9 (DXVK, so Vulkan).");
    }

    /** Box64's speed/safety preset, Winlator's own names (Box64Preset): slowest and safest first. */
    object Box64 {
        enum class Preset(val label: String, val id: String?) {
            DEFAULT("Default", null),
            STABILITY("Stability", "STABILITY"),
            COMPATIBLE("Compatible", "CONSERVATIVE"),
            INTERMEDIATE("Intermediate", "INTERMEDIATE"),
            PERFORMANCE("Performance", "PERFORMANCE");
        }
    }

    /** cnc-ddraw's `maxfps`: how often the picture is drawn (the game's own speed is not changed). */
    enum class Fps(val label: String, val value: Int?) {
        DEFAULT("Default", null),
        FPS_30("30", 30),
        FPS_60("60", 60),
        UNLIMITED("No limit", 0);
    }

    enum class Tri { DEFAULT, ON, OFF;
        /** The choice, or [default] when it is [DEFAULT]. */
        fun or(default: Boolean) = when (this) { DEFAULT -> default; ON -> true; OFF -> false }
    }

    /** What the phone is: its GPU makes the driver (read at the start, see [com.logie.blizz.game.WindowsRuntime]). */
    data class Hardware(val adreno: Boolean = false)

    /** Every value the options come to for a game, nothing left to a default. */
    data class Resolved(
        /** "cnc-ddraw" or null (Wine's own DirectDraw). */
        val ddrawWrapper: String?,
        /** cnc-ddraw's renderer: gdi, opengl or direct3d9 (meaningless without the wrapper). */
        val renderer: String,
        /** Box64 preset id (Winlator's). */
        val box64Preset: String,
        /** The container's graphics driver: "vulkan,opengl". */
        val graphicsDriver: String,
        /** The container's Direct3D layer: dxvk or wined3d. */
        val dxwrapper: String,
        /** The phone-shaped screen's lines, or null for the game's own size. */
        val lines: Int?,
        val maxFps: Int,
        val vsync: Boolean,
        val singleCpu: Boolean,
        /** cnc-ddraw `nonexclusive` and `minfps`: for videos, menus and loading screens that stay invisible. */
        val redraw: Boolean,
        /** The graphics card DXVK tells the game it has ("device:vendor:name", Winlator's customDevice), or null for the phone's own. */
        val customDevice: String? = null,
    ) {
        /** The container's `dxwrapperConfig` (a Winlator KeyValueSet). */
        val dxwrapperConfig: String get() = listOfNotNull(ddrawWrapper?.let { "ddrawWrapper=$it" }, customDevice?.let { "customDevice=$it" }).joinToString(",")

        /** Everything Winlator caches per container, so a change can be told from the last start. */
        val cacheKey: String get() = "$dxwrapper|$dxwrapperConfig|$graphicsDriver|$box64Preset"
    }

    /** The options as they apply to [gameId]: defaults filled in, [safeMode] and what the game can't use applied. */
    fun resolve(gameId: String, hardware: Hardware = Hardware()): Resolved {
        val key = key(gameId)
        val classic = isClassic(key)
        val s = safeMode
        // WHY these defaults (Diablo II, StarCraft, Warcraft II), from cnc-ddraw's own ddraw.ini notes
        // and the first phone reports (StarCraft: black screen and no sound; Diablo II: no videos, ~3 fps):
        //  - singlecpu=false. "Force CPU0 affinity ... disable if the game is not running smooth or there
        //    are sound issues": on a phone CPU0 is a slow efficiency core, and under Box64 the whole of Wine
        //    shares it, which is both the 3 fps and the audio that never starts. The first release had it on.
        //  - renderer opengl, not gdi: GDI drew and stretched every frame in emulated software; OpenGL
        //    lets the GPU do it. GDI stays a choice (and is Safe mode's), as it needs no GL at all.
        //  - borderless fullscreen (windowed=true + fullscreen=true), not exclusive fullscreen: Wine has
        //    no display modes to switch to on Winlator's X server, which exclusive mode asks for.
        //  - redraw on: nonexclusive "in case videos are invisible" and minfps "if parts of the game are
        //    not displayed (menus, loading screens)" are cnc-ddraw's two cures for Diablo II's missing
        //    movies and a black first screen. (nonexclusive does nothing for the GDI renderer.)
        //  - Box64 Intermediate: 1998-2000 games are light for the CPU, so the strict float/flag
        //    handling of Intermediate costs little and Performance's fast-round and no-x87-double is the
        //    likeliest cause of a crash that leaves a black screen.
        val wrapper = when {
            !classic -> null
            s -> "cnc-ddraw"
            ddraw == DDraw.WINE -> null
            else -> "cnc-ddraw"
        }
        val renderer = when {
            s -> "gdi"
            ddraw == DDraw.GDI -> "gdi"
            ddraw == DDraw.D3D9 -> "direct3d9"
            else -> "opengl"
        }
        val preset = when {
            s -> Box64.Preset.STABILITY.id!!
            box64.id != null -> box64.id
            // Diablo II 1.13 died inside Fog.dll (a stack overflow at its window's creation) under Intermediate: the safest preset.
            key == "diablo2" -> Box64.Preset.STABILITY.id!!
            classic -> Box64.Preset.INTERMEDIATE.id!!
            else -> Box64.Preset.PERFORMANCE.id!! // Winlator's own default (Box64Preset.DEFAULT)
        }
        return Resolved(
            ddrawWrapper = wrapper,
            renderer = renderer,
            box64Preset = preset,
            // Chosen by the app, never per game: Turnip on an Adreno GPU (Snapdragon, the Fold's), Vortek
            // elsewhere; DXVK for Direct3D. Safe mode keeps Winlator's own defaults.
            graphicsDriver = if (!s && hardware.adreno) TURNIP_DRIVER else DEFAULT_DRIVER,
            dxwrapper = DEFAULT_D3D,
            // As many lines as the screen has, always.
            lines = if (s || resolutionLocked(key)) null else Screen.MOST,
            maxFps = if (s) 30 else fps.value ?: 60,
            vsync = if (s) false else vsync.or(false),
            singleCpu = if (s) false else singleCpu.or(false),
            redraw = if (s) true else redraw.or(true),
            // On the Fold's Adreno, the games are told of a desktop card they know (a Radeon RX 6800 XT): one that never
            // changes between starts and that their own checks count as supported, so they pick their best settings and
            // show no "hardware changed" or "unsupported driver" message. Safe mode reports the phone's own.
            customDevice = if (!s && hardware.adreno) DESKTOP_CARD else null,
        )
    }

    /** cnc-ddraw's `ddraw.ini` for [gameId], or null when it isn't drawn through cnc-ddraw. */
    fun ddrawIni(gameId: String): String? = ddrawIni(resolve(gameId), key(gameId))

    companion object {
        /** Winlator's defaults for a new container (Container(0)): Vortek and Gladio, DXVK. */
        const val DEFAULT_DRIVER = "vortek,gladio"
        const val DEFAULT_D3D = "dxvk"
        const val TURNIP_DRIVER = "turnip,gladio"
        const val DESKTOP_CARD = "73bf:1002:AMD Radeon RX 6800 XT"

        /** The classic 2D games, which draw with DirectDraw. */
        val CLASSIC = setOf("diablo2", "starcraft", "warcraft2")

        /** Warcraft I and II are played natively (Stratagus), not in Windows: no options. */
        val NATIVE = setOf("warcraft", "warcraft2", "diablo2_resurrected", "wow_legion", "wow_octowow", "wow_forever")

        /** The WoW client's library entry ("wow-client") is the shelf's World of Warcraft. */
        fun key(gameId: String) = gameId.removeSuffix("-client")

        fun isClassic(gameId: String) = key(gameId) in CLASSIC

        fun hasOptions(gameId: String) = key(gameId) !in NATIVE

        /** The classic and Diablo's windows are their own size; stretching them is cnc-ddraw's and Winlator's job. */
        fun resolutionLocked(gameId: String) = LaunchProfile.of(key(gameId)).fixedSize != null || isClassic(gameId)

        fun ddrawIni(r: Resolved, gameId: String): String? {
            if (r.ddrawWrapper == null) return null
            val text = StringBuilder("[ddraw]\n")
            fun put(k: String, v: Any) { text.append(k).append('=').append(v).append('\n') }
            put("renderer", r.renderer)
            // Borderless fullscreen, the game's shape kept; see resolve().
            put("fullscreen", true)
            put("windowed", true)
            put("border", false)
            put("maintas", true)
            put("boxing", false)
            put("adjmouse", true)
            put("shader", "Nearest neighbor")
            put("vsync", r.vsync)
            put("maxfps", r.maxFps)
            put("singlecpu", r.singleCpu)
            put("nonexclusive", r.redraw)
            put("minfps", if (r.redraw) -1 else 0)
            put("noactivateapp", false)
            put("hook_peekmessage", false)
            put("savesettings", 0) // the window is the screen: nothing worth remembering between starts
            if (key(gameId) == "starcraft") text.append("\n[StarCraft]\ngame_handles_close=true\n")
            return text.toString()
        }
    }
}

/** The options kept per game in SharedPreferences: one key per choice, `<game>.<choice>`, the enum's name. */
class LaunchOptionsStore(private val prefs: SharedPreferences) {
    constructor(context: Context) : this(context.getSharedPreferences(PREFS, Context.MODE_PRIVATE))

    fun get(gameId: String): LaunchOptions {
        val g = LaunchOptions.key(gameId)
        fun <T : Enum<T>> read(field: String, values: Array<T>, fallback: T): T {
            val name = prefs.getString("$g.$field", null) ?: return fallback
            return values.firstOrNull { it.name == name } ?: fallback
        }
        return LaunchOptions(
            safeMode = prefs.getBoolean("$g.safe", false),
            ddraw = read("ddraw", LaunchOptions.DDraw.entries.toTypedArray(), LaunchOptions.DDraw.DEFAULT),
            box64 = read("box64", LaunchOptions.Box64.Preset.entries.toTypedArray(), LaunchOptions.Box64.Preset.DEFAULT),
            fps = read("fps", LaunchOptions.Fps.entries.toTypedArray(), LaunchOptions.Fps.DEFAULT),
            vsync = read("vsync", LaunchOptions.Tri.entries.toTypedArray(), LaunchOptions.Tri.DEFAULT),
            singleCpu = read("singlecpu", LaunchOptions.Tri.entries.toTypedArray(), LaunchOptions.Tri.DEFAULT),
            redraw = read("redraw", LaunchOptions.Tri.entries.toTypedArray(), LaunchOptions.Tri.DEFAULT),
        )
    }

    fun set(gameId: String, o: LaunchOptions) {
        val g = LaunchOptions.key(gameId)
        prefs.edit()
            .putBoolean("$g.safe", o.safeMode)
            .putString("$g.ddraw", o.ddraw.name)
            .putString("$g.box64", o.box64.name)
            .putString("$g.fps", o.fps.name)
            .putString("$g.vsync", o.vsync.name)
            .putString("$g.singlecpu", o.singleCpu.name)
            .putString("$g.redraw", o.redraw.name)
            .apply()
    }

    /** Back to the defaults. */
    fun reset(gameId: String) {
        val g = LaunchOptions.key(gameId)
        val e = prefs.edit()
        prefs.all.keys.filter { it.startsWith("$g.") }.forEach { e.remove(it) }
        e.apply()
    }

    /** What the last start of the game applied ([LaunchOptions.Resolved.cacheKey]), to tell a change. */
    fun lastApplied(): String? = prefs.getString(APPLIED, null)

    fun setLastApplied(key: String) {
        prefs.edit().putString(APPLIED, key).apply()
    }

    companion object {
        private const val PREFS = "launch_options"
        private const val APPLIED = "applied"
    }
}
