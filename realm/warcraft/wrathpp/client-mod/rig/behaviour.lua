-- What the creator does, on the rig, one thing at a time:  luajit behaviour.lua RIG_DIR CREATOR LOOKS UNDEAD
local dir, creator, looks, undead = arg[1], arg[2], arg[3], arg[4]
local work = os.getenv("RIG_WORK") or dir
local data = os.getenv("RIG_DATA") or (work.."/data")
local fails = 0
local function check(cond, what) if not cond then fails = fails + 1; print("FAIL "..what) else print("ok   "..what) end end
local function make(first, opts)
	opts = opts or {}
	local R = dofile(dir.."/rig.lua")({ dir = dir, stock = work.."/stock", data = data, creator = creator, looks = looks, undead = opts.undead ~= false and undead ~= "-" and undead or nil, native = opts.native })
	R.G.forceFirst = first
	return R
end
local function clean(R) local p = R.problems(); return #p == 0, p[1] and (": "..p[1]:sub(1, 200)) or "" end

-- The screen shown: the client runs a frame's children's OnShow before its own, so the creator's own frame hears of it
-- before the game has made the character (the crash of builds 226 to 232, reports #102 and #104).
local R = make({ race = 1, sex = 1, class = 8 })
local good, err = pcall(R.open)
local ok, why = clean(R)
check(good and ok and not R.G.crashed, "the screen opens: nothing of the game's is asked before the game has its character"..(good and why or (": "..tostring(err):sub(1, 200))))
check(R.visible("WrathppAlliancePanel") and R.visible("WrathppHordePanel") and R.visible("WrathppClassPanel") and R.visible("WrathppSexPanel") and R.visible("WrathppCustomizeButton") and R.visible("CharCreateBackButton"),
	"race and class: the two sides' races, the sexes, the classes, Back and Customize")
check(not R.visible("CharacterCreateConfigurationFrame") and not R.visible("CharacterCreateWoWLogo") and not R.visible("CharacterCreateCharacterRace") and not R.visible("CharCreateOkayButton")
	and not R.visible("CharacterCreateNameEdit") and not R.visible("CharacterCustomizationButtonFrame1"), "  the game's own panel, its logo, its two texts, its Accept and the name put away")
check(CharacterCreateRaceButton1.__parent == WrathppAlliancePanel and CharacterCreateRaceButton6.__parent == WrathppHordePanel and CharacterCreateClassButton3.__parent == WrathppClassPanel
	and CharacterCreateGenderButtonFemale.__parent == WrathppSexPanel, "  the game's own race, class and sex buttons in the creator's panels")
check(R.G.log[1] == "built" and R.G.log[2]:match("^opened: native 0.3.0, looks' options in") and R.G.log[3] == "screen: race and class", "  the log: built, opened, the first screen ("..table.concat(R.G.log, " | ")..")")
-- the game's own buttons, where the creator put them, do the game's own work
R.tap("CharacterCreateRaceButton7"); R.frames(0.1)
check(R.G.character.race == R.G.races[7] and select(1, clean(R)), "a race tapped is the game's race (race "..R.G.character.race..")"..select(2, clean(R)))
R.tap("CharacterCreateGenderButtonMale"); R.frames(0.1)
check(R.G.character.sex == 0 and select(1, clean(R)), "a sex tapped is the game's sex"..select(2, clean(R)))
local before = R.G.selectedClassID
for i = 1, 10 do local b = _G["CharacterCreateClassButton"..i]; if b:IsVisible() and b.__enabled and R.G.T.classes[i].id ~= before then R.tap(b); break end end
R.frames(0.1)
check(R.G.selectedClassID ~= before and select(1, clean(R)), "a class tapped is the game's class"..select(2, clean(R)))

-- Customize
R = make({ race = 4, sex = 1, class = 1 })
R.open(); R.tap("WrathppCustomizeButton"); R.frames(0.1)
check(R.visible("WrathppOptionPanel") and R.visible("WrathppCategory1") and R.visible("WrathppFinishButton") and R.visible("WrathppBackButton") and R.visible("CharacterCreateNameEdit")
	and not R.visible("WrathppAlliancePanel") and not R.visible("WrathppSexPanel") and not R.visible("CharCreateBackButton") and select(1, clean(R)),
	"Customize: the categories, the options, the name, Back and Finish; the first screen's pieces away"..select(2, clean(R)))
local l1 = R.E.rect(WrathppCategory1); local l2 = R.E.rect(WrathppCategory2)
local _, nb = R.E.rect(CharacterCreateNameEdit); local vl, vb = R.E.rect(WrathppViewPanel)
check(l1 > R.E.screen.w / 2 and l2 > l1 and nb > R.E.screen.h * 0.8 and vl < 100 and vb > R.E.screen.h * 0.8,
	"  laid out as Shadowlands' screen: the categories top right, the name top middle, the view's buttons top left")
check(#R.rows() >= 4 and R.rows()[1].row.at ~= nil, "  the first category's options, each showing what is on")

-- the undead skins: a switch under Accessories; on, Skin Color lists the undead skins alone and Face goes
if undead ~= "-" then
	local found
	for k = 1, 6 do
		if R.visible("WrathppCategory"..k) then R.tap("WrathppCategory"..k); R.frames(0.1); if R.row("Undead") then found = k; break end end
	end
	check(found ~= nil, "the Undead switch is under one of the categories (Accessories)")
	if found then
		local living = R.G.character.skin
		R.tap(R.row("Undead").check, WrathppOptionList); R.frames(0.1)
		local first = WrathppUndead.models["4_1"].first
		check(R.G.character.skin >= first and select(1, clean(R)), "  on: the game's skin is an undead one ("..R.G.character.skin..", from "..first..")"..select(2, clean(R)))
		local skins, face
		for k = 1, 6 do
			if R.visible("WrathppCategory"..k) then
				R.tap("WrathppCategory"..k); R.frames(0.1)
				if R.row("Skin Color") then skins = #R.row("Skin Color").row.choices end
				if R.row("Face") then face = true end
			end
		end
		check(skins == #WrathppUndead.models["4_1"].skins and not face, "  Skin Color lists the undead skins alone ("..tostring(skins).."), and Face is gone (an undead skin has its own)")
		R.tap("WrathppRandomize"); R.frames(0.1)
		check(R.G.character.skin >= first, "  Randomize keeps an undead skin")
		R.tap("WrathppCategory"..found); R.frames(0.1); R.tap(R.row("Undead").check, WrathppOptionList); R.frames(0.1)
		check(R.G.character.skin < first and select(1, clean(R)), "  off: a living skin again ("..R.G.character.skin..")"..select(2, clean(R)))
		for _ = 1, 4 do R.tap("WrathppRandomize"); R.frames(0.1) end
		check(R.G.character.skin < first, "  Randomize while living never lands on an undead skin")
	end
end

-- Gear
local gear = R.row("Gear")
check(gear ~= nil and gear.check:GetChecked() == 1 and R.G.character.dressed, "Gear: a switch, last in the category, on; the character dressed")
if gear then
	R.tap(gear.check, WrathppOptionList); R.frames(0.1)
	check(R.G.character.dressed == false and select(1, clean(R)), "  off: the outfit is off the game's character"..select(2, clean(R)))
	R.tap("WrathppRandomize"); R.frames(0.1)
	check(R.G.character.dressed == false, "  and stays off through Randomize (the game dresses the character again there)")
	R.tap("WrathppBackButton"); R.frames(0.1); R.tap("CharacterCreateRaceButton2"); R.frames(0.1); R.tap("WrathppCustomizeButton"); R.frames(0.1)
	check(R.G.character.dressed == false and R.row("Gear") and R.row("Gear").check:GetChecked() == nil, "  and through another race")
	R.tap(R.row("Gear").check, WrathppOptionList); R.frames(0.1)
	check(R.G.character.dressed == true, "  on: dressed again")
	R.tap(R.row("Gear").check, WrathppOptionList); R.frames(0.1); R.close(); R.open()
	check(R.G.character.dressed == true and select(1, clean(R)), "  the screen opened again starts dressed"..select(2, clean(R)))
	R.tap("WrathppCustomizeButton"); R.frames(0.1)
end

-- the view
local facing = R.G.facing
WrathppTurnRight.__scripts.OnMouseDown(WrathppTurnRight); R.frames(0.3); WrathppTurnRight.__scripts.OnMouseUp(WrathppTurnRight)
check(R.G.facing > facing and select(1, clean(R)), "the turn button held turns the character"..select(2, clean(R)))
R.E.cursor = { 500, 400 }; WrathppSpinArea.__scripts.OnMouseDown(WrathppSpinArea); R.E.cursor = { 560, 400 }; R.frames(0.04); WrathppSpinArea.__scripts.OnMouseUp(WrathppSpinArea)
local turned = R.G.facing
R.frames(0.3)
check(turned ~= facing and R.G.facing ~= turned, "a finger across the middle turns it, and it carries on a little after")
R.tap("WrathppZoomIn"); R.frames(1)
local ml, mb, mw, mh = R.E.rect(CharacterCreate)
check(mw > R.E.screen.w * 1.2 and select(1, clean(R)), "nearer: the game's model frame grown round the character ("..math.floor(mw).." wide)"..select(2, clean(R)))
R.tap("WrathppResetView"); R.frames(1.5)
ml, mb, mw, mh = R.E.rect(CharacterCreate)
check(math.abs(mw - R.E.screen.w) < 1 and math.abs(ml) < 1, "the first of the view's buttons puts the view back")

-- a long list under a finger
local list = WrathppOptionList
R.tap("WrathppCategory1"); R.frames(0.1)
if list:Limit() > 0 then
	local row = R.rows()[2]
	R.E.cursor = { 900, 300 }; row.choice.__scripts.OnMouseDown(row.choice); R.E.cursor = { 900, 340 }; R.frames(0.04)
	check(list.offset > 0 and list:GetVerticalScroll() == list.offset, "a finger dragged up a list moves it ("..list.offset..")")
	row.choice.__scripts.OnMouseUp(row.choice); row.choice.__scripts.OnClick(row.choice)
	check(not R.visible("WrathppPopout"), "  and the row it began on isn't tapped")
else print("ok   (this category's options fit their place: no list to drag)") end

-- Finish
CharacterCreateNameEdit:SetText("Rigtest"); R.tap("WrathppFinishButton")
local P, made = R.G.character, R.G.created
check(made and made.name == "Rigtest" and made.race == P.race and made.sex == P.sex and made.skin == P.skin and made.face == P.face and made.hairStyle == P.hairStyle and made.hairColor == P.hairColor and made.facialHair == P.facialHair,
	"Finish creates the character that is on the screen")

-- a death knight: its own faces, skins and eye colours (Shadowlands'), and never without a face
R = make({ race = 4, sex = 1, class = 6 }, { undead = false })
R.open(); R.tap("WrathppCustomizeButton"); R.frames(0.1)
local face, skin = R.row("Face"), R.row("Skin Color")
check(select(1, clean(R)) and face and face.row.at and skin and skin.row.at, "a death knight: Customize opens, Face and Skin Color show what is on"..select(2, clean(R)))
local onlyMine = true
for _, f in ipairs({ face, skin }) do if f then for _, c in ipairs(f.row.choices) do if c.c == "nodk" then onlyMine = false end end end end
check(onlyMine, "  its lists have none of the choices that are not a death knight's")

-- without the native mod: the game's own five, by the game's own arrows
R = make({ race = 1, sex = 0, class = 1 }, { native = false })
R.open(); R.tap("WrathppCustomizeButton"); R.frames(0.1)
local names = {}
for _, f in ipairs(R.rows()) do names[#names + 1] = f.row.name end
local skin0 = R.G.character.skin
if R.rows()[1] then R.tap(R.rows()[1].next); R.frames(0.1) end
check(#names == 5 and R.G.character.skin ~= skin0 and select(1, clean(R)), "without the native mod: the game's own five ("..table.concat(names, ", ").."), stepped by the game"..select(2, clean(R)))

print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
