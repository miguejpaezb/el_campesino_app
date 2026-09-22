package com.miguelpaezdev.elcampesino.ui.navigation

import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.miguelpaezdev.elcampesino.ui.screens.SectionScreen
import com.miguelpaezdev.elcampesino.ui.screens.lots.LotsScreen

private const val TRANSITION_DURATION = 300

@Composable
fun AppNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier,
) {
    NavHost(
        navController = navController,
        startDestination = Destinations.Dashboard,
        modifier = modifier,
        enterTransition = {
            fadeIn(animationSpec = tween(TRANSITION_DURATION))
        },
        exitTransition = {
            fadeOut(animationSpec = tween(TRANSITION_DURATION))
        },
        popEnterTransition = {
            fadeIn(animationSpec = tween(TRANSITION_DURATION))
        },
        popExitTransition = {
            fadeOut(animationSpec = tween(TRANSITION_DURATION))
        },
    ) {
        Destinations.all.forEach { item ->
            composable(item.route) {
                if (item.route == Destinations.Lotes) {
                    LotsScreen()
                } else {
                    SectionScreen(eyebrow = item.eyebrow, title = item.title)
                }
            }
        }
    }
}
