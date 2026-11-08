# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's story's assets' rows (tools/naga/sounds.py, tools/naga/looks.py), for the game's tables
(the module's patch, data/client/dbc) and the world database (its `*_dbc` copies and creature_model_info):

  - SoundEntries 995000 to 995199: the Warcraft III voices (their WAVs: tools/naga_voices.py);
  - CreatureModelData 3800 to 3849: today's models made 3.3.5's (tools/naga_models.py);
  - CreatureDisplayInfo 40000 to 40299: their looks, and the looks made of the game's parts;
  - CreatureDisplayInfoExtra 25000 to 25099: those looks' race, skin, face, hair and items (no baked
    texture: the game dresses them from their items, as Wrath Remix's looks).

tools/build_data.py calls add_naga_assets(client, sql, D) once, in its main() (its Client, its Sql, its
reader of the server's tables). The rows are there whether or not the server package made the files:
a voice without its WAV plays nothing (its line shows as text), a look without its model draws nothing
(looks.FALLBACK says what to give those people instead).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from naga import looks as LK  # noqa: E402
from naga import sounds as S  # noqa: E402

DISPLAY_TYPES = "iiiifissssiiiiii"                                   # (build_data.py's for the same tables)
MODEL_TYPES = "iisifiiffffiiifff" + "ffffff" + "fffff"
EXTRA_TYPES = "i" * 20 + "s"
VOICE_TEMPLATE = 11531                                               # Lady Vashj's Serpentshrine intro line
EXTRA_COLUMNS = ["ID", "DisplayRaceID", "DisplaySexID", "SkinID", "FaceID", "HairStyleID", "HairColorID", "FacialHairID"] \
    + ["NPCItemDisplay%d" % i for i in range(1, 12)] + ["Flags", "BakeName"]
DISPLAY_COLUMNS = ["ID", "ModelID", "SoundID", "ExtendedDisplayInfoID", "CreatureModelScale", "CreatureModelAlpha",
                   "TextureVariation_1", "TextureVariation_2", "TextureVariation_3", "PortraitTextureName", "BloodLevel",
                   "BloodID", "NPCSoundID", "ParticleColorID", "CreatureGeosetData", "ObjectEffectPackageID"]
MODEL_COLUMNS = ["ID", "Flags", "ModelName", "SizeClass", "ModelScale", "BloodID", "FootprintTextureID",
                 "FootprintTextureLength", "FootprintTextureWidth", "FootprintParticleScale", "FoleyMaterialID",
                 "FootstepShakeSize", "DeathThudShakeSize", "SoundID", "CollisionWidth", "CollisionHeight", "MountHeight",
                 "GeoBoxMinX", "GeoBoxMinY", "GeoBoxMinZ", "GeoBoxMaxX", "GeoBoxMaxY", "GeoBoxMaxZ", "WorldEffectScale",
                 "AttachedEffectScale", "MissileCollisionRadius", "MissileCollisionPush", "MissileCollisionRaise"]


def add_naga_assets(client, sql, D):
    import build_data as B                                           # (its row helpers; it's the caller)
    import json
    types = json.load(open(os.path.join(HERE, "..", "..", "mod-allied-races", "tools", "dbc_types.json")))

    def rows_of(name):
        table = D(name)
        return table, {r[0]: r for r in table.rows}

    def replace(table, columns, kinds, rows):
        sql.raw("REPLACE INTO `%s` (%s) VALUES\n" % (table, ", ".join("`%s`" % c for c in columns))
                + ",\n".join("(" + ", ".join(B.sql_value(v, t) for v, t in zip(r, kinds)) + ")" for r in rows) + ";")

    # The voices: a SoundEntries row each, as Lady Vashj's own lines are (a creature's speech: its
    # volume and distances), the module's WAV in its folder.
    sounds, sound_rows = rows_of("SoundEntries")
    snt = types["soundentries_dbc"]
    voice_rows = []
    for name, sound_id in S.SOUNDS.items():
        v = B.values_of(sounds, sound_rows[VOICE_TEMPLATE], snt)
        v[0], v[2] = sound_id, "NagaStory_" + name
        v[3:13] = [S.file_name(name)] + [""] * 9
        v[13:23] = [1] + [0] * 9
        v[23] = S.DIRECTORY
        client.put("SoundEntries", snt, v)
        voice_rows.append(v)
    sql.comment("The naga's story's Warcraft III voices (tools/naga/sounds.py): their WAVs are the server package's (never in\n"
                "this repository); without them the game plays nothing and the lines show as text.")
    sql.raw("DELETE FROM `soundentries_dbc` WHERE `ID` BETWEEN %d AND %d;" % (S.FIRST_ID, S.LAST_ID))
    sql.replace_dbc("soundentries_dbc", snt, voice_rows)

    # Today's models made 3.3.5's: a CreatureModelData row each, copied from the game's model of the
    # same size (footprints, blood, collision), with its own name, sounds and box.
    models, model_rows = rows_of("CreatureModelData")
    displays, display_rows = rows_of("CreatureDisplayInfo")
    new_models, new_displays, info = [], [], []
    for c in LK.CREATURES:
        m = B.values_of(models, model_rows[c["template"]], MODEL_TYPES)
        m[0], m[1] = c["model_data"], 0
        m[2] = "%s\\%s.mdx" % (c["folder"].replace("/", "\\"), c["name"])
        m[13] = c["sound"]
        m[17:23] = list(c["box"])
        client.put("CreatureModelData", MODEL_TYPES, m)
        new_models.append(m)
    for display, (model_data, template, scale, skins) in sorted(LK.CREATURE_LOOKS.items()):
        d = B.values_of(displays, display_rows[template], DISPLAY_TYPES)
        d[0], d[1], d[3], d[4] = display, model_data, 0, scale
        d[6], d[7], d[8], d[9] = skins[0], skins[1], skins[2], ""
        d[12], d[14] = 0, 0                                            # (no NPC voice of the template's; every geoset)
        client.put("CreatureDisplayInfo", DISPLAY_TYPES, d)
        new_displays.append(d)
        info.append((display, template))

    # Looks of the game's parts: a CreatureDisplayInfoExtra row each (no baked texture: dressed from its
    # items), and a CreatureDisplayInfo row copied from a look of the same race and sex with it.
    extras = []
    for display, (extra, template, race, sex, skin, face, hair, colour, facial, items) in sorted(LK.PARTS_LOOKS.items()):
        x = [extra, race, sex, skin, face, hair, colour, facial] + list(items) + [0, ""]
        client.put("CreatureDisplayInfoExtra", EXTRA_TYPES, x)
        extras.append(x)
        d = B.values_of(displays, display_rows[template], DISPLAY_TYPES)
        d[0], d[3] = display, extra
        client.put("CreatureDisplayInfo", DISPLAY_TYPES, d)
        new_displays.append(d)
        info.append((display, template))

    sql.comment("The naga's story's looks (tools/naga/looks.py): today's sea witch, warden and Queen Azshara made 3.3.5's (their\n"
                "files the server package's), and looks made of the game's parts; their sizes the game's people's they're\n"
                "copied from.")
    for table, lo, hi in (("creaturemodeldata_dbc", LK.MODEL_DATA_FIRST, LK.MODEL_DATA_LAST),
                          ("creaturedisplayinfo_dbc", LK.DISPLAY_FIRST, LK.DISPLAY_LAST),
                          ("creaturedisplayinfoextra_dbc", LK.EXTRA_FIRST, LK.EXTRA_LAST)):
        sql.raw("DELETE FROM `%s` WHERE `ID` BETWEEN %d AND %d;" % (table, lo, hi))
    replace("creaturemodeldata_dbc", MODEL_COLUMNS, MODEL_TYPES, new_models)
    replace("creaturedisplayinfo_dbc", DISPLAY_COLUMNS, DISPLAY_TYPES, new_displays)
    replace("creaturedisplayinfoextra_dbc", EXTRA_COLUMNS, EXTRA_TYPES, extras)
    # (a person's size: the game's for a humanoid, 0.306 yards about and 1.5 of reach; the women's
    # gender, the sea witch and the warden's included)
    sql.raw("DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN %d AND %d;" % (LK.DISPLAY_FIRST, LK.DISPLAY_LAST))
    sql.raw("INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES\n"
            + ",\n".join("(%d, 0.306, 1.5, %d, 0)" % (display, LK.PARTS_LOOKS[display][3] if display in LK.PARTS_LOOKS else 1)
                         for display, _ in info) + ";")
