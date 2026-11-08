Android's seccomp policy for apps, from AOSP bionic (`libc/`, main branch, fetched 2026-10-11,
https://android.googlesource.com/platform/bionic/+/refs/heads/main/libc/). Android kills an app's
process (SIGSYS) when it makes a system call outside this policy, and the server's programs run as
the app. `../seccomp_check.py` turns these files into the list of system calls arm64 apps may make,
for CI's test of the server (scripts/test-warcraft-server.sh).

The allowed set is SYSCALLS.TXT + SECCOMP_ALLOWLIST_COMMON.TXT + SECCOMP_ALLOWLIST_APP.TXT
- SECCOMP_BLOCKLIST_COMMON.TXT - SECCOMP_BLOCKLIST_APP.TXT, for the arm64 entries.
