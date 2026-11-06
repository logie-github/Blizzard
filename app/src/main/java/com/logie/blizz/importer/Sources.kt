package com.logie.blizz.importer

import android.content.ContentResolver
import android.net.Uri
import android.provider.DocumentsContract
import java.io.File
import java.io.InputStream

/**
 * A file or folder the importer reads from: on the phone's own storage ([FileNode]) or one the
 * person picked with Android's document picker ([DocumentNode], read through the Storage Access
 * Framework, never by path). Read as streams, never whole into memory.
 */
interface SourceNode {
    val name: String
    val isDirectory: Boolean
    val size: Long
    /** Where it is, for the person (a path or a picker's name). */
    val display: String
    fun children(): List<SourceNode>
    fun open(): InputStream
    /** A file on this phone that can be handed to a program (innoextract), when it already is one. */
    fun localFile(): File? = null

    /** Deletes it (a folder with what is in it); whether it did. For the export a verified import no longer needs. */
    fun delete(): Boolean = false

    fun child(name: String): SourceNode? = children().firstOrNull { it.name.equals(name, ignoreCase = true) }

    /** Every file under this node, to [depth] folders down. */
    fun walk(depth: Int = 6): Sequence<SourceNode> = sequence {
        if (!isDirectory) {
            yield(this@SourceNode)
            return@sequence
        }
        if (depth < 0) return@sequence
        for (child in children()) {
            if (child.isDirectory) yieldAll(child.walk(depth - 1)) else yield(child)
        }
    }
}

class FileNode(val file: File) : SourceNode {
    override val name: String get() = file.name
    override val isDirectory: Boolean get() = file.isDirectory
    override val size: Long get() = if (file.isFile) file.length() else 0
    override val display: String get() = file.path
    override fun children(): List<SourceNode> = file.listFiles()?.sortedBy { it.name }?.map { FileNode(it) } ?: emptyList()
    override fun open(): InputStream = file.inputStream()
    override fun localFile(): File = file
    override fun delete(): Boolean = file.deleteTree()
}

/** A document or folder from the picker ([Uri] from ACTION_OPEN_DOCUMENT or ACTION_OPEN_DOCUMENT_TREE). */
class DocumentNode(
    private val resolver: ContentResolver,
    val uri: Uri,
    override val name: String,
    override val isDirectory: Boolean,
    override val size: Long,
    private val treeUri: Uri?,
) : SourceNode {
    override val display: String get() = name

    override fun children(): List<SourceNode> {
        val tree = treeUri ?: return emptyList()
        if (!isDirectory) return emptyList()
        val parent = DocumentsContract.getDocumentId(uri)
        val list = DocumentsContract.buildChildDocumentsUriUsingTree(tree, parent)
        val out = ArrayList<SourceNode>()
        val columns = arrayOf(
            DocumentsContract.Document.COLUMN_DOCUMENT_ID,
            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE,
            DocumentsContract.Document.COLUMN_SIZE,
        )
        resolver.query(list, columns, null, null, null)?.use { c ->
            while (c.moveToNext()) {
                val id = c.getString(0)
                val dir = c.getString(2) == DocumentsContract.Document.MIME_TYPE_DIR
                out += DocumentNode(resolver, DocumentsContract.buildDocumentUriUsingTree(tree, id), c.getString(1) ?: id, dir, if (c.isNull(3)) 0 else c.getLong(3), tree)
            }
        }
        return out.sortedBy { it.name }
    }

    override fun open(): InputStream = resolver.openInputStream(uri)
        ?: throw ImportException(Problem.PERMISSION_DENIED, "$name can't be opened: pick it again so the app may read it.")

    override fun delete(): Boolean = runCatching { DocumentsContract.deleteDocument(resolver, uri) }.getOrDefault(false)

    companion object {
        /** A folder picked with ACTION_OPEN_DOCUMENT_TREE. */
        fun tree(resolver: ContentResolver, treeUri: Uri): DocumentNode {
            val doc = DocumentsContract.buildDocumentUriUsingTree(treeUri, DocumentsContract.getTreeDocumentId(treeUri))
            val name = query(resolver, doc)?.first ?: "Folder"
            return DocumentNode(resolver, doc, name, true, 0, treeUri)
        }

        /** A file picked with ACTION_OPEN_DOCUMENT. */
        fun file(resolver: ContentResolver, uri: Uri): DocumentNode {
            val (name, size) = query(resolver, uri) ?: ((uri.lastPathSegment ?: "file") to 0L)
            return DocumentNode(resolver, uri, name, false, size, null)
        }

        private fun query(resolver: ContentResolver, uri: Uri): Pair<String, Long>? = runCatching {
            resolver.query(uri, arrayOf(DocumentsContract.Document.COLUMN_DISPLAY_NAME, DocumentsContract.Document.COLUMN_SIZE), null, null, null)?.use { c ->
                if (c.moveToFirst()) (c.getString(0) ?: "file") to (if (c.isNull(1)) 0L else c.getLong(1)) else null
            }
        }.getOrNull()
    }
}
