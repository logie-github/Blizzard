package com.logie.blizz.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.text.KeyboardOptions
import com.logie.blizz.wow.WowLogin

/**
 * The account a World of Warcraft version logs in with by itself at every start: the one given here, else the one the World of
 * Warcraft app had saved in its export. For [version] (a [WowLogin] key). The password stays in the app's own storage and is typed
 * at the game's login screen, nowhere else.
 */
@Composable
internal fun AutoLoginCard(version: String, accountLabel: String) {
    val context = LocalContext.current
    var own by remember(version) { mutableStateOf(WowLogin.own(context, version)) }
    var exported by remember(version) { mutableStateOf(WowLogin.exported(context, version)) }
    var name by remember(version) { mutableStateOf(own?.name ?: "") }
    var password by remember(version) { mutableStateOf(own?.password ?: "") }
    SettingCard("Auto login") {
        val status = when {
            own != null -> "Logs in as ${own!!.name} at every start."
            exported != null -> "Logs in as ${exported!!.name} at every start (from the World of Warcraft app's export)."
            else -> "Not set: the game will ask for the password at its login screen. Give the account below to log in by itself."
        }
        Text(status, style = MaterialTheme.typography.bodyMedium, color = if (own != null || exported != null) Colors.Ice else Colors.Gold)
        val colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = Colors.Text, unfocusedTextColor = Colors.Text,
            focusedBorderColor = Colors.Ice, unfocusedBorderColor = Colors.Steel, cursorColor = Colors.Ice,
            focusedContainerColor = Colors.Abyss.copy(alpha = 0.55f), unfocusedContainerColor = Colors.Abyss.copy(alpha = 0.55f),
        )
        OutlinedTextField(
            value = name, onValueChange = { name = it }, label = { Text(accountLabel, color = Colors.Mist) }, singleLine = true,
            textStyle = MaterialTheme.typography.bodyLarge, colors = colors, modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(autoCorrectEnabled = false),
        )
        OutlinedTextField(
            value = password, onValueChange = { password = it }, label = { Text("Password", color = Colors.Mist) }, singleLine = true,
            visualTransformation = PasswordVisualTransformation(), textStyle = MaterialTheme.typography.bodyLarge, colors = colors,
            modifier = Modifier.fillMaxWidth(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, autoCorrectEnabled = false),
        )
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            FrameButton("Save", primary = name.isNotBlank() && password.isNotEmpty()) {
                if (name.isNotBlank() && password.isNotEmpty()) {
                    WowLogin.setOwn(context, version, name, password)
                    own = WowLogin.own(context, version)
                }
            }
            if (own != null) FrameButton("Use the export's", primary = false) {
                WowLogin.clearOwn(context, version)
                own = null; name = ""; password = ""
                exported = WowLogin.exported(context, version)
            }
        }
    }
}
