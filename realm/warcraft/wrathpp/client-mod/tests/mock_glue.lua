-- A stand-in for the 3.3.5 character creation screen (GlueXML's CharacterCreate): its frames, the functions the creator's
-- script calls, and the game's five numbers behind them. For test_creator.lua and test_creator_data.lua:
--   local mock = dofile("mock_glue.lua")     mock.game, mock.state (the five numbers, from 0), mock.counts
-- Frames: whatever is called on one that isn't below does nothing.
local Frame = {}
local function nothing() end
-- (a frame's methods begin with a capital; anything else not set is nil, as in the game)
Frame.__index = function(t, k) return Frame[k] or (type(k) == "string" and k:match("^[A-Z]") and nothing) or nil end
local function frame(name, kind)
	local f = setmetatable({ name = name, kind = kind, shown = true, scripts = {}, points = {}, w = 0, h = 0, enabled = true, alpha = 1 }, Frame)
	if name then _G[name] = f end
	return f
end
function Frame:GetName() return self.name end
function Frame:Show() self.shown = true end
function Frame:Hide() self.shown = false end
function Frame:IsShown() return self.shown end
function Frame:SetParent(p) self.parent = p end
function Frame:GetParent() return self.parent end
function Frame:SetScript(k, fn) self.scripts[k] = fn end
function Frame:GetScript(k) return self.scripts[k] end
function Frame:HookScript(k, fn) local old = self.scripts[k]; self.scripts[k] = function(...) if old then old(...) end; fn(...) end end
function Frame:Click() if self.scripts.OnMouseDown then self.scripts.OnMouseDown(self) end; if self.scripts.OnMouseUp then self.scripts.OnMouseUp(self) end; self.scripts.OnClick(self) end
function Frame:SetText(t) self.text = t end
function Frame:GetText() return self.text end
function Frame:SetWidth(w) self.w = w end
function Frame:SetHeight(h) self.h = h end
function Frame:GetWidth() return self.w end
function Frame:GetHeight() return self.h end
function Frame:GetEffectiveScale() return 1 end
function Frame:SetAlpha(a) self.alpha = a end
function Frame:Enable() self.enabled = true end
function Frame:Disable() self.enabled = false end
function Frame:SetChecked(c) self.checked = c and true or false end
function Frame:GetChecked() return self.checked and 1 or nil end
function Frame:ClearAllPoints() self.points = {} end
function Frame:SetPoint(...) self.points[#self.points + 1] = { ... } end
function Frame:SetAllPoints(to) self.points = { { "ALL", to } } end
function Frame:SetBackdropBorderColor(r, g, b) self.border = { r, g, b } end
function Frame:SetVerticalScroll(v) self.scroll = v end
function Frame:SetScrollChild(c) self.scrollChild = c end
function Frame:SetTexture(r, g, b) self.texture = { r, g, b } end
function Frame:CreateFontString() return frame(nil, "FontString") end
function Frame:CreateTexture() return frame(nil, "Texture") end
function Frame:GetFrameLevel() return 1 end
_G.CreateFrame = function(kind, name, parent)
	local f = frame(name, kind)
	f.parent = parent
	return f
end

-- The game's screen: ten races, their buttons, the classes, the rows it has itself.
local TOKENS = { "Human", "Dwarf", "NightElf", "Gnome", "Draenei", "Orc", "Scourge", "Tauren", "Troll", "BloodElf" }
frame("GlueParent"); GlueParent:SetWidth(1366); GlueParent:SetHeight(768)
for _, n in ipairs({ "CharacterCreate", "CharacterCreateFrame", "CharacterCreateCharacterClass", "CharacterCreateCharacterRace",
		"CharacterCreateConfigurationFrame", "CharacterCreateGenderButtonMale", "CharacterCreateGenderButtonFemale",
		"CharCreateRandomizeButton", "CharCreateOkayButton", "CharCreateBackButton", "CharacterCreateNameEdit", "CharacterCreateRandomName",
		"CharacterCreateRotateLeft", "CharacterCreateRotateRight" }) do frame(n) end
for i = 1, 10 do frame("CharacterCreateRaceButton"..i); frame("CharacterCreateClassButton"..i) end
local labels = { "Skin Color", "Face", "Hair Style", "Hair Color", "Facial Hair" }
for i = 1, 5 do
	frame("CharacterCustomizationButtonFrame"..i)
	frame("CharacterCustomizationButtonFrame"..i.."Text"):SetText(labels[i])
end
NUM_CHAR_CUSTOMIZATIONS = 5
SEX_MALE, SEX_FEMALE = 2, 3

-- game.character: whether the game has a character on the creator. The client makes it in its own OnShow
-- (ResetCharCustomize), and these of its functions read it without looking whether there is one (the decompiled
-- client's CharacterCreation_Scripts.cpp: GetSelectedClass, GetSelectedSex, GetNameForRace, GetAvailableRaces,
-- GetAvailableClasses, GetClassesForRace, GetFacialHairCustomization, and through the character CycleCharCustomization,
-- RandomizeCharCustomization, SetCharacterCreateFacing): called without one the game dies (12 November 2026: reading
-- 0x1C in GetSelectedClass). Here such a call is counted in game.crashes, which a test wants at 0.
local game = { race = 1, sex = 3, class = "WARRIOR", facing = 0, cursor = { 0, 0 }, cycles = 0, sets = 0, created = nil, fail = false,
	character = false, crashes = 0, crashedIn = {} }
local function needsCharacter(name)
	if ( not game.character ) then game.crashes = game.crashes + 1; game.crashedIn[#game.crashedIn + 1] = name end
end
-- the five numbers (from 0) and how many of each: a human woman's as the test's looks have them, four undead skins after
local state = { 2, 0, 0, 0, 0 }
local counts = { 3 + 4, 3 * 2, 4, 3, 3 * 2 }
function GetAvailableRaces()
	needsCharacter("GetAvailableRaces")
	local out = {}
	for _, t in ipairs(TOKENS) do out[#out + 1] = t.." people"; out[#out + 1] = t; out[#out + 1] = 1 end
	return unpack(out)
end
function GetNameForRace() needsCharacter("GetNameForRace"); if game.fail then error("the game said no") end; return TOKENS[game.race].." people", TOKENS[game.race] end
function GetSelectedSex() needsCharacter("GetSelectedSex"); return game.sex end
function GetSelectedClass() needsCharacter("GetSelectedClass"); return game.class == "DEATHKNIGHT" and "Death Knight" or "Warrior", game.class end
function CycleCharCustomization(i, delta)
	needsCharacter("CycleCharCustomization")
	game.cycles = game.cycles + 1
	state[i] = (state[i] + (delta > 0 and 1 or -1)) % counts[i]
end
function RandomizeCharCustomization() needsCharacter("RandomizeCharCustomization"); for i = 1, 5 do state[i] = game.random and game.random[i] or 0 end end
function CharacterCreate_Randomize() RandomizeCharCustomization() end
function GetCharacterCreateFacing() return game.facing end
function SetCharacterCreateFacing(f) needsCharacter("SetCharacterCreateFacing"); game.facing = f end
function GetCursorPosition() return game.cursor[1], game.cursor[2] end
function CharacterCreate_Okay() game.created = true end
-- The game's own OnShow makes the character (ResetCharCustomize) before anything else of it.
function CharacterCreate_OnShow() game.character = true end
function SetCharacterRace() end
function SetCharacterGender() end
function SetCharacterClass() end
function CharacterCreate_UpdateHairCustomization() end

-- stockOnShow: the game's own OnShow as the screen was made with it (a screen bound to the function itself never calls
-- a name wrapped later).
return { game = game, state = state, counts = counts, tokens = TOKENS, frame = frame, stockOnShow = CharacterCreate_OnShow }
