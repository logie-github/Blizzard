/* Warcraft III's movies decoded with FFmpeg (see player.h). */
#include "player.h"

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libavutil/channel_layout.h>
#include <libavutil/imgutils.h>
#include <libswresample/swresample.h>
#include <libswscale/swscale.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Movie {
	AVFormatContext *fmt;
	AVCodecContext *vdec, *adec;
	int vidx, aidx;
	AVPacket *pkt;
	AVFrame *frame;
	struct SwsContext *sws;
	SwrContext *swr;
	uint8_t *rgba;
	int stride;
	int16_t *pcm;
	int pcm_frames_cap;
	MovieInfo info;
	int eof, vflushed, aflushed;
	double last_video; /* the last picture's time, for one that comes without (the decoder's held-back last one) */
	AVCodecContext *pending; /* the decoder that may have frames to hand out */
};

static void say(char *err, size_t errlen, const char *what, int code) {
	if (!err || !errlen) return;
	if (code < 0) {
		char text[128];
		av_strerror(code, text, sizeof text);
		snprintf(err, errlen, "%s: %s", what, text);
	} else {
		snprintf(err, errlen, "%s", what);
	}
}

static AVCodecContext *open_decoder(AVFormatContext *fmt, int index, char *err, size_t errlen) {
	const AVCodecParameters *par = fmt->streams[index]->codecpar;
	const AVCodec *codec = avcodec_find_decoder(par->codec_id);
	if (!codec) {
		say(err, errlen, "no decoder for the movie's stream", 0);
		return NULL;
	}
	AVCodecContext *ctx = avcodec_alloc_context3(codec);
	if (!ctx) return NULL;
	int r = avcodec_parameters_to_context(ctx, par);
	if (r >= 0) r = avcodec_open2(ctx, codec, NULL);
	if (r < 0) {
		say(err, errlen, "the movie's decoder didn't open", r);
		avcodec_free_context(&ctx);
		return NULL;
	}
	return ctx;
}

Movie *movie_open(const char *path, char *err, size_t errlen) {
	Movie *m = calloc(1, sizeof *m);
	if (!m) return NULL;
	m->vidx = m->aidx = -1;
	m->last_video = -1;
	int r = avformat_open_input(&m->fmt, path, NULL, NULL);
	if (r < 0) {
		say(err, errlen, "the movie didn't open", r);
		free(m);
		return NULL;
	}
	r = avformat_find_stream_info(m->fmt, NULL);
	if (r < 0) {
		say(err, errlen, "the movie's streams weren't read", r);
		movie_close(m);
		return NULL;
	}
	m->vidx = av_find_best_stream(m->fmt, AVMEDIA_TYPE_VIDEO, -1, -1, NULL, 0);
	if (m->vidx < 0) {
		say(err, errlen, "the movie has no picture", 0);
		movie_close(m);
		return NULL;
	}
	m->vdec = open_decoder(m->fmt, m->vidx, err, errlen);
	if (!m->vdec) {
		movie_close(m);
		return NULL;
	}
	/* The sound is a help, not a must: a movie whose sound won't decode plays silent. */
	m->aidx = av_find_best_stream(m->fmt, AVMEDIA_TYPE_AUDIO, -1, m->vidx, NULL, 0);
	if (m->aidx >= 0) {
		m->adec = open_decoder(m->fmt, m->aidx, NULL, 0);
		if (!m->adec) m->aidx = -1;
	}
	m->pkt = av_packet_alloc();
	m->frame = av_frame_alloc();
	m->info.width = m->vdec->width;
	m->info.height = m->vdec->height;
	AVRational rate = av_guess_frame_rate(m->fmt, m->fmt->streams[m->vidx], NULL);
	m->info.fps = (rate.num > 0 && rate.den > 0) ? av_q2d(rate) : 0;
	m->info.duration = m->fmt->duration > 0 ? (double) m->fmt->duration / AV_TIME_BASE : 0;
	m->info.has_audio = m->adec != NULL;
	m->info.sample_rate = m->adec ? m->adec->sample_rate : 0;
	m->stride = m->info.width * 4;
	m->rgba = av_malloc((size_t) m->stride * (size_t) m->info.height);
	if (!m->pkt || !m->frame || !m->rgba || m->info.width <= 0 || m->info.height <= 0) {
		say(err, errlen, "the movie's picture has no size", 0);
		movie_close(m);
		return NULL;
	}
	return m;
}

const MovieInfo *movie_info(const Movie *m) { return &m->info; }

static double seconds(const Movie *m, int index, const AVFrame *f) {
	int64_t t = f->best_effort_timestamp;
	if (t == AV_NOPTS_VALUE) t = f->pts;
	if (t == AV_NOPTS_VALUE) return -1;
	return t * av_q2d(m->fmt->streams[index]->time_base);
}

static int picture(Movie *m, MovieEvent *ev) {
	AVFrame *f = m->frame;
	if (!m->sws) {
		m->sws = sws_getContext(f->width, f->height, f->format, m->info.width, m->info.height, AV_PIX_FMT_RGBA,
		                        SWS_BILINEAR, NULL, NULL, NULL);
		if (!m->sws) return -1;
	}
	uint8_t *dst[4] = {m->rgba, NULL, NULL, NULL};
	int dst_stride[4] = {m->stride, 0, 0, 0};
	sws_scale(m->sws, (const uint8_t *const *) f->data, f->linesize, 0, f->height, dst, dst_stride);
	double t = seconds(m, m->vidx, f);
	if (t < 0) t = m->last_video < 0 ? 0 : m->last_video + (m->info.fps > 0 ? 1.0 / m->info.fps : 1.0 / 24);
	m->last_video = t;
	ev->type = MOVIE_VIDEO;
	ev->pts = t;
	ev->rgba = m->rgba;
	ev->stride = m->stride;
	ev->pcm = NULL;
	ev->frames = 0;
	return MOVIE_VIDEO;
}

static int sound(Movie *m, MovieEvent *ev) {
	AVFrame *f = m->frame;
	if (!m->swr) {
		AVChannelLayout stereo = AV_CHANNEL_LAYOUT_STEREO;
		if (swr_alloc_set_opts2(&m->swr, &stereo, AV_SAMPLE_FMT_S16, m->info.sample_rate, &f->ch_layout, f->format,
		                        f->sample_rate, 0, NULL) < 0 || swr_init(m->swr) < 0) {
			return -1;
		}
	}
	int max = swr_get_out_samples(m->swr, f->nb_samples);
	if (max > m->pcm_frames_cap) {
		av_free(m->pcm);
		m->pcm = av_malloc((size_t) max * 2 * sizeof(int16_t));
		m->pcm_frames_cap = m->pcm ? max : 0;
		if (!m->pcm) return -1;
	}
	uint8_t *out[1] = {(uint8_t *) m->pcm};
	int n = swr_convert(m->swr, out, max, (const uint8_t **) f->extended_data, f->nb_samples);
	if (n < 0) return -1;
	ev->type = MOVIE_AUDIO;
	ev->pts = seconds(m, m->aidx, f);
	ev->rgba = NULL;
	ev->stride = 0;
	ev->pcm = m->pcm;
	ev->frames = n;
	return MOVIE_AUDIO;
}

int movie_next(Movie *m, MovieEvent *ev) {
	for (;;) {
		if (m->pending) {
			int r = avcodec_receive_frame(m->pending, m->frame);
			if (r == 0) {
				int got = m->pending == m->vdec ? picture(m, ev) : sound(m, ev);
				av_frame_unref(m->frame);
				/* A sound that comes out empty isn't handed out. */
				if (got == MOVIE_AUDIO && ev->frames == 0) continue;
				return got;
			}
			m->pending = NULL;
			if (r != AVERROR(EAGAIN) && r != AVERROR_EOF) return r;
		}
		if (m->eof) {
			/* The end: what the decoders still hold comes out. */
			if (!m->vflushed) {
				m->vflushed = 1;
				avcodec_send_packet(m->vdec, NULL);
				m->pending = m->vdec;
				continue;
			}
			if (m->adec && !m->aflushed) {
				m->aflushed = 1;
				avcodec_send_packet(m->adec, NULL);
				m->pending = m->adec;
				continue;
			}
			return MOVIE_END;
		}
		int r = av_read_frame(m->fmt, m->pkt);
		if (r == AVERROR_EOF) {
			m->eof = 1;
			continue;
		}
		if (r < 0) return r;
		AVCodecContext *dec = m->pkt->stream_index == m->vidx ? m->vdec : (m->pkt->stream_index == m->aidx ? m->adec : NULL);
		if (dec) {
			r = avcodec_send_packet(dec, m->pkt);
			/* A damaged packet is passed over, as a player does. */
			if (r >= 0 || r == AVERROR(EAGAIN)) m->pending = dec;
		}
		av_packet_unref(m->pkt);
	}
}

void movie_close(Movie *m) {
	if (!m) return;
	sws_freeContext(m->sws);
	swr_free(&m->swr);
	av_free(m->rgba);
	av_free(m->pcm);
	av_frame_free(&m->frame);
	av_packet_free(&m->pkt);
	avcodec_free_context(&m->vdec);
	avcodec_free_context(&m->adec);
	avformat_close_input(&m->fmt);
	free(m);
}
