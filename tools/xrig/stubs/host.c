/* Host stand-ins for what the X server's native code takes from Android (tools/xrig). */
#include <sys/syscall.h>
#include <unistd.h>
#include <stddef.h>
#include "android/sharedmem.h"

/* Shared memory by name and size: an anonymous memory file, as Android's ashmem region is to its users. */
int ASharedMemory_create(const char *name, size_t size) {
    int fd = (int)syscall(SYS_memfd_create, name ? name : "xrig", 0);
    if (fd < 0) return -1;
    if (ftruncate(fd, (off_t)size) < 0) { close(fd); return -1; }
    return fd;
}

/*
 * Shared memory segments of this machine's own (System V), for the X server's MIT-SHM requests: on the phone the X
 * library of the games' Windows gets its segments from Winlator's own shared memory service and the server knows them by
 * number; here Wine's X library takes them from the kernel, and the server is handed them by these two (HostShm, in the
 * rig's test sources). Without them the server took the attach in silence and refused the first picture drawn from one
 * (BadShmSeg), which ends an X program.
 */
#include <jni.h>
#include <sys/ipc.h>
#include <sys/shm.h>

JNIEXPORT jobject JNICALL Java_com_logie_blizz_rig_HostShm_attach(JNIEnv *env, jclass cls, jint shmid) {
    struct shmid_ds info;
    void *memory;
    (void)cls;
    if (shmctl(shmid, IPC_STAT, &info) < 0) return NULL;
    memory = shmat(shmid, NULL, SHM_RDONLY);
    if (memory == (void *)-1) return NULL;
    return (*env)->NewDirectByteBuffer(env, memory, (jlong)info.shm_segsz);
}

JNIEXPORT void JNICALL Java_com_logie_blizz_rig_HostShm_detach(JNIEnv *env, jclass cls, jobject data) {
    void *memory = (*env)->GetDirectBufferAddress(env, data);
    (void)cls;
    if (memory) shmdt(memory);
}
