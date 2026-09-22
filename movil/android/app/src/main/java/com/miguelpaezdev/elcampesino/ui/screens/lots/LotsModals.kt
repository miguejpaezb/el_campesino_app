package com.miguelpaezdev.elcampesino.ui.screens.lots

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.miguelpaezdev.elcampesino.data.dto.LotCreateRequest
import com.miguelpaezdev.elcampesino.data.dto.LotDto
import com.miguelpaezdev.elcampesino.data.dto.LotUpdateRequest
import com.miguelpaezdev.elcampesino.ui.components.AppButton
import com.miguelpaezdev.elcampesino.ui.components.AppButtonVariant
import com.miguelpaezdev.elcampesino.ui.components.AppDateField
import com.miguelpaezdev.elcampesino.ui.components.AppFormGroup
import com.miguelpaezdev.elcampesino.ui.components.AppModal
import com.miguelpaezdev.elcampesino.ui.components.AppTextField
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.CountdownBackground
import com.miguelpaezdev.elcampesino.ui.theme.CountdownBarBackground
import com.miguelpaezdev.elcampesino.ui.theme.RowDivider
import com.miguelpaezdev.elcampesino.ui.theme.SearchPlaceholder
import com.miguelpaezdev.elcampesino.ui.theme.SecondaryText
import com.miguelpaezdev.elcampesino.ui.theme.TitleText
import com.miguelpaezdev.elcampesino.ui.theme.WarningBackground
import com.miguelpaezdev.elcampesino.ui.theme.WarningBorder
import com.miguelpaezdev.elcampesino.ui.theme.WarningText
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlinx.coroutines.delay

private const val DISCARD_SECONDS = 5

private fun todayIso(): String =
    SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())

private fun format2(value: Double): String =
    String.format(Locale.US, "%.2f", value)

@Composable
fun CreateLotModal(
    submitting: Boolean,
    onClose: () -> Unit,
    onSubmit: (LotCreateRequest) -> Unit,
) {
    var lotCode by remember { mutableStateOf("") }
    var breed by remember { mutableStateOf("") }
    var quantity by remember { mutableStateOf("") }
    var entryDate by remember { mutableStateOf(todayIso()) }
    var observations by remember { mutableStateOf("") }
    var codeError by remember { mutableStateOf<String?>(null) }
    var breedError by remember { mutableStateOf<String?>(null) }
    var qtyError by remember { mutableStateOf<String?>(null) }

    fun submit() {
        val parsed = quantity.toIntOrNull()
        codeError = if (lotCode.trim().isEmpty()) "El código del lote es obligatorio" else null
        breedError = if (breed.trim().isEmpty()) "La raza es obligatoria" else null
        qtyError = if (quantity.isEmpty() || parsed == null || parsed <= 0) {
            "Ingresa una cantidad mayor a 0"
        } else {
            null
        }
        if (codeError != null || breedError != null || qtyError != null || parsed == null) return

        onSubmit(
            LotCreateRequest(
                lotCode = lotCode.trim(),
                breed = breed.trim(),
                initialQuantity = parsed,
                entryDate = entryDate.ifBlank { null },
                observations = observations.trim().ifBlank { null },
            ),
        )
    }

    AppModal(
        title = "Crear lote de aves",
        subtitle = "Registra un nuevo lote en la granja",
        onClose = onClose,
        footer = {
            AppButton(
                text = "Cancelar",
                onClick = onClose,
                variant = AppButtonVariant.SECONDARY,
                enabled = !submitting,
            )
            AppButton(
                text = if (submitting) "Creando..." else "Crear lote",
                onClick = { submit() },
                enabled = !submitting,
            )
        },
    ) {
        AppFormGroup(label = "Código del lote", error = codeError) {
            AppTextField(
                value = lotCode,
                onValueChange = {
                    lotCode = it
                    codeError = null
                },
                placeholder = "Ej: lote0003",
                maxLength = 20,
                enabled = !submitting,
            )
        }
        AppFormGroup(label = "Raza", error = breedError) {
            AppTextField(
                value = breed,
                onValueChange = {
                    breed = it
                    breedError = null
                },
                placeholder = "Ej: Hy-Line Brown",
                maxLength = 50,
                enabled = !submitting,
            )
        }
        AppFormGroup(label = "Cantidad inicial", error = qtyError) {
            AppTextField(
                value = quantity,
                onValueChange = {
                    quantity = it
                    qtyError = null
                },
                placeholder = "Ej: 100",
                keyboardType = KeyboardType.Number,
                enabled = !submitting,
            )
        }
        AppFormGroup(label = "Fecha de ingreso") {
            AppDateField(
                value = entryDate,
                onChange = { entryDate = it },
                enabled = !submitting,
            )
        }
        AppFormGroup(label = "Observaciones") {
            AppTextField(
                value = observations,
                onValueChange = { observations = it },
                placeholder = "Notas adicionales del lote",
                singleLine = false,
                minLines = 3,
                maxLength = 500,
                enabled = !submitting,
            )
        }
    }
}

@Composable
fun EditLotModal(
    lot: LotDto,
    submitting: Boolean,
    onClose: () -> Unit,
    onSubmit: (LotUpdateRequest) -> Unit,
) {
    var breed by remember { mutableStateOf(lot.breed) }
    var observations by remember { mutableStateOf(lot.observations.orEmpty()) }
    var breedError by remember { mutableStateOf<String?>(null) }

    fun submit() {
        if (breed.trim().isEmpty()) {
            breedError = "La raza es obligatoria"
            return
        }
        onSubmit(
            LotUpdateRequest(
                breed = breed.trim(),
                observations = observations.trim().ifBlank { null },
            ),
        )
    }

    AppModal(
        title = "Editando ${lot.lotCode}",
        subtitle = "Modifica los datos del lote",
        onClose = onClose,
        footer = {
            AppButton(
                text = "Cancelar",
                onClick = onClose,
                variant = AppButtonVariant.SECONDARY,
                enabled = !submitting,
            )
            AppButton(
                text = if (submitting) "Guardando..." else "Guardar cambios",
                onClick = { submit() },
                enabled = !submitting,
            )
        },
    ) {
        AppFormGroup(label = "Raza", error = breedError) {
            AppTextField(
                value = breed,
                onValueChange = {
                    breed = it
                    breedError = null
                },
                maxLength = 50,
                enabled = !submitting,
            )
        }
        AppFormGroup(label = "Observaciones") {
            AppTextField(
                value = observations,
                onValueChange = { observations = it },
                singleLine = false,
                minLines = 4,
                maxLength = 500,
                enabled = !submitting,
            )
        }
    }
}

@Composable
fun DiscardLotModal(
    lot: LotDto,
    submitting: Boolean,
    onClose: () -> Unit,
    onConfirm: (String, () -> Unit) -> Unit,
) {
    var reason by remember { mutableStateOf("") }
    var secondsLeft by remember { mutableStateOf<Int?>(null) }

    LaunchedEffect(secondsLeft) {
        val current = secondsLeft
        if (current == null) return@LaunchedEffect
        if (current > 0) {
            delay(1000L)
            secondsLeft = current - 1
        } else {
            onConfirm(reason.trim()) { secondsLeft = null }
        }
    }

    val counting = secondsLeft != null && !submitting
    val seconds = secondsLeft

    AppModal(
        title = "Descartar lote",
        subtitle = "${lot.lotCode} · ${lot.breed}",
        onClose = onClose,
        footer = {
            if (counting || submitting) {
                AppButton(
                    text = if (submitting) "Descartando..." else "Cancelar descarte",
                    onClick = { secondsLeft = null },
                    variant = AppButtonVariant.SECONDARY,
                    enabled = !submitting,
                )
            } else {
                AppButton(
                    text = "Cancelar",
                    onClick = onClose,
                    variant = AppButtonVariant.SECONDARY,
                )
                AppButton(
                    text = "Confirmar descarte",
                    onClick = { secondsLeft = DISCARD_SECONDS },
                    variant = AppButtonVariant.DANGER,
                    enabled = reason.trim().isNotEmpty(),
                )
            }
        },
    ) {
        Text(
            text = "Esta acción es irreversible: el lote quedará inactivo y " +
                "registrado con el motivo del descarte.",
            color = WarningText,
            fontSize = 14.sp,
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(WarningBackground)
                .border(1.dp, WarningBorder, RoundedCornerShape(12.dp))
                .padding(12.dp),
        )
        Spacer(modifier = Modifier.height(14.dp))
        Text(
            text = "Razón del descarte",
            color = SecondaryText,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
        )
        Spacer(modifier = Modifier.height(6.dp))
        AppTextField(
            value = reason,
            onValueChange = { reason = it },
            placeholder = "Indica el motivo del descarte",
            singleLine = false,
            minLines = 3,
            maxLength = 500,
            enabled = !(counting || submitting),
        )

        if (counting && seconds != null) {
            Spacer(modifier = Modifier.height(16.dp))
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(CountdownBackground)
                    .border(1.dp, RowDivider, RoundedCornerShape(14.dp))
                    .padding(16.dp),
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(10.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(CountdownBarBackground),
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth(fraction = seconds / DISCARD_SECONDS.toFloat())
                            .fillMaxHeight()
                            .clip(RoundedCornerShape(percent = 50))
                            .background(BrandBrown),
                    )
                }
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        text = seconds.toString(),
                        color = BrandBrown,
                        fontSize = 26.sp,
                        fontWeight = FontWeight.ExtraBold,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.width(34.dp),
                    )
                    Text(
                        text = "El lote se descartará en $seconds " +
                            (if (seconds == 1) "segundo" else "segundos") +
                            ". Puedes cancelar.",
                        color = SecondaryText,
                        fontSize = 13.sp,
                    )
                }
            }
        }
    }
}

@Composable
fun EvaluateResultModal(
    data: EvaluateData,
    onClose: () -> Unit,
) {
    AppModal(
        title = "Resultado de la evaluación",
        subtitle = data.lot.lotCode,
        onClose = onClose,
        footer = {
            AppButton(text = "Cerrar", onClick = onClose)
        },
    ) {
        Text(
            text = data.result.message,
            color = TitleText,
            fontSize = 16.sp,
        )
        Spacer(modifier = Modifier.height(12.dp))
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = "Estado resultante:",
                color = SecondaryText,
                fontSize = 15.sp,
            )
            StatusBadge(isActive = data.result.isActive)
        }
    }
}

@Composable
fun SummaryModal(
    data: SummaryData,
    onClose: () -> Unit,
) {
    val summary = data.summary
    val rows = listOf(
        "Lote" to summary.lotCode,
        "Raza" to summary.breed,
        "Semana actual" to summary.currentWeek.toString(),
        "Aves iniciales" to summary.initialQuantity.toString(),
        "Aves actuales" to summary.currentQuantity.toString(),
        "Total de huevos" to summary.totalEggs.toString(),
        "Promedio semanal" to format2(summary.averageWeeklyProduction),
        "Porcentaje de postura" to "${summary.layingPercentage}%",
        "Alimento total (kg)" to format2(summary.totalFeed),
        "Mortalidad total" to summary.totalMortality.toString(),
        "Porcentaje de mortalidad" to "${summary.mortalityPercentage}%",
        "Porcentaje de supervivencia" to "${summary.survivalPercentage}%",
        "Vacunas aplicadas" to summary.vaccinationCount.toString(),
        "Estado" to if (summary.isActive) "Activo" else "Descartado",
    )

    AppModal(
        title = "Resumen productivo - ${data.lot.lotCode}",
        subtitle = "Indicadores del lote",
        wide = true,
        onClose = onClose,
        footer = {
            AppButton(text = "Cerrar", onClick = onClose)
        },
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            rows.forEach { (label, value) ->
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(CountdownBackground)
                        .border(1.dp, RowDivider, RoundedCornerShape(12.dp))
                        .padding(horizontal = 14.dp, vertical = 12.dp),
                ) {
                    Text(
                        text = label.uppercase(),
                        color = SearchPlaceholder,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        letterSpacing = 0.5.sp,
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = value,
                        color = TitleText,
                        fontSize = 16.sp,
                    )
                }
            }
        }
    }
}
