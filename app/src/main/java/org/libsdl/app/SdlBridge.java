// SPDX-License-Identifier: GPL-2.0-or-later

package org.libsdl.app;

/**
 * The Warcraft app's way into SDL's input, for the native games (Stratagus): its gestures become
 * SDL's mouse, keys and text, as a mouse and keyboard on the phone would give them. In SDL's
 * package, for its text call (SDLInputConnection's, not public).
 */
public final class SdlBridge {
    /** Android's MotionEvent actions and button bits, as SDL reads them (SDL_androidmouse.c). */
    public static final int ACTION_DOWN = 0;
    public static final int ACTION_UP = 1;
    public static final int ACTION_MOVE = 2;
    public static final int ACTION_HOVER_MOVE = 7;
    public static final int ACTION_SCROLL = 8;
    public static final int BUTTON_PRIMARY = 1;
    public static final int BUTTON_SECONDARY = 2;

    private SdlBridge() {}

    /** [buttons]: the buttons held after this event (the pressed one on DOWN, none on UP). */
    public static void mouse(int buttons, int action, float x, float y) {
        SDLActivity.onNativeMouse(buttons, action, x, y, false);
    }

    public static void keyDown(int keycode) {
        SDLActivity.onNativeKeyDown(keycode);
    }

    public static void keyUp(int keycode) {
        SDLActivity.onNativeKeyUp(keycode);
    }

    /** Text typed into the game (its chat, a save's name). */
    public static void text(String text) {
        SDLInputConnection.nativeCommitText(text, 1);
    }
}
