"""The game's paths of the races' textures, as tools/textures.py writes them and the tables
(tools/build_data.py) name them. A face's FaceLower is named by the face texture it's cut from
and the eye glow painted into it (nightborne), its FaceUpper by the eye colour: a face number
on a skin draws on the same files as every other that takes the same pictures."""


def race_folder(model):
    return model["folder"].rsplit("\\", 1)[0]


def files_of(model, colour):
    """The colour's number in the files' names: a look made of another model's skins (Wrath++'s High Elf is the Void Elf's
    high elf skins, renumbered from 0) names its file by [model]'s "file_index"; else the colour itself."""
    return model.get("file_index", {}).get(str(colour), colour)


def skin(model, colour):
    colour = files_of(model, colour)
    return "%s\\%sSkin00_%02d.blp" % (model["folder"], model["name"], colour)


def skin_extra(model, colour):
    """the skin's second texture (3.3.5's skin extra: m2.py draws the parts the face's place can't hold on it)"""
    return "%s\\%sSkin00_%02d_Extra.blp" % (model["folder"], model["name"], colour)


def pelvis(model, colour):
    colour = files_of(model, colour)
    return "%s\\%sNakedPelvisSkin00_%02d.blp" % (model["folder"], model["name"], colour)


def torso(model, colour):
    colour = files_of(model, colour)
    return "%s\\%sNakedTorsoSkin00_%02d.blp" % (model["folder"], model["name"], colour)


def hair(model, colour):
    return "%s\\%sHair00_%02d.blp" % (race_folder(model), model["name"], colour)


def overlay(model, file_id):
    """a picture laid over the head by a part (sl_parts: eyebrows, makeup, scars...), named by today's file"""
    return "%s\\%sOv%d.blp" % (model["folder"], model["name"], file_id)


def body_overlay(model, file_id):
    """a picture laid over the body by a part (sl_parts.body_shell), named by today's file"""
    return "%s\\%sBo%d.blp" % (model["folder"], model["name"], file_id)


def body_shell(model):
    """the body shell its pictures are drawn on (sl_parts.body_shell)"""
    return "%s\\%sBody.m2" % (model["folder"], model["name"])


def shell(model):
    """the head shell a part's pictures are drawn on (sl_parts.head_shell)"""
    return "%s\\%sFace.m2" % (model["folder"], model["name"])


def scalp(model, file_id):
    """a hair style's scalp for one hair colour (ScalpLower, a layer over FaceLower): named by today's file"""
    return "%s\\%sScalp%d.blp" % (model["folder"], model["name"], file_id)


def face_lower(model, face_file, eye):
    """[face_file]: the face texture's file id; [eye]: the eye colour (its glow is painted into
    the face when it has one), else None."""
    if eye is not None and eye.get("overlay"):
        return "%s\\%sFaceLower%d_%02d.blp" % (model["folder"], model["name"], face_file, eye["index"])
    return "%s\\%sFaceLower%d.blp" % (model["folder"], model["name"], face_file)


def face_upper(model, eye):
    return "%s\\%sFaceUpper%02d.blp" % (model["folder"], model["name"], eye["index"])


def face_file(model, face, skin_entry):
    """The face texture (file id) a face takes on a skin: the face's for the skin's base skin."""
    textures = face["textures"]
    return textures.get(str(skin_entry["base"])) or textures.get(skin_entry["base"]) or 0


def face_variation(model, face_index, eye_index):
    """3.3.5's face number for a face and an eye colour (face 1 eye 1, face 1 eye 2...)."""
    return face_index * len(model["eyes"]) + eye_index
