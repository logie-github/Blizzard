/*
 * borderless.exe: the windowed games fill the screen with no title bar.
 *
 * The games' Windows is Wine's virtual desktop, the size of the phone's screen, where Wine draws
 * every window's title bar and frame itself (no window manager: the X server is Winlator's). A
 * game started in a window (Warcraft III 1.2x's -window, Diablo II's -w) at the screen's size then
 * sits under its own title bar, the picture pushed down and cut at the bottom, and no setting of
 * Wine's takes the bar away (10.10 knows no "Decorated"). This program, run by the app inside that
 * Windows once the game's window is up (winhandler's exec), takes the caption and frame styles off
 * every top-level window of the games (not Wine's own programs, not dialog boxes) and puts it at the
 * top left at its client area's size, so the window is the whole screen. It keeps watching (a game
 * makes its window again when its resolution changes) and ends with the Windows it runs in.
 *
 * Built with Zig for x86_64 Windows (scripts/build-tools.sh), the Windows subsystem: no console.
 */
#include <windows.h>
#include <string.h>

/* Wine's own programs and the launcher's helper: never theirs. */
static const char *const kept[] = {"explorer.exe", "winhandler.exe", "wfm.exe", "wineconsole.exe", "winecfg.exe", "taskmgr.exe", "services.exe", "winedevice.exe", "plugplay.exe", "rpcss.exe", "conhost.exe", NULL};

static const DWORD FRAME_STYLES = WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU | WS_BORDER | WS_DLGFRAME;
static const DWORD FRAME_EXSTYLES = WS_EX_DLGMODALFRAME | WS_EX_CLIENTEDGE | WS_EX_STATICEDGE | WS_EX_WINDOWEDGE;

/* Wine's own windows, by class: the taskbar, the desktop, dialog boxes. */
static const char *const kept_classes[] = {"Shell_TrayWnd", "Progman", "#32770", NULL};

/*
 * Whether the window is one of Wine's own programs'. A process that cannot be opened (Wine refused the game's, a 32-bit
 * one, with access denied on 9 November 2026, while its own opened) is taken for the game's.
 */
static int kept_program(HWND hwnd)
{
    DWORD pid = 0;
    char path[MAX_PATH];
    DWORD size = sizeof(path);
    const char *name;
    int i;

    GetWindowThreadProcessId(hwnd, &pid);
    if (!pid) return 0;
    {
        HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
        if (!process) return 0;
        if (!QueryFullProcessImageNameA(process, 0, path, &size)) { CloseHandle(process); return 0; }
        CloseHandle(process);
    }
    name = strrchr(path, '\\');
    name = name ? name + 1 : path;
    for (i = 0; kept[i]; i++) if (!lstrcmpiA(name, kept[i])) return 1;
    return 0;
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

    exstyle = (DWORD)GetWindowLongW(hwnd, GWL_EXSTYLE);
    SetWindowLongW(hwnd, GWL_STYLE, (LONG)(style & ~FRAME_STYLES));
    SetWindowLongW(hwnd, GWL_EXSTYLE, (LONG)(exstyle & ~FRAME_EXSTYLES));
    SetWindowPos(hwnd, NULL, 0, 0, width, height, SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED | SWP_NOOWNERZORDER);
    (*(int *)lparam)++;
    return TRUE;
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous, LPSTR command, int show)
{
    (void)instance; (void)previous; (void)command; (void)show;
    for (;;) {
        int changed = 0;
        EnumWindows(strip, (LPARAM)&changed);
        Sleep(changed ? 100 : 400);
    }
    return 0;
}
