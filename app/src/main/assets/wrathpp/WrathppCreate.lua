-- Wrath++'s character creator (docs/wrathpp): Shadowlands' creator, on the 3.3.5 game's creation screen.
--
--   Race and class: the Alliance's races down the left, the Horde's down the right, the sexes at the top, the
--                   classes in a row at the bottom over the name; Back, Customize.
--   Customize:      Shadowlands' categories of the race (Face, Hair, Accessories, Body, Markings) down the left; on
--                   the right the chosen category's options in Shadowlands' order, each a row: its name, the choice
--                   on (its number, colour swatch and name) between a previous and a next arrow; tapping the choice
--                   opens the list of them all. Randomize; the character turns under a finger, by the two turn
--                   buttons and by itself after a flick; the wheel (a pinch) and the two zoom buttons bring it
--                   nearer; lists longer than their panel scroll under a finger, eased; Back, Finish.
--
-- What an option is and how a choice reaches the game is WrathppLooks (made with the looks by
-- realm/warcraft/wrathpp/tools/sl_creator.py): 3.3.5 keeps five numbers a character, and Shadowlands' options are
-- packed into them (a face number is a face and an eye colour...). The numbers are read and set through Wrath++'s
-- native mod (WrathPP_GetCustomization, WrathPP_SetCustomization) and the game's own CycleCharCustomization.
-- Without the looks or the native mod the rows are the game's own five. WrathppUndead (written by the app when the
-- undead skins are imported) adds the Undead switch under Accessories: its skins are new colours after the race's own.
--
-- The game's own buttons do the work (races, classes, sexes, the name, creating): this moves them into its panels.
-- Anything that fails here puts the game's own screen back (WrathppCreate_Disable), with the reason on the screen.
-- Put in by the app into Wrath++'s copy of the game only (Data/patch-X.MPQ, last in GlueXML.toc).

local root = CharacterCreateFrame or CharacterCreate
local W = { step = 1, category = nil, undead = false, zoom = 1, focusY = 0.6, spin = 0 }
WrathppCreator = W
local made = {}
local function make(kind, name, parent, template)
	local f = CreateFrame(kind, name, parent, template)
	made[#made + 1] = f
	return f
end

local FIELD = { skin = 1, face = 2, hair = 3, haircolor = 4, feature = 5 }
local RACE_ID = { HUMAN = 1, ORC = 2, DWARF = 3, NIGHTELF = 4, SCOURGE = 5, TAUREN = 6, GNOME = 7, TROLL = 8, GOBLIN = 9, BLOODELF = 10, DRAENEI = 11 }
local ALLIANCE = { HUMAN = true, DWARF = true, NIGHTELF = true, GNOME = true, DRAENEI = true, WORGEN = true, VOIDELF = true,
	LIGHTFORGEDDRAENEI = true, HIGHORDER = true, PANDAREN = true, KULTIRAN = true, DARKIRONDWARF = true, MECHAGNOME = true }
local ROW_H, LIST_W = 58, 318
local GOLD = { 1, 0.82, 0 }

local BACKDROP = {
	bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
	edgeFile = "Interface\\Glues\\Common\\Glue-Tooltip-Border",
	tile = true, tileSize = 16, edgeSize = 16,
	insets = { left = 4, right = 4, top = 4, bottom = 4 },
}

local function build()

-- What a button or the screen runs: whatever fails in it puts the game's own screen back (WrathppCreate_Disable).
local function guarded(fn)
	return function(...)
		if ( W.off ) then return end
		local ok, err = pcall(fn, ...)
		if ( not ok ) then WrathppCreate_Disable(err) end
	end
end

-- Small pieces ---------------------------------------------------------------------------------------------------

local function fontOf(wanted, fallback) return (type(_G[wanted]) == "table" and wanted) or fallback end
local FONT_TITLE = fontOf("GlueFontNormalLarge", "GlueFontNormalLarge")
local FONT_LABEL = fontOf("GlueFontNormal", "GlueFontNormalLarge")
local FONT_TEXT = fontOf("GlueFontHighlight", "GlueFontHighlightSmall")
local FONT_SMALL = fontOf("GlueFontHighlightSmall", "GlueFontHighlightSmall")

local function panel(name, parent, width, height)
	local f = make("Frame", name, parent or root)
	f:SetWidth(width); f:SetHeight(height)
	f:SetBackdrop(BACKDROP)
	f:SetBackdropColor(0.03, 0.03, 0.05, 0.86)
	f:SetBackdropBorderColor(0.55, 0.5, 0.4, 1)
	return f
end

local function text(parent, font, layer)
	local s = parent:CreateFontString(nil, layer or "OVERLAY", font or FONT_TEXT)
	return s
end

local function glueButton(name, parent, label, width, onClick, template)
	local b = make("Button", name, parent, template or "GlueButtonSmallTemplate")
	b:SetWidth(width or 140); b:SetHeight(template and 36 or 30)
	b:SetText(label)
	b:SetScript("OnClick", guarded(onClick))
	return b
end

-- A plain button made here: a dark box with a border that lights, and a label.
local function box(name, parent, width, height)
	local b = make("Button", name, parent)
	b:SetWidth(width); b:SetHeight(height)
	b:SetBackdrop(BACKDROP)
	b:SetBackdropColor(0.08, 0.08, 0.1, 0.95)
	b:SetBackdropBorderColor(0.5, 0.46, 0.38, 1)
	b.label = text(b, FONT_TEXT)
	b.label:SetPoint("CENTER", b, "CENTER", 0, 0)
	b.Lit = function(self, on)
		if ( on ) then self:SetBackdropBorderColor(GOLD[1], GOLD[2], GOLD[3], 1) else self:SetBackdropBorderColor(0.5, 0.46, 0.38, 1) end
	end
	return b
end

local function swatch(parent, size)
	local t = parent:CreateTexture(nil, "ARTWORK")
	t:SetWidth(size); t:SetHeight(size)
	return t
end

local function paint(tex, colour)
	if ( not colour ) then tex:Hide(); return end
	local r = math.floor(colour / 65536) % 256
	local g = math.floor(colour / 256) % 256
	local b = colour % 256
	tex:SetTexture(r / 255, g / 255, b / 255, 1)
	tex:Show()
end

local function cursor()
	local x, y = GetCursorPosition()
	return x or 0, y or 0
end

-- The character being made --------------------------------------------------------------------------------------

-- race id, sex (0 a man, 1 a woman), whether a death knight
local function creating()
	if ( type(WrathPP_GetCreating) == "function" ) then
		local race, sex, class = WrathPP_GetCreating()
		if ( race ) then return race, sex, class == 6 end
	end
	local _, token = GetNameForRace()
	local race = token and RACE_ID[string.upper(token)] or 0
	local sex = (GetSelectedSex() == (SEX_FEMALE or 3)) and 1 or 0
	local _, class = GetSelectedClass()
	return race, sex, class == "DEATHKNIGHT"
end

local function looks()
	local race, sex, dk = creating()
	local key = race.."_"..sex
	local all = type(WrathppLooks) == "table" and WrathppLooks.models
	local undead = type(WrathppUndead) == "table" and WrathppUndead.models
	return all and all[key], undead and undead[key], dk, key
end

-- The game's number i (1 skin, 2 face, 3 hair style, 4 hair colour, 5 feature): the one on from 0, how many.
local function number(i)
	if ( type(WrathPP_GetCustomization) ~= "function" ) then return nil end
	local current, count = WrathPP_GetCustomization(i)
	if ( not current or not count or count < 1 ) then return nil end
	return current - 1, count
end

local function step(i, delta)
	CycleCharCustomization(i, delta)
end

-- Sets the game's number i to target (from 0): by the native mod in one move, else by the game's own steps.
local function setNumber(i, target)
	local current, count = number(i)
	if ( not current or target < 0 or target >= count or current == target ) then return current == target end
	if ( type(WrathPP_SetCustomization) == "function" ) then
		-- the one before it put in, and the game's own "next" moves onto it and draws
		WrathPP_SetCustomization(i, ((target - 1) % count) + 1)
		step(i, 1)
		current = number(i)
		if ( current == target ) then return true end
	end
	local forward = (target - current) % count
	local back = (current - target) % count
	for _ = 1, math.min(forward, back) do
		step(i, forward <= back and 1 or -1)
	end
	return number(i) == target
end

local function decode(value, parts)
	local digits = {}
	for k = #parts, 1, -1 do
		digits[k] = value % parts[k]
		value = math.floor(value / parts[k])
	end
	return digits
end

local function encode(digits, parts)
	local value = 0
	for k = 1, #parts do value = value * parts[k] + (digits[k] or 0) end
	return value
end

local function product(parts)
	local n = 1
	for k = 1, #parts do n = n * parts[k] end
	return n
end

-- The rows of a category --------------------------------------------------------------------------------------------

local function allowed(choice, dk)
	if ( choice.c == "dk" ) then return dk end
	if ( choice.c == "nodk" ) then return not dk end
	return true
end

-- Whether the skin on is one of the undead's (the colours after the race's own).
local function undeadOn(model, undead)
	if ( not model or not undead ) then return false end
	local skin = number(FIELD.skin)
	return skin ~= nil and skin >= undead.first
end

-- The rows to show: { name, kind ("list", "switch", "plain"), choices, at (index of the one on), option, ... }
function W.Rows()
	local model, undead, dk = looks()
	local rows = {}
	if ( not model or not number(FIELD.skin) ) then
		-- the game's own five
		for i = 1, (NUM_CHAR_CUSTOMIZATIONS or 5) do
			local label = _G["CharacterCustomizationButtonFrame"..i.."Text"]
			local name = (label and label:GetText()) or _G["CHAR_CUSTOMIZATION"..i.."_DESC"] or ("Option "..i)
			local current, count = number(i)
			local row = { name = name, kind = current and "list" or "plain", index = i, at = current and current + 1, choices = {} }
			for k = 1, count or 0 do row.choices[k] = { v = k - 1, n = "" } end
			rows[#rows + 1] = row
		end
		return rows, nil
	end
	local isUndead = undeadOn(model, undead)
	local accessories
	for _, c in ipairs(model.categories) do
		if ( c.name == "Accessories" ) then accessories = c.id end
	end
	accessories = accessories or model.categories[#model.categories].id
	for _, option in ipairs(model.options) do
		if ( option.category == W.category ) then
			local row = { name = option.name, option = option, kind = option.type == 1 and "switch" or "list", choices = {} }
			local skinColour = option.field == "skin" and option.part == #model.fields.skin
			if ( not option.field ) then
				row.kind = "later"
				for _, c in ipairs(option.choices) do if ( allowed(c, dk) ) then row.choices[#row.choices + 1] = c end end
			elseif ( isUndead and option.field == "skin" and not skinColour ) then
				row = nil                                   -- a tattoo is the living skins' own
			elseif ( isUndead and option.field == "face" and option.part == 1 ) then
				row = nil                                   -- an undead skin has its own face
			elseif ( isUndead and skinColour ) then
				local skin = number(FIELD.skin)
				for k, c in ipairs(undead.skins) do
					row.choices[k] = { v = undead.first + k - 1, n = c.n, s = c.s, whole = true }
					if ( skin == undead.first + k - 1 ) then row.at = k end
				end
			else
				local value = number(FIELD[option.field])
				local digit = decode(math.min(value, product(model.fields[option.field]) - 1), model.fields[option.field])[option.part]
				for _, c in ipairs(option.choices) do
					if ( allowed(c, dk) ) then
						row.choices[#row.choices + 1] = c
						if ( c.v == digit ) then row.at = #row.choices end
					end
				end
			end
			if ( row and (#row.choices > 1 or row.kind == "later") ) then rows[#rows + 1] = row end
		end
	end
	if ( undead and W.category == accessories ) then
		rows[#rows + 1] = { name = "Undead", kind = "switch", undead = true, on = isUndead }
	end
	return rows, model
end

-- Puts a row's choice on.
function W.Choose(row, k)
	local model, undead = looks()
	if ( row.index ) then
		if ( k == "next" ) then step(row.index, 1) elseif ( k == "previous" ) then step(row.index, -1) else setNumber(row.index, k - 1) end
		return
	end
	local choice = row.choices[k]
	if ( not choice or not model or row.kind == "later" ) then return end
	if ( choice.whole ) then
		setNumber(FIELD.skin, choice.v)
		return
	end
	local field = row.option.field
	local parts = model.fields[field]
	local digits = decode(math.min(number(FIELD[field]), product(parts) - 1), parts)
	digits[row.option.part] = choice.v
	setNumber(FIELD[field], encode(digits, parts))
end

-- The living skin that was on before Undead, kept a race and sex, so turning it off goes back to it.
W.living = {}

function W.SetUndead(on)
	local model, undead, _, key = looks()
	if ( not model or not undead ) then return end
	local skin = number(FIELD.skin)
	if ( on and skin < undead.first ) then
		W.living[key] = skin
		setNumber(FIELD.skin, undead.first)
	elseif ( not on and skin >= undead.first ) then
		setNumber(FIELD.skin, W.living[key] or 0)
	end
end

-- After the game's own Randomize: an undead skin only while Undead is on, a living one otherwise.
function W.AfterRandomize(wasUndead)
	local model, undead = looks()
	if ( not model or not undead ) then return end
	local skin = number(FIELD.skin)
	if ( not skin ) then return end
	if ( wasUndead and skin < undead.first ) then
		setNumber(FIELD.skin, undead.first + math.random(#undead.skins) - 1)
	elseif ( not wasUndead and skin >= undead.first ) then
		setNumber(FIELD.skin, math.random(undead.first) - 1)
	end
end

-- A list that scrolls under a finger ---------------------------------------------------------------------------------

-- scroller(name, parent, width, height): .child holds the content, :SetContentHeight(h), :Watch(frame) makes a frame
-- inside it pass a drag on. A drag moves the content with the finger and carries on after a flick; the wheel moves it
-- three rows; both ease to rest and stop at the ends.
local scrollers = {}
local function scroller(name, parent, width, height)
	local s = make("ScrollFrame", name, parent)
	s:SetWidth(width); s:SetHeight(height)
	s.child = make("Frame", name and (name.."Child") or nil, s)
	s.child:SetWidth(width); s.child:SetHeight(height)
	s:SetScrollChild(s.child)
	s.offset, s.target, s.velocity, s.content, s.view = 0, 0, 0, height, height
	s.bar = s:CreateTexture(nil, "OVERLAY")
	s.bar:SetWidth(4)
	s.bar:SetTexture(GOLD[1], GOLD[2], GOLD[3], 0.7)
	s.bar:Hide()
	function s:Limit() return math.max(0, self.content - self.view) end
	function s:SetContentHeight(h)
		self.content = h
		self.child:SetHeight(math.max(h, 1))
		self.target = math.min(self.target, self:Limit())
		self.offset = math.min(self.offset, self:Limit())
		self:Place()
	end
	function s:SetView(h) self.view = h; self:SetHeight(h); self:SetContentHeight(self.content) end
	function s:Place()
		self:SetVerticalScroll(self.offset)
		local limit = self:Limit()
		if ( limit <= 0 ) then self.bar:Hide(); return end
		local length = math.max(24, self.view * self.view / self.content)
		self.bar:SetHeight(length)
		self.bar:ClearAllPoints()
		self.bar:SetPoint("TOPRIGHT", self, "TOPRIGHT", -1, -(self.view - length) * (self.offset / limit))
		self.bar:Show()
	end
	function s:ScrollTo(offset) self.target = math.max(0, math.min(offset, self:Limit())); self.velocity = 0 end
	function s:Reveal(top, bottom)
		if ( top < self.target ) then self:ScrollTo(top) elseif ( bottom > self.target + self.view ) then self:ScrollTo(bottom - self.view) end
	end
	function s:Press()
		local _, y = cursor()
		self.dragging, self.pressY, self.pressOffset, self.lastY, self.moved, self.velocity = true, y, self.offset, y, false, 0
	end
	function s:Release() self.dragging = false; self.target = self.offset + self.velocity * 0.25; self.target = math.max(0, math.min(self.target, self:Limit())) end
	-- A tap on something inside counts only if the finger didn't drag the list.
	function s:Tapped() return not self.moved end
	function s:Watch(frame)
		local list = self
		frame:SetScript("OnMouseDown", function() list:Press() end)
		frame:SetScript("OnMouseUp", function() list:Release() end)
	end
	function s:Update(elapsed)
		if ( self.dragging ) then
			local _, y = cursor()
			local scale = (self.GetEffectiveScale and self:GetEffectiveScale()) or 1
			if ( scale <= 0 ) then scale = 1 end
			local moved = (y - self.pressY) / scale
			if ( math.abs(moved) > 6 ) then self.moved = true end
			if ( self.moved ) then
				local offset = math.max(0, math.min(self.pressOffset + moved, self:Limit()))
				if ( elapsed > 0 ) then self.velocity = 0.6 * self.velocity + 0.4 * ((y - self.lastY) / scale) / elapsed end
				self.offset, self.target = offset, offset
				self:Place()
			end
			self.lastY = y
		elseif ( self.offset ~= self.target ) then
			local gap = self.target - self.offset
			local move = gap * math.min(1, elapsed * 12)
			if ( math.abs(gap) < 0.5 ) then self.offset = self.target else self.offset = self.offset + move end
			self:Place()
		end
	end
	s:EnableMouse(true)
	s:EnableMouseWheel(true)
	s:SetScript("OnMouseWheel", function(self, delta) self:ScrollTo(self.target - (delta or arg1 or 0) * ROW_H * 1.5) end)
	s:Watch(s)
	scrollers[#scrollers + 1] = s
	return s
end

-- The panels -----------------------------------------------------------------------------------------------------------

local alliancePanel = panel("WrathppAlliancePanel", root, 236, 420)
alliancePanel:SetPoint("TOPLEFT", root, "TOPLEFT", 14, -14)
local allianceTitle = text(alliancePanel, FONT_TITLE); allianceTitle:SetPoint("TOP", alliancePanel, "TOP", 0, -12); allianceTitle:SetText(FACTION_ALLIANCE or "Alliance")

local hordePanel = panel("WrathppHordePanel", root, 236, 420)
hordePanel:SetPoint("TOPRIGHT", root, "TOPRIGHT", -14, -14)
local hordeTitle = text(hordePanel, FONT_TITLE); hordeTitle:SetPoint("TOP", hordePanel, "TOP", 0, -12); hordeTitle:SetText(FACTION_HORDE or "Horde")

local sexPanel = panel("WrathppSexPanel", root, 150, 64)
sexPanel:SetPoint("TOP", root, "TOP", 0, -14)

local classPanel = panel("WrathppClassPanel", root, 560, 92)
classPanel:SetPoint("BOTTOM", root, "BOTTOM", 0, 92)
local className = text(classPanel, FONT_LABEL); className:SetPoint("TOP", classPanel, "TOP", 0, -8)

local categoryPanel = panel("WrathppCategoryPanel", root, 184, 100)
categoryPanel:SetPoint("TOPLEFT", root, "TOPLEFT", 14, -14)

local optionPanel = panel("WrathppOptionPanel", root, LIST_W + 22, 560)
optionPanel:SetPoint("TOPRIGHT", root, "TOPRIGHT", -14, -64)
local optionTitle = text(optionPanel, FONT_TITLE); optionTitle:SetPoint("TOP", optionPanel, "TOP", 0, -10)
local optionList = scroller("WrathppOptionList", optionPanel, LIST_W, 500)
optionList:SetPoint("TOPLEFT", optionPanel, "TOPLEFT", 11, -38)
local notice = text(optionPanel, FONT_SMALL); notice:SetPoint("TOP", optionPanel, "BOTTOM", 0, -4)

local viewPanel = make("Frame", "WrathppViewPanel", root)
viewPanel:SetWidth(260); viewPanel:SetHeight(44)
viewPanel:SetPoint("BOTTOM", root, "BOTTOM", 0, 92)

-- The buttons at the foot.
local customizeButton = glueButton("WrathppCustomizeButton", root, "Customize", 170, function() WrathppCreate_SetStep(2) end, "GlueButtonTemplate")
customizeButton:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", -24, 24)
local backButton = glueButton("WrathppBackButton", root, BACK or "Back", 150, function() WrathppCreate_SetStep(1) end, "GlueButtonTemplate")
backButton:SetPoint("BOTTOMLEFT", root, "BOTTOMLEFT", 24, 24)
local finishButton = glueButton("WrathppFinishButton", root, "Finish", 170, function()
	if ( type(CharacterCreate_Okay) == "function" ) then CharacterCreate_Okay() else CreateCharacter(CharacterCreateNameEdit:GetText()) end
end, "GlueButtonTemplate")
finishButton:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", -24, 24)
local randomizeButton = glueButton("WrathppRandomize", root, RANDOMIZE or "Randomize", 150, function()
	local model, undead = looks()
	local wasUndead = undeadOn(model, undead)
	if ( type(CharacterCreate_Randomize) == "function" ) then CharacterCreate_Randomize() else RandomizeCharCustomization() end
	W.AfterRandomize(wasUndead)
	WrathppCreate_Refresh()
end)
randomizeButton:SetPoint("BOTTOMRIGHT", optionPanel, "TOPRIGHT", 0, 6)

-- Turning and zooming ------------------------------------------------------------------------------------------------

local function facing() return (type(GetCharacterCreateFacing) == "function" and GetCharacterCreateFacing()) or 0 end
local function turn(degrees)
	if ( type(SetCharacterCreateFacing) == "function" ) then SetCharacterCreateFacing(facing() + degrees) end
end

-- The game's preview is the screen's model frame, whose camera no script moves: a model frame draws its scene to fit
-- its rectangle, so nearer is that frame made larger around where the character stands (mod-skyborne's zoom).
function W.ApplyZoom()
	local model, screen = CharacterCreate, GlueParent
	if ( type(model) ~= "table" or type(screen) ~= "table" or model == root ) then return end
	local w, h = screen:GetWidth(), screen:GetHeight()
	if ( not w or not h or w <= 0 or h <= 0 ) then return end
	root:ClearAllPoints(); root:SetAllPoints(screen)
	model:ClearAllPoints()
	if ( W.zoom <= 1.001 ) then model:SetAllPoints(screen); return end
	local fx, fy = w * 0.5, h * W.focusY
	model:SetPoint("BOTTOMLEFT", screen, "BOTTOMLEFT", fx - fx * W.zoom, fy - fy * W.zoom)
	model:SetPoint("TOPRIGHT", screen, "BOTTOMLEFT", fx + (w - fx) * W.zoom, fy + (h - fy) * W.zoom)
end

function W.SetZoom(zoom, focusY)
	W.zoomTarget = math.max(1, math.min(zoom, 2.6))
	if ( focusY ) then W.focusTarget = focusY end
end

-- The middle of the screen: a finger across it turns the character (and, while zoomed, up and down moves the view).
local spinArea = make("Button", "WrathppSpinArea", root)
spinArea:SetPoint("TOPLEFT", root, "TOPLEFT", 260, -90)
spinArea:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", -(LIST_W + 50), 196)
spinArea:EnableMouseWheel(true)
spinArea:SetScript("OnMouseDown", function()
	local x, y = cursor()
	W.turning, W.lastX, W.lastY, W.spin = true, x, y, 0
end)
spinArea:SetScript("OnMouseUp", function() W.turning = false end)
spinArea:SetScript("OnMouseWheel", function(self, delta) W.SetZoom((W.zoomTarget or W.zoom) + (delta or arg1 or 0) * 0.2) end)

local function holdButton(name, parent, label, width, held, tapped)
	local b = box(name, parent, width, 40)
	b.label:SetText(label)
	b:SetScript("OnMouseDown", function(self) self.held = true; self:Lit(true) end)
	b:SetScript("OnMouseUp", function(self) self.held = false; self:Lit(false) end)
	b:SetScript("OnClick", guarded(tapped or function() end))
	b.whileHeld = held
	return b
end
local turnLeft = holdButton("WrathppTurnLeft", viewPanel, "<<", 60, function(elapsed) turn(-140 * elapsed) end)
turnLeft:SetPoint("LEFT", viewPanel, "LEFT", 0, 0)
local zoomOut = holdButton("WrathppZoomOut", viewPanel, "-", 60, nil, function() W.SetZoom((W.zoomTarget or W.zoom) - 0.3) end)
zoomOut:SetPoint("LEFT", turnLeft, "RIGHT", 6, 0)
local zoomIn = holdButton("WrathppZoomIn", viewPanel, "+", 60, nil, function() W.SetZoom((W.zoomTarget or W.zoom) + 0.3) end)
zoomIn:SetPoint("LEFT", zoomOut, "RIGHT", 6, 0)
local turnRight = holdButton("WrathppTurnRight", viewPanel, ">>", 60, function(elapsed) turn(140 * elapsed) end)
turnRight:SetPoint("LEFT", zoomIn, "RIGHT", 6, 0)

-- The categories -------------------------------------------------------------------------------------------------------

local categoryButtons = {}
local function categoryButton(k)
	local b = categoryButtons[k]
	if ( not b ) then
		b = box("WrathppCategory"..k, categoryPanel, 160, 42)
		b:SetPoint("TOP", categoryPanel, "TOP", 0, -12 - (k - 1) * 48)
		b:SetScript("OnClick", guarded(function(self)
			W.category = self.category
			WrathppCreate_ClosePopout()
			optionList:ScrollTo(0)
			-- Shadowlands brings the view in for the face's categories and back out for the body's
			local zoom = self.zoom or 0
			if ( zoom >= 80 ) then W.SetZoom(1.45, 0.72) elseif ( zoom >= 50 ) then W.SetZoom(1.2, 0.62) else W.SetZoom(1, 0.6) end
			WrathppCreate_Refresh()
		end))
		categoryButtons[k] = b
	end
	return b
end

-- The option rows --------------------------------------------------------------------------------------------------------

local rowFrames = {}
local shown = {}

local function arrow(parent, direction)
	local b = make("Button", nil, parent)
	b:SetWidth(32); b:SetHeight(32)
	local side = direction < 0 and "Left" or "Right"
	b:SetNormalTexture("Interface\\Glues\\Common\\Glue-"..side.."Arrow-Button-Up")
	b:SetPushedTexture("Interface\\Glues\\Common\\Glue-"..side.."Arrow-Button-Down")
	b:SetHighlightTexture("Interface\\Glues\\Common\\Glue-"..side.."Arrow-Button-Highlight")
	return b
end

local function rowFrame(k)
	local f = rowFrames[k]
	if ( f ) then return f end
	f = make("Frame", "WrathppRow"..k, optionList.child)
	f:SetWidth(LIST_W - 8); f:SetHeight(ROW_H)
	f:SetPoint("TOPLEFT", optionList.child, "TOPLEFT", 0, -(k - 1) * ROW_H)
	f.name = text(f, FONT_LABEL)
	f.name:SetPoint("TOPLEFT", f, "TOPLEFT", 36, -2)
	f.name:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
	f.previous = arrow(f, -1)
	f.previous:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", 0, 4)
	f.next = arrow(f, 1)
	f.next:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", 0, 4)
	f.choice = box("WrathppRow"..k.."Choice", f, LIST_W - 8 - 72, 34)
	f.choice:SetPoint("BOTTOM", f, "BOTTOM", 0, 3)
	f.choice.label:ClearAllPoints()
	f.choice.label:SetPoint("LEFT", f.choice, "LEFT", 44, 0)
	f.choice.label:SetPoint("RIGHT", f.choice, "RIGHT", -26, 0)
	f.choice.label:SetJustifyH("LEFT")
	f.choice.label:SetHeight(14)
	f.choice.number = text(f.choice, FONT_TEXT)
	f.choice.number:SetPoint("LEFT", f.choice, "LEFT", 10, 0)
	f.choice.swatch = swatch(f.choice, 18); f.choice.swatch:SetPoint("LEFT", f.choice, "LEFT", 44, 0)
	f.choice.swatch2 = swatch(f.choice, 18); f.choice.swatch2:SetPoint("LEFT", f.choice.swatch, "RIGHT", 2, 0)
	f.choice.mark = text(f.choice, FONT_SMALL); f.choice.mark:SetPoint("RIGHT", f.choice, "RIGHT", -10, 0); f.choice.mark:SetText("v")
	f.check = make("CheckButton", "WrathppRow"..k.."Check", f)
	f.check:SetWidth(34); f.check:SetHeight(34)
	f.check:SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", 34, 2)
	f.check:SetNormalTexture("Interface\\Buttons\\UI-CheckBox-Up")
	f.check:SetPushedTexture("Interface\\Buttons\\UI-CheckBox-Down")
	f.check:SetHighlightTexture("Interface\\Buttons\\UI-CheckBox-Highlight")
	f.check:SetCheckedTexture("Interface\\Buttons\\UI-CheckBox-Check")
	f.checkText = text(f, FONT_TEXT); f.checkText:SetPoint("LEFT", f.check, "RIGHT", 6, 0)
	local function tapped(fn)
		return guarded(function(self)
			if ( not optionList:Tapped() ) then
				if ( self.SetChecked and f.row ) then self:SetChecked(f.row.on or (f.row.at == 2)) end
				return
			end
			fn(self)
			WrathppCreate_Refresh()
		end)
	end
	f.previous:SetScript("OnClick", tapped(function() WrathppCreate_ClosePopout(); W.Step(f.row, -1) end))
	f.next:SetScript("OnClick", tapped(function() WrathppCreate_ClosePopout(); W.Step(f.row, 1) end))
	f.choice:SetScript("OnClick", tapped(function() WrathppCreate_TogglePopout(f) end))
	f.check:SetScript("OnClick", tapped(function(self)
		WrathppCreate_ClosePopout()
		if ( f.row.undead ) then W.SetUndead(self:GetChecked() and true or false) else W.Choose(f.row, self:GetChecked() and 2 or 1) end
	end))
	for _, piece in ipairs({ f, f.previous, f.next, f.choice, f.check }) do
		if ( piece.EnableMouse ) then piece:EnableMouse(true) end
		optionList:Watch(piece)
	end
	rowFrames[k] = f
	return f
end

-- The next or previous choice of a row, round the ends.
function W.Step(row, delta)
	if ( row.kind == "plain" ) then W.Choose(row, delta > 0 and "next" or "previous"); return end
	if ( row.kind ~= "list" and row.kind ~= "switch" ) then return end
	local n = #row.choices
	if ( n < 1 ) then return end
	W.Choose(row, ((row.at or 1) - 1 + delta) % n + 1)
end

local function describe(choice, k)
	if ( choice.n and choice.n ~= "" ) then return choice.n end
	return ""
end

local function showRow(f, row)
	f.row = row
	f.name:SetText(row.name)
	local list = row.kind == "list" or row.kind == "plain" or row.kind == "later"
	if ( list ) then
		f.previous:Show(); f.next:Show(); f.choice:Show(); f.check:Hide(); f.checkText:Hide()
		local c = row.choices and row.at and row.choices[row.at]
		if ( row.kind == "plain" ) then
			f.choice.number:SetText("")
			f.choice.label:SetText(""); paint(f.choice.swatch, nil); paint(f.choice.swatch2, nil)
			f.choice.mark:Hide()
		elseif ( row.kind == "later" ) then
			f.choice.number:SetText("")
			f.choice.label:SetText("Not drawn yet")
			paint(f.choice.swatch, nil); paint(f.choice.swatch2, nil)
			f.choice.mark:Hide()
		else
			f.choice.number:SetText(row.at or "")
			paint(f.choice.swatch, c and c.s); paint(f.choice.swatch2, c and c.s2)
			f.choice.label:ClearAllPoints()
			f.choice.label:SetPoint("LEFT", f.choice, "LEFT", 44 + ((c and c.s) and 22 or 0) + ((c and c.s2) and 20 or 0), 0)
			f.choice.label:SetPoint("RIGHT", f.choice, "RIGHT", -26, 0)
			f.choice.label:SetText(c and describe(c, row.at) or "")
			f.choice.mark:Show()
		end
		local dim = row.kind == "later"
		f:SetAlpha(dim and 0.45 or 1)
		if ( dim ) then f.previous:Disable(); f.next:Disable(); f.choice:Disable() else f.previous:Enable(); f.next:Enable(); f.choice:Enable() end
	else
		f:SetAlpha(1)
		f.previous:Hide(); f.next:Hide(); f.choice:Hide(); f.check:Show(); f.checkText:Show()
		local on = row.on
		if ( on == nil ) then on = row.at == 2 end
		f.check:SetChecked(on and 1 or nil)
		local c = row.choices and row.choices[on and 2 or 1]
		f.checkText:SetText((c and c.n ~= "" and c.n) or (on and "On" or "Off"))
	end
	f:Show()
end

-- The list of an option's choices -----------------------------------------------------------------------------------------

local popout = panel("WrathppPopout", root, 300, 300)
popout:SetFrameStrata("DIALOG")
popout:Hide()
local popoutList = scroller("WrathppPopoutList", popout, 280, 280)
popoutList:SetPoint("TOPLEFT", popout, "TOPLEFT", 10, -10)
local catcher = make("Button", "WrathppPopoutCatcher", root)
catcher:SetAllPoints(root)
catcher:SetFrameStrata("HIGH")
catcher:Hide()
catcher:SetScript("OnClick", function() WrathppCreate_ClosePopout() end)
local cells = {}

local function cell(k)
	local b = cells[k]
	if ( b ) then return b end
	b = box("WrathppChoice"..k, popoutList.child, 60, 34)
	b.number = text(b, FONT_TEXT); b.number:SetPoint("LEFT", b, "LEFT", 8, 0)
	b.swatch = swatch(b, 18)
	b.swatch2 = swatch(b, 18)
	b.label:ClearAllPoints(); b.label:SetJustifyH("LEFT"); b.label:SetHeight(14)
	b:SetScript("OnClick", guarded(function(self)
		if ( not popoutList:Tapped() ) then return end
		W.Choose(popout.row, self.index)
		WrathppCreate_Refresh()
	end))
	popoutList:Watch(b)
	cells[k] = b
	return b
end

function WrathppCreate_ClosePopout()
	popout:Hide(); catcher:Hide()
	popout.row, popout.owner = nil, nil
end

local function fillPopout()
	local row = popout.row
	if ( not row ) then return end
	local named = false
	for _, c in ipairs(row.choices) do if ( c.n and c.n ~= "" ) then named = true end end
	local columns = named and 1 or 4
	local cw = named and 276 or 66
	local n = #row.choices
	local lines = math.ceil(n / columns)
	for k = 1, n do
		local c, b = row.choices[k], cell(k)
		b.index = k
		b:SetWidth(cw); b:ClearAllPoints()
		b:SetPoint("TOPLEFT", popoutList.child, "TOPLEFT", ((k - 1) % columns) * (cw + 4), -math.floor((k - 1) / columns) * 38)
		b.number:SetText(k)
		b.swatch:ClearAllPoints(); b.swatch:SetPoint("LEFT", b, "LEFT", named and 40 or 34, 0)
		b.swatch2:ClearAllPoints(); b.swatch2:SetPoint("LEFT", b.swatch, "RIGHT", 2, 0)
		paint(b.swatch, c.s); paint(b.swatch2, c.s2)
		b.label:ClearAllPoints()
		b.label:SetPoint("LEFT", b, "LEFT", 40 + (c.s and 22 or 0) + (c.s2 and 20 or 0), 0)
		b.label:SetPoint("RIGHT", b, "RIGHT", -6, 0)
		b.label:SetText(named and describe(c, k) or "")
		b:Lit(k == row.at)
		b:Show()
	end
	for k = n + 1, #cells do cells[k]:Hide() end
	local width = columns * (cw + 4) + 4
	local height = math.min(lines * 38, 420)
	popoutList:SetWidth(width); popoutList.child:SetWidth(width)
	popoutList:SetView(height)
	popoutList:SetContentHeight(lines * 38)
	popout:SetWidth(width + 20); popout:SetHeight(height + 20)
	return lines, columns
end

function WrathppCreate_TogglePopout(f)
	if ( popout.owner == f ) then WrathppCreate_ClosePopout(); return end
	local row = f.row
	if ( not row or row.kind ~= "list" ) then return end
	popout.row, popout.owner = row, f
	local _, columns = fillPopout()
	popout:ClearAllPoints()
	popout:SetPoint("TOPRIGHT", optionPanel, "TOPLEFT", -6, 0)
	local at = row.at or 1
	popoutList.offset, popoutList.target = 0, 0
	local line = math.floor((at - 1) / columns)
	popoutList:Reveal(line * 38, line * 38 + 38)
	popoutList.offset = popoutList.target
	popoutList:Place()
	catcher:Show(); popout:Show()
end

-- Moving the game's own pieces ---------------------------------------------------------------------------------------------

local function races()
	local list = {}
	local names = { GetAvailableRaces() }
	local i = 1
	while ( _G["CharacterCreateRaceButton"..i] ) do
		local token = names[(i - 1) * 3 + 2]
		list[i] = { button = _G["CharacterCreateRaceButton"..i], name = names[(i - 1) * 3 + 1], token = token and string.upper(token) or nil }
		i = i + 1
	end
	return list
end

local raceLabels = {}
local function placeRaces()
	local sides = { {}, {} }
	local list = races()
	for i, r in ipairs(list) do
		local alliance
		if ( r.token ) then alliance = ALLIANCE[r.token] and true or false else alliance = i <= math.ceil(#list / 2) end
		if ( r.button:IsShown() ) then table.insert(sides[alliance and 1 or 2], r) end
	end
	local tallest = 0
	for s, side in ipairs(sides) do
		local parent = s == 1 and alliancePanel or hordePanel
		local columns = #side > 6 and 2 or 1
		for k, r in ipairs(side) do
			local b = r.button
			b:SetParent(parent)
			b:ClearAllPoints()
			local column, line = (k - 1) % columns, math.floor((k - 1) / columns)
			if ( columns == 1 ) then
				b:SetPoint("TOPLEFT", parent, "TOPLEFT", 18, -44 - line * 62)
			else
				b:SetPoint("TOPLEFT", parent, "TOPLEFT", 30 + column * 106, -44 - line * 78)
			end
			local label = raceLabels[b]
			if ( not label ) then label = text(parent, FONT_TEXT); raceLabels[b] = label end
			label:ClearAllPoints()
			if ( columns == 1 ) then label:SetPoint("LEFT", b, "RIGHT", 12, 0) else label:SetPoint("TOP", b, "BOTTOM", 0, -2) end
			label:SetText(r.name or "")
			label:Show()
		end
		local lines = math.ceil(#side / columns)
		tallest = math.max(tallest, 56 + lines * (columns == 1 and 62 or 78))
	end
	alliancePanel:SetHeight(tallest); hordePanel:SetHeight(tallest)
end

local function place()
	for _, name in ipairs({ "CharacterCreateGenderButtonMale", "CharacterCreateGenderButtonFemale" }) do
		local b = _G[name]
		if ( b ) then
			b:SetParent(sexPanel)
			b:ClearAllPoints()
			b:SetPoint("CENTER", sexPanel, "CENTER", name == "CharacterCreateGenderButtonMale" and -30 or 30, 0)
			b:Show()
		end
	end
	local i, n = 1, 0
	while ( _G["CharacterCreateClassButton"..i] ) do
		if ( _G["CharacterCreateClassButton"..i]:IsShown() ) then n = n + 1 end
		i = i + 1
	end
	local at = 0
	i = 1
	while ( _G["CharacterCreateClassButton"..i] ) do
		local b = _G["CharacterCreateClassButton"..i]
		b:SetParent(classPanel)
		b:ClearAllPoints()
		if ( b:IsShown() ) then
			b:SetPoint("BOTTOMLEFT", classPanel, "BOTTOMLEFT", 16 + at * 50, 10)
			at = at + 1
		end
		i = i + 1
	end
	classPanel:SetWidth(math.max(200, 32 + math.max(n, 1) * 50))
	local name = GetSelectedClass and GetSelectedClass()
	className:SetText(name or "")
	placeRaces()
	if ( CharacterCreateConfigurationFrame ) then CharacterCreateConfigurationFrame:Hide() end
	i = 1
	while ( _G["CharacterCustomizationButtonFrame"..i] ) do _G["CharacterCustomizationButtonFrame"..i]:Hide(); i = i + 1 end
	for _, name in ipairs({ "CharCreateRandomizeButton", "CharacterCreateCharacterClass", "CharacterCreateCharacterRace", "CharCreateOkayButton",
			"CharacterCreateRotateLeft", "CharacterCreateRotateRight" }) do
		if ( _G[name] ) then _G[name]:Hide() end
	end
	if ( CharacterCreateNameEdit ) then
		CharacterCreateNameEdit:ClearAllPoints()
		CharacterCreateNameEdit:SetPoint("BOTTOM", root, "BOTTOM", 0, 44)
		CharacterCreateNameEdit:Show()
	end
	if ( CharacterCreateRandomName ) then
		CharacterCreateRandomName:ClearAllPoints()
		CharacterCreateRandomName:SetPoint("TOP", CharacterCreateNameEdit or root, "BOTTOM", 0, -2)
		CharacterCreateRandomName:Show()
	end
	if ( CharCreateBackButton ) then
		CharCreateBackButton:ClearAllPoints()
		CharCreateBackButton:SetPoint("BOTTOMLEFT", root, "BOTTOMLEFT", 24, 24)
	end
end

-- What is on the screen ---------------------------------------------------------------------------------------------------------

local function refresh()
	if ( W.off or W.step ~= 2 ) then return end
	local model = looks()
	-- the categories of this race and sex
	local n = 0
	if ( model and number(FIELD.skin) ) then
		local found = false
		for _, c in ipairs(model.categories) do if ( c.id == W.category ) then found = true end end
		if ( not found ) then W.category = model.categories[1].id end
		for k, c in ipairs(model.categories) do
			local b = categoryButton(k)
			b.category, b.zoom = c.id, c.zoom
			b.label:SetText(c.name)
			b:Lit(c.id == W.category)
			b:Show()
			if ( c.id == W.category ) then optionTitle:SetText(c.name) end
			n = k
		end
	else
		optionTitle:SetText("Appearance")
	end
	for k = n + 1, #categoryButtons do categoryButtons[k]:Hide() end
	if ( n > 1 ) then categoryPanel:SetHeight(24 + n * 48); categoryPanel:Show() else categoryPanel:Hide() end
	local rows = W.Rows()
	for k, row in ipairs(rows) do showRow(rowFrame(k), row) end
	for k = #rows + 1, #rowFrames do rowFrames[k]:Hide(); rowFrames[k].row = nil end
	shown = rows
	optionList:SetContentHeight(#rows * ROW_H)
	if ( popout.owner and popout.owner.row and popout:IsShown() ) then
		popout.row = popout.owner.row
		if ( popout.row.kind == "list" ) then fillPopout() else WrathppCreate_ClosePopout() end
	end
	if ( type(WrathPP_GetCustomization) ~= "function" ) then
		notice:SetText("Wrath++ add-on not running: the game's own five")
	elseif ( not model ) then
		notice:SetText("The game's own looks for this race and sex")
	else
		notice:SetText("")
	end
end

WrathppCreate_Refresh = guarded(refresh)

local function setStep(n)
	if ( W.off ) then return end
	W.step = n
	local first = n == 1
	place()
	local function show(frame, on) if ( frame ) then if ( on ) then frame:Show() else frame:Hide() end end end
	show(alliancePanel, first); show(hordePanel, first); show(classPanel, first)
	show(customizeButton, first); show(CharCreateBackButton, first)
	show(optionPanel, not first); show(randomizeButton, not first); show(viewPanel, not first)
	show(backButton, not first); show(finishButton, not first)
	if ( first ) then categoryPanel:Hide(); WrathppCreate_ClosePopout(); W.SetZoom(1, 0.6) end
	sexPanel:ClearAllPoints()
	if ( first ) then sexPanel:SetPoint("TOP", root, "TOP", 0, -14) else sexPanel:SetPoint("TOPLEFT", root, "TOPLEFT", 214, -14) end
	sexPanel:Show(); spinArea:Show()
	WrathppCreate_Refresh()
end

WrathppCreate_SetStep = guarded(setStep)

-- The game's own screen back, and why.
function WrathppCreate_Disable(reason)
	W.off = true
	for _, f in ipairs({ alliancePanel, hordePanel, sexPanel, classPanel, categoryPanel, optionPanel, viewPanel, customizeButton, backButton,
			finishButton, randomizeButton, spinArea, popout, catcher }) do f:Hide() end
	for _, name in ipairs({ "CharacterCreateConfigurationFrame", "CharCreateRandomizeButton", "CharCreateOkayButton", "CharCreateBackButton",
			"CharacterCreateCharacterClass", "CharacterCreateCharacterRace", "CharacterCreateRotateLeft", "CharacterCreateRotateRight" }) do
		if ( _G[name] ) then _G[name]:Show() end
	end
	local i = 1
	while ( _G["CharacterCustomizationButtonFrame"..i] ) do _G["CharacterCustomizationButtonFrame"..i]:Show(); i = i + 1 end
	if ( not W.reason ) then
		W.reason = text(root, FONT_SMALL)
		W.reason:SetPoint("TOP", root, "TOP", 0, -4)
	end
	W.reason:SetText("Wrath++ creator off: "..tostring(reason))
end

-- After the game's own changes: the first screen when the creator opens, the rows again after anything changes.
local function after(name, fn)
	local original = _G[name]
	if ( type(original) ~= "function" ) then return end
	_G[name] = function(...)
		local a, b, c = original(...)
		fn()
		return a, b, c
	end
end
-- The creator opened. However the game's screen runs its own OnShow (by the function's name, or bound to the function
-- it was when the screen was made), this is told: the function's name is wrapped, and the driver below, a frame of the
-- screen's, has an OnShow of its own. Twice is the same as once. The game's own OnShow may run after the driver's, so
-- the pieces are placed again on the first frames.
local opened = guarded(function()
	W.category = nil
	W.zoom, W.zoomTarget, W.focusY, W.focusTarget, W.spin = 1, 1, 0.6, 0.6, 0
	W.fresh = 3
	W.ApplyZoom()
	WrathppCreate_SetStep(1)
end)
if ( type(CharacterCreate_OnShow) == "function" ) then after("CharacterCreate_OnShow", opened) end
for _, name in ipairs({ "SetCharacterRace", "SetCharacterGender", "SetCharacterClass", "CharacterCreate_UpdateHairCustomization" }) do
	after(name, guarded(function() WrathppCreate_ClosePopout(); place(); WrathppCreate_Refresh() end))
end

-- Every frame: the lists easing, the character turning, the view coming nearer; four times a second the rows again
-- (what the game's own state is, however it changed).
local driver = make("Frame", "WrathppDriver", root)
local sinceRefresh = 0
driver:SetScript("OnShow", opened)
driver:SetScript("OnUpdate", guarded(function(self, elapsed)
	elapsed = elapsed or arg1 or 0
	if ( (W.fresh or 0) > 0 ) then
		W.fresh = W.fresh - 1
		WrathppCreate_SetStep(W.step)
	end
	for _, s in ipairs(scrollers) do s:Update(elapsed) end
	if ( W.turning ) then
		local x, y = cursor()
		local dx, dy = x - W.lastX, y - W.lastY
		W.lastX, W.lastY = x, y
		if ( dx ~= 0 ) then turn(dx * 0.45) end
		if ( elapsed > 0 ) then W.spin = 0.7 * W.spin + 0.3 * (dx * 0.45 / elapsed) end
		if ( W.zoom > 1.05 and dy ~= 0 ) then
			local h = (GlueParent and GlueParent:GetHeight()) or 768
			W.focusY = math.max(0.25, math.min(0.95, W.focusY - dy / (h * W.zoom)))
			W.focusTarget = W.focusY
			W.ApplyZoom()
		end
	elseif ( math.abs(W.spin) > 4 ) then
		turn(W.spin * elapsed)
		W.spin = W.spin * math.max(0, 1 - elapsed * 3)
	end
	for _, b in ipairs({ turnLeft, turnRight }) do
		if ( b.held and b.whileHeld ) then W.spin = 0; b.whileHeld(elapsed) end
	end
	local target, focus = W.zoomTarget or W.zoom, W.focusTarget or W.focusY
	if ( math.abs(target - W.zoom) > 0.002 or math.abs(focus - W.focusY) > 0.002 ) then
		local share = math.min(1, elapsed * 8)
		W.zoom = W.zoom + (target - W.zoom) * share
		W.focusY = W.focusY + (focus - W.focusY) * share
		if ( math.abs(target - W.zoom) <= 0.002 ) then W.zoom = target end
		W.ApplyZoom()
	end
	sinceRefresh = sinceRefresh + elapsed
	if ( sinceRefresh >= 0.25 ) then sinceRefresh = 0; WrathppCreate_Refresh() end
end))

-- Nothing of this shows before the creator is opened (the game's own pieces are moved then, not now).
for _, f in ipairs({ alliancePanel, hordePanel, sexPanel, classPanel, categoryPanel, optionPanel, viewPanel, customizeButton, backButton,
		finishButton, randomizeButton, spinArea }) do f:Hide() end

end -- build

local ok, err = pcall(build)
if ( not ok ) then
	-- the game's own screen, untouched, and why
	W.off, W.error = true, err
	for _, f in ipairs(made) do pcall(f.Hide, f) end
	pcall(function()
		local s = root:CreateFontString(nil, "OVERLAY", "GlueFontHighlightSmall")
		s:SetPoint("TOP", root, "TOP", 0, -4)
		s:SetText("Wrath++ creator off: "..tostring(err))
	end)
end
