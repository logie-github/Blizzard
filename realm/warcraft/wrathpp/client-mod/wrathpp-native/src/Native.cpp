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
//   WrathPP_ApplyLook(guid, shell1, picture1, ... shell8, picture8)
//                                the parts a character of the world wears (the add-on's WRATHPP_APPEARANCE: its registry choices
//                                made paths by the parts table, Wrathpp\parts.txt): head shells hung on the model the character
//                                draws with (wxl.m2's ObjectModel, WXL_M2_ATTACH_FOLLOW_BONES), each with its picture; "" for none.
//                                guid: "0x" and sixteen hex digits. Kept every quarter second; let go with the model.
//   WrathPP_NativeVersion()      -> this mod's version, for the interface to know it is there.
//   WrathPP_MaxRace()            -> the highest race id the client's creation screen can hold: 21 as it is, 63 where this mod moved
//                                the saved choices' array (below).
//
// And, with no function to call: the body options' layer (realm/warcraft/wrathpp/tools/body_shapes/layer.py) shown on a
// character with nothing on its legs. The layer is geoset 1901 of the looks' women's models, which the client's
// CCharacterComponent::GeosRenderPrep (0x004ED900, thiscall, no arguments) hides with every geoset to 2000 and nothing
// of the game's shows. A detour at its end (wxl.hook.raw) shows it when
//   - the component's model is loaded (CM2Model::m_fFlags +0x10, bit 1) and is one with the layer: its last texture
//     (CM2Shared +0x150 m_data, M2Data +0x50 m_textures, 16 bytes each, its type first) is type 11, the display's
//     design (CCharacterComponent::ReplaceMonsterSkin puts it in from the display's TextureVariation_1);
//   - a display put that texture in (CM2Model +0xA4 m_textures[last] is not the model file's own, CM2Shared +0x174
//     m_textures[last]: the empty design the layer names, which a creature's model or the character screens' keep; the
//     race's own display puts in the empty design too, a body options display the style's);
//   - and the component's legs slot is empty (CCharacterComponent +0x428 m_itemDisplayID[12], ITEMSLOT_PANTS 5).
// Then CM2Model::SetGeometryVisible(1901, 1901, 1) (0x0082C7C0, thiscall) and OptimizeVisibleGeometry (0x0082C970,
// thiscall), as GeosRenderPrep itself ends. Every read is guarded (structured exceptions): a client whose layout
// differs shows no layer and keeps running. Addresses and layouts: the pinned decompilation (CharacterComponent.h,
// ComponentData.h, M2Model.h, M2Shared.h, M2Data.h); NOT run in the game.
//
// And the creatures' skins. A creature drawn with a race's model (CreatureDisplayInfoExtra) gets a texture baked for the model
// 3.3.5 had: CGUnit_C::InitializeExtendedDisplay (0x0071D010) sets ComponentData's flag 1 and m_npcSkinTexture
// ("Textures\\BakedNpcTextures\\" and the row's BakeName), and CCharacterComponent::Init (0x004F24D0, thiscall: data, debug) then
// calls SkinNpc (0x004F1FC0), which puts that file on as the whole skin; with the flag on, nothing is composed (SetSkinColor,
// SetFace, the item textures all return early). On the looks' models the head is laid out otherwise, so the baked face lies in
// the wrong place (the user's pictures of 18 November 2026: Keina, Conservator Ilthalaine). A detour on Init takes the flag and
// the name off for the races and sexes whose model is the looks' (Wrathpp\\npc.txt in the looks' package: "race<TAB>sex" a line,
// read once through wxl.storage when the first such creature is made), and the game composes the creature's skin as it does a
// player's: the skin, face and hair of the row's five numbers (which the looks' change file has made the looks' own:
// sl_looks.py npc_changes) and its items' textures (InitializeComponent's AddItem of the row's eleven item displays, which
// composes them when the flag is off). No list, no storage or no hook: every creature keeps its baked texture, as before.
// Compiled by CI only; NOT run in the game.
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
#include <cstdlib>
#include <atomic>
#include <cctype>
#include <cmath>
#include <map>
#include <mutex>
#include <optional>
#include <set>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#endif

#include "wxl/objects.hpp"
#include "wxl/sdk.hpp"
#include "wxl/services/hook.hpp"
#include "wxl/services/m2.hpp"
#include "wxl/services/script.hpp"
#include "wxl/services/storage.hpp"

namespace
{
    constexpr const char* kTag = "wrathpp";
    constexpr int kPartSlots = 8;            // the parts a character can wear at once (a head shell and a body shell for each option drawn so)

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

    // --- the body options' layer -------------------------------------------------------------------------------------
    constexpr uint32_t kLayerGeoset = 1901;
    constexpr uint32_t kDesignTexture = 11;
    using GeosRenderPrepFn = void(__thiscall*)(void*);
    using SetGeometryVisibleFn = void(__thiscall*)(void*, uint32_t, uint32_t, int32_t);
    using OptimizeFn = void(__thiscall*)(void*);
    GeosRenderPrepFn g_geosRenderPrep = nullptr;
    wxl::Hook g_layerHook;

    /// The model to show the layer on, or null: loaded, the layer's, its design in, nothing on the legs.
    uintptr_t LayerModel(uintptr_t component)
    {
        __try
        {
            const uintptr_t model = *reinterpret_cast<const uintptr_t*>(component + 0x18 + 0x20);
            if (!model || !(*reinterpret_cast<const uint32_t*>(model + 0x10) & 1)) return 0;
            if (*reinterpret_cast<const uint32_t*>(component + 0x428 + 5 * 4)) return 0;
            const uintptr_t shared = *reinterpret_cast<const uintptr_t*>(model + 0x2C);
            const uintptr_t data = shared ? *reinterpret_cast<const uintptr_t*>(shared + 0x150) : 0;
            if (!data) return 0;
            const uint32_t count = *reinterpret_cast<const uint32_t*>(data + 0x50);
            if (!count || count > 64) return 0;
            const uintptr_t textures = data + 0x50 + static_cast<uintptr_t>(static_cast<intptr_t>(*reinterpret_cast<const int32_t*>(data + 0x54)));
            if (*reinterpret_cast<const uint32_t*>(textures + (count - 1) * 16) != kDesignTexture) return 0;
            // the model's design: the display's when one was put in, else the same texture as the model file's own
            // (CM2Model::InitializeLoaded copies the shared one's handle: HandleDuplicate returns it as it is)
            const uintptr_t mine = *reinterpret_cast<const uintptr_t*>(model + 0xA4);
            const uintptr_t own = *reinterpret_cast<const uintptr_t*>(shared + 0x174);
            if (!mine || !own) return 0;
            const uintptr_t design = *reinterpret_cast<const uintptr_t*>(mine + (count - 1) * 4);
            if (!design || design == *reinterpret_cast<const uintptr_t*>(own + (count - 1) * 4)) return 0;
            return model;
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
            return 0;
        }
    }

    void ShowLayer(uintptr_t model)
    {
        __try
        {
            reinterpret_cast<SetGeometryVisibleFn>(0x0082C7C0)(reinterpret_cast<void*>(model), kLayerGeoset, kLayerGeoset, 1);
            reinterpret_cast<OptimizeFn>(0x0082C970)(reinterpret_cast<void*>(model));
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
        }
    }

    // The creator's own preview of the body options' design (the realm's displays carry it in the world; the creator's
    // character is a component, not a display): the Lua says which design file the woman being made has
    // (WrathPP_SetBodyPreview), and the creation component's model takes it as texture type 11, through wxl.m2. The layer
    // is then drawn as for any model whose design is not the model file's own (LayerModel), where nothing is on her legs.
    std::string g_previewDesign;       // "" for no preview (the model keeps what it has)
    uintptr_t   g_previewModel = 0;    // the model the design was last put on
    std::string g_previewApplied;      // and which

    uintptr_t CreationComponent()
    {
        __try { return *reinterpret_cast<const uintptr_t*>(0x00B6B1A0); }
        __except (EXCEPTION_EXECUTE_HANDLER) { return 0; }
    }

    uintptr_t ComponentModel(uintptr_t component)
    {
        __try { return component ? *reinterpret_cast<const uintptr_t*>(component + 0x18 + 0x20) : 0; }
        __except (EXCEPTION_EXECUTE_HANDLER) { return 0; }
    }

    // The client's own calls, as the runtime's binding makes them (corex's BindingX86 m2_replace_texture; the runtime's wxl.m2
    // takes only models it made itself, which the creation component's is not: its ReplaceTexture answered WXL_E_INVALID on the
    // phone). GetGlobalStatusObj (0x0047C090) and CCharacterComponent's CreateTexture (0x004E8D30) are cdecl, as is HandleClose
    // (0x0047BF30); CM2Model::ReplaceTexture (0x00825260) is thiscall, `ret 8`. The model takes a handle of its own.
    using StatusFn = void*(__cdecl*)();
    using CreateTextureFn = void*(__cdecl*)(const char*, void*);
    using ReplaceTextureFn = void(__thiscall*)(void*, uint32_t, void*);
    using CloseFn = void(__cdecl*)(void*);

    bool ReplaceDesign(uintptr_t model, const char* path)
    {
        __try
        {
            void* status = reinterpret_cast<StatusFn>(0x0047C090)();
            void* texture = reinterpret_cast<CreateTextureFn>(0x004E8D30)(path, status);
            if (!texture) return false;
            reinterpret_cast<ReplaceTextureFn>(0x00825260)(reinterpret_cast<void*>(model), kDesignTexture, texture);
            reinterpret_cast<CloseFn>(0x0047BF30)(texture);
            return true;
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
            return false;
        }
    }

    /// Puts the preview's design on the creation component's model, once for each model and design.
    void ApplyPreview(uintptr_t component)
    {
        if (g_previewDesign.empty() || component != CreationComponent()) return;
        const uintptr_t model = ComponentModel(component);
        if (!model || (model == g_previewModel && g_previewApplied == g_previewDesign)) return;
        if (ReplaceDesign(model, g_previewDesign.c_str()))
        {
            g_previewModel = model;
            g_previewApplied = g_previewDesign;
        }
        else if (g_previewApplied != g_previewDesign)
        {
            g_previewApplied = g_previewDesign;
            wxl::Log(WXL_LOG_WARN, kTag, "body preview: {} not put on", g_previewDesign);
        }
    }

    /// Whether a CM2Model has loaded (its flags' first bit). (No object with a destructor beside a __try: MSVC's C2712.)
    bool ModelLoaded(uintptr_t model)
    {
        __try { return model && (*reinterpret_cast<const uint32_t*>(model + 0x10) & 1); }
        __except (EXCEPTION_EXECUTE_HANDLER) { return false; }
    }

    /// Once, when the creation component's model has loaded: whether this runtime lets a model skinned to a character's
    /// skeleton be hung on it (wxl.m2's WXL_M2_ATTACH_FOLLOW_BONES), which the options that are parts of the model (hair,
    /// horns, markings) would be made of; the answer is in the log (Wrath++'s start report carries it). An empty model
    /// of the game's, taken off again at once.
    void ProbeBones(uintptr_t component)
    {
        static bool done = false;
        if (done || component != CreationComponent()) return;
        const uintptr_t model = ComponentModel(component);
        if (!ModelLoaded(model)) return;
        done = true;
        wxl::M2Model probe(reinterpret_cast<void*>(model), "Spells\\Blank.mdx");
        if (!probe)
        {
            wxl::Log(WXL_LOG_INFO, kTag, "bones probe: wxl.m2 made no model");
            return;
        }
        const wxl_result hung = probe.Attach(reinterpret_cast<void*>(model), 0, WXL_M2_ATTACH_ROOT | WXL_M2_ATTACH_FOLLOW_BONES);
        wxl::Log(WXL_LOG_INFO, kTag, "bones probe: a model that follows the character's bones {} ({})",
                 hung == WXL_OK ? "can be hung" : "can not be hung", wxl::ResultName(hung));
    }

    // The pictures laid over the head (eyebrows, makeup, scars: realm/warcraft/wrathpp/tools/sl_parts.py): for each, a head
    // shell, a model of the mod's own hung on the creation component's model so that the character's bones pose it every frame
    // (wxl.m2, WXL_M2_ATTACH_FOLLOW_BONES), with the picture put on it as texture type 11 (the runtime knows the models it made:
    // it answers for this one). The Lua says which (WrathPP_SetOverlay); they are made again whenever the character's model is.
    struct OverlayPart
    {
        std::string wantShell, wantPicture;     // what the Lua asked for ("" for none); the picture is texture type 11
        std::string wantPicture12, wantPicture13;   // the hair's (type 12) and a customization's (type 13) pictures of a part that has them
        int wantChoice = 0;                     // 0 the whole model, else which choice's geosets show (ids choice * 100 to choice * 100 + 99)
        uint32_t wantAttach = 0;                // 0 posed by the character's bones, else hung on that attachment point (the helm's, 11: horns, blindfolds)
        uint32_t attach = 0;
        std::string shell, picture, picture12, picture13;   // what is on
        int choice = -1;
        uintptr_t parent = 0;
        wxl::M2Model model;
    };
    OverlayPart g_overlays[kPartSlots];

    /// Keeps one part on a model: made and hung when there is none on [parent] (a new model of the character: made again),
    /// its picture put on when it is not. [parent] 0 or not loaded: nothing now. [what]: the log's name for it.
    void SyncPart(OverlayPart& part, uintptr_t parent, const char* what, int index)
    {
        if (part.wantShell.empty())
        {
            if (part.model) { part.model.Reset(); part.parent = 0; part.shell.clear(); part.picture.clear(); part.picture12.clear(); part.picture13.clear(); part.choice = -1; }
            return;
        }
        if (!parent || !ModelLoaded(parent)) return;
        if (!part.model || part.parent != parent || part.shell != part.wantShell || part.attach != part.wantAttach || !part.model.Parent())
        {
            part.model.Reset();
            part.model = wxl::M2Model(reinterpret_cast<void*>(parent), part.wantShell);
            part.parent = parent;
            part.shell = part.wantShell;
            part.picture.clear(); part.picture12.clear(); part.picture13.clear(); part.choice = -1;
            if (!part.model) { wxl::Log(WXL_LOG_WARN, kTag, "{} {}: wxl.m2 made no model of {}", what, index, part.wantShell); return; }
            part.attach = part.wantAttach;
            const wxl_result hung = part.attach
                ? part.model.Attach(reinterpret_cast<void*>(parent), part.attach, 0)
                : part.model.Attach(reinterpret_cast<void*>(parent), 0, WXL_M2_ATTACH_ROOT | WXL_M2_ATTACH_FOLLOW_BONES);
            wxl::Log(WXL_LOG_INFO, kTag, "{} {}: {} hung on the character ({})", what, index, part.shell, wxl::ResultName(hung));
        }
        if (!part.model) return;
        const struct { uint32_t type; const std::string& want; std::string& has; } pictures[] = {
            {11, part.wantPicture, part.picture}, {12, part.wantPicture12, part.picture12}, {13, part.wantPicture13, part.picture13}};
        for (const auto& p : pictures)
        {
            if (p.has == p.want || p.want.empty()) continue;
            const wxl_result put = part.model.ReplaceTexture(p.type, p.want);
            p.has = p.want;
            if (put != WXL_OK) wxl::Log(WXL_LOG_WARN, kTag, "{} {}: {} not put on as type {} ({})", what, index, p.want, p.type, wxl::ResultName(put));
        }
        if (part.choice != part.wantChoice)
        {
            // a model of several choices' geosets: only the chosen one's show (a choice's ids are choice * 100 and up)
            part.model.SetGeosets(0, 65535, part.wantChoice == 0);
            if (part.wantChoice > 0) part.model.SetGeosets(static_cast<uint32_t>(part.wantChoice) * 100, static_cast<uint32_t>(part.wantChoice) * 100 + 99, true);
            part.choice = part.wantChoice;
        }
    }

    void SyncOverlays(uintptr_t component)
    {
        if (component != CreationComponent()) return;
        const uintptr_t parent = ComponentModel(component);
        for (int i = 0; i < kPartSlots; ++i) SyncPart(g_overlays[i], parent, "overlay", i + 1);
    }

    // The characters of the world (WrathPP_ApplyLook): the same parts, on the model each draws with (wxl.m2's ObjectModel), for
    // every guid the add-on has told of; kept at the pace of a few times a second, and let go when the character leaves the view
    // (a model comes again with the object) or the world.
    constexpr int kWorldParts = kPartSlots;
    struct WorldLook
    {
        OverlayPart parts[kWorldParts];
    };
    std::map<uint64_t, WorldLook> g_world;
    std::set<uint64_t> g_mounted;           // the units that are mounted: wxl.m2's ObjectModel answers the mount's model for them, which isn't theirs to wear parts on

    void SyncWorld()
    {
        for (auto it = g_world.begin(); it != g_world.end();)
        {
            WorldLook& look = it->second;
            const wxl::Object object = wxl::Object::Resolve(it->first);
            bool any = false;
            for (const OverlayPart& part : look.parts) any = any || !part.wantShell.empty();
            if (!any)
            {
                it = g_world.erase(it);
                continue;
            }
            uintptr_t parent = 0;
            if (object && !g_mounted.count(it->first)) parent = reinterpret_cast<uintptr_t>(wxl::M2Service::ObjectModel(object));
            for (int i = 0; i < kWorldParts; ++i)
            {
                OverlayPart& part = look.parts[i];
                if (!parent)
                {
                    if (part.model) { part.model.Reset(); part.parent = 0; part.shell.clear(); part.picture.clear(); part.picture12.clear(); part.picture13.clear(); part.choice = -1; }
                    continue;
                }
                SyncPart(part, parent, "world part", i + 1);
            }
            ++it;
        }
    }

    class World final : public wxl::WorldScript
    {
    public:
        void OnUpdate(float delta) override
        {
            wait_ -= delta;
            if (wait_ > 0.0f || g_world.empty()) return;
            wait_ = 0.25f;
            SyncWorld();
        }
        // The world's models go with it; the looks stay and are made again on the way back in.
        void OnWorldLeave(uint32_t, wxl_vec3) override
        {
            for (auto& entry : g_world)
                for (OverlayPart& part : entry.second.parts) { part.model.Reset(); part.parent = 0; part.shell.clear(); part.picture.clear(); part.picture12.clear(); part.picture13.clear(); part.choice = -1; }
        }

    private:
        float wait_ = 0.0f;
    };
    World g_worldScript;

    /// Who is mounted (UnitMountChanged): their parts come off the mount's model and are hung again when they get off.
    class MountWatch final : public wxl::ObjectScript
    {
    public:
        void OnUnitMountChanged(wxl::Object, wxl_guid guid, uint32_t, uint32_t display) override
        {
            if (display) g_mounted.insert(guid); else g_mounted.erase(guid);
        }
    };
    MountWatch g_mountWatch;

    /// What a character of the world is to wear: part [slot] (0 to 2) the head shell and its picture, "" for none.
    void WorldLookSet(uint64_t guid, int slot, const std::string& shell, const std::string& picture, int choice,
                      const std::string& picture12, const std::string& picture13, uint32_t attach)
    {
        WorldLook& look = g_world[guid];
        OverlayPart& part = look.parts[slot];
        part.wantShell = shell;
        part.wantPicture = picture;
        part.wantChoice = choice;
        part.wantPicture12 = picture12;
        part.wantPicture13 = picture13;
        part.wantAttach = attach;
    }

    void __fastcall GeosRenderPrepDetour(void* component, void* /*edx*/)
    {
        SyncOverlays(reinterpret_cast<uintptr_t>(component));
        ProbeBones(reinterpret_cast<uintptr_t>(component));
        ApplyPreview(reinterpret_cast<uintptr_t>(component));
        g_geosRenderPrep(component);
        if (const uintptr_t model = LayerModel(reinterpret_cast<uintptr_t>(component))) ShowLayer(model);
    }

    /// The design now; the creation component is made to prepare its geosets again so that it shows at once.
    void PreviewNow()
    {
        const uintptr_t component = CreationComponent();
        if (!component || !g_geosRenderPrep) return;
        GeosRenderPrepDetour(reinterpret_cast<void*>(component), nullptr);
    }

    void AttachLayer()
    {
        const wxl::RawHookService raw;
        if (!raw)
        {
            wxl::Log(WXL_LOG_WARN, kTag, "no wxl.hook.raw: the body options' layer stays hidden");
            return;
        }
        g_layerHook = raw.AttachAt("CCharacterComponent::GeosRenderPrep", 0x004ED900, reinterpret_cast<void*>(&GeosRenderPrepDetour),
                                   reinterpret_cast<void**>(&g_geosRenderPrep));
        if (g_layerHook) wxl::Log(WXL_LOG_INFO, kTag, "body options' layer: attached");
        else wxl::Log(WXL_LOG_WARN, kTag, "body options' layer: not attached");
    }

    // --- the creatures' skins ----------------------------------------------------------------------------------------
    // ComponentData (ComponentData.h): its CharacterPreferences first (race +0x00, sex +0x04), m_flags +0x24 (1: the baked
    // texture is the skin), m_npcSkinTexture +0x28.
    using ComponentInitFn = bool(__thiscall*)(void*, void*, const char*);
    ComponentInitFn g_componentInit = nullptr;
    wxl::Hook g_creatureHook;
    constexpr uint32_t kComposedRaces = 256;
    bool g_composed[kComposedRaces * 2] = {};      // [race * 2 + sex]: the looks' models
    bool g_composedRead = false;
    uint32_t g_composedCount = 0, g_composedMade = 0;

    /// Wrathpp\\npc.txt: "race<TAB>sex" a line ('#' a comment). Read once; without it nothing is composed.
    void ReadComposed()
    {
        g_composedRead = true;
        const wxl::StorageService storage;
        if (!storage)
        {
            wxl::Log(WXL_LOG_WARN, kTag, "creatures' skins: no wxl.storage: the baked textures stay");
            return;
        }
        const wxl::Expected<std::string> text = storage.ReadText("Wrathpp\\npc.txt");
        if (!text)
        {
            wxl::Log(WXL_LOG_INFO, kTag, "creatures' skins: no Wrathpp\\npc.txt ({}): the baked textures stay", wxl::ResultName(text.Error()));
            return;
        }
        const std::string& all = *text;
        size_t at = 0;
        while (at < all.size())
        {
            size_t end = all.find('\n', at);
            if (end == std::string::npos) end = all.size();
            uint32_t numbers[2] = {0, 0};
            int have = 0;
            bool digit = false, bad = false;
            for (size_t i = at; i < end && !bad; i++)
            {
                const char c = all[i];
                if (c == '#') break;
                if (c >= '0' && c <= '9')
                {
                    if (!digit && have == 2) { bad = true; break; }
                    if (!digit) have++;
                    digit = true;
                    numbers[have - 1] = numbers[have - 1] * 10 + static_cast<uint32_t>(c - '0');
                    if (numbers[have - 1] > 100000) bad = true;
                }
                else if (c == ' ' || c == '\t' || c == '\r') digit = false;
                else bad = true;
            }
            if (!bad && have == 2 && numbers[0] < kComposedRaces && numbers[1] < 2 && !g_composed[numbers[0] * 2 + numbers[1]])
            {
                g_composed[numbers[0] * 2 + numbers[1]] = true;
                g_composedCount++;
            }
            at = end + 1;
        }
        wxl::Log(WXL_LOG_INFO, kTag, "creatures' skins: composed for {} models of the looks (Wrathpp\\npc.txt)", g_composedCount);
    }

    bool Composed(uint32_t race, uint32_t sex)
    {
        if (!g_composedRead) ReadComposed();
        return race < kComposedRaces && sex < 2 && g_composed[race * 2 + sex];
    }

    /// A creature's ComponentData about to be made a component: the baked texture taken off where the model is the looks'.
    bool Unbake(uintptr_t data)
    {
        __try
        {
            uint32_t* flags = reinterpret_cast<uint32_t*>(data + 0x24);
            if (!(*flags & 1)) return false;                                   // a player's, or composed already
            if (!Composed(*reinterpret_cast<const uint32_t*>(data), *reinterpret_cast<const uint32_t*>(data + 4))) return false;
            *flags &= ~1u;
            *reinterpret_cast<char*>(data + 0x28) = 0;
            return true;
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
            return false;
        }
    }

    bool __fastcall ComponentInitDetour(void* component, void* /*edx*/, void* data, const char* debug)
    {
        if (data && Unbake(reinterpret_cast<uintptr_t>(data)) && ++g_composedMade == 1)
            wxl::Log(WXL_LOG_INFO, kTag, "creatures' skins: the first creature composed");
        return g_componentInit(component, data, debug);
    }

    void AttachCreatureSkins()
    {
        const wxl::RawHookService raw;
        if (!raw)
        {
            wxl::Log(WXL_LOG_WARN, kTag, "no wxl.hook.raw: the creatures keep their baked textures");
            return;
        }
        g_creatureHook = raw.AttachAt("CCharacterComponent::Init", 0x004F24D0, reinterpret_cast<void*>(&ComponentInitDetour),
                                      reinterpret_cast<void**>(&g_componentInit));
        if (g_creatureHook) wxl::Log(WXL_LOG_INFO, kTag, "creatures' skins: attached");
        else wxl::Log(WXL_LOG_WARN, kTag, "creatures' skins: not attached");
    }
#else
    void AttachCreatureSkins() {}
    bool Customization(int, int32_t&, int32_t&) { return false; }
    bool SetCustomization(int, int32_t) { return false; }
    bool CreatingWho(int32_t&, int32_t&, int32_t&) { return false; }
    bool SetGear(bool) { return false; }
    void AttachLayer() {}
    std::string g_previewDesign;
    void PreviewNow() {}
    struct OverlayPart { std::string wantShell, wantPicture, wantPicture12, wantPicture13; int wantChoice = 0; uint32_t wantAttach = 0; };
    OverlayPart g_overlays[kPartSlots];
    void SyncOverlays(uintptr_t) {}
    void WorldLookSet(uint64_t, int, const std::string&, const std::string&, int, const std::string&, const std::string&, uint32_t) {}
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

    /// The design file of the woman being made, a path of the game's (Character\\Human\\Female\\WppLayer_3_2.blp), or ""
    /// for none: the creator's preview of her body options.
    void SetBodyPreviewCall(wxl::ScriptCall& call)
    {
        const auto path = call.String(0);
        if (!path)
        {
            call.Fail("WrathPP_SetBodyPreview(path): path is a string, empty for none");
            return;
        }
        const std::string next(path->substr(0, 260));
        if (next == g_previewDesign) { call.PushBool(true); return; }
        g_previewDesign = next;
        PreviewNow();
        call.PushBool(true);
    }

    /// An overlay on the creator's character: slot 1 to 8, a shell's path and the picture's, both "" for none.
    void SetOverlayCall(wxl::ScriptCall& call)
    {
        const auto slot = call.Number(0);
        const auto shell = call.String(1);
        const auto picture = call.String(2);
        if (!slot || *slot < 1 || *slot > kPartSlots || !shell || !picture)
        {
            call.Fail("WrathPP_SetOverlay(slot, shell, picture): slot is 1 to 8, shell and picture are paths, empty for none");
            return;
        }
        OverlayPart& part = g_overlays[static_cast<int>(*slot) - 1];
        part.wantShell = std::string(shell->substr(0, 260));
        part.wantPicture = std::string(picture->substr(0, 260));
        const auto choice = call.Number(3);
        const auto p12 = call.String(4);
        const auto p13 = call.String(5);
        part.wantChoice = choice ? static_cast<int>(*choice) : 0;
        part.wantPicture12 = p12 ? std::string(p12->substr(0, 260)) : std::string();
        part.wantPicture13 = p13 ? std::string(p13->substr(0, 260)) : std::string();
        const auto attach = call.Number(6);
        part.wantAttach = attach && *attach > 0 ? static_cast<uint32_t>(*attach) : 0;
#if defined(_M_IX86)
        const uintptr_t component = CreationComponent();
        if (component) SyncOverlays(component);
#endif
        call.PushBool(true);
    }

    /// The parts of a character of the world: guid ("0x" and sixteen hex digits, as the add-on has it), then up to eight
    /// pairs of a head shell's path and a picture's ("" for none). Replaces what the character was to wear.
    void ApplyLookCall(wxl::ScriptCall& call)
    {
        const auto guidText = call.String(0);
        if (!guidText || guidText->empty())
        {
            call.Fail("WrathPP_ApplyLook(guid, slot1, ... slot8): a slot is shell|choice|picture11|picture12|picture13|attach; guid is \"0x\" and hex digits");
            return;
        }
        const std::string text(*guidText);
        const uint64_t guid = std::strtoull(text.c_str(), nullptr, 16);
        if (!guid)
        {
            call.Fail("WrathPP_ApplyLook: no guid");
            return;
        }
        for (int i = 0; i < kPartSlots; ++i)
        {
            // a slot: "shell|choice|picture11|picture12|picture13|attach" ("" for none; paths have no bar)
            const auto spec = call.String(1 + i);
            std::string fields[6];
            if (spec)
            {
                size_t from = 0;
                const std::string whole(*spec);
                for (int k = 0; k < 6; ++k)
                {
                    const size_t bar = whole.find('|', from);
                    fields[k] = whole.substr(from, bar == std::string::npos ? std::string::npos : bar - from);
                    if (bar == std::string::npos) break;
                    from = bar + 1;
                }
            }
            WorldLookSet(guid, i, fields[0].substr(0, 260), fields[2].substr(0, 260), std::atoi(fields[1].c_str()), fields[3].substr(0, 260), fields[4].substr(0, 260), static_cast<uint32_t>(std::atoi(fields[5].c_str())));
        }
        call.PushBool(true);
    }

    // ---- Soft body: a woman's breasts hang under gravity and bounce, lag and settle (realm/warcraft/wrathpp/tools/sl_parts.py soft_body
    // finds her breast bones in the converted model; the add-on tells this their indices from the package's parts.txt: WrathPP_SetSoftBody).
    // wxl.m2's bone watcher hands each such model's bone matrices every frame, right after the client posed them, to rewrite: each breast
    // bone (and the bones below it) is moved by a damped spring that is hung on the bone it is a child of and driven by that bone's own
    // motion (its acceleration in the world), simulated at 120 Hz at most, with gravity. Matrices: 16 floats a bone, row vectors, the
    // translation at 12 to 14, taking a point of the file to the scene's camera-relative space; view_to_world takes that to the world.
    // Ideas and numbers: the same spring Wifecraft's softbody.cpp has (freq, damping, sag, a limit), as a bone, not a vertex shader.
    // Four sides at most: the chest's two (WrathPP_SetSoftBody), then the seat's two (WrathPP_SetSoftSeat: soft_weights.py gives a
    // woman's model bones of its own for both, weighted at the bottom of the curve; each side hangs on its own bone: chest, pelvis).
    constexpr int kSoftSides = 4;
    struct SoftSide
    {
        bool set = false;
        uint32_t parent = 0;
        uint32_t bone = 0;
        float pivot[3] = {0, 0, 0};
        std::vector<uint32_t> below;
    };
    struct SoftConfig
    {
        SoftSide sides[kSoftSides];
    };
    struct SoftState
    {
        bool started = false;
        uint32_t lastMs = 0;
        double anchor[kSoftSides][3] = {}, velocity[kSoftSides][3] = {}, offset[kSoftSides][3] = {}, speed[kSoftSides][3] = {};
        uint32_t seen = 0;
    };
    std::mutex g_softLock;
    std::map<uint32_t, SoftConfig> g_soft;          // by the model file's bone count (an add-on that names no model: the older way)
    std::map<std::string, SoftConfig> g_softByName; // by the model's name, lower case ("humanfemale"): that model, its variants (V1...) and body shapes (Wpp1...)
    std::map<const void*, SoftState> g_softState;   // by model, one each
    std::atomic<int> g_softLevel{2};                // 0 off, 1 subtle, 2 natural, 3 strong
    wxl::M2BoneWatch g_boneWatch;

    struct SoftTuning { double freq, damping, sag, limit; };
    SoftTuning TuningOf(int level)
    {
        static const double amount[4] = {0.0, 0.5, 1.0, 1.8};
        const double a = amount[level < 0 ? 0 : level > 3 ? 3 : level];
        return {3.2, 0.22, 0.012 * a, 0.035 * a};
    }

    /// The name a model file is sprung by: its file name, lower case, without ".m2" and without a variant's ("V2") or a body shape's
    /// ("Wpp1") ending; "" for a file that isn't a woman's model. The head's and body's shells ("...Face", "...Body") and the pieces
    /// ("...P<Name>") keep their endings, so no name matches them: they are posed by her bones and aren't sprung again.
    std::string SoftName(std::string_view p)
    {
        std::string lower(p);
        for (char& c : lower) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        const bool m2 = lower.size() > 3 && lower.compare(lower.size() - 3, 3, ".m2") == 0;
        const bool mdx = lower.size() > 4 && lower.compare(lower.size() - 4, 4, ".mdx") == 0;     // (the tables' own name for it)
        if (lower.find("\\female\\") == std::string::npos || (!m2 && !mdx)) return {};
        const size_t slash = lower.find_last_of("\\/");
        std::string name = lower.substr(slash == std::string::npos ? 0 : slash + 1);
        name.resize(name.size() - (m2 ? 3 : 4));
        size_t end = name.size();
        while (end > 0 && std::isdigit(static_cast<unsigned char>(name[end - 1]))) --end;
        if (end < name.size())
        {
            if (end >= 3 && name.compare(end - 3, 3, "wpp") == 0) name.resize(end - 3);
            else if (end >= 1 && name[end - 1] == 'v') name.resize(end - 1);
        }
        return name;
    }

    /// The soft body for a model: by its name where the add-on named models, else by its bone count. nullptr for none.
    const SoftConfig* SoftFor(wxl_str path, uint32_t boneCount)
    {
        if (!g_softByName.empty())
        {
            const std::string name = SoftName(wxl::View(path));
            if (name.empty()) return nullptr;
            const auto it = g_softByName.find(name);
            return it == g_softByName.end() ? nullptr : &it->second;
        }
        if (SoftName(wxl::View(path)).empty()) return nullptr;
        const auto it = g_soft.find(boneCount);
        return it == g_soft.end() ? nullptr : &it->second;
    }

    wxl_bool WXL_CALL SoftFilter(void*, wxl_str path, uint32_t boneCount, void*)
    {
        std::lock_guard<std::mutex> hold(g_softLock);
        return SoftFor(path, boneCount) ? WXL_TRUE : WXL_FALSE;
    }

    void Row(const float* m, const double p[3], double out[3])
    {
        for (int j = 0; j < 3; ++j) out[j] = p[0] * m[0 + j] + p[1] * m[4 + j] + p[2] * m[8 + j] + m[12 + j];
    }

    void WXL_CALL SoftWatch(const wxl_m2_bones* bones, void*)
    {
        const int level = g_softLevel.load();
        if (level <= 0 || !bones || !bones->matrices) return;
        std::lock_guard<std::mutex> hold(g_softLock);
        const SoftConfig* config = SoftFor(bones->path, bones->bone_count);
        if (!config) return;
        const SoftConfig& c = *config;
        SoftState& st = g_softState[bones->model];
        st.seen = bones->time_ms;
        if (g_softState.size() > 96)                                    // models that left: forgotten
            for (auto it = g_softState.begin(); it != g_softState.end();)
                it = (bones->time_ms - it->second.seen > 5000 && it->first != bones->model) ? g_softState.erase(it) : std::next(it);
        const SoftTuning t = TuningOf(level);
        const double omega = 6.283185307 * t.freq;
        const float* toWorld = bones->view_to_world;
        double dt = (bones->time_ms - st.lastMs) / 1000.0;
        const bool fresh = !st.started || dt <= 0.0 || dt > 0.25;        // a pause, a hitch or a first frame: held still
        if (!fresh && dt > 0.1) dt = 0.1;
        for (int s = 0; s < kSoftSides; ++s)
        {
            const SoftSide& side = c.sides[s];
            if (!side.set || side.bone >= bones->bone_count || side.parent >= bones->bone_count) continue;
            const float* parent = bones->matrices + side.parent * 16;
            const double pivot[3] = {side.pivot[0], side.pivot[1], side.pivot[2]};
            double cam[3], world[3];
            Row(parent, pivot, cam);                                    // where the bone's rest point is now, carried by its parent
            const double camP[3] = {cam[0], cam[1], cam[2]};
            Row(toWorld, camP, world);
            double accel[3] = {0, 0, 0};
            if (!fresh)
            {
                for (int k = 0; k < 3; ++k)
                {
                    const double v = (world[k] - st.anchor[s][k]) / dt;
                    accel[k] = (v - st.velocity[s][k]) / dt;
                    if (accel[k] > 60.0) accel[k] = 60.0; else if (accel[k] < -60.0) accel[k] = -60.0;
                    st.velocity[s][k] = v;
                }
            }
            else
                for (int k = 0; k < 3; ++k) { st.velocity[s][k] = 0; st.offset[s][k] = 0; st.speed[s][k] = 0; }
            for (int k = 0; k < 3; ++k) st.anchor[s][k] = world[k];
            if (!fresh)
            {
                // the spring, in world space: toward gravity's sag at rest, pushed by minus the anchor's acceleration
                const double rest[3] = {0.0, 0.0, -t.sag};
                double left = dt;
                while (left > 1e-6)
                {
                    const double h = left > 1.0 / 120.0 ? 1.0 / 120.0 : left;
                    left -= h;
                    for (int k = 0; k < 3; ++k)
                    {
                        const double a = -omega * omega * (st.offset[s][k] - rest[k]) - 2.0 * t.damping * omega * st.speed[s][k] - accel[k];
                        st.speed[s][k] += a * h;
                        st.offset[s][k] += st.speed[s][k] * h;
                    }
                }
                double len = std::sqrt(st.offset[s][0] * st.offset[s][0] + st.offset[s][1] * st.offset[s][1] + st.offset[s][2] * st.offset[s][2]);
                if (len > t.limit && len > 0.0)                         // softly limited: past the limit it gives less
                {
                    const double shown = t.limit + (len - t.limit) * 0.2;
                    for (int k = 0; k < 3; ++k) st.offset[s][k] *= shown / len;
                }
            }
            // the offset (world) into the camera-relative space: the rows of view_to_world are its axes
            double cam3[3];
            for (int i = 0; i < 3; ++i) cam3[i] = st.offset[s][0] * toWorld[i * 4 + 0] + st.offset[s][1] * toWorld[i * 4 + 1] + st.offset[s][2] * toWorld[i * 4 + 2];
            auto move = [&](uint32_t bone)
            {
                if (bone >= bones->bone_count) return;
                float* m = bones->matrices + bone * 16;
                m[12] += static_cast<float>(cam3[0]); m[13] += static_cast<float>(cam3[1]); m[14] += static_cast<float>(cam3[2]);
            };
            move(side.bone);
            for (uint32_t below : side.below) move(below);
        }
        st.started = true;
        st.lastMs = bones->time_ms;
    }

    /// The soft body of a woman's model: WrathPP_SetSoftBody(boneCount, parent, boneL, lx, ly, lz, "below,below", boneR, rx, ry, rz, "below,..",
    /// "ModelName"). The name (the package's parts.txt has it since 17 November 2026) makes it that model's only: by the bone count
    /// alone, another race's model of the same count (the Troll's, the Zandalari's and the Dark Troll's women: 200) took the last one's
    /// bones, and the head's shell, of her bones, was sprung too.
    void SetSoft(wxl::ScriptCall& call, int first, const char* usage)
    {
        const auto count = call.Number(0), parent = call.Number(1);
        const auto leftBone = call.Number(2), lx = call.Number(3), ly = call.Number(4), lz = call.Number(5);
        const auto leftBelow = call.String(6);
        const auto rightBone = call.Number(7), rx = call.Number(8), ry = call.Number(9), rz = call.Number(10);
        const auto rightBelow = call.String(11);
        const auto modelName = call.String(12);
        if (!count || !parent || !leftBone || !lx || !ly || !lz || !rightBone || !rx || !ry || !rz)
        {
            call.Fail(usage);
            return;
        }
        auto list = [](const std::optional<std::string_view>& text, std::vector<uint32_t>& out)
        {
            out.clear();
            if (!text) return;
            const std::string s(*text);
            size_t at = 0;
            while (at < s.size() && out.size() < 64)
            {
                char* end = nullptr;
                const unsigned long v = std::strtoul(s.c_str() + at, &end, 10);
                if (end == s.c_str() + at) break;
                out.push_back(static_cast<uint32_t>(v));
                at = static_cast<size_t>(end - s.c_str());
                while (at < s.size() && (s[at] == ',' || s[at] == ' ')) ++at;
            }
        };
        SoftSide left, right;
        left.set = right.set = true;
        left.parent = right.parent = static_cast<uint32_t>(*parent);
        left.bone = static_cast<uint32_t>(*leftBone);
        left.pivot[0] = static_cast<float>(*lx); left.pivot[1] = static_cast<float>(*ly); left.pivot[2] = static_cast<float>(*lz);
        list(leftBelow, left.below);
        right.bone = static_cast<uint32_t>(*rightBone);
        right.pivot[0] = static_cast<float>(*rx); right.pivot[1] = static_cast<float>(*ry); right.pivot[2] = static_cast<float>(*rz);
        list(rightBelow, right.below);
        {
            // (the chest's call starts a model's soft body anew; the seat's adds its two sides to what the model has)
            std::lock_guard<std::mutex> hold(g_softLock);
            auto put = [&](SoftConfig& c)
            {
                if (first == 0) c = SoftConfig();
                c.sides[first] = left;
                c.sides[first + 1] = right;
            };
            put(g_soft[static_cast<uint32_t>(*count)]);
            if (modelName && !modelName->empty())
            {
                std::string name(*modelName);
                for (char& ch : name) ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));
                put(g_softByName[name]);
            }
        }
        if (!g_boneWatch)
        {
            g_boneWatch = wxl::M2BoneWatch(&SoftFilter, &SoftWatch);
            wxl::Log(g_boneWatch ? WXL_LOG_INFO : WXL_LOG_WARN, kTag, "soft body: bone watcher {}", g_boneWatch ? "started" : "not started");
        }
        call.PushBool(true);
    }

    void SetSoftBodyCall(wxl::ScriptCall& call)
    {
        SetSoft(call, 0, "WrathPP_SetSoftBody(boneCount, parent, boneL, x, y, z, \"below,...\", boneR, x, y, z, \"below,...\")");
    }

    /// The seat's two bones of the same model (after its WrathPP_SetSoftBody): the same arguments, the bone they hang on her pelvis.
    void SetSoftSeatCall(wxl::ScriptCall& call)
    {
        SetSoft(call, 2, "WrathPP_SetSoftSeat(boneCount, parent, boneL, x, y, z, \"below,...\", boneR, x, y, z, \"below,...\")");
    }

    /// WrathPP_SetSoftBodyLevel(n): 0 off, 1 subtle, 2 natural (the default), 3 strong.
    void SetSoftBodyLevelCall(wxl::ScriptCall& call)
    {
        const auto level = call.Number(0);
        if (!level || *level < 0 || *level > 3)
        {
            call.Fail("WrathPP_SetSoftBodyLevel(n): n is 0 (off), 1, 2 or 3");
            return;
        }
        g_softLevel = static_cast<int>(*level);
        call.PushBool(true);
    }

    void NativeVersion(wxl::ScriptCall& call) { call.PushString("0.10.0"); }

#if defined(_M_IX86)
    // --- The race ids past 21 ---------------------------------------------------------------------------------------------
    // The client keeps each race's saved choices in CCharacterCreation::m_charPreferences[22][2] (CharacterPreferences*, 0x00B6B0D0, 176
    // bytes; m_raceIndex follows at 0x00B6B180): a race id of 22 or more writes past it into the client's other statics (issue 281). Every
    // function that names it is in CharacterCreation.cpp (0x004DFA50 to 0x004E24E0 at the pinned decompilation). Here, as the mod loads
    // (before any of them runs), a larger zeroed array is made and the 32-bit operand of each instruction in that stretch of code that
    // names the old one (an address from 0x00B6B0D0 to 0x00B6B17F) is pointed at the same place in it. Done only when the stretch holds
    // between 5 and 48 such operands (the decompilation's functions use it in about ten places): a client whose code isn't what the pinned
    // decompilation has is left as it is, and WrathPP_MaxRace says 21.
    constexpr uint32_t kPrefsOld = 0x00B6B0D0, kPrefsEnd = 0x00B6B180;
    constexpr uint32_t kPrefsCodeFrom = 0x004DF800, kPrefsCodeTo = 0x004E3000;
    constexpr uint32_t kPrefsRaces = 64;
    uint32_t g_maxRace = 21;

    /// The addresses in the stretch of code whose next four bytes name the old array (into [sites], at most [room]); how many; -1 on a fault.
    int FindPreferenceOperands(uint32_t* sites, int room)
    {
        int count = 0;
        __try
        {
            for (uint32_t at = kPrefsCodeFrom; at + 4 <= kPrefsCodeTo; ++at)
            {
                const uint32_t value = *reinterpret_cast<const uint32_t*>(at);
                if (value >= kPrefsOld && value < kPrefsEnd)
                {
                    if (count < room) sites[count] = at;
                    ++count;
                }
            }
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
            return -1;
        }
        return count;
    }

    bool PatchOperand(uint32_t at, uint32_t to)
    {
        DWORD old = 0;
        if (!VirtualProtect(reinterpret_cast<void*>(at), 4, PAGE_EXECUTE_READWRITE, &old)) return false;
        *reinterpret_cast<uint32_t*>(at) = to;
        DWORD ignored = 0;
        VirtualProtect(reinterpret_cast<void*>(at), 4, old, &ignored);
        FlushInstructionCache(GetCurrentProcess(), reinterpret_cast<void*>(at), 4);
        return true;
    }

    void MovePreferences()
    {
        uint32_t sites[64];
        const int found = FindPreferenceOperands(sites, 64);
        if (found < 5 || found > 48)
        {
            wxl::Log(WXL_LOG_WARN, kTag, "race ids past 21: {} operands of the saved choices' array in the creation code (5 to 48 expected): left as it is", found);
            return;
        }
        void* room = VirtualAlloc(nullptr, kPrefsRaces * 2 * sizeof(uint32_t), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
        if (!room || reinterpret_cast<uintptr_t>(room) > 0xFFFFF000u - kPrefsRaces * 8)
        {
            wxl::Log(WXL_LOG_WARN, kTag, "race ids past 21: no room for a larger array: left as it is");
            return;
        }
        const uint32_t base = static_cast<uint32_t>(reinterpret_cast<uintptr_t>(room));
        for (int i = 0; i < found; ++i)
        {
            const uint32_t old = *reinterpret_cast<const uint32_t*>(sites[i]);
            if (!PatchOperand(sites[i], base + (old - kPrefsOld)))
            {
                wxl::Log(WXL_LOG_ERROR, kTag, "race ids past 21: operand {} of {} (0x{:08X}) couldn't be written; the first {} are", i + 1, found, sites[i], i);
                return;
            }
        }
        g_maxRace = static_cast<uint32_t>(kPrefsRaces - 1);
        wxl::Log(WXL_LOG_INFO, kTag, "race ids past 21: the saved choices' array moved ({} operands), room for race ids to {}", found, g_maxRace);
    }
#else
    uint32_t g_maxRace = 21;
    void MovePreferences() {}
#endif

    void MaxRaceCall(wxl::ScriptCall& call) { call.PushNumber(static_cast<double>(g_maxRace)); }

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
                                        std::pair{"WrathPP_SetBodyPreview", script.RegisterFunction<&SetBodyPreviewCall>("WrathPP_SetBodyPreview")},
                                        std::pair{"WrathPP_SetOverlay", script.RegisterFunction<&SetOverlayCall>("WrathPP_SetOverlay")},
                                        std::pair{"WrathPP_ApplyLook", script.RegisterFunction<&ApplyLookCall>("WrathPP_ApplyLook")},
                                        std::pair{"WrathPP_SetSoftBody", script.RegisterFunction<&SetSoftBodyCall>("WrathPP_SetSoftBody")},
                                        std::pair{"WrathPP_SetSoftSeat", script.RegisterFunction<&SetSoftSeatCall>("WrathPP_SetSoftSeat")},
                                        std::pair{"WrathPP_SetSoftBodyLevel", script.RegisterFunction<&SetSoftBodyLevelCall>("WrathPP_SetSoftBodyLevel")},
                                        std::pair{"WrathPP_NativeVersion", script.RegisterFunction<&NativeVersion>("WrathPP_NativeVersion")},
                                        std::pair{"WrathPP_MaxRace", script.RegisterFunction<&MaxRaceCall>("WrathPP_MaxRace")}})
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
#if defined(_M_IX86)
            wxl::ScriptMgr::Add(&g_worldScript);
            wxl::ScriptMgr::Add(&g_mountWatch);
#endif
            AttachLayer();
            AttachCreatureSkins();
            MovePreferences();
            wxl::Log(WXL_LOG_INFO, kTag, "Wrath++ native loaded");
            return WXL_OK;
        }
    };
} // namespace

WXL_MOD(NativeMod, "wrathpp.native", "Wrath++ native")
