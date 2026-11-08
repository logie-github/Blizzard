// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cstdint>
#include <memory>
#include <set>
using uint32 = uint32_t;
constexpr uint32 PLAYER_FLAGS_GHOST = 16;
namespace DataMap { struct Base { virtual ~Base() = default; }; }
struct Player {
    bool ghost = false;
    std::set<uint32> auras;
    int casts = 0;
    struct {
        std::unique_ptr<DataMap::Base> state;
        template<class T> T* GetDefault(char const*) {
            if (!state) state = std::make_unique<T>();
            return static_cast<T*>(state.get());
        }
    } CustomData;
    bool HasPlayerFlag(uint32) const { return ghost; }
    bool HasAura(uint32 id) const { return auras.count(id); }
    void CastSpell(Player* target, uint32 id, bool triggered) { ++casts; target->auras.insert(id); }
    void RemoveAurasDueToSpell(uint32 id) { auras.erase(id); }
};
