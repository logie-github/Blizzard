-- The creator turned off (WrathppCreate_Disable): the game's own screen must be whole again, every piece of the game's
-- where and as it is without the creator, none of the creator's left on it, and the game's own buttons working.
--   luajit off.lua RIG_DIR CREATOR LOOKS UNDEAD|-
local dir, creator, looks, undead = arg[1], arg[2], arg[3], arg[4]
local work = os.getenv("RIG_WORK") or dir
local data = os.getenv("RIG_DATA") or (work.."/data")
local fails = 0
local function check(cond, what) if not cond then fails = fails + 1; print("FAIL "..what) else print("ok   "..what) end end
local function make(with)
	local R = dofile(dir.."/rig.lua")({ dir = dir, stock = work.."/stock", data = data, creator = with and creator or nil, looks = with and looks or nil, undead = with and undead ~= "-" and undead or nil })
	R.G.forceFirst = { race = 1, sex = 1, class = 8 }
	return R
end
local function snapshot(R)
	local out = {}
	for _, f in ipairs(R.E.frames) do
		local name = f.__name
		if name and not name:match("^Wrathpp") and not f.__isScreen then
			local l, b, w, h = R.E.rect(f)
			out[name] = { visible = f:IsVisible() and true or false, l = l, b = b, w = w, h = h, parent = f.__parent and f.__parent.__name, checked = f.__checked, text = f.__text }
		end
	end
	return out
end
-- the game's own screen, by itself
local A = make(false)
A.open()
local plain = snapshot(A)
check(#A.problems() == 0, "the game's own screen opens by itself on the rig"..(A.problems()[1] and (": "..A.problems()[1]) or ""))
-- with the creator: used a little, then turned off
local B = make(true)
B.open()
B.tap("WrathppCustomizeButton"); B.frames(0.1)
local row = B.rows()[1]
B.tap(row.next); B.frames(0.1); B.tap(row.previous); B.frames(0.1)
B.tap("WrathppZoomIn"); B.frames(1)
check(#B.problems() == 0, "the creator in use before it is turned off"..(B.problems()[1] and (": "..B.problems()[1]) or ""))
WrathppCreate_Disable("the rig turned it off")
B.frames(0.2)
local now = snapshot(B)
local wrong, shown = {}, 0
for name, a in pairs(plain) do
	local b = now[name]
	if not b then wrong[#wrong + 1] = name.." is gone"
	elseif a.visible ~= b.visible then wrong[#wrong + 1] = name.." is "..(b.visible and "shown" or "hidden").." and was "..(a.visible and "shown" or "hidden")
	elseif a.visible and (math.abs((a.l or 0) - (b.l or 0)) > 0.5 or math.abs((a.b or 0) - (b.b or 0)) > 0.5 or math.abs((a.w or 0) - (b.w or 0)) > 0.5 or math.abs((a.h or 0) - (b.h or 0)) > 0.5) then
		wrong[#wrong + 1] = ("%s is at %d,%d %dx%d and was at %d,%d %dx%d"):format(name, b.l or -1, b.b or -1, b.w or -1, b.h or -1, a.l or -1, a.b or -1, a.w or -1, a.h or -1)
	elseif a.parent ~= b.parent then wrong[#wrong + 1] = name.." is "..tostring(b.parent).."'s and was "..tostring(a.parent).."'s"
	end
	if a.visible then shown = shown + 1 end
end
table.sort(wrong)
check(#wrong == 0, "every piece of the game's own screen is where and as it is without the creator ("..shown.." on the screen)"..(#wrong > 0 and (": "..#wrong.." differ") or ""))
for i = 1, math.min(#wrong, 25) do print("     "..wrong[i]) end
local left = {}
for _, f in ipairs(B.E.frames) do if f.__name and f.__name:match("^Wrathpp") and f:IsVisible() and f.__kind ~= "Frame" then left[#left + 1] = f.__name end end
for _, f in ipairs(B.E.frames) do if f.__name and f.__name:match("^Wrathpp") and f:IsVisible() and f.__kind == "Frame" and f.__name ~= "WrathppDriver" and (f.__backdrop or #f.__regions > 0) then left[#left + 1] = f.__name end end
check(#left == 0, "none of the creator's pieces is left on the screen"..(#left > 0 and (": "..table.concat(left, ", ")) or ""))
-- and the game's own screen works: its races, sexes, classes, arrows, name and Accept
local G = B.G
local ok, err = pcall(function()
	B.tap("CharacterCreateRaceButton6"); B.tap("CharacterCreateGenderButtonMale"); B.tap("CharacterCreateClassButton1")
	B.tap("CharacterCustomizationButtonFrame1RightButton"); B.tap("CharacterCustomizationButtonFrame3LeftButton"); B.tap("CharCreateRandomizeButton")
	CharacterCreateNameEdit:SetText("Offtest"); B.tap("CharCreateOkayButton")
end)
local errs = {}
for i = B.stockErrors + 1, #B.E.errors do errs[#errs + 1] = tostring(B.E.errors[i].message):match("^[^\n]*") end
check(ok and #errs == 0 and not G.crashed, "the game's own buttons work after it"..((not ok and (": "..tostring(err))) or (errs[1] and (": "..errs[1])) or ""))
check(G.created and G.created.name == "Offtest" and G.created.race == G.races[6] and G.created.sex == 0 and G.created.class == 1, "  and its Accept makes the character chosen on it (race "..tostring(G.created and G.created.race)..")")
print(fails == 0 and "all passed" or (fails.." failed"))
os.exit(fails == 0 and 0 or 1)
