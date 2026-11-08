# mod-murloc-naga: the Murlocs and the Naga

Two races of the app's ChromieCraft realm (not Wrath Remix's: "Only chromie needs new races"), both starting at
level 10 (the user: "Murloc to alliance and naga to horde", "Both start at level 10"), each at its own story's start:
the murlocs in the Zoram Strand's slave pens, the naga at Rethress Sanctum in Azshara.

| Race | Id | Side | Starts | Classes |
| --- | --- | --- | --- | --- |
| Murloc | 19 | Alliance | The Wrathtail's slave pens on the Zoram Strand (Ashenvale): their story's start | Warrior, Hunter, Rogue, Priest, Shaman, Mage |
| Naga | 20 | Horde | Rethress Sanctum, the Spitelash's crèche on Azshara's south coast: their story's start | Warrior, Hunter, Rogue, Priest, Shaman, Mage, Warlock |

Races 19 and 20 were the game's Taunka and Northrend Skeleton, which only creatures use; in the game's tables they
move to 30 and 31 (the client's own rows of theirs, whatever their ids: their race, looks, hair shapes, facial hair
styles and voice rows), as the other race modules move theirs to 22 to 29.

## What they have

- **Models and looks**, from the game's own files (the Alternative HD Patch's when it's in: the user's look):
  - *Naga*: the game's naga character model (`Character\Naga_\`, men and women; the HD look has its own of both),
    its five skin colours a sex, and four more made from them (the colours of the game's creature naga: the naga
    lords' crimson, the sirens' gold and violet, and a grey for the men, silver for the women). The naga's one face
    is the game's. Added to that model as the realm makes the patch (`tools/naga_looks.py`): Blizzard's own naga
    headdresses and outfits (Battle for Azeroth's Nazjatar naga wear them; made for the naga's body, `_na_m` and
    `_na_f`):
    - **Headdress** (the hair style): none, and for men the myrmidon's crown and the warlord's helm, for women the
      sea witch's headdress (on the head's bone, where the newer naga's helm attachment is);
    - **Headdress color**: each headdress's colours (three or four, its item displays' textures);
    - **Features**: none, and each outfit in each of its colours (men: the myrmidon's harness in three, the warlord's
      plate in four; women: the sea witch's regalia in four), on the naga's own bones.
    The game's naga have no hair or facial hair of their own: their rows named textures the game hasn't, and are the
    headdresses' and the features' now.
  - *Murloc*: Blizzard's newer murloc (`creature/murloc2/murloc2.m2`, the murlocs of Cataclysm on) made a character's
    model: its fins cut from its body (the triangles its blue skin paints the fins' gold) and drawn in a colour of
    their own, its kin's parts (the murlocs built on the same skeleton: every bone of theirs at one of its bones'
    places) as geosets the creation screen picks (`tools/murloc_looks.py` says what each choice is):
    - **Skin color** (13): the body in every skin the game gives that model and its re-skinned kin (grey, blue,
      green, pale, orange, gold, fel, red, purple, slate, abyssal, bronze, ice);
    - **Eye Color** (the game's Face, 16): the eyes of each of those skins (silver, sky, jade, pearl, amber, gold,
      fel, blood, violet, lilac, abyssal, ember, frost) and three made from them (onyx, rose, sea green);
    - **Fins** (the hair style, 6): murloc2's crest as it is, short, long and swept back; the classic murloc's crest
      (the murlocs of 2004); the deep sea murloc's sail along its head and back;
    - **Fin Color** (the hair colour, 16): the fins of each skin (gold, crimson, plum, amethyst, rust, fel, olive,
      teal, abyssal, sand, frost) and five made from them (coral, sea green, azure, ebony, bone); the other models'
      fins recoloured to each;
    - **Features** (the facial hair style): none, the demon hunter murloc's horns, the deep sea murloc's lure, the
      demon hunter's blindfold, the shark-hooded murloc's outfit, the loincloth, and for women Maria's hair, and
      her dress with her hair (the Darkmoon Faire murloc in a dress).
    The murlocs have no hair: their hair choices are the fins' (the labels set by `MurlocNagaCreate.lua`). The files
    are the game's of today, fetched and made 3.3.5's as the server is packaged (`tools/murloc_model.py`, never in
    this repository); `tools/render_murloc.py` draws every choice to a contact sheet.
  - *How the choices are drawn*: the game draws a character's body with its composed texture (the skin colour's
    base, the face's two textures, armour), its hair with the hair row's texture, and shows one geoset of each group
    by the hair and facial hair styles. The murloc's body and eyes read the composed texture's face region (FaceUpper
    and FaceLower, 256 x 192 at the HD looks' scale): a face row (an eye colour, in each skin colour) fills it, the
    body's lower part in FaceLower and the eyes beside the body's upper part in FaceUpper. Its fins read the hair
    texture: a hair row (a fin style, in each fin colour) names the fins' colour. A fin style is a geoset of group 0
    (2 to 7); a feature one of group 1 (none 101, which the model hasn't: the game takes a facial style's geoset 0 as
    "leave the group as it is", and showed every feature at once). The eyes' own bones are the head's on the model
    (their animations draw the eyeballs back into the head as the murloc stands).
  - *A player's model*: the game draws a player as a character (all of the above) only on a model its
    CreatureModelData flags a player's (0x4). The murlocs' models take a playable race's flags (the human's, 0x804);
    the game's naga male hasn't the flag (its female has), so the patch sets it on both naga models. Without it, in
    the world a murloc was drawn as a creature is: white, every fin and feature at once (the user's screenshot of
    1.0.449), while the creation screen, which draws the race's character itself, was right.
- **Armour** on a murloc: the game paints armour into a character's composed texture, in its regions for arms, chest
  and legs; the murloc's body and eyes read only the face region, which armour never paints, so a murloc stays a
  murloc in any armour. Helmets, shoulders and gear models need places on the model a creature hasn't: they don't
  show. Weapons in hand do.
- **Racials** (learned at creation from `playercreateinfo_spell_custom`):
  - Murloc: **Amphibious** (breathe underwater, swim 50% faster), **Mrrgglll!** (a war-gurgle: enemies within 8
    yards stunned for 2 sec, 2 min cooldown), **Slippery** (dodge +1%).
  - Naga: **Serpent's Grace** (breathe underwater, swim 50% faster), **Tail Sweep** (enemies within 8 yards stunned for
    2 sec, 2 min cooldown), **Scales of the Deep** (armour from items +5%).
- **Stats, standing, quests and items**: their kin's, the night elves' for the murlocs and the trolls' for the naga:
  every quest, item and condition open to the kin is open to them (the game's race masks, theirs OR'd in), once their
  story is done (each story's gate, below). The naga are also **neutral** to Darnassus (Azshara's Talrendis Point and
  Shadowsong Shrine are its people's), the Explorers' League (Ironforge) and the Gnomeregan Exiles.
- **Level 10, and their class's spells**: the world server makes a new character level 10 at its first login, at full
  health, and teaches it every spell its class's trainers teach up to its level; and again at every level after (they
  start far from their kin's trainers). A rank of a talent's spell once the talent is theirs.
- **Their stories' places**, seen by their own race alone: each race's phase where its story goes (`spell_area`: an
  aura with its phase, and the world's where the story shows it), so nothing of the game's world changes for anyone
  else, and neither race sees the other's people (both stories are in Azshara: below). The first releases' homes,
  the murlocs' island village west of Auberdine and the naga's renegade camp north of it, are retired (their ids
  kept; the camp's Lady Szaria, Myrmidon Ssaveth and Vyssa the Coral-Keeper are the naga's story's people now).
- **The intros**, seen once at a new character's first login: a flight over their home (each its own camera, written
  by `tools/cameras.py`), with the game's own sounds as narration: the murlocs' own voices for the murlocs (a village
  waking, a fry's dance, a warning, a war-gurgle, a cheer, 42 seconds); for the naga, Lady Vashj's (61 seconds, below)
  over Azshara.
- **Character creation**: twenty races, each side's ten in two columns (the allied races' and the Skyborne's layout),
  their icons (the game's murloc head and murloc oracle, Warlord Kalithresh and Lady Vashj), the Dwarves' scene for
  the murlocs and the Tauren's for the naga (framed for their height), their texts.
- **Voices**: at the UI's moments ("not enough mana"), the game's own creature sounds: the murlocs' gurgles, the naga's
  and the sirens' hiss. Their people gurgle (or hiss) as they're spoken to, and the murlocs cheer as a quest is handed in.
- **Add-ons**: Questie's race table gets them as their kin (the murlocs the night elves, the naga the trolls).

## The Murlocs' questline

The murlocs start at the Zoram Strand (Ashenvale), slaves of the Wrathtail naga, and level from 10 to 55
through a story of their own: being one murloc of a tribe, not part of the wider world, escaping the
naga's tyranny, with serious, funny, stupid and boring quests, some a hero's and some a menace's. The
story is data (`tools/murloc/ch*.py`, written as `tools/murloc/SCHEMA.md` says) that
`tools/murloc/compile.py` makes the world database's rows (`data/sql/chromiecraft/world/murloc_story.sql`).
The Darkshore island village of the first release, and its seventeen quests, are retired.

The story (a story bible written first, then a writer for each chapter, all of them agents): the
Saltscar, slaves of the Wrathtail at the Zoram Strand, ten chapters, 299 quests written (both sides of
each hero/menace pair, class lessons, chores):

| Chapter | Levels | Where | Hub |
| --- | --- | --- | --- |
| 1 The Pens | 10-14 | the Zoram Strand (the pens' own phase: no world until the breakout) | the Huddle, a capsized boat |
| 2 The Free Shore | 14-19 | Darkshore's south coast, Auberdine at night | Greymist Cove |
| 3 Saltscar | 19-24 | the Zoram Strand, Blackfathom's mouth, Maestra's Post, Zoram'gar | the Drowned Pier, then the freed pens |
| 4 The Long Swim | 24-29 | the Wetlands, Menethil's harbour | Saltscar Shallows by the Bluegill |
| 5 Torn Fins | 29-33 | Hillsbrad's coast, Southshore, Tarren Mill | Torn Fin Cove |
| 6 The Stone City | 33-36 | Westfall's coast, Stormwind's harbour and canals | Murk-Eye's Grotto |
| 7 Brokenchain | 36-40 | Dustwallow Marsh, Theramore's pier, Brackenwall | the Mire Islets |
| 8 Red Sails | 40-44 | Stranglethorn's south coast, Booty Bay, Nek'mani Wellspring | the wreck of the Lucky Cod |
| 9 The Last Walk | 44-48 | Feralas's coast, Sardor Isle, the Isle of Dread | Colossal Cove |
| 10 The Storm Bay | 48-55 | Azshara: the Bay of Storms, the Ruins of Eldarath | Saltscar Landing |

What holds the story together:
- **Nerglish.** Every word a murloc reads is Nerglish: Blizzard's own translator of April 2019 (its
  script, `assets.webn.mobi/nerglish/nerglish.js`), ported word for word in `tools/nerglish.py` (its
  Mersenne Twister seeded by each word's hash, its letter chain, its dictionary of real murloc words:
  "friend" is always "mmmrrglllm"). Only each quest's one-line goal in the log stays English, and the
  names of what it asks for. Another race's words are garbled as the game garbles a language one doesn't
  know (`tools/murloc/garble.py`, its LanguageWords).
- **Their language.** Murlocs speak Nerglish (the game's Titan language, renamed in the patch, its
  words murloc words) and not Common: what Alliance and Horde people say is gibberish to them, and
  theirs to everyone else.
- **Show, don't tell.** Every scene is acted: talk, point, cheer, bow, cry, kneel, beg, laugh, sit,
  sleep, dance... with sounds, moves, spell visuals and music (SmartAI). The game's murloc models have no
  emotes; the murloc costume (BlizzCon 2007's) has them all, on a skeleton like murloc2's, and
  `tools/murloc_anims.py` adds its 32 emotes to murloc2, bone for bone: to the race's models (a
  murloc player's /talk and /cheer play) and to the tribe's people (`Creature\MurlocTribe`, in each of
  the 13 skins). Quests mark the map where they want you.
- **No one else's quests.** Until its story's last quest, a murloc takes no Alliance or Horde quest, nor
  any open to all: a gate the module builds as the world server starts, from every quest the world
  database has (other modules' too): each quest's conditions, and a murloc's alternative with the story
  done. Then the Alliance's are its too.
- **Hostile towns.** A murloc starts Hostile (-3500) with the Alliance's and the Horde's towns
  (Stormwind, Ironforge, Darnassus, Gnomeregan, the Exodar; Orgrimmar, Thunder Bluff, the Undercity, the
  Darkspear, Silvermoon): at war, their guards attack it and it them. The goblins (the Steamwheedle
  Cartel and its four ports) are mercenary: Unfriendly (-500), they neither trade with it nor attack it.
  Standing earned with sympathizers ends the war (the core's own rule, above Hostile); a menace's deeds
  cost it. The story's last quest makes the Alliance's towns Neutral.
- **Guards.** In every town (AreaTable's town flag) a murloc keeps a Low Profile: creatures notice it at
  5 yards, the game's least. A guard that doesn't like it warns it off first, as it comes within 20
  yards: it turns, points or shouts, in its own people's annoyed voice and language (Darnassian for
  Sentinels, Dwarvish, Gnomish, Orcish, Taurahe, Gutterspeak, Thalassian, Troll, Common...), which a murloc
  can't understand; one that likes it salutes.
- **Trainers.** The tribe's class trainers and profession trainers teach, in Nerglish (the game's
  trainers' spell lists); a murloc learns no spells by itself after level 10. Each hub has the same
  people (an innkeeper, a banker in a hollow log, a stable, later an auction house through a goblin
  fence), and a Current-Caller who takes it to the hubs it has reached.
- **The tribe's graveyards.** A murloc whose story isn't done wakes as a ghost at the tribe's nearest
  graveyard (with a spirit healer), never in a town's.
- **The pens.** Until the breakout, Ashenvale shows a murloc only its own phase: the pens, the naga
  who keep them, the crabs on the reef; none of the world (its Wrathtail would kill a level-10 slave).
- **Acting it out.** Quests ask for the player's own emotes (/wave at the slaves), put marks and
  disguises on it (a Salt-Scar brand, a barrel), stun it with a Lasher's whip as it strays, set props
  out, take it into visions and across the sea, have the tribe's fry follow it.
- **Murlocs of the first release** speak Nerglish from their next login, are Hostile with the towns,
  and, if still in Darkshore, go to the story's start.

## The Naga's questline

The naga start at Rethress Sanctum in Azshara, the lowest of the Spitelash's crèche, and level from 10 to 55 through
a story of their own, all of it in Azshara (the user: the naga in Azshara, 10 to 55, Lady Vashj's war from Warcraft
III, lore accurate; a story bible written first, then the chapters): living memory. Azshara as it is in 3.3.5 is the
present; Warcraft III's campaign comes back as memories the naga live, each on Azshara's own ground in a phase of its
own. As the murlocs' story is, it's data (`tools/naga/ch*.py`, written as `tools/naga/SCHEMA.md` and
`tools/murloc/SCHEMA.md` say) that the same compiler (`tools/murloc/compile.py`, with the naga's profile:
`tools/murloc/profiles.py`) makes the world database's rows (`data/sql/chromiecraft/world/naga_story.sql`).

**Where it stands**: the engine is built; chapter 1, The Low Tide (`tools/naga/ch1_low_tide.py`, levels 10 to 15:
the crèche at Rethress Sanctum, its 35 quests and two memories), and the shared cast and hub kit
(`tools/naga/ch0_people.py`) are written; chapters 2 to 10 are being written. The story isn't released until it's
whole (the gate would close every other quest to a naga with nothing after chapter 1).

What holds it together (the engine):

- **Readable words.** The naga's people speak their own tongue, shown as written, and so does everyone in a memory;
  Orcish is theirs too (the Horde's camp at Valormok); other races' words are garbled as the game garbles a language.
- **No one else's quests.** Until its story's last quest (Thrall's, in Grommash Hold), a naga takes no Horde quest,
  nor any open to all: the module's gate (as the murlocs'), made as the world server starts from every quest the
  world database has. Both stories' gates live in the same conditions: a quest's own condition groups (or one of its
  own) say "not a murloc" and "not a naga" for those it's closed to; each race has its own way in once its story is
  done (the quest's groups again, with its last quest done). Flights out of Azshara are allowed; quests aren't.
- **Azshara alone.** Until chapter 7's live world quest, Azshara shows a naga only its own phase (none of the zone's
  level 42 to 60 creatures); Valormok (the Horde's camp) shows the world and the naga's from the first login.
- **Phases that don't cross.** The murlocs' chapter 10 is in Azshara too: each story's people carry its own race's
  phase and its own story bits alone (never the other's, never every bit, as the murlocs' did before), and the naga's
  story is compiled after the murlocs' and given the bits theirs use in each zone, taking others (in Azshara also
  bits the game doesn't use there). The build stops if either race could see the other's people.
- **Memories** (the module, `src/MurlocNaga.cpp`): a song at a pool takes the naga into one (the screen fades, the
  memory's stage, its phase alone: no present, no world; "Reliving: <its name>" on the bar and the game's flashback
  look on the screen; the naga of their party on its quest go in too); its last quest done, the song's last note and
  they wake at the pool. A death inside: alive again at once at the pool, the memory's unfinished quest started over
  (no corpse run); back in through the singer. A logout inside: awake at the pool at the next login. Leaving the
  memory's ground: awake at the pool. Three phase bits carry every memory (memories sharing one stand 500 yards apart).
- **What the story's scenes can do**, beyond the murlocs': people turned into another look or size (`morph`,
  `scale`), the canon figures untouchable, someone sized whatever their look's own scale, people placed high in the
  sky (Kil'jaeden), new looks of playable races' people (Garithos, the Highborne court), a question with answers
  (a wrong one asks again), the tug escort (a cart the enemy takes back at the midpoint), turrets at plots, a heavy
  thing carried that slows. Each is in `tools/murloc/SCHEMA.md`, checked as the story compiles.
- **Their graveyards**: a naga whose story isn't done wakes at the story's nearest (with a spirit healer).

Lady Vashj's words are the naga's intro (re-cut for the story: no spoiler of her death, its end): the game's own
lines of hers (Serpentshrine Cavern's), who the naga were and what they wanted ("Water... is life... We are the
Highborne, and the time has come at last for us to retake our rightful place in the world!") and their war on the
surface ("I did not wish to lower myself by engaging your kind...", "Death to the outsiders!", "The time is now!
Leave none standing!", "Seek your mark!", "Victory to Lord Illidan!"), then the present: the sea off Rethress Sanctum,
the crèche's horn and far off a siren's hiss (the game's sounds), over a 61 second flight from the Bay of Storms along
Southridge Beach, up past the Ravencrest Monument and down to the crèche, where a new naga stands.

### The naga's retired start (the first release's)

The renegades' camp on the island north of Auberdine, its phase in Darkshore and Ashenvale, and its five quests
(Blood in the Water, Sealed Orders, The Tide Turns, Strangers on the Shore, An Unlikely Allegiance) are gone (their
ids kept), and with them the Darkshore Alliance quests opened to the naga and the conditions that closed Darkshore's
way out to the Alliance (undone where a realm had them). The naga's neutral standing with Darnassus stays.

What SQL alone can't do here, and what does it instead:

- **A race the game knows**: the client has its own ChrRaces, CharSections, CharBaseInfo... and can't make a race the
  server's tables alone have; the module's patch for the game (below) gives it the rows, the murloc's model and skins.
- **A Horde race some Alliance people talk to**: possible in SQL only through reputation (the naga's Darnassus slot).
  People of a faction without reputation (the Alliance's generic templates) react by the two sides' faction templates,
  the same for every race of a side; changing that for one race would need a player faction template of its own in
  the client too (and the core's `IfNormalReaction` hook changes the server's mind alone).
- **Level 10 at creation, and their class's spells as they level**: the core's start level is one setting for every
  race (`StartPlayerLevel`); the module's script makes theirs 10 at the first login and teaches the trainers' spells.
- **Their homes seen by them alone**: a phase is an aura's; `spell_area` gives it by race and zone, in SQL, but the
  aura is a spell the client must know too (the patch's Spell rows).
- **The intros**: a flight is a camera the client plays (its file in the patch) and the world server follows (the
  same file in its data folder).
- **Memories**: a phase given and taken by an aura (the memory's: its bit alone) and a marker the module puts on,
  which every one of the naga's phase rows needs absent (`spell_area`'s aura condition); the module moves the
  player in and out, and handles a death, a logout and leaving the ground inside one (`src/MurlocNaga.cpp`).
- **A story's gate**: conditions on every quest, made by the module as the world starts from the quests there are.

Assumed, not seen in the game (nothing here runs the 3.3.5 client):

- That the client draws a player of race 19 and 20 from the model its ChrRaces row names
  (`Character\<ClientFileString>\<Sex>\<ClientFileString><Sex>.m2` and the display ids: both match), and the
  murloc's composed texture as the naga's and the allied races' (512 x 512 skins, the face textures drawn over their
  region).
- That the client shows a reputation faction's people as the server's standing says (it gets the standing from the
  server: the same rule).
- That the client reads `Data/<locale>/patch-<locale>-T.MPQ` after `patch-S` and before `patch-U` (the other race
  modules' order, the Skyborne's `Game`).
- That the memories look as meant: the game's flashback screen effect (ScreenEffect 21) and the fade (201), and a
  new look of a playable race's person (display_extra) drawn without a baked texture.

## The naga's story's assets

What the naga's story (its bible's 18.5 and 18.6) uses that the 3.3.5 game hasn't. The files are Blizzard's, made as
the server is packaged and never in this repository; the rows are in the patch and the world database either way.

- **Voices** (`tools/naga/sounds.py`: `SOUNDS["LadyVashjReady1"]` -> 995000, the story's sound beats' table; `WORDS`
  their words): 82 Warcraft III unit lines (Lady Vashj's 21, the naga siren's, myrmidon's and royal guard's, Illidan,
  Maiev, Kael'thas, Garithos, Akama, Tyrande, Malfurion, Arthas, a dreadlord, the pit lord), SoundEntries 995000 to
  995081 (`Sound\Creature\WC3Voices\<name>.wav`, as Lady Vashj's own lines are played: a creature's speech). The files
  are warcraft.wiki.gg's (`/images/<name>.wav`; its robots.txt allows the folder), or Wowpedia's copies of the same
  files, each checked against the SHA-1 and size the table pins: all 82 are already the game's own format (16-bit
  PCM, mono, 22,050 Hz) and are written without the wiki's tags. Without a file, the game plays nothing for its row
  and the line shows as text.
- **The naga's emotes** (`tools/naga_emotes.py`): the 3.3.5 naga models have no bow, wave, cheer, laugh, cry, salute,
  kneel, point, sit, sleep or mount pose, and no naga model of today's game has the full set either (today's naga, the
  naga lord, the elite naga, the sea witch, the siren, Azshara's naga: talk, work, roar, kneel and point at most). So:
  kneel (and its start, loop and end) and point are today's naga's own, bone for bone; sitting is the naga's tail coiled
  as it kneels with its upper body upright, riding the same with the night elf's riding arms, sleeping its own
  drowning (a collapse into a coil, lying, and back); and the rest (bow, wave, cheer, talk with an exclamation or a
  question, applaud, beg, chicken, flex, kiss, laugh, shout, cry, shy, dance, salute, eat, rude, train, yes, no) are
  the night elves' (today's night elf character models: the naga were night elves), on the naga's upper body (spine,
  chest, neck, head, jaw, arms, fingers: the female's four arms each as the night elf's arm on its side), its tail held
  as it stands. 39 sequences a sex (6 of them the game's aliases of others). As the patch is made, `MergeEmotes` adds them to the client's own naga models
  (an HD look's, with one in) after their headdresses and outfits: each bone found at its place, its keys worked out
  against the client model's own parents (the 3.3.5 naga's tail bones all hang from one bone, today's from each
  other); the sequences it already has are left as they are.
- **Models** (`tools/naga_models.py`, `tools/naga/looks.py`): Serena Scarscale's sea witch (Battle for Azeroth's,
  `creature/seawitch/seawitch.m2`), Maiev's Watchers (Legion's warden, in its four skins) and Queen Azshara as a night
  elf (Cataclysm's), made 3.3.5's (Wrath Remix's converter, and: sequences with ids 3.3.5 hasn't left out, each batch
  its own first texture, textures over 1024 made 1024): CreatureModelData 3800 to 3802, CreatureDisplayInfo 40000 to
  40005, `creature_model_info` for the server. The sea witch talks, works, roars, channels and holds and shoots a bow;
  the warden and Azshara have every emote (looks.py's EMOTES). Azshara's texture keeps no colour where its alpha is 0
  (a quarter of it: most of her gown, spots of her gold), and her batches draw it opaque: those texels are given the
  colour around them (her cream gown, as warcraft.wiki.gg's screenshots of her in the Well of Eternity show it, not
  black), and her two-texture batch (hair, jewellery: the colour and an environment map, today's Opaque_Mod2xNA_Alpha)
  draws one texture made of both (the map's mean colour where the alpha lets it through).
- **Looks of the game's parts** (CreatureDisplayInfoExtra 25000 to 25007 with CreatureDisplayInfo 40010 to 40017, no
  baked texture: dressed from their items): Grand Marshal Garithos (a human in Lordaeron's blue and silver plate, a
  closed helm, the Alliance's tabard), Handmaiden Vashj and the Highborne court (night elves in the Highborne
  Summoners' robes), Taelon Emberveil (a blood elf in red and gold), Shaelyn Harborsong (an old night elf in green
  leathers). `LOOKS` names every look for the chapters (`LOOKS["serena"]` -> 40000); `FALLBACK` gives a look of the
  game's for the converted ones' people when their models weren't made.

## How it's made

- **`tools/build_data.py DBC_DIR WORLD_SQL_DIR MAPS_DIR`** reads the game's tables (the server's dbc folder), the core's
  world SQL and the server's maps (the ground's height, the water's: `tools/terrain.py`), and `tools/content.py` (the
  people, things, places and quests, every word of them), and writes `data/sql/chromiecraft/world/murloc_naga_world.sql`,
  `data/client/dbc/*.txt` (the rows to change in the game's tables), `data/client/looks.txt` (what textures and model the
  patch makes from the game's), `data/client/narration.txt` (the intros' sounds) and `data/client/Cameras/` (the intros'
  cameras, `tools/cameras.py`). Committed; run it again after changing it.
- As the world server starts, as the configuration is about to be read (`src/MurlocNaga.cpp`: first of the race modules'
  patches, the modules loaded in their folders' order), `src/MurlocNagaPatch.cpp` makes the game's
  `Data/<locale>/patch-<locale>-T.MPQ` from the client's own files: the tables with the rows changed, the naga's new
  colours, the icons, the screen's files, the cameras and the narrations (the game's WAVs mixed, 22050 Hz mono); and
  the murlocs' model and textures the server package brought (`data/files`, `murloc.files`: below).
- **`tools/murloc_model.py fetch DIR`** (run by `scripts/package-azerothcore.sh` as the server is packaged) fetches
  murloc2, its kin (`murloc2shark`, `murloc2maria`, `dhmurloc`, `murlocdeepsea`, the classic `murloc`), their skins
  and parts' textures from wago.tools by their file ids and writes the murlocs' files: murloc2 converted by Wrath
  Remix's converter (`mod-wrath-remix/tools/models.py`); its body's and eyes' texture coordinates moved into the
  composed texture's face region (the body's block 192 x 192, the eyes' 64 x 64); its fins cut from the body and, a
  copy a fin style, drawn with the hair texture (each spine lengthened or swept back from where it joins the body,
  or another model's fins); each part's triangles (the pieces of a batch's mesh by where they are, or a head's bones
  alone, or the bones murloc2 hasn't) added with its bones taken to murloc2's at the same places (a bone it hasn't,
  to its nearest parent it has), every section at most 64 bones; a track with one set of keys for every sequence
  given one a sequence (none for a sequence kept in its own .anim: its flag at byte 12). The face textures
  (`MurlocBody<skin>`, `MurlocEyes<eyes>_<skin>`) are palettized at the composed texture's scale; the fins'
  (`MurlocFins[Classic|Sail]<colour>`) 256 x 256. Its list, `murloc.files`, is written last; without it the patch
  says so and the murlocs aren't drawn.
- **`tools/naga_parts.py fetch DIR`** (run with it) fetches the naga's headdresses and outfits (`helm_*_na_m/_na_f`,
  `collections_*_na_m/_na_f`), their colours' textures (from their item displays) and the newer naga's skeleton, and
  writes each sex's parts (`Character/Naga_/<Sex>/Naga<Sex>Parts.dat`: each geometry's vertices with their bones'
  places, its triangles, the geosets and textures that draw it: an outfit's colours share its triangles, as the
  game reads a section's start in 16 bits) and textures, its list `naga.files` last. As the patch is made,
  `MergeParts` (`src/MurlocNagaPatch.cpp`) adds them to the client's own naga models (an HD look's, with one in):
  each vertex on the model's bone at its place (within 15 cm, or the parts aren't added), its triangles a section
  of each use's geoset, their textures its own (type 0) or the hair's (type 6, the headdress's colour).
  - **What the game draws into a character's composed texture** (the skin, faces, underwear) is made as the game's
    own character textures are: palettized (256 colours, every mip level) and at the scale of the skin it's drawn
    over (the HD looks' skins are 512: FaceLower 256 x 128, FaceUpper 256 x 64, underwear 256 x 128). The game's
    own naga faces and underwear are a quarter that size and compressed (never drawn by the game: the naga were
    never playable), and the murlocs' first faces were compressed: the character creation screen drew them green, and
    making the character broke the game's memory (crash report #110, at `CreateCharacter`). The game's naga rows
    also name hair, scalp and facial hair textures it hasn't (`Character\Naga_\Hair00_00.blp`, `ScalpLowerHair`,
    `ScalpUpperHair`, `FacialLowerHair`, `FacialUpperHair`): every texture the races' rows name that isn't in the game
    or the patch is left out of their look (the log says which). Read after the HD looks' patches (A, F, 6, E, Q, S:
  the Alternative HD Patch's SoundEntries; ChromieCraft's H, F, G, S, T) and before the Worgen and Goblins' patch-U, the
  allied races' patch-V, Wrath Remix's patch-Y and the Skyborne's patch-Z, which are made from the game with it in and
  carry its rows; it's made from the game without them (they come after it). Made again only when the client or the
  module change (the stamp in `patch-<locale>-T.MPQ.murlocnaga`); one that isn't the module's is left alone.
  `MurlocNaga.ClientPatch = 0` takes it out; on Wrath Remix (`MurlocNaga.Enable = 0`, set by ctl.sh) it's set aside.
  The world server reads the cameras from its own data folder's `Cameras` too (put there as the configuration is read), to
  follow the camera.
- **The naga's story's assets** (above): `tools/naga_assets.py` makes their rows (`add_naga_assets`, called once by
  `tools/build_data.py`); as the server is packaged, `tools/naga_emotes.py fetch DIR` (`Naga<Sex>Emotes.dat`,
  `nagaemotes.files`), `tools/naga_models.py fetch DIR` (`Creature/...`, `nagamodels.files`) and
  `tools/naga_voices.py fetch DIR` (`Sound/Creature/WC3Voices/`, `nagavoices.files`) make their files, each list
  last; the patch takes each list's files (`MergeEmotes` the emotes) and logs a missing list. A source that refuses
  leaves its files out with a line in the package's log (the tool exits 1, `package-azerothcore.sh` says what's
  missing and goes on: the package is made without them). What they fetch is cached with the allied races' files
  (CI's cache key covers `tools/naga_looks.py` and `tools/naga/*.py`, which name the files: `naga/sources.py` the
  emotes' models). `tools/render_naga.py` draws the models and the emotes to contact sheets.
- The SQL is ChromieCraft's alone: in `data/sql/chromiecraft/world`, which ctl.sh (`realm_sql`) puts in ChromieCraft's
  world database's update list, last.

## Tests

- `tools/test_patch.cpp`: the patch made for a game folder and read back (the races, their looks and the creatures'
  races moved, the murloc's model reading the face region alone, its face textures, the naga's colours, the icons,
  the screen, the cameras, the narrations' lengths, every composed texture palettized at the skin's scale, every
  texture the races' rows name there; the naga's emotes in the client's naga models (every id, every track with an
  entry for each sequence, the look-up and aliases, a second merge adding nothing), the 82 voices' rows and WAVs, the
  three models (3.3.5's, their skins, textures and animation files, no id 3.3.5 hasn't), their looks and the
  CreatureDisplayInfoExtra rows; a second start keeping it). Run here on a stand-in of the Alternative HD Patch's
  client (its files out of its archive); `--dump DIR` writes its naga models for `tools/render_naga.py`.
- `tools/test_screen.py`: `MurlocNagaCreate.lua` in Lua 5.1 with the Worgen and Goblins', the allied races' and the
  Skyborne's screen code after it: twenty buttons, their icons kept on their buttons, both sides' ten races in two
  columns, scenes, music, texts; Questie's table. CI runs it.
- `tools/test_data.py`: the committed data (the quests' givers, enders and items all there, every id in the module's
  ranges, the retired starts gone, the two stories' SQL apart: their ranges, their tables, their phases, each DELETE
  its own rows; the cameras as the world server reads them over the ground; the naga's story's voices and looks in
  their ranges and in the tables). CI runs it.
- `tools/build_data.py` itself checks each story as it compiles it (a mistake it can be sure of stops it), and that
  neither race can see the other's people; it prints the naga's story's lint warnings.
- CI's server test (`scripts/test-warcraft-server.sh`): the patch made before the other race modules', the races
  playable, the naga neutral to the three factions; a murloc warrior and a naga shaman start at their stories' starts
  at level 10 with their racials, language and class spells; then in the world (`warcraft/server/murloc_naga_*.steps`,
  made from each story's `test.steps`): the murloc's pens and every chapter's hub, Auberdine's quests closed to it; the
  naga at Rethress Sanctum in its phase alone, chapter 1's quests, a memory gone into, died in (alive at the pool, its
  quest started over), gone back into and woken from, a question answered, and Valormok's quests closed to it. On
  Wrath Remix, the patch set aside and no rows.
- Not tested: the game itself (the models drawn, the composed textures, the intros, the screen on a phone): nothing
  here runs the 3.3.5 client. The naga's emotes and the converted models were drawn with mod-allied-races' renderer
  (its reading of the files, not the game's); the looks of the game's parts weren't drawn at all (that renderer
  doesn't dress characters in items); the voices' fetch was run here, not on a GitHub runner.
