/*
 * The mariadb client as dbimport and the world server run it (their MySQLExecutable setting).
 *
 * The server's programs are musl programs started through the musl loader, with a compatibility
 * library preloaded (LD_PRELOAD), and that variable is inherited by whatever they start. A shell
 * script as the client would be run by Android's own /system/bin/sh, which cannot load that library
 * and stops. This program is built static, so Android's dynamic linker never looks at LD_PRELOAD for
 * it: it starts the real client through the musl loader, with the library preloaded for that alone.
 *
 * BLIZZ_LDSO (the musl loader) and BLIZZ_SERVER (the server's folder) come from the environment the
 * realm's commands are started with. Everything else is passed on as it is (the SQL arrives on stdin).
 */
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char **argv) {
	const char *loader = getenv("BLIZZ_LDSO");
	const char *server = getenv("BLIZZ_SERVER");
	const char *logpath = getenv("BLIZZ_LOG");
	FILE *log = logpath ? fopen(logpath, "a") : NULL;
	if (!loader || !server) {
		fputs("blizzmaria: BLIZZ_LDSO and BLIZZ_SERVER are not set\n", stderr);
		if (log) fputs("blizzmaria: BLIZZ_LDSO and BLIZZ_SERVER are not set\n", log);
		return 127;
	}
	char lib[4096], bin[4096], preload[4096];
	snprintf(lib, sizeof lib, "%s/lib", server);
	snprintf(bin, sizeof bin, "%s/bin/mariadb", server);
	snprintf(preload, sizeof preload, "%s/lib/libandroidcompat.so", server);
	setenv("LD_PRELOAD", preload, 1);
	char **args = malloc((argc + 5) * sizeof *args);
	if (!args) return 127;
	int n = 0;
	args[n++] = (char *)loader;
	args[n++] = "--library-path";
	args[n++] = lib;
	args[n++] = bin;
	for (int i = 1; i < argc; i++) args[n++] = argv[i];
	args[n] = NULL;
	if (log) {
		/* What it was asked to do (the password's value never goes in the log), then what came of it. */
		fprintf(log, "blizzmaria:");
		for (int i = 1; i < argc; i++) fprintf(log, " %s", strncmp(argv[i], "-p", 2) == 0 ? "-p***" : argv[i]);
		fprintf(log, "\n");
		fflush(log);
	}
	pid_t pid = fork();
	if (pid < 0) {
		if (log) fprintf(log, "blizzmaria: fork failed\n");
		return 127;
	}
	if (pid == 0) {
		/* The client's own messages go to the log: dbimport doesn't show them. */
		if (log) { dup2(fileno(log), 2); }
		execv(loader, args);
		perror("blizzmaria: exec of the musl loader");
		_exit(127);
	}
	int status = 0;
	waitpid(pid, &status, 0);
	int code = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
	if (log) { fprintf(log, "blizzmaria: exit %d\n", code); fclose(log); }
	return code;
}
