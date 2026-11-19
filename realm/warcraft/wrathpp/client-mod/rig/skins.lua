-- The skins the creator offers once Ralia's mod is in (WrathppSkins, written by the app: WrathppSkins.kt), on the rig with a fake list:
--   luajit skins.lua RIG_DIR CREATOR LOOKS UNDEAD
-- Skin Color lists only the listed skins and the looks' `keep` ones (the Dark Ranger); the game's skin on the screen, after the start,
-- a race change and Randomize, is one of them; a model the list doesn't name, or one it would leave without a skin, is not filtered;
-- the game's own number of a choice is still its real position (nothing renumbered); the undead switch is as it was.
local dir, creator, looks, undead = arg[1], arg[2], arg[3], arg[4]
local work = os.getenv("RIG_WORK") or dir
local data = os.getenv("RIG_DATA") or (work.."/data")
local fails = 0
local function check(cond, what) if not cond then fails = fails + 1; print("FAIL "..what) else print("ok   "..what) end end
local POLICY
local function make(first)
	local R = dofile(dir.."/rig.lua")({ dir = dir, stock = work.."/stock", data = data, creator = creator, looks = looks, undead = undead ~= "-" and undead or nil, skins = POLICY })
	R.G.forceFirst = first
	return R
end
local function clean(R) local p = R.problems(); return #p == 0, p[1] and (": "..p[1]:sub(1, 200)) or "" end

local function skinOption(model)
	for _, o in ipairs(model.options) do
		if ( o.field == "skin" and o.part == #model.fields.skin ) then return o end
	end
end

-- the skin colour's digit on the screen: the game's skin number is the parts' mixed-radix number, the colour its last part
local function digit(R, model) return R.G.character.skin % model.fields.skin[#model.fields.skin] end

-- the skin row's choices on the screen (the category that holds it is looked for)
local function skinRow(R)
	if ( R.row("Skin Color") ) then return R.row("Skin Color").row end
	for k = 1, 8 do
		if ( R.visible("WrathppCategory"..k) ) then
			R.tap("WrathppCategory"..k); R.frames(0.1)
			local r = R.row("Skin Color")
			if ( r ) then return r.row end
		end
	end
end

local function start(race, sex)
	local R = make({ race = race, sex = sex, class = race == 10 and 2 or 1 })
	R.open(); R.tap("WrathppCustomizeButton"); R.frames(0.1)
	return R
end

local KEYS = { "1_0", "1_1", "2_1", "4_1", "6_0", "8_1", "10_0", "10_1" }
for _, key in ipairs(KEYS) do
	local race, sex = key:match("^(%d+)_(%d+)$"); race, sex = tonumber(race), tonumber(sex)
	POLICY = nil
	local R0 = start(race, sex)
	local model = WrathppLooks.models[key]
	local option = model and skinOption(model)
	if ( not option ) then
		check(false, key..": the looks have a Skin Color option")
	else
		-- every other skin of the looks listed (by position), as an app list would be
		local list, byV = {}, {}
		for _, c in ipairs(option.choices) do byV[#byV + 1] = c.v end
		table.sort(byV)
		for i, v in ipairs(byV) do if ( i % 2 == 1 ) then list[#list + 1] = v end end
		local want, keeps = {}, 0
		for _, v in ipairs(list) do want[v] = true end
		for _, c in ipairs(option.choices) do if ( c.keep ) then want[c.v] = true; keeps = keeps + 1 end end
		local n = 0; for _, c in ipairs(option.choices) do if ( want[c.v] and c.c ~= "dk" ) then n = n + 1 end end
		local r0 = skinRow(R0)
		local all = r0 and #r0.choices or 0
		check(all > n, key..": a list that offers fewer than the looks' "..all.." skins ("..n..")")
		POLICY = { [key] = list }
		local R = start(race, sex)
		local row = skinRow(R)
		local ok = row ~= nil
		for _, c in ipairs(row and row.choices or {}) do if ( not want[c.v] ) then ok = false end end
		check(ok and #row.choices == n, key..": Skin Color lists the "..n.." offered skins only (".. (row and #row.choices or "no row")..")"..select(2, clean(R)))
		check(want[digit(R, model)], key..": the skin the game starts on is an offered one ("..digit(R, model)..")")
		-- a choice keeps its real position: the row's choices are the looks' own entries
		local real = true
		for _, c in ipairs(row and row.choices or {}) do
			local found = false
			for _, o in ipairs(option.choices) do if ( o.v == c.v and o.n == c.n and o.s == c.s ) then found = true end end
			real = real and found
		end
		check(real, key..": each offered choice is the looks' own, its number its real position")
		local fine = true
		for _ = 1, 10 do
			R.tap("WrathppRandomize"); R.frames(0.1)
			if ( not want[digit(R, model)] ) then fine = false end
		end
		check(fine and select(1, clean(R)), key..": Randomize always lands on an offered skin"..select(2, clean(R)))
		-- the character's skin is one the list doesn't offer (the game's own random pick on a race change): moved onto the first offered
		local first = row and row.choices[1]
		for _, c in ipairs(option.choices) do
			if ( not want[c.v] ) then
				local parts = model.fields.skin
				R.G.character.skin = R.G.character.skin - digit(R, model) + c.v
				break
			end
		end
		R.tap("WrathppRandomize"); R.frames(0.1)
		check(want[digit(R, model)], key..": a skin not offered is never what stays on the screen")
		if ( keeps > 0 ) then
			local shown = {}
			for _, c in ipairs(row.choices) do if ( c.keep ) then shown[#shown + 1] = c.v end end
			check(#shown == keeps, key..": the looks' kept skin(s) (the Dark Ranger) are offered whatever the list says ("..#shown..")")
		end
		-- a list that names none of the model's skins, and no kept one, filters nothing; a model the list doesn't name, nothing
		local nokeep = keeps == 0
		POLICY = { [key] = {} }
		R = start(race, sex)
		row = skinRow(R)
		if ( nokeep ) then
			check(row and #row.choices == all, key..": a list with none of its skins filters nothing ("..(row and #row.choices or "no row")..")")
		else
			-- one offered skin is no choice: the row is not shown (as any option with one choice), the character wears the kept one
			local kept = {}
			for _, c in ipairs(option.choices) do if ( c.keep ) then kept[c.v] = true end end
			check(row == nil and kept[digit(R, model)], key..": a list with none of its skins offers the kept one alone, and the character wears it ("..digit(R, model)..")")
		end
		POLICY = { ["99_9"] = { 1 } }
		R = start(race, sex)
		row = skinRow(R)
		check(row and #row.choices == all, key..": a model the list doesn't name keeps all its "..all.." skins")
	end
end

-- no list at all: all skins
POLICY = nil
do
	local R = start(1, 0)
	local row = skinRow(R)
	local n = 0; for _, c in ipairs(skinOption(WrathppLooks.models["1_0"]).choices) do if ( c.c ~= "dk" ) then n = n + 1 end end
	check(row and #row.choices == n and select(1, clean(R)), "no WrathppSkins: all skins, nothing filtered"..select(2, clean(R)))
end

-- the Undead switch is as it was with a list in
if ( undead ~= "-" ) then
	POLICY = { ["4_1"] = { 0 } }
	local R = make({ race = 4, sex = 1, class = 1 })
	R.open(); R.tap("WrathppCustomizeButton"); R.frames(0.1)
	local found
	for k = 1, 6 do
		if ( R.visible("WrathppCategory"..k) ) then R.tap("WrathppCategory"..k); R.frames(0.1); if ( R.row("Undead") ) then found = true; break end end
	end
	if ( found ) then
		R.tap(R.row("Undead").check, WrathppOptionList); R.frames(0.1)
		local skins
		for k = 1, 6 do
			if ( R.visible("WrathppCategory"..k) ) then R.tap("WrathppCategory"..k); R.frames(0.1); if ( R.row("Skin Color") ) then skins = #R.row("Skin Color").row.choices end end
		end
		check(skins == #WrathppUndead.models["4_1"].skins and R.G.character.skin >= WrathppUndead.models["4_1"].first, "Undead on: Skin Color lists the undead skins alone, as with no list ("..tostring(skins)..")")
	else
		check(false, "the Undead switch is there")
	end
end

print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
