-- Moratari's part in the war (STORY.md, "Moratari in the war"), written by tools/story.py from the
-- story_*.py files and romance.py: edit those and run it again. Her words on the game's quests, where
-- she walks with the Timerunner, what can be said to her and to the war's own people, the
-- interventions before the turn and their undoing after it, and the romance (RemixMoratari.cpp,
-- RemixOutings.cpp). This file owns: creatures 770500-770999, spawns 7704330-7704399, NPC texts
-- 7702600-7702999, its quests, the conditions on the quests it gates, the texts it changes, the gossip
-- flag of the game's creatures it gives something to say, the unit flags of those it spares.

DROP TABLE IF EXISTS `remix_quest_whisper`;
CREATE TABLE `remix_quest_whisper` (
  `quest` INT UNSIGNED NOT NULL,
  `moment` TINYINT UNSIGNED NOT NULL,             -- 1 taken, 2 its objectives done, 3 turned in
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,     -- 0 both, 1 Alliance, 2 Horde
  `seq` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `speaker` INT UNSIGNED NOT NULL DEFAULT 770001,
  `delay_ms` INT UNSIGNED NOT NULL DEFAULT 3000,  -- after the line before it
  `after_quest` INT UNSIGNED NOT NULL DEFAULT 0,  -- said only once this is turned in
  `before_quest` INT UNSIGNED NOT NULL DEFAULT 0, -- said only until this is turned in
  `races` INT UNSIGNED NOT NULL DEFAULT 0,        -- a race mask (0: any)
  `text` TEXT NOT NULL,
  PRIMARY KEY (`quest`, `moment`, `side`, `seq`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_companion`;
CREATE TABLE `remix_companion` (
  `id` INT UNSIGNED NOT NULL,
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `zone` INT UNSIGNED NOT NULL DEFAULT 0,          -- 0: anywhere
  `from_quest` INT UNSIGNED NOT NULL DEFAULT 0,    -- turned in (0: from the start)
  `until_quest` INT UNSIGNED NOT NULL DEFAULT 0,   -- turned in ends it (0: never)
  `during_quest` INT UNSIGNED NOT NULL DEFAULT 0,  -- in the log (0: any time)
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_place`;
CREATE TABLE `remix_place` (
  `quest` INT UNSIGNED NOT NULL,
  `credit` INT UNSIGNED NOT NULL,                  -- given as they come within the radius
  `map` INT UNSIGNED NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `radius` FLOAT NOT NULL DEFAULT 20,
  `scene` INT UNSIGNED NOT NULL DEFAULT 0,         -- played there instead (its end gives the credit)
  `text` TEXT NOT NULL,                            -- Moratari's words there ('' for none)
  PRIMARY KEY (`quest`, `credit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_outing`;
CREATE TABLE `remix_outing` (
  `id` INT UNSIGNED NOT NULL,
  `map` INT UNSIGNED NOT NULL,
  `x` FLOAT NOT NULL, `y` FLOAT NOT NULL, `z` FLOAT NOT NULL, `o` FLOAT NOT NULL,
  `scene` INT UNSIGNED NOT NULL DEFAULT 0,          -- played there (remix_scene)
  `private` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- in a phase of its own
  `undress` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- the Timerunner's gear unseen while it lasts
  `back` TINYINT UNSIGNED NOT NULL DEFAULT 1,       -- back where they were after
  `flight_from` INT UNSIGNED NOT NULL DEFAULT 0,    -- a flight on her: from this flight point (at x y z)
  `flight_to` INT UNSIGNED NOT NULL DEFAULT 0,
  `mount` INT UNSIGNED NOT NULL DEFAULT 0,          -- her shape under them
  `name` VARCHAR(120) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_outing_line`;
CREATE TABLE `remix_outing_line` (
  `outing` INT UNSIGNED NOT NULL,
  `at_ms` INT UNSIGNED NOT NULL,                    -- after the flight starts
  `text` TEXT NOT NULL,
  PRIMARY KEY (`outing`, `at_ms`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_look`;
CREATE TABLE `remix_look` (
  `display` INT UNSIGNED NOT NULL,                  -- the new look (CreatureDisplayInfo)
  `from_display` INT UNSIGNED NOT NULL,             -- copied from
  `extra` INT UNSIGNED NOT NULL,                    -- its clothes (CreatureDisplayInfoExtra)
  `from_extra` INT UNSIGNED NOT NULL,               -- copied from
  `bake` TINYINT UNSIGNED NOT NULL DEFAULT 0,       -- keep the copied look's baked texture (0: dressed from its items)
  `item1` INT UNSIGNED NOT NULL DEFAULT 0, `item2` INT UNSIGNED NOT NULL DEFAULT 0, `item3` INT UNSIGNED NOT NULL DEFAULT 0,
  `item4` INT UNSIGNED NOT NULL DEFAULT 0, `item5` INT UNSIGNED NOT NULL DEFAULT 0, `item6` INT UNSIGNED NOT NULL DEFAULT 0,
  `item7` INT UNSIGNED NOT NULL DEFAULT 0, `item8` INT UNSIGNED NOT NULL DEFAULT 0, `item9` INT UNSIGNED NOT NULL DEFAULT 0,
  `item10` INT UNSIGNED NOT NULL DEFAULT 0, `item11` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`display`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_talk`;
CREATE TABLE `remix_talk` (
  `id` INT UNSIGNED NOT NULL,
  `npc` INT UNSIGNED NOT NULL,                     -- the creature it's said to
  `parent` INT UNSIGNED NOT NULL DEFAULT 0,        -- 0: in its first menu; else after that entry's reply
  `ord` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `races` INT UNSIGNED NOT NULL DEFAULT 0,
  `gender` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- 0 any, 1 male, 2 female
  `quest` INT UNSIGNED NOT NULL DEFAULT 0,         -- only while this is in the log, unfinished
  `after_quest` INT UNSIGNED NOT NULL DEFAULT 0,
  `before_quest` INT UNSIGNED NOT NULL DEFAULT 0,
  `icon` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `option_text` VARCHAR(255) NOT NULL,
  `reply` INT UNSIGNED NOT NULL DEFAULT 0,         -- npc_text (0: the menu closes)
  `credit` INT UNSIGNED NOT NULL DEFAULT 0,        -- a quest's credit, given as it's said
  `action` TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- 1 scene [param], 2 close, 3 she waits, 4 she comes, 5 outing [param]
  `param` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `remix_companion` (`id`, `side`, `zone`, `from_quest`, `until_quest`, `during_quest`, `comment`) VALUES
(1, 1, 3537, 77014, 77121, 0, 'Chapter I: the Borean Tundra, while the Timerunner finds their feet'),
(2, 2, 3537, 77015, 77122, 0, 'Chapter I: the Borean Tundra, while the Timerunner finds their feet'),
(3, 0, 0, 77908, 77802, 0, 'After her tent: everywhere, until they go home');

INSERT INTO `remix_place` (`quest`, `credit`, `map`, `x`, `y`, `radius`, `scene`, `text`) VALUES
(77042, 770532, 571, 2332.0, 5470.0, 14.0, 101, 'Here. Under the dune. Put your ear to the sand.');

INSERT INTO `remix_quest_whisper` (`quest`, `moment`, `side`, `seq`, `speaker`, `delay_ms`, `after_quest`, `before_quest`, `races`, `text`) VALUES
(77014, 3, 1, 1, 770001, 3000, 0, 0, 0, 'Valiance Keep. The fleet came in three days ago, and the Scourge has tested the walls every night since. You remember the smell of this place, I imagine: tar, salt, and far too many soldiers in one harbor.'),
(77014, 3, 1, 2, 770001, 7000, 0, 0, 0, 'I will walk with you while you find your feet. If you would rather I waited somewhere, say so.'),
(77015, 3, 2, 1, 770001, 3000, 0, 0, 0, 'Warsong Hold. Garrosh''s fortress, built over tunnels that are already full of nerubians, though no one inside knows it yet. Well. Almost no one.'),
(77015, 3, 2, 2, 770001, 7000, 0, 0, 0, 'I will walk with you while you find your feet. If you would rather I waited somewhere, say so.'),
(11672, 1, 1, 1, 770001, 3000, 0, 0, 0, 'He has heard about Outland. Best not to mention the rest; he has nowhere to write it down.'),
(11672, 3, 1, 1, 770001, 5000, 0, 0, 0, 'Look at the general''s eyes when his counselor speaks. I will tell you why when no one is listening.'),
(77041, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Scouts, $N. Not visions, not dreams, and certainly not ''a dragon told me''.'),
(77041, 2, 1, 1, 770001, 3000, 0, 0, 0, 'Did you see him look at his counselor before he answered you? Every day he looks a little sooner.'),
(11727, 1, 1, 1, 770001, 3000, 0, 0, 0, 'The keep does not fall, as it happens. It only comes close, three times. Let us make it two.'),
(11727, 3, 1, 1, 770001, 3000, 0, 0, 0, 'Wasn''t her, she says. She lies worse than you do, $N.'),
(11797, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Crypt crawlers. They were nerubians once, citizens of Azjol-Nerub, until the Lich King took their kingdom and kept its dead. Be quick with them. It is the only mercy anyone can give them now.'),
(11797, 3, 1, 1, 770001, 3000, 0, 0, 0, 'Twenty years, and he has never seen a day like it. He will call it luck. Soldiers always do.'),
(11889, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Fishing nets, against flying nerubians. It should not work. It does, and I have never understood why.'),
(11889, 3, 1, 1, 770001, 3000, 0, 0, 0, 'He wants them to come by sea next, for the beating of their lives. I have given up arguing with dwarves about details.'),
(11897, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Two sinkholes in Hammerhill''s orders. Three in Eternus''s notes. Four in the ground. Collapse his two and report to him; leave the rest to us.'),
(11897, 2, 1, 1, 770001, 3000, 0, 0, 0, 'Those cultists chanting by the northern sinkhole: mark where they stand. We will be back for them.'),
(77042, 1, 1, 1, 770001, 3000, 0, 0, 0, 'The necrolytes first. I have always wondered who they think is listening.'),
(77019, 3, 1, 1, 770001, 3000, 0, 0, 0, 'Of everyone in this keep, she is the one I most wanted to meet.'),
(11927, 3, 1, 1, 770001, 3000, 0, 0, 0, 'Before she asks you anything: a word with me, $N. Now, please.'),
(77043, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Go on. She is waiting, and so is William.'),
(77043, 2, 1, 1, 770001, 3000, 0, 0, 0, 'Alive. I was not at all sure we would be in time.'),
(11599, 1, 1, 1, 770001, 3000, 0, 0, 0, 'The mine is north of the keep, past the Farshire fields. Run, $N.'),
(77044, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Colburn will want a bottle of Kul Tiras wine before he talks. Ask him anyway. It has been years since anyone wanted to hear what he knows.'),
(77044, 2, 1, 1, 770001, 3000, 0, 0, 0, 'The counselor''s hand. I know what you want to do, $N, and you cannot. If he falls in this keep, he does not fall where history needs him to.'),
(77006, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Venn''s men have not heard a friendly voice since they landed. They will be glad of yours.'),
(77045, 1, 1, 1, 770001, 3000, 0, 0, 0, 'They have been kneeling in the cold for days. Do not expect them to run.'),
(77045, 2, 1, 1, 770001, 3000, 0, 0, 0, 'Four. History said none. Let it argue.'),
(12088, 1, 1, 1, 770001, 3000, 0, 0, 0, 'When the Scarlet Crusade took Koltira Deathweaver, Orbaz would have left him to them. Thassarian would not: ''In death we are brothers.'' Now think what he will do for his sister.'),
(12088, 3, 1, 1, 770001, 3000, 0, 0, 0, 'He has not seen her in years. Give him a moment, and then talk to me.'),
(77046, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Leryssa first; the vindicator is at the far end of the inn. Hold on.'),
(11956, 1, 1, 1, 770001, 3000, 0, 0, 0, 'A lich who hides his soul in the ice and thinks no one will look. Liches are so predictable.'),
(11938, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Hammerhill''s volunteers are holding the ziggurat while you are away. Thassarian would rather not find out whether he could hold it alone. Now he never has to.'),
(11942, 1, 1, 1, 770001, 3000, 0, 0, 0, 'I know all three words, and you will still have to fetch the scrolls. Thassarian would want to know where you learned them.'),
(12019, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Leryssa is gone from the inn. The general''s own escort came for her under his seal, and she went with them like a sleepwalker; Yaala could not hold a woman who wanted to go. I am sorry, $N. Some threads are knots.'),
(12019, 3, 1, 1, 770001, 3000, 0, 0, 0, 'He knelt up there with his offerings, the general and Leryssa, and that is the only reason anyone ever saw the face under Talbot''s. History needed her on that tower. I hate that it held.'),
(12019, 3, 1, 2, 770001, 9000, 0, 0, 0, 'He will be back, you know. In the Citadel, at the very end, with the other princes: ''Naxxanar was merely a setback.'' You will enjoy proving him wrong a second time.'),
(77047, 3, 1, 1, 770001, 60000, 0, 0, 0, 'Two regiments of draenei, a general who thinks his own thoughts, and four of Unit S who will see their mothers again. I have kept the record of this week for a very long time, $N. I like this version better.'),
(11585, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Garrosh holds court at the war map, in the heart of the hold. Do not expect him to welcome you.'),
(11585, 3, 2, 1, 770001, 6000, 0, 0, 0, 'He and Saurfang have the same argument at that map every few minutes: shipping lanes, supplies, and then Garrosh''s boot comes down. I could recite it for you.'),
(77050, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Garrosh and Saurfang first. Then the captain, up on the battlements of the south wall.'),
(77050, 2, 2, 1, 770001, 3000, 0, 0, 0, 'That is all three. I wonder which of them will still remember your face when this war is over.'),
(11596, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Saurfang drank the same blood Grom did, and lived to remember everything it made him do. Garrosh only knows the songs.'),
(11598, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Some of the cocoons in the quarry hold Warsong soldiers, still alive. Cut them free and they will fight beside you.'),
(11598, 3, 2, 1, 770001, 3000, 0, 0, 0, 'Razgor is right: more will come. Next time, from underneath.'),
(77051, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Holgoth is a few steps away, past Razgor''s hut.'),
(11606, 1, 2, 1, 770001, 3000, 0, 0, 0, 'The crates are scattered across the quarry floor. Gather them quickly; the nerubians will not leave you alone down there for long.'),
(11608, 1, 2, 1, 770001, 3000, 0, 0, 0, 'When the last charge goes off, listen. You will hear the tunnels collapse, all the way back under the hold.'),
(11608, 3, 2, 1, 770001, 3000, 0, 0, 0, 'In your war, the nerubians were inside the hold by now. Tonight it sleeps on solid stone, and will never know how close it came.'),
(11602, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Twenty to an egg, Razgor says. I counted once. He is being modest.'),
(11634, 1, 2, 1, 770001, 3000, 0, 0, 0, 'From the top of the hold you can see what Razgor keeps pointing at.'),
(11636, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Yanni will quote you his odds. Pay them no mind. I will be at the coast when you land.'),
(11642, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Mobu is down by the tanks. Be gentle with him; he has wanted to go home since the day he got here.'),
(11642, 3, 2, 1, 770001, 4000, 0, 0, 0, 'He is about to send you for a transjigamarig and ten metal plates. I know where every one of them is. Come, we can be back before he has finished complaining.'),
(11643, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Into the mist, then. Take heart: the Kvaldir see no better in it than you do.'),
(11651, 3, 2, 1, 770001, 3000, 0, 0, 0, 'Before the tanks roll, $N, there is one more thing this beach needs.'),
(77054, 1, 2, 1, 770001, 3000, 0, 0, 0, 'The Mist Lords keep to the thickest of the mist, on the landing itself. As for Gorge, let him shout. He will come around.'),
(11652, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Three seats in that tank for the wounded. Fill them, $N. Whoever the Scourge reach first, they stitch into something else and send back at the Horde.'),
(11652, 3, 2, 1, 770001, 3000, 0, 0, 0, '''Underestimated.'' From Garrosh Hellscream, that is very nearly an apology. Do not wait for a second one.'),
(77056, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Saurfang is just there, at Garrosh''s shoulder. Stand where he can see you.'),
(77056, 3, 2, 1, 770001, 50000, 0, 0, 0, 'All the other times I have heard him say that, his boot came down on the map. Remember this afternoon, $N. It does not last.'),
(12235, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Wintergarde. You have seen it once already, the morning I showed you. Now you see it from the walls.'),
(12237, 1, 1, 1, 770001, 3000, 0, 0, 0, '''I picked a bad day to stop drinking!'' Someone says it every time. Not always the same someone.'),
(12237, 3, 1, 1, 770001, 4000, 0, 0, 0, 'Wanting is not mending. Look at the beam above the gryphons, $N. Find me at the crypt before you go back to the High Commander.'),
(77223, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Lynore is with the High Commander. Leoric is up the hill with the gnome engineer, and Urik is at the roost, where you left him.'),
(12253, 1, 1, 1, 770001, 3000, 0, 0, 0, 'The geists in that square were Wintergarde''s own people, not long ago. They do not know they are hunting their neighbors. Bring out whoever you can.'),
(12309, 3, 1, 1, 770001, 3000, 0, 0, 0, 'Necrolord Amarion is at the bottom of that crypt, raising the nobles buried there. Left alone, he has days down there, and days are a long time in a crypt. Go now.'),
(12311, 1, 1, 1, 770001, 3000, 0, 0, 0, 'The shadow beside the necrolord is Thel''zan''s; the Duskbringer himself keeps to the mausoleum. That fight comes later. You will win it.'),
(12311, 3, 1, 1, 770001, 5000, 0, 0, 0, 'A company to Fordragon Hold. The way history went, Wintergarde never spared Bolvar a single blade. This time he will have a hundred more at his back.'),
(12034, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Agmar speaks for Hellscream here, and his Kor''kron listen for anyone who doesn''t.'),
(77236, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Torvus is the orc by the burning brazier, waiting for nobody in particular.'),
(12036, 1, 2, 1, 770001, 3000, 0, 0, 0, 'The Pit of Narjun opens onto Azjol-Nerub. The nerubian at its edge is Kilix: not everything down there serves the Lich King. One day he will ask you to kill Anub''arak for him. Try to look as if it is the first time.'),
(77234, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Icemist is west, at the foot of the mountains. Look for the cultists with their hands raised to the beasts overhead.'),
(77234, 3, 2, 1, 770001, 4000, 0, 0, 0, 'Malefious is a Grand Apothecary, as Putress is. That proves nothing about him. Watch what you carry for him all the same.'),
(12189, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Venomspite is on the far eastern edge of the Dragonblight. Middleton runs the blight works there; you will know him by how pleased he is with himself.'),
(12188, 1, 2, 1, 770001, 3000, 0, 0, 0, 'The specters on that beach were Prince Arthas''s men, the ones he stranded when he burned his ships. They have waited a long time for someone to come for them. I doubt this is what they hoped for.'),
(12200, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Middleton has never watched a dragon die. I have. Take the tears, and do not make a joke of it.'),
(12218, 1, 2, 1, 770001, 3000, 0, 0, 0, 'The dead you will be testing it on came out of Wintergarde''s mausoleum. Somebody in that keep buried every one of them.'),
(77235, 1, 2, 1, 770001, 3000, 0, 0, 0, 'Molder is across the yard, by the alchemists. Lawrence is the one with the ledger, among the braziers near Middleton.'),
(12221, 3, 2, 1, 770001, 4000, 0, 0, 0, 'So Eternus has her vial. Whatever she learns from it, you and I already know what it does. We saw the Wrathgate after.'),
(12470, 1, 0, 1, 770001, 3000, 0, 0, 0, 'The storm keeps her out as well as me. Something in common at last. I will wait at its edge, $N.'),
(12470, 2, 0, 1, 770001, 3000, 0, 0, 0, 'The hourglass answered her question, $N. It will be years before she believes the answer. It took me longer.'),
(12470, 3, 0, 1, 770001, 16000, 0, 0, 0, 'The Lord of Time was shown his own ending, long ago, and he has spent ages refusing it. If he may refuse one, Eternus says, so may we.'),
(77204, 1, 0, 1, 770001, 3000, 0, 0, 0, 'Mind the ambassadors on that platform, $N. Dragons listen better than they pretend to.'),
(77218, 1, 2, 1, 770001, 3000, 77236, 0, 0, 'Your note to Varok never left Agmar''s Hammer. The Kor''kron searched Torvus before he could go, and Agmar burned what they found. I went and looked, $N. I was glad. I am not proud of it.'),
(77048, 1, 1, 1, 770001, 3000, 0, 0, 0, 'The mine. He has moved his cot down to the bottom level, where the light is worse and the knives have further to climb.'),
(77049, 1, 1, 1, 770001, 3000, 0, 0, 0, 'Death''s Stand. Venn has kept them there a week, waiting for orders nobody was ever going to send.'),
(77230, 1, 2, 1, 770001, 3000, 0, 0, 0, 'The coast. Gorge is by the tanks; he always is.'),
(13242, 3, 2, 1, 770001, 24000, 77207, 0, 0, 'And there goes the patience he learned. History needs him angry, $N. I wish it needed something else.'),
(77901, 1, 0, 1, 770001, 3000, 0, 0, 0, 'Sit. Here, out of the wind.'),
(77902, 1, 0, 1, 770001, 3000, 0, 0, 0, 'One drink. I will hold you to one. You may hold me to two.'),
(77903, 1, 0, 1, 770001, 3000, 0, 0, 0, 'Do not look at the dress yet. Look when we get there. I want to see your face.'),
(77904, 1, 0, 1, 770001, 3000, 0, 0, 0, 'At night the Accord sleeps on the lower tiers. The top is only wind.'),
(77906, 1, 0, 1, 770001, 3000, 0, 0, 0, 'Eat something light first, and tie down anything you would like to keep.'),
(77907, 1, 0, 1, 770001, 3000, 0, 0, 0, 'Leave the map in your pack today. We are getting lost on purpose.'),
(77907, 2, 0, 1, 770001, 3000, 0, 0, 0, 'Look at that. An afternoon with nothing left to do in it.'),
(77908, 1, 0, 1, 770001, 3000, 0, 0, 0, 'Come whenever you like. The lamp is lit; it always is.'),
(77909, 1, 0, 1, 770001, 3000, 0, 0, 0, 'Not far. Just past the last fire, where the wind is.'),
(77207, 1, 0, 1, 770001, 3000, 77904, 0, 0, 'Stay close to me today, $N. I do not know why. I only know I want you close.'),
(77048, 3, 1, 1, 770001, 9000, 77905, 0, 0, 'We are putting back what we did. Not all of it, though. Not us.'),
(77230, 3, 2, 1, 770001, 9000, 77905, 0, 0, 'We are putting back what we did. Not all of it, though. Not us.'),
(77800, 1, 0, 1, 770001, 3000, 77908, 0, 0, 'If you die up there, I will be cross with you for a thousand years. I can, you know. I have them.'),
(77801, 1, 0, 1, 770001, 3000, 77909, 0, 0, 'I have always preferred hello to goodbye. So I will say what everyone says, $N: see you later. I intend to mean it.'),
(77802, 1, 0, 1, 770001, 3000, 77909, 0, 0, 'When you are home, look in your mailbox. I keep my promises, $N. I always have.');

INSERT INTO `remix_talk` (`id`, `npc`, `parent`, `ord`, `side`, `races`, `gender`, `quest`, `after_quest`, `before_quest`, `icon`, `option_text`, `reply`, `credit`, `action`, `param`) VALUES
(77001, 770001, 0, 1, 0, 0, 0, 0, 0, 0, 0, 'Wait for me here. I''d like to walk alone for a while.', 7702600, 0, 3, 0),
(77002, 770001, 0, 2, 0, 0, 0, 0, 0, 0, 0, 'Walk with me again.', 7702601, 0, 4, 0),
(77003, 25250, 0, 1, 0, 0, 0, 77041, 0, 0, 0, 'General, the crawlers on the beach are only the vanguard. My scouts found worm-trails on the western ridge, and their flyers will come over the inner wall.', 7702602, 770530, 0, 0),
(77004, 25301, 0, 1, 0, 0, 0, 77041, 0, 0, 0, 'Counselor, the general says you have the ridge reports. I''d like to see them.', 7702603, 0, 0, 0),
(77005, 25816, 0, 1, 0, 0, 0, 77041, 0, 0, 0, 'Sergeant, they''ll dig under the western ridge and come at the south wall from behind your line. And their flyers will hit the inner defenses.', 7702604, 770531, 0, 0),
(77006, 25302, 0, 1, 0, 0, 0, 77044, 0, 0, 0, 'Colburn, what do you know about Unit S?', 7702605, 770533, 0, 0),
(77007, 25395, 0, 1, 0, 0, 0, 77044, 0, 0, 0, 'Private, who signed the order that sent Unit S east?', 7702606, 770534, 0, 0),
(77008, 770552, 0, 1, 0, 0, 0, 77045, 0, 0, 0, 'Private Harker? Get up. Valiance Keep sent me. Head for Death''s Stand.', 7702607, 770535, 0, 0),
(77009, 770553, 0, 1, 0, 0, 0, 77045, 0, 0, 0, 'Private Dunn. On your feet, soldier. Death''s Stand, now.', 7702608, 770536, 0, 0),
(77010, 770554, 0, 1, 0, 0, 0, 77045, 0, 0, 0, 'Corporal Mabry. Your men are getting out. Lead them to Death''s Stand.', 7702609, 770537, 0, 0),
(77011, 770555, 0, 1, 0, 0, 0, 77045, 0, 0, 0, 'Private Sorrel. Can you stand? Death''s Stand is south. Go.', 7702610, 770538, 0, 0),
(77012, 25251, 0, 1, 0, 0, 0, 77046, 0, 0, 0, 'Leryssa, the counselor knows you''re asking about Thassarian. Leave Valiance Keep tonight. Take the Kraken home.', 7702611, 770539, 0, 0),
(77013, 25826, 0, 1, 0, 0, 0, 77046, 0, 0, 0, 'Vindicator, the woman upstairs is in danger. Someone in the inner hold wants her silenced. Will you watch over her?', 7702612, 770540, 0, 0),
(77014, 25237, 0, 1, 0, 0, 0, 77050, 0, 0, 0, 'The nerubians are under the floor, Overlord. When they come, they''ll come from below and above at once.', 7702613, 770560, 0, 0),
(77015, 25237, 0, 2, 0, 0, 0, 77050, 0, 0, 0, 'And the cultists out west serve a lich. Kel''Thuzad. I''d stake my life on it.', 7702614, 0, 0, 0),
(77016, 25256, 0, 1, 0, 0, 0, 77050, 0, 0, 0, 'High Overlord, the nerubians will come up through the floor of the hold. The quarry is riddled with their tunnels.', 7702615, 770561, 0, 0),
(77017, 25446, 0, 1, 0, 0, 0, 77050, 0, 0, 0, 'Captain, they''ll come over the south wall, and out of the sky. Put your marksmen up.', 7702616, 770562, 0, 0),
(77018, 25329, 0, 1, 0, 0, 0, 77054, 0, 0, 0, 'Gorge, keep a garrison on this coast once the tanks roll out. The Kvaldir will be back the moment the beach is empty. Ask Saurfang for the men; he''ll send them.', 7702617, 770563, 0, 0),
(77019, 27155, 0, 1, 0, 0, 0, 77223, 0, 0, 0, 'Commander, the riders who fell over the lower village will dive on the square next. Get your archers off the roofs before they do.', 7702618, 770580, 0, 0),
(77020, 27156, 0, 1, 0, 0, 0, 77223, 0, 0, 0, 'Highlord, close the mine road. The dead will come up it before the week is out.', 7702619, 770581, 0, 0),
(77021, 27317, 0, 1, 0, 0, 0, 77223, 0, 0, 0, 'Gryphon Commander, the roost that cracked won''t hold much longer. Move your birds tonight.', 7702620, 770582, 0, 0),
(77022, 26649, 0, 1, 0, 0, 0, 77236, 0, 0, 0, 'Tell Saurfang this, from me: I have seen sons die proving themselves to their fathers. His should not lead the charge himself.', 7702621, 770583, 0, 0),
(77023, 27320, 0, 1, 0, 0, 0, 77235, 0, 0, 0, 'Deathguard, those blight spreaders by the east gate. What are they being saved for?', 7702622, 770584, 0, 0),
(77024, 27846, 0, 1, 0, 0, 0, 77235, 0, 0, 0, 'Apothecary, I''m counting crates for Agmar''s Hammer. How much of the blight is going there?', 7702623, 770585, 0, 0),
(77025, 770550, 0, 1, 0, 0, 0, 77048, 0, 0, 0, 'William, the cult will try again, and next time I won''t be there. Sail home tonight, under another name.', 7702624, 770600, 0, 0),
(77026, 26187, 0, 1, 0, 0, 0, 77049, 0, 0, 0, 'Corporal, these orders send your men home to Stormwind. The record will say Unit S was lost at the landing. Nobody will come looking.', 7702625, 770601, 0, 0),
(77027, 25329, 0, 2, 0, 0, 0, 77230, 0, 0, 0, 'Gorge, the Warchief is calling every soldier who can walk back to Orgrimmar. The garrison too, and the spare tanks.', 7702626, 770602, 0, 0),
(77028, 770001, 0, 3, 0, 0, 0, 77901, 0, 0, 0, 'Sit with her, and take the cup she offers.', 7702627, 0, 0, 0),
(77029, 770001, 77028, 1, 0, 0, 0, 77901, 0, 0, 0, 'How old are you, really?', 7702628, 0, 0, 0),
(77030, 770001, 77028, 2, 0, 0, 0, 77901, 0, 0, 0, 'Is it true that dragons sleep on gold?', 7702629, 0, 0, 0),
(77031, 770001, 77028, 3, 0, 1, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702630, 0, 0, 0),
(77032, 770001, 77028, 4, 0, 4, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702631, 0, 0, 0),
(77033, 770001, 77028, 5, 0, 8, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702632, 0, 0, 0),
(77034, 770001, 77028, 6, 0, 64, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702633, 0, 0, 0),
(77035, 770001, 77028, 7, 0, 1024, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702634, 0, 0, 0),
(77036, 770001, 77028, 8, 0, 2, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702635, 0, 0, 0),
(77037, 770001, 77028, 9, 0, 16, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702636, 0, 0, 0),
(77038, 770001, 77028, 10, 0, 32, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702637, 0, 0, 0),
(77039, 770001, 77028, 11, 0, 128, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702638, 0, 0, 0),
(77040, 770001, 77028, 12, 0, 512, 0, 77901, 0, 0, 0, 'You keep looking at me.', 7702639, 0, 0, 0),
(77041, 770001, 77028, 13, 0, 0, 0, 77901, 0, 0, 0, 'What do you do when you''re not working?', 7702640, 770700, 0, 0),
(77042, 770001, 0, 4, 1, 0, 0, 77902, 0, 0, 0, 'One drink, then. A Hero''s Welcome?', 0, 0, 5, 1),
(77043, 770001, 0, 5, 2, 0, 0, 77902, 0, 0, 0, 'One drink, then. The Filthy Animal?', 0, 0, 5, 2),
(77044, 770001, 0, 6, 0, 0, 0, 77903, 0, 0, 0, 'I''d love to. Show me this landing.', 0, 0, 5, 3),
(77045, 770001, 0, 7, 0, 0, 0, 77904, 0, 0, 0, 'Show me.', 0, 0, 5, 4),
(77046, 770001, 0, 8, 0, 0, 0, 77906, 0, 0, 0, 'I''m ready. Take me flying.', 0, 0, 5, 5),
(77047, 770001, 0, 9, 0, 0, 0, 77907, 0, 0, 0, 'Lead the way. I''ll carry the basket.', 0, 0, 5, 7),
(77048, 770001, 0, 10, 0, 0, 0, 77908, 0, 0, 0, 'Take me to your tent.', 0, 0, 5, 6),
(77049, 770001, 0, 11, 0, 0, 0, 77909, 0, 0, 0, 'Walk with her to the edge of the camp.', 0, 0, 5, 8),
(77050, 770001, 0, 12, 0, 0, 0, 77905, 0, 0, 0, 'Sit beside her, and take her hand.', 7702641, 0, 0, 0),
(77051, 770001, 77050, 1, 0, 0, 0, 77905, 0, 0, 0, 'You''re not a monster. You gave them more time than history ever did.', 7702642, 0, 0, 0),
(77052, 770001, 77051, 1, 0, 0, 0, 77905, 0, 0, 0, 'From you. I love you, Moratari.', 7702643, 770704, 0, 0),
(77053, 770001, 0, 13, 0, 1, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702644, 0, 0, 0),
(77054, 770001, 0, 14, 0, 4, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702645, 0, 0, 0),
(77055, 770001, 0, 15, 0, 8, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702646, 0, 0, 0),
(77056, 770001, 0, 16, 0, 64, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702647, 0, 0, 0),
(77057, 770001, 0, 17, 0, 1024, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702648, 0, 0, 0),
(77058, 770001, 0, 18, 0, 2, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702649, 0, 0, 0),
(77059, 770001, 0, 19, 0, 16, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702650, 0, 0, 0),
(77060, 770001, 0, 20, 0, 32, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702651, 0, 0, 0),
(77061, 770001, 0, 21, 0, 128, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702652, 0, 0, 0),
(77062, 770001, 0, 22, 0, 512, 0, 0, 77902, 0, 0, 'Tell her she looks lovely today.', 7702653, 0, 0, 0),
(77063, 770001, 0, 23, 0, 0, 0, 0, 77903, 0, 0, 'Kiss her.', 0, 0, 1, 909),
(77064, 770001, 0, 24, 0, 0, 0, 0, 0, 77910, 0, 'I''m a time jumper. I already know where this goes between us, and I don''t want to wait.', 7702654, 0, 6, 0);

DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702600 AND 7702999;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(7702600, 'Of course. I will be at the camps, beside whoever has work for you next. Say the word when you want me back.', 'Of course. I will be at the camps, beside whoever has work for you next. Say the word when you want me back.', 1),
(7702601, 'I was hoping you would ask. Lead on, $N.', 'I was hoping you would ask. Lead on, $N.', 1),
(7702602, '<General Arlos glances at Counselor Talbot before he answers.>$B$BYour concern does you credit, $N. But Counselor Talbot has the ridge reports, and he assures me there is nothing in them to trouble us. The walls will hold.$B$BIf your scouts are still uneasy, take it to Sergeant Hammerhill. The defenses are his to worry about.', '<General Arlos glances at Counselor Talbot before he answers.>$B$BYour concern does you credit, $N. But Counselor Talbot has the ridge reports, and he assures me there is nothing in them to trouble us. The walls will hold.$B$BIf your scouts are still uneasy, take it to Sergeant Hammerhill. The defenses are his to worry about.', 1),
(7702603, '<Counselor Talbot smiles. It does not reach his eyes.>$B$BThe ridge reports are for the general''s staff, $N. Our men are villagers, mostly, and villagers see worms in every shadow. Surely you didn''t come all the way to Northrend to chase their superstitions?$B$BDo tell your scouts to be careful up there. It would be a shame to lose them.', '<Counselor Talbot smiles. It does not reach his eyes.>$B$BThe ridge reports are for the general''s staff, $N. Our men are villagers, mostly, and villagers see worms in every shadow. Surely you didn''t come all the way to Northrend to chase their superstitions?$B$BDo tell your scouts to be careful up there. It would be a shame to lose them.', 1),
(7702604, 'Under the ridge, eh? <Sergeant Hammerhill tugs at his beard.> Blasted worms. Years in the mines teach you to listen to the ground, and it''s been grumbling at me since we landed.$B$BThe general can keep his reports. I''ll have two catapults on the south wall by dark and spotters up on that ridge, and if anyone asks, they walked there on their own.$B$BIf you''re wrong, I''ve lost a night''s sleep. If you''re right, I owe you a drink.', 'Under the ridge, eh? <Sergeant Hammerhill tugs at his beard.> Blasted worms. Years in the mines teach you to listen to the ground, and it''s been grumbling at me since we landed.$B$BThe general can keep his reports. I''ll have two catapults on the south wall by dark and spotters up on that ridge, and if anyone asks, they walked there on their own.$B$BIf you''re wrong, I''ve lost a night''s sleep. If you''re right, I owe you a drink.', 1),
(7702605, '<Old Man Colburn looks up from his empty cup, and for a moment his eyes are sharp.>$B$BUnit S... hmmph. Don''t make any sense. Darkshire went to the Dragonblight. The Goldshire boys went to the Fjord. I know every unit, every brigade, every detachment in this expedition, and there''s no S.$B$BSo somebody made it up. And people don''t make up units to send them somewhere nice.', '<Old Man Colburn looks up from his empty cup, and for a moment his eyes are sharp.>$B$BUnit S... hmmph. Don''t make any sense. Darkshire went to the Dragonblight. The Goldshire boys went to the Fjord. I know every unit, every brigade, every detachment in this expedition, and there''s no S.$B$BSo somebody made it up. And people don''t make up units to send them somewhere nice.', 1),
(7702606, '<Private Brau looks past you at the guard by the door, and drops his voice.>$B$B''S'' stood for suicide. That''s what the lads called it. A dozen of us against a Scourge ziggurat. Call me a coward if you like; I know a grave when I''m marched into one.$B$BThe orders came down from the inner hold with the general''s seal on them, but the general never signed nothing, friend. I ran letters up there before they put me in that unit. I saw the hand. It was the counselor''s.$B$BDon''t say I told you. That one hears everything.', '<Private Brau looks past you at the guard by the door, and drops his voice.>$B$B''S'' stood for suicide. That''s what the lads called it. A dozen of us against a Scourge ziggurat. Call me a coward if you like; I know a grave when I''m marched into one.$B$BThe orders came down from the inner hold with the general''s seal on them, but the general never signed nothing, friend. I ran letters up there before they put me in that unit. I saw the hand. It was the counselor''s.$B$BDon''t say I told you. That one hears everything.', 1),
(7702607, 'Sent? Somebody sent... <Private Harker scrambles to his feet.> Yes, $Gsir:ma''am;. Death''s Stand. I can walk. I can run, if it comes to it.', 'Sent? Somebody sent... <Private Harker scrambles to his feet.> Yes, $Gsir:ma''am;. Death''s Stand. I can walk. I can run, if it comes to it.', 1),
(7702608, 'I knew it. I told Harker someone would come. He said I was mad. <Private Dunn laughs, too loudly, then stops.> Death''s Stand. Yes.', 'I knew it. I told Harker someone would come. He said I was mad. <Private Dunn laughs, too loudly, then stops.> Death''s Stand. Yes.', 1),
(7702609, 'Lead them. Right. <Corporal Mabry rubs his rope-burned wrists.> The cult said we''d be serving them by the full moon. Tell whoever sent you... no. I''ll tell them myself.', 'Lead them. Right. <Corporal Mabry rubs his rope-burned wrists.> The cult said we''d be serving them by the full moon. Tell whoever sent you... no. I''ll tell them myself.', 1),
(7702610, '<Private Sorrel stares at you as if you were a ghost.>$B$BThey said no one knew we were here. They said we didn''t even have a name.$B$B...South. Yes. South.', '<Private Sorrel stares at you as if you were a ghost.>$B$BThey said no one knew we were here. They said we didn''t even have a name.$B$B...South. Yes. South.', 1),
(7702611, 'Go home? <Leryssa laughs, not kindly.>$B$BI sold everything I had to get here, $N. My brother is out there somewhere, alive, and you want me to sail away before I''ve even seen his face?$B$BNo. Let them come. I''m not leaving without him.', 'Go home? <Leryssa laughs, not kindly.>$B$BI sold everything I had to get here, $N. My brother is out there somewhere, alive, and you want me to sail away before I''ve even seen his face?$B$BNo. Let them come. I''m not leaving without him.', 1),
(7702612, '<Vindicator Yaala''s eyes narrow.>$B$BThe inner hold. You choose your words carefully, $c. So do I.$B$BI have hunted this cult through the keep since we landed: the docks, the jail, this inn''s own kitchen. I had not thought it reached so high.$B$BI will watch over the girl. If anyone comes for her, they will have to come through me.', '<Vindicator Yaala''s eyes narrow.>$B$BThe inner hold. You choose your words carefully, $c. So do I.$B$BI have hunted this cult through the keep since we landed: the docks, the jail, this inn''s own kitchen. I had not thought it reached so high.$B$BI will watch over the girl. If anyone comes for her, they will have to come through me.', 1),
(7702613, 'Under my floor? <Garrosh sniffs.> Then they will find my boot waiting for them.$B$BI smelled your fear the moment you walked in, $r. Keep it out of my hold. The Warsong does not cower before insects.', 'Under my floor? <Garrosh sniffs.> Then they will find my boot waiting for them.$B$BI smelled your fear the moment you walked in, $r. Keep it out of my hold. The Warsong does not cower before insects.', 1),
(7702614, 'Kel''Thuzad? That lich was destroyed in the Plaguelands. <Garrosh spits.> I do not fight ghost stories, $r. I fight what bleeds.', 'Kel''Thuzad? That lich was destroyed in the Plaguelands. <Garrosh spits.> I do not fight ghost stories, $r. I fight what bleeds.', 1),
(7702615, '<Saurfang studies you for a long moment.>$B$BRazgor tells me the quarry is soft. Holgoth tells me he has charges and no one to carry them. And now you.$B$BHolgoth will have his hands by nightfall.$B$B<Saurfang looks west, toward the plains.>$B$BThere are necromancers out there in the robes of the Cult of the Damned. Where the Cult goes, plague is never far behind. I will put scouts on the plains.$B$BWhat I have told you stays between us. Hellscream has enough to shout about.', '<Saurfang studies you for a long moment.>$B$BRazgor tells me the quarry is soft. Holgoth tells me he has charges and no one to carry them. And now you.$B$BHolgoth will have his hands by nightfall.$B$B<Saurfang looks west, toward the plains.>$B$BThere are necromancers out there in the robes of the Cult of the Damned. Where the Cult goes, plague is never far behind. I will put scouts on the plains.$B$BWhat I have told you stays between us. Hellscream has enough to shout about.', 1),
(7702616, 'Settle down, soldier!$B$B<The captain looks up at the sky, then back at you.>$B$BWe''ll be ready for ''em... You did a good job in warning us.', 'Settle down, soldier!$B$B<The captain looks up at the sky, then back at you.>$B$BWe''ll be ready for ''em... You did a good job in warning us.', 1),
(7702617, 'A garrison? Here? Hellscream condemned this coast, an'' everybody on it!$B$B<Gorge chews on that.>$B$B...But Saurfang ain''t Hellscream. An'' I ain''t sendin'' my tanks out to the plains so them mist-men can walk in behind ''em.$B$BI''ll send a runner to the hold. An'' if anybody asks, it was my idea.', 'A garrison? Here? Hellscream condemned this coast, an'' everybody on it!$B$B<Gorge chews on that.>$B$B...But Saurfang ain''t Hellscream. An'' I ain''t sendin'' my tanks out to the plains so them mist-men can walk in behind ''em.$B$BI''ll send a runner to the hold. An'' if anybody asks, it was my idea.', 1),
(7702618, '<Commander Lynore Windstryke follows your gaze to the rooftops around the square.>$B$BThose riders flew from this keep. They know where we post our archers because we taught them.$B$BVery well, $c. They come off the roofs before dark.', '<Commander Lynore Windstryke follows your gaze to the rooftops around the square.>$B$BThose riders flew from this keep. They know where we post our archers because we taught them.$B$BVery well, $c. They come off the roofs before dark.', 1),
(7702619, 'Close the mine road? On whose authority?$B$B<Highlord Leoric Von Zeldig glares at you, then at Siege Engineer Quarterflash, who only shrugs.>$B$B...Mine, I suppose. The mine is lost already, and my miners dig for the Scourge now. I''ll not have them walking up my road as well. Consider it closed.', 'Close the mine road? On whose authority?$B$B<Highlord Leoric Von Zeldig glares at you, then at Siege Engineer Quarterflash, who only shrugs.>$B$B...Mine, I suppose. The mine is lost already, and my miners dig for the Scourge now. I''ll not have them walking up my road as well. Consider it closed.', 1),
(7702620, '<Gryphon Commander Urik looks up at the cracked beam, and his face falls.>$B$BThe birds have known for days. They won''t settle up there, and I''ve been calling it nerves.$B$BAll right, friend. They come down and sleep in the yard. They''ll sulk about it for a week, and I''ll let them.', '<Gryphon Commander Urik looks up at the cracked beam, and his face falls.>$B$BThe birds have known for days. They won''t settle up there, and I''ve been calling it nerves.$B$BAll right, friend. They come down and sleep in the yard. They''ll sulk about it for a week, and I''ll let them.', 1),
(7702621, '<Messenger Torvus is quiet for a moment.>$B$BSaurfang the Younger needs no nursemaid, and he would not thank you for this. But it is not meant for him, is it?$B$BWrite it small, and give it to me with a handshake. The Kor''kron watch anyone who stands near me too long.', '<Messenger Torvus is quiet for a moment.>$B$BSaurfang the Younger needs no nursemaid, and he would not thank you for this. But it is not meant for him, is it?$B$BWrite it small, and give it to me with a handshake. The Kor''kron watch anyone who stands near me too long.', 1),
(7702622, 'Saved for? ''Special missions''! <Deathguard Molder spits.>$B$BFive spreaders, loaded and sealed, and the Grand Apothecary''s own people sitting on them day and night. Meanwhile I''ve the Onslaught''s ballistae to break, and I''m out picking bombs off Scourge siegesmiths like a common grave robber.$B$BWhatever they''re saving them for, it had better be worth it.', 'Saved for? ''Special missions''! <Deathguard Molder spits.>$B$BFive spreaders, loaded and sealed, and the Grand Apothecary''s own people sitting on them day and night. Meanwhile I''ve the Onslaught''s ballistae to break, and I''m out picking bombs off Scourge siegesmiths like a common grave robber.$B$BWhatever they''re saving them for, it had better be worth it.', 1),
(7702623, 'Agmar''s Hammer? Only the specimen. One crate, yes. <Junior Apothecary Lawrence pulls his ledger closer.>$B$BThe rest goes to the Grand Apothecary''s special detachment, up at the ga-- up north. I''m not to say where. I wasn''t to say that, either.$B$BYou won''t mention it? No. No, of course you won''t. Of course.', 'Agmar''s Hammer? Only the specimen. One crate, yes. <Junior Apothecary Lawrence pulls his ledger closer.>$B$BThe rest goes to the Grand Apothecary''s special detachment, up at the ga-- up north. I''m not to say where. I wasn''t to say that, either.$B$BYou won''t mention it? No. No, of course you won''t. Of course.', 1),
(7702624, 'Another name? <William Allerton laughs, then stops.> You''re serious.$B$BSo as far as the Expedition knows, I died down here. ...Fine. Leryssa has her brother back. That''s what I wrote to her for.$B$BI always fancied myself a farmer. Somewhere warm, where the ground doesn''t open up under you.', 'Another name? <William Allerton laughs, then stops.> You''re serious.$B$BSo as far as the Expedition knows, I died down here. ...Fine. Leryssa has her brother back. That''s what I wrote to her for.$B$BI always fancied myself a farmer. Somewhere warm, where the ground doesn''t open up under you.', 1),
(7702625, 'Lost at the landing. <Corporal Venn reads the orders twice, then a third time.>$B$BWell. We were, weren''t we? For a while there.$B$BGeneral''s seal, and not the general''s hand. That''s how we got sent out here in the first place.$B$B''S'' for suicide, the lads called it. Maybe now it''s ''S'' for ''sent home''. I''ll take it, friend, and I won''t ask who wrote it.', 'Lost at the landing. <Corporal Venn reads the orders twice, then a third time.>$B$BWell. We were, weren''t we? For a while there.$B$BGeneral''s seal, and not the general''s hand. That''s how we got sent out here in the first place.$B$B''S'' for suicide, the lads called it. Maybe now it''s ''S'' for ''sent home''. I''ll take it, friend, and I won''t ask who wrote it.', 1),
(7702626, 'Orgrimmar? Martial law, they''re sayin''... <Gorge spits into the sand.>$B$BCondemned again, then. Figures. Every time I get this beach lookin'' like somethin'', somebody takes it away.$B$BFine! Take ''em, buddy! But the six tanks stay with me. Somebody''s gotta keep an eye on that mist.', 'Orgrimmar? Martial law, they''re sayin''... <Gorge spits into the sand.>$B$BCondemned again, then. Figures. Every time I get this beach lookin'' like somethin'', somebody takes it away.$B$BFine! Take ''em, buddy! But the six tanks stay with me. Somebody''s gotta keep an eye on that mist.', 1),
(7702627, '<Moratari pours two cups from a pot that was not there a moment ago.>$B$BCareful. It is hot. It has been hot for about four hundred years; I keep it in a pocket of an afternoon in Tanaris.$B$BWell? Ask me something.', '<Moratari pours two cups from a pot that was not there a moment ago.>$B$BCareful. It is hot. It has been hot for about four hundred years; I keep it in a pocket of an afternoon in Tanaris.$B$BWell? Ask me something.', 1),
(7702628, 'That depends on how you count. About ten thousand years, but not all of them in order, and a few of them twice. Next question.', 'That depends on how you count. About ten thousand years, but not all of them in order, and a few of them twice. Next question.', 1),
(7702629, 'Only in stories. My kind sleeps on sand: soft, warm, and in your scales for the rest of your life. Next question.', 'Only in stories. My kind sleeps on sand: soft, warm, and in your scales for the rest of your life. Next question.', 1),
(7702630, 'Humans change so quickly. I look away for a season, and you are someone else. I am trying to remember you exactly as you are now.', 'Humans change so quickly. I look away for a season, and you are someone else. I am trying to remember you exactly as you are now.', 1),
(7702631, 'You have tea in your $Gbeard:hair;. No, leave it. It suits you.', 'You have tea in your $Gbeard:hair;. No, leave it. It suits you.', 1),
(7702632, 'I was in Zin-Azshari once, before the Sundering. Your people blushed exactly like that, even then. I am glad some things kept.', 'I was in Zin-Azshari once, before the Sundering. Your people blushed exactly like that, even then. I am glad some things kept.', 1),
(7702633, 'I am trying to decide whether to kneel down or to pick you up. Both seem rude.', 'I am trying to decide whether to kneel down or to pick you up. Both seem rude.', 1),
(7702634, 'Your tail has been tapping the ground since I sat down. Is that a good sign? Tell me it is a good sign.', 'Your tail has been tapping the ground since I sat down. Is that a good sign? Tell me it is a good sign.', 1),
(7702635, 'Your tusks. I was wondering how anyone... Never mind. It was purely academic. Drink your tea.', 'Your tusks. I was wondering how anyone... Never mind. It was purely academic. Drink your tea.', 1),
(7702636, 'Your hands are cold. Here, hold the cup. No, hold it longer. There.', 'Your hands are cold. Here, hold the cup. No, hold it longer. There.', 1),
(7702637, 'You are holding that tiny cup as if it were a baby bird. I find that I like that very much.', 'You are holding that tiny cup as if it were a baby bird. I find that I like that very much.', 1),
(7702638, 'You have been grinning since I poured. They say trolls grin at everything. I hope they are wrong, and it is only me.', 'You have been grinning since I poured. They say trolls grin at everything. I hope they are wrong, and it is only me.', 1),
(7702639, 'I am checking my work. I borrowed this shape from your people, and I have always wondered whether I got the ears right. I did, as it happens. Do not let it go to your head.', 'I am checking my work. I borrowed this shape from your people, and I have always wondered whether I got the ears right. I did, as it happens. Do not let it go to your head.', 1),
(7702640, 'I... read. I keep records, and when I have finished keeping them, I read them.$B$B<Moratari looks at you over the rim of her cup for a long moment.>$B$BThat is a dreadful answer, is it not? I think I would like a better one. Perhaps you could help me find it.', 'I... read. I keep records, and when I have finished keeping them, I read them.$B$B<Moratari looks at you over the rim of her cup for a long moment.>$B$BThat is a dreadful answer, is it not? I think I would like a better one. Perhaps you could help me find it.', 1),
(7702641, '<Moratari''s hand is warm, and shaking.>$B$BEvery one of them was real, $N. Every soldier who walked off that tundra because we were there. I wrote down all their names.$B$BAnd now I have to help put the record back. Tell me I am not a monster.', '<Moratari''s hand is warm, and shaking.>$B$BEvery one of them was real, $N. Every soldier who walked off that tundra because we were there. I wrote down all their names.$B$BAnd now I have to help put the record back. Tell me I am not a monster.', 1),
(7702642, 'More time. <She laughs, wetly.> That is such a dragon thing to say. Where did you learn to talk like a dragon?', 'More time. <She laughs, wetly.> That is such a dragon thing to say. Where did you learn to talk like a dragon?', 1),
(7702643, '<For a long moment, Moratari says nothing at all.>$B$BI have watched people say that to each other for ten thousand years. I never once thought anyone would say it to me.$B$B...I love you too. I think I have since the tea. I do not know what this does to the record, and for once I do not care.', '<For a long moment, Moratari says nothing at all.>$B$BI have watched people say that to each other for ten thousand years. I never once thought anyone would say it to me.$B$B...I love you too. I think I have since the tea. I do not know what this does to the record, and for once I do not care.', 1),
(7702644, 'Your people say that as if you had all the time in the world. I like that about you. Say it again tomorrow.', 'Your people say that as if you had all the time in the world. I like that about you. Say it again tomorrow.', 1),
(7702645, 'The titans made your people out of stone, you know. It shows: you said that as if it cost you something. Thank you.', 'The titans made your people out of stone, you know. It shows: you said that as if it cost you something. Thank you.', 1),
(7702646, 'I have heard your people say that to the moon. I did not know they said it to anyone else.', 'I have heard your people say that to the moon. I did not know they said it to anyone else.', 1),
(7702647, 'Say it again, louder. I am all the way up here.', 'Say it again, louder. I am all the way up here.', 1),
(7702648, 'Your tail is doing the thing again. I have decided it is my favorite thing.', 'Your tail is doing the thing again. I have decided it is my favorite thing.', 1),
(7702649, 'An orc paying compliments. Somewhere, Garrosh just felt a chill and does not know why.', 'An orc paying compliments. Somewhere, Garrosh just felt a chill and does not know why.', 1),
(7702650, 'You say that without even breathing. It is a very efficient compliment. I accept it.', 'You say that without even breathing. It is a very efficient compliment. I accept it.', 1),
(7702651, 'In all my records, I have never once caught a tauren flattering anyone. So I suppose I must believe you.', 'In all my records, I have never once caught a tauren flattering anyone. So I suppose I must believe you.', 1),
(7702652, 'Dat''s what ya say to all de dragons, mon? ...I am sorry. I have wanted to try the accent for weeks.', 'Dat''s what ya say to all de dragons, mon? ...I am sorry. I have wanted to try the accent for weeks.', 1),
(7702653, 'Of course I do. So do you. We are a very good-looking pair, and everyone in the Bazaar is annoyed about it.', 'Of course I do. So do you. We are a very good-looking pair, and everyone in the Bazaar is annoyed about it.', 1),
(7702654, '<Moratari laughs, a real one, surprised out of her.>$B$BA time jumper. Of course you are. You have read ahead, to the pages with me in them.$B$BVery well. I will not make you wait for the war''s permission. Some of what we do will not have happened yet, for you. Humor me, and pretend it has.', '<Moratari laughs, a real one, surprised out of her.>$B$BA time jumper. Of course you are. You have read ahead, to the pages with me in them.$B$BVery well. I will not make you wait for the war''s permission. Some of what we do will not have happened yet, for you. Humor me, and pretend it has.', 1);

CREATE TABLE IF NOT EXISTS `remix_original_story_npcflag` (
  `entry` INT UNSIGNED NOT NULL,
  `npcflag` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
UPDATE `creature_template` c JOIN `remix_original_story_npcflag` o ON o.`entry` = c.`entry` SET c.`npcflag` = o.`npcflag`;
DELETE FROM `remix_original_story_npcflag`;
INSERT INTO `remix_original_story_npcflag` (`entry`, `npcflag`) SELECT `entry`, `npcflag` FROM `creature_template` WHERE `entry` IN (25237, 25250, 25251, 25256, 25301, 25302, 25329, 25395, 25446, 25816, 25826, 26187, 26649, 27155, 27156, 27317, 27320, 27846) AND (`npcflag` & 3) = 0;
UPDATE `creature_template` c JOIN `remix_original_story_npcflag` o ON o.`entry` = c.`entry` SET c.`npcflag` = c.`npcflag` | 1;
CREATE TABLE IF NOT EXISTS `remix_original_story_unit_flags` (
  `entry` INT UNSIGNED NOT NULL,
  `unit_flags` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
UPDATE `creature_template` c JOIN `remix_original_story_unit_flags` o ON o.`entry` = c.`entry` SET c.`unit_flags` = o.`unit_flags`;
DELETE FROM `remix_original_story_unit_flags`;
INSERT INTO `remix_original_story_unit_flags` (`entry`, `unit_flags`) SELECT `entry`, `unit_flags` FROM `creature_template` WHERE `entry` IN (25446);
UPDATE `creature_template` c JOIN `remix_original_story_unit_flags` o ON o.`entry` = c.`entry` SET c.`unit_flags` = c.`unit_flags` | 512;

INSERT INTO `remix_outing` (`id`, `map`, `x`, `y`, `z`, `o`, `scene`, `private`, `undress`, `back`, `flight_from`, `flight_to`, `mount`, `name`) VALUES
(1, 571, 5851.00, 640.60, 647.60, 1.050, 901, 0, 0, 1, 0, 0, 0, 'Cider at A Hero''s Welcome, Dalaran'),
(2, 571, 5886.90, 513.70, 641.70, 1.870, 902, 0, 0, 1, 0, 0, 0, 'Cider at The Filthy Animal, Dalaran'),
(3, 571, 5806.00, 444.00, 658.80, 4.450, 903, 0, 0, 1, 0, 0, 0, 'Dinner at Krasus'' Landing, Dalaran'),
(4, 571, 3528.00, 268.00, 342.80, 2.400, 904, 0, 0, 1, 0, 0, 0, 'Atop Wyrmrest Temple, at night'),
(5, 571, 5816.00, 447.00, 658.80, 4.450, 905, 0, 0, 1, 310, 252, 25833, 'On her back, from Dalaran to Wyrmrest Temple'),
(6, 571, 6413.00, 1853.00, 508.70, 5.712, 906, 1, 1, 1, 0, 0, 0, 'Moratari''s tent, the Bazaar'),
(7, 571, 5551.80, 5850.30, -74.60, 2.000, 907, 1, 0, 1, 0, 0, 0, 'An afternoon by the river, Sholazar Basin'),
(8, 571, 6410.00, 470.00, 511.40, 2.400, 908, 1, 0, 1, 0, 0, 0, 'The edge of the camp, Crusaders'' Pinnacle');
INSERT INTO `remix_outing_line` (`outing`, `at_ms`, `text`) VALUES
(5, 4000, 'Lean with me. Not that way. ...There.'),
(5, 14000, 'The Violet Citadel, behind us. The Kirin Tor are at war with the blue dragonflight this year; let us hope their sentries know a bronze when they see one.'),
(5, 28000, 'Crystalsong. The trees ring when the wind is right. Listen.'),
(5, 44000, 'You are holding on tightly. I do not mind.'),
(5, 62000, 'Wyrmrest. Every dragon comes here in the end, to sleep. I wanted you to see it the way we do: from above, and arriving.'),
(5, 80000, 'Down we go. And not one mage shot at us. A successful first flight, I would say.');

INSERT INTO `remix_look` (`display`, `from_display`, `extra`, `from_extra`, `bake`, `item1`, `item2`, `item3`, `item4`, `item5`, `item6`, `item7`, `item8`, `item9`, `item10`, `item11`) VALUES
(32755, 25458, 21382, 17276, 0, 0, 0, 0, 34726, 0, 0, 0, 0, 0, 0, 0),
(32756, 25458, 21383, 17276, 0, 0, 0, 12327, 0, 0, 0, 0, 0, 0, 0, 0);
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (32755, 32756);
DELETE FROM `creaturedisplayinfoextra_dbc` WHERE `ID` IN (21382, 21383);
DELETE FROM `creature_model_info` WHERE `DisplayID` IN (32755, 32756);
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (32755, 2209, 0, 21382, 1.25, 255, '', '', '', '', 1, 0, 292, 0, 0, 0);
INSERT INTO `creaturedisplayinfoextra_dbc` (`ID`, `DisplayRaceID`, `DisplaySexID`, `SkinID`, `FaceID`, `HairStyleID`, `HairColorID`, `FacialHairID`, `NPCItemDisplay1`, `NPCItemDisplay2`, `NPCItemDisplay3`, `NPCItemDisplay4`, `NPCItemDisplay5`, `NPCItemDisplay6`, `NPCItemDisplay7`, `NPCItemDisplay8`, `NPCItemDisplay9`, `NPCItemDisplay10`, `NPCItemDisplay11`, `Flags`, `BakeName`) VALUES (21382, 10, 1, 15, 2, 11, 4, 2, 0, 0, 0, 34726, 0, 0, 0, 0, 0, 0, 0, 0, '');
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`, `VerifiedBuild`) SELECT 32755, `BoundingRadius`, `CombatReach`, `Gender`, 0, 0 FROM `creature_model_info` WHERE `DisplayID` = 25458;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES (32756, 2209, 0, 21383, 1.25, 255, '', '', '', '', 1, 0, 292, 0, 0, 0);
INSERT INTO `creaturedisplayinfoextra_dbc` (`ID`, `DisplayRaceID`, `DisplaySexID`, `SkinID`, `FaceID`, `HairStyleID`, `HairColorID`, `FacialHairID`, `NPCItemDisplay1`, `NPCItemDisplay2`, `NPCItemDisplay3`, `NPCItemDisplay4`, `NPCItemDisplay5`, `NPCItemDisplay6`, `NPCItemDisplay7`, `NPCItemDisplay8`, `NPCItemDisplay9`, `NPCItemDisplay10`, `NPCItemDisplay11`, `Flags`, `BakeName`) VALUES (21383, 10, 1, 15, 2, 11, 4, 2, 0, 0, 12327, 0, 0, 0, 0, 0, 0, 0, 0, 0, '');
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`, `VerifiedBuild`) SELECT 32756, `BoundingRadius`, `CombatReach`, `Gender`, 0, 0 FROM `creature_model_info` WHERE `DisplayID` = 25458;

-- The creatures this file owns (770500 to 770999): credits never spawned, and copies of the game's.
DELETE FROM `creature_template` WHERE `entry` BETWEEN 770500 AND 770999;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 770500 AND 770999;
DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN 770500 AND 770999;
DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN 770500 AND 770999;
DELETE FROM `creature_queststarter` WHERE `id` BETWEEN 770500 AND 770999;
DELETE FROM `creature_questender` WHERE `id` BETWEEN 770500 AND 770999;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`, `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES
(770530, 'General Arlos warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770531, 'Sergeant Hammerhill warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770532, 'The fourth sinkhole collapsed', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770533, 'Old Man Colburn asked about Unit S', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770534, 'Private Brau asked who signed the order', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770535, 'Private Harker freed', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770536, 'Private Dunn freed', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770537, 'Corporal Mabry freed', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770538, 'Private Sorrel freed', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770539, 'Leryssa warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770540, 'Vindicator Yaala asked to watch over Leryssa', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770560, 'Garrosh Hellscream warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770561, 'High Overlord Saurfang warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770562, 'The Warsong Captain warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770563, 'Gorge asked to hold the coast', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770580, 'Commander Lynore Windstryke warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770581, 'Highlord Leoric Von Zeldig warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770582, 'Gryphon Commander Urik warned', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770583, 'A word sent with Messenger Torvus', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770584, 'Deathguard Molder asked about the blight spreaders', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770585, 'Junior Apothecary Lawrence asked about the shipments', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770600, 'William Allerton persuaded to sail home', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770601, 'Corporal Venn given the orders', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770602, 'Gorge told of the recall', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770700, 'Tea shared with Moratari', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770701, 'A drink with Moratari', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770702, 'Dinner at Krasus'' Landing', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770703, 'The view from Wyrmrest', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770704, 'Moratari comforted', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770705, 'A flight on Moratari''s back', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770706, 'An afternoon by the river', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770707, 'A night in Moratari''s tent', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(770708, 'Moratari''s promise', NULL, 80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(770530, 0, 19373, 1, 1, 0),
(770531, 0, 19373, 1, 1, 0),
(770532, 0, 19373, 1, 1, 0),
(770533, 0, 19373, 1, 1, 0),
(770534, 0, 19373, 1, 1, 0),
(770535, 0, 19373, 1, 1, 0),
(770536, 0, 19373, 1, 1, 0),
(770537, 0, 19373, 1, 1, 0),
(770538, 0, 19373, 1, 1, 0),
(770539, 0, 19373, 1, 1, 0),
(770540, 0, 19373, 1, 1, 0),
(770560, 0, 19373, 1, 1, 0),
(770561, 0, 19373, 1, 1, 0),
(770562, 0, 19373, 1, 1, 0),
(770563, 0, 19373, 1, 1, 0),
(770580, 0, 19373, 1, 1, 0),
(770581, 0, 19373, 1, 1, 0),
(770582, 0, 19373, 1, 1, 0),
(770583, 0, 19373, 1, 1, 0),
(770584, 0, 19373, 1, 1, 0),
(770585, 0, 19373, 1, 1, 0),
(770600, 0, 19373, 1, 1, 0),
(770601, 0, 19373, 1, 1, 0),
(770602, 0, 19373, 1, 1, 0),
(770700, 0, 19373, 1, 1, 0),
(770701, 0, 19373, 1, 1, 0),
(770702, 0, 19373, 1, 1, 0),
(770703, 0, 19373, 1, 1, 0),
(770704, 0, 19373, 1, 1, 0),
(770705, 0, 19373, 1, 1, 0),
(770706, 0, 19373, 1, 1, 0),
(770707, 0, 19373, 1, 1, 0),
(770708, 0, 19373, 1, 1, 0);

-- William Allerton, alive (WRM-043)
CREATE TEMPORARY TABLE `remix_story_770550` SELECT * FROM `creature_template` WHERE `entry` = 25385;
UPDATE `remix_story_770550` SET `entry` = 770550, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'William Allerton', `npcflag` = 3, `unit_flags` = 768, `dynamicflags` = 0, `flags_extra` = 2;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770550`;
DROP TEMPORARY TABLE `remix_story_770550`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770550, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25385;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES (770550, 0, 0, 0, 1, 0, 0, '');
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770550, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25385;
-- The cult's assassin sent for Allerton, in a Valiance tabard (WRM-043)
CREATE TEMPORARY TABLE `remix_story_770551` SELECT * FROM `creature_template` WHERE `entry` = 25605;
UPDATE `remix_story_770551` SET `entry` = 770551, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Cult Assassin', `subname` = 'Cult of the Damned';
INSERT INTO `creature_template` SELECT * FROM `remix_story_770551`;
DROP TEMPORARY TABLE `remix_story_770551`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770551, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25605;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770551, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 25605;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770551, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25605;
-- Unit S's captives at En'kilah (WRM-045)
CREATE TEMPORARY TABLE `remix_story_770552` SELECT * FROM `creature_template` WHERE `entry` = 25313;
UPDATE `remix_story_770552` SET `entry` = 770552, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Private Harker', `subname` = 'Unit S', `npcflag` = 1, `faction` = 35, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770552`;
DROP TEMPORARY TABLE `remix_story_770552`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770552, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25313;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES (770552, 0, 0, 8, 1, 0, 0, '');
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770552, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25313;
-- Private Dunn
CREATE TEMPORARY TABLE `remix_story_770553` SELECT * FROM `creature_template` WHERE `entry` = 25313;
UPDATE `remix_story_770553` SET `entry` = 770553, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Private Dunn', `subname` = 'Unit S', `npcflag` = 1, `faction` = 35, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770553`;
DROP TEMPORARY TABLE `remix_story_770553`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770553, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25313;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES (770553, 0, 0, 8, 1, 0, 0, '');
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770553, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25313;
-- Corporal Mabry
CREATE TEMPORARY TABLE `remix_story_770554` SELECT * FROM `creature_template` WHERE `entry` = 25313;
UPDATE `remix_story_770554` SET `entry` = 770554, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Corporal Mabry', `subname` = 'Unit S', `npcflag` = 1, `faction` = 35, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770554`;
DROP TEMPORARY TABLE `remix_story_770554`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770554, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25313;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES (770554, 0, 0, 8, 1, 0, 0, '');
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770554, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25313;
-- Private Sorrel
CREATE TEMPORARY TABLE `remix_story_770555` SELECT * FROM `creature_template` WHERE `entry` = 25313;
UPDATE `remix_story_770555` SET `entry` = 770555, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Private Sorrel', `subname` = 'Unit S', `npcflag` = 1, `faction` = 35, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770555`;
DROP TEMPORARY TABLE `remix_story_770555`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770555, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25313;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES (770555, 0, 0, 8, 1, 0, 0, '');
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770555, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25313;
-- The freed men of Unit S, at Death's Stand
CREATE TEMPORARY TABLE `remix_story_770556` SELECT * FROM `creature_template` WHERE `entry` = 25313;
UPDATE `remix_story_770556` SET `entry` = 770556, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Unit S Survivor', `subname` = NULL, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770556`;
DROP TEMPORARY TABLE `remix_story_770556`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770556, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25313;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770556, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 25313;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770556, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25313;
-- The men Hammerhill sent east, because the Timerunner warned him
CREATE TEMPORARY TABLE `remix_story_770557` SELECT * FROM `creature_template` WHERE `entry` = 25313;
UPDATE `remix_story_770557` SET `entry` = 770557, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Valiance Volunteer', `subname` = 'Sergeant Hammerhill''s', `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770557`;
DROP TEMPORARY TABLE `remix_story_770557`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770557, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25313;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770557, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 25313;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770557, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25313;
-- Vurenn's regiments, accepted at last (WRM-047)
CREATE TEMPORARY TABLE `remix_story_770558` SELECT * FROM `creature_template` WHERE `entry` = 25300;
UPDATE `remix_story_770558` SET `entry` = 770558, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Draenei Vanguard', `subname` = 'Harbinger Vurenn''s', `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770558`;
DROP TEMPORARY TABLE `remix_story_770558`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770558, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25300;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770558, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 25300;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770558, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25300;
-- Grunts on the collapsed sinkholes of Mightstone Quarry (the hands Saurfang sent)
CREATE TEMPORARY TABLE `remix_story_770570` SELECT * FROM `creature_template` WHERE `entry` = 25242;
UPDATE `remix_story_770570` SET `entry` = 770570, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Warsong Sapper', `subname` = NULL, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770570`;
DROP TEMPORARY TABLE `remix_story_770570`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770570, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25242;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770570, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 25242;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770570, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25242;
-- The garrison on the condemned coast (WRM-054)
CREATE TEMPORARY TABLE `remix_story_770571` SELECT * FROM `creature_template` WHERE `entry` = 25242;
UPDATE `remix_story_770571` SET `entry` = 770571, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Warsong Coast Guard', `subname` = NULL, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770571`;
DROP TEMPORARY TABLE `remix_story_770571`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770571, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 25242;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770571, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 25242;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770571, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 25242;
-- Two more tanks, patched from Mobu's spare plates
CREATE TEMPORARY TABLE `remix_story_770572` SELECT * FROM `creature_template` WHERE `entry` = 27103;
UPDATE `remix_story_770572` SET `entry` = 770572, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Horde Siege Tank', `subname` = NULL, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770572`;
DROP TEMPORARY TABLE `remix_story_770572`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770572, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 27103;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770572, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 27103;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770572, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 27103;
-- The Plains of Nasam's wounded, brought home
CREATE TEMPORARY TABLE `remix_story_770573` SELECT * FROM `creature_template` WHERE `entry` = 27106;
UPDATE `remix_story_770573` SET `entry` = 770573, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Recovering Warsong Warrior', `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770573`;
DROP TEMPORARY TABLE `remix_story_770573`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770573, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 27106;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES (770573, 0, 0, 1, 1, 0, 0, '');
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770573, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 27106;
-- The Plains of Nasam's wounded, brought home
CREATE TEMPORARY TABLE `remix_story_770574` SELECT * FROM `creature_template` WHERE `entry` = 27107;
UPDATE `remix_story_770574` SET `entry` = 770574, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Recovering Warsong Mage', `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770574`;
DROP TEMPORARY TABLE `remix_story_770574`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770574, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 27107;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES (770574, 0, 0, 1, 1, 0, 0, '');
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770574, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 27107;
-- The tanks rolling out together in The Plains of Nasam's scene
CREATE TEMPORARY TABLE `remix_story_770575` SELECT * FROM `creature_template` WHERE `entry` = 27103;
UPDATE `remix_story_770575` SET `entry` = 770575, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Horde Siege Tank', `subname` = NULL, `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770575`;
DROP TEMPORARY TABLE `remix_story_770575`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770575, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 27103;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770575, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 27103;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770575, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 27103;
-- The company Wyrmbane sends to Bolvar at Fordragon Hold, until he recalls it
CREATE TEMPORARY TABLE `remix_story_770590` SELECT * FROM `creature_template` WHERE `entry` = 27162;
UPDATE `remix_story_770590` SET `entry` = 770590, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = '7th Legion Sentinel', `subname` = 'Wintergarde''s company', `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770590`;
DROP TEMPORARY TABLE `remix_story_770590`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770590, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 27162;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770590, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 27162;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770590, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 27162;
-- One of the Infinite, watching the Timerunner atop Wyrmrest (a scene's)
CREATE TEMPORARY TABLE `remix_story_770591` SELECT * FROM `creature_template` WHERE `entry` = 27898;
UPDATE `remix_story_770591` SET `entry` = 770591, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Infinite Chrono-Magus', `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770591`;
DROP TEMPORARY TABLE `remix_story_770591`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770591, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 27898;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770591, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 27898;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770591, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 27898;
-- Moratari in her evening dress (the romance's scenes)
CREATE TEMPORARY TABLE `remix_story_770720` SELECT * FROM `creature_template` WHERE `entry` = 770013;
UPDATE `remix_story_770720` SET `entry` = 770720, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770720`;
DROP TEMPORARY TABLE `remix_story_770720`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES (770720, 0, 32755, 1, 1, 0);
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770720, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 770013;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770720, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 770013;
-- Moratari in her tent (the romance's scene)
CREATE TEMPORARY TABLE `remix_story_770721` SELECT * FROM `creature_template` WHERE `entry` = 770013;
UPDATE `remix_story_770721` SET `entry` = 770721, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770721`;
DROP TEMPORARY TABLE `remix_story_770721`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES (770721, 0, 32756, 1, 1, 0);
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770721, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 770013;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770721, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 770013;
-- Moratari in her true shape, atop Wyrmrest (a bronze drake: the bronze she was before the Infinite)
CREATE TEMPORARY TABLE `remix_story_770722` SELECT * FROM `creature_template` WHERE `entry` = 31696;
UPDATE `remix_story_770722` SET `entry` = 770722, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `name` = 'Moratari', `subname` = 'Infinite Dragonflight', `unit_flags` = 770;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770722`;
DROP TEMPORARY TABLE `remix_story_770722`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770722, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 31696;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770722, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 31696;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770722, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 31696;
-- The crocolisks on the sunny bank of the picnic's river (a scene's, never fought)
CREATE TEMPORARY TABLE `remix_story_770723` SELECT * FROM `creature_template` WHERE `entry` = 28002;
UPDATE `remix_story_770723` SET `entry` = 770723, `KillCredit1` = 0, `KillCredit2` = 0, `ScriptName` = '', `AIName` = '', `gossip_menu_id` = 0, `faction` = 35, `unit_flags` = 770, `lootid` = 0;
INSERT INTO `creature_template` SELECT * FROM `remix_story_770723`;
DROP TEMPORARY TABLE `remix_story_770723`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) SELECT 770723, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 28002;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) SELECT 770723, 0, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras` FROM `creature_template_addon` WHERE `entry` = 28002;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770723, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 28002;

DELETE FROM `creature` WHERE `guid` BETWEEN 7704330 AND 7704399;
DELETE FROM `creature_addon` WHERE `guid` BETWEEN 7704330 AND 7704399;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704330, 770550, 571, 1, 1, 0, 2768.00, 5339.90, 30.03, 3.050, 120, 0, 0, 'Wrath Remix: William Allerton, alive, Farshire Mine'),
(7704331, 770551, 571, 1, 1, 1, 2765.90, 5340.20, 30.03, 6.200, 30, 0, 0, 'Wrath Remix: the cult''s assassin over Allerton'),
(7704332, 770552, 571, 1, 1, 1, 3845.60, 3726.40, 47.40, 3.600, 120, 0, 0, 'Wrath Remix: Private Harker, captive, En''kilah'),
(7704333, 770553, 571, 1, 1, 1, 3847.80, 3729.60, 47.50, 3.600, 120, 0, 0, 'Wrath Remix: Private Dunn, captive, En''kilah'),
(7704334, 770554, 571, 1, 1, 1, 3836.40, 3728.20, 47.30, 0.300, 120, 0, 0, 'Wrath Remix: Corporal Mabry, captive, En''kilah'),
(7704335, 770555, 571, 1, 1, 1, 3843.00, 3721.00, 47.20, 1.600, 120, 0, 0, 'Wrath Remix: Private Sorrel, captive, En''kilah'),
(7704336, 770556, 571, 1, 1, 1, 3110.20, 3838.40, 22.85, 5.750, 120, 0, 0, 'Wrath Remix: Unit S, Death''s Stand'),
(7704337, 770556, 571, 1, 1, 1, 3117.60, 3839.20, 22.80, 3.400, 120, 0, 0, 'Wrath Remix: Unit S, Death''s Stand'),
(7704338, 770556, 571, 1, 1, 1, 3109.40, 3843.60, 22.80, 5.200, 120, 0, 0, 'Wrath Remix: Unit S, Death''s Stand'),
(7704339, 770556, 571, 1, 1, 1, 3117.90, 3846.20, 22.75, 3.900, 120, 0, 0, 'Wrath Remix: Unit S, Death''s Stand'),
(7704340, 770557, 571, 1, 1, 1, 3104.50, 3830.50, 23.20, 5.600, 120, 0, 0, 'Wrath Remix: volunteers, Death''s Stand'),
(7704341, 770557, 571, 1, 1, 1, 3120.60, 3830.40, 22.90, 4.200, 120, 0, 0, 'Wrath Remix: volunteers, Death''s Stand'),
(7704342, 770557, 571, 1, 1, 1, 3290.50, 3679.50, 32.55, 0.400, 120, 0, 0, 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(7704343, 770557, 571, 1, 1, 1, 3289.60, 3686.40, 32.55, 5.900, 120, 0, 0, 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(7704344, 770557, 571, 1, 1, 1, 3304.00, 3678.60, 32.55, 2.600, 120, 0, 0, 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(7704345, 770558, 571, 1, 1, 0, 2119.80, 5303.20, 32.86, 3.200, 120, 0, 0, 'Wrath Remix: Vurenn''s vanguard, Valiance Keep''s barracks'),
(7704346, 770558, 571, 1, 1, 0, 2120.60, 5306.00, 32.86, 3.200, 120, 0, 0, 'Wrath Remix: Vurenn''s vanguard, Valiance Keep''s barracks'),
(7704347, 770558, 571, 1, 1, 0, 2119.90, 5308.60, 32.86, 3.200, 120, 0, 0, 'Wrath Remix: Vurenn''s vanguard, Valiance Keep''s barracks'),
(7704360, 770570, 571, 1, 1, 1, 2660.50, 6175.00, 39.00, 3.900, 120, 0, 0, 'Wrath Remix: a sapper on the southern sinkhole, Mightstone Quarry'),
(7704361, 770570, 571, 1, 1, 1, 2719.50, 6024.50, 31.30, 3.900, 120, 0, 0, 'Wrath Remix: a sapper on the eastern sinkhole, Mightstone Quarry'),
(7704362, 770570, 571, 1, 1, 1, 2881.50, 6279.50, 60.90, 3.900, 120, 0, 0, 'Wrath Remix: a sapper on the western sinkhole, Mightstone Quarry'),
(7704363, 770570, 571, 1, 1, 1, 2965.50, 6191.00, 62.10, 3.900, 120, 0, 0, 'Wrath Remix: a sapper on the northern sinkhole, Mightstone Quarry'),
(7704364, 770572, 571, 1, 1, 0, 2795.00, 6747.00, 7.60, 5.800, 120, 0, 0, 'Wrath Remix: a spare tank, the Coast of Echoes'),
(7704365, 770572, 571, 1, 1, 0, 2782.50, 6757.00, 7.60, 5.800, 120, 0, 0, 'Wrath Remix: a spare tank, the Coast of Echoes'),
(7704366, 770571, 571, 1, 1, 1, 2826.00, 6705.00, 10.80, 2.700, 120, 0, 0, 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(7704367, 770571, 571, 1, 1, 1, 2829.00, 6716.00, 10.80, 2.700, 120, 0, 0, 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(7704368, 770571, 571, 1, 1, 1, 2823.00, 6722.00, 10.50, 2.400, 120, 0, 0, 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(7704369, 770573, 571, 1, 1, 1, 2812.00, 6740.00, 9.80, 4.700, 120, 0, 0, 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(7704370, 770574, 571, 1, 1, 1, 2815.20, 6737.20, 10.00, 4.200, 120, 0, 0, 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(7704371, 770573, 571, 1, 1, 1, 2809.20, 6736.20, 9.80, 5.200, 120, 0, 0, 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(7704384, 770001, 571, 1, 1, 0, 3225.20, -730.90, 168.10, 2.510, 120, 0, 0, 'Wrath Remix: Moratari beside Middleton, Venomspite'),
(7704380, 770590, 571, 1, 1, 1, 4690.50, 1504.00, 261.00, 0.460, 120, 0, 0, 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(7704381, 770590, 571, 1, 1, 1, 4692.00, 1500.50, 261.00, 0.460, 120, 0, 0, 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(7704382, 770590, 571, 1, 1, 1, 4687.50, 1501.50, 260.80, 0.460, 120, 0, 0, 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(7704383, 770590, 571, 1, 1, 1, 4691.30, 1502.30, 261.00, 0.460, 120, 0, 0, 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(7704385, 770001, 571, 1, 1, 0, 3106.50, 3839.50, 22.80, 0.470, 120, 0, 0, 'Wrath Remix: Moratari at Death''s Stand while Forged Orders is in hand');
-- Who is seen (type 30, a spawn's own conditions by its guid): this file's spawns, and the game's that
-- some Timerunners no longer see. Quest states: 1 not taken, 2 objectives done, 8 in progress, 64 turned in.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND (`SourceId` BETWEEN 7704330 AND 7704399 OR `SourceId` IN (99763, 115989));
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(30, 0, 770550, 7704330, 0, 47, 0, 77043, 74, 0, 0, 0, 0, '', 'Wrath Remix: William Allerton, alive, Farshire Mine'),
(30, 0, 770550, 7704330, 0, 8, 0, 77048, 0, 0, 1, 0, 0, '', 'Wrath Remix: William Allerton, alive, Farshire Mine'),
(30, 0, 770550, 7704330, 1, 47, 0, 77043, 74, 0, 0, 0, 0, '', 'Wrath Remix: William Allerton, alive, Farshire Mine'),
(30, 0, 770550, 7704330, 1, 47, 0, 11599, 10, 0, 0, 0, 0, '', 'Wrath Remix: William Allerton, alive, Farshire Mine'),
(30, 0, 770551, 7704331, 0, 47, 0, 77043, 8, 0, 0, 0, 0, '', 'Wrath Remix: the cult''s assassin over Allerton'),
(30, 0, 770552, 7704332, 0, 47, 0, 77045, 8, 0, 0, 0, 0, '', 'Wrath Remix: Private Harker, captive, En''kilah'),
(30, 0, 770553, 7704333, 0, 47, 0, 77045, 8, 0, 0, 0, 0, '', 'Wrath Remix: Private Dunn, captive, En''kilah'),
(30, 0, 770554, 7704334, 0, 47, 0, 77045, 8, 0, 0, 0, 0, '', 'Wrath Remix: Corporal Mabry, captive, En''kilah'),
(30, 0, 770555, 7704335, 0, 47, 0, 77045, 8, 0, 0, 0, 0, '', 'Wrath Remix: Private Sorrel, captive, En''kilah'),
(30, 0, 770556, 7704336, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770556, 7704336, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770556, 7704337, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770556, 7704337, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770556, 7704338, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770556, 7704338, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770556, 7704339, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770556, 7704339, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: Unit S, Death''s Stand'),
(30, 0, 770557, 7704340, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: volunteers, Death''s Stand'),
(30, 0, 770557, 7704340, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: volunteers, Death''s Stand'),
(30, 0, 770557, 7704341, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: volunteers, Death''s Stand'),
(30, 0, 770557, 7704341, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: volunteers, Death''s Stand'),
(30, 0, 770557, 7704342, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(30, 0, 770557, 7704342, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(30, 0, 770557, 7704343, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(30, 0, 770557, 7704343, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(30, 0, 770557, 7704344, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(30, 0, 770557, 7704344, 0, 8, 0, 77049, 0, 0, 1, 0, 0, '', 'Wrath Remix: volunteers holding the Wailing Ziggurat'),
(30, 0, 770558, 7704345, 0, 8, 0, 77047, 0, 0, 0, 0, 0, '', 'Wrath Remix: Vurenn''s vanguard, Valiance Keep''s barracks'),
(30, 0, 770558, 7704346, 0, 8, 0, 77047, 0, 0, 0, 0, 0, '', 'Wrath Remix: Vurenn''s vanguard, Valiance Keep''s barracks'),
(30, 0, 770558, 7704347, 0, 8, 0, 77047, 0, 0, 0, 0, 0, '', 'Wrath Remix: Vurenn''s vanguard, Valiance Keep''s barracks'),
(30, 0, 770570, 7704360, 0, 8, 0, 11608, 0, 0, 0, 0, 0, '', 'Wrath Remix: a sapper on the southern sinkhole, Mightstone Quarry'),
(30, 0, 770570, 7704361, 0, 8, 0, 11608, 0, 0, 0, 0, 0, '', 'Wrath Remix: a sapper on the eastern sinkhole, Mightstone Quarry'),
(30, 0, 770570, 7704362, 0, 8, 0, 11608, 0, 0, 0, 0, 0, '', 'Wrath Remix: a sapper on the western sinkhole, Mightstone Quarry'),
(30, 0, 770570, 7704363, 0, 8, 0, 11608, 0, 0, 0, 0, 0, '', 'Wrath Remix: a sapper on the northern sinkhole, Mightstone Quarry'),
(30, 0, 770572, 7704364, 0, 8, 0, 11651, 0, 0, 0, 0, 0, '', 'Wrath Remix: a spare tank, the Coast of Echoes'),
(30, 0, 770572, 7704364, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: a spare tank, the Coast of Echoes'),
(30, 0, 770572, 7704365, 0, 8, 0, 11651, 0, 0, 0, 0, 0, '', 'Wrath Remix: a spare tank, the Coast of Echoes'),
(30, 0, 770572, 7704365, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: a spare tank, the Coast of Echoes'),
(30, 0, 770571, 7704366, 0, 8, 0, 77054, 0, 0, 0, 0, 0, '', 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(30, 0, 770571, 7704366, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(30, 0, 770571, 7704367, 0, 8, 0, 77054, 0, 0, 0, 0, 0, '', 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(30, 0, 770571, 7704367, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(30, 0, 770571, 7704368, 0, 8, 0, 77054, 0, 0, 0, 0, 0, '', 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(30, 0, 770571, 7704368, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: the coast''s garrison, the Coast of Echoes'),
(30, 0, 770573, 7704369, 0, 8, 0, 11652, 0, 0, 0, 0, 0, '', 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(30, 0, 770573, 7704369, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(30, 0, 770574, 7704370, 0, 8, 0, 11652, 0, 0, 0, 0, 0, '', 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(30, 0, 770574, 7704370, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(30, 0, 770573, 7704371, 0, 8, 0, 11652, 0, 0, 0, 0, 0, '', 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(30, 0, 770573, 7704371, 0, 8, 0, 77230, 0, 0, 1, 0, 0, '', 'Wrath Remix: the plains'' wounded, recovering by Elder Mootoo'),
(30, 0, 770001, 7704384, 0, 8, 0, 12218, 0, 0, 0, 0, 0, '', 'Wrath Remix: Moratari beside Middleton, Venomspite'),
(30, 0, 770001, 7704384, 0, 8, 0, 12221, 0, 0, 1, 0, 0, '', 'Wrath Remix: Moratari beside Middleton, Venomspite'),
(30, 0, 770590, 7704380, 0, 8, 0, 12311, 0, 0, 0, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770590, 7704380, 0, 8, 0, 77201, 0, 0, 1, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770590, 7704381, 0, 8, 0, 12311, 0, 0, 0, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770590, 7704381, 0, 8, 0, 77201, 0, 0, 1, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770590, 7704382, 0, 8, 0, 12311, 0, 0, 0, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770590, 7704382, 0, 8, 0, 77201, 0, 0, 1, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770590, 7704383, 0, 8, 0, 12311, 0, 0, 0, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770590, 7704383, 0, 8, 0, 77201, 0, 0, 1, 0, 0, '', 'Wrath Remix: Wintergarde''s company at Fordragon Hold'),
(30, 0, 770001, 7704385, 0, 47, 0, 77049, 10, 0, 0, 0, 0, '', 'Wrath Remix: Moratari at Death''s Stand while Forged Orders is in hand'),
(30, 0, 25385, 99763, 0, 47, 0, 77043, 1, 0, 0, 0, 0, '', 'Wrath Remix: Allerton''s corpse, unless he was saved'),
(30, 0, 25301, 115989, 0, 8, 0, 12019, 0, 0, 1, 0, 0, '', 'Wrath Remix: Counselor Talbot, gone after Last Rites');

DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 770100 AND 770199;
DELETE FROM `gameobject` WHERE `guid` BETWEEN 7705300 AND 7705399;
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES
(770100, 5, 7194, 'Moratari''s Tent', '', '', '', 1.0, '', '', 0),
(770101, 5, 159, 'Rug', '', '', '', 1.0, '', '', 0),
(770102, 5, 5914, 'Cushions', '', '', '', 1.0, '', '', 0),
(770103, 5, 6644, 'Candle', '', '', '', 1.0, '', '', 0),
(770104, 5, 6038, 'Lantern', '', '', '', 1.0, '', '', 0),
(770105, 5, 194, 'Brazier', '', '', '', 1.0, '', '', 0);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `ScriptName`, `VerifiedBuild`, `Comment`) VALUES
(7705300, 770100, 571, 0, 0, 1, 32769, 6413.00, 1853.00, 508.60, 2.5703, 0, 0, 0.959473, 0.281799, 300, 100, 1, '', 0, 'Wrath Remix: Moratari''s tent, the Bazaar'),
(7705301, 770101, 571, 0, 0, 1, 32769, 6413.42, 1852.73, 508.62, 2.5703, 0, 0, 0.959473, 0.281799, 300, 100, 1, '', 0, 'Wrath Remix: her tent''s rug'),
(7705302, 770102, 571, 0, 0, 1, 32769, 6415.32, 1850.32, 508.62, 2.8703, 0, 0, 0.990811, 0.135253, 300, 100, 1, '', 0, 'Wrath Remix: cushions in her tent'),
(7705303, 770102, 571, 0, 0, 1, 32769, 6416.57, 1851.89, 508.62, 2.1703, 0, 0, 0.884363, 0.466800, 300, 100, 1, '', 0, 'Wrath Remix: cushions in her tent'),
(7705304, 770102, 571, 0, 0, 1, 32769, 6416.59, 1853.78, 508.62, 3.7703, 0, 0, 0.951003, -0.309181, 300, 100, 1, '', 0, 'Wrath Remix: cushions in her tent'),
(7705305, 770103, 571, 0, 0, 1, 32769, 6415.24, 1848.71, 508.62, 2.5703, 0, 0, 0.959473, 0.281799, 300, 100, 1, '', 0, 'Wrath Remix: a candle in her tent'),
(7705306, 770103, 571, 0, 0, 1, 32769, 6417.89, 1852.47, 508.62, 2.5703, 0, 0, 0.959473, 0.281799, 300, 100, 1, '', 0, 'Wrath Remix: a candle in her tent'),
(7705307, 770103, 571, 0, 0, 1, 32769, 6413.00, 1856.33, 508.62, 2.5703, 0, 0, 0.959473, 0.281799, 300, 100, 1, '', 0, 'Wrath Remix: a candle in her tent'),
(7705308, 770105, 571, 0, 0, 1, 32769, 6410.98, 1850.97, 508.62, 2.5703, 0, 0, 0.959473, 0.281799, 300, 100, 1, '', 0, 'Wrath Remix: her tent''s brazier'),
(7705309, 770104, 571, 0, 0, 1, 32769, 6408.31, 1857.91, 508.60, 2.5703, 0, 0, 0.959473, 0.281799, 300, 100, 1, '', 0, 'Wrath Remix: the lamp by her tent''s door');

DELETE FROM `quest_template` WHERE `ID` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `quest_template_addon` WHERE `ID` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `quest_offer_reward` WHERE `ID` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `quest_request_items` WHERE `ID` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `creature_queststarter` WHERE `quest` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `creature_questender` WHERE `quest` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `remix_departure` WHERE `quest` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `remix_bridge` WHERE `quest` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
DELETE FROM `remix_quest_reward` WHERE `quest` IN (77041, 77042, 77043, 77044, 77045, 77046, 77047, 77050, 77051, 77054, 77056, 77223, 77236, 77234, 77235, 77048, 77049, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`, `AllowableRaces`, `StartItem`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`, `ObjectiveText4`, `RequiredItemId1`, `RequiredItemCount1`, `VerifiedBuild`) VALUES
(77041, 2, -1, 10, 3537, 5, 0, 0, 1101, 0, 'A Word in the General''s Ear', 'Warn General Arlos and Sergeant Hammerhill of what is coming to Valiance Keep, without telling them how you know.', 'You remember this week, don''t you? The crawlers on the beach. The flyers over the inner wall. And on the third night, the ground opening under the western ridge.$B$BThis time, they can be ready. Tell the general in the barracks, and the sergeant at the barricade. Not how you know, $N: no one in this year may learn that. Say your scouts saw worm-trails on the ridge.$B$BAnd mind the counselor at the general''s elbow. Tell him nothing you would not tell the Scourge.', 'Return to Moratari.', 770530, 1, 770531, 1, 0, 0, 0, 0, 'General Arlos warned', 'Sergeant Hammerhill warned', '', '', 0, 0, 0),
(77042, 2, -1, 10, 3537, 5, 0, 0, 1101, 0, 'The Fourth Sinkhole', 'Slay 6 Cultist Necrolytes at the northern sinkhole, then go with Moratari to the dunes behind the beach line.', 'Eternus told you there was a fourth. It opens under the dunes behind the beach, the same night as the others, and what comes out of it reaches the docks before anyone can sound a horn.$B$BIt has not opened yet. The worms are still digging, and the cult''s necrolytes at the northern sinkhole are feeding them, chanting the dead awake under the sand.$B$BKill the necrolytes. Then come with me to the dunes, and I will show you what can be done with wooden supports and a little time.', 'Return to Moratari.', 25651, 6, 770532, 1, 0, 0, 0, 0, '', 'The fourth sinkhole collapsed', '', '', 0, 0, 0),
(77043, 2, -1, 10, 3537, 5, 0, 0, 1101, 0, 'Not Yet Late', 'Reach William Allerton in the Farshire Mine before the cult''s assassin does.', 'Leryssa is about to ask you to find a family friend of hers, William Allerton, at the Farshire mine. Say yes. Then run.$B$BThe first time, you found him on the floor of that mine with his throat cut, and not a claw mark on him. A man in a Valiance tabard got there an hour before you did.$B$BWilliam knows where they sent Thassarian. That is why he died. Today, I would rather he didn''t.', 'Speak with William Allerton.', 770551, 1, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0),
(77044, 2, -1, 10, 3537, 5, 0, 0, 1101, 0, 'Named for No Town', 'Ask Old Man Colburn at the inn and Private Brau in the barracks jail about Unit S, then tell Leryssa what you have learned.', 'I saw Thassarian in the enlistment line, $c, plain as I see you. Dead all these years, and there he stood, signing his name.$B$BThe next day they put him in charge of something called Unit S and sent him east. Every other unit in this expedition is named after a town. I started asking why. You''ve seen where that got me.$B$BOld Colburn at the inn knows more about this army than the army does; ask him. And there''s a deserter in the barracks jail, Brau, who was in Unit S before he ran. Ask him who signed the order.$B$BThen tell Leryssa. She deserves to know where her brother went.', 'Return to Leryssa at the Valiance Keep inn.', 770533, 1, 770534, 1, 0, 0, 0, 0, 'Old Man Colburn asked about Unit S', 'Private Brau asked who signed the order', '', '', 0, 0, 0),
(77045, 2, -1, 10, 3537, 5, 0, 0, 1101, 0, 'No One Left Behind', 'Free Private Harker, Private Dunn, Corporal Mabry and Private Sorrel of Unit S, held in the Temple City of En''kilah, then return to Corporal Venn at Death''s Stand.', 'Venn has written off the rest of Unit S. Most of them are dead. Four are not.$B$BThe cult took them alive, to the necromancers'' yard in the Temple City of En''kilah, north of here. No one ever goes looking for them, and within the week the cult has four new servants who used to be Stormwind boys.$B$BGo and get them, $N. Tell them Valiance Keep sent you. It is kinder than the truth, and they will believe it.', 'Return to Corporal Venn at Death''s Stand.', 770535, 1, 770536, 1, 770537, 1, 770538, 1, 'Private Harker freed', 'Private Dunn freed', 'Corporal Mabry freed', 'Private Sorrel freed', 0, 0, 0),
(77046, 2, -1, 10, 3537, 5, 0, 0, 1101, 0, 'Before She Gets Hurt', 'Warn Leryssa, and ask Vindicator Yaala to watch over her, at Valiance Keep''s inn. Moratari will take you there and back.', '''We must finish this before she gets hurt.'' He is right to be afraid, $N. In the record, the counselor''s men come for Leryssa within the week, and she is taken to the top of Naxxanar as an offering.$B$BI can fold the road to Valiance Keep and back. Warn her. Ask the draenei vindicator at the inn to watch over her. And then... we will see what the hour allows.', 'Return to Moratari.', 770539, 1, 770540, 1, 0, 0, 0, 0, 'Leryssa warned', 'Vindicator Yaala asked to watch over Leryssa', '', '', 0, 0, 0),
(77047, 2, -1, 10, 3537, 5, 0, 0, 1101, 0, 'The Keep Holds', 'Speak with General Arlos in Valiance Keep''s barracks.', 'Talbot is dead, and his hold on the general''s mind died with him. For the first time since he landed, Arlos is himself, and he has asked for you.$B$BCome; I will fold the road.', 'Speak with General Arlos.', 0, 0, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0),
(77050, 2, -1, 10, 3537, 5, 0, 0, 690, 0, 'Beneath the Floor', 'Warn Garrosh Hellscream, High Overlord Saurfang and the Warsong Captain on the south wall of what is coming to Warsong Hold, without telling them how you know.', 'You remember this hold''s first week, $N: what came up through the floor of this ''impregnable fortress'', and what dropped onto the south wall every hour after.$B$BThis time the Horde can be ready for both. Tell Garrosh; he will scoff. Tell Saurfang; he will listen, and tell no one he did. Tell the captain on the wall to put his marksmen up.$B$BBut not how you know. No one in this year can ever learn that. Say you have a bad feeling about the quarry. Orcs have gone to war on less.', 'Return to Moratari.', 770560, 1, 770561, 1, 770562, 1, 0, 0, 'Garrosh Hellscream warned', 'High Overlord Saurfang warned', 'The Warsong Captain warned', '', 0, 0, 0),
(77051, 2, -1, 10, 3537, 5, 0, 0, 690, 0, 'Hands for Holgoth', 'Speak with Quartermaster Holgoth in Warsong Hold.', 'Saurfang promised Holgoth hands by nightfall. Yours are the first to arrive.$B$BThe quartermaster''s munitions are out in the quarry, and he has a plan for the nerubians'' sinkholes. In the record, those sinkholes are still open when the floor gives way. Let us close them before it does.', 'Speak with Quartermaster Holgoth.', 0, 0, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0),
(77054, 2, -1, 10, 3537, 5, 0, 0, 690, 0, 'The Condemned Coast', 'Slay 6 Kvaldir Mist Lords in the mist over Garrosh''s Landing, and ask Gorge to keep a garrison on the coast.', 'This coast was condemned the day the mist came, and only Gorge, a goblin and six tanks stayed. When the tanks leave for the plains, the Kvaldir come out of the mist behind them, and there is no one left on this beach to stop them.$B$BThin the Mist Lords on the landing. Then tell Gorge to ask Saurfang for a garrison. Hellscream condemned the coast; he never said no one could guard it.', 'Return to Moratari.', 25496, 6, 770563, 1, 0, 0, 0, 0, '', 'Gorge asked to hold the coast', '', '', 0, 0, 0),
(77056, 2, -1, 10, 3537, 5, 0, 0, 690, 0, 'Shipping Lanes', 'Speak with High Overlord Saurfang in Warsong Hold.', 'Kel''Thuzad. You saw him over the plains with your own eyes, and Garrosh has had an hour to think about it, which for Garrosh is a long time. You can guess what he has decided.$B$BSaurfang will talk him out of it, barely. He always has. But today there is a garrison on Garrosh''s Landing, and I think the argument may end differently.$B$BCome, $N. I would not miss this one.', 'Speak with High Overlord Saurfang.', 0, 0, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0),
(77223, 2, -1, 20, 65, 5, 0, 0, 1101, 0, 'The Second Sky', 'Warn Commander Lynore Windstryke, Highlord Leoric Von Zeldig and Gryphon Commander Urik of what Naxxramas will do next.', 'The lower village is lost. Naxxramas fell on it before either of us set foot here, and that I cannot undo, $N.$B$BBut I know where the next blows land. The risen gryphon riders will dive on the archers posted over the town square. The dead will come up the mine road. And the roost that should have fallen is still standing, thanks to Eternus, but nobody has mended the beam. When it goes, it goes with the gryphons in it.$B$BTell the commander, the highlord and the gryphon commander. A veteran''s eye, a hunch, a rumor from the barracks: whatever they will believe.', 'Return to Moratari.', 770580, 1, 770581, 1, 770582, 1, 0, 0, 'Commander Lynore Windstryke warned', 'Highlord Leoric Von Zeldig warned', 'Gryphon Commander Urik warned', '', 0, 0, 0),
(77236, 2, -1, 20, 65, 5, 0, 0, 690, 0, 'Eyes and Ears', 'Send a word to High Overlord Saurfang with Messenger Torvus at Agmar''s Hammer.', 'Messenger Torvus carries Saurfang''s letters, the ones Agmar is not meant to read. Saurfang has sent his son to command the Horde at the Wrathgate, and you know how the son''s story ends.$B$BSend a word back with Torvus. Not what you know, $N. What any old soldier might say to a father, if he had the nerve. Let Saurfang read it, and decide.', 'Speak with Messenger Torvus.', 770583, 1, 0, 0, 0, 0, 0, 0, 'A word sent with Messenger Torvus', '', '', '', 0, 0, 0),
(77234, 2, -1, 20, 65, 5, 0, 0, 690, 0, 'Before the Second Wave', 'Slay 8 Anub''ar Cultists at Icemist Village, then speak with Doctor Sintar Malefious at Agmar''s Hammer.', 'The Anub''ar razed Icemist, and its taunka are refugees now. Nothing I can do will give them back their village.$B$BBut I can take something from the Anub''ar. Their cultists are on the ruins, pouring their power into the blightbeasts. The Horde''s wind riders will bring down the beasts you can see. In the record, the cultists raise a second wave after them, and that one reaches the Wrathgate.$B$BKill the cultists before they finish. Then come back to Agmar''s Hammer: Doctor Malefious is waiting on a shipment, and I want you to see it before he does.', 'Speak with Doctor Sintar Malefious at Agmar''s Hammer.', 26319, 8, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0),
(77235, 2, -1, 20, 65, 5, 0, 0, 690, 0, 'A Careful Inventory', 'Ask Deathguard Molder and Junior Apothecary Lawrence at Venomspite about the blight''s shipments, then return to Moratari.', 'Before you carry Middleton''s package to Agmar''s Hammer, I want you to take an inventory, $N.$B$BDeathguard Molder asked for the blight spreaders and was told they were for ''special missions''. Junior Apothecary Lawrence signs for every crate that leaves Venomspite. Ask them, the way a courier making conversation would.$B$BAnd whatever you learn stays with you. No one in this year can hear it from you: not Agmar, not the Warchief, not anyone.', 'Return to Moratari.', 770584, 1, 770585, 1, 0, 0, 0, 0, 'Deathguard Molder asked about the blight spreaders', 'Junior Apothecary Lawrence asked about the shipments', '', '', 0, 0, 0),
(77048, 2, -1, 20, 3537, 5, 0, 0, 1101, 0, 'Lost at Sea', 'Persuade William Allerton, in the Farshire Mine, to sail home under another name. Moratari will take you there and back.', 'I need your help to put something back, $N, and you are not going to like it.$B$BWilliam Allerton was supposed to die in the Farshire mine. He did not, because of us. Now he is alive in the Borean Tundra, writing letters to Stormwind about Unit S, about the counselor, about a hero with a strange way of knowing where to be. Every letter pulls the war somewhere it never went.$B$BHe cannot stay. Not here, and not under his own name. But he does not have to die. I will not ask that of you, and I would not do it myself. Talk to him.', 'Return to Moratari.', 770600, 1, 0, 0, 0, 0, 0, 0, 'William Allerton persuaded to sail home', '', '', '', 0, 0, 0),
(77049, 2, -1, 20, 3537, 5, 0, 0, 1101, 0, 'Forged Orders', 'Give Corporal Venn at Death''s Stand the orders that send Unit S''s survivors and Hammerhill''s volunteers home.', 'History lost Unit S on the beach where they landed, and never went looking. If four of them walk back into Valiance Keep with the counselor''s name on their lips, the questions the Expedition asks next are ones history never asked.$B$BThey are not going to die for that. I will not allow it. But they can go home, quietly: I have written orders sending them to Stormwind''s harbor, with Hammerhill''s volunteers to see them aboard. They carry the general''s seal. The counselor kept a copy in his desk, and he will not be needing it.$B$BTake them to Corporal Venn. He will understand more than you think.', 'Return to Moratari.', 770601, 1, 0, 0, 0, 0, 0, 0, 'Corporal Venn given the orders', '', '', '', 0, 0, 0),
(77230, 2, -1, 20, 3537, 5, 0, 0, 690, 0, 'The Record Keeps Warsong', 'Tell Gorge, on the Coast of Echoes, that the Warchief is calling every soldier who can walk back to Orgrimmar. Moratari will take you there and back.', 'Orgrimmar is under martial law, and the Warchief is calling every soldier who can walk back to the city. In the record, the coast at Garrosh''s Landing is condemned again by the end of the week: no garrison, no spare tanks, no one on the beach but Gorge, a goblin and the mist.$B$BThere is a garrison there now, because of us. If it stays while the rest of the Horde goes home, someone will ask why, and I would rather nobody did, $N.$B$BGo and tell Gorge. He will take it badly. He takes everything badly.', 'Return to Moratari.', 770602, 1, 0, 0, 0, 0, 0, 0, 'Gorge told of the recall', '', '', '', 0, 0, 0),
(77901, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'A Cup of Something Hot', 'Sit with Moratari, and share her tea.', 'I have been taking notes on you since the landing, $N: how you fight, what you eat, which way you turn when something growls. It occurs to me that you have none on me.$B$BYou ask me where the Scourge will be, and when, and how many. Sensible questions. Nobody ever asks a dragon anything else.$B$BSit with me a while. I have tea. Every dragon who keeps time keeps tea; it is the one thing that tastes the same in every century.', 'Return to Moratari.', 770700, 1, 0, 0, 0, 0, 0, 0, 'Tea shared with Moratari', '', '', '', 0, 0, 0),
(77902, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'Shore Leave', 'Have a drink with Moratari at an inn in Dalaran.', 'Eternus says we are ahead of the record. Two days, perhaps three. She says it as if it were a problem.$B$BI say it is shore leave. There is an inn in Dalaran (in this year the city has only just arrived, and the floors are still settling) where nobody knows either of us, and the cider is better than it has any right to be.$B$BOne drink, $N. As friends. Mostly as friends.', 'Return to Moratari.', 770701, 1, 0, 0, 0, 0, 0, 0, 'A drink with Moratari', '', '', '', 0, 0, 0),
(77903, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'Dinner at Krasus'' Landing', 'Have dinner with Moratari at Krasus'' Landing in Dalaran.', 'I have a confession. I bought a dress.$B$BIn the Bazaar you can buy anything from any year. I tried on eleven. I have chosen between whole centuries with less fuss.$B$BThere is a landing on the edge of Dalaran named for Krasus, a dragon who sat on the Kirin Tor''s council for years in an elf''s shape, and hardly anyone knew. I have always thought he would understand me.$B$BHave dinner with me there, $N. Properly. Not as friends.', 'Return to Moratari.', 770702, 1, 0, 0, 0, 0, 0, 0, 'Dinner at Krasus'' Landing', '', '', '', 0, 0, 0),
(77904, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'The View from Wyrmrest', 'Go with Moratari to the top of Wyrmrest Temple at night.', 'You were on Wyrmrest today, among the Accord''s dragons, and I kept my distance. Dragons always know another dragon, whatever shape she wears, and Chromie has met enough of the Infinite this week.$B$BBut there is something I want to show you there, $N, from the top of the temple, at night, when the Accord is asleep. Come with me.', 'Return to Moratari.', 770703, 1, 0, 0, 0, 0, 0, 0, 'The view from Wyrmrest', '', '', '', 0, 0, 0),
(77905, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'What Eternus Left Out', 'Stay with Moratari a while.', 'I need to sit down.$B$B...She knew, $N. Eternus knew the war had to happen as it did, and she sent us to change it anyway, and she let me believe that every life we saved was a life kept.$B$BI do not know what I am anymore. A keeper of time who spent a month vandalizing it.$B$BSit with me a while. Please. You do not have to say anything.', 'Return to Moratari.', 770704, 1, 0, 0, 0, 0, 0, 0, 'Moratari comforted', '', '', '', 0, 0, 0),
(77906, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'On Bronze Wings', 'Fly with Moratari from Dalaran to Wyrmrest Temple, on her back.', 'You have flown on gryphons, and wyverns, and the Accord''s drakes, and every one of them was carrying you somewhere for the war.$B$BI am offering something else, $N: my back, the sky over Dalaran, and the long way down to Wyrmrest, with nowhere we have to be when we land.$B$BI have never carried anyone before. I find I would like to.', 'Return to Moratari.', 770705, 1, 0, 0, 0, 0, 0, 0, 'A flight on Moratari''s back', '', '', '', 0, 0, 0),
(77907, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'An Adventure of Our Own', 'Spend an afternoon with Moratari by a river in Sholazar Basin.', 'I have followed you through a great many other people''s stories. Today I would like one of our own.$B$BThere is a river below Nesingwary''s camp, warm and slow, with one good bank in the sun. There are also crocolisks, who believe that bank is theirs. I have brought a blanket and a basket. Shall we discuss it with them?', 'Return to Moratari.', 770706, 1, 0, 0, 0, 0, 0, 0, 'An afternoon by the river', '', '', '', 0, 0, 0),
(77908, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'The Lamp That Is Always Lit', 'Spend the night in Moratari''s tent at the Bazaar.', 'I have a tent at the Bazaar. You have walked past it a hundred times: the one with the lamp that is always lit.$B$BNo one goes in. Not Eternus, when she was there; not the porters who sweep the paths. It is the only place in any year that is only mine.$B$BI would like it to be ours, tonight. Leave your armor at the door, $N. Nothing in there will need a sword.', 'Return to Moratari.', 770707, 1, 0, 0, 0, 0, 0, 0, 'A night in Moratari''s tent', '', '', '', 0, 0, 0),
(77909, 2, -1, 10, 0, 5, 0, 0, 0, 0, 'Whatever Comes After', 'Walk with Moratari to the edge of the camp, and hear her promise.', 'Icecrown. The end of the war is up that glacier, and after the end you go home, to your own year. I cannot follow you there, $N. One of my kind who walks out of her own time does not come back, and someone has to stay behind and send you home.$B$BI am not sad. I am... a little sad.$B$BWalk with me to the edge of the camp. I want to make you a promise, and I would rather not make it in front of Tirion.', 'Return to Moratari.', 770708, 1, 0, 0, 0, 0, 0, 0, 'Moratari''s promise', '', '', '', 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `NextQuestID`, `ExclusiveGroup`) VALUES
(77041, 11672, 0, 0),
(77042, 11897, 0, 0),
(77043, 11927, 0, 0),
(77044, 77043, 0, 0),
(77045, 77006, 0, 0),
(77046, 12088, 0, 0),
(77047, 12019, 0, 0),
(77050, 0, 0, 0),
(77051, 11598, 0, 0),
(77054, 11651, 0, 0),
(77056, 11652, 0, 0),
(77223, 12237, 0, 0),
(77236, 12034, 0, 0),
(77234, 12036, 0, 0),
(77235, 12218, 0, 0),
(77048, 0, 0, 0),
(77049, 0, 0, 0),
(77230, 0, 0, 0),
(77901, 0, 0, 0),
(77902, 77901, 0, 0),
(77903, 77902, 0, 0),
(77904, 77903, 0, 0),
(77905, 77904, 0, 0),
(77906, 77905, 0, 0),
(77907, 77906, 0, 0),
(77908, 77907, 0, 0),
(77909, 77908, 0, 0);
INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES
(77041, 'The general did not believe you. The sergeant did. In my experience, sergeants are the most useful variable in any war.$B$BAnd you lie rather well, for an honest $c. I mean that kindly.', 0),
(77042, 'Then the docks stay quiet. Hammerhill will sleep through that night and never know why.', 0),
(77043, 'You... you''re not one of them? <William Allerton slides down the wall of the mine, shaking.>$B$BHe said he had orders for me from the inner hold. I took the paper from him, and he drew a knife.$B$BWhoever you are, thank you.', 0),
(77044, 'William''s alive? Oh, thank the Light. <Leryssa sits down, hard.>$B$BThe counselor. He''s at the general''s side every hour of the day, and he signed my brother''s death warrant.$B$BPlease, $N. Find Thassarian before they finish what they started.', 0),
(77045, 'Harker? Dunn? <Corporal Venn grabs the nearest man by the shoulders, laughing.> We gave you up for dead! I said the words over you myself!$B$BAnd Hammerhill''s sent volunteers up from the keep. Says the siege left him men to spare, for once. Remind me to buy that dwarf a barrel.$B$BI don''t know how you found them, $N, and I''m not going to ask.', 0),
(77046, 'She will not run, and Yaala will not sleep. Whether that is enough, we will know at the top of Naxxanar.$B$BBack to Thassarian, then.', 0),
(77047, '<General Arlos looks older than he did a week ago. He also looks awake.>$B$BCome in, $N. There is a great deal I need to say, and most of it is an apology.', 0),
(77050, 'Hands for the quartermaster, eyes on the plains, and marksmen on the wall before the next attack. Not bad, for a bad feeling.$B$BSaurfang has work for you now. Go and see him.', 0),
(77051, 'The High Overlord sent you? <Holgoth scratches his chin.> Huh. First time anybody at that map''s remembered this hold has a quartermaster.$B$BWell, you''re here now. Let''s not waste it.', 0),
(77054, 'Good. With a garrison on it, it will stay that way.$B$BNow think what a held beach is worth, $N, to an army whose ships have nowhere on this coast to land. Saurfang will. Give him a day.', 0),
(77056, '<High Overlord Saurfang glances at Hellscream across the war map.>$B$BYou brought him that name, $N. Stay, and hear what he means to do with it.', 0),
(77223, 'The commander believed you. The gryphon commander believed his birds. The highlord believed no one, and closed the road anyway.$B$BEternus will be pleased. So, I find, am I.', 0),
(77236, '<Messenger Torvus clasps your hand, and the note is gone into his glove.>$B$B<He raises his voice for anyone listening.> The Hammer stands strong, soldier! Warsong Hold will hear of it!$B$B<Under his breath.> It goes west with me tonight. What the High Overlord does with it is for him to decide.', 0),
(77234, 'Cultists, at Icemist? How very heroic. I''m sure Agmar will want a song.$B$B<Doctor Malefious looks you over.>$B$BStill, you went there and came back with all your limbs, which puts you ahead of everyone else I work with. I have an errand for you.', 0),
(77235, 'More blight than Agmar ever ordered, consigned to ''the Grand Apothecary''s special detachment''. Spreaders kept back for ''special missions''. And a Chief Plaguebringer who keeps saying ''the living'' when he means the Scourge.$B$BSay nothing, $N, to anyone. Eternus has a plan for the Wrathgate, and I think, now, I understand what it is for.', 0),
(77048, 'The Kraken sails at dawn, with a passenger the ledger has never heard of. In Westfall, a farmer called Will Allard will grow very good corn, and tell nobody where he learned to look over his shoulder.$B$BThank you, $N. That one I could not have done alone.', 0),
(77049, 'Then the record keeps Unit S on its beach, and Stormwind gets its sons back. Somewhere in the Old Town, a mother is going to open her door to a boy the army already wrote to her about.$B$BSome changes, $N, the war can keep, as long as it never hears of them.', 0),
(77230, 'Condemned again, as it was. The garrison sails for Orgrimmar with the spare tanks, and the wounded go with them. History has its coast back.$B$BI keep thinking of the war map, the day Hellscream gave way and did not stamp on anything. It was real, $N. For one afternoon, it was real.', 0),
(77901, 'Thank you, $N. I had forgotten what it is like to be asked about myself.$B$BAsk me something again sometime. I may have a better answer by then.', 0),
(77902, 'One drink, as promised. I made no promises about the rest of it.$B$BThank you, $N. I have not enjoyed an evening that much in... I was going to say a century. I think it may have been longer.', 0),
(77903, '<Moratari touches her lips, as if to make sure they are still hers.>$B$BI have changed history before, $N. I know exactly what it feels like.$B$BIt feels like that.$B$BI am keeping the dress.', 0),
(77904, 'I was so sure you would step back. I had a speech ready for it.$B$BWould you like to hear it? No? Good. It was a terrible speech.', 0),
(77905, 'Thank you for staying.$B$BTomorrow we start putting things back, one at a time. I will find a way to do it without losing anyone. I have to.$B$BFor now, I would like to sit here a little longer, with you, and not take a single note.', 0),
(77906, 'My wings ache, and I cannot stop smiling. I had forgotten that flying could be for nothing but the flying.$B$BNext time, we do not land.', 0),
(77907, 'Somewhere tomorrow, about noon, two crocolisks are going to be very confused.$B$BThank you, $N. I did not know I could still have a day like that.', 0),
(77908, '<Moratari is humming. She notices, stops, and then starts again.>$B$BFrom now on I walk with you. Everywhere. Let my posts stand empty and look mysterious without me.', 0),
(77909, '<Moratari brushes the frost from your shoulders, though there was hardly any.>$B$BNow. There is a king at the top of that glacier, and he has kept you waiting long enough. Shall we?', 0);
INSERT INTO `quest_request_items` (`ID`, `CompletionText`, `VerifiedBuild`) VALUES
(77041, 'Well? Did they listen?', 0),
(77042, 'Not yet? The worms will not wait for us.', 0),
(77043, '<William Allerton is pressed against the wall of the mine, staring at the knife.>', 0),
(77044, 'Did you find William? Is he...', 0),
(77045, 'From Valiance Keep? Tell me there''s more of you on the road.', 0),
(77046, 'What did she say?', 0),
(77050, 'How did they take it?', 0),
(77054, 'Is the landing quiet?', 0),
(77223, 'Did they listen?', 0),
(77234, '<Doctor Malefious does not look up.> You are standing in my light.', 0),
(77235, 'Well? What did they tell you?', 0),
(77048, 'Will he go?', 0),
(77049, 'Did he take them?', 0),
(77230, 'Did he take it badly?', 0),
(77901, 'The tea is in no hurry, $N, and neither am I.', 0),
(77902, 'I have already decided what I am having. That should tell you how long I have been thinking about this.', 0),
(77903, 'The dress is ready. I am nearly ready. Give me a moment to stop being nervous.', 0),
(77904, 'Not yet? That is all right. I am still working up my courage.', 0),
(77906, 'I have been stretching my wings all morning, and pretending I was not.', 0),
(77907, 'There is sand in the basket already. There is always sand in my baskets.', 0);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (770001, 77041), (770001, 77042), (770001, 77043), (770550, 77044), (770001, 77045), (770001, 77046), (770001, 77047), (770001, 77050), (770001, 77051), (770001, 77054), (770001, 77056), (770001, 77223), (770001, 77236), (770001, 77234), (770001, 77235), (770001, 77048), (770001, 77049), (770001, 77230), (770001, 77901), (770001, 77902), (770001, 77903), (770001, 77904), (770001, 77905), (770001, 77906), (770001, 77907), (770001, 77908), (770001, 77909);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (770001, 77041), (770001, 77042), (770550, 77043), (25251, 77044), (26187, 77045), (770001, 77046), (25250, 77047), (770001, 77050), (25327, 77051), (770001, 77054), (25256, 77056), (770001, 77223), (26649, 77236), (26505, 77234), (770001, 77235), (770001, 77048), (770001, 77049), (770001, 77230), (770001, 77901), (770001, 77902), (770001, 77903), (770001, 77904), (770001, 77905), (770001, 77906), (770001, 77907), (770001, 77908), (770001, 77909);
INSERT INTO `remix_departure` (`quest`, `map`, `x`, `y`, `z`, `o`) VALUES
(77046, 571, 2272.60, 5186.20, 20.38, 3.400),
(77047, 571, 2110.20, 5300.60, 34.09, 2.300),
(77048, 571, 2765.60, 5337.80, 30.03, 0.200),
(77049, 571, 3111.00, 3840.00, 22.85, 5.750),
(77230, 571, 2822.50, 6708.50, 10.80, 2.700);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES
(77046, 0, 0, 571, 3292.80, 3679.60, 32.55, 0.600, ''),
(77048, 0, 0, 571, 6394.00, 1866.00, 508.70, 1.570, ''),
(77049, 0, 0, 571, 6394.00, 1866.00, 508.70, 1.570, ''),
(77230, 0, 0, 571, 6394.00, 1866.00, 508.70, 1.570, '');
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES (77041, 800), (77042, 800), (77043, 800), (77044, 800), (77045, 800), (77046, 800), (77047, 1500), (77050, 800), (77051, 800), (77054, 800), (77056, 1500), (77223, 800), (77236, 800), (77234, 800), (77235, 800), (77048, 1000), (77049, 1000), (77230, 1000), (77901, 300), (77902, 300), (77903, 500), (77904, 300), (77905, 300), (77906, 500), (77907, 300), (77908, 500), (77909, 1000);

DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (11596, 11599, 11606, 11727, 11956, 12036, 12189, 12221, 12251, 77006, 77017, 77018, 77048, 77049, 77050, 77056, 77121, 77122, 77221, 77222, 77230, 77901, 77902, 77903, 77904, 77905, 77906, 77907, 77908, 77909);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 11596, 0, 0, 8, 0, 7784, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 11596 in the story'),
(19, 0, 11596, 0, 0, 8, 0, 8743, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 11596 in the story'),
(19, 0, 11596, 0, 0, 8, 0, 77050, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 11596 in the story'),
(19, 0, 11599, 0, 0, 47, 0, 77043, 74, 0, 0, 0, 0, '', 'Wrath Remix: quest 11599 in the story'),
(19, 0, 11606, 0, 0, 8, 0, 77051, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 11606 in the story'),
(19, 0, 11727, 0, 0, 8, 0, 77041, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 11727 in the story'),
(19, 0, 11956, 0, 0, 8, 0, 77046, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 11956 in the story'),
(19, 0, 12036, 0, 0, 8, 0, 77236, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 12036 in the story'),
(19, 0, 12189, 0, 0, 8, 0, 77234, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 12189 in the story'),
(19, 0, 12221, 0, 0, 8, 0, 77235, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 12221 in the story'),
(19, 0, 12251, 0, 0, 8, 0, 77223, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 12251 in the story'),
(19, 0, 77006, 0, 0, 8, 0, 77044, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77006 in the story'),
(19, 0, 77017, 0, 0, 8, 0, 77042, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77017 in the story'),
(19, 0, 77018, 0, 0, 8, 0, 11608, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77018 in the story'),
(19, 0, 77048, 0, 0, 8, 0, 77207, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77048 in the story'),
(19, 0, 77048, 0, 0, 8, 0, 77043, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77048 in the story'),
(19, 0, 77049, 0, 0, 8, 0, 77207, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77049 in the story'),
(19, 0, 77049, 0, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77049 in the story'),
(19, 0, 77050, 0, 0, 8, 0, 11585, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77050 in the story'),
(19, 0, 77050, 0, 1, 8, 0, 11586, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77050 in the story'),
(19, 0, 77056, 0, 0, 8, 0, 77054, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77056 in the story'),
(19, 0, 77121, 0, 0, 8, 0, 77047, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77121 in the story'),
(19, 0, 77122, 0, 0, 8, 0, 77056, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77122 in the story'),
(19, 0, 77221, 0, 0, 8, 0, 77207, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 1, 8, 0, 77048, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 1, 8, 0, 77049, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 2, 8, 0, 77048, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 2, 8, 0, 77045, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 3, 8, 0, 77043, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 3, 8, 0, 77049, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 4, 8, 0, 77043, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77221, 0, 4, 8, 0, 77045, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 77221 in the story'),
(19, 0, 77222, 0, 0, 8, 0, 77207, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 77222 in the story'),
(19, 0, 77222, 0, 1, 8, 0, 77230, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77222 in the story'),
(19, 0, 77222, 0, 2, 8, 0, 77054, 0, 0, 1, 0, 0, '', 'Wrath Remix: quest 77222 in the story'),
(19, 0, 77230, 0, 0, 8, 0, 77207, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77230 in the story'),
(19, 0, 77230, 0, 0, 8, 0, 13242, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77230 in the story'),
(19, 0, 77230, 0, 0, 8, 0, 77054, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77230 in the story'),
(19, 0, 77901, 0, 0, 8, 0, 11727, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77901 in the story'),
(19, 0, 77901, 0, 1, 8, 0, 11596, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77901 in the story'),
(19, 0, 77901, 0, 2, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77901 in the story'),
(19, 0, 77902, 0, 0, 8, 0, 77043, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77902 in the story'),
(19, 0, 77902, 0, 1, 8, 0, 77054, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77902 in the story'),
(19, 0, 77902, 0, 2, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77902 in the story'),
(19, 0, 77903, 0, 0, 8, 0, 77121, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77903 in the story'),
(19, 0, 77903, 0, 1, 8, 0, 77122, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77903 in the story'),
(19, 0, 77903, 0, 2, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77903 in the story'),
(19, 0, 77904, 0, 0, 8, 0, 77204, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77904 in the story'),
(19, 0, 77904, 0, 1, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77904 in the story'),
(19, 0, 77905, 0, 0, 8, 0, 77207, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77905 in the story'),
(19, 0, 77905, 0, 1, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77905 in the story'),
(19, 0, 77906, 0, 0, 8, 0, 77301, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77906 in the story'),
(19, 0, 77906, 0, 1, 8, 0, 77311, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77906 in the story'),
(19, 0, 77906, 0, 2, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77906 in the story'),
(19, 0, 77907, 0, 0, 8, 0, 77501, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77907 in the story'),
(19, 0, 77907, 0, 1, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77907 in the story'),
(19, 0, 77908, 0, 0, 8, 0, 77601, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77908 in the story'),
(19, 0, 77908, 0, 1, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77908 in the story'),
(19, 0, 77909, 0, 0, 8, 0, 77701, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77909 in the story'),
(19, 0, 77909, 0, 1, 8, 0, 77711, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77909 in the story'),
(19, 0, 77909, 0, 2, 8, 0, 77910, 0, 0, 0, 0, 0, '', 'Wrath Remix: quest 77909 in the story');

INSERT INTO `creature_questender` (`id`, `quest`) VALUES (770550, 11599);
-- The game's quests' texts this file changes, from their originals (kept the first time, and put
-- back first each time, so a text dropped from here is the game's again).
CREATE TABLE IF NOT EXISTS `remix_original_story_text` (
  `quest` INT UNSIGNED NOT NULL,
  `col` VARCHAR(16) NOT NULL,                     -- desc, log, done, reward, request
  `text` TEXT NULL,                               -- NULL: the quest had no such row
  PRIMARY KEY (`quest`, `col`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
UPDATE `quest_template` q JOIN `remix_original_story_text` o ON o.`quest` = q.`ID` AND o.`col` = 'desc' SET q.`QuestDescription` = o.`text`;
UPDATE `quest_template` q JOIN `remix_original_story_text` o ON o.`quest` = q.`ID` AND o.`col` = 'log' SET q.`LogDescription` = o.`text`;
UPDATE `quest_template` q JOIN `remix_original_story_text` o ON o.`quest` = q.`ID` AND o.`col` = 'done' SET q.`QuestCompletionLog` = o.`text`;
UPDATE `quest_offer_reward` r JOIN `remix_original_story_text` o ON o.`quest` = r.`ID` AND o.`col` = 'reward' SET r.`RewardText` = o.`text` WHERE o.`text` IS NOT NULL;
DELETE r FROM `quest_offer_reward` r JOIN `remix_original_story_text` o ON o.`quest` = r.`ID` AND o.`col` = 'reward' WHERE o.`text` IS NULL;
UPDATE `quest_request_items` i JOIN `remix_original_story_text` o ON o.`quest` = i.`ID` AND o.`col` = 'request' SET i.`CompletionText` = o.`text` WHERE o.`text` IS NOT NULL;
DELETE i FROM `quest_request_items` i JOIN `remix_original_story_text` o ON o.`quest` = i.`ID` AND o.`col` = 'request' WHERE o.`text` IS NULL;
DELETE FROM `remix_original_story_text`;
INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT 11599, 'reward', (SELECT `RewardText` FROM `quest_offer_reward` WHERE `ID` = 11599);
INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES (11599, '<William Allerton presses a rag to the shallow cut along his neck.>$B$BLeryssa sent you? She came all this way? Light bless that stubborn girl.$B$BI should never have written to her. If they''ll do this to me for asking about Thassarian, what will they do to her?', 0) ON DUPLICATE KEY UPDATE `RewardText` = VALUES(`RewardText`);
INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT 11608, 'reward', (SELECT `RewardText` FROM `quest_offer_reward` WHERE `ID` = 11608);
INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES (11608, 'That''ll stop ''em - at least I think it''ll stop ''em. Either way, you''ve done your part. That''s all an $r can ask for, no?$B$BAnd the High Overlord''s sending sappers out to sit on every one of those holes, in case anything tries digging back up. Somebody''s been talking in his ear.', 0) ON DUPLICATE KEY UPDATE `RewardText` = VALUES(`RewardText`);
INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT 11643, 'reward', (SELECT `RewardText` FROM `quest_offer_reward` WHERE `ID` = 11643);
INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES (11643, 'Already? Buddy, I been starin'' at that hut since the mist rolled in, tryin'' to work up the nerve! You just walked in there an'' back out like it was nothin''.$B$BNow where''d I put those spare parts...', 0) ON DUPLICATE KEY UPDATE `RewardText` = VALUES(`RewardText`);
INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT 11651, 'reward', (SELECT `RewardText` FROM `quest_offer_reward` WHERE `ID` = 11651);
INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES (11651, 'With the current state of our transports and shipping lanes, we haven''t been able to get a damned siege engine to Warsong. These tanks are all that we have left from the original expedition. Now that they''re operational, you''re gonna use ''em to stomp the Scourge offensive at the Plains of Nasam.$B$BAn'' Mobu says there''s plates left over to patch up two more. Two more tanks! Maybe I won''t cleave the little gnome in two after all.', 0) ON DUPLICATE KEY UPDATE `RewardText` = VALUES(`RewardText`);
INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT 11652, 'desc', (SELECT `QuestDescription` FROM `quest_template` WHERE `ID` = 11652);
UPDATE `quest_template` SET `QuestDescription` = 'Once you''re ready, jump into one of the tanks and drive it out to the Plains of Nasam, southeast of here.$B$BUse the tank''s weapon arsenal to take down the Scourge army. If you get in a jam, the "Meatpounder" will tear ''em up and the land mines will finish ''em off! If you find any of our soldiers, grab ''em and bring ''em back here! One last thing, fuel tanks can be found all over the field.$B$BTry to get close enough to that structure in the center and see what''s going on.$B$BIf you do all of this and live, go to Hellscream!' WHERE `ID` = 11652;
INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT 11938, 'reward', (SELECT `RewardText` FROM `quest_offer_reward` WHERE `ID` = 11938);
INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES (11938, 'That should buy us some time. Isidorus has been cooperative, but I really needed that alone time with the lich.$B$B<Thassarian nods toward the Valiance volunteers at the ziggurat''s edge.>$B$BAnd thank Hammerhill''s lads for me. I didn''t ask for help. It came anyway. I''d forgotten what that was like.', 0) ON DUPLICATE KEY UPDATE `RewardText` = VALUES(`RewardText`);
INSERT INTO `remix_original_story_text` (`quest`, `col`, `text`) SELECT 12311, 'reward', (SELECT `RewardText` FROM `quest_offer_reward` WHERE `ID` = 12311);
INSERT INTO `quest_offer_reward` (`ID`, `RewardText`, `VerifiedBuild`) VALUES (12311, 'That''s the attack from inside stopped. And with the mine road shut and the archers off the roofs, the attacks from outside aren''t bleeding us like they were. The High Commander says that''s enough: he''s sending a company to Lord Fordragon. They march for Fordragon Hold at first light.$B$B<Durkon looks at you for a long moment.>$B$BYou went straight down to the bottom chamber, $Glad:lass;, like you knew the way. Lucky guess, I''ll call it.', 0) ON DUPLICATE KEY UPDATE `RewardText` = VALUES(`RewardText`);

-- Never offered: flags, "rewarded" while they hold (RemixMoratari.cpp): the Timerunner has asked Moratari to
-- wait, and the others the content files name.
DELETE FROM `quest_template` WHERE `ID` IN (77040, 77910);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `LogTitle`, `LogDescription`, `QuestDescription`, `VerifiedBuild`) VALUES
(77040, 2, 1, 1, 0, 0, 'Walking Alone', '', 'Moratari waits at her posts while you walk alone.', 0),
(77910, 2, 1, 1, 0, 0, 'A Time Jumper', '', 'You told Moratari you are a time jumper: her story opens without waiting for the war''s.', 0);
