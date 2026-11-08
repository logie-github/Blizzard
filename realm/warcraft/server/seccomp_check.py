#!/usr/bin/env python3
"""Android's seccomp policy for apps on this machine's architecture (arm64, as on the phone, or
x86_64), from android-seccomp/ (AOSP bionic's lists).

    seccomp_check.py filter         strace's -e trace= list: every call apps may not make, and
                                    the calls that start processes (to know which are the server's)
    seccomp_check.py check DIR LOG...
                                    list the calls in strace logs that apps may not make, made by
                                    programs from DIR (the server's), and exit 1 if there are any

CI runs the server under strace with a filter that only stops on calls outside the allowed list,
so any call in its log would get the server killed on a phone. The test machine's own shell runs
ctl.sh there (on the phone it's Android's), so calls before a process runs one of the server's
programs don't count.
"""
import os
import platform
import re
import sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "android-seccomp")
# The phone is arm64; on an x86_64 test machine, Android's x86_64 policy (same idea, x86 names).
ARCH = {"all", "lp64", "x86_64" if platform.machine() == "x86_64" else "arm64"}


def names(filename):
    out = set()
    with open(os.path.join(HERE, filename)) as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line or "(" not in line:
                continue
            head, _, rest = line.partition("(")
            arches = rest.rsplit(")", 1)[-1].split()
            if not arches or not ARCH & set(arches[-1].split(",")):
                continue
            func = head.split()[-1]
            parts = func.split(":")
            name = parts[1] if len(parts) > 1 else parts[0].split("|")[0]
            out.add(name)
    return out


def allowed():
    return (names("SYSCALLS.TXT") | names("SECCOMP_ALLOWLIST_COMMON.TXT") | names("SECCOMP_ALLOWLIST_APP.TXT")) \
        - names("SECCOMP_BLOCKLIST_COMMON.TXT") - names("SECCOMP_BLOCKLIST_APP.TXT")


SPAWN = {"clone", "clone3", "fork", "vfork", "execve", "execveat"}


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "allowed":
        print(",".join(sorted(allowed())))
    elif len(sys.argv) == 2 and sys.argv[1] == "filter":
        # Negated: trace everything but the allowed calls (minus the spawning ones). "?" lets strace
        # skip names it doesn't know.
        print("!" + ",".join("?" + name for name in sorted(allowed() - SPAWN)))
    elif len(sys.argv) >= 4 and sys.argv[1] == "check":
        server_dir = sys.argv[2].rstrip("/") + "/"
        ok = allowed()
        found = {}
        server = set()
        call = re.compile(r"^(\d+)\s+(?:<\.\.\. )?([a-z_0-9]+)(?:\(| resumed>)(.*)$")
        for path in sys.argv[3:]:
            with open(path, errors="replace") as f:
                for line in f:
                    m = call.match(line)
                    if not m:
                        continue
                    pid, name, rest = m.group(1), m.group(2), m.group(3)
                    if name in ("execve", "execveat") and "resumed>" not in line:
                        target = re.search(r'"([^"]*)"', rest)
                        if target and target.group(1).startswith(server_dir):
                            server.add(pid)
                        elif target:
                            server.discard(pid)
                        continue
                    if name in ("clone", "clone3", "fork", "vfork"):
                        child = re.search(r"= (\d+)", rest)
                        if child and pid in server:
                            server.add(child.group(1))
                        continue
                    if pid in server and name not in ok:
                        found.setdefault(name, line.strip()[:160])
        for name, example in sorted(found.items()):
            print(f"not allowed on Android: {name}    e.g. {example}")
        print(f"{len(server)} server processes and threads checked")
        sys.exit(1 if found else 0)
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
