#!/usr/bin/env python3
"""The Murlocs' and the Naga's character screen code (data/client/Interface/GlueXML/MurlocNagaCreate.lua)
run in Lua 5.1 against stand-ins for the game's screen, loaded as the game loads it with every patch in:
the game's screen, then this (patch-enUS-T), the Worgen and Goblins' (patch-U), the allied races'
(patch-V) and the Skyborne's (patch-Z). Twenty buttons; their buttons and round icon show their own
icon sheet (put there each frame, after the Worgen and Goblins' code gave every race not its own the
game's), every other race's as the others left it; each side's ten races in two columns; their scenes
and music; their texts; Questie's race table.
Needs lupa (pip)."""
import os
import sys

from lupa import lua51

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = os.path.join(HERE, "..", "..")
OURS = os.path.join(HERE, "..", "data", "client", "Interface", "GlueXML", "MurlocNagaCreate.lua")
OTHERS = [os.path.join(MODULES, "mod-worgen-goblin", "data", "client", "Interface", "GlueXML", "WorgenGoblinCreate.lua"),
          os.path.join(MODULES, "mod-allied-races", "data", "client", "Interface", "GlueXML", "AlliedRacesCreate.lua"),
          os.path.join(MODULES, "mod-skyborne", "data", "client", "Interface", "GlueXML", "SkyborneCreate.lua")]
GAME_SHEET = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Races"
GAME_ROUND = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-RacesRound"
OUR_SHEET = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MurlocNaga"
OUR_ROUND = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-MurlocNagaRound"
WORGEN_SHEET = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-Worgoblin"

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
  _G[name] = b; _G[name.."NormalTexture"] = Texture(GAME_SHEET); _G[name.."PushedTexture"] = Texture(GAME_SHEET); _G[name.."Text"] = {}
  return b
end
Frame = { name = "CharacterCreateConfigurationFrame" }
for i = 1, 10 do Button("CharacterCreateRaceButton"..i).parent = Frame end
-- (each patch's XML makes its buttons before its code runs; the game reads this patch's first)
for i = 11, 20 do Button("MurlocNagaRaceButton"..i).parent = { name = "xml" } end
for i = 11, 18 do Button("WorgenGoblinRaceButton"..i).parent = { name = "xml" } end
for i = 11, 16 do Button("AlliedRaceButton"..i).parent = { name = "xml" } end
for i = 11, 16 do Button("SkyborneRaceButton"..i).parent = { name = "xml" } end
CharacterCreateRaceIcon = Texture(GAME_ROUND)
MAX_RACES = 10
SEX_MALE, SEX_FEMALE = 2, 3
sex = SEX_MALE
function GetSelectedSex() return sex end
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
function GetAvailableRaces()
  local out = {}
  for i, r in ipairs(RACES) do out[#out + 1] = r[3]; out[#out + 1] = r[3]; out[#out + 1] = 1 end
  return unpack(out)
end
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
CharModelGlowInfo = { DWARF = 0.2 }
RaceLights = { TAUREN = { "tauren's lights" } }
local function Label(text)
  local l = { text = text }
  function l:SetText(t) self.text = t end
  function l:GetText() return self.text end
  return l
end
CharacterCustomizationButtonFrame2Text = Label("Face")
CharacterCustomizationButtonFrame3Text = Label("Hair Style")
CharacterCustomizationButtonFrame4Text = Label("Hair Color")
HAIR_NORMAL_STYLE, HAIR_NORMAL_COLOR = "Hair Style", "Hair Color"
TOKENS = { [19] = "MURLOC", [20] = "NAGA" }
function GetHairCustomization() return TOKENS[selected] or "NORMAL" end
function CharacterCreate_UpdateHairCustomization()
  CharacterCustomizationButtonFrame3Text:SetText(_G["HAIR_"..GetHairCustomization().."_STYLE"])
  CharacterCustomizationButtonFrame4Text:SetText(_G["HAIR_"..GetHairCustomization().."_COLOR"])
end
"""
failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


# The races as the game lists them (ChrRaces' order), with their sides.
RACES = ["A Human", "H Orc", "A Dwarf", "A NightElf", "H Scourge", "H Tauren", "A Gnome", "H Troll", "H Goblin",
         "H BloodElf", "A Draenei", "A Worgen", "A SkyborneA", "H SkyborneH", "A VoidElf", "H Nightborne",
         "A LightforgedDraenei", "H ZandalariTroll", "A Murloc", "H Naga_"]

lua = lua51.LuaRuntime(unpack_returned_tuples=True)
lua.execute(f'GAME_SHEET = "{GAME_SHEET.replace(chr(92), chr(92) * 2)}"; GAME_ROUND = "{GAME_ROUND.replace(chr(92), chr(92) * 2)}"')
lua.execute(STUBS)
for i, r in enumerate(RACES, 1):
    side, name = r.split()
    lua.execute(f'RACES[{i}] = {{ "{"Alliance" if side == "A" else "Horde"}", "{"Alliance" if side == "A" else "Horde"}", "{name}" }}')
for path in [OURS] + OTHERS:
    lua.execute(open(path).read())
g = lua.globals()
args = ", ".join(f'"{r.split()[1]}", "{r.split()[1]}", 1' for r in RACES)


def show_screen():
    lua.execute(f"CharacterCreateEnumerateRaces({args})")
    g.MurlocNaga_Icons()                     # (the screen's next frame)


def button(i):
    t = g[f"CharacterCreateRaceButton{i}NormalTexture"]
    return t.file, tuple(t.coords[k] for k in (1, 2, 3, 4)) if t.coords else None


show_screen()
murloc, naga = 19, 20
check(g.CharacterCreate.numRaces == 20 and g.MAX_RACES == 20, "20 races, the screen's maximum 20")
check(all(g[f"CharacterCreateRaceButton{i}"] is not None for i in range(1, 21)), "a button for every race")
check(lua.eval("CharacterCreateRaceButton19 == MurlocNagaRaceButton19 and CharacterCreateRaceButton19.parent == Frame"),
      "...the extra buttons this patch's, on the screen's frame")
check(button(murloc) == (OUR_SHEET, (0, 1, 0, 0.25)), "the Murlocs' button: their sheet, the man's icon")
check(button(naga) == (OUR_SHEET, (0, 1, 0.25, 0.5)), "the Naga's button: their sheet, the man's icon")
check(button(12) == (WORGEN_SHEET, (0, 1, 0, 0.25)), "the Worgen's button: theirs, as the Worgen and Goblins' code put it")
check(button(1) == (GAME_SHEET, (0, 0.125, 0, 0.25)), "the Humans' button: the game's sheet")
lua.eval("SetCharacterGender")(3)
show_screen()
check(button(murloc) == (OUR_SHEET, (0, 1, 0.5, 0.75)) and button(naga) == (OUR_SHEET, (0, 1, 0.75, 1.0)), "as women: the women's icons")
lua.eval("SetCharacterRace")(naga)
g.MurlocNaga_Icons()
icon = g.CharacterCreateRaceIcon
check(icon.file == OUR_ROUND and tuple(icon.coords[k] for k in (1, 2, 3, 4)) == (0, 1, 0.75, 1.0), "the round icon by the race's name: theirs")
lua.eval("SetCharacterRace")(1)
g.MurlocNaga_Icons()
check(g.CharacterCreateRaceIcon.file != OUR_ROUND, "...and not for another race")

placed = {"Alliance": [], "Horde": []}
for i, r in enumerate(RACES, 1):
    side = "Alliance" if r.startswith("A") else "Horde"
    pts = list(g[f"CharacterCreateRaceButton{i}"].points.values())
    p = list(pts[-1].values())
    placed[side].append((p[3], p[4]))
for side, xs in (("Alliance", (-90, -46)), ("Horde", (46, 90))):
    want = [(xs[n % 2], -50 - 50 * (n // 2)) for n in range(10)]
    check(placed[side] == want, f"{side}'s ten races in two columns, two to a row")

lua.execute('SetBackgroundModel("m", "Murloc")')
check(g.BACKGROUND == "Dwarf", "the Murlocs' scene is the Dwarves' (framed for their height)")
lua.execute('SetBackgroundModel("m", "Naga_")')
check(g.BACKGROUND == "Tauren", "the Naga's scene is the Tauren's")
lua.execute('SetBackgroundModel("m", "VoidElf")')
check(g.BACKGROUND == "BloodElf", "the others' scenes stay theirs")
check(g.GlueAmbienceTracks.MURLOC == "GlueScreenDwarfGnome" and g.GlueAmbienceTracks.NAGA_ == "GlueScreenTauren", "their scenes' music on the selection screen")
check(g.CharModelGlowInfo.MURLOC == 0.2 and g.RaceLights.NAGA_ is not None, "their scenes' glow and lights")
def labels(race):
    lua.eval("SetCharacterRace")(race)
    g.CharacterCreate_UpdateHairCustomization()
    return tuple(g[f"CharacterCustomizationButtonFrame{i}Text"].text for i in (2, 3, 4))


check(labels(murloc) == ("Eye Color", "Fins", "Fin Color"), "the Murlocs' choices: Eye Color, Fins, Fin Color")
check(labels(naga) == ("Face", "Headdress", "Headdress Color"), "the Naga's: Face, Headdress, Headdress Color")
check(labels(1) == ("Face", "Hair Style", "Hair Color"), "...and every other race's the game's own")
check(g.RACE_INFO_MURLOC and g.RACE_INFO_NAGA_ and g.ABILITY_INFO_MURLOC4 and g.ABILITY_INFO_NAGA_4 and g.NAGA__DISABLED, "their texts")

ADDONS = open(os.path.join(HERE, "..", "data", "client", "Interface", "FrameXML", "MurlocNagaAddons.lua")).read()
lua = lua51.LuaRuntime(unpack_returned_tuples=True)
lua.execute(r"""
FRAMES = {}
function CreateFrame() local f = { events = {} }
  function f:RegisterEvent(e) self.events[e] = true end
  function f:SetScript(k, fn) self[k] = fn end
  FRAMES[#FRAMES + 1] = f; return f end
function Fire(e, ...) for _, f in ipairs(FRAMES) do if f.events[e] and f.OnEvent then f.OnEvent(f, e, ...) end end end
""")
lua.execute(ADDONS)
lua.execute('QuestieCompat = { ChrRaces = { Human = 1, NightElf = 4, Troll = 8 } }; Fire("ADDON_LOADED", "Questie-335")')
r = lua.globals().QuestieCompat.ChrRaces
check(r.Murloc == 4 and r.Naga_ == 8 and r.Human == 1, "Questie's race table: the murlocs the night elves, the naga the trolls")
check(lua.globals().HAIR_MURLOC_STYLE == "Fins" and lua.globals().HAIR_MURLOC_COLOR == "Fin Color", "the barber shop's names for the murlocs' fins")

print("PASSED" if not failures else f"FAILED ({failures})")
sys.exit(1 if failures else 0)
