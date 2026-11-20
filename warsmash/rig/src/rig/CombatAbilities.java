package rig;
import java.util.*;
import com.etheller.warsmash.util.War3ID;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.CAbility;

/**
 * One fight at a time, the attacker given an ability (autocast turned on): attacker defender ability. Each line is
 * compared with the same pair without the ability. Prints life, the defender's buffs seen during the fight, and mana.
 * The list is read from FIGHTLIST (lines "attacker defender ability"), defaulting to the arrow and orb abilities.
 */
public class CombatAbilities extends Scenario {
  List<String[]> todo = new ArrayList<>(); int idx = -1, phaseStart; CUnit a, d; float aLife0, dLife0, aMana0; Set<String> seen = new TreeSet<>(); List<String> excs = new ArrayList<>(); float bx, by;
  public void exception(Throwable t) { excs.add(t.toString()); }
  CombatAbilities() {
    String f = System.getenv("FIGHTLIST");
    try { if (f != null) for (String l : java.nio.file.Files.readAllLines(java.nio.file.Paths.get(f))) if (!l.isBlank() && !l.startsWith("#")) todo.add(l.trim().split("\\s+")); } catch (Exception e) { throw new RuntimeException(e); }
  }
  public boolean frame(War3MapViewer v, int n) {
    CSimulation s = v.simulation;
    if (n < 30) return false;
    if (idx == -1) { for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && u.isBuilding()) { bx = u.getX() + 700; by = u.getY(); break; } idx = 0; phaseStart = n; start(s); return false; }
    int t = n - phaseStart;
    if (d != null) for (CAbility b : d.getAbilities()) if (b instanceof com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.generic.CBuff) seen.add(b.getAlias().toString());
    if (t >= 600) { report(s); idx++; if (idx >= todo.size()) return true; phaseStart = n; start(s); }
    return false;
  }
  void start(CSimulation s) {
    String[] e = todo.get(idx); seen.clear(); excs.clear();
    a = s.createUnitSimple(War3ID.fromString(e[0]), 0, bx, by, 0);
    d = s.createUnitSimple(War3ID.fromString(e[1]), 1, bx + 250, by, 180);
    if (e.length > 2 && !e[2].equals("-")) {
      CAbility ab = s.getAbilityData().getAbilityType(War3ID.fromString(e[2])).createAbility(s.getHandleIdAllocator().createId());
      a.add(s, ab);
      try { ab.getClass().getMethod("setAutoCastOn", CUnit.class, boolean.class).invoke(ab, a, true); } catch (Exception x) { }
    }
    if (a.getMaximumMana() < 500) a.setMaximumMana(1000); a.setMana(1000);
    aLife0 = a.getLife(); dLife0 = d.getLife(); aMana0 = a.getMana();
    a.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.attack, d);
  }
  void report(CSimulation s) {
    String[] e = todo.get(idx);
    System.err.println(String.format("RIG: AFIGHT %s %s %s attacker life %.0f->%.0f%s defender life %.0f->%.0f%s mana %.0f buffs %s%s",
      e[0], e[1], e.length > 2 ? e[2] : "-", aLife0, a.getLife(), a.isDead() ? " DEAD" : "", dLife0, d.getLife(), d.isDead() ? " DEAD" : "", a.getMana() - aMana0, seen, excs.isEmpty() ? "" : " EXC " + excs));
    s.removeUnit(a); s.removeUnit(d); a = d = null;
  }
}
