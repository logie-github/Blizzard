-- Wrath++'s creator script (app/src/main/assets/wrathpp/WrathppCreate.lua) on a stand-in for the 3.3.5 creation screen's
-- frames and functions: Shadowlands' two screens, the option rows of a race unpacked from the game's five numbers and
-- packed back, the list of an option's choices, the lists under a finger, the character turned and brought nearer, the
-- Undead switch, and the game's own screen when something is missing or fails.
--   luajit test_creator.lua WrathppCreate.lua
local script = arg[1]
local fails = 0
local function check(cond, what) print((cond and "ok   " or "FAIL ")..what); if not cond then fails = fails + 1 end end

local here = arg[0]:match("^(.*)[/\\][^/\\]*$") or "."
local mock = dofile(here.."/mock_glue.lua")
local game, state, counts = mock.game, mock.state, mock.counts

-- The looks of a human woman (race 1, sex 1), small: three skins, three faces x two eye colours, four hair styles, three
-- hair colours, necklace (3) x piercings (2) on the feature number; an option nothing draws; a death knight's skin.
WrathppLooks = { build = "test", models = { ["1_1"] = {
	name = "HumanFemale", race = 1, sex = 1,
	fields = { skin = { 3 }, face = { 3, 2 }, hair = { 4 }, haircolor = { 3 }, feature = { 3, 2 } },
	categories = { { id = 2, name = "Face", order = 1, zoom = 100 }, { id = 3, name = "Accessories", order = 3, zoom = 100 }, { id = 1, name = "Body", order = 4, zoom = 20 } },
	options = {
		{ name = "Face", category = 2, type = 0, field = "face", part = 1, choices = { { v = 0, n = "" }, { v = 1, n = "" }, { v = 2, n = "" } } },
		{ name = "Skin Color", category = 2, type = 0, field = "skin", part = 1,
			choices = { { v = 1, n = "", s = 0xddbb99 }, { v = 0, n = "", s = 0xeeccaa }, { v = 2, n = "", s = 0x8899aa, c = "dk" } } },
		{ name = "Hair Style", category = 2, type = 0, field = "hair", part = 1,
			choices = { { v = 0, n = "Bald" }, { v = 1, n = "Bun" }, { v = 2, n = "Braid" }, { v = 3, n = "Long" } } },
		{ name = "Hair Color", category = 2, type = 0, field = "haircolor", part = 1, choices = { { v = 0, n = "", s = 0x111111 }, { v = 1, n = "", s = 0x884422 }, { v = 2, n = "", s = 0xffee99 } } },
		{ name = "Eyebrows", category = 3, type = 0, choices = { { v = 0, n = "Thin" }, { v = 1, n = "Thick" } } },
		{ name = "Eye Color", category = 3, type = 0, field = "face", part = 2, choices = { { v = 0, n = "", s = 0x3366ff }, { v = 1, n = "", s = 0x33aa55 } } },
		{ name = "Necklace", category = 3, type = 0, field = "feature", part = 1, choices = { { v = 0, n = "None" }, { v = 1, n = "Pearls" }, { v = 2, n = "Chain" } } },
		{ name = "Piercings", category = 3, type = 0, field = "feature", part = 2, choices = { { v = 0, n = "None" }, { v = 1, n = "Studs" } } },
	},
} } }

local function show() CharacterCreate_OnShow() end
local function tick(seconds, frames)
	for _ = 1, frames or 1 do WrathppDriver.scripts.OnUpdate(WrathppDriver, seconds / (frames or 1)) end
end
local function rowNamed(name)
	for k = 1, 20 do
		local f = _G["WrathppRow"..k]
		if f and f.shown and f.row and f.row.name == name then return f end
	end
end
local function rowNames()
	local out = {}
	for k = 1, 20 do
		local f = _G["WrathppRow"..k]
		if f and f.shown and f.row then out[#out + 1] = f.row.name end
	end
	return table.concat(out, ", ")
end

dofile(script)
local W = WrathppCreator
check(not W.off, "the script loads on the game's screen"..(W.error and (": "..tostring(W.error)) or ""))
check(not WrathppAlliancePanel.shown and CharacterCreateConfigurationFrame.shown, "nothing is moved before the creator opens")

-- Race and class -------------------------------------------------------------------------------------------------------
show()
check(WrathppAlliancePanel.shown and WrathppHordePanel.shown and WrathppClassPanel.shown and not WrathppOptionPanel.shown, "opened: the two sides' races and the classes, no options")
check(CharacterCreateRaceButton1.parent == WrathppAlliancePanel and CharacterCreateRaceButton5.parent == WrathppAlliancePanel, "  the Alliance's races on the left (Human ... Draenei)")
check(CharacterCreateRaceButton6.parent == WrathppHordePanel and CharacterCreateRaceButton10.parent == WrathppHordePanel, "  the Horde's on the right (Orc ... Blood Elf)")
check(CharacterCreateClassButton3.parent == WrathppClassPanel and CharacterCreateGenderButtonFemale.parent == WrathppSexPanel, "  the game's class and sex buttons in their panels")
check(not CharacterCreateConfigurationFrame.shown and not CharacterCustomizationButtonFrame1.shown and not CharCreateOkayButton.shown, "  the game's own panel, rows and Accept put away")
check(WrathppCustomizeButton.shown and not WrathppFinishButton.shown and CharacterCreateNameEdit.shown, "  Customize, the name; no Finish yet")

-- Customize, without the native mod ---------------------------------------------------------------------------------------
WrathppCustomizeButton:Click()
check(WrathppOptionPanel.shown and not WrathppAlliancePanel.shown and WrathppFinishButton.shown and WrathppBackButton.shown, "Customize: the options, Back, Finish; the races put away")
check(rowNames() == "Skin Color, Face, Hair Style, Hair Color, Facial Hair", "without the native mod: the game's own five ("..rowNames()..")")
local before = state[2]
rowNamed("Face").next:Click()
check(state[2] == before + 1, "  and their arrows step the game's own")
state[2] = 0

-- With it: Shadowlands' rows ----------------------------------------------------------------------------------------------
function WrathPP_GetCustomization(i) return state[i] + 1, counts[i] end
WrathppCreate_Refresh()
check(WrathppCategory1.shown and WrathppCategory1.label.text == "Face" and WrathppCategory2.label.text == "Accessories" and WrathppCategory3.label.text == "Body", "the race's categories in Shadowlands' order")
check(rowNames() == "Face, Skin Color, Hair Style, Hair Color", "Face's options in Shadowlands' order ("..rowNames()..")")
state[1] = 0; WrathppCreate_Refresh()
local skin = rowNamed("Skin Color")
check(#skin.row.choices == 2 and skin.row.at == 2, "a warrior's skins: two (the death knight's left out), the game's skin 0 the second shown")
check(skin.choice.number.text == 2 and skin.choice.swatch.texture and math.abs(skin.choice.swatch.texture[1] - 0xee / 255) < 0.001, "  its number and colour swatch on the row")
game.class = "DEATHKNIGHT"; WrathppCreate_Refresh()
check(#rowNamed("Skin Color").row.choices == 3, "a death knight's: three")
game.class = "WARRIOR"; WrathppCreate_Refresh()

-- one number, two options: the face number is face x eye colour
state[2] = 2 * 2 + 1; WrathppCreate_Refresh()
check(rowNamed("Face").row.at == 3, "face number 5 of (3 faces x 2 eyes): the Face row says face 3")
WrathppCategory2:Click()
check(rowNames() == "Eyebrows, Eye Color, Necklace, Piercings", "Accessories' options ("..rowNames()..")")
check(rowNamed("Eye Color").row.at == 2, "  and the Eye Color row says eye 2")
check(rowNamed("Eyebrows").row.kind == "later" and rowNamed("Eyebrows").alpha < 1 and not rowNamed("Eyebrows").choice.enabled, "an option nothing draws yet is listed, greyed, and can't be chosen from")

-- choosing: by the arrows, and from the list
game.cycles = 0
rowNamed("Eye Color").previous:Click()
check(state[2] == 2 * 2 + 0, "Eye Color's previous: eye 1, the face kept (number 4)")
state[5] = 0; WrathppCreate_Refresh()
rowNamed("Necklace").choice:Click()
check(WrathppPopout.shown and WrathppChoice3.shown and WrathppChoice3.label.text == "Chain" and not (WrathppChoice4 and WrathppChoice4.shown), "tapping the choice opens the list of them all (None, Pearls, Chain)")
game.cycles = 0
WrathppChoice3:Click()
check(state[5] == 2 * 2 + 0 and game.cycles == 2, "Chain: the feature number 4 (necklace 3 x piercings 1), by the game's steps the shorter way round (2)")
check(WrathppChoice3.border[2] == 0.82 and rowNamed("Necklace").choice.label.text == "Chain", "  the list and the row show it on")
rowNamed("Piercings").next:Click()
check(state[5] == 2 * 2 + 1, "Piercings' next: studs, the necklace kept (number 5)")
WrathppPopoutCatcher:Click()
check(not WrathppPopout.shown, "a tap elsewhere closes the list")

-- the native mod's set: one move
function WrathPP_SetCustomization(i, value) game.sets = game.sets + 1; state[i] = value - 1 end
WrathppCategory1:Click()
state[3] = 0; WrathppCreate_Refresh()
game.cycles, game.sets = 0, 0
rowNamed("Hair Style").choice:Click(); WrathppChoice4:Click()
check(state[3] == 3 and game.sets == 1 and game.cycles == 1, "with the native mod's set: the one before put in, then the game's own next (Long)")
WrathppCreate_ClosePopout()
rowNamed("Hair Style").next:Click()
check(state[3] == 0, "the arrows go round the ends")

-- Undead -----------------------------------------------------------------------------------------------------------------
WrathppCategory2:Click()
check(not rowNamed("Undead"), "no Undead switch without the imported skins")
WrathppUndead = { models = { ["1_1"] = { first = 3, skins = { { n = "Grave Blue", s = 0x7788aa }, { n = "Ash", s = 0x999999 }, { n = "Bog Green", s = 0x778866 }, { n = "Dusk", s = 0x886699 } } } } }
state[1] = 1; WrathppCreate_Refresh()
local undead = rowNamed("Undead")
check(undead and undead.row.kind == "switch" and not undead.check.checked, "with them: an Undead switch under Accessories, off on a living skin")
undead.check:SetChecked(true); undead.check:Click()
check(state[1] == 3 and rowNamed("Undead").check.checked, "on: the first undead skin (the colour after the race's own)")
WrathppCategory1:Click()
check(rowNames() == "Skin Color, Hair Style, Hair Color", "undead: no Face row (an undead skin has its own face) ("..rowNames()..")")
skin = rowNamed("Skin Color")
check(#skin.row.choices == 4 and skin.row.choices[2].n == "Ash" and skin.row.at == 1, "  and Skin Color lists the undead skins alone")
skin.next:Click()
check(state[1] == 4, "  its next: the second undead skin")
game.random = { 1, 0, 0, 0, 0 }
WrathppRandomize:Click()
check(state[1] >= 3, "Randomize while undead keeps an undead skin (the game picked a living one)")
WrathppCategory2:Click()
undead = rowNamed("Undead"); undead.check:SetChecked(false); undead.check:Click()
check(state[1] == 1, "off: back to the living skin that was on")
game.random = { 5, 0, 0, 0, 0 }
WrathppRandomize:Click()
check(state[1] < 3, "Randomize while living never lands on an undead skin")

-- A list under a finger ------------------------------------------------------------------------------------------------------
local list = WrathppOptionList
list:SetView(100); WrathppCreate_Refresh()
check(list:Limit() == 5 * 58 - 100, "a list longer than its panel scrolls ("..list:Limit()..")")
game.cursor = { 500, 300 }
local row = rowNamed("Necklace")
row.choice.scripts.OnMouseDown(row.choice)
game.cursor = { 500, 360 }; tick(0.02)
check(list.offset == 60 and list.scroll == 60, "a finger dragged up 60 moves the list 60")
row.choice.scripts.OnMouseUp(row.choice); row.choice.scripts.OnClick(row.choice)
check(not WrathppPopout.shown, "  and the row it began on isn't tapped")
local at = list.offset
tick(0.5, 30)
check(list.offset > at and list.offset <= list:Limit(), "  after a flick it carries on, and stops by the end")
list.scripts.OnMouseWheel(list, 1); tick(0.01)
local mid = list.offset
tick(1, 60)
check(mid > list.target and list.offset == list.target, "the wheel eases it there rather than jumping")
list:SetView(500); WrathppCreate_Refresh()

-- Turning and zooming --------------------------------------------------------------------------------------------------------
game.facing, game.cursor = 0, { 400, 300 }
WrathppSpinArea.scripts.OnMouseDown(WrathppSpinArea)
game.cursor = { 500, 300 }; tick(0.02)
check(game.facing > 0, "a finger across the middle turns the character ("..game.facing..")")
WrathppSpinArea.scripts.OnMouseUp(WrathppSpinArea)
local turned = game.facing
tick(0.2, 10)
check(game.facing > turned, "  and it carries on a little after a flick")
tick(3, 60)
turned = game.facing
tick(0.2, 5)
check(game.facing == turned, "  then rests")
WrathppTurnRight.scripts.OnMouseDown(WrathppTurnRight); tick(0.1, 5); WrathppTurnRight.scripts.OnMouseUp(WrathppTurnRight)
check(game.facing > turned, "the turn button turns it while held")
WrathppSpinArea.scripts.OnMouseWheel(WrathppSpinArea, 1); tick(1, 60)
check(W.zoom > 1.15 and #CharacterCreate.points == 2, "the wheel (a pinch) brings the character nearer: the model frame grown round it")
for _ = 1, 6 do WrathppZoomOut:Click() end; tick(1, 60)
check(W.zoom == 1 and CharacterCreate.points[1][1] == "ALL", "zoom out: the whole screen again, no further ("..W.zoom..", "..tostring(CharacterCreate.points[1][1])..")")
WrathppCategory1:Click(); tick(1, 60)
check(W.zoom > 1.3, "Face's category brings the view in (Shadowlands' camera for it)")
WrathppCategory3:Click(); tick(1, 60)
check(W.zoom == 1, "  Body's takes it back out")

-- Finish, Back, another race ---------------------------------------------------------------------------------------------------
WrathppFinishButton:Click()
check(game.created, "Finish creates the character")
WrathppBackButton:Click()
check(WrathppAlliancePanel.shown and not WrathppOptionPanel.shown and W.zoomTarget == 1, "Back: the races again, the view out")
game.race = 6; SetCharacterRace(6)
WrathppCustomizeButton:Click()
check(rowNames() == "Skin Color, Face, Hair Style, Hair Color, Facial Hair" and rowNamed("Face").row.kind == "list", "a race the looks don't have: the game's five, each a numbered list")
game.cycles, game.sets, state[2] = 0, 0, 0
rowNamed("Face").choice:Click(); WrathppChoice5:Click()
check(state[2] == 4, "  and a number picked from it is set")
WrathppCreate_ClosePopout()

-- Something fails ---------------------------------------------------------------------------------------------------------------
game.fail = true
WrathppCreate_Refresh()
check(W.off and CharacterCreateConfigurationFrame.shown and CharacterCustomizationButtonFrame1.shown and not WrathppOptionPanel.shown, "an error here puts the game's own screen back")
print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
