package com.logie.blizz.forever.arm64

import android.content.Context
import android.os.Build
import com.logie.blizz.forever.tact.Blte
import com.logie.blizz.forever.tact.BlteInputStream
import com.logie.blizz.forever.tact.Key16
import com.logie.blizz.forever.tact.Tact
import com.logie.blizz.forever.tact.TactCdn
import com.logie.blizz.forever.tact.Verify
import com.winlator.core.TarCompressorUtils
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.zip.ZipInputStream

/**
 * World of Warcraft: Forever on its Windows ARM64 client (`Wow-ARM64.exe`), run natively on the phone's CPU in the
 * Android-native (bionic) Wine container jaredgei/wow-forever-android runs it in (GameNative's, GPL-3.0): Proton 11 ARM64EC,
 * DXVK 2.4.1 for aarch64, Turnip through a Vulkan wrapper. No Box64: the PC client through Box64 never drew a window on the
 * phone (reports 174 to 181, 14 November 2026). Only the container comes in; the game screen, touch controls, keeper, sign-in
 * and realm stay this app's.
 *
 * - [Runtime]: the container's files from this repository's release [RELEASE] only (`mirror-forever-arm64.yml` copies them
 *   there once), each checked against its `SHA256SUMS`, laid out the way the container's own libraries expect: the image at
 *   `files/imagefs` (its redirect library computes that path from the package name), Proton at
 *   `files/imagefs_shared/proton/<version>`.
 * - [Prefix]: the Windows prefix from Proton's `prefixPack.txz`, Proton's ARM64 and 32-bit Windows libraries copied in, DXVK
 *   from its `profile.json`, drive G: at the game.
 * - [Client]: the ARM64 client's own programs, added to an installed client of the same build (the game's data is shared).
 * - [Launch]: the environment and the `/system/bin/linker64` command the game screen runs (Winlator patch 0010).
 *
 * Not run on a phone: this machine runs neither Android nor its Wine. Each step logs what it did for the reports.
 */
object ForeverArm64 {
    const val RELEASE = "forever-arm64-runtime-1"
    const val BASE = "https://github.com/logie-github/Blizzard/releases/download/$RELEASE"
    const val PROTON = "proton-11.0-90624-arm64ec"
    const val EXE = "Wow-ARM64.exe"

    /** Where everything goes, under the app's `files` folder. */
    class Layout(val files: File) {
        val imagefs = File(files, "imagefs")
        val proton = File(files, "imagefs_shared/proton/$PROTON")
        val home = File(imagefs, "home/xuser")
        val prefix = File(home, ".wine")
        val windows = File(prefix, "drive_c/windows")
        val system32 = File(windows, "system32")
        val syswow64 = File(windows, "syswow64")
        val root = File(files, "forever-arm64")
        val dxvk = File(root, "dxvk")
        val libs = File(root, "lib")
        val kept = File(root, "kept")
        val markers = File(root, "installed")
        val downloads = File(root, "download")
        fun turnip(zip: String) = File(root, "turnip/" + zip.removeSuffix(".zip"))
        companion object { fun of(context: Context) = Layout(context.applicationContext.filesDir) }
    }

    /** Where a part of the runtime goes. */
    enum class Into { IMAGE, IMAGEFS, IMAGE_LIB, PROTON, DXVK, TURNIP, LIB, KEEP }

    data class Part(val name: String, val into: Into)

    /** The runtime, in the order it is put in place (the image first: the parts after it go into it). */
    val PARTS = listOf(
        Part("imagefs_bionic.txz", Into.IMAGE),
        Part("redirect.tzst", Into.IMAGEFS),
        Part("extras.tzst", Into.IMAGEFS),
        Part("wrapper.tzst", Into.IMAGEFS),
        Part("extra_libs.tzst", Into.IMAGEFS),
        Part("libredirect-bionic-wx.so", Into.IMAGE_LIB),
        Part("libredirect-bionic-wx-minimal.so", Into.IMAGE_LIB),
        Part("$PROTON.wcp", Into.PROTON),
        Part("dxvk-2.4.1-wow-aarch64-test.wcp", Into.DXVK),
        Part(TURNIP_740, Into.TURNIP),
        Part(TURNIP_8XX, Into.TURNIP),
        Part("container_pattern_common_20260821.tzst", Into.KEEP),
        Part("wowbox64-0.4.2.tzst", Into.KEEP),
        Part("libgamenative_dns_v4mapped.so", Into.LIB),
        Part("libc++_shared.so", Into.LIB),
    )
    const val TURNIP_740 = "turnip-wow-scheduler-test.zip"
    const val TURNIP_8XX = "turnip-V32-RP6sched.zip"

    /** `SHA256SUMS` (`hash  name` per line) as name to hash. */
    fun parseSums(text: String): Map<String, String> = text.lineSequence()
        .map { it.trim().split(Regex("\\s+")) }
        .filter { it.size == 2 && it[0].length == 64 }
        .associate { it[1].removePrefix("*") to it[0].lowercase() }

    /** Snapdragon 8 Elite and later (Adreno 8xx): the Turnip and settings jaredgei/wow-forever-android gives them. */
    fun isAdreno8xx(socModel: String?, hardware: String?): Boolean =
        socModel?.uppercase() in setOf("SM8735", "SM8750", "SM8845", "SM8850") || hardware.equals("sun", ignoreCase = true)

    fun adreno8xx(): Boolean = isAdreno8xx(if (Build.VERSION.SDK_INT >= 31) Build.SOC_MODEL else null, Build.HARDWARE)

    /** The Turnip for this phone's GPU. */
    fun turnipZip(adreno8: Boolean) = if (adreno8) TURNIP_8XX else TURNIP_740

    // Runtime ----------------------------------------------------------------------------------------------------------

    object Runtime {
        /**
         * Puts every [PARTS] file in place that isn't yet (by its hash): downloads it from [BASE], checks it against
         * `SHA256SUMS`, unpacks it where it goes, keeps a marker. A new image clears the image's other parts and the prefix
         * in it. [onStep] gets a line per step and its share done.
         */
        fun install(layout: Layout, onStep: (String, Float?) -> Unit, fetch: (String) -> ByteArray = ::httpBytes, download: (String, File) -> Unit = ::httpDownload) {
            onStep("Checking the game's runtime", null)
            val sums = parseSums(String(fetch("$BASE/SHA256SUMS"), Charsets.UTF_8))
            layout.markers.mkdirs(); layout.downloads.mkdirs()
            for ((i, part) in PARTS.withIndex()) {
                val sha = sums[part.name] ?: throw IOException("${part.name} isn't in $RELEASE's SHA256SUMS")
                val marker = File(layout.markers, part.name)
                if (marker.isFile && marker.readText().trim() == sha) continue
                onStep("Getting the game's runtime (${i + 1} of ${PARTS.size})", i.toFloat() / PARTS.size)
                val file = File(layout.downloads, part.name)
                if (!(file.isFile && sha256(file) == sha)) {
                    download("$BASE/${part.name}", file)
                    val got = sha256(file)
                    if (got != sha) { file.delete(); throw IOException("${part.name} came with the wrong content ($got)") }
                }
                place(layout, part, file)
                marker.writeText(sha)
                file.delete()
            }
        }

        private fun place(layout: Layout, part: Part, file: File) {
            when (part.into) {
                Into.IMAGE -> {
                    layout.imagefs.deleteRecursively(); layout.imagefs.mkdirs()
                    // Everything that went into the old image goes in again.
                    PARTS.filter { it.into == Into.IMAGEFS || it.into == Into.IMAGE_LIB }.forEach { File(layout.markers, it.name).delete() }
                    untar(TarCompressorUtils.Type.XZ, file, layout.imagefs)
                }
                Into.IMAGEFS -> untar(TarCompressorUtils.Type.ZSTD, file, layout.imagefs)
                Into.IMAGE_LIB -> copyExecutable(file, File(layout.imagefs, "usr/lib/${part.name}"))
                Into.PROTON -> {
                    layout.proton.deleteRecursively(); layout.proton.mkdirs()
                    untar(TarCompressorUtils.Type.ZSTD, file, layout.proton)
                    // bin/wine and the rest are links into lib/wine/aarch64-unix, where the programs are.
                    for (dir in listOf("bin", "lib/wine/aarch64-unix")) layout.proton.resolve(dir).listFiles()?.forEach { it.setExecutable(true, false) }
                }
                Into.DXVK -> { layout.dxvk.deleteRecursively(); layout.dxvk.mkdirs(); untar(TarCompressorUtils.Type.ZSTD, file, layout.dxvk) }
                Into.TURNIP -> { val dir = layout.turnip(part.name); dir.deleteRecursively(); unzip(file, dir) }
                Into.LIB -> copyExecutable(file, File(layout.libs, part.name))
                Into.KEEP -> file.copyTo(File(layout.kept, part.name), overwrite = true)
            }
        }

        private fun untar(type: TarCompressorUtils.Type, file: File, into: File) {
            if (!TarCompressorUtils.extract(type, file, into)) throw IOException("${file.name} couldn't be unpacked")
        }

        private fun copyExecutable(from: File, to: File) {
            to.parentFile?.mkdirs(); from.copyTo(to, overwrite = true); to.setExecutable(true, false)
        }
    }

    internal fun unzip(zip: File, into: File) {
        into.mkdirs()
        val base = into.canonicalPath + File.separator
        ZipInputStream(zip.inputStream().buffered()).use { z ->
            while (true) {
                val e = z.nextEntry ?: break
                val out = File(into, e.name)
                if (!out.canonicalPath.startsWith(base)) throw IOException("${zip.name}: ${e.name} points outside")
                if (e.isDirectory) out.mkdirs() else { out.parentFile?.mkdirs(); out.outputStream().use { z.copyTo(it) } }
            }
        }
    }

    fun sha256(file: File): String {
        val d = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input -> val b = ByteArray(1 shl 20); while (true) { val n = input.read(b); if (n < 0) break; d.update(b, 0, n) } }
        return d.digest().joinToString("") { "%02x".format(it) }
    }

    private fun connect(url: String): HttpURLConnection {
        var u = URL(url)
        repeat(6) {
            val c = (u.openConnection() as HttpURLConnection).apply { instanceFollowRedirects = false; connectTimeout = 20_000; readTimeout = 60_000 }
            val code = c.responseCode
            if (code in 300..399) { u = URL(u, c.getHeaderField("Location")); c.disconnect() } else if (code == 200) return c else throw IOException("$url answered $code")
        }
        throw IOException("$url: too many redirects")
    }

    fun httpBytes(url: String): ByteArray = connect(url).let { c -> try { c.inputStream.use { it.readBytes() } } finally { c.disconnect() } }

    fun httpDownload(url: String, to: File) {
        val part = File(to.path + ".part")
        val c = connect(url)
        try { c.inputStream.use { input -> part.outputStream().use { input.copyTo(it, 1 shl 20) } } } finally { c.disconnect() }
        to.delete(); if (!part.renameTo(to)) throw IOException("Couldn't place ${to.name}")
    }

    // Prefix -----------------------------------------------------------------------------------------------------------

    object Prefix {
        /**
         * The Windows prefix, made once from Proton's `prefixPack.txz` (Proton's ARM64 and 32-bit libraries in it, the
         * common files over it), then at every start: DXVK's files from its `profile.json`, wowbox64, drive G: at [game]
         * (the client folder: `G:\_forever_\Wow-ARM64.exe`), and [extras] (name in `C:\windows` to its bytes).
         */
        fun ensure(layout: Layout, game: File, extras: Map<String, ByteArray> = emptyMap()) {
            if (!File(layout.prefix, "system.reg").isFile) {
                layout.home.mkdirs()
                val pack = File(layout.proton, "prefixPack.txz")
                if (!TarCompressorUtils.extract(TarCompressorUtils.Type.XZ, pack, layout.home)) throw IOException("Proton's prefixPack couldn't be unpacked")
                copyMissing(File(layout.proton, "lib/wine/aarch64-windows"), layout.system32)
                copyMissing(File(layout.proton, "lib/wine/i386-windows"), layout.syswow64)
                File(layout.kept, "container_pattern_common_20260821.tzst").takeIf { it.isFile }?.let {
                    TarCompressorUtils.extract(TarCompressorUtils.Type.ZSTD, it, layout.home)
                }
            }
            for ((source, target) in dxvkFiles(File(layout.dxvk, "profile.json").readText())) {
                File(layout.dxvk, source).copyTo(File(target.replace("\${system32}", layout.system32.path)), overwrite = true)
            }
            File(layout.kept, "wowbox64-0.4.2.tzst").takeIf { it.isFile }?.let { TarCompressorUtils.extract(TarCompressorUtils.Type.ZSTD, it, layout.system32) }
            val g = File(layout.prefix, "dosdevices/g:")
            g.parentFile?.mkdirs()
            if (g.exists() || runCatching { java.nio.file.Files.isSymbolicLink(g.toPath()) }.getOrDefault(false)) g.delete()
            java.nio.file.Files.createSymbolicLink(g.toPath(), game.toPath())
            for ((name, bytes) in extras) File(layout.windows, name).writeBytes(bytes)
        }

        private fun copyMissing(from: File, to: File) {
            to.mkdirs()
            from.listFiles()?.filter { it.isFile }?.forEach { f -> File(to, f.name).let { if (!it.exists()) f.copyTo(it) } }
        }
    }

    /** A content package's files (`profile.json`): source in the package to target (`${system32}/...`). */
    fun dxvkFiles(profileJson: String): List<Pair<String, String>> {
        val files = JSONObject(profileJson).getJSONArray("files")
        return (0 until files.length()).map { files.getJSONObject(it).let { f -> f.getString("source") to f.getString("target") } }
    }

    // Client -----------------------------------------------------------------------------------------------------------

    object Client {
        /** The ARM64 client's own programs (Windows, arm64): the install manifest's files of those tags. */
        val TAGS = setOf("Windows", "arm64", "enUS", "US")

        /**
         * Puts the ARM64 client's programs into [client]'s game folder (`_forever_`), next to the PC client's: same build,
         * same data (`Data/`), only the programs differ. Each checked by its content key (MD5). Files already right are kept.
         */
        fun install(client: File, onStep: (String) -> Unit, cdn: TactCdn = TactCdn()) {
            onStep("Getting the game's ARM64 program")
            val version = cdn.version()
            val build = Tact.parseConfig(String(cdn.get("config", version.buildConfig) { Verify.config(it, version.buildConfig) }, Charsets.UTF_8))
            val cdnConfig = Tact.parseConfig(String(cdn.get("config", version.cdnConfig) { Verify.config(it, version.cdnConfig) }, Charsets.UTF_8))
            val installKey = Key16.hex(build.getValue("install")[1])
            val install = Tact.parseInstall(Blte.decode(cdn.get("data", installKey.hex()) { Verify.blte(it, installKey) }))
            val selection = install.tags.select(TAGS, emptySet())
            val game = File(client, "_forever_")
            val wanted = install.files.filterIndexed { i, f -> selection.selects(i) && !(File(game, f.name.replace('\\', '/')).let { it.isFile && md5(it) == f.contentKey.hex() }) }
            if (wanted.isEmpty()) return
            val encodingKey = Key16.hex(build.getValue("encoding")[1])
            val staging = File(client, ".blizz-arm64").apply { mkdirs() }
            val encoding = File(staging, "encoding.blte")
            if (!encoding.isFile) cdn.download(encodingKey.hex(), build["encoding-size"]?.getOrNull(1)?.toLongOrNull() ?: 0L, encoding, 8)
            val encoded = BlteInputStream(encoding.inputStream().buffered(1 shl 20)).use { Tact.encodingKeys(it, wanted.map { it.contentKey }.toSet()) }
            // Where each is: an archive (the indexes the installed client has, else the CDN's).
            val where = HashMap<Key16, Triple<String, Long, Long>>()
            val keys = wanted.mapNotNull { encoded[it.contentKey] }.toSet()
            for (archive in cdnConfig.getValue("archives")) {
                if (where.size == keys.size) break
                val local = File(client, "Data/indices/$archive.index")
                val bytes = if (local.isFile) local.readBytes() else cdn.get("data", archive, ".index") { Verify.index(it, archive) }
                Tact.parseIndex(bytes) { data, o, size, offset ->
                    val k = Key16.of(data, o)
                    if (k in keys && k !in where) where[k] = Triple(archive, offset, size)
                }
            }
            for (f in wanted) {
                val ekey = encoded[f.contentKey] ?: throw IOException("The encoding table has no ${f.name}")
                onStep("Getting ${f.name}")
                val bytes = where[ekey]?.let { (archive, offset, size) -> cdn.open(archive, offset, size, 0).use { it.readBytes() } }
                    ?: cdn.get("data", ekey.hex()) { Verify.blte(it, ekey) }
                val content = Blte.decode(bytes)
                if (md5(content) != f.contentKey.hex()) throw IOException("${f.name} came with the wrong content")
                val target = File(game, f.name.replace('\\', '/'))
                target.parentFile?.mkdirs()
                File(target.path + ".part").apply { writeBytes(content); if (!renameTo(target)) { target.delete(); renameTo(target) } }
            }
            staging.deleteRecursively()
        }

        fun has(client: File) = File(client, "_forever_/$EXE").isFile

        private fun md5(f: File): String = f.inputStream().use { input ->
            val d = MessageDigest.getInstance("MD5"); val b = ByteArray(1 shl 20)
            while (true) { val n = input.read(b); if (n < 0) break; d.update(b, 0, n) }
            d.digest().joinToString("") { "%02x".format(it) }
        }
        private fun md5(b: ByteArray) = MessageDigest.getInstance("MD5").digest(b).joinToString("") { "%02x".format(it) }
    }

    // Launch -----------------------------------------------------------------------------------------------------------

    /**
     * The environment the game's Wine runs with (`NAME=value`), after GameNative's bionic launcher and jaredgei's WoW container,
     * with real paths in place of the redirect library's guest ones. [winRoot] is the session's Winlator root, whose servers
     * (shared memory; the X server through `imagefs/tmp/.X11-unix`; sound by PULSE_SERVER, set by the game screen) the game uses.
     */
    fun environment(layout: Layout, winRoot: String, packageName: String, turnip: File, turnipLibrary: String, adreno8: Boolean, samsung: Boolean,
                    vkPatch: Int = 0): List<String> {
        val root = layout.imagefs.path
        val wine = layout.proton.path
        val env = linkedMapOf(
            "HOME" to layout.home.path,
            "USER" to "xuser",
            "WINEPREFIX" to layout.prefix.path,
            "TMPDIR" to "$root/usr/tmp",
            "DISPLAY" to ":0",
            "PATH" to "$wine/bin:$root/usr/bin",
            "LD_LIBRARY_PATH" to "$root/usr/lib:/system/lib64:$wine/lib:${layout.libs.path}",
            "REDIRECT_EXEC__PROC_SELF_EXE" to "$wine/bin/wine",
            "WINEMU_HOST_PKG" to packageName,
            "HOST_PKG" to packageName,
            "ANDROID_SYSVSHM_SERVER" to "$winRoot/tmp/.sysvshm/SM0",
            "FONTCONFIG_PATH" to "$root/usr/etc/fonts",
            "XDG_DATA_DIRS" to "$root/usr/share",
            "XDG_CONFIG_DIRS" to "$root/usr/etc/xdg",
            "VK_LAYER_PATH" to "$root/usr/share/vulkan/implicit_layer.d:$root/usr/share/vulkan/explicit_layer.d",
            "PREFIX" to "$root/usr",
            "OPENSSL_CONF" to "$root/usr/etc/tls/openssl.cnf",
            "SSL_CERT_FILE" to "$root/usr/etc/tls/cert.pem",
            "SSL_CERT_DIR" to "$root/usr/etc/tls/certs",
            "WINE_ADDITIONAL_CERTS_DIR" to "$root/usr/etc/tls/cert.pem",
            // Sound: ALSA's configuration and its plugin for the session's sound server (ANDROID_ALSA_SERVER, from the session).
            // GameNative's launcher sets these; without them Wine's ALSA said "Cannot access file .../alsa.conf" and "Unknown
            // PCM default", and the game's main thread then stood still for a minute at its sixth frame (report 212).
            "ALSA_CONFIG_PATH" to "$root/usr/share/alsa/alsa.conf:$root/usr/etc/alsa/conf.d/android_aserver.conf",
            "ALSA_PLUGIN_DIR" to "$root/usr/lib/alsa-lib",
            "PULSE_LATENCY_MSEC" to "144",
            // The rest of GameNative's launcher's and its WoW container's environment.
            "GST_PLUGIN_PATH" to "$root/usr/lib/gstreamer-1.0",
            "GST_PLUGIN_FEATURE_RANK" to "ximagesink:3000",
            "WINE_GST_NO_GL" to "1",
            "WINE_X11FORCEGLX" to "1",
            "ENABLE_UTIL_LAYER" to "1",
            "SteamGameId" to "0",
            "ZINK_DESCRIPTORS" to "lazy",
            "ZINK_DEBUG" to "compact,deck_emu",
            "mesa_glthread" to "true",
            "WINE_NO_DUPLICATE_EXPLORER" to "1",
            "WINE_DISABLE_FULLSCREEN_HACK" to "1",
            "WINE_NEW_NDIS" to "1",
            "ANDROID_RESOLV_DNS" to "8.8.4.4",
            "HODLL" to "wowbox64.dll",
            // The names in the image's hosts file (the realm's): Android's resolver never reads it (tools/hostsfix).
            "BLIZZ_HOSTS" to "$root/etc/hosts",
            // Each name it answers goes into Wine's output, which the reports carry.
            "BLIZZ_HOSTS_LOG" to "1",
            "LD_PRELOAD" to listOf("${layout.libs.path}/$HOSTS_ASSET", "$root/usr/lib/libandroid-sysvshm.so", "${layout.libs.path}/libgamenative_dns_v4mapped.so", "$root/usr/lib/libredirect-bionic-wx.so").joinToString(":"),
            // Graphics: the Vulkan wrapper over this phone's Turnip, DXVK (D3D11) on it.
            "VK_ICD_FILENAMES" to "$root/usr/share/vulkan/icd.d/wrapper_icd.aarch64.json",
            "ADRENOTOOLS_DRIVER_PATH" to turnip.path + "/",
            "ADRENOTOOLS_HOOKS_PATH" to "$root/usr/lib",
            "ADRENOTOOLS_DRIVER_NAME" to turnipLibrary,
            // The Vulkan version the wrapper offers: 1.3 with the phone's own driver's patch level (GameNative's default,
            // `vulkanVersion=1.3` + GPUHelper.vkVersionPatch()); DXVK 2.4 needs 1.3.
            "WRAPPER_VK_VERSION" to "1.3.$vkPatch",
            "WRAPPER_MAX_IMAGE_COUNT" to "0",
            "WRAPPER_RESOURCE_TYPE" to "buffer",
            "WRAPPER_EMULATE_BCN" to "3",
            "WRAPPER_BCN_GPU" to "0",
            "WRAPPER_ASTC_BLOCK" to "4x4",
            "TU_DEBUG" to if (adreno8) "noconform,sysmem" else "noconform",
            "MESA_VK_WSI_PRESENT_MODE" to "mailbox",
            "MESA_SHADER_CACHE_DISABLE" to "false",
            "MESA_SHADER_CACHE_MAX_SIZE" to "512MB",
            "VKD3D_SHADER_MODEL" to "6_0",
            "GALLIUM_DRIVER" to "zink",
            "LIBGL_KOPPER_DISABLE" to "true",
            "MESA_VK_WSI_DEBUG" to "sw",
            "DXVK_STATE_CACHE_PATH" to "${layout.home.path}/.cache",
            // DXVK's d3d11 and dxgi (in system32) before Wine's own: without this Wine's builtin Direct3D answered, over OpenGL
            // (zink), and the game said "Your 3D accelerator card is not supported" (report 183). GameNative sets the same in
            // the prefix's DllOverrides (WineUtils: the Direct3D libraries native,builtin).
            "WINEDLLOVERRIDES" to "d3d8,d3d9,d3d10,d3d10_1,d3d10core,d3d11,d3d12,d3d12core,ddraw,dxgi,wined3d=n,b",
            // Warnings and errors to Wine's output, which goes into the reports.
            "DXVK_LOG_LEVEL" to "warn",
            "DXVK_LOG_PATH" to "none",
            "WINEESYNC" to "0",
        )
        if (samsung) env["FD_DEV_FEATURES"] = "enable_tp_ubwc_flag_hint=1"
        return env.map { (k, v) -> "$k=$v" }
    }

    /**
     * The command: Android's loader runs Proton's Wine, whose desktop starts the keeper, which starts [program] (the sign-in,
     * then the game). `{screen}` is the screen's size (the game screen fills it in).
     */
    fun command(layout: Layout, program: String): String =
        "/system/bin/linker64 ${layout.proton.path}/bin/wine explorer /desktop=shell,{screen} $program"

    /**
     * Before each start: the image's X socket folder is the session's (the game's X client opens `/tmp/.X11-unix/X0`, which the
     * redirect library puts in the image), and the image's own temporary folder exists.
     */
    fun linkX11(layout: Layout, winRoot: String) {
        val tmp = File(layout.imagefs, "tmp").apply { mkdirs() }
        File(layout.imagefs, "usr/tmp").mkdirs()
        val x11 = File(tmp, ".X11-unix")
        if (x11.exists() || isLink(x11)) x11.deleteRecursively().also { x11.delete() }
        java.nio.file.Files.createSymbolicLink(x11.toPath(), File("$winRoot/tmp/.X11-unix").toPath())
    }

    private fun isLink(f: File) = runCatching { java.nio.file.Files.isSymbolicLink(f.toPath()) }.getOrDefault(false)

    /** What the game screen runs: the command, its environment (`NAME=value`) and its folder (Winlator patch 0010). */
    class Launch(val command: String, val env: Array<String>, val dir: File, val signedIn: Boolean)

    /** The ARM64 builds of the keeper and the sign-in (scripts/build-tools.sh), as the app's assets name them. */
    const val KEEPER_ASSET = "borderless-arm64.exe"
    const val SIGN_IN_ASSET = "forevergo-arm64.exe"
    /** The hosts library for the container's programs (tools/hostsfix, built by scripts/build-tools.sh with the NDK). */
    const val HOSTS_ASSET = "libblizzhosts.so"

    /**
     * Everything for one start of the game: the prefix ([Prefix.ensure]) with the ARM64 keeper and sign-in in `C:\windows`,
     * the realm's CA and the sign-in Play made ([login]: game account and ticket, or null for the game's login screen), last
     * session's logs gone, the realm's name in the image's hosts file, the X socket linked ([linkX11]), this phone's Turnip.
     */
    fun prepare(context: Context, layout: Layout, client: File, ca: File, login: Pair<String, String>?, winRoot: String, worldPort: Int): Launch {
        val assets = context.assets
        val extras = linkedMapOf(
            "borderless.exe" to assets.open(KEEPER_ASSET).use { it.readBytes() },
            "forevergo.exe" to assets.open(SIGN_IN_ASSET).use { it.readBytes() },
        )
        if (login != null && ca.isFile) {
            extras["forevergo.ca"] = ca.readBytes()
            extras["forevergo.login"] = com.logie.blizz.forever.ForeverGo.loginFile(login.first, login.second, worldPort).toByteArray()
        }
        Prefix.ensure(layout, client, extras)
        // Wine's sound goes through ALSA to the session's sound server (GameNative's changeWineAudioDriver for "alsa").
        runCatching {
            com.winlator.core.WineRegistryEditor(File(layout.prefix, "user.reg")).use { it.setStringValue("Software\\Wine\\Drivers", "Audio", "alsa") }
        }
        File(layout.libs, HOSTS_ASSET).let { lib ->
            layout.libs.mkdirs()
            assets.open(HOSTS_ASSET).use { input -> lib.outputStream().use { input.copyTo(it) } }
            lib.setExecutable(true, false); lib.setReadable(true, false)
        }
        for (name in listOf("borderless.log", "borderless.dialog", "forevergo.log")) File(layout.windows, name).delete()
        if (login == null) File(layout.windows, "forevergo.login").delete()
        File(layout.imagefs, "etc").mkdirs()
        File(layout.imagefs, "etc/hosts").writeText("127.0.0.1 localhost\n127.0.0.1 ${com.logie.blizz.forever.ForeverLauncher.PORTAL}\n")
        linkX11(layout, winRoot)
        val adreno8 = adreno8xx()
        val turnip = layout.turnip(turnipZip(adreno8))
        val env = environment(layout, winRoot, context.packageName, turnip, turnipLibrary(turnip), adreno8,
            Build.MANUFACTURER.equals("samsung", ignoreCase = true), vulkanPatch())
        val signedIn = login != null && File(layout.windows, "forevergo.login").isFile
        return Launch(command(layout, program(signedIn)), env.toTypedArray(), File(client, "_forever_"), signedIn)
    }

    /** The phone's Vulkan driver's patch level (0 when it can't be read). */
    private fun vulkanPatch(): Int = runCatching { com.winlator.core.GPUHelper.vkGetApiVersion() and 0xFFF }.getOrDefault(0)

    /** The game's own log of its graphics start (`_forever_/Logs/gx.log`): which adapter, which API, why it refused one. */
    fun gxLog(client: File) = File(client, "_forever_/Logs/gx.log")

    /** What the desktop starts: the keeper, then (signed in) the sign-in, then the game (Direct3D 11: DXVK). */
    fun program(signedIn: Boolean): String =
        "C:\\windows\\borderless.exe /noframes " + (if (signedIn) "C:\\windows\\forevergo.exe " else "") +
            "G:\\_forever_\\$EXE" + (if (signedIn) " " + com.logie.blizz.forever.ForeverGo.ARGUMENT else "") + " -d3d11"

    /** The session keeper's files in the prefix (its log, its dialog flag) and the sign-in's log, for the reports. */
    fun keeperLog(layout: Layout) = File(layout.windows, "borderless.log")
    fun dialogFile(layout: Layout) = File(layout.windows, "borderless.dialog")
    fun signInLog(layout: Layout) = File(layout.windows, "forevergo.log")

    /** The Turnip's library (its `meta.json`'s `libraryName`). */
    fun turnipLibrary(dir: File): String = JSONObject(File(dir, "meta.json").readText()).getString("libraryName")
}
