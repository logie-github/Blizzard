package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
/** Loads the map and lets it run ($FRAMES frames, 300 by default): the map loads, its scripts start, the simulation ticks. */
public class Idle extends Scenario {
  static final int FRAMES = Integer.parseInt(System.getenv().getOrDefault("FRAMES", "300"));
  public boolean frame(War3MapViewer v, int n) { if (n % 100 == 0) System.err.println("RIG: tick " + v.simulation.getGameTurnTick() + " units " + v.simulation.getUnits().size()); return n >= FRAMES; }
}
