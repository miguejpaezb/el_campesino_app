package com.miguelpaezdev.elcampesino.ui.screens.lots

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.miguelpaezdev.elcampesino.data.RetrofitClient
import com.miguelpaezdev.elcampesino.data.dto.EvaluateResultDto
import com.miguelpaezdev.elcampesino.data.dto.LotCreateRequest
import com.miguelpaezdev.elcampesino.data.dto.LotDiscardRequest
import com.miguelpaezdev.elcampesino.data.dto.LotDto
import com.miguelpaezdev.elcampesino.data.dto.LotSummaryDto
import com.miguelpaezdev.elcampesino.data.dto.LotUpdateRequest
import com.miguelpaezdev.elcampesino.ui.components.ToastController
import com.miguelpaezdev.elcampesino.ui.components.ToastType
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class EvaluateData(val lot: LotDto, val result: EvaluateResultDto)

data class SummaryData(val lot: LotDto, val summary: LotSummaryDto)

data class LotsUiState(
    val lots: List<LotDto> = emptyList(),
    val loading: Boolean = true,
    val search: String = "",
    val selectedIds: Set<Int> = emptySet(),
    val accion: String = "",
    val filtro: String = "",
    val filtroAplicado: String = "",
    val accionBusy: Boolean = false,
    val submitting: Boolean = false,
    val createOpen: Boolean = false,
    val editLot: LotDto? = null,
    val discardLot: LotDto? = null,
    val evaluateResult: EvaluateData? = null,
    val summaryData: SummaryData? = null,
)

class LotsViewModel : ViewModel() {

    private val _state = MutableStateFlow(LotsUiState())
    val state: StateFlow<LotsUiState> = _state.asStateFlow()

    init {
        loadLots(showError = true)
    }

    private fun filter(state: LotsUiState): List<LotDto> {
        val term = state.search.trim().lowercase()
        return state.lots
            .filter { lot ->
                when (state.filtroAplicado) {
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

    fun onSearchChange(value: String) = _state.update { it.copy(search = value) }

    fun setAccion(value: String) = _state.update { it.copy(accion = value) }

    fun setFiltro(value: String) = _state.update { it.copy(filtro = value) }

    fun toggleSelect(id: Int) = _state.update { s ->
        s.copy(
            selectedIds = if (id in s.selectedIds) {
                s.selectedIds - id
            } else {
                s.selectedIds + id
            },
        )
    }

    fun toggleSelectAll() {
        val current = _state.value
        val ids = filter(current).map { it.id }.toSet()
        val allSelected = ids.isNotEmpty() && ids.all { it in current.selectedIds }
        _state.update {
            it.copy(
                selectedIds = if (allSelected) {
                    it.selectedIds - ids
                } else {
                    it.selectedIds + ids
                },
            )
        }
    }

    fun loadLots(showError: Boolean) {
        viewModelScope.launch {
            _state.update { it.copy(loading = true) }
            try {
                val lots = RetrofitClient.unwrap(RetrofitClient.api.getLots())
                _state.update { s ->
                    val ids = lots.map { it.id }.toSet()
                    s.copy(lots = lots, selectedIds = s.selectedIds.intersect(ids))
                }
            } catch (e: Exception) {
                if (showError) {
                    showToast(ToastType.ERROR, e.message ?: "No se pudieron cargar los lotes")
                }
            } finally {
                _state.update { it.copy(loading = false) }
            }
        }
    }

    private fun showToast(type: ToastType, message: String) {
        ToastController.show(type, message)
    }

    fun openCreate() = _state.update { it.copy(createOpen = true) }

    fun closeCreate() = _state.update { it.copy(createOpen = false) }

    fun closeEdit() = _state.update { it.copy(editLot = null) }

    fun closeDiscard() = _state.update { it.copy(discardLot = null) }

    fun closeEvaluate() = _state.update { it.copy(evaluateResult = null) }

    fun closeSummary() = _state.update { it.copy(summaryData = null) }

    fun clearAll() = _state.update {
        it.copy(
            search = "",
            selectedIds = emptySet(),
            accion = "",
            filtro = "",
            filtroAplicado = "",
            createOpen = false,
            editLot = null,
            discardLot = null,
            evaluateResult = null,
            summaryData = null,
        )
    }

    private fun resetSelectors() = _state.update { it.copy(accion = "", filtro = "") }

    fun applyAction() {
        val s = _state.value
        if (s.accion.isEmpty() && s.filtro.isEmpty()) return

        if (s.accion.isNotEmpty() && s.filtro.isNotEmpty()) {
            showToast(
                ToastType.ERROR,
                "No puedes combinar una acción por lote con un filtro de estado. " +
                    "Deja uno en la opción predeterminada.",
            )
            return
        }

        if (s.filtro.isNotEmpty()) {
            _state.update { it.copy(filtroAplicado = it.filtro, accion = "", filtro = "") }
            return
        }

        val selected = s.lots.filter { it.id in s.selectedIds }
        if (selected.isEmpty()) {
            showToast(ToastType.ERROR, "Selecciona al menos un lote para ejecutar la acción.")
            return
        }

        if (s.accion == "advance") {
            val discarded = selected.firstOrNull { !it.isActive }
            if (discarded != null) {
                showToast(
                    ToastType.ERROR,
                    "El lote ${discarded.lotCode} se encuentra descartado y no puede avanzar de semana.",
                )
                return
            }
            advanceWeek(selected)
            resetSelectors()
            return
        }

        if (selected.size > 1) {
            showToast(
                ToastType.ERROR,
                "Esta acción solo puede ejecutarse sobre un lote a la vez.",
            )
            return
        }

        val lot = selected.first()
        when (s.accion) {
            "edit" -> {
                _state.update { it.copy(editLot = lot) }
                resetSelectors()
            }

            "evaluate" -> {
                if (!lot.isActive) {
                    showToast(ToastType.ERROR, "El lote ya se encuentra descartado.")
                    return
                }
                evaluate(lot)
                resetSelectors()
            }

            "summary" -> {
                loadSummary(lot)
                resetSelectors()
            }

            "discard" -> {
                if (!lot.isActive) {
                    showToast(ToastType.ERROR, "El lote ya se encuentra descartado.")
                    return
                }
                _state.update { it.copy(discardLot = lot) }
                resetSelectors()
            }
        }
    }

    private fun advanceWeek(selected: List<LotDto>) {
        viewModelScope.launch {
            _state.update { it.copy(accionBusy = true) }
            try {
                selected.forEach { RetrofitClient.unwrap(RetrofitClient.api.advanceWeek(it.id)) }
                val count = selected.size
                showToast(
                    ToastType.SUCCESS,
                    "Semana avanzada para $count ${if (count == 1) "lote" else "lotes"}.",
                )
                loadLots(showError = true)
            } catch (e: Exception) {
                showToast(ToastType.ERROR, e.message ?: "No se pudo avanzar la semana del lote")
            } finally {
                _state.update { it.copy(accionBusy = false) }
            }
        }
    }

    private fun evaluate(lot: LotDto) {
        viewModelScope.launch {
            _state.update { it.copy(accionBusy = true) }
            try {
                val result = RetrofitClient.unwrap(RetrofitClient.api.evaluateLot(lot.id))
                if (result.message.startsWith("Aún no es la semana")) {
                    showToast(ToastType.INFO, result.message)
                } else {
                    _state.update { it.copy(evaluateResult = EvaluateData(lot, result)) }
                }
                loadLots(showError = true)
            } catch (e: Exception) {
                showToast(ToastType.ERROR, e.message ?: "No se pudo evaluar el lote")
            } finally {
                _state.update { it.copy(accionBusy = false) }
            }
        }
    }

    private fun loadSummary(lot: LotDto) {
        viewModelScope.launch {
            _state.update { it.copy(accionBusy = true) }
            try {
                val summary = RetrofitClient.unwrap(RetrofitClient.api.getLotSummary(lot.id))
                _state.update { it.copy(summaryData = SummaryData(lot, summary)) }
            } catch (e: Exception) {
                showToast(ToastType.ERROR, e.message ?: "No se pudo obtener el resumen del lote")
            } finally {
                _state.update { it.copy(accionBusy = false) }
            }
        }
    }

    fun createLot(request: LotCreateRequest) {
        viewModelScope.launch {
            _state.update { it.copy(submitting = true) }
            try {
                RetrofitClient.unwrap(RetrofitClient.api.createLot(request))
                showToast(ToastType.SUCCESS, "Lote ${request.lotCode} creado correctamente.")
                _state.update { it.copy(createOpen = false) }
                loadLots(showError = true)
            } catch (e: Exception) {
                showToast(ToastType.ERROR, e.message ?: "No se pudo crear el lote")
            } finally {
                _state.update { it.copy(submitting = false) }
            }
        }
    }

    fun updateLot(lot: LotDto, request: LotUpdateRequest) {
        viewModelScope.launch {
            _state.update { it.copy(submitting = true) }
            try {
                RetrofitClient.unwrap(RetrofitClient.api.updateLot(lot.id, request))
                showToast(ToastType.SUCCESS, "Lote ${lot.lotCode} actualizado.")
                _state.update { it.copy(editLot = null) }
                loadLots(showError = true)
            } catch (e: Exception) {
                showToast(ToastType.ERROR, e.message ?: "No se pudo actualizar el lote")
            } finally {
                _state.update { it.copy(submitting = false) }
            }
        }
    }

    fun discardLot(lot: LotDto, reason: String, onError: () -> Unit) {
        viewModelScope.launch {
            _state.update { it.copy(submitting = true) }
            try {
                RetrofitClient.unwrap(
                    RetrofitClient.api.discardLot(lot.id, LotDiscardRequest(reason)),
                )
                showToast(ToastType.SUCCESS, "Lote ${lot.lotCode} descartado.")
                _state.update { it.copy(discardLot = null) }
                loadLots(showError = true)
            } catch (e: Exception) {
                showToast(ToastType.ERROR, e.message ?: "No se pudo descartar el lote")
                onError()
            } finally {
                _state.update { it.copy(submitting = false) }
            }
        }
    }
}
