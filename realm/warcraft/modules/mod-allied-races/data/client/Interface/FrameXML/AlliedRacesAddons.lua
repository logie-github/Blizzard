-- SPDX-License-Identifier: GPL-3.0-or-later
-- The void elves, nightborne, Lightforged Draenei and Zandalari Trolls (mod-allied-races) for
-- add-ons that know the races by a table of their own. Loaded after the game's own interface code
-- (the patch adds it to FrameXML.toc), before any add-on.
--
--  * Questie's 3.3.5 port: it reads the player's race id from the race's file name
--    (QuestieCompat.ChrRaces, the game's races alone) and stopped with "attempt to perform
--    arithmetic on local 'playerRaceId' (a nil value)" (QuestiePlayer.lua). Each race is its start
--    race there, whose quests are theirs on this realm: the Draenei's for the void elves and the
--    Lightforged, the Forsaken's for the nightborne, the Tauren's for the Zandalari.

local START = { VoidElf = 11, Nightborne = 5, LightforgedDraenei = 11, ZandalariTroll = 6 };

local frame = CreateFrame("Frame");
frame:RegisterEvent("ADDON_LOADED");
frame:SetScript("OnEvent", function(self, event, name)
	-- (each add-on's files have run by its ADDON_LOADED; Questie reads the race later, at login)
	local races = type(QuestieCompat) == "table" and QuestieCompat.ChrRaces;
	if ( type(races) == "table" ) then
		for file, id in pairs(START) do
			if ( races[file] == nil ) then
				races[file] = id;
			end
		end
	end
end);
