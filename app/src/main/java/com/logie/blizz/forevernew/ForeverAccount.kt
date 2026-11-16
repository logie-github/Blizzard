package com.logie.blizz.forevernew

import java.math.BigInteger
import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

/**
 * The local Battle.net account made directly in the auth database, the way TrinityCore's own `bnetaccount create` stores it
 * (BattlenetAccountMgr.cpp, SRP6.cpp, srp version 2: PBKDF2-HMAC-SHA512, 15000 rounds), so it doesn't wait on the world server's
 * console. Checked against the real login server: the account made here logs in through bnetserver's REST login (see docs/forever/README.md).
 *  - the name is upper-cased (Latin letters) and the SRP user name is the hex of its SHA-256;
 *  - x = PBKDF2(user ":" password, salt) as a big-endian number, minus 2^512 if its top bit is set, mod (N - 1);
 *  - the verifier is g^x mod N, stored little-endian; the salt is 32 random bytes.
 * The game account `<id>#1` and GM level 3 on this local realm (`account_access`, realm -1) come with it.
 */
object ForeverAccount {
    private val N = BigInteger(
        "AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC3192943DB56050A37329CBB4A099ED8193E0757767A13DD52312AB4B03310DCD7F48A9DA04FD50E8083969EDB767B0CF6095179A163AB3661A05FBD5FAAAE82918A9962F0B93B855F97993EC975EEAA80D740ADBF4FF747359D041D5C33EA71D281E446B14773BCA97B43A23FB801676BD207A436C6481F1D2B9078717461A5B9D32E688F87748544523B524B0D57D5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6AF874E7303CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB694B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F9E4AFF73", 16)
    private val G = BigInteger.valueOf(2)
    private const val ITERATIONS = 15000

    /** TrinityCore upper-cases only the Latin letters of a name. */
    fun upper(name: String) = buildString { for (c in name) append(if (c in 'a'..'z') c.uppercaseChar() else c) }

    fun srpUsername(email: String): String =
        MessageDigest.getInstance("SHA-256").digest(upper(email).toByteArray(Charsets.UTF_8)).joinToString("") { "%02X".format(it) }

    private fun x(srpUser: String, password: String, salt: ByteArray): BigInteger {
        val spec = PBEKeySpec((srpUser + ":" + password).toCharArray(), salt, ITERATIONS, 512)
        val bytes = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA512").generateSecret(spec).encoded
        var x = BigInteger(1, bytes)
        if (bytes[0].toInt() and 0x80 != 0) x -= BigInteger.ONE.shiftLeft(512)
        return x.mod(N - BigInteger.ONE)
    }

    class Registration(val salt: ByteArray, val verifier: ByteArray)

    fun registration(email: String, password: String, salt: ByteArray = ByteArray(32).also { SecureRandom().nextBytes(it) }): Registration {
        val v = G.modPow(x(srpUsername(email), password, salt), N)
        return Registration(salt, littleEndian(v))
    }

    private fun littleEndian(v: BigInteger): ByteArray {
        val be = v.toByteArray().let { if (it.size > 1 && it[0] == 0.toByte()) it.copyOfRange(1, it.size) else it }
        return be.reversedArray()
    }

    private fun hex(b: ByteArray) = "0x" + b.joinToString("") { "%02x".format(it) }
    private fun q(s: String) = "'" + ForeverDb.escape(s) + "'"

    /** SQL (for the `auth` database) that makes or updates the account, its game account and its GM level; safe to run again. */
    fun sql(email: String, password: String, gmLevel: Int = 3, reg: Registration = registration(email, password)): String {
        val e = q(upper(email)); val salt = hex(reg.salt); val ver = hex(reg.verifier)
        val gameSalt = hex(ByteArray(32).also { SecureRandom().nextBytes(it) }); val gameVerifier = hex(ByteArray(32).also { SecureRandom().nextBytes(it) })
        return """
            INSERT INTO battlenet_accounts (email, srp_version, salt, verifier) SELECT $e, 2, $salt, $ver FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM battlenet_accounts WHERE email = $e);
            UPDATE battlenet_accounts SET srp_version = 2, salt = $salt, verifier = $ver, failed_logins = 0, locked = 0 WHERE email = $e;
            SET @id = (SELECT id FROM battlenet_accounts WHERE email = $e);
            INSERT INTO account (username, salt, verifier, email, reg_mail, battlenet_account, battlenet_index) SELECT CONCAT(@id, '#1'), $gameSalt, $gameVerifier, $e, $e, @id, 1 FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM account WHERE battlenet_account = @id AND battlenet_index = 1);
            SET @gid = (SELECT id FROM account WHERE battlenet_account = @id AND battlenet_index = 1);
            INSERT INTO account_access (AccountID, SecurityLevel, RealmID, Comment) VALUES (@gid, $gmLevel, -1, 'local realm') ON DUPLICATE KEY UPDATE SecurityLevel = $gmLevel;
        """.trimIndent() + "\n"
    }
}
