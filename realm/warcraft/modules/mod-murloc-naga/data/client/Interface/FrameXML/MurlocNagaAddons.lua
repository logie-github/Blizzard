-- SPDX-License-Identifier: GPL-3.0-or-later
-- The Murlocs and the Naga (mod-murloc-naga) for add-ons that know the races by a table of their own.
-- Loaded after the game's own interface code (the patch adds it to FrameXML.toc), before any add-on.
--
--  * Questie's 3.3.5 port reads the player's race id from the race's file name (QuestieCompat.ChrRaces,
--    the game's races alone), and stops at login on a race it hasn't. Each is its kin there, whose
--    quests are theirs on this realm: the night elves' for the murlocs, the trolls' for the naga.
--  * The barber shop's names for their hair choices (by their ChrRaces hair token, as the creation
--    screen's): the murlocs' fins, the naga's headdresses.

HAIR_MURLOC_STYLE = "Fins";
HAIR_MURLOC_COLOR = "Fin Color";
HAIR_NAGA_STYLE = "Headdress";
HAIR_NAGA_COLOR = "Headdress Color";

local KIN = { Murloc = 4, Naga_ = 8 };

local frame = CreateFrame("Frame");
frame:RegisterEvent("ADDON_LOADED");
frame:SetScript("OnEvent", function(self, event, name)
	local races = type(QuestieCompat) == "table" and QuestieCompat.ChrRaces;
	if ( type(races) == "table" ) then
		for file, id in pairs(KIN) do
			if ( races[file] == nil ) then
				races[file] = id;
			end
		end
	end
end);
