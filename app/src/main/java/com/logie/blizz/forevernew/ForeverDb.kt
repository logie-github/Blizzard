package com.logie.blizz.forevernew

import java.io.File

/**
 * Forever's own MariaDB: its own data folder, on 127.0.0.1:[ForeverPorts.DATABASE], with the stock databases of upstream's
 * configs (`auth`, `world`, `characters`, `hotfixes`, `playerbot`) inside it. They can't collide with another realm's: it is
 * another server process with another data folder. NOT run on a phone.
 *
 * The base data comes from three places, imported in this order: the source tree's base SQL (auth, characters), the world and
 * hotfix dumps out of Karrz's repack ([ForeverRepackData]), and the bots' shared schema and data. The servers then apply
 * the update files (`sql/updates`, `sql/custom`, `sql/playerbot_v2`) themselves (Updates.EnableDatabases = 15).
 * One thing is unverified: that the repack's dumps carry the `updates` table rows that tell the servers which updates they
 * already hold; if they don't, the first start would apply them all again (the log would say so).
 */
object ForeverDb {
    val DATABASES = listOf("auth", "world", "characters", "hotfixes", "playerbot")

    /**
     * The bootstrap SQL for a fresh data folder, as the package's own `mariadb-install-db` makes it (its `cat_sql`, with the
     * "normal" root login: no password, reachable only through the app's own socket and loopback): the system tables, the
     * performance tables, their data, the help tables, the GIS procedures and the sys schema. One statement per line group, the
     * way bootstrap mode reads them. Found and fixed by running this against the package's MariaDB 11.4 under qemu.
     */
    fun bootstrapSql(share: File): String = buildString {
        append("create database if not exists mysql;\nuse mysql;\nSET @auth_root_socket=NULL;\n")
        for (name in BOOTSTRAP_FILES) {
            val f = File(share, name)
            if (!f.isFile) throw java.io.IOException("MariaDB's $name is missing from the server package")
            append(f.readText()).append('\n')
        }
    }

    /** MariaDB 11.4's names, in `mariadb-install-db`'s order. */
    val BOOTSTRAP_FILES = listOf(
        "mariadb_system_tables.sql", "mariadb_performance_tables.sql", "mariadb_system_tables_data.sql",
        "fill_help_tables.sql", "maria_add_gis_sp_bootstrap.sql", "mariadb_sys_schema.sql",
    )

    fun needsBootstrap(layout: ForeverLayout) = !File(layout.db, "mysql").isDirectory

    /** Creates the five databases and the account the servers use, from the root login (no password, socket and loopback only). */
    fun createSql(user: String, password: String): String = buildString {
        for (d in DATABASES) append("CREATE DATABASE IF NOT EXISTS `$d` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n")
        append("CREATE USER IF NOT EXISTS '$user'@'127.0.0.1' IDENTIFIED BY '${escape(password)}';\n")
        append("CREATE USER IF NOT EXISTS '$user'@'localhost' IDENTIFIED BY '${escape(password)}';\n")
        append("ALTER USER '$user'@'127.0.0.1' IDENTIFIED BY '${escape(password)}';\nALTER USER '$user'@'localhost' IDENTIFIED BY '${escape(password)}';\n")
        for (d in DATABASES) for (host in listOf("127.0.0.1", "localhost")) append("GRANT ALL PRIVILEGES ON `$d`.* TO '$user'@'$host';\n")
        append("FLUSH PRIVILEGES;\n")
    }

    /** Where a root-less local admin is no longer possible: after setup the root login is given the generated secret. */
    fun lockRootSql(rootPassword: String): String =
        "ALTER USER 'root'@'localhost' IDENTIFIED BY '${escape(rootPassword)}'; DELETE FROM mysql.global_priv WHERE User='' ; FLUSH PRIVILEGES;\n"

    fun escape(s: String) = s.replace("\\", "\\\\").replace("'", "\\'")

    /** The base SQL files in import order, as (database, file); files that aren't there are left out (reported by the caller). */
    fun importPlan(layout: ForeverLayout, worldDump: File, hotfixDump: File): List<Pair<String, File>> = listOf(
        "auth" to File(layout.sql, "base/auth_database.sql"),
        "characters" to File(layout.sql, "base/characters_database.sql"),
        "world" to worldDump,
        "hotfixes" to hotfixDump,
        "playerbot" to File(layout.sql, "playerbot_shared/playerbot_shared_schema.sql"),
        "playerbot" to File(layout.sql, "playerbot_shared/playerbot_shared_data.sql"),
    )

    /** A base is imported once: [imported] says it was ([isImported] reads that). */
    fun marker(layout: ForeverLayout, database: String, file: File) = File(layout.checkpoints, "db-$database-${file.name}.done")
}
