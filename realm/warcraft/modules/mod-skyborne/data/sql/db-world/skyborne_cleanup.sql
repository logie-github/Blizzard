-- Ids an earlier build of the module used and this one doesn't: taken out of a world database that has them.
DELETE FROM `spell_script_names` WHERE `spell_id` = 98708;
DELETE FROM `item_template` WHERE `entry` = 98708;
DELETE FROM `spell_dbc` WHERE `ID` = 98708;
DELETE FROM `playercreateinfo_spell_custom` WHERE `Spell` = 98708;
DELETE FROM `charsections_dbc` WHERE `ID` BETWEEN 970000 AND 999999;
