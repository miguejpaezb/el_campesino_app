/**
 * Página de inventario de aves (lotes).
 *
 * Lista los lotes registrados con buscador por id/lot_code, filtro por
 * estado y acciones por lote (crear, editar, avanzar semana, evaluar,
 * resumen y descartar). La tabla se reduce en pantallas móviles para
 * facilitar la selección táctil.
 *
 * @returns {JSX.Element} Página de gestión de lotes.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Modal from '../components/Modal.jsx'
import PageHeader from '../components/PageHeader.jsx'
import Toast from '../components/Toast.jsx'
import lotService from '../services/lotService.js'
import { getErrorMessage } from '../utils/errors.js'
import './LotsPage.css'

const DISCARD_SECONDS = 5
const TOAST_DURATION = 4000

const toISODate = (d) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const mortalityOf = (lot) =>
  lot.initial_quantity > 0
    ? Math.round(
      ((lot.initial_quantity - lot.current_quantity) / lot.initial_quantity) *
      100,
    )
    : 0

function CreateModal({ open, onClose, onSubmit }) {
  const [form, setForm] = useState({
    lot_code: '',
    breed: '',
    initial_quantity: '',
    entry_date: toISODate(new Date()),
    observations: '',
  })
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const setField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const validate = () => {
    const next = {}
    if (!form.lot_code.trim()) {
      next.lot_code = 'El código del lote es obligatorio'
    }
    if (!form.breed.trim()) {
      next.breed = 'La raza es obligatoria'
    }
    const quantity = Number(form.initial_quantity)
    if (
      !form.initial_quantity ||
      !Number.isInteger(quantity) ||
      quantity <= 0
    ) {
      next.initial_quantity = 'Ingresa una cantidad mayor a 0'
    }
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    await onSubmit({
      lot_code: form.lot_code.trim(),
      breed: form.breed.trim(),
      initial_quantity: Number(form.initial_quantity),
      entry_date: form.entry_date || null,
      observations: form.observations.trim() || null,
    })
    setSubmitting(false)
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Crear lote de aves"
      subtitle="Registra un nuevo lote en la granja"
      footer={
        <div className="modal-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={onClose}
            disabled={submitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn-primary"
            form="create-lot-form"
            disabled={submitting}
          >
            {submitting ? 'Creando...' : 'Crear lote'}
          </button>
        </div>
      }
    >
      <form id="create-lot-form" onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label className="form-label" htmlFor="create-lot-code">
            Código del lote
          </label>
          <input
            id="create-lot-code"
            className="form-control"
            type="text"
            maxLength={20}
            placeholder="Ej: lote0003"
            value={form.lot_code}
            onChange={(event) => setField('lot_code', event.target.value)}
          />
          {errors.lot_code && <p className="form-error">{errors.lot_code}</p>}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="create-breed">
            Raza
          </label>
          <input
            id="create-breed"
            className="form-control"
            type="text"
            maxLength={50}
            placeholder="Ej: Hy-Line Brown"
            value={form.breed}
            onChange={(event) => setField('breed', event.target.value)}
          />
          {errors.breed && <p className="form-error">{errors.breed}</p>}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="create-quantity">
            Cantidad inicial
          </label>
          <input
            id="create-quantity"
            className="form-control"
            type="number"
            min="1"
            step="1"
            placeholder="Ej: 100"
            value={form.initial_quantity}
            onChange={(event) =>
              setField('initial_quantity', event.target.value)
            }
          />
          {errors.initial_quantity && (
            <p className="form-error">{errors.initial_quantity}</p>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="create-entry-date">
            Fecha de ingreso
          </label>
          <input
            id="create-entry-date"
            className="form-control"
            type="date"
            value={form.entry_date}
            onChange={(event) => setField('entry_date', event.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="create-observations">
            Observaciones
          </label>
          <textarea
            id="create-observations"
            className="form-control"
            rows={3}
            maxLength={500}
            placeholder="Notas adicionales del lote"
            value={form.observations}
            onChange={(event) => setField('observations', event.target.value)}
          />
        </div>
      </form>
    </Modal>
  )
}

function EditModal({ lot, open, onClose, onSubmit }) {
  const [breed, setBreed] = useState(lot?.breed ?? '')
  const [observations, setObservations] = useState(lot?.observations ?? '')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!breed.trim()) {
      setError('La raza es obligatoria')
      return
    }
    setSubmitting(true)
    await onSubmit({
      breed: breed.trim(),
      observations: observations.trim() || null,
    })
    setSubmitting(false)
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Editando ${lot?.lot_code || ''}`}
      subtitle="Modifica los datos del lote"
      footer={
        <div className="modal-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={onClose}
            disabled={submitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn-primary"
            form="edit-lot-form"
            disabled={submitting}
          >
            {submitting ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      }
    >
      <form id="edit-lot-form" onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label className="form-label" htmlFor="edit-breed">
            Raza
          </label>
          <input
            id="edit-breed"
            className="form-control"
            type="text"
            maxLength={50}
            value={breed}
            onChange={(event) => {
              setBreed(event.target.value)
              setError('')
            }}
          />
          {error && <p className="form-error">{error}</p>}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="edit-observations">
            Observaciones
          </label>
          <textarea
            id="edit-observations"
            className="form-control"
            rows={4}
            maxLength={500}
            value={observations}
            onChange={(event) => setObservations(event.target.value)}
          />
        </div>
      </form>
    </Modal>
  )
}

function DiscardModal({ lot, open, onClose, onSubmit }) {
  const [reason, setReason] = useState('')
  const [secondsLeft, setSecondsLeft] = useState(null) // null = sin conteo
  const [discarding, setDiscarding] = useState(false)
  const secondsRef = useRef(0)
  const intervalRef = useRef(null)

  useEffect(() => {
    return () => clearInterval(intervalRef.current)
  }, [])

  const clearCountdown = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const executeDiscard = async () => {
    setDiscarding(true)
    try {
      await onSubmit(reason.trim())
    } catch {
      setDiscarding(false)
      setSecondsLeft(null)
    }
  }

  const startCountdown = () => {
    clearCountdown()
    setDiscarding(false)
    secondsRef.current = DISCARD_SECONDS
    setSecondsLeft(DISCARD_SECONDS)
    intervalRef.current = setInterval(() => {
      secondsRef.current -= 1
      if (secondsRef.current <= 0) {
        clearCountdown()
        setSecondsLeft(0)
        executeDiscard()
        return
      }
      setSecondsLeft(secondsRef.current)
    }, 1000)
  }

  const cancel = () => {
    clearCountdown()
    setDiscarding(false)
    setSecondsLeft(null)
  }

  const counting = secondsLeft !== null && !discarding

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Descartar lote"
      subtitle={lot ? `${lot.lot_code} · ${lot.breed}` : ''}
      footer={
        <div className="modal-actions">
          {counting || discarding ? (
            <button
              type="button"
              className="btn-secondary"
              onClick={cancel}
              disabled={discarding}
            >
              {discarding ? 'Descartando...' : 'Cancelar descarte'}
            </button>
          ) : (
            <>
              <button type="button" className="btn-secondary" onClick={onClose}>
                Cancelar
              </button>
              <button
                type="button"
                className="btn-danger"
                onClick={startCountdown}
                disabled={!reason.trim()}
              >
                Confirmar descarte
              </button>
            </>
          )}
        </div>
      }
    >
      <p className="discard-warning">
        Esta acción es irreversible: el lote quedará inactivo y registrado con
        el motivo del descarte.
      </p>

      <label className="form-label" htmlFor="discard-reason">
        Razón del descarte
      </label>
      <textarea
        id="discard-reason"
        className="form-control"
        rows={3}
        maxLength={500}
        placeholder="Indica el motivo del descarte"
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        disabled={counting || discarding}
      />

      {counting && (
        <div className="countdown">
          <div className="countdown-bar">
            <div
              className="countdown-fill"
              style={{ width: `${(secondsLeft / DISCARD_SECONDS) * 100}%` }}
            ></div>
          </div>
          <div className="countdown-info">
            <span className="countdown-number">{secondsLeft}</span>
            <p>
              El lote se descartará en {secondsLeft}{' '}
              {secondsLeft === 1 ? 'segundo' : 'segundos'}. Puedes cancelar.
            </p>
          </div>
        </div>
      )}
    </Modal>
  )
}

function EvaluateResultModal({ data, onClose }) {
  const { lot, result } = data
  return (
    <Modal
      open
      onClose={onClose}
      title="Resultado de la evaluación"
      subtitle={lot?.lot_code}
      footer={
        <div className="modal-actions">
          <button type="button" className="btn-primary" onClick={onClose}>
            Cerrar
          </button>
        </div>
      }
    >
      <p className="evaluate-message">{result?.message}</p>
      <p className="evaluate-state">
        Estado resultante:{' '}
        <span
          className={`estado estado-${result?.is_active ? 'activo' : 'descartado'
            }`}
        >
          {result?.is_active ? 'Activo' : 'Descartado'}
        </span>
      </p>
    </Modal>
  )
}

function SummaryModal({ data, onClose }) {
  const { lot, summary } = data

  const rows = [
    { label: 'Lote', value: summary.lot_code },
    { label: 'Raza', value: summary.breed },
    { label: 'Semana actual', value: summary.current_week },
    { label: 'Aves iniciales', value: summary.initial_quantity },
    { label: 'Aves actuales', value: summary.current_quantity },
    { label: 'Total de huevos', value: summary.total_eggs },
    {
      label: 'Promedio semanal',
      value: summary.average_weekly_production.toFixed(2),
    },
    {
      label: 'Porcentaje de postura',
      value: `${summary.laying_percentage}%`,
    },
    {
      label: 'Alimento total (kg)',
      value: summary.total_feed.toFixed(2),
    },
    { label: 'Mortalidad total', value: summary.total_mortality },
    {
      label: 'Porcentaje de mortalidad',
      value: `${summary.mortality_percentage}%`,
    },
    {
      label: 'Porcentaje de supervivencia',
      value: `${summary.survival_percentage}%`,
    },
    { label: 'Vacunas aplicadas', value: summary.vaccination_count },
    {
      label: 'Estado',
      value: summary.is_active ? 'Activo' : 'Descartado',
    },
  ]

  return (
    <Modal
      open
      onClose={onClose}
      title={`Resumen productivo - ${lot?.lot_code || ''}`}
      subtitle="Indicadores del lote"
      size="wide"
      footer={
        <div className="modal-actions">
          <button type="button" className="btn-primary" onClick={onClose}>
            Cerrar
          </button>
        </div>
      }
    >
      <div className="summary-grid">
        {rows.map((row) => (
          <div key={row.label} className="summary-item">
            <span>{row.label}</span>
            <strong>{row.value}</strong>
          </div>
        ))}
      </div>
    </Modal>
  )
}

function LotsPage() {
  const [lots, setLots] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedIds, setSelectedIds] = useState([])
  const [accion, setAccion] = useState('')
  const [filtro, setFiltro] = useState('')
  const [filtroAplicado, setFiltroAplicado] = useState('')
  const [accionBusy, setAccionBusy] = useState(false)
  const [createOpen, setCreateOpen] = useState(false)
  const [editLot, setEditLot] = useState(null)
  const [evaluateResult, setEvaluateResult] = useState(null)
  const [summaryData, setSummaryData] = useState(null)
  const [discardLot, setDiscardLot] = useState(null)
  const [toasts, setToasts] = useState([])

  const toastIdRef = useRef(0)
  const toastTimeoutsRef = useRef([])

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const pushToast = useCallback(
    (type, message) => {
      const id = ++toastIdRef.current
      setToasts((prev) => [...prev, { id, type, message }])
      const timeout = setTimeout(() => dismissToast(id), TOAST_DURATION)
      toastTimeoutsRef.current.push(timeout)
    },
    [dismissToast],
  )

  useEffect(() => {
    const timeouts = toastTimeoutsRef.current
    return () => timeouts.forEach((timeout) => clearTimeout(timeout))
  }, [])

  const refreshLots = useCallback(async () => {
    try {
      const data = await lotService.getLots()
      setLots(data)
      setSelectedIds((prev) =>
        prev.filter((id) => data.some((lot) => lot.id === id)),
      )
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo actualizar la lista de lotes'),
      )
    }
  }, [pushToast])

  useEffect(() => {
    let mounted = true
    lotService
      .getLots()
      .then((data) => {
        if (mounted) setLots(data)
      })
      .catch((error) => {
        if (mounted) {
          pushToast(
            'error',
            getErrorMessage(error, 'No se pudieron cargar los lotes'),
          )
        }
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [pushToast])

  const filteredLots = useMemo(() => {
    const term = search.trim().toLowerCase()
    return lots
      .filter((lot) => {
        if (filtroAplicado === 'active' && !lot.is_active) return false
        if (filtroAplicado === 'discarded' && lot.is_active) return false
        return true
      })
      .filter((lot) => {
        if (!term) return true
        return (
          String(lot.id).includes(term) ||
          lot.lot_code.toLowerCase().includes(term)
        )
      })
      .sort((a, b) => b.id - a.id)
  }, [lots, search, filtroAplicado])

  const allSelected =
    filteredLots.length > 0 &&
    filteredLots.every((lot) => selectedIds.includes(lot.id))

  const toggleSelect = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    )
  }

  const toggleSelectAll = () => {
    const ids = filteredLots.map((lot) => lot.id)
    setSelectedIds((prev) =>
      allSelected
        ? prev.filter((id) => !ids.includes(id))
        : Array.from(new Set([...prev, ...ids])),
    )
  }

  const handleAdvanceWeek = async (selected) => {
    const discarded = selected.filter((lot) => !lot.is_active)
    if (discarded.length > 0) {
      pushToast(
        'error',
        `El lote ${discarded[0].lot_code} se encuentra descartado y no puede avanzar de semana.`,
      )
      return
    }
    setAccionBusy(true)
    try {
      await Promise.all(selected.map((lot) => lotService.advanceWeek(lot.id)))
      const count = selected.length
      pushToast(
        'success',
        `Semana avanzada para ${count} ${count === 1 ? 'lote' : 'lotes'}.`,
      )
      await refreshLots()
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo avanzar la semana del lote'),
      )
    } finally {
      setAccionBusy(false)
    }
  }

  const handleEvaluate = async (lot) => {
    setAccionBusy(true)
    try {
      const result = await lotService.evaluateLot(lot.id)
      if (result.message?.startsWith('Aún no es la semana')) {
        pushToast('info', result.message)
      } else {
        setEvaluateResult({ lot, result })
      }
      await refreshLots()
    } catch (error) {
      pushToast('error', getErrorMessage(error, 'No se pudo evaluar el lote'))
    } finally {
      setAccionBusy(false)
    }
  }

  const handleSummary = async (lot) => {
    setAccionBusy(true)
    try {
      const summary = await lotService.getSummary(lot.id)
      setSummaryData({ lot, summary })
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo obtener el resumen del lote'),
      )
    } finally {
      setAccionBusy(false)
    }
  }

  const handleApply = () => {
    if (!accion && !filtro) return

    if (accion && filtro) {
      pushToast(
        'error',
        'No puedes combinar una acción por lote con un filtro de estado. Deja uno en la opción predeterminada.',
      )
      return
    }

    if (filtro) {
      setFiltroAplicado(filtro)
      return
    }

    const selected = lots.filter((lot) => selectedIds.includes(lot.id))
    if (selected.length === 0) {
      pushToast('error', 'Selecciona al menos un lote para ejecutar la acción.')
      return
    }

    if (accion === 'advance') {
      handleAdvanceWeek(selected)
      return
    }

    if (selected.length > 1) {
      pushToast(
        'error',
        'Esta acción solo puede ejecutarse sobre un lote a la vez.',
      )
      return
    }

    const lot = selected[0]
    if (accion === 'edit') {
      setEditLot(lot)
    } else if (accion === 'evaluate') {
      if (!lot.is_active) {
        pushToast('error', 'El lote ya se encuentra descartado.')
        return
      }
      handleEvaluate(lot)
    } else if (accion === 'summary') {
      handleSummary(lot)
    } else if (accion === 'discard') {
      if (!lot.is_active) {
        pushToast('error', 'El lote ya se encuentra descartado.')
        return
      }
      setDiscardLot(lot)
    }
  }

  const handleCreateSubmit = async (values) => {
    try {
      await lotService.createLot(values)
      pushToast('success', `Lote ${values.lot_code} creado correctamente.`)
      setCreateOpen(false)
      await refreshLots()
    } catch (error) {
      pushToast('error', getErrorMessage(error, 'No se pudo crear el lote'))
    }
  }

  const handleEditSubmit = async (values) => {
    try {
      await lotService.updateLot(editLot.id, values)
      pushToast('success', `Lote ${editLot.lot_code} actualizado.`)
      setEditLot(null)
      await refreshLots()
    } catch (error) {
      pushToast(
        'error',
        getErrorMessage(error, 'No se pudo actualizar el lote'),
      )
    }
  }

  const handleDiscardSubmit = async (reason) => {
    try {
      await lotService.discardLot(discardLot.id, reason)
      pushToast('success', `Lote ${discardLot.lot_code} descartado.`)
      setDiscardLot(null)
      await refreshLots()
    } catch (error) {
      pushToast('error', getErrorMessage(error, 'No se pudo descartar el lote'))
      throw error
    }
  }

  const estadoLabel = (isActive) => (isActive ? 'Activo' : 'Descartado')

  return (
    <div className="lots-shell">
      <PageHeader eyebrow="Inventario de Aves" title="Gestión de lotes" />

      <div className="lots-toolbar">
        <div className="lots-search">
          <input
            type="search"
            placeholder="Buscar por ID o código de lote"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Buscar lote"
          />
        </div>

        <button
          className="btn-add-mobile"
          onClick={() => setCreateOpen(true)}
          aria-label="Crear lote"
        >
          <img src="/icons/add.svg" alt="Crear lote" />
        </button>

        <div className="action-field action-accion">
          <label htmlFor="action-select">Acción por lote</label>
          <select
            id="action-select"
            value={accion}
            onChange={(event) => setAccion(event.target.value)}
          >
            <option value="">Acción por lote</option>
            <option value="edit">Editar</option>
            <option value="advance">Avanzar semana</option>
            <option value="evaluate">Evaluar</option>
            <option value="summary">Resumen</option>
            <option value="discard">Descartar</option>
          </select>
        </div>

        <div className="action-field action-filtro">
          <label htmlFor="filter-select">Filtro</label>
          <select
            id="filter-select"
            value={filtro}
            onChange={(event) => setFiltro(event.target.value)}
          >
            <option value="">Filtro</option>
            <option value="active">Activos</option>
            <option value="discarded">Descartados</option>
          </select>
        </div>

        <button
          className="btn-apply"
          onClick={handleApply}
          disabled={accionBusy}
        >
          <span className="btn-apply-label">
            {accionBusy ? 'Procesando...' : 'Aplicar'}
          </span>
          <img
            className="btn-apply-icon"
            src="/icons/arrow.svg"
            alt="Aplicar"
          />
        </button>

        <button
          className="btn-primary lots-create-btn"
          onClick={() => setCreateOpen(true)}
        >
          Crear lote
        </button>
      </div>

      <div className="lots-table-wrap">
        <table className="lots-table">
          <thead>
            <tr>
              <th className="col-check">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={toggleSelectAll}
                  aria-label="Seleccionar todos"
                />
              </th>
              <th>ID</th>
              <th>Lote </th>
              <th className="col-desktop">Aves actuales</th>
              <th className="col-desktop">Semana actual</th>
              <th className="col-desktop">Mortalidad</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="table-empty">
                  Cargando...
                </td>
              </tr>
            ) : filteredLots.length === 0 ? (
              <tr>
                <td colSpan={7} className="table-empty">
                  No se encontraron lotes
                </td>
              </tr>
            ) : (
              filteredLots.map((lot) => {
                const checked = selectedIds.includes(lot.id)
                return (
                  <tr key={lot.id} className={checked ? 'row-selected' : ''}>
                    <td className="col-check">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleSelect(lot.id)}
                        aria-label={`Seleccionar lote ${lot.lot_code}`}
                      />
                    </td>
                    <td className="cell-id">
                      {String(lot.id).padStart(2, '0')}
                    </td>
                    <td className="cell-code">{lot.lot_code}</td>
                    <td className="col-desktop">{lot.current_quantity}</td>
                    <td className="col-desktop">{lot.current_week}</td>
                    <td className="col-desktop">{mortalityOf(lot)}%</td>
                    <td>
                      <span
                        className={`estado estado-${lot.is_active ? 'activo' : 'descartado'
                          }`}
                      >
                        {estadoLabel(lot.is_active)}
                      </span>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      <CreateModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSubmit={handleCreateSubmit}
      />
      <EditModal
        key={editLot?.id ?? 'edit-empty'}
        lot={editLot}
        open={!!editLot}
        onClose={() => setEditLot(null)}
        onSubmit={handleEditSubmit}
      />
      {evaluateResult && (
        <EvaluateResultModal
          data={evaluateResult}
          onClose={() => setEvaluateResult(null)}
        />
      )}
      {summaryData && (
        <SummaryModal data={summaryData} onClose={() => setSummaryData(null)} />
      )}
      <DiscardModal
        key={discardLot?.id ?? 'discard-empty'}
        lot={discardLot}
        open={!!discardLot}
        onClose={() => setDiscardLot(null)}
        onSubmit={handleDiscardSubmit}
      />

      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default LotsPage
