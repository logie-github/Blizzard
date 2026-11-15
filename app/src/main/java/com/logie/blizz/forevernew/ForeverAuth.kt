package com.logie.blizz.forevernew

import org.json.JSONObject
import java.io.File
import java.security.SecureRandom

/**
 * The local account and the login certificate. Everything is made per install on the phone; nothing secret is in the package,
 * the source or the logs.
 *
 * What upstream says the client needs (doc/ForeverSetup.md): it logs in over TLS to [ForeverConfig.PORTAL]; that name must
 * resolve to the server (inside the game's own Wine only here, never Android's hosts file); the certificate for it must
 * chain to a root the client trusts (a CA the install makes itself, name-constrained to `actual.battle.net`); and the
 * launcher writes the server's public key into the running client. THE LAST TWO HALVES (the Wine trust store, and the
 * launcher's key injection every start) ARE NOT IMPLEMENTED OR TESTED YET: [Launch] says so instead of starting the game.
 */
object ForeverAuth {
    /** The local account's name and password, generated once, kept in app-private storage. */
    data class Account(val name: String, val password: String, val dbUser: String, val dbPassword: String, val dbRoot: String)

    fun randomSecret(bytes: Int = 18, random: SecureRandom = SecureRandom()): String {
        val raw = ByteArray(bytes).also { random.nextBytes(it) }
        return raw.joinToString("") { "%02x".format(it) }
    }

    fun loadOrCreate(layout: ForeverLayout, random: SecureRandom = SecureRandom()): Account {
        layout.credentials.takeIf { it.isFile }?.let { f ->
            runCatching {
                val j = JSONObject(f.readText())
                return Account(j.getString("name"), j.getString("password"), j.getString("dbUser"), j.getString("dbPassword"), j.getString("dbRoot"))
            }
        }
        val a = Account("forever", randomSecret(9, random), "forever", randomSecret(18, random), randomSecret(18, random))
        layout.keys.mkdirs()
        val tmp = File(layout.credentials.path + ".tmp")
        tmp.writeText(JSONObject().put("name", a.name).put("password", a.password).put("dbUser", a.dbUser).put("dbPassword", a.dbPassword).put("dbRoot", a.dbRoot).toString())
        tmp.setReadable(false, false); tmp.setReadable(true, true); tmp.setWritable(false, false); tmp.setWritable(true, true)
        tmp.renameTo(layout.credentials)
        return a
    }

    /**
     * The account in the auth database: Battle.net accounts here are `email` rows with a SRP6 verifier, and the game account
     * `1#1`. The password hash is made by bnetserver's own scheme, which the app doesn't reimplement: the account is made with
     * the world server's console (`bnetaccount create <email> <password>`, `bnetaccount gameaccountcreate`, `account set gmlevel`),
     * which is what [consoleCommands] lists, sent once the world server is up.
     */
    fun email(account: Account) = "${account.name}@forever.local"

    fun consoleCommands(account: Account): List<String> = listOf(
        "bnetaccount create ${email(account)} ${account.password}",
        "bnetaccount gameaccountcreate ${email(account)} ${account.name}",
        // GM level 3 on this local realm only, so the ForeverBots window and .bot commands work.
        "account set gmlevel 1#1 3 -1",
    )

    /** The realm's row in the auth database: id 70 (what the client accepts), this phone, the client's build. */
    fun realmSql(build: Int): String =
        "INSERT INTO realmlist (id, name, address, localAddress, port, icon, flag, timezone, allowedSecurityLevel, gamebuild) " +
            "VALUES (${ForeverConfig.REALM_ID}, 'Forever', '127.0.0.1', '127.0.0.1', ${ForeverPorts.WORLD}, 0, 0, 1, 0, $build) " +
            "ON DUPLICATE KEY UPDATE name = VALUES(name), address = VALUES(address), localAddress = VALUES(localAddress), " +
            "port = VALUES(port), gamebuild = VALUES(gamebuild);"

    /** `openssl` commands (run through the loader by the installer) for a name-constrained root and the portal's certificate. */
    fun certificateCommands(layout: ForeverLayout): List<List<String>> {
        val k = layout.keys
        val ca = File(k, "forever-root-ca.key.pem").path; val caCert = File(k, "forever-root-ca.cert.pem").path
        val key = File(k, "bnetserver.key.pem").path; val csr = File(k, "bnetserver.csr.pem").path
        val cert = File(k, "bnetserver.cert.pem").path; val ext = File(k, "bnetserver.ext").path
        val caExt = File(k, "ca.ext").path
        val openssl = File(layout.bin, "openssl").path
        return listOf(
            listOf(openssl, "req", "-x509", "-newkey", "rsa:3072", "-nodes", "-keyout", ca, "-out", caCert, "-days", "3650",
                "-subj", "/CN=Forever local root", "-addext", "basicConstraints=critical,CA:TRUE", "-addext", "nameConstraints=critical,permitted;DNS:actual.battle.net"),
            listOf(openssl, "req", "-newkey", "rsa:2048", "-nodes", "-keyout", key, "-out", csr, "-subj", "/CN=${ForeverConfig.PORTAL}"),
            listOf(openssl, "x509", "-req", "-in", csr, "-CA", caCert, "-CAkey", ca, "-CAcreateserial", "-out", cert, "-days", "825",
                "-extfile", ext),
        )
    }

    fun serverCertExt(): String = "subjectAltName=DNS:${ForeverConfig.PORTAL}\nbasicConstraints=CA:FALSE\nextendedKeyUsage=serverAuth\n"

    /** The root's private key never leaves keys/ and isn't packaged, copied or logged; only its certificate is for the game's trust store. */
    fun hasCertificate(layout: ForeverLayout) = File(layout.keys, "bnetserver.cert.pem").isFile && File(layout.keys, "bnetserver.key.pem").isFile

    /** The honest state of game start-up: what isn't done yet. */
    object Launch {
        const val NOT_WIRED = "Starting the game is not implemented yet: the game's Wine certificate trust and the launcher's server-key step " +
            "(WoWForeverLauncher.exe under the app's Wine) have not been built or tested on a phone."
    }
}
