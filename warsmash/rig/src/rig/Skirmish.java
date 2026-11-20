package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;

/**
 * A melee game with computer players (COMPUTERS=1 or 1,2,...): every 300 frames prints each player's units and
 * buildings, gold and lumber and whether an AI script runs for it; $FRAMES long (6000 by default).
 */
public class Skirmish extends Scenario {
  int[] lost = new int[4]; java.util.Set<CUnit> seen = new java.util.HashSet<>();
  static final int FRAMES = Integer.parseInt(System.getenv().getOrDefault("FRAMES", "6000"));
  public boolean frame(War3MapViewer v, int n) {
    CSimulation s = v.simulation;
    for (CUnit u : s.getUnits()) { if (u.isDead() && seen.add(u) && u.getPlayerIndex() < 4) lost[u.getPlayerIndex()]++; }
    if (n % 300 == 0) {
      StringBuilder b = new StringBuilder("RIG: skirmish frame " + n);
      for (int p = 0; p < 4; p++) {
        int units = 0, buildings = 0, workers = 0;
        for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == p && !u.isDead()) { if (u.isBuilding()) buildings++; else units++; if (u.getUnitType().getClassifications().contains(CUnitClassification.PEON)) workers++; }
        var pl = s.getPlayer(p);
        CUnit hall = null; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == p && u.isBuilding() && !u.isDead() && u.getUnitType().getClassifications().contains(CUnitClassification.TOWNHALL)) { hall = u; break; }
        int blighted = 0; if (hall != null) for (int dx = -640; dx <= 640; dx += 64) for (int dy = -640; dy <= 640; dy += 64) if ((s.getPathingGrid().getPathing(hall.getX() + dx, hall.getY() + dy) & com.etheller.warsmash.viewer5.handlers.w3x.environment.PathingGrid.PathingFlags.BLIGHTED) != 0) blighted++;
        b.append(String.format(" | p%d %s %s ai=%s units=%d (workers %d) buildings=%d gold=%d lumber=%d food=%d blight=%d lost=%d", p, pl.getController(), hall == null ? "-" : hall.getTypeId(), pl.getAiScript() != null, units, workers, buildings, pl.getGold(), pl.getLumber(), pl.getFoodUsed(), blighted, lost[p]));
      }
      System.err.println(b);
      if (System.getenv("UNITS") != null && n % 1500 == 0) { StringBuilder c = new StringBuilder("RIG: units:"); for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == Integer.parseInt(System.getenv("UNITS")) && !u.isBuilding() && !u.isDead()) c.append(' ').append(u.getTypeId()).append('/').append(u.getCurrentBehavior() == null ? "-" : u.getCurrentBehavior().getClass().getSimpleName()); System.err.println(c); }
      if (System.getenv("UNITS") != null && n % 1500 == 0) { for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == Integer.parseInt(System.getenv("UNITS")) && !u.isDead()) { var h = u.getFirstAbilityOfType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.harvest.CAbilityHarvest.class); if (h != null) { var t = h.getLastHarvestTarget(); System.err.println("RIG: harvester " + u.getTypeId() + " at " + (int) u.getX() + "," + (int) u.getY() + " carries " + h.getCarriedResourceAmount() + " " + h.getCarriedResourceType() + " last " + (t == null ? "-" : t.getClass().getSimpleName() + "@" + (int) t.getX() + "," + (int) t.getY() + " life " + (int) t.getLife()) + " beh " + (u.getCurrentBehavior() == null ? "-" : u.getCurrentBehavior().getClass().getSimpleName()) + (u.getCurrentBehavior() instanceof com.etheller.warsmash.viewer5.handlers.w3x.simulation.behaviors.CBehaviorAttack ab ? " target " + ab.getTarget().getClass().getSimpleName() + "@" + (int) ab.getTarget().getX() + "," + (int) ab.getTarget().getY() + (ab.getTarget() instanceof CWidget w ? " life " + w.getLife() + " dead " + w.isDead() : "") + " treeAttack " + (ab == h.getBehaviorTreeAttack()) : "")); } } }
      if (n % 1500 == 0) { StringBuilder c = new StringBuilder("RIG: buildings:"); for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == Integer.parseInt(System.getenv().getOrDefault("BPLAYER", "0")) && u.isBuilding() && !u.isDead()) c.append(' ').append(u.getTypeId()).append(u.isConstructing() ? "(building " + (int) (u.getLife() * 100 / u.getMaximumLife()) + "%)" : ""); System.err.println(c); }
    }
    return n >= FRAMES;
  }
}
