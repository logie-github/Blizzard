-- The rig's game: the 3.3.5a client's character creation, ported from its decompiled source (WarcraftXL-Labs/client at
-- the commit wrathpp.env pins: CharacterCreation.cpp, CharacterCreation_Scripts.cpp, CharacterComponent.cpp,
-- ComponentUtils.cpp), working from the game's own tables (data/, made by tools/build_data.py). The functions the
-- creation screen's scripts call are defined as globals, as the client registers them, and Wrath++'s native mod's
-- (client-mod/wrathpp-native/src/Native.cpp) beside them.
--
-- The client reads the character being created without looking whether there is one; here such a read is a CRASH
-- (G.crash, an error no script's pcall is let to swallow), as it is in the game.
local G = { character = nil, races = {}, classes = {}, raceIndex = -1, selectedClassID = 0, prefs = {}, facing = 0, expansion = 2,
	prev = {}, loads = 0, created = nil, seed = 12345, log = {} }

local function crash(what)
	G.crashed = G.crashed or what
	error("RIG CRASH: "..what, 0)
end
G.crash = crash

-- Tables ------------------------------------------------------------------------------------------------------------------
function G.load(dir)
	local T = dofile(dir.."/tables.lua")
	G.T = T
	G.raceById, G.classById = {}, {}
	for _, r in ipairs(T.races) do G.raceById[r.id] = r end
	for i, c in ipairs(T.classes) do G.classById[c.id] = c; c.index = i end
	G.sections = {}
	for line in io.lines(dir.."/charsections.txt") do
		local race, sex, section, flags, variation, colour = line:match("(%d+) (%d+) (%d+) (%d+) (%d+) (%d+)")
		G.sections[#G.sections + 1] = { race = tonumber(race), sex = tonumber(sex), section = tonumber(section), flags = tonumber(flags), variation = tonumber(variation), colour = tonumber(colour) }
	end
	G.facial = {}
	local maxRace = 0
	for _, r in ipairs(T.races) do maxRace = math.max(maxRace, r.id) end
	for line in io.lines(dir.."/facialhair.txt") do
		local race, sex = line:match("(%d+) (%d+)")
		local k = tonumber(race) * 2 + tonumber(sex)
		G.facial[k] = (G.facial[k] or 0) + 1                               -- CountFacialFeatures
	end
	G.build(2 * maxRace + 2)
	G.initialize()
end

-- BuildComponentArray (ComponentUtils.cpp): sizes come from the table's rows in the order they are in, a run at a time.
function G.build(count)
	local lookup = {}
	for i = 0, count - 1 do lookup[i] = { [0] = { n = 0 }, [1] = { n = 0 }, [2] = { n = 0 }, [3] = { n = 0 }, [4] = { n = 0 } } end
	local recs = {}
	for _, r in ipairs(G.sections) do if ( r.section < 5 ) then recs[#recs + 1] = r end end
	local function list(race, sex, section) local l = lookup[race * 2 + sex]; if ( not l ) then crash("CharSections has race "..race..", past ChrRaces' highest") end; return l[section] end
	-- pass 1: variations of each run of a race, sex and section
	local vi = 0
	local race, sex, section = recs[1].race, recs[1].sex, recs[1].section
	for _, r in ipairs(recs) do
		if ( race ~= r.race or sex ~= r.sex or section ~= r.section ) then
			local l = list(race, sex, section); l.n = vi + 1; l.v = {}
			for i = 0, l.n - 1 do l.v[i] = { n = 0 } end
			vi = 0
		end
		if ( vi <= r.variation ) then vi = r.variation end
		race, sex, section = r.race, r.sex, r.section
	end
	do local l = list(race, sex, section); l.n = vi + 1; l.v = {}; for i = 0, l.n - 1 do l.v[i] = { n = 0 } end end
	-- pass 2: colours of each run of a race, sex, section and variation
	sex, race, section, vi = 0, 1, 0, 0
	local ci = 0
	local function close()
		local l = list(race, sex, section)
		if ( l.n > 0 ) then
			if ( vi >= l.n ) then crash("BuildComponentArray writes past its array: "..race.."/"..sex.." section "..section.." variation "..vi.." of "..l.n) end
			l.v[vi] = { n = ci + 1, c = {} }
		end
	end
	for _, r in ipairs(recs) do
		if ( race ~= r.race or sex ~= r.sex or section ~= r.section or vi ~= r.variation ) then close(); ci = 0 end
		if ( ci <= r.colour ) then ci = r.colour end
		race, sex, section, vi = r.race, r.sex, r.section, r.variation
	end
	close()
	-- pass 3: the rows put in
	for _, r in ipairs(recs) do
		local l = list(r.race, r.sex, r.section)
		if ( l.n > 0 and r.variation < l.n ) then
			local colours = l.v[r.variation]
			if ( colours.n > 0 and r.colour < colours.n ) then colours.c[r.colour] = r end
		end
	end
	G.lookup = lookup
end

-- ComponentUtils.cpp -------------------------------------------------------------------------------------------------------
local band = bit.band
local function flagsMatch(flags, selection)
	if ( selection == 0 ) then return band(flags, 0x1) ~= 0 and band(flags, 0xC) == 0 end
	if ( selection == 1 ) then return band(flags, 0x1) ~= 0 and band(flags, 0x14) ~= 0 and band(flags, 0x8) == 0 end
	if ( selection == 4 ) then return true end
	error("selection "..tostring(selection).." is not the creator's")
end
local function selectionOf(class) return class == 6 and 1 or 0 end            -- GetSelectionFromContext(COMPONENT_CONTEXT_0, class)
local function numVariations(race, sex, section) local l = G.lookup[race * 2 + sex][section]; if ( not l.v ) then return 0 end; return l.n end
local function numColors(race, sex, section, variation)
	local l = G.lookup[race * 2 + sex][section]
	if ( not l.v or variation >= l.n or l.n <= 0 or not l.v[variation].c ) then return 0 end
	return l.v[variation].n
end
local function rec(race, sex, section, variation, colour)
	if ( variation >= 0 ) then
		local l = G.lookup[race * 2 + sex][section]
		if ( variation < l.n and l.n ~= 0 and colour >= 0 ) then
			local n = l.v[variation].n
			if ( colour < n and n ~= 0 ) then return l.v[variation].c and l.v[variation].c[colour], true end
		end
	end
	return nil, false
end
G.rec, G.flagsMatch, G.numVariations, G.numColors = rec, flagsMatch, numVariations, numColors
local SKIN, FACE, FACIALHAIR, HAIR, UNDERWEAR = 0, 1, 2, 3, 4

-- CharacterComponent.cpp: the counts ------------------------------------------------------------------------------------------
local function getNumSkins(race, sex, class)
	local sel, n, count = selectionOf(class), numColors(race, sex, SKIN, 0), 0
	for i = 0, n - 1 do local r = rec(race, sex, SKIN, 0, i); if ( r and flagsMatch(r.flags, sel) ) then count = count + 1 end end
	return count
end
local function getNumHairStylesForColor(race, sex, class, hairColor)
	local sel, n, count = selectionOf(class), numVariations(race, sex, HAIR), 0
	for i = 0, n - 1 do local r = rec(race, sex, HAIR, i, hairColor); if ( r and flagsMatch(r.flags, sel) ) then count = count + 1 end end
	return count
end
local function getNumHairColorsForStyle(race, sex, class, hairStyle)
	local sel, n, count = selectionOf(class), numColors(race, sex, HAIR, hairStyle), 0
	for i = 0, n - 1 do local r = rec(race, sex, HAIR, hairStyle, i); if ( r and flagsMatch(r.flags, sel) ) then count = count + 1 end end
	return count
end
local function getNumFacesForSkin(race, sex, class, skin)
	local sel, n, count = selectionOf(class), numVariations(race, sex, FACE), 0
	for i = 0, n - 1 do local r = rec(race, sex, FACE, i, skin); if ( r and flagsMatch(r.flags, sel) ) then count = count + 1 end end
	return count
end
local function getNumFacialFeaturesForHairColor(race, sex, class, hairColor)
	local sel, n = selectionOf(class), numVariations(race, sex, FACIALHAIR)
	if ( n == 0 ) then return G.facial[race * 2 + sex] or 0 end
	local count = 0
	for i = 0, n - 1 do local r = rec(race, sex, FACIALHAIR, i, hairColor); if ( r and flagsMatch(r.flags, sel) ) then count = count + 1 end end
	return count
end
G.counts = { getNumSkins, getNumFacesForSkin, getNumHairStylesForColor, getNumHairColorsForStyle, getNumFacialFeaturesForHairColor }
local function nth(n, section, variationFixed, colourFixed, race, sex, index, sel)
	-- the index-th row that matches, along the variations (colourFixed given) or the colours (variationFixed given)
	local found = 0
	for i = 0, n - 1 do
		local r = rec(race, sex, section, variationFixed or i, colourFixed or i)
		if ( r and flagsMatch(r.flags, sel) ) then
			if ( index == found ) then return variationFixed and r.colour or r.variation end
			found = found + 1
		end
	end
	return -1
end
local function getSkinColor(race, sex, index, sel) return nth(numColors(race, sex, SKIN, 0), SKIN, 0, nil, race, sex, index, sel) end
local function getHairVariation(race, sex, hairColor, index, sel) return nth(numVariations(race, sex, HAIR), HAIR, nil, hairColor, race, sex, index, sel) end
local function getHairColor(race, sex, hairStyle, index, sel) return nth(numColors(race, sex, HAIR, hairStyle), HAIR, hairStyle, nil, race, sex, index, sel) end
local function getFaceVariation(race, sex, skin, index, sel) return nth(numVariations(race, sex, FACE), FACE, nil, skin, race, sex, index, sel) end
local function getNthFacialFeatureIndex(race, sex, class, hairColor, facialHair, index, sel)
	local _, found = rec(race, sex, FACIALHAIR, facialHair, hairColor)
	if ( not found ) then
		if ( index < (G.facial[race * 2 + sex] or 0) ) then return index end
		return -1
	end
	local count = getNumFacialFeaturesForHairColor(race, sex, class, hairColor)
	if ( count <= 0 ) then return -1 end
	local matched = 0
	for i = 0, count - 1 do
		local r = rec(race, sex, FACIALHAIR, i, hairColor)
		if ( r and flagsMatch(r.flags, sel) ) then
			if ( index == matched ) then return r.variation end
			matched = matched + 1
		end
	end
	return -1
end

-- the client's own dice (CRandom::dice_): any generator will do; this one is repeatable
local function dice(n)
	G.seed = (G.seed * 1103515245 + 12345) % 2147483648
	return math.floor(G.seed / 65536) % n
end
G.dice = dice

-- The character's own moves (CCharacterComponent::SetNext..., SetPrev..., SetRandom...) -------------------------------------
local function validSkin(P, skin, sel)
	local f, s, u = rec(P.race, P.sex, FACE, P.face, skin), rec(P.race, P.sex, SKIN, 0, skin), rec(P.race, P.sex, UNDERWEAR, 0, skin)
	return s and flagsMatch(s.flags, sel) and f and flagsMatch(f.flags, sel) and u and flagsMatch(u.flags, sel), s
end
local function stepSkin(P, delta)
	local sel, n = selectionOf(P.class), numColors(P.race, P.sex, SKIN, 0)
	if ( n <= 0 ) then return false end
	local skin = (P.skin + delta) % n
	if ( skin == P.skin ) then return false end
	while ( true ) do
		local ok, s = validSkin(P, skin, sel)
		if ( ok ) then P.skin = s.colour; return true end
		skin = (skin + delta) % n
		if ( skin == P.skin ) then return false end
	end
end
local function stepHairColor(P, delta)
	local sel, n = selectionOf(P.class), numColors(P.race, P.sex, HAIR, P.hairStyle)
	if ( n <= 0 ) then return false end
	local colour = (P.hairColor + delta) % n
	if ( colour == P.hairColor ) then return false end
	while ( true ) do
		local r = rec(P.race, P.sex, HAIR, P.hairStyle, colour)
		if ( r and flagsMatch(r.flags, sel) ) then P.hairColor = r.colour; return true end
		colour = (colour + delta) % n
		if ( colour == P.hairColor ) then return false end
	end
end
local function stepFace(P, delta, colourOffset)
	local sel, n = selectionOf(P.class), numVariations(P.race, P.sex, FACE)
	if ( n <= 0 ) then return false end
	local face = (P.face + delta) % n
	if ( face == P.face ) then return false end
	local skin
	while ( true ) do
		local colours = numColors(P.race, P.sex, FACE, face)
		local matched = false
		local i = 0
		while ( i < colours ) do
			skin = (i + colourOffset) % colours
			local f, s, u = rec(P.race, P.sex, FACE, face, skin), rec(P.race, P.sex, SKIN, 0, skin), rec(P.race, P.sex, UNDERWEAR, 0, skin)
			if ( f and flagsMatch(f.flags, sel) and s and flagsMatch(s.flags, sel) and u and flagsMatch(u.flags, sel) ) then matched = true; break end
			i = skin + 1                                                            -- (the client's own loop: i = skinID + 1)
		end
		if ( matched ) then break end
		face = (face + delta) % n
		if ( face == P.face ) then return false end
	end
	local f, s, u = rec(P.race, P.sex, FACE, face, P.skin), rec(P.race, P.sex, SKIN, 0, P.skin), rec(P.race, P.sex, UNDERWEAR, 0, P.skin)
	if ( not f or not flagsMatch(f.flags, sel) or not s or not flagsMatch(s.flags, sel) or not u or not flagsMatch(u.flags, sel) ) then P.skin = skin end
	P.face = face
	return true
end
local function stepHairStyle(P, delta)
	local sel, n = selectionOf(P.class), numVariations(P.race, P.sex, HAIR)
	if ( n <= 0 ) then return false end
	local style = (P.hairStyle + delta) % n
	if ( style == P.hairStyle ) then return false end
	local r
	while ( true ) do
		local colours, colour = numColors(P.race, P.sex, HAIR, style), 0
		while ( colour < colours ) do
			r = rec(P.race, P.sex, HAIR, style, colour)
			if ( r and flagsMatch(r.flags, sel) ) then break end
			colour = colour + 1
		end
		if ( colour < colours ) then break end
		style = (style + delta) % n
		if ( style == P.hairStyle ) then return false end
	end
	local keep = rec(P.race, P.sex, HAIR, style, P.hairColor)
	if ( keep and flagsMatch(keep.flags, sel) ) then P.hairStyle = keep.variation; return true end
	P.hairColor = r.colour
	P.hairStyle = r.variation
	local facial = getNthFacialFeatureIndex(P.race, P.sex, P.class, P.hairColor, P.facialHair, 0, sel)
	if ( facial >= 0 ) then P.facialHair = facial end
	return true
end
local function stepFacialFeature(P, delta)
	local sel = selectionOf(P.class)
	local _, found = rec(P.race, P.sex, FACIALHAIR, P.facialHair, P.hairColor)
	if ( not found ) then
		local count = G.facial[P.race * 2 + P.sex] or 0
		local facial = P.facialHair + delta
		if ( delta > 0 ) then P.facialHair = (facial >= count) and 0 or facial else P.facialHair = (facial >= 0) and facial or count - 1 end
		return true
	end
	-- a race and sex whose facial hair has rows of its own in the table (the game's own models: the Blood Elf man)
	local n = numVariations(P.race, P.sex, FACIALHAIR)
	if ( n <= 0 ) then return false end
	local facial = (P.facialHair + delta) % n
	if ( facial == P.facialHair ) then return false end
	local r
	while ( true ) do
		local colours, colour = numColors(P.race, P.sex, FACIALHAIR, facial), 0
		while ( colour < colours ) do
			r = rec(P.race, P.sex, FACIALHAIR, facial, colour)
			if ( r and flagsMatch(r.flags, sel) ) then break end
			colour = colour + 1
		end
		if ( colour < colours ) then break end
		facial = (facial + delta) % n
		if ( facial == P.facialHair ) then return false end
	end
	local keep = rec(P.race, P.sex, FACIALHAIR, facial, P.hairColor)
	if ( delta < 0 and not keep ) then crash("SetPrevFacialFeature reads a facial hair row that is not there (variation "..facial..", hair colour "..P.hairColor..")") end
	if ( keep and flagsMatch(keep.flags, sel) ) then P.facialHair = keep.variation
	else P.hairColor = r.colour; P.facialHair = r.variation end
	return true
end
local function randomSkin(P) local sel = selectionOf(P.class); local n = getNumSkins(P.race, P.sex, P.class); local s = getSkinColor(P.race, P.sex, n > 0 and dice(n) or 0, sel); if ( s < 0 ) then return false end; P.skin = s; return true end
local function randomHairStyle(P) local sel = selectionOf(P.class); local n = getNumHairStylesForColor(P.race, P.sex, P.class, P.hairColor); local s = getHairVariation(P.race, P.sex, P.hairColor, n > 0 and dice(n) or 0, sel); if ( s < 0 ) then return false end; P.hairStyle = s; return true end
local function randomHairColor(P) local sel = selectionOf(P.class); local n = getNumHairColorsForStyle(P.race, P.sex, P.class, P.hairStyle); local s = getHairColor(P.race, P.sex, P.hairStyle, n > 0 and dice(n) or 0, sel); if ( s < 0 ) then return false end; P.hairColor = s; return true end
local function randomFace(P) local sel = selectionOf(P.class); local n = getNumFacesForSkin(P.race, P.sex, P.class, P.skin); local s = getFaceVariation(P.race, P.sex, P.skin, n > 0 and dice(n) or 0, sel); if ( s < 0 ) then return false end; P.face = s; return true end
local function randomFacialFeature(P) local sel = selectionOf(P.class); local n = getNumFacialFeaturesForHairColor(P.race, P.sex, P.class, P.hairColor); local s = getNthFacialFeatureIndex(P.race, P.sex, P.class, P.hairColor, P.facialHair, n > 0 and dice(n) or 0, sel); if ( s < 0 ) then return false end; P.facialHair = s; return true end

-- ComponentValidate..., ValidateComponentData
local function validBase(race, sex, section, class, colour, variation)
	if ( variation < 0 ) then return false end
	local l = G.lookup[race * 2 + sex][section]
	if ( variation >= l.n or l.n == 0 or colour < 0 ) then return false end
	local colours = l.v[variation]
	if ( colour >= colours.n or colours.n == 0 or not colours.c or not colours.c[colour] ) then return false end
	return flagsMatch(colours.c[colour].flags, selectionOf(class))
end
local function validate(P)
	local sel = selectionOf(P.class)
	if ( not validBase(P.race, P.sex, SKIN, P.class, P.skin, 0) ) then
		local n = getNumSkins(P.race, P.sex, P.class)
		P.skin = n <= 0 and 0 or getSkinColor(P.race, P.sex, P.skin % n, sel)
	end
	if ( not validBase(P.race, P.sex, FACE, P.class, P.skin, P.face) ) then
		local n = getNumFacesForSkin(P.race, P.sex, P.class, P.skin)
		P.face = n <= 0 and 0 or getFaceVariation(P.race, P.sex, P.skin, P.face % n, sel)
	end
	if ( not validBase(P.race, P.sex, HAIR, P.class, P.hairColor, P.hairStyle) ) then
		local n = getNumHairStylesForColor(P.race, P.sex, P.class, P.hairColor)
		if ( n > 0 ) then P.hairStyle = getHairVariation(P.race, P.sex, P.hairColor, P.hairStyle % n, sel)
		else
			local variations, colours, valid = numVariations(P.race, P.sex, HAIR), {}, 0
			for i = 0, variations - 1 do colours[i] = getNumHairColorsForStyle(P.race, P.sex, P.class, i); if ( colours[i] > 0 ) then valid = valid + 1 end end
			if ( valid <= 0 ) then P.hairColor, P.hairStyle = 0, 0
			else
				for i = 0, variations - 1 do if ( colours[i] > 0 and P.hairStyle % valid == i ) then P.hairStyle = i; break end end
				if ( not colours[P.hairStyle] or colours[P.hairStyle] == 0 ) then crash("ValidateComponentData divides by a hair style's zero colours (style "..P.hairStyle..")") end
				P.hairColor = getHairColor(P.race, P.sex, P.hairStyle, P.hairColor % colours[P.hairStyle], sel)
			end
		end
	end
	-- ComponentValidateFacialFeature
	local okFacial
	local index = P.race * 2 + P.sex
	if ( P.facialHair < 0 or P.facialHair > (G.facial[index] or 0) ) then okFacial = false
	else
		local l = G.lookup[index][FACIALHAIR]
		if ( P.facialHair >= l.n or l.n == 0 or P.hairColor < 0 ) then okFacial = true
		else
			local colours = l.v[P.facialHair]
			if ( P.hairColor >= colours.n or colours.n == 0 ) then okFacial = true
			elseif ( not colours.c[P.hairColor] ) then okFacial = false
			else okFacial = flagsMatch(colours.c[P.hairColor].flags, sel) end
		end
	end
	if ( not okFacial ) then
		local n = getNumFacialFeaturesForHairColor(P.race, P.sex, P.class, P.hairColor)
		P.facialHair = n <= 0 and 0 or getNthFacialFeatureIndex(P.race, P.sex, P.class, P.hairColor, P.facialHair, P.facialHair % n, sel)
	end
end

-- CharacterCreation.cpp -------------------------------------------------------------------------------------------------------
function G.initialize()
	G.races = {}
	for faction = 0, 1 do
		for _, race in ipairs(G.T.races) do
			if ( band(race.flags, 0x1) == 0 and race.factionGroup ) then
				for _, group in ipairs(G.T.factionGroups) do
					if ( group.mask ~= 0 and band(bit.lshift(1, group.mask), race.factionGroup) ~= 0 and group.internal:lower() == (faction == 0 and "alliance" or "horde") ) then
						G.races[#G.races + 1] = race.id
					end
				end
			end
		end
	end
end
local function C() if ( not G.character ) then crash("the game read the character being created, and there is none") end; return G.character end
local function startLoad() G.loads = G.loads + 1 end
local function dress() local P = C(); P.dressed = true; G.dresses = (G.dresses or 0) + 1 end
G.Dress = dress
local function calcClasses(race)
	G.classes = {}
	for _, pair in ipairs(G.T.baseInfo) do if ( pair[1] == race ) then G.classes[#G.classes + 1] = G.classById[pair[2]] end end
end
local function isRaceClassValid(race, class)
	for _, pair in ipairs(G.T.baseInfo) do if ( pair[1] == race and pair[2] == class ) then return true end end
	return false
end
local function initCharacterComponents(data, randomize)
	if ( not G.raceById[data.race] ) then return end
	local P = { race = data.race, sex = data.sex, class = data.class or 0, hairColor = data.hairColor or 0, skin = data.skin or 0, face = data.face or 0,
		facialHair = data.facialHair or 0, hairStyle = data.hairStyle or 0 }
	G.character = P
	if ( randomize ) then randomSkin(P); randomHairColor(P); randomHairStyle(P); randomFace(P); randomFacialFeature(P) end
	G.prev = { skin = P.skin, face = P.face, hairColor = P.hairColor, hairStyle = P.hairStyle, facialHair = P.facialHair }
	dress()
end
local function getRandomClassID()
	local classes = {}
	for _, c in ipairs(G.classes) do if ( G.expansion >= c.expansion ) then classes[#classes + 1] = c.id end end
	if ( #classes <= 0 ) then return 0 end
	return classes[dice(#classes) + 1]
end
local function isClassAvailable(class) for _, c in ipairs(G.classes) do if ( c.id == class ) then return true end end; return false end
local function setSelectedClass(class)
	if ( not isClassAvailable(class) ) then return end
	G.selectedClassID = class
	local P = C()
	local data = { race = P.race, sex = P.sex, class = class, skin = P.skin, hairStyle = P.hairStyle, hairColor = P.hairColor, facialHair = P.facialHair, face = P.face }
	validate(data)
	initCharacterComponents(data, false)
	dress(); startLoad()
end
local function prefsOf(race, sex) G.prefs[race] = G.prefs[race] or {}; return G.prefs[race][sex] end
local function savePrefs()
	local P = C()
	local race = G.races[G.raceIndex + 1]
	if ( not race ) then crash("SetSelectedRace/Sex reads m_races["..G.raceIndex.."]") end
	G.prefs[race] = G.prefs[race] or {}
	G.prefs[race][P.sex] = { race = P.race, sex = P.sex, class = P.class, hairColor = P.hairColor, skin = P.skin, face = P.face, facialHair = P.facialHair, hairStyle = P.hairStyle }
end
local function setSelectedSex(sex)
	local P = C()
	if ( sex >= 3 or sex == P.sex ) then return end
	savePrefs()
	local class = G.selectedClassID
	local saved = prefsOf(G.races[G.raceIndex + 1], sex)
	if ( saved ) then
		local data = { race = saved.race, sex = saved.sex, class = class, hairColor = saved.hairColor, skin = saved.skin, face = saved.face, facialHair = saved.facialHair, hairStyle = saved.hairStyle }
		validate(data); initCharacterComponents(data, false)
	else
		initCharacterComponents({ race = P.race, sex = sex, class = class }, true)
	end
	startLoad()
end
local function setSelectedRace(raceIndex)
	if ( raceIndex < 0 or raceIndex >= #G.races or raceIndex == G.raceIndex ) then return end
	local P = C()
	savePrefs()
	G.raceIndex = raceIndex
	local saved = prefsOf(G.races[raceIndex + 1], P.sex)
	if ( saved ) then
		local data = { race = saved.race, sex = saved.sex, hairColor = saved.hairColor, skin = saved.skin, face = saved.face, facialHair = saved.facialHair, hairStyle = saved.hairStyle }
		calcClasses(data.race)
		local class = G.selectedClassID
		if ( not isRaceClassValid(data.race, class) ) then class = getRandomClassID(); G.selectedClassID = class end
		data.class = class
		validate(data); initCharacterComponents(data, false)
	else
		local data = { sex = P.sex, race = G.races[raceIndex + 1] }
		calcClasses(data.race)
		if ( not isRaceClassValid(data.race, G.selectedClassID) ) then setSelectedClass(getRandomClassID()) end
		data.class = G.selectedClassID
		initCharacterComponents(data, true)
	end
	dress(); startLoad()
end
local function resetCharCustomizeInfo()
	if ( not G.customizeFrame ) then return end
	-- GetRandomRaceAndSex
	local data = { sex = dice(2) }
	repeat
		data.race = G.races[(#G.races > 0 and dice(#G.races) or 0) + 1]
	until G.raceById[data.race].expansion <= G.expansion
	if ( G.forceFirst ) then data.race, data.sex = G.forceFirst.race, G.forceFirst.sex end      -- (the rig: a start that is asked for)
	calcClasses(data.race)
	initCharacterComponents(data, true)
	setSelectedClass(G.forceFirst and G.forceFirst.class or getRandomClassID())
	G.raceIndex = -1
	for i, id in ipairs(G.races) do if ( id == G.character.race ) then G.raceIndex = i - 1; break end end
	startLoad()
end

-- The script functions (CharacterCreation_Scripts.cpp), as globals -------------------------------------------------------------
local SCRIPT_SEX = { [0] = 2, [1] = 3, [2] = 1 }                                -- g_scriptSexIndex: a man 2, a woman 3
local function raceName(r, sex) if ( not r ) then return nil end; return (sex == 1 and r.nameFemale ~= "" and r.nameFemale) or (sex == 0 and r.nameMale ~= "" and r.nameMale) or r.name end
local function className(c, sex) return (sex == 1 and c.nameFemale ~= "" and c.nameFemale) or (sex == 0 and c.nameMale ~= "" and c.nameMale) or c.name end
local function number(v, usage) if ( type(v) ~= "number" and not (type(v) == "string" and tonumber(v)) ) then error(usage, 3) end; return tonumber(v) end

function G.define()
	function SetCharCustomizeFrame(name) G.customizeFrame = _G[name]; if ( not G.customizeFrame ) then error("SetCharCustomizeFrame: no frame "..tostring(name), 2) end end
	function ResetCharCustomize() resetCharCustomizeInfo() end
	function GetNameForRace() local P = C(); local r = G.raceById[P.race]; local name = raceName(r, P.sex); if ( r and name ) then return name, r.file end; return nil, nil end
	function GetFactionForRace(index)
		index = number(index, "Usage: GetFactionForRace(index)") - 1
		local r = G.raceById[G.races[index + 1] or 0]
		if ( r and r.factionGroup ) then
			for _, group in ipairs(G.T.factionGroups) do
				if ( group.mask ~= 0 and band(bit.lshift(1, group.mask), r.factionGroup) ~= 0 ) then return group.name, group.internal end
			end
		end
		return nil, nil
	end
	function GetAvailableRaces()
		local P = C()
		local out = {}
		for _, id in ipairs(G.races) do
			local r = G.raceById[id]
			out[#out + 1] = raceName(r, P.sex); out[#out + 1] = r.file; out[#out + 1] = (G.expansion >= r.expansion) and 1 or 0
		end
		return unpack(out, 1, #G.races * 3)
	end
	function GetAvailableClasses()
		local P = C()
		local out = {}
		for _, c in ipairs(G.T.classes) do out[#out + 1] = className(c, P.sex); out[#out + 1] = c.file; out[#out + 1] = (G.expansion >= c.expansion) and 1 or 0 end
		return unpack(out, 1, #G.T.classes * 3)
	end
	function GetClassesForRace()
		local P = C()
		local out = {}
		for _, c in ipairs(G.classes) do out[#out + 1] = className(c, P.sex); out[#out + 1] = c.file; out[#out + 1] = (G.expansion >= c.expansion) and 1 or 0 end
		return unpack(out, 1, #G.classes * 3)
	end
	function GetHairCustomization() local r = G.raceById[G.races[G.raceIndex + 1] or 0]; return r and r.hair or "NORMAL" end
	function GetFacialHairCustomization()
		local r = G.raceById[G.races[G.raceIndex + 1] or 0]
		if ( r ) then return r.facial[C().sex + 1] end
		return "NORMAL"
	end
	function GetSelectedRace() return G.raceIndex + 1 end
	function GetSelectedSex() return SCRIPT_SEX[C().sex] end
	function GetSelectedClass()
		local c = G.classById[G.selectedClassID]
		if ( not c ) then return end
		return className(c, C().sex), c.file, c.index, false, false, true
	end
	function SetSelectedRace(index) setSelectedRace(number(index, "Usage: SetSelectedRace(index)") - 1) end
	function SetSelectedSex(sex)
		sex = number(sex, "Usage: SetSelectedSex(index)")
		for i = 0, 2 do if ( sex == SCRIPT_SEX[i] ) then setSelectedSex(i) end end
	end
	function SetSelectedClass(index)
		index = number(index, "Usage: SetSelectedClass(index)")
		local c = G.T.classes[index]
		if ( not c ) then crash("SetSelectedClass("..tostring(index).."): the client reads a class record that is not there") end
		setSelectedClass(c.id)
	end
	function IsRaceClassValid(raceIndex, classIndex)
		raceIndex, classIndex = number(raceIndex, "Usage: IsRaceClassValid(raceIndex, classIndex)"), number(classIndex, "Usage: IsRaceClassValid(raceIndex, classIndex)")
		local c = G.T.classes[classIndex]
		if ( not c ) then return end
		if ( isRaceClassValid(G.races[raceIndex] or 0, c.id) ) then return 1 end
		return nil
	end
	function CycleCharCustomization(index, delta)
		if ( type(index) ~= "number" or type(delta) ~= "number" ) then error("Usage: CycleCharCustomization(index, delta)", 2) end
		index, delta = math.floor(index) - 1, (delta < 0 and math.ceil(delta) or math.floor(delta))
		if ( delta == 0 ) then return end
		local P = C()
		local d = delta > 0 and 1 or -1
		if ( index == 0 ) then stepSkin(P, d); G.prev.skin = P.skin; startLoad(); return
		elseif ( index == 1 ) then stepFace(P, d, G.prev.skin)
		elseif ( index == 2 ) then stepHairStyle(P, d)
		elseif ( index == 3 ) then stepHairColor(P, d)
		elseif ( index == 4 ) then stepFacialFeature(P, d) end
		startLoad()
	end
	function RandomizeCharCustomization()
		local P = C()
		randomSkin(P); randomFace(P); randomHairColor(P); randomHairStyle(P); randomFacialFeature(P)
		G.prev = { skin = P.skin, face = P.face, hairColor = P.hairColor, hairStyle = P.hairStyle, facialHair = P.facialHair }
		dress(); startLoad()
	end
	function GetCharacterCreateFacing() return G.facing * 57.29578 end
	function SetCharacterCreateFacing(degrees)
		if ( type(degrees) ~= "number" ) then error("Usage: SetCharacterCreateFacing(degrees)", 2) end
		G.facing = degrees * 0.017453292
		C()                                                                           -- SetCharacterFacing reads the character's model
		return 1
	end
	function GetCreateBackgroundModel()
		if ( G.selectedClassID == 6 ) then return G.classById[6].file end
		local race = C().race
		if ( race == 7 ) then race = 3 elseif ( race == 8 ) then race = 2 end
		local r = G.raceById[race]
		return r and r.file or ""
	end
	function SetCharCustomizeBackground() end
	function UpdateCustomizationBackground() setSelectedRace(G.raceIndex) end
	function UpdateCustomizationScene() C() end
	function GetRandomName() return "Rigname" end
	function CreateCharacter(name)
		local P = C()
		-- CHARACTER_CREATE_INFO: each number goes as a byte
		for _, k in ipairs({ "skin", "face", "hairStyle", "hairColor", "facialHair" }) do
			if ( P[k] > 255 ) then crash("CreateCharacter sends "..k.." "..P[k].." as a byte") end
		end
		G.created = { name = name, race = P.race, sex = P.sex, class = G.selectedClassID, skin = P.skin, face = P.face, hairStyle = P.hairStyle, hairColor = P.hairColor, facialHair = P.facialHair }
	end
	function CustomizeExistingCharacter() error("the rig has no existing character to customize") end
	function PaidChange_GetName() return C() and "" end
	function PaidChange_GetCurrentRaceIndex() return -1 end
	function PaidChange_GetCurrentClassIndex() return -1 end
	function IsRaceClassRestricted() return nil end

	-- Wrath++'s native mod (Native.cpp)
	function WrathPP_GetCustomization(i)
		if ( type(i) ~= "number" or i < 1 or i > 5 ) then error("WrathPP_GetCustomization(i): i is 1 to 5", 2) end
		local P = G.character
		if ( not P ) then return end
		i = math.floor(i)
		if ( i == 1 ) then return P.skin + 1, getNumSkins(P.race, P.sex, P.class) end
		if ( i == 2 ) then return P.face + 1, getNumFacesForSkin(P.race, P.sex, P.class, P.skin) end
		if ( i == 3 ) then return P.hairStyle + 1, getNumHairStylesForColor(P.race, P.sex, P.class, P.hairColor) end
		if ( i == 4 ) then return P.hairColor + 1, getNumHairColorsForStyle(P.race, P.sex, P.class, P.hairStyle) end
		return P.facialHair + 1, getNumFacialFeaturesForHairColor(P.race, P.sex, P.class, P.hairColor)
	end
	function WrathPP_SetCustomization(i, n)
		if ( type(i) ~= "number" or i < 1 or i > 5 or type(n) ~= "number" ) then error("WrathPP_SetCustomization(i, n): i is 1 to 5, n a choice from 1", 2) end
		local P = G.character
		if ( not P ) then return end
		local _, count = WrathPP_GetCustomization(i)
		local value = math.floor(n) - 1
		if ( value < 0 or value >= count ) then return end
		local key = ({ "skin", "face", "hairStyle", "hairColor", "facialHair" })[math.floor(i)]
		P[key] = value
		return true
	end
	function WrathPP_GetCreating()
		local P = G.character
		if ( not P ) then return end
		return P.race, P.sex, P.class
	end
	function WrathPP_SetGear(on)
		if ( type(on) ~= "boolean" ) then error("WrathPP_SetGear(on): on is true or false", 2) end
		local P = G.character
		if ( not P ) then return end
		if ( on ) then dress() else P.dressed = false end
		return true
	end
	G.screen = nil
	function WrathPP_SetScreen(text) if ( type(text) ~= "string" ) then error("WrathPP_SetScreen(text): text is a string", 2) end; G.screen = text; G.screens = (G.screens or 0) + 1; return true end
	function WrathPP_Log(text) if ( type(text) ~= "string" ) then error("WrathPP_Log(text): text is a string", 2) end; G.log[#G.log + 1] = text end
	function WrathPP_NativeVersion() return "0.4.0" end
end

return G
