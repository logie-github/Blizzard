-- SPDX-License-Identifier: GPL-3.0-or-later
-- Zoom on the character creation screen (mod-skyborne): the mouse wheel, which is the app's pinch,
-- zooms the preview in and out. 3.3.5's preview is the screen's ModelFFX (CharacterCreate), whose
-- camera no Lua can move; a model frame draws its scene to fit its rectangle, so zooming in makes
-- that frame larger around the character (the middle of the screen, a little above its middle:
-- where the character stands), the part beyond the screen not drawn. The screen's panels stay
-- where they were: CharacterCreateFrame, which holds them all, is anchored to the whole screen
-- (GlueParent) in place of the model frame. Zooming out goes back to the whole screen, no further;
-- so does showing the screen again. Loaded after the game's screen (the patch adds it to
-- GlueXML.toc).

local MIN, MAX, STEP = 1.0, 2.5, 0.15;
local FOCUS_X, FOCUS_Y = 0.5, 0.55;    -- where the character stands, a share of the screen from its bottom left
local zoom = MIN;

local function Apply()
	local model, panels, screen = CharacterCreate, CharacterCreateFrame, GlueParent;
	if ( type(model) ~= "table" or type(panels) ~= "table" or type(screen) ~= "table" ) then
		return false;
	end
	local w, h = screen:GetWidth(), screen:GetHeight();
	if ( not w or not h or w <= 0 or h <= 0 ) then
		return false;
	end
	panels:ClearAllPoints();
	panels:SetAllPoints(screen);
	model:ClearAllPoints();
	if ( zoom <= MIN ) then
		model:SetAllPoints(screen);
		return true;
	end
	-- the focus stays where it is on the screen; everything else moves zoom times as far from it
	local fx, fy = w * FOCUS_X, h * FOCUS_Y;
	model:SetPoint("BOTTOMLEFT", screen, "BOTTOMLEFT", fx - fx * zoom, fy - fy * zoom);
	model:SetPoint("TOPRIGHT", screen, "BOTTOMLEFT", fx + (w - fx) * zoom, fy + (h - fy) * zoom);
	return true;
end

local function Wheel(self, delta)
	delta = delta or arg1 or 0;
	if ( delta > 0 ) then
		zoom = math.min(MAX, zoom + STEP);
	elseif ( delta < 0 ) then
		zoom = math.max(MIN, zoom - STEP);
	end
	Apply();
end

local function Reset()
	zoom = MIN;
	Apply();
end

local function Hook(frame, script, handler)
	if ( type(frame) ~= "table" ) then
		return;
	end
	if ( type(frame.GetScript) == "function" and frame:GetScript(script) and type(frame.HookScript) == "function" ) then
		frame:HookScript(script, handler);
	else
		frame:SetScript(script, handler);
	end
end

-- The wheel over the screen: CharacterCreateFrame covers it all (it already takes the mouse, to
-- turn the character).
if ( type(CharacterCreateFrame) == "table" ) then
	CharacterCreateFrame:EnableMouseWheel(true);
	Hook(CharacterCreateFrame, "OnMouseWheel", Wheel);
end
Hook(CharacterCreate, "OnShow", Reset);
