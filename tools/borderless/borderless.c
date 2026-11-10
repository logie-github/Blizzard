/*
 * borderless.exe: the games' session keeper. The app starts every Windows game through it:
 *
 *     explorer /desktop=shell,WxH  C:\windows\borderless.exe [/noframes]  C:\windows\winhandler.exe /dir D:\game "Game.exe" args
 *
 * It starts the rest of its command line (Winlator's winhandler.exe, which starts the game), and for as long as the game
 * runs it does three things that nothing else in the games' Windows does:
 *
 * 1. The games' desktop takes the mouse. A game that locks the cursor to its window (ClipCursor: Warcraft III) makes Wine
 *    report the mouse without a window, and Wine's server gives such input to the window station's *input desktop*: the
 *    first desktop made there ("Default"), not the virtual desktop the games run on ("shell"), until some input with a
 *    window (a key, a click on an unlocked window) happens to switch it. A game that locks the cursor from its first
 *    moment never got a click or a move on the phone (Warcraft III, 9 November 2026: "it won't let me click"). Read off
 *    Winlator's own X server run on a desktop (tools/xrig): `send_hardware_message( win=0 ... )` answered with a cursor
 *    that never left 0,0, and after one SwitchDesktop the same click arrived. So: SwitchDesktop to this desktop, at the
 *    start and again every tick.
 *
 * 2. No title bars. The games' Windows is Wine's virtual desktop, where Wine draws every window's title bar and frame
 *    itself (no window manager: the X server is Winlator's) and has no setting against it (10.10 knows no "Decorated").
 *    A game started in a window at the screen's size (Warcraft III 1.2x's -window, Diablo II's -w) sat under its own
 *    bar, the picture pushed down and cut at the bottom. The caption and frame styles are taken off every top-level
 *    window of the games (not Wine's own programs, not dialog boxes) and the window is put at the top left at its client
 *    area's size, so it is the whole screen. Not with /noframes (World of Warcraft, an installer).
 *
 * 3. The session ends with the game. winhandler.exe stays for as long as the desktop does, and the desktop for as long
 *    as winhandler.exe: a game that was quit from its own menu (or crashed) left a black screen until the person found
 *    the app's menu. When no program of the game's is left for three seconds (or none ever started in a minute and a
 *    half), winhandler.exe is ended and this program exits: the desktop closes, Wine exits, and the app returns to the
 *    launcher.
 *
 * Built with Zig for x86_64 Windows (scripts/build-tools.sh), the Windows subsystem: no console.
 */
#include <windows.h>
#include <tlhelp32.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/*
 * What it did, for the app's reports (C:\windows\borderless.log, a few lines a session, started anew each time): the
 * desktop switch, what it started, each window it took the frame off, the game's programs as they come and go, why it ended.
 */
static HANDLE log_file = INVALID_HANDLE_VALUE;

static void note(const char *format, ...)
{
    char text[600];
    DWORD written;
    va_list args;
    int length;

    if (log_file == INVALID_HANDLE_VALUE) return;
    length = wsprintfA(text, "%lu ", GetTickCount() / 1000);
    va_start(args, format);
    length += wvsprintfA(text + length, format, args);
    va_end(args);
    text[length++] = '\n';
    WriteFile(log_file, text, (DWORD)length, &written, NULL);
}

/* Wine's own programs and this session's helpers: never the game's. */
static const WCHAR *const kept[] = {
    L"explorer.exe", L"winhandler.exe", L"borderless.exe", L"services.exe", L"winedevice.exe", L"plugplay.exe", L"rpcss.exe",
    L"svchost.exe", L"conhost.exe", L"start.exe", L"wineboot.exe", L"winemenubuilder.exe", L"tabtip.exe", L"wfm.exe", NULL};

/* Wine's own windows, by class: the taskbar, the desktop, dialog boxes. */
static const char *const kept_classes[] = {"Shell_TrayWnd", "Progman", "#32770", NULL};

static const DWORD FRAME_STYLES = WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU | WS_BORDER | WS_DLGFRAME;
static const DWORD FRAME_EXSTYLES = WS_EX_DLGMODALFRAME | WS_EX_CLIENTEDGE | WS_EX_STATICEDGE | WS_EX_WINDOWEDGE;

static int kept_name(const WCHAR *path)
{
    const WCHAR *name = wcsrchr(path, L'\\');
    int i;
    name = name ? name + 1 : path;
    for (i = 0; kept[i]; i++) if (!lstrcmpiW(name, kept[i])) return 1;
    return 0;
}

/*
 * Whether the window is one of Wine's own programs'. A process that cannot be opened (Wine refused the game's, a 32-bit
 * one, with access denied on 9 November 2026, while its own opened) is taken for the game's.
 */
static int kept_program(HWND hwnd)
{
    DWORD pid = 0;
    WCHAR path[MAX_PATH];
    DWORD size = MAX_PATH;
    HANDLE process;

    GetWindowThreadProcessId(hwnd, &pid);
    if (!pid) return 0;
    if (pid == GetCurrentProcessId()) return 1;
    process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (!process) return 0;
    if (!QueryFullProcessImageNameW(process, 0, path, &size)) { CloseHandle(process); return 0; }
    CloseHandle(process);
    return kept_name(path);
}

static BOOL CALLBACK strip(HWND hwnd, LPARAM lparam)
{
    char cls[64] = "";
    DWORD style, exstyle;
    RECT client;
    int width, height, screen_width, screen_height, i;

    if (!IsWindowVisible(hwnd) || GetAncestor(hwnd, GA_PARENT) != GetDesktopWindow()) return TRUE;
    style = (DWORD)GetWindowLongW(hwnd, GWL_STYLE);
    screen_width = GetSystemMetrics(SM_CXSCREEN);
    screen_height = GetSystemMetrics(SM_CYSCREEN);
    if (!(style & (WS_CAPTION | WS_THICKFRAME))) {
        /*
         * A window already without a frame that hangs a little over the screen's edge at the top left: a game that sized
         * its frameless window to the outer size its framed one had (Diablo II, 806x612 again as a game began) is trimmed
         * to the screen. The game draws at the top left as before; nothing of it is lost.
         */
        RECT rect;
        if (GetWindowRect(hwnd, &rect) && rect.left == 0 && rect.top == 0 &&
            rect.right >= screen_width && rect.right <= screen_width + 48 && rect.bottom >= screen_height && rect.bottom <= screen_height + 48 &&
            (rect.right > screen_width || rect.bottom > screen_height) && !kept_program(hwnd)) {
            SetWindowPos(hwnd, NULL, 0, 0, screen_width, screen_height, SWP_NOZORDER | SWP_NOACTIVATE | SWP_NOOWNERZORDER);
            note("trimmed a frameless window of %ldx%ld to the screen (%dx%d)", rect.right, rect.bottom, screen_width, screen_height);
            (*(int *)lparam)++;
        }
        return TRUE;
    }
    /* Dialog boxes (a message, the game's own error) keep their frame: they are small and want to be seen as what they are. */
    GetClassNameA(hwnd, cls, sizeof(cls));
    for (i = 0; kept_classes[i]; i++) if (!lstrcmpA(cls, kept_classes[i])) return TRUE;
    if (!GetClientRect(hwnd, &client) || client.right < 320 || client.bottom < 200) return TRUE;
    if (kept_program(hwnd)) return TRUE;

    /*
     * The client area where it was, the whole window now: at the top left of the screen, the client area's size. A game
     * that filled the screen's width meant the screen: its height is made the screen's too (Diablo II's 1.13 window, made
     * for another Windows' bar, was 806x612 with a client area of 800x587 on an 800x600 screen: 13 lines of the game cut).
     */
    width = client.right;
    height = client.bottom;
    if (width >= screen_width - 8 && width <= screen_width) width = screen_width;
    if (width == screen_width && height >= screen_height - 48 && height <= screen_height) height = screen_height;
    /*
     * A window the person could have dragged larger (a sizing frame) is one the game draws at whatever size it is given:
     * it gets the whole screen. Warcraft III 1.2x opens its window at 592x423 whatever its resolution setting says, and
     * the launcher stretched that small picture over the phone's screen, soft; given the screen's size the game draws at
     * the screen's own resolution. A window of a fixed size (Diablo II's) keeps it: its game would draw in a corner.
     */
    if (style & WS_THICKFRAME) { width = screen_width; height = screen_height; }

    exstyle = (DWORD)GetWindowLongW(hwnd, GWL_EXSTYLE);
    SetWindowLongW(hwnd, GWL_STYLE, (LONG)(style & ~FRAME_STYLES));
    SetWindowLongW(hwnd, GWL_EXSTYLE, (LONG)(exstyle & ~FRAME_EXSTYLES));
    SetWindowPos(hwnd, NULL, 0, 0, width, height, SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED | SWP_NOOWNERZORDER);
    note("frame off a window of class '%s'%s: client %ldx%ld, now %dx%d at the top left (screen %dx%d)", cls, (style & WS_THICKFRAME) ? " (resizable)" : "",
         client.right, client.bottom, width, height, screen_width, screen_height);
    (*(int *)lparam)++;
    return TRUE;
}

/* How many programs of the game's are running: every process but Wine's own and the session's helpers. The first one's name goes into [name] (64 characters). */
static int game_processes(char *name)
{
    PROCESSENTRY32W entry;
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    DWORD self = GetCurrentProcessId();
    int count = 0;

    name[0] = 0;
    if (snapshot == INVALID_HANDLE_VALUE) return -1;
    entry.dwSize = sizeof(entry);
    if (Process32FirstW(snapshot, &entry)) {
        do {
            if (entry.th32ProcessID && entry.th32ProcessID != self && !kept_name(entry.szExeFile)) {
                if (!count) WideCharToMultiByte(CP_ACP, 0, entry.szExeFile, -1, name, 64, NULL, NULL);
                count++;
            }
        } while (Process32NextW(snapshot, &entry));
    }
    CloseHandle(snapshot);
    return count;
}

/* The command line after this program's own name and switches: what to start. Sets *frames to 0 for /noframes. */
static WCHAR *rest_of_command_line(int *frames)
{
    WCHAR *p = GetCommandLineW();
    if (*p == L'"') { p++; while (*p && *p != L'"') p++; if (*p) p++; }
    else while (*p && *p != L' ' && *p != L'\t') p++;
    for (;;) {
        while (*p == L' ' || *p == L'\t') p++;
        if (!_wcsnicmp(p, L"/noframes", 9) && (p[9] == 0 || p[9] == L' ' || p[9] == L'\t')) { *frames = 0; p += 9; continue; }
        break;
    }
    return p;
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous, LPSTR command, int show)
{
    int frames = 1, seen = 0, last_games = -2, helper_gone = 0;
    DWORD started = GetTickCount(), last_seen = started, exit_code = 0;
    WCHAR *rest = rest_of_command_line(&frames);
    PROCESS_INFORMATION child;
    HDESK desktop = GetThreadDesktop(GetCurrentThreadId());
    char desktop_name[64] = "", game[64] = "";
    DWORD needed = 0;
    BOOL switched;

    (void)instance; (void)previous; (void)command; (void)show;
    memset(&child, 0, sizeof(child));
    log_file = CreateFileA("C:\\windows\\borderless.log", GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    GetUserObjectInformationA(desktop, UOI_NAME, desktop_name, sizeof(desktop_name), &needed);
    switched = SwitchDesktop(desktop);
    note("session keeper: desktop '%s' takes the input: %s; frames %s; screen %dx%d", desktop_name, switched ? "yes" : "NO",
         frames ? "off the games' windows" : "left", GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN));

    if (*rest) {
        STARTUPINFOW startup;
        WCHAR *copy = HeapAlloc(GetProcessHeap(), 0, (lstrlenW(rest) + 1) * sizeof(WCHAR));
        memset(&startup, 0, sizeof(startup));
        startup.cb = sizeof(startup);
        if (!copy) return 1;
        lstrcpyW(copy, rest);
        if (!CreateProcessW(NULL, copy, NULL, NULL, FALSE, 0, NULL, NULL, &startup, &child)) {
            note("could not start '%ls': error %lu", rest, GetLastError());
            return 1;
        }
        note("started '%ls'", rest);
        CloseHandle(child.hThread);
    }

    for (;;) {
        int changed = 0, games;
        DWORD now;

        SwitchDesktop(desktop);
        if (frames) EnumWindows(strip, (LPARAM)&changed);
        if (!child.hProcess) {
            /* Run by itself (no command line): one pass, as a tool. */
            if (!changed) break;
            Sleep(100);
            continue;
        }
        if (helper_gone) Sleep(changed ? 100 : 400);
        else if (WaitForSingleObject(child.hProcess, changed ? 100 : 400) == WAIT_OBJECT_0) {
            /* What this started is gone (a launcher that started the game and left): the game's own programs decide from here. */
            GetExitCodeProcess(child.hProcess, &exit_code);
            note("the program this started ended by itself (code %lu)", exit_code);
            helper_gone = 1;
        }
        games = game_processes(game);
        now = GetTickCount();
        if (games != last_games) {
            if (games > 0) note("%d program(s) of the game's running (%s)", games, game);
            else if (games == 0 && seen) note("no program of the game's is left");
            last_games = games;
        }
        if (games > 0) { seen = 1; last_seen = now; }
        else if (games == 0 && ((seen && now - last_seen >= 3000) || (!seen && now - started >= 90000) || (helper_gone && now - last_seen >= 3000))) {
            /* The game is over (or never came): the helper goes, and with it the desktop and the session. */
            note(seen ? "the game is over: ending the session" : "no program of the game's started: ending the session");
            if (!helper_gone) {
                TerminateProcess(child.hProcess, 0);
                WaitForSingleObject(child.hProcess, 2000);
            }
            break;
        }
    }
    if (child.hProcess) CloseHandle(child.hProcess);
    return (int)exit_code;
}
