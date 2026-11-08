-- Wrath Remix (STORY.md, Chapter VII): the Forge of Souls' Sylvanas, the Banshee Queen of this year,
-- who knows nothing of the one from the future at the Bazaar. After her briefing (the game's own),
-- she names the one who asked her to begin, senses a presence she has not felt since she was alive,
-- and goes off to the other side of the hall, murmuring about her sisters if anyone speaks to her
-- (RemixFrozenHalls.cpp). The dungeon and its quests go on as they always do. Jaina, the Alliance's,
-- is as the game has her: the instance makes this same creature Jaina for an Alliance group, and
-- the script then gives her the game's own (npc_fos_leader, her briefing).

UPDATE `creature_template` SET `ScriptName` = 'npc_remix_fos_sylvanas' WHERE `entry` = 37596;

-- What she murmurs (npc_text 7703101 to 7703109).
DELETE FROM `npc_text` WHERE `ID` BETWEEN 7703101 AND 7703109;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(7703101, '<Sylvanas stands apart from the others, staring at nothing. She does not seem to notice you.>$B$B...Alleria? No. You went through the Portal, and you never came back. You never came back.$B$B<Her voice drops lower.>$B$BYou would not know me now, sister. I would not let you.', '<Sylvanas stands apart from the others, staring at nothing. She does not seem to notice you.>$B$B...Alleria? No. You went through the Portal, and you never came back. You never came back.$B$B<Her voice drops lower.>$B$BYou would not know me now, sister. I would not let you.', 1),
(7703102, '<Sylvanas is murmuring to herself, too low to be meant for anyone.>$B$BThe three of us at Windrunner Spire, and Lirath always underfoot. Alleria first out of every door. Vereesa always following. And I...$B$B<She falls silent. When she speaks again, her voice is cold.>$B$BIt is this place. It digs up the dead. Leave me.', '<Sylvanas is murmuring to herself, too low to be meant for anyone.>$B$BThe three of us at Windrunner Spire, and Lirath always underfoot. Alleria first out of every door. Vereesa always following. And I...$B$B<She falls silent. When she speaks again, her voice is cold.>$B$BIt is this place. It digs up the dead. Leave me.', 1),
(7703103, '<Sylvanas does not turn when you approach.>$B$BFor a moment I felt you, Alleria. As plainly as the day you left. That cannot be. You are gone, and I am... this.$B$B<Her hand tightens on her bow.>$B$BWhatever is watching us wears my sister''s shadow. When I find it, it will answer for that.', '<Sylvanas does not turn when you approach.>$B$BFor a moment I felt you, Alleria. As plainly as the day you left. That cannot be. You are gone, and I am... this.$B$B<Her hand tightens on her bow.>$B$BWhatever is watching us wears my sister''s shadow. When I find it, it will answer for that.', 1);
