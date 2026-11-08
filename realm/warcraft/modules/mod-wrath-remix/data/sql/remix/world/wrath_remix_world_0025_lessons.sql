-- The class lessons (src/RemixLessons.cpp): a Timerunner wakes at level 10 with a class's worth of
-- abilities they have never used here, so the instructor of their class in the Bazaar's training
-- yard walks them through three of them (WRM-030 to 039, one a class: 77030 the druid's, 77030 +
-- the class's number for the others). Each ability used as the lesson says is its credit (770067 +
-- its slot, in wrath_remix_world_0002_npcs.sql): on one of the yard's dummies, or (a seal, a shield,
-- a heal, stealth) within sight of one. The prologue's step after Old Habits (WRM-020), offered by
-- the instructor until it's done, alongside the trainer's list; the lessons' level is the
-- Timerunner's own.

CREATE TABLE IF NOT EXISTS `remix_lesson` (
  `class` TINYINT UNSIGNED NOT NULL,
  `quest` INT UNSIGNED NOT NULL,
  `slot` TINYINT UNSIGNED NOT NULL,       -- 0 to 2: the quest's objective, and the credit 770067 + slot
  `spell` INT UNSIGNED NOT NULL,          -- its first rank (every rank counts)
  `target` TINYINT UNSIGNED NOT NULL,     -- 0 on a training dummy, 1 anywhere within sight of one
  PRIMARY KEY (`class`, `slot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELETE FROM `remix_lesson`;
INSERT INTO `remix_lesson` (`class`, `quest`, `slot`, `spell`, `target`) VALUES
(1, 77031, 0, 100, 0),      -- Charge
(1, 77031, 1, 772, 0),      -- Rend
(1, 77031, 2, 78, 0),       -- Heroic Strike
(2, 77032, 0, 21084, 1),    -- Seal of Righteousness
(2, 77032, 1, 20271, 0),    -- Judgement of Light
(2, 77032, 2, 635, 1),      -- Holy Light
(3, 77033, 0, 1130, 0),     -- Hunter's Mark
(3, 77033, 1, 1978, 0),     -- Serpent Sting
(3, 77033, 2, 3044, 0),     -- Arcane Shot
(4, 77034, 0, 1784, 1),     -- Stealth
(4, 77034, 1, 1752, 0),     -- Sinister Strike
(4, 77034, 2, 2098, 0),     -- Eviscerate
(5, 77035, 0, 589, 0),      -- Shadow Word: Pain
(5, 77035, 1, 585, 0),      -- Smite
(5, 77035, 2, 17, 1),       -- Power Word: Shield
(6, 77036, 0, 45477, 0),    -- Icy Touch
(6, 77036, 1, 45462, 0),    -- Plague Strike
(6, 77036, 2, 47541, 0),    -- Death Coil
(7, 77037, 0, 403, 0),      -- Lightning Bolt
(7, 77037, 1, 8042, 0),     -- Earth Shock
(7, 77037, 2, 331, 1),      -- Healing Wave
(8, 77038, 0, 116, 0),      -- Frostbolt
(8, 77038, 1, 133, 0),      -- Fireball
(8, 77038, 2, 2136, 0),     -- Fire Blast
(9, 77039, 0, 172, 0),      -- Corruption
(9, 77039, 1, 348, 0),      -- Immolate
(9, 77039, 2, 686, 0),      -- Shadow Bolt
(11, 77030, 0, 8921, 0),    -- Moonfire
(11, 77030, 1, 5176, 0),    -- Wrath
(11, 77030, 2, 774, 1);     -- Rejuvenation

SET @LESSON_1 := 770067, @LESSON_2 := 770068, @LESSON_3 := 770069;

DELETE FROM `quest_template` WHERE `ID` BETWEEN 77030 AND 77039;
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `RewardItem1`, `RewardAmount1`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGo2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGoCount2`, `RequiredNpcOrGoCount3`,
  `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`, `VerifiedBuild`) VALUES
(77031, 2, -1, 1, -81, 3, 0, 0, 0, 0, 0,
 'Steel Remembers',
 'Use Charge, Rend and Heroic Strike on a Training Dummy in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'A warrior learns with a weapon in hand, $n, so I will keep this short.$B$BStart from a distance: Charge closes the gap in a heartbeat and gives you rage to spend. Rend next, so your enemy bleeds while you work. Then Heroic Strike: it takes the place of your next swing, so press it and keep swinging.$B$BThe dummies in the yard can take it. Show me all three.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Charge a Training Dummy', 'Rend a Training Dummy', 'Heroic Strike a Training Dummy', 0),
(77032, 2, -1, 1, -141, 3, 0, 0, 0, 0, 0,
 'Seal and Judgement',
 'Take up Seal of Righteousness, use Judgement of Light on a Training Dummy and cast Holy Light in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'The Light has not left you, $n. You have only forgotten how to call it.$B$BFirst, a seal: Seal of Righteousness rests on you and lends every swing a little holy fire. Then Judgement of Light on your enemy: it unleashes the seal''s power on them at once, and for a while after, the Light mends whoever strikes them. And when the fight turns against you, Holy Light, on yourself if no one else needs it more.$B$BUse the dummies, and stay where I can see you.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Seal of Righteousness taken up', 'Judgement of Light on a Training Dummy', 'Holy Light cast in the training yard', 0),
(77033, 2, -1, 1, -261, 3, 0, 0, 0, 0, 0,
 'Mark, Sting and Shot',
 'Use Hunter''s Mark, Serpent Sting and Arcane Shot on a Training Dummy in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'A hunter fights from where the prey cannot reach, $n. Let us see your aim.$B$BMark your quarry first: Hunter''s Mark keeps it in your sight even when it hides, and every shot you put into it hits harder. Then Serpent Sting, a poison that works while you do. Then Arcane Shot, quick and hard, between your automatic shots.$B$BStand back from a dummy and put all three into it.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Hunter''s Mark on a Training Dummy', 'Serpent Sting on a Training Dummy', 'Arcane Shot on a Training Dummy', 0),
(77034, 2, -1, 1, -162, 3, 0, 0, 0, 0, 0,
 'Out of the Shadows',
 'Enter Stealth, then use Sinister Strike and Eviscerate on a Training Dummy in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'Most fights a rogue wins are over before the other side knows they have started.$B$BBegin in Stealth, and close in unseen. Then Sinister Strike: every one puts a combo point on your target. With a few points gathered, finish with Eviscerate; the more points you spend, the harder it lands.$B$BThe dummies will not see you coming. Neither should anyone else.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Stealth entered in the training yard', 'Sinister Strike on a Training Dummy', 'Eviscerate on a Training Dummy', 0),
(77035, 2, -1, 1, -262, 3, 0, 0, 0, 0, 0,
 'Word and Shield',
 'Use Shadow Word: Pain and Smite on a Training Dummy and cast Power Word: Shield in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'The Light answers those who ask clearly, $n. So ask.$B$BShadow Word: Pain first: it lingers, and does its work while you do yours. Smite is your steady strike of holy fire. And before anything reaches you, Power Word: Shield, on yourself or on whoever needs it more.$B$BStrike the dummies, then shield yourself where I can see it.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Shadow Word: Pain on a Training Dummy', 'Smite on a Training Dummy', 'Power Word: Shield cast in the training yard', 0),
(77036, 2, -1, 1, -372, 3, 0, 0, 0, 0, 0,
 'Frost, Plague and Shadow',
 'Use Icy Touch, Plague Strike and Death Coil on a Training Dummy in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'You were made for this, $n, whether you wanted to be or not.$B$BIcy Touch sets Frost Fever in your enemy. Plague Strike adds Blood Plague. With both diseases on them, your other strikes cut deeper; and Death Coil, paid for with the runic power your strikes have gathered, finishes what the diseases began.$B$BOn a dummy. All three.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Icy Touch on a Training Dummy', 'Plague Strike on a Training Dummy', 'Death Coil on a Training Dummy', 0),
(77037, 2, -1, 1, -82, 3, 0, 0, 0, 0, 0,
 'The Elements Answer',
 'Use Lightning Bolt and Earth Shock on a Training Dummy and cast Healing Wave in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'The elements have not forgotten you, $n, even if you have forgotten them.$B$BLightning Bolt is your first word to an enemy, from a distance. Earth Shock is instant, and it slows the swings of whatever it strikes: use it as they close in. And Healing Wave, on yourself or a friend, when a fight runs long.$B$BTwo for a dummy, and one for yourself, here in the yard.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Lightning Bolt on a Training Dummy', 'Earth Shock on a Training Dummy', 'Healing Wave cast in the training yard', 0),
(77038, 2, -1, 1, -161, 3, 0, 0, 0, 0, 0,
 'Fire and Frost',
 'Use Frostbolt, Fireball and Fire Blast on a Training Dummy in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'Every mage forgets something on a journey like yours, $n. Usually the hat. Sometimes the fireball.$B$BFrostbolt first: it slows whatever it strikes, and that buys you time. Fireball for the real damage, while they crawl toward you. And Fire Blast, instant, for when they arrive anyway.$B$BThe dummies are fireproof. More or less.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Frostbolt on a Training Dummy', 'Fireball on a Training Dummy', 'Fire Blast on a Training Dummy', 0),
(77039, 2, -1, 1, -61, 3, 0, 0, 0, 0, 0,
 'What Power Costs',
 'Use Corruption, Immolate and Shadow Bolt on a Training Dummy in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'Power always costs something, $n. Today, the dummy is paying.$B$BCorruption first: instant, and it keeps eating at your enemy long after you cast it. Then Immolate, fire that burns and goes on burning. Then Shadow Bolt, again and again, while the rest does its work.$B$BAll three, on a dummy. Let them stack.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Corruption on a Training Dummy', 'Immolate on a Training Dummy', 'Shadow Bolt on a Training Dummy', 0),
(77030, 2, -1, 1, -263, 3, 0, 0, 0, 0, 0,
 'The Balance of Things',
 'Use Moonfire and Wrath on a Training Dummy and cast Rejuvenation in the Bazaar''s training yard, then return to the Timeworn Instructor.',
 'Nature is patient, $n. A druid need not be.$B$BMoonfire first: instant, and its burn lingers. Then Wrath, a bolt of nature''s anger, from a distance. And when you are hurt, Rejuvenation: it mends you over time while you keep fighting.$B$BMoonfire and Wrath on a dummy; Rejuvenation on yourself, here in the yard.',
 'Return to the Timeworn Instructor.',
 @LESSON_1, @LESSON_2, @LESSON_3, 1, 1, 1,
 'Moonfire on a Training Dummy', 'Wrath on a Training Dummy', 'Rejuvenation cast in the training yard', 0);

-- Each for its own class only, after Old Habits (WRM-020); whichever it was opens the Bazaar's
-- Keepers (WRM-021: each lesson's NextQuestID, so any one of them will do). A death knight's has no
-- Old Habits before it (they come to the Bazaar later, by their own road).
DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 77030 AND 77039;
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `NextQuestID`, `AllowableClasses`) VALUES
(77031, 77020, 77021, 1), (77032, 77020, 77021, 2), (77033, 77020, 77021, 4), (77034, 77020, 77021, 8), (77035, 77020, 77021, 16),
(77036, 0, 0, 32), (77037, 77020, 77021, 64), (77038, 77020, 77021, 128), (77039, 77020, 77021, 256), (77030, 77020, 77021, 1024);

DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 77030 AND 77039;
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`, `VerifiedBuild`)
SELECT `ID`, 1, 1, 'The dummies are still standing, I see. Go on, I am watching.', 0 FROM `quest_template` WHERE `ID` BETWEEN 77030 AND 77039;

DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 77030 AND 77039;
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77031, 1, 'Good. Rage is earned by fighting and lost by waiting, so spend it. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77032, 1, 'There it is. Seal, Judgement, and the Light to see you through. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77033, 1, 'Clean work. Keep your distance, keep your mark on them, and they will never reach you. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77034, 1, 'I barely saw you. Good. Build your points, spend them well, and never fight fair. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77035, 1, 'Well done. Shield first, then strike; you will outlast far worse than a dummy. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77036, 1, 'Diseases first, then the coil. You remember. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77037, 1, 'The elements still answer you. Bolt from afar, shock up close, and a wave to keep you standing. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77038, 1, 'Slow them, burn them, and blast what is left. That is most of magic, really. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77039, 1, 'Corruption, Immolate, Shadow Bolt. Let your enemy pay for every second they stand there. The rest will come back to you as you grow, and I will be here when you need more.', 0),
(77030, 1, 'Moonfire, Wrath, and Rejuvenation to keep you on your feet. Balance. The rest will come back to you as you grow, and I will be here when you need more.', 0);

-- From the instructor of the class, who takes it back (both of the paladins' have it).
DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN 77030 AND 77039;
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(770101, 77031), (770102, 77032), (770103, 77032), (770104, 77033), (770105, 77034), (770106, 77035),
(770107, 77036), (770108, 77037), (770109, 77038), (770110, 77039), (770111, 77030);
DELETE FROM `creature_questender` WHERE `quest` BETWEEN 77030 AND 77039;
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(770101, 77031), (770102, 77032), (770103, 77032), (770104, 77033), (770105, 77034), (770106, 77035),
(770107, 77036), (770108, 77037), (770109, 77038), (770110, 77039), (770111, 77030);

DELETE FROM `remix_quest_reward` WHERE `quest` BETWEEN 77030 AND 77039;
INSERT INTO `remix_quest_reward` (`quest`, `bronze`)
SELECT `ID`, 500 FROM `quest_template` WHERE `ID` BETWEEN 77030 AND 77039;

-- What an instructor says while a Timerunner's lesson is still to do.
DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702501 AND 7702509;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(7702501, 'The yard is yours, Timerunner. Let me walk you through what you already know, or teach you something new.',
          'The yard is yours, Timerunner. Let me walk you through what you already know, or teach you something new.', 1);
