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
 *    the app's menu. When no program of the game's is left for three seconds (fifteen with /noframes: an installer
 *    may start its next part late; or none ever started in a minute and a half), winhandler.exe is ended and this
 *    program exits: the desktop closes, Wine exits, and the app returns to the launcher.
 *
 * It also tells the app what only a program inside the games' Windows can see: its log (C:\windows\borderless.log: the
 * game's windows, a dialog box's words) and whether a dialog box is up (C:\windows\borderless.dialog).
 *
 * Built with Zig for x86_64 Windows (scripts/build-tools.sh), the Windows subsystem: no console.
 */
#include <windows.h>
#include <tlhelp32.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/*
 * What it did and saw, for the app's reports (C:\windows\borderless.log, a few lines a session, started anew each time): the
 * desktop switch, what it started, the game's windows as they appear (a dialog box with its words: the game's own error
 * message), each window it took the frame off, the game's programs as they come and go, why it ended.
 */
static HANDLE log_file = INVALID_HANDLE_VALUE;
static DWORD log_started;

/* One line: the seconds since this program started, then the text (wvsprintfA writes at most 1024 characters). */
static void note(const char *format, ...)
{
    char text[1100];
    DWORD written;
    va_list args;
    int length, i;

    if (log_file == INVALID_HANDLE_VALUE) return;
    length = wsprintfA(text, "%lu ", (GetTickCount() - log_started) / 1000);
    va_start(args, format);
    length += wvsprintfA(text + length, format, args);
    va_end(args);
    for (i = 0; i < length; i++) if (text[i] == '\r' || text[i] == '\n') text[i] = ' ';
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

/*
 * The game's windows as they appear, once each: class, title, place, style. A dialog box's words too (its texts and
 * buttons): a game that stops at a message of its own says in the report what the message was. Windows already looked at
 * are remembered (Wine's own as well, so their program is asked about once), and one of the game's that goes while the
 * game still runs is said to be gone: the app reads from that whether a movie's window (Warcraft III's) was still up
 * when the game's programs went, which is a movie that could not be played.
 */
#define NOTED 64
static HWND noted[NOTED];
static char noted_class[NOTED][32]; /* "" for a window that is not the game's */
static int noted_count;
static char gone_class[8][32]; /* gone at the last tick: said at this one if the game still runs */
static int gone_count;

static BOOL CALLBACK say(HWND child, LPARAM lparam)
{
    char cls[32] = "", text[400] = "";
    DWORD_PTR result = 0;

    (void)lparam;
    GetClassNameA(child, cls, sizeof(cls));
    if (lstrcmpiA(cls, "Static") && lstrcmpiA(cls, "Button") && lstrcmpiA(cls, "Edit")) return TRUE;
    if (!SendMessageTimeoutA(child, WM_GETTEXT, sizeof(text), (LPARAM)text, SMTO_ABORTIFHUNG, 200, &result) || !text[0]) return TRUE;
    note("    %s: %.380s", cls, text);
    return TRUE;
}

static BOOL CALLBACK watch(HWND hwnd, LPARAM lparam)
{
    char cls[64] = "", title[128] = "";
    RECT rect;
    int i;

    (void)lparam;
    if (!IsWindowVisible(hwnd) || GetAncestor(hwnd, GA_PARENT) != GetDesktopWindow()) return TRUE;
    for (i = 0; i < noted_count; i++) if (noted[i] == hwnd) return TRUE;
    if (noted_count >= NOTED) return TRUE;
    noted[noted_count] = hwnd;
    noted_class[noted_count][0] = 0;
    noted_count++;
    if (kept_program(hwnd) || !GetWindowRect(hwnd, &rect)) return TRUE;
    GetClassNameA(hwnd, cls, sizeof(cls));
    GetWindowTextA(hwnd, title, sizeof(title));
    lstrcpynA(noted_class[noted_count - 1], cls, sizeof(noted_class[0]));
    note("window of class '%s' \"%.120s\": %ldx%ld at %ld,%ld, style %08lx", cls, title, rect.right - rect.left, rect.bottom - rect.top,
         rect.left, rect.top, (DWORD)GetWindowLongW(hwnd, GWL_STYLE));
    if (!lstrcmpA(cls, "#32770")) EnumChildWindows(hwnd, say, 0);
    return TRUE;
}

/*
 * The windows that have gone since the last tick: their places are freed (a new window can get the same handle), and
 * the game's are said to be gone one tick later, if the game still runs then. A game whose programs end takes its
 * windows with it in the same moment; those are not "gone", they were up at the end.
 */
static void windows_gone(int game_runs)
{
    int i;

    if (game_runs) for (i = 0; i < gone_count; i++) note("window of class '%s' gone", gone_class[i]);
    gone_count = 0;
    for (i = 0; i < noted_count; ) {
        if (IsWindow(noted[i])) { i++; continue; }
        if (noted_class[i][0] && gone_count < (int)(sizeof(gone_class) / sizeof(gone_class[0]))) lstrcpynA(gone_class[gone_count++], noted_class[i], sizeof(gone_class[0]));
        noted_count--;
        noted[i] = noted[noted_count];
        lstrcpynA(noted_class[i], noted_class[noted_count], sizeof(noted_class[0]));
    }
}

/*
 * Whether a dialog box of the game's is up (Windows' own kind: an error message, "already running", a prompt). The app's
 * touch for the strategy games makes a tap the right click, which presses nothing on such a box, and Winlator's X server
 * cannot tell a dialog from a game's window here (Wine sets no window type on them in its desktop: read on the rig). So
 * the keeper says it: the file C:\windows\borderless.dialog is there for as long as one is up, and a tap is then the left
 * click.
 */
static BOOL CALLBACK count_dialogs(HWND hwnd, LPARAM lparam)
{
    char cls[16] = "";

    if (!IsWindowVisible(hwnd) || GetAncestor(hwnd, GA_PARENT) != GetDesktopWindow()) return TRUE;
    GetClassNameA(hwnd, cls, sizeof(cls));
    if (lstrcmpA(cls, "#32770") || kept_program(hwnd)) return TRUE;
    (*(int *)lparam)++;
    return TRUE;
}

static const char DIALOG_FLAG[] = "C:\\windows\\borderless.dialog";

static void say_dialog(int up)
{
    static int said = -1;
    HANDLE file;

    if (up == said) return;
    said = up;
    if (!up) { DeleteFileA(DIALOG_FLAG); return; }
    file = CreateFileA(DIALOG_FLAG, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_DELETE, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file != INVALID_HANDLE_VALUE) CloseHandle(file);
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
     * A change of style is a message to the window's own thread, and waits for it: Warcraft III's is busy for the whole
     * of a movie (the keeper stood still for the 90 seconds of its intro on the rig), and at its start. A window that does
     * not answer now is left for the next tick.
     */
    {
        DWORD_PTR answer = 0;
        if (!SendMessageTimeoutW(hwnd, WM_NULL, 0, 0, SMTO_ABORTIFHUNG, 150, &answer)) return TRUE;
    }

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
     * the screen's own resolution. (A lock of the cursor to a window that is the whole screen is no lock to Wine either:
     * it then holds no pointer grab, seen on the rig.) A window of a fixed size (Diablo II's) keeps it: its game would
     * draw in a corner.
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
    DWORD started = GetTickCount(), last_seen = started, exit_code = 0, grace;
    WCHAR *rest = rest_of_command_line(&frames);
    PROCESS_INFORMATION child;
    HDESK desktop = GetThreadDesktop(GetCurrentThreadId());
    char desktop_name[64] = "", game[64] = "";
    DWORD needed = 0;
    BOOL switched;

    (void)instance; (void)previous; (void)command; (void)show;
    memset(&child, 0, sizeof(child));
    log_started = started;
    log_file = CreateFileA("C:\\windows\\borderless.log", GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    GetUserObjectInformationA(desktop, UOI_NAME, desktop_name, sizeof(desktop_name), &needed);
    grace = frames ? 3000 : 15000;
    DeleteFileA(DIALOG_FLAG);
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
        int changed = 0, dialogs = 0, games;
        DWORD now;

        SwitchDesktop(desktop);
        EnumWindows(watch, 0);
        EnumWindows(count_dialogs, (LPARAM)&dialogs);
        say_dialog(dialogs > 0);
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
        windows_gone(games > 0);
        now = GetTickCount();
        if (games != last_games) {
            if (games > 0) note("%d program(s) of the game's running (%s)", games, game);
            /* (the app reads these words, and "window of class '...' gone": Wc3Movies.upAtEnd) */
            else if (games == 0 && seen) note("no program of the game's is left");
            last_games = games;
        }
        if (games > 0) { seen = 1; last_seen = now; }
        else if (games == 0 && ((seen && now - last_seen >= grace) || (!seen && now - started >= 90000) || (helper_gone && now - last_seen >= grace))) {
            /* The game is over (or never came): the helper goes, and with it the desktop and the session. */
            note(seen ? "the game is over: ending the session" : "no program of the game's started: ending the session");
            if (!helper_gone) {
                TerminateProcess(child.hProcess, 0);
                WaitForSingleObject(child.hProcess, 2000);
            }
            break;
        }
    }
    say_dialog(0);
    if (child.hProcess) CloseHandle(child.hProcess);
    return (int)exit_code;
}
