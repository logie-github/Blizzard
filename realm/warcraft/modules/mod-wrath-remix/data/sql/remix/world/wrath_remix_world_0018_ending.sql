-- The end (STORY.md): back at the Infinite Bazaar once the Lich King has fallen and the ending
-- cinematic is over. The Keepers of Time, who came with the bronze after the turn; Eternus's
-- letter; See You Later (the goodbyes, and what Sylvanas and Alleria can tell of what comes after
-- this war, while they still remember telling it); and Back to Your Own Time, whose scene takes
-- their memories and sends the Timerunner home to the ChromieCraft realm (WrathRemix.cpp).
--
--   WRM-801  after The Last Necessary Battle (77800), Moratari: say goodbye to Sylvanas, Alleria,
--            Andormu and Nozari
--   WRM-802  after See You Later, Moratari: home
--
-- What the people of the end say when spoken to: npc_text 7703001 and up. Spawns 7704300 to 7704309.

SET @MORATARI := 770001, @ANDORMU := 770003, @NOZARI := 770004, @SYLVANAS := 770011, @ALLERIA := 770012,
    @SCENE_CREDIT := 770035, @BYE_SYLVANAS := 770037, @BYE_ALLERIA := 770038, @BYE_ANDORMU := 770039, @BYE_NOZARI := 770040;

DELETE FROM `quest_template` WHERE `ID` IN (77801, 77802);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`,
  `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`,
  `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`, `ObjectiveText4`, `VerifiedBuild`) VALUES
(77801, 2, 80, 70, 210, 5, 0, 0, 0,
 'See You Later',
 'Say goodbye to Sylvanas Windrunner, Alleria Windrunner, Andormu and Nozari at the Infinite Bazaar, then speak with Moratari.',
 'You did it. All of it, exactly as it happened. That was the hardest thing anyone has ever asked of you, and nobody will ever thank you for it.$B$BSome of what you did here will never be known, $n. Not by the people you did it for, not by anyone in your own time. Time is unreliable that way. It keeps its debts quietly.$B$BAnd there is one more thing. Sylvanas and Alleria cannot take this home with them. Everything they saw here, everything they could tell you about what comes after: if they remember it, it bleeds into choices they have not made yet. So before they go, I am going to take it from them.$B$BAnd a little from you, $n. Northrend you keep; you earned it. But whatever they tell you of your own years ahead, the shore you are going back to and everything after it, I will take that too. You would try to change it. Anyone would.$B$BSay your goodbyes. Ask them anything you like. They have a great deal they could tell you, and for a little while longer, you will both remember it.',
 'Speak with Moratari at the Infinite Bazaar.',
 @BYE_SYLVANAS, 1, @BYE_ALLERIA, 1, @BYE_ANDORMU, 1, @BYE_NOZARI, 1,
 'Goodbye said to Sylvanas', 'Goodbye said to Alleria', 'Goodbye said to Andormu', 'Goodbye said to Nozari', 0),
(77802, 2, 80, 70, 210, 5, 0, 0, 0,
 'Back to Your Own Time',
 'Tell Moratari you are ready to go home.',
 'When you are ready, I will open the way. You will be back in your own time, in your side''s capital, the moment you left that table, with everything you carry. The Bronze stays here; it was never really yours. It belonged to the hours.$B$BI will not pretend I am glad to see you go. Ready?',
 'Go home.', @SCENE_CREDIT, 1, 0, 0, 0, 0, 0, 0, 'Gone home', '', '', '', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77801, 77802);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES (77801, 77800), (77802, 77801);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77801, 77802);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77801, 1, 'Take whatever time you need. They will not remember it. You will, most of it.', 0),
(77802, 1, 'Goodbye, Timerunner.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77801, 77802);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (@MORATARI, 77801), (@MORATARI, 77802);
DELETE FROM `creature_questender` WHERE `quest` IN (77801, 77802);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (@MORATARI, 77801), (@MORATARI, 77802);

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77801, 77802);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES (77801, 5000), (77802, 0);

-- The Keepers of Time at the Bazaar, where Eternus stood, once the turn is done; for one who never
-- saw it (a death knight, one the Chronologist sent past it), once Eternus has gone from it all the
-- same, from The Armies Are in Place, The Last Hour or The Last Necessary Battle
-- (wrath_remix_world_0011_chapter2.sql), so that the end can be played.
DELETE FROM `creature` WHERE `guid` BETWEEN 7704300 AND 7704309;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704300, @ANDORMU, 571, 1, 1, 0, 6395.5, 1878.0, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Andormu, Bazaar'),
(7704301, @NOZARI,  571, 1, 1, 0, 6392.5, 1878.0, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Nozari, Bazaar');
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND `SourceId` BETWEEN 7704300 AND 7704309;
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(30, 0, @ANDORMU, 7704300, 0, 47, 0, 77207, 66, 0, 0, 0, 0, '', 'Wrath Remix: Andormu at the Bazaar after The Weight of Time'),
(30, 0, @ANDORMU, 7704300, 1, 47, 0, 77701, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Armies Are in Place (Alliance)'),
(30, 0, @ANDORMU, 7704300, 2, 47, 0, 77711, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
(30, 0, @ANDORMU, 7704300, 3, 47, 0, 77721, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Hour'),
(30, 0, @ANDORMU, 7704300, 4, 47, 0, 77800, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Necessary Battle'),
(30, 0, @NOZARI, 7704301, 0, 47, 0, 77207, 66, 0, 0, 0, 0, '', 'Wrath Remix: Nozari at the Bazaar after The Weight of Time'),
(30, 0, @NOZARI, 7704301, 1, 47, 0, 77701, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Armies Are in Place (Alliance)'),
(30, 0, @NOZARI, 7704301, 2, 47, 0, 77711, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
(30, 0, @NOZARI, 7704301, 3, 47, 0, 77721, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Hour'),
(30, 0, @NOZARI, 7704301, 4, 47, 0, 77800, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Necessary Battle');

-- What Sylvanas and Alleria can tell, once the Lich King has fallen (npc_remix_windrunner offers
-- these as a conversation, one gossip option each, while See You Later or Back to Your Own Time is
-- open or after), and the goodbyes.
CREATE TABLE IF NOT EXISTS `remix_conversation` (
  `npc` INT UNSIGNED NOT NULL,
  `topic` TINYINT UNSIGNED NOT NULL,
  `label` VARCHAR(120) NOT NULL,
  `text` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`npc`, `topic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DELETE FROM `remix_conversation` WHERE `npc` IN (@SYLVANAS, @ALLERIA, @MORATARI, @ANDORMU, @NOZARI);
INSERT INTO `remix_conversation` (`npc`, `topic`, `label`, `text`) VALUES
(@SYLVANAS, 1, 'What happens to you, after this war?', 7703001),
(@SYLVANAS, 2, 'Garrosh. What becomes of him?', 7703002),
(@SYLVANAS, 3, 'Does the Legion ever come back?', 7703003),
(@SYLVANAS, 4, 'And after the Legion?', 7703004),
(@SYLVANAS, 5, 'What becomes of the Helm? Of Bolvar?', 7703005),
(@SYLVANAS, 6, 'And now? In your own time?', 7703006),
(@SYLVANAS, 7, 'Tell me about your sisters.', 7703007),
(@SYLVANAS, 8, 'You talk to me like you know me.', 7703008),
(@ALLERIA, 1, 'Everyone thinks you''re dead. Where are you, in this year?', 7703011),
(@ALLERIA, 2, 'How do you come home?', 7703012),
(@ALLERIA, 3, 'There is something dark in you. What is it?', 7703013),
(@ALLERIA, 4, 'Who are your people now?', 7703014),
(@ALLERIA, 5, 'Tell me about your son.', 7703015),
(@ALLERIA, 6, 'When the Helm broke, what did you feel?', 7703016),
(@ALLERIA, 7, 'Who are you fighting, in your own time?', 7703017),
(@ALLERIA, 8, 'Tell me about Sylvanas.', 7703018),
(@ALLERIA, 9, 'Why do you keep looking out for me?', 7703019),
(@MORATARI, 1, 'What will you do now?', 7703021),
(@MORATARI, 2, 'Will I remember any of this?', 7703024),
(@ANDORMU, 1, 'Will the bronze remember any of this?', 7703022),
(@NOZARI, 1, 'What goes in the record?', 7703023);

-- Eternus's letter, as the Timerunner returns to the Bazaar.
CREATE TABLE IF NOT EXISTS `remix_letter` (
  `id` TINYINT UNSIGNED NOT NULL,
  `subject` VARCHAR(120) NOT NULL,
  `body` TEXT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DELETE FROM `remix_letter` WHERE `id` = 1;
INSERT INTO `remix_letter` (`id`, `subject`, `body`) VALUES
(1, 'From the river''s edge',
 'Timerunner,\n\nI watched from the river''s edge as you went in. I watched the throne take its new king: the paladin, taking up the cold I wanted to spare him. The record held. It always holds, when people like you are standing under it.\n\nI will not tell you I was wrong. I will tell you that tonight, for the first time in a very long while, I have stopped counting graves, and I do not yet know what to do with my hands.\n\nIf you see Moratari, tell her the records are hers now. She always kept them better than I did.\n\nE.');

DELETE FROM `npc_text` WHERE `ID` BETWEEN 7703001 AND 7703099;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
-- Sylvanas, after the war.
(7703001, 'In a few days, the woman I was in this year will climb that citadel. She will find him already dead, and a paladin wearing his crown. She came for a victory, and she will find nothing left to fight.$B$BSo she will throw herself from the top.$B$BWhat she sees on the way down is the reason for everything I became: a darkness that does not end, waiting for her, and nothing she has ever done enough to keep it away. The val''kyr will catch her before she reaches it. She will spend years making sure she never has to see it again.$B$BAfter that, Gilneas, and Garrosh, and the rest of it: years you have not lived yet. You will see what I do in them. You will never know why. I will not tell you I was wise. I will tell you I was afraid, and that fear looks a great deal like ambition from the outside.', '', 1),
(7703002, 'He becomes Warchief, in time. He makes the Horde a weapon and points it at everyone, the Forsaken included. When the Horde finally turns on him, I turn with it. I would like to tell you it was principle. Some of it was.$B$BAnd then his madness, and an old world dragged into a new war. I stayed home, and counted what the Horde lost, and wondered how long it would be before something came for all of us.$B$BSomething does. You will be standing on a dock when it comes.', '', 1),
(7703003, '<She is quiet for a long moment.>$B$BIt does. Years from your tavern, on a coast called the Broken Shore. I was on that shore, $n. I will not tell you what happens on it. Some of it you would try to stop, and you cannot, and trying would cost you more than it saved.$B$BI will tell you what you will hear soon enough: Vol''jin takes his death wound there, and with his last breath he names me Warchief. He said the spirits told him to. I never knew whether to believe him.$B$BThen Stormheim, and Eyir, the queen of the val''kyr. I meant to bind her, so that my people would never stop rising, so that none of us would ever have to fall into that darkness again. Genn Greymane stopped me. I have never forgiven him for it, and I have never quite been able to blame him.$B$BWe won your war. I remember thinking, at the end of it: now, at last, there will be time to prepare for what comes after death. There was not.', '', 1),
(7703004, 'You will hear the name Teldrassil, $n, and you will hear mine beside it. I will not explain it. Not because there is no reason, but because you would hear the reason and believe it was enough, and it was not.$B$BI poisoned my own city before I would let the Alliance have it. Lordaeron, the home I had made for my people. I stood on its walls and filled it with blight.$B$BVarok Saurfang, the father of the boy who died at the Wrathgate, challenged me at the end of it all. He asked me a question, and I gave him an answer he did not deserve, and then he died. He was a better soldier than I was a Warchief. He was right about me.', '', 1),
(7703005, 'The Helm. One day, at the top of that citadel you just climbed, I will take it from Bolvar''s head and break it in my hands. The sky above Icecrown will tear open, and every soul in the world will fall into the place I saw on my way down from that tower.$B$BI did it for a jailer who promised me the world could be remade without its cruelest lie: that death is only darkness. I thought I could use him. He used me. When I finally saw what he was, I helped to stop him, and it was not enough to make anything right.$B$BThey judged me for the rest. They were right to. My sentence is to free the souls I sent into the dark, one at a time, for as long as it takes. It will take a very long time.', '', 1),
(7703006, 'The Maw. It is quieter than you would think. The souls do not thank me. Most of them do not know who I am, and the ones who do would rather I left them there.$B$BI hear about the world the way the dead hear things: late, and in pieces, and from people who did not mean to tell me. A war beneath the earth. And then, the last thing before Chromie found me: the Void had come for Quel''Thalas, and my sister was standing in its way.$B$B<A pause.>$B$BOf course she was.$B$BThe world kept going without me. It is the only thing I have ever done for it that it truly wanted.', '', 1),
(7703007, 'Alleria went through the Dark Portal when we were young, and did not come back. When she did, she was a thousand years older, and I was dead, and neither of us knew how to begin. We still do not, entirely.$B$BVereesa is in Dalaran in this year, with her husband and her two boys. You know what happens to Rhonin at Theramore. So do I. Neither of us will tell her.$B$BWe were three girls in a house in Eversong, once. I think about that more than I should.', '', 1),
(7703008, 'Because I do. Where I come from, you are... <She chooses the word with care.> ...someone I trust. There are not many.$B$BI will not tell you how it happens. If you knew, you would go looking for it, and the road you took to find it would not be the one that brought you to me. Some things only stay true if no one knows them in advance.$B$BSo I will slip, now and then. Forgive me that. I have not had to be a stranger to you in a very long time.', '', 1),
-- Alleria, after the war.
(7703011, 'Far from here. Beyond the Twisting Nether, with Turalyon and the Army of the Light, fighting the Legion on worlds you have never heard of, in a war that was ancient long before we joined it.$B$BI have been gone a very long time, Timerunner. Longer for me than for anyone on Azeroth: time runs differently out there. I have been fighting for over a thousand years.$B$BIn your year too, $n. You will go home to a world that still tells my story with an ending. It is a little early. Do not correct them. I would like to see their faces.', '', 1),
(7703012, '<She glances toward Moratari.>$B$BShe will take this from you anyway, so: through Argus. The Legion''s own homeworld, burning under its master''s eye. The Army of the Light, the Prime Naaru Xe''ra, and Illidan Stormrage, who had been dead and imprisoned and was not, in the end, either.$B$BXe''ra wanted Illidan to be her chosen one. She wanted it very badly. The Light wanted to be obeyed. Illidan refused, and he struck her down for it, and I have never been entirely sure he was wrong.$B$BWe won. We came home. I found that home had gone on without me, which is what homes do.$B$B<She looks at you, and her mouth twists.>$B$BYou would hate Argus. You would go anyway. I can tell that much just by looking at you.', '', 1),
(7703013, 'On Argus, a wanderer called Locus-Walker showed me the Void. Not the darkness people fear: the other side of the coin from the Light, just as old and just as true.$B$BAt the Seat of the Triumvirate, I met L''ura, a naaru who had fallen into the Void. I took her into myself. I could not have told you then whether I was saving the world or damning myself. I still cannot.$B$BIt whispers. It always will. The trick is not to stop listening. The trick is to remember that I am the one doing the listening.$B$B<She sees your face, and her voice sharpens.>$B$BDo not look at me like that. It is mine to carry, and I carry it well. I do not need anyone worrying over me. You least of all.', '', 1),
(7703014, 'Magister Umbric and his followers studied the Void in Silvermoon and were driven out for it. They went too deep, and the Void went into them. When I found them, at the edge of a rift called Telogrus, they were frightened and furious and very, very proud.$B$BI taught them what Locus-Walker taught me. They taught me that I was not the only one. The ren''dorei are my people now as much as anyone''s. I am not their queen. If they follow me, it is because I went first. Someone told me once that going first is the only kind of leading worth the name. I will not tell you who.', '', 1),
(7703015, 'My son. Turalyon''s and mine. We left him behind when he was a baby, when we went through the Portal, because we thought we would be back in a season. Vereesa kept him safe for a while. Others raised him.$B$BBy the time we came home, he was a grown man and a paladin of the Light, and he had every right to hate us. He did not. I do not know what I did to deserve that. I think he decided to give it to me anyway.$B$BFamily is a strange thing, $n. Sometimes it is the people you are born to. Sometimes it is only the people who keep turning up, whether you ask them to or not.$B$B<She clears her throat.>$B$BThat is a general observation.', '', 1),
(7703016, 'When the sky tore open over Icecrown, every soul in the world began to go the wrong way. I felt it in the Void like a door left open in winter: a cold draught, everywhere at once, and nothing anyone could do to close it.$B$BI have stood in the Light and in the Void. I had never felt the place where the dead go before. I hope never to feel it again.', '', 1),
(7703017, 'Her name is Xal''atath. She calls herself the Harbinger of the Void, and she knows every one of my fears by name and wears them like jewelry.$B$BShe came up out of the earth first, in Khaz Algar, among the earthen and the nerubians. When the bronze found me, she had come for Quel''Thalas. For the Sunwell. For home.$B$BShe wants me to break. She knows exactly where I am cracked, and she presses there, again and again. I will be fighting her when I go back. That is the thing about the Void, Timerunner. It is very patient. So am I.', '', 1),
(7703018, 'She asked me to come. She has never asked me for anything, not once, in all the years either of us has been alive or otherwise.$B$BShe did terrible things. I will not pretend she did not, and she would not thank me for it. But she is my sister, and when Chromie told her what was happening here, she came, and she brought me, and she has spent every day since making sure that the war against the man who killed her ends exactly as it did.$B$BI do not know what that is, if it is not love.$B$BAnd she is careful with you, $n. Have you noticed? I have never once seen her careful with anyone.$B$BShe is not the only one, I suppose.$B$B<She stops.>$B$BWe were talking about Sylvanas.', '', 1),
(7703019, 'I do not. You are imagining it.$B$B<You wait. She lets the silence go on long enough to be uncomfortable, and then a little longer.>$B$B...Sylvanas is careful with you. I am not careful. I am cross with you, constantly, which in our family is very much worse.$B$BAsk me again when you come to say goodbye. Not before. I would like a little longer of you not knowing.', '', 1),
-- Moratari and the Keepers.
(7703021, 'I will keep the records. Someone has to. Eternus left them to me; it is the closest thing to an apology she knows how to make.$B$BAnd watch the river. She will come back to it one day, looking for a grave history does not need. When she does, I would like to be the one standing there.', '', 1),
(7703022, 'Every word of it. We are good at remembering, Timerunner. It is most of what we are for.$B$BThe people you saved it for will never know. That is the oldest arrangement there is between the bronze and the world, and it has always seemed to me a fair one.', '', 1),
(7703024, 'The war, yes. Northrend, the echoes, the people you stood beside: those are yours. You earned them.$B$BWhat Sylvanas and Alleria tell you of your own years ahead, no. When you go home, I will send that back to the hours it came from. You would try to change it. Anyone would. I have watched what that does to someone; I watched it do it to Eternus.$B$BSo ask them anything. Just know that I will be the only one who remembers the answers.', '', 1),
(7703023, 'The record says the war ended as it ended. That is all it will ever say, to anyone who reads it.$B$BIn the margin, where only the Keepers look, I have written your name. It is where the most important things go.', '', 1),
-- The goodbyes.
(7703031, 'Then go. Do not make a ceremony of it; I never could stand them.$B$B...It was good to fight on the right side of something, Timerunner. Even once.$B$B<She looks at you as if she might say more, and does not.>$B$BI know what you are to me, $n. You do not, yet. That is how it has to be.', '', 1),
(7703032, '<For once, she does not reach for her hood, or look away.>$B$BSo you are going. Then I will say it once, while Moratari still lets us keep it, and you will let me finish.$B$BWhere I come from, you are family, $n. Nobody wrote it down and nobody swore to it. It happened the long way: on Argus, and on every road the Void has walked since, with you beside me each time I needed someone there and was too proud to ask. You are my $Gbrother:sister; in every way that counts.$B$BTuralyon says I treat you the way I treated Lirath, before the war took him: badly, and as though you were mine to look after. He is right. I have never told him that either.$B$BThat is why I kept my distance. It was that or tell you everything, and you deserve to find your own way to it.$B$B<She pulls you into a brief, fierce embrace, and lets go before you can return it.>$B$BGo home, Timerunner. Hug someone for me. You don''t have to tell them why.$B$BI will see you in the future, $n. Try not to be late. You always are.', '', 1),
(7703033, 'The bronze will remember your name, even if no one else does. Safe travels, Timerunner. The roads home are always shorter than the roads away.', '', 1),
(7703034, 'Goodbye, Timerunner. Of everyone I have watched this war through, you are the one I least expected to be sorry to see go.', '', 1);
