#!/usr/bin/env python3
"""The races' character screen code (data/client/Interface/GlueXML/AlliedRacesCreate.lua) run in
Lua 5.1 against stand-ins for the game's screen: the extra buttons get the screen's names, each
side's races in two columns, two to a row, the backgrounds, icons and selection screen music are
theirs; and with the
Skyborne's screen code loaded after it (as in a client with both patches), both sides' races still
line up.
Needs lupa (pip)."""
import os
import sys

from lupa import lua51

HERE = os.path.dirname(os.path.abspath(__file__))
LUA = open(os.path.join(HERE, "..", "data", "client", "Interface", "GlueXML", "AlliedRacesCreate.lua")).read()
SKYBORNE = os.path.join(HERE, "..", "..", "mod-skyborne", "data", "client", "Interface", "GlueXML", "SkyborneCreate.lua")
STUBS = r"""
strupper = string.upper
local function Button(name)
  local b = { name = name, points = {} }
  function b:SetParent(p) self.parent = p end
  function b:GetParent() return self.parent end
  function b:ClearAllPoints() self.points = {} end
  function b:SetPoint(...) self.points[#self.points + 1] = { ... } end
  _G[name] = b; _G[name.."NormalTexture"] = {}; _G[name.."PushedTexture"] = {}; _G[name.."Text"] = {}
  return b
end
Frame = { name = "CharacterCreateConfigurationFrame" }
for i = 1, NATIVE do Button("CharacterCreateRaceButton"..i).parent = Frame end
for i = 11, 16 do Button("AlliedRaceButton"..i).parent = { name = "xml" } end
for i = 11, 16 do Button("SkyborneRaceButton"..i).parent = { name = "xml" } end
MAX_RACES = NATIVE
RACE_ICON_TCOORDS = {}
CharacterCreate = {}
RACES = {}
function GetFactionForRace(i) return RACES[i][1], RACES[i][2] end
function CharacterCreateEnumerateRaces(...) CharacterCreate.numRaces = select("#", ...) / 3 end
BACKGROUND = nil
function SetBackgroundModel(model, name) BACKGROUND = name end
-- the game's table of the scenes' music (GlueParent.lua): the scenes there are, no TROLL or GNOME
-- (trolls are shown in the Orcs' scene, gnomes in the Dwarves')
GlueAmbienceTracks = { HUMAN = "GlueScreenHuman", ORC = "GlueScreenOrcTroll",
  DWARF = "GlueScreenDwarfGnome", TAUREN = "GlueScreenTauren", SCOURGE = "GlueScreenUndead",
  NIGHTELF = "GlueScreenNightElf", DRAENEI = "GlueScreenDraenei", BLOODELF = "GlueScreenBloodElf",
  DARKPORTAL = "GlueScreenIntro", DEATHKNIGHT = "GlueScreenIntro", CHARACTERSELECT = "GlueScreenIntro" }
AMBIENCE = nil
function PlayGlueAmbience(track, fade) AMBIENCE = track end
-- as CharacterSelect_OnShow plays it: by the selected character's own race (GetSelectBackgroundModel's)
function ShowSelection(race) AMBIENCE = nil; PlayGlueAmbience(GlueAmbienceTracks[strupper(race)], 4.0) end
"""
failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


for native, races, with_skyborne in [
    (10, ["A Human", "A Dwarf", "A NightElf", "A Gnome", "A Draenei", "A VoidElf", "A LightforgedDraenei",
          "H Orc", "H Scourge", "H Tauren", "H Troll", "H BloodElf", "H Nightborne", "H ZandalariTroll"], False),
    (10, ["A Human", "A Dwarf", "A NightElf", "A Gnome", "A Draenei", "A VoidElf", "A LightforgedDraenei", "A SkyborneA",
          "H Orc", "H Scourge", "H Tauren", "H Troll", "H BloodElf", "H Nightborne", "H ZandalariTroll", "H SkyborneH"], True),
]:
    lua = lua51.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(f"NATIVE = {native}")
    lua.execute(STUBS)
    for i, r in enumerate(races, 1):
        side, name = r.split()
        lua.execute(f'RACES[{i}] = {{ "{name}", "{"Alliance" if side == "A" else "Horde"}" }}')
    lua.execute(LUA)
    if with_skyborne and os.path.exists(SKYBORNE):
        lua.execute(open(SKYBORNE).read())
    g = lua.globals()
    label = "with the Skyborne's screen too" if with_skyborne else "on the game's screen"
    check(g.MAX_RACES >= len(races), f"{label}: MAX_RACES {g.MAX_RACES} for {len(races)} races")
    check(all(g["CharacterCreateRaceButton%d" % i] is not None for i in range(1, len(races) + 1)), "a button for every race")
    check(g.CharacterCreateRaceButton12.GetParent(g.CharacterCreateRaceButton12).name == "CharacterCreateConfigurationFrame", "the extra buttons sit with the game's")
    args = ", ".join(f'"{r.split()[1]}", "{r.split()[1]}", 1' for r in races)
    lua.execute(f"CharacterCreateEnumerateRaces({args})")
    placed = {"Alliance": [], "Horde": []}
    for i, r in enumerate(races, 1):
        side = "Alliance" if r.startswith("A") else "Horde"
        pts = list(g["CharacterCreateRaceButton%d" % i].points.values())
        p = list(pts[-1].values())
        placed[side].append((p[0], p[1]["name"] == "CharacterCreateConfigurationFrame", p[2], p[3], p[4]))
    for side, xs in (("Alliance", (-90, -46)), ("Horde", (46, 90))):
        want = [("TOP", True, "TOP", xs[n % 2], -50 - 50 * (n // 2)) for n in range(len(placed[side]))]
        check(placed[side] == want, f"{side}'s races in two columns, two to a row ({placed[side]})")
    tc = g.RACE_ICON_TCOORDS
    check(tc["VOIDELF_MALE"][1] == 0.875 and tc["VOIDELF_MALE"][4] == 0.25 and tc["NIGHTBORNE_FEMALE"][3] == 0.75, "the icons in the last column, by side and sex")
    check(tc["LIGHTFORGEDDRAENEI_MALE"][1] == 0.625 and tc["LIGHTFORGEDDRAENEI_MALE"][2] == 0.75 and tc["ZANDALARITROLL_FEMALE"][3] == 0.75, "the Lightforged's and Zandalari's icons in the next column")
    lua.execute('SetBackgroundModel("m", "VoidElf")')
    check(g.BACKGROUND == "BloodElf", "the void elves' background is the Blood Elves' (their kin's height)")
    lua.execute('SetBackgroundModel("m", "Nightborne")')
    check(g.BACKGROUND == "NightElf", "the nightborne's background is the Night Elves' (framed for their height)")
    lua.execute('SetBackgroundModel("m", "LightforgedDraenei")')
    check(g.BACKGROUND == "Draenei", "the Lightforged Draenei's background is the Draenei's")
    lua.execute('SetBackgroundModel("m", "ZandalariTroll")')
    check(g.BACKGROUND == "Orc", "the Zandalari's background is the Trolls' own, the Orcs' scene (3.3.5 has no UI_Troll)")
    check(g.GlueAmbienceTracks[g.BACKGROUND.upper()] is not None, "every background the screen asks for has its music")
    lua.execute('SetBackgroundModel("m", "Orc")')
    check(g.BACKGROUND == "Orc", "the game's own backgrounds stay")
    music = [("VoidElf", "GlueScreenBloodElf"), ("Nightborne", "GlueScreenNightElf"), ("LightforgedDraenei", "GlueScreenDraenei"),
             ("ZandalariTroll", "GlueScreenOrcTroll"), ("Orc", "GlueScreenOrcTroll"), ("Human", "GlueScreenHuman")]
    if with_skyborne:
        music += [("SkyborneA", "GlueScreenHuman"), ("SkyborneH", "GlueScreenTauren")]
    heard = []
    for race, track in music:
        g.ShowSelection(race)
        heard.append((race, g.AMBIENCE))
    check(heard == music, f"the selection screen's music by the selected character's race: their kin's, the game's own kept ({heard})")
    check(g.RACE_INFO_VOIDELF and g.ABILITY_INFO_NIGHTBORNE4 and g.VOIDELF_DISABLED, "the races' texts")
    check(g.RACE_INFO_LIGHTFORGEDDRAENEI and g.ABILITY_INFO_ZANDALARITROLL4 and g.ZANDALARITROLL_DISABLED, "the Lightforged's and Zandalari's texts")

# The in-game script for add-ons: Questie's 3.3.5 port's race table gets the races as their start
# races, as that add-on loads (its own entries left as they are).
ADDONS = open(os.path.join(HERE, "..", "data", "client", "Interface", "FrameXML", "AlliedRacesAddons.lua")).read()
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
lua.execute('Fire("ADDON_LOADED", "Blizzard_AuctionUI")')
lua.execute('QuestieCompat = { ChrRaces = { Human = 1, Draenei = 11, Scourge = 5 } }; Fire("ADDON_LOADED", "Questie-335")')
g = lua.globals()
r = g.QuestieCompat.ChrRaces
check(r.VoidElf == 11 and r.LightforgedDraenei == 11 and r.Nightborne == 5 and r.ZandalariTroll == 6,
      "Questie's race table: the void elves and Lightforged the Draenei, the nightborne the Forsaken, the Zandalari the Tauren")
check(r.Human == 1 and r.Scourge == 5, "...the game's races as Questie has them")
lua.execute('QuestieCompat.ChrRaces.VoidElf = 15; Fire("ADDON_LOADED", "Other")')
check(r.VoidElf == 15, "...and a race Questie knows itself stays its")

print("PASSED" if not failures else f"FAILED ({failures})")
sys.exit(1 if failures else 0)
