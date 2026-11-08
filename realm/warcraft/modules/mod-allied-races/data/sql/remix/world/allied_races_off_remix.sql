-- The allied races (mod-allied-races) are ChromieCraft's alone (the user: "Only chromie needs new
-- races"): their SQL (data/sql/chromiecraft) goes into ChromieCraft's world database only, and Wrath
-- Remix's game has no patch of theirs. This takes out of Remix's world database what earlier
-- releases put in it, so that no character or bot of theirs can be made there, and the realm's races
-- 15 to 18 are the game's own again (the creatures' races the game has there without the patch).
-- Characters of theirs made on Remix stay in its characters database, left out of the character
-- list (the core lists only the race and class pairs it has a start for). Safe to run again.

-- Their starts, stats, action bars and racials: no new character of theirs, player or bot.
DELETE FROM `playercreateinfo` WHERE `race` IN (15, 16, 17, 18);
DELETE FROM `playercreateinfo_action` WHERE `race` IN (15, 16, 17, 18);
DELETE FROM `player_race_stats` WHERE `Race` IN (15, 16, 17, 18);
DELETE FROM `playercreateinfo_spell_custom` WHERE `Spell` BETWEEN 98711 AND 98734;

-- The races and their looks as the game's own tables have them (races 15 to 18 the creatures', none
-- at 24 to 27): the module's rows over the server's tables go.
DELETE FROM `chrraces_dbc` WHERE `ID` IN (15, 16, 17, 18, 24, 25, 26, 27);
DELETE FROM `charsections_dbc` WHERE `ID` BETWEEN 920000 AND 969999 OR `RaceID` IN (24, 25, 26, 27);
