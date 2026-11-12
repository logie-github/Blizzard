-- The creator's script on the looks' real data (WrathppLooks.lua, made by tools/sl_creator.py with the looks package):
-- for every race and sex, every category shows its rows, and every choice of every option that is drawn can be put on
-- and reads back as the one on, with every other option left as it was. Run by wrathpp-looks.yml on what it makes.
--   luajit test_creator_data.lua WrathppLooks.lua WrathppCreate.lua
local data, script = arg[1], arg[2]
local here = arg[0]:match("^(.*)[/\\][^/\\]*$") or "."
local mock = dofile(here.."/mock_glue.lua")
local game, state, counts = mock.game, mock.state, mock.counts
local RACE = { Human = 1, Orc = 2, Dwarf = 3, NightElf = 4, Scourge = 5, Tauren = 6, Gnome = 7, Troll = 8, BloodElf = 10, Draenei = 11 }
dofile(data)
function WrathPP_GetCustomization(i) return state[i] + 1, counts[i] end
function WrathPP_SetCustomization(i, value) state[i] = value - 1 end
dofile(script)
local W = WrathppCreator
assert(not W.off, "the script doesn't load: "..tostring(W.error))
CharacterCreate_OnShow()
local fails, models, options, choices = 0, 0, 0, 0
local function fail(what) fails = fails + 1; if fails <= 20 then print("FAIL "..what) end end
local FIELD = { skin = 1, face = 2, hair = 3, haircolor = 4, feature = 5 }
for index, token in ipairs(mock.tokens) do
	for sex = 0, 1 do
		local model = WrathppLooks.models[RACE[token].."_"..sex]
		if model then
			models = models + 1
			game.race, game.sex = index, sex == 1 and 3 or 2
			for field, i in pairs(FIELD) do
				local n = 1
				for _, p in ipairs(model.fields[field]) do n = n * p end
				counts[i], state[i] = n, 0
			end
			WrathppCreate_SetStep(2)
			for _, category in ipairs(model.categories) do
				W.category = category.id
				for _, class in ipairs({ "WARRIOR", "DEATHKNIGHT" }) do
					game.class = class
					local rows = W.Rows()
					if #rows == 0 then fail(model.name.." "..category.name..": no rows") end
					for r, row in ipairs(rows) do
						if row.kind == "list" then
							options = options + 1
							for k = 1, #row.choices do
								local before = { unpack(state) }
								W.Choose(row, k)
								local again = W.Rows()[r]
								choices = choices + 1
								if not again or again.name ~= row.name or again.at ~= k then
									fail(model.name.." "..row.name.." choice "..k.." reads back "..tostring(again and again.at))
								end
								for i = 1, 5 do
									if i ~= FIELD[row.option.field] and state[i] ~= before[i] then fail(model.name.." "..row.name.." moved number "..i) end
								end
								-- every other row as it was
								local other = W.Rows()
								for o, was in ipairs(rows) do
									if o ~= r and was.kind == "list" and other[o].at ~= (o < r and other[o].at or was.at) and was.option.field ~= row.option.field then
										fail(model.name.." "..row.name.." changed "..was.name)
									end
								end
								rows = other; row = rows[r]
							end
						end
					end
				end
			end
			if W.off then fail(model.name..": the creator turned itself off: "..tostring(W.reason and W.reason.text)); break end
		end
	end
end
-- nothing of the game's asked while it had no character on the creator (the game dies of that: mock_glue.lua)
if mock.game.crashes > 0 then fail("the game's functions were called without a character: "..table.concat(mock.game.crashedIn, ", ")) end
print(("%d races and sexes, %d option rows, %d choices put on and read back: %s"):format(models, options, choices, fails == 0 and "all as chosen" or (fails.." wrong")))
os.exit(fails == 0 and models > 0 and 0 or 1)
