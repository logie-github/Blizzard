/*
 * The phone's movie player (com.logie.blizz.warsmash.MovieNative): a movie decoded by player.c, its pictures drawn on an
 * Android surface at their time and its sound played through AAudio. The caller's thread runs the movie (run) until it
 * ends or stop is asked (a tap, Back).
 */
#include "player.h"

#include <aaudio/AAudio.h>
#include <android/log.h>
#include <android/native_window.h>
#include <android/native_window_jni.h>
#include <jni.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define TAG "Wc3Movie"
#define LOG(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

typedef struct Player {
	Movie *movie;
	atomic_int stop;
	/* The sound waiting to be played: stereo frames, written by the decoding, read by AAudio's callback. */
	int16_t *ring;
	int capacity; /* frames */
	atomic_long written, read;
} Player;

static double now(void) {
	struct timespec t;
	clock_gettime(CLOCK_MONOTONIC, &t);
	return t.tv_sec + t.tv_nsec / 1e9;
}

static aaudio_data_callback_result_t on_sound(AAudioStream *stream, void *user, void *data, int32_t frames) {
	(void) stream;
	Player *p = user;
	int16_t *out = data;
	long r = atomic_load(&p->read);
	long avail = atomic_load(&p->written) - r;
	int n = avail < frames ? (int) avail : frames;
	for (int i = 0; i < n; i++) {
		int at = (int) ((r + i) % p->capacity);
		out[i * 2] = p->ring[at * 2];
		out[i * 2 + 1] = p->ring[at * 2 + 1];
	}
	memset(out + n * 2, 0, (size_t) (frames - n) * 4);
	atomic_store(&p->read, r + n);
	return AAUDIO_CALLBACK_RESULT_CONTINUE;
}

/* Puts [frames] of sound in the ring, waiting while it is full (the movie's sound runs ahead of its pictures). */
static void queue_sound(Player *p, const int16_t *pcm, int frames) {
	int done = 0;
	while (done < frames && !atomic_load(&p->stop)) {
		long w = atomic_load(&p->written);
		long room = p->capacity - (w - atomic_load(&p->read));
		if (room <= 0) {
			usleep(2000);
			continue;
		}
		int n = frames - done < room ? frames - done : (int) room;
		for (int i = 0; i < n; i++) {
			int at = (int) ((w + i) % p->capacity);
			p->ring[at * 2] = pcm[(done + i) * 2];
			p->ring[at * 2 + 1] = pcm[(done + i) * 2 + 1];
		}
		atomic_store(&p->written, w + n);
		done += n;
	}
}

static AAudioStream *open_sound(Player *p, int rate) {
	AAudioStreamBuilder *b = NULL;
	if (AAudio_createStreamBuilder(&b) != AAUDIO_OK) return NULL;
	AAudioStreamBuilder_setFormat(b, AAUDIO_FORMAT_PCM_I16);
	AAudioStreamBuilder_setChannelCount(b, 2);
	AAudioStreamBuilder_setSampleRate(b, rate);
	AAudioStreamBuilder_setPerformanceMode(b, AAUDIO_PERFORMANCE_MODE_NONE);
	AAudioStreamBuilder_setDataCallback(b, on_sound, p);
	AAudioStream *s = NULL;
	aaudio_result_t r = AAudioStreamBuilder_openStream(b, &s);
	AAudioStreamBuilder_delete(b);
	if (r != AAUDIO_OK) {
		LOG("sound didn't open: %s", AAudio_convertResultToText(r));
		return NULL;
	}
	return s;
}

JNIEXPORT jlong JNICALL Java_com_logie_blizz_warsmash_MovieNative_open(JNIEnv *env, jclass cls, jstring jpath) {
	(void) cls;
	const char *path = (*env)->GetStringUTFChars(env, jpath, NULL);
	char err[256] = "";
	Movie *m = movie_open(path, err, sizeof err);
	(*env)->ReleaseStringUTFChars(env, jpath, path);
	if (!m) {
		jclass io = (*env)->FindClass(env, "java/io/IOException");
		(*env)->ThrowNew(env, io, err[0] ? err : "the movie didn't open");
		return 0;
	}
	Player *p = calloc(1, sizeof *p);
	p->movie = m;
	const MovieInfo *info = movie_info(m);
	if (info->has_audio) {
		p->capacity = info->sample_rate * 4; /* four seconds */
		p->ring = calloc((size_t) p->capacity * 2, sizeof(int16_t));
	}
	return (jlong) (intptr_t) p;
}

JNIEXPORT jintArray JNICALL Java_com_logie_blizz_warsmash_MovieNative_size(JNIEnv *env, jclass cls, jlong handle) {
	(void) cls;
	Player *p = (Player *) (intptr_t) handle;
	const MovieInfo *info = movie_info(p->movie);
	jint values[2] = {info->width, info->height};
	jintArray out = (*env)->NewIntArray(env, 2);
	(*env)->SetIntArrayRegion(env, out, 0, 2, values);
	return out;
}

/* Plays the movie on [surface]; 0 when it ended, 1 when it was stopped, below 0 when it couldn't go on. */
JNIEXPORT jint JNICALL Java_com_logie_blizz_warsmash_MovieNative_run(JNIEnv *env, jclass cls, jlong handle, jobject surface) {
	(void) cls;
	Player *p = (Player *) (intptr_t) handle;
	const MovieInfo *info = movie_info(p->movie);
	ANativeWindow *window = ANativeWindow_fromSurface(env, surface);
	if (!window) return -1;
	ANativeWindow_setBuffersGeometry(window, info->width, info->height, WINDOW_FORMAT_RGBA_8888);
	AAudioStream *sound = info->has_audio && p->ring ? open_sound(p, info->sample_rate) : NULL;
	double start = -1;
	int result = 0;
	MovieEvent ev;
	for (;;) {
		if (atomic_load(&p->stop)) {
			result = 1;
			break;
		}
		int r = movie_next(p->movie, &ev);
		if (r == MOVIE_END) break;
		if (r < 0) {
			LOG("decoding stopped: %d", r);
			result = r;
			break;
		}
		if (ev.type == MOVIE_AUDIO) {
			if (sound) queue_sound(p, ev.pcm, ev.frames);
			continue;
		}
		/* The movie's clock starts with its first picture, and its sound with it. */
		if (start < 0) {
			start = now();
			if (sound) AAudioStream_requestStart(sound);
		}
		double due = start + (ev.pts > 0 ? ev.pts : 0);
		for (double t = now(); t < due && !atomic_load(&p->stop); t = now()) {
			double wait = due - t;
			usleep((useconds_t) ((wait > 0.005 ? 0.005 : wait) * 1e6));
		}
		/* A picture more than a quarter second late is passed over: the sound keeps the time. */
		if (now() - due > 0.25) continue;
		ANativeWindow_Buffer buffer;
		if (ANativeWindow_lock(window, &buffer, NULL) == 0) {
			uint8_t *dst = buffer.bits;
			for (int y = 0; y < info->height && y < buffer.height; y++) {
				memcpy(dst + (size_t) y * buffer.stride * 4, ev.rgba + (size_t) y * ev.stride,
				       (size_t) (info->width < buffer.width ? info->width : buffer.width) * 4);
			}
			ANativeWindow_unlockAndPost(window);
		}
	}
	if (sound) {
		/* The last of the sound plays out (up to a second), unless the movie was stopped. */
		double until = now() + 1;
		while (!atomic_load(&p->stop) && atomic_load(&p->written) > atomic_load(&p->read) && now() < until) usleep(5000);
		AAudioStream_requestStop(sound);
		AAudioStream_close(sound);
	}
	ANativeWindow_release(window);
	return result;
}

JNIEXPORT void JNICALL Java_com_logie_blizz_warsmash_MovieNative_stop(JNIEnv *env, jclass cls, jlong handle) {
	(void) env;
	(void) cls;
	Player *p = (Player *) (intptr_t) handle;
	atomic_store(&p->stop, 1);
}

JNIEXPORT void JNICALL Java_com_logie_blizz_warsmash_MovieNative_close(JNIEnv *env, jclass cls, jlong handle) {
	(void) env;
	(void) cls;
	Player *p = (Player *) (intptr_t) handle;
	if (!p) return;
	movie_close(p->movie);
	free(p->ring);
	free(p);
}
