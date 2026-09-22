package com.miguelpaezdev.elcampesino.ui.navigation

import androidx.annotation.DrawableRes
import com.miguelpaezdev.elcampesino.R

data class NavItem(
    val route: String,
    val label: String,
    @DrawableRes val icon: Int,
    val eyebrow: String,
    val title: String,
)

object Destinations {

    const val Dashboard = "dashboard"
    const val Lotes = "lotes"
    const val Alimentacion = "alimentacion"
    const val Sanidad = "sanidad"
    const val Produccion = "produccion"
    const val Trazabilidad = "trazabilidad"
    const val Iot = "iot"
    const val Usuarios = "usuarios"
    const val Cuenta = "cuenta"

    val menu = listOf(
        NavItem(
            route = Dashboard,
            label = "Dashboard",
            icon = R.drawable.ic_dashboard,
            eyebrow = "Panel de control",
            title = "Producción semanal",
        ),
        NavItem(
            route = Lotes,
            label = "Inventario Aves",
            icon = R.drawable.ic_lotes,
            eyebrow = "Inventario de Aves",
            title = "Gestión de lotes",
        ),
        NavItem(
            route = Alimentacion,
            label = "Alimento",
            icon = R.drawable.ic_alimento,
            eyebrow = "Alimentación",
            title = "Registro de suministro",
        ),
        NavItem(
            route = Sanidad,
            label = "Sanidad",
            icon = R.drawable.ic_sanidad,
            eyebrow = "Sanidad",
            title = "Panel de sanidad",
        ),
        NavItem(
            route = Produccion,
            label = "Producción Diaria",
            icon = R.drawable.ic_produccion,
            eyebrow = "Producción Diaria",
            title = "Registro de postura",
        ),
        NavItem(
            route = Trazabilidad,
            label = "Trazabilidad",
            icon = R.drawable.ic_trazabilidad,
            eyebrow = "Trazabilidad",
            title = "Trazabilidad y auditoría",
        ),
        NavItem(
            route = Iot,
            label = "Monitoreo IoT",
            icon = R.drawable.ic_iot,
            eyebrow = "Monitoreo IoT",
            title = "En construcción",
        ),
        NavItem(
            route = Usuarios,
            label = "Usuarios",
            icon = R.drawable.ic_usuarios,
            eyebrow = "Usuarios",
            title = "En construcción",
        ),
    )

    val cuenta = NavItem(
        route = Cuenta,
        label = "Administrar cuenta",
        icon = R.drawable.ic_usuarios,
        eyebrow = "Administrar cuenta",
        title = "En construcción",
    )

    val all = menu + cuenta
}
