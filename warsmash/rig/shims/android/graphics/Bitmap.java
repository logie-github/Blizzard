package android.graphics;
public class Bitmap { public enum Config { ARGB_8888 }
  final int w,h; final int[] px;
  Bitmap(int w,int h){this.w=w;this.h=h;px=new int[w*h];}
  public static Bitmap createBitmap(int w,int h,Config c){return new Bitmap(w,h);}
  public int getWidth(){return w;} public int getHeight(){return h;}
  public void setPixel(int x,int y,int c){px[y*w+x]=c;} public int getPixel(int x,int y){return px[y*w+x];}
  public void setPixels(int[] p,int off,int stride,int x,int y,int ww,int hh){for(int j=0;j<hh;j++)System.arraycopy(p,off+j*stride,px,(y+j)*w+x,ww);}
  public void recycle(){} }
