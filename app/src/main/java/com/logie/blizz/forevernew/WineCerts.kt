package com.logie.blizz.forevernew

import java.io.File
import java.security.MessageDigest
import java.util.Base64

/**
 * Makes the game's Windows (Wine) trust Forever's own login CA, the way upstream's Windows setup does with
 * `Import-Certificate ... Cert:\LocalMachine\Root`: the certificate goes into `HKLM\Software\Microsoft\SystemCertificates\Root\Certificates\<SHA-1>`
 * as a serialized certificate (`Blob`), in both registry views. Only inside the games' own Wine prefix, never Android's trust store.
 * Must be written while Wine isn't running (the app does it before the game screen starts). Checked against the phone's own
 * Wine on a desktop with a chain check (CertGetCertificateChain) before and after.
 */
object WineCerts {
    private const val ROOT = "Software\\\\Microsoft\\\\SystemCertificates\\\\Root\\\\Certificates"

    fun pemToDer(pem: String): ByteArray =
        Base64.getMimeDecoder().decode(pem.lineSequence().filter { !it.startsWith("-----") }.joinToString(""))

    fun thumbprint(der: ByteArray): String = MessageDigest.getInstance("SHA-1").digest(der).joinToString("") { "%02X".format(it) }

    /** The registry's serialized element for a certificate: property 32 (the certificate itself), flags 1, its length, its bytes. */
    fun blob(der: ByteArray): ByteArray {
        fun le(v: Int) = byteArrayOf(v.toByte(), (v shr 8).toByte(), (v shr 16).toByte(), (v shr 24).toByte())
        return le(32) + le(1) + le(der.size) + der
    }

    /** Wine's .reg text for the certificate, both views, hex lines wrapped as Wine writes them. */
    fun registryText(der: ByteArray, nowSeconds: Long): String = buildString {
        val hex = blob(der).joinToString(",") { "%02x".format(it) }
        for (view in listOf("", "Wow6432Node\\\\")) {
            val key = if (view.isEmpty()) ROOT else ROOT.replace("Software\\\\", "Software\\\\$view")
            append("\n[").append(key).append("\\\\").append(thumbprint(der)).append("] ").append(nowSeconds).append('\n')
            append("\"Blob\"=hex:")
            var col = 11
            val parts = hex.split(',')
            for ((i, p) in parts.withIndex()) {
                if (col > 74) { append("\\\n  "); col = 2 }
                append(p); col += 2
                if (i < parts.lastIndex) { append(','); col++ }
            }
            append('\n')
        }
    }

    fun isInstalled(systemReg: File, der: ByteArray): Boolean = systemReg.isFile && systemReg.readText().contains("\\\\" + thumbprint(der) + "]")

    /** Adds the certificate to [systemReg] unless it is there; true if it was added. */
    fun install(systemReg: File, der: ByteArray, nowSeconds: Long = System.currentTimeMillis() / 1000): Boolean {
        if (!systemReg.isFile || isInstalled(systemReg, der)) return false
        systemReg.appendText(registryText(der, nowSeconds))
        return true
    }
}
