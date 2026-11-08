"""Reads Lua table literals as data (no Lua is run): tables, strings, numbers, nil/true/false,
dotted names (resolved by a callback), + and - of numbers, and parenthesised expressions."""
import re

TOK = re.compile(r"""
 (?P<ws>\s+)
|(?P<lcom>--\[(?P<eq>=*)\[.*?\](?P=eq)\])
|(?P<com>--[^\n]*)
|(?P<lstr>\[(?P<eq2>=*)\[.*?\](?P=eq2)\])
|(?P<str>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')
|(?P<num>0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)
|(?P<name>[A-Za-z_][A-Za-z_0-9]*)
|(?P<op>\.\.|[{}\[\]=,;.+\-()*/:#<>~])
|(?P<other>.)
""", re.S | re.X)
ESC = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "\n": "\n", "a": "\a", "b": "\b", "f": "\f", "v": "\v"}

def unescape(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            n = s[i + 1]
            if n.isdigit():
                m = re.match(r"\d{1,3}", s[i + 1:]).group(0)
                out.append(chr(int(m))); i += 1 + len(m); continue
            out.append(ESC.get(n, n)); i += 2; continue
        out.append(c); i += 1
    return "".join(out)

def tokens(text):
    pos = 0
    out = []
    for m in TOK.finditer(text):
        if m.start() != pos:
            raise ValueError("bad character at %d: %r" % (pos, text[pos:pos + 40]))
        pos = m.end()
        k = m.lastgroup
        if k in ("ws", "lcom", "com", "eq"):
            continue
        v = m.group(k)
        if k == "lstr":
            body = v[v.index("[", 1) + 1: -len(m.group("eq2")) - 2]
            out.append(("str", body[1:] if body.startswith("\n") else body))
        elif k == "str":
            out.append(("str", unescape(v[1:-1])))
        elif k == "num":
            out.append(("num", int(v, 16) if v.lower().startswith("0x") else (float(v) if re.search(r"[.eE]", v) else int(v))))
        elif k == "eq2":
            continue
        else:
            out.append((k, v))
    if pos != len(text):
        raise ValueError("trailing text at %d" % pos)
    return out

class Table:
    """A Lua table: hash part (dict) with integer keys for positional items; nil holes leave keys out."""
    def __init__(self):
        self.d = {}
    def __repr__(self):
        return "T%r" % self.d

class Parser:
    def __init__(self, toks, resolve):
        self.t, self.i, self.resolve = toks, 0, resolve
    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else (None, None)
    def take(self, v=None):
        tok = self.t[self.i]
        if v is not None and tok[1] != v:
            raise ValueError("expected %r got %r at token %d" % (v, tok, self.i))
        self.i += 1
        return tok
    def expr(self):
        v = self.term()
        while self.peek()[1] in ("+", "-", "..") and self.peek()[0] == "op":
            op = self.take()[1]
            w = self.term()
            if op == "..":
                v = str(v) + str(w)
            elif isinstance(v, (int, float)) and isinstance(w, (int, float)):
                v = v + w if op == "+" else v - w
            else:
                v = ("expr", v, op, w)
        return v
    def term(self):
        k, v = self.peek()
        if k == "op" and v == "-":
            self.take(); x = self.term()
            return -x if isinstance(x, (int, float)) else ("neg", x)
        if k == "op" and v == "(":
            self.take(); x = self.expr(); self.take(")"); return x
        if k == "op" and v == "{":
            return self.table()
        if k in ("num", "str"):
            self.take(); return v
        if k == "name":
            self.take()
            if v == "nil": return None
            if v == "true": return True
            if v == "false": return False
            parts = [v]
            while self.peek()[1] == "." and self.peek()[0] == "op":
                self.take(); parts.append(self.take()[1])
            return self.resolve(".".join(parts))
        raise ValueError("unexpected %r at token %d" % ((k, v), self.i))
    def table(self):
        self.take("{")
        t, n = Table(), 0
        while self.peek()[1] != "}":
            k, v = self.peek()
            if k == "op" and v == "[":
                self.take(); key = self.expr(); self.take("]"); self.take("="); val = self.expr()
                if val is not None: t.d[key] = val
            elif k == "name" and self.peek(1)[1] == "=" and self.peek(1)[0] == "op":
                self.take(); self.take("="); val = self.expr()
                if val is not None: t.d[v] = val
            else:
                n += 1; val = self.expr()
                if val is not None: t.d[n] = val
            if self.peek()[1] in (",", ";"):
                self.take()
        self.take("}")
        return t

def parse_return_table(text, resolve, after=None):
    """The first `return {` (after the text [after], if given) parsed as a table."""
    at = text.index(after) if after else 0
    m = re.compile(r"return\s*\{").search(text, at)
    toks = tokens(text[m.start() + len("return"):].rstrip())
    p = Parser(toks, resolve)
    return p.table()

def to_py(x):
    """Tables to Python: a list (None for holes) if keys are 1..n integers, else a dict."""
    if isinstance(x, Table):
        keys = list(x.d)
        if keys and all(isinstance(k, int) and k > 0 for k in keys):
            n = max(keys)
            if n <= 4 * len(keys) + 8:
                return [to_py(x.d.get(i)) for i in range(1, n + 1)]
        if not keys:
            return []
        return {k: to_py(v) for k, v in x.d.items()}
    return x
