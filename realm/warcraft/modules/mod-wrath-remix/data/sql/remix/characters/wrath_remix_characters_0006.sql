-- The prologue's new steps (build 90): Old Habits (77020) and the Bazaar's Keepers (77021) come
-- between Time's Toll (77012) and A Small Demonstration (77013), which now waits for them. A
-- Timerunner who had already turned in Time's Toll under the old prologue has them counted as done,
-- so the demonstration is still there for them.
INSERT IGNORE INTO `character_queststatus_rewarded` (`guid`, `quest`, `active`)
SELECT r.`guid`, q.`quest`, 1
FROM `character_queststatus_rewarded` r
JOIN (SELECT 77020 AS `quest` UNION ALL SELECT 77021) q
WHERE r.`quest` = 77012;
