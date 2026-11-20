package rig;
import com.etheller.warsmash.util.War3ID;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;
public class CombatDebug extends Scenario {
  CUnit a, d; int start = -1;
  public boolean frame(War3MapViewer v, int n) {
    CSimulation s = v.simulation;
    if (n < 30) return false;
    if (start < 0) { start = n; float bx = 0, by = 0;
      for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && u.isBuilding()) { bx = u.getX(); by = u.getY(); break; }
      a = s.createUnitSimple(War3ID.fromString(System.getenv().getOrDefault("ATK", "Hpal")), 0, bx + 500, by, 0);
      d = s.createUnitSimple(War3ID.fromString("ogru"), 1, bx + 750, by, 180);
      System.err.println("RIG: attacks " + a.getCurrentAttacks() + " unitAttacks " + a.getUnitSpecificAttacks());
      a.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.attack, d); return false; }
    int t = n - start;
    if (t % 60 == 0) System.err.println("RIG: t=" + t + " beh=" + (a.getCurrentBehavior() == null ? null : a.getCurrentBehavior().getClass().getSimpleName()) + " dist=" + (int) a.distance(d) + " aLife=" + a.getLife() + " dLife=" + d.getLife() + " attacks=" + a.getCurrentAttacks().size());
    return t > 600;
  }
}
