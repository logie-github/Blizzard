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
        setContent { Launcher() }
    }

    override fun onResume() {
        super.onResume()
        visible = true
        // A game prepared while the app was in the background starts now.
        WindowsRuntime.onLauncherShown(this)
    }

    override fun onPause() {
        visible = false
        super.onPause()
    }

    companion object {
        /** Whether the launcher is on screen (Android starts no screens from the background). */
        @Volatile var visible = false
    }
}
