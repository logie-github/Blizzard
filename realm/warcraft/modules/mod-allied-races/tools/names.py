"""The game's paths of the races' textures, as tools/textures.py writes them and the tables
(tools/build_data.py) name them. A face's FaceLower is named by the face texture it's cut from
and the eye glow painted into it (nightborne), its FaceUpper by the eye colour: a face number
on a skin draws on the same files as every other that takes the same pictures."""


def race_folder(model):
    return model["folder"].rsplit("\\", 1)[0]


def skin(model, colour):
    return "%s\\%sSkin00_%02d.blp" % (model["folder"], model["name"], colour)


def pelvis(model, colour):
    return "%s\\%sNakedPelvisSkin00_%02d.blp" % (model["folder"], model["name"], colour)


def torso(model, colour):
    return "%s\\%sNakedTorsoSkin00_%02d.blp" % (model["folder"], model["name"], colour)


def hair(model, colour):
    return "%s\\%sHair00_%02d.blp" % (race_folder(model), model["name"], colour)


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
