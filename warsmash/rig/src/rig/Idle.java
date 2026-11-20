package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
public class Idle extends Scenario { public boolean frame(War3MapViewer v, int n) { if (n % 100 == 0) System.err.println("RIG: tick " + v.simulation.getGameTurnTick() + " units " + v.simulation.getUnits().size()); return n >= 300; } }
