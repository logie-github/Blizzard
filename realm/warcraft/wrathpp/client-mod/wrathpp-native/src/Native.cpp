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
#include <utility>

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

    const Preferences* Creating()
    {
        const uintptr_t component = *reinterpret_cast<const uintptr_t*>(0x00B6B1A0);
        if (!component) return nullptr;
        return reinterpret_cast<const Preferences*>(component + 0x18);
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
#else
    bool Customization(int, int32_t&, int32_t&) { return false; }
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

    void NativeVersion(wxl::ScriptCall& call) { call.PushString("0.1.0"); }

    class Api final : public wxl::LuaScript
    {
    public:
        void OnScriptVmReady(wxl_script_context, void*) override
        {
            const wxl::ScriptService script;
            if (!script) return;
            for (auto [name, result] : {std::pair{"WrathPP_GetCustomization", script.RegisterFunction<&GetCustomization>("WrathPP_GetCustomization")},
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
