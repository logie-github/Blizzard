package rig;
import com.badlogic.gdx.math.Vector2;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.environment.PathingGrid;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.*;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.behaviors.CBehaviorMove;
import com.etheller.warsmash.viewer5.handlers.w3x.simulation.pathing.CPathfindingProcessor;
import java.util.*;
/** Fixed path queries through the real pathfinder: a hash of every path found (to compare two builds) and the time they took. QUERIES=n (default 300). */
public class PathCheck extends Scenario {
  public boolean frame(War3MapViewer v, int n) {
    if (n != 400) return false;
    try {
      CSimulation sim = v.simulation; PathingGrid grid = sim.getPathingGrid();
      var pf = CSimulation.class.getDeclaredField("pathfindingProcessors"); pf.setAccessible(true); CPathfindingProcessor[] procs = (CPathfindingProcessor[]) pf.get(sim);
      CUnit owner = null; for (CUnit u : sim.getUnits()) if (!u.isBuilding() && !u.isDead()) { owner = u; break; }
      final Vector2[] captured = new Vector2[1]; final List<Vector2>[] got = new List[1];
      Random rnd = new Random(42); int queries = Integer.parseInt(System.getenv().getOrDefault("QUERIES", "300"));
      float[] sizes = {16f, 24f, 32f, 48f, 64f}; long hash = 1125899906842597L; int found = 0, empty = 0, points = 0; long updates = 0;
      float minX = grid.getWorldX(5), maxX = grid.getWorldX(grid.getWidth() - 6), minY = grid.getWorldY(5), maxY = grid.getWorldY(grid.getHeight() - 6);
      long t0 = System.nanoTime();
      for (int q = 0; q < queries; q++) {
        float sx = minX + rnd.nextFloat() * (maxX - minX), sy = minY + rnd.nextFloat() * (maxY - minY);
        float gx = sx + (rnd.nextFloat() - 0.5f) * 3000, gy = sy + (rnd.nextFloat() - 0.5f) * 3000;
        gx = Math.max(minX, Math.min(maxX, gx)); gy = Math.max(minY, Math.min(maxY, gy));
        float size = sizes[q % sizes.length]; boolean smooth = (q % 2) == 0;
        final List<Vector2>[] result = new List[1];
        CBehaviorMove move = new CBehaviorMove(owner) { @Override public void pathFound(List<Vector2> w, CSimulation s) { result[0] = w; } };
        sim.findNaiveSlowPath(owner, null, sx, sy, new Vector2(gx, gy), PathingGrid.MovementType.FOOT, size, smooth, move);
        int pi = owner.getPlayerIndex(); int guard = 0; while (result[0] == null && guard++ < 5000) { procs[pi].update(sim); updates++; }
        if (result[0] == null) { hash = 31 * hash + 7; continue; }
        found++; if (result[0].isEmpty()) empty++;
        hash = 31 * hash + result[0].size(); for (Vector2 p : result[0]) { hash = 31 * hash + Float.floatToIntBits(p.x); hash = 31 * hash + Float.floatToIntBits(p.y); points++; }
      }
      long t1 = System.nanoTime();
      System.err.println("RIG: PATHCHECK queries " + queries + " answered " + found + " (empty " + empty + "), waypoints " + points + ", processor updates " + updates + ", hash " + hash + ", time " + (t1 - t0) / 1000000 + " ms");
    } catch (Throwable t) { t.printStackTrace(); System.err.println("RIG: PATHCHECK failed " + t); }
    return true;
  }
}
