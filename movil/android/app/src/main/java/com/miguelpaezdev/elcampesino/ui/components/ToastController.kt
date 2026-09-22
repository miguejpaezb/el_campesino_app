package com.miguelpaezdev.elcampesino.ui.components

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

object ToastController {

    private const val DEFAULT_DURATION = 4000L

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

    private val _toasts = MutableStateFlow<List<AppToast>>(emptyList())
    val toasts: StateFlow<List<AppToast>> = _toasts.asStateFlow()

    private var nextId = 0L

    fun show(type: ToastType, message: String, durationMs: Long = DEFAULT_DURATION) {
        val id = ++nextId
        _toasts.update { it + AppToast(id, type, message) }
        scope.launch {
            delay(durationMs)
            dismiss(id)
        }
    }

    fun dismiss(id: Long) {
        _toasts.update { list -> list.filterNot { it.id == id } }
    }
}
