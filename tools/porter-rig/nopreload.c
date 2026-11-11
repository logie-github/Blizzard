/*
 * The rig's MySQLExecutable: the machine's own mariadb client, started without LD_PRELOAD.
 *
 * dbimport and the world server (arm64 programs under qemu on the rig) run the client by their
 * MySQLExecutable setting, and hand their own LD_PRELOAD (the realm's arm64 compatibility library)
 * down to it. The machine's client would say "cannot be preloaded" on every file it applies. This is
 * linked statically (no dynamic loader, so the variable means nothing to it), drops the variable and
 * runs the real client with the same arguments.
 *
 *   cc -static -O1 -o maria nopreload.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
	(void)argc;
	const char *client = getenv("RIG_MARIADB");
	if (!client || !*client) client = "/usr/bin/mariadb";
	unsetenv("LD_PRELOAD");
	/* (the client warns when it is started under any name but its own) */
	argv[0] = (char *)client;
	execv(client, argv);
	perror(client);
	return 127;
}
