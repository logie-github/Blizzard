package com.logie.blizz.music

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import java.nio.ByteBuffer
import kotlin.concurrent.thread

/** Decodes audio into a game AudioTrack. Launcher sounds have no system media player or transport session. */
internal class LauncherAudio(
    private val source: (MediaExtractor) -> Unit,
    private val loop: Boolean = false,
    private val prepared: () -> Unit = {},
    private val ended: () -> Unit = {},
    private val failed: () -> Unit = {},
) {
    @Volatile var isPlaying = false
        private set
    @Volatile var durationMs = 0
        private set
    @Volatile var positionMs = 0
        private set
    @Volatile var volume = 0f
    @Volatile private var closed = false
    private val playback = Object()

    private val worker = thread(start = false, name = "launcher-audio") {
        val extractor = MediaExtractor()
        var decoder: MediaCodec? = null
        var output: AudioTrack? = null
        try {
            source(extractor)
            if (closed) return@thread
            val index = (0 until extractor.trackCount).first { extractor.getTrackFormat(it).getString(MediaFormat.KEY_MIME)?.startsWith("audio/") == true }
            val format = extractor.getTrackFormat(index)
            extractor.selectTrack(index)
            if (format.containsKey(MediaFormat.KEY_DURATION)) {
                durationMs = (format.getLong(MediaFormat.KEY_DURATION) / 1000).coerceIn(0, Int.MAX_VALUE.toLong()).toInt()
            }
            val codec = MediaCodec.createDecoderByType(checkNotNull(format.getString(MediaFormat.KEY_MIME))).also { decoder = it }
            codec.configure(format, null, null, 0)
            codec.start()
            prepared()
            val info = MediaCodec.BufferInfo()
            var inputEnded = false
            var outputIndex = -1
            var pendingAudio: ByteBuffer? = null
            var bytesPerFrame = 0
            var sampleRate = 0
            var framesWritten = 0L
            var appliedVolume = Float.NaN

            while (!closed) {
                val track = output
                if (!isPlaying) {
                    if (track?.playState == AudioTrack.PLAYSTATE_PLAYING) track.pause()
                    synchronized(playback) {
                        if (!isPlaying && !closed) playback.wait()
                    }
                    continue
                }
                if (track != null) {
                    val level = volume
                    if (appliedVolume != level) {
                        track.setVolume(level)
                        appliedVolume = level
                    }
                    if (track.playState != AudioTrack.PLAYSTATE_PLAYING) track.play()
                    if (!loop) positionMs = (playedFrames(track) * 1000 / sampleRate).toInt()
                }
                if (!inputEnded) {
                    val inputIndex = codec.dequeueInputBuffer(0)
                    if (inputIndex >= 0) {
                        val input = checkNotNull(codec.getInputBuffer(inputIndex))
                        val size = extractor.readSampleData(input, 0)
                        inputEnded = size < 0
                        codec.queueInputBuffer(inputIndex, 0, size.coerceAtLeast(0), extractor.sampleTime.coerceAtLeast(0),
                            if (inputEnded) MediaCodec.BUFFER_FLAG_END_OF_STREAM else 0)
                        if (!inputEnded) extractor.advance()
                    }
                }
                if (outputIndex < 0) outputIndex = codec.dequeueOutputBuffer(info, 5_000)
                when {
                    outputIndex == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED -> {
                        val pcm = codec.outputFormat
                        if (output == null) {
                            sampleRate = pcm.getInteger(MediaFormat.KEY_SAMPLE_RATE)
                            val channels = pcm.getInteger(MediaFormat.KEY_CHANNEL_COUNT)
                            val encoding = if (pcm.containsKey(MediaFormat.KEY_PCM_ENCODING)) pcm.getInteger(MediaFormat.KEY_PCM_ENCODING)
                                else AudioFormat.ENCODING_PCM_16BIT
                            bytesPerFrame = channels * when (encoding) {
                                AudioFormat.ENCODING_PCM_FLOAT -> 4
                                AudioFormat.ENCODING_PCM_8BIT -> 1
                                else -> 2
                            }
                            output = audioTrack(sampleRate, channels, encoding)
                        }
                    }
                    outputIndex >= 0 -> {
                        if (info.size > 0) {
                            val audio = pendingAudio ?: checkNotNull(codec.getOutputBuffer(outputIndex)).also { pendingAudio = it }
                            val written = checkNotNull(output).write(audio, audio.remaining(), AudioTrack.WRITE_NON_BLOCKING)
                            check(written >= 0) { "AudioTrack write failed ($written)" }
                            framesWritten += written / bytesPerFrame
                            if (audio.hasRemaining()) {
                                Thread.sleep(5)
                                continue
                            }
                        }
                        val finished = info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0
                        codec.releaseOutputBuffer(outputIndex, false)
                        pendingAudio = null
                        outputIndex = -1
                        if (finished) {
                            if (!loop) {
                                val sink = checkNotNull(output)
                                while (!closed && playedFrames(sink) < framesWritten) {
                                    if (!isPlaying && sink.playState == AudioTrack.PLAYSTATE_PLAYING) sink.pause()
                                    if (isPlaying && sink.playState != AudioTrack.PLAYSTATE_PLAYING) sink.play()
                                    positionMs = (playedFrames(sink) * 1000 / sampleRate).toInt()
                                    Thread.sleep(10)
                                }
                                if (closed) break
                                sink.pause()
                                sink.flush()
                                framesWritten = 0
                                positionMs = 0
                                isPlaying = false
                            }
                            extractor.seekTo(0, MediaExtractor.SEEK_TO_CLOSEST_SYNC)
                            codec.flush()
                            inputEnded = false
                            if (!loop) ended()
                        }
                    }
                }
            }
        } catch (_: Exception) {
            if (!closed) failed()
        } finally {
            isPlaying = false
            runCatching { output?.release() }
            runCatching { decoder?.release() }
            runCatching { extractor.release() }
        }
    }

    fun prepare() = worker.start()
    fun start() = synchronized(playback) {
        if (!closed) {
            isPlaying = true
            playback.notifyAll()
        }
    }
    fun pause() { isPlaying = false }
    fun release() { closed = true; worker.interrupt() }

    private fun playedFrames(track: AudioTrack): Long = track.playbackHeadPosition.toLong() and 0xffffffffL

    private fun audioTrack(rate: Int, channels: Int, encoding: Int): AudioTrack {
        val mask = when (channels) {
            1 -> AudioFormat.CHANNEL_OUT_MONO
            2 -> AudioFormat.CHANNEL_OUT_STEREO
            4 -> AudioFormat.CHANNEL_OUT_QUAD
            6 -> AudioFormat.CHANNEL_OUT_5POINT1
            8 -> AudioFormat.CHANNEL_OUT_7POINT1_SURROUND
            else -> error("Unsupported channel count: $channels")
        }
        val buffer = AudioTrack.getMinBufferSize(rate, mask, encoding)
        check(buffer > 0) { "Unsupported audio format" }
        return AudioTrack.Builder()
            .setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).build())
            .setAudioFormat(AudioFormat.Builder().setSampleRate(rate).setChannelMask(mask).setEncoding(encoding).build())
            .setBufferSizeInBytes(buffer)
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()
    }
}
