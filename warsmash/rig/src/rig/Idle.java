package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.CUnit;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
/** Loads the map and lets it run ($FRAMES frames, 300 by default): the map loads, its scripts start, the simulation ticks. */
public class Idle extends Scenario {
  static final int FRAMES = Integer.parseInt(System.getenv().getOrDefault("FRAMES", "300"));
  boolean wasShown;
  public boolean frame(War3MapViewer v, int n) {
    if (n % 100 == 0) System.err.println("RIG: tick " + v.simulation.getGameTurnTick() + " units " + v.simulation.getUnits().size());
    com.etheller.warsmash.viewer5.handlers.w3x.ui.CineFilter f = null; try { var fld = com.etheller.warsmash.WarsmashGdxMapScreen.class.getDeclaredField("minimapUI"); fld.setAccessible(true); var ui = (com.etheller.warsmash.viewer5.handlers.w3x.ui.MeleeUI) fld.get(Main.mapScreen); f = ui == null ? null : ui.getCineFilter(); } catch (Exception e) { }
    if (n == 50) System.err.println("RIG: cine filter object " + f);
    boolean shown = f != null && f.isDisplayed();
    if (shown != wasShown) { System.err.println("RIG: cine filter " + (shown ? "shown" : "hidden") + " at tick " + v.simulation.getGameTurnTick()); wasShown = shown; }
    if (n == FRAMES - 30 || n == FRAMES) { try { var fld = com.etheller.warsmash.WarsmashGdxMapScreen.class.getDeclaredField("minimapUI"); fld.setAccessible(true); var ui = (com.etheller.warsmash.viewer5.handlers.w3x.ui.MeleeUI) fld.get(Main.mapScreen); var d = ui.getQuestDialog(); if (n == FRAMES - 30) { d.setVisible(true); } else { var root = (com.etheller.warsmash.parsers.fdf.GameUI) v.getGameUI(); var t = (com.etheller.warsmash.parsers.fdf.frames.StringFrame) root.getFrameByName("QuestDetailsTitle", 0); System.err.println("RIG: quest dialog visible=" + d.isVisible() + " details title=" + (t == null ? "-" : t.getText())); } } catch (Throwable e) { System.err.println("RIG: quest dialog EXC " + e); e.printStackTrace(); } }
    if (System.getenv("DRAIN") != null && n == FRAMES / 2) { v.simulation.getPlayer(3).setGold(100); System.err.println("RIG: drained player 3 gold to 100"); }
    if (System.getenv("DRAIN") != null && n == FRAMES / 2 + 5) System.err.println("RIG: player 3 gold 5 frames later " + v.simulation.getPlayer(3).getGold());
    if (n == FRAMES - 20) { try { var fld = com.etheller.warsmash.WarsmashGdxMapScreen.class.getDeclaredField("minimapUI"); fld.setAccessible(true); var ui = (com.etheller.warsmash.viewer5.handlers.w3x.ui.MeleeUI) fld.get(Main.mapScreen); var m = com.etheller.warsmash.viewer5.handlers.w3x.ui.MeleeUI.class.getDeclaredMethod("approachQuestVillager", CUnit.class); m.setAccessible(true); int marked = 0; String r = ""; for (CUnit u : new java.util.ArrayList<>(v.simulation.getUnits())) if (v.hasQuestDialogueMarker(u)) { marked++; if (r.isEmpty()) { boolean ok = (Boolean) m.invoke(ui, u); r = " tapping " + u.getUnitType().getName() + ": hero sent=" + ok; } } System.err.println("RIG: quest villagers marked=" + marked + r); } catch (Throwable e) { System.err.println("RIG: villager check " + e); } }
    if (n == FRAMES) { StringBuilder pg = new StringBuilder("RIG: player gold/lumber"); for (int i = 0; i < 12; i++) pg.append(' ').append(i).append('=').append(v.simulation.getPlayer(i).getGold()).append('/').append(v.simulation.getPlayer(i).getLumber()); System.err.println(pg); }
    if (n == FRAMES) { for (var q : v.simulation.getQuestLog().getQuests()) { StringBuilder b = new StringBuilder("RIG: quest " + q.getTitle() + " required=" + q.isRequired() + " discovered=" + q.isDiscovered() + " completed=" + q.isCompleted() + " items:"); for (var i : q.getItems()) b.append(" [").append(i.getDescription()).append(i.isCompleted() ? " done" : "").append(']'); System.err.println(b); } }
    return n >= FRAMES;
  }
}
