# mod-forever-quests: WoW: Forever's quests

WoW: Forever's new quests in the old zones, on ChromieCraft's realm only: 123 of Forever's 889 new
quests (ids 86000 and up that the core hasn't), in Forever's own words, with the 91 new people
and creatures they need. Forever's new zones and dungeons aren't here (the user: "don't worry about
the new zone ones").

| | |
| --- | --- |
| Realm | ChromieCraft (`ctl.sh`, `realm_sql`: `data/sql/chromiecraft/world` into `acore_world` alone); Wrath Remix has none of it |
| Ids | Forever's own: quests 86574 to 99158, NPCs 209797 to 276099, items 247826 to 286355; the new NPCs' spawns are guids 8600000 and up |
| Races | Forever's race masks: an Alliance quest is every Alliance race's, the Draenei's, void elves' and Lightforged's included; a race the realm adds goes with the race whose start it takes (the Skyborne of the High Order with the Humans, the Windshapers and Zandalari with the Tauren, the nightborne and blood elves with the Forsaken, the void elves, Lightforged and Draenei with the Night Elves) |

## The new people and creatures

Forever's NPCs that 3.3.5 hasn't stand where Forever has them (QuestieDB's spots on the zone's map,
put on the world by 3.3.5's WorldMapArea; on the ground there, from the server's map files the way
the core reads them, or at the height of the core's own spawns close by where those stand inside a
building), one spot for a quest giver or a named creature, up to 40 for the rest. 3.3.5 has none
of their models, so each is drawn as the core's creature nearest it in kind (the user: "use
whatever model you think"):

- the same type, and family for beasts (Wowhead's tooltip: Beast, Spider; Humanoid);
- for people, someone of the same side (friendly to the Alliance, the Horde or both, by the faction
  and its standing as the core reacts to a player), unless named for the same kind of creature (an
  Abomination);
- the most name words shared ("Dragonmaw Infiltrator" is drawn as a Dragonmaw Raider), a quest
  giver as one of the core's quest givers;
- then the nearest spawn to where it stands, one of the old world's before Outland's and
  Northrend's, the nearest level. Never a holiday's creature, a spirit healer or an invisible
  trigger.

It takes that creature's look, equipment and fighting numbers (and its loot, as its own), under its
own name, title, level and rank (an elite three times its look's health, where that isn't one), and its own side: a quest
giver is on its quests' side where the data has none, a creature to kill or loot is no friend of
the side its quests are for. The table below names each one's look.

## The quests

| Quest | Id | Zone | Side | Level | Notes |
| --- | --- | --- | --- | --- | --- |
| An Alarming Request | 92432 | Alterac Mountains | Alliance | 33 | new quest giver; money estimated, experience estimated; hand-in text made up |
| Friend of the Kirin Tor | 92459 | Alterac Mountains | Alliance | 33 | new quest giver; money estimated, experience estimated; hand-in text made up |
| Shrewd Negotiations | 97287 | Alterac Mountains | Horde | 33 | new quest giver; money estimated, experience estimated; hand-in text made up |
| Shared Fury | 98418 | Ashenvale | Alliance | 30 | new quest giver; money estimated, experience estimated; hand-in text made up |
| Slowing the Orc Advance | 86757 | Ashenvale | Alliance | 32 | hand-in text made up |
| WANTED: Jai'vhanel | 98025 | Darkshore | Alliance | 13 |  |
| Business in Auberdine | 97894 | Darkshore | Alliance | 17 | money estimated, experience estimated |
| Making Do | 97926 | Darkshore | Alliance | 17 |  |
| It's All Fun and Games Until... | 98042 | Darkshore | Alliance | 17 |  |
| Holy Diver | 87760 | Darkshore | Alliance | 20 | money estimated, experience estimated |
| Swelling Forces | 98013 | Darkshore | Alliance | 20 | new quest giver; money estimated |
| Baron Marinous | 98028 | Darkshore | Alliance | 21 |  |
| The Sisterhood of Elune | 98391 | Darnassus | Alliance | 10 | money estimated |
| Carved Centaur Totems | 93224 | Desolace | Alliance | 40 | money estimated, experience estimated; hand-in text made up |
| Buying Friendship: Magram | 94872 | Desolace | Both | 45 | new quest giver; money estimated, experience estimated; hand-in text made up |
| Carved Centaur Totems | 93225 | Desolace | Horde | 40 | money estimated, experience estimated; hand-in text made up |
| Secure the Mountain | 98322 | Dun Morogh | Alliance | 8 | new quest giver; money estimated |
| Dawn in the Mountains | 99158 | Dun Morogh | Alliance | 8 | money estimated |
| Frosthowl | 98326 | Dun Morogh | Alliance | 9 |  |
| Never Saddle on Quality | 95212 | Dun Morogh | Alliance | 10 | money estimated |
| Stolen Blasting Powder | 95213 | Dun Morogh | Alliance | 10 | money estimated |
| Stolen Blasting Powder | 95214 | Dun Morogh | Alliance | 10 | money estimated |
| A Visitor to Dun Morogh | 96408 | Dun Morogh | Alliance | 13 | new quest giver; money estimated |
| Underground Map | 96391 | Dun Morogh | Alliance | 15 | new quest giver |
| Legging It | 96821 | Durotar | Horde | 6 | new creatures |
| Ukor's Lost Pack | 96876 | Durotar | Horde | 8 |  |
| Bloodtalon Matriarch | 97223 | Durotar | Horde | 8 |  |
| A Simmering Storm | 97281 | Durotar | Horde | 11 | money estimated |
| Stormy Potential | 97282 | Durotar | Horde | 11 |  |
| A Missing Hand | 99048 | Durotar | Horde | 11 | new quest giver; money estimated |
| Halikor's Hoof | 96877 | Durotar | Horde | 12 |  |
| Ira's Dagger | 96137 | Duskwood | Alliance | 24 | money estimated; hand-in text made up |
| Merrick's Bow | 96138 | Duskwood | Alliance | 28 | money estimated; hand-in text made up |
| Nibbled-On Book | 91741 | Elwynn Forest | Alliance | 2 |  |
| Rascally Rodents | 91743 | Elwynn Forest | Alliance | 2 |  |
| Book Inventory | 92124 | Elwynn Forest | Alliance | 2 | new quest giver |
| Mining Consultant | 91745 | Elwynn Forest | Alliance | 3 | new quest giver |
| The Big Picture | 91752 | Elwynn Forest | Alliance | 3 | new quest giver |
| Follow That Kobold! | 91758 | Elwynn Forest | Alliance | 4 | new quest giver |
| Delicate Instruments | 91723 | Elwynn Forest | Alliance | 10 | new quest giver |
| Delicate Instruments | 91724 | Elwynn Forest | Alliance | 10 | new quest giver |
| Croaky's Head | 91740 | Elwynn Forest | Alliance | 10 | new quest giver |
| Elmpaw's Head | 91746 | Elwynn Forest | Alliance | 10 |  |
| Hillsbrad's Hoard | 98059 | Hillsbrad Foothills | Alliance | 27 | new quest giver; hand-in text made up |
| Word to Ironforge | 98300 | Ironforge | Alliance | 34 | new quest giver; hand-in text made up |
| For Further Study | 98313 | Ironforge | Both | 32 | money estimated, experience estimated; hand-in text made up |
| Twisting the Knife | 86758 | Loch Modan | Alliance | 16 |  |
| Banner of the Fallen | 86585 | Loch Modan | Alliance | 17 | new quest giver; new creatures |
| Ingredients for the Forge | 86776 | Loch Modan | Alliance | 30 |  |
| Thunderhorn's Report | 98435 | Mulgore | Horde | 10 |  |
| Meal Appeal | 97246 | Orgrimmar | Horde | 15 | new quest giver; money estimated |
| Favorite Food | 97249 | Orgrimmar | Horde | 15 | new quest giver; money estimated |
| Whuut's the Rush | 97275 | Orgrimmar | Horde | 15 |  |
| Show of Force | 98407 | Redridge Mountains | Alliance | 17 | money estimated |
| Wild Eyes | 91920 | Silverpine Forest | Horde | 11 |  |
| Return to Quinn (Again) | 91921 | Silverpine Forest | Horde | 11 | money estimated |
| Arugal's Folly | 98298 | Silverpine Forest | Horde | 16 |  |
| Watching the Roads | 95981 | Silverpine Forest | Horde | 20 |  |
| Stop the Spread | 98299 | Silverpine Forest | Horde | 20 |  |
| Stonetalon Supply Run | 86574 | Stonetalon Mountains | Alliance | 24 | new quest giver; hand-in text made up |
| Bloodfury Trinkets | 86576 | Stonetalon Mountains | Horde | 26 | hand-in text made up |
| Expanding Horizons | 97914 | Stormwind City | Alliance | 17 |  |
| The Shamed Lieutenant | 98219 | Stormwind City | Alliance | 30 | money estimated; hand-in text made up |
| Talk of the Town | 98463 | Stranglethorn Vale | Alliance | 33 | money estimated, experience estimated; hand-in text made up |
| My Little Friends | 93176 | Swamp of Sorrows | Both | 35 | new quest giver; money estimated, experience estimated; hand-in text made up |
| Fang of Githyiss | 97236 | Teldrassil | Alliance | 5 |  |
| Soft Saber Pelts | 87288 | Teldrassil | Alliance | 7 |  |
| The Lost Runner | 99046 | Teldrassil | Alliance | 9 | new quest giver; money estimated |
| Not Dead Yet | 99047 | Teldrassil | Alliance | 9 | new quest giver; money estimated |
| The Great Tree Provides | 99050 | Teldrassil | Alliance | 10 |  |
| Easing Suffering | 99073 | Teldrassil | Alliance | 10 | new quest giver; money estimated |
| Crown of the Earth | 98046 | Teldrassil | Alliance | 11 | money estimated |
| Crown of the Earth | 98065 | Teldrassil | Alliance | 11 | money estimated |
| Darkness in the Glade | 98392 | Teldrassil | Alliance | 12 | money estimated |
| Twisted Hatred | 98403 | Teldrassil | Alliance | 12 | new creatures |
| Chol'aruk the Ravener | 97005 | The Barrens | Alliance | 21 | new quest giver |
| Bruised Pride and Lion Hides | 95494 | The Barrens | Horde | 18 |  |
| The Hermit Tanner | 95495 | The Barrens | Horde | 18 | new quest giver; money estimated |
| Unwelcome Guests | 95508 | The Barrens | Horde | 18 | new quest giver |
| Trouble in the Valley | 95621 | The Barrens | Horde | 18 | new quest giver; money estimated |
| WANTED: Bruuz | 92706 | The Barrens | Horde | 20 |  |
| Her Name Is Olgra | 95774 | The Barrens | Horde | 20 |  |
| Chol'aruk the Ravener | 97003 | The Barrens | Horde | 21 | new quest giver |
| Wrongly Blamed, Justly Corrected | 97250 | The Barrens | Horde | 23 | new creatures |
| Scout Support | 98094 | The Barrens | Horde | 25 | new quest giver; hand-in text made up |
| Valuable Vantages | 98095 | The Barrens | Horde | 25 | new quest giver; hand-in text made up |
| Pristine Pesterhide Pelts | 98155 | Thousand Needles | Alliance | 31 | hand-in text made up |
| Stop the Screeching | 98070 | Thousand Needles | Horde | 31 | hand-in text made up |
| Never Coming Back | 98251 | Thunder Bluff | Horde | 22 | new quest giver; hand-in text made up |
| A Void Path | 98252 | Thunder Bluff | Horde | 22 | new quest giver; money estimated; hand-in text made up |
| Patience | 99141 | Tirisfal Glades | Horde | 6 | money estimated |
| Whispering Horror Residue | 95328 | Tirisfal Glades | Horde | 10 |  |
| As Above, So Below | 99152 | Tirisfal Glades | Horde | 10 | new quest giver; money estimated |
| Hides for the Forsaken | 97558 | Tirisfal Glades | Horde | 11 |  |
| The Argent Emissary | 96895 | Tirisfal Glades | Horde | 13 | new quest giver |
| A Righteous Cause | 96896 | Tirisfal Glades | Horde | 13 | new quest giver; money estimated |
| The Cult of the Damned | 96897 | Tirisfal Glades | Horde | 13 | new quest giver; new creatures; money estimated |
| Remnants of War | 96898 | Tirisfal Glades | Horde | 13 | new quest giver; money estimated |
| Bandarion Keep | 96899 | Tirisfal Glades | Horde | 13 | new quest giver; money estimated |
| Leonid's Letter | 98545 | Tirisfal Glades | Horde | 13 | new quest giver |
| Rear Guard Patrol | 99156 | Tirisfal Glades | Horde | 13 |  |
| Prompt Potion Runner | 97891 | Undercity | Horde | 16 |  |
| Unending Torment | 97290 | Undercity | Horde | 21 | new quest giver |
| Thundering Hearts | 97985 | Undercity | Horde | 33 | new quest giver; hand-in text made up |
| Murloc Gills | 92744 | Westfall | Alliance | 12 | new quest giver |
| Harvesting the Harvesters | 92909 | Westfall | Alliance | 15 | new quest giver |
| A Lack of Virtue | 98459 | Wetlands | Alliance | 21 | new quest giver; money estimated |
| Unrequited Love | 98461 | Wetlands | Alliance | 21 |  |
| Alchemical Hazards | 98282 | Wetlands | Alliance | 22 | hand-in text made up |
| Return the Statuette | 98189 | Wetlands | Alliance | 25 | money estimated; hand-in text made up |
| This Land Was Their Land | 98230 | Wetlands | Alliance | 29 | new quest giver; money estimated, experience estimated; hand-in text made up |
| Crimson Crate Delivery | 98240 | Wetlands | Alliance | 29 | new quest giver; hand-in text made up |
| Razormaw Needling | 98245 | Wetlands | Alliance | 29 | new quest giver; money estimated; hand-in text made up |
| Death to the Dragonmaw | 98291 | Wetlands | Alliance | 30 | new quest giver; new creatures; money estimated, experience estimated; hand-in text made up |
| Understanding Our Present | 98216 | Wetlands | Alliance | 31 | hand-in text made up |
| Spark of Freedom | 87491 | Wetlands | Alliance | 32 | new quest giver; hand-in text made up |
| Gleaning Our Future | 98310 | Wetlands | Alliance | 32 | hand-in text made up |
| Sentiments of the Lost | 88758 | Wetlands | Alliance | 33 | new quest giver; hand-in text made up |
| Stopping the Cycle | 98297 | Wetlands | Alliance | 34 | new quest giver; new creatures; hand-in text made up |
| Crocs of the Sky | 98072 | Wetlands | Both | 27 | money estimated; hand-in text made up |
| Bloom of the Heavens | 98209 | Wetlands | Both | 29 | new quest giver; hand-in text made up |
| Carnage | 98283 | Wetlands | Both | 30 | hand-in text made up |
| Hearts of the Lost | 87318 | Wetlands | Both | 33 | new quest giver; money estimated, experience estimated; hand-in text made up |

## The new people and creatures

Each drawn as the 3.3.5 creature named (its look and equipment, and its fighting numbers), under its own name, level, rank and side.

| Forever's | Id | Drawn as |
| --- | --- | --- |
| Bruuz | 209797 | Hecklefang Hyena (4127) |
| Amaryllis Webb | 217412 | Baker Masterson (11287) |
| Maseara Autumnmoon | 221269 | Loh'atu (11548) |
| Hilda the Breaker | 246389 | Deathguard Randolph (1736) |
| Kelsey Fargo | 247226 | Brother Neals (952) |
| Daniel | 247229 | Brother Neals (952) |
| Emissary Jacques | 247264 | Lieutenant Farren Orinelle (2228) |
| Hamish Bergwort | 248242 | Theocritus (313) |
| Merell Ross | 248277 | Watcher Callahan (2142) |
| Croaky | 248278 | Murloc Forager (46) |
| Elmpaw | 248299 | Young Forest Bear (822) |
| Shinyfinder Narf | 248362 | Kobold Laborer (80) |
| Tordrin Sternblade | 248415 | Jorik Kerridan (915) |
| Deathguard Kristof | 251001 | Deathguard Elite (7980) |
| Captain McManus | 251493 | Captain Armando Ossex (16392) |
| Archmage Celindra | 252085 | Archmage Ansirem Runeweaver (2543) |
| Alba Fairmoon | 253092 | Scout Galiaan (878) |
| Gorhak | 253139 | Warug (5398) |
| Ozwin Ironsprocket | 253395 | Farmer Saldean (233) |
| Tom "Half-fish" Wilson | 254078 | Raleigh the Devout (3980) |
| Elder Snow Leopard | 260157 | Snow Leopard (1201) |
| Whispering Horror | 260396 | Bleeding Horror (1529) |
| Shadowvale Lurcher | 260428 | Rot Hide Gladerunner (1772) |
| Shadowvale Mystic | 260430 | Rot Hide Mystic (1773) |
| Shadowvale Mystic | 260432 | Rot Hide Mystic (1773) |
| Walton | 261366 | Kadrak (8582) |
| Corporal Adamore | 262119 | Witchwing Windcaller (3280) |
| Earthseer Farsen | 264936 | Foreman Stonebrow (1254) |
| Ridgeshade Lurker | 266849 | Webwood Lurker (1998) |
| Ridgeshade Creeper | 266850 | Deepmoss Creeper (4005) |
| Ukorsbane | 266851 | Webwood Venomfang (1999) |
| Halikor | 266852 | Thunder Lizard (3130) |
| Dark Neophyte | 267006 | Dark Cleric Beryl (2129) |
| Leonid Barthalomew the Revered | 267008 | Leonid Barthalomew the Revered (11036) |
| Hadric Harlson | 267009 | Kaal Soulreaper (4563) |
| Va'xug Firefure | 267214 | Braug Dimspirit (4489) |
| Chol'aruk | 267307 | Kreenig Snarlsnout (3438) |
| Bainham | 267309 | Takar the Seer (6244) |
| Gur'ak | 267310 | Thork (3429) |
| Bloodtalon Matriarch | 268530 | Bloodtalon Taillasher (3122) |
| Encroaching Soldier | 268622 | Bael'dun Soldier (3376) |
| Outraged Pillager | 268623 | Razormane Pathfinder (3456) |
| Razormane Raider | 268624 | Bristleback Hunter (3258) |
| Migi | 268682 | Searn Firewarder (5892) |
| Thatog | 268701 | Sana (3319) |
| Night Elf Courier | 268925 | Veenix (4086) |
| Image of Archmage Modera | 269127 | Archmage Cedric (18165) |
| Mountaineer Ylva | 269153 | Mountaineer Gravelgaw (1091) |
| Headsplitter | 269185 | Stonesplinter Skullthumper (1163) |
| Calder Gray | 270038 | Master Apothecary Faranell (2055) |
| Stormheart | 270094 | Needles Cougar (4124) |
| Jai'vhanel | 270196 | Ironbeak Hunter (7099) |
| Arbal | 270269 | Onu (3616) |
| Baron Marinous | 270294 | Irontree Stomper (7139) |
| Deathstalker Masoj | 270438 | Deathstalker Lesh (2214) |
| Howin Kindfeather | 270637 | Howin Kindfeather (11810) |
| Daggerfang | 270693 | Loch Crocolisk (1693) |
| Sylessa Duskwhisper | 270844 | James Halloran (2094) |
| Goaz Warder | 270892 | Mirelow (14424) |
| Eye of Kilrogg | 271181 | Braug Dimspirit (4489) |
| Essene Villard | 271322 | Comar Villard (5683) |
| Maddened Rotclaw | 271334 | Elder Gray Bear (2356) |
| Carnage | 271336 | Elder Razormaw (1019) |
| Ados | 271338 | Fen Dweller (1039) |
| Dragonmaw Infiltrator | 271346 | Dragonmaw Raider (1034) |
| Dragonmaw Soulbinder | 271348 | Dragonmaw Raider (1034) |
| Dragonmaw Reclaimer | 271351 | Dragonmaw Raider (1034) |
| Subdued Dragonspawn | 271373 | Red Dragonspawn (1045) |
| Neru | 271458 | Fen Creeper (1040) |
| Modr | 271460 | Fen Creeper (1040) |
| Golm | 271462 | Fen Dweller (1039) |
| Captive Fire Elemental | 271481 | Rethiel the Greenwarden (1244) |
| Mountaineer Gretchen | 271546 | Mountaineer Dolf (12427) |
| Frosthowl | 271587 | Edan the Howler (1137) |
| Unfinished Abomination | 271613 | Terrifying Abomination (31098) |
| Stormscale Beastmistress | 271903 | Stormscale Myrmidon (2181) |
| Hatescreech | 272034 | Bloodfeather Sorceress (2018) |
| Windmistress Gaedress | 272044 | Bloodfeather Rogue (2017) |
| Witchmother Arysa | 272046 | Bloodfeather Matriarch (2021) |
| Befouled Webwood | 272096 | Webwood Lurker (1998) |
| Xethorr the Wicked | 272116 | Vicious Grell (2005) |
| Lost Stalker | 272260 | Skeletal Horror (202) |
| Lost Watcher | 272273 | Skeletal Horror (202) |
| Glix Xizzix | 272526 | Auctioneer Stockton (15675) |
| Dark Enforcer | 275437 | Dark Cleric Beryl (2129) |
| Heglan Shadeeye | 275657 | Ophek (3294) |
| Sentinel Eralya Leafshadow | 275683 | Sentinel Arynia Cloudsbreak (3519) |
| Lasher Sproutling | 275703 | Timberling Bark Ripper (2025) |
| Blooming Lasher | 275708 | Timberling Trampler (2027) |
| Riptear | 276020 | Wandering Spirit (1532) |
| Wrathvine | 276099 | Timberling Bark Ripper (2025) |

"Money estimated": Wowhead's data has no rewards for the quest (no money or experience), so its
money is the median of what the core's quests of the same level and experience pay.
"Experience estimated": wow4ever.quest hasn't it either, so it's the 3.3.5 step for a quest of its
kind (a delivery 2, a quest with objectives 5). "Hand-in text made up": Wowhead's data has none, so
it's "Hand in the quest." (the user: "just make something simple up").

## Where everything comes from

- **Which quests, who gives and ends them, objectives, item sources, prerequisites, races, levels,
  the new NPCs' spots**: [QuestieDB](https://github.com/Questie/QuestieDB)'s Forever database
  (`data/Forever` and its Forever corrections: the generated delta-base, traces and authored fixes,
  in its own order), read as data by `tools/lualit.py` and `tools/questiedb.py` (no Lua is run).
- **The words, objectives' counts, rewards, money, experience, reputation**: each quest's page on
  [foreverchanges.pro](https://foreverchanges.pro/quests) (Wowhead's Forever database as the site
  shows it; beta client 1.60.1.70532), read by `tools/foreverchanges.py`. Wowhead itself turns
  away scripted reading of its pages. Quest text © Blizzard Entertainment.
- **Experience the page hasn't**: wow4ever.quest's pages (`data/forever/experience.json`).
- **The new NPCs' type, family and rank, the new rewards' stats, damage, armor and effects**:
  Wowhead's tooltips (`tools/wowhead.py`); the rewards' class, slot, binding, prices and levels:
  the Forever client's Item and ItemSparse tables (wago.tools). Equip lines 3.3.5 can carry as a
  stat (spell damage and healing is 3.3.5's spell power) are stats; the others (Forever's "+2%
  movement speed in Silverpine") aren't kept. A reward whose use is a spell 3.3.5 hasn't (Forever's
  profession books) isn't given (`report.json`, `rewards_left_out`).
- **Looks of the new items**: the 3.3.5 item display with the same icon (ItemDisplayInfo.dbc), the
  one the core's items of the same slot use first; a quest item whose icon 3.3.5 hasn't looks like
  the core's quest item with the nearest name.
- **Drop chances**: not in any source. A quest item drops at 60% from one or two kinds of creature
  and 35% from more; an item that starts a quest drops for anyone who hasn't taken it, always from
  a single creature, 8% from several.
- **What a friendly person "drops"**: QuestieDB lists an item handed over as a drop (Patience's
  reports from Deathguard Dillinger, Deathguard Kristof and Gordo); they can't be killed for it, so
  it's asked of them: "I'm here for your report." in their menu while the quest is in the log and
  the item isn't in the bags (the option's conditions; their SmartAI hands it over).
- **A new person the data gives no side**: drawn as one of a side's own (a guard) and no quest's to
  kill, they're that side's, as they look: Deathguard Kristof at the waystation on the Undercity
  road is the Deathguard's (his look's, level 55), not a monster.

## What isn't here, and why

`data/forever/report.json` lists every other new quest with its reasons. In short:

- **New zones and dungeons**: Zephras Isle, Shen'dralas, Riverglades, the Darkspear Islands, the
  Hall of Thanes, the Ruins of Lordaeron, Excavation Site: Wetlands, the City of Dalaran.
- **Items no creature drops in the data** (from objects, from people's hands, from what QuestieDB
  hasn't recorded), quests whose ender or starter the data lacks, people with no spot in the old
  zones in the data (QuestieDB holds back the new spawns in Redridge, the Eastern Plaguelands,
  Mulgore and Stormwind, whose maps Forever redrew).
- **Scripts**: places to explore, spells to cast, objects to use, kill credit, events, duels.
- **Class quests** (3.3.5's class training has its own), **Crafting** (Craftsman's Writs),
  **Camping** (Forever's profession), Forever's fishing contest, holidays and invasions.

## How it's made

    python3 tools/forever.py import QUESTIEDB_DIR WORLD_SQL_DIR SERVER_DATA_DIR CACHE_DIR
    python3 tools/forever.py build SERVER_DATA_DIR WORLD_SQL_DIR

`import` picks the quests and writes `data/forever/quests.json` and `report.json` (fetching the
quests' pages, the tooltips and the client's tables into CACHE_DIR, kept between runs); `build`
writes `data/sql/chromiecraft/world/forever_quests.sql` (quests, their givers and enders, the new
NPCs, their looks and spawns, items, drops; safe to run again). WORLD_SQL_DIR: the core's
`data/sql/base/db_world` at the realm's commit (`warcraft/server-version.env`); SERVER_DATA_DIR:
the server data's `dbc` and `maps` (`warcraft/server-data.env`). Both outputs are committed.

## Tests

- `tools/test_forever.py` (CI): the page reader on a stand-in page; the tooltip reader on stand-in
  tooltips; the races each Forever race mask opens; the committed SQL against its data (each
  quest's words, a giver, an ender, every new item it names made, every new NPC drawn and
  standing somewhere).
- Checked here: the SQL in MariaDB 10.11 on the core's base world tables, applied twice; there,
  every quest's giver, ender and creature to kill stands somewhere, every item to collect drops
  from something, every new NPC has a look. The height reader against the core's own spawns: 79%
  within a yard of the ground it gives (the rest stand in buildings, caves and water).
- CI's server test: all the quests and new NPCs in ChromieCraft's world, none in Remix's, and not
  a word from the world server about any of them.
- Not checked: playing them; how the new NPCs look and stand in the game.
