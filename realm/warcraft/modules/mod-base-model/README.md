# No Gear (mod-base-model)

**Game options → No Gear** (named Body before) previews female characters without starter gear in the character creation
menu. Male previews, the character list and characters in the world keep their equipment visible.
Both 3.3.5a realms support it. Restart the realm and game after changing the option.

The existing `files/base-model/enabled` preference is preserved. The final client patch
(`mod-skyborne`) clears equipment only from female `CharStartOutfit.dbc` records, each slot emptied as
the game's own empty slots are (item, display and inventory type -1; zeros, until issue #119, read as
an item and corrupted the creation screen's memory). The server's
outfits, equipment and visible item fields are untouched. Turning it off rebuilds the client
patch from the original outfits. `BaseModel.Enable = 0` disables the option.

The old module loader remains for compatibility and registers no player hooks.
