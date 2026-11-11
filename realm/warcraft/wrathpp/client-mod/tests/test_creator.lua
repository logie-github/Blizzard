-- Wrath++'s creator script (app/src/main/assets/wrathpp/WrathppCreate.lua) on a mock of the 3.3.5 glue frames and
-- functions it uses: its two steps, the client's own buttons moved, a tile tapped reaching that option by the client's
-- own arrows, and the column without the native mod.
local script = arg[1]
local fails = 0
local function check(cond, what) print((cond and "ok   " or "FAIL ")..what); if not cond then fails = fails + 1 end end

local Frame = {}
Frame.__index = function(t, k) return Frame[k] or function() end end
local function frame(name)
	local f = setmetatable({ name = name, shown = true, scripts = {} }, Frame)
	if name then _G[name] = f end
	return f
end
function Frame:GetName() return self.name end
function Frame:Show() self.shown = true end
function Frame:Hide() self.shown = false end
function Frame:IsShown() return self.shown end
function Frame:SetParent(p) self.parent = p end
function Frame:SetScript(k, fn) self.scripts[k] = fn end
function Frame:Click() self.scripts.OnClick(self) end
function Frame:SetText(t) self.text = t end
function Frame:GetText() return self.text end
function Frame:SetBackdropBorderColor(r, g, b) self.border = { r, g, b } end
function Frame:CreateFontString() return frame(nil) end
_G.CreateFrame = function(_, name) return frame(name) end

for _, n in ipairs({ "CharacterCreate", "CharacterCreateFrame", "CharacterCreateCharacterClass", "CharacterCreateCharacterRace",
		"CharacterCreateConfigurationFrame", "CharacterCreateGenderButtonMale", "CharacterCreateGenderButtonFemale",
		"CharCreateRandomizeButton", "CharCreateOkayButton", "CharCreateBackButton", "CharacterCreateNameEdit", "CharacterCreateRandomName" }) do frame(n) end
for i = 1, 10 do frame("CharacterCreateClassButton"..i) end
local labels = { "Skin Color", "Face", "Hair Style", "Hair Color", "Facial Hair" }
for i = 1, 5 do
	frame("CharacterCustomizationButtonFrame"..i)
	frame("CharacterCustomizationButtonFrame"..i.."Text"):SetText(labels[i])
end
NUM_CHAR_CUSTOMIZATIONS = 5

-- The client's state as the native mod reads it, and its own arrows stepping it.
local state = { { 1, 14 }, { 1, 10 }, { 1, 10 }, { 1, 7 }, { 1, 8 } }
local steps = 0
function CharacterCustomization_Right(i) steps = steps + 1; state[i][1] = state[i][1] % state[i][2] + 1 end
function CharacterCustomization_Left(i) steps = steps + 1; state[i][1] = (state[i][1] - 2) % state[i][2] + 1 end
local created = false
function CharacterCreate_Okay() created = true end
function CharacterCreate_Randomize() end
function CharacterCreate_OnShow() end

dofile(script)

-- Without the native mod.
check(WrathppClassPanel.shown and not WrathppOptionPanel.shown, "step 1: the class column, no options")
check(CharacterCreateClassButton3.parent == WrathppClassPanel, "  the client's class buttons are in it")
check(CharacterCreateGenderButtonFemale.parent == WrathppGenderPanel, "  the gender buttons in the Gender panel")
check(WrathppCustomizeButton.shown and not CharCreateOkayButton.shown and not CharacterCreateNameEdit.shown, "  Customize, no Accept, no name yet")
check(not CharacterCustomizationButtonFrame1.shown, "  the old rows are gone")
WrathppCustomizeButton:Click()
check(WrathppOptionPanel.shown and WrathppCategoryPanel.shown and not WrathppClassPanel.shown, "Customize: categories and options")
check(not CharacterCreateConfigurationFrame.shown, "  the races put away")
check(WrathppFinishButton.shown and WrathppBackButton.shown and CharacterCreateNameEdit.shown, "  Finish, Back, the name")
check(WrathppOptionTile1.number.text == "<" and WrathppOptionTile2.number.text == ">", "without the native mod: previous and next")
WrathppOptionTile2:Click()
check(state[1][1] == 2, "  and they step the client's own")

-- With it.
function WrathPP_GetCustomization(i) return state[i][1], state[i][2] end
WrathppCategory2:Click()
check(WrathppCategory2.text == "Face", "category 2 is Face")
check(WrathppOptionTile1.number.text == 1 and WrathppOptionTile5.number.text == 5, "the column: options 1 to 5")
check(WrathppOptionTile1.border[2] == 0.82, "  the one on is lit")
steps = 0
WrathppOptionTile4:Click()
check(state[2][1] == 4 and steps == 3, "tapping 4 steps the face to 4, three steps")
state[2][1] = 9; WrathppCreate_Refresh()
check(WrathppOptionTile5.number.text == 9 and WrathppOptionTile5.border[2] == 0.82, "the column follows the one on (9)")
steps = 0
WrathppOptionTile1.option = 1; WrathppOptionTile1:Click()
check(state[2][1] == 1 and steps == 2, "  back to 1 the shorter way round (two steps)")
WrathppOptionsDown:Click(); WrathppOptionsDown:Click(); WrathppCreate_Refresh()
check(WrathppOptionTile1.number.text == 3, "the arrows scroll the column (and it stays)")
labels[5] = "Markings"; CharacterCustomizationButtonFrame5Text:SetText("Markings"); WrathppCreate_Refresh()
check(WrathppCategory5.text == "Markings", "the race's own name for a customization")
WrathppFinishButton:Click()
check(created, "Finish creates the character")
WrathppBackButton:Click()
check(WrathppClassPanel.shown and CharacterCreateConfigurationFrame.shown, "Back: step 1 again")
print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
