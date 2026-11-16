package com.logie.blizz.forevernew

import android.content.ContentResolver
import android.net.Uri
import android.provider.DocumentsContract
import java.io.IOException
import java.io.InputStream

/** Android's folder picker's tree ([DocumentsContract]) as a [ForeverClientImport.Tree]. NOT run on a phone. */
class ForeverSafTree(private val resolver: ContentResolver, private val tree: Uri) : ForeverClientImport.Tree {
    override val rootId: String = DocumentsContract.getTreeDocumentId(tree)

    override fun list(id: String): List<ForeverClientImport.Entry> {
        val children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, id)
        val out = ArrayList<ForeverClientImport.Entry>()
        resolver.query(children, arrayOf(
            DocumentsContract.Document.COLUMN_DOCUMENT_ID, DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE, DocumentsContract.Document.COLUMN_SIZE,
        ), null, null, null)?.use { c ->
            while (c.moveToNext()) {
                val mime = c.getString(2).orEmpty()
                out += ForeverClientImport.Entry(c.getString(0), c.getString(1).orEmpty(), mime == DocumentsContract.Document.MIME_TYPE_DIR, if (c.isNull(3)) 0L else c.getLong(3))
            }
        }
        return out
    }

    override fun open(id: String): InputStream =
        resolver.openInputStream(DocumentsContract.buildDocumentUriUsingTree(tree, id)) ?: throw IOException("A file of the folder couldn't be opened")
}
