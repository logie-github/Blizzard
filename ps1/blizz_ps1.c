// SPDX-License-Identifier: GPL-2.0-or-later
#include <jni.h>
#include <libretro.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define MAX_WIDTH 1024
#define MAX_HEIGHT 512

static char directory[1024], image[1024];
static uint32_t pixels[MAX_WIDTH * MAX_HEIGHT];
static int width, height, buttons;
static enum retro_pixel_format pixel_format;
static int16_t samples[16384];
static size_t sample_count;
static bool attempted, loaded, compatibility;

static bool environment(unsigned command, void *data)
{
    switch (command) {
    case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:
    case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY:
        *(const char **)data = directory;
        return true;
    case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT: {
        enum retro_pixel_format requested = *(const enum retro_pixel_format *)data;
        if (requested != RETRO_PIXEL_FORMAT_RGB565 && requested != RETRO_PIXEL_FORMAT_XRGB8888)
            return false;
        pixel_format = requested;
        return true;
    }
    case RETRO_ENVIRONMENT_GET_VARIABLE: {
        struct retro_variable *variable = data;
        if (strcmp(variable->key, "pcsx_rearmed_memcard1") == 0)
            variable->value = "shared";
        else if (strcmp(variable->key, "pcsx_rearmed_memcard2") == 0)
            variable->value = "disabled";
        else if (compatibility &&
                 (!strcmp(variable->key, "pcsx_rearmed_drc") ||
                  !strcmp(variable->key, "pcsx_rearmed_gpu_thread_rendering") ||
                  !strcmp(variable->key, "pcsx_rearmed_spu_thread")))
            variable->value = "disabled";
        else if (compatibility && !strcmp(variable->key, "pcsx_rearmed_cd_readahead"))
            variable->value = "0";
        else
            return false;
        return true;
    }
    case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
        *(bool *)data = false;
        return true;
    case RETRO_ENVIRONMENT_GET_INPUT_BITMASKS:
        return true;
    case RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS:
    case RETRO_ENVIRONMENT_SET_CONTROLLER_INFO:
    case RETRO_ENVIRONMENT_SET_GEOMETRY:
        return true;
    default:
        return false;
    }
}

static void video(const void *frame, unsigned w, unsigned h, size_t pitch)
{
    if (!frame || w > MAX_WIDTH || h > MAX_HEIGHT)
        return;
    width = (int)w;
    height = (int)h;
    for (unsigned y = 0; y < h; y++) {
        const uint8_t *row = (const uint8_t *)frame + y * pitch;
        for (unsigned x = 0; x < w; x++) {
            uint32_t color;
            if (pixel_format == RETRO_PIXEL_FORMAT_XRGB8888) {
                memcpy(&color, row + x * 4, 4);
            } else {
                uint16_t value;
                memcpy(&value, row + x * 2, 2);
                unsigned r = value >> 11, g = (value >> 5) & 63, b = value & 31;
                color = (r << 19) | ((r >> 2) << 16) | (g << 10) |
                        ((g >> 4) << 8) | (b << 3) | (b >> 2);
            }
            pixels[y * w + x] = 0xff000000u | color;
        }
    }
}

static size_t audio_batch(const int16_t *data, size_t frames)
{
    size_t available = (sizeof(samples) / sizeof(samples[0]) - sample_count) / 2;
    size_t copied = frames < available ? frames : available;
    memcpy(samples + sample_count, data, copied * 2 * sizeof(*data));
    sample_count += copied * 2;
    return frames;
}

static void audio_sample(int16_t left, int16_t right)
{
    const int16_t data[] = {left, right};
    audio_batch(data, 1);
}

static void input_poll(void) {}

static int16_t input_state(unsigned port, unsigned device, unsigned index, unsigned id)
{
    if (port != 0 || index != 0 || device != RETRO_DEVICE_JOYPAD)
        return 0;
    if (id == RETRO_DEVICE_ID_JOYPAD_MASK)
        return (int16_t)buttons;
    return id < 16 && (buttons & (1 << id)) != 0;
}

#define JNI_METHOD(name) Java_com_logie_blizz_ps1_Ps1Core_##name

static bool copy_path(JNIEnv *env, jstring path, char *out, size_t capacity)
{
    const char *value = (*env)->GetStringUTFChars(env, path, NULL);
    if (!value)
        return false;
    int written = snprintf(out, capacity, "%s", value);
    (*env)->ReleaseStringUTFChars(env, path, value);
    return written >= 0 && (size_t)written < capacity;
}

JNIEXPORT jdouble JNICALL JNI_METHOD(open)(JNIEnv *env, jobject self, jstring path, jstring saves, jboolean safe)
{
    (void)self;
    if (attempted || !copy_path(env, path, image, sizeof(image)) ||
        !copy_path(env, saves, directory, sizeof(directory)))
        return 0;
    attempted = true;
    compatibility = safe == JNI_TRUE;
    retro_set_environment(environment);
    retro_set_video_refresh(video);
    retro_set_audio_sample(audio_sample);
    retro_set_audio_sample_batch(audio_batch);
    retro_set_input_poll(input_poll);
    retro_set_input_state(input_state);
    retro_init();
    struct retro_game_info game = {.path = image};
    loaded = retro_load_game(&game);
    if (!loaded)
        return 0;
    retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD);
    struct retro_system_av_info info;
    retro_get_system_av_info(&info);
    return info.timing.fps;
}

JNIEXPORT jint JNICALL JNI_METHOD(step)(JNIEnv *env, jobject self, jint pad, jintArray frame)
{
    (void)self;
    buttons = pad;
    sample_count = 0;
    retro_run();
    if (!width || !height)
        return 0;
    (*env)->SetIntArrayRegion(env, frame, 0, width * height, (const jint *)pixels);
    return (width << 16) | height;
}

JNIEXPORT jint JNICALL JNI_METHOD(readAudio)(JNIEnv *env, jobject self, jshortArray target)
{
    (void)self;
    (*env)->SetShortArrayRegion(env, target, 0, (jsize)sample_count, samples);
    return (jint)sample_count;
}

JNIEXPORT void JNICALL JNI_METHOD(close)(JNIEnv *env, jobject self)
{
    (void)env;
    (void)self;
    if (loaded)
        retro_unload_game();
    if (attempted)
        retro_deinit();
    loaded = attempted = false;
    width = height = buttons = 0;
}
