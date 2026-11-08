# mod-allied-races: the void elves, the nightborne, the Lightforged Draenei and the Zandalari Trolls

Blizzard's allied races of today, playable in the app's 3.3.5 ChromieCraft realm (not on Wrath
Remix's, the user's call: "Only chromie needs new races"; Turtle WoW is another game and untouched),
in their own models, looks and voices:

| Race | Id | Side | Starts | Classes |
| --- | --- | --- | --- | --- |
| Void Elf | 15 | Alliance | Ammen Vale (the Draenei's start, quests and standing: the Exodar) | Warrior, Hunter, Rogue, Priest, Death Knight, Mage, Warlock |
| Nightborne | 16 | Horde | Deathknell (the Forsaken's start, quests and standing: Undercity) | Warrior, Hunter, Rogue, Priest, Death Knight, Mage, Warlock |
| Lightforged Draenei | 17 | Alliance | Ammen Vale (the Draenei's start, quests and standing: the Exodar) | Warrior, Paladin, Hunter, Priest, Death Knight, Mage |
| Zandalari Troll | 18 | Horde | Camp Narache in Mulgore (the Tauren's start, quests and standing: Thunder Bluff) | Warrior, Paladin, Hunter, Rogue, Priest, Death Knight, Shaman, Mage, Druid |

**The old races' new classes** too, on this realm: undead paladins (the user: "let undead be
paladins") and WoW: Forever's new pairs (the user: "Add these race class combos"): human hunters,
dwarf shamans, gnome priests, orc mages and troll warlocks (`EXTRA_CLASSES` in `tools/build_data.py`).
Each starts where its race's warriors do, with the gear, action bar (without that race's racials),
class skills and abilities of a race that has the class: the Blood Elves' paladins, the dwarves'
hunters (their Guns), the Draenei's shamans, the humans' priests, the trolls' mages, the orcs'
warlocks; that race's class quests (one class's alone: a hunter's taming, a shaman's totems) are
theirs too. They train at their class's own trainers, and at another class's (the user: "For human
hunters make them use the warrior trainer..."):

| Pair | Also trains at |
| --- | --- |
| Undead paladin | the priest trainers |
| Human hunter | the warrior trainers |
| Dwarf shaman | the priest trainers |
| Gnome priest | the mage trainers |
| Orc mage | the warlock trainers |
| Troll warlock | the mage trainers |

There the core gives them their own class's trainer whose spells suit them most
(`warcraft/patches/azerothcore/0011`: the gossip's trainer option, the list, buying a spell,
unlearning talents, seeing the trainer), and `data/sql/chromiecraft/world/allied_races_class_trainers.sql`
gives them that trainer's greeting and options (training, talents, dual specialization) as to its own
class (a second way through the class conditions, a way each pair), and its "I can't train you" not.

**WoW: Forever's racials** for the eight races of 1.x, on this realm (the user: "Add the new or updated
racials to each race"), as forever.warcraftdb.com has them (Forever 1.60.1); Blood Elves and Draenei,
which Forever hasn't, keep theirs:

| Race | Racials |
| --- | --- |
| Human | Will to Survive (removes Stuns, 3 min), Perception (stealth detection for 20 sec, 3 min), Ruthless (+2% crit), The Human Spirit (+5% Spirit) |
| Orc | Blood Fury (+10% Attack Power and Spell Power for 15 sec, 3 min), Hardiness (Stuns 20% shorter), Savage (+1% crit), Shatter Curse (removes Curses, 5% less Magical damage for 8 sec, 3 min) |
| Dwarf | Stoneform (removes and grants immunity to Bleeds, Poisons and Diseases, 10% less Physical damage for 8 sec, 3 min), Find Treasure, Earth Fury (+2% crit bonus to damage and healing), Big Game Hunter (+5% damage to Beasts) |
| Night Elf | Elune's Light (+10% crit for 15 sec, 3 min), Quickness (+1% dodge, +2% movement speed, stealth a level better for rogues and druids), Shadowmeld (10 sec cooldown, 2 min in combat), Wisp Spirit |
| Undead | Cannibalize, Touch of the Grave (20% chance for warriors, paladins, rogues and death knights, 30% for priests, mages and warlocks: a hit drains as much Health as it did, 5% of maximum Health at most), Underwater Breathing (300%), Will of the Forsaken |
| Tauren | War Stomp (1.5 min), Endurance (+5% Health, +2% crit bonus), Cultivation (harvests the herb within 10 yards without Herbalism, each herb once; 3 sec cast, 15 min), Plainsrunning (+1% speed every 5 sec moving, 30% at most; standing still or hits take it away; +3% mounted) |
| Gnome | Engineering Specialization, Escape Artist (and 3 sec immune to movement impairing effects, 2 min), Expansive Mind (+5% maximum Mana, Rage, Energy or Runic Power), Eureka! (10% cheaper, 10% stronger abilities for 8 sec, 2 min; a version each class) |
| Troll | Berserking (+10% attack and casting speed for 10 sec, 3 min), Regeneration (+20%, 20% in combat), Rapid Regeneration (50% of maximum Health over 6 sec, until you move, act or are hit; 3 min), Beast Slaying |

Gnome priests also have Forever's two priest racials: Confounding Flash (level 10: confuses up to 5
enemies within 8 yards for 3 sec, until hit; 2 min) and Contingency Plan (a rank at levels 20, 30,
40, 50 and 60: a ward on an ally for 30 sec that, when damage leaves them below 35% Health, shields
155 to 926 and heals 125 to 670 over 15 sec; 10 min), taught as those levels come (Forever teaches
them by quests from a priestess 3.3.5 hasn't).

How: `tools/build_data.py` writes Forever's spells (ids 98800 to 98842; Forever's own ids pass a
million, past 3.3.5's tables) and the changes to the racials 3.3.5 has, and gives each race's racial
skill line Forever's racials (its rows, and new ones from 23500); the old ones are no longer taught,
and a character loses them at its next login (the core teaches a skill's spells at each login without
keeping them). `src/AlliedRacesForever.cpp` scripts what a spell's row can't: Blood Fury's Spell
Power, Shadowmeld's cooldown in combat, Touch of the Grave's drain, Cultivation, Plainsrunning,
Contingency Plan and the gnome priest's spells. New characters' action bars have Will to Survive and
the one Blood Fury where 3.3.5's racials stood. Departures, where 3.3.5 can't do as Forever does:
Engineering Specialization has its text alone (3.3.5's devices fail by their own scripts' rolls);
Eureka!'s "non-periodic" is the class's direct damage and healing (3.3.5's spell modifiers), the
mage's periodic damage too, as Forever has; the death knights (which Forever hasn't) have Touch of the
Grave's 20% and, gnomes, Expansive Mind's Runic Power; Cultivation's harvest goes into the bags
rather than a second herb to pick, and a herb's skill needs a level of a fifth of it (80 at most).
Wrath Remix's realm keeps 3.3.5's racials: the patch is set aside there, and its world database has
none of this.

(The classes are today's that 3.3.5 has: no monks, demon hunters or evokers.) Races 15 to 18 were
the game's Skeleton, Vrykul, Tuskarr and Forest Troll, which only creatures use; in the game's
tables they move to 24 to 27, as the Skyborne moved 13 and 14 to 22 and 23: the client's own rows of
theirs, whatever their ids (an HD look's too), their race, looks, hair shapes, facial hair styles and
voice rows with them (until allied-races-9 the rows were put by the server's tables' ids, and their
facial hair styles and the Skeleton's voice row stayed at 15 to 18 beside the new races').

## What they have

- **Models**: Blizzard's own player models of today (`character/voidelf/...`,
  `character/nightborne/...`: the models, their skeletons with the parent skeletons, their
  animations), made models the 3.3.5 game draws by `tools/m2.py` (below). Not the blood elf's or
  the night elf's body.
- **Their size: their kin's** (the user: "Trolls to trolls. Draenei to draenei. Elves to elves."):
  each model measured as the game poses it (where its head's bone is in Stand, the feet at 0: ears,
  hair and how the body stoops don't move it) and made its kin's height all through by
  `tools/scale.py`, the heights the old races have in both HD looks the app offers (the same in
  each): void elves the blood elves' (1.868 men, 1.717 women), the nightborne the night elves'
  (2.212, 2.017), the Lightforged the Draenei's (2.251, 2.108), the Zandalari the trolls' (2.072,
  2.136). Today's void elves and Lightforged measure their kin's already and stay as they are; the
  nightborne are made 0.985 (men) and 1.009 (women), the Zandalari 0.817 and 0.874 (today's stand
  upright, their heads 0.3 to 0.5 yards above the stooped trolls').
- **Weapons on their backs as their kin wear them**: today's game turns a sheathed weapon by data
  3.3.5 hasn't, so on our models a staff or a two-hander on the back went through the body.
  `tools/sheaths.py` gives each back sheath point (the sheathed main and off hand, the shield, the
  large weapons) a bone of its own, turned to the orientation the kin's model has there in Stand
  (`data/sheaths.json`, measured on the Alternative HD Patch's models); the weapon moves with the
  body as before.
- **Looks**, from today's customization tables, on 3.3.5's five sliders:
  - *Skin colour*: every skin colour a player picks today (void elves 30, among them the high elf
    skins; nightborne 10, each with each of the seven body tattoos: 70; Lightforged Draenei 7 with
    each of the four tattoos: 28; Zandalari 6 with each of the four: 24).
  - *Face*: every face with every eye colour, cycling face 1 eye 1, face 1 eye 2... (void elves
    28 faces x 9 eye colours = 252; nightborne 12 x 6 = 72; Lightforged 10 x 2 = 20; Zandalari
    6 x 5 = 30). The void elves' nine eye colours are
    the ones a player picks without a demon hunter's blindfold (3.3.5 holds at most 255 faces). A
    face today has textures for the skins of its kind (the eight void faces for the void skins,
    the twenty high elf faces for the high elf skins): on a skin of the other kind, a face number
    shows that kind's face of the same rank, so every face draws on every skin.
  - *Hair style*: every style.
  - *Hair colour*: every colour a player picks today (void elves, nightborne and Zandalari 16,
    Lightforged 10).
  - *Feature*: void elf men their facial hair x void tentacles (8 x 7: today's Tentacles switch
    gives each hair style its own tentacle shape; here the shapes are variants named for the
    style they were made for, and any goes with any style), void elf women their earrings x
    tentacles (5 x 7); nightborne men every chin decoration x mustache x jaw jewellery (160),
    nightborne women every jaw jewellery x earrings x necklace (160); Lightforged men their
    facial hair x tendrils (12 x 7), Lightforged women their horns x tendrils (13 x 2: the horns'
    slider is the second row's "Horns"); Zandalari men their tusks x piercings (7 x 6), Zandalari
    women their tusks x earrings x piercings x necklace (7 x 2 x 4 x 2).
  - The Lightforged's forehead rune (today's Rune, whose first choice is None) is always on, as
    Righteous: the glowing glyph on the brow. Today's runes are drawn from two textures of one
    atlas, a scrolling band of light times the glyph; 3.3.5 draws one texture, and until
    allied-races-12 the card took the band's coordinates and showed as a solid white bar. The
    converter (`tools/m2.py`, `glyph_card`) gives such cards their glyph's coordinates instead, the
    runes in the men's hair too. The band's stage scrolls (a texture animation); the glyph's
    doesn't, and the card takes the glyph's (until allied-races-13 it kept the band's, and the
    atlas's glyphs slid across the brow).
  - The Lightforged men's forehead and crest (the bony plates over the brow, their "horns", drawn
    with the hair's texture as the Draenei men's are) are their model's geoset 1, which isn't a
    hair style; until allied-races-13 it was left out with the hair styles not chosen, and the men
    had no forehead. It's kept always now (`tools/races.py`, HEAD).
  - Left at their first choice (3.3.5 has no slider for them): ears, eyebrows, eye style and
    eyesight, face tattoos, face jewellery, headdresses, hair decorations, luminous hands. Faces
    differ by texture alone (today's faces also reshape the head with bone files, which 3.3.5
    hasn't).
- **Voices**: today's (VocalUISounds: the words at the UI's moments; EmotesTextSound: the
  emotes 3.3.5 has), as MP3s encoded the way the game's own are (44.1 kHz, constant bit rate, no
  tags or VBR header). The two moments 3.3.5 has twice that today's tables list once have the same
  words ("can't drink any more", 6, as 47; "invalid target", 66, as 11: so the game's own blood elves
  and Draenei have them). Their VocalUISounds rows are 9200 on, clear of the Skyborne's (9000 to
  9107): until allied-races-9 they began at 9100, and the Skyborne's patch, read after this one, put
  its rows over the void elves' first eight moments ("inventory full" among them).
- **Names**: today's name generator's.
- **Racials** (learned at creation from `playercreateinfo_spell_custom`), as today's where 3.3.5
  allows:
  - Void elves: **Spatial Rift** (tear a rift up to 15 yards ahead; use again within 6 sec to
    teleport through it; 3 min cooldown from when the rift is used or closes:
    `src/AlliedRacesSpells.cpp`), **Entropic Embrace** (abilities have a 10% chance, at most every
    30 sec, to empower you: +5% damage and healing for 12 sec; today's "as Shadowfrost" has no
    3.3.5 equivalent), **Chill of Night** (Shadow damage taken -1%), **Preternatural Calm** (no
    spell pushback), **Cantrips** (a mailbox for 10 min, 10 min cooldown: MOLL-E's). Ethereal
    Connection (transmogrification cost) has nothing to act on in 3.3.5 and isn't here.
  - Nightborne: **Arcane Pulse** (Arcane damage to enemies within 8 yards, scaling with level, and
    a 50% slow for 12 sec; 3 min cooldown), **Arcane Resistance** (Arcane damage taken -1%),
    **Magical Affinity** (magical damage +1%), **Ancient History** (Inscription +15).
  - Lightforged Draenei: **Light's Judgment** (a strike of Holy damage on the target, or the
    player, three seconds after the cast, to enemies within 5 yards; 3 min cooldown),
    **Forge of Light** (Blacksmithing +10), **Light's Reckoning** (on death, a burst of Holy
    damage to enemies and healing to allies within 8 yards), **Holy Resistance** (Holy damage
    taken -1%), **Demonbane** (+20% experience from demons). Light's Judgment's strike and Light's
    Reckoning's burst are the player's own casts (`src/AlliedRacesSpells.cpp`), so what they kill
    is the player's kill: loot, experience, quest credit (the first release with them cast them
    from unseen creatures, whose kills nobody got).
  - Zandalari Trolls: **Regeneratin'** (heals 17% of maximum health a second for 6 sec, ended
    by damage; 2.5 min cooldown), **Embrace of Pa'ku** (attacks and abilities have a 10% chance,
    at most every 30 sec, for +4% critical strike for 12 sec), **Pterrordax Swoop** (Slow Fall
    for 2 min, 15 min cooldown: today's is a glide, with no 3.3.5 equivalent), **City of Gold**
    (+2% money looted). Today's Zandalari also have Bwonsamdi's Reach (a free resurrection) and
    Pterrordax's flight; those aren't here.
- **Stats**: their kin's (the blood elves' for the void elves, the night elves' for the
  nightborne, the Draenei's for the Lightforged, the Trolls' for the Zandalari).
- **Starts**: the Draenei's, the Forsaken's and the Tauren's places for every class (death
  knights at Ebon Hold); the start race's starting gear and action bars (the Humans' for void elf
  rogues and warlocks, the Blood Elves' for nightborne hunters and Zandalari paladins, the Trolls'
  for Zandalari rogues, priests and mages, which the start race hasn't). A class the start race
  hasn't starts where the start race's warriors do. Their skills: their side's weapons and armour,
  and Common (void elves, Lightforged) or Orcish (nightborne, Zandalari). Releases up to 1.0.236
  gave them no language: they were also put in the other side's language row (a tiered one, for
  learning it), which the server may read first and then teach nothing. The skill rows are found
  by their stock races, so the Skyborne's module, whose SQL changes the same rows, finds them
  whichever goes first (this module's goes first: its folder's name comes first). A character made
  then learns what it lacks at its next login (the core teaches a character's missing start skills
  at every login).
- **Quests**: the start race's own quests in its first zones are **cloned** for the new race
  (`tools/quests.py`, `data/sql/chromiecraft/world/allied_races_quests.sql`): the same quests from the same
  people, with the quest-givers taking in who the player is (a void elf among the Exodar's
  survivors, a nightborne sent to learn the Forsaken's ways) before sending them down the same
  road; the originals stay the start race's alone. Void elves: the seventeen Draenei-only quests
  of Ammen Vale, Azuremyst and Bloodmyst (You Survived!, Replenishing the Healing Crystals, Rescue
  the Survivors!, Medicinal Purpose, An Alternative Alternative, The Prophecy of Velen, A Hearty
  Thanks!, the hippogryph and the prophecy chains); nightborne: Rude Awakening and the ride to the
  Undercity. The Lightforged take the same seventeen as the void elves, with their own words
  (an Army of the Light soldier washed up among the exiles). The Zandalari: The Hunt Begins on
  Red Cloud Mesa, the Cleansing chain, Journey to the Crossroads and the ride to Thunder Bluff
  (the Tauren's alone) with a troll of Zandalar's welcome from each giver. A quest that needs a
  cloned quest done first (the Draenei's class training; Mulgore's Hunt Continues, totems,
  Battleboars and class notes) is cloned too, chained to the clones, since the original is
  closed to the new race and would never unlock: `tools/quests.py` finds them. Every other
  quest, item and condition of the start race (and of the classes' template races) is open to
  the new race as it is. What the world does on an original quest's id is done on its clone's
  too (`tools/quests.py`'s bindings): the people's scripts on accepting or handing in a quest
  (the Ending Their World escort at Blood Watch, Legoso's run), the quest credit they give, and
  the conditions on their gossip and texts (an "is on the quest" or "has done it" for the
  original also holds for the clone, a "hasn't done it" for both). Rescue the Survivors!'s
  survivors stand up for Gift of the Naaru, a Draenei racial: a void elf or Lightforged holds it
  while their clone of the quest is in the log, and loses it when it's handed in or abandoned.
- **The intro**: the start race's flight over its home with each race's own narration (the user's
  MP3s, `data/client/voidelf_intro.mp3`, `nightborne_intro.mp3`, `lightforged_intro.mp3` and
  `zandalari_intro.mp3`), played through the cinematic's voice entry as the game's own
  narrations are, its sound naming that file alone (the nine other places empty and unweighted, as
  the Death Knights' narration has them; the other narrations' rows, which they were made from,
  weigh all ten). They're kept in the game's own narrations' format: MPEG-1 Layer III, 44.1 kHz,
  constant 160 kbit/s, no ID3 tags and no Xing/VBR header (the user's files were variable bit
  rate with ID3v2.4 tags, which 3.3.5's player may not start).
  The flight is as long as the narration and 1.5 seconds more (the user: "the intros video needs to
  be around the same length as the sound clip"): the game's flybys run 69 to 77 seconds and the
  narrations 37 to 54, so the scene went on in silence. As the world server makes the patch, each
  race's camera is the game's own flyby (FlybyDraenei, FlybyUndead, FlyByTauren) with every key
  moved to the same place in the narration's length (`RetimeCamera`, `src/AlliedRacesPatch.cpp`;
  the narration's length read from its MP3's frames), as its own file (`Cameras\FlybyVoidElf.m2`,
  `FlybyNightborne`, `FlybyLightforgedDraenei`, `FlybyZandalariTroll`): the same flight, faster
  (1.5 to 1.9 times; the Zandalari's 1.25). A flyby the game hasn't, or one that doesn't read as a
  3.3.5 camera, stays the stock one at its own length (the server's log says so).
- **Add-ons**: Questie's 3.3.5 port knows a race by its own table of the game's races
  (`QuestieCompat.ChrRaces`, by the race's file name) and stopped at login with "playerRaceId (a
  nil value)" (QuestiePlayer.lua) on a void elf. The patch adds `Interface/FrameXML/
  AlliedRacesAddons.lua` (in the game's FrameXML.toc, after its own files), which gives that table
  each race as its start race as the add-on loads: the Draenei for the void elves and the
  Lightforged, the Forsaken for the nightborne, the Tauren for the Zandalari, whose quests are
  theirs here. Entries Questie has itself are left as they are. (The Skyborne aren't in it: on
  Wrath Remix's realm this patch is out of the game.)
- **Character creation**: their portraits (Wowhead's race icons, `data/client/icons`) in the free
  columns of the race icons (the void elves' and nightborne's in the last, the Lightforged's and
  Zandalari's in the one before the Skyborne's); each side's races in two columns, two to a row
  from the top (`AlliedRacesCreate.lua`, which the Skyborne's screen code lays out again after,
  the same way); their kin's backgrounds: the Blood Elves' for the void elves, the Night Elves' for
  the nightborne, the Draenei's for the Lightforged, the Trolls' for the Zandalari, which in 3.3.5 is
  the Orcs' scene (the game has no troll scene of its own: until allied-races-11 the Zandalari were
  sent to one, and the screen went black with a missing model's cube in it and an error about
  PlayGlueAmbience) (each scene's
  camera is framed for its own race's height, and theirs is their kin's: the Draenei's, which the
  void elves had, showed them small; the Forsaken's cut off the nightborne's heads); on the character
  list, their kin's music (the list plays it again by the selected character's own race,
  `GlueAmbienceTracks`, which has no entry for them); their texts.

## ChromieCraft's alone

- **The SQL**: in `data/sql/chromiecraft/world`, which the servers don't read on their own; the app's
  `ctl.sh` (`realm_sql`) puts it in ChromieCraft's world database's update list, so it goes in there
  as the world server starts and never into Wrath Remix's. `data/sql/remix/world/allied_races_off_remix.sql`,
  on Remix's list, takes out what earlier releases put in Remix's world database: their starts (no
  character or bot of theirs is made there), stats, action bars and racials, and their race and look
  rows (races 15 to 18 the game's own creatures' again). A character of theirs made there before stays
  in its characters database, out of the character list (the core lists only the race and class pairs
  it has a start for).
- **The game's patch**: `AlliedRaces.Enable` (`mod_allied_races.conf`), which `ctl.sh` sets to 1 for
  ChromieCraft and 0 for Remix as each starts. Off, the module sets `patch-V.MPQ` aside
  (`patch-V.MPQ.aside`, out of the game) as the configuration is read, before the Skyborne's patch is
  made from the game's tables; on, it puts it back, and makes it again only if what it's made from
  changed. Its tables are made without Wrath Remix's patches (`patch-Y` and the language folder's
  `patch-<locale>-Y`), which are Remix's realm's alone.

## How it's made

- **`tools/races.py CSV_DIR`** reads Blizzard's tables of today (wago.tools' CSVs: ChrRaces,
  ChrModel, ChrCustomization*, TextureFileData, SoundKitEntry, VocalUISounds, EmotesTextSound,
  NameGen, and the four displays' CreatureDisplayInfo rows) and writes
  **`data/retail/races.json`** (committed): for each race and sex the model's files, the geoset
  policy, skins, faces, eyes, hair, features, voices and names, by file id. The other tools work
  from it alone.
- **`tools/build_data.py DBC_DIR WORLD_SQL_DIR`** reads the game's tables (the server's dbc
  folder) and the core's world SQL and writes `data/sql/chromiecraft/world/allied_races_world.sql` (the
  `*_dbc` tables the core reads over its DBC files, starts, skills, racials, standing, the quests
  opened) and `data/client/dbc/*.txt` (the rows to change in the game's tables, applied the
  Skyborne's way). Committed.
- **`tools/quests.py WORLD_SQL_DIR`** writes the cloned quests' SQL and
  `data/retail/cloned_quests.json`. Committed.
- **`tools/package.py fetch CACHE DIR`** (run by `scripts/package-azerothcore.sh` as the server is
  packaged; CI caches what it fetched by the list of files) fetches the game's files by id from
  wago.tools and writes DIR (`data/files` in the package: never in the repository), laid out as
  the game's patch, with `alliedraces.files` listing it:
  - **`tools/m2.py`**: today's model (format 274) made 3.3.5's (264): the child's bones with the
    parent skeleton's sequences (the child's own over them), every track with an entry a
    sequence, the sequence lookup a hash table as the game reads it, external animations kept
    in `.anim` files (one block, as 3.3.5's: today's keep the bones', the attachments' and the
    model's data in chunks of their own, the tracks pointing into theirs; earlier builds wrote only
    the model's few bytes, and the game read every such animation's bones past the end of the
    file). A few of today's skeletons list files laid out for another: a sequence's bone
    data is used only where its file is that skeleton's (every track's times rising within the
    sequence); the nightborne's parents list their older night elf models' files, whose own bones
    then give those sequences (bones matched by their names' hashes); where nothing fits (32 of the void
    elf women's, their emotes, sits and two dances among them; the Lightforged women's Cry, the
    Zandalari women's Shy), the sequence is drawn as the animation's first variation or Stand. A translation or scale that
    isn't real floats within 100 yards is left out. A global sequence's track (a loop of its own,
    not a sequence's) is read from the model whatever the sequences' files (it's never in a
    sequence's own file: earlier builds took it for one where the first sequence was kept outside),
    and merged from the track whose loop it is (earlier builds took the first merged sequence's
    entry, often the parent skeleton's: of the void elves', nightborne's and Lightforged's 329
    loops' tracks, 225 had another animation's times and 4 none); the body's texture coordinates stretched across (today's body texture is
    twice as wide as tall, the head in its right half; 3.3.5 composes a square), the head's into
    the face region, the eyes' (a texture of their own today) into the FaceUpper strip; the
    geosets 3.3.5's tables choose from kept whole (hair, features, armour); the body parts today's
    models keep in groups 3.3.5 doesn't know (the head, mouth, eyes and eyebrows, the toes, torso
    and forearms: groups 20 and up, which the game doesn't draw) folded into geoset 0, which it
    always draws, as the HD look's models keep their body; of other groups only the first
    variant; **the mesh cut down to 65535 indices** (`tools/decimate.py`: 3.3.5 reads a section's
    triangle start as 16 bits, so every section has to begin within the first 65535 indices, and
    today's models have 85,000 to 140,000; quadric-error half-edge collapses, which keep every
    vertex's texture coordinates, normal and bones and leave boundaries and seams alone, take
    from the gear first, then the features and the hair, the body last: the log says how much of
    each); every batch one texture (body, cape, hair; the tentacle and jewellery textures fixed); mesh
    sections of at most 64 bones, each section's bone combo naming the very bones its vertices
    carry (the game draws with the combo); cameras in 3.3.5's layout. `<Name>.layout.json` tells the
    texture tool where the head went. **`tools/check_m2.py`** checks a model the way the game
    would trip over it, its sequences' own files too (each track's entry within its `.anim`, every
    bone's translations and scales real floats within 100 yards, a global sequence's track's times
    within its loop); each model is checked after it's
    scaled, and one with a problem stops the package.
  - **`tools/scale.py`**: each model made its kin's height (above), measured on the converted
    model as `tools/render_m2.py` poses it (its head's bone in Stand); the vertices, the bones' pivots and every translation
    (the model's and its `.anim` files'), attachments, events, cameras, bounds, collision and the
    skin's section centres scaled about the feet, so every pose is the old one scaled.
  - **`tools/textures.py`**: the skins (512 x 512 palettized, as the HD looks': 3.3.5's compositing
    needs palettized textures; the body half of today's), FaceLower (the head's used part, turned
    if that fits better, 256 x 128; nightborne with the eye colour's glow painted in), FaceUpper
    (the eyes, 256 x 64), underwear (256 x 128), hair (as it is, DXT). `tools/blp.py` reads and
    writes BLP2 (palette, DXT1/3/5). `tools/names.py` names them for both the textures and the
    tables.
  - the voices as MP3s (ffmpeg: mono, 44.1 kHz, constant 64 kbit/s, no tags or VBR header), made
    from the game's files each time (an MP3 an earlier run left cut short still decodes in part); one
    ffmpeg can't read whole stops the package.
  - `alliedraces.files` is taken out as the package starts and written last, so a package that
    stops leaves none, and the world server doesn't make the patch from part of the files (the races
    aren't in the game then: `scripts/package-azerothcore.sh` says so and carries on).
- As the world server starts, as soon as its configuration is read (`src/AlliedRaces.cpp`),
  `src/AlliedRacesPatch.cpp` makes the game's `Data/patch-V.MPQ` (read after the HD looks'
  patches, whose character tables it builds on, and before Wrath Remix's `patch-Y` and the
  Skyborne's `patch-Z`, which are made later in the start from the client with it in and so carry
  its rows: Remix's patch takes the looks' and models' tables from the client for that; made at
  the startup like theirs, it came after them on a first start and the game didn't know the races
  until the next) from the module's `data/client` and the package's `data/files`: the tables with the rows
  changed, the models, textures and voices, the character screen's files, the race icons with
  their portraits, the narrations. Made again only when the client, the module or the files
  change (the stamp in `patch-V.MPQ.alliedraces`); a `patch-V.MPQ` that isn't the module's is
  left alone. `AlliedRaces.ClientPatch = 0` (`mod_allied_races.conf`) takes it out. The letter V
  is free of the HD looks' (the alternative HD look has a `patch-W`).
- The archive reading and writing, the tables and the textures in C++ are the Skyborne's
  (`mod-skyborne/src/SkyborneFiles`), which this module includes.

## Tests

- `tools/test_tools.py`: the texture codec round-trips, the converter's pieces (the sequence
  lookup, the geoset policy, the coordinate remapping, a sequence's file made one block, a
  track's entry checked against its file), the size (a one-bone model's head measured, then scaled
  with its own file's animation, pivot, attachment and section), races.json's shape, the tables naming
  the textures the way they're made. CI runs it.
- **`tools/check_looks.py DBC_DIR`**: the creation screen's tables out of a client's whole patch
  chain checked for every look it can step to (each player skin with the faces of its race and
  sex's others, a death knight's with the other death knights', hair colours for every style and
  its geoset row, the features 0 to n-1 each once, the looks' display and model rows): the rule crash report
  #34 broke. Run here on the Alternative HD Patch's tables with this module's and the Skyborne's
  patches in: 53 races and sexes, no problem; on the rows before that fix it finds 926, with
  the patches before allied-races-9 and skyborne-15 32 (the creatures' facial hair styles left at
  the new races' numbers: run on the Alternative HD Patch's CharSections over ChromieCraft's HD
  archive, with the server's creature tables).
- `tools/test_screen.py`: `AlliedRacesCreate.lua` in Lua 5.1 against stand-ins for the game's
  screen, alone and with the Skyborne's screen code after it (the character list's music by the
  selected character's race too). CI runs it.
- `tools/test_safety.py`: a global sequence's track read from the model where the first sequence
  is kept outside it, and merged from its own loop's track; `check_m2.py` finding a track's entry
  past the end of its `.anim` and translations that aren't real floats; the narrations' rows
  naming their file alone. CI runs it.
- `tools/test_voices.py`: the voices made with the real ffmpeg (the game's MP3 format, the sound
  whole; one left empty or cut short made again; a file ffmpeg can't read whole stops the package,
  leaving no voice and no list of files). CI runs it.
- `tools/test_intro.cpp`: the patch made for a stand-in game from the module's intro tables and
  narrations, each race's intro followed as the game does (its cinematic, camera, sound and the
  sound's file in the patch, the user's MP3 byte for byte, played alone). CI runs it.
- `tools/test_voice_tables.cpp`: this module's and the Skyborne's voice tables applied in the
  game's order (this patch, then the Skyborne's on it): every race's words at the UI's moments and
  emotes as each module made them, no moment twice, each of the four races with its 51. Fails on
  the rows before allied-races-9 (the Skyborne's over the void elves' first eight). CI runs it.
- `../mod-skyborne/tools/test_table_moves.cpp`: the creatures' races moved in a client's own rows
  (both modules). CI runs it.
- `tools/test_patch.cpp`: the patch made for a stand-in game from the package's files and read
  back (races, looks and their textures, models, voices, spells, the screen, a second start keeping
  it). Built and run here against the server's tables and a local package.
- **`tools/render_m2.py MODEL.m2 FILES DBC_DIR OUT.png`** draws a converted model the way the game
  reads it (the sections through their bone combos, posed on Stand, the composed character
  texture, the model's own cameras) to a PNG: how the model will look, short of the game itself.
  Run here on all four models before a release. It reads the sections' triangle starts as the
  game does (16 bits), so a model over the limit shows its damage here first.
- `tools/check_m2.py` on every converted model (every vertex's bone slots lead through its
  section's combo to the bones the vertex names: the first models' didn't, and the game drew them
  in pieces; every track's entry for a sequence kept outside within its `.anim`; run here: all
  eight pass, on the package of allied-races-9 too; the HD look's blood elf,
  read the same way, passes but for what the HD look itself leaves out).
- CI's server test: the world server makes the patch (19 tables) before the Skyborne's and Wrath
  Remix's, the races are playable in the world database with their looks, a warrior of each starts
  in its place with its racials; then each in the world (`warcraft/server/allied_*.steps`):
  Preternatural Calm's aura, Spatial Rift through the rift, Arcane Pulse's, Light's Reckoning's
  and Light's Judgment's damage as the character's own, Regeneratin' and Pterrordax Swoop on the
  character, the race's own first quest offered and the start race's not, Rescue the Survivors!
  credited with the lent Gift of the Naaru, handed in to Zalduun, and the gift taken back. Not tested: Entropic
  Embrace's and Embrace of Pa'ku's procs, Demonbane's and City of Gold's amounts.
- Not tested: the game itself (the models drawn, the looks, the voices, the intros, the screen on
  a phone): nothing here runs the 3.3.5 client.
