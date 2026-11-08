# SPDX-License-Identifier: GPL-3.0-or-later
"""The Last Customer: Ambrose Wicke, a Forsaken shopkeeper whose stall stands behind Brill's town hall
(east of it, on open ground clear of the town's own people and the tournament's "[DND] TAR Pedestal"
rows), won't sell a thing while an order placed before the plague is uncollected: a pair of silvered
candlesticks Tobias Balnir paid for, for his wedding to Marian Hale. The player cleans the stall, reads
the order, finds the Balnir Farmstead (south-east of Brill: the burnt farmhouse, the family plot and its
open grave) and the one Balnir left, Agnes, Tobias's sister: she was in service in Silverpine when the
plague came, died there later and rose, and now washes shrouds at the Sepulcher (a Horde town of levels
10 to 20, as the line is). Her letter leaves the candlesticks to the player: lit in Ambrose's window, or
sold to the next couple who'll have them. Ambrose opens the stall again (the phase "open": his goods out)
and sells odd, cheap things, cheerful and morbid about his new customers.
"""

# The stall's middle is (2345, 278), facing 2.7 (toward the town hall and the square); its heights are the
# terrain's (map tile 0002731).

LINE = {
    "title": "The Last Customer",
    "quests": [
        {
            "id": "business", "title": "Business as Usual", "giver": "ambrose", "ender": "ambrose",
            "log": "Clean the dust from Ambrose Wicke's stall behind Brill's town hall and find his old order ledger.",
            "offer": (
                "Closed. Can't you read the sign? Oh. The sign fell down. Years ago, I expect.$B$B"
                "Ambrose Wicke, candles, lamps and sundries, established in Brill before most of Brill was buried. "
                "I don't sell, $g lad:lass;. Not until an order is collected. A customer paid in full, and a shop that "
                "sells his goods out from under him is a shop that cheats. My father said that, and his father before him, "
                "and they were both a great deal warmer than I am now.$B$B"
                "But the dust. The dust I will admit to. I woke behind this counter after the plague and I have been "
                "standing at it since, and the moths have had the run of the place. Shake out the rug, clear the crate "
                "and the shelf, and look under the counter for my order ledger. Green binding. It has his name in it. "
                "I'd look myself, but I'm keeping shop."
            ),
            "progress": "The ledger, $n. Green binding. Under the counter. I'd know it by the smell if I still had one.",
            "done": (
                "There it is. The binding's gone grey, but then so have I.$B$B"
                "And the stall looks very nearly like a place someone might buy something. Not that they may. "
                "Take this for your trouble: it's payment, not a sale, and I'll thank you not to confuse the two."
            ),
            "return": "Return to Ambrose Wicke in Brill.",
            "objectives": [("credit", "dust_credit", 3, "Dusty corners cleaned"),
                           ("credit", "ledger_credit", 1, "Order ledger found")],
            "money": 600, "xp": 2, "min_level": 5,
        },
        {
            "id": "outstanding", "title": "An Outstanding Order", "giver": "ambrose", "ender": "ambrose",
            "prev": "business",
            "log": "Read the ledger's last entry with Ambrose Wicke, find the order wrapped at the back of his stall, "
                   "and ask Magistrate Sevren in Brill's town hall about the customer's family.",
            "offer": (
                "Now that you've found it, you may as well read it. My eyes aren't what they were, chiefly because "
                "one of them isn't anywhere.$B$B"
                "The last entry. Read it with me. He'll be here any day: he said so when he paid. Then look at the back "
                "of the stall, behind the shelf. His order is wrapped in brown paper and string, the way it's been waiting.$B$B"
                "And ask the Magistrate about the family. Sevren keeps the town's books now, such as they are. If the "
                "young man's moved house, the Magistrate will know where. People move. I did. Into the ground and out "
                "again, but it counts."
            ),
            "progress": "Has the Magistrate said where he's gone? People don't just stop coming for their orders.",
            "done": (
                "Quarantined. By the Crown.$B$B"
                "I remember the soldiers on the road. I remember thinking it was a great deal of fuss over grain.$B$B"
                "And the date. Eleven years. I'd have sworn it was last spring. You lose the count, standing still; the "
                "days don't come in and buy anything, so you don't notice them. Still. A farm doesn't move, $n. "
                "Someone there will know where he went."
            ),
            "return": "Return to Ambrose Wicke in Brill.",
            "objectives": [("credit", "entry_credit", 1, "The ledger's last entry read"),
                           ("credit", "parcel_credit", 1, "The wrapped order found"),
                           ("credit", "sevren_credit", 1, "Magistrate Sevren asked about the Balnirs")],
            "money": 800, "xp": 3, "min_level": 5,
        },
        {
            "id": "address", "title": "No Forwarding Address", "giver": "ambrose", "ender": "ambrose",
            "prev": "outstanding",
            "log": "Search the Balnir Farmstead, south-east of Brill, for what became of the Balnir family, then return "
                   "to Ambrose Wicke.",
            "offer": (
                "The Balnir Farmstead. South and east of here, past the crossroads, where the road bends toward the old "
                "Crusade tower. A good farm, once: Tobias's father grew snapdragons for the market, of all things, and "
                "brought me the wax from his bees.$B$B"
                "Go and see. There will be something. A notice on the gate, a family book in the house, the stones in the "
                "family plot; farmers write things down, and they bury their people where they can see them from the "
                "kitchen.$B$B"
                "Mind the farm. The Magistrate says nothing living goes there, and from his face I gather nothing dead "
                "goes there gladly either. Find out where Tobias went, $n. I don't ask you to bring him. Only to "
                "tell me where to send word."
            ),
            "progress": "Well? Is there a forwarding address? Even the dead leave forwarding addresses. I left one. It's here.",
            "done": (
                "Marian first, then Tobias, then the old man. And the grave open.$B$B"
                "...$B$B"
                "I sold Osric Balnir his wife's funeral candles, you know. Plain ones. He wouldn't take the good ones on "
                "credit, though I offered.$B$B"
                "But the girl. Agnes. Her name isn't crossed out. In service in Silverpine, the book says. If she lived, "
                "or if she did what I did and didn't stay dead, she is the order's next of kin."
            ),
            "return": "Return to Ambrose Wicke in Brill.",
            "objectives": [("credit", "clue_credit", 3, "Signs of the Balnirs' fate found")],
            "items": [(858, 2)],
            "money": 1500, "xp": 4, "min_level": 9,
        },
        {
            "id": "gift", "title": "The Gift Never Given", "giver": "ambrose", "ender": "agnes",
            "prev": "address",
            "log": "Find Agnes Balnir at the Sepulcher in Silverpine Forest.",
            "offer": (
                "Silverpine. A great many of us who woke there went no further than the Sepulcher: the Dark Lady's people "
                "keep it, and it's the nearest thing to a town those woods have left. If Agnes Balnir is anywhere, she's "
                "there, or under it.$B$B"
                "Go and find her. Don't tell her about the candlesticks straight off. Tell her Ambrose Wicke of Brill "
                "is holding an order in her brother's name, paid in full, and wishes to know what she would like done "
                "with it. That's the proper form.$B$B"
                "And $n... if she doesn't remember him, don't press her. Some of us came back with the whole of our "
                "lives. Some came back with a name and a smell of smoke."
            ),
            "progress": "",
            "done": (
                "Ambrose Wicke? Old Wicke, with the candles? He's still... well. Aren't we all, still.$B$B"
                "Tobias's candlesticks. He showed me the drawing. Silver, with a vine going up them, and their names on "
                "the base and the date. Harvest, the twelfth. Four years they waited for the levies to come down so the "
                "wedding could be paid for, and when they finally set the day it was the week the grain came.$B$B"
                "I remember it. I remember all of it. That's the trouble with me."
            ),
            "return": "Return to Agnes Balnir at the Sepulcher.",
            "money": 1000, "xp": 3, "min_level": 9,
        },
        {
            "id": "closing", "title": "Closing the Ledger", "giver": "agnes", "ender": "ambrose",
            "prev": "gift",
            "log": "Take Agnes Balnir's letter to Ambrose Wicke in Brill and decide what becomes of the candlesticks.",
            "offer": (
                "I've written to him. It's short. I was never one for letters; Tobias wrote them for both of us.$B$B"
                "I can't say what's to be done with them, $n. If I say keep them, I'm keeping a wedding that never came. "
                "If I say sell them, I'm selling my brother's last good idea. So I've told old Wicke the order is yours "
                "to settle. You found the farm. You saw the grave. You choose.$B$B"
                "Tell him one more thing for me, would you? Tell him Tobias isn't coming. Not because he doesn't care. "
                "Whatever climbed out of that grave wasn't my brother, and it didn't come to me, or to Marian, and it "
                "won't come to a candle shop. Tell him to open the shutters."
            ),
            "progress": "You've given him the letter? What did he say?",
            "done": (
                "\"The order is settled. Signed, A. Balnir, next of kin.\"$B$B"
                "Well. That's that, then.$B$B"
                "Eleven years I've kept this stall shut for a young man who was in the ground before I was. And I'd have "
                "kept it shut eleven more, $n, because while the order was open I was still a shopkeeper with a customer "
                "coming, and not just a dead man standing behind a counter.$B$B"
                "Help me with the shutters. We're open. Take this from stock, on the house: it's been waiting for someone "
                "too."
            ),
            "return": "Return to Ambrose Wicke in Brill.",
            "objectives": [("credit", "choice_credit", 1, "The candlesticks settled")],
            "items": [(7338, 1)],
            "money": 2500, "xp": 4, "min_level": 9,
        },
    ],
    # What became of the candlesticks.
    "markers": ["lit", "sold"],
    "npcs": [
        {"id": "ambrose", "name": "Ambrose Wicke", "subname": "Candles and Sundries", "display": 2622,
         "level": 22, "faction": 68, "flags": ["gossip", "quest", "vendor"],
         "spawns": [[0, 2345.3, 277.9, 34.75, 2.7]],
         # Cheap, odd and a little sad: candles, wrapping for gifts, wedding flowers, keepsakes.
         "vendor": [755, 17027, 5042, 5048, 3419, 3420, 5363, 18233, 5374, 5115, 5376, 3300, 5373, 5433, 11940, 6297]},
        {"id": "agnes", "name": "Agnes Balnir", "subname": "Laundress", "display": 2671,
         "level": 18, "faction": 68, "flags": ["gossip", "quest"],
         # The Sepulcher (Silverpine), by the vendors' tables, on the ground Dalar Dawnweaver stands on.
         "spawns": [[0, 547.0, 1588.0, 130.12, 0.9]]},
    ],
    "credits": [
        {"id": "dust_credit", "name": "Dusty corners cleaned"},
        {"id": "ledger_credit", "name": "Order ledger found"},
        {"id": "entry_credit", "name": "The ledger's last entry read"},
        {"id": "parcel_credit", "name": "The wrapped order found"},
        {"id": "sevren_credit", "name": "Magistrate Sevren asked about the Balnirs"},
        {"id": "clue_credit", "name": "Signs of the Balnirs' fate found"},
        {"id": "choice_credit", "name": "The candlesticks settled"},
    ],
    "objects": [
        # The stall, everyone's.
        {"id": "tent", "name": "Wicke's Stall", "display": 7872, "spawns": [[0, 2345.0, 278.0, 34.72, 2.7]]},
        {"id": "counter", "name": "Shop Counter", "display": 7732, "spawns": [[0, 2343.9, 278.5, 34.60, 2.7]]},
        # Business as Usual: the dust, and the ledger under the counter.
        {"id": "rug", "name": "Moth-Eaten Rug", "display": 159, "spawns": [[0, 2342.1, 279.4, 34.43, 2.7]],
         "use": [
             {"cond": ["I:business"], "quest": "business", "credit": "dust_credit"},
         ]},
        {"id": "crate", "name": "Dust-Choked Crate", "display": 113, "spawns": [[0, 2345.8, 280.9, 34.61, 1.2]],
         "use": [
             {"cond": ["I:business"], "quest": "business", "credit": "dust_credit"},
         ]},
        {"id": "shelf", "name": "Cobwebbed Shelf", "display": 187, "spawns": [[0, 2347.9, 279.5, 34.91, 2.7]],
         "use": [
             {"cond": ["I:business"], "quest": "business", "credit": "dust_credit"},
         ]},
        {"id": "ledger", "name": "Green-Bound Ledger", "display": 164, "spawns": [[0, 2343.1, 277.2, 34.57, 2.7]],
         "use": [
             {"cond": ["I:business"], "quest": "business", "credit": "ledger_credit"},
         ]},
        # An Outstanding Order: the order itself, wrapped and waiting.
        {"id": "parcel", "name": "Paper-Wrapped Parcel", "quest_only": True, "display": 4191, "spawns": [[0, 2345.6, 275.1, 34.92, 2.7]],
         "use": [
             {"cond": ["I:outstanding"], "quest": "outstanding", "credit": "parcel_credit"},
         ]},
        # No Forwarding Address: the Balnir Farmstead (map tile 0002832's terrain).
        {"id": "notice", "name": "Weathered Notice", "quest_only": True, "display": 2491, "spawns": [[0, 1998.0, -455.0, 34.53, 1.6]],
         "use": [
             {"cond": ["I:address"], "quest": "address", "credit": "clue_credit",
              "text": "(BY ORDER OF THE CROWN OF LORDAERON. THIS HOLDING IS UNDER QUARANTINE. NO PERSON SHALL ENTER OR LEAVE. GRAIN FROM THIS HOLDING IS TO BE BURNED.$B$BBelow, in pencil: we did burn it. it didn't help.)"},
         ]},
        {"id": "bible", "name": "Scorched Family Book", "quest_only": True, "display": 470, "spawns": [[0, 1948.0, -442.0, 35.45, 0.3]],
         "use": [
             {"cond": ["I:address"], "quest": "address", "credit": "clue_credit",
              "text": "(The Balnirs: Osric and Ada; Tobias, to wed Marian Hale, the date scratched out and written again three times; Agnes.$B$BThen, in Osric's shaking hand, all one autumn: Marian. Tobias. Ada. In another hand: Osric.$B$BBeside Agnes: in service, Silverpine.)"},
         ]},
        {"id": "stone", "name": "Balnir Family Stone", "display": 2452, "spawns": [[0, 2041.0, -517.0, 43.66, 4.7]],
         "use": [
             {"cond": ["I:address"], "quest": "address", "credit": "clue_credit"},
         ]},
        # Closing the Ledger: the stall open, its goods out (the phase "open").
        {"id": "candles", "name": "Wicke's Candles", "display": 100, "phase": "open",
         "spawns": [[0, 2341.6, 276.5, 34.45, 2.7]]},
        {"id": "basket", "name": "Basket of Sundries", "display": 7494, "phase": "open",
         "spawns": [[0, 2343.5, 281.8, 34.44, 1.9]]},
        {"id": "vase", "name": "Black Roses", "display": 6311, "phase": "open",
         "spawns": [[0, 2340.5, 278.3, 34.43, 2.7]]},
        {"id": "books", "name": "Second-Hand Books", "display": 107, "phase": "open",
         "spawns": [[0, 2347.4, 280.6, 34.77, 1.0]]},
    ],
    "gossip": [
        # Ambrose: what he says, by how far the line has gone (the first that holds).
        {"npc": "ambrose", "kind": "greet", "cond": ["R:closing", "M:lit"], "texts": [
            "Customer! A living one, or near enough. Mind the candlesticks in the window: they're not for sale. "
            "Everything else is, and most of it is older than you are.",
            "Welcome, welcome. Business is excellent. Nobody in Brill needs light to see by, so they buy candles "
            "for the smell. You'd be amazed what people want to smell like, round here.",
            "Two candles in the window, burning for a wedding. Folk ask who they're for. I tell them a customer. "
            "The best kind: paid in full and never complains.",
            "Ah, $n. Come in. I've a pocket watch that stopped the hour its owner did. Very reasonable. "
            "It's right twice a day, which is more than most of my customers manage.",
        ]},
        {"npc": "ambrose", "kind": "greet", "cond": ["R:closing", "M:sold"], "texts": [
            "Customer! The candlesticks are for sale, if you're marrying. Nobody's asked yet. Forsaken courtship "
            "is slow, I'm told. Something about the hands coming off.",
            "Welcome, welcome. Wrapping paper, $n? Red ribbon or blue. I've a great deal of practice wrapping things "
            "that never get collected.",
            "Sold three candles to a Deathguard this morning. He didn't say what for. In Brill, you learn not to ask "
            "what the candles are for.",
            "Ah, $n. I've a mirror in stock. Broken, I'm afraid. Most of my customers prefer it that way.",
        ]},
        {"npc": "ambrose", "kind": "greet", "cond": ["R:closing"], "texts": [
            "Open for business, $n. Candles, curios, and a very good price on handkerchiefs. Funerals and weddings "
            "both: I don't ask which.",
            "Customer! Come in, come in, before you die. Though if you do, I'll still be here.",
        ]},
        {"npc": "ambrose", "kind": "greet", "cond": ["A:closing"],
         "text": "That's Agnes Balnir's hand on that letter. I'd know it anywhere: she used to sign for her father's "
                 "wax. Well? Give it here. No. Wait. Tell me first. Then give it here."},
        {"npc": "ambrose", "kind": "greet", "cond": ["T:gift"],
         "text": "Silverpine. I've not been out of Brill since I woke up. I'd lose the custom. Not that I've any. "
                 "Go on, $n: the Sepulcher. Tell her it's paid in full."},
        {"npc": "ambrose", "kind": "greet", "cond": ["T:address"],
         "text": "The Balnir Farmstead, $n. South and east. When you come back, try not to look at me like that. "
                 "I can see your face from here. Well. With the one eye."},
        {"npc": "ambrose", "kind": "greet", "cond": ["T:business"],
         "text": "Mind the counter. It's held up a good deal of business in its time, and lately it's been holding up "
                 "me."},
        {"npc": "ambrose", "kind": "greet",
         "text": "Closed. We're closed. There's an order outstanding, and until it's collected, nothing in this stall "
                 "is for sale. No, not even that. Especially not that."},
        # Ambrose: the ledger read with him (An Outstanding Order).
        {"npc": "ambrose", "kind": "option", "cond": ["I:outstanding"], "text": "Read the ledger's last entry with him.",
         "action": "credit", "quest": "outstanding", "credit": "entry_credit", "emote": 1,
         "reply": "\"Balnir, T., of the Balnir Farmstead. One pair candlesticks, silvered, vine pattern, engraved. "
                  "For his wedding. Paid in full, in coin and two seasons' beeswax.\" And the date, $n. Read me the date. "
                  "...Eleven years? No. No, that's the ink. It runs."},
        # Ambrose: the candlesticks settled (Closing the Ledger): the player's choice.
        {"npc": "ambrose", "kind": "option", "cond": ["I:closing"],
         "text": "Light them, and keep them in your window. For the wedding.",
         "action": "choice", "quest": "closing", "credit": "choice_credit", "marker": "lit", "emote": 2,
         "reply": "In the window. Yes. Yes, that's proper. Folk will ask who they're for, and I'll say: a customer. "
                  "Paid in full. Not for sale."},
        {"npc": "ambrose", "kind": "option", "cond": ["I:closing"],
         "text": "Sell them to the next couple who'll have them. Someone should be married by them.",
         "action": "choice", "quest": "closing", "credit": "choice_credit", "marker": "sold", "emote": 273,
         "reply": "Sell them. To a wedding. Hah! In Brill! I may be waiting another eleven years, $n. But I'll wait "
                  "with the shutters open, this time."},
        # Ambrose, open: his wares, and a word for a neighbour.
        {"npc": "ambrose", "kind": "option", "cond": ["R:closing"], "text": "Let me see what you're selling.",
         "action": "vendor"},
        {"npc": "ambrose", "kind": "option", "cond": ["R:closing", "OWN"], "text": "Anything for the house by the road?",
         "action": "say", "emote": 1,
         "reply": "The old Harrow place? Candles, $n. A house is only a house until someone lights a candle in it. "
                  "After that it's a home, and after that, in my experience, it's a fire risk. I sell buckets too."},
        {"npc": "ambrose", "kind": "option", "cond": ["R:closing", "R:house.housewarming"],
         "text": "I had a housewarming, you know.", "action": "say", "emote": 6,
         "reply": "And nobody told me? I'd have brought a candle. Two! Well. Next time someone in Brill dies and gets "
                  "up again, we'll call it a housewarming and I'll bring three."},
        # Magistrate Sevren: the town's books (An Outstanding Order).
        {"npc": 1499, "kind": "option", "cond": ["I:outstanding"],
         "text": "Do the town's books say what became of the Balnir family?",
         "action": "credit", "quest": "outstanding", "credit": "sevren_credit", "emote": 1,
         "reply": "Balnir. The farm south-east, past the crossroads. The Crown quarantined it the first autumn of the "
                  "plague: the grain. My predecessor's hand. No departures recorded, $n, and nobody living's been there "
                  "since. If Wicke's sending you out there, tell him the Deathguard won't fetch you back."},
        # Agnes Balnir.
        {"npc": "agnes", "kind": "greet", "cond": ["R:closing"],
         "text": "Did he open the shutters? Good. Good. Tobias always said old Wicke would have sold candles to the "
                 "sun if it stood still long enough."},
        {"npc": "agnes", "kind": "greet", "cond": ["R:gift"],
         "text": "Shrouds don't wash themselves, $n. Well. Some of them try. Those I report to the Deathguard."},
        {"npc": "agnes", "kind": "greet",
         "text": "Laundry? Leave it there, and careful what you hand me: half of what comes in here used to belong to "
                 "someone, and they may want it back."},
        {"npc": "agnes", "kind": "option", "cond": ["R:gift"], "text": "Tell me about the wedding that never happened.",
         "action": "say", "emote": 1,
         "reply": "Harvest, the twelfth. Marian had a dress her mother wore, let out twice. Father had bought a pig. "
                  "I was to come home from Silverpine the week before. I didn't: the roads were closed. I had a letter "
                  "from Tobias saying the grain had come in plentiful, and they'd have bread enough for half of Brill. "
                  "That was the last letter. I've read it so often I don't need it any more."},
    ],
    "phases": {
        # The stall open: its goods out.
        "open": [["R:closing"]],
    },
}
