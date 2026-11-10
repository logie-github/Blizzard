/*
 * The phone's look at a game's frame, on a real OpenGL ES (this machine's Mesa), call for call.
 *
 * On the phone Warcraft III draws through OpenGL; Winlator copies each finished frame into a texture
 * (Texture.copyFromReadBuffer: glCopyTexImage2D, GL_RGBA) in the game's own context, which shares its objects with the
 * context of the app's drawing thread (GPUHelper's globalEGLContext). The app's Wc3Watch then, on the drawing thread,
 * puts that texture on a framebuffer of its own and reads four small rectangles with glReadPixels. That cannot be run
 * on a phone from here, so this program does the same calls in the same order with two contexts of one share group:
 *
 *   game context:     a frame of the game's (a raw RGB file, top row first) is the content of its framebuffer, the right
 *                     way up as OpenGL sees it; Winlator's allocateTexture(null) and copyFromReadBuffer are made on it,
 *                     twice (a second frame after the first, as every frame does on the phone);
 *   drawing context:  Wc3Watch.fromTexture: glGenFramebuffers, glFramebufferTexture2D, glCheckFramebufferStatus,
 *                     glPixelStorei(GL_PACK_ALIGNMENT, 1), glReadPixels(GL_RGBA, GL_UNSIGNED_BYTE) of the whole
 *                     texture and of the four rectangles Wc3Screen.partial fetches, the texture taken off again.
 *
 * It fails (exit 1) if the framebuffer is not complete, on any OpenGL error, if a rectangle read by itself differs from
 * the same part of the whole, or if the second frame is not what the drawing context then reads. The whole texture as
 * read is written to <out> (red, green, blue, alpha; the texture's first row first): Wc3ScreenTest reads the game's state
 * from it as the phone would (BLIZZ_WC3_FRAMES, a <name>.rgba beside <name>.png).
 *
 *   glread <frame.rgb> <width> <height> <out.rgba>
 *
 * Built by tools/xrig/glread.sh (the EGL and OpenGL ES headers are the NDK's).
 */
#include <EGL/egl.h>
#include <GLES2/gl2.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void die(const char *what) {
    fprintf(stderr, "glread: %s (EGL 0x%x, GL 0x%x)\n", what, eglGetError(), eglGetCurrentContext() != EGL_NO_CONTEXT ? glGetError() : 0);
    exit(1);
}

static void no_error(const char *after) {
    GLenum e = glGetError();
    if (e != GL_NO_ERROR) {
        fprintf(stderr, "glread: OpenGL error 0x%x after %s\n", e, after);
        exit(1);
    }
}

/* Winlator's Texture.allocateTexture(width, height, null): a name and its parameters, no picture yet. */
static GLuint allocate_texture(void) {
    GLuint id = 0;
    glGenTextures(1, &id);
    glActiveTexture(GL_TEXTURE0);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
    glBindTexture(GL_TEXTURE_2D, id);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glBindTexture(GL_TEXTURE_2D, 0);
    return id;
}

/* Winlator's Texture.copyFromReadBuffer(width, height). */
static void copy_from_read_buffer(GLuint id, int width, int height) {
    glBindTexture(GL_TEXTURE_2D, id);
    glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 0, 0, width, height, 0);
    glBindTexture(GL_TEXTURE_2D, 0);
    glFlush();
}

/* The game's framebuffer holding [rgb] (top row first) the right way up as OpenGL sees it: its first row is the picture's bottom. */
static GLuint game_framebuffer(const unsigned char *rgb, int width, int height, int inverted) {
    unsigned char *rows = malloc((size_t)width * height * 4);
    for (int y = 0; y < height; y++) {
        const unsigned char *from = rgb + (size_t)(height - 1 - y) * width * 3;
        unsigned char *to = rows + (size_t)y * width * 4;
        for (int x = 0; x < width; x++) {
            to[x * 4 + 0] = inverted ? 255 - from[x * 3 + 0] : from[x * 3 + 0];
            to[x * 4 + 1] = inverted ? 255 - from[x * 3 + 1] : from[x * 3 + 1];
            to[x * 4 + 2] = inverted ? 255 - from[x * 3 + 2] : from[x * 3 + 2];
            to[x * 4 + 3] = 255;
        }
    }
    GLuint texture = 0, framebuffer = 0;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, rows);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glBindTexture(GL_TEXTURE_2D, 0);
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) die("the game's own framebuffer is not complete");
    free(rows);
    return framebuffer;
}

/* Wc3Watch.fromTexture and part(): the texture on the reader's framebuffer, one rectangle read. */
static void read_part(int left, int top, int width, int height, unsigned char *into) {
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadPixels(left, top, width, height, GL_RGBA, GL_UNSIGNED_BYTE, into);
    no_error("glReadPixels");
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "glread <frame.rgb> <width> <height> <out.rgba>\n");
        return 2;
    }
    int width = atoi(argv[2]), height = atoi(argv[3]);
    size_t count = (size_t)width * height;
    unsigned char *rgb = malloc(count * 3);
    FILE *in = fopen(argv[1], "rb");
    if (!in || fread(rgb, 3, count, in) != count) { fprintf(stderr, "glread: %s is not %dx%d of RGB\n", argv[1], width, height); return 2; }
    fclose(in);

    EGLDisplay display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
    if (display == EGL_NO_DISPLAY || !eglInitialize(display, NULL, NULL)) die("no EGL display");
    eglBindAPI(EGL_OPENGL_ES_API);
    const EGLint config_attributes[] = { EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,
        EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_ALPHA_SIZE, 8, EGL_NONE };
    EGLConfig config;
    EGLint configs = 0;
    if (!eglChooseConfig(display, config_attributes, &config, 1, &configs) || configs != 1) die("no EGL config");
    const EGLint context_attributes[] = { EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE };
    const EGLint surface_attributes[] = { EGL_WIDTH, 16, EGL_HEIGHT, 16, EGL_NONE };
    /* The drawing thread's context first; the game's shares with it (Winlator: eglCreateContext(..., globalEGLContext, ...)). */
    EGLContext drawing = eglCreateContext(display, config, EGL_NO_CONTEXT, context_attributes);
    EGLContext game = eglCreateContext(display, config, drawing, context_attributes);
    EGLSurface drawing_surface = eglCreatePbufferSurface(display, config, surface_attributes);
    EGLSurface game_surface = eglCreatePbufferSurface(display, config, surface_attributes);
    if (drawing == EGL_NO_CONTEXT || game == EGL_NO_CONTEXT || drawing_surface == EGL_NO_SURFACE || game_surface == EGL_NO_SURFACE) die("no contexts");

    /* The game draws a frame and Winlator copies it into the window's texture. */
    if (!eglMakeCurrent(display, game_surface, game_surface, game)) die("the game's context");
    printf("OpenGL ES: %s, %s\n", (const char *)glGetString(GL_VERSION), (const char *)glGetString(GL_RENDERER));
    GLuint first = game_framebuffer(rgb, width, height, 1);
    GLuint texture = allocate_texture();
    copy_from_read_buffer(texture, width, height);
    no_error("the first frame's copy");

    /* The app's drawing thread looks at it. */
    if (!eglMakeCurrent(display, drawing_surface, drawing_surface, drawing)) die("the drawing context");
    GLuint reader = 0;
    glGenFramebuffers(1, &reader);
    if (!reader) die("no framebuffer");
    unsigned char *whole = malloc(count * 4), *part = malloc(count * 4);
    glBindFramebuffer(GL_FRAMEBUFFER, reader);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
    if (status != GL_FRAMEBUFFER_COMPLETE) { fprintf(stderr, "glread: the shared texture's framebuffer status is 0x%x\n", status); return 1; }
    read_part(0, 0, width, height, whole);
    /* The inverted first frame: its top-left pixel (the texture's last row) is the frame's, inverted. */
    const unsigned char *corner = whole + (size_t)(height - 1) * width * 4;
    if (corner[0] != 255 - rgb[0] || corner[1] != 255 - rgb[1] || corner[2] != 255 - rgb[2]) { fprintf(stderr, "glread: the first frame is not what was read\n"); return 1; }
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, 0, 0);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    no_error("the first look");

    /* The game's next frame (the real one), copied over the same texture. */
    if (!eglMakeCurrent(display, game_surface, game_surface, game)) die("the game's context again");
    glDeleteFramebuffers(1, &first);
    game_framebuffer(rgb, width, height, 0);
    copy_from_read_buffer(texture, width, height);
    no_error("the second frame's copy");

    /* The next look: the whole, and the four rectangles Wc3Screen.partial fetches (each band as it lies either way up). */
    if (!eglMakeCurrent(display, drawing_surface, drawing_surface, drawing)) die("the drawing context again");
    glBindFramebuffer(GL_FRAMEBUFFER, reader);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
    if (status != GL_FRAMEBUFFER_COMPLETE) { fprintf(stderr, "glread: at the second look the framebuffer status is 0x%x\n", status); return 1; }
    read_part(0, 0, width, height, whole);
    for (int y = 0; y < height; y++) {
        const unsigned char *got = whole + (size_t)y * width * 4;
        const unsigned char *want = rgb + (size_t)(height - 1 - y) * width * 3;
        for (int x = 0; x < width; x++) {
            if (got[x * 4] != want[x * 3] || got[x * 4 + 1] != want[x * 3 + 1] || got[x * 4 + 2] != want[x * 3 + 2]) {
                fprintf(stderr, "glread: the second frame differs at %d,%d (texture row %d)\n", x, height - 1 - y, y);
                return 1;
            }
        }
    }
    const float bands[2][4] = { { 0.10f, 0.0f, 0.62f, 0.04f }, { 0.76f, 0.76f, 1.0f, 1.0f } };   /* Wc3Screen.TOP_BAND, CARD_BAND */
    long fetched = 0;
    for (int b = 0; b < 2; b++) {
        int left = (int)floor((double)(bands[b][0] * width)), right = (int)ceil((double)(bands[b][2] * width));
        int top = (int)floor((double)(bands[b][1] * height)), bottom = (int)ceil((double)(bands[b][3] * height));
        if (right > width) right = width;
        if (bottom > height) bottom = height;
        int tops[2] = { top, height - bottom };
        for (int k = 0; k < 2; k++) {
            int w = right - left, h = bottom - top;
            read_part(left, tops[k], w, h, part);
            for (int y = 0; y < h; y++) {
                if (memcmp(part + (size_t)y * w * 4, whole + ((size_t)(tops[k] + y) * width + left) * 4, (size_t)w * 4) != 0) {
                    fprintf(stderr, "glread: the rectangle %d,%d %dx%d read by itself differs from the whole at its row %d\n", left, tops[k], w, h, y);
                    return 1;
                }
            }
            fetched += (long)w * h;
        }
    }
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, 0, 0);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    no_error("the second look");

    FILE *out = fopen(argv[4], "wb");
    if (!out || fwrite(whole, 4, count, out) != count) { fprintf(stderr, "glread: %s can't be written\n", argv[4]); return 1; }
    fclose(out);
    printf("%s: framebuffer complete at both looks, the second frame read exactly, four rectangles (%ld of %zu pixels) as the whole\n", argv[1], fetched, count);
    return 0;
}
