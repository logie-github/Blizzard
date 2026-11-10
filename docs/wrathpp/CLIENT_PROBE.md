# Wrath++ client probe

The client half of the mission: what was established about the source-built WarcraftXL client, what
is implemented for it, and exactly what is missing before an extended category can be seen.

## Status

| | State |
|---|---|
| Client source located, pinned, licensing read | done (SOURCE_AUDIT.md; `realm/warcraft/wrathpp/wrathpp.env`) |
| Matching runtime/SDK identified | done: WarcraftXL-Labs core/sdk `gitea-sync` (ABI 0.1.46) |
| Windows x64 build | **CI probe added** (`.github/workflows/wrathpp-client.yml`); result in TEST_RESULTS.md |
| Boot to glue screens with 3.3.5a data | **untested**: needs the user's own 12340 client data and a Windows (or Wine) machine |
| Alternative HD data on this client | **untested** |
| Protocol + registry + glue API (Lua mod `wrathpp.appearance`) | implemented, tested on a mock of the runtime (`client-mod/tests/run.sh`), its output decoded as the live server decodes it; **not run in the real client** |
| Rendering an extended category | **not implemented**: blocked on the seam below |
| Legion-style creator UI | not started (waits for rendering: no control without an effect) |
| Android (Winlator/Wine/Box64) | **untested** |

## Why a mod alone can't draw it yet

At the pinned commit, `CCharacterComponent::GeosRenderPrep`
(`WoW/Common/ComponentCore/CharacterComponent.cpp`, ~line 3430) runs every time a character's
look or gear changes. It hides geosets 0-2999, shows the five stock fields' geosets, then shows
`group*100 + 1` for every group 20-29, then applies gear. Legion-era categories such as horns or
blindfolds live in those groups (to be confirmed per model: LEGION_OPTIONS_735.md), so:

1. A change made from outside (an `OnAppearanceChanged` handler) is undone at the next
   `GeosRenderPrep`; it has to happen **inside** it, after the group 20-29 default and before or
   after gear by a defined rule.
2. The SDK's `Model:SetGeosets` works on models the mod created (`m2.CreateModel`), not on the
   client's character model pointer that `m2.ObjectModel` / `OnAppearanceChanged` hand over.
3. The component doesn't know whose it is; the mod knows looks by guid.

## The smallest native change (next milestone; to be built in the CI probe before any claim)

In WarcraftXL-Labs/core (a row and its body, per the client README's "Adding a seam"):

```
// include/wxl/seams/component.def
WXL_SEAM_AFTER(Component, GeosRenderPrep, "CCharacterComponent::GeosRenderPrep", void, thiscall,
               (void* self, void* model, uint32_t race, uint32_t sex, uint32_t class_id, uint64_t owner_guid, uint32_t context))
```

raising an event `Object/ComponentGeosets` with those values, and a service call
`m2.set_component_geosets(component, first, last, visible)` valid only during that event.

In the client, one call at the end of `GeosRenderPrep`, with the owner and context supplied by
the three users of the compositor:

| Context | Owner | Where the client knows it |
|---|---|---|
| creation preview | none (the creation screen's selection) | `CCharacterCreation::m_character` |
| character list | the listed character's guid | `CharacterSelectionDisplay` (per index; `OnGlueCharacter` gives the mod index → guid) |
| world (self and others) | the unit's guid | `Unit_C`'s component |

The mod's handler then applies `GeosetsFor(registry, look)`: for each geoset category, hide the
group and show `group*100 + value`. A model that lacks the geoset shows nothing for it, which is the
documented fallback; the mod logs it once per model and option.

This touches the client source, core and the SDK's ABI (a new event and call), so it is a patch
series in `realm/warcraft/wrathpp/patches/{client,core}/` (applied by the CI probe), plus an SDK
patch, all pinned. Not written in this session: it can't be compiled here (no MSVC), and an
unbuilt patch to a decompiled client is not evidence of anything.

## The Lua mod's glue API (implemented)

| Function | Returns |
|---|---|
| `WrathPP_Status()` | state (`waiting`/`ready`/`refused`), reason, registry version, renderer available (false) |
| `WrathPP_GetNumCategories(race, sex, class)` | count of eligible categories |
| `WrathPP_GetCategoryInfo(i, race, sex, class)` | id, name, option count, default, kind |
| `WrathPP_GetOptionInfo(category, i, class)` | option id, name |
| `WrathPP_GetChoice(category)` / `WrathPP_SetChoice(category, option)` / `WrathPP_CycleChoice(category, delta, class)` | the creation screen's selection, one category at a time |
| `WrathPP_ResetChoices()` / `WrathPP_RandomizeChoices(race, sex, class)` | |
| `WrathPP_SendCreateChoices(race, sex, class)` | sends the pending-create choices; call before `CreateCharacter` |
| `WrathPP_GetCharacterChoice(guid, category)` / `WrathPP_SetCharacterChoice(guid, category, option)` | an existing character's |

Events: `WRATHPP_READY`, `WRATHPP_APPEARANCE` (guid), `WRATHPP_RESULT` (code, guid, category).

## Gate E (Android) plan

The x64 client under the app's Winlator/Wine/Box64 is a different runtime from the 32-bit `Wow.exe`
the app runs today (Box64 for x86_64 PE, a 64-bit Wine prefix, D3D9 through DXVK or the client's own
Vulkan device). Order once the Windows build boots: the README's "Testing the Windows games here"
rig (Winlator's Wine x86_64 under Xvfb) with a disposable copy of the data, then the phone. If x64
fails there, fallback 2 (stock x86 client + the injected runtime, where the SDK says the same Lua
mod runs) is evaluated with the same seam requirements.
