/*
 * foreverkey.exe: starts WoW Forever's client for the phone's own realm and makes it trust that realm's login key. Written new
 * (15 November 2026) from what Karrz's own launch script (repack/Play-WoWForever.ps1, release v0.1.36.1) documents:
 *
 *  1. The game is started as `Wow.exe -config <wtf>` in its own folder; the wtf (written by the app: a copy of Config.wtf with
 *     SET portal "<name>") is what points the client at the portal.
 *  2. The client keeps a table of 12 login public keys in private memory (12 records of 40 bytes: a number 1..12, a 32-byte
 *     key, a flag byte, a byte that is 0 or 0x7f, two zero bytes). The server announces one of them by region group. This
 *     program finds that table in the running game (by its layout, so it survives client updates) and writes the server's
 *     public key into the record of the realm's region group, and keeps watching in case the client rebuilds the table.
 *     Nothing on disk and no game code is changed.
 *
 * It must run on the games' desktop beside the game (the app starts it as the game's program, through the session's keeper).
 * Settings are read from foreverkey.cfg beside it (lines `name=value`): client (the game's program), config (the wtf's name),
 * key (64 hex characters), group (2-12, not 9). Its log is C:\windows\foreverkey.log (started anew each session).
 *
 * Built with Zig or MinGW for x86_64 Windows, the Windows subsystem (scripts/build-tools.sh).
 */
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#define ENTRIES 12
#define ENTRY_SIZE 40
#define BLOCK_SIZE (ENTRIES * ENTRY_SIZE)
static const unsigned char FLAGS[ENTRIES] = { 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1 };

static FILE *logfile;
static void say(const char *fmt, ...)
{
    if (!logfile) return;
    va_list ap; va_start(ap, fmt);
    SYSTEMTIME t; GetLocalTime(&t);
    fprintf(logfile, "[%02d:%02d:%02d.%03d] ", t.wHour, t.wMinute, t.wSecond, t.wMilliseconds);
    vfprintf(logfile, fmt, ap); fputc('\n', logfile); fflush(logfile);
    va_end(ap);
}

/* true if b[0 .. 480) has the layout of the key table */
static int looks(const unsigned char *b)
{
    for (int e = 0; e < ENTRIES; e++) {
        const unsigned char *o = b + e * ENTRY_SIZE;
        unsigned id = o[0] | (o[1] << 8) | (o[2] << 16) | ((unsigned)o[3] << 24);
        if (id != (unsigned)(e + 1)) return 0;
        if (o[36] != FLAGS[e]) return 0;
        if (o[38] != 0 || o[39] != 0) return 0;
        if (o[37] != 0 && o[37] != 0x7f) return 0;
        int nonzero = 0;
        for (int k = 4; k < 36; k++) if (o[k]) { nonzero = 1; break; }
        if (!nonzero) return 0;
    }
    return 1;
}

/* every table found in the target's private read/write memory; returns the count (at most max) */
static int find_tables(HANDLE h, ULONG_PTR *out, int max)
{
    int count = 0;
    ULONG_PTR addr = 0;
    MEMORY_BASIC_INFORMATION mbi;
    static unsigned char buf[8 * 1024 * 1024];
    while (addr < (ULONG_PTR)0x7FFFFFFF0000ULL) {
        if (!VirtualQueryEx(h, (LPCVOID)addr, &mbi, sizeof mbi)) break;
        SIZE_T size = mbi.RegionSize;
        if (mbi.State == MEM_COMMIT && mbi.Type == MEM_PRIVATE && mbi.Protect == PAGE_READWRITE && size > 0) {
            SIZE_T pos = 0;
            while (pos < size) {
                SIZE_T take = size - pos < sizeof buf ? size - pos : sizeof buf, got = 0;
                if (!ReadProcessMemory(h, (LPCVOID)((ULONG_PTR)mbi.BaseAddress + pos), buf, take, &got) || got < BLOCK_SIZE) break;
                for (SIZE_T i = 0; i + BLOCK_SIZE <= got; i += 4) {
                    if (buf[i] == 1 && buf[i + 1] == 0 && buf[i + 40] == 2 && looks(buf + i)) {
                        if (count < max) out[count] = (ULONG_PTR)mbi.BaseAddress + pos + i;
                        count++;
                    }
                }
                if (pos + take >= size) break;
                pos += take - BLOCK_SIZE; /* overlap, so a table on a chunk border is not missed */
            }
        }
        addr = (ULONG_PTR)mbi.BaseAddress + size;
        if (size == 0) break;
    }
    return count;
}

/* 0 invalid, 1 original, 2 patched */
static int state(HANDLE h, ULONG_PTR table, int group, const unsigned char *key)
{
    unsigned char b[BLOCK_SIZE]; SIZE_T got = 0;
    if (!ReadProcessMemory(h, (LPCVOID)table, b, BLOCK_SIZE, &got) || got != BLOCK_SIZE || !looks(b)) return 0;
    return memcmp(b + (group - 1) * ENTRY_SIZE + 4, key, 32) == 0 ? 2 : 1;
}

static int write_key(HANDLE h, ULONG_PTR table, int group, const unsigned char *key)
{
    SIZE_T w = 0;
    if (!WriteProcessMemory(h, (LPVOID)(table + (group - 1) * ENTRY_SIZE + 4), key, 32, &w) || w != 32) return 0;
    return state(h, table, group, key) == 2;
}

static int hexval(char c) { return c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10 : c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1; }

int WINAPI WinMain(HINSTANCE inst, HINSTANCE prev, LPSTR cmd, int show)
{
    char self[MAX_PATH], dir[MAX_PATH], cfgpath[MAX_PATH];
    GetModuleFileNameA(NULL, self, sizeof self);
    strcpy(dir, self);
    char *slash = strrchr(dir, '\\'); if (slash) *slash = 0;
    snprintf(cfgpath, sizeof cfgpath, "%s\\foreverkey.cfg", dir);

    char wdir[MAX_PATH];
    GetWindowsDirectoryA(wdir, sizeof wdir);
    char logpath[MAX_PATH]; snprintf(logpath, sizeof logpath, "%s\\foreverkey.log", wdir);
    logfile = fopen(logpath, "w");

    char client[MAX_PATH] = "Wow.exe", config[MAX_PATH] = "ForeverLauncher.wtf", keyhex[128] = "";
    int group = 8;
    FILE *cfg = fopen(cfgpath, "r");
    if (!cfg) { say("no %s", cfgpath); return 2; }
    char line[512];
    while (fgets(line, sizeof line, cfg)) {
        char *eq = strchr(line, '='); if (!eq) continue;
        *eq = 0; char *v = eq + 1; v[strcspn(v, "\r\n")] = 0;
        if (!strcmp(line, "client")) snprintf(client, sizeof client, "%s", v);
        else if (!strcmp(line, "config")) snprintf(config, sizeof config, "%s", v);
        else if (!strcmp(line, "key")) snprintf(keyhex, sizeof keyhex, "%s", v);
        else if (!strcmp(line, "group")) group = atoi(v);
    }
    fclose(cfg);
    unsigned char key[32];
    if (strlen(keyhex) != 64) { say("key must be 64 hex characters"); return 2; }
    for (int i = 0; i < 32; i++) {
        int a = hexval(keyhex[i * 2]), b = hexval(keyhex[i * 2 + 1]);
        if (a < 0 || b < 0) { say("key is not hex"); return 2; }
        key[i] = (unsigned char)(a * 16 + b);
    }
    if (group < 2 || group > 12 || group == 9) { say("group %d is not 2-12 (not 9)", group); return 2; }

    char command[2 * MAX_PATH + 64], program[MAX_PATH];
    snprintf(program, sizeof program, "%s\\%s", dir, client);
    snprintf(command, sizeof command, "\"%s\" -config %s", program, config);
    STARTUPINFOA si; PROCESS_INFORMATION pi;
    memset(&si, 0, sizeof si); si.cb = sizeof si;
    say("starting %s (region group %d)", command, group);
    if (!CreateProcessA(program, command, NULL, NULL, FALSE, 0, NULL, dir, &si, &pi)) { say("CreateProcess failed: %lu", GetLastError()); return 3; }

    ULONG_PTR table = 0;
    int waited = 0;
    while (WaitForSingleObject(pi.hProcess, table ? 3000 : 1500) == WAIT_TIMEOUT) {
        if (table) {
            int st = state(pi.hProcess, table, group, key);
            if (st == 2) continue;
            if (st == 1) { say("the client restored its key table: applying the key again"); if (write_key(pi.hProcess, table, group, key)) say("key applied"); continue; }
            table = 0; /* freed: look again */
        }
        ULONG_PTR found[4];
        int n = find_tables(pi.hProcess, found, 4);
        if (n == 1) {
            if (write_key(pi.hProcess, found[0], group, key)) { table = found[0]; say("key applied at %p", (void *)table); }
            else say("could not write the key; trying again");
        } else if (n > 1) say("%d key tables found at once; waiting for one", n);
        else if (!waited) { say("waiting for the client to prepare the login"); waited = 1; }
    }
    DWORD code = 0; GetExitCodeProcess(pi.hProcess, &code);
    say("the game ended with code %lu", code);
    CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    return (int)code;
}
