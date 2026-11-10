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
check(state == "ready" and version == 1 and renderer == false, "status: ready, registry 1, renderer false (no seam yet)")

check(mock.functions.WrathPP_GetNumCategories(10, 0, 2) == 2, "a blood elf man paladin: 2 categories")
check(mock.functions.WrathPP_GetNumCategories(4, 1, 1) == 2, "a night elf woman warrior: 2")
check(mock.functions.WrathPP_GetNumCategories(1, 0, 1) == 0, "a human: none")
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
