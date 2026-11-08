/*
 * Preloaded into the server's programs (ctl.sh): system calls Android's seccomp policy doesn't
 * allow apps, made with ones it does. Android kills a process that makes a call outside the policy,
 * and the server's programs run as the app.
 *
 * - accept: bionic has only accept4, so the policy has only accept4; musl's accept is the accept
 *   system call, and so is its accept4 without flags. Boost.Asio (the auth and world servers) uses
 *   accept for every new connection.
 * - setfsuid, setfsgid: ncurses calls them around opening a terminfo file, which the world
 *   server's console (readline) does once the world is up. An app's process runs with one user
 *   and group id, so its filesystem ids never change: the calls change nothing, and return the
 *   id, as the system calls do when they change nothing.
 */
#define _GNU_SOURCE
#include <sys/fsuid.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <unistd.h>

int accept(int fd, struct sockaddr *restrict addr, socklen_t *restrict len)
{
	return syscall(SYS_accept4, fd, addr, len, 0);
}

int accept4(int fd, struct sockaddr *restrict addr, socklen_t *restrict len, int flags)
{
	return syscall(SYS_accept4, fd, addr, len, flags);
}

int setfsuid(uid_t uid)
{
	(void)uid;
	return (int)getuid();
}

int setfsgid(gid_t gid)
{
	(void)gid;
	return (int)getgid();
}
