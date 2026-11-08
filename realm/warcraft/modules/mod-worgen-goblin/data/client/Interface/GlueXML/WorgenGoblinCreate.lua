-- The Worgen and Goblins (mod-worgen-goblin, from mod-worgoblin) on the character creation and selection
-- screens, on top of the game's own screen (mod-worgoblin's own screen files are the game's with
-- these few changes; they'd take the place of the others' changes, so they aren't used):
--  * Their icons, from a sheet of their own (UI-CharacterCreate-Worgoblin and -WorgoblinRound, cut out
--    of mod-worgoblin's race icons as the server is packaged): the game's sheet has no column left for
--    them (the allied races and the Skyborne have its free ones), so their buttons and the round icon
--    by the race's text show that sheet, and every other race's the game's.
--  * Their scenes' music and lights (their backgrounds are mod-worgoblin's, UI_Worgen and UI_Goblin):
--    the Humans' music for the Worgen, the Orcs' and Trolls' for the Goblins, as mod-worgoblin has it.
--  * More race buttons: the game's screen has ten, and the allied races' and the Skyborne's code make
--    it sixteen; with the Worgen and Goblins there are eighteen races (WorgenGoblinCreate.xml's
--    buttons, named as the screen looks for them where it hasn't a button by that number).
-- Their texts are in WorgenGoblinStrings.lua (mod-worgoblin's). The screen's layout and the races'
-- sides are the allied races' (AlliedRacesCreate.lua, read after this).

local BUTTONS = 18;
local highest = 0;
for i = 1, BUTTONS do
	local name = "CharacterCreateRaceButton"..i;
	if ( not _G[name] and _G["WorgenGoblinRaceButton"..i] ) then
		local extra = "WorgenGoblinRaceButton"..i;
		_G[name] = _G[extra];
		_G[name.."NormalTexture"] = _G[extra.."NormalTexture"];
		_G[name.."PushedTexture"] = _G[extra.."PushedTexture"];
		_G[name.."Text"] = _G[extra.."Text"];
		_G[name.."Shadow"] = _G[extra.."Shadow"];
		if ( CharacterCreateRaceButton1 ) then
			_G[name]:SetParent(CharacterCreateRaceButton1:GetParent());
		end
	end
	if ( _G[name] ) then
		highest = i;
	end
end
if ( highest > MAX_RACES ) then
	MAX_RACES = highest;
end

local SHEET = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Worgoblin";
local ROUND = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-WorgoblinRound";
local ICONS = {
	WORGEN_MALE = { 0, 1, 0, 0.25 }, GOBLIN_MALE = { 0, 1, 0.25, 0.5 },
	WORGEN_FEMALE = { 0, 1, 0.5, 0.75 }, GOBLIN_FEMALE = { 0, 1, 0.75, 1.0 },
};
local OURS = { WORGEN = true, GOBLIN = true };

for key, coords in pairs(ICONS) do
	RACE_ICON_TCOORDS[key] = coords;
end

-- The game's own sheets, as its buttons and icon have them before any race is shown.
local gameSheet = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races";
local gameRound = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound";
if ( CharacterCreateRaceButton1NormalTexture and CharacterCreateRaceButton1NormalTexture:GetTexture() ) then
	gameSheet = CharacterCreateRaceButton1NormalTexture:GetTexture();
end
if ( CharacterCreateRaceIcon and CharacterCreateRaceIcon:GetTexture() ) then
	gameRound = CharacterCreateRaceIcon:GetTexture();
end

local function gender()
	if ( GetSelectedSex() == (SEX_MALE or 2) ) then
		return "MALE";
	end
	return "FEMALE";
end

-- Each race button's sheet: theirs for the Worgen and Goblins, the game's for every other race.
local function SetSheets(...)
	local sex = gender();
	for i = 1, select("#", ...) / 3 do
		local file = strupper(select(i * 3 - 1, ...) or "");
		local coords = RACE_ICON_TCOORDS[file.."_"..sex];
		for _, part in ipairs({ "NormalTexture", "PushedTexture" }) do
			local texture = _G["CharacterCreateRaceButton"..i..part];
			if ( texture ) then
				texture:SetTexture(OURS[file] and SHEET or gameSheet);
				if ( coords ) then
					texture:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
				end
			end
		end
	end
end

local enumerateRaces = CharacterCreateEnumerateRaces;
function CharacterCreateEnumerateRaces(...)
	local ok, problem = pcall(enumerateRaces, ...);
	SetSheets(...);
	if ( not ok ) then
		error(problem, 0);
	end
end

-- The round icon by the race's text.
local function SetRound()
	if ( not CharacterCreateRaceIcon ) then
		return;
	end
	local _, file = GetNameForRace();
	file = strupper(file or "");
	local coords = RACE_ICON_TCOORDS[file.."_"..gender()];
	CharacterCreateRaceIcon:SetTexture(OURS[file] and ROUND or gameRound);
	if ( coords ) then
		CharacterCreateRaceIcon:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
	end
end

for _, name in ipairs({ "SetCharacterRace", "SetCharacterGender" }) do
	local original = _G[name];
	if ( original ) then
		_G[name] = function(...)
			local results = { original(...) };
			SetRound();
			return unpack(results);
		end
	end
end

-- Their scenes' music (the selection screen plays it again by the selected character's race) and
-- lights, and no glow, as mod-worgoblin has them.
if ( type(GlueAmbienceTracks) == "table" ) then
	GlueAmbienceTracks["WORGEN"] = GlueAmbienceTracks["WORGEN"] or GlueAmbienceTracks["HUMAN"] or "GlueScreenHuman";
	GlueAmbienceTracks["GOBLIN"] = GlueAmbienceTracks["GOBLIN"] or GlueAmbienceTracks["ORC"] or "GlueScreenOrcTroll";
end
if ( type(CharModelGlowInfo) == "table" ) then
	CharModelGlowInfo["WORGEN"] = CharModelGlowInfo["WORGEN"] or 0.0;
	CharModelGlowInfo["GOBLIN"] = CharModelGlowInfo["GOBLIN"] or 0.0;
end
if ( type(RaceLights) == "table" ) then
	RaceLights["GOBLIN"] = RaceLights["GOBLIN"] or RaceLights["ORC"];
end
