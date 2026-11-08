# Wrath Remix: the story

The story Wrath Remix tells, quest by quest: who gives each quest, what you do, and where it sends
you next. Every step leads to the next one; nothing is left to find on your own. The build follows
this script (the SQL in `data/sql/remix/world/`, the scenes in `src/RemixNpcs.cpp`); where the two
disagree, this file is what was meant.

WRM-nnn is quest 77nnn. Original quests are named with their ids.

## The premise

You are a veteran of the war against the Lich King, some time after his fall. The Frozen Throne
is empty, the Scourge is scattered, and you are drinking with three friends in your faction's
tavern (the Gilded Rose in Stormwind, the Broken Tusk in Orgrimmar): remembering the Wrathgate and
Ulduar, and the one of you who didn't come home from Icecrown (Haldren, for the Alliance; Kaga,
for the Horde). Moratari of the Infinite Dragonflight stops the room mid-toast and takes you back:
through the war's last battle and what the Lich King's reign cost, and on to Northrend in the year
his war begins. You will go back to that table, to the very moment you left it. The journey costs
travelers their strength: you arrive as a level 10 with nothing but what Eternus gives you, and you
grow strong again as the war goes on. That is what a Timerunner is.

What you know, and what you don't. You know how Northrend's war goes, because you fought it. You
know nothing past the Lich King's fall. Sylvanas and Alleria do. They come from much further on,
the days of Midnight, when the Void has come for Quel'Thalas; to you, Sylvanas is still the Banshee
Queen of the Undercity, and Alleria a legend who went through the Dark Portal and never came home.
They know your future; you know their past. That gap is the story's dramatic irony, and the rules
of time (and, at the end, Moratari) keep it that way: you keep Northrend, and lose what they told
you of your own years ahead.

And no one of this year may ever learn what you are. Whatever you change, you change the way anyone
could: a hunch, a scout's report, a clue found at the right moment, a careful look at the right
map. The people of the year make their own decisions with what you put in front of them; some of
them doubt you, and you let them find it for themselves.

Eternus wants the war to go differently. The war against the Lich King cost the world dearly:
Saurfang's son and Bolvar Fordragon at the Wrathgate, the Forsaken's betrayal there, the dead of
every battle raised to fight for the Scourge. Eternus believes a kinder history is possible, and
that heroes who know how the story goes can steer it there. The bronze dragonflight would call
this a crime. Eternus answers that the bronze also let Stratholme burn.

She is not lying to you about what she wants. She is wrong about what it costs.

In Wrath itself the Infinite Dragonflight is already the enemy of history: they try to stop the
Culling of Stratholme, and Chromie hunts their agents at Wyrmrest Temple. Eternus is one of them
who believes she is better than the rest.

## The people

- **Eternus** (Infinite Dragonflight): the Bazaar's mistress. Grand, patient, sincerely grieving for
  the people the war will kill. She never admits she is wrong; after the turn she keeps trying to
  save the war's dead, and her agents fight you for it.
- **Moratari** (Infinite Dragonflight): Eternus's lieutenant and your guide. A scholar of what
  she calls variables, dry and curious. She believes in Eternus until Sylvanas gives her a reason
  to look, and then she looks.
- **Sylvanas Windrunner**, from the days of Midnight, years into her sentence. The bronze dragonflight
  brings her back, because no one alive understands the Lich King's place in the world better:
  she served the Jailer who made his Helm, and she is spending eternity freeing the souls it took.
  If the war goes differently, those souls are lost, and the Helm passes to no one fit to hold
  it. She also stands to gain more than anyone from a different war: Arthas killed her and made
  her a banshee. That she will not let it change is what makes her believable. She keeps out of
  her own sight: the Sylvanas of this time is alive in the Undercity, and must never see her.
- **Alleria Windrunner**, from the days of Midnight, taken from Quel'Thalas with the Void at its
  gates: her sister, a ranger touched by the Void, who can feel when the world's shape is wrong.
  Wry where Sylvanas is cold; she came because Sylvanas asked, which Sylvanas does not do. To a
  Timerunner from before her return she is a name from the end of the Second War's histories, and
  she shows them her face once, at Wyrmrest, before she hides it again. Where she comes from, the
  Timerunner is family to her, a brother or sister in all but blood (Argus, and every road the Void
  has walked since), and she keeps them at arm's length here for it: prickly, proud, insisting she
  is only here for the timeline, and giving herself away in small ways. She finally says it as they
  say goodbye. (The 3.3.5 game has no Alleria; she wears the look of the living
  Ranger-General, which is what she looked like before the Void.)
- **Chromie** (bronze dragonflight), at Wyrmrest Temple, as the game has her: she is already
  fighting the Infinite there (Mystery of the Infinite). She brought Sylvanas and Alleria.
- **Andormu and Nozari** (Keepers of Time): arrive at the Bazaar after the turn, with the bronze.
- At the Bazaar throughout: Alurmi (Bronze trader, sells to anyone), the Bronze vendors (Legion
  Remix's Bazaar cast, Horos to Erus), Pageturner Metros, Nedward the barber, Zephyr's roads, Sa'at's
  dungeons, the Chronologist, Momentus (the weaponmaster), the class instructors.

## The Infinite Bazaar

The home of the whole story, in Malykriss: The Vile Hold, the necropolis the Lich King began in Icecrown
to replace Acherus and never finished (in Crystalsong Forest until build 117). When the Bazaar's dragons
started cleaning up the timeline, the Scourge infestation here was one of the first things they took
care of: the Ebon Blade's fight for it (Vereth's riders, Orbaz Bloodbane) never happens, and Malykriss
is entirely theirs, the infinite dragonflight's, the Knights of the Ebon Blade's who keep its gates,
and the last free nerubians of Azjol-Nerub's, who were building in saronite before the Scourge stole
the craft from them (`tools/malykriss.py`). Moratari says so as the Timerunner wakes: they may
remember it otherwise. Every new Timerunner wakes here (no more Caverns of Time). Your hearthstone remembers it. Until the turn
it is Eternus's camp; after it, Eternus is gone from it and Sylvanas and Alleria are there, with
Moratari and the Keepers of Time.

It is a camp, not a ring of people (`tools/bazaar.py`): the heart, under a great hourglass, where
you wake, with Eternus, Moratari and the echoes; the market lane down the west side, a stall for
each Bronze trader with Alurmi's at its head; the north row, the heroic raids' pavilions and the
apparel stalls, with Nedward's barber's chair at its end; the training yard to the south-east, the
instructors at work among dummies and targets, Grandmaster Jakkus and Momentus the weaponmaster at
its edge; the waystation to the north-east, Zephyr by a door in time and her drake resting, Sa'at at
his map table, Hemet Nesingwary with his mounts; the chronicle corner to the north, the
Chronologist's shelves, Lidamorrutu's gems and Lindormi's emblems; and the campfire to the south,
where other Timerunners from your own hour sit, eat the cook's stew and talk about home, and Nostwin
sells snacks beside Erus's scrap. Pageturner Metros keeps a desk at the heart and knows where
everyone is. Porters and wardens make their rounds, whelps get underfoot, and while you are near,
people talk: to the air, or to each other. While they are here, the Bronze dragons and the Infinite
wear mortal shapes (elves, orcs, humans, gnomes, a pandaren), or come as Legion Remix has its
traders: the infinite dragonflight's dragonspawn and drakonid, and a whelp.

## The opening

The opening (`src/RemixIntro.cpp`), about five minutes, played once:

1. **The tavern.** The Timerunner drinks with three friends of their side (Brannoc Ironvale,
   Sylenna Moonfall and Tobias Harlan; Grakka Bloodfist, Tahono Swiftwind and Veylan Dawnspire), the
   innkeeper (Allison, or Gryshka) pouring a round on the house for the heroes of Icecrown. Each
   side remembers its own war: for the Alliance, a toast to King Varian and the empty throne, the
   beach at Valiance Keep, the lower village at Wintergarde, Bolvar in the dragonfire, Varian
   kicking in the doors of the Undercity, the Skybreaker over Icecrown; for the Horde, a toast to
   the Warchief, the nerubians coming up through Warsong Hold's floor, Garrosh wanting to march on
   Icecrown the first afternoon, Saurfang's son at the Gate, Thrall and Vol'jin taking the Undercity
   back, Orgrim's Hammer over Icecrown. A toast to Haldren (or Kaga); "whatever comes next can't be
   worse"; and the question they never get to answer, "What was it like, when he fell?" The room
   stops mid-question. Moratari walks out of a rift: "I'm sorry, hero. I need you."
2. **The Broken Front**, in Icecrown, the Citadel ahead: the war's last battle as the Timerunner
   remembers it, the Light's wings on them, Tirion and the Argent Crusade spread along the line with
   the Skybreaker's marines or the Kor'kron, the Scourge coming across the snow from far off. "Do
   you remember this?" Ghouls claw out of the ice at the Lich King's word, abominations and
   deathbringers come down the slope, frost bombs and plague burst across the field, a frost wyrm
   strafes the line, the val'kyr come at his call. Then the Lich King himself, and the Scourge
   kneel; Tirion charges him; the winter takes the paladin to his knee; Arthas turns to the
   Timerunner ("You... You are not of this hour.") and raises Frostmourne. Time stops. "You won.
   But you remember what it cost."
3. **What his reign cost**, three moments Moratari holds still: the Wrathgate after the plague
   (Saurfang's son and Bolvar as they fell, the dead of both sides, the green fog); Wintergarde
   under Naxxramas (its villagers cowering, their risen neighbours coming for them, the dead of
   the morning rising); Icecrown's fields (the fallen in rows, the val'kyr over them, the bodies
   rising one after another into the ranks of the Scourge, Haldren or Kaga among them). "Unless
   none of it ever happens. We can stop all of this. We can undo it."
4. **The Bazaar**, years earlier: "Welcome to the Infinite Bazaar. Eternus will want to see you."

## Prologue: the Infinite Bazaar (level 10)

One thing at a time, each quest given where the last one ended:

1. **WRM-010 Out of Time** (Moratari → Eternus). Where and when you are: the Bazaar, outside time,
   in the year the war began; none of what she showed you has happened yet; your friends are still
   at that table. Eternus sent her; she will tell you why.
2. **WRM-011 The Plan** (Eternus → Eternus). Ask her three things. What she wants: fewer graves; a
   war is made of a thousand small moments, and changing enough of them changes the large ones. How
   it is done: quietly; you fight the war again from its first day, and wherever you know more than
   you should, you use it, but no one of this year may ever learn what you are. Why you: because you
   were there, and because you lost someone in it.
3. **WRM-012 Time's Toll** (Eternus → Alurmi). Time takes its toll: you are weaker than the hero in
   the tavern, and it comes back fast. Bronze is what time leaves behind when you act in it; Alurmi,
   at the head of the market lane, trades it for heirlooms, and gives you some to start.
4. **WRM-020 Old Habits** (Alurmi → your class's Timeworn Instructor, in the training yard). Only your
   own class's instructor takes it back.
5. **WRM-030 to 039, the class lesson** (your instructor → your instructor). The instructor walks you
   through three of the abilities you woke with, each explained, then used as it says on one of the
   yard's training dummies or on yourself in the yard: the warrior's Charge, Rend and Heroic Strike;
   the paladin's Seal of Righteousness, Judgement of Light and Holy Light; the hunter's Hunter's Mark,
   Serpent Sting and Arcane Shot; the rogue's Stealth, Sinister Strike and Eviscerate; the priest's
   Shadow Word: Pain, Smite and Power Word: Shield; the death knight's Icy Touch, Plague Strike and
   Death Coil; the shaman's Lightning Bolt, Earth Shock and Healing Wave; the mage's Frostbolt,
   Fireball and Fire Blast; the warlock's Corruption, Immolate and Shadow Bolt; the druid's Moonfire,
   Wrath and Rejuvenation.
6. **WRM-021 The Bazaar's Keepers** (Moratari → Moratari). Zephyr (travel), Sa'at (dungeons and
   raids), the Chronologist (chapters): speak with all three. Moratari's hourglass: turned anywhere,
   it brings you to the Bazaar; turned there, it takes you back to wherever you were (not in a
   fight). Your hearthstone now remembers the Bazaar.
7. **WRM-013 A Small Demonstration** (Moratari → Moratari). Time pushes back against being
   changed, and the seams fray: anomalies come through. Moratari lets three through, one at a time;
   you deal with them.
8. **WRM-014 / WRM-015 To the Front** (Moratari → Eternus; the Alliance's, the Horde's). Eternus sends
   you to the war's first day: keep what you know to yourself, and when something can be done
   better, find a reason anyone would believe. Both sides land in the Borean Tundra: the Alliance at
   Valiance Keep, the Horde at Warsong Hold. Moratari meets you at the landing.

Death knights keep Acherus and their own story; when the Ebon Blade lets them go, Moratari finds
them, tells them what they missed, and brings them to the Bazaar at their chapter.

## Chapter I: The Northrend Invasion (Borean Tundra, 10 to 20)

One route for everyone: the Borean Tundra. Howling Fjord stays in the world for whoever wants it.

The game's own chains, with a step added wherever the game leaves you to find the next quest giver
yourself: a short quest from the last quest's giver to the next one ("Report to..."). Moratari's
transitions skip the afternoons of errands, as before, but now they are Eternus's: she is
shortening the war, and you are helping.

- **Alliance:** Enlistment Day, A Time for Heroes, The Siege, Death From Above, Plug the Sinkholes;
  Leryssa's search for Thassarian (WRM-006 *A Useful Omission*, Eternus's: she skips the road to
  Thassarian), Thassarian, the Death Knight, Finding the Phylactery, Buying Some Time, Words of
  Power, Last Rites.
- **Horde:** Hellscream's Vigil, The Defense of Warsong Hold, Taking Back Mightstone Quarry, Cutting
  Off the Source, Wind Master To'bor, Magic Carpet Ride, Tank Ain't Gonna Fix Itself, Mobu's
  Pneumatic Tank Transjigamarig and Super Strong Metal Plates! (until build 91 WRM-016 skipped
  them), Tanks a lot..., The Plains of Nasam.
- Moratari walks with the Timerunner through the whole of the Borean Tundra, and her interventions
  sit in both chains: see "Moratari in the war".
- **WRM-017 / WRM-018 A Kindness Out of Time** (mid-chapter, by Sergeant Hammerhill after Plug the
  Sinkholes, or by Overlord Razgor after Cutting Off the Source): Eternus's first "improvement".
  Moratari brings Eternus's request: a squad history lost (the 7th Legion's on Valiance Keep's beach, a
  Warsong patrol in Mightstone Quarry's tunnels); clear the crypt crawlers or the Nerub'ar before
  they go in, and they come home. You do. It feels like heroism. (Sylvanas will later ask what
  became of the ones who would have taken their places.) The chain's next quest opens after it.
- **WRM-019 Word at the Gate** (Alliance, Moratari → Mark Hanes): Word on the Street is his, a little
  way off, and the game leaves it to be found.
- **WRM-121 Into the Dragonblight** (by the chapter's last quest giver): Eternus wants you at the
  Dragonblight's front. To Wintergarde Keep or Agmar's Hammer.

## Chapter II: The Wrathgate (Dragonblight, 20 to 32)

The chapter the story turns on. Built (build 65), in `wrath_remix_world_0011_chapter2.sql` and the
scene in `RemixNpcs.cpp`. Alliance and Horde quests have their own ids where the places differ
(the Horde's is the Alliance's + 10).

1. Arrival (WRM-121 to 124), and each side's chain begins: Wintergarde Keep for the Alliance
   (Naxxramas and the Fall of Wintergarde... Find Durkon!), Agmar's Hammer for the Horde (Victory
   Nears... The Forsaken Blight).
2. **WRM-203 / 213 A Summons from Wyrmrest** (Moratari, by Cavalier Durkon or Doctor Sintar
   Malefious, where The Road to Angrathar used to be offered): Chromie has sent for you by name,
   which should not be possible. Moratari takes you to her, atop Wyrmrest Temple.
3. **Mystery of the Infinite** (12470, Chromie, the game's own): Infinite agents attack Chromie's
   hourglass; you defend it, and your own future self comes to help.
4. **WRM-204 Strangers Out of Time** (Chromie → Sylvanas, beside her): one of the Infinite has
   been bringing heroes from the future into this war, and Chromie went and fetched two people who
   are unhappy about it. Sylvanas and Alleria appear beside her as you take it, hooded. Sylvanas
   (who hears you were taken from a tavern after the war, toasting it, and says only "Of course
   you were"): stop helping her; the war must happen as it did. Alleria, spoken to, lowers her hood for
   you alone: the ranger every history of the Second War ends with, who in your year has still
   never come home.
5. **WRM-205 / 215 Ask Her Yourself** (Sylvanas → Eternus; Chromie sends you to the Bazaar as you
   take it): ask your mistress what she means to do at the Wrathgate, and who will wear the Helm.
   Eternus answers that the woman lecturing you will one day set a world tree burning with its
   people inside it; she wants the war kinder, that is all. Moratari takes you back to the front.
6. **WRM-201 / 211 The Road to Angrathar** (II-A, Moratari, by Durkon or Sintar): the camp's
   errands skipped, as before, at Eternus's asking.
7. The chain to the Wrathgate's door: To Fordragon Hold! (Bolvar) or The Kor'kron Vanguard!
   (Saurfang's son).
8. **WRM-206 / 216 A Warning, Unwritten** (Moratari, by Bolvar or Saurfang's son → Eternus at the
   Bazaar; taking it goes there): Eternus's whole plan. The Forsaken's apothecaries will turn on
   everyone at the gate; her loyalists are on the cliffs above it, where Putress's men will stand,
   to strike first, so that Bolvar and Saurfang's son walk home. You are to lead them.
9. **WRM-207 The Weight of Time** (Eternus → Moratari), the turn, a scene at the Bazaar as you take
   it: Eternus says something has followed you from Wyrmrest; Sylvanas and Alleria walk in.
   Eternus throws Teldrassil at Sylvanas; she answers that it is why the bronze sent her, and
   tells Moratari what Eternus left out: if Bolvar does not burn, no one takes up the Helm when
   Arthas falls, the Scourge goes masterless, and every soul the Helm has bound is lost; she has
   spent years freeing souls like those. Alleria feels where Eternus's road ends. Moratari says Eternus
   told her it was mercy, casts a spell and vanishes; ten seconds later a time rift opens and she
   steps out of it: the road where Bolvar lives ends at a throne no one holds. It has to happen as
   it did. Eternus: "I know. I have always known. I will not watch it again." She leaves. From then
   on the Bazaar is Moratari's, Sylvanas's and Alleria's: Eternus is gone from it (for those past
   the turn; a new Timerunner still meets her in the prologue).
10. **WRM-208 / 218 The Hour of the Gate** (Sylvanas → Alleria, on the cliffs above the Wrathgate;
    taking it goes there): Eternus's loyalists (Infinite Interlopers) wait where the Forsaken's
    catapults will stand. Slay six; leave the Forsaken be. Sylvanas will not come: she cannot be
    seen anywhere near the gate. Alleria sends you to Bolvar or Saurfang's son, whose Audience With
    The Dragon Queen waits for this.
11. The Wrathgate's chain as the game has it: Audience With The Dragon Queen, Galakrond and the
    Scourge, On Ruby Wings, **Return To Angrathar** (12499 / 12500) and the Wrathgate.
12. **WRM-202 / 212 What We Cannot Change** (II-B, Moratari by Alexstrasza): no skip. It happened as
    it did; we made sure of it. Sylvanas's message: Putress was hers once, she did not order this,
    and she remembers taking her city back from the ones who did.
13. The post-Wrathgate chains and the Battle for the Undercity, as the game has them.
14. **WRM-221 / 222 After Angrathar** (II-C, Moratari by Varian or Thrall): Sylvanas watched the
    battle from where her past self could not see her; it went exactly as she remembers. To the
    Grizzly Hills and Chapter III. Eternus will be there before us.

Who is seen where follows the story: Sylvanas and Alleria atop Wyrmrest from WRM-204 until WRM-205
is turned in; at the Bazaar once WRM-207 is done, when Eternus is gone from it; Alleria and the
loyalists on the cliffs during WRM-208.

Anywhere but the Bazaar, the two from the future go hooded and pass for adventurers, one more pair of
rangers in a war full of them: the **Hooded Ranger** (Sylvanas, in black) and the **Cloaked Ranger**
(Alleria, in blue), with *Adventurer* under their names. Chromie says so as she sends the Timerunner
to them, and Sylvanas, lowering her voice, says who she is and that to everyone else she is a ranger
passing through. Every place they meet the Timerunner in the world (Wyrmrest, the Wrathgate's
cliffs, the Grizzly Hills, the Ebon Watch and Voltarus, the scenes, the last hour at Icecrown
Citadel's doors) has them in their disguises; only the Bazaar has them as themselves. Moratari, who
meets the Timerunner beside quest givers all over Northrend, wears no title over her head.

## Two Sylvanases

The Sylvanas of this year is the game's own, and nothing in Wrath Remix changes her: to her the
Timerunner is one more soldier, through the Battle for the Undercity and into the Frozen Halls. She
does not know the one from the future is here. Once, in the Forge of Souls (the Horde's way in),
something reaches her: at the end of her briefing she says the Timerunner's name, says that they are
being watched, or rather observed, that she senses a presence she has not felt since..., and goes off
to the other side of the hall. Spoken to there, she is murmuring about her sisters (three variants:
Alleria gone beyond the Portal; the three of them and Lirath at Windrunner Spire; the presence that
wears her sister's shadow). It is optional; the dungeon goes on as the game has it
(`RemixFrozenHalls.cpp`, `wrath_remix_world_0020_frozen_halls.sql`).

The Sylvanas from the future is careful never to come near the one of this year, even when she is
the one deciding what the Timerunner does next: she will not go near the Wrathgate, watches the
Battle for the Undercity from where her past self cannot see her, and will not set foot in the
Frozen Halls ("If she sees me..."). The one of this year never learns she is there.

The Sylvanas from the future knows the Timerunner far better than the Timerunner knows her: where she
comes from, they are close. She slips, now and then (a name said too familiarly, "you always stand
on my left", "you never did listen to me about trolls"), and catches herself; she is open that she
will not say more, because knowing it would change how it happens. Asked outright ("You talk to me
like you know me"), she says so. Alleria notices how careful her sister is with the Timerunner.

Alleria knows them too, and is worse at hiding it, and hides it harder. She looks after the
Timerunner the way an eldest sister does, crossly: they have not been sleeping, they should eat,
that scratch wants cleaning, they went in ahead of her again ("do that again and I will shoot you
myself"). Every kindness comes with its excuse: it is for the timeline, for her sister's sake, as a
matter of policy, "it is not as if I would miss you". She slips into the future tense ("you always
do that", "you will hear it again at the bottom of Ulduar"), and takes it back. Her words at the
Bazaar warm as the war goes on (`npc_remix_windrunner`: after the turn, from Chapter V, from
Chapter VII, and once the war is over), until, before the Citadel, she tells them there is
something she would say if things were otherwise: "Ask me after." After the war, asked why she
keeps looking out for them, she denies it, then admits it ("Sylvanas is careful with you. I am
not careful. I am cross with you, constantly, which in our family is very much worse"), and tells
them to ask again when they say goodbye. Her goodbye says it: where she comes from, the
Timerunner is family; Turalyon says she treats them the way she treated Lirath, her little brother,
before the war took him, and he is right; she kept her distance so they could find their own way
to it; she will see them in the future. It is platonic, a sibling's love; Sylvanas's "someone I
trust" is a soldier's.

## Before the turn: Eternus's small changes

Until the turn, Eternus is folding the war her way, quietly, and the Timerunner can see it. Nine
original quests on each side's path through the Borean Tundra and the Dragonblight turn in a little
differently than history has them: the one who takes the quest back notices something small that
went better than it should have (a transport that came in, a wall braced in the night, a fog over
the plains, a vial gone missing), and a moment later Eternus whispers that it was her. The people
in hers are history's unnamed. (Moratari's go further: a named man lives, see "Moratari in the war".)
Their texts and her whispers are in `wrath_remix_world_0019_eternus_kindnesses.sql`; the whispers
stop at the turn.

- Alliance: Enlistment Day, A Time for Heroes, The Siege, Death From Above, Plug the Sinkholes,
  Finding the Phylactery, Flight of the Wintergarde Defender, Rescue from Town Square, Find Durkon!
- Horde: Hellscream's Vigil (both), The Defense of Warsong Hold, Cutting Off the Source, Magic
  Carpet Ride, The Plains of Nasam, Victory Nears..., Spread the Good Word, The Forsaken Blight.

## Moratari in the war

The user's brief after the first chapters: Moratari more involved in the war's own quests, at the
Timerunner's side while they find their feet, steering it with them until the Timerunner meets the
future Sylvanas; after that, the quests that undo it. Built in build 91 (`RemixMoratari.cpp`,
`tools/story.py` and its `story_*.py`, `0027_moratari.sql`).

**The rules it keeps.** The time travel stays secret: no one of this year is told or finds out. The
Timerunner warns with a scout's report, a veteran's eye, a hunch, a soldier's superstition, and the
people of the year doubt them as they would (Arlos glances at his counselor; Garrosh scoffs; Leoric
asks on whose authority). Established events stay: Valanar is still unmasked and killed at
Naxxanar, Leryssa is still taken there, the Wrathgate burns, Dranosh dies. What is directly changed
is said plainly; what follows from it is only rumored. Not everything works.

**At the Timerunner's side.** Through the Borean Tundra (both sides) Moratari walks with them: their
level, fighting what fights them and healing them, stepping aside to her own spawn when they come
near one, waiting when asked. Everywhere, she has words for the game's own quests: lore, the war's
timeline, what happens to these people later, a joke now and then; said beside them when she walks
with them, whispered when she doesn't.

**Alliance, the Borean Tundra.**
- **WRM-041 A Word in the General's Ear** (after Enlistment Day): warn General Arlos (who glances at
  Counselor Talbot and waves it away) and Sergeant Hammerhill (who moves two catapults: the ones
  Eternus's note on A Time for Heroes speaks of). Talbot, asked for the ridge reports, smiles.
- **WRM-042 The Fourth Sinkhole** (after Plug the Sinkholes): the cult's necrolytes feeding the worms
  at the northern sinkhole, and a fourth tunnel under the dunes that history never records:
  Moratari ages its supports a hundred years in a heartbeat.
- **WRM-043 Not Yet Late** (after Word on the Street): William Allerton, in the game a corpse in the
  Farshire Mine with his throat cut "and no claw marks", is reached before the cult's assassin in a
  Valiance tabard. He lives, and takes back Leryssa's quest himself.
- **WRM-044 Named for No Town**: his testimony, Old Man Colburn ("people don't make up units to send
  them somewhere nice") and Private Brau ("'S' stood for suicide... I saw the hand. It was the
  counselor's."). The Timerunner does not confront Talbot: if he falls in the keep, he does not fall
  where history needs him to.
- **WRM-045 No One Left Behind** (after A Useful Omission, at Death's Stand): four of Unit S, taken
  alive to the necromancers' yard at En'kilah, freed; Hammerhill's volunteers (the warning, again)
  hold Death's Stand and the Wailing Ziggurat behind Thassarian.
- **WRM-046 Before She Gets Hurt** (after Thassarian, the Death Knight): Leryssa warned (she will not
  leave without her brother) and Vindicator Yaala asked to watch her. It fails: the general's own
  escort comes for her under his seal, and Last Rites plays as the game has it. Moratari: if Leryssa
  had not been on that tower, Valanar would never have knelt before his master and boasted.
- **WRM-047 The Keep Holds** (after Last Rites): the chapter's new end, at Valiance Keep: Arlos himself
  again (his apology, Unit S on his conscience), Vurenn's two regiments accepted at last, and the
  road to Wintergarde (WRM-121 waits for it). Talbot is gone from the barracks after Last Rites.

**Horde, the Borean Tundra.**
- **WRM-050 Beneath the Floor** (after Hellscream's Vigil): warn Garrosh (who scoffs, and calls
  Kel'Thuzad a ghost story), Saurfang (who listens, sends Holgoth hands and scouts onto the plains,
  and tells the Timerunner to say nothing to Hellscream) and the Warsong Captain ("Settle down,
  soldier! ... You did a good job in warning us": his own lines, unused in the game). On Remix's realm
  he no longer fights creatures: the game's own assault on the hold (Ith'rix the Harvester's flight,
  What the Cold Wind Brings..., half of every hour) killed him at the chapter's levels every few
  minutes, an elite's seven minutes dead each time, while the Timerunner was on the way to warn him.
- **WRM-051 Hands for Holgoth**: the game's Patience is a Virtue and Bury Those Cockroaches! on the
  road: the four sinkholes under the quarry collapsed before the floor of the keep gives way.
- **Mobu's parts** are back on the road, Moratari knowing exactly where they are ("Already? Buddy, I
  been starin' at that hut since the mist rolled in, tryin' to work up the nerve!"), and two more tanks
  patched from the spare plates; Shipping Lanes waits for the coast to be held.
- **WRM-054 The Condemned Coast** (after Tanks a lot...): the Kvaldir thinned on the landing, and a
  garrison Gorge asks Saurfang for ("if anybody asks, it was my idea").
- **The Plains of Nasam**: every tank that will run rolls out together (its accept scene), and the
  wounded recover on the coast. At the turn-in Garrosh says, as the game has him, "So it's true".
- **WRM-056 Shipping Lanes**: the chapter's new end: the argument Garrosh and Saurfang have at the war
  map every few minutes, settled the other way, once: "Then it is not condemned. There. Now we have
  a shipping lane." WRM-122 waits for it.

**The Dragonblight.**
- Alliance: **WRM-223 The Second Sky** (Lynore, Leoric and Urik warned of Naxxramas's next blows);
  **The Noble's Crypt** (Necrolord Amarion) put on the road before Chromie's summons, and a 7th
  Legion company sent to Bolvar at Fordragon Hold, which the High Commander recalls after the
  Timerunner has met Sylvanas (WRM-201: "I did not stop the rider").
- Horde: **WRM-236 Eyes and Ears** (a soldier's word for Saurfang's son, through Messenger Torvus;
  Agmar burns it, she learns after the turn); **WRM-234 Before the Second Wave** (the cultists
  breathing on Icemist's blightbeasts, and the road to Venomspite); **WRM-235 A Careful Inventory**
  (what the Royal Apothecary Society's people let slip: blight consigned to "the Grand Apothecary's
  special detachment"; the Timerunner must show no one).
- The bronze: Moratari waits outside the time storm at the Bronze Dragonshrine; after Mystery of the
  Infinite, one of the Infinite on the edge of Wyrmrest's platform was watching the Timerunner, not
  the hourglass.

**Undoing it, after the turn.** Moratari, who now knows what Eternus left out, asks the Timerunner to
help her put back what the record cannot keep, without taking a single life:
- **WRM-048 Lost at Sea** (Alliance): William Allerton sails home under another name; the ledger
  keeps him dead at Farshire.
- **WRM-049 Forged Orders** (Alliance): Unit S's freed men and the volunteers go home to Stormwind's
  harbor; the record keeps Unit S lost at the landing ("'S' for 'sent home'").
- **WRM-230 The Record Keeps Warsong** (Horde, after Darkness Stirs): the coast's garrison, the spare
  tanks and the wounded go back to Orgrimmar under the Warchief's martial law. At Darkness Stirs
  Garrosh's lesson breaks: "No more waiting."
- After Angrathar, the end of Chapter II, waits for these.

## Moratari, if you like

The user's brief: an optional romance with Moratari, flirting first and then something real, gated by
the main story; kisses, dates, adventures, her dragon shape, a fade to black; her private tent at the
Bazaar, where both appear without their gear and from which she goes back to her post and the gear comes
back on; a full companion as it grows; it ends when the Timerunner goes home, with a letter in the mail.
The same words for every Timerunner, whatever their sex, now and then a word about their race; PG-13
and in Warcraft's voice. Built in `tools/romance.py` (`0027_moratari.sql`, scenes 901 to 909),
`RemixOutings.cpp` (the dates), `RemixCampfire.cpp`, `RemixEnding.cpp` (the letter).

Nine quests, each given by Moratari wherever she is, each opened by the one before it and a point in the
war (the guide leaves them out of "your next quest"):
1. **WRM-901 A Cup of Something Hot** (after A Time for Heroes or The Defense of Warsong Hold, the
   third quest of each side's Borean Tundra): tea, and what she is asked over it (how old she is,
   whether dragons sleep on gold, why she keeps looking: a word for each race).
2. **WRM-902 Shore Leave** (after Not Yet Late or The Condemned Coast): a drink in Dalaran, at the
   side's own inn, A Hero's Welcome or The Filthy Animal; a kiss on the cheek.
3. **WRM-903 Dinner at Krasus' Landing** (after Into the Dragonblight): her evening dress (a new look,
   the Lovely Red Dress), all of Northrend below, the first kiss.
4. **WRM-904 The View from Wyrmrest** (after Strangers Out of Time): the top of the temple at night,
   where she shows the Timerunner her true shape (the bronze she was before the Infinite), and they
   don't run.
5. **WRM-905 What Eternus Left Out** (after The Weight of Time): she is shaken by the turn; they stay
   with her; "I love you."
6. **WRM-906 On Bronze Wings** (after A Shorter Path Through the Woods): a flight on her back from
   Dalaran to Wyrmrest Temple, her words on the way.
7. **WRM-907 An Adventure of Our Own** (after A Brief Hunting Expedition): an afternoon by a river in
   Sholazar Basin, two crocolisks sent to tomorrow noon, a blanket.
8. **WRM-908 The Lamp That Is Always Lit** (after The Very Long Road to Thorim): her tent at the
   Bazaar, theirs alone (a phase of its own), their gear unseen and hers set aside, the screen fading
   to black, "Good morning." From then on she walks with them everywhere until they go home.
9. **WRM-909 Whatever Comes After** (after The Armies Are in Place): the edge of the camp at
   Crusaders' Pinnacle, and her promise to write.

Any time after the dinner: "Kiss her." After the drink: "Tell her she looks lovely today." (a word for
each race). On the war's last quests she has a few words of her own for them. On ChromieCraft, after
the way home, a letter waits in the mailbox, brought by Chromie: the whole letter for one who finished
her story, a shorter one for one who reached its heart, a note for one who only had tea.

**The campfire.** Clicking the Bazaar's campfire has her walk over from her post and sit with the
Timerunner a while (and nothing happens there otherwise). Only while she sits there can they tell her
they're a time jumper; then her quests open one after another without waiting for the war's points.

## After the turn

From Chapter III on, Eternus is no longer the one guiding you. She keeps trying to save the war's
dead, and each time she picks a quieter grave than the last, hoping history will not miss it. Each
chapter has one of these attempts at its heart: her agents (the Infinite still loyal to her) at the
place where she means to change things, and you stopping them. Then the history she tried to change
goes on as it did.

Moratari's other transitions stay what they were (skipping an afternoon of errands), but they are
hers now, not Eternus's. Every original quest is always still there to play.

Each chapter belongs a little more to one of the people beside you:

- **Chapter III, Alleria.** The thing under the Grizzly Hills has a voice, and she has heard its
  cousins.
- **Chapter IV, Sylvanas.** A troll who sells his people to a king of ice, and a woman who once did
  worse.
- **Chapter V, Moratari.** Eternus herself comes for her, and tells her what she is building.
- **Chapter VI, Eternus.** She offers a grieving god his wife back, and is told the truth about
  kindness.
- **Chapter VII, all of them.** The Frozen Halls, the last of Eternus's hours, and the throne.

Scenes are played for the Timerunner alone (`remix_scene`, `wrath_remix_world_0014_scenes.sql`):
the people in them are summoned where they stand and heard only by that Timerunner.

## Chapter III: The Curse of Grizzly Hills (32 to 42)

1. Arrival at Amberpine Lodge or Conquest Hold (WRM-221 / 222), and each side's Ursoc chain: the
   Alliance's Hierophant Thayreen (The Failed World Tree... Vordrassil's Sapling), the Horde's
   Windseer Grayhorn (Vordrassil's Fall... The Bear God's Offspring).
2. **WRM-303 / 313 The Hollow Crown** (Alleria, beside Thayreen or Grayhorn once Vordrassil's
   Sapling or The Bear God's Offspring is done; she is there from then until it is turned in).
   A scene as it is taken. Eternus's agents have set three Temporal Anchors around Ursoc's Den: she
   means to turn the Bear God back to the years before Vordrassil's roots reached what lies
   beneath, and give the furbolgs their god whole. Break the anchors (their Infinite Rewinders stand
   guard), then speak with Alleria at the den, by Tur Ragepaw.

   > **Alleria:** There is something under these hills, Timerunner. I felt it the moment the bronze
   > set me down. It has a voice, and the voice is very patient.
   >
   > **Alleria:** Eternus has felt something too, but not the same thing. She sees a god driven mad
   > and she thinks: a wound. Wind it back, and the bear is whole again.
   >
   > **Alleria:** The madness is not a wound. It is a whisper, and whispers do not care what year
   > it is. Turn Ursoc back, and it only finds another ear. A druid's. A child's. Yours.
   >
   > **Alleria:** I know that voice. Not this one: a cousin of it. I have had it in my own head.
   >
   > **Alleria:** Go and break her anchors. I will meet you at the den. If you are late, I will
   > come looking, and you will not enjoy being found.

   Ursoc, the Bear God (12249 / 12236) waits for it. As the Bear God's quest is turned in, Alleria
   speaks once more, beside the one who gave it:

   > **Alleria:** He is at peace now. The voice is not. It reaches far deeper than that tree, and it
   > is not alone down there.
   >
   > **Alleria:** You will hear it again at the bottom of Ulduar. ...You may. I cannot know that.
   > When you reach the Storm Peaks, listen for it, and send me word.
   >
   > **Alleria:** I want to know where it is. That is all. Do not read anything into it.

3. **WRM-301 / 311 A Shorter Path Through the Woods** (Moratari, as before): Amberpine Lodge's or
   Conquest Hold's other wars, left to whoever wants them; to Samir, by Drakuru's cages.
4. Drakuru's chain: Filling the Cages, Truce?... Voices From the Dust.
5. **WRM-302 A Friend of Questionable Judgment** (Moratari, at Drak'Tharon's door, no skip).
   Sylvanas has come to the door too, out of sight of the road:

   > **Sylvanas:** So this is Drakuru's errand. A keep full of his own kind, cleansed by a stranger
   > he will thank very warmly.
   >
   > **Sylvanas:** I know the kind of gratitude he will show you. I have shown it myself. Do what
   > he asks, Timerunner. Just do not stand with your back to him.

6. **WRM-321 The Truth About Drakuru** (Moratari, after Cleansing Drak'Tharon): to Light's Breach
   in Zul'Drak, and Chapter IV.

## Chapter IV: The Fallen Empire (42 to 52)

1. **WRM-401 The Things the Scourge Remembers**, **WRM-402 The Paperwork of Betrayal** and
   **WRM-403 A Pilgrim's Shortcut** (Moratari, as before): the way into Voltarus, the way to its
   sabotage, and the loa's pilgrimage to Har'koa.
2. **WRM-405 One Life Too Many** (Sylvanas, at the Ebon Watch beside Stefan Vadu once Sabotage is
   done; she is there until it is turned in). A scene as it is taken. Eternus's agents are under
   Voltarus, opening a rift to carry Drakuru out of history before his master comes for him. Slay
   six Infinite Timesnatchers and close the Unstable Rift, then return to Sylvanas.

   > **Sylvanas:** Eternus has found another life to save. You will not like whose.
   >
   > **Sylvanas:** Drakuru's. The troll who sold his people to the Scourge for a crown. Eternus's
   > agents are beneath Voltarus, opening a door to carry him away before his master comes.
   >
   > **Sylvanas:** Here is what happens if they succeed. The Lich King comes to Voltarus for a
   > traitor and finds no one. He never sees you. He never decides that you are worth keeping for
   > the end. And everything at the top of his citadel waits on that decision.
   >
   > **Sylvanas:** I know what it is to kneel to a king of ice and call it a bargain. I knelt to a
   > worse one, and I called it freedom. Let the troll keep the price he agreed to.

   Betrayal (12713) waits for it. As it is turned in:

   > **Sylvanas:** Good. Now go and betray him. He has earned that much.
   >
   > **Sylvanas:** When the Lich King comes for him, he will look at you. Look back. Remember his
   > face. You will see it again.

3. Betrayal, as the game has it: Drakuru falls on Voltarus, and the Lich King comes for him himself.
4. **WRM-404 The Gods Are Still Silent** and **WRM-421 A Kingdom Gone** (Moratari, as before): the
   last of the loa, Gundrak, and Sholazar Basin.

## Chapter V: The Lifewarden's Warning (52 to 60)

1. **WRM-421** brings the Timerunner to Hemet Nesingwary's camp.
2. **WRM-501 A Brief Hunting Expedition** (Moratari, by Hemet Nesingwary): the hunt's collections,
   admired from a safe temporal distance; to Pilot Vic, whose Force of Nature leads to the Avatar of
   Freya.
3. The Avatar of Freya's chain: Force of Nature, An Issue of Trust, Returned Sevenfold, The Fallen
   Pillar, Cultist Incursion, Exterminate the Intruders, Weapons of Destruction, The Lifewarden's
   Wrath, Freya's Pact.
4. **WRM-502 Stolen Hours** (Moratari, by the Avatar of Freya, after Freya's Pact; taking it goes to
   the Maker's Overlook). Eternus's agents have climbed to the Makers' pillar and are bleeding its
   power away. Slay six Infinite Siphoners and break the Siphon, then speak with Moratari at the
   Overlook. Powering the Waygate waits for it. As it is turned in, Eternus comes for her:

   > **Eternus:** Moratari.
   >
   > **Moratari:** You should not be here.
   >
   > **Eternus:** Neither should you. And yet here we both are, in a garden the titans built so that
   > nothing living here would ever be lost. They wanted what I want, Moratari. They simply had more
   > time.
   >
   > **Moratari:** Your agents were draining the Makers' pillar. I know what that much power is for.
   > You are building something that can hold an hour still.
   >
   > **Eternus:** One hour. Only one. The hour the Lich King falls.
   >
   > **Moratari:** Why that one?
   >
   > **Eternus:** Because it is the last stone in the arch. While it is open, every hour of this war
   > before it is wet ink. Let it close, and every grave is written in stone. I would hold it open
   > long enough to go back. Page by page. Name by name.
   >
   > **Moratari:** And the arch comes down on everyone standing under it.
   >
   > **Eternus:** I would catch them.
   >
   > **Moratari:** No one can catch a world, Eternus. Not even you.
   >
   > **Eternus:** Come home, Moratari. You kept my records for ten thousand years. You know every
   > name I want to save. Help me save them.
   >
   > **Moratari:** I kept your records. That is exactly why I can't.
   >
   > **Eternus:** Then I will remember them for both of us.
   >
   > *(She is gone.)*
   >
   > **Moratari:** She was kind to me, $n, when no one else in my flight was. I hope you never have to
   > choose between a kindness and the truth. I hope you never have to do it twice.

5. The Waygate: Powering the Waygate (the Maker's Perch, the Maker's Overlook), The Etymidian, The
   Activation Rune in Un'Goro, Back Through the Waygate, Reclamation.
6. **WRM-521 The Makers' Trail** (Moratari, by the Avatar of Freya, after Reclamation): to K3 in the
   Storm Peaks, and Chapter VI. Alleria has asked to be told when the Timerunner reaches the
   mountains.

## Chapter VI: The Secrets of Ulduar (60 to 70)

1. K3 and the Sons of Hodir's road: They Took Our Men!, Leave No Goblin Behind, The Crone's
   Bargain... The Hyldsmeet, Taking on All Challengers.
2. **WRM-601 The Very Long Road to Thorim** (Moratari, by Lok'lira the Crone, after Taking on All
   Challengers): the bear, the harness, the last proto-drake and the pit's sparring matches, annotated
   rather than fought; Lok'lira's Parting Gift is next, and the Drakkensryd after it.
3. The Drakkensryd, and Thorim's story: Sibling Rivalry, Mending Fences... Krolmir, Hammer of
   Storms, The Terrace of the Makers.
4. **WRM-602 A Gift of Grief** (Moratari, by Thorim on the Terrace of the Makers, after The Terrace
   of the Makers). Eternus's agents are weaving an echo of Sif out of the hours before she died, to
   stand before her husband. Slay four Infinite Weavers, then speak with Moratari. Loken's Lackeys
   and The Earthen Oath wait for it. As it is turned in, Eternus stands before Thorim herself:

   > **Eternus:** Stormlord. I have watched you grieve for longer than these mountains have had
   > names. Let me give her back to you. Not a memory: her, as she was, before your brother's hand.
   >
   > **Thorim:** My brother gave me a story once. Arngrim, he said. Arngrim killed her. I believed
   > him, because I wanted a name to hate, and I made war on the frost giants for his lie.
   >
   > **Thorim:** I have been fed comfort by those who wanted something from me. I know the taste of
   > it. I will not be lied to with her face. Not by Loken. Not by you.
   >
   > **Eternus:** It is no lie. It is a kindness.
   >
   > **Thorim:** That is what he called it too.
   >
   > **Alleria:** Listen to him, dragon. Grief that is lied to does not heal. It waits. There is
   > something beneath these mountains that has fed on grief for a very long time, and it is
   > listening to you right now.
   >
   > **Eternus:** ...Keep your grief, Stormlord. I will keep mine.
   >
   > *(She is gone.)*
   >
   > **Thorim:** Whoever that was, she loved someone once. It is written all over her. Now: Loken. My
   > brother has much to answer for.
   >
   > **Alleria:** That was meant for you as much as for him. Whatever you were toasting when the
   > bronze found you, do not let anyone sell it back to you. ...As a matter of policy. Go on.

5. Loken's Lackeys, The Earthen Oath, The Reckoning; Loken waits in the Halls of Lightning.
6. **WRM-621 Storm's End** (Moratari, by King Jokkum, after The Reckoning): to the Argent Vanguard
   in Icecrown, before Highlord Tirion Fordring, and Chapter VII.

## Chapter VII: Icecrown (70 to 80)

1. The Argent Crusade's war, as the game has it: Honor Above All Else, Scourge Tactics, Curing the
   Incurable, Defending the Vanguard, If There Are Survivors... The Battle for Crusaders' Pinnacle,
   The Crusaders' Pinnacle.
2. **WRM-702 What He Was Offered** (Moratari, by Tirion at Crusaders' Pinnacle, after Light Within
   the Darkness: only for those who walked Crusader Bridenbrad's road with him). A scene as it is
   taken:

   > **Eternus:** I went to him before the naaru did. I thought: here is one I can save without
   > breaking anything. One paladin, dying in the snow. History would not miss a single tabard.
   >
   > **Eternus:** I offered him a hundred years. Whole, and out of the plague's reach. He asked me if
   > the Light would be in them.
   >
   > **Eternus:** I could not lie to him. He thanked me, and he asked me to go, and he waited for the
   > naaru.
   >
   > **Eternus:** Tell me, Timerunner. Why is it always the ones who most deserve saving who will
   > not let me?
   >
   > **Moratari:** Because they have already decided what their lives are for, Eternus. You never
   > asked any of them.
   >
   > **Eternus:** ...No. I suppose I never did.

3. **WRM-701 / 711 The Armies Are in Place** (Moratari, by Tirion at Crusaders' Pinnacle, after The
   Crusaders' Pinnacle; taking it goes to the Bazaar): the rest of Icecrown's war is in hand;
   Sylvanas wants to see the Timerunner before the Frozen Halls. As it is turned in, at the Bazaar:

   > **Sylvanas:** The Frozen Halls. The forge where he breaks souls, the pit where he works the
   > living to death, and his hall of mirrors at the end of it all.
   >
   > *(the Horde's)* **Sylvanas:** You will meet me in there. The woman I was in this year. She
   > will lead you through the forge and into his halls, and when she finally stands before him she
   > will hate him with everything she has left. And then she will run.
   >
   > *(the Alliance's)* **Sylvanas:** Jaina Proudmoore will lead you in. On the Horde's side of
   > that day, it was me. We went in for different reasons, she and I. She hoped there was
   > something left of him to save. I wanted there to be nothing left of him at all. We both came
   > out running.
   >
   > **Alleria:** You don't have to be anywhere near it, sister.
   >
   > **Sylvanas:** I was there the first time. I am not going in again. If she sees me... I am not
   > going in.
   >
   > **Sylvanas:** Uther waits in those halls, Timerunner. What is left of him. He will tell you what
   > the Lich King is for. Believe him. It will cost you nothing. It cost me everything to learn it.
   >
   > **Alleria:** She means be careful. So do I. A little. Go, before I say something foolish.

   Moratari's way then goes to Dalaran, before Apprentice Nelphi or Dark Ranger Vorel, and Inside
   the Frozen Citadel.
4. The Frozen Halls, as the game has them: Inside the Frozen Citadel, Echoes of Tortured Souls (the
   Forge of Souls), The Pit of Saron, The Path to the Citadel, Deliverance from the Pit, Frostmourne
   and Wrath of the Lich King (the Halls of Reflection, and the escape).
5. **WRM-721 The Last Hour** (Moratari, outside the Frozen Halls once Wrath of the Lich King is
   done; taking it goes to the doors of Icecrown Citadel). Eternus is there with every Infinite
   still loyal to her, and so are Moratari, Sylvanas and Alleria, beside you. She speaks first:

   > **Eternus:** So. You came the long way round, as I knew you would.
   >
   > **Eternus:** Behind those doors is the last hour of this war. A king on a throne of ice, and a
   > paladin who will burn in his place. You know how it ends. So do I. I have watched it end more
   > times than you have drawn breath.
   >
   > **Eternus:** I am not here to stop the Lich King from falling. I am here to keep the hour from
   > closing behind him. Hold this door with me, and every grave in this war stays open long enough
   > for me to reach into it.
   >
   > **Eternus:** And yours, Timerunner. I know the hour I took you from: a table of friends
   > toasting a war they won, and one chair empty. Hold this door with me, and no one ever has to
   > sit beside it.
   >
   > **Sylvanas:** Do not answer her. Not about that chair.
   >
   > **Moratari:** And the arch comes down on all of them, Eternus. On everyone who lives because
   > this war ended the way it did.
   >
   > **Sylvanas:** On me. On my people. On the souls I freed and the ones I failed. You do not get
   > to decide that they were worth less than the ones you mourn.
   >
   > **Alleria:** I can feel the hour you have built, dragon. It isn't open. It's hungry.
   >
   > **Eternus:** Then you will have to take it from me.

   The fight: Eternus and her loyalists, wave after wave, with Moratari, Sylvanas and Alleria
   fighting beside you. As it turns:

   > **Eternus** *(half her strength gone)*: Do you know how many died on the beaches of
   > the Borean Tundra? I do. I counted them. I counted every one.
   >
   > **Eternus** *(a third left)*: Windrunner! I would have given you Quel'Thalas! Not a ruin. Not a
   > grave. Your home, with your people in it!
   >
   > **Sylvanas:** I know. That is why I came.

   She is not killed. With a tenth of her strength left, she stops:

   > **Eternus:** ...Enough.
   >
   > **Eternus:** Not today, then. The river is long, Timerunner, and I am very patient. One day I
   > will find a grave that history does not need.
   >
   > *(She steps into a rift, and is gone.)*
   >
   > **Moratari:** She's gone. Not dead. Eternus has never been any good at dying.
   >
   > **Sylvanas:** The doors are open, Timerunner. Go and end it.
   >
   > **Alleria:** We will be waiting at the Bazaar. All of us. Come back to us. I will not say it
   > twice.

6. **WRM-800 The Last Necessary Battle** (Moratari, at the Citadel's doors, after The Last Hour):
   Icecrown Citadel and the Lich King, as the game has them: the encounter, Tirion, Terenas, and the
   ending cinematic, untouched. Bolvar takes up the Helm.

## The end

1. **The return.** When the ending cinematic is over, the Timerunner is brought back to the Infinite
   Bazaar, where everyone is waiting:

   > **Andormu:** The last hour came as it must. The sacrifices are neither erased nor forgotten.
   >
   > **Nozari:** Bolvar Fordragon sits the Frozen Throne. The record is whole. I have checked it
   > twice.
   >
   > **Sylvanas:** He is gone. I have imagined saying those words for a very long time. They are
   > quieter than I thought they would be.
   >
   > **Alleria:** Welcome back, Timerunner. You took your time. Not that anyone was counting.
   >
   > **Moratari:** Come and see me when you are ready. There is one more thing we have to talk about.

   A letter arrives from Eternus:

   > Timerunner,
   >
   > I watched from the river's edge as you went in. I watched the throne take its new king, and the
   > paladin take up the cold I wanted to spare him. The record held. It always holds, when people
   > like you are standing under it.
   >
   > I will not tell you I was wrong. I will tell you that tonight, for the first time in a very
   > long while, I have stopped counting graves, and I do not yet know what to do with my hands.
   >
   > If you see Moratari, tell her the records are hers now. She always kept them better than I did.
   >
   > E.

2. **WRM-801 See You Later** (Moratari, after The Last Necessary Battle). Moratari tells you it is
   time to go home, and what that means:

   > **Moratari:** You did it. All of it, exactly as it happened. That was the hardest thing anyone
   > has ever asked of you, and nobody will ever thank you for it.
   >
   > **Moratari:** Some of what you did here will never be known, $n. Not by the people you saved
   > it for, not by anyone in your own time. Time is unreliable that way; it keeps its debts quietly.
   >
   > **Moratari:** And there is one more thing. Sylvanas and Alleria cannot take this home with them.
   > Everything they saw here, everything they told you about what comes after: if they remember it,
   > it bleeds into choices they have not made yet. So before they go, I am going to take it from
   > them.
   >
   > **Moratari:** And a little from you, $n. Northrend you keep; you earned it. But whatever they
   > tell you of your own years ahead, the shore you are going back to and everything after it, I
   > will take that too. You would try to change it. Anyone would.
   >
   > **Moratari:** Say your goodbyes. Ask them anything you like. They have a great deal they could
   > tell you, and for a little while longer, you will both remember it.

   Say goodbye to Sylvanas, Alleria, Andormu and Nozari, then speak with Moratari.

3. **Their stories.** Until you go, Sylvanas and Alleria will talk with you about what comes after
   this war, as people talk: one conversation for each age, in their own words, asked as a veteran
   of this war would ask (all of it is your future).
   Moratari, asked whether you will remember any of it: Northrend, yes; your own years ahead, no.

   Sylvanas:
   - *After this war*: in a few days her past self will climb this citadel, find him already dead,
     a paladin in his crown and the victory hollow, and throw herself from the top; what she saw on the way down, and the
     val'kyr who brought her back; Gilneas; Garrosh; years you have not lived yet.
   - *Garrosh*: he becomes Warchief, makes the Horde a weapon and points it at everyone, the
     Forsaken included; when the Horde turns on him, she turns with it. Then his madness, an old
     world dragged into a new war, and something that comes for all of them: you will be standing
     on a dock when it does.
   - *Does the Legion come back?*: it does, years from your tavern; she was on the Broken Shore and will not tell
     you what happens there; she tells you only what you will hear soon enough: Vol'jin, wounded to death there, named her Warchief and said the
     spirits told him to; Stormheim, where she tried to bind a queen of the val'kyr so her people would never stop
     rising, and Genn Greymane stopped her.
   - *After the Legion*: you will hear the name Teldrassil beside hers, and she will not explain it; Lordaeron, the home she made
     for her people, where she poisoned her own city before she would give it up; Varok Saurfang, who asked her a question she
     answered badly, and died.
   - *The Helm, and Bolvar*: the Helm, broken on Bolvar's head at the top of this citadel; the sky torn
     open; the Jailer she thought she could use, who used her; the judgment, and her sentence.
   - *Now*: the Maw, and the souls she frees one at a time; the war beneath the earth, heard of the
     way the dead hear things, and last, before Chromie found her, that the Void had come for
     Quel'Thalas and her sister was standing in its way.
   - *Her sisters*: Alleria, who went through the Dark Portal and came back a thousand years older;
     Vereesa, in Dalaran in this year with her husband and her boys; Rhonin's death at Theramore,
     which the Timerunner knows too, and neither of them will tell her.

   Alleria:
   - *Everyone thinks you're dead*: in this year, and in the Timerunner's, she is beyond the
     Twisting Nether with Turalyon and the Army of the Light; they will go home to a world that
     still tells her story with an ending, and should not correct it.
   - *Coming home* (she will tell it, since Moratari will take it anyway): Argus, Xe'ra and Illidan, the Light that wanted very badly to be obeyed.
   - *The dark in her* (the Void): Locus-Walker, who taught her on Argus; L'ura at the Seat of the Triumvirate, whom she took
     into herself.
   - *Her people now* (the ren'dorei): Magister Umbric's exiles, Telogrus Rift, and leading people who only wanted to
     understand what had been done to them.
   - *Her son*, Arator: the son she and Turalyon left behind as a baby (Vereesa kept him safe for a while),
     grown and a paladin by the time they came home.
   - *When the Helm broke*: the sky over Icecrown torn open, and every soul going the wrong way, felt in
     the Void like a door left open in winter.
   - *Who she is fighting, in her own time*: Xal'atath, the Harbinger of the Void, who wears her
     fears; Khaz Algar first, then Quel'Thalas, the Sunwell, home; why she will keep fighting.
   - *Sylvanas*: she asked Alleria to come. She has never asked her for anything. And she is careful
     with the Timerunner; she is not the only one, Alleria supposes, and then: "We were talking about
     Sylvanas."
   - *Why she keeps looking out for you*: she does not; you are imagining it; you are not. Ask her
     again when you say goodbye.

   Her stories carry her guard too: you would hate Argus, and go anyway; the Void is hers to carry
   and she does not need anyone worrying over her, you least of all; someone once told her going
   first is the only leading worth the name, and she will not say who; family is sometimes only the
   people who keep turning up ("That is a general observation").

   Her goodbye is the reveal: where she comes from, you are family, her brother or sister in every
   way that counts; Turalyon says she treats you as she treated Lirath, and he is right; she kept her
   distance so you could find your own way to it. She embraces you, briefly, and lets go before you
   can return it: "Go home, Timerunner. Hug someone for me. You don't have to tell them why. I will
   see you in the future, $n. Try not to be late. You always are."

4. **WRM-802 Back to Your Own Time** (Moratari, after See You Later). As it is taken:

   > **Moratari:** This is the part I have been dreading.
   >
   > **Moratari:** Sylvanas. Alleria. You know what I have to do.
   >
   > **Alleria:** We know. Time is not fond of people who remember too much of it.
   >
   > **Sylvanas:** Be quick about it, Moratari. I have had enough long goodbyes for one eternity.
   >
   > **Sylvanas:** $n. Whatever I become, whatever they say of me where you are going: you saw
   > this. Keep it for me.
   >
   > **Sylvanas:** And when we meet, the way we are meant to, do not tell me any of this. Let me find
   > you the long way.
   >
   > **Alleria:** And if you see my son... no. Don't tell him anything. He'll know.
   >
   > **Alleria:** And you, $n. You heard me the first time. I will see you in the future. Do not be
   > late.
   >
   > *(Moratari's spell takes them.)*
   >
   > **Alleria:** ...Strange. I had the oddest feeling I was about to say goodbye to someone.
   >
   > **Sylvanas:** Chromie. Take us home. Wherever this is, I do not like it.
   >
   > *(They are gone.)*
   >
   > **Moratari:** There. They will wake in their own times with nothing but a feeling they cannot
   > name. That is the kindest thing I know how to do.
   >
   > **Moratari:** Now you. Hold still. Northrend stays with you: the war, the echoes, the two of
   > them. Only what they told you of the years ahead goes back to the hours it came from.
   >
   > *(The spell takes that from the Timerunner too.)*
   >
   > **Moratari:** There. You will go home not knowing how your war ends, the way everyone else goes
   > into theirs. It is the only fair way to go.
   >
   > **Moratari:** But I will remember. Someone has to. Goodbye, Timerunner. Go home.

   **Home.** As Legion Remix does, the Timerunner goes to the ChromieCraft realm: at the level they
   reached, with everything they carry (it is all Wrath's own; Bronze stays behind at the Bazaar).
   The game closes, the server starts again on ChromieCraft, and they log in in their side's
   capital, Stormwind or Orgrimmar. The Timerunner leaves Wrath Remix.

## Status

Built in this order: the prologue and Chapter I (build 64), Report Time Anomaly and Chapter II with
the turn (build 65), and now Chapters III to VII after the turn, Eternus's last hour, the return and
the way home.
