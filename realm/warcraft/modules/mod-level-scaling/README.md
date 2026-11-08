# Level scaling (mod-level-scaling)

ChromieCraft's realm. Ascension WoW's level scaling (the user: "Can you bring in ascenscion wow's level
scaling?"), at the user's choices: "Make it so you can talk to your class trainer and turn on or off
scaling. Off by default"; "+-2 your level at all times. Dynamically not set"; and dungeons and raids
scaled to the group's size, as Wrath Remix's.

- **Each character's choice**, off until they turn it on: their own class's trainer has **Level
  scaling is off: ... Turn it on** in their gossip (and **... Turn it off** once it's on). Kept with
  the character (`character_settings`, `mod-level-scaling`).
- **With it on**, every creature near them they could fight (hostile or neutral; not anyone's pet,
  guardian, totem or companion, not a town's people, civilians, critters or unseen triggers) is within
  `LevelScaling.Range` (2) levels of theirs, above or below, out in the world and in dungeons and
  raids; a boss (a dungeon's or raid's, or a world boss) at the top of it. A creature takes its level
  as it appears, and again within 100 yards of them as they level (each a level of the range, which it
  keeps while it's in it; one in a fight keeps its level to the end). Out in the world a creature
  follows the real player nearest it; in a dungeon or raid, the highest of those with it on. Near no
  one with it on (the realm's bots load the world around them too) creatures are their own level, and
  one brought to a level goes back to its own. Its health, mana, armour and melee are its new level's;
  its spells, made for its own level, hit and heal for the new one's. Experience from kills follows
  (a creature within two levels is never grey), and a quest below their level gives the experience of
  one at their level (`LevelScaling.QuestExperience`). Loot, gold and gathering are as they were (3.3.5a
  can't make an item of another level).
- **Dungeons and raids for however many are there** (`LevelScaling.Solo.*`, every character, on or
  off): an instance's share of a full group is its players (the realm's bots count) over the players it
  is made for. Below a full group its creatures' blows land softer (the share's 0.6th power, never
  below 35% of a full group's in a dungeon, 15% in a raid) and the players' harder (the share's
  -0.85th power, at most 15 times): alone in a five-player dungeon you take about two fifths of the
  damage and deal about four times as much. The creatures' health is as it was, so a boss's phases
  still happen. Heals the players give an instance's friendly people go as far as their blows. In
  Icecrown Citadel with less than a third of a group, the three things only a group can do are done for
  them: Blood-Queen Lana'thel's bite passes, Sindragosa's Ice Tombs break by themselves, Valithria
  Dreamwalker mends a little every second. (Wrath Remix's own, `mod-wrath-remix/src/RemixSolo.cpp`.)
- Battlegrounds and arenas, and the crews of ships and zeppelins, are as they are. Wrath Remix has its
  own Northrend at your level (the app's `ctl.sh` turns this module off there).

Settings: `files/etc/modules/mod_level_scaling.conf` (`conf/mod_level_scaling.conf.dist`).

Built from Wrath Remix's level bands and solo scaling (`mod-wrath-remix/src/WrathRemix.cpp`,
`RemixSolo.cpp`). Checked: compiled against AzerothCore's headers. Not yet played.
