-- Moratari's Hourglass (src/RemixHourglass.cpp): Moratari puts it in every Timerunner's bags as
-- they wake at the Bazaar (the module gives it, and gives it again if it's lost). Turned anywhere,
-- it takes them to the Bazaar; turned at the Bazaar, back where they came to it from. Its use is
-- the module's: the item's spell (a cosmetic one) is never cast.

SET @HOURGLASS := 77002;

-- The item: the Hearthstone's, renamed, with the Hourglass of Eternity's look and no cooldown.
DELETE FROM `item_template` WHERE `entry` = @HOURGLASS;
DROP TEMPORARY TABLE IF EXISTS `remix_hourglass_item`;
CREATE TEMPORARY TABLE `remix_hourglass_item` SELECT * FROM `item_template` WHERE `entry` = 6948;
UPDATE `remix_hourglass_item` SET `entry` = @HOURGLASS, `name` = 'Moratari''s Hourglass', `displayid` = 43101, `Quality` = 3,
  `ItemLevel` = 1, `RequiredLevel` = 0, `BuyPrice` = 0, `SellPrice` = 0, `bonding` = 1, `maxcount` = 1, `stackable` = 1,
  `spellid_1` = 52096, `spelltrigger_1` = 0, `spellcooldown_1` = -1, `spellcategory_1` = 0, `spellcategorycooldown_1` = -1,
  `ScriptName` = 'item_remix_hourglass',
  `description` = 'Turn it anywhere to go to the Infinite Bazaar, in Malykriss. Turn it at the Bazaar to go back to where you came from.';
INSERT INTO `item_template` SELECT * FROM `remix_hourglass_item`;
DROP TEMPORARY TABLE `remix_hourglass_item`;

-- What the game itself needs to know of it (written into the game's patch as the realm starts).
DELETE FROM `item_dbc` WHERE `ID` = @HOURGLASS;
INSERT INTO `item_dbc` (`ID`, `ClassID`, `SubclassID`, `Sound_Override_Subclassid`, `Material`, `DisplayInfoID`, `InventoryType`, `SheatheType`) VALUES
(@HOURGLASS, 15, 0, -1, -1, 43101, 0, 0);
