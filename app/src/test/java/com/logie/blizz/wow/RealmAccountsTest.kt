package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class RealmAccountsTest {
    @Test
    fun octoHashIsTheSha1OfNameAndPasswordInCapitals() {
        // SHA-1("TEST:TEST")
        assertEquals("3D0D99423E31FCC67A6745EC89D70D700344BC76", RealmAccounts.octoHash("test", "test"))
        assertEquals(RealmAccounts.octoHash("Logan", "Secret1"), RealmAccounts.octoHash("LOGAN", "SECRET1"))
    }

    @Test
    fun legionHashIsTheReversedSha256() {
        val h = RealmAccounts.legionHash("a@b.c", "pw")
        assertEquals(64, h.length)
        assertTrue(h.all { it in "0123456789ABCDEF" })
        assertEquals(h, RealmAccounts.legionHash("A@B.C", "PW"))
    }

    @Test
    fun theSqlKeepsAnExistingAccountAndOnlySetsItsPassword() {
        val sql = RealmAccounts.octoSql("Logan", "Secret1")!!
        assertTrue(sql.contains("WHERE NOT EXISTS (SELECT 1 FROM account WHERE username = 'LOGAN')"))
        assertTrue(sql.contains("UPDATE account SET v = '0', s = '0', sha_pass_hash = '${RealmAccounts.octoHash("LOGAN", "SECRET1")}' WHERE username = 'LOGAN' AND sha_pass_hash <>"))
        val legion = RealmAccounts.legionSql("me@x.y", "pw")!!
        assertTrue(legion.contains("'ME@X.Y'"))
        assertTrue(legion.contains("UPDATE account SET v = '', s = '', sessionkey = ''"))
    }

    @Test
    fun namesAndPasswordsThatCouldBreakTheSqlAreRefused() {
        assertNull(RealmAccounts.octoSql("a'b", "pw"))
        assertNull(RealmAccounts.octoSql("name", "p'w"))
        assertNull(RealmAccounts.octoSql("name", "back\\slash"))
        assertNull(RealmAccounts.octoSql("toolongaccountname1", "pw"))
        assertNull(RealmAccounts.octoSql("me@x.y", "pw"))
        assertNull(RealmAccounts.legionSql("plainname", "pw"))
        assertNull(RealmAccounts.legionSql("a@b.c", "has space"))
    }
}
