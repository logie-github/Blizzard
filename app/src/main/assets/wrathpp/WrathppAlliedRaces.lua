-- SPDX-License-Identifier: GPL-3.0-or-later
-- Wrath++'s allied races on the character creation screen (docs/wrathpp/ALLIED_RACES.md): the ten of Shadowlands' and the
-- Alliance's High Elf, after the game's ten, as realm/warcraft/modules/mod-allied-races' AlliedRacesCreate.lua does for its four:
--  * More race buttons (WrathppAlliedRaces.xml makes them) given the names the screen looks for.
--  * Each side's races in two columns (the Alliance's left, the Horde's right), two to a row from the top.
--  * Their icons: one picture each (Interface\\Glues\\CharacterCreate\\WrathppRaces\\<Race>.blp, wago.tools' own race icons),
--    put on their buttons whenever the screen lays the races out.
--  * Their backgrounds: their start race's scene (the screen's models have ten); on the selection screen its music.
--  * Their text.
-- Loaded after the game's own screens and before WrathppCreate.lua (the file names sort so).

local BACKGROUNDS = { VOIDELF = "BloodElf", LIGHTFORGEDDRAENEI = "Draenei", KULTIRAN = "Human", DARKIRONDWARF = "Dwarf", MECHAGNOME = "Gnome", HIGHELF = "BloodElf", NIGHTBORNE = "NightElf", ZANDALARITROLL = "Orc", HIGHMOUNTAINTAUREN = "Tauren", VULPERA = "Orc", MAGHARORC = "Orc" };
local SIDES = { VOIDELF = "Alliance", LIGHTFORGEDDRAENEI = "Alliance", KULTIRAN = "Alliance", DARKIRONDWARF = "Alliance", MECHAGNOME = "Alliance", HIGHELF = "Alliance", NIGHTBORNE = "Horde", ZANDALARITROLL = "Horde", HIGHMOUNTAINTAUREN = "Horde", VULPERA = "Horde", MAGHARORC = "Horde", HUMAN = "Alliance", DWARF = "Alliance", NIGHTELF = "Alliance", GNOME = "Alliance", DRAENEI = "Alliance", ORC = "Horde", SCOURGE = "Horde", TAUREN = "Horde", TROLL = "Horde", BLOODELF = "Horde" };
local ICON_PATH = "Interface\\Glues\\CharacterCreate\\WrathppRaces\\"
local ICONS = { }
for token in pairs(BACKGROUNDS) do ICONS[token] = ICON_PATH..token end

local highest = 0;
for i = 1, 24 do
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

local COLUMNS = { Alliance = { -90, -46 }, Horde = { 46, 90 } };

local function LayOut(...)
	local first = CharacterCreateRaceButton1;
	if ( not first or not CharacterCreate.numRaces ) then
		return;
	end
	local parent = first:GetParent();
	local sides = { Alliance = {}, Horde = {} };
	for i = 1, CharacterCreate.numRaces do
		local token = strupper(select(i * 3 - 1, ...) or "");
		local ok, _, faction = pcall(GetFactionForRace, i);
		if ( not (ok and sides[faction]) ) then
			faction = SIDES[token] or "Alliance";
		end
		local side = sides[faction];
		side[#side + 1] = _G["CharacterCreateRaceButton"..i];
		-- the race's own picture (the game's ten are in the screen's atlas)
		if ( ICONS[token] and _G["CharacterCreateRaceButton"..i.."NormalTexture"] ) then
			local normal = _G["CharacterCreateRaceButton"..i.."NormalTexture"];
			normal:SetTexture(ICONS[token]);
			normal:SetTexCoord(0, 1, 0, 1);
			local pushed = _G["CharacterCreateRaceButton"..i.."PushedTexture"];
			if ( pushed ) then pushed:SetTexture(ICONS[token]); pushed:SetTexCoord(0, 1, 0, 1); end
		end
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
	return setBackgroundModel(model, BACKGROUNDS[strupper(name or "")] or name);
end

if ( type(GlueAmbienceTracks) == "table" ) then
	for race, background in pairs(BACKGROUNDS) do
		GlueAmbienceTracks[race] = GlueAmbienceTracks[strupper(background)] or GlueAmbienceTracks["CHARACTERSELECT"] or "GlueScreenIntro";
	end
end

RACE_INFO_VOIDELF = "Blood elves who studied the Void were cast out of Silvermoon and changed by it. Now ren'dorei, they stand with the Alliance, welcomed by the draenei who know what exile is.";
ABILITY_INFO_VOIDELF1 = "- Spatial Rift: Tear a rift in space; use it again to step through.";
ABILITY_INFO_VOIDELF2 = "- Entropic Embrace: Your abilities may empower you with the Void.";
ABILITY_INFO_VOIDELF3 = "- Chill of Night: Reduces Shadow damage taken by 1%.";
ABILITY_INFO_VOIDELF4 = "- Preternatural Calm: Your spell casts are not delayed by taking damage.";
VOIDELF_DISABLED = "Void Elf can't be made on this realm.";

RACE_INFO_LIGHTFORGEDDRAENEI = "Draenei remade in the Light's radiance above Argus: warriors bound to the Holy, who now fight beside the Alliance.";
ABILITY_INFO_LIGHTFORGEDDRAENEI1 = "- Light's Judgment: A strike of Holy energy on your target.";
ABILITY_INFO_LIGHTFORGEDDRAENEI2 = "- Forge of Light: Blacksmithing skill increased by 10.";
ABILITY_INFO_LIGHTFORGEDDRAENEI3 = "- Light's Reckoning: When you die, Holy energy harms enemies and heals allies.";
ABILITY_INFO_LIGHTFORGEDDRAENEI4 = "- Holy Resistance, Demonbane.";
LIGHTFORGEDDRAENEI_DISABLED = "Lightforged Draenei can't be made on this realm.";

RACE_INFO_KULTIRAN = "Seafaring humans of Boralus and Kul Tiras, hardened by storms, tides and long wars. Stubborn, loyal and strong.";
ABILITY_INFO_KULTIRAN1 = "- Brush It Off: All damage taken reduced by 2%.";
ABILITY_INFO_KULTIRAN2 = "- Haymaker: Stun nearby enemies with a mighty swing.";
ABILITY_INFO_KULTIRAN3 = "- Diplomacy: 10% more reputation gained.";
ABILITY_INFO_KULTIRAN4 = "- Child of the Sea: Breathe underwater far longer.";
KULTIRAN_DISABLED = "Kul Tiran can't be made on this realm.";

RACE_INFO_DARKIRONDWARF = "Dwarves of the Dark Iron clan, forged by the fires of Blackrock and long bound to Ragnaros. Now they have a place in the Alliance.";
ABILITY_INFO_DARKIRONDWARF1 = "- Fireblood: Removes poison, disease, curse, magic and bleeds, and reduces damage taken for 8 sec.";
ABILITY_INFO_DARKIRONDWARF2 = "- Forged in Flames: Fire damage taken reduced by 10%.";
DARKIRONDWARF_DISABLED = "Dark Iron Dwarf can't be made on this realm.";

RACE_INFO_MECHAGNOME = "Gnomes who rebuilt themselves in metal. Clever engineers who bring their inventions, and their own improvements, to the Alliance.";
ABILITY_INFO_MECHAGNOME1 = "- Combat Analysis: Critical strike chance increased by 2%.";
ABILITY_INFO_MECHAGNOME2 = "- Skillful Scavenger: Engineering skill increased by 15.";
ABILITY_INFO_MECHAGNOME3 = "- Escape Artist: Escape roots and snares.";
ABILITY_INFO_MECHAGNOME4 = "- Engineering Specialization.";
MECHAGNOME_DISABLED = "Mechagnome can't be made on this realm.";

RACE_INFO_HIGHELF = "The long-lived elves of Quel'Thalas who kept their old ways and their old loyalties, and stand with the Alliance.";
ABILITY_INFO_HIGHELF1 = "- Arcane Torrent: Silences nearby enemies and restores resource (by class).";
ABILITY_INFO_HIGHELF2 = "- Magic Resistance: Reduces magic damage taken.";
ABILITY_INFO_HIGHELF3 = "- Arcane Affinity: Enchanting skill increased by 10.";
HIGHELF_DISABLED = "High Elf can't be made on this realm.";

RACE_INFO_NIGHTBORNE = "Behind a barrier of their own making the nightborne of Suramar mastered the arcane for ten thousand years. Freed from the Legion, they joined the Horde.";
ABILITY_INFO_NIGHTBORNE1 = "- Arcane Pulse: Damages nearby enemies and slows them by 50%.";
ABILITY_INFO_NIGHTBORNE2 = "- Arcane Resistance: Reduces Arcane damage taken by 1%.";
ABILITY_INFO_NIGHTBORNE3 = "- Magical Affinity: Increases magical damage dealt by 1%.";
ABILITY_INFO_NIGHTBORNE4 = "- Ancient History: Inscription skill increased by 15.";
NIGHTBORNE_DISABLED = "Nightborne can't be made on this realm.";

RACE_INFO_ZANDALARITROLL = "The oldest and proudest of the troll tribes, keepers of the loa and of Zuldazar's golden city, allies of the Horde.";
ABILITY_INFO_ZANDALARITROLL1 = "- Regeneratin': Regenerates health until you take damage.";
ABILITY_INFO_ZANDALARITROLL2 = "- Embrace of Pa'ku: Your attacks may raise your critical strike chance.";
ABILITY_INFO_ZANDALARITROLL3 = "- Pterrordax Swoop: Slows your fall.";
ABILITY_INFO_ZANDALARITROLL4 = "- City of Gold: 2% more money looted.";
ZANDALARITROLL_DISABLED = "Zandalari Troll can't be made on this realm.";

RACE_INFO_HIGHMOUNTAINTAUREN = "Tauren of the high peaks, mountaineers who keep to their elders' ways and march with the Horde.";
ABILITY_INFO_HIGHMOUNTAINTAUREN1 = "- Mountaineer: Stamina increased by 3%.";
ABILITY_INFO_HIGHMOUNTAINTAUREN2 = "- Bull Rush: Run speed increased by 30% for 3 sec.";
ABILITY_INFO_HIGHMOUNTAINTAUREN3 = "- Endurance: Health increased by 5%.";
HIGHMOUNTAINTAUREN_DISABLED = "Highmountain Tauren can't be made on this realm.";

RACE_INFO_VULPERA = "Small, quick desert foxes, scavengers who learned to survive where no one else would. They travel with the Horde.";
ABILITY_INFO_VULPERA1 = "- Bag of Tricks: Damage to nearby enemies.";
ABILITY_INFO_VULPERA2 = "- Nose for Trouble: Stealth detection increased.";
ABILITY_INFO_VULPERA3 = "- Rummaging: Skinning skill increased by 10.";
ABILITY_INFO_VULPERA4 = "- Escape Artist: Escape roots and snares.";
VULPERA_DISABLED = "Vulpera can't be made on this realm.";

RACE_INFO_MAGHARORC = "Orcs of Draenor who never drank the demon's blood. Proud, spiritual, and brothers to the Horde.";
ABILITY_INFO_MAGHARORC1 = "- Ancestral Call: Damage done increased by 10% for 12 sec.";
ABILITY_INFO_MAGHARORC2 = "- Brawn: Critical strikes deal 2% more damage and healing.";
ABILITY_INFO_MAGHARORC3 = "- Hardiness: Stun duration reduced.";
ABILITY_INFO_MAGHARORC4 = "- Command: Pet damage increased.";
MAGHARORC_DISABLED = "Mag'har Orc can't be made on this realm.";

