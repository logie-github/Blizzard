-- Wrath++'s allied races glue file (app/src/main/assets/wrathpp/WrathppAlliedRaces.lua) on a mock of the 3.3.5 creation screen:
-- the buttons the xml makes taking the names the screen looks for, the races in each side's two columns, the new races' pictures
-- on their buttons whenever the races are laid out, their backgrounds, and their text.
local script = arg[1]
strupper = string.upper
local fails = 0
local function check(cond, what) print((cond and "ok   " or "FAIL ")..what); if not cond then fails = fails + 1 end end

local Frame = {}
Frame.__index = function(t, k) return Frame[k] or function() end end
local function frame(name, parent)
	local f = setmetatable({ name = name, parent = parent, points = {}, texture = nil }, Frame)
	if name then _G[name] = f end
	return f
end
function Frame:GetParent() return self.parent end
function Frame:SetParent(p) self.parent = p end
function Frame:ClearAllPoints() self.points = {} end
function Frame:SetPoint(...) self.points[#self.points + 1] = { ... } end
function Frame:SetTexture(t) self.texture = t end
function Frame:SetTexCoord(a, b, c, d) self.coords = { a, b, c, d } end

local config = frame("CharacterCreateConfigurationFrame")
for i = 1, 21 do
	local name = i <= 10 and "CharacterCreateRaceButton"..i or "AlliedRaceButton"..i
	frame(name, config)
	frame(name.."NormalTexture"); frame(name.."PushedTexture"); frame(name.."Text"); frame(name.."Shadow")
end
CharacterCreate = { numRaces = 21 }
MAX_RACES = 10
local tokens = { "Human", "Dwarf", "NightElf", "Gnome", "Draenei", "Orc", "Scourge", "Tauren", "Troll", "BloodElf",
	"VoidElf", "Lightforged", "KulTiran", "DarkIron", "Mechagnome", "HighElf", "Nightborne", "Zandalari", "Highmountain", "Vulpera", "Maghar" }
local alliance = { Human = 1, Dwarf = 1, NightElf = 1, Gnome = 1, Draenei = 1, VoidElf = 1, Lightforged = 1, KulTiran = 1, DarkIron = 1, Mechagnome = 1, HighElf = 1 }
function GetFactionForRace(i) return nil, alliance[tokens[i]] and "Alliance" or "Horde" end
local seen
function CharacterCreateEnumerateRaces(...) seen = { ... } end
local background
function SetBackgroundModel(model, name) background = name end
GlueAmbienceTracks = { CHARACTERSELECT = "select", DRAENEI = "draenei" }

dofile(script)

check(MAX_RACES == 21, "the screen counts 21 races")
check(CharacterCreateRaceButton11 == AlliedRaceButton11 and CharacterCreateRaceButton21 == AlliedRaceButton21, "the xml's buttons have the names the screen looks for")
check(CharacterCreateRaceButton11NormalTexture == AlliedRaceButton11NormalTexture, "  with their pictures")
check(CharacterCreateRaceButton11.parent == config, "  and the screen's frame as parent")

local args = {}
for i, t in ipairs(tokens) do args[#args + 1] = t; args[#args + 1] = t; args[#args + 1] = true end
-- (the screen's enumerate returns name, file string, enabled for each race)
for i, t in ipairs(tokens) do args[i * 3 - 1] = t end
CharacterCreateEnumerateRaces(unpack(args))
check(seen ~= nil, "the screen's own layout still runs")
local x = function(i) return CharacterCreateRaceButton21.points[1] and CharacterCreateRaceButton21.points[1][4] end
local left, right = 0, 0
for i = 1, 21 do
	local p = _G["CharacterCreateRaceButton"..i].points[1]
	if alliance[tokens[i]] then if p[4] < 0 then left = left + 1 end else if p[4] > 0 then right = right + 1 end end
end
check(left == 11 and right == 10, "the Alliance's eleven on the left, the Horde's ten on the right")
check(CharacterCreateRaceButton21.points[1][5] > -400 and CharacterCreateRaceButton11.points[1][5] <= -50, "the rows fit above the gender buttons")
check(CharacterCreateRaceButton21NormalTexture.texture == "Interface\\Glues\\CharacterCreate\\WrathppRaces\\MAGHAR", "Mag'har's picture is on its button")
check(CharacterCreateRaceButton16NormalTexture.texture == "Interface\\Glues\\CharacterCreate\\WrathppRaces\\HIGHELF", "the High Elf's too")
check(rawget(CharacterCreateRaceButton1NormalTexture, "texture") == nil, "the game's own ten keep the screen's atlas")
SetBackgroundModel("m", "Maghar"); check(background == "Orc", "Mag'har's scene is the Orcs'")
SetBackgroundModel("m", "KulTiran"); check(background == "Human", "the Kul Tirans' the Humans'")
SetBackgroundModel("m", "HighElf"); check(background == "BloodElf", "the High Elf's the Blood Elves'")
SetBackgroundModel("m", "Human"); check(background == "Human", "a game race's own")
check(GlueAmbienceTracks.MAGHAR == "GlueScreenIntro" or GlueAmbienceTracks.MAGHAR ~= nil, "their selection music")
check(RACE_INFO_MAGHAR and ABILITY_INFO_MAGHAR1 and ABILITY_INFO_HIGHELF3 and MAGHAR_DISABLED, "their texts")
print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
