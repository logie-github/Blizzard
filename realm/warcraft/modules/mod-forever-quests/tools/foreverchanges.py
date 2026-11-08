"""foreverchanges.pro's quest pages (foreverchanges.pro/quest/<id>: Wowhead's Forever database, as the
site shows it): the quest's own words, objectives, rewards and facts, read from the page's HTML."""
import html
import os
import re
import time
import urllib.request

URL = "https://foreverchanges.pro/quest/%d"
USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"
# The page's placeholders and the game's: the player's name, class and race.
PLACEHOLDERS = {"‹name›": "$N", "‹class›": "$C", "‹race›": "$R"}


def fetch(ids, cache):
    """Each quest's page into [cache] (<id>.html), the ones not there yet, a third of a second apart."""
    os.makedirs(cache, exist_ok=True)
    for qid in ids:
        path = os.path.join(cache, "%d.html" % qid)
        if os.path.exists(path) and os.path.getsize(path):
            continue
        try:
            with urllib.request.urlopen(urllib.request.Request(URL % qid, headers={"User-Agent": USER_AGENT}), timeout=60) as r:
                data = r.read()
        except urllib.error.HTTPError as e:
            data = e.read()
        with open(path, "wb") as f:
            f.write(data)
        time.sleep(0.3)


def text(fragment):
    """A fragment's paragraphs as the game writes them: $B$B between paragraphs, its placeholders."""
    paras = re.findall(r"<p>(.*?)</p>", fragment, re.S)
    out = []
    for p in paras:
        p = re.sub(r"<br\s*/?>", "\n", p)
        p = html.unescape(re.sub(r"<[^>]+>", "", p)).strip()
        for a, b in PLACEHOLDERS.items():
            p = p.replace(a, b)
        p = p.replace("\n", "$B")
        if p:
            out.append(p)
    return "$B$B".join(out)


def items(fragment):
    """The items a list shows: (id, count, icon)."""
    out = []
    for m in re.finditer(r'<a class="qp-item" href="/item/(\d+)".*?<img src="/icon/([\w-]+)\.jpg"[^>]*/>(?:<b>(\d+)</b>)?', fragment, re.S):
        out.append((int(m.group(1)), int(m.group(3) or 1), m.group(2)))
    return out


def section(page, start, ends):
    at = page.find(start)
    if at < 0:
        return ""
    stop = min([i for i in (page.find(e, at + len(start)) for e in ends) if i > 0] or [len(page)])
    return page[at + len(start):stop]


def parse(path):
    """A quest page as data, or None if the site has no page for it."""
    page = re.sub(r"\s*\n\s*", " ", open(path, encoding="utf-8", errors="replace").read())   # (a line break in HTML is a space)
    if not re.search(r"<dt>Quest ID</dt>", page):
        return None
    sheet = page[page.find('<article class="qp-sheet">'):page.find("</article>")]
    heads = ["<h2>", '<div class="qp-more">']
    q = {}
    # where the site files it: Quests › <zone, class or kind>
    m = re.search(r'<nav class="qp-crumbs"[^>]*>.*?</a>.*?<span>([^<]+)</span>\s*</nav>', page)
    q["category"] = html.unescape(m.group(1)).strip() if m else ""
    objectives = section(sheet, "<h2>Quest Objectives</h2>", heads)
    q["objectives_text"] = text(objectives.split('<ul class="qp-need">')[0])
    q["need_items"] = [(i, c) for i, c, _ in items(objectives)]
    q["need_goals"] = []
    for m in re.finditer(r'<li class="qp-need-goal">.*?</span>(.*?)</li>', objectives, re.S):
        goal = html.unescape(re.sub(r"<[^>]+>|<!-- -->", "", m.group(1)))
        g = re.match(r"(.*?)(?: slain)?: 0/(\d+)$", goal.strip())
        q["need_goals"].append([g.group(1), int(g.group(2))] if g else [goal.strip(), 1])
    q["description"] = text(section(sheet, "<h2>Description</h2>", heads))
    rewards = section(sheet, "<h2>Rewards</h2>", ['<div class="qp-more">'])
    choose = section(rewards, "choose one of these rewards", ["You will receive", '<p class="qp-gains">'])
    receive = section(rewards, "You will receive", ["choose one of these rewards", '<p class="qp-gains">'])
    q["reward_choice"] = [[i, c] for i, c, _ in items(choose)]
    q["reward_items"] = [[i, c] for i, c, _ in items(receive)]
    q["icons"] = {str(i): icon for i, _, icon in items(rewards) + items(objectives)}
    money = re.search(r'class="qp-sr">(\d+) gold, (\d+) silver, (\d+) copper', rewards)
    q["money"] = int(money.group(1)) * 10000 + int(money.group(2)) * 100 + int(money.group(3)) if money else 0
    xp = re.search(r"<span>Experience:</span>\s*<b>([\d,]+)</b>", rewards)
    q["xp"] = int(xp.group(1).replace(",", "")) if xp else 0
    q["reputation"] = [[html.unescape(f), int(v)] for v, f in re.findall(r"<li>\+?(-?\d+) reputation with ([^<]+)</li>", rewards)]
    spell = re.search(r'href="/spell/(\d+)"', rewards)
    q["reward_spell"] = int(spell.group(1)) if spell else 0
    q["progress"] = text(section(sheet, "<summary>When you come back</summary>", ["</details>"]))
    q["completion"] = text(section(sheet, "<summary>When you hand it in</summary>", ["</details>"]))
    facts = page[page.find('<dl class="qp-facts">'):]
    facts = facts[:facts.find("</dl>")]
    level = re.search(r"<dt>Level</dt>\s*<dd>(\d+)(?:<!-- -->, <!-- -->requires level (\d+))?", facts)
    q["level"] = int(level.group(1)) if level else 0
    q["min_level"] = int(level.group(2)) if level and level.group(2) else 0
    side = re.search(r"<dt>Side</dt>\s*<dd>(\w+)</dd>", facts)
    q["side"] = side.group(1) if side else ""
    q["shareable"] = bool(re.search(r"<dt>Shareable</dt>\s*<dd>Yes</dd>", facts))
    return q
