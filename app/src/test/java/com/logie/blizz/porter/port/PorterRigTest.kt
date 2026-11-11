package com.logie.blizz.porter.port

import com.logie.blizz.wow.Realm
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File
import java.net.InetSocketAddress
import java.net.Socket

/**
 * The porter against a real realm: the app's own ChromieCraft package on the rig of `tools/porter-rig` (README there),
 * its MariaDB up and its world server stopped, as the screens leave it for a port. Each fixture ([PorterFixtures]) is
 * planned and written by the engine through the MariaDB command-line client, the way the phone pipes SQL to
 * `ctl.sh sql`, with the realm's own `data/dbc`. What each was given is written to `<rig>/ported/<name>.expect` (and its
 * report beside it) for `tools/porter-rig/prove.sh`, which takes each into the world and checks it.
 *
 * Run with `BLIZZ_PORTER_RIG=<the rig's folder>`; skipped otherwise.
 */
class PorterRigTest {
    private val rig = System.getenv("BLIZZ_PORTER_RIG")?.let(::File)

    private fun db(): RealmDb {
        val client = File(rig, "mariadb/bin/mariadb")
        return ProcessRealmDb(listOf(client.path, "--no-defaults", "-h127.0.0.1", "-P3310", "-uacore", "-pacore", "--batch", "--skip-column-names"))
    }

    private fun portOpen(port: Int): Boolean = runCatching { Socket().use { it.connect(InetSocketAddress("127.0.0.1", port), 500); true } }.getOrDefault(false)

    /** Takes out a character an earlier run of this test made (its every row), so the run starts clean. */
    private fun remove(db: RealmDb, name: String) {
        val guid = db.query("acore_characters", "SELECT guid FROM characters WHERE name = ${Sql.text(name)}").firstOrNull()?.firstOrNull()?.toIntOrNull() ?: return
        val tables = db.query("information_schema", "SELECT TABLE_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'acore_characters' AND COLUMN_NAME = 'guid' AND TABLE_NAME LIKE 'character%'")
            .mapNotNull { it.firstOrNull() }
        val script = buildString {
            append("START TRANSACTION;\n")
            append("DELETE FROM item_instance WHERE owner_guid = $guid;\n")
            append("DELETE FROM mail_items WHERE receiver = $guid;\n")
            append("DELETE FROM mail WHERE receiver = $guid;\n")
            for (table in tables) append("DELETE FROM ${Sql.name(table)} WHERE guid = $guid;\n")
            append("COMMIT;\n")
        }
        db.execute("acore_characters", script)
    }

    @Test fun portsEachFixtureIntoTheRealm() {
        assumeTrue("BLIZZ_PORTER_RIG isn't set", rig != null)
        assertFalse("The rig's world server is running: stop it (tools/porter-rig/rig.sh world-stop)", portOpen(8085))
        assertTrue("The rig's database isn't up (tools/porter-rig/rig.sh db-start)", portOpen(3310))
        val db = db()
        val porter = Porter(db, RealmFiles(File(rig, "files"), PortRealm.of(Realm.CHROMIE)!!))
        assertTrue(porter.support().toString(), porter.support().supported)
        val refused = Porter(db, RealmFiles(File(rig, "files"), PortRealm.of(Realm.REMIX)!!)).support()
        assertFalse(refused.supported)

        val out = File(rig, "ported").apply { mkdirs() }
        val summary = StringBuilder()
        summary.append("realm: level cap ${porter.levelCap()}, ${porter.raceClassCombos().size} race and class pairs\n")
        for (fixture in PorterFixtures.all) {
            remove(db, PortNames.normalize(fixture.options.name))
            val suggestion = porter.suggestTarget(fixture.character, fixture.options.level)
            assertNotNull(suggestion)
            summary.append("${fixture.character.name}: suggested ${suggestion!!.race}/${suggestion.classId} choice=${suggestion.needsChoice} ${suggestion.notes}\n")
            val started = System.currentTimeMillis()
            val plan = porter.plan(fixture.character, fixture.options)
            val planned = System.currentTimeMillis() - started
            File(out, "${plan.name}.report.txt").writeText((listOf("${fixture.about}; planned in $planned ms") + plan.report.lines()).joinToString("\n") + "\n")
            assertTrue("${fixture.character.name}: ${plan.refusals}", plan.ready)
            val result = porter.apply(plan)
            assertEquals(plan.name, result.name)
            File(out, "${plan.name}.expect").writeText(expectations(plan, result))
            summary.append("${plan.name}: guid ${result.guid}, level ${plan.level}, ${plan.items.size} items, ${plan.spells.size} spells, ${plan.skills.size} skills, planned in $planned ms\n")
        }
        // The mapped fixture: a demon hunter, which the realm can't have, is proposed as a class to choose.
        val dh = porter.suggestTarget(PorterFixtures.mapped.character)!!
        assertEquals(15, dh.race)
        assertTrue(dh.needsChoice)
        File(out, "summary.txt").writeText(summary.toString())
    }

    /** What prove.sh checks after the character has been in the world: a key and its values, a line each. */
    private fun expectations(plan: PortPlan, result: PortResult): String = buildString {
        append("name\t${plan.name}\n")
        append("guid\t${result.guid}\n")
        append("race\t${plan.race}\n")
        append("class\t${plan.classId}\n")
        append("level\t${plan.level}\n")
        append("money\t${plan.money}\n")
        append("map\t${plan.position.map}\n")
        append("items\t" + plan.items.joinToString(" ") { "${it.slot}:${it.entry}" } + "\n")
        append("spells\t" + plan.spells.joinToString(" ") + "\n")
        append("skills\t" + plan.skills.joinToString(" ") { "${it.skill}:${it.value}:${it.max}" } + "\n")
        append("reputations\t" + plan.reputations.joinToString(" ") { "${it.faction}:${it.standing}" } + "\n")
        append("quests\t${plan.quests.size}\n")
        append("achievements\t" + plan.achievements.joinToString(" ") { "${it.first}" } + "\n")
        append("actions\t${plan.actions.size}\n")
        append("mounts\t" + plan.report.of(PortArea.MOUNTS).joinToString(" | ") { "${it.subject}=${it.detail}" } + "\n")
    }
}
