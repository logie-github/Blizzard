/*
 * The mariadb client as dbimport and the world server run it (their MySQLExecutable setting).
 *
 * The server's programs are musl programs started through the musl loader, with a compatibility
 * library preloaded (LD_PRELOAD), and that variable is inherited by whatever they start. A shell
 * script as the client would be run by Android's own /system/bin/sh, which cannot load that library
 * and stops; a program linked against Android's libc would hit the same preload, and a static one
 * built with Android's libc stops at its own start-up check of its thread-local storage.
 *
 * So this program uses no libc at all: it is freestanding, talks to the kernel with system calls,
 * and has no thread-local storage and no dynamic linker. It starts the real client through the musl
 * loader with the library preloaded for that alone, and writes a log of what it did.
 *
 * Environment: BLIZZ_LDSO (the musl loader), BLIZZ_SERVER (the server's folder), BLIZZ_LOG (optional:
 * a file it appends to). Everything else is passed on as it is; the SQL arrives on stdin.
 * AArch64 Linux only.
 */
typedef unsigned long u64;
typedef long i64;

#define MAXARGS 128
#define MAXENV 1024
#define BUF 4096

static i64 sys6(i64 n, i64 a, i64 b, i64 c, i64 d, i64 e, i64 f) {
	register i64 x8 __asm__("x8") = n;
	register i64 x0 __asm__("x0") = a;
	register i64 x1 __asm__("x1") = b;
	register i64 x2 __asm__("x2") = c;
	register i64 x3 __asm__("x3") = d;
	register i64 x4 __asm__("x4") = e;
	register i64 x5 __asm__("x5") = f;
	__asm__ volatile("svc 0" : "+r"(x0) : "r"(x8), "r"(x1), "r"(x2), "r"(x3), "r"(x4), "r"(x5) : "memory", "cc");
	return x0;
}

#define SYS_dup3 24
#define SYS_openat 56
#define SYS_close 57
#define SYS_write 64
#define SYS_exit_group 94
#define SYS_clone 220
#define SYS_execve 221
#define SYS_wait4 260
#define AT_FDCWD (-100)
#define O_WRONLY 1
#define O_CREAT 0100
#define O_APPEND 02000
#define SIGCHLD 17

static u64 len(const char *s) { u64 n = 0; while (s[n]) n++; return n; }

static int starts(const char *s, const char *prefix) {
	while (*prefix) if (*s++ != *prefix++) return 0;
	return 1;
}

/* Appends [s] to [out] (size BUF); returns the new length. */
static u64 put(char *out, u64 at, const char *s) {
	while (*s && at < BUF - 1) out[at++] = *s++;
	out[at] = 0;
	return at;
}

static const char *envget(char **envp, const char *name) {
	u64 n = len(name);
	for (; *envp; envp++) if (starts(*envp, name) && (*envp)[n] == '=') return *envp + n + 1;
	return 0;
}

static void logs(int fd, const char *s) {
	if (fd >= 0) sys6(SYS_write, fd, (i64)s, (i64)len(s), 0, 0, 0);
}

static void number(char *out, i64 v) {
	char tmp[24];
	int n = 0;
	if (v < 0) { *out++ = '-'; v = -v; }
	if (v == 0) tmp[n++] = '0';
	while (v > 0) { tmp[n++] = '0' + v % 10; v /= 10; }
	while (n > 0) *out++ = tmp[--n];
	*out = 0;
}

static char libdir[BUF], bindir[BUF], preload[BUF];
static char *newargv[MAXARGS + 8];
static char *newenv[MAXENV + 2];

__attribute__((noreturn, used)) void blizz_main(u64 *sp) {
	int argc = (int)sp[0];
	char **argv = (char **)(sp + 1);
	char **envp = argv + argc + 1;
	const char *loader = envget(envp, "BLIZZ_LDSO");
	const char *server = envget(envp, "BLIZZ_SERVER");
	const char *logpath = envget(envp, "BLIZZ_LOG");
	int log = logpath ? (int)sys6(SYS_openat, AT_FDCWD, (i64)logpath, O_WRONLY | O_CREAT | O_APPEND, 0644, 0, 0) : -1;
	if (log < 0) log = -1;
	if (!loader || !server || argc > MAXARGS) {
		logs(2, "blizzmaria: BLIZZ_LDSO and BLIZZ_SERVER must be set, and there can be at most 128 arguments\n");
		logs(log, "blizzmaria: BLIZZ_LDSO and BLIZZ_SERVER must be set, and there can be at most 128 arguments\n");
		sys6(SYS_exit_group, 127, 0, 0, 0, 0, 0);
	}
	put(libdir, put(libdir, 0, server), "/lib");
	put(bindir, put(bindir, 0, server), "/bin/mariadb");
	put(preload, put(preload, 0, "LD_PRELOAD="), server);
	put(preload, len(preload), "/lib/libandroidcompat.so");

	/* The client's command line: the loader, its library path, the client, then what we were given. */
	int n = 0;
	newargv[n++] = (char *)loader;
	newargv[n++] = "--library-path";
	newargv[n++] = libdir;
	newargv[n++] = bindir;
	for (int i = 1; i < argc; i++) newargv[n++] = argv[i];
	newargv[n] = 0;

	/* Its environment: ours, with LD_PRELOAD set to the compatibility library. */
	int e = 0;
	for (char **p = envp; *p && e < MAXENV; p++) if (!starts(*p, "LD_PRELOAD=")) newenv[e++] = *p;
	newenv[e++] = preload;
	newenv[e] = 0;

	if (log >= 0) {
		/* What it was asked to do (a password's value never goes in the log). */
		static char line[BUF];
		u64 at = put(line, 0, "blizzmaria:");
		for (int i = 1; i < argc; i++) {
			at = put(line, at, " ");
			at = put(line, at, starts(argv[i], "-p") ? "-p***" : argv[i]);
		}
		put(line, at, "\n");
		logs(log, line);
	}

	i64 pid = sys6(SYS_clone, SIGCHLD, 0, 0, 0, 0, 0);
	if (pid < 0) {
		logs(log, "blizzmaria: fork failed\n");
		sys6(SYS_exit_group, 127, 0, 0, 0, 0, 0);
	}
	if (pid == 0) {
		/* The client's own messages go to the log: dbimport doesn't show them. */
		if (log >= 0) sys6(SYS_dup3, log, 2, 0, 0, 0, 0);
		i64 r = sys6(SYS_execve, (i64)loader, (i64)newargv, (i64)newenv, 0, 0, 0);
		char num[24];
		number(num, r);
		logs(2, "blizzmaria: exec of the musl loader failed, error ");
		logs(2, num);
		logs(2, "\n");
		sys6(SYS_exit_group, 127, 0, 0, 0, 0, 0);
	}
	int status = 0;
	sys6(SYS_wait4, pid, (i64)&status, 0, 0, 0, 0);
	int code = (status & 0x7f) == 0 ? (status >> 8) & 0xff : 128 + (status & 0x7f);
	if (log >= 0) {
		char num[24], line[64];
		number(num, code);
		put(line, put(line, 0, "blizzmaria: exit "), num);
		put(line, len(line), "\n");
		logs(log, line);
	}
	sys6(SYS_exit_group, code, 0, 0, 0, 0, 0);
	for (;;) {}
}

/* The compiler may turn loops into calls to these; they are loops of their own that it can't. */
void *memcpy(void *d, const void *s, u64 n) { volatile char *a = d; const volatile char *b = s; while (n--) *a++ = *b++; return d; }
void *memset(void *d, int c, u64 n) { volatile char *a = d; while (n--) *a++ = (char)c; return d; }

__asm__(".text\n.global _start\n_start:\n\tmov x0, sp\n\tbl blizz_main\n");
