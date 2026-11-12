# The X server rig: Winlator's own X server on a desktop

On the phone a game's clicks and keys go through Winlator's X server, which is Java code in the app, and it differs from a
stock X server exactly where the games' input goes wrong: pointer grabs, the stretch of a small window over the screen, which
window an event is sent to. Xvfb (README, "Testing the Windows games here") cannot show those faults. The rig runs
Winlator's server itself in a unit test (Robolectric), with Winlator's native library built for this machine, and the same
Wine the phone runs (an x86_64 build) connects to it. What a Windows program gets of a touch can then be read here.

This is how "Warcraft III won't let me click" (the phone, 9 November 2026) was found and fixed: see `tools/borderless/borderless.c`.

## What is here

- `build-lib.sh <out>`: builds `libwinlator.so` for this machine from Winlator's C sources (`app/winlator/cpp/winlator/src`, so
  `scripts/prepare-winlator.sh` must have run), a stand-in `libgladiorenderer.so`, and, with `ZIG=<path to zig>`,
  `inputprobe.exe`. The sources are copied and adapted on the way: Android's `@CriticalNative` functions take no JNI
  environment, a desktop JVM passes one, so the copies take the two extra arguments.
- `stubs/`: the few Android headers and functions the library wants (`ASharedMemory_create` over memfd, the log, bitmaps),
  and `HostShm`: real System V segments mapped for the server, which MIT-SHM (Wine's drawing) needs.
- `inputprobe.c`: a Windows program that opens a 400x300 window (sizable, or of a fixed size with `fixed`), locks the cursor
  to it as games do (`clip`), and writes every button, key, character and size it is given to `C:\windows\inputprobe.log`.
- `glread.c`, `glread.sh <frames dir>`: the phone's look at a game's frame on a real OpenGL ES (this machine's Mesa), call for
  call. On the phone Warcraft III's frame is in a texture only the drawing thread can read (`Wc3Watch`); the server here has
  no GPU, so the calls are made by this program instead: two contexts sharing their objects, the frame copied into a texture
  in one as Winlator's `Texture.copyFromReadBuffer` does, read through a framebuffer in the other. It leaves `<name>.rgba`
  beside each `<name>.png`, which `Wc3ScreenTest` then reads the game's state from (`BLIZZ_WC3_FRAMES=<frames dir>`).
- `app/src/test/java/com/logie/blizz/rig/XRig.kt`: the rig (the server, its renderer's stretch, the win handler, Wine's
  processes, clicks and keys as the app's touch layer makes them, a screenshot of the server's windows).
- `app/src/test/java/com/logie/blizz/rig/XServerRigTest.kt`: the tests, and `hold`, which keeps the server up to be driven by hand.

## Running it

Needed once: Winlator's root file system unpacked at `/data/data/com.logie.blizz/winrootfs` and a Wine prefix at
`/tmp/wlc/.wine` (README, "Testing the Windows games here", steps 1 to 3), and `borderless.exe` built
(`scripts/build-tools.sh`, or the one `zig cc` line in it) and copied beside the library.

```sh
tools/xrig/build-lib.sh /tmp/xrig                      # libwinlator.so, libgladiorenderer.so, inputprobe.exe (ZIG=...)
cp app/tools/assets/borderless.exe /tmp/xrig/
BLIZZ_XRIG=1 BLIZZ_XRIG_LIB=/tmp/xrig ./gradlew --init-script <maven-mirror.init.gradle> \
    :app:testDebugUnitTest --tests 'com.logie.blizz.rig.XServerRigTest'
```

Without `BLIZZ_XRIG=1` the tests are skipped: CI and an ordinary test run pass over them.

## The tests

| Test | What it shows |
| --- | --- |
| `aSizableWindowGetsTheWholeScreenAndItsClicks` | The probe locks the cursor in a sizable window (Warcraft III's kind), started as the app starts a game (keeper, winhandler.exe, program). The keeper gives the window the whole screen, the program is told its new size, Wine holds no pointer grab (a lock to the whole screen is none), and a touch arrives as one click where it was made. |
| `withoutTheKeeperALockedCursorGetsNoClick` | A locked cursor without the keeper: no click arrives. The fault, kept as a record. |
| `aLockedCursorInAStretchedWindowGetsItsClickWhereTouched` | A fixed 400x300 window stretched over 800x600 with the cursor locked and Wine's pointer grab held, through the keeper: one click, where the picture was touched (the input desktop switched; the grab window takes the stretched window's transformation, Winlator patch 0009). |
| `aGameThatDoesNotLockTheCursorGetsItsClicks` | Diablo II's kind of window through the keeper. |
| `aFramedWindowStretchedToTheScreenGetsItsClickWhereTouched` | A program by itself, frame on, stretched. |
| `theKeeperSaysWhenADialogBoxIsUp` | A Windows dialog box (Wine's About box, started as a game is): the keeper's file `borderless.dialog` is there while it is up and its words are in the keeper's log; the app makes a strategy game's tap the left click meanwhile. Winlator's server cannot tell such a window from a game's (no dialog type on it). |
| `theSessionEndsWhenTheGameDoes` | The game's window closed: Wine exits within seconds (the app returns to the launcher). |
| `theAppsKeyboardTypesWhatItsCapsShow` | The app's keyboard: letters, Shift, digits, Enter, Escape, F10 as the program reads them. |

## By hand

`BLIZZ_XRIG_HOLD=<seconds>` (and `BLIZZ_XRIG_SIZE=WxH`) with `--tests 'com.logie.blizz.rig.XServerRigTest.hold'` keeps the
server up as display `:77`. A Wine program started with `DISPLAY=:77` (in `explorer /desktop=shell,WxH`, as the phone
starts games) draws on it. Commands written to `/tmp/xrig-77-cmd`, one a line, are answered in `/tmp/xrig-77-out.txt`:
`move X Y`, `click X Y`, `dclick X Y`, `down`/`up`, `key NAME`, `type text`, `shot file.png`, `windows`, `state`,
`pshot file.png` (below), `sleep MS`, `exec command`. The window tree is written to `/tmp/xrig-77-windows.txt` as it changes. Diablo II 1.13 was
played this way through the keeper and winhandler.exe: its menu, a character named with the app's keys, a game entered,
and the session ending when the game was quit from its own menu.

## Through the phone's Box64

The phone runs the same Wine through Box64 (arm64). That runs here too, slowly, with `qemu-user`: a program that fails only on
the phone can be tried through the phone's own Box64 build before anything is changed for it (World of Warcraft: Forever's
launcher, 12 November 2026: it ran, so Box64 was not what failed).

1. `apt-get install qemu-user-static`; `mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc` and register
   `qemu-aarch64-static` for arm64 programs with the flag `F` (README, "The Forever client and realm on the rig").
2. Box64: unpack `app/winlator/assets/box64/box64-0.4.4.tzst` and put its `usr/local/bin/box64` into the runtime
   (`winrootfs/usr/local/bin`); its loader path is Winlator's, so link `/data/data/com.winlator/files/rootfs` at the runtime.
   `box64/default.box64rc` goes to `winrootfs/etc/config.box64rc`.
3. The runtime's X library looks for the server under the runtime (`winrootfs/tmp/.X11-unix/X<display>`): link that at the
   rig's socket (`/tmp/xrig-<display>/tmp/.X11-unix/X0`).
4. Start as the phone does (`GuestProgramLauncherComponent`): `box64 <wine> explorer /desktop=shell,WxH ...` with
   `LD_LIBRARY_PATH=winrootfs/usr/lib`, `BOX64_LD_LIBRARY_PATH=winrootfs/lib/x86_64-linux-gnu`, `TMPDIR=winrootfs/tmp`,
   `ANDROID_SYSVSHM_SERVER=/tmp/xrig-<display>/tmp/.sysvshm/SM0`, `BOX64_RCFILE`, `BOX64_DYNAREC=1`, and the preset's
   variables (`Box64PresetManager`). Without the shared memory server's address Wine's drawing faults in
   `NtUserShowWindow`/`NtUserSetWindowPos` and no window shows; the rig's server takes both kinds of segment (the service's,
   as on the phone, and this machine's own for the native Wine).

A .NET program's window took three to four minutes to come up this way (seconds natively).

`pshot FILE` in the hold mode writes the screen as the phone's renderer composes it (`GLRenderer`, with the games' forced
full screen): black first, a plain undecorated window stretched over the screen, a layered or transparent window blended by
its own alpha. `shot` shows what the windows hold instead. The window list says ` layered`, ` transparent` and the range of
alpha in each mapped window's pixels: a window the renderer blends whose pixels carry alpha 0 is not seen on the phone.

## What it cannot do

There is no GPU behind the server: programs that draw with GDI or DirectDraw (the probe, Diablo II's window) show; a
Direct3D game needs GLX or Vulkan presentation, which the rig has not, so Warcraft III itself is run on Xvfb with the
keeper (clicks, campaigns, movies) and its click path is proved here with the probe. Nothing here is a phone: Box64, the
phone's GPU driver and Android's own input come after it.
