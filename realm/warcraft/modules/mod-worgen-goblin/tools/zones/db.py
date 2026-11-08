"""The two worlds the port reads, in a local MariaDB: the Cataclysm Preservation Project's (its full
TDB with its updates since: CPP_DB) and AzerothCore's (the realm's core's base and updates: AC_DB), as
rows of text by column name (None for NULL). README (The starting areas) says how they're loaded.
"""
import os
import subprocess

CPP_DB = os.environ.get("ZONES_CPP_DB", "cpp_world")
AC_DB = os.environ.get("ZONES_AC_DB", "ac_world")


def unescape(value):
    """A value as mariadb's batch output escapes it (\\n, \\t, \\\\, \\0), as it is."""
    if "\\" not in value:
        return value
    out, i = [], 0
    while i < len(value):
        c = value[i]
        if c == "\\" and i + 1 < len(value):
            out.append({"n": "\n", "t": "\t", "0": "\0", "\\": "\\", "r": "\r"}.get(value[i + 1], value[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def rows(db, sql):
    out = subprocess.run(["mariadb", "-B", db, "-e", sql], check=True, capture_output=True).stdout.decode("utf-8", "replace")
    lines = out.split("\n")
    if not lines or not lines[0]:
        return []
    names = lines[0].split("\t")
    result = []
    for line in lines[1:]:
        if not line:
            continue
        values = line.split("\t")
        result.append({n: (None if v == "NULL" else unescape(v)) for n, v in zip(names, values)})
    return result


def column_names(db, table):
    return [r["column_name"] for r in rows(db, f"SELECT column_name FROM information_schema.columns WHERE "
                                              f"table_schema = '{db}' AND table_name = '{table}' ORDER BY ordinal_position")]


def ids_in(values):
    """A SQL list of numbers (0 alone for none)."""
    values = sorted({int(v) for v in values})
    return ", ".join(str(v) for v in values) if values else "0"
