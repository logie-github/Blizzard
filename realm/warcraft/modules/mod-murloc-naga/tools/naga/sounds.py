# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's story's Warcraft III voices (the bible's 18.5): 82 unit lines of Lady Vashj, the naga
siren, myrmidon and royal guard, Illidan, Maiev, Kael'thas, Garithos, Akama, Tyrande, Malfurion, Arthas
as a death knight, a dreadlord and the pit lord, as 3.3.5 sounds: a SoundEntries row each in the
module's patch (tools/naga_assets.py), its file the WAV the server package makes
(tools/naga_voices.py: fetched, checked by its SHA-1, never in this repository).

    SOUNDS["LadyVashjReady1"]  -> 995000, the SoundEntries id a `sound` beat or creature_text plays

Without the files (the package couldn't fetch them) the rows are still there and the lines show as
text: the game plays nothing for a sound whose file isn't there.

The files are warcraft.wiki.gg's (https://warcraft.wiki.gg/images/<name>.wav), the same files (the
same SHA-1) as Wowpedia's (static.wikia.nocookie.net/wowpedia/images/...): the package takes either.
The words are the wiki's Quotes of Warcraft III pages' (Neutral Heroes, Neutral, Night Elf
Sentinels, Human Alliance, Undead Scourge), each beside its file there.
"""

FIRST_ID = 995000                 # SoundEntries: the module's range for them, 995000 to 995199
LAST_ID = 995199
DIRECTORY = "Sound\\Creature\\WC3Voices"    # where the patch puts the WAVs (the game's path, backslashes)
MANIFEST = "nagavoices.files"     # the package's list of them, written last (tools/naga_voices.py)

# (name, the file's SHA-1 and size on the wiki, seconds, the words); the order gives the ids.
VOICES = [
    # Lady Vashj (the Naga Sea Witch's voice; Warcraft III gave every sea witch hero hers)
    ("LadyVashjReady1", "72e16c15d61331a60c7fed277f29d734597fb2fe", 58504, 1.32, "I stand ready."),
    ("LadyVashjWhat1", "3f061cba7dfbd40cc8d5d3c8af55fc09473296ec", 41992, 0.95, "Is it time?"),
    ("LadyVashjWhat2", "ec5821fd3511bf38c2d060f26f96818521fa1efc", 93960, 2.13, "I grow anxious to act."),
    ("LadyVashjWhat3", "e3fb6d53fbc7f72b051afaebd1bfac2844c31048", 90504, 2.05, "Our will shall be done."),
    ("LadyVashjWhat4", "6944fb65ebaab377ec417e947fc3e097647d3d23", 104968, 2.38, "I will not be trifled with."),
    ("LadyVashjWhat5", "cdca9df73262881b9b779531f03626afe6c09f1e", 85128, 1.93, "Time is short, mortal."),
    ("LadyVashjYes1", "07dad4a40a52b229e5c30165bed49ddeb48e257a", 75530, 1.71, "By your command."),
    ("LadyVashjYes2", "f8a81e7d0f1d1e4c74efdfdd28056db90cacc7a7", 50824, 1.15, "Yes."),
    ("LadyVashjYes3", "a3fcb265c69d8a839b9b0f21ad30dc52bbc891f8", 52104, 1.18, "Brilliant."),
    ("LadyVashjYes4", "bd549dd8729decf995cb68d0ac12dcfb2e9d6e90", 68872, 1.56, "(serpentine shriek)"),
    ("LadyVashjYes5", "58caef2f3f0284448cd8bd704e02a1efdfe35357", 69898, 1.58, "In Azshara's name."),
    ("LadyVashjYes6", "68bedebd6f688d4aca0e2ccc9d79f155eeefcd2e", 66696, 1.51, "For the empress."),
    ("LadyVashjYesAttack1", "f48ef515819d291e648f4bc069ba536a396bdbdc", 83720, 1.90, "For Nazjatar!"),
    ("LadyVashjYesAttack2", "78fbca5d9d25fd4de61a0899c73f2c5ab12c0be0", 87304, 1.98, "Taste my sting!"),
    ("LadyVashjYesAttack3", "fffe413c193ff0fc74dde599d43ddc84365fef89", 72456, 1.64, "Era'sazjar!"),
    ("LadyVashjWarcry1", "41503faaefb8146450cbc258210707b7353b3ac0", 72968, 1.65, "Athero bath'rilas!"),
    ("LadyVashjPissed1", "6d6b3a1aeebca7adc79be92b4076a5cc2f3e3acb", 285448, 6.47,
     "Soon, we will reclaim the surface world, and take vengeance upon the night elves!"),
    ("LadyVashjPissed2", "65e64cadf57af9a5357b25d028db11a986f9eeaf", 134568, 3.05, "Illidan will show us the path to power!"),
    ("LadyVashjPissed3", "ba3e6662e4201e6904354cece4dfa4268353b6fd", 121608, 2.75, "Keep tripping over this damn tail!"),
    ("LadyVashjPissed4", "49fb4699913aa2f5fb8276d32ddff5533dd599af", 159880, 3.62,
     "Damn sea water! I'll never get these coils out of my hair!"),
    ("LadyVashjPissed5", "33c7bd93baf92a49190ae885c5ef64194f4773c1", 250888, 5.69,
     "It's far too bright in this surface world, and this... (sniff) fresh air is irritating my eyes!"),
    # The naga siren
    ("NagaSirenReady1", "98603ef2fcf6b75d0ae3725029a8ca2426e85dff", 126728, 2.87, "My song echoes from the deeps."),
    ("NagaSirenWhat2", "875e702adf773fb5cf6fb3b5ae2c8ec2cd0648ed", 47560, 1.08, "Don't be afraid."),
    ("NagaSirenWhat4", "753d560e420f15d62a4420f07b47439730a45ae7", 49738, 1.12, "Hey, sailor."),
    ("NagaSirenYes1", "092f0193d14e3fa95d8491681c3ef7abe387a9ca", 73480, 1.66, "By land or sea."),
    ("NagaSirenYes3", "f66460dd0f63e989e43e34946986bc760669b580", 49800, 1.13, "Ash'valana thure."),
    ("NagaSirenYesAttack1", "0767efb22927b87a7a468309db6977b158b8bb41", 105768, 2.40, "The tide turns."),
    ("NagaSirenPissed1", "bcd52276365975ef5d7b8232519ce34dcf6ad306", 158728, 3.60, "I'll sing a requiem for the land-walkers."),
    ("NagaSirenPissed4", "62a84b4f255b0896dfc9904c489448b100281ea3", 74212, 1.68, "Do you find me alluring?"),
    # The naga myrmidon (the wiki's files spell it "Myrmadon")
    ("NagaMyrmadonReady1", "11f70b6322e79d4cfc07ac01d0e3f3bc86207214", 119302, 2.70, "From the murky depths I come."),
    ("NagaMyrmadonYes3", "3bddb499f2907c47aa8b9bfc1eb32491abfad539", 104454, 2.37, "Our alliance binds me."),
    ("NagaMyrmadonYes4", "2ea2519db51ec966171ccf0481e4dbd575a22e1d", 98566, 2.23, "I will honor our pact."),
    ("NagaMyrmadonWarcry1", "cc8c7c63ebe2966586cead5fd913de18775af110", 91910, 2.08, "For Nazjatar!"),
    ("NagaMyrmadonPissed1", "36fabb9efaeb03aae6b98b25cded09ee524075fc", 219912, 4.98, "After ten thousand years, our revenge... is at hand."),
    ("NagaMyrmadonPissed2", "8dcf7e9c941269ff0531336b83508c4303683bb5", 137030, 3.10, "I think I just slithered in something."),
    ("NagaMyrmadonPissed3", "21419a19d85a13fb1e7818a4930a14ceca574ff8", 136712, 3.10, "I can't smell... I bit my tongue."),
    ("NagaMyrmadonPissed4", "ea499a222005dab73de2bd9c70ff18632073f172", 109830, 2.49, "COOOOBRAAAAAAAA!"),
    ("NagaMyrmadonPissed5", "5b4059767c4fbce4bb53552ee97f559e109937b3", 357254, 8.10, "Ack... going... into... tor... por... (snores)"),
    ("NagaMyrmadonPissed6", "ca219f07753a94cd9f4c446dc8c4c8e0a44687c9", 340486, 7.72, "Ooohhh, it's kind of cold... in... (snores)"),
    ("NagaMyrmadonPissed7", "3b4ca5a6fa3a3f3d1f88950a42dc3103be44a133", 360070, 8.16,
     "My next plan for world domination is... (snores) snkthkch ...my hair!!!"),
    # The naga royal guard
    ("NagaRoyalGuardReady1", "dc76fb06036cdcf62cd846758b598ce1618f751e", 173064, 3.92, "I come to you now, at the turn of the tide."),
    ("NagaRoyalGuardYes3", "b120379b1919129d2556fd0a974ded24c7409c9b", 91656, 2.08, "Our alliance binds me."),
    ("NagaRoyalGuardYesAttack1", "af8a62f1063b532ad6fb912f3f2408489c5ff382", 79112, 1.79, "Drown them all!"),
    ("NagaRoyalGuardYesAttack2", "a60443d63f7387e59193771d1d8600bceb41aec2", 85448, 1.93, "Land-born scum!"),
    ("NagaRoyalGuardPissed1", "d07158af0633468d7eb3c66b7ac018a4c4eef1e1", 99080, 2.24, "Our tide.. is rising."),
    ("NagaRoyalGuardPissed3", "930552047404949a741f3d5d4ef8208f180bd760", 104552, 2.37, "I think I have swimmer's ear."),
    ("NagaRoyalGuardPissed7", "7eb68f609e34189e19069bade081ca412171137d", 226312, 5.13, "The day of our invasion shall be known as B-Day."),
    # Illidan
    ("IllidanPissed1", "f726bcb359d04f5bcc623cbbe9864093a4270bcb", 120756, 2.74, "I have been caged in darkness."),
    ("IllidanPissed3", "db5e23952cddffba159bab244125305740b2504b", 156952, 3.56, "I've been alone for ten thousand years."),
    ("IllidanPissed4", "ecf6b6df49752ee6f201bd24dd65e94e38a2ecef", 168160, 3.81, "My brother will pay dearly for his betrayal."),
    ("IllidanPissed5", "764a1719b2cec73787bd106060ee5a875e46e83f", 107082, 2.43, "None of them know my true power!"),
    ("IllidanWhat1", "388d56d6e320c3d3f4767b388f8c3eb4ba1d2d8b", 71404, 1.62, "I'm blind, not deaf."),
    ("IllidanYes4", "2e2db5b026e033d7e80c8d45235e7df6abc70844", 89356, 2.02, "Evil draws close."),
    ("IllidanYesAttack1", "03f523faf57c1ea04fa791ad0fc597ec412ed506", 84168, 1.91, "Vengeance is mine."),
    ("IllidanMorphedWarcry1", "e6d9d5a5a6b6de0e7646bef7996a26e1acea7b96", 97654, 2.21, "None may challenge me!"),
    # Maiev Shadowsong
    ("MaievReady1", "a77b8da58dd51000eddf303d778efedd42b3abec", 111750, 2.53, "I am the hand of justice!"),
    ("MaievWarcry1", "14de45ec33fb727577dea6359ee7fed48592ede9", 70022, 1.58, "Tor ilisar'thera'nal!"),
    ("MaievPissed5", "83f19745e8cd91272097a62a62188b0f53f0e9d8", 156294, 3.54, "I will recapture Illidan, or die trying."),
    ("MaievYesAttack1", "c0c628ed9175b8c73ccebdf805bf0b2c6164dd7e", 45318, 1.02, "For the Watchers!"),
    # Kael'thas Sunstrider
    ("KaelYesAttack1", "4f359ad014d2727044bc805062c61a3ed1702db5", 59270, 1.34, "By fire be purged!"),
    ("KaelPissed2", "d9a88844cd8f1daa7b626bce527b8b7230f738db", 122694, 2.78, "My hunger for magic is clouding my judgment!"),
    ("KaelPissed4", "4baacf29ecbc2d527d538596cbf34d1d024e13e6", 122438, 2.77, "The Alliance has failed my people."),
    ("KaelYes2", "d0ccca9b1508c9296b7760d61b4c5c8df4147f45", 45318, 1.02, "Outstanding!"),
    ("KaelWarcry1", "2b9c546f57bea712b029a4ab380e6bc5abbbffdf", 66182, 1.50, "Endo-enah Quel'Thalas!"),
    # Grand Marshal Garithos
    ("GarithosWhat3", "ce5e43c6da9a44f85811e215cbad6951f77ee6ee", 118058, 2.67, "I hate working with these... people."),
    ("GarithosPissed5", "e071f47ef815c29c0fad72a96bbd881ac806857a", 66310, 1.50, "Never trust an elf!"),
    ("GarithosYesAttack3", "baf61ccff26bff3314792dea1cc2ec079aafe474", 53382, 1.21, "Inhuman beast!"),
    ("GarithosPissed2", "32554c5a595160d3b1d737070534f93d35abca8b", 181638, 4.12, "The lesser races must be purged from the kingdom."),
    ("GarithosWarcry1", "b26e098c2665d443b2282b614ff74aae4c1f1203", 68486, 1.55, "In memory of Terenas!"),
    ("GarithosReady1", "f08fa8b3f8d2eb817a1cb1d70c7f4811ec660ab4", 112262, 2.54, "Humanity will rise again!"),
    # Akama
    ("AkamaReady1", "c081346f05bddbd58213df5004e75e6643cf5127", 91014, 2.06, "I pledge my loyalty."),
    ("AkamaPissed6", "a2e6f7006d45142b62d228805d385015cab1fc71", 145030, 3.29, "I'm too old for this... urgh."),
    ("AkamaWarcry1", "be14683e60b3e1f35aa1dbeeb6df119ff3a8a43a", 68998, 1.56, "Strength and honor!"),
    # Tyrande Whisperwind, Malfurion Stormrage
    ("TyrandeWarcry1", "1005dfd3122cb286eedc8be59b4e4f4842eb4c19", 55688, 1.26, "Sentinels, attack!"),
    ("TyrandeYes2", "8082d5e4d58ce5cbb1dc99ec5f31e067b2b9776c", 56258, 1.27, "By Elune."),
    ("MalfurionPissed4", "f6ea424bd5d68a50c4492219b111a87d00eb2abc", 156040, 3.54, "Our sins have returned to haunt us."),
    ("MalfurionYesAttack2", "08c416f41a4ac4bc22262c7cdbe0f228745d9d8c", 85128, 1.93, "How dare you!"),
    # Arthas as a death knight, a dreadlord, the pit lord
    ("EvilArthasYes2", "01b92fcbc0c619636a2b96f80e9008d0f9dd5fe9", 70798, 1.58, "Frostmourne hungers."),
    ("EvilArthasWarcry1", "6d908d6aa465e2976fb8125c10a5b389a9982aa9", 85034, 1.93, "Glory to the Scourge!"),
    ("EvilArthasYesAttack6", "409d4ae14fcb5a2f0b3aa150ddd50328aeadb3b2", 60046, 1.34, "Now Frostmourne!"),
    ("HeroDreadlordWarcry1", "d5b42fac86cac6696006d28cb7662907e4f52081", 72080, 1.63, "Your soul is mine!"),
    ("PitLordYes2", "7d1285c99fcadaad1d70033264bf5e7644036443", 109998, 2.49, "Mekin Krenah."),
]

# The name the bible uses -> its SoundEntries id (the story compiler's sound-by-name beat reads this).
SOUNDS = {name: FIRST_ID + i for i, (name, _, _, _, _) in enumerate(VOICES)}
# The name -> its words (for the text the scene shows beside the sound).
WORDS = {name: words for name, _, _, _, words in VOICES}


def file_name(name):
    """The WAV's name in the patch's DIRECTORY and in the package's folder."""
    return name + ".wav"


def packaged_path(name):
    """Where the package puts the WAV (data/files/<this>), the patch's path with slashes."""
    return DIRECTORY.replace("\\", "/") + "/" + file_name(name)
