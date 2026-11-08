#!/usr/bin/env python3
"""The Worgen's and Goblins' character screen code (data/client/Interface/GlueXML/
WorgenGoblinCreate.lua) run in Lua 5.1 against stand-ins for the game's screen, loaded as the game
loads it with every patch in: the game's screen, then this (patch-U), the allied races' (patch-V) and
the Skyborne's (patch-Z). Their buttons and round icon show their own icon sheet and every other
race's the game's, as the sex and the race change; their scenes' music; and the allied races' layout
still puts each side's nine races in two columns.
Needs lupa (pip)."""
import os
import sys

from lupa import lua51

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = os.path.join(HERE, "..", "..")
OURS = os.path.join(HERE, "..", "data", "client", "Interface", "GlueXML", "WorgenGoblinCreate.lua")
ALLIED = os.path.join(MODULES, "mod-allied-races", "data", "client", "Interface", "GlueXML", "AlliedRacesCreate.lua")
SKYBORNE = os.path.join(MODULES, "mod-skyborne", "data", "client", "Interface", "GlueXML", "SkyborneCreate.lua")
GAME_SHEET = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races"
GAME_ROUND = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound"
OUR_SHEET = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Worgoblin"
OUR_ROUND = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-WorgoblinRound"

STUBS = r"""
strupper = string.upper
unpack = unpack or table.unpack
local function Texture(file)
  local t = { file = file }
  function t:SetTexture(f) self.file = f end
  function t:GetTexture() return self.file end
  function t:SetTexCoord(...) self.coords = { ... } end
  return t
end
local function Button(name)
  local b = { name = name, points = {} }
  function b:SetParent(p) self.parent = p end
  function b:GetParent() return self.parent end
  function b:ClearAllPoints() self.points = {} end
  function b:SetPoint(...) self.points[#self.points + 1] = { ... } end
  function b:Show() self.shown = true end
  function b:Hide() self.shown = false end
  _G[name] = b; _G[name.."NormalTexture"] = Texture(GAME_SHEET); _G[name.."PushedTexture"] = Texture(GAME_SHEET); _G[name.."Text"] = {}
  return b
end
Frame = { name = "CharacterCreateConfigurationFrame" }
for i = 1, 10 do Button("CharacterCreateRaceButton"..i).parent = Frame end
for i = 11, 16 do Button("AlliedRaceButton"..i).parent = { name = "xml" } end
for i = 11, 16 do Button("SkyborneRaceButton"..i).parent = { name = "xml" } end
for i = 11, 18 do Button("WorgenGoblinRaceButton"..i).parent = { name = "xml" } end
CharacterCreateRaceIcon = Texture(GAME_ROUND)
MAX_RACES = 10
SEX_MALE, SEX_FEMALE = 2, 3
sex = SEX_MALE
function GetSelectedSex() return sex end
-- the game's coordinates for its own races (CharacterCreate.lua's), a few of them
RACE_ICON_TCOORDS = {}
for column, races in ipairs({ { "HUMAN", "TAUREN" }, { "DWARF", "SCOURGE" }, { "GNOME", "TROLL" }, { "NIGHTELF", "ORC" }, { "DRAENEI", "BLOODELF" } }) do
  local left = (column - 1) * 0.125
  RACE_ICON_TCOORDS[races[1].."_MALE"] = { left, left + 0.125, 0, 0.25 }
  RACE_ICON_TCOORDS[races[2].."_MALE"] = { left, left + 0.125, 0.25, 0.5 }
  RACE_ICON_TCOORDS[races[1].."_FEMALE"] = { left, left + 0.125, 0.5, 0.75 }
  RACE_ICON_TCOORDS[races[2].."_FEMALE"] = { left, left + 0.125, 0.75, 1.0 }
end
CharacterCreate = {}
RACES = {}
function GetFactionForRace(i) return RACES[i][1], RACES[i][2] end
-- the game's CharacterCreateEnumerateRaces: each button's coordinates from RACE_ICON_TCOORDS (an
-- error for a race it has none for, as the game's code has)
function CharacterCreateEnumerateRaces(...)
  CharacterCreate.numRaces = select("#", ...) / 3
  local gender = GetSelectedSex() == SEX_MALE and "MALE" or "FEMALE"
  for i = 1, CharacterCreate.numRaces do
    local coords = RACE_ICON_TCOORDS[strupper(select(i * 3 - 1, ...)).."_"..gender]
    _G["CharacterCreateRaceButton"..i.."NormalTexture"]:SetTexCoord(coords[1], coords[2], coords[3], coords[4])
  end
end
selected = 1
function GetNameForRace() return RACES[selected][3], RACES[selected][3] end
-- the game's SetCharacterRace and SetCharacterGender: the round icon's coordinates
function SetCharacterRace(id)
  selected = id
  local _, file = GetNameForRace()
  local coords = RACE_ICON_TCOORDS[strupper(file).."_"..(GetSelectedSex() == SEX_MALE and "MALE" or "FEMALE")]
  if coords then CharacterCreateRaceIcon:SetTexCoord(unpack(coords)) end
end
function SetCharacterGender(s) sex = s; SetCharacterRace(selected) end
BACKGROUND = nil
function SetBackgroundModel(model, name) BACKGROUND = name end
GlueAmbienceTracks = { HUMAN = "GlueScreenHuman", ORC = "GlueScreenOrcTroll",
  DWARF = "GlueScreenDwarfGnome", TAUREN = "GlueScreenTauren", SCOURGE = "GlueScreenUndead",
  NIGHTELF = "GlueScreenNightElf", DRAENEI = "GlueScreenDraenei", BLOODELF = "GlueScreenBloodElf",
  DARKPORTAL = "GlueScreenIntro", DEATHKNIGHT = "GlueScreenIntro", CHARACTERSELECT = "GlueScreenIntro" }
CharModelGlowInfo = { HUMAN = 0.15 }
RaceLights = { ORC = { "orc's lights" } }
"""
failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


# The enumeration as the game makes it (ChrRaces' order), then a side for each.
RACES = ["A Human", "H Orc", "A Dwarf", "A NightElf", "H Scourge", "H Tauren", "A Gnome", "H Troll", "H Goblin",
         "H BloodElf", "A Draenei", "A Worgen", "A SkyborneA", "H SkyborneH", "A VoidElf", "H Nightborne",
         "A LightforgedDraenei", "H ZandalariTroll"]

lua = lua51.LuaRuntime(unpack_returned_tuples=True)
lua.execute(f'GAME_SHEET = "{GAME_SHEET.replace(chr(92), chr(92) * 2)}"; GAME_ROUND = "{GAME_ROUND.replace(chr(92), chr(92) * 2)}"')
lua.execute(STUBS)
for i, r in enumerate(RACES, 1):
    side, name = r.split()
    lua.execute(f'RACES[{i}] = {{ "{"Alliance" if side == "A" else "Horde"}", "{"Alliance" if side == "A" else "Horde"}", "{name}" }}')
for path in (OURS, ALLIED, SKYBORNE):
    lua.execute(open(path).read())
g = lua.globals()

enumerate_args = ", ".join(f'"{r.split()[1]}", "{r.split()[1]}", 1' for r in RACES)


def enumerate_races():
    lua.execute(f"CharacterCreateEnumerateRaces({enumerate_args})")


def button(i):
    t = g[f"CharacterCreateRaceButton{i}NormalTexture"]
    return t.file, tuple(t.coords[k] for k in (1, 2, 3, 4)) if t.coords else None


enumerate_races()
worgen, goblin, human = RACES.index("A Worgen") + 1, RACES.index("H Goblin") + 1, 1
check(g.CharacterCreate.numRaces == 18, "18 races enumerated")
check(g.MAX_RACES == 18 and lua.eval("CharacterCreateRaceButton17 == WorgenGoblinRaceButton17 and CharacterCreateRaceButton18 == WorgenGoblinRaceButton18"),
      "18 buttons (the allied races' and the Skyborne's code make 16), the screen's maximum 18")
check(lua.eval("CharacterCreateRaceButton17.parent == Frame"), "...the extra buttons on the screen's frame")
check(button(worgen) == (OUR_SHEET, (0, 1, 0, 0.25)), "the Worgen's button: their sheet, the man's icon")
check(button(goblin) == (OUR_SHEET, (0, 1, 0.25, 0.5)), "the Goblins' button: their sheet, the man's icon")
check(button(human) == (GAME_SHEET, (0, 0.125, 0, 0.25)), "the Humans' button: the game's sheet, as it was")
lua.execute("sex = SEX_FEMALE")
enumerate_races()
check(button(worgen) == (OUR_SHEET, (0, 1, 0.5, 0.75)) and button(goblin) == (OUR_SHEET, (0, 1, 0.75, 1.0)),
      "women: the Worgen's and Goblins' women's icons")
check(button(2)[0] == GAME_SHEET, "...the Orcs' still the game's sheet")
# A button that showed a Worgen and then another race (the screen's buttons are numbered, not the races).
lua.execute(f'RACES[{worgen}] = {{ "Alliance", "Alliance", "Human" }}')
lua.execute(f'RACES[{worgen}] = {{ "Alliance", "Alliance", "Worgen" }}')

lua.execute(f"SetCharacterRace({worgen})")
check(g.CharacterCreateRaceIcon.file == OUR_ROUND and g.CharacterCreateRaceIcon.coords[3] == 0.5,
      "the round icon by the text: the Worgen woman's from their sheet")
lua.execute("SetCharacterGender(SEX_MALE)")
check(g.CharacterCreateRaceIcon.file == OUR_ROUND and g.CharacterCreateRaceIcon.coords[3] == 0,
      "...the man's when the sex changes")
lua.execute("SetCharacterRace(1)")
check(g.CharacterCreateRaceIcon.file == GAME_ROUND and g.CharacterCreateRaceIcon.coords[2] == 0.125,
      "...the game's sheet again for a Human")

check(g.GlueAmbienceTracks["WORGEN"] == "GlueScreenHuman" and g.GlueAmbienceTracks["GOBLIN"] == "GlueScreenOrcTroll",
      "their scenes' music: the Humans' for the Worgen, the Orcs' for the Goblins")
check(lua.eval("RaceLights.GOBLIN == RaceLights.ORC"), "the Goblins' scene lit as the Orcs'")
lua.execute('SetBackgroundModel("m", "Worgen")')
check(g.BACKGROUND == "Worgen", "their own scenes (mod-worgoblin's UI_Worgen and UI_Goblin), not another race's")

# The allied races' layout over all 18: each side's nine, two to a row.
xs = {}
for i, r in enumerate(RACES, 1):
    b = g[f"CharacterCreateRaceButton{i}"]
    point = b.points[1] if b.points and b.points[1] else None
    xs.setdefault(r.split()[0], []).append(point[4] if point else None)
check(sorted(set(xs["A"])) == [-90, -46] and sorted(set(xs["H"])) == [46, 90], f"each side's races in its two columns ({xs})")

print("PASSED" if not failures else f"FAILED ({failures})")
sys.exit(1 if failures else 0)
