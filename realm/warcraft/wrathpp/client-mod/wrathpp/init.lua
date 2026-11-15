-- Wrath++ appearance: the client's half of docs/wrathpp/PROTOCOL.md, for the WarcraftXL client's
-- Lua runtime (wxl.lua). It
--   * hears the Wrath++ world server's hello and registry before the character list, checks the
--     registry's bytes against the hash the hello names, and answers with its own hello;
--   * keeps the looks the server sends (the account's characters, the player, the players around);
--   * gives the glue and game scripts the WrathPP_* functions below, and the events
--     WRATHPP_READY, WRATHPP_APPEARANCE (guid) and WRATHPP_RESULT (code, guid, category);
--   * asks the server for the looks of players it sees and doesn't know yet.
-- What it does not do yet: draw. The looks reach a model only through the client's
-- Component.GeosRenderPrep seam, which isn't there (docs/wrathpp/CLIENT_PROBE.md); until then
-- WrathPP_Status() says renderer = false, and no screen may claim a preview.

local WPP = {}
WPP.MAGIC = 0x31505057
WPP.PROTOCOL = 1
WPP.SMSG_HELLO, WPP.CMSG_HELLO, WPP.SMSG_REGISTRY = 0x521, 0x522, 0x523
WPP.CMSG_SET_APPEARANCE, WPP.SMSG_APPEARANCE, WPP.SMSG_RESULT, WPP.CMSG_QUERY = 0x524, 0x525, 0x526, 0x527
WPP.RESULTS = { [0] = "ok", "malformed", "unsupported_version", "unknown_category", "unknown_option", "ineligible",
    "duplicate", "too_many", "not_owner", "registry_mismatch", "disabled", "character_mismatch" }
WPP.CAP_GEOSET = 1
WPP.MAX_ENTRIES, WPP.MAX_BATCH = 32, 64
local PENDING_CREATE, EXISTING = 0, 1

local bit = bit or require("bit")
local net = wxl.net

WPP.state = "waiting"        -- waiting | ready | refused
WPP.reason = nil
WPP.server = nil             -- the hello
WPP.registry = nil           -- { version, hash, categories = { [id] = category }, order = { ids } }
WPP.looks = {}               -- [guid] = { race, sex, class, version, entries = { [category] = option } }
WPP.choices = {}             -- the creation screen's: [category] = option
WPP.lastResult = nil
WPP.renderer = false         -- no native seam yet: nothing is drawn
local wanted, asked = {}, {}

-- FNV-1a over a byte string, unsigned 32-bit (LuaJIT's bit works in signed 32 bits; h * 16777619 is
-- split as h << 24 + h * 403 so no product passes 2^53).
function WPP.fnv1a(bytes)
    local h = 2166136261
    for i = 1, #bytes do
        h = bit.bxor(h, bytes:byte(i)) % 4294967296
        h = (bit.lshift(h, 24) % 4294967296 + h * 403) % 4294967296
    end
    return h
end

local function fire(name, ...)
    if wxl.script and wxl.script.FireEvent then wxl.script.FireEvent(name, ...) end
end

local function readAppearance(r)
    local version, n = r:U16(), r:U8()
    if not r:Ok() or n > WPP.MAX_ENTRIES then return nil end
    local entries, last = {}, -1
    for _ = 1, n do
        local cat, opt = r:U16(), r:U16()
        if not r:Ok() or cat <= last then return nil end
        entries[cat], last = opt, cat
    end
    return version, entries
end

local function writeAppearance(w, version, entries)
    local cats = {}
    for cat in pairs(entries) do cats[#cats + 1] = cat end
    table.sort(cats)
    w:U16(version):U8(#cats)
    for _, cat in ipairs(cats) do w:U16(cat):U16(entries[cat]) end
    return w
end

-- The protocol's names: a length byte, then the bytes (not the zero-ended strings of NetReader:String).
local function name(r)
    local n = r:U8()
    if not r:Ok() or n > 48 then return nil end
    return n == 0 and "" or r:Bytes(n)
end

function WPP.parseRegistry(r)
    local reg = { categories = {}, order = {} }
    reg.version = r:U16()
    local nc = r:U16()
    if not r:Ok() then return nil, "malformed" end
    for _ = 1, nc do
        local c = { options = {}, optionOrder = {}, eligibility = {} }
        c.id, c.kind, c.geosetGroup, c.default = r:U16(), r:U8(), r:U16(), r:U16()
        c.name = name(r)
        for _ = 1, r:U16() do
            c.eligibility[#c.eligibility + 1] = { race = r:U8(), sexMask = r:U8(), classMask = r:U32() }
        end
        for _ = 1, r:U16() do
            local o = { id = r:U16(), value = r:U16(), classMask = r:U32() }
            o.name = name(r)
            c.options[o.id] = o
            c.optionOrder[#c.optionOrder + 1] = o.id
        end
        if not r:Ok() or not c.name then return nil, "malformed" end
        for _, o in pairs(c.options) do if not o.name then return nil, "malformed" end end
        reg.categories[c.id] = c
        reg.order[#reg.order + 1] = c.id
    end
    if not r:AtEnd() then return nil, "malformed" end
    return reg
end

local function classAllowed(mask, class)
    return mask == 0 or (class >= 1 and class <= 32 and bit.band(mask, bit.lshift(1, class - 1)) ~= 0)
end

-- The categories a race / sex (0 male, 1 female) / class may choose, in the registry's order.
function WPP.categoriesFor(race, sex, class)
    local out = {}
    if not WPP.registry then return out end
    for _, id in ipairs(WPP.registry.order) do
        local c = WPP.registry.categories[id]
        for _, e in ipairs(c.eligibility) do
            if e.race == race and bit.band(e.sexMask, bit.lshift(1, sex)) ~= 0 and classAllowed(e.classMask, class) then
                out[#out + 1] = c
                break
            end
        end
    end
    return out
end

function WPP.optionsFor(c, class)
    local out = {}
    for _, id in ipairs(c.optionOrder) do
        local o = c.options[id]
        if classAllowed(o.classMask, class) then out[#out + 1] = o end
    end
    return out
end

-- Messages from the server.
function WPP.onHello(r)
    local magic, pmin, pmax, version, hash = r:U32(), r:U16(), r:U16(), r:U16(), r:U32()
    if not r:Ok() or not r:AtEnd() or magic ~= WPP.MAGIC then
        WPP.state, WPP.reason = "refused", "malformed hello"
        return
    end
    if WPP.PROTOCOL < pmin or WPP.PROTOCOL > pmax then
        WPP.state, WPP.reason = "refused", "the server speaks protocols " .. pmin .. "-" .. pmax
        return
    end
    WPP.server = { protocolMin = pmin, protocolMax = pmax, version = version, hash = hash }
end

function WPP.onRegistry(r)
    local bytes = r:Data()
    if not WPP.server then return end
    local reg, why = WPP.parseRegistry(r)
    if not reg then
        WPP.state, WPP.reason = "refused", "registry: " .. why
        return
    end
    reg.hash = WPP.fnv1a(bytes)
    if reg.hash ~= WPP.server.hash or reg.version ~= WPP.server.version then
        WPP.state, WPP.reason = "refused", "the registry isn't the one the hello names"
        return
    end
    WPP.registry = reg
    local ok, why2 = net.Send(WPP.CMSG_HELLO, net.Writer():U32(WPP.MAGIC):U16(WPP.PROTOCOL):U32(reg.hash):U32(WPP.CAP_GEOSET))
    if not ok then
        WPP.state, WPP.reason = "refused", "hello not sent: " .. tostring(why2)
        return
    end
    WPP.state, WPP.reason = "ready", nil
    fire("WRATHPP_READY")
end

-- The parts (tools/sl_parts.py: Wrathpp\parts.txt in the looks' package): what a character's registry choices of the
-- Shadowlands options mean as pictures on head shells. Tab separated, `S race sex slot category shell` and
-- `C race sex category option colour picture`. The native mod hangs them (WrathPP_ApplyLook) on the model each character of the
-- world draws with.
WPP.parts = nil
WPP.HAIR_COLOUR = 1190
WPP.MAX_PARTS = 8

function WPP.loadParts()
    if WPP.parts then return WPP.parts end
    local parts = { slots = {}, pictures = {}, bodyPictures = {} }
    if not (wxl.storage and wxl.storage.Read) then return parts end
    local ok, text = pcall(wxl.storage.Read, "Wrathpp\\parts.txt")
    if not ok or type(text) ~= "string" then return parts end      -- (a package without parts: asked again next time)
    WPP.parts = parts
    for line in text:gmatch("[^\r\n]+") do
        local kind, a, b, c, d, e, f = line:match("^(%a)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t?([^\t]*)\t?([^\t]*)$")
        local key = a and (a .. ":" .. b)
        if kind == "S" and key then
            local list = parts.slots[key] or {}
            parts.slots[key] = list
            list[#list + 1] = { category = tonumber(d), shell = e }
        elseif kind == "P" and key then                       -- a paint: its colour's category, then its style's
            local list = parts.slots[key] or {}
            parts.slots[key] = list
            list[#list + 1] = { category = tonumber(d), style = tonumber(e), shell = f }
        elseif kind == "T" and key then                       -- the same on the body shell (its pictures: D lines)
            local list = parts.slots[key] or {}
            parts.slots[key] = list
            list[#list + 1] = { category = tonumber(d), shell = e, body = true }
        elseif kind == "U" and key then
            local list = parts.slots[key] or {}
            parts.slots[key] = list
            list[#list + 1] = { category = tonumber(d), style = tonumber(e), shell = f, body = true }
        elseif kind == "D" and key then
            local byCategory = parts.bodyPictures[key] or {}
            parts.bodyPictures[key] = byCategory
            local options = byCategory[tonumber(c)] or {}
            byCategory[tonumber(c)] = options
            local colours = options[tonumber(d)] or {}
            options[tonumber(d)] = colours
            colours[e] = f
        elseif kind == "C" and key then
            local byCategory = parts.pictures[key] or {}
            parts.pictures[key] = byCategory
            local options = byCategory[tonumber(c)] or {}
            byCategory[tonumber(c)] = options
            local colours = options[tonumber(d)] or {}
            options[tonumber(d)] = colours
            colours[e] = f
        end
    end
    return parts
end

-- The shells and pictures a look names: { { shell, picture }, ... } (no more than the native mod keeps).
function WPP.partsOf(look)
    local parts = WPP.loadParts()
    local list = parts.slots[look.race .. ":" .. look.sex]
    local out = {}
    if not list then return out end
    local colour = tostring((look.entries[WPP.HAIR_COLOUR] or 1) - 1)
    for _, slot in ipairs(list) do
        local options = (slot.body and parts.bodyPictures or parts.pictures)[look.race .. ":" .. look.sex]
        options = options and options[slot.category]
        local colours = options and options[look.entries[slot.category] or 1]
        local picture = colours and (colours["*"] or colours[colour] or (slot.style and colours["s" .. (look.entries[slot.style] or 1)]))
        if picture and #out < WPP.MAX_PARTS then out[#out + 1] = { shell = slot.shell, picture = picture } end
    end
    return out
end

-- Gives the native mod a character's parts (it hangs them once the character's model is in the world, and again whenever
-- the model is made again). The text runs in the client's own Lua, where the native mod's WrathPP_* functions are.
function WPP.applyParts(guid)
    local look = WPP.looks[guid]
    if not look or not (wxl.script and wxl.script.Run) then return false end
    local list = WPP.partsOf(look)
    local args = { string.format("%q", guid) }
    for i = 1, WPP.MAX_PARTS do
        local part = list[i]
        args[#args + 1] = string.format("%q", part and part.shell or "")
        args[#args + 1] = string.format("%q", part and part.picture or "")
    end
    local ok = pcall(wxl.script.Run, "if WrathPP_ApplyLook then WrathPP_ApplyLook(" .. table.concat(args, ",") .. ") end", "wrathpp-parts")
    return ok
end

function WPP.onAppearance(r)
    local count = r:U8()
    if not r:Ok() or count > WPP.MAX_BATCH then return end
    for _ = 1, count do
        local guid, race, sex, class = r:Guid(), r:U8(), r:U8(), r:U8()
        local version, entries = readAppearance(r)
        if not version then return end
        WPP.looks[guid] = { race = race, sex = sex, class = class, version = version, entries = entries }
        wanted[guid], asked[guid] = nil, nil
        fire("WRATHPP_APPEARANCE", guid)
        WPP.applyParts(guid)
    end
end

function WPP.onResult(r)
    local kind, guid, code, category = r:U8(), r:Guid(), r:U8(), r:U16()
    if not r:Ok() then return end
    WPP.lastResult = { kind = kind, guid = guid, code = WPP.RESULTS[code] or tostring(code), category = category }
    fire("WRATHPP_RESULT", WPP.lastResult.code, guid, category)
end

-- What the scripts call.
local function find(category)
    return WPP.registry and WPP.registry.categories[category]
end

function WPP.status()
    return WPP.state, WPP.reason, WPP.registry and WPP.registry.version or 0, WPP.renderer
end

function WPP.setChoice(category, option)
    local c = find(category)
    if not c or not c.options[option] then return false end
    WPP.choices[category] = option
    return true
end

function WPP.cycleChoice(category, delta, class)
    local c = find(category)
    if not c then return nil end
    local opts = WPP.optionsFor(c, class or 0)
    if #opts == 0 then return nil end
    local current = WPP.choices[category] or c.default
    local at = 1
    for i, o in ipairs(opts) do if o.id == current then at = i end end
    local nxt = opts[(at - 1 + delta) % #opts + 1]
    WPP.choices[category] = nxt.id
    return nxt.id, nxt.name
end

function WPP.resetChoices()
    WPP.choices = {}
end

function WPP.randomizeChoices(race, sex, class)
    WPP.choices = {}
    for _, c in ipairs(WPP.categoriesFor(race, sex, class)) do
        local opts = WPP.optionsFor(c, class)
        if #opts > 0 then WPP.choices[c.id] = opts[math.random(#opts)].id end
    end
end

-- The creation screen's choices that apply to race / sex / class, sent before CreateCharacter.
function WPP.sendCreate(race, sex, class)
    if WPP.state ~= "ready" then return false, WPP.reason or WPP.state end
    local entries = {}
    for _, c in ipairs(WPP.categoriesFor(race, sex, class)) do
        entries[c.id] = WPP.choices[c.id] or c.default
    end
    local w = net.Writer():U8(PENDING_CREATE):Guid("0x0000000000000000"):U8(race):U8(sex):U8(class)
    return net.Send(WPP.CMSG_SET_APPEARANCE, writeAppearance(w, WPP.registry.version, entries))
end

-- One category of an existing character changed, the others kept as the server last said.
function WPP.sendCharacterChoice(guid, category, option)
    if WPP.state ~= "ready" then return false, WPP.reason or WPP.state end
    local look = WPP.looks[guid]
    if not look then return false, "unknown character" end
    local entries = {}
    for cat, opt in pairs(look.entries) do entries[cat] = opt end
    entries[category] = option
    local w = net.Writer():U8(EXISTING):Guid(guid):U8(look.race):U8(look.sex):U8(look.class)
    return net.Send(WPP.CMSG_SET_APPEARANCE, writeAppearance(w, WPP.registry.version, entries))
end

-- A player seen without known looks: asked for on the next update, a batch at a time.
function WPP.want(guid)
    if WPP.looks[guid] or asked[guid] then return end
    wanted[guid] = true
end

function WPP.flushQueries()
    if WPP.state ~= "ready" then return 0 end
    local n, list = 0, {}
    for guid in pairs(wanted) do
        if n == WPP.MAX_BATCH then break end
        list[#list + 1], n = guid, n + 1
    end
    if n == 0 then return 0 end
    local w = net.Writer():U8(n)
    for _, guid in ipairs(list) do
        w:Guid(guid)
        wanted[guid], asked[guid] = nil, true
    end
    net.Send(WPP.CMSG_QUERY, w)
    return n
end

function WPP.reset()
    WPP.state, WPP.reason, WPP.server, WPP.registry = "waiting", nil, nil, nil
    WPP.looks, WPP.choices, WPP.lastResult = {}, {}, nil
    wanted, asked = {}, {}
end

-- Wiring into the runtime.
for op = WPP.SMSG_HELLO, WPP.CMSG_QUERY do assert(net.Claim(op)) end
net.SetHandler(WPP.SMSG_HELLO, WPP.onHello)
net.SetHandler(WPP.SMSG_REGISTRY, WPP.onRegistry)
net.SetHandler(WPP.SMSG_APPEARANCE, WPP.onAppearance)
net.SetHandler(WPP.SMSG_RESULT, WPP.onResult)

local fns = {
    WrathPP_Status = WPP.status,
    WrathPP_GetNumCategories = function(race, sex, class) return #WPP.categoriesFor(race, sex, class) end,
    WrathPP_GetCategoryInfo = function(index, race, sex, class)
        local c = WPP.categoriesFor(race, sex, class)[index]
        if not c then return nil end
        return c.id, c.name, #WPP.optionsFor(c, class), c.default, c.kind
    end,
    WrathPP_GetOptionInfo = function(category, index, class)
        local c = find(category)
        local o = c and WPP.optionsFor(c, class or 0)[index]
        if not o then return nil end
        return o.id, o.name
    end,
    WrathPP_GetChoice = function(category)
        local c = find(category)
        if not c then return nil end
        local id = WPP.choices[category] or c.default
        return id, c.options[id] and c.options[id].name
    end,
    WrathPP_SetChoice = WPP.setChoice,
    WrathPP_CycleChoice = WPP.cycleChoice,
    WrathPP_ResetChoices = WPP.resetChoices,
    WrathPP_RandomizeChoices = WPP.randomizeChoices,
    WrathPP_SendCreateChoices = WPP.sendCreate,
    WrathPP_GetCharacterChoice = function(guid, category)
        local look, c = WPP.looks[guid], find(category)
        if not look or not c then return nil end
        local id = look.entries[category]
        return id, id and c.options[id] and c.options[id].name
    end,
    WrathPP_SetCharacterChoice = WPP.sendCharacterChoice,
}
for name, fn in pairs(fns) do wxl.script.RegisterFunction(name, fn) end
for _, name in ipairs({ "WRATHPP_READY", "WRATHPP_APPEARANCE", "WRATHPP_RESULT" }) do wxl.script.RegisterEvent(name) end

Observe("NetScript", "OnDisconnected", function() WPP.reset() end)
Observe("ObjectScript", "OnObjectCreate", function(_, guid, type)
    if type == "Player" or type == 4 then WPP.want(guid) end -- (4: TYPEID_PLAYER, a newer runtime's number)
end)
Observe("WorldScript", "OnUpdate", function() WPP.flushQueries() end)

return WPP
