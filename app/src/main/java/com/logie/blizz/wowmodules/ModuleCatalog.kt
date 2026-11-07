
package com.logie.blizz.wowmodules

import org.json.JSONObject
import java.net.URLEncoder

/**
 * AzerothCore's modules as GitHub lists them: the repositories with the topic `azerothcore-module`
 * (github.com/topics/azerothcore-module), found with GitHub's search, a page at a time.
 */
object ModuleCatalog {
    const val TOPIC = "azerothcore-module"
    const val PER_PAGE = 30

    enum class Order(val sort: String) { STARS("stars"), UPDATED("updated") }

    data class Listing(
        /** owner/name. */
        val fullName: String,
        val owner: String,
        val name: String,
        val description: String?,
        val stars: Int,
        /** When it last changed (ISO 8601). */
        val updated: String?,
        val defaultBranch: String,
        val avatar: String?,
        val url: String,
        val archived: Boolean,
        val language: String?,
    )

    data class Page(val total: Int, val items: List<Listing>)

    /** A page of the topic's modules, [search]ed by words in their names and descriptions. */
    fun searchUrl(search: String, order: Order, page: Int): String {
        val words = search.trim().split(Regex("\\s+")).filter { it.isNotEmpty() }.joinToString(" ")
        val query = if (words.isEmpty()) "topic:$TOPIC" else "$words topic:$TOPIC"
        return "https://api.github.com/search/repositories?q=" + URLEncoder.encode(query, "UTF-8") +
            "&sort=${order.sort}&order=desc&per_page=$PER_PAGE&page=$page"
    }

    fun parseSearch(json: String): Page {
        val root = JSONObject(json)
        val items = root.optJSONArray("items")
        val listings = (0 until (items?.length() ?: 0)).mapNotNull { i -> listing(items!!.getJSONObject(i)) }
        return Page(root.optInt("total_count"), listings)
    }

    /** One repository of GitHub's answers (the search's, or the repository's own). */
    fun listing(repo: JSONObject): Listing? {
        val fullName = repo.optString("full_name").takeIf { isFullName(it) } ?: return null
        val owner = repo.optJSONObject("owner")
        return Listing(
            fullName = fullName,
            owner = fullName.substringBefore('/'),
            name = fullName.substringAfter('/'),
            description = repo.text("description"),
            stars = repo.optInt("stargazers_count"),
            updated = repo.text("pushed_at") ?: repo.text("updated_at"),
            defaultBranch = repo.text("default_branch") ?: "master",
            avatar = owner?.text("avatar_url"),
            url = repo.text("html_url") ?: "https://github.com/$fullName",
            archived = repo.optBoolean("archived"),
            language = repo.text("language"),
        )
    }

    private fun JSONObject.text(key: String): String? =
        if (isNull(key)) null else optString(key).trim().takeIf { it.isNotEmpty() }

    /** The day of an ISO 8601 time ("2026-10-12"). */
    fun day(iso: String?): String? = iso?.takeIf { it.length >= 10 }?.substring(0, 10)

    // What a build may be asked for: names that are safe as a folder, commits as GitHub writes them.

    private val NAME = Regex("[A-Za-z0-9_-][A-Za-z0-9_.-]*")
    private val COMMIT = Regex("[0-9a-f]{40}")

    fun isFullName(text: String): Boolean {
        val parts = text.split('/')
        return parts.size == 2 && parts.all { NAME.matches(it) }
    }

    fun isCommit(text: String): Boolean = COMMIT.matches(text)
}
