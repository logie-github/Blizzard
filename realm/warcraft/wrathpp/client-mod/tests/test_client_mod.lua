-- Tests of the Wrath++ client mod (wrathpp/init.lua) on the mock runtime (mock_wxl.lua), fed the
-- server's messages run.sh made with the server's own encoders (fixtures.lua). Writes what the
-- mod sent into SENT_FILE for run.sh to decode as the server would.
local here, mod, fixtures, sent_file = arg[1], arg[2], arg[3], arg[4]
local fails, passes = 0, 0
local function check(cond, what)
	if cond then passes = passes + 1 print("ok   " .. what) else fails = fails + 1 print("FAIL " .. what) end
end
local function fromhex(h) return (h:gsub("..", function(x) return string.char(tonumber(x, 16)) end)) end
local F = dofile(fixtures)

local function load()
	package.loaded.mock = nil
	local mock = dofile(here .. "/mock_wxl.lua")
	_G.wxl, _G.Observe = mock.wxl, mock.observe
	_G.bit = require("bit")
	local WPP = dofile(mod)
	return mock, WPP
end

-- A registry that isn't the one the hello names: refused, no hello sent.
local mock, WPP = load()
mock.deliver(0x521, fromhex(F.hello))
mock.deliver(0x523, fromhex(F.registry) .. "\0")
check(WPP.state == "refused" and #mock.sent == 0, "a registry with a byte more than the hello's hash is refused, nothing sent")

mock, WPP = load()
check(mock.claimed[0x521] and mock.claimed[0x527], "opcodes 0x521-0x527 claimed")
check(mock.functions.WrathPP_Status ~= nil and mock.functions.WrathPP_SendCreateChoices ~= nil, "glue functions registered")
local ok = WPP.sendCreate(10, 0, 2)
check(not ok, "nothing sent before the server's hello")
mock.deliver(0x521, fromhex(F.hello))
mock.deliver(0x523, fromhex(F.registry))
check(WPP.state == "ready", "ready after hello and registry")
check(WPP.registry.hash == tonumber(F.hash, 16), "the registry's FNV-1a in Lua is the server's hash")
check(#mock.sent == 1 and mock.sent[1].op == 0x522, "the client's hello sent")
local state, _, version, renderer = mock.functions.WrathPP_Status()
check(state == "ready" and version == F.version and renderer == false, "status: ready, the registry's version, renderer false (no seam yet)")

check(mock.functions.WrathPP_GetNumCategories(10, 0, 2) == 3, "a blood elf man paladin: 3 categories (the two of the demon hunter look and the hair colour)")
check(mock.functions.WrathPP_GetNumCategories(4, 1, 1) == 19, "a night elf woman warrior: 19 (the two, the three body options, her scars, markings, tattoos, vines, ears, eyebrows, headdress, horns and blindfold with their colours, the hair and the skin colour)")
check(mock.functions.WrathPP_GetNumCategories(1, 0, 1) == 3, "a human man: his eyebrows and face shape and the hair colour")
check(mock.functions.WrathPP_GetNumCategories(1, 1, 1) == 7, "a human woman: the three body options, her eyebrows, makeup and face shape and the hair colour")
local id, name, n, default = mock.functions.WrathPP_GetCategoryInfo(1, 10, 0, 2)
check(id == 1002 and name == "Horns" and n == 3 and default == 1, "category 1: Horns, 3 options, default 1")
local oid, oname = mock.functions.WrathPP_GetOptionInfo(1002, 2, 2)
check(oid == 2 and oname == "Horns 1", "option 2 of Horns: Horns 1")

check(WPP.setChoice(1002, 2), "horns 2 chosen")
check(not WPP.setChoice(1002, 9), "an option that doesn't exist refused")
local cid = WPP.cycleChoice(1003, 1, 2)
check(cid == 2, "blindfold cycled from its default to 2")
check(WPP.choices[1002] == 2, "  horns still 2")
cid = WPP.cycleChoice(1003, 1, 2)
check(cid == 1, "  and around to 1")
WPP.cycleChoice(1003, -1, 2)
check(WPP.choices[1003] == 2, "  and back to 2")
check(WPP.sendCreate(10, 0, 2), "the new character's choices sent")

mock.deliver(0x525, fromhex(F.appearance))
check(#mock.events > 0, "events fired")
local g = F.guid
local copt, cname = mock.functions.WrathPP_GetCharacterChoice(g, 1003)
check(copt == 2 and cname == "Blindfold 1", "the character list's look kept: blindfold 2")
check(WPP.sendCharacterChoice(g, 1002, 3), "one category of the character changed")
check(not WPP.sendCharacterChoice("0x0000000000000099", 1002, 3), "  a character the server didn't describe refused")

WPP.want("0x00000000000000AA")
WPP.want(g) -- known: not asked
check(WPP.flushQueries() == 1, "one unknown player asked for")
check(WPP.flushQueries() == 0, "  once")

mock.deliver(0x526, fromhex(F.result))
check(WPP.lastResult.code == "ineligible" and WPP.lastResult.category == 1003, "a result read: ineligible, category 1003")

-- The parts: a human woman with the second makeup and the second hair colour gets her shell and picture to the native mod
mock.files["Wrathpp\\parts.txt"] = table.concat({
	"# header", "S\t1\t1\t1\t1201\tCharacter\\Human\\Female\\HumanFemaleFace.m2",
	"S\t1\t1\t2\t1202\tCharacter\\Human\\Female\\HumanFemaleFace.m2",
	"C\t1\t1\t1201\t1\t0\tCharacter\\Human\\Female\\HumanFemaleOv1.blp",
	"C\t1\t1\t1201\t1\t1\tCharacter\\Human\\Female\\HumanFemaleOv2.blp",
	"C\t1\t1\t1202\t1\t*\tCharacter\\Human\\Female\\HumanFemaleOv3.blp",
	"C\t1\t1\t1202\t2\t*\tCharacter\\Human\\Female\\HumanFemaleOv4.blp",
	"P\t2\t0\t1\t1211\t1212\tCharacter\\Orc\\Male\\OrcMaleFace.m2",
	"C\t2\t0\t1211\t1\ts2\tCharacter\\Orc\\Male\\OrcMaleOvGhost.blp",
	"C\t2\t0\t1211\t1\ts3\tCharacter\\Orc\\Male\\OrcMaleOvBeast.blp" }, "\n") .. "\n"
WPP.looks["0x00000000000000B1"] = { race = 1, sex = 1, class = 1, version = 3, entries = { [1190] = 2, [1202] = 2 } }
check(WPP.applyParts("0x00000000000000B1"), "a character's parts handed to the native mod")
local chunk = mock.ran[#mock.ran] and mock.ran[#mock.ran].chunk or ""
check(chunk:find("HumanFemaleOv2.blp", 1, true) and chunk:find("HumanFemaleOv4.blp", 1, true), "  her hair colour's eyebrows and her second makeup")
check(chunk:find('"0x00000000000000B1"', 1, true) and chunk:find('""', 1, true), "  the guid, and the empty third part")
check(not WPP.applyParts("0x00000000000000B2"), "  a character the server didn't describe: nothing")
WPP.looks["0x00000000000000B4"] = { race = 2, sex = 0, class = 1, version = 3, entries = { [1211] = 1, [1212] = 3 } }
WPP.applyParts("0x00000000000000B4")
chunk = mock.ran[#mock.ran].chunk
check(chunk:find("OrcMaleOvBeast.blp", 1, true) and chunk:find("OrcMaleFace.m2", 1, true), "  an orc's war paint: the colour's picture for the style he chose")
mock.files["Wrathpp\\parts.txt"] = mock.files["Wrathpp\\parts.txt"] .. "T\t6\t0\t2\t1300\tCharacter\\Tauren\\Male\\TaurenMaleBody.m2\nD\t6\t0\t1300\t2\t*\tCharacter\\Tauren\\Male\\TaurenMaleBo6.blp\n"
WPP.parts = nil
WPP.looks["0x00000000000000B5"] = { race = 6, sex = 0, class = 1, version = 3, entries = { [1300] = 2 } }
WPP.applyParts("0x00000000000000B5")
chunk = mock.ran[#mock.ran].chunk
check(chunk:find("TaurenMaleBody.m2", 1, true) and chunk:find("TaurenMaleBo6.blp", 1, true), "  a tauren's tattoo: the body shell and the body picture")
mock.files["Wrathpp\\parts.txt"] = mock.files["Wrathpp\\parts.txt"] .. table.concat({
	"H\t4\t1\tCharacter\\NightElf\\Female\\NightElfFemaleHair00_%02d.blp",
	"K\t4\t1\t1\tCharacter\\NightElf\\Female\\NightElfFemaleSkin00_00.blp",
	"K\t4\t1\t2\tCharacter\\NightElf\\Female\\NightElfFemaleSkin00_01.blp",
	"Z\t4\t1\t1330\t2\tCharacter\\NightElf\\Female\\NightElfFemalePk9.blp",
	"G\t4\t1\t1\t1320\tCharacter\\NightElf\\Female\\NightElfFemalePVines.m2\t13\t1330\t0",
	"G\t4\t1\t4\t1323\tCharacter\\NightElf\\Female\\NightElfFemalePHorns.m2\t\t0\t11",
	"G\t4\t1\t2\t1321\tCharacter\\NightElf\\Female\\NightElfFemalePEars.m2\t11\t0",
	"G\t4\t1\t3\t1322\tCharacter\\NightElf\\Female\\NightElfFemalePEyebrows.m2\t12\t0" }, "\n") .. "\n"
WPP.parts = nil
WPP.looks["0x00000000000000B6"] = { race = 4, sex = 1, class = 1, version = 3, entries = { [1190] = 4, [1191] = 2, [1320] = 2, [1321] = 5, [1322] = 3, [1323] = 6, [1330] = 2 } }
WPP.applyParts("0x00000000000000B6")
chunk = mock.ran[#mock.ran].chunk
check(chunk:find("NightElfFemalePVines.m2|2||%S*|Character\\\\NightElf\\\\Female\\\\NightElfFemalePk9.blp") or (chunk:find("PVines.m2|2||", 1, true) and chunk:find("Pk9.blp", 1, true)), "  a night elf woman's vines: choice 2 and the picked colour's texture")
check(chunk:find("PEars.m2|5|Character", 1, true) and chunk:find("Skin00_01.blp", 1, true), "  her ears: choice 5 on the second skin's texture")
check(chunk:find("PHorns.m2|6||||11", 1, true), "  her horns: choice 6 on the helm point (11)")
check(chunk:find("PEyebrows.m2|3||Character", 1, true) and chunk:find("Hair00_03.blp", 1, true), "  her eyebrows: choice 3 in the third hair colour's texture")
mock.files["Wrathpp\\parts.txt"] = mock.files["Wrathpp\\parts.txt"] .. "B\t1\t1\t201\t16\t23\t0.08742\t0.08189\t1.45428\t30,31\t26\t0.08742\t-0.08300\t1.45428\t\n"
WPP.parts = nil
local before = #mock.ran
WPP.applyParts("0x00000000000000B6")
local soft
for k = before + 1, #mock.ran do if mock.ran[k].chunk:find("WrathPP_SetSoftBody", 1, true) then soft = mock.ran[k].chunk end end
check(soft and soft:find("WrathPP_SetSoftBody(201,16,23,0.08742,0.08189,1.45428,\"30,31\",26,", 1, true), "  the women's breast bones go to the native mod when the parts table is read")
WPP.looks["0x00000000000000B3"] = { race = 10, sex = 0, class = 1, version = 3, entries = {} }
local before = #mock.ran
WPP.applyParts("0x00000000000000B3")
check(#mock.ran == before + 1 and not mock.ran[#mock.ran].chunk:find("Human", 1, true), "  a race with no parts: all three empty")

mock.observers["NetScript.OnDisconnected"]("127.0.0.1")
check(WPP.state == "waiting" and next(WPP.looks) == nil, "a disconnect forgets the server")
check(not WPP.sendCreate(10, 0, 2), "  and sends nothing until it speaks again")

local f = assert(io.open(sent_file, "w"))
for _, m in ipairs(mock.sent) do
	f:write(string.format("%x ", m.op), (m.body:gsub(".", function(c) return string.format("%02x", c:byte()) end)), "\n")
end
f:close()
print(passes .. " passed, " .. fails .. " failed")
os.exit(fails == 0 and 0 or 1)
