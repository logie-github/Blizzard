package com.logie.blizz.wowmodules

import com.logie.blizz.wowmodules.ModuleReadme.Block
import org.junit.Test
import org.junit.Assert.assertEquals

class ModuleReadmeTest {
    @Test
    fun readsAModulesReadme() {
        val markdown = """
            # ![logo](icon.png) mod-transmog [![Build](https://img.shields.io/badge.svg)](https://ci)

            <!-- a comment
                 over lines -->
            Lets players **change** the look of their _gear_, with an [NPC](https://wiki/npc) and `.transmog` commands.
            It costs gold.

            ## Installation
            1. Clone it into `modules/`
            2) Re-run cmake
            - [x] Done
            * Apply the SQL

            ```sh
            git clone https://github.com/azerothcore/mod-transmog
            ```

            | Setting | Default |
            |---|:---:|
            | Transmogrification.Enable | 1 |

            > Note: back up first.

            ---
            Made by <b>someone</b>&nbsp;&amp; friends.<br>Thanks.
        """.trimIndent()
        assertEquals(
            listOf(
                Block.Heading("mod-transmog"),
                Block.Paragraph("Lets players change the look of their gear, with an NPC and .transmog commands. It costs gold."),
                Block.Heading("Installation"),
                Block.Item("Clone it into modules/", 1),
                Block.Item("Re-run cmake", 2),
                Block.Item("Done", null),
                Block.Item("Apply the SQL", null),
                Block.Code("git clone https://github.com/azerothcore/mod-transmog"),
                Block.Paragraph("Setting · Default"),
                Block.Paragraph("Transmogrification.Enable · 1"),
                Block.Paragraph("Note: back up first."),
                Block.Rule,
                Block.Paragraph("Made by someone & friends. Thanks."),
            ),
            ModuleReadme.blocks(markdown),
        )
    }

    @Test
    fun windowsLineEndingsAndNothing() {
        assertEquals(listOf(Block.Heading("Title"), Block.Paragraph("one two")), ModuleReadme.blocks("# Title\r\n\r\none\r\ntwo\r\n"))
        assertEquals(emptyList<Any>(), ModuleReadme.blocks(""))
        assertEquals(emptyList<Any>(), ModuleReadme.blocks("![only a picture](x.png)"))
    }
}
