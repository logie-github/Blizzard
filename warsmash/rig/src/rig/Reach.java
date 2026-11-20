package rig;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
import com.etheller.warsmash.viewer5.handlers.w3x.environment.PathingGrid;
/** Flood fill on foot ($R radius) from $FROM (x,y) towards $TO (x,y) on the map's pathing grid: reachable or not. */
public class Reach extends Scenario {
  public boolean frame(War3MapViewer v, int n) {
    if (n < 40) return false;
    var g = v.simulation.getPathingGrid(); float r = Float.parseFloat(System.getenv().getOrDefault("R", "32"));
    String[] f = System.getenv("FROM").split(","), t = System.getenv("TO").split(",");
    int sx = Math.round(Float.parseFloat(f[0]) / 32), sy = Math.round(Float.parseFloat(f[1]) / 32), tx = Math.round(Float.parseFloat(t[0]) / 32), ty = Math.round(Float.parseFloat(t[1]) / 32);
    java.util.ArrayDeque<int[]> q = new java.util.ArrayDeque<>(); java.util.Set<Long> seen = new java.util.HashSet<>(); q.add(new int[]{sx, sy}); seen.add(((long) sx << 32) ^ (sy & 0xffffffffL));
    int best = Integer.MAX_VALUE, cells = 0; boolean reached = false;
    while (!q.isEmpty()) { int[] c = q.poll(); cells++; int d = Math.abs(c[0] - tx) + Math.abs(c[1] - ty); best = Math.min(best, d); if (d <= 1) { reached = true; break; }
      for (int[] o : new int[][]{{1,0},{-1,0},{0,1},{0,-1}}) { int nx = c[0] + o[0], ny = c[1] + o[1]; long k = ((long) nx << 32) ^ (ny & 0xffffffffL); if (!seen.add(k)) continue;
        if (g.isPathable(nx * 32f, ny * 32f, PathingGrid.MovementType.FOOT, r)) q.add(new int[]{nx, ny}); } }
    System.err.println("RIG: reach " + reached + " cells " + cells + " closest " + best * 32 + " units");
    return true;
  }
}
