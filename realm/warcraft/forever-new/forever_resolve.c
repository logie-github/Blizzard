/*
 * Preloaded into Forever's programs. The login server resolves its own portal name (trinity.actual.battle.net, upstream
 * doc/ForeverSetup.md) when it starts and stops with "Could not resolve LoginREST.ExternalAddress" if it can't; Android has
 * no hosts file an app may edit, and the runtime's own hosts file belongs to the game's Wine. So the name is answered here,
 * for these programs only: any name under actual.battle.net is this phone (127.0.0.1). Every other name goes to the
 * C library unchanged. Nothing global is edited and no root is needed.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <netdb.h>
#include <string.h>
#include <strings.h>

static int under_portal(const char *name)
{
	static const char suffix[] = ".actual.battle.net";
	size_t n = strlen(name), s = sizeof suffix - 1;
	return n > s && strcasecmp(name + n - s, suffix) == 0;
}

int getaddrinfo(const char *node, const char *service, const struct addrinfo *hints, struct addrinfo **res)
{
	static int (*real)(const char *, const char *, const struct addrinfo *, struct addrinfo **);
	if (!real) real = (int (*)(const char *, const char *, const struct addrinfo *, struct addrinfo **))dlsym(RTLD_NEXT, "getaddrinfo");
	if (node && under_portal(node)) node = "127.0.0.1";
	return real(node, service, hints, res);
}
