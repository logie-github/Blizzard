package com.logie.blizz.porter.look

import com.logie.blizz.porter.armory.Armory
import com.logie.blizz.porter.armory.Region
import com.logie.blizz.porter.wago.CsvTables
import com.logie.blizz.porter.wago.Row
import com.logie.blizz.porter.wago.Tables
import com.logie.blizz.porter.wago.WagoTables
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * A character's look from the game's tables: on small tables written here (each rule of the game's on its own), and, with
 * `BLIZZ_PORTER_TABLES=<folder of wago.tools CSVs of build 12.1.5.70783>`, on the game's own tables for a real character
 * (the Armory's summary kept in the tests): the same look the desktop render of porter/harness was checked with.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class LooksTest {
    @get:Rule val tmp = TemporaryFolder()

    /** Tables given as rows: table name to its rows (each a column-to-value map). */
    private class MapTables(private val data: Map<String, List<Map<String, Any>>>) : Tables {
        override fun rows(table: String, column: String, values: Collection<Int>): List<Row> =
            data[table].orEmpty().map { r -> Row(r.mapValues { it.value.toString() }) }.filter { it.int(column) in values }
    }

    private fun r(vararg pairs: Pair<String, Any>): Map<String, Any> = mapOf(*pairs)

    /** One race (2, male) with two options, and a few items. */
    private val tables = MapTables(
        mapOf(
            "ChrRaceXChrModel" to listOf(r("ID" to 3, "ChrRacesID" to 2, "ChrModelID" to 3, "Sex" to 0), r("ID" to 4, "ChrRacesID" to 2, "ChrModelID" to 4, "Sex" to 1),
                r("ID" to 9, "ChrRacesID" to 99, "ChrModelID" to 3, "Sex" to 0)),
            "ChrModel" to listOf(r("ID" to 3, "DisplayID" to 100, "CharComponentTextureLayoutID" to 105)),
            "CreatureDisplayInfo" to listOf(r("ID" to 100, "ModelID" to 6838)),
            "CreatureModelData" to listOf(r("ID" to 6838, "FileDataID" to 917116)),
            "ChrCustomizationOption" to listOf(r("ID" to 21, "ChrModelID" to 3, "OrderIndex" to 1), r("ID" to 20, "ChrModelID" to 3, "OrderIndex" to 0)),
            "ChrCustomizationChoice" to listOf(
                r("ID" to 385, "ChrCustomizationOptionID" to 20, "ChrCustomizationReqID" to 0, "OrderIndex" to 1),
                r("ID" to 384, "ChrCustomizationOptionID" to 20, "ChrCustomizationReqID" to 0, "OrderIndex" to 0),
                // The first of option 21 needs something (a quest, a race): the default is the first open to all.
                r("ID" to 402, "ChrCustomizationOptionID" to 21, "ChrCustomizationReqID" to 5, "OrderIndex" to 0),
                r("ID" to 403, "ChrCustomizationOptionID" to 21, "ChrCustomizationReqID" to 0, "OrderIndex" to 1),
            ),
            "ChrCustomizationElement" to listOf(
                r("ID" to 1, "ChrCustomizationChoiceID" to 384, "ChrCustomizationMaterialID" to 10),
                r("ID" to 2, "ChrCustomizationChoiceID" to 403, "ChrCustomizationGeosetID" to 2, "ChrCustomizationMaterialID" to 11),
                // Counts only with choice 384 chosen (it is), and wins over the plain one for the same target.
                r("ID" to 3, "ChrCustomizationChoiceID" to 403, "RelatedChrCustomizationChoiceID" to 384, "ChrCustomizationMaterialID" to 12),
                r("ID" to 4, "ChrCustomizationChoiceID" to 403, "ChrCustomizationMaterialID" to 13),
                // Tied to a choice not chosen: nothing.
                r("ID" to 5, "ChrCustomizationChoiceID" to 403, "RelatedChrCustomizationChoiceID" to 999, "ChrCustomizationGeosetID" to 3),
                r("ID" to 6, "ChrCustomizationChoiceID" to 385, "ChrCustomizationGeosetID" to 3),
                r("ID" to 7, "ChrCustomizationChoiceID" to 384, "ChrCustomizationSkinnedModelID" to 50),
                r("ID" to 8, "ChrCustomizationChoiceID" to 403, "ChrCustomizationSkinnedModelID" to 51),
            ),
            "ChrCustomizationGeoset" to listOf(r("ID" to 2, "GeosetType" to 0, "GeosetID" to 7), r("ID" to 3, "GeosetType" to 7, "GeosetID" to 2)),
            "ChrCustomizationMaterial" to listOf(
                r("ID" to 10, "ChrModelTextureTargetID" to 1, "MaterialResourcesID" to 500),
                r("ID" to 11, "ChrModelTextureTargetID" to 10, "MaterialResourcesID" to 501),
                r("ID" to 12, "ChrModelTextureTargetID" to 5, "MaterialResourcesID" to 502),
                r("ID" to 13, "ChrModelTextureTargetID" to 5, "MaterialResourcesID" to 503),
            ),
            "ChrCustomizationSkinnedModel" to listOf(
                r("ID" to 50, "CollectionsFileDataID" to 7760203, "GeosetType" to 25, "GeosetID" to 0),
                r("ID" to 51, "CollectionsFileDataID" to 7760203, "GeosetType" to 24, "GeosetID" to 3),
            ),
            "CharComponentTextureSections" to listOf(
                r("CharComponentTextureLayoutID" to 105, "SectionType" to 3, "X" to 512, "Y" to 0, "Width" to 512, "Height" to 256),
                r("CharComponentTextureLayoutID" to 105, "SectionType" to 10, "X" to 1024, "Y" to 0, "Width" to 1024, "Height" to 1024),
            ),
            "ChrModelMaterial" to listOf(
                r("CharComponentTextureLayoutsID" to 105, "TextureType" to 1, "Width" to 2048, "Height" to 1024),
                r("CharComponentTextureLayoutsID" to 105, "TextureType" to 6, "Width" to 512, "Height" to 256),
                r("CharComponentTextureLayoutsID" to 105, "TextureType" to 19, "Width" to 256, "Height" to 128),
            ),
            "ChrModelTextureLayer" to listOf(
                r("CharComponentTextureLayoutsID" to 105, "TextureType" to 1, "Layer" to 3, "BlendMode" to 15, "TextureSectionTypeBitMask" to 1024, "ChrModelTextureTargetID_0" to 5),
                r("CharComponentTextureLayoutsID" to 105, "TextureType" to 1, "Layer" to 0, "BlendMode" to 1, "TextureSectionTypeBitMask" to -1, "ChrModelTextureTargetID_0" to 1),
                r("CharComponentTextureLayoutsID" to 105, "TextureType" to 6, "Layer" to 1, "BlendMode" to 1, "TextureSectionTypeBitMask" to -1, "ChrModelTextureTargetID_0" to 10),
            ),
            "TextureFileData" to listOf(
                r("FileDataID" to 9000, "UsageType" to 0, "MaterialResourcesID" to 500),
                r("FileDataID" to 8999, "UsageType" to 1, "MaterialResourcesID" to 500),
                r("FileDataID" to 9001, "UsageType" to 0, "MaterialResourcesID" to 501),
                // A face made for each sex: the man's.
                r("FileDataID" to 9002, "UsageType" to 0, "MaterialResourcesID" to 502),
                r("FileDataID" to 9003, "UsageType" to 0, "MaterialResourcesID" to 502),
                r("FileDataID" to 9100, "UsageType" to 0, "MaterialResourcesID" to 600),
                r("FileDataID" to 9101, "UsageType" to 0, "MaterialResourcesID" to 601),
                r("FileDataID" to 9200, "UsageType" to 0, "MaterialResourcesID" to 72),
                r("FileDataID" to 9300, "UsageType" to 0, "MaterialResourcesID" to 73),
            ),
            "ComponentTextureFileData" to listOf(r("ID" to 9002, "GenderIndex" to 1, "ClassID" to 0, "RaceID" to 0), r("ID" to 9003, "GenderIndex" to 0, "ClassID" to 0, "RaceID" to 0)),
            // Items: a robe (shown as another item), trousers, boots, a helm, shoulders, a cloak, a bow.
            "ItemModifiedAppearance" to listOf(
                r("ID" to 1, "ItemID" to 2000, "ItemAppearanceID" to 30, "ItemAppearanceModifierID" to 0, "OrderIndex" to 0),
                r("ID" to 2, "ItemID" to 2000, "ItemAppearanceID" to 31, "ItemAppearanceModifierID" to 3, "OrderIndex" to 0),
                r("ID" to 3, "ItemID" to 1001, "ItemAppearanceID" to 32, "ItemAppearanceModifierID" to 0),
                r("ID" to 4, "ItemID" to 1002, "ItemAppearanceID" to 33, "ItemAppearanceModifierID" to 0),
                r("ID" to 5, "ItemID" to 1003, "ItemAppearanceID" to 34, "ItemAppearanceModifierID" to 0),
                r("ID" to 6, "ItemID" to 1004, "ItemAppearanceID" to 35, "ItemAppearanceModifierID" to 0),
                r("ID" to 7, "ItemID" to 1005, "ItemAppearanceID" to 36, "ItemAppearanceModifierID" to 0),
                r("ID" to 8, "ItemID" to 1006, "ItemAppearanceID" to 37, "ItemAppearanceModifierID" to 0),
                // The bow's heroic variant, which the Armory names.
                r("ID" to 9, "ItemID" to 1006, "ItemAppearanceID" to 38, "ItemAppearanceModifierID" to 1),
            ),
            "ItemAppearance" to listOf(
                r("ID" to 30, "ItemDisplayInfoID" to 40), r("ID" to 31, "ItemDisplayInfoID" to 49), r("ID" to 32, "ItemDisplayInfoID" to 41),
                r("ID" to 33, "ItemDisplayInfoID" to 42), r("ID" to 34, "ItemDisplayInfoID" to 43), r("ID" to 35, "ItemDisplayInfoID" to 44),
                r("ID" to 36, "ItemDisplayInfoID" to 45), r("ID" to 37, "ItemDisplayInfoID" to 46), r("ID" to 38, "ItemDisplayInfoID" to 47),
            ),
            "ItemDisplayInfo" to listOf(
                r("ID" to 40, "GeosetGroup_2" to 1),
                r("ID" to 41, "GeosetGroup_2" to 0),
                r("ID" to 42, "GeosetGroup_0" to 2),
                r("ID" to 43, "ModelResourcesID_0" to 70, "ModelMaterialResourcesID_0" to 72, "HelmetGeosetVis_0" to 80),
                r("ID" to 44, "ModelResourcesID_0" to 71, "ModelResourcesID_1" to 71, "ModelMaterialResourcesID_0" to 72, "ModelMaterialResourcesID_1" to 72),
                r("ID" to 45, "ModelMaterialResourcesID_0" to 73, "ModelType_0" to 5),
                r("ID" to 46, "ModelResourcesID_0" to 74),
                r("ID" to 47, "ModelResourcesID_0" to 75),
            ),
            "ItemDisplayInfoMaterialRes" to listOf(
                r("ItemDisplayInfoID" to 40, "ComponentSection" to 3, "MaterialResourcesID" to 600),
                r("ItemDisplayInfoID" to 41, "ComponentSection" to 3, "MaterialResourcesID" to 601),
            ),
            "ModelFileData" to listOf(
                r("FileDataID" to 7001, "ModelResourcesID" to 70), r("FileDataID" to 7002, "ModelResourcesID" to 70),
                r("FileDataID" to 7101, "ModelResourcesID" to 71), r("FileDataID" to 7102, "ModelResourcesID" to 71),
                r("FileDataID" to 7401, "ModelResourcesID" to 74), r("FileDataID" to 7501, "ModelResourcesID" to 75),
            ),
            "ComponentModelFileData" to listOf(
                r("ID" to 7001, "GenderIndex" to 0, "ClassID" to 0, "RaceID" to 2, "PositionIndex" to -1),
                r("ID" to 7002, "GenderIndex" to 0, "ClassID" to 0, "RaceID" to 1, "PositionIndex" to -1),
                r("ID" to 7101, "GenderIndex" to 2, "ClassID" to 0, "RaceID" to 0, "PositionIndex" to 0),
                r("ID" to 7102, "GenderIndex" to 2, "ClassID" to 0, "RaceID" to 0, "PositionIndex" to 1),
            ),
            "HelmetGeosetData" to listOf(r("HelmetGeosetVisDataID" to 80, "RaceID" to 2, "HideGeosetGroup" to 0), r("HelmetGeosetVisDataID" to 80, "RaceID" to 1, "HideGeosetGroup" to 7)),
            "ChrRaces" to listOf(r("ID" to 99, "MaleModelFallbackRaceID" to 2, "MaleModelFallbackSex" to 0)),
        ),
    )

    private val worn = listOf(
        Worn("chest", 1000, transmog = 2000),
        Worn("leg", 1001),
        Worn("foot", 1002),
        Worn("head", 1003),
        Worn("shoulder", 1004),
        Worn("back", 1005),
        Worn("weapon", 1006, appearance = 9, inventoryType = "RANGED"),
        Worn("neck", 1007),
    )

    @Test fun theBodyIsTheRacesModelWithItsDefaultChoices() {
        val look = Looks(tables).of(2, 0, 9, emptyList())
        assertEquals(917116, look.model)
        // Option 20's first (384) and option 21's first open to all (403); 385's geoset isn't there.
        assertEquals(mapOf(0 to 7), look.geosetGroups)
        // The skin: 384's material over the whole canvas, then 403's tied to 384 (the man's file of two) in its section.
        assertEquals(listOf(Layer(9000, 0, 0, 2048, 1024, 1), Layer(9003, 1024, 0, 1024, 1024, 15)), look.canvases.getValue(1).layers)
        assertEquals(listOf(Layer(9001, 0, 0, 512, 256, 1)), look.canvases.getValue(6).layers)
        // A canvas nothing paints isn't there.
        assertTrue(19 !in look.canvases)
        // One model that moves with the body, showing the geosets of the two choices that turn its parts on.
        assertEquals(listOf(Skinned(null, 7760203, emptyMap(), listOf(2500, 2403))), look.skinned)
        // A choice given over the default.
        assertEquals(mapOf(0 to 7, 7 to 2), Looks(tables).of(2, 0, 9, emptyList(), choices = mapOf(20 to 385)).geosetGroups)
    }

    @Test fun whatIsWornPaintsTheBodyShowsItsGeosetsAndHangsItsModels() {
        val look = Looks(tables).of(2, 0, 9, worn)
        // The robe's look (the item it was given), its texture in the chest's section over the trousers'.
        val skin = look.canvases.getValue(1).layers
        assertEquals(listOf(Layer(9101, 512, 0, 512, 256, 1), Layer(9100, 512, 0, 512, 256, 1)), skin.drop(2))
        // The robe's skirt wins over the trousers', so the boots' tops go (a robe covers them); the helm hides the hair (group 0) for this race.
        assertEquals(2, look.geosetGroups[13])
        assertEquals(1, look.geosetGroups[5])
        assertEquals(0, look.geosetGroups[0])
        assertEquals(1, look.geosetGroups[11])
        // The helm made for this race; the shoulders each on its side; the bow in the left hand, in the variant the Armory named.
        assertEquals(
            listOf(Hung("head", 11, 7001, mapOf(2 to 9200)), Hung("shoulder", 6, 7101, mapOf(2 to 9200)), Hung("shoulder", 5, 7102, mapOf(2 to 9200)), Hung("weapon", 2, 7501, emptyMap())),
            look.hung,
        )
        assertEquals(mapOf(2 to 9300), look.textures)
        // A neck shows nothing, and says nothing.
        assertEquals(emptyList<String>(), look.notes)
        assertTrue(look.files().containsAll(listOf(917116, 7001, 7101, 7102, 7501, 9000, 9100, 9101, 9200, 9300)))
    }

    @Test fun aRaceWithoutItsOwnHelmBorrowsItsFallbacksAndAnUnknownItemIsSaid() {
        val look = Looks(tables).of(99, 0, 9, listOf(Worn("head", 1003), Worn("hand", 4242)))
        assertEquals(7001, look.hung.single().model)
        assertEquals(listOf("hand: no look for item 4242"), look.notes)
    }

    @Test fun aModelsFilesAreReadFromItsChunks() {
        fun chunk(tag: String, vararg ints: Int): ByteArray {
            val body = java.nio.ByteBuffer.allocate(ints.size * 4).order(java.nio.ByteOrder.LITTLE_ENDIAN)
            for (i in ints) body.putInt(i)
            return java.nio.ByteBuffer.allocate(8).order(java.nio.ByteOrder.LITTLE_ENDIAN).put(tag.toByteArray()).putInt(ints.size * 4).array() + body.array()
        }
        val afid = java.nio.ByteBuffer.allocate(8 + 24).order(java.nio.ByteOrder.LITTLE_ENDIAN).put("AFID".toByteArray()).putInt(24)
            .putShort(0).putShort(0).putInt(501).putShort(0).putShort(1).putInt(502).putShort(4).putShort(0).putInt(503).array()
        val model = tmp.newFile("model")
        model.writeBytes(chunk("MD21", 0, 0) + chunk("SFID", 100, 101) + chunk("TXID", 200, 0, 201) + afid + chunk("SKID", 300))
        val found = ModelFiles.of(model)!!
        assertEquals(100, found.skin)
        assertEquals(listOf(200, 201), found.textures)
        // The standing animation's file only, in its first variation.
        assertEquals(listOf(501), found.animations)
        assertEquals(300, found.skeleton)
        val skeleton = tmp.newFile("skeleton")
        skeleton.writeBytes(chunk("SKL1", 0, 0) + chunk("SKPD", 0, 0, 400, 0) + afid)
        val s = ModelFiles.skeleton(skeleton)!!
        assertEquals(400, s.skeleton)
        assertEquals(listOf(501), s.animations)
        // Not a model of today's kind.
        assertEquals(null, ModelFiles.of(tmp.newFile("empty").apply { writeBytes(ByteArray(16)) }))
    }

    private fun armoryCharacter() = Armory.parseCharacter(Region.US, String(javaClass.classLoader!!.getResourceAsStream("porter/armory-model.json")!!.readBytes()))

    private fun wornOf(c: com.logie.blizz.porter.armory.ArmoryCharacter) =
        c.items.map { Worn(it.slot, it.id, it.transmogItemId, it.modifiedAppearanceId, it.inventoryType) }

    /** What the desktop render was checked with (the prototype's own result for this character, build 12.1.5.70783). */
    private fun assertTheOrcWarlock(look: CharacterLook) {
        assertEquals(917116, look.model)
        assertEquals(
            listOf(Hung("head", 11, 1511309, mapOf(2 to 1511362)), Hung("shoulder", 6, 1511347, mapOf(2 to 1511369)), Hung("shoulder", 5, 1511348, mapOf(2 to 1511369)),
                Hung("waist", 53, 1511346, mapOf(2 to 1511378)), Hung("weapon", 1, 1689887, mapOf(2 to 6980570))).sortedBy { it.model },
            look.hung.sortedBy { it.model },
        )
        assertEquals(listOf(Skinned("hand", 1511283, mapOf(2 to 1511357), emptyList())), look.skinned.filter { it.slot != null })
        assertEquals(mapOf(2 to 461810), look.textures)
        assertEquals(2, look.geosetGroups[13])
        assertEquals(4, look.geosetGroups[4])
        assertEquals(17, look.canvases.getValue(1).layers.size)
    }

    @Test fun theGamesOwnTables() {
        val dir = System.getenv("BLIZZ_PORTER_TABLES")?.let { File(it) }
        assumeTrue(dir != null && File(dir, "ChrModel.csv").isFile)
        val c = armoryCharacter()
        assertTheOrcWarlock(Looks(CsvTables(dir!!)).of(c.raceId, c.gender, c.classId, wornOf(c)))
    }

    /** The same from wago.tools itself, a few rows at a time, then again from what was kept (no request). */
    @Test fun wagoTools() {
        assumeTrue(System.getenv("BLIZZ_PORTER_LIVE") == "1")
        val counting = object : com.logie.blizz.porter.net.Net {
            val real = com.logie.blizz.porter.net.HttpNet("BlizzardLauncher-test/1.0")
            var asked = 0
            override fun get(url: String, headers: Map<String, String>) = real.get(url, headers).also { asked++ }
            override fun post(url: String, body: ByteArray, headers: Map<String, String>) = real.post(url, body, headers)
            override fun save(url: String, to: File, headers: Map<String, String>, progress: (Long) -> Unit) = real.save(url, to, headers, progress)
        }
        val c = armoryCharacter()
        val cache = tmp.newFolder("tables")
        val first = Looks(WagoTables(counting, "12.1.5.70783", cache)).of(c.raceId, c.gender, c.classId, wornOf(c))
        assertTheOrcWarlock(first)
        val requests = counting.asked
        println("LooksTest live: $requests requests to wago.tools for one character")
        assertTrue("$requests requests", requests in 5..40)
        val again = Looks(WagoTables(counting, "12.1.5.70783", cache)).of(c.raceId, c.gender, c.classId, wornOf(c))
        assertEquals(first, again)
        assertEquals(requests, counting.asked)
    }
}
