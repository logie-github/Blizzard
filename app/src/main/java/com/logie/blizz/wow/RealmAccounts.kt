package com.logie.blizz.wow

import java.security.MessageDigest

/**
 * The account a version logs in with by itself, made sure of in the realm's own login database at each start, so the login the
 * app types always has an account to go to (whatever the export held, or the person typed in the Auto login card). Made the way
 * each server's own `account create` makes them: OctoWoW's (Tortoise-WoW's `tw_logon.account`: the name and password in
 * capitals, `sha_pass_hash` the SHA-1 of `NAME:PASSWORD`) and Legion's (LegionCore's `auth.account`: an e-mail, `sha_pass_hash` the
 * SHA-256 of `<SHA-256 of the name in capital hex>:<password>`, its bytes reversed). An account that is there keeps its security
 * level and characters; only its password is set to the one given. The SQL is only ever made from names and passwords that
 * passed the rules below, which allow no quote or backslash. Plain Kotlin, unit-tested.
 */
internal object RealmAccounts {
    val OCTO_NAME = Regex("[A-Za-z0-9]{1,16}")
    val LEGION_NAME = Regex("[A-Za-z0-9._-]{1,48}@[A-Za-z0-9.-]{1,15}")
    val PASSWORD = Regex("""[A-Za-z0-9!#$%&()*+,\-./:;<=>?@\[\]^_{|}~]{1,16}""")

    private fun hex(bytes: ByteArray) = bytes.joinToString("") { "%02X".format(it) }
    private fun digest(algorithm: String, text: String) = MessageDigest.getInstance(algorithm).digest(text.toByteArray(Charsets.UTF_8))

    fun octoHash(name: String, password: String) = hex(digest("SHA-1", "${name.uppercase()}:${password.uppercase()}"))

    fun legionHash(name: String, password: String) =
        hex(digest("SHA-256", hex(digest("SHA-256", name.uppercase())) + ":" + password.uppercase()).reversedArray())

    /** OctoWoW's: the SQL for `tw_logon`, or null when the name or password can't be a Tortoise account's. */
    fun octoSql(name: String, password: String): String? {
        if (!OCTO_NAME.matches(name.trim()) || !PASSWORD.matches(password)) return null
        val user = name.trim().uppercase()
        val hash = octoHash(user, password)
        return "INSERT INTO account (username, sha_pass_hash, `rank`, joindate) SELECT '$user', '$hash', 0, NOW() FROM DUAL " +
            "WHERE NOT EXISTS (SELECT 1 FROM account WHERE username = '$user');\n" +
            "UPDATE account SET v = '0', s = '0', sha_pass_hash = '$hash' WHERE username = '$user' AND sha_pass_hash <> '$hash';\n" +
            "REPLACE INTO realmcharacters (realmid, acctid, numchars) SELECT realmlist.id, account.id, 0 " +
            "FROM realmlist, account LEFT JOIN realmcharacters ON acctid = account.id WHERE acctid IS NULL;"
    }

    /** Legion's: the SQL for `auth`, or null when the e-mail or password can't be a LegionCore account's. */
    fun legionSql(name: String, password: String): String? {
        if (!LEGION_NAME.matches(name.trim()) || !PASSWORD.matches(password)) return null
        val user = name.trim().uppercase()
        val hash = legionHash(user, password)
        return "INSERT INTO account (username, sha_pass_hash, email, joindate) SELECT '$user', '$hash', '$user', NOW() FROM DUAL " +
            "WHERE NOT EXISTS (SELECT 1 FROM account WHERE username = '$user');\n" +
            "UPDATE account SET v = '', s = '', sessionkey = '', sha_pass_hash = '$hash' WHERE username = '$user' AND sha_pass_hash <> '$hash';\n" +
            "REPLACE INTO realmcharacters (realmid, acctid, numchars) SELECT realmlist.id, account.id, 0 " +
            "FROM realmlist, account LEFT JOIN realmcharacters ON acctid = account.id WHERE acctid IS NULL;"
    }
}
