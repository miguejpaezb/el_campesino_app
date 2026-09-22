package com.miguelpaezdev.elcampesino.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.BrandYellow
import com.miguelpaezdev.elcampesino.ui.theme.FieldBorder
import com.miguelpaezdev.elcampesino.ui.theme.LogoutButton
import com.miguelpaezdev.elcampesino.ui.theme.SearchPlaceholder
import com.miguelpaezdev.elcampesino.ui.theme.SecondaryBorder
import com.miguelpaezdev.elcampesino.ui.theme.SecondaryText
import com.miguelpaezdev.elcampesino.ui.theme.TitleText
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

enum class AppButtonVariant { PRIMARY, SECONDARY, DANGER, BROWN }

@Composable
fun AppButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    variant: AppButtonVariant = AppButtonVariant.PRIMARY,
    enabled: Boolean = true,
) {
    val container = when (variant) {
        AppButtonVariant.PRIMARY -> BrandYellow
        AppButtonVariant.SECONDARY -> Color.White
        AppButtonVariant.DANGER -> LogoutButton
        AppButtonVariant.BROWN -> BrandBrown
    }
    val content = when (variant) {
        AppButtonVariant.PRIMARY -> Color(0xFF1D1D1D)
        AppButtonVariant.SECONDARY -> SecondaryText
        AppButtonVariant.DANGER -> Color.White
        AppButtonVariant.BROWN -> Color.White
    }
    val shape = RoundedCornerShape(12.dp)
    val padding = PaddingValues(horizontal = 18.dp, vertical = 11.dp)

    if (variant == AppButtonVariant.SECONDARY) {
        OutlinedButton(
            onClick = onClick,
            enabled = enabled,
            shape = shape,
            border = BorderStroke(1.5.dp, SecondaryBorder),
            colors = ButtonDefaults.outlinedButtonColors(
                containerColor = Color.White,
                contentColor = content,
                disabledContainerColor = Color.White,
                disabledContentColor = content.copy(alpha = 0.6f),
            ),
            contentPadding = padding,
            modifier = modifier,
        ) {
            Text(text = text, fontSize = 14.sp, fontWeight = FontWeight.Bold)
        }
    } else {
        Button(
            onClick = onClick,
            enabled = enabled,
            shape = shape,
            colors = ButtonDefaults.buttonColors(
                containerColor = container,
                contentColor = content,
                disabledContainerColor = container,
                disabledContentColor = content.copy(alpha = 0.6f),
            ),
            contentPadding = padding,
            modifier = modifier,
        ) {
            Text(text = text, fontSize = 14.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun AppTextField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    enabled: Boolean = true,
    singleLine: Boolean = true,
    minLines: Int = 1,
    keyboardType: KeyboardType = KeyboardType.Text,
    maxLength: Int? = null,
) {
    OutlinedTextField(
        value = value,
        onValueChange = { new ->
            if (maxLength == null || new.length <= maxLength) onValueChange(new)
        },
        placeholder = {
            Text(text = placeholder, color = SearchPlaceholder, fontSize = 14.sp)
        },
        singleLine = singleLine,
        minLines = minLines,
        enabled = enabled,
        shape = RoundedCornerShape(10.dp),
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = BrandBrown,
            unfocusedBorderColor = FieldBorder,
            disabledBorderColor = FieldBorder,
            focusedContainerColor = Color.White,
            unfocusedContainerColor = Color.White,
            disabledContainerColor = Color.White,
            cursorColor = BrandBrown,
        ),
        modifier = modifier.fillMaxWidth(),
    )
}

@Composable
fun AppFormGroup(
    label: String,
    modifier: Modifier = Modifier,
    error: String? = null,
    content: @Composable () -> Unit,
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(bottom = 14.dp),
    ) {
        Text(
            text = label,
            color = SecondaryText,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
        )
        Spacer(modifier = Modifier.height(6.dp))
        content()
        if (error != null) {
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = error,
                color = LogoutButton,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppDateField(
    value: String,
    onChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    var showPicker by remember { mutableStateOf(false) }
    val formatter = remember { SimpleDateFormat("yyyy-MM-dd", Locale.US) }

    Box(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(10.dp))
                .background(Color.White)
                .border(1.dp, FieldBorder, RoundedCornerShape(10.dp))
                .clickable(enabled = enabled) { showPicker = true }
                .padding(horizontal = 12.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = value.ifBlank { "Seleccionar fecha" },
                color = if (value.isBlank()) SearchPlaceholder else TitleText,
                fontSize = 15.sp,
            )
        }

        if (showPicker) {
            val state = rememberDatePickerState(
                initialSelectedDateMillis = value.toDateMillis(),
            )
            DatePickerDialog(
                onDismissRequest = { showPicker = false },
                confirmButton = {
                    TextButton(
                        onClick = {
                            state.selectedDateMillis?.let {
                                onChange(formatter.format(Date(it)))
                            }
                            showPicker = false
                        },
                    ) {
                        Text("Aceptar")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showPicker = false }) {
                        Text("Cancelar")
                    }
                },
            ) {
                DatePicker(state = state)
            }
        }
    }
}

private fun String.toDateMillis(): Long? = runCatching {
    SimpleDateFormat("yyyy-MM-dd", Locale.US).parse(this)?.time
}.getOrNull()
