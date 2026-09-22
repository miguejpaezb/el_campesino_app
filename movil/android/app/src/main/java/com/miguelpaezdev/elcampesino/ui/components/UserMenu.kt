package com.miguelpaezdev.elcampesino.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.miguelpaezdev.elcampesino.data.dto.UserDto
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.BrandYellow
import com.miguelpaezdev.elcampesino.ui.theme.FooterDivider
import com.miguelpaezdev.elcampesino.ui.theme.FooterText
import com.miguelpaezdev.elcampesino.ui.theme.LogoutButton
import com.miguelpaezdev.elcampesino.ui.theme.MutedText
import com.miguelpaezdev.elcampesino.ui.theme.TitleText

@Composable
fun UserMenu(
    user: UserDto,
    expanded: Boolean,
    onDismissRequest: () -> Unit,
    onManageAccount: () -> Unit,
    onLogout: () -> Unit,
) {
    val initial = (user.fullName.firstOrNull() ?: user.username.firstOrNull() ?: 'A')
        .uppercase()
    val displayName = user.fullName.ifBlank { user.username }

    DropdownMenu(
        expanded = expanded,
        onDismissRequest = onDismissRequest,
        modifier = Modifier.width(320.dp),
        shape = RoundedCornerShape(16.dp),
        containerColor = Color.White,
        shadowElevation = 16.dp,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 14.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = user.email,
                color = MutedText,
                fontSize = 13.sp,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(10.dp))
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(CircleShape)
                    .background(BrandYellow),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = initial.toString(),
                    color = BrandBrown,
                    fontSize = 26.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = "¡Hola, $displayName!",
                color = TitleText,
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(14.dp))
            OutlinedButton(
                onClick = onManageAccount,
                border = BorderStroke(1.5.dp, BrandBrown),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = BrandBrown),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = "Administrar cuenta",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Button(
                onClick = onLogout,
                colors = ButtonDefaults.buttonColors(
                    containerColor = LogoutButton,
                    contentColor = Color.White,
                ),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    text = "Cerrar sesión",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            Spacer(modifier = Modifier.height(14.dp))
            HorizontalDivider(color = FooterDivider.copy(alpha = 0.4f))
            Spacer(modifier = Modifier.height(10.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = "Políticas de privacidad",
                    color = FooterText,
                    fontSize = 11.sp,
                    modifier = Modifier.clickable { },
                )
                Text(text = "-", color = FooterDivider, fontSize = 11.sp)
                Text(
                    text = "Condiciones de Servicio",
                    color = FooterText,
                    fontSize = 11.sp,
                    modifier = Modifier.clickable { },
                )
            }
        }
    }
}
