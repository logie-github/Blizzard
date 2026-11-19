#!/usr/bin/env python3
"""The creator as the game draws it on the phone: the pictures the app sent (WrathppPictures: the game's own screenshots
of the creator's screens, each an issue or a few, its JPEG in base64), put together into files.
    fetch_pictures.py OUT_DIR [owner/repo]         by gh (search/issues), the newest first
    fetch_pictures.py OUT_DIR --bodies FILE.json   from a list of {"title", "body", "number"} (the tests)
A picture's file is OUT_DIR/<issue of its first part>-<which>-<what>.jpg; one whose parts are not all there is said."""
import base64, json, os, re, subprocess, sys

def read(issues):
    """{(state, which): {"what", "of", "parts": {i: text}, "count", "bytes", "issue"}} from the issues' titles and texts."""
    pictures = {}
    for issue in issues:
        body = issue.get("body") or ""
        m = re.search(r"picture (\d+) of (\d+), part (\d+) of (\d+), (\d+) bytes of JPEG", body)
        data = re.search(r"-----BEGIN PICTURE-----\n(.*?)-----END PICTURE-----", body, re.S)
        if not m or not data:
            continue
        which, of, part, count, size = (int(x) for x in m.groups())
        title = issue.get("title") or ""
        state = (re.search(r"\(([^()]*)\)\s*$", title) or re.search(r"\(([^()]*)\)", title))
        what = re.search(r":\s*(.*?)\s*\(", title)
        key = (state.group(1) if state else "", which)
        p = pictures.setdefault(key, {"what": what.group(1) if what else "", "of": of, "parts": {}, "count": count, "bytes": size, "issue": issue.get("number")})
        p["parts"].setdefault(part, "".join(data.group(1).split()))
        if part == 1:
            p["issue"] = issue.get("number")
    return pictures

def write(pictures, out):
    os.makedirs(out, exist_ok=True)
    done = []
    for (state, which), p in sorted(pictures.items(), key=lambda kv: (-(kv[1]["issue"] or 0), kv[0][1])):
        if len(p["parts"]) != p["count"]:
            print("picture %d of %s: %d of its %d parts are there" % (which, state, len(p["parts"]), p["count"]))
            continue
        raw = base64.b64decode("".join(p["parts"][i] for i in sorted(p["parts"])))
        if len(raw) != p["bytes"]:
            print("picture %d of %s: %d bytes and it said %d" % (which, state, len(raw), p["bytes"]))
            continue
        name = "%s-%d-%s.jpg" % (p["issue"], which, re.sub(r"[^a-z0-9]+", "-", p["what"].lower()).strip("-") or "picture")
        with open(os.path.join(out, name), "wb") as f:
            f.write(raw)
        done.append(name)
        print("%s  (%s; %d bytes)" % (name, state, len(raw)))
    return done

def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    out = argv[1]
    if len(argv) > 3 and argv[2] == "--bodies":
        issues = json.load(open(argv[3], encoding="utf-8"))
    else:
        repo = argv[2] if len(argv) > 2 else "logie-github/Blizzard"
        q = 'repo:%s is:issue "Wrath++ creator picture" in:title' % repo
        text = subprocess.run(["gh", "api", "-X", "GET", "search/issues", "-f", "q=" + q, "-f", "sort=created", "-f", "order=desc", "-f", "per_page=60",
                               "--jq", "[.items[] | {number, title, body}]"], check=True, capture_output=True, text=True).stdout
        issues = json.loads(text)
    done = write(read(issues), out)
    print("%d picture(s)" % len(done))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
