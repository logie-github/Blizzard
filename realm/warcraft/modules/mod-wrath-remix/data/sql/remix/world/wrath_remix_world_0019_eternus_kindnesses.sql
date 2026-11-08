-- Wrath Remix (STORY.md, "Before the turn"): until Sylvanas and Alleria stop her, Eternus is
-- folding the war her way, quietly. Some of the original quests on the story's path through the
-- Borean Tundra and the Dragonblight turn in a little differently than history has them: an NPC
-- notices a small thing that went better than it should have (their turn-in text), and Eternus
-- whispers that it was her (remix_quest_note: only before WRM-207, The Weight of Time; WrathRemix.cpp).
-- The originals are kept in remix_original_reward_text, and each text is made from its original.
CREATE TABLE IF NOT EXISTS `remix_original_reward_text` (
  `ID` INT UNSIGNED NOT NULL,
  `RewardText` TEXT,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT IGNORE INTO `remix_original_reward_text` (`ID`, `RewardText`)
SELECT `ID`, `RewardText` FROM `quest_offer_reward` WHERE `ID` IN (11672, 11727, 11797, 11889, 11897, 11956, 12237, 12253, 12309, 11585, 11586, 11595, 11596, 11602, 11636, 11652, 12034, 12218, 12221);
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'You bring luck with you, it seems. We''d given one of the transports up for lost in last night''s storm, and she limped in at dawn with every soul aboard. Her captain swears the storm opened in front of him like a curtain.') WHERE o.`ID` = 11672;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'And those two catapults I moved to the south wall on your word? The Scourge hit that wall before dawn, and they were waiting for them. Looks like I owe you that drink.') WHERE o.`ID` = 11727;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'And the medic''s got nobody to stitch tonight. Not one man lost on the barricade. I''ve held a lot of barricades, and that doesn''t happen.') WHERE o.`ID` = 11797;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'Funny thing, though. Their big run on the inner defenses came in late this morning, well behind the crawlers, and every net we had was out and waiting.') WHERE o.`ID` = 11889;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'The engineers found a third sinkhole past the ridge, already caved in on itself before anything could crawl out of it. I''m not one to look a gift gryphon in the beak.') WHERE o.`ID` = 11897;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'Corporal Venn counted twice as many guarding that phylactery. Either the corporal can''t count, or someone thinned them out before you got there.') WHERE o.`ID` = 11956;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'Strange thing, though: the roost that cracked on the first night is still standing. Every handler down there swore it would come down.') WHERE o.`ID` = 12237;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = REPLACE(r.`RewardText`, '<Halford says a prayer for the deceased.>', '<Halford says a prayer for the deceased.>$B$BA shorter prayer than I had dreaded. The healers made ready for twice the wounded they have seen.') WHERE o.`ID` = 12253;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = REPLACE(r.`RewardText`, 'I barely made it out last time - which is what prompted', 'I barely made it out last time, me and my squire both. A beam came down a breath behind us; it should''ve flattened the pair of us. Which is what prompted') WHERE o.`ID` = 12309;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'At least the wind knows which side it is on. It turned at dawn and blew the Scourge''s filth back into their own lines. Let them choke on it.') WHERE o.`ID` = 11585;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'At least the wind knows which side it is on. It turned at dawn and blew the Scourge''s filth back into their own lines. Let them choke on it.') WHERE o.`ID` = 11586;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'Strange morning. The stretch of wall that cracked in the last assault was braced before the masons ever got to it. Nobody''s owning up.') WHERE o.`ID` IN (11595, 11596);
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'One thing''s going our way, at least. The supply wagons from the docks got through without a scratch. First time since we landed.') WHERE o.`ID` = 11602;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'Thinner today, though. Lifted right off the tanks for an hour this mornin'', like somebody pulled a sheet off ''em.') WHERE o.`ID` = 11636;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = REPLACE(r.`RewardText`, 'You are dismissed.', 'And the old one''s scouts crept home from the plains under a fog, every one of them. The spirits must be fond of old orcs.$B$BYou are dismissed.') WHERE o.`ID` = 11652;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'And the morning sortie came home with every rider it took out. Somebody moved it up without telling me. Whoever it was, I''d shake their hand.') WHERE o.`ID` = 12034;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', 'One small disappointment: the cloud drifted south over the farmsteads, and every one of them was empty. Cleared out the night before. Pity. I would so have liked a broader sample.') WHERE o.`ID` = 12218;
UPDATE `quest_offer_reward` o JOIN `remix_original_reward_text` r ON r.`ID` = o.`ID` SET o.`RewardText` = CONCAT(TRIM(TRAILING '\n' FROM r.`RewardText`), '$B$B', '<Doctor Malefious counts the vials again, and frowns.>$B$BOne short. You didn''t... no. No, of course you didn''t.') WHERE o.`ID` = 12221;

CREATE TABLE IF NOT EXISTS `remix_quest_note` (
  `quest` INT UNSIGNED NOT NULL,
  `text` TEXT NOT NULL,
  PRIMARY KEY (`quest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DELETE FROM `remix_quest_note` WHERE `quest` IN (11672, 11727, 11797, 11889, 11897, 11956, 12237, 12253, 12309, 11585, 11586, 11595, 11596, 11602, 11636, 11652, 12034, 12218, 12221);
INSERT INTO `remix_quest_note` (`quest`, `text`) VALUES
(11672, 'That transport was lost with all hands, champion. Today it was not. No one will ever ask why, and that is how I prefer it.'),
(11727, 'In the war you remember, the catapults stood on the wrong wall, and the south wall paid for it. You told him, and he listened. They never hear me, champion. They hear you.'),
(11797, 'A young man named Brennick died on that barricade, with his letters home still in his pack. He will post them tomorrow.'),
(11889, 'A flyer only has to be a minute late to miss. I made them late.'),
(11897, 'The third sinkhole was mine. There is a fourth, and Moratari knows where. History will never hear of that one.'),
(11956, 'I am not in the habit of fighting liches. I am in the habit of being early.'),
(12237, 'That roost came down, and eleven gryphons with it. I have lent it a few more days. Only a few; spend them well.'),
(12253, 'Twelve of the people in those houses never came out of them. Tonight they did. The bronze would call that a wound in time. I call it a good night''s work.'),
(12309, 'His squire''s name is Tobin. You never heard it, because that beam did not wait for him. Today it did.'),
(11585, 'The wind blew the other way, champion, and the sick tents of Warsong Hold were full for a week. Weather is the easiest thing in the world to change, and no one ever asks who changed it.'),
(11586, 'The wind blew the other way, champion, and the sick tents of Warsong Hold were full for a week. Weather is the easiest thing in the world to change, and no one ever asks who changed it.'),
(11595, 'That wall came down in the next assault, and the grunts beneath it with it. I braced it in the night. Let Razgor wonder.'),
(11596, 'That wall came down in the next assault, and the grunts beneath it with it. I braced it in the night. Let Razgor wonder.'),
(11602, 'Those wagons burned. I sent the Scourge''s scouts the long way round. Small kindnesses, champion.'),
(11636, 'The Kvaldir walk out of that mist whenever they please. This morning they found nothing worth taking. I lifted it for an hour; it was all I could spare.'),
(11652, 'Six of Saurfang''s scouts went out onto those plains, and four came home. Today, six. I am told the fog was very convincing.'),
(12034, 'Juktok lost two riders that morning, flying into the sun. I moved the sortie. The sun stayed where it was.'),
(12218, 'That cloud drifted over the farmsteads, and there were families in them. I emptied them the night before. You will meet that blight again, at the gate. When you do, I would like it to find no one waiting.'),
(12221, 'I took one vial. I want to know exactly what it is I mean to stop.');
