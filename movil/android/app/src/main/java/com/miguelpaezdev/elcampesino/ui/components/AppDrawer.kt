package com.miguelpaezdev.elcampesino.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.miguelpaezdev.elcampesino.R
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import com.miguelpaezdev.elcampesino.ui.navigation.Destinations
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.BrandYellow
import com.miguelpaezdev.elcampesino.ui.theme.DrawerActive
import com.miguelpaezdev.elcampesino.ui.theme.InfoText

@Composable
fun AppDrawer(
    currentRoute: String?,
    user: UserDto,
    onNavigate: (String) -> Unit,
    onClose: () -> Unit,
    onLogout: () -> Unit,
) {
    var menuOpen by remember { mutableStateOf(false) }

    val initial = (user.fullName.firstOrNull() ?: user.username.firstOrNull() ?: 'A')
        .uppercase()
    val displayName = user.fullName.ifBlank { user.username }

    ModalDrawerSheet(
        modifier = Modifier.width(280.dp),
        drawerShape = RectangleShape,
        drawerContainerColor = BrandBrown,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(10.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        painter = painterResource(R.drawable.ic_pluma),
                        contentDescription = null,
                        tint = Color.Unspecified,
                        modifier = Modifier.size(40.dp),
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "El Campesino",
                        color = BrandYellow,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Medium,
                    )
                }
                IconButton(onClick = onClose) {
                    Icon(
                        painter = painterResource(R.drawable.ic_arrow),
                        contentDescription = "Cerrar menú",
                        tint = InfoText,
                        modifier = Modifier.size(20.dp),
                    )
                }
            }

            Spacer(modifier = Modifier.height(15.dp))

            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                Destinations.menu.forEach { item ->
                    val selected = currentRoute == item.route
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(10.dp))
                            .background(if (selected) DrawerActive else Color.Transparent)
                            .clickable { onNavigate(item.route) }
                            .padding(horizontal = 15.dp, vertical = 10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            painter = painterResource(item.icon),
                            contentDescription = null,
                            tint = InfoText,
                            modifier = Modifier.size(28.dp),
                        )
                        Spacer(modifier = Modifier.width(7.dp))
                        Text(
                            text = item.label,
                            color = InfoText,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            Box {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(10.dp))
                        .background(if (menuOpen) DrawerActive else Color.Transparent)
                        .clickable { menuOpen = !menuOpen }
                        .padding(horizontal = 15.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(BrandYellow),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = initial.toString(),
                            color = BrandBrown,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        text = displayName,
                        color = InfoText,
                        fontSize = 16.sp,
                    )
                }

                UserMenu(
                    user = user,
                    expanded = menuOpen,
                    onDismissRequest = { menuOpen = false },
                    onManageAccount = {
                        menuOpen = false
                        onNavigate(Destinations.Cuenta)
                    },
                    onLogout = {
                        menuOpen = false
                        onLogout()
                    },
                )
            }
        }
    }
}
