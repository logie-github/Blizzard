-- A picture's worth of the screen: every frame on it, where it is.  luajit shot.lua RIG_DIR CREATOR LOOKS UNDEAD|- OUT.json W H race sex class [step] [category] [row whose list to open]
local dir, creator, looks, undead, out = arg[1], arg[2], arg[3], arg[4], arg[5]
local work = os.getenv("RIG_WORK") or dir
local R = dofile(dir.."/rig.lua")({ dir = dir, stock = work.."/stock", data = os.getenv("RIG_DATA") or (work.."/data"), creator = creator ~= "-" and creator or nil,
	looks = creator ~= "-" and looks or nil, undead = (creator ~= "-" and undead ~= "-") and undead or nil, screen = { w = tonumber(arg[6]), h = tonumber(arg[7]) } })
R.G.forceFirst = { race = tonumber(arg[8]), sex = tonumber(arg[9]), class = tonumber(arg[10]) }
R.open()
if arg[11] == "2" then R.tap("WrathppCustomizeButton"); R.frames(0.1) end
if arg[12] and arg[12] ~= "-" then R.tap("WrathppCategory"..arg[12]); R.frames(1.5) end
if arg[13] then local f = R.row(arg[13]); if f then R.tap(f.choice); R.frames(0.1) else print("no row "..arg[13]) end end
for _, p in ipairs(R.problems()) do print("PROBLEM "..p) end
local function q(s) return '"'..tostring(s):gsub('[\\"]', "\\%0"):gsub("\n", " ")..'"' end
local parts = {}
for _, f in ipairs(R.layout()) do
	parts[#parts + 1] = ('{"name":%s,"kind":%s,"l":%.1f,"b":%.1f,"w":%.1f,"h":%.1f,"text":%s,"mouse":%s,"parent":%s,"file":%s,"enabled":%s}'):format(
		q(f.name), q(f.kind), f.l, f.b, f.w, f.h, q(f.text or ""), tostring(f.mouse and true or false), q(f.parent), q(f.file or ""), tostring(f.enabled ~= false))
end
local h = io.open(out, "w"); h:write('{"w":'..R.E.screen.w..',"h":'..R.E.screen.h..',"frames":['..table.concat(parts, ",\n").."]}"); h:close()
print(#parts.." frames on the screen")
