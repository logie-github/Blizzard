package com.logie.blizz.forever

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.KeyStore
import java.security.cert.CertificateFactory
import java.util.Base64
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManagerFactory

/**
 * World of Warcraft: Forever's sign-in, with nothing on screen (the way ForeverNXT's local launcher does it, without a
 * launcher): the app signs in at the phone's realm itself and the game starts already signed in.
 *
 * 1. [signIn]: the realm's HTTPS login service (127.0.0.1:8081, certificate made by this phone's CA for
 *    `trinity.actual.battle.net`): `POST /bnetserver/login/` gives a login ticket, `GET /bnetserver/gameAccounts/` the
 *    game account (`WoW1`).
 * 2. [prepare]: puts `forevergo.exe` (tools/forevergo, built by scripts/build-tools.sh into the app's assets), the CA
 *    (`forevergo.ca`) and the sign-in (`forevergo.login`: account, ticket) into the games' Windows (`C:\windows`).
 * 3. The game screen starts `forevergo.exe` in front of the session keeper ([wrapper]) and the game with
 *    [ARGUMENT]: it trusts the CA in Windows' root stores, writes the sign-in where the game reads it, and keeps the
 *    realm's public key in the game's table of realm keys while it runs, which is what lets the game into the realm.
 *
 * Run on the desktop rig (14 November 2026) with client 1.60.1.70707 and the realm's arm64 build under qemu: no login
 * screen, the realm joined, a character made, Enter World. Not run on a phone.
 */
object ForeverGo {
    const val ASSET = "forevergo.exe"
    const val PATH = "C:\\windows\\forevergo.exe"
    const val LOGIN_FILE = "forevergo.login"
    const val CA_FILE = "forevergo.ca"
    const val LOG = "forevergo.log"
    /** What the game is started with: it signs in with what the registry holds, no login screen. */
    const val ARGUMENT = "-launcherlogin"
    const val REST_PORT = 8081

    /** The sign-in Play made for the next start of the game (game account, ticket), taken by the game screen's setup. */
    @Volatile var pending: Pair<String, String>? = null

    /** The exec wrapper: this program, then the keeper's own command ([Borderless.command]). */
    fun wrapper(keeper: String): String = "$PATH $keeper"

    /** The JSON body of `POST /bnetserver/login/` (the game's own login form). */
    fun loginBody(email: String, password: String): String = JSONObject()
        .put("version", "1.0")
        .put("inputs", JSONArray()
            .put(JSONObject().put("input_id", "account_name").put("value", email))
            .put(JSONObject().put("input_id", "password").put("value", password)))
        .toString()

    /** The login ticket from the login answer, or null (wrong account or password, or an authenticator asked for). */
    fun ticketOf(answer: String): String? = runCatching {
        JSONObject(answer).optString("login_ticket").takeIf { Regex("[A-Za-z0-9-]{8,256}").matches(it) }
    }.getOrNull()

    /** The first game account that is neither banned nor suspended, from `GET /bnetserver/gameAccounts/`. */
    fun accountOf(answer: String): String? = runCatching {
        val list = JSONObject(answer).optJSONArray("game_accounts") ?: return null
        (0 until list.length()).map { list.getJSONObject(it) }
            .firstOrNull { !it.optBoolean("is_banned") && !it.optBoolean("is_suspended") }
            ?.optString("display_name")?.takeIf { Regex("[A-Za-z0-9#_-]{1,64}").matches(it) }
    }.getOrNull()

    /**
     * The contents of [LOGIN_FILE]: the game account, the ticket, and the realm's world port (forevergo.exe presses Reconnect
     * while the game is not connected to it once the realm's key is in).
     */
    fun loginFile(account: String, ticket: String, worldPort: Int = ForeverLauncher.WORLD_PORT) = "$account\n$ticket\n$worldPort\n"

    class SignInException(message: String) : Exception(message)

    /** Signs in at the phone's realm: (game account, login ticket). Throws [SignInException] with the reason. */
    fun signIn(caFile: File, email: String, password: String, port: Int = REST_PORT): Pair<String, String> {
        val tls = sslFor(caFile)
        fun open(path: String): HttpsURLConnection = (URL("https://127.0.0.1:$port$path").openConnection() as HttpsURLConnection).apply {
            sslSocketFactory = tls.socketFactory
            // The certificate names the realm (trinity.actual.battle.net), reached here by its address.
            hostnameVerifier = javax.net.ssl.HostnameVerifier { _, session ->
                javax.net.ssl.HttpsURLConnection.getDefaultHostnameVerifier().verify(ForeverLauncher.PORTAL, session)
            }
            connectTimeout = 10_000; readTimeout = 20_000
        }
        val login = open("/bnetserver/login/").apply {
            requestMethod = "POST"; doOutput = true
            setRequestProperty("Content-Type", "application/json")
            outputStream.use { it.write(loginBody(email, password).toByteArray()) }
        }
        val ticket = ticketOf(read(login)) ?: throw SignInException("The realm did not accept the account $email.")
        val accounts = open("/bnetserver/gameAccounts/").apply {
            setRequestProperty("Authorization", "Basic " + Base64.getEncoder().encodeToString("$ticket:".toByteArray()))
        }
        val account = accountOf(read(accounts)) ?: throw SignInException("The account $email has no game account on the realm.")
        return account to ticket
    }

    private fun read(connection: HttpURLConnection): String = try {
        val code = connection.responseCode
        val stream = if (code in 200..299) connection.inputStream else connection.errorStream
        stream?.bufferedReader()?.use { it.readText() } ?: throw SignInException("The realm's login service answered $code.")
    } finally {
        connection.disconnect()
    }

    private fun sslFor(caFile: File): SSLContext {
        val ca = caFile.inputStream().use { CertificateFactory.getInstance("X.509").generateCertificate(it) }
        val store = KeyStore.getInstance(KeyStore.getDefaultType()).apply { load(null, null); setCertificateEntry("realm", ca) }
        val trust = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm()).apply { init(store) }
        return SSLContext.getInstance("TLS").apply { init(null, trust.trustManagers, null) }
    }

    fun logFile(containerRoot: File) = File(containerRoot, ".wine/drive_c/windows/$LOG")

    /**
     * Puts the program, the realm's CA and the sign-in into the games' Windows at [containerRoot]. Whether all three are
     * there (without them the game starts as before, at its login screen).
     */
    fun prepare(context: Context, containerRoot: File, caFile: File, account: String, ticket: String): Boolean {
        val windows = File(containerRoot, ".wine/drive_c/windows")
        if (!windows.isDirectory || !caFile.isFile) return false
        val bytes = context.assets.open(ASSET).use { it.readBytes() }
        val exe = File(windows, ASSET)
        if (!(exe.isFile && exe.length() == bytes.size.toLong() && exe.readBytes().contentEquals(bytes))) exe.writeBytes(bytes)
        caFile.copyTo(File(windows, CA_FILE), overwrite = true)
        File(windows, LOGIN_FILE).writeText(loginFile(account, ticket))
        runCatching { logFile(containerRoot).delete() }
        return exe.length() == bytes.size.toLong()
    }
}
