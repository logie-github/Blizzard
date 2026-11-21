package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.save.SavedObjectGraph;
import java.util.*;
/** Feasibility spike: serialise the live simulation (whatever lies outside the simulation package is dropped) and report size, time and the dropped references. */
public class SaveSpike extends Scenario {
  static final int AT = Integer.parseInt(System.getenv().getOrDefault("SAVEAT", "600"));
  public boolean frame(War3MapViewer v, int n) {
    if (n != AT) return false;
    final Map<String, Integer> dropped = new TreeMap<>(); final Map<String, Integer> droppedClasses = new TreeMap<>();
    SavedObjectGraph.Rules rules = new SavedObjectGraph.Rules() {
      public String externalName(Object o) { return null; }
      public boolean isInPlace(Object o) { return false; }
      public boolean isDropped(Object o) { String c = o.getClass().getName(); boolean keep = c.startsWith("java.") || c.startsWith("[") || c.startsWith("com.etheller.warsmash.viewer5.handlers.w3x.simulation.") || c.startsWith("com.etheller.warsmash.util.War3ID") || c.startsWith("com.badlogic.gdx.math.") || c.startsWith("com.badlogic.gdx.utils.") && !c.contains("Pixmap"); if (!keep) droppedClasses.merge(c, 1, Integer::sum); return !keep; }
      public Object replace(Object o) { return o; }
      public Object resolveExternal(String name) { return null; }
      public void reportDropped(Class<?> holder, String field, Object o) { dropped.merge(holder.getSimpleName() + "." + field + " -> " + o.getClass().getSimpleName(), 1, Integer::sum); }
    };
    try {
      long t0 = System.nanoTime(); var bytes = new SavedObjectGraph.Bytes(1 << 20); var out = new SavedObjectGraph.BytesData(bytes);
      var w = new SavedObjectGraph.Writer(rules, out); w.writeRoot(v.simulation); var table = w.finishTableBytes();
      long t1 = System.nanoTime();
      System.err.println("RIG: SAVESPIKE tick " + v.simulation.getGameTurnTick() + " objects " + w.objectCount() + " body " + bytes.size() + " bytes, table " + table.size() + " bytes, " + (t1 - t0) / 1000000 + " ms; dropped reference kinds " + dropped.size() + ", dropped classes " + droppedClasses.size());
      droppedClasses.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(25).forEach(e -> System.err.println("RIG: SAVESPIKE dropped class " + e.getKey() + " x" + e.getValue()));
    } catch (Throwable t) { System.err.println("RIG: SAVESPIKE failed " + t); t.printStackTrace(); }
    return true;
  }
}
