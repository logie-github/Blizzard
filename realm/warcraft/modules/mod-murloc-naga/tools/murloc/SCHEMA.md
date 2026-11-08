# The murlocs' questline: how a chapter is written

A chapter is a Python file, `tools/murloc/chNN_<name>.py`, holding plain data (no logic) that
`tools/murloc/compile.py` turns into the world database's rows (quests, people, objects, items,
scripts, gossip, map markers) and checks. Write every text in plain English: the compiler runs it
through Blizzard's Nerglish translator (`tools/nerglish.py`), so the player reads none of it. The
quest log's one-line goal (`goal`) stays English. Alliance and Horde people speak their own language
(`language`), which the game garbles for a murloc.

So every scene must work with the words gone: what people DO is the story. Use beats (below):
emotes, sounds, moving, handing things over, spell visuals, music, summoned creatures. Bracketed
stage directions are not shown to anyone; don't write them.

## The file

```python
CHAPTER = dict(key="ch1", title="The Pens", levels=(10, 15), map=1, zones=[331], hub="pens",
               start="first_step", start_facing=1.5,      # (the first chapter's: where a new murloc stands)
               alone_until="ch1_breakout")                # (its zones show the murlocs' phase alone, no world,
                                                          #  until that quest's reward)

PLACES = {                      # named points: (x, y) on the ground, or (x, y, z) exactly
    "pens": (4213.0, 1012.5),
    "overseer_rock": (4190.2, 990.1, 12.3),
}

NPCS = [
    dict(key="elder", name="Elder Mrrglmrgl", subname="Tribe Elder", look="oracle", level=12,
         side="tribe", role="quest", at="pens", facing=4.7,
         idle=[("state", "self", "sit"), ("every", 20000, [("emote", "self", "talk")])]),
    dict(key="overseer", name="Wrathtail Overseer", look="naga_male", level=(11, 12), side="naga",
         role="enemy", at=["overseer_rock", (4200, 1000), (4205, 1010)], respawn=120),
    dict(key="trainer_warrior", name="Grrbl", subname="Warrior Trainer", look="warrior", level=30,
         side="tribe", role="trainer:warrior", at=(4220, 1015), facing=1.2),
]
```

- `looks=[...]`: up to three more looks (the database takes four in all), one picked per spawn.
- `look`: a key of `LOOKS` in `tools/murloc/common.py`, or a CreatureDisplayInfo id. The tribe's
  murlocs are `murloc_<skin>` (grey, blue, green, pale, orange, gold, fel, red, purple, slate, abyssal,
  bronze, ice): the race's own murloc with emotes (talk, point, cheer, bow, wave, cry, laugh, beg,
  applaud, kneel, rude, kiss, flex, eat, question, exclamation, yes, no, sit, sleep, work, dance all
  play). The game's other murloc looks (`oracle`, `tidehunter`...) play no emote but attacks, spell
  casts, stun, cower and swimming: use them for enemies and crowds, never for someone who acts. Naga
  looks play talk, work, roar, battle roar and casts; people of the other races play everything.
- `level`: a number or (min, max).
- `side`: `tribe` (friendly to murlocs, can't be attacked), `naga` (hostile), `hostile` (hostile to
  murlocs, an enemy), `neutral` (yellow), or a FactionTemplate id; a town's own people (a sentinel,
  a guard, a carter) are `faction:<Faction.dbc id>` (the murloc's standing with the town decides: at
  war, they attack on sight). A sympathizer, wherever they stand, is `tribe`: friendly to the murloc
  whatever its standing.
- `role`: `quest`, `vendor`, `trainer:<class>` (warrior, hunter, rogue, priest, shaman, mage),
  `profession:<skill>` (first_aid, cooking, fishing, skinning, mining, herbalism, leatherworking,
  tailoring, blacksmithing, alchemy, engineering, enchanting, jewelcrafting, inscription),
  `innkeeper`, `repair`, `banker`, `stable`, `auctioneer`, `travel`, `ambient`, `enemy`, `guard`; several
  joined by `+` (`"trainer:rogue+banker"`). A vendor sells `sells=[item entries]` (default: food).
  `travel`: `travel=[("<place>", "<quest key>" | None, "words")]`, a gossip line each (teleports there;
  shown once the quest's done; the words, English, are Nerglish to the player).
- `watch=(yards, [beats], cooldown ms)`: a player coming that near (in sight) starts the beats ("player"
  is them): a Lasher's hiss, point and lash; a slave hiding. Default cooldown 15000.
- `at_health=(30, [beats])`: in a fight, hurt to that share of its health, its beats (a duel's end:
  `("faction", "self", "tribe")`, `("evade", "self")`, `("state", "self", "kneel")`). A `("credit", quest)` here gives
  nothing: the core's health event has no player to credit (a kill or an emote objective instead).
- `plural`: how an emote objective names them ("pen slaves": "/wave at pen slaves 0/5").
- `at`: a place, a point, or a list of them (one creature at each).
- `language`: `nerglish` (the default for murlocs: translated), or `common`, `orcish`, `darnassian`,
  `dwarvish`, `gnomish`, `taurahe`, `troll`, `gutterspeak`, `thalassian`, `draenei` (English as
  written; the game garbles it for murlocs), or `naga` (naga speak Common in the game; English,
  garbled likewise).
- `idle`: beats it repeats when nobody's doing anything with it (see `every`).
- `phase`: when it's there: `always` (the default), `("from", "<quest>")` (from that quest's
  reward on), `("until", "<quest>")` (until that quest's reward), `("during", "<quest>")` (while it's
  in the log), `("between", "<quest>", "<quest>")` (from the first's reward until the second's).

```python
OBJECTS = [
    dict(key="kelp", model="kelp", name="Kelp Bed", at=["kelp1", (4230, 990)], kind="loot",
         loot=[("kelp", 1, 2)], quest="ch1_kelp"),          # a loot object (only on the quest)
    dict(key="cage", model="cage", name="Slave Cage", at="pens", kind="use", quest="ch1_free",
         goal="Slave Cage opened"),                         # used for a quest's credit: the quest's objects=
    dict(key="hut", model="murloc_hut", name="Hut", at=(4210, 1020), kind="doodad", scale=1.1),
]
```
`model`: a key of `MODELS` in common.py or a game model path ("World\\...\\X.mdx"). Kinds: `loot`,
`use` (clicked once for a quest's credit; `beats=[...]` a scene it starts: the object's own beats are
sounds, summons, objects and auras, anyone else's (an NPC key: the nearest of them) anything),
`doodad`, `chair`, `mailbox`. `phase` as NPCs'.

```python
ITEMS = [
    dict(key="kelp", name="Slimy Kelp", icon="kelp", stack=20),                   # a quest item
    dict(key="spear", name="Pen-Breaker Spear", icon="spear", kind="weapon:spear", quality=2, level=14,
         stats=[("str", 3), ("sta", 2)]),                                          # a reward
]
```
An item with `aura="<aura key>"` puts that aura on the player when used (a disguise in a barrel);
`consumed=True` uses it up. Kinds: quest items (no `kind`), `food` and `drink` (like the game's of their `level`: its spell and
price), `bag` (`slots=8`), `weapon:<dagger|sword|axe|mace|spear|staff|fist|bow|gun|wand>`,
`armor:<cloth|leather|mail|plate>:<head|shoulder|chest|waist|legs|feet|wrist|hands|back>`,
`ring`, `neck`, `trinket`, `shield`, `offhand`. Stats: str, agi, sta, int,
spi, ap, sp (spell power), hit, crit, dodge, def, mp5, armor.

## Quests

```python
QUESTS = [
    dict(key="ch1_kelp", title="Kelp for the Cauldron", giver="cook", ender="cook", level=10,
         prev="ch1_wake",                       # the quest before (or a list: all of them)
         goal="Gather 6 Slimy Kelp from the shallows north of the pens.",
         items=[("kelp", 6)],                   # and/or kill / explore / interact / use / escort
         text="The pot is empty again. The naga take the fish and leave us the bones...",
         progress="Still nothing for the pot?",
         reward="Kelp! Now the little ones will eat tonight.",
         accept=[...beats...], complete=[...beats...],
         poi=["kelp_beds"],                     # where the map marks it
         tone="boring", path=None,              # path: "hero", "menace" or None
         rep=[(69, 150)],                       # Faction.dbc id, standing (negative for a menace)
         rewards=["spear"], choice=["ring_a", "cloak_b"], money=150),
]
```

Objectives (up to four kinds, four entries each):
- `kill=[("<npc key>" | <creature entry>, count)]`
- `items=[("<item key>" | <item entry>, count)]` and where they come from: `drops={"kelp":
  [("overseer", 40), (3711, 25)]}` (chance %, on the quest only), or loot objects (OBJECTS).
- `explore="<place>"` (with `radius`, default 15 yards): reach the place.
- `interact=[("<npc key>", "What you do, in English: a gossip line shown as Nerglish")]`: talk to them.
- `use=[("<item key>", "<npc key>" | "<place>", count)]`: use a quest item on a creature or at a place. At a place
  it's a small thing there to click (the item's name) while carrying the item on the quest: the item is spent, the
  credit given, and a fourth element `[beats]` plays (the object's own scene).
- `escort=("<npc key>", ["p1", "p2", ...])`: they follow you; reach the last place with them.
- `objects=[("<object key>", count)]`: use the story's objects (kind `use`, `quest` this quest; `goal` on
  the object is the log's line for it: "Slave Cage opened 0/4").
- `emotes=[("<npc key>", "wave", count, [beats])]`: the player's own emote at them (/wave, /bow,
  /dance, /roar, /cheer, /hug, /salute, /cry...: common.py TEXT_EMOTES), each answering with the beats
  (their own: "self"); one credit per emote, a few seconds apart per creature.

The giver gives a `source` item if the quest needs one (`source="cage_key"`).

More: `learn=[spell ids]` (taught as it's handed in: a class quest's stance, Tame Beast...),
`reward_spell=<id>` (cast on the player as it's handed in), `time=180` (seconds to finish it), `classes=["warrior"]` (only them), `repeatable=True` (a
chore), `details=["talk", "point"]` (the giver's emotes as it's offered), `reward_emotes=["cheer"]`
(the ender's as it's handed in), `plain_reward=True` (the reward text as written: the story's last
quest alone, the first words a murloc can read; finishing it teaches the murloc Common), `exclusive=N` (quests sharing N: taking one closes the others).

`prev_any=["ch2_honor", "ch2_totem"]`: after either of them (a hero/menace pair's next quest); with a
`prev` list too, after all of those and either of these.

`level` is the quest's level; `min` defaults to level - 2. `xp` (1-8) defaults to 7; the last of a
chapter's chains and set pieces take 8.

## Beats

A beat is a tuple. `who` is `"self"` (the giver or ender), an NPC key (the nearest one of them), or
`"player"`.

| Beat | What happens |
| --- | --- |
| `("say", who, "English text", "emote"?, sound?)` | speaks (Nerglish, or its language); optional emote and sound |
| `("yell", who, "text", ...)` / `("whisper", ...)` | the same, louder / to the player alone |
| `("emote", who, "point")` | plays an emote once (names: common.py EMOTES, or an Emotes.dbc id) |
| `("state", who, "dance" \| "sit" \| "kneel" \| "sleep" \| "work" \| "none")` | keeps doing it |
| `("sound", who, <SoundEntries id or name>)` | plays a sound there |
| `("music", <SoundEntries id or name>)` | plays music to the player |
| `("visual", who, <SpellVisual or spell id or name>)` | a spell's look, nothing else, on `who` (the player casts it on themselves; another person on themselves, their own scene still running) |
| `("cast", who, <spell id or name>, target)` | casts it (target "player", "self" or an NPC key) |
| `("move", who, "<place>", "walk" \| "run")` | goes there |
| `("face", who, "player" \| "<place>")` | turns |
| `("jump", who, "<place>")` | jumps there |
| `("give", "<item key>", count)` | hands the player something |
| `("take", "<item key>", count)` | takes it back |
| `("summon", "<npc key>", "<place>", seconds)` | it appears for a while (with its own idle) |
| `("despawn", who)` | it goes |
| `("credit", "<quest key>")` | completes an `event` objective (`event="text"` in the quest) |
| `("teleport", "player", "<place>", facing?)` | moves the player there (a vision, a crossing) |
| `("aura", who, "<aura key>")` / `("unaura", who, "<aura key>")` | puts an aura (AURAS) on them / takes it off |
| `("object", "<object key>", "<place>", seconds)` | an object appears there for a while |
| `("follow", who)` | they follow the player |
| `("faction", who, "tribe" \| "naga" \| "hostile" \| "neutral" \| id)` | whose side they're on now (until they respawn) |
| `("evade", who)` | they stop fighting and go home |
| `("wait", ms)` | pause before the next beat |
| `("every", ms, [beats])` | (idle only) repeats beats on that period |
| `("every", ms, [beats], ("until", "ch1_breakout"))` | (idle only) only where it stands in that phase (a slave's habits in the pens, not at later hubs) |

Order matters; each beat follows the last at once unless a `wait` comes between. Keep sequences
under a minute. A beat given to someone else (an NPC key) is theirs to do, the player still the one
it's for ("player" in it is the player: Sloshy following, a sentinel facing them); they must be
within 80 yards of whoever runs the scene. A quest's scene interrupts a person's idle; an idle never
interrupts a scene. An object's own scene (`beats` on an object) can summon, set out objects, give
auras and items, and hand beats to people; it can't speak, emote or play a sound itself.
Emotes once: `dance`, `work` too (EMOTES); for a lasting dance or work, `state`.
Sounds that loop (BeachDay 4164, BoatSailFlapLoop 5454, MurlocBabyDanceLoop 8485, any "Loop") play on and
on: don't use them in beats. A quest whose reward ends its ender's phase plays its reward scene where the
player no longer sees it: put the show in its accept or its talk instead. An escort's follower must be
within 80 yards of the giver as the quest is taken.

Everyone a scene hands beats to must share a phase with whoever runs it: someone "always" there
shares every phase; two people in different story phases can't see each other.

Phases: a story phase (`from`, `until`, `between`, `during`) is given in the zones its people and
things stand in, wherever that is; someone "always" there is seen by every murloc and can find any
story-phased person for a scene.

## Auras, more spawns, graveyards

```python
AURAS = [                       # spells of the story's own, shown on the bar with their name and text
    dict(key="brand", name="Salt-Scar", kind="mark", text="Branded by the naga.", icon=1126),
    dict(key="barrel", name="Barrel Disguise", kind="disguise", look=4553, seconds=300),  # another look
    dict(key="heavy", name="Heavy Coral", kind="slow", percent=40, seconds=60),
    dict(key="lashed", name="Lashed", kind="stun", seconds=2),
]   # kinds: mark, disguise (look: a CreatureDisplayInfo id or LOOKS key), slow, speed (percent), stun, root;
    # seconds: 0 lasts until taken off; icon: a spell id whose icon it shows; visual: a SpellVisual id

SPAWNS = [                      # more of someone already made: the hub's people at a later hub, or the
                                # game's creatures (an entry) in the murlocs' phase
    dict(npc="ch1:murlorga", at="hub_pot", phase=("from", "ch3_arrival"), facing=2.0),
    dict(npc=3711, at=[(4100, 950), (4110, 960)], wander=8, respawn=60),
    dict(object="ch0:mailbox", at="hub_post", phase=("from", "ch3_arrival")),   # an object likewise
]

GRAVEYARDS = [                  # where a murloc wakes as a ghost (the nearest on its map), with a spirit healer
    dict(at="hub_shore", name="the pens", phase=("until", "ch1_breakout")),
]
```

## Finding places

Positions come from the world: the research's gazetteer (`scratchpad/murloc/gazetteer.md`) and
`tools/murloc/where.py`, which says what's at a spot (land, shallows or deep water; the game's creatures
and objects nearest) and finds the game's creatures by name:

    WOW_SERVER_MAPS=... WOW_WORLD_SQL=... python3 tools/murloc/where.py 1 4213 1012
    WOW_SERVER_MAPS=... WOW_WORLD_SQL=... python3 tools/murloc/where.py find "Wrathtail" 1

Someone standing needs land (or a building's floor: give z, as a creature of the game's stands there);
an (x, y) is put on the ground, which under water is the sea floor (fine for murlocs and naga).

## Sounds, visuals

`common.py` names the usual sounds (`murloc_aggro`, `naga_hiss`, `splash`, `tavern`...); any
SoundEntries id works, and the research's `effects.md` lists them by kind, with ~140 spells NPCs can
cast for their look alone (bubbles, sparkles, frost, smoke, summons...) by id.

## Guards and towns

Towns are the game's. A murloc not in good standing is attacked by guards within a few yards, and
warned first in their own language (the module does it). A chapter only says which towns it sends
the player into (`TOWNS = ["Astranaar"]`), so the compiler can check standing quests.

## Names

Keys are `chN_<word>` for quests, plain words for the rest; unique within the chapter (the compiler
prefixes them with the chapter). Refer to another chapter's thing as `"ch2:<key>"`.

## More (written for the naga's story, open to both)

The compiler compiles a race's story from its profile (`tools/murloc/profiles.py`: its race, phases, ids,
tables and words); the naga's notes are `tools/naga/SCHEMA.md`. These work in either story; the ones a mistake
is easy in are checked as the story compiles (an error stops the build) or by `compile.lint` (a warning).

People:

```python
dict(key="vashj", name="Lady Vashj", look="vashj", size=1.4, untouchable=True, ...),   # a head taller than a naga
dict(key="kiljaeden", name="Kil'jaeden", look="kiljaeden", size=6.0, sky=40, at="sky_spot", ...),
dict(key="garithos", name="Grand Marshal Garithos", language="common", untouchable=True, at="garithos",
     display_extra=dict(race="human", sex="male", skin=1, face=1, hair=1, hair_color=1, facial=0,
                        gear={"head": "item:12640", "chest": "item:12618", "tabard": "item:15196"})),
dict(key="cannon", name="Coral Cannon", look=..., level=18, turret=True, abilities=[(9053, 3000)], summoned=True),
```

- `untouchable=True`: never attacked or killed, by players or creatures (a canon figure: bible 18.3); still
  clicked for its quests. An enemy can't be untouchable (an error).
- `size=1.4`: how big, whatever the look's own scale (Lady Vashj's look is 3.5 times a naga already: `size`
  takes it out); `scale=` stays the multiplier on top of the look's own. Not both (an error); 0.05 to 20.
- `sky=40`: its spawns stand that many yards above the ground (or the water there), floating (no gravity).
- `equip=(main hand, off hand, ranged)`: what they hold, the game's item ids (0 for none): a trident, a bow.
- `speed=1.5`: how fast they walk and run, against the ordinary (an old matron 0.7, a scout 1.4).
- A beat handed to someone else reaches the nearest of them within 80 yards, measured in three dimensions (one on a
  cliff far below is out of reach: nothing happens).
- `display_extra=dict(...)`: a new look of a playable race's person (race: human, orc, dwarf, nightelf, undead,
  tauren, gnome, troll, bloodelf, draenei; sex: male, female; skin, face, hair, hair_color, facial: the game's
  character choices, checked against its CharSections; gear: head, shoulder, shirt, chest, waist, legs, feet,
  wrist, hands, tabard, back, each an ItemDisplayInfo id or "item:<entry>" for an item's look; flags, bake: the
  game's own fields, rarely needed). Not with `look=`. Only a story with its own look range has it (the naga's).
  Not seen in the game yet: the client may want a baked texture for such a look (`bake=`).
- `turret=True`: rooted where it stands, it shoots what comes near with its `abilities` (a ranged spell: an
  error without them); on the Horde's side by default (`ally`, the naga's) or `tribe`.

Beats:

| Beat | What happens |
| --- | --- |
| `("morph", who, "<look>")` / `("morph", who, None)` | another look until they respawn / their own again (bible 1.12: the Highborne become naga) |
| `("scale", who, 1.4)` | bigger or smaller until they respawn (0.05 to 20) |
| `("sound", who, "LadyVashjReady1")` | a sound by name: common.py's, the profile's (Vashj's Serpentshrine lines: `vashj_intro`...) or a fetched one's (`tools/naga/sounds.py`) |
| `("sky", "<npc>", "<place>", 60, 30)` | the NPC appears 60 yards above the place (ground or water) for 30 seconds, floating (Kil'jaeden in a storm) |
| `("relive", "<memory>")` / `("wake", "<memory>")` | the player into a memory / out of it (the naga's: `tools/naga/SCHEMA.md`) |

Objectives:

```python
quiz=[dict(npc="isshara", ask="Ask me.", question="What did the water show you?", goal="Isshara's question answered",
           answers=[("The Empress, saving us.", False, [("say", "self", "No. Listen again.")]),
                    ("Fire, and the Well, and the sea coming in.", True, [("emote", "self", "omnicast")]),
                    ("Nothing.", False, [])])],
```
- `quiz`: while the quest is in the log, unfinished, the NPC's gossip offers `ask`; it opens `question` with the
  answers (2 to 8, one right: an error otherwise); the right one is the objective's credit (and its beats, the
  NPC's own), a wrong one its beats and the question again. Several entries, several objectives.

```python
tug=dict(cart="cart", path=["road_1", "road_2", "mid", "road_3", "gate"], midpoint="mid",
         enemies=[("raider", "ambush_1"), ("raider", "ambush_2")], back="road_1",
         taken=[("say", "self", "...")], retaken=[("emote", "self", "talk")], radius=40, seconds=600),
```
- `tug`: the tug escort (bible 7.09, 7.14). Taking the quest calls the cart (an NPC, `summoned=True`; one quest a
  cart) at the path's first place; it walks the path (`run=True`: runs); at the midpoint the enemies appear at
  their places and it rolls back toward `back` (default the start), its `taken` beats; once every one of them is
  dead it turns (`retaken`) and goes on; at the last place everyone of the race within `radius` with the quest has
  its objective (an event quest: the goal says what). If the player isn't near then, they take the quest again.

```python
turrets=[dict(npc="cannon", at=["plot_1", "plot_2", "plot_3"], seconds=90, goal="Coral cannon planted", model="crate")],
```
- `turrets`: a plot (an object, `model`, `name`) at each place, used while the quest is in the log: each use is
  the objective's credit (`count`, default the plots') and puts the turret (an NPC with `turret=True`: an error
  otherwise) there for `seconds`.

Items:

```python
dict(key="jar", name="Heavy Water Jar", icon="letter", carry="heavy"),   # AURAS: dict(key="heavy", kind="slow", ...)
```
- `carry="<aura>"`: while it's in the bags the aura is on the player (the module, every second): a heavy jar
  that slows (bible 7.20a, 9.17). The aura goes when the item does.

Auras: kind `screen` (`screen=<ScreenEffect.dbc id>`): the screen looks otherwise while it's on (21, "Arthas
Memory Events", the game's flashback look; 201, a dark transition; 41, a mist), checked against the game's table.

Emotes and poses for the naga's models (bible 4.2): `talk`, `roar`, `battle_roar`, `spell`, `omnicast`, `work`,
attacks, `wound`, `throw`, `drown`, `stun`, `ready1h`, `ready_bow`; poses (`state`) `channel` (singing, praying,
remembering), `channel_directed`, `drowned` (lying still), `swim_idle`, `ready_thrown` (a trident shouldered),
`ready_bow`, `work`, `talk`, `roar`, `stun`, `dead`. `compile.lint` warns of any other on a naga's model: it stands
still for it.
