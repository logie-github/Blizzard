/* Host stand-in for Android's bitmap.h (tools/xrig): no bitmaps here; cursors and icons are not drawn. */
#ifndef XRIG_ANDROID_BITMAP_H
#define XRIG_ANDROID_BITMAP_H
#include <jni.h>
#include <stdint.h>
typedef struct { uint32_t width, height, stride; int32_t format; uint32_t flags; } AndroidBitmapInfo;
static inline int AndroidBitmap_getInfo(JNIEnv *env, jobject bitmap, AndroidBitmapInfo *info) { (void)env; (void)bitmap; info->width = info->height = info->stride = 0; info->format = 0; info->flags = 0; return -1; }
static inline int AndroidBitmap_lockPixels(JNIEnv *env, jobject bitmap, void **pixels) { (void)env; (void)bitmap; *pixels = 0; return -1; }
static inline int AndroidBitmap_unlockPixels(JNIEnv *env, jobject bitmap) { (void)env; (void)bitmap; return 0; }
#endif
