-- Wrath++'s character creator (docs/wrathpp): Shadowlands' creator, on the 3.3.5 game's creation screen.
--
--   Race and class: the Alliance's races down the left, the Horde's down the right, the sexes at the top, the
--                   classes in a row at the bottom; Back, Customize.
--   Customize:      as Shadowlands' own screen. Top right: a dice (Randomize) and the race's categories (Face, Hair,
--                   Accessories, Body, Markings) as round buttons in a row; under them the chosen category's options
--                   in Shadowlands' order, each one line: its name, the choice on (its number, colour swatch and
--                   name) between a previous and a next arrow; tapping the choice opens the list of them all under
--                   it. Top middle: "Name" and the name's box. Top left: the view's round buttons (back to the start,
--                   further, nearer, turn left, turn right); the character also turns under a finger and by itself
--                   after a flick, and the wheel (a pinch) brings it nearer. Lists longer than their place scroll
--                   under a finger, eased. Bottom: Back, Finish. Gear, last in every category, takes the starting
--                   outfit off and puts it back.
--
-- What an option is and how a choice reaches the game is WrathppLooks (made with the looks by
-- realm/warcraft/wrathpp/tools/sl_creator.py): 3.3.5 keeps five numbers a character, and Shadowlands' options are
-- packed into them (a face number is a face and an eye colour...). The numbers are read and set through Wrath++'s
-- native mod (WrathPP_GetCustomization, WrathPP_SetCustomization) and the game's own CycleCharCustomization.
-- Without the looks or the native mod the rows are the game's own five. WrathppUndead (written by the app when the
-- undead skins are imported) adds the Undead switch under Accessories: its skins are new colours after the race's own.
--
-- It is drawn with Shadowlands' own art (WrathppAtlas: the pieces of its creation screens, cut out of the game's sheets
-- by realm/warcraft/wrathpp/tools/sl_ui_art.py, in Data/patch-S.MPQ) at Shadowlands' own sizes and places
-- (Blizzard_CharacterCreate and Blizzard_CharacterCustomize, build 9.2.7); without the art, with 3.3.5's own pictures
-- in the same places.
--
-- The game's own buttons do the work (races, classes, sexes, the name, creating) out of sight: Shadowlands' round
-- buttons here show what they say and, tapped, do what a tap on them does.
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
-- The other realms' own races (mod-murloc-naga: ChrRaces' file names Murloc and Naga_), whose buttons the shared game data
-- brings: not Wrath++'s.
local LEFT_OUT = { MURLOC = true, NAGA = true, NAGA_ = true }
local ALLIANCE = { HUMAN = true, DWARF = true, NIGHTELF = true, GNOME = true, DRAENEI = true, WORGEN = true, VOIDELF = true,
	LIGHTFORGEDDRAENEI = true, HIGHORDER = true, PANDAREN = true, KULTIRAN = true, DARKIRONDWARF = true, MECHAGNOME = true }
-- Shadowlands lays its creator out for a screen 1080 units high (its CharacterCreateFrame is scaled by 768 over the
-- display's height, 0.75 at most); 3.3.5's screen is 768 high on any display, so one of Shadowlands' units is
-- 768/1080 of one here. SIZE draws all of it larger again: at a monitor's proportions a line of a list is 1.6 mm high
-- on the phone this is played on. Every size and place of the creator is Shadowlands' own number through u().
local SIZE = 1.2
local S = 768 / 1080 * SIZE
local function u(n) return n * S end
-- One pixel of the game's screen in the screen's units (gxResolution's height over the 768 units of the screen).
local pixel
function W.Pixel()
	if ( pixel == nil ) then
		pixel = 0
		local res = type(GetCVar) == "function" and GetCVar("gxResolution")
		local h = res and tonumber(string.match(res, "x(%d+)"))
		local units = GlueParent and GlueParent:GetHeight()
		if ( h and h > 0 and units and units > 0 ) then pixel = units / h end
	end
	return pixel
end
local POP = 1.4                                         -- the lists of choices larger again: a line is a finger's target
local ROW_PITCH = u(38 + 32)                            -- an option's row and the space under it (the Options layout's spacing)
local ROW_H = ROW_PITCH
local ROW_W = 223                                       -- SelectionPopoutWithButtonsTemplate: the box and its two arrows
local NAME_W = 190                                      -- room for an option's name left of them
local LIST_W = u(ROW_W + 34 + NAME_W)
local GOLD = { 1, 0.82, 0 }

-- What the creator did, into WarcraftXL's log (the native mod's WrathPP_Log), which the app's reports carry: whether
-- it was built, opened, which screen was up, why it went off. A line is written once, when it changes.
local lastLine
local function log(line)
	line = tostring(line)
	if ( line == lastLine ) then return end
	lastLine = line
	if ( type(WrathPP_Log) == "function" ) then pcall(WrathPP_Log, line) end
end
W.Log = log

local function build()

-- Whether the game has a character on the creator. The game makes it in its own OnShow (ResetCharCustomize), and its
-- functions for the creator read it without looking whether there is one: GetSelectedClass, GetSelectedSex,
-- GetNameForRace, GetAvailableRaces, GetAvailableClasses, CycleCharCustomization, RandomizeCharCustomization,
-- SetCharacterCreateFacing... Called without one the game dies (12 November 2026: an access violation reading 0x1C
-- at 0x004E0A9B, GetSelectedClass, called from this script's own OnShow, which ran before the game's). So nothing
-- here runs before this says yes: every handler goes through guarded(), which asks. The native mod knows
-- (WrathPP_GetCreating gives nothing while there is none); without it, yes once the game's own OnShow has been run
-- (W.made: its wrapped name was called, or a frame has been drawn since the screen was shown).
local function hasCharacter()
	if ( type(WrathPP_GetCreating) == "function" ) then
		local ok, race = pcall(WrathPP_GetCreating)
		if ( ok ) then return race ~= nil end
	end
	return W.made == true
end
W.HasCharacter = hasCharacter

-- What a button or the screen runs, once the game has its character: whatever fails in it puts the game's own screen
-- back (WrathppCreate_Disable). `always`: also without a character (the frame's own ticking, which waits for one).
local function guarded(fn, always)
	return function(...)
		if ( W.off ) then return end
		if ( not always and not hasCharacter() ) then return end
		local ok, err = pcall(fn, ...)
		if ( not ok ) then WrathppCreate_Disable(err) end
	end
end

-- Small pieces ---------------------------------------------------------------------------------------------------

-- Shadowlands' own art (WrathppAtlas: the pieces of its creation screens, cut out of the game's sheets by
-- realm/warcraft/wrathpp/tools/sl_ui_art.py and put in by the app as Data/patch-S.MPQ). atlas(texture, name) is
-- Shadowlands' SetAtlas: the piece's file and where it is in it; `sized` gives the texture the size Shadowlands draws
-- the piece at. Whether the art is used is settled as the creator opens (W.art: the table is in and the game reads its
-- files); until then, and without it, each piece is one of 3.3.5's own pictures or a plain colour, in the same places.
local FALLBACK = {
	["common-button-square-gray-up"] = { 0.09, 0.09, 0.11, 0.92 }, ["common-button-square-gray-down"] = { 0.17, 0.16, 0.12, 0.95 },
	["common-icon-undo"] = "Interface\\PaperDollInfoFrame\\UI-GearManager-Undo",
	["common-icon-zoomin"] = "Interface\\Minimap\\UI-Minimap-ZoomInButton-Up", ["common-icon-zoomout"] = "Interface\\Minimap\\UI-Minimap-ZoomOutButton-Up",
	["common-icon-rotateleft"] = "Interface\\Buttons\\UI-RotationLeft-Button-Up", ["common-icon-rotateright"] = "Interface\\Buttons\\UI-RotationRight-Button-Up",
	["charactercreate-icon-dice"] = "Interface\\Buttons\\UI-GroupLoot-Dice-Up",
	["charactercreate-customize-nextbutton"] = "Interface\\Glues\\Common\\Glue-RightArrow-Button-Up",
	["charactercreate-customize-nextbutton-down"] = "Interface\\Glues\\Common\\Glue-RightArrow-Button-Down",
	["charactercreate-customize-nextbutton-disabled"] = "Interface\\Glues\\Common\\Glue-RightArrow-Button-Up",
	["charactercreate-customize-backbutton"] = "Interface\\Glues\\Common\\Glue-LeftArrow-Button-Up",
	["charactercreate-customize-backbutton-down"] = "Interface\\Glues\\Common\\Glue-LeftArrow-Button-Down",
	["charactercreate-customize-backbutton-disabled"] = "Interface\\Glues\\Common\\Glue-LeftArrow-Button-Up",
	["charactercreate-customize-dropdownbox"] = { 0.08, 0.08, 0.1, 0.95 }, ["charactercreate-customize-dropdownbox-open"] = { 0.17, 0.16, 0.12, 0.95 },
	["charactercreatedropdown-nineslice-center"] = { 0.04, 0.04, 0.06, 0.96 },
	["charactercreate-customize-palette"] = { 1, 1, 1, 1 }, ["charactercreate-customize-palette-half"] = { 1, 1, 1, 1 },
}
local function plain(name)
	local f = FALLBACK[name]
	if ( f ) then return f end
	if ( string.find(name, "128-redbutton", 1, true) and not string.find(name, "highlight", 1, true) ) then
		if ( string.find(name, "disabled", 1, true) ) then return { 0.25, 0.25, 0.25, 1 } end
		if ( string.find(name, "pressed", 1, true) ) then return { 0.3, 0.03, 0.03, 1 } end
		return { 0.45, 0.05, 0.05, 1 }
	end
end
local function piece(name) return W.art and WrathppAtlas[name] or nil end
local function atlas(tex, name, sized, flip)
	local p = piece(name)
	if ( p ) then
		tex:SetTexture(p[1])
		if ( flip ) then tex:SetTexCoord(p[5], p[4], p[6], p[7]) else tex:SetTexCoord(p[4], p[5], p[6], p[7]) end
		if ( sized ) then tex:SetWidth(u(p[2])); tex:SetHeight(u(p[3])) end
		return true
	end
	local f = plain(name)
	tex:SetTexCoord(0, 1, 0, 1)
	if ( type(f) == "string" ) then tex:SetTexture(f)
	elseif ( type(f) == "table" ) then tex:SetTexture(f[1], f[2], f[3], f[4])
	else tex:SetTexture(0, 0, 0, 0) end
	return false
end
-- Everything drawn is drawn by a function kept here, so that it is drawn again once the art is known to be there.
local skins = {}
local function skin(fn) skins[#skins + 1] = fn; fn() end
function W.Reskin() for _, fn in ipairs(skins) do fn() end end
-- As the creator opens: is Shadowlands' art in, and does the game read it (SetTexture gives nothing for a file the
-- game cannot set)? Said in the log, once.
function W.DecideArt()
	if ( W.art ~= nil ) then return end
	W.art = false
	local why = "not in"
	if ( type(WrathppAtlas) == "table" and WrathppAtlas["charactercreate-ring-select"] ) then
		local probe = root:CreateTexture(nil, "BACKGROUND")
		probe:SetWidth(1); probe:SetHeight(1); probe:SetPoint("TOPLEFT", root, "TOPLEFT", 0, 0); probe:SetAlpha(0)
		if ( probe:SetTexture(WrathppAtlas["charactercreate-ring-select"][1]) ) then W.art = true else why = "in, and the game does not read its files" end
		probe:Hide()
	end
	log("art: "..(W.art and "Shadowlands' own" or ("3.3.5's own pictures (Shadowlands' art "..why..")")))
	W.Reskin()
end

-- Text: Shadowlands' fonts are Friz Quadrata (3.3.5's own file) at 12 (GameFontNormal), 14 (Med2), 18 (Large2) and 22
-- outlined (the foot's buttons), gold or white, with a shadow one unit down and right.
-- (the file is the game's own font's, which is another file in a game of another language)
local FRIZ = "Fonts\\FRIZQT__.TTF"
if ( type(GlueFontNormal) == "table" and GlueFontNormal.GetFont ) then
	local ok, file = pcall(GlueFontNormal.GetFont, GlueFontNormal)
	if ( ok and type(file) == "string" and file ~= "" ) then FRIZ = file end
end
local function label(parent, size, colour, outline, layer)
	local s = parent:CreateFontString(nil, layer or "OVERLAY", "GlueFontHighlightSmall")
	s:SetFont(FRIZ, u(size or 12), outline and "OUTLINE" or nil)
	if ( colour == "gold" ) then s:SetTextColor(1, 0.82, 0) elseif ( colour == "grey" ) then s:SetTextColor(0.5, 0.5, 0.5) else s:SetTextColor(1, 1, 1) end
	s:SetShadowColor(0, 0, 0, 1); s:SetShadowOffset(u(1), -u(1))
	return s
end
local function text(parent) return label(parent, 12, "white") end

-- CharCustomizeSmallButtonTemplate: a grey square (48) with a gold picture (24 x 23) in its middle; pressed, the square
-- is its pressed piece and the picture a unit down and right; under a pointer the picture glows.
local function smallButton(name, parent, icon)
	local b = make("Button", name, parent)
	b:SetWidth(u(48)); b:SetHeight(u(48))
	b.back = b:CreateTexture(nil, "BACKGROUND"); b.back:SetAllPoints(b)
	b.icon = b:CreateTexture(nil, "OVERLAY"); b.icon:SetWidth(u(24)); b.icon:SetHeight(u(23)); b.icon:SetPoint("CENTER", b, "CENTER", 0, 0)
	b.glow = b:CreateTexture(nil, "HIGHLIGHT"); b.glow:SetAllPoints(b.icon); b.glow:SetBlendMode("ADD"); b.glow:SetAlpha(0.4)
	function b:Paint()
		atlas(self.back, self.held and "common-button-square-gray-down" or "common-button-square-gray-up")
		atlas(self.icon, icon); atlas(self.glow, icon)
		self.icon:ClearAllPoints()
		self.icon:SetPoint("CENTER", self, "CENTER", self.held and u(1) or 0, self.held and -u(1) or 0)
	end
	b:SetScript("OnMouseDown", function(self) self.held = true; self:Paint() end)
	b:SetScript("OnMouseUp", function(self) self.held = false; self:Paint() end)
	skin(function() b:Paint() end)
	return b
end

-- CharCustomizeMaskedButtonTemplate: a round picture in a ring, a gold ring over it while it is the one chosen.
-- Shadowlands trims the picture round with a mask, which 3.3.5 has not: the art has each picture already trimmed for
-- its kind of button ("<name>.<kind>"). Without the art the picture is `plain` (one of 3.3.5's own, with its place in
-- its file), bright while chosen and dim while not.
local function maskedButton(name, parent, width, height, ring, ringWidth, ringHeight, chosenSize, kind)
	local b = make("Button", name, parent)
	b:SetWidth(u(width)); b:SetHeight(u(height))
	b.kind, b.ringAtlas = kind, ring
	b.icon = b:CreateTexture(nil, "BORDER"); b.icon:SetAllPoints(b)
	b.ring = b:CreateTexture(nil, "ARTWORK"); b.ring:SetWidth(u(ringWidth)); b.ring:SetHeight(u(ringHeight)); b.ring:SetPoint("CENTER", b, "CENTER", 0, 0)
	b.chosen = b:CreateTexture(nil, "OVERLAY"); b.chosen:SetWidth(u(chosenSize)); b.chosen:SetHeight(u(chosenSize)); b.chosen:SetPoint("CENTER", b, "CENTER", 0, 0)
	b.glow = b:CreateTexture(nil, "HIGHLIGHT"); b.glow:SetAllPoints(b.ring); b.glow:SetBlendMode("ADD"); b.glow:SetAlpha(0.5)
	function b:Paint()
		local drawn = self.iconAtlas and atlas(self.icon, self.iconAtlas.."."..self.kind, false, self.flip)
		if ( not drawn ) then
			if ( self.plain ) then
				self.icon:SetTexture(self.plain)
				local c = self.plainCoords
				if ( c ) then self.icon:SetTexCoord(c[1], c[2], c[3], c[4]) else self.icon:SetTexCoord(0, 1, 0, 1) end
			else self.icon:SetTexture(0, 0, 0, 0) end
		end
		-- (dimmed by its colour only: SetDesaturated, even SetDesaturated(nil), puts the game's own pixel shader on the
		-- texture, which on the phone drew the portraits' clear corners as solid squares in build 241)
		local dim = (self.off and 0.35) or ((drawn or self.on) and 1) or 0.55
		self.icon:SetVertexColor(dim, dim, dim)
		local ringName = self.ringAtlas
		if ( self.off and piece(ringName.."-disabled") ) then ringName = ringName.."-disabled" end
		atlas(self.ring, ringName)
		atlas(self.chosen, "charactercreate-ring-select")
		atlas(self.glow, ringName)
		if ( self.on ) then self.chosen:Show() else self.chosen:Hide() end
	end
	-- Set(atlas name or nil, chosen, off, plain picture, its coords, flipped)
	function b:Set(iconAtlas, on, off, plainFile, plainCoords, flip)
		self.iconAtlas, self.on, self.off, self.plain, self.plainCoords, self.flip = iconAtlas, on and true or false, off and true or false, plainFile, plainCoords, flip
		self:Paint()
	end
	skin(function() b:Paint() end)
	return b
end

-- ThreeSliceButtonTemplate "128-RedButton" (the foot's buttons, 250 x 66): a left and a right piece at the button's
-- height and the middle between them; pressed and disabled pieces; the text 22 high, outlined.
local function redButton(name, parent, caption, width, height, onClick, arrow)
	local b = make("Button", name, parent)
	b:SetWidth(u(width)); b:SetHeight(u(height))
	local scale = height / 128
	b.left = b:CreateTexture(nil, "BACKGROUND"); b.left:SetWidth(u(114 * scale)); b.left:SetHeight(u(height)); b.left:SetPoint("LEFT", b, "LEFT", 0, 0)
	b.right = b:CreateTexture(nil, "BACKGROUND"); b.right:SetWidth(u(292 * scale)); b.right:SetHeight(u(height)); b.right:SetPoint("RIGHT", b, "RIGHT", 0, 0)
	b.middle = b:CreateTexture(nil, "BACKGROUND")
	b.middle:SetPoint("TOPLEFT", b.left, "TOPRIGHT", 0, 0); b.middle:SetPoint("BOTTOMRIGHT", b.right, "BOTTOMLEFT", 0, 0)
	b.glow = b:CreateTexture(nil, "HIGHLIGHT"); b.glow:SetAllPoints(b); b.glow:SetBlendMode("ADD")
	b.caption = label(b, 22, "gold", true); b.caption:SetPoint("CENTER", b, "CENTER", 0, 0); b.caption:SetText(caption)
	-- CharacterCreateNavButtonMixin:UpdateText: an arrow 8 x 13 after the text of the button that goes on, before the
	-- text of the one that goes back, two spaces between (common-icon-forwardarrow, -backarrow)
	local gap = u(12)
	if ( arrow ) then
		b.arrow = b:CreateTexture(nil, "OVERLAY"); b.arrow:SetWidth(u(8)); b.arrow:SetHeight(u(13))
		if ( arrow == "forward" ) then b.arrow:SetPoint("LEFT", b.caption, "RIGHT", gap, 0) else b.arrow:SetPoint("RIGHT", b.caption, "LEFT", -gap, 0) end
	end
	function b:Paint()
		local state = (not self:IsEnabled() and "-disabled") or (self.held and "-pressed") or ""
		atlas(self.left, "128-redbutton-left"..state); atlas(self.right, "128-redbutton-right"..state); atlas(self.middle, "_128-redbutton-center"..state)
		atlas(self.glow, "128-redbutton-highlight")
		-- the text and its arrow together in the button's middle (without the art there is no arrow)
		local lean = 0
		if ( self.arrow ) then
			if ( atlas(self.arrow, "common-icon-"..arrow.."arrow"..(self:IsEnabled() and "" or "-disable")) ) then
				self.arrow:Show(); lean = (u(8) + gap) / 2 * (arrow == "forward" and -1 or 1)
			else self.arrow:Hide() end
		end
		self.caption:ClearAllPoints()
		self.caption:SetPoint("CENTER", self, "CENTER", lean + (self.held and u(2) or 0), self.held and -u(2) or 0)
	end
	b:SetScript("OnMouseDown", function(self) self.held = true; self:Paint() end)
	b:SetScript("OnMouseUp", function(self) self.held = false; self:Paint() end)
	b:SetScript("OnClick", guarded(onClick))
	skin(function() b:Paint() end)
	return b
end

-- A colour's swatch: Shadowlands' brush stroke (charactercreate-customize-palette, 84 x 20) in the colour.
local function swatch(parent)
	local t = parent:CreateTexture(nil, "ARTWORK")
	t:SetWidth(u(84)); t:SetHeight(u(20))
	return t
end
local function paint(tex, colour, half)
	if ( not colour ) then tex:Hide(); return end
	atlas(tex, half and "charactercreate-customize-palette-half" or "charactercreate-customize-palette")
	tex:SetVertexColor((math.floor(colour / 65536) % 256) / 255, (math.floor(colour / 256) % 256) / 255, (colour % 256) / 255)
	tex:Show()
end

-- NineSlicePanelTemplate "CharacterCreateDropdown": the frame of a list of choices. Corners set out from the frame's
-- own (30 sideways, 20 up or down), the edges between them, the middle inside.
local function nineSlice(f)
	local n = {}
	local function part(key) n[key] = f:CreateTexture(nil, "BACKGROUND"); return n[key] end
	part("tl"):SetPoint("TOPLEFT", f, "TOPLEFT", -u(30), u(20)); n.tl:SetWidth(u(62)); n.tl:SetHeight(u(52))
	part("tr"):SetPoint("TOPRIGHT", f, "TOPRIGHT", u(30), u(20)); n.tr:SetWidth(u(62)); n.tr:SetHeight(u(52))
	part("bl"):SetPoint("BOTTOMLEFT", f, "BOTTOMLEFT", -u(30), -u(20)); n.bl:SetWidth(u(62)); n.bl:SetHeight(u(72))
	part("br"):SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", u(30), -u(20)); n.br:SetWidth(u(62)); n.br:SetHeight(u(72))
	part("top"):SetPoint("TOPLEFT", n.tl, "TOPRIGHT", 0, 0); n.top:SetPoint("BOTTOMRIGHT", n.tr, "BOTTOMLEFT", 0, 0)
	part("bottom"):SetPoint("TOPLEFT", n.bl, "TOPRIGHT", 0, 0); n.bottom:SetPoint("BOTTOMRIGHT", n.br, "BOTTOMLEFT", 0, 0)
	part("left"):SetPoint("TOPLEFT", n.tl, "BOTTOMLEFT", 0, 0); n.left:SetPoint("BOTTOMRIGHT", n.bl, "TOPRIGHT", 0, 0)
	part("right"):SetPoint("TOPLEFT", n.tr, "BOTTOMLEFT", 0, 0); n.right:SetPoint("BOTTOMRIGHT", n.br, "TOPRIGHT", 0, 0)
	part("middle"):SetPoint("TOPLEFT", n.tl, "BOTTOMRIGHT", 0, 0); n.middle:SetPoint("BOTTOMRIGHT", n.br, "TOPLEFT", 0, 0)
	skin(function()
		local a = "charactercreatedropdown-nineslice-"
		atlas(n.tl, a.."cornertopleft"); atlas(n.tr, a.."cornertopright"); atlas(n.bl, a.."cornerbottomleft"); atlas(n.br, a.."cornerbottomright")
		atlas(n.top, "_"..a.."edgetop"); atlas(n.bottom, "_"..a.."edgebottom"); atlas(n.left, "!"..a.."edgeleft"); atlas(n.right, "!"..a.."edgeright")
		atlas(n.middle, a.."center")
		-- (without the art: a dark box over the whole list)
		n.middle:ClearAllPoints()
		if ( W.art ) then n.middle:SetPoint("TOPLEFT", n.tl, "BOTTOMRIGHT", 0, 0); n.middle:SetPoint("BOTTOMRIGHT", n.br, "TOPLEFT", 0, 0)
		else n.middle:SetPoint("TOPLEFT", f, "TOPLEFT", -u(6), u(6)); n.middle:SetPoint("BOTTOMRIGHT", f, "BOTTOMRIGHT", u(6), -u(6)) end
	end)
	return n
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

-- Wrath++'s own body options (the realm's registry, through the appearance add-on: categories 1101 to 1103) on a
-- woman's Body tab: chosen here, sent with the new character at Finish (WrathPP_SendCreateChoices) and kept by the realm,
-- which shows them in the world (her display); this screen's character stays as drawn. A Body tab of its own where her
-- looks have none. Nothing without the add-on, or before the realm has said hello.
local BODY_TAB = 9001
local BODY_FIRST, BODY_LAST = 1101, 1103
local BODY_ROWS = { "Shape", "Style", "Density" }
-- the body options of the woman being made, or nothing; and for a woman, why there are none (the realm not answering)
local function bodyOptions()
	local out = {}
	if ( type(WrathPP_GetCreating) ~= "function" ) then return out end
	local race, sex, class = WrathPP_GetCreating()
	if ( not race or sex ~= 1 ) then return out end
	if ( type(WrathPP_Status) ~= "function" or type(WrathPP_GetNumCategories) ~= "function" ) then return out, "The Wrath++ add-on isn't running" end
	local ok, state = pcall(WrathPP_Status)
	if ( not ok or state ~= "ready" ) then return out, (state == "refused") and "The realm's answer was refused" or "Waiting for the realm" end
	for i = 1, (WrathPP_GetNumCategories(race, sex, class) or 0) do
		local id, name, count = WrathPP_GetCategoryInfo(i, race, sex, class)
		if ( id and id >= BODY_FIRST and id <= BODY_LAST ) then out[#out + 1] = { id = id, name = name, count = count or 0, class = class } end
	end
	return out
end

local function bodyRows(rows)
	local list, why = bodyOptions()
	if ( why ) then
		-- shown, greyed, saying why (a woman's Body tab is there whatever the realm said)
		for _, name in ipairs(BODY_ROWS) do rows[#rows + 1] = { name = name, kind = "later", why = why, choices = {} } end
		return
	end
	for _, c in ipairs(list) do
		local row = { name = c.name, kind = "list", body = c.id, choices = {} }
		local on = WrathPP_GetChoice(c.id)
		for i = 1, c.count do
			local id, name = WrathPP_GetOptionInfo(c.id, i, c.class)
			if ( id ) then
				row.choices[#row.choices + 1] = { v = id, n = name or "" }
				if ( id == on ) then row.at = #row.choices end
			end
		end
		if ( #row.choices > 1 ) then rows[#rows + 1] = row end
	end
end

-- Sends the body options with the character about to be made (the realm keeps them for the character the game makes next).
function W.SendBody()
	if ( type(WrathPP_SendCreateChoices) ~= "function" or type(WrathPP_GetCreating) ~= "function" ) then return end
	local race, sex, class = WrathPP_GetCreating()
	if ( not race ) then return end
	local ok, sent, why = pcall(WrathPP_SendCreateChoices, race, sex, class)
	log("body options: "..((ok and sent) and "sent" or ("not sent ("..tostring(why or sent)..")")))
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
		if ( type(WrathPP_SetGear) == "function" ) then rows[#rows + 1] = { name = "Gear", kind = "switch", gear = true, on = W.gear ~= false } end
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
				if ( value == nil ) then
					-- the game has none of this for the character as it is (it counts 0): shown, greyed, not chosen from
					row.kind, row.none = "later", true
					for _, c in ipairs(option.choices) do if ( allowed(c, dk) ) then row.choices[#row.choices + 1] = c end end
				else
					local digit = decode(math.min(value, product(model.fields[option.field]) - 1), model.fields[option.field])[option.part]
					for _, c in ipairs(option.choices) do
						if ( allowed(c, dk) ) then
							row.choices[#row.choices + 1] = c
							if ( c.v == digit ) then row.at = #row.choices end
						end
					end
				end
			end
			if ( row and (#row.choices > 1 or row.kind == "later") ) then rows[#rows + 1] = row end
		end
	end
	if ( undead and W.category == accessories ) then
		rows[#rows + 1] = { name = "Undead", kind = "switch", undead = true, on = isUndead }
	end
	-- the Body tab: the body options after the looks' own
	local bodyTab = W.category == BODY_TAB
	for _, c in ipairs(model.categories) do if ( c.name == "Body" and c.id == W.category ) then bodyTab = true end end
	if ( bodyTab ) then bodyRows(rows) end
	-- Gear, last in every category: the starting outfit on or off (to see a skin)
	if ( type(WrathPP_SetGear) == "function" ) then rows[#rows + 1] = { name = "Gear", kind = "switch", gear = true, on = W.gear ~= false } end
	return rows, model
end

-- Puts a row's choice on.
function W.Choose(row, k)
	if ( row.body ) then
		local c = row.choices[k]
		if ( c and type(WrathPP_SetChoice) == "function" ) then WrathPP_SetChoice(row.body, c.v) end
		return
	end
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

-- The character with its starting outfit or without, to see the skin (the native mod's WrathPP_SetGear: the outfit taken
-- off as the game's own dressing takes it off, or the game's dressing itself). The game draws at its next step of a
-- customization: the hair colour stepped on and back.
function W.SetGear(on)
	if ( type(WrathPP_SetGear) ~= "function" ) then return end
	W.gear = on and true or false
	if ( WrathPP_SetGear(W.gear) ) then step(FIELD.haircolor, 1); step(FIELD.haircolor, -1) end
end

-- The game dresses the character again whenever its race, sex or class changes and when it randomizes.
function W.Regear()
	if ( W.gear == false ) then W.SetGear(false) end
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

-- A class's own choices. Shadowlands gives a death knight faces, eye colours and skins of its own and keeps the
-- others' from it (and its own from the others); the game here knows no such rule (every face is every class's in
-- its table, so that a death knight has faces at all), and what it picks by itself when the screen opens, at a new
-- race, sex or class, and at Randomize can be a choice this class may not have. Such a number is moved onto this
-- class's choice at the same place among its kind (a death knight's third face for the others' third).
function W.Normalize()
	local model, undead, dk = looks()
	if ( not model ) then return end
	local isUndead = undeadOn(model, undead)
	for _, option in ipairs(model.options) do
		local index = option.field and FIELD[option.field]
		if ( index and not (isUndead and option.field == "skin") ) then
			local value = number(index)
			local parts = model.fields[option.field]
			if ( value ~= nil and value < product(parts) ) then
				local digits = decode(value, parts)
				local current, mine = nil, {}
				for _, c in ipairs(option.choices) do
					if ( c.v == digits[option.part] ) then current = c end
					if ( allowed(c, dk) ) then mine[#mine + 1] = c end
				end
				if ( #mine > 0 and (not current or not allowed(current, dk)) ) then
					local place = 1
					if ( current ) then
						local n = 0
						for _, c in ipairs(option.choices) do
							if ( c.c == current.c ) then n = n + 1; if ( c == current ) then place = n end end
						end
					end
					digits[option.part] = mine[math.min(place, #mine)].v
					setNumber(index, encode(digits, parts))
				end
			end
		end
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
	-- (the content placed on whole pixels of the phone's screen: between them its text and pictures shimmer as it moves)
	function s:Place()
		local px = W.Pixel and W.Pixel() or 0
		self:SetVerticalScroll(px > 0 and math.floor(self.offset / px + 0.5) * px or self.offset)
		local limit = self:Limit()
		if ( limit <= 0 ) then self.bar:Hide(); return end
		local length = math.max(24, self.view * self.view / self.content)
		self.bar:SetHeight(length)
		self.bar:ClearAllPoints()
		self.bar:SetPoint("TOPRIGHT", self, "TOPRIGHT", -1, -(self.view - length) * (self.offset / limit))
		self.bar:Show()
	end
	function s:ScrollTo(offset) self.target = math.max(0, math.min(offset, self:Limit())); self.velocity = 0; self.flinging = false end
	function s:Reveal(top, bottom)
		if ( top < self.target ) then self:ScrollTo(top) elseif ( bottom > self.target + self.view ) then self:ScrollTo(bottom - self.view) end
	end
	-- Whether the list is moving (a finger on it, a fling, an ease): the creator does nothing heavy meanwhile.
	function s:Busy() return self.dragging or self.flinging or math.abs(self.target - self.offset) >= 0.25 end
	-- A drag: the content goes with the finger one for one, from where it was when the finger had moved past a few
	-- units (a tap stays a tap); where it was over the last tenth of a second is kept, for how fast it goes on after.
	local SLOP, KEEP = 6, 0.1
	function s:Press()
		local _, y = cursor()
		self.dragging, self.pressY, self.pressOffset, self.moved, self.velocity, self.flinging = true, y, self.offset, false, 0, false
		self.target = self.offset
		self.samples = {}
	end
	function s:Release()
		if ( not self.dragging ) then return end
		self.dragging = false
		self.velocity, self.flinging = 0, false
		local samples, now = self.samples or {}, GetTime()
		local last = samples[#samples]
		-- (a finger that stopped before it lifted throws nothing)
		if ( self.moved and last and now - last[1] < 0.06 ) then
			local first = samples[1]
			for _, p in ipairs(samples) do if ( now - p[1] <= KEEP ) then first = p; break end end
			if ( first and last[1] - first[1] > 0.008 ) then
				self.velocity = (last[2] - first[2]) / (last[1] - first[1])
				self.flinging = math.abs(self.velocity) > 40
			end
		end
		self.target = self.offset
	end
	-- A tap on something inside counts only if the finger didn't drag the list.
	function s:Tapped() return not self.moved end
	function s:Watch(frame)
		local list = self
		frame:SetScript("OnMouseDown", function() list:Press() end)
		frame:SetScript("OnMouseUp", function() list:Release() end)
	end
	function s:Update(elapsed)
		if ( elapsed <= 0 ) then return end
		local limit = self:Limit()
		if ( self.dragging ) then
			local _, y = cursor()
			local scale = (self.GetEffectiveScale and self:GetEffectiveScale()) or 1
			if ( scale <= 0 ) then scale = 1 end
			if ( not self.moved and math.abs(y - self.pressY) / scale > SLOP ) then
				-- from here on with the finger, without the slop's jump
				self.moved, self.pressY, self.pressOffset = true, y, self.offset
			end
			if ( self.moved ) then
				local offset = math.max(0, math.min(self.pressOffset + (y - self.pressY) / scale, limit))
				self.offset, self.target = offset, offset
				local now = GetTime()
				local samples = self.samples
				samples[#samples + 1] = { now, offset }
				while ( #samples > 2 and now - samples[1][1] > KEEP * 2 ) do table.remove(samples, 1) end
				self:Place()
			end
		elseif ( self.flinging ) then
			-- on with the speed it was let go at, slowing as a page on a phone does (a quarter second to lose two thirds),
			-- stopping at the ends
			self.offset = self.offset + self.velocity * elapsed
			self.velocity = self.velocity * math.exp(-elapsed * 4)
			if ( self.offset <= 0 or self.offset >= limit ) then self.offset = math.max(0, math.min(self.offset, limit)); self.velocity = 0 end
			if ( math.abs(self.velocity) < 15 ) then self.flinging, self.velocity = false, 0 end
			self.target = self.offset
			self:Place()
		elseif ( self.offset ~= self.target ) then
			-- the wheel, a reveal: eased there, the same share of the way each moment whatever the frame rate
			local gap = self.target - self.offset
			if ( math.abs(gap) < 0.25 ) then self.offset = self.target else self.offset = self.offset + gap * (1 - math.exp(-elapsed * 14)) end
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
-- Every number here is Shadowlands' own (Blizzard_CharacterCreate.xml, Blizzard_CharacterCustomize.xml and the shared
-- templates they inherit, build 9.2.7), through u().

-- Shadowlands darkens the screen's edges over the scene (charactercreate-vignette-*: 451 of 1080 down from the top, 577
-- up from the foot, 703 of 1920 in from each side): the same shares of this screen, whatever its shape.
local vignette = {}
for _, v in ipairs({ { "top", "charactercreate-vignette-top" }, { "bottom", "charactercreate-vignette-bottom" },
		{ "left", "charactercreate-vignette-sides" }, { "right", "charactercreate-vignette-sides", true } }) do
	local t = root:CreateTexture(nil, "BACKGROUND")
	vignette[#vignette + 1] = t
	vignette[v[1]] = t
	skin(function() atlas(t, v[2], false, v[3]) end)
	t:Hide()
end
local function placeVignette()
	local w = (GlueParent and GlueParent:GetWidth()) or 1024
	vignette.top:ClearAllPoints(); vignette.top:SetPoint("TOPLEFT", root, "TOPLEFT", 0, 0); vignette.top:SetPoint("TOPRIGHT", root, "TOPRIGHT", 0, 0); vignette.top:SetHeight(768 * 451 / 1080)
	vignette.bottom:ClearAllPoints(); vignette.bottom:SetPoint("BOTTOMLEFT", root, "BOTTOMLEFT", 0, 0); vignette.bottom:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", 0, 0); vignette.bottom:SetHeight(768 * 577 / 1080)
	vignette.left:ClearAllPoints(); vignette.left:SetPoint("TOPLEFT", root, "TOPLEFT", 0, 0); vignette.left:SetPoint("BOTTOMLEFT", root, "BOTTOMLEFT", 0, 0); vignette.left:SetWidth(w * 703 / 1920)
	vignette.right:ClearAllPoints(); vignette.right:SetPoint("TOPRIGHT", root, "TOPRIGHT", 0, 0); vignette.right:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", 0, 0); vignette.right:SetWidth(w * 703 / 1920)
end

-- Race and class. The factions' crests and names in the top corners (AllianceHeader, HordeHeader), the races down the
-- sides under them (AllianceRaces at 68, -106; 79 across, 18 between), the sexes at the top (Sexes: 46 across, 22
-- between, 27 down), the classes in a row at the foot (Classes: 67 across, 62 up).
local function header(alliance)
	local f = make("Frame", alliance and "WrathppAlliancePanel" or "WrathppHordePanel", root)
	f:SetWidth(u(92)); f:SetHeight(u(100))
	f:SetPoint(alliance and "TOPLEFT" or "TOPRIGHT", root, alliance and "TOPLEFT" or "TOPRIGHT", alliance and u(3) or -u(3), -u(10))
	f.logo = f:CreateTexture(nil, "ARTWORK"); f.logo:SetAllPoints(f)
	f.name = label(f, 18, "gold")
	if ( alliance ) then f.name:SetPoint("LEFT", f, "RIGHT", -u(18), -u(2)) else f.name:SetPoint("RIGHT", f, "LEFT", u(18), -u(2)) end
	f.name:SetText(alliance and (FACTION_ALLIANCE or "Alliance") or (FACTION_HORDE or "Horde"))
	skin(function() atlas(f.logo, alliance and "charactercreate-icon-alliance" or "charactercreate-icon-horde") end)
	-- the races' column under it
	f.races = make("Frame", alliance and "WrathppAllianceRaces" or "WrathppHordeRaces", root)
	f.races:SetWidth(u(79)); f.races:SetHeight(u(79))
	f.races:SetPoint(alliance and "TOPLEFT" or "TOPRIGHT", root, alliance and "TOPLEFT" or "TOPRIGHT", alliance and u(68) or -u(68), -u(106))
	return f
end
local alliancePanel, hordePanel = header(true), header(false)

local sexPanel = make("Frame", "WrathppSexPanel", root)
sexPanel:SetWidth(u(46 * 2 + 22)); sexPanel:SetHeight(u(46))
sexPanel:SetPoint("TOP", root, "TOP", 0, -u(27))

local classPanel = make("Frame", "WrathppClassPanel", root)
classPanel:SetWidth(u(969)); classPanel:SetHeight(u(67))
classPanel:SetPoint("BOTTOM", root, "BOTTOM", 0, u(62))

-- Customize (CharCustomizeFrame): the categories' round buttons in a row at the top right (Categories at -20, -166: 104
-- across, overlapping by 21), the dice left of them (9 away); the chosen category's options under them (Options at
-- -33, -297, 32 between rows); the view's five buttons at the top left (SmallButtons at 40, -30: 48 across,
-- overlapping by 5, 30 before the two that turn); Back and Finish at the foot (46 in, 28 up, 250 x 66).
local categoryPanel = make("Frame", "WrathppCategoryPanel", root)
categoryPanel:SetWidth(u(104)); categoryPanel:SetHeight(u(105))
categoryPanel:SetPoint("TOPRIGHT", root, "TOPRIGHT", -u(20), -u(166))

local optionPanel = make("Frame", "WrathppOptionPanel", root)
optionPanel:SetWidth(LIST_W); optionPanel:SetHeight(768 - u(297) - u(28 + 66 + 14))
optionPanel:SetPoint("TOPRIGHT", root, "TOPRIGHT", -u(33), -u(297))
local optionList = scroller("WrathppOptionList", optionPanel, LIST_W, 768 - u(297) - u(28 + 66 + 14))
optionList:SetPoint("TOPRIGHT", optionPanel, "TOPRIGHT", 0, 0)
local notice = label(optionPanel, 12, "grey"); notice:SetPoint("BOTTOMRIGHT", optionPanel, "TOPRIGHT", 0, u(6))

local viewPanel = make("Frame", "WrathppViewPanel", root)
viewPanel:SetWidth(u(48 * 5 - 5 * 4 + 30)); viewPanel:SetHeight(u(48))
viewPanel:SetPoint("TOPLEFT", root, "TOPLEFT", u(40), -u(30))

-- The name (NameChoiceFrame: 34 down from the top; "Name" in white at 18, and 2 under it the box, 343 x 48 of the grey
-- entry box's three pieces: SharedEditBoxTemplate, its left piece 13 wide, its right 314, the middle between; a dice
-- left of it for a name drawn at random, where the game allows one). The box that takes the name is the game's own,
-- laid over Shadowlands' pieces without its own border and "Name" (W.nameKept: as it was, for when the creator goes
-- off). Only with Shadowlands' art; without it the game's own box as it is.
local namePanel = make("Frame", "WrathppNamePanel", root)
namePanel:SetWidth(u(343)); namePanel:SetHeight(u(20 + 2 + 48))
namePanel:SetPoint("TOP", root, "TOP", 0, -u(34))
namePanel.title = label(namePanel, 18, "white"); namePanel.title:SetPoint("TOP", namePanel, "TOP", 0, 0); namePanel.title:SetHeight(u(20))
namePanel.title:SetText(NAME or "Name")
local nameBox = make("Frame", "WrathppNameBox", namePanel)
nameBox:SetWidth(u(343)); nameBox:SetHeight(u(48))
nameBox:SetPoint("TOP", namePanel, "TOP", 0, -u(20 + 2))
nameBox.left = nameBox:CreateTexture(nil, "BACKGROUND"); nameBox.left:SetWidth(u(13)); nameBox.left:SetHeight(u(48)); nameBox.left:SetPoint("LEFT", nameBox, "LEFT", 0, 0)
nameBox.right = nameBox:CreateTexture(nil, "BACKGROUND"); nameBox.right:SetWidth(u(314)); nameBox.right:SetHeight(u(48)); nameBox.right:SetPoint("RIGHT", nameBox, "RIGHT", 0, 0)
nameBox.middle = nameBox:CreateTexture(nil, "BACKGROUND")
nameBox.middle:SetPoint("TOPLEFT", nameBox.left, "TOPRIGHT", 0, 0); nameBox.middle:SetPoint("BOTTOMRIGHT", nameBox.right, "BOTTOMLEFT", 0, 0)
skin(function()
	atlas(nameBox.left, "common-gray-button-entrybox-left"); atlas(nameBox.right, "common-gray-button-entrybox-right"); atlas(nameBox.middle, "common-gray-button-entrybox-center")
end)
local randomName = smallButton("WrathppRandomName", namePanel, "charactercreate-icon-dice")
randomName:SetPoint("RIGHT", nameBox, "LEFT", 0, -u(1))
randomName:SetScript("OnClick", guarded(function()
	local stock = CharacterCreateRandomName
	local run = stock and stock.GetScript and stock:GetScript("OnClick")
	if ( run ) then run(stock) end
end))
namePanel:Hide()
local function restoreName()
	local k, edit = W.nameKept, CharacterCreateNameEdit
	if ( not k or not edit or not k.changed ) then return end
	k.changed = nil
	if ( k.backdrop ) then edit:SetBackdrop(k.backdrop) end
	edit:SetWidth(k.width); edit:SetHeight(k.height)
	if ( k.font[1] and edit.SetFont ) then edit:SetFont(k.font[1], k.font[2], k.font[3]) end
	if ( edit.SetJustifyH ) then edit:SetJustifyH("LEFT") end
	for _, r in ipairs(k.labels) do r:Show() end
end

-- The buttons at the foot (CharacterCreateNavButtonTemplate: BackButton at 46, 28 from the bottom left, ForwardButton
-- from the bottom right). On the first screen Back leaves for the list of characters, as the game's own Back does.
local customizeButton = redButton("WrathppCustomizeButton", root, "Customize", 250, 66, function() WrathppCreate_SetStep(2) end, "forward")
customizeButton:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", -u(46), u(28))
local leaveButton = redButton("WrathppLeaveButton", root, BACK or "Back", 250, 66, function()
	if ( type(CharacterCreate_Back) == "function" ) then CharacterCreate_Back() elseif ( CharCreateBackButton ) then CharCreateBackButton:Click() end
end, "back")
leaveButton:SetPoint("BOTTOMLEFT", root, "BOTTOMLEFT", u(46), u(28))
local backButton = redButton("WrathppBackButton", root, BACK or "Back", 250, 66, function() WrathppCreate_SetStep(1) end, "back")
backButton:SetPoint("BOTTOMLEFT", root, "BOTTOMLEFT", u(46), u(28))
local finishButton = redButton("WrathppFinishButton", root, "Finish", 250, 66, function()
	pcall(W.SendBody)
	if ( type(CharacterCreate_Okay) == "function" ) then CharacterCreate_Okay() else CreateCharacter(CharacterCreateNameEdit:GetText()) end
end)
finishButton:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", -u(46), u(28))
local randomizeButton = smallButton("WrathppRandomize", root, "charactercreate-icon-dice")
randomizeButton:SetScript("OnClick", guarded(function()
	local model, undead = looks()
	local wasUndead = undeadOn(model, undead)
	if ( type(CharacterCreate_Randomize) == "function" ) then CharacterCreate_Randomize() else RandomizeCharCustomization() end
	W.AfterRandomize(wasUndead)
	W.Normalize()
	W.Regear()
	WrathppCreate_Refresh()
end))
randomizeButton:SetPoint("RIGHT", categoryPanel, "LEFT", -u(9), 0)

-- Turning and zooming ------------------------------------------------------------------------------------------------

local function facing() return (type(GetCharacterCreateFacing) == "function" and GetCharacterCreateFacing()) or 0 end
local function turn(degrees)
	if ( type(SetCharacterCreateFacing) == "function" ) then SetCharacterCreateFacing(facing() + degrees) end
	if ( W.view and W.PaintViews ) then W.view = nil; W.PaintViews() end      -- turned by hand: no preset's view now
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

local ZOOM_MAX = 3.4
-- The zoom slider shows where the view is going, whoever moved it (a button, the wheel, a category, a preset).
function W.SyncZoomSlider()
	local s = W.zoomSlider
	if ( not s ) then return end
	W.syncingZoom = true
	s:SetValue(W.zoomTarget or W.zoom)
	W.syncingZoom = false
end

function W.SetZoom(zoom, focusY)
	W.zoomTarget = math.max(1, math.min(zoom, ZOOM_MAX))
	if ( focusY ) then W.focusTarget = focusY end
	W.SyncZoomSlider()
end

-- The middle of the screen: a finger across it turns the character (and, while zoomed, up and down moves the view).
local spinArea = make("Button", "WrathppSpinArea", root)
spinArea:SetPoint("TOPLEFT", root, "TOPLEFT", u(68 + 79 + 40), -u(110))
spinArea:SetPoint("BOTTOMRIGHT", root, "BOTTOMRIGHT", -(LIST_W + u(60)), u(62 + 67 + 60))
spinArea:EnableMouseWheel(true)
spinArea:SetScript("OnMouseDown", function()
	local x, y = cursor()
	W.turning, W.lastX, W.lastY, W.spin = true, x, y, 0
end)
spinArea:SetScript("OnMouseUp", function() W.turning = false end)
spinArea:SetScript("OnMouseWheel", function(self, delta) W.SetZoom((W.zoomTarget or W.zoom) + (delta or arg1 or 0) * 0.2) end)

local function holdButton(name, icon, held, tapped)
	local b = smallButton(name, viewPanel, icon)
	b:SetScript("OnClick", guarded(tapped or function() end))
	b.whileHeld = held
	return b
end
local resetView = holdButton("WrathppResetView", "common-icon-undo", nil, function()
	W.SetZoom(1, 0.6); W.spin = 0
	if ( type(SetCharacterCreateFacing) == "function" ) then SetCharacterCreateFacing(-15) end
end)
resetView:SetPoint("LEFT", viewPanel, "LEFT", 0, 0)
local zoomOut = holdButton("WrathppZoomOut", "common-icon-zoomout", nil, function() W.SetZoom((W.zoomTarget or W.zoom) - 0.3) end)
zoomOut:SetPoint("LEFT", resetView, "RIGHT", -u(5), 0)
local zoomIn = holdButton("WrathppZoomIn", "common-icon-zoomin", nil, function() W.SetZoom((W.zoomTarget or W.zoom) + 0.3) end)
zoomIn:SetPoint("LEFT", zoomOut, "RIGHT", -u(5), 0)
local turnLeft = holdButton("WrathppTurnLeft", "common-icon-rotateleft", function(elapsed) turn(-140 * elapsed) end)
turnLeft:SetPoint("LEFT", zoomIn, "RIGHT", u(30 - 5), 0)
local turnRight = holdButton("WrathppTurnRight", "common-icon-rotateright", function(elapsed) turn(140 * elapsed) end)
turnRight:SetPoint("LEFT", turnLeft, "RIGHT", -u(5), 0)

-- The zoom as a slider beside the turning buttons, and views a tap away under them (default, face, torso and rear, so a
-- change can be seen where it is). Shadowlands has no slider here: the track and thumb are drawn with plain colours
-- and the chosen ring's gold, files every client has. On the phone a finger dragged on it is a drag (tellScreen).
local zoomSlider = make("Slider", "WrathppZoomSlider", viewPanel)
zoomSlider:SetOrientation("HORIZONTAL")
zoomSlider:SetWidth(u(150)); zoomSlider:SetHeight(u(30))
zoomSlider:SetPoint("LEFT", turnRight, "RIGHT", u(14), 0)
zoomSlider:SetMinMaxValues(1, ZOOM_MAX); zoomSlider:SetValueStep(0.01)
zoomSlider:EnableMouse(true)
zoomSlider.track = zoomSlider:CreateTexture(nil, "BACKGROUND")
zoomSlider.track:SetHeight(u(8)); zoomSlider.track:SetPoint("LEFT", zoomSlider, "LEFT", 0, 0); zoomSlider.track:SetPoint("RIGHT", zoomSlider, "RIGHT", 0, 0)
zoomSlider.track:SetTexture(0.06, 0.06, 0.08, 0.9)
zoomSlider.edge = zoomSlider:CreateTexture(nil, "BORDER")
zoomSlider.edge:SetHeight(u(2)); zoomSlider.edge:SetPoint("LEFT", zoomSlider.track, "LEFT", 0, 0); zoomSlider.edge:SetPoint("RIGHT", zoomSlider.track, "RIGHT", 0, 0)
zoomSlider.edge:SetTexture(0.55, 0.45, 0.2, 0.9)
zoomSlider.thumb = zoomSlider:CreateTexture(nil, "OVERLAY")
zoomSlider.thumb:SetWidth(u(26)); zoomSlider.thumb:SetHeight(u(26))
skin(function() atlas(zoomSlider.thumb, "charactercreate-ring-select") end)
zoomSlider:SetThumbTexture(zoomSlider.thumb)
zoomSlider:SetScript("OnValueChanged", function(self, value)
	if ( W.syncingZoom ) then return end
	value = tonumber(value) or tonumber(arg1) or self:GetValue()
	W.view = nil
	W.zoomTarget = math.max(1, math.min(value, ZOOM_MAX))
end)
W.zoomSlider = zoomSlider
W.SyncZoomSlider()

-- The views: how near, the height on the screen the view comes in on (as the categories' own zoom), and for the rear
-- the character turned away (a little to the side, as the front view is: -15); a second tap on Rear turns it side on.
local VIEWS = {
	{ name = "Full", zoom = 1, focus = 0.6, facing = -15 },
	{ name = "Face", zoom = 3.0, focus = 0.76 },
	{ name = "Torso", zoom = 1.9, focus = 0.6 },
	{ name = "Rear", zoom = 2.1, focus = 0.44, facing = 165, again = 75 },
}
function W.View(name)
	for _, v in ipairs(VIEWS) do
		if ( v.name == name ) then
			-- (Rear tapped again: side on, and again: back to the rear)
			if ( W.view == name and v.again ) then W.viewAgain = not W.viewAgain else W.viewAgain = false end
			W.SetZoom(v.zoom, v.focus); W.spin = 0
			local face = W.viewAgain and v.again or v.facing
			if ( face and type(SetCharacterCreateFacing) == "function" ) then SetCharacterCreateFacing(face) end
			W.view = name
		end
	end
	if ( W.PaintViews ) then W.PaintViews() end
end
local viewButtons = {}
for k, v in ipairs(VIEWS) do
	local b = make("Button", "WrathppView"..v.name, viewPanel)
	b:SetWidth(u(120)); b:SetHeight(u(38))
	b:SetPoint("TOPLEFT", viewPanel, "BOTTOMLEFT", u(2), -u(12) - (k - 1) * u(46))
	b.back = b:CreateTexture(nil, "BACKGROUND"); b.back:SetAllPoints(b)
	b.glow = b:CreateTexture(nil, "HIGHLIGHT"); b.glow:SetAllPoints(b); b.glow:SetBlendMode("ADD"); b.glow:SetAlpha(0.3)
	b.caption = label(b, 14, "gold"); b.caption:SetPoint("CENTER", b, "CENTER", 0, 0); b.caption:SetText(v.name)
	function b:Paint()
		atlas(self.back, "charactercreate-customize-dropdownbox"..(W.view == v.name and "-open" or ""))
		atlas(self.glow, "charactercreate-customize-dropdownbox-hover")
	end
	b:SetScript("OnClick", guarded(function() W.View(v.name) end))
	skin(function() b:Paint() end)
	viewButtons[k] = b
end
function W.PaintViews() for _, b in ipairs(viewButtons) do b:Paint() end end

-- The categories -------------------------------------------------------------------------------------------------------

-- CharCustomizeCategoryButtonTemplate: 104 x 105, the ring (charactercreate-ring-metallight) 108 x 109, the gold ring
-- of the one chosen 93. Which picture a category has is the game's own table's (ChrCustomizationCategory): the head
-- for Face, the comb for Hair, the necklace for Accessories, the figure for Body and for Markings.
local CATEGORY_ART = { Face = "head", Hair = "hair", Accessories = "accessories", Body = "body", Markings = "body" }
local CATEGORY_PLAIN = {
	Face = "Interface\\Icons\\INV_Misc_Head_Human_01", Hair = "Interface\\Icons\\INV_Misc_Comb_01",
	Accessories = "Interface\\Icons\\INV_Jewelry_Necklace_07", Body = "Interface\\Icons\\INV_Chest_Cloth_21",
	Markings = "Interface\\Icons\\INV_Inscription_Tradeskill01",
}
local categoryButtons = {}
local function categoryButton(k)
	local b = categoryButtons[k]
	if ( not b ) then
		b = maskedButton("WrathppCategory"..k, categoryPanel, 104, 105, "charactercreate-ring-metallight", 108, 109, 93, "category")
		b.label = label(b, 12, "white"); b.label:Hide()
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
local function showCategory(b, name, chosen, female)
	local word = string.match(name or "", "^(%a+)") or ""
	local art = CATEGORY_ART[word] or "body"
	-- a woman's Body: her own picture (a figure; body_icon.py), where the art has it
	if ( word == "Body" and female and piece("charactercreate-icon-customize-figure") ) then art = "figure" end
	b:Set("charactercreate-icon-customize-"..art..(chosen and "-selected" or ""), chosen, false, CATEGORY_PLAIN[word] or "Interface\\Icons\\INV_Misc_QuestionMark", { 0.08, 0.92, 0.08, 0.92 })
end

-- The option rows --------------------------------------------------------------------------------------------------------

-- SelectionPopoutWithButtonsAndLabelTemplate: 223 x 38. The box (150 x 38, charactercreate-customize-dropdownbox) in
-- its middle, the next arrow 4 right of the box and the previous 5 left of it (32 x 32 each), the option's name ending
-- 34 left of the previous arrow (white, 14). In the box, in its middle: the choice's name (gold, 12), or its colour's
-- swatch, or its number where it has neither. A switch (CharCustomizeOptionCheckButtonTemplate) is the game's own
-- check box, 32 x 32, where the previous arrow would be.
local rowFrames = {}
local shown = {}

local function arrow(parent, piece)
	local b = make("Button", nil, parent)
	b:SetWidth(u(32)); b:SetHeight(u(32))
	b.back = b:CreateTexture(nil, "ARTWORK"); b.back:SetAllPoints(b)
	function b:Paint() atlas(self.back, "charactercreate-customize-"..piece..((not self:IsEnabled() and "-disabled") or (self.held and "-down") or "")) end
	b:SetScript("OnMouseDown", function(self) self.held = true; self:Paint() end)
	b:SetScript("OnMouseUp", function(self) self.held = false; self:Paint() end)
	skin(function() b:Paint() end)
	return b
end

local function rowFrame(k)
	local f = rowFrames[k]
	if ( f ) then return f end
	f = make("Frame", "WrathppRow"..k, optionList.child)
	f:SetWidth(LIST_W); f:SetHeight(u(38))
	f:SetPoint("TOPRIGHT", optionList.child, "TOPRIGHT", 0, -(k - 1) * ROW_PITCH - u(4))
	f.choice = make("Button", "WrathppRow"..k.."Choice", f)
	f.choice:SetWidth(u(150)); f.choice:SetHeight(u(38))
	f.choice:SetPoint("RIGHT", f, "RIGHT", -u((ROW_W - 150) / 2), 0)
	f.choice.back = f.choice:CreateTexture(nil, "BACKGROUND"); f.choice.back:SetAllPoints(f.choice)
	function f.choice:Paint() atlas(self.back, "charactercreate-customize-dropdownbox"..(self.open and "-open" or "")) end
	skin(function() f.choice:Paint() end)
	f.next = arrow(f, "nextbutton"); f.next:SetPoint("LEFT", f.choice, "RIGHT", u(4), 0)
	f.previous = arrow(f, "backbutton"); f.previous:SetPoint("RIGHT", f.choice, "LEFT", -u(5), 0)
	f.name = label(f, 14, "white")
	f.name:SetPoint("RIGHT", f.previous, "LEFT", -u(34), 0)
	f.name:SetPoint("LEFT", f, "LEFT", 0, 0)
	f.name:SetJustifyH("RIGHT")
	f.name:SetHeight(u(16))
	f.choice.label = label(f.choice, 12, "gold")
	f.choice.label:SetPoint("LEFT", f.choice, "LEFT", u(12), 0); f.choice.label:SetPoint("RIGHT", f.choice, "RIGHT", -u(12), 0)
	f.choice.label:SetJustifyH("CENTER"); f.choice.label:SetHeight(u(14))
	f.choice.swatch = swatch(f.choice); f.choice.swatch:SetPoint("CENTER", f.choice, "CENTER", 0, 0)
	f.choice.swatch2 = swatch(f.choice); f.choice.swatch2:SetWidth(u(36)); f.choice.swatch2:SetHeight(u(8)); f.choice.swatch2:SetPoint("LEFT", f.choice.swatch, "LEFT", u(18), -u(2))
	f.check = make("CheckButton", "WrathppRow"..k.."Check", f)
	f.check:SetWidth(u(32)); f.check:SetHeight(u(32))
	f.check:SetPoint("LEFT", f, "RIGHT", -u(ROW_W), 0)
	f.check:SetNormalTexture("Interface\\Buttons\\UI-CheckBox-Up")
	f.check:SetPushedTexture("Interface\\Buttons\\UI-CheckBox-Down")
	f.check:SetHighlightTexture("Interface\\Buttons\\UI-CheckBox-Highlight")
	f.check:SetCheckedTexture("Interface\\Buttons\\UI-CheckBox-Check")
	f.checkText = label(f, 12, "gold"); f.checkText:SetPoint("LEFT", f.check, "RIGHT", u(6), 0)
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
		if ( f.row.undead ) then W.SetUndead(self:GetChecked() and true or false)
		elseif ( f.row.gear ) then W.SetGear(self:GetChecked() and true or false)
		else W.Choose(f.row, self:GetChecked() and 2 or 1) end
	end))
	-- a drag that starts on a row moves the list (an arrow keeps its own pressed look as well)
	for _, piece in ipairs({ f, f.previous, f.next, f.choice, f.check }) do
		if ( piece.EnableMouse ) then piece:EnableMouse(true) end
		local down, up = piece:GetScript("OnMouseDown"), piece:GetScript("OnMouseUp")
		piece:SetScript("OnMouseDown", function(self, ...) optionList:Press(); if ( down ) then down(self, ...) end end)
		piece:SetScript("OnMouseUp", function(self, ...) optionList:Release(); if ( up ) then up(self, ...) end end)
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
			f.choice.label:SetText(""); paint(f.choice.swatch, nil); paint(f.choice.swatch2, nil)
		elseif ( row.kind == "later" ) then
			f.choice.label:SetText(row.why or (row.none and "None for this character") or "Not drawn yet")
			paint(f.choice.swatch, nil); paint(f.choice.swatch2, nil)
		else
			-- as Shadowlands' box shows the choice on: its colour, or its name, or (having neither) its number
			paint(f.choice.swatch, c and c.s, c and c.s2 and true); paint(f.choice.swatch2, c and c.s and c.s2)
			local name = c and describe(c, row.at) or ""
			f.choice.label:SetText((c and c.s and "") or (name ~= "" and name) or tostring(row.at or ""))
		end
		local dim = row.kind == "later"
		f:SetAlpha(dim and 0.45 or 1)
		if ( dim ) then f.previous:Disable(); f.next:Disable(); f.choice:Disable() else f.previous:Enable(); f.next:Enable(); f.choice:Enable() end
		f.previous:Paint(); f.next:Paint()
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

-- SelectionPopoutTemplate and its entries (SelectionPopoutButtonMixin:UpdatePopout): one column up to 10 choices, two
-- up to 24, three up to 36, four beyond, filled downwards column by column, and more columns where the screen has not
-- the height; an entry is a line 20 high: its number (gold, 25 wide), then its name or its colour's swatch, the one on
-- in gold (a colour's with charactercreate-customize-palette-selected round it) and the others grey. The first entry is
-- 6 in and 12 down, the list is 6 wider and 32 taller than its entries, and it hangs from the box's bottom right
-- corner, 3 right and 11 up. POP draws all of it larger: a line is a finger's target here.
local popout = make("Frame", "WrathppPopout", root)
popout:SetWidth(100); popout:SetHeight(100)
popout:SetFrameStrata("DIALOG")
popout:Hide()
popout.border = nineSlice(popout)
local catcher = make("Button", "WrathppPopoutCatcher", root)
catcher:SetAllPoints(root)
catcher:SetFrameStrata("HIGH")
catcher:Hide()
catcher:SetScript("OnClick", function() WrathppCreate_ClosePopout() end)
local cells = {}
local function p(n) return u(n * POP) end

local function cell(k)
	local b = cells[k]
	if ( b ) then return b end
	b = make("Button", "WrathppChoice"..k, popout)
	b:SetHeight(p(20))
	b.mark = b:CreateTexture(nil, "BACKGROUND"); b.mark:SetWidth(p(102)); b.mark:SetHeight(p(40))
	b.number = label(b, 12 * POP, "grey"); b.number:SetPoint("LEFT", b, "LEFT", p(14), 0); b.number:SetWidth(p(25)); b.number:SetJustifyH("LEFT")
	b.swatch = swatch(b); b.swatch:SetWidth(p(84)); b.swatch:SetHeight(p(20)); b.swatch:SetPoint("LEFT", b.number, "RIGHT", 0, 0)
	b.swatch2 = swatch(b); b.swatch2:SetWidth(p(36)); b.swatch2:SetHeight(p(8)); b.swatch2:SetPoint("LEFT", b.number, "RIGHT", p(18), -p(2))
	b.mark:SetPoint("LEFT", b.swatch, "LEFT", -p(4), 0)
	b.label = label(b, 12 * POP, "grey"); b.label:SetPoint("LEFT", b.number, "RIGHT", 0, 0); b.label:SetJustifyH("LEFT"); b.label:SetHeight(p(14))
	b:SetScript("OnClick", guarded(function(self)
		W.Choose(popout.row, self.index)
		WrathppCreate_Refresh()
	end))
	cells[k] = b
	return b
end

function WrathppCreate_ClosePopout()
	if ( popout.owner and popout.owner.choice ) then popout.owner.choice.open = nil; popout.owner.choice:Paint() end
	popout:Hide(); catcher:Hide()
	popout.row, popout.owner, popout.room = nil, nil, nil
	if ( W.TellScreen and not W.off ) then W.TellScreen(true) end
end

-- How many columns, and how many lines in each (Shadowlands' getNumColumnsAndStride).
local function columnsFor(n, most)
	local columns = (n > 36 and 4) or (n > 24 and 3) or (n > 10 and 2) or 1
	local stride = math.ceil(n / columns)
	if ( most and most >= 1 and stride > most ) then
		columns = math.ceil(n / most)
		stride = math.ceil(n / columns)
	end
	return columns, stride
end

local function fillPopout(room)
	local row = popout.row
	if ( not row ) then return end
	room = room or popout.room
	local n = #row.choices
	local named, coloured = false, false
	for _, c in ipairs(row.choices) do
		if ( c.n and c.n ~= "" ) then named = true end
		if ( c.s ) then coloured = true end
	end
	local columns, stride = columnsFor(n, room and math.floor((room - p(32)) / p(20)) or nil)
	-- an entry's width: its number and what follows it (CharCustomizeSelectionPopoutDetailsMixin:AdjustWidth)
	local details = 116
	if ( columns > 1 ) then details = (coloured and (25 + 36 + 18)) or (named and 108) or 42 end
	local width = p(14 + details + 14)
	for k = 1, n do
		local c, b = row.choices[k], cell(k)
		b.index = k
		b:SetWidth(width); b:ClearAllPoints()
		b:SetPoint("TOPLEFT", popout, "TOPLEFT", p(6) + math.floor((k - 1) / stride) * width, -p(12) - ((k - 1) % stride) * p(20))
		local on = k == row.at
		b.number:SetText(k)
		if ( on ) then b.number:SetTextColor(1, 0.82, 0); b.label:SetTextColor(1, 0.82, 0) else b.number:SetTextColor(0.5, 0.5, 0.5); b.label:SetTextColor(0.5, 0.5, 0.5) end
		paint(b.swatch, c.s, c.s2 and true); paint(b.swatch2, c.s and c.s2)
		b.label:SetWidth(p(details - 25))
		b.label:SetText((not c.s and describe(c, k)) or "")
		if ( on and c.s ) then atlas(b.mark, "charactercreate-customize-palette-selected"); b.mark:Show() else b.mark:Hide() end
		b:Show()
	end
	for k = n + 1, #cells do cells[k]:Hide() end
	popout:SetWidth(columns * width + p(6) * 2); popout:SetHeight(stride * p(20) + p(32))
	return stride, columns
end

function WrathppCreate_TogglePopout(f)
	if ( popout.owner == f ) then WrathppCreate_ClosePopout(); return end
	WrathppCreate_ClosePopout()
	local row = f.row
	if ( not row or row.kind ~= "list" ) then return end
	popout.row, popout.owner = row, f
	f.choice.open = true; f.choice:Paint()
	-- Under the box, as Shadowlands hangs it, or over it where there is more room there; as many columns as it takes
	-- for all of it to be on the screen.
	popout:ClearAllPoints()
	popout.room = nil
	local top, bottom = f.choice:GetTop(), f.choice:GetBottom()
	local screen = (GlueParent and GlueParent:GetHeight()) or 768
	local under = true
	if ( type(top) == "number" and type(bottom) == "number" and screen > 0 ) then
		local below, above = bottom + u(11) - u(24), screen - top + u(11) - u(24)
		local _, stride = columnsFor(#row.choices)
		under = (stride * p(20) + p(32) <= below) or (below >= above)
		popout.room = under and below or above
	end
	fillPopout()
	if ( under ) then popout:SetPoint("TOPRIGHT", f.choice, "BOTTOMRIGHT", u(3), u(11)) else popout:SetPoint("BOTTOMRIGHT", f.choice, "TOPRIGHT", u(3), -u(11)) end
	catcher:Show(); popout:Show()
	if ( W.ShotDue ) then W.ShotDue("a list", 0.6) end
	if ( W.TellScreen ) then W.TellScreen(true) end
end

-- The game's own pieces ---------------------------------------------------------------------------------------------------
-- The game's race, class and sex buttons keep doing the work and are not seen: each has one of Shadowlands' round
-- buttons here that shows what the game's button says (there or not, allowed or not, the one chosen) and, tapped,
-- does what a tap on the game's button does.

-- A place out of sight for the game's buttons: still shown or hidden, allowed or not, as the game sets them.
local away = make("Frame", "WrathppAway", root)
away:Hide()

local RACE_ART = { scourge = "undead", highmountaintauren = "highmountain", lightforgeddraenei = "lightforged", zandalaritroll = "zandalari" }
-- One of the game's buttons' own picture and its place in its file (the picture without Shadowlands' art).
local function plainOf(stock)
	local t = stock and stock.GetNormalTexture and stock:GetNormalTexture()
	if ( not t or not t.GetTexture ) then return nil end
	local coords
	if ( t.GetTexCoord ) then
		local ulx, uly, llx, lly, urx = t:GetTexCoord()
		if ( ulx and urx and lly ) then coords = { ulx, urx, uly, lly } end
	end
	return t:GetTexture(), coords
end

local raceButtons, classButtons, sexButtons = {}, {}, {}
local function raceButton(i, alliance)
	local b = raceButtons[i]
	if ( b ) then return b end
	-- CharacterCreateRaceButtonTemplate: 79 x 79, its faction's ring 139 x 140, the gold ring of the one chosen 118; the
	-- race's name under it (gold, 14, outlined)
	b = maskedButton("WrathppRace"..i, alliance and alliancePanel.races or hordePanel.races, 79, 79,
		alliance and "charactercreate-ring-alliance" or "charactercreate-ring-horde", 139, 140, 118, "race")
	b.name = label(b, 14, "gold", true); b.name:SetPoint("TOP", b, "BOTTOM", u(2), u(7))
	b:SetScript("OnClick", guarded(function(self)
		local stock = _G["CharacterCreateRaceButton"..self.index]
		if ( not stock or self.off ) then return end
		stock:SetChecked(1)
		CharacterRace_OnClick(stock, stock:GetID())
	end))
	raceButtons[i] = b
	return b
end
local function classButton(i)
	local b = classButtons[i]
	if ( b ) then return b end
	-- CharacterCreateClassButtonTemplate: 67 x 67, the dark ring 116 x 117, the gold ring 99; the class's name under it
	b = maskedButton("WrathppClass"..i, classPanel, 67, 67, "charactercreate-ring-metaldark", 116, 117, 99, "class")
	-- (ClassName: a box 85 x 50 whose top is 3 over the button's foot, the name in its middle, on two lines where it is long)
	b.name = label(b, 14, "gold"); b.name:SetPoint("TOP", b, "BOTTOM", u(2), u(3)); b.name:SetWidth(u(85)); b.name:SetHeight(u(50))
	b.name:SetJustifyH("CENTER"); b.name:SetJustifyV("MIDDLE")
	b:SetScript("OnClick", guarded(function(self)
		local stock = _G["CharacterCreateClassButton"..self.index]
		if ( not stock or self.off ) then return end
		CharacterClass_OnClick(stock:GetID())
	end))
	classButtons[i] = b
	return b
end
local function sexButton(i)
	local b = sexButtons[i]
	if ( b ) then return b end
	-- CharCustomizeSexButtonTemplate: 46 x 46, the dark ring 99 x 100, the gold ring 84
	b = maskedButton(i == 1 and "WrathppSexMale" or "WrathppSexFemale", sexPanel, 46, 46, "charactercreate-ring-metaldark", 99, 100, 84, "sex")
	b:SetPoint("LEFT", sexPanel, "LEFT", (i - 1) * u(46 + 22), 0)
	b:SetScript("OnClick", guarded(function() SetCharacterGender(i == 1 and (SEX_MALE or 2) or (SEX_FEMALE or 3)) end))
	sexButtons[i] = b
	return b
end

-- The game's own pieces as they were (whose child, where, shown or not) before this script moved, hid or showed
-- them: noted the first time the creator places anything, and put back as noted if it goes off, so that the game's
-- own screen is whole again (build 235's went off with the races, sexes and classes left in its hidden panels).
local kept, keptOrder = {}, {}
local function keep(f)
	if ( type(f) ~= "table" or kept[f] ) then return end
	local k = { parent = f:GetParent(), shown = f:IsShown() and true or false, points = {} }
	for i = 1, f:GetNumPoints() do k.points[i] = { f:GetPoint(i) } end
	kept[f] = k
	keptOrder[#keptOrder + 1] = f
end
local function keepAll()
	if ( W.keptAll ) then return end
	W.keptAll = true
	for _, name in ipairs({ "CharacterCreateGenderButtonMale", "CharacterCreateGenderButtonFemale", "CharacterCreateConfigurationFrame", "CharCreateRandomizeButton",
			"CharacterCreateCharacterClass", "CharacterCreateCharacterRace", "CharCreateOkayButton", "CharacterCreateRotateLeft", "CharacterCreateRotateRight",
			"CharacterCreateNameEdit", "CharacterCreateRandomName", "CharCreateBackButton", "CharacterCreateWoWLogo" }) do keep(_G[name]) end
	for _, prefix in ipairs({ "CharacterCreateRaceButton", "CharacterCreateClassButton", "CharacterCustomizationButtonFrame" }) do
		local i = 1
		while ( _G[prefix..i] ) do keep(_G[prefix..i]); keep(_G[prefix..i.."Text"]); i = i + 1 end
	end
end
local function putBack()
	for _, f in ipairs(keptOrder) do
		local k = kept[f]
		f:SetParent(k.parent)
		f:ClearAllPoints()
		for _, p in ipairs(k.points) do f:SetPoint(p[1], p[2] or k.parent, p[3], p[4], p[5]) end
	end
	-- shown or hidden as they were, once each is its own parent's again
	for _, f in ipairs(keptOrder) do if ( kept[f].shown ) then f:Show() else f:Hide() end end
end

local function place()
	keepAll()
	local female = GetSelectedSex and GetSelectedSex() == (SEX_FEMALE or 3)
	-- the sexes
	for i, name in ipairs({ "CharacterCreateGenderButtonMale", "CharacterCreateGenderButtonFemale" }) do
		local stock = _G[name]
		if ( stock ) then stock:SetParent(away) end
		local chosen = (i == 2) == (female and true or false)
		local file, coords = plainOf(stock)
		sexButton(i):Set("charactercreate-gendericon-"..(i == 1 and "male" or "female")..(chosen and "-selected" or ""), chosen, false, file, coords)
	end
	-- the races: the Alliance's down the left, the Horde's down the right; a side's sixth and later in a second column
	-- beside the first and 68 lower, as Shadowlands sets its allied races
	local names = { GetAvailableRaces() }
	local chosenRace = GetSelectedRace and GetSelectedRace()
	local count = { 0, 0 }
	local i, total = 1, 0
	while ( _G["CharacterCreateRaceButton"..i] ) do total = i; i = i + 1 end
	for index = 1, total do
		local stock = _G["CharacterCreateRaceButton"..index]
		stock:SetParent(away)
		local own = stock.GetName and stock:GetName() and _G[stock:GetName().."Text"]
		local token = names[(index - 1) * 3 + 2]
		token = token and string.upper(token) or nil
		-- races of the other realms' data that Wrath++ doesn't have (the user: "Naga and murloc are not supposed to be
		-- in this version"): their buttons are left out
		if ( token and LEFT_OUT[token] ) then token = nil; stock:Hide() end
		local alliance
		if ( token ) then alliance = ALLIANCE[token] and true or false else alliance = index <= math.ceil(total / 2) end
		local b = raceButton(index, alliance)
		b.index = index
		if ( stock:IsShown() and token ) then
			local side = alliance and 1 or 2
			count[side] = count[side] + 1
			local k = count[side]
			local column, line = (k > 5) and 1 or 0, (k > 5) and (k - 6) or (k - 1)
			b:ClearAllPoints()
			local x = column * u(79 + 18) * (alliance and 1 or -1)
			b:SetPoint(alliance and "TOPLEFT" or "TOPRIGHT", alliance and alliancePanel.races or hordePanel.races, alliance and "TOPLEFT" or "TOPRIGHT", x, -line * u(79 + 18) - column * u(68))
			local art = string.lower(token)
			local file, coords = plainOf(stock)
			b:Set("raceicon128-"..(RACE_ART[art] or art).."-"..(female and "female" or "male"), index == chosenRace, not stock:IsEnabled(), file, coords, not alliance)
			b.name:SetText(names[(index - 1) * 3 + 1] or "")
			b:Show()
		else
			b:Hide()
		end
		if ( own ) then own:Hide() end
	end
	-- the classes, in a row in the middle of the foot (15 between them, as twelve of Shadowlands' fill its 969)
	local classes = { GetAvailableClasses() }
	local _, _, chosenClass = GetSelectedClass()
	local n, shownClasses = 0, {}
	i = 1
	while ( _G["CharacterCreateClassButton"..i] ) do
		local stock = _G["CharacterCreateClassButton"..i]
		stock:SetParent(away)
		local b = classButton(i)
		b.index = i
		if ( stock:IsShown() ) then n = n + 1; shownClasses[n] = i else b:Hide() end
		i = i + 1
	end
	local pitch = u(67 + 15)
	-- Shadowlands' row is beside the foot's two buttons on a screen 16:9 wide; on a narrower one it would run into them,
	-- and stands over them instead (the buttons' 28 + 66, and the names' room)
	local width = (GlueParent and GlueParent:GetWidth()) or 1024
	local beside = (n * pitch - u(15)) / 2 + u(12) <= width / 2 - u(46 + 250)
	classPanel:ClearAllPoints()
	classPanel:SetPoint("BOTTOM", root, "BOTTOM", 0, beside and u(62) or u(28 + 66 + 50))
	for k, index in ipairs(shownClasses) do
		local stock, b = _G["CharacterCreateClassButton"..index], classButtons[index]
		b:ClearAllPoints()
		b:SetPoint("LEFT", classPanel, "CENTER", (k - 1) * pitch - (n * pitch - u(15)) / 2, 0)
		local token = classes[(index - 1) * 3 + 2]
		local file, coords = plainOf(stock)
		b:Set(token and ("classicon-"..string.lower(token)) or nil, index == chosenClass, not stock:IsEnabled(), file, coords)
		b.name:SetText(classes[(index - 1) * 3 + 1] or "")
		b:Show()
	end
	if ( CharacterCreateConfigurationFrame ) then CharacterCreateConfigurationFrame:Hide() end
	i = 1
	while ( _G["CharacterCustomizationButtonFrame"..i] ) do _G["CharacterCustomizationButtonFrame"..i]:Hide(); i = i + 1 end
	for _, name in ipairs({ "CharCreateRandomizeButton", "CharacterCreateCharacterClass", "CharacterCreateCharacterRace", "CharCreateOkayButton",
			"CharacterCreateRotateLeft", "CharacterCreateRotateRight", "CharacterCreateWoWLogo", "CharCreateBackButton" }) do
		if ( _G[name] ) then _G[name]:Hide() end
	end
	-- the name's box (the game's own, with its "Name" over it): at the top in the middle on Customize, where Shadowlands
	-- has its own (NameChoiceFrame, 34 down)
	local naming = W.step == 2
	local edit = CharacterCreateNameEdit
	-- the game's button for a random name is the game's to show (it does where names may be drawn)
	local drawn = ALLOW_RANDOM_NAME_BUTTON or (kept[CharacterCreateRandomName] and kept[CharacterCreateRandomName].shown)
	if ( edit ) then
		if ( not W.nameKept ) then
			local k = { backdrop = edit.GetBackdrop and edit:GetBackdrop(), width = edit:GetWidth(), height = edit:GetHeight(), font = {}, labels = {} }
			if ( edit.GetFont ) then k.font = { edit:GetFont() } end
			for _, r in ipairs({ edit:GetRegions() }) do
				if ( r.GetObjectType and r:GetObjectType() == "FontString" and r:IsShown() ) then k.labels[#k.labels + 1] = r end
			end
			W.nameKept = k
		end
		edit:ClearAllPoints()
		if ( W.art ) then
			-- over Shadowlands' box: no border and no "Name" of its own, the box's size, its text 20 high in the middle
			local k = W.nameKept
			if ( not k.changed ) then
				k.changed = true
				edit:SetBackdrop(nil)
				for _, r in ipairs(k.labels) do r:Hide() end
				edit:SetWidth(u(343 - 30)); edit:SetHeight(u(48))
				if ( edit.SetFont and k.font[1] ) then edit:SetFont(k.font[1], u(20), k.font[3]) end
				if ( edit.SetJustifyH ) then edit:SetJustifyH("CENTER") end
			end
			edit:SetPoint("CENTER", nameBox, "CENTER", 0, 0)
			if ( naming ) then namePanel:Show() else namePanel:Hide() end
			if ( naming and drawn ) then randomName:Show() else randomName:Hide() end
		else
			restoreName()
			edit:SetPoint("TOP", root, "TOP", 0, -u(34) - 22)
			namePanel:Hide()
		end
		if ( naming ) then edit:Show() else edit:Hide() end
	end
	if ( CharacterCreateRandomName ) then
		CharacterCreateRandomName:ClearAllPoints()
		CharacterCreateRandomName:SetPoint("RIGHT", edit or root, "LEFT", -6, 0)
		if ( naming and drawn and not W.art ) then CharacterCreateRandomName:Show() else CharacterCreateRandomName:Hide() end
	end
end

-- What is on the screen ---------------------------------------------------------------------------------------------------------

local function refresh()
	if ( W.off or W.step ~= 2 ) then return end
	W.refreshes = (W.refreshes or 0) + 1
	local model = looks()
	-- the categories of this race and sex, in a row that ends 20 from the screen's right edge
	local n = 0
	if ( model and number(FIELD.skin) ) then
		-- the Body tab last in the row (the user: "the tab needs to be the last tab"), the others in their own order
		local row = {}
		for _, c in ipairs(model.categories) do if ( c.name ~= "Body" ) then row[#row + 1] = c end end
		for _, c in ipairs(model.categories) do if ( c.name == "Body" ) then row[#row + 1] = c end end
		local bodyList, bodyWhy = bodyOptions()
		if ( row[#row].name ~= "Body" and (#bodyList > 0 or bodyWhy) ) then row[#row + 1] = { id = BODY_TAB, name = "Body", zoom = 100 } end
		local found = false
		for _, c in ipairs(row) do if ( c.id == W.category ) then found = true end end
		if ( not found ) then W.category = row[1].id end
		for k, c in ipairs(row) do
			local b = categoryButton(k)
			b.category, b.zoom = c.id, c.zoom
			b.label:SetText(c.name)
			b:ClearAllPoints()
			b:SetPoint("RIGHT", categoryPanel, "RIGHT", -(#row - k) * u(104 - 21), 0)
			showCategory(b, c.name, c.id == W.category, model.sex == 1)
			b:Show()
			n = k
		end
	end
	for k = n + 1, #categoryButtons do categoryButtons[k]:Hide() end
	if ( n > 1 ) then categoryPanel:SetWidth(u(104) + (n - 1) * u(104 - 21)); categoryPanel:Show() else categoryPanel:SetWidth(1); categoryPanel:Hide() end
	local rows = W.Rows()
	for k, row in ipairs(rows) do showRow(rowFrame(k), row) end
	for k = #rows + 1, #rowFrames do rowFrames[k]:Hide(); rowFrames[k].row = nil end
	shown = rows
	optionList:SetContentHeight(#rows * ROW_PITCH)
	if ( popout.owner and popout.owner.row and popout:IsShown() ) then
		popout.row = popout.owner.row
		if ( popout.row.kind == "list" ) then fillPopout() else WrathppCreate_ClosePopout() end
	end
	local race, sex, deathKnight = creating()
	log("customize: "..tostring(race).."_"..tostring(sex)..(deathKnight and " (a death knight)" or "")..", "..#rows.." rows, "..((model and number(FIELD.skin)) and "Shadowlands' options" or "the game's own five")
		..(sex == 1 and (", body options "..#(bodyOptions())..(select(2, bodyOptions()) and (" ("..select(2, bodyOptions())..")") or "")) or ""))
	if ( type(WrathPP_GetCustomization) ~= "function" ) then
		notice:SetText("Wrath++ add-on not running: the game's own five")
	elseif ( not model ) then
		notice:SetText("The game's own looks for this race and sex")
	else
		notice:SetText("")
	end
	-- an undead skin on a race not the Forsaken's own: the server makes the character one of them (mod-wrathpp-customization's
	-- WrathppUndeadStart: Deathknell, the Forsaken's quests, the Horde)
	local _, undead = looks()
	if ( model and undeadOn(model, undead) and race ~= RACE_ID.SCOURGE ) then
		notice:SetText("Undead: starts in Deathknell as one of the Forsaken, for the Horde")
	end
end

WrathppCreate_Refresh = guarded(refresh)

local function setStep(n)
	if ( W.off ) then return end
	W.step = n
	log(n == 1 and "screen: race and class" or "screen: customize")
	local first = n == 1
	W.DecideArt()
	placeVignette()
	for _, t in ipairs(vignette) do t:Show() end
	place()
	local function show(frame, on) if ( frame ) then if ( on ) then frame:Show() else frame:Hide() end end end
	show(alliancePanel, first); show(hordePanel, first); show(alliancePanel.races, first); show(hordePanel.races, first)
	show(classPanel, first); show(sexPanel, first)
	show(customizeButton, first); show(leaveButton, first)
	show(optionPanel, not first); show(randomizeButton, not first); show(viewPanel, not first)
	show(backButton, not first); show(finishButton, not first)
	if ( first ) then categoryPanel:Hide(); WrathppCreate_ClosePopout(); W.SetZoom(1, 0.6) end
	spinArea:Show()
	WrathppCreate_Refresh()
	W.ShotDue(first and "race and class" or "customize", 1.5)
	if ( W.TellScreen ) then W.TellScreen(true) end
end

WrathppCreate_SetStep = guarded(setStep)

-- The game's own screen back, and why.
-- The character as the game has it, for the log: race_sex, class, and each of the five numbers as "on/of how many".
local function stateLine()
	local parts = {}
	pcall(function()
		if ( type(WrathPP_GetCreating) == "function" ) then
			local race, sex, class = WrathPP_GetCreating()
			parts[#parts + 1] = tostring(race).."_"..tostring(sex).." class "..tostring(class)
		end
		if ( type(WrathPP_GetCustomization) == "function" ) then
			for i = 1, 5 do
				local current, count = WrathPP_GetCustomization(i)
				parts[#parts + 1] = tostring(current).."/"..tostring(count)
			end
		end
	end)
	return table.concat(parts, " ")
end

function WrathppCreate_Disable(reason)
	W.off = true
	pcall(tellScreen, false)
	log("off: "..tostring(reason))
	log("off with the character "..stateLine())
	-- the game's own screen whole again: this script's pieces away (each by itself: one that fails doesn't keep the rest),
	-- the game's back where and as they were, the view as the game has it
	for _, f in ipairs({ alliancePanel, hordePanel, alliancePanel.races, hordePanel.races, sexPanel, classPanel, categoryPanel, optionPanel, viewPanel,
			customizeButton, leaveButton, backButton, finishButton, randomizeButton, spinArea, popout, catcher }) do pcall(f.Hide, f) end
	for _, t in ipairs(vignette) do pcall(t.Hide, t) end
	pcall(namePanel.Hide, namePanel)
	pcall(restoreName)
	pcall(putBack)
	W.zoom, W.zoomTarget = 1, 1
	pcall(W.ApplyZoom)
	if ( not W.reason ) then
		W.reason = text(root)
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
	W.view, W.viewAgain = nil, false
	pcall(W.SyncZoomSlider); pcall(W.PaintViews)
	W.fresh = 3
	W.gear = true                                         -- the game dresses the character as the creator opens
	if ( type(WrathPP_ResetChoices) == "function" ) then pcall(WrathPP_ResetChoices) end   -- the body options from their defaults
	log("opened: native "..tostring(type(WrathPP_NativeVersion) == "function" and WrathPP_NativeVersion() or "none")
		..", looks' options "..(type(WrathppLooks) == "table" and "in" or "not in")..", undead skins "..(type(WrathppUndead) == "table" and "in" or "not in"))
	-- whether the realm's extra choices are here (the appearance add-on, the realm's hello and registry): the Body tab's
	-- options are there only when they are
	if ( type(WrathPP_Status) == "function" ) then
		local ok, state, reason, version = pcall(WrathPP_Status)
		log("appearance add-on: "..tostring(ok and state or "error")..(reason and (" ("..tostring(reason)..")") or "")..", registry "..tostring(version))
	else
		log("appearance add-on: not running")
	end
	W.ApplyZoom()
	WrathppCreate_SetStep(1)
	W.Normalize()
end)
if ( type(CharacterCreate_OnShow) == "function" ) then
	after("CharacterCreate_OnShow", function() W.made = true; W.pending = nil; opened() end)
end
for _, name in ipairs({ "SetCharacterRace", "SetCharacterGender", "SetCharacterClass", "CharacterCreate_UpdateHairCustomization" }) do
	after(name, guarded(function()
		WrathppCreate_ClosePopout()
		place()
		if ( name ~= "CharacterCreate_UpdateHairCustomization" ) then W.Normalize(); W.Regear() end
		WrathppCreate_Refresh()
	end))
end

-- What the app's touch is told (the native mod's WrathPP_SetScreen, a file it reads): the creator is up, and where a
-- finger drags a list (the options, an open list of choices) in thousandths of the screen from its bottom left. On the
-- creator a finger that moves elsewhere turns the character; without this word the app looked for the 3.3.5 creator's
-- banners, which this screen has not, and a swipe walked (W, A, S, D: build 243).
local lastScreen
local function tellScreen(up)
	if ( type(WrathPP_SetScreen) ~= "function" ) then return end
	local text = "creator 0"
	if ( up ) then
		local w, h = (GlueParent and GlueParent:GetWidth()) or 0, (GlueParent and GlueParent:GetHeight()) or 0
		local parts = { "creator 1 drag" }
		local function add(f)
			if ( not f or not f:IsVisible() or w <= 0 or h <= 0 ) then return end
			local l, b, r, t = f:GetLeft(), f:GetBottom(), f:GetRight(), f:GetTop()
			if ( not (l and b and r and t) ) then return end
			parts[#parts + 1] = string.format("%d %d %d %d", math.floor(l / w * 1000), math.floor(b / h * 1000), math.ceil(r / w * 1000), math.ceil(t / h * 1000))
		end
		if ( W.step == 2 and optionList.content > optionList.view ) then add(optionList) end
		if ( popout:IsShown() ) then add(popout) end
		if ( W.step == 2 ) then add(W.zoomSlider) end
		text = table.concat(parts, " ")
	end
	if ( text == lastScreen ) then return end
	lastScreen = text
	pcall(WrathPP_SetScreen, text)
end
W.TellScreen = tellScreen

-- Pictures of the creator as the game draws it, for the app's report (WrathppShots: set by the app when it has no
-- pictures of this build yet; the game's own Screenshot, as its Print Screen key takes one): each of the two screens a
-- moment after it is first up, and the first list of choices opened. Three at most a launch; nothing without the
-- app's asking. What the rig cannot show (the game's own drawing of the art, the fonts, the scene) is seen from these.
local shots = { taken = {}, due = {}, count = 0 }
function W.ShotDue(what, seconds)
	if ( WrathppShots == nil or type(Screenshot) ~= "function" or shots.taken[what] or shots.count >= 3 ) then return end
	shots.due[what] = shots.due[what] or seconds
end
local function shoot(elapsed)
	for what, left in pairs(shots.due) do
		left = left - elapsed
		if ( left > 0 ) then shots.due[what] = left
		else
			shots.due[what] = nil
			-- still the screen it was asked for (the list still open, the same step)
			local still = (what == "a list" and popout:IsShown()) or (what == "race and class" and W.step == 1 and not popout:IsShown())
				or (what == "customize" and W.step == 2 and not popout:IsShown())
			if ( still and not shots.taken[what] and shots.count < 3 ) then
				shots.taken[what] = true; shots.count = shots.count + 1
				local ok = pcall(Screenshot)
				log("shot "..shots.count..": "..what..(ok and "" or " (the game would not take it)"))
			end
		end
	end
end

-- Every frame: the lists easing, the character turning, the view coming nearer; four times a second the rows again
-- (what the game's own state is, however it changed).
local driver = make("Frame", "WrathppDriver", root)
local sinceRefresh, sinceScreen = 0, 0
-- The screen shown: the game's own OnShow may not have run yet (this frame's runs first), and until it has there is no
-- character, so nothing is opened from here: the first frame drawn after it opens the creator (OnUpdate below).
driver:SetScript("OnShow", function() if ( not W.off ) then W.pending = 1 end end)
-- Closed (a character made, or Back): the next opening starts dressed, and the log says the creator was left.
driver:SetScript("OnHide", function() W.gear = true; W.pending = nil; W.made = nil; log("closed"); tellScreen(false) end)
driver:SetScript("OnUpdate", guarded(function(self, elapsed)
	elapsed = elapsed or arg1 or 0
	if ( W.pending ) then
		-- a frame after the screen was shown: the game's OnShow has run, its character is there
		W.pending = W.pending - 1
		if ( W.pending > 0 ) then return end
		W.made = true
		if ( not hasCharacter() ) then W.pending = 1; log("waiting: the game has no character on the creator yet"); return end
		W.pending = nil
		opened()
		return
	end
	if ( not hasCharacter() ) then return end
	if ( (W.fresh or 0) > 0 ) then
		W.fresh = W.fresh - 1
		WrathppCreate_SetStep(W.step)
	end
	for _, s in ipairs(scrollers) do s:Update(elapsed) end
	shoot(elapsed)
	sinceScreen = sinceScreen + elapsed
	if ( sinceScreen >= 0.2 ) then sinceScreen = 0; tellScreen(true) end
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
	-- the rows read again four times a second, but not while a list moves: reading them sets every row's text and
	-- pictures again, and done under a finger it made the list stutter
	sinceRefresh = sinceRefresh + elapsed
	local moving = false
	for _, s in ipairs(scrollers) do if ( s:Busy() ) then moving = true end end
	if ( sinceRefresh >= 0.25 and not moving ) then sinceRefresh = 0; WrathppCreate_Refresh() end
end, true))

-- Nothing of this shows before the creator is opened (the game's own pieces are moved then, not now).
for _, f in ipairs({ alliancePanel, hordePanel, alliancePanel.races, hordePanel.races, sexPanel, classPanel, categoryPanel, optionPanel, viewPanel,
		customizeButton, leaveButton, backButton, finishButton, randomizeButton, spinArea }) do f:Hide() end

end -- build

local ok, err = pcall(build)
if ( ok ) then
	log("built")
else
	-- the game's own screen, untouched, and why
	W.off, W.error = true, err
	log("off at build: "..tostring(err))
	for _, f in ipairs(made) do pcall(f.Hide, f) end
	pcall(function()
		local s = root:CreateFontString(nil, "OVERLAY", "GlueFontHighlightSmall")
		s:SetPoint("TOP", root, "TOP", 0, -4)
		s:SetText("Wrath++ creator off: "..tostring(err))
	end)
end
