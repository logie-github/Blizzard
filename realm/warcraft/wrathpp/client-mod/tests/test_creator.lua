-- Wrath++'s creator script (app/src/main/assets/wrathpp/WrathppCreate.lua) on a mock of the 3.3.5 glue frames it uses:
-- runs without the native mod and with it, and checks the boxes, the hidden description boxes and the rows moved in.
local script = arg[1]
local fails = 0
local function check(cond, what) print((cond and "ok   " or "FAIL ")..what); if not cond then fails = fails + 1 end end

local Frame = {}
Frame.__index = function(t, k) return Frame[k] or function() end end
local function frame(name)
	local f = setmetatable({ name = name, shown = true, children = {} }, Frame)
	if name then _G[name] = f end
	return f
end
function Frame:GetName() return self.name end
function Frame:Show() self.shown = true end
function Frame:Hide() self.shown = false end
function Frame:IsShown() return self.shown end
function Frame:SetParent(p) self.parent = p end
function Frame:SetScript(k, fn) self[k] = fn end
function Frame:SetText(t) self.text = t end
function Frame:GetText() return self.text end
function Frame:CreateFontString() return frame(nil) end
_G.CreateFrame = function(_, name) return frame(name) end

frame("CharacterCreate"); frame("CharacterCreateFrame"); frame("CharacterCreateCharacterClass"); frame("CharacterCreateCharacterRace")
local labels = { "Skin Color", "Face", "Hair Style", "Hair Color", "Facial Hair" }
for i = 1, 5 do
	local row = frame("CharacterCustomizationButtonFrame"..i)
	for _, part in ipairs({ "Left", "Right", "Middle" }) do frame(row.name..part) end
	frame(row.name.."Text"):SetText(labels[i])
end
NUM_CHAR_CUSTOMIZATIONS = 5
local cycled = {}
function CharacterCustomization_Right(i) cycled[#cycled + 1] = i end

dofile(script)
check(WrathppAppearance and WrathppAppearance.shown, "the Appearance column is up")
check(not CharacterCreateCharacterClass.shown and not CharacterCreateCharacterRace.shown, "the description boxes on the right are hidden")
check(WrathppAppearanceBox2 and WrathppAppearanceBox2.name.text == "Face", "box 2 is Face")
check(CharacterCustomizationButtonFrame2.parent == WrathppAppearanceBox2, "the client's own row (its arrows) is inside the box")
check(not CharacterCustomizationButtonFrame2Text.shown, "  its own label hidden")
check(WrathppAppearanceBox2.value.text == "-", "without the native mod: no number")

function WrathPP_GetCustomization(i) return i + 1, 9 end
CharacterCustomization_Right(2)
check(cycled[1] == 2, "the arrows still do what they did")
check(WrathppAppearanceBox2.value.text == "3 of 9", "with it: 3 of 9")
WrathppAppearance.OnUpdate(WrathppAppearance, 0.3)
check(WrathppAppearanceBox5.value.text == "6 of 9", "the column refreshes itself")
print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
