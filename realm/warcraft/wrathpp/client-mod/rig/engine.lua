-- The rig's widget engine: the 3.3.5 glue screens' frames, as far as the character creation screen needs them, built
-- from the game's own XML (tools/xml2lua.py) and driven by the game's own Lua.
--
-- What it keeps to, because the stand-in before it did not and was wrong each time:
--   * a method the 3.3.5 client does not have is not there (calling it is the error it is in the game);
--   * a frame is visible only if it and every parent are shown; a click on what is not visible or is disabled is refused;
--   * OnShow runs for a frame's children before the frame itself (the client's CSimpleFrame::ShowThis; the phone's
--     crash of 12 November 2026 showed the order), OnLoad after a frame's children are made;
--   * a script's error stops that script and is kept (E.errors), as the game stops the script and goes on;
--   * anchors are resolved to places on a screen of the phone's shape, so what overlaps or falls off can be seen.
local E = { frames = {}, templates = {}, errors = {}, screen = { w = 1125, h = 768 }, clock = 0, cursor = { 0, 0 } }

local function fail(fmt, ...) error(string.format(fmt, ...), 3) end

-- Every texture file a script names (not the game's XML: those the game has), with the script's line that named it:
-- E.files[name] = "WrathppCreate.lua:642". The rig draws nothing, so a file the client does not have is found by its name.
E.files = {}
local function names(file)
	if ( type(file) ~= "string" or file == "" ) then return end
	for level = 3, 12 do
		local info = debug.getinfo(level, "Sl")
		if ( not info ) then break end
		if ( not info.short_src:match("engine%.lua$") and info.what ~= "C" ) then
			E.files[file] = E.files[file] or (info.short_src:match("[^/\\]*$")..":"..tostring(info.currentline))
			return
		end
	end
	E.files[file] = E.files[file] or "?"
end

-- Classes -------------------------------------------------------------------------------------------------------------
local Region = {}
local Frame, Texture, FontString = setmetatable({}, { __index = Region }), setmetatable({}, { __index = Region }), setmetatable({}, { __index = Region })
local Button = setmetatable({}, { __index = Frame })
local CheckButton = setmetatable({}, { __index = Button })
local EditBox = setmetatable({}, { __index = Frame })
local ScrollFrame = setmetatable({}, { __index = Frame })
local Slider = setmetatable({}, { __index = Frame })
local Model = setmetatable({}, { __index = Frame })
local ModelFFX = setmetatable({}, { __index = Model })
local Font = {}
local CLASS = { Frame = Frame, Button = Button, CheckButton = CheckButton, EditBox = EditBox, ScrollFrame = ScrollFrame, Slider = Slider,
	Model = Model, ModelFFX = ModelFFX, Texture = Texture, FontString = FontString, SimpleHTML = Frame, StatusBar = Frame, GameTooltip = Frame }
E.CLASS = CLASS

local function new(kind, name, parent)
	local class = CLASS[kind]
	if ( not class ) then fail("CreateFrame: unknown frame type '%s'", tostring(kind)) end
	local o = setmetatable({ [0] = newproxy and newproxy() or {}, __kind = kind, __name = name, __parent = parent, __shown = true, __points = {}, __scripts = {},
		__children = {}, __regions = {}, __alpha = 1, __enabled = true, __level = 1 }, { __index = class })
	if ( kind == "Texture" or kind == "FontString" ) then
		if ( parent ) then parent.__regions[#parent.__regions + 1] = o end
	elseif ( parent ) then parent.__children[#parent.__children + 1] = o end
	E.frames[#E.frames + 1] = o
	if ( name ) then _G[name] = o end
	return o
end
E.new = new

-- Scripts ---------------------------------------------------------------------------------------------------------------
function E.run(frame, handler, ...)
	local fn = frame.__scripts[handler]
	if ( not fn ) then return end
	local ok, err = xpcall(function(...) return fn(frame, ...) end, function(e) return tostring(e).."\n"..debug.traceback("", 2) end, ...)
	if ( not ok ) then
		if ( type(err) == "string" and err:find("RIG CRASH", 1, true) ) then error(err, 0) end
		E.errors[#E.errors + 1] = { frame = frame.__name or frame.__kind, handler = handler, message = err }
	end
end

-- Region ----------------------------------------------------------------------------------------------------------------
function Region:GetName() return self.__name end
function Region:GetObjectType() return self.__kind end
function Region:IsObjectType(t) return self.__kind == t or (t == "Frame" and CLASS[self.__kind] ~= Texture and CLASS[self.__kind] ~= FontString) end
function Region:GetParent() return self.__parent end
function Region:SetParent(p)
	if ( type(p) == "string" ) then p = _G[p] end
	if ( p == self ) then fail("SetParent: a frame cannot be its own parent") end
	local a = p
	while ( a ) do if ( a == self ) then fail("SetParent: %s would become its own ancestor", tostring(self.__name)) end; a = a.__parent end
	local old = self.__parent
	local wasVisible = self:IsVisible()
	if ( old ) then
		local list = (self.__kind == "Texture" or self.__kind == "FontString") and old.__regions or old.__children
		for i, c in ipairs(list) do if ( c == self ) then table.remove(list, i); break end end
	end
	self.__parent = p
	if ( p ) then
		local list = (self.__kind == "Texture" or self.__kind == "FontString") and p.__regions or p.__children
		list[#list + 1] = self
	end
	-- a frame moved under a hidden parent goes from the screen, under a shown one comes to it: its scripts hear of it
	if ( self.__scripts ) then
		local now = self:IsVisible()
		if ( wasVisible and not now ) then E.hidden(self) elseif ( now and not wasVisible ) then E.shown(self) end
	end
end
function Region:ClearAllPoints() self.__points = {} end
local POINTS = { TOPLEFT = { 0, 1 }, TOP = { 0.5, 1 }, TOPRIGHT = { 1, 1 }, LEFT = { 0, 0.5 }, CENTER = { 0.5, 0.5 }, RIGHT = { 1, 0.5 },
	BOTTOMLEFT = { 0, 0 }, BOTTOM = { 0.5, 0 }, BOTTOMRIGHT = { 1, 0 } }
E.POINTS = POINTS
function Region:SetPoint(point, a, b, c, d)
	if ( type(point) ~= "string" or not POINTS[point:upper()] ) then fail("SetPoint: unknown point '%s'", tostring(point)) end
	point = point:upper()
	local rel, relPoint, x, y = self.__parent, point, 0, 0
	local relGiven = false
	if ( type(a) == "number" ) then x, y = a, b or 0
	else
		if ( a ~= nil ) then
			relGiven = true
			if ( type(a) == "string" ) then
				rel = _G[a]
				if ( not rel ) then fail("SetPoint: Couldn't find region named '%s'", a) end
			elseif ( type(a) == "table" ) then rel = a
			else fail("SetPoint: bad relativeTo (%s)", type(a)) end
		end
		if ( type(b) == "string" ) then
			relPoint = b:upper()
			if ( not POINTS[relPoint] ) then fail("SetPoint: unknown relative point '%s'", b) end
			x, y = c or 0, d or 0
		elseif ( type(b) == "number" ) then x, y = b, c or 0 end
	end
	if ( type(x) ~= "number" or type(y) ~= "number" or x ~= x or y ~= y or math.abs(x) == math.huge or math.abs(y) == math.huge ) then fail("SetPoint: bad offset (%s, %s)", tostring(x), tostring(y)) end
	if ( rel == self ) then fail("SetPoint: %s cannot be anchored to itself", tostring(self.__name)) end
	-- a region anchored to one that depends on it: the game refuses it
	local seen, stack = {}, { rel }
	while ( #stack > 0 ) do
		local r = table.remove(stack)
		if ( r and not seen[r] ) then
			seen[r] = true
			if ( r == self ) then fail("SetPoint: %s cannot anchor to a region dependent on it", tostring(self.__name)) end
			for _, p in ipairs(r.__points or {}) do stack[#stack + 1] = p.rel end
			if ( r.__allPoints ) then stack[#stack + 1] = r.__allPoints end
		end
	end
	for i, p in ipairs(self.__points) do if ( p.point == point ) then table.remove(self.__points, i); break end end
	self.__allPoints = nil
	self.__points[#self.__points + 1] = { point = point, rel = rel, relPoint = relPoint, x = x, y = y, relGiven = relGiven }
end
function Region:SetAllPoints(to)
	if ( type(to) == "string" ) then to = _G[to] end
	self.__points = {}
	self.__allPoints = to or self.__parent
end
function Region:GetNumPoints() return #self.__points end
function Region:GetPoint(i) local p = self.__points[i or 1]; if p then return p.point, p.rel, p.relPoint, p.x, p.y end end
local function size(v, what) if ( type(v) ~= "number" or v ~= v or v == math.huge or v < 0 ) then fail("%s: bad size (%s)", what, tostring(v)) end; return v end
function Region:SetWidth(w) self.__w = size(w, "SetWidth") end
function Region:SetHeight(h) self.__h = size(h, "SetHeight") end
-- (the phone's own CharacterCreate.xml calls SetSize on a texture: this client has it)
function Region:SetSize(w, h) self.__w, self.__h = size(w, "SetSize"), size(h, "SetSize") end
function Region:GetSize() return self:GetWidth(), self:GetHeight() end
function Region:Show() if ( not self.__shown ) then self.__shown = true; if ( self.__scripts and self:IsVisible() ) then E.shown(self) end end end
function Region:Hide() if ( self.__shown ) then local was = self:IsVisible(); self.__shown = false; if ( was and self.__scripts ) then E.hidden(self) end end end
function Region:IsShown() return self.__shown and 1 or nil end
function Region:IsVisible()
	local f = self
	while ( f ) do if ( not f.__shown ) then return nil end; f = f.__parent end
	return 1
end
function Region:SetAlpha(a) if ( type(a) ~= "number" ) then fail("SetAlpha: number expected") end; self.__alpha = a end
function Region:GetAlpha() return self.__alpha end

-- where a region is: left, bottom, width, height on the screen (nil: it has no place)
local resolving = {}
function E.rect(r)
	if ( r == nil ) then return nil end
	if ( r.__isScreen ) then return 0, 0, E.screen.w, E.screen.h end
	if ( resolving[r] ) then return nil end
	resolving[r] = true
	local l, b, w, h
	if ( r.__allPoints ) then l, b, w, h = E.rect(r.__allPoints)
	elseif ( r.__scrollOwner ) then
		-- a scroll frame's child sits at its top left, moved by the scroll
		local sl, sb, sw, sh = E.rect(r.__scrollOwner)
		if ( sl ) then w, h = r.__w or sw, r.__h or sh; l = sl - (r.__scrollOwner.__hscroll or 0); b = sb + sh - h + (r.__scrollOwner.__vscroll or 0) end
	elseif ( #r.__points > 0 ) then
		local xs, ys = {}, {}
		for _, p in ipairs(r.__points) do
			local rl, rb, rw, rh = E.rect(p.rel)
			if ( not rl ) then rl, rb, rw, rh = 0, 0, E.screen.w, E.screen.h end
			local rp, sp = POINTS[p.relPoint], POINTS[p.point]
			xs[sp[1]] = rl + rw * rp[1] + p.x
			ys[sp[2]] = rb + rh * rp[2] + p.y
		end
		local function span(t, given)
			local lo, hi
			for f in pairs(t) do if ( not lo or f < lo ) then lo = f end; if ( not hi or f > hi ) then hi = f end end
			if ( lo ~= hi ) then local len = (t[hi] - t[lo]) / (hi - lo); return t[lo] - len * lo, len end
			local len = given or 0
			return t[lo] - len * lo, len
		end
		local tw, th = r.__w, r.__h
		if ( r.__kind == "FontString" ) then
			tw = tw or (#tostring(r.__text or "") * 7)
			th = th or 12
		end
		l, w = span(xs, tw); b, h = span(ys, th)
	end
	resolving[r] = nil
	return l, b, w, h
end
function Region:GetLeft() local l = E.rect(self); return l end
function Region:GetBottom() local _, b = E.rect(self); return b end
function Region:GetRight() local l, _, w = E.rect(self); return l and l + w end
function Region:GetTop() local _, b, _, h = E.rect(self); return b and b + h end
function Region:GetWidth() local _, _, w = E.rect(self); return w or self.__w or 0 end
function Region:GetHeight() local _, _, _, h = E.rect(self); return h or self.__h or 0 end
function Region:GetCenter() local l, b, w, h = E.rect(self); if l then return l + w / 2, b + h / 2 end end

-- Showing and hiding: children first, then the frame's own script (CSimpleFrame::ShowThis / HideThis)
function E.shown(f)
	for _, c in ipairs({ unpack(f.__children) }) do if ( c.__shown ) then E.shown(c) end end
	E.run(f, "OnShow")
end
function E.hidden(f)
	for _, c in ipairs({ unpack(f.__children) }) do if ( c.__shown ) then E.hidden(c) end end
	E.run(f, "OnHide")
end

-- Frame -----------------------------------------------------------------------------------------------------------------
local HANDLERS = { OnLoad = true, OnShow = true, OnHide = true, OnUpdate = true, OnClick = true, OnEnter = true, OnLeave = true, OnMouseDown = true,
	OnMouseUp = true, OnMouseWheel = true, OnEvent = true, OnChar = true, OnKeyDown = true, OnKeyUp = true, OnEnterPressed = true, OnEscapePressed = true,
	OnTextChanged = true, OnValueChanged = true, OnVerticalScroll = true, OnHorizontalScroll = true, OnScrollRangeChanged = true, OnUpdateModel = true,
	OnSizeChanged = true, OnEditFocusGained = true, OnEditFocusLost = true, OnTabPressed = true, OnSpacePressed = true, OnDoubleClick = true,
	OnDragStart = true, OnDragStop = true, OnReceiveDrag = true, OnAnimFinished = true, OnTextSet = true, OnCursorChanged = true, OnInputLanguageChanged = true,
	OnAttributeChanged = true, OnEnable = true, OnDisable = true, PreClick = true, PostClick = true, OnMinMaxChanged = true, OnHyperlinkClick = true }
local TYPED = { OnClick = Button, PreClick = Button, PostClick = Button, OnDoubleClick = Button, OnVerticalScroll = ScrollFrame, OnHorizontalScroll = ScrollFrame,
	OnScrollRangeChanged = ScrollFrame, OnValueChanged = Slider, OnMinMaxChanged = Slider, OnUpdateModel = Model, OnAnimFinished = Model,
	OnTextChanged = EditBox, OnEnterPressed = EditBox, OnEscapePressed = EditBox, OnTabPressed = EditBox, OnSpacePressed = EditBox, OnEditFocusGained = EditBox,
	OnEditFocusLost = EditBox, OnTextSet = EditBox, OnCursorChanged = EditBox, OnInputLanguageChanged = EditBox }
local function isA(o, class) local c = CLASS[o.__kind]; while c do if c == class then return true end; local m = getmetatable(c); c = m and m.__index end end
function Frame:HasScript(h) return (HANDLERS[h] and (not TYPED[h] or isA(self, TYPED[h]))) and 1 or nil end
function Frame:SetScript(h, fn)
	if ( not self:HasScript(h) ) then fail("%s doesn't have a \"%s\" script", self.__kind, tostring(h)) end
	if ( fn ~= nil and type(fn) ~= "function" ) then fail("SetScript(\"%s\", function): function expected", h) end
	self.__scripts[h] = fn
end
function Frame:GetScript(h) if ( not self:HasScript(h) ) then fail("%s doesn't have a \"%s\" script", self.__kind, tostring(h)) end; return self.__scripts[h] end
function Frame:HookScript(h, fn)
	if ( not self:HasScript(h) ) then fail("%s doesn't have a \"%s\" script", self.__kind, tostring(h)) end
	local old = self.__scripts[h]
	self.__scripts[h] = old and function(...) old(...); fn(...) end or fn
end
local LAYERS = { BACKGROUND = true, BORDER = true, ARTWORK = true, OVERLAY = true, HIGHLIGHT = true }
function Frame:CreateTexture(name, layer, inherits)
	if ( layer and not LAYERS[layer] ) then fail("CreateTexture: unknown layer '%s'", tostring(layer)) end
	local t = new("Texture", name, self); t.__layer = layer or "ARTWORK"
	if ( inherits ) then E.inherit(t, inherits) end
	return t
end
function Frame:CreateFontString(name, layer, inherits)
	if ( layer and not LAYERS[layer] ) then fail("CreateFontString: unknown layer '%s'", tostring(layer)) end
	local t = new("FontString", name, self); t.__layer = layer or "ARTWORK"
	if ( inherits ) then
		if ( type(inherits) ~= "string" ) then fail("CreateFontString: the font to inherit is named by a string") end
		local font = _G[inherits]
		if ( type(font) == "table" and font.__font ) then t.__fontObject = font
		elseif ( E.templates[inherits] ) then E.inherit(t, inherits)
		else fail("CreateFontString: Couldn't find inherited node: %s", inherits) end
	end
	return t
end
local STRATA = { BACKGROUND = 1, LOW = 2, MEDIUM = 3, HIGH = 4, DIALOG = 5, FULLSCREEN = 6, FULLSCREEN_DIALOG = 7, TOOLTIP = 8 }
function Frame:SetFrameStrata(s) if ( not STRATA[s] ) then fail("SetFrameStrata: unknown strata '%s'", tostring(s)) end; self.__strata = s end
function Frame:GetFrameStrata() local f = self; while f do if f.__strata then return f.__strata end; f = f.__parent end; return "MEDIUM" end
function Frame:SetFrameLevel(n) if ( type(n) ~= "number" ) then fail("SetFrameLevel: number expected") end; self.__level = n end
function Frame:GetFrameLevel() return self.__level end
function Frame:EnableMouse(on) self.__mouse = on and true or false end
function Frame:IsMouseEnabled() return self.__mouse and 1 or nil end
function Frame:EnableMouseWheel(on) self.__wheel = on and true or false end
function Frame:EnableKeyboard(on) self.__keyboard = on and true or false end
function Frame:SetBackdrop(t) if ( t ~= nil and type(t) ~= "table" ) then fail("SetBackdrop: table expected") end; self.__backdrop = t; if ( t ) then names(t.bgFile); names(t.edgeFile) end end
function Frame:GetBackdrop() return self.__backdrop end
local function colour(what, r, g, b) if ( type(r) ~= "number" or type(g) ~= "number" or type(b) ~= "number" ) then fail("%s: r, g, b are numbers", what) end end
function Frame:SetBackdropColor(r, g, b, a) colour("SetBackdropColor", r, g, b); self.__backdropColor = { r, g, b, a or 1 } end
function Frame:SetBackdropBorderColor(r, g, b, a) colour("SetBackdropBorderColor", r, g, b); self.__backdropBorder = { r, g, b, a or 1 } end
function Frame:SetScale(s) if ( type(s) ~= "number" or s <= 0 ) then fail("SetScale: a number above 0") end; self.__scale = s end
function Frame:GetScale() return self.__scale or 1 end
function Frame:GetEffectiveScale() return 1 end
function Frame:SetID(id) self.__id = id end
function Frame:GetID() return self.__id or 0 end
function Frame:RegisterEvent(e) self.__events = self.__events or {}; self.__events[e] = true end
function Frame:UnregisterEvent(e) if self.__events then self.__events[e] = nil end end
function Frame:UnregisterAllEvents() self.__events = nil end
function Frame:SetToplevel() end
function Frame:Raise() end
function Frame:Lower() end
function Frame:GetChildren() return unpack(self.__children) end
function Frame:GetNumChildren() return #self.__children end
function Frame:GetRegions() return unpack(self.__regions) end
function Frame:GetNumRegions() return #self.__regions end
function Frame:SetHitRectInsets() end
function Frame:SetMovable() end
function Frame:SetClampedToScreen() end
function Frame:RegisterForDrag() end
function Frame:SetBackdropInsets() fail("SetBackdropInsets is not a method of the 3.3.5 client") end

-- Button, CheckButton ---------------------------------------------------------------------------------------------------
local function buttonTexture(self, key, tex, suffix)
	if ( tex == nil ) then self[key] = nil; return end
	local t = self[key]
	if ( type(tex) == "table" ) then self[key] = tex; return end
	if ( type(tex) ~= "string" ) then fail("%s: a texture or its file's name", suffix) end
	if ( not t ) then t = new("Texture", nil, self); t.__allPoints = self; self[key] = t end
	t.__file = tex
	names(tex)
end
function Button:SetNormalTexture(t) buttonTexture(self, "__normal", t, "SetNormalTexture") end
function Button:GetNormalTexture() return self.__normal end
function Button:SetPushedTexture(t) buttonTexture(self, "__pushed", t, "SetPushedTexture") end
function Button:GetPushedTexture() return self.__pushed end
function Button:SetHighlightTexture(t, mode) buttonTexture(self, "__highlight", t, "SetHighlightTexture") end
function Button:GetHighlightTexture() return self.__highlight end
function Button:SetDisabledTexture(t) buttonTexture(self, "__disabledTex", t, "SetDisabledTexture") end
function Button:GetDisabledTexture() return self.__disabledTex end
function Button:SetText(t) self.__text = t ~= nil and tostring(t) or nil; if ( self.__fontString ) then self.__fontString.__text = self.__text end end
function Button:GetText() return self.__text end
function Button:GetFontString() return self.__fontString end
function Button:SetFontString(fs) self.__fontString = fs end
function Button:GetTextWidth() return #(self.__text or "") * 7 end
function Button:GetTextHeight() return 12 end
function Button:Enable() self.__enabled = true end
function Button:Disable() self.__enabled = false end
function Button:IsEnabled() return self.__enabled and 1 or nil end
function Button:SetButtonState(s) self.__state = s end
function Button:GetButtonState() return self.__state or (self.__enabled and "NORMAL" or "DISABLED") end
function Button:LockHighlight() end
function Button:UnlockHighlight() end
function Button:RegisterForClicks() end
function Button:SetNormalFontObject(f) self.__font = f end
function Button:SetHighlightFontObject() end
function Button:SetDisabledFontObject() end
function Button:SetPushedTextOffset() end
function Button:Click(button, down)
	if ( not self.__enabled ) then return end
	if ( isA(self, CheckButton) ) then self.__checked = not self.__checked end
	E.run(self, "OnClick", button or "LeftButton", down)
end
function CheckButton:SetChecked(c) self.__checked = (c and c ~= 0) and true or false end
function CheckButton:GetChecked() return self.__checked and 1 or nil end
function CheckButton:SetCheckedTexture(t) buttonTexture(self, "__checkedTex", t, "SetCheckedTexture") end
function CheckButton:GetCheckedTexture() return self.__checkedTex end
function CheckButton:SetDisabledCheckedTexture(t) buttonTexture(self, "__disabledChecked", t, "SetDisabledCheckedTexture") end

-- EditBox, ScrollFrame, Slider, Model -------------------------------------------------------------------------------------
function EditBox:SetText(t) self.__text = tostring(t or ""); E.run(self, "OnTextChanged", false) end
function EditBox:GetText() return self.__text or "" end
function EditBox:SetFocus() E.focus = self end
function EditBox:ClearFocus() if ( E.focus == self ) then E.focus = nil end end
function EditBox:HighlightText() end
function EditBox:SetMaxLetters(n) self.__letters = n end
function EditBox:GetNumLetters() return #(self.__text or "") end
function EditBox:SetAutoFocus() end
function EditBox:SetTextInsets() end
function EditBox:SetFontObject(f) self.__font = f end
function EditBox:SetTextColor() end
function ScrollFrame:SetScrollChild(c)
	if ( type(c) ~= "table" ) then fail("SetScrollChild: a frame") end
	if ( self.__scrollChild ) then self.__scrollChild.__scrollOwner = nil end
	self.__scrollChild = c; c.__scrollOwner = self
	if ( c.__parent ~= self ) then c:SetParent(self) end
end
function ScrollFrame:GetScrollChild() return self.__scrollChild end
local function scroll(v, what) if ( type(v) ~= "number" or v ~= v or math.abs(v) == math.huge ) then fail("%s: bad offset (%s)", what, tostring(v)) end; return v end
function ScrollFrame:SetVerticalScroll(v) self.__vscroll = scroll(v, "SetVerticalScroll"); E.run(self, "OnVerticalScroll", v) end
function ScrollFrame:GetVerticalScroll() return self.__vscroll or 0 end
function ScrollFrame:SetHorizontalScroll(v) self.__hscroll = scroll(v, "SetHorizontalScroll") end
function ScrollFrame:GetHorizontalScroll() return self.__hscroll or 0 end
function ScrollFrame:GetVerticalScrollRange()
	local c = self.__scrollChild
	return c and math.max(0, (c.__h or 0) - self:GetHeight()) or 0
end
function ScrollFrame:GetHorizontalScrollRange() return 0 end
function ScrollFrame:UpdateScrollChildRect() end
function Slider:SetValue(v) self.__value = v; E.run(self, "OnValueChanged", v) end
function Slider:GetValue() return self.__value or 0 end
function Slider:SetMinMaxValues(a, b) self.__min, self.__max = a, b end
function Slider:GetMinMaxValues() return self.__min or 0, self.__max or 0 end
function Slider:SetValueStep() end
function Slider:SetOrientation() end
function Slider:SetThumbTexture(t) self.__thumb = t end
function Slider:GetThumbTexture() return self.__thumb end
function Slider:Enable() self.__enabled = true end
function Slider:Disable() self.__enabled = false end
for _, m in ipairs({ "SetSequence", "SetCamera", "AdvanceTime", "SetModel", "ClearModel", "SetLight", "SetFogColor", "SetFogNear", "SetFogFar", "ClearFog",
		"SetPosition", "SetFacing", "SetModelScale", "ReplaceIconTexture", "SetGlow", "SetSequenceTime" }) do Model[m] = function() end end
function Model:GetModel() return self.__model end
function ModelFFX:ResetLights() end
function ModelFFX:AddCharacterLight() end
function ModelFFX:AddLight() end
function ModelFFX:AddPetLight() end

-- Texture, FontString, Font -----------------------------------------------------------------------------------------------
function Texture:SetTexture(a, b, c, d)
	if ( type(a) == "number" ) then colour("SetTexture", a, b, c); self.__colour = { a, b, c, d or 1 }; self.__file = nil
	elseif ( a == nil or type(a) == "string" ) then
		self.__file = a; self.__colour = nil; names(a)
		-- the client gives nothing for a file it cannot set (Script_SetTexture): E.unreadable(name) says which those are
		if ( a and E.unreadable and E.unreadable(a) ) then self.__file = nil; return nil end
	else fail("SetTexture: a file's name or r, g, b") end
	return 1
end
function Texture:GetTexture() return self.__file end
function Texture:GetTexCoord()
	local c = self.__coords
	if ( not c ) then return 0, 0, 0, 1, 1, 0, 1, 1 end
	if ( #c == 8 ) then return unpack(c) end
	return c[1], c[3], c[1], c[4], c[2], c[3], c[2], c[4]          -- (left, right, top, bottom) as the four corners
end
function Texture:SetTexCoord(...) local n = select("#", ...); if ( n ~= 4 and n ~= 8 ) then fail("SetTexCoord: 4 or 8 numbers, got %d", n) end
	for i = 1, n do if ( type(select(i, ...)) ~= "number" ) then fail("SetTexCoord: numbers") end end; self.__coords = { ... } end
function Texture:SetVertexColor(r, g, b, a) colour("SetVertexColor", r, g, b); self.__vertex = { r, g, b, a or 1 } end
function Texture:SetDesaturated(d) self.__desaturated = d and true or false; return 1 end
function Texture:SetBlendMode(m) self.__blend = m end
function Texture:SetDrawLayer(l) if ( not LAYERS[l] ) then fail("SetDrawLayer: unknown layer") end; self.__layer = l end
function Texture:GetDrawLayer() return self.__layer end
function Texture:SetGradient() end
function Texture:SetGradientAlpha() end
function FontString:SetText(t) self.__text = t ~= nil and tostring(t) or nil end
function FontString:GetText() return self.__text end
function FontString:SetFormattedText(f, ...) self.__text = string.format(f, ...) end
function FontString:SetTextColor(r, g, b, a) colour("SetTextColor", r, g, b); self.__colour = { r, g, b, a or 1 } end
function FontString:SetVertexColor(r, g, b, a) colour("SetVertexColor", r, g, b); self.__colour = { r, g, b, a or 1 } end
local JH, JV = { LEFT = true, CENTER = true, RIGHT = true }, { TOP = true, MIDDLE = true, BOTTOM = true }
function FontString:SetJustifyH(j) if ( not JH[j] ) then fail("SetJustifyH: LEFT, CENTER or RIGHT, got '%s'", tostring(j)) end; self.__justify = j end
function FontString:SetJustifyV(j) if ( not JV[j] ) then fail("SetJustifyV: TOP, MIDDLE or BOTTOM, got '%s'", tostring(j)) end; self.__justifyV = j end
function FontString:SetFont(file, height, flags) if ( type(file) ~= "string" or type(height) ~= "number" ) then fail("SetFont(file, height[, flags])") end; self.__fontFile, self.__fontHeight = file, height; return 1 end
function FontString:GetFont() return self.__fontFile, self.__fontHeight end
function FontString:SetFontObject(f) if ( type(f) == "string" ) then f = _G[f] end; if ( type(f) ~= "table" ) then fail("SetFontObject: a font") end; self.__fontObject = f end
function FontString:GetFontObject() return self.__fontObject end
function FontString:GetStringWidth() return #tostring(self.__text or "") * (self.__fontHeight or 12) * 0.55 end
function FontString:GetStringHeight() return self.__fontHeight or 12 end
function FontString:SetNonSpaceWrap() end
function FontString:SetShadowColor() end
function FontString:SetShadowOffset() end
function FontString:SetTextHeight() end
function FontString:SetSpacing() end
function FontString:SetDrawLayer(l) if ( not LAYERS[l] ) then fail("SetDrawLayer: unknown layer") end; self.__layer = l end
function Font:GetName() return self.__name end
function Font:SetFont() end
function Font:GetFont() return "Fonts\\FRIZQT__.TTF", 12 end
function Font:SetTextColor() end
function Font:SetShadowColor() end
function Font:SetShadowOffset() end
function Font:SetJustifyH() end
function Font:SetFontObject() end
function E.font(name) local f = setmetatable({ __font = true, __name = name }, { __index = Font }); _G[name] = f; return f end

-- Frames from the game's XML ----------------------------------------------------------------------------------------------
local FRAME_TAGS = { Frame = true, Button = true, CheckButton = true, EditBox = true, ScrollFrame = true, Slider = true, Model = true, ModelFFX = true,
	SimpleHTML = true, StatusBar = true, GameTooltip = true }
local ARGS = { OnUpdate = "elapsed", OnClick = "button, down", OnEnter = "motion", OnLeave = "motion", OnMouseDown = "button", OnMouseUp = "button", OnMouseWheel = "delta",
	OnEvent = "event, ...", OnChar = "text", OnKeyDown = "key", OnKeyUp = "key", OnTextChanged = "userInput", OnValueChanged = "value", OnVerticalScroll = "offset",
	OnScrollRangeChanged = "xrange, yrange", OnSizeChanged = "w, h", OnHorizontalScroll = "offset" }
local function child(node, tag) for _, c in ipairs(node) do if ( c.tag == tag ) then return c end end end
local function named(name, parent)
	if ( not name ) then return nil end
	return (name:gsub("%$parent", parent and parent.__name or ""))
end
local function num(v) return v and tonumber(v) end
local function dims(node)
	-- <Size x= y=/>, or <AbsDimension x= y=/> inside it; <Offset> likewise
	local a = node.attr or {}
	local x, y = num(a.x), num(a.y)
	local abs = child(node, "AbsDimension")
	if ( abs ) then x, y = num(abs.attr.x) or x, num(abs.attr.y) or y end
	return x, y
end

function E.applyRegion(node, o)
	local a = node.attr or {}
	if ( a.hidden == "true" ) then o.__shown = false end
	if ( a.alpha ) then o.__alpha = tonumber(a.alpha) end
	if ( a.setAllPoints == "true" ) then o.__allPoints = o.__parent end
	for _, c in ipairs(node) do
		if ( c.tag == "Size" ) then
			local x, y = dims(c); if x then o.__w = x end; if y then o.__h = y end
		elseif ( c.tag == "Anchors" ) then
			o.__points = {}
			for _, an in ipairs(c) do
				local at = an.attr or {}
				local x, y = num(at.x) or 0, num(at.y) or 0
				local off = child(an, "Offset")
				if ( off ) then local ox, oy = dims(off); x, y = ox or x, oy or y end
				local relName = at.relativeTo and named(at.relativeTo, o.__parent)
				local rel = relName and _G[relName] or o.__parent
				if ( relName and not _G[relName] ) then E.errors[#E.errors + 1] = { frame = o.__name or o.__kind, handler = "XML", message = "Couldn't find relative frame: "..relName } end
				o.__points[#o.__points + 1] = { point = at.point, rel = rel, relPoint = at.relativePoint or at.point, x = x, y = y, relGiven = relName ~= nil }
			end
		end
	end
end

function E.applyTexture(node, t)
	local a = node.attr or {}
	if ( a.inherits ) then E.inherit(t, a.inherits) end
	if ( a.file ) then t.__file = a.file end
	E.applyRegion(node, t)
	local tc = child(node, "TexCoords")
	if ( tc ) then t.__coords = { num(tc.attr.left), num(tc.attr.right), num(tc.attr.top), num(tc.attr.bottom) } end
end
function E.applyFontString(node, t)
	local a = node.attr or {}
	if ( a.inherits ) then
		if ( type(_G[a.inherits]) == "table" and _G[a.inherits].__font ) then t.__fontObject = _G[a.inherits]
		elseif ( E.templates[a.inherits] ) then E.inherit(t, a.inherits)
		else t.__fontObject = E.font(a.inherits) end          -- a font of a file the phone did not send: made, so the screen builds
	end
	if ( a.text ) then t.__text = _G[a.text] or a.text end
	if ( a.justifyH ) then t.__justify = a.justifyH end
	E.applyRegion(node, t)
end
function E.inherit(o, names)
	for name in tostring(names):gmatch("[^,%s]+") do
		local node = E.templates[name]
		if ( node ) then
			if ( o.__kind == "Texture" ) then E.applyTexture(node, o) elseif ( o.__kind == "FontString" ) then E.applyFontString(node, o) else E.applyFrame(node, o) end
		elseif ( E.builtin[name] ) then E.builtin[name](o)
		else E.missingTemplates[name] = true end
	end
end
E.builtin, E.missingTemplates = {}, {}

function E.applyFrame(node, f)
	local a = node.attr or {}
	if ( a.inherits ) then E.inherit(f, a.inherits) end
	if ( a.id ) then f.__id = tonumber(a.id) end
	if ( a.frameStrata ) then f.__strata = a.frameStrata end
	if ( a.enableMouse == "true" ) then f.__mouse = true end
	if ( a.enableKeyboard == "true" ) then f.__keyboard = true end
	if ( a.letters ) then f.__letters = tonumber(a.letters) end
	E.applyRegion(node, f)
	if ( a.text and f.SetText ) then f:SetText(_G[a.text] or a.text) end
	for _, c in ipairs(node) do
		if ( c.tag == "Layers" ) then
			for _, layer in ipairs(c) do
				for _, r in ipairs(layer) do
					local name = named(r.attr and r.attr.name, f)
					if ( r.tag == "Texture" ) then
						local t = new("Texture", name, f); t.__layer = layer.attr and layer.attr.level or "ARTWORK"; E.applyTexture(r, t)
					elseif ( r.tag == "FontString" ) then
						local t = new("FontString", name, f); t.__layer = layer.attr and layer.attr.level or "ARTWORK"; E.applyFontString(r, t)
					end
				end
			end
		elseif ( c.tag == "Frames" ) then
			for _, k in ipairs(c) do if ( FRAME_TAGS[k.tag] ) then E.build(k, f) end end
		elseif ( c.tag == "ScrollChild" ) then
			for _, k in ipairs(c) do if ( FRAME_TAGS[k.tag] ) then local sc = E.build(k, f); f.__scrollChild = sc; sc.__scrollOwner = f end end
		elseif ( c.tag == "NormalTexture" or c.tag == "PushedTexture" or c.tag == "HighlightTexture" or c.tag == "DisabledTexture" or c.tag == "CheckedTexture" or c.tag == "DisabledCheckedTexture" ) then
			local t = new("Texture", named(c.attr and c.attr.name, f), f)
			t.__allPoints = f
			E.applyTexture(c, t)
			local key = ({ NormalTexture = "__normal", PushedTexture = "__pushed", HighlightTexture = "__highlight", DisabledTexture = "__disabledTex", CheckedTexture = "__checkedTex", DisabledCheckedTexture = "__disabledChecked" })[c.tag]
			f[key] = t
		elseif ( c.tag == "ButtonText" ) then
			local t = new("FontString", named(c.attr and c.attr.name, f), f); E.applyFontString(c, t)
			if ( #t.__points == 0 and not t.__allPoints ) then t.__points = { { point = "CENTER", rel = f, relPoint = "CENTER", x = 0, y = 0 } } end
			f.__fontString = t; t.__text = f.__text
		elseif ( c.tag == "Backdrop" ) then
			f.__backdrop = { bgFile = c.attr.bgFile, edgeFile = c.attr.edgeFile }
		elseif ( c.tag == "Scripts" ) then
			for _, s in ipairs(c) do
				local fn
				if ( s.attr and s.attr["function"] ) then
					fn = _G[s.attr["function"]]                        -- bound to the function as it is now
					if ( type(fn) ~= "function" ) then E.errors[#E.errors + 1] = { frame = f.__name or f.__kind, handler = s.tag, message = "no function "..s.attr["function"] } end
				elseif ( s.text ) then
					local code = "return function(self"..(ARGS[s.tag] and (", "..ARGS[s.tag]) or "")..") "..s.text.."\nend"
					local chunk, err = loadstring(code, "*"..(f.__name or f.__kind)..":"..s.tag)
					if ( not chunk ) then E.errors[#E.errors + 1] = { frame = f.__name or f.__kind, handler = s.tag, message = err } else fn = chunk() end
				end
				if ( fn ) then f.__scripts[s.tag] = fn end
			end
		end
	end
end

-- One frame of the XML made, its children with it, then its OnLoad.
function E.build(node, parent)
	local a = node.attr or {}
	if ( a.virtual == "true" ) then E.templates[a.name] = node; return nil end
	if ( a.parent ) then parent = _G[a.parent] or parent end
	local f = new(node.tag, named(a.name, parent), parent)
	E.applyFrame(node, f)
	E.run(f, "OnLoad")
	return f
end

-- A whole file: its templates noted, its frames made (scripts named by <Script file=> are the caller's to run first).
function E.load(ui)
	for _, node in ipairs(ui) do
		local a = node.attr or {}
		if ( a.virtual == "true" and a.name ) then E.templates[a.name] = node
		elseif ( FRAME_TAGS[node.tag] ) then E.build(node, nil)
		elseif ( node.tag == "Font" and a.name ) then E.font(a.name) end
	end
end

-- CreateFrame, as scripts call it
function E.CreateFrame(kind, name, parent, template)
	if ( type(kind) ~= "string" ) then fail("CreateFrame: the frame's type is a string") end
	if ( name ~= nil and type(name) ~= "string" ) then fail("CreateFrame: the name is a string or nil") end
	if ( type(parent) == "string" ) then parent = _G[parent] end
	if ( parent ~= nil and type(parent) ~= "table" ) then fail("CreateFrame: the parent is a frame") end
	if ( not FRAME_TAGS[kind] ) then fail("CreateFrame: Unknown frame type '%s'", kind) end
	local f = new(kind, name and named(name, parent) or nil, parent)
	if ( template ) then
		if ( type(template) ~= "string" ) then fail("CreateFrame: the template is named by a string") end
		for t in template:gmatch("[^,%s]+") do
			if ( not E.templates[t] and not E.builtin[t] ) then fail("CreateFrame: Couldn't find inherited node: %s", t) end
		end
		E.inherit(f, template)
		E.run(f, "OnLoad")
	end
	return f
end

-- The screen, a click, a frame of time -------------------------------------------------------------------------------------
-- A tap on a frame, as a finger would give it: only on what is on the screen and takes it.
-- Whether a frame inside a scroll frame is scrolled out of its sight (a scroll frame shows only what is inside itself).
function E.clipped(f)
	local l, b, w, h = E.rect(f)
	if ( not l ) then return false end
	local cx, cy = l + w / 2, b + h / 2
	local a = f
	while ( a ) do
		if ( a.__scrollOwner ) then
			local sl, sb, sw, sh = E.rect(a.__scrollOwner)
			if ( sl and (cx < sl or cx > sl + sw or cy < sb or cy > sb + sh) ) then return true end
		end
		a = a.__parent
	end
	return false
end
function E.click(f, button)
	if ( type(f) ~= "table" ) then fail("click: no such frame") end
	if ( not f:IsVisible() ) then fail("click: %s is not on the screen", tostring(f.__name or f.__kind)) end
	local l, b, w, h = E.rect(f)
	if ( not l or w <= 0 or h <= 0 ) then fail("click: %s has no size on the screen", tostring(f.__name or f.__kind)) end
	if ( E.clipped(f) ) then fail("click: %s is scrolled out of sight in its list", tostring(f.__name or f.__kind)) end
	-- what shows of it (a scroll frame shows only what is inside itself) is all on the screen
	local vl, vb, vr, vt = l, b, l + w, b + h
	local a = f
	while ( a ) do
		if ( a.__scrollOwner ) then
			local sl, sb, sw, sh = E.rect(a.__scrollOwner)
			if ( sl ) then vl, vb, vr, vt = math.max(vl, sl), math.max(vb, sb), math.min(vr, sl + sw), math.min(vt, sb + sh) end
		end
		a = a.__parent
	end
	if ( vl < -1 or vb < -1 or vr > E.screen.w + 1 or vt > E.screen.h + 1 ) then fail("click: %s is partly off the screen (%d, %d, %d x %d)", tostring(f.__name), l, b, w, h) end
	E.run(f, "OnMouseDown", button or "LeftButton")
	E.run(f, "OnMouseUp", button or "LeftButton")
	if ( f.Click and f.__enabled ) then f:Click(button or "LeftButton") end
end
function E.update(elapsed, frames)
	for _ = 1, frames or 1 do
		E.clock = E.clock + elapsed
		for _, f in ipairs({ unpack(E.frames) }) do
			if ( f.__scripts and f.__scripts.OnUpdate and f:IsVisible() ) then E.run(f, "OnUpdate", elapsed) end
		end
	end
end

return E
