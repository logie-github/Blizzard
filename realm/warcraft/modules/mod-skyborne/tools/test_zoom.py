#!/usr/bin/env python3
"""The creation screen's zoom (data/client/Interface/GlueXML/SkyborneZoom.lua) run in Lua 5.1 against
stand-ins for the game's screen: the mouse wheel (the app's pinch) makes the preview's model frame
larger around the character and back, no smaller than the screen and no larger than its limit, the
screen's panels staying over the whole screen, and showing the screen again starts from the whole
screen. Needs lupa (pip)."""
import os, sys
from lupa import lua51

HERE = os.path.dirname(os.path.abspath(__file__))
LUA = open(os.path.join(HERE, "..", "data", "client", "Interface", "GlueXML", "SkyborneZoom.lua")).read()

STUBS = r"""
local function Frame(name, w, h)
  local f = { name = name, scripts = {}, points = {}, w = w, h = h }
  function f:GetWidth() return self.w end
  function f:GetHeight() return self.h end
  function f:ClearAllPoints() self.points = {} end
  function f:SetPoint(point, rel, relPoint, x, y) self.points[#self.points + 1] = { point, rel, relPoint, x or 0, y or 0 } end
  function f:SetAllPoints(rel) self.points = { { "ALL", rel } } end
  function f:SetScript(k, fn) self.scripts[k] = fn end
  function f:GetScript(k) return self.scripts[k] end
  function f:HookScript(k, fn)
    local old = self.scripts[k]
    self.scripts[k] = function(...) old(...); fn(...) end
  end
  function f:EnableMouseWheel(on) self.wheel = on end
  return f
end
GlueParent = Frame("GlueParent", 1600, 900)
CharacterCreate = Frame("CharacterCreate")
CharacterCreateFrame = Frame("CharacterCreateFrame")
SHOWN = 0
CharacterCreate:SetScript("OnShow", function() SHOWN = SHOWN + 1 end)      -- the game's own

-- The model frame's rectangle on the screen, from its anchors.
function RECT()
  local p = CharacterCreate.points
  if p[1][1] == "ALL" then return 0, 0, GlueParent.w, GlueParent.h end
  local l, b, r, t
  for _, a in ipairs(p) do
    if a[1] == "BOTTOMLEFT" then l, b = a[4], a[5] end
    if a[1] == "TOPRIGHT" then r, t = a[4], a[5] end
  end
  return l, b, r, t
end
"""

failures = 0
def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1

lua = lua51.LuaRuntime(unpack_returned_tuples=True)
lua.execute(STUBS)
lua.execute(LUA)
g = lua.globals()

def wheel(delta, times=1):
    for _ in range(times):
        lua.execute("CharacterCreateFrame.scripts.OnMouseWheel(CharacterCreateFrame, %d)" % delta)

def rect():
    return [float(v) for v in lua.eval("{ RECT() }").values()]

check(bool(g.CharacterCreateFrame.wheel), "the screen takes the mouse wheel")
lua.execute("CharacterCreate.scripts.OnShow(CharacterCreate)")
check(g.SHOWN == 1, "the game's own OnShow still runs")
check(rect() == [0, 0, 1600, 900], "shown: the preview fills the screen")

wheel(1)
l, b, r, t = rect()
check(abs((r - l) / 1600 - 1.15) < 1e-6 and abs((t - b) / 900 - 1.15) < 1e-6, "a notch in makes it 15%% larger (%s)" % (rect(),))
fx, fy = 800, 900 * 0.55
check(abs((fx - l) / (r - l) - 0.5) < 1e-6 and abs((fy - b) / (t - b) - 0.55) < 1e-6, "around the character: the focus stays where it is")
panels = lua.eval("CharacterCreateFrame.points[1]")
check(str(panels[1]) == "ALL" and lua.eval("CharacterCreateFrame.points[1][2] == GlueParent"), "the panels stay over the whole screen")

wheel(1, 30)
l, b, r, t = rect()
check(abs((r - l) / 1600 - 2.5) < 1e-6, "no more than two and a half times (%s)" % ((r - l) / 1600))

wheel(-1, 30)
check(rect() == [0, 0, 1600, 900], "zoomed out: back to the whole screen, no further")

wheel(1, 4)
lua.execute("CharacterCreate.scripts.OnShow(CharacterCreate)")
check(rect() == [0, 0, 1600, 900], "showing the screen again starts from the whole screen")

lua.execute("CharacterCreateFrame.scripts.OnMouseWheel(CharacterCreateFrame, nil)")
check(rect() == [0, 0, 1600, 900], "a wheel event with no delta changes nothing")

print("%d failure(s)" % failures)
sys.exit(1 if failures else 0)
