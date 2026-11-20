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

  final List<Case> cases = List.of(
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
  );
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
