/*
 * Host stand-in for Winlator's OpenGL renderer library (tools/xrig): the X server's GLX extension loads it by name as
 * the server starts. There is no GPU path in the rig; a program that asks for a GL context gets none (0).
 */
#include <jni.h>

JNIEXPORT jlong JNICALL Java_com_winlator_xserver_extensions_GLXExtension_createGLContext(JNIEnv *env, jobject obj, jint clientFd) { (void)env; (void)obj; (void)clientFd; return 0; }
JNIEXPORT void JNICALL Java_com_winlator_xserver_extensions_GLXExtension_destroyGLContext(JNIEnv *env, jobject obj, jlong contextPtr) { (void)env; (void)obj; (void)contextPtr; }
JNIEXPORT jlong JNICALL Java_com_winlator_xserver_extensions_GLXExtension_createGLXContext(JNIEnv *env, jobject obj, jint contextId, jlong sharedContextPtr) { (void)env; (void)obj; (void)contextId; (void)sharedContextPtr; return 0; }
JNIEXPORT void JNICALL Java_com_winlator_xserver_extensions_GLXExtension_destroyGLXContext(JNIEnv *env, jobject obj, jlong contextPtr) { (void)env; (void)obj; (void)contextPtr; }
