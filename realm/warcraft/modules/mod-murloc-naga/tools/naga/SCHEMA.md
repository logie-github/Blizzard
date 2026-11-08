# The naga's questline: how a chapter is written

The naga's story (the bible: `scratchpad/naga/bible.md`) is written as the murlocs' is: a chapter is a Python file
of plain data, `tools/naga/chN_<name>.py`, that `tools/murloc/compile.py` turns into the world database's rows
(`data/sql/chromiecraft/world/naga_story.sql`). Everything in `tools/murloc/SCHEMA.md` holds (its last section,
"More", was written for this story); this file says what's different for the naga. `tools/naga/ch0_people.py` is
the shared cast (people who come back chapter after chapter, placed by each chapter's SPAWNS);
`tools/naga/ch1_low_tide.py` is chapter 1 (the model for the others: format and how much every scene acts);
`tools/naga/test.steps` the server test's steps (with the story's names), which each chapter's writer extends.
`content.py`'s `NAGA_CHAPTERS` says how many chapters are released (the ones after are still being written: a
reference to one of their quests is a quest no one has done yet).

Run `tools/build_data.py` (the module's README says how): it compiles the murlocs' story, then the naga's (clear of
the murlocs' phases), checks that neither race sees the other's people, prints the naga's lint warnings, and writes
the SQL, the patch's rows and `warcraft/server/murloc_naga_naga.steps`. A mistake it can be sure of stops it.

## What's different from the murlocs'

- **Words are readable.** The naga's people (the Tide-Broken, the Spitelash, the crèche) speak Nazja, shown as
  written; so does everyone in a memory (Universal); `language="orcish"` is readable too (the naga speak it). Give
  every land-walker a language (`darnassian`, `thalassian`, `common`, `troll`...): the game garbles it for a naga.
  The lint warns of a person with a playable race's look and no language. A quest text is the character's voice,
  never the instructions (bible 4.1); the goal says what to do.
- **The naga's models play little** (bible 4.2): see "More" in `tools/murloc/SCHEMA.md` for what they play; the lint
  warns of the rest. Give gestures to the land-walkers and the mur'gul (`murloc_abyssal`: every emote).
- **Looks and sounds by name.** The profile's (`tools/murloc/profiles.py` NAGA_LOOKS: `vashj`, `illidan`, `maiev`,
  `kaelthas`, `akama`, `malfurion`, `tyrande`, `magtheridon`, `kiljaeden`, `arthas`, `anubarak`, `guldan`, the
  Spitelash's, the Coilfang's...; NAGA_SOUNDS: Vashj's fourteen Serpentshrine lines, `vashj_intro`...), and the
  assets' (`tools/naga/looks.py`, `tools/naga/sounds.py`: converted models and fetched Warcraft III voices, by
  their file names: `("sound", "self", "LadyVashjReady1")`). Every look and sound named must be the game's or in
  those ranges (an error otherwise). Don't use one of the assets' before the assets make it (the server has no
  such look or sound until then).
- **Ids** (`profiles.py`): creatures 990000-991999, objects 1990000-1991999, quests 992000-992599 (992599 kept
  for "a quest not written yet"), items 993000-993799, spells 994000-994399, spawns 9900000-9939999, graveyards
  9900-9939, object looks 10400-10599, new looks (display_extra) 40200-40299. Lady Szaria, Myrmidon Ssaveth and
  Vyssa the Coral-Keeper keep the retired Darkshore camp's entries (`entry=975017` etc. in ch0: no one else may).
- **No one else's quests until the last** (`final=True` on the story's last quest: Thrall's, bible 21.1): the
  module's gate closes every other quest open to the naga until it's handed in, then the Horde's are theirs.
- **Graveyards** (GRAVEYARDS) as the murlocs': a naga whose story isn't done wakes at the nearest of the story's.

## Phases

- **Azshara alone.** A chapter's `alone_until="<quest>"` (chapter 1's: `"ch7:ch7_live_world"`, bible 7.24) keeps
  Azshara the naga's phase alone (no world) until that quest's reward; chapter 7's writer gives that quest that
  key (or chapter 1's `alone_until` the key it has). Valormok (area 1237) shows the world and the naga's from the
  first login (the profile's `world_areas`).
- **Story phases** (`phase=("from", ...)`, `until`, `during`, `between`) as the murlocs'. The naga's bits in a zone
  are never the murlocs' there (the murlocs' chapter 10 is in Azshara: the compile is given their bits and takes
  others: in Azshara today eleven at most, the two of the sixteen story bits the murlocs leave there and nine
  the game doesn't use there; the memories' three are apart). The build stops if they run out, or if either race
  could see the other's people.
- **Everyone "always" there** carries the naga's phase alone (2048), never the murlocs' or the world's.

## Memories (bible 2.2, 7.2, 18.2, 18.3)

```python
MEMORIES = [
    dict(key="m1", name="The Awakening", whose="Isshara", bit="B",       # its aura: "Reliving: The Awakening"
         text="Isshara's memory: the night the call reached the deep.",  # the aura's text on the bar
         stage="m1_arrive", facing=1.2,                                 # where one arrives
         centre="m1_centre", radius=150,                                # its ground: leaving it wakes one
         pool="hollow_pool", pool_facing=3.0,                           # where one wakes
         singer="ch0:isshara", again="Sing it again."),                 # the way back in (her gossip)
]
NPCS = [dict(key="young_vashj", name="Lady Vashj", look="vashj", size=1.4, untouchable=True, at="m1_vashj",
             phase=("memory", "m1"), ...)]
QUESTS = [dict(key="ch1_awakening", ..., memory="m1", wake=True,
               accept=[("state", "self", "channel"), ("sound", "self", "NagaSirenReady1"), ("wait", 3000), ("relive", "m1")])]
```

- A memory is an aura on the player: `("relive", "m1")` puts it on (a quest's scene, an object's, or the singer's
  gossip), `("wake", "m1")` or the completion of a quest with `wake=True` (its objectives done; four seconds
  later, the song's last note) takes it off. The module does the rest: the screen fades, the player goes to
  `stage` with the memory's phase alone (no present, no world: every phase of the naga's is given only without the
  module's marker, the profile's `race_spells`), the naga of their party near them on one of its quests go in too;
  and out again, to `pool`. The aura shows the game's flashback look (`screen=`, default 21).
- **Its people and things** are `phase=("memory", "<key>")`: always there, seen only by one reliving it. They must
  stand on its ground (within `radius` of `centre`: an error otherwise); objects and SPAWNS likewise.
- **Its quests** are those with `memory="<key>"`: no choices in them (`path`, `exclusive`, `prev_any`: an error;
  history doesn't change). Their givers and enders may be in the memory or in the present (the singer).
- **Bits**: `bit="A"`, `"B"` or `"C"` (the bible's 18.2 table: A for M0, M2, M3, M6, M7, M8, M12; B for M1, M4, M5,
  M9, M11, M13, M14, M19; C for M10, M15 to M18, M20, Ithessa's). Memories sharing a bit must stand 500 yards apart
  (an error otherwise: one would be seen from the other).
- **A death inside**: alive again at once at the pool, the memory's unfinished quests started over (out of the log
  and in again: their kills and gathered quest items gone), no corpse. Back in through the singer (`singer=`).
- **A logout inside**: awake at the pool at the next login. **Leaving its ground** (walking, swimming or being
  taken out of its radius, or off its map): awake at the pool.
- Big scenes' speakers (bible 18.3) can be summoned for the scene (`("summon", ...)` from someone in the memory:
  a summoned creature takes its summoner's phase).

## Test steps

`tools/naga/test.steps` (auth_check.py's steps, with `{chN:key}` for the story's ids, `{xyz:chN:place}` and
`{z:chN:place}` for places): a naga shaman from its start. `cmd .gps` and `has Phase: 2048` check the phase; a
memory's is its bit alone (A: 2, B: 4, C: 8).

## Known limits

- A quest's own words (title, text, progress, reward) are always readable, whoever gives it; what a land-walker says
  aloud (say, yell, gossip) is in their language.
- A converted look (`tools/naga/looks.py`) plays what its EMOTES entry lists; the lint doesn't check them: keep to
  that list by hand.
- `at_health` beats run, but can't give credit (the core's health event has no player to give it to).
- A memory's singer offers the way back in while any of its quests is in the log (a quest with `wake=True` only
  while it's unfinished: it's handed in in the present).
