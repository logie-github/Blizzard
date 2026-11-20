package rig;
import java.util.*; import java.nio.file.*;
import com.etheller.warsmash.util.War3ID;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.generic.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.skills.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.targeting.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.abilities.types.CAbilityType;

/** Each ability (code alias kind) given to a fresh caster beside an enemy, an ally and a flyer; cast; what changed is printed. */
public class AbilitySmoke extends Scenario {
  List<String[]> todo = new ArrayList<>(); int idx = -1, phaseStart; CUnit caster, enemy, ally, flyer, enemy2; War3ID type0; CAbility ab;
  float e2Mana0, eLife0, aLife0, fLife0, cMana0, e2Life0; int eBuff0, aBuff0, cBuff0, fBuff0; String kind; boolean accepted; List<String> excs = new ArrayList<>();
  float bx, by; int gold0, lumber0; String why = ""; int results = 0, effected = 0; int fx = 0; boolean listening; int castAt = 6; int p0alive0, ill0, corpses0; float allyX0, allyY0;
  public AbilitySmoke() throws Exception { Path list = Path.of(System.getenv("ABLIST")); if (!list.isAbsolute()) list = Path.of("..").resolve(list); /* run/ is the working folder */ for (String l : Files.readAllLines(list)) if (!l.isBlank()) todo.add(l.trim().split("\\s+")); }
  static int buffs(CUnit u) { int n = 0; for (CAbility a : u.getAbilities()) if (a instanceof CBuff) n++; return n; }
  static String buffNames(CUnit u) { StringBuilder b = new StringBuilder(); for (CAbility a : u.getAbilities()) if (a instanceof CBuff) b.append(a.getAlias()).append(','); return b.toString(); }
  public void exception(Throwable t) { excs.add(t.toString()); }
  void clear(CSimulation s) { for (CUnit u : new CUnit[]{caster, enemy, ally, flyer, enemy2}) if (u != null) s.removeUnit(u); caster = enemy = ally = flyer = enemy2 = null; }
  public boolean frame(War3MapViewer v, int n) {
    CSimulation s = v.simulation;
    if (n < 30) return false;
    if (idx == -1) { for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == 0 && u.isBuilding()) { bx = u.getX() + 600; by = u.getY(); break; } idx = 0; phaseStart = n; start(s); return false; }
    int t = n - phaseStart;
    if (t == castAt && kind != null) cast(s);
    if (t >= 260) { report(s); clear(s); idx++; if (idx >= todo.size()) { System.err.println("RIG: SUMMARY " + effected + "/" + results + " showed an effect"); return true; } phaseStart = n; start(s); }
    return false;
  }
  void start(CSimulation s) {
    if (!listening) { listening = true; s.addSpellEffectListener((sim, c, a) -> { if (c == caster) fx++; }); }
    fx = 0;
    String[] e = todo.get(idx); excs.clear(); kind = null;
    War3ID alias = War3ID.fromString(e[1]);
    CAbilityType<?> type = s.getAbilityData().getAbilityType(alias);
    if (type == null) { System.err.println("RIG: RESULT " + e[0] + " " + e[1] + " NOTYPE"); return; }
    caster = s.createUnitSimple(War3ID.fromString(e.length > 3 ? e[3] : "Hblm"), 0, bx, by, 0);
    enemy = s.createUnitSimple(War3ID.fromString("hfoo"), 1, bx + 250, by, 180);
    enemy2 = s.createUnitSimple(War3ID.fromString("hsor"), 1, bx + 300, by + 80, 180);
    ally = s.createUnitSimple(War3ID.fromString("hfoo"), 0, bx - 150, by, 0);
    flyer = s.createUnitSimple(War3ID.fromString("hgry"), 1, bx + 200, by - 150, 180);
    ally.setLife(s, ally.getLife() * 0.5f); caster.setLife(s, caster.getLife() * 0.6f);
    for (CUnit u : new CUnit[]{caster, enemy, ally, flyer, enemy2}) { u.addStateModBuff(new com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuff(com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK, 1)); u.computeUnitState(s, com.etheller.warsmash.viewer5.handlers.w3x.simulation.unit.StateModBuffType.DISABLE_ATTACK); }
    gold0 = s.getPlayer(0).getGold(); lumber0 = s.getPlayer(0).getLumber();
    ab = type.createAbility(s.getHandleIdAllocator().createId());
    caster.add(s, ab);
    caster.setMana(caster.getMaximumMana() > 0 ? caster.getMaximumMana() : 0);
    kind = e[2];
    castAt = 6;
    if (kind.startsWith("corpse")) {
      // corpses to work with: the two enemy soldiers die first, the cast waits for their bodies
      enemy.kill(s); enemy2.kill(s); castAt = 200; kind = kind.substring("corpse".length()); if (kind.isEmpty()) kind = "none";
    }
    if (kind.equals("summoned")) { enemy.addClassification(com.etheller.warsmash.viewer5.handlers.w3x.simulation.CUnitClassification.SUMMONED); kind = "enemy"; }
    if (kind.equals("hero")) {
      // a hero with a skill learned (Tome of Retraining): Siphon Mana
      caster.getHeroData().selectHeroSkill(s, caster, War3ID.fromString("AHdr"));
      System.err.println("RIG: hero skill points before " + caster.getHeroData().getSkillPoints());
      kind = "none";
    }
  }
  static int alive(CSimulation s, int p) { int n = 0; for (CUnit u : s.getUnits()) if (u.getPlayerIndex() == p && !u.isDead() && !u.isHidden()) n++; return n; }
  static int illusions(CSimulation s) { int n = 0; for (CUnit u : s.getUnits()) if (u.isIllusion() && !u.isDead()) n++; return n; }
  static int corpses(CSimulation s) { int n = 0; for (CUnit u : s.getUnits()) if (u.isDead() && u.isCorpse() && !u.isHidden()) n++; return n; }
  void cast(CSimulation s) {
    if (caster.getMaximumMana() < 500) { caster.setMaximumMana(1000); }
    caster.setMana(1000);
    p0alive0 = alive(s, 0); ill0 = illusions(s); corpses0 = corpses(s); allyX0 = ally.getX(); type0 = caster.getTypeId(); allyY0 = ally.getY();
    eLife0 = enemy.getLife(); aLife0 = ally.getLife(); fLife0 = flyer.getLife(); e2Life0 = enemy2.getLife(); cMana0 = caster.getMana(); e2Mana0 = enemy2.getMana();
    eBuff0 = buffs(enemy); aBuff0 = buffs(ally); cBuff0 = buffs(caster); fBuff0 = buffs(flyer);
    int order = (ab instanceof AbstractGenericSingleIconActiveAbility a) ? a.getBaseOrderId() : 0;
    // research the ability asks for is given to the caster's player (the rig tests the ability, not the tech tree)
    for (int tries = 0; tries < 4 && order != 0; tries++) {
      final java.util.List<Object[]> missing = new java.util.ArrayList<>();
      Object r = java.lang.reflect.Proxy.newProxyInstance(getClass().getClassLoader(), new Class<?>[]{com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver.class}, (p, m, a) -> { if (m.getName().equals("missingRequirement")) missing.add(a); return null; });
      ab.checkCanUse(s, caster, order, (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver) r);
      if (missing.isEmpty()) break;
      for (Object[] a : missing) s.getPlayer(0).setTechResearched(s, (War3ID) a[0], Math.max(1, (Integer) a[1]));
      caster.checkDisabledAbilities(s, false);
    }
    AbilityTarget target = switch (kind) { case "enemy" -> enemy; case "caster" -> enemyCaster(); case "ally" -> ally; case "air" -> flyer; case "point" -> new AbilityPointTarget(enemy.getX(), enemy.getY()); case "self" -> caster; default -> null; };
    accepted = order != 0 && caster.order(s, order, "passive".equals(kind) ? null : target);
    if (!accepted && order != 0) {
      StringBuilder w = new StringBuilder();
      Object rec = java.lang.reflect.Proxy.newProxyInstance(getClass().getClassLoader(), new Class<?>[]{com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver.class}, (p, m, a) -> { if (!m.getName().equals("useOk")) w.append(m.getName()).append(a == null ? "" : java.util.Arrays.toString(a)).append(' '); return null; });
      ab.checkCanUse(s, caster, order, (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityActivationReceiver) rec);
      Object trec = java.lang.reflect.Proxy.newProxyInstance(getClass().getClassLoader(), new Class<?>[]{com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityTargetCheckReceiver.class}, (p, m, a) -> { if (!m.getName().startsWith("target")) {} if (m.getName().equals("targetCheckFailed")) w.append("target:").append(a[0]).append(' '); return null; });
      if (target instanceof CWidget wd) ab.checkCanTarget(s, caster, order, wd, (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityTargetCheckReceiver) trec);
      else if (target instanceof AbilityPointTarget pt) ab.checkCanTarget(s, caster, order, pt, (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityTargetCheckReceiver) trec);
      else ab.checkCanTargetNoTarget(s, caster, order, (com.etheller.warsmash.viewer5.handlers.w3x.simulation.util.AbilityTargetCheckReceiver) trec);
      why = w.toString().trim();
    } else why = "";
  }
  CUnit enemyCaster() { return enemy2; }
  void report(CSimulation s) {
    String[] e = todo.get(idx);
    if (caster != null && caster.getHeroData() != null) System.err.println("RIG: hero skill points after " + caster.getHeroData().getSkillPoints());
    if (kind == null) return;
    String d = String.format("acc=%s mana=%.0f enemy=%.0f/%+d enemy2=%.0f ally=%.0f/%+d air=%.0f/%+d self=%+d gold=%+d lumber=%+d e2mana=%.0f fx=%d p0=%+d ill=%+d corpses=%+d eOwner=%d allyMoved=%.0f type=%s",
      accepted, caster.getMana() - cMana0, enemy.getLife() - eLife0, buffs(enemy) - eBuff0, enemy2.getLife() - e2Life0, ally.getLife() - aLife0, buffs(ally) - aBuff0, flyer.getLife() - fLife0, buffs(flyer) - fBuff0, buffs(caster) - cBuff0, s.getPlayer(0).getGold() - gold0, s.getPlayer(0).getLumber() - lumber0, enemy2.getMana() - e2Mana0, fx, alive(s, 0) - p0alive0, illusions(s) - ill0, corpses(s) - corpses0, enemy.getPlayerIndex(), (float) Math.hypot(ally.getX() - allyX0, ally.getY() - allyY0), caster.getTypeId().equals(type0) ? "same" : type0 + ">" + caster.getTypeId());
    boolean eff = !caster.getTypeId().equals(type0) || caster.getMana() < cMana0 - 0.5f || Math.abs(enemy.getLife() - eLife0) > 0.5f || Math.abs(ally.getLife() - aLife0) > 0.5f || Math.abs(flyer.getLife()-fLife0) > 0.5f || buffs(enemy) != eBuff0 || buffs(ally) != aBuff0 || buffs(caster) != cBuff0 || buffs(flyer) != fBuff0 || enemy.isDead() || "passive".equals(kind) || alive(s, 0) != p0alive0 || illusions(s) != ill0 || corpses(s) != corpses0 || enemy.getPlayerIndex() != 1 || Math.hypot(ally.getX() - allyX0, ally.getY() - allyY0) > 50 || s.getPlayer(0).getGold() != gold0 || s.getPlayer(0).getLumber() != lumber0;
    results++; if (eff && excs.isEmpty()) effected++;
    System.err.println("RIG: RESULT " + e[0] + " " + e[1] + " " + kind + " " + ab.getClass().getSimpleName() + " " + d + " buffs[e=" + buffNames(enemy) + " a=" + buffNames(ally) + " c=" + buffNames(caster) + " f=" + buffNames(flyer) + "]" + (why.isEmpty() ? "" : " WHY " + why) + (excs.isEmpty() ? "" : " EXC " + excs));
  }
}
