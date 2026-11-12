package com.logie.blizz

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.logie.blizz.game.WindowsRuntime
import com.logie.blizz.ui.Launcher

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        // Crashes and failures from now on go to GitHub as issues; ones waiting from before go now.
        com.logie.blizz.reports.BugReports.start(this)
        // A crash of Wrath++'s game that was never reported (its runtime's logs stay on the phone) goes as the app starts.
        applicationContext.let { app -> Thread { runCatching { com.logie.blizz.wrathpp.WrathppSetup.reportCrashes(app) } }.start() }
        // World of Warcraft: Play starts the realm through this.
        com.logie.blizz.game.WowPlay.realm = com.logie.blizz.wow.WowRealmControl
        com.logie.blizz.wow.WowCtl.nativeWrapper = java.io.File(applicationInfo.nativeLibraryDir, "libblizzmaria.so")
        com.logie.blizz.music.MusicPlayer.load(this)
        setContent { Launcher() }
    }

    override fun onResume() {
        super.onResume()
        visible = true
        // A game prepared while the app was in the background starts now.
        WindowsRuntime.onLauncherShown(this)
        com.logie.blizz.music.MusicPlayer.foreground(this, true)
    }

    override fun onPause() {
        visible = false
        // A running game has its own sound.
        com.logie.blizz.music.MusicPlayer.foreground(this, false)
        super.onPause()
    }

    companion object {
        /** Whether the launcher is on screen (Android starts no screens from the background). */
        @Volatile var visible = false
    }
}
