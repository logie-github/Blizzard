-- The voices Remix's people speak with as they're clicked on: a look's NPCSoundID in the game's
-- CreatureDisplayInfo.dbc, which Wrath Remix's patch for the game (src/ClientPatch.cpp) sets for
-- the looks named here. Moratari wears Lady Alistra's look (25458), a blood elf woman in dark
-- plate, which speaks as a death knight (NPCSounds 292): here it has no voice of its own (0), so
-- what's heard as she's clicked is hers, her own greetings (src/RemixVoices.cpp, remix_voice), and
-- not the game's blood elf woman's or death knight's. Lady Alistra, at Acherus, is quiet too on
-- this realm.
CREATE TABLE IF NOT EXISTS `remix_display_sound` (
  `display` INT UNSIGNED NOT NULL,
  `npc_sound` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`display`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELETE FROM `remix_display_sound`;
INSERT INTO `remix_display_sound` (`display`, `npc_sound`) VALUES
(25458, 0);
