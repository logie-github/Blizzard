package com.logie.blizz;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.view.Gravity;
import android.view.View;
import android.widget.*;

/** Offline showcase. Runtime integration belongs outside the presentation layer. */
public final class MainActivity extends Activity {
    private int background, panel, blue, textPrimary, muted, border, onBlue, bluePressed;
    private final Game[] games = {
        new Game("warcraft", "WORLD OF", "WARCRAFT", "A world worth getting lost in.", "Explore Azeroth, from its earliest adventures to new horizons.", "ROLE PLAYING", "W"),
        new Game("diablo", "THE WORLD OF", "DIABLO", "Into the darkness.", "Discover Sanctuary and its dark fantasy adventures.", "ACTION RPG", "D"),
        new Game("starcraft", "THE UNIVERSE OF", "STARCRAFT", "The frontier is calling.", "Explore a distant future of rival factions and interstellar strategy.", "STRATEGY", "S"),
        new Game("warcraft-rts", "THE ORIGINS OF", "WARCRAFT", "Every legend has a beginning.", "Return to the strategy adventures that shaped Azeroth.", "STRATEGY", "W")
    };
    private SharedPreferences prefs;
    private LinearLayout root, content;
    private String page = "Discover";
    private String filter = "All games";
    private String selected = "warcraft";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        background = getColor(R.color.blizzard_background);
        panel = getColor(R.color.blizzard_panel);
        blue = getColor(R.color.blizzard_blue);
        textPrimary = getColor(R.color.blizzard_text);
        muted = getColor(R.color.blizzard_text_muted);
        border = getColor(R.color.blizzard_border);
        onBlue = getColor(R.color.blizzard_on_blue);
        bluePressed = getColor(R.color.blizzard_blue_pressed);
        prefs = getSharedPreferences("library", MODE_PRIVATE);
        if (state != null) { page = state.getString("page", page); filter = state.getString("filter", filter); selected = state.getString("selected", selected); }
        render();
    }
    @Override public void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out); out.putString("page", page); out.putString("filter", filter); out.putString("selected", selected);
    }
    private void render() {
        FrameLayout scene = new FrameLayout(this);
        scene.setBackgroundColor(background);
        ImageView backdrop = new ImageView(this);
        backdrop.setImageResource(R.drawable.ice_background);
        backdrop.setScaleType(ImageView.ScaleType.CENTER_CROP);
        backdrop.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        scene.addView(backdrop, new FrameLayout.LayoutParams(-1, -1));
        View shade = new View(this);
        shade.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
            new int[]{0x99131929, 0xdd131929, 0xf5131929}));
        shade.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        scene.addView(shade, new FrameLayout.LayoutParams(-1, -1));
        root = column();
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
        scene.addView(root, new FrameLayout.LayoutParams(-1, -1));
        setContentView(scene);
        LinearLayout brand = row();
        brand.setGravity(Gravity.CENTER_VERTICAL);
        ImageView logo = new ImageView(this); logo.setImageResource(R.drawable.app_logo);
        logo.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        brand.addView(logo, new LinearLayout.LayoutParams(dp(48), dp(48)));
        LinearLayout title = column(); title.setPadding(dp(12),0,0,0);
        ImageView wordmark = new ImageView(this); wordmark.setImageResource(R.drawable.blizzard_wordmark);
        wordmark.setScaleType(ImageView.ScaleType.FIT_START); wordmark.setContentDescription("Blizzard Launcher");
        title.addView(wordmark, new LinearLayout.LayoutParams(dp(124), dp(65)));
        title.addView(text("YOUR NEXT ADVENTURE", 10, muted));
        brand.addView(title, new LinearLayout.LayoutParams(0,-2,1));
        TextView info = text("ⓘ",24,muted); info.setGravity(Gravity.CENTER);
        info.setContentDescription("About Blizzard Launcher"); info.setFocusable(true);
        info.setBackground(new RippleDrawable(ColorStateList.valueOf(0x4400b4ff), rounded(panel), null));
        info.setOnClickListener(v -> about()); brand.addView(info,new LinearLayout.LayoutParams(dp(48),dp(48))); root.addView(brand);
        ScrollView scroll = new ScrollView(this); scroll.setFillViewport(true);
        content = column(); content.setPadding(0,dp(28),0,dp(20)); scroll.addView(content); root.addView(scroll, new LinearLayout.LayoutParams(-1,0,1));
        if (page.equals("Discover")) discover(); else library();
        LinearLayout nav = row();
        for (String name : new String[]{"Discover", "Library"}) {
            Button b = button(name, page.equals(name)); b.setSelected(page.equals(name));
            b.setOnClickListener(v -> {page = name; render();});
            LinearLayout.LayoutParams navParams = new LinearLayout.LayoutParams(0,dp(52),1);
            if (nav.getChildCount() > 0) navParams.leftMargin = dp(8);
            nav.addView(b,navParams);
        }
        root.addView(nav);
        root.requestApplyInsets();
    }
    private void discover() {
        content.addView(text("THE COLLECTION",11,blue)); content.addView(text("Choose your universe.",30,textPrimary));
        TextView intro = text("Legendary worlds. One place to begin.",14,muted); intro.setPadding(0,dp(8),0,dp(20)); content.addView(intro);
        Game hero = games[0]; for(Game g:games) if(g.id.equals(selected)) hero=g;
        LinearLayout feature = column(); feature.setPadding(dp(24),dp(28),dp(24),dp(24));
        feature.setBackground(gradient());
        feature.addView(text("FEATURED UNIVERSE  /  " + hero.genre,10,blue));
        TextView emblem = text(hero.mark,80,blue); emblem.setGravity(Gravity.END); emblem.setTypeface(Typeface.SERIF,Typeface.BOLD); feature.addView(emblem);
        feature.addView(text(hero.eyebrow,12,muted));
        TextView name = text(hero.title,34,textPrimary); name.setTypeface(Typeface.SERIF,Typeface.BOLD); feature.addView(name);
        feature.addView(text(hero.tagline,16,textPrimary));
        Button explore = button("Explore universe  ›",true); final Game featured=hero; explore.setOnClickListener(v -> details(featured)); feature.addView(explore); content.addView(feature);
        TextView heading=text("Explore the collection",21,textPrimary); heading.setPadding(0,dp(26),0,dp(12)); content.addView(heading);
        LinearLayout filters=row(); for(String f:new String[]{"All games","Role playing","Strategy"}) { Button b=button(f,filter.equals(f)); b.setSelected(filter.equals(f)); b.setTextSize(11); b.setOnClickListener(v->{filter=f;render();}); LinearLayout.LayoutParams filterParams=new LinearLayout.LayoutParams(0,dp(48),1); if(filters.getChildCount()>0)filterParams.leftMargin=dp(6); filters.addView(b,filterParams); } content.addView(filters);
        for(Game g:games) if(filter.equals("All games") || (filter.equals("Strategy") ? g.genre.equals("STRATEGY") : !g.genre.equals("STRATEGY"))) card(g);
    }
    private void library() {
        content.addView(text("YOUR COLLECTION",11,blue)); content.addView(text("Library",32,textPrimary));
        content.addView(text("Keep your favorite universes close.",14,muted));
        boolean any=false; for(Game g:games) if(prefs.getBoolean(g.id,false)){card(g);any=true;}
        if(!any) { TextView empty=text("Your collection starts here.\n\nExplore a universe and add it to your library. Game installation and launching will arrive in a later stage.",17,muted); empty.setPadding(dp(20),dp(24),dp(20),dp(24)); empty.setBackground(rounded(panel)); LinearLayout.LayoutParams emptyParams=new LinearLayout.LayoutParams(-1,-2); emptyParams.topMargin=dp(24); emptyParams.bottomMargin=dp(12); content.addView(empty,emptyParams); Button browse=button("Explore games",true); browse.setOnClickListener(v->{page="Discover";render();}); content.addView(browse); }
    }
    private void card(Game g) {
        LinearLayout card=row(); card.setGravity(Gravity.CENTER_VERTICAL); card.setPadding(dp(16),dp(18),dp(16),dp(18)); card.setBackground(new RippleDrawable(ColorStateList.valueOf(0x4400b4ff),rounded(panel),null));
        TextView mark=text(g.mark,30,blue); mark.setTypeface(Typeface.SERIF,Typeface.BOLD); mark.setWidth(dp(48)); card.addView(mark);
        LinearLayout labels=column(); labels.addView(text(g.eyebrow+" "+g.title,15,textPrimary)); labels.addView(text(g.genre+"  ·  PREVIEW",10,muted)); card.addView(labels,new LinearLayout.LayoutParams(0,-2,1)); card.addView(text("›",25,blue));
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
    private Button button(String s,boolean active){
        Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextColor(active?onBlue:textPrimary);b.setTextSize(14);
        b.setMinHeight(dp(48));b.setMinimumHeight(dp(48));b.setPadding(dp(8),dp(8),dp(8),dp(8));
        b.setBackgroundTintList(null);
        b.setBackground(new RippleDrawable(ColorStateList.valueOf(active?bluePressed:0x4400b4ff),rounded(active?blue:panel),null));
        return b;
    }
    private GradientDrawable rounded(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(12));d.setStroke(dp(1),color==blue?blue:border);return d;}
    private GradientDrawable gradient(){GradientDrawable d=new GradientDrawable(GradientDrawable.Orientation.TR_BL,new int[]{0xdd174364,0xf5131929});d.setCornerRadius(dp(16));d.setStroke(dp(1),border);return d;}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private static final class Game {
        final String id,eyebrow,title,tagline,description,genre,mark;
        Game(String id,String eyebrow,String title,String tagline,String description,String genre,String mark){this.id=id;this.eyebrow=eyebrow;this.title=title;this.tagline=tagline;this.description=description;this.genre=genre;this.mark=mark;}
    }
}

