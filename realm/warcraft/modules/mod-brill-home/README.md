# A home in Brill (mod-brill-home)

ChromieCraft's realm alone (ctl.sh: `BrillHome.Enable`, and its SQL in ChromieCraft's databases only).

The user: "Add a small house facing the road, the same style house that's at Brill 59.28, 52.29. Add an
NPC inside and a quest where he decides to leave the house to you... Let you be able to speak to Jamie
Nore at the Brill town hall and she will give you upgrade options such as adding furniture... her first
quest be to go try out the bed... Sleeping will fade to black while doing a yawn emote... a small rested
xp bonus. Like a quarter of a level's worth."

## The house

Brill's farmhouse (the game's own `Duskwood_Human_Farm.wmo`, the house at Brill 59.28, 52.29; display
7432) as a gameobject (type 33, a destructible building, as the game's own world buildings are spawned),
beside the road north out of Brill, at (2275.0, 480.5), map 56.5, 51.9, its door onto the road. The
user, after four places: "The best place you think that doesn't look stupid and looks like a natural place
to put it". It was found by searching Brill (every spot and every turn) against the server's data
(`tools/build_sql.py` says how) for ground that holds the whole model level, beside a road, its door
onto it, with nothing in the way:

- the ground under the house level to 0.4 yards; the floor (4.1 above the model's base) 0.2 above its
  highest point, so the doorstep stands a quarter yard above the ground outside, as Brill's own
  farmhouse does (the earlier spots sloped 1.8 to 2.3 yards);
- the road (the town guards' patrol path follows it) 15 yards from the house's middle, the door turned
  to face it (290 degrees);
- no tree, doodad or spawn of the game's within the model's 19 by 18 yards; the Community Projects'
  builder's yard moved east of it to make room.

The house stands at Brill's north edge: the module's phases and the projects' stages apply in Brill and
within 35 yards of the house.

Everyone sees the house. What's in it is each player's own, by phases: in Brill (and by the house) the
module puts a player in the world's phase and the ones that are theirs; away from it, the world's alone.
A player under one of the game's own phasing spells is left as the spell has them.

| Phase | What | Whose |
| --- | --- | --- |
| 0x100 | Cedric Harrow | until his quest is turned in |
| 0x200 | the bed | from Jamie Nore's bed quest on |
| 0x800 | a kitchen table and two chairs (sitting works) | bought: 2 gold |
| 0x1000 | a wardrobe | bought: 1 gold 50 silver |
| 0x2000 | a bookshelf | bought: 1 gold |
| 0x4000 | a bearskin rug | bought: 50 silver |
| 0x8000 | a pot-bellied stove | bought: 3 gold |

## The quests

1. **The House by the Road** (Cedric Harrow, inside): a Forsaken who built the house in life for his
   family, rebuilt it after, and is leaving on the ship to Vengeance Landing; he leaves the house to
   someone the town can count on. To Jamie Nore.
2. **Welcome Home** (Jamie Nore): the deed signed; done as it's taken.
3. **Not on the Floor** (Jamie Nore): "We can't have someone living in this town sleeping on the floor
   now, can we?" The inn's spare bed carried over: sleep in it, then back to her.

After the deed, Jamie Nore's "I'd like to make my house more of a home." lists the furniture not
bought yet; each is paid for in gold and is in the house at once.

## The bed

Clicked: **Lie down to rest.** (onto the bed, lying along it, head at the headboard) or **Go to
sleep.**: a yawn, the screen fading to black and back (the app's add-on's fade), and asleep in the bed
until the player moves. Sleeping gives a quarter of the level's experience as rested experience (the
game's cap of a level and a half stays), at most once every six hours (`brill_home.last_rested`), and
the bed quest's credit.

### Inside the house, and the cellar

Everything in the house is placed against the farmhouse's own walls, measured from its collision model
(the server's `vmaps/Duskwood_Human_Farm.wmo.vmo`) and each model's own size (the game's files): the room
inside is x -5.25 to 5.5, y -5.75 to 5.5 in the house's coordinates; the hearth stands out from the north
wall (x -1.0 to 3.5, to y 4.6; its mantel 2.1 up); the door is x -3.0 to -0.25 in the south wall; braces
fill the north corners and posts the south ones; the loft is over the south third. The bed is in the
south-east corner under the loft, the table, chairs and wardrobe on the west side, the bookshelf and the
chests on the east wall, the rug and the dog's bed before the hearth, the stove beside it, the family
portrait over the mantel, and the projects' furnishings in the gaps (books and Croft's black candle on
the mantel). The house's model draws only its own loft barrels. No piece overlaps another, a wall, the
hearth or the doorway (the rug lies under a chair and the dog's bed).

The cellar hatch (boards in the floor by the rug) takes the house's owner down to the cellar: the game's
own cellar of a Duskwood-style inn (Brill's tavern is one: stone, barrels, kegs, crates and cobwebs, the
model's own), placed as an object (display 9700: the client's table in the module's patch, the server's
`gameobjectdisplayinfo_dbc`) 37 yards under the house, its top 6 yards under the lowest ground over it so
nothing shows above. In it: the ladder back up (display 9701, the game's Northrend human ladder), the
rats of Beneath the Floorboards (they run straight at what they fight: the server's paths don't know the
cellar's floor) and, behind their nest, the old stair bricked shut with the Cult's mark (the quest's
wall). A player in the cellar who falls through its floor (a game without the module's patch) or logs in
down there is put back in the house by the hatch. Before, the hatch was Gundrak's trapdoor scaled down,
still 10 by 15 yards with its collision, standing through half the house and blocking it, and there was
no cellar (the rats were on the house's floor). The Reclamation Library's flooded hatch was the same
trapdoor; it is boards now too.

Not checked on a phone: the cellar (how it looks from inside, its stair seen past the bricked-up wall), the
house as a gameobject (the game's own houses are part of the map), how the
sleeping pose lies on the bed (assumed: lying back along the way the character faces), and the
furniture's turns (assumed: the models' fronts at their +x).

## Corn, the dog

The first time the player sleeps in the bed, they wake to Corn beside it: a zombified pug, the game's own
pug in the user's Forsaken coat (`warcraft/branding/corn-forsaken-pug.png` (`warcraft/branding/corn-forsaken-pug.png`: gray-green, stitched,
glowing yellow eyes, his name on his collar's tag; the user: "Use this texture on the pug dog you get from
the quest in brill. Name the dog Corn", then "my pug is supposed to be zombified"). He doesn't talk; what
he does is shown: "(The dog looks happy to see you.)". His quest, **A Visitor in the Night**: throw the
stick for him three times (he runs out the door after it and brings it back) and scratch him behind the
ears. Turned in, the
dog is the player's pet, made as a hunter's tamed beast is, at their level, for any class:

- the game counts its keeper a hunter wherever it asks about pets (`OnPlayerIsClass`: the pet's kind,
  the stable master, Tame Beast, a pet's happiness and training), so it works as a hunter's pet does;
- they learn Call Pet, Dismiss Pet, Revive Pet, Feed Pet and Mend Pet (its ranks at a hunter's levels,
  learnt as they level), which go under General in their spellbook (not their class's);
- a player who already has a pet out or kept as their current one (a hunter's own, a warlock's demon)
  finds the dog waiting by the door: once there's room, "(Whistle for it to follow you.)".

Then any hunter trainer teaches them to tame beasts, as it does a hunter: their menu's "Teach me to
tame beasts, as you would a hunter." gives Tame Beast and Beast Lore (from level 10, a hunter's level
for it), under General too. Taming, the stable, a pet's food and talents are then a hunter's.

A hunter's dog is one more beside their own pet, never in its place (the user: "you can have your
current pets out but also the dog. To a limit of 2 for regular hunters and 3 out at a time for beast
masters"): a companion that follows them and fights what they fight (their target, or whatever is
fighting them), at their level; a beast master's (Bestial Wrath learnt) first stabled pet comes out
beside the two of them, in its own looks. Companions go while their hunter rides, flies or is dead, and
come back after; one left behind (more than 60 yards, another map) comes back to their side. They're
the game's guardians: the pet bar is their own pet's alone.

What it changes for classes with their own summons: a warlock, mage, shaman or death knight with the
dog counts as a hunter for pets too, so their own pets come back after a mount or a flight as a hunter's
do, and keep their spells' cooldowns when summoned.

His looks: the game's own pug (Perky Pug's model and display, 31174) in the user's coat. The coat
(`data/client/corn/ForsakenPug_Corn.blp`, a DXT5 BLP `tools/build_sql.py` makes from the user's texture) has the
game's own pug coat's layout, the same as the Alternative HD Patch's `Creature\Pug\Pug_Tan.blp`, so the module's
patch (`Data/<locale>/patch-<locale>-V.MPQ`, `src/BrillHomePatch.cpp`) puts it at the path the game's pug model
names for its coat; no model and no table of the game's is changed. In the game the `Data` folder's patches win
over the language folder's, and the HD patch's `Data/patch-F.MPQ` has its own coat at that path: the coat's path
is listed beside the patch (`.files`) and the Skyborne's `Data/patch-Z.MPQ`, the last of the `Data` patches,
carries it too. (Before: a display of his own, 39700, and then a model converted from today's game to 3.3.5a's
format both showed as the game's blue and white cube; the coat in this patch alone lost to the HD patch's.)
Every pug in the game wears his coat (Perky Pug is the only other). Without the patch in the game he's the plain tan pug. The quest dog,
adopted pets (in the stable too) and hunters' companions are all the pug's display; quest progress and pet
ownership are kept. An old `Data/patch-W.MPQ` of this module's (the mastiff's) is still taken out; the
Alternative HD Patch's water, which has the same name, is left alone.

## Carolai Anise

The user: "Make one you move in and get the dog that she can give a quest, essentially it's a quest line
where you can romance her or just say friends. The reward is the same as in you don't miss out on
anything. Except if you do become romantically involved you can have her move in to your house. Do about
a questline with 5 quests. Don't rush it but make it believable. Not just a mail order bride. And she's a
yandere. All in universe style dialogue."

Brill's alchemy trainer (by Apothecary Johaan, across the square from the house), once Corn's
quest is done. She watches the house from her bench; she's sweet, attentive, and a little too much of both.

1. **A Tonic for Corn**: the dog's scratching is blightmange, from the darkhounds. Kill 8 Cursed
   Darkhounds north of Brill; she brews the tonic ("I counted the howls from here").
2. **What Solliden Kept**: her mother's locket, left in the farmhouse at Solliden Farmstead when she died
   (the footlocker beside old Farmer Solliden, who doesn't remember her).
3. **A Gift for Jamie Nore**: a "perfume" for the woman who found you the house, "and that she needn't
   trouble herself over you any longer". Jamie smells bitterroot (rat poison), pours it out, and tells you
   Carolai asked her which key opens your door.
4. **An Unlocked Door**: she's in your house when you get home ("Your door was open. It was."), has swept,
   folded your shirts her way and made tea. Drink it: the locket's other side holds a lock of your hair,
   taken while you slept. Then to her shop, where she says it properly.
5. **What the Heart Keeps**: a moonpetal lily from Brightwater Lake's west shore (east of Brill, map 64.9,
   44.5, by the water; marked on the world map and the quest tracker, as the locket's farmhouse is; a pale,
   glowing flower, Felwood's songflower's model). It was first placed 2.9 map units north of the lake, on
   dry ground, as a plain small flower in the grass: the user couldn't find it; kept, in old Tirisfal, it meant yes. Giving it to her, the player answers:
   - **"I'm keeping it, Carolai. Yes."**: lovers. Her menu then has "Would you like to move in with me?":
     she's in the house from then on (her own lines at random; "(Hold her for a while.)"), until asked
     "Would you like some time back at your shop?" (asked again whenever the player likes).
   - **"You mean a great deal to me, Carolai. As a friend."**: friends ("I'll go on looking after you.
     You won't even notice.").

Rewards are the same either way (experience, silver, and the last one's 5 Healing Potions and 3 Lesser
Mana Potions). The answer is `brill_home.flags` (0x10 lovers, 0x20 friends; 0x40 living in the house).
Phases: her visit 0x10000 (after Jamie's gift until the tea), living there 0x20000.

Not checked on a phone: where she stands in the house, the footlocker's and the lily's spots (the
footlocker at Farmer Solliden's height, beside him; the lily at the terrain's height on the shore, found by the server's map of the lake's water).

## Brill: A Place Among the Forsaken

The user's design: separate, optional questlines that make Brill feel like a town the character lives in;
any can be started, left half done or ignored for good, none needs another (except where noted), and
their people keep their own routines. Each is a data file in `tools/town/` (its format:
`tools/town/README.md`), made into `data/sql/chromiecraft/world/brill_town_world.sql` by
`tools/build_town.py` and run by `src/BrillTown.cpp`. What a line changes in the town is shown to that
character alone (the town's phases, anywhere in Brill), or in what people say.

| Line | Quests (ids) | Giver | Choice | What stays changed |
| --- | --- | --- | --- | --- |
| The New House | 970200-970205 | Oswin Thatcher, carpenter (outside the house), after the deed | two free furnishings | debris until the timber; the cellar's rats while Beneath the Floorboards is on; lamps, a chest, the dog's straw bed; the housewarming's guests, now and then after |
| The Gravekeeper's Ledger | 970300-970304 | Mortimer Weller, gravekeeper (Brill's cemetery) | the newcomers walk in by day or by night | Mercy, Gideon, Edith and Walter living in Brill; the clue to Beneath the Gallows |
| The Apothecary's Apprentice | 970400-970404 | Apothecary Johaan | surrender the Stay, supervise Wendell Crane, or burn it | the yard behind the lab (apparatus, or charred remains); Wendell's, Johaan's and Carolai's words |
| Whispers of the Scarlet | 970500-970504 | Magistrate Sevren | expose Lowell Marsh, spare him, or let him go | Lowell gone or still lighting the lamps; the Deathguards' and Sevren's words; his letters via Renee |
| The Last Customer | 970600-970604 | Ambrose Wicke, Candles and Sundries (east of the town hall) | the candlesticks kept lit or sold | his stall's goods out, and his wares; his morbid cheer |
| A Deathguard's Duty | 970700-970704 | Deathguard Dillinger | Harlan back at his post or reassigned | Harlan on the north road or at the cemetery |
| Something in the Well | 970800-970804 | Maudie Fenwick, laundress (the square's new well) | none | the well clean, its water drawn; Maudie's washtubs |
| Beneath the Gallows | 970900-970904 | Deathstalker Isolde Ashcroft (by the mausoleum), once the house's cellar wall or the gravekeeper's passage is found | none | Aldric Croft's black candle in the house |

The Gallows' crypt is the game's own Agamand Family Crypt (its sentinels and Croft are everyone's to see);
the Last Customer's relative is at the Sepulcher in Silverpine. Lines notice each other where it fits (the
gravekeeper and Oswin's cellar mark; Maudie and Wendell's experiments; Dillinger and Lowell's fate; Oswin
and Carolai living in the house). Carolai: as lovers she lives in the house by turns at her alchemy table,
the stove, the dog's bed and the bookshelf; as friends she lets herself in one day in five; she and Jamie
Nore each have words for the other, and she has some on Wendell and the well.

### The Community Projects

The user's next design: once any three of the lines above (or Carolai's) are done, Magistrate Sevren's
**Brill Endures** (971000: tell Executor Zygand and Jamie Nore, ring the square's bell) opens the
builder's yard on the north road (Rudd Carver).
Six projects then open at once, each optional, each its own:

| Project | Quests | Leader | Where | Choices (words only) |
| --- | --- | --- | --- | --- |
| The Forgotten Shadow Chapel | 971100-971104, daily Names to Remember | Dark Cleric Mirelle Vane | east of the cemetery | Willem Vale's name added or the wall kept; Corven's answer |
| The Reclamation Library | 971200-971204, daily Lost Pages | Edmund Rook | Stillhome Lane, west edge | the artifact donated |
| The Stillgarden | 971300-971304, daily A Garden Is Kept | Edda Graves | Holt's Rise, the eastern edge | herbs or flowers to the front |
| The Surgeon's Hall | 971400-971404, daily Repairs Required | Surgeon Elspeth Rane | by Junior Apothecary Holland | a clinical charter or supervised research |
| The Caravan Office | 971500-971504, daily Brill Deliveries, Somewhere to Stay | Quartermaster Irena Sable | the Undercity road | Selwyn exposed or supervised; the first road |
| The Old Brewery | 971600-971604, weekly Brewer's Special | Brewmaster Oren Blackbarrel | beside the Gallows' End | the recipe; the signature drink's name |

Each goes Survey, Construction, Opening, Established, for each character as far as they've taken it: the
building, scaffolding, workers, its people and their wares show from the stage reached (the game's own
invisibility carries a project's stages: no phases needed; core patch 0012 lets a building be hidden so).
Established, each has its vendor (and a priest, herbalism or first-aid trainer), daily routines (the
town's day: morning, day, evening, night, as game events 230 to 233), visits to the other projects, and a
set of furnishings for the player's house, bought from its people. **The Town We Made** (971001), once all
six are open: a walk past the six leaders.

Every line has a realm test: `warcraft/server/brill_town_<line>.steps` (`.brilltown state`, `.brilltown use`).
Not seen in the game: any of the new places, the projects' buildings (placed by the game's collision
models: the chapel 30 yards east of its planned spot to clear the graves, the brewery a farmhouse, not a
barn, which fit nowhere by the Gallows' End), models' sizes and turns, the crypt's spawns inside it, the
new well and stall, the routes. Nothing here has run on a phone.

## The quests on the maps, and Questie

The user: "Be sure to add quest markers and stuff so that it shows objectives on the map and make it compatible
with questie". `tools/build_questie.py` (run by `tools/build_town.py` and `tools/build_sql.py` after them) makes both
from the module's world SQL:

- **The game's own markers** (`data/sql/chromiecraft/world/brill_quest_poi.sql`, `quest_poi` and
  `quest_poi_points`): for each of the house's and town's quests, a blob on the world map around where each
  objective is done (the objects that give it, the creatures to speak with or kill; the game's own creatures where
  the world database has them, read as the file is applied) and one at whoever takes it back. The tracker's map
  button and the world map's quest list show them.
- **Questie** (its 3.3.5 port, Questie-335, which doesn't know the module's quests): an add-on,
  `data/client/addon/BrillTown` (`BrillTown.toc`, `BrillTown.lua`), which the module puts in the client's
  `Interface/AddOns` at the realm's start (taken out with the patch, and on Wrath Remix's realm). As Questie's
  database starts at login, it adds the module's 89 quests and their creatures to the database's own runtime
  additions (`QuestieDB.questDataOverrides`, `npcDataOverrides`) and their numbers to the list Questie checks a
  quest log against: so Questie tracks them (no more "missing from Questie's database"), draws their objectives on
  the map and minimap, marks their turn-ins, and puts its "!" over the givers of the quests a character can take
  whenever the giver is there (not over those waiting on a choice, a project's stage or another quest finished
  first beyond the one before it, which Questie can't know). An objective done by speaking with one of the game's
  own creatures takes that creature's places from Questie's own data. Without Questie the add-on does nothing.
  Tested with a stand-in for Questie's database (its functions as Questie-335's source has them), not in the game.

## Files

- `data/sql/chromiecraft/world/brill_home_world.sql`: made by `tools/build_sql.py`; don't edit it.
- `data/sql/chromiecraft/characters/brill_home_characters.sql`: `brill_home` (guid, furniture, last
  rested sleep).
- `tools/build_town.py`, `tools/town/*.py`, `src/BrillTown.cpp`: Brill's questlines (above);
  `data/sql/chromiecraft/world/brill_town_world.sql` is made by it; don't edit it.
- `src/BrillHome.cpp`: the phases, Jamie Nore's menu, the bed, Carolai's menus and keepsakes;
  `.brillhome state`, `.brillhome sleep`, `.brillhome adopt` and `.brillhome use` (the nearest keepsake) for game masters (CI's realm test: `warcraft/server/brill_home.steps`).

## Next

A 5th stable slot for hunters isn't made: the game's stable window has four, and the dog doesn't take
one (it lives outside the stable, out beside them), which is the hunter's one more pet. Jamie Nore may
have more quests later: `warcraft/PLAN.md`.
