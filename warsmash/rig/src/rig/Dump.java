package rig;
import java.io.*; import java.nio.file.*;
import com.etheller.warsmash.datasources.*;
public class Dump { public static void main(String[] a) throws Exception {
  String g=System.getenv("GAME")+"/";
  if (System.getenv("MAPS") != null) { for (String m : System.getenv("MAPS").split(":")) { try { DataSource ms = new MpqDataSourceDescriptor(m).createDataSource(); for (String jn : new String[]{"war3map.j","Scripts\\war3map.j"}) { try (InputStream in = ms.getResourceAsStream(jn)) { if (in != null) { Path out = Path.of(a[0], Path.of(m).getFileName() + ".j"); Files.createDirectories(out.getParent()); Files.copy(in, out, StandardCopyOption.REPLACE_EXISTING); break; } } } } catch (Exception e) { System.err.println("map " + m + ": " + e); } } return; }
  java.util.List<DataSourceDescriptor> ds = new java.util.ArrayList<>();
  for (String m : new String[]{"War3.mpq","War3x.mpq","War3xLocal.mpq","War3Patch.mpq"}) ds.add(new MpqDataSourceDescriptor(g+m));
  if (System.getenv("EXTRA") != null) for (String m : System.getenv("EXTRA").split(":")) ds.add(new MpqDataSourceDescriptor(m));
  DataSource src = new CompoundDataSourceDescriptor(ds).createDataSource();
  for (int i=1;i<a.length;i++) { try (InputStream in = src.getResourceAsStream(a[i])) { if (in==null) { System.err.println("missing "+a[i]); continue; } Path out=Path.of(a[0], a[i].replace('\\','/')); Files.createDirectories(out.getParent()); Files.copy(in,out,StandardCopyOption.REPLACE_EXISTING); } }
} }
