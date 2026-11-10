-- A stand-in for the WarcraftXL Lua runtime's API, as much of it as the Wrath++ mod uses
-- (sdk lua/types/wxl.d.lua at the pinned SDK): net's claims, handlers, readers and writers,
-- script functions and events, Observe. Little-endian, guids as "0x" and 16 hex digits.
local M = { sent = {}, events = {}, functions = {}, observers = {}, claimed = {}, handlers = {}, heard = false }

local function le(value, size)
	local t = {}
	for i = 1, size do
		t[i] = string.char(value % 256)
		value = math.floor(value / 256)
	end
	return table.concat(t)
end

local Writer = {}
Writer.__index = Writer
function Writer:U8(v) self.b[#self.b + 1] = le(v, 1) return self end
function Writer:U16(v) self.b[#self.b + 1] = le(v, 2) return self end
function Writer:U32(v) self.b[#self.b + 1] = le(v, 4) return self end
function Writer:Guid(g)
	local hex = g:sub(3)
	local lo, hi = tonumber(hex:sub(9, 16), 16), tonumber(hex:sub(1, 8), 16)
	self.b[#self.b + 1] = le(lo, 4) .. le(hi, 4)
	return self
end
function Writer:String(s) self.b[#self.b + 1] = s .. "\0" return self end
function Writer:Data() return table.concat(self.b) end

local Reader = {}
Reader.__index = Reader
local function take(self, n)
	if not self.ok or self.pos + n - 1 > #self.s then self.ok = false return nil end
	local part = self.s:sub(self.pos, self.pos + n - 1)
	self.pos = self.pos + n
	return part
end
local function num(self, n)
	local part = take(self, n)
	if not part then return 0 end
	local v = 0
	for i = n, 1, -1 do v = v * 256 + part:byte(i) end
	return v
end
function Reader:U8() return num(self, 1) end
function Reader:U16() return num(self, 2) end
function Reader:U32() return num(self, 4) end
function Reader:Guid()
	local lo, hi = num(self, 4), num(self, 4)
	return string.format("0x%08X%08X", hi, lo)
end
-- A string ended by a zero byte (as the runtime's).
function Reader:String(max)
	local at = self.s:find("\0", self.pos, true)
	if not at or at - self.pos > (max or 4096) then self.ok = false return "" end
	local s = self.s:sub(self.pos, at - 1)
	self.pos = at + 1
	return s
end
function Reader:Bytes(n) return take(self, n) or "" end
function Reader:Ok() return self.ok end
function Reader:AtEnd() return self.ok and self.pos == #self.s + 1 end
function Reader:Data() return self.s end

M.wxl = {
	net = {
		Claim = function(op) M.claimed[op] = true return true end,
		SetHandler = function(op, fn) M.handlers[op] = fn return true end,
		Writer = function() return setmetatable({ b = {} }, Writer) end,
		Send = function(op, w)
			if not M.claimed[op] then return nil, "invalid" end
			if not M.heard then return nil, "failed" end
			M.sent[#M.sent + 1] = { op = op, body = type(w) == "string" and w or w:Data() }
			return true
		end,
	},
	script = {
		RegisterFunction = function(name, fn) M.functions[name] = fn return true end,
		RegisterEvent = function() return true end,
		FireEvent = function(name, ...) M.events[#M.events + 1] = { name, ... } return true end,
	},
}
function M.observe(family, method, fn) M.observers[family .. "." .. method] = fn return 1 end
function M.deliver(op, bytes)
	M.heard = true
	M.handlers[op](setmetatable({ s = bytes, pos = 1, ok = true }, Reader))
end
return M
