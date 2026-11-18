"""Where the game's files and tables come from, and what happens when that is down.

A Source gives `file(fdid) -> bytes` and `table(name) -> csv text` at one build. Three kinds:
  HttpSource   wago.tools (`/api/casc/<fdid>?download&version=<build>`, `/db2/<Table>/csv?build=<build>`), the endpoints
               mod-worgen-goblin/tools/zones/common.py uses; retries with back-off and jitter, honours Retry-After, rejects
               truncated bodies and HTML error pages (wago.tools answers 500 with a 6.5 KB page when it is down), gives up after
               a time budget with SourceDown (the map is then `deferred`, not failed).
  DirSource    a folder: files/<fdid>, tables/<Name>.csv (the zones' own cache layout, so a cache of theirs works, and the
               tests' fixture).
  ChainSource  several in order: the first that has it; a down one passes to the next.
CachedSource keeps what any source gave in a folder of the same layout (a miss, an empty file, is kept too).
Missing means the build does not have the file (HTTP 400/404): not an error, a line in the report.
"""
import os
import random
import time
import urllib.error
import urllib.request

from . import util

USER_AGENT = "catabackport/1.0 (+https://github.com/logie-github/blizzard)"   # (wago.tools turns away Python's own)


class Missing(Exception):
    """The build has no such file or table."""


class SourceDown(Exception):
    """The source could not be reached within the retry budget: the work is deferred to a later run."""


class Budget:
    """A time budget for all waiting on a source in one stage."""

    def __init__(self, seconds, clock=time.monotonic):
        self.clock = clock
        self.deadline = clock() + seconds

    def left(self):
        return self.deadline - self.clock()


class HttpSource:
    def __init__(self, build, base="https://wago.tools", tries=6, budget=None, sleep=time.sleep, urlopen=None, timeout=180):
        self.build, self.base, self.tries = build, base.rstrip("/"), tries
        self.budget, self.sleep, self.timeout = budget, sleep, timeout
        self.urlopen = urlopen or urllib.request.urlopen
        self.stats = {"requests": 0, "retries": 0, "bytes": 0}

    def _get(self, url, html_is_error=False):
        err = None
        for attempt in range(self.tries):
            if self.budget is not None and self.budget.left() <= 0:
                raise SourceDown(f"{url}: retry budget used up ({err})")
            wait = min(60, 2 ** attempt) + random.random()
            try:
                self.stats["requests"] += 1
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with self.urlopen(req, timeout=self.timeout) as r:
                    data = r.read()
                    expected = r.headers.get("Content-Length") if getattr(r, "headers", None) else None
                if expected is not None and expected.isdigit() and int(expected) != len(data):
                    raise IOError(f"truncated: {len(data)} of {expected} bytes")
                if html_is_error and data[:15].lstrip().lower().startswith((b"<!doctype html", b"<html")):
                    raise IOError("an HTML page instead of a table")
                self.stats["bytes"] += len(data)
                return data
            except urllib.error.HTTPError as e:
                if e.code in (400, 404):
                    raise Missing(url)
                err = e
                retry_after = e.headers.get("Retry-After") if e.headers else None
                if retry_after and retry_after.isdigit():
                    wait = min(300, int(retry_after))
            except Exception as e:       # (a dropped connection, a timeout, a truncated body: tried again)
                err = e
            self.stats["retries"] += 1
            if attempt + 1 < self.tries:
                if self.budget is not None:
                    wait = min(wait, max(0, self.budget.left()))
                self.sleep(wait)
        raise SourceDown(f"{url}: {err}")

    def file(self, fdid):
        return self._get(f"{self.base}/api/casc/{fdid}?download&version={self.build}")

    def table(self, name):
        return self._get(f"{self.base}/db2/{name}/csv?build={self.build}", html_is_error=True).decode("utf-8")

    def builds(self):
        """The builds wago.tools lists (the inventory's note; None when it can't say)."""
        try:
            return self._get(f"{self.base}/api/builds").decode("utf-8")
        except (Missing, SourceDown):
            return None


class DirSource:
    def __init__(self, root):
        self.root = root

    def file(self, fdid):
        path = os.path.join(self.root, "files", str(fdid))
        if not os.path.exists(path):
            raise Missing(path)
        data = open(path, "rb").read()
        if not data:
            raise Missing(path)
        return data

    def table(self, name):
        path = os.path.join(self.root, "tables", name + ".csv")
        if not os.path.exists(path):
            raise Missing(path)
        return open(path, encoding="utf-8").read()


class ChainSource:
    def __init__(self, sources):
        self.sources = list(sources)

    def _try(self, method, arg):
        down = None
        for s in self.sources:
            try:
                return getattr(s, method)(arg)
            except SourceDown as e:
                down = e
            except Missing:
                continue
        if down:
            raise down
        raise Missing(str(arg))

    def file(self, fdid):
        return self._try("file", fdid)

    def table(self, name):
        return self._try("table", name)


class CachedSource:
    def __init__(self, inner, cache):
        self.inner, self.cache = inner, cache

    def file(self, fdid):
        path = os.path.join(self.cache, "files", str(fdid))
        if os.path.exists(path):
            data = open(path, "rb").read()
            if not data:
                raise Missing(str(fdid))
            return data
        try:
            data = self.inner.file(fdid)
        except Missing:
            util.write_atomic(path, b"")
            raise
        util.write_atomic(path, data)
        return data

    def table(self, name):
        path = os.path.join(self.cache, "tables", name + ".csv")
        if os.path.exists(path):
            return open(path, encoding="utf-8").read()
        text = self.inner.table(name)
        util.write_atomic(path, text)
        return text


def from_spec(spec, build, cache=None, budget_seconds=5400, sleep=time.sleep):
    """`wago`, `dir:PATH` or `url:BASE` (a mirror with wago.tools' paths), comma separated, in order."""
    budget = Budget(budget_seconds)
    sources = []
    for part in spec.split(","):
        part = part.strip()
        if part == "wago":
            sources.append(HttpSource(build, budget=budget, sleep=sleep))
        elif part.startswith("dir:"):
            sources.append(DirSource(part[4:]))
        elif part.startswith("url:"):
            sources.append(HttpSource(build, base=part[4:], budget=budget, sleep=sleep))
        elif part:
            raise ValueError(f"unknown source {part!r} (wago, dir:PATH, url:BASE)")
    src = sources[0] if len(sources) == 1 else ChainSource(sources)
    return CachedSource(src, cache) if cache else src
