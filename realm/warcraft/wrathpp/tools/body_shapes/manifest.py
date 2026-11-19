"""The release's list of a body options package (wrathpp-body.json, which the app reads before it downloads the zip:
WrathppBodyFetch.kt): usage

  manifest.py PACKAGE.zip LOOKS_SHA256 INPUTS_SHA256 COMMIT > wrathpp-body.json

size and sha256: the zip's; models: how many models it has (the app takes the release's over a package of the user's
with fewer); looks: the looks package it was made for; inputs: what it was made from (the looks and the tools: the
workflow makes no new package while this is the published one's)."""
import hashlib
import json
import os
import sys
import zipfile


def manifest(package, looks, inputs, commit):
    h = hashlib.sha256()
    with open(package, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    with zipfile.ZipFile(package) as z:
        listed = json.loads(z.read("wrathpp-body.json"))
    if listed.get("kind") != "wrathpp-body" or listed.get("format") != 2 or not listed.get("models"):
        raise SystemExit("%s is not a body options package of format 2" % package)
    return {"size": os.path.getsize(package), "sha256": h.hexdigest(), "format": 2, "models": len(listed["models"]),
            "races": len(listed["races"]), "looks": looks, "inputs": inputs, "commit": commit}


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    print(json.dumps(manifest(*sys.argv[1:5])))
