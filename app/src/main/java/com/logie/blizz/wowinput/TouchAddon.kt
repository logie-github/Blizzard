// SPDX-License-Identifier: GPL-3.0-or-later
// Ported from the World of Warcraft app (com.logie.warcraft), unchanged apart from its package.

package com.logie.blizz.wowinput

/**
 * The app's own add-on, put into the client's `Interface/AddOns` before each start (and left out
 * of the add-on manager's list): it tells the touch controls where the spellbook is while it's
 * open, so a drag that starts on it drags a spell, as the mouse does on a PC; and where the
 * game's windows of items, talents and abilities are (the bags, the bank, the character pane, the
 * talents, the action bars), where a hold is a right click.
 *
 * An add-on can't reach the app directly, so it says it to the realm on the phone: an add-on
 * message (prefix `WowTouch`) whispered to the player itself, which the realm keeps for the app
 * instead of passing on (patches/azerothcore/0009, `files/run/interface`). It says it again only
 * when it changes: "open <0 or 1> drag <left> <bottom> <right> <top> hold <left> <bottom> <right> <top>
 * ..." in thousandths of the screen from its bottom left (the spellbook inside its own edges; each
 * group of windows as one area: the bags, the bank, the character pane, the talents, the bars at
 * the bottom, the bars on the right, the portraits), "-" for none.
 *
 * The mounts and companions pane (the character pane's Pet tab) drags too, so a mount or a
 * companion goes onto the action bars as a spell does.
 *
 * A right click on an action bar's button (a hold, from the app) takes its action off the bar, as
 * dragging it away does on a PC, and does nothing else.
 *
 * The note starts "open 1" while a window the player is using is open (the loot, a talk, a quest, a
 * vendor, a trainer, the flight master's map, the mail, a trade, Immersion's, the game's questions),
 * "open 0" otherwise: a double tap then clicks twice and never jumps, which would close it.
 *
 * Sticky targeting keeps a double tap's first ground click from clearing the current target.
 * Jumping never clears and restores the target or changes the player's bindings.
 *
 * A talent's first tap shows what it does (its tooltip) and spends nothing; a second tap on it
 * straight after (a double tap: the app clicks twice on the game's windows) spends the point.
 *
 * On the Wrath Remix realm it also puts **Report Time Anomaly** in the game's menu, under Macros,
 * and on the toolbar's Help button (there are no game masters to ask): a window asks what went
 * wrong, in as many lines as it takes (up to 1000 letters; the player may write nothing), and asks
 * the realm for a report, in add-on messages to the player itself (prefix `WowRemix`: "report
 * <what they wrote>", a long one in pieces, each but the last "report+ <its words>"). The realm
 * writes the report (mod-wrath-remix, RemixReport.cpp) and the app sends it to GitHub
 * ([com.logie.warcraft.AnomalyReports]).
 *
 * And it darkens the screen for a moment of the story when the realm asks (a scene's fade to black,
 * Moratari's tent): the realm's add-on message to the player "fade <milliseconds> <words>" (prefix
 * `WowRemix`, mod-wrath-remix's RemixOutings.cpp). The dark comes up in a second or so, the words in
 * the middle of it, and it goes again as the time is up.
 *
 * The opening's curtain (mod-wrath-remix's RemixIntro.cpp): "curtain <milliseconds> <words>" makes
 * the screen dark at once (the words on it: where and when the next act is; " | " a new line) and
 * keeps it so until "lift <milliseconds>" fades it out over that long, or the time runs out. Behind
 * it the game loads the place the realm has just put the player in, which is choppy on a phone; the
 * add-on watches the frames and tells the realm "settled <milliseconds>" once they have run smoothly
 * for a while (no frame over a fifth of a second for a second and a half, two seconds in at least),
 * counted from the curtain or from entering the world, whichever came last. The realm lifts the
 * curtain then, and the act begins on a world that has finished appearing.
 *
 * Add-ons made for a PC's screen are fitted to the phone's: TomTom's arrow at the top of the screen,
 * in the middle (TomTom's own place for it is the middle of the screen, over the character), unless
 * the player has dragged it elsewhere; Immersion's quest and gossip choices and its talking box kept
 * on the screen (its choices sit 500 right of the middle, past a phone screen's edge: they come in to
 * 16 from it each time they show, and Immersion keeps that place).
 */
object TouchAddon {
    const val FOLDER = "WowTouch"
    const val PREFIX = "WowTouch"
    const val REMIX_PREFIX = "WowRemix"
    /** The realm whose menu has Report Time Anomaly, as the game names it ([com.logie.warcraft.Realms]). */
    const val REMIX_REALM = "Wrath Remix"

    val files: Map<String, String> = mapOf(
        "$FOLDER.toc" to """
            ## Interface: 30300
            ## Title: WowTouch
            ## Notes: The World of Warcraft app's touch controls: where the spellbook and the mounts are, for dragging them; holds as right clicks on items, talents and abilities; a talent's tooltip before its point; Report Time Anomaly and the story's fades to black on Wrath Remix; TomTom's arrow and Immersion's windows fitted to the phone's screen.
            ## Author: World of Warcraft app
            ## Version: 10
            ## OptionalDeps: TomTom, Immersion
            $FOLDER.lua
        """.trimIndent() + "\n",
        "$FOLDER.lua" to """
            -- The World of Warcraft app's touch controls (installed by the app at each start). Says
            -- where the spellbook and the mounts and companions are while they're open, so a drag
            -- that starts on them drags a spell or a mount, as the mouse does on a PC, and where the
            -- windows of items, talents and abilities are, where a hold is a right click: in an
            -- add-on message to the player itself, which the realm on the phone keeps for the app.
            -- A right click on an action bar's button takes it off the bar. A talent's first tap
            -- shows its tooltip, a second one spends the point. On Wrath Remix, Report Time Anomaly
            -- in the game's menu and on the toolbar's Help button, and the story's fades to black.

            local said
            local inWorld = false

            -- A share of the screen, in thousandths.
            local function share(value)
                return math.floor(value * 1000 + 0.5)
            end

            -- A window's place inside its edges, in thousandths of the screen from its bottom left.
            local function place(frame)
                if not frame or not frame:IsVisible() then return "-" end
                local left, bottom, width, height = frame:GetRect()
                if not left then return "-" end
                local insetLeft, insetRight, insetTop, insetBottom = frame:GetHitRectInsets()
                local scale = frame:GetEffectiveScale()
                local screenWidth = GetScreenWidth() * UIParent:GetEffectiveScale()
                local screenHeight = GetScreenHeight() * UIParent:GetEffectiveScale()
                return string.format("%d %d %d %d",
                    share((left + insetLeft) * scale / screenWidth),
                    share((bottom + insetBottom) * scale / screenHeight),
                    share((left + width - insetRight) * scale / screenWidth),
                    share((bottom + height - insetTop) * scale / screenHeight))
            end

            -- Some frames, nil ones too: { n = how many, ... }.
            local function frames(...)
                return { n = select("#", ...), ... }
            end

            -- Shown windows' places together, as one area: "<left> <bottom> <right> <top>", or nil.
            local function around(list)
                local left, bottom, right, top
                local screenWidth = GetScreenWidth() * UIParent:GetEffectiveScale()
                local screenHeight = GetScreenHeight() * UIParent:GetEffectiveScale()
                for i = 1, list.n do
                    local frame = list[i]
                    if frame and frame:IsVisible() then
                        local l, b, w, h = frame:GetRect()
                        if l then
                            local scale = frame:GetEffectiveScale()
                            l, b, w, h = l * scale / screenWidth, b * scale / screenHeight, w * scale / screenWidth, h * scale / screenHeight
                            left = math.min(left or l, l)
                            bottom = math.min(bottom or b, b)
                            right = math.max(right or l + w, l + w)
                            top = math.max(top or b + h, b + h)
                        end
                    end
                end
                if not left then return nil end
                return string.format("%d %d %d %d", share(left), share(bottom), share(right), share(top))
            end

            local function bags()
                local list = { n = NUM_CONTAINER_FRAMES or 13 }
                for i = 1, list.n do list[i] = _G["ContainerFrame" .. i] end
                return list
            end

            -- Where a drag drags: the spellbook, and the mounts and companions (the character
            -- pane's Pet tab), each inside its own edges.
            local function drags()
                local areas = {}
                for _, frame in ipairs({ SpellBookFrame, _G["PetPaperDollFrameCompanionFrame"] or false }) do
                    local area = frame and place(frame) or "-"
                    if area ~= "-" then table.insert(areas, area) end
                end
                return areas
            end

            -- Where a hold is a right click (and a double tap two clicks): the bags, the bank, the
            -- character pane, the talents, the report window, the action bars at the bottom and on
            -- the right, and the portraits (the player's and their pet's, the target's, the focus's,
            -- the party's), whose right click is their menu (trade, inspect, invite, follow...).
            local function holds()
                local areas = {}
                for _, list in ipairs({
                    bags(),
                    frames(BankFrame),
                    frames(CharacterFrame),
                    frames(PlayerTalentFrame),
                    frames(_G["WowTouchReportFrame"]),
                    frames(MainMenuBar, MultiBarBottomLeft, MultiBarBottomRight, ShapeshiftBarFrame, PetActionBarFrame),
                    frames(MultiBarRight, MultiBarLeft),
                    frames(PlayerFrame, PetFrame),
                    frames(TargetFrame, _G["TargetFrameToT"]),
                    frames(_G["FocusFrame"]),
                    frames(PartyMemberFrame1, PartyMemberFrame2, PartyMemberFrame3, PartyMemberFrame4),
                }) do
                    local area = around(list)
                    if area then table.insert(areas, area) end
                end
                return areas
            end

            -- Whether a window the player is using is open (where a double tap's jump would close it):
            -- the loot, a talk, a quest, a vendor, a trainer, the flight master's map, the mail, a
            -- trade, Immersion's, the game's questions.
            local function opened()
                for _, frame in ipairs({ LootFrame or false, GossipFrame or false, QuestFrame or false,
                        MerchantFrame or false, ClassTrainerFrame or false, TaxiFrame or false, MailFrame or false,
                        TradeFrame or false, _G["ImmersionFrame"] or false, StaticPopup1 or false }) do
                    if frame and frame.IsVisible and frame:IsVisible() then return "1" end
                end
                return "0"
            end

            -- The note: "open", then the areas. The realm keeps its first 200 characters: past that,
            -- the last hold areas are left out whole (never a number cut short).
            local NOTE_MOST = 200
            local function listed(areas)
                return #areas > 0 and table.concat(areas, " ") or "-"
            end

            local function tell()
                if not inWorld then return end
                local open, dragAreas, holdAreas = opened(), drags(), holds()
                local function compose()
                    return "open " .. open .. " drag " .. listed(dragAreas) .. " hold " .. listed(holdAreas)
                end
                local note = compose()
                while #note > NOTE_MOST and #holdAreas > 0 do
                    table.remove(holdAreas)
                    note = compose()
                end
                if note ~= said then
                    said = note
                    SendAddonMessage("$PREFIX", note, "WHISPER", UnitName("player"))
                end
            end

            -- A right click on an action bar's button (a hold, from the app) takes its action off the
            -- bar and does nothing else: its right click has no action of its own ("type2"), and
            -- after it the action is picked up and let go of. Set out of combat, as the game asks.
            local barButtons = { "ActionButton", "BonusActionButton", "MultiBarBottomLeftButton",
                "MultiBarBottomRightButton", "MultiBarRightButton", "MultiBarLeftButton" }
            local barsReady = false

            local function takeOff(button, mouseButton)
                if mouseButton ~= "RightButton" then return end
                local slot = button.action or (ActionButton_GetPagedID and ActionButton_GetPagedID(button))
                if slot and HasAction(slot) then
                    PickupAction(slot)
                    ClearCursor()
                end
            end

            local function readyBars()
                if SetCVar then SetCVar("stickyTargeting", "1") end
                if barsReady or InCombatLockdown() then return end
                for _, name in ipairs(barButtons) do
                    for i = 1, 12 do
                        local button = _G[name .. i]
                        if button then
                            button:SetAttribute("type2", "none")
                            button:HookScript("PostClick", takeOff)
                        end
                    end
                end
                barsReady = true
            end

            -- Destroying an item: the game's question ("Do you want to destroy ...?") stays up until
            -- it's answered. A tap that puts an item down outside the windows is a left click, which
            -- asks the question; the item's picture is still the cursor after it, so the app clicks
            -- the right button too, which lets go of the item, and the game closes its question as
            -- soon as the cursor holds no item. So where an item is picked up from is kept, the
            -- question no longer closes by itself, and its Yes picks the item up again first when it
            -- was let go of (only that item, still in its place; another one on the cursor stays).
            local DELETE_POPUPS = { "DELETE_ITEM", "DELETE_GOOD_ITEM", "DELETE_QUEST_ITEM", "DELETE_GOOD_QUEST_ITEM" }
            local picked, asked

            local function linkAt(place)
                if place.bag then return GetContainerItemLink(place.bag, place.slot) end
                return GetInventoryItemLink("player", place.slot)
            end

            hooksecurefunc("PickupContainerItem", function(bag, slot)
                picked = { bag = bag, slot = slot }
                picked.link = linkAt(picked)
            end)
            hooksecurefunc("PickupInventoryItem", function(slot)
                picked = { slot = slot }
                picked.link = linkAt(picked)
            end)

            -- Before the question's Yes: whether the item asked about is on the cursor (picked up
            -- again if it was let go of).
            local function holdAsked()
                if not asked then return CursorHasItem() end
                if CursorHasItem() then
                    local _, _, link = GetCursorInfo()
                    return link == asked.link
                end
                if linkAt(asked) ~= asked.link then return false end
                if asked.bag then PickupContainerItem(asked.bag, asked.slot) else PickupInventoryItem(asked.slot) end
                return CursorHasItem()
            end

            local function readyDeletes()
                if not StaticPopupDialogs then return end
                for _, which in ipairs(DELETE_POPUPS) do
                    local dialog = StaticPopupDialogs[which]
                    if dialog and not dialog.wowTouch then
                        dialog.wowTouch = true
                        dialog.OnUpdate = nil
                        local accept, enter = dialog.OnAccept, dialog.EditBoxOnEnterPressed
                        if accept then
                            dialog.OnAccept = function(...)
                                if holdAsked() then return accept(...) end
                            end
                        end
                        if enter then
                            dialog.EditBoxOnEnterPressed = function(...)
                                if holdAsked() then return enter(...) end
                            end
                        end
                    end
                end
            end
            readyDeletes()

            -- A talent's first tap shows what it does (the pointer on it shows its tooltip) and
            -- spends nothing; a second tap on the same talent soon after spends the point, as the
            -- game's own click does. The talents' window is the game's own add-on, loaded when it's
            -- first opened.
            local TALENT_AGAIN = 1.0
            local tappedTalent, tappedAt = nil, 0

            local function readyTalents()
                for i = 1, (MAX_NUM_TALENTS or 40) do
                    local button = _G["PlayerTalentFrameTalent" .. i]
                    local click = button and button:GetScript("OnClick")
                    if click and not button.wowTouch then
                        button.wowTouch = true
                        button:SetScript("OnClick", function(self, mouseButton, ...)
                            if mouseButton == "LeftButton" and not IsModifierKeyDown() then
                                local now = GetTime()
                                if tappedTalent ~= self or now - tappedAt > TALENT_AGAIN then
                                    tappedTalent, tappedAt = self, now
                                    local enter = self:GetScript("OnEnter")
                                    if enter then enter(self) end
                                    return
                                end
                                tappedTalent = nil
                            end
                            return click(self, mouseButton, ...)
                        end)
                    end
                end
            end

            -- The frames since the realm's curtain or the world's loading screen: once they have run
            -- smoothly for a while (SETTLE_SMOOTH seconds with none over SETTLE_HITCH, SETTLE_LEAST in
            -- at least), the realm is told so, once.
            local SETTLE_HITCH, SETTLE_SMOOTH, SETTLE_LEAST, SETTLE_MOST = 0.2, 1.5, 2.0, 60
            local settle

            local function watchSettling()
                if GetRealmName() ~= "$REMIX_REALM" then return end
                settle = { at = 0, smooth = 0 }
            end

            local function settling(elapsed)
                if not settle then return end
                settle.at = settle.at + elapsed
                if elapsed > SETTLE_HITCH then
                    settle.smooth = 0
                else
                    settle.smooth = settle.smooth + elapsed
                end
                if settle.at >= SETTLE_LEAST and settle.smooth >= SETTLE_SMOOTH then
                    SendAddonMessage("$REMIX_PREFIX", "settled " .. math.floor(settle.at * 1000), "WHISPER", UnitName("player"))
                    settle = nil
                elseif settle.at >= SETTLE_MOST then
                    settle = nil
                end
            end

            local watcher = CreateFrame("Frame")
            local wait = 0
            watcher:SetScript("OnUpdate", function(self, elapsed)
                settling(elapsed)
                wait = wait - elapsed
                if wait > 0 then return end
                wait = 0.1
                tell()
            end)
            -- On the Wrath Remix realm: Report Time Anomaly in the game's menu, under Macros, and on
            -- the toolbar's Help button. A window asks what went wrong, then the realm is asked for a
            -- report of the Timerunner's way so far, which the app sends to GitHub.
            local REPORT_LETTERS = 1000
            local REPORT_PIECE = 200
            local reportButton
            local menuHeight
            local reportFrame

            -- [text] in pieces of at most [size] bytes, none cut inside a letter.
            local function pieces(text, size)
                local list, i = {}, 1
                while i <= #text do
                    local j = math.min(#text, i + size - 1)
                    while j < #text and j > i do
                        local byte = string.byte(text, j + 1)
                        if byte < 128 or byte >= 192 then break end
                        j = j - 1
                    end
                    table.insert(list, string.sub(text, i, j))
                    i = j + 1
                end
                return list
            end

            local function report(text)
                text = string.gsub(text or "", "[%c]", " ")
                local list = pieces(string.sub(text, 1, REPORT_LETTERS * 4), REPORT_PIECE)
                for i = 1, #list - 1 do
                    SendAddonMessage("$REMIX_PREFIX", "report+ " .. list[i], "WHISPER", UnitName("player"))
                end
                SendAddonMessage("$REMIX_PREFIX", "report " .. (list[#list] or ""), "WHISPER", UnitName("player"))
            end

            local function reportWindow()
                if reportFrame then return reportFrame end
                local frame = CreateFrame("Frame", "WowTouchReportFrame", UIParent)
                frame:SetWidth(500)
                frame:SetHeight(340)
                frame:SetPoint("CENTER", UIParent, "CENTER", 0, 60)
                frame:SetFrameStrata("DIALOG")
                frame:SetToplevel(true)
                frame:EnableMouse(true)
                frame:SetBackdrop({
                    bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
                    edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
                    tile = true, tileSize = 32, edgeSize = 32,
                    insets = { left = 11, right = 12, top = 12, bottom = 11 },
                })
                frame:Hide()
                table.insert(UISpecialFrames, "WowTouchReportFrame")

                local title = frame:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
                title:SetPoint("TOP", frame, "TOP", 0, -20)
                title:SetText("Report a Time Anomaly")

                local about = frame:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
                about:SetPoint("TOPLEFT", frame, "TOPLEFT", 26, -46)
                about:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -26, -46)
                about:SetJustifyH("LEFT")
                about:SetText("The realm writes down where you are, the quest you're on, who you've spoken to and the way you came, and the app sends it to the realm's makers on GitHub.\n\nWhat went wrong? Write as much as you like, or leave it empty. (Tap the box, then three fingers for the keyboard.)")

                local well = CreateFrame("Frame", nil, frame)
                well:SetPoint("TOPLEFT", frame, "TOPLEFT", 22, -110)
                well:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -22, 58)
                well:SetBackdrop({
                    bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
                    edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
                    tile = true, tileSize = 16, edgeSize = 16,
                    insets = { left = 4, right = 4, top = 4, bottom = 4 },
                })
                well:SetBackdropColor(0, 0, 0, 0.8)

                local scroll = CreateFrame("ScrollFrame", "WowTouchReportScroll", well, "UIPanelScrollFrameTemplate")
                scroll:SetPoint("TOPLEFT", well, "TOPLEFT", 8, -8)
                scroll:SetPoint("BOTTOMRIGHT", well, "BOTTOMRIGHT", -28, 8)

                local box = CreateFrame("EditBox", "WowTouchReportBox", scroll)
                box:SetMultiLine(true)
                box:SetAutoFocus(false)
                box:SetMaxLetters(REPORT_LETTERS)
                box:SetFontObject(ChatFontNormal)
                box:SetWidth(410)
                box:SetHeight(150)
                -- (the game's scrolling reads where the cursor is as the text changes, which can come
                -- before the cursor's first move)
                box.cursorOffset = 0
                box.cursorHeight = 0
                box:SetScript("OnEscapePressed", function() frame:Hide() end)
                box:SetScript("OnTextChanged", function(self)
                    if ScrollingEdit_OnTextChanged then ScrollingEdit_OnTextChanged(self, scroll) end
                end)
                box:SetScript("OnCursorChanged", function(self, x, y, w, h)
                    if ScrollingEdit_OnCursorChanged then ScrollingEdit_OnCursorChanged(self, x, y, w, h) end
                end)
                box:SetScript("OnUpdate", function(self, elapsed)
                    if ScrollingEdit_OnUpdate then ScrollingEdit_OnUpdate(self, elapsed, scroll) end
                end)
                scroll:SetScrollChild(box)
                -- (a tap anywhere in the box's well puts the cursor in it)
                well:EnableMouse(true)
                well:SetScript("OnMouseDown", function() box:SetFocus() end)

                local send = CreateFrame("Button", "WowTouchReportSend", frame, "UIPanelButtonTemplate")
                send:SetWidth(140)
                send:SetHeight(24)
                send:SetPoint("BOTTOMRIGHT", frame, "BOTTOM", -8, 22)
                send:SetText("Report")
                send:SetScript("OnClick", function()
                    report(box:GetText())
                    box:ClearFocus()
                    frame:Hide()
                end)

                local cancel = CreateFrame("Button", "WowTouchReportCancel", frame, "UIPanelButtonTemplate")
                cancel:SetWidth(140)
                cancel:SetHeight(24)
                cancel:SetPoint("BOTTOMLEFT", frame, "BOTTOM", 8, 22)
                cancel:SetText(CANCEL or "Cancel")
                cancel:SetScript("OnClick", function()
                    box:ClearFocus()
                    frame:Hide()
                end)

                frame:SetScript("OnShow", function()
                    box:SetText("")
                    box:SetFocus()
                end)
                frame.box = box
                reportFrame = frame
                return frame
            end

            local function showReport()
                PlaySound("igMainMenuOption")
                if GameMenuFrame and GameMenuFrame:IsShown() then HideUIPanel(GameMenuFrame) end
                reportWindow():Show()
            end

            -- The button, in its own group between Macros and Log Out: in Log Out's place, with Log Out
            -- under it, and the menu taller by as much.
            local function addReportButton()
                if reportButton or not GameMenuFrame or not GameMenuButtonLogout then return end
                reportButton = CreateFrame("Button", "GameMenuButtonWowTouchReport", GameMenuFrame, "GameMenuButtonTemplate")
                reportButton:SetText("Report Time Anomaly")
                reportButton:SetScript("OnClick", showReport)
                local point, anchor, relativePoint, x, y = GameMenuButtonLogout:GetPoint()
                reportButton:ClearAllPoints()
                reportButton:SetPoint(point, anchor, relativePoint, x, y)
                GameMenuButtonLogout:ClearAllPoints()
                GameMenuButtonLogout:SetPoint(point, reportButton, relativePoint, x, y)
                menuHeight = GameMenuFrame:GetHeight() + reportButton:GetHeight() - y
                GameMenuFrame:SetHeight(menuHeight)
                -- (the game sizes its menu as it opens on some clients: it stays tall enough)
                GameMenuFrame:HookScript("OnShow", function(menu)
                    if menu:GetHeight() < menuHeight then menu:SetHeight(menuHeight) end
                end)
            end

            -- The toolbar's Help button (the question mark): there are no game masters on the
            -- phone's realm to ask, so it reports a time anomaly.
            local function takeHelpButton()
                if not HelpMicroButton or HelpMicroButton.wowTouch then return end
                HelpMicroButton.wowTouch = true
                HelpMicroButton:SetScript("OnClick", showReport)
                HelpMicroButton.tooltipText = "Report Time Anomaly"
                HelpMicroButton.newbieText = "Tell the realm's makers what went wrong: the realm writes down where you are and the way you came, and the app sends it to GitHub."
            end

            -- A moment of the story with the screen dark (a scene's fade to black), its words in the
            -- middle: the realm's add-on message "fade <milliseconds> <words>". The dark comes up and
            -- goes again in a second or so; the words stay while it lasts. The opening's curtain
            -- ("curtain <milliseconds> <words>") is dark at once and stays until the realm lifts it
            -- ("lift <milliseconds>": gone over that long) or its time runs out.
            local FADE_IN, FADE_OUT, LIFT = 1.2, 1.5, 2.5
            local fadeFrame

            local function fadeWindow()
                if fadeFrame then return fadeFrame end
                local frame = CreateFrame("Frame", "WowTouchFadeFrame", UIParent)
                frame:SetAllPoints(UIParent)
                frame:SetFrameStrata("FULLSCREEN_DIALOG")
                local dark = frame:CreateTexture(nil, "BACKGROUND")
                dark:SetAllPoints(frame)
                dark:SetTexture(0, 0, 0, 1)
                local words = frame:CreateFontString(nil, "ARTWORK", "GameFontHighlightLarge")
                words:SetPoint("CENTER", frame, "CENTER", 0, 40)
                words:SetWidth(640)
                words:SetJustifyH("CENTER")
                words:SetTextColor(0.86, 0.79, 0.67)
                frame.words = words
                frame:SetScript("OnUpdate", function(self, elapsed)
                    self.at = self.at + elapsed
                    if self.at >= self.lasts then
                        self:Hide()
                        return
                    end
                    local up = self.fadeIn > 0 and self.at / self.fadeIn or 1
                    self:SetAlpha(math.min(1, up, (self.lasts - self.at) / self.fadeOut))
                end)
                frame:Hide()
                fadeFrame = frame
                return frame
            end

            local function words(text)
                return string.gsub(text or "", " | ", "\n")
            end

            local function fade(seconds, text)
                local frame = fadeWindow()
                frame.at, frame.fadeIn, frame.fadeOut = 0, FADE_IN, FADE_OUT
                frame.lasts = math.max(seconds, FADE_IN + FADE_OUT)
                frame.words:SetText(words(text))
                frame:SetAlpha(0)
                frame:Show()
            end

            local function curtain(seconds, text)
                local frame = fadeWindow()
                frame.at, frame.fadeIn, frame.fadeOut = 0, 0, LIFT
                frame.lasts = math.max(seconds, LIFT)
                frame.words:SetText(words(text))
                frame:SetAlpha(1)
                frame:Show()
                watchSettling()
            end

            local function lift(seconds)
                local frame = fadeFrame
                if not frame or not frame:IsShown() then return end
                seconds = math.max(seconds, 0.1)
                frame.fadeOut = seconds
                frame.lasts = frame.at + seconds
            end

            -- Add-ons made for a PC's screen, fitted to the phone's (they load before this one: the
            -- .toc's OptionalDeps). TomTom's arrow goes to the top of the screen, in the middle:
            -- TomTom puts it in the middle of the screen, over the character. Where the player has
            -- dragged it, it stays (the game keeps that place, and the arrow is then user-placed).
            -- Immersion's quest and gossip choices and its talking box stay on the screen, 16 from
            -- its edges: Immersion puts the choices 500 to the right of the middle, which on a
            -- phone's screen (narrower than a PC's, the interface bigger) is partly past its edge.
            local ARROW_TOP, EDGE, CHOICE_WIDTH = -36, 16, 310

            -- Immersion's choices sit at an offset from the middle of the screen (its setting
            -- titleoffset, 500 at first; a drag sets it anew). Where that puts them past the edge,
            -- they come in to 16 from it, and Immersion keeps that place (its setting): each time
            -- they show, as the screen's width can change (the Fold opened or closed).
            local function fitImmersionChoices(titles)
                local point, to, toPoint, x, y = titles:GetPoint()
                if type(x) ~= "number" then return end
                local scale = titles:GetEffectiveScale() / UIParent:GetEffectiveScale()
                local room = math.max(0, GetScreenWidth() / scale / 2 - CHOICE_WIDTH / 2 - EDGE)
                if math.abs(x) <= room then return end
                x = x > 0 and room or -room
                titles:ClearAllPoints()
                titles:SetPoint(point, to, toPoint, x, y)
                if type(ImmersionSetup) == "table" then ImmersionSetup.titleoffset = x end
            end

            local function fitAddons()
                local arrow = TomTomCrazyArrow
                if arrow and not arrow.wowTouchFitted then
                    arrow.wowTouchFitted = true
                    arrow:SetClampedToScreen(true)
                    if not arrow:IsUserPlaced() then
                        arrow:ClearAllPoints()
                        arrow:SetPoint("TOP", UIParent, "TOP", 0, ARROW_TOP)
                    end
                end
                local immersion = ImmersionFrame
                if immersion and not immersion.wowTouchFitted then
                    immersion.wowTouchFitted = true
                    for _, part in ipairs({ immersion.TitleButtons, immersion.TalkBox }) do
                        -- (the choices are 310 wide on a list 300 wide: the margin keeps them in too)
                        part:SetClampedToScreen(true)
                        part:SetClampRectInsets(-EDGE, EDGE, EDGE, -EDGE)
                    end
                    local titles = immersion.TitleButtons
                    fitImmersionChoices(titles)
                    titles:HookScript("OnShow", fitImmersionChoices)
                end
            end

            watcher:RegisterEvent("PLAYER_ENTERING_WORLD")
            watcher:RegisterEvent("PLAYER_LEAVING_WORLD")
            watcher:RegisterEvent("PLAYER_REGEN_ENABLED")
            watcher:RegisterEvent("ADDON_LOADED")
            watcher:RegisterEvent("CHAT_MSG_ADDON")
            watcher:RegisterEvent("DELETE_ITEM_CONFIRM")
            watcher:SetScript("OnEvent", function(self, event, name, message, channel, sender)
                if event == "DELETE_ITEM_CONFIRM" then
                    -- (the item on the cursor, when the question comes up)
                    asked = picked and CursorHasItem() and picked.link and select(3, GetCursorInfo()) == picked.link and picked or nil
                    readyDeletes()
                    return
                end
                if event == "CHAT_MSG_ADDON" then
                    -- (the realm's, to the player itself)
                    if name == "$REMIX_PREFIX" and sender == UnitName("player") then
                        local ms, text = string.match(message or "", "^fade (%d+) ?(.*)")
                        if ms then fade(tonumber(ms) / 1000, text) end
                        ms, text = string.match(message or "", "^curtain (%d+) ?(.*)")
                        if ms then curtain(tonumber(ms) / 1000, text) end
                        ms = string.match(message or "", "^lift (%d+)")
                        if ms then lift(tonumber(ms) / 1000) end
                    end
                    return
                end
                if event == "PLAYER_REGEN_ENABLED" then
                    readyBars()
                    return
                end
                if event == "ADDON_LOADED" then
                    if name == "Blizzard_TalentUI" then readyTalents() end
                    if name == "TomTom" or name == "Immersion" then fitAddons() end
                    return
                end
                inWorld = event == "PLAYER_ENTERING_WORLD"
                said = nil
                tell()
                if inWorld then
                    fitAddons()
                    readyBars()
                    readyTalents()
                    watchSettling()
                else
                    settle = nil
                end
                if inWorld and GetRealmName() == "$REMIX_REALM" then
                    addReportButton()
                    takeHelpButton()
                end
            end)
        """.trimIndent() + "\n",
    )
}
