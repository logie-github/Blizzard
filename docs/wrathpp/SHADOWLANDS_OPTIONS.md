# Shadowlands' character options for Wrath++

Wrath++ carries Shadowlands' character customization (its last build, 9.2.7.45745) for the ten races
3.3.5 has, each option a category of its own in the game's order, with the game's choices and names.
This page is what that is, read from the game's own tables (`ChrCustomizationOption`, `Choice`,
`Element`, `Geoset`, `Material`, `SkinnedModel`, `Req`, `ChrModel`, `ChrRaceXChrModel`: wago.tools'
CSVs) by `realm/warcraft/wrathpp/tools/sl_inventory.py`:

    python3 tools/sl_inventory.py fetch CSV_DIR
    python3 tools/sl_inventory.py build CSV_DIR inventory.json
    python3 tools/sl_inventory.py markdown inventory.json      (the tables below)

Totals: 20 race/sex models, 277 options, 3529 choices.

## What draws a choice

- **geoset**: pieces of the model shown or hidden (hair styles, beards, earrings, tusks, horns of
  the Tauren and Draenei, tails). 3.3.5 draws geosets the same way (group × 100 + variant), so these
  need the Shadowlands model and the client told which variant of each group to show.
- **material**: a texture painted into a region of the character's skin (skin colours, faces,
  eye colours, tattoos, scars, war paint colours, makeup). 3.3.5 composes the skin from its own
  layers (skin, face lower and upper, facial hair, scalp, underwear); a Shadowlands material that
  is none of those is one more layer composed into the same texture.
- **model**: a model of its own drawn on the character (the night elves' and blood elves' horns
  and blindfolds).
- An option with nothing (War Paint, Tattoo, Markings, Face/Body Paint) chooses the pattern whose
  colour option paints it (its material rows hang on the colour's choices, `RelatedChrCustomizationChoiceID`).
- Druid forms (Bear, Cat, Travel, Aquatic, Flight, Moonkin) change shapeshift models; 3.3.5's forms
  are fixed models. They are listed and left for later.

## Who may pick a choice

The game's restrictions are kept for 3.3.5's classes: death knights' own skins and eyes (and the other
classes' eyes, not theirs), the druids' forms. Choices for a demon hunter alone (horns, blindfolds,
tattoos): Wrath++ has no demon hunter class, and the looks are offered to every class (as the
registry's seed decided). "unlock N" is `ChrCustomizationReq.ReqType` N other than 3: choices the game
opens by achievements, quests or events (pride hair colours, heritage looks); what each type means is
not read here, and Wrath++ has none of those unlocks: offered to all until decided otherwise.

## The way there

1. **Models.** Shadowlands' models of the ten races (ChrModel → CreatureDisplayInfo →
   CreatureModelData's file, fetched from wago.tools by file id) made 3.3.5 models by the converter the
   allied races already use (`realm/warcraft/modules/mod-allied-races/tools/m2.py`), keeping every
   customization geoset group (there, only the chosen variant of a group 3.3.5 doesn't know stays),
   into the Wrath++ client's own patch (never the shared game's archives).
2. **3.3.5's five sliders** carry Shadowlands' Skin Color, Face, Hair Style, Hair Color and the race's
   first facial option, with Shadowlands' choices: CharSections, CharHairGeosets and
   CharacterFacialHairStyles rows written from these tables (as `races.py` does for the allied
   races), in the Wrath++ client's patch and its server's own data folder (`data-modules-wrathpp`),
   so the server checks a new character against the same counts.
3. **Every other option a Wrath++ category**: geosets drawn by the native mod's hook of the
   client's geoset choice (`0x004ED900`), materials as layers composed into the skin texture, models
   attached. The creator shows them as it shows the five now.
4. **Registry.** 3529 choices are about 48 KB of registry, past the 10,000 bytes one Wrath++ message
   may carry: protocol 2 sends the registry in parts (the hash over the whole), and the choices'
   names go with the client's add-on.

## The options, a race and sex

### Human male (ChrModel 1)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 36 | material |  | face |
| 2 | Skin Color | 24 | material | 3 DeathKnight, 4 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 26 | geoset, material |  | hair style |
| 4 | Hair Color | 43 | material | 1 unlock 4 | hair colour |
| 5 | Mustache | 7 | geoset |  |  |
| 6 | Beard | 8 | geoset |  |  |
| 7 | Sideburns | 3 | geoset |  |  |
| 8 | Face Shape | 3 | geoset |  |  |
| 9 | Eyebrows | 12 | geoset, material |  |  |
| 10 | Eye Color | 28 | geoset, material | 1 DeathKnight, 24 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 2 unlock 2, 1 unlock 4 |  |

### Human female (ChrModel 2)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 45 | material |  | face |
| 2 | Skin Color | 23 | material | 3 DeathKnight, 3 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 34 | geoset, material |  | hair style |
| 4 | Hair Color | 43 | material | 1 unlock 4 | hair colour |
| 5 | Eyebrows | 26 | material |  |  |
| 6 | Face Shape | 3 | geoset |  |  |
| 7 | Eye Color | 29 | geoset, material | 1 DeathKnight, 24 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 3 unlock 2, 1 unlock 4 |  |
| 8 | Makeup | 7 | material |  |  |
| 9 | Piercings | 15 | geoset, material |  |  |
| 10 | Necklace | 9 | geoset, material |  |  |

### Orc male (ChrModel 3)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 18 | material | 9 DeathKnight, 9 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 34 | material | 3 DeathKnight, 18 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 18 | geoset, material |  | hair style |
| 4 | Hair Color | 15 | material | 1 unlock 4 | hair colour |
| 5 | Beard | 14 | geoset, material |  |  |
| 6 | Sideburns | 9 | geoset |  |  |
| 7 | Eye Color | 22 | geoset, material | 1 DeathKnight, 19 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |
| 8 | Scars | 4 | material |  |  |
| 9 | Grime | 3 | material |  |  |
| 10 | Earrings | 6 | geoset |  |  |
| 11 | Nose Ring | 4 | geoset |  |  |
| 12 | Tusks | 4 | geoset |  |  |
| 13 | Tattoo | 4 | material |  |  |
| 14 | War Paint | 4 | form (druid) |  |  |
| 15 | War Paint Color | 4 | material |  |  |
| 16 | Upright | 2 | form (druid) |  |  |

### Orc female (ChrModel 4)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 18 | material | 9 DeathKnight, 9 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 35 | material | 3 DeathKnight, 19 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 20 | geoset, material |  | hair style |
| 4 | Hair Color | 15 | material | 1 unlock 4 | hair colour |
| 5 | Eye Color | 22 | geoset, material | 1 DeathKnight, 19 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |
| 6 | Scars | 5 | material |  |  |
| 7 | Earrings | 14 | geoset |  |  |
| 8 | Nose Ring | 3 | geoset |  |  |
| 9 | Necklace | 3 | geoset |  |  |
| 10 | Tattoo | 4 | material |  |  |
| 11 | War Paint | 4 | form (druid) |  |  |
| 12 | War Paint Color | 4 | material |  |  |

### Dwarf male (ChrModel 5)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 20 | material | 10 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 30 | material | 3 DeathKnight, 14 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 22 | geoset, material |  | hair style |
| 4 | Hair Color | 21 | material | 1 unlock 4 | hair colour |
| 5 | Mustache | 10 | geoset |  |  |
| 6 | Beard | 11 | geoset |  |  |
| 7 | Eye Color | 29 | geoset, material | 1 DeathKnight, 19 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 8 unlock 2, 1 unlock 4 |  |
| 8 | Earrings | 8 | geoset, material |  |  |
| 9 | Nose Ring | 6 | geoset, material |  |  |
| 10 | Eyebrows | 1 | geoset |  |  |
| 11 | Tattoo | 8 | form (druid) |  |  |
| 12 | Tattoo Color | 4 | material |  |  |

### Dwarf female (ChrModel 6)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 20 | material | 10 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 22 | material | 3 DeathKnight, 6 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 26 | geoset, material |  | hair style |
| 4 | Hair Color | 21 | material | 1 unlock 4 | hair colour |
| 5 | Eye Color | 29 | geoset, material | 1 DeathKnight, 19 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 8 unlock 2, 1 unlock 4 |  |
| 6 | Earrings | 8 | geoset, material |  |  |
| 7 | Piercings | 6 | geoset, material |  |  |
| 8 | Tattoo | 8 | form (druid) |  |  |
| 9 | Tattoo Color | 4 | material |  |  |

### NightElf male (ChrModel 7)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 24 | material | 12 DeathKnight, 12 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 27 | material | 3 DeathKnight, 1 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 6 none of 3.3.5's, 3 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 17 | geoset, material |  | hair style |
| 4 | Hair Color | 19 | material | 1 unlock 2, 1 unlock 4 | hair colour |
| 5 | Sideburns | 5 | geoset |  |  |
| 6 | Mustache | 5 | geoset |  |  |
| 7 | Beard | 8 | geoset |  |  |
| 8 | Horns | 7 | model | 6 none of 3.3.5's |  |
| 9 | Blindfold | 12 | model | 10 none of 3.3.5's |  |
| 10 | Eyebrows | 9 | geoset |  |  |
| 11 | Ears | 5 | geoset |  |  |
| 12 | Scars | 6 | material |  |  |
| 13 | Eye Color | 17 | geoset, material | 2 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 none of 3.3.5's, 2 unlock 2, 1 unlock 4 |  |
| 14 | Vines | 2 | geoset |  |  |
| 15 | Vine Color | 5 | material |  |  |
| 16 | Tattoo | 12 | material | 6 none of 3.3.5's |  |
| 17 | Tattoo Color | 7 | material | 6 none of 3.3.5's |  |
| 18 | Bear Form | 31 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 30 Druid |  |
| 19 | Cat Form | 33 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 29 Druid, 3 unlock 1 |  |
| 20 | Aquatic Form | 5 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 3 unlock 1 |  |
| 21 | Travel Form | 6 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 4 unlock 1 |  |
| 22 | Flight Form | 11 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 9 unlock 1 |  |
| 23 | Moonkin Form | 2 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid |  |

### NightElf female (ChrModel 8)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 18 | material | 9 DeathKnight, 9 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 27 | material | 3 DeathKnight, 1 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 6 none of 3.3.5's, 3 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 20 | geoset, material |  | hair style |
| 4 | Hair Color | 18 | material | 1 unlock 4 | hair colour |
| 5 | Vines | 2 | geoset |  |  |
| 6 | Vine Color | 5 | material |  |  |
| 7 | Eyebrows | 4 | geoset |  |  |
| 8 | Ears | 5 | geoset |  |  |
| 9 | Blindfold | 12 | model | 11 none of 3.3.5's |  |
| 10 | Scars | 6 | material |  |  |
| 11 | Eye Color | 16 | geoset, material | 1 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 none of 3.3.5's, 2 unlock 2, 1 unlock 4 |  |
| 12 | Markings | 10 | form (druid) |  |  |
| 13 | Markings Color | 10 | material | 2 DeathKnight |  |
| 14 | Headdress | 3 | geoset |  |  |
| 15 | Earrings | 4 | geoset |  |  |
| 16 | Nose Ring | 4 | geoset |  |  |
| 17 | Necklace | 4 | geoset |  |  |
| 18 | Horns | 7 | model | 6 none of 3.3.5's |  |
| 19 | Tattoo | 7 | form (druid) | 6 none of 3.3.5's |  |
| 20 | Tattoo Color | 7 | material | 6 none of 3.3.5's |  |
| 21 | Bear Form | 31 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 30 Druid |  |
| 22 | Cat Form | 33 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 29 Druid, 3 unlock 1 |  |
| 23 | Aquatic Form | 5 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 3 unlock 1 |  |
| 24 | Travel Form | 6 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 4 unlock 1 |  |
| 25 | Flight Form | 11 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 9 unlock 1 |  |
| 26 | Moonkin Form | 2 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid |  |

### Scourge male (ChrModel 9)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 11 | material |  | face |
| 2 | Skin Type | 3 | geoset |  |  |
| 3 | Skin Color | 34 | material | 1 unlock 4 | skin |
| 4 | Hair Style | 21 | geoset, material |  | hair style |
| 5 | Hair Color | 18 | material | 1 unlock 4 | hair colour |
| 6 | Jaw Features | 11 | geoset, material |  |  |
| 7 | Face Features | 5 | geoset, material |  |  |
| 8 | Eye Color | 10 | geoset, material | 1 DeathKnight, 8 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 4 |  |

### Scourge female (ChrModel 10)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 10 | material |  | face |
| 2 | Skin Type | 3 | geoset |  |  |
| 3 | Skin Color | 34 | material | 1 unlock 4 | skin |
| 4 | Hair Style | 19 | geoset, material |  | hair style |
| 5 | Hair Color | 18 | material | 1 unlock 4 | hair colour |
| 6 | Face Features | 4 | geoset, material |  |  |
| 7 | Jaw Features | 5 | geoset, material |  |  |
| 8 | Eye Color | 10 | geoset, material | 1 DeathKnight, 8 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 4 |  |

### Tauren male (ChrModel 11)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 10 | material | 5 DeathKnight, 5 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 32 | material | 3 DeathKnight, 6 unlock 2, 1 unlock 4 | skin |
| 3 | Horn Style | 20 | geoset | 3 unlock 2 |  |
| 4 | Horn Color | 7 | material | 4 unlock 2 |  |
| 5 | Foremane | 4 | geoset |  |  |
| 6 | Hair | 11 | geoset |  |  |
| 7 | Facial Hair | 13 | geoset |  |  |
| 8 | Eye Color | 9 | geoset, material | 1 DeathKnight, 7 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 4 |  |
| 9 | Face Paint | 4 | form (druid) |  |  |
| 10 | Headdress | 3 | geoset |  |  |
| 11 | Nose Ring | 5 | geoset |  |  |
| 12 | Necklace | 3 | geoset |  |  |
| 13 | Jewelry Color | 1 | material |  |  |
| 14 | Flower | 2 | geoset |  |  |
| 15 | Body Paint | 4 | form (druid) |  |  |
| 16 | Paint Color | 6 | material |  |  |
| 17 | Bear Form | 31 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 30 Druid |  |
| 18 | Cat Form | 33 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 29 Druid, 3 unlock 1 |  |
| 19 | Moonkin Form | 2 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid |  |
| 20 | Aquatic Form | 5 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 3 unlock 1 |  |
| 21 | Travel Form | 6 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 4 unlock 1 |  |
| 22 | Flight Form | 11 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 9 unlock 1 |  |

### Tauren female (ChrModel 12)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 8 | material | 4 DeathKnight, 4 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 24 | material | 3 DeathKnight, 6 unlock 2, 1 unlock 4 | skin |
| 3 | Horn Style | 23 | geoset | 3 unlock 2 |  |
| 4 | Horn Color | 8 | material | 5 unlock 2 |  |
| 5 | Foremane | 3 | geoset |  |  |
| 6 | Hair | 15 | geoset |  |  |
| 7 | Eye Color | 9 | geoset, material | 1 DeathKnight, 7 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 4 |  |
| 8 | Face Paint | 4 | form (druid) |  |  |
| 9 | Headdress | 3 | geoset |  |  |
| 10 | Earrings | 5 | geoset |  |  |
| 11 | Nose Ring | 4 | geoset |  |  |
| 12 | Necklace | 4 | geoset |  |  |
| 13 | Jewelry Color | 1 | material |  |  |
| 14 | Flower | 2 | geoset |  |  |
| 15 | Body Paint | 4 | form (druid) |  |  |
| 16 | Paint Color | 6 | material |  |  |
| 17 | Bear Form | 31 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 30 Druid |  |
| 18 | Cat Form | 33 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 29 Druid, 3 unlock 1 |  |
| 19 | Moonkin Form | 2 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid |  |
| 20 | Aquatic Form | 5 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 3 unlock 1 |  |
| 21 | Travel Form | 6 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 4 unlock 1 |  |
| 22 | Flight Form | 11 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 9 unlock 1 |  |

### Gnome male (ChrModel 13)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 14 | material | 7 DeathKnight, 7 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 14 | material | 3 DeathKnight, 2 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 18 | geoset, material |  | hair style |
| 4 | Hair Color | 19 | material | 1 unlock 4 | hair colour |
| 5 | Mustache | 11 | geoset |  |  |
| 6 | Beard | 9 | geoset |  |  |
| 7 | Eyebrows | 9 | geoset |  |  |
| 8 | Eye Color | 16 | geoset, material | 1 DeathKnight, 13 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |

### Gnome female (ChrModel 14)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 14 | material | 7 DeathKnight, 7 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 14 | material | 3 DeathKnight, 2 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 20 | geoset, material |  | hair style |
| 4 | Hair Color | 19 | material | 1 unlock 4 | hair colour |
| 5 | Eye Color | 16 | geoset, material | 1 DeathKnight, 13 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |
| 6 | Earrings | 15 | geoset |  |  |
| 7 | Earring Color | 16 | material |  |  |

### Troll male (ChrModel 15)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 10 | material | 5 DeathKnight, 5 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 22 | material | 3 DeathKnight, 9 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 18 | geoset, material |  | hair style |
| 4 | Hair Color | 17 | material | 1 unlock 4 | hair colour |
| 5 | Tusks | 10 | geoset |  |  |
| 6 | Eye Color | 18 | geoset, material | 1 DeathKnight, 15 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |
| 7 | Face Paint | 10 | form (druid) |  |  |
| 8 | Face Paint Color | 21 | material | 3 DeathKnight, 1 unlock 4 |  |
| 9 | Earrings | 6 | geoset |  |  |
| 10 | Piercing | 3 | geoset |  |  |
| 11 | Body Paint | 4 | form (druid) |  |  |
| 12 | Body Paint Color | 7 | material |  |  |
| 13 | Bear Form | 31 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 30 Druid |  |
| 14 | Cat Form | 33 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 29 Druid, 3 unlock 1 |  |
| 15 | Moonkin Form | 2 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid |  |
| 16 | Aquatic Form | 5 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 3 unlock 1 |  |
| 17 | Travel Form | 6 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 4 unlock 1 |  |
| 18 | Flight Form | 11 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 9 unlock 1 |  |

### Troll female (ChrModel 16)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 12 | material | 6 DeathKnight, 6 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 22 | material | 3 DeathKnight, 9 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 17 | geoset, material |  | hair style |
| 4 | Hair Color | 17 | material | 1 unlock 4 | hair colour |
| 5 | Tusks | 6 | geoset |  |  |
| 6 | Eye Color | 18 | geoset, material | 1 DeathKnight, 15 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |
| 7 | Face Paint | 4 | form (druid) |  |  |
| 8 | Face Paint Color | 7 | material |  |  |
| 9 | Earrings | 8 | geoset |  |  |
| 10 | Piercing | 3 | geoset |  |  |
| 11 | Body Paint | 4 | form (druid) |  |  |
| 12 | Body Paint Color | 7 | material |  |  |
| 13 | Bear Form | 31 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 30 Druid |  |
| 14 | Cat Form | 33 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 29 Druid, 3 unlock 1 |  |
| 15 | Moonkin Form | 2 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid |  |
| 16 | Aquatic Form | 5 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 3 unlock 1 |  |
| 17 | Travel Form | 6 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 4 unlock 1 |  |
| 18 | Flight Form | 11 | form (druid) | 1 DeathKnight+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 Druid, 9 unlock 1 |  |

### BloodElf male (ChrModel 19)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 20 | material | 10 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 31 | material | 3 DeathKnight, 1 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 6 none of 3.3.5's, 6 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 21 | geoset, material |  | hair style |
| 4 | Hair Color | 17 | material | 1 unlock 4 | hair colour |
| 5 | Facial Hair | 13 | geoset |  |  |
| 6 | Ears | 3 | geoset |  |  |
| 7 | Horns | 7 | model | 6 none of 3.3.5's |  |
| 8 | Blindfold | 12 | model | 11 none of 3.3.5's |  |
| 9 | Tattoo | 7 | form (druid) | 6 none of 3.3.5's |  |
| 10 | Tattoo Color | 7 | material | 6 none of 3.3.5's |  |
| 11 | Eye Color | 21 | geoset, material | 1 DeathKnight, 17 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 none of 3.3.5's, 1 unlock 2, 1 unlock 4 |  |

### BloodElf female (ChrModel 20)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 20 | material | 10 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 30 | material | 3 DeathKnight, 1 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 6 none of 3.3.5's, 5 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 25 | geoset, material |  | hair style |
| 4 | Hair Color | 17 | material | 1 unlock 4 | hair colour |
| 5 | Horns | 7 | model | 6 none of 3.3.5's |  |
| 6 | Eye Color | 21 | geoset, material | 1 DeathKnight, 17 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 none of 3.3.5's, 1 unlock 2, 1 unlock 4 |  |
| 7 | Blindfold | 12 | model | 11 none of 3.3.5's |  |
| 8 | Ears | 3 | geoset |  |  |
| 9 | Earrings | 14 | geoset |  |  |
| 10 | Necklace | 4 | geoset |  |  |
| 11 | Tattoo | 7 | form (druid) | 6 none of 3.3.5's |  |
| 12 | Tattoo Color | 7 | material | 6 none of 3.3.5's |  |
| 13 | Armbands | 4 | geoset |  |  |
| 14 | Jewelry Color | 2 | material |  |  |
| 15 | Bracelets | 7 | material |  |  |

### Draenei male (ChrModel 21)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 20 | material | 10 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 24 | material | 3 DeathKnight, 3 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 23 | geoset |  | hair style |
| 4 | Hair Color | 15 | material | 1 unlock 2, 1 unlock 4 | hair colour |
| 5 | Facial Hair | 11 | geoset |  |  |
| 6 | Eye Color | 4 | geoset, material | 1 DeathKnight, 1 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |
| 7 | Circlet | 2 | geoset |  |  |
| 8 | Horn Decoration | 3 | geoset |  |  |
| 9 | Tendrils | 8 | geoset |  |  |
| 10 | Jewelry Color | 31 | material | 1 unlock 4 |  |
| 11 | Tail | 2 | geoset |  |  |

### Draenei female (ChrModel 22)

| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |
|---|---|---|---|---|---|
| 1 | Face | 20 | material | 10 DeathKnight, 10 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior | face |
| 2 | Skin Color | 22 | material | 3 DeathKnight, 3 unlock 2, 1 unlock 4 | skin |
| 3 | Hair Style | 24 | geoset |  | hair style |
| 4 | Hair Color | 14 | material | 1 unlock 4 | hair colour |
| 5 | Horns | 12 | geoset | 1 unlock 2 |  |
| 6 | Eye Color | 4 | geoset, material | 1 DeathKnight, 1 Druid+Hunter+Mage+Paladin+Priest+Rogue+Shaman+Warlock+Warrior, 1 unlock 2, 1 unlock 4 |  |
| 7 | Circlet | 2 | geoset |  |  |
| 8 | Hair Decoration | 3 | geoset |  |  |
| 9 | Tendrils | 2 | geoset |  |  |
| 10 | Jewelry Color | 16 | material | 1 unlock 4 |  |
| 11 | Tail | 6 | geoset |  |  |

