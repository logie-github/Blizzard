package rig;
import com.etheller.warsmash.util.War3ID;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;

/** Every ability alias in $ALIASES (one per line): prints those the engine has no ability type for. */
public class TypeScan extends Scenario {
  public boolean frame(War3MapViewer v, int n) {
    if (n < 30) return false;
    CSimulation s = v.simulation; int none = 0, all = 0;
    try {
      for (String l : java.nio.file.Files.readAllLines(java.nio.file.Paths.get(System.getenv("ALIASES")))) {
        if (l.isBlank()) continue; all++;
        String a = l.trim().split("\\s+")[0];
        if (s.getAbilityData().getAbilityType(War3ID.fromString(a)) == null) { none++; System.err.println("RIG: NOTYPE " + l.trim()); }
      }
    } catch (Exception e) { throw new RuntimeException(e); }
    System.err.println("RIG: TYPESCAN " + none + " of " + all + " without a type");
    return true;
  }
}
