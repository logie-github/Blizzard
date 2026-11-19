/*
 * inputprobe.exe: what a Windows program gets of the mouse and keyboard, written down.
 *
 * For the X server rig (tools/xrig/README.md): run inside Wine against Winlator's own X server on a desktop,
 * it opens a 400x300 window at 100,100 (one the person could drag larger, as Warcraft III's is; with the argument
 * "fixed" one of a fixed size, as Diablo II's), optionally locks the cursor to its client area the way games do
 * (ClipCursor, again on a timer: argument "clip"), and writes every button, key and character message it is
 * sent, and each size its client area takes, to C:\windows\inputprobe.log, one a line, flushed as written. With
 * "game" it stands in for a modern World of Warcraft client instead: a window over the whole screen with the arrow,
 * and from its fourth second its own cursor (a cross, set on every tick as the game sets its cursor every frame),
 * which is how the app tells that the game's login screen is up; its log is C:\windows\inputprobe-game.log. The
 * test injects input into the X server and reads the log: what arrives here is what a game would have got on the phone.
 *
 * Built with Zig for x86_64 Windows, the Windows subsystem (no console).
 */
#include <windows.h>
#include <stdio.h>
#include <string.h>

static FILE *out;
static int clip;
static int game;
static DWORD started;

static void line(const char *fmt, ...)
{
    va_list args;
    if (!out) return;
    va_start(args, fmt);
    vfprintf(out, fmt, args);
    va_end(args);
    fputc('\n', out);
    fflush(out);
}

static void lock_cursor(HWND hwnd)
{
    RECT r;
    POINT a, b;
    if (!clip || GetForegroundWindow() != hwnd) return;
    GetClientRect(hwnd, &r);
    a.x = r.left; a.y = r.top; b.x = r.right; b.y = r.bottom;
    ClientToScreen(hwnd, &a);
    ClientToScreen(hwnd, &b);
    r.left = a.x; r.top = a.y; r.right = b.x; r.bottom = b.y;
    ClipCursor(&r);
}

static LRESULT CALLBACK proc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp)
{
    int x = (short)LOWORD(lp), y = (short)HIWORD(lp);
    switch (msg) {
    case WM_CREATE: SetTimer(hwnd, 1, 250, NULL); return 0;
    case WM_TIMER:
        lock_cursor(hwnd);
        if (game && GetTickCount() - started >= 4000) {
            HCURSOR cross = LoadCursorA(NULL, (LPCSTR)IDC_CROSS);
            SetClassLongPtrA(hwnd, GCLP_HCURSOR, (LONG_PTR)cross);
            SetCursor(cross);
        }
        return 0;
    case WM_ACTIVATE: line("ACTIVATE %d", (int)LOWORD(wp)); lock_cursor(hwnd); return 0;
    case WM_SIZE: line("SIZE %d %d", (int)LOWORD(lp), (int)HIWORD(lp)); lock_cursor(hwnd); break;
    case WM_MOVE: lock_cursor(hwnd); break;
    case WM_LBUTTONDOWN: line("LDOWN %d %d", x, y); return 0;
    case WM_LBUTTONUP: line("LUP %d %d", x, y); return 0;
    case WM_RBUTTONDOWN: line("RDOWN %d %d", x, y); return 0;
    case WM_RBUTTONUP: line("RUP %d %d", x, y); return 0;
    case WM_LBUTTONDBLCLK: line("LDBL %d %d", x, y); return 0;
    case WM_MOUSEWHEEL: line("WHEEL %d", (int)(short)HIWORD(wp)); return 0;
    case WM_KEYDOWN: case WM_SYSKEYDOWN: line("KEYDOWN vk=%02X scan=%02X", (unsigned)wp, (unsigned)((lp >> 16) & 0xff)); break;
    case WM_KEYUP: case WM_SYSKEYUP: line("KEYUP vk=%02X", (unsigned)wp); break;
    case WM_CHAR: line("CHAR %u '%c'", (unsigned)wp, wp >= 32 && wp < 127 ? (char)wp : '?'); return 0;
    case WM_DESTROY: PostQuitMessage(0); return 0;
    }
    return DefWindowProcA(hwnd, msg, wp, lp);
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous, LPSTR command, int show)
{
    WNDCLASSA wc;
    HWND hwnd;
    MSG msg;
    RECT r;
    DWORD style;
    (void)previous; (void)show;
    clip = command && strstr(command, "clip") != NULL && strstr(command, "noclip") == NULL;
    style = command && strstr(command, "fixed") != NULL ? WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX : WS_OVERLAPPEDWINDOW;
    game = command && strstr(command, "game") != NULL;
    started = GetTickCount();
    if (game) style = WS_POPUP;
    /* (the stand-in for a game writes its own log: a launcher's stand-in may be up beside it) */
    out = fopen(command && strstr(command, "game") != NULL ? "C:\\windows\\inputprobe-game.log" : "C:\\windows\\inputprobe.log", "w");
    memset(&wc, 0, sizeof(wc));
    wc.style = CS_DBLCLKS;
    wc.lpfnWndProc = proc;
    wc.hInstance = instance;
    wc.hCursor = LoadCursorA(NULL, (LPCSTR)IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = "InputProbe";
    RegisterClassA(&wc);
    /* A client area of 400x300 with its top left at 100,100 on the screen, whatever the frame's size. */
    r.left = 100; r.top = 100; r.right = 500; r.bottom = 400;
    if (game) { r.left = 0; r.top = 0; r.right = GetSystemMetrics(SM_CXSCREEN); r.bottom = GetSystemMetrics(SM_CYSCREEN); }
    else AdjustWindowRect(&r, style, FALSE);
    hwnd = CreateWindowA("InputProbe", "inputprobe", style | WS_VISIBLE, r.left, r.top, r.right - r.left, r.bottom - r.top, NULL, NULL, instance, NULL);
    {
        /* Where the client area starts inside the window (the frame's left and the title bar's height), for the test's arithmetic. */
        RECT w;
        POINT c = {0, 0};
        GetWindowRect(hwnd, &w);
        ClientToScreen(hwnd, &c);
        line("START clip=%d hwnd=%p frame=%d,%d", clip, (void *)hwnd, (int)(c.x - w.left), (int)(c.y - w.top));
    }
    SetForegroundWindow(hwnd);
    lock_cursor(hwnd);
    while (GetMessageA(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }
    return 0;
}
