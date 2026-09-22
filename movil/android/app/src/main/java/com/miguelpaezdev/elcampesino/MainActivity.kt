package com.miguelpaezdev.elcampesino

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.miguelpaezdev.elcampesino.data.ApiException
import com.miguelpaezdev.elcampesino.data.RetrofitClient
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import com.miguelpaezdev.elcampesino.data.session.SessionManager
import com.miguelpaezdev.elcampesino.ui.navigation.AppShell
import com.miguelpaezdev.elcampesino.ui.screens.ConnectionErrorScreen
import com.miguelpaezdev.elcampesino.ui.screens.LoadingScreen
import com.miguelpaezdev.elcampesino.ui.screens.LoginScreen
import com.miguelpaezdev.elcampesino.ui.theme.ElCampesinoTheme
import kotlinx.coroutines.launch

private sealed interface SessionState {
    data object Loading : SessionState
    data object LoggedOut : SessionState
    data object NoConnection : SessionState
    data class LoggedIn(val user: UserDto) : SessionState
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.light(
                android.graphics.Color.TRANSPARENT,
                android.graphics.Color.TRANSPARENT,
            ),
            navigationBarStyle = SystemBarStyle.light(
                android.graphics.Color.argb(0xe6, 0xFF, 0xFF, 0xFF),
                android.graphics.Color.argb(0x80, 0xFF, 0xFF, 0xFF),
            ),
        )
        val session = (application as ElCampesinoApp).session
        setContent {
            ElCampesinoTheme {
                AppRoot(session = session)
            }
        }
    }
}

@Composable
private fun AppRoot(session: SessionManager) {
    var state by remember { mutableStateOf<SessionState>(SessionState.Loading) }
    var retryKey by remember { mutableIntStateOf(0) }
    val scope = rememberCoroutineScope()

    LaunchedEffect(retryKey) {
        state = SessionState.Loading

        val online = try {
            RetrofitClient.api.health().isSuccessful
        } catch (e: Exception) {
            false
        }
        if (!online) {
            state = SessionState.NoConnection
            return@LaunchedEffect
        }

        val token = session.getToken()
        if (token == null) {
            state = SessionState.LoggedOut
            return@LaunchedEffect
        }

        state = try {
            val user = RetrofitClient.unwrap(
                RetrofitClient.api.getMe(RetrofitClient.bearer(token)),
            )
            SessionState.LoggedIn(user)
        } catch (e: ApiException) {
            if (e.statusCode == 401) {
                session.clear()
                SessionState.LoggedOut
            } else {
                SessionState.NoConnection
            }
        } catch (e: Exception) {
            SessionState.NoConnection
        }
    }

    when (val current = state) {
        SessionState.Loading -> LoadingScreen(modifier = Modifier.fillMaxSize())

        SessionState.NoConnection -> ConnectionErrorScreen(
            onRetry = { retryKey++ },
            modifier = Modifier.fillMaxSize(),
        )

        SessionState.LoggedOut -> LoginScreen(
            onLoggedIn = { token, user ->
                scope.launch { session.save(token, user) }
                state = SessionState.LoggedIn(user)
            },
            modifier = Modifier.fillMaxSize(),
        )

        is SessionState.LoggedIn -> AppShell(
            user = current.user,
            onLogout = {
                scope.launch { session.clear() }
                state = SessionState.LoggedOut
            },
            modifier = Modifier.fillMaxSize(),
        )
    }
}
