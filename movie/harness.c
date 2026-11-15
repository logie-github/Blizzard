/*
 * The desktop check of the movie decoding (player.c), built against FFmpeg built for this machine
 * (scripts/build-ffmpeg.sh --host; movie/build-harness.sh):
 *
 *   harness MOVIE.bik OUT_DIR
 *
 * Decodes the whole movie as the phone does and prints what it found (size, rate, frames, sound, the timestamps' order);
 * writes the first, middle and last pictures as OUT_DIR/frame-N.ppm and the sound as OUT_DIR/sound.wav.
 * Exit 0 when the movie decoded to its end with its timestamps in order.
 */
#include "player.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void write_ppm(const char *path, const uint8_t *rgba, int stride, int w, int h) {
	FILE *f = fopen(path, "wb");
	if (!f) return;
	fprintf(f, "P6\n%d %d\n255\n", w, h);
	for (int y = 0; y < h; y++) {
		const uint8_t *row = rgba + (size_t) y * stride;
		for (int x = 0; x < w; x++) fwrite(row + x * 4, 1, 3, f);
	}
	fclose(f);
}

static void put32(FILE *f, uint32_t v) { fputc(v & 255, f); fputc((v >> 8) & 255, f); fputc((v >> 16) & 255, f); fputc(v >> 24, f); }
static void put16(FILE *f, uint16_t v) { fputc(v & 255, f); fputc(v >> 8, f); }

int main(int argc, char **argv) {
	if (argc < 3) {
		fprintf(stderr, "usage: %s MOVIE OUT_DIR\n", argv[0]);
		return 2;
	}
	char err[256] = "";
	Movie *m = movie_open(argv[1], err, sizeof err);
	if (!m) {
		fprintf(stderr, "open failed: %s\n", err);
		return 1;
	}
	const MovieInfo *info = movie_info(m);
	printf("picture %dx%d, %.3f fps, duration %.2f s, sound %s %d Hz\n", info->width, info->height, info->fps,
	       info->duration, info->has_audio ? "yes" : "no", info->sample_rate);

	/* First pass: count, to know the middle picture. */
	int pictures = 0;
	long sound_frames = 0;
	double last_video = -1, last_audio = -1;
	int out_of_order = 0;
	MovieEvent ev;
	int r;
	while ((r = movie_next(m, &ev)) > 0) {
		if (ev.type == MOVIE_VIDEO) {
			if (ev.pts < last_video) out_of_order++;
			last_video = ev.pts;
			pictures++;
		} else {
			if (ev.pts >= 0 && ev.pts < last_audio) out_of_order++;
			if (ev.pts >= 0) last_audio = ev.pts;
			sound_frames += ev.frames;
		}
	}
	movie_close(m);
	if (r < 0) {
		fprintf(stderr, "decoding stopped with error %d after %d pictures\n", r, pictures);
		return 1;
	}
	printf("%d pictures, last at %.3f s; sound %.3f s (%ld frames), last at %.3f s; out of order: %d\n", pictures,
	       last_video, info->sample_rate ? (double) sound_frames / info->sample_rate : 0, sound_frames, last_audio,
	       out_of_order);

	/* Second pass: the pictures to look at and the sound to hear. */
	m = movie_open(argv[1], err, sizeof err);
	char path[1024];
	snprintf(path, sizeof path, "%s/sound.wav", argv[2]);
	FILE *wav = info->has_audio ? fopen(path, "wb") : NULL;
	int rate = info->sample_rate;
	if (wav) {
		fwrite("RIFF", 1, 4, wav); put32(wav, 36 + (uint32_t) sound_frames * 4); fwrite("WAVEfmt ", 1, 8, wav);
		put32(wav, 16); put16(wav, 1); put16(wav, 2); put32(wav, (uint32_t) rate); put32(wav, (uint32_t) rate * 4);
		put16(wav, 4); put16(wav, 16); fwrite("data", 1, 4, wav); put32(wav, (uint32_t) sound_frames * 4);
	}
	int index = 0;
	int wanted[3] = {0, pictures / 2, pictures - 1};
	while (movie_next(m, &ev) > 0) {
		if (ev.type == MOVIE_VIDEO) {
			for (int i = 0; i < 3; i++) {
				if (index == wanted[i]) {
					snprintf(path, sizeof path, "%s/frame-%d.ppm", argv[2], index);
					write_ppm(path, ev.rgba, ev.stride, info->width, info->height);
				}
			}
			index++;
		} else if (wav) {
			fwrite(ev.pcm, 4, (size_t) ev.frames, wav);
		}
	}
	if (wav) fclose(wav);
	movie_close(m);
	return out_of_order == 0 && pictures > 0 ? 0 : 1;
}
