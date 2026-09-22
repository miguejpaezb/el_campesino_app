package com.miguelpaezdev.elcampesino.ui.screens.lots

import androidx.annotation.DrawableRes
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CheckboxDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.miguelpaezdev.elcampesino.R
import com.miguelpaezdev.elcampesino.data.dto.LotDto
import com.miguelpaezdev.elcampesino.ui.components.AppDropdown
import com.miguelpaezdev.elcampesino.ui.components.PageHeader
import com.miguelpaezdev.elcampesino.ui.theme.ActiveBadgeBackground
import com.miguelpaezdev.elcampesino.ui.theme.ActiveBadgeText
import com.miguelpaezdev.elcampesino.ui.theme.BrandBrown
import com.miguelpaezdev.elcampesino.ui.theme.BrandYellow
import com.miguelpaezdev.elcampesino.ui.theme.CardBorder
import com.miguelpaezdev.elcampesino.ui.theme.CardWhite
import com.miguelpaezdev.elcampesino.ui.theme.DiscardedBadgeBackground
import com.miguelpaezdev.elcampesino.ui.theme.DiscardedBadgeText
import com.miguelpaezdev.elcampesino.ui.theme.InputBorder
import com.miguelpaezdev.elcampesino.ui.theme.RowDivider
import com.miguelpaezdev.elcampesino.ui.theme.RowSelectedBackground
import com.miguelpaezdev.elcampesino.ui.theme.SearchBackground
import com.miguelpaezdev.elcampesino.ui.theme.SearchPlaceholder
import com.miguelpaezdev.elcampesino.ui.theme.SecondaryBorder
import com.miguelpaezdev.elcampesino.ui.theme.TableHeaderBackground
import com.miguelpaezdev.elcampesino.ui.theme.TableHeaderText
import com.miguelpaezdev.elcampesino.ui.theme.TitleText

private val accionOptions = listOf(
    "" to "Acción por lote",
    "edit" to "Editar",
    "advance" to "Avanzar semana",
    "evaluate" to "Evaluar",
    "summary" to "Resumen",
    "discard" to "Descartar",
)

private val filtroOptions = listOf(
    "" to "Filtro",
    "active" to "Activos",
    "discarded" to "Descartados",
)

@Composable
fun LotsScreen(
    modifier: Modifier = Modifier,
    viewModel: LotsViewModel = viewModel(),
) {
    val state by viewModel.state.collectAsState()
    val filtered = remember(state.lots, state.search, state.filtroAplicado) {
        filterLots(state.lots, state.search, state.filtroAplicado)
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .statusBarsPadding()
            .navigationBarsPadding(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp, vertical = 24.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            PageHeader(eyebrow = "Inventario de Aves", title = "Gestión de lotes")

            LotsToolbar(
                state = state,
                onSearch = viewModel::onSearchChange,
                onAccion = viewModel::setAccion,
                onFiltro = viewModel::setFiltro,
                onApply = viewModel::applyAction,
                onClear = viewModel::clearAll,
                onCreate = viewModel::openCreate,
            )

            LotsTable(
                loading = state.loading,
                lots = filtered,
                selectedIds = state.selectedIds,
                onToggle = viewModel::toggleSelect,
                onToggleAll = viewModel::toggleSelectAll,
            )
        }

        if (state.createOpen) {
            CreateLotModal(
                submitting = state.submitting,
                onClose = viewModel::closeCreate,
                onSubmit = viewModel::createLot,
            )
        }

        state.editLot?.let { lot ->
            EditLotModal(
                lot = lot,
                submitting = state.submitting,
                onClose = viewModel::closeEdit,
                onSubmit = { request -> viewModel.updateLot(lot, request) },
            )
        }

        state.discardLot?.let { lot ->
            DiscardLotModal(
                lot = lot,
                submitting = state.submitting,
                onClose = viewModel::closeDiscard,
                onConfirm = { reason, onError -> viewModel.discardLot(lot, reason, onError) },
            )
        }

        state.evaluateResult?.let { data ->
            EvaluateResultModal(data = data, onClose = viewModel::closeEvaluate)
        }

        state.summaryData?.let { data ->
            SummaryModal(data = data, onClose = viewModel::closeSummary)
        }
    }
}

private fun filterLots(lots: List<LotDto>, search: String, filtroAplicado: String): List<LotDto> {
    val term = search.trim().lowercase()
    return lots
        .filter { lot ->
            when (filtroAplicado) {
                "active" -> lot.isActive
                "discarded" -> !lot.isActive
                else -> true
            }
        }
        .filter { lot ->
            term.isEmpty() ||
                lot.id.toString().contains(term) ||
                lot.lotCode.lowercase().contains(term)
        }
        .sortedByDescending { it.id }
}

@Composable
private fun LotsToolbar(
    state: LotsUiState,
    onSearch: (String) -> Unit,
    onAccion: (String) -> Unit,
    onFiltro: (String) -> Unit,
    onApply: () -> Unit,
    onClear: () -> Unit,
    onCreate: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .background(CardWhite)
            .border(1.dp, CardBorder, RoundedCornerShape(18.dp))
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(10.dp))
                    .background(SearchBackground)
                    .border(1.dp, CardBorder, RoundedCornerShape(10.dp))
                    .padding(horizontal = 10.dp),
            ) {
                if (state.search.isEmpty()) {
                    Text(
                        text = "Buscar por ID o código de lote",
                        color = SearchPlaceholder,
                        fontSize = 13.sp,
                        modifier = Modifier.align(Alignment.CenterStart),
                    )
                }
                BasicTextField(
                    value = state.search,
                    onValueChange = onSearch,
                    singleLine = true,
                    textStyle = TextStyle(color = TitleText, fontSize = 13.sp),
                    cursorBrush = SolidColor(BrandBrown),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 11.dp),
                )
            }

            IconSquareButton(
                icon = R.drawable.ic_add,
                background = BrandYellow,
                onClick = onCreate,
                contentDescription = "Crear lote",
                iconSize = 20.dp,
            )

            IconSquareButton(
                icon = R.drawable.ic_clean,
                background = Color.White,
                border = BorderStroke(1.5.dp, SecondaryBorder),
                onClick = onClear,
                contentDescription = "Limpiar filtros",
                iconSize = 18.dp,
            )
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            AppDropdown(
                selectedLabel = accionOptions.first { it.first == state.accion }.second,
                options = accionOptions,
                onSelect = onAccion,
                enabled = !state.accionBusy,
                modifier = Modifier.weight(1f),
            )

            AppDropdown(
                selectedLabel = filtroOptions.first { it.first == state.filtro }.second,
                options = filtroOptions,
                onSelect = onFiltro,
                enabled = !state.accionBusy,
                modifier = Modifier.weight(1f),
            )

            IconSquareButton(
                icon = R.drawable.ic_arrow,
                background = BrandBrown,
                onClick = onApply,
                contentDescription = "Aplicar",
                iconSize = 20.dp,
                rotate = 180f,
                enabled = !state.accionBusy,
            )
        }
    }
}

@Composable
private fun LotsTable(
    loading: Boolean,
    lots: List<LotDto>,
    selectedIds: Set<Int>,
    onToggle: (Int) -> Unit,
    onToggleAll: () -> Unit,
) {
    val allSelected = lots.isNotEmpty() && lots.all { it.id in selectedIds }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(20.dp))
            .background(CardWhite)
            .border(1.dp, CardBorder, RoundedCornerShape(20.dp))
            .padding(8.dp),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(TableHeaderBackground)
                .padding(vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(modifier = Modifier.width(40.dp), contentAlignment = Alignment.Center) {
                Checkbox(
                    checked = allSelected,
                    onCheckedChange = { onToggleAll() },
                    colors = checkboxColors(),
                )
            }
            HeaderCell("ID", modifier = Modifier.width(48.dp))
            HeaderCell("Lote", modifier = Modifier.weight(1f))
            HeaderCell("Estado", modifier = Modifier.padding(end = 16.dp))
        }

        when {
            loading -> EmptyRow("Cargando...")
            lots.isEmpty() -> EmptyRow("No se encontraron lotes")
            else -> lots.forEachIndexed { index, lot ->
                LotsRow(
                    lot = lot,
                    selected = lot.id in selectedIds,
                    onToggle = { onToggle(lot.id) },
                )
                if (index < lots.lastIndex) {
                    HorizontalDivider(color = RowDivider)
                }
            }
        }
    }
}

@Composable
private fun LotsRow(
    lot: LotDto,
    selected: Boolean,
    onToggle: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(if (selected) RowSelectedBackground else Color.Transparent)
            .clickable(onClick = onToggle)
            .padding(vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(modifier = Modifier.width(40.dp), contentAlignment = Alignment.Center) {
            Checkbox(
                checked = selected,
                onCheckedChange = null,
                colors = checkboxColors(),
            )
        }
        Text(
            text = String.format("%02d", lot.id),
            color = TitleText,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.width(48.dp),
        )
        Text(
            text = lot.lotCode,
            color = BrandBrown,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.weight(1f),
        )
        Box(modifier = Modifier.padding(end = 16.dp)) {
            StatusBadge(isActive = lot.isActive)
        }
    }
}

@Composable
private fun HeaderCell(text: String, modifier: Modifier = Modifier) {
    Text(
        text = text.uppercase(),
        color = TableHeaderText,
        fontSize = 12.sp,
        fontWeight = FontWeight.Bold,
        letterSpacing = 0.5.sp,
        modifier = modifier,
    )
}

@Composable
private fun EmptyRow(message: String) {
    Text(
        text = message,
        color = SearchPlaceholder,
        fontSize = 15.sp,
        textAlign = TextAlign.Center,
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 30.dp),
    )
}

@Composable
fun StatusBadge(isActive: Boolean) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(percent = 50))
            .background(if (isActive) ActiveBadgeBackground else DiscardedBadgeBackground)
            .padding(horizontal = 10.dp, vertical = 4.dp),
    ) {
        Text(
            text = if (isActive) "Activo" else "Descartado",
            color = if (isActive) ActiveBadgeText else DiscardedBadgeText,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
        )
    }
}

@Composable
private fun checkboxColors() = CheckboxDefaults.colors(
    checkedColor = BrandBrown,
    uncheckedColor = InputBorder,
    checkmarkColor = Color.White,
)

@Composable
private fun IconSquareButton(
    @DrawableRes icon: Int,
    background: Color,
    onClick: () -> Unit,
    contentDescription: String,
    iconSize: Dp,
    modifier: Modifier = Modifier,
    border: BorderStroke? = null,
    rotate: Float = 0f,
    enabled: Boolean = true,
) {
    Box(
        modifier = modifier
            .size(40.dp)
            .clip(RoundedCornerShape(10.dp))
            .background(background)
            .then(
                if (border != null) {
                    Modifier.border(border, RoundedCornerShape(10.dp))
                } else {
                    Modifier
                },
            )
            .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            painter = painterResource(icon),
            contentDescription = contentDescription,
            tint = Color.Unspecified,
            modifier = Modifier
                .size(iconSize)
                .rotate(rotate),
        )
    }
}
