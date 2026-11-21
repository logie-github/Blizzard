package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;

/** Every native common.j declares that the engine registered without code (a call does nothing): one RIG: NOCODE line each. */
public class NativeAudit extends Scenario {
  public boolean frame(War3MapViewer v, int n) {
    if (n < 10) return false;
    var g = v.simulation.getGlobalScope(); int none = 0, all = 0;
    try {
      java.lang.reflect.Field impl = com.etheller.interpreter.ast.function.NativeJassFunction.class.getDeclaredField("implementation"); impl.setAccessible(true);
      for (String name : java.nio.file.Files.readAllLines(java.nio.file.Paths.get(System.getenv("NATIVES")))) {
        name = name.trim(); if (name.isEmpty()) continue;
        Integer id = g.getNativeId(name); if (id == null) continue; all++;
        if (impl.get(g.getNativeById(id)) == null) { none++; System.err.println("RIG: NOCODE " + name); }
      }
    } catch (Exception e) { throw new RuntimeException(e); }
    System.err.println("RIG: NATIVEAUDIT " + none + " of " + all + " without code");
    return true;
  }
}
