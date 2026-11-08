"""The Alliance's Borean Tundra, while Moratari and Eternus steer the war (STORY.md, "Moratari in the
war"; tools/story.py writes it).

Before the turn, Moratari walks with the Timerunner and acts on what she knows of the war, quietly:
no one of this year may learn how. The interventions, in the order the chain meets them:

- WRM-041 A Word in the General's Ear: warn General Arlos and Sergeant Hammerhill of the siege, the
  flyers and the ground. The general, at Counselor Talbot's elbow, waves it away; the sergeant
  listens (the catapults Eternus's note speaks of, moved because he did).
- WRM-042 The Fourth Sinkhole: the cult's necrolytes at the northern sinkhole, and a fourth tunnel
  that history never records, collapsed by Moratari before it opens.
- WRM-043 Not Yet Late: William Allerton, saved from the cult's knife in the Farshire Mine (the
  game has him dead, his throat cut, "no bite or claw marks").
- WRM-044 Named for No Town: Allerton's testimony, Old Man Colburn and Private Brau: Unit S ("'S'
  stood for suicide"), and whose hand signed it.
- WRM-045 No One Left Behind: four of Unit S taken alive to En'kilah, freed; the volunteers
  Hammerhill sent east because the Timerunner warned him.
- WRM-046 Before She Gets Hurt: Leryssa warned and Vindicator Yaala asked to watch her. It fails:
  Last Rites plays as the game has it, because Valanar's unmasking needs his "offerings".
- WRM-047 The Keep Holds: the chapter's new end, at Valiance Keep: Arlos himself again, Vurenn's
  regiments accepted, and the road to Wintergarde.

After the turn, story_undo.py puts back what the record cannot keep (Allerton, Unit S).
"""
from story_common import (ALLIANCE, MORATARI, TAKEN, DONE, TURNED_IN, OUTING, ZONE_BOREAN_TUNDRA,
                          INTO_THE_DRAGONBLIGHT_A, rewarded, not_rewarded, state, IN_PROGRESS, NOT_TAKEN,
                          OBJECTIVES_DONE, TAKEN_OR_DONE)

# The game's people
BLYTHE, ARLOS, TALBOT, VURENN, HAMMERHILL, MARK_HANES = 25307, 25250, 25301, 25285, 25816, 26155
LERYSSA, ALLERTON, COLBURN, BRAU, YAALA, DEACON = 25251, 25385, 25302, 25395, 25826, 25245
VENN, CASEY, THASSARIAN, CULTIST_NECROLYTE = 26187, 26186, 26170, 25651

# The game's quests on the way
ENLISTMENT_DAY, A_TIME_FOR_HEROES, THE_SIEGE, DEATH_FROM_ABOVE, PLUG_THE_SINKHOLES = 11672, 11727, 11797, 11889, 11897
KINDNESS, WORD_AT_THE_GATE, WORD_ON_THE_STREET = 77017, 77019, 11927
THASSARIAN_MY_BROTHER, A_USEFUL_OMISSION = 11599, 77006
THASSARIAN_THE_DEATH_KNIGHT, FINDING_THE_PHYLACTERY, BUYING_SOME_TIME, WORDS_OF_POWER, LAST_RITES = 12088, 11956, 11938, 11942, 12019

# This file's quests
WORD_IN_THE_EAR, FOURTH_SINKHOLE, NOT_YET_LATE, NAMED_FOR_NO_TOWN, NO_ONE_LEFT_BEHIND = 77041, 77042, 77043, 77044, 77045
BEFORE_SHE_GETS_HURT, THE_KEEP_HOLDS = 77046, 77047
LOST_AT_SEA, FORGED_ORDERS = 77048, 77049    # the undoing (story_undo.py)

# Credits (never spawned) and new creatures
C_ARLOS, C_HAMMERHILL, C_SINKHOLE, C_COLBURN, C_BRAU = 770530, 770531, 770532, 770533, 770534
C_HARKER, C_DUNN, C_MABRY, C_SORREL, C_LERYSSA, C_YAALA = 770535, 770536, 770537, 770538, 770539, 770540
LIVING_ALLERTON, CULT_ASSASSIN = 770550, 770551
HARKER, DUNN, MABRY, SORREL = 770552, 770553, 770554, 770555
UNIT_S_SURVIVOR, VOLUNTEER, DRAENEI_VANGUARD = 770556, 770557, 770558

SCENE_FOURTH_SINKHOLE, SCENE_KEEP_HOLDS = 101, 102

CREATURES = [
    dict(entry=C_ARLOS, name="General Arlos warned", credit=True),
    dict(entry=C_HAMMERHILL, name="Sergeant Hammerhill warned", credit=True),
    dict(entry=C_SINKHOLE, name="The fourth sinkhole collapsed", credit=True),
    dict(entry=C_COLBURN, name="Old Man Colburn asked about Unit S", credit=True),
    dict(entry=C_BRAU, name="Private Brau asked who signed the order", credit=True),
    dict(entry=C_HARKER, name="Private Harker freed", credit=True),
    dict(entry=C_DUNN, name="Private Dunn freed", credit=True),
    dict(entry=C_MABRY, name="Corporal Mabry freed", credit=True),
    dict(entry=C_SORREL, name="Private Sorrel freed", credit=True),
    dict(entry=C_LERYSSA, name="Leryssa warned", credit=True),
    dict(entry=C_YAALA, name="Vindicator Yaala asked to watch over Leryssa", credit=True),
    # William Allerton as he is when someone gets to the mine in time: the game's, alive (no corpse's
    # look, no feigned death), who can be spoken to and takes back Thassarian, My Brother.
    dict(entry=LIVING_ALLERTON, **{"from": ALLERTON}, name="William Allerton", npcflag=3, dynamicflags=0, unit_flags=768, flags_extra=2,
         auras="", why="William Allerton, alive (WRM-043)"),
    dict(entry=CULT_ASSASSIN, **{"from": 25605}, name="Cult Assassin", subname="Cult of the Damned",
         why="The cult's assassin sent for Allerton, in a Valiance tabard (WRM-043)"),
    dict(entry=HARKER, **{"from": 25313}, name="Private Harker", subname="Unit S", npcflag=1, faction=35, unit_flags=770, stand=8,
         why="Unit S's captives at En'kilah (WRM-045)"),
    dict(entry=DUNN, **{"from": 25313}, name="Private Dunn", subname="Unit S", npcflag=1, faction=35, unit_flags=770, stand=8),
    dict(entry=MABRY, **{"from": 25313}, name="Corporal Mabry", subname="Unit S", npcflag=1, faction=35, unit_flags=770, stand=8),
    dict(entry=SORREL, **{"from": 25313}, name="Private Sorrel", subname="Unit S", npcflag=1, faction=35, unit_flags=770, stand=8),
    dict(entry=UNIT_S_SURVIVOR, **{"from": 25313}, name="Unit S Survivor", subname=None, unit_flags=770,
         why="The freed men of Unit S, at Death's Stand"),
    dict(entry=VOLUNTEER, **{"from": 25313}, name="Valiance Volunteer", subname="Sergeant Hammerhill's", unit_flags=770,
         why="The men Hammerhill sent east, because the Timerunner warned him"),
    dict(entry=DRAENEI_VANGUARD, **{"from": 25300}, name="Draenei Vanguard", subname="Harbinger Vurenn's", unit_flags=770,
         why="Vurenn's regiments, accepted at last (WRM-047)"),
]

# Who sees them: the living Allerton from the moment the Timerunner sets out to save him, until he
# sails (WRM-048), and after it to whoever still has Thassarian, My Brother to give him (Leryssa offers
# it all the while, and he is its only ender then); the dead one only for whoever never set out; the
# assassin while it's being done; the captives while they wait; the survivors and volunteers from their
# rescue until the record takes them back (WRM-049); the draenei from the keep's new day.
ALIVE = [[state(NOT_YET_LATE, TAKEN_OR_DONE), not_rewarded(LOST_AT_SEA)],
         [state(NOT_YET_LATE, TAKEN_OR_DONE), state(THASSARIAN_MY_BROTHER, IN_PROGRESS | OBJECTIVES_DONE)]]
SAVED = [[rewarded(NO_ONE_LEFT_BEHIND), not_rewarded(FORGED_ORDERS)]]
SPAWNS = [
    dict(guid=7704330, equip=0, entry=LIVING_ALLERTON, x=2768.0, y=5339.9, z=30.03, o=3.05, visible=ALIVE,
         why="William Allerton, alive, Farshire Mine"),
    dict(guid=7704331, entry=CULT_ASSASSIN, x=2765.9, y=5340.2, z=30.03, o=6.20, respawn=30,
         visible=[[state(NOT_YET_LATE, IN_PROGRESS)]], why="the cult's assassin over Allerton"),
    dict(guid=7704332, entry=HARKER, x=3845.6, y=3726.4, z=47.4, o=3.60, visible=[[state(NO_ONE_LEFT_BEHIND, IN_PROGRESS)]],
         why="Private Harker, captive, En'kilah"),
    dict(guid=7704333, entry=DUNN, x=3847.8, y=3729.6, z=47.5, o=3.60, visible=[[state(NO_ONE_LEFT_BEHIND, IN_PROGRESS)]],
         why="Private Dunn, captive, En'kilah"),
    dict(guid=7704334, entry=MABRY, x=3836.4, y=3728.2, z=47.3, o=0.30, visible=[[state(NO_ONE_LEFT_BEHIND, IN_PROGRESS)]],
         why="Corporal Mabry, captive, En'kilah"),
    dict(guid=7704335, entry=SORREL, x=3843.0, y=3721.0, z=47.2, o=1.60, visible=[[state(NO_ONE_LEFT_BEHIND, IN_PROGRESS)]],
         why="Private Sorrel, captive, En'kilah"),
    dict(guid=7704336, entry=UNIT_S_SURVIVOR, x=3110.2, y=3838.4, z=22.85, o=5.75, visible=SAVED, why="Unit S, Death's Stand"),
    dict(guid=7704337, entry=UNIT_S_SURVIVOR, x=3117.6, y=3839.2, z=22.80, o=3.40, visible=SAVED, why="Unit S, Death's Stand"),
    dict(guid=7704338, entry=UNIT_S_SURVIVOR, x=3109.4, y=3843.6, z=22.80, o=5.20, visible=SAVED, why="Unit S, Death's Stand"),
    dict(guid=7704339, entry=UNIT_S_SURVIVOR, x=3117.9, y=3846.2, z=22.75, o=3.90, visible=SAVED, why="Unit S, Death's Stand"),
    dict(guid=7704340, entry=VOLUNTEER, x=3104.5, y=3830.5, z=23.20, o=5.60, visible=SAVED, why="volunteers, Death's Stand"),
    dict(guid=7704341, entry=VOLUNTEER, x=3120.6, y=3830.4, z=22.90, o=4.20, visible=SAVED, why="volunteers, Death's Stand"),
    dict(guid=7704342, entry=VOLUNTEER, x=3290.5, y=3679.5, z=32.55, o=0.40, visible=SAVED, why="volunteers holding the Wailing Ziggurat"),
    dict(guid=7704343, entry=VOLUNTEER, x=3289.6, y=3686.4, z=32.55, o=5.90, visible=SAVED, why="volunteers holding the Wailing Ziggurat"),
    dict(guid=7704344, entry=VOLUNTEER, x=3304.0, y=3678.6, z=32.55, o=2.60, visible=SAVED, why="volunteers holding the Wailing Ziggurat"),
    dict(guid=7704345, equip=0, entry=DRAENEI_VANGUARD, x=2119.8, y=5303.2, z=32.86, o=3.20, visible=[[rewarded(THE_KEEP_HOLDS)]],
         why="Vurenn's vanguard, Valiance Keep's barracks"),
    dict(guid=7704346, equip=0, entry=DRAENEI_VANGUARD, x=2120.6, y=5306.0, z=32.86, o=3.20, visible=[[rewarded(THE_KEEP_HOLDS)]],
         why="Vurenn's vanguard, Valiance Keep's barracks"),
    dict(guid=7704347, equip=0, entry=DRAENEI_VANGUARD, x=2119.9, y=5308.6, z=32.86, o=3.20, visible=[[rewarded(THE_KEEP_HOLDS)]],
         why="Vurenn's vanguard, Valiance Keep's barracks"),
]

HIDE = [
    # Allerton's corpse, for whoever set out to save him in time.
    dict(guid=99763, entry=ALLERTON, visible=[[state(NOT_YET_LATE, NOT_TAKEN)]], why="Allerton's corpse, unless he was saved"),
    # Counselor Talbot in the barracks, once Prince Valanar has died at Naxxanar (the game leaves him
    # standing beside the general afterwards).
    dict(guid=115989, entry=TALBOT, visible=[[not_rewarded(LAST_RITES)]], why="Counselor Talbot, gone after Last Rites"),
]

# Allerton alive takes back Thassarian, My Brother (Leryssa sends the Timerunner to him).
RELATIONS = [("ender", LIVING_ALLERTON, THASSARIAN_MY_BROTHER)]

COMMON = dict(side=ALLIANCE, sort=ZONE_BOREAN_TUNDRA, level=-1, min=10, bronze=800)

QUESTS = [
    dict(COMMON, id=WORD_IN_THE_EAR, title="A Word in the General's Ear", prev=ENLISTMENT_DAY,
         log="Warn General Arlos and Sergeant Hammerhill of what is coming to Valiance Keep, without telling them how you know.",
         desc="You remember this week, don't you? The crawlers on the beach. The flyers over the inner wall. And on the third night, the ground "
              "opening under the western ridge.$B$BThis time, they can be ready. Tell the general in the barracks, and the sergeant at the "
              "barricade. Not how you know, $N: no one in this year may learn that. Say your scouts saw worm-trails on the ridge.$B$B"
              "And mind the counselor at the general's elbow. Tell him nothing you would not tell the Scourge.",
         done="Return to Moratari.",
         objectives=[(C_ARLOS, 1, "General Arlos warned"), (C_HAMMERHILL, 1, "Sergeant Hammerhill warned")],
         request="Well? Did they listen?",
         reward="The general did not believe you. The sergeant did. In my experience, sergeants are the most useful variable in any war.$B$B"
                "And you lie rather well, for an honest $c. I mean that kindly."),
    dict(COMMON, id=FOURTH_SINKHOLE, title="The Fourth Sinkhole", prev=PLUG_THE_SINKHOLES,
         log="Slay 6 Cultist Necrolytes at the northern sinkhole, then go with Moratari to the dunes behind the beach line.",
         desc="Eternus told you there was a fourth. It opens under the dunes behind the beach, the same night as the others, and what comes "
              "out of it reaches the docks before anyone can sound a horn.$B$BIt has not opened yet. The worms are still digging, and the "
              "cult's necrolytes at the northern sinkhole are feeding them, chanting the dead awake under the sand.$B$BKill the necrolytes. "
              "Then come with me to the dunes, and I will show you what can be done with wooden supports and a little time.",
         done="Return to Moratari.",
         objectives=[(CULTIST_NECROLYTE, 6, ""), (C_SINKHOLE, 1, "The fourth sinkhole collapsed")],
         request="Not yet? The worms will not wait for us.",
         reward="Then the docks stay quiet. Hammerhill will sleep through that night and never know why."),
    dict(COMMON, id=NOT_YET_LATE, title="Not Yet Late", prev=WORD_ON_THE_STREET, ender=LIVING_ALLERTON,
         log="Reach William Allerton in the Farshire Mine before the cult's assassin does.",
         desc="Leryssa is about to ask you to find a family friend of hers, William Allerton, at the Farshire mine. Say yes. Then run.$B$B"
              "The first time, you found him on the floor of that mine with his throat cut, and not a claw mark on him. A man in a Valiance "
              "tabard got there an hour before you did.$B$BWilliam knows where they sent Thassarian. That is why he died. Today, I would "
              "rather he didn't.",
         done="Speak with William Allerton.",
         objectives=[(CULT_ASSASSIN, 1, "")],
         request="<William Allerton is pressed against the wall of the mine, staring at the knife.>",
         reward="You... you're not one of them? <William Allerton slides down the wall of the mine, shaking.>$B$BHe said he had orders for me "
                "from the inner hold. I took the paper from him, and he drew a knife.$B$BWhoever you are, thank you."),
    dict(COMMON, id=NAMED_FOR_NO_TOWN, title="Named for No Town", prev=NOT_YET_LATE, giver=LIVING_ALLERTON, ender=LERYSSA,
         log="Ask Old Man Colburn at the inn and Private Brau in the barracks jail about Unit S, then tell Leryssa what you have learned.",
         desc="I saw Thassarian in the enlistment line, $c, plain as I see you. Dead all these years, and there he stood, signing his name.$B$B"
              "The next day they put him in charge of something called Unit S and sent him east. Every other unit in this expedition is "
              "named after a town. I started asking why. You've seen where that got me.$B$BOld Colburn at the inn knows more about this army "
              "than the army does; ask him. And there's a deserter in the barracks jail, Brau, who was in Unit S before he ran. Ask him who "
              "signed the order.$B$BThen tell Leryssa. She deserves to know where her brother went.",
         done="Return to Leryssa at the Valiance Keep inn.",
         objectives=[(C_COLBURN, 1, "Old Man Colburn asked about Unit S"), (C_BRAU, 1, "Private Brau asked who signed the order")],
         request="Did you find William? Is he...",
         reward="William's alive? Oh, thank the Light. <Leryssa sits down, hard.>$B$BThe counselor. He's at the general's side every hour of "
                "the day, and he signed my brother's death warrant.$B$BPlease, $N. Find Thassarian before they finish what they started."),
    dict(COMMON, id=NO_ONE_LEFT_BEHIND, title="No One Left Behind", prev=A_USEFUL_OMISSION, ender=VENN,
         log="Free Private Harker, Private Dunn, Corporal Mabry and Private Sorrel of Unit S, held in the Temple City of En'kilah, then "
             "return to Corporal Venn at Death's Stand.",
         desc="Venn has written off the rest of Unit S. Most of them are dead. Four are not.$B$BThe cult took them alive, to the "
              "necromancers' yard in the Temple City of En'kilah, north of here. No one ever goes looking for them, and within the week the "
              "cult has four new servants who used to be Stormwind boys.$B$BGo and get them, $N. Tell them Valiance Keep sent you. It is "
              "kinder than the truth, and they will believe it.",
         done="Return to Corporal Venn at Death's Stand.",
         objectives=[(C_HARKER, 1, "Private Harker freed"), (C_DUNN, 1, "Private Dunn freed"), (C_MABRY, 1, "Corporal Mabry freed"),
                     (C_SORREL, 1, "Private Sorrel freed")],
         request="From Valiance Keep? Tell me there's more of you on the road.",
         reward="Harker? Dunn? <Corporal Venn grabs the nearest man by the shoulders, laughing.> We gave you up for dead! I said the words "
                "over you myself!$B$BAnd Hammerhill's sent volunteers up from the keep. Says the siege left him men to spare, for once. "
                "Remind me to buy that dwarf a barrel.$B$BI don't know how you found them, $N, and I'm not going to ask."),
    dict(COMMON, id=BEFORE_SHE_GETS_HURT, title="Before She Gets Hurt", prev=THASSARIAN_THE_DEATH_KNIGHT,
         log="Warn Leryssa, and ask Vindicator Yaala to watch over her, at Valiance Keep's inn. Moratari will take you there and back.",
         desc="'We must finish this before she gets hurt.' He is right to be afraid, $N. In the record, the counselor's men come for Leryssa "
              "within the week, and she is taken to the top of Naxxanar as an offering.$B$BI can fold the road to Valiance Keep and back. "
              "Warn her. Ask the draenei vindicator at the inn to watch over her. And then... we will see what the hour allows.",
         done="Return to Moratari.",
         departure=(571, 2272.6, 5186.2, 20.38, 3.40),
         bridge=dict(at=(571, 3292.8, 3679.6, 32.55, 0.60)),
         objectives=[(C_LERYSSA, 1, "Leryssa warned"), (C_YAALA, 1, "Vindicator Yaala asked to watch over Leryssa")],
         request="What did she say?",
         reward="She will not run, and Yaala will not sleep. Whether that is enough, we will know at the top of Naxxanar.$B$BBack to "
                "Thassarian, then."),
    dict(COMMON, id=THE_KEEP_HOLDS, title="The Keep Holds", prev=LAST_RITES, ender=ARLOS, bronze=1500,
         log="Speak with General Arlos in Valiance Keep's barracks.",
         desc="Talbot is dead, and his hold on the general's mind died with him. For the first time since he landed, Arlos is himself, and "
              "he has asked for you.$B$BCome; I will fold the road.",
         done="Speak with General Arlos.",
         departure=(571, 2110.2, 5300.6, 34.09, 2.30),
         reward="<General Arlos looks older than he did a week ago. He also looks awake.>$B$BCome in, $N. There is a great deal I need to say, "
                "and most of it is an apology."),
]

# The game's own quests, placed in the story.
GATES = {
    A_TIME_FOR_HEROES: [[rewarded(WORD_IN_THE_EAR)]],
    KINDNESS: [[rewarded(FOURTH_SINKHOLE)]],
    THASSARIAN_MY_BROTHER: [[state(NOT_YET_LATE, TAKEN_OR_DONE)]],
    A_USEFUL_OMISSION: [[rewarded(NAMED_FOR_NO_TOWN)]],
    FINDING_THE_PHYLACTERY: [[rewarded(BEFORE_SHE_GETS_HURT)]],
    INTO_THE_DRAGONBLIGHT_A: [[rewarded(THE_KEEP_HOLDS)]],
}

TEXTS = {
    THASSARIAN_MY_BROTHER: dict(
        reward="<William Allerton presses a rag to the shallow cut along his neck.>$B$BLeryssa sent you? She came all this way? Light bless "
               "that stubborn girl.$B$BI should never have written to her. If they'll do this to me for asking about Thassarian, what will "
               "they do to her?"),
    BUYING_SOME_TIME: dict(
        reward="That should buy us some time. Isidorus has been cooperative, but I really needed that alone time with the lich.$B$B"
               "<Thassarian nods toward the Valiance volunteers at the ziggurat's edge.>$B$BAnd thank Hammerhill's lads for me. I didn't ask "
               "for help. It came anyway. I'd forgotten what that was like."),
}

PLACES = [
    dict(quest=FOURTH_SINKHOLE, credit=C_SINKHOLE, x=2332.0, y=5470.0, radius=14, scene=SCENE_FOURTH_SINKHOLE,
         text="Here. Under the dune. Put your ear to the sand."),
]

TALK = [
    # WRM-041
    dict(npc=ARLOS, quest=WORD_IN_THE_EAR, credit=C_ARLOS,
         option="General, the crawlers on the beach are only the vanguard. My scouts found worm-trails on the western ridge, and their flyers "
                "will come over the inner wall.",
         reply="<General Arlos glances at Counselor Talbot before he answers.>$B$BYour concern does you credit, $N. But Counselor Talbot has "
               "the ridge reports, and he assures me there is nothing in them to trouble us. The walls will hold.$B$BIf your scouts are still "
               "uneasy, take it to Sergeant Hammerhill. The defenses are his to worry about."),
    dict(npc=TALBOT, quest=WORD_IN_THE_EAR,
         option="Counselor, the general says you have the ridge reports. I'd like to see them.",
         reply="<Counselor Talbot smiles. It does not reach his eyes.>$B$BThe ridge reports are for the general's staff, $N. Our men are "
               "villagers, mostly, and villagers see worms in every shadow. Surely you didn't come all the way to Northrend to chase their "
               "superstitions?$B$BDo tell your scouts to be careful up there. It would be a shame to lose them."),
    dict(npc=HAMMERHILL, quest=WORD_IN_THE_EAR, credit=C_HAMMERHILL,
         option="Sergeant, they'll dig under the western ridge and come at the south wall from behind your line. And their flyers will hit "
                "the inner defenses.",
         reply="Under the ridge, eh? <Sergeant Hammerhill tugs at his beard.> Blasted worms. Years in the mines teach you to listen to the "
               "ground, and it's been grumbling at me since we landed.$B$BThe general can keep his reports. I'll have two catapults on the "
               "south wall by dark and spotters up on that ridge, and if anyone asks, they walked there on their own.$B$BIf you're wrong, "
               "I've lost a night's sleep. If you're right, I owe you a drink."),
    # WRM-044
    dict(npc=COLBURN, quest=NAMED_FOR_NO_TOWN, credit=C_COLBURN,
         option="Colburn, what do you know about Unit S?",
         reply="<Old Man Colburn looks up from his empty cup, and for a moment his eyes are sharp.>$B$BUnit S... hmmph. Don't make any "
               "sense. Darkshire went to the Dragonblight. The Goldshire boys went to the Fjord. I know every unit, every brigade, every "
               "detachment in this expedition, and there's no S.$B$BSo somebody made it up. And people don't make up units to send them "
               "somewhere nice."),
    dict(npc=BRAU, quest=NAMED_FOR_NO_TOWN, credit=C_BRAU,
         option="Private, who signed the order that sent Unit S east?",
         reply="<Private Brau looks past you at the guard by the door, and drops his voice.>$B$B'S' stood for suicide. That's what the lads "
               "called it. A dozen of us against a Scourge ziggurat. Call me a coward if you like; I know a grave when I'm marched into "
               "one.$B$BThe orders came down from the inner hold with the general's seal on them, but the general never signed nothing, "
               "friend. I ran letters up there before they put me in that unit. I saw the hand. It was the counselor's.$B$BDon't say I told "
               "you. That one hears everything."),
    # WRM-045
    dict(npc=HARKER, quest=NO_ONE_LEFT_BEHIND, credit=C_HARKER, option="Private Harker? Get up. Valiance Keep sent me. Head for Death's Stand.",
         reply="Sent? Somebody sent... <Private Harker scrambles to his feet.> Yes, $Gsir:ma'am;. Death's Stand. I can walk. I can run, if it "
               "comes to it."),
    dict(npc=DUNN, quest=NO_ONE_LEFT_BEHIND, credit=C_DUNN, option="Private Dunn. On your feet, soldier. Death's Stand, now.",
         reply="I knew it. I told Harker someone would come. He said I was mad. <Private Dunn laughs, too loudly, then stops.> Death's Stand. Yes."),
    dict(npc=MABRY, quest=NO_ONE_LEFT_BEHIND, credit=C_MABRY, option="Corporal Mabry. Your men are getting out. Lead them to Death's Stand.",
         reply="Lead them. Right. <Corporal Mabry rubs his rope-burned wrists.> The cult said we'd be serving them by the full moon. Tell "
               "whoever sent you... no. I'll tell them myself."),
    dict(npc=SORREL, quest=NO_ONE_LEFT_BEHIND, credit=C_SORREL, option="Private Sorrel. Can you stand? Death's Stand is south. Go.",
         reply="<Private Sorrel stares at you as if you were a ghost.>$B$BThey said no one knew we were here. They said we didn't even have a "
               "name.$B$B...South. Yes. South."),
    # WRM-046
    dict(npc=LERYSSA, quest=BEFORE_SHE_GETS_HURT, credit=C_LERYSSA,
         option="Leryssa, the counselor knows you're asking about Thassarian. Leave Valiance Keep tonight. Take the Kraken home.",
         reply="Go home? <Leryssa laughs, not kindly.>$B$BI sold everything I had to get here, $N. My brother is out there somewhere, alive, "
               "and you want me to sail away before I've even seen his face?$B$BNo. Let them come. I'm not leaving without him."),
    dict(npc=YAALA, quest=BEFORE_SHE_GETS_HURT, credit=C_YAALA,
         option="Vindicator, the woman upstairs is in danger. Someone in the inner hold wants her silenced. Will you watch over her?",
         reply="<Vindicator Yaala's eyes narrow.>$B$BThe inner hold. You choose your words carefully, $c. So do I.$B$BI have hunted this cult "
               "through the keep since we landed: the docks, the jail, this inn's own kitchen. I had not thought it reached so high.$B$BI "
               "will watch over the girl. If anyone comes for her, they will have to come through me."),
]

SCENES = [
    # WRM-042: the fourth sinkhole, at the dunes (where the Timerunner stands as it starts).
    dict(id=SCENE_FOURTH_SINKHOLE, name="The fourth sinkhole: Moratari and the supports", quest=0, trigger=0, anchor=0,
         credit=C_SINKHOLE, steps=[
             ("summon", 1, 770013, 1.5, 2.0, -0.6),
             ("summon", 2, 26250, 8.0, 0.0, 3.14),
             ("face", 1, 2),
             ("say", 1, "Hear it? Something is chewing under there. The worms dig, and the cult shores the tunnel up behind them, so it holds "
                        "until they want it to open."),
             ("cast", 1, 31387, 2),
             ("say", 1, "Supports are only wood, $N, and wood is only time. A hundred years in a heartbeat."),
             ("wait", 1500),
             ("cast", 2, 46419, 0),
             ("despawn", 2),
             ("wait", 1500),
             ("face", 1, 255),
             ("say", 1, "There. Nothing will come out of these dunes now but sand."),
         ]),
    # WRM-047: Valiance Keep's new day, as it's turned in, at the general.
    dict(id=SCENE_KEEP_HOLDS, name="The Keep Holds: Arlos, Vurenn, and the road to Wintergarde", quest=THE_KEEP_HOLDS, trigger=2, anchor=ARLOS,
         steps=[
             ("bind", 1, ARLOS),
             ("bind", 2, VURENN),
             ("face", 1, 255),
             ("say", 1, "I remember pieces of it. His voice in my ear every morning, telling me what I thought. Light help me, I signed "
                        "whatever he put in front of me."),
             ("say", 1, "Unit S. Thassarian and a dozen good men, sent to die under my seal. I will carry that for the rest of my life."),
             ("face", 1, 2),
             ("say", 1, "Harbinger. Your offer of two regiments. Is it still open?"),
             ("face", 2, 1),
             ("say", 2, "It never closed, general. I was only waiting to hear you answer in your own words."),
             ("say", 1, "Then the Valiance Expedition accepts, with the gratitude it should have shown you from the start."),
             ("face", 1, 255),
             ("say", 1, "And you, $N. High Commander Wyrmbane is holding Wintergarde Keep, and he needs every blade I can send him. Go to "
                        "him. Tell him Valiance Keep holds."),
         ]),
]

WORDS = [
    # Enlistment Day
    (ENLISTMENT_DAY, TAKEN, ALLIANCE, "He has heard about Outland. Best not to mention the rest; he has nowhere to write it down."),
    (ENLISTMENT_DAY, TURNED_IN, ALLIANCE, "Look at the general's eyes when his counselor speaks. I will tell you why when no one is "
                                          "listening.", dict(delay=5000)),
    # A Word in the General's Ear
    (WORD_IN_THE_EAR, TAKEN, ALLIANCE, "Scouts, $N. Not visions, not dreams, and certainly not 'a dragon told me'."),
    (WORD_IN_THE_EAR, DONE, ALLIANCE, "Did you see him look at his counselor before he answered you? Every day he looks a little sooner."),
    # A Time for Heroes
    (A_TIME_FOR_HEROES, TAKEN, ALLIANCE, "The keep does not fall, as it happens. It only comes close, three times. Let us make it two."),
    (A_TIME_FOR_HEROES, TURNED_IN, ALLIANCE, "Wasn't her, she says. She lies worse than you do, $N."),
    # The Siege
    (THE_SIEGE, TAKEN, ALLIANCE, "Crypt crawlers. They were nerubians once, citizens of Azjol-Nerub, until the Lich King took their kingdom "
                                 "and kept its dead. Be quick with them. It is the only mercy anyone can give them now."),
    (THE_SIEGE, TURNED_IN, ALLIANCE, "Twenty years, and he has never seen a day like it. He will call it luck. Soldiers always do."),
    # Death From Above
    (DEATH_FROM_ABOVE, TAKEN, ALLIANCE, "Fishing nets, against flying nerubians. It should not work. It does, and I have never understood "
                                        "why."),
    (DEATH_FROM_ABOVE, TURNED_IN, ALLIANCE, "He wants them to come by sea next, for the beating of their lives. I have given up arguing with "
                                            "dwarves about details."),
    # Plug the Sinkholes
    (PLUG_THE_SINKHOLES, TAKEN, ALLIANCE, "Two sinkholes in Hammerhill's orders. Three in Eternus's notes. Four in the ground. Collapse his "
                                          "two and report to him; leave the rest to us."),
    (PLUG_THE_SINKHOLES, DONE, ALLIANCE, "Those cultists chanting by the northern sinkhole: mark where they stand. We will be back for them."),
    # The Fourth Sinkhole
    (FOURTH_SINKHOLE, TAKEN, ALLIANCE, "The necrolytes first. I have always wondered who they think is listening."),
    # A Kindness Out of Time / Word at the Gate / Word on the Street
    (WORD_AT_THE_GATE, TURNED_IN, ALLIANCE, "Of everyone in this keep, she is the one I most wanted to meet."),
    (WORD_ON_THE_STREET, TURNED_IN, ALLIANCE, "Before she asks you anything: a word with me, $N. Now, please."),
    # Not Yet Late
    (NOT_YET_LATE, TAKEN, ALLIANCE, "Go on. She is waiting, and so is William."),
    (NOT_YET_LATE, DONE, ALLIANCE, "Alive. I was not at all sure we would be in time."),
    (THASSARIAN_MY_BROTHER, TAKEN, ALLIANCE, "The mine is north of the keep, past the Farshire fields. Run, $N."),
    # Named for No Town
    (NAMED_FOR_NO_TOWN, TAKEN, ALLIANCE, "Colburn will want a bottle of Kul Tiras wine before he talks. Ask him anyway. It has been years since "
                                         "anyone wanted to hear what he knows."),
    (NAMED_FOR_NO_TOWN, DONE, ALLIANCE, "The counselor's hand. I know what you want to do, $N, and you cannot. If he falls in this keep, he "
                                        "does not fall where history needs him to."),
    # A Useful Omission
    (A_USEFUL_OMISSION, TAKEN, ALLIANCE, "Venn's men have not heard a friendly voice since they landed. They will be glad of yours."),
    # No One Left Behind
    (NO_ONE_LEFT_BEHIND, TAKEN, ALLIANCE, "They have been kneeling in the cold for days. Do not expect them to run."),
    (NO_ONE_LEFT_BEHIND, DONE, ALLIANCE, "Four. History said none. Let it argue."),
    # Thassarian, the Death Knight
    (THASSARIAN_THE_DEATH_KNIGHT, TAKEN, ALLIANCE, "When the Scarlet Crusade took Koltira Deathweaver, Orbaz would have left him to them. "
                                                   "Thassarian would not: 'In death we are brothers.' Now think what he will do for his "
                                                   "sister."),
    (THASSARIAN_THE_DEATH_KNIGHT, TURNED_IN, ALLIANCE, "He has not seen her in years. Give him a moment, and then talk to me."),
    # Before She Gets Hurt
    (BEFORE_SHE_GETS_HURT, TAKEN, ALLIANCE, "Leryssa first; the vindicator is at the far end of the inn. Hold on."),
    # Finding the Phylactery
    (FINDING_THE_PHYLACTERY, TAKEN, ALLIANCE, "A lich who hides his soul in the ice and thinks no one will look. Liches are so predictable."),
    # Buying Some Time
    (BUYING_SOME_TIME, TAKEN, ALLIANCE, "Hammerhill's volunteers are holding the ziggurat while you are away. Thassarian would rather not find "
                                        "out whether he could hold it alone. Now he never has to."),
    # Words of Power
    (WORDS_OF_POWER, TAKEN, ALLIANCE, "I know all three words, and you will still have to fetch the scrolls. Thassarian would want to know "
                                      "where you learned them."),
    # Last Rites
    (LAST_RITES, TAKEN, ALLIANCE, "Leryssa is gone from the inn. The general's own escort came for her under his seal, and she went with "
                                  "them like a sleepwalker; Yaala could not hold a woman who wanted to go. I am sorry, $N. Some threads are "
                                  "knots."),
    (LAST_RITES, TURNED_IN, ALLIANCE, "He knelt up there with his offerings, the general and Leryssa, and that is the only reason anyone ever "
                                      "saw the face under Talbot's. History needed her on that tower. I hate that it held."),
    (LAST_RITES, TURNED_IN, ALLIANCE, "He will be back, you know. In the Citadel, at the very end, with the other princes: 'Naxxanar was "
                                      "merely a setback.' You will enjoy proving him wrong a second time.", dict(delay=9000)),
    # The Keep Holds
    (THE_KEEP_HOLDS, TURNED_IN, ALLIANCE, "Two regiments of draenei, a general who thinks his own thoughts, and four of Unit S who will see "
                                          "their mothers again. I have kept the record of this week for a very long time, $N. I like this "
                                          "version better.", dict(delay=60000)),
]
