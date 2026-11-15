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
 * launcher writes the server's public key into the running client. Those halves are [WineCerts], the hosts line and
 * `tools/foreverkey` (see [ForeverLaunch]).
 */
object ForeverAuth {
    /** The local account's name and password, generated once, kept in app-private storage. */
    data class Account(val name: String, val password: String, val dbUser: String, val dbPassword: String, val dbRoot: String)

    const val DEFAULT_NAME = "logie@wow.server"
    const val DEFAULT_PASSWORD = "Logie"

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
        // The player's own choice (a made-up address, local to this phone): the server limits a password to 16 characters, with no minimum.
        val a = Account(DEFAULT_NAME, DEFAULT_PASSWORD, "forever", randomSecret(18, random), randomSecret(18, random))
        layout.keys.mkdirs()
        val tmp = File(layout.credentials.path + ".tmp")
        tmp.writeText(JSONObject().put("name", a.name).put("password", a.password).put("dbUser", a.dbUser).put("dbPassword", a.dbPassword).put("dbRoot", a.dbRoot).toString())
        tmp.setReadable(false, false); tmp.setReadable(true, true); tmp.setWritable(false, false); tmp.setWritable(true, true)
        tmp.renameTo(layout.credentials)
        return a
    }

    /** The login name is an e-mail-shaped name (a Battle.net account); the password is 16 characters, upstream allows 6 to 16 with no spaces or quotes. */
    fun email(name: String) = "$name@forever.local"

    /**
     * Upstream's own way (repack/Create-Account.ps1): the world server's console makes the Battle.net account
     * (`bnetaccount create <name> <password>`, which also makes its game account `<id>#1`), then
     * `account set gmlevel <id>#1 3 -1` gives GM level 3 on this local realm so the ForeverBots window and `.bot` commands
     * work. The id is read from `auth.battlenet_accounts` after the first command ([ID_SQL]).
     */
    fun createCommand(account: Account) = "bnetaccount create ${account.name} ${account.password}"
    fun gmCommand(id: Int) = "account set gmlevel $id#1 3 -1"
    fun idSql(account: Account) = "SELECT id FROM auth.battlenet_accounts WHERE UPPER(email)=UPPER('${ForeverDb.escape(account.name)}')"
    fun gmSql(account: Account) = "SELECT MAX(aa.SecurityLevel) FROM auth.account a JOIN auth.account_access aa ON aa.AccountID=a.id " +
        "JOIN auth.battlenet_accounts b ON a.battlenet_account=b.id WHERE UPPER(b.email)=UPPER('${ForeverDb.escape(account.name)}')"

    /** The realm's row in the auth database: id 70 (what the client accepts), this phone, the client's build. */
    fun realmSql(build: Int): String =
        "INSERT INTO realmlist (id, name, address, localAddress, port, icon, flag, timezone, allowedSecurityLevel, gamebuild) " +
            "VALUES (${ForeverConfig.REALM_ID}, 'Forever', '127.0.0.1', '127.0.0.1', ${ForeverPorts.WORLD}, 0, 0, 1, 0, $build) " +
            "ON DUPLICATE KEY UPDATE name = VALUES(name), address = VALUES(address), localAddress = VALUES(localAddress), " +
            "port = VALUES(port), gamebuild = VALUES(gamebuild);"

    /** Upstream's certificate settings (repack/make-certs.ps1): a root restricted to actual.battle.net, and the portal's leaf signed by it. */
    fun caConfig(tag: String) = "[req]\ndistinguished_name=dn\nx509_extensions=ca\nprompt=no\n[dn]\nCN=WoW Forever Local CA $tag\n" +
        "[ca]\nbasicConstraints=critical,CA:TRUE\nkeyUsage=critical,keyCertSign,cRLSign\nsubjectKeyIdentifier=hash\n" +
        "nameConstraints=critical,permitted;DNS:actual.battle.net\n"
    fun serverConfig() = "[req]\ndistinguished_name=dn\nprompt=no\n[dn]\nCN=${ForeverConfig.PORTAL}\n"
    fun leafExt() = "subjectAltName=DNS:${ForeverConfig.PORTAL}\nextendedKeyUsage=serverAuth\nauthorityKeyIdentifier=keyid:always\n"

    /** `openssl` commands (run through the loader by the installer) for the root and the portal's certificate, 825 days (a client's limit). */
    fun certificateCommands(layout: ForeverLayout): List<List<String>> {
        val k = layout.keys
        fun f(n: String) = File(k, n).path
        val openssl = File(layout.bin, "openssl").path
        return listOf(
            listOf(openssl, "req", "-x509", "-newkey", "rsa:3072", "-nodes", "-keyout", f("forever-root-ca.key.pem"), "-out", f("forever-root-ca.cert.pem"), "-days", "825", "-config", f("ca.cnf")),
            listOf(openssl, "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", f("bnetserver.key.pem"), "-out", f("bnetserver.csr.pem"), "-config", f("server.cnf")),
            listOf(openssl, "x509", "-req", "-in", f("bnetserver.csr.pem"), "-CA", f("forever-root-ca.cert.pem"), "-CAkey", f("forever-root-ca.key.pem"), "-CAcreateserial", "-out", f("bnetserver.leaf.pem"), "-days", "825", "-extfile", f("leaf.ext")),
        )
    }

    /** The chain file bnetserver sends: the leaf, then the root (upstream's chain.pem). */
    fun chain(leaf: String, ca: String) = leaf.trimEnd() + "\n" + ca.trimEnd() + "\n"

    /** The root's private key never leaves keys/ and isn't packaged, copied or logged; only its certificate is for the game's trust store. */
    fun hasCertificate(layout: ForeverLayout) = File(layout.keys, "bnetserver.cert.pem").isFile && File(layout.keys, "bnetserver.key.pem").isFile &&
        File(layout.keys, "forever-root-ca.cert.pem").isFile

    /** The root's certificate (public), which the game's Wine is made to trust ([WineCerts]). */
    fun rootCertificate(layout: ForeverLayout) = File(layout.keys, "forever-root-ca.cert.pem")

}
