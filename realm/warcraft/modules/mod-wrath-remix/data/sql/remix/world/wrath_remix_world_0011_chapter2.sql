-- Chapter II, The Wrathgate (STORY.md): the chapter the story turns on. Moratari's transitions
-- (the guide's bridges II-A, II-B and II-C) as Chapter I's are made
-- (wrath_remix_world_0006_bridges.sql), and between them the story: Wyrmrest Temple, where
-- Chromie has brought Sylvanas and Alleria Windrunner back from the future; Eternus's answer;
-- right before the Wrathgate's chain, her real plan, and the turn at the Bazaar; then a fight on
-- the cliffs above the gate, so that it happens as it did. Never the Wrathgate itself, nor the
-- Battle for the Undercity: II-B only follows the Wrathgate, and II-C the battle.
--
--   WRM-203  Alliance  after Find Durkon! (12309), Moratari: to Chromie, Mystery of the Infinite (12470)
--   WRM-213  Horde     after The Forsaken Blight (12221), the same
--   WRM-204  both      after Mystery of the Infinite: Chromie to Sylvanas, atop Wyrmrest Temple
--   WRM-205  Alliance  Sylvanas to Eternus at the Bazaar (taking it goes there); back to Durkon
--   WRM-215  Horde     the same; back to Doctor Sintar Malefious
--   WRM-201  Alliance  after WRM-205, Moratari by Durkon: opens Into Hostile Territory (12325)
--   WRM-211  Horde     after WRM-215, Moratari by Sintar: opens The Kor'kron Vanguard! (12224)
--   WRM-206  Alliance  after To Fordragon Hold! (12474), Moratari by Bolvar: to Eternus
--   WRM-216  Horde     after The Kor'kron Vanguard! (12224), Moratari by Saurfang: to Eternus
--   WRM-207  both      Eternus to Moratari: the turn, a scene at the Bazaar (RemixNpcs.cpp)
--   WRM-208  Alliance  Sylvanas to Alleria on the Wrathgate's cliffs: Eternus's loyalists; to
--                      Bolvar, whose Audience With The Dragon Queen (12495) now waits for it
--   WRM-218  Horde     the same; to Saurfang, Audience With The Dragon Queen (12496)
--   WRM-202  Alliance  after Return To Angrathar (12499)    by Alexstrasza, before Reborn From The Ashes
--   WRM-212  Horde     after Return To Angrathar (12500)    by Alexstrasza, before Darkness Stirs
--   WRM-221  Alliance  after The Battle For The Undercity (13377): to Amberpine Lodge, Chapter III
--   WRM-222  Horde     after The Battle For The Undercity (13267): to Conquest Hold, Chapter III,
--                      opening The Conqueror's Task (12468) in place of its Dragonblight breadcrumb
--
-- Who is seen where (conditions of type 30, object visibility; rechecked as the story's quests
-- move, WrathRemix.cpp): Sylvanas and Alleria atop Wyrmrest from WRM-204 until WRM-205; at the
-- Bazaar once WRM-207 is done, when Eternus is gone from it (or, for one who never saw the turn,
-- from Chapter VII's quests: below); the Bazaar's own Moratari hidden
-- while WRM-207's scene plays (its own Moratari acts); Alleria and the loyalists on the cliffs
-- during WRM-208. Ids and chains from the Remix world database (data/campaign_manifest.csv).

SET @MORATARI := 770001, @ETERNUS := 770002, @SYLVANAS := 770011, @ALLERIA := 770012, @CHROMIE := 27856,
    @SYLVANAS_ABROAD := 770014, @ALLERIA_ABROAD := 770015,
    @TURN_CREDIT := 770034, @INTERLOPER := 770041;

DELETE FROM `quest_template` WHERE `ID` IN (77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208,
  77211, 77212, 77213, 77215, 77216, 77218, 77221, 77222);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `VerifiedBuild`) VALUES
-- WRM-203 / 213: Moratari, after the first stretch of each side's chain. Chromie has sent for the
-- Timerunner by name.
(77203, 2, 24, 20, 65, 5, 0, 0, 1101,
 'A Summons from Wyrmrest',
 'Speak with Moratari again to travel to Wyrmrest Temple, where Chromie of the bronze dragonflight is asking for you.',
 'Something strange, $n. The Wyrmrest Accord has sent for you by name: not for a hero of the Alliance, but for you, as if someone up there knows what you are. That is a variable I did not account for.$B$BThe one asking is Chromie, of the bronze dragonflight. The bronze guard history the way any dragon guards a hoard, and they do not care for Eternus. I would rather know what she wants than wonder.$B$BI will take you to the temple. Be polite. She looks like a gnome. She is not.',
 'Speak with Moratari.', 0, 0, '', 0),
(77213, 2, 24, 20, 65, 5, 0, 0, 690,
 'A Summons from Wyrmrest',
 'Speak with Moratari again to travel to Wyrmrest Temple, where Chromie of the bronze dragonflight is asking for you.',
 'Something strange, $n. The Wyrmrest Accord has sent for you by name: not for a hero of the Horde, but for you, as if someone up there knows what you are. That is a variable I did not account for.$B$BThe one asking is Chromie, of the bronze dragonflight. The bronze guard history the way any dragon guards a hoard, and they do not care for Eternus. I would rather know what she wants than wonder.$B$BI will take you to the temple. Be polite. She looks like a gnome. She is not.',
 'Speak with Moratari.', 0, 0, '', 0),
-- WRM-204: Chromie, after Mystery of the Infinite. The two she brought back.
(77204, 2, 25, 20, 65, 5, 0, 0, 0,
 'Strangers Out of Time',
 'Speak with Sylvanas Windrunner, hooded as a ranger, beside Chromie atop Wyrmrest Temple.',
 'You did well with the hourglass. And yes, that was you. Don''t think about it too hard; I''ve tried.$B$BThe Infinite aren''t only out there, $n. One of them has been fetching heroes out of the years after this war and pointing them at it. Heroes like you. I know, because I went and fetched two people of my own, and they''re very unhappy about it.$B$BThey''re right behind you: the two rangers in the hoods. As far as anyone on this temple knows, they''re adventurers, same as you. The Banshee Queen of this year is very busy with a war of her own, and she must never hear that there are two of her.$B$BYes, the one in black is Sylvanas. From further along than you are; a good deal further. Try not to stare.$B$BAnd the other one... no. Talk to her yourself. Some faces should be seen, not described.',
 'Speak with Sylvanas Windrunner.', 0, 0, '', 0),
-- WRM-205 / 215: Sylvanas. Ask Eternus yourself (Chromie sends the Timerunner to the Bazaar).
(77205, 2, 25, 20, 65, 5, 0, 0, 1101,
 'Ask Her Yourself',
 'Speak with Eternus at the Infinite Bazaar.',
 'You do not believe me. Good. Belief is cheap.$B$BThen ask her yourself: what she means to do at the gate, and who will take up the Helm. Watch her face while she answers, and notice which question she does not.$B$BChromie will send you to her.',
 'Speak with Eternus.', 0, 0, '', 0),
(77215, 2, 25, 20, 65, 5, 0, 0, 690,
 'Ask Her Yourself',
 'Speak with Eternus at the Infinite Bazaar.',
 'You do not believe me. Good. Belief is cheap.$B$BThen ask her yourself: what she means to do at the gate, and who will take up the Helm. Watch her face while she answers, and notice which question she does not.$B$BChromie will send you to her.',
 'Speak with Eternus.', 0, 0, '', 0),
-- II-A, Alliance: Wintergarde's errands between Durkon's rescue and the push into hostile
-- territory (the crypt, the tome and the sermon; the mine, the demo-gnome and the war machine).
(77201, 2, 25, 20, 65, 5, 0, 0, 1101,
 'The Road to Angrathar',
 'Speak with Moratari again to return to High Commander Wyrmbane, ready to take the fight into hostile territory.',
 'Eternus asked me to keep you moving, and for once that is easy: Wintergarde has a tome to translate, a sermon to sit through, a mine to clear, and a gnome who is very good at blowing things up. None of it is where this war turns.$B$BThe High Commander has called his company back from Fordragon Hold; he needs every blade for the mausoleum under the old village. I did not stop the rider. A week ago, I would have.$B$BHe is ready to carry the fight into hostile territory, and the road he takes ends at Angrathar. The errands will keep, if you want them later. The sermon especially.',
 'Speak with Moratari.', 0, 0, '', 0),
-- II-A, Horde: Agmar's Hammer's errands around the Forsaken's blight (the taunka's oath, the
-- blightbeasts, the Icemist chief in the nerubians' pit).
(77211, 2, 25, 20, 65, 5, 0, 0, 690,
 'The Road to Angrathar',
 'Speak with Moratari again to return to Overlord Agmar, ready for the Kor''kron Vanguard.',
 'Eternus asked me to keep you moving, and for once that is easy: Agmar''s Hammer has an oath for the taunka to swear, the last of the blightbeasts you thinned over Icemist, and a high chief to pull out of a nerubian pit. The taunka will get their chief back without us; the Horde makes sure of it. None of it is where this war turns.$B$BOverlord Agmar is sending his best to the Kor''kron Vanguard, and Saurfang''s son will not wait for stragglers.$B$BAgmar will still have work for you later, if you want it. He always has work.',
 'Speak with Moratari.', 0, 0, '', 0),
-- WRM-206 / 216: Moratari, by Bolvar or by Saurfang's son, right before the Wrathgate's chain.
(77206, 2, 28, 20, 65, 5, 0, 0, 1101,
 'A Warning, Unwritten',
 'Speak with Eternus at the Infinite Bazaar.',
 'The Highlord is about to send you to the Dragonqueen. After that comes Angrathar, and the gate, and the day Eternus brought you here to change.$B$BShe has asked for you, $n. She says it is time you knew the whole of it, and she is waiting.',
 'Speak with Eternus.', 0, 0, '', 0),
(77216, 2, 28, 20, 65, 5, 0, 0, 690,
 'A Warning, Unwritten',
 'Speak with Eternus at the Infinite Bazaar.',
 'Saurfang''s son is about to send you to the Dragonqueen. After that comes Angrathar, and the gate, and the day Eternus brought you here to change.$B$BShe has asked for you, $n. She says it is time you knew the whole of it, and she is waiting.',
 'Speak with Eternus.', 0, 0, '', 0),
-- WRM-207: Eternus. The turn: its scene plays as it's taken (RemixNpcs.cpp), and gives its credit.
(77207, 2, 28, 20, 65, 5, 0, 0, 0,
 'The Weight of Time',
 'Hear what Sylvanas Windrunner has come to say at the Bazaar, then speak with Moratari.',
 'One more thing before you go to the cliffs, champion. Something has followed you from Wyrmrest Temple, and I would rather meet it here, among friends, than at the gate.$B$BStand with me.',
 'Speak with Moratari.', @TURN_CREDIT, 1, 'Sylvanas''s warning heard', 0),
-- WRM-208 / 218: Sylvanas, after the turn. Eternus's loyalists on the cliffs above the gate.
(77208, 2, 29, 20, 65, 5, 0, 0, 1101,
 'The Hour of the Gate',
 'Slay 6 Infinite Interlopers on the cliffs above the Wrathgate, then speak with Alleria Windrunner there.',
 'Eternus''s loyalists are on the cliffs above the Wrathgate, waiting where Putress''s men will stand. If they strike first, Bolvar lives, no one takes up the Helm, and everything I told Moratari comes to pass.$B$BMy sister is already there. Go to her, and kill every one of them you find. Leave the Forsaken be. I know what they will do. Let them.$B$BI will not come with you. Half the Forsaken on that field would know me by my walk, hood or no hood.',
 'Speak with Alleria Windrunner.', @INTERLOPER, 6, 'Infinite Interloper slain', 0),
(77218, 2, 29, 20, 65, 5, 0, 0, 690,
 'The Hour of the Gate',
 'Slay 6 Infinite Interlopers on the cliffs above the Wrathgate, then speak with Alleria Windrunner there.',
 'Eternus''s loyalists are on the cliffs above the Wrathgate, waiting where Putress''s men will stand. If they strike first, Saurfang''s son lives, and Bolvar, and no one takes up the Helm, and everything I told Moratari comes to pass.$B$BMy sister is already there. Go to her, and kill every one of them you find. Leave the Forsaken be. I know what they will do. Let them.$B$BI will not come with you. Half the Forsaken on that field would know me by my walk, hood or no hood.',
 'Speak with Alleria Windrunner.', @INTERLOPER, 6, 'Infinite Interloper slain', 0),
-- II-B: no skip. After the Wrathgate, by Alexstrasza, before what she asks next.
(77202, 2, 29, 20, 65, 5, 0, 0, 1101,
 'What We Cannot Change',
 'Speak with Moratari at the Wrathgate.',
 'You saw it. Saurfang''s son fallen before the gate, the Forsaken''s plague over everyone, Bolvar in the dragonfire. It happened as it did. We made sure of it, and it was right, and it does not feel right at all.$B$BSylvanas asked me to tell you something. Putress was hers, once. She did not order this. She remembers the day she heard of it, and taking her city back from the ones who did.$B$BThe Life-Binder has words for you. She will tell you Bolvar''s fall could not have been prevented. Let her believe it.',
 'Speak with Moratari.', 0, 0, '', 0),
(77212, 2, 29, 20, 65, 5, 0, 0, 690,
 'What We Cannot Change',
 'Speak with Moratari at the Wrathgate.',
 'You saw it. Saurfang''s son fallen before the gate, the Forsaken''s plague over everyone, Bolvar in the dragonfire. It happened as it did. We made sure of it, and it was right, and it does not feel right at all.$B$BSylvanas asked me to tell you something. Putress was hers, once. She did not order this. She remembers the day she heard of it, and taking her city back from the ones who did.$B$BThe Life-Binder has words for you. She will say that no one but the Timeless One could have seen this coming. Let her believe it.',
 'Speak with Moratari.', 0, 0, '', 0),
-- II-C (WRM-221): after the battle, the aftermath's errands, and Chapter III.
(77221, 2, 30, 20, 65, 5, 0, 0, 1101,
 'After Angrathar',
 'Speak with Moratari again to travel to Amberpine Lodge in the Grizzly Hills.',
 'It is over in the Undercity. Putress is dead, Varimathras is dead, and the King of Stormwind came within a breath of starting the next war on the spot. Jaina pulled him out of there before he could. History is grateful.$B$BSylvanas watched it from where her past self could not see her. She said nothing for a long time. Then she said it went exactly as she remembers, and walked away.$B$BThe Grizzly Hills, $n. Something is wrong at the heart of an old forest, and a troll named Drakuru is making friends. Eternus will be there before us. Chapter III begins at Amberpine Lodge.',
 'Speak with Moratari.', 0, 0, '', 0),
(77222, 2, 30, 20, 65, 5, 0, 0, 690,
 'After Angrathar',
 'Speak with Moratari again to travel to Conquest Hold in the Grizzly Hills.',
 'Lordaeron''s throne room is the Horde''s again. Varimathras is dead, Putress is dead, and the Alliance came within a breath of starting the next war. Jaina stopped it. History is grateful.$B$BSylvanas watched it from where her past self could not see her: the Banshee Queen taking back her city, beside Thrall. She said nothing for a long time. Then she said it went exactly as she remembers, and walked away.$B$BThe Grizzly Hills, $n. Something stirs beneath an old forest, and a troll named Drakuru is making friends. Eternus will be there before us. Chapter III begins at Conquest Hold.',
 'Speak with Moratari.', 0, 0, '', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208,
  77211, 77212, 77213, 77215, 77216, 77218, 77221, 77222);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES
(77203, 12311), (77213, 12221), (77204, 12470), (77205, 77204), (77215, 77204),
(77201, 77205), (77211, 77215), (77206, 12474), (77216, 12224),
-- (WRM-207 follows either side's WRM-206: the conditions below)
(77207, 0), (77208, 77207), (77218, 77207),
(77202, 12499), (77212, 12500), (77221, 13377), (77222, 13267);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208,
  77211, 77212, 77213, 77215, 77216, 77218, 77221, 77222);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77203, 1, 'Hold on. Wyrmrest Temple is very tall, and Chromie is very punctual.', 0),
(77213, 1, 'Hold on. Wyrmrest Temple is very tall, and Chromie is very punctual.', 0),
(77204, 1, 'So you are hers. You do not know what you have been doing, do you?$B$B<The ranger in the black hood looks at you a moment longer than she needs to.>$B$B...$n.$B$B<She stops herself.>$B$BNo. You do not know me. Not yet. Where I come from, you and I have stood together through more than I will ever tell you, and if I told you any of it now, you would go looking for it, and you would not find it the way you did. So I will not.$B$BChromie says you were taken from a tavern, after the war. You were toasting it.$B$B<Something crosses her face and is gone.>$B$BOf course you were.$B$B<She lowers her voice.>$B$BI am Sylvanas Windrunner. To everyone else on this temple I am a ranger passing through, and that is how it stays: the woman who wears my name in this year must never learn that I am here. I did not come here for your forgiveness.$B$BWhatever Eternus has promised you, Timerunner, the war against the Lich King must happen as it did. Every battle. Every grave. I know what it cost. I know better than anyone here what it cost me.$B$BStop helping her.', 0),
(77205, 1, 'Sylvanas Windrunner. The bronze sends the woman who will one day set a world tree burning with its people inside it, to lecture you on what must not change.$B$BI will not pretend the war I want is safe. I want it kinder. That is all I have ever wanted.$B$BKeep going, champion. Moratari will see you back to the front.', 0),
(77215, 1, 'Sylvanas Windrunner. The bronze sends the woman who will one day set a world tree burning with its people inside it, to lecture you on what must not change.$B$BI will not pretend the war I want is safe. I want it kinder. That is all I have ever wanted.$B$BKeep going, champion. Moratari will see you back to the front.', 0),
(77201, 1, 'Hold on to something. The High Commander does not like to be kept waiting.', 0),
(77211, 1, 'Hold on. Saurfang the Younger is a good man to stand beside. Remember that.', 0),
(77206, 1, 'Here is the whole of it, champion. At the Wrathgate, the Forsaken''s Royal Apothecary Society will turn on everyone there: Alliance, Horde and Scourge alike. Dranosh Saurfang will fall to the Lich King''s own blade before the gate, and then their plague will take Bolvar Fordragon, and thousands with him.$B$BMy loyalists are already on the cliffs above the gate, where Putress''s men will stand. Before the plague is loosed, they strike, and one of mine will be at Saurfang''s side when the gate opens. Bolvar walks home. Saurfang''s son walks home.$B$BAnd you will lead them.', 0),
(77216, 1, 'Here is the whole of it, champion. At the Wrathgate, the Forsaken''s Royal Apothecary Society will turn on everyone there: Horde, Alliance and Scourge alike. Dranosh Saurfang will fall to the Lich King''s own blade before the gate, and then their plague will take Bolvar Fordragon, and thousands with him.$B$BMy loyalists are already on the cliffs above the gate, where Putress''s men will stand. Before the plague is loosed, they strike, and one of mine will be at Saurfang''s side when the gate opens. Saurfang''s son walks home to his father. Bolvar walks home.$B$BAnd you will lead them.', 0),
(77207, 1, 'I kept Eternus''s records for longer than you have been alive, $n. I believed every word of them.$B$BI have seen it now with my own eyes: the road where Bolvar lives ends at a throne no one holds. Eternus knew. She knew, and she brought you here anyway.$B$BSo. We were on the wrong side, you and I. Now we are not. Sylvanas and Alleria will stay at the Bazaar with me. Eternus will not stop. Neither will we.', 0),
(77208, 1, 'That is the last of them, for today. Eternus will be back; she is too stubborn not to be.$B$B<She lowers her bow, and for a moment she looks at you instead of the cliffs.>$B$BYou went in ahead of me. Do that again and I will shoot you myself, and save Eternus the trouble.$B$BGo to the Highlord now. He will send you to the Dragonqueen, and then to the gate, and it will happen as it did.$B$BI am sorry, $n. That is the hard part of all this: we fought to make sure it happens.', 0),
(77218, 1, 'That is the last of them, for today. Eternus will be back; she is too stubborn not to be.$B$B<She lowers her bow, and for a moment she looks at you instead of the cliffs.>$B$BYou went in ahead of me. Do that again and I will shoot you myself, and save Eternus the trouble.$B$BGo to Saurfang''s son now. He will send you to the Dragonqueen, and then to the gate, and it will happen as it did.$B$BI am sorry, $n. That is the hard part of all this: we fought to make sure it happens.', 0),
(77202, 1, 'Go on. The Life-Binder is waiting, and Stormwind will not wait much longer.', 0),
(77212, 1, 'Go on. The Life-Binder is waiting, and so is a father at Warsong Hold.', 0),
(77221, 1, 'Hold on. The Grizzly Hills are kinder than the Dragonblight, which is not saying much.', 0),
(77222, 1, 'Hold on. The Grizzly Hills are kinder than the Dragonblight, which is not saying much.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208,
  77211, 77212, 77213, 77215, 77216, 77218, 77221, 77222);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(@MORATARI, 77203), (@MORATARI, 77213), (@CHROMIE, 77204), (@SYLVANAS_ABROAD, 77205), (@SYLVANAS_ABROAD, 77215),
(@MORATARI, 77201), (@MORATARI, 77211), (@MORATARI, 77206), (@MORATARI, 77216), (@ETERNUS, 77207),
(@SYLVANAS, 77208), (@SYLVANAS, 77218),
(@MORATARI, 77202), (@MORATARI, 77212), (@MORATARI, 77221), (@MORATARI, 77222);
DELETE FROM `creature_questender` WHERE `quest` IN (77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208,
  77211, 77212, 77213, 77215, 77216, 77218, 77221, 77222);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(@MORATARI, 77203), (@MORATARI, 77213), (@SYLVANAS_ABROAD, 77204), (@ETERNUS, 77205), (@ETERNUS, 77215),
(@MORATARI, 77201), (@MORATARI, 77211), (@ETERNUS, 77206), (@ETERNUS, 77216), (@MORATARI, 77207),
(@ALLERIA_ABROAD, 77208), (@ALLERIA_ABROAD, 77218),
(@MORATARI, 77202), (@MORATARI, 77212), (@MORATARI, 77221), (@MORATARI, 77222);

-- Where a quest takes the Timerunner as it's taken (WrathRemix.cpp): to the Bazaar, before
-- Eternus (who stands at its north side, facing south), and to the cliffs above the Wrathgate,
-- beside Alleria.
CREATE TABLE IF NOT EXISTS `remix_departure` (
  `quest` INT UNSIGNED NOT NULL,
  `map` SMALLINT UNSIGNED NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `o` FLOAT NOT NULL,
  PRIMARY KEY (`quest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DELETE FROM `remix_departure` WHERE `quest` IN (77205, 77215, 77206, 77216, 77208, 77218);
INSERT INTO `remix_departure` (`quest`, `map`, `x`, `y`, `z`, `o`) VALUES
(77205, 571, 6394.0, 1872.5, 508.7, 1.57),
(77215, 571, 6394.0, 1872.5, 508.7, 1.57),
(77206, 571, 6394.0, 1872.5, 508.7, 1.57),
(77216, 571, 6394.0, 1872.5, 508.7, 1.57),
(77208, 571, 4970.5, 1381.5, 282.0, 0.30),
(77218, 571, 4970.5, 1381.5, 282.0, 0.30);

DELETE FROM `remix_bridge` WHERE `quest` IN (77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208,
  77211, 77212, 77213, 77215, 77216, 77218, 77221, 77222);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES
-- Before High Commander Halford Wyrmbane's Into Hostile Territory, and Overlord Agmar's The
-- Kor'kron Vanguard!
(77201, 12325, 2, 571, 3764.6, -772.4, 196.1, 5.54, '12312 12319 12320 12321 12272 12275 12276 12277 12281'),
(77211, 12224, 2, 571, 3842.4, 1489.6, 92.1, 4.71, '11983 12008 12053 12071 12072 12064 12069 12140'),
-- At the Wrathgate: nothing skipped, nowhere to go.
(77202, 13347, 2, 65535, 0, 0, 0, 0, ''),
(77212, 13242, 2, 65535, 0, 0, 0, 0, ''),
-- To Chapter III's start for each side (remix_chapter's): Amberpine Lodge's Lieutenant Dumont, and
-- Conquest Hold, where Conqueror Krenna's The Conqueror's Task begins the Horde's chapter (it asks
-- for a breadcrumb from the Dragonblight, To Conquest Hold, But Be Careful!, which WRM-222 stands
-- for).
(77221, 12292, 3, 571, 3446.4, -2754.1, 199.4, 3.90, ''),
(77222, 12468, 3, 571, 3258.9, -2263.1, 114.4, 0.50, '12487');
-- The story's steps that take the Timerunner on: before Chromie (Mystery of the Infinite), back
-- before Durkon or Sintar and the Moratari beside them (The Road to Angrathar), before Bolvar or
-- Saurfang's son (Audience With The Dragon Queen). Four yards in front of each, facing them.
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`)
SELECT b.quest, b.next_quest, 2, c.`map`, c.`position_x` + 4 * COS(c.`orientation`), c.`position_y` + 4 * SIN(c.`orientation`),
  c.`position_z` + 0.5, MOD(c.`orientation` + PI(), 2 * PI()), ''
FROM `creature` c JOIN (
  SELECT 77203 AS quest, 12470 AS next_quest, 131083 AS facing UNION ALL
  SELECT 77213, 12470, 131083 UNION ALL
  SELECT 77205, 77201, 133653 UNION ALL
  SELECT 77215, 77211, 108123 UNION ALL
  SELECT 77208, 12495, 133759 UNION ALL
  SELECT 77218, 12496, 111852
) b ON c.`guid` = b.facing;

-- Into Hostile Territory opens with either II-A or both of the block's ends (The Scourge war
-- machine, and A Righteous Sermon). Their NextQuestID made the block's ends its only way in; the
-- conditions say it now.
UPDATE `quest_template_addon` SET `NextQuestID` = 0 WHERE `ID` IN (12281, 12321);
-- The Kor'kron Vanguard!: either II-A, or the four camps' last quests as the world has it.
-- The Conqueror's Task: either WRM-222 or the breadcrumb.
UPDATE `quest_template_addon` SET `PrevQuestID` = 0 WHERE `ID` = 12468;
-- WRM-207 follows either side's WRM-206. Audience With The Dragon Queen waits for the turn and
-- the cliffs (WRM-208 or 218): the Wrathgate's chain is the story's, after them.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (12325, 12224, 12468, 77207, 12495, 12496);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 12325, 0, 0, 8, 0, 77201, 0, 0, 0, 0, 0, '', 'Wrath Remix: Into Hostile Territory after The Road to Angrathar'),
(19, 0, 12325, 0, 1, 8, 0, 12281, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Understanding the Scourge War Machine'),
(19, 0, 12325, 0, 1, 8, 0, 12321, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... and A Righteous Sermon'),
(19, 0, 12224, 0, 0, 8, 0, 77211, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Kor''kron Vanguard! after The Road to Angrathar'),
(19, 0, 12224, 0, 1, 8, 0, 12008, 0, 0, 0, 0, 0, '', 'Requires quest rewarded'),
(19, 0, 12224, 0, 1, 8, 0, 12072, 0, 0, 0, 0, 0, '', 'Requires quest rewarded'),
(19, 0, 12224, 0, 1, 8, 0, 12140, 0, 0, 0, 0, 0, '', 'Requires quest rewarded'),
(19, 0, 12224, 0, 1, 8, 0, 12221, 0, 0, 0, 0, 0, '', 'Requires quest rewarded'),
(19, 0, 12468, 0, 0, 8, 0, 77222, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Conqueror''s Task after After Angrathar'),
(19, 0, 12468, 0, 1, 8, 0, 12487, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after To Conquest Hold, But Be Careful!'),
(19, 0, 77207, 0, 0, 8, 0, 77206, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Weight of Time after A Warning, Unwritten (Alliance)'),
(19, 0, 77207, 0, 1, 8, 0, 77216, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
(19, 0, 12495, 0, 0, 8, 0, 77208, 0, 0, 0, 0, 0, '', 'Wrath Remix: Audience With The Dragon Queen after The Hour of the Gate'),
(19, 0, 12496, 0, 0, 8, 0, 77218, 0, 0, 0, 0, 0, '', 'Wrath Remix: Audience With The Dragon Queen after The Hour of the Gate');

-- Who is seen where (type 30: object visibility, for the player; a spawn's own conditions, by its
-- guid, or every spawn of an entry's, guid 0). Conditions of one ElseGroup must all hold; any one
-- ElseGroup will do. Quest states: 2 objectives done, 8 in progress, 64 turned in.
-- (only its own: the later chapters' files have conditions for these people too)
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND (`SourceEntry` = @INTERLOPER OR
  (`SourceEntry` IN (@MORATARI, @ETERNUS, @SYLVANAS, @ALLERIA, @SYLVANAS_ABROAD, @ALLERIA_ABROAD) AND `SourceId` IN (7704011, 7704012, 7704013, 7704014, 7704033, 7704034, 7704035)));
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
-- The Bazaar: Eternus until the turn is done; its own Moratari but while the turn's scene plays;
-- Sylvanas and Alleria once it's done. One who never saw the turn (a death knight, who starts at
-- Chapter V; one the Chronologist sent past it) has it so all the same for Chapter VII and the end,
-- from the first of The Armies Are in Place (WRM-701/711), The Last Hour (WRM-721) or The Last
-- Necessary Battle (WRM-800) taken, done or turned in: Eternus gone (the Keepers in her place,
-- wrath_remix_world_0018_ending.sql), Sylvanas and Alleria there; never the three of them at
-- once. (Until then Chapter II is still there for them to play, Eternus's part in it with it.)
(30, 0, @ETERNUS, 7704011, 0, 47, 0, 77207, 66, 0, 1, 0, 0, '', 'Wrath Remix: Eternus gone from the Bazaar after The Weight of Time'),
(30, 0, @ETERNUS, 7704011, 0, 47, 0, 77701, 74, 0, 1, 0, 0, '', 'Wrath Remix: ... or from The Armies Are in Place (Alliance)'),
(30, 0, @ETERNUS, 7704011, 0, 47, 0, 77711, 74, 0, 1, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
(30, 0, @ETERNUS, 7704011, 0, 47, 0, 77721, 74, 0, 1, 0, 0, '', 'Wrath Remix: ... or from The Last Hour'),
(30, 0, @ETERNUS, 7704011, 0, 47, 0, 77800, 74, 0, 1, 0, 0, '', 'Wrath Remix: ... or from The Last Necessary Battle'),
(30, 0, @MORATARI, 7704012, 0, 47, 0, 77207, 8, 0, 1, 0, 0, '', 'Wrath Remix: the Bazaar''s Moratari away while The Weight of Time plays'),
(30, 0, @SYLVANAS, 7704013, 0, 47, 0, 77207, 66, 0, 0, 0, 0, '', 'Wrath Remix: Sylvanas at the Bazaar after The Weight of Time'),
(30, 0, @SYLVANAS, 7704013, 1, 47, 0, 77701, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Armies Are in Place (Alliance)'),
(30, 0, @SYLVANAS, 7704013, 2, 47, 0, 77711, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
(30, 0, @SYLVANAS, 7704013, 3, 47, 0, 77721, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Hour'),
(30, 0, @SYLVANAS, 7704013, 4, 47, 0, 77800, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Necessary Battle'),
(30, 0, @ALLERIA, 7704014, 0, 47, 0, 77207, 66, 0, 0, 0, 0, '', 'Wrath Remix: Alleria at the Bazaar after The Weight of Time'),
(30, 0, @ALLERIA, 7704014, 1, 47, 0, 77701, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Armies Are in Place (Alliance)'),
(30, 0, @ALLERIA, 7704014, 2, 47, 0, 77711, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
(30, 0, @ALLERIA, 7704014, 3, 47, 0, 77721, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Hour'),
(30, 0, @ALLERIA, 7704014, 4, 47, 0, 77800, 74, 0, 0, 0, 0, '', 'Wrath Remix: ... or from The Last Necessary Battle'),
-- Atop Wyrmrest Temple: from Strangers Out of Time until Ask Her Yourself is turned in.
(30, 0, @SYLVANAS_ABROAD, 7704033, 0, 47, 0, 77204, 74, 0, 0, 0, 0, '', 'Wrath Remix: Sylvanas at Wyrmrest from Strangers Out of Time'),
(30, 0, @SYLVANAS_ABROAD, 7704033, 0, 8, 0, 77205, 0, 0, 1, 0, 0, '', 'Wrath Remix: ... until Ask Her Yourself (Alliance)'),
(30, 0, @SYLVANAS_ABROAD, 7704033, 0, 8, 0, 77215, 0, 0, 1, 0, 0, '', 'Wrath Remix: ... until Ask Her Yourself (Horde)'),
(30, 0, @ALLERIA_ABROAD, 7704034, 0, 47, 0, 77204, 74, 0, 0, 0, 0, '', 'Wrath Remix: Alleria at Wyrmrest from Strangers Out of Time'),
(30, 0, @ALLERIA_ABROAD, 7704034, 0, 8, 0, 77205, 0, 0, 1, 0, 0, '', 'Wrath Remix: ... until Ask Her Yourself (Alliance)'),
(30, 0, @ALLERIA_ABROAD, 7704034, 0, 8, 0, 77215, 0, 0, 1, 0, 0, '', 'Wrath Remix: ... until Ask Her Yourself (Horde)'),
-- The Wrathgate's cliffs: Alleria during The Hour of the Gate, the loyalists while it's being done.
(30, 0, @ALLERIA_ABROAD, 7704035, 0, 47, 0, 77208, 10, 0, 0, 0, 0, '', 'Wrath Remix: Alleria on the cliffs during The Hour of the Gate'),
(30, 0, @ALLERIA_ABROAD, 7704035, 1, 47, 0, 77218, 10, 0, 0, 0, 0, '', 'Wrath Remix: ... the Horde''s'),
(30, 0, @INTERLOPER, 0, 0, 47, 0, 77208, 8, 0, 0, 0, 0, '', 'Wrath Remix: Eternus''s loyalists, for The Hour of the Gate'),
(30, 0, @INTERLOPER, 0, 1, 47, 0, 77218, 8, 0, 0, 0, 0, '', 'Wrath Remix: ... the Horde''s');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208,
  77211, 77212, 77213, 77215, 77216, 77218, 77221, 77222);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES
(77203, 600), (77213, 600), (77204, 1000), (77205, 600), (77215, 600),
(77201, 800), (77211, 800), (77206, 600), (77216, 600), (77207, 1500), (77208, 2500), (77218, 2500),
(77202, 500), (77212, 500), (77221, 1500), (77222, 1500);
