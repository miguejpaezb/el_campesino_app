package com.miguelpaezdev.elcampesino.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInHorizontally
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.FooterText
import com.miguelpaezdev.elcampesino.ui.theme.LogoutButton
import com.miguelpaezdev.elcampesino.ui.theme.SuccessGreen
import com.miguelpaezdev.elcampesino.ui.theme.TitleText

enum class ToastType { SUCCESS, ERROR, INFO }

data class AppToast(
    val id: Long,
    val type: ToastType,
    val message: String,
)

@Composable
fun AppToastHost(
    toasts: List<AppToast>,
    onDismiss: (Long) -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(10.dp),
        horizontalAlignment = Alignment.End,
    ) {
        toasts.forEach { toast ->
            AppToastItem(
                toast = toast,
                onDismiss = { onDismiss(toast.id) },
            )
        }
    }
}

@Composable
private fun AppToastItem(
    toast: AppToast,
    onDismiss: () -> Unit,
) {
    var visible by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) { visible = true }

    AnimatedVisibility(
        visible = visible,
        enter = slideInHorizontally(initialOffsetX = { it }) + fadeIn(),
    ) {
        val dotColor = when (toast.type) {
            ToastType.SUCCESS -> SuccessGreen
            ToastType.ERROR -> LogoutButton
            ToastType.INFO -> BrandBrown
        }
        Surface(
            shape = RoundedCornerShape(14.dp),
            color = Color.White,
            shadowElevation = 14.dp,
            modifier = Modifier.widthIn(max = 360.dp),
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .clip(CircleShape)
                        .background(dotColor),
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = toast.message,
                    color = TitleText,
                    fontSize = 14.sp,
                    modifier = Modifier.weight(1f),
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "×",
                    color = FooterText,
                    fontSize = 18.sp,
                    modifier = Modifier.clickable(onClick = onDismiss),
                )
            }
        }
    }
}
