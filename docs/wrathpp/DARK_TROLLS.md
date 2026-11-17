# Wrath++: the Dark Trolls

Wanted (the user, 2026-11-17, after warcraft.wiki.gg/wiki/Dark_troll): an Alliance race of dark trolls starting in Shadowglen with the
Night Elves' intro camera; lore-accurate skin, eye and hair colours (all of the Troll's skins plus the night elves' colours, no warts;
the Night Elves' hair colours as a recolour of the current hair); the Night Elves' racials with their text rewritten; Alliance, and able to
do the Alliance's quests as trolls ("basically fully trolls coded"); lore-accurate classes including druid and shaman; the narrator's voice
for a custom intro; every regular sound covered.

Status 2026-11-17: **built and published (looks `8a44af8`, server and app `4891e3e`); the CI rig passes (0 problems) and the phone's own start report shows the creator opening Customize for the Dark Troll, man and woman, without a crash; nothing else of it has been seen in the game.**

## Stage 1 (done in the files)

| Part | How |
|---|---|
| Race | id **21** (free since the Kul Tiran went), file string `DarkTroll`, Alliance, `tools/races_profile.py` (`DARKTROLL`) |
| Look | the Troll's models, skins, faces, hair and features as they are (`sl_looks.py dark_troll`: an entry with `alias_of` "8", the Troll's own files) |
| Sounds | the Troll's: its CreatureModelData row (`MODEL_FROM`/`STATS_FROM` Troll: scale, collision, sound entries) and its UI voices and emotes copied as rows of the new race (`VOICE_COPY`; no files) |
| Start | the Night Elves' (Shadowglen: quests, gear, standing, intro camera, `START`) |
| Classes | Warrior, Hunter, Rogue, Priest, Mage, Death Knight, Shaman (the wiki's shamans), Druid (the user's word, by the Night Elves' kin) |
| Racials | Shadowmeld itself (58984: the core scripts it by that id, its words name no race), and three spells of their own with their own names and words: Nightstalker's Grace (the Night Elves' Quickness), Ward of the Wild Gods (Nature Resistance), Shadowtooth Hush (Elusiveness). Wisp Spirit is left out (the core makes a night elf's wisp by race) |
| Creator | the race button (`WrathppAlliedRaces`: Alliance, the Night Elves' scene, its texts), the Troll's art (`RACE_ART`) |

## Stage 2 (in the files, not run)

- **Own files, tinted colours** (`tools/dark_troll.py`, `sl_looks.dark_troll_entry`): the Dark Troll is built as a race of its own under `Character\DarkTroll\...` (its model
  and textures are the Troll's by content), so its colours can differ. Added to the Troll's 22 skins: the Night Elf's skin colours and four of the dark trolls' own (Ash
  Grey, Slate, Charcoal, Royal Purple: the wiki's grey to black and the RPG book's purple), each a tint of the Troll skin nearest in colour (a per-channel factor to the
  wanted mean colour, the detail kept), the same factor on the body, underwear, extra, every face and every scalp of that skin. The Night Elf's hair colours likewise on
  the Troll's hair. The data names such a texture by a made-up file id (2000000000 and up) with its spec; the package step's reader makes it when asked
  (`dark_troll.Resolver`): no pixel is read when the data is made.
- **The creator** lists the new colours with their swatches (`sl_creator`: the model's `extra_choices`).
- **Warts**: no option or choice in Shadowlands' Troll tables is named for warts (the options are Face, Skin Color, Hair Style and Color, Tusks, Eye Color, Face and Body
  Paint with colours, Earrings, Piercing); if warts are drawn in a face texture they are the Troll's own and can't be told apart by the tables.

## Still to do

1. **Eyes**: the Troll's 18 eye colours include yellows (the wiki's pale yellow). The night elves' eye colours are NOT added: 3.3.5 holds 255 face numbers a race and sex, a face number being a face and an eye colour (10 faces x 18 eyes = 180 now; the Night Elf's 17 more would make 350).
2. **Intro**: the Night Elves' camera is the start race's, retimed to the narration's length (the allied races' way); the narration is `realm/warcraft/wrathpp/data/darktroll_intro.mp3` (49 s, an AI voice made like the Zandalari intro's from the user's recording, with the user's words on the pronunciations: High-jall, Ee-loon; the script is in `DARK_TROLLS.md`'s history): in the package as `Sound\CinematicVoices\DarkTrollNarration.mp3`.
3. **Quests as trolls**: the generator ORs the new race into the Night Elves' quest, item and spell masks; troll-only gates (none known) are not touched.
4. **The first run**: CI's looks run is the first to make these files; the Dark Troll's counts (skins, colours) are checked by `sl_creator`'s own consistency errors and the rig.
