package com.miguelpaezdev.elcampesino.ui.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.miguelpaezdev.elcampesino.R
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import com.miguelpaezdev.elcampesino.ui.components.AppDrawer
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.InfoText
import com.miguelpaezdev.elcampesino.ui.theme.MainGradientEnd
import com.miguelpaezdev.elcampesino.ui.theme.MainGradientStart
import kotlinx.coroutines.launch

@Composable
fun AppShell(
    user: UserDto,
    onLogout: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val navController = rememberNavController()
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    ModalNavigationDrawer(
        modifier = modifier,
        drawerState = drawerState,
        gesturesEnabled = true,
        scrimColor = Color.Transparent,
        drawerContent = {
            AppDrawer(
                currentRoute = currentRoute,
                user = user,
                onNavigate = { route ->
                    scope.launch { drawerState.close() }
                    if (route != currentRoute) {
                        navController.navigate(route) {
                            popUpTo(Destinations.Dashboard) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                },
                onClose = { scope.launch { drawerState.close() } },
                onLogout = onLogout,
            )
        },
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(MainGradientStart, MainGradientEnd),
                    ),
                ),
        ) {
            AppNavHost(
                navController = navController,
                modifier = Modifier.fillMaxSize(),
            )

            if (!drawerState.isOpen) {
                MenuFab(
                    onClick = { scope.launch { drawerState.open() } },
                    modifier = Modifier
                        .align(Alignment.TopStart)
                        .statusBarsPadding()
                        .padding(start = 13.dp, top = 13.dp),
                )
            }
        }
    }
}

@Composable
private fun MenuFab(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .size(52.dp)
            .shadow(elevation = 10.dp, shape = CircleShape)
            .clip(CircleShape)
            .background(BrandBrown)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            painter = painterResource(R.drawable.ic_menu),
            contentDescription = "Abrir menú",
            tint = InfoText,
            modifier = Modifier.size(26.dp),
        )
    }
}
