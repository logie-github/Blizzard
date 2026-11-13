-- The rig: the 3.3.5 client's character creation screen put together from the real pieces, to run Wrath++'s creator on.
--   the screen:  the phone's own GlueXML files (CharacterCreate.xml and .lua, GlueButtons.xml, GlueParent.xml, GlueStrings.lua:
--                sent by the app as issues #57 to #64), built by engine.lua;
--   the game:    game.lua, the client's creation logic ported from its decompiled source, on the game's tables;
--   Wrath++:     Shadowlands' art's table (WrathppAtlas.lua), the creator (WrathppCreate.lua), the looks' options
--                (WrathppLooks.lua) and the undead skins' (WrathppUndead.lua), loaded last, as the app's patch has them
--                in GlueXML.toc.
-- local R = dofile("rig.lua")(opts)      opts: dir (this folder), stock, data, creator, looks, undead, screen = { w, h }, native (false: none)
return function(opts)
	local dir = opts.dir
	-- a rig made after another in the same Lua starts from nothing of the other's: its frames, the creator's and the
	-- game's globals go (a frame named as one of the last rig's would be found by name and be the wrong one)
	setmetatable(_G, nil)
	for k, v in pairs(_G) do
		if ( type(v) == "table" and (rawget(v, "__kind") or rawget(v, "__font")) ) then _G[k] = nil
		elseif ( type(k) == "string" and (k:match("^Wrath") or k:match("^CharacterCreate") or k:match("^CharCreate") or k:match("^SetCharacter") or k:match("^CharacterC")) ) then _G[k] = nil end
	end
	local E = dofile(dir.."/engine.lua")
	-- RIG_ART=unreadable: the art's files are in and the game cannot set them (what a phone whose client does not read
	-- them would be); without the art's table at all its files are not there either
	local atlasGiven = opts.atlas or os.getenv("RIG_ATLAS")
	local unreadable = os.getenv("RIG_ART") == "unreadable" or not atlasGiven or atlasGiven == "-" or atlasGiven == ""
	E.unreadable = function(name) return unreadable and name:lower():find("interface\\wrathpp\\", 1, false) ~= nil end
	local G = dofile(dir.."/game.lua")
	local R = { E = E, G = G, notes = {} }
	E.screen = opts.screen or E.screen

	-- what the glue's Lua has besides Lua's own (GlueParent.lua and the client)
	for k, v in pairs({ strupper = string.upper, strlower = string.lower, strsub = string.sub, strfind = string.find, strlen = string.len, format = string.format,
			gsub = string.gsub, strrep = string.rep, tinsert = table.insert, tremove = table.remove, floor = math.floor, ceil = math.ceil, max = math.max, min = math.min,
			abs = math.abs, mod = math.fmod, getn = table.getn }) do _G[k] = v end
	function getglobal(n) return _G[n] end
	function setglobal(n, v) _G[n] = v end
	SEX_NONE, SEX_MALE, SEX_FEMALE = 1, 2, 3
	CHARACTER_ROTATION_CONSTANT = 0.6
	function GetCursorPosition() return E.cursor[1], E.cursor[2] end
	function GetTime() return E.clock end
	-- the phone's screen: 1828 x 1248 pixels (Config.wtf's gxResolution, as the phone's report has it)
	local cvars = { gxResolution = opts.resolution or "1828x1248" }
	function GetCVar(name) return cvars[name] end
	function PlaySound() end
	function Screenshot() R.notes[#R.notes + 1] = "screenshot" end
	function message(text) R.notes[#R.notes + 1] = "message: "..tostring(text) end
	function GlueDialog_Show(which) R.notes[#R.notes + 1] = "dialog: "..tostring(which) end
	function SetBackgroundModel(frame, name) frame.__background = name end
	function GlueParent_OnLoad() end
	function GlueParent_OnEvent() end
	function GlueFrameFadeUpdate() end
	-- (two functions of files the phone did not send, which the creation screen's own frames call as they load)
	function GlueTooltip_SetFont() end
	function GlueScrollFrame_OnScrollRangeChanged() end
	function SetGlueScreen(name)
		R.screenName = name
		if ( name == "charcreate" ) then CharacterCreate:Show() else CharacterCreate:Hide() end
	end
	CreateFrame = E.CreateFrame

	-- the game's strings: the part of GlueStrings.lua the phone's report held (cut at what an issue takes), up to its last whole line
	local strings = io.open(opts.stock.."/GlueStrings.lua"):read("*a"):gsub("\r", "")
	local chunk
	while ( #strings > 0 ) do
		chunk = loadstring(strings, "GlueStrings.lua")
		if ( chunk ) then break end
		local cut = strings:match("^(.*)\n[^\n]*$")
		if ( not cut ) then break end
		strings = cut
	end
	if ( chunk ) then chunk() end
	-- the strings the creation screen asks for by a made-up name, where the cut file did not reach them
	setmetatable(_G, { __index = function(_, k)
		if ( type(k) ~= "string" ) then return nil end
		if ( k:match("^RACE_INFO_%u+$") or k:match("^RACE_INFO_%u+_FEMALE$") or k:match("^CLASS_%u+$") or k:match("^CLASS_%u+_FEMALE$")
			or k:match("^HAIR_%u+_STYLE$") or k:match("^HAIR_%u+_COLOR$") or k:match("^FACIAL_HAIR_%u+$") or k:match("^CHAR_CUSTOMIZATION%d_DESC$") or k:match("^%u+_DISABLED$") ) then
			return k
		end
		return nil
	end })
	for _, k in ipairs({ "MALE", "FEMALE", "RANDOMIZE", "BACK", "CHARACTER_CREATE_ACCEPT", "ALLIANCE", "HORDE", "NAME", "CHARACTER_CREATE" }) do
		if ( rawget(_G, k) == nil ) then _G[k] = k:sub(1, 1)..k:sub(2):lower() end
	end

	-- fonts the phone's own files name (GlueFonts.xml itself was not among the files sent)
	for _, name in ipairs({ "GlueFontNormalSmall", "GlueFontHighlight", "GlueFontNormal", "GlueFontNormalLarge", "GlueFontHighlightSmall", "GlueFontDisableSmall",
			"GlueFontDisable", "GlueFontNormalHuge", "GlueFontDisableLarge", "GlueEditBoxFont", "GlueFontCharacterCreate", "CharacterCreateTooltipFont",
			"FactionName_Shadow_Huge", "OptionsFontSmall" }) do E.font(name) end
	-- templates of files that were not sent, as far as the creation screen uses them
	E.builtin.GlueScrollFrameTemplate = function(f)
		local bar = E.new("Slider", f.__name and (f.__name.."ScrollBar") or nil, f)
		bar.__w, bar.__h = 16, 100
		bar.__points = { { point = "TOPLEFT", rel = f, relPoint = "TOPRIGHT", x = 6, y = -16 } }
	end
	E.builtin.GlueTooltipTemplate = function() end

	-- the screen itself
	G.load(opts.data)
	G.define()
	local function xml(name) return dofile(opts.data.."/"..name..".xml.lua") end
	E.load(xml("GlueParent"))
	GlueParent.__isScreen = true
	E.load(xml("GlueButtons"))
	local stockLua = assert(loadstring(io.open(opts.stock.."/CharacterCreate.lua"):read("*a"):gsub("\r", ""), "CharacterCreate.lua"))
	stockLua()
	E.load(xml("CharacterCreate"))
	R.stockErrors = #E.errors

	-- Wrath++'s files, last
	if ( opts.native == false ) then
		for _, n in ipairs({ "WrathPP_GetCustomization", "WrathPP_SetCustomization", "WrathPP_GetCreating", "WrathPP_SetGear", "WrathPP_Log", "WrathPP_SetScreen", "WrathPP_NativeVersion" }) do _G[n] = nil end
	end
	-- (the art's table first, as the app's patch lists the files by name: WrathppAtlas, WrathppCreate, WrathppLooks, WrathppUndead;
	-- RIG_ATLAS: the art package's WrathppAtlas.lua, "-" or unset for a phone without the art)
	local atlasFile = opts.atlas or os.getenv("RIG_ATLAS")
	if ( atlasFile == "-" or atlasFile == "" or not opts.creator ) then atlasFile = nil end
	WrathppAtlas = nil
	WrathppShots = opts.shots and "rig" or nil            -- the app asks for pictures of the creator (WrathppShots.lua in its patch)
	for _, file in ipairs({ atlasFile or false, opts.creator or false, opts.looks or false, opts.undead or false }) do
		if ( file ) then
			local fn, err = loadfile(file)
			if ( not fn ) then error("the game would not load "..file..": "..tostring(err)) end
			local ok, e = pcall(fn)
			if ( not ok ) then E.errors[#E.errors + 1] = { frame = file, handler = "load", message = tostring(e) } end
		end
	end

	-- What a person does ------------------------------------------------------------------------------------------------------
	function R.open() SetGlueScreen("charcreate"); E.update(0.02, 3) end
	function R.close() SetGlueScreen("charselect") end
	-- a frame in a list brought into sight as a person brings it: the wheel (a two-finger drag) over the list, until it is
	function R.reach(f, list)
		if ( type(f) == "string" ) then f = _G[f] end
		if ( not f or not list or not list.__scripts or not list.__scripts.OnMouseWheel ) then return end
		for _ = 1, 80 do
			if ( not E.clipped(f) ) then return end
			local _, b = E.rect(f)
			local _, lb, _, lh = E.rect(list)
			list.__scripts.OnMouseWheel(list, (b + 1 > lb + lh / 2) and 1 or -1)
			E.update(0.02, 25)
		end
	end
	-- a tap (list: the list the frame is in, scrolled first if the frame is out of its sight)
	function R.tap(f, list)
		if ( type(f) == "string" ) then local n = f; f = _G[n]; if ( not f ) then error("no frame named "..n, 2) end end
		if ( list ) then R.reach(f, list) end
		E.click(f)
	end
	function R.frames(seconds) E.update(0.02, math.max(1, math.floor((seconds or 0.02) / 0.02))) end
	function R.visible(f) if ( type(f) == "string" ) then f = _G[f] end; return f and f:IsVisible() and true or false end
	-- the creator's rows that are on the screen, in order
	function R.rows()
		local out = {}
		for k = 1, 60 do
			local f = _G["WrathppRow"..k]
			if ( f and f:IsVisible() and f.row ) then out[#out + 1] = f end
		end
		return out
	end
	function R.row(name) for _, f in ipairs(R.rows()) do if ( f.row.name == name ) then return f end end end
	function R.creatorOff() return WrathppCreator and WrathppCreator.off end
	function R.problems()
		local out = {}
		if ( G.crashed ) then out[#out + 1] = "CRASH: "..G.crashed end
		for i = R.stockErrors + 1, #E.errors do local e = E.errors[i]; out[#out + 1] = "error in "..tostring(e.frame).." "..tostring(e.handler)..": "..tostring(e.message):match("^[^\n]*") end
		if ( R.creatorOff() ) then out[#out + 1] = "the creator went off: "..tostring(G.log[#G.log]) end
		return out
	end
	-- every frame on the screen: where it is, what it says (for a picture, and for what overlaps)
	function R.layout()
		local out = {}
		for _, f in ipairs(E.frames) do
			if ( f:IsVisible() and not f.__isScreen ) then
				local l, b, w, h = E.rect(f)
				if ( l and w > 0 and h > 0 ) then
					-- (for a picture of the screen: what is drawn, how, and over what; alpha and strata are the frame's and its parents')
					local alpha, strata, scripted, p = 1, nil, false, f
					local clip
					while ( p ) do
						alpha = alpha * (p.__alpha or 1)
						strata = strata or p.__strata
						if ( p.__name and p.__name:match("^Wrathpp") ) then scripted = true end
						-- inside a scroll frame only what the scroll frame shows is drawn
						if ( p.__scrollOwner and not clip ) then local cl, cb, cw, ch = E.rect(p.__scrollOwner); if ( cl ) then clip = { cl, cb, cw, ch } end end
						p = p.__parent
					end
					out[#out + 1] = { name = f.__name or "", kind = f.__kind, l = l, b = b, w = w, h = h, text = f.__text, enabled = f.__enabled, mouse = f.__mouse or (f.__scripts and (f.__scripts.OnClick or f.__scripts.OnMouseDown)) and true or false,
						parent = f.__parent and f.__parent.__name or "", file = f.__file, checked = f.__checked, strata = strata or "MEDIUM",
						coords = f.__coords, colour = f.__colour, vertex = f.__vertex, alpha = alpha, blend = f.__blend, layer = f.__layer, fontHeight = f.__fontHeight,
						justify = f.__justify, mine = scripted, desaturated = f.__desaturated, clip = clip }
				end
			end
		end
		return out
	end
	return R
end
