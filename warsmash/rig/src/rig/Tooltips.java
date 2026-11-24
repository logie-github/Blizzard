package rig;
import java.lang.reflect.*;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.parsers.w3x.objectdata.Warcraft3MapRuntimeObjectData;
/** Tooltip codes that read an upgrade's numbers (<Rhlh,mod1>) are filled in, not left "{missing}". */
public class Tooltips extends Scenario {
  public boolean frame(War3MapViewer v, int n) {
    if (n < 5) return false;
    try {
      Field f = War3MapViewer.class.getDeclaredField("allObjectData"); f.setAccessible(true); Warcraft3MapRuntimeObjectData d = (Warcraft3MapRuntimeObjectData) f.get(v);
      Method m = Class.forName("com.etheller.warsmash.viewer5.handlers.w3x.rendersim.ability.AbilityDataUI").getDeclaredMethod("parseUbertip", Warcraft3MapRuntimeObjectData.class, String.class); m.setAccessible(true);
      String out = (String) m.invoke(null, d, "Increases the amount of lumber that Peasants can carry by <Rhlh,mod1>.");
      System.err.println("RIG: tooltip -> " + out);
      check(!out.contains("missing") && out.contains("by 10"), "upgrade code filled in");
      int bad = 0, total = 0; java.util.Map<String, Integer> kinds = new java.util.TreeMap<>();
      for (var od : new com.etheller.warsmash.units.ObjectData[]{d.getUnits(), d.getItems(), d.getAbilities(), d.getUpgrades()}) {
        for (String id : od.keySet()) { var row = od.get(id); if (row == null) continue;
          for (String fld : new String[]{"Ubertip", "Researchubertip", "Unubertip", "Tip"}) for (int lv = 0; lv < 4; lv++) { String t; try { t = row.getFieldAsString(fld, lv); } catch (Throwable e) { continue; } if (t == null || t.indexOf('<') < 0) continue; total++;
            String r = (String) m.invoke(null, d, t); if (r.contains("{missing}")) { bad++; String key = r.replaceAll("(?s).*?([^ ]*,[^ ]*)\\{missing\\}.*", "$1"); kinds.merge(key.replaceAll("^[A-Za-z0-9]{4},", "?,"), 1, Integer::sum); } } } }
      System.err.println("RIG: unresolved " + bad + " of " + total + " tooltip texts with codes; by field: " + kinds);
    } catch (Throwable t) { t.printStackTrace(); failed = true; }
    return true;
  }
}
