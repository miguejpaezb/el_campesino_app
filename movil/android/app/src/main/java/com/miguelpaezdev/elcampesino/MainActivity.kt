package com.miguelpaezdev.elcampesino

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import com.miguelpaezdev.elcampesino.ui.screens.LoginScreen
import com.miguelpaezdev.elcampesino.ui.screens.WelcomeScreen
import com.miguelpaezdev.elcampesino.ui.theme.ElCampesinoTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ElCampesinoTheme {
                var loggedUser by remember { mutableStateOf<UserDto?>(null) }

                val user = loggedUser
                if (user == null) {
                    LoginScreen(
                        onLoggedIn = { loggedUser = it },
                        modifier = Modifier.fillMaxSize(),
                    )
                } else {
                    WelcomeScreen(
                        user = user,
                        onLogout = { loggedUser = null },
                        modifier = Modifier.fillMaxSize(),
                    )
                }
            }
        }
    }
}
