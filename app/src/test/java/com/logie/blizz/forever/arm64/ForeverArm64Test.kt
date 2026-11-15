package com.logie.blizz.forever.arm64

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File
import java.nio.file.Files

@RunWith(RobolectricTestRunner::class)
class ForeverArm64Test {
    @Test fun `SHA256SUMS lines`() {
        val sums = ForeverArm64.parseSums("137807f4145b1b440075f83b2b1b3501d19c4eb618784b1a28418652cae3db03  proton-11.0-90624-arm64ec.wcp\n\nnot a line\n")
        assertEquals(mapOf("proton-11.0-90624-arm64ec.wcp" to "137807f4145b1b440075f83b2b1b3501d19c4eb618784b1a28418652cae3db03"), sums)
    }

    @Test fun `every part is in the published sums`() {
        // forever-arm64/sources.txt is what the release holds; every part the app installs is one of them.
        val names = File("../forever-arm64/sources.txt").readLines().filter { it.isNotBlank() && !it.startsWith("#") }.map { it.substringBefore(' ') }.toSet()
        for (part in ForeverArm64.PARTS) assertTrue(part.name, part.name in names)
    }

    @Test fun `the Turnip for the GPU`() {
        assertTrue(ForeverArm64.isAdreno8xx("SM8750", "qcom"))
        assertTrue(ForeverArm64.isAdreno8xx(null, "sun"))
        assertFalse(ForeverArm64.isAdreno8xx("SM8550", "kalama"))
        assertEquals(ForeverArm64.TURNIP_8XX, ForeverArm64.turnipZip(true))
        assertEquals(ForeverArm64.TURNIP_740, ForeverArm64.turnipZip(false))
    }

    @Test fun `DXVK's files from its profile`() {
        // The published package's profile.json, as it is.
        val profile = """{"type":"DXVK","versionName":"2.4.1-wow-aarch64-test","versionCode":1,"description":"x","files":[
            {"source":"system32/dxgi.dll","target":"${'$'}{system32}/dxgi.dll"},{"source":"system32/d3d11.dll","target":"${'$'}{system32}/d3d11.dll"}]}"""
        assertEquals(listOf("system32/dxgi.dll" to "\${system32}/dxgi.dll", "system32/d3d11.dll" to "\${system32}/d3d11.dll"), ForeverArm64.dxvkFiles(profile))
    }

    @Test fun `the environment and the command`() {
        val layout = ForeverArm64.Layout(File("/data/user/0/com.logie.blizz/files"))
        val env = ForeverArm64.environment(layout, "/data/data/com.logie.blizz/winrootfs", "com.logie.blizz",
            File("/data/user/0/com.logie.blizz/files/forever-arm64/turnip/turnip-V32-RP6sched"), "libvulkan_freedreno.so", adreno8 = true, samsung = true, vkPatch = 284)
            .associate { it.substringBefore('=') to it.substringAfter('=') }
        assertEquals("/data/user/0/com.logie.blizz/files/imagefs/home/xuser/.wine", env["WINEPREFIX"])
        assertEquals("/data/data/com.logie.blizz/winrootfs/tmp/.sysvshm/SM0", env["ANDROID_SYSVSHM_SERVER"])
        assertEquals("com.logie.blizz", env["HOST_PKG"])
        assertEquals("0", env["WINEESYNC"])
        // DXVK's Direct3D, not Wine's (report 183: "Your 3D accelerator card is not supported").
        assertTrue(env.getValue("WINEDLLOVERRIDES").let { it.endsWith("=n,b") && "d3d11" in it.split('=')[0].split(',') && "dxgi" in it.split('=')[0].split(',') })
        assertEquals("1.3.284", env["WRAPPER_VK_VERSION"])
        assertEquals("noconform,sysmem", env["TU_DEBUG"])
        assertEquals("libvulkan_freedreno.so", env["ADRENOTOOLS_DRIVER_NAME"])
        assertEquals("enable_tp_ubwc_flag_hint=1", env["FD_DEV_FEATURES"])
        assertTrue(env.getValue("LD_PRELOAD").endsWith("/usr/lib/libredirect-bionic-wx.so"))
        assertEquals(
            "/system/bin/linker64 /data/user/0/com.logie.blizz/files/imagefs_shared/proton/proton-11.0-90624-arm64ec/bin/wine explorer /desktop=shell,{screen} C:\\windows\\borderless.exe /noframes G:\\_forever_\\Wow-ARM64.exe",
            ForeverArm64.command(layout, "C:\\windows\\borderless.exe /noframes G:\\_forever_\\Wow-ARM64.exe"),
        )
    }

    /** The whole runtime from the release, laid out and the prefix made (BLIZZ_FOREVER_ARM64=1: ~460 MB down, ~1.5 GB on disk). */
    @Test fun `the runtime and the prefix from the release`() {
        assumeTrue(System.getenv("BLIZZ_FOREVER_ARM64") == "1")
        val files = Files.createTempDirectory("arm64").toFile()
        try {
            val layout = ForeverArm64.Layout(files)
            ForeverArm64.Runtime.install(layout, { step, _ -> println(step) })
            assertTrue(File(layout.proton, "lib/wine/aarch64-unix/wine").canExecute())
            assertTrue(File(layout.imagefs, "usr/lib/libredirect-bionic-wx.so").isFile)
            assertTrue(File(layout.imagefs, "usr/share/vulkan/icd.d/wrapper_icd.aarch64.json").isFile)
            val turnip = layout.turnip(ForeverArm64.TURNIP_8XX)
            assertTrue(File(turnip, ForeverArm64.turnipLibrary(turnip)).isFile)
            val game = File(files, "client").apply { mkdirs() }
            ForeverArm64.Prefix.ensure(layout, game, mapOf("x.txt" to byteArrayOf(1)))
            assertTrue(File(layout.prefix, "system.reg").isFile)
            assertTrue(File(layout.system32, "d3d11.dll").isFile)
            assertTrue(File(layout.system32, "ntdll.dll").isFile)
            assertEquals(game.canonicalPath, File(layout.prefix, "dosdevices/g:").canonicalPath)
            assertTrue(File(layout.windows, "x.txt").isFile)
            // A second run changes nothing it needn't.
            ForeverArm64.Runtime.install(layout, { step, _ -> assertFalse(step, step.startsWith("Getting")) })
        } finally { files.deleteRecursively() }
    }

    /** The ARM64 client's programs from Blizzard's CDN into a bare client folder (BLIZZ_FOREVER_ARM64_CLIENT=1). */
    @Test fun `the ARM64 programs from Blizzard`() {
        assumeTrue(System.getenv("BLIZZ_FOREVER_ARM64_CLIENT") == "1")
        val client = Files.createTempDirectory("client").toFile()
        try {
            ForeverArm64.Client.install(client, { println(it) })
            assertTrue(ForeverArm64.Client.has(client))
            assertTrue(File(client, "_forever_/${ForeverArm64.EXE}").length() > 50_000_000)
        } finally { client.deleteRecursively() }
    }
}
