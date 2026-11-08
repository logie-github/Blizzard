"""Reading the core's world SQL dumps (data/sql/base/db_world/<table>.sql): the columns of the
table's CREATE TABLE and the rows of its INSERTs, each a dict of column -> value (strings
unquoted, NULL as None, numbers as text)."""
import re


def columns(text):
    head = text.split("CREATE TABLE", 1)[1].split("\n)", 1)[0]
    head = head.split("\n", 1)[1] if "\n" in head else ""       # (the first line names the table)
    return re.findall(r"^\s*`(\w+)`", head, re.M)


def values(text):
    """Every row of every INSERT in [text], as lists of raw values."""
    rows = []
    at = 0
    while True:
        at = text.find("INSERT INTO", at)
        if at < 0:
            break
        at = text.find("VALUES", at)
        if at < 0:
            break
        at += 6
        n = len(text)
        while at < n:
            while at < n and text[at] in " \n\r\t,":
                at += 1
            if at >= n or text[at] != "(":
                break
            at += 1
            row = []
            while at < n:
                while text[at] in " \t":
                    at += 1
                if text[at] == "'":
                    end = at + 1
                    out = []
                    while text[end] != "'":
                        if text[end] == "\\":
                            nxt = text[end + 1]
                            out.append({"n": "\n", "r": "\r", "t": "\t", "0": "\0"}.get(nxt, nxt))
                            end += 2
                        else:
                            out.append(text[end])
                            end += 1
                    row.append("".join(out))
                    at = end + 1
                else:
                    end = at
                    while text[end] not in ",)":
                        end += 1
                    token = text[at:end].strip()
                    row.append(None if token == "NULL" else token)
                    at = end
                while text[at] in " \t":
                    at += 1
                if text[at] == ",":
                    at += 1
                    continue
                if text[at] == ")":
                    at += 1
                    break
            rows.append(row)
            if at < n and text[at] == ";":
                at += 1
                break
    return rows


def table(path):
    """The table's rows as dicts."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    cols = columns(text)
    out = []
    for row in values(text):
        if len(row) == len(cols):
            out.append(dict(zip(cols, row)))
    return cols, out


def quote(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return repr(value) if isinstance(value, float) else str(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r") + "'"
