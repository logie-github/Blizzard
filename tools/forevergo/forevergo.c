/*
 * forevergo.exe: World of Warcraft: Forever's sign-in, with nothing on screen. The app starts it first in the games' desktop
 * (Winlator patch 0009's `exec_wrapper`), in front of the session keeper, with the game's command line carrying -launcherlogin:
 *
 *     forevergo.exe C:\windows\borderless.exe /noframes C:\windows\winhandler.exe ... Wow.exe -launcherlogin
 *
 * The app has already signed in at the phone's realm (its HTTPS login service: POST /bnetserver/login/, then
 * /bnetserver/gameAccounts/) and left the result in C:\windows\forevergo.login: the game account's name on the first line,
 * the login ticket on the second. This program
 *
 * 0. puts the realm's own certificate authority (C:\windows\forevergo.ca, the phone-made CA in PEM) into Windows' trusted
 *    roots (the machine's and the user's Root stores): build 70707 checks the login server's certificate there, and without
 *    it ends the sign-in with ERROR_NETWORK_MODULE_SSL_CERT_CHAIN_VALIDATION_FAILED (1023; the rig, 14 November 2026);
 * 1. reads that file and deletes it;
 * 2. writes the sign-in where the game reads it when it is started with -launcherlogin (as Battle.net does):
 *    HKCU\Software\Blizzard Entertainment\Battle.net\Launch Options\WoW: CONNECTION_STRING (the realm's name),
 *    GAME_ACCOUNT, and WEB_TOKEN (the ticket, protected with CryptProtectData and the game's own entropy);
 * 3. starts the rest of its command line (the keeper, which starts the game), so the game signs in by itself: no login screen;
 * 4. finds the game's program (Wow.exe) as it starts and puts the phone realm's public key into the game's table of realm
 *    keys (its 12 records of 40 bytes: record 8's key) for as long as it runs, which is what lets it accept this realm when
 *    it enters the world;
 *    The table is made only when the game starts connecting to the realm, and the first connection is checked at once:
 *    a scan of the game's memory (1.6 GB, seconds) finds it too late for that one (the rig: "You have been disconnected",
 *    Reconnect). The table stays, so once the key is in, a failed first connection is retried by pressing Enter in the
 *    game (its Reconnect button), up to three times: when the game is not connected to the realm's world server (Windows'
 *    TCP table, by the game's process), or once when that table can't be read (Android may keep it from Wine);
 * 5. removes the sign-in from the registry when what it started has ended, and ends with its exit code.
 *
 * Steps 2 to 4 follow ForeverNXT's local launcher 1.2.1 (GPL-2.0-or-later, its src/Auth.cpp, KeyStore.cpp and
 * KeyMonitor.cpp, itself adapted from the Forever Launcher at github.com/jibay442/forever_docker): the same registry
 * values, entropy, key table and checks. Unlike it, this one also looks in shared (mapped) read/write memory, where Wine
 * keeps the table on some builds.
 *
 * Its log (C:\windows\forevergo.log) goes into the app's reports. Built with Zig for x86_64 Windows (scripts/build-tools.sh),
 * the Windows subsystem: no console.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later
 */
#include <winsock2.h>
#include <windows.h>
#include <wincrypt.h>
#include <iphlpapi.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <tlhelp32.h>

#define LOGIN_FILE L"C:\\windows\\forevergo.login"
#define CA_FILE L"C:\\windows\\forevergo.ca"
#define LOG_FILE L"C:\\windows\\forevergo.log"
#define REGISTRY_PATH L"Software\\Blizzard Entertainment\\Battle.net\\Launch Options\\WoW"
#define PORTAL L"trinity.actual.battle.net"

static HANDLE log_file = INVALID_HANDLE_VALUE;
static DWORD log_started;

static void note(const char *format, ...)
{
    char text[1100];
    DWORD written;
    va_list args;
    int length, i;

    if (log_file == INVALID_HANDLE_VALUE) return;
    length = wsprintfA(text, "%lu.%03lu ", (GetTickCount() - log_started) / 1000, (GetTickCount() - log_started) % 1000);
    va_start(args, format);
    length += wvsprintfA(text + length, format, args);
    va_end(args);
    for (i = 0; i < length; i++) if (text[i] == '\r' || text[i] == '\n') text[i] = ' ';
    text[length++] = '\n';
    WriteFile(log_file, text, (DWORD)length, &written, NULL);
}

/* The game's own entropy for WEB_TOKEN (Auth.cpp: TicketEntropy). */
static const BYTE ticket_entropy[16] = {0xC8, 0x76, 0xF4, 0xAE, 0x4C, 0x95, 0x2E, 0xFE, 0xF2, 0xFA, 0x0F, 0x54, 0x19, 0xC0, 0x9C, 0x43};

/* The key table (KeyStore.cpp): 12 records of 40 bytes, each its number (1-12, 32 bits), a 32-byte key, a flag byte and three bytes. */
#define ENTRY_SIZE 40
#define ENTRY_COUNT 12
#define STORE_SIZE (ENTRY_SIZE * ENTRY_COUNT)
#define REPLACED 7
static const char *const key_hex[ENTRY_COUNT] = {
    "9B0671C815DFF513BFD4A2B26AE1F84EC9106841B2FB620DB65F6ADE7C21AD06",
    "112451B9843C2799E4750AA3D9B9AFABF536A645B863C4ADB2078B932B354E04",
    "A6B858485748BF38BE193517AB90F8DE169EFF0989EA9360DB346A378B0FFE15",
    "50FFDEB807F8FF73A299A16000AA6575C5945BE875ADFC8795374ED3415249AC",
    "9F842D078755647C008E5FE3E12B839A981DE02A1F520CB2545CC04CD2323E0E",
    "B8CC75864D8EF461D8DD6AA7425E2C63C24D3982066B8D773A1549BFE24E05EE",
    "76BB7BBDD9F34E124A4573C3AA227E3C87CC603506697D054F6FDEC342E56EBF",
    "1FD6DD8FA0EC30D39E3F72E755B8A045BDE0F70449DC71008B767C2EAA89FB9F",
    "15D618BD7DB577BD9A8D45769C59E4FC631633BF447398A4B489B4C26FBC03AD",
    "B34EC592D2AC4993F5FFC85B15C3DA9078694051CB224345592AF7136D796C99",
    "9E91586DD4B115AB0568B21959E181F6545910BC5E2F30B8975CA09D7BC3EFCE",
    "769C824A1DADD19AEEFA420414D1732DAF44537F98AA229FC5477BCA55F9D59A",
};
/* The phone realm's public key (the stock key of the realm's source; ForeverLauncher.PUBLIC_KEY in the app). */
static const char server_hex[] = "02596F0D0C061A8B30745988FD72C59E29EC367FB0F341F28E0F08D037BAFC69";
static const BYTE flags[ENTRY_COUNT] = {1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1};
static BYTE keys[ENTRY_COUNT][32], server_key[32];

static int nibble(char c) { return c <= '9' ? c - '0' : c - 'A' + 10; }
static void unhex(const char *hex, BYTE *out) { int i; for (i = 0; i < 32; i++) out[i] = (BYTE)(nibble(hex[2 * i]) << 4 | nibble(hex[2 * i + 1])); }

enum { INVALID, ORIGINAL, PATCHED };

static int store_state(const BYTE *data)
{
    int i, patched = 0;
    for (i = 0; i < ENTRY_COUNT; i++) {
        const BYTE *entry = data + i * ENTRY_SIZE;
        int original, local;
        if (entry[0] != i + 1 || entry[1] || entry[2] || entry[3]) return INVALID;
        original = memcmp(entry + 4, keys[i], 32) == 0;
        local = i == REPLACED && memcmp(entry + 4, server_key, 32) == 0;
        if (!original && !local) return INVALID;
        if (entry[36] != flags[i] || entry[38] || entry[39]) return INVALID;
        if (i == REPLACED) patched = local;
    }
    return patched ? PATCHED : ORIGINAL;
}

static int writable(const MEMORY_BASIC_INFORMATION *info)
{
    return info->State == MEM_COMMIT && (info->Type == MEM_PRIVATE || info->Type == MEM_MAPPED) && info->Protect == PAGE_READWRITE;
}

/* Every key table in the game's read/write memory: up to [max] addresses into [found]; how many. */
#define CHUNK (8u << 20)
static BYTE *buffer;
static int scan(HANDLE process, ULONG_PTR *found, int max, DWORD *regions, SIZE_T *bytes)
{
    ULONG_PTR cursor = 0;
    int count = 0;
    *regions = 0; *bytes = 0;
    for (;;) {
        MEMORY_BASIC_INFORMATION info;
        ULONG_PTR base, end, at;
        if (!VirtualQueryEx(process, (LPCVOID)cursor, &info, sizeof(info))) break;
        base = (ULONG_PTR)info.BaseAddress;
        end = base + info.RegionSize;
        if (end <= cursor) break;
        cursor = end;
        if (!writable(&info)) continue;
        (*regions)++;
        for (at = base; at < end;) {
            SIZE_T take = end - at < CHUNK ? end - at : CHUNK, got = 0, i;
            if (ReadProcessMemory(process, (LPCVOID)at, buffer, take, &got) && got >= STORE_SIZE) {
                *bytes += got;
                for (i = 0; i + STORE_SIZE <= got; i += 4) {
                    if (buffer[i] != 1 || buffer[i + 4] != keys[0][0] || buffer[i + ENTRY_SIZE] != 2) continue;
                    if (store_state(buffer + i) != INVALID && count < max) found[count++] = at + i;
                }
            }
            if (take < CHUNK) break;
            at += take - (STORE_SIZE - 4);
        }
    }
    return count;
}

static int read_store(HANDLE process, ULONG_PTR address)
{
    BYTE store[STORE_SIZE];
    SIZE_T got = 0;
    if (!ReadProcessMemory(process, (LPCVOID)address, store, sizeof(store), &got) || got != sizeof(store)) return INVALID;
    return store_state(store);
}

static int patch(HANDLE process, ULONG_PTR address)
{
    SIZE_T written = 0;
    DWORD old;
    int state = read_store(process, address);
    if (state != ORIGINAL) return state == PATCHED;
    if (!WriteProcessMemory(process, (LPVOID)(address + REPLACED * ENTRY_SIZE + 4), server_key, 32, &written) || written != 32) {
        /* A mapped view may need its protection lifted for another process's write. */
        if (VirtualProtectEx(process, (LPVOID)(address + REPLACED * ENTRY_SIZE + 4), 32, PAGE_READWRITE, &old))
            WriteProcessMemory(process, (LPVOID)(address + REPLACED * ENTRY_SIZE + 4), server_key, 32, &written);
    }
    return read_store(process, address) == PATCHED;
}

/* The registry values, each written and later deleted. */
static HKEY launch_key;
static int write_login(const char *account, const char *ticket)
{
    WCHAR wide[256];
    DATA_BLOB input, entropy, out;
    LONG error;
    int n;

    error = RegCreateKeyExW(HKEY_CURRENT_USER, REGISTRY_PATH, 0, NULL, REG_OPTION_NON_VOLATILE, KEY_QUERY_VALUE | KEY_SET_VALUE, NULL, &launch_key, NULL);
    if (error != ERROR_SUCCESS) { note("registry: cannot open the launch options (%ld)", error); return 0; }
    input.cbData = (DWORD)strlen(ticket); input.pbData = (BYTE *)ticket;
    entropy.cbData = sizeof(ticket_entropy); entropy.pbData = (BYTE *)ticket_entropy;
    out.cbData = 0; out.pbData = NULL;
    if (!CryptProtectData(&input, L"ForeverNXT local login", &entropy, NULL, NULL, CRYPTPROTECT_UI_FORBIDDEN, &out)) {
        note("CryptProtectData failed (%lu)", GetLastError());
        return 0;
    }
    n = MultiByteToWideChar(CP_UTF8, 0, account, -1, wide, 256);
    if (RegSetValueExW(launch_key, L"CONNECTION_STRING", 0, REG_SZ, (const BYTE *)PORTAL, sizeof(PORTAL)) != ERROR_SUCCESS ||
        RegSetValueExW(launch_key, L"GAME_ACCOUNT", 0, REG_SZ, (const BYTE *)wide, (DWORD)(n * sizeof(WCHAR))) != ERROR_SUCCESS ||
        RegSetValueExW(launch_key, L"WEB_TOKEN", 0, REG_BINARY, out.pbData, out.cbData) != ERROR_SUCCESS) {
        note("registry: cannot write the sign-in");
        LocalFree(out.pbData);
        return 0;
    }
    SecureZeroMemory(out.pbData, out.cbData);
    LocalFree(out.pbData);
    note("sign-in written for game account %s (ticket %d characters)", account, (int)strlen(ticket));
    return 1;
}

static void remove_login(void)
{
    if (!launch_key) return;
    RegDeleteValueW(launch_key, L"WEB_TOKEN");
    RegDeleteValueW(launch_key, L"GAME_ACCOUNT");
    RegDeleteValueW(launch_key, L"CONNECTION_STRING");
    RegCloseKey(launch_key);
    launch_key = NULL;
}

/* The login file: the game account, then the ticket; deleted once read. */
static int world_port;
static int read_login(char *account, int account_size, char *ticket, int ticket_size)
{
    char text[4096];
    DWORD got = 0;
    char *line2, *end;
    HANDLE file = CreateFileW(LOGIN_FILE, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (file == INVALID_HANDLE_VALUE) { note("no sign-in from the app (%lu)", GetLastError()); return 0; }
    ReadFile(file, text, sizeof(text) - 1, &got, NULL);
    CloseHandle(file);
    DeleteFileW(LOGIN_FILE);
    text[got] = 0;
    line2 = strchr(text, '\n');
    if (!line2) { note("sign-in file has one line"); return 0; }
    *line2++ = 0;
    if (line2 > text + 1 && line2[-2] == '\r') line2[-2] = 0;
    for (end = line2; *end && *end != '\r' && *end != '\n'; end++) {}
    if (*end) { char *port = end + 1; while (*port == '\r' || *port == '\n') port++; world_port = atoi(port); }
    *end = 0;
    if (!*text || !*line2 || lstrlenA(text) >= account_size || lstrlenA(line2) >= ticket_size) { note("sign-in file malformed"); return 0; }
    lstrcpyA(account, text);
    lstrcpyA(ticket, line2);
    SecureZeroMemory(text, sizeof(text));
    return 1;
}

/* The realm's CA into the trusted roots ([CA_FILE], PEM): how many stores took it. */
static int trust_ca(void)
{
    char pem[16384];
    BYTE der[8192];
    DWORD got = 0, size = sizeof(der);
    int stores = 0, i;
    static const DWORD where[2] = {CERT_SYSTEM_STORE_LOCAL_MACHINE, CERT_SYSTEM_STORE_CURRENT_USER};
    HANDLE file = CreateFileW(CA_FILE, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (file == INVALID_HANDLE_VALUE) { note("no realm CA (%lu)", GetLastError()); return 0; }
    ReadFile(file, pem, sizeof(pem) - 1, &got, NULL);
    CloseHandle(file);
    pem[got] = 0;
    if (!CryptStringToBinaryA(pem, 0, CRYPT_STRING_BASE64HEADER, der, &size, NULL, NULL)) { note("realm CA unreadable (%lu)", GetLastError()); return 0; }
    for (i = 0; i < 2; i++) {
        HCERTSTORE store = CertOpenStore(CERT_STORE_PROV_SYSTEM_W, 0, 0, where[i] | CERT_STORE_OPEN_EXISTING_FLAG, L"Root");
        if (!store) store = CertOpenStore(CERT_STORE_PROV_SYSTEM_W, 0, 0, where[i], L"Root");
        if (!store) { note("Root store %d: cannot open (%lu)", i, GetLastError()); continue; }
        if (CertAddEncodedCertificateToStore(store, X509_ASN_ENCODING, der, size, CERT_STORE_ADD_REPLACE_EXISTING, NULL)) stores++;
        else note("Root store %d: cannot add (%lu)", i, GetLastError());
        CertCloseStore(store, 0);
    }
    note("realm CA trusted in %d of 2 Root stores", stores);
    return stores;
}

/* The command line after this program's own name: what to start. */
static WCHAR *rest_of_command_line(void)
{
    WCHAR *p = GetCommandLineW();
    if (*p == L'"') { p++; while (*p && *p != L'"') p++; if (*p) p++; }
    else while (*p && *p != L' ' && *p != L'\t') p++;
    while (*p == L' ' || *p == L'\t') p++;
    return p;
}

/* The game's programs: _forever_\Wow.exe, the beta's and test's. */
static const WCHAR *const game_names[] = {L"Wow.exe", L"WowB.exe", L"WowT.exe", NULL};

/* A running game program other than [skip]: opened for the key, or NULL. */
static HANDLE find_game(DWORD skip, DWORD *pid)
{
    PROCESSENTRY32W entry;
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0), process = NULL;
    BOOL more;
    int i;
    if (snapshot == INVALID_HANDLE_VALUE) return NULL;
    entry.dwSize = sizeof(entry);
    for (more = Process32FirstW(snapshot, &entry); more && !process; more = Process32NextW(snapshot, &entry)) {
        if (entry.th32ProcessID == skip) continue;
        for (i = 0; game_names[i]; i++) if (!lstrcmpiW(entry.szExeFile, game_names[i])) break;
        if (!game_names[i]) continue;
        process = OpenProcess(PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION | SYNCHRONIZE, FALSE, entry.th32ProcessID);
        if (process) { *pid = entry.th32ProcessID; note("game program %ls (pid %lu)", entry.szExeFile, *pid); }
        else note("cannot open %ls (pid %lu): %lu", entry.szExeFile, entry.th32ProcessID, GetLastError());
    }
    CloseHandle(snapshot);
    return process;
}

/* Whether the game [pid] is connected to the realm's world server: 1, 0, or -1 when Windows' TCP table can't tell. */
static int world_connected(DWORD pid)
{
    static BYTE table[256 * 1024];
    DWORD size = sizeof(table), i, mine = 0;
    MIB_TCPTABLE_OWNER_PID *t = (MIB_TCPTABLE_OWNER_PID *)table;
    if (!world_port || GetExtendedTcpTable(t, &size, FALSE, AF_INET, TCP_TABLE_OWNER_PID_ALL, 0) != NO_ERROR) return -1;
    for (i = 0; i < t->dwNumEntries; i++) {
        if (t->table[i].dwOwningPid != pid) continue;
        mine++;
        if (t->table[i].dwState == MIB_TCP_STATE_ESTAB && ntohs((u_short)t->table[i].dwRemotePort) == world_port) return 1;
    }
    return mine ? 0 : -1;
}

/* Enter in the game's window (on the disconnected screen: Reconnect). */
static BOOL CALLBACK press_enter(HWND hwnd, LPARAM lparam)
{
    DWORD owner = 0;
    GetWindowThreadProcessId(hwnd, &owner);
    if (owner != (DWORD)lparam || !IsWindowVisible(hwnd) || GetWindow(hwnd, GW_OWNER)) return TRUE;
    SetForegroundWindow(hwnd);
    PostMessageW(hwnd, WM_KEYDOWN, VK_RETURN, 0x001C0001);
    PostMessageW(hwnd, WM_CHAR, L'\r', 0x001C0001);
    PostMessageW(hwnd, WM_KEYUP, VK_RETURN, 0xC01C0001);
    return FALSE;
}

/* One run of the game: record 8 of its key table kept at the realm's key until it ends or [outer] does. */
static void keep_key(HANDLE game, DWORD pid, HANDLE outer)
{
    HANDLE both[2];
    ULONG_PTR known = 0, found[8];
    DWORD regions, started = GetTickCount(), last_scan = 0, interval = 150, code = 0;
    SIZE_T bytes;
    int scans = 0, reported_none = 0, ever = 0, presses = 0;
    DWORD found_at = 0;

    both[0] = game; both[1] = outer;
    while (WaitForMultipleObjects(2, both, FALSE, known ? 250 : 100) == WAIT_TIMEOUT) {
        if (known) {
            int state = read_store(game, known);
            /* The first connection, checked before the key was in, failed: Reconnect (2 s after, then every 20 s, three times at most). */
            if (state == PATCHED && presses < 3 && GetTickCount() - found_at >= (presses ? 20000u : 2000u)) {
                int connected = world_connected(pid);
                if (connected == 1 || (connected == -1 && presses)) presses = 3;
                else {
                    EnumWindows(press_enter, (LPARAM)pid);
                    presses++;
                    found_at = GetTickCount();
                    note("not connected to the realm (%s): Enter pressed (Reconnect), %d of 3", connected ? "can't tell" : "no connection", presses);
                }
            }
            if (state == PATCHED) continue;
            if (state == ORIGINAL && patch(game, known)) { note("key table at %p was reset; key put back", (void *)known); continue; }
            note("key table at %p gone (state %d); looking again", (void *)known, state);
            known = 0;
        }
        if (GetTickCount() - last_scan < interval) continue;
        {
            DWORD t0 = GetTickCount(), took;
            int count = scan(game, found, 8, &regions, &bytes);
            took = GetTickCount() - t0;
            last_scan = GetTickCount();
            scans++;
            if (count == 1) {
                if (patch(game, found[0])) {
                    known = found[0];
                    ever = 1;
                    found_at = GetTickCount();
                    note("key put in the table at %p after %lu s (scan %d: %lu regions, %lu MB, %lu ms)", (void *)known,
                         (GetTickCount() - started) / 1000, scans, regions, (DWORD)(bytes >> 20), took);
                } else note("table at %p could not be written (%lu)", (void *)found[0], GetLastError());
            } else if (count > 1) {
                note("%d key tables found; none changed", count);
            } else if (!reported_none || scans % 40 == 0) {
                note("no key table yet (scan %d: %lu regions, %lu MB, %lu ms)", scans, regions, (DWORD)(bytes >> 20), took);
                reported_none = 1;
            }
            /* A scan costs; while none is found, look less often as time goes on (at most every 2 s). */
            if (!known && interval < 2000) interval += 50;
        }
    }
    if (WaitForSingleObject(game, 0) == WAIT_OBJECT_0) {
        GetExitCodeProcess(game, &code);
        note("game program ended (code 0x%08lX) after %lu s%s", code, (GetTickCount() - started) / 1000, ever ? "" : "; its key table was never found");
    }
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous, LPSTR command, int show)
{
    WCHAR *rest = rest_of_command_line();
    char account[256], ticket[2048];
    STARTUPINFOW startup;
    PROCESS_INFORMATION child;
    DWORD code = 1, pid = 0, last_pid = 0;
    int i;

    (void)instance; (void)previous; (void)command; (void)show;
    log_started = GetTickCount();
    log_file = CreateFileW(LOG_FILE, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, 0, NULL);
    for (i = 0; i < ENTRY_COUNT; i++) unhex(key_hex[i], keys[i]);
    unhex(server_hex, server_key);
    if (!*rest) { note("usage: forevergo.exe <command line>"); return 2; }

    trust_ca();
    if (read_login(account, sizeof(account), ticket, sizeof(ticket))) write_login(account, ticket);
    SecureZeroMemory(ticket, sizeof(ticket));

    memset(&startup, 0, sizeof(startup));
    startup.cb = sizeof(startup);
    if (!CreateProcessW(NULL, rest, NULL, NULL, FALSE, 0, NULL, NULL, &startup, &child)) {
        note("cannot start %ls (%lu)", rest, GetLastError());
        remove_login();
        return 3;
    }
    note("started %ls (pid %lu)", rest, child.dwProcessId);
    buffer = VirtualAlloc(NULL, CHUNK, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);

    /* Each run of the game while what it started runs (a game restarted from its own menu is a new program). */
    while (WaitForSingleObject(child.hProcess, 250) == WAIT_TIMEOUT) {
        HANDLE game = find_game(last_pid, &pid);
        if (!game) continue;
        last_pid = pid;
        keep_key(game, pid, child.hProcess);
        CloseHandle(game);
    }
    GetExitCodeProcess(child.hProcess, &code);
    note("ended (code 0x%08lX)", code);
    remove_login();
    return (int)code;
}
