#pragma once
#include <cstdio>
#define ANDROID_LOG_INFO 4
#define ANDROID_LOG_ERROR 6
#define ANDROID_LOG_DEBUG 3
#define __android_log_print(p,t,...) (fprintf(stderr,__VA_ARGS__),0)
