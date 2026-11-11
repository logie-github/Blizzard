package com.logie.blizz.porter.look

import com.logie.blizz.porter.wago.Row
import com.logie.blizz.porter.wago.Tables

/** One picture painted into a character's texture: where on the canvas, and how it mixes (the game's layer blend modes). */
data class Layer(val file: Int, val x: Int, val y: Int, val width: Int, val height: Int, val blend: Int)

/** One of the character's own textures, painted from [layers] in order on a canvas of [width] x [height]. */
data class Canvas(val width: Int, val height: Int, val layers: List<Layer>)

/** An item's model hung on one of the character's attachment points (11 the helm, 6 and 5 the shoulders, 1 and 2 the hands, 0 a shield, 53 a belt's buckle). */
data class Hung(val slot: String, val attachment: Int, val model: Int, val textures: Map<Int, Int>)

/** A model that moves with the character's bones: armour's pieces, or a customization's (horns, a blindfold): only [geosets] of it show, or all when empty. */
data class Skinned(val slot: String?, val model: Int, val textures: Map<Int, Int>, val geosets: List<Int>)

/** Everything the preview draws for one character: worked out from the game's tables by [Looks], drawn by porter/engine's viewer. */
data class CharacterLook(
    val race: Int,
    val sex: Int,
    val classId: Int,
    /** The race's model (its file id). */
    val model: Int,
    /** Geoset group to the value that shows (0: none of that group), over the model's defaults. */
    val geosetGroups: Map<Int, Int>,
    /** The textures painted from layers, by texture type (1 the skin, 6 the hair, 19 the eyes...). */
    val canvases: Map<Int, Canvas>,
    /** Textures that are one file, by type (2: the cape). */
    val textures: Map<Int, Int>,
    val hung: List<Hung>,
    val skinned: List<Skinned>,
    /** What could not be drawn and why ("Head: no look for item 123"), for the screen to say. */
    val notes: List<String> = emptyList(),
) {
    /** The models, the race's first. */
    fun models(): List<Int> = (listOf(model) + hung.map { it.model } + skinned.map { it.model }).filter { it > 0 }.distinct()

    /** Every file the look names itself (the models' own skins, skeletons and textures come from the models: [ModelFiles]). */
    fun files(): List<Int> = (models() + canvases.values.flatMap { c -> c.layers.map { it.file } } + textures.values +
        hung.flatMap { it.textures.values } + skinned.flatMap { it.textures.values }).filter { it > 0 }.distinct()
}

/** What a character wears, as the Armory gives it: the slot, the item, the item whose look it was given, the item's own look among its variants. */
data class Worn(val slot: String, val item: Int, val transmog: Int? = null, val appearance: Int? = null, val inventoryType: String = "")

/**
 * A character's look from the game's own tables ([Tables]: wago.tools'): the race's model and its customizations (the
 * choices given, or the race's defaults: the Armory doesn't give a character's), the skin painted from the race's layers,
 * and what is worn: the textures items paint on the body, the geosets they show (sleeves, a robe's skirt, boots), the
 * models hung on the body (helm, shoulders, weapons) and those that move with it (newer armour's pieces). The game's way,
 * as the game's tables lay it out; a desktop render of it was checked against the Armory's own pictures of the same
 * characters (porter/README.md). Plain Kotlin, unit-tested.
 */
class Looks(private val tables: Tables) {

    /** The look of race [race], sex [sex] (0 male, 1 female), class [classId], wearing [worn], with [choices] (option id to choice id) over the defaults. */
    fun of(race: Int, sex: Int, classId: Int, worn: List<Worn>, choices: Map<Int, Int> = emptyMap()): CharacterLook {
        val base = base(race, sex, classId, choices)
        return wear(base, worn)
    }

    // The body -------------------------------------------------------------------------------------------------------

    private class Base(
        val race: Int, val sex: Int, val classId: Int, val chrModel: Int, val model: Int, val layout: Int,
        val sections: Map<Int, IntArray>,
        val groups: MutableMap<Int, Int>,
        val canvases: MutableMap<Int, Triple<Int, Int, MutableList<Layer>>>,
        val skinned: MutableList<Skinned>,
    )

    private fun Row.order() = int("OrderIndex")

    private fun base(race: Int, sex: Int, classId: Int, picks: Map<Int, Int>): Base {
        val link = tables.rows("ChrRaceXChrModel", "ChrRacesID", race).filter { it.int("Sex") == sex }.minByOrNull { it.int("ID") }
            ?: throw IllegalArgumentException("The game has no model for race $race, sex $sex")
        val chrModel = tables.byId("ChrModel", link.int("ChrModelID")) ?: throw IllegalArgumentException("No ChrModel ${link.int("ChrModelID")}")
        val display = tables.byId("CreatureDisplayInfo", chrModel.int("DisplayID")) ?: throw IllegalArgumentException("No display for model ${chrModel.int("ID")}")
        val modelFile = tables.byId("CreatureModelData", display.int("ModelID"))?.int("FileDataID") ?: 0
        val layout = chrModel.int("CharComponentTextureLayoutID")

        // Each option's choice: the one given, else the first open to everyone (the race's default).
        val options = tables.rows("ChrCustomizationOption", "ChrModelID", chrModel.int("ID")).sortedBy { it.order() }
        val choicesByOption = tables.rows("ChrCustomizationChoice", "ChrCustomizationOptionID", options.map { it.int("ID") })
            .groupBy { it.int("ChrCustomizationOptionID") }
        val chosen = LinkedHashMap<Int, Int>()
        for (option in options) {
            val list = choicesByOption[option.int("ID")].orEmpty().sortedWith(compareBy({ it.order() }, { it.int("ID") }))
            if (list.isEmpty()) continue
            val pick = list.firstOrNull { it.int("ID") == picks[option.int("ID")] }
                ?: (list.filter { it.int("ChrCustomizationReqID") == 0 }.ifEmpty { list }).first()
            chosen[option.int("ID")] = pick.int("ID")
        }
        val chosenIds = chosen.values.toSet()

        // What the choices do: geosets, materials (textures by target), models that move with the body.
        val elements = tables.rows("ChrCustomizationElement", "ChrCustomizationChoiceID", chosenIds)
        val geosets = tables.rows("ChrCustomizationGeoset", "ID", elements.map { it.int("ChrCustomizationGeosetID") }.filter { it != 0 }).associateBy { it.int("ID") }
        val materials = tables.rows("ChrCustomizationMaterial", "ID", elements.map { it.int("ChrCustomizationMaterialID") }.filter { it != 0 }).associateBy { it.int("ID") }
        val skinnedRows = tables.rows("ChrCustomizationSkinnedModel", "ID", elements.map { it.int("ChrCustomizationSkinnedModelID") }.filter { it != 0 }).associateBy { it.int("ID") }
        val groups = HashMap<Int, Int>()
        val byTarget = HashMap<Int, Int>()
        val skinned = ArrayList<Skinned>()
        for (choice in chosen.values) {
            // An element tied to another choice counts only with that one chosen; it then wins over the plain ones.
            val mine = elements.filter { it.int("ChrCustomizationChoiceID") == choice }.sortedBy { if (it.int("RelatedChrCustomizationChoiceID") != 0) 1 else 0 }
            for (e in mine) {
                val related = e.int("RelatedChrCustomizationChoiceID")
                if (related != 0 && related !in chosenIds) continue
                geosets[e.int("ChrCustomizationGeosetID")]?.let { groups[it.int("GeosetType")] = it.int("GeosetID") }
                materials[e.int("ChrCustomizationMaterialID")]?.let { byTarget[it.int("ChrModelTextureTargetID")] = it.int("MaterialResourcesID") }
                skinnedRows[e.int("ChrCustomizationSkinnedModelID")]?.let { s ->
                    val file = s.int("CollectionsFileDataID")
                    val geoset = s.int("GeosetType") * 100 + s.int("GeosetID")
                    val at = skinned.indexOfFirst { it.model == file }
                    if (at < 0) skinned += Skinned(null, file, emptyMap(), listOf(geoset))
                    else skinned[at] = skinned[at].copy(geosets = skinned[at].geosets + geoset)
                }
            }
        }

        val sections = tables.rows("CharComponentTextureSections", "CharComponentTextureLayoutID", layout)
            .associate { it.int("SectionType") to intArrayOf(it.int("X"), it.int("Y"), it.int("Width"), it.int("Height")) }
        val canvases = HashMap<Int, Triple<Int, Int, MutableList<Layer>>>()
        for (m in tables.rows("ChrModelMaterial", "CharComponentTextureLayoutsID", layout)) {
            canvases[m.int("TextureType")] = Triple(m.int("Width"), m.int("Height"), ArrayList())
        }
        val layers = tables.rows("ChrModelTextureLayer", "CharComponentTextureLayoutsID", layout).sortedBy { it.int("Layer") }
        val files = textureFiles(layers.mapNotNull { byTarget[it.int("ChrModelTextureTargetID_0")] }, sex, classId, race)
        for (layer in layers) {
            val material = byTarget[layer.int("ChrModelTextureTargetID_0")] ?: continue
            val canvas = canvases[layer.int("TextureType")] ?: continue
            val file = files[material] ?: continue
            val mask = layer.int("TextureSectionTypeBitMask")
            val rects = if (mask == -1) listOf(intArrayOf(0, 0, canvas.first, canvas.second))
            else sections.keys.sorted().filter { mask and (1 shl it) != 0 }.mapNotNull { sections[it] }
            for (r in rects) canvas.third += Layer(file, r[0], r[1], r[2], r[3], layer.int("BlendMode"))
        }
        return Base(race, sex, classId, chrModel.int("ID"), modelFile, layout, sections, groups, canvases, skinned)
    }

    /**
     * The picture of each material: its diffuse file; of several (made for each sex, class or race), the one that fits this
     * character best (ComponentTextureFileData).
     */
    private fun textureFiles(materials: Collection<Int>, sex: Int, classId: Int, race: Int): Map<Int, Int> {
        val wanted = materials.filter { it != 0 }.distinct()
        if (wanted.isEmpty()) return emptyMap()
        val rows = tables.rows("TextureFileData", "MaterialResourcesID", wanted).filter { it.int("UsageType") == 0 }
        val byMaterial = rows.groupBy { it.int("MaterialResourcesID") }
        val several = byMaterial.values.filter { it.size > 1 }.flatten().map { it.int("FileDataID") }
        val components = if (several.isEmpty()) emptyMap() else tables.rows("ComponentTextureFileData", "ID", several).associateBy { it.int("ID") }
        val out = HashMap<Int, Int>()
        for ((material, list) in byMaterial) {
            if (list.size == 1) { out[material] = list[0].int("FileDataID"); continue }
            var best = 0
            var score = -1
            for (r in list) {
                val file = r.int("FileDataID")
                val c = components[file]
                val s = if (c == null) 1 else {
                    val g = c.int("GenderIndex"); val cl = c.int("ClassID"); val ra = c.int("RaceID")
                    if (g != sex && g != 2 && g != 3) -1
                    else if (cl != 0 && cl != classId) -1
                    else if (ra != 0 && ra != race) -1
                    else (if (g == sex) 4 else 2) + (if (cl != 0) 2 else 0) + (if (ra != 0) 2 else 0)
                }
                if (s > score) { best = file; score = s }
            }
            out[material] = if (best != 0) best else list[0].int("FileDataID")
        }
        return out
    }

    // What is worn ------------------------------------------------------------------------------------------------------

    private fun wear(base: Base, worn: List<Worn>): CharacterLook {
        val race = base.race; val sex = base.sex; val classId = base.classId
        val notes = ArrayList<String>()
        // Each item's look: the given variant of the item itself, else the item (or the item whose look it was given) in its plain variant.
        val shownItem = worn.associateWith { it.transmog ?: it.item }
        val variants = tables.rows("ItemModifiedAppearance", "ItemID", shownItem.values.distinct())
        val given = tables.rows("ItemModifiedAppearance", "ID", worn.filter { it.transmog == null }.mapNotNull { it.appearance })
        val appearanceIds = (variants + given).map { it.int("ItemAppearanceID") }.distinct()
        val appearances = tables.rows("ItemAppearance", "ID", appearanceIds).associateBy { it.int("ID") }
        val displayIds = appearances.values.map { it.int("ItemDisplayInfoID") }.filter { it != 0 }.distinct()
        val displays = tables.rows("ItemDisplayInfo", "ID", displayIds).associateBy { it.int("ID") }
        fun displayOf(w: Worn): Row? {
            val item = shownItem.getValue(w)
            if (w.transmog == null && w.appearance != null) {
                given.firstOrNull { it.int("ID") == w.appearance && it.int("ItemID") == item }?.let { ima ->
                    appearances[ima.int("ItemAppearanceID")]?.let { displays[it.int("ItemDisplayInfoID")] }?.let { return it }
                }
            }
            for (ima in variants.filter { it.int("ItemID") == item }.sortedWith(compareBy({ it.int("ItemAppearanceModifierID") }, { it.int("OrderIndex") }))) {
                val display = appearances[ima.int("ItemAppearanceID")]?.let { displays[it.int("ItemDisplayInfoID")] }
                if (display != null) return display
            }
            return null
        }
        val displayOf = worn.associateWith { displayOf(it) }
        for ((w, d) in displayOf) if (d == null && w.slot in VISIBLE) notes += "${w.slot}: no look for item ${shownItem.getValue(w)}"

        // The textures items paint on the body and those their models wear, and the models themselves.
        val shown = displayOf.values.filterNotNull()
        val sectionMaterials = tables.rows("ItemDisplayInfoMaterialRes", "ItemDisplayInfoID", shown.map { it.int("ID") }.distinct())
        val modelMaterials = shown.flatMap { listOf(it.int("ModelMaterialResourcesID_0"), it.int("ModelMaterialResourcesID_1")) }.filter { it != 0 }
        val files = textureFiles(sectionMaterials.map { it.int("MaterialResourcesID") } + modelMaterials, sex, classId, race)
        val resources = shown.flatMap { listOf(it.int("ModelResourcesID_0"), it.int("ModelResourcesID_1")) }.filter { it != 0 }.distinct()
        val modelRows = tables.rows("ModelFileData", "ModelResourcesID", resources).groupBy { it.int("ModelResourcesID") }
        val multi = modelRows.values.filter { it.size > 1 }.flatten().map { it.int("FileDataID") }
        val componentModels = if (multi.isEmpty()) emptyMap() else tables.rows("ComponentModelFileData", "ID", multi).associateBy { it.int("ID") }
        val fallbacks = HashMap<Int, Row?>()
        fun fallback(r: Int, s: Int): Pair<Int, Int> {
            val row = fallbacks.getOrPut(r) { tables.byId("ChrRaces", r) } ?: return 0 to s
            val prefix = if (s == 0) "Male" else "Female"
            return row.int("${prefix}ModelFallbackRaceID") to row.int("${prefix}ModelFallbackSex")
        }
        /** The file of a model resource for this race and sex (a helm is made once for each); of a pair, the side asked for. */
        fun modelOf(resource: Int, position: Int? = null): Int {
            val list = modelRows[resource].orEmpty().map { it.int("FileDataID") }
            if (list.isEmpty()) return 0
            if (list.size == 1) return list[0]
            fun pick(r: Int, s: Int): Int {
                var best = 0
                var score = -1
                for (file in list) {
                    val c = componentModels[file] ?: continue
                    val g = c.int("GenderIndex"); val cl = c.int("ClassID"); val ra = c.int("RaceID"); val pos = c.int("PositionIndex")
                    if (position != null && pos != position && pos != -1) continue
                    if (ra != 0 && ra != r) continue
                    if (g != s && g != 2 && g != 3) continue
                    if (cl != 0 && cl != classId) continue
                    val sc = (if (ra == r) 4 else 0) + (if (g == s) 2 else 0) + (if (cl != 0) 1 else 0)
                    if (sc > score) { best = file; score = sc }
                }
                return best
            }
            var found = pick(race, sex)
            var r = race; var s = sex
            var guard = 0
            while (found == 0 && guard++ < 4) {
                val (fr, fs) = fallback(r, s)
                if (fr == 0) break
                r = fr; s = fs
                found = pick(r, s)
            }
            return if (found != 0) found else list[0]
        }

        val groups = HashMap(base.groups)
        val perGroup = HashMap<Int, MutableList<Pair<String, Int>>>()
        val painted = ArrayList<Triple<Int, Int, Int>>()   // (order, section, file)
        val hung = ArrayList<Hung>()
        val skinned = ArrayList(base.skinned)
        val textures = HashMap<Int, Int>()
        val helmVis = ArrayList<Int>()
        for (w in worn) {
            val d = displayOf[w] ?: continue
            val (order, geo) = SLOTS[w.slot] ?: (0 to emptyList())
            for ((index, group) in geo) {
                val v = d.int("GeosetGroup_$index")
                perGroup.getOrPut(group) { ArrayList() } += w.slot to (if (group == 20) (if (v == 0) 2 else v) else 1 + v)
            }
            if (order != 0) for (r in sectionMaterials.filter { it.int("ItemDisplayInfoID") == d.int("ID") }) {
                val section = r.int("ComponentSection")
                val file = files[r.int("MaterialResourcesID")] ?: continue
                if (section in base.sections) painted += Triple(order, section, file)
            }
            fun texture(i: Int): Map<Int, Int> = files[d.int("ModelMaterialResourcesID_$i")]?.let { mapOf(2 to it) } ?: emptyMap()
            val res0 = d.int("ModelResourcesID_0"); val res1 = d.int("ModelResourcesID_1")
            val type0 = d.int("ModelType_0"); val type1 = d.int("ModelType_1")
            fun hang(attachment: Int, resource: Int, i: Int, position: Int? = null) {
                val m = modelOf(resource, position)
                if (m != 0) hung += Hung(w.slot, attachment, m, texture(i))
            }
            fun skin(resource: Int, i: Int) {
                val m = modelOf(resource)
                if (m != 0) skinned += Skinned(w.slot, m, texture(i), emptyList())
            }
            when (w.slot) {
                "head" -> {
                    if (res0 != 0) hang(11, res0, 0)
                    if (res1 != 0 && type1 == 1) skin(res1, 1)
                    d.int("HelmetGeosetVis_$sex").takeIf { it != 0 }?.let { helmVis += it }
                }
                "shoulder" -> {
                    if (res0 != 0) hang(6, res0, 0, 0)
                    if (res1 != 0) hang(5, res1, 1, 1)
                }
                "waist" -> {
                    if (res0 != 0 && type0 == 0) hang(53, res0, 0)
                    if (res0 != 0 && type0 == 1) skin(res0, 0)
                    if (res1 != 0 && type1 == 1) skin(res1, 1)
                }
                "back" -> texture(0)[2]?.let { textures[2] = it }
                "weapon" -> if (res0 != 0) hang(if (w.inventoryType == "RANGED") 2 else 1, res0, 0)
                "offhand" -> if (res0 != 0) hang(if (w.inventoryType == "SHIELD") 0 else 2, res0, 0)
                else -> if (res0 != 0 && type0 == 1) skin(res0, 0)
            }
        }
        // A helm hides what the race's helm rules say (hair, ears, horns) for this race.
        if (helmVis.isNotEmpty()) {
            for (h in tables.rows("HelmetGeosetData", "HelmetGeosetVisDataID", helmVis)) if (h.int("RaceID") == race) groups[h.int("HideGeosetGroup")] = 0
        }
        // Where several items set one geoset group, the first of the group's order wins (gloves over sleeves, a robe over trousers).
        for ((group, values) in perGroup) {
            var pick = values.first()
            for (slot in PRIORITY[group].orEmpty()) {
                val hit = values.firstOrNull { it.first == slot }
                if (hit != null) { pick = hit; break }
            }
            groups[group] = pick.second
        }
        // A robe covers the boots' tops, as in the game.
        if (groups[13] == 2 && (groups[5] ?: 1) > 1) groups[5] = 1

        val canvases = base.canvases.mapValues { (type, c) ->
            val layers = ArrayList(c.third)
            if (type == 1) for ((_, section, file) in painted.sortedBy { it.first }) {
                val r = base.sections.getValue(section)
                layers += Layer(file, r[0], r[1], r[2], r[3], 1)
            }
            Canvas(c.first, c.second, layers)
        }.filterValues { it.layers.isNotEmpty() }
        return CharacterLook(race, sex, classId, base.model, groups, canvases, textures, hung, skinned, notes)
    }

    companion object {
        /** The Armory's slots that show on the body (rings, a neck and trinkets don't). */
        val VISIBLE = setOf("head", "shoulder", "back", "chest", "shirt", "tabard", "wrist", "hand", "waist", "leg", "foot", "weapon", "offhand")

        /**
         * Each slot's place in the order the body's textures are painted, and its item's geoset groups: (index into
         * ItemDisplayInfo.GeosetGroup, the character's geoset group). Slots with 0 paint nothing on the body.
         */
        private val SLOTS: Map<String, Pair<Int, List<Pair<Int, Int>>>> = mapOf(
            "shirt" to (10 to listOf(0 to 8, 1 to 10)),
            "leg" to (20 to listOf(0 to 11, 1 to 9, 2 to 13)),
            "foot" to (30 to listOf(0 to 5, 1 to 20)),
            "chest" to (40 to listOf(0 to 8, 1 to 10, 2 to 13, 3 to 22, 4 to 28)),
            "wrist" to (50 to emptyList()),
            "hand" to (60 to listOf(0 to 4, 1 to 23)),
            "tabard" to (70 to listOf(0 to 12)),
            "waist" to (80 to listOf(0 to 18)),
            "head" to (0 to listOf(0 to 27, 1 to 21)),
            "shoulder" to (0 to listOf(0 to 26)),
            "back" to (0 to listOf(0 to 15)),
        )

        /** When several slots set one group, the first listed here wins. */
        private val PRIORITY = mapOf(8 to listOf("hand", "chest", "shirt"), 10 to listOf("chest", "shirt"), 13 to listOf("chest", "leg"))
    }
}
