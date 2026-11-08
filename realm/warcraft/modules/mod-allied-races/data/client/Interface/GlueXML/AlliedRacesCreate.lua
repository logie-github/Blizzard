-- SPDX-License-Identifier: GPL-3.0-or-later
-- The void elves, nightborne, Lightforged Draenei and Zandalari Trolls (mod-allied-races) on the character creation and selection
-- screens. Loaded after the game's own screens (the patch adds it to GlueXML.toc), before
-- mod-skyborne's SkyborneCreate.lua when that patch is in (it reads this one's archive):
--
--  * More race buttons: the game's screen has ten (CharacterCreateRaceButton1-10);
--    AlliedRacesCreate.xml makes six more, here given the names the screen looks for, where it
--    hasn't a button by that number already (another patch's screen may have more).
--  * Where they go: after the screen lays out its races, each side's in two columns (the
--    Alliance's left, the Horde's right), two to a row from the top (the Skyborne's screen lays
--    them out the same way, after this).
--  * Their icons: their portraits in the free columns of the race icons (the patch paints them
--    there: data/client/icons).
--  * Their backgrounds: their kin's, whose height their models are made (tools/scale.py): the
--    Blood Elves' for the void elves, the Night Elves' for the nightborne, the Draenei's for the
--    Lightforged, the Trolls' for the Zandalari: the Orcs' (3.3.5's trolls have no scene of their
--    own, Interface\Glues\Models has no UI_Troll, and the music table no TROLL: a Zandalari sent
--    there had a black screen, a missing model's cube and PlayGlueAmbience's usage error). Each
--    scene's camera is framed for its own race's height, so each looks as its kin does there (the
--    Draenei's showed the void elves small, the Forsaken's cut off the nightborne's heads). On the
--    selection screen, their kin's music too.
--  * Their text.

local ALLIED = { VOIDELF = "BloodElf", NIGHTBORNE = "NightElf", LIGHTFORGEDDRAENEI = "Draenei", ZANDALARITROLL = "Orc" };

RACE_ICON_TCOORDS["VOIDELF_MALE"]      = { 0.875, 1.0, 0, 0.25 };
RACE_ICON_TCOORDS["NIGHTBORNE_MALE"]   = { 0.875, 1.0, 0.25, 0.5 };
RACE_ICON_TCOORDS["VOIDELF_FEMALE"]    = { 0.875, 1.0, 0.5, 0.75 };
RACE_ICON_TCOORDS["NIGHTBORNE_FEMALE"] = { 0.875, 1.0, 0.75, 1.0 };
RACE_ICON_TCOORDS["LIGHTFORGEDDRAENEI_MALE"]   = { 0.625, 0.75, 0, 0.25 };
RACE_ICON_TCOORDS["ZANDALARITROLL_MALE"]       = { 0.625, 0.75, 0.25, 0.5 };
RACE_ICON_TCOORDS["LIGHTFORGEDDRAENEI_FEMALE"] = { 0.625, 0.75, 0.5, 0.75 };
RACE_ICON_TCOORDS["ZANDALARITROLL_FEMALE"]     = { 0.625, 0.75, 0.75, 1.0 };

local highest = 0;
for i = 1, 16 do
	local name = "CharacterCreateRaceButton"..i;
	if ( not _G[name] and _G["AlliedRaceButton"..i] ) then
		local extra = "AlliedRaceButton"..i;
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

-- Each side's races in two columns, the Alliance's on the left and the Horde's on the right, two to
-- a row from the top in the screen's order. The side is the game's (GetFactionForRace), or the
-- race's own where the game gives none.
local SIDES = { HUMAN = "Alliance", DWARF = "Alliance", NIGHTELF = "Alliance", GNOME = "Alliance", DRAENEI = "Alliance",
	WORGEN = "Alliance", SKYBORNEA = "Alliance", VOIDELF = "Alliance", LIGHTFORGEDDRAENEI = "Alliance",
	ORC = "Horde", SCOURGE = "Horde", TAUREN = "Horde", TROLL = "Horde", BLOODELF = "Horde", GOBLIN = "Horde",
	SKYBORNEH = "Horde", NIGHTBORNE = "Horde", ZANDALARITROLL = "Horde" };
local COLUMNS = { Alliance = { -90, -46 }, Horde = { 46, 90 } };

local function LayOut(...)
	local first = CharacterCreateRaceButton1;
	if ( not first or not CharacterCreate.numRaces ) then
		return;
	end
	local parent = first:GetParent();
	local sides = { Alliance = {}, Horde = {} };
	for i = 1, CharacterCreate.numRaces do
		local ok, _, faction = pcall(GetFactionForRace, i);
		if ( not (ok and sides[faction]) ) then
			faction = SIDES[strupper(select(i * 3 - 1, ...) or "")] or "Alliance";
		end
		local side = sides[faction];
		side[#side + 1] = _G["CharacterCreateRaceButton"..i];
	end
	-- Rows 50 apart (the game's buttons are 38), closer if more than fit above the sex buttons.
	local rows = math.ceil(math.max(#sides.Alliance, #sides.Horde) / 2);
	local step = 50;
	if ( rows > 1 ) then
		step = math.min(50, math.floor((326 - 38) / (rows - 1)));
	end
	for faction, x in pairs(COLUMNS) do
		for n, button in ipairs(sides[faction]) do
			button:ClearAllPoints();
			button:SetPoint("TOP", parent, "TOP", x[(n - 1) % 2 + 1], -50 - step * math.floor((n - 1) / 2));
		end
	end
end

local enumerateRaces = CharacterCreateEnumerateRaces;
function CharacterCreateEnumerateRaces(...)
	-- (laid out even if the screen's own code stops on a race it doesn't know; its error still shows)
	local ok, problem = pcall(enumerateRaces, ...);
	LayOut(...);
	if ( not ok ) then
		error(problem, 0);
	end
end

local setBackgroundModel = SetBackgroundModel;
function SetBackgroundModel(model, name)
	return setBackgroundModel(model, ALLIED[strupper(name or "")] or name);
end

-- Their scenes' music on the character selection screen: the screen plays it again as it's shown, by
-- the selected character's own race (CharacterSelect_OnShow: GlueAmbienceTracks[strupper(race)]),
-- which the game's table hasn't for them, so theirs is their kin's (or the selection screen's own).
if ( type(GlueAmbienceTracks) == "table" ) then
	for race, background in pairs(ALLIED) do
		GlueAmbienceTracks[race] = GlueAmbienceTracks[strupper(background)] or GlueAmbienceTracks["CHARACTERSELECT"] or "GlueScreenIntro";
	end
end

RACE_INFO_VOIDELF = "Years ago, a group of blood elves led by Magister Umbric sought to harness the power of the Void. Cast out of Silvermoon, they were transformed by the very force they studied, and now, as the ren'dorei, they fight for the Alliance. Those who wash up on the shores of Azuremyst Isle find a welcome among the draenei, who know what it is to be exiles.";
RACE_INFO_NIGHTBORNE = "Secluded in Suramar for ten thousand years behind a barrier of their own making, the nightborne developed an unrivaled mastery of the arcane. Freed from the Legion and from their own tyrant, the shal'dorei have joined the Horde, and their emissaries now walk the roads of Tirisfal beside the Forsaken.";

ABILITY_INFO_VOIDELF1 = "- Spatial Rift: Tear a rift in space. Use it again to teleport through the rift.";
ABILITY_INFO_VOIDELF2 = "- Entropic Embrace: Your abilities have a chance to empower you with the essence of the Void.";
ABILITY_INFO_VOIDELF3 = "- Chill of Night: Reduces Shadow damage taken by 1%.";
ABILITY_INFO_VOIDELF4 = "- Preternatural Calm: Your spell casts are not delayed by taking damage.";
ABILITY_INFO_NIGHTBORNE1 = "- Arcane Pulse: Deals Arcane damage to nearby enemies and reduces their movement speed by 50%.";
ABILITY_INFO_NIGHTBORNE2 = "- Arcane Resistance: Reduces Arcane damage taken by 1%.";
ABILITY_INFO_NIGHTBORNE3 = "- Magical Affinity: Increases magical damage dealt by 1%.";
ABILITY_INFO_NIGHTBORNE4 = "- Ancient History: Inscription skill increased by 15.";

RACE_INFO_LIGHTFORGEDDRAENEI = "When the Army of the Light fell upon the Legion's ships above Argus, the draenei who were forged anew in its radiance became the Lightforged: warriors bound to the Holy Light, who fight the demons that once corrupted their people. The Lightforged who arrive on Azuremyst Isle are welcomed among the exiles of the Exodar as kin.";
RACE_INFO_ZANDALARITROLL = "The Zandalari are the oldest and proudest of the troll tribes, keepers of the loa and of Zuldazar's golden city. Their kings have stood beside the Horde in its wars, and their emissaries now cross the sea to Mulgore, where the tauren teach them the earth's ways before they find their own place among the Horde.";

ABILITY_INFO_LIGHTFORGEDDRAENEI1 = "- Light's Judgment: Calls down a strike of Holy energy on your target, damaging nearby enemies.";
ABILITY_INFO_LIGHTFORGEDDRAENEI2 = "- Forge of Light: Blacksmithing skill increased by 10.";
ABILITY_INFO_LIGHTFORGEDDRAENEI3 = "- Light's Reckoning: When you die, Holy energy bursts from you, harming enemies and healing allies.";
ABILITY_INFO_LIGHTFORGEDDRAENEI4 = "- Holy Resistance: Reduces Holy damage taken by 1%. Demonbane: more experience from demons.";
ABILITY_INFO_ZANDALARITROLL1 = "- Regeneratin': Regenerates your health over 6 sec, until you take damage.";
ABILITY_INFO_ZANDALARITROLL2 = "- Embrace of Pa'ku: Your attacks have a chance to increase your critical strike chance.";
ABILITY_INFO_ZANDALARITROLL3 = "- Pterrordax Swoop: Slows your fall for 2 min.";
ABILITY_INFO_ZANDALARITROLL4 = "- City of Gold: 2% more money looted from creatures.";

LIGHTFORGEDDRAENEI_DISABLED = "Lightforged Draenei can't be made on this realm.";
ZANDALARITROLL_DISABLED = "Zandalari Trolls can't be made on this realm.";
VOIDELF_DISABLED = "Void elves can't be made on this realm.";
NIGHTBORNE_DISABLED = "Nightborne can't be made on this realm.";
