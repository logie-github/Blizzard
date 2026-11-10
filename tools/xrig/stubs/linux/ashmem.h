/* Host stand-in for linux/ashmem.h (tools/xrig): gone from mainline headers; only the names the code compiles against. */
#ifndef XRIG_LINUX_ASHMEM_H
#define XRIG_LINUX_ASHMEM_H
#include <sys/ioctl.h>
#define ASHMEM_NAME_LEN 256
#define ASHMEM_SET_NAME _IOW(0x77, 1, char[ASHMEM_NAME_LEN])
#define ASHMEM_SET_SIZE _IOW(0x77, 3, size_t)
#endif
