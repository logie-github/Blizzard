package com.logie.blizz;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

/** Offline showcase. Runtime integration belongs outside the presentation layer. */
public final class MainActivity extends Activity {
    private static final int BG = 0xff0a101c, PANEL = 0xff141f30, BLUE = 0xff58c8ff, MUTED = 0xffa3b3c9;
    private final Game[] games = {
        new Game("warcraft", "WORLD OF", "WARCRAFT", "A world worth getting lost in.", "Explore Azeroth, from its earliest adventures to new horizons.", "ROLE PLAYING", 0xff37577d, "W"),
        new Game("diablo", "THE WORLD OF", "DIABLO", "Into the darkness.", "Discover Sanctuary and its dark fantasy adventures.", "ACTION RPG", 0xff773b3e, "D"),
        new Game("starcraft", "THE UNIVERSE OF", "STARCRAFT", "The frontier is calling.", "Explore a distant future of rival factions and interstellar strategy.", "STRATEGY", 0xff345d69, "S"),
        new Game("warcraft-rts", "THE ORIGINS OF", "WARCRAFT", "Every legend has a beginning.", "Return to the strategy adventures that shaped Azeroth.", "STRATEGY", 0xff536447, "W")
    };
    private SharedPreferences prefs;
    private LinearLayout root, content;
    private String page = "Discover";
    private String filter = "All games";
    private String selected = "warcraft";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs = getSharedPreferences("library", MODE_PRIVATE);
        if (state != null) { page = state.getString("page", page); filter = state.getString("filter", filter); selected = state.getString("selected", selected); }
        render();
    }
    @Override public void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out); out.putString("page", page); out.putString("filter", filter); out.putString("selected", selected);
    }
    private void render() {
        root = column(); root.setBackgroundColor(BG);
        root.setPadding(dp(22), dp(20), dp(22), dp(12));
        // Respect Android 15 edge-to-edge system bars and display cutouts.
        root.setOnApplyWindowInsetsListener((v, insets) -> {
            if (android.os.Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets bars = insets.getInsets(android.view.WindowInsets.Type.systemBars() | android.view.WindowInsets.Type.displayCutout());
                v.setPadding(dp(22) + bars.left, dp(16) + bars.top, dp(22) + bars.right, dp(12) + bars.bottom);
            } else {
                v.setPadding(dp(22) + insets.getSystemWindowInsetLeft(), dp(16) + insets.getSystemWindowInsetTop(), dp(22) + insets.getSystemWindowInsetRight(), dp(12) + insets.getSystemWindowInsetBottom());
            }
            return insets;
        });
        setContentView(root);
        LinearLayout brand = row();
        TextView logo = text("B", 28, BLUE); logo.setTypeface(null, Typeface.BOLD); brand.addView(logo);
        LinearLayout title = column(); title.setPadding(dp(12),0,0,0); title.addView(text("BLIZZARD LAUNCHER", 16, Color.WHITE)); title.addView(text("YOUR NEXT ADVENTURE", 10, MUTED));
        brand.addView(title, new LinearLayout.LayoutParams(0,-2,1));
        TextView info = text("ⓘ",24,MUTED); info.setContentDescription("About Blizzard Launcher"); info.setOnClickListener(v -> about()); brand.addView(info); root.addView(brand);
        ScrollView scroll = new ScrollView(this); scroll.setFillViewport(true);
        content = column(); content.setPadding(0,dp(28),0,dp(20)); scroll.addView(content); root.addView(scroll, new LinearLayout.LayoutParams(-1,0,1));
        if (page.equals("Discover")) discover(); else library();
        LinearLayout nav = row();
        for (String name : new String[]{"Discover", "Library"}) {
            Button b = button(name, page.equals(name)); b.setOnClickListener(v -> {page = name; render();}); nav.addView(b,new LinearLayout.LayoutParams(0,dp(52),1));
        }
        root.addView(nav);
        root.requestApplyInsets();
    }
    private void discover() {
        content.addView(text("THE COLLECTION",11,BLUE)); content.addView(text("Choose your universe.",30,Color.WHITE));
        TextView intro = text("Legendary worlds. One place to begin.",14,MUTED); intro.setPadding(0,dp(8),0,dp(20)); content.addView(intro);
        Game hero = games[0]; for(Game g:games) if(g.id.equals(selected)) hero=g;
        LinearLayout feature = column(); feature.setPadding(dp(24),dp(28),dp(24),dp(24));
        feature.setBackground(gradient(hero.color));
        feature.addView(text("FEATURED UNIVERSE  /  " + hero.genre,10,0xffceeaff));
        TextView emblem = text(hero.mark,80,0xffa9c8e5); emblem.setGravity(Gravity.END); emblem.setTypeface(Typeface.SERIF,Typeface.BOLD); feature.addView(emblem);
        feature.addView(text(hero.eyebrow,12,0xffd0e0ee));
        TextView name = text(hero.title,34,Color.WHITE); name.setTypeface(Typeface.SERIF,Typeface.BOLD); feature.addView(name);
        feature.addView(text(hero.tagline,16,Color.WHITE));
        Button explore = button("Explore universe  ›",true); final Game featured=hero; explore.setOnClickListener(v -> details(featured)); feature.addView(explore); content.addView(feature);
        TextView heading=text("Explore the collection",21,Color.WHITE); heading.setPadding(0,dp(26),0,dp(12)); content.addView(heading);
        LinearLayout filters=row(); for(String f:new String[]{"All games","Role playing","Strategy"}) { Button b=button(f,filter.equals(f)); b.setTextSize(11); b.setOnClickListener(v->{filter=f;render();}); filters.addView(b,new LinearLayout.LayoutParams(0,dp(48),1)); } content.addView(filters);
        for(Game g:games) if(filter.equals("All games") || (filter.equals("Strategy") ? g.genre.equals("STRATEGY") : !g.genre.equals("STRATEGY"))) card(g);
    }
    private void library() {
        content.addView(text("YOUR COLLECTION",11,BLUE)); content.addView(text("Library",32,Color.WHITE));
        content.addView(text("Keep your favorite universes close.",14,MUTED));
        boolean any=false; for(Game g:games) if(prefs.getBoolean(g.id,false)){card(g);any=true;}
        if(!any) { TextView empty=text("Your collection starts here.\n\nExplore a universe and add it to your library. Game installation and launching will arrive in a later stage.",17,MUTED); empty.setPadding(0,dp(42),0,dp(24)); content.addView(empty); Button browse=button("Explore games",true); browse.setOnClickListener(v->{page="Discover";render();}); content.addView(browse); }
    }
    private void card(Game g) {
        LinearLayout card=row(); card.setGravity(Gravity.CENTER_VERTICAL); card.setPadding(dp(16),dp(18),dp(16),dp(18)); card.setBackground(rounded(PANEL));
        TextView mark=text(g.mark,30,g.color | 0xff808080); mark.setTypeface(Typeface.SERIF,Typeface.BOLD); mark.setWidth(dp(48)); card.addView(mark);
        LinearLayout labels=column(); labels.addView(text(g.eyebrow+" "+g.title,15,Color.WHITE)); labels.addView(text(g.genre+"  ·  PREVIEW",10,MUTED)); card.addView(labels,new LinearLayout.LayoutParams(0,-2,1)); card.addView(text("›",25,BLUE));
        card.setOnClickListener(v->{selected=g.id;details(g);}); card.setFocusable(true); card.setContentDescription("Explore "+g.eyebrow+" "+g.title);
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2); p.topMargin=dp(12); content.addView(card,p);
    }
    private void details(Game g) {
        boolean saved=prefs.getBoolean(g.id,false);
        new AlertDialog.Builder(this).setTitle(g.eyebrow+" "+g.title)
            .setMessage(g.tagline+"\n\n"+g.description+"\n\nShowcase preview\nGame installation and launching are not connected yet.")
            .setPositiveButton(saved?"Remove from library":"Add to library",(d,w)->{prefs.edit().putBoolean(g.id,!saved).apply();render();})
            .setNeutralButton("Feature this universe",(d,w)->{selected=g.id;page="Discover";render();})
            .setNegativeButton("Close",null).show();
    }
    private void about() { new AlertDialog.Builder(this).setTitle("Blizzard Launcher").setMessage("Version 0.1.0\nAn independent frontend showcase.\n\nThis first stage is an offline collection browser. No games, downloads, accounts or emulation runtimes are included.\n\nNot affiliated with Blizzard Entertainment.").setPositiveButton("Done",null).show(); }
    private LinearLayout column(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);return l;}
    private LinearLayout row(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.HORIZONTAL);return l;}
    private TextView text(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);return t;}
    private Button button(String s,boolean active){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextColor(active?BG:MUTED);b.setTextSize(14);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(active?BLUE:PANEL));return b;}
    private GradientDrawable rounded(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(12));return d;}
    private GradientDrawable gradient(int color){GradientDrawable d=new GradientDrawable(GradientDrawable.Orientation.TR_BL,new int[]{color,0xff101d31});d.setCornerRadius(dp(16));d.setStroke(dp(1),0xff34516e);return d;}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private static final class Game {
        final String id,eyebrow,title,tagline,description,genre,mark; final int color;
        Game(String id,String eyebrow,String title,String tagline,String description,String genre,int color,String mark){this.id=id;this.eyebrow=eyebrow;this.title=title;this.tagline=tagline;this.description=description;this.genre=genre;this.color=color;this.mark=mark;}
    }
}
