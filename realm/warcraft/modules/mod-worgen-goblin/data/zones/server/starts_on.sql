-- The Worgen's and Goblins' new characters start in their starting areas (tools/zones/build_tables.py).
UPDATE `playercreateinfo` SET `map` = 648, `zone` = 4765, `position_x` = -8423.81, `position_y` = 1361.3, `position_z` = 104.671, `orientation` = 1.55428 WHERE `race` = 9 AND `class` <> 6;
UPDATE `playercreateinfo` SET `map` = 638, `zone` = 4756, `position_x` = -1451.53, `position_y` = 1403.35, `position_z` = 35.5561, `orientation` = 0.333847 WHERE `race` = 12 AND `class` <> 6;
UPDATE `chrraces_dbc` SET `CinematicSequenceID` = 172 WHERE `ID` = 9;
UPDATE `chrraces_dbc` SET `CinematicSequenceID` = 170 WHERE `ID` = 12;
