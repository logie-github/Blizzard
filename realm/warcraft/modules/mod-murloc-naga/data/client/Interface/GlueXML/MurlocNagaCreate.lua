-- SPDX-License-Identifier: GPL-3.0-or-later
-- The Murlocs and the Naga (mod-murloc-naga) on the character creation and selection screens. Loaded
-- after the game's own screens (the patch adds it to GlueXML.toc), before the other race modules'
-- screen code (their patches are read after this one):
--
--  * More race buttons: the game's screen has ten; MurlocNagaCreate.xml makes ten more, here given
--    the names the screen looks for (the others' code finds them there and leaves theirs unused).
--    Where they go is the allied races' and the Skyborne's code's (each side's races in two
--    columns, by the game's GetFactionForRace: the Murlocs the Alliance's, the Naga the Horde's).
--  * Their icons: the game's murloc head and murloc oracle, Warlord Kalithresh and Lady Vashj, on a
--    sheet of their own (UI-CharacterCreate-MurlocNaga and -MurlocNagaRound, made by the patch from
--    the game's icons), put on their buttons and by the race's name every frame the screen shows.
--  * Their backgrounds: a scene framed for their height. Murlocs stand as short as dwarves (the
--    Dwarves' scene); naga as tall as tauren (the Tauren's). On the selection screen, that scene's
--    music.
--  * Their text.

local SCENE = { MURLOC = "Dwarf", NAGA_ = "Tauren" };
local SHEET = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MurlocNaga";
local ROUND = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MurlocNagaRound";
local ICONS = {
	MURLOC_MALE = { 0, 1, 0, 0.25 }, NAGA__MALE = { 0, 1, 0.25, 0.5 },
	MURLOC_FEMALE = { 0, 1, 0.5, 0.75 }, NAGA__FEMALE = { 0, 1, 0.75, 1.0 },
};

local BUTTONS = 20;
local highest = 0;
for i = 1, BUTTONS do
	local name = "CharacterCreateRaceButton"..i;
	if ( not _G[name] and _G["MurlocNagaRaceButton"..i] ) then
		local extra = "MurlocNagaRaceButton"..i;
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

for key, coords in pairs(ICONS) do
	RACE_ICON_TCOORDS[key] = coords;
end

local function Sex()
	if ( GetSelectedSex() == (SEX_MALE or 2) ) then
		return "MALE";
	end
	return "FEMALE";
end

-- Their buttons' and the race's round icon's sheet (every other race's is left as it is).
function MurlocNaga_Icons()
	if ( not GetAvailableRaces ) then
		return;
	end
	local sex = Sex();
	local races = { GetAvailableRaces() };
	for i = 1, #races / 3 do
		local file = strupper(races[i * 3 - 1] or "");
		local coords = ICONS[file.."_"..sex];
		if ( coords ) then
			for _, part in ipairs({ "NormalTexture", "PushedTexture" }) do
				local texture = _G["CharacterCreateRaceButton"..i..part];
				if ( texture and texture.SetTexture ) then
					texture:SetTexture(SHEET);
					texture:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
				end
			end
		end
	end
	if ( CharacterCreateRaceIcon and GetNameForRace ) then
		local _, file = GetNameForRace();
		local coords = ICONS[strupper(file or "").."_"..sex];
		if ( coords ) then
			CharacterCreateRaceIcon:SetTexture(ROUND);
			CharacterCreateRaceIcon:SetTexCoord(coords[1], coords[2], coords[3], coords[4]);
		end
	end
end

local setBackgroundModel = SetBackgroundModel;
function SetBackgroundModel(model, name)
	return setBackgroundModel(model, SCENE[strupper(name or "")] or name);
end

-- Their scenes' music on the character selection screen (the screen plays it by the selected
-- character's own race, which the game's table hasn't for them), and their scenes' light and glow.
if ( type(GlueAmbienceTracks) == "table" ) then
	for race, scene in pairs(SCENE) do
		GlueAmbienceTracks[race] = GlueAmbienceTracks[strupper(scene)] or GlueAmbienceTracks["CHARACTERSELECT"] or "GlueScreenIntro";
	end
end
if ( type(CharModelGlowInfo) == "table" ) then
	for race, scene in pairs(SCENE) do
		CharModelGlowInfo[race] = CharModelGlowInfo[race] or CharModelGlowInfo[strupper(scene)];
	end
end
if ( type(RaceLights) == "table" ) then
	for race, scene in pairs(SCENE) do
		RaceLights[race] = RaceLights[race] or RaceLights[strupper(scene)];
	end
end

RACE_INFO_MURLOC = "Mrgl mrgl! Mrrrgl mrgl mrrgl. Mrglmrgl!|n|n(Murlocs have lived along Azeroth's shores for longer than anyone has kept count. Most are hostile to anything that walks on land. The village on the island off Auberdine is different: its elder has decided, for reasons he gurgles about at length, that the night elves across the water are friends. Mostly. Their things are still very shiny.)";
RACE_INFO_NAGA_ = "Once they were the Highborne of Queen Azshara's court, drowned when the Well of Eternity tore the world apart and remade in the deep. The naga served Azshara, and later Lady Vashj and Illidan.|n|nNot all of them. A small band of renegades, deserters from the Stormscale, now camps on an island off Darkshore's coast, hunted by their own kind and distrusted by the night elves. They will need allies to survive, and the Horde has always made room for those the world has thrown away.";

ABILITY_INFO_MURLOC1 = "- Amphibious: Breathe underwater, and swim 50% faster.";
ABILITY_INFO_MURLOC2 = "- Mrrgglll!: A terrible war-gurgle stuns nearby enemies for 2 sec.";
ABILITY_INFO_MURLOC3 = "- Slippery: Increases your chance to dodge by 1%.";
ABILITY_INFO_MURLOC4 = "- Starts at level 10, in a murloc village off Darkshore.";
ABILITY_INFO_NAGA_1 = "- Serpent's Grace: Breathe underwater, and swim 50% faster.";
ABILITY_INFO_NAGA_2 = "- Tail Sweep: Stuns nearby enemies for 2 sec.";
ABILITY_INFO_NAGA_3 = "- Scales of the Deep: Increases the armor you get from items by 5%.";
ABILITY_INFO_NAGA_4 = "- Starts at level 10, in the renegades' camp off Darkshore.";

-- The murlocs' choices' names (their ChrRaces row's hair token MURLOC; features, the game's FEATURES):
-- their hair styles are their fins' shapes, their hair colour the fins' colour, their faces their eyes'
-- colours (the face's label, the game's own for every other race, is set by race below).
HAIR_MURLOC_STYLE = "Fins";
HAIR_MURLOC_COLOR = "Fin Color";
MURLOC_FACE = "Eye Color";
-- The naga's (their hair token NAGA): the naga's own headdresses (a myrmidon's crown, a warlord's helm,
-- a sea witch's headdress) and their colours.
HAIR_NAGA_STYLE = "Headdress";
HAIR_NAGA_COLOR = "Headdress Color";

-- The face's label, "Eye Color" for a murloc: set where the game sets the hair's (each time the race,
-- the sex or the screen changes), the game's own put back for every other race.
local faceLabel;
local updateHairCustomization = CharacterCreate_UpdateHairCustomization;
function CharacterCreate_UpdateHairCustomization(...)
	if ( updateHairCustomization ) then
		updateHairCustomization(...);
	end
	local label = CharacterCustomizationButtonFrame2Text;
	if ( not label or not label.SetText or not GetHairCustomization ) then
		return;
	end
	faceLabel = faceLabel or label:GetText();
	if ( GetHairCustomization() == "MURLOC" ) then
		label:SetText(MURLOC_FACE);
	elseif ( faceLabel ) then
		label:SetText(faceLabel);
	end
end

MURLOC_DISABLED = "Murlocs can't be made on this realm.";
NAGA__DISABLED = "Naga can't be made on this realm.";
