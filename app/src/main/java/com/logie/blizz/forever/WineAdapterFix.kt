package com.logie.blizz.forever

import java.io.File
import java.security.MessageDigest

/**
 * Winlator's Wine (10.10, the build pinned in `winlator-version.env`) is compiled without a way to list the
 * network interfaces (its `nsiproxy.so` has no `if_nameindex`/`getifaddrs`: Android refuses them), so its interface
 * table is always empty, and its `GetAdaptersAddresses` (iphlpapi.dll) then walks a zero-length allocation as if it
 * were an adapter: `strlen` of a null name. The Forever client asks for the adapters in its first second and died
 * there (its own crash file: "ACCESS_VIOLATION ... IPHLPAPI.DLL"; Wine's own `ipconfig /all` dies the same way),
 * which on the phone was the black screen and the launcher again.
 *
 * The fix is the answer Windows gives a computer with no adapters: the function returns ERROR_NO_DATA (232) at
 * once (`mov eax, 232; ret` over its first bytes). Only the one known file is touched (by its SHA-256); any other
 * build of the DLL is left as it is. Run on the desktop on 9 November 2026 against the same Wine: with it the
 * client goes on to its login screen and connects to 127.0.0.1:1119.
 */
object WineAdapterFix {
    /** Wine 10.10's iphlpapi.dll as Winlator 11.2 ships it, and as fixed here. */
    const val ORIGINAL = "44252fd64cf6beb86694a434dc46c096eb31296ad1c9d6d3b25ba7e8286d9a22"
    const val FIXED = "373c9a9c4b385684d24bb234b6ac3e791cdb0ad0289fd8085b38d07f84fa33a8"

    /** GetAdaptersAddresses in that file (its export's address, which is also its place in the file). */
    const val OFFSET = 0x4cb0

    /** `mov eax, 232` (ERROR_NO_DATA); `ret`. */
    val CODE = byteArrayOf(0xB8.toByte(), 0xE8.toByte(), 0, 0, 0, 0xC3.toByte())

    /** The fixed file, or null when [dll] isn't the file this is for (another build, or fixed already). */
    fun fixed(dll: ByteArray, original: String = ORIGINAL): ByteArray? {
        if (dll.size < OFFSET + CODE.size || sha256(dll) != original) return null
        return dll.copyOf().also { System.arraycopy(CODE, 0, it, OFFSET, CODE.size) }
    }

    /**
     * Fixes Wine's own iphlpapi.dll under [rootfs] (the one Wine loads) and the copy in the [container]'s Windows.
     * Returns how many files were rewritten (0 once done, or for another Wine).
     */
    fun apply(rootfs: File, container: File?): Int {
        val files = listOfNotNull(
            File(rootfs, "opt/wine/lib/wine/x86_64-windows/iphlpapi.dll"),
            container?.let { File(it, ".wine/drive_c/windows/system32/iphlpapi.dll") },
        )
        var count = 0
        for (file in files) {
            if (!file.isFile) continue
            val patched = fixed(file.readBytes()) ?: continue
            val temp = File(file.parentFile, file.name + ".fix")
            temp.writeBytes(patched)
            if (temp.renameTo(file)) count++ else temp.delete()
        }
        return count
    }

    fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
