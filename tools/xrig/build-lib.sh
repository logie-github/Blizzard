#!/bin/sh
# Builds Winlator's X server native code (app/winlator/cpp/winlator: its socket reader and writer, the epoll
# connector, the drawing helpers, shared memory, the registry editor) for this machine, as libwinlator.so in
# $1 (default build/xrig), with stand-ins for the few Android headers it includes (stubs/). The GPU parts
# (gpu_image.c, gpu_helper.c: hardware buffers, EGL) are left out: nothing in the rig draws through them.
# Beside it, the rig's Windows programs (inputprobe.exe), built with Zig when ZIG names it or it is on the PATH.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/build/xrig}"
SRC="$ROOT/app/winlator/cpp/winlator"
JAVA="${JAVA_HOME:-$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")}"
mkdir -p "$OUT/src"
# Some of its functions are Android "critical natives" (@CriticalNative: called with their arguments alone). A desktop
# JVM calls every native function with the JNI environment and the class first, so the copies built here take those two
# as well (without them the first argument, a pointer the code frees, was the JVM's own environment).
for name in drawable sysvshared_memory xconnector_epoll xinput_stream xoutput_stream arrays ring_buffer wine_registry_editor; do
	sed -E 's/^(Java_com_winlator_[A-Za-z0-9_]+)\((j(long|int|byte|short|boolean|float|double) )/\1(JNIEnv* xrigEnv, jclass xrigClass, \2/' \
		"$SRC/src/$name.c" > "$OUT/src/$name.c"
done
cc -shared -fPIC -O2 -g -w -o "$OUT/libwinlator.so" \
	-I"$JAVA/include" -I"$JAVA/include/linux" -I"$ROOT/tools/xrig/stubs" -I"$SRC/include" \
	-D__ANDROID__ -D__ANDROID_API__=26 -D_DEFAULT_SOURCE \
	-include stdint.h -include stdbool.h -include string.h -include stdlib.h -include sys/types.h -include linux/memfd.h \
	"$OUT/src/drawable.c" "$OUT/src/sysvshared_memory.c" "$OUT/src/xconnector_epoll.c" \
	"$OUT/src/xinput_stream.c" "$OUT/src/xoutput_stream.c" "$OUT/src/arrays.c" "$OUT/src/ring_buffer.c" \
	"$OUT/src/wine_registry_editor.c" "$ROOT/tools/xrig/stubs/host.c" -lpthread
# The GLX extension's library, loaded by name as the server starts: a stand-in with no GPU behind it.
cc -shared -fPIC -O2 -w -o "$OUT/libgladiorenderer.so" -I"$JAVA/include" -I"$JAVA/include/linux" "$ROOT/tools/xrig/stubs/gladiorenderer.c"
echo "$OUT/libwinlator.so"

ZIG="${ZIG:-$(command -v zig || true)}"
if [ -n "$ZIG" ]; then
	"$ZIG" cc -target x86_64-windows-gnu -O2 -s -Wl,--subsystem,windows "$ROOT/tools/xrig/inputprobe.c" -luser32 -lkernel32 -lgdi32 -o "$OUT/inputprobe.exe" 2> "$OUT/inputprobe.log" ||
		{ tail -20 "$OUT/inputprobe.log"; exit 1; }
	echo "$OUT/inputprobe.exe"
else
	echo "No zig: inputprobe.exe not built (set ZIG=<path to zig>)." >&2
fi
