-- Wrath++'s character creator (docs/wrathpp): the newer client's two steps, on the 3.3.5 creator.
--
--   Step 1, Race:      Gender at the top left, the races under it, the classes in a column on the right; Back, Customize.
--   Step 2, Customize: Gender and one button per customization (skin colour, face, hair style, hair colour, facial hair
--                      or the race's own name for it) with Randomize on the left; on the right a column of the chosen
--                      customization's options, one tile each, the one on lit, a number beside it, arrows to scroll;
--                      the name under the character; Back, Finish.
--
-- The client's own buttons do the work (races, classes, gender, the customization arrows, Randomize, the name, creating):
-- this moves them and adds the panels, so whatever they did they still do. Which option is on and how many there are
-- comes from WrathPP_GetCustomization (Wrath++'s native mod under WarcraftXL's runtime); without it the column has
-- Previous and Next only. The tiles are numbered (pictures of each option need the native mod to draw more models).
-- Put in by the app into Wrath++'s copy of the game only (Data/patch-X.MPQ, last in GlueXML.toc).

local ROWS = NUM_CHAR_CUSTOMIZATIONS or 5
local TILES = 5
local root = CharacterCreateFrame or CharacterCreate
local step = 1
local category = 1
local scroll = 0
local shownCurrent, shownCategory

local BACKDROP = {
	bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
	edgeFile = "Interface\\Glues\\Common\\Glue-Tooltip-Border",
	tile = true, tileSize = 16, edgeSize = 16,
	insets = { left = 4, right = 4, top = 4, bottom = 4 },
}

local function panel(name, parent, width, height)
	local f = CreateFrame("Frame", name, parent or root)
	f:SetWidth(width); f:SetHeight(height)
	f:SetBackdrop(BACKDROP)
	f:SetBackdropColor(0.05, 0.08, 0.25, 0.92)
	f:SetBackdropBorderColor(0.8, 0.8, 0.85, 1)
	return f
end

local function heading(parent, text)
	local s = parent:CreateFontString(nil, "OVERLAY", "GlueFontNormalLarge")
	s:SetPoint("TOP", parent, "TOP", 0, -10)
	s:SetText(text)
	return s
end

local function button(name, parent, text, width, onClick, template)
	local b = CreateFrame("Button", name, parent, template or "GlueButtonSmallTemplate")
	b:SetWidth(width or 140); b:SetHeight(30)
	b:SetText(text)
	b:SetScript("OnClick", onClick)
	return b
end

-- What the native mod says: which option is on (1-based) and how many there are, or nil.
local function customization(i)
	if ( type(WrathPP_GetCustomization) ~= "function" ) then return nil end
	return WrathPP_GetCustomization(i)
end

local function rowLabel(i)
	local text = _G["CharacterCustomizationButtonFrame"..i.."Text"]
	local name = text and text:GetText()
	if ( not name or name == "" ) then name = _G["CHAR_CUSTOMIZATION"..i.."_DESC"] or ("Option "..i) end
	return name
end

-- The panels -----------------------------------------------------------------------------------------------------

local genderPanel = panel("WrathppGenderPanel", root, 230, 92)
genderPanel:SetPoint("TOPLEFT", root, "TOPLEFT", 12, -12)
heading(genderPanel, "Gender")

local classPanel = panel("WrathppClassPanel", root, 110, 560)
classPanel:SetPoint("TOPRIGHT", root, "TOPRIGHT", -12, -12)
heading(classPanel, "Class")

local categoryPanel = panel("WrathppCategoryPanel", root, 230, 52 + ROWS * 38 + 40)
categoryPanel:SetPoint("TOPLEFT", genderPanel, "BOTTOMLEFT", 0, -6)

local optionPanel = panel("WrathppOptionPanel", root, 130, 40 + TILES * 98 + 40)
optionPanel:SetPoint("RIGHT", root, "RIGHT", -12, 10)

local badge = optionPanel:CreateFontString(nil, "OVERLAY", "GlueFontNormalLarge")
local status = optionPanel:CreateFontString(nil, "OVERLAY", "GlueFontHighlightSmall")
status:SetPoint("TOP", optionPanel, "BOTTOM", 0, -4)

-- Step 1's and step 2's own buttons.
local customizeButton = button("WrathppCustomizeButton", root, "Customize", 170, function() WrathppCreate_SetStep(2) end, "GlueButtonTemplate")
customizeButton:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", -150, 24)
local backButton = button("WrathppBackButton", root, "Back", 150, function() WrathppCreate_SetStep(1) end, "GlueButtonTemplate")
backButton:SetPoint("BOTTOM", root, "BOTTOM", -260, 24)
local finishButton = button("WrathppFinishButton", root, "Finish", 150, function() CharacterCreate_Okay() end, "GlueButtonTemplate")
finishButton:SetPoint("BOTTOM", root, "BOTTOM", 260, 24)

-- One button per customization on the left.
local categories = {}
for i = 1, ROWS do
	local b = button("WrathppCategory"..i, categoryPanel, rowLabel(i), 190, function()
		category = i
		scroll = 0
		WrathppCreate_Refresh()
	end)
	b:SetPoint("TOP", categoryPanel, "TOP", 0, -16 - (i - 1) * 38)
	categories[i] = b
end
local randomize = button("WrathppRandomize", categoryPanel, RANDOMIZE or "Randomize", 140, function() CharacterCreate_Randomize() end)
randomize:SetPoint("BOTTOM", categoryPanel, "BOTTOM", 0, 12)

-- The column of options on the right.
local tiles = {}
local function choose(target)
	local current, count = customization(category)
	if ( not current or not count ) then return end
	-- The client steps one at a time: the shorter way round, at most the whole way.
	local forward = (target - current) % count
	local back = (current - target) % count
	for _ = 1, math.min(forward, back) do
		if ( forward <= back ) then CharacterCustomization_Right(category) else CharacterCustomization_Left(category) end
	end
	WrathppCreate_Refresh()
end
for t = 1, TILES do
	local tile = CreateFrame("Button", "WrathppOptionTile"..t, optionPanel)
	tile:SetWidth(104); tile:SetHeight(92)
	tile:SetPoint("TOP", optionPanel, "TOP", 0, -36 - (t - 1) * 98)
	tile:SetBackdrop(BACKDROP)
	tile.number = tile:CreateFontString(nil, "OVERLAY", "GlueFontNormalLarge")
	tile.number:SetPoint("CENTER", tile, "CENTER", 0, 0)
	tile:SetScript("OnClick", function(self)
		if ( self.option == "previous" ) then CharacterCustomization_Left(category); WrathppCreate_Refresh()
		elseif ( self.option == "next" ) then CharacterCustomization_Right(category); WrathppCreate_Refresh()
		elseif ( self.option ) then choose(self.option) end
	end)
	tiles[t] = tile
end
local up = button("WrathppOptionsUp", optionPanel, "^", 100, function() scroll = math.max(0, scroll - 1); WrathppCreate_Refresh() end)
up:SetPoint("TOP", optionPanel, "TOP", 0, -6)
local down = button("WrathppOptionsDown", optionPanel, "v", 100, function() scroll = scroll + 1; WrathppCreate_Refresh() end)
down:SetPoint("BOTTOM", optionPanel, "BOTTOM", 0, 6)

-- Moving the client's own pieces --------------------------------------------------------------------------------

local function place()
	for _, name in ipairs({ "CharacterCreateGenderButtonMale", "CharacterCreateGenderButtonFemale" }) do
		local b = _G[name]
		if ( b ) then
			b:SetParent(genderPanel)
			b:ClearAllPoints()
			b:SetPoint("BOTTOM", genderPanel, "BOTTOM", name == "CharacterCreateGenderButtonMale" and -30 or 30, 12)
			b:Show()
		end
	end
	for i = 1, 12 do
		local b = _G["CharacterCreateClassButton"..i]
		if ( b ) then
			b:SetParent(classPanel)
			b:ClearAllPoints()
			b:SetPoint("TOP", classPanel, "TOP", 0, -40 - (i - 1) * 50)
		end
	end
	if ( CharacterCreateConfigurationFrame ) then
		-- The races stay where they are; the panel's other pieces are the panels above now.
		CharacterCreateConfigurationFrame:ClearAllPoints()
		CharacterCreateConfigurationFrame:SetPoint("TOPLEFT", genderPanel, "BOTTOMLEFT", -12, 10)
	end
	for i = 1, ROWS do
		local row = _G["CharacterCustomizationButtonFrame"..i]
		if ( row ) then row:Hide() end
	end
	if ( CharCreateRandomizeButton ) then CharCreateRandomizeButton:Hide() end
	if ( CharacterCreateCharacterClass ) then CharacterCreateCharacterClass:Hide() end
	if ( CharacterCreateCharacterRace ) then CharacterCreateCharacterRace:Hide() end
end

function WrathppCreate_Refresh()
	if ( step ~= 2 ) then return end
	for i = 1, ROWS do
		local b = categories[i]
		b:SetText(rowLabel(i))
		if ( i == category ) then b:LockHighlight() else b:UnlockHighlight() end
	end
	local current, count = customization(category)
	if ( current and count and count > 0 ) then
		scroll = math.max(0, math.min(scroll, count - TILES))
		-- The one on brought into view when it changes (the arrows scroll freely otherwise).
		if ( current ~= shownCurrent or category ~= shownCategory ) then
			if ( current <= scroll ) then scroll = current - 1 elseif ( current > scroll + TILES ) then scroll = current - TILES end
			shownCurrent, shownCategory = current, category
		end
		scroll = math.max(0, scroll)
		for t = 1, TILES do
			local option = scroll + t
			local tile = tiles[t]
			if ( option <= count ) then
				tile.option = option
				tile.number:SetText(option)
				if ( option == current ) then tile:SetBackdropBorderColor(1, 0.82, 0, 1) else tile:SetBackdropBorderColor(0.6, 0.6, 0.65, 1) end
				tile:Show()
			else
				tile.option = nil
				tile:Hide()
			end
		end
		local lit = tiles[current - scroll]
		if ( lit and current - scroll <= TILES ) then
			badge:ClearAllPoints()
			badge:SetPoint("RIGHT", lit, "LEFT", -6, 0)
			badge:SetText(current)
			badge:Show()
		else
			badge:Hide()
		end
		up:Show(); down:Show()
		status:SetText(current.." of "..count)
	else
		-- Without the native mod: the client's own previous and next.
		for t = 1, TILES do
			local tile = tiles[t]
			tile.option = (t == 1 and "previous") or (t == 2 and "next") or nil
			tile.number:SetText(t == 1 and "<" or ">")
			tile:SetBackdropBorderColor(0.6, 0.6, 0.65, 1)
			if ( tile.option ) then tile:Show() else tile:Hide() end
		end
		badge:Hide(); up:Hide(); down:Hide()
		status:SetText("Wrath++ add-on not running")
	end
end

function WrathppCreate_SetStep(n)
	step = n
	place()
	local race = n == 1
	if ( CharacterCreateConfigurationFrame ) then if ( race ) then CharacterCreateConfigurationFrame:Show() else CharacterCreateConfigurationFrame:Hide() end end
	if ( race ) then classPanel:Show() else classPanel:Hide() end
	if ( race ) then categoryPanel:Hide(); optionPanel:Hide() else categoryPanel:Show(); optionPanel:Show() end
	if ( race ) then customizeButton:Show() else customizeButton:Hide() end
	if ( race ) then backButton:Hide(); finishButton:Hide() else backButton:Show(); finishButton:Show() end
	if ( CharCreateOkayButton ) then CharCreateOkayButton:Hide() end
	if ( CharCreateBackButton ) then if ( race ) then CharCreateBackButton:Show() else CharCreateBackButton:Hide() end end
	for _, name in ipairs({ "CharacterCreateNameEdit", "CharacterCreateRandomName" }) do
		local f = _G[name]
		if ( f ) then if ( race ) then f:Hide() else f:Show() end end
	end
	genderPanel:Show()
	WrathppCreate_Refresh()
end

-- After the client's own changes: back to step 1 when the screen opens, the column again after anything changes.
local function after(name, fn)
	local original = _G[name]
	if ( type(original) ~= "function" ) then return end
	_G[name] = function(...)
		local a, b, c = original(...)
		fn()
		return a, b, c
	end
end
after("CharacterCreate_OnShow", function() category = 1; scroll = 0; WrathppCreate_SetStep(1) end)
for _, name in ipairs({ "CharacterCustomization_Left", "CharacterCustomization_Right", "CharacterCreate_Randomize",
		"SetCharacterRace", "SetCharacterGender", "SetCharacterClass", "CharacterCreate_UpdateHairCustomization" }) do
	after(name, function() place(); WrathppCreate_Refresh() end)
end

local elapsed = 0
optionPanel:SetScript("OnUpdate", function(self, delta)
	elapsed = elapsed + (delta or 0)
	if ( elapsed >= 0.25 ) then elapsed = 0; WrathppCreate_Refresh() end
end)
WrathppCreate_SetStep(1)
