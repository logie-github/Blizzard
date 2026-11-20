package rig;
import java.lang.reflect.*; import java.nio.*; import java.util.concurrent.atomic.AtomicInteger;
import com.badlogic.gdx.graphics.*;
public final class MockGL {
  static final AtomicInteger ids = new AtomicInteger(1);
  public static GL32 create() {
    return (GL32) Proxy.newProxyInstance(MockGL.class.getClassLoader(), new Class<?>[]{GL32.class}, (p, m, a) -> {
      String n = m.getName(); Class<?> r = m.getReturnType();
      if (n.startsWith("glGen") || n.startsWith("glCreate")) {
        if (a != null) for (Object o : a) if (o instanceof IntBuffer b) { while (b.hasRemaining()) b.put(ids.getAndIncrement()); b.flip(); }
        if (r == int.class) return ids.getAndIncrement(); return null; }
      if (n.equals("glGetShaderiv") || n.equals("glGetProgramiv") || n.equals("glGetIntegerv") || n.equals("glGetFramebufferiv")|| n.equals("glGetRenderbufferParameteriv")) {
        int pname = (Integer) a[a.length-2 >= 0 && a[a.length-1] instanceof IntBuffer ? a.length-2 : 0];
        IntBuffer b = (IntBuffer) a[a.length-1];
        int v = switch (pname) { case 0x8B81, 0x8B82, 0x8B83 -> 1; case 0x8B86, 0x8B89, 0x8B87, 0x8B8A, 0x8B84 -> 0;
          case 0x0D33, 0x84E8 -> 8192; case 0x8872, 0x8B4D, 0x8B4C, 0x8869 -> 16; default -> 0; };
        b.put(b.position(), v); return null; }
      if (n.equals("glCheckFramebufferStatus")) return 0x8CD5;
      if (n.equals("glGetString")) return "Mock";
      if (n.equals("glGetError")) return 0;
      if (r == String.class) return "";
      if (r == int.class) return n.contains("Location") ? 0 : 0;
      if (r == boolean.class) return true;
      if (r == float.class) return 0f; if (r == long.class) return 0L;
      return null; });
  }
}
