/*
 * Warcraft III's movies (Bink 1 video, Bink audio) decoded with FFmpeg: the frames as RGBA pictures and the sound as
 * 16-bit stereo, in the order the file holds them. The phone's player (android.c) puts them on the screen and through
 * AAudio; the desktop harness (harness.c) checks them.
 */
#ifndef WC3_MOVIE_PLAYER_H
#define WC3_MOVIE_PLAYER_H

#include <stddef.h>
#include <stdint.h>

typedef struct Movie Movie;

typedef struct MovieInfo {
	int width, height;   /* the picture's size */
	double fps;          /* frames per second (the file's own rate) */
	double duration;     /* seconds, 0 when unknown */
	int has_audio;
	int sample_rate;     /* of the sound handed out (the file's own), 0 without sound */
} MovieInfo;

enum { MOVIE_END = 0, MOVIE_VIDEO = 1, MOVIE_AUDIO = 2 };

typedef struct MovieEvent {
	int type;               /* MOVIE_VIDEO or MOVIE_AUDIO */
	double pts;             /* seconds from the movie's start */
	const uint8_t *rgba;    /* MOVIE_VIDEO: width x height pixels, 4 bytes each, [stride] bytes a row */
	int stride;
	const int16_t *pcm;     /* MOVIE_AUDIO: [frames] stereo frames, interleaved */
	int frames;
} MovieEvent;

/* Opens [path]; null with the reason in [err] when it can't be played. */
Movie *movie_open(const char *path, char *err, size_t errlen);
const MovieInfo *movie_info(const Movie *m);
/* The next picture or sound: MOVIE_VIDEO, MOVIE_AUDIO, MOVIE_END at the end, below 0 on an error. What [ev] points at
 * stays good until the next call. */
int movie_next(Movie *m, MovieEvent *ev);
void movie_close(Movie *m);

#endif
