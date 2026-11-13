// SPDX-License-Identifier: MIT
// Wrath++'s native mod for the stock 32-bit 3.3.5a client (build 12340), under WarcraftXL's runtime.
//
// The character creator's interface can step a customization (CycleCharCustomization) but can't read
// which choice is on or how many there are, which Legion's creator shows in each of its boxes. This
// reads them where the client keeps them, and gives the interface:
//
//   WrathPP_GetCustomization(i)  i: 1 skin colour, 2 face, 3 hair style, 4 hair colour, 5 facial hair
//                                (NUM_CHAR_CUSTOMIZATIONS' order) -> current (1-based), count; nothing
//                                while no character is on the creator.
//   WrathPP_SetCustomization(i, n)  puts choice n (1-based) of customization i into the character being made, as a
//                                number alone: nothing is drawn. The creator puts in the choice BEFORE the one it wants
//                                and calls the game's own CycleCharCustomization(i, 1), whose "next" (SetNextSkin,
//                                SetNextFace... at the client's pinned source) then moves onto the wanted one through
//                                the client's own checks and redraws: one step in place of up to a hundred.
//                                -> true, or nothing while no character is on the creator or n is past the count.
//   WrathPP_GetCreating()        -> race id, sex (0 a man, 1 a woman), class id of the character being made.
//   WrathPP_SetGear(on)          the character being made with its starting outfit (true) or without (false), to see
//                                the skin. Without: what the client's own CCharacterCreation::Dress does first, the
//                                twelve item slots taken off (CCharacterComponent::RemoveItem, 0x004EE460, thiscall:
//                                the address WarcraftXL's own Component.RemoveItem seam attaches at). With: Dress
//                                itself (0x004E0FD0, a static function without arguments), which takes them off and
//                                puts the class's outfit on. Nothing is drawn until the creator's next step of a
//                                customization (the client's StartLoad). -> true, or nothing while no character is on it.
//   WrathPP_Log(text)            a line of the creator's into the runtime's log, tagged wrathpp, "creator: text": what
//                                the creator did (built, opened, which screen, why it went off), for the app's reports.
//   WrathPP_SetScreen(text)      the creator's word to the app on what is on the screen: "creator 1 drag <left bottom
//                                right top>..." while it is up (where a finger drags a list, in thousandths of the screen
//                                from its bottom left), "creator 0" when it is not. Written whole (a file beside it, then
//                                moved over it) to Logs\wrathpp-screen.txt beside the game; the app's touch reads it
//                                (WowGestureView): on the creator a finger turns the character and walks nowhere.
//   WrathPP_NativeVersion()      -> this mod's version, for the interface to know it is there.
//
// Addresses and layouts: WarcraftXL-Labs/core's offset tables and the decompiled client
// (docs/wrathpp/CLIENT_PROBE.md), both at the commits wrathpp.env pins:
//   CCharacterCreation::m_character            0x00B6B1A0   CCharacterComponent*
//   CCharacterComponent::m_data                +0x18        ComponentData, its CharacterPreferences first:
//     race +0x00, sex +0x04, class +0x08, hair colour +0x0C, skin +0x10, face +0x14, facial hair +0x18, hair style +0x1C
//   CCharacterComponent::GetNumSkins           0x004E7B80   (race, sex, class, context)
//   ::GetNumHairStylesForColor                 0x004E7C10   (race, sex, class, hairColor, context)
//   ::GetNumHairColorsForStyle                 0x004E7CB0   (race, sex, class, hairStyle, context)
//   ::GetNumFacesForSkin                       0x004E7D50   (race, sex, class, skin, context)
//   ::GetNumFacialFeaturesForHairColor         0x004E7DF0   (race, sex, class, hairColor, context)
// The counts are static member functions: cdecl (the decompilation's x86 build matches their bytes).
// The creator uses context 0 (COMPONENT_CONTEXT_0), as CCharacterCreation's own calls do.

#include <cstdint>
#include <string>
#include <utility>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#endif

#include "wxl/sdk.hpp"
#include "wxl/services/script.hpp"

namespace
{
    constexpr const char* kTag = "wrathpp";

#if defined(_M_IX86)
    using Count4 = int32_t(__cdecl*)(int32_t, int32_t, int32_t, int32_t);
    using Count5 = int32_t(__cdecl*)(int32_t, int32_t, int32_t, int32_t, int32_t);

    struct Preferences
    {
        uint32_t race, sex, classId, hairColor, skin, face, facialHair, hairStyle;
    };

    Preferences* Creating()
    {
        const uintptr_t component = *reinterpret_cast<const uintptr_t*>(0x00B6B1A0);
        if (!component) return nullptr;
        return reinterpret_cast<Preferences*>(component + 0x18);
    }

    /// The current choice (0-based) and how many there are, for customization 0..4.
    bool Customization(int which, int32_t& current, int32_t& count)
    {
        const Preferences* p = Creating();
        if (!p) return false;
        const int32_t race = static_cast<int32_t>(p->race), sex = static_cast<int32_t>(p->sex), cls = static_cast<int32_t>(p->classId);
        switch (which)
        {
        case 0:
            current = static_cast<int32_t>(p->skin);
            count   = reinterpret_cast<Count4>(0x004E7B80)(race, sex, cls, 0);
            return true;
        case 1:
            current = static_cast<int32_t>(p->face);
            count   = reinterpret_cast<Count5>(0x004E7D50)(race, sex, cls, static_cast<int32_t>(p->skin), 0);
            return true;
        case 2:
            current = static_cast<int32_t>(p->hairStyle);
            count   = reinterpret_cast<Count5>(0x004E7C10)(race, sex, cls, static_cast<int32_t>(p->hairColor), 0);
            return true;
        case 3:
            current = static_cast<int32_t>(p->hairColor);
            count   = reinterpret_cast<Count5>(0x004E7CB0)(race, sex, cls, static_cast<int32_t>(p->hairStyle), 0);
            return true;
        case 4:
            current = static_cast<int32_t>(p->facialHair);
            count   = reinterpret_cast<Count5>(0x004E7DF0)(race, sex, cls, static_cast<int32_t>(p->hairColor), 0);
            return true;
        default:
            return false;
        }
    }

    /// Customization 0..4's number put in (0-based, below its count). The game draws nothing until its own next step.
    bool SetCustomization(int which, int32_t value)
    {
        int32_t current = 0, count = 0;
        if (!Customization(which, current, count) || value < 0 || value >= count) return false;
        Preferences* p = Creating();
        switch (which)
        {
        case 0: p->skin = static_cast<uint32_t>(value); return true;
        case 1: p->face = static_cast<uint32_t>(value); return true;
        case 2: p->hairStyle = static_cast<uint32_t>(value); return true;
        case 3: p->hairColor = static_cast<uint32_t>(value); return true;
        case 4: p->facialHair = static_cast<uint32_t>(value); return true;
        default: return false;
        }
    }

    using RemoveItemFn = void(__thiscall*)(void*, int32_t);
    using DressFn = void(__cdecl*)();

    bool SetGear(bool on)
    {
        const uintptr_t component = *reinterpret_cast<const uintptr_t*>(0x00B6B1A0);
        if (!component) return false;
        if (on)
        {
            reinterpret_cast<DressFn>(0x004E0FD0)();
            return true;
        }
        for (int32_t slot = 0; slot < 12; slot++) // NUM_ITEM_SLOTS
            reinterpret_cast<RemoveItemFn>(0x004EE460)(reinterpret_cast<void*>(component), slot);
        return true;
    }

    bool CreatingWho(int32_t& race, int32_t& sex, int32_t& cls)
    {
        const Preferences* p = Creating();
        if (!p) return false;
        race = static_cast<int32_t>(p->race); sex = static_cast<int32_t>(p->sex); cls = static_cast<int32_t>(p->classId);
        return true;
    }
#else
    bool Customization(int, int32_t&, int32_t&) { return false; }
    bool SetCustomization(int, int32_t) { return false; }
    bool CreatingWho(int32_t&, int32_t&, int32_t&) { return false; }
    bool SetGear(bool) { return false; }
#endif

    void GetCustomization(wxl::ScriptCall& call)
    {
        const auto index = call.Number(0);
        if (!index || *index < 1 || *index > 5)
        {
            call.Fail("WrathPP_GetCustomization(i): i is 1 to 5");
            return;
        }
        int32_t current = 0, count = 0;
        if (!Customization(static_cast<int>(*index) - 1, current, count)) return;
        call.PushNumber(static_cast<double>(current) + 1.0);
        call.PushNumber(static_cast<double>(count));
    }

    void SetCustomizationCall(wxl::ScriptCall& call)
    {
        const auto index = call.Number(0);
        const auto value = call.Number(1);
        if (!index || *index < 1 || *index > 5 || !value)
        {
            call.Fail("WrathPP_SetCustomization(i, n): i is 1 to 5, n a choice from 1");
            return;
        }
        if (!SetCustomization(static_cast<int>(*index) - 1, static_cast<int32_t>(*value) - 1)) return;
        call.PushBool(true);
    }

    void GetCreating(wxl::ScriptCall& call)
    {
        int32_t race = 0, sex = 0, cls = 0;
        if (!CreatingWho(race, sex, cls)) return;
        call.PushNumber(static_cast<double>(race));
        call.PushNumber(static_cast<double>(sex));
        call.PushNumber(static_cast<double>(cls));
    }

    void SetGearCall(wxl::ScriptCall& call)
    {
        const auto on = call.Bool(0);
        if (!on)
        {
            call.Fail("WrathPP_SetGear(on): on is true or false");
            return;
        }
        if (!SetGear(*on)) return;
        call.PushBool(true);
    }

    /// A line of the creator's into the runtime's log (Logs/WarcraftXL.log), which the app's reports carry.
    void LogCall(wxl::ScriptCall& call)
    {
        const auto text = call.String(0);
        if (!text)
        {
            call.Fail("WrathPP_Log(text): text is a string");
            return;
        }
        wxl::Log(WXL_LOG_INFO, kTag, "creator: {}", text->substr(0, 400));
    }

#if defined(_WIN32)
    /// Logs\wrathpp-screen.txt beside the game's program, written whole: [text] into a file beside it, then moved over it.
    bool WriteScreen(const std::string& text)
    {
        wchar_t exe[MAX_PATH];
        const DWORD n = GetModuleFileNameW(nullptr, exe, MAX_PATH);
        if (n == 0 || n >= MAX_PATH) return false;
        std::wstring dir(exe, n);
        const auto slash = dir.find_last_of(L"\\/");
        if (slash == std::wstring::npos) return false;
        dir.resize(slash + 1);
        dir += L"Logs";
        CreateDirectoryW(dir.c_str(), nullptr);
        const std::wstring target = dir + L"\\wrathpp-screen.txt";
        const std::wstring part = target + L".part";
        HANDLE file = CreateFileW(part.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
        if (file == INVALID_HANDLE_VALUE) return false;
        DWORD written = 0;
        const bool ok = WriteFile(file, text.data(), static_cast<DWORD>(text.size()), &written, nullptr) && written == text.size();
        FlushFileBuffers(file);
        CloseHandle(file);
        return ok && MoveFileExW(part.c_str(), target.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH);
    }
#else
    bool WriteScreen(const std::string&) { return false; }
#endif

    void SetScreenCall(wxl::ScriptCall& call)
    {
        const auto text = call.String(0);
        if (!text)
        {
            call.Fail("WrathPP_SetScreen(text): text is a string");
            return;
        }
        if (!WriteScreen(std::string(text->substr(0, 2000)) + "\n")) return;
        call.PushBool(true);
    }

    void NativeVersion(wxl::ScriptCall& call) { call.PushString("0.4.0"); }

    class Api final : public wxl::LuaScript
    {
    public:
        void OnScriptVmReady(wxl_script_context, void*) override
        {
            const wxl::ScriptService script;
            if (!script) return;
            for (auto [name, result] : {std::pair{"WrathPP_GetCustomization", script.RegisterFunction<&GetCustomization>("WrathPP_GetCustomization")},
                                        std::pair{"WrathPP_SetCustomization", script.RegisterFunction<&SetCustomizationCall>("WrathPP_SetCustomization")},
                                        std::pair{"WrathPP_GetCreating", script.RegisterFunction<&GetCreating>("WrathPP_GetCreating")},
                                        std::pair{"WrathPP_SetGear", script.RegisterFunction<&SetGearCall>("WrathPP_SetGear")},
                                        std::pair{"WrathPP_Log", script.RegisterFunction<&LogCall>("WrathPP_Log")},
                                        std::pair{"WrathPP_SetScreen", script.RegisterFunction<&SetScreenCall>("WrathPP_SetScreen")},
                                        std::pair{"WrathPP_NativeVersion", script.RegisterFunction<&NativeVersion>("WrathPP_NativeVersion")}})
            {
                if (result != WXL_OK) wxl::Log(WXL_LOG_WARN, kTag, "could not register {}: {}", name, wxl::ResultName(result));
            }
        }
    };

    Api g_api;

    class NativeMod final : public wxl::Mod
    {
    public:
        wxl_result OnLoad() override
        {
            wxl::ScriptMgr::Add(&g_api);
            wxl::Log(WXL_LOG_INFO, kTag, "Wrath++ native loaded");
            return WXL_OK;
        }
    };
} // namespace

WXL_MOD(NativeMod, "wrathpp.native", "Wrath++ native")
