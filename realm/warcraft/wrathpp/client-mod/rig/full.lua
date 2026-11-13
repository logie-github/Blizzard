-- Wrath++'s creator used as a person uses it, on the rig, for every race, sex and class:
--   luajit full.lua RIG_DIR CREATOR LOOKS UNDEAD|- [quick]
-- opens the screen, taps every race, both sexes and every class that can be tapped, Customize, every category, every row's
-- arrows and every choice of its list, Randomize, Gear, Undead, Back, Finish, and closes and opens the screen again.
-- After each tap: no error, no crash, the creator still on, the row showing what was chosen, the other rows as they were.
-- At the end: every texture file the creator named is one the 3.3.5 client is known to have.
local dir, creator, looks, undead, quick = arg[1], arg[2], arg[3], arg[4], arg[5] == "quick"
local work = os.getenv("RIG_WORK") or dir
local data = os.getenv("RIG_DATA") or (work.."/data")
local T = dofile(data.."/tables.lua")
local fails, checks, taps = {}, 0, 0
local where = ""
local function fail(what) if #fails < 60 then fails[#fails + 1] = where..": "..what end; fails.n = (fails.n or 0) + 1 end
local function make(first, opts)
	opts = opts or {}
	local native = nil
	if os.getenv("RIG_NATIVE") == "0" then native = false end
	local R = dofile(dir.."/rig.lua")({ dir = dir, stock = work.."/stock", data = data, creator = creator, looks = looks, undead = undead ~= "-" and undead or nil,
		native = native,
		screen = os.getenv("RIG_W") and { w = tonumber(os.getenv("RIG_W")), h = tonumber(os.getenv("RIG_H") or "768") } or nil })
	R.G.forceFirst = first
	return R
end
local function ok(R, what)
	checks = checks + 1
	local p = R.problems()
	if #p > 0 then fail(what..": "..p[1]:sub(1, 220)); return false end
	return true
end
local function tap(R, f, what, list)
	taps = taps + 1
	local good, err = pcall(R.tap, f, list)
	if not good then fail((what or tostring(type(f) == "string" and f or f.__name))..": "..tostring(err):sub(1, 200)); return false end
	R.frames(0.06)
	return ok(R, "after "..(what or tostring(type(f) == "string" and f or f.__name)))
end
-- No two of the creator's buttons on the screen lie over one another (each taken a little in from its edges: Shadowlands'
-- own round buttons overlap by their rings, and their middles are what is tapped). A row of classes run into the foot's
-- buttons on a screen narrower than Shadowlands' is the kind of fault this finds.
local function apart(R, when)
	local boxes = {}
	for _, f in ipairs(R.E.frames) do
		local name = f.__name
		if name and name:match("^Wrathpp") and (f.__kind == "Button" or f.__kind == "CheckButton") and f:IsVisible() and f.__scripts and f.__scripts.OnClick
				and name ~= "WrathppSpinArea" and name ~= "WrathppPopoutCatcher" and not R.E.clipped(f) then
			local l, b, w, h = R.E.rect(f)
			if l and w > 0 and h > 0 then boxes[#boxes + 1] = { name = name, l = l + w * 0.12, r = l + w * 0.88, b = b + h * 0.12, t = b + h * 0.88 } end
		end
	end
	for i = 1, #boxes do
		for j = i + 1, #boxes do
			local a, c = boxes[i], boxes[j]
			if a.l < c.r and c.l < a.r and a.b < c.t and c.b < a.t then fail(when..": "..a.name.." and "..c.name.." lie over one another") end
		end
	end
	checks = checks + 1
end
-- every list on the screen shows what is on (a row with no current choice is a number the creator could not read back)
local function current(R, when)
	for _, f in ipairs(R.rows()) do
		if f.row.kind == "list" and not f.row.at then fail(when..": "..f.row.name.." shows no choice as the one that is on") end
	end
end
local function state(R)
	local out = {}
	for _, f in ipairs(R.rows()) do out[f.row.name] = f.row.kind == "switch" and tostring(f.check:GetChecked() and true or false) or tostring(f.row.at) end
	return out
end
-- one character's Customize screen, all of it
local function customize(R, deep)
	local W = WrathppCreator
	local k = 1
	while _G["WrathppCategory"..k] and R.visible("WrathppCategory"..k) do
		if not tap(R, "WrathppCategory"..k, "category "..k) then return end
		current(R, "category "..k)
		for _, name in ipairs((function() local n = {}; for _, f in ipairs(R.rows()) do n[#n + 1] = f.row.name end; return n end)()) do
			local f = R.row(name)
			if f and f.row.kind == "list" and #f.row.choices > 1 then
				local before = state(R)
				local at = f.row.at
				if not tap(R, f.next, name.." next", WrathppOptionList) then return end
				f = R.row(name)
				if not f then fail(name.." went from the screen after next") return end
				local n = #f.row.choices
				if at and f.row.at ~= (at % n) + 1 then fail(name.." next: on "..tostring(f.row.at).." after "..tostring(at).." of "..n) end
				local now = state(R)
				for other, v in pairs(before) do if other ~= name and now[other] ~= nil and now[other] ~= v then fail(name.." next moved "..other.." from "..v.." to "..tostring(now[other])) end end
				if not tap(R, f.previous, name.." previous", WrathppOptionList) then return end
				f = R.row(name)
				if at and f and f.row.at ~= at then fail(name.." previous: on "..tostring(f.row.at).." and not back on "..tostring(at)) end
				-- its list: every choice (a few of them when quick)
				if not tap(R, f.choice, name.." list", WrathppOptionList) then return end
				if not R.visible("WrathppPopout") then fail(name..": its list did not open")
				else
					local step = (deep and 1) or math.max(1, math.floor(n / 4))
					for c = 1, n, step do
						if not R.visible("WrathppPopout") then
							-- the list closes when a choice is taken: opened again for the next
							f = R.row(name)
							if not f or not tap(R, f.choice, name.." list again", WrathppOptionList) then return end
						end
						local cell = _G["WrathppChoice"..c]
						if cell and cell:IsVisible() then
							local b2 = state(R)
							if not tap(R, cell, name.." choice "..c, WrathppPopoutList) then return end
							f = R.row(name)
							if not f then fail(name.." went from the screen after choice "..c) return end
							if f.row.at ~= c then fail(name..": choice "..c.." of "..n.." tapped, the row shows "..tostring(f.row.at)) end
							local n2 = state(R)
							for other, v in pairs(b2) do if other ~= name and n2[other] ~= nil and n2[other] ~= v then fail(name.." choice "..c.." moved "..other.." from "..v.." to "..tostring(n2[other])) end end
						else fail(name..": choice "..c.." of "..n.." is not in its list on the screen") end
					end
					if R.visible("WrathppPopout") then WrathppCreate_ClosePopout() end
				end
			elseif f and f.row.kind == "switch" then
				local on = f.check:GetChecked()
				if not tap(R, f.check, name.." switch", WrathppOptionList) then return end
				f = R.row(name)
				if f and (f.check:GetChecked() and true or false) == (on and true or false) then fail(name..": the switch did not change") end
				if f then if not tap(R, f.check, name.." switch back", WrathppOptionList) then return end end
			end
		end
		k = k + 1
	end
	if k == 1 then
		-- no categories: the game's own five
		for _, f in ipairs(R.rows()) do
			if f.row.kind == "list" or f.row.kind == "plain" then
				if not tap(R, f.next, f.row.name.." next", WrathppOptionList) then return end
				if not tap(R, f.previous, f.row.name.." previous", WrathppOptionList) then return end
			end
		end
	end
end

local started = os.clock()
local done = {}
local named = {}           -- every texture file a script named, and the line that named it
local shaded = {}          -- where a Wrath++ script put a pixel shader on a texture (SetDesaturated)
for _, pair in ipairs(T.baseInfo) do
	for sex = 0, 1 do
		local race, class = pair[1], pair[2]
		local key = race.."_"..sex
		-- every class is opened and customized a little; the whole of a race and sex's options once (with its first class), and once as a death knight
		local deep = (not quick) and (not done[key] or (class == 6 and not done[key.."dk"]))
		where = ("race %d sex %d class %d"):format(race, sex, class)
		local R = make({ race = race, sex = sex, class = class })
		local good, err = pcall(function()
			R.open()
			if not ok(R, "opened") then return end
			if not R.visible("WrathppCustomizeButton") then fail("no Customize button on the screen") return end
			apart(R, "race and class")
			if not tap(R, "WrathppCustomizeButton", "Customize") then return end
			apart(R, "customize")
			customize(R, deep)
			if R.visible("WrathppRandomize") then for i = 1, 3 do if not tap(R, "WrathppRandomize", "Randomize") then return end; current(R, "Randomize "..i) end end
			if not tap(R, "WrathppBackButton", "Back") then return end
			if not R.visible("WrathppCustomizeButton") then fail("Back did not bring the first screen") return end
			if not tap(R, "WrathppCustomizeButton", "Customize again") then return end
			CharacterCreateNameEdit:SetText("Rigtest")
			if not tap(R, "WrathppFinishButton", "Finish") then return end
			local P, made = R.G.character, R.G.created
			if not made or made.name ~= "Rigtest" or made.race ~= P.race or made.skin ~= P.skin or made.face ~= P.face then fail("Finish did not create the character that is on the screen") end
			R.close(); R.open()
			ok(R, "closed and opened again")
		end)
		if not good then fail("the rig stopped: "..tostring(err):sub(1, 300)) end
		for file, by in pairs(R.E.files) do named[file] = named[file] or by end
		for by in pairs(R.E.shaded) do shaded[by] = true end
		if deep then done[key] = true; if class == 6 then done[key.."dk"] = true end end
	end
end
-- the textures Wrath++'s scripts named: each one a file the 3.3.5 client is known to have (the rig draws nothing: a file the
-- client does not have is a green square on the phone, and only its name shows it here)
local known = dofile(work.."/textures.lua")
local files = 0
where = "textures"
for file, by in pairs(named) do
	if by:match("^Wrathpp") then
		files = files + 1
		local name = file:gsub("/", "\\"):lower():gsub("%.blp$", ""):gsub("%.tga$", "")
		if not known[name] then fail(file.." ("..by.."): not a file the 3.3.5 client is known to have (textures335.txt)") end
	end
end
if files == 0 then fail("no texture named by the creator was seen: the check is not looking") end
for by in pairs(shaded) do
	if by:match("^Wrathpp") then fail(by..": SetDesaturated puts the game's pixel shader on a texture (the phone drew build 241's portraits through it as squares)") end
end
-- every file of Shadowlands' art at least 8 on a side: the client draws a smaller one as a green square
local artList = os.getenv("RIG_ART_LIST")
if artList and artList ~= "" then
	local small = 0
	for line in io.lines(artList) do
		local file, cw, ch = line:match("^[^\t]+\t([^\t]+)\t.* in (%d+) x (%d+)$")
		if file and (tonumber(cw) < 8 or tonumber(ch) < 8) then small = small + 1; if small <= 5 then fail(file..": "..cw.." x "..ch..", smaller than the client draws (8 x 8): a green square") end end
	end
end
-- with Shadowlands' art in and read, the creator draws with it; without, with 3.3.5's own and plain colours
local artUsed = 0
for file, by in pairs(named) do if by:match("^Wrathpp") and file:lower():find("interface\\wrathpp\\", 1, false) then artUsed = artUsed + 1 end end
local wantArt = (os.getenv("RIG_ATLAS") or "-") ~= "-" and os.getenv("RIG_ATLAS") ~= "" and os.getenv("RIG_ART") ~= "unreadable"
if wantArt and (artUsed < 40 or not (WrathppCreator and WrathppCreator.art)) then fail("Shadowlands' art is in and the creator drew "..artUsed.." of its pieces") end
if not wantArt and WrathppCreator and WrathppCreator.art then fail("the creator says it draws with Shadowlands' art, which is not readable here") end
print(("%d taps, %d checks, %d textures named (%d of Shadowlands' art), %.0f s; %d problems"):format(taps, checks, files, artUsed, os.clock() - started, fails.n or 0))
for _, f in ipairs(fails) do print("  "..f) end
os.exit((fails.n or 0) == 0 and 0 or 1)
