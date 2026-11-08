# Quest drops (mod-quest-drops)

The user: "if you are doing a collect quest like go and get me 10 bear asses then the bears will
always drop the item at 100% drop rate rather than you kill 50 bears to get 10 asses"; then: "At ones
that had ridiculously low drop rates, such as less than 25% chance push the drop rate to 75. For 10%
or less set it to 50" (for quest items, in place of the 100%); then, of Decrepit Darkhounds' Darkhound
Blood at 35%: "Quests like that need better drop rates" (every chance under 75% to 75%).

An item a quest asks for (a quest drop: the loot tables' `QuestRequired`) drops, while the quest needs
it, 75% of the time where its chance was under 75%, 50% where it was 10% or less, and as it always did
from 75% up. The core rolls each loot entry's chance; the module's `OnItemRoll` (a `GlobalScript`
hook) changes a quest drop's chance before the roll. Each player who needs the item sees it in the
corpse's loot, as before, and those who don't, don't; the number that drops (the loot table's count)
is unchanged.

An epic or better (purple and up) in a dungeon or raid, or from a rare spawn (rare or rare elite),
rolls ten times its chance, 10% at the least and 100% at the most (the user: "Increase other drop
rates by 10 total so 1% drop rate in rare etc item becomes 10 but 100 stays at 100 but not less than
10"; then: "I only wanted quest items increased and stuff like purple and above for dungeons and rare
spawns"): from a creature's loot or a chest's in a dungeon, and a reference (the roll into another
loot table) where that table can give one. Every other drop keeps the game's own chance: grey, white,
green and blue items, cloth, the world's drops outside dungeons and rares, chests elsewhere, skinning,
mining, herbs, fishing and pickpocketing. No loot table is changed: the module changes a chance as
it's rolled.

Left as they are: drops in a loot group (one item of the group drops, by its chances), where a
higher chance would take from the group's other items. In AzerothCore's base world, of the 5725 quest
drops, 24 are in groups.

Both realms: the app's `ctl.sh` sets `QuestDrops.Enable` (`conf/mod_quest_drops.conf.dist`) to 1 for each
once (the user, for Wrath Remix too: "Yes"); a later 0 is kept.

Game masters: `.questdrops chance <percent>` says what a quest drop, an epic in a dungeon or from a rare,
and any other drop of that chance roll on the realm;
`.questdrops near <entry>` takes you beside the nearest living creature of an entry (300 yards at most).

Tested by the realm test (`scripts/test-warcraft-server.sh`, `warcraft/server/quest_drops.steps`): the
chances 40, 15, 10, 5, 0.5 and 100 roll 40, 75, 50, 50, 50 and 100 for a quest item, 100, 100, 100,
50, 10 and 100 for an epic in a dungeon or from a rare, and their own for any other; and a warlock on Piercing the Veil kills twenty
Rattlecage Skeletons, which drop its skull at 15%: nine skulls at least (at 75% that's missed about
once in a thousand tries, at 15% reached about once in a thousand).
