// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * The class lessons (wrath_remix_world_0025_lessons.sql): a Timerunner wakes at level 10 with a
 * class's worth of abilities they have never used here, so their class's instructor in the
 * training yard walks them through three of them, used as the lesson says (remix_lesson): on one
 * of the yard's dummies, or (a shield, a heal, a seal) on themselves within sight of one. Each one
 * used is the lesson's credit for it (770067 + its slot).
 *
 * The dummies are the game's own, as it scripts them (npc_training_dummy: they take every blow and
 * no damage, and let go of a fight five seconds after the last one).
 */

#include "WrathRemix.h"
#include "Creature.h"
#include "CreatureAI.h"
#include "DatabaseEnv.h"
#include "Field.h"
#include "Log.h"
#include "ObjectMgr.h"
#include "PassiveAI.h"
#include "Player.h"
#include "QueryResult.h"
#include "ScriptMgr.h"
#include "Spell.h"
#include "SpellInfo.h"
#include "Trainer.h"
#include <unordered_map>
#include <vector>

using namespace WrathRemix;

namespace
{
    constexpr float DUMMY_SIGHT = 40.0f;    // how near a dummy a lesson's "on yourself" has to be

    enum LessonTarget : uint8
    {
        ON_A_DUMMY = 0,
        NEAR_A_DUMMY = 1,   // on themselves or a friend, in the training yard
    };

    struct Ability
    {
        uint32 spell;   // the first rank: every rank counts
        uint8 slot;
        uint8 target;
    };

    struct Lesson
    {
        uint32 quest = 0;
        std::vector<Ability> abilities;
    };

    std::unordered_map<uint8, Lesson> lessons;     // by class

    Lesson const* LessonOf(Player* player)
    {
        auto it = lessons.find(player->getClass());
        return it == lessons.end() ? nullptr : &it->second;
    }

    // A spell a Timerunner has cast, as their lesson's: credit for the ability it is, if it was
    // used as the lesson says.
    void Practised(Player* player, Spell* spell)
    {
        Lesson const* lesson = LessonOf(player);
        if (!lesson || player->GetQuestStatus(lesson->quest) != QUEST_STATUS_INCOMPLETE)
            return;
        SpellInfo const* first = spell->GetSpellInfo()->GetFirstRankSpell();
        uint32 id = first ? first->Id : spell->GetSpellInfo()->Id;
        for (Ability const& ability : lesson->abilities)
        {
            if (ability.spell != id)
                continue;
            if (ability.target == ON_A_DUMMY)
            {
                Unit* target = spell->m_targets.GetUnitTarget();
                if (!target || target->GetEntry() != NPC_TRAINING_DUMMY)
                    return;
            }
            else if (!player->FindNearestCreature(NPC_TRAINING_DUMMY, DUMMY_SIGHT))
                return;
            player->KilledMonsterCredit(NPC_LESSON_CREDIT + ability.slot);
            return;
        }
    }
}

namespace WrathRemix
{
    void LoadLessons()
    {
        lessons.clear();
        if (!Active())
            return;
        if (QueryResult result = WorldDatabase.Query("SELECT `class`, `quest`, `slot`, `spell`, `target` FROM `remix_lesson` ORDER BY `class`, `slot`"))
        {
            do
            {
                Field* f = result->Fetch();
                Lesson& lesson = lessons[f[0].Get<uint8>()];
                lesson.quest = f[1].Get<uint32>();
                lesson.abilities.push_back({ f[3].Get<uint32>(), f[2].Get<uint8>(), f[4].Get<uint8>() });
            } while (result->NextRow());
        }
        LOG_INFO("module", "Wrath Remix: {} class lessons", lessons.size());
    }

    uint32 LessonQuest(Player* player)
    {
        Lesson const* lesson = LessonOf(player);
        return lesson ? lesson->quest : 0;
    }

    bool IsLesson(uint32 quest)
    {
        return quest >= QUEST_LESSON_FIRST && quest <= QUEST_LESSON_LAST;
    }

    // The instructor teaches the Timerunner's class (their trainer list is that class's).
    bool TeachesClassOf(uint32 instructor, Player* player)
    {
        Trainer::Trainer* trainer = sObjectMgr->GetTrainer(instructor);
        return trainer && trainer->GetTrainerType() == Trainer::Type::Class && trainer->IsTrainerValidForPlayer(player);
    }

    bool TeachesClassOf(Creature* instructor, Player* player)
    {
        return TeachesClassOf(instructor->GetEntry(), player);
    }
}

// The training yard's dummies: the game's own (npc_training_dummy), under Remix's name.
class npc_remix_dummy : public CreatureScript
{
public:
    npc_remix_dummy() : CreatureScript("npc_remix_dummy") { }

    struct npc_remix_dummyAI : public NullCreatureAI
    {
        npc_remix_dummyAI(Creature* creature) : NullCreatureAI(creature) { }

        void JustEnteredCombat(Unit* who) override
        {
            combatTimer[who->GetGUID()] = 5s;
        }

        void DamageTaken(Unit* attacker, uint32& damage, DamageEffectType damageType, SpellSchoolMask) override
        {
            damage = 0;
            if (!attacker || damageType == DOT)
                return;
            combatTimer[attacker->GetGUID()] = 5s;
            if (Unit* owner = attacker->GetCharmerOrOwner())
                if (me->GetCombatManager().IsInCombatWith(owner))
                    combatTimer[owner->GetGUID()] = 5s;
        }

        void UpdateAI(uint32 diff) override
        {
            for (auto it = combatTimer.begin(); it != combatTimer.end();)
            {
                it->second -= Milliseconds(diff);
                if (it->second <= 0s)
                {
                    auto const& refs = me->GetCombatManager().GetPvECombatRefs();
                    if (auto ref = refs.find(it->first); ref != refs.end())
                        ref->second->EndCombat();
                    it = combatTimer.erase(it);
                }
                else
                    ++it;
            }
        }

        std::unordered_map<ObjectGuid, Milliseconds> combatTimer;
    };

    CreatureAI* GetAI(Creature* creature) const override
    {
        return new npc_remix_dummyAI(creature);
    }
};

// Each spell a Timerunner casts, for their lesson (only while it's under way).
class RemixLessonPlayer : public PlayerScript
{
public:
    RemixLessonPlayer() : PlayerScript("RemixLessonPlayer", { PLAYERHOOK_ON_SPELL_CAST }) { }

    void OnPlayerSpellCast(Player* player, Spell* spell, bool /*skipCheck*/) override
    {
        if (Active() && !lessons.empty())
            Practised(player, spell);
    }
};

void AddRemixLessonScripts()
{
    new npc_remix_dummy();
    new RemixLessonPlayer();
}
