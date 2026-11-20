package rig;
import java.util.*;
import java.util.function.*;
import com.etheller.warsmash.util.War3ID;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.CAbility;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.generic.AbstractGenericSingleIconActiveAbility;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.targeting.AbilityPointTarget;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds;

/**
 * Abilities that need more than a caster and a target: a tree, a building to hit, workers to call, an upgrade, a
 * neutral unit to wander. Each case sets its scene up, waits its frames, and prints what it measured.
 */
public class Setups extends Scenario {
  abstract static class Later extends com.etheller.warsmash.viewer5.handlers.w3x.simulation.timers.CTimer { void go(CSimulation s, float t) { setTimeoutTime(t); start(s); } }
  interface Case { String name(); int frames(); Supplier<String> start(CSimulation s, float x, float y); }
  static Case c(String name, int frames, BiFunction<CSimulation, float[], Supplier<String>> f) {
    return new Case() { public String name() { return name; } public int frames() { return frames; } public Supplier<String> start(CSimulation s, float x, float y) { return f.apply(s, new float[]{x, y}); } };
  }
  final List<CUnit> made = new ArrayList<>();
  CUnit unit(CSimulation s, String type, int player, float x, float y) { CUnit u = s.createUnitSimple(War3ID.fromString(type), player, x, y, 0); made.add(u); return u; }
  CAbility give(CSimulation s, CUnit u, String alias) { CAbility a = s.getAbilityData().getAbilityType(War3ID.fromString(alias)).createAbility(s.getHandleIdAllocator().createId()); u.add(s, a); return a; }
  static int order(CAbility a) { return a instanceof AbstractGenericSingleIconActiveAbility g ? g.getBaseOrderId() : 0; }
  static int count(CSimulation s, int p) { int n = 0; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == p && !u.isDead()) n++; return n; }
  static CDestructable tree(CSimulation s, float x, float y) {
    CDestructable best = null; double d = 1e9;
    for (CDestructable t : s.getDestructables()) { double e = Math.hypot(t.getX() - x, t.getY() - y); if (!t.isDead() && e < d && t.getDestType().getTargetedAs().contains(com.etheller.warsmash.viewer5.handlers.w3x.simulation.combat.CTargetType.TREE)) { best = t; d = e; } }
    return best;
  }

  final List<Case> cases = filter(List.of(
    c("Player 1's own peons ordered to 4128,2720", 900, (s, p) -> {
      java.util.List<CUnit> ps = new java.util.ArrayList<>(); for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 1 && !u.isBuilding() && !u.isDead()) ps.add(u);
      StringBuilder start = new StringBuilder(); for (CUnit u : ps) start.append((int) u.getX()).append(',').append((int) u.getY()).append(' ').append(u.isHidden() ? "hidden " : "");
      for (CUnit u : ps) u.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(4128, 2720));
      return () -> { StringBuilder b = new StringBuilder(); for (CUnit u : ps) b.append((int) Math.hypot(u.getX() - 4128, u.getY() - 2720)).append(' '); return "peons " + ps.size() + " started at " + start + "; left to go " + b; };
    }),
    c("Footmen ordered 300, 800 and 1500 away", 900, (s, p) -> {
      CUnit[] fs = { unit(s, "hfoo", 0, p[0], p[1]), unit(s, "hfoo", 0, p[0], p[1] + 100), unit(s, "hfoo", 0, p[0], p[1] + 200) };
      float[] d = { 300, 800, 1500 };
      for (int i = 0; i < 3; i++) fs[i].order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(p[0] + d[i], p[1] + i * 100));
      return () -> { StringBuilder b = new StringBuilder(); for (int i = 0; i < 3; i++) b.append((int) (d[i]) + "->left " + (int) Math.hypot(fs[i].getX() - p[0] - d[i], fs[i].getY() - p[1] - i * 100) + "; "); return b.toString(); };
    }),
    c("Orc peon of player 1 told to move to 4128,2720", 900, (s, p) -> {
      CUnit peon = unit(s, "opeo", 1, 4700, 3100);
      final float x0 = peon.getX(), y0 = peon.getY();
      boolean ok = peon.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(4128, 2720));
      return () -> "accepted=" + ok + " from " + (int) x0 + "," + (int) y0 + " now at " + (int) peon.getX() + "," + (int) peon.getY() + " pathable there " + s.getPathingGrid().isPathable(4128, 2720, com.etheller.warsmash.viewer5.handlers.w3x.environment.PathingGrid.MovementType.FOOT, 16);
    }),
    c("Flood fill on foot from player 1's peons to 4128,2720", 30, (s, p) -> {
      var g = s.getPathingGrid(); CUnit peon = null; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 1 && !u.isBuilding()) { peon = u; break; }
      final float sx = peon.getX(), sy = peon.getY();
      java.util.ArrayDeque<int[]> q = new java.util.ArrayDeque<>(); java.util.Set<Long> seenCells = new java.util.HashSet<>();
      int cx = Math.round(sx / 32), cy = Math.round(sy / 32); q.add(new int[]{cx, cy}); seenCells.add(((long) cx << 32) ^ (cy & 0xffffffffL));
      boolean reached = false; int n = 0; int tx = Math.round(4128f / 32), ty = Math.round(2720f / 32);
      while (!q.isEmpty() && n < 400000) { int[] c = q.poll(); n++; if (Math.abs(c[0] - tx) <= 1 && Math.abs(c[1] - ty) <= 1) { reached = true; break; }
        for (int[] d : new int[][]{{1,0},{-1,0},{0,1},{0,-1}}) { int nx = c[0] + d[0], ny = c[1] + d[1]; long k = ((long) nx << 32) ^ (ny & 0xffffffffL);
          if (seenCells.contains(k)) continue; seenCells.add(k);
          if (g.isPathable(nx * 32f, ny * 32f, com.etheller.warsmash.viewer5.handlers.w3x.environment.PathingGrid.MovementType.FOOT, Float.parseFloat(System.getenv().getOrDefault("FILLR", "8")))) q.add(new int[]{nx, ny}); } }
      final boolean r = reached; final int cells = n; final float peon_c = peon.getUnitType().getCollisionSize();
      return () -> "reachable=" + r + " cells searched " + cells + " from " + (int) sx + "," + (int) sy + " peon collision " + peon_c + " start pathable " + g.isPathable(sx, sy, com.etheller.warsmash.viewer5.handlers.w3x.environment.PathingGrid.MovementType.FOOT, peon_c);
    }),
    c("Footman ordered behind a U-shaped wall (opening away from it)", 1200, (s, p) -> {
      for (int i = -4; i <= 4; i++) unit(s, "hhou", 0, p[0] + 300, p[1] + i * 128);
      for (int i = 1; i <= 3; i++) { unit(s, "hhou", 0, p[0] + 300 - i * 128, p[1] + 4 * 128); unit(s, "hhou", 0, p[0] + 300 - i * 128, p[1] - 4 * 128); }
      CUnit f = unit(s, "hfoo", 0, p[0], p[1]);
      final float tx = p[0] + 700, ty = p[1];
      boolean ok = f.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(tx, ty));
      return () -> "accepted=" + ok + " left to go " + (int) Math.hypot(f.getX() - tx, f.getY() - ty) + " at " + (int) (f.getX() - p[0]) + "," + (int) (f.getY() - p[1]) + " relative";
    }),
    c("Footman told to attack a grunt behind a wall of farms", 1200, (s, p) -> {
      for (int i = -4; i <= 4; i++) unit(s, "hhou", 0, p[0] + 300, p[1] + i * 128);
      CUnit f = unit(s, "hfoo", 0, p[0], p[1]);
      CUnit g = unit(s, "ogru", 1, p[0] + 600, p[1]);
      g.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK, 1)); g.computeUnitState(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK);
      g.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_MOVE, 1)); g.computeUnitState(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_MOVE);
      float l0 = g.getLife();
      boolean ok = f.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.attack, g);
      return () -> "accepted=" + ok + " grunt lost " + (int) (l0 - g.getLife()) + " footman at " + (int) (f.getX() - p[0]) + "," + (int) (f.getY() - p[1]) + " relative";
    }),
    c("Footman ordered behind a wall of farms", 900, (s, p) -> {
      for (int i = -3; i <= 3; i++) unit(s, "hhou", 0, p[0] + 300, p[1] + i * 128);
      CUnit f = unit(s, "hfoo", 0, p[0], p[1]);
      final float tx = p[0] + 600, ty = p[1];
      boolean ok = f.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(tx, ty));
      return () -> "accepted=" + ok + " left to go " + (int) Math.hypot(f.getX() - tx, f.getY() - ty) + " at " + (int) f.getX() + "," + (int) f.getY() + " (wall at x=" + (int) (p[0] + 300) + ")";
    }),
    c("Footman ordered to a point behind trees (the nearest tree's far side)", 900, (s, p) -> {
      CDestructable t = tree(s, p[0], p[1]);
      CUnit f = unit(s, "hfoo", 0, p[0], p[1]);
      double ang = Math.atan2(t.getY() - p[1], t.getX() - p[0]);
      final float tx = (float) (t.getX() + Math.cos(ang) * 400), ty = (float) (t.getY() + Math.sin(ang) * 400);
      final boolean pathable = s.getPathingGrid().isPathable(tx, ty, com.etheller.warsmash.viewer5.handlers.w3x.environment.PathingGrid.MovementType.FOOT, 16);
      boolean ok = f.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(tx, ty));
      return () -> "target pathable=" + pathable + " accepted=" + ok + " left to go " + (int) Math.hypot(f.getX() - tx, f.getY() - ty) + " from start " + (int) Math.hypot(p[0] - tx, p[1] - ty);
    }),
    c("Orc peon of player 1 told to build an altar at 4128,2720", 900, (s, p) -> {
      CUnit peon = null; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 1 && u.getTypeId().toString().equals("opeo")) { peon = u; break; }
      if (peon == null) { peon = unit(s, "opeo", 1, 4400, 2900); }
      final CUnit pe = peon; s.getPlayer(1).setGold(1000); s.getPlayer(1).setLumber(1000);
      boolean ok = pe.order(s, War3ID.fromString("oalt").getValue(), new AbilityPointTarget(4128, 2720));
      final int g0 = s.getPlayer(1).getGold();
      return () -> { CUnit alt = null; for (CUnit u : s.getUnits()) if (u.getTypeId().toString().equals("oalt")) alt = u;
        return "accepted=" + ok + " gold " + g0 + "->" + s.getPlayer(1).getGold() + " altar " + (alt == null ? "none" : "at " + (int) alt.getX() + "," + (int) alt.getY()) + " peon at " + (int) pe.getX() + "," + (int) pe.getY() + " " + pe.getCurrentBehavior(); };
    }),
    c("Thunder Clap (AHtc): the ground ripples and settles", 300, (s, p) -> {
      CUnit m = unit(s, "Hmkg", 0, p[0], p[1]); CAbility a = give(s, m, "AHtc"); m.setMana(500);
      float[] pr = new float[42]; pr[0] = p[0]; pr[1] = p[1];
      for (int k = 0; k < 8; k++) { double an = k * Math.PI / 4; for (float r = 64; r <= 320; r += 64) pr[2 + k * 5 + (int) (r / 64) - 1] = viewer.terrain.getGroundHeight((float) (p[0] + Math.cos(an) * r), (float) (p[1] + Math.sin(an) * r)); }
      maxDev = 0; probe = pr;
      boolean ok = m.order(s, order(a), null);
      return () -> { float dev = maxDev; float settled = 0; for (int k = 0; k < 8; k++) { double an = k * Math.PI / 4; for (float r = 64; r <= 320; r += 64) settled = Math.max(settled, Math.abs(viewer.terrain.getGroundHeight((float) (p[0] + Math.cos(an) * r), (float) (p[1] + Math.sin(an) * r)) - pr[2 + k * 5 + (int) (r / 64) - 1])); }
        probe = null; return "accepted=" + ok + " largest ground change during it " + dev + ", left after it " + settled; };
    }),
    c("Death and Decay (AUdd) on a computer player's footmen: they walk out", 600, (s, p) -> {
      com.etheller.warsmash.viewer5.handlers.w3x.simulation.players.CMapControl was = s.getPlayer(1).getController();
      s.getPlayer(1).setController(com.etheller.warsmash.viewer5.handlers.w3x.simulation.players.CMapControl.COMPUTER);
      CUnit l = unit(s, "Ulic", 0, p[0], p[1]); CAbility a = give(s, l, "AUdd"); l.setMana(1000);
      CUnit[] fs = { unit(s, "hfoo", 1, p[0] + 500, p[1]), unit(s, "hfoo", 1, p[0] + 520, p[1] + 60) };
      for (CUnit f : fs) { f.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK, 1)); f.computeUnitState(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK); }
      final float cx = p[0] + 510, cy = p[1] + 30;
      boolean ok = l.order(s, order(a), new AbilityPointTarget(cx, cy));
      return () -> { s.getPlayer(1).setController(was); StringBuilder b = new StringBuilder(); for (CUnit f : fs) b.append((int) Math.hypot(f.getX() - cx, f.getY() - cy)).append(' ');
        return "accepted=" + ok + " footmen now this far from the centre: " + b + "(the area is 250 wide)"; };
    }),
    c("Blizzard (AHbz) on a computer player's footmen: they walk out", 600, (s, p) -> {
      com.etheller.warsmash.viewer5.handlers.w3x.simulation.players.CMapControl was = s.getPlayer(1).getController();
      s.getPlayer(1).setController(com.etheller.warsmash.viewer5.handlers.w3x.simulation.players.CMapControl.COMPUTER);
      CUnit l = unit(s, "Hjai", 0, p[0], p[1]); CAbility a = give(s, l, "AHbz"); l.setMana(1000);
      CUnit[] fs = { unit(s, "hfoo", 1, p[0] + 500, p[1]), unit(s, "hfoo", 1, p[0] + 520, p[1] + 60) };
      for (CUnit f : fs) { f.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK, 1)); f.computeUnitState(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK); }
      final float cx = p[0] + 510, cy = p[1] + 30;
      boolean ok = l.order(s, order(a), new AbilityPointTarget(cx, cy));
      return () -> { s.getPlayer(1).setController(was); StringBuilder b = new StringBuilder(); for (CUnit f : fs) b.append((int) Math.hypot(f.getX() - cx, f.getY() - cy)).append(' ');
        return "accepted=" + ok + " footmen now this far from the centre: " + b; };
    }),
    c("Breath of Frost (ACbf): Blue Dragon on three footmen", 300, (s, p) -> {
      CUnit d = unit(s, "nbdo", 0, p[0], p[1]); CAbility a = null; for (CAbility x : d.getAbilities()) if (x.getAlias().toString().equals("ACbf")) a = x; if (a == null) a = give(s, d, "ACbf"); d.setMana(500);
      CUnit[] fs = { unit(s, "hfoo", 1, p[0] + 300, p[1]), unit(s, "hfoo", 1, p[0] + 350, p[1] + 40), unit(s, "hfoo", 1, p[0] + 330, p[1] - 40) };
      for (CUnit f : fs) { f.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK, 1)); f.computeUnitState(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK); }
      d.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK, 1)); d.computeUnitState(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK);
      float l0 = 0; for (CUnit f : fs) l0 += f.getLife(); final float life0 = l0; final java.util.Set<String> seen = new java.util.TreeSet<>();
      boolean ok = d.order(s, order(a), new AbilityPointTarget(p[0] + 320, p[1]));
      return () -> { float l = 0; for (CUnit f : fs) { l += Math.max(0, f.getLife()); seen.add(AbilitySmoke.buffNames(f)); } return "accepted=" + ok + " footmen lost " + (int) (life0 - l) + " (50 each, then 7 a second for 5 s) buffs " + seen; };
    }),
    c("Tornado (ANto): Sea Witch's tornado among five footmen", 150, (s, p) -> {
      CUnit w = unit(s, "Nngs", 0, p[0], p[1]); CAbility a = give(s, w, "ANto"); w.setMana(1000);
      CUnit[] fs = new CUnit[5]; for (int i = 0; i < 5; i++) fs[i] = unit(s, "hfoo", 1, p[0] + 300 + i * 30, p[1] + (i - 2) * 40);
      CUnit farm = unit(s, "hhou", 1, p[0] + 450, p[1] + 200); final float farm0 = farm.getLife(); final int[] caught = {0};
      s.getPlayer(0); final java.util.Set<CUnit> spun = new java.util.HashSet<>();
      float l0 = 0; for (CUnit f : fs) l0 += f.getLife(); final float life0 = l0;
      boolean ok = w.order(s, order(a), new AbilityPointTarget(p[0] + 350, p[1]));
      final int[] stunned = {0};
      return () -> { float l = 0; CUnit t = null; for (CUnit u : s.getUnits()) if (u.getTypeId().toString().equals("ntor") && !u.isDead()) t = u; for (CUnit f : fs) l += Math.max(0, f.getLife());
        return "accepted=" + ok + " tornado " + (t == null ? "none" : "at " + (int) Math.hypot(t.getX() - p[0] - 350, t.getY() - p[1]) + " from its point") + " footmen lost " + (int) (life0 - l) + " footmen spun now " + java.util.Arrays.stream(fs).filter(f -> AbilitySmoke.buffNames(f).contains("Btsp")).count() + " farm lost " + (int) (farm0 - farm.getLife()); };
    }),
    c("Healing Spray (ANhs) on three wounded footmen", 400, (s, p) -> {
      CUnit h = unit(s, "Nalc", 0, p[0], p[1]); CAbility a = give(s, h, "ANhs"); h.setMana(500);
      CUnit[] fs = { unit(s, "hfoo", 0, p[0] + 400, p[1]), unit(s, "hfoo", 0, p[0] + 430, p[1] + 50), unit(s, "hfoo", 0, p[0] + 380, p[1] - 50) };
      float l0 = 0; for (CUnit f : fs) { f.setLife(s, 100); l0 += 100; } final float life0 = l0;
      boolean ok = h.order(s, order(a), new AbilityPointTarget(p[0] + 400, p[1]));
      return () -> { float l = 0; for (CUnit f : fs) l += f.getLife(); return "accepted=" + ok + " footmen healed " + (int) (l - life0) + " (3 waves of 40, at most 280 a wave)"; };
    }),
    c("Lava Spawn (ANlm) splits after its attacks", 1500, (s, p) -> {
      CUnit h = unit(s, "Nfir", 0, p[0], p[1]); CAbility a = give(s, h, "ANlm"); h.setMana(500);
      CUnit g = unit(s, "hgtw", 1, p[0] + 350, p[1]); g.setMaximumLife(20000); g.setLife(s, 20000);
      boolean ok = h.order(s, order(a), null);
      return () -> { int n = 0; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && !u.isDead() && u.getTypeId().toString().startsWith("nlv")) n++; return "accepted=" + ok + " lava spawns alive " + n + " tower life " + (int) g.getLife(); };
    }),
    c("Engineering Upgrade (ANeg) on a Tinker with Pocket Factory", 30, (s, p) -> {
      CUnit t = unit(s, "Ntin", 0, p[0], p[1]); give(s, t, "ANsy"); int sp0 = t.getSpeed(); int d0 = t.getUnitSpecificAttacks().get(0).getDamageBase();
      give(s, t, "ANeg");
      return () -> { StringBuilder b = new StringBuilder(); for (CAbility x : t.getAbilities()) if (x.getAlias().toString().startsWith("ANs")) b.append(x.getAlias()).append(' ');
        return "speed " + sp0 + "->" + t.getSpeed() + " damage " + d0 + "->" + t.getUnitSpecificAttacks().get(0).getDamageBase() + " factory ability " + b; };
    }),
    c("Demolish (ANde): footman with it hits a farm, beside one without", 600, (s, p) -> {
      CUnit a1 = unit(s, "hfoo", 0, p[0], p[1]); give(s, a1, "ANde"); CUnit f1 = unit(s, "hhou", 1, p[0] + 200, p[1]);
      CUnit a2 = unit(s, "hfoo", 0, p[0], p[1] - 450); CUnit f2 = unit(s, "hhou", 1, p[0] + 200, p[1] - 450);
      float l1 = f1.getLife(), l2 = f2.getLife(); a1.order(s, OrderIds.attack, f1); a2.order(s, OrderIds.attack, f2);
      return () -> "farm hit with Demolish lost " + (int) (l1 - f1.getLife()) + ", without " + (int) (l2 - f2.getLife());
    }),
    c("Tiny Farm (AIbf) on open ground", 900, (s, p) -> {
      CUnit h = unit(s, "Hblm", 0, p[0], p[1]); CAbility a = give(s, h, "AIbf"); int n0 = count(s, 0);
      boolean ok = h.order(s, order(a), new AbilityPointTarget(p[0] + 300, p[1] + 300));
      return () -> { CUnit built = null; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && u.isBuilding() && Math.hypot(u.getX() - p[0] - 300, u.getY() - p[1] - 300) < 150) built = u;
        return "accepted=" + ok + " units " + n0 + "->" + count(s, 0) + " built=" + (built == null ? "none" : built.getTypeId() + " constructing=" + built.isConstructing() + " life=" + (int) built.getLife() + "/" + (int) built.getMaximumLife()); };
    }),
    c("Spell Book (Aspb) adds its spells", 30, (s, p) -> {
      CUnit h = unit(s, "Hblm", 0, p[0], p[1]); int n0 = h.getAbilities().size(); give(s, h, "Aspb");
      return () -> { StringBuilder b = new StringBuilder(); for (CAbility a : h.getAbilities()) if (a.getContainerMenuOrderId() != 0) b.append(a.getAlias()).append(' ');
        return "abilities " + n0 + "->" + h.getAbilities().size() + " in the book: " + b; };
    }),
    c("Wander (Awan) on a neutral-passive critter", 1200, (s, p) -> {
      CUnit u = unit(s, "nfro", com.etheller.warsmash.util.WarsmashConstants.MAX_PLAYERS - 1, p[0], p[1]); give(s, u, "Awan"); float x0 = u.getX(), y0 = u.getY();
      return () -> "owner=" + u.getPlayerIndex() + " moved " + (int) Math.hypot(u.getX() - x0, u.getY() - y0) + " wanderer=" + u.isWanderer();
    }),
    c("Pillage (Asal): grunt hits an enemy farm", 900, (s, p) -> {
      s.getPlayer(0).setTechResearched(s, War3ID.fromString("Ropg"), 1);
      CUnit g = unit(s, "ogru", 0, p[0], p[1]); give(s, g, "Asal"); g.checkDisabledAbilities(s, false);
      CUnit f = unit(s, "hhou", 1, p[0] + 250, p[1]); int g0 = s.getPlayer(0).getGold(), l0 = s.getPlayer(0).getLumber();
      g.order(s, OrderIds.attack, f);
      return () -> "gold +" + (s.getPlayer(0).getGold() - g0) + " lumber +" + (s.getPlayer(0).getLumber() - l0) + " farm life " + (int) f.getLife();
    }),
    c("Spiked Barricades (Aspi, Rosp 1): footman hits a burrow", 600, (s, p) -> {
      s.getPlayer(0).setTechResearched(s, War3ID.fromString("Rosp"), 1);
      CUnit b = unit(s, "otrb", 0, p[0], p[1]); CUnit f = unit(s, "hfoo", 1, p[0] + 160, p[1]); float l0 = f.getLife();
      boolean[] hb = {false}; for (CAbility a : b.getAbilities()) if (a.getAlias().toString().equals("Aspi")) hb[0] = true; if (!hb[0]) give(s, b, "Aspi"); final boolean has = hb[0];
      f.order(s, OrderIds.attack, b);
      return () -> "burrow had Aspi=" + has + " returned per unit " + b.getSpikedBarricadesDamage() + " footman life " + (int) l0 + "->" + (int) f.getLife() + " burrow life " + (int) b.getLife() + "/" + (int) b.getMaximumLife() + " footman behavior " + f.getCurrentBehavior();
    }),
    c("Spiked Barricades baseline (no upgrade): footman hits a burrow", 600, (s, p) -> {
      s.getPlayer(2).setTechResearched(s, War3ID.fromString("Rosp"), 0);
      CUnit b = unit(s, "otrb", 2, p[0], p[1]); CUnit f = unit(s, "hfoo", 1, p[0] + 160, p[1]); float l0 = f.getLife();
      f.order(s, OrderIds.attack, b);
      return () -> "footman life " + (int) l0 + "->" + (int) f.getLife();
    }),
    c("Battle Stations (Abtl): burrow calls two peons", 600, (s, p) -> {
      CUnit b = unit(s, "otrb", 0, p[0], p[1]); unit(s, "opeo", 0, p[0] + 300, p[1]); unit(s, "opeo", 0, p[0] + 300, p[1] + 100);
      CAbility a = null; for (CAbility x : b.getAbilities()) if (x.getAlias().toString().equals("Abtl")) a = x; if (a == null) a = give(s, b, "Abtl");
      boolean ok = b.order(s, order(a), null);
      return () -> { int cargo = -1; for (CAbility x : b.getAbilities()) if (x instanceof com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.cargohold.CAbilityCargoHold h) cargo = h.getCargoCount(); StringBuilder w = new StringBuilder(); for (CUnit u : made) if (u.getTypeId().toString().equals("opeo")) w.append(u.getCurrentBehavior()).append(" at ").append((int) u.distance(b)).append(" hidden=").append(u.isHidden()).append("; "); return "accepted=" + ok + " peons in the burrow " + cargo + " peons: " + w; };
    }),
    c("Sentinel (Aesn): huntress sends an owl to a tree", 300, (s, p) -> {
      CUnit h = unit(s, "esen", 0, p[0], p[1]); CAbility a = give(s, h, "Aesn"); h.checkDisabledAbilities(s, false);
      s.getPlayer(0).setTechResearched(s, War3ID.fromString("Resc"), 1); h.checkDisabledAbilities(s, false);
      CDestructable t = tree(s, p[0], p[1]); int n0 = count(s, 0);
      boolean ok = t != null && h.order(s, order(a), t);
      return () -> "tree " + (t == null ? "none" : (int) Math.hypot(t.getX() - p[0], t.getY() - p[1]) + " away") + " accepted=" + ok + " owls on the tree " + (t == null ? 0 : t.getBuffs().size()) + " units " + n0 + "->" + count(s, 0) + " huntress behavior " + h.getCurrentBehavior() + " mana " + (int) h.getMana() + " owls " + s.getUnits().stream().filter(u -> !made.contains(u) && u.getPlayerIndex() == 0 && !u.isBuilding()).map(u -> u.getTypeId() + "@" + (int) u.distance(h)).toList();
    }),
    c("Mountain giant walks to a tree (move order to its point)", 400, (s, p) -> {
      CUnit m = unit(s, "emtg", 0, p[0], p[1]); CDestructable t = tree(s, p[0], p[1]);
      m.order(s, OrderIds.move, new AbilityPointTarget(t.getX(), t.getY()));
      return () -> "giant from 229 to " + (int) Math.hypot(t.getX() - m.getX(), t.getY() - m.getY());
    }),
    c("Peasant harvests that tree", 400, (s, p) -> {
      CUnit m = unit(s, "hpea", 0, p[0], p[1]); CDestructable t = tree(s, p[0], p[1]);
      boolean ok = m.order(s, OrderIds.harvest, t);
      return () -> "accepted=" + ok + " peasant to " + (int) Math.hypot(t.getX() - m.getX(), t.getY() - m.getY()) + " " + m.getCurrentBehavior();
    }),
    c("Blizzard (AHbz) after a walk: archmage 1100 from three footmen", 900, (s, p) -> {
      CUnit h = unit(s, "Hjai", 0, p[0] - 600, p[1]); CAbility a = give(s, h, "AHbz"); h.setMana(500);
      CUnit[] fs = { unit(s, "hfoo", 1, p[0] + 500, p[1]), unit(s, "hfoo", 1, p[0] + 520, p[1] + 60), unit(s, "hfoo", 1, p[0] + 480, p[1] - 60) };
      float l0 = 0; for (CUnit f : fs) l0 += f.getLife(); final float life0 = l0;
      boolean ok = h.order(s, order(a), new AbilityPointTarget(p[0] + 500, p[1]));
      return () -> { float l = 0; for (CUnit f : fs) l += Math.max(0, f.getLife()); return "accepted=" + ok + " footmen lost " + (int) (life0 - l) + " archmage walked " + (int) (h.getX() - (p[0] - 600)); };
    }),
    c("Goblin Land Mine (Amin): a footman walks over it at once, another after it arms", 900, (s, p) -> {
      CUnit mine = unit(s, "nglm", 0, p[0], p[1]);
      CUnit early = unit(s, "hfoo", 1, p[0] - 500, p[1] + 200), late = unit(s, "hfoo", 1, p[0] - 500, p[1] - 200);
      early.order(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(p[0] + 500, p[1]));
      final float[] seen = { 0, -1 };
      new Later() { public void onFire(CSimulation sim) { seen[0] = mine.getInvisLevels() != 0 ? 1 : 0; seen[1] = mine.isDead() ? 1 : 0; late.order(sim, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.move, new AbilityPointTarget(p[0] + 500, p[1])); } }.go(s, 12f);
      return () -> "after 12 s: mine invisible=" + (seen[0] == 1) + " dead=" + (seen[1] == 1) + "; end: mine dead=" + mine.isDead() + " early footman life " + (int) early.getLife() + " late footman life " + (int) late.getLife() + " of " + (int) late.getMaxLife();
    }),
    c("Creep sleep: two trolls at night, one hit", 600, (s, p) -> {
      int na = s.getPlayers().size() - 4; s.setGameTimeOfDay(0f);
      CUnit a = unit(s, "nftr", na, p[0], p[1] - 1500), b = unit(s, "nftr", na, p[0] + 100, p[1] - 1500), hitter = unit(s, "hfoo", 0, p[0] - 2500, p[1]);
      final String[] mid = { "" };
      new Later() { public void onFire(CSimulation sim) { mid[0] = "night=" + sim.isNight() + " asleep " + a.isUnitType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.CUnitTypeJass.SLEEPING) + "," + b.isUnitType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.CUnitTypeJass.SLEEPING);
        a.damage(sim, hitter, new com.etheller.warsmash.viewer5.handlers.w3x.simulation.combat.CSpellDamageFlags(), com.etheller.warsmash.viewer5.handlers.w3x.simulation.combat.CAttackType.SPELLS, com.etheller.warsmash.viewer5.handlers.w3x.simulation.trigger.enumtypes.CDamageType.NORMAL, "WHOKNOWS", 10f); } }.go(s, 8f);
      final String[] after = { "" };
      new Later() { public void onFire(CSimulation sim) { after[0] = "asleep " + a.isUnitType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.CUnitTypeJass.SLEEPING) + "," + b.isUnitType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.CUnitTypeJass.SLEEPING); } }.go(s, 9f);
      return () -> "after 8 s: " + mid[0] + "; 1 s after the hit: " + after[0] + "; at the end: asleep " + a.isUnitType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.CUnitTypeJass.SLEEPING) + "," + b.isUnitType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.CUnitTypeJass.SLEEPING);
    }),
    c("Tavern (Sellunits): a peasant beside it buys a Brewmaster before and after its stock starts", 6000, (s, p) -> {
      int np = s.getPlayers().size() - 1;
      CUnit tav = unit(s, "ntav", np, p[0], p[1] + 300); CUnit peasant = unit(s, "hpea", 0, p[0], p[1]); final String preAltar = "TALT before altar " + s.getPlayer(0).getTechtreeUnlocked(War3ID.fromString("TALT")); CUnit altar = unit(s, "halt", 0, p[0] - 600, p[1] - 400); s.getPlayer(0).addTechtreeUnlocked(s, War3ID.fromString("halt"));
      var sell = tav.getFirstAbilityOfType(com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.item.shop.CAbilitySellUnits.class);
      final String[] early = { "" };
      final int idx = sell == null ? -1 : sell.getUnitsSold().indexOf(War3ID.fromString("Npbm"));
      final int[] heroes = { 0, 0 }; final int[] gold = { 0, 0 };
      s.getPlayer(0).setGold(2000); s.getPlayer(0).setLumber(2000);
      new Later() { public void onFire(CSimulation sim) { int g = sim.getPlayer(0).getGold(); boolean ok = tav.order(sim, com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.item.shop.CAbilitySellUnits.orderId(0, idx), null); var st = sell.getStockState(War3ID.fromString("Npbm")); var ty = sim.getUnitData().getUnitType(War3ID.fromString("Npbm")); early[0] = "type stock " + ty.getStockMax() + "/" + ty.getStockStartDelay() + "/" + ty.getStockReplenishInterval() + " state " + (st == null ? "-" : st.getMaxStock() + " next " + st.getNextStockReplenishGameTurnTick()) + " tick " + sim.getGameTurnTick() + " disabled " + sell.isDisabled() + " constructing " + tav.isConstructing() + " paused " + tav.isPaused() + " beh " + tav.getCurrentBehavior() + " at 10 s: stock " + sell.getStock(War3ID.fromString("Npbm")) + " order " + ok + " gold spent " + (g - sim.getPlayer(0).getGold()); } }.go(s, 10f);
      new Later() { public void onFire(CSimulation sim) { StringBuilder why = new StringBuilder(); Object rec = java.lang.reflect.Proxy.newProxyInstance(Setups.class.getClassLoader(), new Class<?>[]{com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver.class}, (pr, mm, aa) -> { why.append(mm.getName()).append(java.util.Arrays.toString(aa)); return null; }); sell.checkCanUse(sim, tav, com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.item.shop.CAbilitySellUnits.orderId(0, idx), (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver) rec); System.err.println("RIG: tavern check " + why + " patron " + (tav.getNeutralBuildingData() == null ? "no data" : tav.getNeutralBuildingData().getSelectedPlayerUnit(0)));
        gold[0] = sim.getPlayer(0).getGold(); heroes[0] = sim.getPlayer(0).getHeroCount(sim, false); tav.order(sim, com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.item.shop.CAbilitySellUnits.orderId(0, idx), null); heroes[1] = sim.getPlayer(0).getHeroCount(sim, false); gold[1] = sim.getPlayer(0).getGold(); } }.go(s, 150f);
      final String[] awake = { "" };
      new Later() { public void onFire(CSimulation sim) { for (CUnit u : sim.getUnits()) if (u.getPlayerIndex() == 0 && u.getTypeId().toString().equals("Npbm")) u.kill(sim); } }.go(s, 160f);
      new Later() { public void onFire(CSimulation sim) { CUnit hero = null; for (CUnit u : sim.getPlayerHeroes(0)) if (u.getTypeId().toString().equals("Npbm")) hero = u; if (hero == null) { awake[0] = "no hero"; return; } int g = sim.getPlayer(0).getGold(); boolean before = hero.isDead(); boolean ok = tav.order(sim, hero.getHandleId(), null); awake[0] = "awaken: dead before " + before + " order " + ok + " alive after " + !hero.isDead() + " life " + (int) hero.getLife() + "/" + (int) hero.getMaximumLife() + " gold spent " + (g - sim.getPlayer(0).getGold()) + " distance from tavern " + (int) Math.hypot(hero.getX() - tav.getX(), hero.getY() - tav.getY()); } }.go(s, 180f);
      return () -> { int bm = 0; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && u.getTypeId().toString().equals("Npbm") && !u.isDead()) { bm++; made.add(u); }
        return preAltar + ", after " + s.getPlayer(0).getTechtreeUnlocked(War3ID.fromString("TALT")) + "; end tick " + s.getGameTurnTick() + " sells " + (sell == null ? "nothing" : sell.getUnitsSold()) + "; " + early[0] + "; at 150 s: heroes " + heroes[0] + "->" + heroes[1] + " gold spent " + (gold[0] - gold[1]) + " stock now " + (sell == null ? -1 : sell.getStock(War3ID.fromString("Npbm"))) + " brewmasters " + bm + "; " + awake[0]; };
    }),
    c("Natives (0026): alliances, orders, visibility called through the map's script", 400, (s, p) -> {
      var g = s.getGlobalScope(); var pt = g.getHandleType("player"); var ut = g.getHandleType("unit");
      java.util.function.BiFunction<String, java.util.List<com.etheller.interpreter.ast.value.JassValue>, Object> call = (name, args) -> { Integer id = g.getNativeId(name); if (id == null) return "NONE"; var r = g.getNativeById(id).call(args, g, new com.etheller.warsmash.parsers.jass.scope.CommonTriggerExecutionScope((com.etheller.interpreter.ast.scope.trigger.Trigger) null)); return r == null ? "null" : r.toString(); };
      var p0 = new com.etheller.interpreter.ast.value.HandleJassValue(pt, s.getPlayer(0)); var p1 = new com.etheller.interpreter.ast.value.HandleJassValue(pt, s.getPlayer(1));
      CUnit f = unit(s, "hfoo", 0, p[0], p[1]); var fu = new com.etheller.interpreter.ast.value.HandleJassValue(ut, f);
      StringBuilder b = new StringBuilder();
      b.append("ally(0,0)=").append(call.apply("IsPlayerAlly", java.util.List.of(p0, p0))).append(" enemy(0,1)=").append(call.apply("IsPlayerEnemy", java.util.List.of(p0, p1)));
      b.append(" owned=").append(call.apply("IsUnitOwnedByPlayer", java.util.List.of(fu, p0))).append(" visible to 0=").append(call.apply("IsUnitVisible", java.util.List.of(fu, p0)));
      b.append(" heroId Hpal=").append(call.apply("IsHeroUnitId", java.util.List.of(com.etheller.interpreter.ast.value.IntegerJassValue.of(War3ID.fromString("Hpal").getValue()))));
      b.append(" level=").append(call.apply("GetUnitLevel", java.util.List.of(fu)));
      b.append(" order=").append(call.apply("IssuePointOrder", java.util.List.of(fu, new com.etheller.interpreter.ast.value.StringJassValue("move"), com.etheller.interpreter.ast.value.RealJassValue.of(p[0] + 400), com.etheller.interpreter.ast.value.RealJassValue.of(p[1]))));
      var trig = new com.etheller.interpreter.ast.scope.trigger.Trigger(); final String[] dmg = { "never fired" };
      trig.addAction((args, gs, scope) -> { dmg[0] = "fired: GetEventDamage=" + call2(g, "GetEventDamage", java.util.List.of(), scope) + " source=" + call2(g, "GetEventDamageSource", java.util.List.of(), scope) + " triggering=" + call2(g, "GetTriggerUnit", java.util.List.of(), scope); return null; });
      f.addEvent(g, trig, com.etheller.warsmash.viewer5.handlers.w3x.simulation.trigger.JassGameEventsWar3.EVENT_UNIT_DAMAGED);
      CUnit hitter = unit(s, "hfoo", 1, p[0] + 2000, p[1] + 2000);
      f.damage(s, hitter, false, false, com.etheller.warsmash.viewer5.handlers.w3x.simulation.combat.CAttackType.SPELLS, com.etheller.warsmash.viewer5.handlers.w3x.simulation.trigger.enumtypes.CDamageType.NORMAL, "WHOKNOWS", 50f);
      b.append(" damage event ").append(dmg[0]).append(" (footman ").append(f.getHandleId()).append(", hitter ").append(hitter.getHandleId()).append(")");
      call.apply("SetCineFilterStartColor", java.util.List.of(com.etheller.interpreter.ast.value.IntegerJassValue.of(0), com.etheller.interpreter.ast.value.IntegerJassValue.of(0), com.etheller.interpreter.ast.value.IntegerJassValue.of(0), com.etheller.interpreter.ast.value.IntegerJassValue.of(255)));
      call.apply("DisplayCineFilter", java.util.List.of(com.etheller.interpreter.ast.value.BooleanJassValue.TRUE));
      b.append(" cine filter shown=").append(call.apply("IsCineFilterDisplayed", java.util.List.of()));
      call.apply("DisplayCineFilter", java.util.List.of(com.etheller.interpreter.ast.value.BooleanJassValue.FALSE));
      b.append(" hidden=").append(call.apply("IsCineFilterDisplayed", java.util.List.of()));
      var timer = call3(g, "CreateTimer", java.util.List.of(), null); call.apply("TimerStart", java.util.Arrays.asList((com.etheller.interpreter.ast.value.JassValue) timer, com.etheller.interpreter.ast.value.RealJassValue.of(90), com.etheller.interpreter.ast.value.BooleanJassValue.FALSE, null));
      var dlg = call3(g, "CreateTimerDialog", java.util.List.of((com.etheller.interpreter.ast.value.JassValue) timer), null);
      b.append(" timer dialog shown at creation=").append(call.apply("IsTimerDialogDisplayed", java.util.List.of((com.etheller.interpreter.ast.value.JassValue) dlg)));
      call.apply("TimerDialogSetTitle", java.util.List.of((com.etheller.interpreter.ast.value.JassValue) dlg, new com.etheller.interpreter.ast.value.StringJassValue("Reinforcements in")));
      call.apply("TimerDialogDisplay", java.util.List.of((com.etheller.interpreter.ast.value.JassValue) dlg, com.etheller.interpreter.ast.value.BooleanJassValue.TRUE));
      b.append(" after display=").append(call.apply("IsTimerDialogDisplayed", java.util.List.of((com.etheller.interpreter.ast.value.JassValue) dlg)));
      CUnit cd = unit(s, "hfoo", 0, p[0] - 300, p[1]); var fcd = new com.etheller.interpreter.ast.value.HandleJassValue(ut, cd);
      cd.beginCooldown(s, War3ID.fromString("AHtb"), 10f);
      b.append(" cooldown before reset=").append(cd.getCooldownRemainingTicks(s, War3ID.fromString("AHtb")));
      call.apply("UnitResetCooldown", java.util.List.of(fcd));
      b.append(" after=").append(cd.getCooldownRemainingTicks(s, War3ID.fromString("AHtb")));
      cd.add(s, new com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.skills.util.CBuffTimedLife(s.getHandleIdAllocator().createId(), War3ID.fromString("BTLF"), 60f, false));
      java.util.function.Supplier<Integer> nb = () -> { int k = 0; for (var a : cd.getAbilities()) if (a instanceof com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.generic.CBuff) k++; return k; };
      b.append(" buffs with timed life=").append(nb.get());
      call.apply("UnitRemoveBuffs", java.util.List.of(fcd, com.etheller.interpreter.ast.value.BooleanJassValue.TRUE, com.etheller.interpreter.ast.value.BooleanJassValue.TRUE));
      b.append(" after UnitRemoveBuffs=").append(nb.get());
      var T = com.etheller.interpreter.ast.value.BooleanJassValue.TRUE;
      call.apply("UnitRemoveBuffsEx", java.util.List.of(fcd, T, T, T, T, T, T, T));
      b.append(" after UnitRemoveBuffsEx(timed life too)=").append(nb.get());
      final String before = b.toString(); final float x0 = f.getX();
      return () -> { var root = (com.etheller.warsmash.parsers.fdf.GameUI) viewer.getGameUI(); var tv = (com.etheller.warsmash.parsers.fdf.frames.StringFrame) root.getFrameByName("TimerDialogValue", 0); var tt = (com.etheller.warsmash.parsers.fdf.frames.StringFrame) root.getFrameByName("TimerDialogTitle", 0); return before + " footman moved " + (int) (f.getX() - x0) + "; timer dialog reads \"" + (tt == null ? "-" : tt.getText()) + " " + (tv == null ? "-" : tv.getText()) + "\""; };
    }),
    c("Siege minimum range: catapults on a footman beside them and one far off", 700, (s, p) -> {
      CUnit c1 = unit(s, "ocat", 0, p[0], p[1]), c2 = unit(s, "ocat", 0, p[0] - 3000, p[1] - 1500);
      CUnit near = unit(s, "hfoo", 1, p[0] + 60, p[1]), far = unit(s, "hfoo", 1, p[0] - 2300, p[1] - 1500);
      for (CUnit f : new CUnit[]{near, far}) f.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK, 1));
      final float n0 = near.getLife(), f0 = far.getLife(); final float x0 = c1.getX(), y0 = c1.getY(); final boolean[] o = new boolean[2];
      new Later() { public void onFire(CSimulation sim) { o[0] = c1.order(sim, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.attack, near); o[1] = c2.order(sim, com.etheller.warsmash.viewer5.handlers.w3x.simulation.orders.OrderIds.attack, far); } }.go(s, 1f);
      return () -> "min range " + c1.getUnitType().getMinimumAttackRange() + "; orders " + o[0] + "," + o[1] + "; near footman lost " + (int) (n0 - near.getLife()) + " (catapult moved " + (int) Math.hypot(c1.getX() - x0, c1.getY() - y0) + ", now " + (int) c1.distance(near) + " away, " + c1.getCurrentBehavior().getClass().getSimpleName() + "), far footman lost " + (int) (f0 - far.getLife());
    }),
    c("War Club (Agra): mountain giant takes a tree", 400, (s, p) -> {
      CUnit m = unit(s, "emtg", 0, p[0], p[1]); CAbility a = null; for (CAbility x : m.getAbilities()) if (x.getAlias().toString().equals("Agra")) a = x; if (a == null) a = give(s, m, "Agra");
      CDestructable t = tree(s, p[0], p[1]);
      if (t != null && System.getenv("NEAR") != null) { m.setX(t.getX() + 90, s.getWorldCollision(), s.getRegionManager()); m.setY(t.getY(), s.getWorldCollision(), s.getRegionManager()); }
      final CAbility wc = a; StringBuilder why = new StringBuilder();
      Object rec = java.lang.reflect.Proxy.newProxyInstance(Setups.class.getClassLoader(), new Class<?>[]{com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver.class}, (pr, mm, aa) -> { if (!mm.getName().equals("useOk")) why.append(mm.getName()).append(java.util.Arrays.toString(aa)); return null; });
      a.checkCanUse(s, m, order(a), (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver) rec);
      Object trec = java.lang.reflect.Proxy.newProxyInstance(Setups.class.getClassLoader(), new Class<?>[]{com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityTargetCheckReceiver.class}, (pr, mm, aa) -> { if (!mm.getName().equals("targetOk")) why.append(" target:").append(mm.getName()).append(java.util.Arrays.toString(aa)); return null; });
      if (t != null) a.checkCanTarget(s, m, order(a), t, (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityTargetCheckReceiver) trec);
      System.err.println("RIG: warclub disabled=" + a.isDisabled() + " order=" + order(a) + " why=" + why);
      boolean ok = t != null && m.order(s, order(a), t);
      return () -> { StringBuilder b = new StringBuilder(); for (CAbility x : m.getAbilities()) if (x instanceof com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.generic.CBuff) b.append(x.getAlias()).append(' ');
        return "accepted=" + ok + " tree dead=" + (t != null && t.isDead()) + " tree at " + (t == null ? -1 : (int) Math.hypot(t.getX() - m.getX(), t.getY() - m.getY())) + " buffs " + b + " behavior " + m.getCurrentBehavior() + " giant at " + (t == null ? -1 : (int) Math.hypot(t.getX() - m.getX(), t.getY() - m.getY())) + " cd " + m.getCooldownRemainingTicks(s, War3ID.fromString("Agra")); };
    })
  ));
  static com.etheller.interpreter.ast.value.JassValue call3(com.etheller.interpreter.ast.scope.GlobalScope g, String name, java.util.List<com.etheller.interpreter.ast.value.JassValue> args, com.etheller.interpreter.ast.scope.TriggerExecutionScope scope) {
    return g.getNativeById(g.getNativeId(name)).call(args, g, scope == null ? new com.etheller.warsmash.parsers.jass.scope.CommonTriggerExecutionScope((com.etheller.interpreter.ast.scope.trigger.Trigger) null) : scope);
  }
  static Object call2(com.etheller.interpreter.ast.scope.GlobalScope g, String name, java.util.List<com.etheller.interpreter.ast.value.JassValue> args, com.etheller.interpreter.ast.scope.TriggerExecutionScope scope) {
    Integer id = g.getNativeId(name); if (id == null) return "NONE"; var r = g.getNativeById(id).call(args, g, scope);
    if (r instanceof com.etheller.interpreter.ast.value.HandleJassValue h) { Object o = h.getJavaValue(); return o instanceof CUnit u ? "unit " + u.getHandleId() : String.valueOf(o); }
    return r == null ? "null" : r.toString();
  }
  static List<Case> filter(List<Case> all) { String c = System.getenv("CASE"); if (c == null) return all; List<Case> out = new ArrayList<>(); for (Case x : all) if (x.name().contains(c)) out.add(x); return out; }
  int idx = -1, phaseStart; Supplier<String> report; float bx, by; List<String> excs = new ArrayList<>();
  public void exception(Throwable t) { excs.add(t.toString()); }
  static War3MapViewer viewer; static float maxDev; static float[] probe;
  public boolean frame(War3MapViewer v, int n) {
    viewer = v; CSimulation s = v.simulation;
    if (probe != null) { for (int k = 0; k < 8; k++) { double a = k * Math.PI / 4; for (float r = 64; r <= 320; r += 64) { float h = v.terrain.getGroundHeight((float) (probe[0] + Math.cos(a) * r), (float) (probe[1] + Math.sin(a) * r)); maxDev = Math.max(maxDev, Math.abs(h - probe[2 + k * 5 + (int) (r / 64) - 1])); } } }
    if (n < 30) return false;
    if (idx == -1) { for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && u.isBuilding()) { bx = u.getX() + 700; by = u.getY(); break; } idx = 0; begin(s, n); return false; }
    if (n - phaseStart >= cases.get(idx).frames()) {
      System.err.println("RIG: SETUP " + cases.get(idx).name() + ": " + report.get() + (excs.isEmpty() ? "" : " EXC " + excs));
      for (CUnit u : made) if (!u.isDead()) s.removeUnit(u); made.clear(); excs.clear();
      idx++; if (idx >= cases.size()) return true; begin(s, n);
    }
    return false;
  }
  void begin(CSimulation s, int n) { phaseStart = n; report = cases.get(idx).start(s, bx, by); }
}
