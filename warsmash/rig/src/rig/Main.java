package rig;
import java.io.*; import java.lang.reflect.*; import java.nio.file.*; import java.util.*;
import com.badlogic.gdx.*; import com.badlogic.gdx.backends.headless.*; import com.badlogic.gdx.backends.headless.mock.graphics.MockGraphics;
import com.etheller.warsmash.*; import com.etheller.warsmash.units.DataTable; import com.etheller.warsmash.util.StringBundle;
import com.etheller.warsmash.viewer5.handlers.w3x.War3MapViewer;
public class Main {
  public static War3MapViewer viewer; public static int mapFrames; public static Object mapScreen;
  public static void main(String[] args) throws Exception {
    String game = System.getenv("GAME");
    String map = args[0]; Scenario sc = (Scenario) Class.forName(args[1]).getDeclaredConstructor().newInstance();
    android.system.Os.setenv("game_files", game, true); android.system.Os.setenv("GAME_VERSION", System.getenv().getOrDefault("GV","1"), true);
    android.system.Os.setenv("PLAYERS_COUNT", "16", true); android.system.Os.setenv("SERVER", "warsmash.net", true);
    android.system.Os.setenv("SCREEN_WIDTH", "", true); android.system.Os.setenv("SCREEN_HEIGHT", "", true);
    String wsrc = System.getenv("WSRC");
    String support = System.getenv().getOrDefault("SUPPORT", wsrc + "/assets/resources");
    String extra = System.getenv("EXTRA");
    List<String[]> layers = new ArrayList<>();
    Map<String, File> present = new HashMap<>(); for (File f : new File(game).listFiles()) if (f.isFile()) present.put(f.getName().toLowerCase(), f);
    for (String a : new String[]{"war3.mpq","war3local.mpq","war3x.mpq","war3xlocal.mpq","war3patch.mpq"}) if (present.containsKey(a)) layers.add(new String[]{"MPQ", present.get(a).getPath()});
    layers.add(new String[]{"Folder", game}); layers.add(new String[]{"Folder", game + "/Maps"});
    if (extra != null) for (String e : extra.split(":")) layers.add(new String[]{"Folder", e});
    layers.add(new String[]{"Folder", support});
    StringBuilder sb = new StringBuilder("[DataSources]\nCount=" + layers.size() + "\n");
    for (int i = 0; i < layers.size(); i++) { String s = String.format("%02d", i); sb.append("Type"+s+"="+layers.get(i)[0]+"\nPath"+s+"="+layers.get(i)[1]+"\n"); }
    String ini = java.nio.file.Files.readString(Path.of(wsrc, "assets/warsmash.ini"));
    sb.append("\n").append(ini.substring(ini.indexOf("[GamingNetwork]")));
    DataTable table = new DataTable(StringBundle.EMPTY); table.readTXT(new ByteArrayInputStream(sb.toString().getBytes()), true);
    KeysEmulator keys = new KeysEmulator();
    final WarsmashGdxMenuScreen[] menu = new WarsmashGdxMenuScreen[1];
    WarsmashGdxMultiScreenGame g = new WarsmashGdxMultiScreenGame(engine -> { menu[0] = new WarsmashGdxMenuScreen(table, engine, keys); engine.setScreen(menu[0]); });
    final int[] frame = {0}; final boolean[] started = {false};
    ApplicationListener wrap = new ApplicationListener() {
      public void create() { final Application real = Gdx.app; Gdx.app = (Application) java.lang.reflect.Proxy.newProxyInstance(Main.class.getClassLoader(), new Class<?>[]{Application.class}, (p2, m2, a2) -> m2.getName().equals("getType") ? Application.ApplicationType.Desktop : m2.invoke(real, a2));
        try { Class.forName("com.etheller.warsmash.viewer5.handlers.w3x.environment.TerrainShaders", true, Main.class.getClassLoader()); } catch (Exception e) { throw new RuntimeException(e); } Gdx.app = real; Ext.install(); Gdx.graphics = gfx(); var gl = MockGL.create(); Gdx.gl = Gdx.gl20 = Gdx.gl30 = Gdx.gl31 = Gdx.gl32 = gl;
        try { Field f = MockGraphics.class.getDeclaredField("gl20"); } catch (Exception ignored) {}
        g.create(); }
      public void resize(int w, int h) { g.resize(w, h); }
      public void render() {
        
        try {
          frame[0]++;
          if (!started[0] && frame[0] == 5) { started[0] = true; System.err.println("RIG: startMap " + map); menu[0].startMap(map); }
          try { g.render(); } catch (Throwable t) { if (viewer == null) throw t; System.err.println("RIG: EXC " + t); for (StackTraceElement e : t.getStackTrace()) { if (e.getClassName().contains("etheller")) System.err.println("RIG:   at " + e); } for (Throwable c = t.getCause(); c != null && c != c.getCause(); c = c.getCause()) { System.err.println("RIG:   cause " + c); for (StackTraceElement e : c.getStackTrace()) { if (e.getClassName().contains("etheller")) { System.err.println("RIG:     at " + e); break; } } } sc.exception(t); }
          Screen s = g.getScreen();
          if (s instanceof WarsmashGdxMapScreen ms) {
            mapScreen = ms;
            if (viewer == null) { Field f = WarsmashGdxMapScreen.class.getDeclaredField("viewer"); f.setAccessible(true); viewer = (War3MapViewer) f.get(ms); System.err.println("RIG: map screen at frame " + frame[0]); }
            mapFrames++;
            if (sc.frame(viewer, mapFrames)) { System.err.println("RIG: scenario done"); System.out.flush(); System.err.flush(); Runtime.getRuntime().halt(sc.failed ? 1 : 0); }
          }
          if (frame[0] > 200000) { System.err.println("RIG: timeout"); Runtime.getRuntime().halt(3); }
        } catch (Throwable t) { t.printStackTrace(); Runtime.getRuntime().halt(2); }
      }
      public void pause() {} public void resume() {} public void dispose() {}
    };
    HeadlessApplicationConfiguration cfg = new HeadlessApplicationConfiguration(); cfg.updatesPerSecond = 0;
    new HeadlessApplication(wrap, cfg);
  }
  static Graphics gfx() { return new MockGraphics() { public int getWidth(){return 1280;} public int getHeight(){return 720;} public int getBackBufferWidth(){return 1280;} public int getBackBufferHeight(){return 720;} public boolean isGL30Available(){return true;} public float getDeltaTime(){return 1f/30f;} public com.badlogic.gdx.graphics.GL20 getGL20(){return Gdx.gl20;} public com.badlogic.gdx.graphics.GL30 getGL30(){return Gdx.gl30;} public com.badlogic.gdx.graphics.GL31 getGL31(){return Gdx.gl31;} public com.badlogic.gdx.graphics.GL32 getGL32(){return Gdx.gl32;} public boolean isGL31Available(){return true;} public boolean isGL32Available(){return true;} };
  }
}
