# Wrath++: the Dark Trolls

Wanted (the user, 2026-11-17, after warcraft.wiki.gg/wiki/Dark_troll): an Alliance race of dark trolls starting in Shadowglen with the
Night Elves' intro camera; lore-accurate skin, eye and hair colours (all of the Troll's skins plus the night elves' colours, no warts;
the Night Elves' hair colours as a recolour of the current hair); the Night Elves' racials with their text rewritten; Alliance, and able to
do the Alliance's quests as trolls ("basically fully trolls coded"); lore-accurate classes including druid and shaman; the narrator's voice
for a custom intro; every regular sound covered.

Status 2026-11-17: **stage 1 is in the generator and the creator's glue; nothing has run in the game or on a phone.**

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

## Not done yet

1. **Skins and eyes**: the night elves' colours as extra skins of the Troll's body (the Troll's skin textures tinted to each night elf skin's colour,
   faces, underwear and scalps with them), and the dark trolls' own greys and violets (the wiki: grey to black skin; the RPG book's royal purple,
   pale yellow eyes). Needs the Troll's converted textures and the night elves' measured colours (`textures.py`).
2. **Hair**: the night elves' hair colours as a recolour of the Troll's hair textures.
3. **No warts**: the Troll's feature choices without the warty ones (Shadowlands' own table names them; read at the next packaging).
4. **Customize**: the creator's options for the new race are the Troll's (alias); the parts session's `sl_creator.py` keys them by the ten races.
5. **Intro**: the Night Elves' camera is the start race's; the narration is a draft (an AI clone of the Zandalari intro's voice, not in the repository).
6. **Quests as trolls**: the quest, item and spell race masks the Night Elves have get the new race's bit (the generator's start-race rule); troll-only
   gates (none known) are not touched.
