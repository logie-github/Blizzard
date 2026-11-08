"""The Horde's Borean Tundra, while Moratari and Eternus steer the war (STORY.md, "Moratari in the war";
tools/story.py writes it).

Before the turn, Moratari walks with the Timerunner through the whole tundra and acts on what she
knows, quietly. The interventions, in the order the chain meets them:

- WRM-050 Beneath the Floor: warn Garrosh, Saurfang and the Warsong Captain that the nerubians will
  come up through the floor and down out of the sky. Garrosh scoffs; Saurfang listens, and hears a
  name from the east (Kel'Thuzad: "So it's true", Garrosh will say at the Plains of Nasam).
- WRM-051 Hands for Holgoth: Saurfang's promised hands, and the game's own Patience is a Virtue and
  Bury Those Cockroaches! put on the road: the four sinkholes under the quarry collapsed early.
- Mobu's parts: the game's own two quests, back on the road (WRM-016 no longer skips them), with
  Moratari knowing exactly where they are; two more tanks patched from the spare plates.
- WRM-054 The Condemned Coast: the Kvaldir driven off the landing, and a garrison Gorge asks
  Saurfang for, on the coast Hellscream condemned.
- The Plains of Nasam: every tank that will run rolls out together, and the wounded come home.
- WRM-056 Shipping Lanes: the chapter's new end: the argument Garrosh and Saurfang have every few
  minutes at the war map, settled the other way, for once.

After the turn, story_undo.py lets the record take its own back (the garrison and the spare tanks
recalled under the Warchief's martial law; Garrosh's lesson broken at his son's armour).
"""
from story_common import (HORDE, TAKEN, DONE, TURNED_IN, ZONE_BOREAN_TUNDRA, INTO_THE_DRAGONBLIGHT_H,
                          rewarded, not_rewarded)

# The game's people
GARROSH, SAURFANG, CAPTAIN, RAZGOR, HOLGOTH, GORGE, MOBU = 25237, 25256, 25446, 25279, 25327, 25329, 25475
KVALDIR_MIST_LORD = 25496

# The game's quests on the way
HELLSCREAMS_VIGIL, HELLSCREAMS_VIGIL_2 = 11585, 11586
DEFENSE_OF_WARSONG_HOLD = 11596
TAKING_BACK_MIGHTSTONE, CUTTING_OFF_THE_SOURCE = 11598, 11602
PATIENCE, BURY_THOSE_COCKROACHES = 11606, 11608
KINDNESS_H, WIND_MASTER, MAGIC_CARPET_RIDE = 77018, 11634, 11636
TANK_AINT_GONNA_FIX_ITSELF, TRANSJIGAMARIG, METAL_PLATES, TANKS_A_LOT, PLAINS_OF_NASAM = 11642, 11643, 11644, 11651, 11652
DARKNESS_STIRS, HERALD_OF_WAR = 13242, 13257

# This file's quests
BENEATH_THE_FLOOR, HANDS_FOR_HOLGOTH, THE_CONDEMNED_COAST, SHIPPING_LANES = 77050, 77051, 77054, 77056
RECORD_KEEPS_WARSONG = 77230   # the undoing (story_undo.py)

# Credits and new creatures
C_GARROSH, C_SAURFANG, C_CAPTAIN, C_GORGE = 770560, 770561, 770562, 770563
SINKHOLE_GUARD, COAST_GUARD, SPARE_TANK, RECOVERING_WARRIOR, RECOVERING_MAGE, SCENE_TANK = 770570, 770571, 770572, 770573, 770574, 770575

SCENE_TANKS_ROLL, SCENE_SHIPPING_LANES = 150, 151

CREATURES = [
    dict(entry=C_GARROSH, name="Garrosh Hellscream warned", credit=True),
    dict(entry=C_SAURFANG, name="High Overlord Saurfang warned", credit=True),
    dict(entry=C_CAPTAIN, name="The Warsong Captain warned", credit=True),
    dict(entry=C_GORGE, name="Gorge asked to hold the coast", credit=True),
    dict(entry=SINKHOLE_GUARD, **{"from": 25242}, name="Warsong Sapper", subname=None, unit_flags=770,
         why="Grunts on the collapsed sinkholes of Mightstone Quarry (the hands Saurfang sent)"),
    dict(entry=COAST_GUARD, **{"from": 25242}, name="Warsong Coast Guard", subname=None, unit_flags=770,
         why="The garrison on the condemned coast (WRM-054)"),
    dict(entry=SPARE_TANK, **{"from": 27103}, name="Horde Siege Tank", subname=None, unit_flags=770,
         why="Two more tanks, patched from Mobu's spare plates"),
    dict(entry=RECOVERING_WARRIOR, **{"from": 27106}, name="Recovering Warsong Warrior", unit_flags=770, stand=1, emote=0,
         why="The Plains of Nasam's wounded, brought home"),
    dict(entry=RECOVERING_MAGE, **{"from": 27107}, name="Recovering Warsong Mage", unit_flags=770, stand=1, emote=0,
         why="The Plains of Nasam's wounded, brought home"),
    dict(entry=SCENE_TANK, **{"from": 27103}, name="Horde Siege Tank", subname=None, unit_flags=770,
         why="The tanks rolling out together in The Plains of Nasam's scene"),
]

UNTIL_RECALLED = not_rewarded(RECORD_KEEPS_WARSONG)
SPAWNS = [
    # The sinkholes, collapsed early, with a sapper on each.
    dict(guid=7704360, entry=SINKHOLE_GUARD, x=2660.5, y=6175.0, z=39.0, o=3.90, visible=[[rewarded(BURY_THOSE_COCKROACHES)]],
         why="a sapper on the southern sinkhole, Mightstone Quarry"),
    dict(guid=7704361, entry=SINKHOLE_GUARD, x=2719.5, y=6024.5, z=31.3, o=3.90, visible=[[rewarded(BURY_THOSE_COCKROACHES)]],
         why="a sapper on the eastern sinkhole, Mightstone Quarry"),
    dict(guid=7704362, entry=SINKHOLE_GUARD, x=2881.5, y=6279.5, z=60.9, o=3.90, visible=[[rewarded(BURY_THOSE_COCKROACHES)]],
         why="a sapper on the western sinkhole, Mightstone Quarry"),
    dict(guid=7704363, entry=SINKHOLE_GUARD, x=2965.5, y=6191.0, z=62.1, o=3.90, visible=[[rewarded(BURY_THOSE_COCKROACHES)]],
         why="a sapper on the northern sinkhole, Mightstone Quarry"),
    # The coast: two more tanks, a garrison, the wounded.
    dict(guid=7704364, equip=0, entry=SPARE_TANK, x=2795.0, y=6747.0, z=7.6, o=5.80, visible=[[rewarded(TANKS_A_LOT), UNTIL_RECALLED]],
         why="a spare tank, the Coast of Echoes"),
    dict(guid=7704365, equip=0, entry=SPARE_TANK, x=2782.5, y=6757.0, z=7.6, o=5.80, visible=[[rewarded(TANKS_A_LOT), UNTIL_RECALLED]],
         why="a spare tank, the Coast of Echoes"),
    dict(guid=7704366, entry=COAST_GUARD, x=2826.0, y=6705.0, z=10.8, o=2.70, visible=[[rewarded(THE_CONDEMNED_COAST), UNTIL_RECALLED]],
         why="the coast's garrison, the Coast of Echoes"),
    dict(guid=7704367, entry=COAST_GUARD, x=2829.0, y=6716.0, z=10.8, o=2.70, visible=[[rewarded(THE_CONDEMNED_COAST), UNTIL_RECALLED]],
         why="the coast's garrison, the Coast of Echoes"),
    dict(guid=7704368, entry=COAST_GUARD, x=2823.0, y=6722.0, z=10.5, o=2.40, visible=[[rewarded(THE_CONDEMNED_COAST), UNTIL_RECALLED]],
         why="the coast's garrison, the Coast of Echoes"),
    dict(guid=7704369, entry=RECOVERING_WARRIOR, x=2812.0, y=6740.0, z=9.8, o=4.70, visible=[[rewarded(PLAINS_OF_NASAM), UNTIL_RECALLED]],
         why="the plains' wounded, recovering by Elder Mootoo"),
    dict(guid=7704370, entry=RECOVERING_MAGE, x=2815.2, y=6737.2, z=10.0, o=4.20, visible=[[rewarded(PLAINS_OF_NASAM), UNTIL_RECALLED]],
         why="the plains' wounded, recovering by Elder Mootoo"),
    dict(guid=7704371, entry=RECOVERING_WARRIOR, x=2809.2, y=6736.2, z=9.8, o=5.20, visible=[[rewarded(PLAINS_OF_NASAM), UNTIL_RECALLED]],
         why="the plains' wounded, recovering by Elder Mootoo"),
]

COMMON = dict(side=HORDE, sort=ZONE_BOREAN_TUNDRA, level=-1, min=10, bronze=800)

QUESTS = [
    dict(COMMON, id=BENEATH_THE_FLOOR, title="Beneath the Floor",
         gates=[[rewarded(HELLSCREAMS_VIGIL)], [rewarded(HELLSCREAMS_VIGIL_2)]],
         log="Warn Garrosh Hellscream, High Overlord Saurfang and the Warsong Captain on the south wall of what is coming to Warsong "
             "Hold, without telling them how you know.",
         desc="You remember this hold's first week, $N: what came up through the floor of this 'impregnable fortress', and what dropped "
              "onto the south wall every hour after.$B$BThis time the Horde can be ready for both. Tell Garrosh; he will scoff. "
              "Tell Saurfang; he will listen, and tell no one he did. Tell the captain on the wall to put his marksmen up.$B$BBut not "
              "how you know. No one in this year can ever learn that. Say you have a bad feeling about the quarry. Orcs have gone to war "
              "on less.",
         done="Return to Moratari.",
         objectives=[(C_GARROSH, 1, "Garrosh Hellscream warned"), (C_SAURFANG, 1, "High Overlord Saurfang warned"),
                     (C_CAPTAIN, 1, "The Warsong Captain warned")],
         request="How did they take it?",
         reward="Hands for the quartermaster, eyes on the plains, and marksmen on the wall before the next attack. Not bad, for a bad "
                "feeling.$B$BSaurfang has work for you now. Go and see him."),
    dict(COMMON, id=HANDS_FOR_HOLGOTH, title="Hands for Holgoth", prev=TAKING_BACK_MIGHTSTONE, ender=HOLGOTH,
         log="Speak with Quartermaster Holgoth in Warsong Hold.",
         desc="Saurfang promised Holgoth hands by nightfall. Yours are the first to arrive.$B$BThe quartermaster's munitions are out in "
              "the quarry, and he has a plan for the nerubians' sinkholes. In the record, those sinkholes are still open when the floor "
              "gives way. Let us close them before it does.",
         done="Speak with Quartermaster Holgoth.",
         reward="The High Overlord sent you? <Holgoth scratches his chin.> Huh. First time anybody at that map's remembered this hold has a "
                "quartermaster.$B$BWell, you're here now. Let's not waste it."),
    dict(COMMON, id=THE_CONDEMNED_COAST, title="The Condemned Coast", prev=TANKS_A_LOT,
         log="Slay 6 Kvaldir Mist Lords in the mist over Garrosh's Landing, and ask Gorge to keep a garrison on the coast.",
         desc="This coast was condemned the day the mist came, and only Gorge, a goblin and six tanks stayed. When the tanks "
              "leave for the plains, the Kvaldir come out of the mist behind them, and there is no one left on this beach to stop "
              "them.$B$BThin the Mist Lords on the landing. Then tell Gorge to ask Saurfang for a garrison. Hellscream condemned the coast; "
              "he never said no one could guard it.",
         done="Return to Moratari.",
         objectives=[(KVALDIR_MIST_LORD, 6, ""), (C_GORGE, 1, "Gorge asked to hold the coast")],
         request="Is the landing quiet?",
         reward="Good. With a garrison on it, it will stay that way.$B$BNow think what a held beach is worth, $N, to an army whose ships "
                "have nowhere on this coast to land. Saurfang will. Give him a day."),
    dict(COMMON, id=SHIPPING_LANES, title="Shipping Lanes", prev=PLAINS_OF_NASAM, gates=[[rewarded(THE_CONDEMNED_COAST)]], ender=SAURFANG, bronze=1500,
         log="Speak with High Overlord Saurfang in Warsong Hold.",
         desc="Kel'Thuzad. You saw him over the plains with your own eyes, and Garrosh has had an hour to think about it, which for "
              "Garrosh is a long time. You can guess what he has decided.$B$BSaurfang will talk him out of it, barely. He always has. "
              "But today there is a garrison on Garrosh's Landing, and I think the argument may end differently.$B$BCome, $N. I would not "
              "miss this one.",
         done="Speak with High Overlord Saurfang.",
         reward="<High Overlord Saurfang glances at Hellscream across the war map.>$B$BYou brought him that name, $N. Stay, and hear what "
                "he means to do with it."),
]

GATES = {
    # The Defense of Warsong Hold (the variant a new character gets): the game's own conditions, and
    # the warning first.
    DEFENSE_OF_WARSONG_HOLD: [[rewarded(7784, 1), rewarded(8743, 1), rewarded(BENEATH_THE_FLOOR)]],
    KINDNESS_H: [[rewarded(BURY_THOSE_COCKROACHES)]],
    PATIENCE: [[rewarded(HANDS_FOR_HOLGOTH)]],
    INTO_THE_DRAGONBLIGHT_H: [[rewarded(SHIPPING_LANES)]],
}

TEXTS = {
    BURY_THOSE_COCKROACHES: dict(
        reward="That'll stop 'em - at least I think it'll stop 'em. Either way, you've done your part. That's all an $r can ask for, no?$B$B"
               "And the High Overlord's sending sappers out to sit on every one of those holes, in case anything tries digging back up. "
               "Somebody's been talking in his ear."),
    TRANSJIGAMARIG: dict(
        reward="Already? Buddy, I been starin' at that hut since the mist rolled in, tryin' to work up the nerve! You just walked in there "
               "an' back out like it was nothin'.$B$BNow where'd I put those spare parts..."),
    TANKS_A_LOT: dict(
        reward="With the current state of our transports and shipping lanes, we haven't been able to get a damned siege engine to Warsong. "
               "These tanks are all that we have left from the original expedition. Now that they're operational, you're gonna use 'em to "
               "stomp the Scourge offensive at the Plains of Nasam.$B$BAn' Mobu says there's plates left over to patch up two more. Two more "
               "tanks! Maybe I won't cleave the little gnome in two after all."),
    PLAINS_OF_NASAM: dict(
        desc="Once you're ready, jump into one of the tanks and drive it out to the Plains of Nasam, southeast of here.$B$BUse the tank's "
             "weapon arsenal to take down the Scourge army. If you get in a jam, the \"Meatpounder\" will tear 'em up and the land mines "
             "will finish 'em off! If you find any of our soldiers, grab 'em and bring 'em back here! One last thing, fuel tanks can be "
             "found all over the field.$B$BTry to get close enough to that structure in the center and see what's going on.$B$BIf you do "
             "all of this and live, go to Hellscream!"),
}

TALK = [
    # WRM-050
    dict(npc=GARROSH, quest=BENEATH_THE_FLOOR, credit=C_GARROSH,
         option="The nerubians are under the floor, Overlord. When they come, they'll come from below and above at once.",
         reply="Under my floor? <Garrosh sniffs.> Then they will find my boot waiting for them.$B$BI smelled your fear the moment you walked "
               "in, $r. Keep it out of my hold. The Warsong does not cower before insects."),
    dict(npc=GARROSH, quest=BENEATH_THE_FLOOR,
         option="And the cultists out west serve a lich. Kel'Thuzad. I'd stake my life on it.",
         reply="Kel'Thuzad? That lich was destroyed in the Plaguelands. <Garrosh spits.> I do not fight ghost stories, $r. I fight what "
               "bleeds."),
    dict(npc=SAURFANG, quest=BENEATH_THE_FLOOR, credit=C_SAURFANG,
         option="High Overlord, the nerubians will come up through the floor of the hold. The quarry is riddled with their tunnels.",
         reply="<Saurfang studies you for a long moment.>$B$BRazgor tells me the quarry is soft. Holgoth tells me he has charges and no one "
               "to carry them. And now you.$B$BHolgoth will have his hands by nightfall.$B$B<Saurfang looks west, toward the plains.>$B$B"
               "There are necromancers out there in the robes of the Cult of the Damned. Where the Cult goes, plague is never far behind. I "
               "will put scouts on the plains.$B$BWhat I have told you stays between us. Hellscream has enough to shout about."),
    dict(npc=CAPTAIN, quest=BENEATH_THE_FLOOR, credit=C_CAPTAIN,
         option="Captain, they'll come over the south wall, and out of the sky. Put your marksmen up.",
         reply="Settle down, soldier!$B$B<The captain looks up at the sky, then back at you.>$B$BWe'll be ready for 'em... "
               "You did a good job in warning us."),
    # WRM-054
    dict(npc=GORGE, quest=THE_CONDEMNED_COAST, credit=C_GORGE,
         option="Gorge, keep a garrison on this coast once the tanks roll out. The Kvaldir will be back the moment the beach is empty. Ask "
                "Saurfang for the men; he'll send them.",
         reply="A garrison? Here? Hellscream condemned this coast, an' everybody on it!$B$B<Gorge chews on that.>$B$B...But Saurfang ain't "
               "Hellscream. An' I ain't sendin' my tanks out to the plains so them mist-men can walk in behind 'em.$B$BI'll send a runner to "
               "the hold. An' if anybody asks, it was my idea."),
]

# The captain stands where Ith'rix the Harvester's flight comes down on the hold (the game's own assault,
# What the Cold Wind Brings..., half of every hour); at the chapter's levels it killed him every few
# minutes, and an elite lies dead for seven.
SPARED = [
    (CAPTAIN, "Beneath the Floor sends the Timerunner to warn him, on the south wall"),
]

SCENES = [
    # The Plains of Nasam, as it's taken: every tank that will run rolls out with the Timerunner.
    dict(id=SCENE_TANKS_ROLL, name="The Plains of Nasam: the tanks roll out together", quest=PLAINS_OF_NASAM, trigger=1, anchor=GORGE,
         steps=[
             ("bind", 1, GORGE),
             ("summon", 2, SCENE_TANK, -6.0, 8.0, 2.4),
             ("summon", 3, SCENE_TANK, -9.0, 4.0, 2.4),
             ("summon", 4, SCENE_TANK, -12.0, 9.0, 2.4),
             ("yell", 1, "Every tank that runs, rolls! NO MERCY FOR THE DEAD!"),
             ("move", 2, -60.0, 70.0, 1),
             ("move", 3, -64.0, 64.0, 1),
             ("move", 4, -68.0, 72.0, 1),
             ("say", 1, "An' I want every one of 'em back in one piece! Those are my tanks!"),
             ("wait", 6000),
             ("despawn", 2),
             ("despawn", 3),
             ("despawn", 4),
         ]),
    # Shipping Lanes, as it's turned in: the argument at the war map, settled the other way.
    dict(id=SCENE_SHIPPING_LANES, name="Shipping Lanes: Garrosh and Saurfang at the war map", quest=SHIPPING_LANES, trigger=2, anchor=SAURFANG,
         steps=[
             ("bind", 1, GARROSH),
             ("bind", 2, SAURFANG),
             ("face", 1, 2),
             ("say", 1, "Kel'Thuzad lives, and Naxxramas with him. We have waited long enough. We march on Icecrown tonight."),
             ("face", 2, 1),
             ("say", 2, "With what, young Hellscream? Every blade and barrel we own still comes from the far side of this blasted continent. "
                        "Until we have a port on this coast, we march nowhere."),
             ("say", 1, "Shipping lanes... supplies... You still bore me to death, old one."),
             ("say", 2, "And you are still alive to be bored."),
             ("wait", 1500),
             ("say", 1, "...Show me this port of yours."),
             ("say", 2, "Garrosh's Landing. The coast you condemned. Gorge holds it now, with men I sent him."),
             ("say", 1, "Then it is not condemned. There. Now we have a shipping lane."),
         ]),
]

WORDS = [
    (HELLSCREAMS_VIGIL, TAKEN, HORDE, "Garrosh holds court at the war map, in the heart of the hold. Do not expect him to welcome you."),
    (HELLSCREAMS_VIGIL, TURNED_IN, HORDE, "He and Saurfang have the same argument at that map every few minutes: shipping lanes, supplies, "
                                          "and then Garrosh's boot comes down. I could recite it for you.", dict(delay=6000)),
    (BENEATH_THE_FLOOR, TAKEN, HORDE, "Garrosh and Saurfang first. Then the captain, up on the battlements of the south wall."),
    (BENEATH_THE_FLOOR, DONE, HORDE, "That is all three. I wonder which of them will still remember your face when this war is over."),
    (DEFENSE_OF_WARSONG_HOLD, TAKEN, HORDE, "Saurfang drank the same blood Grom did, and lived to remember everything it made him do. "
                                            "Garrosh only knows the songs."),
    (TAKING_BACK_MIGHTSTONE, TAKEN, HORDE, "Some of the cocoons in the quarry hold Warsong soldiers, still alive. Cut them free and they "
                                           "will fight beside you."),
    (TAKING_BACK_MIGHTSTONE, TURNED_IN, HORDE, "Razgor is right: more will come. Next time, from underneath."),
    (HANDS_FOR_HOLGOTH, TAKEN, HORDE, "Holgoth is a few steps away, past Razgor's hut."),
    (PATIENCE, TAKEN, HORDE, "The crates are scattered across the quarry floor. Gather them quickly; the nerubians will not leave you "
                             "alone down there for long."),
    (BURY_THOSE_COCKROACHES, TAKEN, HORDE, "When the last charge goes off, listen. You will hear the tunnels collapse, all the way back "
                                           "under the hold."),
    (BURY_THOSE_COCKROACHES, TURNED_IN, HORDE, "In your war, the nerubians were inside the hold by now. Tonight it sleeps on solid stone, "
                                               "and will never know how close it came."),
    (CUTTING_OFF_THE_SOURCE, TAKEN, HORDE, "Twenty to an egg, Razgor says. I counted once. He is being modest."),
    (WIND_MASTER, TAKEN, HORDE, "From the top of the hold you can see what Razgor keeps pointing at."),
    (MAGIC_CARPET_RIDE, TAKEN, HORDE, "Yanni will quote you his odds. Pay them no mind. I will be at the coast when you land."),
    (TANK_AINT_GONNA_FIX_ITSELF, TAKEN, HORDE, "Mobu is down by the tanks. Be gentle with him; he has wanted to go home since the day he "
                                               "got here."),
    (TANK_AINT_GONNA_FIX_ITSELF, TURNED_IN, HORDE, "He is about to send you for a transjigamarig and ten metal plates. I know where every "
                                                   "one of them is. Come, we can be back before he has finished complaining.",
     dict(delay=4000)),
    (TRANSJIGAMARIG, TAKEN, HORDE, "Into the mist, then. Take heart: the Kvaldir see no better in it than you do."),
    (TANKS_A_LOT, TURNED_IN, HORDE, "Before the tanks roll, $N, there is one more thing this beach needs."),
    (THE_CONDEMNED_COAST, TAKEN, HORDE, "The Mist Lords keep to the thickest of the mist, on the landing itself. As for Gorge, let him "
                                        "shout. He will come around."),
    (PLAINS_OF_NASAM, TAKEN, HORDE, "Three seats in that tank for the wounded. Fill them, $N. Whoever the Scourge reach first, they stitch "
                                    "into something else and send back at the Horde."),
    (PLAINS_OF_NASAM, TURNED_IN, HORDE, "'Underestimated.' From Garrosh Hellscream, that is very nearly an apology. Do not wait for a "
                                        "second one."),
    (SHIPPING_LANES, TAKEN, HORDE, "Saurfang is just there, at Garrosh's shoulder. Stand where he can see you."),
    (SHIPPING_LANES, TURNED_IN, HORDE, "All the other times I have heard him say that, his boot came down on the map. Remember this "
                                       "afternoon, $N. It does not last.",
     dict(delay=50000)),
]
