-- What the creator does, on the rig, one thing at a time:  luajit behaviour.lua RIG_DIR CREATOR LOOKS UNDEAD
local dir, creator, looks, undead = arg[1], arg[2], arg[3], arg[4]
local work = os.getenv("RIG_WORK") or dir
local data = os.getenv("RIG_DATA") or (work.."/data")
local fails = 0
local function check(cond, what) if not cond then fails = fails + 1; print("FAIL "..what) else print("ok   "..what) end end
local function make(first, opts)
	opts = opts or {}
	local R = dofile(dir.."/rig.lua")({ dir = dir, stock = work.."/stock", data = data, creator = creator, looks = looks, undead = opts.undead ~= false and undead ~= "-" and undead or nil, native = opts.native, shots = opts.shots })
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
check(R.visible("WrathppAlliancePanel") and R.visible("WrathppHordePanel") and R.visible("WrathppClassPanel") and R.visible("WrathppSexPanel") and R.visible("WrathppCustomizeButton") and R.visible("WrathppLeaveButton") and not R.visible("CharCreateBackButton"),
	"race and class: the two sides' races, the sexes, the classes, Back and Customize")
check(not R.visible("CharacterCreateConfigurationFrame") and not R.visible("CharacterCreateWoWLogo") and not R.visible("CharacterCreateCharacterRace") and not R.visible("CharCreateOkayButton")
	and not R.visible("CharacterCreateNameEdit") and not R.visible("CharacterCustomizationButtonFrame1"), "  the game's own panel, its logo, its two texts, its Accept and the name put away")
check(not R.visible("CharacterCreateRaceButton1") and not R.visible("CharacterCreateClassButton3") and not R.visible("CharacterCreateGenderButtonFemale")
	and R.visible("WrathppRace1") and WrathppRace1.__parent == WrathppAllianceRaces and R.visible("WrathppRace6") and WrathppRace6.__parent == WrathppHordeRaces
	and R.visible("WrathppClass1") and R.visible("WrathppSexMale") and R.visible("WrathppSexFemale"),
	"  Shadowlands' round race, class and sex buttons on the screen, the game's own out of sight")
check(R.G.log[1] == "built" and R.G.log[2]:match("^opened: native 0.4.0, looks' options in") and R.G.log[3] == "screen: race and class", "  the log: built, opened, the first screen ("..table.concat(R.G.log, " | ")..")")
-- the game's own buttons, where the creator put them, do the game's own work
R.tap("WrathppRace7"); R.frames(0.1)
check(R.G.character.race == R.G.races[7] and select(1, clean(R)), "a race tapped is the game's race (race "..R.G.character.race..")"..select(2, clean(R)))
R.tap("WrathppSexMale"); R.frames(0.1)
check(R.G.character.sex == 0 and select(1, clean(R)), "a sex tapped is the game's sex"..select(2, clean(R)))
local before = R.G.selectedClassID
for i = 1, 10 do local b = _G["WrathppClass"..i]; if b and b:IsVisible() and not b.off and R.G.T.classes[i].id ~= before then R.tap(b); break end end
R.frames(0.1)
check(R.G.selectedClassID ~= before and select(1, clean(R)), "a class tapped is the game's class"..select(2, clean(R)))

-- Customize
R = make({ race = 4, sex = 1, class = 1 })
R.open(); R.tap("WrathppCustomizeButton"); R.frames(0.1)
check(R.visible("WrathppOptionPanel") and R.visible("WrathppCategory1") and R.visible("WrathppFinishButton") and R.visible("WrathppBackButton") and R.visible("CharacterCreateNameEdit")
	and not R.visible("WrathppAlliancePanel") and not R.visible("WrathppSexPanel") and not R.visible("WrathppLeaveButton") and not R.visible("WrathppRace1") and select(1, clean(R)),
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
		local function said(text) for _, f in ipairs(R.layout()) do if f.text and f.text:find(text, 1, true) then return true end end return false end
		R.frames(0.3)
		check(said("starts in Deathknell as one of the Forsaken"), "  and the screen says the character starts in Deathknell, one of the Forsaken, for the Horde")
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
		R.frames(0.3)
		check(not said("starts in Deathknell"), "  and says it no longer")
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
	R.tap("WrathppBackButton"); R.frames(0.1); R.tap("WrathppRace2"); R.frames(0.1); R.tap("WrathppCustomizeButton"); R.frames(0.1)
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
	check(list.offset > 0 and math.abs(list:GetVerticalScroll() - list.offset) <= R.E.screen.h / 1248, "a finger dragged up a list moves it ("..list.offset..")")
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

-- the app's touch told: the creator up, where a finger drags a list, and down when it closes
do
	local R = make({ race = 1, sex = 0, class = 1 })
	R.open(); R.frames(0.2)
	local first = R.G.screen
	check(first == "creator 1 drag", "the app is told the creator is up, nothing to drag on the first screen ("..tostring(first)..")")
	R.tap("WrathppCustomizeButton"); R.frames(0.2)
	local listed = R.G.screen and R.G.screen:match("^creator 1 drag (%d+) (%d+) (%d+) (%d+)$")
	local l, b, r, t = R.E.rect(WrathppOptionList)
	local W2, H2 = R.E.screen.w, R.E.screen.h
	local a1, a2, a3, a4 = (R.G.screen or ""):match("^creator 1 drag (%d+) (%d+) (%d+) (%d+)")
	check(a1 and math.abs(tonumber(a1) - l / W2 * 1000) <= 1 and math.abs(tonumber(a4) - (b + t) / H2 * 1000) <= 1 or (listed == nil and WrathppOptionList.content <= WrathppOptionList.view),
		"  on Customize, the option list's place where it scrolls ("..tostring(R.G.screen)..")")
	local f
	for _, row in ipairs(R.rows()) do if row.row.kind == "list" and not f then f = row end end
	R.tap(f.choice, WrathppOptionList); R.frames(0.1)
	local n = 0; for _ in (R.G.screen or ""):gmatch("%d+ %d+ %d+ %d+") do n = n + 1 end
	check(n >= 1 and R.visible("WrathppPopout"), "  a list of choices open: its place too ("..tostring(R.G.screen)..")")
	local count = R.G.screens
	R.frames(1)
	check(R.G.screens == count, "  said once, not every frame")
	R.close(); R.frames(0.1)
	check(R.G.screen == "creator 0", "  and told it is gone when the screen closes")
end

-- the option list under a finger, frame by frame at 30 a second (the game on the phone): with the finger one for one,
-- no jump as the drag begins, nothing read again meanwhile, a flick going on and slowing, on whole pixels
do
	local R = make({ race = 1, sex = 0, class = 1 })
	R.open(); R.tap("WrathppCustomizeButton"); R.frames(0.5)
	local list = WrathppOptionList
	-- the category with the most rows
	local best, most = nil, 0
	for k = 1, 6 do local b = _G["WrathppCategory"..k]; if b and b:IsVisible() then R.tap(b); R.frames(0.6); if #R.rows() > most then most, best = #R.rows(), b end end end
	R.tap(best); R.frames(1)
	local limit = list.content - list.view
	check(limit > 60, "  a list longer than its place to scroll ("..most.." rows, "..math.floor(limit).." units more than it shows)")
	local row = R.rows()[2]
	local _, rb, _, rh = R.E.rect(row)
	local dt = 1 / 30
	local function frame() R.E.update(dt, 1) end
	R.E.cursor = { 900, rb + rh / 2 }
	local down = row:GetScript("OnMouseDown"); down(row)
	local refreshes = WrathppCreator.refreshes or 0
	local duringDrag
	local steps, jump, follows = {}, 0, true
	local before = list.offset
	for i = 1, 8 do
		R.E.cursor[2] = R.E.cursor[2] + 7                -- the finger up 7 units a frame (210 a second)
		frame()
		local moved = list.offset - before; before = list.offset
		steps[#steps + 1] = moved
		if ( moved > 7.01 ) then jump = math.max(jump, moved) end
		if ( i > 2 and list.offset < limit and math.abs(moved - 7) > 0.01 ) then follows = false end
	end
	check(jump == 0 and follows, "  dragged: the list goes with the finger, unit for unit, and does not jump as the drag begins (steps "..string.format("%.1f %.1f %.1f %.1f", steps[1], steps[2], steps[3], steps[4])..")")
	duringDrag = (WrathppCreator.refreshes or 0) - refreshes
	local up = row:GetScript("OnMouseUp"); up(row)
	local flung, last, slowing, past, during = {}, list.offset, true, false, nil
	local busyReads = 0
	for i = 1, 60 do
		local had = WrathppCreator.refreshes or 0
		frame()
		if ( list:Busy() and (WrathppCreator.refreshes or 0) > had ) then busyReads = busyReads + 1 end
		local moved = list.offset - last; last = list.offset
		if ( #flung > 0 and moved > flung[#flung] + 0.001 ) then slowing = false end
		if ( list.offset > limit + 0.001 or list.offset < -0.001 ) then past = true end
		flung[#flung + 1] = moved
	end
	during = busyReads + ((duringDrag or 0))
	check(flung[1] > 3 and slowing and not past and flung[#flung] == 0, "  let go while moving: it goes on, slowing every frame, and stops, never past the end (first "..string.format("%.1f", flung[1])..", "..string.format("%.0f", list.offset - 56).." units on)")
	check(during == 0, "  the rows not read again while the list moved ("..tostring(during).." times)")
	R.frames(0.6)
	check((WrathppCreator.refreshes or 0) > refreshes, "  and read again once it rests")
	-- a finger that stops before it lifts throws nothing
	R.E.cursor = { 900, rb + rh / 2 }; down(row)
	for i = 1, 10 do R.E.cursor[2] = R.E.cursor[2] - 6; frame() end
	for i = 1, 4 do frame() end
	local at = list.offset; up(row); frame(); frame()
	check(math.abs(list.offset - at) < 0.001, "  stopped, then lifted: it stays where it is")
	-- where the content is set: whole pixels of the phone's 1248
	local px = R.E.screen.h / 1248
	local v = list.__vscroll or 0
	check(math.abs(v / px - math.floor(v / px + 0.5)) < 1e-6, "  placed on whole pixels of the screen ("..string.format("%.3f", v / px)..")")
end

-- pictures for the app's report: only when the app asks, one of each screen a moment after it is first up and one of
-- the first list opened, by the game's own Screenshot
local function shotsOf(R) local n = 0; for _, note in ipairs(R.notes) do if note == "screenshot" then n = n + 1 end end; return n end
local function said(R, what) for _, line in ipairs(R.G.log) do if line:find(what, 1, true) then return true end end return false end
R = make({ race = 1, sex = 0, class = 1 }, { shots = true })
R.open(); R.frames(0.5)
check(shotsOf(R) == 0, "pictures: none before the first screen has been up a moment")
R.frames(1.6)
check(shotsOf(R) == 1 and said(R, "shot 1: race and class"), "  one of the first screen, said in the log")
R.frames(3)
check(shotsOf(R) == 1, "  and no more of it")
R.tap("WrathppCustomizeButton"); R.frames(2)
check(shotsOf(R) == 2 and said(R, "shot 2: customize"), "  one of Customize")
local listed
for _, f in ipairs(R.rows()) do if f.row.kind == "list" and not listed then listed = f end end
R.tap(listed.choice, WrathppOptionList); R.frames(1)
check(shotsOf(R) == 3 and said(R, "shot 3: a list"), "  one of the first list opened")
WrathppCreate_ClosePopout(); R.tap("WrathppBackButton"); R.frames(2); R.tap("WrathppCustomizeButton"); R.frames(2)
check(shotsOf(R) == 3 and select(1, clean(R)), "  three at most"..select(2, clean(R)))
R = make({ race = 1, sex = 0, class = 1 })
R.open(); R.frames(2); R.tap("WrathppCustomizeButton"); R.frames(2)
check(shotsOf(R) == 0, "  none when the app has not asked")

print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
