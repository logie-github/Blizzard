package rig;
import com.badlogic.gdx.audio.Sound;
import com.etheller.warsmash.viewer5.*; import com.etheller.warsmash.viewer5.gl.*;
public final class Ext { public static void install() {
  Extensions.angleInstancedArrays = new ANGLEInstancedArrays() {
    public void glVertexAttribDivisorANGLE(int i, int d) {} public void glDrawElementsInstancedANGLE(int m, int c, int t, int o, int n) {} public void glDrawArraysInstancedANGLE(int m, int f, int c, int n) {} };
  Extensions.dynamicShadowExtension = new DynamicShadowExtension() { public void glFramebufferTexture(int a, int b, int c, int d) {} public void glDrawBuffer(int m) {} };
  Extensions.wireframeExtension = (a, b) -> {};
  Extensions.audio = new AudioExtension() {
    public float getDuration(Sound s) { return s == null ? 1f : 2f; }
    public long play(Sound b, float v, float p, float x, float y, float z, boolean d3, float md, float rd, boolean l) { return 0; }
    public AudioContext createContext(boolean w) { return new AudioContext(AudioContext.Listener.DO_NOTHING, new AudioDestination() {}); } };
} }
