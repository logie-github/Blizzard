package rig;
import java.util.*;
import com.etheller.warsmash.util.War3ID;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;

/**
 * Plain fights with the engine's attacks: pairs of attackers (melee, missile, splash, bounce, line, instant) against
 * defenders, each fight in its own place. Prints the damage taken, the deaths and how long it took.
 */
public class Combat extends Scenario {
  static final String[][] FIGHTS = {
    {"hfoo", "ogru", "melee: footman vs grunt"},
    {"hrif", "ogru", "missile: rifleman vs grunt"},
    {"hmtm", "ogru", "artillery splash: mortar team vs grunt"},
    {"earc", "ogru", "missile: archer vs grunt"},
    {"esen", "ogru", "bounce: huntress vs grunt"},
    {"ocat", "hfoo", "splash: demolisher vs footman"},
    {"hgyr", "ogru", "gyrocopter vs grunt (air vs ground)"},
    {"hmpr", "ogru", "magic: priest vs grunt"},
    {"ugar", "hfoo", "melee: gargoyle-stone? (ugar) vs footman"},
    {"Hpal", "ogru", "hero melee: paladin vs grunt"},
  };
  /** FIGHTS=abilities: the same pairs with an ability given to the attacker (autocast turned on): attacker defender label ability. */
  static final String[][] ABILITY_FIGHTS = {
    {"earc", "ogru", "frost arrows (Afak)", "Afak"},
    {"Hblm", "ogru", "cold arrows AHca", "AHca"},
    {"earc", "ogru", "black arrow ANba", "ANba"},
    {"earc", "ogru", "incinerate arrows ANia", "ANia"},
    {"earc", "ogru", "AEpa", "AEpa"},
    {"hfoo", "ogru", "orb AIcb", "AIcb"},
    {"hfoo", "ogru", "orb AIob", "AIob"},
    {"hfoo", "ogru", "orb AIzb", "AIzb"},
    {"hfoo", "ogru", "orb AIfb", "AIfb"},
    {"hfoo", "ogru", "orb AIsb", "AIsb"},
    {"hfoo", "ogru", "orb AIlb", "AIlb"},
    {"hfoo", "ogru", "orb AIpb", "AIpb"},
    {"hfoo", "ogru", "poison Apoi", "Apoi"},
    {"hfoo", "ogru", "slow poison Aspo", "Aspo"},
    {"hfoo", "ogru", "no ability (baseline)", null},
  };
  String[][] fights; List<CUnit[]> pairs = new ArrayList<>(); List<float[]> life0 = new ArrayList<>(); int start = -1; List<Throwable> excs = new ArrayList<>();
  public void exception(Throwable t) { excs.add(t); }
  public boolean frame(War3MapViewer v, int n) {
    CSimulation s = v.simulation;
    if (n < 30) return false;
    if (start < 0) {
      start = n;
      float bx = 0, by = 0;
      for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && u.isBuilding()) { bx = u.getX(); by = u.getY(); break; }
      String[][] FIGHTS = "abilities".equals(System.getenv("FIGHTS")) ? ABILITY_FIGHTS : Combat.FIGHTS; this.fights = FIGHTS;
      for (int i = 0; i < FIGHTS.length; i++) {
        float x = bx + 500 + (i % 5) * 450, y = by - 600 + (i / 5) * 700;
        CUnit a = s.createUnitSimple(War3ID.fromString(FIGHTS[i][0]), 0, x, y, 0);
        CUnit d = s.createUnitSimple(War3ID.fromString(FIGHTS[i][1]), 1, x + 250, y, 180);
        if (FIGHTS[i].length > 3 && FIGHTS[i][3] != null) {
          com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.CAbility ab = s.getAbilityData().getAbilityType(War3ID.fromString(FIGHTS[i][3])).createAbility(s.getHandleIdAllocator().createId());
          a.add(s, ab);
          try { ab.getClass().getMethod("setAutoCastOn", CUnit.class, boolean.class).invoke(ab, a, true); } catch (Exception e) { }
          if (a.getMaximumMana() < 500) a.setMaximumMana(1000); a.setMana(1000);
        }
        pairs.add(new CUnit[]{a, d}); life0.add(new float[]{a.getLife(), d.getLife()});
        a.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.attack, d);
      }
      return false;
    }
    int t = n - start;
    if (t == 900) {
      for (int i = 0; i < pairs.size(); i++) {
        CUnit a = pairs.get(i)[0], d = pairs.get(i)[1];
        System.err.println(String.format("RIG: FIGHT %-45s attacker %s life %.0f->%.0f%s | defender %s life %.0f->%.0f%s",
          fights[i][2], fights[i][0], life0.get(i)[0], a.getLife(), a.isDead() ? " DEAD" : "", fights[i][1], life0.get(i)[1], d.getLife(), d.isDead() ? " DEAD" : "") + " mana " + (int) a.getMana() + " buffs " + AbilitySmoke.buffNames(d));
      }
      for (Throwable e : excs) System.err.println("RIG: EXC " + e);
      return true;
    }
    return false;
  }
}
