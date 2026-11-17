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
for i = 1, 20 do
	local name = i <= 10 and "CharacterCreateRaceButton"..i or "AlliedRaceButton"..i
	frame(name, config)
	frame(name.."NormalTexture"); frame(name.."PushedTexture"); frame(name.."Text"); frame(name.."Shadow")
end
CharacterCreate = { numRaces = 20 }
MAX_RACES = 10
local tokens = { "Human", "Dwarf", "NightElf", "Gnome", "Draenei", "Orc", "Scourge", "Tauren", "Troll", "BloodElf",
	"VoidElf", "LightforgedDraenei", "DarkIronDwarf", "Mechagnome", "HighElf", "Nightborne", "ZandalariTroll", "HighmountainTauren", "Vulpera", "MagharOrc" }
local alliance = { Human = 1, Dwarf = 1, NightElf = 1, Gnome = 1, Draenei = 1, VoidElf = 1, LightforgedDraenei = 1, DarkIronDwarf = 1, Mechagnome = 1, HighElf = 1 }
function GetFactionForRace(i) return nil, alliance[tokens[i]] and "Alliance" or "Horde" end
local seen
function CharacterCreateEnumerateRaces(...) seen = { ... } end
local background
function SetBackgroundModel(model, name) background = name end
GlueAmbienceTracks = { CHARACTERSELECT = "select", DRAENEI = "draenei" }
local played
function PlayGlueAmbience(sound, fade) if sound == nil then error("Usage: PlayGlueAmbience(\"sound name\", \"(optional)fade in time\")") end played = sound end
-- the screen's own table of its race icons' places (the game's ten; stock CharacterCreate.lua)
RACE_ICON_TCOORDS = {}
for i, t in ipairs({ "HUMAN", "DWARF", "NIGHTELF", "GNOME", "DRAENEI", "ORC", "SCOURGE", "TAUREN", "TROLL", "BLOODELF" }) do
	RACE_ICON_TCOORDS[t.."_MALE"] = { i / 10, i / 10 + 0.1, 0, 0.25 }; RACE_ICON_TCOORDS[t.."_FEMALE"] = { i / 10, i / 10 + 0.1, 0.25, 0.5 }
end

dofile(script)

check(MAX_RACES == 20, "the screen counts 20 races")
do
	local missing = {}
	for _, name in ipairs(tokens) do
		for _, sex in ipairs({ "MALE", "FEMALE" }) do if not rawget(RACE_ICON_TCOORDS, strupper(name).."_"..sex) then missing[#missing + 1] = name.."_"..sex end end
	end
	check(#missing == 0, "every race's icon has its place on the sheet, as the screen's own code looks it up by file string and sex"..(#missing > 0 and (": "..table.concat(missing, ", ")) or ""))
	check(RACE_ICON_TCOORDS.VOIDELF_MALE[1] == RACE_ICON_TCOORDS.BLOODELF_MALE[1], "  an allied race takes its start race's place for the big icon")
end
check(RACE_ICON_TCOORDS.MURLOC_MALE and RACE_ICON_TCOORDS.MURLOC_MALE[2] == 1, "a race the script doesn't know (another patch's tables) gets the whole picture, not nil: the screen's loop over the races doesn't stop")
check(pcall(PlayGlueAmbience, nil, 4) and played == "select", "a race with no music track gets the selection screen's, not the game's usage error")
check(pcall(PlayGlueAmbience, "draenei", 4) and played == "draenei", "  and a race with one keeps it")
check(CharacterCreateRaceButton11 == AlliedRaceButton11 and CharacterCreateRaceButton20 == AlliedRaceButton20, "the xml's buttons have the names the screen looks for")
check(CharacterCreateRaceButton11NormalTexture == AlliedRaceButton11NormalTexture, "  with their pictures")
check(CharacterCreateRaceButton11.parent == config, "  and the screen's frame as parent")

local args = {}
for i, t in ipairs(tokens) do args[#args + 1] = t; args[#args + 1] = t; args[#args + 1] = true end
-- (the screen's enumerate returns name, file string, enabled for each race)
for i, t in ipairs(tokens) do args[i * 3 - 1] = t end
CharacterCreateEnumerateRaces(unpack(args))
check(seen ~= nil, "the screen's own layout still runs")
local x = function(i) return CharacterCreateRaceButton20.points[1] and CharacterCreateRaceButton20.points[1][4] end
local left, right = 0, 0
for i = 1, 20 do
	local p = _G["CharacterCreateRaceButton"..i].points[1]
	if alliance[tokens[i]] then if p[4] < 0 then left = left + 1 end else if p[4] > 0 then right = right + 1 end end
end
check(left == 10 and right == 10, "the Alliance's ten on the left, the Horde's ten on the right")
check(CharacterCreateRaceButton20.points[1][5] > -400 and CharacterCreateRaceButton11.points[1][5] <= -50, "the rows fit above the gender buttons")
check(CharacterCreateRaceButton20NormalTexture.texture == "Interface\\Glues\\CharacterCreate\\WrathppRaces\\MAGHARORC", "Mag'har's picture is on its button")
check(CharacterCreateRaceButton15NormalTexture.texture == "Interface\\Glues\\CharacterCreate\\WrathppRaces\\HIGHELF", "the High Elf's too")
check(rawget(CharacterCreateRaceButton1NormalTexture, "texture") == nil, "the game's own ten keep the screen's atlas")
SetBackgroundModel("m", "MagharOrc"); check(background == "Orc", "Mag'har's scene is the Orcs'")
SetBackgroundModel("m", "HighElf"); check(background == "BloodElf", "the High Elf's the Blood Elves'")
SetBackgroundModel("m", "Human"); check(background == "Human", "a game race's own")
check(GlueAmbienceTracks.MAGHARORC == "GlueScreenIntro" or GlueAmbienceTracks.MAGHARORC ~= nil, "their selection music")
check(RACE_INFO_MAGHARORC and ABILITY_INFO_MAGHARORC1 and ABILITY_INFO_HIGHELF3 and MAGHARORC_DISABLED, "their texts")
print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
