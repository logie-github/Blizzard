package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
public abstract class Scenario { public boolean failed; public abstract boolean frame(War3MapViewer v, int n);
  public void exception(Throwable t) {}
  protected void check(boolean ok, String what) { System.err.println((ok ? "PASS: " : "FAIL: ") + what); if (!ok) failed = true; } }
