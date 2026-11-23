#ifndef BLIZZ_INFINITE_H
#define BLIZZ_INFINITE_H

#include <windows.h>

BOOL infinite_start(void);
BOOL infinite_poll(void);
BOOL infinite_stop_requested(void);
BOOL infinite_service(DWORD pid);
void infinite_stop(void);

void note(const char *format, ...);

#endif
