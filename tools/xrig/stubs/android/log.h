/* Host stand-in for Android's log.h (tools/xrig): the X server's native code logs to stderr. */
#ifndef XRIG_ANDROID_LOG_H
#define XRIG_ANDROID_LOG_H
#include <stdio.h>
enum { ANDROID_LOG_VERBOSE = 2, ANDROID_LOG_DEBUG, ANDROID_LOG_INFO, ANDROID_LOG_WARN, ANDROID_LOG_ERROR };
#define __android_log_print(prio, tag, ...) (fprintf(stderr, "[%s] ", tag), fprintf(stderr, __VA_ARGS__), fprintf(stderr, "\n"))
#endif
