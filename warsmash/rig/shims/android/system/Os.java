package android.system;
public final class Os { public static final java.util.Map<String,String> ENV = new java.util.concurrent.ConcurrentHashMap<>();
  public static String getenv(String k) { String v = ENV.get(k); return v != null ? v : System.getenv(k); }
  public static void setenv(String k, String v, boolean o) { ENV.put(k, v); } }
