"""How Wrath++'s client reads a skin section's first index (the converter, the checker, the renderer and the body layer share it).

WarcraftXL-Labs/client, Engine/Source/Model2/M2Data.h (commit e3dc928, "wide skin indices"): the skin section's id field is
32 bits, the id in its low half and, in the high half, the "level" (an LOD marker in 3.3.5's files). A section's real first
index is (level << 16) | indexStart, taken only when the window [wide, wide + indexCount) lies inside the skin's own index
array; otherwise the 16-bit indexStart stands (a skin of 65535 indices or fewer reads as it always did).
M2SkinSectionGeosetId then drops the high half (id & 0xFFFF) when the wide start was taken.
"""


def wide_index_start(index_count, level, start, count):
    """M2SkinSectionIndexStart: a skin of [index_count] indices, a section with [level] (high half-word of its id field),
    16-bit [start] and [count]."""
    wide = (level << 16) | start
    if wide != start and wide <= index_count and count <= index_count - wide:
        return wide
    return start


def geoset_id(index_count, id_low, level, start, count):
    """M2SkinSectionGeosetId: the id a section answers to. (With a level the client could not use as a start, it reads the
    32-bit field whole: the level stays in the id.)"""
    if wide_index_start(index_count, level, start, count) != start:
        return id_low
    return (level << 16) | id_low
