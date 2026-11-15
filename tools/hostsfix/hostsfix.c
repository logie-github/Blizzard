/*
 * libblizzhosts.so: the names in the app's own hosts file, for programs run by Android itself (the Forever container's Wine).
 *
 * Android's resolver reads only /system/etc/hosts and the system's DNS; the hosts file the app writes in the container's image
 * is never looked at (seen on the Android rig, 15 November 2026: getaddrinfo(trinity.actual.battle.net) = EAI_NODATA, the
 * game's sign-in ending with ERROR_NETWORK_MODULE_SOCKET_CLOSED). Preloaded first (LD_PRELOAD), this answers getaddrinfo for
 * a name in the file $BLIZZ_HOSTS (`address name [name...]` per line) with that address, and passes every other name on.
 */
#define _GNU_SOURCE
#include <ctype.h>
#include <dlfcn.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

/* The address [name] has in the hosts file, into [out]; 0 when it isn't there. */
static int lookup(const char *name, char *out, size_t size) {
    const char *path = getenv("BLIZZ_HOSTS");
    char line[512];
    FILE *f;
    int found = 0;
    if (!path || !name || !*name) return 0;
    f = fopen(path, "re");
    if (!f) return 0;
    while (!found && fgets(line, sizeof(line), f)) {
        char *save = NULL, *address, *word;
        char *hash = strchr(line, '#');
        if (hash) *hash = 0;
        address = strtok_r(line, " \t\r\n", &save);
        if (!address) continue;
        while ((word = strtok_r(NULL, " \t\r\n", &save)))
            if (!strcasecmp(word, name) && strlen(address) < size) { strcpy(out, address); found = 1; break; }
    }
    fclose(f);
    return found;
}

int getaddrinfo(const char *node, const char *service, const struct addrinfo *hints, struct addrinfo **res) {
    static int (*next)(const char *, const char *, const struct addrinfo *, struct addrinfo **);
    char address[64];
    if (!next) next = (int (*)(const char *, const char *, const struct addrinfo *, struct addrinfo **)) dlsym(RTLD_NEXT, "getaddrinfo");
    if (!next) return EAI_FAIL;
    if (node && lookup(node, address, sizeof(address))) {
        int result = next(address, service, hints, res);
        if (getenv("BLIZZ_HOSTS_LOG")) fprintf(stderr, "[blizzhosts] %s is %s (%d)\n", node, address, result);
        return result;
    }
    return next(node, service, hints, res);
}
