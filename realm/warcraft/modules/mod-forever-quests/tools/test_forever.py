#!/usr/bin/env python3
"""mod-forever-quests' tools and data, without the game's or the core's files: foreverchanges.py on a
stand-in page laid out as the site's are; wowhead.py on stand-in tooltips; the races each Forever
race mask opens; and the committed SQL against the committed data (every quest there with its words,
a giver and an ender; every new item it names made; every new NPC drawn and standing somewhere;
nothing past the core's quest table's limit)."""
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import forever  # noqa: E402
import foreverchanges  # noqa: E402
import wowhead  # noqa: E402
import sqlrows  # noqa: E402

MODULE = os.path.dirname(HERE)
failures = []


def check(ok, what):
    if not ok:
        failures.append(what)
        print("FAIL:", what)


PAGE = """<html><body><nav class="qp-crumbs" aria-label="Breadcrumb"><a href="/quests">Quests</a><span aria-hidden="true"> › </span>
<span>Durotar</span></nav><h1>Stand-in</h1><div class="qp-grid"><article class="qp-sheet"><h2>Quest Objectives</h2>
<p>Bring 4 Test Pelts to Tester and slay 3 Test Wolves.</p><ul class="qp-need"><li class="qp-need-item"><a class="qp-item"
href="/item/250001" data-tip="250001"><span class="qp-item-icon"><img src="/icon/inv_misc_pelt_wolf_01.jpg" alt="" width="40"
height="40" loading="lazy"/><b>4</b></span><span class="qp-item-name q1">Test Pelt</span></a></li><li class="qp-need-goal"><span
class="qp-bullet" aria-hidden="true"></span>Test Wolf slain<!-- -->: <b>0/<!-- -->3</b></li></ul><h2>Description</h2><p>First
line for &lt;‹name›&gt;, a ‹race› ‹class›.</p><p>Second line.</p><h2>Rewards</h2><p>You will be able to choose one of these
rewards:</p><div class="qp-items"><a class="qp-item" href="/item/250002" data-tip="250002"><span class="qp-item-icon"><img
src="/icon/inv_boots_01.jpg" alt="" width="40" height="40" loading="lazy"/></span><span class="qp-item-name q2">Boots</span></a></div>
<p>You will receive:</p><div class="qp-items"><a class="qp-item" href="/item/250003" data-tip="250003"><span class="qp-item-icon"><img
src="/icon/inv_misc_food_01.jpg" alt="" width="40" height="40" loading="lazy"/><b>5</b></span><span class="qp-item-name q1">Bread</span>
</a></div><p class="qp-gains"><span>Money:</span> <span class="qp-money"><span class="qp-coin qp-silver">3</span><span class="qp-sr">1
gold, 3 silver, 7 copper</span></span><span>Experience:</span> <b>1,250</b></p><ul class="qp-rep"><li>+75 reputation with
Undercity</li></ul><div class="qp-more"><details><summary>When you come back</summary><p>Not yet?</p></details><details><summary>When
you hand it in</summary><p>Done, ‹name›.</p></details></div></article><aside class="qp-side"><dl class="qp-facts"><dt>Level</dt>
<dd>12<!-- -->, <!-- -->requires level 7</dd><dt>Side</dt><dd>Horde</dd><dt>Shareable</dt><dd>Yes</dd><dt>Quest ID</dt><dd>90001</dd>
</dl></aside></div></body></html>"""

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "90001.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PAGE)
    page = foreverchanges.parse(path)
    check(page["objectives_text"] == "Bring 4 Test Pelts to Tester and slay 3 Test Wolves.", "the objectives' line")
    check(page["need_items"] == [(250001, 4)], "the items to bring and their count: %r" % page["need_items"])
    check(page["need_goals"] == [["Test Wolf", 3]], "the creatures to slay: %r" % page["need_goals"])
    check(page["description"] == "First line for <$N>, a $R $C.$B$BSecond line.", "the description: %r" % page["description"])
    check(page["reward_choice"] == [[250002, 1]] and page["reward_items"] == [[250003, 5]], "the rewards")
    check(page["money"] == 10307 and page["xp"] == 1250, "money and experience: %r %r" % (page["money"], page["xp"]))
    check(page["reputation"] == [["Undercity", 75]], "the reputation")
    check(page["progress"] == "Not yet?" and page["completion"] == "Done, $N.", "the progress and completion texts")
    check((page["level"], page["min_level"], page["side"], page["shareable"]) == (12, 7, "Horde", True), "the facts")
    check(page["icons"]["250001"] == "inv_misc_pelt_wolf_01", "the icons")
    check(page["category"] == "Durotar", "where the site files it: %r" % page["category"])
    with open(path, "w", encoding="utf-8") as f:
        f.write("<html>404</html>")
    check(foreverchanges.parse(path) is None, "a page the site hasn't")

# Wowhead's tooltips, as nether.wowhead.com gives them.
spider = wowhead.npc({"name": "Test", "tooltip": "<table><tr><td><b class=\"q\">Test</b></td></tr><tr><td>Level 8 Beast (Elite)</td></tr>"
                                                "<tr><td>Spider</td></tr></table>"})
check(spider == {"type": 1, "family": "Spider", "rank": 1, "level": [8, 8]}, "an NPC's tooltip: %r" % spider)
lance = wowhead.item({"name": "Lance", "quality": 2, "icon": "inv_spear_08", "spells": [], "tooltip":
                      "<table><tr><td><b class=\"q2\">Lance</b><span class=\"q\"><br>Item Level <!--ilvl-->25</span><!--bo--><br>Binds when "
                      "picked up<table width=\"100%\"><tr><td>Two-Hand</td><th><!--scstart2:6--><span class=\"q1\">Polearm</span><!--scend--></th>"
                      "</tr></table><table width=\"100%\"><tr><td><span><!--dmg-->44 - 67 Damage</span></td><th>Speed <!--spd-->3.30</th></tr></table>"
                      "<br><span><!--stat3-->+7 Agility</span><br><span><!--stat7-->+5 Stamina</span><br>Durability 75 / 75</td></tr></table><table><tr>"
                      "<td><span class=\"q2\">Equip: Increases damage and healing done by magical spells and effects by up to <span><!--rtg41-->4"
                      "</span>.</span><div class=\"whtt-sellprice\">Sell Price: <span class=\"moneysilver\">32</span> <span class=\"moneycopper\">55"
                      "</span></div></td></tr></table>"})
check((lance["dmg"], lance["speed"], lance["durability"], lance["sell"], lance["bonding"]) == ([44, 67], 3.3, 75, 3255, 1), "an item's numbers: %r" % lance)
check(lance["stats"] == [[3, 7], [7, 5], [45, 4]], "an item's stats, spell damage as spell power: %r" % lance["stats"])

# Forever's race masks (QuestieDB's): every Alliance race is all of the realm's Alliance, a race the
# realm adds goes with the race whose start it takes, Forever's Skyborne are the module's.
alliance = 1 + 4 + 8 + 64 + (1 << 32)
horde = 2 + 16 + 32 + 128 + (1 << 33)
check(forever.races(alliance) == 1 | 4 | 8 | 64 | 1024 | (1 << 12) | (1 << 14) | (1 << 16), "the Alliance's races")
check(forever.races(horde) == 2 | 16 | 32 | 128 | 512 | (1 << 13) | (1 << 15) | (1 << 17), "the Horde's races")
check(forever.races(alliance | horde) == 0 and forever.races(None) == 0, "every race")
check(forever.races(1) == 1 | (1 << 12), "the Humans' quests are the High Order's too")
check(forever.races(32) == 32 | (1 << 13) | (1 << 17), "the Tauren's quests are the Windshapers' and the Zandalari's too")

# The committed data and SQL.
data = json.load(open(os.path.join(MODULE, "data", "forever", "quests.json"), encoding="utf-8"))
text = open(forever.SQL_OUT, encoding="utf-8").read()


def rows(table):
    m = re.search(r"INSERT INTO `%s` \((.*?)\) VALUES\n(.*?);\n" % table, text, re.S)
    if not m:
        return []
    cols = [c.strip("` ") for c in m.group(1).split(",")]
    return [dict(zip(cols, r)) for r in sqlrows.values("INSERT INTO x VALUES " + m.group(2) + ";")]


quests = {int(r["ID"]): r for r in rows("quest_template")}
check(set(quests) == {int(q) for q in data["quests"]}, "the SQL's quests are quests.json's")
check(all(q < 1000000 for q in quests), "quest ids under a million (the core's quest table grows to the highest)")
starters = {int(r["quest"]) for r in rows("creature_queststarter")} | {int(r["quest"]) for r in rows("gameobject_queststarter")}
items = {int(r["entry"]): r for r in rows("item_template")}
starters |= {int(r["startquest"]) for r in items.values() if int(r["startquest"])}
enders = {int(r["quest"]) for r in rows("creature_questender")}
for qid, q in quests.items():
    check(qid in starters, "%d has someone or something to start it" % qid)
    check(qid in enders, "%d has someone to end it" % qid)
    check(q["QuestDescription"] and q["LogDescription"], "%d has its words" % qid)
    check("‹" not in q["QuestDescription"] + q["LogDescription"], "%d has no placeholder of the site's left" % qid)
    for key in [k for k in q if re.match(r"(RequiredItemId|RewardItem|RewardChoiceItemID)\d$", k)] + ["StartItem"]:
        i = int(q[key])
        check(i < 200000 or i in items, "%d's item %d is made" % (qid, i))
    check(int(q["RewardXPDifficulty"]) in range(0, 9), "%d's experience is one of the game's steps" % qid)
new_npcs = {int(n) for n, v in data["npcs"].items() if v.get("new")}
templates = {int(r["entry"]) for r in rows("creature_template")}
models = {int(r["CreatureID"]) for r in rows("creature_template_model")}
spawns = rows("creature")
standing = {int(r["id"]) for r in spawns}
check(templates == new_npcs, "the SQL's new NPCs are quests.json's")
for n in new_npcs:
    check(n in models, "%d is drawn" % n)
    check(n in standing, "%d stands somewhere" % n)
check(all(forever.FIRST_GUID <= int(r["guid"]) < forever.FIRST_GUID + 100000 for r in spawns), "the spawns' guids are the module's")
check(all(-20000 < float(r["position_z"]) < 20000 for r in spawns), "the spawns stand at a height")
for r in rows("creature_loot_template"):
    check(int(r["Item"]) in items or "as " in r["Comment"], "the drop %s is an item made here, or the look's own loot" % r["Item"])

print("%d checks failed" % len(failures) if failures else "All checks passed (%d quests, %d items)" % (len(quests), len(items)))
sys.exit(1 if failures else 0)
