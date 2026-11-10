/* Host stand-in for Android's sharedmem.h (tools/xrig). */
#ifndef XRIG_ANDROID_SHAREDMEM_H
#define XRIG_ANDROID_SHAREDMEM_H
#include <stddef.h>
int ASharedMemory_create(const char *name, size_t size);
#endif
