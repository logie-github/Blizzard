"""The starting-areas tools (mod-worgen-goblin/tools/zones), used read-only: loaded from where they are, never copied or edited.

`files.py` (what an ADT, an M2 and a WMO name) and `spells.py` / `items.py` / `vehicles.py` (world data builders) are imported by
file path under names of their own, with the zones folder on sys.path only while they load (they `import common` by that name).
A missing folder is a clear error, not an ImportError somewhere deep.
"""
import importlib.util
import os
import sys

from . import util

ZONES = os.path.normpath(os.path.join(util.HERE, "..", "..", "modules", "mod-worgen-goblin", "tools", "zones"))
_loaded = {}


def load(name):
    """The zones module `name` (for example `files`), as `zones_<name>`."""
    if name in _loaded:
        return _loaded[name]
    path = os.path.join(ZONES, name + ".py")
    if not os.path.exists(path):
        raise RuntimeError(f"the zones tools are not at {ZONES} (needed for {name}.py)")
    spec = importlib.util.spec_from_file_location("zones_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, ZONES)
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(ZONES)
    _loaded[name] = mod
    return mod
