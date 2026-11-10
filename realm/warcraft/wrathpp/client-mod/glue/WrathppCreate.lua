-- Wrath++'s character creator (realm/warcraft/wrathpp, docs/wrathpp): Legion's boxes on the right, each saying what it
-- is and which of how many is on, over the stock client's own five customization rows (skin colour, face, hair style,
-- hair colour, facial hair). Loaded last (the Wrath++ patch adds it to GlueXML.toc, in Wrath++'s copy of the game only).
--
-- The numbers come from WrathPP_GetCustomization(i) (the Wrath++ native mod under WarcraftXL's runtime): the stock
-- interface can't read them. Without it the rows stay as the stock client shows them.

local ROWS = NUM_CHAR_CUSTOMIZATIONS or 5
local WIDTH = 300

local header = CreateFrame("Frame", "WrathppCreateHeader", CharacterCustomizationButtonFrame1 and CharacterCustomizationButtonFrame1:GetParent() or CharacterCreate)
header:SetWidth(WIDTH); header:SetHeight(24)
local title = header:CreateFontString(nil, "OVERLAY", "GlueFontNormal")
title:SetPoint("CENTER", header, "CENTER", 0, 0)
title:SetText("Appearance")

local function decorate(i)
	local row = _G["CharacterCustomizationButtonFrame"..i]
	if ( not row ) then return nil end
	if ( not row.wrathppValue ) then
		row:SetWidth(WIDTH)
		local text = _G[row:GetName().."Text"]
		local middle = _G[row:GetName().."Middle"]
		if ( text and middle ) then
			text:ClearAllPoints()
			text:SetPoint("LEFT", middle, "LEFT", 4, 2)
		end
		local value = row:CreateFontString(nil, "OVERLAY", "GlueFontHighlightSmall")
		value:SetPoint("RIGHT", middle or row, "RIGHT", -4, 2)
		value:SetJustifyH("RIGHT")
		row.wrathppValue = value
	end
	return row
end

local function refresh()
	if ( not WrathPP_GetCustomization ) then
		header:Hide()
		return
	end
	header:Show()
	local first = decorate(1)
	if ( first ) then
		header:ClearAllPoints()
		header:SetPoint("BOTTOM", first, "TOP", -22, 4)
	end
	for i = 1, ROWS do
		local row = decorate(i)
		if ( row ) then
			local current, count = WrathPP_GetCustomization(i)
			if ( current and count and count > 0 ) then
				row.wrathppValue:SetText(current.." / "..count)
			else
				row.wrathppValue:SetText("")
			end
		end
	end
end

-- After every change the stock buttons make (and a few times a second, for the ones the client makes itself).
for _, name in ipairs({ "CharacterCustomization_Left", "CharacterCustomization_Right", "CharacterCreate_Randomize",
		"SetCharacterRace", "SetCharacterGender", "SetCharacterClass", "CharacterCreate_OnShow" }) do
	local original = _G[name]
	if ( type(original) == "function" ) then
		_G[name] = function(...)
			local a, b, c = original(...)
			refresh()
			return a, b, c
		end
	end
end
local elapsed = 0
header:SetScript("OnUpdate", function(self, delta)
	elapsed = elapsed + (delta or 0)
	if ( elapsed >= 0.25 ) then
		elapsed = 0
		refresh()
	end
end)
refresh()
