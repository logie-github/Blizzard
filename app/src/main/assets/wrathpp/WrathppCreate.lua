-- Wrath++'s character creator (docs/wrathpp): Legion's boxes on the right. The race's and class's description boxes on
-- the right are replaced by an "Appearance" column: one box per customization (skin colour, face, hair style, hair colour, facial
-- hair), each with its name, which of how many is on, and arrows. The stock rows on the left go into those boxes (their
-- arrows are the client's own), so nothing changes in what they do.
--
-- "3 / 9" needs WrathPP_GetCustomization (Wrath++'s native mod under WarcraftXL's runtime): the stock interface can't
-- read it. Without it the boxes show the names only, and the line at the column's foot says the add-on isn't running.
-- Put in by the app into Wrath++'s copy of the game only (Data/patch-X.MPQ, last in GlueXML.toc).

local ROWS = NUM_CHAR_CUSTOMIZATIONS or 5
local BOX_W, BOX_H, GAP = 300, 50, 6

local parent = CharacterCreateFrame or CharacterCreate
local panel = CreateFrame("Frame", "WrathppAppearance", parent)
panel:SetWidth(BOX_W + 24)
panel:SetHeight(48 + ROWS * (BOX_H + GAP) + 30)
panel:SetPoint("RIGHT", parent, "RIGHT", -24, 20)
panel:SetBackdrop({
	bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
	edgeFile = "Interface\\Glues\\Common\\Glue-Tooltip-Border",
	tile = true, tileSize = 16, edgeSize = 16,
	insets = { left = 4, right = 4, top = 4, bottom = 4 },
})
panel:SetBackdropColor(0, 0, 0, 0.75)
panel:SetFrameStrata("HIGH")

local title = panel:CreateFontString(nil, "OVERLAY", "GlueFontNormalLarge")
title:SetPoint("TOP", panel, "TOP", 0, -14)
title:SetText("Appearance")

local status = panel:CreateFontString(nil, "OVERLAY", "GlueFontHighlightSmall")
status:SetPoint("BOTTOM", panel, "BOTTOM", 0, 12)

local boxes = {}

local function box(i)
	if ( boxes[i] ) then return boxes[i] end
	local b = CreateFrame("Frame", "WrathppAppearanceBox"..i, panel)
	b:SetWidth(BOX_W); b:SetHeight(BOX_H)
	b:SetPoint("TOP", panel, "TOP", 0, -44 - (i - 1) * (BOX_H + GAP))
	b:SetBackdrop({
		bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
		edgeFile = "Interface\\Glues\\Common\\Glue-Tooltip-Border",
		tile = true, tileSize = 16, edgeSize = 12,
		insets = { left = 3, right = 3, top = 3, bottom = 3 },
	})
	b:SetBackdropColor(0.12, 0.10, 0.06, 0.9)
	b.name = b:CreateFontString(nil, "OVERLAY", "GlueFontNormalSmall")
	b.name:SetPoint("TOPLEFT", b, "TOPLEFT", 12, -8)
	b.value = b:CreateFontString(nil, "OVERLAY", "GlueFontNormalLarge")
	b.value:SetPoint("BOTTOMLEFT", b, "BOTTOMLEFT", 12, 9)
	-- The client's own row, its arrows kept, inside the box (its label frame hidden: the box says it).
	local row = _G["CharacterCustomizationButtonFrame"..i]
	if ( row ) then
		row:SetParent(b)
		row:ClearAllPoints()
		row:SetPoint("RIGHT", b, "RIGHT", 2, 0)
		row:SetWidth(70)
		for _, part in ipairs({ "Left", "Right", "Middle", "Text" }) do
			local region = _G[row:GetName()..part]
			if ( region ) then region:Hide() end
		end
		row:Show()
	end
	b.row = row
	boxes[i] = b
	return b
end

local function label(i)
	local row = _G["CharacterCustomizationButtonFrame"..i]
	local text = row and _G[row:GetName().."Text"]
	local name = text and text:GetText()
	if ( not name or name == "" ) then name = _G["CHAR_CUSTOMIZATION"..i.."_DESC"] or ("Option "..i) end
	return name
end

local function refresh()
	local native = type(WrathPP_GetCustomization) == "function"
	for i = 1, ROWS do
		local b = box(i)
		b.name:SetText(label(i))
		local current, count
		if ( native ) then current, count = WrathPP_GetCustomization(i) end
		if ( current and count and count > 0 ) then
			b.value:SetText(current.." of "..count)
		else
			b.value:SetText(native and "" or "-")
		end
	end
	if ( native ) then
		status:SetText("Wrath++ add-on running")
	else
		status:SetText("Wrath++ add-on not running: no numbers")
	end
end

local function place()
	-- The race's and class's description boxes were here (Legion's creator has none on screen): the column takes their place.
	if ( CharacterCreateCharacterClass ) then CharacterCreateCharacterClass:Hide() end
	if ( CharacterCreateCharacterRace ) then CharacterCreateCharacterRace:Hide() end
	panel:Show()
	refresh()
end

for _, name in ipairs({ "CharacterCustomization_Left", "CharacterCustomization_Right", "CharacterCreate_Randomize",
		"SetCharacterRace", "SetCharacterGender", "SetCharacterClass", "CharacterCreate_UpdateHairCustomization",
		"CharacterCreate_OnShow", "CharacterClass_OnClick", "CharacterRace_OnClick" }) do
	local original = _G[name]
	if ( type(original) == "function" ) then
		_G[name] = function(...)
			local a, b, c = original(...)
			place()
			return a, b, c
		end
	end
end

local elapsed = 0
panel:SetScript("OnUpdate", function(self, delta)
	elapsed = elapsed + (delta or 0)
	if ( elapsed >= 0.25 ) then
		elapsed = 0
		if ( CharacterCreateCharacterClass and CharacterCreateCharacterClass:IsShown() ) then CharacterCreateCharacterClass:Hide() end
		if ( CharacterCreateCharacterRace and CharacterCreateCharacterRace:IsShown() ) then CharacterCreateCharacterRace:Hide() end
		refresh()
	end
end)
place()
